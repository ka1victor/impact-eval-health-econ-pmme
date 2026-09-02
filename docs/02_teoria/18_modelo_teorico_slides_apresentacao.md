# 18. Modelo microeconômico para apresentação

> **Classificação:** síntese da teoria, sem evidência empírica<br>
> **Base canônica:** [documento 17](17_fundamentacao_teorica_formacao_utilidade_regressores.md)<br>
> **Atualização:** 2 de setembro de 2026

## Slide 1 — Núcleo original e adaptação

Moehling et al. (2020, eq. 1):

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

Adaptação mínima ao PMM-E:

```math
V_{rm}^{(s,0)}
=
\sum_t\delta^t
\left[
\frac{
\mathbb{E}\!\left(w_{rmt}^{(s)}\mid B_m(IVS_m)\right)
}{p_{mt}}
-c_0^{(s)}(IVS_m)
\right]
+\varepsilon_{rm}.
```

- A bolsa federal é fixa em relação à produção e compõe a remuneração esperada.
- $c_0(IVS)$ é a parcela latente em forma reduzida do custo locacional líquido.
- Não se impõe o sinal de $c_0'(IVS)$: desvantagens de infraestrutura competem com oportunidades de impacto social.

## Slide 2 — O que cada complemento abre dentro de $c$

Equações originais da literatura:

```math
V(w_m, r_m; s_m) = \bar{u},
\qquad
u_{nio}^{RRH}
=
\frac{z_{nio}B_n w_i}
{\kappa_{ni}Q_n^{\,1-\beta_R}}.
```

```math
U^{CM}(q,R)
=
R-C(q)+\beta_PV_P(q),
\qquad
q = f(H, L, K; \Omega).
```

```math
u_F^{BB}
=
w_F-\frac{1}{2}\theta x_F^2,
\qquad
u_N^{BB}
=
w_N-\frac{1}{2}\theta x_N^2+\gamma.
```

| Dado empírico adicional | Parcela explicitada | Artigos de fundamentação original |
|---|---|---|
| Origem, graduação ou residência anterior | $c^{\text{dist}}_{rm} = \phi_d(d_{rm})$ | Moehling et al. (2020); Sivey et al. (2012) |
| Preços de moradia, aluguéis e amenidades | $c^{\text{espacial}}_m = (1-\beta)\ln Q_m - \ln B_m$ | Roback (1982); Redding e Rossi-Hansberg (2017) |
| Cuidado médico e insumos da unidade | $c^{\text{clínico}} = C(q; K_m) - \beta_PV_P(q)$ | Choné e Ma (2011); Reinhardt (1975) |
| Trajetória e motivação pró-social | $-g^{\text{missão}} = -\gamma_r\mu_m$ | Barigozzi e Burani (2016) |

## Slide 3 — Decomposição estrutural simplificada

```math
c_{rmt}^{(s)}
=
c_0^{(s)}(IVS_m)
+ c^{\text{dist}}_{rm}
+ c^{\text{espacial}}_{m}
+ c^{\text{clínico}}_{rmt}
- g^{\text{missão}}_{rm}.
```

- Cada termo microfundamenta analiticamente uma camada observável do custo de viver e praticar medicina no local.
- Quando uma dimensão é observada e mensurada, ela substitui parte da variância de $c_0$, evitando dupla contagem.
- Reinhardt fundamenta a infraestrutura ($K_m$) e equipe ($L_m$) como insumos que deslocam o custo de esforço clínico $C(q)$.

## Slide 4 — Versão final integrada e regra de colapso

```math
V_{rm}^{(s)}
=
\sum_t\delta^t
\left[
\frac{
\mathbb{E}\!\left(w_{rmt}^{(s)}\mid B_m(IVS_m)\right)
}{p_{mt}}
-c_{rmt}^{(s)}
\right]
+\varepsilon_{rm},
\qquad
m_r^*
\in
\arg\max_{m \in \mathcal{M} \cup \{0\}}
\;V_{rm}^{(s)}.
```

- **Propriedade de colapso empírico:** sem microdados adicionais, todos os termos específicos permanecem absorvidos em $c_0(IVS_m)$, retornando identicamente ao modelo básico.
- Não observamos diretamente $c$ ou $V$; o modelo fornece a estrutura teórica para estimar inscrição, homologação, alocação e sobrevivência no CNES aos 6 e 12 meses.
- Evidência empírica aplicada (Diamond 2016; Costa, Nunes e Sanches 2024) catalogada no [documento 19](../03_literatura_empirica/19_literatura_empirica_escolha_locacional_medicos.md).
