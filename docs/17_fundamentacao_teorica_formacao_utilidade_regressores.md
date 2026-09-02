# 17. Base Microeconômica Unificada da Escolha Locacional Médica

> **Projeto:** Avaliação de Impacto e Economia da Saúde — Programa Mais Médicos Especialistas (PMM-E / Lei nº 15.233/2025)  
> **Objeto:** Decisão intertemporal de alocação espacial e oferta de trabalho médico  
> **Status:** Documento teórico canônico de referência  
> **Data de Consolidação:** 31 de agosto de 2026  

---

## 1. Arquitetura do Modelo Unificado

O modelo microeconômico do estudo adota uma **arquitetura teórica unificada**:

1. **O Núcleo Canônico é Moehling et al. (2020):** fornece o problema intertemporal em que o médico escolhe a localidade que maximiza o fluxo descontado da remuneração real esperada menos um termo de custos e desamenidades locacionais ($c$).
2. **A Microfundamentação de $c$ vem de Roback (1982) e Reinhardt (1975):** no paper original de Moehling et al., o termo $c$ é mantido em forma reduzida como uma "caixa-preta". Usamos Roback e Reinhardt especificamente para **modelar a estrutura interna de $c$**, transformando-o em uma função estrutural explícita:
   $$
   c^{(s)}_{it} = c\Big(R_{it}, L_{it}, D_{it}, \mathbf{Z}_i; \; r_{it}, s_{it}\Big)
   $$

Essa unificação preserva a regra de decisão intertemporal de Moehling et al., ao mesmo tempo em que dá conteúdo econômico aos fatores não pecuniários, institucionais e espaciais que afetam a atratividade de cada município.

---

## 2. O Ponto de Partida: Moehling et al. (2020) e a "Caixa-Preta" de $c$

Moehling, Niemesh, Thomasson e Treber (2020, p. 187) escrevem o problema microeconômico de escolha locacional do médico como:

$$
\arg\max_{i \in \mathcal{I}} U(\omega_i) = \arg\max_{i \in \mathcal{I}} \sum_t \delta^t \left[ \frac{\mathbb{E}(w^{(s)}_{it})}{p_{it}} - c^{(s)}_{it} \right]
$$

onde:

* $i \in \mathcal{I}$ indexa o município no conjunto de opções viáveis $\mathcal{I}$;
* $t$ indexa o período temporal (horizonte de planejamento);
* $s$ identifica a especialidade médica / grupo de qualificação;
* $w^{(s)}_{it}$ é a remuneração nominal esperada;
* $p_{it}$ é o nível geral de preços local / custo de vida;
* $\delta \in (0, 1)$ é o fator de desconto intertemporal;
* $c^{(s)}_{it}$ é o parâmetro que reúne os custos e desamenidades locacionais.

### O que $c$ representa no paper oficial de Moehling et al.?

No artigo original, os autores discutem $c^{(s)}_{it}$ como um termo aditivo agregado que inclui:
* Preferência por estilo de vida urbano versus rural (*"taste for rural/urban living"*);
* Proximidade geográfica da família e vínculos de origem (*"proximity to family"*);
* Custos de deslocamento e desamenidades de consumo.

Ao mesmo tempo, Moehling et al. tratam hospitais, laboratórios, densidade médica e malha de transporte como **amenidades produtivas** que deslocam a remuneração nominal esperada $\mathbb{E}(w^{(s)}_{it})$.

> [!NOTE]
> **A Limitação de Moehling et al.:**  
> Embora Moehling et al. separem remuneração real e custos locacionais, eles **não abrem o mecanismo interno de $c$**. Fatores como dotação de tempo e sobrecarga de trabalho, carência de equipe de enfermagem, custo de moradia/aluguel e motivação intrínseca por impacto assistencial permanecem implícitos dentro do termo $c$.

---

## 3. Abrindo a Caixa de $c$: Contribuições Estruturais de Roback (1982) e Reinhardt (1975)

Para que $c$ deixe de ser um resíduo inobservável e se torne operacional para o PMM-E, importamos os primitivos de dois modelos seminais:

### 3.1 Bloco Espacial e Habitacional: Roback (1982)

Roback (1982) formaliza o equilíbrio espacial onde o trabalhador consome moradia/terra ($\ell^c$) ao custo de aluguel local $r$, usufruindo de um vetor de amenidades territoriais $s$:

$$
\max_{x, \ell^c} U(x, \ell^c; s) \quad \text{sujeito a} \quad w + I = x + r \ell^c
$$

$$
V(w, r; s) = k, \qquad C(w, r; s) = 1
$$

* **O que Roback adiciona a $c$:**
  1. **Custo de Moradia ($r$):** despesas com aluguel e custos de dupla residência elevam a despesa do profissional ($\frac{\partial c}{\partial r} > 0$);
  2. **Amenidades de Consumo ($s$):** infraestrutura urbana, segurança pública, escolas para os filhos, opções de lazer e conectividade logística reduzem a desamenidade de morar na cidade ($\frac{\partial c}{\partial s} < 0$).

### 3.2 Bloco da Prática Médica e Alocação de Tempo: Reinhardt (1975)

Reinhardt (1975) modela a tecnologia de produção de saúde e a dotação de tempo do médico:

$$
U = U(R, Y, L, D; \mathbf{Z}), \qquad \bar{H} = R + H
$$

$$
q = f(H, L, K; \boldsymbol{\Omega}), \qquad \pi = p q - w L - r K
$$

* **O que Reinhardt adiciona a $c$:**
  1. **Alocação de Tempo e Lazer ($R = \bar{H} - H$):** jornadas excessivas, plantões imprevistos e perda de lazer ($H$) elevam a desutilidade subjetiva ($\frac{\partial c}{\partial R} < 0$, ou $\frac{\partial c}{\partial H} > 0$);
  2. **Equipe Auxiliar ($L$):** a presença de pessoal de apoio e enfermagem qualificado reduz a sobrecarga física e administrativa do especialista ($\frac{\partial c}{\partial L} < 0$);
  3. **Propósito e Impacto Assistencial ($D$):** a oportunidade de atender populações vulneráveis e resolver vazios assistenciais gera ganho moral para médicos vocacionados, atenuando a percepção de isolamento ($\frac{\partial c}{\partial D} < 0$);
  4. **Características Individuais ($\mathbf{Z}$):** estágio de carreira, especialidade clínica/cirúrgica e vínculos prévios com o território.

---

## 4. O Modelo Microeconômico Unificado do PMM-E

Integrando a microfundamentação estrutural de $c$ ao problema intertemporal de Moehling et al., o **valor da opção municipal $i$** para o médico especialista do tipo $s$ é formalizado por:

$$
V_i = \sum_t \delta^t \left[ \frac{\mathbb{E}(w^{(s)}_{it})}{p_{it}} - c\Big(R_{it}, L_{it}, D_{it}, \mathbf{Z}_i; \; r_{it}, s_{it}\Big) \right]
$$

E a **regra de escolha locacional ótima** é:

$$
i^* = \arg\max_{i \in \mathcal{I}} V_i
$$

### Propriedades e Sinais da Função Estrutural de Custos $c(\cdot)$

A função $c(R, L, D, \mathbf{Z}; r, s)$ satisfaz as seguintes propriedades monotônicas:

| Argumento | Origem Conceitual | Sinal em $c$ | Mecanismo Econômico |
| :--- | :--- | :---: | :--- |
| **Horas de Lazer ($R = \bar{H} - H$)** | Reinhardt (1975) | $\frac{\partial c}{\partial R} < 0$ | Menor jornada de trabalho e flexibilidade reduzem a desutilidade locacional. |
| **Equipe Auxiliar ($L$)** | Reinhardt (1975) | $\frac{\partial c}{\partial L} < 0$ | Enfermagem e suporte técnico aliviam o esforço do especialista. |
| **Impacto Assistencial ($D$)** | Reinhardt (1975) | $\frac{\partial c}{\partial D} < 0$ | Propósito social e atendimento a populações carentes reduzem o custo subjetivo da vaga. |
| **Vetor de Preferências ($\mathbf{Z}$)** | Reinhardt (1975) | $\pm$ | Vínculos prévios de nascimento/formação na região reduzem $c$. |
| **Aluguel / Custo de Moradia ($r$)** | Roback (1982) | $\frac{\partial c}{\partial r} > 0$ | Custos habitacionais e manutenção de dupla residência elevam o custo local. |
| **Amenidades Urbanas ($s$)** | Roback (1982) | $\frac{\partial c}{\partial s} < 0$ | Infraestrutura, lazer, transporte e segurança tornam a cidade mais atraente. |

---

## 5. Contextualização para o PMM-E e o Papel do IVS 2010

No contexto do PMM-E, os primitivos do modelo unificado mapeiam-se diretamente nas variáveis observáveis do estudo:

| Primitivo do Modelo Unificado | Dimensão Econômica no PMM-E | Proxy / Mapeamento no Repositório |
| :--- | :--- | :--- |
| $\frac{\mathbb{E}(w)}{p}$ | Retorno financeiro real da bolsa-formação federal | Faixas de Bolsa (R\$ 10.000, 15.000, 20.000) deflacionadas |
| $R = \bar{H} - H$ | Carga horária semanal e previsibilidade de escala | 20h semanais do edital e contratos no CNES |
| $L$ | Equipe multidisciplinar de enfermagem e apoio | Quantidade de enfermeiros/técnicos por leito no CNES |
| $D$ | Necessidade assistencial e demanda epidemiológica | Vulnerabilidade social da população atendida |
| $r$ | Custo de vida local e despesas de moradia | Aluguel estimado e custo de deslocamento |
| $s$ | Amenidades territoriais e conectividade | Distância rodoviária até polos regionais/capitais |
| $\mathbf{Z}$ | Especialidade e vínculos regionais prévios | Especialidade médica e proximidade da formação/origem |
| $\delta^t$ | Desconto intertemporal do valor da formação | Duração da bolsa (12 a 24 meses) e certificação futura |

> [!IMPORTANT]
> **Por que o Efeito Total do IVS 2010 é Teoricamente Ambíguo?**  
> No modelo unificado, o IVS atua simultaneamente sobre múltiplos canais:
> 1. **Canal Positivo na Remuneração:** O IVS define a regra da bolsa federal ($\Delta \mathbb{E}(w) > 0$ nos municípios de maior vulnerabilidade);
> 2. **Canal Negativo em $c$ (Desamenidades e Infraestrutura):** Municípios com alto IVS apresentam déficit de amenidades ($s$), menor estoque de equipe ($L$) e maior isolamento logístico ($r$), elevando $c$;
> 3. **Canal Positivo em $c$ (Propósito Assistencial):** Para especialistas com motivação pró-social ($\mathbf{Z}$), o alto IVS representa maior oportunidade de impacto assistencial ($D$), reduzindo $c$.
> 
> Como essas forças possuem vetores opostos, **o sinal líquido total $\frac{dV_i}{d(IVS)}$ não pode ser determinado *a priori* pela teoria**. Essa ambiguidade justifica a relevância da identificação empírica via RDD nos cutoffs de bolsa e modelos de duração.

---

## 6. O que as Equações Autorizam sobre Forma Funcional

1. **Benchmark Linear na Remuneração Real:** A equação de Moehling et al. introduz a remuneração real linearmente ($\mathbb{E}(w)/p$). Portanto, a forma canônica principal adota a bolsa deflacionada em nível real.
2. **Restrições a Formas Alternativas:** Os modelos originais selecionados não impõem utilidade logarítmica ($\ln w$), CRRA ou utilidade exponencial CARA ($-\exp(-aw)$). Tais transformações constituem especificações alternativas a serem tratadas em testes de sensibilidade.
3. **Não Imposição de Interações Mecânicas:** Não se impõe a priori que $\beta_{\text{Bolsa} \times \text{IVS}} > 0$. A compensação pecuniária por desamenidades ocorre de forma aditiva no modelo unificado.

---

## 7. Referências Canônicas

* **Moehling, C. M.; Niemesh, G. T.; Thomasson, M. A.; Treber, J. (2020).** [*Medical Education Reforms and the Origins of the Rural Physician Shortage*](https://doi.org/10.1007/s11698-019-00187-w). **Cliometrica**, 14(2), 181–225. ([Manuscrito dos Autores](https://niemesgt.github.io/files/MoehlingNiemeshThomassonTreber2019.pdf)).
* **Reinhardt, U. E. (1975).** [*Health Manpower Planning in a Market Context: The Case of Physician Manpower*](https://pure.iiasa.ac.at/213/1/XB-75-001.pdf), em N. T. J. Bailey e M. Thompson (eds.), *Systems Aspects of Health Planning*, North-Holland / IIASA, pp. 131–162.
* **Roback, J. (1982).** [*Wages, Rents, and the Quality of Life: A General Equilibrium Model of Geographic Differences*](https://doi.org/10.1086/261120). **Journal of Political Economy**, 90(6), 1257–1278. ([PDF](https://www.nathanschiff.com/webdocs/grad_urban/urban_papers/Roback_JPE_1982.pdf)).
