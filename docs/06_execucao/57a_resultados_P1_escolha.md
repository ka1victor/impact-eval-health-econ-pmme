# 57a. Resultados do P1: quanto a bolsa anunciada move a escolha de onde trabalhar

> **Gerado por** `scripts/rdd_bolsa/25_escolha_dap.py` a partir de `output/rdd_bolsa/P1_*`; não editar à mão (o teste `tests/test_escolha_dap.py` confere que este arquivo é igual ao gerado).<br>
> **Protocolo:** [`52_protocolo_P1_escolha_dap.md`](52_protocolo_P1_escolha_dap.md), congelado em 19/10/2026 antes de estimar; estatuto `PROTOCOLO_52_POS_RESULTADO` (o E9, a X4 e a X5 já tinham sido vistos).<br>
> **Saídas:** `output/rdd_bolsa/P1_estimativas.csv`, `P1_dap.csv`, `P1_resumo.json` e `P1_figuras/`; toda linha tem `natureza_dos_dados = EMPIRICO`.<br>
> **Fora deste bloco:** os cenários contrafactuais do T1.6 (doc 51, §3), que só rodam depois da auditoria.<br>
> **Para a síntese:** este documento é a seção P1 que o protocolo manda pôr no doc 57 (ver desvios).

## 1. O que se mede e o que não se pode dizer

- **Estimando principal (P1a).** O peso da bolsa anunciada (por R$ 1 mil por mês) na escolha da 1ª opção do candidato **dentro do conjunto de vagas abertas** do seu curso e ciclo, com a distância e os atributos de origem controlados.
- **Identificação.** A bolsa muda só nos cortes do IVS 2010 oficial (0,300 e 0,400); o IVS entra como uma curva contínua com dobras nos cortes e sem salto. O peso da bolsa sai, portanto, dos saltos da bolsa nos cortes, com a vulnerabilidade contínua controlada.
- **O que o contraste mede.** O pacote do corte (bolsa +R$ 5 mil e outras regras federais que mudam no mesmo IVS, auditoria 18) e o incentivo marginal da bolsa. Não mede a participação no PMM-E nem o efeito total do Agora Tem Especialistas.
- **O que não diz.** Nada sobre quem não se candidatou, nem sobre o número total de candidatos: é uma realocação entre vagas já abertas.
- **DAP (P1b, P1c).** Razão de coeficientes: quanto de bolsa mensal equivale a um atributo da vaga. É uma estimativa com intervalo, sem teste de zero.

**Ameaças declaradas (protocolo, §4):**
- seleção pela ligação: os candidatos sem município de origem no G1 ficam fora (seção 2);
- a origem é o município do estabelecimento em que o candidato tinha vínculo médico, não a residência;
- o conjunto de escolha supõe que o candidato viu todas as células do curso;
- outras políticas nos mesmos cortes podem mudar atributos não observados da vaga (pacote).

## 2. Amostra

<!-- P1:amostra:inicio -->
| Item | Ciclo 1 | Ciclo 2 | Ciclo 3 | Total |
|---|---|---|---|---|
| candidatos com linha de 1ª opção (E9) | 993 | 2140 | 2581 | 5714 |
| fora: 1ª opção em célula de município sem região de saúde na tabela oficial | 3 | 0 | 0 | 3 |
| fora: município de origem sem região de saúde na tabela oficial (TabNet) | 0 | 1 | 0 | 1 |
| fora: sem município de origem no G1 (candidato não ligado) | 55 | 77 | 69 | 201 |
| fora: sem município de origem no G1 (sem vínculo médico na competência de referência) | 20 | 30 | 38 | 88 |
| **amostra P1 (1ª opção)** | 915 | 2032 | 2474 | 5421 |
| 2ª opção na amostra P1 (M7) | 629 | 1384 | 1850 | 3863 |

- Células do conjunto de escolha: 5134 no E9; 5125 na amostra P1 (fora 9 células de município sem região de saúde na tabela oficial: 110002).
- Linhas candidato × célula no M1: 932577; conjuntos de escolha: 56.
- 2ª opção fora por cair em célula sem região de saúde: 2.
- Distância das células escolhidas igual à do G1: 5421 escolhas, diferença máxima 0,000000000 km.
- Reprodução do E9 (amostra completa, ciclos empilhados): coeficiente 0,066171 contra 0,066171 gravado; EP 0,022183 contra 0,022183.
<!-- P1:amostra:fim -->

## 3. Leitura em linguagem simples

<!-- P1:leitura:inicio -->
**P1a.** No modelo principal (M1, ciclos 1–3, 5421 candidatos), cada R$ 1 mil por mês de bolsa anunciada muda a utilidade da vaga em +0,0424 (IC 95% [−0,0027; 0,0874]; p = 0,065; p = 0,070 pela t com G − 1 gl); o intervalo de 95% contém zero: os dados não distinguem o efeito de zero com a precisão relatada. Sem a distância, na mesma amostra (M0): +0,0690 (IC [0,0247; 0,1134]); na amostra completa do E9: +0,0662 (IC [0,0227; 0,1096]). Nas outras especificações do empilhado, o IC de 95% exclui zero em M2, M4, M8, M9 e contém zero em M7; o coeficiente varia de +0,0304 a +0,0759. A leitura de P1a é sensível à especificação: só o M1 é a principal e o único com Holm, e as demais são relatadas, não escolhidas.

**P1b e P1c (R$ mil por mês de bolsa equivalentes, M1).** 100 km a menos: +4,47 (delta [−0,36; 9,29]; bootstrap [−20,09; 45,55]); mesma UF da origem: +56,67 (delta [−2,46; 115,79]; bootstrap [−251,83; 558,87]); capital (vs. interior próximo de polo): −3,67 (delta [−11,77; 4,43]; bootstrap [−44,27; 16,30]); 1 vaga imediata: +13,38 (delta [−0,10; 26,85]; bootstrap [−54,71; 126,27]). **Os intervalos são largos: o IC contém zero em 4 dos 4 atributos pelo delta e em 4 pelo bootstrap.** A DAP é uma razão: com o coeficiente da bolsa perto de zero (o IC do M1 contém zero), o intervalo fica largo e assimétrico, e o ponto não é um preço. A bolsa só varia entre R$ 10 e R$ 20 mil nos dados, então valores muito maiores que isso são extrapolação da razão, não algo que a escolha observada mostre.

**P1d.** Por ciclo (M5): ciclo 1: +0,0132 (IC [−0,0731; 0,0996]); ciclo 2: +0,1064 (IC [0,0405; 0,1722]); ciclo 3: −0,0004 (IC [−0,0662; 0,0653]). Wald da igualdade: p = 0,058 (q BKY = 0,062).

**P1e.** M6_nota bolsa_x_tercil2: −0,0336 (p = 0,129, q BKY = 0,098); M6_nota bolsa_x_tercil3: −0,0199 (p = 0,328, q BKY = 0,197); M6_nota bolsa_x_sem_pontuacao: −0,1042 (p = 0,034, q BKY = 0,047); M6_nota wald_inclinacoes_iguais: Wald (p = 0,133, q BKY = 0,098); M6_municipio bolsa_x_mesmo_municipio: +0,0594 (p = 0,003, q BKY = 0,007). Diferença com q BKY ≥ 0,05 não é evidência de heterogeneidade.

**P1f.** No logit misto (M8), a média do coeficiente da bolsa é +0,0499 (IC [0,0083; 0,0915]) e o desvio entre candidatos, 0,1750 (p < 0,001, q BKY = 0,001).

**P1g.** Nos cortes empilhados (ciclos 1–3), o modelo prevê +0,218 candidato de 1ª opção por célula (IC [−0,015; 0,451]) quando só a bolsa sobe um degrau; a RDD por célula, na mesma amostra de candidatos, observa −0,457 (IC [−1,031; 0,117]). É leitura de consistência, não teste. Os sinais são opostos, mas os dois intervalos se sobrepõem e ambos contêm zero: o salto observado não confirma nem refuta o modelo, e o P1g não é usado para validar nem para rejeitar o M1. O observado inclui quem passou a se candidatar ou deixou de se candidatar; o previsto não.

Tudo acima é escolha condicional a candidatar-se, dentro das vagas abertas; o contraste no corte mede o pacote do corte e o incentivo marginal da bolsa, não a participação no PMM-E.
<!-- P1:leitura:fim -->

## 4. P1a: coeficiente da bolsa em todas as especificações

Coeficiente por R$ 1 mil por mês de bolsa, IC 95% e p com o EP de cluster por conjunto de escolha (curso × ciclo); ao lado, o p pela t com G − 1 graus de liberdade e os EPs de máxima verossimilhança e por candidato. Holm só na linha principal (M1, ciclos empilhados), família de um teste: o p de Holm é o próprio p.

<!-- P1:bolsa:inicio -->
| Modelo | Ciclo | Especificação | Candidatos | Coef. | IC 95% | p | p (t, G−1) | EP MV | EP candidato | p Holm | Situação |
|---|---|---|---|---|---|---|---|---|---|---|---|
| E9_amostra_completa | empilhado | E9 principal reestimado na amostra completa do E9 (sensibilidade da seleção pela ligação) | 5714 | 0,0662 | [0,0227; 0,1096] | 0,003 | 0,004 | 0,0091 | 0,0093 | — |  |
| M0 | empilhado | E9 principal na amostra G1, sem distância | 5421 | 0,0690 | [0,0247; 0,1134] | 0,002 | 0,004 | 0,0094 | 0,0095 | — |  |
| M1 | empilhado | M0 + distância/100 km + mesma UF + mesma região de saúde + mesmo município + capital (principal) | 5421 | 0,0424 | [−0,0027; 0,0874] | 0,065 | 0,070 | 0,0120 | 0,0122 | 0,065 |  |
| M2 | empilhado | M1 com log(1 + distância em km) | 5421 | 0,0492 | [0,0086; 0,0897] | 0,017 | 0,021 | 0,0122 | 0,0124 | — |  |
| M3 | empilhado | M1 com distância da origem mais próxima | — | — | [—; —] | — | — | — | — | — | NAO_EXECUTADO |
| M4 | empilhado | M1 com efeito fixo de UF da vaga (no lugar da macrorregião) | 5421 | 0,0759 | [0,0282; 0,1237] | 0,002 | 0,003 | 0,0128 | 0,0130 | — |  |
| M5 | 1 | M1 por ciclo | 915 | 0,0132 | [−0,0731; 0,0996] | 0,764 | 0,768 | 0,0293 | 0,0287 | — |  |
| M5 | 2 | M1 por ciclo | 2032 | 0,1064 | [0,0405; 0,1722] | 0,002 | 0,006 | 0,0200 | 0,0208 | — |  |
| M5 | 3 | M1 por ciclo | 2474 | −0,0004 | [−0,0662; 0,0653] | 0,990 | 0,990 | 0,0179 | 0,0183 | — |  |
| M7 | empilhado | logit explodido (1ª e 2ª opção) com M1 | 5421 | 0,0304 | [−0,0150; 0,0758] | 0,190 | 0,195 | 0,0089 | 0,0099 | — |  |
| M8 | empilhado | logit misto (bolsa e distância normais; 500 sorteios Halton) (média) | 5421 | 0,0499 | [0,0083; 0,0915] | 0,019 | 0,022 | 0,0142 | 0,0143 | — |  |
| M9 | empilhado | logit aninhado por região de saúde (CIR) dentro do conjunto, com M1 | 5421 | 0,0434 | [0,0156; 0,0713] | 0,002 | 0,003 | 0,0085 | 0,0086 | — |  |

M3 não executado: a distância da origem mais próxima exige o conjunto completo de municípios de origem de cada candidato; o G1 gravou só a origem principal e a distância mais próxima das células ranqueadas (G1_distancias_opcoes.parquet), não das demais células do conjunto de escolha; o cache dos vínculos (output/rdd_bolsa/G1_cache/ e X1_cache/, fora do Git) não está neste checkout; refazê-lo exige baixar de novo a tbDadosProfissionalSus e os vínculos do CNES; nada é aproximado.

As inclinações por grupo do M6 estão na seção 8.
<!-- P1:bolsa:fim -->

## 5. P1b e P1c: disposição a pagar

<!-- P1:dap:inicio -->
| Modelo | Ciclo | Atributo | DAP (R$ mil/mês) | IC 95% delta | IC 95% bootstrap | Situação |
|---|---|---|---|---|---|---|
| M1 | empilhado | 100 km a menos | 4,47 | [−0,36; 9,29] | [−20,09; 45,55] |  |
| M1 | empilhado | mesma UF da origem | 56,67 | [−2,46; 115,79] | [−251,83; 558,87] |  |
| M1 | empilhado | capital (vs. interior próximo de polo) | −3,67 | [−11,77; 4,43] | [−44,27; 16,30] |  |
| M1 | empilhado | 1 vaga imediata | 13,38 | [−0,10; 26,85] | [−54,71; 126,27] |  |
| M4 | empilhado | 100 km a menos | 2,62 | [0,95; 4,30] | — |  |
| M4 | empilhado | mesma UF da origem | 32,81 | [12,74; 52,88] | — |  |
| M4 | empilhado | capital (vs. interior próximo de polo) | −5,24 | [−10,11; −0,37] | — |  |
| M4 | empilhado | 1 vaga imediata | 8,43 | [3,20; 13,67] | — |  |
| M7 | empilhado | 100 km a menos | 6,02 | [−3,06; 15,11] | — |  |
| M7 | empilhado | mesma UF da origem | 78,08 | [−37,46; 193,61] | — |  |
| M7 | empilhado | capital (vs. interior próximo de polo) | −3,47 | [−11,17; 4,24] | — |  |
| M7 | empilhado | 1 vaga imediata | 14,10 | [−5,98; 34,17] | — |  |
| M5 | 1 | 100 km a menos | 17,18 | [−96,95; 131,30] | — |  |
| M5 | 1 | mesma UF da origem | 187,03 | [−1031,98; 1406,04] | — |  |
| M5 | 1 | capital (vs. interior próximo de polo) | 34,55 | [−149,65; 218,74] | — |  |
| M5 | 1 | 1 vaga imediata | 24,40 | [−119,07; 167,88] | — |  |
| M5 | 2 | 100 km a menos | 1,76 | [0,70; 2,82] | — |  |
| M5 | 2 | mesma UF da origem | 22,32 | [9,66; 34,98] | — |  |
| M5 | 2 | capital (vs. interior próximo de polo) | 2,06 | [−3,39; 7,51] | — |  |
| M5 | 2 | 1 vaga imediata | 10,33 | [4,62; 16,03] | — |  |
| M5 | 3 | 100 km a menos | −394,44 | [−60392,17; 59603,30] | — |  |
| M5 | 3 | mesma UF da origem | −5480,18 | [−839512,99; 828552,63] | — |  |
| M5 | 3 | capital (vs. interior próximo de polo) | 1070,79 | [−162004,21; 164145,80] | — |  |
| M5 | 3 | 1 vaga imediata | −752,41 | [−115001,85; 113497,04] | — |  |

Bootstrap de pares por conjunto de escolha: 999 réplicas válidas de 999; fração das réplicas com coeficiente da bolsa ≤ 0: 0,040.

Leitura: os intervalos acima são largos, e a maioria contém zero no M1. Por ciclo (M5), onde o coeficiente da bolsa é próximo de zero, a razão explode e não tem leitura econômica; a DAP não é um preço de mercado.

- **100 km a menos:** quanto vale, em R$ mil/mês, ter 100 km a menos entre o município de origem e o da vaga, mantidos os demais atributos (`−β(distância/100 km) / β(bolsa)`).
- **mesma UF da origem:** quanto vale, em R$ mil/mês, a vaga ficar na UF de origem (além da distância, da região de saúde e do município) (`β(mesma UF) / β(bolsa)`).
- **capital (vs. interior próximo de polo):** quanto vale, em R$ mil/mês, a vaga ficar numa capital de UF em vez de num município do interior próximo de polo (estrato A2 de referência), mantidos porte e macrorregião (`β(capital) / β(bolsa)`).
- **1 vaga imediata:** quanto vale, em R$ mil/mês, a célula ter 1 vaga imediata em vez de só cadastro reserva (`[β(tem vaga imediata) + ln 2 · β(log(vagas imediatas + 1))] / β(bolsa)`).
<!-- P1:dap:fim -->

## 6. Atributos do modelo principal (M1)

<!-- P1:m1:inicio -->
| Termo | Coef. | IC 95% (cluster por conjunto) | p | EP MV |
|---|---|---|---|---|
| bolsa_mil | 0,0424 | [−0,0027; 0,0874] | 0,065 | 0,0120 |
| ivs_inclinacao | −0,0012 | [−0,2273; 0,2249] | 0,992 | 0,0806 |
| ivs_mudanca_inclinacao_0300 | 0,3755 | [0,0284; 0,7226] | 0,034 | 0,1254 |
| ivs_mudanca_inclinacao_0400 | −0,5326 | [−0,8184; −0,2467] | < 0,001 | 0,1133 |
| tem_vaga_imediata | 0,3530 | [0,0704; 0,6356] | 0,014 | 0,0796 |
| log_vagas_imediatas_mais_1 | 0,3088 | [0,1396; 0,4781] | < 0,001 | 0,0685 |
| log_populacao_2022 | 0,0477 | [−0,0412; 0,1367] | 0,293 | 0,0222 |
| macro_centro_oeste | 0,9133 | [0,5705; 1,2562] | < 0,001 | 0,1141 |
| macro_nordeste | 1,4685 | [1,1794; 1,7577] | < 0,001 | 0,0929 |
| macro_norte | 0,9302 | [0,5248; 1,3356] | < 0,001 | 0,1408 |
| macro_sul | 0,4146 | [0,1141; 0,7152] | 0,007 | 0,1428 |
| capital | −0,1554 | [−0,4604; 0,1495] | 0,318 | 0,0811 |
| estrato_interior_remoto | −0,2546 | [−0,4705; −0,0388] | 0,021 | 0,0681 |
| estrato_metropolitano | 0,2329 | [0,0874; 0,3785] | 0,002 | 0,0459 |
| distancia_100km | −0,1893 | [−0,2129; −0,1657] | < 0,001 | 0,0063 |
| mesma_uf | 2,4024 | [2,2777; 2,5271] | < 0,001 | 0,0563 |
| mesma_regiao_saude | 1,6452 | [1,2879; 2,0026] | < 0,001 | 0,0666 |
| mesmo_municipio | 0,7874 | [0,5193; 1,0555] | < 0,001 | 0,0728 |

Spline do IVS em unidades de 0,1 de IVS a partir de 0,300; estrato de referência: interior próximo de polo; macrorregião de referência: Sudeste; distância por 100 km.
<!-- P1:m1:fim -->

## 7. P1d: por que só o ciclo 2? (T1.3)

<!-- P1:ciclos:inicio -->
| Ciclo | Candidatos | Coef. da bolsa | IC 95% | p | q BKY |
|---|---|---|---|---|---|
| ciclo 1 | 915 | 0,0132 | [−0,0731; 0,0996] | 0,764 | 0,264 |
| ciclo 2 | 2032 | 0,1064 | [0,0405; 0,1722] | 0,002 | 0,006 |
| ciclo 3 | 2474 | −0,0004 | [−0,0662; 0,0653] | 0,990 | 0,329 |

Wald da igualdade do coeficiente da bolsa nos três ciclos (χ², 2 gl, ciclos tratados como amostras independentes): 5,69, p = 0,058, q BKY = 0,062.

Estrutura dos conjuntos por ciclo (amostra P1; descritivo, sem usar a escolha):

| Ciclo | Candidatos | Conjuntos | Células | Alternativas por candidato (média) | Fração de células com vaga imediata | Fração de células nas faixas 3 / 2 / 1 | Fração de candidatos sem pontuação |
|---|---|---|---|---|---|---|---|
| ciclo 1 | 915 | 16 | 1289 | 88,0 | 0,396 | 0,413 / 0,361 / 0,226 | 0,104 |
| ciclo 2 | 2032 | 16 | 1545 | 187,0 | 0,656 | 0,524 / 0,309 / 0,167 | 0,000 |
| ciclo 3 | 2474 | 24 | 2291 | 190,8 | 0,303 | 0,454 / 0,344 / 0,202 | 0,000 |
<!-- P1:ciclos:fim -->

Leituras candidatas, todas a relatar (doc 51, T1.3): (i) informação, porque a grade de faixas foi publicada com o quadro no ciclo 1; (ii) número de opções e composição dos candidatos; (iii) proporção de vagas imediatas. A tabela de estrutura acima descreve (ii) e (iii) sem usar a escolha; nenhuma das leituras é testada aqui.

## 8. P1e e P1f: heterogeneidade

<!-- P1:heterogeneidade:inicio -->
| Modelo | Termo | Coef. | IC 95% | p | q BKY | Inferência |
|---|---|---|---|---|---|---|
| M6_nota | bolsa_mil|tercil1 | 0,0536 | [−0,0005; 0,1076] | 0,052 | — | cluster por conjunto |
| M6_nota | bolsa_mil|tercil2 | 0,0200 | [−0,0260; 0,0659] | 0,395 | — | cluster por conjunto |
| M6_nota | bolsa_mil|tercil3 | 0,0336 | [−0,0030; 0,0703] | 0,072 | — | cluster por conjunto |
| M6_nota | bolsa_mil|sem_pontuacao | −0,0507 | [−0,1340; 0,0327] | 0,233 | — | cluster por conjunto |
| M6_nota | bolsa_x_tercil2 | −0,0336 | [−0,0770; 0,0098] | 0,129 | 0,098 | cluster por conjunto |
| M6_nota | bolsa_x_tercil3 | −0,0199 | [−0,0599; 0,0200] | 0,328 | 0,197 | cluster por conjunto |
| M6_nota | bolsa_x_sem_pontuacao | −0,1042 | [−0,2004; −0,0081] | 0,034 | 0,047 | cluster por conjunto |
| M6_nota | Wald (χ², 3 gl) = 5,59 | — | — | 0,133 | 0,098 | cluster por conjunto |
| M6_municipio | bolsa_mil|fora_do_municipio | 0,0329 | [−0,0112; 0,0770] | 0,144 | — | cluster por conjunto |
| M6_municipio | bolsa_mil|mesmo_municipio | 0,0923 | [0,0374; 0,1472] | < 0,001 | — | cluster por conjunto |
| M6_municipio | bolsa_x_mesmo_municipio | 0,0594 | [0,0201; 0,0988] | 0,003 | 0,007 | cluster por conjunto |
| M6_curso | bolsa_mil|curso01 | 0,1442 | [0,1155; 0,1728] | < 0,001 | — | MV (cluster degenerado) |
| M6_curso | bolsa_mil|curso02 | 0,0065 | [−0,0263; 0,0393] | 0,699 | — | MV (cluster degenerado) |
| M6_curso | bolsa_mil|curso06 | −0,0770 | [−0,1579; 0,0039] | 0,062 | — | MV (cluster degenerado) |
| M6_curso | bolsa_mil|curso07 | −0,0204 | [−0,0813; 0,0406] | 0,513 | — | MV (cluster degenerado) |
| M6_curso | bolsa_mil|curso08 | 0,0013 | [−0,0321; 0,0348] | 0,938 | — | MV (cluster degenerado) |
| M6_curso | bolsa_mil|curso09 | 0,0645 | [0,0029; 0,1261] | 0,040 | — | MV (cluster degenerado) |
| M6_curso | bolsa_mil|curso11 | 0,0504 | [−0,0013; 0,1021] | 0,056 | — | MV (cluster degenerado) |
| M6_curso | bolsa_mil|curso14 | 0,0250 | [−0,0183; 0,0684] | 0,258 | — | MV (cluster degenerado) |
| M6_curso | bolsa_mil|curso15 | 0,0525 | [0,0079; 0,0972] | 0,021 | — | MV (cluster degenerado) |
| M6_curso | bolsa_mil|curso17 | −0,0131 | [−0,0652; 0,0390] | 0,622 | — | MV (cluster degenerado) |
| M6_curso | bolsa_mil|curso18 | −0,0038 | [−0,0532; 0,0456] | 0,881 | — | MV (cluster degenerado) |
| M6_curso | bolsa_mil|curso24 | −0,0840 | [−0,1722; 0,0042] | 0,062 | — | MV (cluster degenerado) |
| M6_curso | bolsa_mil|demais_cursos | 0,0096 | [−0,0361; 0,0552] | 0,681 | — | MV (cluster degenerado) |
| M6_curso | bolsa_x_curso02 | −0,1377 | [−0,1677; −0,1077] | < 0,001 | — | MV (cluster degenerado) |
| M6_curso | bolsa_x_curso06 | −0,2212 | [−0,3019; −0,1405] | < 0,001 | — | MV (cluster degenerado) |
| M6_curso | bolsa_x_curso07 | −0,1645 | [−0,2245; −0,1045] | < 0,001 | — | MV (cluster degenerado) |
| M6_curso | bolsa_x_curso08 | −0,1428 | [−0,1748; −0,1109] | < 0,001 | — | MV (cluster degenerado) |
| M6_curso | bolsa_x_curso09 | −0,0797 | [−0,1403; −0,0190] | 0,010 | — | MV (cluster degenerado) |
| M6_curso | bolsa_x_curso11 | −0,0937 | [−0,1441; −0,0434] | < 0,001 | — | MV (cluster degenerado) |
| M6_curso | bolsa_x_curso14 | −0,1191 | [−0,1609; −0,0774] | < 0,001 | — | MV (cluster degenerado) |
| M6_curso | bolsa_x_curso15 | −0,0916 | [−0,1353; −0,0480] | < 0,001 | — | MV (cluster degenerado) |
| M6_curso | bolsa_x_curso17 | −0,1573 | [−0,2085; −0,1060] | < 0,001 | — | MV (cluster degenerado) |
| M6_curso | bolsa_x_curso18 | −0,1479 | [−0,1960; −0,0999] | < 0,001 | — | MV (cluster degenerado) |
| M6_curso | bolsa_x_curso24 | −0,2282 | [−0,3156; −0,1408] | < 0,001 | — | MV (cluster degenerado) |
| M6_curso | bolsa_x_demais_cursos | −0,1346 | [−0,1790; −0,0902] | < 0,001 | — | MV (cluster degenerado) |
| M6_curso | Wald (χ², 12 gl) = 461,28 | — | — | < 0,001 | — | MV (cluster degenerado) |

`bolsa_mil|grupo` é a inclinação da bolsa no grupo; `bolsa_x_grupo` é a diferença para o grupo de base. Na dimensão curso, o termo de cada curso só varia nos conjuntos do curso (no máximo 3 clusters): o EP por cluster é degenerado, a linha usa o EP de máxima verossimilhança e fica fora do BKY, como na X4.

**P1f, logit misto (M8).**

| Parâmetro | Estimativa | IC 95% | EP (cluster por conjunto) | p | q BKY | Situação |
|---|---|---|---|---|---|---|
| media_bolsa_mil | 0,0499 | [0,0083; 0,0915] | 0,0212 | 0,019 | 0,031 | EXECUTADO |
| desvio_bolsa_mil | 0,1750 | — | 0,0202 | < 0,001 | 0,001 | EXECUTADO |
| media_distancia_100km | −1,1110 | [−1,2378; −0,9841] | 0,0647 | < 0,001 | — | EXECUTADO |
| desvio_distancia_100km | 0,7064 | — | 0,0394 | < 0,001 | 0,001 | EXECUTADO |

Desvios em valor absoluto; o IC do desvio não é relatado porque H0: desvio = 0 fica na fronteira.

**M9, logit aninhado por região de saúde.** lambda = 0,449 (IC 95% [0,341; 0,556]; situação EXECUTADO); 1 = logit condicional, menos de 1 = mais substituição entre vagas da mesma região de saúde. Wald de lambda = 1: p < 0,001.
<!-- P1:heterogeneidade:fim -->

## 9. P1g: ponte com o preenchimento (T1.5)

O modelo prevê, para as células perto do corte, quantos candidatos de 1ª opção a mais a célula teria se só a sua bolsa subisse um degrau, com os candidatos e as outras células fixos. A RDD por célula mede o salto observado. A leitura é de consistência, não um teste novo; o salto observado inclui também quem passou a se candidatar ou deixou de se candidatar, e o previsto não.

<!-- P1:p1g:inicio -->
| Ciclos | Corte | Previsto por M1 | IC 95% (delta) | Observado, amostra P1 | IC 95% | Observado, todos os candidatos | IC 95% |
|---|---|---|---|---|---|---|---|
| 1+2+3 | 0,300 | +0,202 | [−0,006; 0,411] | −0,658 | [−1,362; 0,047] | −0,718 | [−1,457; 0,022] |
| 1+2+3 | 0,400 | +0,243 | [−0,030; 0,516] | −0,194 | [−1,086; 0,699] | −0,195 | [−1,126; 0,736] |
| 1+2+3 | empilhado | +0,218 | [−0,015; 0,451] | −0,457 | [−1,031; 0,117] | −0,488 | [−1,089; 0,112] |
| 1 | 0,300 | +0,107 | [−0,003; 0,217] | −0,159 | [−1,223; 0,905] | −0,240 | [−1,385; 0,906] |
| 1 | 0,400 | +0,171 | [−0,018; 0,360] | +0,470 | [−1,021; 1,960] | +0,438 | [−1,061; 1,936] |
| 1 | empilhado | +0,135 | [−0,010; 0,280] | +0,127 | [−0,784; 1,038] | +0,068 | [−0,872; 1,007] |
| 2 | 0,300 | +0,251 | [−0,012; 0,513] | −1,025 | [−2,227; 0,177] | −1,172 | [−2,433; 0,090] |
| 2 | 0,400 | +0,300 | [−0,043; 0,643] | −0,612 | [−2,027; 0,802] | −0,554 | [−2,085; 0,977] |
| 2 | empilhado | +0,269 | [−0,024; 0,562] | −0,879 | [−1,830; 0,073] | −0,932 | [−1,950; 0,085] |
| 3 | 0,300 | +0,217 | [−0,005; 0,439] | −0,647 | [−1,444; 0,150] | −0,640 | [−1,474; 0,194] |
| 3 | 0,400 | +0,252 | [−0,029; 0,534] | −0,293 | [−1,244; 0,659] | −0,319 | [−1,326; 0,687] |
| 3 | empilhado | +0,230 | [−0,013; 0,472] | −0,476 | [−1,102; 0,150] | −0,478 | [−1,133; 0,178] |
<!-- P1:p1g:fim -->

## 10. Figuras

Nenhuma figura traz texto de leitura dentro da imagem; o "Como ler" fica aqui e no campo `como_ler` de `P1_resumo.json`.

<!-- P1:figuras:inicio -->
| Arquivo | O que mostra | Como ler |
|---|---|---|
| `P1_dap.png` | DAP do M1 (P1b, P1c) com IC delta e bootstrap | Cada ponto é quanto de bolsa mensal (em R$ mil) equivale a um atributo da vaga no modelo principal; a barra mais grossa é o intervalo pelo método delta e a mais fina, o do bootstrap. Ponto à direita do zero: o atributo vale como bolsa a mais. Intervalo que cruza o zero ou é muito largo não permite ler o ponto como preço. |
| `P1_beta_por_ciclo.png` | coeficiente da bolsa por ciclo (M5) e empilhado (M1), IC 95% cluster por conjunto | Cada ponto é o peso da bolsa (por R$ 1 mil) na escolha, em cada ciclo e nos três juntos, com intervalo de 95%. Ponto acima do zero: vagas com bolsa maior foram mais escolhidas como 1ª opção. |
| `P1_ponte_P1g.png` | P1g: salto previsto por M1 contra a RDD por célula, ciclos 1–3 | Cada par compara, no corte, quantos candidatos de 1ª opção a mais por célula o modelo de escolha prevê (só mudando a bolsa) com o salto observado nos dados. É leitura de consistência, não teste: sinais opostos com intervalos que se sobrepõem não mostram que o modelo acerta nem que erra. |
<!-- P1:figuras:fim -->

## 11. Desvios e decisões de implementação

<!-- P1:desvios:inicio -->
1. **Local do resultado** (23/10/2026). O §5 do protocolo diz 'doc 57, seção P1'; o doc 57 é a síntese da onda 5 (doc 51, §5), e outros blocos escrevem em paralelo. *Resolução:* Resultados em docs/06_execucao/57a_resultados_P1_escolha.md, gerado inteiro pelo script, para entrar na síntese 57 (mesma solução do P5, doc 57e).
2. **M3 não executado** (23/10/2026). a distância da origem mais próxima exige o conjunto completo de municípios de origem de cada candidato; o G1 gravou só a origem principal e a distância mais próxima das células ranqueadas (G1_distancias_opcoes.parquet), não das demais células do conjunto de escolha; o cache dos vínculos (output/rdd_bolsa/G1_cache/ e X1_cache/, fora do Git) não está neste checkout; refazê-lo exige baixar de novo a tbDadosProfissionalSus e os vínculos do CNES; nada é aproximado. *Resolução:* Linhas do M3 com status NAO_EXECUTADO e o motivo; nenhuma distância aproximada.
3. **Células e origens sem região de saúde** (23/10/2026). A 'mesma região de saúde' de M1 exige a CIR da origem e da célula; um município do quadro (células nos três ciclos) e um município de origem não estão na tabela oficial do TabNet. *Resolução:* Como na X5: as células desse município saem do conjunto de escolha de todos os modelos da amostra P1 (M0 incluído), e saem os candidatos cuja 1ª opção estava nelas ou cuja origem não tem região; a 2ª opção nessas células sai do M7. Contagens na seção 2; nada imputado.
4. **Capital em M1** (23/10/2026). O E9 já tem o estrato A2 com base na capital; acrescentar um indicador de capital seria colinear. *Resolução:* Em M1 a base do estrato passa a ser o interior próximo de polo; o termo 'capital' é capital contra essa base, mantidos porte (log da população) e macrorregião. É reparametrização: o coeficiente da bolsa não muda por isso.
5. **Vaga imediata na DAP** (23/10/2026). O E9 tem 'tem vaga imediata' e log(vagas imediatas + 1); mudar o indicador sem mudar o log é impossível. *Resolução:* DAP da vaga imediata = célula com 1 vaga imediata contra só cadastro reserva: [β(tem) + ln 2 · β(log)] / β(bolsa).
6. **M4** (23/10/2026). A macrorregião é função da UF. *Resolução:* Em M4 o efeito fixo de UF da vaga substitui a macrorregião (UF de base: a de mais células).
7. **M6** (23/10/2026). O §3 lista três interações sem dizer se entram juntas. *Resolução:* Um modelo por dimensão (como na X4). Tercis da nota dentro do ciclo, sobre os candidatos de 1ª opção da amostra P1 com pontuação, empate no corte para baixo, sem pontuação = grupo próprio. Curso: cursos com ≥ 100 candidatos de 1ª opção na amostra empilhada, base = o de mais candidatos; inferência por cluster degenerada (o termo do curso só varia nos conjuntos dele), EP de máxima verossimilhança relatado e linhas fora do BKY, como na X4.
8. **BKY** (23/10/2026). O §4 manda BKY nas secundárias com p-valor sem listar as linhas. *Resolução:* Família única: β da bolsa por ciclo e Wald entre ciclos (P1d); termos de interação da nota e do município de origem e Wald da nota (P1e); média da bolsa e desvios da bolsa e da distância no logit misto, se convergir (P1f). p com cluster por conjunto.
9. **M8 (logit misto)** (23/10/2026). 500 sorteios por candidato em cerca de um milhão de linhas candidato × célula; o prompt do agente pede não forçar além de 30 min. *Resolução:* Gradiente analítico, teto determinístico de 300 avaliações da verossimilhança (≈ 30 min nesta máquina) para que duas execuções deem o mesmo resultado; sem convergência, status NAO_CONVERGIU com o motivo.
10. **Polimento por Newton no M8 e no M9** (23/10/2026). Na primeira execução completa o L-BFGS-B parou pelo critério de redução relativa da função com gradiente máximo de 1,2e-3 (M8) e 3,6e-4 (M9), acima da tolerância de 1e-4; as duas linhas saíram NAO_CONVERGIU. Nenhum coeficiente dessas execuções foi lido para decidir a mudança. *Resolução:* Até 6 passos de Newton com a hessiana numérica do gradiente analítico depois do L-BFGS-B, como o polimento da X5; mesma tolerância (1e-4), mesma amostra, mesma especificação. Se ainda assim não convergir, a linha fica NAO_CONVERGIU.
11. **M9 (logit aninhado)** (23/10/2026). A X5 usou gradiente numérico; aqui as linhas são do candidato (distância e origem variam por candidato). *Resolução:* Ninhos = CIR da célula dentro do conjunto de cada candidato; gradiente analítico (conferido contra o numérico no teste sintético); lambda limitado a [0,001; 50] como na X5.
12. **P1g** (23/10/2026). O §3 manda comparar com a RDD por célula de n_cand_1a_opcao, mas o modelo só prevê os candidatos da amostra P1. *Resolução:* Relatadas as duas RDDs (todos os candidatos, conferida contra o A3 gravado, e só a amostra P1); o salto previsto é a média, com peso de kernel triangular nas células da janela, da diferença de candidatos esperados com a bolsa do lado de cima e do lado de baixo do corte.
13. **T1.4 (RDD da nota média)** (23/10/2026). O doc 51 lista a RDD da nota média dos alocados e dos candidatos (F4) no T1.4; o protocolo 52 não a inclui. *Resolução:* Não reestimada aqui (o F4 está no E6); o T1.4 entra pela interação bolsa × tercil da nota (M6).
<!-- P1:desvios:fim -->

## 12. Limites

- **Escolha condicional.** O coeficiente descreve como quem se candidatou ordena as vagas abertas; não mede entrada no programa nem oferta líquida de especialistas.
- **Poucos conjuntos.** Há 56 conjuntos de escolha (curso × ciclo); o EP com cluster por conjunto é impreciso, e por isso o p pela t com G − 1 graus de liberdade vai ao lado.
- **IIA.** O logit condicional supõe independência de alternativas irrelevantes; o aninhado (M9) e o misto (M8) relaxam isso em parte.
- **Origem não é residência.** A distância vai do município do estabelecimento de origem no CNES ao da vaga.
- **DAP com bolsa fraca.** Quando o coeficiente da bolsa é pequeno perto do seu erro, a razão fica instável: o IC delta é simétrico por construção e o do bootstrap mostra a assimetria.
