# Resultados do E6: funil da bolsa (famílias F0, F1, F2 e F4)

> **Data:** 18/10/2026.<br>
> **Protocolo:** [`40_protocolo_multioutcome_rdd_bolsa.md`](40_protocolo_multioutcome_rdd_bolsa.md)
> e [`protocolo_E6_multioutcome.json`](../../output/rdd_bolsa/protocolo_E6_multioutcome.json),
> congelados antes de abrir os outcomes novos (o SHA-256 do texto confere com o
> declarado; ver `protocolo` em `E6_resumo.json`).<br>
> **Outcomes:** construídos às cegas pela tarefa B
> ([`41a`](41a_construcao_outcomes_funil.md)).<br>
> **Script:** `scripts/rdd_bolsa/13_estimar_E6_funil.py` (estimadores de
> `scripts/rdd_bolsa/rdd_lib.py`).<br>
> **Saídas:** `output/rdd_bolsa/E6_estimativas.csv` (formato longo, uma linha
> por especificação), `E6_diagnosticos.csv`, `E6_lr_selecao_janela.csv`,
> `E6_resumo.json` (entradas com SHA-256, decisões, desvios, validações) e
> `E6_figuras/`.<br>
> **Testes:** `tests/test_e6_funil.py`.<br>
> **Natureza:** empírica. Nenhum número de resultado neste documento é
> digitado: as tabelas ficam entre marcadores `<!-- E6:... -->` e são
> regravadas das saídas por `13_estimar_E6_funil.py --atualizar-doc`; o teste
> confere que o conteúdo é idêntico ao gerado e que a prosa só contém
> parâmetros do protocolo.

## 1. O que o E6 estima e o que o contraste identifica

O E6 roda, para cada outcome das famílias F0, F1, F2 e F4, cada população
(U, G3, V1, V2, V3), cada corte (0,300 e 0,400) e os cortes empilhados, todas
as especificações do protocolo (§§6–7 e adendo §13): local linear triangular
com h = 0,050 (principal), h = 0,030 e 0,080, IC honesto de Armstrong e
Kolesár com M pela regra de bolso e 0,5M e 2M, local randomization com p de
Fisher na janela escolhida por balanço, e os estimadores por tipo (Poisson
local para contagens; ponderado por células e nível célula para proporções;
limites de Lee para F4.1). Os ciclos são empilhados com intercepto e
inclinações por ciclo (que contêm o efeito fixo de ciclo) e cluster por
município. O índice de atração-presença P1 junta F1.1, F1.2, F1.3 e F2.1.

**O contraste é um pacote.** Uma RDD em nível no corte mede tudo o que muda
ali. A auditoria 18
([`auditorias/18`](../auditorias/18_politicas_nos_mesmos_cortes_ivs.md)) e o
adendo §13 do protocolo mostram que, além da bolsa anunciada do PMM-E, mudam
nos mesmos cortes o teto de vagas de coparticipação do PMMB (Portaria
752/2023), o estrato do financiamento da APS em parte das classes de porte
(Portaria 3.493/2024), o teto de emendas e parcelas com "IVS maior que 0,3" e,
em 0,400, a ajuda de custo do PMMB fora da Amazônia Legal e da faixa de
fronteira. Portanto:

- nenhuma linha deste documento é o efeito da bolsa pura, nem da participação
  no PMM-E, nem do Agora Tem Especialistas;
- os outcomes do funil do candidato (F1.1, F1.2, F4.2) são os mais próximos da
  bolsa, porque as outras regras não mudam a remuneração do especialista do
  PMM-E; ainda assim, o lado da demanda municipal (vagas oferecidas) pode
  responder às outras regras;
- S3 (porte onde o estrato da APS muda × não muda) e S4 (Amazônia Legal ou
  faixa de fronteira × fora, em 0,400) tentam separar canais; são
  suplementares e têm pouca potência;
- a DiRD no CNES, que remove a parte fixa das outras descontinuidades, é o
  E7, não este documento.

## 2. Como ler o salto

Salto = valor estimado no corte do lado com bolsa maior (IVS acima do corte)
menos o do lado com bolsa menor; o próprio corte pertence ao lado de baixo:

- em 0,300, de R$ 10 mil para R$ 15 mil por mês;
- em 0,400, de R$ 15 mil para R$ 20 mil por mês.

Positivo significa mais do outcome onde a bolsa é maior. Para o índice P1, o
sinal foi pré-especificado: + = mais provimento. As frações aparecem em pontos
percentuais (p.p.), as contagens por célula ou por 10 mil habitantes na
própria escala, o Poisson local em log (efeito relativo = exp(salto) − 1) e o
índice em desvios-padrão do lado de baixo dentro da janela. A convenção de
sinal é testada: três linhas são recalculadas com numpy puro (reta ponderada
de cada lado, acima menos abaixo) e as linhas do E3 são reproduzidas
exatamente.

"Sem efeito detectável" quer dizer que o IC 95% contém zero, não que o efeito
é zero. Para cada linha, o maior efeito que o IC ainda admite é o limite
superior do IC (protocolo §7: referências de +10 p.p. de preenchimento e +25%
de candidaturas).

## 3. Diagnósticos antes de ler V_k

### 3.1 Seleção: ter vaga e número de células em U (F0.1 e F0.2)

V1, V2 e V3 são condicionadas a ter vaga. Se ter vaga saltasse no corte, a
comparação dentro de V_k misturaria efeito e seleção. A continuidade de F0.1 e
F0.2 em U (todos os municípios com IVS oficial) é, por isso, lida primeiro.

<!-- E6:selecao_F0:inicio -->
| Outcome | Ciclo | Corte | n abaixo / acima | Salto | IC 95% | p | q BKY |
|---|---|---|---|---|---|---|---|
| F0.1 `f0_1_tem_celula_c1` | 1 | 0,300 | 859 / 654 | −1,2 p.p. | [−6,2; +3,8] | 0,630 | 1,000 |
| F0.1 `f0_1_tem_celula_c1` | 1 | 0,400 | 587 / 603 | −5,3 p.p. | [−12,9; +2,2] | 0,164 | 1,000 |
| F0.1 `f0_1_tem_celula_c1` | 1 | empilhado | 1446 / 1257 | −3,0 p.p. | [−7,4; +1,3] | 0,171 | 1,000 |
| F0.1 `f0_1_tem_celula_c2` | 2 | 0,300 | 859 / 654 | −0,1 p.p. | [−6,6; +6,3] | 0,965 | 1,000 |
| F0.1 `f0_1_tem_celula_c2` | 2 | 0,400 | 587 / 603 | +0,4 p.p. | [−7,3; +8,1] | 0,920 | 1,000 |
| F0.1 `f0_1_tem_celula_c2` | 2 | empilhado | 1446 / 1257 | +0,1 p.p. | [−4,8; +5,0] | 0,971 | 1,000 |
| F0.1 `f0_1_tem_celula_c3` | 3 | 0,300 | 859 / 654 | −4,3 p.p. | [−11,4; +2,9] | 0,243 | 1,000 |
| F0.1 `f0_1_tem_celula_c3` | 3 | 0,400 | 587 / 603 | +0,4 p.p. | [−9,8; +10,6] | 0,940 | 1,000 |
| F0.1 `f0_1_tem_celula_c3` | 3 | empilhado | 1446 / 1257 | −2,2 p.p. | [−8,2; +3,8] | 0,468 | 1,000 |
| F0.2 `f0_2_celulas_por_10k_c1` | 1 | 0,300 | 859 / 654 | −0,008 | [−0,047; +0,031] | 0,692 | 1,000 |
| F0.2 `f0_2_celulas_por_10k_c1` | 1 | 0,400 | 587 / 603 | −0,091 | [−0,193; +0,012] | 0,085 | 1,000 |
| F0.2 `f0_2_celulas_por_10k_c1` | 1 | empilhado | 1446 / 1257 | −0,044 | [−0,094; +0,006] | 0,085 | 1,000 |
| F0.2 `f0_2_celulas_por_10k_c2` | 2 | 0,300 | 859 / 654 | +0,002 | [−0,048; +0,052] | 0,929 | 1,000 |
| F0.2 `f0_2_celulas_por_10k_c2` | 2 | 0,400 | 587 / 603 | −0,067 | [−0,248; +0,114] | 0,467 | 1,000 |
| F0.2 `f0_2_celulas_por_10k_c2` | 2 | empilhado | 1446 / 1257 | −0,028 | [−0,112; +0,056] | 0,512 | 1,000 |
| F0.2 `f0_2_celulas_por_10k_c3` | 3 | 0,300 | 859 / 654 | −0,023 | [−0,075; +0,029] | 0,386 | 1,000 |
| F0.2 `f0_2_celulas_por_10k_c3` | 3 | 0,400 | 587 / 603 | −0,059 | [−0,200; +0,081] | 0,407 | 1,000 |
| F0.2 `f0_2_celulas_por_10k_c3` | 3 | empilhado | 1446 / 1257 | −0,039 | [−0,107; +0,029] | 0,263 | 1,000 |
| F0.2 `f0_2_vagas_imediatas_por_10k_c1` | 1 | 0,300 | 859 / 654 | −0,006 | [−0,028; +0,016] | 0,615 | 1,000 |
| F0.2 `f0_2_vagas_imediatas_por_10k_c1` | 1 | 0,400 | 587 / 603 | −0,074 | [−0,134; −0,013] | 0,018 | 0,717 |
| F0.2 `f0_2_vagas_imediatas_por_10k_c1` | 1 | empilhado | 1446 / 1257 | −0,035 | [−0,065; −0,006] | 0,019 | 0,717 |
| F0.2 `f0_2_vagas_imediatas_por_10k_c2` | 2 | 0,300 | 859 / 654 | −0,040 | [−0,081; +0,001] | 0,057 | 1,000 |
| F0.2 `f0_2_vagas_imediatas_por_10k_c2` | 2 | 0,400 | 587 / 603 | −0,194 | [−0,568; +0,180] | 0,309 | 1,000 |
| F0.2 `f0_2_vagas_imediatas_por_10k_c2` | 2 | empilhado | 1446 / 1257 | −0,107 | [−0,273; +0,058] | 0,204 | 1,000 |
| F0.2 `f0_2_vagas_imediatas_por_10k_c3` | 3 | 0,300 | 859 / 654 | +0,012 | [−0,014; +0,038] | 0,365 | 1,000 |
| F0.2 `f0_2_vagas_imediatas_por_10k_c3` | 3 | 0,400 | 587 / 603 | −0,017 | [−0,092; +0,058] | 0,661 | 1,000 |
| F0.2 `f0_2_vagas_imediatas_por_10k_c3` | 3 | empilhado | 1446 / 1257 | −0,001 | [−0,037; +0,035] | 0,975 | 1,000 |
<!-- E6:selecao_F0:fim -->

### 3.2 Densidade e balanço de covariáveis (sem outcome)

Gravados antes de qualquer outcome (`E6_diagnosticos.csv`). Densidade: razão
das densidades de municípios dos dois lados (Poisson em mass points de 0,001,
estimador do E1/E3), h = 0,050.

<!-- E6:densidade:inicio -->
| População | Corte | n abaixo / acima | Razão de densidades | IC 95% | p |
|---|---|---|---|---|---|
| U | 0,300 | 859 / 671 | 0,99 | [0,79; 1,24] | 0,945 |
| U | 0,400 | 587 / 612 | 1,04 | [0,86; 1,25] | 0,678 |
| G3 | 0,300 | 399 / 279 | 0,97 | [0,71; 1,32] | 0,838 |
| G3 | 0,400 | 270 / 318 | 1,18 | [0,89; 1,57] | 0,240 |
| V1 | 0,300 | 61 / 54 | 0,93 | [0,40; 2,16] | 0,873 |
| V1 | 0,400 | 53 / 41 | 0,61 | [0,29; 1,30] | 0,201 |
| V2 | 0,300 | 82 / 62 | 1,09 | [0,58; 2,04] | 0,785 |
| V2 | 0,400 | 53 / 53 | 0,96 | [0,44; 2,11] | 0,927 |
| V3 | 0,300 | 102 / 83 | 0,81 | [0,43; 1,51] | 0,505 |
| V3 | 0,400 | 97 / 119 | 1,04 | [0,60; 1,82] | 0,888 |
<!-- E6:densidade:fim -->

Balanço (h = 0,050): subíndices do IVS, IDHM, população e renda per capita de
2010 (a08), população de 2022 (Censo), estrato territorial (A2) e
macrorregião. O próprio IVS não entra, porque é a running variable. Com cerca
de quinze covariáveis por população e corte, parte dos p < 0,05 é esperada por
acaso; os subíndices do IVS não são testes independentes.

<!-- E6:balanco:inicio -->
| População | Corte | Covariáveis testadas | p < 0,05 | Quais |
|---|---|---|---|---|
| U | 0,300 | 14 | 1 | estrato_capital (−0,025; p = 0,016) |
| U | 0,400 | 14 | 0 | — |
| G3 | 0,300 | 14 | 1 | estrato_capital (−0,055; p = 0,017) |
| G3 | 0,400 | 14 | 0 | — |
| V1 | 0,300 | 14 | 0 | — |
| V1 | 0,400 | 13 | 3 | ivs_ch_2010 (+0,036; p = 0,020), estrato_metropolitano (−0,245; p = 0,043), estrato_interior_proximo_polo (+0,388; p = 0,018) |
| V2 | 0,300 | 14 | 2 | estrato_capital (−0,224; p = 0,025), regiao_NE (−0,326; p = 0,038) |
| V2 | 0,400 | 14 | 0 | — |
| V3 | 0,300 | 14 | 0 | — |
| V3 | 0,400 | 13 | 0 | — |
<!-- E6:balanco:fim -->

### 3.3 Janelas de local randomization

Regra do E5 (só covariáveis, antes dos outcomes; `E6_lr_selecao_janela.csv`).
V1 e V2 usam a janela gravada pelo E5, e a recomputação a reproduz; U, G3 e
V3 recebem a mesma regra (desvio registrado).

<!-- E6:janelas_lr:inicio -->
| População | Corte | Janela (± IVS) |
|---|---|---|
| U | 0,300 | nenhuma passou no balanço |
| U | 0,400 | 0,008 |
| G3 | 0,300 | 0,003 |
| G3 | 0,400 | 0,007 |
| V1 | 0,300 | 0,020 |
| V1 | 0,400 | 0,007 |
| V2 | 0,300 | nenhuma passou no balanço |
| V2 | 0,400 | 0,006 |
| V3 | 0,300 | 0,002 |
| V3 | 0,400 | nenhuma passou no balanço |
<!-- E6:janelas_lr:fim -->

## 4. Hipótese primária P1: índice de atração-presença

P1 = índice de Kling, Liebman e Katz de F1.1, F1.2, F1.3 e F2.1, com ciclos e
cortes empilhados (h = 0,050, CR1 por município). No ciclo 3 não há F2.1, e o
índice de V3 tem três componentes (componente ausente não é imputado).

<!-- E6:p1_holm:inicio -->
p de P1 (para o Holm com P2 do E7): **0,426**; salto −0,13 DP, IC 95% [−0,44; +0,19].
<!-- E6:p1_holm:fim -->

O Holm entre P1 e P2 (F3.1 por DiRD, E7) é feito pelo coordenador (E8).

<!-- E6:indice_P1:inicio -->
| População | Corte | n abaixo / acima | Salto | IC 95% (CR1/HC1) | IC honesto | p |
|---|---|---|---|---|---|---|
| V1+V2+V3 | empilhado | 267 / 265 | −0,13 DP | [−0,44; +0,19] | [−22,50; +22,24] | 0,426 |
| V1+V2+V3 | 0,300 | 145 / 120 | −0,25 DP | [−0,67; +0,17] | [−21,10; +20,60] | 0,245 |
| V1+V2+V3 | 0,400 | 122 / 145 | −0,02 DP | [−0,49; +0,44] | [−20,15; +20,11] | 0,927 |
| V1 | empilhado | 114 / 94 | −0,03 DP | [−0,67; +0,61] | [−19,97; +19,91] | 0,930 |
| V1 | 0,300 | 61 / 53 | −0,25 DP | [−1,06; +0,57] | [−26,11; +25,61] | 0,554 |
| V1 | 0,400 | 53 / 41 | +0,15 DP | [−0,79; +1,10] | [−2,21; +2,52] | 0,753 |
| V2 | empilhado | 135 / 114 | −0,22 DP | [−0,73; +0,28] | [−22,52; +22,08] | 0,389 |
| V2 | 0,300 | 82 / 61 | −0,47 DP | [−1,16; +0,21] | [−16,78; +15,84] | 0,178 |
| V2 | 0,400 | 53 / 53 | +0,07 DP | [−0,68; +0,82] | [−20,43; +20,57] | 0,852 |
| V3 | empilhado | 199 / 200 | −0,12 DP | [−0,50; +0,27] | [−16,95; +16,71] | 0,554 |
| V3 | 0,300 | 102 / 82 | −0,08 DP | [−0,59; +0,43] | [−8,45; +8,30] | 0,764 |
| V3 | 0,400 | 97 / 118 | −0,15 DP | [−0,70; +0,41] | [−16,30; +16,01] | 0,609 |
<!-- E6:indice_P1:fim -->

**IC honesto.** Com o M da regra de bolso do protocolo (quártica global por
lado, com o suporte de cada corte indo até o ponto médio entre os cortes), o
lado que fica entre os dois cortes tem só a faixa de 0,050 até o ponto médio, e
a quártica ajustada nela tem curvatura muito grande. O M resultante torna os
IC honestos muito largos, em geral sem informação. A tabela abaixo mostra o M
de cada lado para os componentes do índice e para o índice (o mesmo M entra nas
linhas do índice empilhado como máximo entre grupos). O protocolo fixa essa
regra; nenhuma outra escolha de M é feita depois de ver os resultados.

<!-- E6:diagnostico_M:inicio -->
| Outcome | População | Corte | Suporte (milésimos) | mass points abaixo / acima | M abaixo | M acima |
|---|---|---|---|---|---|---|
| F1.1 | V1 | 0,300 | [−∞; 350] | 97 / 33 | 3707,4 | 18880,9 |
| F1.1 | V1 | 0,400 | [350; +∞] | 37 / 83 | 5566,4 | 326,9 |
| F1.1 | V2 | 0,300 | [−∞; 350] | 115 / 37 | 1099,0 | 17904,6 |
| F1.1 | V2 | 0,400 | [350; +∞] | 34 / 90 | 78826,4 | 769,4 |
| F1.1 | V3 | 0,300 | [−∞; 350] | 139 / 41 | 1144,6 | 46488,4 |
| F1.1 | V3 | 0,400 | [350; +∞] | 43 / 153 | 26289,2 | 309,1 |
| F1.2 | V1 | 0,300 | [−∞; 350] | 97 / 33 | 1022,4 | 11846,0 |
| F1.2 | V1 | 0,400 | [350; +∞] | 37 / 83 | 5218,0 | 223,4 |
| F1.2 | V2 | 0,300 | [−∞; 350] | 115 / 37 | 640,0 | 18365,9 |
| F1.2 | V2 | 0,400 | [350; +∞] | 34 / 90 | 17975,9 | 294,1 |
| F1.2 | V3 | 0,300 | [−∞; 350] | 139 / 41 | 1070,8 | 11423,1 |
| F1.2 | V3 | 0,400 | [350; +∞] | 43 / 153 | 9303,4 | 426,7 |
| F1.3 | V1 | 0,300 | [−∞; 350] | 97 / 33 | 642,6 | 10719,8 |
| F1.3 | V1 | 0,400 | [350; +∞] | 37 / 83 | 5920,0 | 385,9 |
| F1.3 | V2 | 0,300 | [−∞; 350] | 115 / 37 | 532,0 | 21015,3 |
| F1.3 | V2 | 0,400 | [350; +∞] | 34 / 90 | 11637,0 | 276,4 |
| F1.3 | V3 | 0,300 | [−∞; 350] | 139 / 41 | 729,6 | 7760,0 |
| F1.3 | V3 | 0,400 | [350; +∞] | 43 / 153 | 21378,3 | 157,2 |
| F2.1 | V1 | 0,300 | [−∞; 350] | 97 / 33 | 486,1 | 37868,1 |
| F2.1 | V1 | 0,400 | [350; +∞] | 37 / 83 | 15020,5 | 273,2 |
| F2.1 | V2 | 0,300 | [−∞; 350] | 115 / 37 | 367,0 | 6471,6 |
| F2.1 | V2 | 0,400 | [350; +∞] | 34 / 90 | 63157,9 | 34,0 |
| P1 | V1 | 0,300 | [−∞; 350] | 97 / 33 | 1984,4 | 41176,5 |
| P1 | V1 | 0,400 | [350; +∞] | 37 / 83 | 4233,2 | 497,2 |
| P1 | V2 | 0,300 | [−∞; 350] | 115 / 37 | 1183,5 | 33219,8 |
| P1 | V2 | 0,400 | [350; +∞] | 34 / 90 | 49830,6 | 408,1 |
| P1 | V3 | 0,300 | [−∞; 350] | 139 / 41 | 2229,7 | 17241,5 |
| P1 | V3 | 0,400 | [350; +∞] | 43 / 153 | 38084,7 | 573,9 |
<!-- E6:diagnostico_M:fim -->

Sensibilidades de P1 (ciclos e cortes empilhados):

<!-- E6:indice_P1_sensibilidade:inicio -->
| Especificação | h | M | Salto | IC 95% | p |
|---|---|---|---|---|---|
| sensibilidade_h | 0,030 | — | −0,17 DP | [−0,58; +0,25] | 0,438 |
| sensibilidade_h | 0,080 | — | +0,02 DP | [−0,24; +0,28] | 0,856 |
| ic_honesto | 0,050 | 0,5 × M | −0,13 DP | [−11,44; +11,19] | 1,000 |
| ic_honesto | 0,050 | 1,0 × M | −0,13 DP | [−22,50; +22,24] | 1,000 |
| ic_honesto | 0,050 | 2,0 × M | −0,13 DP | [−44,60; +44,34] | 1,000 |
| S2_donut | 0,050 | — | −0,05 DP | [−0,36; +0,26] | 0,748 |
| indice_anderson (Anderson) | 0,050 | — | −0,15 DP | [−0,47; +0,17] | 0,373 |
<!-- E6:indice_P1_sensibilidade:fim -->

## 5. Componentes e secundárias

Linhas principais (h = 0,050); o q é o BKY dentro da família, sobre todas as
linhas principais do protocolo daquela família (cada outcome × população ×
ciclo × corte, cortes e ciclos empilhados incluídos).

<!-- E6:resumo_testes:inicio -->
| Família | Linhas principais no BKY | p < 0,05 | q BKY < 0,05 | menor p | menor q |
|---|---|---|---|---|---|
| F0 | 45 | 2 | 0 | 0,018 | 0,717 |
| F1 | 45 | 0 | 0 | 0,057 | 1,000 |
| F2 | 24 | 1 | 0 | 0,019 | 0,828 |
| F4 | 24 | 2 | 0 | 0,035 | 0,830 |
| S2–S4, todos os outcomes (fora do BKY) | 612 | 30 | — | 0,001 | — |
<!-- E6:resumo_testes:fim -->

Linhas principais com p < 0,05 (antes da correção):

<!-- E6:principais_p_menor_005:inicio -->
| Família | Outcome | População | Ciclo | Corte | Salto | IC 95% | IC honesto | p | q BKY |
|---|---|---|---|---|---|---|---|---|---|
| F0 | F0.2 `f0_2_vagas_imediatas_por_10k_c1` | U | 1 | 0,400 | −0,074 | [−0,134; −0,013] | [−1,154; +1,007] | 0,018 | 0,717 |
| F0 | F0.2 `f0_2_vagas_imediatas_por_10k_c1` | U | 1 | empilhado | −0,035 | [−0,065; −0,006] | [−1,076; +1,005] | 0,019 | 0,717 |
| F2 | F2.2 `f2_2_ativos_pmme_por_10k_c2` | U | 2 | 0,300 | −0,025 | [−0,046; −0,004] | [−0,785; +0,735] | 0,019 | 0,828 |
| F4 | F4.2 `f4_2_pontuacao_media_cand_1a_opcao` | V3 | 3 | empilhado | −0,639 | [−1,259; −0,019] | [−8,805; +7,527] | 0,043 | 0,830 |
| F4 | F4.2 `f4_2_pontuacao_media_cand_1a_opcao` | V1+V2+V3 | 1+2+3 | empilhado | −0,453 | [−0,873; −0,033] | [−21,982; +21,076] | 0,035 | 0,830 |
<!-- E6:principais_p_menor_005:fim -->

### 5.1 F1: atração

<!-- E6:componentes_F1:inicio -->
| Outcome | População | Ciclo | Corte | n abaixo / acima | Salto | IC 95% | IC honesto | p | q BKY |
|---|---|---|---|---|---|---|---|---|---|
| F1.1 | V1 | 1 | 0,300 | 61 / 53 | −0,646 | [−2,173; +0,881] | [−13,485; +12,193] | 0,407 | 1,000 |
| F1.1 | V1 | 1 | 0,400 | 53 / 41 | +0,626 | [−0,873; +2,124] | [−2,670; +3,921] | 0,413 | 1,000 |
| F1.1 | V1 | 1 | empilhado | 114 / 94 | +0,051 | [−1,035; +1,137] | [−9,758; +9,860] | 0,927 | 1,000 |
| F1.1 | V2 | 2 | 0,300 | 82 / 61 | −0,324 | [−1,168; +0,520] | [−9,522; +8,874] | 0,452 | 1,000 |
| F1.1 | V2 | 2 | 0,400 | 53 / 53 | +0,067 | [−2,110; +2,243] | [−33,286; +33,419] | 0,952 | 1,000 |
| F1.1 | V2 | 2 | empilhado | 135 / 114 | −0,145 | [−1,241; +0,952] | [−35,669; +35,380] | 0,796 | 1,000 |
| F1.1 | V3 | 3 | 0,300 | 102 / 82 | +0,058 | [−0,537; +0,653] | [−21,868; +21,984] | 0,848 | 1,000 |
| F1.1 | V3 | 3 | 0,400 | 97 / 118 | +0,301 | [−0,729; +1,331] | [−11,419; +12,021] | 0,567 | 1,000 |
| F1.1 | V3 | 3 | empilhado | 199 / 200 | +0,197 | [−0,445; +0,840] | [−20,488; +20,883] | 0,547 | 1,000 |
| F1.1 | V1+V2+V3 | 1+2+3 | 0,300 | 145 / 120 | −0,227 | [−0,786; +0,332] | [−23,833; +23,379] | 0,426 | 1,000 |
| F1.1 | V1+V2+V3 | 1+2+3 | 0,400 | 122 / 145 | +0,316 | [−0,637; +1,268] | [−31,717; +32,349] | 0,516 | 1,000 |
| F1.1 | V1+V2+V3 | 1+2+3 | empilhado | 267 / 265 | +0,063 | [−0,511; +0,636] | [−35,382; +35,507] | 0,830 | 1,000 |
| F1.2 | V1 | 1 | 0,300 | 61 / 53 | −10,8 p.p. | [−42,7; +21,1] | [−761,9; +740,3] | 0,508 | 1,000 |
| F1.2 | V1 | 1 | 0,400 | 53 / 41 | +3,6 p.p. | [−29,0; +36,2] | [−211,6; +218,8] | 0,828 | 1,000 |
| F1.2 | V1 | 1 | empilhado | 114 / 94 | −2,9 p.p. | [−26,0; +20,2] | [−580,5; +574,7] | 0,806 | 1,000 |
| F1.2 | V2 | 2 | 0,300 | 82 / 61 | −21,2 p.p. | [−46,4; +4,0] | [−909,7; +867,4] | 0,100 | 1,000 |
| F1.2 | V2 | 2 | 0,400 | 53 / 53 | +13,2 p.p. | [−11,8; +38,2] | [−726,4; +752,8] | 0,302 | 1,000 |
| F1.2 | V2 | 2 | empilhado | 135 / 114 | −5,4 p.p. | [−23,6; +12,8] | [−826,9; +816,1] | 0,561 | 1,000 |
| F1.2 | V3 | 3 | 0,300 | 102 / 82 | −11,5 p.p. | [−36,8; +13,8] | [−559,4; +536,5] | 0,374 | 1,000 |
| F1.2 | V3 | 3 | 0,400 | 97 / 118 | −8,8 p.p. | [−33,5; +15,8] | [−413,8; +396,1] | 0,482 | 1,000 |
| F1.2 | V3 | 3 | empilhado | 199 / 200 | −10,0 p.p. | [−27,7; +7,8] | [−519,9; +500,0] | 0,272 | 1,000 |
| F1.2 | V1+V2+V3 | 1+2+3 | 0,300 | 145 / 120 | −14,7 p.p. | [−32,0; +2,7] | [−943,3; +913,9] | 0,097 | 1,000 |
| F1.2 | V1+V2+V3 | 1+2+3 | 0,400 | 122 / 145 | −0,3 p.p. | [−16,5; +15,8] | [−726,1; +725,5] | 0,968 | 1,000 |
| F1.2 | V1+V2+V3 | 1+2+3 | empilhado | 267 / 265 | −7,0 p.p. | [−18,9; +4,9] | [−831,6; +817,6] | 0,247 | 1,000 |
| F1.3 | V1 | 1 | 0,300 | 61 / 53 | −12,8 p.p. | [−45,5; +19,8] | [−695,4; +669,7] | 0,441 | 1,000 |
| F1.3 | V1 | 1 | 0,400 | 53 / 41 | −5,1 p.p. | [−36,5; +26,2] | [−244,7; +234,4] | 0,748 | 1,000 |
| F1.3 | V1 | 1 | empilhado | 114 / 94 | −8,6 p.p. | [−31,2; +14,0] | [−532,8; +515,5] | 0,454 | 1,000 |
| F1.3 | V2 | 2 | 0,300 | 82 / 61 | −20,3 p.p. | [−48,2; +7,7] | [−1038,7; +998,1] | 0,155 | 1,000 |
| F1.3 | V2 | 2 | 0,400 | 53 / 53 | +12,2 p.p. | [−13,8; +38,3] | [−473,9; +498,4] | 0,358 | 1,000 |
| F1.3 | V2 | 2 | empilhado | 135 / 114 | −5,4 p.p. | [−24,8; +14,1] | [−944,2; +933,5] | 0,588 | 1,000 |
| F1.3 | V3 | 3 | 0,300 | 102 / 82 | +0,2 p.p. | [−16,5; +16,9] | [−372,4; +372,8] | 0,980 | 1,000 |
| F1.3 | V3 | 3 | 0,400 | 97 / 118 | −13,8 p.p. | [−31,5; +3,9] | [−908,0; +880,4] | 0,126 | 1,000 |
| F1.3 | V3 | 3 | empilhado | 199 / 200 | −7,8 p.p. | [−20,4; +4,7] | [−944,8; +929,1] | 0,222 | 1,000 |
| F1.3 | V1+V2+V3 | 1+2+3 | 0,300 | 145 / 120 | −9,7 p.p. | [−24,9; +5,5] | [−1068,4; +1049,0] | 0,212 | 1,000 |
| F1.3 | V1+V2+V3 | 1+2+3 | 0,400 | 122 / 145 | −5,1 p.p. | [−20,1; +9,8] | [−864,8; +854,5] | 0,501 | 1,000 |
| F1.3 | V1+V2+V3 | 1+2+3 | empilhado | 267 / 265 | −7,3 p.p. | [−17,9; +3,4] | [−964,4; +949,9] | 0,181 | 1,000 |
| F1.4 | V1 | 1 | 0,300 | 61 / 53 | −8,9 p.p. | [−42,7; +24,9] | [−980,0; +962,1] | 0,604 | 1,000 |
| F1.4 | V1 | 1 | 0,400 | 53 / 41 | −7,8 p.p. | [−38,5; +22,9] | [−123,2; +107,6] | 0,619 | 1,000 |
| F1.4 | V1 | 1 | empilhado | 114 / 94 | −8,3 p.p. | [−31,0; +14,4] | [−753,9; +737,2] | 0,472 | 1,000 |
| F1.4 | V2 | 2 | 0,300 | 82 / 61 | −27,3 p.p. | [−55,4; +0,8] | [−774,4; +719,8] | 0,057 | 1,000 |
| F1.4 | V2 | 2 | 0,400 | 53 / 53 | +15,1 p.p. | [−9,2; +39,4] | [−253,9; +284,1] | 0,223 | 1,000 |
| F1.4 | V2 | 2 | empilhado | 135 / 114 | −7,8 p.p. | [−27,0; +11,4] | [−694,6; +679,0] | 0,425 | 1,000 |
| F1.4 | V1+V2 | 1+2 | 0,300 | 100 / 80 | −20,2 p.p. | [−42,5; +2,2] | [−849,3; +809,0] | 0,077 | 1,000 |
| F1.4 | V1+V2 | 1+2 | 0,400 | 69 / 71 | +4,2 p.p. | [−17,2; +25,7] | [−251,5; +260,0] | 0,699 | 1,000 |
| F1.4 | V1+V2 | 1+2 | empilhado | 169 / 151 | −8,0 p.p. | [−23,6; +7,6] | [−719,3; +703,2] | 0,313 | 1,000 |
<!-- E6:componentes_F1:fim -->

### 5.2 F2: presença

<!-- E6:componentes_F2:inicio -->
| Outcome | População | Ciclo | Corte | n abaixo / acima | Salto | IC 95% | IC honesto | p | q BKY |
|---|---|---|---|---|---|---|---|---|---|
| F2.1 | V1 | 1 | 0,300 | 61 / 53 | +0,026 | [−0,555; +0,607] | [−23,624; +23,676] | 0,930 | 1,000 |
| F2.1 | V1 | 1 | 0,400 | 53 / 41 | +0,041 | [−0,784; +0,867] | [−6,060; +6,142] | 0,922 | 1,000 |
| F2.1 | V1 | 1 | empilhado | 114 / 94 | +0,034 | [−0,487; +0,556] | [−18,249; +18,317] | 0,897 | 1,000 |
| F2.1 | V2 | 2 | 0,300 | 82 / 61 | −0,194 | [−0,607; +0,219] | [−3,622; +3,234] | 0,357 | 1,000 |
| F2.1 | V2 | 2 | 0,400 | 53 / 53 | −0,349 | [−1,211; +0,512] | [−26,195; +25,497] | 0,427 | 1,000 |
| F2.1 | V2 | 2 | empilhado | 135 / 114 | −0,265 | [−0,720; +0,190] | [−28,373; +27,842] | 0,253 | 1,000 |
| F2.1 | V1+V2 | 1+2 | 0,300 | 100 / 80 | −0,109 | [−0,461; +0,243] | [−20,310; +20,092] | 0,544 | 1,000 |
| F2.1 | V1+V2 | 1+2 | 0,400 | 69 / 71 | −0,164 | [−0,783; +0,455] | [−24,640; +24,312] | 0,604 | 1,000 |
| F2.1 | V1+V2 | 1+2 | empilhado | 169 / 151 | −0,136 | [−0,491; +0,218] | [−29,036; +28,764] | 0,451 | 1,000 |
| F2.2 | U | 1 | 0,300 | 859 / 654 | +0,001 | [−0,021; +0,023] | [−0,647; +0,649] | 0,917 | 1,000 |
| F2.2 | U | 1 | 0,400 | 587 / 603 | −0,020 | [−0,154; +0,113] | [−2,208; +2,167] | 0,765 | 1,000 |
| F2.2 | U | 1 | empilhado | 1446 / 1257 | −0,008 | [−0,068; +0,051] | [−2,108; +2,091] | 0,786 | 1,000 |
| F2.2 | U | 2 | 0,300 | 859 / 654 | −0,025 | [−0,046; −0,004] | [−0,785; +0,735] | 0,019 | 0,828 |
| F2.2 | U | 2 | 0,400 | 587 / 603 | −0,148 | [−0,513; +0,217] | [−11,019; +10,723] | 0,426 | 1,000 |
| F2.2 | U | 2 | empilhado | 1446 / 1257 | −0,079 | [−0,239; +0,081] | [−10,644; +10,486] | 0,334 | 1,000 |
| F2.3 | V1 | 1 | 0,300 | 61 / 53 | −3,2 p.p. | [−47,5; +41,1] | [−918,6; +912,2] | 0,887 | 1,000 |
| F2.3 | V1 | 1 | 0,400 | 53 / 41 | −12,0 p.p. | [−53,1; +29,0] | [−462,3; +438,2] | 0,566 | 1,000 |
| F2.3 | V1 | 1 | empilhado | 114 / 94 | −8,0 p.p. | [−38,1; +22,0] | [−709,1; +693,0] | 0,600 | 1,000 |
| F2.3 | V2 | 2 | 0,300 | 82 / 61 | −15,2 p.p. | [−51,6; +21,1] | [−715,2; +684,7] | 0,411 | 1,000 |
| F2.3 | V2 | 2 | 0,400 | 53 / 53 | +11,5 p.p. | [−13,9; +36,9] | [−466,2; +489,2] | 0,376 | 1,000 |
| F2.3 | V2 | 2 | empilhado | 135 / 114 | −3,0 p.p. | [−25,7; +19,8] | [−642,9; +637,0] | 0,798 | 1,000 |
| F2.3 | V1+V2 | 1+2 | 0,300 | 100 / 80 | −10,6 p.p. | [−41,4; +20,3] | [−790,4; +769,2] | 0,501 | 1,000 |
| F2.3 | V1+V2 | 1+2 | 0,400 | 69 / 71 | +0,3 p.p. | [−24,5; +25,2] | [−458,6; +459,3] | 0,978 | 1,000 |
| F2.3 | V1+V2 | 1+2 | empilhado | 169 / 151 | −5,2 p.p. | [−25,0; +14,7] | [−671,3; +661,0] | 0,610 | 1,000 |
<!-- E6:componentes_F2:fim -->

### 5.3 O que o IC ainda admite (referências do protocolo §7)

<!-- E6:referencias_magnitude:inicio -->
| Outcome | População | Ciclo | Corte | Referência | Limite superior do IC 95% | IC 95% exclui a referência? |
|---|---|---|---|---|---|---|
| F1.2 | V1 | 1 | 0,300 | +10 p.p. | +21,1 p.p. | não |
| F1.2 | V1 | 1 | 0,400 | +10 p.p. | +36,2 p.p. | não |
| F1.2 | V1 | 1 | empilhado | +10 p.p. | +20,2 p.p. | não |
| F1.2 | V2 | 2 | 0,300 | +10 p.p. | +4,0 p.p. | sim |
| F1.2 | V2 | 2 | 0,400 | +10 p.p. | +38,2 p.p. | não |
| F1.2 | V2 | 2 | empilhado | +10 p.p. | +12,8 p.p. | não |
| F1.2 | V3 | 3 | 0,300 | +10 p.p. | +13,8 p.p. | não |
| F1.2 | V3 | 3 | 0,400 | +10 p.p. | +15,8 p.p. | não |
| F1.2 | V3 | 3 | empilhado | +10 p.p. | +7,8 p.p. | sim |
| F1.2 | V1+V2+V3 | 1+2+3 | 0,300 | +10 p.p. | +2,7 p.p. | sim |
| F1.2 | V1+V2+V3 | 1+2+3 | 0,400 | +10 p.p. | +15,8 p.p. | não |
| F1.2 | V1+V2+V3 | 1+2+3 | empilhado | +10 p.p. | +4,9 p.p. | sim |
| F1.3 | V1 | 1 | 0,300 | +10 p.p. | +19,8 p.p. | não |
| F1.3 | V1 | 1 | 0,400 | +10 p.p. | +26,2 p.p. | não |
| F1.3 | V1 | 1 | empilhado | +10 p.p. | +14,0 p.p. | não |
| F1.3 | V2 | 2 | 0,300 | +10 p.p. | +7,7 p.p. | sim |
| F1.3 | V2 | 2 | 0,400 | +10 p.p. | +38,3 p.p. | não |
| F1.3 | V2 | 2 | empilhado | +10 p.p. | +14,1 p.p. | não |
| F1.3 | V3 | 3 | 0,300 | +10 p.p. | +16,9 p.p. | não |
| F1.3 | V3 | 3 | 0,400 | +10 p.p. | +3,9 p.p. | sim |
| F1.3 | V3 | 3 | empilhado | +10 p.p. | +4,7 p.p. | sim |
| F1.3 | V1+V2+V3 | 1+2+3 | 0,300 | +10 p.p. | +5,5 p.p. | sim |
| F1.3 | V1+V2+V3 | 1+2+3 | 0,400 | +10 p.p. | +9,8 p.p. | sim |
| F1.3 | V1+V2+V3 | 1+2+3 | empilhado | +10 p.p. | +3,4 p.p. | sim |
| F1.4 | V1 | 1 | 0,300 | +10 p.p. | +24,9 p.p. | não |
| F1.4 | V1 | 1 | 0,400 | +10 p.p. | +22,9 p.p. | não |
| F1.4 | V1 | 1 | empilhado | +10 p.p. | +14,4 p.p. | não |
| F1.4 | V2 | 2 | 0,300 | +10 p.p. | +0,8 p.p. | sim |
| F1.4 | V2 | 2 | 0,400 | +10 p.p. | +39,4 p.p. | não |
| F1.4 | V2 | 2 | empilhado | +10 p.p. | +11,4 p.p. | não |
| F1.4 | V1+V2 | 1+2 | 0,300 | +10 p.p. | +2,2 p.p. | sim |
| F1.4 | V1+V2 | 1+2 | 0,400 | +10 p.p. | +25,7 p.p. | não |
| F1.4 | V1+V2 | 1+2 | empilhado | +10 p.p. | +7,6 p.p. | sim |
| F1.1 (Poisson) | V1 | 1 | 0,300 | +25 % | +60,7 % | não |
| F1.1 (Poisson) | V1 | 1 | 0,400 | +25 % | +718,4 % | não |
| F1.1 (Poisson) | V2 | 2 | 0,300 | +25 % | +0,4 % | sim |
| F1.1 (Poisson) | V2 | 2 | 0,400 | +25 % | +105,0 % | não |
| F1.1 (Poisson) | V3 | 3 | 0,300 | +25 % | +9,5 % | sim |
| F1.1 (Poisson) | V3 | 3 | 0,400 | +25 % | +81,9 % | não |
<!-- E6:referencias_magnitude:fim -->

### 5.4 Contagens em escala log (Poisson local)

<!-- E6:poisson:inicio -->
| Outcome | População | Ciclo | Corte | Salto em log | Efeito relativo | IC 95% (relativo) | p |
|---|---|---|---|---|---|---|---|
| F1.1 | V1 | 1 | 0,300 | −0,694 | −50,0 % | [−84,5; +60,7] | 0,244 |
| F1.1 | V1 | 1 | 0,400 | +0,691 | +99,5 % | [−51,4; +718,4] | 0,338 |
| F1.1 | V2 | 2 | 0,300 | −0,741 | −52,3 % | [−77,4; +0,4] | 0,051 |
| F1.1 | V2 | 2 | 0,400 | −0,012 | −1,1 % | [−52,3; +105,0] | 0,975 |
| F1.1 | V3 | 3 | 0,300 | −0,543 | −41,9 % | [−69,2; +9,5] | 0,093 |
| F1.1 | V3 | 3 | 0,400 | −0,060 | −5,8 % | [−51,2; +81,9] | 0,858 |
| F2.1 | V1 | 1 | 0,300 | +0,342 | +40,8 % | [−51,4; +307,8] | 0,528 |
| F2.1 | V1 | 1 | 0,400 | +0,149 | +16,0 % | [−65,9; +294,6] | 0,812 |
| F2.1 | V2 | 2 | 0,300 | −0,513 | −40,2 % | [−71,1; +23,8] | 0,166 |
| F2.1 | V2 | 2 | 0,400 | −0,283 | −24,7 % | [−56,7; +31,0] | 0,315 |
| F2.2 | U | 1 | 0,300 | +1,352 | +286,7 % | [−35,4; +2214,1] | 0,138 |
| F2.2 | U | 1 | 0,400 | −0,602 | −45,2 % | [−87,0; +131,3] | 0,413 |
| F2.2 | U | 2 | 0,300 | +0,177 | +19,3 % | [−76,0; +493,4] | 0,829 |
| F2.2 | U | 2 | 0,400 | −0,727 | −51,6 % | [−86,7; +75,9] | 0,270 |
<!-- E6:poisson:fim -->

### 5.5 F4: quem chega (sinal teórico ambíguo, fora do índice)

F4.1 é condicional a preencher: a linha principal compara só municípios com
alguma célula preenchida; os limites de Lee tratam a seleção.

<!-- E6:componentes_F4:inicio -->
| Outcome | População | Ciclo | Corte | n abaixo / acima | Salto | IC 95% | IC honesto | p | q BKY |
|---|---|---|---|---|---|---|---|---|---|
| F4.1 | V1 | 1 | 0,300 | 31 / 35 | +0,158 | [−1,581; +1,896] | [−3,222; +3,538] | 0,859 | 1,000 |
| F4.1 | V1 | 1 | 0,400 | 42 / 25 | +0,191 | [−1,325; +1,707] | [−16,999; +17,381] | 0,805 | 1,000 |
| F4.1 | V1 | 1 | empilhado | 73 / 60 | +0,177 | [−0,962; +1,315] | [−20,839; +21,192] | 0,761 | 1,000 |
| F4.1 | V2 | 2 | 0,300 | 54 / 45 | −0,456 | [−1,687; +0,775] | [−20,962; +20,051] | 0,468 | 1,000 |
| F4.1 | V2 | 2 | 0,400 | 42 / 45 | −0,286 | [−1,409; +0,838] | [−13,311; +12,740] | 0,618 | 1,000 |
| F4.1 | V2 | 2 | empilhado | 96 / 90 | −0,367 | [−1,197; +0,462] | [−18,235; +17,500] | 0,385 | 0,953 |
| F4.1 | V3 | 3 | 0,300 | 42 / 33 | −0,886 | [−2,346; +0,575] | [−21,691; +19,920] | 0,235 | 0,830 |
| F4.1 | V3 | 3 | 0,400 | 30 / 35 | −1,007 | [−2,488; +0,475] | [−32,440; +30,427] | 0,183 | 0,830 |
| F4.1 | V3 | 3 | empilhado | 72 / 68 | −0,950 | [−1,990; +0,091] | [−36,351; +34,451] | 0,074 | 0,830 |
| F4.1 | V1+V2+V3 | 1+2+3 | 0,300 | 80 / 73 | −0,435 | [−1,187; +0,318] | [−22,432; +21,563] | 0,257 | 0,830 |
| F4.1 | V1+V2+V3 | 1+2+3 | 0,400 | 75 / 76 | −0,363 | [−1,140; +0,415] | [−29,370; +28,645] | 0,360 | 0,953 |
| F4.1 | V1+V2+V3 | 1+2+3 | empilhado | 155 / 149 | −0,396 | [−0,939; +0,147] | [−34,102; +33,309] | 0,152 | 0,830 |
| F4.2 | V1 | 1 | 0,300 | 35 / 37 | +0,104 | [−1,342; +1,551] | [−11,274; +11,482] | 0,888 | 1,000 |
| F4.2 | V1 | 1 | 0,400 | 41 / 27 | −0,275 | [−1,537; +0,988] | [−13,702; +13,153] | 0,670 | 1,000 |
| F4.2 | V1 | 1 | empilhado | 76 / 64 | −0,109 | [−1,055; +0,836] | [−16,822; +16,604] | 0,821 | 1,000 |
| F4.2 | V2 | 2 | 0,300 | 53 / 44 | −0,432 | [−1,526; +0,662] | [−9,022; +8,158] | 0,439 | 1,000 |
| F4.2 | V2 | 2 | 0,400 | 40 / 45 | −0,461 | [−1,473; +0,550] | [−18,933; +18,011] | 0,372 | 0,953 |
| F4.2 | V2 | 2 | empilhado | 93 / 89 | −0,448 | [−1,188; +0,293] | [−21,547; +20,652] | 0,236 | 0,830 |
| F4.2 | V3 | 3 | 0,300 | 72 / 47 | −0,587 | [−1,558; +0,384] | [−9,764; +8,590] | 0,236 | 0,830 |
| F4.2 | V3 | 3 | 0,400 | 51 / 71 | −0,684 | [−1,485; +0,118] | [−5,209; +3,842] | 0,094 | 0,830 |
| F4.2 | V3 | 3 | empilhado | 123 / 118 | −0,639 | [−1,259; −0,019] | [−8,805; +7,527] | 0,043 | 0,830 |
| F4.2 | V1+V2+V3 | 1+2+3 | 0,300 | 100 / 75 | −0,381 | [−0,994; +0,232] | [−9,823; +9,060] | 0,223 | 0,830 |
| F4.2 | V1+V2+V3 | 1+2+3 | 0,400 | 80 / 101 | −0,513 | [−1,089; +0,063] | [−19,293; +18,267] | 0,081 | 0,830 |
| F4.2 | V1+V2+V3 | 1+2+3 | empilhado | 180 / 176 | −0,453 | [−0,873; −0,033] | [−21,982; +21,076] | 0,035 | 0,830 |
<!-- E6:componentes_F4:fim -->

<!-- E6:lee:inicio -->
| População | Corte | Limite inferior | Limite superior | IC 95% conservador |
|---|---|---|---|---|
| V1 | 0,300 | +0,077 | +0,149 | [−1,645; +1,885] |
| V1 | 0,400 | −0,608 | +1,247 | [−2,149; +2,592] |
| V2 | 0,300 | −0,984 | −0,163 | [−2,124; +1,011] |
| V2 | 0,400 | −0,366 | +0,149 | [−1,481; +1,176] |
| V3 | 0,300 | −1,550 | +0,011 | [−2,863; +1,438] |
| V3 | 0,400 | −1,856 | +0,176 | [−3,263; +1,441] |
<!-- E6:lee:fim -->

## 6. Co-políticas e suplementares

### 6.1 Adesão do ciclo 3 (F0.3), PMMB (F0.4) e coparticipação (S1)

F0.4 e S1 são retratos de 09/10/2026 do PMMB: estoque acumulado de todas as
políticas, não fluxo do PMM-E. Um salto em `ativas_coparticipacao` (S1) é o
sinal de que o teto da Portaria 752/2023 operou no corte.

<!-- E6:copolitica:inicio -->
| Outcome | População | Corte | n abaixo / acima | Salto | IC 95% | p |
|---|---|---|---|---|---|---|
| F0.3 `f0_3a_consta_do_resultado_final_adesao` | G3 | 0,300 | 399 / 276 | −3,6 p.p. | [−20,1; +12,9] | 0,670 |
| F0.3 `f0_3a_consta_do_resultado_final_adesao` | G3 | 0,400 | 270 / 315 | −10,9 p.p. | [−28,0; +6,1] | 0,210 |
| F0.3 `f0_3a_consta_do_resultado_final_adesao` | G3 | empilhado | 669 / 591 | −7,0 p.p. | [−18,9; +4,8] | 0,244 |
| F0.3 `f0_3_vagas_pedidas` | G3 | 0,300 | 150 / 118 | +0,149 | [−19,346; +19,645] | 0,988 |
| F0.3 `f0_3_vagas_pedidas` | G3 | 0,400 | 143 / 175 | −2,200 | [−8,638; +4,239] | 0,503 |
| F0.3 `f0_3_vagas_pedidas` | G3 | empilhado | 293 / 293 | −1,163 | [−10,478; +8,152] | 0,807 |
| F0.3 `f0_3_fracao_priorizada` | G3 | 0,300 | 150 / 118 | −4,2 p.p. | [−22,7; +14,3] | 0,657 |
| F0.3 `f0_3_fracao_priorizada` | G3 | 0,400 | 143 / 175 | −7,2 p.p. | [−23,0; +8,6] | 0,369 |
| F0.3 `f0_3_fracao_priorizada` | G3 | empilhado | 293 / 293 | −5,9 p.p. | [−17,9; +6,1] | 0,337 |
| F0.3 `f0_3_vagas_imediatas_priorizadas` | G3 | 0,300 | 150 / 118 | −0,249 | [−2,462; +1,964] | 0,826 |
| F0.3 `f0_3_vagas_imediatas_priorizadas` | G3 | 0,400 | 143 / 175 | −0,036 | [−0,785; +0,713] | 0,925 |
| F0.3 `f0_3_vagas_imediatas_priorizadas` | G3 | empilhado | 293 / 293 | −0,130 | [−1,191; +0,931] | 0,810 |
| F0.4 `f0_4_pmmb_vagas_por_10k` | U | 0,300 | 859 / 654 | +0,001 | [−0,405; +0,407] | 0,998 |
| F0.4 `f0_4_pmmb_vagas_por_10k` | U | 0,400 | 587 / 603 | +0,151 | [−0,267; +0,568] | 0,480 |
| F0.4 `f0_4_pmmb_vagas_por_10k` | U | empilhado | 1446 / 1257 | +0,066 | [−0,226; +0,359] | 0,656 |
| F0.4 `f0_4_pmmb_medicos_por_10k` | U | 0,300 | 859 / 654 | −0,127 | [−0,529; +0,276] | 0,537 |
| F0.4 `f0_4_pmmb_medicos_por_10k` | U | 0,400 | 587 / 603 | +0,133 | [−0,277; +0,544] | 0,524 |
| F0.4 `f0_4_pmmb_medicos_por_10k` | U | empilhado | 1446 / 1257 | −0,013 | [−0,302; +0,276] | 0,931 |
| S1 `s1_pmmb_coparticipacao_por_10k` | U | 0,300 | 859 / 654 | −0,078 | [−0,326; +0,169] | 0,535 |
| S1 `s1_pmmb_coparticipacao_por_10k` | U | 0,400 | 587 / 603 | +0,106 | [−0,150; +0,361] | 0,417 |
| S1 `s1_pmmb_coparticipacao_por_10k` | U | empilhado | 1446 / 1257 | +0,002 | [−0,176; +0,181] | 0,981 |
<!-- E6:copolitica:fim -->

### 6.2 S2–S4 no índice

S2 exclui os municípios com IVS exatamente 0,300 e 0,400 (onde as regras com
limite oposto divergem). S3 separa as classes de porte em que o estrato da APS
muda no corte (lidas do a10: em 0,300, portes 2 e 3; em 0,400, portes 1, 2 e
4). S4, só em 0,400, separa Amazônia Legal ou faixa de fronteira (onde a ajuda
de custo do PMMB não muda) do resto. As linhas de S2–S4 de todos os outcomes
estão em `E6_estimativas.csv`.

<!-- E6:s3_s4_indice:inicio -->
| População | Especificação | Corte | n abaixo / acima | Salto | IC 95% | p |
|---|---|---|---|---|---|---|
| V1+V2+V3 | S3_porte_muda | 0,300 | 71 / 47 | −0,30 DP | [−0,94; +0,33] | 0,350 |
| V1+V2+V3 | S3_porte_nao_muda | 0,300 | 74 / 73 | −0,25 DP | [−0,80; +0,30] | 0,379 |
| V1+V2+V3 | S3_diferenca | 0,300 | 145 / 120 | −0,06 DP | [−0,90; +0,78] | 0,895 |
| V1+V2+V3 | S3_porte_muda | 0,400 | 100 / 123 | −0,10 DP | [−0,61; +0,42] | 0,714 |
| V1+V2+V3 | S3_porte_nao_muda | 0,400 | 22 / 22 | +0,38 DP | [−0,52; +1,29] | 0,410 |
| V1+V2+V3 | S3_diferenca | 0,400 | 122 / 145 | −0,48 DP | [−1,52; +0,56] | 0,370 |
| V1+V2+V3 | S4_dentro | 0,400 | 28 / 18 | −0,52 DP | [−1,42; +0,38] | 0,260 |
| V1+V2+V3 | S4_fora | 0,400 | 94 / 127 | +0,10 DP | [−0,41; +0,61] | 0,701 |
| V1+V2+V3 | S4_diferenca | 0,400 | 122 / 145 | −0,62 DP | [−1,65; +0,42] | 0,243 |
| V1 | S3_porte_muda | 0,300 | 29 / 23 | −0,47 DP | [−1,27; +0,32] | 0,245 |
| V1 | S3_porte_nao_muda | 0,300 | 32 / 30 | −0,43 DP | [−1,58; +0,73] | 0,471 |
| V1 | S3_diferenca | 0,300 | 61 / 53 | −0,05 DP | [−1,45; +1,36] | 0,947 |
| V1 | S3_porte_muda | 0,400 | 38 / 30 | −0,08 DP | [−0,95; +0,78] | 0,847 |
| V1 | S3_porte_nao_muda | 0,400 | 15 / 11 | +0,89 DP | [−1,12; +2,91] | 0,385 |
| V1 | S3_diferenca | 0,400 | 53 / 41 | −0,98 DP | [−3,17; +1,21] | 0,382 |
| V1 | S4_dentro | 0,400 | 17 / 11 | −0,14 DP | [−1,07; +0,78] | 0,760 |
| V1 | S4_fora | 0,400 | 36 / 30 | +0,26 DP | [−0,94; +1,46] | 0,668 |
| V1 | S4_diferenca | 0,400 | 53 / 41 | −0,41 DP | [−1,92; +1,11] | 0,599 |
| V2 | S3_porte_muda | 0,300 | 39 / 25 | −1,11 DP | [−2,13; −0,08] | 0,035 |
| V2 | S3_porte_nao_muda | 0,300 | 43 / 36 | +0,19 DP | [−0,65; +1,03] | 0,662 |
| V2 | S3_diferenca | 0,300 | 82 / 61 | −1,29 DP | [−2,62; +0,03] | 0,056 |
| V2 | S3_porte_muda | 0,400 | 38 / 40 | +0,20 DP | [−0,75; +1,16] | 0,675 |
| V2 | S3_porte_nao_muda | 0,400 | 15 / 13 | −0,18 DP | [−1,40; +1,04] | 0,768 |
| V2 | S3_diferenca | 0,400 | 53 / 53 | +0,39 DP | [−1,16; +1,94] | 0,623 |
| V2 | S4_dentro | 0,400 | 15 / 11 | +0,15 DP | [−1,73; +2,02] | 0,878 |
| V2 | S4_fora | 0,400 | 38 / 42 | +0,03 DP | [−0,79; +0,86] | 0,938 |
| V2 | S4_diferenca | 0,400 | 53 / 53 | +0,11 DP | [−1,93; +2,16] | 0,913 |
| V3 | S3_porte_muda | 0,300 | 48 / 31 | +0,61 DP | [−0,13; +1,36] | 0,107 |
| V3 | S3_porte_nao_muda | 0,300 | 54 / 51 | −0,46 DP | [−1,10; +0,19] | 0,164 |
| V3 | S3_diferenca | 0,300 | 102 / 82 | +1,07 DP | [+0,09; +2,05] | 0,033 |
| V3 | S3_porte_muda | 0,400 | 79 / 101 | −0,23 DP | [−0,83; +0,37] | 0,454 |
| V3 | S3_porte_nao_muda | 0,400 | 18 / 17 | +0,49 DP | [−1,22; +2,20] | 0,574 |
| V3 | S3_diferenca | 0,400 | 97 / 118 | −0,72 DP | [−2,54; +1,09] | 0,436 |
| V3 | S4_dentro | 0,400 | 21 / 14 | −1,30 DP | [−2,07; −0,53] | 0,001 |
| V3 | S4_fora | 0,400 | 76 / 104 | +0,07 DP | [−0,57; +0,70] | 0,838 |
| V3 | S4_diferenca | 0,400 | 97 / 118 | −1,37 DP | [−2,36; −0,37] | 0,007 |
<!-- E6:s3_s4_indice:fim -->

## 7. Leitura

A leitura abaixo só resume as tabelas; os números estão nelas.

1. **Seleção (§3.1).** Em U, ter célula no quadro e o número de células por
   10 mil habitantes não saltam de forma distinguível de zero em nenhum ciclo
   ou corte. A exceção são as vagas imediatas por 10 mil habitantes do ciclo 1
   em 0,400 e com cortes empilhados (salto negativo, p < 0,05, q BKY alto).
   Como o E3 já registrava desequilíbrio de covariáveis no ciclo 1 em 0,400,
   as linhas de V1 nesse corte pedem cautela. A densidade de municípios não
   salta em nenhuma população; os desequilíbrios de covariáveis são poucos e
   compatíveis com o acaso, salvo o de V1 em 0,400, já conhecido.
2. **P1.** O índice de atração-presença, com ciclos e cortes empilhados, tem
   salto negativo e IC 95% que contém zero. O IC também contém zero por corte,
   por ciclo, com h = 0,030 e 0,080, no donut e na variante de Anderson. Não
   detectamos efeito do pacote do corte sobre o índice.
3. **Componentes.** Nenhuma linha principal de F1 tem p < 0,05. Em F2 e F4 há
   poucas linhas com p < 0,05 (presença por 10 mil habitantes do ciclo 2 em
   0,300; pontuação dos candidatos de 1ª opção no ciclo 3 e com ciclos
   empilhados), todas com salto negativo e nenhuma com q BKY < 0,05. O número de
   linhas com p < 0,05 em cada família é da ordem do esperado por acaso.
4. **Magnitude (§5.3).** Com o IC convencional, os saltos de preenchimento com
   ciclos e cortes empilhados (F1.2 e F1.3; F1.4 com V1 e V2) têm limite
   superior abaixo da referência de +10 p.p. do protocolo: um salto dessa
   ordem, a favor do lado de bolsa maior, não é compatível com esses dados.
   Por ciclo e corte isolados, a maior parte dos IC ainda admite +10 p.p. Essa
   leitura depende da aproximação local linear: o IC honesto, com o M da regra
   de bolso do protocolo, não descarta nada (§4).
5. **Co-políticas.** As vagas do PMMB em coparticipação (S1), as vagas e os
   médicos ativos do PMMB (F0.4) e a adesão do ciclo 3 (F0.3) não saltam de
   forma distinguível de zero. O retrato do PMMB é estoque acumulado: isso
   não mostra que a Portaria 752/2023 deixou de operar, só que o estoque de
   09/10/2026 não tem descontinuidade detectável no corte.
6. **Suplementares S2–S4.** O donut não muda a leitura do índice. Em S3 e S4
   há linhas com p < 0,05 em subamostras pequenas de V2 e V3; a fração de
   linhas suplementares com p < 0,05 é a esperada por acaso (§5), elas não
   têm correção para testes múltiplos e não sustentam conclusão sobre canal.

**Em uma frase:** com o protocolo congelado, não detectamos efeito do pacote
do corte de IVS (bolsa anunciada de +R$ 5 mil e as outras regras dos mesmos
cortes) sobre atração, preenchimento ou presença dos especialistas do PMM-E;
com ciclos e cortes empilhados e o IC convencional, saltos positivos de
preenchimento da ordem de +10 p.p. ficam fora do intervalo. Isso é evidência
sobre o pacote no corte, não sobre a bolsa isolada, a participação no PMM-E ou
a oferta líquida no CNES (E7).

## 8. Limites

1. **Pacote, não bolsa.** Ver §1. Nenhum resultado em nível isola a bolsa.
2. **Potência.** Cada corte tem poucas dezenas de municípios com vaga de cada
   lado na janela principal; empilhar cortes e ciclos ajuda, mas efeitos
   moderados continuam fora do alcance de muitas linhas.
3. **Seleção em V_k.** Os outcomes por célula só existem onde houve vaga; a
   leitura deles depende da continuidade de F0 (§3.1).
4. **Presença é retrato.** F2 usa a relação nominal publicada em 09/10/2026:
   estoque em uma data, não retenção individual.
5. **Exposição prévia.** F1.3 do ciclo 1, F2.3 dos ciclos 1 e 2 e F1.4 do
   ciclo 1 já tinham sido vistos (protocolo §10).
6. **Muitos testes.** Os q-valores BKY controlam a taxa de falsas descobertas
   dentro de cada família; p < 0,05 isolado não é evidência.
7. **Local randomization** depende da janela escolhida por balanço; em alguns
   cortes nenhuma janela passou e a linha sai sem estimativa.
8. **S4** usa o atributo municipal de Amazônia Legal e faixa de fronteira do
   PMMB consolidado (MS), não uma lista do IBGE conferida aqui.

## 9. Desvios e decisões

Registrados com data e motivo em `E6_resumo.json` (`desvios`, `decisoes`):
local randomization em U, G3 e V3 com a regra do E5; fonte do atributo do S4;
Poisson local e limites de Lee só por ciclo e corte (a biblioteca não tem
versão empilhada); municípios criados depois de 2010 fora da RDD, sem
imputação.

## 10. Validações

<!-- E6:validacoes:inicio -->
| Conferência | Resultado |
|---|---|
| linhas do E3 reproduzidas (F1.3 ciclo 1, F2.3 ciclos 1 e 2) | 18; max abs dif = 1.1102230246251565e-16 |
| linhas do E5 reproduzidas (LR, ponderado, célula, ciclos empilhados) | 12 (+ 1 sem janela); max abs dif = 5.021150162320964e-12 |
| linhas em E6_estimativas.csv | 2022 |
| linhas do protocolo (no_protocolo = True) | 1743 |
| linhas NAO_EXECUTADO | 35 |
| linhas SEM_ESTIMATIVA (biblioteca devolveu NaN com motivo) | 2 |
<!-- E6:validacoes:fim -->

## 11. Reprodução

1. `scripts/rdd_bolsa/12_construir_outcomes_funil.py` (tarefa B);
2. `scripts/aquisicao/a10_normas_mesmos_cortes_ivs.py` (tarefa D, insumo do S3);
3. `scripts/rdd_bolsa/13_estimar_E6_funil.py` (grava as saídas e regrava as
   tabelas deste documento).
