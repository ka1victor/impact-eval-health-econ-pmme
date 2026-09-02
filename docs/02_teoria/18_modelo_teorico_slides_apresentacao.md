# 18. Modelo microeconômico para apresentação

> **Classificação:** síntese da teoria, sem evidência empírica<br>
> **Base canônica:** [documento 17](17_fundamentacao_teorica_formacao_utilidade_regressores.md)<br>
> **Atualização:** 2 de setembro de 2026

## Slide 1 — Demarcação

**Teoria:** Redding e Rossi-Hansberg (2017); Choné e Ma (2011); Barigozzi e Burani (2016).

**Modelo autoral:** combina escolha espacial, agência médica, missão e decisão dinâmica.

**Literatura empírica:** trabalhos que estimam regressões ou modelos estruturais ficam no [documento 19](../03_literatura_empirica/19_literatura_empirica_escolha_locacional_medicos.md), fora da fundamentação das equações.

Roteiro:

> “A teoria fornece primitivas e mecanismos; a literatura empírica documenta magnitudes e fatos; a econometria identifica os efeitos do PMM-E. Não usamos uma regressão como se fosse uma condição microeconômica.”

## Slide 2 — Utilidade espacial

$$
U^{S}_{imt}=A_{mt}C_{imt}^{\alpha}h_{imt}^{1-\alpha},
\qquad
P_{mt}C_{imt}+R_{mt}h_{imt}\leq y^0_{imt}+B_{mt}.
$$

$$
v^{S}_{imt}
=\log A_{mt}+\log(y^0_{imt}+B_{mt})
-\alpha\log P_{mt}-(1-\alpha)\log R_{mt}.
$$

- bolsa e amenidades elevam a atratividade;
- custo de vida e aluguel a reduzem;
- o IVS 2010 determina a regra administrativa, mas não é sinônimo de amenidades.

Roteiro:

> “Redding e Rossi-Hansberg oferecem a formulação espacial moderna. Roback permanece como antecedente histórico, não como a única equação operacional.”

## Slide 3 — Prática médica e missão

$$
u^{P}_{imt}
=b_{mt}q_{imt}
-C(q_{imt},H_{imt};K_{mt},L_{mt},\Omega_{mt})
+\beta_iG(q_{imt},D_{mt}),
$$

$$
u^{BB}_{ij}=w_j(e_{ij})-c(e_{ij};a_i)
+\mathbf 1\{j=M\}\gamma_i e_{ij}.
$$

- Choné e Ma fundamentam o trade-off entre retorno próprio, custo e benefício do paciente;
- Barigozzi e Burani fundamentam salário, esforço, missão e seleção de profissionais de saúde motivados;
- o modelo unificado importa desse bloco somente o prêmio de missão $\gamma_i\mu_m(e)$, evitando duplicar renda e custo;
- os efeitos de jornada, equipe, capital e rede sobre o custo são hipóteses autorais explícitas.

Roteiro:

> “Não atribuímos mais a Reinhardt uma noção moderna de propósito ou um efeito necessariamente favorável da equipe. Esses canais são separados e suas hipóteses são declaradas.”

## Slide 4 — Atração e retenção

$$
u_{imt}=v^{S}_{imt}+u^{P}_{imt}+\gamma_i\mu_m(e_{imt})
-\tau_{im}+\varepsilon_{imt},
$$

$$
V_{imt}=u_{imt}
+\delta\mathbb E_t
\left[\max_n\{V_{in,t+1}-\kappa_{imn,t+1}\}\right].
$$

Entrada:

$$
m^*_{it}\in\arg\max_m V_{imt}.
$$

Permanência:

$$
V_{imt}\geq\max_{n\neq m}\{V_{int}-\kappa_{imn,t}\}.
$$

Roteiro:

> “Atração compara a vaga com a alternativa externa. Retenção compara permanecer com sair depois que o médico já conhece o posto e enfrenta custos de troca.”

## Slide 5 — Hipóteses e identificação

1. bolsa maior tende a elevar atração;
2. custos espaciais elevam a compensação mínima;
3. infraestrutura e equipe podem reduzir o custo de exercer a medicina;
4. missão produz heterogeneidade, não um sinal uniforme do IVS;
5. o efeito total do IVS sobre utilidade é teoricamente ambíguo.

Essas hipóteses motivam os estimandos, mas não impõem sinais aos coeficientes de RDD. As equações de RDD, Cox ou duração pertencem à seção metodológica.
