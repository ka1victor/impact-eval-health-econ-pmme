# 17. Formação da utilidade médica, regressores e hipóteses

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

Essa formulação combina utilidade aleatória e escolha discreta (McFadden, 1974), diferenciais compensatórios e equilíbrio espacial (Roback, 1982), mobilidade dinâmica (Kennan e Walker, 2011), matching por missão (Besley e Ghatak, 2005) e evidências específicas sobre localização de médicos (Scott, 2001; Costa, Nunes e Sanches, 2024).

No PMM-E, o pagamento deve ser tratado como **bolsa-formação**, e não automaticamente como “salário municipal + bônus”. A documentação oficial descreve bolsa de R$ 10 mil, R$ 15 mil ou R$ 20 mil conforme a faixa de IVS, 20 horas semanais de atividades e ausência de vínculo empregatício. O programa também oferece mentoria, imersões e certificação. Portanto, renda corrente, custo de oportunidade do tempo e valor futuro da formação são componentes distintos da utilidade.

A decomposição também é coerente com evidência brasileira. Um experimento de escolha discreta em Minas Gerais incluiu localização, remuneração, vínculo, jornada, acesso à residência e condições de trabalho. Entrevistas nas “rotas da escassez” destacaram remuneração, flexibilidade, infraestrutura da unidade, origem do profissional, infraestrutura urbana e lazer. Esses resultados apoiam a inclusão dos argumentos, mas não fixam seus coeficientes no PMM-E.

## 2. Equação 1 — utilidade de fluxo e formas funcionais

Considere o médico $i$, da especialidade $s$, avaliando o município $m$ no período $t$. Uma forma suficientemente geral, mas disciplinada pela teoria, é:

$$
\begin{aligned}
u_{ismt}={}&
\underbrace{\frac{C_{ismt}^{1-\sigma_i}-1}{1-\sigma_i}}_{\text{consumo real}}
-\underbrace{\frac{\theta_i}{1+\eta_i}
\left[\frac{E_{ismt}}{(1+K_{smt})^{\lambda_{is}}}\right]^{1+\eta_i}}_{\text{custo de esforço}}
+\underbrace{\kappa_{is}\ln(1+K_{smt})}_{\text{condições clínicas}}\\
&+\underbrace{\gamma_iG_{ismt}}_{\text{formação e carreira}}
+\underbrace{\mu_iM_iN_{mt}}_{\text{missão} \times \text{necessidade}}
+\underbrace{a_iA_{mt}}_{\text{amenidades}}
+\underbrace{\rho_iTies_{im}}_{\text{vínculos locais}}
-\underbrace{\phi_iD_{im}^{\nu_i}}_{\text{distância e separação}}
+\varepsilon_{ismt},
\end{aligned}
\tag{1}
$$

Os parâmetros satisfazem $\sigma_i>0$, $\theta_i>0$, $\eta_i>0$, $\lambda_{is}\geq0$, $\kappa_{is}\geq0$, $\gamma_i\geq0$, $\mu_i\geq0$, $a_i\geq0$, $\rho_i\geq0$, $\phi_i>0$ e $\nu_i>0$. A teoria disciplina principalmente sinais e curvaturas; os valores desses parâmetros são objetos empíricos.

em que

$$
C_{ismt}=\frac{Y^{out}_{it}+B_{mt}-Cost_{imt}}{P_{mt}}>0.
$$

Aqui, $B$ é a bolsa; $Y^{out}$ representa outras rendas compatíveis com o programa; $Cost$ inclui deslocamento, dupla moradia e outros custos monetários; e $P$ é um índice de custo de vida. $E$ reúne horas efetivas, demanda, plantões, imprevisibilidade, carga administrativa e risco clínico. $K$ é infraestrutura e suporte específicos da especialidade. $G$ representa formação, mentoria, certificação, autonomia e valor de carreira. $M_i$ é a orientação pró-social do médico e $N_m$ é a necessidade assistencial. $A$ reúne amenidades locais; $Ties$, vínculos de origem, residência ou formação; e $D$, distância ou tempo de viagem.

Quando $\sigma_i=1$, o primeiro termo converge para $\ln C_{ismt}$. A família CRRA impõe utilidade crescente e côncava da renda:

$$
\frac{\partial u}{\partial B}
=\frac{C^{-\sigma_i}}{P}>0,
\qquad
\frac{\partial^2 u}{\partial B^2}
=-\frac{\sigma_i C^{-\sigma_i-1}}{P^2}<0
\quad (\sigma_i>0).
$$

Portanto, a hipótese teórica não é apenas “mais bolsa aumenta utilidade”; ela também prevê **retorno marginal decrescente**. Uma diferença de R$ 5 mil tende a importar relativamente mais quando o consumo disponível inicial é menor.

O termo de esforço impõe custo crescente e convexo:

$$
\frac{\partial u}{\partial E}<0,
\qquad
\frac{\partial^2 u}{\partial E^2}<0,
\qquad
\frac{\partial^2 u}{\partial E\,\partial K}>0.
$$

A última desigualdade formaliza a hipótese de que equipe, equipamentos e retaguarda reduzem a desutilidade marginal da pressão assistencial. Não significa que qualquer item do CNES seja igualmente relevante: $K_{smt}$ deve ser construído de forma específica à especialidade e em período anterior ao tratamento quando usado como covariável basal.

### 2.1 Por que não impor IVS negativo

Se $R_m$ denota o IVS 2010, a derivada total contém mecanismos de sinais opostos:

$$
\frac{du}{dR_m}
=u_B\frac{dB}{dR_m}
+u_N\frac{dN}{dR_m}
+u_A\frac{dA}{dR_m}
+u_E\frac{dE}{dR_m}
+u_K\frac{dK}{dR_m}
+u_D\frac{dD}{dR_m},
$$

com $u_B,u_N,u_A,u_K>0$ e $u_E,u_D<0$ para um médico orientado pela missão.

Em geral, $dN/dR>0$, enquanto amenidades e condições de trabalho podem piorar com a vulnerabilidade. Para médicos com forte orientação por missão, o termo $\mu_iM_i\,dN/dR$ pode compensar parte das desamenidades. Por isso:

$$
\operatorname{sign}\left(\frac{du}{dIVS}\right)
\quad\text{é teoricamente ambíguo.}
$$

O IVS 2010 continua sendo a **running variable canônica** do projeto. Amenidades, infraestrutura e necessidade ajudam a interpretar mecanismos; não autorizam substituir o IVS por IDHM ou PIB per capita.

### 2.2 Disposição a aceitar uma desamenidade

Para qualquer atributo $x$, a compensação monetária marginal que mantém a utilidade constante é:

$$
\frac{dB}{dx}\bigg|_{du=0}=-\frac{u_x}{u_B}.
$$

Com utilidade $u=\alpha\ln C-\gamma d$, em que $d$ é uma desamenidade, a compensação exata para um aumento finito $\Delta d>0$ é:

$$
WTA_B(\Delta d)
=PC\left[\exp\left(\frac{\gamma}{\alpha}\Delta d\right)-1\right]
\approx PC\frac{\gamma}{\alpha}\Delta d
\quad\text{para mudanças pequenas.}
$$

O resultado mantém $P$ fixo e mede a WTA na unidade monetária da bolsa. Assim, uma WTA que cresce exponencialmente para grandes perdas de amenidade pode emergir de **utilidade logarítmica da renda**. Não é necessário postular utilidade exponencial da renda.

## 3. Equação 2 — entrada, permanência e valor futuro da formação

A decisão de entrada é prospectiva. Se o programa dura até $T$, o valor líquido da opção é:

$$
V^{enter}_{ism0}
=-F_{im}
+\mathbb{E}_0\left[\sum_{t=0}^{T}\delta_i^t u_{ismt}\right]
+\delta_i^{T+1}\Gamma_{is,m}
-V^{out}_{is0},
\tag{2}
$$

onde $0<\delta_i\leq1$ é o fator de desconto, $F_{im}$ é o custo inicial de mudança e informação; $\Gamma_{is,m}$ é o valor pós-programa da certificação, da aprendizagem e da rede profissional; e $V^{out}$ é o valor da melhor alternativa externa. O médico se candidata, ranqueia ou aceita a vaga quando esse valor supera o das demais opções disponíveis.

A equação gera quatro previsões dinâmicas:

1. **Custos de mudança pesam mais na entrada.** Depois da mudança, parte de $F_{im}$ é irrecuperável, criando dependência de estado.
2. **Capital local pode crescer com a duração.** Relações com equipe, pacientes e comunidade elevam o custo de saída.
3. **Burnout pode acumular.** Pressão persistente e baixa resolutividade podem reduzir a utilidade ao longo do tempo.
4. **Formação e bolsa têm horizontes diferentes.** A bolsa eleva consumo corrente; mentoria e certificação também alteram $\Gamma$. Uma saída próxima ao fim do curso é hipótese testável, não consequência necessária.

Retenção condicional aos que entraram não mede automaticamente o mesmo efeito da atração. Uma bolsa maior pode alterar a composição dos entrantes; comparar apenas quem entrou condiciona em uma variável afetada pelo tratamento.

## 4. Linear, logarítmica, potência ou exponencial?

| Objeto | Forma teórica preferida | Forma empírica inicial | Interpretação |
|---|---|---|---|
| Consumo/renda disponível | CRRA; log quando $\sigma=1$ | $\ln C$, quando $C$ puder ser construído | Utilidade marginal positiva e decrescente |
| Salto causal da bolsa no RDD | Regra administrativa discreta | dummy acima do corte e tendências locais em IVS | Efeito local de uma dose de R$ 5 mil; não substituir por $\ln B$ no tratamento principal |
| Esforço/carga | custo potência, $\eta>0$ | nível + quadrado, spline ou categorias pré-especificadas | Sobrecarga marginal crescente |
| Infraestrutura | produtividade com retornos decrescentes e complementaridade | $\ln(1+K_s)$ e $K_s\times Especialidade$ | Ganho maior onde o insumo é tecnicamente necessário |
| Distância | custo crescente; curvatura não determinada pela teoria | $\ln(1+d)$, tempo de viagem ou faixas | Grande diferença entre vínculo local e mudança; menor precisão dos km adicionais muito distantes |
| Amenidades | índice de consumo local | componentes padronizados ou índice pré-definido | Evitar usar o IVS como proxy perfeita de lazer, segurança e escola |
| Densidade médica | pares/suporte versus competição | spline ou categorias | Sinal e curvatura potencialmente não monotônicos |
| Propósito | matching entre tipo e missão | $Need_m\times M_i$, com $M_i$ medido antes da escolha | Necessidade isolada não identifica propósito |
| Probabilidade de escolha | utilidade aleatória | conditional/mixed logit | A exponencial pertence ao link probabilístico |

Uma especificação linear de renda é defensável como aproximação local de primeira ordem, especialmente perto de um cutoff. Para diferenças amplas de renda, a forma log/CRRA é teoricamente mais coerente. A forma CARA, $v(C)=-e^{-aC}$, impõe aversão absoluta ao risco constante e não é a escolha padrão para renda positiva em decisões locacionais; ela só deve ser usada se houver razão substantiva e comparação de ajuste.

No logit condicional, a exponencial surge porque se assume erro extremo-valor tipo I:

$$
P_i(m\mid\mathcal{J}_{it})
=\frac{\exp(\bar V_{im}/s)}
{\exp(V_i^{out}/s)+\sum_{j\in\mathcal{J}_{it}}\exp(\bar V_{ij}/s)}.
$$

Isso **não** significa que renda entre exponencialmente na utilidade. Pode-se ter $\bar V_{im}=\alpha\ln C_{im}+\beta X_{im}$ e, ao mesmo tempo, probabilidade logit.

## 5. Hipóteses estruturais e sinais esperados

| Hipótese | Predição para escolha/atração | Predição para saída | Restrição ou ressalva |
|---|---:|---:|---|
| H1. Bolsa/renda real | $+$, com efeito marginal decrescente | $-$ enquanto vigente | Bolsa é função administrativa do IVS |
| H2. Carga, plantão e imprevisibilidade | $-$, possivelmente convexo | $+$ | Jornada contratada comum não identifica diferenças de carga efetiva |
| H3. Infraestrutura, equipe e referência | $+$ | $-$ | Efeito maior em especialidades procedimentais |
| H4. Autonomia e flexibilidade | $+$ | $-$ | Podem compensar parcialmente ausência de vínculo |
| H5. Formação, mentoria e certificação | $+$ | $-$ durante o curso | Efeito provavelmente maior no início da carreira |
| H6. Amenidades, segurança e conectividade | $+$ | $-$ | Custo de moradia entra separadamente no consumo real |
| H7. Distância e separação familiar | $-$ | $+$ | Mesma região de residência/origem/formação deve elevar utilidade |
| H8. Necessidade assistencial $\times$ orientação pró-social | $+$ | $-$ | O efeito médio do IVS permanece ambíguo |
| H9. Densidade de pares | ambígua/não linear | ambígua | Suporte e aprendizado versus competição |
| H10. Duração | dependência de estado positiva ou burnout | não monotônica | Exige dados longitudinais além do cumprimento contratual |

Não há fundamento geral para impor $\beta_{Bolsa\times IVS}>0$. Em uma utilidade aditiva, a bolsa pode compensar uma desamenidade sem qualquer interação. Uma interação positiva exigiria a hipótese adicional de que a utilidade marginal da bolsa cresce com o IVS. Como a bolsa é mecanicamente definida por faixas de IVS, uma regressão global com ambos não separa seus efeitos causais.

## 6. Tradução para as especificações do projeto

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

- **McFadden, D. (1974).** [*Conditional Logit Analysis of Qualitative Choice Behavior*](https://eml.berkeley.edu/reprints/mcfadden/zarembka.pdf). Base para utilidade aleatória, conjunto de escolha e conditional logit.
- **Becker, G. S. (1965).** [*A Theory of the Allocation of Time*](https://doi.org/10.2307/2228949). Fundamenta o custo de oportunidade do tempo e a escolha entre trabalho, consumo e demais usos do tempo.
- **Roback, J. (1982).** [*Wages, Rents, and the Quality of Life*](https://doi.org/10.1086/261120). Fundamenta diferenciais compensatórios; o sinal do salário observado não é trivial quando amenidades também afetam produtividade e custos locais.
- **Glaeser, E. L.; Kolko, J.; Saiz, A. (2001).** [*Consumer City*](https://doi.org/10.1093/jeg/1.1.27). Fundamenta a entrada de lazer, serviços e outras amenidades locais na escolha residencial.
- **Kennan, J.; Walker, J. R. (2011).** [*The Effect of Expected Income on Individual Migration Decisions*](https://doi.org/10.3982/ECTA4657). Fundamenta decisão dinâmica, custos de mudança e repetição de escolhas locacionais.
- **Besley, T.; Ghatak, M. (2005).** [*Competition and Incentives with Motivated Agents*](https://doi.org/10.1257/0002828054201413). Fundamenta heterogeneidade de motivação e matching por missão; não implica que incentivo financeiro seja irrelevante.
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

1. Usar a Equação (1) para justificar sinais e formas funcionais, sem alegar que os pesos já são identificados.
2. Preferir log/CRRA para renda em modelos amplos; usar nível/dummy no efeito local da regra de bolsa.
3. Modelar esforço com convexidade e infraestrutura como complemento específico da especialidade.
4. Não impor sinal negativo ao IVS nem interação positiva `Bolsa × IVS`.
5. Manter IVS 2010 do IPEA como running variable canônica.
6. Separar renda corrente, formação e valor futuro da certificação.
7. Incluir opção externa e conjunto real de alternativas em futuros modelos individuais.
8. Separar atração, alocação administrativa e retenção.
9. Usar somente covariáveis pré-tratamento na especificação do efeito total.
10. Tratar propósito, preferências familiares e burnout como heterogeneidade não observada até que sejam medidos de forma prévia e defensável.
