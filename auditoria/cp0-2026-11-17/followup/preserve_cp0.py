"""Build and restore-test a portable local CP0 ZIP. No network or remote writes.

Includes exact commit objects and complete trees from the approved experimental
base onward, with a shallow boundary excluding older credential-bearing history.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

BASE = '3399f680c01301cb19f36305fac9a064764d10b6'
ORIGINAL = 'b3b7016d5563a3d22ec96529855aa1cbd9ad9549'
BRANCH = 'audit/cp0-2026-11-17'
AUDIT = 'auditoria/cp0-2026-11-17'

def git(repo, *args, input_data=None):
    return subprocess.check_output(['git','-C',str(repo),*args], input=input_data, stderr=subprocess.PIPE)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def build(repo, output):
    output.mkdir(parents=True, exist_ok=True)
    head=git(repo,'rev-parse','HEAD').decode().strip()
    git(repo,'merge-base','--is-ancestor',ORIGINAL,head)
    commits=git(repo,'rev-list',head,'^'+BASE).decode().splitlines()+[BASE]
    original_files=git(repo,'ls-tree','-r','--name-only',ORIGINAL,'--',AUDIT).decode().splitlines()
    assert len(original_files)==21
    original_hashes=[]
    for name in original_files:
        content=git(repo,'show',ORIGINAL+':'+name)
        assert git(repo,'show',head+':'+name)==content, 'Original audit file changed: '+name
        original_hashes.append({'path':name,'sha256':sha(content)})

    with tempfile.TemporaryDirectory(prefix='cp0-build-', dir=output) as work:
        payload=Path(work)/'StageKit_CP0';payload.mkdir()
        bare=payload/'snapshot.git'
        subprocess.run(['git','init','--bare','--quiet',str(bare)],check=True)
        shutil.rmtree(bare/'hooks')
        objects=set(commits)
        for commit in commits:
            objects.add(git(repo,'rev-parse',commit+'^{tree}').decode().strip())
            for line in git(repo,'ls-tree','-r','-t',commit).decode().splitlines():
                objects.add(line.split('\t',1)[0].split()[2])
        pack=git(repo,'pack-objects','--stdout',input_data=('\n'.join(sorted(objects))+'\n').encode())
        git(bare,'unpack-objects','-q',input_data=pack)
        (bare/'shallow').write_text(BASE+'\n')
        git(bare,'update-ref','refs/heads/'+BRANCH,head)
        git(bare,'symbolic-ref','HEAD','refs/heads/'+BRANCH)
        git(bare,'fsck','--full')
        files=git(repo,'ls-tree','-r','--name-only',head,'--',AUDIT).decode().splitlines()
        for name in files:
            dest=payload/'arquivos'/name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(git(repo,'show',head+':'+name))
        info={'created_at_utc':datetime.now(timezone.utc).isoformat(),
              'original_commit':ORIGINAL,'head':head,'branch':BRANCH,
              'shallow_boundary':BASE,'commits_included':commits,
              'git_objects_included':len(objects),'original_audit_files':21,
              'audit_files_in_snapshot':len(files),'original_files':original_hashes,
              'old_ancestors_included':False,'database_backup':False,
              'remote_copy_confirmed':False}
        (payload/'PRESERVACAO.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n')
        (payload/'COMO_RESTAURAR.md').write_text(
            '# StageKit CP0 — cópia portátil\n\n'
            'Extraia o ZIP. A pasta arquivos contém a auditoria legível, incluindo os 21 arquivos originais, sem precisar de Git.\n\n'
            'Para recuperar código, assets e commits exatos offline, execute na pasta extraída:\n\n'
            '```sh\ngit clone --no-local snapshot.git STAGEKIT-restaurado\n'
            'git -C STAGEKIT-restaurado fsck --full\n'
            'git -C STAGEKIT-restaurado show --stat b3b7016\n```\n\n'
            'O repositório é shallow por desenho: inclui a base experimental verificada e os commits de auditoria, '
            'com árvores completas, sem importar o histórico antigo com candidatos a credenciais. '
            'O commit original b3b7016 mantém seu SHA e seus 21 arquivos byte a byte. '
            'Não contém banco, Auth, objetos de Storage nem configurações privadas de Vercel. '
            'Inclui fonte legada com configuração publicável e conteúdo demonstrativo; guardar como cópia privada.\n\n'
            'O ZIP só passa a ser uma cópia sob seu controle depois de baixado/salvo fora do ambiente. '
            'Sua criação local não confirma armazenamento durável externo ou branch remota.\n',encoding='utf-8')
        manifest=[]
        for file in sorted(payload.rglob('*')):
            if file.is_file():
                data=file.read_bytes()
                manifest.append({'path':str(file.relative_to(payload)),'bytes':len(data),'sha256':sha(data)})
        (payload/'MANIFESTO_ZIP.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
        archive=output/'STAGEKIT_CP0_PRESERVADO_2026-11-17.zip'
        with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
            for file in sorted(payload.rglob('*')):
                if file.is_file():z.write(file,str(file.relative_to(Path(work))))

    with tempfile.TemporaryDirectory(prefix='cp0-restore-',dir=output) as work:
        with zipfile.ZipFile(archive) as z:
            assert z.testzip() is None
            z.extractall(work)
        extracted=Path(work)/'StageKit_CP0'
        for row in json.loads((extracted/'MANIFESTO_ZIP.json').read_text()):
            data=(extracted/row['path']).read_bytes()
            assert len(data)==row['bytes'] and sha(data)==row['sha256']
        restored=Path(work)/'restored'
        subprocess.run(['git','clone','--no-local','--quiet',str(extracted/'snapshot.git'),str(restored)],check=True)
        git(restored,'fsck','--full')
        assert git(restored,'rev-parse','HEAD').decode().strip()==head
        assert git(restored,'rev-parse','--is-shallow-repository').decode().strip()=='true'
        assert int(git(restored,'rev-list','--count','--all'))==len(commits)
        for row in original_hashes:
            assert sha(git(restored,'show',ORIGINAL+':'+row['path']))==row['sha256']
        for row in git(repo,'ls-tree','-r',head).decode().splitlines():
            name=row.split('\t',1)[1]
            assert git(restored,'show',head+':'+name)==git(repo,'show',head+':'+name)
    checksum=sha(archive.read_bytes())
    (output/(archive.name+'.sha256')).write_text(checksum+'  '+archive.name+'\n')
    verification={'archive':archive.name,'bytes':archive.stat().st_size,'sha256':checksum,
                  'zip_crc_verified':True,'manifest_verified':True,'offline_restore_tested':True,
                  'git_fsck_passed':True,'original_commit_preserved':ORIGINAL,
                  'original_21_files_verified':True,'restored_head':head,
                  'all_head_files_verified':True,'commits_included':len(commits),
                  'older_history_excluded':True,'external_durability_confirmed':False}
    (output/'VERIFICACAO_RESTAURACAO.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(verification,ensure_ascii=False,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[3])
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    build(args.repo.resolve(),args.output.resolve())
