# StageKit CP0 — preservação no GitHub

Adendo de 17/11/2026. A integração GitHub passou a fornecer acesso de leitura e escrita ao repositório correto `casa6producoes/STAGEKIT-CASA6PRODUCOES`. Isso substitui o bloqueio de autenticação registrado nas revisões anteriores; os registros históricos continuam intactos.

## Destino separado
- Branch de auditoria: `audit/cp0-2026-11-17`.
- Base experimental: `3399f680c01301cb19f36305fac9a064764d10b6`.
- Auditoria original: `b3b7016d5563a3d22ec96529855aa1cbd9ad9549`, com os 21 arquivos originais inalterados.
- Complementos e roteiro de recuperação: `b25da5fabe804295e4f4038c14bf65059fad7819`.
- A main deve permanecer em `9f46f9d6ca1e9605dfc90a82dede9c3559f03f72` nesta operação.

Nenhuma alteração no aplicativo legado, banco, DNS ou configuração Vercel acompanha esta preservação. O commit de publicação solicita skip de CI/Vercel; nenhuma promoção ou deploy de produção é solicitado. Não abrir nem mesclar PR na main como parte desta operação.

## Onde estão os resultados
- [Relatório CP0](docs/30_RELATORIO_CP0_ATUALIZADO.md).
- [As 11 reprovações e seus limites](followup/36_ONZE_REPROVACOES_E_LIMITES.md).
- [Guia para autorizar Supabase e Vercel](followup/37_GUIA_CONEXOES_CORRETAS.md).
- [Plano por checkpoints](docs/33_PLANO_NEXTJS_CP0_CP7.md).

## Cópia Git incremental para quem baixar o ZIP da branch
A pasta `preservacao` contém `CP0_b3b7016_b25da5f.bundle`, preservando os dois commits locais exatos acima. A base experimental já existente no repositório é pré-requisito; o bundle não inclui o histórico anterior à base.

Depois de clonar o repositório e baixar o arquivo bundle, executar:

```sh
git fetch origin stagekit-v3-14-teste
git bundle verify /caminho/CP0_b3b7016_b25da5f.bundle
git fetch /caminho/CP0_b3b7016_b25da5f.bundle refs/heads/audit/cp0-2026-11-17:refs/heads/cp0-original-exato
git show --stat b3b7016
```

Quem clonar diretamente a branch de auditoria já terá os commits no histórico; não precisa importar o bundle.

Esta cópia guarda código/documentação, não backups do Supabase ou Storage. CP0 continua parcial até auditoria real das permissões, Auth, Storage, vínculos, infraestrutura e restauração. CP1 não foi iniciado; DEC-001 a DEC-018 permanecem aprovadas e inalteradas.
