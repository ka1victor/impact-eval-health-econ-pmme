# Prompts da avaliação prospectiva do ciclo 3

> **Status:** fila prospectiva preparada; nenhum prompt desta pasta foi
> executado. A estratégia substantiva está em
> [`docs/12_estrategia_causal_prospectiva_ciclo3.md`](../../docs/12_estrategia_causal_prospectiva_ciclo3.md).

## Ordem

| Ordem | Prompt | Pode rodar agora? | Resultado |
|---:|---|---|---|
| 1 | [`01_congelar_coorte_e_exposicao.md`](01_congelar_coorte_e_exposicao.md) | Sim | coorte e tratamento auditados |
| 2 | [`02_piloto_sih_anestesiologia.md`](02_piloto_sih_anestesiologia.md) | Após 1 | painel SIH somente pré-tratamento |
| 3 | [`03_torneio_pre_tratamento_e_pre_analise.md`](03_torneio_pre_tratamento_e_pre_analise.md) | Após 1–2 | desenho e protocolo congelados |
| 4 | [`04_piloto_sia_condicional.md`](04_piloto_sia_condicional.md) | Só se o portão 3 acionar | alternativa ecocardiografia/SIA |
| 5 | [`05_estimacao_seis_meses.md`](05_estimacao_seis_meses.md) | Somente com seis meses maduros | primeira análise causal |
| 6 | [`06_atualizacao_doze_meses.md`](06_atualizacao_doze_meses.md) | Somente com doze meses maduros | durabilidade e retenção |

## Regras de uso

1. Rodar um prompt por sessão e revisar o commit antes do seguinte.
2. Os prompts 1–4 não podem consultar ou estimar outcomes pós-tratamento.
3. O prompt 4 é condicional; não baixar SIA por precaução.
4. Os prompts 5–6 não podem reescolher amostra, outcome ou estimador depois de
   observar resultados.
5. Cada sessão cria commit próprio. Push somente quando o autor pedir.
6. Nenhum prompt modifica arquivos brutos existentes ou libera o prompt 03 do
   desenho individual histórico.

## Estado inicial

- estudo geral: planejado, não executado;
- SIH/SIA local: ausente;
- coorte C3: ainda não congelada em produto analítico;
- assinatura pública da Nota Técnica nº 59/2026: ainda não validada nas
  competências CNES futuras;
- protocolo prospectivo: ainda não congelado;
- efeitos pós-tratamento: não estimados.
