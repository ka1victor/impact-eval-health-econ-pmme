# 48c. Adendo: capitais e UF no corte 0,300 (H1)

> **Data de congelamento:** 26/10/2026, antes de rodar as contas deste
> adendo.<br>
> **Estatuto:** `ADENDO_48C_POS_RESULTADO`, robustez pós-resultado. Não muda a
> especificação principal (48b). Toda saída leva `natureza_dos_dados = EMPIRICO`.<br>
> **O que já foi visto** (auditorias 36 e 37):
> - Abaixo de 0,300 há 13 capitais e acima há 6. A até 0,010 do corte há 4
>   abaixo (São Paulo, Goiânia, Natal, Brasília) e nenhuma acima. Com uma
>   dummy de capital, o salto do A3, da taxa por vaga e do N1 em 0,300 encolhe
>   e passa a ter IC que contém zero (auditoria 36).
> - Na faixa de R$ 10 mil, as células do Norte e do Nordeste se concentram nos
>   últimos 0,050 antes de 0,300 (auditoria 37).

## 1. O que se estima

| Id | Linha |
|---|---|
| C-1 | **balanço no corte**: salto de "é capital" e de macrorregião (Nordeste; Norte), por município e por célula, em 0,300 e 0,400 |
| C-2 | HI-1 e HI-2 (48b) com dummy de capital |
| C-3 | HI-1 e HI-2 com efeito fixo de UF |
| C-4 | HI-1 e HI-2 sem as capitais |
| C-5 | as medidas antigas (A3, N1 com controle, taxa por vaga oferecida) com C-2, C-3 e C-4, para comparação |

- Especificação base do 48b: local linear, kernel triangular, h = 0,050, cada
  corte separado, ciclos empilhados com parâmetros por ciclo, CR1 por município.
- No ciclo 2, o tipo de vaga vem do quadro de 13/02/2026 (48b, §7).
- BKY entre as linhas C-2 a C-4.

## 2. Leitura pré-registrada

| Situação | Leitura |
|---|---|
| C-1 mostra salto em capital ou região, e C-2 a C-4 levam o salto da H1 a um IC que contém zero | a queda em 0,300 anda junto com a presença de capitais (ou região) logo abaixo do corte, que é desbalanceamento de poucos municípios grandes, e não com a bolsa |
| caso contrário | relatar como está |

Em qualquer caso é robustez pós-resultado. A violação de balanço em capital é
relatada como **limite da RDD** em 0,300.

## 3. Saídas

| Item | Onde |
|---|---|
| script | `scripts/rdd_bolsa/41_h1_capitais_uf.py` |
| saídas | `output/rdd_bolsa/HC_estimativas.csv`, `HC_resumo.json`, `HC_figuras/` |
| resultados | `docs/06_execucao/57o_h1_capitais_uf.md` |
| testes | `tests/test_h1_capitais_uf.py` |
