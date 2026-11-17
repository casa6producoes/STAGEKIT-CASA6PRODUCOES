# 32 — Complementos de engenharia para o MVP aprovado

**Estado: especificação proposta, sem implantação.** Não cria DEC-019, não muda DEC-001–018. Regras com impacto de produto ainda indefinido estão explicitadas para resolução no checkpoint pertinente, sem repetir decisões fechadas.

## Identidade, convites e beta — CP1
- Fonte confiável de identidade: Supabase Auth validado no servidor. Ownership derivado da identidade; não aceitar user_id/role livres do corpo como autorização.
- Autoridade de owner única, provisionada por procedimento seguro fora do navegador; não fixar e-mail/UID no código. Recuperação administrativa com confirmação de titularidade, sem promover segundo owner.
- Proposta: usar fluxo nativo de convite Supabase e uma autorização de entrada protegida no servidor, associada ao destinatário, lifecycle e turma. Não implementar segundo sistema de senha ou duplicar tokens de ativação sem necessidade comprovada.
- Estados lógicos de convite: pendente, aceito, expirado, revogado; falha de entrega é resultado operacional distinto de aceite. Token gerenciado pelo provedor ou armazenado só como hash, nunca em logs.
- Aceite/revogação/reenvio devem ser atômicos e resistentes a replay/concorrência. Reenvio invalida autorização anterior; e-mail confirmado precisa ser o destinatário elegível. Recuperação de conta ativa não depende de novo convite.
- Configuração real de signup, provedores anônimos, hooks e restrição de ativação precisa ser auditada. Nenhum ajuste em produção está autorizado por esta spec.
- TTL numérico, cadência de reenvio, reserva/liberação de vagas e tratamento de cancelados/testes: **detalhes operacionais ainda sem valor aprovado**. Proposta a validar antes de CP1: reservar vaga por convite válido pendente ou conta ativa, sem ultrapassar 10 por concorrência; não retirar participantes do denominador retroativamente para inflar métricas. Não habilitar emissão enquanto faltar regra de contagem.
- Bloqueio deve consultar estado atual de autorização nas operações protegidas; não depender somente de JWT antigo ou logout visual. Reavaliar publicação conforme regra canônica de ativo/publicado. Não apagar kit, contrato ou mídia ao bloquear.

## Autorização e projeção pública — CP1/CP3
- Separar dados operacionais administrativos dos dados privados do artista. Admin acompanha convites, bloqueios e agregados; não recebe profile_data com eventos/cachês de todos.
- Projeção pública por allowlist validada, inclusive estruturas aninhadas de formatos/depoimentos. Não usar blacklist de dois campos como proteção suficiente. Status/publicação e bloqueio precisam ser verificados no banco/servidor.
- Respostas públicas, HTML inicial, RSC, OG, caches e erros não podem conter dados internos. Resposta de artista autenticado não pode contaminar cache público nem outro artista.
- Se necessário, adotar estados de rascunho/publicação de forma aditiva após inspecionar schema. A existência de role/status Ativo não prova publicação explícita conforme o fluxo aprovado.
- URLs antigas incluem `/{slug}`, `/dashboard`, `/modovisualizacao`, `?artista=...`, `?slug=...`. Mapear casos de uso atuais antes de adotar aliases/redirecionamentos. Não reservar novos slugs sem conferir colisões com kits existentes.
- Na beta, noindex no HTML inicial e X-Robots-Tag; OG por artista, canonical a partir da URL oficial verificada. Preview protegida e noindex. Não habilitar indexação após 30 dias automaticamente.

## Conteúdo, cotas e arquivos — CP2
- Servidor e banco devem impor 1 kit, 5 fotos de galeria, 3 vídeos por URL, 3 formatos e 5 depoimentos. Concorrência não pode permitir ultrapassar cotas. Capa/avatar/formatos não gastam vagas de galeria.
- Validar strings/URLs e renderizar texto escapado. Permitir apenas protocolos/hosts apropriados para cada uso; iframes por providers conhecidos. Sem HTML arbitrário em bio/formatos.
- Limites do legado são referência, não política Storage comprovada: capa 3 MB, perfil 1 MB, galeria/formatos 2 MB, depoimentos 1 MB. Confirmar bytes/MIME permitidos e plano real no inventário antes de fixar configuração.
- Vídeos no MVP são links externos; preservar a função legada de upload MP4 sem oferecê-la como recurso homologado. Sem aumento de quota/upgrade de plano.
- Novos caminhos de mídia usarão identificador de proprietário, categoria e ID aleatório; evitar telefone no path novo. Preservar URLs de objetos antigos até migração auditada.
- Validar tipo real e tamanho no backend/Storage, remover metadados quando apropriado e definir tratamento de SVG/arquivos ativos. Prefixo de usuário no cliente não substitui policy.
- Substituição: gravar novo objeto → atualizar referência com sucesso → remover anterior só quando seguro. Falha não apaga conteúdo válido; remoção órfã posterior controlada e sem excluir arquivo de outro dono.
- Suspensão reversível deve impedir novos uploads inclusive por API, mantendo leitura/edição e mídias atuais. Monitoramento 70%/90% sobre capacidade real; suspensão não é automática por percentual.

## Formulário público — CP3
- Obrigatórios: nome, tipo de evento, data válida, cidade/local; observação opcional. Seleção de formato não substitui tipo; público estimado não é obrigatório aprovado.
- Mensagem proposta: saudação, nome artístico/kit, nome do solicitante, tipo, data, cidade/local, formato se selecionado, observação se fornecida. Texto usa encodeURIComponent/URLSearchParams e telefone do kit atual.
- Sem telefone válido: desabilitar prosseguir com explicação acessível; não usar telefone de exemplo, owner ou outro artista.
- Dados ficam em memória somente enquanto o formulário está aberto. Nenhum endpoint, saveData, localStorage, cookie, analytics ou log recebe conteúdo. Limpar estado ao encerrar/trocar kit. Sem API de lead.
- Botão: “Abrir WhatsApp”; explicar que dados serão enviados ao WhatsApp e que o visitante confirma o envio lá. Se abertura falhar, manter formulário e oferecer link explícito seguro, sem anunciar sucesso de envio.
- Formato de data e texto final são detalhes de UX a validar; não rejeitar eventos históricos existentes por regra nova de data futura.

## Shows, valores e confirmação — CP5
- Eventos têm ID estável e dono; vínculo músico–evento tem ID e status exato Pendente/Confirmado/Recusado. Não identificar pessoa somente por nome na migração; preservar escala histórica se músico sair do catálogo.
- Conversão do legado conserva valores, textos, IDs e vínculos. Dinheiro será representado em centavos ou numeric com escala explícita; somas e arredondamento testados, sem alterar significado dos campos atuais.
- Mostrar total, soma de cachês, despesas e saldo de modo coerente com fórmula existente `saldo = cachê do evento − cachês dos músicos − despesas`; só formalizar após confirmar formato real dos dados.
- Status não muda por WhatsApp. Pendente como valor de dados antigos continua **proposta não homologada**; definir conversão sem inventar confirmação ou recusa.
- API valida data/hora real e valores finitos. Histórico não deve ser eliminado por validação de criação. Edição deve detectar conflito para não sobrescrever escala modificada em outra sessão silenciosamente.
- Mensagem individual contém apenas cachê do destinatário e detalhes pertinentes. Não incluir outros músicos/valores privados. Identificar destinatário de forma estável e validar telefone.

## Calendário / ICS — CP5
- Fonte de horário documentada e explícita; legado usa datetime-local em America/Sao_Paulo. Não converter hora digitada como se já fosse UTC.
- UID derivado do ID persistente do evento, independente de índice, título ou ordenação. Mudança de data preserva identidade. Um VEVENT por evento exportável.
- Validar dia/mês/ano e hora antes de construir Date; escape de TEXT e CRLF, folding por octetos conforme RFC 5545. Não normalizar 30 de fevereiro para março.
- Escolher representação interoperável (UTC correto ou TZID com definição apropriada) e verificar Google Agenda real, casos de meia-noite e caracteres acentuados.
- Duração de 2h é comportamento do legado, não nova regra de produto aprovada. Validar fallback/horário final na spec antes do aceite. Não adicionar recorrência como funcionalidade do MVP.
- ICS só leva campos públicos pertinentes do show. Não leva CPF, cachês, dados bancários, notas ou escala privada. Não promete sincronização após importação manual.

## Temas e operação — CP4/CP6
Extrair tokens/componentes do design documentado e CSS real; manter os três layouts distintos e controles nos intervalos existentes. Prévia privada não grava tema publicado. Manter dois temas extras e contratos preservados e inativos para a beta, sem migração destrutiva.
Registrar capacidade, plano, uso semanal e entrega dos avisos. Canal/destinatário dos alertas e retenção operacional dependem da infraestrutura correta, sem abrir integrações pagas ou envio a terceiros nesta revisão.
Métricas da beta: denominador de convidados válidos, teto 10, ceil(70% × n), ceil(50% × n), três testes distintos sem PII e zero P0. Data oficial, cancelamentos e protocolo de suporte devem ser registrados antes do piloto. Metas e duração permanecem inalteradas.
