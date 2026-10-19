# Resultados exploratórios pós-síntese (X1–X6)

> **Protocolo:** [`45_protocolo_exploratorio_pos_sintese.md`](45_protocolo_exploratorio_pos_sintese.md),
> congelado em 19/10/2026 antes de abrir os outcomes.<br>
> **Estatuto:** exploratório e pós-resultado. Nada aqui muda o protocolo 40,
> os resultados E3–E9 nem o Holm das primárias. Toda saída leva
> `estatuto = EXPLORATORIO_POS_SINTESE`.<br>
> **Regra dos números:** cada seção é autocontida e seus números estão em
> blocos gerados pelo script da seção, entre marcadores, a partir de
> `output/rdd_bolsa/`.

## X2

> **Script:** `scripts/rdd_bolsa/18_permanencia_ativos.py`.<br>
> **Saídas:** `output/rdd_bolsa/X2_*` (`natureza_dos_dados = EMPIRICO`;
> fontes, SHA-256, regras de ligação e conferências em `X2_resumo.json`).<br>
> **Testes:** `tests/test_x2_x3_permanencia.py`.<br>
> **Pergunta (doc 45, §3):** quem foi alocado na 1ª chamada dos ciclos 1 e 2
> continua ativo? A saída é maior do lado de bolsa menor?

### Construção

- **Alocados.**
  - Ciclo 1: local confirmado na alocação retificada sub judice e
    homologados da 1ª chamada. A célula final é a da homologação, se houver;
    senão, a da confirmação.
  - Ciclo 2: situação "ALOCADO" na aba Classificados de
    `resultado-final-pmme-2o-ciclo-25-05.xlsx`.
  - As contagens por célula reproduzem as colunas da tarefa B (doc 41a), e o
    script para se não reproduzirem.
- **Ligação.**
  - Os arquivos de resultado não têm CRM (o script confere o cabeçalho). Por
    isso a ligação usa nome normalizado + curso + município, e o município vem
    do quadro pela célula.
  - Chave exata e única dos dois lados: LIGADO. Chave repetida, ou o mesmo
    ativo ligado a dois alocados: AMBÍGUO.
  - Sem chave exata, mas com um ativo não ligado no mesmo curso e município e
    nome próximo: INCERTO. Nome próximo é similaridade ≥ 0,85 ou o mesmo
    primeiro nome com ao menos duas partes do nome em comum. O critério das
    partes entrou depois de um diagnóstico de quase-correspondências e antes de
    qualquer estimativa RDD ser aberta. Ele só reclassifica alocados de "sem
    correspondente" para INCERTO.
  - O resto é NÃO LIGADO, com o motivo.
  - AMBÍGUO e INCERTO ficam fora do outcome.
  - O CRM entra entre os dois retratos de ativos: a relação nominal de
    09/10/2026 (`dt_referencia` 11/09/2026) e `data/pmm_especialistas_nominal.csv`
    (12/08/2026).
- **Outcomes.**
  - X2.1 e X2.2: fração dos alocados determinados ainda ativos no município
    de alocação, por célula e por município. São condicionais a preencher e
    recebem limites de Lee, com seleção = ter alocado determinado.
  - X2.3: célula com alocado ainda ativo. X2.4: alocados ainda ativos por
    célula oferecida. Os dois são incondicionais.
- **Estimação.**
  - Local linear sharp no IVS 2010 oficial (a08), cortes 0,300 e 0,400,
    h = 0,050, kernel triangular. Células com CR1 por município; municípios
    com HC1.
  - Também: cortes empilhados, ciclos empilhados (interceptos por ciclo) e
    tudo empilhado.
  - Lee só por ciclo e corte (a biblioteca não tem Lee empilhado). q de BKY
    sobre todas as linhas X2 com p.

**O que o outcome mede.** Mede presença, no retrato, no município de
alocação. Não observa a data de saída, nem a diferença entre não começar e
sair depois de começar. No ciclo 1 isso pesa: quem só teve o local
confirmado e não foi homologado quase nunca aparece entre os ativos (linha
"confirmacao" da tabela abaixo). Por isso, no ciclo 1, X2 mistura não adesão
com saída. Em nível, a RDD mede o pacote do corte (auditoria 18), não a
participação no PMM-E.

### Ligação e motivos

<!-- X2:ligacao:inicio -->
| Ciclo | Retrato | Status | Motivo | Alocados |
|---|---|---|---|---:|
| 1 | 12/08/2026 | AMBIGUO | chave nome+curso+municipio repetida entre alocados | 3 |
| 1 | 12/08/2026 | INCERTO | grafia proxima (similaridade >= 0.85 ou mesmo 1o nome e 2 partes em comum) no mesmo curso e municipio | 15 |
| 1 | 12/08/2026 | LIGADO | nome+curso+municipio exato e unico | 249 |
| 1 | 12/08/2026 | NAO_LIGADO | nome ativo em outro curso | 15 |
| 1 | 12/08/2026 | NAO_LIGADO | nome e curso ativos em outro municipio | 27 |
| 1 | 12/08/2026 | NAO_LIGADO | sem correspondente na lista de ativos | 185 |
| 1 | 11/09/2026 | AMBIGUO | chave nome+curso+municipio repetida entre alocados | 3 |
| 1 | 11/09/2026 | INCERTO | grafia proxima (similaridade >= 0.85 ou mesmo 1o nome e 2 partes em comum) no mesmo curso e municipio | 15 |
| 1 | 11/09/2026 | LIGADO | nome+curso+municipio exato e unico | 249 |
| 1 | 11/09/2026 | NAO_LIGADO | nome ativo em outro curso | 19 |
| 1 | 11/09/2026 | NAO_LIGADO | nome e curso ativos em outro municipio | 36 |
| 1 | 11/09/2026 | NAO_LIGADO | sem correspondente na lista de ativos | 172 |
| 2 | 12/08/2026 | AMBIGUO | chave nome+curso+municipio repetida entre alocados | 3 |
| 2 | 12/08/2026 | INCERTO | grafia proxima (similaridade >= 0.85 ou mesmo 1o nome e 2 partes em comum) no mesmo curso e municipio | 42 |
| 2 | 12/08/2026 | LIGADO | nome+curso+municipio exato e unico | 680 |
| 2 | 12/08/2026 | NAO_LIGADO | nome e curso ativos em outro municipio | 22 |
| 2 | 12/08/2026 | NAO_LIGADO | sem correspondente na lista de ativos | 310 |
| 2 | 11/09/2026 | AMBIGUO | chave nome+curso+municipio repetida entre alocados | 3 |
| 2 | 11/09/2026 | INCERTO | grafia proxima (similaridade >= 0.85 ou mesmo 1o nome e 2 partes em comum) no mesmo curso e municipio | 42 |
| 2 | 11/09/2026 | LIGADO | nome+curso+municipio exato e unico | 667 |
| 2 | 11/09/2026 | NAO_LIGADO | nome e curso ativos em outro municipio | 29 |
| 2 | 11/09/2026 | NAO_LIGADO | sem correspondente na lista de ativos | 316 |
<!-- X2:ligacao:fim -->

CRM entre os dois retratos (a lista não traz a UF do CRM, então a presença
do CRM é indício, não prova):

<!-- X2:crm:inicio -->
| Medida | Pessoas |
|---|---:|
| ligados nos dois retratos | 911 |
| ligados nos dois com mesmo crm | 911 |
| ligados em ago e nao ligados em set | 18 |
| desses crm presente no retrato de set | 2 |
| desses crm ausente do retrato de set | 16 |
<!-- X2:crm:fim -->

### Permanência por ciclo e faixa (descritivo)

A faixa vem da regra sharp no IVS a08. "Incertos como ativos" e "incertos como
saídos" dão os dois extremos para os INCERTOS. "Presença no programa" também
conta como presente quem tem nome e curso ativos em outro município ou nome
ativo em outro curso.

<!-- X2:descritivo:inicio -->
| Ciclo | Subgrupo | Faixa | Alocados | Ligados | Não ligados | Ambíguos | Incertos | Ligação | Permanência (11/09) | Incertos como ativos | Incertos como saídos | Permanência (12/08) | Presença no programa |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | confirmacao | FAIXA 1 | 33 | 1 | 31 | 1 | 0 | 3,0% | 3,1% | 3,1% | 3,1% | 3,1% | 15,6% |
| 1 | confirmacao | FAIXA 2 | 66 | 0 | 66 | 0 | 0 | 0,0% | 0,0% | 0,0% | 0,0% | 0,0% | 24,2% |
| 1 | confirmacao | FAIXA 3 | 79 | 0 | 77 | 2 | 0 | 0,0% | 0,0% | 0,0% | 0,0% | 0,0% | 18,2% |
| 1 | confirmacao | TOTAL | 178 | 1 | 174 | 3 | 0 | 0,6% | 0,6% | 0,6% | 0,6% | 0,6% | 20,0% |
| 1 | homologacao | FAIXA 1 | 88 | 78 | 5 | 0 | 5 | 88,6% | 94,0% | 94,3% | 88,6% | 94,0% | 96,4% |
| 1 | homologacao | FAIXA 2 | 138 | 109 | 22 | 0 | 7 | 79,0% | 83,2% | 84,1% | 79,0% | 84,0% | 90,1% |
| 1 | homologacao | FAIXA 3 | 90 | 61 | 26 | 0 | 3 | 67,8% | 70,1% | 71,1% | 67,8% | 69,0% | 81,6% |
| 1 | homologacao | TOTAL | 316 | 248 | 53 | 0 | 15 | 78,5% | 82,4% | 83,2% | 78,5% | 82,4% | 89,4% |
| 1 | todos | FAIXA 1 | 121 | 79 | 36 | 1 | 5 | 65,3% | 68,7% | 70,0% | 65,8% | 68,7% | 73,9% |
| 1 | todos | FAIXA 2 | 204 | 109 | 88 | 0 | 7 | 53,4% | 55,3% | 56,9% | 53,4% | 55,8% | 68,0% |
| 1 | todos | FAIXA 3 | 169 | 61 | 103 | 2 | 3 | 36,1% | 37,2% | 38,3% | 36,5% | 36,6% | 51,8% |
| 1 | todos | TOTAL | 494 | 249 | 227 | 3 | 15 | 50,4% | 52,3% | 53,8% | 50,7% | 52,3% | 63,9% |
| 2 | todos | FAIXA 1 | 178 | 128 | 43 | 1 | 6 | 71,9% | 74,9% | 75,7% | 72,3% | 75,4% | 79,5% |
| 2 | todos | FAIXA 2 | 425 | 297 | 111 | 0 | 17 | 69,9% | 72,8% | 73,9% | 69,9% | 75,0% | 75,2% |
| 2 | todos | FAIXA 3 | 454 | 242 | 191 | 2 | 19 | 53,3% | 55,9% | 57,7% | 53,5% | 56,6% | 58,4% |
| 2 | todos | TOTAL | 1057 | 667 | 345 | 3 | 42 | 63,1% | 65,9% | 67,3% | 63,3% | 67,2% | 68,8% |
<!-- X2:descritivo:fim -->

### RDD e limites de Lee

Nas linhas `limites_lee`, τ é o local linear ingênuo nos selecionados. O
efeito só é limitado pelo par Lee [inf; sup], e o IC de Lee é conservador.

<!-- X2:estimativas:inicio -->
| Outcome | Ciclo | Corte | Especificação | τ | IC 95% | p | q BKY | Lee [inf; sup] | IC 95% Lee | n abaixo/acima |
|---|---|---|---|---:|---|---:|---:|---|---|---|
| X2.1 | 1 | 0.300 | principal | 0,130 | [−0,302; 0,562] | 0,555 | 1,000 | — | — | 31/35 |
| X2.1 | 1 | 0.300 | limites_lee | 0,130 | — | — | — | [0,035; 0,339] | [−0,465; 0,777] | 31/35 |
| X2.1 | 1 | 0.400 | principal | −0,055 | [−0,356; 0,246] | 0,719 | 1,000 | — | — | 41/25 |
| X2.1 | 1 | 0.400 | limites_lee | −0,055 | — | — | — | [−0,063; −0,032] | [−0,364; 0,264] | 41/25 |
| X2.1 | 1 | empilhado | cortes_empilhados | 0,037 | [−0,232; 0,306] | 0,789 | 1,000 | — | — | 72/60 |
| X2.1 | 2 | 0.300 | principal | −0,021 | [−0,256; 0,213] | 0,858 | 1,000 | — | — | 53/45 |
| X2.1 | 2 | 0.300 | limites_lee | −0,021 | — | — | — | [−0,399; 0,312] | [−0,609; 0,603] | 53/45 |
| X2.1 | 2 | 0.400 | principal | −0,093 | [−0,305; 0,118] | 0,388 | 1,000 | — | — | 42/45 |
| X2.1 | 2 | 0.400 | limites_lee | −0,093 | — | — | — | [−0,140; 0,034] | [−0,392; 0,192] | 42/45 |
| X2.1 | 2 | empilhado | cortes_empilhados | −0,057 | [−0,218; 0,103] | 0,485 | 1,000 | — | — | 95/90 |
| X2.1 | 1+2 | 0.300 | ciclos_empilhados | 0,031 | [−0,209; 0,270] | 0,802 | 1,000 | — | — | 64/58 |
| X2.1 | 1+2 | 0.400 | ciclos_empilhados | −0,080 | [−0,241; 0,081] | 0,329 | 1,000 | — | — | 59/57 |
| X2.1 | 1+2 | empilhado | ciclos_e_cortes_empilhados | −0,025 | [−0,173; 0,123] | 0,743 | 1,000 | — | — | 123/115 |
| X2.2 | 1 | 0.300 | principal | 0,035 | [−0,456; 0,525] | 0,890 | 1,000 | — | — | 31/35 |
| X2.2 | 1 | 0.300 | limites_lee | 0,035 | — | — | — | [0,039; 0,041] | [−0,452; 0,531] | 31/35 |
| X2.2 | 1 | 0.400 | principal | 0,062 | [−0,322; 0,445] | 0,753 | 1,000 | — | — | 41/25 |
| X2.2 | 1 | 0.400 | limites_lee | 0,062 | — | — | — | [−0,292; 0,295] | [−0,614; 0,664] | 41/25 |
| X2.2 | 1 | empilhado | cortes_empilhados | 0,050 | [−0,253; 0,353] | 0,746 | 1,000 | — | — | 72/60 |
| X2.2 | 2 | 0.300 | principal | −0,078 | [−0,425; 0,269] | 0,661 | 1,000 | — | — | 53/45 |
| X2.2 | 2 | 0.300 | limites_lee | −0,078 | — | — | — | [−0,288; 0,028] | [−0,601; 0,364] | 53/45 |
| X2.2 | 2 | 0.400 | principal | −0,109 | [−0,335; 0,116] | 0,341 | 1,000 | — | — | 42/45 |
| X2.2 | 2 | 0.400 | limites_lee | −0,109 | — | — | — | [−0,140; 0,020] | [−0,388; 0,192] | 42/45 |
| X2.2 | 2 | empilhado | cortes_empilhados | −0,094 | [−0,298; 0,109] | 0,364 | 1,000 | — | — | 95/90 |
| X2.2 | 1+2 | 0.300 | ciclos_empilhados | −0,039 | [−0,344; 0,266] | 0,802 | 1,000 | — | — | 64/58 |
| X2.2 | 1+2 | 0.400 | ciclos_empilhados | −0,042 | [−0,229; 0,144] | 0,656 | 1,000 | — | — | 59/57 |
| X2.2 | 1+2 | empilhado | ciclos_e_cortes_empilhados | −0,041 | [−0,214; 0,132] | 0,643 | 1,000 | — | — | 123/115 |
| X2.3 | 1 | 0.300 | principal | 0,003 | [−0,200; 0,205] | 0,978 | 1,000 | — | — | 61/53 |
| X2.3 | 1 | 0.400 | principal | −0,037 | [−0,245; 0,171] | 0,725 | 1,000 | — | — | 53/41 |
| X2.3 | 1 | empilhado | cortes_empilhados | −0,016 | [−0,162; 0,130] | 0,832 | 1,000 | — | — | 114/94 |
| X2.3 | 2 | 0.300 | principal | −0,175 | [−0,361; 0,011] | 0,066 | 1,000 | — | — | 82/61 |
| X2.3 | 2 | 0.400 | principal | 0,007 | [−0,243; 0,258] | 0,954 | 1,000 | — | — | 52/53 |
| X2.3 | 2 | empilhado | cortes_empilhados | −0,099 | [−0,248; 0,051] | 0,197 | 1,000 | — | — | 134/114 |
| X2.3 | 1+2 | 0.300 | ciclos_empilhados | −0,100 | [−0,246; 0,046] | 0,180 | 1,000 | — | — | 100/80 |
| X2.3 | 1+2 | 0.400 | ciclos_empilhados | −0,014 | [−0,186; 0,159] | 0,878 | 1,000 | — | — | 69/71 |
| X2.3 | 1+2 | empilhado | ciclos_e_cortes_empilhados | −0,062 | [−0,173; 0,049] | 0,271 | 1,000 | — | — | 169/151 |
| X2.4 | 1 | 0.300 | principal | −0,007 | [−0,286; 0,271] | 0,959 | 1,000 | — | — | 59/53 |
| X2.4 | 1 | 0.400 | principal | −0,011 | [−0,325; 0,303] | 0,945 | 1,000 | — | — | 47/38 |
| X2.4 | 1 | empilhado | cortes_empilhados | −0,009 | [−0,221; 0,202] | 0,931 | 1,000 | — | — | 106/91 |
| X2.4 | 2 | 0.300 | principal | −0,088 | [−0,382; 0,207] | 0,559 | 1,000 | — | — | 74/56 |
| X2.4 | 2 | 0.400 | principal | −0,339 | [−1,160; 0,482] | 0,419 | 1,000 | — | — | 48/50 |
| X2.4 | 2 | empilhado | cortes_empilhados | −0,200 | [−0,606; 0,206] | 0,334 | 1,000 | — | — | 122/106 |
| X2.4 | 1+2 | 0.300 | ciclos_empilhados | −0,055 | [−0,278; 0,168] | 0,628 | 1,000 | — | — | 97/79 |
| X2.4 | 1+2 | 0.400 | ciclos_empilhados | −0,176 | [−0,598; 0,246] | 0,413 | 1,000 | — | — | 66/68 |
| X2.4 | 1+2 | empilhado | ciclos_e_cortes_empilhados | −0,114 | [−0,351; 0,123] | 0,344 | 1,000 | — | — | 163/147 |
<!-- X2:estimativas:fim -->

### Leitura

<!-- X2:leitura:inicio -->
- Ciclo 1: 494 alocados da 1ª chamada; 50,4% ligados a um ativo no município de alocação em 11/09/2026; permanência entre os determinados 52,3% (12/08/2026: 52,3%).
- Ciclo 2: 1057 alocados da 1ª chamada; 63,1% ligados a um ativo no município de alocação em 11/09/2026; permanência entre os determinados 65,9% (12/08/2026: 67,2%).
- Ciclo 1 por evento final: permanência 82,4% entre os homologados e 0,6% entre os que só tiveram o local confirmado.
- CRM entre os dois retratos: 911 de 911 pessoas ligadas nos dois têm o mesmo CRM.
- RDD: 36 estimativas com p; 0 com p < 0,05; menor q de BKY = 1,000.
- Limites de Lee: 8 de 8 ICs de Lee contêm zero.
<!-- X2:leitura:fim -->

- Os números estão no bloco acima.
- Como em todo o protocolo 45, nada aqui é confirmatório: os q de BKY valem
  dentro do X2.
- A leitura relevante para H2 e para a proposta C é se os limites de Lee e os
  ICs incondicionais descartam saídas grandes do lado de bolsa menor. Não
  basta olhar se o ponto é zero.

## X3

> **Script:** `scripts/rdd_bolsa/18_permanencia_ativos.py`.<br>
> **Saídas:** `output/rdd_bolsa/X3_*` (`natureza_dos_dados = EMPIRICO`;
> conferência de completude e populações em `X3_resumo.json`).<br>
> **Pergunta (doc 45, §3):** como evolui o número de ativos por município e
> curso, mês a mês, de dez/25 a ago/26?

### Fonte e completude

- **Leitura.**
  - De `data/pmm_especialistas_serie_historica.csv` só se leem `co_ibge`, o
    código do curso (número inicial do rótulo, que tem mojibake), a
    competência e `qtd_ativos`.
  - A coluna `ivs` do arquivo (rótulos inconsistentes) e a faixa do arquivo
    não são usadas. A running variable é o IVS a08.
  - Linhas repetidas de município × curso × mês são somadas.
- **Conferência de completude** (antes de qualquer outcome), contra o retrato
  nominal de 12/08/2026:
  - (i) o último mês tem de reproduzir o retrato por município × curso;
  - (ii) cada mês tem de conter, por município × curso, ao menos os ativos do
    retrato que começaram antes do 1º dia do mês.
- **Regra fixada.** Se todos os meses passam, ausência de linha vira zero em
  U. Se algum falha, cada mês usa só os municípios listados naquele mês. A
  queda usa zero no último mês para quem não está listado nele, porque o
  último mês reproduz o retrato.
- **Sensibilidade.**
  - A conferência mostrou meses em que municípios da cota somem da listagem.
    O total do mês se mantém, porque alguns municípios aparecem com mais
    ativos que nos meses vizinhos.
  - Daí uma sensibilidade, declarada antes de abrir qualquer estimativa X3:
    pico só nos meses sem município da cota ausente (X3.3s–X3.5s, rotulada
    `ESPECIFICACAO_ADICIONAL_AO_PROTOCOLO`).

<!-- X3:completude:inicio -->
| Mês | Municípios listados | Células município × curso | Ativos na série | Cota inferior do retrato | Células com violação | Déficit | Municípios da cota ausentes | Municípios acima dos meses vizinhos | Excesso |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2025-12 | 186 | 407 | 577 | 507 | 58 | 70 | 9 | 9 | 14 |
| 2026-01 | 151 | 375 | 583 | 516 | 96 | 123 | 37 | 17 | 78 |
| 2026-02 | 188 | 416 | 569 | 518 | 19 | 19 | 1 | 5 | 5 |
| 2026-03 | 181 | 400 | 551 | 519 | 19 | 19 | 1 | 0 | 0 |
| 2026-04 | 318 | 781 | 1350 | 830 | 21 | 21 | 0 | 52 | 116 |
| 2026-05 | 245 | 639 | 1363 | 1279 | 235 | 304 | 75 | 6 | 8 |
| 2026-06 | 257 | 692 | 1501 | 1295 | 232 | 302 | 72 | 14 | 45 |
| 2026-07 | 513 | 1346 | 1511 | 1478 | 4 | 4 | 0 | 9 | 10 |
| 2026-08 | 325 | 838 | 1480 | 1480 | 0 | 0 | 0 | 4 | 4 |
<!-- X3:completude:fim -->

### Descritivo por mês e faixa

Os municípios listados mudam de mês a mês, e a ausência não é zero. As médias
mensais não são comparáveis entre meses com listagens diferentes.

<!-- X3:descritivo_mensal:inicio -->
| Mês | FAIXA 3: municípios / ativos / média por 10 mil | FAIXA 2: municípios / ativos / média por 10 mil | FAIXA 1: municípios / ativos / média por 10 mil | TOTAL: municípios / ativos / média por 10 mil |
|---|---|---|---|---|
| 2025-12 | 57 / 149 / 0,292 | 75 / 306 / 0,486 | 54 / 122 / 0,677 | 186 / 577 / 0,482 |
| 2026-01 | 49 / 161 / 0,343 | 64 / 335 / 0,527 | 38 / 87 / 0,812 | 151 / 583 / 0,539 |
| 2026-02 | 59 / 149 / 0,299 | 76 / 282 / 0,505 | 53 / 138 / 0,739 | 188 / 569 / 0,506 |
| 2026-03 | 54 / 138 / 0,256 | 75 / 276 / 0,505 | 52 / 137 / 0,752 | 181 / 551 / 0,502 |
| 2026-04 | 112 / 443 / 0,302 | 101 / 630 / 0,933 | 105 / 277 / 0,769 | 318 / 1350 / 0,657 |
| 2026-05 | 95 / 476 / 0,301 | 77 / 707 / 1,019 | 73 / 180 / 0,841 | 245 / 1363 / 0,688 |
| 2026-06 | 97 / 524 / 0,328 | 78 / 776 / 1,057 | 82 / 201 / 0,825 | 257 / 1501 / 0,708 |
| 2026-07 | 193 / 481 / 0,196 | 153 / 712 / 0,660 | 167 / 318 / 0,556 | 513 / 1511 / 0,452 |
| 2026-08 | 108 / 467 / 0,337 | 105 / 697 / 0,903 | 112 / 316 / 0,826 | 325 / 1480 / 0,688 |
<!-- X3:descritivo_mensal:fim -->

<!-- X3:descritivo_queda:inicio -->
| Faixa | Municípios com ativo em algum mês | Com ativo no último mês | Queda média (ativos) | Queda média por 10 mil | Fração com queda | Queda relativa média | Meses com ativo (média) | Queda média (sensibilidade) | Queda relativa média (sensibilidade) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAIXA 1 | 115 | 112 | 0,078 | 0,016 | 7,0% | 4,1% | 5,93 | 0,053 | 2,1% |
| FAIXA 2 | 111 | 105 | 2,117 | 0,097 | 29,7% | 12,8% | 6,82 | 0,302 | 5,0% |
| FAIXA 3 | 131 | 108 | 1,427 | 0,088 | 40,5% | 25,6% | 5,68 | 0,435 | 17,0% |
| TOTAL | 357 | 325 | 1,207 | 0,068 | 26,3% | 14,7% | 6,11 | 0,268 | 8,4% |
<!-- X3:descritivo_queda:fim -->

### RDD mês a mês e da queda

- Outcomes:
  - X3.1 e X3.2: ativos no mês (contagem e por 10 mil habitantes, Censo 2022);
  - X3.3 a X3.5: queda do pico ao último mês (contagem, por 10 mil habitantes
    e relativa);
  - X3.6: meses listados com ativo.
- Estimação: local linear sharp, h = 0,050, HC1, cortes 0,300 e 0,400 e
  empilhado.
- A nota de cada linha mensal em `X3_estimativas.csv` registra se o mês falha
  a conferência de completude.

<!-- X3:estimativas:inicio -->
| Outcome | Mês | Corte | Especificação | τ | IC 95% | p | q BKY | n abaixo/acima |
|---|---|---|---|---:|---|---:|---:|---|
| X3.1 | 2025-12 | 0.300 | principal | 2,800 | [−2,413; 8,013] | 0,293 | 1,000 | 31/36 |
| X3.1 | 2025-12 | 0.400 | principal | 0,419 | [−2,488; 3,325] | 0,778 | 1,000 | 37/29 |
| X3.1 | 2025-12 | empilhado | cortes_empilhados | 1,404 | [−1,347; 4,155] | 0,317 | 1,000 | 68/65 |
| X3.1 | 2026-01 | 0.300 | principal | 1,485 | [−4,454; 7,424] | 0,624 | 1,000 | 27/35 |
| X3.1 | 2026-01 | 0.400 | principal | 2,040 | [−2,044; 6,124] | 0,328 | 1,000 | 28/20 |
| X3.1 | 2026-01 | empilhado | cortes_empilhados | 1,764 | [−1,832; 5,361] | 0,336 | 1,000 | 55/55 |
| X3.1 | 2026-02 | 0.300 | principal | 2,338 | [−2,417; 7,094] | 0,335 | 1,000 | 32/39 |
| X3.1 | 2026-02 | 0.400 | principal | −0,089 | [−3,043; 2,865] | 0,953 | 1,000 | 36/29 |
| X3.1 | 2026-02 | empilhado | cortes_empilhados | 1,022 | [−1,675; 3,719] | 0,458 | 1,000 | 68/68 |
| X3.1 | 2026-03 | 0.300 | principal | 2,700 | [−2,297; 7,696] | 0,290 | 1,000 | 32/38 |
| X3.1 | 2026-03 | 0.400 | principal | −0,142 | [−3,127; 2,842] | 0,926 | 1,000 | 36/28 |
| X3.1 | 2026-03 | empilhado | cortes_empilhados | 1,100 | [−1,675; 3,875] | 0,437 | 1,000 | 68/66 |
| X3.1 | 2026-04 | 0.300 | principal | −1,460 | [−7,735; 4,814] | 0,648 | 1,000 | 54/51 |
| X3.1 | 2026-04 | 0.400 | principal | −4,434 | [−10,357; 1,489] | 0,142 | 1,000 | 49/57 |
| X3.1 | 2026-04 | empilhado | cortes_empilhados | −3,213 | [−7,563; 1,138] | 0,148 | 1,000 | 103/108 |
| X3.1 | 2026-05 | 0.300 | principal | −7,404 | [−20,530; 5,721] | 0,269 | 1,000 | 43/41 |
| X3.1 | 2026-05 | 0.400 | principal | −4,181 | [−12,465; 4,103] | 0,323 | 1,000 | 34/40 |
| X3.1 | 2026-05 | empilhado | cortes_empilhados | −5,574 | [−12,912; 1,763] | 0,136 | 1,000 | 77/81 |
| X3.1 | 2026-06 | 0.300 | principal | −6,954 | [−20,822; 6,915] | 0,326 | 1,000 | 45/42 |
| X3.1 | 2026-06 | 0.400 | principal | −4,637 | [−14,710; 5,436] | 0,367 | 1,000 | 34/43 |
| X3.1 | 2026-06 | empilhado | cortes_empilhados | −5,649 | [−13,917; 2,620] | 0,181 | 1,000 | 79/85 |
| X3.1 | 2026-07 | 0.300 | principal | −4,238 | [−9,759; 1,282] | 0,132 | 1,000 | 75/75 |
| X3.1 | 2026-07 | 0.400 | principal | −3,693 | [−10,230; 2,844] | 0,268 | 1,000 | 76/75 |
| X3.1 | 2026-07 | empilhado | cortes_empilhados | −3,942 | [−8,290; 0,406] | 0,076 | 1,000 | 151/150 |
| X3.1 | 2026-08 | 0.300 | principal | −3,243 | [−10,100; 3,613] | 0,354 | 1,000 | 51/56 |
| X3.1 | 2026-08 | 0.400 | principal | −4,773 | [−12,291; 2,745] | 0,213 | 1,000 | 48/60 |
| X3.1 | 2026-08 | empilhado | cortes_empilhados | −4,137 | [−9,366; 1,092] | 0,121 | 1,000 | 99/116 |
| X3.2 | 2025-12 | 0.300 | principal | 0,239 | [−0,247; 0,726] | 0,335 | 1,000 | 31/36 |
| X3.2 | 2025-12 | 0.400 | principal | 0,470 | [−1,604; 2,544] | 0,657 | 1,000 | 37/29 |
| X3.2 | 2025-12 | empilhado | cortes_empilhados | 0,375 | [−0,852; 1,601] | 0,549 | 1,000 | 68/65 |
| X3.2 | 2026-01 | 0.300 | principal | 0,313 | [−0,191; 0,816] | 0,223 | 1,000 | 27/35 |
| X3.2 | 2026-01 | 0.400 | principal | 1,331 | [−1,998; 4,660] | 0,433 | 1,000 | 28/20 |
| X3.2 | 2026-01 | empilhado | cortes_empilhados | 0,825 | [−0,859; 2,509] | 0,337 | 1,000 | 55/55 |
| X3.2 | 2026-02 | 0.300 | principal | 0,199 | [−0,234; 0,631] | 0,368 | 1,000 | 32/39 |
| X3.2 | 2026-02 | 0.400 | principal | 0,405 | [−1,688; 2,498] | 0,704 | 1,000 | 36/29 |
| X3.2 | 2026-02 | empilhado | cortes_empilhados | 0,311 | [−0,835; 1,456] | 0,595 | 1,000 | 68/68 |
| X3.2 | 2026-03 | 0.300 | principal | 0,217 | [−0,261; 0,694] | 0,374 | 1,000 | 32/38 |
| X3.2 | 2026-03 | 0.400 | principal | 0,388 | [−1,716; 2,493] | 0,718 | 1,000 | 36/28 |
| X3.2 | 2026-03 | empilhado | cortes_empilhados | 0,313 | [−0,882; 1,509] | 0,608 | 1,000 | 68/66 |
| X3.2 | 2026-04 | 0.300 | principal | −0,241 | [−0,674; 0,193] | 0,277 | 1,000 | 54/51 |
| X3.2 | 2026-04 | 0.400 | principal | −1,629 | [−5,466; 2,209] | 0,405 | 1,000 | 49/57 |
| X3.2 | 2026-04 | empilhado | cortes_empilhados | −1,059 | [−3,340; 1,223] | 0,363 | 1,000 | 103/108 |
| X3.2 | 2026-05 | 0.300 | principal | −0,152 | [−0,586; 0,281] | 0,491 | 1,000 | 43/41 |
| X3.2 | 2026-05 | 0.400 | principal | −2,088 | [−7,075; 2,899] | 0,412 | 1,000 | 34/40 |
| X3.2 | 2026-05 | empilhado | cortes_empilhados | −1,251 | [−4,110; 1,608] | 0,391 | 1,000 | 77/81 |
| X3.2 | 2026-06 | 0.300 | principal | −0,117 | [−0,586; 0,353] | 0,626 | 1,000 | 45/42 |
| X3.2 | 2026-06 | 0.400 | principal | −2,056 | [−7,035; 2,923] | 0,418 | 1,000 | 34/43 |
| X3.2 | 2026-06 | empilhado | cortes_empilhados | −1,209 | [−4,043; 1,625] | 0,403 | 1,000 | 79/85 |
| X3.2 | 2026-07 | 0.300 | principal | −0,381 | [−0,711; −0,052] | 0,023 | 1,000 | 75/75 |
| X3.2 | 2026-07 | 0.400 | principal | −1,023 | [−4,197; 2,150] | 0,527 | 1,000 | 76/75 |
| X3.2 | 2026-07 | empilhado | cortes_empilhados | −0,730 | [−2,462; 1,002] | 0,409 | 1,000 | 151/150 |
| X3.2 | 2026-08 | 0.300 | principal | −0,315 | [−0,729; 0,099] | 0,136 | 1,000 | 51/56 |
| X3.2 | 2026-08 | 0.400 | principal | −1,538 | [−5,400; 2,324] | 0,435 | 1,000 | 48/60 |
| X3.2 | 2026-08 | empilhado | cortes_empilhados | −1,029 | [−3,301; 1,243] | 0,375 | 1,000 | 99/116 |
| X3.3 | dez/25-ago/26 | 0.300 | principal | −4,424 | [−9,606; 0,757] | 0,094 | 1,000 | 60/58 |
| X3.3 | dez/25-ago/26 | 0.400 | principal | −0,086 | [−0,848; 0,675] | 0,824 | 1,000 | 51/61 |
| X3.3 | dez/25-ago/26 | empilhado | cortes_empilhados | −1,927 | [−4,199; 0,345] | 0,096 | 1,000 | 111/119 |
| X3.3s | 2026-04,2026-07,2026-08 | 0.300 | sensibilidade_meses_sem_ausencia | −0,432 | [−1,171; 0,306] | 0,251 | 1,000 | 58/56 |
| X3.3s | 2026-04,2026-07,2026-08 | 0.400 | sensibilidade_meses_sem_ausencia | −0,242 | [−0,545; 0,062] | 0,118 | 1,000 | 49/60 |
| X3.3s | 2026-04,2026-07,2026-08 | empilhado | sensibilidade_meses_sem_ausencia_cortes_empilhados | −0,324 | [−0,686; 0,037] | 0,079 | 1,000 | 107/116 |
| X3.4 | dez/25-ago/26 | 0.300 | principal | −0,099 | [−0,186; −0,011] | 0,027 | 1,000 | 60/58 |
| X3.4 | dez/25-ago/26 | 0.400 | principal | −0,038 | [−0,140; 0,064] | 0,461 | 1,000 | 51/61 |
| X3.4 | dez/25-ago/26 | empilhado | cortes_empilhados | −0,064 | [−0,133; 0,005] | 0,069 | 1,000 | 111/119 |
| X3.4s | 2026-04,2026-07,2026-08 | 0.300 | sensibilidade_meses_sem_ausencia | −0,024 | [−0,085; 0,037] | 0,434 | 1,000 | 58/56 |
| X3.4s | 2026-04,2026-07,2026-08 | 0.400 | sensibilidade_meses_sem_ausencia | 0,006 | [−0,086; 0,098] | 0,894 | 1,000 | 49/60 |
| X3.4s | 2026-04,2026-07,2026-08 | empilhado | sensibilidade_meses_sem_ausencia_cortes_empilhados | −0,007 | [−0,065; 0,051] | 0,815 | 1,000 | 107/116 |
| X3.5 | dez/25-ago/26 | 0.300 | principal | −0,250 | [−0,488; −0,013] | 0,039 | 1,000 | 60/58 |
| X3.5 | dez/25-ago/26 | 0.400 | principal | −0,139 | [−0,311; 0,033] | 0,114 | 1,000 | 51/61 |
| X3.5 | dez/25-ago/26 | empilhado | cortes_empilhados | −0,186 | [−0,327; −0,045] | 0,010 | 1,000 | 111/119 |
| X3.5s | 2026-04,2026-07,2026-08 | 0.300 | sensibilidade_meses_sem_ausencia | −0,069 | [−0,275; 0,136] | 0,509 | 1,000 | 58/56 |
| X3.5s | 2026-04,2026-07,2026-08 | 0.400 | sensibilidade_meses_sem_ausencia | −0,008 | [−0,063; 0,046] | 0,769 | 1,000 | 49/60 |
| X3.5s | 2026-04,2026-07,2026-08 | empilhado | sensibilidade_meses_sem_ausencia_cortes_empilhados | −0,035 | [−0,129; 0,059] | 0,471 | 1,000 | 107/116 |
| X3.6 | dez/25-ago/26 | 0.300 | principal | −0,352 | [−2,353; 1,649] | 0,730 | 1,000 | 60/58 |
| X3.6 | dez/25-ago/26 | 0.400 | principal | −1,148 | [−2,968; 0,671] | 0,216 | 1,000 | 51/61 |
| X3.6 | dez/25-ago/26 | empilhado | cortes_empilhados | −0,810 | [−2,155; 0,534] | 0,238 | 1,000 | 111/119 |
<!-- X3:estimativas:fim -->

### Leitura

<!-- X3:leitura:inicio -->
- Último mês (2026-08) reproduz o retrato nominal por município × curso: sim.
- Listagem completa em todos os meses: não; meses que falham a cota inferior: 2025-12, 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07; meses sem município da cota ausente: 2026-04, 2026-07, 2026-08.
- População de estimação mensal: municipios listados no mes (listagem incompleta: ausencia nao e zero).
- Especificações do protocolo: 66 estimativas com p; com p < 0,05: X3.2 2026-07 0.300 (τ = −0,381, p = 0,023, q = 1,000); X3.4 dez/25-ago/26 0.300 (τ = −0,099, p = 0,027, q = 1,000); X3.5 dez/25-ago/26 0.300 (τ = −0,250, p = 0,039, q = 1,000); X3.5 dez/25-ago/26 empilhado (τ = −0,186, p = 0,010, q = 1,000).
- Sensibilidade de meses sem ausência: 9 estimativas com p; com p < 0,05: nenhuma.
- Menor q de BKY no X3: 1,000.
<!-- X3:leitura:fim -->

- A série é agregada e sem identificador individual. Uma queda de ativos num
  município não separa saída, transferência, correção cadastral e mudança na
  regra de listagem.
- Nos meses em que a listagem falha a conferência, o pico pode vir da
  redistribuição de ativos entre municípios, não de presença real. Por isso a
  queda das especificações do protocolo e a da sensibilidade são lidas juntas.
