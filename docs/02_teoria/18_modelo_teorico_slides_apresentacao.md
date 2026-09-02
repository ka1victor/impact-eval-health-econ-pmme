# 18. Modelo microeconômico para apresentação

> **Classificação:** síntese da teoria, sem evidência empírica<br>
> **Base canônica:** [documento 17](17_fundamentacao_teorica_formacao_utilidade_regressores.md)<br>
> **Atualização:** 2 de setembro de 2026

## Slide 1 — Núcleo original e adaptação

Moehling et al. (2020, eq. 1):

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

- A bolsa é fixa em relação à produção e compõe a remuneração esperada.
- $c_0(IVS)$ é a parcela ainda latente do custo locacional.
- Não se impõe o sinal de $c_0'(IVS)$.

## Slide 2 — O que cada complemento abre dentro de $c$

Equações originais:

```math
u_{nio}^{RRH}
=
\frac{z_{nio}B_n w_i}
{\kappa_{ni}Q_n^{\,1-\beta_R}},
\qquad
U^{CM}(q,R)
=
R-C(q)+\beta_PV_P(q).
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

| Dado adicional | Parcela explicitada | Conexão com Moehling |
|---|---|---|
| origem ou residência anterior | $c^d(d)$ | abre proximidade familiar já contida em $c$ |
| preços, amenidades ou deslocamento | $c^S$ | abre o componente espacial de $c$ |
| produção e condições da prática | $c^P=C-\beta_PG$ | abre custo clínico líquido do benefício ao paciente |
| motivação ou congruência de propósito | $-g^M=-\gamma\mu$ | acrescenta missão além do benefício do paciente |

## Slide 3 — Composição antes da versão final

```math
\widetilde c_{rmt}^{(s)}
=
c_0^{(s)}(IVS_m)
+a_d c_{rm}^{d}
+a_S\lambda_S c_{rm}^{S}
+a_P\lambda_P
\left[
C\!\left(q_{rmt};H_{rmt},L_{mt},K_{mt},\Omega_{mt}\right)
-\beta_{P,r}G\!\left(q_{rmt},D_{mt}\right)
\right]
-a_M\lambda_M\gamma_r\mu_m.
```

- $a_k=1$ somente quando a dimensão puder ser construída com dados adequados.
- Ao abrir uma dimensão, $c_0$ vira o resíduo e deixa de contê-la, evitando dupla contagem.
- Reinhardt interpreta $H,L,K,\Omega$ como insumos de produção; eles afetam primeiro $q$.

## Slide 4 — Versão final e escolha

```math
V_{rm}^{(s)}
=
\sum_t\delta^t
\left[
\frac{
\mathbb{E}\!\left(w_{rmt}^{(s)}\mid B_m(IVS_m)\right)
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

Sem dados adicionais, todos os $a_k$ são zero e a equação retorna ao modelo principal. Não observamos diretamente $c$ ou $V$; observamos entrada, alocação, estoque, saída e presença após seis meses.

Diamond e Costa--Nunes--Sanches fornecem evidência empírica complementar, catalogada no [documento 19](../03_literatura_empirica/19_literatura_empirica_escolha_locacional_medicos.md).
