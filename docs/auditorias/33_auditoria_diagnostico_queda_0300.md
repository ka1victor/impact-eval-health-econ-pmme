# Auditoria independente do protocolo 61: diagnóstico da queda no corte 0,300

> **Data:** 26/10/2026.<br>
> **Objeto:** commits `daca437` (protocolo) e `8ba0c35` (execução, WIP marcado "não auditado"):
> `scripts/rdd_bolsa/38_diagnostico_queda_0300.py`, `output/rdd_bolsa/DQ_estimativas.csv`, `DQ_resumo.json`,
> `DQ_figuras/` (três PNG), o [doc 57l](../06_execucao/57l_diagnostico_queda_0300.md) e
> `tests/test_diagnostico_queda_0300.py`, contra o
> [protocolo 61](../06_execucao/61_protocolo_diagnostico_queda_0300.md).<br>
> **Veredito:** **APROVADO COM CORREÇÕES.**
> - Nenhum número mudou. `DQ_estimativas.csv` e as três figuras têm o mesmo SHA-256 antes e depois da
>   correção.
> - 328 conferências numéricas contra o gravado, com código próprio: todas batem (diferença absoluta
>   máxima 1,4e-10). A única diferença é ruído de Monte Carlo do meu gerador de permutações (seção 3.2).
> - A leitura pré-registrada está aplicada corretamente.
> - As correções são de texto e de rótulo: uma média (a frase "Para dizer na banca") e seis baixas
>   (seção 5). Foram feitas no script 38, que regravou o doc 57l e o `DQ_resumo.json`.<br>
> **Proveniência dos números:** lidos de `output/rdd_bolsa/DQ_estimativas.csv` e `DQ_resumo.json` e
> recalculados das entradas em `output/` (seção 2). A conferência que fica no repositório é
> `TestCorrecoesAuditoria33` em `tests/test_diagnostico_queda_0300.py`, junto com os recálculos que o
> teste já fazia.

## 1. Ordem dos commits

- `daca437` toca dois arquivos: o protocolo 61 e o registro de mudanças. Não há conta nele.
- `8ba0c35` é o filho direto. Traz o script, as saídas, o doc 57l, os testes, as linhas do `run_all.py`,
  do `test_pipeline_rdd_bolsa.py`, do `tests/README.md` e do manifesto A6.
- O protocolo não mudou entre os dois commits. O SHA-256 do texto atual (`0d3185de…`) é o gravado em
  `DQ_resumo.json["protocolo"]`.
- O protocolo declara o estatuto `DIAGNOSTICO_61_POS_RESULTADO`: as quedas já eram conhecidas (docs 49 e
  49b) quando a lista foi fixada. O doc 57l repete isso no topo e nos limites.
- O auditado chegou num só commit WIP. Por isso não dá para saber, pelo Git, o que foi decidido antes de
  rodar e o que foi decidido depois (achado B4).

## 2. Como a auditoria foi feita

O recálculo está num script próprio, fora do repositório. Ele não importa o script 38 nem os scripts 23,
23b, 24 e 32.

**Estimador próprio**
- MQP com kernel triangular e h = 0,050.
- Intercepto, inclinação e inclinação × lado por ciclo; um salto comum.
- Efeitos fixos como dummies; covariáveis com um coeficiente por ciclo.
- EP CR1 por município (HC1 no ciclo 2 sozinho e em U).
- Pesos ω e limites do lado de baixo tirados da própria regressão.

**Dados montados do zero**
- Running variable: IVS do `a08` × 1000.
- Municípios: `outcomes_V_municipio.parquet`. Células: `outcomes_V_celula.parquet`.
- Gestão: `quadro_vagas_consolidado.parquet`.
- Índices de curso, tipo e gestão; agregados municipais; células só de CR.
- Concorrência: laço próprio por ciclo × curso, com mercado CIR e UF e bolsa pela regra 0,300/0,400.
- Vínculos do curso na CIR; REGIC; vínculos SUS pré por 10 mil hab.

Do script 29 usei só os leitores de arquivo bruto: CIR, REGIC, ponte, CNES pré, população e cardápio. Da
`rdd_lib` usei só a matriz de permutação, para conferir o p de Fisher exato. O p também foi refeito com
um gerador próprio.

**Fora do recálculo**
- A distância à origem (D-e), que exige o join do G1 com os centróides.
- A linha D-e do "quanto da queda", que depende dessa distância.
- O balanço de generalistas (D-g).

Nenhuma dessas linhas muda a leitura (seção 6).

## 3. Recálculo contra o gravado

### 3.1 Linhas centrais (0,300; em 0,400 também batem)

Q1 em vagas por município; Q2, Q3 e frações em p.p. "Comparado com" segue a regra do script:
- covariável: o original na mesma amostra;
- retirada de células: o Q original.

| Bloco | Linha | Recalculado | Gravado | Dif. máx. |
|---|---|---|---|---|
| Reprodução | Q1 (S-a), Q2 (S-e), Q3 (A3) | −1,447 / −15,99 / −8,39 | −1,447 / −15,99 / −8,39 | 8e-12 (também contra `N_`, `NA_` e `ND_estimativas`, salto e EP) |
| D-a | grade do protocolo | 0,250; 0,350; 0,450 | idem | — |
| D-a | t dos 9 placebos do protocolo | Q1 −0,69 / −0,34 / −0,67 … | idem | 1e-12 |
| D-a | p por posto (protocolo / complementar) | Q1 0,250 / 0,031; Q2 0,250 / 0,031; Q3 0,250 / 0,188 | idem | 0 |
| D-a | fração com \|t\| > 1,96 (complementar) | Q1 0%; Q2 9,7%; Q3 0% | idem | 0 |
| D-a | Fisher ±0,010: diferença e p | Q1 −1,62, 0,017; Q2 −18,0, 0,018; Q3 −11,6, 0,086 | idem | 7e-16; p igual com a matriz da `rdd_lib` |
| D-a | Fisher ±0,020: diferença e p | Q1 −0,82, 0,154; Q2 −6,8, 0,218; Q3 −1,2, 0,781 | idem | idem |
| D-b | salto da parte de células só de CR | +15,37 | +15,37 | 1e-15 |
| D-b | índice de curso | −4,54 | −4,54 | 2e-14 |
| D-b | só CR por ciclo (1 / 2 / 3) | +17,9 / +28,4 / +5,6 | idem | 1e-14 |
| D-b (ii) | Q3 sem efeitos fixos / Q3 / Q3 + tipo e gestão (mesma amostra) | −14,37 / −7,31 / −6,27 | idem | 8e-14 |
| D-b (iii) | Q2 sem células só de CR | −11,04 | −11,04 | 5e-14 |
| D-c | P(candidato de 1ª opção), espec. Q3 / sem efeitos fixos | −10,75 / −14,19 | idem | 5e-14 |
| D-c | decomposição: candidatos / preencher dado candidato / sem candidato / resíduo | −7,77 / −3,18 / −3,54 / −1,60 | idem | 3e-14 |
| D-c | funil bruto, preenchida abaixo / acima | 33,31% / 33,48% | idem | 6e-17 |
| D-d | concorrentes na UF / bolsa média na CIR | +10,64 / +2,93 | idem | 5e-13 |
| D-e | REGIC (célula / município × ciclo / U), vínculos do curso na CIR | −0,08 / −0,29 / −0,14, −0,33 | idem | 1e-13 |
| D-f | Q2 do ciclo 2: todas / sem só CR / só imediatas | −27,84 / −12,92 / −12,88 | idem | 3e-14 |
| D-g | vínculos SUS pré por 10 mil hab. (U) | −4,53 | −4,53 | 1e-13 |
| Quanto da queda | D-b composição: Q1 / Q2 / Q3 (razão) | 93% / 32% / 86% | idem | 5e-11 |
| Quanto da queda | D-b sem só CR: Q1 / Q2 / Q3 | 51% / 69% / 40% | idem | 5e-11 |
| Quanto da queda | D-c funil: Q1 / Q2 / Q3 | 34% / 68% / 41% | idem | 1e-10 |
| Quanto da queda | D-d concorrência: Q1 / Q2 / Q3 | 69% / 27% / 39% | idem | 8e-11 |
| Quanto da queda | D-f sem só CR do ciclo 2: Q1 / Q2 / Q3 | 69% / 72% / 79% | idem | 1e-11 |
| Regra "metade ou mais" | 15 linhas de 0,300 recalculadas (sem a D-e) | sim em D-b comp. Q2; D-b sem CR Q3; D-c Q1, Q3; D-d Q2, Q3 | idem | — |

### 3.2 Randomização local com gerador próprio

A estatística observada bate em todas as 12 linhas (diferença ≤ 7e-16). Com a matriz de permutação da
`rdd_lib` e a semente 20261026, o p bate exatamente.

Com um gerador próprio (999 sorteios), o p difere por ruído de Monte Carlo:
- nas linhas de 0,300, no máximo 0,017;
- em Q1 ±0,010, 0,023 contra 0,017;
- a maior diferença está no contraste 0,400 (Q2 ±0,010: 0,454 contra 0,406).

Nada disso muda a leitura.

### 3.3 Tabela "quanto da queda" e regra da metade

- A regra é |salto fixado| ≤ 0,5 × |salto comparado|, só em 0,300.
- Recalculada nas 15 linhas de 0,300 conferidas (D-b, D-c, D-d e D-f), bate.
- Nenhum fator reduz a queda pela metade nas três quantidades ao mesmo tempo.
- A D-f não reduz nenhuma das três na amostra conjunta. Entra entre as candidatas só pelo critério
  próprio do ciclo 2: a queda do ciclo 2 vai de −27,8 para −12,9 p.p., ficam 46%.

## 4. Fidelidade ao protocolo 61

| Regra | Situação |
|---|---|
| Q1–Q3 reproduzidos antes de qualquer teste, com parada se não baterem | ok; 10 comparações, 6,9e-17 |
| Lista fechada D-a a D-g, todas relatadas, em 0,300 e 0,400 | ok; nenhuma explicação a mais, nenhuma omitida |
| D-a: grade de 0,250 a 0,450, passo 0,005, sem os pontos a menos de h dos cortes reais | ok. A leitura "a menos de h" mantém os pontos a exatamente 0,050 (0,250; 0,350; 0,450). A leitura estrita não deixaria nenhum placebo |
| D-a: p por posto, fração com \|t\| > 1,96; Fisher ±0,010 e ±0,020, 999 permutações, semente 20261026 | ok |
| D-b (i) a (iii) | ok nos números. Na leitura, a tabela da §10 compara a composição com o Q3 original, e não com o "Q3 sem eles" do protocolo (achado B1). A leitura não muda |
| D-c: partes do funil e motivo de não alocação onde a base distingue | ok. As ausências estão registradas: nota contra a 2ª opção, desclassificação nos ciclos 2 e 3, desistência. A identidade dos motivos fecha (5e-15). A regra dos 2/3 é do script (achado B4) |
| D-d, D-e, D-g: saltos e controle | ok |
| D-f: com e sem só CR, só imediatas, contagem, regra do edital | ok. O texto do Edital nº 3/2026 não está arquivado; a ausência está registrada, e o script cita a observação do quadro original do ciclo 2 |
| BKY entre as linhas de salto de cada explicação; nenhuma primária | ok. A família de cada explicação inclui o contraste 0,400 e as linhas por ciclo; no D-b são 80 linhas. É uma leitura válida de "cada explicação" |
| Tabela "quanto da queda" com o salto original ao lado | ok |
| Leitura pré-registrada (§3) | ok. O D-a "apoia" (p por posto 0,250 > 0,10) e a leitura é `ACASO_MAIS_POUCOS_MUNICIPIOS`. As demais viram descrição |
| Análises fora do protocolo | ok. A grade de 31 placebos tem o rótulo `COMPLEMENTAR_FORA_DO_PROTOCOLO_61`. Fica fora do BKY e fora da leitura: a função da leitura usa só o rótulo do protocolo |
| Saídas, doc entre marcadores, testes | ok |

**O teste de acaso que não podia reprovar.** O doc diz isso com honestidade em quatro lugares: resposta
curta, ressalva datada, leitura e limites.
- Com 3 placebos, o menor p por posto possível é 0,25, acima do limiar de 0,10.
- A leitura literal é aplicada e qualificada como "acaso não descartado, não demonstrado".
- O desvio está em `DQ_resumo.json["desvios"]`, com data e motivo.
- O que faltava dizer sobre a grade maior (achado B2): os cortes falsos vizinhos compartilham municípios,
  e perto dos cortes reais a janela fica truncada, enquanto o salto real usa a janela inteira. O p de
  0,031 é o menor possível com 31 placebos e é indicativo, não um teste.

## 5. Achados e correções

| # | Gravidade | Achado | Correção |
|---|---|---|---|
| M1 | média | A frase "Para dizer na banca" afirmava mais do que o CSV sustenta. (i) "Menos células foram escolhidas em 1º lugar" vinha como fato, mas o salto é −10,8 p.p. com IC [−28,2; +6,7]. Nas médias da janela inteira, a fração com candidato de 1ª opção é **maior** acima (48,3% → 51,7%); só a ±0,010 ela é menor (61,7% → 45,2%). (ii) "Mais vagas de cursos que preenchem pouco": o índice é por célula, não por vaga. (iii) "No ciclo 2 vaga de reserva não podia ser preenchida" é uma regra que vale dos dois lados. Para explicar a queda falta o que o CSV mostra: no corte, o lado de cima do ciclo 2 tinha mais células só de reserva (+28,4 p.p., IC exclui zero). (iv) A frase omitia que a fração preenchida nas médias da janela é igual dos dois lados (33,3% e 33,5%), isto é, que a queda vem da reta levada até o corte. (v) Omitia a concorrência, que é um dos fatores que mais reduzem a queda (Q2 27%, Q3 39%). A medida dela salta no corte (concorrentes na UF +10,6, IC exclui zero) | Frase regerada das saídas, cláusula a cláusula, com a condição de sinal e incerteza de cada uma (versão final na seção 8): (i) "(estimativa imprecisa)" quando o IC contém zero; (ii) "células"; (iii) "mais células desse lado eram só de reserva"; (iv) "estimado no corte" e as médias da janela; (v) a concorrência na UF; e "nenhum fator nas três" |
| B1 | baixa | O teste D-b (ii) do protocolo compara Q3 com a composição contra "Q3 sem eles". Lido assim, o salto vai de −14,4 para −6,3 p.p. (sobram 44%) e cai pela metade. A §10 compara com o Q3 original (−7,3; sobram 86%) e o doc não fazia a leitura literal. O D-b já estava entre as candidatas; a leitura não muda | Bloco novo `db_q3_leitura` no §4 do doc 57l, gerado das saídas, com as duas leituras e o motivo da escolha da §10 |
| B2 | baixa | A ressalva da grade complementar não dizia que os 31 placebos são dependentes e que, perto dos cortes reais, a janela fica truncada | A ressalva datada ganhou essa frase e "o p por posto dela é indicativo, não um teste" |
| B3 | baixa | O "Como ler" da figura de placebos falava em "ponto cinza" e "salto", mas o eixo é a estatística t. Os pontos pretos (os 3 placebos do protocolo) não eram explicados | Texto novo: "em erros-padrão (t)"; pretos são do protocolo e cinza vazados, fora dele; cortes vizinhos não são sorteios independentes. A imagem não mudou |
| B4 | baixa | A regra "concentra se a maior contribuição for ≥ 2/3 da soma" aparecia como "fixada no script antes de rodar". Ela não está no protocolo, e o commit único não permite verificar quando foi fixada. Não muda nada: a maior parte leva 54% | Doc e `decisoes` dizem "regra do script, não do protocolo"; o histórico não mostra quando foi fixada; qualquer limiar acima de 54% dá a mesma leitura |
| B5 | baixa | Na tabela da leitura (§11), a D-f aparece entre as que "reduzem pela metade", mas na §10 as três linhas da D-f dizem "não". Ela entra só pelo critério do ciclo 2 | A célula diz "D-f (só pelo critério do ciclo 2; na §10 não reduz)" |
| B6 | baixa | A distância à origem (D-e) usa o G1, medido no CNES da competência de referência de cada ciclo (202506, 202510, 202602). O doc e a docstring diziam só "CNES no pré 202406–202506". Não fere o protocolo, que proíbe CNES ≥ 202609 | Bloco novo `de_origem` no §7 (lido de `G1_resumo.json`) e docstring ajustada |

**Hashes depois da correção**
- `DQ_estimativas.csv` `81897f10…`: não mudou.
- As três figuras não mudaram: `DQ_placebos.png` `8b874aa0…`, `DQ_quanto_da_queda.png` `806b888c…`,
  `DQ_funil.png` `02863905…`.
- `DQ_resumo.json`: `b2e7170e…` → `ad5a3b53…`. Mudaram só o `como_ler` da figura de placebos e uma
  frase de `decisoes`.

**Mudanças no código e nos testes**
- Script 38, só texto:
  - a frase da banca, em `resposta_curta`;
  - `leitura_db_ii`, nova;
  - blocos `db_q3_leitura` e `de_origem`;
  - ressalva da grade complementar;
  - regra dos 2/3;
  - célula da D-f na leitura;
  - `COMO_LER` da figura de placebos;
  - `DECISOES` e docstring;
  - constante `G1_RESUMO`.
- `tests/test_diagnostico_queda_0300.py` ganhou `TestCorrecoesAuditoria33` (2 testes):
  - a frase da banca diz "estimativa imprecisa" se e só se o IC de P(candidato) contém zero;
  - não diz "vagas de cursos";
  - traz as médias da janela lidas do CSV;
  - as notas da auditoria estão no doc;
  - as competências do G1 são anteriores a 202609 e aparecem no doc.

## 6. Linguagem

- O doc chama tudo de descritivo e pós-resultado. Contraste: o pacote do corte, com a auditoria 18
  citada.
- Não há "a bolsa reduz" afirmativo. A única ocorrência é "Nada disso mostra que a bolsa reduz o
  preenchimento". "Causal" aparece só em "sem teste causal".
- Fatores pós-anúncio (composição, candidatos, concorrência) são ditos como "o que acompanha a queda, não
  o que a causa".
- O parágrafo "Sem a reta" e o achado M1 deixam claro que, nas médias da janela, a fração preenchida é
  igual dos dois lados. Perto do corte (±0,010; 55 municípios), as diferenças aparecem nas médias brutas:
  - preenchida, 45,4% → 26,5%;
  - candidato de 1ª opção, 61,7% → 45,2%;
  - só CR, 50,3% → 67,6%;
  - índice de curso, 26,6 → 22,6.

  Isso é coerente com "depende de poucos municípios perto dele".
- Linhas não recalculadas (seção 2): na D-e, nenhuma medida salta no corte. Igualá-las deixa 107%, 103%
  e 80% da queda, e com a distância recalculada a leitura "não explica" só mudaria se ela sozinha
  revertesse isso. O balanço de generalistas não salta (IC contém zero nas duas unidades).

## 7. Figuras

- As três são legíveis em slide (fonte ≥ 12 pt, 2400 × 1080 px) e têm "Como ler" e "Detalhe técnico"
  no doc e no resumo.
- **Placebos:** os valores batem com o CSV (t real −2,32; −2,63; −1,63). O texto foi corrigido (B3).
- **Quanto da queda:** os pontos e os IC batem com as linhas `fixado`. A linha tracejada é a metade do
  original. Nas linhas de covariável, a comparação no texto é com o original na mesma amostra, e o
  "Detalhe técnico" diz isso.
- **Funil:** são médias brutas da janela. Os valores batem com `funil_bruto` (por exemplo, 33% e 33%
  preenchidas em 0,300). A figura mostra que, na janela inteira, os lados quase não se separam. O
  "Como ler" ("mostra em que passo os dois lados se separam") continua correto.

## 8. Frase "Para dizer na banca" validada

> "Em 0,300 o preenchimento estimado no corte cai, mas os dados só descrevem a queda. No corte, o lado de
> cima tinha mais células de cursos que preenchem pouco em qualquer lugar e mais células do mesmo curso na
> mesma UF; menos células desse lado tiveram candidato de 1ª opção (estimativa imprecisa); e no ciclo 2, em
> que vaga de reserva não podia ser preenchida na 1ª chamada, mais células desse lado eram só de reserva.
> Igualando esses fatores entre os lados, a queda diminui pela metade ou mais em parte das medidas, nenhum
> fator nas três. A queda aparece quando a reta de cada lado é levada até o corte (nas médias da janela,
> 33% das células preenchidas abaixo e 33% acima), e acaso não está descartado. Nada disso mostra que a
> bolsa reduz o preenchimento: o corte junta a bolsa com outras regras."

| Afirmação | Linha do CSV | Valor |
|---|---|---|
| preenchimento estimado no corte cai | reprodução, 0,300 | Q1 −1,45 [−2,67; −0,22]; Q2 −16,0 [−27,9; −4,1]; Q3 −8,4 [−18,5; +1,7] |
| células de cursos que preenchem pouco | D-b, `idx_curso`, 1+2+3 | −4,5 p.p. [−7,1; −2,0], q BKY 0,010 |
| mais células do mesmo curso na mesma UF | D-d, `n_conc_uf` | +10,6 [+3,5; +17,8], q BKY 0,020 |
| menos células com candidato de 1ª opção (imprecisa) | D-c, `P_C`, espec. Q3 | −10,8 p.p. [−28,2; +6,7] |
| ciclo 2: reserva não preenchida na 1ª chamada | `regra_ciclo2` (quadro original, linha 13); zero alocado em célula só de CR no ciclo 2 (o script para se houver) | — |
| ciclo 2: mais células só de reserva acima | D-b, `so_cr`, ciclo 2 | +28,4 p.p., IC exclui zero |
| metade ou mais em parte das medidas, nenhum nas três | `fixado`, 0,300 | D-b comp. Q2 32%; D-b sem CR Q3 40%; D-c Q1 34%, Q3 41%; D-d Q2 27%, Q3 39%; D-f ciclo 2 46% |
| 33% e 33% nas médias da janela | `funil_bruto`, `preenchida` | 33,3% e 33,5% |
| acaso não descartado | `resumo_placebo` e Fisher | p por posto 0,250 (protocolo); Fisher ±0,020: 0,154 / 0,218 / 0,781 |

## 9. Integridade e testes

**Integridade**
- `data/`: nada alterado; os commits auditados e o desta auditoria não tocam em `data/`. Os brutos do
  ciclo 2 são só lidos.
- IVS: nenhum arquivo de `scripts/rdd_bolsa/` cita `ivs_ipea_2010_municipios`, inclusive o 38 e tudo o
  que ele importa (12, 13, 16, 17, 19, 23, 23b, 24, 29, 32 e a `rdd_lib`). A running variable é o `a08`.
- CNES: as leituras diretas filtram 202406–202506 e param fora disso. O G1 usa 202506, 202510 e 202602
  (B6); nada é ≥ 202609.
- Identificadores: nenhuma coluna de identificador pessoal. No JSON, "CPF"/"NOME" aparecem só como nomes
  de colunas do cabeçalho da aba Desclassificados e de chaves de leitura.
- Saídas de outros blocos: não foram regravadas. O manifesto A6 ganhou a linha do script 38, como nos
  blocos anteriores (protocolo 60); é o registro do passo do `run_all`.

**Testes** (logs na pasta temporária da auditoria; não rodei a suíte inteira)

| Teste | Antes da correção | Depois |
|---|---|---|
| `tests/test_diagnostico_queda_0300.py` | 24 passaram, saída 0 | 26 passaram, saída 0 |
| `tests/test_integridade_dados.py` | — | 15 passaram, saída 0 |
| `tests/test_pipeline_rdd_bolsa.py` | — | 4 passaram, saída 0 |
