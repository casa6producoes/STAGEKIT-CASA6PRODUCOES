# 30 — Relatório CP0 atualizado

**Estado: PARCIAL / NÃO HOMOLOGADO.** Observação de 17/11/2026, BRT. Revisão documental 2.3, sobre handoff 2.2. Nenhuma mudança no escopo aprovado.

## Arquivos abertos e precedência
Os 57 arquivos do ZIP foram extraídos. Foram abertos os oito documentos pedidos: mensagem inicial, README, decisões, PRD executivo, auditoria CP0 anterior, gap analysis, migração/rollback e agent/AGENTS.md. Foram examinados os demais documentos, checklists, manifestos, SQLs históricos e HTML/configuração de ambas as branches.
Os arquivos originais continuam intactos em workspace separado. DEC-001–018 e docs/00_PRD_FINAL_ESCOPO_PRODUTO.md prevalecem sobre rascunhos, orientações antigas e comportamento legado.

## Quadro de situação
| Área | Confirmado | Pendente | Bloqueado | Próxima ação |
|---|---|---|---|---|
| Pacote | 57 arquivos; 55/55 hashes do manifesto iguais | Homologação funcional | Não | Preservar referência original e usar este adendo |
| GitHub | Clone, SHAs, seis commits, diff e binários | Nenhuma recuperação de arquivo identificada | Não | Preservar bases e revalidar antes de CP1 |
| Código | Sintaxe válida nas duas branches; matriz e testes locais | Persistência, UX e integração reais | Staging inexistente/não confirmado | Completar auditoria e preparar ambiente isolado |
| Supabase | URL/ref no código; endpoint público Auth responde 200 | Schema, RLS, grants, Auth administrativo, Storage, triggers, vínculos e planos | Sem conexão de gestão/SQL autorizada disponível | Autorizar projeto correto, somente leitura |
| Vercel | Domínio conhecido responde; três rotas servem HTML main exato | Conta/equipe, project ID, deployment ID, Preview, envs, domínios, planos e rollback | Sem conexão de gestão disponível | Autorizar equipe proprietária e conferir project ID |
| Segurança | Cadastro sem convite no cliente; noindex ausente; injeção HTML local; riscos legados | Exploração/negação por RLS e segurança efetiva | Sem staging e identidades de teste | Executar matriz de acesso isolada após inventário |
| Backup | Plano e roteiro preparados | Backup real, cobertura e restauração verificada | Sem acesso aos provedores e destino isolado | Levantar retenção e autorizar destino antes do ensaio |
| CP1–CP7 | Plano e critérios de aceite detalhados | Toda implementação e homologação subsequente | CP0 aberto | Concluir gates CP0, então avançar um checkpoint por vez |

## GitHub: evidência atual
- Repositório: `https://github.com/casa6producoes/STAGEKIT-CASA6PRODUCOES`.
- main: `9f46f9d6ca1e9605dfc90a82dede9c3559f03f72`; index blob `3c459ff01446297eef46623de3be16ba1a2e0508`, 240.461 bytes.
- stagekit-v3-14-teste: `3399f680c01301cb19f36305fac9a064764d10b6`; index blob `1f3ff21d2554d762698f456c1a9a301f707dba42`, 313.489 bytes.
- Nenhum desvio do HTML/configuração em relação ao pacote; testes 6 commits adiante / 0 atrás. Somente index.html diferente entre branches: +1.382 / −546 linhas.
- Os seis commits estão enumerados em evidence/cp0-local-audit.json; o último é a atualização v3.18.
- `SIMBOLO CASA 6.jpg`: 123.369 bytes, blob `59e06442954b8a334b5a8b8da693b1937c806acf`.
- `videodoyoutube.png`: 1.914.641 bytes, blob `014bf22420a550b4ea330e1f2e905a3711fd21cd`.
- Ambos os binários são iguais nas duas branches e estão recuperados na raiz do clone. HTML/vercel.json preservados.
- Branch de trabalho **local**: `audit/cp0-2026-11-17`, criada da branch de testes. Nenhum push foi realizado; permissão de escrita remota não foi testada.

## HTTP e infraestrutura: alcance exato
GET de `/`, `/cantormatheusfelipe` e `/dashboard` em `https://stagekitcasa6.vercel.app` retornou 200 com os 240.461 bytes exatos da main. Isso confirma o artefato servido naquele instante, sem provar qual equipe ou deployment o publicou. O 200 da SPA também não prova que o slug carregou dados ou que o painel autoriza corretamente.
Nessas respostas não há robots meta, X-Robots-Tag, Open Graph inicial nem CSP por header. Não se conclui que o site esteja indexado, nem que CSP sozinho resolveria XSS.
O GET `/auth/v1/settings` de `gixxspfvcgxumyxnyumi` retornou 200: `disable_signup=false`, `external.anonymous_users=true`, `external.email=true`, `mailer_autoconfirm=false`. Usou somente a chave publicável já presente no HTML, em memória. Não foram chamados signup, login, tabelas, funções de negócio ou uploads. Hooks, políticas e bloqueios reais não foram auditados.

## Testes e resultados
| Verificação | Resultado | Limite |
|---|---|---|
| Manifesto SHA-256 e tamanho | 55/55 iguais | Mensagem inicial e manifesto não cobertos pelo manifesto recebido |
| Blobs Git das árvores | 8/8 blobs conferidos; 4 arquivos por branch | HTML/configuração comparados ao ZIP; binários não estavam nele |
| Sintaxe JavaScript | 6/6 scripts inline passaram | Não verifica dependências, DOM ou autorização |
| Critérios funcionais locais v3.18 | 21 executados; 10 passaram; 11 falharam | Funções extraídas em VM; DOM e serviços simulados; dados sintéticos |
| HTTP público | 3/3 respostas 200, iguais à main | Sem execução do navegador, backend privado ou Preview |
| Auth público | 200, configurações levantadas | Sem prova de cadastro efetivo, RLS ou administração |
| Histórico por padrões | 76 blobs; 54 candidatos, 107 ocorrências | Podem incluir defaults/demonstrações; não foram usados nem validados |

Falhas locais: BUD-01/02/03/05/06, AUTH-01, EV-03, ICS-03/04/05, XSS-01. Detalhes, linhas e resultados individuais em evidence/legacy-checks.json. O sucesso do teste de não copiar nome do orçamento para artistData não certifica ausência global de PII em logs/analytics.
Não existe package.json, aplicação Next.js, build/lint configurados ou suíte E2E no legado. Build de Next.js e homologações dos próximos CPs **não executados**, não se aplicam à entrega CP0.

## Gates e conclusão
Código, proveniência e assets: verificados. Matriz de equivalência e revisão estática/local: produzidas, com falhas abertas. Schema/RLS/Storage, backups restauráveis, equipe Vercel e rollback: bloqueados. CP0 não pode ser aceito integralmente e CP1 não foi iniciado.
O conjunto de evidências registra o que é reproduzível agora e o que precisa de conexão, sem promover achados estáticos a prova de exploração ou funcionalidade concluída.

## Correções de leitura dos documentos antigos
- README/mensagem inicial/SOURCE_MANIFEST usam v2.1 embora o ZIP seja v2.2: rótulos históricos, não perda de arquivos; todos os hashes recebidos conferem.
- agent/CLAUDE.md ainda diz que DEC-018 não foi aprovada e que PRD é preliminar; os documentos canônicos e a solicitação atual prevalecem.
- Backlog marca DEC-013/016/017/018 como pendentes e ARCH-01 como escolha de arquitetura. São decisões aprovadas; só implementação/detalhes operacionais faltam.
- Doc 07 diz CP0 a iniciar e doc 12 deixa SHA sem confirmação: substituídos, quanto ao estado atual, por esta auditoria.
- O inventário anterior informa 256 IDs; o parser desta revisão conta 253 IDs HTML na branch de testes e 213 na main, sem duplicatas. Contagem lexical do texto não deve ser confundida com atributos HTML reais.
- A data do pacote/hashes não é comprovação de execução SQL, deploy ou restauração. Não repetir afirmações históricas de conexão como se fossem verificações desta sessão.
