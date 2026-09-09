# Roteiro narrativo da banca 1

> **Classificação:** decisão de comunicação, não de método<br>
> **Conteúdo dos slides:** [02_conteudo_slides.md](02_conteudo_slides.md)<br>
> **Atualização:** 9 de setembro de 2026

---

## 1. Arco da apresentação

Um único fio condutor: **um preço foi colocado sobre a vulnerabilidade
territorial, e ainda não se sabe se esse preço compra o preenchimento das vagas
que pretendia comprar.**

A banca 1 tem seis seções fixas. Cada seção ocupa quantos slides o argumento
pedir — a motivação, que tem mais a dizer, ocupa oito; as demais, um a quatro.

| Seção | Papel narrativo | Slides |
|---|---|:---:|
| — Capa e sumário | contrato com a banca | 1–2 |
| **1. Motivação** | em três blocos. **Problema:** especialistas existem, mas não no interior; nos municípios do programa já havia menos especialistas e menos colegas onde a bolsa seria maior; para o médico, "vulnerável" são quatro desvantagens concretas. **Política:** o que é o PMM-E — lei, quem participa, aprimoramento em serviço, 16 cursos, como a vaga chega, onde está — e a regra que faz o IVS virar bolsa. **Efeito incerto:** a evidência a favor de pagar mais, a evidência contra, e o que o primeiro ciclo mostrou | 3–10 |
| **2. Pergunta** | a pergunta, e a leitura em dois objetos: o preço e a desvantagem | 11 |
| **3. Literatura teórica** | as três tradições que o modelo junta e o que cada uma resolve | 12 |
| **4. Modelo microeconômico** | a decisão; o que a bolsa paga e o que não paga; o custo de estar ali; por que o IVS organiza o custo | 13–16 |
| **5. Hipóteses** | da condição de aceitação às duas hipóteses e à condição de degrau, em quatro passos | 17 |
| **6. Viabilidade empírica** | o que se consegue medir de cada peça, o que fica de fora, e por que separar bolsa de vulnerabilidade é difícil | 18 |

A seção 6 encerra a entrega: não há slide de perguntas. A margem tratada é o
**preenchimento** das vagas; permanência da oferta fica fora desta
apresentação, embora continue no escopo do projeto.

### 1.1 A lógica de cada bloco da motivação

O bloco **problema** vai do geral ao particular e termina no ponto de vista do
médico, porque é dele que a teoria parte. O retrato nacional (slide 3) diz que
a escassez é territorial, não numérica. Os dados do programa (slide 4) mostram
que a mesma coisa vale dentro dos 368 municípios que receberam vaga. O slide 5
traduz "município vulnerável" em quatro desvantagens que o médico enfrenta —
retaguarda, infraestrutura, distância da família, mercado privado — e diz quais
delas medimos. São essas quatro que reaparecem, formalizadas, nos slides 14 e 15.

O bloco **política** responde à pergunta que qualquer banca faz — "o que é
exatamente esse programa?" — antes de discutir a bolsa. O slide 6 resume o
edital: quem, o quê, como, onde. O slide 7 isola a única peça da política que
o trabalho estuda: a regra que transforma o índice em valor.

O bloco **efeito incerto** é a exceção declarada ao escopo teórico (seção 2.4).
Ele existe para justificar a pergunta, e por isso precisa mostrar que a
resposta não é óbvia: a evidência internacional diz que pagar mais funciona
(slide 8), mas que é caro, não move todo mundo e não segura ninguém (slide 9);
e o primeiro ciclo do PMM-E mostra que a faixa maior não veio com mais
preenchimento, enquanto o território ordenou o resultado (slide 10). Sem esse
bloco a pergunta pareceria retórica.

---

## 2. Regras de composição

### 2.1 Título é takeaway, seção é rastreio

Nenhum título nomeia a seção. O título carrega **a afirmação que o slide
sustenta**. A posição na apresentação fica em um elemento separado — no
markdown, a linha em `código` logo abaixo do título; no slide, uma faixa fina
fora do título.

Títulos dos slides 3 a 18 — curtos, declarativos e sem palavra difícil:

3. Especialistas não faltam; faltam no interior
4. Onde a bolsa é maior, já havia menos especialistas
5. O que o médico vê ao decidir
6. O que é o PMM-E
7. A bolsa remunera o lugar
8. Pagar mais funciona: a evidência a favor
9. Mas é caro, e não segura: a evidência contra
10. No primeiro ciclo, a bolsa maior não ordenou o preenchimento
11. Pergunta
12. De onde vem o modelo
13. Como o médico escolhe onde trabalhar
14. O que a bolsa paga — e o que não paga
15. O custo de estar ali
16. O IVS organiza o custo
17. Duas hipóteses
18. Viabilidade empírica

### 2.2 Uma afirmação por slide

Slide com mais de uma figura só quando todas sustentam **a mesma** afirmação. O
slide 4 tem duas figuras — oferta por habitante e colegas por município —
porque as duas dizem que, onde a bolsa seria maior, já havia menos
especialistas. O slide 10 tem uma figura em dois painéis porque o contraste
entre faixa e território é a afirmação.

### 2.3 Fontes, não notas

Todo número exibido traz a fonte no próprio slide. Não há notas de apresentador
nem justificativas no documento de conteúdo: o que precisa ser dito está no
slide ou não está. Manchetes entram como citação textual com veículo e data, e
não como imagem de recorte.

### 2.4 A banca 1 é teórica

Fora da motivação, **nada de econometria**. Não entram estimador,
especificação, regressão, coeficiente, elasticidade, colinearidade, desenho de
identificação nem o vocabulário de descontinuidade. Literatura empírica também
não: o slide 12 traz apenas trabalhos teóricos.

A motivação é a exceção declarada. Ali, antes da pergunta, entra evidência sobre
o que se pode esperar da política — inclusive de trabalhos empíricos de outros
países — porque é o que justifica perguntar. Mesmo ali, o desenho de cada estudo
é descrito em palavras comuns: "sorteou o salário anunciado", e não "RCT com
randomização em dois estágios". O slide 10 mostra proporções brutas e diz que
são descrição, não efeito.

A viabilidade empírica descreve **o que se consegue medir**, não como se
estimaria. A dificuldade de separar bolsa de vulnerabilidade é apresentada como
fato sobre os dados — não existe município com bolsa alta e vulnerabilidade
baixa — sem nomear estimadores.

### 2.5 Vocabulário

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
| 1 | **Títulos: só o takeaway, não o nome da seção (tracking separado)** | Todos os títulos eram rótulos de seção com numeral romano. Cada slide recebeu título em frase completa com a afirmação que sustenta; o nome da seção e a posição foram para o rastreio, fora do título. |
| 2 | **Motivação: dividir entre (i) dor, (ii) política, (iii) efeitos** | O painel 2×2 repetido em dois slides virou três blocos em sequência causal — problema (slides 3 a 5), política (6 e 7) e efeito incerto (8 a 10) — cada um com os slides que o argumento pede. |
| 3 | **Pergunta: simplificar** | De *"Bolsas maiores conseguem compensar as desvantagens territoriais no preenchimento e na manutenção das vagas do PMM-E?"* para **"Maiores bolsas do PMM-E para municípios mais vulneráveis compensam suas desvantagens territoriais na atração de médicos especialistas?"**, com a leitura em dois objetos logo abaixo. |
| 4 | **Teoria: derivar hipóteses diretamente** | O bloco teórico termina em um slide que escreve a condição de aceitação e dela tira as duas hipóteses como derivadas parciais — remuneração real com sinal positivo, custo locacional com sinal negativo — e as junta na condição de degrau. |

## 4. Ajustes de conteúdo de 09/09/2026

Quatro rodadas de revisão do autor sobre a versão em markdown.

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

### Terceira rodada

| Alvo | Ajuste |
|---|---|
| títulos | simplificados: "Três primitivas teóricas" virou "De onde vem o modelo"; "A decisão locacional do médico" virou "Como o médico escolhe onde trabalhar" |
| escopo | a banca 1 é teórica. Literatura empírica sai do slide de literatura; qualquer referência a econometria ou estimação sai de todos os slides, exceto na motivação |
| evidência | reescrita como narrativa em três movimentos — funciona, é caro, não segura — no lugar da tabela de estudos. Desenhos descritos em palavras comuns |
| literatura | **Reinhardt removido**. Choné & Ma já colocam equipe e capital no custo de atender; o que Reinhardt acrescentaria é que esses insumos também elevam o benefício produzido, mas essa extensão é do projeto, não dele. Some-se a isso que a equação verificável é do artigo de 1972, não do livro de 1975 que o projeto cita. Mantido como referência secundária em `modelo_micro.md` |
| custo | a extensão $B(q; L, K)$ passa a ser creditada ao projeto, não a Reinhardt |
| viabilidade | reescrita sem vocabulário econométrico: passa a perguntar se há como medir cada peça do modelo, e declara as duas que ficam de fora |

### Quarta rodada

Reorganização da apresentação nas **seis seções da banca 1** — o sumário em
"Parte I/II/III" estava errado — e aprofundamento de conteúdo em cada seção.
De 11 para 18 slides.

| Seção | Ajuste |
|---|---|
| sumário | as seis seções, sem partes |
| motivação · problema | ganha um slide de abertura com o retrato nacional — Demografia Médica 2025 e manchetes — antes dos dados do programa; o slide das desvantagens na visão do médico passa a ter tabela própria, com o que cada uma significa e se a medimos, e três evidências da literatura sobre o peso de cada uma (Moehling; Costa, Nunes & Sanches; Scott et al.). Não há depoimentos verificáveis de médicos; usou-se a evidência de pesquisa |
| motivação · política | ganha o slide "O que é o PMM-E", que faltava: lei, objetivo, quem participa, formato do aprimoramento em serviço, os 16 cursos em dois grupos, como a vaga chega ao médico, onde estão as vagas do ciclo 1. O edital de 2025 passa a estar no repositório em texto integral |
| motivação · efeito incerto | a narrativa "funciona / é caro / não segura" é dividida em **a favor** e **contra**, cada um em seu slide; o fato descritivo do ciclo 1 ganha slide próprio com figura em dois painéis, por faixa e por estrato territorial |
| pergunta | acrescida da leitura em dois objetos — preço e desvantagem — e da margem observada |
| literatura | ganha parágrafo dizendo o que cada tradição resolve e uma linha sobre o que nenhuma trata |
| modelo | de 2 para 4 slides: entram "O que a bolsa paga — e o que não paga", que desenvolve $w = B + w^{\text{priv}}$ e o deflator, e "O IVS organiza o custo", que traz a correspondência entre as três dimensões do índice e os blocos do custo e o sinal ambíguo de $c_0'(IVS)$ — o argumento que justifica estudar o degrau |
| hipóteses | derivação escrita em quatro passos numerados |
| viabilidade | custo de vida e distância da família entram na tabela; fecha com o primeiro passo do trabalho empírico |

## 5. Defeitos do material anterior

Encontrados no `PEE__Modelo_econômico.pptx` recebido em 09/09/2026.

| Defeito | Tratamento |
|---|---|
| Slide de literatura com economia do crime — Becker, Ehrlich, Fella & Gallipoli, Bennett & Ouazad, Dix-Carneiro et al., Deshpande & Mueller-Smith | substituído pela literatura teórica do projeto |
| Função utilidade com nove marcadores `X` e equações vazias | reescrita a partir do modelo canônico |
| Painel de motivação duplicado em dois slides | desmembrado em três blocos |
| Placeholder de master visível no sumário | eliminado |
| Blocos sem conteúdo (modelo teórico, viabilidade, perguntas) | preenchidos |
| Gráfico de participação regional com valores não reprodutíveis | substituído por especialistas por habitante, gerados por script |
| Gráfico de especialistas por UF montado à mão a partir da Demografia Médica | substituído pelos dois extremos citados em texto, com fonte, e pelos dados do programa gerados por script |

---

## 6. Tempo estimado

| Seção | Slides | Minutos |
|---|:---:|:---:|
| Capa e sumário | 2 | 1 |
| 1. Motivação | 8 | 11 |
| 2. Pergunta | 1 | 1 |
| 3. Literatura teórica | 1 | 2 |
| 4. Modelo microeconômico | 4 | 8 |
| 5. Hipóteses | 1 | 3 |
| 6. Viabilidade empírica | 1 | 2 |
| **Total** | **18** | **28** |
