# Reauditoria independente de A1 a A8

> **Data:** 2026-09-09. **Mandato:** reverificar do zero, sem confiar na
> execução nem na lógica anteriores, re-derivando números a partir dos dados
> observados. **Método:** reimplementação independente, sem chamar os scripts do
> projeto; documentação tratada como afirmação a testar.

## 1. Veredito

O núcleo numérico do projeto está correto. Todas as estimativas publicadas de
A1 a A8 reproduzem — em A4, A5 e A8 com diferença máxima na ordem de `1e-14`.
Não há referência trocada, cluster perdido, controle pós-tratamento, join que
infle denominador nem amostra diferente da declarada.

Os achados abaixo são de três tipos: divergências entre protocolo declarado e
execução, escolhas de medida não documentadas, e afirmações de documentação sem
lastro. Dois têm severidade alta e um deles derrubou uma afirmação do artigo.

## 2. O que foi reproduzido do zero

| Módulo | Reprodução |
|---|---|
| A1 | reimplementação integral a partir dos XLSX brutos: `3.323×25`, zero divergência em 23 das 25 colunas; as duas restantes são pontuação de nome de município, e os joins usam código IBGE |
| A2 | reclassificação dos 5.570 municípios direto de REGIC/RM: **0 divergências em 540/540** |
| A3 | MDEs recalculados: 0,1946 / 0,1374 / 0,1190, idênticos aos publicados; fórmula do contraste correta, DEFF de Kish/Moulton |
| A4 | LPM, Logit, ajuste completo, winsorizado, FDR e 411 linhas de leave-one-out, `\|Δ\| ≤ 3,1e-15` |
| A5 | estudo de evento reestimado por dois algoritmos independentes de absorção: beta `202603` = 0,5001997255, EP 0,2340124350, pré-tendências `F=1,0310168` |
| A7/A8 | 36 pares reconstruídos dos brutos; todos os efeitos, ICs e 21 p-valores exatos recalculados à mão, idênticos |

Portões anti-outcome verificados **além da leitura de código**: o universo dos
540 municípios de A2 é exatamente oferta ch1 (368) ∪ reserva ch2 (507), ambos
publicados antes do resultado; a janela de estoque pré é estritamente
`competencia < 202507`, anterior à oferta de 24/07/2025.

## 3. Achados de severidade alta

### 3.1 A8 — `ativo em qualquer local` só conta o ciclo 1

`active_sets(1)` filtra `nominal["ciclo"].eq(1)`. Controles que aparecem ativos
no retrato de 12/08/2026 **sob o ciclo 2** são codificados como zero. O viés é
unidirecional: nenhum selecionado está no ciclo 2.

Reconstrução independente da primeira chamada (30 pares, idêntica à do projeto):

```
selecionados     : 0,5333 sob qualquer definição
nao selecionados : 0,2000 (filtro ciclo 1)  ->  0,2333 (qualquer ciclo)
diferenca        : +0,3333 (p=0,0414)       ->  +0,3000 (p=0,0784)
```

### 3.2 A8 — `homologação em qualquer local` usa só a lista da primeira chamada

A lista da segunda chamada é cumulativa. Usando as duas listas, a homologação
dos não selecionados em qualquer local sobe de 5,6% para 25,0%, e o contraste
cai de 58,3 para 44,4 pontos percentuais.

### 3.3 Consequência para o artigo

O artigo afirmava que os desfechos em qualquer local mostravam que o efeito
"não é apenas uma troca mecânica de endereço". **Essa afirmação não sobrevive** e
foi removida. O resultado principal — homologação e presença ativa no mesmo
curso–CNES — não depende dessas escolhas e sobrevive a todas as correções
simultâneas.

### 3.4 A5 — o resultado de manchete depende da composição de cursos

Leave-one-curso-out no estudo de evento, exercício ausente dos artefatos:

```
todos os 10 cursos          : 0,500 (p = 0,033)
sem o curso 14              : 0,200 (p = 0,366)
so os 8 cursos 1:1 estritos : 0,121 (p = 0,608)
```

E "dez cursos com CBO unívoco" é falso para dois deles: o curso 14 é
`MULTIESPECIALIDADE_EXCLUSIVA` e o 16 é `FAMILIA_PATOLOGIA` na própria ponte.
"Unívoco" está sendo usado como "não compartilhado com outro curso", que é outra
coisa. A versão proporcional do mesmo achado é robusta a tudo (`log1p`: +0,068,
`p = 0,0002`; +0,057 com os 8 cursos estritos) e seria a forma defensável de
reportá-lo.

### 3.5 A5 — a significância depende do mês de referência

Contra a média dos doze meses pré, o efeito é +0,405 (EP 0,297, `p = 0,174`).
`202506`, a referência escolhida, é o ponto mais baixo do caminho pré.

## 4. Achados de severidade moderada

- **A4 — colapso de UF divergente do protocolo.** A3 manda colapsar UF com menos
  de cinco clusters *em região*; o código as junta num balde único `RESTO`,
  misturando quatro macrorregiões. O coeficiente de capital vai de **+0,2318**
  (executado) para **+0,3264** (protocolo) ou **+0,3358** (sem colapso). Dentro
  do balde há 32 células de capital contra uma única de interior remoto.
  Metropolitano e interior próximo são estáveis; o resultado principal sobrevive.
- **A4 — inferência anti-conservadora.** `G = 368` é nominal; a variância de
  `estrato_metropolitano` concentra 61,5% nos cinco maiores municípios, dando
  `G` efetivo ≈ 32. O wild cluster bootstrap exigido pelo A3 para subgrupos com
  `G < 30` nunca foi computado; computado agora, capital passa de `p = 0,007`
  para `p = 0,019`.
- **A4 — sobrecontrole no ajuste completo.** `log_pop` tem `R² = 0,493` contra as
  dummies de estrato e a faixa de bolsa cobre 61,0% do interior remoto e 0,0% das
  capitais. O "+19,8" não é o mesmo estimando melhor ajustado; é outro estimando.
- **A5 — correção de pequenas amostras ignora os FE absorvidos.** `k = 25` em vez
  de incluir os ~1.547 parâmetros absorvidos: `p` de 0,033 para 0,044.
- **A8 — insumo oficial inventariado nunca lido.** A planilha de alocados da
  segunda chamada mostra quatro dos controles alocados depois à célula que
  perderam. O contraste é mais próximo de *obter a vaga primeiro* do que de
  *obter a vaga*.
- **A1 — o portão não pode reprovar.** `vacancy_id_available = False` e
  `immediate_capacity_all_calls = False` são literais, não testes. `APROVADO_VAGA`
  e `REPROVADO` são inatingíveis por construção. As premissas são factualmente
  corretas, mas o JSON as publica em `criterios` como se tivessem sido testadas.

## 5. Achados de documentação

- `docs/06_execucao/32_sintese_A6...md` diz "primeiro ciclo … 30,3% das células".
  O 30,3% é da **primeira chamada**. Pelo ciclo 1 inteiro são 461/1.295 = 35,6%:
  68 células com desfecho zero na primeira chamada receberam homologado novo na
  segunda.
- `manifesto_tipologia_territorial.json`: a nota diz "1316 nacionais após remover
  27 capitais duplas". Só 25 das 27 capitais estão em RM/RIDE strict — Rio Branco
  e Campo Grande não estão. O correto é 1331 − 25 = **1306**, que é o que o
  parquet publica.
- `A4_relatorio_diagnostico.md` atribui a atenuação do ajuste completo a "UF e
  curso capturarem variação territorial". Impossível: ambos já estão no modelo
  mínimo. A atenuação vem inteiramente de `log_pop` (+0,2942 → +0,2155).
- A afirmação de que linhas sub judice são descartadas é falsa para o ciclo 1: o
  marcador existe na coluna 17 e nunca é lido. Numericamente imaterial.
- `A5_relatorio_diagnostico.md`: o bloco que monta o relatório completo é
  sobrescrito antes de ser escrito, então influência e robustez não aparecem no
  arquivo publicado.
- `A6_manifesto_reproducao.json` lista caminhos Windows, começa em A1 omitindo
  toda a aquisição, e não hasheia `A5_painel_T0.parquet`, que é o dataset de
  estimação.

## 6. Risco de garimpo retrospectivo em A8

Não há sinal de escolha de janela que maximize o efeito: `gap = 1` **não** é o
máximo para o desfecho substantivo (33,3 contra 35,1 em gap ≤ 2 e 36,0 em
qualquer gap), e a amostra de empates, que daria o maior efeito de todos
(+64,5/+43,4), foi explicitamente posta em quarentena. O protocolo se
autodeclara `pre_registro: false`.

O que merece atenção do parecerista não é a janela, e sim as escolhas de
**medida** da seção 3: elas empurram o contraste na mesma direção e nenhuma
estava documentada. Agora estão, no artigo e aqui.

## 7. Não verificado

- Autenticidade das planilhas contra as fontes oficiais (hashes conferem com o
  disco, não com o portal).
- Microdados do CNES: `output/aquisicao/cnes_mensal/` não existe no repositório,
  então a cadeia auditável de A5 começa no painel já integrado.
- Identidade candidato ↔ retrato nominal: o retrato tem CRM mas não CPF. O elo
  candidato ↔ homologados **é** corroborado por CPF mascarado, com zero
  divergência em 316/316, 270/270 e 360/360.
- Comparabilidade local em A8, que é intestável com dado público.
