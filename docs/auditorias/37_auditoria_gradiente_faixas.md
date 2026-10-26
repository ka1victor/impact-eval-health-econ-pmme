# Auditoria independente do protocolo 62: gradiente do preenchimento dentro das faixas da bolsa

> **Data:** 26/10/2026.<br>
> **Objeto:** commits `3e89731` (protocolo), `ae3dc5d` (execução) e `e4ceb30` (G-f aponta a auditoria 35):
> `scripts/rdd_bolsa/39_gradiente_faixas.py`, `output/rdd_bolsa/GF_estimativas.csv`, `GF_resumo.json`,
> `GF_figuras/` (três PNG), o [doc 57m](../06_execucao/57m_gradiente_faixas.md) e
> `tests/test_gradiente_faixas.py`, contra o
> [protocolo 62](../06_execucao/62_protocolo_gradiente_dentro_das_faixas.md).<br>
> **Veredito:** **APROVADO COM CORREÇÕES.**
> - Nenhum número mudou. `GF_estimativas.csv` e as três figuras têm o mesmo SHA-256 antes e depois da
>   correção.
> - As 75 inclinações executadas foram recalculadas com código próprio. Inclinação, EP, p, fração da subida,
>   regra da metade, células e municípios batem em todas (diferença máxima 9e-12). O q BKY bate exatamente.
> - A leitura pré-registrada está aplicada corretamente.
> - A frase "Para dizer na banca" afirmava mais do que o CSV sustenta sobre a janela de 0,050 (achado M1).
>   As correções são de texto e foram feitas no script 39, que regravou o doc 57m e o `GF_resumo.json`.<br>
> **Proveniência dos números:** os números do 57m vêm de `output/rdd_bolsa/GF_estimativas.csv` e
> `GF_resumo.json`. Os números novos desta auditoria (leave-one-out, janelas alternativas, inclinações da
> RDD) vêm do script de recálculo fora do repositório (seção 2). São registro de auditoria: não entram no
> deck sem passar por script versionado em `output/` (achado B4). A conferência que fica no repositório é
> `TestCorrecoesAuditoria37` em `tests/test_gradiente_faixas.py`.

## 1. Ordem dos commits

- `3e89731` toca dois arquivos: o protocolo 62 e o registro de mudanças. Não há conta nele.
- `ae3dc5d` é o filho direto. Traz o script, as saídas, o doc 57m, os testes, as linhas do `run_all.py`,
  do `test_pipeline_rdd_bolsa.py`, do `tests/README.md` e do manifesto A6.
- `e4ceb30` só troca o relato do G-f, que passa a apontar a auditoria 35. Os números ficam idênticos.
- O protocolo não mudou depois de congelado. O SHA-256 do texto atual (`01995cf4…`) é o gravado em
  `GF_resumo.json["protocolo"]`.
- O protocolo declara o estatuto `DESCRITIVO_62_POS_RESULTADO`: a subida foi vista na figura de dados crus
  antes de o protocolo ser escrito. O doc 57m repete isso no topo e nos limites.

## 2. Como a auditoria foi feita

O recálculo está num script próprio, fora do repositório. Ele não importa os scripts 38 e 39, nem a
`rdd_lib`, nem os scripts que o 38 importa.

**Dados montados do zero**
- Células: `outcomes_V_celula.parquet`. Running variable: IVS do `a08` × 1000. A célula sem IVS sai,
  e ficam 5134 células.
- Célula preenchida: `n_alocados_ch1 ≥ 1`. Faixas: s ≤ 300, 300 < s ≤ 400, s > 400. Janela: 250 < s ≤ 300 e
  350 < s ≤ 400.
- Macrorregião e UF: dígitos do código IBGE.
- CIR: o `.cnv` do TabNet, com leitor próprio. REGIC: o `.xlsx` do IBGE (1º dígito de "Hierarquia - grupo").
  População: o CSV do Censo 2022.
- Tipo do estabelecimento: o cardápio do ciclo 3, lido do `.xlsx` bruto. Gestão: o quadro OFERTA_VAGAS da
  1ª chamada; CNES com gestões diferentes no ciclo fica ausente.
- G-b: G1 (`g1_cpf_nome`) com as escolhas e as vagas oferecidas do quadro inteiro, por (ciclo, curso, UF ou
  CIR).
- G-e: outras células do mesmo ciclo e curso na CIR, contadas no universo com IVS e CIR.

**Estimador próprio**
- MQO com intercepto, IVS/0,100 e dummies de ciclo, mais os fatores. Colinearidade é resolvida por posto.
- EP CR1 por município. IC e p pela normal.
- BKY: implementação própria do q "aguçado" de Benjamini, Krieger e Yekutieli (algoritmo de Anderson,
  grade de 0,001).

Para a ligação com a RDD (seção 5), o A3 em 0,300 foi refeito:
- kernel triangular, h = 0,050;
- intercepto, inclinação e inclinação × lado por ciclo, com salto comum;
- efeitos fixos de curso × ciclo e tipo de vaga;
- CR1 por município.

O salto reproduz o Q3 da auditoria 33: −8,39 p.p., IC [−18,5; +1,7].

O script 39 também foi rodado de novo com um gancho que registra todo arquivo aberto (seção 7).

## 3. Recálculo contra o gravado

### 3.1 Todas as inclinações

| Conferência | Linhas | Diferença máxima |
|---|---|---|
| inclinação (faixa × trecho × fator × variante) | 75 | 3,9e-12 |
| EP CR1 | 75 | 2,2e-12 |
| p | 75 | 4,4e-12 |
| células e municípios | 75 | 0 |
| original na mesma amostra | 70 | 3,4e-12 |
| fração da subida levada | 70 | 9,1e-12 |
| "reduz pela metade" (sim / não / não se aplica) | 70 | nenhuma divergência |
| q BKY (família: as 75 inclinações executadas) | 75 | 0 |
| médias por faixa de IVS de 0,010 (n e fração) | 64 | 0 (64 de 64) |
| balanço "Norte ou Nordeste", faixa e janela de R$ 10 mil | 2 | 5,9e-12 |

### 3.2 Faixa de R$ 10 mil, linha a linha (recalculado = gravado)

Inclinação em p.p. por 0,100 de IVS. "Leva" = 1 − depois ÷ original na mesma amostra.

| Trecho | Fator | Células / municípios | Original (mesma amostra) | Depois | IC 95% | Leva | Metade? | q BKY |
|---|---|---|---|---|---|---|---|---|
| até 0,300 | original | 2392 / 404 | — | +11,9 | [+6,0; +17,7] | — | — | 0,001 |
| até 0,300 | G-a macrorregião | 2392 / 404 | +11,9 | +3,3 | [−2,8; +9,5] | 72% | sim | 0,213 |
| até 0,300 | G-a UF | 2392 / 404 | +11,9 | +1,3 | [−4,8; +7,3] | 89% | sim | 0,389 |
| até 0,300 | G-b os dois | 2383 / 403 | +12,0 | +6,8 | [+1,7; +11,9] | 44% | não | 0,015 |
| até 0,300 | G-c os três | 2298 / 392 | +10,9 | +6,9 | [+2,2; +11,6] | 37% | não | 0,009 |
| até 0,300 | G-d os dois | 2392 / 404 | +11,9 | +8,9 | [+3,4; +14,4] | 25% | não | 0,005 |
| até 0,300 | G-e | 2383 / 403 | +12,0 | +12,7 | [+6,6; +18,7] | −6% | não | 0,001 |
| até 0,300 | todos juntos | 2289 / 391 | +11,0 | +0,5 | [−4,7; +5,6] | 96% | (não é fator) | 0,486 |
| 0,251 a 0,300 | original | 1180 / 145 | — | +36,1 | [+7,4; +64,7] | — | — | 0,019 |
| 0,251 a 0,300 | G-a macrorregião | 1180 / 145 | +36,1 | +24,5 | [+0,7; +48,2] | 32% | não | 0,042 |
| 0,251 a 0,300 | G-a UF | 1180 / 145 | +36,1 | +21,6 | [−2,2; +45,4] | 40% | não | 0,068 |
| 0,251 a 0,300 | G-b UF | 1180 / 145 | +36,1 | +24,0 | [−2,0; +49,9] | 33% | não | 0,065 |
| 0,251 a 0,300 | G-b CIR | 1171 / 144 | +35,6 | +21,6 | [−5,4; +48,5] | 39% | não | 0,097 |
| 0,251 a 0,300 | G-b os dois | 1171 / 144 | +35,6 | +19,9 | [−6,1; +45,8] | 44% | não | 0,110 |
| 0,251 a 0,300 | G-c curso × ciclo | 1180 / 145 | +36,1 | +33,5 | [+7,1; +59,8] | 7% | não | 0,019 |
| 0,251 a 0,300 | G-c só CR | 1180 / 145 | +36,1 | +30,1 | [+7,3; +53,0] | 17% | não | 0,015 |
| 0,251 a 0,300 | G-c tipo e gestão | 1114 / 141 | +36,9 | +34,9 | [+9,0; +60,8] | 5% | não | 0,014 |
| 0,251 a 0,300 | G-c os três | 1114 / 141 | +36,9 | +32,4 | [+11,7; +53,2] | 12% | não | 0,006 |
| 0,251 a 0,300 | G-d log(pop.) | 1180 / 145 | +36,1 | +28,2 | [+2,5; +53,9] | 22% | não | 0,034 |
| 0,251 a 0,300 | G-d REGIC | 1180 / 145 | +36,1 | +35,5 | [+12,3; +58,8] | 2% | não | 0,007 |
| 0,251 a 0,300 | G-d os dois | 1180 / 145 | +36,1 | +31,9 | [+8,8; +55,0] | 12% | não | 0,013 |
| 0,251 a 0,300 | G-e | 1171 / 144 | +35,6 | +40,2 | [+10,3; +70,0] | −13% | não | 0,014 |
| 0,251 a 0,300 | todos juntos | 1105 / 140 | +36,4 | +26,1 | [+4,8; +47,3] | 28% | (não é fator) | 0,021 |

As faixas de R$ 15 e de R$ 20 mil também batem (estão nas 75 linhas da seção 3.1).

### 3.3 Regra da metade e leitura

A regra de leitura (§3) e o "reduz pela metade" foram refeitos nas 70 linhas de fator. A leitura gravada
em `GF_resumo.json["leitura"]` está certa nos seis trechos:
- R$ 10 mil, faixa inteira: G-a (as duas variantes).
- R$ 10 mil, janela: nenhum fator.
- R$ 15 mil, faixa inteira: G-a e G-c (só CR; os três).
- R$ 15 mil, janela: G-a (UF) e G-c (curso × ciclo; só CR; os três).
- R$ 20 mil: sem subida.
- R$ 20 mil, janela: não se aplica.

## 4. A afirmação central para a banca

> "Dentro da faixa de R$ 10 mil a subida anda junto com a região (Nordeste) e quase some dentro da mesma UF;
> nos últimos 0,050 antes de 0,300 sobra uma subida forte sem fator."

### 4.1 Cada número

| Afirmação | Confere? | O que o CSV e o recálculo mostram |
|---|---|---|
| a faixa sobe | sim | +11,9 [+6,0; +17,7], 2392 células, 404 municípios |
| anda junto com a região | sim, pela regra | UF leva 89% (+1,3 [−4,8; +7,3]); macrorregião, 72% |
| Nordeste | sim | 483 células em 22 municípios; 42,9% preenchidas (outras regiões: 19,7% a 28,0%); IVS médio 0,280 (outras: até 0,256). Balanço: +49,1 p.p. de células no Norte ou Nordeste por 0,100 de IVS [+32,4; +65,7] |
| quase some na mesma UF | sim | de +11,9 para +1,3 |
| subida forte nos últimos 0,050 | forte, mas imprecisa | +36,1 [+7,4; +64,7]; 1180 células, 145 municípios |
| "sem fator" | **não, como está escrito** | Pela regra, nenhum fator leva metade. Mas a mesma UF leva 40% e os candidatos por perto, 44%. Comparando dentro da mesma UF, o IC passa a incluir zero (+21,6 [−2,2; +45,4]). "Todos juntos" leva só 28%, e o IC continua sem zero (+26,1 [+4,8; +47,3]) |

### 4.2 O que a frase escondia: a região e a janela são quase as mesmas células

Contagem refeita no recálculo e agora escrita no 57m (lida das linhas `regiao` e do balanço):
- Das 641 células do Norte e do Nordeste na faixa de R$ 10 mil, 563 estão nos últimos 0,050.
- Do Nordeste sozinho: 463 de 483 células, em 20 dos 22 municípios.
- São Teresina (67 células, IVS 0,288), Mossoró, Sobral, João Pessoa, Campina Grande, Natal, Floriano,
  Picos, Patos, Aracaju e outros, todos entre 0,251 e 0,300.

Recálculo fora do 57m, só para leitura:
- Até 0,250, a faixa quase não sobe: +4,4 [−6,4; +15,1], p = 0,43, com 1212 células e 259 municípios.
- Com UF, sobra +1,4; com macrorregião, +0,6.

Logo, "a faixa sobe junto com a região" e "a janela sobe sem fator" não são duas subidas separadas:
- A subida da faixa mora quase toda nos últimos 0,050.
- É ali que estão as células do Nordeste.
- O efeito fixo de UF "leva" a subida da faixa inteira porque compara o Nordeste, todo perto de 0,300, com
  o Sul e o Sudeste, de IVS mais baixo.
- Dentro da janela, a mesma UF leva só 40%.

### 4.3 Janela de 0,050: quantos sustentam a subida

**Composição**
- 1180 células, 145 municípios e 49 valores distintos de IVS.
- Por ciclo: 288, 386 e 506 células.
- Por macrorregião:

  | Macrorregião | Células | Municípios |
  |---|---|---|
  | Norte | 100 | 11 |
  | Nordeste | 463 | 20 |
  | Sudeste | 327 | 65 |
  | Sul | 79 | 10 |
  | Centro-Oeste | 211 | 39 |

- Os 5 maiores municípios têm 21% das células; os 10 maiores, 36%.

**Médias por faixa de IVS de 0,010 (preenchidas; células; municípios)**

| IVS | Preenchidas | Células | Municípios |
|---|---|---|---|
| 0,251–0,260 | 26,0% | 250 | 35 |
| 0,261–0,270 | 31,0% | 210 | 31 |
| 0,271–0,280 | 31,4% | 185 | 25 |
| 0,281–0,290 | 34,7% | 352 | 27 |
| 0,291–0,300 | 45,4% | 183 | 27 |

Em faixas de 0,005, o pico está em 0,291–0,295 (47,2%; 159 células; 16 municípios). Em 0,296–0,300 a
fração cai para 33,3%, com só 24 células em 11 municípios.

**Leave-one-out por município** (145 retiradas, mesmo modelo do 57m)

| Especificação | Inclinação mínima | Mediana | Máxima | Retiradas com p > 0,05 |
|---|---|---|---|---|
| original | +30,1 (sem Teresina) | +36,0 | +41,4 (sem Cuiabá) | 0 de 145 |
| G-a UF | +17,3 (sem Goiânia) | +21,6 | +32,0 (sem Cuiabá) | 140 de 145 |
| todos juntos | +18,4 (sem Mossoró) | +26,1 | +31,5 (sem Curitiba) | 4 de 140 |

Nenhum município sozinho faz a subida. Ela fica entre +30 e +41 p.p. e sempre com p < 0,05.

**Retirando os maiores municípios, em ordem de células, de forma cumulativa**

| Retirados | Inclinação | IC 95% | p |
|---|---|---|---|
| 0 | +36,1 | [+7,4; +64,7] | 0,014 |
| 1 (Teresina) | +30,1 | [+1,9; +58,3] | 0,036 |
| 4 | +28,6 | [−4,1; +61,3] | 0,086 |
| 10 | +25,3 | [−13,2; +63,9] | 0,198 |

O sinal fica; a precisão some com poucos municípios grandes.

**Outras janelas antes de 0,300 (só leitura; o protocolo fixa 0,050)**

| Janela | Inclinação | IC 95% | Municípios |
|---|---|---|---|
| 0,020 | +95,0 | [−29,9; +219,9] | 54 |
| 0,030 | +60,9 | [+0,8; +121,0] | 79 |
| 0,040 | +31,2 | [−19,7; +82,1] | 110 |
| 0,050 (protocolo) | +36,1 | [+7,4; +64,7] | 145 |
| 0,060 | +33,6 | [+11,8; +55,5] | 177 |
| 0,070 | +32,8 | [+15,5; +50,1] | 204 |
| 0,100 | +15,0 | [+4,8; +25,2] | 291 |

**Média por município × ciclo** (uma linha por município e ciclo, sem peso): +38,4 [+7,9; +68,9],
245 linhas.

**Conclusão**
- A subida da janela não depende de um município.
- É imprecisa: o IC é largo, inclui zero na janela de 0,040 e depois de retirar quatro municípios grandes.
- O pico está em 0,286–0,295, não no último milésimo antes do corte.
- "Forte" se sustenta como tamanho do ponto, com "imprecisa" ao lado.

## 5. Ligação com a queda em 0,300

**A explicação é coerente com o 57l e o 49b.**
- O 57l mostra que, nas células da janela, sem reta, a fração preenchida é 33,3% abaixo e 33,5% acima de
  0,300. A queda aparece quando a reta de cada lado é levada até o corte.
- O 49b (§6) mostra o mesmo nas médias locais constantes. Sem peso: janela de 0,030, −0,2 p.p.; adendo de
  0,050, +9,6 p.p.
- Uma reta de baixo íngreme leva o ponto de partida do lado de R$ 10 mil, em 0,300, acima da média da
  janela. Esse é o mecanismo aritmético da queda estimada.

**Mas é metade da história.** O lado de cima também sobe. No mesmo modelo do 57m, de 0,301 a 0,349: +26,2
[−1,2; +53,6], 935 células, 120 municípios. Com médias iguais dos dois lados, as duas retas inclinadas para
cima abrem o degrau no corte. O 57l já diz "a reta de cada lado"; o 57m fala só da de baixo, o que não é
erro, mas é parcial.

**A inclinação da janela não é a que a RDD usa.** As células são as mesmas: 0,251 a 0,300 é exatamente o lado
de baixo da janela da RDD (|IVS − 0,300| < 0,050). A reta é outra:

| Reta do lado de baixo de 0,300 (p.p. por 0,100) | Ciclo 1 | Ciclo 2 | Ciclo 3 | Média (peso do kernel) | Salto em 0,300 |
|---|---|---|---|---|---|
| A3/Q3 da RDD: kernel triangular, uma reta por ciclo, EF curso × ciclo e tipo de vaga | +58,2 | +42,7 | +20,4 | +36,1 | −8,39 |
| A3 sem efeitos fixos | +67,2 | +51,2 | +25,3 | +43,0 | −16,1 |
| A3 com kernel uniforme | +29,5 | +28,3 | +31,5 | +30,0 | −6,4 |
| 57m: uma reta comum, EF de ciclo, peso uniforme | — | — | — | +36,1 | — |
| 57m com kernel triangular | — | — | — | +43,8 | — |

A coincidência dos dois +36,1 é numérica, não de especificação. O texto do 57m dizia "o mesmo trecho"; agora
diz "as mesmas células, não a mesma reta".

## 6. Fidelidade ao protocolo 62 e escolhas do agente

| Regra ou escolha | Situação | Defensável? Muda a leitura? |
|---|---|---|
| Amostra: células abertas dos ciclos 1–3, base do A3 | ok; 5134 células; faixa pelo IVS oficial = faixa anunciada (o script para se não for) | — |
| MPL, EF de ciclo, CR1 por município, inclinação por 0,100 | ok | — |
| Lista fechada G-a a G-f, todas relatadas, separadas e juntas | ok; G-f só relato (auditorias 18 e 35) | — |
| **"Candidatos por vaga oferecida"** lido como razão do mercado: candidatos do curso e ciclo com origem na UF ou CIR ÷ vagas (imediatas + CR) do curso e ciclo nesse mercado | declarado em `decisoes` | Defensável. A leitura alternativa, candidatos da própria célula por vaga, é quase o outcome (o funil da célula). Os candidatos sem origem no G1 não entram, e a medida é um piso. G-b leva 28% a 44% na faixa e na janela de R$ 10 mil: abaixo da metade em todas as variantes. Definições alternativas não foram testadas |
| **Janela 0,250 < IVS ≤ 0,300** (e 0,350 < IVS ≤ 0,400) | declarada | Defensável e a melhor leitura: são exatamente as células do lado de baixo da RDD. A leitura com 0,250 incluído mudaria pouco. A sensibilidade à largura (seção 4.3) importa mais que a borda |
| **"Metade" só para inclinação positiva** | declarada; R$ 20 mil = "sem subida" | Defensável: a pergunta do protocolo é por que sobe. Não muda a leitura: na faixa de R$ 20 mil nenhum fator sozinho reduz a queda pela metade (o maior leva 28%); todos juntos levam 49% (−14,0 → −7,1) |
| **Tabela de balanço fora do protocolo** | estava em `decisoes` como "fora do protocolo", fora do BKY e fora da leitura (a função da leitura só usa linhas `inclinacao`) | Defensável e útil. Mas as cinco seções diziam só "descritivo, fora do BKY", e a resposta curta usava o +49 p.p. do balanço sem rótulo (B1, corrigido) |
| BKY entre as inclinações; nenhuma primária | ok; família das 75 inclinações executadas | — |
| Leitura pré-registrada (§3) | ok (seção 3.3) | — |
| Figura de médias por 0,010 com reta original e ajustada; "Como ler" em cada figura | ok | — |

## 7. Achados e correções

| # | Gravidade | Achado | Correção |
|---|---|---|---|
| M1 | média | A frase "Para dizer na banca" afirmava mais do que o CSV sustenta. (i) "Sobra uma subida forte que nenhum dado nosso acompanha": pela regra, nenhum fator leva metade, mas a mesma UF leva 40% e os candidatos por perto, 44%, e com a mesma UF o IC inclui zero. (ii) "Forte" sem "imprecisa": o IC é [+7,4; +64,7]. (iii) A frase separa "região" e "janela" como duas histórias, mas 563 das 641 células do Norte e Nordeste da faixa estão na janela (463 de 483 só do Nordeste). (iv) "Preenchem mais vagas": a medida é a fração de células preenchidas, não de vagas (o mesmo deslize da auditoria 33, M1 (ii)) | Frase e parágrafo da janela regerados das saídas pelo script 39: "forte e imprecisa", IC, "nenhum fator sozinho", quanto a mesma UF e os candidatos por perto levam, a contagem 563 de 641 (lida das linhas `regiao` e do balanço) e "células abertas preenchidas". Versão final na seção 9 |
| B1 | baixa | O balanço (fator no lugar do preenchimento) está fora do protocolo, mas as seções 3 a 7 do 57m não diziam isso, e a resposta curta citava o +49 p.p. sem rótulo | "balanço fora do protocolo 62; descritivo, fora do BKY e fora da leitura do §3" nas cinco seções; "(balanço, fora do protocolo)" na resposta curta |
| B2 | baixa | O 57m dizia "é o mesmo trecho que a RDD usa do lado de baixo". As células são as mesmas, mas a reta não: a RDD usa kernel triangular, uma reta por ciclo (+58,2, +42,7, +20,4) e efeitos fixos. O +36,1 igual é coincidência (seção 5) | "São as mesmas células que a RDD usa do lado de baixo de 0,300, mas não a mesma reta" com o porquê; a comparação numérica fica nesta auditoria |
| B3 | baixa | Na tabela da leitura (§10), as variantes saíam com o nome interno ("G-a (macrorregiao)", "G-c (so_cr)") | Rótulos legíveis ("G-a (macrorregião)", "G-c (só cadastro reserva)") na renderização; `GF_resumo.json["leitura"]` mantém os nomes internos |
| B4 | baixa | Os resultados desta auditoria que mudam a leitura da janela não estão em `output/`: a subida até 0,250 é quase nula (+4,4 [−6,4; +15,1]), e a sensibilidade à largura da janela e ao leave-one-out. Pela regra de proveniência, não podem ir para o deck a partir deste documento | Não corrigido (seria análise nova, não texto). Se o autor quiser no deck, recomendo acrescentar ao script 39 a inclinação até 0,250 e o leave-one-out da janela, com rótulo de complementar fora do protocolo |
| B5 | baixa | O 57m explica a queda só pela reta de baixo; o lado de cima também sobe (+26,2 de 0,301 a 0,349) | Não corrigido no 57m (seria número novo). Registrado na seção 5; o 57l já diz "a reta de cada lado" |
| O1 | observação | No título da figura de médias, "+11,9 → +0,5" compara a original da faixa inteira (2392 células) com "todos juntos" estimado nas 2289 células com todos os fatores (original nessa amostra +11,0). O "Detalhe técnico" diz isso | Sem mudança; a diferença não muda a leitura |

**Hashes depois da correção**
- `GF_estimativas.csv` `aaa44638…`: não mudou.
- As três figuras não mudaram:
  - `GF_medias_por_ivs.png` `7e12cac3…`;
  - `GF_inclinacao_fatores.png` `6cd1d571…`;
  - `GF_inclinacao_fatores_janela.png` `65c2c787…`.
- `GF_resumo.json`: `e90f6b2d…` → `cfb94c23…`. Mudou só a lista `decisoes`, com uma linha nova.

**Mudanças no código e nos testes**
- Script 39, só texto:
  - `resposta_curta` (parágrafo da faixa, parágrafo da janela, frase da banca);
  - `norte_nordeste_na_janela`, `_media_nota` e `_rot_variante`, novas;
  - rótulo do balanço;
  - rótulos da tabela da leitura;
  - `DECISOES`.
- `tests/test_gradiente_faixas.py` ganhou `TestCorrecoesAuditoria37` (3 testes):
  - a frase da banca não diz "nenhum dado nosso acompanha" nem "vagas";
  - traz "imprecisa", o IC da janela e as frações da UF e do G-b, que ficam abaixo de 50% e acima de zero;
  - a contagem do Norte e do Nordeste é refeita sem o script, a partir do parquet e do a08;
  - o texto diz "não a mesma reta" e rotula o balanço como fora do protocolo nas cinco seções.

## 8. Linguagem

**Descritivo e pós-resultado**
- O 57m chama tudo de descritivo e pós-resultado, no topo, na leitura e nos limites.
- Diz que dentro da faixa a bolsa é constante e que nada ali é efeito da bolsa, da participação no PMM-E ou do
  Agora Tem Especialistas.

**Sem causalidade**
- "Anda junto com" é a forma usada para todo fator.
- "Leva" é definido como a conta 1 − depois ÷ original.
- O teste proíbe "causa", "provoca" e "efeito da bolsa sobre".
- Os fatores formados depois do anúncio (G-b, G-c, G-e) são ditos como "descreve, não isola".

**Dois pontos a cuidar na banca**
- O título do 57m pergunta "por que", como o protocolo, mas a resposta é "com o que anda junto". A frase da
  banca termina com isso.
- "Não se explica com os dados disponíveis" é o rótulo pré-registrado. Agora ele vem com "pela regra do §3" e
  com quanto cada fator leva, para não soar como "nada acompanha".

## 9. Frase "Para dizer na banca" validada

> "Dentro da faixa de R$ 10 mil, onde a bolsa é a mesma, as células abertas dos municípios mais vulneráveis são
> preenchidas com mais frequência. Na faixa inteira, isso anda junto com a região: os de IVS mais alto da faixa
> estão mais no Nordeste, onde as células preenchem mais, e comparando municípios da mesma UF a subida quase
> some. Mas as células do Norte e do Nordeste da faixa estão quase todas (563 de 641) nos últimos 0,050 antes de
> 0,300, e ali sobra uma subida forte e imprecisa (+36,1 p.p. por 0,100, IC 95% [+7,4; +64,7]) que nenhum fator
> sozinho reduz pela metade: comparando dentro da mesma UF, sai 40% dela; com os candidatos por perto, 44%. Na
> faixa de R$ 15 mil a subida é pequena e incerta; na de R$ 20 mil o preenchimento cai. É descrição: mostra com
> o que a subida anda junto, não por quê."

| Afirmação | Linha do CSV | Valor |
|---|---|---|
| células dos mais vulneráveis preenchidas com mais frequência | `inclinacao`, R$ 10 mil, faixa, ORIGINAL | +11,9 [+6,0; +17,7] |
| anda junto com a região; quase some na mesma UF | G-a `uf` e `macrorregiao`, faixa | +1,3 (89%); +3,3 (72%) |
| IVS mais alto no Nordeste, que preenche mais | `regiao`, R$ 10 mil | NE 0,280 e 42,9%; outras até 0,256 e 19,7%–28,0% |
| 563 de 641 na janela | `regiao` (N + NE = 641) e `balanco` `norte_ou_nordeste` na janela (47,7% × 1180 = 563) | 563 / 641 |
| forte e imprecisa | ORIGINAL, janela | +36,1 [+7,4; +64,7] |
| nenhum fator sozinho pela metade; UF 40%, candidatos 44% | G-a `uf`, G-b `uf_e_cir`, janela; `leitura` | 40%, 44%; `SUBIDA_NAO_SE_EXPLICA_COM_OS_DADOS` |
| R$ 15 mil pequena e incerta | ORIGINAL, R$ 15 mil | +7,0 [−3,2; +17,2] |
| R$ 20 mil cai | ORIGINAL, R$ 20 mil | −12,2 [−15,9; −8,6] |

Se o autor quiser uma versão curta para slide: "Dentro da faixa de R$ 10 mil a subida do preenchimento anda
junto com a região: o Nordeste está quase todo perto de 0,300 e, na mesma UF, a subida quase some. Nos últimos
0,050 antes do corte sobra uma subida forte e imprecisa que nenhum fator sozinho reduz pela metade (UF e
candidatos por perto levam cerca de 40% cada). É descrição, não causa."

## 10. Integridade e testes

**Integridade**
- `data/`: nada alterado. Os commits auditados e o desta auditoria não tocam em `data/`. Na rodada com gancho
  de abertura de arquivos, o script 39 só leu de `data/raw/`:
  - CIR;
  - REGIC;
  - metadados de malha;
  - cardápio do ciclo 3.
- IVS: o arquivo `data/ivs_ipea_2010_municipios.csv` não foi aberto (0 ocorrências no registro de
  aberturas). A running variable é o `a08`.
- CNES:
  - o painel `a09` foi aberto uma vez, pelo `carregar()` do 38, com filtro 202406–202506 (conferido na
    auditoria 33);
  - o G1 usa as competências 202506, 202510 e 202602;
  - nada é ≥ 202609.
- Identificadores: nenhuma coluna de identificador pessoal no CSV. No JSON, `id_candidato` e `cpf_nome`
  aparecem só como nome de chave de leitura e de regra de ligação.
- Saídas de outros blocos: não foram regravadas. O script 39 só escreveu em:
  - `GF_estimativas.csv`;
  - `GF_resumo.json`;
  - as três figuras em `GF_figuras/`;
  - o doc 57m.

  O manifesto A6 ganhou a linha do script 39 em `ae3dc5d`, como nos blocos anteriores.
- Determinismo: rodado de novo antes da correção, o script 39 reproduziu os seis arquivos com o mesmo
  SHA-256.

**Testes** (logs na pasta temporária da auditoria; não rodei a suíte inteira)

| Teste | Antes da correção | Depois |
|---|---|---|
| `tests/test_gradiente_faixas.py` | 21 passaram, saída 0 | 24 passaram, saída 0 |
| `tests/test_integridade_dados.py` | 4 passaram, saída 0 | 4 passaram, saída 0 |
| `tests/test_pipeline_rdd_bolsa.py` | 15 passaram, saída 0 | 15 passaram, saída 0 |
