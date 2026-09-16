---
documento: Conteúdo da apresentação — banca 1
papel: fonte de verdade do que vai à tela
escopo: teórico, termina na viabilidade empírica; sem resultado de estimação
slides: 16
atualizacao: 16 de setembro de 2026
---

> [!IMPORTANT]
> **Como ler este arquivo.** O deck começa e termina nos comentários
> `deck:inicio` e `deck:fim`, invisíveis na renderização. Entre eles, **cada
> cabeçalho é um slide, e só os cabeçalhos são slides**:
>
> | Nível | Layout | Uso |
> |:---:|---|---|
> | `#` | capa | capa da apresentação e as três divisórias de seção |
> | `##` | conteúdo | os doze slides de conteúdo |
>
> Abaixo de cada cabeçalho, a linha em `código` é o **rastreio** que aparece no
> rodapé, no formato `Seção · Rótulo do roteiro`. Os rótulos são os do roteiro
> acordado (Problema, Política, Efeitos, …) e os títulos são as manchetes que
> vão à tela.
>
> Os decks em [`deck_beamer/`](deck_beamer/) e [`deck_slidev/`](deck_slidev/)
> são **derivados** deste arquivo: divergência entre deck e documento é erro do
> deck. Em 16/09/2026 os decks ainda estão na estrutura anterior, de 15 slides —
> divergência conhecida e datada, a resolver na próxima reconstrução.

## Mapa da apresentação

| # | Layout | Seção | Rótulo do roteiro | Título na tela |
|:---:|:---:|---|---|---|
| 1 | capa | — | — | Capa |
| 2 | conteúdo | — | Sumário | Sumário |
| 3 | capa | 1 | — | **Motivação e Pergunta** |
| 4 | conteúdo | 1 | Problema | O especialista está longe do interior — e quase nunca é só do SUS |
| 5 | conteúdo | 1 | Política | A bolsa é do município, não do médico nem da especialidade |
| 6 | conteúdo | 1 | Efeitos | O programa já deu sinais; a literatura aponta para os dois lados |
| 7 | conteúdo | 1 | Pergunta de Pesquisa | A pergunta que organiza o trabalho |
| 8 | capa | 2 | — | **Literatura Teórica e Modelo Microeconômico** |
| 9 | conteúdo | 2 | Visão geral | A escolha locacional maximiza a renda real líquida |
| 10 | conteúdo | 2 | Custo da localidade | O custo da localidade tem duas metades: o lugar e o trabalho |
| 11 | conteúdo | 2 | Remuneração da localidade | A bolsa não é toda a remuneração da localidade |
| 12 | capa | 3 | — | **Hipótese e Viabilidade Empírica** |
| 13 | conteúdo | 3 | Implicações para o PMM-E | No PMM-E, a regra fixa a remuneração e o IVS organiza o custo |
| 14 | conteúdo | 3 | Hipótese do trabalho | Da condição de aceitação sai a hipótese |
| 15 | conteúdo | 3 | Disponibilidade de dados | Há dado para quase todo termo — e sabemos quais faltam |
| 16 | conteúdo | 3 | Desafio metodológico | Separar o efeito da bolsa do efeito da vulnerabilidade |

---

<!-- deck:inicio -->

# Remuneração como incentivo limitado

### Um modelo de escolha racional para o Programa Mais Médicos Especialistas

**Grupo 2** · Bernardo Gomes · Bruno Manta · Felipe Barros · Felipe Marques ·
Gabriel Benegra · Kauã Santos · Vinicius Sbruzzi

`sem rastreio`

> [!NOTE]
> **Decisão pendente sobre o título.** "Incentivo limitado" antecipa uma
> conclusão que esta banca não entrega: a apresentação termina na viabilidade
> empírica, sem estimação. Alternativa neutra, se a banca preferir:
> *"Quanto vale o lugar? Um modelo de escolha locacional para o PMM-E"*.
> Mantido o título do grupo até decisão do autor.

---

## Sumário

`sem rastreio`

1. **Motivação e Pergunta** — o problema, a política, os efeitos já observados e a pergunta
2. **Literatura Teórica e Modelo Microeconômico** — a equação de escolha, o custo e a remuneração do lugar
3. **Hipótese e Viabilidade Empírica** — o que o modelo implica, o que se testa, o que os dados permitem

> [!TIP]
> **Mudança em relação ao deck atual.** O sumário aparece **uma vez**. As
> divisórias de seção (slides 3, 8 e 12) substituem as quatro repetições do
> sumário do deck anterior, que custavam quatro slides e nenhum argumento.

---

# 1. Motivação e Pergunta

### Por que a pergunta importa, o que o programa faz e o que já se sabe

`sem rastreio`

---

## O especialista está longe do interior — e quase nunca é só do SUS

`1. Motivação e Pergunta · Problema`

### O retrato

O Brasil tinha, em 2024, **353 mil médicos especialistas** — 59% dos 597 mil
médicos do país. O problema não é o número, é a distribuição: **55,4%** estão no
**Sudeste** e **5,9%** no **Norte**; são **453** especialistas por 100 mil
habitantes no **Distrito Federal** e **68** no **Maranhão**. A contrapartida
está no deslocamento: para serviços de alta complexidade, a população do
**Norte** percorre em média **276 km**, contra **101 km** no **Sul**
— números herdados do deck do grupo, com **fonte primária ainda não
confirmada** (pendência 2).

| Figura na tela | O que mostra | Estado |
|---|---|---|
| **I. A escassez é territorial** | especialistas por 100 mil habitantes, por UF, 2024 — de 453 no DF a 68 no MA | do deck atual do grupo; **falta gerar por script** (pendência 1) |
| **II. O acesso exige distância** | deslocamento médio da população para serviços de alta complexidade, em km, por região | do deck atual do grupo; **falta gerar por script e confirmar a fonte** (pendências 1 e 2) |

### E o ponto que faltava: o SUS divide o especialista com o setor privado

Dedicação exclusiva ao SUS é **rara**. No único recorte setorial da *Demografia
Médica no Brasil 2025* — um inquérito com **1.544 cirurgiões**:

| Onde o cirurgião atua | Participação |
|---|---:|
| Dupla prática, público **e** privado | **72,4%** |
| Exclusivamente no setor privado | **19,9%** |
| Exclusivamente no setor público ou com pacientes do SUS | **7,7%** |

Ou seja: o SUS não compra a carreira de um especialista, compra **uma fração
dela** — e disputa o resto com o mercado privado local. É essa fração que o
PMM-E tenta comprar com **20 horas semanais**, e é por isso que o mercado local
volta ao argumento no slide 11.

> [!WARNING]
> **O que não dá para dizer.** A frase corrente "apenas 10% dos especialistas
> atendem no SUS" **não se sustenta**: ela vem de fala do ministro da Saúde em
> debate no Senado (24/09/2025), sem metodologia publicada, e é contradita pela
> fonte primária — somando dupla prática e exclusivos do público, **80,1%** dos
> cirurgiões atendem SUS. O defensável é o inverso: **exclusividade** ao SUS é
> que é rara. O dado **por especialidade não existe** em fonte pública: o estudo
> só o reporta para cirurgiões, e por amostra de associados do Colégio
> Brasileiro de Cirurgiões, não por censo.

### Quais especialistas

O PMM-E oferta **16 cursos** — **6 cirúrgicos** e **10 ambulatoriais**. O peso
está em **diagnóstico** e **oncologia**: os três maiores em oferta no ciclo 1
são **endoscopia digestiva alta** (188 células estabelecimento–curso),
**colonoscopia** (164) e **anestesiologia perioperatória** (147), e **6 dos 16**
títulos citam oncologia, tumores ou câncer. O edital declara foco *"na redução
do tempo de espera, na ampliação do diagnóstico precoce e no fortalecimento das
redes de atenção especializada"*.

Nada disso se resolve sozinho: em 2025 o Ministério da Saúde reconheceu
**situação de urgência em saúde pública**, por **24 meses**, em razão do tempo
de espera na atenção especializada — e lançou o **Agora Tem Especialistas**, do
qual o PMM-E é o braço de provimento.

**Fontes:** Scheffer, M. et al., *Demografia Médica no Brasil 2025* (FMUSP/AMB),
dados de dez/2024 — cap. 11 e cap. 13, Figura 1, p. 254; deslocamento médio:
origem provável na REGIC 2018 (IBGE), **a confirmar**; Portaria GM/MS nº
7.061/2025; Edital SGTES/MS nº 3/2025, itens 1.2.1 e Tabela 3;
`output/aquisicao/quadro_vagas_tratamento.parquet`.

---

## A bolsa é do município, não do médico nem da especialidade

`1. Motivação e Pergunta · Política`

### O que é o PMM-E

A **Lei nº 15.233/2025** criou o Projeto Mais Médicos Especialistas dentro do
Programa Mais Médicos, *"destinado ao provimento de profissionais com vistas à
redução no tempo de espera de atendimento ao usuário do SUS, nas regiões
prioritárias"*. Não é concurso nem emprego: o médico com **RQE** na área da vaga
recebe **bolsa-formação** mensal do Ministério, **sem vínculo**, por até **12
meses**, em **aprimoramento em serviço** de **20 horas semanais** num
estabelecimento do SUS. No **ciclo 1** (julho de 2025) foram **1.295 vagas**
estabelecimento–curso, em **460 estabelecimentos** e **368 municípios**, em todas
as UFs.

### O que determina a remuneração oferecida

O valor **não** depende da especialidade, do curso, do estabelecimento, da
produção, do desempenho nem do médico. A carga é fixa em 20 horas. Depende de
**uma coisa só: o município**. No quadro de vagas do ciclo 1, **nenhum**
município e **nenhuma** célula município–curso aparece com mais de uma faixa.

O edital fixa o valor em **duas cláusulas que não dizem a mesma coisa**:

| Cláusula | O que diz | Situação |
|---|---|---|
| **11.1.4** | grade de três faixas pela **categoria de IVS 2010 do Ipea** — índice que resume, de 0 a 1, dezesseis indicadores do Censo 2010 em infraestrutura urbana, capital humano e renda e trabalho: categoria muito alta → **R$ 20.000**, alta → **R$ 15.000**, média, baixa ou muito baixa → **R$ 10.000** | pública e reproduzível |
| **11.1.3** | o valor segue *"critérios de **localização e vulnerabilidade** definidos de acordo com a faixa de atração definida no **Anexo IV**"* | o Anexo IV **não é público** |

![Valor mensal da bolsa-formação por faixa de atração](../../../output/apresentacao_banca1/bolsa_por_faixa.png)

**São dois critérios, e só um é público.** O dado tem a forma disso: em **177
dos 368** municípios a faixa publicada não é a que a categoria de IVS manda, e a
divergência tem **uma direção só** — **zero** municípios abaixo do que a
categoria determina, **177 acima**. Erro de medida erraria nos dois sentidos.
**O IVS é o piso da bolsa, não o critério dela**; o critério de localização
promove 48% dos municípios acima desse piso.

Duas notas que mudam o valor de bolso e costumam passar batido: incide
**contribuição previdenciária** como contribuinte individual (item 11.2); e o
**adicional** para Amazônia Legal, territórios indígenas e alta vulnerabilidade
existe na **Lei** (art. 22-D, §4º) mas **não foi regulamentado** no ciclo 1 — o
quadro de vagas tem um único campo de remuneração, a faixa de atração.

### Onde a regra manda o dinheiro

![Especialistas por 100 mil habitantes, jun/2025 — 15,0 na Faixa 3, 14,4 na Faixa 2, 18,3 na Faixa 1](../../../output/apresentacao_banca1/oferta_pre_por_faixa.png)
![Colegas da mesma especialidade no município, jun/2025 — mediana de 6,5, 5,0 e 2,5 da Faixa 3 à Faixa 1](../../../output/apresentacao_banca1/retaguarda_por_faixa.png)

As duas medidas **discordam**, e é a discordância que importa. **Por habitante**,
a bolsa maior não vai para onde falta mais: vai para municípios pequenos, onde
poucos profissionais já produzem taxa alta. **Em número de colegas, vai**: da
Faixa 3 à Faixa 1 a mediana cai de 6,5 para 2,5, e a chance de o especialista
ser o único ou ter um só colega sobe de 12% para 31%. O que a Faixa 1 compensa é
**isolamento profissional**, não cobertura populacional.

### A teoria da mudança que o desenho oficial supõe

```mermaid
flowchart LR
    A("Regra de valor<br/>faixa de atração<br/>R$ 10 / 15 / 20 mil") -. suposição .-> B("Decisão<br/>do médico")
    B -. suposição .-> C("Preenchimento<br/>da vaga")
    C --> D("Oferta de especialista<br/>no município")
    D -. suposição .-> E("Produção<br/>assistencial")
    E --> F("Redução do tempo<br/>de espera")

    classDef escrito fill:#e6f4ea,stroke:#1e7e34,stroke-width:2px,color:#14532d
    classDef suposto fill:#fff4e5,stroke:#c77700,stroke-width:2px,color:#7a4b00
    class A,D,F escrito
    class B,C,E suposto
```

| | Leitura |
|---|---|
| **Caixa verde** | o ato oficial nomeia esse elemento: a regra de valor (itens 11.1.3 e 11.1.4), o provimento como finalidade (art. 22-D e item 1.1.2) e a redução da espera como objetivo último (art. 22-D e itens 1.2.1 e 1.2.5.V) |
| **Caixa laranja** | nenhum ato o nomeia; é o mecanismo que o programa supõe |
| **Seta cheia** | ligação afirmada em ato oficial, ainda que só como finalidade |
| **Seta tracejada** | ligação que **nenhum documento oficial afirma** |

**Os três elos supostos.** Nenhum ato diz que **o valor da bolsa muda a escolha
de local**, nem que bolsa maior gera mais preenchimento, nem que presença
cadastral vira produção adicional. O desenho justapõe o instrumento e a
finalidade sem enunciar o mecanismo no meio. Uma ressalva do lado escrito: nem
mesmo o elo "preenchimento → oferta" assegura **oferta líquida** — o bolsista
cumpre 20 horas e não tem vínculo, e o edital apenas **veda substituição** de
profissional já vinculado.

> [!NOTE]
> **É aí que este trabalho entra.** A banca 1 para no terceiro elo — o
> **preenchimento**. O primeiro elo suposto é justamente a hipótese que vamos
> testar.

**Fontes:** Lei nº 15.233/2025, art. 21 (art. 22-D da Lei nº 12.871/2013);
Edital SGTES/MS nº 3/2025 (DOU 24/07/2025), itens 1.1, 1.2.1, 1.2.5, 11.1 a
11.4 e Tabela 3; Ipea, *Atlas da Vulnerabilidade Social* (2015);
`output/aquisicao/quadro_vagas_tratamento.parquet`; CNES 06/2025 e Censo 2022
(IBGE). Figuras geradas por `scripts/apresentacao/gerar_figuras_banca1.py`.

---

## O programa já deu sinais; a literatura aponta para os dois lados

`1. Motivação e Pergunta · Efeitos`

### O que o ciclo 1 mostra

Das **1.295 vagas** da primeira chamada, **393 (30,3%)** tiveram alguém
confirmado ou homologado.

![Preenchimento do ciclo 1 — por faixa: 23,6% na Faixa 3, 37,4% na Faixa 2, 31,6% na Faixa 1; por território: 44,9% metropolitano, 35,6% capitais, 26,9% interior conectado, 20,5% interior remoto](../../../output/apresentacao_banca1/preenchimento_ciclo1.png)

- **Por faixa de bolsa, não há ordem.** Pagar o dobro (Faixa 1, 31,6%) não
  preencheu mais do que pagar uma vez e meia (Faixa 2, 37,4%).
- **Por território, há.** O preenchimento cai do metropolitano (44,9%) e das
  capitais (35,6%) para o interior ligado a um polo (26,9%) e é menor no
  interior remoto (20,5%). Ajustado, o metropolitano fica **+20,9 p.p.** acima
  do interior remoto.
- **O estoque cadastrado se move.** Em mar/2026, as células com atração têm
  **+0,50 especialista** cadastrado no CNES em relação a jun/2025 (erro padrão
  0,234), sem pré-tendência detectável.

> [!CAUTION]
> **Isto é descrição, não efeito.** As faixas diferem em muito mais do que na
> bolsa, e território prevê o desfecho melhor do que ela. A linguagem correta é
> **gradiente** e **associação**. Nenhum destes números é efeito causal do
> PMM-E, e o slide 16 explica por quê.

> [!NOTE]
> **Sobre o gráfico de série mensal do deck atual.** A série de especialistas
> por 100 mil habitantes por faixa, de 07/24 a 07/26, **é reprodutível**: o
> manifesto termina em 22,0 na Faixa 1, 18,0 na Faixa 3 e 16,2 na Faixa 2, e ela
> pode entrar como contexto descritivo. A **tabela de inclinações pré/pós** que a
> acompanha, não: os coeficientes não têm origem rastreável em `output/` e não se
> reproduzem por mínimos quadrados sobre a própria série. Além disso, um
> contraste antes-depois **sem grupo de comparação** não se lê como efeito do
> programa. Ela fica fora.

### A literatura aponta para os dois lados

| Pagar mais funciona | Pagar mais não basta — ou não fica |
|---|---|
| **México: o salário foi sorteado.** Um concurso real distribuiu **106 postos** em municípios pobres e anunciou, **ao acaso**, dois salários. Onde o salário era **33% maior**, a aceitação subiu **15 p.p.**; a mais de 200 km da cidade natal, foi de 25% para cerca de **80%** — sem atrair candidatos menos qualificados. | **Brasil: o programa-irmão expandiu menos do que parece.** No Mais Médicos, a chegada de **+15,1 médicos do programa** por 100 mil habitantes resultou em apenas **+5,7** de expansão **líquida**: o resto substituiu profissionais que já estavam lá. |
| **O degrau do PMM-E tem o tamanho que a literatura pede.** O prêmio exigido para ir a um posto pior vai de **37% a 64%** da renda anual em cidades pequenas, e a oferta de médicos no interior brasileiro responde a salário com elasticidade de **0,7**. O degrau do programa — R$ 5 mil sobre R$ 10 mil, **+50%** — cai dentro dessa faixa. | **Austrália: a maioria não vai por preço nenhum.** Dos **3.727 clínicos**, **65%** ficaram onde estavam em **todos** os cenários oferecidos; para o pior posto, quem mudaria pedia **130%** da renda anual. |
| | **Brasil: salário compra pouco e custa muito.** Elevar em 50% o salário público no interior do Norte e Nordeste corrigiria **12,4%** do desequilíbrio, a **US$ 15,7 milhões por ponto percentual**; reservar vagas na faculdade para quem nasceu ali corrigiria **63,8%**, por US$ 2,2 a 5,1 milhões o ponto. |
| | **EUA: quem vai por obrigação, vai embora.** Oito anos depois, **12%** dos médicos que foram para clínicas rurais com bolsa e obrigação de permanência ainda estavam lá — contra **39%** dos que foram sem obrigação. |

**Ressalva:** os percentuais da literatura são sobre a **renda total** do médico;
a bolsa do PMM-E remunera **20 horas semanais**.

**A evidência não decide se um degrau de R$ 5 mil basta.**

**Fontes:** Dal Bó, Finan & Rossi (2013), *QJE* 128(3); Hone et al. (2020),
*BMC Health Services Research* 20:873; Scott et al. (2013), *Social Science &
Medicine* 96; Costa, Nunes & Sanches (2024), *REStat* 106(1); Pathman, Konrad &
Ricketts (1992), *JAMA* 268(12). Números do ciclo 1:
`output/tema_trabalho/` (módulos A4 e A5).

---

## A pergunta que organiza o trabalho

`1. Motivação e Pergunta · Pergunta de Pesquisa`

> ### O incentivo financeiro oferecido pelo PMM-E funciona para atrair especialistas para regiões mais vulneráveis?

Dois objetos, um contra o outro: o **preço** que a política colocou sobre a
vulnerabilidade — o degrau de **R$ 5 mil** entre faixas — e a **desvantagem**
que esse preço pretende compensar.

A margem que observamos é o **preenchimento da vaga**: se, ao final da chamada,
apareceu alguém disposto a ocupá-la. Permanência fica fora desta banca.

> [!NOTE]
> **Correspondência com a formulação canônica.** Em
> [`01_pergunta_escopo/15`](../../01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md)
> a pergunta está escrita como *"maiores bolsas do PMM-E para municípios mais
> vulneráveis compensam suas desvantagens territoriais na atração de médicos
> especialistas?"*. É a mesma pergunta; a formulação acima é a versão de tela.

---

# 2. Literatura Teórica e Modelo Microeconômico

### De onde vem a equação de escolha, e o que há dentro do custo

`sem rastreio`

---

## A escolha locacional maximiza a renda real líquida

`2. Literatura e Modelo · Visão geral`

### Três tradições sustentam uma equação

| Trabalho | Entra no modelo como | Primitiva que fornece |
|---|---|---|
| **Moehling, Niemesh, Thomasson & Treber (2020)** | escolha locacional intertemporal: o médico maximiza o valor presente do rendimento real menos um custo locacional não pecuniário | a **equação de escolha** e o horizonte $\sum_t \delta^t$ |
| **Redding & Rossi-Hansberg (2017)** | equilíbrio espacial: amenidades e custo de moradia determinam a atratividade de um lugar | o **custo geográfico** e o deflator $p_m$ |
| **Choné & Ma (2011)**, com **Reinhardt (1972, 1975)** | utilidade do médico com altruísmo: atender gera cansaço e satisfação, ambos mediados por equipe e capital instalado | o **custo laboral líquido** e o papel de $L$ e $K$ |

### A equação de escolha

$$\arg\max_{i \in I} \left\{ \sum_t \delta^t \left[ \frac{\mathbb{E}(w_{it}^{(s)})}{p_{it}} - c_{it}^{(s)} \right] \right\}$$

| Termo | O que significa |
|---|---|
| $i \in I$ | localidades candidatas |
| $\mathbb{E}(w^{(s)}_{it})$ | salário esperado em $i$, no ano $t$, na especialidade $s$ |
| $p_{it}$ | nível de preços da localidade — o deflator |
| $c^{(s)}_{it}$ | custo **não pecuniário** de viver ali |
| $\delta^t$, $\sum_t$ | desconto e soma ao longo do horizonte de carreira |

**O que a conta faz.** Divide o salário pelos preços locais, porque o que decide
é o salário **real**. Subtrai o custo não pecuniário, e sobra o ganho líquido do
ano. Desconta cada ano e soma a carreira inteira. Compara as localidades e
devolve a de maior valor.

**Onde chegamos.** A localidade escolhida é a de maior **renda real líquida
descontada** — salário nominal alto não compensa preços e custos locais altos.

> [!IMPORTANT]
> **O buraco que os outros dois preenchem.** Na definição dos próprios autores,
> $c$ reúne *"preferences over rural or urban living, or other
> location-specific attributes, such as proximity to family"* — uma
> **caixa-preta**. Abri-la é o trabalho dos dois slides seguintes.

**Fontes:** Moehling et al. (2020), *Cliometrica* 14, p. 184, eq. 1;
[`docs/02_teoria/modelo_micro.md`](../../02_teoria/modelo_micro.md), §1.

---

## O custo da localidade tem duas metades: o lugar e o trabalho

`2. Literatura e Modelo · Custo da localidade`

### O lugar — Redding & Rossi-Hansberg (2017), eq. 24, p. 28

$$u_{nio} = \frac{z_{nio}\, B_n\, w_i}{\kappa_{ni}\, Q_n^{\,1-\beta}}$$

No numerador, **o que atrai**: o salário do local de trabalho, multiplicado
pelas amenidades $B_n$ e pelo gosto pessoal. No denominador, **o que repele**: o
custo de deslocamento $\kappa_{ni}$ e o preço da moradia $Q_n$. A divisão
transforma salário nominal em bem-estar — o mesmo salário vale menos onde morar
é caro ou a viagem é longa. Daí sai o bloco geográfico do custo:

$$c^{\text{geo}}_{im} = \phi(\text{dist}_{im}) - \gamma A_m + \theta_i^{\text{rural}}$$

Afastar-se da família custa, e custa mais a cada quilômetro ($\phi' > 0$); a
amenidade urbana compensa ($-\gamma A_m$); o gosto por cidade pequena ou grande
não tem sinal universal.

### O trabalho — Choné & Ma (2011), eq. 1, p. 232

$$U = R - C(q; L, K) + \alpha B(q)$$

O médico soma a renda do atendimento, subtrai o **custo de esforço** de produzir
$q$ e soma o **benefício ao paciente**, ponderado pelo altruísmo $\alpha$. Daí
sai o bloco laboral:

$$c^{\text{laboral}}_{im} = C(q; L_m, K_m) - \alpha_i B(q; L_m, K_m)$$

Atender cansa, e cansa de forma crescente ($C' > 0$, $C'' > 0$); curar dá
satisfação decrescente, porque a triagem prioriza o caso grave ($B' > 0$,
$B'' < 0$). O custo marginal $c'(q) = C' - \alpha B'$ tem **sinal incerto**, mas
$c'' \gg 0$: a curva é um **U**, com uma zona em que atender mais *reduz* o
custo líquido, um mínimo, e uma zona de exaustão.

**Equipe ($L$) e capital ($K$) atuam duas vezes.** Reduzem o cansaço,
$\partial C/\partial K < 0$ — canal que já está em Choné & Ma. E **ampliam o
benefício**, $\partial B/\partial K > 0$: sem insumo ou maquinário em
funcionamento, o atendimento perde resolutividade. Esse segundo canal é
**extensão deste projeto**, motivada pela função de produção médica de
Reinhardt. Por dois caminhos, $\partial c^{\text{laboral}}/\partial K < 0$.

### As quatro desvantagens, na visão do médico

"Município vulnerável" não é um índice para quem decide. É um conjunto de
desvantagens concretas, e cada uma cai num bloco do custo:

| Desvantagem | O que significa para o médico | Bloco | Medimos? |
|---|---|:---:|:---:|
| **Retaguarda profissional** | sem segunda opinião, sem plantão, sem a quem encaminhar o caso difícil | $L$ | sim — colegas da especialidade no CNES |
| **Infraestrutura** | equipamento, insumo e equipe escassos: atender cansa mais e resolve menos | $K$ | em parte |
| **Distância da família** | viver longe de onde a família está e onde se formou | $\phi(\text{dist})$ | não |
| **Mercado privado ausente** | a remuneração se reduz ao que o programa paga | $w^{\text{priv}}$ | não — ver slide 11 |

**O peso de cada uma, na literatura.** No **Brasil**, entre 50 mil generalistas
formados de 2001 a 2013, **a proximidade do lugar de nascimento ou de formação é
o principal fator**; salário e infraestrutura pesam menos.

> [!NOTE]
> **Uma limitação assumida.** CNES e edital não informam a residência do
> profissional, por sigilo fiscal. A unidade de análise é o **município do
> estabelecimento**, não o de moradia: a distância entra como latente.

**Fontes:** Redding & Rossi-Hansberg (2017), *Annual Review of Economics* 9,
p. 28, eq. 24; Choné & Ma (2011), *IJHCFE* 11, p. 232, eq. 1; Reinhardt (1972,
1975); Costa, Nunes & Sanches (2024), *REStat* 106(1);
[`modelo_micro.md`](../../02_teoria/modelo_micro.md), §2.1 a §2.3 e §3.2.

---

## A bolsa não é toda a remuneração da localidade

`2. Literatura e Modelo · Remuneração da localidade`

A bolsa compra **20 horas semanais**. O que o médico faz com as outras horas
entra na decisão junto com ela:

$$\mathbb{E}(w_{imt} \mid B_m) = \underbrace{B_m}_{\text{fixado pela regra}} + \underbrace{w^{\text{priv}}_m}_{\text{mercado local}}$$

| | Capital ou região metropolitana | Interior isolado |
|---|---|---|
| **Bolsa $B_m$** | R$ 10 mil (Faixa 3) | R$ 20 mil (Faixa 1) |
| **Mercado local $w^{\text{priv}}_m$** | alto — consultório, plano, hospital privado | ausente |
| **Remuneração total** | $B + w^{\text{priv}}$, pode superar R$ 20 mil | $w \to B$: a bolsa é **toda** a remuneração |
| **Deflator $p_m$** | custo de vida alto | custo de vida baixo, valoriza a mesma bolsa |

**A consequência é contraintuitiva.** A bolsa nominal do interior é o **dobro**
da bolsa da capital, e ainda assim a **remuneração total** do médico pode ser
**menor** no interior — porque na capital ela é um piso somado a um mercado, e
no interior é o teto. O deflator trabalha no sentido oposto, e não se sabe a
priori qual das duas forças vence.

> [!IMPORTANT]
> **É aqui que o slide 4 volta.** Se apenas **7,7%** dos cirurgiões atuam
> exclusivamente no setor público e **72,4%** vivem de dupla prática, então
> $w^{\text{priv}} > 0$ é a **regra**, não a exceção. A política aposta que
> R$ 5 mil a mais compensam o lugar; o modelo diz que eles competem com um
> mercado privado cuja ausência é, ela própria, uma desvantagem do lugar.

**Fontes:** [`modelo_micro.md`](../../02_teoria/modelo_micro.md), §3;
[`hipoteses_e_viabilidade_empirica.md`](../../02_teoria/hipoteses_e_viabilidade_empirica.md), §2;
Edital SGTES/MS nº 3/2025, item 11.3.b (20 horas).

---

# 3. Hipótese e Viabilidade Empírica

### O que o modelo implica para o PMM-E, o que se testa e o que os dados permitem

`sem rastreio`

---

## No PMM-E, a regra fixa a remuneração e o IVS organiza o custo

`3. Hipótese e Viabilidade · Implicações para o PMM-E`

O médico $i$ escolhe o município $m$ que maximiza o valor presente líquido da
carreira:

$$V_{im} = \sum_t \delta^t \left[ \frac{\mathbb{E}(w_{imt} \mid B_m)}{p_{mt}} - c_{im} \right] + \varepsilon_{im}$$

$$c_{im} = \underbrace{\phi(\text{dist}_{im}) - \gamma A_m + \theta_i^{\text{rural}}}_{\text{Redding \& Rossi-Hansberg}} + \underbrace{C(q; L_m, K_m) - \alpha_i B(q; L_m, K_m)}_{\text{Choné \& Ma, com a extensão em } B}$$

**O que nenhuma das três tradições tem.** Nenhuma trata de um componente da
remuneração **fixado por regra pública sobre um índice territorial**. É isso, e
só isso, que a adaptação ao PMM-E acrescenta.

### Cada termo do modelo, sobre uma variável do programa

| Termo do modelo | Variável do programa | Derivada | Leitura |
|---|---|:---:|---|
| $B_m$ | **valor da bolsa**, R$ 10/15/20 mil | $\partial V/\partial B_m > 0$ | é o instrumento; entra aditivamente na remuneração real |
| $w^{\text{priv}}_m$ | **mercado local**, não observado | $\partial^2 V/\partial B_m \partial w^{\text{priv}} < 0$ | a bolsa vale mais onde não há mercado |
| $p_m$ | **custo de vida**, UF | $\partial V/\partial p_m < 0$ | opera no sentido contrário ao da vulnerabilidade |
| $c_{im}$ | **IVS** e suas três dimensões | $c_0'(IVS) \gtrless 0$ | **sinal ambíguo** — ver abaixo |

### Por que o IVS organiza o custo

Distância da família, aluguel, mercado privado e esforço clínico **não são
observados**. O que se observa, para todo município, é o **IVS**. Escrevemos o
custo como função do índice mais um desvio individual, $c_{im} = c_0(IVS_m) + \eta_i$.
Isso não é atalho: **cada dimensão do índice corresponde a um bloco do custo.**

| Dimensão do IVS | Indicadores | Bloco do custo | Efeito sobre $c$ |
|---|---|---|:---:|
| Infraestrutura urbana | saneamento, lixo, tempo de deslocamento | amenidades $A_m$ | $\uparrow$ |
| Renda e trabalho | pobreza, desemprego, informalidade | mercado privado ausente, $w \to B$ | $\uparrow$ |
| Capital humano | mortalidade infantil, analfabetismo, mães adolescentes | gravidade do caso, $B'(q)\uparrow$; escassez de $L$ e $K$ | **ambíguo** |

A terceira linha é o que impede assumir que o custo cresce com o índice.
Carência sanitária **eleva o benefício** de atender — o que **reduz** o custo
para um médico altruísta — e ao mesmo tempo **sinaliza falta de insumos**, o que
**eleva** o cansaço. Logo $c_0'(IVS) \gtrless 0$: o sinal é questão empírica.

**É por isso que o objeto do trabalho é o degrau da bolsa entre faixas, e não a
inclinação do índice.**

**Fontes:** [`modelo_micro.md`](../../02_teoria/modelo_micro.md), §2.4, §3 e §3.1;
[`hipoteses_e_viabilidade_empirica.md`](../../02_teoria/hipoteses_e_viabilidade_empirica.md), §3.

---

## Da condição de aceitação sai a hipótese

`3. Hipótese e Viabilidade · Hipótese do trabalho`

**Passo 1 — a condição de aceitação.** O médico $i$ aceita a vaga em $m$ quando
o que ela vale supera sua melhor alternativa $\bar{v}_i$:

$$\frac{B_m + w^{\text{priv}}_m}{p_m} - c_0(IVS_m) \;\geq\; \bar{v}_i$$

**Passo 2 — do médico à vaga.** A vaga é preenchida se existir **ao menos um**
candidato para quem a desigualdade vale. Tudo o que aumenta o lado esquerdo
aumenta essa probabilidade.

**Passo 3 — a hipótese.**

> ### H1 — Uma elevação na remuneração oferecida pelo PMM-E eleva a taxa de preenchimento das vagas ofertadas

$$\frac{\partial \Pr(\text{preenchimento}_m)}{\partial (B_m / p_m)} > 0$$

**Passo 4 — o custo é obstáculo, não hipótese.** O custo locacional não entra
como segunda hipótese porque **não varia livremente**: a regra do edital o amarra
à bolsa, e os dois sobem juntos. Ele é o que torna H1 **difícil de testar**, não
uma segunda afirmação a testar.

Na fronteira entre duas faixas, o preenchimento do lado mais vulnerável exige
que o degrau monetário supere o degrau de custo:

$$\frac{\Delta B_m}{p_m} > \Delta c_0, \qquad \Delta B_m = \text{R\$ } 5.000$$

**A pergunta da apresentação é se essa desigualdade vale.**

**Fontes:** [`modelo_micro.md`](../../02_teoria/modelo_micro.md), §4.1 e §4.2;
[`hipoteses_e_viabilidade_empirica.md`](../../02_teoria/hipoteses_e_viabilidade_empirica.md), §4.2.

---

## Há dado para quase todo termo — e sabemos quais faltam

`3. Hipótese e Viabilidade · Disponibilidade de dados`

| Termo do modelo | O que observamos | Fonte | Grau |
|---|---|---|:---:|
| **Preenchimento** (desfecho) | confirmação ou homologação por célula estabelecimento–curso, ciclo 1 | quadros publicados do edital — 1.295 células, 368 municípios | 🟢 direto |
| **Bolsa $B_m$** | faixa de atração anunciada em cada vaga e seu valor | edital e quadro de vagas — 2.815 municípios, ciclos 1 a 3 | 🟢 direto |
| **Remuneração total** ($B + w^{\text{priv}}$) | — | RAIS nunca adquirida; CNES não traz carga horária nem renda | 🔴 não observado |
| **Custo de vida $p_m$** | diferenças entre estados, por efeito fixo de UF | IBGE | 🟡 proxy |
| **Custos geográficos** | amenidades pelo sub-índice de infraestrutura do IVS e pela tipologia territorial em 4 estratos | Ipea; REGIC 2018 e RMs/RIDEs 2022 (IBGE) | 🟡 proxy |
| — distância da família | — | residência do profissional é sigilo fiscal | 🔴 não observado |
| — custo de moradia | — | sem fonte municipal no repositório | 🔴 não observado |
| **Custos laborais** — equipe $L$ | especialistas da mesma especialidade no município, 12 meses prévios | CNES mensal | 🟡 proxy |
| — capital $K$ | leitos e equipamentos estão mapeados, mas as competências do CNES físico não foram baixadas | CNES | 🔴 pendente de aquisição |
| — volume e gravidade $q$ | produção existe só como pré-tratamento de outro módulo, e está bloqueada | SIH/SUS | 🔴 bloqueado |

**Sim, para o essencial.** O desfecho e o instrumento são observados
diretamente. O custo é observado por proxies declaradas — IVS, sub-índices,
tipologia territorial e estoque prévio de colegas.

> [!WARNING]
> **As duas ausências que mais doem.** A **remuneração de mercado local** e a
> **distância da família** são exatamente os dois termos que o modelo diz serem
> decisivos, e nenhum dos dois é observável com fonte pública. Eles entram como
> parte do custo que o IVS e a tipologia territorial resumem — e essa
> substituição é uma escolha, não uma solução.

**Fontes:** [`04_dados/02_inventario_dados_por_outcome.md`](../../04_dados/02_inventario_dados_por_outcome.md);
[`hipoteses_e_viabilidade_empirica.md`](../../02_teoria/hipoteses_e_viabilidade_empirica.md), §3;
`output/tema_trabalho/`, `output/aquisicao/` e `output/rdd_bolsa/`.

---

## Separar o efeito da bolsa do efeito da vulnerabilidade

`3. Hipótese e Viabilidade · Desafio metodológico`

**O problema.** A regra dá mais dinheiro exatamente aos municípios mais
difíceis. Comparar Faixa 1 com Faixa 3 compara, ao mesmo tempo, **R$ 10 mil a
mais** e **todas as desvantagens** que levaram àquela faixa. O gradiente
observado mistura os dois.

**A resposta natural.** Se o valor é atribuído por um corte no IVS, municípios
imediatamente acima e abaixo do corte são quase iguais em tudo — menos na bolsa.
É uma **regressão descontínua**, e reconstruir a regra era o primeiro passo do
trabalho empírico. **Ele foi dado, em 14/09/2026.** Tem três resultados.

| | Achado | Número |
|:---:|---|---|
| **1** | **Há suporte comum.** Existe município com bolsa alta e vulnerabilidade baixa | 37 municípios com IVS ≤ 0,400 na Faixa 1 e 94 na Faixa 2; os intervalos das três faixas se sobrepõem |
| **2** | **Mas não há descontinuidade onde os cortes estão.** O tratamento é localmente constante | em torno de `0,500`, os dois lados são **100% Faixa 1** em qualquer janela até ±0,050; em torno de `0,400`, o maior IVS da Faixa 3 é `0,372` — não há Faixa 3 por perto |
| **3** | **E a variação que sobra não é exógena.** Quem é promovido acima do piso é sistematicamente diferente | dos 83 municípios fora da melhor regra de limiar, os 41 promovidos têm mediana de população **7.933** contra **32.179** dos 42 rebaixados, e muito mais interior remoto |

**Por que o item 3 é fatal.** Como a remoticidade é o previsor mais forte do
preenchimento, parear por IVS **confunde bolsa com posição territorial** — e o
viés tem direção conhecida: ele funciona **contra** a bolsa, podendo inverter o
sinal do que se estimaria.

| Figura na tela | O que mostra | Estado |
|---|---|---|
| **A descontinuidade que não existe** | dispersão de IVS 2010 no eixo horizontal contra a **faixa publicada** de cada município, com os cortes `0,400` e `0,500` marcados: as três faixas se sobrepõem, e nos dois cortes o salto de tratamento é nulo | **a gerar** (pendência 7). É a figura que sustenta este slide, e é o contraponto honesto ao gráfico de degrau da bolsa do slide 5 |

> [!CAUTION]
> **Conclusão de viabilidade.** O efeito causal do **valor da bolsa** não é
> identificável com as fontes públicas, e a razão **não** é potência amostral: é
> que o IVS é o piso da bolsa, não o critério dela. Destravá-lo exige o **Anexo
> IV** e os critérios de localização da cláusula 11.1.3, que só o Ministério pode
> fornecer. O pacote de solicitação está pronto; o envio é decisão do autor.

### O que fica de pé

- **A pergunta continua sendo a pergunta.** Ela não depende do desenho.
- **A relação entre faixa e preenchimento é reportada como gradiente**, não como
  efeito, enquanto a regra não for recuperada.
- **Há um desenho causal vivo, mas ele responde a outra pergunta.** A
  descontinuidade no **escore de seleção do candidato** compara o último
  selecionado com o primeiro não selecionado dentro da **mesma** célula
  curso–estabelecimento. Ali a bolsa é constante por construção: ele identifica
  o efeito de **ganhar a vaga**, não o do valor da bolsa.

**Fontes:** [`05_identificacao/14_plano_implementacao_rdd_bolsa.md`](../../05_identificacao/14_plano_implementacao_rdd_bolsa.md);
[`05_identificacao/16_sintese_achados_e_novo_plano_causal.md`](../../05_identificacao/16_sintese_achados_e_novo_plano_causal.md), §3.5, §3.5.1 e §6;
[`06_execucao/36_backlog_pos_auditoria.md`](../../06_execucao/36_backlog_pos_auditoria.md), item D-3.

---

<!-- deck:fim -->

## Pendências abertas em 16/09/2026

Registradas aqui porque afetam o que vai à tela. Detalhe e rastreio em
[03 — Proveniência](03_proveniencia_figuras_e_numeros.md).

| # | Pendência | Efeito | O que fecha |
|:---:|---|---|---|
| **1** | As duas figuras do slide 4 — especialistas por UF e deslocamento médio por região — vêm de fontes externas e **não são geradas por script versionado** | bloqueia a regra de proveniência do projeto | acrescentar as duas séries a `gerar_figuras_banca1.py`, lendo de `output/`, com a fonte registrada |
| **2** | Os valores do gráfico de deslocamento (Norte 276 km … Sul 101 km) **não tiveram a fonte primária confirmada** | número em tela sem rastreio | localizar a tabela da REGIC 2018 sobre deslocamentos para serviços de saúde e registrar o arquivo em `data/raw/` |
| **3** | A proveniência registrava "10% dos cirurgiões atuando exclusivamente no SUS"; a fonte primária diz **7,7%** | número errado, agora corrigido no slide 4 | ✅ corrigido em 16/09/2026; PDF da *Demografia Médica 2025* a registrar em `data/raw/` com hash |
| **4** | A tabela de inclinações pré/pós por faixa do deck do grupo (0,012 / 0,271 …) **não é reproduzível** a partir do repositório e não tem grupo de comparação | seria resultado sem rastreio | mantida **fora** do slide 6; a série mensal por faixa é reprodutível e pode entrar como contexto descritivo |
| **5** | "Sudeste 55,4% dos especialistas" está conferido em **cobertura**, não localizado no PDF integral | ressalva de fonte | conferir na *Demografia Médica 2025* ao registrar o PDF |
| **6** | Os decks Beamer e Slidev ainda estão na estrutura de **15 slides** | divergência deck × documento | reconstruir os dois decks sobre esta estrutura |
| **7** | O slide 16 pede uma figura que ainda **não existe**: IVS contra faixa publicada, com os cortes marcados | o slide fica só em texto, e o achado central da viabilidade fica sem imagem | acrescentar a figura a `gerar_figuras_banca1.py`, lendo `output/rdd_bolsa/matriz_municipio_regra_ivs.csv` |

## Ressalvas de conteúdo encerradas

1. **Cursos ambulatoriais.** A contagem de 10 ambulatoriais e 6 cirúrgicos foi
   conferida na Tabela 3 do edital e nos códigos 1 a 16 de
   `output/aquisicao/quadro_vagas_tratamento.parquet`. Encerrada em 16/09/2026.
2. **Figura do custo laboral.** `curva_custo_laboral_burnout.png` saiu do deck;
   o formato em U é descrito em texto no slide 10. A figura permanece como
   ilustração canônica em `docs/02_teoria/figuras/`. Encerrada em 16/09/2026.
3. **Portaria GM/MS nº 7.177/2025.** O texto bruto não está preservado em
   `data/`. Nenhum slide a cita entre aspas; ela aparece apenas como referência.
   Encerrada em 16/09/2026 por remoção da citação direta.
