# 31 — Segurança: achados confirmados e riscos a validar

Referências de linha: `index.html` v3.18 na raiz do clone; main consultada no objeto Git `origin/main:index.html`. Sem teste adversarial contra produção.

| ID | Prioridade | Evidência | Conclusão e correção planejada |
|---|---|---|---|
| SEC-CP0-01 | P0 | v3.18:3588–3615; AUTH-01; Auth público disable_signup=false e anonymous_users=true | Cliente chama signUp sem convite. Configuração real permite esses modos; não foi testada ativação sem convite. CP1 deve negar signup/ativação não autorizados no backend e aplicar defesa por RLS. Alteração real depende de autorização específica. |
| SEC-CP0-02 | P0 risco | main:1896–1918, 1938–1954, 2141–2144 | Produção servida ainda consulta stagekit_users, incluindo select de profile_data; listagem usa select('*') e cache local. Se RLS/grants permitirem acesso, dados privados podem chegar ao visitante. Não foi feita leitura dessas linhas no banco real. Auditar legado antes de liberar migração. |
| SEC-CP0-03 | P0 risco | v3.18:2524–2536; SQL histórico v3.14 policies self_or_admin | Consulta administrativa pede profile_data completo; política histórica permite SELECT amplo para admin, divergindo de DEC-011. Não comprova política aplicada. CP1 limitar admin à operação/contagens, sem finanças de terceiros; verificar claims e efetivo bloqueio de sessões. |
| SEC-CP0-04 | P0 para release | v3.18:3110–3125; XSS-01 reprovado | fmt.title/sub/desc entram em innerHTML sem escape. Teste local prova HTML não escapado; execução persistente em produção não testada. Corrigir com renderização React textual, schemas, validação de URL e testes em Preview. Campos coverFontSize e renderização admin também exigem revisão. |
| SEC-CP0-05 | P1; destino incorreto pode ser P0 | v3.18:3711–3730; BUD-01/02/03/05/06 | Formulário aceita obrigatórios vazios; contato vazio produz destino inválido; chama saveData para contador. CP3 validar campos e contato do kit, remover gravação do fluxo de orçamento. Teste não encontrou cópia do conteúdo do formulário para artistData; contador agregado não é prova de armazenamento de lead. |
| SEC-CP0-06 | P1 | HTTP público de três rotas; robots/OG ausentes no HTML/headers | DEC-015 não atendida nas respostas observadas. CP3 emitir noindex no HTML inicial, headers e Preview, com OG por artista, sem bloquear crawler de ler diretiva. Não houve verificação de índice de buscador. |
| SEC-CP0-07 | P0 risco | v3.18:3835–3910; main:3303 | Upload/exclusão têm validações no navegador; main usa sessão anônima para Storage. RLS/MIME/tamanho reais e prefixos não auditados. CP0 inspecionar políticas; CP2 testar cross-tenant, quotas, tipo real, tamanho e objetos privados em staging. |
| SEC-CP0-08 | P1 | v3.18:4264–4278 e escala 4337–4355; EV-03 | Conversores/lista de escala não têm confirmação e descartam propriedade sintética de status. Implementar status no vínculo músico–evento em CP5, com migração preservadora e isolamento. |
| SEC-CP0-09 | P1 | v3.18:4665–4711; ICS-03/04/05 | UID usa posição, data impossível normaliza e não há folding de linhas. CP5 usar id estável, validação estrita e RFC 5545; confirmar no Google real em conta de teste. Campos financeiros estruturados ficaram fora do ICS sintético testado. |
| SEC-CP0-10 | P0 investigação | 76 blobs históricos; 107 candidatos de credencial literal em 54 blobs | Nenhum valor exportado. Candidatos podem ser senha de demonstração/default ou dados reais. Confirmar natureza e revogação em cofre/provedor, sem tentar autenticar com valores; não reescrever histórico ou rotacionar serviços automaticamente. |
| SEC-CP0-11 | P1 | CDN Tailwind/Lucide latest/Chart/Supabase major; vercel.json sem headers | Sem lockfile ou build reproduzível; CSP ausente nas respostas observadas. CP1 pin/lockfile/CI e CP6A revisão de dependências e headers compatíveis com embeds. |
| SEC-CP0-12 | P0 risco | Banco e backups sem conexão de gestão | Vínculos de artistas, senhas legadas e restauração não certificados. Bloqueia migração e release. |

## Proteção de credenciais nesta revisão
A chave `sb_publishable_` aparece em ambas as branches. Essa classe é pública por desenho; depende de RLS e não substitui autorização. Não foi reproduzida em relatórios. As assinaturas de service keys, tokens GitHub, tokens Meta e chaves privadas não deram ocorrências nos dois HEADs pelo conjunto limitado de padrões usado. Isso não certifica ausência de segredos.
O histórico tem candidatos adicionais. Não copiamos os valores para a branch de auditoria. Nenhuma credencial legada foi testada, revogada ou reutilizada. Validar especialmente o token Meta mencionado no handoff em interface segura do provedor.

## Matriz de segurança a executar em ambiente isolado
Identidades: anônimo, artista A, artista B, proprietário, artista bloqueado com token previamente emitido. Usar contas sintéticas; não criar usuários reais nesta etapa.
Recursos: conta, perfil, kit/draft/publicação, eventos, cachês, músicos, confirmação, contratos preservados, objetos Storage, convites e recuperação.
Operações: SELECT/INSERT/UPDATE/DELETE e RPC/API/SSR/exportação, inclusive alteração de owner_id/role, prefixo de arquivo alheio, convite usado duas vezes e chamadas concorrentes.
Esperado: A só acessa dados privados de A; B só de B; admin não ganha acesso geral a finanças; anônimo só recebe projeção positiva publicada/ativa. Revogação/bloqueio deve surtir efeito também com sessão antiga. Não aceitar ocultação de UI como evidência.
Capturar apenas resultado, caso, SHA, ambiente, horário e logs sanitizados. Não registrar senha, token, CPF, contato ou cachê em evidência pública.
