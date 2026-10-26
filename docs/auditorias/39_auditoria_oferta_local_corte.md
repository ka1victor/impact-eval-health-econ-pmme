# 39. Auditoria independente do protocolo 64: oferta local de especialistas comparada no corte de IVS

> **Data:** 26/10/2026.<br>
> **Objeto:** commits `4083fba` (protocolo congelado), `9d10c82` (decisões D1–D16 do doc 57q) e `93c76c7`
> (execução), trazidos pelo merge de `5de2fab` (branch `claude/vigilant-mccarthy-dd92mc`):
> `scripts/rdd_bolsa/43_oferta_local_corte.py`, `output/rdd_bolsa/OC_estimativas.csv`, `OC_estudo_evento.csv`,
> `OC_resumo.json`, `OC_figuras/` (três PNG), o [doc 57q](../06_execucao/57q_resultados_oferta_local_corte.md) e
> `tests/test_oferta_local_corte.py`, contra o
> [protocolo 64](../06_execucao/64_protocolo_oferta_local_no_corte.md).<br>
> **Veredito:** **APROVADO COM CORREÇÕES** (só de texto).
> - Nenhum número mudou. O script 43 rodou de novo e as três saídas `OC_*`, as três figuras e o doc 57q saíram
>   com o mesmo SHA-256 de antes.
> - A forma reduzida (OC-A1 a A5, em V e em U, com as sensibilidades de h e de pós com pré covariável), o
>   primeiro estágio, o p de Anderson–Rubin em β = 0, o Wald conjunto do pré, o OC-E, o Holm e o BKY foram
>   recalculados com código próprio. Diferença máxima: 7e−12.
> - O conjunto de Anderson–Rubin foi resolvido de forma exata. Nas dez linhas com D1 em V, ele é a reta inteira.
>   "Ilimitado" está certo.
> - A leitura pré-registrada se sustenta: nenhuma primária se distingue de zero, o placebo não se move, o pré
>   passa e o instrumento é fraco nos dois cortes.
> - As correções (seção 6) são de texto no 57q e um teste novo. Nenhuma muda especificação.<br>
> **Proveniência dos números:** lidos de `output/rdd_bolsa/OC_*`. O recálculo ficou fora do repositório
> (scratchpad), como nas auditorias 34 e 37. A conferência que fica no repositório é o teste
> `test_ar_ilimitado_quando_f_abaixo_do_critico`, junto com os testes que já existiam.

## 1. Ordem dos commits e decisões tomadas antes do resultado

| Commit | Hora (UTC) | O que grava |
|---|---|---|
| `4083fba` | 16:02:15 | protocolo 64 congelado; o arquivo não mudou depois (único commit dele) |
| `9d10c82` | 16:07:38 | esqueleto do 57q com a seção 9 (D1–D16) e os marcadores vazios |
| `148479c` | 16:08:33 | adendo 48d, que registra que "nenhuma estimativa do 64 existia" quando foi congelado |
| `93c76c7` | 16:20:55 | script 43, saídas `OC_*`, testes e blocos do 57q |

- Entre `9d10c82` e `93c76c7` o 57q só mudou **dentro** dos marcadores `OC:`. A seção 9 e todo o texto de fora
  ficaram byte a byte iguais. As decisões não foram reescritas depois de ver número.
- O SHA-256 do protocolo gravado em `OC_resumo.json` é o do arquivo de `4083fba`.
- Limite da prova: o script 43 só entra no Git em `93c76c7`. O Git não exclui uma rodada de teste antes de
  16:07. O que há é compatível com a ordem declarada: o script roda em cerca de 3 minutos (rodada desta
  auditoria: 2 min 58 s), o que cabe na janela de 13 minutos entre `9d10c82` e `93c76c7`. O 48d, gravado no
  minuto seguinte a `9d10c82`, confirma. Observação, não achado.

## 2. Fidelidade ao protocolo

| Item do protocolo | Executado | Confere |
|---|---|---|
| Running variable | a08 (IVS 2010 oficial), pela função do E7 | sim |
| Populações | V = U com célula em algum ciclo, menos os 2 tratados com célula só no ciclo 3 (1.037, igual ao `OL_resumo.json`); U = a08 com população 2022 > 0 (5.565) | sim |
| Janelas | pré 2024-06 a 2025-06 (13 meses), pós 2025-10 a 2026-08 (11); evento 2024-06 a 2026-08, referência 2025-06 | sim |
| Outcomes | B1–B5 pelas funções do script 37, importadas | sim |
| ΔY | média pós − média pré, município sem algum mês sai e é contado | sim |
| Estimador | local linear, triangular, h = 0,050, cada corte separado, um município por linha, HC1; sem empilhar | sim |
| D1 e D2 | D1 = chegada até 2026-08 (lista nominal, ciclos 1 e 2); D2 = médicos ligados por 10 mil hab. | sim (ver achado B2 sobre o que o D2 mede) |
| Partes A–E | todas executadas, com OC-A-U e as sensibilidades (h 0,030 e 0,080, IC honesto, pós com pré covariável) | sim |
| Holm | 4 primárias (OC-A1, OC-A2 × 2 cortes) | sim |
| BKY | 24 secundárias: A3–A5 (6), B0 com D1 (2), B1–B5 com D1 (10), D (6) | sim (ver achado B3) |
| Portão do E7 | antes de qualquer estimativa, com parada sem gravar | sim |
| Integridade (§6) | ver seção 4 | sim |

**Decisões D1–D16.** Nenhuma muda o que o protocolo fixava. Elas preenchem o que o protocolo deixava aberto:
grade de Anderson–Rubin (D8), F do primeiro estágio (D9), composição exata do BKY (D10), definição de "pré plano"
(D11), regra de controles da parte D (D12), regras da leitura (D14) e o caso que a tabela do §4 não cobre (D15).
O IC honesto em U é idêntico ao do E7 (F3.1, fator 1, nos dois cortes), como a D16 promete.

**Leitura pré-registrada.** Aplicada como escrita. O código classifica o caso como `nulo` (os quatro IC das
primárias contêm zero). O placebo não rejeita, o pré passa nos seis testes conjuntos, o F robusto fica abaixo de
10 nos dois cortes (razão sem ponto, só o IC de AR), o OC-A3 não é negativo com IC abaixo de zero, a diferença do
OC-D contém zero nos seis casos e o OC-E não salta. As frases do bloco de leitura do 57q seguem a tabela do §4.

## 3. Recálculo independente

O código foi escrito do zero, sem importar a `rdd_lib` nem os scripts 14, 21, 22, 37 ou 43. Lê direto:
- o a08 e a população do Censo 2022;
- `outcomes_V_municipio`;
- a lista nominal, só em `co_ibge`, `dt_inicio_atividade` e `ciclo`;
- o painel a09 e o manifesto a09 (CBO-alvo);
- o a16 (`painel_vinculo_mes`, `chaves_origem`, regra `d1_pos_hoc`).

O estimador é um MQP próprio: [1, x, T, T·x], peso triangular em −h < x < h, EP HC1 com n/(n − k). O Wald do
pré usa os pesos lineares a_i do salto e os resíduos de cada mês: V = f · E' diag(a²) E. Holm e BKY (dois
estágios, q na grade de 0,001) foram escritos de novo.

### 3.1 Amostra e portão

| Item | Gravado | Recálculo |
|---|---|---|
| U / com célula / fora de V / V | 5.565 / 1.039 / 2 / 1.037 | iguais |
| D1 = 1 em V / em U | 315 / 325 | iguais |
| Tratados da parte D, abaixo / acima, em 0,300 e 0,400 | 50 / 53 e 47 / 59 | iguais |
| Portão: salto do F3.1 em U, 0,300 | +0,287332 (E7) | +0,287332068012; diferença para o E7 de 2,3e−15 no salto e 2,8e−16 no EP; n 859 / 654 |

O portão do script 43 (diferença 5,6e−17) passa e é reproduzido por fora.

### 3.2 Forma reduzida, primeiro estágio, Wald do pré e OC-E

Diferença máxima entre o recálculo e `OC_estimativas.csv`:

| Bloco | Linhas | Salto | EP | p |
|---|---|---|---|---|
| Parte A principal (B1–B5, V e U, dois cortes) | 20 | 3,7e−14 | 1,8e−14 | 6,1e−15 |
| Parte A, h = 0,030 e 0,080 | 40 | 1,1e−13 | 2,2e−14 | 2,0e−14 |
| Parte A, pós com pré covariável | 20 | 6,9e−12 | 7,6e−14 | 1,9e−12 |
| OC-B0, D1 em V e em U | 4 | 9,0e−16 | 1,4e−16 | 5,1e−15 (F: 2,9e−15) |
| OC-B1 a B5 com D1 em V: forma reduzida, primeiro estágio, p em β = 0 | 10 | 3,7e−14 | — | 3,9e−15 |
| OC-C, Wald do pré (B1–B3, dois cortes) | 6 | 3,6e−13 (W) | — | 9,7e−15 |
| OC-E | 2 | 4,6e−16 | 1,2e−16 | — |

Os n abaixo / acima batem em todas as linhas. Os pedidos explícitos:

| Item | Recálculo |
|---|---|
| OC-A1 (B1, V) em 0,300 / 0,400 | −0,2291 [−1,507; +1,049], p 0,725 / −0,4558 [−1,856; +0,944], p 0,523 |
| OC-A2 (B2, V) em 0,300 / 0,400 | −6,147 [−20,91; +8,62], p 0,414 / −6,091 [−31,01; +18,83], p 0,632 |
| OC-A3 (B3, V) em 0,300 / 0,400 | −4,752 [−19,26; +9,76] / +0,367 [−12,46; +13,20] |
| OC-A5 (placebo B5, V) em 0,300 / 0,400 | +0,215 [−1,92; +2,35], p 0,844 / −1,094 [−2,72; +0,54], p 0,188 |
| Primeiro estágio, D1 em V, 0,300 / 0,400 | +5,01 p.p. [−20,1; +30,1], F 0,153 / +2,90 p.p. [−22,7; +28,5], F 0,049 |
| Wald do pré, B1 em 0,300 | W = 20,238 (12 gl), p = 0,0627, 1.037 municípios |
| Holm das 4 primárias | 1, 1, 1, 1 (igual) |
| BKY das 24 secundárias | todas q = 1 (igual) |

### 3.3 Anderson–Rubin

**A construção está certa.** Para cada β, o script roda a RDD de ΔY − β·D1 com o mesmo kernel, h e HC1, e
aceita β se p ≥ 0,05. Como os pesos do salto são os mesmos para ΔY e D1, o resíduo é e_y − β·e_d. A estatística
é então a razão de duas quadráticas em β:

t²(β) = (τ_y − β·τ_d)² / (V_yy − 2β·V_yd + β²·V_dd).

O conjunto aceito é {β: (τ_y − β·τ_d)² ≤ 3,84·(V_yy − 2β·V_yd + β²·V_dd)}. O coeficiente de β² é
τ_d² − 3,84·V_dd, que é negativo sempre que o F robusto do primeiro estágio, na mesma amostra, fica abaixo de
3,84. Nesse caso o conjunto é ilimitado: ou é a reta inteira, ou são duas semirretas.

**Resultado exato.** Nas dez linhas com D1 em V (B1–B5 × dois cortes), o F na amostra com ΔY fica entre 0,05 e
0,25, e o discriminante é negativo: o conjunto é a **reta inteira**. Nenhum β é rejeitado. A grade do script
(4.001 pontos em ±2·max|ΔY|) aceita todos os pontos e marca os dois lados como abertos, o que é coerente. O IC
ilimitado com F ≈ 0,2 é o esperado: o corte não move a chance de receber médico. A razão *fuzzy* não é
informativa, e só a forma reduzida diz algo.

O p em β = 0 é o p da forma reduzida na mesma amostra (conferido, 3,9e−15).

### 3.4 O que não foi recalculado por fora

O ATT da chegada por lado (OC-D) não foi refeito do zero. O estimador é o Callaway–Sant'Anna do script 37,
auditado na auditoria 34 com diferença máxima de 2e−15. O script 43 confere que a função de influência do ATT
médio reproduz o `estimar_cs` (tolerância 1e−12). Aqui foram conferidos os grupos (contagens da seção 3.1), a
regra da D12 no código e a diferença = acima − abaixo (teste existente).

## 4. Integridade

| Verificação | Resultado |
|---|---|
| `data/ivs_ipea_2010_municipios.csv` | não aparece no 43 nem na cadeia que ele importa (37, 22, 21, 14, `rdd_lib`, `honestdid_lib`); `OC_resumo.json` lista o a08 como running variable |
| Competências ≥ 202609 | o painel a09 e o a16 vão até 202608; a lista nominal, até 2026-07; a lista de ativos de 11/09/2026 só é usada para inícios até 202608 (regra do 37, auditoria 34); o estudo de evento vai de 202406 a 202608 |
| `natureza_dos_dados` | `EMPIRICO` em todas as linhas de `OC_estimativas.csv` e `OC_estudo_evento.csv` e no resumo |
| Nada imputado | ΔY ausente quando falta mês (contado: 4 em V e 6 em U para B2–B4); zero do B3 e do D2 só onde o a16 tem a competência (manifesto conferido antes) |
| `E7_*`, `OL_*`, `EQ_*` | SHA-256 iguais antes e depois de rodar o 43; nenhum commit do protocolo 64 os toca |
| Determinismo | o 43 rodou de novo: `OC_estimativas.csv`, `OC_estudo_evento.csv`, `OC_resumo.json`, as três figuras e o 57q saíram byte a byte iguais |
| Testes | `tests/test_oferta_local_corte.py`: 25 passam (com o teste novo); os testes do `test_pipeline_rdd_bolsa.py` sobre ordem e dependências do 43 passam |

## 5. Achados

Nenhum achado alto ou médio.

**Baixos**

- **B1. Números da razão fraca no CSV.** Em `OC_estimativas.csv`, as linhas `fuzzy_*` guardam em `tau` a conta
  forma reduzida ÷ primeiro estágio (por exemplo, −95,6 para B2 em 0,300). Em `ar_ic_inf`/`ar_ic_sup`, guardam a
  borda da grade (±L). A nota e as colunas `ar_aberto_*` avisam, e o 57q mostra "— (fraco)". Ainda assim, quem
  ler só o CSV pode levar um ponto ou um "IC" para o deck, o que o §4 do protocolo proíbe. **Correção:** texto no
  57q §5.4. Mudar o CSV mudaria o esquema da saída e fica como sugestão para o autor: `tau` vazio quando
  F < 10.
- **B2. O D2 não mede a intensidade da alocação.** Pela D6, o D2 conta médicos ligados dos ciclos 1 e 2 com
  **qualquer** vínculo SUS em CBO-alvo no município, desde o primeiro mês de chegada nacional (202509). Entra o
  médico alocado em outro município e entra o vínculo de antes do início do próprio médico. O D2 é positivo em
  884 municípios, contra 325 tratados em U. A D6 segue a letra do protocolo e o D2 é só sensibilidade (F < 1),
  mas o rótulo "intensidade" engana. **Correção:** texto no 57q §5.3.
- **B3. Testes repetidos no BKY.** Pela D10, o p de OC-B1 a B5 é o p de AR em β = 0, que é o p da forma reduzida.
  Assim, OC-A3, A4 e A5 entram duas vezes, e o p das duas primárias também entra na família secundária. Isso
  segue o protocolo (que lista B0–B5 no BKY) e só torna o BKY mais conservador. Sem as dez linhas repetidas (14
  testes), todo q continua 1. Sem efeito na leitura; registrado.
- **B4. Texto da D5 incompleto.** A D5 diz que, em U, "os dois tratados sem célula nos ciclos 1 ou 2" têm D1 = 1.
  Os tratados de U fora de V são 10: 2 com célula só no ciclo 3 e 8 sem célula em nenhum ciclo do quadro. O
  código já dá D1 = 1 a todos os 325, que é a definição do protocolo. A seção 9 é congelada e não foi editada.
  **Correção:** esclarecimento datado na seção 8 do 57q.
- **B5. Leitura dos ATT de cada lado no OC-D.** A tabela 5.6 mostra o ATT de cada lado, e alguns têm IC fora do
  zero, por exemplo B1 acima de 0,300. Esses ATT herdam o problema do 57k: o pré já subia e a ruptura M̄ < 1. O
  protocolo só lê a diferença, e o bloco de leitura também, mas o texto da seção não avisava. **Correção:** texto
  no 57q §5.6.
- **B6. Meses isolados no estudo de evento.** 7 dos 150 meses estimados têm IC fora do zero:
  - B1 em 0,400: 2024-12 a 2025-02, no pré;
  - B2 em 0,300: 2026-05 e 2026-06;
  - B2 em 0,400: 2025-09 e 2025-10.

  É perto dos 5% esperados ao acaso, e a regra (D11) usa o teste conjunto. No B1 em 0,300, o p do pré é
  0,063: passa, mas no limite e com todos os pontos do pré do mesmo lado. O bloco de leitura diz só "o pré é
  plano em todos". **Correção:** texto no 57q §5.5, sem número fora de bloco gerado.

**Observações (sem correção)**

- O1. O IC honesto (M da regra de bolso, como no E7) é largo demais para informar, por exemplo B1 em V, 0,300:
  ±23. Isso já valia no E7.
- O2. O OC-E não salta, mas o IC tem meia-largura de 8 a 11 p.p.: o teste não exclui uma seleção moderada de V. A
  parte A em U, que não depende de V, também não se distingue de zero.
- O3. A frase pré-registrada "não se detecta que a chegada mude a oferta de forma diferente onde a bolsa é
  maior" vem do protocolo. "Onde a bolsa é maior" quer dizer "do lado de cima do corte" (pacote). Mantida.

## 6. Correções feitas

| Arquivo | O que mudou |
|---|---|
| `docs/06_execucao/57q_resultados_oferta_local_corte.md` | cabeçalho aponta esta auditoria; §5.3 explica o que o D2 mede (B2); §5.4 explica "ilimitado" (reta inteira, solução exata) e diz que `tau` e a borda da grade das linhas *fuzzy* não são estimativas para relatar (B1); §5.5 trata dos meses isolados e do pré do B1 em 0,300 (B6); §5.6 diz que só a diferença é lida (B5); §8 traz o esclarecimento da D5 (B4). Tudo fora dos blocos gerados e sem número de resultado. |
| `tests/test_oferta_local_corte.py` | o cabeçalho esperado passa a ser o desta auditoria; teste novo `test_ar_ilimitado_quando_f_abaixo_do_critico` (com F robusto < z², as linhas *fuzzy* têm de estar abertas dos dois lados) |

O script 43 não foi alterado. Nenhuma saída de `output/` mudou.

## 7. O que o desenho identifica (para o autor)

- **Forma reduzida (parte A).** Mede o **pacote do corte**: a bolsa de R$ 5 mil a mais e as outras regras
  federais em 0,300 e 0,400 (auditoria 18), sobre a **mudança** na oferta cadastrada. A DiRD tira só a parte
  dessas regras que é constante no tempo. Não é efeito da bolsa sozinha, nem da participação no PMM-E, nem do
  Agora Tem Especialistas. O resultado: nos dois cortes, a mudança na oferta local de especialistas não se
  distingue entre os lados.
- **Razão *fuzzy* (parte B).** Só seria efeito de receber médico sob exclusão (o corte mexer na oferta só pelo
  médico do programa), e o pacote do corte pode violar isso. Aqui a questão nem chega a valer: o corte não move a
  chance de receber médico (F < 1). O conjunto de Anderson–Rubin é a reta inteira e não diz nada sobre o efeito
  de receber médico.
- **Para a banca.** "Comparando os dois lados do corte de IVS, a mudança na oferta cadastrada de especialistas
  não se distingue; e o lado do corte não muda a chance de o município receber médico do programa, por isso esse
  corte não serve para medir o efeito da chegada."
