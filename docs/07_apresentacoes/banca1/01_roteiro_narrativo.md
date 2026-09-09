# Roteiro narrativo da banca 1

> **Classificação:** decisão de comunicação, não de método<br>
> **Conteúdo dos slides:** [02_conteudo_slides.md](02_conteudo_slides.md)<br>
> **Atualização:** 9 de setembro de 2026

---

## 1. Arco da apresentação

Um único fio condutor: **um preço foi colocado sobre a vulnerabilidade
territorial, e ainda não se sabe se esse preço compra o preenchimento das vagas
que pretendia comprar.**

| Parte | Conteúdo | Papel narrativo | Slides |
|:---:|---|---|:---:|
| — | Capa e sumário | contrato com a banca | 1–2 |
| **1** | Motivação e pergunta | há um problema territorial, há uma política que coloca preço sobre ele, os primeiros efeitos observados não ordenam pelo preço; disso sai uma pergunta única | 3–6 |
| **2** | Literatura teórica, modelo microeconômico e hipóteses | de onde vêm as primitivas, a condição que governa a decisão do médico, e as duas hipóteses que saem dela por derivação | 7–10 |
| **3** | Viabilidade empírica | o que temos, o que dá para medir hoje e qual é o desafio de identificação | 11 |
| — | Encerramento | perguntas | 12 |

A banca 1 cobre a margem **preenchimento**. Permanência da oferta fica fora
desta apresentação, embora continue no escopo do projeto.

---

## 2. Regras de composição

### 2.1 Título é takeaway, seção é rastreio

Nenhum título nomeia a seção. O título carrega **a afirmação que o slide
sustenta**. A posição na apresentação fica em um elemento separado — no
markdown, a linha em `código` logo abaixo do título; no slide, uma faixa fina
fora do título.

Sequência de títulos dos slides 3 a 11. Lidos em ordem, são o argumento inteiro:

1. A escassez de especialistas é territorial — e já é tratada como urgência sanitária.
2. O programa responde com um preço explícito pela vulnerabilidade do município.
3. Depois da oferta a presença de especialistas cresceu em todas as faixas, mas só 30% das vagas tiveram confirmação — e a bolsa maior não ordenou o preenchimento.
4. Bolsa maior compensa município pior no preenchimento das vagas?
5. O modelo combina três primitivas da literatura teórica.
6. O médico aceita a vaga quando a remuneração real supera o custo de estar ali.
7. O custo de estar ali tem duas partes, e a infraestrutura entra nas duas.
8. Da condição de aceitação saem duas hipóteses: remuneração atrai, custo repele.
9. Os dados são públicos; o desafio empírico é separar bolsa de vulnerabilidade, que a regra amarra.

### 2.2 Uma afirmação por slide

Slide com mais de uma figura só quando todas sustentam **a mesma** afirmação. O
slide 3 tem três elementos visuais — manchetes, gradiente por faixa e distância
— porque os três dizem que a escassez é territorial.

### 2.3 Fontes, não notas

Todo número exibido traz a fonte no próprio slide. Não há notas de apresentador
nem justificativas no documento de conteúdo: o que precisa ser dito está no
slide ou não está.

### 2.4 Vocabulário

| Não dizer | Dizer |
|---|---|
| efeito do PMM-E, efeito da bolsa | associação; gradiente; evolução observada |
| efeito da vulnerabilidade | gradiente de vulnerabilidade |
| vaga preenchida | célula com alguma confirmação ou homologação |
| especialistas do município | presença cadastral no CNES nos CBOs do programa |

---

## 3. Rastreio do feedback dos professores

| # | Feedback | Ajuste aplicado |
|---|---|---|
| 1 | **Títulos: só o takeaway, não o nome da seção (tracking separado)** | Todos os títulos eram rótulos de seção com numeral romano. Cada slide recebeu título em frase completa com a afirmação que sustenta; o nome da parte e a posição foram para o rastreio, fora do título. |
| 2 | **Motivação: dividir entre (i) dor, (ii) política, (iii) efeitos** | O painel 2×2 repetido em dois slides virou três slides em sequência causal: o problema (slide 3), a política que responde a ele (slide 4) e o que se observa depois dela (slide 5). |
| 3 | **Pergunta: simplificar** | De *"Bolsas maiores conseguem compensar as desvantagens territoriais no preenchimento e na manutenção das vagas do PMM-E?"* para **"Bolsa maior compensa município pior no preenchimento das vagas?"**, com a leitura em termos do modelo em uma linha. |
| 4 | **Teoria: derivar hipóteses diretamente** | O bloco teórico termina em um slide que escreve a condição de aceitação e dela tira as duas hipóteses como derivadas parciais — remuneração real com sinal positivo, custo locacional com sinal negativo — e as junta na condição de degrau. |

## 4. Ajustes de conteúdo de 09/09/2026

Decisões do autor sobre a primeira versão do conteúdo em markdown.

| Slide | Ajuste |
|---|---|
| 1 | título formal e completo, nomeando os dois objetos das hipóteses — incentivos e custos territoriais — e o programa |
| 2 | sumário só com os títulos das três partes |
| 3 | manchetes e medidas do problema no mesmo slide; o gráfico por UF de fonte externa foi substituído pelo gradiente de especialistas por habitante por faixa de bolsa, calculado do CNES e do Censo 2022 — mesma unidade e mesma dimensão da política |
| 4 | explicação de onde vem a vulnerabilidade declarada: IVS, dimensões, cortes do Ipea e conversão em faixa; retirada a frase sobre "o dobro" e "degrau de R$ 5 mil" |
| 5 | efeitos observados em **especialistas por habitante, antes e depois**, por faixa, no lugar da participação regional; acrescentada a taxa de confirmação por faixa do quadro de vagas |
| 6 | retirado o bloco "o que a pergunta não é" |
| 7 | apenas literatura teórica; colunas simples; coluna com a equação original de cada trabalho |
| 8 | a leitura do termo de remuneração inclui o mercado local: a bolsa precisa compensar também a renda privada perdida |
| 9 | os dois parágrafos após a tabela foram fundidos; figura do custo laboral incluída |
| 10 | hipóteses reduzidas a duas — remuneração e custo — sobre preenchimento apenas, com a leitura de como cada objeto aparece nos dados |
| 11 | viabilidade em um único slide, simples e geral |
| todos | retiradas as notas de apresentador e as fontes que apontavam para documentos internos; ficaram apenas as fontes dos dados exibidos |

---

## 5. Defeitos do material anterior

Encontrados no `PEE__Modelo_econômico.pptx` recebido em 09/09/2026.

| Defeito | Tratamento |
|---|---|
| Slide de literatura com economia do crime — Becker, Ehrlich, Fella & Gallipoli, Bennett & Ouazad, Dix-Carneiro et al., Deshpande & Mueller-Smith | substituído pela literatura teórica do projeto |
| Função utilidade com nove marcadores `X` e equações vazias | reescrita a partir do modelo canônico |
| Painel de motivação duplicado em dois slides | desmembrado em três slides |
| Placeholder de master visível no sumário | eliminado |
| Blocos sem conteúdo (modelo teórico, viabilidade, perguntas) | preenchidos |
| Gráfico de participação regional com valores não reprodutíveis | substituído por especialistas por habitante, gerados por script |

---

## 6. Tempo estimado

| Parte | Slides | Minutos |
|---|:---:|:---:|
| Capa e sumário | 2 | 1 |
| 1. Motivação e pergunta | 4 | 7 |
| 2. Literatura teórica, modelo e hipóteses | 4 | 10 |
| 3. Viabilidade empírica | 1 | 2 |
| Encerramento | 1 | — |
| **Total** | **12** | **20** |
