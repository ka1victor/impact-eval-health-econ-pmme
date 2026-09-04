# -*- coding: utf-8 -*-
"""
scripts/gerar_doc_teoria_pmme.py
Gera o documento mestre docs/90_arquivo_historico/10_fundamentacao_teorica_problema_pmme.md
com a fundamentação teórica formal completa para a:
Atração e Retenção de Médicos Especialistas em Cidades do Interior com base nas Diferentes Bolsas e IVS.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT_MD = ROOT / "docs" / "90_arquivo_historico" / "10_fundamentacao_teorica_problema_pmme.md"

doc_text = r"""# 10. Fundamentação Teórica Estrutural do Problema do PMM-E

> **Documento Teórico Central**  
> **Projeto:** Avaliação de Impacto e Economia da Saúde — Programa Mais Médicos Especialistas (PMM-E / Lei nº 15.233/2025)  
> **Tema Central:** *Atração e Retenção de Médicos Especialistas em Cidades do Interior com base nas Diferentes Bolsas e no IVS (Índice de Vulnerabilidade Social).*  
> **Autores:** Equipe de Pesquisa Econômica em Saúde  
> **Data de Consolidação:** 31 de Agosto de 2026  

---

## 1. Visão Geral: Por que a Teoria Microeconômica é Indispensável?

A literatura econômica em provimento de recursos humanos em saúde (Roback 1982; Sivey et al. 2012; Gravelle et al. 2018; Russell et al. 2021) demonstra que **a distribuição geográfica de médicos especialistas no interior não decorre de simples inércia, mas de escolhas microeconômicas de otimização sob fortes diferenciais de remuneração, preferências por amenidades urbanas e custos de isolamento**.

No caso do **PMM-E**, a intervenção federal desenha um esquema de incentivos monetários escalonados (bolsa formação + adicionais de fixação) condicionados ao **Índice de Vulnerabilidade Social (IVS 2010 do IPEA)** para induzir dois comportamentos distintos:
1. **Atração Imediata (Novas Entradas):** Deslocamento da curva de oferta de médicos especialistas para municípios remotos do interior via preenchimento do gap de *diferencial salarial compensatório*.
2. **Retenção Sustentada (Permanência / Sobrevivência):** Mitigação da taxa de evasão e rotatividade após o período obrigatório ou término do bônus financeiro ativo.

Este documento formaliza os **7 Pilares Teóricos Seminais** e desenvolve um **Modelo Teórico Unificado** que conecta as preferências dos especialistas, a resposta a bolsas escalonadas e as desamenidades do IVS às especificações empíricas (Worker Flows, RDD nos cutoffs de IVS e Tripla Diferença em Painel CNES).

```mermaid
graph TD
    subgraph "Arcabouço Teórico Integrado do PMM-E no Interior"
        P1["Pilar 1: Equilíbrio Espacial & Diferenciais por IVS<br/>(Roback 1982)"] --> M["Modelo Microeconômico Unificado<br/>Atração vs Retenção por Bolsa e IVS"]
        P2["Pilar 2: Preferências Locacionais & WTA<br/>(Sivey et al. 2012)"] --> M
        P3["Pilar 3: Matching Centralizado sob Bolsas<br/>(Agarwal 2015)"] --> M
        P4["Pilar 4: Worker Flows em Entradas vs Saídas<br/>(Gravelle et al. 2018)"] --> M
        P5["Pilar 5: Federalismo Fiscal & Crowding-Out<br/>(Baicker & Staiger 2005)"] --> M
        P6["Pilar 6: Complementaridade Fator-Infraestrutura<br/>(Acemoglu & Finkelstein 2008)"] --> M
        P7["Pilar 7: Políticas Place-Based & Bem-Estar Social<br/>(Kline & Moretti 2014)"] --> M
    end
    
    M --> TEST1["Hipótese 1: Atração Imediata (Salto em Entradas CNES)"]
    M --> TEST2["Hipótese 2: Retenção e Sobrevida por IVS (Cox / Kaplan-Meier)"]
    M --> TEST3["Hipótese 3: RDD em Cutoffs de Bolsa no IVS (0,400 e 0,500)"]
```

---

## 2. Os 7 Pilares Teóricos do Problema Substantivo

---

### PILAR 1 — Equilíbrio Espacial e Diferenciais Salariais Compensatórios por IVS
* **Paper Canônico:** **Roback (1982, *JPE*)**.
* **Referência:** Roback, Jennifer. (1982). *Wages, Rents, and the Quality of Life: A General Equilibrium Model of Geographic Differences*. **Journal of Political Economy**, 90(6), 1257–1278.
* **Extensão:** 22 páginas | **Foco:** **pp. 1257–1272 (Seções 1 a 3: 15 págs)**.
* **Mecanismo Econômico Formal:**  
  O equilíbrio espacial hedônico exige que a utilidade indireta de um especialista com mobilidade perfeita seja constante no território:
  $$V(w_m, r_m; A_m) = \bar{u}$$
  onde $w_m$ é a remuneração, $r_m$ é o custo de moradia e $A_m$ é o vetor de amenidades locais (infraestrutura urbana, escolas, lazer e amenidades de prática médica).  
  Diferenciando implicitamente a utilidade em relação às amenidades:
  $$\left. \frac{dw_m}{dA_m} \right|_{V = \bar{u}} = -\frac{V_{A}(w_m, r_m; A_m)}{V_{w}(w_m, r_m; A_m)} < 0$$
* **Aplicação Estrutural ao PMM-E:**  
  Municípios com desamenidades severas e alta vulnerabilidade socioeconômica (**alto IVS 2010**) geram desutilidade locacional aos médicos. Para que um especialista aceite atuar no interior vulnerável, o programa deve ofertar um **diferencial salarial compensatório ($\Delta w$)** proporcional ao déficit de amenidades ($1 - A_m \propto IVS_m$). As faixas progressivas de bolsa do PMM-E operam exatamente como esse vetor compensatório equalizador.

---

### PILAR 2 — Preferências Médicas, Willingness to Accept (WTA) e Elasticidade da Bolsa
* **Paper Canônico:** **Sivey et al. (2012, *JHE*)**.
* **Referência:** Sivey, Peter; Scott, Anthony; Witt, Julia; Joyce, Catherine; Humphreys, John. (2012). *Junior Doctors' Preferences for Specialty Choice*. **Journal of Health Economics**, 31(6), 813–826.
* **Extensão:** **14 páginas (Artigo completo)**.
* **Mecanismo Econômico Formal:**  
  Sob modelos de utilidade aleatória (RUM), a escolha locacional do médico $i$ pelo município $j$ é:
  $$U_{ij} = \beta_w w_j + \beta_{loc} Loc_j + \beta_h Horas_j + \varepsilon_{ij}$$
  O *Willingness to Accept* monetário para aceitar trabalhar no interior remoto é dado por:
  $$WTA_{interior} = -\frac{\beta_{loc}}{\beta_w}$$
* **Aplicação Estrutural ao PMM-E:**  
  Permite parametrizar a elasticidade da oferta médica a diferentes doses de incentivo financeiro (R$ 5.000 vs R$ 10.000 de adicional). Mostra ainda que especialidades com alto custo de oportunidade em consultório privado (cirúrgicas) exigem um WTA substancialmente mais alto para o interior do que especialidades clínicas.

---

### PILAR 3 — Matching Centralizado sob Bolsas e Custos de Busca Espacial
* **Paper Canônico:** **Agarwal (2015, *AER*)**.
* **Referência:** Agarwal, Nikhil. (2015). *An Empirical Model of the Medical Match*. **American Economic Review**, 105(7), 1939–1978.
* **Extensão:** 40 páginas | **Foco:** **pp. 1940–1958 (Seções I a III: 18 págs)**.
* **Mecanismo Econômico Formal:**  
  Mercados descentralizados de especialistas sofrem com atritos informacionais e assimetria de busca: hospitais no interior não alcançam candidatos em centros universitários. A centralização em plataforma nacional de matching com ranking de preferências e subsídios financeiros resolve falhas de coordenação:
  $$\mu = \arg\max_{\mu \in \mathcal{M}_{\text{estável}}} \sum_{i \in \mathcal{I}} u_i(\mu(i))$$
* **Aplicação Estrutural ao PMM-E:**  
  Explica por que o edital centralizado do Ministério da Saúde viabiliza o preenchimento de vagas em municípios remotos que jamais conseguiriam atrair especialistas por processos seletivos locais isolados.

---

### PILAR 4 — Dinâmica de Worker Flows: Efeito de Bônus em Entradas vs. Saídas
* **Paper Canônico:** **Gravelle, Scott, Yong & McGrail (2018, *SSM*)**.
* **Referência:** Gravelle, Hugh; Scott, Anthony; Yong, Jongsay; McGrail, Matthew. (2018). *Do Rural Incentives Payments Affect Entries and Exits of General Practitioners?* **Social Science & Medicine**, 216, 88–96.
* **Extensão:** **9 páginas (Artigo completo)**.
* **Mecanismo Econômico Formal:**  
  A variação do estoque médico local é a diferença entre fluxos brutos de entrada e saída:
  $$\Delta L_{mt} = Entry_{mt}(w_{\text{bolsa}}) - Exit_{mt}(w_{\text{bolsa}})$$
  Gravelle et al. provam empiricamente que incentivos financeiros possuem alta elasticidade sobre as **novas entradas** ($\frac{\partial Entry}{\partial w} > 0$), mas **efeito quase nulo sobre a evasão de médio prazo** ($\frac{\partial Exit}{\partial w} \approx 0$).
* **Aplicação Estrutural ao PMM-E:**  
  Fundamenta nossa hipótese central: as bolsas elevadas do PMM-E são altamente eficazes para atrair especialistas (efeito imediato de entrada), mas a fixação duradoura depende de condições estruturais e vínculo local.

---

### PILAR 5 — Federalismo Fiscal, Otimização Municipal e Crowding-Out
* **Paper Canônico:** **Baicker & Staiger (2005, *QJE*)**.
* **Referência:** Baicker, Katherine; Staiger, Douglas. (2005). *Fiscal Shenanigans, Targeted Federal Health Care Funds, and Patient Mortality*. **Quarterly Journal of Economics**, 120(1), 345–386.
* **Extensão:** 42 páginas | **Foco:** **pp. 348–360 (Seção II: Teoria, 12 págs)**.
* **Mecanismo Econômico Formal:**  
  O gestor municipal maximiza $U(L_m, G_m)$ sujeito a $w_m L_m^{\text{próprio}} + G_m = R_m + w_{\text{bolsa}} L_m^{\text{fed}}$. A resposta líquida é:
  $$\frac{\partial L_m^{\text{total}}}{\partial L_m^{\text{fed}}} = 1 + \frac{\partial L_m^{\text{próprio}}}{\partial L_m^{\text{fed}}}$$
  Se o município cancela contratos preexistentes financiados com receita própria, ocorre substituição fiscal (*crowding-out*).
* **Aplicação Estrutural ao PMM-E:**  
  Fundamenta a necessidade de auditar no CNES se as bolsas do PMM-E adicionam especialistas líquidos ou se substituem médicos municipais preexistentes.

---

### PILAR 6 — Complementaridade Trabalho Especializado - Capital Hospitalar
* **Paper Canônico:** **Acemoglu & Finkelstein (2008, *JPE*)**.
* **Referência:** Acemoglu, Daron; Finkelstein, Amy. (2008). *Input and Technology Choices in Regulated Industries: Evidence from the Health Care Sector*. **Journal of Political Economy**, 116(5), 837–880.
* **Extensão:** 44 páginas | **Foco:** **pp. 839–858 (Seções I a III: 20 págs)**.
* **Mecanismo Econômico Formal:**  
  A função de produção de procedimentos hospitalares e cirurgias exibe complementaridade estrita:
  $$Y = F(K, L), \quad \frac{\partial^2 Y}{\partial L \partial K} > 0$$
  onde $L$ é o médico especialista e $K$ é o capital tecnológico hospitalar (leitos cirúrgicos, tomógrafos, centros cirúrgicos).
* **Aplicação Estrutural ao PMM-E:**  
  Explica por que especialistas alocados em cidades do interior desprovidas de hospital estruturado apresentam alta evasão e baixa resolutividade: a falta de $K$ anula a produtividade marginal de $L$.

---

### PILAR 7 — Políticas Place-Based e Balanço de Bem-Estar no Interior
* **Paper Canônico:** **Kline & Moretti (2014, *Ann. Rev. Econ.*)**.
* **Referência:** Kline, Patrick; Moretti, Enrico. (2014). *People, Places, and Public Policy: Some Simple Analytics of Local Economic Development Programs*. **Annual Review of Economics**, 6, 629–662.
* **Extensão:** 34 páginas | **Foco:** **pp. 631–648 (Seções 1 a 3: 17 págs)**.
* **Mecanismo Econômico Formal:**  
  O bem-estar social agregado de subsidiar médicos no interior é positivo se o ganho de acesso em saúde local superar os custos do subsídio e eventuais distorções espaciais:
  $$W = \sum_{m} N_m \left[ v_m(w_m, r_m) - c_m \right] + \text{Benefício da Redução de TFD e Mortalidade}$$
* **Aplicação Estrutural ao PMM-E:**  
  Fundamenta a avaliação de custo-benefício social e eficiência do gasto público federal no provimento de especialistas no interior do Brasil.

---

## 3. O Modelo Microeconômico Unificado de Atração e Retenção no Interior

O modelo unificado resolve simultaneamente:
1. **A Decisão do Especialista:** Aceitar o posto no município $m$ se a remuneração total (salário base + bolsa PMM-E $\Delta w(IVS_m)$) compensar o diferencial hedônico do interior:
   $$w_{\text{base}} + \Delta w(IVS_m) \ge w_{\text{capital}} + WTA(A_m)$$
2. **A Dinâmica de Sobrevivência:** A taxa instantânea de evasão médica $\lambda(t \mid IVS_m, K_m)$ segue um modelo de riscos proporcionais de Cox:
   $$\lambda(t \mid X_m) = \lambda_0(t) \exp\left( \gamma_1 IVS_m + \gamma_2 K_m - \gamma_3 \text{Bolsa}_m \right)$$
3. **O Efeito nos Cutoffs de IVS:** No limiar de descontinuidade do IVS ($c \in \{0.400, 0.500\}$), a bolsa sofre um salto discreto de R$ 5.000, permitindo identificar a elasticidade local da atração e retenção via RDD:
   $$\tau_{\text{RDD}} = \lim_{IVS \downarrow c} \mathbb{E}[Y \mid IVS] - \lim_{IVS \uparrow c} \mathbb{E}[Y \mid IVS]$$

---

## 4. Guia de Atribuição da Equipe (7 Membros)

| Membro | Paper Teórico Atribuído | Extensão Foco | O que Redigir para a Seção Teórica |
|:---:|:---|:---|:---|
| **Membro 1** | **Roback (1982)** | 15 págs (pp. 1257–1272) | Formalizar o equilíbrio hedônico espacial e a curva de oferta médica compensatória indexada ao IVS 2010. |
| **Membro 2** | **Sivey et al. (2012)** | 14 págs (Artigo completo) | Modelar as preferências locacionais e a estimativa de WTA para o interior por especialidade. |
| **Membro 3** | **Agarwal (2015)** | 18 págs (pp. 1940–1958) | Modelar o edital centralizado como mecanismo de matching que reduz custos de busca espacial. |
| **Membro 4** | **Gravelle et al. (2018)** | 9 págs (Artigo completo) | Formalizar a decomposição de worker flows: sensibilidade de novas entradas vs. persistência de saídas. |
| **Membro 5** | **Baicker & Staiger (2005)** | 12 págs (pp. 348–360) | Deduzir a proposição teórica de crowding-out fiscal e substituição de vínculos locais no CNES. |
| **Membro 6** | **Acemoglu & Finkelstein (2008)** | 20 págs (pp. 839–858) | Escrever a função de produção hospitalar e a complementaridade entre especialista e capital físico ($K$). |
| **Membro 7** | **Kline & Moretti (2014)** | 17 págs (pp. 631–648) | Redigir o enquadramento de eficiência econômica e bem-estar social de políticas place-based no interior. |
"""

with open(OUT_MD, "w", encoding="utf-8") as f:
    f.write(doc_text)

print(f"Documento {OUT_MD} gerado com sucesso.")
