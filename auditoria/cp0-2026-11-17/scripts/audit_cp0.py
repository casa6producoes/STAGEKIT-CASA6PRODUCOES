"""CP0: leitura local/Git; GETs públicos opcionais. Nunca escreve serviços remotos."""
import argparse
import base64
import hashlib
import json
import re
import subprocess
import urllib.request
import urllib.error
from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = None  # Explicit external handoff path supplied by --package
REPO = ROOT.parents[1]
EVIDENCE = ROOT / 'evidence'

def git(*args):
    return subprocess.check_output(['git', '-C', str(REPO), *args])

def blob(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

class Inventory(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.dependencies, self.metas, self.scripts = [], [], [], []
        self.inline, self.current = False, ''
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id'): self.ids.append(a['id'])
        if tag == 'meta': self.metas.append(a)
        if tag == 'script':
            if a.get('src'): self.dependencies.append(a['src'])
            self.inline, self.current = not a.get('src'), ''
    def handle_data(self, data):
        if self.inline: self.current += data
    def handle_endtag(self, tag):
        if tag == 'script' and self.inline:
            self.scripts.append(self.current)
            self.inline = False

def get(url, headers=None):
    req = urllib.request.Request(url, headers={'User-Agent':'StageKit-CP0-readonly/1.0', **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            return response.status, response.headers, response.read(2_000_000)
    except urllib.error.HTTPError as e:
        return e.code, e.headers, b''

def run(network=False):
    EVIDENCE.mkdir(exist_ok=True)
    result = {'observed_at_utc':datetime.now(timezone.utc).isoformat(),
              'method':'Local hashes, git objects, node --check; optional allowlisted public GET only',
              'remote_mutations':False,'historical_sql_executed':False}
    manifest = json.loads((PACKAGE/'auditoria/MANIFESTO_SHA256_ARQUIVOS.json').read_text())
    integrity=[]
    for row in manifest:
        data=(PACKAGE/row['path']).read_bytes()
        digest=hashlib.sha256(data).hexdigest()
        integrity.append({'path':row['path'], 'bytes':len(data),'sha256':digest,
                          'matches_manifest':digest==row['sha256'] and len(data)==row['bytes']})
    result['package']={'file_count':sum(p.is_file() for p in PACKAGE.rglob('*')),
                       'manifest_checked':len(integrity),'matches':sum(x['matches_manifest'] for x in integrity),
                       'mismatches':[x for x in integrity if not x['matches_manifest']],
                       'not_in_manifest':sorted(str(p.relative_to(PACKAGE)) for p in PACKAGE.rglob('*') if p.is_file() and str(p.relative_to(PACKAGE)) not in {x['path'] for x in integrity})}
    branches={}
    for local, branch in [('github_main','main'),('github_teste','stagekit-v3-14-teste')]:
        ref='origin/'+branch
        tree=[]
        for line in git('ls-tree','-rl',ref).decode().splitlines():
            metadata, path=line.split('\t',1)
            mode,kind,sha,size=metadata.split()
            data=git('show',f'{ref}:{path}')
            original=PACKAGE/'codigo'/local/path
            tree.append({'path':path,'git_blob':sha,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),
                         'blob_verified':blob(data)==sha,'in_original_package':original.exists(),
                         'equals_original':data==original.read_bytes() if original.exists() else None})
        html=git('show',f'{ref}:index.html').decode()
        parser=Inventory(); parser.feed(html)
        checks=[]
        scratch=ROOT/'scratch'; scratch.mkdir(exist_ok=True)
        for i,script in enumerate(parser.scripts,1):
            file=scratch/f'{local}-{i}.js'; file.write_text(script)
            run=subprocess.run(['node','--check',str(file)],capture_output=True)
            checks.append({'script':i,'bytes':len(script.encode()),'passed':run.returncode==0})
        # Never write token values to reports. Decode only non-secret role/ref fields.
        keys=[]
        for match in re.finditer(r'\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+',html):
            try:
                part=match.group().split('.')[1]
                payload=json.loads(base64.urlsafe_b64decode(part+'='*(-len(part)%4)))
                keys.append({'line':html[:match.start()].count('\n')+1,'role':payload.get('role'),'ref':payload.get('ref')})
            except (ValueError, json.JSONDecodeError): pass
        sensitive=[]
        patterns={'supabase_secret':r'sb_secret_[A-Za-z0-9_-]+','github_token':r'gh[pousr]_[A-Za-z0-9]{20,}',
                  'private_key':r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
                  'meta_token':r'\bEAA[A-Za-z0-9]{50,}',
                  'credential_literal':r'''(?i)\b(?:password|registeredPassword|service_role|smtp_password|client_secret|access_token)\s*[:=]\s*["'][^"'\n]{3,}["']'''}
        for label, pattern in patterns.items():
            for match in re.finditer(pattern,html):
                sensitive.append({'kind':label,'line':html[:match.start()].count('\n')+1})
        branches[branch]={'head':git('rev-parse',ref).decode().strip(),'tree':tree,
                          'inline_syntax':checks,'html_ids':len(parser.ids),
                          'duplicate_ids':{k:v for k,v in Counter(parser.ids).items() if v>1},
                          'dependencies':parser.dependencies,
                          'robots_meta':[x for x in parser.metas if x.get('name','').lower() in ('robots','googlebot')],
                          'og_meta_count':sum(x.get('property','').startswith('og:') for x in parser.metas),
                          'jwt_public_metadata':keys,'sensitive_pattern_hits_redacted':sensitive,
                          'publishable_key_count':len(re.findall(r'sb_publishable_[A-Za-z0-9_-]+',html)),
                          'innerHTML_occurrences':len(re.findall(r'\.innerHTML\s*=',html))}
    history=[]
    seen=set()
    for commit in git('rev-list','origin/main','origin/stagekit-v3-14-teste').decode().splitlines():
        try:
            sha=git('rev-parse',commit+':index.html').decode().strip()
            if sha in seen: continue
            seen.add(sha)
            old=git('show',commit+':index.html').decode(errors='replace')
            hits=[]
            for label,pattern in patterns.items():
                for match in re.finditer(pattern,old):
                    hits.append({'kind':label,'line':old[:match.start()].count('\n')+1})
            for match in re.finditer(r'\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+',old):
                try:
                    part=match.group().split('.')[1]
                    payload=json.loads(base64.urlsafe_b64decode(part+'='*(-len(part)%4)))
                    if payload.get('role')=='service_role': hits.append({'kind':'jwt_service_role','line':old[:match.start()].count('\n')+1})
                except (ValueError,json.JSONDecodeError): pass
            if hits: history.append({'commit':commit,'blob':sha,'hits_redacted':hits})
        except subprocess.CalledProcessError: continue
    result['history_pattern_scan']={'unique_html_blobs_checked':len(seen),'hits':history,
        'limitation':'Recognizable patterns only; not proof of no secrets; no values are emitted; other files/history and external providers need separate review'}
    result['github']={'repository':'casa6producoes/STAGEKIT-CASA6PRODUCOES','branches':branches,
                      'left_right_count':git('rev-list','--left-right','--count','origin/main...origin/stagekit-v3-14-teste').decode().strip(),
                      'diff_numstat':git('diff','--numstat','origin/main...origin/stagekit-v3-14-teste').decode().strip(),
                      'commits_ahead':git('log','--format=%H %s','origin/main..origin/stagekit-v3-14-teste').decode().splitlines()}
    if network:
        remote=[]
        for path in ['/','/cantormatheusfelipe','/dashboard']:
            url='https://stagekitcasa6.vercel.app'+path
            try:
                status,headers,body=get(url)
                parser=Inventory(); parser.feed(body.decode(errors='replace'))
                remote.append({'url':url,'status':status,'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest(),
                               'matches_main':body==git('show','origin/main:index.html'),
                               'matches_test':body==git('show','origin/stagekit-v3-14-teste:index.html'),
                               'x_robots_tag':headers.get('x-robots-tag'),
                               'content_security_policy_present':bool(headers.get('content-security-policy')),
                               'robots_meta':[x for x in parser.metas if x.get('name','').lower() in ('robots','googlebot')],
                               'og_meta_count':sum(x.get('property','').startswith('og:') for x in parser.metas)})
            except Exception as e: remote.append({'url':url,'error_type':type(e).__name__})
        result['public_http']=remote
        source=(REPO/'index.html').read_text()
        key=re.search(r"const SUPABASE_KEY\s*=\s*['\"]([^'\"]+)",source).group(1)
        url='https://gixxspfvcgxumyxnyumi.supabase.co/auth/v1/settings'
        try:
            status,headers,body=get(url,{'apikey':key})
            settings=json.loads(body) if status==200 else {}
            result['supabase_public_auth_settings']={'project_ref':'gixxspfvcgxumyxnyumi','status':status,
                'settings':{k:settings[k] for k in ['disable_signup','mailer_autoconfirm','phone_autoconfirm','external'] if k in settings},
                'scope':'Public Auth configuration only; no users, private data, database, storage or management API audited'}
        except Exception as e:
            result['supabase_public_auth_settings']={'error_type':type(e).__name__}
    (EVIDENCE/'cp0-local-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    (EVIDENCE/'package-integrity.json').write_text(json.dumps(integrity,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':
    args=argparse.ArgumentParser()
    args.add_argument('--package',type=Path,required=True,help='Extracted original handoff directory; never copied into public repo')
    args.add_argument('--public-http',action='store_true',help='Perform bounded public GETs; no signup/login/database queries')
    options=args.parse_args()
    PACKAGE=options.package.resolve()
    run(options.public_http)
