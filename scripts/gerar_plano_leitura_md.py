# -*- coding: utf-8 -*-
"""
scripts/gerar_plano_leitura_md.py
Gera o documento docs/08_plano_leitura_equipe_literatura.md
com o plano de leitura da equipe focado estritamente na:
Atração e Retenção de Médicos Especialistas em Cidades do Interior sob Diferentes Bolsas e IVS.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "output" / "revisao_literatura" / "matriz_evidencias_artigos_expandida.json"
OUT_MD_PATH = ROOT / "docs" / "08_plano_leitura_equipe_literatura.md"

with open(JSON_PATH, "r", encoding="utf-8") as f:
    papers = json.load(f)

md_content = r"""# 08. Plano Estratégico de Busca, Leitura da Literatura e Guia de Atribuição da Equipe

> **Projeto:** Avaliação de Impacto e Economia da Saúde — Programa Mais Médicos Especialistas (PMM-E / Lei nº 15.233/2025)  
> **Tema Central:** *Atração e Retenção de Médicos Especialistas em Cidades do Interior com base nas Diferentes Bolsas e no IVS (Índice de Vulnerabilidade Social).*  
> **Finalidade:** Protocolo formal de busca bibliográfica, seleção sistemática de literatura recente (2018–2026) e clássica, e guia de divisão de leitura para os 14 membros da equipe de pesquisa.  
> **Diretriz Metodológica Especial:** Abordagem **"Teoria + Empiria"**, integrando modelos microeconômicos de equilíbrio espacial e contratos a desenhos causais quase-experimentais em saúde.  
> **Data de Consolidação:** 31 de Agosto de 2026  

---

## 1. Protocolo de Busca Sistemática e Filtros Aplicados

Para construir uma base bibliográfica focada na **atração, retenção e resposta a incentivos financeiros (bolsas) por nível de vulnerabilidade (IVS)**, estabelecemos um protocolo em **quatro etapas**:

```mermaid
graph TD
    S1["Etapa 1: Strings de Busca em 4 Clusters Temáticos<br/>(Diferenciais Espaciais, Retenção & Worker Flows, Bolsas/Incentivos, RDD & IVS)"] --> S2["Etapa 2: Coleta em 5 Bases Acadêmicas<br/>(OpenAlex, PubMed, NBER/RePEc, Scopus/Web of Science, SciELO)"]
    S2 --> S3["Etapa 3: Triagem por Rigor Causal & Especificidade de Interior"]
    S3 --> S4["Etapa 4: Curadoria Final & Foco em Páginas Operacionais (10 a 20 pp.)"]
    
    S4 --> T1["Tier 1: 7 Papers de Teoria e Preferências Médicas (Média foco: ~16 pp.)"]
    S4 --> T2["Tier 1: 7 Papers Empíricos, Sobrevivência e Métodos (Média foco: ~14 pp.)"]
    S4 --> T3["Tier 2: 12+ Papers de Apoio e Extensão Metodológica (2018–2026)"]
```

### 1.1 Clusters de Busca e Strings Booleanas Executadas

1. **Cluster A (Equilíbrio Espacial, Oferta Médica & Desamenidades do Interior):**
   `("physician labor supply" OR "specialist location" OR "compensating differentials" OR "spatial equilibrium" OR "amenities") AND ("rural" OR "remote" OR "deprived areas" OR "social vulnerability")`
2. **Cluster B (Incentivos Financeiros, Bolsas Escalonadas & Crowding-Out):**
   `("financial incentives" OR "wage bonus" OR "stipend" OR "loan repayment" OR "return-of-service" OR "crowding-out") AND ("physician recruitment" OR "physician retention")`
3. **Cluster C (Dinâmica de Worker Flows, Retenção e Sobrevivência):**
   `("physician retention" OR "worker flows" OR "entry and exit" OR "turnover" OR "hazard rate" OR "survival analysis" OR "tenure") AND ("health workforce")`
4. **Cluster D (Métodos Quase-Experimentais, RDD, DDD & Microdados do SUS):**
   `("Mais Médicos" OR "PMM" OR "CNES" OR "IVS" OR "IPEA") AND ("regression discontinuity" OR "triple differences" OR "event study" OR "local randomization")`

---

## 2. O Paradigma "Teoria + Empiria" no Contexto de Atração e Retenção

A literatura econômica de referência (Roback, Agarwal, Gravelle, Russell, Pathman) ensina que a atração e a fixação de especialistas no interior devem ser modeladas sob três mecanismos complementares:

1. **Diferencial Compensatório Espacial (Roback 1982; Sivey et al. 2012):** Médicos possuem preferências por capitais e centros com infraestrutura; atraí-los para o interior vulnerável (alto IVS) requer uma bolsa $\Delta w(IVS)$ que compense a carência de amenidades.
2. **Decomposição de Worker Flows (Gravelle et al. 2018):** Incentivos financeiros possuem alta elasticidade sobre a **taxa de entrada (atração imediata)**, mas efeito declinante sobre a **taxa de saída (retenção de longo prazo)**.
3. **Modelagem Longitudinal de Sobrevivência (Russell et al. 2021; Pathman et al. 2004):** A probabilidade de evasão cresce após o término do incentivo financeiro ativo, exigindo isolar o período sob bolsa (6 meses) do horizonte de permanência autônoma (12+ meses).

---

## 3. Quadro Geral de Atribuição da Equipe (14 Membros)

| ID | Categoria | Subtema Central | Autores & Ano | Periódico | Extensão Total | Páginas de Foco Prioritário |
|:---|:---|:---|:---|:---|:---|:---|
| **TEO_01** | Teoria Espacial | Equilíbrio Hedônico e Diferencial por IVS | Roback (1982) | *J. Polit. Econ.* | 22 págs | **pp. 1257–1272 (15 págs)** |
| **TEO_02** | Teoria + Empiria | Preferências, WTA e Elasticidade da Bolsa | Sivey et al. (2012) | *J. Health Econ.* | 14 págs | **Artigo Completo (14 págs)** |
| **TEO_03** | Teoria + Empiria | Matching Centralizado sob Bolsas e Fricções | Agarwal (2015) | *Am. Econ. Rev.* | 40 págs | **pp. 1940–1958 (18 págs)** |
| **TEO_04** | Teoria + Empiria | Worker Flows: Efeito em Entradas vs Saídas | Gravelle et al. (2018) | *Soc. Sci. Med.* | 9 págs | **Artigo Completo (9 págs)** |
| **TEO_05** | Teoria + Empiria | Federalismo Fiscal e Crowding-Out Municipal | Baicker & Staiger (2005) | *Q. J. Econ.* | 42 págs | **pp. 348–360 (12 págs)** |
| **TEO_06** | Teoria + Empiria | Complementaridade Trabalho-Capital Hospitalar | Acemoglu & Finkelstein (2008) | *J. Polit. Econ.* | 44 págs | **pp. 839–858 (20 págs)** |
| **TEO_07** | Teoria Espacial | Políticas Place-Based e Bem-Estar no Interior | Kline & Moretti (2014) | *Ann. Rev. Econ.* | 34 págs | **pp. 631–648 (17 págs)** |
| **EMP_01** | Empírica | Sobrevivência (Cox) e Fixação no Interior | Russell et al. (2021) | *Hum. Resour. Health* | 10 págs | **Artigo Completo (10 págs)** |
| **EMP_02** | Empírica | Coortes sob Bolsa Ativa vs Pós-Obrigação | Pathman et al. (2004) | *Medical Care* | 9 págs | **Artigo Completo (9 págs)** |
| **EMP_03** | Empírica | Revisão Global de Return-of-Service | Bärnighausen & Bloom (2009) | *BMC Health Serv. Res.* | 17 págs | **Artigo Completo (17 págs)** |
| **EMP_04** | Empírica | Incentivos Financeiros Progressivos | Somville (2020) | *World Development* | 14 págs | **Artigo Completo (14 págs)** |
| **EMP_05** | Empírica | Painel CNES Mensal e Rotatividade no SUS | Sliwa Ruiz et al. (2024) | *J. Health Econ.* | 18 págs | **Artigo Completo (18 págs)** |
| **EMP_06** | Empírica | Provimento e Heterogeneidade por Escassez | Fontes et al. (2018) | *Health Econ.* | 16 págs | **Artigo Completo (16 págs)** |
| **EMP_07** | Metodológica | Identificação Causal por Tripla Diferença | Olden & Møen (2022) | *The Econometrics J.* | 17 págs | **Artigo Completo (17 págs)** |

---

## 4. Fichas de Leitura — Fundamentação Teórica e "Teoria + Empiria" (7 Papers)

### [TEO_01] Roback (1982) — *Wages, Rents, and the Quality of Life*
- **Referência:** Roback, Jennifer. (1982). *Wages, Rents, and the Quality of Life: A General Equilibrium Model of Geographic Differences*. **Journal of Political Economy**, 90(6), 1257–1278. DOI: [10.1086/261120](https://doi.org/10.1086/261120).
- **Extensão:** 22 páginas | **Foco:** **pp. 1257–1272 (Seções 1 a 3: 15 págs)**.
- **Mecanismo:** Equilíbrio geral espacial hedônico: $V(w_m, r_m; A_m) = \bar{u}$. Cidades com desamenidades severas (alto IVS) exigem $\Delta w > 0$ para atrair profissionais.
- **Aplicação no PMM-E:** Fundamenta por que o programa indexa os adicionais de bolsa ao IVS 2010.

---

### [TEO_02] Sivey et al. (2012) — *Junior Doctors' Preferences for Specialty Choice*
- **Referência:** Sivey, Peter et al. (2012). *Junior Doctors' Preferences for Specialty Choice*. **Journal of Health Economics**, 31(6), 813–826. DOI: [10.1016/j.jhealeco.2012.07.001](https://doi.org/10.1016/j.jhealeco.2012.07.001).
- **Extensão:** **14 páginas (Artigo completo)**.
- **Mecanismo:** Random Utility Model e Discrete Choice Experiment (DCE): estima o Willingness to Accept (WTA) monetário para postos remotos no interior.
- **Aplicação no PMM-E:** Parametriza a sensibilidade de especialistas a diferentes faixas de bolsa e a diferença entre especialidades cirúrgicas vs. clínicas.

---

### [TEO_03] Agarwal (2015) — *An Empirical Model of the Medical Match*
- **Referência:** Agarwal, Nikhil. (2015). *An Empirical Model of the Medical Match*. **American Economic Review**, 105(7), 1939–1978. DOI: [10.1257/aer.20130663](https://doi.org/10.1257/aer.20130663).
- **Extensão:** 40 páginas | **Foco:** **pp. 1940–1958 (Seções I a III: 18 págs)**.
- **Mecanismo:** Modelo estrutural de matching centralizado sob restrições salariais e fricções de busca espacial.
- **Aplicação no PMM-E:** Modela como a centralização do edital público reduz custos de busca e como a bolsa atrai formandos para hospitais periféricos.

---

### [TEO_04] Gravelle, Scott, Yong & McGrail (2018) — *Do Rural Incentives Payments Affect Entries and Exits?*
- **Referência:** Gravelle, Hugh et al. (2018). *Do Rural Incentives Payments Affect Entries and Exits of General Practitioners?* **Social Science & Medicine**, 216, 88–96. DOI: [10.1016/j.socscimed.2018.09.041](https://doi.org/10.1016/j.socscimed.2018.09.041).
- **Extensão:** **9 páginas (Artigo completo)**.
- **Mecanismo:** Modelagem teórica e empírica de fluxos de trabalhadores (worker flows): bônus aumentam entradas mas têm efeito modesto na retenção.
- **Aplicação no PMM-E:** Inspiração direta para a decomposição em taxas de entrada (atração), saída (evasão) e saldo líquido.

---

### [TEO_05] Baicker & Staiger (2005) — *Fiscal Shenanigans, Targeted Federal Health Care Funds*
- **Referência:** Baicker, Katherine; Staiger, Douglas. (2005). *Fiscal Shenanigans, Targeted Federal Health Care Funds, and Patient Mortality*. **Quarterly Journal of Economics**, 120(1), 345–386. DOI: [10.1162/0033553053317416](https://doi.org/10.1162/0033553053317416).
- **Extensão:** 42 páginas | **Foco:** **pp. 348–360 (Seção II: Teoria, 12 págs)**.
- **Mecanismo:** Modelo de federalismo fiscal: governos locais remanejam gastos próprios ao receber subsídios federais vinculados (crowding-out).
- **Aplicação no PMM-E:** Base formal para testar se a bolsa federal atrai capacidade líquida ou substitui médicos contratados pelo município.

---

### [TEO_06] Acemoglu & Finkelstein (2008) — *Input and Technology Choices in Regulated Industries*
- **Referência:** Acemoglu, Daron; Finkelstein, Amy. (2008). *Input and Technology Choices in Regulated Industries: Evidence from the Health Care Sector*. **Journal of Political Economy**, 116(5), 837–880. DOI: [10.1086/595015](https://doi.org/10.1086/595015).
- **Extensão:** 44 páginas | **Foco:** **pp. 839–858 (Seções I a III: 20 págs)**.
- **Mecanismo:** Escolha ótima de fatores sob regulação: trabalho especializado ($L$) requer capital tecnológico ($K$) complementar ($\partial^2 Y / \partial L \partial K > 0$).
- **Aplicação no PMM-E:** Explica por que especialistas atraídos por bolsas ao interior não se fixam sem infraestrutura hospitalar mínima.

---

### [TEO_07] Kline & Moretti (2014) — *People, Places, and Public Policy*
- **Referência:** Kline, Patrick; Moretti, Enrico. (2014). *People, Places, and Public Policy: Some Simple Analytics of Local Economic Development Programs*. **Annual Review of Economics**, 6, 629–662. DOI: [10.1146/annurev-economics-080213-040845](https://doi.org/10.1146/annurev-economics-080213-040845).
- **Extensão:** 34 páginas | **Foco:** **pp. 631–648 (Seções 1 a 3: 17 págs)**.
- **Mecanismo:** Framework analítico de equilíbrio espacial para avaliar políticas place-based e bem-estar social.
- **Aplicação no PMM-E:** Formaliza a justificativa normativa e de bem-estar de subsidiar médicos no interior com alto IVS.

---

## 5. Fichas de Leitura — Literatura Empírica, Sobrevivência e Métodos (7 Papers)

### [EMP_01] Russell, McGrail & Humphreys (2021) — *Determinants of Rural Australian GP Retention*
- **Referência:** Russell, Deborah J. et al. (2021). *Determinants of Rural Australian General Practitioner Retention: A Longitudinal Analysis*. **Human Resources for Health**, 19, Artigo 7. DOI: [10.1186/s12960-020-00549-3](https://doi.org/10.1186/s12960-020-00549-3).
- **Extensão:** **10 páginas (Artigo completo)**.
- **Método:** Kaplan-Meier e modelo de Cox para estimar Hazard Ratios de evasão médica no interior por isolamento e infraestrutura.

---

### [EMP_02] Pathman et al. (2004) — *Outcomes of States' Scholarship, Loan Repayment Programs*
- **Referência:** Pathman, Donald E. et al. (2004). *Outcomes of States' Scholarship, Loan Repayment, and Related Programs for Physicians*. **Medical Care**, 42(6), 560–568. DOI: [10.1097/01.mlr.0000128004.26577.8b](https://doi.org/10.1097/01.mlr.0000128004.26577.8b).
- **Extensão:** **9 páginas (Artigo completo)**.
- **Método:** Acompanhamento de coortes longitudinais: retenção ativa (85%) vs. queda pós-bolsa (45%), justificando censura aos 12 meses.

---

### [EMP_03] Bärnighausen & Bloom (2009) — *Financial Incentives for Return of Service*
- **Referência:** Bärnighausen, Till; Bloom, David E. (2009). *Financial Incentives for Return of Service in Underserved Areas: A Systematic Review*. **BMC Health Services Research**, 9, Artigo 86. DOI: [10.1186/1472-6963-9-86](https://doi.org/10.1186/1472-6963-9-86).
- **Extensão:** **17 páginas (Artigo completo)**.
- **Método:** Revisão sistemática global de 43 programas de incentivo financeiro por retorno de serviço em 10 países.

---

### [EMP_04] Somville (2020) — *Financial Incentives and Physician Supply in Underserved Areas*
- **Referência:** Somville, Vincent. (2020). *Financial Incentives and Physician Supply in Underserved Areas*. **World Development**, 127, Artigo 104764. DOI: [10.1016/j.worlddev.2019.104764](https://doi.org/10.1016/j.worlddev.2019.104764).
- **Extensão:** **14 páginas (Artigo completo)**.
- **Método:** Avaliação quase-experimental de incentivos financeiros escalonados sobre oferta e retenção médica em áreas vulneráveis.

---

### [EMP_05] Sliwa Ruiz, Becker, Hone & Rocha (2024) — *Departure of Cuban Doctors in Brazil*
- **Referência:** Sliwa Ruiz, Julia et al. (2024). *The Supply of Primary Care Physicians and Population Health: Evidence from the Sudden Departure of Cuban Doctors in Brazil*. **Journal of Health Economics**, 93, Artigo 102833. DOI: [10.1016/j.jhealeco.2023.102833](https://doi.org/10.1016/j.jhealeco.2023.102833).
- **Extensão:** **18 páginas (Artigo completo)**.
- **Método:** Painel CNES mensal de alta frequência para avaliar rotatividade, saídas e substituição de médicos no interior.

---

### [EMP_06] Fontes, Conceição & Jacinto (2018) — *Evaluating the More Doctors Program*
- **Referência:** Fontes, Luiz Felipe Campos et al. (2018). *Evaluating the Impact of Physicians' Provision on Primary Healthcare: Evidence from Brazil's More Doctors Program*. **Health Economics**, 27(8), 1284–1299. DOI: [10.1002/hec.3768](https://doi.org/10.1002/hec.3768).
- **Extensão:** **16 páginas (Artigo completo)**.
- **Método:** PSM-DiD em microdados do DATASUS documentando impactos concentrados em municípios com maior vulnerabilidade inicial.

---

### [EMP_07] Olden & Møen (2022) — *The Triple Difference Estimator*
- **Referência:** Olden, Andreas; Møen, Jarle. (2022). *The Triple Difference Estimator*. **The Econometrics Journal**, 25(3), 606–622. DOI: [10.1093/ectj/utac010](https://doi.org/10.1093/ectj/utac010).
- **Extensão:** **17 páginas (Artigo completo)**.
- **Método:** Formalização econométrica do estimador DDD em painel com efeitos fixos de alta dimensão.

---

## 6. Bibliografia Expandida de Apoio e Métodos (Tier 2)

1. **Cattaneo, Matias D.; Idrobo, Nicolas; Titiunik, Rocio (2020)** — *A Practical Introduction to Regression Discontinuity Designs*, Cambridge University Press. (Guia para RDD em cutoffs discretos de IVS).
2. **Carrillo, Paul; Feres, Pedro (2019)** — *Provider Supply, Utilization, and Infant Health*, **AEJ: Economic Policy**, 11(3), 156–196. (Quase-experimento no Brasil e estudos de evento).
3. **Roth, Jonathan (2022)** — *Pretest with Caution: Event-Study Estimates After Testing for Parallel Trends*, **AER: Insights**, 4(3), 305–322. (Diretrizes para testes de pré-tendências).
4. **Clarke, Damian (2017)** — *Estimating Difference-in-Differences in the Presence of Spillovers*, IZA Discussion Paper No. 10984. (Diagnóstico de spillovers espaciais).
5. **Holte, J. H. et al. (2015/2020)** — *The impact of financial incentives on physician retention in rural and remote areas*, **Health Policy** / **Human Resources for Health**. (Evidência nórdica de incentivos no interior).
6. **Scheffer, Mário et al. (2023/2025)** — *Demografia Médica no Brasil*, FMUSP/CFM. (Diagnóstico estrutural da escassez de especialistas no interior do Brasil).
7. **Soares, Sergei; Barbosa, Rogério (2020)** — *A Oferta e a Distribuição Geográfica de Médicos no Brasil*, IPEA TD. (Mobilidade e fixação no território nacional).
8. **Davis, Steven J.; Faberman, R. J.; Haltiwanger, J. (2012)** — *Labor Market Flows, Job Openings, and Vacancy Chains*, NBER WP 18274. (Fundamentação de fluxos de vagas e contratações).

---

## 7. Roteiro Operacional de Entrega da Ficha de Leitura

Cada membro preencherá uma ficha padronizada em **4 blocos sintéticos**:
1. **O Mecanismo de Atração / Retenção / Bolsa (1 parágrafo):** Qual é a hipótese, equação ou parâmetro estimado de resposta à remuneração e ao isolamento?
2. **Dados e Identificação Causal (1 parágrafo):** Qual a base de dados (painel, coorte, experimento) e como os autores isolam a causalidade?
3. **Figura ou Tabela de Referência (1 item):** Qual gráfico (curva de sobrevida, estudo de evento, elasticidade) serve de espelho visual para o nosso estudo?
4. **Conexão Direta com o PMM-E no Interior (2–3 tópicos):** Como o paper fundamenta nossa modelagem de bolsas, o uso do IVS 2010 ou a decomposição de fluxos no CNES?
"""

with open(OUT_MD_PATH, "w", encoding="utf-8") as f:
    f.write(md_content)

print("docs/08_plano_leitura_equipe_literatura.md atualizado com sucesso.")

