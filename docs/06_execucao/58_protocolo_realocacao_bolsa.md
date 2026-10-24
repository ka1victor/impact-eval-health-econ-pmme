# 58. Protocolo da realocação: a bolsa das concorrentes desloca candidatos e preenchimento?

> **Data de congelamento:** 24/10/2026, antes de abrir qualquer outcome por
> exposição.<br>
> **Pedido do autor:** testar se a bolsa maior **desloca** médicos entre vagas
> do programa em vez de preencher mais vagas no total.<br>
> **Estatuto:** `EXPLORATORIO_REALOCACAO`. Já foram vistos o E9 (doc 42: sinal
> da bolsa na escolha, robusto só no ciclo 2), o P1 (doc 57a: peso da
> distância, da UF e da região de saúde; logit aninhado por CIR com
> lambda < 1) e o A3 (doc 49, §15: RDD por célula aberta, nula ou frágil). Este
> protocolo não muda nenhum deles nem o Holm do protocolo 40. Toda saída leva
> `natureza_dos_dados = EMPIRICO`.<br>
> **Script:** `scripts/rdd_bolsa/32_realocacao_bolsa.py`.<br>
> **Saídas:** `output/rdd_bolsa/R_*`.<br>
> **Resultados:** `docs/06_execucao/57g_resultados_realocacao.md`, gerado
> inteiro pelo script.<br>
> **Testes:** `tests/test_realocacao_bolsa.py`.

## 1. Pergunta, mecanismo e por que importa

As vagas do PMM-E disputam o mesmo grupo de candidatos numa alocação
centralizada por nota. Os candidatos escolhem entre as células abertas do seu
curso e ciclo (P1). Se uma bolsa maior atrai candidatos para uma célula, eles
podem sair de células próximas do mesmo curso. Duas consequências:

1. **Agregado.** A bolsa maior pode preencher mais uma vaga e menos outra,
   sem mudar o total. O efeito líquido do programa seria menor que o efeito
   na célula.
2. **SUTVA da RDD.** A RDD nos cortes compara vizinhos que disputam as mesmas
   pessoas. Se o lado de cima tira candidatos do lado de baixo, o salto mede
   tratamento mais deslocamento, e o salto fica maior que o efeito líquido.

**Hipótese (H-R).** Uma célula que tem, entre as concorrentes próximas do
mesmo curso e ciclo, bolsa média mais alta que a sua recebe menos candidatos
de 1ª opção e preenche menos na 1ª chamada.

**Fonte de variação.** A bolsa das concorrentes muda só onde os municípios
delas caem em relação a 0,300 e 0,400. Com o IVS próprio e o IVS das
concorrentes controlados de forma contínua, a variação que sobra na exposição
vem dos degraus da bolsa das concorrentes.

## 2. O que o contraste identifica e o que não identifica

- **Identifica (sob as hipóteses do §5):** quanto os outcomes da célula mudam
  quando a bolsa média das concorrentes do mesmo mercado sobe, com a própria
  faixa, o próprio IVS e o IVS das concorrentes mantidos. É um efeito de
  equilíbrio parcial entre vagas já abertas.
- **Pacote do corte.** Em 0,300 e 0,400 mudam também outras regras federais
  (auditoria 18). A exposição é "concorrentes do outro lado do corte", isto é,
  concorrentes sob o pacote do corte, não só sob a bolsa.
- **Não identifica:** a participação no PMM-E, o efeito total do Agora Tem
  Especialistas, a entrada de novos candidatos no programa nem a oferta
  líquida de especialistas no município.
- **Incentivo marginal.** O contraste é do incentivo marginal de R$ 5 mil das
  concorrentes, condicional à abertura das vagas.

## 3. Dados

| Item | Fonte |
|---|---|
| Células | `output/rdd_bolsa/outcomes/outcomes_V_celula.parquet` (estabelecimento × curso × ciclo do quadro da 1ª chamada, ciclos 1–3) |
| Bolsa | `faixa_anunciada` → R$ 10, 15 ou 20 mil, pelo mapa do E9 (`mapa_bolsa_por_faixa`), conferida contra a regra de dois cortes |
| IVS | IVS 2010 oficial do a08 (`output/aquisicao/a08_ivs_2010_oficial_municipio.csv`), conferido contra `ivs_2010_oficial` da célula. O arquivo `data/ivs_ipea_2010_municipios.csv` **não é lido** |
| Região de saúde (CIR) | tabela oficial do TabNet (`data/raw/aquisicao/territorio/datasus_tabnet_br_regsaud.cnv`), lida sem alteração pela função da X5 |
| Distância | círculo máximo entre os centroides do IBGE dos municípios (mesma função e arquivo do G1 e do P1) |
| Covariáveis pré | log da população do Censo 2022 (a06) e estoques CNES pré-programa (202406–202506) das CBO-alvo e de generalistas (a09), pela função do A4 (script 24) |

Nenhum dado de candidato é gravado: os outcomes são contagens por célula que
já estão em `outcomes_V_celula`.

## 4. Unidade, mercado e exposição

**Unidade.** Célula aberta (estabelecimento × curso × ciclo), ciclos 1–3
empilhados.

**Mercado relevante.** Mesmo curso e mesmo ciclo. As concorrentes de uma
célula são as outras células do mesmo curso e ciclo no mesmo mercado
geográfico.

| Definição | Papel | Justificativa (P1, doc 57a) |
|---|---|---|
| **Mesma região de saúde (CIR)** | **principal** | No M1, "mesma região de saúde" pesa +1,65 na utilidade além da distância, e no logit aninhado por CIR (M9) lambda = 0,449 (IC [0,341; 0,556]): a substituição entre vagas é mais forte dentro da CIR do que o logit simples supõe. É o mercado em que o deslocamento, se existe, deve aparecer primeiro |
| Raio de 200 km entre centroides | sensibilidade declarada (R1) | A distância pesa −0,189 por 100 km no M1 e −1,11 em média no logit misto (M8), com desvio de 0,71 entre candidatos: para parte dos candidatos a distância domina a escolha. O raio captura concorrentes próximas que caem em CIR vizinha |
| Mesma UF | sensibilidade (R2) | "Mesma UF da origem" é o atributo de maior peso no M1 (+2,40); mercado largo, com mais concorrentes e mais variação |

Concorrentes no mesmo município têm o mesmo IVS e a mesma bolsa da célula:
entram no mercado e na média (contribuem com diferença zero de bolsa).

**Exposição principal.** `E = bolsa média das concorrentes − bolsa da
célula`, em R$ mil por mês, média simples sobre as células concorrentes
(cada célula é uma alternativa do conjunto de escolha, como no P1). Como a
faixa própria entra como efeito fixo, o coeficiente de E é o da bolsa média
das concorrentes. O coeficiente é relatado por R$ 1 mil e por R$ 5 mil (todas
as concorrentes um degrau acima).

**Exposição alternativa (R3).** Fração das concorrentes com bolsa maior que a
da célula.

**Células sem concorrente** no mercado não têm exposição definida: ficam fora
da amostra daquela definição, com o motivo `sem concorrente do mesmo curso e
ciclo no mercado`. Nada é imputado.

**Informação já vista no desenho (sem outcomes).** Antes de congelar, foi
calculada só a distribuição da exposição, sem nenhum outcome: das 5.135
células, 2.876 têm ao menos uma concorrente na mesma CIR (mediana 2), 4.533 no
raio de 200 km (mediana 5) e 4.854 na mesma UF (mediana 11); 26% das células
com concorrente na CIR têm alguma concorrente com bolsa maior (44% no raio de
200 km). Uma célula sem IVS oficial e 9 células de município sem CIR oficial
(110002) ficam fora.

## 5. Identificação

**Desenho principal (a).** MQO (modelo linear de probabilidade nos outcomes
binários) na amostra de células com concorrente na CIR:

```
y_i = β·E_i + faixa própria (2 indicadores) + spline do IVS próprio
      + média, nas concorrentes, da spline do IVS
      + log(1 + nº de concorrentes)
      + efeito fixo de curso × ciclo
      + log da população 2022 + estoque CNES pré das CBO-alvo + estoque pré de generalistas
      + erro
```

- Spline do IVS: linear, contínua, com nós em 0,300 e 0,400, em unidades de
  0,1 de IVS (base do E9 §15: IVS − 0,300, (IVS − 0,300)₊, (IVS − 0,400)₊).
- Controle das concorrentes: a média, sobre as concorrentes, de cada termo
  da mesma spline. Como a bolsa de cada concorrente é 10 + 5·1[IVS > 0,300] +
  5·1[IVS > 0,400], a variação de E que sobra vem dos degraus das
  concorrentes, não do nível contínuo do IVS delas.
- A faixa própria absorve o salto da própria célula; β não é o efeito da
  bolsa própria.

**Hipóteses de identificação.** (i) Com o IVS das concorrentes controlado de
forma contínua, a posição delas em relação aos cortes não se correlaciona com
outros determinantes dos outcomes da célula; (ii) as demais políticas dos
mesmos cortes (auditoria 18) não afetam os outcomes da célula pelo lado das
concorrentes, ou entram como parte do pacote; (iii) o conjunto de células
abertas é tomado como dado (ver limitações).

**Efeitos fixos e inferência (b).** Efeito fixo de curso × ciclo. EP CR1 com
cluster por **CIR** (as exposições são comuns às células da mesma CIR);
cluster por município como sensibilidade (R5). Ao lado, o p pela t com G − 1
graus de liberdade.

**Covariáveis (c).** As do A4: log da população do Censo 2022 e estoques CNES
pré-programa (média mensal de profissionais distintos, 202406–202506) das
CBO-alvo e de generalistas do município da célula. Célula sem estoque
completo sai da amostra com o motivo, nunca com zero.

## 6. Outcomes e famílias

| Id | Outcome | Coluna | Papel |
|---|---|---|---|
| **R-P1** | célula preenchida na 1ª chamada (≥ 1 alocado) | `n_alocados_ch1 ≥ 1` (como `A3_PREENCHIDA`) | **primária** |
| **R-P2** | nº de candidatos de 1ª opção da célula | `n_cand_1a_opcao` | **primária** |
| R-S1 | tem candidato de 1ª opção | `n_cand_1a_opcao > 0` | secundária |

**Holm** nas duas primárias, só na especificação principal (CIR, E, ciclos
1–3, com covariáveis). Hipótese de deslocamento: β < 0; o teste é bilateral.

## 7. Especificações relatadas (todas; nenhuma é escolhida depois)

| Id | Variação sobre a principal |
|---|---|
| **PRINCIPAL** | CIR, E, ciclos 1–3, cluster CIR, com covariáveis |
| R1 | mercado = raio de 200 km (sensibilidade declarada) |
| R2 | mercado = mesma UF |
| R3 | exposição = fração das concorrentes com bolsa maior (CIR) |
| R4 | spline quadrática (grau 2, nós nos cortes) no IVS próprio e na média das concorrentes |
| R5 | cluster por município |
| R6 | sem covariáveis, na mesma amostra |
| R7 | "RDD do vizinho": células com ao menos uma concorrente de outro município com IVS a até 0,050 de um corte; exposição = 5 × fração dessas concorrentes acima do seu corte (R$ mil); controles = média de (IVS − corte) dessas concorrentes, dos dois lados separados, mais os controles próprios da principal |
| C1, C2, C3 | principal por ciclo (o ciclo 1 à parte porque a adesão dos gestores precedeu o anúncio da faixa; heterogeneidade por condição pré-tratamento) |

R1–R7 e C1–C3 são relatados para os três outcomes, sem Holm próprio.

## 8. Placebos

| Id | Exposição placebo | Leitura esperada |
|---|---|---|
| PL1 | bolsa média das células de **outros cursos** do mesmo ciclo na mesma CIR, menos a própria (com os mesmos controles calculados sobre essas células) | vagas que não disputam os mesmos candidatos: coeficiente ≈ 0 |
| PL2 | bolsa média das células do mesmo curso na mesma CIR que **só abrem em ciclo posterior** (chave estabelecimento × curso ausente no ciclo da célula), menos a própria; ciclos 1 e 2 | o candidato do ciclo da célula não podia escolhê-las: coeficiente ≈ 0 |

Um placebo com p < 0,05 indica que a exposição capta outra coisa (geografia
do IVS, abertura), e a principal não é lida como deslocamento.

## 9. Poder

MDE com 80% de poder e teste bilateral a 5%: `MDE = 2,802 × EP`, por R$ 1 mil
e por R$ 5 mil de E, e pelo desvio-padrão da exposição residualizada (E
depois de tirar os controles). Também a variação disponível: desvio-padrão de
E bruto e residualizado, e a fração da variância de E que os controles
explicam.

**Limiares (por R$ 5 mil de E), fixados agora:**
- R-P1: MDE ≤ 10 p.p. é "pequeno" (o alvo de +10 p.p. do T2.3, doc 51);
- R-P2: MDE ≤ 0,25 candidato por célula é "pequeno" (próximo do salto
  previsto pelo P1g para a própria bolsa, +0,218).

## 10. Leitura pré-registrada

Por outcome primário, na especificação principal:

| Resultado | Leitura |
|---|---|
| β < 0, p de Holm < 0,05, mesmo sinal em R1 e R3 e PL1 e PL2 com p ≥ 0,05 | evidência de deslocamento |
| β < 0 com p de Holm < 0,05, mas placebo com p < 0,05 ou sinal trocado em R1 ou R3 | sinal não robusto; não é lido como deslocamento |
| IC contém zero e MDE abaixo do limiar | pouca competição local nessa margem |
| IC contém zero e MDE acima do limiar | inconclusivo |
| β > 0 com p de Holm < 0,05 | contrário à hipótese; relatado como tal (complementaridade ou confusão geográfica), sem leitura causal forte |

Tudo é condicional às vagas abertas e ao pacote do corte.

## 11. Limitações declaradas

- **Pacote do corte** (auditoria 18): as concorrentes acima do corte estão
  sob outras regras federais além da bolsa.
- **Vagas abertas endógenas:** a abertura é decisão do gestor e da SGTES. No
  A2 (doc 49, §15), os limites de Lee para o preenchimento são largos (no
  empilhado, margem intensiva [−31,2; +26,3] p.p.); no P5 (doc 57e), a célula
  pedida salta +14,7 p.p. nos cortes (IC [+1,8; +27,6], sem passar no BKY). O
  conjunto de concorrentes, e portanto a exposição, depende dessa abertura.
- **Conjunto de escolha:** supõe-se que o candidato vê todas as células do
  curso no ciclo (§14 do protocolo 40); a escolha da 1ª opção não diz o
  mercado que ele de fato considerou.
- **Mercado geográfico aproximado:** CIR e raio são aproximações do mercado
  de cada candidato; a origem do candidato não entra na definição do
  mercado.
- **Poucas células com concorrente de outra faixa** na CIR: o poder pode ser
  baixo (§9).
- **Associação vs. causa:** fora das hipóteses do §5, os coeficientes são
  associações condicionais e são descritos como tais.

## 12. Integridade

- nada simulado, imputado ou digitado vira observação;
- faltante fica faltante, com motivo e contagem;
- todo número do doc 57g sai de `output/` e é conferido por teste;
- o IVS é o oficial do a08; `data/ivs_ipea_2010_municipios.csv` não é lido;
- `data/` não é alterado;
- nenhum identificador de candidato em `output/`;
- desvio forçado pelos dados vira adendo datado neste documento ou na seção
  de desvios do 57g;
- heterogeneidade só por condição pré-tratamento (ciclo);
- linguagem descritiva onde a identificação não sustenta causalidade;
- figuras sem texto de leitura embutido; o "Como ler" fica no doc e no campo
  `como_ler` do resumo;
- a verificação sintética (mercado simulado com deslocamento conhecido) fica
  só em memória, no teste, rotulada "sintético".
