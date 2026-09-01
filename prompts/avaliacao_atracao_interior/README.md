# Fila operacional — atração e provimento fora das capitais

Esta fila executa o núcleo econométrico associativo definido em
[`docs/15_incentivos_ivs_provimento_duradouro.md`](../../docs/15_incentivos_ivs_provimento_duradouro.md).
Ela não substitui os portões R1–R5 do RDD da bolsa.

Execute uma sessão por vez e preserve os outputs aprovados antes de avançar:

| Ordem | Prompt | Estado inicial | Dependência |
|---:|---|---|---|
| A1 | [`01_reconciliar_funil_ciclo1.md`](01_reconciliar_funil_ciclo1.md) | concluído: `APROVADO_CELULA` | auditoria de viabilidade concluída |
| A2 | [`02_construir_tipologia_territorial.md`](02_construir_tipologia_territorial.md) | liberado | população e chaves congeladas por A1 |
| A3 | [`03_congelar_pre_analise.md`](03_congelar_pre_analise.md) | após A1–A2 | denominador e território aprovados |
| A4 | [`04_estimar_atracao.md`](04_estimar_atracao.md) | bloqueado | registro A3 com hashes |
| A5 | [`05_avaliar_provimento_cnes.md`](05_avaliar_provimento_cnes.md) | bloqueado | A4 e T0 físico validado |
| A6 | [`06_red_team_e_sintese.md`](06_red_team_e_sintese.md) | bloqueado | A4–A5 concluídos |

Regras comuns:

- não alterar arquivos brutos em `data/`;
- não usar resultado para escolher amostra, cutoff, janela ou outcome;
- agrupar inferência no município quando a exposição varia no município;
- não chamar confirmação de local de entrada, homologação de atividade, estoque
  CNES de bolsista ou presença cadastral de retenção individual;
- interromper a sequência quando o portão da sessão falhar e documentar a
  versão reduzida ainda defensável.
