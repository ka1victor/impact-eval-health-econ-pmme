# 52g. Adendo: escolha da 1ª opção com o par de UFs fixado, ciclo a ciclo (ciclos 1 e 3)

> **Data de congelamento:** 28/10/2026, antes de rodar as contas deste adendo.<br>
> **Decisão do autor (28/10/2026):** "a hipótese é simplesmente sobre o efeito bolsa → 1ª opção", com "só
> comparação entre municípios da mesma UF". A especificação que compara só vagas da mesma UF é o VL-1 do adendo
> 52e (doc 57x), estimado nos ciclos 1–3 empilhados e no ciclo 2. Faltam os ciclos 1 e 3 separados, que a
> robustez por ciclo precisa.<br>
> **Estatuto:** `ADENDO_52G_POS_RESULTADO`. O VL-1 empilhado e do ciclo 2 já foram vistos. Toda saída leva
> `natureza_dos_dados = EMPIRICO`.

## 1. O que se estima

Exatamente o VL-1 do 52e (mesmo script, mesmas funções, mesmas decisões de implementação do doc 57x, quadro do
ciclo 2 de 13/02/2026), rodado em cada ciclo separado:

| Id | Linha | Papel |
|---|---|---|
| **VG-1** | VL-1 no ciclo 1: razão de chances da 1ª opção por +R$ 5 mil, efeito fixo de UF de origem × UF da vaga | robustez por ciclo |
| **VG-3** | idem no ciclo 3 | robustez por ciclo |
| VG-4 | km equivalentes de +R$ 5 mil em VG-1 e VG-3 (como VL-4) | secundária |
| VG-5 | contagem de pares de UF e de candidatos que identificam em cada ciclo | diagnóstico |
| VG-R | reprodução do VL-1 do ciclo 2 e dos ciclos 1–3 (≤ 1e−8) | portão |

Inferência como no 52e (cluster por conjunto de escolha; score bootstrap de Rademacher). Com poucos conjuntos de
escolha num ciclo, relatar o número de *clusters* e dar peso ao score bootstrap.

## 2. Leitura pré-registrada

| Resultado | Leitura |
|---|---|
| VG-1 e VG-3 com IC que contém 1 | dentro da mesma UF, o efeito da bolsa na escolha é forte só no ciclo 2, como na especificação base |
| VG-1 ou VG-3 com IC que exclui 1, mesmo sinal | o efeito dentro da mesma UF aparece também nesse ciclo |
| sinal oposto com IC que exclui 1 | relatar; a leitura empilhada passa a depender da composição dos ciclos |

## 3. Saídas

| Item | Onde |
|---|---|
| script | `scripts/rdd_bolsa/53_VL1_por_ciclo.py` (importa o 50; não o reescreve) |
| estimativas | `output/rdd_bolsa/VG_estimativas.csv`, `VG_resumo.json` |
| resultados | `docs/06_execucao/57z_VL1_por_ciclo.md` (blocos gerados pelo script) |
| testes | `tests/test_VL1_por_ciclo.py` |

## 4. Integridade

Nada imputado, adquirido ou escrito em `data/`; IVS oficial; `VL_*` e demais saídas não são regravadas.
