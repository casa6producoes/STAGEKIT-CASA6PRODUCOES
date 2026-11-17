# 38 — Preservação e estado de execução

O commit original **b3b7016d5563a3d22ec96529855aa1cbd9ad9549** e seus **21 arquivos** foram encontrados intactos na retomada. Git fsck passou e todos os bytes foram comparados ao commit. Objetos dangling observados são sobras de versões intermediárias do índice, não corrupção de commits alcançáveis.
O workspace sobreviveu à retomada, mas isso não comprova garantia de retenção externa. Um commit somente local não é, por si só, backup durável.

## Cópia de recuperação preparada
`preserve_cp0.py` prepara um ZIP com os 21 arquivos originais e complementos legíveis, mais um repositório Git portátil com os commits exatos e árvores completas. A fronteira shallow está na base experimental 3399f680: o histórico mais antigo com candidatos de credencial não é incluído. A cópia contém código e assets Git; não é backup de Supabase/Storage/Vercel.
O script testa o ZIP, hashes, extração, clone offline, integridade Git, o commit b3b7016, os 21 arquivos e a árvore completa da revisão. Os resultados ficam em VERIFICACAO_RESTAURACAO.json e o checksum externo acompanha o ZIP.

```sh
python auditoria/cp0-2026-11-17/followup/preserve_cp0.py --output /caminho/gravavel
```

Guardar o pacote em local privado. O download/salvamento pelo responsável ou a publicação da branch autorizada no GitHub ainda são necessários para comprovar uma cópia fora deste ambiente.

## Impedimentos confirmados
- GitHub: API devolve HTTP 401; simulação de push não encontra autenticação. Nenhum push real executado. A branch remota dedicada não foi localizada na consulta.
- Supabase e Vercel: integrações não instaladas/autorizadas nesta sessão. Sem gestão/SQL real; próximos passos no guia 37.
- Diretório de download designado pelo cliente, /codex/browser/projectless/0001-eu-t-criando-um-projeto-um-site-que-uma-landing-/output: criação falha com filesystem somente leitura, inclusive com solicitação de acesso restrita ao caminho. É limitação técnica do filesystem, não recusa de revisão automática.
- Os arquivos de recuperação ficam em `/workspace/work/stagekit/preservation/release/`. Se o cliente permitir abrir/baixar arquivos do workspace, salvar o ZIP por esse fluxo. Caso contrário, autorizar GitHub para publicar a branch separada; não é necessário enviar tokens ao chat.

## Escopo e produto
Esta revisão só acrescenta documentação, verificação de preservação e teste local de renderização. Não corrige o app legado, altera produção ou inicia CP1. As 18 decisões aprovadas continuam intactas. CP0 segue parcial até auditoria real de infraestrutura, backup/restore e demais gates.
