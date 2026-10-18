# Inferência alternativa para a RDD da bolsa (E5)

> **Data:** 18/10/2026.<br>
> **Estado:** **EXPLORATÓRIO, pós-resultado.** Escrito depois de o E3 ser
> lido. O principal continua sendo o do protocolo congelado (local linear,
> kernel triangular, h = 0,050, EP HC1;
> [`37`](37_resultados_rdd_bolsa_ivs_oficial.md)). Nenhuma especificação daqui
> o substitui. Todas as calculadas estão relatadas abaixo ou nos CSVs
> indicados, qualquer que seja o resultado. A lista foi fixada no cabeçalho do
> script antes da primeira execução com dados reais e não foi alterada
> depois.<br>
> **Script:** `scripts/rdd_bolsa/11_inferencia_alternativa.py` (numpy e pandas;
> determinístico; semente 20261018).<br>
> **Saídas:** `output/rdd_bolsa/E5_especificacoes.csv`,
> `E5_decomposicao_ic.csv`, `E5_decomposicao_lados.csv`,
> `E5_lr_selecao_janela.csv`, `E5_lr_sensibilidade_janelas.csv` e
> `E5_resumo.json` (fontes e SHA-256).<br>
> **Teste:** `tests/test_e5_inferencia_sintetico.py` (31 testes, dados
> sintéticos).

Pergunta do autor: por que os ICs do E3 são tão largos, se dá para
estreitá-los e se outro método daria inferência melhor ou diferente.

O contraste continua sendo o **incentivo marginal anunciado de R$ 5 mil**
(Faixa 3 → 2 em 0,300; Faixa 2 → 1 em 0,400), possivelmente um pacote. Não é
efeito do PMM-E nem do Agora Tem Especialistas.

- **Outcome da hipótese (Y1):** fração das células CNES–curso da 1ª chamada
  do ciclo 1 (2025) com alguma confirmação ou homologação.
- **Secundários:** presença de especialista ativo do ciclo na relação de
  09/10/2026 (D1 para o ciclo 1, D2 para o ciclo 2).
- **Populações:** municípios do quadro da 1ª chamada do ciclo 1 (P1, 368) e
  dos quadros do ciclo 2 (P2, 454).
- **Unidade:** município; célula CNES–curso em E1 e E2.

## 1. Por que o IC é largo

Y1, janela h = 0,050, mesma amostra do principal
([`E5_decomposicao_ic.csv`](../../output/rdd_bolsa/E5_decomposicao_ic.csv),
[`E5_decomposicao_lados.csv`](../../output/rdd_bolsa/E5_decomposicao_lados.csv)):

| | 0,300 | 0,400 |
|---|---:|---:|
| municípios abaixo / acima | 61 / 53 | 53 / 41 |
| n efetivo com o kernel triangular | 44 / 39 | 42 / 32 |
| desvio-padrão de Y1 (combinado) | 0,343 | 0,345 |
| municípios com uma única célula (abaixo / acima) | 38% / 26% | 23% / 29% |
| (1) EP da diferença de médias simples | 0,065 | 0,074 |
| (2) × kernel triangular (local constante) | × 1,18 → 0,076 | × 1,13 → 0,083 |
| (3) × inclinações (local linear) | × 2,19 → **0,166** | × 1,92 → **0,160** |
| fator total (3)/(1) | **× 2,57** | **× 2,17** |
| referência teórica, desenho uniforme | × 2,19 | × 2,19 |
| MDE do principal (2,8 × EP) | **46,6 p.p.** | **44,8 p.p.** |

A largura vem de três fatores que se multiplicam:

1. **Ruído do outcome e n pequeno.** Y1 é uma fração de poucas células: 503
   células em 114 municípios na janela de 0,300 (4,4 por município). Entre
   23% e 38% dos municípios de cada lado têm uma única célula, e para eles Y1
   só pode ser 0 ou 1. Com desvio-padrão de 0,34 e cerca de 57 municípios por
   lado, até uma diferença de médias simples teria EP de 0,065, isto é, IC de
   ±13 p.p.
2. **Kernel triangular.** Dá menos peso aos municípios longe do corte: o n
   efetivo cai para 73% a 80% do n. Isso multiplica o EP por 1,13 a 1,18.
3. **Extrapolação até o corte.** O local linear estima o valor de cada reta
   exatamente na borda dos dados, onde a inclinação estimada pesa mais. É o
   fator dominante: × 1,9 a × 2,2. Em 0,300 o fator total (2,57) supera a
   referência (2,19), que supõe municípios uniformes na janela e variância
   constante.

Os quatro estimadores da decomposição, todos na mesma amostra:

| Estimador | 0,300 | 0,400 |
|---|---|---|
| diferença de médias simples | +12,9 [+0,3; +25,6], p = 0,045 | +0,7 [−13,7; +15,2], p = 0,92 |
| local constante triangular (= A) | +5,2 [−9,8; +20,1], p = 0,50 | −0,9 [−17,2; +15,4], p = 0,91 |
| local linear com kernel uniforme | −11,6 [−40,1; +16,9], p = 0,43 | −4,6 [−33,0; +23,8], p = 0,75 |
| local linear triangular (= principal) | −12,8 [−45,5; +19,8], p = 0,44 | −5,1 [−36,5; +26,2], p = 0,75 |

A diferença de médias simples em 0,300 é a comparação bruta (0,243 → 0,372).
Não estima o salto, porque ignora o gradiente de Y1 no IVS, explicado a
seguir.

**Por que a média bruta é maior acima de 0,300, mas o salto é negativo.**

| Lado (0,300) | média bruta | média ponderada pelo kernel | valor da reta no corte | inclinação por 0,01 de IVS |
|---|---:|---:|---:|---:|
| abaixo | 0,243 | 0,287 | **0,407** | +6,7 p.p. |
| acima | 0,372 | 0,339 | **0,279** | +3,2 p.p. |

Y1 sobe com o IVS dos dois lados da janela. A média ponderada de cada lado é
exatamente o valor da reta na posição média ponderada dos municípios: 0,018
abaixo e 0,019 acima do corte. Ao longo de um gradiente crescente, o lado de
cima tem média maior mesmo que a reta caia no corte. O salto compara as duas
retas **no** corte: 0,279 − 0,407 = −12,8 p.p. Em números
([`E5_resumo.json`](../../output/rdd_bolsa/E5_resumo.json), `identidade`):

> média ponderada acima − abaixo (+5,2 p.p.) = salto (−12,8) + inclinação acima (+6,0) + inclinação abaixo (+12,0).

A reta de baixo é íngreme no trecho final antes do corte, e poucos municípios
perto do corte determinam essa inclinação. É por isso que a extrapolação pesa
tanto no EP e que a estimativa pontual muda entre especificações.

## 2. Todas as especificações

### 2.1 Outcome da hipótese (Y1)

Salto em p.p.; IC 95% pela normal, exceto em D (permutação)
([`E5_especificacoes.csv`](../../output/rdd_bolsa/E5_especificacoes.csv)):

| Especificação | Corte | Salto | IC 95% | p | n abaixo / acima | EP | MDE |
|---|---|---:|---|---:|---|---:|---:|
| S0 principal (reprodução) | 0,300 | −12,8 | [−45,5; +19,8] | 0,44 | 61 / 53 | 0,166 | 46,6 |
| S0 principal (reprodução) | 0,400 | −5,1 | [−36,5; +26,2] | 0,75 | 53 / 41 | 0,160 | 44,8 |
| A local constante | 0,300 | +5,2 | [−9,8; +20,1] | 0,50 | 61 / 53 | 0,076 | 21,3 |
| A local constante | 0,400 | −0,9 | [−17,2; +15,4] | 0,91 | 53 / 41 | 0,083 | 23,3 |
| B cortes empilhados | 0,300+0,400 | −8,6 | [−31,2; +14,0] | 0,45 | 114 / 94 | 0,115 | 32,3 |
| C1 + estrato, região, log pop. | 0,300 | −3,5 | [−28,8; +21,8] | 0,79 | 61 / 53 | 0,129 | 36,2 |
| C1 + estrato, região, log pop. | 0,400 | +1,9 | [−24,2; +28,0] | 0,89 | 53 / 41 | 0,133 | 37,2 |
| C2 = C1 + IDHM | 0,300 | −4,1 | [−29,2; +21,0] | 0,75 | 61 / 53 | 0,128 | 35,9 |
| C2 = C1 + IDHM | 0,400 | +2,3 | [−23,8; +28,4] | 0,86 | 53 / 41 | 0,133 | 37,3 |
| D local randomization | 0,300 (±0,020) | −4,4 | [−27,4; +18,7] | 0,70 | 20 / 19 | 0,112 | 31,5 |
| D local randomization | 0,400 (±0,007) | +2,6 | [−33,3; +38,3] | 0,88 | 10 / 9 | 0,164 | 46,0 |
| E0 município, peso × n.º de células | 0,300 | −9,3 | [−34,2; +15,6] | 0,46 | 61 / 53 | 0,127 | 35,5 |
| E0 município, peso × n.º de células | 0,400 | −1,0 | [−28,1; +26,1] | 0,94 | 53 / 41 | 0,138 | 38,7 |
| E1 célula, EP por município | 0,300 | −9,3 | [−33,9; +15,3] | 0,46 | 61 / 53 (503 células) | 0,126 | 35,1 |
| E1 célula, EP por município | 0,400 | −1,0 | [−27,7; +25,8] | 0,94 | 53 / 41 (386 células) | 0,137 | 38,2 |
| E2 = E1 + efeitos fixos de curso | 0,300 | +3,2 | [−20,7; +27,1] | 0,79 | 61 / 53 (503 células) | 0,122 | 34,1 |
| E2 = E1 + efeitos fixos de curso | 0,400 | −10,1 | [−35,9; +15,7] | 0,44 | 53 / 41 (386 células) | 0,132 | 36,8 |

O que cada uma é, e o que muda em relação ao principal:

- **A, local constante.** Diferença das médias ponderadas pelo kernel. Não
  modela a inclinação. Difere do principal exatamente pela contribuição das
  inclinações (+18,0 p.p. em 0,300; +4,2 p.p. em 0,400). Se as inclinações
  forem reais, esse é o viés de A, e o IC de A não o inclui. **O IC estreito
  de A não é ganho de precisão.**
- **B, cortes empilhados** (Cattaneo, Keele, Titiunik e Vazquez-Bare, 2016).
  Running variable s − c, interceptos e inclinações por corte × lado, salto
  comum. As janelas (0,250; 0,350] e (0,350; 0,450] não se sobrepõem:
  nenhum município aparece nas duas. O estimando muda para uma média ponderada
  dos dois saltos. Se os dois forem diferentes, essa média não descreve
  nenhum deles.
- **C1 e C2, covariáveis pré** (Calonico, Cattaneo, Farrell e Titiunik,
  2019). Não entram o IVS e seus subíndices, que são componentes mecânicos da
  running variable, nem nada do arquivo local errado (auditoria 16).
  - C1 usa estrato territorial, macrorregião e log da população 2010 (base
    a08).
  - C2 soma o IDHM 2010. O IDHM não é componente do IVS, mas usa os mesmos
    dados do Censo (correlação −0,88). Por isso fica como acréscimo
    separado.
  - O EP cai 17% a 23%. A estimativa pontual em 0,300 vai de −12,8 para
    −3,5, dentro do IC do principal. As covariáveis predizem Y1 e diferem um
    pouco entre os lados. No E3, porém, não houve desequilíbrio significativo
    nesse corte (por exemplo, capital: −0,19, p = 0,13).
- **D, local randomization** (Cattaneo, Frandsen e Titiunik, 2015; Cattaneo,
  Titiunik e Vazquez-Bare, 2016). Premissa mais forte: dentro de uma janela
  estreita, o lado do corte é como sorteado e Y1 não depende do IVS.
  - **Seleção da janela, gravada antes de ler outcomes.** Só pelo balanço de
    log população, IDHM, estrato e macrorregião. Regra: a maior janela
    simétrica em que o p mínimo é ≥ 0,15 nela e em todas as menores. No ciclo
    1, escolheu ±0,020 em 0,300 e ±0,007 em 0,400. Em 0,400, as janelas de
    ±0,008 em diante reprovam, coerente com o desequilíbrio do E3 nesse corte.
  - **Inferência.** p de Fisher com 10.000 permutações; IC por inversão sob
    efeito constante.
  - **Sensibilidade nas janelas viáveis de ±0,002 a ±0,020**
    ([`E5_lr_sensibilidade_janelas.csv`](../../output/rdd_bolsa/E5_lr_sensibilidade_janelas.csv)):
    nenhum p de Y1 abaixo de 0,40. Nas menores janelas, com 2 a 5 municípios
    por lado, o IC cobre quase toda a grade [−1, +1].
- **E0, E1 e E2, nível célula.**
  - As 1.295 células CNES–curso foram reconstituídas pela fonte canônica
    usada no `08a`. Agregadas, elas reproduzem Y1.
  - E0 (município, peso = kernel × n.º de células) e E1 (célula, EP por
    município) têm o mesmo ponto. O estimando passa a ser o salto médio
    **por célula**, não por município.
  - E2 acrescenta efeitos fixos de curso. A estimativa muda bastante: de −9,3
    para +3,2 em 0,300 e de −1,0 para −10,1 em 0,400. Isso indica que a
    composição de cursos difere entre os lados da janela; não foi testado
    formalmente.

### 2.2 Presença de especialista (secundário)

| Outcome | Especificação | Corte | Salto | IC 95% | p | n abaixo / acima |
|---|---|---|---:|---|---:|---|
| D1 ciclo 1 | S0 principal | 0,300 | −3,2 | [−47,5; +41,1] | 0,89 | 61 / 53 |
| D1 ciclo 1 | S0 principal | 0,400 | −12,0 | [−53,1; +29,0] | 0,57 | 53 / 41 |
| D1 ciclo 1 | A local constante | 0,300 | +13,1 | [−8,4; +34,6] | 0,23 | 61 / 53 |
| D1 ciclo 1 | A local constante | 0,400 | −1,5 | [−24,1; +21,1] | 0,90 | 53 / 41 |
| D1 ciclo 1 | B cortes empilhados | 0,300+0,400 | −8,0 | [−38,1; +22,0] | 0,60 | 114 / 94 |
| D1 ciclo 1 | C1 | 0,300 | +28,5 | [−4,7; +61,7] | 0,09 | 61 / 53 |
| D1 ciclo 1 | C1 | 0,400 | −12,2 | [−52,6; +28,2] | 0,55 | 53 / 41 |
| D1 ciclo 1 | C2 | 0,300 | +28,6 | [−4,4; +61,6] | 0,09 | 61 / 53 |
| D1 ciclo 1 | C2 | 0,400 | −11,5 | [−51,3; +28,3] | 0,57 | 53 / 41 |
| D1 ciclo 1 | D local randomization | 0,300 (±0,020) | +2,9 | [−30,0; +37,5] | 1,00 | 20 / 19 |
| D1 ciclo 1 | D local randomization | 0,400 (±0,007) | −3,3 | [−51,7; +48,4] | 1,00 | 10 / 9 |
| D2 ciclo 2 | S0 principal | 0,300 | −15,2 | [−51,6; +21,1] | 0,41 | 82 / 61 |
| D2 ciclo 2 | S0 principal | 0,400 | +11,5 | [−13,9; +36,9] | 0,38 | 53 / 53 |
| D2 ciclo 2 | A local constante | 0,300 | +4,0 | [−15,2; +23,3] | 0,68 | 82 / 61 |
| D2 ciclo 2 | A local constante | 0,400 | +12,7 | [−2,7; +28,0] | 0,11 | 53 / 53 |
| D2 ciclo 2 | B cortes empilhados | 0,300+0,400 | −3,0 | [−25,7; +19,8] | 0,80 | 135 / 114 |
| D2 ciclo 2 | C1 | 0,300 | +1,9 | [−27,0; +30,8] | 0,90 | 82 / 61 |
| D2 ciclo 2 | C1 | 0,400 | +11,8 | [−12,7; +36,2] | 0,34 | 53 / 53 |
| D2 ciclo 2 | C2 | 0,300 | +1,8 | [−27,2; +30,9] | 0,90 | 82 / 61 |
| D2 ciclo 2 | C2 | 0,400 | +10,6 | [−12,7; +33,9] | 0,37 | 53 / 53 |
| D2 ciclo 2 | D local randomization | 0,300 | sem janela | — | — | — |
| D2 ciclo 2 | D local randomization | 0,400 (±0,006) | +5,2 | [−25,0; +40,6] | 1,00 | 7 / 11 |
| D1 + D2 | F1 ciclos empilhados | 0,300 | −10,6 | [−41,4; +20,3] | 0,50 | 100 / 80 (257 linhas) |
| D1 + D2 | F1 ciclos empilhados | 0,400 | +0,3 | [−24,5; +25,2] | 0,98 | 69 / 71 (200 linhas) |
| D1 + D2 | F2 ciclos e cortes empilhados | 0,300+0,400 | −5,2 | [−25,0; +14,7] | 0,61 | 169 / 151 (457 linhas) |

- **Ciclo 2, corte 0,300, sem janela de local randomization.** A menor janela
  viável (±0,002, 3 contra 3 municípios) reprovou no balanço de população
  (p = 0,10). Pela regra fixada, não há janela, e o resultado fica assim.
- **F1 e F2.** O mesmo município pode estar nos ciclos 1 e 2; por isso o EP é
  agrupado por município.
- **Leitura.** Nenhum salto de presença é distinguível de zero a 5%. O mais
  próximo é D1 em 0,300 com covariáveis (+28,5 p.p., p = 0,09), que tem sinal
  oposto ao principal (−3,2). Isso é sintoma de baixa precisão e de
  sensibilidade à especificação, não evidência de efeito.

## 3. O que os dados permitem descartar (Y1)

Limite superior unilateral de 95% (τ̂ + 1,645 EP; em D, por inversão do teste
unilateral de permutação), p unilateral de H0: τ ≥ Δ e p do TOST
(equivalência em [−Δ, +Δ]). Em negrito, p < 0,05.

| Especificação | Corte | Limite sup. 95% | p(τ ≥ +10) | p(τ ≥ +15) | p(τ ≥ +20) | TOST ±10 | TOST ±15 | TOST ±20 |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| S0 principal | 0,300 | +14,5 | 0,085 | **0,047** | **0,024** | 0,568 | 0,448 | 0,334 |
| S0 principal | 0,400 | +21,2 | 0,172 | 0,104 | 0,058 | 0,381 | 0,269 | 0,177 |
| A local constante | 0,300 | +17,7 | 0,263 | 0,098 | **0,026** | 0,263 | 0,098 | **0,026** |
| A local constante | 0,400 | +12,8 | 0,094 | **0,028** | **0,006** | 0,138 | **0,045** | **0,011** |
| B cortes empilhados | 0,300+0,400 | +10,3 | 0,053 | **0,020** | **0,007** | 0,453 | 0,290 | 0,162 |
| C1 | 0,300 | +17,8 | 0,149 | 0,076 | **0,035** | 0,307 | 0,186 | 0,100 |
| C1 | 0,400 | +23,8 | 0,271 | 0,162 | 0,087 | 0,271 | 0,162 | 0,087 |
| C2 | 0,300 | +17,0 | 0,136 | 0,068 | **0,030** | 0,322 | 0,197 | 0,107 |
| C2 | 0,400 | +24,2 | 0,282 | 0,171 | 0,092 | 0,282 | 0,171 | 0,092 |
| D local randomization | 0,300 | +14,7 | 0,107 | **0,048** | **0,019** | 0,316 | 0,176 | 0,088 |
| D local randomization | 0,400 | +32,0 | 0,333 | 0,240 | 0,159 | 0,333 | 0,240 | 0,159 |
| E0 | 0,300 | +11,6 | 0,064 | **0,028** | **0,010** | 0,478 | 0,327 | 0,199 |
| E0 | 0,400 | +21,8 | 0,214 | 0,124 | 0,065 | 0,257 | 0,155 | 0,084 |
| E1 | 0,300 | +11,3 | 0,062 | **0,026** | **0,010** | 0,478 | 0,325 | 0,197 |
| E1 | 0,400 | +21,5 | 0,211 | 0,121 | 0,062 | 0,254 | 0,152 | 0,082 |
| E2 | 0,300 | +23,2 | 0,288 | 0,166 | 0,084 | 0,288 | 0,166 | 0,084 |
| E2 | 0,400 | +11,5 | 0,063 | **0,028** | **0,011** | 0,503 | 0,355 | 0,226 |

- **Principal.** Em 0,300, saltos de +15 p.p. ou mais são incompatíveis com
  os dados a 5% unilateral (p = 0,047, no limite), e os de +20 p.p. também
  (p = 0,024). Em 0,400, o limite superior é +21,2 p.p., e nenhuma das
  margens de +10, +15 e +20 p.p. é descartada (p = 0,058 para +20).
- **+10 p.p.** Nenhuma especificação descarta. As mais próximas são B
  (p = 0,053) e E1 em 0,300 (p = 0,062).
- **+20 p.p.** Em 0,300, sete das oito especificações por corte descartam
  (todas menos E2). Em 0,400, só A e E2. Empilhando os cortes (B), +15 p.p.
  ficam descartados: limite superior de +10,3 p.p. para a média dos dois
  saltos.
- **Equivalência.** Só A passa no TOST, e A ignora as inclinações (seção 2.1).
  Fora de A, nenhuma especificação mostra que o salto está dentro de ±20 p.p.
- **Presença.** O principal descarta +20 p.p. só para D2 em 0,300
  (p = 0,029). F2, com ciclos e cortes empilhados, descarta +15 p.p.
  (limite superior de +11,5 p.p.).

## 4. Dá para estreitar o IC?

Pouco, e sempre a um custo:

| Alavanca | EP de Y1 em 0,300 (principal: 0,166) | Custo |
|---|---:|---|
| covariáveis pré (C1, C2) | 0,129; 0,128 | estimativa pontual muda (−12,8 → −3,5); as covariáveis predizem Y1 e diferem um pouco entre os lados |
| células com EP por município (E1) | 0,126 | estimando por célula, não por município |
| células + efeitos fixos de curso (E2) | 0,122 | idem, e a estimativa muda (−9,3 → +3,2) |
| cortes empilhados (B) | 0,115 | estimando vira a média dos dois saltos |
| local randomization (D, ±0,020) | 0,112 (DP de permutação) | premissa de sorteio na janela e de Y1 sem relação com o IVS; 39 municípios |
| local constante (A) | 0,076 | viés da inclinação fora do IC; não serve |

Nenhuma alternativa válida chega a MDE abaixo de 31 p.p. A janela larga do E3
(h = 0,080) tem EP de 0,124 e 0,129
([`E3_estimativas.csv`](../../output/rdd_bolsa/E3_estimativas.csv)), com mais
viés de suavização. A inferência robusta com correção de viés (Calonico,
Cattaneo e Titiunik, 2014) alargaria o IC, não o estreitaria.

**Cenário ilustrativo, não observação** (`cenarios_ilustrativos_rotulados` em
`E5_resumo.json`). Supõe o mesmo desvio-padrão e o mesmo desenho, e só
muda o n:

| Cenário | n abaixo / acima em 0,300 | MDE |
|---|---:|---:|
| observado | 61 / 53 | 46,6 p.p. |
| preenchimento dos ciclos 1 e 2 juntos, sem correlação entre ciclos (otimista) | 143 / 114 | 31,2 p.p. |
| todos os municípios do Brasil na janela | 859 / 654 | 12,9 p.p. |
| n necessário para MDE de 10 p.p. | 1.325 / 1.151 | 10 p.p. |

Para detectar 10 p.p. seria preciso cerca de 22 vezes o n atual, mais do que
todos os municípios do país na janela. Em 0,400, os números são parecidos
(MDE de 12,5 p.p. com o Brasil inteiro). Com este outcome, nenhuma RDD nestes
cortes detecta efeitos de ~10 p.p. No máximo, descarta efeitos grandes.

## 5. Controle sintético e outros desenhos

| Desenho | O que exige | Situação aqui | Avaliação |
|---|---|---|---|
| Controle sintético (Abadie, Diamond e Hainmueller, 2010); DiD sintético (Arkhangelsky et al., 2021) | poucas unidades tratadas; série pré-tratamento longa do mesmo outcome; doadores sem interferência | o preenchimento de vagas do PMM-E não existe antes do programa; centenas de municípios em cada faixa; os doadores disputam os mesmos candidatos | **não se aplica** |
| DiD / estudo de evento por faixa | pré-período do outcome e tendências paralelas | sem pré-período do preenchimento nem da presença PMM-E; as faixas diferem muito em vulnerabilidade, e tendências paralelas não são verificáveis sem pré-período | **não se aplica** ao outcome da hipótese |
| Diferença em descontinuidades (Grembi, Nannicini e Troiano, 2016) com oferta CNES | outcome observado antes e depois, nos mesmos cortes | o estoque CNES existe antes; removeria descontinuidades fixas de outras políticas com os mesmos cortes, como as categorias do PMMB, e a diferença no tempo pode reduzir variância | **candidato**, mas muda o outcome (oferta cadastrada ≠ preenchimento ≠ retenção) e exige protocolo próprio congelado antes de olhar dados; fora da fila autorizada |
| RD com múltiplos cortes e extrapolação (Cattaneo, Keele, Titiunik e Vazquez-Bare, 2021) | grupos expostos a cortes diferentes na mesma running variable, com diferença constante entre as funções de regressão | todos os municípios enfrentam os mesmos dois cortes cumulativos; não há segundo grupo para ancorar a extrapolação | **não se aplica**; o que cabe é o empilhamento (B), que muda o estimando |
| RD geográfica (Keele e Titiunik, 2015) | fronteira que atribui o tratamento | a bolsa segue o IVS municipal, não uma fronteira; vizinhos em faixas diferentes disputam os mesmos candidatos | **não se aplica** como RD; comparar vizinhos mediria deslocamento entre municípios, outro estimando |
| Mais ciclos | outcome comparável em mais coortes | ciclo 2: preenchimento ainda não reconciliado (decisão D2 do [`38`](38_estado_e_pendencias_rdd_bolsa.md)); ciclo 3: congelado até a maturidade pelo `CLAUDE.md` | ciclos 1 e 2 juntos dariam MDE de ~31 p.p. no cenário otimista; não muda a conclusão |

## 6. O que podemos e não podemos afirmar

**Podemos:**
- **Nenhuma estimativa distinguível de zero.** Nenhuma das especificações
  para Y1 dá p < 0,05: o menor p é 0,44, e na sensibilidade de janelas da
  local randomization, 0,40. A leitura inconclusiva do E3 se mantém em todas
  as especificações.
- **Saltos positivos grandes descartados em 0,300.** No principal, os dados são
  incompatíveis, a 5% unilateral, com saltos de +20 p.p. ou mais no
  preenchimento, e no limite com +15 p.p. Empilhando os cortes, saltos médios
  de +15 p.p. ou mais ficam descartados.
- **Origem da largura do IC.** O IC é largo pelo ruído de um outcome com
  poucas células, por ~57 municípios por lado e pela extrapolação do local
  linear (× 2,2 a × 2,6 sobre a diferença de médias). Não é defeito de
  especificação.

**Não podemos:**
- **Afirmar ausência de efeito.** Nenhuma especificação válida mostra que o
  salto está em ±20 p.p., e nenhuma descarta +10 p.p. **Inconclusivo não é
  ausência de efeito.**
- **Usar A.** O IC estreito de A não é inferência válida para o salto.
- **Promover uma alternativa a principal.** As alternativas mudam o estimando
  ou a premissa, e a estimativa pontual oscila entre −12,8 e +3,2 p.p. em
  0,300 (sem contar A). Essa oscilação é sintoma de baixa precisão, não
  informação sobre o sinal.
- **Ler o descarte em 0,400.** Nesse corte o principal não descarta nada a
  partir de +10 p.p., e o desequilíbrio de covariáveis do E3 limita ainda mais
  a leitura.
- **Usar linguagem causal.** Tudo aqui é exploratório e pós-resultado.

## 7. Verificações e limites

**Verificações** (`verificacoes` em `E5_resumo.json`):
- S0 reproduz o E3 nas seis linhas principais. A diferença máxima é de
  1,4 × 10⁻¹¹, porque o CSV do E4 grava Y1 com 10 casas.
- Y1 do E4 coincide com o outcome do E3 nos 368 municípios (diferença
  máxima de 4,4 × 10⁻¹¹).
- As 1.295 células reproduzem Y1.
- Duas execuções dão saídas com o mesmo SHA-256.

**Limites:**
- **Pós-resultado.** Todas as especificações foram desenhadas depois de ver o
  E3. A lista foi fixada antes de rodar, mas a escolha de **quais**
  alternativas testar já sabia que o principal era inconclusivo.
- **Seleção da janela.** O critério de balanço com p mínimo ≥ 0,15 em quatro
  covariáveis é conservador. Com 2 a 5 municípios por lado, o teste quase não
  tem poder, e uma única janela minúscula reprovada elimina o corte (ciclo 2,
  0,300).
- **Efeito constante.** A inversão do teste de Fisher supõe efeito aditivo
  constante. Com outcome binário (presença), as menores janelas dão ICs
  degenerados ou na borda da grade; estão na sensibilidade, marcados em
  `ic_toca_borda_da_grade`.
- **Inferência pela normal.** Com 94 a 114 municípios e até 13 parâmetros
  (C2), os ICs normais podem ser um pouco curtos.

## 8. Reprodução

```bash
python3 scripts/rdd_bolsa/11_inferencia_alternativa.py   # ~30 s
python3 -m unittest tests/test_e5_inferencia_sintetico.py
```

Entradas, com SHA-256 em `E5_resumo.json`:
- `output/rdd_bolsa/escore_completo_ivs2010_oficial.csv`;
- quadros do ciclo 1 e do ciclo 2 em `data/raw`;
- `output/aquisicao/a08_ivs_2010_oficial_municipio.csv`;
- `output/tema_trabalho/matriz_tipologia_territorial.parquet` (só o estrato);
- `output/rdd_bolsa/E4_proporcao_municipio.csv`;
- `output/tema_trabalho/matriz_funil_ciclo1.parquet`;
- `output/aquisicao/quadro_vagas_tratamento.parquet`;
- a relação nominal de ativos de 09/10/2026, com o SHA-256 fixado no
  protocolo;
- `output/rdd_bolsa/E3_estimativas.csv`, para conferir S0.
