# Resultados exploratórios pós-síntese (X1–X6)

## X4 — Heterogeneidade da escolha (E9)

> **Data:** 19/10/2026.<br>
> **Estatuto:** `EXPLORATORIO_POS_SINTESE` (protocolo
> [`45`](45_protocolo_exploratorio_pos_sintese.md), §2 e §3). Pós-resultado: nada
> aqui é teste confirmatório, e nada muda o protocolo 40, o E9 ou o Holm das
> primárias.<br>
> **Script:** `scripts/rdd_bolsa/19_escolha_heterogeneidade.py` (importa do
> `16_estimar_E9_escolha.py` a preparação dos dados, a verossimilhança, o
> sanduíche por cluster e o score bootstrap).<br>
> **Saídas:** `output/rdd_bolsa/X4_estimativas.csv`, `X4X5_resumo.json`
> (entradas com SHA-256, conferências, decisões, desvios) e
> `X4X5_tabelas_relato.md`.<br>
> **Testes:** `tests/test_x4_x5_escolha.py` (recuperação de interações em dados
> sintéticos, invariantes das saídas, blocos abaixo iguais aos gerados, frases
> desta seção conferidas contra os CSVs).

Nenhum número desta seção foi digitado: as tabelas são copiadas do bloco X4 de
`output/rdd_bolsa/X4X5_tabelas_relato.md`, e um teste confere que são idênticas
e que, fora delas, só aparecem números do protocolo.

### Especificação

- **Base:** o principal do E9 (logit condicional da 1a opção, conjunto
  principal, spline linear contínuo com nós em 0,300 e 0,400, bolsa linear em
  R$ mil). O script reestima esse modelo e para se o coeficiente e o EP da bolsa
  não reproduzirem `E9_estimativas.csv` (conferência em `X4X5_resumo.json`).
- **Interações**, uma dimensão por modelo, por ciclo e empilhado; bolsa (grupo
  de base) mais bolsa × grupo para os demais:
  - (a) **tercil da pontuação** do candidato dentro do ciclo (a pontuação do
    F4), calculado antes da estimação; empate no corte vai para o tercil de
    baixo (Tabela X4.3). Quem não tem pontuação (os "SEM PRÉ-REQUISITO" do ciclo
    1) é um grupo próprio, sem imputação. Como a pontuação é do candidato, cada
    conjunto é replicado por grupo de candidato; sem interação, a
    verossimilhança é a do E9 (conferido no script e no teste);
  - (b) **curso**, com ao menos 100 candidatos de 1a opção na amostra do
    modelo; os demais juntos; base = grupo com mais candidatos;
  - (c) **escassez pré-programa** da especialidade no município: vínculos das
    CBO do curso (ponte curso–CBO) por 10 mil habitantes (Censo 2022), média de
    202406 a 202506 no painel CNES nacional; tercis dentro do conjunto de
    escolha (tercil 1 = mais escasso). Os indicadores de tercil também entram
    como atributo da célula. Os cursos 17 a 24 não têm ponte e formam o grupo
    `sem_ponte_curso_cbo`;
  - (d) **estrato territorial** (base capital, como no E9).
- **Inferência:** cluster por conjunto (principal do E9), por curso (no
  empilhado; por ciclo coincide com o conjunto), máxima verossimilhança (MV) e
  cluster por candidato; score bootstrap de Kline–Santos dos termos de
  interação; Wald da igualdade de todas as inclinações. q de
  Benjamini–Krieger–Yekutieli dentro do X4, sobre interações e Wald, com o p de
  cluster por conjunto.
- **Curso:** o termo próprio de um curso só varia nos conjuntos desse curso. Com
  cluster por conjunto ou por curso, o G efetivo de cada termo é 1 por ciclo
  (coluna `g_efetivo_conjunto`), e o EP por cluster não tem sentido. Essas
  linhas ficam marcadas (`inferencia_cluster_degenerada`), fora do BKY, com o EP
  de MV e o de cluster por candidato ao lado.

### Resultados

<!-- X4_TABELAS_INICIO -->
<!-- gerado por scripts/rdd_bolsa/19_escolha_heterogeneidade.py; não editar à mão -->

**Tabela X4.1. Inclinação da bolsa por grupo (coef. por R$ 1 mil; logit condicional, principal do E9 com interações).** EP e IC 95% com cluster por conjunto; p pela normal. Na dimensão curso, o EP por cluster é degenerado (ver nota) e o p de máxima verossimilhança vem ao lado.

| dimensão | ciclo | grupo | candidatos | coef. | IC 95% | p | p (MV) |
|---|---|---|---:|---:|---|---:|---:|
| nota_tercil | 1 | tercil1 | 323 | 0,0450 | [−0,0376; 0,1276] | 0,286 | 0,087 |
| nota_tercil | 1 | tercil2 | 284 | 0,0695 | [−0,0203; 0,1593] | 0,129 | 0,010 |
| nota_tercil | 1 | tercil3 | 272 | 0,1001 | [−0,0041; 0,2044] | 0,060 | < 0,001 |
| nota_tercil | 1 | sem_pontuacao | 114 | 0,0354 | [−0,0722; 0,1429] | 0,519 | 0,296 |
| nota_tercil | 2 | tercil1 | 1372 | 0,1455 | [0,0898; 0,2012] | < 0,001 | < 0,001 |
| nota_tercil | 2 | tercil2 | 120 | 0,1027 | [0,0029; 0,2025] | 0,044 | < 0,001 |
| nota_tercil | 2 | tercil3 | 648 | 0,1107 | [0,0679; 0,1534] | < 0,001 | < 0,001 |
| nota_tercil | 3 | tercil1 | 1635 | 0,0137 | [−0,0532; 0,0806] | 0,688 | 0,330 |
| nota_tercil | 3 | tercil2 | 184 | −0,0032 | [−0,0931; 0,0866] | 0,944 | 0,900 |
| nota_tercil | 3 | tercil3 | 762 | 0,0016 | [−0,0555; 0,0586] | 0,957 | 0,926 |
| nota_tercil | empilhado | tercil1 | 3330 | 0,0756 | [0,0275; 0,1237] | 0,002 | < 0,001 |
| nota_tercil | empilhado | tercil2 | 588 | 0,0383 | [−0,0074; 0,0840] | 0,100 | 0,008 |
| nota_tercil | empilhado | tercil3 | 1682 | 0,0609 | [0,0226; 0,0992] | 0,002 | < 0,001 |
| nota_tercil | empilhado | sem_pontuacao | 114 | −0,0145 | [−0,0716; 0,0426] | 0,618 | 0,600 |
| curso | 1 | curso02 | 106 | 0,0880 | [−0,0108; 0,1868] | 0,081 | 0,008 |
| curso | 1 | curso08 | 185 | 0,0362 | [−0,0632; 0,1356] | 0,475 | 0,203 |
| curso | 1 | curso14 | 115 | 0,1013 | [−0,0010; 0,2036] | 0,052 | 0,002 |
| curso | 1 | demais_cursos | 587 | 0,0656 | [−0,0347; 0,1660] | 0,200 | 0,008 |
| curso | 2 | curso01 | 510 | 0,2073 | [0,1844; 0,2302] | < 0,001 | < 0,001 |
| curso | 2 | curso02 | 408 | 0,1005 | [0,0791; 0,1219] | < 0,001 | < 0,001 |
| curso | 2 | curso07 | 103 | 0,0566 | [0,0345; 0,0788] | < 0,001 | 0,101 |
| curso | 2 | curso08 | 400 | 0,1210 | [0,0933; 0,1487] | < 0,001 | < 0,001 |
| curso | 2 | curso11 | 119 | 0,0950 | [0,0714; 0,1185] | < 0,001 | < 0,001 |
| curso | 2 | curso14 | 162 | 0,1093 | [0,0891; 0,1295] | < 0,001 | < 0,001 |
| curso | 2 | curso15 | 139 | 0,1306 | [0,1018; 0,1593] | < 0,001 | < 0,001 |
| curso | 2 | demais_cursos | 299 | 0,1286 | [0,0639; 0,1934] | < 0,001 | < 0,001 |
| curso | 3 | curso01 | 597 | 0,0716 | [0,0431; 0,1000] | < 0,001 | < 0,001 |
| curso | 3 | curso02 | 349 | 0,0326 | [0,0026; 0,0627] | 0,033 | 0,100 |
| curso | 3 | curso08 | 222 | −0,0197 | [−0,0634; 0,0240] | 0,378 | 0,392 |
| curso | 3 | curso17 | 155 | −0,0112 | [−0,0427; 0,0204] | 0,487 | 0,613 |
| curso | 3 | curso18 | 216 | −0,0186 | [−0,0515; 0,0144] | 0,269 | 0,407 |
| curso | 3 | curso24 | 230 | −0,1697 | [−0,2054; −0,1341] | < 0,001 | < 0,001 |
| curso | 3 | demais_cursos | 812 | −0,0049 | [−0,0440; 0,0343] | 0,808 | 0,774 |
| curso | empilhado | curso01 | 1200 | 0,1367 | [0,0835; 0,1899] | < 0,001 | < 0,001 |
| curso | empilhado | curso02 | 863 | 0,0774 | [0,0490; 0,1058] | < 0,001 | < 0,001 |
| curso | empilhado | curso06 | 206 | −0,0323 | [−0,1205; 0,0559] | 0,474 | 0,246 |
| curso | empilhado | curso07 | 206 | 0,0149 | [−0,0611; 0,0908] | 0,701 | 0,528 |
| curso | empilhado | curso08 | 807 | 0,0486 | [−0,0015; 0,0988] | 0,057 | < 0,001 |
| curso | empilhado | curso09 | 139 | 0,1003 | [0,0107; 0,1900] | 0,028 | < 0,001 |
| curso | empilhado | curso11 | 249 | 0,0469 | [0,0089; 0,0849] | 0,016 | 0,023 |
| curso | empilhado | curso14 | 372 | 0,0660 | [0,0311; 0,1009] | < 0,001 | < 0,001 |
| curso | empilhado | curso15 | 318 | 0,0681 | [0,0235; 0,1127] | 0,003 | < 0,001 |
| curso | empilhado | curso16 | 121 | 0,0233 | [−0,0456; 0,0923] | 0,507 | 0,474 |
| curso | empilhado | curso17 | 155 | 0,0430 | [0,0131; 0,0729] | 0,005 | 0,029 |
| curso | empilhado | curso18 | 216 | 0,0305 | [0,0028; 0,0583] | 0,031 | 0,126 |
| curso | empilhado | curso24 | 230 | −0,1174 | [−0,1520; −0,0829] | < 0,001 | < 0,001 |
| curso | empilhado | demais_cursos | 632 | 0,0309 | [−0,0109; 0,0727] | 0,147 | 0,062 |
| escassez_tercil | 1 | tercil1 | 300 | 0,0653 | [−0,0216; 0,1522] | 0,141 | 0,020 |
| escassez_tercil | 1 | tercil2 | 302 | −0,0056 | [−0,0971; 0,0859] | 0,904 | 0,841 |
| escassez_tercil | 1 | tercil3 | 391 | 0,1116 | [0,0066; 0,2167] | 0,037 | < 0,001 |
| escassez_tercil | 2 | tercil1 | 563 | 0,1417 | [0,0685; 0,2149] | < 0,001 | < 0,001 |
| escassez_tercil | 2 | tercil2 | 793 | 0,1514 | [0,1003; 0,2026] | < 0,001 | < 0,001 |
| escassez_tercil | 2 | tercil3 | 784 | 0,1292 | [0,0653; 0,1931] | < 0,001 | < 0,001 |
| escassez_tercil | 3 | tercil1 | 549 | 0,0590 | [−0,0184; 0,1364] | 0,135 | 0,001 |
| escassez_tercil | 3 | tercil2 | 554 | 0,0140 | [−0,0554; 0,0835] | 0,692 | 0,437 |
| escassez_tercil | 3 | tercil3 | 691 | 0,0149 | [−0,0433; 0,0730] | 0,617 | 0,416 |
| escassez_tercil | 3 | sem_ponte_curso_cbo | 787 | −0,0430 | [−0,1027; 0,0168] | 0,159 | 0,010 |
| escassez_tercil | empilhado | tercil1 | 1412 | 0,0948 | [0,0470; 0,1426] | < 0,001 | < 0,001 |
| escassez_tercil | empilhado | tercil2 | 1649 | 0,0642 | [0,0142; 0,1142] | 0,012 | < 0,001 |
| escassez_tercil | empilhado | tercil3 | 1866 | 0,0747 | [0,0311; 0,1183] | < 0,001 | < 0,001 |
| escassez_tercil | empilhado | sem_ponte_curso_cbo | 787 | 0,0006 | [−0,0574; 0,0587] | 0,983 | 0,962 |
| estrato | 1 | capital | 73 | 0,0292 | [−0,0996; 0,1581] | 0,656 | 0,608 |
| estrato | 1 | interior_proximo_polo | 510 | 0,0537 | [−0,0390; 0,1465] | 0,256 | 0,027 |
| estrato | 1 | interior_remoto | 84 | 0,0453 | [−0,0300; 0,1205] | 0,238 | 0,198 |
| estrato | 1 | metropolitano | 326 | 0,0998 | [−0,0071; 0,2068] | 0,067 | < 0,001 |
| estrato | 2 | capital | 714 | 0,0933 | [0,0333; 0,1533] | 0,002 | < 0,001 |
| estrato | 2 | interior_proximo_polo | 665 | 0,1249 | [0,0726; 0,1772] | < 0,001 | < 0,001 |
| estrato | 2 | interior_remoto | 135 | 0,1331 | [0,0845; 0,1817] | < 0,001 | < 0,001 |
| estrato | 2 | metropolitano | 626 | 0,1575 | [0,0796; 0,2354] | < 0,001 | < 0,001 |
| estrato | 3 | capital | 985 | −0,0615 | [−0,1406; 0,0175] | 0,127 | < 0,001 |
| estrato | 3 | interior_proximo_polo | 746 | 0,0355 | [−0,0214; 0,0923] | 0,222 | 0,035 |
| estrato | 3 | interior_remoto | 214 | −0,0031 | [−0,0456; 0,0394] | 0,886 | 0,892 |
| estrato | 3 | metropolitano | 636 | 0,0788 | [−0,0126; 0,1702] | 0,091 | < 0,001 |
| estrato | empilhado | capital | 1772 | 0,0072 | [−0,0493; 0,0636] | 0,803 | 0,570 |
| estrato | empilhado | interior_proximo_polo | 1921 | 0,0672 | [0,0267; 0,1077] | 0,001 | < 0,001 |
| estrato | empilhado | interior_remoto | 433 | 0,0581 | [0,0170; 0,0991] | 0,006 | < 0,001 |
| estrato | empilhado | metropolitano | 1588 | 0,1106 | [0,0573; 0,1640] | < 0,001 | < 0,001 |

**Tabela X4.2. Termos de interação (diferença para o grupo de base) e Wald da igualdade das inclinações.** p pela normal com cluster por conjunto; p do score bootstrap (Rademacher; enumeração completa com G ≤ 24, senão sorteios); no empilhado, também com cluster por curso. q de BKY dentro do X4 (linhas fora da família: —).

| dimensão | ciclo | termo | base | coef. | IC 95% | p | p score (conjunto) | p score (curso) | q BKY |
|---|---|---|---|---:|---|---:|---:|---:|---:|
| nota_tercil | 1 | bolsa_x_tercil2 | tercil1 | 0,0245 | [−0,0131; 0,0621] | 0,201 | 0,270 | — | 0,204 |
| nota_tercil | 1 | bolsa_x_tercil3 | tercil1 | 0,0551 | [0,0074; 0,1029] | 0,024 | 0,064 | — | 0,064 |
| nota_tercil | 1 | bolsa_x_sem_pontuacao | tercil1 | −0,0096 | [−0,0596; 0,0404] | 0,706 | 0,712 | — | 0,435 |
| nota_tercil | 1 | Wald (χ², 3 gl) = 5,17 | tercil1 | — | — | 0,160 | — | — | 0,182 |
| nota_tercil | 2 | bolsa_x_tercil2 | tercil1 | −0,0428 | [−0,1159; 0,0303] | 0,251 | 0,343 | — | 0,214 |
| nota_tercil | 2 | bolsa_x_tercil3 | tercil1 | −0,0348 | [−0,0691; −0,0006] | 0,046 | 0,129 | — | 0,092 |
| nota_tercil | 2 | Wald (χ², 2 gl) = 6,47 | tercil1 | — | — | 0,039 | — | — | 0,087 |
| nota_tercil | 3 | bolsa_x_tercil2 | tercil1 | −0,0169 | [−0,1043; 0,0704] | 0,704 | 0,732 | — | 0,435 |
| nota_tercil | 3 | bolsa_x_tercil3 | tercil1 | −0,0121 | [−0,0427; 0,0184] | 0,436 | 0,502 | — | 0,333 |
| nota_tercil | 3 | Wald (χ², 2 gl) = 0,71 | tercil1 | — | — | 0,700 | — | — | 0,435 |
| nota_tercil | empilhado | bolsa_x_tercil2 | tercil1 | −0,0373 | [−0,0721; −0,0025] | 0,036 | 0,038 | 0,121 | 0,087 |
| nota_tercil | empilhado | bolsa_x_tercil3 | tercil1 | −0,0147 | [−0,0405; 0,0111] | 0,265 | 0,329 | 0,414 | 0,219 |
| nota_tercil | empilhado | bolsa_x_sem_pontuacao | tercil1 | −0,0901 | [−0,1458; −0,0345] | 0,002 | 0,018 | 0,030 | 0,010 |
| nota_tercil | empilhado | Wald (χ², 3 gl) = 12,38 | tercil1 | — | — | 0,006 | — | — | 0,023 |
| curso | 1 | bolsa_x_curso02 | demais_cursos | 0,0224 | [−0,0151; 0,0598] | 0,242 | 0,367 | — | — |
| curso | 1 | bolsa_x_curso08 | demais_cursos | −0,0294 | [−0,0672; 0,0085] | 0,128 | 0,289 | — | — |
| curso | 1 | bolsa_x_curso14 | demais_cursos | 0,0357 | [−0,0048; 0,0761] | 0,084 | 0,224 | — | — |
| curso | 1 | Wald (χ², 3 gl) = 402,19 | demais_cursos | — | — | < 0,001 | — | — | — |
| curso | 2 | bolsa_x_curso02 | curso01 | −0,1069 | [−0,1268; −0,0869] | < 0,001 | 0,052 | — | — |
| curso | 2 | bolsa_x_curso07 | curso01 | −0,1507 | [−0,1696; −0,1317] | < 0,001 | 0,172 | — | — |
| curso | 2 | bolsa_x_curso08 | curso01 | −0,0863 | [−0,0954; −0,0772] | < 0,001 | 0,133 | — | — |
| curso | 2 | bolsa_x_curso11 | curso01 | −0,1123 | [−0,1186; −0,1061] | < 0,001 | 0,380 | — | — |
| curso | 2 | bolsa_x_curso14 | curso01 | −0,0980 | [−0,1038; −0,0923] | < 0,001 | 0,368 | — | — |
| curso | 2 | bolsa_x_curso15 | curso01 | −0,0768 | [−0,0959; −0,0577] | < 0,001 | 0,191 | — | — |
| curso | 2 | bolsa_x_demais_cursos | curso01 | −0,0787 | [−0,1381; −0,0192] | 0,009 | 0,012 | — | — |
| curso | 2 | Wald (χ², 7 gl) = 5386,01 | curso01 | — | — | < 0,001 | — | — | — |
| curso | 3 | bolsa_x_curso01 | demais_cursos | 0,0764 | [0,0545; 0,0984] | < 0,001 | 0,007 | — | — |
| curso | 3 | bolsa_x_curso02 | demais_cursos | 0,0375 | [0,0150; 0,0600] | 0,001 | 0,107 | — | — |
| curso | 3 | bolsa_x_curso08 | demais_cursos | −0,0148 | [−0,0401; 0,0105] | 0,252 | 0,454 | — | — |
| curso | 3 | bolsa_x_curso17 | demais_cursos | −0,0063 | [−0,0314; 0,0188] | 0,622 | 0,606 | — | — |
| curso | 3 | bolsa_x_curso18 | demais_cursos | −0,0137 | [−0,0359; 0,0085] | 0,226 | 0,363 | — | — |
| curso | 3 | bolsa_x_curso24 | demais_cursos | −0,1649 | [−0,1902; −0,1396] | < 0,001 | 0,006 | — | — |
| curso | 3 | Wald (χ², 6 gl) = 3035,17 | demais_cursos | — | — | < 0,001 | — | — | — |
| curso | empilhado | bolsa_x_curso02 | curso01 | −0,0593 | [−0,0990; −0,0195] | 0,003 | 0,063 | 0,030 | — |
| curso | empilhado | bolsa_x_curso06 | curso01 | −0,1690 | [−0,2600; −0,0779] | < 0,001 | 0,078 | 0,194 | — |
| curso | empilhado | bolsa_x_curso07 | curso01 | −0,1218 | [−0,2003; −0,0434] | 0,002 | 0,149 | 0,208 | — |
| curso | empilhado | bolsa_x_curso08 | curso01 | −0,0880 | [−0,1400; −0,0361] | < 0,001 | 0,040 | 0,141 | — |
| curso | empilhado | bolsa_x_curso09 | curso01 | −0,0364 | [−0,1296; 0,0569] | 0,445 | 0,601 | 0,216 | — |
| curso | empilhado | bolsa_x_curso11 | curso01 | −0,0898 | [−0,1325; −0,0472] | < 0,001 | 0,092 | 0,336 | — |
| curso | empilhado | bolsa_x_curso14 | curso01 | −0,0707 | [−0,1118; −0,0296] | < 0,001 | 0,074 | 0,189 | — |
| curso | empilhado | bolsa_x_curso15 | curso01 | −0,0686 | [−0,1214; −0,0158] | 0,011 | 0,097 | 0,192 | — |
| curso | empilhado | bolsa_x_curso16 | curso01 | −0,1134 | [−0,1810; −0,0457] | 0,001 | 0,096 | 0,019 | — |
| curso | empilhado | bolsa_x_curso17 | curso01 | −0,0937 | [−0,1288; −0,0586] | < 0,001 | 0,301 | 0,223 | — |
| curso | empilhado | bolsa_x_curso18 | curso01 | −0,1062 | [−0,1436; −0,0687] | < 0,001 | 0,322 | 0,235 | — |
| curso | empilhado | bolsa_x_curso24 | curso01 | −0,2541 | [−0,2838; −0,2245] | < 0,001 | 0,149 | 0,058 | — |
| curso | empilhado | bolsa_x_demais_cursos | curso01 | −0,1058 | [−0,1535; −0,0581] | < 0,001 | < 0,001 | < 0,001 | — |
| curso | empilhado | Wald (χ², 13 gl) = 2204,07 | curso01 | — | — | < 0,001 | — | — | — |
| escassez_tercil | 1 | bolsa_x_tercil2 | tercil1 | −0,0709 | [−0,1507; 0,0089] | 0,082 | 0,058 | — | 0,125 |
| escassez_tercil | 1 | bolsa_x_tercil3 | tercil1 | 0,0463 | [−0,0238; 0,1165] | 0,195 | 0,303 | — | 0,204 |
| escassez_tercil | 1 | Wald (χ², 2 gl) = 14,38 | tercil1 | — | — | < 0,001 | — | — | 0,008 |
| escassez_tercil | 2 | bolsa_x_tercil2 | tercil1 | 0,0097 | [−0,0268; 0,0462] | 0,602 | 0,602 | — | 0,400 |
| escassez_tercil | 2 | bolsa_x_tercil3 | tercil1 | −0,0125 | [−0,0709; 0,0459] | 0,674 | 0,674 | — | 0,435 |
| escassez_tercil | 2 | Wald (χ², 2 gl) = 1,55 | tercil1 | — | — | 0,460 | — | — | 0,343 |
| escassez_tercil | 3 | bolsa_x_tercil2 | tercil1 | −0,0450 | [−0,0907; 0,0007] | 0,054 | 0,194 | — | 0,097 |
| escassez_tercil | 3 | bolsa_x_tercil3 | tercil1 | −0,0442 | [−0,0944; 0,0061] | 0,085 | 0,247 | — | 0,125 |
| escassez_tercil | 3 | bolsa_x_sem_ponte_curso_cbo | tercil1 | −0,1020 | [−0,1801; −0,0239] | 0,010 | 0,006 | — | 0,034 |
| escassez_tercil | 3 | Wald (χ², 3 gl) = 7,75 | tercil1 | — | — | 0,052 | — | — | 0,097 |
| escassez_tercil | empilhado | bolsa_x_tercil2 | tercil1 | −0,0306 | [−0,0657; 0,0046] | 0,088 | 0,108 | 0,178 | 0,125 |
| escassez_tercil | empilhado | bolsa_x_tercil3 | tercil1 | −0,0201 | [−0,0564; 0,0163] | 0,279 | 0,334 | 0,438 | 0,225 |
| escassez_tercil | empilhado | bolsa_x_sem_ponte_curso_cbo | tercil1 | −0,0941 | [−0,1577; −0,0306] | 0,004 | 0,012 | 0,035 | 0,018 |
| escassez_tercil | empilhado | Wald (χ², 3 gl) = 9,83 | tercil1 | — | — | 0,020 | — | — | 0,059 |
| estrato | 1 | bolsa_x_interior_proximo_polo | capital | 0,0245 | [−0,1130; 0,1620] | 0,727 | 0,738 | — | 0,438 |
| estrato | 1 | bolsa_x_interior_remoto | capital | 0,0160 | [−0,1122; 0,1442] | 0,807 | 0,807 | — | 0,462 |
| estrato | 1 | bolsa_x_metropolitano | capital | 0,0706 | [−0,0730; 0,2142] | 0,335 | 0,382 | — | 0,262 |
| estrato | 1 | Wald (χ², 3 gl) = 2,52 | capital | — | — | 0,472 | — | — | 0,343 |
| estrato | 2 | bolsa_x_interior_proximo_polo | capital | 0,0316 | [−0,0044; 0,0675] | 0,085 | 0,060 | — | 0,125 |
| estrato | 2 | bolsa_x_interior_remoto | capital | 0,0398 | [−0,0250; 0,1046] | 0,229 | 0,185 | — | 0,204 |
| estrato | 2 | bolsa_x_metropolitano | capital | 0,0642 | [−0,0167; 0,1452] | 0,120 | 0,113 | — | 0,143 |
| estrato | 2 | Wald (χ², 3 gl) = 3,60 | capital | — | — | 0,308 | — | — | 0,244 |
| estrato | 3 | bolsa_x_interior_proximo_polo | capital | 0,0970 | [0,0347; 0,1592] | 0,002 | 0,009 | — | 0,013 |
| estrato | 3 | bolsa_x_interior_remoto | capital | 0,0584 | [−0,0207; 0,1375] | 0,148 | 0,220 | — | 0,174 |
| estrato | 3 | bolsa_x_metropolitano | capital | 0,1403 | [0,0806; 0,2001] | < 0,001 | 0,003 | — | 0,001 |
| estrato | 3 | Wald (χ², 3 gl) = 25,07 | capital | — | — | < 0,001 | — | — | 0,001 |
| estrato | empilhado | bolsa_x_interior_proximo_polo | capital | 0,0600 | [0,0177; 0,1023] | 0,005 | 0,007 | 0,015 | 0,023 |
| estrato | empilhado | bolsa_x_interior_remoto | capital | 0,0509 | [0,0022; 0,0995] | 0,040 | 0,030 | 0,047 | 0,087 |
| estrato | empilhado | bolsa_x_metropolitano | capital | 0,1035 | [0,0517; 0,1553] | < 0,001 | < 0,001 | 0,001 | 0,002 |
| estrato | empilhado | Wald (χ², 3 gl) = 16,60 | capital | — | — | < 0,001 | — | — | 0,008 |

**Tabela X4.3. Pontos de corte dos tercis da pontuação (1/3 e 2/3, quantil linear; empate no corte vai para o tercil de baixo).**

| ciclo | corte 1/3 | corte 2/3 | tercil 1 | tercil 2 | tercil 3 | sem pontuação |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 4,00 | 5,00 | 323 | 284 | 272 | 114 |
| 2 | 5,00 | 6,00 | 1372 | 120 | 648 | 0 |
| 3 | 5,00 | 6,00 | 1635 | 184 | 762 | 0 |

<!-- X4_TABELAS_FIM -->

### Leitura

- **Nota do candidato:** dentro de cada ciclo, nenhum tercil difere do tercil 1
  com q < 0,05, e o Wald da igualdade não rejeita com q < 0,05 em nenhum ciclo.
  No empilhado, o Wald rejeita, mas por causa do grupo sem pontuação, que só
  existe no ciclo 1. No empilhado, esse grupo é comparado a um tercil 1 que
  junta os três ciclos; dentro do ciclo 1, a diferença não tem q < 0,05. Não
  há evidência de que candidatos de nota alta e baixa respondam à bolsa de
  forma diferente. Por causa dos empates, o tercil 2 é o menor nos ciclos 2 e
  3 (Tabela X4.3).
- **Escassez:** entre os tercis, nenhuma interação tem q < 0,05. O Wald só
  rejeita com q < 0,05 no ciclo 1, e com o tercil do meio abaixo dos outros dois: um padrão
  não monotônico, que não sustenta "a bolsa pesa mais onde a especialidade é
  mais escassa". O grupo sem ponte (cursos 17 a 24, só no ciclo 3) responde
  menos que o tercil 1, com q < 0,05. Isso é diferença entre cursos, não entre
  níveis de escassez: na dimensão curso, o curso 24 tem inclinação negativa no
  ciclo 3, também pelo EP de MV.
- **Estrato:** no ciclo 3 e no empilhado, o Wald rejeita a igualdade com
  q < 0,05. No empilhado, todas as interações são positivas: a capital
  responde menos que os outros estratos, e a inclinação da capital tem IC 95%
  que inclui zero. Nos ciclos 1 e 2 não há rejeição. O estrato não é
  aleatório e anda junto com outros atributos da célula; a diferença é
  descritiva da escolha.
- **Ciclo 2:** a inclinação é positiva, com IC 95% acima de zero, em todos os
  grupos de nota, escassez e estrato. A resposta do ciclo 2 não vem de um grupo
  só.
- **Curso:** pelo EP de MV, o Wald entre cursos rejeita nos ciclos 2, 3 e
  empilhado, e não no ciclo 1. O E9 mostrou que o EP de MV ignora o choque
  comum dentro do conjunto e subestima a incerteza; nos termos próprios de
  curso, o EP por cluster fica ainda menor que o de MV, o que é sintoma da
  degeneração, não precisão. A heterogeneidade entre cursos é descritiva.
- **Para as propostas do doc 44 (§7):** a resposta não se concentra em
  candidatos de nota alta ou baixa nem nos municípios de especialidade mais
  escassa. Dentro de ciclo, fora da dimensão curso, as linhas com q < 0,05 são
  só três grupos de achados: a menor resposta das capitais no ciclo 3, o padrão
  não monotônico da escassez no ciclo 1 e a menor resposta dos cursos sem ponte
  no ciclo 3. A das capitais é compatível com a leitura B (atributos não
  pecuniários pesam mais em algumas células), mas não a distingue de outras
  explicações.

### Desvios e limites

- **Cursos 17 a 24 sem ponte curso–CBO:** sem escassez calculada; grupo próprio,
  sem imputação.
- **Grupo sem pontuação:** existe só no ciclo 1; no empilhado, a comparação
  mistura grupo e ciclo.
- **Tercis com empate:** pontuações discretas fazem tercis desiguais; a regra
  (empate para baixo) foi fixada antes da estimação.
- **Curso:** inferência por cluster degenerada (acima); fora do BKY.
- **Limites do E9 valem aqui:** IIA, atributos não observados, seleção para
  candidatar-se e escolha estratégica.

## X5 — Deslocamento regional

> **Data:** 19/10/2026.<br>
> **Estatuto:** `EXPLORATORIO_POS_SINTESE` (protocolo
> [`45`](45_protocolo_exploratorio_pos_sintese.md), §2 e §3).<br>
> **Script:** `scripts/rdd_bolsa/19_escolha_heterogeneidade.py`.<br>
> **Região de saúde:** tabela oficial de conversão município → Região de Saúde
> (CIR) do TabNet/DATASUS (`territorio/br_regsaud.cnv`), baixada com
> `--baixar-regioes` para `data/raw/aquisicao/territorio/datasus_tabnet_br_regsaud.cnv`;
> URL, data e SHA-256 em `output/rdd_bolsa/X5_manifesto_regioes_saude_cir.json`.<br>
> **Saídas:** `output/rdd_bolsa/X5_estimativas.csv`, `X4X5_resumo.json` e
> `X4X5_tabelas_relato.md`.<br>
> **Testes:** `tests/test_x4_x5_escolha.py` (recuperação do efeito de
> vizinhança e de lambda em dados sintéticos; identidade do aninhado com
> lambda = 1 e do condicional; invariantes; blocos e frases conferidos).

Nenhum número desta seção foi digitado: as tabelas são o bloco X5 de
`output/rdd_bolsa/X4X5_tabelas_relato.md`, conferido por teste.

### Especificação

- **Por que não a malha do repositório:** a região de saúde de
  `malha_municipios_regioes_saude.parquet` vem da série e da lista nominal do
  PMM-E, e só existe nos municípios com ativo do programa. Usá-la condicionaria
  a amostra a um resultado pós-tratamento. A malha fica como conferência: nos
  municípios em que as duas fontes têm região, a partição da malha coincide com
  a da CIR oficial (`conferencias.cir_contra_malha` no resumo).
- **Município sem CIR oficial:** um município do quadro não está na tabela do
  TabNet. Suas células e os candidatos que as escolheram saem do X5, sem
  imputação (Tabela X5.3); o principal do E9 é reestimado nessa amostra
  (linhas `sem_vizinhanca`).
- **(i) Logit aninhado:** ninhos = CIR dentro do curso × ciclo, um lambda comum,
  por máxima verossimilhança própria (quase-Newton e polimento por Newton com
  hessiana numérica), iniciado no condicional (lambda = 1). Lambda = 1 é o logit
  condicional; lambda < 1 quer dizer escolhas mais correlacionadas dentro da
  CIR, isto é, mais substituição entre células da mesma região. Relatam-se
  lambda, a bolsa, o Wald de lambda = 1 (cluster por conjunto) e a razão de
  verossimilhança contra o condicional.
- **(ii) Atributos de vizinhança** no logit condicional: número de outras
  células da mesma CIR e do mesmo conjunto com bolsa maior (como no doc 45);
  variante com o total de outras células da CIR no conjunto, para separar ter
  vizinhos de ter vizinhos de bolsa maior; variante com a fração de vizinhos de
  bolsa maior (zero sem vizinho, sempre com o indicador de ter vizinho). A
  proposta A prevê coeficiente negativo.
- **Inferência:** como no X4. q de BKY dentro do X5, sobre os termos de
  vizinhança e o Wald de lambda = 1.

### Resultados

<!-- X5_TABELAS_INICIO -->
<!-- gerado por scripts/rdd_bolsa/19_escolha_heterogeneidade.py; não editar à mão -->

**Tabela X5.1. Bolsa com e sem termos de vizinhança, termos de vizinhança e logit aninhado por região de saúde (CIR).** Amostra do X5 (sem células de município sem CIR oficial). EP e IC 95% com cluster por conjunto; p pela normal; p do score bootstrap Rademacher (cluster por conjunto) nos termos de vizinhança. Na linha lambda − 1, o p é o do Wald de H0: lambda = 1. q de BKY dentro do X5.

| ciclo | especificação | termo | coef. | IC 95% | p | p score (conjunto) | q BKY |
|---|---|---|---:|---|---:|---:|---:|
| 1 | sem_vizinhanca | bolsa_mil | 0,0663 | [−0,0197; 0,1524] | 0,131 | — | — |
| 1 | vizinhos_contagem | bolsa_mil | 0,0623 | [−0,0230; 0,1476] | 0,152 | — | — |
| 1 | vizinhos_contagem | n_vizinhos_bolsa_maior | −0,3873 | [−0,7816; 0,0071] | 0,054 | 0,033 | 0,134 |
| 1 | vizinhos_contagem_e_total | bolsa_mil | 0,0690 | [−0,0131; 0,1511] | 0,100 | — | — |
| 1 | vizinhos_contagem_e_total | n_vizinhos_bolsa_maior | −0,0165 | [−0,3220; 0,2890] | 0,916 | 0,938 | 0,578 |
| 1 | vizinhos_fracao | bolsa_mil | 0,0610 | [−0,0194; 0,1414] | 0,137 | — | — |
| 1 | vizinhos_fracao | fracao_vizinhos_bolsa_maior | −0,2547 | [−0,6208; 0,1114] | 0,173 | 0,206 | 0,238 |
| 1 | aninhado_cir | bolsa_mil | 0,0547 | [−0,0239; 0,1333] | 0,173 | — | — |
| 1 | aninhado_cir | lambda | 0,5633 | [0,4193; 0,7072] | — | — | — |
| 1 | aninhado_cir | lambda_menos_1 | −0,4367 | [−0,5807; −0,2928] | < 0,001 | — | 0,001 |
| 2 | sem_vizinhanca | bolsa_mil | 0,1328 | [0,0778; 0,1878] | < 0,001 | — | — |
| 2 | vizinhos_contagem | bolsa_mil | 0,1328 | [0,0778; 0,1879] | < 0,001 | — | — |
| 2 | vizinhos_contagem | n_vizinhos_bolsa_maior | −0,0183 | [−0,2564; 0,2198] | 0,880 | 0,852 | 0,578 |
| 2 | vizinhos_contagem_e_total | bolsa_mil | 0,1479 | [0,0913; 0,2045] | < 0,001 | — | — |
| 2 | vizinhos_contagem_e_total | n_vizinhos_bolsa_maior | 0,1837 | [−0,1085; 0,4759] | 0,218 | 0,373 | 0,279 |
| 2 | vizinhos_fracao | bolsa_mil | 0,1491 | [0,0884; 0,2099] | < 0,001 | — | — |
| 2 | vizinhos_fracao | fracao_vizinhos_bolsa_maior | 0,3846 | [−0,1620; 0,9311] | 0,168 | 0,385 | 0,238 |
| 2 | aninhado_cir | bolsa_mil | 0,1323 | [0,0806; 0,1839] | < 0,001 | — | — |
| 2 | aninhado_cir | lambda | 0,7497 | [0,6860; 0,8134] | — | — | — |
| 2 | aninhado_cir | lambda_menos_1 | −0,2503 | [−0,3140; −0,1866] | < 0,001 | — | 0,001 |
| 3 | sem_vizinhanca | bolsa_mil | 0,0095 | [−0,0527; 0,0716] | 0,766 | — | — |
| 3 | vizinhos_contagem | bolsa_mil | 0,0134 | [−0,0556; 0,0824] | 0,703 | — | — |
| 3 | vizinhos_contagem | n_vizinhos_bolsa_maior | −0,0420 | [−0,0920; 0,0080] | 0,100 | 0,345 | 0,170 |
| 3 | vizinhos_contagem_e_total | bolsa_mil | 0,0131 | [−0,0426; 0,0688] | 0,644 | — | — |
| 3 | vizinhos_contagem_e_total | n_vizinhos_bolsa_maior | −0,0428 | [−0,1423; 0,0567] | 0,399 | 0,853 | 0,444 |
| 3 | vizinhos_fracao | bolsa_mil | 0,0188 | [−0,0358; 0,0734] | 0,499 | — | — |
| 3 | vizinhos_fracao | fracao_vizinhos_bolsa_maior | 0,0219 | [−0,3255; 0,3693] | 0,902 | 0,912 | 0,578 |
| 3 | aninhado_cir | bolsa_mil | 0,0256 | [−0,0283; 0,0795] | 0,351 | — | — |
| 3 | aninhado_cir | lambda | 0,8520 | [0,7179; 0,9862] | — | — | — |
| 3 | aninhado_cir | lambda_menos_1 | −0,1480 | [−0,2821; −0,0138] | 0,031 | — | 0,111 |
| empilhado | sem_vizinhanca | bolsa_mil | 0,0661 | [0,0227; 0,1095] | 0,003 | — | — |
| empilhado | vizinhos_contagem | bolsa_mil | 0,0686 | [0,0248; 0,1124] | 0,002 | — | — |
| empilhado | vizinhos_contagem | n_vizinhos_bolsa_maior | −0,0477 | [−0,0955; 0,0001] | 0,051 | 0,188 | 0,134 |
| empilhado | vizinhos_contagem_e_total | bolsa_mil | 0,0766 | [0,0327; 0,1206] | < 0,001 | — | — |
| empilhado | vizinhos_contagem_e_total | n_vizinhos_bolsa_maior | 0,0008 | [−0,1272; 0,1288] | 0,990 | 0,996 | 0,591 |
| empilhado | vizinhos_fracao | bolsa_mil | 0,0752 | [0,0313; 0,1190] | < 0,001 | — | — |
| empilhado | vizinhos_fracao | fracao_vizinhos_bolsa_maior | 0,1145 | [−0,1816; 0,4106] | 0,449 | 0,489 | 0,444 |
| empilhado | aninhado_cir | bolsa_mil | 0,0745 | [0,0348; 0,1142] | < 0,001 | — | — |
| empilhado | aninhado_cir | lambda | 0,7563 | [0,6474; 0,8653] | — | — | — |
| empilhado | aninhado_cir | lambda_menos_1 | −0,2437 | [−0,3526; −0,1347] | < 0,001 | — | 0,001 |

**Tabela X5.2. Amostra, ninhos e convergência do logit aninhado.**

| ciclo | candidatos | células | células com vizinho na CIR | ninhos | ninhos de uma célula | lambda no limite | convergiu | LR contra o condicional | p LR |
|---|---:|---:|---:|---:|---:|---|---|---:|---:|
| 1 | 990 | 1289 | 416 | 1044 | 873 | não | sim | 41,78 | < 0,001 |
| 2 | 2140 | 1545 | 783 | 1032 | 762 | não | sim | 52,35 | < 0,001 |
| 3 | 2581 | 2291 | 1676 | 1098 | 615 | não | sim | 23,02 | < 0,001 |
| empilhado | 5711 | 5125 | 2875 | 3174 | 2250 | não | sim | 137,06 | < 0,001 |

**Tabela X5.3. Fora do X5 por falta de CIR oficial (sem imputação).**

| ciclo | células retiradas | candidatos de 1a opção retirados |
|---|---:|---:|
| 1 | 6 | 3 |
| 2 | 2 | 0 |
| 3 | 1 | 0 |

<!-- X5_TABELAS_FIM -->

### Leitura

- **Logit aninhado:** lambda fica abaixo de 1 em todos os ciclos, com IC 95%
  abaixo de 1. O Wald de lambda = 1 tem q < 0,05 nos ciclos 1, 2 e empilhado,
  e não no ciclo 3; a razão de verossimilhança rejeita o condicional em todos
  os ciclos. As 1as opções são mais correlacionadas dentro da região de saúde
  do que o logit condicional permite: o candidato troca mais facilmente uma
  célula por outra da mesma região. Esse padrão é o que a proposta A precisa
  para que uma bolsa maior tire candidatos sobretudo das vizinhas. Mas lambda
  não diz por quê: qualquer fator comum à região (a origem do candidato, que
  não é publicada, ou atributos regionais não observados) gera o mesmo padrão.
- **Bolsa:** o coeficiente muda pouco com os termos de vizinhança e no
  aninhado. Em cada ciclo, o IC 95% da bolsa exclui zero em todas as
  especificações ou em nenhuma, como no E9: as conclusões do E9 por ciclo não
  mudam.
- **Vizinhança:** nenhum termo tem q < 0,05. A contagem de vizinhos de bolsa
  maior, sozinha, tem coeficiente negativo em todos os ciclos; com o total de
  outras células da região no modelo, ela fica perto de zero, com IC 95% que
  inclui zero. O sinal da contagem sozinha acompanha o número de vizinhas, e
  não o fato de elas pagarem mais. A fração de vizinhos de bolsa
  maior também tem IC 95% que inclui zero em todos os ciclos.
- **Para a proposta A:** a forma (ii) não encontra deslocamento específico
  para vizinhas de bolsa menor, além da substituição proporcional do logit. A
  forma (i) mostra substituição concentrada na região, de natureza não
  identificada. Os dados de escolha são compatíveis com realocação regional,
  mas não a demonstram.

### Desvios e limites

- **Fonte da região de saúde:** CIR oficial do TabNet em vez da malha indicada
  na tarefa (motivo acima); download público, permitido pelo §2 do doc 45. É a
  base territorial corrente do TabNet, não uma competência do CNES.
- **Município sem CIR:** fora do X5, com contagem; nada imputado.
- **Ninhos de uma célula:** muitos (Tabela X5.2); lambda é identificado pelos
  ninhos com mais de uma célula.
- **Sem residência do candidato:** a distância e a região de origem não entram;
  lambda < 1 pode refletir preferência pela região de origem.
- **IIA dentro do ninho e um lambda comum** a todos os ninhos, cursos e
  ciclos.
