# 52f. Adendo: robustez do E9 no ciclo 2 com o tipo de vaga do quadro de 13/02/2026

> **Data de congelamento:** 27/10/2026, antes de rodar as contas deste adendo.<br>
> **Decisão do autor (27/10/2026):** "faz também" o item 1 das pendências, refazer com o quadro de 13/02 as
> robustezes do conjunto principal da escolha no ciclo 2 (auditoria 46, achados A1 e A2).<br>
> **Estatuto:** `ADENDO_52F_POS_RESULTADO`. As versões com o quadro de 19/03 e os adendos 52c, 52d e 52e já foram
> vistos. Toda saída leva `natureza_dos_dados = EMPIRICO`.

## 1. O que falta

O adendo 52c corrigiu o **E9 principal** do ciclo 2 (tipo de vaga e vagas imediatas do quadro de 13/02/2026, vigente
na inscrição) e o 52d corrigiu as sensibilidades do P1 e o conjunto "só vaga imediata". Continuam com o quadro de
19/03/2026, refeito depois do resultado:

- **A1, conjunto principal do E9:** as robustezes pós-auditoria de `E9_robustez_pos_auditoria.csv` (doc 42):
  score bootstrap, CV3, inversão do score, placebos de corte, *spline* cúbico, nós a cada 0,05 e janelas;
- **A2, conjunto "só vaga imediata":** as variantes quadrática e de degraus e o *cluster* por curso;
- **fora do 52d, pelo espírito do §1 dele:** o logit explodido (1ª e 2ª opções) e as versões quadrática e de
  degraus do E9 no conjunto principal.

## 2. O que se estima

As **mesmas especificações** do doc 42 e do 52d, com uma única troca: no ciclo 2, toda variável ou definição que
depende do tipo de vaga vem do quadro de **13/02/2026**, lido como no 52c (mesmo leitor, mesmo hash). Ciclos 1 e 3
não mudam. Mesmos tamanhos de bootstrap, mesmas sementes e mesmas grades de placebo do original.

| Id | Linha | Papel |
|---|---|---|
| **RB-1** | E9 ciclo 2, conjunto principal, corrigido: score bootstrap e CV3 (p e IC) | **principal** deste adendo |
| RB-2 | placebos de corte (grade do doc 42), corrigidos | secundária |
| RB-3 | *spline* cúbico, nós a cada 0,05, janelas | secundária |
| RB-4 | conjunto "só vaga imediata": quadrática, degraus, *cluster* por curso | secundária |
| RB-5 | logit explodido e versões quadrática e de degraus no conjunto principal | secundária |
| RB-6 | todas as linhas acima com o quadro de 19/03 (reprodução de `E9_robustez_pos_auditoria.csv` e afins) | referência |

BKY entre as secundárias.

## 3. Leitura pré-registrada

| Resultado | Leitura |
|---|---|
| RB-1 com p < 0,05 (score bootstrap e CV3) e RB-2 com o corte verdadeiro fora da distribuição dos placebos, como no original | a frase do doc 44 "o ciclo 2 é robusto a poucos *clusters* e a placebos" vale também com o quadro anterior à alocação |
| RB-1 com p ≥ 0,05 em alguma das duas inferências | rebaixar a frase do doc 44 para o ciclo 2; relatar qual inferência caiu |
| alguma variante de RB-3 a RB-5 muda de sinal ou perde o IC que exclui 1 | relatar quais; a leitura se apoia nas que não mudam |

## 4. Saídas

| Item | Onde |
|---|---|
| script | `scripts/rdd_bolsa/52_robustez_E9_ciclo2_quadro_1302.py` (importa 16, 42 e 48; não os reescreve) |
| estimativas | `output/rdd_bolsa/RB_estimativas.csv`, `RB_resumo.json`, `RB_figuras/` |
| resultados | `docs/06_execucao/57y_robustez_E9_ciclo2_quadro_1302.md` (blocos gerados pelo script) |
| testes | `tests/test_robustez_E9_ciclo2_quadro_1302.py` |

**Portão:** reproduzir as linhas RB-6 contra as saídas antigas (≤ 1e−8; nos bootstraps, mesma semente e mesmo
resultado) antes de qualquer conta nova.

## 5. Integridade

Nada imputado, adquirido ou escrito em `data/`; IVS oficial; `E9_*`, `VC_*`, `VD_*` e `VL_*` não são regravados. A
origem é preferência revelada; a bolsa é o pacote do corte.
