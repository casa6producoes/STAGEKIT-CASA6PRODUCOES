# 33 — Plano de implementação incremental

Nenhum código de CP1 foi criado nesta revisão. O trabalho executado é CP0. Sequência canônica: CP0 → CP1 → CP2 → CP3 → CP4 → CP5 → CP6A → CP6B → CP7.

## Estrutura técnica proposta
Na branch isolada derivada da base experimental verificada, preservar o legado versionado e introduzir gradualmente:

```text
src/app/(public)/page.tsx
src/app/(public)/[slug]/page.tsx
src/app/(auth)/login/page.tsx
src/app/(auth)/ativar/...
src/app/(private)/dashboard/...
src/app/(admin)/admin/...
src/components/ui/
src/features/{auth,invitations,artists,media,public-kit,themes,events,calendar,admin}/
src/lib/supabase/{browser,server,admin}.ts
src/lib/{authorization,validation,observability}/
src/types/
supabase/migrations/
tests/{unit,integration,e2e}/
legacy/ (referência preservada, sem servir dados privados ou contratos publicamente)
```

App Router, TypeScript estrito e clients browser/server separados. `admin.ts` server-only, uso restrito às operações administrativas após autorização; não usar chave privilegiada como atalho para todas as consultas. Fluxo normal usa contexto do usuário e RLS. Sessão SSR em cookies com validação atual de identidade/estado; proteção CSRF/origin nas operações mutantes.
Versões exatas Next.js/React/TypeScript/Node/Supabase SSR serão escolhidas em CP1 com suporte/vulnerabilidades verificados, dependências pinadas e lockfile. Não presumir middleware.ts ou proxy.ts sem versão definida.
CI executará tipos, lint, testes, scan de segredos e build. A configuração de CI será revista antes de push que possa disparar Preview. Nenhum deploy foi autorizado nem executado nesta revisão.
O schema físico e tipos gerados dependem do banco real auditado. A normalização sugerida no doc 22 não é migration pronta. Novas migrations serão aditivas, testadas em staging e reconciliadas com constraints/JSON existentes.

## Entregas, dependências e aceite
| CP | Tarefas concretas | Testes / critério de aceite | Estado nesta revisão |
|---|---|---|---|
| CP0 | Fonte, assets, matriz, Auth/RLS/grants/Storage/legado, contas, custos, backups e Vercel | SHAs e hashes; políticas reais auditadas; backup restaurável; domínio/Preview/rollback comprovados | Parcial: Git e auditoria local concluídos; infraestrutura bloqueada |
| CP1 | Fundação Next.js/TS, CI, SSR, convites, owner único, RLS, migração de identidade | Build/tipos/lint; convite entregue ao teste autorizado; expiração/replay/revogação/concorrência; signup livre negado; A/B/admin/anônimo/bloqueado isolados; recuperação; preservar vínculos | Não iniciado; depende do aceite CP0 e ambiente isolado |
| CP2 | Editor perfil, bio/redes, mídia, formatos, depoimentos; quotas transacionais e uploads | Persistência após relogin; sexta foto/quarto vídeo/quarto formato/sexto depoimento negados por API; substituição/exclusão; MIME/tamanho; concorrência; suspensão reversível; exclusão cruzada negada | Não iniciado; depende de CP1 |
| CP3 | Rota pública SSR, projeção positiva, URLs antigas e noindex/OG, orçamento sem persistência | HTTP/RSC/OG sem privados; todos slugs preservados; 404/ativo/publicado; campos e número correto em dois kits; nenhuma API/log/storage do formulário; abertura manual acessível | Não iniciado; depende de CP2 |
| CP4 | Extrair CSS/DS e componentes dos 3 temas; prévia/publicação e escalas | Screenshots e interação 360/768/1440; conteúdo ausente/longo; mudança só após publicar; persistência; isolamento; dois temas extras preservados e ocultos | Não iniciado; depende de CP3 |
| CP5 | Shows e escala, cachês/cálculos, status manual, calendário, WhatsApp individual e ICS | CRUD e concorrência; músicos distintos/homônimos; status por evento após relogin; outro artista negado; ICS válido e importação real em conta de teste Google; privacidade; hora/fuso; sem teto de eventos | Não iniciado; depende de CP4 |
| CP6A | QA/regressão completos, alertas 70/90, restore/rollback e release candidato | 0 P0; P1 centrais corrigidos; backup/rollback ensaiados; evidências por SHA/Preview; entrega de convite real de teste; aceite expresso para produção/beta | Não iniciado; depende de CP5 e acessos |
| CP6B | Abrir turma autorizada de até 10, operar 30 dias com suporte/monitoramento semanal | Data oficial registrada; agregados de convidados/ativados/publicações/shows; três contratantes distintos testam abertura manual sem PII; incidentes classificados | Não iniciado; depende de CP6A e autorização de abertura |
| CP7 | Avaliar quatro metas e recomendar continuidade | ≥70% convidados publicam, ≥50% com show, três testes, 0 P0; proprietário delibera sobre expansão | Não iniciado; depende dos 30 dias de CP6B |

## Execução de cada etapa
1. Revalidar HEAD/base e mudanças externas; abrir branch pequena de feature a partir da base experimental aceita. Não sobrescrever trabalho posterior.
2. Associar tarefa → DEC → teste → artefato → SHA → resultado. Casos herdados continuam NAO_EXECUTADO até execução real.
3. Desenvolver somente o checkpoint ativo; banco isolado com dados sintéticos, variáveis por ambiente, sem service key no cliente.
4. Rodar testes do módulo, integração e negativos de acesso; Preview/visual quando exigido; registrar falhas e reteste.
5. Entregar diff e evidência; gate fecha apenas quando todos os critérios exigidos passam. Não converter “presente no código” em “homologado”.
6. Mudança em main, produção, banco real ou DNS só mediante autorização expressa para a ação concreta. Rollback deve considerar dados novos e compatibilidade do schema, além do HTML/deployment.

## Próxima sequência operacional CP0
1. Autorizar conexões corretas de Supabase e Vercel; conferir IDs antes de qualquer consulta.
2. Executar inventário somente leitura preparado, verificar Auth/Storage/backups/planos e vínculos agregados.
3. Definir destino isolado e cobertura de backup; preparar ensaio revisável. Antes de copiar dados reais, obter autorização específica e controles de acesso.
4. Ensaiar restauração e rollback autorizados fora de produção; fechar matriz de risco com evidências.
5. Apresentar CP0 completo. Só então iniciar CP1, preservando decisões e sistema atual.
