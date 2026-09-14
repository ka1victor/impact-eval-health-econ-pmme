# Conteúdo da apresentação — banca 1

> **Fonte de verdade do que é apresentado.** Cada seção numerada é um slide do
> deck vigente; o cabeçalho é seu título literal e a linha em `código`, o
> rastreio de seção. O deck é **derivado**: divergência entre deck e este
> documento é erro do deck.<br>
> **Deck vigente:** o `.pptx` sobre o template do autor, montado por
> [`scripts/apresentacao/montar_deck_banca1_pptx.py`](../../../scripts/apresentacao/montar_deck_banca1_pptx.py)
> a partir de `deck_pptx/base_modelo_economico.pptx` e gravado em
> `output/apresentacao_banca1/deck_banca1_modelo_economico.pptx`. São **21
> slides**, na ordem da constante `ROTEIRO` do script.<br>
> **Decks divergentes:** [`deck_beamer/`](deck_beamer/) e
> [`deck_slidev/`](deck_slidev/) descrevem a **estrutura anterior, de 19
> slides**, e **não** correspondem ao que será apresentado. Ficam preservados
> como registro; não foram apagados nem editados.<br>
> **Escopo:** a banca 1 é teórica e termina na **viabilidade empírica**; não
> apresenta resultado de estimação. Toda leitura de figura de oferta é
> **descritiva**.<br>
> **Atualização:** 14 de setembro de 2026.

---

## 1 — Bolsa-formação como diferencial compensatório: um modelo de escolha racional para o preenchimento e a permanência de vagas no PMM-E

`capa · sem rastreio`

Capa do template, com o título do trabalho. O script não altera este slide.

---

## 2 — Sumário

`sumário · destaque em Motivação`

Slide de sumário do template, com seis entradas. O script corrige nele os erros
de digitação do original (`porposto` → `proposto`, `Téorica` → `Teórica`) e
completa `Modelo` para `Modelo Teórico`.

| Seção | Linha de apoio |
|---|---|
| **Motivação** | Por que a pergunta é importante |
| **Pergunta** | Pergunta proposta |
| **Literatura** | Literatura Teórica para a fundamentação |
| **Modelo Teórico** | Aplicação microeconômica e modelo proposto |
| **Hipóteses** | Hipóteses formuladas |
| **Viabilidade Empírica** | Viabilidade dos dados para a realização do teste empírico |

O mesmo slide reaparece antes de cada seção (slides 6, 8, 14, 18 e 20), com o
destaque deslocado.

---

# 1. Motivação

## 3 — A escassez de especialistas não é de número, é de lugar

`1. Motivação · O problema`

Slide do template preservado: o script troca apenas o título e acrescenta o
rodapé de fonte. Traz dois gráficos nativos do `.pptx`, com as manchetes do
próprio template:

| | |
|---|---|
| **I. Escassez de especialistas é concentrada territorialmente**<br>*Médicos especialistas por 100 mil habitantes, por UF — 2024* | **II. O acesso a serviços especializados exige longas distâncias**<br>*Deslocamento médio da população para serviços de alta complexidade (km)* |

Os dois gráficos são **objetos de gráfico do template**, com os dados embutidos
no arquivo `.pptx`; não são lidos de `output/`. Ver ressalva 1.

**Fontes (rodapé literal do slide):** Scheffer, M. (coord.). *Demografia
Médica no Brasil 2025* (FMUSP/AMB), dez/2024; IBGE, *Regiões de Influência das
Cidades — REGIC 2018*; Portaria GM/MS nº 7.061/2025, que reconheceu situação de
urgência em saúde pública na atenção especializada, por 24 meses.

---

## 4 — A bolsa do PMM-E é fixada por regra territorial

`1. Motivação · A política`

**Coluna da esquerda — o que o programa é.**

- **Bolsa-formação mensal** do Ministério da Saúde. Não é emprego nem concurso:
  não há vínculo.
- **Aprimoramento em serviço de 12 meses**, 20 horas semanais em
  estabelecimento do SUS, com supervisão de instituição formadora.
- **16 cursos de especialidade**, concentrados no câncer e no diagnóstico que o
  SUS mais espera.
- **O serviço não pode substituir** profissional já contratado: a vaga é
  acréscimo, não troca.

**Como a vaga chega ao médico.**

1. Estado ou município indica serviço e especialidade; a comissão bipartite
   prioriza.
2. O Ministério publica o quadro de vagas: município, estabelecimento, curso e
   faixa de bolsa.
3. O médico escolhe até dois locais, em ordem de preferência, e é classificado
   por titulação e tempo de formação.

**Coluna da direita — o que determina o valor da bolsa.**

- **A faixa vem do IVS do município** — índice do Ipea que resume, de 0 a 1,
  infraestrutura urbana, capital humano, e renda e trabalho.
- O edital de 2025 agrupa as cinco categorias do índice em três faixas de
  valor.

Gráfico do template (objeto nativo do `.pptx`, reposicionado pelo script):
*valor mensal da bolsa-formação por faixa de atração/vulnerabilidade* —
Faixa 3 R$ 10.000, Faixa 2 R$ 15.000, Faixa 1 R$ 20.000. Ver ressalva 1.

Abaixo do gráfico: **no ciclo 1, 102 municípios na Faixa 1, 107 na Faixa 2 e
159 na Faixa 3.**

**Fecho do slide.** *O valor não depende da especialidade, da carga horária nem
do que o médico produz. Depende de onde fica o município — e é essa regra, e só
ela, que o trabalho estuda.*

**Fontes (rodapé literal do slide):** Lei nº 15.233/2025, art. 22-D; Portaria
GM/MS nº 7.177/2025; Edital SGTES/MS nº 3/2025 (DOU 24/07/2025), itens 1, 3–5,
10 e 11; quadro de vagas do ciclo 1, chamada 1 — 1.295 vagas
estabelecimento–curso em 460 estabelecimentos e 368 municípios.

---

## 5 — A presença de especialistas cresceu nas três faixas

`1. Motivação · O efeito`

Figura: [`output/apresentacao_banca1/oferta_antes_depois_por_faixa.png`](../../../output/apresentacao_banca1/oferta_antes_depois_por_faixa.png)
— especialistas por 100 mil habitantes, série mensal por faixa de bolsa.

**O que o gráfico mostra.**

- As três faixas sobem a partir da publicação da oferta. A Faixa 1, de R$ 20
  mil, vai de **17,4** a **22,0** especialistas por 100 mil habitantes.
- A distância entre a Faixa 1 e as outras duas aumenta depois da homologação.

**O que isso pode significar.**

- Que a bolsa maior atraiu profissionais para onde ela é maior.
- Ou que as três faixas seguem uma tendência comum — do programa, do mercado ou
  do próprio cadastro — e o degrau apenas a acompanha.
- Não há município fora do programa para comparar: todos os 368 receberam vaga.

**O que queremos entender.** Quanto desse crescimento é o **preço** que a
política pôs sobre a vulnerabilidade — e quanto é o **lugar** que esse preço
deveria compensar.

**Fontes (rodapé literal do slide):** *Leitura descritiva: sem município fora
do programa, a figura não identifica efeito.* Especialistas nos CBOs dos cursos
com correspondência unívoca curso–CBO, CNES mensal jun/2024 a jul/2026;
população do Censo 2022 (IBGE); faixa pela bolsa publicada na vaga.

---

# 2. Pergunta

## 6 — Sumário

`sumário · destaque em Pergunta`

Repetição do slide 2, com o destaque na seção **Pergunta**.

---

## 7 — II. Pergunta

`2. Pergunta`

Slide do template, não alterado pelo script. O enunciado, literal:

> **Um aumento na remuneração do PMM-E consegue atrair especialistas para
> municípios mais vulneráveis?**

**Fontes (rodapé literal do slide):** Scheffer, M. (coord.). *Demografia Médica
no Brasil 2025*; IBGE, *Regiões de Influência das Cidades — REGIC 2018*;
Ministério da Saúde, PMM-E, edital e painéis/resultados administrativos do
programa.

---

# 3. Literatura teórica

## 8 — Sumário

`sumário · destaque em Literatura`

Repetição do slide 2, com o destaque na seção **Literatura**.

---

## 9 — O modelo combina três elementos da teoria

`3. Literatura teórica · abertura`

Slide do template, não alterado pelo script. Manchete: *Três primitivas
teóricas sustentam a equação de escolha locacional do médico.* As três colunas
trazem, para cada trabalho, o que ele é e o que entrega ao modelo.

| Trabalho | Primitiva que fornece | Entra no modelo como |
|---|---|---|
| **Moehling, Niemesh, Thomasson & Treber (2020)** | escolha locacional intertemporal: o médico maximiza o valor presente do rendimento real menos um custo locacional não pecuniário | equação de escolha e o horizonte $\sum_t \delta^t$ |
| **Redding & Rossi-Hansberg (2017)** | equilíbrio espacial: amenidades e custo de moradia determinam a atratividade de um lugar | custo geográfico e o deflator $p_m$ |
| **Choné & Ma (2011); Reinhardt (1975)** | utilidade do médico com altruísmo: atender gera cansaço $C(q)$ e satisfação $\alpha B(q)$, ambos mediados por equipe e capital instalado | custo laboral líquido e o papel de $L$ e $K$ |

---

## 10 — A escolha locacional maximiza a renda real líquida

`3. Literatura teórica · 1 de 4`

Rubrica do slide: **MOEHLING, NIEMESH, THOMASSON & TREBER (2020), EQ. 1,
P. 184**. Slide do template, não alterado pelo script.

$$\max_{i \in I} \sum_t \delta^t \left[ \frac{\mathbb{E}\left(w_{it}^{(s)}\right)}{p_{it}} - c_{it}^{(s)} \right]$$

**O que cada termo significa.**

- $i \in I$: localidades candidatas.
- $\mathbb{E}\left(w_{it}^{(s)}\right)$: salário esperado em $i$, no ano $t$, na
  especialidade $s$.
- $p_{it}$: nível de preços da localidade (deflator).
- $c_{it}^{(s)}$: custo não pecuniário de viver ali.
- $\delta^t$: desconto do ano $t$ ($0 < \delta < 1$).
- $\sum_t$: soma ao longo do horizonte de carreira.

**O que a conta faz.**

1. Divide o salário esperado pelos preços locais: o que entra na decisão é o
   salário real, não o nominal.
2. Subtrai o custo não pecuniário de viver na localidade: sobra o ganho líquido
   daquele ano.
3. Desconta cada ano por $\delta$ e soma a carreira inteira: o resultado é um
   valor presente por localidade.
4. Compara as localidades e devolve a que tem o maior valor (*arg max*).

**Onde chegamos:** a localidade escolhida é a de maior renda real líquida
descontada — salário nominal alto não compensa preços e custos locais altos.

---

## 11 — Amenidades e moradia definem quanto vale o salário

`3. Literatura teórica · 2 de 4`

Rubrica do slide: **REDDING & ROSSI-HANSBERG (2017), EQ. 24, P. 28**. Slide do
template, não alterado pelo script.

$$u_{nio} = \frac{z_{nio}\, B_n\, w_i}{\kappa_{ni}\, Q_n^{\,1-\beta}}$$

**O que cada termo significa.**

- $u_{nio}$: utilidade de morar em $n$ e trabalhar em $i$.
- $z_{nio}$: gosto idiossincrático pelo par $(n, i)$.
- $B_n$: amenidades da localidade $n$.
- $w_i$: salário pago no local de trabalho $i$.
- $\kappa_{ni}$: custo de deslocamento entre $n$ e $i$.
- $Q_n$: preço da moradia em $n$.
- $1-\beta$: parcela da renda gasta com moradia.

**O que a conta faz.**

1. No numerador, o que atrai: o salário do local de trabalho, multiplicado pelas
   amenidades e pelo gosto pessoal.
2. No denominador, o que repele: o custo de deslocamento e o preço da moradia
   elevado à fração da renda gasta com moradia.
3. A divisão transforma salário nominal em bem-estar: o mesmo salário vale menos
   onde morar é caro ou a viagem é longa.
4. Cada médico escolhe o par morar–trabalhar com a maior utilidade.

**Onde chegamos:** um local só atrai se o salário compensar moradia e
deslocamento — é daqui que sai o deflator espacial usado na equação de escolha.

---

## 12 — Atender rende, cansa e gera benefício ao paciente

`3. Literatura teórica · 3 de 4`

Rubrica do slide: **CHONÉ & MA (2011), EQ. 1, P. 232**. Slide do template, não
alterado pelo script.

$$U = R - C(q; L, K) + \alpha B(q)$$

**O que cada termo significa.**

- $U$: utilidade do médico ao atender.
- $R$: receita recebida pelo atendimento.
- $q$: quantidade ou intensidade de cuidado prestado.
- $C(q; L, K)$: custo de esforço para produzir $q$.
- $L$: equipe disponível (trabalho de apoio).
- $K$: capital instalado — leitos, equipamentos, estrutura.
- $\alpha$: peso do altruísmo do médico.
- $B(q)$: benefício gerado ao paciente.

**O que a conta faz.**

1. Soma a renda do atendimento: é o ganho monetário direto.
2. Subtrai o custo de atender, que depende de equipe e capital: com mais $L$ e
   $K$, o mesmo $q$ cansa menos.
3. Soma o benefício ao paciente ponderado pelo altruísmo: o médico valoriza
   curar, não só receber.
4. O resultado é a utilidade de trabalhar naquele lugar, dada sua estrutura
   assistencial.

**Onde chegamos:** estrutura e equipe entram na decisão como custo de trabalhar;
é por isso que salário igual em locais com estruturas diferentes não é oferta
igual.

---

## 13 — Equipe e capital entram duas vezes no custo de atender

`3. Literatura teórica · 4 de 4`

Slide novo, montado pelo script sobre uma cópia do gabarito de equação.
Rubrica: **CHONÉ & MA (2011), §2.3; REINHARDT (1972, 1975)**.

$$\frac{\partial C}{\partial K} < 0 \qquad\text{e}\qquad \frac{\partial B}{\partial K} > 0 \qquad\Longrightarrow\qquad \frac{\partial c^{\mathrm{laboral}}}{\partial K} < 0$$

**A curva em U do custo líquido.**

Figura: [`output/apresentacao_banca1/custo_laboral_deck.png`](../../../output/apresentacao_banca1/custo_laboral_deck.png),
gerada por
[`scripts/apresentacao/gerar_figura_custo_laboral_deck.py`](../../../scripts/apresentacao/gerar_figura_custo_laboral_deck.py)
em versão de projeção. **Ilustração conceitual:** não há escala cardinal nem
dado observado.

Legenda literal sob a figura: *O custo marginal c′(q) = C′ − αB′ tem sinal
incerto; c″ ≫ 0 não tem. Daí o U.*

**Os dois canais de equipe e capital.**

| | |
|---|---|
| **Canal 1 · já está em Choné & Ma** | Com equipe de apoio e capital instalado, o mesmo volume de atendimentos **cansa menos**: leitos, equipamento e pessoal reduzem o esforço de produzir $q$. |
| **Canal 2 · extensão deste projeto** | Sem medicamento, insumo cirúrgico ou maquinário em funcionamento, o atendimento **perde resolutividade** — e com ela cai o benefício ao paciente, que é o que move o médico altruísta. O canal vem da função de produção médica de Reinhardt. |

**Onde chegamos:** por dois caminhos, falta de estrutura eleva o custo de
atender. Salário igual em municípios com estruturas diferentes não é oferta
igual.

---

# 4. Modelo microeconômico

## 14 — Sumário

`sumário · destaque em Modelo Teórico`

Repetição do slide 2, com o destaque na seção **Modelo Teórico**.

---

## 15 — Como juntamos os três

`4. Modelo microeconômico · 1 de 3`

A equação de escolha do template, preservada, com as legendas reescritas pelo
script:

$$V_{im} = \sum_t \delta^t \left[ \frac{\mathbb{E}(w_{imt} \mid B_m)}{p_{mt}} - c_{im} \right] + \varepsilon_{im}, \qquad m_i^{*} \in \arg\max_{m \in M \cup \{0\}} V_{im}$$

Legendas que apontam para os termos: *a escolha é de carreira* (sobre
$\sum_t \delta^t$); *a bolsa, deflacionada* (sobre
$\mathbb{E}(w_{imt} \mid B_m)/p_{mt}$); *o custo de estar ali* (sobre $c_{im}$);
*m = 0 é ficar fora do programa* (sobre o conjunto de escolha).

O custo, que em Moehling et al. era caixa-preta, é aberto pelas outras duas
tradições:

$$c_{im} = \underbrace{\phi(\text{dist}_{im}) - \gamma A_m + \theta_i^{\text{rural}}}_{\text{Redding \& Rossi-Hansberg}} + \underbrace{C(q; L_m, K_m) - \alpha_i B(q; L_m, K_m)}_{\text{Choné \& Ma, com a extensão em } B}$$

Três blocos em linha dizem de onde vem cada peça:

| Trabalho | O que entrega |
|---|---|
| **Moehling et al. (2020)** | o *arg max* intertemporal, o deflator $p$ e a existência de um custo $c$ |
| **Redding & Rossi-Hansberg (2017)** | distância, amenidades e custo de moradia, dentro de $c$ |
| **Choné & Ma (2011), com Reinhardt** | esforço, altruísmo e o papel de equipe e capital, dentro de $c$ |

**Fecho do slide, em dois parágrafos.**

- **A decisão.** A alternativa $m = 0$ é ficar fora do programa. A vaga em $m$ é
  aceita quando $V(i,m) \geq V(i,0)$ e $m$ é a melhor entre as disponíveis;
  $\varepsilon(i,m)$ recolhe os gostos que não observamos.
- **O que nenhuma das três tem.** Nenhuma trata de um componente da remuneração
  fixado por **regra pública sobre um índice territorial**. É isso, e só isso,
  que a adaptação ao PMM-E acrescenta.

**Fonte (rodapé literal do slide):** `docs/02_teoria/modelo_micro.md`, §2.4 e §3.

---

## 16 — A remuneração do município vai além da bolsa

`4. Modelo microeconômico · 2 de 3`

$$\mathbb{E}\left(w_{imt} \mid B_m\right) = \underbrace{B_m}_{\text{fixada por regra pública}} + \underbrace{w^{\mathrm{priv}}_m}_{\text{mercado local}}$$

**O mesmo valor, dois lugares.**

| | |
|---|---|
| **Capital ou região metropolitana** | Consultório, planos de saúde e hospitais privados sustentam a especialidade fora das 20 horas do programa: $w = B + w^{\text{priv}}$, com a segunda parcela alta. |
| **Interior isolado** | Não há demanda privada que sustente a especialidade: $w \to B$. A bolsa é toda a remuneração — e é exatamente ali que a política mais aposta nela. |

**Desdobramentos.**

| | |
|---|---|
| **Bolsa maior pode ser renda menor** | R$ 20 mil sem complemento contra R$ 10 mil mais o consultório da capital |
| **A regra não observa o mercado local** | a bolsa responde ao IVS, e o IVS não mede demanda privada |
| **O deflator atua no sentido oposto** | custo de vida menor no interior valoriza a mesma bolsa em termos reais |

**Onde chegamos.** A bolsa é a única parcela da remuneração que a regra controla
— e, onde o mercado privado não sustenta a especialidade, é também a única que
existe. É ali que a política aposta, e é ali que o custo de estar é maior.

---

## 17 — O IVS organiza o custo, com um sinal e uma dúvida

`4. Modelo microeconômico · 3 de 3`

$$c_{im} = c_0(IVS_m) + \eta_i$$

*Distância da família, aluguel e esforço clínico não são observados. O IVS é. E
cada dimensão do índice corresponde a um bloco do custo.*

**Custo geográfico · sinal conhecido**

- **Infraestrutura urbana** — saneamento, coleta de lixo, tempo de deslocamento;
  é a amenidade $A_m$ de Redding & Rossi-Hansberg. Índice maior, amenidade pior.
- **Renda e trabalho** — pobreza, desemprego, informalidade; sem renda local não
  há mercado privado que sustente a especialidade, e $w$ tende a $B$.

> Nas duas dimensões o sentido é o mesmo: IVS maior, custo maior.

**Custo laboral · sinal ambíguo**

- **Capital humano** — mortalidade infantil, analfabetismo, mães adolescentes.
  Carência sanitária eleva a gravidade do caso — e com ela o benefício de
  atender, $B'(q) \uparrow$, o que reduz o custo para um médico altruísta.
- **A mesma dimensão, em sentido contrário** — carência também sinaliza escassez
  de equipe $L$ e de capital $K$, o que eleva o cansaço $C(q)$.

> Os dois efeitos se opõem: o sinal de $\partial c^{\text{laboral}}/\partial IVS$
> é questão empírica.

**O que não é ambíguo.** O sinal de
$\partial c^{\text{laboral}}/\partial K$: mais equipe e mais capital reduzem o
custo de atender pelos dois canais do slide 13. O que não sabemos é quanto do
IVS é falta de $K$.

É por isso que o objeto do trabalho é o **degrau da bolsa entre faixas**, e não
a inclinação do índice.

---

# 5. Hipótese

## 18 — Sumário

`sumário · destaque em Hipóteses`

Repetição do slide 2, com o destaque na seção **Hipóteses**.

---

## 19 — Da condição de aceitação sai uma hipótese

`5. Hipótese`

**A derivação.**

*Passo 1 · a condição de aceitação.* O médico $i$ aceita a vaga em $m$ quando o
que ela vale supera sua melhor alternativa $\bar{v}_i$:

$$\frac{B_m + w^{\mathrm{priv}}_m}{p_m} - c_0(IVS_m) \;\geq\; \bar{v}_i$$

*Passo 2 · do médico à vaga.* A vaga é preenchida se existir ao menos um
candidato para quem a desigualdade vale. Tudo o que aumenta o lado esquerdo
aumenta essa probabilidade.

*Passo 3 · a derivada que o trabalho testa.*

$$\frac{\partial \Pr(\text{preenchimento}_m)}{\partial \left(B_m / p_m\right)} \;>\; 0$$

**O custo é obstáculo, não hipótese.** Ele não entra como segunda hipótese
porque não varia livremente: a regra do edital o amarra à bolsa, e os dois sobem
juntos. É o que torna a hipótese difícil de testar, não uma segunda afirmação a
testar.

**Hipótese econômica.**

> *Ceteris paribus*, municípios com maior remuneração do PMM-E conseguem atrair
> mais especialistas.

**O que isso exige na fronteira entre duas faixas.** Do lado mais vulnerável, o
preenchimento exige que o degrau monetário supere o degrau de custo:

$$\frac{\Delta B_m}{p_m} > \Delta c_0, \qquad \Delta B_m = \text{R\$}\,5.000$$

A pergunta da apresentação é se essa desigualdade vale — e o que vem a seguir é
se conseguimos respondê-la com o que existe publicado.

---

# 6. Viabilidade empírica

## 20 — Sumário

`sumário · destaque em Viabilidade Empírica`

Repetição do slide 2, com o destaque na seção **Viabilidade Empírica**.

---

## 21 — Temos as peças; falta a variação exógena

`6. Viabilidade empírica`

**O que conseguimos medir.**

| | Peça | Fonte, como o slide a enuncia |
|:---:|---|---|
| ● | **Preenchimento da vaga** | quadro de vagas e resultados do ciclo 1: 1.295 vagas em 368 municípios |
| ● | **Bolsa $B_m$** | o valor anunciado na vaga: R$ 10, 15 ou 20 mil — edital |
| ● | **Custo $c_m$** | IVS e suas três dimensões (Ipea); capital, metropolitano, interior conectado ou remoto (REGIC 2018 e RMs 2022); especialistas e estrutura preexistentes (CNES mensal, jun/2024 a jul/2026) |
| ◐ | **Custo de vida $p_m$** | diferenças entre estados — IBGE |
| ○ | **Mercado privado $w^{\text{priv}}$** | não observado |
| ○ | **Distância da família** | não observado |

*As duas peças não observadas entram no modelo como parte do custo que o IVS e a
tipologia territorial resumem. Para o essencial, os dados existem.*

**Onde procurar variação exógena.** O edital corta o IVS em categorias, e a
categoria fixa a bolsa (cláusula 11.1.4). Os cortes de **0,400** e **0,500** são
o lugar natural de uma regressão descontínua: comparar municípios logo acima e
logo abaixo.

1. **Há suporte comum.** 37 municípios com IVS ≤ 0,400 estão na Faixa 1 e 94 na
   Faixa 2; os intervalos das três faixas se sobrepõem. Não falta variação.
2. **Mas não há descontinuidade onde os cortes estão.** Em torno de 0,500 os
   dois lados são 100% Faixa 1 em qualquer janela até ±0,050; em torno de 0,400
   o maior IVS da Faixa 3 é 0,372. O tratamento é localmente constante nos dois
   cortes.
3. **E a variação que sobra não é exógena.** Dos 83 municípios fora da melhor
   regra de limiar possível, os 41 promovidos têm mediana de população de 7.933
   contra 32.179 dos 42 rebaixados. Parear por IVS confunde bolsa com posição
   territorial.

**O que destrava.** A cláusula 11.1.3 manda seguir critérios de localização
definidos no Anexo IV, que o edital não reproduz. O dado tem a forma das duas
cláusulas: em 177 dos 368 municípios a faixa publicada está acima da categoria
de IVS, e em nenhum abaixo. **O IVS é o piso da bolsa, não o seu critério.**

**Fontes (rodapé literal do slide):** *Diagnóstico de reconstrução da regra, sem
abertura de desfecho:* `output/rdd_bolsa/a01b_reconstrucao_regra_faixa.json`.
Edital SGTES/MS nº 3/2025, itens 11.1.3 e 11.1.4; Ipea, *Atlas da
Vulnerabilidade Social* (2015).

---

## Ressalvas abertas

1. **Gráficos do template, resolvidos.** Os três gráficos que o template trazia
   como objetos nativos, com dados embutidos no `.pptx`, saíram do deck. O de
   *especialistas por 100 mil habitantes por UF* tinha catorze das dezesseis
   barras interpoladas em números redondos, e duas delas contradiziam a fonte
   registrada em
   [`03_proveniencia_figuras_e_numeros.md`](03_proveniencia_figuras_e_numeros.md):
   São Paulo aparecia em 414 e Pará em 145, contra **244** e **70** conferidos.
   No lugar dele entrou `output/apresentacao_banca1/especialistas_extremos_uf.png`,
   que mostra **apenas as quatro unidades da federação que a fonte reporta**. O
   gráfico de deslocamento passou a ler
   `docs/07_apresentacoes/banca1/figuras/deslocamento_por_regiao.png`, e o da
   bolsa, `output/apresentacao_banca1/bolsa_por_faixa.png`. Nenhum gráfico do
   deck vigente tem dado embutido no `.pptx`.<br>
   **O que continua em aberto:** a tabela integral da *Demografia Médica no
   Brasil 2025* nunca foi baixada por este projeto — só a cobertura que reporta
   os extremos. Um gráfico com as 27 unidades da federação depende de obter a
   fonte primária. E o painel de deslocamento havia sido retirado, em revisão
   anterior, por medir o custo do paciente e não o do médico; ele volta ao deck
   por decisão de desenho do autor, e a pertinência é decisão dele.
2. **Contagem de cursos.** O slide 4 afirma **16 cursos de especialidade** e não
   os enumera — a enumeração da versão anterior do deck saiu. A contagem vem da
   Tabela 3 do Edital SGTES/MS nº 3/2025, registrada como *16 cursos, 6
   cirúrgicos e 10 ambulatoriais*; mas o roteiro narrativo enumera apenas **oito**
   cursos ambulatoriais. A contagem do edital continua não reconferida, e o "16"
   do slide herda essa pendência.
3. **Conferência contra o artefato.** O deck vigente está gravado em
   `output/apresentacao_banca1/deck_banca1_modelo_economico.pptx`, com 21 slides,
   e o manifesto `output/apresentacao_banca1/manifesto_deck_banca1.json` registra
   os hashes da base, da saída, das figuras de `output/` e das sete equações
   renderizadas, além do hash da figura de deslocamento lida de `docs/`.
   Este documento foi conferido contra esse `.pptx`. A cada nova montagem, a
   conferência deve ser refeita: o script é a origem, o `.pptx` é o artefato, e
   este documento é a fonte de verdade do conteúdo.
