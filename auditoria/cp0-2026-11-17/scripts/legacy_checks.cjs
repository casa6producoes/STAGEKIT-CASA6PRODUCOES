/* Runs extracted legacy functions with synthetic data and stubbed services.
 * No application bootstrap, network calls, credentials, or production writes.
 * FAIL means the legacy behavior fails an MVP criterion, not an unhandled test error.
 */
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
const source = fs.readFileSync(path.resolve(root, '../../index.html'), 'utf8');
const results = [];

function extract(name) {
  const match = new RegExp('(?:async\\s+)?function\\s+' + name + '\\s*\\(').exec(source);
  if (!match) throw new Error('Function unavailable: ' + name);
  const start = match.index;
  for (let end = source.indexOf('}', start); end !== -1; end = source.indexOf('}', end + 1)) {
    const text = source.slice(start, end + 1);
    try {
      new vm.Script('(' + text + ')');
      return { text, startLine: source.slice(0,start).split('\n').length,
        endLine: source.slice(0,end).split('\n').length };
    } catch (e) { if (!(e instanceof SyntaxError)) throw e; }
  }
  throw new Error('Incomplete function: ' + name);
}

function context(overrides = {}) {
  const calls = { open:[], toast:[], alert:[], save:0 };
  const elements = {};
  const sandbox = {
    URL, Blob, Date, console: { log(){}, warn(){}, error(){} },
    artistData: { slug:'artista-teste', artistMainName:'Artista Teste', whatsapp:'5511999990000' },
    sessionUser:null, eventsList:[], musiciansList:[], totalBudgetsCount:0,
    selectedFormatForModal:'Acústico',
    document:{getElementById: id => elements[id] || null},
    window:{open: (...args)=>calls.open.push(args)},
    alert: text=>calls.alert.push(text), showToast:(...args)=>calls.toast.push(args),
    closeFormatModal(){}, saveData:async()=>{ calls.save++; return false; },
    applyStagekitTheme(){}, lucide:{createIcons(){}},
    ...overrides,
  };
  const ctx=vm.createContext(sandbox);
  const install = (...names) => {
    for (const name of names) vm.runInContext(extract(name).text,ctx);
  };
  install('normalizeWhatsapp','escHtml','safeExternalUrl','formatStagekitMoney');
  return {ctx,calls,elements,install};
}

async function check(id, criterion, functions, fn) {
  try {
    await fn();
    results.push({id,criterion,status:'PASS',source:functions.map(f=>({function:f,...extract(f),text:undefined}))});
  } catch (e) {
    results.push({id,criterion,status:'FAIL',reason:e.message,
      source:functions.map(f=>({function:f,...extract(f),text:undefined}))});
  }
}

function budget(fields={},phone='5511999990000') {
  const s=context();
  const values={qClientName:'Pessoa Teste',qDateTime:'2026-12-20T19:30',qEventType:'Evento Teste',qAudience:'50',qLocation:'Local Teste',...fields};
  for (const [key,value] of Object.entries(values)) s.elements[key]={value};
  s.ctx.artistData.whatsapp=phone;
  s.install('sendWhatsAppBudget');
  return s;
}

async function ics(events) {
  let content;
  const s=context({sessionUser:{role:'artista'},eventsList:events,
    URL:{createObjectURL:b=>{content=b; return 'blob:synthetic';},revokeObjectURL(){}},
    setTimeout(){},document:{body:{appendChild(){}},createElement:()=>({click(){},remove(){}})}});
  s.install('downloadStagekitCalendarIcs');
  s.ctx.downloadStagekitCalendarIcs();
  return content ? content.text() : '';
}
const event={id:'event-a',name:'Show Teste',date:'2026-12-20T19:30',location:'Local Teste',project:'Acústico',cache:9876,fuel:432,
  musicians:[{name:'Músico A',value:123},{name:'Músico B',value:456}],cpf:'PII_SENTINEL',notes:'PRIVATE_SENTINEL'};

(async()=>{
  for (const [id,field] of [['BUD-01','qDateTime'],['BUD-02','qLocation'],['BUD-03','qEventType']]) {
    await check(id,field+' obrigatório impede abertura vazia',['sendWhatsAppBudget'],async()=>{
      const s=budget({[field]:''});await s.ctx.sendWhatsAppBudget();
      assert.equal(s.calls.open.length,0,'WhatsApp abriu com campo obrigatório vazio');
    });
  }
  await check('BUD-04','Nome vazio impede abertura',['sendWhatsAppBudget'],async()=>{
    const s=budget({qClientName:''});await s.ctx.sendWhatsAppBudget();assert.equal(s.calls.open.length,0);
  });
  await check('BUD-05','Contato ausente impede destino inválido',['sendWhatsAppBudget'],async()=>{
    const s=budget({},'');await s.ctx.sendWhatsAppBudget();
    assert.equal(s.calls.open.length,0,'WhatsApp abriu sem contato válido');
  });
  await check('BUD-06','Fluxo público não tenta gravar perfil',['sendWhatsAppBudget'],async()=>{
    const s=budget();await s.ctx.sendWhatsAppBudget();assert.equal(s.calls.save,0,'saveData foi chamado no orçamento');
  });
  await check('BUD-07','Nome com símbolos chega corretamente codificado',['sendWhatsAppBudget'],async()=>{
    const name='Pessoa & Teste #1 + ç';const s=budget({qClientName:name});await s.ctx.sendWhatsAppBudget();
    const url=new URL(s.calls.open[0][0]);assert.ok(url.searchParams.get('text').includes(name));assert.equal(url.pathname,'/5511999990000');
  });
  await check('BUD-08','Orçamento não envia conteúdo à persistência stubada',['sendWhatsAppBudget'],async()=>{
    const sentinel='PII_FORM_SENTINEL';const s=budget({qClientName:sentinel});await s.ctx.sendWhatsAppBudget();
    assert.ok(!JSON.stringify(s.ctx.artistData).includes(sentinel));
    // This only checks this extracted function; it does not prove absence from all logs/analytics.
  });
  await check('AUTH-01','Cadastro novo exige convite antes de chamar signUp',['submitRegister'],async()=>{
    let signups=0;
    const s=context({STAGEKIT_AUTH_REDIRECT:'https://example.invalid/',supabaseClient:{auth:{signUp:async()=>{signups++;return {data:{session:null},error:null};}}},closeRegisterModal(){}});
    const fields={regFullName:'Artista Sintético',regEmail:'teste@example.invalid',regBirthDate:'1990-01-01',regPhone:'11999990000',regPassword:'Synthetic123'};
    for(const [k,v] of Object.entries(fields))s.elements[k]={value:v};
    s.install('isValidPassword','submitRegister');await s.ctx.submitRegister();
    assert.equal(signups,0,'signUp chamado sem validar convite');
  });
  await check('EV-01','Mensagem do músico não contém cachês dos demais',['buildStagekitEventMessage','getStagekitEventDateTime'],()=>{
    const s=context();s.install('getStagekitEventDateTime','buildStagekitEventMessage');
    const msg=s.ctx.buildStagekitEventMessage(event,event.musicians[0]);
    assert.ok(msg.includes('123'));assert.ok(!msg.includes('456'));assert.ok(!msg.includes('9876'));assert.ok(!msg.includes('PRIVATE_SENTINEL'));
  });
  await check('EV-02','Formatter rejeita data impossível',['getStagekitEventDateTime'],()=>{
    const s=context();s.install('getStagekitEventDateTime');assert.equal(s.ctx.getStagekitEventDateTime('2026-02-30T20:00').date,'');
  });
  await check('EV-03','Escala preserva status por músico ao converter dados',['getEventMusicians'],()=>{
    const s=context();s.install('getEventMusicians');
    const members=s.ctx.getEventMusicians({musicians:[{name:'Músico A',value:123,confirmation_status:'Confirmado'}]});
    assert.equal(members[0].confirmation_status,'Confirmado','Status não preservado pelo conversor legado');
  });
  await check('EV-04','Mensagem não modifica confirmação',['buildStagekitEventMessage','getStagekitEventDateTime'],()=>{
    const s=context();s.install('getStagekitEventDateTime','buildStagekitEventMessage');
    const input={...event.musicians[0],confirmation_status:'Pendente'};s.ctx.buildStagekitEventMessage(event,input);assert.equal(input.confirmation_status,'Pendente');
  });
  await check('ICS-01','Exportação preserva horário local digitado',['downloadStagekitCalendarIcs'],async()=>{
    const content=await ics([event]);assert.ok(content.includes('DTSTART;TZID=America/Sao_Paulo:20261220T193000'));
  });
  await check('ICS-02','Exportação exclui campos financeiros e notas privadas',['downloadStagekitCalendarIcs'],async()=>{
    const privateEvent={...event,cache:987654321.55,fuel:876543210.44,
      musicians:[{name:'PRIVATE_MUSICIAN_A',value:765432109.33},{name:'PRIVATE_MUSICIAN_B',value:654321098.22}]};
    const content=await ics([privateEvent]);
    for(const sentinel of ['987654321','876543210','765432109','654321098','PRIVATE_MUSICIAN','PII_SENTINEL','PRIVATE_SENTINEL'])
      assert.ok(!content.includes(sentinel),'Campo privado encontrado');
  });
  await check('ICS-03','UID estável ao reordenar lista de eventos',['downloadStagekitCalendarIcs'],async()=>{
    const contentA=await ics([event]);const contentB=await ics([{...event,id:'event-b',name:'Show B',date:'2026-12-21T18:00'},event]);
    const uidA=contentA.match(/UID:([^\r\n]+)/)[1];const uidB=[...contentB.matchAll(/UID:([^\r\n]+)/g)][1][1];
    assert.equal(uidA,uidB,'UID muda com índice na lista');
  });
  await check('ICS-04','Data impossível não é normalizada para outro dia',['downloadStagekitCalendarIcs'],async()=>{
    assert.equal(await ics([{...event,date:'2026-02-30T20:00'}]),'','Data impossível foi exportada');
  });
  await check('ICS-05','Linhas ICS até 75 octetos com folding',['downloadStagekitCalendarIcs'],async()=>{
    const content=await ics([{...event,name:'Título ç '.repeat(30)}]);
    assert.ok(content.split('\r\n').every(line=>Buffer.byteLength(line,'utf8')<=75),'Há linha maior que 75 octetos sem folding');
  });
  await check('ICS-06','Escape de vírgula ponto e vírgula e nova linha',['downloadStagekitCalendarIcs'],async()=>{
    const content=await ics([{...event,name:'Show, Teste; A\nB'}]);assert.ok(content.includes('SUMMARY:Show\\, Teste\\; A\\nB'));
  });
  await check('XSS-01','Campos de formato são texto escapado no HTML público',['applyPublicData'],()=>{
    const s=context();const target={innerHTML:''};s.elements.displayFormatsPublicGrid=target;
    s.ctx.artistData.formats=[{title:'<img src=x onerror="globalThis.syntheticXss=true">',sub:'Sub',desc:'Descrição',photo:''}];
    s.install('applyPublicData');s.ctx.applyPublicData();assert.ok(!target.innerHTML.includes('<img src=x'),'HTML inserido sem escape no título do formato');
  });
  await check('XSS-02','Escape HTML trata aspas e tags',['escHtml'],()=>{
    const s=context();assert.equal(s.ctx.escHtml('<b>"\'&'), '&lt;b&gt;&quot;&#39;&amp;');
  });
  const report={executed_at_utc:new Date().toISOString(),scope:'Funções reais v3.18 extraídas; VM com DOM/serviços stubados; dados sintéticos. Sem rede ou E2E.',
    acceptance_pass:results.filter(r=>r.status==='PASS').length,acceptance_fail:results.filter(r=>r.status==='FAIL').length,results};
  fs.mkdirSync(path.join(root,'evidence'),{recursive:true});
  fs.writeFileSync(path.join(root,'evidence/legacy-checks.json'),JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify(report,null,2));
})().catch(e=>{console.error(e);process.exitCode=1;});
