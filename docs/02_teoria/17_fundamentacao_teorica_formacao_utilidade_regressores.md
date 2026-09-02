# 17. Fundamentação teórica da escolha locacional médica

> **Classificação:** literatura teórica e modelo microeconômico autoral<br>
> **Status:** documento teórico canônico<br>
> **Atualização:** 2 de setembro de 2026

## 1. Modelo principal

O núcleo é a escolha locacional dinâmica de Moehling et al. (2020):

$$
V_{im}^{(s)}
=
\sum_t \delta^t
\left[
\frac{\mathbb{E}(w_{imt}^{(s)})}{p_{mt}}
-c_{mt}^{(s)}
\right],
\qquad
m_i^*\in\arg\max_{m\in\mathcal{M}\cup\{0\}} V_{im}^{(s)}.
$$

Para o PMM-E, a bolsa anunciada compõe a remuneração esperada; ela não remunera produção clínica marginal. A versão empiricamente parcimoniosa trata o custo locacional como uma forma reduzida da vulnerabilidade administrativa:

$$
c_{mt}^{(s)}=c^{(s)}(IVS_m).
$$

Definindo o incentivo real anunciado como

$$
b_{imt}(IVS_m)
\equiv
\frac{\mathbb{E}\!\left(w_{imt}^{(s)}\mid B_m(IVS_m)\right)}{p_{mt}},
$$

a regra pode ser escrita como

$$
V_{im}^{(s)}
=
\sum_t\delta^t
\left[b_{imt}(IVS_m)-c^{(s)}(IVS_m)\right]
+\varepsilon_{im}.
$$

Não se impõe $c'(IVS)>0$. Maior vulnerabilidade pode elevar o custo de viver e trabalhar no município, mas também pode representar maior oportunidade de impacto para médicos vocacionados. O sinal líquido é uma questão empírica. Nem $c$ nem $V$ são regredidos diretamente: eles interpretam os desfechos observáveis de entrada, alocação, estoque, saída e presença após seis meses.

## 2. Complementos diretos, condicionados aos dados

Os complementos abaixo não substituem o modelo principal. Eles entram somente se houver medida pré-tratamento que permita uma operacionalização honesta.

### Proximidade familiar e trajetória anterior

Se houver origem, residência anterior ou rede profissional observável, ela é uma extensão direta de Moehling, não um canal espacial autônomo:

$$
c_{im}^{(s)}=c^{(s)}(IVS_m,d_{im}),
$$

em que $d_{im}$ mede a distância à família, à residência anterior ou à rede profissional, conforme a informação disponível.

### Componente espacial do custo

Com dados de preços, moradia, amenidades ou fricções de deslocamento, Redding e Rossi-Hansberg (2017) oferecem uma microfundamentação contemporânea para uma parcela de $c$. Uma forma reduzida de sua utilidade indireta é:

$$
u^{S}_{n j o}
=
\frac{z_{n j o}A_n w_j}
{\kappa_{n j}Q_n^{1-\eta}}.
$$

Logo, um índice espacial de custo pode ser definido como

$$
c^{S}_{n j o}
=
\log \kappa_{n j}+(1-\eta)\log Q_n
-\log A_n-\log z_{n j o}.
$$

Esse complemento explica apenas o custo locacional. Salários e preços não devem ser contados novamente quando já aparecem em $b_{imt}$. Roback (1982) permanece como antecedente da tradição de compensação espacial, mas a extensão só é usada se os dados a sustentarem.

### Prática médica e benefício ao paciente

Choné e Ma (2011) formalizam a utilidade da prática como

$$
U^{CM}=R-C(q)+\beta V(q).
$$

Aqui, $R$ é o pagamento total, $C(q)$ é o custo de produzir atendimento e $\beta V(q)$ é o valor atribuído ao benefício do paciente. Como a bolsa do PMM-E é fixa em relação a $q$, a adaptação útil é deslocar o canal de prática para o custo líquido:

$$
c^{P}_{imt}
=C(q_{imt};H_{imt},L_{mt},K_{mt},\Omega_{mt})
-\beta_iG(q_{imt},D_{mt}).
$$

Reinhardt (1975) pode fundamentar a tecnologia de produção,

$$
q_{imt}=f(H_{imt},L_{mt},K_{mt};\Omega_{mt}),
$$

mas seus insumos pertencem primeiro a $q$, e não automaticamente a $c$. Se só houver infraestrutura pré-tratamento, o uso empírico adequado é heterogeneidade da resposta ao programa por $K^{\mathrm{pre}}$, não a estimação direta de $c^P$.

### Missão

Barigozzi e Burani (2016) representam missão na utilidade do profissional como

$$
U^M=w-\frac{\theta e^2}{2}+\gamma e.
$$

No PMM-E, esse mecanismo pode entrar como $g^M_{imt}=\gamma_i\mu_{mt}(e)$: propósito associado ao esforço ou ao local. Ele é distinto de $\beta_iG(q,D)$, que representa o benefício do paciente gerado pelo atendimento.

Juntando apenas os complementos observáveis, uma expansão possível é

$$
\widetilde c_{imt}^{(s)}
=c^{(s)}(IVS_m,d_{im})
+\lambda_Sc^S_{imt}
+\lambda_P\left[C(q_{imt};H_{imt},L_{mt},K_{mt},\Omega_{mt})-\beta_iG(q_{imt},D_{mt})\right]
-\lambda_M\gamma_i\mu_{mt}(e),
$$

substituindo $c_{mt}^{(s)}$ por $\widetilde c_{imt}^{(s)}$ na equação principal de Moehling.

## 3. Regra prática de incorporação

| Dados efetivamente disponíveis | Complemento | Papel teórico |
|---|---|---|
| apenas bolsa e IVS | $c=c(IVS)$ | modelo principal de Moehling |
| origem ou residência anterior | $c=c(IVS,d)$ | proximidade familiar e trajetória |
| preços, moradia ou deslocamento | $c^S$ | Redding--Rossi-Hansberg; tradição Roback |
| produção, equipe ou infraestrutura | $C-\beta G$ ou heterogeneidade por insumos | Choné--Ma; tecnologia de Reinhardt |
| medida de propósito ou esforço | $-\gamma\mu$ | Barigozzi--Burani |

Sem dados para uma extensão, a respectiva referência serve apenas como microfundamentação de componente latente de $c$, e não como pilar de uma especificação estimada.

## 4. Referências

- Barigozzi, F.; Burani, N. (2016). *Competition and Screening in the Market for Health Care Providers*. **Journal of Health Economics**, 47, 85--103. [Working paper](https://ftp.iza.org/dp8468.pdf).
- Choné, P.; Ma, C.-T. A. (2011). *Optimal Health Care Contract under Physician Agency*. **Annals of Economics and Statistics**, 101/102, 229--256. [Texto](https://www.jstor.org/stable/41219166).
- Moehling, C. M.; Niemesh, G. T.; Thomasson, M. A.; Treber, J. (2020). *Medical Education Reforms and the Origins of the Rural Physician Shortage*. **Cliometrica**, 14, 181--225. [Artigo](https://doi.org/10.1007/s11698-019-00187-w).
- Redding, S. J.; Rossi-Hansberg, E. (2017). *Quantitative Spatial Economics*. **Annual Review of Economics**, 9, 21--58. [Artigo](https://doi.org/10.1146/annurev-economics-063016-103713).
- Reinhardt, U. E. (1975). *Physician Productivity and the Demand for Health Manpower*. **Milbank Memorial Fund Quarterly**, 53, 406--423.
- Roback, J. (1982). *Wages, Rents, and the Quality of Life*. **Journal of Political Economy**, 90, 1257--1278.
