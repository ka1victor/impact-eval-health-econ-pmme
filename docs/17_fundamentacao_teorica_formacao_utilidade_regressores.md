# 17. Base microeconômica da escolha locacional médica

> **Escopo:** equações originais, modelo micro adotado e hipóteses derivadas para o relatório
>
> **Data de consolidação:** 31 de agosto de 2026

## 1. Arquitetura teórica

A fundamentação é organizada em três camadas:

1. **Moehling et al. (2020) são o núcleo:** apresentam o problema intertemporal de escolha da localidade pelo médico.
2. **Roback (1982) complementa o bloco espacial:** formaliza amenidades de consumo, custo de moradia e amenidades produtivas.
3. **Reinhardt (1975) complementa o bloco de produção médica:** explicita utilidade, tempo, renda e produção de serviços médicos.

Os três trabalhos não escrevem conjuntamente um único modelo. A relação proposta aqui é interpretativa: Roback e Reinhardt ajudam a compreender os canais que permanecem em forma reduzida na equação locacional de Moehling et al. Nenhuma função nova é criada para uni-los.

## 2. Moehling et al. — escolha locacional

Moehling, Niemesh, Thomasson e Treber (2020) escrevem o problema de escolha locacional do médico como:

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

Na notação dos autores:

- $i$ indexa a localidade;
- $t$ indexa o período;
- $s$ identifica o grupo de qualificação;
- $w^{(s)}_{it}$ é a remuneração nominal esperada;
- $p_{it}$ é o nível de preços local;
- $c^{(s)}_{it}$ reúne custos e amenidades de consumo ligados à localidade;
- $\delta$ é o fator de desconto.

O médico escolhe a localidade que oferece o maior valor presente da remuneração real esperada, líquida dos custos e desamenidades locacionais representados por $c$.

O artigo menciona preferência por vida rural ou urbana e proximidade da família ao discutir $c$. Hospitais, laboratórios, tamanho do mercado, estradas, aglomeração profissional e escolas médicas são tratados separadamente como **amenidades produtivas** capazes de afetar a remuneração nominal esperada.

Moehling et al. não escrevem uma função de produção. A produção aparece em forma reduzida: características produtivas da localidade alteram $\mathbb E(w^{(s)}_{it})$, que, por sua vez, altera o valor da opção locacional.

## 3. Reinhardt — utilidade, tempo e produção médica

Reinhardt (1975) modela a prática médica por meio das seguintes equações:

$$
U=U(R,Y,L,D;\mathbf Z),
\tag{6; Reinhardt, 1975}
$$

$$
\bar H=R+H,
\tag{7; Reinhardt, 1975}
$$

$$
q=f(H,L,K;\boldsymbol\Omega),
\tag{8; Reinhardt, 1975}
$$

$$
Y=[1-t(\pi+I)](\pi+I),
\tag{9; Reinhardt, 1975}
$$

$$
\pi=pq-wL-rK.
\tag{10; Reinhardt, 1975}
$$

Na notação do autor:

- $R$ são horas de lazer;
- $H$ são horas de trabalho do médico;
- $\bar H$ é a dotação total de tempo;
- $Y$ é a renda líquida;
- $I$ é a renda externa à prática;
- $q$ é a produção de serviços médicos;
- $L$ é o trabalho de pessoal auxiliar;
- $K$ é o índice de insumos não laborais empregado pelo autor;
- $D$ representa a preocupação do médico com a assistência disponível à comunidade e com sua própria contribuição;
- $\mathbf Z$ reúne características pessoais e profissionais que deslocam a utilidade;
- $\boldsymbol\Omega$ reúne deslocadores da tecnologia produtiva;
- $p$ é o preço ou reembolso por unidade de serviço;
- $w$ e $r$ são, respectivamente, os preços dos insumos laborais e não laborais.

Aqui a produção é explícita. Horas do médico, trabalho auxiliar e insumos não laborais entram diretamente na tecnologia que gera serviços médicos. Essa produção afeta o lucro e a renda, enquanto a alocação de tempo liga horas de trabalho e lazer.

O símbolo $p$ tem significados diferentes nos dois trabalhos: em Moehling et al. é o nível de preços da localidade; em Reinhardt é o preço ou reembolso do serviço médico.

## 4. Roback — amenidades de consumo e amenidades produtivas

Roback (1982) apresenta o problema do trabalhador como:

$$
\max_{x,\ell^c} U(x,\ell^c;s)
\quad\text{sujeito a}\quad
w+I=x+r\ell^c,
\tag{1; Roback, 1982}
$$

com a condição de equilíbrio espacial:

$$
V(w,r;s)=k.
\tag{2; Roback, 1982}
$$

Do lado da produção, a condição de equilíbrio é:

$$
C(w,r;s)=1.
\tag{3; Roback, 1982}
$$

Na notação da autora:

- $x$ é o bem de consumo composto;
- $\ell^c$ é a quantidade de terra ou moradia consumida;
- $r$ é o aluguel;
- $w$ é o salário;
- $I$ é a renda não laboral;
- $s$ é uma característica ou amenidade local;
- $V$ é a utilidade indireta do trabalhador;
- $C$ é a função de custo da firma.

Roback permite que uma característica local afete diretamente a utilidade do trabalhador e também a produtividade da firma. Salários e aluguéis ajustam-se conjuntamente para compensar diferenças entre localidades.

Esse modelo esclarece a separação usada por Moehling et al.: atributos valorizados no consumo pertencem ao canal de amenidades e custos locacionais, enquanto atributos que alteram a produtividade pertencem ao canal dos retornos produtivos. Roback não fornece uma lista fechada desses atributos.

## 5. Relação entre os três modelos

| Pergunta teórica | Trabalho | Resposta do modelo |
|---|---|---|
| Em qual localidade o médico escolhe trabalhar? | Moehling et al. | escolhe o maior valor presente da remuneração real esperada menos custos e amenidades locacionais |
| Como amenidades, salários e aluguéis se relacionam no espaço? | Roback | amenidades afetam utilidade e/ou produtividade, e salários e aluguéis se ajustam no equilíbrio |
| Como os serviços médicos são produzidos? | Reinhardt | a produção resulta do uso de tempo do médico, pessoal auxiliar e insumos não laborais |

A conexão pode ser lida da seguinte forma:

1. **Reinhardt explicita a produção médica.**
2. **Roback mostra como condições de consumo e produção são capitalizadas espacialmente em salários e aluguéis.**
3. **Moehling et al. condensam esses retornos e custos no problema intertemporal de escolha entre localidades.**

Essa leitura preserva a autonomia dos modelos. A função de produção de Reinhardt não foi escrita por Moehling et al.; a equação locacional de Moehling et al. não aparece em Reinhardt; e Roback é um modelo geral de equilíbrio espacial, não um modelo específico de médicos.

### 5.1 Comparação do tratamento da produção

| Trabalho | Tratamento da produção |
|---|---|
| Moehling et al. | não há função de produção explícita; amenidades produtivas deslocam a remuneração nominal esperada |
| Reinhardt | há uma função de produção explícita de serviços médicos |
| Roback | a produtividade local aparece na função de custo da firma e na condição de equilíbrio |

## 6. Modelo micro adotado

O modelo microeconômico adotado para o relatório é o problema intertemporal de escolha locacional de **Moehling et al. (2020)**, reproduzido na Seção 2. Ele é adotado sem substituir seus primitivos por uma função criada para o projeto.

Para escrever as estáticas comparativas sem alterar o modelo, o critério do lado direito da equação publicada será apenas denotado por:

$$
V_i\equiv
\sum_t \delta^t
\left[
\frac{\mathbb E\!\left(w^{(s)}_{it}\right)}{p_{it}}
-c^{(s)}_{it}
\right].
$$

Essa linha introduz somente uma abreviação de notação: a escolha continua sendo $\arg\max_i V_i$, exatamente como no problema de Moehling et al.

Assim, o médico compara localidades pelo valor presente de:

1. remuneração nominal esperada;
2. poder de compra dessa remuneração;
3. custos e amenidades de consumo ligados à localidade;
4. retornos presentes e futuros, ponderados pelo fator de desconto.

Roback e Reinhardt não substituem essa equação. Eles cumprem papéis complementares:

- **Roback** esclarece a distinção entre amenidades de consumo, custo de moradia e características que afetam a produtividade;
- **Reinhardt** mostra, no caso médico, como tempo e insumos da prática se relacionam com produção, renda e utilidade.

Portanto, Moehling et al. fornecem a regra de escolha entre localidades; Roback e Reinhardt dão conteúdo econômico aos canais que podem determinar os termos dessa escolha.

## 7. Contextualização posterior para o estudo

Somente depois de apresentar o modelo publicado, seus termos podem ser relacionados ao objeto do estudo:

| Elemento teórico | Interpretação no relatório |
|---|---|
| $\mathbb E(w)/p$ em Moehling et al. | retorno monetário real esperado de uma opção |
| $c$ em Moehling et al. | custos e desamenidades de consumo associados à localidade, incluindo distância familiar e preferência rural ou urbana |
| amenidades produtivas em Moehling et al. | condições locais que alteram o retorno esperado do exercício profissional |
| $\delta$ em Moehling et al. | peso atribuído a retornos que ocorrem em momentos diferentes |
| $s$ e $r$ em Roback | amenidades locais e custo de moradia, com possível capitalização em salários e aluguéis |
| $R$ e $H$ em Reinhardt | escolha entre lazer e tempo dedicado ao trabalho médico |
| $L$ e os demais insumos da produção em Reinhardt | organização produtiva da prática médica |
| $D$ em Reinhardt | preocupação com a assistência disponível à comunidade e com a contribuição do próprio médico |

Essa contextualização não afirma que cada variável disponível corresponde perfeitamente a um primitivo teórico. Ela serve para orientar a construção dos regressores e explicitar quais mecanismos cada um pretende representar.

O IVS não é um argumento primitivo de nenhuma das funções. No estudo, ele pode estar relacionado a vários canais ao mesmo tempo: regra de remuneração, poder de compra, amenidades locais, condições produtivas e necessidade assistencial. Por isso, ele não deve ser identificado exclusivamente com $c$, com uma amenidade de consumo ou com um insumo produtivo.

## 8. Hipóteses derivadas do modelo

As hipóteses abaixo são apresentadas **depois** do modelo porque decorrem de suas equações e de condições de monotonicidade declaradas. As derivadas não são novas funções de utilidade; são implicações das funções publicadas.

### H1. Remuneração real esperada aumenta o valor da opção

Na equação de Moehling et al.:

$$
\frac{\partial V_i}
{\partial \mathbb E(w^{(s)}_{it})}
=\frac{\delta^t}{p_{it}}>0,
$$

para $p_{it}>0$ e $\delta>0$. Logo, uma opção com maior remuneração real esperada deve ser mais atraente, mantidos os demais termos constantes.

### H2. Maior nível de preços reduz o valor da remuneração nominal

Ainda em Moehling et al.:

$$
\frac{\partial V_i}
{\partial p_{it}}
=-\delta^t
\frac{\mathbb E(w^{(s)}_{it})}{p_{it}^{2}}<0,
$$

quando a remuneração nominal esperada é positiva. Portanto, o mesmo pagamento nominal produz menor valor quando o nível de preços é maior. Roback reforça esse mecanismo ao explicitar o custo da moradia na restrição orçamentária.

### H3. Custos e desamenidades locacionais reduzem o valor da opção

Se $c$ for codificado como custo ou desamenidade:

$$
\frac{\partial V_i}
{\partial c^{(s)}_{it}}
=-\delta^t<0.
$$

Distância da família e incompatibilidade com o modo de vida preferido são exemplos mencionados na discussão de Moehling et al. Uma amenidade favorável pode ser representada como redução de $c$.

### H4. Amenidades produtivas aumentam a atração quando elevam o retorno esperado

Considere uma amenidade produtiva $a_{it}$ que, como na discussão de Moehling et al., eleve a remuneração nominal esperada. Então:

$$
\frac{\partial V_i}{\partial a_{it}}
=
\frac{\delta^t}{p_{it}}
\frac{\partial \mathbb E(w^{(s)}_{it})}{\partial a_{it}}
>0
$$

sob a condição

$$
\frac{\partial \mathbb E(w^{(s)}_{it})}{\partial a_{it}}>0.
$$

Reinhardt dá conteúdo ao mecanismo produtivo, enquanto Roback mostra que amenidades produtivas também podem ser capitalizadas em salários e aluguéis. O sinal positivo é, portanto, condicional ao efeito da característica sobre o retorno esperado.

### H5. Mais tempo de trabalho reduz lazer, mas o efeito total pode ser ambíguo

Da restrição de tempo de Reinhardt,

$$
R=\bar H-H.
$$

Mantidos os demais argumentos da utilidade constantes e supondo $U_R>0$:

$$
\left.
\frac{\partial U}{\partial H}
\right|_{Y,L,D}
=-U_R<0.
$$

Essa é a desutilidade do tempo de trabalho pelo canal do lazer. O efeito total de $H$ não é necessariamente negativo, pois horas adicionais também podem elevar produção, renda ou a contribuição percebida para a comunidade. Reinhardt não impõe uma forma quadrática nem fixa a magnitude desses canais.

### H6. Condições produtivas têm efeito positivo apenas sob canais especificados

Na função de produção de Reinhardt, horas, pessoal auxiliar e insumos não laborais determinam $q$. O modelo permite formular a hipótese de que melhores condições produtivas elevem o valor da opção quando:

- aumentam a renda valorizada pelo médico;
- reduzem o tempo necessário para determinado nível de produção; ou
- elevam uma dimensão da assistência que o médico valoriza.

Sem uma dessas ligações e sem hipóteses sobre as derivadas de $U$ e de $f$, não há sinal incondicional da característica produtiva sobre a escolha locacional.

### H7. Necessidade assistencial só gera propósito sob preferências compatíveis

Como $D$ entra diretamente na utilidade de Reinhardt, uma melhora na dimensão representada por $D$ aumenta utilidade apenas sob a hipótese de que $U_D>0$, dada a codificação adotada. Necessidade local elevada, isoladamente, não prova que todos os médicos obtenham maior utilidade da opção. A hipótese relevante envolve a interação entre necessidade assistencial e preferências do médico.

### H8. Retornos futuros positivos são descontados

Na soma intertemporal de Moehling et al., um retorno positivo no período $t$ recebe peso $\delta^t$. Se $0<\delta<1$, benefícios mais distantes têm menor peso. Assim, oportunidades que elevem retornos profissionais futuros devem aumentar o valor da opção, mas menos quanto mais distante estiver sua realização.

### H9. O efeito total do IVS é teoricamente ambíguo

Como o IVS pode estar relacionado simultaneamente a remuneração, preços, amenidades, condições produtivas e necessidade assistencial, os modelos não determinam um único sinal para seu efeito total sobre utilidade. Um sinal líquido exige conhecer a intensidade e a direção de cada canal.

Essa ambiguidade é uma hipótese teórica relevante, não uma falha do modelo. Ela impede que vulnerabilidade seja tratada automaticamente como desamenidade, propósito ou precariedade produtiva.

## 9. O que as equações autorizam sobre forma funcional

Na equação de Moehling et al., a remuneração real esperada entra linearmente e $c$ entra de forma aditiva. Essa é a fundamentação publicada para usar o valor real da remuneração em nível como benchmark.

Reinhardt escreve uma função de utilidade e uma função de produção genéricas. Roback também mantém genéricas a utilidade do trabalhador e a função de custo da firma. Esses dois trabalhos identificam os argumentos relevantes e suas relações, mas não escolhem entre forma linear, logarítmica, CRRA ou exponencial.

Portanto, as equações selecionadas não autorizam atribuir a Reinhardt ou Roback uma curvatura que os autores não especificaram. Qualquer hipótese adicional sobre utilidade marginal decrescente da renda, custo convexo das horas ou retornos decrescentes dos insumos exigiria outro fundamento teórico.

Também é necessário distinguir:

- **predições diretas**, como o sinal da remuneração real, do nível de preços e de $c$ na equação de Moehling et al.;
- **predições condicionais**, como o efeito das condições produtivas ou da necessidade assistencial;
- **efeitos teoricamente ambíguos**, como o efeito total do IVS.

## 10. Referências

- **Moehling, C. M.; Niemesh, G. T.; Thomasson, M. A.; Treber, J. (2020).** [*Medical Education Reforms and the Origins of the Rural Physician Shortage*](https://doi.org/10.1007/s11698-019-00187-w) ([manuscrito dos autores](https://niemesgt.github.io/files/MoehlingNiemeshThomassonTreber2019.pdf)).
- **Reinhardt, U. E. (1975).** [*Health Manpower Planning in a Market Context: The Case of Physician Manpower*](https://pure.iiasa.ac.at/213/1/XB-75-001.pdf), em N. T. J. Bailey e M. Thompson (eds.), *Systems Aspects of Health Planning*, pp. 131–162.
- **Roback, J. (1982).** [*Wages, Rents, and the Quality of Life*](https://doi.org/10.1086/261120) ([PDF](https://www.nathanschiff.com/webdocs/grad_urban/urban_papers/Roback_JPE_1982.pdf)).
