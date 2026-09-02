# 18. Sistema de Equações Teóricas Microeconômicas para Apresentação (Slides)

> **Documento Teórico de Referência para Apresentações e Defesas**  
> **Projeto:** Avaliação de Impacto e Economia da Saúde — Programa Mais Médicos Especialistas (PMM-E / Lei nº 15.233/2025)  
> **Base Canônica:** Fundamentação Teórica Consolidada em [Doc 17](file:///c:/Users/camil/Desktop/Kauã/Insper/impact-eval-health-econ-pmme/docs/17_fundamentacao_teorica_formacao_utilidade_regressores.md)  
> **Finalidade:** Fornecer estrutura visual e roteiro de fala para defesa do Modelo Microeconômico Unificado (Moehling como núcleo com $c(R, L, D, \mathbf{Z}; r, s)$ microfundamentado por Roback e Reinhardt).  
> **Data de Consolidação:** 31 de agosto de 2026  

---

## 1. Estrutura dos Slides Teóricos: Modelo Unificado

### [Slide 1] O Ponto de Partida: O Problema Intertemporal de Moehling et al. (2020)

$$
i^* = \arg\max_{i \in \mathcal{I}} \sum_t \delta^t \left[ \frac{\mathbb{E}(w^{(s)}_{it})}{p_{it}} - c^{(s)}_{it} \right]
$$

* **O que $c$ representa em Moehling et al.?**  
  Um termo agregado em forma reduzida para custos e desamenidades de consumo (estilo de vida rural/urbano e proximidade da família), enquanto amenidades produtivas deslocam $\mathbb{E}(w)$.
* **A Limitação:** Moehling et al. não abrem a "caixa-preta" de $c$ (carga de trabalho, equipe, aluguel, infraestrutura e vocação pública).

---

### [Slide 2] Abrindo a Caixa de $c$: A Microfundamentação Estrutural
*(Contribuições Teóricas de Roback 1982 e Reinhardt 1975)*

$$
c^{(s)}_{it} = c\Big(R_{it}, L_{it}, D_{it}, \mathbf{Z}_i; \; r_{it}, s_{it}\Big)
$$

* **Do Bloco de Reinhardt (1975) — Prática Médica e Alocação de Tempo:**
  * $R = \bar{H} - H$: perda de lazer e excesso de jornada elevam a desutilidade ($\frac{\partial c}{\partial R} < 0$);
  * $L$: escassez de equipe de enfermagem/apoio sobrecarrega o médico ($\frac{\partial c}{\partial L} < 0$);
  * $D$: necessidade de saúde gera utilidade moral / propósito assistencial ($\frac{\partial c}{\partial D} < 0$);
  * $\mathbf{Z}$: heterogeneidade de preferências, especialidade e vínculos de origem.
* **Do Bloco de Roback (1982) — Equilíbrio Espacial e Habitação:**
  * $r$: custos locais de moradia e aluguel elevam a despesa do médico ($\frac{\partial c}{\partial r} > 0$);
  * $s$: amenidades urbanas, lazer, segurança e conectividade reduzem $c$ ($\frac{\partial c}{\partial s} < 0$).

---

### [Slide 3] O Modelo Microeconômico Unificado do PMM-E

$$
V_i = \sum_t \delta^t \left[ \frac{\mathbb{E}(w^{(s)}_{it})}{p_{it}} - c\Big(R_{it}, L_{it}, D_{it}, \mathbf{Z}_i; \; r_{it}, s_{it}\Big) \right], \qquad i^* = \arg\max_{i \in \mathcal{I}} V_i
$$

* **Por que o Efeito Total do IVS é Teoricamente Ambíguo?**
  * **Canal Positivo (+):** Faixas de bolsa maiores do governo federal ($\Delta \mathbb{E}(w) > 0$);
  * **Canal Negativo (-):** Déficit de amenidades urbanas ($s$) e de suporte clínico ($L, K$), aumentando $c$;
  * **Canal Condicional ($\pm$):** Oportunidade de impacto assistencial ($D$) atenuando $c$ para médicos vocacionados ($\mathbf{Z}$).

---

## 2. Roteiro de Fala para a Apresentação dos Slides (Script Acadêmico)

1. *"Partimos do problema intertemporal de escolha locacional de Moehling et al. (2020), no qual o médico maximiza o fluxo descontado de remuneração real esperado líquido de um termo de custos locacionais $c$."*
2. *"No artigo original de Moehling et al., o termo $c$ é uma 'caixa-preta' aditiva que captura apenas preferências genéricas por estilo de vida e proximidade familiar. No nosso estudo, abrimos estruturalmente essa caixa: microfundamentamos $c$ como uma função $c(R, L, D, \mathbf{Z}; r, s)$, incorporando a alocação de tempo, equipe e propósito de Reinhardt (1975) e o custo de moradia e amenidades de Roback (1982)."*
3. *"Essa unificação gera um modelo completo e rigoroso: ele preserva o benchmark linear para a remuneração real e explica por que o efeito total do IVS é teoricamente ambíguo, operando positivamente sobre a bolsa federal e em direções opostas sobre as desamenidades e o propósito assistencial."*



