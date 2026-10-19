<!-- gerado por scripts/rdd_bolsa/16_estimar_E9_escolha.py; não editar à mão -->

**Tabela 1. Amostra por ciclo (conjunto principal, logit condicional da 1ª opção).**

| ciclo | candidatos | conjuntos | alternativas | alternativas por conjunto (mín.–mediana–máx.) | candidatos sem linha de 1ª opção (excluídos) |
|---|---:|---:|---:|---|---:|
| 1 | 993 | 16 | 1295 | 22–57,5–188 | 0 |
| 2 | 2140 | 16 | 1547 | 15–78,5–333 | 39 |
| 3 | 2581 | 24 | 2292 | 4–59,5–438 | 23 |
| empilhado | 5714 | 56 | 5134 | 4–60,5–438 | 62 |

**Tabela 2. Bolsa linear: coeficiente (por R$ 1 mil), razão de chances por +R$ 5 mil e variação média da probabilidade de escolha da célula (p.p.) quando a sua bolsa sobe R$ 5 mil.** EP e IC 95% com cluster por conjunto de escolha; p pela normal e pela t com G − 1 gl.

| ciclo | modelo | conjunto | spline | coef. | EP | IC 95% | p | p (t, G−1) | RC por +R$ 5 mil [IC 95%] | Δ prob. média, p.p. [IC 95%] | prob. média base, p.p. |
|---|---|---|---|---:|---:|---|---:|---:|---|---|---:|
| 1 | condicional | principal | linear | 0,0653 | 0,0440 | [−0,0208; 0,1515] | 0,137 | 0,158 | 1,386 [0,901; 2,133] | 0,4262 [−0,2264; 1,0788] | 1,1365 |
| 2 | condicional | principal | linear | 0,1331 | 0,0282 | [0,0778; 0,1884] | < 0,001 | < 0,001 | 1,945 [1,475; 2,566] | 0,4936 [0,2162; 0,7710] | 0,5385 |
| 3 | condicional | principal | linear | 0,0097 | 0,0318 | [−0,0527; 0,0720] | 0,761 | 0,764 | 1,049 [0,768; 1,433] | 0,0257 [−0,1439; 0,1952] | 0,5272 |
| empilhado | condicional | principal | linear | 0,0662 | 0,0222 | [0,0227; 0,1096] | 0,003 | 0,004 | 1,392 [1,120; 1,730] | 0,2249 [0,0524; 0,3974] | 0,5864 |
| 1 | condicional | principal | quadrático | 0,0828 | 0,0479 | [−0,0111; 0,1767] | 0,084 | 0,104 | 1,513 [0,946; 2,419] | 0,5641 [−0,2073; 1,3356] | 1,1365 |
| 2 | condicional | principal | quadrático | 0,1361 | 0,0206 | [0,0958; 0,1765] | < 0,001 | < 0,001 | 1,975 [1,614; 2,417] | 0,5090 [0,3036; 0,7143] | 0,5385 |
| 3 | condicional | principal | quadrático | 0,0546 | 0,0349 | [−0,0138; 0,1230] | 0,118 | 0,131 | 1,314 [0,933; 1,849] | 0,1620 [−0,0688; 0,3928] | 0,5272 |
| empilhado | condicional | principal | quadrático | 0,0868 | 0,0192 | [0,0490; 0,1245] | < 0,001 | < 0,001 | 1,543 [1,278; 1,863] | 0,3107 [0,1456; 0,4758] | 0,5864 |
| 1 | condicional | sensibilidade | linear | 0,0882 | 0,0647 | [−0,0386; 0,2150] | 0,173 | 0,193 | 1,554 [0,825; 2,930] | 1,2560 [−0,9142; 3,4261] | 2,4219 |
| 2 | condicional | sensibilidade | linear | 0,1336 | 0,0322 | [0,0705; 0,1968] | < 0,001 | < 0,001 | 1,951 [1,423; 2,675] | 0,6797 [0,2469; 1,1126] | 0,7420 |
| 3 | condicional | sensibilidade | linear | 0,0745 | 0,0270 | [0,0215; 0,1275] | 0,006 | 0,012 | 1,451 [1,113; 1,892] | 0,8259 [0,1342; 1,5175] | 1,9563 |
| empilhado | condicional | sensibilidade | linear | 0,1101 | 0,0229 | [0,0653; 0,1549] | < 0,001 | < 0,001 | 1,734 [1,386; 2,170] | 0,7413 [0,3565; 1,1261] | 1,0619 |
| 1 | condicional | sensibilidade | quadrático | 0,0967 | 0,0611 | [−0,0231; 0,2164] | 0,114 | 0,134 | 1,622 [0,891; 2,951] | 1,4037 [−0,7193; 3,5267] | 2,4219 |
| 2 | condicional | sensibilidade | quadrático | 0,1437 | 0,0213 | [0,1021; 0,1854] | < 0,001 | < 0,001 | 2,052 [1,666; 2,527] | 0,7507 [0,4517; 1,0496] | 0,7420 |
| 3 | condicional | sensibilidade | quadrático | 0,1239 | 0,0358 | [0,0537; 0,1942] | < 0,001 | 0,002 | 1,858 [1,308; 2,640] | 1,5412 [0,4111; 2,6713] | 1,9563 |
| empilhado | condicional | sensibilidade | quadrático | 0,1302 | 0,0175 | [0,0959; 0,1645] | < 0,001 | < 0,001 | 1,918 [1,615; 2,276] | 0,9215 [0,5996; 1,2434] | 1,0619 |
| 1 | explodido | principal | linear | 0,0732 | 0,0375 | [−0,0004; 0,1467] | 0,051 | 0,070 | 1,442 [0,998; 2,083] | 0,4873 [−0,0917; 1,0664] | 1,1365 |
| 2 | explodido | principal | linear | 0,1179 | 0,0358 | [0,0477; 0,1881] | < 0,001 | 0,005 | 1,803 [1,269; 2,561] | 0,4203 [0,0930; 0,7475] | 0,5385 |
| 3 | explodido | principal | linear | −0,0013 | 0,0297 | [−0,0595; 0,0570] | 0,966 | 0,966 | 0,994 [0,743; 1,329] | −0,0033 [−0,1534; 0,1468] | 0,5272 |
| empilhado | explodido | principal | linear | 0,0561 | 0,0231 | [0,0109; 0,1013] | 0,015 | 0,018 | 1,324 [1,056; 1,659] | 0,1858 [0,0149; 0,3567] | 0,5864 |
| 1 | explodido | principal | quadrático | 0,0901 | 0,0344 | [0,0227; 0,1575] | 0,009 | 0,019 | 1,569 [1,120; 2,198] | 0,6260 [0,0514; 1,2006] | 1,1365 |
| 2 | explodido | principal | quadrático | 0,1138 | 0,0308 | [0,0534; 0,1742] | < 0,001 | 0,002 | 1,766 [1,306; 2,389] | 0,4012 [0,1249; 0,6774] | 0,5385 |
| 3 | explodido | principal | quadrático | 0,0417 | 0,0354 | [−0,0277; 0,1111] | 0,239 | 0,251 | 1,232 [0,871; 1,743] | 0,1198 [−0,1002; 0,3398] | 0,5272 |
| empilhado | explodido | principal | quadrático | 0,0712 | 0,0207 | [0,0306; 0,1119] | < 0,001 | 0,001 | 1,428 [1,165; 1,749] | 0,2450 [0,0799; 0,4102] | 0,5864 |

**Tabela 3. Principal (condicional, conjunto principal, spline linear, bolsa linear): os três EPs do coeficiente da bolsa.**

| ciclo | coef. | EP cluster por conjunto (G) | EP máxima verossimilhança | EP cluster por candidato |
|---|---:|---:|---:|---:|
| 1 | 0,0653 | 0,0440 (16) | 0,0232 | 0,0233 |
| 2 | 0,1331 | 0,0282 (16) | 0,0151 | 0,0153 |
| 3 | 0,0097 | 0,0318 (24) | 0,0135 | 0,0137 |
| empilhado | 0,0662 | 0,0222 (56) | 0,0091 | 0,0093 |

**Tabela 4. Degraus por corte (cada degrau = +R$ 5 mil; coeficiente em log da razão de chances) e teste de igualdade.** EP cluster por conjunto.

| ciclo | modelo | conjunto | spline | degrau 0,300 [IC 95%] | degrau 0,400 [IC 95%] | diferença | p igualdade | p igualdade (t, G−1) |
|---|---|---|---|---|---|---:|---:|---:|
| 1 | condicional | principal | linear | 0,126 [−0,549; 0,801] | 0,530 [−0,038; 1,098] | −0,404 | 0,369 | 0,383 |
| 2 | condicional | principal | linear | 0,605 [0,376; 0,834] | 0,734 [0,293; 1,176] | −0,130 | 0,553 | 0,562 |
| 3 | condicional | principal | linear | −0,269 [−0,566; 0,029] | 0,587 [0,188; 0,986] | −0,856 | < 0,001 | < 0,001 |
| empilhado | condicional | principal | linear | 0,115 [−0,134; 0,364] | 0,621 [0,349; 0,892] | −0,506 | 0,002 | 0,003 |
| 1 | condicional | principal | quadrático | 0,342 [−0,418; 1,102] | 0,479 [−0,379; 1,337] | −0,137 | 0,840 | 0,843 |
| 2 | condicional | principal | quadrático | 0,754 [0,358; 1,151] | 0,631 [0,361; 0,901] | 0,123 | 0,644 | 0,651 |
| 3 | condicional | principal | quadrático | 0,330 [−0,133; 0,792] | 0,221 [−0,215; 0,658] | 0,108 | 0,715 | 0,719 |
| empilhado | condicional | principal | quadrático | 0,436 [0,173; 0,700] | 0,432 [0,178; 0,686] | 0,004 | 0,982 | 0,982 |
| 1 | condicional | sensibilidade | linear | 0,326 [−0,580; 1,232] | 0,558 [0,090; 1,026] | −0,232 | 0,515 | 0,525 |
| 2 | condicional | sensibilidade | linear | 0,564 [0,311; 0,816] | 0,769 [0,334; 1,204] | −0,205 | 0,222 | 0,241 |
| 3 | condicional | sensibilidade | linear | 0,116 [−0,146; 0,378] | 0,826 [0,225; 1,427] | −0,710 | 0,022 | 0,032 |
| empilhado | condicional | sensibilidade | linear | 0,358 [0,113; 0,603] | 0,769 [0,463; 1,075] | −0,410 | 0,012 | 0,016 |
| 1 | condicional | sensibilidade | quadrático | 0,715 [−0,299; 1,730] | 0,274 [−0,142; 0,690] | 0,441 | 0,349 | 0,364 |
| 2 | condicional | sensibilidade | quadrático | 0,774 [0,316; 1,233] | 0,685 [0,375; 0,995] | 0,089 | 0,785 | 0,789 |
| 3 | condicional | sensibilidade | quadrático | 0,844 [0,523; 1,165] | 0,410 [−0,186; 1,006] | 0,434 | 0,222 | 0,235 |
| empilhado | condicional | sensibilidade | quadrático | 0,716 [0,409; 1,024] | 0,604 [0,331; 0,876] | 0,113 | 0,638 | 0,640 |
| 1 | explodido | principal | linear | 0,220 [−0,338; 0,777] | 0,504 [0,130; 0,878] | −0,284 | 0,355 | 0,370 |
| 2 | explodido | principal | linear | 0,529 [0,241; 0,818] | 0,654 [0,151; 1,157] | −0,125 | 0,561 | 0,570 |
| 3 | explodido | principal | linear | −0,327 [−0,596; −0,058] | 0,546 [0,099; 0,993] | −0,873 | < 0,001 | < 0,001 |
| empilhado | explodido | principal | linear | 0,063 [−0,193; 0,319] | 0,565 [0,279; 0,851] | −0,503 | 0,002 | 0,004 |
| 1 | explodido | principal | quadrático | 0,534 [0,022; 1,047] | 0,379 [−0,121; 0,880] | 0,155 | 0,686 | 0,692 |
| 2 | explodido | principal | quadrático | 0,552 [0,169; 0,935] | 0,580 [0,292; 0,868] | −0,028 | 0,836 | 0,839 |
| 3 | explodido | principal | quadrático | 0,196 [−0,248; 0,640] | 0,220 [−0,330; 0,769] | −0,023 | 0,950 | 0,950 |
| empilhado | explodido | principal | quadrático | 0,318 [0,069; 0,567] | 0,387 [0,104; 0,670] | −0,069 | 0,699 | 0,701 |

**Tabela 5. Colinearidade da bolsa (principal, spline linear): R² da bolsa contra o spline e os controles, com X centrado dentro do conjunto de escolha.**

| ciclo | R² | VIF | nº de condição de X centrado |
|---|---:|---:|---:|
| 1 | 0,864 | 7,33 | 43,4 |
| 2 | 0,868 | 7,56 | 37,0 |
| 3 | 0,859 | 7,09 | 37,7 |
| empilhado | 0,860 | 7,15 | 36,4 |

**Robustez pós-auditoria (tabelas 6 a 10).** Pós-resultado e fora do protocolo; linhas `ROBUSTEZ_POS_AUDITORIA` com `no_protocolo = False`. Não substituem as tabelas 1 a 5.

**Tabela 6. Inferência com poucos clusters (principal: condicional, conjunto principal, spline linear, bolsa linear).** p do score bootstrap de Kline–Santos sob H0: coef. = 0; Rademacher por enumeração completa quando G ≤ 24, senão 199999 sorteios; Webb sempre por sorteio. CV3 com IC e p pela t com G − 1 gl. IC por inversão do score bootstrap Rademacher.

| ciclo | cluster | G | coef. | EP CR1 | p CR1 | EP CV3 | p CV3 | p score (Rademacher) | p score (Webb) | IC 95% por inversão |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | conjunto | 16 | 0,0653 | 0,0440 | 0,137 | 0,0466 | 0,181 | 0,195 | 0,197 | — |
| 2 | conjunto | 16 | 0,1331 | 0,0282 | < 0,001 | 0,0327 | < 0,001 | < 0,001 | 0,002 | [0,0682; 0,1882] |
| 3 | conjunto | 24 | 0,0097 | 0,0318 | 0,761 | 0,0385 | 0,804 | 0,825 | 0,826 | — |
| empilhado | conjunto | 56 | 0,0662 | 0,0222 | 0,003 | 0,0236 | 0,007 | 0,010 | 0,010 | [0,0159; 0,1064] |
| empilhado | curso | 24 | 0,0662 | 0,0256 | 0,010 | 0,0300 | 0,037 | 0,042 | 0,047 | [0,0023; 0,1089] |

**Tabela 7. Forma funcional e conjuntos restritos a janelas em torno dos cortes (condicional, bolsa linear).** EP cluster por conjunto. Janela: só células com |IVS − corte| ≤ h e candidatos com a 1ª opção nelas.

| ciclo | especificação | coef. | EP | IC 95% | p | candidatos | alternativas |
|---|---|---:|---:|---|---:|---:|---:|
| 1 | spline cúbico | 0,0462 | 0,0340 | [−0,0204; 0,1129] | 0,174 | 993 | 1295 |
| 2 | spline cúbico | 0,0642 | 0,0371 | [−0,0084; 0,1369] | 0,083 | 2140 | 1547 |
| 3 | spline cúbico | −0,0175 | 0,0537 | [−0,1229; 0,0878] | 0,744 | 2581 | 2292 |
| empilhado | spline cúbico | 0,0326 | 0,0266 | [−0,0194; 0,0847] | 0,220 | 5714 | 5134 |
| 1 | spline linear, nós a cada 0,05 | 0,0629 | 0,0425 | [−0,0203; 0,1462] | 0,138 | 993 | 1295 |
| 2 | spline linear, nós a cada 0,05 | 0,1071 | 0,0184 | [0,0711; 0,1431] | < 0,001 | 2140 | 1547 |
| 3 | spline linear, nós a cada 0,05 | 0,0475 | 0,0363 | [−0,0237; 0,1186] | 0,191 | 2581 | 2292 |
| empilhado | spline linear, nós a cada 0,05 | 0,0691 | 0,0178 | [0,0341; 0,1041] | < 0,001 | 5714 | 5134 |
| 1 | janela ±0,100, spline linear | 0,0834 | 0,0460 | [−0,0068; 0,1736] | 0,070 | 894 | 1125 |
| 2 | janela ±0,100, spline linear | 0,1265 | 0,0231 | [0,0812; 0,1718] | < 0,001 | 1986 | 1321 |
| 3 | janela ±0,100, spline linear | 0,0235 | 0,0380 | [−0,0509; 0,0979] | 0,536 | 2443 | 1964 |
| empilhado | janela ±0,100, spline linear | 0,0716 | 0,0207 | [0,0310; 0,1123] | < 0,001 | 5323 | 4410 |
| 1 | janela ±0,100, spline cúbico | 0,0009 | 0,0420 | [−0,0814; 0,0832] | 0,983 | 894 | 1125 |
| 2 | janela ±0,100, spline cúbico | 0,0567 | 0,0639 | [−0,0685; 0,1819] | 0,375 | 1986 | 1321 |
| 3 | janela ±0,100, spline cúbico | −0,0438 | 0,0462 | [−0,1344; 0,0469] | 0,344 | 2443 | 1964 |
| empilhado | janela ±0,100, spline cúbico | 0,0105 | 0,0307 | [−0,0497; 0,0708] | 0,732 | 5323 | 4410 |
| 1 | janela ±0,050, spline linear | 0,0515 | 0,0483 | [−0,0432; 0,1461] | 0,286 | 736 | 892 |
| 2 | janela ±0,050, spline linear | 0,0946 | 0,0282 | [0,0393; 0,1499] | < 0,001 | 1722 | 983 |
| 3 | janela ±0,050, spline linear | 0,0045 | 0,0343 | [−0,0627; 0,0717] | 0,895 | 2095 | 1508 |
| empilhado | janela ±0,050, spline linear | 0,0404 | 0,0186 | [0,0040; 0,0768] | 0,030 | 4553 | 3383 |
| 1 | janela ±0,050, spline cúbico | −0,0089 | 0,1219 | [−0,2477; 0,2299] | 0,942 | 736 | 892 |
| 2 | janela ±0,050, spline cúbico | 0,0943 | 0,0984 | [−0,0986; 0,2872] | 0,338 | 1722 | 983 |
| 3 | janela ±0,050, spline cúbico | −0,0180 | 0,0618 | [−0,1390; 0,1031] | 0,771 | 2095 | 1508 |
| empilhado | janela ±0,050, spline cúbico | 0,0370 | 0,0514 | [−0,0637; 0,1378] | 0,471 | 4553 | 3383 |
| 1 | janela ±0,025, spline linear | 0,0439 | 0,0649 | [−0,0832; 0,1710] | 0,498 | 379 | 448 |
| 2 | janela ±0,025, spline linear | 0,1325 | 0,0612 | [0,0127; 0,2524] | 0,030 | 982 | 539 |
| 3 | janela ±0,025, spline linear | 0,0149 | 0,0284 | [−0,0408; 0,0705] | 0,601 | 1341 | 861 |
| empilhado | janela ±0,025, spline linear | 0,0533 | 0,0304 | [−0,0062; 0,1128] | 0,079 | 2702 | 1848 |
| 1 | janela ±0,025, spline cúbico | 0,3862 | 0,0787 | [0,2319; 0,5405] | < 0,001 | 379 | 448 |
| 2 | janela ±0,025, spline cúbico | 0,1269 | 0,0603 | [0,0086; 0,2452] | 0,035 | 982 | 539 |
| 3 | janela ±0,025, spline cúbico | 0,0715 | 0,1066 | [−0,1374; 0,2805] | 0,502 | 1341 | 861 |
| empilhado | janela ±0,025, spline cúbico | 0,1653 | 0,0515 | [0,0644; 0,2663] | 0,001 | 2702 | 1848 |

**Tabela 8. Cortes placebo** (degrau falso e nó no corte falso, com a bolsa verdadeira no modelo; cortes de 0,190 a 0,510 a cada 0,010, sem 0,290–0,310 e 0,390–0,410). t com EP cluster por conjunto. p por posto = (1 + nº de |t placebo| ≥ |t real|)/(1 + N).

| ciclo | N | média do t placebo | dp do t placebo | fração com |t| > 1,96 | máx. |t| placebo | t real | nº |t placebo| ≥ |t real| | p por posto |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 27 | −0,38 | 1,44 | 0,185 | 3,18 | 1,49 | 9 | 0,357 |
| 2 | 27 | −0,30 | 1,52 | 0,148 | 3,68 | 4,71 | 0 | 0,036 |
| 3 | 27 | −0,23 | 1,86 | 0,296 | 4,05 | 0,30 | 23 | 0,857 |
| empilhado | 27 | −0,50 | 1,41 | 0,148 | 3,65 | 2,98 | 2 | 0,107 |

**Tabela 9. Heterogeneidade entre ciclos (principal).**

| teste | estimativa | EP | IC 95% | p |
|---|---:|---:|---|---:|
| ciclos 1 e 3 empilhados, coef. da bolsa (G = 40) | 0,0266 | 0,0240 | [−0,0204; 0,0735] | 0,267 |
| Q de Cochran, ciclos 1, 2 e 3 (2 gl) | 8,50 | — | — | 0,014 |
| z, ciclo 2 menos ciclo 3 | 2,90 | 0,0425 | — | 0,004 |

**Tabela 10. Empilhado: EP com cluster por conjunto (protocolo) e por curso (robustez).**

| modelo | conjunto | especificação | termo | coef. | EP conjunto (G) | p conjunto | EP curso (G) | p curso |
|---|---|---|---|---:|---:|---:|---:|---:|
| condicional | principal | spline_linear__bolsa_linear | bolsa_mil | 0,0662 | 0,0222 (56) | 0,003 | 0,0256 (24) | 0,010 |
| condicional | principal | spline_quadratico__bolsa_linear | bolsa_mil | 0,0868 | 0,0192 (56) | < 0,001 | 0,0269 (24) | 0,001 |
| condicional | principal | spline_linear__degraus_por_corte | degrau_0300 | 0,1149 | 0,1269 (56) | 0,365 | 0,1114 (24) | 0,302 |
| condicional | principal | spline_linear__degraus_por_corte | degrau_0400 | 0,6207 | 0,1386 (56) | < 0,001 | 0,1887 (24) | 0,001 |
| condicional | principal | spline_quadratico__degraus_por_corte | degrau_0300 | 0,4360 | 0,1344 (56) | 0,001 | 0,1524 (24) | 0,004 |
| condicional | principal | spline_quadratico__degraus_por_corte | degrau_0400 | 0,4320 | 0,1296 (56) | < 0,001 | 0,1505 (24) | 0,004 |
| condicional | sensibilidade | spline_linear__bolsa_linear | bolsa_mil | 0,1101 | 0,0229 (55) | < 0,001 | 0,0247 (24) | < 0,001 |
| condicional | sensibilidade | spline_quadratico__bolsa_linear | bolsa_mil | 0,1302 | 0,0175 (55) | < 0,001 | 0,0225 (24) | < 0,001 |
| condicional | sensibilidade | spline_linear__degraus_por_corte | degrau_0300 | 0,3585 | 0,1250 (55) | 0,004 | 0,1047 (24) | < 0,001 |
| condicional | sensibilidade | spline_linear__degraus_por_corte | degrau_0400 | 0,7688 | 0,1562 (55) | < 0,001 | 0,1975 (24) | < 0,001 |
| condicional | sensibilidade | spline_quadratico__degraus_por_corte | degrau_0300 | 0,7164 | 0,1569 (55) | < 0,001 | 0,1252 (24) | < 0,001 |
| condicional | sensibilidade | spline_quadratico__degraus_por_corte | degrau_0400 | 0,6036 | 0,1391 (55) | < 0,001 | 0,1724 (24) | < 0,001 |
| explodido | principal | spline_linear__bolsa_linear | bolsa_mil | 0,0561 | 0,0231 (56) | 0,015 | 0,0258 (24) | 0,030 |
| explodido | principal | spline_quadratico__bolsa_linear | bolsa_mil | 0,0712 | 0,0207 (56) | < 0,001 | 0,0278 (24) | 0,010 |
| explodido | principal | spline_linear__degraus_por_corte | degrau_0300 | 0,0627 | 0,1307 (56) | 0,631 | 0,1075 (24) | 0,560 |
| explodido | principal | spline_linear__degraus_por_corte | degrau_0400 | 0,5652 | 0,1458 (56) | < 0,001 | 0,2057 (24) | 0,006 |
| explodido | principal | spline_quadratico__degraus_por_corte | degrau_0300 | 0,3179 | 0,1271 (56) | 0,012 | 0,1394 (24) | 0,023 |
| explodido | principal | spline_quadratico__degraus_por_corte | degrau_0400 | 0,3872 | 0,1443 (56) | 0,007 | 0,1917 (24) | 0,043 |
