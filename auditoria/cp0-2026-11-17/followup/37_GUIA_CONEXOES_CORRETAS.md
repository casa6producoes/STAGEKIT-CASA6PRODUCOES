# 37 — Autorizar as conexões corretas sem compartilhar credenciais

Estado confirmado em 17/11/2026: integrações Supabase e Vercel ainda não instaladas/autorizadas nesta sessão. GitHub tem leitura pública por Git, mas API retorna 401 e simulação de push não encontra autenticação de escrita. Isso é indisponibilidade de conexão, não rejeição por revisão automática.

## Caminho no ChatGPT/Codex
Abra Configurações → Apps/Aplicativos ou o diretório https://chatgpt.com/plugins. Procure o serviço, adicione a integração e conclua a autorização na página oficial do provedor. Os rótulos podem variar entre clientes. Não envie token, senha, .env, SMTP ou service_role no chat.

## Supabase
1. No dashboard oficial, entre na conta que possui o StageKit e selecione a organização correta.
2. Abra https://supabase.com/dashboard/project/gixxspfvcgxumyxnyumi. Confira o ID em Settings/General e na URL. Se não houver acesso, a conta/organização ainda não é a correta; não selecionar outro projeto por semelhança.
3. Na autorização da integração, selecione essa organização/projeto quando o provedor permitir restringir escopo. Prefira capacidades somente leitura para esta auditoria; não autorizar SQL de escrita como parte do CP0.
4. Depois de autorizar, o agente verificará o acesso e a referência antes de qualquer consulta. A autorização não muda a regra: nenhuma alteração em banco real, Auth ou Storage está aprovada.
5. Conferiremos schema/constraints, grants/RLS, Auth/convites/recuperação, Storage/policies, triggers/funções, vínculos agregados e cobertura de backups/PITR. Valores secretos e linhas com dados pessoais não irão para os relatórios.

Não confundir com projetos LA Music. O endpoint público de Auth consultado anteriormente não concede auditoria administrativa e não confirma RLS.

## Vercel
1. Entre na Vercel e use o seletor de conta/equipe para localizar o projeto que possui o domínio **stagekitcasa6.vercel.app**.
2. No projeto, confira Domains, Git e Deployments: domínio exato, repo `casa6producoes/STAGEKIT-CASA6PRODUCOES`, branch de produção e SHA servido. Não trocar nenhum desses campos.
3. Adicione/autorize a integração Vercel na equipe proprietária, com leitura de projeto/configuração/deployments quando disponível. Se o serviço não permitir escopo por projeto, registre o alcance e mantenha as ações da auditoria limitadas ao StageKit.
4. O agente confirmará team ID/project ID e verificará Production/Preview, variáveis por nome/ambiente sem valores, proteção de Preview, domínios/redirects, deployments e opções de rollback. Nenhum deploy, promoção ou rollback real nesta etapa.

O fato de o domínio responder com a main não identifica por si a equipe nem o deployment. A equipe citada no handoff anterior não localizou o StageKit; não presumir que ela seja a proprietária.

## GitHub para uma cópia externa durável da auditoria
Adicionar/autorizar a integração GitHub para o repositório **casa6producoes/STAGEKIT-CASA6PRODUCOES**, com capacidade de publicar em branch separada. Aprovação da organização pode ser necessária conforme suas regras.
O destino proposto é `audit/cp0-2026-11-17`; o nome foi consultado e não apareceu como branch remota. A simulação não escreveu nada. Após conexão, revalidar destino e publicar somente a branch dedicada, sem force push ou alteração de main. A aplicação legada permanece intacta.
Se a integração só fornecer leitura, configurar escrita pelo fluxo seguro GitHub/ambiente, nunca colando token no chat. Não houve publicação remota nesta revisão.

## Gates após conexão
Auditoria real somente leitura → plano de restauração/rollback revisável → destino isolado e autorização específica antes de copiar dados reais ou executar restore → provas e aceite CP0 → CP1. Sem alteração das 18 decisões e sem iniciar desenvolvimento de CP1 antecipadamente.
