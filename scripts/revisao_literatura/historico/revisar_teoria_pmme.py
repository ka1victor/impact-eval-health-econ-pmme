# -*- coding: utf-8 -*-
"""
scripts/revisar_teoria_pmme.py
Estrutura e formaliza o arcabouço microeconômico do PMM-E integrando os 7 pilares teóricos seminais,
focando na Atração e Retenção de Médicos Especialistas no Interior sob Diferentes Bolsas e IVS.
"""

import json
import os
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = ROOT / "output" / "revisao_literatura"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

THEORETICAL_PILLARS = [
    {
        "pilar_id": "PILAR_01",
        "nome": "Equilíbrio Espacial e Diferenciais Compensatórios por IVS",
        "paper_canonico": "Roback (1982, JPE)",
        "autores": "Roback, Jennifer",
        "ano": 1982,
        "periodico": "Journal of Political Economy",
        "volume": "Vol. 90, No. 6, pp. 1257–1278",
        "paginas": 22,
        "paginas_foco": "pp. 1257–1272 (Seções 1 a 3: 15 págs)",
        "equacao_central": r"V(w_m, r_m; A_m) = \bar{u} \implies \left. \frac{dw_m}{dA_m} \right|_{V = \bar{u}} = -\frac{\partial V / \partial A_m}{\partial V / \partial w_m} < 0",
        "mecanismo_teorico": "O médico especialista possui mobilidade geográfica. Em cidades do interior com vulnerabilidade e carência de amenidades (alto IVS), a utilidade indireta seria inferior a u_bar sem compensação. O adicional financeiro federal (\\Delta w) preenche o diferencial salarial equalizador necessário para viabilizar a atração ao interior.",
        "implicacao_testavel_pmme": "A atração de médicos ao interior depende monotonicamente da bolsa federal e do escalonamento por faixas de IVS 2010.",
        "sessao_artigo": "Seção Teórica: Curva de Oferta Espacial e Salários Compensatórios"
    },
    {
        "pilar_id": "PILAR_02",
        "nome": "Preferências Locacionais, WTA e Elasticidade da Bolsa",
        "paper_canonico": "Sivey et al. (2012, JHE)",
        "autores": "Sivey, Peter; Scott, Anthony; Witt, Julia; Joyce, Catherine; Humphreys, John",
        "ano": 2012,
        "periodico": "Journal of Health Economics",
        "volume": "Vol. 31, No. 6, pp. 813–826",
        "paginas": 14,
        "paginas_foco": "Artigo completo (14 págs)",
        "equacao_central": r"U_{ij} = \beta_w w_j + \beta_{loc} Loc_j + \beta_h Horas_j + \varepsilon_{ij}, \quad WTA_{rural} = -\frac{\beta_{loc}}{\beta_w}",
        "mecanismo_teorico": "Sob modelos de utilidade aleatória (RUM) e Discrete Choice Experiments (DCE), quantifica-se a compensação financeira monetária exigida (WTA) para aceitar postos em áreas remotas do interior. Especialistas cirúrgicos exigem prêmio 40% superior a clínicos.",
        "implicacao_testavel_pmme": "A resposta de atração ao bônus da bolsa varia entre especialidades clínicas (maior elasticidade) e cirúrgicas (maior exigência de compensação).",
        "sessao_artigo": "Seção Teórica: Elasticidade-Preço da Oferta Especializada e Heterogeneidade por Especialidade"
    },
    {
        "pilar_id": "PILAR_03",
        "nome": "Matching Centralizado sob Bolsas e Custos de Busca",
        "paper_canonico": "Agarwal (2015, AER)",
        "autores": "Agarwal, Nikhil",
        "ano": 2015,
        "periodico": "American Economic Review",
        "volume": "Vol. 105, No. 7, pp. 1939–1978",
        "paginas": 40,
        "paginas_foco": "pp. 1940–1958 (Seções I a III: 18 págs)",
        "equacao_central": r"\max_{\mu \in \mathcal{M}} \sum_{i} u_i(\mu(i)) \quad \text{s.t. estabilidade e capacidades } q_m",
        "mecanismo_teorico": "O mercado médico descentralizado sofre com atritos informacionais e custos de busca. Um edital centralizado com matching estável e bolsas públicas reduz atritos e direciona candidatos para hospitais periféricos.",
        "implicacao_testavel_pmme": "A publicação de vagas em plataforma nacional centralizada gera maior preenchimento de vagas imediatas do que seleções municipais isoladas.",
        "sessao_artigo": "Seção Teórica: Redução de Fricções de Busca e Matching Centralizado"
    },
    {
        "pilar_id": "PILAR_04",
        "nome": "Worker Flows: Efeito de Bônus em Entradas vs. Saídas",
        "paper_canonico": "Gravelle et al. (2018, SSM)",
        "autores": "Gravelle, Hugh; Scott, Anthony; Yong, Jongsay; McGrail, Matthew",
        "ano": 2018,
        "periodico": "Social Science & Medicine",
        "volume": "Vol. 216, pp. 88–96",
        "paginas": 9,
        "paginas_foco": "Artigo completo (9 págs)",
        "equacao_central": r"\Delta L_{mt} = Entry_{mt}(w_{bolsa}) - Exit_{mt}(w_{bolsa}), \quad \frac{\partial Entry}{\partial w_{bolsa}} > 0, \quad \frac{\partial Exit}{\partial w_{bolsa}} \approx 0",
        "mecanismo_teorico": "Modela teoricamente a dinâmica de worker flows em mercados de trabalho médico no interior. Incentivos financeiros aumentam fortemente a taxa bruta de novas entradas (atração), mas têm impacto residual na redução da evasão (retenção) de médio e longo prazo.",
        "implicacao_testavel_pmme": "O programa elevará de imediato as contratações brutas no interior, mas a permanência sustentada decairá se não houver fatores estruturais de fixação.",
        "sessao_artigo": "Seção Teórica: Decomposição de Fluxos Brutos (Entradas, Saídas e Retenção)"
    },
    {
        "pilar_id": "PILAR_05",
        "nome": "Federalismo Fiscal e Crowding-Out de Contratos Municipais",
        "paper_canonico": "Baicker & Staiger (2005, QJE)",
        "autores": "Baicker, Katherine; Staiger, Douglas",
        "ano": 2005,
        "periodico": "Quarterly Journal of Economics",
        "volume": "Vol. 120, No. 1, pp. 345–386",
        "paginas": 42,
        "paginas_foco": "pp. 348–360 (Seção II: 12 págs)",
        "equacao_central": r"\max_{L_m^{proprio}, G_m} U(L_m, G_m) \quad \text{s.t. } w_m L_m^{proprio} + G_m = R_m + w_{bolsa} L_m^{fed}",
        "mecanismo_teorico": "Quando o governo federal assume os custos do médico especialista via bolsa, gestores municipais têm incentivos fiscais para descontinuar contratos próprios locais, gerando substituição fiscal (crowding-out).",
        "implicacao_testavel_pmme": "O efeito líquido sobre o estoque total de especialistas no CNES pode ser inferior a 1,0 devido ao desmonte de contratos prévios pagos pelo município.",
        "sessao_artigo": "Seção Teórica: Comportamento Fiscal Municipal e Crowding-Out"
    },
    {
        "pilar_id": "PILAR_06",
        "nome": "Complementaridade Trabalho Especializado - Capital Hospitalar",
        "paper_canonico": "Acemoglu & Finkelstein (2008, JPE)",
        "autores": "Acemoglu, Daron; Finkelstein, Amy",
        "ano": 2008,
        "periodico": "Journal of Political Economy",
        "volume": "Vol. 116, No. 5, pp. 837–880",
        "paginas": 44,
        "paginas_foco": "pp. 839–858 (Seções I a III: 20 págs)",
        "equacao_central": r"Y = F(K, L), \quad \frac{\partial^2 Y}{\partial L \partial K} > 0 \implies \text{Produtividade marginal do especialista é crescente no capital hospitalar } K",
        "mecanismo_teorico": "Médicos especialistas dependem criticamente de leitos cirúrgicos, tomógrafos e tecnologias diagnósticas (K). Alocar especialistas em municípios desprovidos de infraestrutura hospitalar gera baixa produtividade e acelera a rotatividade/evasão.",
        "implicacao_testavel_pmme": "A permanência do especialista e o impacto em cirurgias/internações são heterogêneos e estritamente maiores em municípios dotados de hospitais com capital instalado.",
        "sessao_artigo": "Seção Teórica: Função de Produção e Complementaridade Fator-Infraestrutura"
    },
    {
        "pilar_id": "PILAR_07",
        "nome": "Políticas Place-Based e Ganho Líquido de Bem-Estar no Interior",
        "paper_canonico": "Kline & Moretti (2014, AnnRevEcon)",
        "autores": "Kline, Patrick; Moretti, Enrico",
        "ano": 2014,
        "periodico": "Annual Review of Economics",
        "volume": "Vol. 6, pp. 629–662",
        "paginas": 34,
        "paginas_foco": "pp. 631–648 (Seções 1 a 3: 17 págs)",
        "equacao_central": r"W = \sum_{m} N_m \left[ v_m(w_m, r_m) - c_m \right] + \text{Externalidades Locais de Saúde}",
        "mecanismo_teorico": "Políticas de desenvolvimento regional e subsídios à atração espacial geram ganhos de bem-estar agregado se as externalidades de saúde locais em áreas vulneráveis superarem os custos de distorção tributária e descolamento.",
        "implicacao_testavel_pmme": "O programa melhora o bem-estar social ao reduzir custos de transporte sanitário e vazamento de pacientes (TFD) sem gerar desassistência nos municípios vizinhos.",
        "sessao_artigo": "Seção Teórica: Eficiência Agregada, Equidade e Balanço de Bem-Estar"
    }
]

def main():
    df = pd.DataFrame(THEORETICAL_PILLARS)
    csv_path = OUTPUT_DIR / "pilares_teoricos_pmme.csv"
    json_path = OUTPUT_DIR / "pilares_teoricos_pmme.json"
    
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(THEORETICAL_PILLARS, f, indent=2, ensure_ascii=False)
        
    print(f"Sucesso: {len(THEORETICAL_PILLARS)} Pilares Teóricos seminais estruturados e exportados.")

if __name__ == "__main__":
    main()

