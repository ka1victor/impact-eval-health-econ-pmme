# 18. Modelo microeconômico para apresentação

> **Classificação:** síntese da teoria, sem evidência empírica<br>
> **Base canônica:** [documento 17](17_fundamentacao_teorica_formacao_utilidade_regressores.md)<br>
> **Atualização:** 2 de setembro de 2026

## Slide 1 — Modelo principal

$$
V_{im}^{(s)}
=
\sum_t\delta^t
\left[
\frac{\mathbb{E}(w_{imt}^{(s)})}{p_{mt}}
-c^{(s)}(IVS_m)
\right]
+\varepsilon_{im},
\qquad
m_i^*\in\arg\max_{m\in\mathcal{M}\cup\{0\}}V_{im}^{(s)}.
$$

- Moehling et al. é o único núcleo do modelo.
- A bolsa é remuneração esperada fixa; não é pagamento por produção clínica.
- $c(IVS)$ é um custo locacional líquido e latente.
- Não se impõe o sinal de $c'(IVS)$.

> “A bolsa tenta compensar o custo locacional associado à vulnerabilidade; o saldo dessa compensação determina a atratividade da vaga.”

## Slide 2 — Complementos, somente se observáveis

$$
\widetilde c_{imt}^{(s)}
=c^{(s)}(IVS_m,d_{im})
+\lambda_Sc^S_{imt}
+\lambda_P\left[C(q_{imt};H_{imt},L_{mt},K_{mt},\Omega_{mt})-\beta_iG(q_{imt},D_{mt})\right]
-\lambda_M\gamma_i\mu_{mt}(e).
$$

| Dado adicional | Complemento direto | Referência |
|---|---|---|
| origem ou residência anterior | distância $d_{im}$ | Moehling et al. |
| preços, moradia ou deslocamento | custo espacial $c^S$ | Redding--Rossi-Hansberg; Roback |
| produção, equipe ou infraestrutura | custo da prática menos benefício ao paciente | Choné--Ma; Reinhardt para $q=f(H,L,K;\Omega)$ |
| medida de propósito ou esforço | missão $-\gamma\mu$ | Barigozzi--Burani |

> “Os complementos refinam o mesmo custo locacional. Sem dados para medi-los, eles não viram regressores nem pilares do modelo estimado.”

## Slide 3 — Leitura empírica

- Não observamos diretamente $c$ ou $V$; observamos entrada, alocação, estoque, saída e presença após seis meses.
- Distância à terra natal operacionaliza proximidade familiar, não um mecanismo espacial independente.
- Infraestrutura e equipe afetam primeiro a produção $q$; com medidas pré-tratamento, podem gerar heterogeneidade da resposta ao incentivo.
- O benefício ao paciente, $\beta G(q,D)$, não é o mesmo que missão, $\gamma\mu(e)$.
- Diamond e Costa--Nunes--Sanches são evidência empírica complementar, catalogada no [documento 19](../03_literatura_empirica/19_literatura_empirica_escolha_locacional_medicos.md).
