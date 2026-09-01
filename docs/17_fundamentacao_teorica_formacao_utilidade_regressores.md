# 17. Base microeconômica da escolha locacional médica

> **Escopo:** equações originais dos trabalhos selecionados e relação conceitual entre elas
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

## 6. O que as equações autorizam sobre forma funcional

Na equação de Moehling et al., a remuneração real esperada entra linearmente e $c$ entra de forma aditiva. Essa é a fundamentação publicada para usar o valor real da remuneração em nível como benchmark.

Reinhardt escreve uma função de utilidade e uma função de produção genéricas. Roback também mantém genéricas a utilidade do trabalhador e a função de custo da firma. Esses dois trabalhos identificam os argumentos relevantes e suas relações, mas não escolhem entre forma linear, logarítmica, CRRA ou exponencial.

Portanto, as equações selecionadas não autorizam atribuir a Reinhardt ou Roback uma curvatura que os autores não especificaram. Qualquer hipótese adicional sobre utilidade marginal decrescente da renda, custo convexo das horas ou retornos decrescentes dos insumos exigiria outro fundamento teórico.

## 7. Referências

- **Moehling, C. M.; Niemesh, G. T.; Thomasson, M. A.; Treber, J. (2020).** [*Medical Education Reforms and the Origins of the Rural Physician Shortage*](https://doi.org/10.1007/s11698-019-00187-w) ([manuscrito dos autores](https://niemesgt.github.io/files/MoehlingNiemeshThomassonTreber2019.pdf)).
- **Reinhardt, U. E. (1975).** [*Health Manpower Planning in a Market Context: The Case of Physician Manpower*](https://pure.iiasa.ac.at/213/1/XB-75-001.pdf), em N. T. J. Bailey e M. Thompson (eds.), *Systems Aspects of Health Planning*, pp. 131–162.
- **Roback, J. (1982).** [*Wages, Rents, and the Quality of Life*](https://doi.org/10.1086/261120) ([PDF](https://www.nathanschiff.com/webdocs/grad_urban/urban_papers/Roback_JPE_1982.pdf)).
