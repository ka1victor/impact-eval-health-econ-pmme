# 57e. Resultados do P5: com o que a abertura de vagas anda junto

> **Data:** 19/10/2026.<br>
> **Protocolo:** [`55_protocolo_P5_abertura_vagas.md`](55_protocolo_P5_abertura_vagas.md), congelado antes de
> estimar.<br>
> **Script:** `scripts/rdd_bolsa/29_determinantes_abertura.py`.<br>
> **Saídas:** `output/rdd_bolsa/P5_estimativas.csv`, `P5_resumo.json` e `P5_figuras/`.<br>
> **Testes:** `tests/test_P5_abertura.py`.<br>
> **Estatuto:** `PROTOCOLO_55_DESCRITIVO`; toda linha tem `natureza_dos_dados = EMPIRICO`.<br>
> **Para a síntese:** este documento é a seção P5 que o protocolo manda pôr no doc 57 (ver desvios).

Os números deste documento ficam só entre os marcadores `<!-- P5:... -->`. O
script os grava a partir de `output/` e o teste confere que são iguais. A prosa
fora dos marcadores não traz resultado.

## 1. O que se pergunta e o que não se pode dizer

A abertura de uma vaga do PMM-E passa por três decisões:
- o gestor escolhe, no cardápio, as células (estabelecimento × curso) que pede;
- a SGTES prioriza, tudo ou nada, parte das células pedidas;
- o quadro publicado de cada ciclo traz as células e as vagas que ficaram.

O P5 pergunta quais características medidas **antes** do programa andam junto
com cada decisão. A leitura é **descritiva**:
- "associado a", nunca "o Ministério escolhe por causa de";
- o critério oficial de priorização não é publicado (auditoria 01; doc 51, §1);
- uma característica pode aparecer associada porque anda junto com outra que
  não foi medida.

A RDD nos cortes (T5.2) mede o **pacote** do corte: a bolsa anunciada maior e
as outras regras federais que mudam no mesmo IVS (auditoria 18). Não mede a
bolsa sozinha nem a participação no PMM-E.

Regras de ausência:
- o município que não consta do resultado da adesão fica com o pedido
  **ausente**, nunca zero (doc 41a, §5);
- a presença no resultado é uma linha à parte, no nível do município;
- célula sem alguma covariável sai da amostra e é contada; nada é imputado.

## 2. Amostras

<!-- P5:amostras:inicio -->
| Item | Contagem |
|---|---|
| células do cardápio do ciclo 3 | 17543 |
| municípios do cardápio | 2699 |
| municípios que constam do resultado da adesão | 1163 |
| células em municípios que constam (população do E1) | 10073 |
| células pedidas (população do E2) | 5288 |
| células pedidas e priorizadas | 2143 |
| linhas da adesão fora do cardápio (não entram) | 246 |
| células de cursos fora da ponte curso–CBO (cursos 17, 18, 19, 20, 21, 22, 23, 24) | 5019 |
| municípios que constam sem célula do cardápio pedida | 11 |
| E1 (T5.1a), amostra estimada | 7152 de 10073 |
| E2 (T5.1b), amostra estimada | 3538 de 5288 |
| presença (T5.1a, município), amostra estimada | 2697 de 2699 |
| E1, sensibilidade com todos os cursos | 10057 de 10073 |
| E2, sensibilidade com todos os cursos | 5097 de 5288 |
<!-- P5:amostras:fim -->

As células dos cursos que a ponte curso–CBO do a09 não cobre não têm vínculos
do curso. A especificação principal as deixa de fora. A sensibilidade rotulada
"todos os cursos" usa, no lugar, a capacidade e a escassez do conjunto de CBO
dos cursos (alvo).

## 3. Leitura em linguagem simples

<!-- P5:leitura:inicio -->
**Pedido do gestor (E1).** Probabilidade maior associada a: macrorregião: SUL (ref.: SUDESTE) (quando a célula tem o atributo: +16,2 p.p., IC 95% [+6,0; +26,4]); macrorregião: NORDESTE (ref.: SUDESTE) (quando a célula tem o atributo: +13,7 p.p., IC 95% [+3,9; +23,6]); vínculos CNES pré das CBO do curso por 10 mil hab. (quando a característica sobe um desvio-padrão: +4,2 p.p., IC 95% [+1,2; +7,3]). Probabilidade menor associada a: gestão: ESTADUAL (ref.: MUNICIPAL) (quando a célula tem o atributo: −9,3 p.p., IC 95% [−15,6; −3,0]); log da população do Censo 2022 (quando a característica sobe um desvio-padrão: −8,9 p.p., IC 95% [−16,2; −1,7]); natureza jurídica: SEM FINS LUCRATIVOS (ref.: PUBLICO) (quando a célula tem o atributo: −5,8 p.p., IC 95% [−11,3; −0,2]); vínculos CNES pré de todos os médicos por 10 mil hab. (quando a característica sobe um desvio-padrão: −4,9 p.p., IC 95% [−9,3; −0,5]). O IVS contínuo, mantidas as demais características, não se distingue de zero (−1,8 p.p. por desvio-padrão, IC 95% [−5,7; +2,1]). O grupo que mais separa os casos é município (população, REGIC, capital, macrorregião, polo) (queda do pseudo-R² de 0,026 sem ele, num pseudo-R² completo de 0,082).

**Priorização da SGTES (E2).** Probabilidade maior associada a: macrorregião: NORTE (ref.: SUDESTE) (quando a célula tem o atributo: +30,5 p.p., IC 95% [+21,0; +40,0]); macrorregião: CENTRO OESTE (ref.: SUDESTE) (quando a célula tem o atributo: +21,4 p.p., IC 95% [+13,5; +29,2]); macrorregião: NORDESTE (ref.: SUDESTE) (quando a célula tem o atributo: +14,2 p.p., IC 95% [+6,5; +21,9]); vínculos das CBO do curso por 10 mil hab. na região de saúde (quando a característica sobe um desvio-padrão: +6,5 p.p., IC 95% [+3,4; +9,6]). Probabilidade menor associada a: natureza jurídica: SEM FINS LUCRATIVOS (ref.: PUBLICO) (quando a célula tem o atributo: −4,9 p.p., IC 95% [−9,0; −0,8]). O IVS contínuo, mantidas as demais características, não se distingue de zero (+0,1 p.p. por desvio-padrão, IC 95% [−3,4; +3,5]). O grupo que mais separa os casos é município (população, REGIC, capital, macrorregião, polo) (queda do pseudo-R² de 0,028 sem ele, num pseudo-R² completo de 0,103).

**Presença do município no resultado (E1).** Probabilidade maior associada a: macrorregião: NORDESTE (ref.: SUDESTE) (quando o município tem o atributo: +26,5 p.p., IC 95% [+20,2; +32,9]); macrorregião: NORTE (ref.: SUDESTE) (quando o município tem o atributo: +21,0 p.p., IC 95% [+12,3; +29,7]); hierarquia urbana (REGIC 2018): 2 CAPITAL REGIONAL (ref.: 5 CENTRO LOCAL) (quando o município tem o atributo: +9,9 p.p., IC 95% [+0,5; +19,3]); log da população do Censo 2022 (quando a característica sobe um desvio-padrão: +9,6 p.p., IC 95% [+6,7; +12,4]). O IVS contínuo, mantidas as demais características, está associado a uma variação de −3,4 p.p. por desvio-padrão (IC 95% [−6,7; −0,1]). O grupo que mais separa os casos é município (população, REGIC, capital, macrorregião, polo) (queda do pseudo-R² de 0,063 sem ele, num pseudo-R² completo de 0,076).

**Nos cortes (T5.2a, cortes empilhados, h = 0,050).** fração de células pedidas (município): salto de −2,3 p.p. (IC 95% [−12,5; +8,0], q BKY 1,000), que os dados não distinguem de zero; fração de pedidas priorizadas (município): salto de −7,6 p.p. (IC 95% [−19,3; +4,2], q BKY 1,000), que os dados não distinguem de zero; célula pedida: salto de +14,7 p.p. (IC 95% [+1,8; +27,6], q BKY 0,602): o IC 95% exclui zero, mas a linha não passa no BKY entre as linhas do T5.2 (q ≥ 0,05); célula pedida priorizada: salto de −0,3 p.p. (IC 95% [−12,4; +11,8], q BKY 1,000), que os dados não distinguem de zero; presença do município no resultado: salto de −7,0 p.p. (IC 95% [−18,9; +4,8], q BKY 1,000), que os dados não distinguem de zero. Cada salto mede o pacote do corte (bolsa anunciada +R$ 5 mil e outras regras federais nos mesmos cortes), não a bolsa sozinha nem efeito da participação no PMM-E; IC que contém zero é falta de evidência com a precisão relatada, não prova de ausência.

**Quadro dos ciclos 1 e 2 (T5.3).** Mantidas as demais características municipais, o IVS contínuo está associado a: ciclo 1, células: razão de taxas de 0,75 por desvio-padrão do IVS (IC 95% [0,60; 0,95]); ciclo 1, vagas: razão de taxas de 0,78 por desvio-padrão do IVS (IC 95% [0,59; 1,03]), não distinguível de 1; ciclo 2, células: razão de taxas de 1,03 por desvio-padrão do IVS (IC 95% [0,80; 1,33]), não distinguível de 1; ciclo 2, vagas: razão de taxas de 0,97 por desvio-padrão do IVS (IC 95% [0,69; 1,37]), não distinguível de 1. As demais razões estão na tabela da seção 7.

Tudo acima é descritivo: diz com o que a abertura anda junto, não por que o Ministério decide. O critério oficial de priorização não é publicado.
<!-- P5:leitura:fim -->

## 4. Efeitos marginais médios (T5.1a, T5.1b e T5.1c)

Como ler as tabelas:
- cada linha é uma característica, com todas as outras mantidas e o efeito
  fixo de curso;
- para as medidas contínuas, o efeito é o de subir um desvio-padrão da
  amostra;
- para os atributos, é a diferença contra a categoria de referência;
- o efeito está em pontos percentuais de probabilidade;
- o IC usa o erro-padrão com cluster por município;
- não há correção para testes múltiplos (§4 do protocolo).

Os coeficientes do logit estão no CSV (`T5.1a` e `T5.1b`).

### 4.1 Pedido do gestor (E1): célula do cardápio, municípios que constam

<!-- P5:ame_e1:inicio -->
| Grupo | Característica | Variação | Efeito marginal médio | IC 95% | p | IC exclui zero |
|---|---|---|---|---|---|---|
| estabelecimento | gestão: DUPLA (ref.: MUNICIPAL) | atributo vs. referência | −3,2 p.p. | [−12,9; +6,5] | 0,519 | não |
| estabelecimento | gestão: ESTADUAL (ref.: MUNICIPAL) | atributo vs. referência | −9,3 p.p. | [−15,6; −3,0] | 0,004 | sim |
| estabelecimento | natureza jurídica: PRIVADO (ref.: PUBLICO) | atributo vs. referência | +7,4 p.p. | [−11,2; +26,1] | 0,434 | não |
| estabelecimento | natureza jurídica: SEM FINS LUCRATIVOS (ref.: PUBLICO) | atributo vs. referência | −5,8 p.p. | [−11,3; −0,2] | 0,042 | sim |
| estabelecimento | tipo do estabelecimento: 04 POLICLINICA (ref.: 05 HOSPITAL GERAL) | atributo vs. referência | −5,6 p.p. | [−11,4; +0,2] | 0,060 | não |
| estabelecimento | tipo do estabelecimento: 07 HOSPITAL ESPECIALIZADO (ref.: 05 HOSPITAL GERAL) | atributo vs. referência | −8,2 p.p. | [−18,2; +1,8] | 0,106 | não |
| estabelecimento | tipo do estabelecimento: 36 CLINICA CENTRO DE ESPECIALIDADE (ref.: 05 HOSPITAL GERAL) | atributo vs. referência | −5,3 p.p. | [−11,0; +0,4] | 0,066 | não |
| estabelecimento | tipo do estabelecimento: 62 HOSPITAL DIA ISOLADO (ref.: 05 HOSPITAL GERAL) | atributo vs. referência | −2,4 p.p. | [−22,4; +17,6] | 0,814 | não |
| município | capital de UF | atributo vs. referência | −0,4 p.p. | [−13,8; +12,9] | 0,951 | não |
| município | log da população do Censo 2022 | +1 DP (DP = 1,640) | −8,9 p.p. | [−16,2; −1,7] | 0,016 | sim |
| município | macrorregião: CENTRO OESTE (ref.: SUDESTE) | atributo vs. referência | +7,5 p.p. | [−3,6; +18,5] | 0,185 | não |
| município | macrorregião: NORDESTE (ref.: SUDESTE) | atributo vs. referência | +13,7 p.p. | [+3,9; +23,6] | 0,006 | sim |
| município | macrorregião: NORTE (ref.: SUDESTE) | atributo vs. referência | +5,8 p.p. | [−6,0; +17,7] | 0,334 | não |
| município | macrorregião: SUL (ref.: SUDESTE) | atributo vs. referência | +16,2 p.p. | [+6,0; +26,4] | 0,002 | sim |
| município | polo da região de saúde (maior população da região) | atributo vs. referência | −3,3 p.p. | [−10,7; +4,1] | 0,385 | não |
| município | hierarquia urbana (REGIC 2018): 1 METROPOLE (ref.: 5 CENTRO LOCAL) | atributo vs. referência | +8,5 p.p. | [−4,5; +21,5] | 0,198 | não |
| município | hierarquia urbana (REGIC 2018): 2 CAPITAL REGIONAL (ref.: 5 CENTRO LOCAL) | atributo vs. referência | +0,0 p.p. | [−11,7; +11,8] | 0,995 | não |
| município | hierarquia urbana (REGIC 2018): 3 CENTRO SUB REGIONAL (ref.: 5 CENTRO LOCAL) | atributo vs. referência | −3,4 p.p. | [−13,0; +6,1] | 0,483 | não |
| município | hierarquia urbana (REGIC 2018): 4 CENTRO DE ZONA (ref.: 5 CENTRO LOCAL) | atributo vs. referência | −1,8 p.p. | [−9,5; +5,9] | 0,652 | não |
| capacidade pré no CNES | vínculos CNES pré das CBO do curso por 10 mil hab. | +1 DP (DP = 3,433) | +4,2 p.p. | [+1,2; +7,3] | 0,006 | sim |
| capacidade pré no CNES | vínculos CNES pré de todos os médicos por 10 mil hab. | +1 DP (DP = 61,762) | −4,9 p.p. | [−9,3; −0,5] | 0,028 | sim |
| produção pré no SIA | produção SIA pré das CBO-alvo por 10 mil hab. (média mensal) | +1 DP (DP = 587,771) | −0,5 p.p. | [−3,8; +2,8] | 0,758 | não |
| produção pré no SIA | produção SIA pré de todos os profissionais por 10 mil hab. (média mensal) | +1 DP (DP = 19184,645) | −0,4 p.p. | [−5,3; +4,4] | 0,855 | não |
| escassez regional | vínculos das CBO do curso por 10 mil hab. na região de saúde | +1 DP (DP = 2,412) | −3,6 p.p. | [−6,8; −0,5] | 0,025 | sim |
| IVS 2010 oficial | IVS 2010 oficial (contínuo) | +1 DP (DP = 0,098) | −1,8 p.p. | [−5,7; +2,1] | 0,366 | não |

Amostra: 7152 linhas (3593 com outcome = 1), 1046 municípios (clusters); 2921 linhas fora (motivos na coluna `nota` do CSV). Média do outcome: 50,2 %.
<!-- P5:ame_e1:fim -->

### 4.2 Priorização da SGTES (E2): célula pedida

<!-- P5:ame_e2:inicio -->
| Grupo | Característica | Variação | Efeito marginal médio | IC 95% | p | IC exclui zero |
|---|---|---|---|---|---|---|
| estabelecimento | gestão: DUPLA (ref.: MUNICIPAL) | atributo vs. referência | +3,5 p.p. | [−3,2; +10,2] | 0,307 | não |
| estabelecimento | gestão: ESTADUAL (ref.: MUNICIPAL) | atributo vs. referência | −3,4 p.p. | [−7,9; +1,2] | 0,144 | não |
| estabelecimento | natureza jurídica: PRIVADO (ref.: PUBLICO) | atributo vs. referência | +0,7 p.p. | [−14,5; +15,9] | 0,926 | não |
| estabelecimento | natureza jurídica: SEM FINS LUCRATIVOS (ref.: PUBLICO) | atributo vs. referência | −4,9 p.p. | [−9,0; −0,8] | 0,019 | sim |
| estabelecimento | tipo do estabelecimento: 04 POLICLINICA (ref.: 05 HOSPITAL GERAL) | atributo vs. referência | +0,1 p.p. | [−6,0; +6,2] | 0,980 | não |
| estabelecimento | tipo do estabelecimento: 07 HOSPITAL ESPECIALIZADO (ref.: 05 HOSPITAL GERAL) | atributo vs. referência | −1,8 p.p. | [−7,7; +4,2] | 0,562 | não |
| estabelecimento | tipo do estabelecimento: 36 CLINICA CENTRO DE ESPECIALIDADE (ref.: 05 HOSPITAL GERAL) | atributo vs. referência | −2,3 p.p. | [−8,6; +4,0] | 0,482 | não |
| estabelecimento | tipo do estabelecimento: 62 HOSPITAL DIA ISOLADO (ref.: 05 HOSPITAL GERAL) | atributo vs. referência | −12,3 p.p. | [−32,9; +8,3] | 0,243 | não |
| município | capital de UF | atributo vs. referência | −9,1 p.p. | [−20,2; +2,0] | 0,108 | não |
| município | log da população do Censo 2022 | +1 DP (DP = 1,610) | +4,8 p.p. | [−0,4; +10,1] | 0,073 | não |
| município | macrorregião: CENTRO OESTE (ref.: SUDESTE) | atributo vs. referência | +21,4 p.p. | [+13,5; +29,2] | 0,000 | sim |
| município | macrorregião: NORDESTE (ref.: SUDESTE) | atributo vs. referência | +14,2 p.p. | [+6,5; +21,9] | 0,000 | sim |
| município | macrorregião: NORTE (ref.: SUDESTE) | atributo vs. referência | +30,5 p.p. | [+21,0; +40,0] | 0,000 | sim |
| município | macrorregião: SUL (ref.: SUDESTE) | atributo vs. referência | −4,9 p.p. | [−10,8; +0,9] | 0,099 | não |
| município | polo da região de saúde (maior população da região) | atributo vs. referência | −0,2 p.p. | [−5,7; +5,4] | 0,949 | não |
| município | hierarquia urbana (REGIC 2018): 1 METROPOLE (ref.: 5 CENTRO LOCAL) | atributo vs. referência | −8,5 p.p. | [−19,7; +2,8] | 0,140 | não |
| município | hierarquia urbana (REGIC 2018): 2 CAPITAL REGIONAL (ref.: 5 CENTRO LOCAL) | atributo vs. referência | −1,7 p.p. | [−12,2; +8,7] | 0,745 | não |
| município | hierarquia urbana (REGIC 2018): 3 CENTRO SUB REGIONAL (ref.: 5 CENTRO LOCAL) | atributo vs. referência | −2,3 p.p. | [−10,4; +5,8] | 0,577 | não |
| município | hierarquia urbana (REGIC 2018): 4 CENTRO DE ZONA (ref.: 5 CENTRO LOCAL) | atributo vs. referência | −4,4 p.p. | [−11,1; +2,3] | 0,194 | não |
| capacidade pré no CNES | vínculos CNES pré das CBO do curso por 10 mil hab. | +1 DP (DP = 3,540) | −1,6 p.p. | [−4,9; +1,7] | 0,337 | não |
| capacidade pré no CNES | vínculos CNES pré de todos os médicos por 10 mil hab. | +1 DP (DP = 57,224) | +3,1 p.p. | [−1,4; +7,6] | 0,182 | não |
| produção pré no SIA | produção SIA pré das CBO-alvo por 10 mil hab. (média mensal) | +1 DP (DP = 630,463) | −1,6 p.p. | [−3,9; +0,8] | 0,196 | não |
| produção pré no SIA | produção SIA pré de todos os profissionais por 10 mil hab. (média mensal) | +1 DP (DP = 19283,386) | +1,0 p.p. | [−1,1; +3,0] | 0,357 | não |
| escassez regional | vínculos das CBO do curso por 10 mil hab. na região de saúde | +1 DP (DP = 2,284) | +6,5 p.p. | [+3,4; +9,6] | 0,000 | sim |
| IVS 2010 oficial | IVS 2010 oficial (contínuo) | +1 DP (DP = 0,105) | +0,1 p.p. | [−3,4; +3,5] | 0,959 | não |

Amostra: 3538 linhas (1328 com outcome = 1), 919 municípios (clusters); 1750 linhas fora (motivos na coluna `nota` do CSV). Média do outcome: 37,5 %.
<!-- P5:ame_e2:fim -->

### 4.3 Presença do município no resultado da adesão (linha separada do §1)

<!-- P5:ame_presenca:inicio -->
| Grupo | Característica | Variação | Efeito marginal médio | IC 95% | p | IC exclui zero |
|---|---|---|---|---|---|---|
| município | capital de UF | atributo vs. referência | +11,2 p.p. | [−18,8; +41,1] | 0,465 | não |
| município | log da população do Censo 2022 | +1 DP (DP = 1,130) | +9,6 p.p. | [+6,7; +12,4] | 0,000 | sim |
| município | macrorregião: CENTRO OESTE (ref.: SUDESTE) | atributo vs. referência | +8,8 p.p. | [+2,2; +15,5] | 0,009 | sim |
| município | macrorregião: NORDESTE (ref.: SUDESTE) | atributo vs. referência | +26,5 p.p. | [+20,2; +32,9] | 0,000 | sim |
| município | macrorregião: NORTE (ref.: SUDESTE) | atributo vs. referência | +21,0 p.p. | [+12,3; +29,7] | 0,000 | sim |
| município | macrorregião: SUL (ref.: SUDESTE) | atributo vs. referência | −0,3 p.p. | [−5,7; +5,1] | 0,906 | não |
| município | polo da região de saúde (maior população da região) | atributo vs. referência | +5,1 p.p. | [−1,5; +11,8] | 0,131 | não |
| município | hierarquia urbana (REGIC 2018): 1 METROPOLE (ref.: 5 CENTRO LOCAL) | atributo vs. referência | −0,9 p.p. | [−9,7; +7,9] | 0,838 | não |
| município | hierarquia urbana (REGIC 2018): 2 CAPITAL REGIONAL (ref.: 5 CENTRO LOCAL) | atributo vs. referência | +9,9 p.p. | [+0,5; +19,3] | 0,038 | sim |
| município | hierarquia urbana (REGIC 2018): 3 CENTRO SUB REGIONAL (ref.: 5 CENTRO LOCAL) | atributo vs. referência | +2,6 p.p. | [−4,3; +9,5] | 0,468 | não |
| município | hierarquia urbana (REGIC 2018): 4 CENTRO DE ZONA (ref.: 5 CENTRO LOCAL) | atributo vs. referência | +6,1 p.p. | [+0,1; +12,1] | 0,047 | sim |
| capacidade pré no CNES | vínculos CNES pré das CBO dos cursos (conjunto alvo) por 10 mil hab. | +1 DP (DP = 15,455) | +6,3 p.p. | [−0,1; +12,6] | 0,054 | não |
| capacidade pré no CNES | vínculos CNES pré de todos os médicos por 10 mil hab. | +1 DP (DP = 48,300) | −6,8 p.p. | [−14,0; +0,5] | 0,069 | não |
| produção pré no SIA | produção SIA pré das CBO-alvo por 10 mil hab. (média mensal) | +1 DP (DP = 688,102) | −0,8 p.p. | [−3,0; +1,4] | 0,484 | não |
| produção pré no SIA | produção SIA pré de todos os profissionais por 10 mil hab. (média mensal) | +1 DP (DP = 13563,154) | +0,8 p.p. | [−1,3; +2,8] | 0,466 | não |
| escassez regional | vínculos das CBO dos cursos (conjunto alvo) por 10 mil hab. na região de saúde | +1 DP (DP = 12,394) | +0,3 p.p. | [−2,3; +2,9] | 0,822 | não |
| IVS 2010 oficial | IVS 2010 oficial (contínuo) | +1 DP (DP = 0,133) | −3,4 p.p. | [−6,7; −0,1] | 0,046 | sim |

Amostra: 2697 linhas (1161 com outcome = 1), 2697 municípios (clusters); 2 linhas fora (motivos na coluna `nota` do CSV). Média do outcome: 43,0 %.
<!-- P5:ame_presenca:fim -->

### 4.4 Sensibilidade fora do protocolo: todos os cursos

Pedido:

<!-- P5:ame_sensibilidade_e1:inicio -->
| Grupo | Característica | Variação | Efeito marginal médio | IC 95% | p | IC exclui zero |
|---|---|---|---|---|---|---|
| estabelecimento | gestão: DUPLA (ref.: MUNICIPAL) | atributo vs. referência | −3,6 p.p. | [−12,6; +5,3] | 0,424 | não |
| estabelecimento | gestão: ESTADUAL (ref.: MUNICIPAL) | atributo vs. referência | −9,8 p.p. | [−15,9; −3,8] | 0,001 | sim |
| estabelecimento | natureza jurídica: PRIVADO (ref.: PUBLICO) | atributo vs. referência | +6,1 p.p. | [−11,1; +23,4] | 0,487 | não |
| estabelecimento | natureza jurídica: SEM FINS LUCRATIVOS (ref.: PUBLICO) | atributo vs. referência | −5,9 p.p. | [−11,1; −0,8] | 0,024 | sim |
| estabelecimento | tipo do estabelecimento: 04 POLICLINICA (ref.: 05 HOSPITAL GERAL) | atributo vs. referência | −1,1 p.p. | [−6,1; +3,8] | 0,652 | não |
| estabelecimento | tipo do estabelecimento: 07 HOSPITAL ESPECIALIZADO (ref.: 05 HOSPITAL GERAL) | atributo vs. referência | −6,8 p.p. | [−16,4; +2,9] | 0,169 | não |
| estabelecimento | tipo do estabelecimento: 36 CLINICA CENTRO DE ESPECIALIDADE (ref.: 05 HOSPITAL GERAL) | atributo vs. referência | −3,2 p.p. | [−8,2; +1,9] | 0,217 | não |
| estabelecimento | tipo do estabelecimento: 62 HOSPITAL DIA ISOLADO (ref.: 05 HOSPITAL GERAL) | atributo vs. referência | −2,9 p.p. | [−21,4; +15,7] | 0,763 | não |
| estabelecimento | tipo do estabelecimento: 70 CENTRO DE ATENCAO PSICOSSOCIAL (ref.: 05 HOSPITAL GERAL) | atributo vs. referência | +16,9 p.p. | [+3,4; +30,3] | 0,014 | sim |
| município | capital de UF | atributo vs. referência | +2,9 p.p. | [−9,2; +15,1] | 0,634 | não |
| município | log da população do Censo 2022 | +1 DP (DP = 1,665) | −9,9 p.p. | [−16,5; −3,4] | 0,003 | sim |
| município | macrorregião: CENTRO OESTE (ref.: SUDESTE) | atributo vs. referência | +4,4 p.p. | [−6,1; +14,8] | 0,413 | não |
| município | macrorregião: NORDESTE (ref.: SUDESTE) | atributo vs. referência | +8,1 p.p. | [−1,3; +17,4] | 0,090 | não |
| município | macrorregião: NORTE (ref.: SUDESTE) | atributo vs. referência | −0,4 p.p. | [−11,1; +10,2] | 0,936 | não |
| município | macrorregião: SUL (ref.: SUDESTE) | atributo vs. referência | +14,8 p.p. | [+5,7; +23,9] | 0,001 | sim |
| município | polo da região de saúde (maior população da região) | atributo vs. referência | −4,5 p.p. | [−11,7; +2,7] | 0,221 | não |
| município | hierarquia urbana (REGIC 2018): 1 METROPOLE (ref.: 5 CENTRO LOCAL) | atributo vs. referência | +7,4 p.p. | [−3,8; +18,6] | 0,193 | não |
| município | hierarquia urbana (REGIC 2018): 2 CAPITAL REGIONAL (ref.: 5 CENTRO LOCAL) | atributo vs. referência | +0,3 p.p. | [−10,2; +10,7] | 0,963 | não |
| município | hierarquia urbana (REGIC 2018): 3 CENTRO SUB REGIONAL (ref.: 5 CENTRO LOCAL) | atributo vs. referência | −3,9 p.p. | [−12,6; +4,8] | 0,378 | não |
| município | hierarquia urbana (REGIC 2018): 4 CENTRO DE ZONA (ref.: 5 CENTRO LOCAL) | atributo vs. referência | −5,0 p.p. | [−12,0; +1,9] | 0,155 | não |
| capacidade pré no CNES | vínculos CNES pré das CBO dos cursos (conjunto alvo) por 10 mil hab. | +1 DP (DP = 22,452) | +22,6 p.p. | [+11,4; +33,7] | 0,000 | sim |
| capacidade pré no CNES | vínculos CNES pré de todos os médicos por 10 mil hab. | +1 DP (DP = 62,978) | −21,6 p.p. | [−32,1; −11,0] | 0,000 | sim |
| produção pré no SIA | produção SIA pré das CBO-alvo por 10 mil hab. (média mensal) | +1 DP (DP = 597,114) | −1,8 p.p. | [−4,8; +1,2] | 0,241 | não |
| produção pré no SIA | produção SIA pré de todos os profissionais por 10 mil hab. (média mensal) | +1 DP (DP = 19333,543) | −0,9 p.p. | [−4,7; +2,9] | 0,643 | não |
| escassez regional | vínculos das CBO dos cursos (conjunto alvo) por 10 mil hab. na região de saúde | +1 DP (DP = 15,374) | −6,1 p.p. | [−10,0; −2,2] | 0,002 | sim |
| IVS 2010 oficial | IVS 2010 oficial (contínuo) | +1 DP (DP = 0,098) | −1,5 p.p. | [−4,9; +1,9] | 0,396 | não |

Amostra: 10057 linhas (5278 com outcome = 1), 1161 municípios (clusters); 16 linhas fora (motivos na coluna `nota` do CSV). Média do outcome: 52,5 %.
<!-- P5:ame_sensibilidade_e1:fim -->

Priorização:

<!-- P5:ame_sensibilidade_e2:inicio -->
| Grupo | Característica | Variação | Efeito marginal médio | IC 95% | p | IC exclui zero |
|---|---|---|---|---|---|---|
| estabelecimento | gestão: DUPLA (ref.: MUNICIPAL) | atributo vs. referência | +3,0 p.p. | [−3,5; +9,5] | 0,371 | não |
| estabelecimento | gestão: ESTADUAL (ref.: MUNICIPAL) | atributo vs. referência | −2,0 p.p. | [−6,5; +2,5] | 0,387 | não |
| estabelecimento | natureza jurídica: PRIVADO (ref.: PUBLICO) | atributo vs. referência | +0,8 p.p. | [−15,3; +16,9] | 0,923 | não |
| estabelecimento | natureza jurídica: SEM FINS LUCRATIVOS (ref.: PUBLICO) | atributo vs. referência | −5,7 p.p. | [−9,6; −1,8] | 0,004 | sim |
| estabelecimento | tipo do estabelecimento: 04 POLICLINICA (ref.: 05 HOSPITAL GERAL) | atributo vs. referência | −0,1 p.p. | [−5,2; +5,0] | 0,979 | não |
| estabelecimento | tipo do estabelecimento: 07 HOSPITAL ESPECIALIZADO (ref.: 05 HOSPITAL GERAL) | atributo vs. referência | +1,1 p.p. | [−4,2; +6,4] | 0,690 | não |
| estabelecimento | tipo do estabelecimento: 36 CLINICA CENTRO DE ESPECIALIDADE (ref.: 05 HOSPITAL GERAL) | atributo vs. referência | −4,1 p.p. | [−9,4; +1,1] | 0,123 | não |
| estabelecimento | tipo do estabelecimento: 62 HOSPITAL DIA ISOLADO (ref.: 05 HOSPITAL GERAL) | atributo vs. referência | −8,7 p.p. | [−25,8; +8,3] | 0,315 | não |
| município | capital de UF | atributo vs. referência | +1,0 p.p. | [−13,2; +15,3] | 0,886 | não |
| município | log da população do Censo 2022 | +1 DP (DP = 1,625) | −1,5 p.p. | [−6,6; +3,6] | 0,558 | não |
| município | macrorregião: CENTRO OESTE (ref.: SUDESTE) | atributo vs. referência | +18,1 p.p. | [+9,6; +26,6] | 0,000 | sim |
| município | macrorregião: NORDESTE (ref.: SUDESTE) | atributo vs. referência | +13,7 p.p. | [+5,5; +21,8] | 0,001 | sim |
| município | macrorregião: NORTE (ref.: SUDESTE) | atributo vs. referência | +27,6 p.p. | [+16,9; +38,3] | 0,000 | sim |
| município | macrorregião: SUL (ref.: SUDESTE) | atributo vs. referência | −4,2 p.p. | [−10,5; +2,0] | 0,184 | não |
| município | polo da região de saúde (maior população da região) | atributo vs. referência | +6,3 p.p. | [+0,6; +12,0] | 0,029 | sim |
| município | hierarquia urbana (REGIC 2018): 1 METROPOLE (ref.: 5 CENTRO LOCAL) | atributo vs. referência | −2,9 p.p. | [−13,1; +7,3] | 0,583 | não |
| município | hierarquia urbana (REGIC 2018): 2 CAPITAL REGIONAL (ref.: 5 CENTRO LOCAL) | atributo vs. referência | +4,9 p.p. | [−5,2; +15,0] | 0,340 | não |
| município | hierarquia urbana (REGIC 2018): 3 CENTRO SUB REGIONAL (ref.: 5 CENTRO LOCAL) | atributo vs. referência | +3,2 p.p. | [−4,2; +10,7] | 0,393 | não |
| município | hierarquia urbana (REGIC 2018): 4 CENTRO DE ZONA (ref.: 5 CENTRO LOCAL) | atributo vs. referência | +1,4 p.p. | [−4,7; +7,5] | 0,650 | não |
| capacidade pré no CNES | vínculos CNES pré das CBO dos cursos (conjunto alvo) por 10 mil hab. | +1 DP (DP = 21,607) | −4,6 p.p. | [−17,5; +8,2] | 0,480 | não |
| capacidade pré no CNES | vínculos CNES pré de todos os médicos por 10 mil hab. | +1 DP (DP = 58,283) | +3,8 p.p. | [−10,5; +18,1] | 0,603 | não |
| produção pré no SIA | produção SIA pré das CBO-alvo por 10 mil hab. (média mensal) | +1 DP (DP = 635,462) | −2,7 p.p. | [−5,5; +0,1] | 0,054 | não |
| produção pré no SIA | produção SIA pré de todos os profissionais por 10 mil hab. (média mensal) | +1 DP (DP = 19351,050) | +2,1 p.p. | [−0,2; +4,5] | 0,074 | não |
| escassez regional | vínculos das CBO dos cursos (conjunto alvo) por 10 mil hab. na região de saúde | +1 DP (DP = 13,553) | +6,7 p.p. | [+3,6; +9,8] | 0,000 | sim |
| IVS 2010 oficial | IVS 2010 oficial (contínuo) | +1 DP (DP = 0,105) | +1,9 p.p. | [−1,7; +5,5] | 0,303 | não |

Amostra: 5097 linhas (1952 com outcome = 1), 1095 municípios (clusters); 191 linhas fora (motivos na coluna `nota` do CSV). Média do outcome: 38,3 %.
<!-- P5:ame_sensibilidade_e2:fim -->

## 5. Quanto cada grupo de características separa os casos (T5.1c)

O que mede cada coluna:
- a queda do pseudo-R² de McFadden quando o grupo sai do modelo, com a mesma
  amostra;
- grupos que se sobrepõem dividem a informação, por isso as colunas não somam
  o total;
- "só efeito fixo" é o pseudo-R² do modelo só com o curso (ou só com a
  constante, no modelo de presença).

<!-- P5:blocos:inicio -->
| Modelo | Pseudo-R² completo | Só efeito fixo (ou constante) | estabelecimento | município | capacidade pré no CNES | produção pré no SIA | escassez regional | IVS 2010 oficial |
|---|---|---|---|---|---|---|---|---|
| Pedido (E1, célula) | 0,082 | 0,025 | 0,008 | 0,026 | 0,002 | 0,000 | 0,001 | 0,000 |
| Priorização (E2, célula pedida) | 0,103 | 0,059 | 0,002 | 0,028 | 0,001 | 0,001 | 0,006 | 0,000 |
| Presença (E1, município) | 0,076 | 0,000 | não se aplica | 0,063 | 0,001 | 0,000 | 0,000 | 0,001 |
| Pedido, todos os cursos (sensibilidade) | 0,103 | 0,029 | 0,008 | 0,028 | 0,008 | 0,001 | 0,004 | 0,000 |
| Priorização, todos os cursos (sensibilidade) | 0,092 | 0,048 | 0,002 | 0,027 | 0,000 | 0,002 | 0,006 | 0,000 |
<!-- P5:blocos:fim -->

## 6. Nos cortes do IVS (T5.2a e T5.2b)

Como ler a tabela:
- salto = lado de bolsa maior menos lado de bolsa menor, com h = 0,050 e kernel
  triangular;
- "empilhado" junta os cortes 0,300 e 0,400 com retas próprias e salto comum;
- por célula, há efeito fixo de curso e cluster por município;
- T5.2b acrescenta as covariáveis pré-determinadas do §2, sem o IVS;
- o q é o de Benjamini–Krieger–Yekutieli entre as linhas do protocolo;
- as leituras alternativas (fração priorizada sobre o cardápio) ficam fora do
  BKY.

<!-- P5:t52:inicio -->
| Esp. | Unidade | Outcome | Corte | Linhas na janela | Municípios abaixo / acima | Salto | IC 95% | p | q BKY | Média abaixo | No protocolo |
|---|---|---|---|---|---|---|---|---|---|---|---|
| T5.2a | celula | E1_pedida | 0,300 | 4126 | 150 / 118 | +20,2 p.p. | [+3,0; +37,3] | 0,021 | 0,602 | 41,5 % | sim |
| T5.2a | celula | E1_pedida | 0,400 | 1989 | 143 / 175 | +3,5 p.p. | [−12,6; +19,6] | 0,668 | 1,000 | 56,3 % | sim |
| T5.2a | celula | E1_pedida | empilhado | 6115 | 293 / 293 | +14,7 p.p. | [+1,8; +27,6] | 0,025 | 0,602 | 46,4 % | sim |
| T5.2b | celula | E1_pedida | 0,300 | 2949 | 135 / 106 | +18,4 p.p. | [+0,1; +36,7] | 0,049 | 0,850 | 40,0 % | sim |
| T5.2b | celula | E1_pedida | 0,400 | 1415 | 135 / 154 | −8,1 p.p. | [−23,2; +6,9] | 0,290 | 1,000 | 54,1 % | sim |
| T5.2b | celula | E1_pedida | empilhado | 4364 | 270 / 260 | +11,6 p.p. | [−2,6; +25,8] | 0,108 | 1,000 | 44,7 % | sim |
| T5.2a | celula | E2_priorizada | 0,300 | 1983 | 149 / 117 | −0,0 p.p. | [−18,4; +18,4] | 0,999 | 1,000 | 43,3 % | sim |
| T5.2a | celula | E2_priorizada | 0,400 | 1214 | 140 / 173 | −0,9 p.p. | [−13,2; +11,5] | 0,891 | 1,000 | 40,5 % | sim |
| T5.2a | celula | E2_priorizada | empilhado | 3197 | 289 / 290 | −0,3 p.p. | [−12,4; +11,8] | 0,961 | 1,000 | 42,2 % | sim |
| T5.2b | celula | E2_priorizada | 0,300 | 1371 | 119 / 96 | −1,1 p.p. | [−20,0; +17,7] | 0,907 | 1,000 | 44,2 % | sim |
| T5.2b | celula | E2_priorizada | 0,400 | 826 | 119 / 134 | −1,8 p.p. | [−13,4; +9,8] | 0,760 | 1,000 | 37,1 % | sim |
| T5.2b | celula | E2_priorizada | empilhado | 2197 | 238 / 230 | +1,9 p.p. | [−9,9; +13,7] | 0,752 | 1,000 | 41,3 % | sim |
| T5.2a | celula | E2_priorizada_cardapio | 0,300 | 4126 | 150 / 118 | +6,8 p.p. | [−4,8; +18,3] | 0,250 | — | 18,0 % | não (leitura alternativa) |
| T5.2a | celula | E2_priorizada_cardapio | 0,400 | 1989 | 143 / 175 | −0,8 p.p. | [−9,8; +8,2] | 0,862 | — | 22,8 % | não (leitura alternativa) |
| T5.2a | celula | E2_priorizada_cardapio | empilhado | 6115 | 293 / 293 | +4,4 p.p. | [−3,8; +12,6] | 0,295 | — | 19,6 % | não (leitura alternativa) |
| T5.2b | celula | E2_priorizada_cardapio | 0,300 | 2949 | 135 / 106 | +5,9 p.p. | [−3,7; +15,5] | 0,227 | — | 17,7 % | não (leitura alternativa) |
| T5.2b | celula | E2_priorizada_cardapio | 0,400 | 1415 | 135 / 154 | −3,7 p.p. | [−12,5; +5,0] | 0,402 | — | 20,0 % | não (leitura alternativa) |
| T5.2b | celula | E2_priorizada_cardapio | empilhado | 4364 | 270 / 260 | +5,5 p.p. | [−1,4; +12,5] | 0,120 | — | 18,5 % | não (leitura alternativa) |
| T5.2a | municipio | E1_frac_pedidas | 0,300 | 268 | 150 / 118 | −0,1 p.p. | [−16,0; +15,8] | 0,990 | 1,000 | 66,9 % | sim |
| T5.2a | municipio | E1_frac_pedidas | 0,400 | 318 | 143 / 175 | −4,0 p.p. | [−17,4; +9,4] | 0,556 | 1,000 | 71,9 % | sim |
| T5.2a | municipio | E1_frac_pedidas | empilhado | 586 | 293 / 293 | −2,3 p.p. | [−12,5; +8,0] | 0,662 | 1,000 | 69,4 % | sim |
| T5.2b | municipio | E1_frac_pedidas | 0,300 | 267 | 149 / 118 | +2,2 p.p. | [−11,3; +15,8] | 0,748 | 1,000 | 67,3 % | sim |
| T5.2b | municipio | E1_frac_pedidas | 0,400 | 318 | 143 / 175 | −4,7 p.p. | [−17,7; +8,2] | 0,474 | 1,000 | 71,9 % | sim |
| T5.2b | municipio | E1_frac_pedidas | empilhado | 585 | 292 / 293 | −0,5 p.p. | [−10,1; +9,2] | 0,922 | 1,000 | 69,6 % | sim |
| T5.2a | municipio | E2_frac_priorizadas | 0,300 | 266 | 149 / 117 | −3,5 p.p. | [−21,9; +14,9] | 0,710 | 1,000 | 39,0 % | sim |
| T5.2a | municipio | E2_frac_priorizadas | 0,400 | 313 | 140 / 173 | −10,8 p.p. | [−26,0; +4,4] | 0,162 | 1,000 | 38,7 % | sim |
| T5.2a | municipio | E2_frac_priorizadas | empilhado | 579 | 289 / 290 | −7,6 p.p. | [−19,3; +4,2] | 0,208 | 1,000 | 38,9 % | sim |
| T5.2b | municipio | E2_frac_priorizadas | 0,300 | 265 | 148 / 117 | −0,4 p.p. | [−18,6; +17,8] | 0,968 | 1,000 | 38,6 % | sim |
| T5.2b | municipio | E2_frac_priorizadas | 0,400 | 313 | 140 / 173 | −9,1 p.p. | [−24,7; +6,4] | 0,250 | 1,000 | 38,7 % | sim |
| T5.2b | municipio | E2_frac_priorizadas | empilhado | 578 | 288 / 290 | −6,0 p.p. | [−17,7; +5,7] | 0,316 | 1,000 | 38,7 % | sim |
| T5.2a | municipio | E2_frac_priorizadas_cardapio | 0,300 | 268 | 150 / 118 | +0,7 p.p. | [−13,9; +15,2] | 0,929 | — | 22,7 % | não (leitura alternativa) |
| T5.2a | municipio | E2_frac_priorizadas_cardapio | 0,400 | 318 | 143 / 175 | −4,9 p.p. | [−16,8; +7,0] | 0,419 | — | 25,6 % | não (leitura alternativa) |
| T5.2a | municipio | E2_frac_priorizadas_cardapio | empilhado | 586 | 293 / 293 | −2,4 p.p. | [−11,7; +6,8] | 0,604 | — | 24,1 % | não (leitura alternativa) |
| T5.2b | municipio | E2_frac_priorizadas_cardapio | 0,300 | 267 | 149 / 118 | +2,8 p.p. | [−11,4; +16,9] | 0,702 | — | 22,8 % | não (leitura alternativa) |
| T5.2b | municipio | E2_frac_priorizadas_cardapio | 0,400 | 318 | 143 / 175 | −3,8 p.p. | [−15,7; +8,1] | 0,528 | — | 25,6 % | não (leitura alternativa) |
| T5.2b | municipio | E2_frac_priorizadas_cardapio | empilhado | 585 | 292 / 293 | −1,0 p.p. | [−10,0; +8,0] | 0,831 | — | 24,2 % | não (leitura alternativa) |
| T5.2a | municipio | E1_presenca | 0,300 | 675 | 399 / 276 | −3,6 p.p. | [−20,1; +12,9] | 0,670 | 1,000 | 37,6 % | sim |
| T5.2a | municipio | E1_presenca | 0,400 | 585 | 270 / 315 | −10,9 p.p. | [−28,0; +6,1] | 0,210 | 1,000 | 53,0 % | sim |
| T5.2a | municipio | E1_presenca | empilhado | 1260 | 669 / 591 | −7,0 p.p. | [−18,9; +4,8] | 0,244 | 1,000 | 43,8 % | sim |
| T5.2b | municipio | E1_presenca | 0,300 | 674 | 398 / 276 | −5,1 p.p. | [−19,9; +9,6] | 0,494 | 1,000 | 37,4 % | sim |
| T5.2b | municipio | E1_presenca | 0,400 | 585 | 270 / 315 | −10,1 p.p. | [−25,9; +5,8] | 0,213 | 1,000 | 53,0 % | sim |
| T5.2b | municipio | E1_presenca | empilhado | 1259 | 668 / 591 | −6,4 p.p. | [−17,4; +4,5] | 0,248 | 1,000 | 43,7 % | sim |
<!-- P5:t52:fim -->

## 7. Quadro dos ciclos 1 e 2 (T5.3)

Como ler a tabela:
- é um Poisson do número de células e do número de vagas (imediatas + cadastro
  reserva) por município;
- entram todos os municípios com IVS oficial, valendo zero quem não teve célula
  no quadro;
- a razão de taxas diz por quanto o número esperado se multiplica: por
  desvio-padrão, nas contínuas, ou com o atributo, nas categorias;
- o EP é robusto.

Serve de base ao A4 do P2.

<!-- P5:t53:inicio -->
| Ciclo | Outcome | Característica | Variação | Razão de taxas | IC 95% | p | IC exclui 1 |
|---|---|---|---|---|---|---|---|
| 1 | células | log da população do Censo 2022 | +1 DP | 2,98 | [2,35; 3,77] | 0,000 | sim |
| 1 | células | hierarquia urbana (REGIC 2018): 1 METROPOLE (ref.: 5 CENTRO LOCAL) | atributo vs. referência | 0,54 | [0,24; 1,18] | 0,123 | não |
| 1 | células | hierarquia urbana (REGIC 2018): 2 CAPITAL REGIONAL (ref.: 5 CENTRO LOCAL) | atributo vs. referência | 1,54 | [0,77; 3,10] | 0,224 | não |
| 1 | células | hierarquia urbana (REGIC 2018): 3 CENTRO SUB REGIONAL (ref.: 5 CENTRO LOCAL) | atributo vs. referência | 2,44 | [1,42; 4,19] | 0,001 | sim |
| 1 | células | hierarquia urbana (REGIC 2018): 4 CENTRO DE ZONA (ref.: 5 CENTRO LOCAL) | atributo vs. referência | 2,57 | [1,62; 4,07] | 0,000 | sim |
| 1 | células | capital de UF | atributo vs. referência | 0,73 | [0,40; 1,33] | 0,307 | não |
| 1 | células | macrorregião: CENTRO OESTE (ref.: SUDESTE) | atributo vs. referência | 0,80 | [0,49; 1,30] | 0,363 | não |
| 1 | células | macrorregião: NORDESTE (ref.: SUDESTE) | atributo vs. referência | 0,93 | [0,56; 1,57] | 0,799 | não |
| 1 | células | macrorregião: NORTE (ref.: SUDESTE) | atributo vs. referência | 1,26 | [0,73; 2,18] | 0,401 | não |
| 1 | células | macrorregião: SUL (ref.: SUDESTE) | atributo vs. referência | 0,44 | [0,28; 0,67] | 0,000 | sim |
| 1 | células | polo da região de saúde (maior população da região) | atributo vs. referência | 2,98 | [1,99; 4,45] | 0,000 | sim |
| 1 | células | vínculos CNES pré das CBO dos cursos (conjunto alvo) por 10 mil hab. | +1 DP | 1,37 | [0,98; 1,93] | 0,068 | não |
| 1 | células | vínculos CNES pré de todos os médicos por 10 mil hab. | +1 DP | 0,92 | [0,66; 1,30] | 0,647 | não |
| 1 | células | produção SIA pré das CBO-alvo por 10 mil hab. (média mensal) | +1 DP | 1,12 | [1,05; 1,19] | 0,001 | sim |
| 1 | células | produção SIA pré de todos os profissionais por 10 mil hab. (média mensal) | +1 DP | 0,94 | [0,84; 1,06] | 0,329 | não |
| 1 | células | vínculos das CBO dos cursos (conjunto alvo) por 10 mil hab. na região de saúde | +1 DP | 0,27 | [0,20; 0,37] | 0,000 | sim |
| 1 | células | IVS 2010 oficial (contínuo) | +1 DP | 0,75 | [0,60; 0,95] | 0,016 | sim |
| 1 | vagas | log da população do Censo 2022 | +1 DP | 2,64 | [2,03; 3,42] | 0,000 | sim |
| 1 | vagas | hierarquia urbana (REGIC 2018): 1 METROPOLE (ref.: 5 CENTRO LOCAL) | atributo vs. referência | 0,68 | [0,26; 1,76] | 0,424 | não |
| 1 | vagas | hierarquia urbana (REGIC 2018): 2 CAPITAL REGIONAL (ref.: 5 CENTRO LOCAL) | atributo vs. referência | 2,16 | [0,99; 4,75] | 0,054 | não |
| 1 | vagas | hierarquia urbana (REGIC 2018): 3 CENTRO SUB REGIONAL (ref.: 5 CENTRO LOCAL) | atributo vs. referência | 2,65 | [1,37; 5,12] | 0,004 | sim |
| 1 | vagas | hierarquia urbana (REGIC 2018): 4 CENTRO DE ZONA (ref.: 5 CENTRO LOCAL) | atributo vs. referência | 2,66 | [1,49; 4,73] | 0,001 | sim |
| 1 | vagas | capital de UF | atributo vs. referência | 1,53 | [0,73; 3,21] | 0,258 | não |
| 1 | vagas | macrorregião: CENTRO OESTE (ref.: SUDESTE) | atributo vs. referência | 0,62 | [0,36; 1,08] | 0,091 | não |
| 1 | vagas | macrorregião: NORDESTE (ref.: SUDESTE) | atributo vs. referência | 0,55 | [0,30; 1,00] | 0,051 | não |
| 1 | vagas | macrorregião: NORTE (ref.: SUDESTE) | atributo vs. referência | 0,97 | [0,50; 1,86] | 0,921 | não |
| 1 | vagas | macrorregião: SUL (ref.: SUDESTE) | atributo vs. referência | 0,33 | [0,21; 0,51] | 0,000 | sim |
| 1 | vagas | polo da região de saúde (maior população da região) | atributo vs. referência | 3,25 | [2,00; 5,30] | 0,000 | sim |
| 1 | vagas | vínculos CNES pré das CBO dos cursos (conjunto alvo) por 10 mil hab. | +1 DP | 1,60 | [1,11; 2,31] | 0,012 | sim |
| 1 | vagas | vínculos CNES pré de todos os médicos por 10 mil hab. | +1 DP | 0,81 | [0,56; 1,16] | 0,251 | não |
| 1 | vagas | produção SIA pré das CBO-alvo por 10 mil hab. (média mensal) | +1 DP | 1,12 | [1,04; 1,21] | 0,003 | sim |
| 1 | vagas | produção SIA pré de todos os profissionais por 10 mil hab. (média mensal) | +1 DP | 0,92 | [0,80; 1,07] | 0,271 | não |
| 1 | vagas | vínculos das CBO dos cursos (conjunto alvo) por 10 mil hab. na região de saúde | +1 DP | 0,23 | [0,15; 0,36] | 0,000 | sim |
| 1 | vagas | IVS 2010 oficial (contínuo) | +1 DP | 0,78 | [0,59; 1,03] | 0,085 | não |
| 2 | células | log da população do Censo 2022 | +1 DP | 3,00 | [2,40; 3,75] | 0,000 | sim |
| 2 | células | hierarquia urbana (REGIC 2018): 1 METROPOLE (ref.: 5 CENTRO LOCAL) | atributo vs. referência | 0,74 | [0,35; 1,57] | 0,430 | não |
| 2 | células | hierarquia urbana (REGIC 2018): 2 CAPITAL REGIONAL (ref.: 5 CENTRO LOCAL) | atributo vs. referência | 2,35 | [1,24; 4,47] | 0,009 | sim |
| 2 | células | hierarquia urbana (REGIC 2018): 3 CENTRO SUB REGIONAL (ref.: 5 CENTRO LOCAL) | atributo vs. referência | 2,62 | [1,59; 4,32] | 0,000 | sim |
| 2 | células | hierarquia urbana (REGIC 2018): 4 CENTRO DE ZONA (ref.: 5 CENTRO LOCAL) | atributo vs. referência | 2,72 | [1,84; 4,03] | 0,000 | sim |
| 2 | células | capital de UF | atributo vs. referência | 0,95 | [0,51; 1,74] | 0,859 | não |
| 2 | células | macrorregião: CENTRO OESTE (ref.: SUDESTE) | atributo vs. referência | 0,62 | [0,40; 0,97] | 0,037 | sim |
| 2 | células | macrorregião: NORDESTE (ref.: SUDESTE) | atributo vs. referência | 1,25 | [0,76; 2,04] | 0,382 | não |
| 2 | células | macrorregião: NORTE (ref.: SUDESTE) | atributo vs. referência | 1,38 | [0,79; 2,41] | 0,260 | não |
| 2 | células | macrorregião: SUL (ref.: SUDESTE) | atributo vs. referência | 0,48 | [0,33; 0,69] | 0,000 | sim |
| 2 | células | polo da região de saúde (maior população da região) | atributo vs. referência | 1,20 | [0,82; 1,76] | 0,355 | não |
| 2 | células | vínculos CNES pré das CBO dos cursos (conjunto alvo) por 10 mil hab. | +1 DP | 1,68 | [1,17; 2,43] | 0,005 | sim |
| 2 | células | vínculos CNES pré de todos os médicos por 10 mil hab. | +1 DP | 0,73 | [0,50; 1,06] | 0,094 | não |
| 2 | células | produção SIA pré das CBO-alvo por 10 mil hab. (média mensal) | +1 DP | 1,10 | [1,01; 1,19] | 0,028 | sim |
| 2 | células | produção SIA pré de todos os profissionais por 10 mil hab. (média mensal) | +1 DP | 0,94 | [0,83; 1,06] | 0,291 | não |
| 2 | células | vínculos das CBO dos cursos (conjunto alvo) por 10 mil hab. na região de saúde | +1 DP | 0,85 | [0,66; 1,07] | 0,170 | não |
| 2 | células | IVS 2010 oficial (contínuo) | +1 DP | 1,03 | [0,80; 1,33] | 0,815 | não |
| 2 | vagas | log da população do Censo 2022 | +1 DP | 2,85 | [2,20; 3,70] | 0,000 | sim |
| 2 | vagas | hierarquia urbana (REGIC 2018): 1 METROPOLE (ref.: 5 CENTRO LOCAL) | atributo vs. referência | 1,21 | [0,47; 3,08] | 0,693 | não |
| 2 | vagas | hierarquia urbana (REGIC 2018): 2 CAPITAL REGIONAL (ref.: 5 CENTRO LOCAL) | atributo vs. referência | 3,17 | [1,37; 7,37] | 0,007 | sim |
| 2 | vagas | hierarquia urbana (REGIC 2018): 3 CENTRO SUB REGIONAL (ref.: 5 CENTRO LOCAL) | atributo vs. referência | 3,25 | [1,63; 6,50] | 0,001 | sim |
| 2 | vagas | hierarquia urbana (REGIC 2018): 4 CENTRO DE ZONA (ref.: 5 CENTRO LOCAL) | atributo vs. referência | 2,67 | [1,57; 4,53] | 0,000 | sim |
| 2 | vagas | capital de UF | atributo vs. referência | 1,09 | [0,52; 2,32] | 0,817 | não |
| 2 | vagas | macrorregião: CENTRO OESTE (ref.: SUDESTE) | atributo vs. referência | 0,56 | [0,33; 0,95] | 0,031 | sim |
| 2 | vagas | macrorregião: NORDESTE (ref.: SUDESTE) | atributo vs. referência | 1,12 | [0,65; 1,93] | 0,687 | não |
| 2 | vagas | macrorregião: NORTE (ref.: SUDESTE) | atributo vs. referência | 1,57 | [0,81; 3,04] | 0,178 | não |
| 2 | vagas | macrorregião: SUL (ref.: SUDESTE) | atributo vs. referência | 0,33 | [0,22; 0,49] | 0,000 | sim |
| 2 | vagas | polo da região de saúde (maior população da região) | atributo vs. referência | 1,02 | [0,66; 1,57] | 0,934 | não |
| 2 | vagas | vínculos CNES pré das CBO dos cursos (conjunto alvo) por 10 mil hab. | +1 DP | 1,88 | [1,36; 2,59] | 0,000 | sim |
| 2 | vagas | vínculos CNES pré de todos os médicos por 10 mil hab. | +1 DP | 0,64 | [0,45; 0,90] | 0,012 | sim |
| 2 | vagas | produção SIA pré das CBO-alvo por 10 mil hab. (média mensal) | +1 DP | 1,08 | [0,98; 1,20] | 0,112 | não |
| 2 | vagas | produção SIA pré de todos os profissionais por 10 mil hab. (média mensal) | +1 DP | 0,92 | [0,82; 1,04] | 0,190 | não |
| 2 | vagas | vínculos das CBO dos cursos (conjunto alvo) por 10 mil hab. na região de saúde | +1 DP | 0,91 | [0,70; 1,18] | 0,484 | não |
| 2 | vagas | IVS 2010 oficial (contínuo) | +1 DP | 0,97 | [0,69; 1,37] | 0,865 | não |

| Ciclo | Outcome | Municípios | Soma do outcome | Pseudo-R² (deviance) | Linhas fora |
|---|---|---|---|---|---|
| 1 | n_celulas_c1 | 5564 | 1289 | 0,595 | 1 |
| 1 | vagas_c1 | 5564 | 1816 | 0,596 | 1 |
| 2 | n_celulas_c2 | 5564 | 1545 | 0,555 | 1 |
| 2 | vagas_c2 | 5564 | 2886 | 0,572 | 1 |
<!-- P5:t53:fim -->

## 8. Figuras

Toda figura traz um bloco "Como ler" dentro da imagem.

<!-- P5:figuras:inicio -->
| Arquivo (em `output/rdd_bolsa/P5_figuras/`) | O que mostra |
|---|---|
| `P5_T51_efeitos_marginais.png` | efeitos marginais médios do pedido (E1) e da priorização (E2), T5.1c |
| `P5_T51_contribuicao_blocos.png` | queda do pseudo-R² sem cada grupo de características (pedido, priorização, presença), T5.1c |
| `P5_T52_rdd_municipio_empilhado.png` | RDD por município, fração pedida e fração priorizada, cortes empilhados, T5.2a |
| `P5_T52_rdd_celula_empilhado.png` | RDD por célula com efeito fixo de curso, pedida e priorizada, cortes empilhados, T5.2a |
| `P5_T53_razao_taxas.png` | razões de taxas do Poisson do quadro dos ciclos 1 e 2, T5.3 |
<!-- P5:figuras:fim -->

## 9. Desvios

As decisões de implementação estão em `P5_resumo.json` (`decisoes`).

<!-- P5:desvios:inicio -->
1. **Cursos do ciclo 3 fora da ponte curso–CBO.** A ponte do a09 cobre os cursos da grade dos ciclos 1 e 2; o cardápio do ciclo 3 tem também os cursos 17, 18, 19, 20, 21, 22, 23, 24, sem CBO na ponte, e o protocolo manda usar a ponte do a09 para a capacidade do curso. *Resolução:* Vínculos do curso e escassez regional do curso ficam ausentes nessas células (nada imputado). A especificação principal é de casos completos e as deixa de fora (contadas). Uma sensibilidade rotulada fora do protocolo usa a capacidade e a escassez do conjunto alvo em todos os cursos.
2. **Covariáveis do curso nos modelos municipais.** A presença (§1), o T5.2 por município e o T5.3 são no nível do município, que não tem curso. *Resolução:* Capacidade e escassez do curso trocadas pelas do conjunto alvo_pmme (união das CBO dos cursos da ponte); registrado nas decisões.
3. **Fração priorizada no T5.2.** O §3 diz 'fração de células pedidas e da priorizada' sem dizer o denominador da priorizada. *Resolução:* Principal sobre as células pedidas (a unidade do E2 no §1); sobre o cardápio, como leitura alternativa rotulada e fora do BKY.
4. **Municípios sem região de saúde ou sem IVS.** Sem região de saúde na tabela do TabNet: 110002; sem IVS 2010 oficial (criados depois de 2010): 422000. *Resolução:* Polo e escassez regional (ou IVS) ausentes; o município e as suas células saem dos modelos que usam a covariável e são contados; nada imputado.
5. **Local do resultado.** O §5 do protocolo diz 'doc 57, seção P5'; o doc 57 é a síntese da onda 5 (doc 51, §5). *Resolução:* Resultados em docs/06_execucao/57e_resultados_P5_abertura.md, para entrar na síntese 57.
<!-- P5:desvios:fim -->

## 10. Limites

- **É descritivo.** Uma associação pode vir de uma característica não medida
  que anda junto com a medida (por exemplo, a força política do gestor ou a
  fila de demanda local).
- **Vínculo não é presença.** Vínculos do CNES não são médicos presentes, e a
  produção do SIA é por município de atendimento, não de residência.
- **Separação.** Células cujo nível (curso, tipo de estabelecimento, etc.) tem
  outcome constante saem do logit; a lista está na nota de cada linha.
- **Ciclo 3 só no pedido e na priorização.** Outcomes do CNES do ciclo 3
  seguem o plano prospectivo e não são lidos aqui.
