# 57g. Resultados da realocação: a bolsa das concorrentes desloca candidatos e preenchimento?

> **Gerado por** `scripts/rdd_bolsa/32_realocacao_bolsa.py` a partir de `output/rdd_bolsa/R_*`; não editar à mão (o teste `tests/test_realocacao_bolsa.py` confere que este arquivo é igual ao gerado).<br>
> **Protocolo:** [`58_protocolo_realocacao_bolsa.md`](58_protocolo_realocacao_bolsa.md), congelado em 24/10/2026 antes de abrir qualquer outcome por exposição; estatuto `EXPLORATORIO_REALOCACAO` (o E9, o P1 e o A3 já tinham sido vistos).<br>
> **Saídas:** `output/rdd_bolsa/R_estimativas.csv`, `R_variacao_exposicao.csv`, `R_resumo.json` e `R_figuras/`; toda linha tem `natureza_dos_dados = EMPIRICO`.

## 1. O que se mede e o que não se pode dizer

- **Pergunta.** A bolsa maior desloca médicos entre vagas do programa, em vez de preencher mais vagas no total? As células do mesmo curso e ciclo disputam os mesmos candidatos numa alocação centralizada por nota.
- **Estimando.** Quanto mudam o preenchimento e os candidatos de 1ª opção de uma célula quando a bolsa média das concorrentes do mesmo curso e ciclo na mesma região de saúde sobe, com a própria faixa, o IVS próprio e o IVS das concorrentes mantidos (spline contínua com nós em 0,300 e 0,400).
- **Fonte de variação.** Onde os municípios das concorrentes caem em relação a 0,300 e 0,400: a bolsa delas muda em degraus, e o IVS delas entra de forma contínua.
- **O que o contraste mede.** O pacote do corte das concorrentes (bolsa +R$ 5 mil e outras regras federais nos mesmos cortes, auditoria 18), condicional às vagas abertas. Não mede a participação no PMM-E, o efeito total do Agora Tem Especialistas nem a entrada de novos candidatos.
- **Por que importa para a RDD.** Se houver deslocamento, a RDD nos cortes, que compara vizinhos que disputam as mesmas pessoas, mede tratamento mais deslocamento (violação de SUTVA).

## 2. Amostra

<!-- R:amostra:inicio -->
| Item | Ciclo 1 | Ciclo 2 | Ciclo 3 | Total |
|---|---|---|---|---|
| células no quadro da 1ª chamada | 1.295 | 1.547 | 2.293 | 5.135 |
| fora do universo: município sem IVS 2010 oficial (a08); célula fora do universo e das concorrentes | 0 | 0 | 1 | 1 |
| fora do universo: município sem região de saúde na tabela oficial (TabNet); célula fora do universo e das concorrentes | 6 | 2 | 1 | 9 |
| fora da principal: sem concorrente do mesmo curso e ciclo no mercado | 873 | 762 | 615 | 2.250 |
| **amostra principal (CIR)** | 416 | 783 | 1.676 | 2.875 |

Na amostra principal há 227 regiões de saúde (clusters) e 754 municípios. As células sem covariável continuam como concorrentes das outras; só saem da estimação.

| Especificação | Descrição | Células | CIR | Fora (motivo: células) |
|---|---|---|---|---|
| PRINCIPAL | CIR, E, ciclos 1–3, cluster CIR, com covariáveis | 2.875 | 227 | sem concorrente do mesmo curso e ciclo no mercado: 2.250 |
| R1 | mercado = raio de 200 km (sensibilidade declarada) | 4.522 | 367 | sem concorrente do mesmo curso e ciclo no mercado: 603 |
| R2 | mercado = mesma UF | 4.844 | 373 | sem concorrente do mesmo curso e ciclo no mercado: 281 |
| R3 | exposição = fração das concorrentes com bolsa maior | 2.875 | 227 | sem concorrente do mesmo curso e ciclo no mercado: 2.250 |
| R4 | spline quadrática no IVS próprio e na média das concorrentes | 2.875 | 227 | sem concorrente do mesmo curso e ciclo no mercado: 2.250 |
| R5 | cluster por município | 2.875 | 227 | sem concorrente do mesmo curso e ciclo no mercado: 2.250 |
| R6 | sem covariáveis, na mesma amostra | 2.875 | 227 | sem concorrente do mesmo curso e ciclo no mercado: 2.250 |
| R7 | RDD do vizinho: concorrentes de outro município a até 0,050 de um corte | 1.444 | 154 | sem concorrente do mesmo curso e ciclo no mercado: 2.250; sem concorrente de outro município a até 0,050 de um corte (R7): 1.431 |
| C1 | principal, só o ciclo 1 | 416 | 69 | sem concorrente do mesmo curso e ciclo no mercado: 873 |
| C2 | principal, só o ciclo 2 | 783 | 99 | sem concorrente do mesmo curso e ciclo no mercado: 762 |
| C3 | principal, só o ciclo 3 | 1.676 | 184 | sem concorrente do mesmo curso e ciclo no mercado: 615 |
| PL1 | placebo: bolsa média das células de outros cursos na mesma CIR e ciclo | 4.864 | 323 | sem célula de outro curso no mesmo ciclo e CIR (PL1): 261 |
| PL2 | placebo: bolsa média das células do mesmo curso na CIR que só abrem em ciclo posterior | 623 | 149 | ciclo 3 sem ciclo posterior publicado (PL2): 2.291; sem célula do mesmo curso na CIR que só abre em ciclo posterior (PL2): 2.211 |
<!-- R:amostra:fim -->

## 3. Leitura em linguagem simples

<!-- R:leitura:inicio -->
**R_P1 (célula preenchida na 1ª chamada).** Na principal (2.875 células, mercado = CIR), quando a bolsa média das concorrentes sobe R$ 5 mil, o outcome muda −4,9 p.p. (IC 95% [−14,3; 4,6]); p = 0,312, p de Holm = 0,624. MDE por R$ 5 mil: 13,5 p.p. (limiar do protocolo: 10,0 p.p.). Leitura pré-registrada: **inconclusivo**.

**R_P2 (candidatos de 1ª opção por célula).** Na principal (2.875 células, mercado = CIR), quando a bolsa média das concorrentes sobe R$ 5 mil, o outcome muda −0,075 (IC 95% [−0,553; 0,404]); p = 0,760, p de Holm = 0,760. MDE por R$ 5 mil: 0,684 (limiar do protocolo: 0,250). Leitura pré-registrada: **inconclusivo**.

**R_S1 (célula com candidato de 1ª opção).** Na principal (2.875 células, mercado = CIR), quando a bolsa média das concorrentes sobe R$ 5 mil, o outcome muda −5,0 p.p. (IC 95% [−15,0; 5,1]); p = 0,332 (secundária, sem Holm).

**Sensibilidades (relatadas, não escolhidas).** R1/R_P1: −2,17 p.p. por unidade da exposição (IC [−4,01; −0,34]; exclui zero); R2/R_P1: −0,26 p.p. por unidade da exposição (IC [−2,95; 2,42]; contém zero); R3/R_P1: +2,74 p.p. por unidade da exposição (IC [−7,02; 12,50]; contém zero); R7/R_P1: −0,21 p.p. por unidade da exposição (IC [−2,89; 2,46]; contém zero); R1/R_P2: −0,0195 por unidade da exposição (IC [−0,1193; 0,0803]; contém zero); R2/R_P2: −0,0041 por unidade da exposição (IC [−0,1197; 0,1115]; contém zero); R3/R_P2: +0,2814 por unidade da exposição (IC [−0,1836; 0,7463]; contém zero); R7/R_P2: −0,1095 por unidade da exposição (IC [−0,2438; 0,0249]; contém zero).

Entre as sensibilidades das primárias, o IC de 95% exclui zero em R1/R_P1. São linhas sem Holm e não mudam a leitura pré-registrada, que é a da principal. O placebo de outros cursos, que não disputa os mesmos candidatos, tem tamanho parecido: R1/R_P1 −2,17 p.p. contra PL1/R_P1 −1,99 p.p. (p = 0,065), ambos por R$ 1 mil. Esse sinal, portanto, não é específico das concorrentes do mesmo curso e não é lido como deslocamento.

**Placebos.** PL1/R_P1: −10,0 p.p. (IC 95% [−20,5; 0,6]), p = 0,065; PL2/R_P1: −10,2 p.p. (IC 95% [−31,0; 10,5]), p = 0,333; PL1/R_P2: −0,020 (IC 95% [−0,561; 0,521]), p = 0,942; PL2/R_P2: −0,750 (IC 95% [−1,749; 0,249]), p = 0,141. Um placebo com p < 0,05 indicaria que a exposição capta outra coisa (geografia do IVS ou abertura de vagas).

**O que "inconclusivo" quer dizer.** O IC de 95% por R$ 5 mil vai R_P1 de −14,3 p.p. a +4,6 p.p.; R_P2 de −0,553 a +0,404, e o MDE fica acima do limiar do protocolo: o desenho não separa deslocamento de zero nessa margem. Não é evidência de que não haja deslocamento, nem de que haja.

**Por ciclo.** São 9 estimativas (3 ciclos × 3 outcomes), sem correção de multiplicidade e com MDE bem acima do da principal; o IC de 95% exclui zero em C1/R_P2, C2/R_S1, e os sinais mudam de um ciclo para outro. Isso não é achado nem heterogeneidade estabelecida: a leitura continua sendo a da principal.

**Variação disponível.** Na principal, 44,1% das células têm alguma concorrente na CIR com bolsa diferente da sua; o desvio-padrão da exposição é R$ 2,61 mil e, depois dos controles, R$ 1,03 mil (os controles explicam 84,6% da variância da exposição).

Tudo acima é condicional às vagas abertas e mede o pacote do corte das concorrentes (bolsa e outras regras federais nos mesmos cortes), não a participação no PMM-E. Fora das hipóteses do protocolo (§5), os coeficientes são associações condicionais.
<!-- R:leitura:fim -->

## 4. Variação disponível na exposição

Para cada especificação: quantas células, quantas concorrentes, quantas têm concorrente com bolsa diferente e quanto da exposição sobra depois dos controles (a variação que identifica o coeficiente).

<!-- R:variacao:inicio -->
| Especificação | Mercado | Exposição | Células | Concorrentes (mediana) | Fração com concorrente de outra faixa | Fração com concorrente de bolsa maior | DP da exposição | DP residual | R² da exposição nos controles | p10 / p50 / p90 |
|---|---|---|---|---|---|---|---|---|---|---|
| PRINCIPAL | mesma região de saúde (CIR) | R$ mil (bolsa média das concorrentes − própria) | 2.875 | 2,0 | 0,441 | 0,258 | 2,613 | 1,025 | 0,846 | −3,75 / 0,00 / 2,50 |
| R1 | raio de 200 km entre centroides | R$ mil (bolsa média das concorrentes − própria) | 4.522 | 5,0 | 0,697 | 0,439 | 2,911 | 0,856 | 0,913 | −4,28 / 0,00 / 3,33 |
| R2 | mesma UF | R$ mil (bolsa média das concorrentes − própria) | 4.844 | 11,0 | 0,793 | 0,523 | 3,070 | 0,725 | 0,944 | −3,94 / 0,00 / 3,33 |
| R3 | mesma região de saúde (CIR) | fração das concorrentes com bolsa maior (0 a 1) | 2.875 | 2,0 | 0,441 | 0,258 | 0,273 | 0,191 | 0,512 | 0,00 / 0,00 / 0,50 |
| R4 | mesma região de saúde (CIR) | R$ mil (bolsa média das concorrentes − própria) | 2.875 | 2,0 | 0,441 | 0,258 | 2,613 | 0,886 | 0,885 | −3,75 / 0,00 / 2,50 |
| R5 | mesma região de saúde (CIR) | R$ mil (bolsa média das concorrentes − própria) | 2.875 | 2,0 | 0,441 | 0,258 | 2,613 | 1,025 | 0,846 | −3,75 / 0,00 / 2,50 |
| R6 | mesma região de saúde (CIR) | R$ mil (bolsa média das concorrentes − própria) | 2.875 | 2,0 | 0,441 | 0,258 | 2,613 | 1,030 | 0,845 | −3,75 / 0,00 / 2,50 |
| R7 | mesma região de saúde (CIR) | R$ mil (5 × fração das concorrentes perto do corte que estão acima dele) | 1.444 | 3,0 | 0,761 | 0,425 | 2,166 | 1,040 | 0,769 | 0,00 / 3,33 / 5,00 |
| C1 | mesma região de saúde (CIR) | R$ mil (bolsa média das concorrentes − própria) | 416 | 1,0 | 0,442 | 0,238 | 3,138 | 1,231 | 0,846 | −5,00 / 0,00 / 5,00 |
| C2 | mesma região de saúde (CIR) | R$ mil (bolsa média das concorrentes − própria) | 783 | 2,0 | 0,405 | 0,255 | 2,630 | 1,014 | 0,852 | −4,00 / 0,00 / 2,50 |
| C3 | mesma região de saúde (CIR) | R$ mil (bolsa média das concorrentes − própria) | 1.676 | 3,0 | 0,457 | 0,265 | 2,459 | 0,944 | 0,853 | −3,33 / 0,00 / 2,50 |
| PL1 | mesma região de saúde (CIR) | R$ mil (bolsa média das células de outros cursos − própria) | 4.864 | 9,0 | 0,455 | 0,316 | 1,850 | 0,726 | 0,846 | −2,50 / 0,00 / 1,67 |
| PL2 | mesma região de saúde (CIR) | R$ mil (bolsa média das células que só abrem depois − própria) | 623 | 2,0 | 0,390 | 0,244 | 2,777 | 1,060 | 0,854 | −5,00 / 0,00 / 5,00 |
<!-- R:variacao:fim -->

## 5. Resultado principal, Holm e MDE

<!-- R:principal:inicio -->
| Id | Outcome | Papel | Células | Média | Coef. por R$ 1 mil | IC 95% | p | p (t, G−1) | p Holm | MDE por R$ 5 mil |
|---|---|---|---|---|---|---|---|---|---|---|
| R_P1 | célula preenchida na 1ª chamada (≥ 1 alocado) | primária | 2.875 | 27,5 p.p. | −0,97 p.p. | [−2,86; 0,91] | 0,312 | 0,313 | 0,624 | 13,5 p.p. |
| R_P2 | nº de candidatos de 1ª opção da célula | primária | 2.875 | 1,117 | −0,0149 | [−0,1107; 0,0808] | 0,760 | 0,760 | 0,760 | 0,684 |
| R_S1 | célula com ≥ 1 candidato de 1ª opção | secundária | 2.875 | 46,1 p.p. | −0,99 p.p. | [−3,01; 1,02] | 0,332 | 0,333 | — | 14,4 p.p. |

EP CR1 com 227 clusters (CIR). Os ids R-P1, R-P2 e R-S1 do protocolo são R_P1, R_P2 e R_S1 nas saídas. Holm só nas duas primárias (R-P1, R-P2) da principal. MDE = 2,802 × EP (80% de poder, teste bilateral a 5%). Limiares fixados no protocolo (§9), por R$ 5 mil: R-P1 10 p.p.; R-P2 0,25 candidato.
<!-- R:principal:fim -->

## 6. Sensibilidades (R1–R7)

Coeficiente por unidade da exposição (R$ 1 mil em todas, menos R3, que é por fração de 0 a 1). Relatadas para os três outcomes, sem Holm próprio.

<!-- R:sensibilidades:inicio -->
| Especificação | Outcome | Células | Coef. por unidade da exposição | IC 95% | p | MDE por R$ 5 mil | DP residual da exposição | Nota |
|---|---|---|---|---|---|---|---|---|
| R1 | R_P1 | 4.522 | −2,17 p.p. | [−4,01; −0,34] | 0,020 | 13,1 p.p. | 0,856 |  |
| R1 | R_P2 | 4.522 | −0,0195 | [−0,1193; 0,0803] | 0,701 | 0,713 | 0,856 |  |
| R1 | R_S1 | 4.522 | −0,63 p.p. | [−2,61; 1,36] | 0,535 | 14,2 p.p. | 0,856 |  |
| R2 | R_P1 | 4.844 | −0,26 p.p. | [−2,95; 2,42] | 0,848 | 19,2 p.p. | 0,725 |  |
| R2 | R_P2 | 4.844 | −0,0041 | [−0,1197; 0,1115] | 0,944 | 0,826 | 0,725 |  |
| R2 | R_S1 | 4.844 | −0,20 p.p. | [−2,37; 1,97] | 0,856 | 15,5 p.p. | 0,725 |  |
| R3 | R_P1 | 2.875 | +2,74 p.p. | [−7,02; 12,50] | 0,582 | 13,9 p.p. (por unidade) | 0,191 |  |
| R3 | R_P2 | 2.875 | +0,2814 | [−0,1836; 0,7463] | 0,236 | 0,665 (por unidade) | 0,191 |  |
| R3 | R_S1 | 2.875 | +6,32 p.p. | [−5,15; 17,78] | 0,280 | 16,4 p.p. (por unidade) | 0,191 |  |
| R4 | R_P1 | 2.875 | −0,99 p.p. | [−3,13; 1,15] | 0,366 | 15,3 p.p. | 0,886 |  |
| R4 | R_P2 | 2.875 | −0,0237 | [−0,1343; 0,0869] | 0,675 | 0,790 | 0,886 |  |
| R4 | R_S1 | 2.875 | −0,94 p.p. | [−3,20; 1,33] | 0,419 | 16,2 p.p. | 0,886 |  |
| R5 | R_P1 | 2.875 | −0,97 p.p. | [−2,67; 0,72] | 0,261 | 12,1 p.p. | 1,025 |  |
| R5 | R_P2 | 2.875 | −0,0149 | [−0,0996; 0,0697] | 0,730 | 0,605 | 1,025 |  |
| R5 | R_S1 | 2.875 | −0,99 p.p. | [−2,90; 0,91] | 0,305 | 13,6 p.p. | 1,025 |  |
| R6 | R_P1 | 2.875 | −1,41 p.p. | [−3,29; 0,46] | 0,140 | 13,4 p.p. | 1,030 |  |
| R6 | R_P2 | 2.875 | −0,0520 | [−0,1531; 0,0491] | 0,313 | 0,722 | 1,030 |  |
| R6 | R_S1 | 2.875 | −1,83 p.p. | [−3,99; 0,34] | 0,098 | 15,5 p.p. | 1,030 |  |
| R7 | R_P1 | 1.444 | −0,21 p.p. | [−2,89; 2,46] | 0,875 | 19,1 p.p. | 1,040 |  |
| R7 | R_P2 | 1.444 | −0,1095 | [−0,2438; 0,0249] | 0,110 | 0,960 | 1,040 |  |
| R7 | R_S1 | 1.444 | −2,24 p.p. | [−4,92; 0,45] | 0,102 | 19,2 p.p. | 1,040 |  |
<!-- R:sensibilidades:fim -->

## 7. Placebos

PL1 usa as células de outros cursos (não disputam os mesmos candidatos); PL2 usa as células do mesmo curso que só abrem em ciclo posterior (o candidato do ciclo não podia escolhê-las).

<!-- R:placebos:inicio -->
| Especificação | Outcome | Células | Coef. por unidade da exposição | IC 95% | p | MDE por R$ 5 mil | DP residual da exposição | Nota |
|---|---|---|---|---|---|---|---|---|
| PL1 | R_P1 | 4.864 | −1,99 p.p. | [−4,10; 0,12] | 0,065 | 15,1 p.p. | 0,726 |  |
| PL1 | R_P2 | 4.864 | −0,0040 | [−0,1123; 0,1043] | 0,942 | 0,774 | 0,726 |  |
| PL1 | R_S1 | 4.864 | −1,84 p.p. | [−4,15; 0,47] | 0,118 | 16,5 p.p. | 0,726 |  |
| PL2 | R_P1 | 623 | −2,05 p.p. | [−6,20; 2,10] | 0,333 | 29,7 p.p. | 1,060 |  |
| PL2 | R_P2 | 623 | −0,1500 | [−0,3498; 0,0499] | 0,141 | 1,428 | 1,060 |  |
| PL2 | R_S1 | 623 | −1,23 p.p. | [−4,83; 2,37] | 0,503 | 25,7 p.p. | 1,060 |  |
<!-- R:placebos:fim -->

## 8. Por ciclo (condição pré-tratamento)

O ciclo 1 fica à parte porque a adesão dos gestores precedeu o anúncio da faixa. As nove linhas abaixo não têm correção de multiplicidade e MDE alto: um p < 0,05 isolado aqui não é achado e não muda a leitura da principal.

<!-- R:ciclos:inicio -->
| Especificação | Outcome | Células | Coef. por unidade da exposição | IC 95% | p | MDE por R$ 5 mil | DP residual da exposição | Nota |
|---|---|---|---|---|---|---|---|---|
| C1 | R_P1 | 416 | +2,33 p.p. | [−1,29; 5,96] | 0,207 | 25,9 p.p. | 1,231 |  |
| C1 | R_P2 | 416 | +0,1077 | [0,0140; 0,2013] | 0,024 | 0,670 | 1,231 |  |
| C1 | R_S1 | 416 | +1,87 p.p. | [−1,67; 5,41] | 0,300 | 25,3 p.p. | 1,231 |  |
| C2 | R_P1 | 783 | −1,28 p.p. | [−4,78; 2,22] | 0,473 | 25,0 p.p. | 1,014 |  |
| C2 | R_P2 | 783 | −0,0279 | [−0,1991; 0,1434] | 0,750 | 1,224 | 1,014 |  |
| C2 | R_S1 | 783 | −4,63 p.p. | [−8,49; −0,77] | 0,019 | 27,6 p.p. | 1,014 |  |
| C3 | R_P1 | 1.676 | −2,26 p.p. | [−5,08; 0,57] | 0,117 | 20,2 p.p. | 0,944 |  |
| C3 | R_P2 | 1.676 | −0,0703 | [−0,2016; 0,0611] | 0,294 | 0,939 | 0,944 |  |
| C3 | R_S1 | 1.676 | −0,53 p.p. | [−3,37; 2,31] | 0,716 | 20,3 p.p. | 0,944 |  |
<!-- R:ciclos:fim -->

## 9. Figuras

Nenhuma figura traz texto de leitura dentro da imagem; o "Como ler" fica aqui e no campo `como_ler` de `R_resumo.json`.

<!-- R:figuras:inicio -->
| Arquivo | O que mostra | Como ler |
|---|---|---|
| `R_coeficientes.png` | coeficiente da exposição por R$ 5 mil, principal, sensibilidades, ciclos e placebos | Cada ponto é a mudança do outcome da célula quando a bolsa média das concorrentes sobe R$ 5 mil; a barra é o IC de 95%. Placebos em laranja. A leitura que vale é a da tabela da seção 5, não a de um ponto isolado. |
| `R_residuos_principal.png` | médias por grupo do outcome e da exposição residualizados, especificação principal | Cada ponto é a média de um grupo de células com exposição parecida, depois de tirar os controles; a reta tem a inclinação do coeficiente principal. A largura do eixo horizontal é a variação da exposição que sobra para identificar o efeito. |
<!-- R:figuras:fim -->

## 10. Desvios e decisões de implementação

<!-- R:desvios:inicio -->
1. **Contagem do §4 do protocolo** (24/10/2026). O §4 registrou 2.876 (CIR), 4.533 (raio) e 4.854 (UF) células com concorrente, numa conta de desenho feita antes de congelar, em que a célula sem IVS oficial e as 9 células sem CIR ainda entravam no universo. O próprio §4 diz que essas células ficam fora. *Resolução:* Universo = células com IVS oficial e CIR, como o §4 manda; a amostra principal tem o número da seção 2. Nada muda na especificação.
2. **R7: concorrente equidistante dos dois cortes** (24/10/2026). O §7 diz 'a até 0,050 de um corte'; uma célula com IVS 0,350 está a 0,050 dos dois. No universo há 23 células com IVS 0,350. *Resolução:* Cada concorrente usa o corte mais próximo; no empate, 0,300 (fica acima dele, com bolsa da faixa 2). Regra definida sem consultar outcome.
3. **PL2: chave que reaparece em mais de um ciclo posterior** (24/10/2026). Uma célula (estabelecimento × curso) ausente do ciclo 1 pode aparecer nos ciclos 2 e 3. *Resolução:* Entra uma vez, com os atributos do primeiro ciclo posterior em que aparece.
4. **Cluster nos mercados largos** (24/10/2026). O §5 fixa cluster por CIR; no raio de 200 km (R1) e na UF (R2) a exposição se repete além da CIR. *Resolução:* Mantido o cluster por CIR, como no protocolo; a limitação fica declarada na seção 11.
5. **R7: controle do número de concorrentes** (24/10/2026). O §7 manda manter os controles próprios da principal; o log(1 + nº de concorrentes) da principal conta todas as concorrentes da CIR, não só as vizinhas do corte. *Resolução:* Mantido o log(1 + nº de concorrentes) da CIR inteira; a média da spline das concorrentes sai e entram as médias de (IVS − corte) das vizinhas, como no §7.
6. **Intervalo de confiança** (24/10/2026). O §5 pede EP CR1 e o p pela t com G − 1 graus de liberdade ao lado. *Resolução:* O IC de 95% e o p principal usam a normal; o p pela t com G − 1 fica na coluna `p_t_G1`. Nenhuma conclusão muda de um para o outro.
<!-- R:desvios:fim -->

## 11. Limites

- **Pacote do corte.** As concorrentes acima do corte estão sob outras regras federais além da bolsa (auditoria 18).
- **Vagas abertas endógenas.** A abertura é decisão do gestor e da SGTES; os limites de Lee do A2 (doc 49, §15) são largos e, no P5 (doc 57e), a célula pedida salta nos cortes sem passar no BKY. O conjunto de concorrentes, e portanto a exposição, depende dessa abertura.
- **Conjunto de escolha.** Supõe-se que o candidato vê todas as células do curso no ciclo; o mercado geográfico (CIR, raio, UF) é uma aproximação e não usa a origem do candidato.
- **Células com concorrente.** A amostra exige ao menos uma concorrente no mercado: as células isoladas ficam fora e a amostra pende para regiões com mais células.
- **Cluster.** Nas definições de mercado mais largas (raio, UF), as exposições se repetem além da CIR, e o EP por CIR pode ser otimista.
- **Associação.** Fora das hipóteses do §5 do protocolo, os coeficientes são associações condicionais.
