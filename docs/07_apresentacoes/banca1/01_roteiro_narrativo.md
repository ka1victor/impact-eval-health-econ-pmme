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
|---|---|---|:---:|
| — | Capa e sumário | contrato com a banca | 1–2 |
| **I — Introdução** | Motivação, Pergunta | o município vulnerável chega com desvantagens que o médico enfrenta; a política responde com preço; a literatura diz que preço move alocação, mas é caro e não segura ninguém; disso sai a pergunta | 3–6 |
| **II — Teoria** | Literatura teórica, Modelo microeconômico, Hipóteses | as três primitivas, a condição de aceitação, e as duas hipóteses que saem dela por derivação | 7–10 |
| **III — Empiria** | Viabilidade empírica | como cada hipótese aparece nos dados e por que separá-las é difícil | 11 |

A Parte III encerra a entrega: não há slide de perguntas. A margem tratada é o
**preenchimento** das vagas; permanência da oferta fica fora desta
apresentação, embora continue no escopo do projeto.

---

## 2. Regras de composição

### 2.1 Título é takeaway, seção é rastreio

Nenhum título nomeia a seção. O título carrega **a afirmação que o slide
sustenta**. A posição na apresentação fica em um elemento separado — no
markdown, a linha em `código` logo abaixo do título; no slide, uma faixa fina
fora do título.

Títulos dos slides 3 a 11, curtos e declarativos:

3. Faltam especialistas justamente onde trabalhar é mais difícil
4. O PMM-E paga mais onde a vulnerabilidade é maior
5. Pagar mais funciona?
6. Pergunta
7. Três primitivas teóricas
8. A decisão locacional do médico
9. O custo de estar ali
10. Duas hipóteses
11. Viabilidade empírica

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

Duas rodadas de revisão do autor sobre a versão em markdown.

### Primeira rodada

| Slide | Ajuste |
|---|---|
| capa | título formal nomeando o objeto teórico e o programa |
| sumário | apenas os títulos das partes |
| motivação | dividida em problema, política e efeitos |
| pergunta | retirado o bloco "o que a pergunta não é" |
| literatura | apenas teórica, com a equação original de cada trabalho |
| modelo | o termo de remuneração passou a incluir o mercado local |
| hipóteses | reduzidas a duas, sobre preenchimento apenas |
| todos | retiradas as notas de apresentador e as fontes internas; ficaram as fontes dos dados exibidos |

### Segunda rodada

| Slide | Ajuste |
|---|---|
| 1 | título passa a "Desvantagens territoriais na escolha locacional de médicos especialistas" |
| 2 | sumário nas três partes nomeadas: Introdução, Teoria, Empiria |
| 3 | passa a explicar **o que são as desvantagens territoriais na visão do médico**. Entra o gráfico de retaguarda profissional, do CNES: quantos colegas da mesma especialidade o médico encontraria. Sai o gráfico de deslocamento por região — mede custo do paciente, não do médico, e reduzir deslocamento **não é objetivo declarado do edital**, que fixa provimento, fixação, equilíbrio territorial e formação (Portaria GM/MS nº 7.177/2025); fluxo de usuários aparece apenas como um entre vários critérios de priorização de vagas |
| 4 | explicação em três passos de como o índice vira valor: IVS, categoria do Ipea, faixa do edital; texto enxugado |
| 5 | refeito por inteiro. Deixa de mostrar a evolução da oferta antes e depois — sem grupo de comparação, era difícil de ler como efeito — e passa a trazer **evidência externa sobre se esse tipo de política funciona**: quatro estudos, a régua do prêmio compensatório e o fato descritivo de que no PMM-E a faixa maior não ordenou o preenchimento |
| 6 | pergunta na formulação do autor |
| 7 | retirada a coluna "o que entra no nosso modelo"; Choné & Ma e Reinhardt passam a ter cada um sua equação original, em linhas separadas; equações corrigidas para renderizar dentro de tabela |
| 10 | a tabela de como cada objeto aparece nos dados sai daqui |
| 11 | e entra aqui, condensada e ligada a H1 e H2, junto com o desafio de identificação |
| 12 | slide de perguntas eliminado: a apresentação termina na viabilidade empírica |

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
| I — Introdução | 4 | 8 |
| II — Teoria | 4 | 9 |
| III — Empiria | 1 | 2 |
| **Total** | **11** | **20** |
