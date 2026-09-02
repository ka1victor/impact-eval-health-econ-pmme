# 17. Fundamentação teórica da escolha locacional médica

> **Classificação:** literatura teórica e modelo microeconômico autoral<br>
> **Status:** documento teórico canônico<br>
> **Atualização:** 2 de setembro de 2026

---

## 1. Modelo principal: escolha locacional em Moehling et al. (2020)

Moehling et al. (2020, eq. 1) modelam a distribuição espacial de médicos por meio da maximização intertemporal dos retornos líquidos esperados de cada localidade:

```math
\arg\max_{i \in I}\;U(\omega_i)
=
\arg\max_{i \in I}
\sum_t\delta^t
\left[
\frac{\mathbb{E}\!\left(w_{it}^{(s)}\right)}{p_{it}}
- c_{it}^{(s)}
\right].
```

- $i \in I$: localidade de atuação (município ou condado);
- $t$ e $\delta \in (0,1)$: períodos de tempo e fator de desconto intertemporal;
- $s$: especialidade ou qualificação médica;
- $w_{it}^{(s)}$: rendimento nominal auferido na localidade;
- $p_{it}$: nível de preços local (custo de vida);
- $c_{it}^{(s)}$: custo locacional líquido não pecuniário (amenidades, moradia, distância familiar e condições de trabalho).

### Adaptação ao PMM-E

Para a avaliação do Programa Mais Médicos Especialistas (Lei nº 15.233/2025), o médico $r$ escolhe o município $m \in \mathcal{M}$ (ou a opção externa de não adesão, $0$) resolvendo:

```math
m_r^* \in \arg\max_{m \in \mathcal{M} \cup \{0\}} V_{rm}^{(s)}.
```

A bolsa federal é pré-fixada pelo Índice de Vulnerabilidade Social do município, $B_m(IVS_m)$, entrando diretamente na remuneração esperada $w_{rmt}^{(s)}$. Na especificação basal (sem microdados granulares do médico ou da unidade de saúde), a utilidade esperada é expressa em forma reduzida:

```math
V_{rm}^{(s,0)}
=
\sum_t\delta^t
\left[
\frac{\mathbb{E}\!\left(w_{rmt}^{(s)}\mid B_m(IVS_m)\right)}{p_{mt}}
- c_0^{(s)}(IVS_m)
\right]
+\varepsilon_{rm}.
```

- $c_0^{(s)}(IVS_m)$ é o custo locacional líquido latente associado ao município, resumindo desvantagens e amenidades não observadas.
- $\varepsilon_{rm}$ é o choque idiossincrático de preferência.
- O sinal de $c_0'(IVS)$ não é imposto: maior vulnerabilidade pode encarecer o exercício profissional (pior infraestrutura), mas também atrair médicos vocacionados (maior utilidade social).

---

## 2. Complementos teóricos: abrindo o custo locacional

A literatura microeconômica permite abrir as camadas que compõem o custo locacional $c_{it}^{(s)}$. Cada bloco abaixo traz a formulação original e seu papel conceitual:

### 2.1. Distância e raízes locais: Moehling et al. (2020) e Sivey et al. (2012)

Moehling et al. (2020) destacam a proximidade familiar como determinante central de $c$, e Sivey et al. (2012) mostram que médicos exigem compensações substanciais para atuar longe de suas origens. Havendo dados de nascimento, formação ou residência prévia:

```math
c^{\text{dist}}_{rm} = \phi_d(d_{rm}), \qquad \phi_d' > 0,
```

em que $d_{rm}$ é a distância física ou tempo de deslocamento entre a origem do médico $r$ e o município $m$.

### 2.2. Equilíbrio espacial e amenidades: Roback (1982) e Redding & Rossi-Hansberg (2017)

Roback (1982, eq. 1-2) estabelece que desvantagens territoriais exigem salários nominais maiores ($w_m$) ou aluguéis menores ($r_m$) para manter a utilidade de equilíbrio constante:

```math
V(w_m, r_m; s_m) = \bar{u}
\implies
\left. \frac{dw}{ds} \right|_{dV=0} < 0,
\quad
\left. \frac{dr}{ds} \right|_{dV=0} > 0.
```

Redding e Rossi-Hansberg (2017, eq. 24) modernizam essa relação com escolha discreta e custos de transporte:

```math
u_{nio} = \frac{z_{nio}B_n w_i}{\kappa_{ni}Q_n^{\,1-\beta_R}}
\implies
c^{\text{espacial}}_m \approx (1-\beta_R)\ln Q_m - \ln B_m + \ln\kappa_{rm},
```

em que $Q_m$ é o preço da moradia local, $B_m$ são as amenidades e $\kappa_{rm}$ é o custo de deslocamento pendular.

### 2.3. Custo da prática e tecnologia médica: Choné & Ma (2011) e Reinhardt (1975)

Choné e Ma (2011, eq. 1) formalizam a utilidade médica sob agência e altruísmo clínico:

```math
U^{CM}(q, R) = R - C(q) + \beta_P V_P(q),
```

em que $R$ é a remuneração, $C(q)$ é o custo de esforço de atender $q$ pacientes, $V_P(q)$ é o benefício do paciente e $\beta_P \ge 0$ é o grau de altruísmo médico.

Pela tecnologia de produção de Reinhardt (1975), $q = f(H, L, K)$, em que $K$ é a infraestrutura clínica e $L$ a equipe de apoio. Invertendo a função, o custo de esforço clínico líquido é:

```math
c^{\text{clínico}}_{rmt} = C(q_{rmt}; K_m, L_m) - \beta_{P,r} V_P(q_{rmt}).
```

Postos com infraestrutura precária ($K_m$ baixo) elevam o custo de esforço do médico e reduzem o retorno em saúde.

### 2.4. Motivação intrínseca e missão pública: Barigozzi & Burani (2016)

Barigozzi e Burani (2016, eq. 1-2) comparam o profissional em hospitais com fins lucrativos ($F$) versus instituições orientadas por missão pública ($N$):

```math
u_F = w_F - \frac{1}{2}\theta x^2,
\qquad
u_N = w_N - \frac{1}{2}\theta x^2 + \gamma,
```

em que $\gamma > 0$ é o prêmio intrínseco de atuar em uma organização engajada com uma causa social. No PMM-E, médicos vocacionados auferem um ganho não monetário de missão que atua como atenuante do custo territorial:

```math
g^{\text{missão}}_{rm} = \gamma_r \mu_m.
```

---

## 3. Modelo integrado simplificado

A conexão entre o modelo principal e os complementos é direta: os complementos não concorrem com Moehling, mas fornecem a **microfundamentação estrutural do custo locacional líquido** $c_{rmt}^{(s)}$.

Na especificação expandida, o custo locacional decompõe-se de forma aditiva:

```math
c_{rmt}^{(s)}
=
c_0^{(s)}(IVS_m)
+ c^{\text{dist}}_{rm}
+ c^{\text{espacial}}_{m}
+ c^{\text{clínico}}_{rmt}
- g^{\text{missão}}_{rm}.
```

Substituindo essa decomposição na função de utilidade de Moehling et al. (2020):

```math
V_{rm}^{(s)}
=
\sum_t\delta^t
\left[
\frac{\mathbb{E}\!\left(w_{rmt}^{(s)}\mid B_m(IVS_m)\right)}{p_{mt}}
- c_{rmt}^{(s)}
\right]
+\varepsilon_{rm},
\qquad
m_r^* \in \arg\max_{m \in \mathcal{M} \cup \{0\}} V_{rm}^{(s)}.
```

### Regra de colapso empírico

- **Sem microdados adicionais:** todos os termos granulares permanecem absorvidos em $c_0^{(s)}(IVS_m)$, recaindo de forma exata e elegante no modelo basal.
- **Com microdados adicionais:** cada variável mensurada substitui parte da variância de $c_0$, tornando o resíduo mais puro e evitando qualquer dupla contagem.

---

## 4. Regra prática de correspondência empírica

| Dados empíricos disponíveis | Parcela explicitada em $c_{rmt}$ | Fundamentação teórica |
|---|---|---|
| Apenas bolsa federal e IVS | Nenhuma: $c_{rmt} = c_0(IVS_m)$ | Moehling et al. (2020) |
| Origem, graduação ou residência prévia | $c^{\text{dist}}_{rm} = \phi_d(d_{rm})$ | Moehling et al. (2020); Sivey et al. (2012) |
| Preços de moradia, aluguéis ou amenidades | $c^{\text{espacial}}_m \approx (1-\beta)\ln Q_m - \ln B_m$ | Roback (1982); Redding e Rossi-Hansberg (2017) |
| Produção e infraestrutura da unidade | $c^{\text{clínico}} = C(q; K_m) - \beta_P V_P(q)$ | Choné e Ma (2011); Reinhardt (1975) |
| Trajetória no SUS ou motivação pró-social | $-g^{\text{missão}}_{rm} = -\gamma_r \mu_m$ | Barigozzi e Burani (2016) |

A literatura empírica aplicada (e.g., Diamond, 2016; Costa, Nunes e Sanches, 2024) fornece estimativas para calibrar essas elasticidades, catalogada no [documento 19](../03_literatura_empirica/19_literatura_empirica_escolha_locacional_medicos.md).

---

## 5. Referências

- Barigozzi, F.; Burani, N. (2016). [*Competition and Screening with Motivated Health Professionals*](https://doi.org/10.1016/j.jhealeco.2016.06.003). **Journal of Health Economics**, 50, 358--371.
- Choné, P.; Ma, C.-T. A. (2011). [*Optimal Health Care Contract under Physician Agency*](https://people.bu.edu/ma/CHONE-MA_Annals2011.pdf). **Annals of Economics and Statistics**, 101/102, 229--256.
- Moehling, C. M.; Niemesh, G. T.; Thomasson, M. A.; Treber, J. (2020). [*Medical Education Reforms and the Origins of the Rural Physician Shortage*](https://doi.org/10.1007/s11698-019-00187-w). **Cliometrica**, 14, 181--225.
- Redding, S. J.; Rossi-Hansberg, E. (2017). [*Quantitative Spatial Economics*](https://doi.org/10.1146/annurev-economics-063016-103713). **Annual Review of Economics**, 9, 21--58.
- Reinhardt, U. E. (1975). *Physician Productivity and the Demand for Health Manpower: An Economic Analysis*. Ballinger Publishing Company.
- Roback, J. (1982). [*Wages, Rents, and the Quality of Life: A Spatial Equilibrium Model*](https://doi.org/10.1086/261120). **Journal of Political Economy**, 90(6), 1257--1278.
- Sivey, P.; Scott, A.; Witt, J.; Joyce, C.; Humphreys, J. (2012). [*Junior Doctors' Preferences for Specialty and Location: A Discrete Choice Experiment*](https://doi.org/10.1016/j.jhealeco.2012.06.002). **Journal of Health Economics**, 31(6), 813--823.

