# -*- coding: utf-8 -*-
"""
scripts/avaliar_rubrica_literatura.py
Aplica a rúbrica estratégica multidimensional para avaliar exaustivamente a contribuição teórica e empírica de cada paper para o estudo do PMM-E.
"""

import json
import os
import pandas as pd

# Pool completo de 22 papers examinados detalhadamente
CANDIDATE_PAPERS = [
    # 1. Acemoglu & Finkelstein (2008)
    {
        "id": "PAPER_01",
        "autores": "Acemoglu, Daron; Finkelstein, Amy",
        "ano": 2008,
        "titulo": "Input and Technology Choices in Regulated Industries: Evidence from the Health Care Sector",
        "periodico": "Journal of Political Economy",
        "volume_edicao": "Vol. 116, No. 5, pp. 837–880",
        "doi": "10.1086/595015",
        "paginas_total": 44,
        "paginas_foco": "pp. 839-858 (Seções I a III: 20 págs)",
        "tipo": "Teoria + Quase-Experimento Hospitalar",
        "resumo_analitico": "Desenvolve modelo formal de otimização de custo hospitalar sob regulação de preços onde a firma escolhe capital (K) e trabalho (L) com tecnologia (T). Mostra que choques no custo relativo do trabalho alteram a intensidade de capital e adoção tecnológica nos hospitais.",
        "aderencia_pmme": "Excelente microfundamentação teórica para modelar como a introdução do médico especialista do PMM-E interage com o capital físico instalado (leitos cirúrgicos, tomógrafos).",
        # Notas da Rúbrica Teórica (0 a 25 cada, total 100)
        "t1_modelo_formal": 25,
        "t2_mecanismo_pmme": 24,
        "t3_microfundamentacao": 25,
        "t4_digestibilidade": 22,
        # Notas da Rúbrica Empírica (0 a 25 cada, total 100)
        "e1_identificacao": 24,
        "e2_dados_contexto": 21,
        "e3_worker_flows": 18,
        "e4_robustez_spillovers": 22
    },
    # 2. Agarwal (2015)
    {
        "id": "PAPER_02",
        "autores": "Agarwal, Nikhil",
        "ano": 2015,
        "titulo": "An Empirical Model of the Medical Match",
        "periodico": "American Economic Review",
        "volume_edicao": "Vol. 105, No. 7, pp. 1939–1978",
        "doi": "10.1257/aer.20130663",
        "paginas_total": 40,
        "paginas_foco": "pp. 1940-1958 (Seções I a III: 18 págs)",
        "tipo": "Design de Mercados + Estimação Estrutural de Preferências",
        "resumo_analitico": "Modela o mercado de residência e alocação médica sob matching centralizado com restrições de capacidade. Estima estruturalmente o trade-off entre prestígio hospitalar, localização urbana e diferenciais salariais/bolsas.",
        "aderencia_pmme": "Modela teoricamente o papel do edital público centralizado do PMM-E em resolver falhas de coordenação e estima as preferências locacionais dos especialistas.",
        "t1_modelo_formal": 25,
        "t2_mecanismo_pmme": 25,
        "t3_microfundamentacao": 24,
        "t4_digestibilidade": 21,
        "e1_identificacao": 25,
        "e2_dados_contexto": 22,
        "e3_worker_flows": 20,
        "e4_robustez_spillovers": 21
    },
    # 3. Roback (1982)
    {
        "id": "PAPER_03",
        "autores": "Roback, Jennifer",
        "ano": 1982,
        "titulo": "Wages, Rents, and the Quality of Life: A General Equilibrium Model of Geographic Differences",
        "periodico": "Journal of Political Economy",
        "volume_edicao": "Vol. 90, No. 6, pp. 1257–1278",
        "doi": "10.1086/261120",
        "paginas_total": 22,
        "paginas_foco": "Artigo completo (22 págs)",
        "tipo": "Modelo Teórico Canônico de Equilíbrio Geral Espacial",
        "resumo_analitico": "Modelo canônico que determina simultaneamente salários e aluguéis em equilíbrio espacial. Mostra que regiões com desamenidades (isolamento, baixa infraestrutura) exigem diferenciais salariais compensatórios (\Delta w).",
        "aderencia_pmme": "Base teórica fundamental para justificar a running variable do IVS e as faixas de bolsa diferenciadas no PMM-E.",
        "t1_modelo_formal": 25,
        "t2_mecanismo_pmme": 25,
        "t3_microfundamentacao": 23,
        "t4_digestibilidade": 24,
        "e1_identificacao": 18,
        "e2_dados_contexto": 18,
        "e3_worker_flows": 15,
        "e4_robustez_spillovers": 20
    },
    # 4. Sivey et al. (2012)
    {
        "id": "PAPER_04",
        "autores": "Sivey, Peter; Scott, Anthony; Witt, Julia; Joyce, Catherine; Humphreys, John",
        "ano": 2012,
        "titulo": "Junior Doctors' Preferences for Specialty Choice",
        "periodico": "Journal of Health Economics",
        "volume_edicao": "Vol. 31, No. 6, pp. 813–826",
        "doi": "10.1016/j.jhealeco.2012.07.001",
        "paginas_total": 14,
        "paginas_foco": "Artigo completo (14 págs - super conciso)",
        "tipo": "Modelo de Utilidade Aleatória + Discrete Choice Experiment",
        "resumo_analitico": "Modela as escolhas de médicos em início de carreira através de Random Utility Models, mensurando elasticidades e Willingness to Accept (WTA) para postos no interior versus capitais.",
        "aderencia_pmme": "Microfundamentação direta da curva de oferta de médicos especialistas frente a incentivos monetários e condições de carga horária hospitalar.",
        "t1_modelo_formal": 24,
        "t2_mecanismo_pmme": 24,
        "t3_microfundamentacao": 24,
        "t4_digestibilidade": 25,
        "e1_identificacao": 23,
        "e2_dados_contexto": 22,
        "e3_worker_flows": 21,
        "e4_robustez_spillovers": 19
    },
    # 5. Baicker & Staiger (2005)
    {
        "id": "PAPER_05",
        "autores": "Baicker, Katherine; Staiger, Douglas",
        "ano": 2005,
        "titulo": "Fiscal Shenanigans, Targeted Federal Health Care Funds, and Patient Mortality",
        "periodico": "Quarterly Journal of Economics",
        "volume_edicao": "Vol. 120, No. 1, pp. 345–386",
        "doi": "10.1162/0033553053317416",
        "paginas_total": 42,
        "paginas_foco": "pp. 348-360 (Seção II: Teoria, 12 págs)",
        "tipo": "Teoria Microeconômica Fiscal + Quase-Experimento em Saúde",
        "resumo_analitico": "Modela o comportamento de governos locais que recebem recursos federais vinculados à saúde e remanejam recursos próprios, gerando crowding-out fiscal e efeitos heterogêneos na mortalidade.",
        "aderencia_pmme": "Base teórica essencial para o teste de substituição do PMM-E: o município substitui contratações próprias por bolsas federais?",
        "t1_modelo_formal": 24,
        "t2_mecanismo_pmme": 25,
        "t3_microfundamentacao": 25,
        "t4_digestibilidade": 22,
        "e1_identificacao": 24,
        "e2_dados_contexto": 21,
        "e3_worker_flows": 19,
        "e4_robustez_spillovers": 22
    },
    # 6. Holmstrom & Milgrom (1991)
    {
        "id": "PAPER_06",
        "autores": "Holmstrom, Bengt; Milgrom, Paul",
        "ano": 1991,
        "titulo": "Multitask Principal-Agent Analyses: Incentive Contracts, Asset Ownership, and Job Design",
        "periodico": "Journal of Law, Economics, & Organization",
        "volume_edicao": "Vol. 7, Special Issue, pp. 24–52",
        "doi": "10.1093/jleo/7.special_issue.24",
        "paginas_total": 29,
        "paginas_foco": "pp. 24-38 (Seções 1 a 3: 15 págs)",
        "tipo": "Teoria de Contratos e Desenho de Mecanismos",
        "resumo_analitico": "Modelo seminal de agência com múltiplos objetivos. Prova que incentivos fortes em tarefas de fácil medição distorcem o esforço e reduzem o desempenho em tarefas qualitativas.",
        "aderencia_pmme": "Modela a estrutura híbrida do PMM-E (carga assistencial hospitalar versus formação acadêmica/residência).",
        "t1_modelo_formal": 25,
        "t2_mecanismo_pmme": 23,
        "t3_microfundamentacao": 22,
        "t4_digestibilidade": 23,
        "e1_identificacao": 15,
        "e2_dados_contexto": 14,
        "e3_worker_flows": 12,
        "e4_robustez_spillovers": 14
    },
    # 7. Chandra & Skinner (2012)
    {
        "id": "PAPER_07",
        "autores": "Chandra, Amitabh; Skinner, Jonathan S.",
        "ano": 2012,
        "titulo": "Technology Growth and Expenditure Growth in Health Care",
        "periodico": "Journal of Economic Literature",
        "volume_edicao": "Vol. 50, No. 3, pp. 645–680",
        "doi": "10.1257/jel.50.3.645",
        "paginas_total": 36,
        "paginas_foco": "pp. 646-664 (Seções 1 a 3: 18 págs)",
        "tipo": "Modelagem de Produtividade Médica e Teoria da Tecnologia",
        "resumo_analitico": "Classifica tecnologias médicas em três categorias de custo-efetividade e modela a estrita complementaridade entre habilidades médicas especializadas e capital hospitalar de ponta.",
        "aderencia_pmme": "Demonstra que a produtividade médica do especialista depende de infraestrutura física complementar nos hospitais do SUS.",
        "t1_modelo_formal": 23,
        "t2_mecanismo_pmme": 25,
        "t3_microfundamentacao": 22,
        "t4_digestibilidade": 23,
        "e1_identificacao": 20,
        "e2_dados_contexto": 21,
        "e3_worker_flows": 16,
        "e4_robustez_spillovers": 19
    },
    # 8. Arrow (1963)
    {
        "id": "PAPER_08",
        "autores": "Arrow, Kenneth J.",
        "ano": 1963,
        "titulo": "Uncertainty and the Welfare Economics of Medical Care",
        "periodico": "American Economic Review",
        "volume_edicao": "Vol. 53, No. 5, pp. 941–973",
        "doi": "10.1016/B978-0-12-214850-7.50028-0",
        "paginas_total": 33,
        "paginas_foco": "Seções B e C (pp. 948-965: 17 págs)",
        "tipo": "Economia do Bem-Estar e Teoria Microeconômica Fundamental",
        "resumo_analitico": "Artigo fundador da Economia da Saúde. Demonstra a falha dos teoremas do bem-estar no mercado de cuidados médicos devido a assimetrias de informação e incerteza.",
        "aderencia_pmme": "Justificativa normativa canônica da intervenção pública federal para regular e prover especialistas onde o mercado privado falha.",
        "t1_modelo_formal": 23,
        "t2_mecanismo_pmme": 21,
        "t3_microfundamentacao": 20,
        "t4_digestibilidade": 22,
        "e1_identificacao": 12,
        "e2_dados_contexto": 14,
        "e3_worker_flows": 10,
        "e4_robustez_spillovers": 12
    },
    # 9. Currie & MacLeod (2017)
    {
        "id": "PAPER_09",
        "autores": "Currie, Janet; MacLeod, W. Bentley",
        "ano": 2017,
        "titulo": "Diagnosing Expertise: Human Capital, Decision Making, and Performance among Physicians",
        "periodico": "Journal of Labor Economics",
        "volume_edicao": "Vol. 35, No. 1, pp. 1–43",
        "doi": "10.1086/687848",
        "paginas_total": 43,
        "paginas_foco": "pp. 4-20 (Modelo Teórico de Diagnóstico: 16 págs)",
        "tipo": "Teoria da Decisão Médica + Quase-Experimento em Saúde",
        "resumo_analitico": "Modela teoricamente a tomada de decisão do especialista médico sob incerteza diagnóstica e testa empiricamente o impacto da expertise e treinamento nos desfechos do paciente.",
        "aderencia_pmme": "Excelente para modelar o canal da qualidade da atenção especializada e resolutividade clínica proporcionada pela formação do PMM-E.",
        "t1_modelo_formal": 24,
        "t2_mecanismo_pmme": 21,
        "t3_microfundamentacao": 23,
        "t4_digestibilidade": 20,
        "e1_identificacao": 24,
        "e2_dados_contexto": 21,
        "e3_worker_flows": 17,
        "e4_robustez_spillovers": 21
    },
    # 10. Gordon (2004)
    {
        "id": "PAPER_10",
        "autores": "Gordon, Nora",
        "ano": 2004,
        "titulo": "Do Federal Grants Boost School Spending? Evidence from Title I",
        "periodico": "Journal of Public Economics",
        "volume_edicao": "Vol. 88, No. 9-10, pp. 1771–1792",
        "doi": "10.1016/j.jpubeco.2003.09.002",
        "paginas_total": 22,
        "paginas_foco": "Artigo completo (22 págs)",
        "tipo": "Modelo Teórico de Federalismo Fiscal + Quase-Experimento",
        "resumo_analitico": "Modela o comportamento intertemporal de governos locais que recebem subsídios federais e reduzem gastos próprios no médio prazo (crowding-out dinâmico).",
        "aderencia_pmme": "Base teórica para demonstrar a resposta dinâmica dos municípios ao longo dos meses pós-anúncio do PMM-E.",
        "t1_modelo_formal": 23,
        "t2_mecanismo_pmme": 22,
        "t3_microfundamentacao": 23,
        "t4_digestibilidade": 23,
        "e1_identificacao": 23,
        "e2_dados_contexto": 18,
        "e3_worker_flows": 16,
        "e4_robustez_spillovers": 20
    },
    # 11. Kline & Moretti (2014)
    {
        "id": "PAPER_11",
        "autores": "Kline, Patrick; Moretti, Enrico",
        "ano": 2014,
        "titulo": "People, Places, and Public Policy: Some Simple Analytics of Local Economic Development Programs",
        "periodico": "Annual Review of Economics",
        "volume_edicao": "Vol. 6, No. 1, pp. 629–662",
        "doi": "10.1146/annurev-economics-080213-040845",
        "paginas_total": 34,
        "paginas_foco": "pp. 631-648 (Seções 1 a 3: 17 págs)",
        "tipo": "Modelagem Analítica de Políticas Baseadas no Lugar (Place-Based)",
        "resumo_analitico": "Desenvolve um framework analítico transparente de equilíbrio espacial para avaliar políticas de subsídios regionais, spillovers de aglomeração e ganhos de bem-estar.",
        "aderencia_pmme": "Permite formular o PMM-E como uma política de desenvolvimento regional de saúde (place-based healthcare policy).",
        "t1_modelo_formal": 24,
        "t2_mecanismo_pmme": 21,
        "t3_microfundamentacao": 22,
        "t4_digestibilidade": 21,
        "e1_identificacao": 21,
        "e2_dados_contexto": 19,
        "e3_worker_flows": 18,
        "e4_robustez_spillovers": 23
    },
    # 12. Roth (1984)
    {
        "id": "PAPER_12",
        "autores": "Roth, Alvin E.",
        "ano": 1984,
        "titulo": "The Evolution of the Labor Market for Medical Interns and Residents: A Case Study in Game Theory",
        "periodico": "Journal of Political Economy",
        "volume_edicao": "Vol. 92, No. 6, pp. 991–1016",
        "doi": "10.1086/261272",
        "paginas_total": 26,
        "paginas_foco": "pp. 992-1010 (Seções I a IV: 18 págs)",
        "tipo": "Teoria dos Jogos e Design de Mercados Médicos",
        "resumo_analitico": "Demonstra como mercados médicos descentralizados sofrem unraveling e assimetrias de informação, e como mecanismos de matching centralizado produzem alocações estáveis.",
        "aderencia_pmme": "Explica o papel de coordenação do edital público do Ministério da Saúde na mitigação de custos de busca.",
        "t1_modelo_formal": 24,
        "t2_mecanismo_pmme": 23,
        "t3_microfundamentacao": 21,
        "t4_digestibilidade": 23,
        "e1_identificacao": 18,
        "e2_dados_contexto": 18,
        "e3_worker_flows": 16,
        "e4_robustez_spillovers": 17
    },
    # 13. Carrillo & Feres (2019)
    {
        "id": "PAPER_13",
        "autores": "Carrillo, Paul; Feres, Pedro",
        "ano": 2019,
        "titulo": "Provider Supply, Utilization, and Infant Health: Evidence from a Physician Distribution Policy",
        "periodico": "American Economic Journal: Economic Policy",
        "volume_edicao": "Vol. 11, No. 3, pp. 156–196",
        "doi": "10.1257/pol.20170500",
        "paginas_total": 41,
        "paginas_foco": "Seções II, IV e Figuras (~20 págs)",
        "tipo": "Quase-Experimento + Estudo de Evento Dinâmico (SUS)",
        "resumo_analitico": "Avaliação de impacto quase-experimental utilizando regras de pontuação do edital do PMM e estudo de evento dinâmico de alta precisão sobre o CNES, SIM e SINASC.",
        "aderencia_pmme": "Padrão de excelência de gráficos de estudo de evento e verificação de pré-tendências no SUS.",
        "t1_modelo_formal": 21,
        "t2_mecanismo_pmme": 23,
        "t3_microfundamentacao": 23,
        "t4_digestibilidade": 21,
        "e1_identificacao": 25,
        "e2_dados_contexto": 25,
        "e3_worker_flows": 23,
        "e4_robustez_spillovers": 24
    },
    # 14. Sliwa Ruiz, Becker, Hone & Rocha (2024)
    {
        "id": "PAPER_14",
        "autores": "Sliwa Ruiz, Julia; Becker, Sascha O.; Hone, Thomas; Rocha, Rudi",
        "ano": 2024,
        "titulo": "The Supply of Primary Care Physicians and Population Health: Evidence from the Sudden Departure of Cuban Doctors in Brazil",
        "periodico": "Journal of Health Economics",
        "volume_edicao": "Vol. 93, Artigo 102833",
        "doi": "10.1016/j.jhealeco.2023.102833",
        "paginas_total": 18,
        "paginas_foco": "Artigo completo (18 págs)",
        "tipo": "Painel Mensal Longitudinal do CNES + Estudo de Evento",
        "resumo_analitico": "Uso de painel longitudinal mensal do CNES para captar um choque exógeno abrupto na oferta médica e mensurar a capacidade de recomposição e perdas assistenciais.",
        "aderencia_pmme": "Validação direta do uso do CNES mensal como painel de alta frequência para rastrear entradas, saídas e substituição.",
        "t1_modelo_formal": 20,
        "t2_mecanismo_pmme": 22,
        "t3_microfundamentacao": 22,
        "t4_digestibilidade": 24,
        "e1_identificacao": 25,
        "e2_dados_contexto": 25,
        "e3_worker_flows": 25,
        "e4_robustez_spillovers": 24
    },
    # 15. Fontes, Conceição & Jacinto (2018)
    {
        "id": "PAPER_15",
        "autores": "Fontes, Luiz Felipe Campos; Conceição, Otavio Canozzi; Jacinto, Paulo de Andrade",
        "ano": 2018,
        "titulo": "Evaluating the Impact of Physicians' Provision on Primary Healthcare: Evidence from Brazil's More Doctors Program",
        "periodico": "Health Economics",
        "volume_edicao": "Vol. 27, No. 8, pp. 1284–1299",
        "doi": "10.1002/hec.3768",
        "paginas_total": 16,
        "paginas_foco": "Artigo completo (16 págs)",
        "tipo": "Diferença em Diferenças com Pareamento (PSM-DiD)",
        "resumo_analitico": "Avaliação quase-experimental do Mais Médicos usando bases administrativas do DATASUS (CNES, SIA, SIH) para medir impacto sobre consultas e internações sensíveis (ICSAP).",
        "aderencia_pmme": "Referência direta para pipeline de dados do DATASUS e variáveis de controle municipal de baseline.",
        "t1_modelo_formal": 19,
        "t2_mecanismo_pmme": 22,
        "t3_microfundamentacao": 21,
        "t4_digestibilidade": 24,
        "e1_identificacao": 24,
        "e2_dados_contexto": 25,
        "e3_worker_flows": 22,
        "e4_robustez_spillovers": 23
    },
    # 16. Gravelle, Scott, Yong & McGrail (2018)
    {
        "id": "PAPER_16",
        "autores": "Gravelle, Hugh; Scott, Anthony; Yong, Jongsay; McGrail, Matthew",
        "ano": 2018,
        "titulo": "Do Rural Incentives Payments Affect Entries and Exits of General Practitioners?",
        "periodico": "Social Science & Medicine",
        "volume_edicao": "Vol. 216, pp. 88–96",
        "doi": "10.1016/j.socscimed.2018.09.041",
        "paginas_total": 9,
        "paginas_foco": "Artigo completo (9 págs - cirúrgico)",
        "tipo": "Modelos de Contagem em Painel com Efeitos Fixos",
        "resumo_analitico": "Decompõe econometricamente o impacto de bônus financeiros sobre taxas brutas de entrada versus taxas brutas de saída de médicos no interior.",
        "aderencia_pmme": "Inspiração econométrica direta para a nossa decomposição em níveis de novos entrantes, saídas e saldo líquido (Tabela 3).",
        "t1_modelo_formal": 21,
        "t2_mecanismo_pmme": 23,
        "t3_microfundamentacao": 23,
        "t4_digestibilidade": 25,
        "e1_identificacao": 24,
        "e2_dados_contexto": 23,
        "e3_worker_flows": 25,
        "e4_robustez_spillovers": 23
    },
    # 17. Pathman et al. (2004)
    {
        "id": "PAPER_17",
        "autores": "Pathman, Donald E.; Konrad, Thomas R.; King, Tonya S.; Taylor, Donald H.; Koch, Gary G.",
        "ano": 2004,
        "titulo": "Outcomes of States' Scholarship, Loan Repayment, and Related Programs for Physicians",
        "periodico": "Medical Care",
        "volume_edicao": "Vol. 42, No. 6, pp. 560–568",
        "doi": "10.1097/01.mlr.0000128004.26577.8b",
        "paginas_total": 9,
        "paginas_foco": "Artigo completo (9 págs)",
        "tipo": "Estudo de Coorte Longitudinal de Retenção",
        "resumo_analitico": "Acompanha coortes de médicos em programas estaduais dos EUA, demonstrando que a permanência é alta durante a bolsa mas cai rapidamente após o fim da obrigação.",
        "aderencia_pmme": "Fundamenta a separação entre coorte madura aos 6 meses e censura aos 12 meses.",
        "t1_modelo_formal": 18,
        "t2_mecanismo_pmme": 21,
        "t3_microfundamentacao": 20,
        "t4_digestibilidade": 25,
        "e1_identificacao": 23,
        "e2_dados_contexto": 23,
        "e3_worker_flows": 24,
        "e4_robustez_spillovers": 22
    },
    # 18. Russell, McGrail & Humphreys (2021)
    {
        "id": "PAPER_18",
        "autores": "Russell, Deborah J.; McGrail, Matthew R.; Humphreys, John S.",
        "ano": 2021,
        "titulo": "Determinants of Rural Australian General Practitioner Retention: A Longitudinal Analysis",
        "periodico": "Human Resources for Health",
        "volume_edicao": "Vol. 19, Artigo 7",
        "doi": "10.1186/s12960-020-00549-3",
        "paginas_total": 10,
        "paginas_foco": "Artigo completo (10 págs)",
        "tipo": "Análise de Sobrevida (Kaplan-Meier + Modelo de Cox)",
        "resumo_analitico": "Estima os determinantes do tempo até a evasão médica em municípios rurais em função do porte populacional, isolamento e suporte hospitalar.",
        "aderencia_pmme": "Orienta testes de heterogeneidade da retenção por porte e vulnerabilidade (IVS).",
        "t1_modelo_formal": 18,
        "t2_mecanismo_pmme": 21,
        "t3_microfundamentacao": 20,
        "t4_digestibilidade": 25,
        "e1_identificacao": 23,
        "e2_dados_contexto": 23,
        "e3_worker_flows": 25,
        "e4_robustez_spillovers": 22
    },
    # 19. Bärnighausen & Bloom (2009)
    {
        "id": "PAPER_19",
        "autores": "Bärnighausen, Till; Bloom, David E.",
        "ano": 2009,
        "titulo": "Financial Incentives for Return of Service in Underserved Areas: A Systematic Review",
        "periodico": "BMC Health Services Research",
        "volume_edicao": "Vol. 9, Artigo 86",
        "doi": "10.1186/1472-6963-9-86",
        "paginas_total": 17,
        "paginas_foco": "Artigo completo (17 págs)",
        "tipo": "Revisão Sistemática Global de 43 Programas Internacionais",
        "resumo_analitico": "Taxonomia comparativa e síntese de evidências sobre 43 programas de incentivos financeiros condicionados a serviço médico obrigatório em 10 países.",
        "aderencia_pmme": "Fornece a régua de benchmark internacional para situar as taxas de cumprimento e custos do PMM-E.",
        "t1_modelo_formal": 19,
        "t2_mecanismo_pmme": 21,
        "t3_microfundamentacao": 19,
        "t4_digestibilidade": 24,
        "e1_identificacao": 22,
        "e2_dados_contexto": 23,
        "e3_worker_flows": 22,
        "e4_robustez_spillovers": 21
    },
    # 20. Diamond (2016)
    {
        "id": "PAPER_20",
        "autores": "Diamond, Rebecca",
        "ano": 2016,
        "titulo": "The Determinants and Welfare Implications of US Workers' Diverging Location Choices by Skill: 1980–2000",
        "periodico": "American Economic Review",
        "volume_edicao": "Vol. 106, No. 3, pp. 479–524",
        "doi": "10.1257/aer.20131706",
        "paginas_total": 46,
        "paginas_foco": "pp. 482-498 (Modelo Teórico: 16 págs)",
        "tipo": "Equilíbrio Espacial com Amenidades Endógenas",
        "resumo_analitico": "Modela como a concentração de trabalhadores qualificados altera as amenidades locais endógenas, ampliando a divergência geográfica de bem-estar.",
        "aderencia_pmme": "Explica por que médicos especialistas tendem a se auto-reforçar nas grandes cidades sem políticas públicas ativas de indução.",
        "t1_modelo_formal": 24,
        "t2_mecanismo_pmme": 21,
        "t3_microfundamentacao": 21,
        "t4_digestibilidade": 20,
        "e1_identificacao": 23,
        "e2_dados_contexto": 19,
        "e3_worker_flows": 18,
        "e4_robustez_spillovers": 21
    },
    # 21. Finkelstein, Gentzkow & Williams (2016)
    {
        "id": "PAPER_21",
        "autores": "Finkelstein, Amy; Gentzkow, Matthew; Williams, Heidi",
        "ano": 2016,
        "titulo": "Sources of Geographic Variation in Health Care: Evidence From Patient Migration",
        "periodico": "Quarterly Journal of Economics",
        "volume_edicao": "Vol. 131, No. 4, pp. 1681–1726",
        "doi": "10.1093/qje/qjw023",
        "paginas_total": 46,
        "paginas_foco": "pp. 1684-1700 (Seções I a III: 16 págs)",
        "tipo": "Modelo de Prática Médica + Painel com Migração",
        "resumo_analitico": "Separa estruturalmente se a variação geográfica nos gastos e procedimentos de saúde decorre de características do paciente (demanda) ou do estilo de prática médica local (oferta).",
        "aderencia_pmme": "Fundamenta por que fixar especialistas altera a função de produção médica local e os padrões de utilização do SUS.",
        "t1_modelo_formal": 23,
        "t2_mecanismo_pmme": 22,
        "t3_microfundamentacao": 23,
        "t4_digestibilidade": 20,
        "e1_identificacao": 25,
        "e2_dados_contexto": 22,
        "e3_worker_flows": 21,
        "e4_robustez_spillovers": 23
    },
    # 22. Olden & Møen (2022)
    {
        "id": "PAPER_22",
        "autores": "Olden, Andreas; Møen, Jarle",
        "ano": 2022,
        "titulo": "The Triple Difference Estimator",
        "periodico": "The Econometrics Journal",
        "volume_edicao": "Vol. 25, No. 3, pp. 606–622",
        "doi": "10.1093/ectj/utac010",
        "paginas_total": 17,
        "paginas_foco": "Artigo completo (17 págs)",
        "tipo": "Econometria Teórica e Identificação Causal",
        "resumo_analitico": "Formaliza as hipóteses de identificação do estimador DDD em relação ao DiD tradicional, provando como o terceiro contraste elimina choques contemporâneos não observados.",
        "aderencia_pmme": "Justificativa metodológica canônica da nossa especificação primária município-curso-mês.",
        "t1_modelo_formal": 23,
        "t2_mecanismo_pmme": 22,
        "t3_microfundamentacao": 24,
        "t4_digestibilidade": 24,
        "e1_identificacao": 25,
        "e2_dados_contexto": 20,
        "e3_worker_flows": 18,
        "e4_robustez_spillovers": 24
    }
]

def calcular_scores(papers):
    for p in papers:
        p["score_teorico_total"] = p["t1_modelo_formal"] + p["t2_mecanismo_pmme"] + p["t3_microfundamentacao"] + p["t4_digestibilidade"]
        p["score_empirico_total"] = p["e1_identificacao"] + p["e2_dados_contexto"] + p["e3_worker_flows"] + p["e4_robustez_spillovers"]
        p["score_geral_ponderado"] = round(0.55 * p["score_teorico_total"] + 0.45 * p["score_empirico_total"], 2)
    return papers

def main():
    os.makedirs("output/revisao_literatura", exist_ok=True)
    os.makedirs("docs", exist_ok=True)
    
    papers = calcular_scores(CANDIDATE_PAPERS)
    df = pd.DataFrame(papers)
    
    # Salvar ranking completo
    df_sorted = df.sort_values(by="score_teorico_total", ascending=False)
    df_sorted.to_csv("output/revisao_literatura/ranking_rubrica_papers_completo.csv", index=False, encoding="utf-8-sig")
    with open("output/revisao_literatura/ranking_rubrica_papers_completo.json", "w", encoding="utf-8") as f:
        json.dump(papers, f, indent=2, ensure_ascii=False)
        
    print("Sucesso: 22 papers avaliados na rúbrica e exportados.")
    print("\n--- TOP 7 MAIORES NOTAS TEÓRICAS ---")
    top7 = df_sorted.head(7)
    for idx, row in top7.iterrows():
        print(f"[{row['score_teorico_total']} pts] {row['autores']} ({row['ano']}) - {row['titulo']} | Foco: {row['paginas_foco']}")

if __name__ == "__main__":
    main()
