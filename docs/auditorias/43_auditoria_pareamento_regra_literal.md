# 43. Auditoria do adendo 48e: pareamento pela regra literal do 48d e PSM em 0,400 sem as categorias de um lado só

> **Data:** 26/10/2026.<br>
> **Objeto:** adendo [`48e`](../06_execucao/48e_adendo_pareamento_regra_literal_e_0400.md) (congelado em `f97e1ca`),
> script `scripts/rdd_bolsa/45_pareamento_regra_literal.py`, saídas `output/rdd_bolsa/PM_*`, doc
> [`57s`](../06_execucao/57s_resultados_pareamento_regra_literal.md) (25 decisões da seção 0, versionadas em `d01d873`)
> e `tests/test_pareamento_regra_literal.py`. Base: branch `claude/vigilant-mccarthy-dd92mc`, commit `8dfeb25`.<br>
> **Referências:** adendo [48d](../06_execucao/48d_adendo_controles_localizacao_e_medicos.md), doc
> [57r](../06_execucao/57r_resultados_controles_localizacao_medicos.md),
> [auditoria 40](40_auditoria_controles_localizacao_medicos.md) (achados 3 e 4) e script 44.<br>
> **Método:** recálculo próprio em memória (scratch), sem importar os scripts 44 e 45 nem a `rdd_lib`. A carga das
> bases (covariáveis L e M, CIR por parser próprio, unidades município × ciclo da H1, amostra V e ΔB) é a escrita do
> zero na auditoria 40; só a leitura do quadro do ciclo 2 de 13/02/2026 usa `a36_leitura.ler_quadro` (auditoria 36), e
> a lista dos 2 municípios tirados de V vem de `CL_resumo.json`. Regra 2, logit, suporte, *caliper*, regra literal,
> regra gulosa, Mahalanobis, permutação com inversão, t pareado, IPW com CR1/HC1, balanço, Holm e BKY foram escritos
> nesta auditoria.

## Veredito

**Aprovado com correções.** Todas as linhas de `PM_estimativas.csv` que recalculei batem com as gravadas, com
diferença máxima de 6e−10 (estimativa, p, IC de permutação e IC t). Os pares de PM-1, PM-2 e PM-3 são os mesmos
nos dois cortes, e a lista de quem saiu pela regra 2 é a mesma nas duas janelas. O portão reproduz o 48d. Nenhuma
decisão da seção 0 mudou o que o adendo fixava. As correções foram só de texto, nos blocos gerados do 57s, e nenhum
número mudou: a reexecução do script deu `PM_*` idênticos byte a byte.

## Achados, por gravidade

Não há achado grave nem médio.

### Menores

**A1. O 57s não dizia a quem vale a comparação em 0,400 (corrigido).** A resposta curta dizia "a comparação vale só
para as unidades que ficaram". Não dizia quais. O parágrafo gerado passou a dizer, a partir de `PM_resumo.json`:

- em 0,300 a regra 2 não tirou ninguém;
- em 0,400, na H1, a comparação vale só para municípios que não são capitais, fora do Centro-Oeste e do Sul;
- em 0,400, na oferta local, vale só para municípios que não são capitais, fora do Sul (o Centro-Oeste tem municípios
  dos dois lados e fica);
- quem ficou fora do suporte comum também não entra.

Isso pesa porque, em 0,400, quatro dos cinco municípios de baixo fora do suporte na oferta local são do Centro-Oeste.

**A2. Suposição do pareamento e pacote do corte sem a clareza pedida (corrigido).** O limite "O que o pareamento
supõe" dizia "como sorteado", sem nomear a randomização local condicional. Também não dizia que o IVS fica fora do
escore, de modo que a suposição inclui que a diferença de IVS entre os lados, dentro da janela, não pesa no outcome.
O limite "Pacote do corte" dizia só que o pareamento não isola os R$ 5 mil. Agora diz que nenhum dos desenhos, nem a
RDD nem o pareamento, remove o pacote do corte.

**A3. Decisão 14 (PM-F): acréscimo com justificativa imprecisa.** A decisão diz que "a figura principal pede" o PSM
literal sem a regra 2. O adendo pede só que os resultados do 48d fiquem lado a lado na figura principal. A PM-F é,
portanto, um acréscimo, e não uma exigência do adendo. Ela não muda nada do que o adendo fixa:

- fica fora do Holm, do BKY e da leitura (conferido no CSV);
- em 0,300 é idêntica à PM-1, porque a regra 2 não tira ninguém;
- em 0,400 não tem estimativa, porque o logit não converge (coeficiente máximo de 24 na H1 e de 22 em V).

Ela ajuda a ler a figura, porque separa o efeito da regra 1 (troca de ordem) do efeito da regra 2 (saída das
categorias). A seção 0 é registro pré-estimativa e não foi editada.

**A4. CL-9 não refeito.** A tarefa A da §2.16 do doc 05 da banca 2 previa refazer "PS-1 a PS-4 e CL-7 a CL-9" pela
regra literal. O 48e cobre:

- PS-1 e PS-2 (PM-1 e PM-2);
- PS-3 (PM-4);
- PS-4 (PM-5);
- CL-7 e CL-8 (PM-6).

O CL-9, Mahalanobis na janela de 0,020, ficou de fora. Isso segue o adendo congelado, que não o lista, e o efeito
prático é nulo: o Mahalanobis com o *caliper* do 48d quase não forma par já na janela de 0,050 (auditoria 40, A10). A
§2.16 foi atualizada com essa nota.

**A5. Cosmético nas figuras.** Em `PM_principal.png`, o rótulo "sem estimativa" dos painéis de 0,400 cruza a linha do
zero. Não muda a leitura e não foi alterado.

### Observações (sem correção)

- **IPW em 0,400 (PM-5)** é a linha mais próxima de 5%:
  - fração preenchida: +13,0 p.p., p 0,069;
  - alocados por vaga imediata: +0,14, IC normal de −0,0008 a +0,279, p 0,051. A tabela mostra o limite inferior como
    "0,00", mas ele é negativo.

  São sensibilidade e têm q de BKY = 1. O ponto do IPW é maior que o do pareamento (+5,5 p.p. e +0,07), porque o IPW
  usa todas as unidades ponderadas e não só as pareadas. O sinal é positivo, do lado de bolsa maior.
- **Leitura "o ponto depende da regra"** (§3, 4ª linha) é coerente. Em 0,300, a gulosa e a literal compartilham só 34
  dos 86 a 92 pares na H1 e 16 dos 88 a 95 em V. As unidades usadas, porém, são quase as mesmas (163 em comum na H1).
  Muda quem forma par com quem, não quem entra. A diferença entre os pontos é pequena perto da largura dos IC:

  | Outcome | Gulosa | Literal | Meia largura do IC |
  |---|---|---|---|
  | fração preenchida | −0,6 p.p. | +4,7 p.p. | cerca de 11 p.p. |
  | ΔB2 | −0,71 | +2,00 | cerca de 8,8 |

  A versão da auditoria 40 (lado menor dos três ciclos juntos, em ordem de código) fica no meio: +2,8 p.p., +0,22 e
  +3,41. Três ordens dão três pontos, todos dentro dos mesmos intervalos. É ruído do pareamento com poucas unidades,
  não sinal.

## Fidelidade ao adendo

**Regra literal (§1, item 1).** Confere com a letra do adendo:

- o lado menor procura, contado por corte, janela e, na H1, ciclo;
- no PSM, em ordem decrescente do escore; no Mahalanobis, em ordem crescente de código IBGE e ciclo;
- cada unidade fica com o vizinho livre mais próximo, dentro do *caliper* e sem reposição;
- empate de tamanho: procura o lado de cima.

A implementação é independente da minha e dá os mesmos pares. Lados que procuram (janela de 0,050):

| Corte | H1 | Oferta local |
|---|---|---|
| 0,300 | ciclo 1: abaixo (28 / 33); ciclos 2 e 3: acima | acima |
| 0,400 | os três ciclos: acima | abaixo (120 / 146) |

A troca do passo final do 44 (`guloso_global`) é feita por *monkeypatch* durante a chamada e desfeita no `finally`.
A PM-3 roda o 44 sem troca.

**Regra 2 (§1, item 2).** Ela é aplicada antes do logit, nos dois cortes e nas duas janelas:

- em 0,300 não tira ninguém;
- em 0,400, janela de 0,050, tira 19 linhas da H1:
  - capitais: Manaus, São Luís e Maceió nos ciclos 1 a 3 e Salvador no ciclo 3;
  - Sul: Antonina, no ciclo 2;
  - Centro-Oeste: 8 municípios, uma linha cada;
- tira também 5 municípios da oferta local (as quatro capitais e Antonina);
- na janela de 0,020, tira 7 linhas da H1 e 3 municípios da oferta local.

`PM_excluidos.csv` tem as 34 linhas, com nome, UF, ciclo, lado, categoria e IVS. Recalculei a lista e ela é idêntica.
Depois da saída, nenhuma categoria fica de um lado só.

**Suporte comum (§1, item 3).** O suporte mínimo–máximo é calculado depois da regra 2. As contagens fora do suporte
batem nas 8 combinações de amostra, corte e janela do PSM.

**Holm e BKY (§2).** O Holm cobre as 8 linhas de PM-1 e PM-2 e o BKY as 38 de PM-3 a PM-7. Refiz os dois a partir dos
p gravados, com diferença 0. O menor p de Holm é 0,636 (alocados por vaga imediata em 0,300).

**Leitura do §3.** Os códigos gravados seguem as regras:

- as 8 principais têm IC que contém zero e balanço limpo (maior |DP| depois entre 0,07 e 0,17), então a leitura é
  `NAO_SE_DETECTA_DIFERENCA`;
- nenhuma rejeita zero depois do Holm;
- a regra 2 tira no máximo 14% de um lado (19 de 132 abaixo, H1 em 0,400), abaixo do limiar de 25%;
- `PONTO_DEPENDE_DA_REGRA` aparece em três linhas de 0,300 (fração preenchida, ΔB1 e ΔB2); em alocados por vaga
  imediata e em 0,400 os sinais coincidem.

**Alguma decisão da seção 0 mudou o adendo? Não.**

| Decisão | Avaliação |
|---|---|
| 14, linha PM-F só para a figura | acréscimo fora das famílias e da leitura (A3); não muda nada fixado |
| 2, regra 2 com os três ciclos juntos | segue a letra ("naquela janela e naquela amostra (H1 ou oferta local)") e o logit, que junta os ciclos. Conferi ciclo a ciclo: em 0,400 cada ciclo tem as mesmas categorias de um lado só (capital e Centro-Oeste em todos, Sul no ciclo 2), e em 0,300 nenhuma. O resultado seria o mesmo |
| 7, lados contados depois da regra 2 | o adendo não diz. Contando antes da regra 2, o lado que procura seria o mesmo em todos os grupos (H1 em 0,400: 40/25, 44/38, 48/35, sempre acima; oferta local: 125/146, abaixo; o mesmo na janela de 0,020). Não muda nenhum par |
| 18, famílias de tamanho fixo com p = 1 nas linhas sem estimativa | segue a letra do §2 (Holm "entre as oito", BKY "entre as demais") e é conservadora (resolve o A6 da auditoria 40). Não tem efeito: as 8 do Holm têm estimativa, e o BKY só com as 36 executadas também dá q = 1 em todas (menor p = 0,051) |

**Ordem no Git.** A sequência é:

1. adendo `f97e1ca`, às 20:47;
2. decisões `d01d873`, às 20:54;
3. execução `549fa53`, às 21:03.

A seção 0 do 57s é idêntica entre `d01d873` e a versão auditada, e o SHA-256 do adendo confere com o gravado no
script.

## Portão

O PS-1 e o PS-2 do 48d em 0,300 (regra gulosa, sem a regra 2) se reproduzem: 86 pares na H1, 88 no ΔB1 e 87 no ΔB2,
porque um par não tem o outcome. O script dá diferença ≤ 1,1e−16 e os mesmos pares de `CL_resumo.json`. O meu recálculo
dá diferença ≤ 1e−10 e os mesmos 86 e 88 pares. A PM-3 em 0,300 é idêntica ao 48d, porque a regra 2 não tira ninguém
nesse corte.

## O que foi recalculado

Valores do recálculo próprio. "Gravado" vem de `PM_estimativas.csv`. Em todas as linhas abaixo, a diferença máxima
entre recalculado e gravado (estimativa, p, IC de permutação e IC t) é ≤ 6e−10.

| Linha | Corte | Outcome | Pares | Diferença média [IC permutação] | p | Maior \|DP\| antes / depois |
|---|---|---|---|---|---|---|
| PM-1 | 0,300 | fração preenchida | 92 | +0,0470 [−0,0651; +0,1605] | 0,409 | 0,25 / 0,14 |
| PM-1 | 0,300 | alocados por vaga imediata | 92 | +0,1019 [−0,0120; +0,2163] | 0,080 | 0,25 / 0,14 |
| PM-2 | 0,300 | ΔB1 | 95 | +0,0571 [−0,7851; +0,8986] | 0,896 | 0,39 / 0,07 |
| PM-2 | 0,300 | ΔB2 | 94 | +1,9983 [−6,7667; +10,8444] | 0,654 | 0,39 / 0,07 |
| PM-1 | 0,400 | fração preenchida | 70 | +0,0546 [−0,0974; +0,2074] | 0,476 | 0,49 / 0,17 |
| PM-1 | 0,400 | alocados por vaga imediata | 70 | +0,0714 [−0,0856; +0,2294] | 0,377 | 0,49 / 0,17 |
| PM-2 | 0,400 | ΔB1 | 88 | −0,1859 [−1,0400; +0,6707] | 0,679 | 0,47 / 0,15 |
| PM-2 | 0,400 | ΔB2 | 88 | +2,6992 [−7,8929; +13,2860] | 0,621 | 0,47 / 0,15 |
| PM-3 | 0,300 | fração / alocados / ΔB1 / ΔB2 | 86 / 86 / 88 / 87 | −0,0061 / +0,0436 / −0,0892 / −0,7106 | — | igual ao 48d |
| PM-3 | 0,400 | fração / alocados / ΔB1 / ΔB2 | 65 / 65 / 91 / 91 | +0,0531 / +0,0631 / −0,1635 / +4,2456 | — | 0,49 / 0,11 e 0,47 / 0,10 |

Também recalculei, com o mesmo resultado (diferença ≤ 6e−10):

- PM-4, janela de 0,020, com a regra 2 refeita na janela: 24 e 38 pares em 0,300; 34 e 32 em 0,400; balanço não limpo
  na H1 em 0,300 (0,34);
- PM-5 (IPW, n por lado igual ao gravado);
- PM-6 (Mahalanobis, regra literal): sem par na H1 em 0,300; 4 pares na H1 em 0,400, com IC não limitado; 10 e 14 pares
  na oferta local;
- PM-7, ΔB4 e ΔB5. O ΔB3 não foi refeito, porque depende da ligação dos médicos no a16;
- PM-F: igual à PM-1 em 0,300 e sem convergência em 0,400.

Também conferi:

- o escore de propensão e a figura `PM_escore_0400.png`;
- o *caliper* e o suporte depois da regra 2. As colunas tiradas por colinearidade em 0,400 são capital, Sul e uma
  região que sobra; o escore não depende de qual região cai.

## Integridade

- **IVS errado:** o recálculo e uma reexecução do script 45, sob *audit hook* de abertura de arquivos, não abrem
  `data/ivs_ipea_2010_municipios.csv`. A running variable é o a08.
- **`data/`:** só é lida (tabela CIR, quadro do ciclo 2, arquivos do universo); `git status` limpo depois da
  reexecução.
- **Competências:** o máximo lido do painel a09 é 202608; nenhuma ≥ 202609.
- **`natureza_dos_dados = EMPIRICO`:** em todas as linhas de `PM_estimativas.csv` (54), `PM_balanco.csv` (200) e
  `PM_excluidos.csv` (34), e no resumo.
- **Nada imputado:** o par sem ΔB2 sai da média, contado ("1 par(es) sem outcome"); as unidades sem covariável saem
  contadas (5 abaixo na H1 e 3 em V, em 0,300).
- **`CL_*`, `HI_*` e `OC_*`:** intactos na reexecução. O commit `8dfeb25` regravou `CL_resumo.json` e `PM_resumo.json`
  só com o SHA-256 novo de `OC_estimativas.csv`, `OC_resumo.json` e `CL_resumo.json`. O `OC_*` tinha mudado de
  formato no commit `515a559` (razão *fuzzy* vazia com instrumento fraco). As estimativas e o `tau_oc` do portão OC
  ficaram iguais.
- **Determinismo:** a reexecução do script na base auditada (`--atualizar-doc`) deu saídas, figuras e doc iguais byte
  a byte. Depois das correções, a nova execução deu `PM_*` idênticos; só os blocos de texto do 57s mudaram.

## Texto do 57s

- **Linguagem causal:** não há. O texto usa "não se detecta diferença", "pacote do corte" e "comparando municípios
  parecidos".
- **Números fora de bloco:** não há resultados digitados fora dos blocos gerados. O teste confere números com duas ou
  mais casas, e a leitura manual não achou outros. Os 86, 88 e 87 da decisão 15 são do 48d, conhecidos antes.
- **Suposição, pacote e parte comparável:** antes estavam incompletos e agora estão explícitos (A1 e A2).
- **Clareza:** a resposta curta diz o resultado, quem saiu e onde o ponto depende da regra. Os códigos da leitura vêm
  com a frase correspondente.

## Correções feitas nesta auditoria

| Arquivo | Mudança | Número mudou? |
|---|---|---|
| `scripts/rdd_bolsa/45_pareamento_regra_literal.py` | frase gerada "Parte comparável" diz, por corte e amostra, a quem vale a comparação (funções `_restricao` e `_restricoes_txt`); limites "Pacote do corte" e "O que o pareamento supõe" reescritos | não (`PM_*` iguais byte a byte) |
| `docs/06_execucao/57s_…md` | blocos regravados; cabeçalho aponta esta auditoria | não |
| `tests/test_pareamento_regra_literal.py` | o teste do cabeçalho passa a esperar a auditoria 43 | — |
| `docs/07_apresentacoes/banca2/05_discussao_historia_empirica.md` | §2.16, tarefas A e B: estado "feito", com a nota do CL-9 | não |

Testes rodados: `test_pareamento_regra_literal.py` e `test_controles_localizacao_medicos.py`, com 52 testes, todos OK.
