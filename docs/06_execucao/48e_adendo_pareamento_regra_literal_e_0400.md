# 48e. Adendo: pareamento pela regra literal do 48d e PSM em 0,400 sem as categorias de um lado só

> **Data de congelamento:** 26/10/2026, antes de rodar as contas deste adendo.<br>
> **Decisão do autor (26/10/2026):** aprovou as recomendações 1 e 2 da §2.16 de
> [`../07_apresentacoes/banca2/05_discussao_historia_empirica.md`](../07_apresentacoes/banca2/05_discussao_historia_empirica.md)
> ("ok, mas anota para fazer mesmo depois"; depois, "segue").<br>
> **Estatuto:** `ADENDO_48E_POS_RESULTADO`. Os resultados do 48d (doc 57r) e a
> auditoria 40 já foram vistos, inclusive a estimativa do PSM em 0,300 pela
> regra literal que a auditoria recalculou. Toda saída leva
> `natureza_dos_dados = EMPIRICO`.<br>
> **O que motiva:**
> - **achado 4 da auditoria 40:** o script 44 pareou pela regra gulosa global
>   (decisão 11 do 57r: o par mais próximo de todos primeiro), e não pela regra
>   da §3.1 do 48d ("o lado com menos municípios é o que procura par");
> - **achado 3 da auditoria 40:** pela decisão 13 do 57r, o PSM em 0,400 ficou
>   sem estimativa porque o logit não converge: na janela, capitais, Sul e
>   Centro-Oeste só aparecem abaixo do corte. A §3.2 do 48d previa tirar e
>   relatar quem ficasse fora do suporte.

## 1. O que muda em relação ao 48d

Tudo o que não está nesta seção segue o 48d (§3.1 e §3.2) e as decisões de
implementação do 57r, como auditadas.

**1. Regra de pareamento (principal).** Em cada corte e janela (e, na H1, em
cada ciclo), o lado com **menos** unidades procura par. As unidades desse lado
procuram par uma a uma:
- no PSM, em ordem **decrescente** do escore;
- no Mahalanobis, em ordem crescente do código IBGE do município (e do ciclo,
  na H1).

Cada uma fica com o vizinho mais próximo ainda livre do outro lado, dentro do
*caliper* (sem reposição). Se os dois lados tiverem o mesmo número de unidades,
procura par o lado de bolsa maior. A regra gulosa global do 48d passa a ser
**sensibilidade**.

**2. Categorias de um lado só (antes do logit).** Na janela de cada corte, uma
unidade sai da amostra do pareamento quando pertence a uma categoria de
**macrorregião** ou de **capital** que, naquela janela e naquela amostra (H1 ou
oferta local), só aparece de um dos lados do corte. Quem sai é contado e
**listado** (município, UF, ciclo, lado). A regra vale **nos dois cortes** e
nas duas janelas (0,050 e 0,020), para que 0,300 e 0,400 sigam a mesma
amostra-regra. Depois disso, o logit roda como no 48d. Se ainda não convergir
ou separar, a linha fica sem estimativa, como na decisão 13.

**3. Suporte comum:** continua o mínimo–máximo do 48d (decisão do 57r),
aplicado depois da regra 2.

## 2. Linhas

| Id | Linha | Papel |
|---|---|---|
| **PM-1** | PSM, regra literal, com a regra 2: H1 (fração preenchida das células com vaga imediata; alocados por vaga imediata), por corte, janela 0,050 | **principal** |
| **PM-2** | idem para a oferta local (ΔB1, ΔB2) | **principal** |
| PM-3 | PM-1 e PM-2 com a regra gulosa global do 48d, com a regra 2 | sensibilidade |
| PM-4 | PM-1 e PM-2 na janela 0,020 | sensibilidade |
| PM-5 | IPW (escore aparado em [0,05; 0,95]) na amostra da regra 2 | sensibilidade |
| PM-6 | Mahalanobis com a regra literal (e o *caliper* do 48d) | sensibilidade |
| PM-7 | ΔB3–ΔB5 da oferta local por PSM, regra literal | secundária |

**Holm** entre as oito linhas principais (PM-1 e PM-2: dois outcomes × dois
cortes cada). **BKY** entre as demais. Os resultados do 48d (doc 57r) não são
regravados e ficam lado a lado na figura principal.

## 3. Leitura pré-registrada

| Situação | Leitura |
|---|---|
| PM-1 e PM-2 com IC que contém zero nos dois cortes, balanço depois do pareamento com \|DP\| ≤ 0,25 | comparando municípios parecidos em localização e médicos na região, perto do corte, não se detecta diferença no preenchimento nem na oferta local |
| alguma linha principal rejeita zero depois do Holm | relatar sinal e tamanho, com o pacote do corte e as unidades que saíram pela regra 2 |
| a regra 2 tira mais de 25% das unidades de um lado num corte | relatar que a comparação daquele corte vale só para a parte comparável da janela (sem capitais, ou sem as regiões que saíram) |
| PM-3 (gulosa) e PM-1 (literal) com sinais opostos e IC que contêm zero | o ponto do pareamento depende da regra; ler só o intervalo |

## 4. Saídas

| Item | Onde |
|---|---|
| script | `scripts/rdd_bolsa/45_pareamento_regra_literal.py` (importa o 44; não o reescreve) |
| estimativas | `output/rdd_bolsa/PM_estimativas.csv`, `PM_balanco.csv`, `PM_excluidos.csv` (quem saiu pela regra 2), `PM_resumo.json`, `PM_figuras/` |
| resultados | `docs/06_execucao/57s_resultados_pareamento_regra_literal.md` (blocos gerados pelo script) |
| testes | `tests/test_pareamento_regra_literal.py` |

**Portão:** antes de qualquer conta nova, o script reproduz o PS-1 do 48d em
0,300 (regra gulosa, sem a regra 2) com diferença ≤ 1e−8, e a contagem de pares
do 48d (86 na H1, 88 na oferta local).

## 5. Integridade

As mesmas do 48d: nada imputado, adquirido ou escrito em `data/`; IVS oficial;
nenhuma competência do CNES ≥ 2026-09; `CL_*`, `HI_*` e `OC_*` não são
regravados.
