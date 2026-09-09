# Conteúdo da apresentação — banca 1

> Conteúdo integral da apresentação, em markdown, para ler de ponta a ponta.
> Cada seção é um slide; o cabeçalho é o título do slide. A linha em `código` é
> o rastreio de seção, exibido fora do título.
> **Atualização:** 9 de setembro de 2026.

---

## 1 — Capa

`sem rastreio`

# Desvantagens territoriais na escolha locacional de médicos especialistas

### Um modelo microeconômico para o preenchimento de vagas do Programa Mais Médicos Especialistas

Autoria · instituição · data da banca

---

## 2 — Sumário

`sem rastreio`

**Parte I — Introdução**
1. Motivação
2. Pergunta

**Parte II — Teoria**
3. Literatura teórica
4. Modelo microeconômico
5. Hipóteses

**Parte III — Empiria**
6. Viabilidade empírica

---

# Parte I — Introdução

## 3 — Faltam especialistas justamente onde trabalhar é mais difícil

`Parte I · Motivação · 1 de 3`

Quando um médico decide onde clinicar, o município vulnerável chega com quatro
desvantagens. Duas delas nós medimos:

![Especialistas por 100 mil habitantes em junho de 2025, por faixa de bolsa](../../../output/apresentacao_banca1/oferta_pre_por_faixa.png)

**A oferta é escassa onde a vulnerabilidade é alta.** Nos municípios que
receberam vaga, havia **16,0 especialistas por 100 mil habitantes** onde a bolsa
seria de R$ 10 mil e **7,3** onde seria de R$ 20 mil — menos da metade, antes de
o programa começar.

![Colegas da mesma especialidade no município, junho de 2025](../../../output/apresentacao_banca1/retaguarda_por_faixa.png)

**E quem vai trabalha sozinho.** O especialista que fosse para um município de
Faixa 1 encontraria **2 colegas da sua especialidade**, contra 5 na Faixa 3. Em
**42%** dos casos seria o único, ou teria um único colega — sem escala, sem
segunda opinião, sem retaguarda para o caso difícil.

**As outras duas desvantagens a literatura documenta, e nossos dados não
alcançam:** a distância da família e o isolamento; e a ausência de mercado
privado local, que faz a remuneração colapsar no valor da bolsa, sem a
complementação de renda que o médico teria na capital.

**Fontes:** CNES, competência 06/2025, CBOs dos 10 cursos do programa com
correspondência unívoca curso–CBO, 295 municípios com vaga no ciclo 1;
população residente do Censo 2022 (IBGE). A Faixa 1 tem só 19 pares
município–especialidade, então a porcentagem oscila com poucos casos; a mediana
não.

---

## 4 — O PMM-E paga mais onde a vulnerabilidade é maior

`Parte I · Motivação · 2 de 3`

O Mais Médicos Especialistas (Lei nº 15.233/2025) paga uma **bolsa-formação
mensal** por vaga — 20 horas semanais em estabelecimento do SUS, por até 12
meses. O valor não é uniforme: depende da vulnerabilidade do município.

**Como o valor é definido, em três passos:**

1. **O índice.** O IVS 2010 do Ipea resume, em um número de 0 a 1, dezesseis
   indicadores do Censo 2010, em três dimensões: infraestrutura urbana
   (saneamento, lixo, tempo de deslocamento), capital humano (mortalidade
   infantil, analfabetismo, crianças fora da escola) e renda e trabalho
   (pobreza, desemprego, informalidade).
2. **A categoria.** O Ipea corta o índice em cinco faixas: muito baixa
   (até 0,200), baixa (0,201–0,300), média (0,301–0,400), alta (0,401–0,500) e
   muito alta (acima de 0,500).
3. **O valor.** O edital de 2025 agrupou as cinco categorias em três faixas de
   bolsa.

| Categoria de IVS | Faixa | Bolsa mensal |
|---|:---:|---:|
| muito alta | 1 | R$ 20.000 |
| alta | 2 | R$ 15.000 |
| média, baixa ou muito baixa | 3 | R$ 10.000 |

![Bolsa mensal por faixa de atração](../../../output/apresentacao_banca1/bolsa_por_faixa.png)

A bolsa, portanto, não remunera o médico pelo que ele produz nem pelo mercado
local: **remunera o lugar**. Duas ressalvas: a categoria que vale é a publicada
na vaga, e em **177 dos 368 municípios** do ciclo 1 ela não coincide com a que
se obtém aplicando os cortes do Ipea ao IVS local; e a grade mudou em 2026,
quando a categoria *alta* passou à Faixa 1.

**Fontes:** Lei nº 15.233/2025; Edital SGTES/MS nº 3/2025 e retificação;
Chamamento SGTES/MS nº 1/2026; Ipea, *Atlas da Vulnerabilidade Social nos
Municípios Brasileiros* (2015).

---

## 5 — Pagar mais funciona?

O programa aposta que dinheiro compensa lugar ruim. Essa aposta já foi feita em
outros países, e sabemos três coisas sobre ela.

### Funciona — e funciona mais justamente onde o lugar é pior

No México, um concurso público de verdade **sorteou o salário anunciado** entre
106 postos. Onde o salário era 33% maior, a aceitação da vaga subiu **15 pontos
percentuais**. E nos postos a mais de 200 km da cidade natal do candidato, a
aceitação foi de **25% para cerca de 80%** — o aumento salarial **anulou** a
rejeição a municípios mais pobres.

> Dal Bó, Finan & Rossi (2013), *Quarterly Journal of Economics*

### Mas é caro, e no Brasil pode ser caro demais

Na Austrália, perguntou-se a 3.727 clínicos o que os faria mudar de cidade.
**65% responderam que não mudariam por nada.** Quem mudaria pedia de **37%**
(cidade de 5 a 20 mil habitantes) a **130%** da renda anual (o pior posto).

No Brasil, um modelo calibrado com todos os generalistas formados entre 2001 e
2013 estima que aumentar em **50%** o salário público no interior do Norte e do
Nordeste corrigiria apenas **12,4%** do desequilíbrio na distribuição de
médicos — ao custo de **US$ 15,7 milhões por ponto percentual**. Reservar vagas
nas faculdades de medicina para quem nasceu nessas regiões corrigiria **63,8%**,
por **US$ 2,2 a 5,1 milhões**.

> Scott et al. (2013), *Social Science & Medicine*; Costa, Nunes & Sanches (2024), *Review of Economics and Statistics*

### E o médico vai embora quando a obrigação acaba

Nos Estados Unidos, oito anos depois, **12%** dos médicos que foram para
clínicas rurais com bolsa e obrigação de permanência ainda estavam lá — contra
**39%** dos que foram sem obrigação nenhuma.

> Pathman, Konrad & Ricketts (1992), *JAMA*

### Onde o PMM-E entra

O degrau do programa — R$ 5 mil sobre R$ 10 mil, ou **+50%** — cai dentro da
faixa que essa literatura estima ser necessária para deslocar um médico. Está
no tamanho certo, em tese.

Só que no primeiro ciclo **a bolsa maior não trouxe mais gente**: das 1.295
vagas da primeira chamada, 30,3% tiveram alguém confirmado — **31,6% na Faixa 1,
37,4% na Faixa 2 e 23,6% na Faixa 3**.

**Ressalva:** os percentuais da literatura são sobre a renda total do médico, e
a bolsa do PMM-E remunera 20 horas semanais.

**Fontes:** referências citadas acima; quadro de vagas e resultados do ciclo 1,
chamada 1 (Ministério da Saúde, 2025).

---

## 6 — Pergunta

`Parte I · Pergunta`

> **Maiores bolsas do PMM-E para municípios mais vulneráveis compensam suas
> desvantagens territoriais na atração de médicos especialistas?**

---

# Parte II — Teoria

## 7 — De onde vem o modelo

| Referência | Ideia central | Equação original |
|---|---|---|
| **Moehling, Niemesh, Thomasson & Treber (2020)**, eq. 1, p. 184 | O médico escolhe a localidade que maximiza o valor presente do rendimento real, líquido do custo não pecuniário de viver ali | $\arg\max_{i \in I} \sum_t \delta^t \left[ \dfrac{\mathbb{E}(w_{it}^{(s)})}{p_{it}} - c_{it}^{(s)} \right]$ |
| **Choné & Ma (2011)**, eq. 1, p. 232 | A utilidade do médico soma a renda, subtrai o custo de atender e soma o benefício ao paciente, ponderado pelo altruísmo. Equipe e capital instalado entram no custo de atender | $U = R - C(q; L, K) + \alpha B(q)$ |
| **Redding & Rossi-Hansberg (2017)**, eq. 24, p. 28 | A utilidade de trabalhar em um lugar depende do salário, das amenidades e do custo de moradia locais | $u_{nio} = \dfrac{z_{nio} B_n w_i}{\kappa_{ni} Q_n^{1-\beta}}$ |

---

## 8 — Como o médico escolhe onde trabalhar

`Parte II · Modelo microeconômico · 1 de 2`

Adaptando Moehling et al. (2020), o médico $i$ escolhe o município $m$ que
maximiza o valor presente líquido da carreira:

$$V_{im} = \sum_t \delta^t \left[ \frac{\mathbb{E}(w_{imt} \mid B_m)}{p_{mt}} - c_{im} \right] + \varepsilon_{im}, \qquad m_i^{\ast} \in \arg\max_{m \in \mathcal{M} \cup \{0\}} V_{im}$$

| Termo | Leitura |
|---|---|
| $\mathbb{E}(w_{imt} \mid B_m)$ | A remuneração esperada tem duas partes: a bolsa $B_m$, fixada pela regra, e o que o médico obtém no **mercado local**, $w^{\text{priv}}_m$. Na capital, $w = B + w^{\text{priv}}$; no interior isolado, sem demanda privada, $w \to B$. A bolsa precisa compensar também a renda privada que o médico deixa de ganhar |
| $p_{mt}$ | O que importa é a remuneração **real**, deflacionada pelo custo de vida local |
| $c_{im}$ | Tudo o que torna estar naquele município custoso e não é pago em dinheiro |

A alternativa $m = 0$ é ficar fora do programa. A vaga em $m$ é aceita quando
$V_{im} \geq V_{i0}$.

---

## 9 — O custo de estar ali

`Parte II · Modelo microeconômico · 2 de 2`

$$c_{im} = \underbrace{\phi(\text{dist}_{im}) - \gamma A_m + \theta_i^{\text{rural}}}_{\text{geográfico}} + \underbrace{C(q; L_m, K_m) - \alpha_i B(q; L_m, K_m)}_{\text{laboral líquido}}$$

| Componente | Sinal | Significado |
|---|:---:|---|
| $\phi'(\text{dist})$ | $> 0$ | Afastar-se da família custa, e custa mais a cada quilômetro |
| $-\gamma A_m$ | $< 0$ | Amenidade urbana compensa |
| $C(q)$ | $C' > 0,\ C'' > 0$ | Atender cansa, e cansa de forma crescente |
| $\alpha_i B(q)$ | $B' > 0,\ B'' < 0$ | Curar dá satisfação, ponderada pelo altruísmo $\alpha_i$ |

Equipe ($L$) e capital instalado ($K$) atuam duas vezes: reduzem o cansaço,
$\partial C / \partial K < 0$, e — nossa extensão a Choné & Ma — ampliam o
benefício que o atendimento produz, $\partial B / \partial K > 0$. Por dois
caminhos, então, $\partial c / \partial K < 0$. Como no município vulnerável
$L$ e $K$ são baixos, **o mesmo lugar que paga mais é o que impõe maior custo
de trabalho**.

![Custo laboral líquido em função do volume de atendimentos](../../02_teoria/figuras/curva_custo_laboral_burnout.png)

---

## 10 — Duas hipóteses

`Parte II · Hipóteses`

Escrevendo o custo latente como função da vulnerabilidade,
$c_{im} = c_0(IVS_m) + \eta_i$, o médico aceita a vaga em $m$ quando

$$\frac{B_m + w^{\text{priv}}_m}{p_m} - c_0(IVS_m) \geq \bar{v}_i$$

A vaga é preenchida se existir ao menos um candidato para quem a desigualdade
vale. Derivando:

| | Hipótese | Derivada |
|:---:|---|---|
| **H1** | Maior remuneração real aumenta a probabilidade de preenchimento da vaga | $\dfrac{\partial \Pr(\text{preenchimento}_m)}{\partial (B_m / p_m)} > 0$ |
| **H2** | Maior custo locacional reduz a probabilidade de preenchimento da vaga | $\dfrac{\partial \Pr(\text{preenchimento}_m)}{\partial c_m} < 0$ |

Na fronteira entre duas faixas, as duas se encontram em uma única condição: o
preenchimento do lado mais vulnerável exige que o degrau monetário supere o
degrau de custo,

$$\frac{\Delta B_m}{p_m} > \Delta c_0, \qquad \Delta B_m = \text{R\$ } 5.000$$

---

# Parte III — Empiria

## 11 — Viabilidade empírica

**Temos como medir cada peça do modelo?**

| Peça do modelo | O que observamos | Fonte |
|---|---|---|
| Preenchimento da vaga | se a vaga teve alguém confirmado ou homologado | quadro de vagas do ciclo 1: 1.295 vagas em 368 municípios |
| Bolsa $B_m$ | o valor anunciado na vaga: R$ 10, 15 ou 20 mil | edital |
| Custo $c_m$ | o IVS e suas três dimensões; se o município é capital, metropolitano, polo do interior ou interior remoto; quantos especialistas já havia antes | Ipea; REGIC 2018; CNES mensal, jun/2024 a jul/2026 |
| Mercado local $w^{\text{priv}}_m$ | — | não observado |

Sim, para o essencial. Duas peças ficam de fora: a **renda que o médico obteria
no mercado privado local** e a **distância até a família**.

**A dificuldade.** A bolsa e a vulnerabilidade andam juntas porque a regra fixa
uma pela outra: **não existe município com bolsa alta e vulnerabilidade baixa**.
Separar o que vem do dinheiro do que vem do lugar exige comparar municípios
parecidos que caíram em faixas diferentes — e a faixa publicada não coincide com
a que sai dos cortes do Ipea em 177 dos 368 municípios do ciclo 1.
