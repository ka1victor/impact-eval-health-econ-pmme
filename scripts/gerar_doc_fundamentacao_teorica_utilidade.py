# -*- coding: utf-8 -*-
"""Gera o memo canônico sobre utilidade, regressores e hipóteses do PMM-E."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_MD = ROOT / "docs" / "17_fundamentacao_teorica_formacao_utilidade_regressores.md"


DOC = r"""# 17. Formação da utilidade médica, regressores e hipóteses

> **Projeto:** avaliação de impacto do Programa Mais Médicos Especialistas (PMM-E)
>
> **Objeto:** escolha de uma oferta de trabalho/formação e permanência no município
>
> **Status:** memo teórico canônico para orientar hipóteses e especificações; não constitui, por si só, identificação estrutural
>
> **Data de consolidação:** 31 de agosto de 2026

## 1. Resultado central

O objeto teórico relevante não é o efeito isolado de “salário” ou de “IVS”, mas a utilidade que o médico deriva de um **pacote de trabalho, formação e localização**. Esse pacote reúne:

1. consumo possibilitado pela bolsa e por outras rendas;
2. carga, pressão, imprevisibilidade e risco do trabalho;
3. infraestrutura clínica, equipe e rede de referência;
4. formação, mentoria, certificação, autonomia e carreira;
5. propósito e alinhamento com a missão assistencial;
6. amenidades locais e oportunidades para a família;
7. vínculos territoriais, distância e custos de mudança;
8. a opção externa de não aderir ou trabalhar em outro local.

A hierarquia de fundamentação adotada neste memo é deliberada. O núcleo vem de dois **modelos microeconômicos publicados**: a escolha locacional intertemporal de um médico em Moehling et al. (2020) e o modelo de esforço e matching por missão de Besley e Ghatak (2005). Roback (1982) fornece a base de equilíbrio espacial. McFadden (1974), Costa, Nunes e Sanches (2024) e os experimentos de escolha entram depois, na passagem para mensuração e estimação; suas especificações econométricas não são apresentadas como teoria da utilidade.

No PMM-E, o pagamento deve ser tratado como **bolsa-formação**, e não automaticamente como “salário municipal + bônus”. A documentação oficial descreve bolsa de R$ 10 mil, R$ 15 mil ou R$ 20 mil conforme a faixa de IVS, 20 horas semanais de atividades e ausência de vínculo empregatício. O programa também oferece mentoria, imersões e certificação. Portanto, renda corrente, custo de oportunidade do tempo e valor futuro da formação são componentes distintos da utilidade.

A decomposição também é coerente com evidência brasileira. Um experimento de escolha discreta em Minas Gerais incluiu localização, remuneração, vínculo, jornada, acesso à residência e condições de trabalho. Entrevistas nas “rotas da escassez” destacaram remuneração, flexibilidade, infraestrutura da unidade, origem do profissional, infraestrutura urbana e lazer. Esses resultados apoiam a inclusão dos argumentos, mas não fixam seus coeficientes no PMM-E.

## 2. Equação 1 — escolha locacional de um médico no modelo publicado

O ponto de partida canônico será a Equação (1) de **Moehling, Niemesh, Thomasson e Treber (2020)**. Os autores apresentam explicitamente um problema microeconômico de escolha locacional do médico antes de introduzir qualquer modelo econométrico:

$$
\arg\max_{i\in\mathcal I} U(\omega_i)
=
\arg\max_{i\in\mathcal I}
\left\{
\sum_t \delta^t
\left[
\frac{\mathbb E\!\left(w^{(s)}_{it}\right)}{p_{it}}
-c^{(s)}_{it}
\right]
\right\}.
\tag{1; Moehling et al., 2020}
$$

Esta é a equação do próprio paper, com sua notação preservada. O médico escolhe a localidade $i$ que maximiza o valor presente da remuneração real esperada menos os custos e desamenidades de consumo da localidade. No artigo, $t$ indexa o ano, $s$ o grupo de qualificação, $w$ a remuneração nominal esperada, $p$ o nível de preços local, $c$ as amenidades ou desamenidades e custos locais, e $\delta$ o fator de desconto.

Os autores incluem em $c$ a preferência por vida rural ou urbana, proximidade da família e outros atributos locacionais. Hospitais, laboratórios, tamanho do mercado, estradas, proximidade de outros profissionais e escola médica são tratados como **amenidades produtivas**: elas podem elevar a remuneração esperada. A equação, portanto, separa duas vias pelas quais uma localidade afeta a escolha: qualidade de vida/custos de um lado e produtividade/retorno profissional do outro.

### 2.1 Sinais e forma funcional que vêm da Equação (1)

Defina o valor da localidade por $\Omega_i$, igual ao termo entre chaves. Então, para cada período:

$$
\frac{\partial \Omega_i}{\partial \mathbb E(w^{(s)}_{it})}
=\frac{\delta^t}{p_{it}}>0,
\qquad
\frac{\partial \Omega_i}{\partial p_{it}}
=-\delta^t\frac{\mathbb E(w^{(s)}_{it})}{p_{it}^2}<0,
\qquad
\frac{\partial \Omega_i}{\partial c^{(s)}_{it}}
=-\delta^t<0.
$$

Essas derivadas não são uma nova função proposta para o PMM-E; são implicações algébricas diretas da equação publicada. Elas fundamentam as hipóteses de que remuneração real esperada eleva o valor da opção, custo de vida reduz esse valor e desamenidades locais o reduzem.

Crucialmente, a remuneração entra **linearmente em nível e deflacionada por preços**. O paper não impõe utilidade logarítmica, CRRA ou exponencial. Se o projeto adotar este modelo como fundamento, o benchmark teórico para a bolsa é, portanto, o valor real em nível. Uma transformação logarítmica seria uma hipótese teórica alternativa; uma exponencial não é implicada pelo modelo.

### 2.2 Tradução dos primitivos para o PMM-E

| Primitivo original | Leitura no PMM-E | Conteúdo observável prioritário |
|---|---|---|
| $\mathbb E(w)/p$ | retorno monetário real esperado da opção | bolsa real, outras rendas compatíveis e custo de vida |
| $c$ | custo/desamenidade de morar e trabalhar no local | distância da família, dupla moradia, segurança, escolas, lazer e conectividade |
| amenidades produtivas em $\mathbb E(w)$ | capacidade de exercer a especialidade e produzir capital profissional | hospitais, laboratórios, equipamentos, equipe, referência, mentoria e rede profissional |
| $\delta$ | valor presente de retornos atuais e futuros | duração da formação e retorno futuro esperado da certificação |
| heterogeneidade em $s$ | atributos têm valores distintos por tipo de médico | especialidade, estágio de carreira e vínculo territorial prévio |

O IVS não aparece como um bem ou mal primitivo na Equação (1). Ele pode elevar a bolsa, sinalizar maior necessidade assistencial e, simultaneamente, correlacionar-se com preços, amenidades, infraestrutura e pressão de trabalho. Por isso, o sinal total do IVS sobre a utilidade permanece teoricamente ambíguo. O IVS 2010 continua sendo a **running variable canônica** do projeto; essa decomposição serve para interpretar mecanismos, não para substituí-lo por IDHM ou PIB per capita.

## 3. Equação 2 — salário, esforço e propósito em um modelo de missão

A Equação (1) de Moehling et al. acomoda amenidades locacionais, mas não abre a caixa de esforço e propósito. Para esses mecanismos, o complemento teórico vem do modelo principal–agente de **Besley e Ghatak (2005)**. No modelo publicado, um agente do tipo $j$ trabalha para uma organização/principal do tipo $i$; o sucesso do projeto ocorre com probabilidade igual ao esforço $e_{ij}$. As utilidades originais são:

$$
u^p_{ij}=(\pi_i-b_{ij})e_{ij}-w_{ij},
\qquad
u^a_{ij}=e_{ij}(b_{ij}+\theta_{ij})+w_{ij}-\frac{1}{2}e_{ij}^{2}.
\tag{2; Besley e Ghatak, 2005}
$$

$w_{ij}$ é o pagamento fixo, $b_{ij}$ o bônus pago em caso de sucesso, $\pi_i$ o valor do sucesso para a organização e $\theta_{ij}$ o benefício não pecuniário que o agente recebe quando o projeto tem sucesso. Esse último termo é o **matching de missão**: ele é maior quando a missão da organização coincide com aquilo que motiva o trabalhador.

A compatibilidade de incentivos do modelo produz:

$$
e^*_{ij}
=\arg\max_{e\in[0,1]}
\left\{e(b_{ij}+\theta_{ij})+w_{ij}-\frac12e^2\right\}
=b_{ij}+\theta_{ij},
\tag{3; Besley e Ghatak, 2005}
$$

para a solução interior considerada pelos autores. Três hipóteses saem diretamente desse bloco teórico:

1. **Pagamento fixo eleva utilidade:** $\partial u^a/\partial w=1$ no modelo, portanto a forma é linear.
2. **Esforço tem custo convexo:** o termo $-e^2/2$ implica $\partial^2u^a/\partial e^2=-1$.
3. **Propósito depende de matching e de resultado:** o ganho de missão é $e\theta$, não uma constante positiva atribuída a qualquer local vulnerável. Maior $\theta$ eleva tanto a utilidade associada ao sucesso quanto o esforço ótimo.

O artigo menciona expressamente médicos comprometidos com salvar vidas como exemplo de agente motivado. Entretanto, ele não diz que todos os médicos valorizam igualmente toda missão pública. Para o PMM-E, $\theta_{ij}$ exige uma medida prévia de orientação do médico e uma medida da missão/necessidade da opção. Usar apenas IVS alto como sinônimo de propósito apagaria o mecanismo de matching do paper.

Também é necessário preservar a interpretação original de $e$: ele é esforço **escolhido** e aumenta a probabilidade de sucesso. Carga assistencial imposta, plantões e falta de equipe não são literalmente $e$. Utilizar o custo quadrático como motivação para uma hipótese de desutilidade convexa da carga é uma extensão disciplinada pelo modelo, mas deve ser rotulada como tal.

## 4. O que os modelos publicados autorizam sobre formas funcionais

| Componente | Forma no paper teórico | Sinal/curvatura autorizados | Decisão para o PMM-E |
|---|---|---|---|
| Remuneração locacional | $\mathbb E(w)/p$ em Moehling et al. | positiva e linear no valor real | benchmark em nível real; faixas da bolsa preservadas no desenho causal |
| Pagamento fixo | $+w$ em Besley–Ghatak | positivo e linear | não impor log ou exponencial como especificação principal |
| Custo de vida | remuneração dividida por $p$ | negativo | deflacionar quando houver índice defensável; aluguel pode entrar separadamente |
| Desamenidades | $-c$ em Moehling et al. | negativas e aditivas; curvatura não fixada | distância, família, segurança, escola e lazer em bloco separado |
| Esforço | $-e^2/2$ em Besley–Ghatak | custo marginal crescente | hipótese quadrática para esforço; carga observada requer ponte conceitual explícita |
| Missão | $+e\theta$ em Besley–Ghatak | positiva quando há matching; complementar ao sucesso | medir tipo pró-social antes da escolha e interagir com missão/necessidade da vaga |
| Formação futura | soma descontada $\sum_t\delta^t[\cdot]$ | retornos futuros valem menos quando mais distantes | tratar certificação/mentoria como alteração do fluxo futuro esperado, não como renda corrente |

### 4.1 Linear, logarítmica ou exponencial para renda?

A escolha canônica deste memo passa a ser **linear em remuneração real**, porque essa é a forma das equações teóricas publicadas selecionadas, e não apenas porque o sinal positivo seja intuitivo. Nesses modelos, a utilidade marginal do pagamento é constante. Logo, eles não autorizam afirmar, a priori, retorno marginal decrescente da bolsa.

Uma função logarítmica ou CRRA poderia ser adotada por outro modelo de consumo côncavo, mas isso seria uma mudança de fundamento teórico e deve vir acompanhada da citação do modelo escolhido. A função exponencial do tipo CARA, $-\exp(-aw)$, é uma representação de preferência sob risco com aversão absoluta constante; ela não aparece nos modelos selecionados de escolha locacional médica ou missão.

Portanto:

- **modelo teórico principal:** bolsa/remuneração real em nível;
- **não impor:** retorno marginal decrescente da renda sem trocar ou ampliar o modelo teórico;
- **não usar:** utilidade exponencial da renda como escolha automática;
- **não confundir:** a exponencial que aparece em probabilidades logit pertence ao mecanismo probabilístico de escolha, não à utilidade monetária do trabalhador.

Como checagem de coerência mais geral, Roback (1982) parte do problema microeconômico $\max U(x,l^c;s)$ sujeito a $w+I=x+rl^c$: salário expande o orçamento, aluguel o reduz e a amenidade $s$ entra diretamente na utilidade. Roback não escolhe entre linear, log ou exponencial; logo, seu modelo fundamenta os **argumentos** da utilidade e a necessidade de considerar custo de moradia, mas não deve ser citado como fundamento de uma curvatura específica.

## 5. Hipóteses estruturais e sinais esperados

| Hipótese | Predição para escolha/atração | Predição para saída | Restrição ou ressalva |
|---|---:|---:|---|
| H1. Bolsa/renda real | $+$ e linear no modelo selecionado | $-$ enquanto vigente | O modelo não impõe utilidade marginal decrescente; bolsa é função administrativa do IVS |
| H2. Carga, plantão e imprevisibilidade | $-$; convexidade é uma extensão do custo quadrático do esforço | $+$ | Esforço escolhido em Besley–Ghatak não é idêntico a carga imposta |
| H3. Infraestrutura, equipe e referência | $+$ como amenidade produtiva | $-$ | Heterogeneidade por especialidade é hipótese adicional |
| H4. Autonomia e flexibilidade | $+$ | $-$ | Podem compensar parcialmente ausência de vínculo |
| H5. Formação, mentoria e certificação | $+$ se elevar o fluxo futuro esperado | $-$ durante o curso | Entra pela soma descontada; heterogeneidade por carreira é hipótese empírica |
| H6. Amenidades, segurança e conectividade | $+$ | $-$ | Custo de moradia entra separadamente no consumo real |
| H7. Distância e separação familiar | $-$ | $+$ | Mesma região de residência/origem/formação deve elevar utilidade |
| H8. Missão da vaga $\times$ orientação pró-social | $+$ quando elevar $\theta_{ij}$ | $-$ | Necessidade/IVS isolados não medem matching; efeito médio do IVS permanece ambíguo |
| H9. Densidade de pares | ambígua/não linear | ambígua | Suporte e aprendizado versus competição |
| H10. Duração | dependência de estado positiva ou burnout | não monotônica | Exige dados longitudinais além do cumprimento contratual |

Não há fundamento geral para impor $\beta_{Bolsa\times IVS}>0$. Em uma utilidade aditiva, a bolsa pode compensar uma desamenidade sem qualquer interação. Uma interação positiva exigiria a hipótese adicional de que a utilidade marginal da bolsa cresce com o IVS. Como a bolsa é mecanicamente definida por faixas de IVS, uma regressão global com ambos não separa seus efeitos causais.

## 6. Tradução para as especificações do projeto

As equações desta seção são implementações econométricas e **não** a fundamentação microeconômica. A teoria do memo está nas Equações (1)–(3), transcritas dos papers; esta seção apenas mostra como seus primitivos orientam variáveis e desenhos empíricos.

### 6.1 Atração e preenchimento com os dados atuais

Para município $m$, especialidade/curso $s$ e chamada $c$:

$$
Filled_{msc}\mid Vacancies_{msc}\sim Binomial(Vacancies_{msc},p_{msc}),
$$

$$
logit(p_{msc})=
\alpha_s+\lambda_c+\mu_{UF}
+f(IVS_{m,2010})
+\beta_1\ln Pop_m
+\beta_2Stock^{pre}_{ms}
+\beta_3K^{pre}_{ms}
+\beta_4Access_m
+\beta_5Amenities_m
+\beta_6OfferSize_{msc}.
$$

Esse modelo é reduzido/associativo. Seus coeficientes não são pesos cardinais de utilidade. Recomenda-se:

- uma especificação de gradiente total com IVS 2010, população, oferta e efeitos fixos;
- blocos sequenciais de infraestrutura, acesso e amenidades para descrever mecanismos;
- erros agrupados no município;
- variáveis basais, medidas antes da oferta;
- nenhuma interpretação causal automática para controles correlacionados com a regra da bolsa.

Não controlar por carga, estoque médico ou infraestrutura pós-programa ao estimar o efeito total: essas variáveis podem ser mediadoras.

### 6.2 Efeito causal da bolsa nos cortes do IVS

Se a regra e o IVS administrativo forem validados, a especificação local é:

$$
Y_m=\alpha+\tau\mathbf{1}(R_m\ge c)
+\beta_1(R_m-c)
+\beta_2\mathbf{1}(R_m\ge c)(R_m-c)
+\alpha_s+\lambda_c+\varepsilon_m.
$$

$\tau$ representa o efeito local do salto de bolsa somente se não houver outra regra ou mudança de composição descontínua no mesmo corte. Covariáveis prévias servem para precisão e diagnóstico de balanço; não substituem a validação institucional.

### 6.3 Escolha individual quando houver microdados

O modelo adequado é conditional logit, rank-ordered logit ou mixed logit com:

- conjunto completo de opções elegíveis e visíveis em cada instante;
- opção externa de não participar;
- atributos de cada oferta;
- indicadores derivados de mesma UF/região de residência, nascimento e formação;
- distância ou tempo de viagem entre origem e oferta;
- heterogeneidade por especialidade e estágio de carreira;
- capacidade da vaga e regras de alocação separadas da preferência.

Coerentemente com Moehling et al. e Besley–Ghatak, a remuneração real em nível deve ser a forma principal. Log da remuneração pode ser apresentado como robustez associada a um modelo alternativo de utilidade côncava; forma exponencial não deve ser incluída sem fundamento teórico adicional.

Sem o conjunto de alternativas, observam-se apenas opções escolhidas, não escolhas frente a oportunidades reais. Sem não candidatos, identifica-se no máximo a localização condicional à candidatura, e não a margem extensiva de participar.

Em conditional logit, atributos que variam apenas entre médicos cancelam na comparação entre opções. Idade, estágio de carreira ou experiência prévia devem interagir com atributos da vaga/localidade ou com a constante da opção externa; não entram isoladamente como determinantes da escolha entre municípios.

### 6.4 Retenção

Com eventos individuais e ponte pseudonimizada, usar um hazard em tempo discreto com dummies de duração. Bolsa recebida, atraso de pagamento, carga e infraestrutura realizadas podem ser usados para mecanismos, desde que se reconheça sua natureza potencialmente pós-tratamento. Participação por 12 meses mede conclusão do programa; não é sinônimo de fixação municipal duradoura.

## 7. Prioridade dos regressores e dados

### Disponíveis ou próximos do núcleo atual

- IVS 2010 total como running variable canônica;
- dimensões do IVS para descrição, sem substituir o índice total;
- população, UF e região de saúde;
- vagas, preenchimento, curso e chamada;
- estoque basal de médicos/especialistas;
- número e tipo de estabelecimentos proponentes.

### Construir a partir do CNES pré-tratamento

- equipamentos e serviços específicos da especialidade;
- leitos relevantes;
- composição e tamanho da equipe;
- capacidade diagnóstica e cirúrgica;
- referência/contrarreferência disponível;
- horas e vínculos basais.

### Adquirir externamente

- tempo rodoviário até polo regional, capital e aeroporto;
- segurança, escolas, internet, transporte e lazer;
- aluguel ou custo de vida;
- cobertura de planos e oportunidade de mercado privado.

Esses atributos podem entrar como controles ou mecanismos, mas não substituem o IVS 2010 sem justificativa econométrica explícita e autorização do autor.

### Solicitar nos microdados administrativos

- universo de opções elegíveis/visíveis, com timestamp e disponibilidade;
- alternativa externa ou registro dos não aderentes, quando legalmente possível;
- mesma UF/região de residência, nascimento e formação;
- faixa de distância até cada opção;
- tempo desde a especialização e experiência prévia no SUS;
- nota/classificação e regra de alocação;
- início, interrupção, conclusão e motivo de saída;
- bolsa devida, paga e data de pagamento.

Por LGPD, preferir indicadores derivados pelo controlador, como `mesma_uf_residencia_opcao` e `faixa_distancia_residencia_opcao`, a endereços ou municípios de residência brutos.

### Medir por survey/DCE ou tratar como heterogeneidade não observada

- orientação por missão;
- preferências por jornada e risco;
- emprego do cônjuge e necessidades escolares dos filhos;
- burnout e apoio social;
- preferências de lazer.

Não construir “vocação” a partir da própria escolha de um município vulnerável: isso seria uma medida pós-escolha e mecanicamente endógena.

## 8. O que pode e o que não pode ser chamado de peso de utilidade

A teoria determina argumentos, sinais locais e algumas curvaturas; não determina a fração da utilidade proveniente de renda, propósito ou lazer. Utilidade é ordinal, e a escala dos coeficientes em modelos de escolha é normalizada pela variância do erro.

Com escolhas individuais e variação identificada, podem ser reportados:

- efeitos marginais sobre probabilidades;
- elasticidades de escolha;
- WTA em reais para uma desamenidade;
- distribuição de preferências em mixed logit;
- heterogeneidade de WTA por especialidade ou vínculo territorial.

Razões como $-\beta_x/\beta_B$ têm interpretação monetária somente quando o atributo de renda está adequadamente identificado e na mesma função de utilidade. Coeficientes de uma regressão agregada de preenchimento não devem ser convertidos diretamente em WTA.

## 9. Referências essenciais e uso correto

### Modelos microeconômicos que geram as equações do memo

- **Moehling, C. M.; Niemesh, G. T.; Thomasson, M. A.; Treber, J. (2020).** [*Medical Education Reforms and the Origins of the Rural Physician Shortage*](https://doi.org/10.1007/s11698-019-00187-w) ([manuscrito dos autores com a Equação 1](https://niemesgt.github.io/files/MoehlingNiemeshThomassonTreber2019.pdf)). Fornece o problema intertemporal de escolha locacional do médico usado na Equação (1): remuneração real esperada menos custos/desamenidades locais.
- **Besley, T.; Ghatak, M. (2005).** [*Competition and Incentives with Motivated Agents*](https://doi.org/10.1257/0002828054201413) ([PDF dos autores](https://personal.lse.ac.uk/ghatak/motivated.pdf)). Fornece as utilidades e a restrição de incentivos reproduzidas nas Equações (2)–(3): pagamento fixo, bônus, matching de missão e custo quadrático do esforço.
- **Roback, J. (1982).** [*Wages, Rents, and the Quality of Life*](https://doi.org/10.1086/261120) ([PDF](https://www.nathanschiff.com/webdocs/grad_urban/urban_papers/Roback_JPE_1982.pdf)). Fornece a microfundamentação espacial de consumo, terra/moradia e amenidades e o equilíbrio de salários e aluguéis. Não fixa uma curvatura específica para renda.
- **Becker, G. S. (1965).** [*A Theory of the Allocation of Time*](https://doi.org/10.2307/2228949). Fundamenta o custo de oportunidade do tempo e a escolha entre trabalho, consumo e demais usos do tempo.
- **Glaeser, E. L.; Kolko, J.; Saiz, A. (2001).** [*Consumer City*](https://doi.org/10.1093/jeg/1.1.27). Fundamenta a entrada de lazer, serviços e outras amenidades locais na escolha residencial.
- **Kennan, J.; Walker, J. R. (2011).** [*The Effect of Expected Income on Individual Migration Decisions*](https://doi.org/10.3982/ECTA4657). Extensão para decisão dinâmica, custos de mudança e repetição de escolhas locacionais; não é a equação principal deste memo.

### Modelagem e evidência empírica para a passagem aos dados

- **McFadden, D. (1974).** [*Conditional Logit Analysis of Qualitative Choice Behavior*](https://eml.berkeley.edu/reprints/mcfadden/zarembka.pdf). Base para estimar escolhas discretas; não é usado como a equação microeconômica substantiva do trabalho médico.
- **Costa, F.; Nunes, L.; Sanches, F. M. (2024).** [*How to Attract Physicians to Underserved Areas? Policy Recommendations from a Structural Model*](https://doi.org/10.1162/rest_a_01155). Evidência brasileira de preferências por salário real, amenidades, infraestrutura e vínculos de nascimento/formação.
- **Scott, A. (2001).** [*Eliciting GPs' Preferences for Pecuniary and Non-Pecuniary Job Characteristics*](https://doi.org/10.1016/S0167-6296(00)00083-7). Mostra como características não pecuniárias do trabalho entram na escolha médica e na WTA.
- **Scott, A. et al. (2013).** [*Getting Doctors into the Bush*](https://doi.org/10.1016/j.socscimed.2013.05.002). Mostra que pacotes de trabalho e características da localidade importam conjuntamente.
- **Sivey, P. et al. (2012).** [*Junior Doctors' Preferences for Specialty Choice*](https://doi.org/10.1016/j.jhealeco.2012.07.001). Útil para renda, horas, plantões, controle de jornada e oportunidades acadêmicas; trata de escolha de especialidade, não de localização rural.
- **Mandeville, K. L.; Lagarde, M.; Hanson, K. (2014).** [*The Use of Discrete Choice Experiments to Inform Health Workforce Policy*](https://doi.org/10.1186/1472-6963-14-367). Fundamenta DCE, heterogeneidade e necessidade de opção externa realista.
- **Van Stralen, A. C. S. et al. (2017).** [*Percepção de médicos sobre fatores de atração e fixação em áreas remotas e desassistidas: rotas da escassez*](https://doi.org/10.1590/S0103-73312017000100008). Evidência brasileira sobre remuneração, trabalho, fatores profissionais, locais e pessoais.
- **Experimento de escolha discreta em Minas Gerais (2017).** [*Preferências para o trabalho na atenção primária por estudantes de medicina*](https://www.scielo.br/j/csp/a/cN9kwNtpg5z3M6hRczVTjFS/?lang=pt). Evidência brasileira sobre localização, condições de trabalho, remuneração, formação, vínculo e jornada.
- **WHO (2021).** [*WHO Guideline on Health Workforce Development, Attraction, Recruitment and Retention in Rural and Remote Areas*](https://www.who.int/publications/i/item/9789240024229). Recomenda pacotes financeiros e não financeiros, reconhecendo baixa certeza em parte da evidência.
- **Brasil, Ministério da Saúde.** [FAQ do Chamamento Público SGTES/MS nº 3/2025](https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2025/chamamento-publico-sgtes-ms-no-3-2025-projeto-mais-medicos-especialistas/faq).
- **Brasil, Ministério da Saúde.** [Projeto Mais Médicos Especialistas](https://www.gov.br/saude/pt-br/composicao/sgtes/mais-medicos/especialistas/especialistas).

## 10. Decisões de modelagem consolidadas

1. Usar Moehling et al. (2020), e não uma função criada para o projeto, como equação canônica da escolha locacional do médico.
2. Usar Besley e Ghatak (2005) como fundamento de esforço, custo quadrático e matching por missão.
3. Adotar remuneração real em nível como forma principal; não impor log/CRRA nem exponencial sem mudar explicitamente o modelo teórico.
4. Não afirmar retorno marginal decrescente da bolsa a partir dos modelos selecionados.
5. Tratar convexidade da carga observada como extensão do custo de esforço, não como identidade literal.
6. Não impor sinal negativo ao IVS nem interação positiva `Bolsa × IVS`.
7. Manter IVS 2010 do IPEA como running variable canônica.
8. Separar renda corrente de retornos futuros de formação e certificação na soma descontada.
9. Incluir opção externa e conjunto real de alternativas em futuros modelos individuais; separar atração, alocação e retenção.
10. Medir orientação por missão antes da escolha; não construir “vocação” a partir da escolha observada.
"""


def main() -> None:
    OUT_MD.write_text(DOC.rstrip() + "\n", encoding="utf-8")
    print(f"Documento gerado: {OUT_MD}")


if __name__ == "__main__":
    main()
