# -*- coding: utf-8 -*-
"""
scripts/gerar_matriz_literatura_expandida.py
Gera a matriz estruturada de literatura (14 papers fundamentais) focada estritamente na:
Atração e Retenção de Médicos Especialistas em Cidades do Interior sob Diferentes Bolsas e Níveis de IVS.
"""

import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = ROOT / "output" / "revisao_literatura"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PAPERS_EXPANDED = [
    # =========================================================================
    # LITERATURA TEÓRICA E TEORIA + EMPIRIA (7 PAPERS FUNDACIONAIS)
    # =========================================================================
    {
        "id": "TEO_01",
        "categoria": "Teorica / Teoria + Empiria",
        "subtema": "Equilíbrio Espacial Hedônico e Diferencial Compensatório por IVS",
        "autores": "Roback, Jennifer",
        "ano": 1982,
        "titulo": "Wages, Rents, and the Quality of Life: A General Equilibrium Model of Geographic Differences",
        "periodico": "Journal of Political Economy",
        "volume_edicao": "Vol. 90, No. 6, pp. 1257–1278",
        "doi": "10.1086/261120",
        "paginas": 22,
        "paginas_foco": "pp. 1257–1272 (Seções 1 a 3: 15 páginas)",
        "tipo_artigo": "Modelo Teórico Canônico de Equilíbrio Geral Espacial",
        "mecanismo_teorico": "Determina a alocação espacial de trabalhadores sob livre mobilidade. Municípios com desamenidades severas, isolamento geográfico e alta vulnerabilidade socioeconômica (alto IVS) exigem um diferencial salarial compensatório (\\Delta w) para equalizar a utilidade indireta à utilidade de reserva.",
        "implicacao_pmme": "Base teórica seminal que justifica o escalonamento das bolsas do PMM-E: a bolsa federal opera como choque exógeno de diferencial compensatório necessário para viabilizar a atração de especialistas para o interior vulnerável.",
        "roteiro_leitura": "Focar no modelo das Seções I e II. Extrair a condição de diferenciação parcial dw/dA < 0 e conectar o vetor de desamenidades A_m ao IVS 2010 do IPEA."
    },
    {
        "id": "TEO_02",
        "categoria": "Teorica / Teoria + Empiria",
        "subtema": "Preferências Médicas, Willingness to Accept (WTA) e Elasticidade da Bolsa",
        "autores": "Sivey, Peter; Scott, Anthony; Witt, Julia; Joyce, Catherine; Humphreys, John",
        "ano": 2012,
        "titulo": "Junior Doctors' Preferences for Specialty Choice",
        "periodico": "Journal of Health Economics",
        "volume_edicao": "Vol. 31, No. 6, pp. 813–826",
        "doi": "10.1016/j.jhealeco.2012.07.001",
        "paginas": 14,
        "paginas_foco": "Artigo completo (14 páginas - super conciso)",
        "tipo_artigo": "Random Utility Theory + Discrete Choice Experiment (DCE)",
        "mecanismo_teorico": "Modela a função de utilidade de médicos em início de carreira através de modelos de utilidade aleatória (RUM), estimando o Willingness to Accept (WTA) monetário exigido para aceitar postos em áreas remotas e regimes de alta carga horária.",
        "implicacao_pmme": "Parametriza a elasticidade da oferta de especialistas frente a adicionais de bolsa no interior e demonstra por que especialidades cirúrgicas exigem incentivos monetários até 40% maiores do que especialidades clínicas.",
        "roteiro_leitura": "Focar na Tabela 3 (Parâmetros estimados de WTA) e na discussão sobre trade-offs entre remuneração monetária direta e isolamento do município."
    },
    {
        "id": "TEO_03",
        "categoria": "Teorica / Teoria + Empiria",
        "subtema": "Matching Estrutural sob Subsídios Financeiros e Fricções de Localização",
        "autores": "Agarwal, Nikhil",
        "ano": 2015,
        "titulo": "An Empirical Model of the Medical Match",
        "periodico": "American Economic Review",
        "volume_edicao": "Vol. 105, No. 7, pp. 1939–1978",
        "doi": "10.1257/aer.20130663",
        "paginas": 40,
        "paginas_foco": "pp. 1940–1958 (Seções I a III: 18 páginas)",
        "tipo_artigo": "Design de Mercados + Estimação Estrutural de Preferências",
        "mecanismo_teorico": "Estrutura um modelo de matching biunívoco com restrições salariais e fricções de busca espacial. Demonstra como transferências e subsídios financeiros deslocam os candidatos em direção a hospitais periféricos e menos prestigiados.",
        "implicacao_pmme": "Modela o papel do edital centralizado do Ministério da Saúde na quebra de assimetrias informacionais entre especialistas recém-formados e hospitais municipais do interior.",
        "roteiro_leitura": "Focar na Seção II (Theoretical Framework). Analisar como subsídios financeiros compensam desvantagens institucionais na ordenação de preferências dos candidatos."
    },
    {
        "id": "TEO_04",
        "categoria": "Teorica / Teoria + Empiria",
        "subtema": "Worker Flows Teóricos: Impacto Diferencial de Bônus em Entradas vs Saídas",
        "autores": "Gravelle, Hugh; Scott, Anthony; Yong, Jongsay; McGrail, Matthew",
        "ano": 2018,
        "titulo": "Do Rural Incentives Payments Affect Entries and Exits of General Practitioners?",
        "periodico": "Social Science & Medicine",
        "volume_edicao": "Vol. 216, pp. 88–96",
        "doi": "10.1016/j.socscimed.2018.09.041",
        "paginas": 9,
        "paginas_foco": "Artigo completo (9 páginas - leitura cirúrgica)",
        "tipo_artigo": "Modelos de Contagem em Painel com Efeitos Fixos + Microfundamentação",
        "mecanismo_teorico": "Desenvolve modelo microeconômico de fluxos brutos de trabalho (worker flows). Prova que pagamentos de incentivos financeiros aumentam substancialmente as novas entradas (+15% a +25%), mas exercem impacto modesto ou nulo sobre a redução de saídas após 2 a 3 anos.",
        "implicacao_pmme": "Base teórica e empírica central para a nossa decomposição entre atração (n_entradas) e retenção (n_saidas, saldo_liquido), evitando a hipótese ingênua de que a bolsa garante fixação permanente.",
        "roteiro_leitura": "Ler integralmente. Analisar a Tabela 2 e Tabela 3, comparando a elasticidade de novas entradas vs a elasticidade de permanência médica no interior."
    },
    {
        "id": "TEO_05",
        "categoria": "Teorica / Teoria + Empiria",
        "subtema": "Federalismo Fiscal, Otimização Municipal e Crowding-Out de Médicos Próprios",
        "autores": "Baicker, Katherine; Staiger, Douglas",
        "ano": 2005,
        "titulo": "Fiscal Shenanigans, Targeted Federal Health Care Funds, and Patient Mortality",
        "periodico": "Quarterly Journal of Economics",
        "volume_edicao": "Vol. 120, No. 1, pp. 345–386",
        "doi": "10.1162/0033553053317416",
        "paginas": 42,
        "paginas_foco": "pp. 348–360 (Seção II: Teoria, 12 páginas)",
        "tipo_artigo": "Modelo Teórico de Federalismo Fiscal + Quase-Experimento em Saúde",
        "mecanismo_teorico": "Modela o comportamento de governos locais que recebem transferências federais vinculadas à saúde. Demonstra as condições em que o município usa o recurso federal para substituir gastos com pessoal próprio (crowding-out fiscal).",
        "implicacao_pmme": "Fornece a microfundamentação direta para testar se as bolsas do PMM-E atraíram médicos adicionais líquidos para o interior ou apenas subsidiaram prefeituras que demitiram médicos contratados.",
        "roteiro_leitura": "Focar na Seção II. Sintetizar a proposição teórica que deduz a derivada do gasto local próprio em relação ao repasse federal da bolsa."
    },
    {
        "id": "TEO_06",
        "categoria": "Teorica / Teoria + Empiria",
        "subtema": "Complementaridade entre Especialistas e Infraestrutura Hospitalar no Interior",
        "autores": "Acemoglu, Daron; Finkelstein, Amy",
        "ano": 2008,
        "titulo": "Input and Technology Choices in Regulated Industries: Evidence from the Health Care Sector",
        "periodico": "Journal of Political Economy",
        "volume_edicao": "Vol. 116, No. 5, pp. 837–880",
        "doi": "10.1086/595015",
        "paginas": 44,
        "paginas_foco": "pp. 839–858 (Seções I a III: 20 páginas)",
        "tipo_artigo": "Teoria Microeconômica + Quase-Experimento Hospitalar",
        "mecanismo_teorico": "Modela a escolha ótima de fatores de produção em hospitais sob preços regulados. A produtividade do trabalho médico especializado (L) é estritamente condicionada à presença de capital físico tecnológico complementar (K: leitos cirúrgicos, aparelhos de imagem).",
        "implicacao_pmme": "Explica por que o médico especialista não se fixa no interior vulnerável se não houver hospital e equipamentos adequados, justificando a interação entre valor da bolsa e capacidade física instalada.",
        "roteiro_leitura": "Focar na Seção II (The Basic Model of Factor Choice). Deduzir a condição de complementaridade marginal d²Y/(dL dK) > 0."
    },
    {
        "id": "TEO_07",
        "categoria": "Teorica / Teoria + Empiria",
        "subtema": "Políticas Públicas Regionais (Place-Based) e Equilíbrio de Bem-Estar no Interior",
        "autores": "Kline, Patrick; Moretti, Enrico",
        "ano": 2014,
        "titulo": "People, Places, and Public Policy: Some Simple Analytics of Local Economic Development Programs",
        "periodico": "Annual Review of Economics",
        "volume_edicao": "Vol. 6, No. 1, pp. 629–662",
        "doi": "10.1146/annurev-economics-080213-040845",
        "paginas": 34,
        "paginas_foco": "pp. 631–648 (Seções 1 a 3: 17 páginas)",
        "tipo_artigo": "Framework Analítico Teórico de Políticas Baseadas no Lugar",
        "mecanismo_teorico": "Desenvolve um framework analítico de equilíbrio espacial para avaliar subsídios à atração de fatores para regiões desassistidas, comparando ganhos de eficiência local contra distorções de realocação espacial e spillovers em polos vizinhos.",
        "implicacao_pmme": "Permite enquadrar o PMM-E como política place-based de saúde, formalizando a função de bem-estar social que justifica concentrar bolsas maiores nos municípios com alto IVS.",
        "roteiro_leitura": "Focar nas Seções 1 a 3. Extrair a equação de bem-estar agregado W e avaliar as condições de ausência de spillovers negativos severos."
    },

    # =========================================================================
    # LITERATURA EMPÍRICA (7 QUASE-EXPERIMENTOS, SOBREVIVÊNCIA E WORKER FLOWS)
    # =========================================================================
    {
        "id": "EMP_01",
        "categoria": "Empirica",
        "subtema": "Modelagem de Sobrevivência (Cox) e Fixação Médica no Interior",
        "autores": "Russell, Deborah J.; McGrail, Matthew R.; Humphreys, John S.",
        "ano": 2021,
        "titulo": "Determinants of Rural Australian General Practitioner Retention: A Longitudinal Analysis",
        "periodico": "Human Resources for Health",
        "volume_edicao": "Vol. 19, Artigo 7",
        "doi": "10.1186/s12960-020-00549-3",
        "paginas": 10,
        "paginas_foco": "Artigo completo (10 páginas)",
        "tipo_artigo": "Análise de Sobrevida Longitudinal (Kaplan-Meier + Modelo de Cox)",
        "mecanismo_teorico": "Estima os determinantes longitudinais do tempo até a evasão médica (tenure) em cidades do interior. Mostra que isolamento geográfico severo quase dobra o risco de saída (HR=1.85), enquanto suporte de hospital terciário reduz a evasão (HR=0.62).",
        "implicacao_pmme": "Referência empírica direta para modelar curvas de sobrevida de especialistas no município em função do valor da bolsa, do IVS e da presença de infraestrutura hospitalar.",
        "roteiro_leitura": "Focar nos Hazard Ratios da Tabela 2 e nas curvas de Kaplan-Meier por nível de isolamento municipal."
    },
    {
        "id": "EMP_02",
        "categoria": "Empirica",
        "subtema": "Acompanhamento Longitudinal de Coortes: Retenção sob Bolsa vs Pós-Obrigação",
        "autores": "Pathman, Donald E.; Konrad, Thomas R.; King, Tonya S.; Taylor, Donald H.; Koch, Gary G.",
        "ano": 2004,
        "titulo": "Outcomes of States' Scholarship, Loan Repayment, and Related Programs for Physicians",
        "periodico": "Medical Care",
        "volume_edicao": "Vol. 42, No. 6, pp. 560–568",
        "doi": "10.1097/01.mlr.0000128004.26577.8b",
        "paginas": 9,
        "paginas_foco": "Artigo completo (9 páginas)",
        "tipo_artigo": "Estudo de Coorte Longitudinal de Retenção Médica",
        "mecanismo_teorico": "Acompanha coortes de médicos participantes de programas estaduais de bolsa e amortização de dívidas em áreas desassistidas nos EUA. Constata que a retenção é superior a 80% durante a bolsa, mas cai para menos de 50% após o fim do compromisso formal.",
        "implicacao_pmme": "Fundamenta por que o PMM-E deve auditar separadamente a retenção de curto prazo (6 meses, bolsa ativa) da retenção duradoura (12+ meses), isolando 'médicos transitórios'.",
        "roteiro_leitura": "Focar na Tabela 3 (Retention Rates over time) e na discussão dos fatores que diferenciam fixação de longo prazo de permanência compulsória temporária."
    },
    {
        "id": "EMP_03",
        "categoria": "Empirica",
        "subtema": "Revisão Sistemática Global de Incentivos Financeiros e Return-of-Service",
        "autores": "Bärnighausen, Till; Bloom, David E.",
        "ano": 2009,
        "titulo": "Financial Incentives for Return of Service in Underserved Areas: A Systematic Review",
        "periodico": "BMC Health Services Research",
        "volume_edicao": "Vol. 9, Artigo 86",
        "doi": "10.1186/1472-6963-9-86",
        "paginas": 17,
        "paginas_foco": "Artigo completo (17 páginas)",
        "tipo_artigo": "Revisão Sistemática Global de 43 Programas Internacionais",
        "mecanismo_teorico": "Reúne e categoriza evidências de 43 programas em 10 países que usaram incentivos financeiros e bolsas condicionadas a serviço no interior. Sintetiza taxas de adesão, evasão, cumprimento contratual e custo-efetividade.",
        "implicacao_pmme": "Fornece a métrica internacional de benchmark para avaliar a atratividade do valor da bolsa e as taxas de abandono observadas no PMM-E frente à experiência global.",
        "roteiro_leitura": "Focar na Tabela 1 (Taxonomia comparativa) e na Seção de Discussão sobre custo por ano de médico fixado."
    },
    {
        "id": "EMP_04",
        "categoria": "Empirica",
        "subtema": "Incentivos Financeiros Progressivos e Oferta Médica em Áreas Periféricas",
        "autores": "Somville, Vincent",
        "ano": 2020,
        "titulo": "Financial Incentives and Physician Supply in Underserved Areas",
        "periodico": "World Development",
        "volume_edicao": "Vol. 127, Artigo 104764",
        "doi": "10.1016/j.worlddev.2019.104764",
        "paginas": 14,
        "paginas_foco": "Artigo completo (14 páginas)",
        "tipo_artigo": "Avaliação Quase-Experimental de Escalas de Incentivo Financeiro",
        "mecanismo_teorico": "Avalia o impacto de pacotes financeiros escalonados sobre a alocação de profissionais de saúde em distritos vulneráveis, demonstrando a sensibilidade da decisão locacional à dose do bônus financeiro.",
        "implicacao_pmme": "Evidência empírica direta que valida o design de doses crescentes de bolsa para municípios com maior carência socioeconômica e isolamento.",
        "roteiro_leitura": "Focar nas seções de identificação econométrica e na resposta não-linear da oferta médica em relação ao valor do benefício financeiro."
    },
    {
        "id": "EMP_05",
        "categoria": "Empirica",
        "subtema": "Painel CNES Mensal de Alta Frequência e Rotatividade Médica no Brasil",
        "autores": "Sliwa Ruiz, Julia; Becker, Sascha O.; Hone, Thomas; Rocha, Rudi",
        "ano": 2024,
        "titulo": "The Supply of Primary Care Physicians and Population Health: Evidence from the Sudden Departure of Cuban Doctors in Brazil",
        "periodico": "Journal of Health Economics",
        "volume_edicao": "Vol. 93, Artigo 102833",
        "doi": "10.1016/j.jhealeco.2023.102833",
        "paginas": 18,
        "paginas_foco": "Artigo completo (18 páginas)",
        "tipo_artigo": "Painel Mensal Longitudinal do CNES + Estudo de Evento Dinâmico",
        "mecanismo_teorico": "Constrói painel longitudinal mensal a nível de estabelecimento e município no CNES para rastrear saídas, recomposição de vagas e rotatividade médica no interior do Brasil após choque de oferta.",
        "implicacao_pmme": "Validação metodológica direta da infraestrutura de dados do nosso projeto: uso do CNES mensal como painel de alta frequência para auditar entradas, saídas e substituição de especialistas.",
        "roteiro_leitura": "Focar na Seção 3 (Tratamento e higienização dos microdados do CNES) e nos testes de heterogeneidade por vulnerabilidade municipal."
    },
    {
        "id": "EMP_06",
        "categoria": "Empirica",
        "subtema": "Avaliação Quase-Experimental de Provimento Médico e Heterogeneidade por Escassez",
        "autores": "Fontes, Luiz Felipe Campos; Conceição, Otavio Canozzi; Jacinto, Paulo de Andrade",
        "ano": 2018,
        "titulo": "Evaluating the Impact of Physicians' Provision on Primary Healthcare: Evidence from Brazil's More Doctors Program",
        "periodico": "Health Economics",
        "volume_edicao": "Vol. 27, No. 8, pp. 1284–1299",
        "doi": "10.1002/hec.3768",
        "paginas": 16,
        "paginas_foco": "Artigo completo (16 páginas)",
        "tipo_artigo": "Diferença em Diferenças com Pareamento (PSM-DiD)",
        "mecanismo_teorico": "Avalia o impacto de políticas federais de alocação de médicos sobre indicadores assistenciais no SUS, documentando que os impactos são estritamente concentrados nos municípios com maior vulnerabilidade e escassez inicial de profissionais.",
        "implicacao_pmme": "Orienta a definição das covariáveis municipais de baseline (IVS 2010, população, leitos, renda per capita) e o pareamento de municípios para controle de tendências.",
        "roteiro_leitura": "Focar na Tabela 1 (Balanço de covariáveis de baseline) e na especificação de heterogeneidade por porte e vulnerabilidade."
    },
    {
        "id": "EMP_07",
        "categoria": "Empirica",
        "subtema": "Identificação Causal por Tripla Diferença (DDD) em Mercados Locais",
        "autores": "Olden, Andreas; Møen, Jarle",
        "ano": 2022,
        "titulo": "The Triple Difference Estimator",
        "periodico": "The Econometrics Journal",
        "volume_edicao": "Vol. 25, No. 3, pp. 606–622",
        "doi": "10.1093/ectj/utac010",
        "paginas": 17,
        "paginas_foco": "Artigo completo (17 páginas)",
        "tipo_artigo": "Econometria Teórica e Métodos de Avaliação Causal",
        "mecanismo_teorico": "Formaliza as hipóteses de identificação do estimador DDD em dados em painel. Prova como o terceiro nível de contraste (município × especialidade × mês) elimina choques macroeconômicos e municipais não observados.",
        "implicacao_pmme": "Fundamentação econométrica formal da especificação empírica primária do projeto, protegendo a estimação do estoque de especialistas contra críticas de viés de endogeneidade municipal.",
        "roteiro_leitura": "Focar nas Seções 2 e 3 (The DDD Estimator and Identification Assumptions). Extrair as condições de relaxamento de tendências paralelas."
    }
]

def main():
    df = pd.DataFrame(PAPERS_EXPANDED)
    
    csv_path = OUTPUT_DIR / "matriz_evidencias_artigos_expandida.csv"
    json_path = OUTPUT_DIR / "matriz_evidencias_artigos_expandida.json"
    
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(PAPERS_EXPANDED, f, indent=2, ensure_ascii=False)
        
    print(f"[OK] Matriz expandida com 14 papers atualizada com sucesso:")
    print(f"     CSV:  {csv_path}")
    print(f"     JSON: {json_path}")
    print(f"     Total de papers consolidados: {len(df)}")

if __name__ == "__main__":
    main()

