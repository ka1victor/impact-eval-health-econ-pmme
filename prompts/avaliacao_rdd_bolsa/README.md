# Fila operacional — RDD do adicional de bolsa

> **Estado em 18/10/2026: fila executada até o E3.** Com o IVS 2010 oficial do
> Ipea, a regra é sharp, com cortes em **0,300 e 0,400**, e R1 foi aprovado. O
> E3 foi estimado sob o protocolo congelado: nenhum salto é distinguível de
> zero, e o resultado é inconclusivo. O E5 é exploratório. A regra antiga "não
> usar `0,300`" vinha da grade do FAQ e de um arquivo de IVS errado, e está
> **revogada**: 0,300 é um dos dois cortes reais. Ver
> [`auditorias/16`](../../docs/auditorias/16_ivs_2010_oficial_e_arquivo_local.md)
> e [`06_execucao/37`](../../docs/06_execucao/37_resultados_rdd_bolsa_ivs_oficial.md)
> a [`39`](../../docs/06_execucao/39_inferencia_alternativa_rdd_bolsa.md).
> A fila vigente está em
> [`06_execucao/38`](../../docs/06_execucao/38_estado_e_pendencias_rdd_bolsa.md).
> A tabela e as regras abaixo são o plano original; continuam valendo, exceto a
> do `0,300`.

Esta fila implementa
[`docs/05_identificacao/14_plano_implementacao_rdd_bolsa.md`](../../docs/05_identificacao/14_plano_implementacao_rdd_bolsa.md).
A pergunta substantiva, os outcomes permitidos e os limites de retenção estão
em
[`docs/01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md`](../../docs/01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md).

| Ordem | Prompt | Autoriza efeitos? | Condição de saída |
|---:|---|---|---|
| R1–R2 | `01_portao_regra_e_suporte.md` | Não | regra reproduzida, suporte e cointervenções auditados |
| R3–R4 | `02_congelar_e_estimar_administrativo.md` | Apenas administrativos | R1–R2 aprovados e registro pré-análise assinado por hash |
| R5 | futuro | Não nesta fila | depende do primeiro estágio administrativo |
| R6 | futuro | Não nesta fila | depende de R1–R5 e portão clínico |

Regras:

- não restaurar os scripts RDD removidos do histórico;
- ~~não usar `0,300` como cutoff da grade de 2025~~ — **revogada em
  14/10/2026**: a grade aplicada tem cortes em 0,300 e 0,400 (auditoria 16);
- não consultar outcomes durante R1–R2;
- não escolher janela, cutoff ou especificação por p-valor;
- não chamar faixa anunciada de valor pago;
- não estimar separadamente “efeito do salário” e “efeito do IVS” por regressão
  global quando o salário é função da faixa de IVS;
- não chamar oferta local persistente no CNES de retenção individual do
  bolsista;
- não promover a comparação imediata versus reserva a efeito causal;
- não executar ciclo 3, SIH ou SIA nesta fila.
