# 17. Fundamentação teórica da escolha locacional médica

> **Classificação:** literatura teórica e modelo microeconômico autoral<br>
> **Status:** documento teórico canônico<br>
> **Atualização:** 2 de setembro de 2026

## 1. Modelo principal: escolha locacional em Moehling et al.

Moehling et al. (2020, eq. 1) formulam a alocação geográfica de médicos a partir da maximização intertemporal dos retornos líquidos esperados de cada localidade. Na notação original do artigo:

```math
\arg\max_{i \in I}\;U(\omega_i)
=
\arg\max_{i \in I}
\left\{
\sum_t\delta^t
\left[
\frac{\mathbb{E}\!\left(w_{it}^{(s)}\right)}{p_{it}}
-c_{it}^{(s)}
\right]
\right\}.
```

No modelo original:
- $i \in I$ indexa a localidade de atuação (município ou condado);
- $t$ indexa os períodos de exercício profissional e $\delta \in (0,1)$ é a taxa de desconto temporal;
- $s$ é a especialidade ou grupo de qualificação do médico;
- $w_{it}^{(s)}$ é o rendimento nominal auferido na localidade;
- $p_{it}$ é o nível de preços local (custo de vida);
- $c_{it}^{(s)}$ é o custo locacional líquido não pecuniário, que agrega amenidades locais, custos de moradia, preferências pessoais e proximidade geográfica da família.

Amenidades produtivas (como hospitais estruturados e densidade de serviços) afetam primordialmente a capacidade de gerar renda $w$.

### Adaptação canônica ao PMM-E

Para a modelagem do Programa Mais Médicos Especialistas (Lei nº 15.233/2025), adaptamos os indexadores para evitar ambiguidades: indexamos o médico por $r$, o município por $m \in \mathcal{M}$, a especialidade médica por $s$, e a opção externa de não adesão ao programa pelo índice $0$.

A decisão ótima de candidatura e aceitação da vaga é dada por:

```math
m_r^*
\in
\arg\max_{m \in \mathcal{M} \cup \{0\}}
\;V_{rm}^{(s)}.
```

No PMM-E, o valor da bolsa federal é fixado institucionalmente como função do Índice de Vulnerabilidade Social do município, $B_m(IVS_m)$. Como o médico bolsista não recebe pagamento por procedimento ou produção marginal no programa, a bolsa entra diretamente na remuneração esperada $w_{rmt}^{(s)}$.

Na especificação basal mínima (antes da incorporação de variáveis granulares adicionais), a utilidade esperada é expressa em forma reduzida:

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

Nessa versão principal:
- $c_0^{(s)}(IVS_m)$ representa o custo locacional líquido latente associado ao município. Ele sumariza todas as desvantagens e amenidades não observadas de residir e exercer a medicina no local.
- O termo $\varepsilon_{rm}$ capta o choque idiossincrático de preferência do médico pelo município $m$.
- Não se impõe *a priori* que $c_0'(IVS) > 0$. Embora municípios de maior vulnerabilidade apresentem piores amenidades urbanas e carência de infraestrutura (elevando o custo de viver e praticar), eles também oferecem maior oportunidade de impacto social para profissionais vocacionados (reduzindo o custo líquido subjetivo).

Não observamos $V$ ou $c_0$ diretamente nos microdados; o modelo microeconômico fornece a estrutura conceitual para interpretar empiricamente as decisões de inscrição, homologação, alocação e permanência observada aos 6 e 12 meses no CNES.

## 2. Complementos teóricos e suas equações originais

A literatura microeconômica e espacial fornece os fundamentos teóricos para abrir e interpretar os determinantes econômicos que compõem o custo locacional $c_{it}^{(s)}$. A seguir, apresentam-se as formulações clássicas originais.

### 2.1. Proximidade familiar e redes de formação: Moehling et al. (2020) e Sivey et al. (2012)

Moehling et al. (2020) destacam explicitamente que o custo locacional $c_{it}^{(s)}$ incorpora a distância geográfica em relação à família e à rede de apoio pessoal do médico. Sivey et al. (2012) comprovam experimentalmente que médicos juniores exigem remunerações substancialmente maiores para se deslocarem para longe de seus centros de graduação e raízes familiares. 

Havendo dados sobre município de nascimento, estado de formação ou residência anterior, esse componente do custo é formalizado como:

```math
c^{\text{dist}}_{rm} = \phi_d(d_{rm}),
```

em que $d_{rm}$ é a distância física ou de viagem entre a origem/formação do médico $r$ e o município $m$, com $\phi_d' > 0$. Trata-se de uma operacionalização direta da dimensão de proximidade já contida na conceituação original de Moehling.

### 2.2. Equilíbrio espacial e diferenciais compensatórios: Roback (1982)

O modelo seminal de Roback (1982, eq. 1 e 2) estabelece a teoria dos diferenciais salariais compensatórios entre localidades heterogêneas. No equilíbrio espacial, indivíduos com preferências idênticas atingem a mesma utilidade indireta $\bar{u}$ no território:

```math
V(w_m, r_m; s_m) = \bar{u},
```

em que $w_m$ é o salário nominal, $r_m$ é o custo da terra/aluguel residencial no município $m$, e $s_m$ é o vetor de amenidades locais (infraestrutura urbana, segurança, clima). A diferenciação total da utilidade indireta ao longo da curva de indiferença define as taxas de compensação espacial:

```math
\left. \frac{dw}{ds} \right|_{dV=0} = -\frac{V_s}{V_w} < 0,
\qquad
\left. \frac{dr}{ds} \right|_{dV=0} = -\frac{V_s}{V_r} > 0.
```

A intuição de Roback é direta: localidades com desamenidades severas ($s_m$ baixo / alto $IVS$) só atraem trabalhadores se oferecerem salários nominais compensatórios superiores ($w_m$ maior) ou custos de vida/aluguel muito inferiores ($r_m$ reduzido).

### 2.3. Economia espacial quantitativa: Redding e Rossi-Hansberg (2017)

Redding e Rossi-Hansberg (2017, eq. 24) modernizam o arcabouço espacial em modelos de escolha discreta. A utilidade indireta de um indivíduo $o$, residente na localidade $n$ e empregado na localidade $i$, é formulada originalmente como:

```math
u_{nio}
=
\frac{z_{nio}B_n w_i}{\kappa_{ni}Q_n^{\,1-\beta_R}},
```

em que:
- $w_i$ é a remuneração nominal no local de trabalho $i$;
- $B_n$ mensura as amenidades residenciais locais de $n$;
- $Q_n$ é o preço do espaço residencial (custo de moradia);
- $1-\beta_R \in (0,1)$ é a parcela dos gastos do trabalhador destinada à habitação;
- $\kappa_{ni} \ge 1$ representa os custos de deslocamento físico entre residência e trabalho;
- $z_{nio}$ é uma preferência idiossincrática com distribuição de Fréchet.

Tomando o logaritmo natural e isolando a remuneração nominal $\ln w_i$, a parcela espacial do custo locacional expressa-se como:

```math
-\ln u_{nio}
=
-\ln w_i
+
\left[
\ln\kappa_{ni}
+(1-\beta_R)\ln Q_n
-\ln B_n
-\ln z_{nio}
\right].
```

Essa equação microfundamenta como preços de aluguel ($Q_m$), carência de amenidades ($B_m$) e isolamento logístico ($\kappa_{rm}$) somam-se na composição da desutilidade locacional.

### 2.4. Agência médica e altruísmo clínico: Choné e Ma (2011)

Choné e Ma (2011, eq. 1) modelam a utilidade do médico prestador sob contratos de saúde considerando altruísmo e esforço clínico:

```math
U^{CM}(q, R)
=
R - C(q) + \beta_P V_P(q),
```

em que:
- $R$ é a remuneração total recebida pelo profissional;
- $q$ é a quantidade ou intensidade de cuidados médicos prestados;
- $C(q)$ é o custo de esforço clínico do médico para prestar o cuidado ($C' > 0, C'' > 0$);
- $V_P(q)$ é o benefício de saúde auferido pelo paciente ($V_P' > 0, V_P'' \le 0$);
- $\beta_P \ge 0$ é o coeficiente de altruísmo médico em relação ao paciente.

Como o pagamento da bolsa do PMM-E compõe $R$ de forma fixa, a utilidade clínica não remuneratória gerada pelo atendimento médico resume-se a $[C(q) - \beta_P V_P(q)]$.

### 2.5. Função de produção médica e infraestrutura: Reinhardt (1975)

Para conectar o custo de esforço $C(q)$ às condições concretas da unidade de saúde, recorre-se à função de produção de serviços médicos de Reinhardt (1975):

```math
q = f(H, L, K; \Omega),
```

em que $H$ são as horas e esforço clínico do médico, $L$ são os profissionais de enfermagem e apoio técnico, $K$ sintetiza o capital físico instalado (consultórios, equipamentos de diagnóstico e leitos) e $\Omega$ reflete a organização institucional da rede assistencial.

Invertendo a tecnologia de produção para expressar o custo de esforço necessário para produzir $q$:

```math
C(q) = C(q; L_m, K_m, \Omega_m).
```

Em municípios desprovidos de apoio técnico ($L_m$ baixo) ou com infraestrutura precária ($K_m$ reduzido), atender os pacientes exige esforço compensatório maior do médico, elevando $C(q)$ e reduzindo o impacto de saúde $V_P(q)$.

### 2.6. Motivação intrínseca e missão organizacional: Barigozzi e Burani (2016)

Barigozzi e Burani (2016, eq. 1 e 2) modelam a oferta de trabalho médico em hospitais com fins lucrativos ($F$) versus instituições sem fins lucrativos orientadas por missão pública ($N$):

```math
u_F
=
w_F - \frac{1}{2}\theta x_F^2,
```

```math
u_N
=
w_N - \frac{1}{2}\theta x_N^2 + \gamma,
```

em que $w$ é o rendimento, $x$ é o esforço despendido, $\theta > 0$ é o parâmetro de desutilidade do esforço e $\gamma > 0$ é a utilidade intrínseca auferida ao trabalhar em uma organização cuja missão de impacto social o profissional compartilha.

Ao contrário do altruísmo de Choné e Ma (que premia a cura do paciente individual via $q$), o benefício $\gamma$ recompensa o próprio pertencimento a um serviço público voltado a populações necessitadas.

---

## 3. Conexão teórica: como os complementos decompõem o custo locacional

A articulação entre o modelo principal de Moehling et al. (2020) e os complementos teóricos não cria um sistema concorrente ou fragmentado. Pelo contrário: os complementos fornecem a **microfundamentação estrutural do custo locacional líquido** $c_{rmt}^{(s)}$.

No modelo basal de Moehling, o termo $c_{it}^{(s)}$ reúne de forma agregada todas as desvantagens territoriais. Na aplicação empírica ao PMM-E, quando observamos apenas os dados de nível municipal do edital, esse custo agregado é capturado de forma reduzida pelo IVS do município:

```math
c_{rmt}^{(s)} \approx c_0^{(s)}(IVS_m).
```

Esse termo $c_0^{(s)}(IVS_m)$ atua, portanto, como um resíduo latente de vulnerabilidade. Cada literatura complementar permite decompor analiticamente uma camada observável desse resíduo:

1. **Afastamento geográfico ($c^{\text{dist}}_{rm}$):** O distanciamento de raízes familiares e de polos de formação gera custos de transporte e desapego afetivo (Moehling et al., 2020; Sivey et al., 2012).
2. **Moradia e amenidades espaciais ($c^{\text{espacial}}_{m}$):** Custo de vida local, aluguéis e carência de serviços urbanos compõem a desamenidade espacial (Roback, 1982; Redding e Rossi-Hansberg, 2017).
3. **Sobrecarga clínica líquida ($c^{\text{clínico}}_{rmt}$):** O esforço clínico exigido no posto, agravado pela carência de equipamentos e equipe, menos o retorno altruístico de cuidar do paciente, $[C(q; K_m) - \beta_P V_P(q)]$ (Choné e Ma, 2011; Reinhardt, 1975).
4. **Prêmio de missão pública ($g^{\text{missão}}_{rm}$):** A vocação para a saúde pública gera uma satisfação direta ao atuar em comunidades desassistidas, $\gamma_r \mu_m$, atuando como atenuante do custo territorial (Barigozzi e Burani, 2016).

### Versão integrada simplificada

Para manter o modelo parcimonioso e diretamente operacional, evitamos sobrecargas notacionais com vetores de escalonamento ou índices artificiais. O custo locacional líquido expandido é expresso de forma aditiva:

```math
c_{rmt}^{(s)}
=
c_0^{(s)}(IVS_m)
+ c^{\text{dist}}_{rm}
+ c^{\text{espacial}}_{m}
+ \left[ C(q_{rmt}; K_m) - \beta_{P,r} V_P(q_{rmt}) \right]
- \gamma_r \mu_m.
```

Substituindo esse custo decomposto no problema de escolha intertemporal de Moehling et al. (2020), a utilidade esperada da vaga municipal é:

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
-c_{rmt}^{(s)}
\right]
+\varepsilon_{rm},
```

com a regra de escolha locacional ótima:

```math
m_r^*
\in
\arg\max_{m \in \mathcal{M} \cup \{0\}}
\;V_{rm}^{(s)}.
```

### Propriedade de colapso empírico

Essa formulação garante consistência metodológica entre teoria e dados:
- **Modelo empírico basal (sem microdados adicionais):** se as variáveis de trajetória, moradia, equipamentos ou perfil não estiverem disponíveis, todos os termos específicos permanecem contidos dentro de $c_0^{(s)}(IVS_m)$. A equação final colapsa exatamente no modelo principal de Moehling adaptado ao PMM-E.
- **Modelo expandido (com microdados adicionais):** sempre que uma dimensão passa a ser mensurada empiricamente, $c_0$ passa a representar apenas o resíduo estrito não explicado, evitando estritamente qualquer dupla contagem da mesma desvantagem territorial.

---

## 4. Regra prática de correspondência empírica

| Dados empíricos disponíveis | Parcela explicitada em $c_{rmt}$ | Fundamentação teórica original |
|---|---|---|
| Apenas bolsa federal e IVS | Nenhuma: $c_{rmt} = c_0(IVS_m)$ | Moehling et al. (2020) |
| Origem, formação ou residência anterior | $c^{\text{dist}}_{rm} = \phi_d(d_{rm})$ | Moehling et al. (2020); Sivey et al. (2012) |
| Preços de moradia, aluguéis ou amenidades | $c^{\text{espacial}}_m = (1-\beta)\ln Q_m - \ln B_m$ | Roback (1982); Redding e Rossi-Hansberg (2017) |
| Produção ambulatorial e infraestrutura hospitalar | $c^{\text{clínico}} = C(q; K_m) - \beta_P V_P(q)$ | Choné e Ma (2011); Reinhardt (1975) |
| Trajetória no SUS ou motivação pró-social | $-g^{\text{missão}}_{rm} = -\gamma_r \mu_m$ | Barigozzi e Burani (2016) |

A literatura empírica aplicada (e.g., Diamond, 2016; Costa, Nunes e Sanches, 2024) fornece parâmetros para calibragem e ordens de grandeza das elasticidades, estando resenhada no [documento 19](../03_literatura_empirica/19_literatura_empirica_escolha_locacional_medicos.md).

---

## 5. Referências

- Barigozzi, F.; Burani, N. (2016). [*Competition and Screening with Motivated Health Professionals*](https://doi.org/10.1016/j.jhealeco.2016.06.003). **Journal of Health Economics**, 50, 358--371.
- Choné, P.; Ma, C.-T. A. (2011). [*Optimal Health Care Contract under Physician Agency*](https://people.bu.edu/ma/CHONE-MA_Annals2011.pdf). **Annals of Economics and Statistics**, 101/102, 229--256.
- Moehling, C. M.; Niemesh, G. T.; Thomasson, M. A.; Treber, J. (2020). [*Medical Education Reforms and the Origins of the Rural Physician Shortage*](https://doi.org/10.1007/s11698-019-00187-w). **Cliometrica**, 14, 181--225.
- Redding, S. J.; Rossi-Hansberg, E. (2017). [*Quantitative Spatial Economics*](https://doi.org/10.1146/annurev-economics-063016-103713). **Annual Review of Economics**, 9, 21--58.
- Reinhardt, U. E. (1975). *Physician Productivity and the Demand for Health Manpower: An Economic Analysis*. Ballinger Publishing Company.
- Roback, J. (1982). [*Wages, Rents, and the Quality of Life: A Spatial Equilibrium Model*](https://doi.org/10.1086/261120). **Journal of Political Economy**, 90(6), 1257--1278.
- Sivey, P.; Scott, A.; Witt, J.; Joyce, C.; Humphreys, J. (2012). [*Junior Doctors' Preferences for Specialty and Location: A Discrete Choice Experiment*](https://doi.org/10.1016/j.jhealeco.2012.06.002). **Journal of Health Economics**, 31(6), 813--823.

