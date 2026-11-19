---
title: "Por que médicos escolhem onde atuar?"
subtitle: "Teoria micro da escolha locacional \\\\ PMM-E — Lei 15.233/2025"
author: "Insper — Economia da Saúde"
date: "\\today"
institute: "Moehling et al. (2020) \\;\\; Choné \\& Ma (2011) \\;\\; Reinhardt (1975)"
lang: pt-BR
aspectratio: 169
theme: metropolis
themeoptions: "progressbar=frametitle,numbering=fraction"
header-includes:
  - \usepackage{mathtools,amssymb,booktabs}
---

## O puzzle e o núcleo canônico

Vagas de alto IVS ociosas: que custo latente $\Delta c_0$ a bolsa $\Delta B$ supera?

$$\arg\max_{i \in I}\; U(\omega_i) = \arg\max_{i \in I}\; \Biggl\{ \sum_{t} \delta^{t} \left[ \frac{\mathbb{E}\!\left(w_{it}^{(s)}\right)}{p_{it}} - c_{it}^{(s)} \right] \Biggr\} \quad \text{\footnotesize (Moehling et al.\ 2020, eq.\,1)}$$

:::: columns
::: {.column width="50%"}
\small
**PMM-E:** $V_{im} = \sum_t \delta^t\!\left[\frac{\mathbb{E}(w \mid B_m(\text{IVS}_m))}{p} - c_0(\text{IVS}_m)\right] + \varepsilon_{im}$; bolsa R\$ 10k/15k/20k compõe $w$. Preencher exige $\Delta B / p > \Delta c_0$.
:::
::: {.column width="50%"}
\small
**Subalocação:** capital $w = B + w^{\text{priv}}$ (complementa em 20h) *vs.* interior $w = B$ (colapsa no piso) $\Rightarrow$ $B_{\text{interior}} > B_{\text{capital}}$ pode dar $w_{\text{total}}$ menor.
:::
::::

## Custos: geográfico e laboral

:::: columns
::: {.column width="50%"}
**Geográfico** {\footnotesize (RRH 2017, eq.\,24)}

$$c^{\text{geo}}_{im} = \phi(\text{dist}_{im}) - \gamma A_m + \theta_i^{\text{rural}}$$

\small
$\phi' > 0$ (distância à família dói), $-\gamma < 0$ (amenidade atrai). Limite CNES: sem residência $\Rightarrow$ município do estabelecimento.
:::
::: {.column width="50%"}
**Laboral em U** {\footnotesize (Choné \& Ma 2011, eq.\,1)}

$$c(q) = C(q) - \alpha B(q), \quad c'' \gg 0$$

\small
$C'>0, C''>0$ (cansaço); $B'>0, B''<0$; $\alpha \ge 0$ (altruísmo). Mínimo em $q_{c_{\max}}$ ($C' = \alpha B'$), neutro em $q_{c=0}$ ($C = \alpha B$).

![](figuras/curva_custo_laboral_burnout.png){width="85%"}
:::
::::

## $K$, $L$ e a equação-mestra

:::: columns
::: {.column width="32%"}
\small
**Efeito duplo** (Reinhardt 1975):

$$\frac{\partial c}{\partial K} < 0, \quad \frac{\partial c}{\partial L} < 0$$

$K$ (centro cirúrgico, UTI) e $L$ (equipe) reduzem $C$ e multiplicam $B$. Sem $K$: resolutividade $\to 0$. Cirúrgico exige $K$; clínico tolera posto simples.
:::
::: {.column width="68%"}
\footnotesize

$$\arg\max_{m}\; U_i = \arg\max_{m}\; \sum_t \delta^t \left[ \frac{\mathbb{E}(w_{mt}^{(s)})}{p_{mt}} - c_{im}^{(s)} \right]$$

$$\begin{aligned}
c_{im}^{(s)} &= \underbrace{\phi(\text{dist}_{im}) - \gamma A_m + \theta_i^{\text{rural}}}_{\text{geográfico}} \\
&\quad + \underbrace{C(q_{im}; L_m, K_m, s) - \alpha_i B(q_{im}; L_m, K_m)}_{\text{laboral líquido}}
\end{aligned}$$
:::
::::

## Do latente ao observável — e 4 hipóteses

:::: columns
::: {.column width="42%"}
\small
$c_m = c_0(\text{IVS}_m)$ (IVS 2010, IPEA — 100\% dos municípios): **Infra** $\Rightarrow c \uparrow$; **Cap.\,Humano** $\Rightarrow B' \uparrow$ mas $K \downarrow$; **Renda/Trab.** $\Rightarrow w = B$. Forças opostas: **não** assumir $c_0'(\text{IVS}) > 0$.
:::
::: {.column width="58%"}
\small
1. **H1 — Compensação:** $\Delta B/p > \Delta c_0$? Vacância na Faixa-1 (20k) $\Rightarrow$ custo $>$ R\$ 5k.
2. **H2 — Subalocação:** isolado ($w = B$) $<$ polo ($w > B$), CNES 6/12m.
3. **H3 — Cir.\ $\times$ clín.:** $\left.\frac{\partial \Pr}{\partial \text{IVS}}\right|_{\text{cir.}} \ll \left.\frac{\partial \Pr}{\partial \text{IVS}}\right|_{\text{clín.}}$
4. **H4 — IVS:** infra $\downarrow$ fixação; cap.\,hum.\ atenuado/positivo.
:::
::::

## Takeaway

\begin{block}{Mensagem central}
A bolsa compensa, mas não resolve $K$, $L$ e isolamento.
\end{block}

- Preencher vaga exige $\Delta B / p > \Delta c_0$ — testar na descontinuidade.
- Interior sem mercado privado e sem $K$ afasta cirurgiões primeiro.
- Decompor o IVS evita anulação de efeitos opostos.

\vspace{0.5em}
{\footnotesize
**Refs:** Moehling et al.\ (2020); Choné \& Ma (2011); Redding \& Rossi-Hansberg (2017); Reinhardt (1975); IPEA (2015); Costa--Nunes--Sanches (2024).
}
