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
