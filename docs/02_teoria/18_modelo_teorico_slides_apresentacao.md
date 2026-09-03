# 18. Modelo microeconômico para apresentação

> **Classificação:** síntese da teoria, sem evidência empírica<br>
> **Base canônica:** [modelo_micro.md](modelo_micro.md)<br>
> **Atualização:** 3 de setembro de 2026

## Slide 1 — Núcleo original e adaptação ao PMM-E

Moehling et al. (2020, eq. 1, p. 184):

```math
\arg\max_{j \in J}\;U(\omega_j)
=
\arg\max_{j \in J}
\sum_t\delta^t
\left[
\frac{\mathbb{E}\!\left(w_{jt}^{(s)}\right)}{p_{jt}}
- c_{jt}^{(s)}
\right].
```

Adaptação ao PMM-E (médico $i$, município $m$, origem $o(i)$):

```math
V_{im}^{(s,0)}
=
\sum_t\delta^t
\left[
\frac{
\mathbb{E}\!\left(w_{imt}^{(s)}\mid B_m(IVS_m)\right)
}{p_{mt}}
- c_0^{(s)}(IVS_m)
\right]
+\varepsilon_{im},
\qquad
m_i^* \in \arg\max_{m \in \mathcal{M} \cup \{0\}} V_{im}^{(s)}.
```

- A bolsa federal $B_m(IVS_m)$ é pré-fixada e compõe a remuneração esperada $w$.
- $c_0(IVS)$ é o custo locacional líquido latente em forma reduzida.

## Slide 2 — Equações originais dos complementos

Redding e Rossi-Hansberg (2017, eq. 24, p. 28):

```math
u_{nio} = \frac{z_{nio}B_n w_i}{\kappa_{ni}Q_n^{\,1-\beta}}
\implies
c^{\text{espacial}}_m = (1-\beta)\ln Q_m - \ln B_m.
```

Choné e Ma (2011, eq. 1, p. 232) e Reinhardt (1975):

```math
U = R - C(q; L_A, K) + \alpha B(q)
\implies
c^{\text{clínico}}_{im} = C(q; L_A, K) - \alpha B(q).
```

## Slide 3 — Derivadas parciais e a questão central de $q$

Derivadas parciais que determinam o custo locacional:
- **Distância da família:** $\frac{\partial c}{\partial \text{dist}} = \phi'(\text{dist}_{im}) > 0$ (Moehling et al., 2020, p. 184).
- **Moradia e amenidades:** $\frac{\partial c}{\partial Q_m} = \frac{1-\beta}{Q_m} > 0$, $\frac{\partial c}{\partial B_m} = -\frac{1}{B_m} < 0$ (Redding e Rossi-Hansberg, 2017, p. 28).
- **Capital e equipe:** $\frac{\partial c}{\partial K} < 0$, $\frac{\partial c}{\partial L_A} < 0$, $\frac{\partial c}{\partial \alpha} = -B(q) < 0$ (Choné e Ma, 2011; Reinhardt, 1975).

**Questão central:** quando atender pacientes eleva a utilidade médica ($\frac{\partial U}{\partial q} > 0$)?
$$\frac{\partial U}{\partial q} = \alpha B'(q) - \frac{\partial C(q; L_A, K)}{\partial q} > 0 \iff \alpha B'(q) > \frac{\partial C}{\partial q}.$$
Ocorre quando o **altruísmo ($\alpha$)** é alto, a **gravidade do paciente ($B'(q)$)** é crítica e a **infraestrutura ($K, L_A$)** reduz o esforço marginal do médico.

## Slide 4 — Dados reais, IVS e modelo canônico operacional

Confronto com os microdados observados:
- Não observamos distância à terra natal, preços locais de aluguel ou esforço individual $q$.
- Observamos para 100% dos municípios a **bolsa federal $B_m(IVS_m)$** e o **IVS 2010 do IPEA**.

Composição do IVS do IPEA (3 sub-índices, 16 indicadores censitários):
1. **Infraestrutura Urbana:** saneamento, lixo e tempo de deslocamento urbano $\to$ capta custos espaciais e amenidades (RRH).
2. **Capital Humano:** mortalidade infantil, mães adolescentes e analfabetismo $\to$ capta carência de saúde (Choné & Ma) e escassez de capital (Reinhardt).
3. **Renda e Trabalho:** extrema pobreza, desemprego e informalidade $\to$ capta dependência do SUS.

**Modelo Canônico Operacional:**
$$c_m = c_0(IVS_m), \qquad V_{im}^{(s)} = \sum_t\delta^t \left[ \frac{\mathbb{E}(w_{imt} \mid B_m)}{p_{mt}} - c_0(IVS_m) \right] + \varepsilon_{im}.$$
