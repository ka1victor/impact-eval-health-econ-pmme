# Conteúdo da apresentação — banca 1

> **Fonte de verdade do que é apresentado.** Cada seção numerada é um slide; o
> cabeçalho é seu título literal e a linha em `código`, o rastreio de seção. Os
> decks em [`deck_beamer/`](deck_beamer/) e [`deck_slidev/`](deck_slidev/) são
> **derivados**: divergência entre deck e este documento é erro do deck.<br>
> **Escopo:** a banca 1 é teórica e termina na viabilidade empírica; não
> apresenta resultado de estimação.<br>
> **Atualização:** 16 de setembro de 2026 — corte de 19 para 15 slides, ver
> [roteiro, seção 4d](01_roteiro_narrativo.md#4d-corte-de-16092026--de-19-para-15-slides).

---

## 1 — Capa

`sem rastreio`

# Desvantagens territoriais na escolha locacional de médicos especialistas

### Um modelo microeconômico para o preenchimento de vagas do Programa Mais Médicos Especialistas

Autoria · orientação · instituição · data da banca

*Slots da capa: nome do(s) autor(es); "Orientação:" e nome dos professores;
instituição e logo do Insper; data da banca.*

---

## 2 — Sumário

`sem rastreio`

| # | Seção | Descrição curta (linha auxiliar do sumário) |
|:---:|---|---|
| 1 | Motivação | Por que a pergunta importa |
| 2 | Pergunta | A pergunta de pesquisa |
| 3 | Literatura teórica | As três referências que fundamentam o modelo |
| 4 | Modelo microeconômico | A decisão do médico e o custo do lugar |
| 5 | Hipótese | O que o modelo prevê |
| 6 | Viabilidade empírica | O que os dados permitem testar |

---

# 1. Motivação

## 3 — Especialistas faltam no interior, e o médico sabe por quê

`1. Motivação · O problema`

O Brasil tinha, em 2024, **353 mil médicos especialistas** — 59% dos 597 mil
médicos do país. **55%** estão no **Sudeste** e **6%** no **Norte**; são **453**
por 100 mil habitantes no **Distrito Federal** e **68** no **Maranhão**. O
problema não é o número. É onde eles estão.

**E o problema tem outro lado: a decisão do médico.** Para ele, "município
vulnerável" não é um índice — é um conjunto de desvantagens concretas, e
**duas delas nós conseguimos medir**.

| Desvantagem | O que significa para o médico | Medimos? |
|---|---|:---:|
| **Retaguarda profissional** | sem segunda opinião, sem plantão, sem a quem encaminhar o caso difícil | sim — colegas da especialidade no CNES |
| **Infraestrutura** | equipamento, insumos e equipe escassos: atender cansa mais e resolve menos | em parte — CNES |
| **Distância da família** | viver longe de onde a família está e onde se formou | não |
| **Mercado privado ausente** | a remuneração se reduz ao que o programa paga | não |

**O peso de cada uma, na literatura.** **Brasil**, 50 mil generalistas de 2001
a 2013: **a proximidade do lugar de nascimento ou de formação é o principal
fator**; salário e infraestrutura pesam menos. **Austrália**, 3.727 clínicos:
**65% não mudariam por pacote nenhum**.

Nenhuma dessas desvantagens se resolve sozinha. Em 2025 o Ministério da Saúde
reconheceu **situação de urgência em saúde pública**, por **24 meses**, em razão
do tempo de espera na atenção especializada — e lançou o **Agora Tem
Especialistas**, do qual o **PMM-E** é o braço de provimento.

**Fontes:** Scheffer et al., *Demografia Médica no Brasil 2025* (FMUSP/AMB),
dez/2024; Portaria GM/MS nº 7.061/2025; Costa, Nunes & Sanches (2024),
*REStat*; Scott et al. (2013), *Social Science & Medicine*.

---

## 4 — O que é o PMM-E

`1. Motivação · A política · 1 de 2`

**Lei.** A Lei nº 15.233/2025 criou o Projeto Mais Médicos Especialistas dentro
do Programa Mais Médicos, *"destinado ao provimento de profissionais com vistas
à redução no tempo de espera"* do usuário do SUS *"nas regiões prioritárias"*.

**Quem.** Médicos com diploma brasileiro ou revalidado e **RQE** na área da
vaga. Não é concurso nem emprego: recebem **bolsa-formação** mensal do
Ministério, **sem vínculo**.

**O quê.** **Aprimoramento em serviço** de **12 meses**, **20 horas semanais**
em estabelecimento do SUS, com supervisão e mentoria de instituição formadora.
São **16 cursos** — 6 cirúrgicos e 10 ambulatoriais — com foco no câncer e no
diagnóstico que o SUS mais espera.

**Onde, no primeiro ciclo (julho de 2025).** **1.295 vagas**
estabelecimento–curso em **460 estabelecimentos** e **368 municípios**, em
todas as UFs. O **Nordeste** concentra 39% das vagas; dois terços dos municípios
têm menos de 100 mil habitantes; **18 são capitais**.

O Ministério publica o quadro de vagas — município, estabelecimento e curso — e
cada vaga sai com uma **faixa de bolsa**. É essa regra — e só ela — que o
trabalho estuda.

**Fontes:** Lei nº 15.233/2025, art. 22-D; Portaria GM/MS nº 7.177/2025; Edital
SGTES/MS nº 3/2025 (DOU 24/07/2025), itens 1, 3–5, 10 e 11 e Tabela 3; quadro
de vagas do ciclo 1, chamada 1; Censo 2022 (IBGE).

---

## 5 — A bolsa remunera o lugar

`1. Motivação · A política · 2 de 2`

O valor da bolsa **não** depende da especialidade, da carga nem do que o médico
produz. Depende de **onde fica o município**, em três passos:

1. **O índice.** O **IVS 2010 do Ipea** resume, de 0 a 1, dezesseis indicadores
   do Censo 2010 em três dimensões: *infraestrutura urbana* (saneamento, lixo,
   deslocamento), *capital humano* (mortalidade infantil, analfabetismo,
   crianças fora da escola) e *renda e trabalho* (pobreza, desemprego,
   informalidade).
2. **A categoria.** O Ipea corta o índice em cinco: muito baixa (até 0,200),
   baixa (0,201–0,300), média (0,301–0,400), alta (0,401–0,500) e muito alta
   (acima de 0,500).
3. **O valor.** O edital de 2025 agrupou as cinco em **três faixas**.

| Categoria de IVS | Faixa | Bolsa mensal |
|---|:---:|---:|
| muito alta | 1 | R$ 20.000 |
| alta | 2 | R$ 15.000 |
| média, baixa ou muito baixa | 3 | R$ 10.000 |

![Bolsa mensal por faixa de atração](../../../output/apresentacao_banca1/bolsa_por_faixa.png)

No ciclo 1, **102** municípios foram publicados na Faixa 1, **107** na Faixa 2 e
**159** na Faixa 3.

**O IVS é o piso, não o critério.** O edital tem duas cláusulas. A **11.1.4** dá
a tabela acima. A **11.1.3** diz que o valor segue "critérios de **localização**
e vulnerabilidade definidos de acordo com a faixa de atração definida no **Anexo
IV**" — documento que o edital não reproduz e que não está entre as fontes
preservadas.

O dado tem a forma das duas cláusulas: em **177 dos 368** municípios a faixa
publicada não é a da categoria de IVS, e a divergência tem **uma direção só** —
**zero** municípios abaixo do que a categoria manda, **177** acima. Erro de
medida erraria nos dois sentidos. A categoria fixa um mínimo; a localização
promove 48% dos municípios acima dele.

A grade também mudou em 2026, quando a categoria *alta* passou à **Faixa 1**.
Aplicada ao ciclo 1, essa regra acerta 224 dos 368 contra 191 da de 2025 — e nem
as duas juntas reproduzem o publicado. Vale sempre a **faixa publicada na vaga**.

**Fontes:** Edital SGTES/MS nº 3/2025, itens 11.1.3 e 11.1.4, e retificação; Chamamento
SGTES/MS nº 1/2026; Ipea, *Atlas da Vulnerabilidade Social nos Municípios
Brasileiros* (2015); quadro de vagas do ciclo 1.

---

## 6 — Onde a bolsa é maior, o médico fica sozinho

`1. Motivação · O efeito é incerto · 1 de 3`

**Onde a regra manda o dinheiro?** Nos **295 municípios** com vaga no ciclo 1,
um mês antes da oferta e agrupados pela **faixa efetivamente publicada**, as
duas medidas de oferta discordam — e é a discordância que importa.

![Especialistas por 100 mil habitantes, jun/2025 — 15,0 na Faixa 3, 14,4 na Faixa 2, 18,3 na Faixa 1](../../../output/apresentacao_banca1/oferta_pre_por_faixa.png)

![Colegas da mesma especialidade no município, jun/2025 — mediana de 6,5, 5,0 e 2,5 da Faixa 3 à Faixa 1; em 12%, 18% e 31% dos casos o especialista seria o único ou teria um só colega](../../../output/apresentacao_banca1/retaguarda_por_faixa.png)

**Por habitante, a bolsa maior não vai para onde falta mais** — vai para
municípios pequenos, onde poucos profissionais já produzem taxa alta. **Em
número de colegas, vai.** É o isolamento profissional, não a cobertura
populacional, que a Faixa 1 tem de compensar.

O programa põe **R$ 5 mil a mais** onde o médico trabalharia sozinho. Isso
compensa?

**Fontes:** CNES 06/2025 — profissionais nos CBOs dos 10 cursos com
correspondência unívoca curso–CBO, nos 295 municípios com vaga no ciclo 1;
população do Censo 2022 (IBGE); **faixa pela bolsa publicada em cada vaga**, não
pela categoria de IVS recalculada — as duas divergem em 177 dos 368 municípios
(slide 5). A Faixa 1 tem 150 pares município–especialidade em 85 municípios.

---

## 7 — A evidência não decide se R$ 5 mil bastam

`1. Motivação · O efeito é incerto · 2 de 3`

O programa aposta que dinheiro compensa lugar ruim. A literatura diz que a
aposta tem precedente — e tem limites.

| A favor: pagar mais funciona | Contra: é caro, e não segura |
|---|---|
| **No México, o salário foi sorteado.** Um concurso público real distribuiu **106 postos** em municípios pobres e anunciou, **ao acaso**, dois salários. Onde o salário era **33% maior**, a aceitação subiu **15 pontos percentuais**; a mais de **200 km** da cidade natal, foi de **25% para cerca de 80%** — **sem** atrair candidatos menos qualificados ou motivados. | **Muitos não vão por preço nenhum.** Dos **3.727 clínicos australianos**, **65%** escolheram ficar onde estavam em todos os cenários oferecidos. Para o pior posto, quem mudaria pedia **130%** da renda anual. |
| **O degrau do PMM-E tem o tamanho que a literatura pede.** O que um médico exige para ir a um posto pior vai de **37% a 64%** da renda anual em cidades pequenas (Austrália), e a oferta de médicos no interior brasileiro responde a salário com elasticidade de **0,7**. O degrau do programa — R$ 5 mil sobre R$ 10 mil, ou **+50%** — cai dentro dessa faixa. | **No Brasil, salário compra pouco e custa muito.** Aumentar em **50%** o salário público no interior do Norte e do Nordeste corrigiria **12,4%** do desequilíbrio na distribuição de médicos, a **US$ 15,7 milhões por ponto percentual**. Reservar vagas nas faculdades de medicina para quem nasceu nessas regiões corrigiria **63,8%**, por **US$ 2,2 a 5,1 milhões** o ponto. |
| | **E o médico vai embora quando a obrigação acaba.** Nos Estados Unidos, oito anos depois, **12%** dos médicos que foram para clínicas rurais com bolsa e **obrigação de permanência** ainda estavam lá — contra **39%** dos que foram **sem obrigação nenhuma**. |

**Ressalva:** os percentuais da literatura são sobre a **renda total** do
médico; a bolsa do PMM-E remunera **20 horas semanais**.

Dinheiro move alocação, mas é caro, não move todo mundo e não garante que quem
foi fique. **A evidência não decide se um degrau de R$ 5 mil basta.**

**Fontes:** Dal Bó, Finan & Rossi (2013), *QJE*; Scott et al. (2013), *Social
Science & Medicine*; Costa, Nunes & Sanches (2024), *REStat*; Pathman, Konrad &
Ricketts (1992), *JAMA*.

---

## 8 — No primeiro ciclo, a bolsa maior não ordenou o preenchimento

`1. Motivação · O efeito é incerto · 3 de 3`

Das **1.295 vagas** da primeira chamada, **30%** tiveram alguém confirmado ou
homologado.

![Preenchimento do ciclo 1 — por faixa: 23,6% na Faixa 3, 37,4% na Faixa 2, 31,6% na Faixa 1; por território: 44,9% metropolitano, 35,6% capitais, 26,9% interior conectado, 20,5% interior remoto](../../../output/apresentacao_banca1/preenchimento_ciclo1.png)

Os números ficam rotulados na figura e não se repetem em texto:

- Por **faixa de bolsa**: pagar o dobro não preencheu mais que pagar uma vez e
  meia.
- Por **território**: o preenchimento cai da capital e da região metropolitana
  para o interior ligado a um polo, e é **menor no interior remoto**.

Isso é **descrição, não efeito**: as faixas diferem em muito mais do que na
bolsa. Mas basta para colocar a pergunta.

**Fontes:** quadro de vagas e resultados do ciclo 1, chamada 1 (Ministério da
Saúde, 2025); estratos pela REGIC 2018 e pelas RMs e RIDEs de 2022 (IBGE).

---

# 2. Pergunta

## 9 — Pergunta

`2. Pergunta`

> **Maiores bolsas do PMM-E para municípios mais vulneráveis compensam suas
> desvantagens territoriais na atração de médicos especialistas?**

Dois objetos, um contra o outro: o **preço** que a política colocou sobre a
vulnerabilidade — o degrau de **R$ 5 mil** entre faixas — e a **desvantagem**
que esse preço pretende compensar.

A margem que observamos é o **preenchimento da vaga**: se, ao final da chamada,
apareceu alguém disposto a ocupá-la.

---

# 3. Literatura teórica

## 10 — A decisão: onde vale a pena estar

`3. Literatura teórica · 1 de 2`

**Moehling, Niemesh, Thomasson & Treber (2020)**, eq. 1, p. 184, dão a
**estrutura da decisão**: o médico escolhe a localidade que maximiza o valor
presente do rendimento **real**, líquido do custo não pecuniário de viver ali.

$$\arg\max_{i \in I} \left\{ \sum_t \delta^t \left[ \frac{\mathbb{E}(w_{it}^{(s)})}{p_{it}} - c_{it}^{(s)} \right] \right\}$$

| Termo | Leitura |
|---|---|
| $\sum_t \delta^t$ | a escolha é de **carreira**, não de um mês: fixar-se ou migrar ao fim do vínculo |
| $\mathbb{E}(w^{(s)}_{it}) / p_{it}$ | rendimento **deflacionado** pelo custo de vida local |
| $c^{(s)}_{it}$ | tudo o que torna estar ali custoso e **não é pago em dinheiro** |
| $s$ | qualificação: generalista atende em posto simples; **especialista** precisa de centro cirúrgico e leito |

Na definição dos próprios autores, $c$ reúne *"preferences over rural or urban
living, or other location-specific attributes, such as proximity to family"* —
uma **caixa-preta**. As duas referências seguintes a abrem.

**Fontes:** Moehling et al. (2020), *Cliometrica* 14, p. 184, eq. 1;
[`docs/02_teoria/modelo_micro.md`](../../02_teoria/modelo_micro.md), §1.

---

## 11 — Abrindo o custo: o lugar e o trabalho

`3. Literatura teórica · 2 de 2`

**O lugar. Redding & Rossi-Hansberg (2017)**, eq. 24, p. 28, dão o **custo
geográfico**: a utilidade de trabalhar num lugar depende do salário, das
**amenidades** e do **custo de moradia** locais.

$$u_{nio} = \frac{z_{nio}\, B_n\, w_i}{\kappa_{ni}\, Q_n^{\,1-\beta}} \quad\Longrightarrow\quad c^{\text{espacial}}_m = (1-\beta)\ln Q_m - \ln A_m$$

Somado à proximidade da família de Moehling et al., o bloco fica
$c^{\text{geo}}_{im} = \phi(\text{dist}_{im}) - \gamma A_m + \theta_i^{\text{rural}}$:
afastar-se da família custa, e custa mais a cada quilômetro ($\phi' > 0$); a
amenidade urbana — saneamento, segurança, escola — compensa ($-\gamma A_m$); o
gosto por cidade pequena ou grande não tem sinal universal ($\theta_i^{\text{rural}} \gtrless 0$).

**O trabalho. Choné & Ma (2011)**, eq. 1, p. 232, dão o **custo laboral**: o
médico soma a renda, subtrai o custo de atender e soma o benefício ao paciente,
ponderado pelo **altruísmo**.

$$U = R - C(q; L, K) + \alpha B(q) \quad\Longrightarrow\quad c^{\text{laboral}}_{im} = C(q; L_m, K_m) - \alpha_i B(q; L_m, K_m)$$

Atender cansa, e cansa de forma **crescente** ($C' > 0$, $C'' > 0$); curar dá
satisfação, **decrescente** porque a triagem prioriza o caso grave ($B' > 0$,
$B'' < 0$). O custo marginal $c'(q) = C' - \alpha B'$ tem **sinal incerto**, mas
$c'' \gg 0$: a curva é um **U** — uma zona em que atender mais *reduz* o custo
líquido, um mínimo, e uma zona de exaustão.

**Equipe ($L$) e capital ($K$) atuam duas vezes.** Reduzem o cansaço,
$\partial C/\partial K < 0$ — canal que já está em Choné & Ma. E **ampliam o
benefício**, $\partial B/\partial K > 0$: sem medicamento, insumo cirúrgico ou
maquinário em funcionamento, o atendimento perde resolutividade. Esse segundo
canal é **extensão deste projeto**, motivada pela função de produção médica de
Reinhardt (1972, 1975). Por dois caminhos, $\partial c^{\text{laboral}}/\partial K < 0$.

**Uma limitação assumida.** CNES e edital não informam a residência do
profissional, por sigilo fiscal. A unidade de análise é o **município do
estabelecimento**, não o de moradia: $\text{dist}$ entra como latente.

**Fontes:** Redding & Rossi-Hansberg (2017), *Annual Review of Economics* 9,
p. 28, eq. 24; Choné & Ma (2011), *International Journal of Health Care Finance
and Economics* 11, p. 232, eq. 1; Reinhardt (1972, 1975);
[`docs/02_teoria/modelo_micro.md`](../../02_teoria/modelo_micro.md), §2.1 a §2.3 e §3.2.

---

# 4. Modelo microeconômico

## 12 — Como juntamos os três

`4. Modelo microeconômico · 1 de 2`

A estrutura vem de Moehling et al.; o custo, que neles era caixa-preta, é
aberto pelas outras duas. O médico $i$ escolhe o município $m$ que maximiza o
valor presente líquido da carreira:

$$V_{im} = \sum_t \delta^t \left[ \frac{\mathbb{E}(w_{imt} \mid B_m)}{p_{mt}} - c_{im} \right] + \varepsilon_{im}$$

$$c_{im} = \underbrace{\phi(\text{dist}_{im}) - \gamma A_m + \theta_i^{\text{rural}}}_{\text{Redding \& Rossi-Hansberg}} + \underbrace{C(q; L_m, K_m) - \alpha_i B(q; L_m, K_m)}_{\text{Choné \& Ma, com a extensão em } B}$$

| De onde vem | O que entrega |
|---|---|
| **Moehling et al. (2020)** | o $\arg\max$ intertemporal, o deflator $p_{mt}$ e a existência de $c$ |
| **Redding & Rossi-Hansberg (2017)** | distância, amenidades e custo de moradia dentro de $c$ |
| **Choné & Ma (2011)**, com Reinhardt | esforço, altruísmo e o papel de $L$ e $K$ dentro de $c$ |

**A decisão.** A alternativa $m = 0$ é **ficar fora do programa**. A vaga em $m$
é aceita quando $V_{im} \geq V_{i0}$ e $m$ é a melhor entre as disponíveis. O
termo $\varepsilon_{im}$ recolhe os gostos que não observamos.

**O que nenhuma das três tem.** Nenhuma trata de um componente da remuneração
**fixado por regra pública sobre um índice territorial**. É isso, e só isso, que
a adaptação ao PMM-E acrescenta — e é o que o slide seguinte desenvolve.

**Fontes:** [`docs/02_teoria/modelo_micro.md`](../../02_teoria/modelo_micro.md), §2.4 e §3.

---

## 13 — O IVS organiza o custo

`4. Modelo microeconômico · 2 de 2`

**O que a bolsa paga — e o que não paga.** A remuneração tem duas partes: a
**bolsa**, que a regra fixa, e o que o médico obtém no **mercado local** fora
das 20 horas do programa:

$$\mathbb{E}(w_{imt} \mid B_m) = B_m + w^{\text{priv}}_m$$

Na capital, $w^{\text{priv}}$ é alto: R$ 10 mil mais o consultório pode superar
R$ 20 mil sem complemento. No interior isolado, $w \to B$ — a bolsa é **toda** a
remuneração, e é ali que a política mais aposta nela. O deflator $p_{mt}$
trabalha no sentido oposto: o custo de vida **menor** valoriza a mesma bolsa em
termos reais.

**O que se observa.** Distância da família, aluguel, mercado privado e esforço
clínico **não são observados**. O que se observa, para todo município, é o
**IVS**. Escrevemos o custo como função do índice mais um desvio individual:

$$c_{im} = c_0(IVS_m) + \eta_i$$

Isso não é atalho: **cada dimensão do IVS corresponde a um bloco do custo.**

| Dimensão do IVS | Indicadores | Bloco do custo | Efeito sobre $c$ |
|---|---|---|:---:|
| Infraestrutura urbana | saneamento, lixo, tempo de deslocamento | amenidades $A_m$ — slide 11 | $\uparrow$ |
| Renda e trabalho | pobreza, desemprego, informalidade | mercado privado ausente, $w \to B$ — acima | $\uparrow$ |
| Capital humano | mortalidade infantil, analfabetismo, mães adolescentes | gravidade do caso, $B'(q)\uparrow$; escassez de $L$ e $K$ — slide 11 | **ambíguo** |

A terceira linha é o que impede assumir que o custo cresce com o índice.
Carência sanitária **eleva o benefício** de atender — o que **reduz** o custo
para um médico altruísta — e ao mesmo tempo **sinaliza falta de insumos**, o
que **eleva** o cansaço. Logo $c_0'(IVS) \gtrless 0$: o sinal é questão
empírica.

É por isso que o objeto do trabalho é o **degrau** da bolsa entre faixas, e não
a inclinação do índice.

**Fontes:** [`docs/02_teoria/modelo_micro.md`](../../02_teoria/modelo_micro.md), §3 e §3.1.

---

# 5. Hipótese

## 14 — A hipótese

`5. Hipótese`

**Passo 1 — a condição de aceitação.** O médico $i$ aceita a vaga em $m$ quando
o que ela vale supera sua melhor alternativa $\bar{v}_i$:

$$\frac{B_m + w^{\text{priv}}_m}{p_m} - c_0(IVS_m) \geq \bar{v}_i$$

**Passo 2 — do médico à vaga.** A vaga é preenchida se existir **ao menos um**
candidato para quem a desigualdade vale. Tudo o que aumenta o lado esquerdo
aumenta essa probabilidade.

**Passo 3 — a hipótese.** O trabalho testa uma só.

| | Hipótese | Derivada |
|:---:|---|---|
| **H1** | Maior **remuneração real** aumenta a probabilidade de preenchimento da vaga | $\dfrac{\partial \Pr(\text{preenchimento}_m)}{\partial (B_m / p_m)} > 0$ |

**Passo 4 — o custo é obstáculo, não hipótese.** O custo locacional não entra
como segunda hipótese porque não varia livremente: a regra do edital o amarra à
bolsa, e os dois sobem juntos. Ele é o que torna H1 difícil de testar, não uma
segunda afirmação a testar.

Na fronteira entre duas faixas, o preenchimento do lado mais vulnerável exige
que o degrau monetário supere o degrau de custo:

$$\frac{\Delta B_m}{p_m} > \Delta c_0, \qquad \Delta B_m = \text{R\$ } 5.000$$

A pergunta da apresentação é se essa desigualdade vale.

---

# 6. Viabilidade empírica

## 15 — Viabilidade empírica

`6. Viabilidade empírica`

**Temos como medir cada peça do modelo?**

| Peça do modelo | O que observamos | Fonte |
|---|---|---|
| Preenchimento da vaga | se teve alguém confirmado ou homologado | quadro de vagas e resultados do ciclo 1: 1.295 vagas, 368 municípios |
| Bolsa $B_m$ | o valor anunciado na vaga: R$ 10, 15 ou 20 mil | edital |
| Custo $c_m$ | o IVS e suas três dimensões; capital, metropolitano, polo do interior ou interior remoto; especialistas e estrutura preexistentes | Ipea; REGIC 2018 e RMs 2022 (IBGE); CNES mensal, jun/2024 a jul/2026 |
| Custo de vida $p_m$ | diferenças entre estados | IBGE |
| Mercado local $w^{\text{priv}}_m$ | — | **não observado** |
| Distância da família | — | **não observado** |

**Sim, para o essencial.** As duas peças não observadas — a renda no mercado
privado local e a distância da família — entram no modelo como parte do custo
que o IVS e a tipologia territorial resumem.

**A dificuldade, e o que já sabemos dela.** O que segue é sobre **o efeito do
valor da bolsa** — o objeto de H1 —, não sobre o trabalho inteiro. Recuperar a
regra que o Ministério aplicou era o primeiro passo do trabalho empírico. **Ele
foi dado**, e tem três resultados.

1. **Há suporte comum.** Existe sim município com bolsa alta e vulnerabilidade
   baixa: **37** municípios com IVS ≤ 0,400 estão na Faixa 1 e **94** na Faixa 2.
   Os intervalos de IVS das três faixas se sobrepõem. Não falta variação.
2. **Mas não há descontinuidade onde os cortes estão.** Em torno de `0,500`, os
   dois lados são **100% Faixa 1** em qualquer janela até ±0,050. Em torno de
   `0,400`, nenhum município de Faixa 3 aparece por perto — o maior IVS da Faixa
   3 é `0,372`. O tratamento é **localmente constante nos dois cortes**.
3. **E a variação que sobra não é exógena.** Dos 83 municípios fora da melhor
   regra de limiar possível, os 41 promovidos têm mediana de população de
   **7.933** contra **32.179** dos 42 rebaixados, e muito mais interior remoto.
   Como a remoticidade é o previsor mais forte do desfecho, parear por IVS
   confunde bolsa com posição territorial — contra a bolsa.

**Conclusão de viabilidade.** O efeito causal do *valor da bolsa* não é
identificável com as fontes públicas; a razão não é potência amostral.
Destravá-lo exige o **Anexo IV** e os critérios de localização da cláusula
11.1.3, que só o Ministério pode fornecer.

**O que fica de pé.** A pergunta do slide 9 continua sendo a pergunta do
trabalho. Até que a regra seja recuperada, a relação entre faixa e
preenchimento é reportada como **gradiente**, não como efeito. O trabalho tem um
desenho causal que não depende disso — a descontinuidade no **escore de seleção
do candidato** —, mas ele responde a outra pergunta: o efeito de **ganhar a
vaga**, não o do valor da bolsa.

---

## Ressalvas encerradas em 16/09/2026

1. **Cursos ambulatoriais.** A versão anterior do slide 4 anunciava **10** e
   enumerava oito, porque juntava num só item os três cursos de endoscopia
   digestiva alta, endoscopia digestiva avançada e colonoscopia. A contagem de
   10 foi conferida na Tabela 3 do edital e nos cursos 7 a 16 de
   `output/aquisicao/quadro_vagas_tratamento.parquet`. O slide passou a dar
   apenas a contagem.
2. **Figura do custo laboral.** `curva_custo_laboral_burnout.png` saiu do deck
   com a fusão dos dois slides de custo; o formato em U passou a ser descrito em
   texto no slide 11. A ilegibilidade da legenda em projeção deixa de afetar a
   apresentação. A figura permanece como ilustração canônica em
   `docs/02_teoria/figuras/`.
