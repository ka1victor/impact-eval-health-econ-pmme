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

A arquitetura teórica adotada neste memo é hierárquica e deliberadamente parcimoniosa:

1. **Moehling et al. (2020) são o núcleo:** fornecem o problema intertemporal de escolha da localidade pelo médico.
2. **Reinhardt (1975) abre a tecnologia da prática médica:** separa renda, lazer/horas, equipe, capital clínico e preocupação com a assistência da comunidade.
3. **Roback (1982) abre o ambiente espacial:** separa amenidades de consumo, custo de moradia e amenidades que afetam a produção.
4. **Besley e Ghatak (2005) permanecem como extensão opcional:** são úteis quando a hipótese exigir matching de missão, mas não são necessários para explicar infraestrutura ou carga de trabalho.

McFadden (1974), Costa, Nunes e Sanches (2024) e os experimentos de escolha entram depois, na passagem para mensuração e estimação; suas especificações econométricas não são apresentadas como a teoria substantiva da utilidade médica.

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

Essa distinção impede que $c$ seja usado como um recipiente para toda característica municipal. No próprio paper, $c$ recebe apenas uma descrição verbal curta e não é decomposto por uma segunda equação. Por isso, Moehling et al. continuam sendo o núcleo da escolha locacional, enquanto Roback e Reinhardt são usados abaixo para abrir, respectivamente, os canais espacial e produtivo.

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
| $c$ | custo/desamenidade de consumo ligada à localidade | distância da família, dupla moradia, segurança, escolas, lazer e conectividade |
| amenidades produtivas em $\mathbb E(w)$ | capacidade de exercer a especialidade e produzir capital profissional | hospitais, laboratórios, equipamentos, equipe, referência, mentoria e rede profissional |
| $\delta$ | valor presente de retornos atuais e futuros | duração da formação e retorno futuro esperado da certificação |
| heterogeneidade em $s$ | atributos têm valores distintos por tipo de médico | especialidade, estágio de carreira e vínculo territorial prévio |

O IVS não aparece como um bem ou mal primitivo na Equação (1) e não deve ser renomeado como uma amenidade de consumo. Ele pode elevar a bolsa, sinalizar maior necessidade assistencial e, simultaneamente, correlacionar-se com preços, amenidades, infraestrutura e pressão de trabalho. Por isso, o sinal total do IVS sobre a utilidade permanece teoricamente ambíguo. O IVS 2010 continua sendo a **running variable canônica** do projeto; essa decomposição serve para interpretar mecanismos, não para substituí-lo por IDHM ou PIB per capita.

## 3. Equações 2–6 — produção, tempo e utilidade da prática médica em Reinhardt

Moehling et al. distinguem amenidades de consumo e amenidades produtivas, mas não escrevem uma função de produção médica. O complemento produtivo vem de **Reinhardt (1975)**. Ao modelar a decisão de insumos e produto de uma prática médica, o autor supõe que o médico maximiza:

$$
U=U(R,Y,L,D;\mathbf Z),
\tag{2; Reinhardt, 1975}
$$

sujeito à restrição de tempo

$$
\bar H=R+H,
\tag{3; Reinhardt, 1975}
$$

à função de produção de serviços médicos

$$
q=f(H,L,K;\boldsymbol\Omega),
\tag{4; Reinhardt, 1975}
$$

e às definições de renda líquida e lucro antes dos impostos

$$
Y=[1-t(\pi+I)](\pi+I),
\tag{5; Reinhardt, 1975}
$$

$$
\pi=pq-wL-rK.
\tag{6; Reinhardt, 1975}
$$

Essas são as Equações (6)–(10) do capítulo original, renumeradas neste memo. Na notação de Reinhardt:

- $R$ são horas de lazer e $H$ horas de trabalho médico, dadas as horas totais $\bar H$;
- $Y$ é a renda líquida e $I$ a renda externa à prática;
- $q$ é a produção de serviços médicos;
- $L$ é o trabalho de pessoal auxiliar;
- $K$ é um índice de insumos não laborais, como espaço, equipamentos e outros recursos clínicos;
- $D$ relaciona a percepção do médico sobre a assistência disponível à comunidade e sua própria contribuição;
- $\mathbf Z$ contém características pessoais e profissionais que afetam utilidade;
- $\boldsymbol\Omega$ contém outros deslocadores da tecnologia produtiva;
- na Equação (6), $p$ é o preço ou reembolso por unidade de serviço, $w$ o custo do pessoal auxiliar e $r$ o custo dos insumos não laborais.

O símbolo $p$ não tem o mesmo significado nos dois papers: em Moehling et al. é o **nível de preços local**; em Reinhardt é o **reembolso por unidade produzida**. As equações devem ser apresentadas em blocos separados para evitar essa colisão de notação.

### 3.1 Como $K$ entra e por que não pertence a $c$

Em Reinhardt, $K$ altera a fronteira de produção médica. Sob $f_K>0$, mais infraestrutura aumenta $q$ para as mesmas horas e equipe. Alternativamente, para uma meta fixa $\bar q$ e com $f_H>0$, a Equação (4) implica:

$$
\left.\frac{dH}{dK}\right|_{q=\bar q}
=-\frac{f_K}{f_H}<0.
$$

Essa derivada é uma estática comparativa obtida da equação publicada, e não uma nova função de utilidade. Com $R=\bar H-H$ e $U_R>0$, infraestrutura pode elevar utilidade ao reduzir as horas necessárias para produzir determinado atendimento. Se as 20 horas do PMM-E forem rígidas, $K$ pode elevar produção e qualidade sem reduzir $H$; nesse caso, o ganho de utilidade depende de valorização de resultado, aprendizado, segurança clínica ou menor frustração, e não é automático apenas pela restrição de tempo.

No PMM-E, $K$ é predominantemente fornecido pela unidade de saúde e não comprado pelo médico. Por isso, as Equações (5)–(6), construídas para um médico proprietário em regime de pagamento por serviço, não devem ser transplantadas literalmente. O mecanismo transferível é o das Equações (2)–(4): cada oferta apresenta ao médico uma combinação exógena de renda, horas, equipe, infraestrutura, necessidade assistencial e condições profissionais.

### 3.2 Equipe, carga e propósito

A equipe $L$ tem dois papéis no modelo original: aumenta a capacidade produtiva em $f(H,L,K)$ e entra diretamente em $U$ porque Reinhardt supõe que administrar auxiliares pode gerar custos psíquicos ao médico proprietário. Para o PMM-E, o segundo sinal não deve ser copiado: equipe fornecida pela unidade pode reduzir sobrecarga, enquanto responsabilidade gerencial pode aumentá-la. O conteúdo empiricamente relevante é a suficiência, composição e governança da equipe, não apenas seu tamanho.

A carga de trabalho entra pelo uso de tempo: maior $H$ reduz $R$. O modelo, porém, não impõe forma quadrática ou outra curvatura específica para essa desutilidade. Pressão, imprevisibilidade, plantões e complexidade da demanda devem ser medidas separadamente das horas sempre que possível.

O termo $D$ permite que preocupação com a assistência da comunidade afete o comportamento médico. Reinhardt afirma que necessidades locais não atendidas podem induzir mais horas ou maior delegação. Isso aproxima $D$ do canal de propósito, mas não torna vulnerabilidade sinônimo de motivação: a resposta depende da identificação do médico com a comunidade e de suas preferências.

### 3.3 Como Moehling e Reinhardt modelam produção

Os dois modelos são compatíveis como camadas, mas não escrevem a produção da mesma maneira:

| Modelo | Representação da produção | Papel no PMM-E |
|---|---|---|
| Moehling et al. | forma reduzida: hospitais, laboratórios, mercado, estradas e aglomeração são amenidades produtivas que podem elevar $\mathbb E(w)$ | explica por que características produtivas da localidade alteram o retorno esperado e a escolha locacional |
| Reinhardt | forma explícita: $q=f(H,L,K;\boldsymbol\Omega)$ | mostra como horas, equipe e infraestrutura determinam a capacidade de produzir serviços e o custo de tempo do médico |

A interpretação operacional é em duas etapas. Primeiro, Reinhardt organiza o valor e a tecnologia do pacote de trabalho oferecido em cada localidade. Depois, Moehling determina qual localidade maximiza o valor presente do médico. Essa combinação é uma **arquitetura de leitura** dos dois papers; não se deve atribuir a função $q=f(H,L,K)$ a Moehling nem afirmar que Reinhardt escreveu um modelo de escolha entre municípios.

## 4. Equações 7–9 — amenidades de consumo e produção em Roback

Roback (1982) fornece a microfundamentação espacial citada pelo próprio Moehling. O trabalhador resolve:

$$
\max_{x,\ell^c} U(x,\ell^c;s)
\quad\text{sujeito a}\quad
w+I=x+r\ell^c,
\tag{7; Roback, 1982}
$$

e o equilíbrio entre localidades exige:

$$
V(w,r;s)=k.
\tag{8; Roback, 1982}
$$

Do lado das firmas, a condição é:

$$
C(w,r;s)=1.
\tag{9; Roback, 1982}
$$

$x$ é o bem de consumo composto, $\ell^c$ a terra ou moradia consumida, $r$ o aluguel, $I$ a renda não laboral e $s$ uma amenidade local. A mesma característica $s$ pode afetar diretamente o bem-estar do trabalhador e a produtividade da firma. Salários e aluguéis ajustam-se conjuntamente no equilíbrio espacial.

Para o PMM-E, Roback disciplina o conteúdo de $c$ em Moehling:

| Bloco | Exemplos | Tratamento conceitual |
|---|---|---|
| amenidades de consumo | segurança, escolas, lazer, clima, conectividade, proximidade familiar | entram em $c$ ou diretamente em $s$ |
| preços locais | aluguel e custo de bens e serviços | entram em $p$ ou na restrição orçamentária; não duplicar em $c$ |
| amenidades produtivas gerais | acesso, aglomeração, mercado e infraestrutura de transporte | afetam custos, produtividade e retornos |
| tecnologia clínica | equipamentos, serviços diagnósticos, leitos, equipe e referência | detalhada por $q=f(H,L,K;\boldsymbol\Omega)$ em Reinhardt |
| condições do trabalho | horas, plantões, pressão e autonomia | entram na utilidade e na restrição de tempo; não são amenidades de consumo |

Roback não fornece uma lista fechada de amenidades nem uma curvatura específica para renda. Seu papel é impedir dupla contagem e separar o que afeta consumo do que afeta produção.

### 4.1 O IVS atravessa vários canais

O IVS do Ipea é composto pelas dimensões infraestrutura urbana, capital humano e renda e trabalho. A dimensão de infraestrutura urbana não mede equipamentos ou capacidade clínica da unidade de saúde. Portanto, o IVS não substitui $K$ e não deve ser colocado integralmente dentro de $c$.

| Canal do IVS | Primitivo correspondente | Sinal esperado sobre utilidade |
|---|---|---:|
| regra administrativa da bolsa | $\mathbb E(w)/p$ em Moehling; $Y$ em Reinhardt | positivo |
| custo de vida | $p$ em Moehling; $r$ em Roback | ambíguo |
| amenidades urbanas e familiares | $c$ em Moehling; $s$ em Roback | em geral negativo quando a vulnerabilidade indica carências |
| infraestrutura clínica | $K$ em Reinhardt | correlação possível, mas IVS não é sua medida |
| pressão e necessidade assistencial | $H$ e $D$ em Reinhardt | pressão negativa; propósito potencialmente positivo |

O efeito líquido do IVS é teoricamente ambíguo porque esses canais têm sinais distintos. Na avaliação causal, o IVS 2010 permanece a running variable; a decomposição serve para formular mecanismos e heterogeneidade, não para substituir o índice ou controlar simultaneamente por mediadores pós-programa.

## 5. Extensão opcional — matching de missão em Besley e Ghatak

Quando a hipótese substantiva for que médicos diferem no alinhamento com a missão da vaga, Besley e Ghatak (2005) oferecem um complemento mais específico que o termo $D$ de Reinhardt. No modelo publicado:

$$
u^p_{ij}=(\pi_i-b_{ij})e_{ij}-w_{ij},
\qquad
u^a_{ij}=e_{ij}(b_{ij}+\theta_{ij})+w_{ij}-\frac{1}{2}e_{ij}^{2},
\tag{10; Besley e Ghatak, 2005}
$$

e, na solução interior,

$$
e^*_{ij}=b_{ij}+\theta_{ij}.
\tag{11; Besley e Ghatak, 2005}
$$

$\theta_{ij}$ é o benefício não pecuniário do matching entre agente e missão. Essa extensão não é necessária para justificar $K$, equipe ou horas. Se usada, exige medida prévia de orientação pró-social e não autoriza tratar IVS alto como propósito para todos os médicos. O esforço $e$ é escolhido e aumenta a probabilidade de sucesso; ele não é idêntico a carga assistencial imposta.

## 6. O que os modelos publicados autorizam sobre formas funcionais

| Componente | Forma no paper teórico | Sinal/curvatura autorizados | Decisão para o PMM-E |
|---|---|---|---|
| Remuneração locacional | $\mathbb E(w)/p$ em Moehling et al. | positiva e linear no valor real | benchmark em nível real; faixas da bolsa preservadas no desenho causal |
| Renda líquida | $Y$ como argumento de $U$ em Reinhardt | $U_Y>0$ é a hipótese econômica usual; a curvatura não é especificada | usar para explicitar o canal de renda, não para escolher entre nível e log |
| Custo de vida | remuneração dividida por $p$ em Moehling; orçamento com $r$ em Roback | preços e aluguel reduzem consumo real, mantidos os demais termos | deflacionar quando houver índice defensável; aluguel pode entrar separadamente |
| Amenidades de consumo | $-c$ em Moehling; $s$ em Roback | $c$ reduz valor; o sinal de $s$ depende de como a amenidade é codificada | distância, família, segurança, escola, lazer e conectividade em bloco separado |
| Horas e lazer | $\bar H=R+H$ e $U(R,\ldots)$ em Reinhardt | se $U_R>0$, mais $H$ reduz lazer; a curvatura não é especificada | não impor custo quadrático à carga sem um modelo adicional |
| Infraestrutura clínica | $K$ em $q=f(H,L,K;\boldsymbol\Omega)$ | $f_K>0$ é uma hipótese de produtividade; o efeito sobre utilidade depende do regime de horas e do valor do produto | construir $K$ pré-tratamento e específico da especialidade |
| Equipe | $L$ na produção e diretamente em $U$ em Reinhardt | $f_L>0$ pode elevar produção; o efeito direto sobre utilidade depende de suporte versus ônus gerencial | medir suficiência, composição e governança, não apenas quantidade |
| Necessidade e assistência comunitária | $D$ em Reinhardt | o sinal depende da codificação de $D$ e das preferências do médico | separar necessidade local de identificação pró-social |
| Matching de missão, opcional | $+e\theta$ em Besley–Ghatak | positivo quando há matching; complementar ao sucesso | usar apenas se houver medida prévia de orientação pró-social |
| Formação futura | soma descontada $\sum_t\delta^t[\cdot]$ | retornos futuros valem menos quando mais distantes | tratar certificação/mentoria como alteração do fluxo futuro esperado, não como renda corrente |

### 6.1 Linear, logarítmica ou exponencial para renda?

A escolha canônica deste memo passa a ser **linear em remuneração real**, porque essa é a forma da equação locacional de Moehling et al., e não apenas porque o sinal positivo seja intuitivo. Nesse modelo específico, a utilidade marginal da remuneração real é constante. Reinhardt escreve uma função de utilidade genérica e Roback não escolhe uma forma funcional; portanto, nenhum dos dois autoriza afirmar, a priori, retorno marginal decrescente da bolsa nem contradiz o benchmark linear de Moehling.

Uma função logarítmica ou CRRA poderia ser adotada por outro modelo de consumo côncavo, mas isso seria uma mudança de fundamento teórico e deve vir acompanhada da citação do modelo escolhido. A função exponencial do tipo CARA, $-\exp(-aw)$, é uma representação de preferência sob risco com aversão absoluta constante; ela não aparece nos modelos selecionados de escolha locacional médica ou missão.

Portanto:

- **modelo teórico principal:** bolsa/remuneração real em nível;
- **não impor:** retorno marginal decrescente da renda sem trocar ou ampliar o modelo teórico;
- **não usar:** utilidade exponencial da renda como escolha automática;
- **não confundir:** a exponencial que aparece em probabilidades logit pertence ao mecanismo probabilístico de escolha, não à utilidade monetária do trabalhador.

Para horas, equipe e infraestrutura, Reinhardt também fundamenta os **argumentos** e as restrições do problema, mas não fixa a curvatura de $U$ ou de $f$. Convexidade da desutilidade da carga, retornos decrescentes de $K$ e complementaridades entre $H$, $L$ e $K$ são hipóteses adicionais que devem ser declaradas e testadas, não atribuídas ao capítulo sem demonstração.

## 7. Hipóteses estruturais e sinais esperados

| Hipótese | Predição para escolha/atração | Predição para saída | Restrição ou ressalva |
|---|---:|---:|---|
| H1. Bolsa/renda real | $+$ e linear no benchmark de Moehling | $-$ enquanto vigente | Reinhardt e Roback não impõem curvatura; bolsa é função administrativa do IVS |
| H2. Horas, plantão e imprevisibilidade | $-$ se reduzirem lazer ou elevarem custo psíquico | $+$ | Reinhardt não impõe convexidade; esforço escolhido em Besley–Ghatak não é carga imposta |
| H3. Infraestrutura, equipe e referência | $+$ sob produtividade positiva e valorização do produto/menor pressão | $-$ | Com jornada fixa, maior $K$ pode elevar $q$ sem elevar automaticamente a utilidade; efeitos variam por especialidade |
| H4. Autonomia e flexibilidade | $+$ | $-$ | Podem compensar parcialmente ausência de vínculo |
| H5. Formação, mentoria e certificação | $+$ se elevar o fluxo futuro esperado | $-$ durante o curso | Entra pela soma descontada; heterogeneidade por carreira é hipótese empírica |
| H6. Amenidades, segurança e conectividade | $+$ | $-$ | Custo de moradia entra separadamente no consumo real |
| H7. Distância e separação familiar | $-$ | $+$ | Mesma região de residência/origem/formação deve elevar utilidade |
| H8. Necessidade local $\times$ identificação pró-social | $+$ para médicos que valorizem a assistência comunitária | $-$ | Pode ser lida por $D$ em Reinhardt ou, se houver matching mensurado, por $\theta_{ij}$ em Besley–Ghatak; IVS isolado não mede propósito |
| H9. Densidade de pares | ambígua/não linear | ambígua | Suporte e aprendizado versus competição |
| H10. Duração | dependência de estado positiva ou burnout | não monotônica | Exige dados longitudinais além do cumprimento contratual |

O efeito total do IVS sobre escolha ou permanência é ambíguo: a regra da bolsa opera positivamente, enquanto custo de vida, amenidades urbanas, infraestrutura clínica, pressão e propósito podem operar em direções diferentes. Também não há fundamento geral para impor $\beta_{Bolsa\times IVS}>0$. Em uma utilidade aditiva, a bolsa pode compensar uma desamenidade sem qualquer interação. Uma interação positiva exigiria a hipótese adicional de que a utilidade marginal da bolsa cresce com o IVS. Como a bolsa é mecanicamente definida por faixas de IVS, uma regressão global com ambos não separa seus efeitos causais.

## 8. Tradução para as especificações do projeto

As equações desta seção são implementações econométricas e **não** a fundamentação microeconômica. A arquitetura teórica central e complementar está nas Equações (1)–(9), transcritas dos trabalhos publicados; as Equações (10)–(11) são a extensão opcional de missão. Esta seção apenas mostra como seus primitivos orientam variáveis e desenhos empíricos.

### 8.1 Atração e preenchimento com os dados atuais

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

### 8.2 Efeito causal da bolsa nos cortes do IVS

Se a regra e o IVS administrativo forem validados, a especificação local é:

$$
Y_m=\alpha+\tau\mathbf{1}(R_m\ge c)
+\beta_1(R_m-c)
+\beta_2\mathbf{1}(R_m\ge c)(R_m-c)
+\alpha_s+\lambda_c+\varepsilon_m.
$$

$\tau$ representa o efeito local do salto de bolsa somente se não houver outra regra ou mudança de composição descontínua no mesmo corte. Covariáveis prévias servem para precisão e diagnóstico de balanço; não substituem a validação institucional.

### 8.3 Escolha individual quando houver microdados

O modelo adequado é conditional logit, rank-ordered logit ou mixed logit com:

- conjunto completo de opções elegíveis e visíveis em cada instante;
- opção externa de não participar;
- atributos de cada oferta;
- indicadores derivados de mesma UF/região de residência, nascimento e formação;
- distância ou tempo de viagem entre origem e oferta;
- heterogeneidade por especialidade e estágio de carreira;
- capacidade da vaga e regras de alocação separadas da preferência.

Coerentemente com o benchmark locacional de Moehling et al., a remuneração real em nível deve ser a forma principal. Log da remuneração pode ser apresentado como robustez associada a um modelo alternativo de utilidade côncava; forma exponencial não deve ser incluída sem fundamento teórico adicional.

Sem o conjunto de alternativas, observam-se apenas opções escolhidas, não escolhas frente a oportunidades reais. Sem não candidatos, identifica-se no máximo a localização condicional à candidatura, e não a margem extensiva de participar.

Em conditional logit, atributos que variam apenas entre médicos cancelam na comparação entre opções. Idade, estágio de carreira ou experiência prévia devem interagir com atributos da vaga/localidade ou com a constante da opção externa; não entram isoladamente como determinantes da escolha entre municípios.

### 8.4 Retenção

Com eventos individuais e ponte pseudonimizada, usar um hazard em tempo discreto com dummies de duração. Bolsa recebida, atraso de pagamento, carga e infraestrutura realizadas podem ser usados para mecanismos, desde que se reconheça sua natureza potencialmente pós-tratamento. Participação por 12 meses mede conclusão do programa; não é sinônimo de fixação municipal duradoura.

## 9. Prioridade dos regressores e dados

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

Essas medidas operacionalizam $K$, $L$ e $\boldsymbol\Omega$ em Reinhardt e devem ser específicas para a tecnologia de cada especialidade. A dimensão “infraestrutura urbana” do IVS não é substituta desses recursos clínicos.

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

## 10. O que pode e o que não pode ser chamado de peso de utilidade

A teoria determina argumentos, sinais locais e algumas curvaturas; não determina a fração da utilidade proveniente de renda, propósito ou lazer. Utilidade é ordinal, e a escala dos coeficientes em modelos de escolha é normalizada pela variância do erro.

Com escolhas individuais e variação identificada, podem ser reportados:

- efeitos marginais sobre probabilidades;
- elasticidades de escolha;
- WTA em reais para uma desamenidade;
- distribuição de preferências em mixed logit;
- heterogeneidade de WTA por especialidade ou vínculo territorial.

Razões como $-\beta_x/\beta_B$ têm interpretação monetária somente quando o atributo de renda está adequadamente identificado e na mesma função de utilidade. Coeficientes de uma regressão agregada de preenchimento não devem ser convertidos diretamente em WTA.

## 11. Referências essenciais e uso correto

### Modelos microeconômicos que geram as equações do memo

- **Moehling, C. M.; Niemesh, G. T.; Thomasson, M. A.; Treber, J. (2020).** [*Medical Education Reforms and the Origins of the Rural Physician Shortage*](https://doi.org/10.1007/s11698-019-00187-w) ([manuscrito dos autores com a Equação 1](https://niemesgt.github.io/files/MoehlingNiemeshThomassonTreber2019.pdf)). Fornece o problema intertemporal de escolha locacional do médico usado na Equação (1): remuneração real esperada menos custos/desamenidades locais.
- **Reinhardt, U. E. (1975).** [*Health Manpower Planning in a Market Context: The Case of Physician Manpower*](https://pure.iiasa.ac.at/213/1/XB-75-001.pdf), em N. T. J. Bailey e M. Thompson (eds.), *Systems Aspects of Health Planning*, pp. 131–162. Fornece as Equações (2)–(6): utilidade do médico, restrição de tempo, produção $q=f(H,L,K;\boldsymbol\Omega)$, renda e lucro da prática. O regime original é de médico proprietário remunerado por serviço; no PMM-E, usam-se sobretudo os canais de utilidade, tempo e produção.
- **Roback, J. (1982).** [*Wages, Rents, and the Quality of Life*](https://doi.org/10.1086/261120) ([PDF](https://www.nathanschiff.com/webdocs/grad_urban/urban_papers/Roback_JPE_1982.pdf)). Fornece as Equações (7)–(9) e a microfundamentação espacial de consumo, terra/moradia, amenidades e produtividade. Não fixa uma curvatura específica para renda.
- **Besley, T.; Ghatak, M. (2005).** [*Competition and Incentives with Motivated Agents*](https://doi.org/10.1257/0002828054201413) ([PDF dos autores](https://personal.lse.ac.uk/ghatak/motivated.pdf)). Extensão opcional reproduzida nas Equações (10)–(11): matching de missão e custo quadrático do esforço escolhido. Não fundamenta, por si só, infraestrutura clínica ou carga assistencial imposta.
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
- **Ipea (2015).** [*Atlas da Vulnerabilidade Social nos Municípios Brasileiros*](https://repositorio.ipea.gov.br/entities/publication/97ad7674-c773-4f74-adbe-58588e99fa4e). Documenta as dimensões de infraestrutura urbana, capital humano e renda e trabalho do IVS; a primeira não deve ser confundida com infraestrutura clínica da unidade.
- **Brasil, Ministério da Saúde.** [FAQ do Chamamento Público SGTES/MS nº 3/2025](https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2025/chamamento-publico-sgtes-ms-no-3-2025-projeto-mais-medicos-especialistas/faq).
- **Brasil, Ministério da Saúde.** [Projeto Mais Médicos Especialistas](https://www.gov.br/saude/pt-br/composicao/sgtes/mais-medicos/especialistas/especialistas).

## 12. Decisões de modelagem consolidadas

1. Usar Moehling et al. (2020), e não uma função criada para o projeto, como equação canônica da escolha locacional do médico.
2. Usar Reinhardt (1975) para abrir produção, tempo e utilidade da prática: $q=f(H,L,K;\boldsymbol\Omega)$, $\bar H=R+H$ e $U(R,Y,L,D;\mathbf Z)$.
3. Usar Roback (1982) para disciplinar o conteúdo espacial de $c$: amenidades de consumo, preços/moradia e amenidades produtivas são canais distintos.
4. Não colocar toda característica municipal em $c$: infraestrutura clínica pertence a $K$; horas e pressão pertencem às condições do trabalho; preços pertencem a $p$ ou à restrição orçamentária.
5. Tratar Besley e Ghatak (2005) apenas como extensão de matching de missão quando houver medida prévia de orientação pró-social.
6. Adotar remuneração real em nível como forma principal pelo benchmark de Moehling; não impor log/CRRA nem exponencial sem mudar explicitamente o modelo teórico.
7. Não afirmar retorno marginal decrescente da bolsa, custo quadrático da carga ou retornos decrescentes de $K$ a partir dos modelos selecionados.
8. Não impor sinal negativo ao IVS nem interação positiva `Bolsa × IVS`; seus canais teóricos têm sinais distintos.
9. Manter IVS 2010 do Ipea como running variable canônica e não tratá-lo como medida de $K$.
10. Separar renda corrente de retornos futuros de formação e certificação na soma descontada.
11. Incluir opção externa e conjunto real de alternativas em futuros modelos individuais; separar atração, alocação e retenção.
12. Medir orientação por missão antes da escolha; não construir “vocação” a partir da escolha observada.
