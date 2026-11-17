# 34 — Roteiro de dados, infraestrutura e recuperação

**Preparado, não executado.** O ZIP é fonte/documentação, não backup do banco ou Storage. Nenhum dump de artistas foi produzido.

## Conexões mínimas que faltam
| Serviço | Identificação antes da consulta | Leitura necessária |
|---|---|---|
| Supabase | Organização dona do StageKit; ref exata `gixxspfvcgxumyxnyumi` | Metadados/schema, Auth/configuração, RLS/grants, Storage, triggers/funções, backups/retention/PITR, uso e planos |
| Vercel | Equipe dona de `stagekitcasa6.vercel.app`, confirmar project ID e repo ligado | Equipe/projeto, domínios, produção/Preview, branches, deployments/SHAs, proteção, envs por nome/escopo, planos e rollback |

Usar OAuth/conexão/cofre do ambiente, nunca senhas, tokens ou .env pelo chat. Não aceitar seleção de outro Supabase por semelhança de nome. GET público de Auth não é acesso de gestão.

## Inventário somente leitura após conectar
- Schema/tabelas/colunas, PK/FK/unique/check, índices, RLS enable/force, policies USING/WITH CHECK, grants de tabela/coluna/sequência e exposição da Data API.
- Funções/triggers: proprietário, SECURITY DEFINER, search_path, EXECUTE e ordem; revisar allowlist inclusive JSON aninhado e bloqueio de status. Não publicar corpos que contenham segredos.
- Auth: signup/provedores, confirmação e-mail, redirects por ambiente, SMTP/limites de entrega por metadados, expiry, recuperação, hooks, JWT/estado de bloqueados. Não listar e-mails/tokens/senhas em relatório.
- Legado stagekit_users e tabelas de credenciais/reset/limites: existência, grants, RLS, contagens e vínculos. Não ler senhas; não copiar/tentar autenticar com credenciais antigas.
- Storage: buckets públicos/privados, MIME, tamanho, quotas, policies de storage.objects por operação, ownership, acessibilidade de arquivos privados, referências órfãs e consumo. Banco não prova cópia dos bytes dos objetos.
- Contas: contagens de accounts/users/public_kits; owners ausentes ou inconsistentes, slugs duplicados/órfãos, vínculo Auth e kits antigos. Não vincular por nome, telefone aproximado ou coincidência. Mapeamento individual só em ambiente privado autorizado; relatório agregado.
- Vercel: confirmar produção main e Preview de testes por deployments reais; domínio/aliases, redirects, rewrites, headers, proteção, envs por ambiente e compatibilidade de rollback. Não inferir deployment ID do HTML servido.
- Edge Functions, RPCs, hooks e jobs: inventário de nomes/versões/efeitos/autorização; código stagekit-conta não está no ZIP nem nas árvores Git auditadas. Recuperá-lo pelo projeto correto sem expor secrets.

O SQL complementar está em ../sql/01_METADADOS_SOMENTE_LEITURA.sql. É revisão do inventário antigo, cobrindo também auth/storage/grants/constraints. Não foi executado. Contagens/vínculos precisam de uma segunda consulta específica, preparada após confirmar colunas reais; não executar SQL histórico de criação ou publicação.

## Backup e restauração: critérios verificáveis
1. Registrar plano vigente, disponibilidade real de backup/PITR, último sucesso, janela de retenção e responsáveis. Não presumir cobertura porque Supabase é usado; não contratar upgrade.
2. Cobrir Postgres (incluindo dependências e identidades conforme suporte do provedor), objetos Storage com bytes e referências, configuração Auth/redirect/SMTP por metadados, funções e configuração Vercel. Segredos ficam no cofre, fora de docs e Git.
3. Definir destino isolado autorizado, acesso restrito, criptografia, retenção, limpeza e bloqueio de e-mail/webhooks/jobs reais. Para fixtures de desenvolvimento preferir dados sintéticos; restauração real só se autorizada.
4. Registrar duração/freshness observadas para propor RTO/RPO. Nenhum número foi aprovado e nenhum tempo de restauração foi medido nesta revisão.
5. Restaurar no destino isolado; comparar contagens e checksums controlados por entidade, slugs, ownership/FKs, eventos/escala/status/valores e contratos preservados. Verificar imagens por tamanho/hash e leitura autorizada. Não exportar PII ou checksums de campos pessoais de baixa entropia para Git.
6. Confirmar que login de teste, leitura pública mínima, isolamento e dados privados permanecem corretos. Guardar evidência sanitizada com ID do ensaio, SHA, origem/destino, timestamp, duração e pass/fail.
7. Critério de aceite: restauração concluída, cobertura comprovada e divergências zero ou justificadas/aceitas. Um backup listado sem ensaio não fecha o gate.

## Coexistência/migração proposta
Manter HTML/rotas atuais; modelo físico só após auditoria. Fazer alterações aditivas, migrar em lotes idempotentes, validar antes/depois e não apagar stagekit_users/contratos. Identidade legada precisa de vínculo comprovado. Separar slugs públicos e dados privados; não copiar JSON completo para projeção pública. Testar corte em Preview sem reutilizar produção.

## Rollback ensaiável
Registrar deployment anterior e SHA, candidato e SHA, domínios/aliases, schema mínimo suportado e efeitos de gravações novas. Em staging: liberar candidato → criar dados sintéticos → reverter aplicação/roteamento → verificar dados e compatibilidade → retomar candidato. Nenhuma alteração DNS real nessa simulação.
Em produção, reverter deployment não reverte Postgres/Storage nem corrige migração incompatível. Preferir aplicação anterior compatível com schema aditivo; avaliar fix-forward. Restore real é último recurso, com análise de dados criados após backup e autorização específica.
Release e eventual rollback real exigem aprovação do proprietário. Não foram testados nem executados nesta revisão.
