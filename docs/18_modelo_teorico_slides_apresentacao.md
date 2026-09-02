# 18. Sistema de Equações Teóricas Microeconômicas para Apresentação (Slides)

> **Documento Teórico de Referência para Apresentações e Defesas**  
> **Projeto:** Avaliação de Impacto e Economia da Saúde — Programa Mais Médicos Especialistas (PMM-E / Lei nº 15.233/2025)  
> **Base Canônica:** Fundamentação Teórica Consolidada em [Doc 17](file:///c:/Users/camil/Desktop/Kauã/Insper/impact-eval-health-econ-pmme/docs/17_fundamentacao_teorica_formacao_utilidade_regressores.md)  
> **Finalidade:** Fornecer estrutura visual e roteiro de fala para defesa da fundamentação microeconômica em 3 camadas complementares (Moehling et al. $\rightarrow$ Roback $\rightarrow$ Reinhardt $\rightarrow$ Hipóteses H1–H9).  
> **Data de Consolidação:** 31 de agosto de 2026  

---

## 1. Estrutura dos Slides Teóricos: Arquitetura em Três Camadas

```
====================================================================================================
               FUNDAMENTAÇÃO TEÓRICA MICROECONÔMICA DO PMM-E (SLIDES ACADÊMICOS)
====================================================================================================
```

### [Slide 1 / Bloco 1] O Problema Central de Escolha Locacional Intertemporal
*(Paper Canônico: Moehling, Niemesh, Thomasson & Treber, 2020, p. 187)*

$$
i^* = \arg\max_{i \in \mathcal{I}} \left\{ \sum_t \delta^t \left[ \frac{\mathbb{E}\left(w^{(s)}_{it}\right)}{p_{it}} - c^{(s)}_{it} \right] \right\}
$$

* **Componentes Teóricos:**
  * $\frac{\mathbb{E}(w^{(s)}_{it})}{p_{it}}$: **Remuneração real esperada** do especialista do tipo $s$ deflacionada pelo nível de preços local $p_{it}$ (Benchmark linear em nível real);
  * $c^{(s)}_{it}$: **Custos e desamenidades de consumo** da localidade (distância da família, transporte e opções urbanas);
  * $\delta^t \in (0, 1)$: **Fator de desconto intertemporal**, capturando o valor futuro da formação e titulação;
  * **Amenidades Produtivas:** Equipamentos e capital hospitalar entram em forma reduzida elevando o retorno esperado $\mathbb{E}(w)$.

---

### [Slide 2 / Bloco 2] Equilíbrio Espacial e Preços Hedônicos
*(Paper Canônico: Roback, 1982, Journal of Political Economy, pp. 1257–1278)*

1. **Livre Mobilidade do Trabalhador:**
   $$V(w_m, r_m; s_m) = k$$
2. **Custo Unitário da Firma / Estabelecimento:**
   $$C(w_m, r_m; s_m) = 1$$
3. **Mecanismo de Capitalização:**  
   Amenidades de consumo elevam a utilidade direta (permitindo salários nominais menores e aluguéis $r_m$ maiores); amenidades produtivas reduzem custos da firma (viabilizando salários nominais maiores).

---

### [Slide 3 / Bloco 3] Microfundamentação da Prática Médica e Alocação de Tempo
*(Paper Canônico: Reinhardt, 1975, Systems Aspects of Health Planning, pp. 131–162)*

1. **Função de Utilidade:** $U = U(R, Y, L, D; \mathbf{Z})$ com restrição de tempo $\bar{H} = R + H$;
2. **Função de Produção Médica Explícita:** $q = f(H, L, K; \boldsymbol{\Omega})$;
3. **Renda Líquida e Lucro:** $Y = [1 - t(\pi + I)](\pi + I)$ onde $\pi = p q - w L - r K$;
4. **Propósito e Responsabilidade Social:** $D$ mensura o compromisso comunitário do médico, gerando ganho de bem-estar se $U_D > 0$.

---

### [Slide 4 / Bloco 4] Síntese Estrutural e as 9 Hipóteses Testáveis

```
+---------------------------------------------------------------------------------------------------+
| H1: Remuneração Real (+)                   | dV/dE(w) = delta^t / p_it > 0 (Benchmark linear)     |
| H2: Nível de Preços Local (-)              | dV/dp = -delta^t * E(w) / p^2 < 0                    |
| H3: Desamenidades e Isolamento (-)         | dV/dc = -delta^t < 0                                 |
| H4: Amenidades Produtivas (+)              | dV/da = (delta^t / p) * [dE(w)/da] > 0               |
| H5: Carga Horária e Lazer (-)              | dU/dH |_(Y,L,D) = -U_R < 0                           |
| H6: Capital Clínico e Equipe Auxiliar (+)  | dq/dK > 0, dq/dL > 0 (expansão da capacidade CNES)   |
| H7: Propósito Assistencial Social (+)      | dU/dD = U_D > 0 (condicional a preferências pró-SUS) |
| H8: Desconto Temporal da Titulação         | Peso delta^t decrescente com a distância do tempo t  |
| H9: Ambiguidade Teórica do IVS Total       | Efeito líquido depende do balanço Bolsa vs. Desamen. |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Roteiro de Fala para a Apresentação dos Slides (Script Acadêmico)

1. *"A decisão de alocação espacial do especialista é modelada rigorosamente a partir de Moehling et al. (2020), no qual o médico escolhe o município que maximiza o valor presente da remuneração real esperada líquida de desamenidades ($V_i = \sum_t \delta^t [\mathbb{E}(w)/p - c]$)."*
2. *"Para dar conteúdo estrutural aos canais em forma reduzida, complementamos o arcabouço com Roback (1982) — que explica a capitalização espacial em aluguéis e salários — e Reinhardt (1975) — que explicita a função de produção médica ($q=f(H,L,K)$), a alocação de tempo entre trabalho e lazer e a motivação assistencial ($D$)."*
3. *"Essa arquitetura teórica estabelece como benchmark a resposta linear à remuneração real e demonstra por que o efeito líquido do IVS é teoricamente ambíguo: o IVS eleva a bolsa federal, mas correlaciona-se com desamenidades urbanas e déficit de capital físico. Por isso, a identificação empírica via RDD nos cutoffs de IVS e modelos de duração é essencial."*

