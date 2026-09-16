---
documento: Conteúdo da apresentação — banca 1
papel: fonte de verdade do que vai à tela
escopo: teórico, termina na viabilidade empírica; sem resultado de estimação
slides: 16
atualizacao: 17 de setembro de 2026
---

> [!IMPORTANT]
> **Como ler este arquivo.** O deck começa e termina nos comentários
> `deck:inicio` e `deck:fim`, invisíveis na renderização. Entre eles, **cada
> cabeçalho é um slide, e só os cabeçalhos são slides**:
>
> | Nível | O que é | Uso |
> |:---:|---|---|
> | `#` | **slide**, layout de capa | a capa e as três divisórias de seção |
> | `##` | **slide**, layout de conteúdo | os doze slides de conteúdo |
> | `###` | **build** dentro do slide | um `\only<n>` no Beamer, um clique no Slidev |
>
> Um slide sem `###` é de tela única. Um slide com três `###` é **um** frame com
> **três** builds, não três frames: a contagem de slides não muda.
>
> Abaixo do cabeçalho do slide, a linha em `código` é o **rastreio** do rodapé,
> no formato `Seção · Rótulo do roteiro`. Os rótulos são os do roteiro acordado
> (Problema, Política, Efeitos, …) e os títulos são as manchetes de tela.
>
> **O que não vai à tela:** a linha `**Fontes:**`, que vira nota de rodapé
> pequena, e todo bloco marcado `**Nota de produção.**`, que é instrução para
> quem monta o deck. Tudo o mais no corpo do slide é conteúdo de tela.
>
> **Orçamento de frame.** Cada build foi dimensionado para caber em cerca de
> **14 linhas de tela**. Quatro builds foram compilados de verdade em Beamer
> 16:9, 11 pt, tema Warsaw, todos **sem Overfull** e com folga vertical: a tabela
> das duas cláusulas e as duas figuras lado a lado no slide 5, o diagrama da
> teoria da mudança como cadeia TikZ — que em 17/09/2026 passou ao slide 7 — e a
> tabela do que falta no slide 15.
>
> Os decks em [`deck_beamer/`](deck_beamer/) e [`deck_slidev/`](deck_slidev/)
> são **derivados** deste arquivo: divergência entre deck e documento é erro do
> deck. Em 16/09/2026 os decks ainda estão na estrutura anterior, de 15 slides —
> divergência conhecida e datada, a resolver na próxima reconstrução.

## Mapa da apresentação

| # | Layout | Builds | Seção | Rótulo do roteiro | Título na tela |
|:---:|:---:|:---:|:---:|---|---|
| 1 | capa | 1 | — | — | Capa |
| 2 | conteúdo | 1 | — | Sumário | Sumário |
| 3 | capa | 1 | 1 | — | **Motivação e Pergunta** |
| 4 | conteúdo | 3 | 1 | Problema | O especialista está longe do interior — e quase nunca é só do SUS |
| 5 | conteúdo | 3 | 1 | Política | A bolsa é do município, não do médico nem da especialidade |
| 6 | conteúdo | 3 | 1 | Efeitos | O programa já deu sinais; a literatura aponta para os dois lados |
| 7 | conteúdo | 2 | 1 | Pergunta de Pesquisa | A pergunta que organiza o trabalho |
| 8 | capa | 1 | 2 | — | **Literatura Teórica e Modelo Microeconômico** |
| 9 | conteúdo | 2 | 2 | Visão geral | A escolha locacional maximiza a renda real líquida |
| 10 | conteúdo | 3 | 2 | Custo da localidade | O custo da localidade tem duas metades: o lugar e o trabalho |
| 11 | conteúdo | 2 | 2 | Remuneração da localidade | A bolsa não é toda a remuneração da localidade |
| 12 | capa | 1 | 3 | — | **Hipótese e Viabilidade Empírica** |
| 13 | conteúdo | 2 | 3 | Implicações para o PMM-E | No PMM-E, a regra fixa a remuneração e o IVS organiza o custo |
| 14 | conteúdo | 2 | 3 | Hipótese do trabalho | Da condição de aceitação sai a hipótese |
| 15 | conteúdo | 2 | 3 | Disponibilidade de dados | Há dado para quase todo termo — e sabemos quais faltam |
| 16 | conteúdo | 3 | 3 | Desafio metodológico | Separar o efeito da bolsa do efeito da vulnerabilidade |

---

<!-- deck:inicio -->

# Remuneração como incentivo limitado

### Um modelo de escolha racional para o Programa Mais Médicos Especialistas

**Grupo 2** · Bernardo Gomes · Bruno Manta · Felipe Barros · Felipe Marques ·
Gabriel Benegra · Kauã Santos · Vinicius Sbruzzi

`sem rastreio`

> [!NOTE]
> **Nota de produção.** "Incentivo limitado" antecipa uma conclusão que esta
> banca não entrega. Alternativa neutra, se a banca preferir: *"Quanto vale o
> lugar? Um modelo de escolha locacional para o PMM-E"*. Mantido o título do
> grupo até decisão do autor.

---

## Sumário

`sem rastreio`

1. **Motivação e Pergunta**
2. **Literatura Teórica e Modelo Microeconômico**
3. **Hipótese e Viabilidade Empírica**

> [!NOTE]
> **Nota de produção.** O sumário aparece uma vez. As divisórias de seção
> substituem as quatro repetições do deck anterior.

---

# 1. Motivação e Pergunta

### O problema, a política, os efeitos e a pergunta

`sem rastreio`

---

## O especialista está longe do interior — e quase nunca é só do SUS

`1. Motivação e Pergunta · Problema`

### Onde eles estão

![Especialistas por 100 mil habitantes, dez/2024 — 453 no DF e 244 em SP, contra 70 no PA e 68 no MA](../../../output/apresentacao_banca1/especialistas_por_uf_extremos.png)
![Distância média para serviços de alta complexidade — 276 km no Norte, 101 km no Sul](../../../output/apresentacao_banca1/deslocamento_por_regiao.png)

> **A escassez é territorial — e onde há menos especialista o paciente anda mais.**

### De quem é o tempo desse especialista

![Setor de atuação dos cirurgiões — 72,4% em dupla prática, 19,9% exclusivamente no privado, 7,7% exclusivamente no público ou SUS](../../../output/apresentacao_banca1/dupla_pratica_cirurgioes.png)

**O SUS não compra a carreira do especialista. Compra uma fração dela** — e
disputa o resto com o mercado privado. A bolsa do PMM-E compra **20 horas**
dessa fração.

### E quais especialistas faltam

- Maiores ofertas do ciclo 1: **endoscopia digestiva alta**, **colonoscopia** e
  **anestesiologia**.
- Em 2025 o Ministério declarou **urgência em saúde pública por 24 meses** pelo
  tempo de espera, e lançou o **Agora Tem Especialistas**, de que o PMM-E é o
  braço de provimento.

**Fontes:** Scheffer et al., *Demografia Médica no Brasil 2025* (FMUSP/AMB),
cap. 11 e cap. 13, Fig. 1, p. 254; deslocamento: origem provável na REGIC 2018
(IBGE), **a confirmar**; Portaria GM/MS nº 7.061/2025; Edital SGTES/MS nº
3/2025, Tabela 3; `output/aquisicao/quadro_vagas_tratamento.parquet`; figuras
por `scripts/apresentacao/gerar_figuras_banca1.py`.

> [!NOTE]
> **Nota de produção — as três figuras.** Desde 17/09/2026 as três saem do
> pipeline, e o texto que elas substituem saiu da tela: os quatro marcadores do
> retrato nacional, a tabela dos três percentuais de atuação e os dois
> marcadores de cursos. A ressalva de cobertura do inquérito — **1.544
> cirurgiões, não censo** — continua **na tela**, dentro do rodapé da figura.
> A figura de UF é dos **extremos**, não das 27 unidades: só quatro UFs têm
> valor em fonte registrada. A do deck do grupo mostrava 16 barras e **não é
> usável** — ver a pendência 1.

> [!NOTE]
> **Nota de produção — o que não dá para dizer.** A frase "apenas 10% dos
> especialistas atendem no SUS" **não se sustenta**: é fala do ministro em
> debate no Senado, 24/09/2025, sem metodologia, e a fonte primária a contradiz
> — somando dupla prática e exclusivos do público, **80,1%** dos cirurgiões
> atendem SUS. O defensável é o inverso: **exclusividade** ao SUS é que é rara.
> O recorte **por especialidade não existe** em fonte pública; o estudo só o traz
> para cirurgiões, por amostra do Colégio Brasileiro de Cirurgiões, não por censo.

---

## A bolsa é do município, não do médico nem da especialidade

`1. Motivação e Pergunta · Política`

### O que o programa oferece

![Valor mensal da bolsa-formação por faixa de atração](../../../output/apresentacao_banca1/bolsa_por_faixa.png)

**Lei nº 15.233/2025**, para reduzir o **tempo de espera** do SUS.
Bolsa-formação **sem vínculo**, até **12 meses**, **20 h semanais**, **RQE**
exigido, com supervisão de instituição formadora — **igual em toda vaga**. O
**valor** é a única coisa que varia. Ciclo 1, jul/2025: **1.295 células**
estabelecimento–curso em **368 municípios**, **678** com vaga imediata.

> **O programa não forma especialista: exige RQE e compra 20 horas de quem já é.**

### Quem fixa o valor

**Não fixam:** especialidade, curso, estabelecimento, carga, produção,
desempenho — nem o médico. **Fixa:** o **município**, e só ele.

| Cláusula | O que fixa o valor | Situação |
|---|---|---|
| **11.1.4** | categoria de **IVS 2010** do Ipea: muito alta → **R$ 20 mil**, alta → **R$ 15 mil**, demais → **R$ 10 mil** | pública |
| **11.1.3** | *"critérios de **localização e vulnerabilidade** definidos de acordo com a faixa de atração definida no **Anexo IV**"* | **não público** |

Em **177 dos 368** municípios a faixa publicada está **acima** da categoria de
IVS; **zero** abaixo.

> **O IVS é o piso da bolsa, não o critério dela.**

### Para onde a regra manda o dinheiro

![Especialistas por 100 mil habitantes, jun/2025 — 15,0 na Faixa 3, 14,4 na Faixa 2, 18,3 na Faixa 1](../../../output/apresentacao_banca1/oferta_pre_por_faixa.png)
![Colegas da mesma especialidade no município, jun/2025 — mediana de 6,5, 5,0 e 2,5 da Faixa 3 à Faixa 1](../../../output/apresentacao_banca1/retaguarda_por_faixa.png)

**Por habitante**, a bolsa maior não vai para onde falta mais. **Em colegas**,
vai: a mediana cai de **6,5** para **2,5**.

> **A Faixa 1 compensa isolamento, não cobertura.**

**Fontes:** Lei nº 15.233/2025, art. 21; Edital SGTES/MS nº 3/2025, itens 1.1,
1.2.1, 1.2.5, 11.1 a 11.4; Ipea, *Atlas da Vulnerabilidade Social* (2015); CNES
06/2025 e Censo 2022 (IBGE); `output/aquisicao/quadro_vagas_tratamento.parquet`;
figuras por `scripts/apresentacao/gerar_figuras_banca1.py`.

> [!NOTE]
> **Nota de produção — o que saiu daqui em 17/09/2026.** O slide tinha **cinco
> builds** e passou a **três**. Saíram da tela: o diagrama de **teoria da
> mudança**, que foi para o **slide 7**, onde faz o trabalho de tornar a
> pergunta inevitável; a frase sobre nenhuma célula município–curso aparecer com
> mais de uma faixa, que é conferência, não argumento; e as duas notas de bolso
> — a **contribuição previdenciária** do item 11.2 e o **adicional** da Lei
> (art. 22-D, §4º) para Amazônia Legal, territórios indígenas e alta
> vulnerabilidade, **não regulamentado** no ciclo 1. As duas continuam
> registradas em `auditorias/01_regra_institucional.md` e servem para responder
> à banca; nenhuma vira afirmação sobre o tamanho líquido do degrau, que
> depende do teto de contribuição e não foi calculado.

> [!NOTE]
> **Nota de produção — três correções do PR de ajuste estrutural.** (1) **D1**:
> "1.295 vagas" virou **1.295 células** estabelecimento–curso, com as **678**
> vagas imediatas ditas na tela — chamar célula de vaga reintroduzia o
> denominador que o portão A1 rejeitou. (2) **F2**: o pacote formativo entrou no
> slide como o que **não** varia — é o que sustenta, mais adiante, que o
> contraste de R$ 5 mil compara valor com pacote constante dos dois lados.
> (3) **F5**, **pendente de decisão do autor**: a retaguarda é medida no
> **município**, mas 42,6% das células estão em estabelecimento de gestão
> estadual e 93 dos 460 CNES têm "REGIONAL" no nome — o incentivo é fixado pelo
> IVS do município-sede e a clientela é regional. Cabe uma linha no build 3
> ("a medida é municipal; para hospital regional a fronteira relevante é
> outra") ou uma limitação declarada. Não entrou na tela sem essa decisão.

---

## O programa já deu sinais; a literatura aponta para os dois lados

`1. Motivação e Pergunta · Efeitos`

### O que o ciclo 1 mostra

![Preenchimento do ciclo 1 — por faixa: 23,6% na Faixa 3, 37,4% na Faixa 2, 31,6% na Faixa 1; por território: 44,9% metropolitano, 35,6% capitais, 26,9% interior conectado, 20,5% interior remoto](../../../output/apresentacao_banca1/preenchimento_ciclo1.png)

Das **1.295 células** da primeira chamada, **393 (30,3%)** tiveram alguém
confirmado ou homologado.

### A leitura

- **Por faixa, não há ordem.** Pagar o dobro (31,6%) não preencheu mais que
  pagar uma vez e meia (37,4%).
- **Por território, há.** De **44,9%** no metropolitano a **20,5%** no interior
  remoto.

> **Isto é descrição, não efeito.** As faixas diferem em muito mais que na
> bolsa, e território prevê melhor que ela. Linguagem correta: **gradiente** e
> **associação**.

### A literatura aponta para os dois lados

| Pagar mais funciona | Pagar mais não basta |
|---|---|
| **México, salário sorteado.** Em 106 postos, salário **33% maior** elevou a aceitação em **15 p.p.**; a mais de 200 km da cidade natal, de 25% para cerca de **80%**, sem perda de qualificação. | **Brasil, o programa-irmão.** No Mais Médicos, **+15,1** médicos do programa por 100 mil viraram **+5,7** de expansão **líquida**. O resto substituiu quem já estava lá. |
| **O degrau tem o tamanho que a literatura pede.** O prêmio exigido para um posto pior vai de **37% a 64%** da renda anual, e a elasticidade da oferta no interior é **0,7**. O degrau do PMM-E é **+50%**. | **Austrália, a maioria não vai por preço.** De 3.727 clínicos, **65%** ficaram onde estavam em **todos** os cenários. Para o pior posto, quem mudaria pedia **130%** da renda anual. |

**Ressalva:** os percentuais são sobre a **renda total** do médico; a bolsa
remunera **20 horas**.

> **A evidência não decide se um degrau de R$ 5 mil basta.**

**Fontes:** Dal Bó, Finan & Rossi (2013), *QJE*; Scott et al. (2013), *Soc Sci
Med* 96; Hone et al. (2020), *BMC HSR* 20:873. Ciclo 1:
`output/tema_trabalho/`, módulos A4 e A5.

> [!NOTE]
> **Nota de produção — dois de cada lado, e o que saiu.** A tabela tinha dois a
> favor e **quatro** contra. Ficaram os dois que atacam elos distintos: a
> **expansão líquida** (Hone) e a **não resposta a preço** (Scott). Saíram da
> tela, e ficam de reserva para pergunta da banca: **Costa, Nunes & Sanches
> (2024)**, *REStat* — subir 50% o salário público no interior do N e NE
> corrige **12,4%** do desequilíbrio a **US$ 15,7 mi** por ponto, contra
> **63,8%** por US$ 2,2 a 5,1 mi reservando vaga na faculdade para quem nasceu
> ali; e **Pathman, Konrad & Ricketts (1992)**, *JAMA* — oito anos depois,
> **12%** dos que foram por obrigação seguiam lá, contra **39%** dos que foram
> sem. Costa et al. continua citado no slide 10.

> [!NOTE]
> **Nota de produção — o que saiu da leitura.** Saíram dois números que são
> **saída de estimação**, e a banca 1 não apresenta resultado de estimação:
> **+0,50** especialista cadastrado por célula com atração em mar/2026, erro
> padrão **0,234**; e o contraste ajustado de **+20,9 p.p.** do estrato
> metropolitano. O gradiente bruto por território continua na tela, na figura e
> na leitura. A série mensal por faixa é reprodutível e pode entrar como
> contexto descritivo; a tabela de inclinações pré/pós do deck do grupo, não —
> motivo e critério de fechamento na **pendência 4**.

---

## A pergunta que organiza o trabalho

`1. Motivação e Pergunta · Pergunta de Pesquisa`

### A cadeia que a política supõe

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

**Verde e cheia:** está em ato oficial. **Laranja e tracejada:** suposição.
Nem o elo cheio seguinte assegura **oferta líquida**: o edital só veda
substituição de quem já está lá.

### A pergunta

> ### O incentivo financeiro oferecido pelo PMM-E funciona para atrair especialistas para regiões mais vulneráveis?

Dois objetos, um contra o outro:

- o **preço** que a política pôs sobre a vulnerabilidade, o degrau de **R$ 5 mil**;
- a **desvantagem** que esse preço pretende compensar.

A margem observada é o **preenchimento da vaga** — o terceiro elo da cadeia, e o
primeiro elo suposto é a hipótese do trabalho. Permanência fica fora desta banca.

**Fontes:** Lei nº 15.233/2025; Edital SGTES/MS nº 3/2025, item 1.2.5;
[`01_pergunta_escopo/15`](../../01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md).

> [!NOTE]
> **Nota de produção.** O diagrama veio do slide 5 em 17/09/2026. É onde ele
> trabalha: separa os elos **escritos em ato oficial** dos que são **suposição
> do programa**, e é isso que torna a pergunta inevitável em vez de retórica.
> Formulação canônica equivalente, em
> [`01_pergunta_escopo/15`](../../01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md):
> *"maiores bolsas do PMM-E para municípios mais vulneráveis compensam suas
> desvantagens territoriais na atração de médicos especialistas?"*. No Beamer o
> diagrama é a cadeia TikZ horizontal de seis nós em `font=\tiny`, compilada em
> 16/09/2026 sem Overfull.

---

# 2. Literatura Teórica e Modelo Microeconômico

### De onde vem a equação de escolha, e o que há dentro do custo

`sem rastreio`

---

## A escolha locacional maximiza a renda real líquida

`2. Literatura e Modelo · Visão geral`

### A equação de escolha

**Moehling, Niemesh, Thomasson & Treber (2020)**, eq. 1, p. 184: o médico escolhe
a localidade que maximiza o valor presente do rendimento **real**, líquido do
custo não pecuniário de viver ali.

$$\arg\max_{i \in I} \left\{ \sum_t \delta^t \left[ \frac{\mathbb{E}(w_{it}^{(s)})}{p_{it}} - c_{it}^{(s)} \right] \right\}$$

| Termo | O que é |
|---|---|
| $i \in I$ | **localidades** candidatas |
| $\mathbb{E}(w^{(s)}_{it})$ | salário esperado em $i$, no ano $t$, na especialidade $s$ |
| $p_{it}$ | nível de preços local, o deflator |
| $c^{(s)}_{it}$ | custo **não pecuniário** de viver ali |
| $\sum_t \delta^t$ | a escolha é de **carreira**, não de um mês |

### O que a conta faz, e o que ela esconde

Deflaciona o salário, subtrai o custo do lugar, desconta a carreira inteira com
o fator $\delta$ e devolve a de maior valor. **A partir do slide 10, $i$ indexa o
médico e $m$ o município** — aqui, $i$ ainda é a localidade.

> **Salário nominal alto não compensa preços e custos locais altos.**

Mas, para os próprios autores, $c$ reúne *"preferences over rural or urban
living … such as proximity to family"* — uma **caixa-preta**. Os dois slides
seguintes a abrem: primeiro o **custo** do lugar, depois a **remuneração** dele.

**Fontes:** Moehling et al. (2020), *Cliometrica* 14, p. 184, eq. 1;
[`modelo_micro.md`](../../02_teoria/modelo_micro.md), §1.

---

## O custo da localidade tem duas metades: o lugar e o trabalho

`2. Literatura e Modelo · Custo da localidade`

### O lugar

**Redding & Rossi-Hansberg (2017)**, eq. 24, p. 28:

$$u_{nio} = \frac{z_{nio}\, B_n\, w_i}{\kappa_{ni}\, Q_n^{\,1-\beta}}
\quad\Longrightarrow\quad
c^{\text{geo}}_{im} = \phi(\text{dist}_{im}) - \gamma A_m + \theta_i^{\text{rural}}$$

No numerador, o que **atrai**: o salário $w_i$, as amenidades $B_n$ e o gosto
pessoal $z_{nio}$. No denominador, o que **repele**: o deslocamento
$\kappa_{ni}$ e a moradia $Q_n$, elevada à fração da renda gasta com ela. Daí:
afastar-se da família custa mais a cada quilômetro ($\phi' > 0$); a amenidade
urbana compensa; o gosto por cidade pequena não tem sinal universal.

> **Atenção ao símbolo $B$.** Aqui $B_n$ é **amenidade** e, no passo seguinte,
> $B(q)$ é **benefício ao paciente**. A **bolsa** é $B_m$, só no slide 11.

### O trabalho

**Choné & Ma (2011)**, eq. 1, p. 232:

$$U = R - C(q; L, K) + \alpha B(q)
\quad\Longrightarrow\quad
c^{\text{laboral}}_{im} = C(q; L_m, K_m) - \alpha_i B(q; L_m, K_m)$$

O médico soma a receita $R$, subtrai o custo de esforço de produzir a
quantidade $q$ e soma o benefício ao paciente $B(q)$, ponderado pelo altruísmo
$\alpha$. Atender cansa de forma crescente ($C'' > 0$); curar dá satisfação decrescente,
porque a triagem prioriza o caso grave ($B'' < 0$). O custo marginal
$c'(q) = C' - \alpha B'$ tem **sinal incerto**, mas $c'' \gg 0$: a curva é um
**U** — atender mais reduz o custo líquido até um mínimo, e depois exaure.

**Equipe e capital atuam duas vezes.** Reduzem o cansaço e **ampliam o
benefício**, $\partial B/\partial K > 0$ — este segundo canal é **extensão deste
projeto**, motivada por Reinhardt. Por dois caminhos,
$\partial c^{\text{laboral}}/\partial K < 0$.

### As quatro desvantagens, na visão do médico

| Desvantagem | Bloco | Medimos? |
|---|:---:|:---:|
| **Retaguarda profissional** — sem segunda opinião nem a quem encaminhar | $L$ | sim, colegas no CNES |
| **Infraestrutura** — atender cansa mais e resolve menos | $K$ | em parte |
| **Distância da família** | $\phi(\text{dist})$ | não |
| **Mercado privado ausente** — a renda se reduz ao que o programa paga | $w^{\text{priv}}$ | não, ver slide 11 |

No Brasil, entre 50 mil generalistas formados de 2001 a 2013, **a proximidade do
lugar de nascimento ou de formação é o principal fator**; salário e
infraestrutura pesam menos.

**Limitação assumida:** CNES e edital não informam a residência do profissional,
por sigilo fiscal. A unidade é o **município do estabelecimento**; a distância
entra como latente.

**Fontes:** Redding & Rossi-Hansberg (2017), *Annual Review of Economics* 9;
Choné & Ma (2011), *IJHCFE* 11; Reinhardt (1972, 1975); Costa, Nunes & Sanches
(2024), *REStat*; [`modelo_micro.md`](../../02_teoria/modelo_micro.md), §2 e §3.2.

---

## A bolsa não é toda a remuneração da localidade

`2. Literatura e Modelo · Remuneração da localidade`

### A bolsa compra 20 horas; o resto é mercado local

$$\mathbb{E}(w_{imt} \mid B_m) = \underbrace{B_m}_{\text{fixado pela regra}} + \underbrace{w^{\text{priv}}_m}_{\text{mercado local}}$$

| | Capital ou metrópole | Interior isolado |
|---|---|---|
| **Bolsa $B_m$** | R$ 10 mil | R$ 20 mil |
| **Mercado $w^{\text{priv}}_m$** | alto | ausente |
| **Total** | pode superar R$ 20 mil | $w \to B$: a bolsa é **tudo** |
| **Deflator $p_m$** | custo de vida alto | custo de vida baixo |

### A consequência é contraintuitiva

A bolsa do interior é o **dobro** da da capital, e ainda assim a **remuneração
total** pode ser **menor** lá. O deflator puxa no sentido oposto, e não se sabe a
priori qual força vence.

> **Pela dupla prática do slide 4, $w^{\text{priv}} > 0$ é a regra, não a exceção.**

A política aposta que R$ 5 mil compensam o lugar. O modelo diz que eles competem
com um mercado privado cuja ausência é, ela própria, uma desvantagem do lugar.

**Fontes:** [`modelo_micro.md`](../../02_teoria/modelo_micro.md), §3;
[`hipoteses_e_viabilidade_empirica.md`](../../02_teoria/hipoteses_e_viabilidade_empirica.md), §2;
Edital SGTES/MS nº 3/2025, item 11.3.b.

---

# 3. Hipótese e Viabilidade Empírica

### O que o modelo implica, o que se testa e o que os dados permitem

`sem rastreio`

---

## No PMM-E, a regra fixa a remuneração e o IVS organiza o custo

`3. Hipótese e Viabilidade · Implicações para o PMM-E`

### O modelo integrado

$$V_{im} = \sum_t \delta^t \left[ \frac{\mathbb{E}(w_{imt} \mid B_m)}{p_{mt}} - c_{im} \right] + \varepsilon_{im}$$

para o médico $i$ no município $m$, com
$\mathbb{E}(w \mid B_m) = B_m + w^{\text{priv}}_m$ do slide 11 e
$c_{im} = c^{\text{geo}}_{im} + c^{\text{laboral}}_{im}$ do slide 10.

| Termo | Variável do programa | Derivada | Leitura |
|---|---|:---:|---|
| $B_m$ | valor da bolsa | $\partial V/\partial B_m > 0$ | é o instrumento |
| $w^{\text{priv}}_m$ | mercado local, não observado | $\partial^2 V/\partial B_m \partial w^{\text{priv}} < 0$ | a bolsa vale mais onde não há mercado |
| $p_m$ | custo de vida, por UF | $\partial V/\partial p_m < 0$ | opera contra a vulnerabilidade |
| $c_{im}$ | **IVS** e suas dimensões | $c_0'(IVS) \gtrless 0$ | **sinal ambíguo** |

> **O que Moehling, Redding & Rossi-Hansberg e Choné & Ma não têm:** remuneração
> fixada por **regra pública sobre um índice territorial**. É só isso que a
> adaptação ao PMM-E acrescenta.

### Por que o IVS organiza o custo

Distância, aluguel, mercado privado e esforço clínico **não são observados**. O
IVS é. Escrevemos $c_{im} = c_0(IVS_m) + \eta_i$ — e isso não é atalho.

O **IVS 2010 do Ipea** resume, de 0 a 1, dezesseis indicadores do Censo 2010 em
três dimensões — e **cada uma é um bloco do custo**:

| Dimensão do IVS | Indicadores | Bloco do custo | Efeito |
|---|---|---|:---:|
| Infraestrutura urbana | saneamento, lixo, tempo de deslocamento | amenidades $A_m$ | $\uparrow$ |
| Renda e trabalho | pobreza, desemprego, informalidade | mercado privado ausente, $w \to B$ | $\uparrow$ |
| Capital humano | mortalidade infantil, analfabetismo, mães adolescentes | gravidade $\uparrow$; escassez de $L$ e $K$ | **ambíguo** |

A terceira linha impede assumir que o custo cresce com o índice: carência
sanitária **eleva o benefício** de atender, o que **reduz** o custo para um médico
altruísta, e ao mesmo tempo sinaliza falta de insumo, o que **eleva** o cansaço.

> **Por isso o objeto é o degrau da bolsa entre faixas, não a inclinação do índice.**

**Fontes:** [`modelo_micro.md`](../../02_teoria/modelo_micro.md), §2.4, §3 e §3.1;
[`hipoteses_e_viabilidade_empirica.md`](../../02_teoria/hipoteses_e_viabilidade_empirica.md), §3.

---

## Da condição de aceitação sai a hipótese

`3. Hipótese e Viabilidade · Hipótese do trabalho`

### A condição de aceitação

O médico $i$ aceita a vaga em $m$ quando ela supera sua melhor alternativa
$\bar{v}_i$:

$$\frac{B_m + w^{\text{priv}}_m}{p_m} - c_0(IVS_m) \;\geq\; \bar{v}_i$$

A vaga é preenchida se existir **ao menos um** candidato para quem isso vale.
Tudo que aumenta o lado esquerdo aumenta essa probabilidade.

### A hipótese

> ### H1 — Uma elevação na remuneração oferecida pelo PMM-E eleva a taxa de preenchimento das vagas ofertadas

$$\frac{\partial \Pr(\text{preenchimento}_m)}{\partial (B_m / p_m)} > 0$$

**O custo é obstáculo, não hipótese.** Ele não varia livremente: a regra do
edital o amarra à bolsa, e os dois sobem juntos. Na fronteira entre faixas, o
preenchimento do lado mais vulnerável exige

$$\frac{\Delta B_m}{p_m} > \Delta c_0, \qquad \Delta B_m = \text{R\$ } 5.000$$

> **A pergunta da apresentação é se essa desigualdade vale.**

**Fontes:** [`modelo_micro.md`](../../02_teoria/modelo_micro.md), §4.1 e §4.2;
[`hipoteses_e_viabilidade_empirica.md`](../../02_teoria/hipoteses_e_viabilidade_empirica.md), §4.2.

---

## Há dado para quase todo termo — e sabemos quais faltam

`3. Hipótese e Viabilidade · Disponibilidade de dados`

### O que observamos

| Termo | O que observamos | Fonte | Grau |
|---|---|---|:---:|
| **Preenchimento** | confirmação ou homologação por célula estabelecimento–curso, **ciclo 1** | quadros do edital | 🟢 direto |
| **Bolsa $B_m$** | faixa anunciada em cada vaga e seu valor | edital e quadro de vagas, ciclos 1 a 3 | 🟢 direto |
| **Custo de vida $p_m$** | diferenças entre estados, por efeito fixo de UF | IBGE | 🟡 proxy |
| **Custos geográficos** | amenidades pelo sub-índice de infraestrutura e pela tipologia em 4 estratos | Ipea; REGIC 2018 e RMs 2022 | 🟡 proxy |
| **Equipe $L$** | colegas da especialidade no município, 12 meses prévios | CNES mensal | 🟡 proxy |

### O que falta

| Termo | Por quê |
|---|---|
| **Remuneração total** ($B + w^{\text{priv}}$) | RAIS nunca adquirida; CNES não traz renda nem carga horária |
| **Distância da família** | residência do profissional é sigilo fiscal |
| **Custo de moradia** | sem fonte municipal no repositório |
| **Capital $K$** | mapeado, mas as competências do CNES físico não foram baixadas |
| **Volume e gravidade $q$** | SIH existe só como pré-tratamento de outro módulo, e está bloqueado |

**Sim, para o essencial:** desfecho e instrumento são diretos; o custo entra por
proxies declaradas.

> **As duas ausências que mais doem — mercado local e distância da família — são
> justamente os termos que o modelo diz serem decisivos.** Elas entram como parte
> do custo que o IVS e a tipologia resumem. Isso é uma escolha, não uma solução.

**Fontes:** [`04_dados/02_inventario_dados_por_outcome.md`](../../04_dados/02_inventario_dados_por_outcome.md);
[`hipoteses_e_viabilidade_empirica.md`](../../02_teoria/hipoteses_e_viabilidade_empirica.md), §3;
`output/tema_trabalho/`, `output/aquisicao/` e `output/rdd_bolsa/`.

---

## Separar o efeito da bolsa do efeito da vulnerabilidade

`3. Hipótese e Viabilidade · Desafio metodológico`

### O problema, e a resposta natural

**O problema.** A regra dá mais dinheiro exatamente aos municípios mais
difíceis. Comparar Faixa 1 com Faixa 3 compara, ao mesmo tempo, **R$ 10 mil a
mais** e **todas as desvantagens** que levaram àquela faixa.

**A resposta natural.** Se o valor vem de um corte no IVS, municípios logo acima
e logo abaixo são quase iguais em tudo, menos na bolsa. É uma **regressão
descontínua** — e reconstruir a regra era o primeiro passo do trabalho empírico.

### Ele foi dado, em 14/09/2026, e tem três resultados

| | Achado | Número |
|:---:|---|---|
| **1** | **Há suporte comum** | 37 municípios com IVS ≤ 0,400 na Faixa 1 e 94 na Faixa 2; os intervalos das faixas se sobrepõem |
| **2** | **Mas não há descontinuidade nos cortes** | em `0,500`, os dois lados são **100% Faixa 1** até ±0,050; em `0,400`, o maior IVS da Faixa 3 é `0,372` |
| **3** | **E a variação restante não é exógena** | dos 83 fora da melhor regra, os 41 promovidos têm mediana de população **7.933** contra **32.179** dos 42 rebaixados, e muito mais interior remoto |

| Figura na tela | O que mostra |
|---|---|
| **A descontinuidade que não existe** | IVS 2010 contra a **faixa publicada**, com `0,400` e `0,500` marcados: faixas sobrepostas e salto nulo nos cortes. **A gerar**, pendência 7 |

**Por que o item 3 é fatal.** A remoticidade é o previsor mais forte do
preenchimento. Parear por IVS **confunde bolsa com posição territorial**, e o
viés funciona **contra** a bolsa — podendo inverter o sinal do que se estimaria.

### Conclusão, e o que fica de pé

> **O efeito causal do valor da bolsa não é identificável com fontes públicas.**
> A razão não é potência amostral: é que o IVS é o **piso** da bolsa, não o
> critério. Destravá-lo exige o **Anexo IV** e os critérios da cláusula 11.1.3,
> que só o Ministério pode fornecer. O pacote de solicitação está pronto; o envio
> é decisão do autor.

- **A pergunta continua sendo a pergunta.** Ela não depende do desenho.
- **Faixa e preenchimento viram gradiente**, não efeito, até a regra ser recuperada.
- **Há um desenho causal vivo, para outra pergunta.** A descontinuidade no
  **escore do candidato** compara o último selecionado com o primeiro não
  selecionado na **mesma** célula curso–estabelecimento. Ali a bolsa é constante:
  ele identifica o efeito de **ganhar a vaga**, não o do valor da bolsa.

**Fontes:** [`05_identificacao/14_plano_implementacao_rdd_bolsa.md`](../../05_identificacao/14_plano_implementacao_rdd_bolsa.md);
[`05_identificacao/16_sintese_achados_e_novo_plano_causal.md`](../../05_identificacao/16_sintese_achados_e_novo_plano_causal.md), §3.5, §3.5.1 e §6;
[`06_execucao/36_backlog_pos_auditoria.md`](../../06_execucao/36_backlog_pos_auditoria.md), item D-3.

---

<!-- deck:fim -->

## Pendências abertas em 17/09/2026

Registradas aqui porque afetam o que vai à tela. Detalhe e rastreio em
[03 — Proveniência](03_proveniencia_figuras_e_numeros.md).

| # | Pendência | Efeito | O que fecha |
|:---:|---|---|---|
| **1** | ✅ **Fechada em 17/09/2026 quanto ao pipeline, aberta quanto à cobertura.** As três figuras do slide 4 passaram a sair de `gerar_figuras_banca1.py`. Mas a figura de UF do deck do grupo **não era usável**: calibrada pelos dois rótulos impressos, ela põe **SP em ≈ 419** e **PA em ≈ 135**, contra os **244** e **70** da série citada na proveniência — só os dois extremos rotulados batem. A figura nova é dos **quatro** valores com fonte registrada, não das 27 UFs | a tela perde o panorama completo por UF | registrar em `data/raw/` a tabela por UF da *Demografia Médica 2025*, com hash, e trocar a figura dos extremos pela das 27 unidades |
| **2** | Os valores do gráfico de deslocamento (Norte 276 km … Sul 101 km) **não tiveram a fonte primária confirmada**. Desde 17/09/2026 a figura é gerada por script, e o rodapé dela diz *"atribuído à REGIC 2018 (IBGE); fonte primária a confirmar"* — o pipeline não confirma fonte | número em tela sem rastreio | localizar a tabela da REGIC 2018 sobre deslocamentos para serviços de saúde e registrar o arquivo em `data/raw/` |
| **3** | A proveniência registrava "10% dos cirurgiões atuando exclusivamente no SUS"; a fonte primária diz **7,7%** | número errado, agora corrigido no slide 4 | ✅ corrigido em 16/09/2026; PDF da *Demografia Médica 2025* a registrar em `data/raw/` com hash |
| **4** | A tabela de inclinações pré/pós por faixa do deck do grupo (0,012 / 0,271 …) **não é reproduzível** a partir do repositório e não tem grupo de comparação | seria resultado sem rastreio | mantida **fora** do slide 6; a série mensal por faixa é reprodutível e pode entrar como contexto descritivo |
| **5** | "Sudeste 55,4% dos especialistas" está conferido em **cobertura**, não localizado no PDF integral | ressalva de fonte | conferir na *Demografia Médica 2025* ao registrar o PDF |
| **6** | Os decks Beamer e Slidev ainda estão na estrutura de **15 slides**; a estrutura vigente tem 16 slides e **32 builds** | divergência deck × documento | reconstruir os dois decks sobre esta estrutura |
| **7** | O slide 16 pede uma figura que ainda **não existe**: IVS contra faixa publicada, com os cortes marcados | o slide fica só em texto, e o achado central da viabilidade fica sem imagem | acrescentar a figura a `gerar_figuras_banca1.py`, lendo `output/rdd_bolsa/matriz_municipio_regra_ivs.csv` |
| **8** | **Decisão do autor, do PR de ajuste estrutural (F5).** A retaguarda do slide 5 é medida no **município**, mas 42,6% das células estão em estabelecimento de gestão estadual e 93 dos 460 CNES têm "REGIONAL" no nome: o incentivo é fixado pelo IVS do município-sede e a clientela é regional | ou o slide ganha uma linha de limitação, ou o descasamento vira argumento próprio da motivação | decisão do autor; o teste de deslocamento intrarregional depende da malha territorial versionada (F4 do mesmo PR) |

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
