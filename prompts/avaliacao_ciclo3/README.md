# Prompts da avaliação prospectiva do ciclo 3

> **Status:** C3-01 concluído e corrigido; C3-02 executado como piloto técnico;
> C3-02B tentado em 31/08/2026 e bloqueado por dois arquivos oficiais ausentes.
> C3-03 não foi executado. A
> estratégia substantiva está em
> [`docs/12_estrategia_causal_prospectiva_ciclo3.md`](../../docs/12_estrategia_causal_prospectiva_ciclo3.md).

## Ordem

| Ordem | Prompt | Pode rodar agora? | Resultado |
|---:|---|---|---|
| 1 | [`01_congelar_coorte_e_exposicao.md`](01_congelar_coorte_e_exposicao.md) | Concluído | coorte e ponte normativa corrigidas |
| 2 | [`02_piloto_sih_anestesiologia.md`](02_piloto_sih_anestesiologia.md) | Executado com ressalvas | viabilidade e painel preliminar |
| 3 | [`02b_corrigir_e_validar_sih_pre.md`](02b_corrigir_e_validar_sih_pre.md) | Repetir quando AC/RR 2026-06 aparecerem | 673/675; SIGTAP 25/25; bloqueio documentado |
| 4 | [`03_torneio_pre_tratamento_e_pre_analise.md`](03_torneio_pre_tratamento_e_pre_analise.md) | **Bloqueado até 675/675** | desenho e protocolo ainda não congelados |
| 5 | [`04_piloto_sia_condicional.md`](04_piloto_sia_condicional.md) | Só se o portão 3 acionar | alternativa ecocardiografia/SIA |
| 6 | [`05_estimacao_seis_meses.md`](05_estimacao_seis_meses.md) | Somente com seis meses maduros | primeira análise causal condicional |
| 7 | [`06_atualizacao_doze_meses.md`](06_atualizacao_doze_meses.md) | Somente com doze meses maduros | durabilidade e retenção |

## Regras de uso

1. Rodar um prompt por sessão e revisar o commit antes do seguinte. Não aceitar
   como C3-03 válido artefatos que ainda afirmem “sete cursos unívocos” ou cujos
   números de MDE/pré-tendência discordem entre Markdown, CSV e JSON.
2. Os prompts 1–4 não podem consultar ou estimar outcomes pós-tratamento.
3. O prompt 4 é condicional; não baixar SIA por precaução.
4. Os prompts 5–6 não podem reescolher amostra, outcome ou estimador depois de
   observar resultados.
5. Cada sessão cria commit próprio. Push somente quando o autor pedir.
6. Nenhum prompt modifica arquivos brutos existentes ou libera o prompt 03 do
   desenho individual histórico.

## Estado atual

- estudo principal: anestesiologia/força de trabalho, planejado e sem efeitos
  pós-tratamento;
- generalização: oncologia clínica e medicina intensiva; curso 2/CBO 225225 como
  sensibilidade;
- SIH local: painéis preliminares C3-02 presentes, mas não aprovados; tentativa
  C3-02B registrou 673 sucessos e ausências oficiais de `RDAC2606.dbc` e
  `RDRR2606.dbc`; SIA ausente;
- SIGTAP: 25 competências historicizadas e auditadas;
- coorte C3: congelada em produto analítico;
- assinatura pública da Nota Técnica nº 59/2026: ainda não validada nas
  competências CNES futuras;
- protocolo prospectivo: ainda não congelado;
- efeitos pós-tratamento: não estimados.

O “C3-03” desta fila é um torneio exclusivamente pré-tratamento e não é o
prompt 03 histórico do desenho individual. Este último continua bloqueado.
