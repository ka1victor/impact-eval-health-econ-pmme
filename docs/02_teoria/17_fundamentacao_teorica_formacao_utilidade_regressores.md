# 17. Fundamentação teórica da escolha locacional médica

> **Classificação:** literatura teórica e modelo microeconômico autoral<br>
> **Status:** documento teórico canônico<br>
> **Atualização:** 2 de setembro de 2026

## 1. Modelo principal: escolha locacional em Moehling et al.

Moehling et al. (2020, eq. 1) partem de uma comparação intertemporal dos retornos de cada localidade. Na notação original do artigo:

```math
\underset{i\in I}{\operatorname{arg\,max}}\;U(\omega_i)
=
\underset{i\in I}{\operatorname{arg\,max}}
\left\{
\sum_t\delta^t
\left[
\frac{\mathbb{E}\!\left(w_{it}^{(s)}\right)}{p_{it}}
-c_{it}^{(s)}
\right]
\right\}.
```

No original, $i$ é a localidade, $t$ é o ano, $s$ é o grupo de qualificação, $w$ é a remuneração nominal, $p$ é o nível de preços e $\delta$ é o fator de desconto. O termo $c$ reúne amenidades e custos de consumo específicos do local, inclusive preferências por áreas rurais ou urbanas e proximidade da família. Amenidades produtivas, como hospitais e laboratórios, afetam primeiro a remuneração nominal esperada.

### Adaptação mínima ao PMM-E

Para evitar que $i$ represente simultaneamente médico e localidade, usamos $r$ para o médico e $m$ para o município. A especialidade é indexada por $s$, e a opção $0$ representa não ocupar a vaga. A regra de escolha passa a ser:

```math
m_r^*
\in
\underset{m\in\mathcal{M}\cup\{0\}}{\operatorname{arg\,max}}
\;V_{rm}^{(s)}.
```

A bolsa anunciada, $B_m(IVS_m)$, compõe a remuneração esperada. Como o médico não recebe por produção, ela entra em $w$ e não como preço marginal de cada atendimento:

```math
V_{rm}^{(s,0)}
=
\sum_t\delta^t
\left[
\frac{
\mathbb{E}\!\left(
w_{rmt}^{(s)}\mid B_m(IVS_m)
\right)
}{p_{mt}}
-c_0^{(s)}(IVS_m)
\right]
+\varepsilon_{rm}.
```

Essa é a versão principal e empiricamente viável antes de obter dados adicionais. O termo $c_0(IVS)$ é um custo locacional líquido em forma reduzida: resume a parte ainda não observada das condições de viver e trabalhar no município.

Não se impõe $c_0'(IVS)>0$. Maior vulnerabilidade pode significar piores amenidades e condições de trabalho, elevando o custo, mas também maior oportunidade de impacto para médicos vocacionados, reduzindo o custo líquido. Não observamos nem regredimos $c_0$ ou $V$ diretamente; eles interpretam os desfechos de entrada, alocação, estoque, saída e presença após seis meses.

## 2. Como os complementos abrem o custo locacional

Cada complemento abaixo substitui uma parte antes latente de $c_0$. Portanto, acrescentar uma medida observável exige redefinir $c_0$ como o resíduo ainda não explicado; não se soma a mesma dimensão duas vezes.

### Proximidade familiar e trajetória anterior

Moehling et al. já incluem proximidade da família entre os atributos de $c$. Se houver origem, local de formação, residência anterior ou rede profissional, essa dimensão pode ser explicitada como:

```math
c_{rm}^{d}=\phi_d(d_{rm}),
```

em que a interpretação de $d_{rm}$ deve seguir exatamente a informação recebida. Distância à terra natal ou à residência anterior é, assim, uma operacionalização direta de Moehling, não uma contribuição que dependa de Roback.

### Preços, amenidades e deslocamento

Redding e Rossi-Hansberg (2017, eq. 24) escrevem a utilidade indireta de uma pessoa $o$, residente em $n$ e empregada em $i$, como:

```math
u_{nio}
=
\frac{z_{nio}B_n w_i}
{\kappa_{ni}Q_n^{\,1-\beta_R}}.
```

Essa é a equação original, apenas com o parâmetro de participação renomeado para $\beta_R$ a fim de não confundi-lo com o peso do benefício do paciente usado adiante. No artigo, $z_{nio}$ é a preferência idiossincrática, $B_n$ representa amenidades residenciais, $w_i$ é o salário, $\kappa_{ni}$ é o custo de deslocamento e $Q_n$ é o preço do espaço residencial.

Tomando logaritmos e separando o salário, obtemos o seguinte índice autoral para a parcela espacial do custo de Moehling:

```math
c_{rm}^{S}
=
\log\kappa_{rm}
+(1-\beta_R)\log Q_m
-\log B_m^{A}
-\log z_{rm}.
```

Usamos $B_m^{A}$ para amenidades e preservamos $B_m(IVS_m)$ para a bolsa. O salário continua no primeiro termo da utilidade principal. O índice de preços $p_{mt}$ e o preço residencial $Q_m$ também não devem representar duas vezes o mesmo custo de moradia. A extensão espacial só entra quando houver medidas compatíveis; Roback (1982) permanece como antecedente da compensação espacial.

### Custo da prática e benefício ao paciente

Choné e Ma (2011) escrevem originalmente a utilidade de agência do médico como:

```math
U^{CM}(q,R)
=
R-C(q)+\beta_P V_P(q).
```

No artigo, $R$ é o pagamento total, $C(q)$ é o custo de prescrever a quantidade $q$, $V_P(q)$ é o benefício do paciente e $\beta_P>0$ é o peso que o médico atribui a esse benefício. Os subscritos $P$ são apenas rótulos nossos para distinguir esse benefício da utilidade locacional $V_{rm}$.

No PMM-E, o pagamento da bolsa é fixo em relação a $q$ e já aparece em $w_{rmt}$. Para evitar dupla contagem, o complemento importa apenas a parte não remuneratória da equação original:

```math
c_{rmt}^{P}
=
C\!\left(q_{rmt};H_{rmt},L_{mt},K_{mt},\Omega_{mt}\right)
-\beta_{P,r}G\!\left(q_{rmt},D_{mt}\right).
```

Essa segunda equação é uma adaptação autoral. $G$ renomeia o benefício do paciente; $H$, $L$, $K$ e $\Omega$ permitem que jornada, equipe, capital e organização da rede desloquem o custo de produzir cuidado.

Reinhardt (1975) continua útil para interpretar esses elementos como insumos de uma tecnologia de produção médica. Eles afetam primeiro $q$ e somente depois $c^P$; não entram automaticamente no custo locacional. Se houver apenas infraestrutura pré-tratamento, o uso mais defensável é testar heterogeneidade da resposta ao programa por essa infraestrutura.

### Missão além do benefício do paciente

Barigozzi e Burani (2016) distinguem a utilidade do trabalhador em um hospital com fins lucrativos, $F$, e em um hospital sem fins lucrativos orientado por missão, $N$. Na formulação original:

```math
u_F
=
w_F-\frac{1}{2}\theta x_F^2,
```

```math
u_N
=
w_N-\frac{1}{2}\theta x_N^2+\gamma.
```

$x$ é esforço, $\theta$ determina o custo de esforço e $\gamma$ é o benefício não monetário de trabalhar na organização cuja missão o profissional compartilha. No modelo de 2016, esse prêmio não depende diretamente do esforço. Isso o distingue tanto do custo de trabalhar quanto do benefício clínico do paciente em Choné e Ma.

Para o PMM-E, a generalização autoral é um encaixe entre motivação individual e missão percebida no posto:

```math
g_{rm}^{M}=\gamma_r\mu_m.
```

Esse termo só deve ser aberto se houver uma medida defensável de motivação, trajetória vocacional ou congruência de missão.

## 3. Versão integrada do modelo

Depois de apresentar as equações originais e seus mapeamentos, o custo locacional expandido pode ser composto como:

```math
\widetilde c_{rmt}^{(s)}
=
c_0^{(s)}(IVS_m)
+a_d\,c_{rm}^{d}
+a_S\lambda_S c_{rm}^{S}
+a_P\lambda_P
\left[
C\!\left(q_{rmt};H_{rmt},L_{mt},K_{mt},\Omega_{mt}\right)
-\beta_{P,r}G\!\left(q_{rmt},D_{mt}\right)
\right]
-a_M\lambda_M\gamma_r\mu_m.
```

Os indicadores $a_k\in\{0,1\}$ registram se a dimensão correspondente pode ser construída com dados adequados; os $\lambda_k$ colocam índices originalmente medidos em escalas diferentes na unidade do custo locacional. Sempre que $a_k=1$, $c_0$ passa a representar apenas o resíduo, excluindo a dimensão aberta.

Substituindo esse custo na estrutura de Moehling, obtemos a versão final:

```math
V_{rm}^{(s)}
=
\sum_t\delta^t
\left[
\frac{
\mathbb{E}\!\left(
w_{rmt}^{(s)}\mid B_m(IVS_m)
\right)
}{p_{mt}}
-\widetilde c_{rmt}^{(s)}
\right]
+\varepsilon_{rm},
\qquad
m_r^*
\in
\underset{m\in\mathcal{M}\cup\{0\}}{\operatorname{arg\,max}}
\;V_{rm}^{(s)}.
```

Sem dados adicionais, $a_d=a_S=a_P=a_M=0$ e a versão final volta exatamente ao modelo principal com $c_0=c(IVS)$. Assim, os complementos tornam o modelo escalável sem prometer regressores inexistentes.

## 4. Regra prática de incorporação

| Dados efetivamente disponíveis | Parcela aberta de $c$ | Fundamentação |
|---|---|---|
| apenas bolsa e IVS | nenhuma: $c_0=c(IVS)$ | Moehling et al. |
| origem, formação ou residência anterior | $c^d(d)$ | proximidade já contida em Moehling |
| preços, moradia, amenidades ou deslocamento | $c^S$ | Redding--Rossi-Hansberg; tradição Roback |
| produção e condições da prática | $c^P=C-\beta_PG$ | Choné--Ma; Reinhardt para a tecnologia |
| motivação ou congruência de propósito | $-g^M=-\gamma\mu$ | Barigozzi--Burani |

Diamond (2016) e Costa, Nunes e Sanches (2024; working paper de 2019) permanecem na [literatura empírica](../03_literatura_empirica/19_literatura_empirica_escolha_locacional_medicos.md). Eles ajudam a escolher medidas e avaliar plausibilidade, mas não substituem as equações originais acima.

## 5. Referências

- Barigozzi, F.; Burani, N. (2016). [*Competition and Screening with Motivated Health Professionals*](https://doi.org/10.1016/j.jhealeco.2016.06.003). **Journal of Health Economics**, 50, 358--371. [Working paper com o modelo](https://amsacta.unibo.it/5354/1/WP1072.pdf).
- Choné, P.; Ma, C.-T. A. (2011). [*Optimal Health Care Contract under Physician Agency*](https://people.bu.edu/ma/CHONE-MA_Annals2011.pdf). **Annals of Economics and Statistics**, 101/102, 229--256.
- Moehling, C. M.; Niemesh, G. T.; Thomasson, M. A.; Treber, J. (2020). [*Medical Education Reforms and the Origins of the Rural Physician Shortage*](https://doi.org/10.1007/s11698-019-00187-w). **Cliometrica**, 14, 181--225. [Manuscrito com a equação](https://niemesgt.github.io/files/MoehlingNiemeshThomassonTreber2019.pdf).
- Redding, S. J.; Rossi-Hansberg, E. (2017). [*Quantitative Spatial Economics*](https://doi.org/10.1146/annurev-economics-063016-103713). **Annual Review of Economics**, 9, 21--58. [Manuscrito com a equação](https://rossihansberg.economics.uchicago.edu/QSE.pdf).
- Reinhardt, U. E. (1975). *Physician Productivity and the Demand for Health Manpower: An Economic Analysis*. Ballinger.
- Roback, J. (1982). [*Wages, Rents, and the Quality of Life*](https://doi.org/10.1086/261120). **Journal of Political Economy**, 90(6), 1257--1278.
