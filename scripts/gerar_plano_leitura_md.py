# -*- coding: utf-8 -*-
import json

with open("output/revisao_literatura/matriz_evidencias_artigos_expandida.json", "r", encoding="utf-8") as f:
    papers = json.load(f)

md_content = """# 08. Plano Estratégico de Busca, Leitura da Literatura e Guia de Atribuição da Equipe

> **Projeto:** Avaliação de Impacto e Economia da Saúde — Programa Mais Médicos Especialistas (PMM-E / Lei nº 15.233/2025)  
> **Finalidade:** Protocolo formal de busca bibliográfica, seleção sistemática de literatura recente (2018–2026) e clássica, e guia de divisão de leitura para a equipe de pesquisa.  
> **Diretriz Metodológica Especial:** Adoção explícita da abordagem **"Teoria + Empiria"** (estilo Acemoglu/Finkelstein/Agarwal/Moretti), integrando modelos microeconômicos formais a identificações causais quase-experimentais em saúde.  
> **Data de Consolidação:** 30 de Agosto de 2026  

---

## 1. Protocolo de Busca Sistemática e Filtros Aplicados

Para construir uma base sólida e atualizada, estabelecemos um protocolo em **quatro etapas estruturadas**:

```mermaid
graph TD
    S1["Etapa 1: Formulação de Strings de Busca em 4 Clusters<br/>(Teoria Espacial, Contratos/Agência, Avaliações SUS, Retenção Global)"] --> S2["Etapa 2: Coleta em 5 Bases Acadêmicas<br/>(OpenAlex, PubMed, NBER/RePEc, Scopus/Web of Science, SciELO)"]
    S2 --> S3["Etapa 3: Triagem por Relevância Causal & Paradigma 'Teoria+Empiria'"]
    S3 --> S4["Etapa 4: Curadoria Final & Foco em Páginas Operacionais para a Equipe"]
    
    S4 --> T1["Tier 1: 7 Papers de Fundamentação Teórica / Modelagem Formal (Média foco: ~18 pp.)"]
    S4 --> T2["Tier 1: 7 Papers Empíricos / Quase-Experimentos Análogos (Média foco: ~16 pp.)"]
    S4 --> T3["Tier 2: 12+ Papers Recentes de Referência Complementar (2018–2026)"]
```

### 1.1 Clusters de Busca e Strings Booleanas Executadas

1. **Cluster A (Teoria do Mercado Médico & Equilíbrio Espacial):**
   `("physician labor supply" OR "specialist allocation" OR "compensating differentials" OR "spatial equilibrium") AND ("hospital capital" OR "factor substitution" OR "residency match")`
2. **Cluster B (Incentivos, Contratos Públicos & Crowding-Out):**
   `("public health incentives" OR "intergovernmental grants" OR "crowding-out" OR "multitask agency" OR "fiscal substitution") AND ("physician practice" OR "hospital supply")`
3. **Cluster C (Provimento Médico no Brasil & Avaliações Causais no SUS):**
   `("Mais Médicos" OR "PMM" OR "médicos especialistas" OR "CNES" OR "SIA-SUS" OR "SIH-SUS") AND ("difference-in-differences" OR "event study" OR "impact evaluation" OR "triple differences")`
4. **Cluster D (Políticas Internacionais de Retenção & Worker Flows):**
   `("physician retention" OR "return-of-service" OR "loan repayment" OR "worker flows" OR "entry and exit") AND ("rural" OR "underserved" OR "financial incentives")`

---

## 2. O Paradigma "Teoria + Empiria" (A Abordagem Acemoglu)

Em artigos de referência na Economia (como os de *Daron Acemoglu, Amy Finkelstein, Nikhil Agarwal e Enrico Moretti*), a seção teórica não é um mero resumo descritivo de conceitos: **é um modelo formal microeconômico que gera previsões testáveis e define a equação econométrica estimada na seção empírica**.

Nossa revisão incorpora esse paradigma em três frentes:
1. **Modelo de Escolha de Insumos Hospitalares (Acemoglu & Finkelstein, 2008 JPE):** Modela como a entrada de um especialista subsidiado altera a demanda por capital físico complementar (leitos e equipamentos diagnósticos) no hospital do SUS.
2. **Modelo de Matching no Mercado Médico com Fricções (Agarwal, 2015 AER):** Formaliza as preferências dos especialistas entre prestígio/infraestrutura urbana vs. bônus financeiro no interior, justificando o papel coordenador do edital centralizado do Ministério da Saúde.
3. **Modelo de Federalismo Fiscal e Substituição Local (Baicker & Staiger, 2005 QJE):** Modela as funções de utilidade do gestor municipal para prever se o repasse federal de bolsas gera expansão líquida ou *crowding-out* de médicos contratados pelo município.

---

## 3. Quadro Geral de Atribuição da Equipe (14 Membros)

Para viabilizar a leitura em 1 a 2 turnos, indicamos a **extensão total do artigo** e as **páginas de foco prioritário** (núcleo do modelo ou da identificação):

| ID | Categoria | Subtema / Pergunta Central | Autores & Ano | Periódico | Extensão Total | Páginas de Foco Prioritário |
|:---|:---|:---|:---|:---|:---|:---|
| **TEO_01** | Teoria + Empiria | Escolha de Insumos & Capital Hospitalar | Acemoglu & Finkelstein (2008) | *J. Polit. Econ.* | 44 págs | **Seções I a III (~20 págs)** |
| **TEO_02** | Teoria + Empiria | Matching Estrutural no Mercado Médico | Agarwal (2015) | *Am. Econ. Rev.* | 40 págs | **Seções I a III (~18 págs)** |
| **TEO_03** | Teórica | Equilíbrio Espacial e Salários | Roback (1982) | *J. Polit. Econ.* | 22 págs | **Artigo Completo (22 págs)** |
| **TEO_04** | Teoria + Empiria | Preferências e Trade-offs Locacionais (DCE) | Sivey et al. (2012) | *J. Health Econ.* | 14 págs | **Artigo Completo (14 págs)** |
| **TEO_05** | Teórica | Agência Multitarefa em Contratos Públicos | Holmstrom & Milgrom (1991) | *J. Law Econ. Org.* | 29 págs | **Seções 1 a 3 (~15 págs)** |
| **TEO_06** | Teoria + Empiria | Substituição Fiscal e Crowding-Out | Baicker & Staiger (2005) | *Q. J. Econ.* | 42 págs | **Seção II: Teoria (~12 págs)** |
| **TEO_07** | Teórica | Complementaridade Tecnológica Hospitalar | Chandra & Skinner (2012) | *J. Econ. Lit.* | 36 págs | **Seções 1 a 3 (~18 págs)** |
| **EMP_01** | Empírica | Provimento SUS e Desfechos (PMM) | Fontes et al. (2018) | *Health Econ.* | 16 págs | **Artigo Completo (16 págs)** |
| **EMP_02** | Empírica | Estudo de Evento e Oferta Médica no Brasil | Carrillo & Feres (2019) | *AEJ: Econ. Policy* | 41 págs | **Seções II, IV e Figs (~20 págs)** |
| **EMP_03** | Empírica | Choque em Painel CNES Mensal de Alta Freq. | Sliwa Ruiz et al. (2024) | *J. Health Econ.* | 18 págs | **Artigo Completo (18 págs)** |
| **EMP_04** | Empírica | Dinâmica de Fluxos de Médicos (Entradas/Saídas) | Gravelle et al. (2018) | *Soc. Sci. Med.* | 9 págs | **Artigo Completo (9 págs)** |
| **EMP_05** | Empírica | Acompanhamento Longitudinal de Retenção | Pathman et al. (2004) | *Medical Care* | 9 págs | **Artigo Completo (9 págs)** |
| **EMP_06** | Empírica | Sobrevivência e Fixação no Interior (Cox) | Russell et al. (2021) | *Hum. Resour. Health* | 10 págs | **Artigo Completo (10 págs)** |
| **EMP_07** | Empírica | Revisão Sistemática Global de Return-of-Service | Bärnighausen & Bloom (2009) | *BMC Health Serv. Res.* | 17 págs | **Artigo Completo (17 págs)** |

---

## 4. Fichas de Leitura — Fundamentação Teórica e "Teoria + Empiria" (7 Papers)

### [TEO_01] Acemoglu & Finkelstein (2008) — *Input and Technology Choices in Regulated Industries*
- **Referência:** Acemoglu, Daron; Finkelstein, Amy. (2008). *Input and Technology Choices in Regulated Industries: Evidence from the Health Care Sector*. **Journal of Political Economy**, 116(5), 837–880. DOI: [10.1086/595015](https://doi.org/10.1086/595015).
- **Extensão Total:** 44 páginas | **Foco de Leitura:** **Seções I a III (~20 páginas)**.
- **Estrutura Metodológica:** Formulação de modelo de otimização de custo hospitalar sob regulação de preços com função de produção $Y = F(K, L, T)$.
- **Aplicação Direta no PMM-E:** Fornece o arcabouço teórico para avaliar se a oferta de mão de obra médica subsidiada pela União ($L$) induz os hospitais locais a aumentarem sua intensidade de capital físico ($K$) ou se a ausência prévia de capital trava a absorção dos especialistas.
- **Roteiro do Leitor:** Extrair a condição de primeira ordem entre custo do trabalho e intensidade de capital para embasar nossa seção de heterogeneidade hospitalar.

---

### [TEO_02] Agarwal (2015) — *An Empirical Model of the Medical Match*
- **Referência:** Agarwal, Nikhil. (2015). *An Empirical Model of the Medical Match*. **American Economic Review**, 105(7), 1939–1978. DOI: [10.1257/aer.20130663](https://doi.org/10.1257/aer.20130663).
- **Extensão Total:** 40 páginas | **Foco de Leitura:** **Seções I a III (~18 páginas)**.
- **Estrutura Metodológica:** Modelo microeconômico de escolhas de médicos residentes sob matching centralizado com estimação estrutural de preferências locacionais e salariais.
- **Aplicação Direta no PMM-E:** Formaliza o mecanismo pelo qual editais públicos centralizados (como o PMM-E) superam falhas de coordenação no mercado de especialistas e como subsídios financeiros deslocam as escolhas locacionais dos formandos.
- **Roteiro do Leitor:** Sintetizar como o modelo mede o *trade-off* entre o prestígio acadêmico da instituição e a remuneração monetária.

---

### [TEO_03] Roback (1982) — *Wages, Rents, and the Quality of Life*
- **Referência:** Roback, Jennifer. (1982). *Wages, Rents, and the Quality of Life: A General Equilibrium Model of Geographic Differences*. **Journal of Political Economy**, 90(6), 1257–1278. DOI: [10.1086/261120](https://doi.org/10.1086/261120).
- **Extensão Total:** **22 páginas (Artigo completo)**.
- **Estrutura Metodológica:** Modelo canônico de equilíbrio geral espacial hedônico de localização de trabalhadores e firmas.
- **Aplicação Direta no PMM-E:** Fundamenta por que as faixas de bolsa do PMM-E precisam ser diferenciadas pelo IVS: o diferencial salarial compensatório ($\Delta w$) deve cobrir o custo de isolamento e a carência de amenidades municipais.
- **Roteiro do Leitor:** Escrever 1 parágrafo formalizando o equilíbrio espacial médico entre amenidades, custo de vida e valor da bolsa.

---

### [TEO_04] Sivey et al. (2012) — *Junior Doctors' Preferences for Specialty Choice*
- **Referência:** Sivey, Peter; Scott, Anthony; Witt, Julia; Joyce, Catherine; Humphreys, John. (2012). *Junior Doctors' Preferences for Specialty Choice*. **Journal of Health Economics**, 31(6), 813–826. DOI: [10.1016/j.jhealeco.2012.07.001](https://doi.org/10.1016/j.jhealeco.2012.07.001).
- **Extensão Total:** **14 páginas (Artigo completo - leitura rápida)**.
- **Estrutura Metodológica:** Modelo de utilidade aleatória (RUM) e experimento de escolha discreta com cálculo de *Willingness to Accept* (WTA).
- **Aplicação Direta no PMM-E:** Fornece estimativas empíricas da elasticidade de médicos em início de carreira em relação à flexibilidade de horários, oportunidades de prática privada e remuneração.
- **Roteiro do Leitor:** Focar na Tabela 3 de parâmetros estimados e identificar qual característica contratual mais reduz a desutilidade de postos no interior.

---

### [TEO_05] Holmstrom & Milgrom (1991) — *Multitask Principal-Agent Analyses*
- **Referência:** Holmstrom, Bengt; Milgrom, Paul. (1991). *Multitask Principal-Agent Analyses: Incentive Contracts, Asset Ownership, and Job Design*. **Journal of Law, Economics, & Organization**, 7, 24–52. DOI: [10.1093/jleo/7.special_issue.24](https://doi.org/10.1093/jleo/7.special_issue.24).
- **Extensão Total:** 29 páginas | **Foco de Leitura:** **Seções 1 a 3 (~15 páginas)**.
- **Estrutura Metodológica:** Teoria dos contratos de agência com múltiplos objetivos concorrentes e esforço multidimensional.
- **Aplicação Direta no PMM-E:** Modela a tensão intrínseca do programa entre o cumprimento da carga horária assistencial hospitalar e a dedicação ao módulo de especialização acadêmica.
- **Roteiro do Leitor:** Explicar como a combinação de bolsa financeira com título de especialista cria um esquema de incentivos ótimo que mitiga a evasão.

---

### [TEO_06] Baicker & Staiger (2005) — *Fiscal Shenanigans, Targeted Federal Health Care Funds*
- **Referência:** Baicker, Katherine; Staiger, Douglas. (2005). *Fiscal Shenanigans, Targeted Federal Health Care Funds, and Patient Mortality*. **Quarterly Journal of Economics**, 120(1), 345–386. DOI: [10.1162/0033553053317416](https://doi.org/10.1162/0033553053317416).
- **Extensão Total:** 42 páginas | **Foco de Leitura:** **Seção II: Theoretical Framework (~12 páginas)**.
- **Estrutura Metodológica:** Modelo teórico de comportamento fiscal do governo local que maximiza utilidade orçamentária sob repasses federais vinculados à saúde.
- **Aplicação Direta no PMM-E:** Base formal para demonstrar por que municípios podem usar as bolsas federais de médicos especialistas para substituir despesas com contratos próprios de saúde (*crowding-out* fiscal).
- **Roteiro do Leitor:** Sintetizar a proposição teórica que demonstra as condições sob as quais ocorre substituição total de gastos locais.

---

### [TEO_07] Chandra & Skinner (2012) — *Technology Growth and Expenditure Growth in Health Care*
- **Referência:** Chandra, Amitabh; Skinner, Jonathan S. (2012). *Technology Growth and Expenditure Growth in Health Care*. **Journal of Economic Literature**, 50(3), 645–680. DOI: [10.1257/jel.50.3.645](https://doi.org/10.1257/jel.50.3.645).
- **Extensão Total:** 36 páginas | **Foco de Leitura:** **Seções 1 a 3 (~18 páginas)**.
- **Estrutura Metodológica:** Síntese analítica e modelagem da produtividade de tecnologias e especialidades em saúde (Categorias I, II e III).
- **Aplicação Direta no PMM-E:** Demonstra que a produtividade médica do especialista no SUS depende da infraestrutura diagnóstica e cirúrgica do município, justificando testes empíricos de heterogeneidade por complexidade de capital.
- **Roteiro do Leitor:** Mapear a taxonomia de tecnologias e classificar as 16 especialidades do edital do PMM-E em alta vs. baixa dependência de capital físico.

---

## 5. Fichas de Leitura — Literatura Empírica e Quase-Experimentos (7 Papers)

### [EMP_01] Fontes, Conceição & Jacinto (2018) — *Evaluating the More Doctors Program*
- **Referência:** Fontes, Luiz Felipe Campos; Conceição, Otavio Canozzi; Jacinto, Paulo de Andrade. (2018). *Evaluating the Impact of Physicians' Provision on Primary Healthcare: Evidence from Brazil's More Doctors Program*. **Health Economics**, 27(8), 1284–1299. DOI: [10.1002/hec.3768](https://doi.org/10.1002/hec.3768).
- **Extensão:** **16 páginas (Artigo completo)**.
- **Dados & Método:** Microdados municipais do DATASUS (CNES, SIA, SIH); Propensity Score Matching combinado com DiD (PSM-DiD).
- **Aplicação Direta no PMM-E:** Modelo prático de construção de variáveis de controle socioeconômico e mensuração de internações por condições sensíveis (ICSAP) no DATASUS.
- **Roteiro do Leitor:** Comparar as covariáveis municipais de baseline do modelo deles com a nossa especificação DDD canônica.

---

### [EMP_02] Carrillo & Feres (2019) — *Provider Supply, Utilization, and Infant Health*
- **Referência:** Carrillo, Paul; Feres, Pedro. (2019). *Provider Supply, Utilization, and Infant Health: Evidence from a Physician Distribution Policy*. **American Economic Journal: Economic Policy**, 11(3), 156–196. DOI: [10.1257/pol.20170500](https://doi.org/10.1257/pol.20170500).
- **Extensão:** 41 páginas | **Foco de Leitura:** **Seções II, IV e Figuras 2 e 3 (~20 páginas)**.
- **Dados & Método:** Quase-experimento com pontuação do edital do PMM; Estudo de evento mensal e DiD sobre o CNES, SIM e SINASC.
- **Aplicação Direta no PMM-E:** Referência visual e metodológica para a nossa Figura 1 (estudo de evento dinâmico) e teste formal de pré-tendências paralelas.
- **Roteiro do Leitor:** Avaliar como os autores reportam a ausência de pré-tendências diferenciais e o efeito dinâmico pós-intervenção.

---

### [EMP_03] Sliwa Ruiz, Becker, Hone & Rocha (2024) — *Sudden Departure of Cuban Doctors in Brazil*
- **Referência:** Sliwa Ruiz, Julia; Becker, Sascha O.; Hone, Thomas; Rocha, Rudi. (2024). *The Supply of Primary Care Physicians and Population Health: Evidence from the Sudden Departure of Cuban Doctors in Brazil*. **Journal of Health Economics**, 93, Artigo 102833. DOI: [10.1016/j.jhealeco.2023.102833](https://doi.org/10.1016/j.jhealeco.2023.102833).
- **Extensão:** **18 páginas (Artigo completo)**.
- **Dados & Método:** Painel municipal mensal do CNES integrado ao SISAB e SIH (2017–2019); Estudo de evento de alta frequência.
- **Aplicação Direta no PMM-E:** Validação metodológica direta do uso do CNES mensal como painel de alta frequência para rastrear saídas, recomposição de vagas e heterogeneidade por vulnerabilidade.
- **Roteiro do Leitor:** Analisar o tratamento dos microdados do CNES para lidar com rotatividade e duplicidades de profissionais.

---

### [EMP_04] Gravelle, Scott, Yong & McGrail (2018) — *Do Rural Incentives Payments Affect Entries and Exits?*
- **Referência:** Gravelle, Hugh; Scott, Anthony; Yong, Jongsay; McGrail, Matthew. (2018). *Do Rural Incentives Payments Affect Entries and Exits of General Practitioners?* **Social Science & Medicine**, 216, 88–96. DOI: [10.1016/j.socscimed.2018.09.041](https://doi.org/10.1016/j.socscimed.2018.09.041).
- **Extensão:** **9 páginas (Artigo cirúrgico e direto)**.
- **Dados & Método:** Painel longitudinal administrativo de médicos na Austrália; Modelos de Poisson com efeitos fixos sobre taxas brutas de entrada e saída.
- **Aplicação Direta no PMM-E:** Inspiração empírica direta para a nossa **Tabela 3 e Figura 4** (decomposição dos mecanismos em níveis de novos entrantes, saídas e saldo líquido).
- **Roteiro do Leitor:** Comparar as equações de taxas de entrada (*entry*) e saída (*exit*) com as nossas variáveis `n_entradas` e `n_saidas`.

---

### [EMP_05] Pathman et al. (2004) — *Outcomes of States' Scholarship, Loan Repayment Programs*
- **Referência:** Pathman, Donald E.; Konrad, Thomas R.; King, Tonya S.; Taylor, Donald H.; Koch, Gary G. (2004). *Outcomes of States' Scholarship, Loan Repayment, and Related Programs for Physicians*. **Medical Care**, 42(6), 560–568. DOI: [10.1097/01.mlr.0000128004.26577.8b](https://doi.org/10.1097/01.mlr.0000128004.26577.8b).
- **Extensão:** **9 páginas (Artigo completo)**.
- **Dados & Método:** Acompanhamento longitudinal de coortes de médicos em 35 estados norte-americanos (programas análogos ao NHSC).
- **Aplicação Direta no PMM-E:** Mostra que a retenção é alta durante a vigência do contrato, mas sofre queda acelerada após o fim da obrigação, fundamentando a análise da coorte de 6 meses e censura aos 12 meses.
- **Roteiro do Leitor:** Focar na Tabela 3 (curvas temporais de retenção) e listar os principais motivos declarados para evasão.

---

### [EMP_06] Russell, McGrail & Humphreys (2021) — *Determinants of Rural Australian GP Retention*
- **Referência:** Russell, Deborah J.; McGrail, Matthew R.; Humphreys, John S. (2021). *Determinants of Rural Australian General Practitioner Retention: A Longitudinal Analysis*. **Human Resources for Health**, 19, Artigo 7. DOI: [10.1186/s12960-020-00549-3](https://doi.org/10.1186/s12960-020-00549-3).
- **Extensão:** **10 páginas (Artigo completo)**.
- **Dados & Método:** Análise de sobrevida de Kaplan-Meier e modelos de riscos proporcionais de Cox sobre o tempo de permanência (*tenure*) de médicos no interior.
- **Aplicação Direta no PMM-E:** Orienta os testes de heterogeneidade da sobrevivência de especialistas no município por porte populacional, isolamento e infraestrutura hospitalar.
- **Roteiro do Leitor:** Focar nos *Hazard Ratios* da Tabela 2 e mapear quais fatores reduzem pela metade o risco de saída médica.

---

### [EMP_07] Bärnighausen & Bloom (2009) — *Financial Incentives for Return of Service*
- **Referência:** Bärnighausen, Till; Bloom, David E. (2009). *Financial Incentives for Return of Service in Underserved Areas: A Systematic Review*. **BMC Health Services Research**, 9, Artigo 86. DOI: [10.1186/1472-6963-9-86](https://doi.org/10.1186/1472-6963-9-86).
- **Extensão:** **17 páginas (Artigo completo)**.
- **Dados & Método:** Revisão sistemática global abrangendo 43 programas de provimento de recursos humanos em saúde em 10 países.
- **Aplicação Direta no PMM-E:** Fornece o benchmarking internacional para comparar taxas de adesão, cumprimento de contrato e custos por profissional fixado do PMM-E.
- **Roteiro do Leitor:** Focar na Tabela 1 (taxonomia de programas) e na Seção de Discussão sobre custo-efetividade.

---

## 6. Bibliografia Expandida de Referência Complementar (2018–2026)

Para aprofundamento durante a redação das seções empíricas e de discussão, a equipe dispõe do **Tier 2 de referências recentes**:

1. **Currie, Janet; MacLeod, W. Bentley (2017)** — *Diagnosing Expertise: Human Capital, Decision Making, and Performance among Physicians*, **Journal of Labor Economics**, 35(1), 1–43. (Modelo teórico e teste empírico de tomada de decisão diagnóstica de especialistas).
2. **Finkelstein, Amy; Gentzkow, Matthew; Williams, Heidi (2016)** — *Sources of Geographic Variation in Health Care: Evidence From Patient Migration*, **Quarterly Journal of Economics**, 131(4), 1681–1726. (Separação entre efeitos de demanda de pacientes e efeitos de oferta/prática médica local).
3. **Kline, Patrick; Moretti, Enrico (2014)** — *People, Places, and Public Policy: Some Simple Analytics of Local Economic Development Programs*, **Annual Review of Economics**, 6(1), 629–662. (Modelagem analítica de políticas baseadas no lugar e atração de mão de obra especializada).
4. **Diamond, Rebecca (2016)** — *The Determinants and Welfare Implications of US Workers' Diverging Location Choices by Skill: 1980–2000*, **American Economic Review**, 106(3), 479–524. (Equilíbrio espacial com amenidades endógenas e divergência de mão de obra qualificada).
5. **Mattos, Enlinson; Mazetto, Débora (2017/2020)** — *Short-Term Impacts of the Mais Médicos Program on Health Outcomes and Local Expenditures*, FGV EESP Working Paper / RBE. (Evidência sobre redução de internações e economia de recursos locais).
6. **Scheffer, Mário et al. (2023/2025)** — *Demografia Médica no Brasil*, FMUSP / AMB / CFM. (Diagnóstico estrutural da hiperconcentração de especialistas nas capitais e no setor privado).
7. **Soares, Sergei; Barbosa, Rogério (2020)** — *A Oferta e a Distribuição Geográfica de Médicos no Brasil*, IPEA Texto para Discussão. (Análise de mobilidade e estoques de médicos a partir do CNES e RAIS).
8. **Somville, Vincent (2020)** — *Financial Incentives and Physician Supply in Underserved Areas*, **World Development**, 127, 104764. (Avaliação quase-experimental de incentivos financeiros a profissionais de saúde).
9. **Olden, Andreas; Møen, Jarle (2022)** — *The Triple Difference Estimator*, **The Econometrics Journal**, 25(3), 606–622. (Formalização teórica do estimador DDD aplicado em mercados locais).
10. **Roth, Jonathan (2022)** — *Pretest with Caution: Event-Study Estimates After Testing for Parallel Trends*, **AER: Insights**, 4(3), 305–322. (Diretrizes econométricas para testes e reporte de estudos de evento).
11. **Davis, Steven J.; Faberman, R. Jason; Haltiwanger, John (2012)** — *Labor Market Flows, Job Openings, and Vacancy Chains*, **NBER Working Paper No. 18274**. (Fundamentação teórica de criação, destruição e transição de vagas).
12. **Clarke, Damian (2017)** — *Estimating Difference-in-Differences in the Presence of Spillovers*, **IZA Discussion Paper No. 10984**. (Econometria de spillovers espaciais entre municípios vizinhos).

---

## 7. Roteiro Operacional de Entrega da Ficha de Leitura

Cada membro da equipe preencherá uma ficha padronizada em **4 blocos sintéticos**:
1. **O Mecanismo Teórico / Pergunta Central (1 parágrafo):** Qual é a equação, o trade-off ou a hipótese econômica central formulada no artigo?
2. **Dados e Estratégia de Identificação (1 parágrafo):** Qual é a base de dados utilizada e como os autores isolam a relação causal?
3. **Figura ou Tabela de Referência (1 item):** Qual gráfico ou tabela do artigo serve de referência visual/metodológica para o nosso trabalho do PMM-E?
4. **Conexão Direta com o PMM-E (2–3 tópicos):** De que forma esse paper fundamenta nossa modelagem, justifica nossas escolhas empíricas (DDD, IVS, CNES mensal, fluxos) ou blinda nossos resultados contra críticas de arbitrariedade?
"""

with open("docs/08_plano_leitura_equipe_literatura.md", "w", encoding="utf-8") as f:
    f.write(md_content)

print("docs/08_plano_leitura_equipe_literatura.md atualizado com sucesso.")
