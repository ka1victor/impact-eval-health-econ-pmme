---
theme: slidev-theme-academic
title: Desvantagens territoriais na escolha locacional de médicos especialistas
info: |
  Banca 1 — conteúdo canônico em docs/07_apresentacoes/banca1/02_conteudo_slides.md.
  Este deck é artefato derivado: divergência entre deck e documento de conteúdo é erro do deck.
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
  sans: Source Sans 3
  serif: Source Serif 4
  mono: ui-monospace
defaults:
  class: centrado
layout: cover
coverDate: ''
class: centrado
---

<div class="capa-rule"></div>

<h1 class="capa-titulo">Desvantagens territoriais na escolha locacional de médicos especialistas</h1>

<p class="capa-sub">Um modelo microeconômico para o preenchimento de vagas do Programa Mais Médicos Especialistas</p>

<p class="capa-meta">Autoria &middot; instituição &middot; data da banca</p>

---

# Sumário

<div class="sumario">
  <div class="sumario-item"><span class="sumario-n">1</span><span class="sumario-t">Motivação</span></div>
  <div class="sumario-item"><span class="sumario-n">2</span><span class="sumario-t">Pergunta</span></div>
  <div class="sumario-item"><span class="sumario-n">3</span><span class="sumario-t">Literatura teórica</span></div>
  <div class="sumario-item"><span class="sumario-n">4</span><span class="sumario-t">Modelo microeconômico</span></div>
  <div class="sumario-item"><span class="sumario-n">5</span><span class="sumario-t">Hipótese</span></div>
  <div class="sumario-item"><span class="sumario-n">6</span><span class="sumario-t">Viabilidade empírica</span></div>
</div>

---
class: centrado stat-lg
---

<Rastreio cont="1 de 2">1. Motivação · O problema · 1 de 2</Rastreio>

# Especialistas não faltam; faltam no interior

<p class="lead">O Brasil tinha, em 2024, <strong>353 mil médicos especialistas</strong> — 59% dos 597 mil médicos do país. O problema não é o número. É onde eles estão.</p>

<div class="cols cols-3 mt-s">
  <div class="stat">
    <span class="stat-num">55<small>%</small> <span class="mut" style="font-weight:400">/</span> 6<small>%</small></span>
    <span class="stat-txt">dos especialistas estão no <strong>Sudeste</strong> / no <strong>Norte</strong></span>
  </div>
  <div class="stat">
    <span class="stat-num">453 <span class="mut" style="font-weight:400">/</span> 68 <span class="mut" style="font-weight:400">e</span> 70</span>
    <span class="stat-txt">especialistas por 100 mil habitantes no <strong>Distrito Federal</strong> / no <strong>Maranhão</strong> e no <strong>Pará</strong></span>
  </div>
  <div class="stat">
    <span class="stat-num">10<small>%</small></span>
    <span class="stat-txt">“apenas <strong>10%</strong> dos especialistas atendem no SUS. Além disso, há concentração desses profissionais nas capitais e regiões mais ricas do país”</span>
  </div>
</div>

<Fonte>Scheffer et al., <em>Demografia Médica no Brasil 2025</em> (FMUSP/AMB), dados de dezembro de 2024. A citação é do Senado Notícias, 25/09/2025, citando o Ministério da Saúde.</Fonte>

---

<Rastreio cont="2 de 2">1. Motivação · O problema · 1 de 2</Rastreio>

# Especialistas não faltam; faltam no interior

<p class="lead">Quem sente a falta é o paciente do SUS fora dos grandes centros. Em 2025 o Ministério da Saúde reconheceu <strong>situação de urgência em saúde pública</strong> em todo o país, por 24 meses, em razão do tempo de espera por consultas, exames e cirurgias na atenção especializada — e lançou o programa Agora Tem Especialistas, do qual o <strong>PMM-E é o braço de provimento</strong>.</p>

<div class="stack mt-m manchete-lg">
  <div class="manchete">
    <span class="manchete-txt">“Ministério da Saúde decreta situação de urgência em saúde pública pelos próximos dois anos”</span>
    <span class="manchete-src">Correio do Povo, 07/05/2025</span>
  </div>
  <div class="manchete">
    <span class="manchete-txt">“Aprovada no Senado, MP deve reduzir fila para atendimento por especialista no SUS”</span>
    <span class="manchete-src">Senado Notícias, 25/09/2025</span>
  </div>
</div>

<Fonte>Portaria GM/MS nº 7.061, de 6 de junho de 2025; recortes de imprensa citados.</Fonte>

---

<Rastreio cont="1 de 2">1. Motivação · O problema · 2 de 2</Rastreio>

# O que o médico vê ao decidir

<p class="lead">Para o médico, “município vulnerável” não é um índice. É um conjunto de desvantagens concretas. Quatro aparecem de forma consistente na literatura — <strong>duas delas nós conseguimos medir</strong>.</p>

<div class="tbl-center fill fill-tbl">

| Desvantagem | O que significa para o médico | Medimos? |
|---|---|---|
| **Retaguarda profissional** | poucos ou nenhum colega da mesma especialidade; sem segunda opinião, sem escala de plantão, sem a quem encaminhar o caso difícil | **sim** — página anterior |
| **Infraestrutura** | equipamento, insumos e equipe de apoio escassos; o atendimento cansa mais e resolve menos | **em parte** — leitos e equipamentos do CNES |
| **Distância da família** | o custo de viver longe de onde a família está, e onde o médico nasceu ou se formou | não |
| **Mercado privado ausente** | sem consultório ou plano de saúde local, a remuneração se reduz ao que o programa paga | não |

</div>

---

<Rastreio cont="2 de 2">1. Motivação · O problema · 2 de 2</Rastreio>

# O que o médico vê ao decidir

<p class="lead tight">O que a literatura diz sobre o peso de cada uma:</p>

<div class="stack mt-s">

<div class="card">
<span class="card-lbl">Estados Unidos, início do século XX</span>

A escolha do lugar já dependia de *“preferences over rural or urban living, or other location-specific attributes, such as proximity to family”*. <span class="cite">Moehling et al. (2020)</span>

</div>

<div class="card">
<span class="card-lbl">Brasil, 50 mil generalistas formados de 2001 a 2013</span>

**A proximidade do lugar de nascimento ou de formação é o principal fator** da escolha locacional; salário e infraestrutura importam, mas em escala menor. <span class="cite">Costa, Nunes &amp; Sanches (2024)</span>

</div>

<div class="card">
<span class="card-lbl">Austrália, 3.727 clínicos consultados</span>

Perguntou-se o que os faria mudar para o interior. **65% não mudariam por pacote nenhum.** Para os demais, o valor exigido depende do tamanho da cidade e — nas palavras dos autores — *“not only of the area but also of the characteristics of the job”*. <span class="cite">Scott et al. (2013)</span>

</div>

</div>

<Fonte>Moehling, Niemesh, Thomasson &amp; Treber (2020), <em>Cliometrica</em>, p. 184; Costa, Nunes &amp; Sanches (2024), <em>Review of Economics and Statistics</em>; Scott et al. (2013), <em>Social Science &amp; Medicine</em>.</Fonte>

---

<Rastreio cont="1 de 3">1. Motivação · A política · 1 de 2</Rastreio>

# O que é o PMM-E

<div class="cols cols-2" style="margin-top:0.1rem">

<div class="card">
<span class="card-lbl">Lei</span>

A Lei nº 15.233/2025 criou o Projeto Mais Médicos Especialistas dentro do Programa Mais Médicos, *“destinado ao provimento de profissionais com vistas à redução no tempo de espera de atendimento ao usuário do SUS, nas regiões prioritárias”*, como braço formativo do programa Agora Tem Especialistas.

</div>

<div class="card">
<span class="card-lbl">Quem</span>

Médicos com diploma brasileiro ou revalidado e **registro de especialista (RQE)** na área da vaga. Não é concurso nem emprego: o médico recebe **bolsa-formação** mensal do Ministério da Saúde, sem vínculo.

</div>

</div>

<div class="card mt-s">
<span class="card-lbl">O quê</span>

Um **aprimoramento em serviço** de **12 meses**, com **20 horas semanais** em estabelecimento do SUS, supervisão e mentoria de uma instituição formadora, e imersões em serviços de referência. São **16 cursos**:

<div class="cols cols-2 gap-s">

<div class="card-plain">
<span class="chip">6 cirúrgicos</span>

<span class="xs">anestesiologia; cirurgia geral, oncológica, colorretal, digestiva e ginecológica</span>

</div>

<div class="card-plain">
<span class="chip">10 ambulatoriais</span>

<span class="xs">endoscopia e colonoscopia, oncologia clínica, radioterapia, ecocardiografia, ultrassonografia mamária, colposcopia, videolaringoscopia, anatomia patológica</span>

</div>

</div>

<p class="sm gap-s tight">O foco é o <strong>câncer</strong> e o <strong>diagnóstico</strong> que o SUS mais espera.</p>

</div>

<Fonte>Lei nº 15.233/2025, art. 22-D; Portaria GM/MS nº 7.177/2025; Edital SGTES/MS nº 3/2025 (DOU 24/07/2025), itens 1, 3 e 11.</Fonte>

---

<Rastreio cont="2 de 3">1. Motivação · A política · 1 de 2</Rastreio>

# O que é o PMM-E

<p class="lead tight"><strong>Como a vaga chega ao médico.</strong></p>

<div class="stack passos-lg mt-s">
  <div class="card-plain"><span class="num-badge">1</span><span>O <strong>estado ou município</strong> indica o serviço e a especialidade.</span></div>
  <div class="card-plain"><span class="num-badge">2</span><span>A <strong>comissão bipartite</strong> prioriza.</span></div>
  <div class="card-plain"><span class="num-badge">3</span><span>O <strong>Ministério</strong> analisa a capacidade instalada e publica o quadro de vagas com município, estabelecimento, curso e <strong>faixa de bolsa</strong>.</span></div>
  <div class="card-plain"><span class="num-badge">4</span><span>O <strong>médico</strong> escolhe <strong>até dois locais</strong>, em ordem de preferência, e é classificado por titulação e tempo de formação.</span></div>
</div>

<div class="ressalva gap-m">O serviço <strong>não pode substituir</strong> profissional já contratado por um bolsista.</div>

<Fonte>Edital SGTES/MS nº 3/2025 (DOU 24/07/2025), itens 4 e 5.</Fonte>

---

<Rastreio cont="3 de 3">1. Motivação · A política · 1 de 2</Rastreio>

# O que é o PMM-E

<p class="lead tight"><strong>Onde, no primeiro ciclo</strong> (julho de 2025).</p>

<div class="cols cols-55 center-y" style="margin-top:0.25rem">
  <Fig src="/fig/vagas_ciclo1_por_regiao.png" alt="Células e vagas imediatas do ciclo 1 por região" h="19rem" />
  <div class="stack">

<div class="callout-soft">

**1.295 vagas** estabelecimento–curso em **460 estabelecimentos** e **368 municípios**, em todas as UFs; **678** para preenchimento imediato e **1.145** em cadastro de reserva.

</div>

<ul class="sm">
<li>O <strong>Nordeste</strong> concentra <strong>39%</strong> das vagas.</li>
<li><strong>Minas Gerais</strong> é o estado com mais vagas (252).</li>
<li>Dois terços dos municípios têm <strong>menos de 100 mil habitantes</strong>; 18 são capitais.</li>
</ul>

  </div>
</div>

<Fonte>Quadro de vagas do ciclo 1, chamada 1; Edital SGTES/MS nº 3/2025; Censo 2022 (IBGE).</Fonte>

---

<Rastreio cont="1 de 2">1. Motivação · A política · 2 de 2</Rastreio>

# A bolsa remunera o lugar

<p class="lead tight">O valor da bolsa não depende da especialidade, da carga nem do que o médico produz. Depende de <strong>onde fica o município</strong>, em três passos:</p>

<div class="fluxo mt-s">

<div class="card">
<span class="card-lbl">1 · O índice</span>

<span class="xs">O **IVS 2010 do Ipea** resume, em um número de 0 a 1, dezesseis indicadores do Censo 2010 em três dimensões: infraestrutura urbana (saneamento, lixo, tempo de deslocamento), capital humano (mortalidade infantil, analfabetismo, crianças fora da escola) e renda e trabalho (pobreza, desemprego, informalidade).</span>

</div>

<div class="fluxo-seta">→</div>

<div class="card">
<span class="card-lbl">2 · A categoria</span>

<span class="xs">O Ipea corta o índice em **cinco categorias**: muito baixa (até 0,200), baixa (0,201–0,300), média (0,301–0,400), alta (0,401–0,500) e muito alta (acima de 0,500).</span>

</div>

<div class="fluxo-seta">→</div>

<div class="card">
<span class="card-lbl">3 · O valor</span>

<span class="xs">O **edital de 2025** agrupou as cinco categorias em **três faixas**.</span>

<div class="tbl-tight nowrap-last" style="margin-top:0.35rem">

| Categoria | Faixa | Bolsa |
|---|:--:|--:|
| muito alta | 1 | R$ 20.000 |
| alta | 2 | R$ 15.000 |
| média, baixa ou muito baixa | 3 | R$ 10.000 |

</div>

</div>

</div>

<Fonte>Ipea, <em>Atlas da Vulnerabilidade Social nos Municípios Brasileiros</em> (2015); Edital SGTES/MS nº 3/2025, item 11.1.3, e retificação.</Fonte>

---

<Rastreio cont="2 de 2">1. Motivação · A política · 2 de 2</Rastreio>

# A bolsa remunera o lugar

<div class="cols cols-55 center-y" style="margin-top:0.1rem">
  <Fig src="/fig/bolsa_por_faixa.png" alt="Bolsa mensal por faixa de atração" h="18.5rem" />
  <div class="stack">

<p class="sm tight">No ciclo 1, <strong>102 municípios</strong> foram publicados na Faixa 1, <strong>107</strong> na Faixa 2 e <strong>159</strong> na Faixa 3.</p>

<div class="ressalva">

**O IVS é o piso, não o critério.** O edital tem duas cláusulas: a 11.1.4 dá a tabela, e a **11.1.3** manda seguir "critérios de **localização** e vulnerabilidade" definidos no **Anexo IV**, que o edital não reproduz.

</div>

<div class="ressalva">

A divergência tem **uma direção só**: em 177 dos 368, **zero** municípios abaixo do que a categoria manda e **177** acima. E a grade mudou em 2026, quando a categoria *alta* passou à Faixa 1. Vale sempre a **faixa publicada na vaga**.

</div>

  </div>
</div>

<Fonte>Edital SGTES/MS nº 3/2025, item 11.1.3, e retificação; Chamamento SGTES/MS nº 1/2026; quadro de vagas do ciclo 1.</Fonte>

---

<Rastreio cont="1 de 2">1. Motivação · O efeito é incerto · 1 de 4</Rastreio>

# Onde a bolsa é maior, o médico fica sozinho

<div class="cols cols-38 fill" style="margin-top:0.2rem">
  <div class="stack">

<p class="sm">O retrato nacional se repete dentro do programa. Nos <strong>295 municípios</strong> que receberam vaga no ciclo 1, um mês antes da oferta ser publicada:</p>

<div class="callout">

**Por habitante, a bolsa maior não vai para onde falta mais.** Ela vai para municípios pequenos, onde poucos profissionais já produzem taxa alta: **18,3** por 100 mil na Faixa 1 contra **15,0** na Faixa 3.

</div>

  </div>
  <Fig src="/fig/oferta_pre_por_faixa.png" alt="Especialistas por 100 mil habitantes em junho de 2025, por faixa de bolsa" h="fill" />
</div>

<Fonte>CNES, competência 06/2025; 295 municípios com vaga no ciclo 1; Censo 2022 (IBGE). <strong>Faixa pela bolsa publicada em cada vaga</strong>, não pela categoria de IVS recalculada — as duas divergem em 177 dos 368 municípios.</Fonte>

---

<Rastreio cont="2 de 2">1. Motivação · O efeito é incerto · 1 de 4</Rastreio>

# Onde a bolsa é maior, o médico fica sozinho

<div class="callout">

**Em número de colegas, vai.** Na Faixa 1 a mediana é de **2,5** colegas da mesma especialidade contra **6,5** na Faixa 3, e em **31%** dos casos o especialista **seria o único, ou teria um só colega** — contra 12% na Faixa 3.

</div>

<Fig src="/fig/retaguarda_por_faixa.png" alt="Colegas da mesma especialidade no município, junho de 2025" h="fill" class="fill mt-s" />

<Fonte>CNES, competência 06/2025; mesma definição da página anterior. Faixa pela bolsa publicada em cada vaga.</Fonte>

---

<Rastreio cont="1 de 2">1. Motivação · O efeito é incerto · 2 de 4</Rastreio>

# Pagar mais funciona: a evidência a favor

<p class="lead">O programa aposta que dinheiro compensa lugar ruim. A aposta tem precedente.</p>

<div class="callout mt-s">

**No México, o salário foi sorteado.** Um concurso público real distribuiu 106 postos em municípios pobres e anunciou, ao acaso, dois salários.

</div>

<div class="cols cols-2 mt-m">
  <div class="stat">
    <span class="stat-num">+15 <small>p.p.</small></span>
    <span class="stat-txt">Onde o salário era <strong>33% maior</strong>, a aceitação da vaga subiu 15 pontos percentuais.</span>
  </div>
  <div class="stat">
    <span class="stat-num">25<small>%</small> → ~80<small>%</small></span>
    <span class="stat-txt">Nos postos a <strong>mais de 200 km</strong> da cidade natal do candidato, a aceitação foi de 25% para cerca de 80%.</span>
  </div>
</div>

<p class="sm mt-s">O aumento <strong>anulou</strong> a rejeição aos municípios de menor desenvolvimento humano, sem atrair candidatos menos qualificados ou menos motivados.</p>

<Fonte>Dal Bó, Finan &amp; Rossi (2013), <em>Quarterly Journal of Economics</em>.</Fonte>

---

<Rastreio cont="2 de 2">1. Motivação · O efeito é incerto · 2 de 4</Rastreio>

# Pagar mais funciona: a evidência a favor

<div class="callout">

**O degrau do PMM-E tem o tamanho que a literatura pede.**

</div>

<div class="cols cols-3 mt-m">
  <div class="stat">
    <span class="stat-num">37<small>%</small> – 64<small>%</small></span>
    <span class="stat-txt">da renda anual é o que um médico exige para ir a um posto pior, em cidades pequenas <strong>(Austrália)</strong>.</span>
  </div>
  <div class="stat">
    <span class="stat-num">0,7</span>
    <span class="stat-txt">é a ordem de grandeza com que a oferta de médicos no <strong>interior brasileiro</strong> responde a salário.</span>
  </div>
  <div class="stat">
    <span class="stat-num">+50<small>%</small></span>
    <span class="stat-txt">é o degrau do programa — <strong>R$ 5 mil sobre R$ 10 mil</strong> — que cai dentro dessa faixa.</span>
  </div>
</div>

<div class="ressalva mt-m">

**Ressalva.** Os percentuais da literatura são sobre a renda total do médico; a bolsa do PMM-E remunera 20 horas semanais.

</div>

<Fonte>Scott et al. (2013), <em>Social Science &amp; Medicine</em>; Costa, Nunes &amp; Sanches (2024), <em>Review of Economics and Statistics</em>.</Fonte>

---

<Rastreio cont="1 de 2">1. Motivação · O efeito é incerto · 3 de 4</Rastreio>

# Mas é caro, e não segura: a evidência contra

<div class="card">
<span class="card-lbl">Muitos não vão por preço nenhum</span>

Dos 3.727 clínicos australianos, **65%** escolheram ficar onde estavam em todos os cenários oferecidos. Para o pior posto, quem mudaria pedia **130%** da renda anual. <span class="cite">Scott et al. (2013), <em>Social Science &amp; Medicine</em></span>

</div>

<div class="card mt-m">
<span class="card-lbl">No Brasil, salário compra pouco e custa muito</span>

Um modelo calibrado com todos os generalistas formados entre 2001 e 2013 estima que:

</div>

<div class="cols cols-2 mt-s">
  <div class="stat">
    <span class="stat-num">12,4<small>%</small></span>
    <span class="stat-txt">do desequilíbrio na distribuição de médicos seria corrigido por <strong>+50% no salário público</strong> no interior do Norte e do Nordeste — a <strong>US$ 15,7 milhões por ponto percentual</strong>.</span>
  </div>
  <div class="stat">
    <span class="stat-num">63,8<small>%</small></span>
    <span class="stat-txt">seria corrigido por <strong>reservar vagas nas faculdades de medicina</strong> para quem nasceu nessas regiões — por <strong>US$ 2,2 a 5,1 milhões</strong> o ponto.</span>
  </div>
</div>

<Fonte>Costa, Nunes &amp; Sanches (2024), <em>Review of Economics and Statistics</em>.</Fonte>

---

<Rastreio cont="2 de 2">1. Motivação · O efeito é incerto · 3 de 4</Rastreio>

# Mas é caro, e não segura: a evidência contra

<div class="card">
<span class="card-lbl">E o médico vai embora quando a obrigação acaba</span>

Nos Estados Unidos, oito anos depois: <span class="cite">Pathman, Konrad &amp; Ricketts (1992), <em>JAMA</em></span>

</div>

<div class="cols cols-2 mt-s">
  <div class="stat">
    <span class="stat-num">12<small>%</small></span>
    <span class="stat-txt">dos médicos que foram para clínicas rurais <strong>com bolsa e obrigação de permanência</strong> ainda estavam lá.</span>
  </div>
  <div class="stat">
    <span class="stat-num">39<small>%</small></span>
    <span class="stat-txt">dos que foram <strong>sem obrigação nenhuma</strong> ainda estavam lá.</span>
  </div>
</div>

<div class="callout mt-m">

Dinheiro move alocação, mas é caro, não move todo mundo, e não garante que quem foi fique. **A evidência não decide se um degrau de R$ 5 mil basta.**

</div>

---

<Rastreio>1. Motivação · O efeito é incerto · 4 de 4</Rastreio>

# No primeiro ciclo, a bolsa maior não ordenou o preenchimento

<p class="sm tight">Das <strong>1.295 vagas</strong> da primeira chamada, <strong>30%</strong> tiveram alguém confirmado ou homologado. A bolsa maior não veio acompanhada de mais preenchimento — e o território, sim, ordenou o resultado:</p>

<Fig src="/fig/preenchimento_ciclo1.png" alt="Preenchimento do ciclo 1 por faixa de bolsa e por estrato territorial" h="fill" class="fill gap-s" />

<div class="callout gap-s">

**Pagar o dobro não preencheu mais que pagar uma vez e meia**, e o preenchimento cai da capital e da região metropolitana para o interior remoto. Isso é **descrição, não efeito**: as faixas diferem em muito mais do que no valor da bolsa. Mas é o suficiente para colocar a pergunta.

</div>

<Fonte>Quadro de vagas e resultados do ciclo 1, chamada 1 (Ministério da Saúde, 2025); estratos pela REGIC 2018 e pela composição de regiões metropolitanas e RIDEs de 2022 (IBGE).</Fonte>

---

<Rastreio>2. Pergunta</Rastreio>

# Pergunta

<div class="pergunta" style="margin-top:0.3rem">Maiores bolsas do PMM-E para municípios mais vulneráveis compensam suas desvantagens territoriais na atração de médicos especialistas?</div>

<p class="sm tight" style="margin-top:1.4rem">Dois objetos, um contra o outro:</p>

<div class="cols cols-2 gap-s">
  <div class="card">
    <span class="card-lbl">O preço</span>
    <span class="sm">que a política colocou sobre a vulnerabilidade — o <strong>degrau de R$ 5 mil</strong> entre faixas.</span>
  </div>
  <div class="card">
    <span class="card-lbl">A desvantagem</span>
    <span class="sm">que esse preço pretende <strong>compensar</strong>.</span>
  </div>
</div>

<p class="sm" style="margin-top:1.4rem">A margem que observamos é o <strong>preenchimento da vaga</strong>: se, ao final da chamada, apareceu alguém disposto a ocupá-la.</p>

---

<Rastreio>3. Literatura teórica · 1 de 3</Rastreio>

# A decisão: onde vale a pena estar

<p class="lead tight"><strong>Moehling, Niemesh, Thomasson &amp; Treber (2020)</strong> dão a <strong>estrutura da decisão</strong>: escolhe-se a localidade que maximiza o valor presente do rendimento <strong>real</strong>, líquido do custo não pecuniário de viver ali.</p>

<div class="eq eq-lg" style="margin-top:0.2rem">

$$\arg\max_{i \in I} \left\{ \sum_t \delta^t \left[ \dfrac{\mathbb{E}(w_{it}^{(s)})}{p_{it}} - c_{it}^{(s)} \right] \right\}$$

</div>

<div class="tbl-sinal mt-s fill fill-tbl">

| Termo | Leitura |
|---|---|
| $\sum_t \delta^t$ | a escolha é de **carreira**: fixar-se ou migrar ao fim do vínculo |
| $\mathbb{E}(w^{(s)}_{it}) / p_{it}$ | rendimento **deflacionado** pelo custo de vida local |
| $c^{(s)}_{it}$ | o que torna estar ali custoso e **não é pago em dinheiro** |
| $s$ | generalista atende em posto simples; **especialista** precisa de centro cirúrgico e leito |

</div>

<div class="callout mt-s">

Na definição dos próprios autores, $c$ reúne *"preferences over rural or urban living, or other location-specific attributes, such as proximity to family"* — uma **caixa-preta**. As duas referências seguintes a abrem.

</div>

<Fonte>Moehling et al. (2020), <em>Cliometrica</em> 14, p. 184, eq. 1.</Fonte>

---

<Rastreio>3. Literatura teórica · 2 de 3</Rastreio>

# Abrindo o custo, parte 1: o lugar

<p class="lead tight"><strong>Redding &amp; Rossi-Hansberg (2017)</strong> dão o <strong>custo geográfico</strong>: a utilidade de trabalhar num lugar depende do salário, das <strong>amenidades</strong> e do <strong>custo de moradia</strong>.</p>

<div class="eq" style="margin-top:0.2rem">

$$u_{nio} = \dfrac{z_{nio}\, B_n\, w_i}{\kappa_{ni}\, Q_n^{\,1-\beta}} \quad\Longrightarrow\quad c^{\text{espacial}}_m = (1-\beta)\ln Q_m - \ln A_m$$

</div>

<p class="sm tight">Somado à proximidade da família de Moehling et al.:</p>

<div class="eq eq-lg">

$$c^{\text{geo}}_{im} = \phi(\text{dist}_{im}) - \gamma A_m + \theta_i^{\text{rural}}$$

</div>

<div class="tbl-sinal mt-s fill fill-tbl">

| Componente | Sinal | Significado |
|---|---|---|
| $\phi(\text{dist}_{im})$ | $\phi' > 0$ | afastar-se da família custa, e custa mais a cada quilômetro |
| $-\gamma A_m$ | $< 0$ | amenidade urbana — saneamento, segurança, escola — compensa |
| $\theta_i^{\text{rural}}$ | $\gtrless 0$ | gosto por cidade pequena ou grande, sem sinal universal |

</div>

<Fonte rotulo="Limitação">CNES e edital não informam a residência do profissional, por sigilo fiscal. A unidade é o município do estabelecimento: $\text{dist}$ entra como latente.</Fonte>

---

<Rastreio cont="1 de 2">3. Literatura teórica · 3 de 3</Rastreio>

# Abrindo o custo, parte 2: o trabalho

<p class="lead tight"><strong>Choné &amp; Ma (2011)</strong> dão o <strong>custo laboral</strong>: soma-se a renda, subtrai-se o custo de atender e soma-se o benefício ao paciente, ponderado pelo <strong>altruísmo</strong>.</p>

<div class="eq" style="margin-top:0.2rem">

$$U = R - C(q; L, K) + \alpha B(q) \quad\Longrightarrow\quad c^{\text{laboral}}_{im} = C(q; L_m, K_m) - \alpha_i B(q; L_m, K_m)$$

</div>

<div class="tbl-sinal mt-s fill fill-tbl">

| Componente | Derivadas | Significado |
|---|---|---|
| $C(q)$ | $C' > 0,\ C'' > 0$ | atender cansa, e cansa de forma **crescente** |
| $\alpha_i B(q)$ | $B' > 0,\ B'' < 0$ | curar dá satisfação, decrescente porque a triagem prioriza o caso grave |

</div>

<div class="callout mt-s">

O custo marginal $c'(q) = C' - \alpha B'$ tem **sinal incerto**, mas $c'' \gg 0$: a curva é um **U**.

</div>

---

<Rastreio cont="2 de 2">3. Literatura teórica · 3 de 3</Rastreio>

# Abrindo o custo, parte 2: o trabalho

<div class="sm tight">

Há uma zona em que atender mais **reduz** o custo líquido, um mínimo, e uma zona de exaustão.

</div>

<Fig src="/fig/curva_custo_laboral_burnout.png" alt="Custo laboral líquido em função do volume de atendimentos" h="fill" class="fill" />

<div class="cols cols-2 mt-s">

<div class="card">
<span class="card-lbl">Reduzem o cansaço — já em Choné &amp; Ma</span>

$$\frac{\partial C}{\partial K} < 0$$

</div>

<div class="card">
<span class="card-lbl">Ampliam o benefício — extensão deste projeto, via Reinhardt</span>

$$\frac{\partial B}{\partial K} > 0$$

</div>

</div>

<Fonte rotulo="Figura">Ilustração conceitual do modelo de Choné &amp; Ma (2011); não é estimação nem dado observado. Por dois caminhos, $\partial c^{\text{laboral}}/\partial K < 0$.</Fonte>

---

<Rastreio cont="1 de 2">4. Modelo microeconômico · 1 de 3</Rastreio>

# Como juntamos os três

<div class="sm tight">

A estrutura vem de Moehling et al.; o custo, que neles era caixa-preta, é aberto pelas outras duas.

</div>

<div class="eq eq-lg" style="margin-top:0.2rem">

$$V_{im} = \sum_t \delta^t \left[ \frac{\mathbb{E}(w_{imt} \mid B_m)}{p_{mt}} - c_{im} \right] + \varepsilon_{im}$$

</div>

<div class="eq">

$$c_{im} = \underbrace{\phi(\text{dist}_{im}) - \gamma A_m + \theta_i^{\text{rural}}}_{\text{Redding \& Rossi-Hansberg}} + \underbrace{C(q; L_m, K_m) - \alpha_i B(q; L_m, K_m)}_{\text{Choné \& Ma, com a extensão em } B}$$

</div>

<div class="tbl-sinal mt-s fill fill-tbl">

| De onde vem | O que entrega |
|---|---|
| **Moehling et al. (2020)** | o $\arg\max$ intertemporal, o deflator $p_{mt}$ e a existência de $c$ |
| **Redding &amp; Rossi-Hansberg (2017)** | distância, amenidades e custo de moradia dentro de $c$ |
| **Choné &amp; Ma (2011)**, com Reinhardt | esforço, altruísmo e o papel de $L$ e $K$ dentro de $c$ |

</div>

---

<Rastreio cont="2 de 2">4. Modelo microeconômico · 1 de 3</Rastreio>

# Como juntamos os três

<div class="card mt-s">
<span class="card-lbl">A decisão</span>

A alternativa $m = 0$ é **ficar fora do programa**. A vaga em $m$ é aceita quando $V_{im} \geq V_{i0}$ e $m$ é a melhor entre as disponíveis. O termo $\varepsilon_{im}$ recolhe os gostos que não observamos.

</div>

<div class="callout mt-m">

Nenhuma das três trata de um componente da remuneração **fixado por regra pública sobre um índice territorial**. É isso, e só isso, que a adaptação ao PMM-E acrescenta.

</div>

<p class="sm" style="margin-top:1.4rem">É o que as duas páginas seguintes desenvolvem.</p>

---

<Rastreio cont="1 de 2">4. Modelo microeconômico · 2 de 3</Rastreio>

# O que a bolsa paga — e o que não paga

<p class="lead tight">A remuneração tem duas partes: a <strong>bolsa</strong>, que a regra fixa, e o que o médico obtém no <strong>mercado local</strong> fora das 20 horas do programa:</p>

<div class="eq eq-lg mt-s">

$$\mathbb{E}(w_{imt} \mid B_m) = B_m + w^{\text{priv}}_m$$

</div>

<div class="mt-s">

| Onde | Mercado privado | Remuneração |
|---|---|---|
| **Capital ou região metropolitana** | consultório, planos de saúde, hospitais privados | $w = B + w^{\text{priv}}$, com $w^{\text{priv}}$ alto |
| **Interior isolado** | sem demanda privada que sustente a especialidade | $w \to B$ |

</div>

---

<Rastreio cont="2 de 2">4. Modelo microeconômico · 2 de 3</Rastreio>

# O que a bolsa paga — e o que não paga

<div class="stack" style="margin-top:0.2rem">

<div class="card">
<span class="card-lbl">Primeiro</span>

A bolsa maior do interior pode significar **remuneração total menor**: R$ 20 mil sem complemento contra R$ 10 mil mais o consultório da capital. Para compensar, $B$ precisa cobrir também a **renda privada que o médico deixa de ganhar**.

</div>

<div class="card">
<span class="card-lbl">Segundo</span>

Onde $w^{\text{priv}} \approx 0$ a bolsa é **toda** a remuneração — e é exatamente ali que a política mais aposta nela.

</div>

<div class="callout-soft">

O deflator $p_{mt}$ trabalha no **sentido oposto**: o custo de vida é menor no interior, o que valoriza a mesma bolsa em termos reais.

</div>

</div>

---

<Rastreio cont="1 de 2">4. Modelo microeconômico · 3 de 3</Rastreio>

# O IVS organiza o custo

<p class="lead tight">Distância da família, aluguel e esforço clínico <strong>não são observados</strong>. O que se observa, para todo município, é o <strong>IVS</strong>. Escrevemos então o custo como função do índice mais um desvio individual:</p>

<div class="eq eq-lg mt-s">

$$c_{im} = c_0(IVS_m) + \eta_i$$

</div>

<p class="sm tight">Isso não é atalho: <strong>cada dimensão do IVS corresponde a um bloco do custo</strong>.</p>

<div class="tbl-tight tbl-center mt-s fill fill-tbl">

| Dimensão do IVS | Indicadores | Bloco do custo | Efeito sobre $c$ |
|---|---|---|---|
| Infraestrutura urbana | saneamento, lixo, tempo de deslocamento | amenidades $A_m$ | $\uparrow$ |
| Renda e trabalho | pobreza, desemprego, informalidade | mercado privado ausente, $w \to B$ | $\uparrow$ |
| Capital humano | mortalidade infantil, analfabetismo, mães adolescentes | gravidade do caso, $B'(q)\uparrow$; e escassez de equipe e capital, $K\downarrow$ | **ambíguo** |

</div>

---

<Rastreio cont="2 de 2">4. Modelo microeconômico · 3 de 3</Rastreio>

# O IVS organiza o custo

<p class="lead tight">A terceira linha é o que impede assumir que o custo cresce com o índice.</p>

<div class="cols cols-2 mt-s">

<div class="card">
<span class="card-lbl">Carência sanitária eleva o benefício de atender</span>

o que **reduz** o custo para um médico altruísta

</div>

<div class="card">
<span class="card-lbl">…ao mesmo tempo em que sinaliza falta de insumos</span>

o que **eleva** o cansaço

</div>

</div>

<div class="eq eq-lg mt-m">

$$c_0'(IVS) \gtrless 0$$

</div>

<p class="sm">O sinal é <strong>questão empírica</strong>.</p>

<div class="callout mt-s">

É por isso que o objeto do trabalho é o **degrau** da bolsa entre faixas, e não a inclinação do índice.

</div>

---

<Rastreio cont="1 de 2">5. Hipótese</Rastreio>

# A hipótese

<div style="margin-top:0.2rem">
<span class="passo-lbl">Passo 1 · a condição de aceitação</span>

<div class="sm tight">

O médico $i$ aceita a vaga em $m$ quando o que ela vale supera sua melhor alternativa $\bar{v}_i$:

</div>

<div class="eq eq-lg eq-tall mt-s">

$$\frac{B_m + w^{\text{priv}}_m}{p_m} - c_0(IVS_m) \geq \bar{v}_i$$

</div>
</div>

<div class="mt-m">
<span class="passo-lbl">Passo 2 · do médico à vaga</span>

<div class="callout">

A vaga é preenchida se **existir ao menos um candidato** para quem a desigualdade vale. Tudo o que aumenta o lado esquerdo aumenta essa probabilidade.

</div>
</div>

---

<Rastreio cont="2 de 2">5. Hipótese</Rastreio>

# A hipótese

<div style="margin-top:0.1rem">
<span class="passo-lbl">Passo 3 · a hipótese — o trabalho testa uma só</span>
</div>

<div class="stack gap-s">

<div class="hip">
  <span class="hip-tag">H1</span>
  <div class="hip-txt">

Maior **remuneração real** aumenta a probabilidade de preenchimento da vaga.

  </div>
  <div class="hip-eq">

$$\dfrac{\partial \Pr(\text{preenchimento}_m)}{\partial (B_m / p_m)} > 0$$

  </div>
</div>


</div>

<div class="gap-m">
<span class="passo-lbl">Passo 4 · o custo é obstáculo, não hipótese</span>

<p class="sm">O custo locacional não entra como segunda hipótese porque não varia livremente: a regra do edital o amarra à bolsa, e os dois sobem juntos. Na fronteira entre duas faixas, o preenchimento do lado mais vulnerável exige que o <strong>degrau monetário supere o degrau de custo</strong>:</p>

<div class="eq eq-lg">

$$\frac{\Delta B_m}{p_m} > \Delta c_0, \qquad \Delta B_m = \text{R\$ } 5.000$$

</div>
</div>

<div class="callout gap-s">

A pergunta da apresentação é **se essa desigualdade vale**.

</div>

---

<Rastreio cont="1 de 2">6. Viabilidade empírica</Rastreio>

# Viabilidade empírica

<p class="lead tight"><strong>Temos como medir cada peça do modelo?</strong></p>

<div class="tbl-tight mt-s fill fill-tbl">

| Peça do modelo | O que observamos | Fonte |
|---|---|---|
| Preenchimento da vaga | se a vaga teve alguém confirmado ou homologado | quadro de vagas e resultados do ciclo 1: 1.295 vagas em 368 municípios |
| Bolsa $B_m$ | o valor anunciado na vaga: R$ 10, 15 ou 20 mil | edital |
| Custo $c_m$ | o IVS e suas três dimensões; se o município é capital, metropolitano, polo do interior ou interior remoto; quantos especialistas e que estrutura já havia | Ipea; REGIC 2018 e RMs 2022 (IBGE); CNES mensal, jun/2024 a jul/2026 |
| Custo de vida $p_m$ | diferenças entre estados | IBGE |
| Mercado local $w^{\text{priv}}_m$ | — | **não observado** |
| Distância da família | — | **não observado** |

</div>

---
class: centrado bloco-lg
---

<Rastreio cont="2 de 2">6. Viabilidade empírica</Rastreio>

# Viabilidade empírica

<div class="callout" style="margin-top:0.3rem">

**Sim, para o essencial.** Duas peças ficam de fora — a renda no mercado privado local e a distância da família — e entram no modelo como parte do custo que o IVS e a tipologia territorial resumem.

</div>

<div class="card mt-m">
<span class="card-lbl">A dificuldade</span>

Recuperar a regra que o Ministério aplicou era o primeiro passo. **Ele foi dado.** Há suporte comum: **37** municípios com IVS ≤ 0,400 estão na Faixa 1 e **94** na Faixa 2.

Mas o tratamento é **localmente constante nos dois cortes** — em 0,500 os dois lados são 100% Faixa 1; em 0,400 não há Faixa 3 por perto. E a variação que sobra está alinhada com remoticidade, o previsor mais forte do desfecho.

</div>

<div class="callout-soft mt-m">

**O efeito do *valor da bolsa* não é identificável com fonte pública: falta o Anexo IV. O desenho do trabalho não depende dele — usa a descontinuidade no escore de seleção do candidato.**

</div>
