---
theme: slidev-theme-academic
title: Remuneração como incentivo limitado
info: |
  Banca 1 — conteúdo canônico em docs/07_apresentacoes/banca1/02_conteudo_slides.md.
  Este deck é artefato derivado: divergência entre deck e documento de conteúdo é erro do deck.
  Estrutura de 17 slides em 3 seções, mais Q&A e apêndice fora da contagem.
  Um build (`###` no documento) é um slide próprio aqui, com o mesmo título e
  o contador "n de N" no rastreio — a convenção deste deck desde a origem.
colorSchema: light
transition: none
drawings:
  persist: false
lineNumbers: false
themeConfig:
  paginationX: ''
  paginationY: ''
fonts:
  provider: none
  sans: Inter
  serif: Playfair Display
  mono: ui-monospace
defaults:
  class: centrado
layout: cover
coverDate: ''
class: centrado
---


<div class="capa-grade">
  <div class="capa-texto">
    <p class="capa-rotulo">Projeto Mais Médicos Especialistas &middot; Banca 1</p>
    <div class="capa-rule"></div>
    <h1 class="capa-titulo">Remuneração como incentivo limitado</h1>
    <p class="capa-sub">Um modelo de escolha racional para o Programa Mais Médicos Especialistas</p>
    <p class="capa-meta"><strong>Grupo 2</strong> &middot; Bernardo Gomes &middot; Bruno Manta &middot; Felipe Barros &middot; Felipe Marques &middot; Gabriel Benegra &middot; Kauã Santos &middot; Vinicius Sbruzzi</p>
    <p class="capa-inst">Insper &middot; 2026</p>
  </div>
  <div class="capa-grafico">
    <img :src="'/insper/insper-bg.png'" alt="" />
  </div>
</div>

---

# Sumário

<div class="sumario">
  <div class="sumario-item"><span class="sumario-n">1</span><span class="sumario-t">Motivação e Pergunta<span class="sumario-d">O problema, a política, o índice, os efeitos e a pergunta</span></span></div>
  <div class="sumario-item"><span class="sumario-n">2</span><span class="sumario-t">Literatura Teórica e Modelo Microeconômico<span class="sumario-d">De onde vem a equação de escolha, e o que há dentro do custo</span></span></div>
  <div class="sumario-item"><span class="sumario-n">3</span><span class="sumario-t">Hipótese e Viabilidade Empírica<span class="sumario-d">O que o modelo implica, o que se testa e o que os dados permitem</span></span></div>
</div>

---
layout: default
class: divisoria
---

<div class="div-rule"></div>
<div class="div-num">1</div>
<h1 class="div-titulo">Motivação e Pergunta</h1>
<p class="div-sub">O problema, a política, o índice, os efeitos e a pergunta</p>

---

<Rastreio cont="1 de 3">1. Motivação e Pergunta · Problema</Rastreio>

# O especialista está longe do interior — e quase nunca é só do SUS

<div class="build-lbl">Onde eles estão</div>

<div class="cols cols-2 gap-s mt-s">
  <div>
    <p class="xs mut tight">Especialistas por 100 mil habitantes, dez/2024</p>
    <Fig src="/fig/especialistas_por_uf_extremos.png" h="13.5rem" alt="Especialistas por 100 mil habitantes, dez/2024 — 453 no DF e 244 em SP, contra 70 no PA e 68 no MA" />
  </div>
  <div>
    <p class="xs mut tight">Distância média para serviços de alta complexidade, em km</p>
    <Fig src="/fig/deslocamento_por_regiao.png" h="13.5rem" alt="Distância média para serviços de alta complexidade — 276 km no Norte, 101 km no Sul" />
  </div>
</div>

<div class="callout mt-s">

A escassez é territorial — e onde há menos especialista o paciente anda mais.

</div>

<Fonte>Scheffer et al., <em>Demografia Médica no Brasil 2025</em> (FMUSP/AMB), cap. 11 e cap. 13, Fig. 1, p. 254; deslocamento: origem provável na REGIC 2018 (IBGE), <strong>a confirmar</strong>; Portaria GM/MS nº 7.061/2025; Edital SGTES/MS nº 3/2025, Tabela 3; <code>output/aquisicao/quadro_vagas_tratamento.parquet</code>; figuras por <code>scripts/apresentacao/gerar_figuras_banca1.py</code>.</Fonte>

---

<Rastreio cont="2 de 3">1. Motivação e Pergunta · Problema</Rastreio>

# O especialista está longe do interior — e quase nunca é só do SUS

<div class="build-lbl">De quem é o tempo desse especialista</div>

<p class="xs mut tight mt-s">Setor de atuação dos cirurgiões</p>

<Fig src="/fig/dupla_pratica_cirurgioes.png" h="10rem" alt="Setor de atuação dos cirurgiões — 72,4% em dupla prática, 19,9% exclusivamente no privado, 7,7% exclusivamente no público ou SUS" />

<p class="sm mt-m"><strong>O SUS não compra a carreira do especialista. Compra uma fração dela</strong> — e disputa o resto com o mercado privado. A bolsa do PMM-E compra <strong>20 horas</strong> dessa fração.</p>

<Fonte>Scheffer et al., <em>Demografia Médica no Brasil 2025</em> (FMUSP/AMB), cap. 11 e cap. 13, Fig. 1, p. 254; deslocamento: origem provável na REGIC 2018 (IBGE), <strong>a confirmar</strong>; Portaria GM/MS nº 7.061/2025; Edital SGTES/MS nº 3/2025, Tabela 3; <code>output/aquisicao/quadro_vagas_tratamento.parquet</code>; figuras por <code>scripts/apresentacao/gerar_figuras_banca1.py</code>.</Fonte>

---

<Rastreio cont="3 de 3">1. Motivação e Pergunta · Problema</Rastreio>

# O especialista está longe do interior — e quase nunca é só do SUS

<div class="build-lbl">E quais especialistas faltam</div>

<div class="stack mt-m bloco-lg">

<div class="card">

Maiores ofertas do ciclo 1: **endoscopia digestiva alta**, **colonoscopia** e **anestesiologia**.

</div>

<div class="card">

Em 2025 o Ministério declarou **urgência em saúde pública por 24 meses** pelo tempo de espera, e lançou o **Agora Tem Especialistas**, de que o PMM-E é o braço de provimento.

</div>

</div>

<Fonte>Scheffer et al., <em>Demografia Médica no Brasil 2025</em> (FMUSP/AMB), cap. 11 e cap. 13, Fig. 1, p. 254; Portaria GM/MS nº 7.061/2025; Edital SGTES/MS nº 3/2025, Tabela 3; <code>output/aquisicao/quadro_vagas_tratamento.parquet</code>; figuras por <code>scripts/apresentacao/gerar_figuras_banca1.py</code>.</Fonte>

---

<Rastreio cont="1 de 3">1. Motivação e Pergunta · Política</Rastreio>

# A bolsa é do município, não do médico nem da especialidade

<div class="build-lbl">O que o programa oferece</div>

<div class="cols cols-38 gap-s mt-s">
  <div>
    <p class="xs mut tight">Valor mensal da bolsa-formação por faixa de atração</p>
    <Fig src="/fig/bolsa_por_faixa.png" h="11rem" alt="Valor mensal da bolsa-formação por faixa de atração" />
  </div>
  <div>

<p class="sm tight"><strong>Lei nº 15.233/2025</strong>, para reduzir o <strong>tempo de espera</strong> do SUS. Bolsa-formação <strong>sem vínculo</strong>, até <strong>12 meses</strong>, <strong>20 h semanais</strong>, <strong>RQE</strong> exigido, com supervisão de instituição formadora — <strong>igual em toda vaga</strong>. O <strong>valor</strong> é a única coisa que varia. Ciclo 1, jul/2025: <strong>1.295 células</strong> estabelecimento–curso em <strong>368 municípios</strong>, <strong>678</strong> com vaga imediata.</p>

  </div>
</div>

<div class="callout mt-s">

O programa não forma especialista: exige RQE e compra 20 horas de quem já é.

</div>

<Fonte>Lei nº 15.233/2025, art. 21; Edital SGTES/MS nº 3/2025, itens 1.1, 1.2.1, 1.2.5, 11.1 a 11.4; Ipea, <em>Atlas da Vulnerabilidade Social</em> (2015); CNES 06/2025 e Censo 2022 (IBGE); <code>output/aquisicao/quadro_vagas_tratamento.parquet</code>.</Fonte>

---

<Rastreio cont="2 de 3">1. Motivação e Pergunta · Política</Rastreio>

# A bolsa é do município, não do médico nem da especialidade

<div class="build-lbl">Quem fixa o valor</div>

<p class="sm mt-s"><strong>Não fixam:</strong> especialidade, curso, estabelecimento, carga, produção, desempenho — nem o médico. <strong>Fixa:</strong> o <strong>município</strong>, e só ele.</p>

<div class="tbl-center mt-s">

| Cláusula | O que fixa o valor | Situação |
|---|---|---|
| **11.1.4** | categoria de **IVS 2010** do Ipea: muito alta → **R$ 20 mil**, alta → **R$ 15 mil**, demais → **R$ 10 mil** | pública |
| **11.1.3** | *"critérios de **localização e vulnerabilidade** definidos de acordo com a faixa de atração definida no **Anexo IV**"* | **não público** |

</div>

<p class="sm mt-s">Em <strong>177 dos 368</strong> municípios a faixa publicada está <strong>acima</strong> da categoria de IVS; <strong>zero</strong> abaixo.</p>

<div class="callout mt-s">

O IVS é o piso da bolsa, não o critério dela.

</div>

<Fonte>Lei nº 15.233/2025, art. 21; Edital SGTES/MS nº 3/2025, itens 1.1, 1.2.1, 1.2.5, 11.1 a 11.4; Ipea, <em>Atlas da Vulnerabilidade Social</em> (2015); <code>output/aquisicao/quadro_vagas_tratamento.parquet</code>.</Fonte>

---

<Rastreio cont="3 de 3">1. Motivação e Pergunta · Política</Rastreio>

# A bolsa é do município, não do médico nem da especialidade

<div class="build-lbl">Para onde a regra manda o dinheiro</div>

<div class="cols cols-2 gap-s mt-s">
  <div>
    <p class="xs mut tight">Especialistas por 100 mil habitantes, jun/2025</p>
    <Fig src="/fig/oferta_pre_por_faixa.png" h="11rem" alt="Especialistas por 100 mil habitantes, jun/2025 — 15,0 na Faixa 3, 14,4 na Faixa 2, 18,3 na Faixa 1" />
  </div>
  <div>
    <p class="xs mut tight">Colegas da mesma especialidade no município, jun/2025</p>
    <Fig src="/fig/retaguarda_por_faixa.png" h="11rem" alt="Colegas da mesma especialidade no município, jun/2025 — mediana de 6,5, 5,0 e 2,5 da Faixa 3 à Faixa 1" />
  </div>
</div>

<p class="sm mt-s"><strong>Por habitante</strong>, a bolsa maior não vai para onde falta mais. <strong>Em colegas</strong>, vai: a mediana cai de <strong>6,5</strong> para <strong>2,5</strong>.</p>

<div class="callout mt-s">

A Faixa 1 compensa isolamento, não cobertura.

</div>

<Fonte>Edital SGTES/MS nº 3/2025, itens 11.1 a 11.4; CNES 06/2025 e Censo 2022 (IBGE); <code>output/aquisicao/quadro_vagas_tratamento.parquet</code>; figuras por <code>scripts/apresentacao/gerar_figuras_banca1.py</code>.</Fonte>

---

<Rastreio cont="1 de 2">1. Motivação e Pergunta · IVS e suas dimensões</Rastreio>

# Quanto maior o IVS, mais difícil é exercer ali

<div class="build-lbl">O que o índice mede</div>

<div class="bloco-lg mt-m">

<div class="card">

**IVS 2010, do Ipea** — do *Atlas da Vulnerabilidade Social nos Municípios Brasileiros*. Resume **16 indicadores** do **Censo 2010** em um número de **0 a 1**: quanto maior, mais vulnerável. Existe para **todos** os municípios, e é a **parte pública** da regra do valor — a outra, a do Anexo IV, não é.

</div>

<div class="card">

As categorias do item 11.1.4 são as do próprio Atlas: **muito alta** acima de **0,500**, **alta** entre **0,400** e **0,500**, e **demais** abaixo disso.

</div>

</div>

<Fonte>Ipea, <em>Atlas da Vulnerabilidade Social nos Municípios Brasileiros</em> (2015) — 16 indicadores do Censo 2010 em três sub-índices, e as faixas de classificação; Edital SGTES/MS nº 3/2025, item 11.1.4; <code>modelo_micro.md</code>, §3.1.</Fonte>

---

<Rastreio cont="2 de 2">1. Motivação e Pergunta · IVS e suas dimensões</Rastreio>

# Quanto maior o IVS, mais difícil é exercer ali

<div class="build-lbl">As três dimensões</div>

<div class="tbl-center mt-s">

| Dimensão | Indicadores | O que significa para quem vai atender ali |
|---|---|---|
| **Infraestrutura urbana** | saneamento, coleta de lixo, tempo de deslocamento | morar e circular custam mais |
| **Capital humano** | mortalidade infantil, analfabetismo, mães adolescentes | população mais doente, e serviço mais precário |
| **Renda e trabalho** | extrema pobreza, desemprego, informalidade | quase não há mercado privado para complementar a renda |

</div>

<div class="callout mt-m">

As três apontam para o mesmo lado: quanto maior o índice, mais caro é viver ali e mais duro é atender ali.

</div>

<Fonte>Ipea, <em>Atlas da Vulnerabilidade Social nos Municípios Brasileiros</em> (2015); Edital SGTES/MS nº 3/2025, item 11.1.4; <code>modelo_micro.md</code>, §3.1.</Fonte>

---

<Rastreio cont="1 de 3">1. Motivação e Pergunta · Efeitos</Rastreio>

# O programa já deu sinais; a literatura aponta para os dois lados

<div class="build-lbl">O que o ciclo 1 mostra</div>

<p class="xs mut tight mt-s">Preenchimento do ciclo 1, por faixa e por estrato territorial</p>

<Fig src="/fig/preenchimento_ciclo1.png" h="16rem" alt="Preenchimento do ciclo 1 — por faixa: 23,6% na Faixa 3, 37,4% na Faixa 2, 31,6% na Faixa 1; por território: 44,9% metropolitano, 35,6% capitais, 26,9% interior conectado, 20,5% interior remoto" />

<p class="sm mt-s">Das <strong>1.295 células</strong> da primeira chamada, <strong>393 (30,3%)</strong> tiveram alguém confirmado ou homologado.</p>

<Fonte>Dal Bó, Finan &amp; Rossi (2013), <em>QJE</em>; Scott et al. (2013), <em>Soc Sci Med</em> 96; Hone et al. (2020), <em>BMC HSR</em> 20:873. Ciclo 1: <code>output/tema_trabalho/</code>, módulos A4 e A5.</Fonte>

---

<Rastreio cont="2 de 3">1. Motivação e Pergunta · Efeitos</Rastreio>

# O programa já deu sinais; a literatura aponta para os dois lados

<div class="build-lbl">A leitura</div>

<div class="stack mt-m bloco-lg">

<div class="card">
<span class="card-lbl">Por faixa, não há ordem</span>

Pagar o dobro (31,6%) não preencheu mais que pagar uma vez e meia (37,4%).

</div>

<div class="card">
<span class="card-lbl">Por território, há</span>

De **44,9%** no metropolitano a **20,5%** no interior remoto.

</div>

</div>

<div class="callout mt-m">

**Isto é descrição, não efeito.** As faixas diferem em muito mais que na bolsa, e território prevê melhor que ela. Linguagem correta: **gradiente** e **associação**.

</div>

<Fonte>Ciclo 1: <code>output/tema_trabalho/</code>, módulos A4 e A5.</Fonte>

---

<Rastreio cont="3 de 3">1. Motivação e Pergunta · Efeitos</Rastreio>

# O programa já deu sinais; a literatura aponta para os dois lados

<div class="build-lbl">A literatura aponta para os dois lados</div>

<div class="cols cols-2 gap-s mt-s">

<div class="card">
<span class="card-lbl">Pagar mais funciona</span>

<span class="xs">**México, salário sorteado.** Em 106 postos, salário **33% maior** elevou a aceitação em **15 p.p.**; a mais de 200 km da cidade natal, de 25% para cerca de **80%**, sem perda de qualificação.</span>

<span class="xs">**O degrau tem o tamanho que a literatura pede.** O prêmio exigido para um posto pior vai de **37% a 64%** da renda anual, e a elasticidade da oferta no interior é **0,7**. O degrau do PMM-E é **+50%**.</span>

</div>

<div class="card">
<span class="card-lbl">Pagar mais não basta</span>

<span class="xs">**Brasil, o programa-irmão.** No Mais Médicos, **+15,1** médicos do programa por 100 mil viraram **+5,7** de expansão **líquida**. O resto substituiu quem já estava lá.</span>

<span class="xs">**Austrália, a maioria não vai por preço.** De 3.727 clínicos, **65%** ficaram onde estavam em **todos** os cenários. Para o pior posto, quem mudaria pedia **130%** da renda anual.</span>

</div>

</div>

<p class="ressalva mt-s"><strong>Ressalva:</strong> os percentuais são sobre a <strong>renda total</strong> do médico; a bolsa remunera <strong>20 horas</strong>.</p>

<div class="callout mt-s">

A evidência não decide se um degrau de R$ 5 mil basta.

</div>

<Fonte>Dal Bó, Finan &amp; Rossi (2013), <em>QJE</em>; Scott et al. (2013), <em>Soc Sci Med</em> 96; Hone et al. (2020), <em>BMC HSR</em> 20:873.</Fonte>

---

<Rastreio cont="1 de 2">1. Motivação e Pergunta · Pergunta de Pesquisa</Rastreio>

# A pergunta que organiza o trabalho

<div class="build-lbl">A cadeia que a política supõe</div>

<div class="fluxo mt-m">
  <div class="card-plain cadeia-escrito"><span class="xs">Regra de valor<br/>faixa de atração<br/>R$ 10 / 15 / 20 mil</span></div>
  <div class="fluxo-seta cadeia-sup">⇢</div>
  <div class="card-plain cadeia-suposto"><span class="xs">Decisão<br/>do médico</span></div>
  <div class="fluxo-seta cadeia-sup">⇢</div>
  <div class="card-plain cadeia-suposto"><span class="xs">Preenchimento<br/>da vaga</span></div>
  <div class="fluxo-seta">→</div>
  <div class="card-plain cadeia-escrito"><span class="xs">Oferta de especialista<br/>no município</span></div>
  <div class="fluxo-seta cadeia-sup">⇢</div>
  <div class="card-plain cadeia-suposto"><span class="xs">Produção<br/>assistencial</span></div>
  <div class="fluxo-seta">→</div>
  <div class="card-plain cadeia-escrito"><span class="xs">Redução do tempo<br/>de espera</span></div>
</div>

<p class="sm mt-m"><strong>Verde e cheia:</strong> está em ato oficial. <strong>Laranja e tracejada:</strong> suposição. Nem o elo cheio seguinte assegura <strong>oferta líquida</strong>: o edital só veda substituição de quem já está lá.</p>

<Fonte>Lei nº 15.233/2025; Edital SGTES/MS nº 3/2025, item 1.2.5; <code>01_pergunta_escopo/15</code>.</Fonte>

---

<Rastreio cont="2 de 2">1. Motivação e Pergunta · Pergunta de Pesquisa</Rastreio>

# A pergunta que organiza o trabalho

<div class="pergunta" style="margin-top:0.3rem">O incentivo financeiro oferecido pelo PMM-E funciona para atrair especialistas para regiões mais vulneráveis?</div>

<p class="sm tight" style="margin-top:1.3rem">Dois objetos, um contra o outro:</p>

<div class="cols cols-2 gap-s">
  <div class="card">
    <span class="card-lbl">O preço</span>
    <span class="sm">que a política pôs sobre a vulnerabilidade, o <strong>degrau de R$ 5 mil</strong>.</span>
  </div>
  <div class="card">
    <span class="card-lbl">A desvantagem</span>
    <span class="sm">que esse preço pretende <strong>compensar</strong>.</span>
  </div>
</div>

<p class="sm" style="margin-top:1.3rem">A margem observada é o <strong>preenchimento da vaga</strong> — o terceiro elo da cadeia, e o primeiro elo suposto é a hipótese do trabalho. Permanência fica fora desta banca.</p>

<Fonte>Lei nº 15.233/2025; Edital SGTES/MS nº 3/2025, item 1.2.5; <code>01_pergunta_escopo/15</code>.</Fonte>

---
layout: default
class: divisoria
---

<div class="div-rule"></div>
<div class="div-num">2</div>
<h1 class="div-titulo">Literatura Teórica e Modelo Microeconômico</h1>
<p class="div-sub">De onde vem a equação de escolha, e o que há dentro do custo</p>

---

<Rastreio>2. Literatura e Modelo · Literatura teórica usada</Rastreio>

# Três tradições sustentam uma equação

<div class="tbl-center tbl-tight mt-s">

| Trabalho | Entra no modelo como | Equações originais |
|---|---|---|
| **Moehling, Niemesh, Thomasson & Treber (2020)**, eq. 1, p. 184 | escolha locacional intertemporal: o médico maximiza o valor presente do rendimento real, líquido de um custo não pecuniário | $\arg\max\limits_{i \in I} \left\{ \sum_t \delta^t \left[ \frac{\mathbb{E}(w_{it}^{(s)})}{p_{it}} - c_{it}^{(s)} \right] \right\}$ |
| **Redding & Rossi-Hansberg (2017)**, eq. 24, p. 28 | equilíbrio espacial: amenidades e custo de moradia determinam a atratividade do lugar | $u_{nio} = \dfrac{z_{nio}\, B_n\, w_i}{\kappa_{ni}\, Q_n^{\,1-\beta}}$ |
| **Choné & Ma (2011)**, eq. 1, p. 232, com **Reinhardt (1972, 1975)** | utilidade do médico com altruísmo: atender cansa e satisfaz, e os dois passam por equipe e capital | $U = R - C(q; L, K) + \alpha B(q)$ |

</div>

<div class="sm mt-s">

Em Redding &amp; Rossi-Hansberg, o numerador é o que <strong>atrai</strong> — salário $w_i$, amenidades $B_n$, gosto pessoal $z_{nio}$ — e o denominador é o que <strong>repele</strong>: deslocamento $\kappa_{ni}$ e moradia $Q_n$.

</div>

<div class="callout mt-s">

**Atenção ao símbolo $B$.** Aqui $B_n$ é **amenidade** e $B(q)$ é **benefício ao paciente**. A **bolsa** é $B_m$, e só aparece no slide 13.

</div>

<Fonte>Moehling et al. (2020), <em>Cliometrica</em> 14, p. 184, eq. 1; Redding &amp; Rossi-Hansberg (2017), <em>Annual Review of Economics</em> 9, p. 28, eq. 24; Choné &amp; Ma (2011), <em>Annals of Economics and Statistics</em> 101/102, p. 232, eq. 1; Reinhardt (1972, 1975); <code>modelo_micro.md</code>, §1, §2 e §3.2.</Fonte>

---

<Rastreio cont="1 de 2">2. Literatura e Modelo · Modelo microeconômico conjunto</Rastreio>

# A escolha locacional maximiza a renda real líquida

<div class="build-lbl">A equação de escolha</div>

<div class="sm mt-s">

O médico $i$ escolhe o município $m$ que maximiza o valor presente do rendimento <strong>real</strong>, líquido do custo não pecuniário de viver e atender ali:

</div>

<div class="eq eq-lg">

$$\arg\max_{m \in M} \left\{ \sum_t \delta^t \left[ \frac{\mathbb{E}(w_{mt}^{(s)})}{p_{mt}} - c_{im}^{(s)} \right] \right\}$$

</div>

<div class="tbl-center tbl-tight mt-s">

| Termo | O que é | Termo | O que é |
|:--:|---|:--:|---|
| $m \in M$ | **municípios** candidatos | $p_{mt}$ | nível de preços local, o deflator |
| $\mathbb{E}(w^{(s)}_{mt})$ | remuneração esperada em $m$, no ano $t$, na especialidade $s$ | $c^{(s)}_{im}$ | custo **não pecuniário** de viver e atender ali |
| $\sum_t \delta^t$ | a escolha é de **carreira**, não de um mês | | |

</div>

<Fonte>Moehling et al. (2020), <em>Cliometrica</em> 14, p. 184, eq. 1; <code>modelo_micro.md</code>, §1 e §2.4.</Fonte>

---

<Rastreio cont="2 de 2">2. Literatura e Modelo · Modelo microeconômico conjunto</Rastreio>

# A escolha locacional maximiza a renda real líquida

<div class="build-lbl">Interpretação</div>

<div class="sm mt-s">

Deflaciona a remuneração, subtrai o custo do lugar, desconta a carreira inteira pelo fator $\delta$ e devolve o município de maior valor.

</div>

<div class="callout mt-s">

Salário nominal alto não compensa preços e custos locais altos.

</div>

<div class="sm mt-m">

Na equação original $i$ é a localidade; <strong>daqui em diante $i$ é o médico e $m$ é o município</strong>, porque o custo depende de quem escolhe, e não só de onde.

</div>

<div class="sm mt-s">

Para os próprios autores, $c$ reúne <em>"preferences over rural or urban living … such as proximity to family"</em> — uma <strong>caixa-preta</strong>. Os dois slides seguintes a abrem: primeiro o <strong>custo</strong> do lugar, depois a <strong>remuneração</strong> dele.

</div>

<Fonte>Moehling et al. (2020), <em>Cliometrica</em> 14, p. 184, eq. 1; <code>modelo_micro.md</code>, §1 e §2.4.</Fonte>

---

<Rastreio cont="1 de 3">2. Literatura e Modelo · Custo da localidade</Rastreio>

# O custo da localidade tem duas metades: o lugar e o trabalho

<div class="build-lbl">O lugar</div>

<p class="sm mt-s">De Redding &amp; Rossi-Hansberg, o custo do <strong>lugar</strong>:</p>

<div class="eq eq-lg eq-tall">

$$c^{\text{geo}}_{im} = \phi(\text{dist}_{im}) - \gamma A_m + \theta_i^{\text{rural}}$$

</div>

<div class="sm mt-m">

$\phi(\text{dist}_{im})$ é o afastamento da família, $A_m$ são as amenidades urbanas e $\theta_i^{\text{rural}}$ é o gosto pessoal por cidade pequena — o único termo sem sinal universal.

</div>

<Fonte><code>modelo_micro.md</code>, §2.1 a §2.3 e §3.2, de onde vêm as duas equações inferidas; Costa, Nunes &amp; Sanches (2024), <em>REStat</em>; as equações originais estão no slide 10.</Fonte>

---

<Rastreio cont="2 de 3">2. Literatura e Modelo · Custo da localidade</Rastreio>

# O custo da localidade tem duas metades: o lugar e o trabalho

<div class="build-lbl">O trabalho</div>

<p class="sm mt-s">De Choné &amp; Ma, com Reinhardt, o custo do <strong>trabalho</strong>:</p>

<div class="eq eq-lg">

$$c^{\text{laboral}}_{im} = C(q; L_m, K_m) - \alpha_i B(q; L_m, K_m)$$

</div>

<div class="sm mt-s">

$C$ é o cansaço de atender $q$ pacientes, $B$ é o benefício gerado a eles e $\alpha_i$ é o altruísmo do médico. Atender cansa de forma crescente ($C'' > 0$) e curar satisfaz de forma decrescente ($B'' < 0$): a curva do custo líquido é um <strong>U</strong> — atender mais compensa até um mínimo, e depois exaure.

</div>

<div class="callout mt-s">

**Extensão deste projeto**, motivada por Reinhardt: escrever $B(q; L, K)$, e não $B(q)$ — equipe e capital não só poupam esforço como ampliam o que o atendimento produz.

</div>

<Fonte><code>modelo_micro.md</code>, §2.1 a §2.3 e §3.2; as equações originais estão no slide 10.</Fonte>

---

<Rastreio cont="3 de 3">2. Literatura e Modelo · Custo da localidade</Rastreio>

# O custo da localidade tem duas metades: o lugar e o trabalho

<div class="build-lbl">As três desvantagens, na visão do médico</div>

<div class="tbl-center tbl-tight mt-s">

| Desvantagem | Termo | Por que pesa | Medimos? |
|---|:--:|---|:--:|
| **Sem retaguarda** | $L_m$ | não há segunda opinião nem a quem encaminhar: cansa mais e resolve menos | sim, colegas no CNES |
| **Sem infraestrutura** | $K_m$ | falta leito, insumo e equipamento: o mesmo esforço rende menos saúde | em parte |
| **Longe da família** | $\phi(\text{dist})$ | cada quilômetro custa, e ninguém paga por ele | não |

</div>

<p class="sm mt-s">No Brasil, entre 50 mil generalistas formados de 2001 a 2013, <strong>a proximidade do lugar de nascimento ou de formação é o principal fator</strong>; salário e infraestrutura pesam menos.</p>

<p class="ressalva mt-s"><strong>Limitação assumida:</strong> CNES e edital não informam a residência do profissional, por sigilo fiscal. A unidade é o <strong>município do estabelecimento</strong>; a distância entra como latente.</p>

<Fonte><code>modelo_micro.md</code>, §2.1 a §2.3 e §3.2; Costa, Nunes &amp; Sanches (2024), <em>REStat</em>.</Fonte>

---

<Rastreio cont="1 de 2">2. Literatura e Modelo · Remuneração da localidade</Rastreio>

# A bolsa é o piso da remuneração, não o total

<div class="build-lbl">A remuneração total</div>

<p class="sm mt-s">A lei fixa a <strong>bolsa</strong>, não a remuneração. A bolsa compra <strong>20 horas</strong>; o que o médico ganha além delas é mercado local. Por construção, a remuneração é maior ou igual à bolsa:</p>

<div class="eq eq-lg">

$$\mathbb{E}(w_{imt} \mid B_m) = \underbrace{B_m}_{\text{fixado pela regra}} + \underbrace{w^{\text{priv}}_m}_{\text{mercado local}} \;\geq\; B_m, \qquad w^{\text{priv}}_m \geq 0$$

</div>

<div class="tbl-center tbl-tight mt-s">

| | Capital ou metrópole | Interior isolado |
|---|---|---|
| **Bolsa $B_m$** | R$ 10 mil | R$ 20 mil |
| **Mercado $w^{\text{priv}}_m$** | maior | **menor — não nulo** |
| **Total $w$** | $\geq$ R$ 10 mil, e pode passar dos R$ 20 mil | $\geq$ R$ 20 mil, e perto do piso |
| **Deflator $p_m$** | custo de vida alto | supomos menor, e não é garantido: o custo logístico encarece parte da cesta |

</div>

<Fonte><code>modelo_micro.md</code>, §3; <code>hipoteses_e_viabilidade_empirica.md</code>, §2; Lei nº 15.233/2025, art. 21; Edital SGTES/MS nº 3/2025, itens 11.1.3 e 11.3.b.</Fonte>

---

<Rastreio cont="2 de 2">2. Literatura e Modelo · Remuneração da localidade</Rastreio>

# A bolsa é o piso da remuneração, não o total

<div class="build-lbl">Interpretação</div>

<p class="sm mt-s">A bolsa do interior é o <strong>dobro</strong> da da capital, e ainda assim a <strong>remuneração total</strong> pode ser <strong>menor</strong> lá: o que a regra acrescenta, o mercado local deixa de acrescentar. O deflator puxa no sentido oposto, e não se sabe a priori qual força vence.</p>

<div class="callout mt-s">

Esta é a quarta desvantagem do lugar: onde o mercado privado é fino, a remuneração encosta no piso da bolsa.

</div>

<div class="sm mt-m">

Pela dupla prática do slide 4, $w^{\text{priv}} > 0$ é a regra, não a exceção — o interior isolado tem <strong>menos</strong> mercado, não nenhum.

</div>

<div class="sm mt-s">

A política aposta que R$ 5 mil compensam o lugar. O modelo diz que eles competem com um mercado privado cuja escassez é, ela própria, uma desvantagem do lugar.

</div>

<Fonte><code>modelo_micro.md</code>, §3; <code>hipoteses_e_viabilidade_empirica.md</code>, §2.</Fonte>

---
layout: default
class: divisoria
---

<div class="div-rule"></div>
<div class="div-num">3</div>
<h1 class="div-titulo">Hipótese e Viabilidade Empírica</h1>
<p class="div-sub">O que o modelo implica, o que se testa e o que os dados permitem</p>

---

<Rastreio cont="1 de 3">3. Hipótese e Viabilidade · Implicações para o PMM-E</Rastreio>

# No PMM-E, a regra fixa a remuneração e o IVS organiza o custo

<div class="build-lbl">O modelo integrado</div>

<div class="eq eq-lg">

$$V_{im} = \sum_t \delta^t \left[ \frac{\mathbb{E}(w_{imt} \mid \mathbf{B}_m)}{p_{mt}} - c_{im} \right]$$

</div>

<div class="xs mut">

para o médico $i$ no município $m$, com $\mathbb{E}(w \mid \mathbf{B}_m) = \mathbf{B}_m + \mathbf{w}^{\text{priv}}_m$ do slide 13 e $c_{im} = c^{\text{geo}}_{im} + c^{\text{laboral}}_{im}$ do slide 12.

</div>

<div class="tbl-center tbl-xtight mt-s">

| Termo | Variável do programa | Derivada | Leitura |
|:--:|---|:--:|---|
| $\mathbf{B}_m$ | valor da bolsa | $\partial V/\partial \mathbf{B}_m > 0$ | é o instrumento |
| $\mathbf{w}^{\text{priv}}_m$ | mercado local, não observado | $\partial^2 V/\partial \mathbf{B}_m\, \partial \mathbf{w}^{\text{priv}} < 0$ | a bolsa vale mais onde há menos mercado |
| $p_m$ | custo de vida, por UF | $\partial V/\partial p_m < 0$ | opera contra a vulnerabilidade |
| $c_{im}$ | **IVS** e suas dimensões, do slide 6 | $c_0'(IVS) > 0$ | o custo **cresce** com o índice |

</div>

<div class="callout mt-s">

**O que Moehling, Redding & Rossi-Hansberg e Choné & Ma não têm:** remuneração fixada por **regra pública sobre um índice territorial**. É só isso que a adaptação ao PMM-E acrescenta.

</div>

<Fonte><code>modelo_micro.md</code>, §2.4, §3, §3.1 e §4.1; <code>hipoteses_e_viabilidade_empirica.md</code>, §3; Edital SGTES/MS nº 3/2025, item 11.1.3.</Fonte>

---

<Rastreio cont="2 de 3">3. Hipótese e Viabilidade · Implicações para o PMM-E</Rastreio>

# No PMM-E, a regra fixa a remuneração e o IVS organiza o custo

<div class="build-lbl">A condição de aceitação</div>

<div class="sm mt-s">

Distância, aluguel, mercado local e esforço clínico <strong>não são observados</strong>; o IVS é. O custo do lugar entra por ele, e o que é do médico fica no desvio individual: $c_{im} = c_0(IVS_m) + \eta_i$.

</div>

<div class="sm mt-s">

O médico $i$ aceita a vaga em $m$ quando ela supera sua melhor alternativa $\bar{v}_i$:

</div>

<div class="eq eq-lg">

$$\frac{\mathbf{B}_m + \mathbf{w}^{\text{priv}}_m}{p_m} - c_0(IVS_m) \;\geq\; \bar{v}_i$$

</div>

<p class="sm mt-s">A vaga é preenchida se existir <strong>ao menos um</strong> candidato para quem isso vale. Tudo que aumenta o lado esquerdo aumenta essa probabilidade.</p>

<Fonte><code>modelo_micro.md</code>, §2.4, §3, §3.1 e §4.1; <code>hipoteses_e_viabilidade_empirica.md</code>, §3.</Fonte>

---

<Rastreio cont="3 de 3">3. Hipótese e Viabilidade · Implicações para o PMM-E</Rastreio>

# No PMM-E, a regra fixa a remuneração e o IVS organiza o custo

<div class="build-lbl">Na fronteira entre faixas</div>

<p class="sm mt-s"><strong>O custo é obstáculo, não hipótese.</strong> Ele não varia livremente: a regra do edital o amarra à bolsa, e os dois sobem juntos. Preencher a vaga do lado mais vulnerável da fronteira exige</p>

<div class="eq eq-lg eq-tall">

$$\frac{\Delta \mathbf{B}_m}{p_m} > \Delta c_0, \qquad \Delta \mathbf{B}_m = \text{R\$ } 5.000$$

</div>

<div class="callout mt-m">

A pergunta da apresentação é se essa desigualdade vale.

</div>

<Fonte><code>modelo_micro.md</code>, §2.4, §3, §3.1 e §4.1; <code>hipoteses_e_viabilidade_empirica.md</code>, §3; Edital SGTES/MS nº 3/2025, item 11.1.3.</Fonte>

---

<Rastreio>3. Hipótese e Viabilidade · Hipótese do trabalho</Rastreio>

# Mais remuneração real, mais vagas preenchidas

<div class="hip" style="margin-top:1.2rem">
  <span class="hip-tag">H1</span>
  <div class="hip-txt">

Uma elevação na remuneração oferecida pelo PMM-E eleva a taxa de preenchimento das vagas ofertadas.

  </div>
  <div class="hip-eq">

$$\dfrac{\partial \Pr(\text{preenchimento}_m)}{\partial (\mathbf{B}_m / p_m)} > 0$$

  </div>
</div>

<p class="sm" style="margin-top:1.6rem">A margem é o <strong>preenchimento</strong> da vaga ofertada; permanência está fora desta apresentação.</p>

<Fonte><code>modelo_micro.md</code>, §4.1 e §4.2; <code>hipoteses_e_viabilidade_empirica.md</code>, §4.2.</Fonte>

---

<Rastreio cont="1 de 2">3. Hipótese e Viabilidade · Disponibilidade de dados</Rastreio>

# Há dado para quase todo termo — e sabemos quais faltam

<div class="build-lbl">O que observamos</div>

<div class="tbl-center tbl-tight mt-s">

| Termo | O que observamos | Fonte | Grau |
|---|---|---|:--:|
| **Preenchimento** | confirmação ou homologação por célula estabelecimento–curso, **ciclo 1** | quadros do edital | 🟢 direto |
| **Bolsa $\mathbf{B}_m$** | faixa anunciada em cada vaga e seu valor | edital e quadro de vagas, ciclos 1 a 3 | 🟢 direto |
| **Custo do lugar $c_m$** | o **IVS 2010**, que resume em um número o custo que não se observa | Ipea | 🟡 proxy |
| **Custo de vida $p_m$** | diferenças entre estados, por efeito fixo de UF | IBGE | 🟡 proxy |
| **Equipe $L$** | colegas da especialidade no município, 12 meses prévios | CNES mensal | 🟡 proxy |

</div>

<Fonte><code>04_dados/02_inventario_dados_por_outcome.md</code>; <code>hipoteses_e_viabilidade_empirica.md</code>, §3; Ipea, <em>Atlas da Vulnerabilidade Social</em> (2015); <code>output/tema_trabalho/</code> e <code>output/aquisicao/</code>.</Fonte>

---

<Rastreio cont="2 de 2">3. Hipótese e Viabilidade · Disponibilidade de dados</Rastreio>

# Há dado para quase todo termo — e sabemos quais faltam

<div class="build-lbl">O que falta</div>

<div class="tbl-center tbl-tight mt-s">

| Termo | Por que não observamos | Por onde entra |
|---|---|---|
| **Mercado local $\mathbf{w}^{\text{priv}}$** | RAIS nunca adquirida; CNES não traz renda nem carga horária | IVS, dimensão de renda e trabalho |
| **Custo de moradia** | sem fonte municipal no repositório | IVS, dimensão de infraestrutura urbana |
| **Capital $K$ e volume $q$** | competências do CNES físico não baixadas; SIH bloqueado | IVS, dimensões de infraestrutura e capital humano |
| **Distância da família** | residência do profissional é sigilo fiscal | não é do lugar: fica no desvio individual $\eta_i$ |

</div>

<p class="sm mt-s"><strong>Sim, para o essencial:</strong> desfecho e instrumento são diretos, e o custo do lugar entra inteiro pelo <strong>IVS</strong> — quanto maior o índice, maior o custo.</p>

<div class="callout mt-s">

O IVS é a proxy declarada do que não se mede. Isso é uma escolha, não uma solução.

</div>

<Fonte><code>04_dados/02_inventario_dados_por_outcome.md</code>; <code>hipoteses_e_viabilidade_empirica.md</code>, §3; <code>output/tema_trabalho/</code> e <code>output/aquisicao/</code>.</Fonte>

---
layout: default
class: divisoria
---

<div class="div-rule"></div>
<h1 class="div-titulo">Perguntas</h1>
<p class="div-sub">O material de apoio está no apêndice, a seguir</p>

---

<Rastreio semnum cont="1 de 4">Apêndice · A1</Rastreio>

# Por que o desafio metodológico não está na apresentação

<div class="build-lbl">A regra existe e é determinística</div>

<p class="sm mt-s">Na janela estável de fev a ago/2026, o rótulo administrativo de IVS determina a faixa de bolsa em <strong>527 de 527</strong> municípios, sem uma única ambiguidade.</p>

<p class="sm mt-s">O que não se recupera é o <strong>escore</strong>. A regra de facto não é a publicada: em oito das nove competências, muito alta e alta vão para a <strong>Faixa 1</strong>, média para a <strong>Faixa 2</strong>, baixa e muito baixa para a <strong>Faixa 3</strong>. Só jan/2026 segue o texto do FAQ.</p>

<div class="callout mt-m">

O problema nunca foi a regra não existir. É que o escore que a alimenta não é o IVS 2010 público.

</div>

<Fonte><code>05_identificacao/14</code>, seções de suporte comum e de reprodução da faixa; <code>05_identificacao/16</code>, §3.5 e §3.5.1.</Fonte>

---

<Rastreio semnum cont="2 de 4">Apêndice · A1</Rastreio>

# Por que o desafio metodológico não está na apresentação

<div class="build-lbl">Nenhum corte sobre o IVS público reproduz a atribuição</div>

<div class="tbl-center mt-s">

| Regra testada sobre o IVS 2010 público | Acerto |
|---|---:|
| Cortes do Ipea supostos, **0,400** e **0,500** | 191 de 368 — **51,9%** |
| Melhor par de cortes, por busca exaustiva, em 0,323 e 0,377 | 285 de 368 — **77,4%** |

</div>

<p class="sm mt-m">Em 44.073 pares comparáveis há <strong>2.763 inversões (6,3%)</strong>: municípios com IVS <em>maior</em> que recebem bolsa <em>menor</em>. Uma inversão já basta para provar que nenhuma regra monótona de limiar reproduz o anúncio, qualquer que seja o corte.</p>

<Fonte><code>05_identificacao/14</code>, §"Quanto falta" e §"Nenhum limiar reproduz a faixa".</Fonte>

---

<Rastreio semnum cont="3 de 4">Apêndice · A1</Rastreio>

# Por que o desafio metodológico não está na apresentação

<div class="build-lbl">Nos dois cortes, não há o que saltar</div>

<div class="stack mt-m bloco-lg">

<div class="card">
<span class="card-lbl">Em 0,500 não há o que saltar</span>

Na janela de $\pm 0{,}050$ há 31 municípios e **todos são Faixa 1**, dos dois lados.

</div>

<div class="card">
<span class="card-lbl">Em 0,400 não há Faixa 3 por perto</span>

O maior IVS da Faixa 3 é **0,372**.

</div>

</div>

<div class="callout mt-m">

Onde a bolsa de fato varia, a variação é governada pelo critério de localização, que não observamos.

</div>

<Fonte><code>05_identificacao/14</code>, tabela de janelas; <code>05_identificacao/16</code>, §3.5.</Fonte>

---

<Rastreio semnum cont="4 de 4">Apêndice · A1</Rastreio>

# Por que o desafio metodológico não está na apresentação

<div class="build-lbl">E a variação que sobra não é ruído</div>

<p class="sm mt-s">Dos 83 municípios fora da melhor regra, os <strong>41</strong> que recebem mais do que o IVS preveria têm mediana de população de <strong>7.933</strong> contra <strong>32.179</strong> dos <strong>42</strong> que recebem menos, e <strong>12 de 41</strong> estão em interior remoto contra <strong>2 de 42</strong>.</p>

<div class="callout mt-s">

O tratamento é localmente constante nos dois cortes, e o que sobra está alinhado com remoticidade — o previsor mais forte do próprio desfecho.

</div>

<p class="sm mt-m"><strong>O que destrava:</strong> um único campo, o <strong>escore administrativo de IVS por município</strong>, com safra, precisão e arredondamento. Com ele o primeiro estágio é <em>sharp</em> por construção, porque a categoria já determina a faixa em 527/527.</p>

<Fonte><code>05_identificacao/14</code>, §"Por que comparar municípios parecidos também não resolve"; <code>05_identificacao/16</code>, §3.5.1.</Fonte>

---

<Rastreio semnum>Apêndice · A2</Rastreio>

# A literatura que ficou de reserva

<p class="sm mt-s">Os dois trabalhos que saíram da tabela do slide 7 quando ela foi reduzida a dois de cada lado. Ambos continuam registrados no repositório.</p>

<div class="tbl-center tbl-tight mt-s">

| Trabalho | O que mede | O que encontra |
|---|---|---|
| **Costa, Nunes & Sanches (2024)**, *REStat* 106(1) | escolha locacional de generalistas formados no Brasil, escolha discreta com coeficientes aleatórios | elevar em **50%** o salário público no interior do Norte e Nordeste corrige **12,4%** do desequilíbrio geográfico, a **US$ 15,7 milhões** por ponto percentual. Cotas em escolas médicas para nascidos em áreas desassistidas corrigem **63,8%**, a **US$ 2,2 a 5,1 milhões** por ponto |
| **Pathman, Konrad & Ricketts (1992)**, *JAMA* 268(12) | coorte de nove anos, 412 médicos nos Estados Unidos | oito anos depois, **12%** dos que foram com bolsa e **obrigação de serviço** seguiam na prática original, contra **39%** dos que foram **sem** obrigação |

</div>

<p class="sm mt-s"><strong>Um mede o preço de mover; o outro, o preço de fazer ficar.</strong> Nenhum dos dois foi para a tela, e os dois respondem perguntas prováveis.</p>

<p class="xs mut mt-s">Os próprios autores do primeiro escrevem que <em>"as baixas elasticidades-salário podem explicar por que incentivos financeiros no Brasil não foram suficientes para atrair mais médicos para áreas desassistidas"</em>.</p>

<Fonte><code>03_literatura_empirica/19</code>, seções 3 e de evidência empírica.</Fonte>

---

<Rastreio semnum>Apêndice · A3</Rastreio>

# Duas notas sobre a regra que não vão à tela

<div class="tbl-center tbl-tight mt-s">

| Nota | O que diz | Onde está |
|---|---|---|
| **Contribuição previdenciária** | o participante é segurado obrigatório do RGPS, como **contribuinte individual**, e o valor devido é **descontado da bolsa-formação** | Edital SGTES/MS nº 3/2025, **item 11.2** |
| **Adicional territorial** | a Lei prevê acréscimo para **Amazônia Legal**, territórios indígenas e áreas de alta vulnerabilidade, *"conforme regulamentação do Ministério da Saúde e disponibilidade orçamentária"*. **Não foi regulamentado no ciclo 1**: a palavra "adicional" aparece uma única vez no edital, e no barema de titulação | Lei nº 15.233/2025, **art. 22-D, §4º** |

</div>

<div class="callout mt-m">

Nenhuma das duas vira afirmação sobre o tamanho líquido do degrau de R$ 5 mil: isso depende do teto de contribuição, e não foi calculado.

</div>

<p class="sm mt-s">É essa a razão de estarem aqui e não no slide 5. O degrau que a apresentação discute é o <strong>anunciado</strong>, bruto, que é o que a regra fixa e o que o candidato lê no quadro de vagas.</p>

<Fonte><code>auditorias/01_regra_institucional.md</code>; <code>03_proveniencia_figuras_e_numeros.md</code>, seção da regra institucional, onde as duas estão conferidas no PDF do DOU.</Fonte>

---

<Rastreio semnum>Apêndice · A4</Rastreio>

# O que ainda não fechamos

<p class="sm mt-s">As pendências abertas, com o efeito de cada uma sobre o que foi dito.</p>

<div class="tbl-center tbl-tight mt-s">

| # | Pendência | Efeito sobre a tela |
|:--:|---|---|
| **1** | a figura por UF é dos **quatro** valores com fonte registrada, não das 27 unidades | a tela perde o panorama completo por UF |
| **2** | os valores de deslocamento não tiveram a **fonte primária confirmada** | número em tela atribuído à REGIC 2018, a confirmar |
| **5** | "Sudeste 55,4% dos especialistas" está conferido em cobertura, não localizado no PDF | ressalva de fonte; fora da tela |
| **8** | a retaguarda é medida no **município**, mas 42,6% das células estão em estabelecimento de gestão estadual | ou o slide 5 ganha uma linha de limitação, ou o descasamento vira argumento próprio |
| **9** | os slides 6, 15 e 17 dizem que o **custo cresce com o IVS**; o documento canônico trata o sinal como **ambíguo** | divergência declarada entre a tela e a teoria do projeto, por decisão do autor |

</div>

<div class="callout mt-m">

Nenhuma delas muda a pergunta nem a hipótese. Todas são de rastreio ou de simplificação declarada.

</div>

<Fonte>A seção <em>Pendências abertas</em> no fim de <code>02_conteudo_slides.md</code>; <code>03_proveniencia_figuras_e_numeros.md</code>, seção 3.</Fonte>
