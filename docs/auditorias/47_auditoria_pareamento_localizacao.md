# 47. Auditoria do adendo 48h: H1 pareada pela localização da unidade (UF e capital) e dos médicos (raio de 100 km)

> **Data:** 27/10/2026.<br>
> **Objeto:** adendo [`48h`](../06_execucao/48h_adendo_pareamento_localizacao_unidade_e_medicos.md) (congelado em
> `243160d`), script `scripts/rdd_bolsa/49_pareamento_localizacao.py`, saídas `output/rdd_bolsa/PL_*`, doc
> [`57w`](../06_execucao/57w_resultados_pareamento_localizacao.md) (25 decisões da seção 0, versionadas em `f5fbebf`)
> e `tests/test_pareamento_localizacao.py`. Base: branch `claude/vigilant-mccarthy-dd92mc`, commit `1679a35`.<br>
> **Referências:** adendos [48d](../06_execucao/48d_adendo_controles_localizacao_e_medicos.md) e
> [48e](../06_execucao/48e_adendo_pareamento_regra_literal_e_0400.md), docs
> [57r](../06_execucao/57r_resultados_controles_localizacao_medicos.md) e
> [57s](../06_execucao/57s_resultados_pareamento_regra_literal.md), auditorias
> [40](40_auditoria_controles_localizacao_medicos.md) e [43](43_auditoria_pareamento_regra_literal.md), scripts 17, 44
> e 45 e a `rdd_lib`.<br>
> **Método:** recálculo próprio, em memória e no scratch, sem importar os scripts 17, 44, 45 e 49 nem a `rdd_lib`.
> Escrevi do zero:
>
> - a leitura das entradas: a08, população de 2022, capitais do IBGE, CIR do TabNet, painel a09 e ponte do manifesto,
>   centroides do IBGE, células do quadro e X1;
> - a montagem das unidades município × ciclo da H1;
> - o raio de 50, 100 e 200 km;
> - a regra 2, o logit (Newton), o suporte, o *caliper*, o exato e a regra literal;
> - a permutação de sinais com inversão, o t pareado e o p exato por enumeração;
> - o balanço, o Holm e o BKY;
> - a RDD empilhada com CR1;
> - a reconstrução do pseudônimo da X1, com CRM e nome descartados na leitura.
>
> Duas leituras vêm de fora do código da execução. O tipo de vaga do ciclo 2 no quadro de 13/02/2026 vem de
> `output/auditoria_H1/a36_celulas.csv` (auditoria 36). Os alocados da 1ª chamada vêm de `outcomes_V_celula.parquet`,
> que bate célula a célula com a reconstrução da auditoria 36 (0 diferenças).

## Veredito

**Aprovado com correções de texto.** Recalculei todas as linhas de `PL_estimativas.csv` com código próprio, e todas
batem com as gravadas:

- PH-1, PH-2, PH-3 e PH-5: estimativa, p, IC de permutação e IC t com diferença ≤ 1e−10;
- PH-4: diferença ≤ 5e−13;
- os pares, o *caliper*, quem saiu pela regra 2 e o balanço são idênticos.

O portão reproduz: refiz o PM-1 do 48e nos dois cortes com o mesmo código e obtive os mesmos 92 e 70 pares. O hash dos
centroides confere. As decisões da seção 0 seguem o adendo.

O texto do 57w, porém, não mostrava quão pouco poder os 25 e 29 pares têm, e atribuía a falta de pares só à UF. Também
lia a PH-5 em 0,400 de forma mais forte do que o dado permite. Corrigi esses pontos nos blocos gerados pelo script e
no limite dos cursos fora da ponte. Nenhum número mudou: a reexecução completa do 49 deu `PL_*` idênticos byte a byte
(figuras incluídas).

## Achados, por gravidade

Não há achado grave.

### Médios (corrigidos no texto)

**A1. O texto não dizia quanto a comparação consegue detectar.** O 57w dizia que "não detectar com tão poucos pares é
um resultado fraco", mas não dava a escala. Calculei a diferença mínima detectável pelo t pareado, com 80% de poder
e teste bicaudal a 5%:

| Corte | Outcome | Pares | EP | Diferença mínima detectável | Lado de baixo nos pares | Ponto |
|---|---|---|---|---|---|---|
| 0,300 | fração preenchida | 25 | 9,9 p.p. | 29 p.p. | 36% | +16,4 p.p. |
| 0,300 | alocados por vaga imediata | 25 | 0,10 | 0,29 | 0,34 | +0,13 |
| 0,400 | fração preenchida | 29 | 8,3 p.p. | 24 p.p. | 69% | −6,0 p.p. |
| 0,400 | alocados por vaga imediata | 29 | 0,11 | 0,32 | 0,71 | −0,08 |

No 48e, com 92 e 70 pares, a diferença mínima era 16 e 22 p.p. na fração preenchida. Em 0,300, só uma diferença de
cerca de 80% do nível do lado de baixo teria boa chance de aparecer. O "não se detecta" do 48h diz, portanto, muito
pouco.

O texto gerado ("O preço") passou a dar:

- a diferença mínima nos dois cortes;
- a comparação com o ponto;
- a observação de que o ponto não é tamanho de efeito.

**A2. A falta de pares vinha atribuída só à UF; o que mais corta é o *caliper*.** No PH-1, o logit tem pouca variação
(DP do logit 0,23 em 0,300 e 0,70 em 0,400). O *caliper* do 48e, de 0,2 DP, fica então em 0,047 e 0,141. Contei os
pares possíveis, sem olhar outcome:

| Linha | Corte | Sem *caliper* (máx. por estrato) | Com 1,0 DP | Com 0,5 DP | Com 0,2 DP (adendo) | Regra literal |
|---|---|---|---|---|---|---|
| PH-1 (UF, capital, ciclo) | 0,300 | 64 | 56 | 41 | 25 | 25 |
| PH-1 | 0,400 | 61 | 54 | 41 | 29 | 29 |
| PH-3 (CIR, capital, ciclo) | 0,300 | 11 | 8 | 4 | 2 | 2 |
| PH-3 | 0,400 | 18 | 12 | 5 | 1 | 1 |

A regra literal chega ao máximo possível com o *caliper* (emparelhamento bipartido máximo). Dentro da UF caberiam
64 e 61 pares; o *caliper* derruba para 25 e 29. O *caliper* é o que o adendo fixa, então não há desvio. Só a
explicação estava incompleta. O texto passou a dizer que o *caliper* é o que mais corta e a dar os máximos sem ele
(calculados pelo script a partir do escore gravado). Na PH-3, a frase "raramente há municípios da mesma região de
saúde" virou "na mesma região de saúde e dentro do *caliper* quase não sobra par". Não estimei nada com outro
*caliper*: seria escolher especificação depois de ver o resultado.

**A3. A PH-5 em 0,400 estava lida como ausência de indício.** A resposta curta dizia "Não há indício de que o lado
de bolsa maior atraia mais médicos de outra UF". O código aplica a regra do §3 corretamente: o IC de permutação contém
o zero (`SEM_INDICIO_DE_ATRAIR_DE_LONGE`). O dado, porém, é este:

- dos 24 pares, 19 têm diferença zero;
- os 5 pares com diferença vão todos para o lado de bolsa maior;
- com 5 pares, o menor p bicaudal possível no teste de sinais é 2/2⁵ = 0,0625;
- p exato = 0,0625 e p Monte Carlo = 0,064: é o padrão mais extremo que 5 pares permitem, e ainda assim fica acima
  de 5%;
- o limite inferior do IC, mostrado como "0,00", é −5,2e−11, ou seja, o próprio zero (o teste não rejeita o zero
  por pouco).

O resultado é inconclusivo por falta de pares informativos, não evidência de que nada aconteça. A resposta curta
passou a dizer "pela regra do §3 não há indício", acrescida de uma frase gerada que descreve esse padrão. A mesma frase
entrou no item da interpretação, que também deixou de usar "traga" ("receba mais médicos"). A tabela de pares com
diferença já mostrava o menor p possível ("0,062", arredondado de 0,0625).

### Menores

**A4. Ciclos desequilibrados: os pares do PH-1 são quase todos dos ciclos 1 e 2.**

| | 48e (PM-1) 0,300 | 48h (PH-1) 0,300 | 48e 0,400 | 48h 0,400 |
|---|---|---|---|---|
| Pares, ciclos 1 / 2 / 3 | 20 / 39 / 33 | 6 / 15 / 4 | 22 / 24 / 24 | 9 / 15 / 5 |
| Amostra do pareamento, ciclos 1 / 2 / 3 | 61 / 101 / 92 | 55 / 90 / 68 | 60 / 77 / 74 | 56 / 74 / 55 |

Parte da perda no ciclo 3 vem dos 61 municípios cujas vagas imediatas são só de cursos 17 a 20 (fora da ponte). Eles
ficam sem raio. Na janela, a perda pesa mais do lado de bolsa maior:

| Corte | Sem raio no ciclo 3 só por curso fora da ponte (abaixo / acima) | Unidades do ciclo 3 na janela (abaixo / acima) |
|---|---|---|
| 0,300 | 5 / 9 | 50 / 43 |
| 0,400 | 7 / 9 | 48 / 35 |

Fora do ciclo 3, a saída por raio ausente é só de municípios sem vizinho a 100 km: 2 em 0,300 e 4 em 0,400, todos do
lado de cima.

A saída é por covariável pré-tratamento e é contada, portanto não é imputação nem seleção pelo outcome. Ela muda, porém,
a população: o PH-1 fala sobretudo do ciclo 2. O texto "O preço" passou a dar os pares por ciclo. O limite "Cursos fora
da ponte" passou a dizer que essas unidades saem do pareamento e remete a esta auditoria para a contagem por lado.

**A5. O ponto de +16,4 p.p. em 0,300.** É o maior ponto das versões pareadas (48d −0,6; 48e +4,7). Tem sinal oposto
ao da RDD do 48b em 0,300 (HI-1 −3,7 p.p.; HI-2 −1,13). Vem de 16 pares com diferença: 12 a favor do lado de cima e
4 contra, p exato 0,112. Só 1 dos 25 pares coincide com os 92 do 48e (em 0,400, 1 de 29 com os 70). As versões de
0,300 com 50 e 200 km também ficam positivas (+13,7 e +7,8 p.p.), dentro dos mesmos intervalos.

Com uma diferença mínima detectável de 29 p.p., o ponto é compatível com ruído. O texto agora diz que ele fica abaixo
da diferença mínima, que vem de outro conjunto de pares e que não é tamanho de efeito. Não acrescentei leitura por
ciclo nem por UF: seria procurar padrão depois do resultado.

### Observações (sem correção)

- **Decisão 10 (o lado que procura é contado por ciclo, não por estrato exato).** O adendo diz "o lado com menos
  unidades procura par" e "exato no ciclo". Contar por ciclo segue a letra do 48e. Testei a outra leitura, com o lado
  contado em cada estrato UF × capital × ciclo:
  - em 0,300 mudam 3 dos 25 pares (+17,7 p.p. [−2,2; +37,6] e +0,16 [−0,04; +0,35]);
  - em 0,400 mudam 2 dos 29 pares (pontos iguais aos gravados, IC [−23,3; +11,3] e [−0,30; +0,15]);
  - todos os IC contêm zero; a leitura não muda.
- **PH-4: o que move a HI-2 em 0,300 é o efeito fixo de UF, não o raio.** Na mesma amostra:
  - sem controle: −1,15 [−2,21; −0,08];
  - só o raio: −1,19 [−2,24; −0,13];
  - só a UF: −0,55 [−1,61; +0,50];
  - os dois: −0,62 [−1,67; +0,43].

  O texto ("o que muda é o controle, não a amostra") está certo; o detalhe fica registrado aqui. Com EF de UF, a RDD
  compara municípios da mesma UF dos dois lados do corte, e o salto passa a vir só de UFs com municípios dos dois
  lados.
- **Classificação da PH-5 pelo limite do IC.** O código decide pelo sinal de `ic95_inf`, e em 0,400 esse limite é
  −5e−11. O veredito está certo em substância, porque p(0) = 0,064 > 0,05 e o zero está na região de aceitação. Uma
  regra futura deveria decidir por p(0), não pelo extremo do intervalo.
- **AM de um lado só depois da regra 2 em 0,400.** Com a saída de Manaus (capital de um lado só), as demais unidades
  do AM ficam todas de um lado. Pela passada única (decisão 3 do 57s) elas ficam na amostra e, pelo exato, não formam
  par. Está relatado na seção 2 do 57w e não afeta pares.
- **Raio por centroides.** O raio de 50 km deixa 337 municípios sem vizinho, e a PH-2 com 50 km perde 42 a 46 unidades
  por covariável ausente. Está na seção 1.2 e não há o que corrigir.

## Fidelidade ao adendo e às decisões

| Ponto | Conferência |
|---|---|
| Raio de 100 km | Círculo máximo com R = 6.371,0088 km entre centroides da malha 2022. Vizinhos = municípios do a08 a ≤ 100 km, sem o próprio. Taxa = Σ média 2024-06 a 2025-06 das CBO do curso nos vizinhos ÷ Σ população 2022 dos vizinhos × 10 mil. Ausente sem vizinho ou com vizinho sem média ou sem população. Meus contadores (municípios sem vizinho 337 / 49 / 4; vizinhos p10, mediana e p90; taxa ausente) são idênticos aos da seção 1.2 |
| Média ponderada por vagas imediatas | Peso = vagas imediatas das células com vaga imediata (ciclo 2 pelo quadro de 13/02), só cursos 1 a 16. Ausentes por ciclo: 2 / 9 / 69 (100 km), iguais ao gravado. Médias de raio por lado no balanço iguais a ≤ 4e−15 |
| 61 municípios do ciclo 3 sem raio | Conferido: 106 municípios do ciclo 3 têm célula de curso 17 a 20 e 61 só têm esses cursos. Efeito nos ciclos: A4 |
| Regra 2 na UF e em capital | Categorias: capital, não capital e cada UF; três ciclos juntos; uma passada; depois da saída por covariável ausente. Minha lista é idêntica a `PL_excluidos.csv` nas 6 combinações (PH-1 e PH-2, dois cortes): 29, 24, 29, 23, 21 e 25 linhas. Maior fração que saiu: 23 de 124 abaixo em 0,400 (18,5%, que o 57w arredonda para 19%). Nenhuma passa de 25% |
| Exato + regra literal | Candidatas: mesmo ciclo, os dois no suporte, \|Δ logit\| ≤ 0,2 DP, mesma UF (ou CIR) e mesma condição de capital. O lado com menos unidades no ciclo procura, em ordem decrescente do escore, e fica com a candidata livre mais próxima. Pares idênticos nas 8 combinações |
| Escore | Constante, log(pop), médicos, especialistas CBO-alvo do município e raio; sem UF, capital e região. *Caliper* igual ao gravado a 1e−6 em todas as linhas |
| Holm e BKY | Holm nas 4 linhas do PH-1 (0,434; 0,579; 0,988; 0,988), diferença 0. BKY nas 16 de PH-2, PH-3 e PH-5, com p = 1 nas duas sem estimativa: q = 1 em todas, diferença 0. Só com as executadas, também q = 1 (menor p 0,064) |
| Leitura do §3 | `NAO_SE_DETECTA_DIFERENCA` (4 IC com zero, maior \|DP\| depois 0,09); nenhuma rejeita depois do Holm; regra 2 ≤ 25%; PH-5 `SEM_INDICIO` nos dois cortes (A3) |
| Origem só como outcome | X1 fora do escore, do exato e da amostra; PH-5 usa os pares da PH-1 |

**Ordem no Git:**

1. adendo `243160d`, às 03:04;
2. decisões `f5fbebf`, às 03:13;
3. execução `eec3290`, às 03:27.

A seção 0 do 57w é idêntica entre `f5fbebf` e `1679a35`. O SHA-256 do adendo (`a2d34233…`) é o gravado no script e
no resumo.

## Portão

- **PM-1 do 48e:** o script o refaz em 0,300 com diferença 9,7e−17 e os mesmos 92 pares. Refiz com meu código nos
  dois cortes (macrorregião e resto da região de saúde no escore, regra 2 na macrorregião) e obtive:
  - 0,300: 92 pares, +0,046977 e +0,101888;
  - 0,400: 70 pares, +0,054558 e +0,071366, com as mesmas 19 linhas fora pela regra 2;
  - diferença ≤ 1e−10.
- **Centroides:** SHA-256 `2ce2914973e5b464…` do arquivo, igual ao do manifesto do 17 e ao de
  `X1_ligacao_resumo.json`. São 5.570 municípios, e todos os 5.565 do a08 têm centroide.

## O que foi recalculado

Valores do meu recálculo; a coluna "máx. dif." compara com `PL_estimativas.csv` (estimativa, p, IC de permutação e IC t).

| Linha | Corte | Outcome | Pares | Diferença média [IC permutação] | p (MC / exato) | Máx. dif. |
|---|---|---|---|---|---|---|
| PH-1 | 0,300 | fração preenchida | 25 | +0,1639 [−0,0380; +0,3665] | 0,108 / 0,112 | 4e−11 |
| PH-1 | 0,300 | alocados por vaga imediata | 25 | +0,1320 [−0,0734; +0,3347] | 0,193 / 0,201 | 5e−11 |
| PH-1 | 0,400 | fração preenchida | 29 | −0,0603 [−0,2321; +0,1146] | 0,494 / 0,483 | 7e−11 |
| PH-1 | 0,400 | alocados por vaga imediata | 29 | −0,0767 [−0,3000; +0,1475] | 0,511 / 0,505 | 4e−11 |
| PH-2 50 km | 0,300 / 0,400 | fração; alocados | 29 / 21 | +0,1371; +0,1913 / −0,0666; −0,0372 | — | ≤ 1e−10 |
| PH-2 200 km | 0,300 / 0,400 | fração; alocados | 31 / 26 | +0,0780; +0,1583 / −0,0499; −0,0074 | — | ≤ 9e−11 |
| PH-3 | 0,300 / 0,400 | fração; alocados | 2 / 1 | +0,25; +0,125 (IC não limitado) / sem estimativa | 1 | 4e−16 |
| PH-5 mesma UF | 0,300 / 0,400 | por vaga imediata | 21 / 24 | +0,0626 / +0,0619 | 0,505 / 0,614 | ≤ 1e−10 |
| PH-5 outra UF | 0,300 / 0,400 | por vaga imediata | 21 / 24 | +0,0212 [−0,0083; +0,0640] / +0,1591 [0; +0,3472] | 0,754 / 0,064 (exato 0,0625) | ≤ 1e−10 |

Também recalculei:

- **Regra 2:** a lista de quem saiu é igual nas 6 combinações. No PH-1:
  - em 0,300 saíram AC, RR, PA, AP, MA, PE, SE, ES, PR e DF, todas de um lado só (19 abaixo, 10 acima);
  - em 0,400 saíram as capitais (10 abaixo) e AP, SE, RJ, PR, MS, MT e GO (23 abaixo, 0 acima).
- **Raio de 100 km por município:** contagens e médias por lado batem com o gravado. Alguns valores do curso 1 (CBO
  225151), para ilustrar:

  | Município | Vizinhos a ≤ 100 km | Taxa do curso 1 (por 10 mil hab.) |
  |---|---|---|
  | São Paulo | 90 | 3,80 |
  | Recife | 80 | 2,08 |
  | Salvador | 54 | 1,84 |
  | Belém | 27 | 0,94 |
  | Manaus | 2 | 0,23 |

- **Balanço PH-6:** médias, DP antes e DP depois de todas as variáveis, nas 8 combinações, com diferença ≤ 4e−15.
  Maior |DP| depois no PH-1: 0,090 (0,300) e 0,094 (0,400).
- **PH-4:** RDD empilhada própria, com interceptos e inclinações por ciclo × lado e τ comum. A HI-1 usa EF de curso ×
  ciclo e o raio do curso da célula. A HI-2 usa o controle das vagas imediatas centrado por ciclo. As duas têm EF de UF
  e CR1 por município.

  | Linha | Corte | Com UF e raio (gravado) | Sem controle |
  |---|---|---|---|
  | HI-1 | 0,300 | +5,44 p.p. [−10,95; +21,84] | −0,40 |
  | HI-2 | 0,300 | −0,620 [−1,671; +0,432] | −1,145 [−2,210; −0,081] |
  | HI-1 | 0,400 | −4,24 [−21,09; +12,62] | +1,83 |
  | HI-2 | 0,400 | −0,080 [−0,684; +0,523] | +0,024 |

  Os n por lado são iguais aos gravados, com diferença ≤ 5e−13. A HI-2 do 48b na amostra toda dá −1,126
  [−2,154; −0,099], igual ao `HI_estimativas.csv`.
- **PH-5:**
  - a reconstrução do pseudônimo bate com a X1 (0 divergências de ciclo, município e lista);
  - 1.460 registros: 637 em células com vaga imediata (508 da mesma UF, 78 de outra UF, 51 de origem desconhecida),
    639 só em células de cadastro reserva e 184 sem célula;
  - as médias por lado e as contagens de sinais (3 pares com diferença em 0,300, 2 a favor do lado de cima e 1
    contra; 5 em 0,400, todos a favor do lado de cima) são iguais às gravadas.

## Integridade

| Item | Conferência |
|---|---|
| IVS errado | Rodei o 49 sob um *audit hook* de `open`. Nenhum arquivo `ivs_ipea_2010_municipios` foi aberto; o IVS vem do a08 |
| CNES | O painel a09 vai até 202608; o script filtra 202406–202506 e falha se houver competência ≥ 202609 |
| `EMPIRICO` | Em todas as linhas de `PL_estimativas`, `PL_balanco` e `PL_excluidos` e no resumo; estatuto `ADENDO_48H_POS_RESULTADO` |
| Nada imputado | Raio, covariáveis e outcome ausentes ficam ausentes e são contados; o ciclo 3 fica sem PH-5 |
| `HI_*`, `CL_*`, `PM_*`, `PO_*`, `X1_*` | 27 arquivos com SHA-256 igual antes e depois de duas execuções; o commit `eec3290` não toca neles |
| Escrita | Só `output/rdd_bolsa/PL_*` (e o 57w com `--atualizar-doc`); nada em `data/`. CRM e nome das listas só em memória |
| Determinismo | Duas execuções completas (a do original e a depois das correções de texto) deram os 7 arquivos `PL_*` idênticos byte a byte; `--atualizar-doc` deixa o 57w igual ao gravado |

## Texto do 57w

- **Linguagem.** Os blocos têm linguagem simples e falam do "pacote do corte", sem leitura causal. Havia duas formas
  verbais com sabor causal sobre a PH-5 ("atraia", "traga"); passaram a "receba mais médicos de outra UF". O código do
  §3 (`INDICIO_ATRAI_DE_LONGE`) segue o nome do adendo e não foi mudado.
- **Números.** Fora dos blocos gerados, o teste continua sem achar número além dos parâmetros. Os números novos (diferença
  mínima, pares possíveis sem *caliper*, pares por ciclo e em comum com o 48e, menor p da PH-5) são calculados pelo
  script a partir das saídas gravadas.
- **Cabeçalho.** O cabeçalho passou a apontar para esta auditoria. O teste foi ajustado para conferir isso.

## O que mudou nesta auditoria

- `scripts/rdd_bolsa/49_pareamento_localizacao.py`: só funções de texto. As novas são `_mde`, `_pares_por_ciclo`,
  `_pares_possiveis_sem_caliper`, `_frase_ponto` e `_frase_ph5_poder`. Mudaram os itens "O preço", "Outros raios e a
  região de saúde" e "De onde vem o médico" da interpretação, a frase final da PH-5 na resposta curta e o limite "Cursos
  fora da ponte". Nenhuma conta mudou.
- `docs/06_execucao/57w_resultados_pareamento_localizacao.md`: blocos regravados por `--so-doc` e cabeçalho da
  auditoria.
- `tests/test_pareamento_localizacao.py`: o cabeçalho esperado passa a ser "**Auditoria:** [auditoria 47]". Os 33
  testes passam.
- `output/rdd_bolsa/PL_*`: sem mudança (SHA-256 iguais).
