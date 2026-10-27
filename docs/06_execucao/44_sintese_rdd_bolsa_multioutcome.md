# 44 — Síntese da RDD da bolsa: rodada multi-outcome (E8)

> **Data:** 19/10/2026.<br>
> **Protocolo:** [`40_protocolo_multioutcome_rdd_bolsa.md`](40_protocolo_multioutcome_rdd_bolsa.md)
> (§7: duas primárias com Holm, secundárias com q BKY por família, referências
> de magnitude; §11: tarefa E8), congelado em 18/10/2026.<br>
> **Insumos:** E3 ([`37`](37_resultados_rdd_bolsa_ivs_oficial.md)), E5
> ([`39`](39_inferencia_alternativa_rdd_bolsa.md)), E6
> ([`41`](41_resultados_E6_funil.md), outcomes em [`41a`](41a_construcao_outcomes_funil.md)),
> E9 ([`42`](42_resultados_E9_escolha.md)) e E7 ([`43`](43_resultados_E7_dird_cnes.md)),
> todos auditados.<br>
> **Script:** `scripts/rdd_bolsa/15_sintese_E8.py`. Não estima nada de novo. A
> única conta inferencial é o ajuste de Holm sobre os p de P1 e P2.<br>
> **Saídas:** `output/rdd_bolsa/E8_resumo.json` e `output/rdd_bolsa/E8_tabela_sintese.csv`.
> Natureza dos dados: **EMPIRICO**.<br>
> **Testes:** `tests/test_e8_sintese.py`.<br>
> **Números:** todo número de resultado está entre marcadores `<!-- E8:... -->`.
> Os blocos são gerados só a partir das duas saídas do E8, por
> `python3 scripts/rdd_bolsa/15_sintese_E8.py --atualizar-doc`. O teste confere
> que os blocos batem com as saídas, que as saídas batem com os CSV do E3 ao E9
> e que a prosa fora dos blocos só tem parâmetros do protocolo.

## 1. Resposta curta

<!-- E8:resposta_curta:inicio -->
Sob o protocolo congelado, nenhum dos dois testes primários rejeita zero depois do Holm: o índice de atração-presença (P1) tem p ajustado 0,851, e a oferta de especialistas nas CBO-alvo no CNES por DiRD (P2) tem p ajustado 0,851. Com ciclos e cortes empilhados, o IC 95% convencional do preenchimento na 1ª chamada vai até +3,4 p.p., abaixo da referência de +10 p.p. do protocolo; esse descarte vale só sob a aproximação local linear, porque o IC honesto não descarta nada. O único sinal que resiste a vários testes está na escolha: no ciclo 2, a bolsa anunciada desloca a 1ª opção dos candidatos para células de bolsa maior (razão de chances 1,95 por +R$ 5 mil), mas o efeito não aparece nos ciclos 1 e 3 e o empilhado (razão 1,39) não resiste a placebos nem a um spline mais flexível. Os contrastes são o pacote do corte (RDD em nível), a bolsa mais a variação das co-políticas (DiRD) e o degrau da bolsa na escolha entre células (E9); nenhum é efeito da participação no PMM-E nem do Agora Tem Especialistas. Leitura: no corte, o degrau de R$ 5 mil não tem efeito detectável sobre preenchimento, presença ou oferta local, e o que se detecta é compatível com realocação de candidatos entre vagas, não com expansão líquida.
<!-- E8:resposta_curta:fim -->

> **Nota de 27/10/2026 (decisão do autor, delegada ao agente).** Com o tipo
> de vaga do quadro vigente na inscrição, o ciclo 2 continua robusto a poucos
> *clusters* e a placebos pela regra fixada antes das contas. Mas a folga do
> corte verdadeiro sobre os cortes placebo ficou menor: ele ainda fica à
> frente de todos, por pouco. Com *spline* cúbico, o IC continua contendo
> zero. Números e regra no [doc 57y](57y_robustez_E9_ciclo2_quadro_1302.md);
> conferência na [auditoria 54](../auditorias/54_auditoria_robustez_E9_ciclo2.md).
> Os blocos gerados deste documento não mudam.

## 2. O que cada contraste identifica

- **RDD em nível (E3, E6):** o **pacote do corte**. Nos cortes de IVS 0,300 e
  0,400 mudam a bolsa anunciada do PMM-E (+R$ 5 mil) e outras regras federais:
  teto do PMMB, estrato da APS, teto de emendas e, em 0,400, a ajuda de custo
  do PMMB ([auditoria 18](../auditorias/18_politicas_nos_mesmos_cortes_ivs.md)).
- **DiRD no CNES (E7):** a bolsa mais a **variação**, entre o pré e o pós, das
  descontinuidades dessas políticas. Ela remove só a parte constante no tempo.
- **Escolha (E9):** o degrau da bolsa na escolha da 1ª opção entre células do
  mesmo curso e ciclo, com o IVS em spline contínuo. Mede **realocação** entre
  células, condicional a candidatar-se. Não mede o total de candidatos.
- **Nenhum** desses contrastes é efeito da participação no PMM-E nem do Agora
  Tem Especialistas. O efeito candidato é o incentivo marginal anunciado.
- Vínculo no CNES não é médico do PMM-E. Presença no retrato de outubro não é
  retenção individual.

## 3. Tabela-síntese por elo da cadeia

Linhas principais (h = 0,050) com cortes empilhados, na ordem da cadeia:
implementação e seleção (F0) → atração (F1) → escolha (E9) → presença (F2) →
oferta no CNES (F3) → seleção de quem chega (F4). As frações aparecem em p.p.;
P1 em desvios-padrão; o E9 em razão de chances por +R$ 5 mil. O q BKY é o da
família do protocolo. O E9 não tem BKY: é secundário e exploratório.

<!-- E8:tabela_sintese:inicio -->
| Elo | Outcome | População | Ciclo | Contraste | Estimativa | IC 95% | p | q BKY | p Holm | Leitura |
|---|---|---|---|---|---|---|---|---|---|---|
| implementação e seleção | F0.1 município tem célula no quadro (ciclo 1) | U | 1 | pacote no corte (RDD em nível) | −3,0 p.p. | [−7,4 p.p.; +1,3 p.p.] | 0,171 | 1,000 | — | IC contém zero |
| implementação e seleção | F0.1 município tem célula no quadro (ciclo 2) | U | 2 | pacote no corte (RDD em nível) | +0,1 p.p. | [−4,8 p.p.; +5,0 p.p.] | 0,971 | 1,000 | — | IC contém zero |
| implementação e seleção | F0.1 município tem célula no quadro (ciclo 3) | U | 3 | pacote no corte (RDD em nível) | −2,2 p.p. | [−8,2 p.p.; +3,8 p.p.] | 0,468 | 1,000 | — | IC contém zero |
| implementação e seleção | F0.2 vagas imediatas por 10 mil hab. (ciclo 1) | U | 1 | pacote no corte (RDD em nível) | −0,035 | [−0,065; −0,006] | 0,019 | 0,639 | — | IC exclui zero; q BKY ≥ 0,05 |
| atração | P1 índice de atração-presença | V1+V2+V3 | 1+2+3 | pacote no corte (RDD em nível) | −0,13 DP | [−0,44 DP; +0,19 DP] | 0,426 | — | 0,851 | primária; Holm não rejeita; IC contém zero |
| atração | F1.1 candidatos de 1ª opção por célula | V1+V2+V3 | 1+2+3 | pacote no corte (RDD em nível) | +0,063 | [−0,511; +0,636] | 0,830 | 1,000 | — | IC contém zero |
| atração | F1.2 fração de células com candidato | V1+V2+V3 | 1+2+3 | pacote no corte (RDD em nível) | −7,0 p.p. | [−18,9 p.p.; +4,9 p.p.] | 0,247 | 1,000 | — | IC contém zero |
| atração | F1.3 fração de células preenchidas na 1ª chamada | V1+V2+V3 | 1+2+3 | pacote no corte (RDD em nível) | −7,3 p.p. | [−17,9 p.p.; +3,4 p.p.] | 0,181 | 1,000 | — | IC contém zero |
| atração | F1.4 fração de células preenchidas até a 2ª chamada | V1+V2 | 1+2 | pacote no corte (RDD em nível) | −8,0 p.p. | [−23,6 p.p.; +7,6 p.p.] | 0,313 | 1,000 | — | IC contém zero |
| escolha | E9 escolha da 1ª opção (razão de chances por +R$ 5 mil) | candidatos de 1ª opção | 1+2+3 | degrau da bolsa na escolha entre células | 1,39 | [1,12; 1,73] | 0,003 | — | — | IC exclui zero; frágil (placebos, spline cúbico, sem o ciclo 2) |
| escolha | E9 escolha da 1ª opção (razão de chances por +R$ 5 mil) | candidatos de 1ª opção | 2 | degrau da bolsa na escolha entre células | 1,95 | [1,48; 2,57] | < 0,001 | — | — | IC exclui zero; robusto a poucos clusters e a placebos; IC contém zero com spline cúbico |
| presença | F2.1 especialistas ativos por célula | V1+V2 | 1+2 | pacote no corte (RDD em nível) | −0,136 | [−0,491; +0,218] | 0,451 | 1,000 | — | IC contém zero |
| presença | F2.2 especialistas ativos por 10 mil hab. (ciclo 1) | U | 1 | pacote no corte (RDD em nível) | −0,008 | [−0,068; +0,051] | 0,786 | 1,000 | — | IC contém zero |
| presença | F2.2 especialistas ativos por 10 mil hab. (ciclo 2) | U | 2 | pacote no corte (RDD em nível) | −0,079 | [−0,239; +0,081] | 0,334 | 1,000 | — | IC contém zero |
| presença | F2.3 algum especialista ativo do ciclo | V1+V2 | 1+2 | pacote no corte (RDD em nível) | −5,2 p.p. | [−25,0 p.p.; +14,7 p.p.] | 0,610 | 1,000 | — | IC contém zero |
| oferta no CNES | P2 F3.1 vínculos nas CBO-alvo por 10 mil hab. | U | pós 2025-10..2026-08 | DiRD: bolsa + variação das co-políticas | +0,083 | [−0,309; +0,476] | 0,677 | 1,000 | 0,851 | primária; Holm não rejeita; IC contém zero |
| oferta no CNES | F3.1 vínculos nas CBO-alvo por 10 mil hab. | V1 | pós 2025-10..2026-08 | DiRD: bolsa + variação das co-políticas | −1,234 | [−2,907; +0,439] | 0,148 | 1,000 | — | IC contém zero |
| oferta no CNES | F3.2 município com especialista nas CBO-alvo | U | pós 2025-10..2026-08 | DiRD: bolsa + variação das co-políticas | −2,5 p.p. | [−5,9 p.p.; +1,0 p.p.] | 0,164 | 1,000 | — | IC contém zero |
| oferta no CNES | F3.3 horas SUS nas CBO-alvo por 10 mil hab. | U | pós 2025-10..2026-08 | DiRD: bolsa + variação das co-políticas | −2,0 | [−6,4; +2,3] | 0,359 | 1,000 | — | IC contém zero |
| oferta no CNES | F3.P1 placebo: generalistas por 10 mil hab. | U | pós 2025-10..2026-08 | DiRD: bolsa + variação das co-políticas | −0,088 | [−1,190; +1,014] | 0,875 | 1,000 | — | IC contém zero |
| oferta no CNES | F3.P2 placebo: especialistas fora das CBO-alvo | U | pós 2025-10..2026-08 | DiRD: bolsa + variação das co-políticas | −0,059 | [−0,485; +0,367] | 0,785 | 1,000 | — | IC contém zero |
| seleção de quem chega | F4.1 nota média dos alocados | V1+V2+V3 | 1+2+3 | pacote no corte (RDD em nível) | −0,396 | [−0,939; +0,147] | 0,152 | 0,830 | — | IC contém zero |
| seleção de quem chega | F4.2 nota média dos candidatos de 1ª opção | V1+V2+V3 | 1+2+3 | pacote no corte (RDD em nível) | −0,453 | [−0,873; −0,033] | 0,035 | 0,830 | — | IC exclui zero; q BKY ≥ 0,05 |
<!-- E8:tabela_sintese:fim -->

Testes por família (todas as linhas principais do protocolo, por corte, ciclo
e empilhadas):

<!-- E8:familias_testes:inicio -->
| Família | Linhas principais no BKY | p < 0,05 | q BKY < 0,05 | menor p | menor q |
|---|---|---|---|---|---|
| F0 | 42 | 2 | 0 | 0,018 | 0,639 |
| F1 | 45 | 0 | 0 | 0,057 | 1,000 |
| F2 | 24 | 1 | 0 | 0,019 | 0,828 |
| F3 | 18 | 0 | 0 | 0,113 | 1,000 |
| F4 | 24 | 2 | 0 | 0,035 | 0,830 |
<!-- E8:familias_testes:fim -->

**Como ler.** "IC contém zero" não quer dizer efeito zero; quer dizer que a
amostra não distingue o efeito de zero. Um p < 0,05 isolado, com q BKY alto,
é da ordem do esperado por acaso numa família com dezenas de testes.

## 4. Testes primários com Holm

O protocolo (§7) fixou duas primárias: P1, o índice de atração-presença com
ciclos e cortes empilhados (E6); P2, a oferta de especialistas nas CBO-alvo por
DiRD em todos os municípios, cortes empilhados (E7). O Holm controla a taxa de
erro da família das duas.

<!-- E8:holm:inicio -->
| Primária | Contraste | Salto | IC 95% | p | p Holm | Rejeita a 5%? |
|---|---|---|---|---|---|---|
| P1: índice de atração-presença (KLK de F1.1, F1.2, F1.3 e F2.1), ciclos e cortes empilhados, V1+V2+V3, h = 0,050, CR1 por município | pacote do corte (RDD em nível) | −0,13 DP | [−0,44 DP; +0,19 DP] | 0,426 | 0,851 | não |
| P2: F3.1 (vínculos nas CBO-alvo por 10 mil hab.) por DiRD em U, cortes empilhados | DiRD: bolsa + variação, entre pré e pós, das descontinuidades das co-políticas | +0,083 | [−0,309; +0,476] | 0,677 | 0,851 | não |
<!-- E8:holm:fim -->

Nenhuma primária é rejeitada. As duas têm IC que contém zero.

## 5. O que podemos afirmar e o que não podemos

### 5.1 O que fica descartado, e sob que condição

A referência do protocolo é +10 p.p. de preenchimento e +25% de candidaturas.
"Descartar" aqui quer dizer: o limite superior do IC 95% fica abaixo da
referência. Isso vale **só** sob três condições:
1. o IC é o convencional (HC1 ou CR1 por município), não o honesto;
2. a aproximação local linear é boa no corte, sem viés de suavização
   relevante;
3. o que se descarta é um salto do **pacote** do corte, não da bolsa isolada.

O IC honesto com o M do protocolo não descarta nada (coluna da direita).

<!-- E8:descarte:inicio -->
| Outcome | População | Ciclo | Salto | IC 95% | Exclui +10 p.p.? | Maior limite superior entre as especificações convencionais | Todas excluem? | IC honesto (M do protocolo) exclui? |
|---|---|---|---|---|---|---|---|---|
| F1.3 | V1+V2+V3 | 1+2+3 | −7,3 p.p. | [−17,9 p.p.; +3,4 p.p.] | sim | +7,8 p.p. (S2_donut, h = 0,050) | sim | não |
| F1.4 | V1+V2 | 1+2 | −8,0 p.p. | [−23,6 p.p.; +7,6 p.p.] | sim | +12,0 p.p. (sensibilidade_h, h = 0,030) | não | não |
| F1.3 | V1 | 1 | −8,6 p.p. | [−31,2 p.p.; +14,0 p.p.] | não | +27,6 p.p. (sensibilidade_h, h = 0,030) | não | não |
| F1.3 | V2 | 2 | −5,4 p.p. | [−24,8 p.p.; +14,1 p.p.] | não | +19,8 p.p. (S2_donut, h = 0,050) | não | não |
| F1.3 | V3 | 3 | −7,8 p.p. | [−20,4 p.p.; +4,7 p.p.] | sim | +10,1 p.p. (S2_donut, h = 0,050) | não | não |
| F1.4 | V1 | 1 | −8,3 p.p. | [−31,0 p.p.; +14,4 p.p.] | não | +26,6 p.p. (sensibilidade_h, h = 0,030) | não | não |
| F1.4 | V2 | 2 | −7,8 p.p. | [−27,0 p.p.; +11,4 p.p.] | não | +15,7 p.p. (S2_donut, h = 0,050) | não | não |

F1.3 (V1+V2+V3): 6 especificações convencionais do protocolo (S2_donut, nivel_celula, ponderado_celulas, principal, sensibilidade_h); todas com salto negativo; com p < 0,05: nivel_celula, h = 0,050: −9,8 p.p. [−19,0 p.p.; −0,6 p.p.]; ponderado_celulas, h = 0,050: −9,8 p.p. [−19,1 p.p.; −0,6 p.p.].

F1.4 (V1+V2): 6 especificações convencionais do protocolo (S2_donut, nivel_celula, ponderado_celulas, principal, sensibilidade_h); todas com salto negativo; com p < 0,05: nenhuma.

| Âncora (E3, ciclo 1, F1.3) | Salto | IC 95% | Exclui +10 p.p.? | MDE de 80% (E5) |
|---|---|---|---|---|
| corte 0,300 | −12,8 p.p. | [−45,5 p.p.; +19,8 p.p.] | não | 46,6 p.p. |
| corte 0,400 | −5,1 p.p. | [−36,5 p.p.; +26,2 p.p.] | não | 44,8 p.p. |

Candidaturas (F1.1, Poisson local, referência de +25 %): 2 de 6 linhas por ciclo e corte têm limite superior abaixo da referência (ciclo 1, 0,300: até +60,7 %; ciclo 1, 0,400: até +718,4 %; ciclo 2, 0,300: até +0,4 %; ciclo 2, 0,400: até +105,0 %; ciclo 3, 0,300: até +9,5 %; ciclo 3, 0,400: até +81,9 %). Não há linha empilhada em escala relativa.

Oferta no CNES (P2): o limite superior do IC 95% é +0,476 vínculo por 10 mil hab., ou 4,4 % da média bruta do pré abaixo do corte 0,300 (10,711); 8,0 % da média bruta do pré abaixo do corte 0,400 (5,941). O IC honesto com o M do protocolo é [−9,958; +10,125].
<!-- E8:descarte:fim -->

Leitura:
- Com ciclos e cortes empilhados, um salto de preenchimento na 1ª chamada da
  ordem de +10 p.p. a favor do lado de bolsa maior fica fora de todas as
  especificações convencionais do protocolo. Todas têm salto negativo, e duas
  delas (ponderada por células e no nível da célula) excluem zero do lado
  negativo.
- Para o preenchimento até a 2ª chamada, o descarte depende da janela.
- Por ciclo isolado, nos ciclos 1 e 2, o IC ainda admite +10 p.p. A âncora do
  E3 (ciclo 1, por corte) também. O ganho de precisão veio de empilhar.
- Para candidaturas, só algumas linhas por ciclo e corte descartam +25%. Não
  há estimativa empilhada em escala relativa.

### 5.2 O que o E9 sugere e por que é frágil

<!-- E8:e9:inicio -->
| Ciclo | Coef. por R$ mil | IC 95% | p | Razão de chances por +R$ 5 mil [IC 95%] | Δ prob. média, p.p. [IC 95%] | Prob. base, p.p. | Variação relativa média [IC 95%] |
|---|---|---|---|---|---|---|---|
| 1 | +0,0653 | [−0,0208; +0,1515] | 0,137 | 1,39 [0,90; 2,13] | +0,426 [−0,226; +1,079] | 1,137 | +38,0 % [−20,5 %; +96,6 %] |
| 2 | +0,1331 | [+0,0778; +0,1884] | < 0,001 | 1,95 [1,48; 2,57] | +0,494 [+0,216; +0,771] | 0,539 | +93,6 % [+40,6 %; +146,6 %] |
| 3 | +0,0097 | [−0,0527; +0,0720] | 0,761 | 1,05 [0,77; 1,43] | +0,026 [−0,144; +0,195] | 0,527 | +4,9 % [−27,6 %; +37,5 %] |
| empilhado | +0,0662 | [+0,0227; +0,1096] | 0,003 | 1,39 [1,12; 1,73] | +0,225 [+0,052; +0,397] | 0,586 | +38,9 % [+8,9 %; +68,8 %] |

| Teste de robustez (pós-auditoria, fora do protocolo) | Ciclo 2 | Empilhado |
|---|---|---|
| p do score bootstrap (Rademacher / Webb), cluster por conjunto | < 0,001 / 0,002 | — |
| p do CV3 | < 0,001 | — |
| IC por inversão do score | [+0,0682; +0,1882] | — |
| cortes placebo: fração com abs(t) > 1,96 | 0,148 | 0,148 |
| cortes placebo: nº com abs(t) ≥ t real, de 27 | 0 | 2 |
| p por posto contra os placebos | 0,036 | 0,107 |
| spline cúbico: coef. [IC 95%]; p | +0,0642 [−0,0084; +0,1369]; 0,083 | +0,0326 [−0,0194; +0,0847]; 0,220 |
| maior p entre spline linear com nós a cada 0,05 e janelas de ±0,10, ±0,05 e ±0,025 | 0,030 | — |
| ciclos 1 e 3 empilhados, sem o 2: coef. [IC 95%]; p | — | +0,0266 [−0,0204; +0,0735]; 0,267 |
| Q de Cochran (ciclos 1, 2, 3); p | — | 8,50; 0,014 |
| cluster por curso: p do score (Rademacher / Webb) | — | 0,042 / 0,047 |
<!-- E8:e9:fim -->

O que o E9 sugere:
- **No ciclo 2,** a bolsa anunciada desloca a 1ª opção dos candidatos para
  células de bolsa maior. O sinal sobrevive à inferência com poucos clusters
  (score bootstrap, CV3, inversão do score) e a cortes placebo, e sobrevive a
  um spline linear mais flexível e a janelas em torno dos cortes. A ressalva é
  o spline cúbico na amostra toda, em que o IC inclui zero.
- **Nos ciclos 1 e 3,** o IC inclui zero.

Por que o empilhado é frágil:
- a significância vem do ciclo 2: sem ele, os ciclos 1 e 3 juntos têm IC que
  inclui zero, e o Q de Cochran rejeita que os três ciclos tenham o mesmo
  coeficiente;
- os cortes placebo dão |t| > 1,96 com frequência bem acima de 5%: o t com
  cluster por conjunto, junto com o spline linear, superestima a precisão.
  Contra essa distribuição, o p por posto do empilhado fica acima de 0,05;
- com spline cúbico, o IC do empilhado inclui zero;
- com cluster por curso, o p do score fica pouco abaixo de 0,05.

O que o E9 **não** diz: que a bolsa aumenta o total de candidatos, o
preenchimento ou a presença. No logit condicional, o que uma célula ganha as
outras do mesmo curso perdem. A variação relativa da probabilidade de escolha
não é comparável a "+26% de candidaturas" (Dal Bó, Finan e Rossi): lá é o
tamanho do pool; aqui é a repartição de um pool dado.

### 5.3 O que o E7 diz, e as ameaças

<!-- E8:e7:inicio -->
- **F3.1 em U, corte 0,300:** 5 meses consecutivos com p < 0,05, de 2025-10 a 2026-02 (saltos de +0,346 a +0,609, relativos a 2025-06; maior p 0,040). Nos 6 meses seguintes do pós, 0 têm p < 0,05. Antes da referência, 0 de 24 meses têm p < 0,05. Salto médio no pré extra +0,455; no pós +0,406. DiRD principal +0,287 [−0,235; +0,810], p = 0,281.
- **Descontinuidade pré-existente (F3.1, U, 0,300, RDD em nível):** pré extra −1,811 [−3,591; −0,030]; pré principal −2,147 [−4,192; −0,101].
- **F3.1 em U, corte 0,400:** meses do pós com p < 0,05: 0.
- **Generalistas (F3.P1), U, 0,400:** 2 de 7 meses do pré extra com p < 0,05; em 2022-01 o salto relativo a 2025-06 é +1,542 (p = 0,045), e a média no pré principal é +0,193. S5 (pré menos pré extra) −0,958 (p = 0,061). DiRD principal −0,111 (p = 0,816).
- **V1, corte 0,300:** 12 de 12 meses do pré extra e do trecho até o pré principal com p < 0,05 (12 com salto positivo). Placebo dentro do pré −1,421 (p = 0,044); S5 −4,068 (p < 0,001).
<!-- E8:e7:fim -->

O que o E7 diz: a DiRD não detecta mudança na oferta cadastrada de
especialistas nas CBO-alvo, nem nos placebos. Em 0,300 há uma sequência de
meses significativos logo no início do pós, que depois se desfaz.

Por que essa sequência não vira efeito:
- **Co-políticas variáveis no tempo.** A DiRD só remove a parte constante das
  outras políticas. Emendas e parcelas de MAC e APS mudam a cada ano, e a de
  MAC com "IVS maior que 0,3" pode mirar especialistas
  ([auditoria 18](../auditorias/18_politicas_nos_mesmos_cortes_ivs.md), §3.1).
- **Descontinuidade pré-existente.** Em 0,300, a oferta em nível já era menor
  do lado de cima no pré extra e no pré principal, antes de todas as regras com
  corte em 0,3 ou 0,4. A referência do estudo de evento (2025-06) está num
  vale: o salto do pós tem tamanho parecido com o do pré extra.
- **Generalistas em 0,400.** O placebo deriva antes do pré principal, o que é
  compatível com uma co-política variável no tempo nesse corte.
- **Pré-tendência em V1.** Em 0,300, a descontinuidade da oferta entre os
  municípios do quadro do ciclo 1 já caía antes do PMM-E. A DiRD em V1 nesse
  corte não é crível.

### 5.4 Seleção em V1 no corte 0,400

<!-- E8:selecao:inicio -->
- vagas imediatas do ciclo 1 por 10 mil hab., em U: 0,400 −0,074 [−0,134; −0,013] (p = 0,018; q BKY = 0,639); empilhado −0,035 [−0,065; −0,006] (p = 0,019; q BKY = 0,639);
- razão de densidades de V1 em 0,400: 0,61 [0,29; 1,30] (p = 0,201);
- balanço de V1 em 0,400: 3 de 13 covariáveis com p < 0,05 (estrato_interior_proximo_polo, estrato_metropolitano, ivs_ch_2010);
- peso do grupo ciclo 1 × 0,400 no P1 empilhado: 12,3 %.
<!-- E8:selecao:fim -->

Em U, as vagas imediatas do ciclo 1 por habitante são menores do lado de bolsa
maior em 0,400 (q BKY alto, mas o sinal aparece em vários estimadores, doc
41, §7). Com a razão de densidades de V1 abaixo de um e desequilíbrios de
covariáveis, isso torna plausível que V1 em 0,400 seja uma amostra selecionada.
As linhas de V1 nesse corte não devem ser lidas como contraste limpo. O peso
desse grupo no P1 empilhado está no bloco acima.

### 5.5 Quadro

| Podemos afirmar | Não podemos afirmar |
|---|---|
| Sob o protocolo, nenhum teste primário rejeita zero depois do Holm | Que a bolsa "não funciona" ou que o efeito é zero |
| Com cortes e ciclos empilhados, IC convencional e linearidade local, saltos de preenchimento na 1ª chamada de +10 p.p. ou mais ficam fora do intervalo | Que esse descarte vale com o IC honesto, por ciclo isolado ou para a bolsa sem as co-políticas |
| Nenhuma família do protocolo tem q BKY < 0,05 | Que os p < 0,05 isolados (vagas imediatas, presença do ciclo 2 em 0,300, nota dos candidatos) são efeitos |
| No ciclo 2, a bolsa anunciada desloca a 1ª opção para células de bolsa maior, com inferência robusta a poucos clusters e a placebos | Que esse deslocamento aumenta o total de candidatos, o preenchimento ou a oferta local; que ele vale para os ciclos 1 e 3 |
| A DiRD no CNES não detecta mudança de oferta das CBO-alvo nem dos placebos | Que a sequência de meses significativos em 0,300 é efeito da bolsa, dadas a descontinuidade pré-existente e as co-políticas |
| O contraste é o incentivo marginal anunciado, como pacote do corte | Efeito da participação no PMM-E, do Agora Tem Especialistas ou do IVS |

## 6. Comparação com a literatura de magnitude

Só o que está no [doc 20 da seção 03](../03_literatura_empirica/20_evidencia_empirica_hipotese_remuneracao_preenchimento.md)
e no protocolo. O texto das linhas é copiado da fonte pelo script, que para se a
linha não existir.

<!-- E8:literatura:inicio -->
Degrau relativo da bolsa neste desenho (grades dos editais): em 0,300, de R$ 10 mil para R$ 15 mil (+50 %); em 0,400, de R$ 15 mil para R$ 20 mil (+33 %).

| Estudo (doc 20) | País | Desenho | Conclusão |
|---|---|---|---|
| A1. Bobba et al. (NBER 2021, rev. 2026) | Peru | RDD no corte censitário de 500 hab. que define adicional de +13% | o adicional **não** mudou o preenchimento (0,063, EP 0,048), mas trouxe professor melhor (+0,42 dp) e mais aprendizagem |
| A2. Dal Bó, Finan & Rossi (2013), *QJE* | México | salário anunciado sorteado (+33%) | aceitação +15,1 p.p.; elasticidade ≈ 2; salário alto anula o efeito da distância; sem perda de motivação |
| A8. Elacqua et al. (2022), *JPAM* | Chile | RD na nota do portfólio; prêmio de ~16% | retém quem já está (+17 a 21 p.p.), não atrai de fora |
| B1. Yong et al. (2018), *SSM* | Austrália | DiD na mudança de elegibilidade de 2010 | recém-formados +50%; outras entradas caem; estoque não muda |
| B3. Khoury, Leganza & Masucci (2025), *AJHE* | EUA | DiD pareado na designação de área de escassez (pacote) | mais médicos em início de carreira; experientes não se mudam |
| C1. Costa, Nunes & Sanches (2024), *REStat* | Brasil | logit estrutural de coeficientes aleatórios com instrumento | elasticidade 0,4–0,7; salário é a alavanca menos custo-efetiva; origem pesa mais |
| C2. Hone et al. (2020), *BMC HSR* | Brasil | DiD com estudo de evento | +15,1 médicos do programa, mas só +5,7 líquido |

- Dal Bó, Finan & Rossi (2013): efeito do salário alto sobre candidaturas (`docs/03_literatura_empirica/20_evidencia_empirica_hipotese_remuneracao_preenchimento.md`): "candidaturas +26%".
- protocolo §1: maior efeito plausível pela literatura (`docs/06_execucao/40_protocolo_multioutcome_rdd_bolsa.md`): "Dal Bó, Finan e Rossi, 2013: +15 p.p. de aceitação com +33% de salário".
<!-- E8:literatura:fim -->

Leitura:
- **Tamanho do degrau.** Em 0,400, o degrau relativo da bolsa é do mesmo
  tamanho do sorteio de Dal Bó, Finan e Rossi; em 0,300, é maior. Se a
  resposta aqui fosse da ordem da de lá, o salto de preenchimento ficaria
  acima da referência do protocolo. O IC empilhado do preenchimento (§5.1) não
  admite isso, sob as condições ditas. Os contextos e os outcomes não são
  iguais: lá, servidores públicos e aceitação da oferta; aqui, especialistas e
  célula com alguma confirmação ou homologação na 1ª chamada.
- **Prêmios por regra com efeito nulo no preenchimento existem.** Bobba et al.
  acham, numa RDD de prêmio por regra, preenchimento sem mudança e professor
  melhor. Aqui, a nota dos candidatos (F4) não mostra seleção positiva.
- **Incentivo que muda quem entra, não quanto.** Yong et al. acham mais
  entradas de recém-formados, menos entradas de outros e estoque igual.
  Khoury, Leganza e Masucci acham resposta só de médicos em início de carreira.
  Hone et al. acham, no Mais Médicos, ganho líquido bem menor que o bruto. É o
  padrão do E9 com o E6 e o E7: escolha que se move, provimento local que não
  se detecta.
- **Elasticidade menor no Brasil.** Costa, Nunes e Sanches estimam, para
  médicos no Brasil, elasticidade ao salário bem menor que a de Dal Bó et al.,
  com a origem do médico pesando mais. Um degrau de R$ 5 mil que mexe na
  escolha sem mexer no preenchimento é compatível com isso.

## 7. Revisão da pergunta e da hipótese econômica (PROPOSTA ao autor, não decisão)

> **Estatuto desta seção.** Tudo aqui é **proposta** para o autor decidir. Os
> achados estão nas seções anteriores. O protocolo 40 (§9) permite rever a pergunta
> econômica **depois** dos resultados, desde que a revisão seja registrada como
> tal e não reescreva o protocolo. Nenhuma proposta abaixo foi executada, e
> nenhuma muda o que foi estimado.

### 7.1 A hipótese original

**H1** ([`modelo_micro.md`](../02_teoria/modelo_micro.md), §4.2;
[`01_pergunta_escopo/15`](../01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md)):
no corte de IVS, +R$ 5 mil na bolsa anunciada aumentam o preenchimento das
vagas e o provimento local de especialistas. Na forma do modelo, o lado de
bolsa maior preenche quando o degrau monetário supera o degrau de custo
latente, ΔB/p > Δc₀, com c₀ contínuo no corte.

### 7.2 O que a evidência diz sobre H1 (achado)

- **Preenchimento, presença, oferta no CNES:** nenhum efeito detectado no
  corte. Com cortes e ciclos empilhados, saltos de preenchimento da ordem de
  +10 p.p. ficam fora do IC convencional. As estimativas pontuais são
  negativas na maior parte das linhas.
- **Escolha:** no ciclo 2, a bolsa desloca a 1ª opção dos candidatos para
  células de bolsa maior; nos outros ciclos, não se detecta.
- **Contraste:** pacote do corte, com co-políticas que também mudam no tempo.
- **Leitura combinada:** H1 não é sustentada como efeito local detectável no
  preenchimento e no provimento. A evidência também não é a de "nenhuma
  resposta": há resposta na escolha, sem tradução detectável em provimento.

### 7.3 Proposta A — Realocação entre vagas, sem expansão líquida detectável

**Formulação proposta.** O degrau da bolsa reordena a escolha dos candidatos
entre vagas (sorting) sem mudar, de forma detectável, o provimento agregado
local. A pergunta passa de "a bolsa atrai?" para "a bolsa **atrai** novos
especialistas ou **redistribui** um conjunto dado entre municípios?".

**Por que é coerente com a teoria.** No modelo (§3 do `modelo_micro.md`), o
médico escolhe m* no conjunto de vagas mais a opção de ficar fora. Um degrau em
B_m muda a utilidade relativa entre vagas. Se a margem extensiva (entrar no
programa) é pouco elástica, o efeito aparece na repartição entre vagas, e o
ganho de uma célula é perda de outra. O E9 mede exatamente essa repartição; o
E6 e o E7 medem o agregado local.

**O que testaria.**
- universo de inscrições e conjunto de escolha efetivo (pedido 2,
  `inscricoes_universo` e `opcoes_elegiveis`, em
  [`pedidos_dados/eventos_e_ponte_cnes.md`](../pedidos_dados/eventos_e_ponte_cnes.md)),
  para medir a margem extensiva, que o E9 não vê;
- um teste pré-especificado de deslocamento: se células de bolsa maior ganham
  candidatos à custa de células próximas de bolsa menor, na mesma região de
  saúde;
- o ciclo 3 maduro (seis meses só com a competência `202703` publicada e
  completa), para replicar o E9 fora da amostra que o gerou e medir a oferta
  líquida município–mês.

### 7.4 Proposta B — Elasticidade local da escolha à remuneração, relativa aos fatores não pecuniários

**Formulação proposta.** O parâmetro econômico relevante é a elasticidade da
escolha locacional do especialista à remuneração, **comparada** ao peso do
custo não pecuniário c₀(IVS), da distância e das amenidades. O desenho de
corte identifica essa resposta só em dois pontos do IVS, e como pacote. O
logit de escolha dá uma estimativa dentro do candidato, que permite
comparar o peso da bolsa com o de outros atributos da vaga.

**Por que é coerente com a teoria.** A condição de aceitação compara ΔB/p com
Δc₀. H3 (renda alternativa) e H4 (sinal ambíguo de c₀′) dizem que essa
comparação varia com o mercado privado local e com a composição do IVS. O
achado de que a escolha se move e o preenchimento não é compatível com uma
elasticidade pequena diante de c₀ e da distância.

**O que testaria.**
- distância ou faixa de distância entre a residência do candidato e a vaga
  (pedido 2, `vinculos_profissional_opcao`), que hoje falta ao E9 (doc 42, §1);
- razões entre coeficientes do logit (bolsa contra vaga imediata, porte,
  estrato), pré-registradas antes de abrir o ciclo 3;
- heterogeneidade pré-tratamento por mercado privado local (estrato A2), que
  é a leitura territorial de H3;
- remuneração efetivamente paga (pedido 3, folha mensal), para saber se o
  anunciado é o recebido.

### 7.5 Proposta C — De "a bolsa funciona?" para "quanto e em que margem?"

**Formulação proposta.** Trocar a pergunta binária por duas quantitativas:
(i) **quanto** de bolsa seria preciso para mover o preenchimento nos
municípios mais vulneráveis, isto é, de que tamanho é Δc₀ em reais; (ii)
**que margem** se move com o incentivo atual: escolha, preenchimento,
presença ou oferta líquida.

**Por que é coerente com a teoria.** O `modelo_micro.md` (§4.1) já diz que a
desigualdade ΔB/p > Δc₀ "não pergunta se o PMM-E funciona; pergunta se o preço
que o programa colocou sobre a vulnerabilidade é suficiente". A evidência atual
responde à segunda parte só pela negativa, e só localmente: com o degrau de
R$ 5 mil, não se detecta efeito no preenchimento.

**O que testaria.**
- um contrafactual de grade de bolsa a partir do modelo de escolha, no estilo
  de Costa, Nunes e Sanches ou de Bobba et al. (doc 20), rotulado como cenário
  e separado dos resultados empíricos (regra do `CLAUDE.md`), validado fora da
  amostra no ciclo 3;
- a cadeia completa por margem (escolha → preenchimento → presença → oferta
  líquida), com o ciclo 3 maduro e a ponte PMM-E–CNES (pedido 2).

### 7.6 O que não muda em nenhuma das propostas

- O contraste continua sendo o incentivo marginal anunciado. Não é
  participação no PMM-E nem Agora Tem Especialistas.
- O protocolo 40 e os resultados do E3 ao E9 não são reescritos.
- Pedidos externos de dados continuam fora até decisão do autor; os pacotes
  estão em [`pedidos_dados/`](../pedidos_dados/README.md) e não foram enviados.
- O ciclo 3 continua congelado até a maturidade.

## 8. Limitações

1. **Pacote, não bolsa.** Nenhum resultado em nível isola a bolsa. A DiRD só
   remove a parte constante das co-políticas.
2. **Potência.** Por corte e ciclo, poucas dezenas de municípios com vaga de
   cada lado. Só o empilhamento estreitou o IC.
3. **IC honesto sem informação.** Com o M da regra de bolso e suporte até o
   ponto médio entre cortes, ele não descarta nada.
4. **Seleção em V_k.** Os outcomes por célula só existem onde houve vaga; V1
   em 0,400 é suspeita (§5.4).
5. **Presença é retrato** e vínculo no CNES não é médico do PMM-E nem
   retenção.
6. **E9:** IIA, sem distância, escolha possivelmente estratégica, robustez
   pós-auditoria fora do protocolo.
7. **Exposição prévia:** parte do ciclo 1 já tinha sido vista antes do
   congelamento (protocolo §10).
8. **Muitos testes:** o BKY supõe dependência positiva entre linhas por corte e
   empilhadas, o que não foi verificado.

## 9. Próximos passos

1. **Decisão do autor** sobre a revisão da hipótese (seção 7): manter H1 como
   pergunta e relatar o nulo, ou adotar uma das propostas, com registro datado.
2. **Conteúdo canônico da apresentação** em `docs/07_apresentacoes/`, a partir
   deste documento.
3. **Artigos:** atualizar o texto da RDD da bolsa com esta síntese (tarefa
   posterior; os `.tex` não foram alterados aqui).
4. **Ciclo 3:** só na maturidade, com o plano congelado.
5. **Pedidos de dados:** decisão externa do autor.

## 10. Proveniência

<!-- E8:entradas:inicio -->
| Entrada | SHA-256 (início) | Papel |
|---|---|---|
| `output/rdd_bolsa/E3_estimativas.csv` | `b38a2d0ea11aaa1b…` | E3: ancora do ciclo 1 (F1.3 e presenca por corte) |
| `output/rdd_bolsa/E3_status.json` | `d9db202cd0044968…` | E3: status e contraste |
| `output/rdd_bolsa/E5_resumo.json` | `35d7a1c25dfc0b02…` | E5: MDE de 80% do F1.3 do ciclo 1 (exploratorio, pos-resultado) |
| `output/rdd_bolsa/E6_estimativas.csv` | `223b4c77326b8399…` | E6: F0, F1, F2, F4 e P1 (RDD em nivel = pacote do corte) |
| `output/rdd_bolsa/E6_diagnosticos.csv` | `4296c6120198664a…` | E6: densidade e balanco de V1 em 0,400 |
| `output/rdd_bolsa/E6_resumo.json` | `73724462b89f3f8f…` | E6: p de P1 para o Holm e contraste |
| `output/rdd_bolsa/E7_estimativas.csv` | `f6acdd7062cd0dad…` | E7: F3 (DiRD no CNES) e niveis |
| `output/rdd_bolsa/E7_estudo_evento.csv` | `bd1ff3d1b52018bd…` | E7: estudo de evento da DiRD |
| `output/rdd_bolsa/E7_resumo.json` | `dcdcd184348cbc82…` | E7: p de P2 para o Holm e contraste |
| `output/rdd_bolsa/E9_estimativas.csv` | `517e88d1488568c6…` | E9: logit condicional da 1a opcao (coeficiente da bolsa) |
| `output/rdd_bolsa/E9_efeitos_marginais.csv` | `812ac52a25cb2b86…` | E9: razao de chances e efeito na probabilidade por +R$ 5 mil |
| `output/rdd_bolsa/E9_robustez_pos_auditoria.csv` | `63b474225e4c5e7a…` | E9: robustez pos-auditoria (fora do protocolo) |
| `output/rdd_bolsa/E9_resumo.json` | `fff0ca8da645a478…` | E9: mapa faixa -> bolsa e natureza |
| `docs/06_execucao/40_protocolo_multioutcome_rdd_bolsa.md` | `85f11f309e033516…` | protocolo congelado (texto canonico) |
| `output/rdd_bolsa/protocolo_E6_multioutcome.json` | `a66fe6183562f8a2…` | protocolo congelado (maquina) |
| `docs/03_literatura_empirica/20_evidencia_empirica_hipotese_remuneracao_preenchimento.md` | `0ac000f5be5ae0ca…` | citacoes de magnitude da literatura (texto, nao resultado) |
<!-- E8:entradas:fim -->

## 11. Reprodução

```bash
python3 scripts/rdd_bolsa/15_sintese_E8.py                  # saídas do E8 e blocos deste doc
python3 scripts/rdd_bolsa/15_sintese_E8.py --atualizar-doc  # só os blocos, a partir das saídas
python3 -m unittest tests.test_e8_sintese
```
