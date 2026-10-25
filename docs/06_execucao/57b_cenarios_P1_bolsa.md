# 57b. Cenários contrafactuais de bolsa (T1.6): SIMULAÇÃO, NÃO OBSERVAÇÃO

> **ATENÇÃO: tudo neste documento é simulação (`natureza_dos_dados = CENARIO_CONTRAFACTUAL`).** Nenhum número abaixo foi observado: são alocações refeitas com um modelo de escolha estimado e o mecanismo do G2, sob hipóteses fixas. Não use estes números como resultado empírico nem como efeito causal estimado.<br>
> **Gerado por** `scripts/rdd_bolsa/25b_cenarios_bolsa.py` a partir de `output/cenarios/P1_*`; não editar à mão (o teste `tests/test_cenarios_bolsa.py` confere que este arquivo é igual ao gerado).<br>
> **Protocolo:** [adendo §7 do protocolo 52](52_protocolo_P1_escolha_dap.md#7-adendo-de-24102026-t16-cenários), congelado em 24/10/2026 antes de simular, e [adendo §8](52_protocolo_P1_escolha_dap.md#8-adendo-de-25102026-t16-nova-regra-de-desempate-e-revalidação) (25/10/2026), que só troca a regra de desempate depois da falha de 24/10 (seção 9). Modelo de escolha: [doc 57a](57a_resultados_P1_escolha.md) (M1), auditado na auditoria 26. Mecanismo: [portão G2](../auditorias/G2_viabilidade_mecanismo.md).

## 1. A pergunta e o que a simulação faz

**Pergunta do autor:** quantas vagas a mais seriam preenchidas no total se a bolsa subisse R$ 5 mil, levando em conta que todas as vagas disputam o mesmo grupo de candidatos numa alocação centralizada por nota? A RDD não responde isso: ela compara células perto do corte, e uma vaga que ganha um candidato pode estar tirando esse candidato de outra.

**O que a simulação faz**, para a 1ª chamada dos ciclos 1, 2 e 3:
1. parte das listas de opções observadas e sorteia a parte da preferência que o modelo não explica, de modo que, sem mudar a bolsa, cada candidato repete exatamente a lista que fez;
2. muda a bolsa das células segundo o cenário e refaz a lista de cada candidato com o peso da bolsa do M1;
3. refaz a alocação com o mecanismo do G2 (aceitação adiada por opção e nota, cotas, capacidade efetiva);
4. compara com a alocação sem mudança (B0) da mesma réplica.

**Hipóteses (todas fixas):** vagas e capacidade fixas; o grupo de candidatos é fixo (ninguém novo entra, ninguém desiste); cada candidato mantém o número de opções que listou; alocação por nota como no G2; só a 1ª chamada; sem 2ª chamada, desistência, homologação ou custo fiscal (o custo abaixo é aritmética simples). Bolsas sempre dentro de R$ 10–20 mil, a faixa observada.

**O que o contraste mede:** o incentivo da bolsa como o M1 o identifica (o pacote do corte, auditoria 18), aplicado a quem já se candidatou. Não mede participação no PMM-E nem quantos médicos a mais o programa atrairia.

## 2. Mercado

| Ciclo | Candidatos elegíveis | Respondem ao cenário (amostra P1) | Lista fixa (fora da amostra P1) | Capacidade efetiva | Vagas preenchidas publicadas |
|---|---|---|---|---|---|
| ciclo 1 | 879 | 820 | 59 | 921 | 527 |
| ciclo 2 | 2179 | 2032 | 147 | 1836 | 1057 |
| ciclo 3 | 2604 | 2474 | 130 | 1295 | 704 |

- Unidades de simulação: 5639 (tipo A, 1ª e 2ª opção no mesmo curso: 3645; tipo B, só a 1ª opção modelada: 1776; tipo C, 2ª opção em outro curso: 218).
- M1 reestimado igual ao gravado (diferença máxima 2.9e-10); β_bolsa = 0,0424 (IC 95% [−0,0027; +0,0874]).
- R = 200 réplicas, semente 20261024; S4 com 100 sorteios por candidato (ESS mediano 69,8).

## 3. Validação de base

O cenário sem mudança (B0) precisa reproduzir as vagas preenchidas publicadas na 1ª chamada, por ciclo e faixa, com |B0 − observado| ≤ max(3; 2% do observado) em todas as réplicas (fixado antes de simular). A coluna do G2 principal usa a classificação publicada como desempate. Desde o adendo §8, o B0 usa a mesma classificação nos pares observados e o sorteio só nos pares novos; como no B0 todos os pares são observados, o B0 coincide com a coluna do G2 principal em todas as réplicas (a validação testa o mecanismo, não o sorteio).

| Ciclo | Faixa | Observado (1ª chamada publicada) | G2 principal (classificação publicada) | B0 nas réplicas (mín.–máx.) | Desvio máximo | Tolerância | Passa |
|---|---|---|---|---|---|---|---|
| ciclo 1 | Faixa 3 (IVS ≤ 0,300; R$ 10 mil) | 183 | 184 | 184–184 | 1 | 3,7 | sim |
| ciclo 1 | Faixa 2 (0,300–0,400; R$ 15 mil) | 212 | 212 | 212–212 | 0 | 4,2 | sim |
| ciclo 1 | Faixa 1 (IVS > 0,400; R$ 20 mil) | 132 | 133 | 133–133 | 1 | 3,0 | sim |
| ciclo 1 | total | 527 | 529 | 529–529 | 2 | 10,5 | sim |
| ciclo 2 | Faixa 3 (IVS ≤ 0,300; R$ 10 mil) | 454 | 454 | 454–454 | 0 | 9,1 | sim |
| ciclo 2 | Faixa 2 (0,300–0,400; R$ 15 mil) | 425 | 425 | 425–425 | 0 | 8,5 | sim |
| ciclo 2 | Faixa 1 (IVS > 0,400; R$ 20 mil) | 178 | 178 | 178–178 | 0 | 3,6 | sim |
| ciclo 2 | total | 1057 | 1057 | 1057–1057 | 0 | 21,1 | sim |
| ciclo 3 | Faixa 3 (IVS ≤ 0,300; R$ 10 mil) | 331 | 331 | 331–331 | 0 | 6,6 | sim |
| ciclo 3 | Faixa 2 (0,300–0,400; R$ 15 mil) | 248 | 249 | 249–249 | 1 | 5,0 | sim |
| ciclo 3 | Faixa 1 (IVS > 0,400; R$ 20 mil) | 125 | 125 | 125–125 | 0 | 3,0 | sim |
| ciclo 3 | total | 704 | 705 | 705–705 | 1 | 14,1 | sim |

**Resultado da validação: PASSOU.**

Conferências em toda réplica: as listas sem mudança são iguais às observadas em 1000 de 1000 sorteios (variante × réplica); células acima da capacidade: 0; alocados fora da própria lista: 0; cada médico ocupa no máximo uma vaga (por construção do mecanismo).

## 4. Leitura em linguagem simples

**Subir a bolsa redistribui médicos entre vagas ou aumenta o total preenchido?**

- **C1** (+R$ 5 mil na faixa de bolsa menor (Faixa 3: 10 → 15)): em média 117,2 médicos terminam numa vaga diferente; 33,4 vagas passam a ser preenchidas e 21,8 deixam de ser. O total preenchido muda +11,6 (faixa S3 [−0,0; +27,1]), e a faixa toca o zero (um dos limites arredonda para 0,0). A variação líquida equivale a 10% das mudanças de vaga: **a bolsa sobretudo redistribui médicos entre vagas**.
- **C2** (todas no maior valor (R$ 20 mil)): em média 223,3 médicos terminam numa vaga diferente; 53,3 vagas passam a ser preenchidas e 38,7 deixam de ser. O total preenchido muda +14,5 (faixa S3 [−2,0; +29,1]), e a faixa contém zero. A variação líquida equivale a 7% das mudanças de vaga: **a bolsa sobretudo redistribui médicos entre vagas**.
- **C3** (+R$ 5 mil só na faixa 0,300–0,400 (Faixa 2: 15 → 20)): em média 150,2 médicos terminam numa vaga diferente; 28,8 vagas passam a ser preenchidas e 35,7 deixam de ser. O total preenchido muda −6,9 (faixa S3 [−26,0; +5,0]), e a faixa contém zero. A variação líquida equivale a 5% das mudanças de vaga: **a bolsa sobretudo redistribui médicos entre vagas**.
- **C4** (bolsa uniforme de R$ 15 mil): em média 223,3 médicos terminam numa vaga diferente; 53,3 vagas passam a ser preenchidas e 38,7 deixam de ser. O total preenchido muda +14,5 (faixa S3 [−2,0; +29,1]), e a faixa contém zero. A variação líquida equivale a 7% das mudanças de vaga: **a bolsa sobretudo redistribui médicos entre vagas**.
- **C2 e C4 dão as mesmas vagas** em todas as variantes (só o custo muda). Não é erro: as duas grades diferem por uma constante (−R$ 5 mil em todas as células), e no modelo de escolha só a diferença de bolsa entre as vagas do conjunto move a escolha. O nível da bolsa só mudaria quem se candidata, e isso está fora da simulação (grupo de candidatos fixo).

**Resposta direta à pergunta do autor (C1, +R$ 5 mil na faixa de bolsa menor):** na simulação, o total de vagas preenchidas na 1ª chamada dos três ciclos muda +11,6 (faixa S3 [−0,0; +27,1]), enquanto 117,2 médicos trocam de vaga. Com o grupo de candidatos fixo, a bolsa só pode mudar o total se levar candidatos de células disputadas (onde perderiam para alguém de nota maior) para células que ficariam vazias, ou o contrário. Isto é simulação condicional ao modelo e às hipóteses da seção 1, não observação.

## 5. Resultados por cenário (ciclos 1–3, 1ª chamada)

Ponto: média das réplicas do principal (M1, θ̂). Entre colchetes: percentis 2,5 e 97,5 do S3 (θ sorteado da distribuição assintótica e erro sorteado), a faixa de incerteza principal do adendo.

| Cenário | Δ total de vagas preenchidas [faixa S3] | Médicos que mudam de vaga [faixa S3] | Vagas que deixam de ser preenchidas | Vagas que passam a ser preenchidas | Δ custo mensal das bolsas, R$ mil (aritmética simples) [faixa S3] |
|---|---|---|---|---|---|
| **C1**: +R$ 5 mil na faixa de bolsa menor (Faixa 3: 10 → 15) | +11,6 [−0,0; +27,1] | 117,2 [9,0; 220,1] | 21,8 | 33,4 | +4.989 [+4.815; +5.216] |
| **C2**: todas no maior valor (R$ 20 mil) | +14,5 [−2,0; +29,1] | 223,3 [19,9; 400,1] | 38,7 | 53,3 | +14.411 [+14.080; +14.702] |
| **C3**: +R$ 5 mil só na faixa 0,300–0,400 (Faixa 2: 15 → 20) | −6,9 [−26,0; +5,0] | 150,2 [11,0; 334,2] | 35,7 | 28,8 | +4.527 [+4.310; +4.770] |
| **C4**: bolsa uniforme de R$ 15 mil | +14,5 [−2,0; +29,1] | 223,3 [19,9; 400,1] | 38,7 | 53,3 | +2.883 [+2.635; +3.101] |

### 5.1 Por faixa observada da célula

| Cenário | Faixa 3 (IVS ≤ 0,300; R$ 10 mil) | Faixa 2 (0,300–0,400; R$ 15 mil) | Faixa 1 (IVS > 0,400; R$ 20 mil) |
|---|---|---|---|
| C1 | +32,7 [−1,0; +67,0] | −15,1 [−32,0; +0,0] | −6,1 [−14,0; +0,0] |
| C2 | +43,7 [−2,0; +87,0] | −6,2 [−19,0; +3,0] | −22,9 [−49,0; +1,1] |
| C3 | −23,5 [−55,1; +1,0] | +27,7 [−1,0; +59,1] | −11,1 [−24,0; +0,0] |
| C4 | +43,7 [−2,0; +87,0] | −6,2 [−19,0; +3,0] | −22,9 [−49,0; +1,1] |

### 5.2 De onde saem e para onde vão os médicos que mudam (principal, média por réplica)

Só os médicos cuja vaga muda entram. "Não alocado" na origem: o médico passa a ter vaga; no destino: perde a vaga que tinha no B0. Na diagonal, mudança de célula dentro da mesma faixa.

| Cenário | Origem (no B0) | para Faixa 3 | para Faixa 2 | para Faixa 1 | para não alocado |
|---|---|---|---|---|---|
| C1 | de Faixa 3 | 0,3 | 1,2 | 0,2 | 19,8 |
| C1 | de Faixa 2 | 14,1 | 1,1 | 0,6 | 14,2 |
| C1 | de Faixa 1 | 7,6 | 0,4 | 0,2 | 5,9 |
| C1 | de não alocado | 32,2 | 12,3 | 7,0 | 0,0 |
| C2 | de Faixa 3 | 0,4 | 1,3 | 0,5 | 28,1 |
| C2 | de Faixa 2 | 14,1 | 1,1 | 2,3 | 29,5 |
| C2 | de Faixa 1 | 15,1 | 12,4 | 1,1 | 22,7 |
| C2 | de não alocado | 44,4 | 26,1 | 24,4 | 0,0 |
| C3 | de Faixa 3 | 1,0 | 17,1 | 0,2 | 17,6 |
| C3 | de Faixa 2 | 0,9 | 0,4 | 1,4 | 31,1 |
| C3 | de Faixa 1 | 0,1 | 12,8 | 0,8 | 12,6 |
| C3 | de não alocado | 10,3 | 31,2 | 12,8 | 0,0 |
| C4 | de Faixa 3 | 0,4 | 1,3 | 0,5 | 28,1 |
| C4 | de Faixa 2 | 14,1 | 1,1 | 2,3 | 29,5 |
| C4 | de Faixa 1 | 15,1 | 12,4 | 1,1 | 22,7 |
| C4 | de não alocado | 44,4 | 26,1 | 24,4 | 0,0 |

### 5.3 Por ciclo (principal [faixa S3]; médicos que mudam)

| Cenário | Ciclo 1 | Ciclo 2 | Ciclo 3 |
|---|---|---|---|
| C1 | −0,5 [−6,0; +5,0]; mudam 23,0 | +5,5 [−3,0; +15,0]; mudam 65,7 | +6,6 [+0,0; +14,0]; mudam 28,5 |
| C2 | −2,3 [−11,0; +3,0]; mudam 47,8 | +7,7 [−2,0; +18,0]; mudam 115,8 | +9,1 [−0,0; +20,0]; mudam 59,7 |
| C3 | −1,9 [−9,0; +3,0]; mudam 42,2 | −5,7 [−18,1; +2,0]; mudam 65,9 | +0,7 [−6,0; +7,0]; mudam 42,2 |
| C4 | −2,3 [−11,0; +3,0]; mudam 47,8 | +7,7 [−2,0; +18,0]; mudam 115,8 | +9,1 [−0,0; +20,0]; mudam 59,7 |

### 5.4 Sensibilidades

| Cenário | Variante | Δ total preenchido (média) | Percentis 2,5–97,5 nas réplicas | Médicos que mudam (média) |
|---|---|---|---|---|
| C1 | M1, θ̂ (só sorteio do erro) | +11,6 | [+1,0; +21,0] | 117,2 |
| C1 | M1 com β_bolsa no limite inferior do IC 95% | −0,2 | [−3,0; +3,0] | 6,3 |
| C1 | M1 com β_bolsa no limite superior do IC 95% | +18,6 | [+5,0; +31,0] | 213,1 |
| C1 | M1 com θ sorteado de N(θ̂, V_cluster) a cada réplica | +11,6 | [−0,0; +27,1] | 118,3 |
| C1 | M8 (logit misto), coeficientes individuais condicionais às escolhas | +6,4 | [−13,0; +21,0] | 287,5 |
| C2 | M1, θ̂ (só sorteio do erro) | +14,5 | [+0,0; +27,0] | 223,3 |
| C2 | M1 com β_bolsa no limite inferior do IC 95% | −0,2 | [−3,0; +3,0] | 11,2 |
| C2 | M1 com β_bolsa no limite superior do IC 95% | +18,1 | [+2,0; +32,0] | 391,6 |
| C2 | M1 com θ sorteado de N(θ̂, V_cluster) a cada réplica | +13,6 | [−2,0; +29,1] | 223,7 |
| C2 | M8 (logit misto), coeficientes individuais condicionais às escolhas | +5,5 | [−14,1; +23,1] | 536,0 |
| C3 | M1, θ̂ (só sorteio do erro) | −6,9 | [−19,0; +6,0] | 150,2 |
| C3 | M1 com β_bolsa no limite inferior do IC 95% | +0,4 | [−3,0; +4,0] | 8,1 |
| C3 | M1 com β_bolsa no limite superior do IC 95% | −19,6 | [−36,0; −4,0] | 303,4 |
| C3 | M1 com θ sorteado de N(θ̂, V_cluster) a cada réplica | −7,6 | [−26,0; +5,0] | 154,9 |
| C3 | M8 (logit misto), coeficientes individuais condicionais às escolhas | −7,2 | [−24,0; +10,0] | 366,8 |
| C4 | M1, θ̂ (só sorteio do erro) | +14,5 | [+0,0; +27,0] | 223,3 |
| C4 | M1 com β_bolsa no limite inferior do IC 95% | −0,2 | [−3,0; +3,0] | 11,2 |
| C4 | M1 com β_bolsa no limite superior do IC 95% | +18,1 | [+2,0; +32,0] | 391,6 |
| C4 | M1 com θ sorteado de N(θ̂, V_cluster) a cada réplica | +13,6 | [−2,0; +29,1] | 223,7 |
| C4 | M8 (logit misto), coeficientes individuais condicionais às escolhas | +5,5 | [−14,1; +23,1] | 536,0 |

S1 e S2 fixam β_bolsa nos limites do IC 95% do M1 (o limite inferior é negativo: bolsa maior atrairia menos). O S4 usa o logit misto (M8), em que o peso da bolsa varia entre os candidatos.

## 6. Figuras

Nenhuma figura traz texto de leitura dentro da imagem; o "Como ler" fica aqui e no campo `como_ler` de `P1_cenarios_resumo.json`.

| Arquivo | O que mostra | Como ler |
|---|---|---|
| `P1_cenarios_total_e_mudancas.png` | médicos que mudam de vaga e variação do total preenchido, por cenário (principal; faixa S3) | Para cada cenário, a barra da esquerda é quantos médicos terminam numa vaga diferente da do cenário sem mudança, e a da direita é quanto muda o total de vagas preenchidas (ciclos 1–3, 1ª chamada). O traço é a faixa de 95% com a incerteza dos parâmetros (S3). Barra da esquerda alta e barra da direita perto de zero: a bolsa troca médicos de lugar, mas quase não aumenta o total. |
| `P1_cenarios_por_faixa.png` | variação das vagas preenchidas por faixa observada da célula, por cenário (principal; faixa S3) | Para cada cenário, cada barra é quanto muda o número de vagas preenchidas numa faixa de IVS (a faixa observada da célula), com a faixa de 95% do S3. Barras que se compensam (uma faixa ganha o que outra perde) indicam redistribuição entre faixas, não médicos a mais. |

## 7. Limites

- **Grupo de candidatos fixo.** Ninguém entra por causa da bolsa e ninguém desiste. Se a bolsa atrai médicos novos, o total preenchido subiria mais do que aqui; isso não é medido.
- **Capacidade efetiva fixa.** Inclui a redistribuição do item 5.7 já feita na 1ª chamada publicada; a SGTES poderia redistribuir de outro modo num cenário.
- **Modelo de escolha.** O peso da bolsa é o do M1, cujo IC 95% contém zero; IIA dentro do curso; o candidato vê todas as células do curso. A ordem entre opções de cursos diferentes fica a observada.
- **Quem não responde.** Candidatos sem origem ligada no G1 mantêm a lista observada (seção 2).
- **Desempate.** Classificação publicada nos pares candidato × célula observados; nos pares novos, sorteio por candidato posicionado entre os observados empatados (adendo §8), no lugar da regra do edital (UF e idade), que não é pública. Em células com muitos empates de nota no corte, o resultado para pares novos depende desse sorteio.
- **Só a 1ª chamada.** Sem 2ª chamada, desistência, homologação; o custo é só bolsa × alocados.
- **Só redistribuição.** Com candidatos e vagas fixos, um aumento uniforme da bolsa não muda nenhuma escolha no logit condicional (só a diferença de bolsa entre as células do conjunto entra na utilidade): C2 e C4 dão o mesmo resultado. Os efeitos dos cenários vêm só da redistribuição de candidatos entre células e faixas, e a variação do total vem de candidatos que saem de células disputadas para células com vaga sobrando. Não é atração de médicos novos.
- **Incerteza herdada do M1.** O IC 95% do β_bolsa contém zero; com β no limite inferior (S1) o efeito no total é nulo, e a faixa S3 (principal) contém ou toca o zero em C1, C2 e C4 para o total. Os números são condicionais ao modelo; leia a faixa, não o ponto.

## 8. Nota de processo

Revalidação de 25/10/2026, depois do commit do adendo §8 (protocolo 52) e da escolha do autor pela opção 1. A falha de 24/10 já era conhecida (seção 9). Antes da execução com R = 200 houve uma depuração com R = 2 (opção `--depurar`, que só roda a validação de base e não grava nada); ela passou a validação e não calculou cenários, então nenhum número de cenário foi visto antes da execução com R = 200. A única mudança de código no cálculo foi o desempate (adendo §8); o doc passou a incluir a falha de 24/10 como histórico (seção 9), a partir da saída preservada. Modelo, mecanismo, tolerância, regra de validação, R e semente não mudaram.

## 9. Histórico: falha da validação de 24/10/2026 (registro preservado)

Execução anterior, com o desempate por sorteio por candidato em todos os pares (adendo §7.3). Saída preservada em `output/cenarios/P1_cenarios_validacao_base_falha_2026-10-24.csv`. Mesma regra e tolerância; a única mudança depois foi o desempate (adendo §8).

| Ciclo | Faixa | Observado (1ª chamada publicada) | G2 principal (classificação publicada) | B0 nas réplicas (mín.–máx.) | Desvio máximo | Tolerância | Passa |
|---|---|---|---|---|---|---|---|
| ciclo 1 | Faixa 3 (IVS ≤ 0,300; R$ 10 mil) | 183 | 184 | 182–188 | 5 | 3,7 | **não** |
| ciclo 1 | Faixa 2 (0,300–0,400; R$ 15 mil) | 212 | 212 | 210–214 | 2 | 4,2 | sim |
| ciclo 1 | Faixa 1 (IVS > 0,400; R$ 20 mil) | 132 | 133 | 130–133 | 2 | 3,0 | sim |
| ciclo 1 | total | 527 | 529 | 525–534 | 7 | 10,5 | sim |
| ciclo 2 | Faixa 3 (IVS ≤ 0,300; R$ 10 mil) | 454 | 454 | 446–453 | 8 | 9,1 | sim |
| ciclo 2 | Faixa 2 (0,300–0,400; R$ 15 mil) | 425 | 425 | 419–425 | 6 | 8,5 | sim |
| ciclo 2 | Faixa 1 (IVS > 0,400; R$ 20 mil) | 178 | 178 | 176–178 | 2 | 3,6 | sim |
| ciclo 2 | total | 1057 | 1057 | 1044–1055 | 13 | 21,1 | sim |
| ciclo 3 | Faixa 3 (IVS ≤ 0,300; R$ 10 mil) | 331 | 331 | 331–331 | 0 | 6,6 | sim |
| ciclo 3 | Faixa 2 (0,300–0,400; R$ 15 mil) | 248 | 249 | 247–249 | 1 | 5,0 | sim |
| ciclo 3 | Faixa 1 (IVS > 0,400; R$ 20 mil) | 125 | 125 | 125–125 | 0 | 3,0 | sim |
| ciclo 3 | total | 704 | 705 | 703–705 | 1 | 14,1 | sim |

**Resultado da validação de 24/10/2026: FALHOU.**

### 9.1 Falha da validação de base

`FALHA_VALIDACAO_BASE`. Onde falhou: ciclo 1, Faixa 3 (IVS ≤ 0,300; R$ 10 mil): observado 183, B0 entre 182 e 188 (média 185,1), desvio máximo 5 > tolerância 3,66.

Conforme o adendo, nada foi calibrado e **os cenários não foram calculados**: não há resposta simulada à pergunta do autor nesta execução. Não há arquivo de réplicas, tabela, fluxos nem figura de cenário em `output/cenarios/`.

**O que a falha mostra.** O mecanismo foi conferido: com o mesmo desempate, a alocação montada pelo script é idêntica à do `alocar` do G2 sobre as linhas publicadas. A diferença vem do desempate por sorteio por candidato, fixado no adendo porque a classificação publicada não existe para pares candidato × célula novos. Com a classificação publicada (coluna do G2 principal), a reconstrução fica a no máximo 2 vaga(s) do observado em cada linha da tabela. Onde há empate de nota no corte da célula (G2, seção 4), o sorteio troca quem fica, e o perdedor pode ocupar ou não a vaga da 2ª opção; isso desloca vagas entre faixas em parte das réplicas.

**Decisões em aberto, do autor (nenhuma foi executada em 24/10):**
1. aceitar um desempate que use a classificação publicada nos pares observados e o sorteio só nos pares novos, com nova validação (**escolhida pelo autor em 25/10/2026; adendo §8**);
2. trocar a regra "em todas as réplicas" por uma regra sobre a média ou sobre um percentil das réplicas;
3. rodar só os ciclos 2 e 3, que passaram;
4. manter a falha como resultado: com o desempate do edital fora dos dados, o mecanismo não é reproduzido com a precisão exigida em todas as réplicas.

Qualquer uma delas exige um adendo datado antes de rodar, que registre que esta falha já foi vista.

### 9.2 Nota de processo de 24/10/2026

Antes da execução com R = 200, o script foi rodado três vezes com R = 2 para depurar o código (24/10/2026, depois do commit do adendo). A 1ª parou numa conferência interna (instabilidade numérica no S4, corrigida no sorteio condicional); a 2ª parou num erro do código das figuras; a 3ª passou a validação de base com 2 réplicas e calculou os cenários, e o agente viu esses números de 2 réplicas. A execução com R = 200 falhou na validação de base. Depois disso só mudaram o texto do doc e a limpeza das saídas de cenário da depuração (apagadas); nada mudou no modelo, no mecanismo, na tolerância ou no desempate.

