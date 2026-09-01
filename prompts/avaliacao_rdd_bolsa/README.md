# Fila operacional — RDD do adicional de bolsa

Esta fila implementa
[`docs/14_plano_implementacao_rdd_bolsa.md`](../../docs/14_plano_implementacao_rdd_bolsa.md).
A pergunta substantiva, os outcomes permitidos e os limites de retenção estão
em
[`docs/15_incentivos_ivs_provimento_duradouro.md`](../../docs/15_incentivos_ivs_provimento_duradouro.md).

| Ordem | Prompt | Autoriza efeitos? | Condição de saída |
|---:|---|---|---|
| R1–R2 | `01_portao_regra_e_suporte.md` | Não | regra reproduzida, suporte e cointervenções auditados |
| R3–R4 | `02_congelar_e_estimar_administrativo.md` | Apenas administrativos | R1–R2 aprovados e registro pré-análise assinado por hash |
| R5 | futuro | Não nesta fila | depende do primeiro estágio administrativo |
| R6 | futuro | Não nesta fila | depende de R1–R5 e portão clínico |

Regras:

- não restaurar os scripts RDD removidos do histórico;
- não usar `0,300` como cutoff da grade de 2025;
- não consultar outcomes durante R1–R2;
- não escolher janela, cutoff ou especificação por p-valor;
- não chamar faixa anunciada de valor pago;
- não estimar separadamente “efeito do salário” e “efeito do IVS” por regressão
  global quando o salário é função da faixa de IVS;
- não chamar oferta local persistente no CNES de retenção individual do
  bolsista;
- não promover a comparação imediata versus reserva a efeito causal;
- não executar ciclo 3, SIH ou SIA nesta fila.
