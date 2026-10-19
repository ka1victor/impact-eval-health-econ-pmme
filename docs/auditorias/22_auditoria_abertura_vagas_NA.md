# Auditoria independente do adendo §7 do protocolo 48 (família NA)

> **Data:** 19/10/2026.<br>
> **Objeto:** commit `738a706`: `scripts/rdd_bolsa/24_abertura_vagas_selecao.py`,
> `output/rdd_bolsa/NA_estimativas.csv`, `NA_resumo.json`, `NA_figuras/`, a
> seção 15 do [doc 49](../06_execucao/49_resultados_contagem_vagas_preenchidas.md),
> `tests/test_abertura_vagas.py` e o helper de Lee da `rdd_lib`, contra o
> [protocolo 48](../06_execucao/48_protocolo_contagem_vagas_preenchidas.md),
> §7 (A1–A4) e §8 (correção).<br>
> **Veredito:** **APROVADO COM CORREÇÕES.** A1, A3, A4 e a margem intensiva do
> A2 foram reproduzidos de forma independente até ~1e-12, inclusive o
> bootstrap. Houve um defeito de implementação no Lee extensivo: o aparo de
> empates seguia a ordem das linhas. Ele foi corrigido e mudou só as 12 linhas
> `A2_EXTENSIVA`. A leitura conjunta tinha frases que diziam mais do que as
> estimativas sustentam; as regras foram corrigidas. As figuras foram
> refeitas.<br>
> **Proveniência dos números:** todo número citado aqui foi lido de
> `output/rdd_bolsa/NA_estimativas.csv` depois da correção. A conferência
> independente que fica no repositório é a classe
> `TestRecalculoIndependenteAuditoria22` de `tests/test_abertura_vagas.py`.

## 1. Como a auditoria foi feita

O código de conferência foi escrito do zero, com MQP em numpy. Ele não importa
os estimadores do script 24 nem os da `rdd_lib`.

Fontes lidas:
- `output/rdd_bolsa/outcomes/` (U, V município e V célula);
- a running variable é a coluna `ivs_2010_oficial`, conferida contra o a08;
- `output/aquisicao/cnes_nacional/painel_municipio_cbo_mes.parquet`, só de
  `202406` a `202506`. O painel tem as 5.565 linhas por competência e grupo,
  com zeros explícitos, então nenhum estoque é imputado;
- `data/ivs_ipea_2010_municipios.csv` não foi lido.

Convenções reproduzidas:
- kernel triangular, h = 0,050, ponto x = h fora;
- HC1 por corte e CR1 por município nos empilhados;
- intercepto e inclinações por grupo × lado e salto comum, com grupo = corte,
  ciclo ou ciclo × corte, como no N;
- zero verdadeiro de U só fora do quadro: sem célula, nenhuma vaga oferecida e
  nenhuma preenchida.

## 2. Recálculo

| Item | Linhas | Diferença máxima (tau, EP) |
|---|---:|---|
| A1, vagas preenchidas, oferecidas e limitadas por 10 mil hab., todos os ciclos e cortes | 36 | 9e-17 |
| A1, Poisson com offset log(população), mesmas amostras | 36 | 3e-15 |
| A3, célula preenchida (principal e sem efeitos fixos), alocados / vaga e candidatos de 1ª opção | 48 | 1e-16 |
| A4, N1 com e sem covariáveis (V) | 24 | 8e-12 |
| A4, A1 com covariáveis (U) | 24 | 6e-13 |
| A4, balanço das covariáveis | 13 | 1e-14 |
| A2 intensiva e variante ponderada pela população: s, f, p, lado e limites | 24 | 5e-16 |
| A2 extensiva, código original (aparo pela ordem das linhas) | 12 | 5e-16 |
| A2, bootstrap de 999 reamostras (semente `[20261018, 48, 7]`): reamostras válidas, EP de cada limite e IC de Imbens–Manski | 36 | idênticos (6 casas), antes e depois da correção |

Também conferido:
- o IC de Imbens–Manski: c resolve Φ(c + Δ/máx EP) − Φ(−c) = 0,95;
- a fórmula dos limites do §7;
- o lado aparado: o de maior taxa de seleção. Nos empilhados, a taxa de cada
  lado é Σ ω_g × intercepto_g, com os pesos ω_g da regressão de seleção, e o
  lado de cima é o de baixo mais o salto comum;
- a direção do salto: lado com bolsa maior menos lado com bolsa menor.

## 3. Achados e correções

### C1. Lee extensivo: empates aparados pela ordem das linhas (defeito, corrigido)

**O problema.** `rdd_lib._multiplicador_aparo` ordena y e desempata pela
posição da linha. A fração preenchida do município tem muitos 0 e 1. Por isso,
"aparar q da massa pelo topo" retirava inteiros os primeiros municípios com
y = 1 na ordem do arquivo, que é a do código IBGE, isto é, por UF. Esses
municípios ficam em posições arbitrárias de x. Retirá-los mudava a inclinação
local, e 4 das 12 linhas tinham o salto sem aparo fora dos limites (2|0,300,
2|0,400, 2|empilhado, 3|0,400), todas com fração aparada pequena (0,9 % a
3,7 %), quando os limites deveriam ficar colados ao salto ingênuo.

Isso não é a aproximação (i) declarada da `rdd_lib`, que trata do quantil
no meio-janela. É uma escolha arbitrária entre observações empatadas.

**A correção.**
- `_multiplicador_aparo` e `limites_lee_rd` ganharam `empates="proporcional"`:
  o bloco empatado na fronteira perde a mesma fração de peso em todas as
  linhas;
- o padrão `"ordem"` ficou inalterado, então os scripts 17 e 18 não mudam;
- o script 24 usa a forma proporcional no pontual, no bootstrap e na
  conferência contra a `rdd_lib`;
- testes novos: a forma proporcional não depende da ordem das linhas, retira
  exatamente q e coincide com a forma por ordem quando não há empate.

**Efeito.** Mudam só as 12 linhas `A2_EXTENSIVA`. Uma linha continua com o
salto ingênuo fora dos limites: ciclo 2, corte 0,400, com q = 3,7 %, salto de
+13,1 p.p. e limites [+11,3; +12,2]. Aí é a aproximação (i) de fato: com reta
local, tirar peso uniforme dos zeros muda também a inclinação, e o intercepto
extrapolado cai. A nota da linha diz isso e não afirma mais que é "por
construção".

Nenhuma conclusão muda: em todas as linhas empilhadas, os limites e o IC de
Imbens–Manski continuam contendo zero.

**Recomendação ao autor, sem execução aqui:** os scripts 17 e 18 chamam
`limites_lee_rd` com o padrão `"ordem"`. Se os outcomes deles tiverem
empates, vale reavaliar com `"proporcional"`.

### C2. Leitura conjunta: regra incompleta e frases fortes demais (corrigido)

A regra do ramo "nenhuma leitura distingue de zero" não olhava duas linhas que
o próprio texto cita:
- o IC de Imbens–Manski da margem extensiva;
- o A1 com covariáveis.

Hoje as duas contêm zero, então a frase gerada não mudou. A regra, porém,
podia gerar a frase mesmo se elas excluíssem zero. Agora entram na condição e
na lista de discordâncias.

Três frases afirmavam mais do que as estimativas mostram:

| Frase gerada | Problema | Agora |
|---|---|---|
| "o único salto que exclui zero é o de N1 [...] (S-b)" | só vale entre as linhas empilhadas; o A1 de vagas preenchidas por habitante no corte 0,300, ciclos empilhados, também exclui zero | "entre as linhas empilhadas desta leitura, só [...]"; os cortes isolados que excluem zero (A1 e A3) são listados por regra, sem correção por comparações múltiplas |
| "é compatível com diferença de porte entre os lados do corte, não com efeito sobre o preenchimento" | um IC que contém zero não mostra efeito nulo. O balanço em V não mostra salto no log da população; os estoques do CNES saltam pouco, com p em torno de 0,08. Com coeficiente único para as covariáveis, fora do adendo, o S-b ainda exclui zero | a frase passa a dizer que isso é compatível com diferenças pré-existentes de porte ou capacidade, mas não as demonstra nem mostra efeito nulo; quando a variante de coeficiente único exclui zero, a regra diz que a leitura depende da especificação |
| ramo da oferta: "não o preenchimento das vagas abertas" | o mesmo problema: "nulo" tratado como zero | "não há evidência de mudança no preenchimento [...]" |

Também foi acrescentado "isso é falta de evidência, não prova de efeito nulo",
e um teste impede as frases antigas.

Continuam valendo:
- as regras dos ramos;
- o rótulo "pacote do corte, não participação no PMM-E";
- a declaração de monotonicidade, no doc 49 e em `NA_resumo.json`.

### C3. Figuras (corrigido)

Problemas encontrados:
- nos dois PNG, o rótulo "salto" ficava sobre a bolha logo à direita do corte;
- a legenda de tamanhos mostrava 1, 10 e 50, mas as faixas têm centenas de
  linhas (A1) ou de células (A3).

Correções:
- o rótulo foi para o alto do painel, junto à linha do corte;
- a chave de tamanhos é desenhada à mão, com a mesma área dos pontos e os
  valores observados (mínimo e máximo por faixa);
- o "Como ler" ganhou a leitura do sinal da seta, a frase "IC que contém zero
  não prova efeito zero" e "descritivo do pacote do corte, não participação".

As opções novas de `desenhar` (script 23) têm padrões que reproduzem as
figuras N. Isso foi conferido: as seis `N_figuras/*.png`, regeneradas com o
código novo, saem byte a byte iguais.

### C4. Ausente virando zero, de forma latente (corrigido)

No script 24, `(aloc >= 1)` e `(n_cand_1a_opcao > 0)` transformariam NaN em
0. Hoje essas colunas não têm ausentes, então nada mudou nas saídas. Agora o
ausente fica ausente.

## 4. Julgamentos sem correção

**Variante do A2 com seleção ponderada pela população.**
- **O rótulo está certo.** O §7 diz "vagas oferecidas por 10 mil habitantes"
  sem dizer o peso, e a principal usa a média municipal, a mesma do A1.
- **Ela é a que mede a fração da massa de vagas.** É a forma coerente com a
  taxa de preenchimento ponderada pelas vagas. As duas coincidem só se a
  intensidade de abertura não depender do porte.
- **Ela é instável.** No ciclo 1, corte 0,300, o intercepto de baixo é
  negativo e só 500 das 999 reamostras são válidas.

Mantida como sensibilidade, fora do adendo. O doc 49 agora explica a diferença
em prosa, sem números.

**Empilhado do A2 intensivo.** f0 agrega os interceptos de f com os pesos ω
da regressão de s, e f1 = f0 + salto comum de f. Os pesos ω de f são
outros. É uma aproximação razoável e declarada em `decisoes`.

**Reamostras inválidas descartadas.** Uma reamostra é descartada quando a
taxa de seleção estimada não é positiva ou falta suporte. O EP passa a ser
condicional às reamostras válidas. As linhas com menos de 90 % de reamostras
válidas têm nota. Nenhuma é linha principal: a pior principal tem 947 de 999.

**Bootstrap do A3 e do A4.** Não é pedido pelo §7; o EP é CR1.

## 5. Correção do §8 e prosa do doc 49

As citações conferem com os arquivos:

| Fonte | O que foi conferido |
|---|---|
| `normas_ivs/edital_sgtes_02_2025_gestores_dou.html` | DOU de 12/06/2025; Edital nº 2, de 10/06/2025; item 3.9 citado literalmente; nenhuma menção a IVS, vulnerabilidade ou faixa |
| `normas_ivs/edital_sgtes_03_2025_ciclo1_dou.html` | DOU de 24/07/2025; item 11.1.4 citado literalmente, com a grade de R$ 20/15/10 mil |
| `ivs_regra/edital_sgtes_03_2025_faq_bolsa.html` | "Publicado em 24/07/2025 14h10, Atualizado em 25/06/2026" |
| `ivs_regra/edital_sgtes_01_2026_ciclo2.html` | publicado em 03/02/2026; a página não traz a grade |
| `ivs_regra/edital_sgtes_05_2026_adesao_ciclo3.html` | publicado em 10/06/2026 |
| A01 | quadro do ciclo 1 de 24/07/2025; proposta preliminar do ciclo 3 de 15/05/2026 |

Ressalvas de precisão, sem erro factual:

1. **"A adesão dos gestores precedeu o anúncio da faixa" é inferência.** O
   cronograma de adesão do Edital 2/2025 foi publicado à parte e não está
   arquivado. O que as fontes mostram é que o chamamento não trazia a grade e
   que o quadro, resultado da adesão, saiu no mesmo dia da grade. A conclusão
   (a oferta do ciclo 1 não respondeu à faixa anunciada) se sustenta. A
   antecipação privada da grade não é observável.
2. **A grade de 2026 "pública desde o Chamamento 1/2026" vem do a03 e da
   [auditoria 01](01_regra_institucional.md), §6.2.** A cópia arquivada da
   página do 1/2026 não traz o texto da grade. O Edital 28/2026 traz, no item
   11.2, mas o arquivo `edital_sgtes_06_2026_edital_28_2026_ciclo3.html` é um
   PDF com extensão `.html`.

**Texto congelado.** O protocolo 48 só recebeu acréscimos:
- `be6c791` acrescentou o §7;
- `738a706` acrescentou o §8;
- nenhuma linha dos §1–§7 foi alterada; o diff de cada commit só tem linhas
  com "+".

**Prosa do doc 49, §1.** A frase "definidas pelo gestor depois de a faixa ser
conhecida" foi corrigida para a versão por ciclo do §8. Está certa e
consistente com o §8.

## 6. Rótulos, ausentes e números do doc

- **Rótulos:** todas as 690 linhas têm `natureza_dos_dados = EMPIRICO` e
  `estatuto = PROTOCOLO_48_ADENDO_7_POS_RESULTADO`. O resumo também, e as
  figuras levam "EMPIRICO" no texto.
- **Ausentes:**
  - o único zero criado é o de U fora do quadro;
  - a fração fora do quadro fica NaN;
  - os estoques do CNES ficam NaN sem as 13 competências (nenhum caso);
  - não há `fillna(0)`.
- **Números do doc 49:** os números da seção 15 vêm só dos blocos
  `<!-- NA:... -->`, que o teste exige idênticos aos gerados. O teste de prosa
  sem número continua passando.
- **Holm:** nenhuma linha entra em Holm, porque o adendo não define um.

## 7. Números principais depois da correção

Ciclos 1 a 3 e cortes empilhados.

| Análise | Linha | Estimativa | Intervalo |
|---|---|---:|---|
| A1 | vagas preenchidas por 10 mil hab. (U) | −0,039 | IC [−0,100; +0,023], p = 0,217 |
| A1 | vagas oferecidas por 10 mil hab. (U) | −0,066 | IC [−0,159; +0,028], p = 0,171 |
| A2 intensiva | aparo de 38,3 % abaixo | limites [−31,2; +26,3] p.p. | Imbens–Manski [−60,9; +47,3] |
| A2 extensiva | aparo de 14,2 % abaixo | limites [−11,8; +5,2] p.p. (antes [−12,7; +5,3]) | Imbens–Manski [−23,2; +18,6] |
| A3 | célula preenchida, EF de curso × ciclo e tipo de vaga | −4,9 p.p. | IC [−12,9; +3,2], p = 0,237 |
| A4 | N1 sem covariáveis (S-b) | −1,45 | IC [−2,90; −0,01], p = 0,048 |
| A4 | N1 com covariáveis | −0,98 | IC [−2,00; +0,03], p = 0,057 |
| A4 | N1, coeficiente único (fora do adendo) | −1,39 | IC [−2,69; −0,08], p = 0,037 |

No ciclo 1, nenhuma linha empilhada exclui zero:
- A1, vagas preenchidas por habitante: −0,013 [−0,032; +0,005];
- A3: −3,3 p.p. [−20,9; +14,2];
- limites de Lee: intensiva [−49,1; +23,8], extensiva [−23,2; +15,5].

Tudo isso é descritivo, do pacote do corte, e não efeito da participação no
PMM-E.

## 8. Reprodução

- **Determinismo:** `python scripts/rdd_bolsa/24_abertura_vagas_selecao.py`
  rodou duas vezes. CSV, JSON, as duas figuras e o doc 49 saíram byte a byte
  iguais.
- **Testes:** `python -m pytest -q` foi interrompido por falta de memória
  (cgroup), por causa de outros processos da máquina. Rodado módulo a módulo,
  os 52 módulos passaram: 905 testes e 2 pulados.
  `tests/test_integridade_dados.py` passou sozinho, sem mudança.
- **Arquivos alterados:**
  - `scripts/rdd_bolsa/rdd_lib.py`: opção `empates`, com o padrão antigo;
  - `scripts/rdd_bolsa/23_estimar_contagem_vagas.py`: opções de `desenhar`,
    com os padrões antigos;
  - `scripts/rdd_bolsa/24_abertura_vagas_selecao.py`;
  - saídas `NA_*`;
  - doc 49, seção 15 (prosa do A2 e blocos regenerados);
  - doc 38;
  - `tests/test_abertura_vagas.py` e `tests/test_rdd_lib.py`.
