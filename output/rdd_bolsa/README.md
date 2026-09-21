# `output/rdd_bolsa/` — pacote da trilha do adicional de bolsa

Artefatos da trilha **arquivada** da RDD do adicional de bolsa pelo IVS. A
trilha está `ARQUIVADO_SEM_PRIMEIRO_ESTAGIO`: nenhum resultado do trabalho
vigente depende dela. O pacote é mantido pronto porque o pedido administrativo
**D-3** é o único caminho para o estimando da bolsa, e a decisão de enviar é do
autor. Texto do pedido em
[`../../docs/pedidos_dados/solicitacao_focal_rdd_bolsa.md`](../../docs/pedidos_dados/solicitacao_focal_rdd_bolsa.md).

Todos os arquivos são gerados por script versionado em `scripts/rdd_bolsa/`.
Nenhum contém dado pessoal.

| Arquivo | Gerado por | O que contém |
|---|---|---|
| `diagnostico_viabilidade_salario_ivs.json` | `00_diagnosticar_viabilidade_salario_ivs.py` | viabilidade inicial do par salário–IVS: cobertura, suporte e sobreposição de faixas |
| `a01_primeiro_estagio_publico.csv` / `.json` | `01_auditar_primeiro_estagio_publico.py` | primeiro estágio nos cortes nominais `0,400` e `0,500` com o IVS 2010 público; sem salto estável |
| `matriz_municipio_regra_ivs.csv` | `01_auditar_regra_e_suporte.py` | uma linha por município: IVS, categoria do Atlas, faixa anunciada, valor e divergência |
| `portao_regra_ivs.json` | `01_auditar_regra_e_suporte.py` | decisão do portão **R1**: `REPROVADO_PENDENTE_DE_RECONSTRUCAO`, 191 de 368 faixas reproduzidas, 177 divergentes, e os bloqueios de R2 a R5 |
| `a01b_reconstrucao_regra_faixa.json` | `01b_reconstruir_regra_faixa.py` | busca exaustiva por regra de dois cortes: teto de 77,4% de acerto, 2.763 inversões em 44.073 pares |
| `status_execucao_plano_causal.json` | `02_controlar_execucao_plano_causal.py` | controlador fail-closed: mantém R2 a R5 bloqueados enquanto R1 não for aprovado |
| `triagem_resposta_administrativa.json` | `03_triagem_resposta_administrativa.py` | estado da resposta ao pedido; hoje `AGUARDANDO_RECEBIMENTO`, sem imputar ausência como zero |

## Ordem de uso quando a resposta do pedido chegar

1. Depositar os arquivos recebidos em `data/raw/administrativo_rdd_bolsa/`.
2. Rodar `03_triagem_resposta_administrativa.py`, que decide se o R1 pode ser
   reexecutado.
3. Se a triagem liberar, rodar `01_auditar_regra_e_suporte.py` de novo e ler o
   `portao_regra_ivs.json`. Só um R1 aprovado destrava R2 a R5.

A triagem não libera estimação por conta própria, e resposta parcial ou negativa
é resultado a registrar. Ver
[`../../docs/06_execucao/36_backlog_pos_auditoria.md`](../../docs/06_execucao/36_backlog_pos_auditoria.md),
seção D-3.
