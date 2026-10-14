# Fila operacional — RDD do adicional de bolsa

Esta fila implementa
[`docs/05_identificacao/14_plano_implementacao_rdd_bolsa.md`](../../docs/05_identificacao/14_plano_implementacao_rdd_bolsa.md).
A pergunta substantiva, os outcomes permitidos e os limites de retenção estão
em
[`docs/01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md`](../../docs/01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md).

> **Estado em 05/10/2026.** R1 e R2 foram executados com o IVS administrativo
> que a SGTES publica no quadro de vagas do PMMB 2026: R1 `APROVADO_SHARP`
> (4.103 de 4.103 município–onda–versão) e R2
> `VIAVEL_CONTINUIDADE_COM_RESSALVAS`. A próxima etapa é o R3, que começa por
> decisões do autor. Auditoria em
> [`docs/auditorias/15_portao_r1_r2_ivs_administrativo.md`](../../docs/auditorias/15_portao_r1_r2_ivs_administrativo.md);
> rascunho do protocolo em
> [`docs/05_identificacao/18_protocolo_r3_rdd_bolsa_rascunho.md`](../../docs/05_identificacao/18_protocolo_r3_rdd_bolsa_rascunho.md).
> Antes do R3, o trabalho de 05/10 deve passar pela revisão de
> [`../integracao_rodadas_outubro_2026/`](../integracao_rodadas_outubro_2026/README.md).

| Ordem | Prompt | Autoriza efeitos? | Condição de saída |
|---:|---|---|---|
| R1–R2 | [`01_portao_regra_e_suporte.md`](01_portao_regra_e_suporte.md) | Não | **executado em 05/10/2026**; reexecutar só para reprodução |
| R3 | [`02_congelar_protocolo_r3.md`](02_congelar_protocolo_r3.md) | Não | decisões do autor registradas e `registro_pre_analise.json` commitado |
| R4 | [`03_estimar_r4_atracao.md`](03_estimar_r4_atracao.md) | Só os efeitos do registro | R3 commitado e controlador em `R3_CONGELADO_R4_AUTORIZAVEL` |
| R5 | futuro | Não nesta fila | depende de R4 e do CNES pós com ponte |
| R6 | futuro | Não nesta fila | depende de R1–R5 e de portão clínico |

Regras:

- **running variable:** o IVS administrativo do quadro do PMMB 2026
  (`output/rdd_bolsa/matriz_municipio_ivs_administrativo.csv`). O IVS 2010
  entra só como covariada ou diagnóstico. A troca da running variable canônica
  exige autorização do autor, pedida no R3 (decisão 0 do doc 18);
- **cortes:** `0,300/0,301` (R$ 10 mil → R$ 15 mil) e `0,400/0,401` (R$ 15 mil →
  R$ 20 mil), iguais em 2025 e 2026. Os cortes `0,200` e `0,500` mudam a
  categoria e não a bolsa: são placebos, não cortes de efeito;
- **não consultar outcomes** de candidatura, alocação, homologação ou CNES pós,
  por faixa ou por IVS, antes de o registro R3 estar commitado;
- não escolher banda, corte, unidade ou especificação por p-valor; a grade de
  bandas é a do R2;
- a randomização local reprovou no R2 e não é estimador principal;
- não chamar faixa anunciada de valor pago;
- não estimar separadamente "efeito do salário" e "efeito do IVS" por regressão
  global quando o salário é função da categoria de IVS;
- não chamar oferta local persistente no CNES de retenção individual do
  bolsista;
- não promover a comparação imediata versus reserva a efeito causal;
- a onda do ciclo 3 só entra como desfecho com autorização do autor, porque o
  ciclo 3 está congelado no `CLAUDE.md`;
- SIH, SIA e o ciclo 3 prospectivo não são executados nesta fila;
- ambiente: Python ≥ 3.12 com as versões de `requirements.txt`. R1 e R2
  reproduzem byte a byte sob Python 3.12.3, numpy 2.5.2 e pandas 3.0.5.
