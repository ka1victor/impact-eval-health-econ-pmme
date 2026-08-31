# -*- coding: utf-8 -*-
"""
scripts/avaliar_alternativas_modernas.py
Avalia alternativas modernas e/ou mais compactas para os 7 pilares teóricos do PMM-E.
"""

import json
import os
import pandas as pd

COMPARATIVE_PILLARS = [
    {
        "pilar": "Pilar 1: Equilíbrio Espacial & Salários Compensatórios",
        "paper_atual": "Roback (1982, JPE)",
        "ano_atual": 1982,
        "paginas_atual": "22 págs (foco: 15 págs)",
        "alternativa_moderna": "Sivey et al. (2012, JHE) / Diamond (2016, AER)",
        "ano_alt": 2012,
        "paginas_alt": "14 págs (Sivey - artigo completo)",
        "veredito": "MANTER Roback (1982) com Sivey (2012) como complemento direto",
        "justificativa": "Roback (1982) é insubstituível para a prova analítica de equilíbrio geral do diferencial compensatório (\Delta w) em função do IVS. Sivey et al. (2012) é a versão moderna mais compacta (14 págs) aplicando a teoria a escolhas locacionais médicas via Discrete Choice Experiment."
    },
    {
        "pilar": "Pilar 2: Matching Centralizado & Redução de Custos de Busca",
        "paper_atual": "Agarwal (2015, AER)",
        "ano_atual": 2015,
        "paginas_atual": "40 págs (foco: 18 págs)",
        "alternativa_moderna": "Roth (1984, JPE) / Roth & Peranson (1999, AER)",
        "ano_alt": 1984,
        "paginas_alt": "26 págs (Roth 1984 - foco: 18 págs)",
        "veredito": "MANTER Agarwal (2015, AER)",
        "justificativa": "Agarwal (2015) já é a referência moderna máxima (AER 2015). Ele avança em relação a Roth (1984) ao incorporar restrições de capacidade hospitalar e mensuração estrutural de preferências locacionais e salariais de residentes, exatamente o desenho do PMM-E."
    },
    {
        "pilar": "Pilar 3: Função de Produção Hospitalar & Capital Físico",
        "paper_atual": "Acemoglu & Finkelstein (2008, JPE)",
        "ano_atual": 2008,
        "paginas_atual": "44 págs (foco: 20 págs)",
        "alternativa_moderna": "Garicano (2000, JPE) / Chandra & Skinner (2012, JEL)",
        "ano_alt": 2012,
        "paginas_alt": "36 págs (Chandra & Skinner - foco: 18 págs)",
        "veredito": "MANTER Acemoglu & Finkelstein (2008) com Chandra & Skinner (2012)",
        "justificativa": "Acemoglu & Finkelstein (2008) fornece o modelo matemático exato de substituição técnica entre trabalho médico e capital sob regulação pública de preços. Chandra & Skinner (2012) complementa com a taxonomia de tecnologias hospitalares."
    },
    {
        "pilar": "Pilar 4: Federalismo Fiscal & Crowding-Out",
        "paper_atual": "Baicker & Staiger (2005, QJE)",
        "ano_atual": 2005,
        "paginas_atual": "42 págs (foco: 12 págs)",
        "alternativa_moderna": "Gordon (2004, JPubE) / Brollo et al. (2013, AER)",
        "ano_alt": 2004,
        "paginas_alt": "22 págs (Gordon - artigo completo)",
        "veredito": "MANTER Baicker & Staiger (2005, QJE)",
        "justificativa": "A Seção II de Baicker & Staiger (2005) tem apenas 12 páginas e trata especificamente de transferências federais vinculadas à saúde hospitalar (DSH funds) e mortalidade, sendo o modelo conceitual mais aderente ao PMM-E existente na literatura."
    },
    {
        "pilar": "Pilar 5: Agência Multitarefa em Contratos Públicos",
        "paper_atual": "Holmstrom & Milgrom (1991, JLEO)",
        "ano_atual": 1991,
        "paginas_atual": "29 págs (foco: 15 págs)",
        "alternativa_moderna": "Besley & Ghatak (2005, AER)",
        "ano_alt": 2005,
        "paginas_alt": "21 págs (foco: 14 págs)",
        "veredito": "INCORPORAR Besley & Ghatak (2005, AER) como alternativa moderna de elite",
        "justificativa": "Besley & Ghatak (2005, AER) é uma alternativa moderna extraordinária: modela agentes públicos motivados (como médicos do SUS) e prova que o alinhamento de missão entre o hospital e o médico substitui incentivos monetários de alta intensidade. É super didático (14 págs de foco)."
    },
    {
        "pilar": "Pilar 6: Políticas Baseadas no Lugar (Place-Based)",
        "paper_atual": "Kline & Moretti (2014, AnnRevEcon)",
        "ano_atual": 2014,
        "paginas_atual": "34 págs (foco: 17 págs)",
        "alternativa_moderna": "Gaubert, Kline & Yagan (2021, QJE) / Slattery & Zidar (2020, JEP)",
        "ano_alt": 2021,
        "paginas_alt": "28 págs (Slattery & Zidar - JEP)",
        "veredito": "MANTER Kline & Moretti (2014)",
        "justificativa": "Kline & Moretti (2014) é o framework teórico analítico mais limpo, transparente e pedagógico para políticas públicas place-based. Suas primeiras 17 páginas são perfeitas para a redação da introdução e motivação de bem-estar social."
    },
    {
        "pilar": "Pilar 7: Decisão sob Incerteza e Resolutividade Diagnóstica",
        "paper_atual": "Currie & MacLeod (2017, JLE)",
        "ano_atual": 2017,
        "paginas_atual": "43 págs (foco: 16 págs)",
        "alternativa_moderna": "Garicano (2000, JPE) — Hierarchies of Knowledge",
        "ano_alt": 2000,
        "paginas_alt": "31 págs (foco: 14 págs)",
        "veredito": "INCORPORAR Garicano (2000, JPE) como modelo formal de triagem e encaminhamento",
        "justificativa": "Garicano (2000, JPE) é o modelo microeconômico definitivo sobre a divisão do trabalho entre generalistas e especialistas: o generalista resolve casos rotineiros locais (z < z*) e encaminha casos complexos (z > z*) para o especialista. Ter o especialista no município expande z* e elimina o custo de transporte de pacientes."
    }
]

def main():
    os.makedirs("output/revisao_literatura", exist_ok=True)
    os.makedirs("docs", exist_ok=True)
    
    df = pd.DataFrame(COMPARATIVE_PILLARS)
    df.to_csv("output/revisao_literatura/comparativo_alternativas_teoricas.csv", index=False, encoding="utf-8-sig")
    with open("output/revisao_literatura/comparativo_alternativas_teoricas.json", "w", encoding="utf-8") as f:
        json.dump(COMPARATIVE_PILLARS, f, indent=2, ensure_ascii=False)
        
    print("Sucesso: Avaliação comparativa de alternativas teóricas exportada.")

if __name__ == "__main__":
    main()
