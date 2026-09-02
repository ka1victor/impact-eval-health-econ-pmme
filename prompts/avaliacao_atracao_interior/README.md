# Fila operacional — atração e provimento fora das capitais

Esta fila executa o núcleo econométrico associativo definido em
[`docs/01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md`](../../docs/01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md).
Ela não substitui os portões R1–R5 do RDD da bolsa.

Execute uma sessão por vez e preserve os outputs aprovados antes de avançar:

| Ordem | Prompt | Estado inicial | Dependência |
|---:|---|---|---|
| A1 | [`01_reconciliar_funil_ciclo1.md`](01_reconciliar_funil_ciclo1.md) | concluído: `APROVADO_CELULA` | auditoria de viabilidade concluída |
| A2 | [`02_construir_tipologia_territorial.md`](02_construir_tipologia_territorial.md) | concluído: `APROVADO_4_ESTRATOS` | 540/540 municípios A1 (25/101/238/176 strict); REGIC 2018 + RM/RIDE 2022 strict |
| A3 | [`03_congelar_pre_analise.md`](03_congelar_pre_analise.md) | concluído: congelado | registro + potência + hashes; A4 liberado |
| A4 | [`04_estimar_atracao.md`](04_estimar_atracao.md) | concluído: LPM/Logit 1295 células 368 mun., metro +29.4pp, capital +23.2pp, próximo +12.7pp vs remoto; AUC out 0.756; 17 artefatos, 14 testes A4 OK (84 total) | registro A3 com hashes |
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
