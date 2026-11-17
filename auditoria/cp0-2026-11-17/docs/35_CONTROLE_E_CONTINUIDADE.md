# 35 — Controle de versões e retomada

## Base preservada
- Branch local: audit/cp0-2026-11-17; base origin/stagekit-v3-14-teste `3399f680c01301cb19f36305fac9a064764d10b6`.
- main permanece no commit original `9f46f9d6ca1e9605dfc90a82dede9c3559f03f72`. Nenhuma alteração nos quatro arquivos legados deste checkout.
- Conteúdo novo restrito a `auditoria/cp0-2026-11-17/`. Scripts e documentação não disparam migrations ou deploys.
- O ZIP recebido e a árvore extraída permanecem fora do Git da aplicação; não publicar o handoff não sanitizado nem o histórico contendo candidatos de credencial.
- Não houve push, PR, deploy, alteração de banco, rotação de credencial ou edição de DNS. Esta revisão não confirma permissão de escrita remota.

## Artefatos desta revisão
Relatório CP0; segurança com linhas; especificação complementar; plano CP0–CP7; roteiro de dados/restore/rollback; matriz de lacunas; gates; backlog atualizado; resultados de 21 verificações locais e 6 de sintaxe; inventário/hashes; SQL de metadados preparado; scripts reproduzíveis; manifesto SHA-256 dos novos arquivos e changelog.
Os binários recuperados são os arquivos originais na raiz do clone, com blobs registrados no relatório/evidência. Não são novos assets redesenhados.

## Estado de aceite
| Etapa | Implementação nesta revisão | Testes de aceite | Homologação |
|---|---|---|---|
| CP0 | Auditoria local/HTTP/documentos parcialmente concluída | Integridade e sintaxe aprovadas; falhas legadas documentadas; infraestrutura pendente | NÃO |
| CP1–CP5 | Não iniciada | Não executados | NÃO |
| CP6A | Não iniciada | Não executados | NÃO |
| CP6B/CP7 | Piloto não aberto; 30 dias não transcorreram | Não aferidos | NÃO |

## Próxima retomada sem repetir o produto
1. Ler README desta revisão, relatório 30 e gates CSV, mantendo DEC-001–018 canônicas do handoff.
2. Conferir estado atual dos conectores. Se Supabase/Vercel já estiverem autorizados, utilizar a conexão; não repetir bloqueio antigo.
3. Verificar project ref Supabase e equipe/project ID Vercel. Consultar somente leitura, completar evidências e preparar ensaio isolado revisável.
4. Não usar senha/token do histórico nem pedir .env pelo chat. Sem acesso de gestão, continuar documentação/testes locais independentes e manter gate bloqueado.
5. Atualizar gates/backlog/changelog/resultados a cada ação. Novo resultado não apaga observação anterior: preservar commit e registrar data/ambiente.
6. Fechar CP0 antes de CP1; usar código existente como referência para migração gradual. Aprovação para alterar produção/main/banco real/DNS deve ser expressa e específica.

## Limite do ambiente de arquivos
O caminho de outputs indicado pelo cliente (`/codex/browser/projectless/0001-eu-t-criando-um-projeto-um-site-que-uma-landing-/output`) não existe neste executor e sua criação retornou filesystem somente leitura. Os artefatos técnicos foram mantidos na branch local sob auditoria, dentro do workspace gravável, sem tentar contornar a restrição. O relatório principal também pode ser apresentado inline. Nenhum arquivo foi publicado externamente para criar um link de download.
