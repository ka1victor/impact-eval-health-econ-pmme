# 48h. Adendo: H1 com pareamento pela localização da unidade (UF) e dos médicos (estoque de especialistas no entorno)

> **Data de congelamento:** 27/10/2026, antes de rodar as contas deste adendo.<br>
> **Pedido do autor (27/10/2026):** "rodar de novo a H1 fazendo pareamento pela localização da unidade e do
> médico, como se fosse um controle […] é o controle mais importante de todos".<br>
> **Estatuto:** `ADENDO_48H_POS_RESULTADO`. A H1 (48b), os controles e pareamentos por macrorregião (48d, 48e),
> UF (48c) e porte (48g) já foram vistos. Toda saída leva `natureza_dos_dados = EMPIRICO`.

## 1. O que muda em relação ao 48e

O 48e pareia exato em **macrorregião** e capital, e usa no escore os médicos do município e do **resto da região de
saúde**. Este adendo aperta as duas localizações:

1. **Localização da unidade:** pareamento **exato na UF** (no lugar da macrorregião) e em capital.
2. **Localização dos médicos:** no escore entra o **estoque de especialistas das CBO-alvo do curso num raio de
   100 km** do município (sem o próprio município), por 10 mil hab. do raio, média de 2024-06 a 2025-06 (CNES a09,
   pré-programa). Distância pelo círculo máximo entre os centroides oficiais do IBGE já usados no script 17 (mesmo
   arquivo e hash). Na unidade município × ciclo, a medida é a média das CBO-alvo dos cursos com vaga imediata
   naquele município × ciclo, ponderada pelas vagas imediatas.

O resto do escore segue o 48d/48e: log(população 2022), médicos por 10 mil hab. no município, especialistas do
curso por 10 mil hab. no município. Regra de pareamento: a **literal** do 48e (o lado com menos unidades procura
par, ordem decrescente do escore, sem reposição, *caliper* 0,2 DP do logit do escore, exato no ciclo).
**Regra 2 do 48e** aplicada à UF: unidade de UF que, na janela daquele corte, só aparece de um lado sai antes do
logit, contada e listada.

## 2. Linhas

| Id | Linha | Papel |
|---|---|---|
| **PH-1** | H1 municipal (Y1: fração das células com vaga imediata preenchidas; Y2: alocados por vaga imediata), PSM exato em UF e capital, escore com o raio de 100 km, por corte, janela 0,050 | **principal** (4 linhas; Holm) |
| PH-2 | PH-1 com raio de 50 km e de 200 km | sensibilidade |
| PH-3 | PH-1 com exato na **região de saúde** (onde houver pares) | sensibilidade |
| PH-4 | RDD do 48b (HI-1 e HI-2) com efeito fixo de UF e o raio de 100 km como covariável (à CCFT) | comparação com a reta |
| PH-5 | **onde vem o médico:** Y2 dividido em alocados com origem (X1) na **mesma UF** da vaga e em **outra UF**, por PSM do PH-1 | secundária, descritiva: diz se a bolsa maior atrai médico de longe |
| PH-6 | balanço antes/depois de cada variável do escore e da UF; contagem de quem saiu pela regra 2 | diagnóstico |

BKY entre PH-2, PH-3 e PH-5.

## 3. Leitura pré-registrada

| Resultado | Leitura |
|---|---|
| PH-1 com IC que contém zero nos dois cortes e balanço depois do pareamento com \|DP\| ≤ 0,25 | comparando municípios da **mesma UF** e com o mesmo estoque de especialistas no entorno, não se detecta diferença de preenchimento no corte |
| alguma linha de PH-1 rejeita zero depois do Holm | relatar sinal e tamanho, com o pacote do corte e quem saiu pela regra 2 |
| a regra 2 tira mais de 25% de um lado num corte | a comparação daquele corte vale só para as UFs que aparecem dos dois lados |
| PH-5 com mais alocados de outra UF do lado de bolsa maior (IC sem zero) | indício de que a bolsa maior atrai médico de longe, mesmo sem mudar o total |

## 4. Saídas

| Item | Onde |
|---|---|
| script | `scripts/rdd_bolsa/49_pareamento_localizacao.py` (importa o 44 e o 45; não os reescreve) |
| estimativas | `output/rdd_bolsa/PL_estimativas.csv`, `PL_balanco.csv`, `PL_excluidos.csv`, `PL_resumo.json`, `PL_figuras/` |
| resultados | `docs/06_execucao/57w_resultados_pareamento_localizacao.md` (blocos gerados pelo script) |
| testes | `tests/test_pareamento_localizacao.py` |

**Portão:** reproduzir o PM-1 do 48e em 0,300 (≤ 1e−8) antes de qualquer conta nova; conferir o hash do arquivo
de centroides contra o manifesto do script 17.

## 5. Integridade

Nada imputado, adquirido ou escrito em `data/`; IVS oficial; nenhuma competência do CNES ≥ 2026-09; `HI_*`, `CL_*`,
`PM_*` e `PO_*` não são regravados. A origem do médico (X1) entra só como **outcome** (PH-5), nunca como controle:
ela é posterior à escolha.
