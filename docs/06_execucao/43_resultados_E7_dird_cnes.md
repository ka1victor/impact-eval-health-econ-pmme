# 43 — Resultados do E7: diferença em descontinuidades no CNES (família F3)

> **Protocolo:** [`40_protocolo_multioutcome_rdd_bolsa.md`](40_protocolo_multioutcome_rdd_bolsa.md)
> (§3, §4, §5 F3, §6 painel CNES, §7 P2, §13 S1–S6, §16 horas SUS), congelado em
> 18/10/2026 (§16 acrescentado em 19/10/2026, antes de estimar o E7),
> e [`output/rdd_bolsa/protocolo_E6_multioutcome.json`](../../output/rdd_bolsa/protocolo_E6_multioutcome.json).<br>
> **Script:** [`scripts/rdd_bolsa/14_estimar_E7_dird_cnes.py`](../../scripts/rdd_bolsa/14_estimar_E7_dird_cnes.py),
> com os estimadores de [`rdd_lib.py`](../../scripts/rdd_bolsa/rdd_lib.py).<br>
> **Saídas:** `output/rdd_bolsa/E7_estimativas.csv`, `E7_estudo_evento.csv`,
> `E7_resumo.json` e `E7_figuras/`. Natureza dos dados: **EMPIRICO**.<br>
> **Painel:** CNES nacional município × grupo de CBO × mês (tarefa C,
> [`auditorias/aquisicao/A09`](../auditorias/aquisicao/A09_cnes_nacional.md)).<br>
> **Números:** todas as tabelas entre marcadores `E7:*` são geradas das saídas
> por `python3 scripts/rdd_bolsa/14_estimar_E7_dird_cnes.py --atualizar-doc`, e o
> teste `tests/test_e7_dird.py` confere que o doc bate com os CSV. Fora delas
> este texto não traz número de resultado.

## 1. O que a DiRD identifica

A bolsa do PMM-E sobe R$ 5 mil por mês em `s > 0,300` e em `s > 0,400` (IVS
2010 oficial do Ipea). Outras regras federais mudam nos mesmos cortes
([`auditorias/18`](../auditorias/18_politicas_nos_mesmos_cortes_ivs.md)): o
teto de vagas do PMMB (Portaria 752/2023), o estrato do cofinanciamento da APS
(Portaria 3.493/2024), o teto de emendas e parcelas de custeio com "IVS maior
que 0,3" e, em 0,400, a ajuda de custo do PMMB.

- **RDD em nível** (média do pré ou do pós, sem diferenciar) mede o **pacote
  do corte**: bolsa anunciada mais todas essas regras.
- **DiRD** (ΔY = média do pós − média do pré, RDD sobre ΔY) mede a **bolsa mais
  a variação, entre pré e pós, das descontinuidades das outras políticas**. Ela
  remove só a parte dessas políticas que é constante no tempo.
- **Ameaça que a DiRD não remove:** co-política cujo efeito no corte muda entre
  pré e pós. A auditoria 18 (§3.1) aponta o estoque de médicos de coparticipação
  do PMMB, o IED da APS (desde 05/2024), as emendas e parcelas de MAC e APS
  (atos e montantes novos a cada ano; em 2026 incluem o Agora Tem Especialistas)
  e o Eixo Vínculo (12/2025, dentro do pós). Duas ferramentas avaliam isso: o
  **placebo de generalistas** (F3.P1, e a CBO 225130 em separado, S6), que essas
  políticas movem e a bolsa do PMM-E não; e o **estudo de evento**, em que o
  salto das CBO-alvo deve ficar plano antes do PMM-E e não acompanhar as datas
  das outras políticas.
- **Nenhum resultado aqui é efeito da participação no PMM-E** nem do Agora Tem
  Especialistas. O contraste é o anúncio do incentivo marginal, nos limites
  acima.

## 2. Dados, outcomes e amostras

| Id | Outcome (grupo do painel a09) | População |
|---|---|---|
| F3.1 | vínculos nas CBO-alvo do PMM-E (`alvo_pmme`) por 10 mil hab. | U e V1 |
| F3.2 | município com ≥ 1 profissional nas CBO-alvo | U |
| F3.3 | horas SUS semanais (vínculos com `TP_SUS_NAO_SUS = 'S'`) nas CBO-alvo por 10 mil hab. | U |
| F3.3.sem_filtro_sus | sensibilidade rotulada (§16): as mesmas horas sem o filtro `TP_SUS_NAO_SUS` (coluna `horas_totais_amb_hosp`) | U |
| F3.3.soma_parcial | sensibilidade rotulada (§16): soma parcial das horas observadas, com a contagem de vínculos em branco (coluna `horas_sus_semanais_parcial`) | U |
| F3.P1 | vínculos de generalistas (225125, 225142, 225170) por 10 mil hab. | U |
| S6 | vínculos de médico de família e comunidade (225130) por 10 mil hab. | U |
| F3.P2 | vínculos de especialistas fora das CBO-alvo por 10 mil hab. | U |

- **Populações:** U = todos os municípios do IVS 2010 oficial (a08); V1 =
  municípios do quadro do ciclo 1. Denominador: população do Censo 2022.
- **Janelas:** pré 2024-06 a 2025-06; pós 2025-10 a 2026-08 (contém o início
  do ciclo 1 e do ciclo 2); referência do estudo de evento 2025-06; placebo
  dentro do pré 2024-12..2025-05 contra 2024-06..2024-11; pré extra (S5)
  2022-01..2023-03, competências disponíveis. Nenhuma competência a partir de
  2026-09 é lida.
- **Horas (F3.3, protocolo §16):** o principal soma as horas ambulatoriais e
  hospitalares só dos vínculos marcados como SUS (`TP_SUS_NAO_SUS = 'S'`). Célula
  com hora em branco fica sem valor, nunca zero, e o município sem todos os
  meses de uma janela sai daquele outcome naquela especificação; a contagem está
  na `nota` das linhas e em `validacoes.horas_ausentes` do resumo. A soma sem o
  filtro SUS e a soma parcial das horas observadas são sensibilidades rotuladas
  (`SENSIBILIDADE_PROTOCOLO_§16`), fora do BKY. O grupo de todos os médicos sem
  residentes não é outcome do E7.
- **Estimadores:** local linear, kernel triangular, h = 0,050, HC1 por corte;
  empilhado com intercepto e inclinações por corte e lado, salto comum, CR1 por
  município. Sensibilidade h = 0,030 e 0,080; IC honesto com M da regra de bolso
  (suporte até o ponto médio entre cortes), 0,5M e 2M; Y_pós com Y_pré como
  covariável; local randomization na janela do E5 (só covariáveis).

## 3. Hipótese primária P2

P2 é F3.1 por DiRD em U, cortes empilhados. O p abaixo entra no Holm com o p de
P1 (E6), feito pelo coordenador.

<!-- E7:p2:inicio -->
| Hipótese | n abaixo / acima | Salto | IC 95% (CR1) | IC honesto (M) | p | q BKY (F3) |
|---|---|---|---|---|---|---|
| P2: F3.1, U, cortes empilhados | 1446 / 1257 | +0,083 | [−0,309; +0,476] | [−9,958; +10,125] | **0,677** | 1,000 |
<!-- E7:p2:fim -->

## 4. Estimativas principais (DiRD, h = 0,050)

q BKY: dentro da família F3, sobre as linhas principais de F3.1 (U e V1), F3.2,
F3.3, F3.P1 e F3.P2, nos dois cortes e empilhado. S6 e as sensibilidades de
horas do §16 ficam fora do BKY.

<!-- E7:principal:inicio -->
| Outcome | População | Corte | n abaixo / acima | Salto | IC 95% | IC honesto (M) | p | q BKY |
|---|---|---|---|---|---|---|---|---|
| F3.1 | U | 0,300 | 859 / 654 | +0,287 | [−0,235; +0,810] | [−8,772; +9,347] | 0,281 | 1,000 |
| F3.1 | U | 0,400 | 587 / 603 | −0,178 | [−0,771; +0,415] | [−10,505; +10,149] | 0,556 | 1,000 |
| F3.1 | U | empilhado | 1446 / 1257 | +0,083 | [−0,309; +0,476] | [−9,958; +10,125] | 0,677 | 1,000 |
| F3.1 | V1 | 0,300 | 61 / 53 | −1,600 | [−3,613; +0,414] | [−56,544; +53,344] | 0,119 | 1,000 |
| F3.1 | V1 | 0,400 | 53 / 41 | −0,932 | [−3,509; +1,645] | [−14,151; +12,287] | 0,478 | 1,000 |
| F3.1 | V1 | empilhado | 114 / 94 | −1,234 | [−2,907; +0,439] | [−43,707; +41,239] | 0,148 | 1,000 |
| F3.2 | U | 0,300 | 859 / 654 | −0,7 p.p. | [−4,5; +3,1] | [−13,6; +12,2] | 0,719 | 1,000 |
| F3.2 | U | 0,400 | 587 / 603 | −4,7 p.p. | [−10,9; +1,5] | [−111,8; +102,3] | 0,136 | 1,000 |
| F3.2 | U | empilhado | 1446 / 1257 | −2,5 p.p. | [−5,9; +1,0] | [−105,8; +100,9] | 0,164 | 1,000 |
| F3.3 | U | 0,300 | 856 / 654 | +1,1 | [−3,8; +6,1] | [−50,8; +53,1] | 0,652 | 1,000 |
| F3.3 | U | 0,400 | 587 / 603 | −6,1 | [−13,7; +1,4] | [−96,5; +84,2] | 0,113 | 1,000 |
| F3.3 | U | empilhado | 1443 / 1257 | −2,0 | [−6,4; +2,3] | [−88,7; +84,6] | 0,359 | 1,000 |
| F3.3.sem_filtro_sus | U | 0,300 | 856 / 654 | +1,0 | [−4,0; +5,9] | [−28,7; +30,6] | 0,708 | — |
| F3.3.sem_filtro_sus | U | 0,400 | 587 / 603 | −4,9 | [−12,6; +2,9] | [−160,1; +150,4] | 0,217 | — |
| F3.3.sem_filtro_sus | U | empilhado | 1443 / 1257 | −1,6 | [−6,0; +2,8] | [−152,3; +149,1] | 0,476 | — |
| F3.3.soma_parcial | U | 0,300 | 859 / 654 | +1,1 | [−3,9; +6,1] | [−50,8; +53,1] | 0,660 | — |
| F3.3.soma_parcial | U | 0,400 | 587 / 603 | −6,1 | [−13,7; +1,4] | [−96,5; +84,2] | 0,113 | — |
| F3.3.soma_parcial | U | empilhado | 1446 / 1257 | −2,0 | [−6,4; +2,3] | [−88,7; +84,6] | 0,355 | — |
| F3.P1 | U | 0,300 | 859 / 654 | −0,071 | [−1,892; +1,750] | [−39,740; +39,599] | 0,939 | 1,000 |
| F3.P1 | U | 0,400 | 587 / 603 | −0,111 | [−1,045; +0,823] | [−67,794; +67,573] | 0,816 | 1,000 |
| F3.P1 | U | empilhado | 1446 / 1257 | −0,088 | [−1,190; +1,014] | [−67,071; +66,895] | 0,875 | 1,000 |
| F3.P2 | U | 0,300 | 859 / 654 | +0,229 | [−0,356; +0,814] | [−14,654; +15,112] | 0,443 | 1,000 |
| F3.P2 | U | 0,400 | 587 / 603 | −0,429 | [−1,048; +0,189] | [−20,262; +19,404] | 0,174 | 1,000 |
| F3.P2 | U | empilhado | 1446 / 1257 | −0,059 | [−0,485; +0,367] | [−19,483; +19,364] | 0,785 | 1,000 |
| S6 | U | 0,300 | 859 / 654 | +0,023 | [−0,076; +0,123] | [−1,064; +1,111] | 0,645 | — |
| S6 | U | 0,400 | 587 / 603 | −0,004 | [−0,050; +0,042] | [−0,346; +0,338] | 0,860 | — |
| S6 | U | empilhado | 1446 / 1257 | +0,011 | [−0,048; +0,071] | [−1,054; +1,077] | 0,708 | — |
<!-- E7:principal:fim -->

Figuras: `output/rdd_bolsa/E7_figuras/E7_dird_<outcome>_<população>.png`.

## 5. Sensibilidades e IC honesto

<!-- E7:sensibilidades:inicio -->
| Outcome | População | Corte | h = 0,030 | h = 0,080 | Y_pós com Y_pré covariável | donut (S2) | LR: janela, salto, p Fisher | painel (conferência) |
|---|---|---|---|---|---|---|---|---|
| F3.1 | U | 0,300 | +0,402 (p = 0,224) | +0,135 (p = 0,541) | +0,337 (p = 0,202) | +0,371 (p = 0,193) | sem janela | ponto idêntico; p CR1 = 0,280 |
| F3.1 | U | 0,400 | −0,672 (p = 0,252) | +0,171 (p = 0,673) | −0,306 (p = 0,501) | +0,011 (p = 0,970) | ±0,008: −0,099 (p = 0,782) | ponto idêntico; p CR1 = 0,555 |
| F3.1 | U | empilhado | −0,063 (p = 0,841) | +0,151 (p = 0,488) | +0,313 (p = 0,250) | +0,213 (p = 0,292) | — | — |
| F3.1 | V1 | 0,300 | −0,772 (p = 0,499) | −1,046 (p = 0,276) | −1,667 (p = 0,130) | −1,600 (p = 0,119) | ±0,020: −1,635 (p = 0,147) | ponto idêntico; p CR1 = 0,115 |
| F3.1 | V1 | 0,400 | −0,853 (p = 0,621) | −0,616 (p = 0,518) | −0,949 (p = 0,302) | +0,236 (p = 0,775) | ±0,007: −0,358 (p = 0,910) | ponto idêntico; p CR1 = 0,472 |
| F3.1 | V1 | empilhado | −0,823 (p = 0,478) | −0,826 (p = 0,223) | −1,180 (p = 0,136) | −0,651 (p = 0,325) | — | — |
| F3.2 | U | 0,300 | −0,3 p.p. (p = 0,919) | −0,8 p.p. (p = 0,609) | −0,4 p.p. (p = 0,817) | +0,3 p.p. (p = 0,897) | sem janela | ponto idêntico; p CR1 = 0,719 |
| F3.2 | U | 0,400 | −5,9 p.p. (p = 0,150) | −3,5 p.p. (p = 0,152) | −3,6 p.p. (p = 0,211) | −5,7 p.p. (p = 0,093) | ±0,008: −5,4 p.p. (p = 0,144) | ponto idêntico; p CR1 = 0,136 |
| F3.2 | U | empilhado | −2,7 p.p. (p = 0,237) | −2,0 p.p. (p = 0,151) | −1,8 p.p. (p = 0,260) | −2,4 p.p. (p = 0,203) | — | — |
| F3.3 | U | 0,300 | +2,4 (p = 0,453) | +1,6 (p = 0,478) | +1,6 (p = 0,513) | +1,7 (p = 0,531) | sem janela | ponto idêntico; p CR1 = 0,652 |
| F3.3 | U | 0,400 | −6,0 (p = 0,257) | −4,3 (p = 0,148) | −6,6 (p = 0,070) | −3,6 (p = 0,243) | ±0,008: −2,2 (p = 0,636) | ponto idêntico; p CR1 = 0,113 |
| F3.3 | U | empilhado | −1,2 (p = 0,668) | −1,0 (p = 0,579) | −1,8 (p = 0,391) | −0,6 (p = 0,748) | — | — |
| F3.3.sem_filtro_sus | U | 0,300 | +2,2 (p = 0,479) | +1,4 (p = 0,541) | +1,6 (p = 0,512) | +1,3 (p = 0,615) | sem janela | ponto idêntico; p CR1 = 0,708 |
| F3.3.sem_filtro_sus | U | 0,400 | −6,5 (p = 0,271) | −2,1 (p = 0,564) | −6,8 (p = 0,086) | −2,4 (p = 0,454) | ±0,008: −0,8 (p = 0,862) | ponto idêntico; p CR1 = 0,217 |
| F3.3.sem_filtro_sus | U | empilhado | −1,6 (p = 0,615) | −0,2 (p = 0,939) | −1,1 (p = 0,627) | −0,3 (p = 0,883) | — | — |
| F3.3.soma_parcial | U | 0,300 | +2,3 (p = 0,461) | +1,5 (p = 0,493) | +1,6 (p = 0,515) | +1,6 (p = 0,539) | sem janela | ponto idêntico; p CR1 = 0,660 |
| F3.3.soma_parcial | U | 0,400 | −6,0 (p = 0,257) | −4,3 (p = 0,149) | −6,6 (p = 0,070) | −3,6 (p = 0,243) | ±0,008: −2,2 (p = 0,636) | ponto idêntico; p CR1 = 0,113 |
| F3.3.soma_parcial | U | empilhado | −1,3 (p = 0,662) | −1,0 (p = 0,569) | −1,8 (p = 0,390) | −0,7 (p = 0,741) | — | — |
| F3.P1 | U | 0,300 | +0,508 (p = 0,683) | −0,405 (p = 0,578) | −0,106 (p = 0,909) | −0,434 (p = 0,648) | sem janela | ponto idêntico; p CR1 = 0,939 |
| F3.P1 | U | 0,400 | −1,919 (p = 0,231) | +0,709 (p = 0,566) | +0,719 (p = 0,460) | +0,067 (p = 0,893) | ±0,008: −0,183 (p = 0,726) | ponto idêntico; p CR1 = 0,816 |
| F3.P1 | U | empilhado | −0,544 (p = 0,581) | +0,085 (p = 0,900) | +0,704 (p = 0,455) | −0,215 (p = 0,710) | — | — |
| F3.P2 | U | 0,300 | +0,436 (p = 0,234) | +0,178 (p = 0,471) | +0,278 (p = 0,351) | +0,282 (p = 0,362) | sem janela | ponto idêntico; p CR1 = 0,442 |
| F3.P2 | U | 0,400 | −0,206 (p = 0,626) | −0,224 (p = 0,375) | −0,514 (p = 0,099) | −0,326 (p = 0,287) | ±0,008: +0,060 (p = 0,861) | ponto idêntico; p CR1 = 0,173 |
| F3.P2 | U | empilhado | +0,158 (p = 0,567) | +0,001 (p = 0,995) | −0,037 (p = 0,865) | +0,016 (p = 0,942) | — | — |
| S6 | U | 0,300 | +0,090 (p = 0,168) | +0,009 (p = 0,821) | +0,029 (p = 0,569) | +0,014 (p = 0,800) | sem janela | ponto idêntico; p CR1 = 0,645 |
| S6 | U | 0,400 | +0,003 (p = 0,905) | −0,010 (p = 0,629) | −0,003 (p = 0,879) | −0,008 (p = 0,741) | ±0,008: −0,007 (p = 0,756) | ponto idêntico; p CR1 = 0,860 |
| S6 | U | empilhado | +0,052 (p = 0,176) | +0,001 (p = 0,968) | +0,015 (p = 0,628) | +0,004 (p = 0,897) | — | — |
<!-- E7:sensibilidades:fim -->

<!-- E7:honesto:inicio -->
| Outcome | População | Corte | fator de M | M | IC honesto | p honesto |
|---|---|---|---|---|---|---|
| F3.1 | U | 0,300 | 0,5 | 9402,2 | [−4,461; +5,036] | 1,000 |
| F3.1 | U | 0,300 | 1,0 | 18804,5 | [−8,772; +9,347] | 1,000 |
| F3.1 | U | 0,300 | 2,0 | 37609,0 | [−17,394; +17,969] | 1,000 |
| F3.1 | U | 0,400 | 0,5 | 10486,0 | [−5,587; +5,231] | 1,000 |
| F3.1 | U | 0,400 | 1,0 | 20971,9 | [−10,505; +10,149] | 1,000 |
| F3.1 | U | 0,400 | 2,0 | 41943,9 | [−20,341; +19,984] | 1,000 |
| F3.1 | U | empilhado | 0,5 | 10486,0 | [−5,102; +5,269] | 1,000 |
| F3.1 | U | empilhado | 1,0 | 20971,9 | [−9,958; +10,125] | 1,000 |
| F3.1 | U | empilhado | 2,0 | 41943,9 | [−19,670; +19,837] | 1,000 |
| F3.1 | V1 | 0,300 | 0,5 | 43573,8 | [−29,942; +26,742] | 1,000 |
| F3.1 | V1 | 0,300 | 1,0 | 87147,7 | [−56,544; +53,344] | 1,000 |
| F3.1 | V1 | 0,300 | 2,0 | 174295,4 | [−109,749; +106,549] | 1,000 |
| F3.1 | V1 | 0,400 | 0,5 | 15466,7 | [−8,640; +6,775] | 1,000 |
| F3.1 | V1 | 0,400 | 1,0 | 30933,4 | [−14,151; +12,287] | 1,000 |
| F3.1 | V1 | 0,400 | 2,0 | 61866,8 | [−25,175; +23,311] | 1,000 |
| F3.1 | V1 | empilhado | 0,5 | 43573,8 | [−23,173; +20,705] | 1,000 |
| F3.1 | V1 | empilhado | 1,0 | 87147,7 | [−43,707; +41,239] | 1,000 |
| F3.1 | V1 | empilhado | 2,0 | 174295,4 | [−84,775; +82,307] | 1,000 |
| F3.2 | U | 0,300 | 0,5 | 106,0 | [−8,8; +7,4] | 0,986 |
| F3.2 | U | 0,300 | 1,0 | 212,1 | [−13,6; +12,2] | 1,000 |
| F3.2 | U | 0,300 | 2,0 | 424,2 | [−23,4; +22,0] | 1,000 |
| F3.2 | U | 0,400 | 0,5 | 1084,9 | [−60,9; +51,4] | 1,000 |
| F3.2 | U | 0,400 | 1,0 | 2169,8 | [−111,8; +102,3] | 1,000 |
| F3.2 | U | 0,400 | 2,0 | 4339,5 | [−213,5; +204,1] | 1,000 |
| F3.2 | U | empilhado | 0,5 | 1084,9 | [−55,6; +50,7] | 1,000 |
| F3.2 | U | empilhado | 1,0 | 2169,8 | [−105,8; +100,9] | 1,000 |
| F3.2 | U | empilhado | 2,0 | 4339,5 | [−206,3; +201,4] | 1,000 |
| F3.3 | U | 0,300 | 0,5 | 52081,3 | [−26,9; +29,2] | 1,000 |
| F3.3 | U | 0,300 | 1,0 | 104162,6 | [−50,8; +53,1] | 1,000 |
| F3.3 | U | 0,300 | 2,0 | 208325,1 | [−98,5; +100,8] | 1,000 |
| F3.3 | U | 0,400 | 0,5 | 89628,8 | [−54,4; +42,2] | 1,000 |
| F3.3 | U | 0,400 | 1,0 | 179257,5 | [−96,5; +84,2] | 1,000 |
| F3.3 | U | 0,400 | 2,0 | 358515,1 | [−180,5; +168,3] | 1,000 |
| F3.3 | U | empilhado | 0,5 | 89628,8 | [−47,2; +43,1] | 1,000 |
| F3.3 | U | empilhado | 1,0 | 179257,5 | [−88,7; +84,6] | 1,000 |
| F3.3 | U | empilhado | 2,0 | 358515,1 | [−171,7; +167,6] | 1,000 |
| F3.3.sem_filtro_sus | U | 0,300 | 0,5 | 27759,4 | [−15,9; +17,8] | 1,000 |
| F3.3.sem_filtro_sus | U | 0,300 | 1,0 | 55518,8 | [−28,7; +30,6] | 1,000 |
| F3.3.sem_filtro_sus | U | 0,300 | 2,0 | 111037,6 | [−54,1; +56,0] | 1,000 |
| F3.3.sem_filtro_sus | U | 0,400 | 0,5 | 158758,7 | [−85,7; +76,0] | 1,000 |
| F3.3.sem_filtro_sus | U | 0,400 | 1,0 | 317517,4 | [−160,1; +150,4] | 1,000 |
| F3.3.sem_filtro_sus | U | 0,400 | 2,0 | 635034,7 | [−309,1; +299,3] | 1,000 |
| F3.3.sem_filtro_sus | U | empilhado | 0,5 | 158758,7 | [−78,8; +75,6] | 1,000 |
| F3.3.sem_filtro_sus | U | empilhado | 1,0 | 317517,4 | [−152,3; +149,1] | 1,000 |
| F3.3.sem_filtro_sus | U | empilhado | 2,0 | 635034,7 | [−299,3; +296,1] | 1,000 |
| F3.3.soma_parcial | U | 0,300 | 0,5 | 52081,3 | [−26,9; +29,2] | 1,000 |
| F3.3.soma_parcial | U | 0,300 | 1,0 | 104162,6 | [−50,8; +53,1] | 1,000 |
| F3.3.soma_parcial | U | 0,300 | 2,0 | 208325,1 | [−98,6; +100,8] | 1,000 |
| F3.3.soma_parcial | U | 0,400 | 0,5 | 89628,8 | [−54,4; +42,2] | 1,000 |
| F3.3.soma_parcial | U | 0,400 | 1,0 | 179257,5 | [−96,5; +84,2] | 1,000 |
| F3.3.soma_parcial | U | 0,400 | 2,0 | 358515,1 | [−180,5; +168,3] | 1,000 |
| F3.3.soma_parcial | U | empilhado | 0,5 | 89628,8 | [−47,2; +43,1] | 1,000 |
| F3.3.soma_parcial | U | empilhado | 1,0 | 179257,5 | [−88,7; +84,6] | 1,000 |
| F3.3.soma_parcial | U | empilhado | 2,0 | 358515,1 | [−171,7; +167,6] | 1,000 |
| F3.P1 | U | 0,300 | 0,5 | 41614,6 | [−20,660; +20,519] | 1,000 |
| F3.P1 | U | 0,300 | 1,0 | 83229,2 | [−39,740; +39,599] | 1,000 |
| F3.P1 | U | 0,300 | 2,0 | 166458,4 | [−77,900; +77,759] | 1,000 |
| F3.P1 | U | 0,400 | 0,5 | 71323,2 | [−34,344; +34,123] | 1,000 |
| F3.P1 | U | 0,400 | 1,0 | 142646,4 | [−67,794; +67,573] | 1,000 |
| F3.P1 | U | 0,400 | 2,0 | 285292,7 | [−134,695; +134,473] | 1,000 |
| F3.P1 | U | empilhado | 0,5 | 71323,2 | [−34,042; +33,866] | 1,000 |
| F3.P1 | U | empilhado | 1,0 | 142646,4 | [−67,071; +66,895] | 1,000 |
| F3.P1 | U | empilhado | 2,0 | 285292,7 | [−133,130; +132,953] | 1,000 |
| F3.P2 | U | 0,300 | 0,5 | 15700,4 | [−7,455; +7,913] | 1,000 |
| F3.P2 | U | 0,300 | 1,0 | 31400,9 | [−14,654; +15,112] | 1,000 |
| F3.P2 | U | 0,300 | 2,0 | 62801,7 | [−29,051; +29,509] | 1,000 |
| F3.P2 | U | 0,400 | 0,5 | 20585,5 | [−10,608; +9,749] | 1,000 |
| F3.P2 | U | 0,400 | 1,0 | 41171,1 | [−20,262; +19,404] | 1,000 |
| F3.P2 | U | 0,400 | 2,0 | 82342,2 | [−39,571; +38,713] | 1,000 |
| F3.P2 | U | empilhado | 0,5 | 20585,5 | [−9,950; +9,831] | 1,000 |
| F3.P2 | U | empilhado | 1,0 | 41171,1 | [−19,483; +19,364] | 1,000 |
| F3.P2 | U | empilhado | 2,0 | 82342,2 | [−38,549; +38,430] | 1,000 |
| S6 | U | 0,300 | 0,5 | 1096,5 | [−0,562; +0,608] | 1,000 |
| S6 | U | 0,300 | 1,0 | 2193,0 | [−1,064; +1,111] | 1,000 |
| S6 | U | 0,300 | 2,0 | 4386,1 | [−2,070; +2,117] | 1,000 |
| S6 | U | 0,400 | 0,5 | 324,0 | [−0,194; +0,186] | 1,000 |
| S6 | U | 0,400 | 1,0 | 648,0 | [−0,346; +0,338] | 1,000 |
| S6 | U | 0,400 | 2,0 | 1296,0 | [−0,650; +0,642] | 1,000 |
| S6 | U | empilhado | 0,5 | 1096,5 | [−0,546; +0,569] | 1,000 |
| S6 | U | empilhado | 1,0 | 2193,0 | [−1,054; +1,077] | 1,000 |
| S6 | U | empilhado | 2,0 | 4386,1 | [−2,070; +2,092] | 1,000 |
<!-- E7:honesto:fim -->

## 6. Placebo dentro do pré

Não é um nulo limpo: o IED da APS começou em 05/2024, o incentivo de nutrição
em 11/2024 e as emendas de 2025 em 04–05/2025 (auditoria 18, §3.1).

<!-- E7:placebo_pre:inicio -->
| Outcome | População | Corte | Especificação | n abaixo / acima | Salto | IC 95% | p |
|---|---|---|---|---|---|---|---|
| F3.1 | U | 0,300 | placebo_pre | 859 / 654 | −0,050 | [−0,376; +0,276] | 0,764 |
| F3.1 | U | 0,400 | placebo_pre | 587 / 603 | +0,038 | [−0,239; +0,315] | 0,790 |
| F3.1 | U | empilhado | placebo_pre | 1446 / 1257 | −0,012 | [−0,231; +0,208] | 0,917 |
| F3.1 | V1 | 0,300 | placebo_pre | 61 / 53 | −1,421 | [−2,800; −0,041] | 0,044 |
| F3.1 | V1 | 0,400 | placebo_pre | 53 / 41 | +0,747 | [−0,220; +1,713] | 0,130 |
| F3.1 | V1 | empilhado | placebo_pre | 114 / 94 | −0,233 | [−1,081; +0,615] | 0,590 |
| F3.2 | U | 0,300 | placebo_pre | 859 / 654 | +0,3 p.p. | [−2,2; +2,8] | 0,805 |
| F3.2 | U | 0,400 | placebo_pre | 587 / 603 | −2,5 p.p. | [−6,5; +1,6] | 0,235 |
| F3.2 | U | empilhado | placebo_pre | 1446 / 1257 | −0,9 p.p. | [−3,2; +1,4] | 0,433 |
| F3.3 | U | 0,300 | placebo_pre | 856 / 654 | +1,3 | [−2,5; +5,1] | 0,515 |
| F3.3 | U | 0,400 | placebo_pre | 587 / 603 | −1,1 | [−4,4; +2,1] | 0,501 |
| F3.3 | U | empilhado | placebo_pre | 1443 / 1257 | +0,2 | [−2,4; +2,8] | 0,868 |
| F3.3.sem_filtro_sus | U | 0,300 | placebo_pre | 856 / 654 | +0,9 | [−2,9; +4,8] | 0,639 |
| F3.3.sem_filtro_sus | U | 0,400 | placebo_pre | 587 / 603 | +0,1 | [−3,4; +3,5] | 0,972 |
| F3.3.sem_filtro_sus | U | empilhado | placebo_pre | 1443 / 1257 | +0,5 | [−2,1; +3,2] | 0,686 |
| F3.3.soma_parcial | U | 0,300 | placebo_pre | 859 / 654 | +1,2 | [−2,6; +5,0] | 0,524 |
| F3.3.soma_parcial | U | 0,400 | placebo_pre | 587 / 603 | −1,1 | [−4,4; +2,1] | 0,501 |
| F3.3.soma_parcial | U | empilhado | placebo_pre | 1446 / 1257 | +0,2 | [−2,4; +2,8] | 0,877 |
| F3.P1 | U | 0,300 | placebo_pre | 859 / 654 | −0,117 | [−1,526; +1,291] | 0,870 |
| F3.P1 | U | 0,400 | placebo_pre | 587 / 603 | −0,302 | [−0,925; +0,322] | 0,343 |
| F3.P1 | U | empilhado | placebo_pre | 1446 / 1257 | −0,198 | [−1,035; +0,639] | 0,643 |
| F3.P2 | U | 0,300 | placebo_pre | 859 / 654 | +0,182 | [−0,160; +0,524] | 0,298 |
| F3.P2 | U | 0,400 | placebo_pre | 587 / 603 | −0,095 | [−0,441; +0,251] | 0,589 |
| F3.P2 | U | empilhado | placebo_pre | 1446 / 1257 | +0,060 | [−0,185; +0,305] | 0,629 |
| S6 | U | 0,300 | placebo_pre | 859 / 654 | −0,019 | [−0,039; +0,001] | 0,065 |
| S6 | U | 0,400 | placebo_pre | 587 / 603 | −0,015 | [−0,055; +0,025] | 0,471 |
| S6 | U | empilhado | placebo_pre | 1446 / 1257 | −0,017 | [−0,038; +0,004] | 0,109 |
<!-- E7:placebo_pre:fim -->

## 7. RDD em nível: o pacote do corte

<!-- E7:niveis:inicio -->
| Outcome | População | Corte | nível pré extra | nível pré | nível pós | DiRD (principal) |
|---|---|---|---|---|---|---|
| F3.1 | U | 0,300 | −1,811 [−3,591; −0,030] | −2,147 [−4,192; −0,101] | −1,859 [−4,008; +0,289] | +0,287 [−0,235; +0,810] |
| F3.1 | U | 0,400 | +0,346 [−1,423; +2,114] | +0,287 [−1,750; +2,323] | +0,108 [−2,208; +2,424] | −0,178 [−0,771; +0,415] |
| F3.1 | U | empilhado | −0,866 [−2,132; +0,400] | −1,081 [−2,536; +0,374] | −0,998 [−2,574; +0,579] | +0,083 [−0,309; +0,476] |
| F3.1 | V1 | 0,300 | +0,505 [−10,238; +11,248] | −3,563 [−15,409; +8,283] | −5,163 [−17,189; +6,863] | −1,600 [−3,613; +0,414] |
| F3.1 | V1 | 0,400 | −0,407 [−11,604; +10,789] | +0,125 [−12,837; +13,086] | −0,807 [−15,730; +14,115] | −0,932 [−3,509; +1,645] |
| F3.1 | V1 | empilhado | +0,005 [−7,793; +7,804] | −1,542 [−10,425; +7,340] | −2,776 [−12,578; +7,026] | −1,234 [−2,907; +0,439] |
| F3.2 | U | 0,300 | −3,0 p.p. [−10,5; +4,6] | +1,4 p.p. [−5,5; +8,2] | +0,7 p.p. [−5,8; +7,2] | −0,7 p.p. [−4,5; +3,1] |
| F3.2 | U | 0,400 | +6,5 p.p. [−3,6; +16,6] | +5,1 p.p. [−4,6; +14,7] | +0,3 p.p. [−8,5; +9,2] | −4,7 p.p. [−10,9; +1,5] |
| F3.2 | U | empilhado | +1,2 p.p. [−4,9; +7,3] | +3,0 p.p. [−2,7; +8,7] | +0,5 p.p. [−4,8; +5,9] | −2,5 p.p. [−5,9; +1,0] |
| F3.3 | U | 0,300 | −14,6 [−30,8; +1,5] | −11,2 [−30,2; +7,7] | −10,1 [−30,5; +10,3] | +1,1 [−3,8; +6,1] |
| F3.3 | U | 0,400 | +6,4 [−11,2; +24,0] | +6,1 [−15,4; +27,6] | +0,0 [−25,3; +25,4] | −6,1 [−13,7; +1,4] |
| F3.3 | U | empilhado | −5,4 [−17,3; +6,5] | −3,6 [−17,9; +10,6] | −5,7 [−21,6; +10,3] | −2,0 [−6,4; +2,3] |
| F3.3.sem_filtro_sus | U | 0,300 | −18,0 [−39,0; +3,1] | −15,6 [−39,8; +8,7] | −14,6 [−40,3; +11,1] | +1,0 [−4,0; +5,9] |
| F3.3.sem_filtro_sus | U | 0,400 | +7,2 [−12,1; +26,4] | +8,4 [−14,9; +31,6] | +3,5 [−23,8; +30,8] | −4,9 [−12,6; +2,9] |
| F3.3.sem_filtro_sus | U | empilhado | −6,9 [−21,5; +7,6] | −5,1 [−22,1; +11,9] | −6,7 [−25,4; +12,1] | −1,6 [−6,0; +2,8] |
| F3.3.soma_parcial | U | 0,300 | −15,0 [−31,1; +1,1] | −11,6 [−30,6; +7,4] | −10,5 [−31,0; +10,0] | +1,1 [−3,9; +6,1] |
| F3.3.soma_parcial | U | 0,400 | +6,4 [−11,2; +24,0] | +6,1 [−15,4; +27,6] | +0,0 [−25,3; +25,4] | −6,1 [−13,7; +1,4] |
| F3.3.soma_parcial | U | empilhado | −5,6 [−17,6; +6,3] | −3,8 [−18,1; +10,4] | −5,9 [−21,9; +10,1] | −2,0 [−6,4; +2,3] |
| F3.P1 | U | 0,300 | −0,732 [−2,849; +1,384] | −1,498 [−4,191; +1,195] | −1,569 [−4,380; +1,242] | −0,071 [−1,892; +1,750] |
| F3.P1 | U | 0,400 | +0,111 [−1,382; +1,603] | −0,848 [−2,663; +0,967] | −0,959 [−3,103; +1,186] | −0,111 [−1,045; +0,823] |
| F3.P1 | U | empilhado | −0,363 [−1,720; +0,994] | −1,213 [−2,922; +0,496] | −1,302 [−3,139; +0,536] | −0,088 [−1,190; +1,014] |
| F3.P2 | U | 0,300 | −1,412 [−3,325; +0,501] | −1,776 [−3,979; +0,427] | −1,546 [−3,871; +0,778] | +0,229 [−0,356; +0,814] |
| F3.P2 | U | 0,400 | +0,795 [−0,424; +2,015] | +0,944 [−0,499; +2,386] | +0,514 [−1,149; +2,178] | −0,429 [−1,048; +0,189] |
| F3.P2 | U | empilhado | −0,445 [−1,648; +0,758] | −0,585 [−1,977; +0,808] | −0,644 [−2,141; +0,853] | −0,059 [−0,485; +0,367] |
| S6 | U | 0,300 | −0,009 [−0,070; +0,053] | +0,024 [−0,069; +0,116] | +0,047 [−0,058; +0,153] | +0,023 [−0,076; +0,123] |
| S6 | U | 0,400 | +0,051 [−0,005; +0,107] | +0,023 [−0,050; +0,097] | +0,019 [−0,074; +0,112] | −0,004 [−0,050; +0,042] |
| S6 | U | empilhado | +0,017 [−0,025; +0,060] | +0,024 [−0,037; +0,085] | +0,035 [−0,037; +0,107] | +0,011 [−0,048; +0,071] |
<!-- E7:niveis:fim -->

Figuras: `output/rdd_bolsa/E7_figuras/E7_nivel_<outcome>_<população>.png`.

## 8. Pré extra (S5)

`S5_pre_menos_pre_extra` testa se a descontinuidade se moveu entre 2022–2023 e
o pré principal, antes do PMM-E; `S5_dird_pre_extra` é a DiRD com o pré extra.
O pré extra antecede todas as regras com corte em 0,3 ou 0,4 encontradas, mas
contém as Portarias 377/2022 e 1.054/2022, que usam o IVS dentro de índice
composto (auditoria 18, §3.2).

<!-- E7:s5:inicio -->
| Outcome | População | Corte | Especificação | n abaixo / acima | Salto | IC 95% | p |
|---|---|---|---|---|---|---|---|
| F3.1 | U | 0,300 | S5_pre_menos_pre_extra | 859 / 654 | −0,336 | [−1,074; +0,401] | 0,372 |
| F3.1 | U | 0,300 | S5_dird_pre_extra | 859 / 654 | −0,049 | [−0,962; +0,864] | 0,916 |
| F3.1 | U | 0,400 | S5_pre_menos_pre_extra | 587 / 603 | −0,059 | [−0,672; +0,554] | 0,850 |
| F3.1 | U | 0,400 | S5_dird_pre_extra | 587 / 603 | −0,237 | [−1,153; +0,678] | 0,611 |
| F3.1 | U | empilhado | S5_pre_menos_pre_extra | 1446 / 1257 | −0,215 | [−0,708; +0,279] | 0,394 |
| F3.1 | U | empilhado | S5_dird_pre_extra | 1446 / 1257 | −0,131 | [−0,783; +0,520] | 0,692 |
| F3.1 | V1 | 0,300 | S5_pre_menos_pre_extra | 61 / 53 | −4,068 | [−6,349; −1,788] | 0,000 |
| F3.1 | V1 | 0,300 | S5_dird_pre_extra | 61 / 53 | −5,668 | [−9,124; −2,212] | 0,001 |
| F3.1 | V1 | 0,400 | S5_pre_menos_pre_extra | 53 / 41 | +0,532 | [−2,163; +3,227] | 0,699 |
| F3.1 | V1 | 0,400 | S5_dird_pre_extra | 53 / 41 | −0,400 | [−4,737; +3,937] | 0,857 |
| F3.1 | V1 | empilhado | S5_pre_menos_pre_extra | 114 / 94 | −1,547 | [−3,407; +0,312] | 0,103 |
| F3.1 | V1 | empilhado | S5_dird_pre_extra | 114 / 94 | −2,781 | [−5,659; +0,096] | 0,058 |
| F3.2 | U | 0,300 | S5_pre_menos_pre_extra | 859 / 654 | +4,3 p.p. | [−0,7; +9,4] | 0,092 |
| F3.2 | U | 0,300 | S5_dird_pre_extra | 859 / 654 | +3,6 p.p. | [−2,3; +9,5] | 0,227 |
| F3.2 | U | 0,400 | S5_pre_menos_pre_extra | 587 / 603 | −1,4 p.p. | [−7,5; +4,7] | 0,650 |
| F3.2 | U | 0,400 | S5_dird_pre_extra | 587 / 603 | −6,1 p.p. | [−14,5; +2,2] | 0,149 |
| F3.2 | U | empilhado | S5_pre_menos_pre_extra | 1446 / 1257 | +1,8 p.p. | [−2,1; +5,7] | 0,359 |
| F3.2 | U | empilhado | S5_dird_pre_extra | 1446 / 1257 | −0,6 p.p. | [−5,6; +4,3] | 0,799 |
| F3.3 | U | 0,300 | S5_pre_menos_pre_extra | 856 / 654 | +3,4 | [−5,5; +12,3] | 0,456 |
| F3.3 | U | 0,300 | S5_dird_pre_extra | 856 / 654 | +4,5 | [−6,3; +15,3] | 0,410 |
| F3.3 | U | 0,400 | S5_pre_menos_pre_extra | 587 / 603 | −0,3 | [−8,1; +7,6] | 0,950 |
| F3.3 | U | 0,400 | S5_dird_pre_extra | 587 / 603 | −6,4 | [−18,4; +5,7] | 0,302 |
| F3.3 | U | empilhado | S5_pre_menos_pre_extra | 1443 / 1257 | +1,8 | [−4,3; +7,9] | 0,564 |
| F3.3 | U | empilhado | S5_dird_pre_extra | 1443 / 1257 | −0,2 | [−8,3; +7,8] | 0,953 |
| F3.3.sem_filtro_sus | U | 0,300 | S5_pre_menos_pre_extra | 856 / 654 | +2,4 | [−6,8; +11,6] | 0,610 |
| F3.3.sem_filtro_sus | U | 0,300 | S5_dird_pre_extra | 856 / 654 | +3,4 | [−7,8; +14,5] | 0,556 |
| F3.3.sem_filtro_sus | U | 0,400 | S5_pre_menos_pre_extra | 587 / 603 | +1,2 | [−7,0; +9,3] | 0,777 |
| F3.3.sem_filtro_sus | U | 0,400 | S5_dird_pre_extra | 587 / 603 | −3,7 | [−16,2; +8,8] | 0,563 |
| F3.3.sem_filtro_sus | U | empilhado | S5_pre_menos_pre_extra | 1443 / 1257 | +1,9 | [−4,4; +8,2] | 0,562 |
| F3.3.sem_filtro_sus | U | empilhado | S5_dird_pre_extra | 1443 / 1257 | +0,3 | [−8,1; +8,6] | 0,950 |
| F3.3.soma_parcial | U | 0,300 | S5_pre_menos_pre_extra | 859 / 654 | +3,4 | [−5,5; +12,3] | 0,456 |
| F3.3.soma_parcial | U | 0,300 | S5_dird_pre_extra | 859 / 654 | +4,5 | [−6,3; +15,3] | 0,413 |
| F3.3.soma_parcial | U | 0,400 | S5_pre_menos_pre_extra | 587 / 603 | −0,3 | [−8,1; +7,6] | 0,950 |
| F3.3.soma_parcial | U | 0,400 | S5_dird_pre_extra | 587 / 603 | −6,4 | [−18,4; +5,7] | 0,302 |
| F3.3.soma_parcial | U | empilhado | S5_pre_menos_pre_extra | 1446 / 1257 | +1,8 | [−4,3; +7,9] | 0,563 |
| F3.3.soma_parcial | U | empilhado | S5_dird_pre_extra | 1446 / 1257 | −0,3 | [−8,3; +7,8] | 0,951 |
| F3.P1 | U | 0,300 | S5_pre_menos_pre_extra | 859 / 654 | −0,766 | [−2,450; +0,918] | 0,373 |
| F3.P1 | U | 0,300 | S5_dird_pre_extra | 859 / 654 | −0,837 | [−2,929; +1,256] | 0,433 |
| F3.P1 | U | 0,400 | S5_pre_menos_pre_extra | 587 / 603 | −0,958 | [−1,962; +0,045] | 0,061 |
| F3.P1 | U | 0,400 | S5_dird_pre_extra | 587 / 603 | −1,069 | [−2,468; +0,330] | 0,134 |
| F3.P1 | U | empilhado | S5_pre_menos_pre_extra | 1446 / 1257 | −0,850 | [−1,893; +0,193] | 0,110 |
| F3.P1 | U | empilhado | S5_dird_pre_extra | 1446 / 1257 | −0,938 | [−2,265; +0,388] | 0,165 |
| F3.P2 | U | 0,300 | S5_pre_menos_pre_extra | 859 / 654 | −0,364 | [−1,185; +0,457] | 0,385 |
| F3.P2 | U | 0,300 | S5_dird_pre_extra | 859 / 654 | −0,135 | [−1,156; +0,887] | 0,796 |
| F3.P2 | U | 0,400 | S5_pre_menos_pre_extra | 587 / 603 | +0,148 | [−0,426; +0,722] | 0,613 |
| F3.P2 | U | 0,400 | S5_dird_pre_extra | 587 / 603 | −0,281 | [−1,160; +0,598] | 0,531 |
| F3.P2 | U | empilhado | S5_pre_menos_pre_extra | 1446 / 1257 | −0,140 | [−0,665; +0,386] | 0,603 |
| F3.P2 | U | empilhado | S5_dird_pre_extra | 1446 / 1257 | −0,199 | [−0,890; +0,492] | 0,573 |
| S6 | U | 0,300 | S5_pre_menos_pre_extra | 859 / 654 | +0,033 | [−0,040; +0,105] | 0,377 |
| S6 | U | 0,300 | S5_dird_pre_extra | 859 / 654 | +0,056 | [−0,057; +0,169] | 0,331 |
| S6 | U | 0,400 | S5_pre_menos_pre_extra | 587 / 603 | −0,028 | [−0,073; +0,018] | 0,231 |
| S6 | U | 0,400 | S5_dird_pre_extra | 587 / 603 | −0,032 | [−0,092; +0,028] | 0,300 |
| S6 | U | empilhado | S5_pre_menos_pre_extra | 1446 / 1257 | +0,006 | [−0,039; +0,052] | 0,787 |
| S6 | U | empilhado | S5_dird_pre_extra | 1446 / 1257 | +0,018 | [−0,051; +0,087] | 0,617 |
<!-- E7:s5:fim -->

## 9. Estudo de evento

Salto da RDD de (Y_t − Y_2025-06) em cada competência. Resumo por janela:

<!-- E7:evento:inicio -->
| Outcome | População | Corte | Janela | Competências estimadas | p < 0,05 | maior abs(salto) | salto médio |
|---|---|---|---|---|---|---|---|
| F3.1 | U | 0,300 | pre_extra | 7 | 0 | 0,551 | +0,455 |
| F3.1 | U | 0,300 | entre_pre_extra_e_pre | 5 | 0 | 0,577 | +0,477 |
| F3.1 | U | 0,300 | pre | 12 | 0 | 0,236 | +0,129 |
| F3.1 | U | 0,300 | transicao | 3 | 0 | 0,241 | +0,200 |
| F3.1 | U | 0,300 | pos | 11 | 5 | 0,609 | +0,406 |
| F3.1 | U | 0,400 | pre_extra | 7 | 0 | 0,171 | −0,032 |
| F3.1 | U | 0,400 | entre_pre_extra_e_pre | 5 | 0 | 0,317 | −0,154 |
| F3.1 | U | 0,400 | pre | 12 | 0 | 0,230 | −0,099 |
| F3.1 | U | 0,400 | transicao | 3 | 0 | 0,238 | −0,143 |
| F3.1 | U | 0,400 | pos | 11 | 0 | 0,657 | −0,270 |
| F3.1 | U | empilhado | pre_extra | 7 | 0 | 0,333 | +0,241 |
| F3.1 | U | empilhado | entre_pre_extra_e_pre | 5 | 0 | 0,279 | +0,201 |
| F3.1 | U | empilhado | pre | 12 | 0 | 0,126 | +0,029 |
| F3.1 | U | empilhado | transicao | 3 | 0 | 0,068 | +0,050 |
| F3.1 | U | empilhado | pos | 11 | 1 | 0,331 | +0,110 |
| F3.1 | V1 | 0,300 | pre_extra | 7 | 7 | 5,623 | +5,371 |
| F3.1 | V1 | 0,300 | entre_pre_extra_e_pre | 5 | 5 | 4,851 | +3,524 |
| F3.1 | V1 | 0,300 | pre | 12 | 1 | 2,458 | +1,411 |
| F3.1 | V1 | 0,300 | transicao | 3 | 0 | 1,913 | −0,987 |
| F3.1 | V1 | 0,300 | pos | 11 | 0 | 0,667 | −0,297 |
| F3.1 | V1 | 0,400 | pre_extra | 7 | 0 | 1,669 | −1,308 |
| F3.1 | V1 | 0,400 | entre_pre_extra_e_pre | 5 | 0 | 1,450 | −1,194 |
| F3.1 | V1 | 0,400 | pre | 12 | 1 | 1,618 | −0,841 |
| F3.1 | V1 | 0,400 | transicao | 3 | 0 | 1,394 | −0,658 |
| F3.1 | V1 | 0,400 | pos | 11 | 0 | 3,473 | −1,709 |
| F3.1 | V1 | empilhado | pre_extra | 7 | 0 | 2,109 | +1,711 |
| F3.1 | V1 | empilhado | entre_pre_extra_e_pre | 5 | 0 | 1,434 | +0,939 |
| F3.1 | V1 | empilhado | pre | 12 | 0 | 0,562 | +0,177 |
| F3.1 | V1 | empilhado | transicao | 3 | 2 | 1,629 | −0,806 |
| F3.1 | V1 | empilhado | pos | 11 | 0 | 1,992 | −1,071 |
| F3.2 | U | 0,300 | pre_extra | 7 | 1 | 6,3 | −5,1 |
| F3.2 | U | 0,300 | entre_pre_extra_e_pre | 5 | 0 | 5,7 | −2,8 |
| F3.2 | U | 0,300 | pre | 12 | 0 | 1,9 | −0,8 |
| F3.2 | U | 0,300 | transicao | 3 | 0 | 1,0 | −0,9 |
| F3.2 | U | 0,300 | pos | 11 | 0 | 2,7 | −1,5 |
| F3.2 | U | 0,400 | pre_extra | 7 | 0 | 7,1 | +4,8 |
| F3.2 | U | 0,400 | entre_pre_extra_e_pre | 5 | 0 | 4,3 | +3,4 |
| F3.2 | U | 0,400 | pre | 12 | 3 | 7,1 | +3,7 |
| F3.2 | U | 0,400 | transicao | 3 | 0 | 2,9 | −0,9 |
| F3.2 | U | 0,400 | pos | 11 | 0 | 3,1 | −1,3 |
| F3.2 | U | empilhado | pre_extra | 7 | 0 | 2,2 | −0,8 |
| F3.2 | U | empilhado | entre_pre_extra_e_pre | 5 | 0 | 1,6 | −0,0 |
| F3.2 | U | empilhado | pre | 12 | 0 | 2,6 | +1,1 |
| F3.2 | U | empilhado | transicao | 3 | 0 | 1,6 | −0,9 |
| F3.2 | U | empilhado | pos | 11 | 0 | 2,7 | −1,4 |
| F3.3 | U | 0,300 | pre_extra | 7 | 0 | 5,9 | −5,0 |
| F3.3 | U | 0,300 | entre_pre_extra_e_pre | 5 | 0 | 5,2 | −1,3 |
| F3.3 | U | 0,300 | pre | 12 | 0 | 3,3 | −1,8 |
| F3.3 | U | 0,300 | transicao | 3 | 0 | 0,9 | +0,8 |
| F3.3 | U | 0,300 | pos | 11 | 0 | 3,6 | −0,5 |
| F3.3 | U | 0,400 | pre_extra | 7 | 0 | 1,6 | +0,3 |
| F3.3 | U | 0,400 | entre_pre_extra_e_pre | 5 | 0 | 3,0 | +1,1 |
| F3.3 | U | 0,400 | pre | 12 | 0 | 2,1 | +0,1 |
| F3.3 | U | 0,400 | transicao | 3 | 2 | 3,8 | −2,7 |
| F3.3 | U | 0,400 | pos | 11 | 1 | 9,4 | −6,0 |
| F3.3 | U | empilhado | pre_extra | 7 | 0 | 3,8 | −2,7 |
| F3.3 | U | empilhado | entre_pre_extra_e_pre | 5 | 0 | 3,4 | −0,3 |
| F3.3 | U | empilhado | pre | 12 | 0 | 1,8 | −1,0 |
| F3.3 | U | empilhado | transicao | 3 | 0 | 1,1 | −0,7 |
| F3.3 | U | empilhado | pos | 11 | 1 | 6,0 | −2,9 |
| F3.3.sem_filtro_sus | U | 0,300 | pre_extra | 7 | 0 | 4,8 | −3,7 |
| F3.3.sem_filtro_sus | U | 0,300 | entre_pre_extra_e_pre | 5 | 0 | 4,6 | −0,6 |
| F3.3.sem_filtro_sus | U | 0,300 | pre | 12 | 0 | 2,8 | −1,4 |
| F3.3.sem_filtro_sus | U | 0,300 | transicao | 3 | 0 | 0,7 | +0,5 |
| F3.3.sem_filtro_sus | U | 0,300 | pos | 11 | 0 | 3,3 | −0,3 |
| F3.3.sem_filtro_sus | U | 0,400 | pre_extra | 7 | 0 | 3,6 | −2,4 |
| F3.3.sem_filtro_sus | U | 0,400 | entre_pre_extra_e_pre | 5 | 0 | 3,6 | −1,4 |
| F3.3.sem_filtro_sus | U | 0,400 | pre | 12 | 0 | 2,7 | −1,3 |
| F3.3.sem_filtro_sus | U | 0,400 | transicao | 3 | 2 | 4,2 | −2,9 |
| F3.3.sem_filtro_sus | U | 0,400 | pos | 11 | 1 | 9,5 | −6,1 |
| F3.3.sem_filtro_sus | U | empilhado | pre_extra | 7 | 0 | 4,3 | −3,1 |
| F3.3.sem_filtro_sus | U | empilhado | entre_pre_extra_e_pre | 5 | 0 | 4,2 | −0,9 |
| F3.3.sem_filtro_sus | U | empilhado | pre | 12 | 0 | 2,4 | −1,3 |
| F3.3.sem_filtro_sus | U | empilhado | transicao | 3 | 0 | 1,7 | −1,0 |
| F3.3.sem_filtro_sus | U | empilhado | pos | 11 | 1 | 6,0 | −2,8 |
| F3.3.soma_parcial | U | 0,300 | pre_extra | 7 | 0 | 5,9 | −5,0 |
| F3.3.soma_parcial | U | 0,300 | entre_pre_extra_e_pre | 5 | 0 | 5,2 | −1,3 |
| F3.3.soma_parcial | U | 0,300 | pre | 12 | 0 | 3,3 | −1,7 |
| F3.3.soma_parcial | U | 0,300 | transicao | 3 | 0 | 0,9 | +0,8 |
| F3.3.soma_parcial | U | 0,300 | pos | 11 | 0 | 3,6 | −0,5 |
| F3.3.soma_parcial | U | 0,400 | pre_extra | 7 | 0 | 1,6 | +0,3 |
| F3.3.soma_parcial | U | 0,400 | entre_pre_extra_e_pre | 5 | 0 | 3,0 | +1,1 |
| F3.3.soma_parcial | U | 0,400 | pre | 12 | 0 | 2,1 | +0,1 |
| F3.3.soma_parcial | U | 0,400 | transicao | 3 | 2 | 3,8 | −2,7 |
| F3.3.soma_parcial | U | 0,400 | pos | 11 | 1 | 9,4 | −6,0 |
| F3.3.soma_parcial | U | empilhado | pre_extra | 7 | 0 | 3,8 | −2,7 |
| F3.3.soma_parcial | U | empilhado | entre_pre_extra_e_pre | 5 | 0 | 3,4 | −0,3 |
| F3.3.soma_parcial | U | empilhado | pre | 12 | 0 | 1,8 | −0,9 |
| F3.3.soma_parcial | U | empilhado | transicao | 3 | 0 | 1,1 | −0,7 |
| F3.3.soma_parcial | U | empilhado | pos | 11 | 1 | 6,0 | −2,9 |
| F3.P1 | U | 0,300 | pre_extra | 7 | 0 | 1,014 | +0,550 |
| F3.P1 | U | 0,300 | entre_pre_extra_e_pre | 5 | 0 | 0,632 | +0,233 |
| F3.P1 | U | 0,300 | pre | 12 | 0 | 0,660 | −0,234 |
| F3.P1 | U | 0,300 | transicao | 3 | 0 | 0,566 | −0,498 |
| F3.P1 | U | 0,300 | pos | 11 | 0 | 0,949 | −0,287 |
| F3.P1 | U | 0,400 | pre_extra | 7 | 2 | 1,542 | +1,136 |
| F3.P1 | U | 0,400 | entre_pre_extra_e_pre | 5 | 0 | 1,026 | +0,626 |
| F3.P1 | U | 0,400 | pre | 12 | 0 | 0,471 | +0,193 |
| F3.P1 | U | 0,400 | transicao | 3 | 0 | 0,427 | −0,006 |
| F3.P1 | U | 0,400 | pos | 11 | 0 | 0,620 | +0,067 |
| F3.P1 | U | empilhado | pre_extra | 7 | 0 | 0,989 | +0,807 |
| F3.P1 | U | empilhado | entre_pre_extra_e_pre | 5 | 0 | 0,736 | +0,405 |
| F3.P1 | U | empilhado | pre | 12 | 0 | 0,418 | −0,047 |
| F3.P1 | U | empilhado | transicao | 3 | 0 | 0,505 | −0,283 |
| F3.P1 | U | empilhado | pos | 11 | 0 | 0,359 | −0,132 |
| F3.P2 | U | 0,300 | pre_extra | 7 | 0 | 0,857 | +0,440 |
| F3.P2 | U | 0,300 | entre_pre_extra_e_pre | 5 | 0 | 0,286 | +0,225 |
| F3.P2 | U | 0,300 | pre | 12 | 0 | 0,277 | +0,082 |
| F3.P2 | U | 0,300 | transicao | 3 | 0 | 0,027 | −0,011 |
| F3.P2 | U | 0,300 | pos | 11 | 0 | 0,426 | +0,305 |
| F3.P2 | U | 0,400 | pre_extra | 7 | 0 | 0,243 | +0,025 |
| F3.P2 | U | 0,400 | entre_pre_extra_e_pre | 5 | 0 | 0,143 | +0,046 |
| F3.P2 | U | 0,400 | pre | 12 | 0 | 0,292 | +0,188 |
| F3.P2 | U | 0,400 | transicao | 3 | 0 | 0,155 | −0,066 |
| F3.P2 | U | 0,400 | pos | 11 | 0 | 0,550 | −0,256 |
| F3.P2 | U | empilhado | pre_extra | 7 | 0 | 0,449 | +0,258 |
| F3.P2 | U | empilhado | entre_pre_extra_e_pre | 5 | 0 | 0,181 | +0,147 |
| F3.P2 | U | empilhado | pre | 12 | 1 | 0,268 | +0,128 |
| F3.P2 | U | empilhado | transicao | 3 | 0 | 0,073 | −0,035 |
| F3.P2 | U | empilhado | pos | 11 | 0 | 0,214 | +0,059 |
| S6 | U | 0,300 | pre_extra | 7 | 0 | 0,032 | +0,008 |
| S6 | U | 0,300 | entre_pre_extra_e_pre | 5 | 1 | 0,074 | +0,050 |
| S6 | U | 0,300 | pre | 12 | 2 | 0,071 | +0,044 |
| S6 | U | 0,300 | transicao | 3 | 0 | 0,062 | +0,043 |
| S6 | U | 0,300 | pos | 11 | 0 | 0,079 | +0,064 |
| S6 | U | 0,400 | pre_extra | 7 | 0 | 0,064 | +0,047 |
| S6 | U | 0,400 | entre_pre_extra_e_pre | 5 | 0 | 0,044 | +0,030 |
| S6 | U | 0,400 | pre | 12 | 0 | 0,036 | +0,021 |
| S6 | U | 0,400 | transicao | 3 | 0 | 0,035 | +0,024 |
| S6 | U | 0,400 | pos | 11 | 0 | 0,030 | +0,015 |
| S6 | U | empilhado | pre_extra | 7 | 0 | 0,040 | +0,025 |
| S6 | U | empilhado | entre_pre_extra_e_pre | 5 | 1 | 0,054 | +0,041 |
| S6 | U | empilhado | pre | 12 | 1 | 0,052 | +0,034 |
| S6 | U | empilhado | transicao | 3 | 0 | 0,050 | +0,035 |
| S6 | U | empilhado | pos | 11 | 0 | 0,053 | +0,043 |
<!-- E7:evento:fim -->

Figuras: `output/rdd_bolsa/E7_figuras/E7_evento_<outcome>_<população>.png`,
com as datas da Portaria 752/2023, da Portaria 3.493/2024 (parcela de
05/2024), do quadro e do início do ciclo 1 e do edital e início do ciclo 2
(tracejado), e das demais regras da auditoria 18 (pontilhado).

## 10. Heterogeneidade pelas co-políticas (S3 e S4)

S3: portes em que o estrato do IED muda no corte contra os em que não muda
(Anexo VI da Portaria 3.493/2024). S4 (só 0,400): dentro contra fora da
Amazônia Legal ou faixa de fronteira, onde a ajuda de custo do PMMB não salta.

<!-- E7:s3_s4:inicio -->
| Outcome | População | Corte | Especificação | n abaixo / acima | Salto | IC 95% | p |
|---|---|---|---|---|---|---|---|
| F3.1 | U | 0,300 | S3_porte_muda | 185 / 109 | −0,415 | [−1,502; +0,672] | 0,455 |
| F3.1 | U | 0,300 | S3_porte_nao_muda | 674 / 545 | +0,448 | [−0,142; +1,038] | 0,137 |
| F3.1 | U | 0,300 | S3_diferenca | 859 / 654 | −0,863 | [−2,100; +0,374] | 0,172 |
| F3.1 | U | 0,400 | S3_porte_muda | 551 / 567 | −0,123 | [−0,741; +0,495] | 0,697 |
| F3.1 | U | 0,400 | S3_porte_nao_muda | 36 / 36 | −1,069 | [−2,964; +0,826] | 0,269 |
| F3.1 | U | 0,400 | S3_diferenca | 587 / 603 | +0,946 | [−1,048; +2,940] | 0,352 |
| F3.1 | U | 0,400 | S4_dentro | 135 / 87 | +0,324 | [−0,737; +1,385] | 0,549 |
| F3.1 | U | 0,400 | S4_fora | 452 / 516 | −0,318 | [−1,008; +0,372] | 0,366 |
| F3.1 | U | 0,400 | S4_diferenca | 587 / 603 | +0,642 | [−0,623; +1,908] | 0,320 |
| F3.1 | V1 | 0,300 | S3_porte_muda | 29 / 23 | +0,011 | [−2,393; +2,414] | 0,993 |
| F3.1 | V1 | 0,300 | S3_porte_nao_muda | 32 / 30 | −2,416 | [−5,545; +0,713] | 0,130 |
| F3.1 | V1 | 0,300 | S3_diferenca | 61 / 53 | +2,427 | [−1,519; +6,372] | 0,228 |
| F3.1 | V1 | 0,400 | S3_porte_muda | 38 / 30 | −0,317 | [−3,642; +3,007] | 0,852 |
| F3.1 | V1 | 0,400 | S3_porte_nao_muda | 15 / 11 | −2,541 | [−5,912; +0,830] | 0,140 |
| F3.1 | V1 | 0,400 | S3_diferenca | 53 / 41 | +2,224 | [−2,511; +6,958] | 0,357 |
| F3.1 | V1 | 0,400 | S4_dentro | 17 / 11 | +1,322 | [−1,434; +4,079] | 0,347 |
| F3.1 | V1 | 0,400 | S4_fora | 36 / 30 | −1,675 | [−4,935; +1,585] | 0,314 |
| F3.1 | V1 | 0,400 | S4_diferenca | 53 / 41 | +2,997 | [−1,272; +7,266] | 0,169 |
| F3.2 | U | 0,300 | S3_porte_muda | 185 / 109 | −0,1 p.p. | [−0,3; +0,1] | 0,357 |
| F3.2 | U | 0,300 | S3_porte_nao_muda | 674 / 545 | −0,8 p.p. | [−5,5; +3,9] | 0,728 |
| F3.2 | U | 0,300 | S3_diferenca | 859 / 654 | +0,8 p.p. | [−3,9; +5,5] | 0,753 |
| F3.2 | U | 0,400 | S3_porte_muda | 551 / 567 | −5,1 p.p. | [−11,7; +1,5] | 0,132 |
| F3.2 | U | 0,400 | S3_porte_nao_muda | 36 / 36 | +0,0 p.p. | [+0,0; +0,0] | — |
| F3.2 | U | 0,400 | S3_diferenca | 587 / 603 | −5,1 p.p. | [−11,7; +1,5] | 0,132 |
| F3.2 | U | 0,400 | S4_dentro | 135 / 87 | −4,5 p.p. | [−18,3; +9,3] | 0,525 |
| F3.2 | U | 0,400 | S4_fora | 452 / 516 | −4,9 p.p. | [−11,7; +2,0] | 0,166 |
| F3.2 | U | 0,400 | S4_diferenca | 587 / 603 | +0,4 p.p. | [−15,0; +15,8] | 0,960 |
| F3.3 | U | 0,300 | S3_porte_muda | 185 / 109 | −10,0 | [−21,9; +2,0] | 0,103 |
| F3.3 | U | 0,300 | S3_porte_nao_muda | 671 / 545 | +3,8 | [−1,6; +9,2] | 0,173 |
| F3.3 | U | 0,300 | S3_diferenca | 856 / 654 | −13,7 | [−26,9; −0,6] | 0,041 |
| F3.3 | U | 0,400 | S3_porte_muda | 551 / 567 | −5,7 | [−13,5; +2,2] | 0,156 |
| F3.3 | U | 0,400 | S3_porte_nao_muda | 36 / 36 | −10,7 | [−37,9; +16,5] | 0,440 |
| F3.3 | U | 0,400 | S3_diferenca | 587 / 603 | +5,0 | [−23,3; +33,3] | 0,728 |
| F3.3 | U | 0,400 | S4_dentro | 135 / 87 | +3,6 | [−17,8; +25,1] | 0,740 |
| F3.3 | U | 0,400 | S4_fora | 452 / 516 | −7,8 | [−16,3; +0,6] | 0,070 |
| F3.3 | U | 0,400 | S4_diferenca | 587 / 603 | +11,5 | [−11,6; +34,6] | 0,330 |
| F3.3.sem_filtro_sus | U | 0,300 | S3_porte_muda | 185 / 109 | −8,5 | [−19,9; +2,9] | 0,145 |
| F3.3.sem_filtro_sus | U | 0,300 | S3_porte_nao_muda | 671 / 545 | +3,1 | [−2,3; +8,6] | 0,260 |
| F3.3.sem_filtro_sus | U | 0,300 | S3_diferenca | 856 / 654 | −11,6 | [−24,3; +1,0] | 0,072 |
| F3.3.sem_filtro_sus | U | 0,400 | S3_porte_muda | 551 / 567 | −4,3 | [−12,4; +3,7] | 0,290 |
| F3.3.sem_filtro_sus | U | 0,400 | S3_porte_nao_muda | 36 / 36 | −11,9 | [−39,2; +15,4] | 0,394 |
| F3.3.sem_filtro_sus | U | 0,400 | S3_diferenca | 587 / 603 | +7,6 | [−20,9; +36,1] | 0,603 |
| F3.3.sem_filtro_sus | U | 0,400 | S4_dentro | 135 / 87 | +5,8 | [−16,6; +28,3] | 0,611 |
| F3.3.sem_filtro_sus | U | 0,400 | S4_fora | 452 / 516 | −6,7 | [−15,3; +1,9] | 0,127 |
| F3.3.sem_filtro_sus | U | 0,400 | S4_diferenca | 587 / 603 | +12,5 | [−11,5; +36,6] | 0,308 |
| F3.3.soma_parcial | U | 0,300 | S3_porte_muda | 185 / 109 | −10,0 | [−21,9; +2,0] | 0,103 |
| F3.3.soma_parcial | U | 0,300 | S3_porte_nao_muda | 674 / 545 | +3,7 | [−1,7; +9,1] | 0,177 |
| F3.3.soma_parcial | U | 0,300 | S3_diferenca | 859 / 654 | −13,7 | [−26,8; −0,5] | 0,041 |
| F3.3.soma_parcial | U | 0,400 | S3_porte_muda | 551 / 567 | −5,7 | [−13,5; +2,2] | 0,156 |
| F3.3.soma_parcial | U | 0,400 | S3_porte_nao_muda | 36 / 36 | −10,7 | [−37,9; +16,5] | 0,440 |
| F3.3.soma_parcial | U | 0,400 | S3_diferenca | 587 / 603 | +5,0 | [−23,3; +33,3] | 0,728 |
| F3.3.soma_parcial | U | 0,400 | S4_dentro | 135 / 87 | +3,6 | [−17,8; +25,1] | 0,740 |
| F3.3.soma_parcial | U | 0,400 | S4_fora | 452 / 516 | −7,8 | [−16,3; +0,6] | 0,070 |
| F3.3.soma_parcial | U | 0,400 | S4_diferenca | 587 / 603 | +11,5 | [−11,6; +34,6] | 0,330 |
| F3.P1 | U | 0,300 | S3_porte_muda | 185 / 109 | −0,139 | [−2,303; +2,024] | 0,899 |
| F3.P1 | U | 0,300 | S3_porte_nao_muda | 674 / 545 | −0,042 | [−2,229; +2,144] | 0,970 |
| F3.P1 | U | 0,300 | S3_diferenca | 859 / 654 | −0,097 | [−3,173; +2,979] | 0,951 |
| F3.P1 | U | 0,400 | S3_porte_muda | 551 / 567 | −0,064 | [−1,038; +0,910] | 0,898 |
| F3.P1 | U | 0,400 | S3_porte_nao_muda | 36 / 36 | −1,146 | [−3,425; +1,134] | 0,325 |
| F3.P1 | U | 0,400 | S3_diferenca | 587 / 603 | +1,082 | [−1,397; +3,561] | 0,392 |
| F3.P1 | U | 0,400 | S4_dentro | 135 / 87 | +0,360 | [−2,415; +3,136] | 0,799 |
| F3.P1 | U | 0,400 | S4_fora | 452 / 516 | −0,166 | [−1,167; +0,835] | 0,746 |
| F3.P1 | U | 0,400 | S4_diferenca | 587 / 603 | +0,526 | [−2,424; +3,476] | 0,727 |
| F3.P2 | U | 0,300 | S3_porte_muda | 185 / 109 | −0,082 | [−1,112; +0,949] | 0,877 |
| F3.P2 | U | 0,300 | S3_porte_nao_muda | 674 / 545 | +0,298 | [−0,383; +0,979] | 0,391 |
| F3.P2 | U | 0,300 | S3_diferenca | 859 / 654 | −0,380 | [−1,615; +0,856] | 0,547 |
| F3.P2 | U | 0,400 | S3_porte_muda | 551 / 567 | −0,282 | [−0,923; +0,358] | 0,388 |
| F3.P2 | U | 0,400 | S3_porte_nao_muda | 36 / 36 | −2,661 | [−4,687; −0,636] | 0,010 |
| F3.P2 | U | 0,400 | S3_diferenca | 587 / 603 | +2,379 | [+0,254; +4,503] | 0,028 |
| F3.P2 | U | 0,400 | S4_dentro | 135 / 87 | −0,240 | [−1,218; +0,737] | 0,630 |
| F3.P2 | U | 0,400 | S4_fora | 452 / 516 | −0,509 | [−1,235; +0,217] | 0,170 |
| F3.P2 | U | 0,400 | S4_diferenca | 587 / 603 | +0,268 | [−0,949; +1,486] | 0,666 |
| S6 | U | 0,300 | S3_porte_muda | 185 / 109 | +0,038 | [−0,042; +0,119] | 0,350 |
| S6 | U | 0,300 | S3_porte_nao_muda | 674 / 545 | +0,020 | [−0,101; +0,141] | 0,751 |
| S6 | U | 0,300 | S3_diferenca | 859 / 654 | +0,019 | [−0,127; +0,164] | 0,800 |
| S6 | U | 0,400 | S3_porte_muda | 551 / 567 | −0,000 | [−0,048; +0,048] | 0,995 |
| S6 | U | 0,400 | S3_porte_nao_muda | 36 / 36 | −0,067 | [−0,201; +0,068] | 0,331 |
| S6 | U | 0,400 | S3_diferenca | 587 / 603 | +0,067 | [−0,076; +0,210] | 0,361 |
| S6 | U | 0,400 | S4_dentro | 135 / 87 | +0,150 | [−0,048; +0,348] | 0,138 |
| S6 | U | 0,400 | S4_fora | 452 / 516 | −0,030 | [−0,074; +0,014] | 0,184 |
| S6 | U | 0,400 | S4_diferenca | 587 / 603 | +0,180 | [−0,023; +0,383] | 0,082 |
<!-- E7:s3_s4:fim -->

## 11. Leitura

Leitura escrita depois da execução de 19/10/2026. Ela não reescolhe nada. Os
números dos blocos `E7:leitura_*` são gerados das saídas, como as tabelas.

**1. P2 não detecta efeito.** A DiRD de F3.1 em U, cortes empilhados, tem IC
95% que inclui zero. Nenhuma linha principal da família F3 tem p < 0,05, em U
ou em V1, e todos os q BKY ficam no máximo da grade. É um nulo, não evidência
de efeito zero.

<!-- E7:leitura_p2:inicio -->
P2: salto +0,083, IC 95% CR1 [−0,309; +0,476], p = 0,677. Só sob a hipótese da DiRD (as outras descontinuidades não mudam entre pré e pós) e sem viés de suavidade, o maior aumento que esse IC admite é +0,476 vínculo por 10 mil hab., ou 4,4 % da média bruta do pré abaixo do corte 0,300 na janela (10,711); 8,0 % da média bruta do pré abaixo do corte 0,400 na janela (5,941).
<!-- E7:leitura_p2:fim -->

**2. O IC honesto não informa.** Com o suporte da quártica até o ponto médio
entre cortes, o lado interno de cada corte tem só meia distância entre cortes
de IVS, e o M da regra de bolso explode (coluna M). O mesmo aconteceu no E6.
Nenhuma especificação pós-resultado foi acrescentada aqui.

**3. Placebo de generalistas (F3.P1) e S6.** A DiRD principal, o placebo dentro
do pré e o S5 de generalistas não têm p < 0,05 em U. Mas o estudo de evento em
0,400 mostra deriva antes do pré principal:

<!-- E7:leitura_generalistas:inicio -->
Em 0,400, o salto de generalistas relativo a 2025-06 é +1,542 (p = 0,045) em 2022-01 (2 meses do pré extra com p < 0,05) e cai no pré principal (média +0,193; −0,221 em 2025-05), atravessando a data da Portaria 752 (2023-06). O S5 (pré menos pré extra) de generalistas em 0,400 é −0,958 (p = 0,061). Isso é compatível com uma co-política variável no tempo em 0,400, antes do pré principal. A DiRD principal de generalistas em 0,400 é −0,111 (p = 0,816).
<!-- E7:leitura_generalistas:fim -->

Ou seja, o placebo não detecta co-política variável no tempo entre o pré
principal e o pós, mas o perfil anterior não é plano em 0,400. Ele também não
exclui o canal da MAC em 0,300, que mira especialistas.

**4. Estudo de evento de F3.1 em U.**

<!-- E7:leitura_evento_f31:inicio -->
Em 0,300 (U, F3.1), os 5 meses consecutivos de 2025-10 a 2026-02 têm p < 0,05 (saltos de +0,346 a +0,609; maior p 0,040), logo depois do início do ciclo 1 (2025-09). De 2026-03 a 2026-08 os saltos ficam entre +0,220 e +0,465; meses com p < 0,05: 0. Ressalva: os saltos são relativos a 2025-06, que está num vale. O salto é +0,577 em 2024-01 e cai até +0,075 em 2025-05; no pré extra a média é +0,455. Meses anteriores a 2025-06 com p < 0,05: 0. A DiRD principal, com a média do pré inteiro, é +0,287 (p = 0,281).
<!-- E7:leitura_evento_f31:fim -->

A sequência significativa começa logo depois do início do ciclo 1 e se
desfaz. Como a referência está num vale e o salto do pré extra tem tamanho
parecido com o do pós, a DiRD com o pré inteiro não detecta salto. Em 0,400 o
salto deriva para baixo no pós, sem significância.

**5. Placebo dentro do pré e S5 em U.** Nenhuma linha, de nenhum outcome, tem
p < 0,05. Para F3.1 não se detecta mudança da descontinuidade entre 2022–2023
e o pré principal, mas há a deriva dentro dos prés descrita no item 4.

<!-- E7:leitura_s5:inicio -->
S5 de F3.1 em U (média do pré menos média do pré extra): 0,300: −0,336 (p = 0,372); 0,400: −0,059 (p = 0,850); empilhado: −0,215 (p = 0,394).
<!-- E7:leitura_s5:fim -->

**6. V1 tem tendência pré.** Em 0,300, o placebo dentro do pré e o S5 (pré menos
pré extra) saem de zero, e no estudo de evento todos os meses do pré extra e
do trecho seguinte ficam acima da referência. A descontinuidade de F3.1 em V1
já caía antes do PMM-E, e a DiRD em V1 nesse corte não é crível. V1 é
condicionada a ter vaga no ciclo 1, e ter vaga pode depender do corte e da
trajetória (protocolo §3).

**7. Pacote em nível.** Em U, F3.1 tem salto negativo em nível em 0,300 no pré
extra e no pré principal, ambos com IC que exclui zero. Havia uma
descontinuidade de oferta antes de 2023-03, anterior a todas as regras com
corte em 0,3 ou 0,4 encontradas pela auditoria 18. Ela é a razão para não ler
a RDD em nível como efeito da bolsa.

**8. Horas (F3.3, §16).** A soma parcial quase não muda o salto. Sem o filtro
SUS o salto muda de magnitude, mas não de sinal nem de significância (tabela
principal):

<!-- E7:leitura_horas:inicio -->
Salto principal das sensibilidades de horas contra o F3.3 só SUS (diferença relativa ao valor absoluto do principal): 0,300, sem filtro SUS: +0,95 contra +1,15 (−17,1 %); 0,300, soma parcial: +1,12 contra +1,15 (−2,6 %); 0,400, sem filtro SUS: −4,86 contra −6,11 (+20,5 %); 0,400, soma parcial: −6,11 contra −6,11 (+0,0 %); empilhado, sem filtro SUS: −1,60 contra −2,04 (+21,5 %); empilhado, soma parcial: −2,05 contra −2,04 (−0,7 %).
<!-- E7:leitura_horas:fim -->

Em 0,400 os pontos de F3.3 e F3.2 são negativos, sem significância. F3.2 tem
meses do pré principal fora de zero no estudo de evento, sinal de
instabilidade antes do PMM-E.

**9. Suplementares S3 e S4** (fora do BKY, muitos testes): duas diferenças
saem de zero isoladamente. A primeira é F3.3 em 0,300 (portes onde o estrato
do IED muda contra os demais); a soma parcial de horas repete essa diferença,
e a versão sem filtro SUS não. A segunda é F3.P2 em 0,400, no porte sem
mudança de estrato, que tem poucos municípios. Com o número de comparações
suplementares, elas não sustentam um canal.

<!-- E7:leitura_s3_nulo:inicio -->
Subamostras do S3/S4 com EP nulo (Δ igual em todos os municípios da janela, sem variação residual): F3.2 0,400 S3_porte_nao_muda (36 / 36 municípios). Nesses casos a linha S3_diferenca correspondente usa só a variância da outra subamostra.
<!-- E7:leitura_s3_nulo:fim -->

**10. Local randomization** em U no corte 0,300 não foi estimada: nenhuma
janela passou no balanço de covariáveis (regra do E5). Nos demais casos, ela
também não detecta salto.

**11. Pré extra.**

<!-- E7:leitura_pre_extra:inicio -->
O pré extra usa as 7 competências disponíveis de 2022-01 a 2023-03 (2022-01, 2022-04, 2022-07, 2022-10, 2023-01, 2023-02, 2023-03). 3 delas são do 1º trimestre de 2023, porque 2023-02 e 2023-03 entraram pelo adendo §13; a média simples do pré extra dá mais peso a esse trimestre do que aos de 2022, que têm uma competência cada.
<!-- E7:leitura_pre_extra:fim -->

**Contraste.** Em U, a DiRD mede a bolsa mais a variação, entre pré e pós, das
descontinuidades das outras políticas. Ela não detecta mudança na oferta
cadastrada de especialistas nas CBO-alvo, nem nos placebos. Isso não é
evidência de que a bolsa não atrai especialistas do PMM-E (F1 e F2, no E6):
vínculo no CNES não é médico do PMM-E (§12).

## 12. Limites

- **Vínculo no CNES não é médico do PMM-E.** O grupo `alvo_pmme` conta todos os
  vínculos nas CBO-alvo, de qualquer programa ou contratação. O E7 mede oferta
  cadastrada local, não a presença do especialista do PMM-E (isso é F2, no E6).
- **Ponte curso–CBO operacional.** As CBO-alvo vêm da ponte
  `ponte_curso_cbo_oficial.json`, que não é crosswalk oficial; cursos diferentes
  compartilham CBO, e especialistas fora do PMM-E nas mesmas CBO entram no
  outcome.
- **Vínculo não é retenção.** O painel conta vínculos e profissionais distintos
  por município e mês; não segue a pessoa. Quem atua em dois municípios conta
  nos dois. Persistência de oferta não equivale a retenção individual.
- **Cadastro não é atendimento:** vínculo e carga horária são declarados.
- **Co-políticas variáveis no tempo** (§1) ameaçam a DiRD nos dois cortes; o
  canal da MAC em 0,300 não tem outcome próprio aqui (auditoria 18, recomendação
  9).
- **Pós curto e acumulado:** o pós junta os ciclos 1 e 2 e termina em 2026-08.

## 13. Desvios e esclarecimentos

<!-- E7:desvios:inicio -->
| Data | Tipo | Item | Descrição |
|---|---|---|---|
| 2026-10-19 | desvio | Poisson local (protocolo §6, contagens por habitante) | nao estimado na F3. O estimando da DiRD e uma diferenca de medias de taxas por municipio; um analogo em log exigiria um modelo de painel (Poisson com efeito de periodo e interacao) que o protocolo nao especifica, e o coordenador o deixou opcional. Nada foi estimado e descartado. |
| 2026-10-19 | regra_de_dado | F3.3 horas (protocolo §16) | principal: horas_sus_semanais = horas ambulatoriais + hospitalares dos vinculos com TP_SUS_NAO_SUS = 'S'; celula com hora em branco fica ausente, nunca zero; o municipio sem todos os meses de uma janela sai daquele outcome naquela especificacao (diferenca_pos_pre com exigir_completo=True); no estudo de evento sai so dos meses afetados. Sensibilidades rotuladas (fora do BKY): F3.3.sem_filtro_sus (sem o filtro TP_SUS_NAO_SUS) e F3.3.soma_parcial (soma das horas observadas, com a contagem de vinculos em branco na nota e em validacoes.horas_ausentes). O grupo todos_medicos_sem_residentes do painel nao e outcome do E7 (§16: nao primario; F3 nao o lista). |
| 2026-10-19 | nota_de_nomenclatura | coluna da sensibilidade 'horas sem filtro SUS' (§16) | o texto do §16 diz que a soma sem o filtro TP_SUS_NAO_SUS 'continua no painel como horas_totais'; no painel auditado da tarefa C, horas_totais e a soma dos tres campos (ambulatorial + hospitalar + outros) e a soma ambulatorial + hospitalar sem filtro chama-se horas_totais_amb_hosp (definicao no manifesto a09). O E7 usa horas_totais_amb_hosp em F3.3.sem_filtro_sus. Mapeamento de nome, sem mudanca de substancia. |
| 2026-10-19 | esclarecimento | populacoes | protocolo §5: F3.1 em U e V1; F3.2, F3.3, F3.P1, F3.P2 e S6 em U. V1 = municipios do quadro do ciclo 1 (outcomes_V_municipio, ciclo 1). Nenhuma outra populacao foi estimada. |
| 2026-10-19 | esclarecimento | S5 | duas formas, ambas fixadas antes de estimar: (a) media(pre) - media(pre extra), teste de que a descontinuidade se moveu antes do PMM-E; (b) DiRD com pre extra (auditoria 18, recomendacao 7). O pre extra contem as Portarias 377/2022 e 1.054/2022 (IVS em indice composto; auditoria 18 §3.2). |
| 2026-10-19 | adicao | RDD em nivel e conferencia painel | nivel_pre, nivel_pos e nivel_pre_extra (pacote do corte) e dird_painel (identidade com o principal) sao adicoes rotuladas ESPECIFICACAO_ADICIONAL_AO_PROTOCOLO, pedidas antes de estimar. |
| 2026-10-19 | esclarecimento | datas do estudo de evento | datas do ciclo 2 do PMM-E vem da auditoria 01 §7 (cronologia auditada), nao da auditoria 18. Estudo de evento empilhado: rd_empilhado em cada competencia (CR1 por municipio). |
| 2026-10-19 | esclarecimento | S3 e S4 | porte = classe do Anexo VI da Portaria 3.493/2024 (a10), portes em que o estrato muda recalculados do a10 e conferidos com o protocolo §13; S4 = Amazonia Legal OU faixa de fronteira do PMMB consolidado (mesmo atributo e mesma regra do E6; areas indigenas sem atributo municipal no repositorio). So corte a corte (S3) e so 0,400 (S4). |
<!-- E7:desvios:fim -->

Nota de 19/10/2026, depois da primeira execução: a guarda de texto da tarefa E
(`tests/test_fonte_ivs_oficial.py`), integrada depois que o código do E7 foi
escrito, proíbe citar pelo nome o arquivo local de IVS da auditoria 16 em
qualquer script. O script do E7 tinha esse nome uma vez, só como rótulo do
campo `arquivo_proibido_nao_lido` do resumo, sem ler o arquivo. O rótulo foi
trocado por uma descrição sem o nome, e as frases da leitura (§11) passaram a
ser geradas das saídas. A pedido da auditoria independente, o script foi
reexecutado por inteiro. As estimativas e o estudo de evento saíram idênticos
byte a byte (conferido por SHA-256 antes do commit), e o resumo saiu sem o
nome antigo.

## 14. Proveniência e validações

<!-- E7:validacoes:inicio -->
| Conferência | Resultado |
|---|---|
| SHA-256 do painel = manifesto a09 | True |
| painel: chave única e balanceado no universo a08 | True / True |
| municípios no universo U / V1 | 5565 / 368 |
| U sem população 2022 | 0 |
| DiRD painel = DiRD delta (todas as combinações por corte) | True |
| seleção LR de V1 reproduz o E5 | True |
| seleção LR de U reproduz o E6 | True |
| definição de horas SUS no manifesto a09 contém TP_SUS_NAO_SUS (§16) | True |
| janelas LR (± IVS) | U|0.300: nenhuma; U|0.400: 0,008; V1|0.300: 0,020; V1|0.400: 0,007 |
| linhas em E7_estimativas.csv / no protocolo | 549 / 396 |
| linhas SEM_ESTIMATIVA / NAO_EXECUTADO | 0 / 8 |
| linhas em E7_estudo_evento.csv | 1053 |
<!-- E7:validacoes:fim -->

<!-- E7:entradas:inicio -->
| Entrada | SHA-256 | Papel |
|---|---|---|
| `output/aquisicao/cnes_nacional/painel_municipio_cbo_mes.parquet` | `08aec0e3b4b4fafa…` | painel CNES municipio x grupo de CBO x mes (F3) |
| `output/aquisicao/a09_manifesto_cnes_nacional.json` | `666d3283f36e323a…` | manifesto do painel (SHA-256, competencias) |
| `output/aquisicao/a08_ivs_2010_oficial_municipio.csv` | `0632a7a313e1179f…` | running variable (IVS 2010 oficial) e universo U |
| `output/aquisicao/populacao_censo2022_municipios.csv` | `b51fc6cf27a49fd5…` | denominador das taxas por 10 mil hab. |
| `output/rdd_bolsa/outcomes/outcomes_V_municipio.parquet` | `36ced6f6a4c41407…` | lista de municipios de V1 (quadro do ciclo 1) |
| `output/aquisicao/a10_ied_aps_2024_municipio.csv` | `2bd4aec48a14e610…` | S3: porte e estrato IED |
| `data/raw/aquisicao/ivs_administrativo/ppf_mais_medicos_csv.zip` | `15083f8127917e52…` | S4: Amazonia Legal / faixa de fronteira |
| `output/tema_trabalho/matriz_tipologia_territorial.parquet` | `10af8712eef95cc8…` | covariavel estrato da selecao da janela LR (regra do E5) |
| `output/rdd_bolsa/E5_lr_selecao_janela.csv` | `366d65f59a47921d…` | janela LR de V1 (E5, P1) para conferencia |
| `output/rdd_bolsa/E6_lr_selecao_janela.csv` | `aac0d0d9673d166f…` | janela LR de U (E6) para conferencia |
| `docs/06_execucao/40_protocolo_multioutcome_rdd_bolsa.md` | `85f11f309e033516…` | protocolo congelado (texto canonico) |
| `output/rdd_bolsa/protocolo_E6_multioutcome.json` | `a66fe6183562f8a2…` | protocolo congelado (maquina) |
| `docs/auditorias/18_politicas_nos_mesmos_cortes_ivs.md` | `9afe8cc10cc28edc…` | datas das politicas nos mesmos cortes (marcas do estudo de evento) |
| `docs/auditorias/01_regra_institucional.md` | `2c4f675c7b6608e8…` | datas dos ciclos 1 e 2 do PMM-E |
<!-- E7:entradas:fim -->

## 15. Reprodução

```bash
python3 scripts/rdd_bolsa/14_estimar_E7_dird_cnes.py --somente-validar   # esquema do painel, sem estimar
python3 scripts/rdd_bolsa/14_estimar_E7_dird_cnes.py                     # estimação, saídas e tabelas do doc
python3 -m unittest tests.test_e7_dird
```
