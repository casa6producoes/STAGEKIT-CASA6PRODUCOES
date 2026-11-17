# StageKit — continuidade CP0, revisão 2.3

Observação: 17/11/2026, America/Sao_Paulo. **CP0 PARCIAL, NÃO HOMOLOGADO.**
Esta revisão acrescenta evidências ao handoff v2.2; não substitui o desenvolvimento anterior.
As DEC-001 a DEC-018 e o PRD executivo permanecem os requisitos canônicos.

## Ler nesta ordem
1. [Relatório e gates CP0](docs/30_RELATORIO_CP0_ATUALIZADO.md).
2. [Segurança e evidências por linha](docs/31_SEGURANCA_E_EVIDENCIAS.md).
3. [Especificações complementares](docs/32_ESPECIFICACOES_COMPLEMENTARES.md).
4. [Plano Next.js por checkpoint](docs/33_PLANO_NEXTJS_CP0_CP7.md).
5. [Auditoria de dados, backup e rollback](docs/34_DADOS_BACKUP_ROLLBACK.md).
6. [Controle de versões e continuidade](docs/35_CONTROLE_E_CONTINUIDADE.md).

## Evidências executadas
- GitHub clonado; HEADs das duas branches conferidos; quatro arquivos por branch, incluindo os dois binários recuperados.
- 55/55 entradas do manifesto do pacote iguais; 57 arquivos presentes. Manifesto e mensagem inicial não têm entrada no próprio manifesto.
- HTML e vercel.json de cada branch idênticos ao pacote; testes seis commits à frente de main.
- `node --check`: seis scripts inline aprovados, três de cada branch.
- 21 critérios locais executados contra funções v3.18: **10 PASS / 11 FAIL**. FAIL registra comportamento legado incompatível com o critério; não é homologação nem E2E.
- GET público de três rotas do domínio conhecido: HTML corresponde exatamente à main; sem noindex nessas respostas.
- GET público de configurações Auth do projeto correto: signup e autenticação anônima habilitados. Não houve criação de usuário ou escrita.
- Varredura por padrões em 76 blobs históricos de HTML: 54 blobs com candidatos a credenciais literais; valores omitidos, validade não testada.

## Reproduzir
Na raiz do clone, com Python 3 e Node.js disponíveis:

```sh
python auditoria/cp0-2026-11-17/scripts/audit_cp0.py --package /caminho/para/STAGEKIT_HANDOFF_V2_2_PRONTO_PARA_IMPORTAR
node auditoria/cp0-2026-11-17/scripts/legacy_checks.cjs
```

O primeiro comando grava nova evidência **local**, sem HTTP por padrão. Para incluir os GETs públicos documentados, adicionar `--public-http`. Um novo resultado offline não contém os GETs anteriores; preservar o commit desta observação para histórico.
O verificador Node retorna código 0 quando o levantamento termina; consultar `acceptance_fail` no JSON para o número de critérios reprovados. Não usar seu código de saída como gate de homologação.
O SQL de `sql/` é **preparado e não executado**. Os SQLs históricos do handoff nunca foram executados nesta revisão.

## Limites e conexões
Autorizar Supabase na organização com projeto ref **gixxspfvcgxumyxnyumi** e Vercel na equipe proprietária do domínio **stagekitcasa6.vercel.app**. Solicitar inicialmente leitura de configurações, schema/policies, backups e deployments. Sem essas conexões, não há auditoria completa de infraestrutura.
Nenhum push, deploy, mudança em main, banco real ou DNS foi feito. CP1 não foi iniciado; o gate técnico CP0 ainda está aberto.
