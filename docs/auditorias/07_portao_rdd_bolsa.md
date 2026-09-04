# Portão R1 — regra administrativa da bolsa pelo IVS

> **Execução:** 2026-09-04.
> **Decisão:** `REPROVADO_PENDENTE_DE_RECONSTRUCAO`.
> Este portão usa o IVS público apenas como candidato e não abre outcomes de atração.

## Resultado

Foram auditados 368 municípios com ofertas do ciclo 1 de 2025. A taxonomia externa reproduz 191 faixas e diverge em 177 (48.1%).

| Faixa anunciada | Recalculada 1 | Recalculada 2 | Recalculada 3 |
|---|---:|---:|---:|
| Faixa 1 | 19 | 46 | 37 |
| Faixa 2 | 0 | 13 | 94 |
| Faixa 3 | 0 | 0 | 159 |

A correspondência não chega a 100% e as divergências não possuem exceção normativa prévia identificada. Além disso, o arquivo público não prova a vintagem, a precisão, o arredondamento nem o escore efetivamente usado pela SGTES/MS. Portanto, R1 está reprovado com os dados públicos atuais.

## Consequência econométrica

- R2, R3 e R4 permanecem bloqueados; nenhum outcome é consultado por este módulo.
- A matriz pública é diagnóstico de incompatibilidade, não instrumento fuzzy.
- A RDD pode ser reaberta apenas com escore e regra administrativos, ou com exceções normativas previamente documentadas.

## Dados que destravam R1

1. escore IVS aplicado em sua precisão original;
2. vintagem e arquivo de origem;
3. arredondamento e inclusão nos cutoffs;
4. categoria, faixa, valor, vigência e exceções por vaga ou município;
5. histórico de versões e fontes administrativas.

A especificação do pedido está em [`docs/pedidos_dados/vagas_e_regra_ivs.md`](../pedidos_dados/vagas_e_regra_ivs.md).

## Artefatos reproduzíveis

- `output/rdd_bolsa/matriz_municipio_regra_ivs.csv`;
- `output/rdd_bolsa/portao_regra_ivs.json`;
- `scripts/rdd_bolsa/01_auditar_regra_e_suporte.py`.
