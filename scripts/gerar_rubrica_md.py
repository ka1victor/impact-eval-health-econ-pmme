# -*- coding: utf-8 -*-
"""
scripts/gerar_rubrica_md.py
Gera docs/09_rubrica_avaliacao_papers.md e output/revisao_literatura/matriz_rubrica_detalhada.md
a partir de output/revisao_literatura/rubrica_ranking_papers.json.
Foco: Atração e Retenção de Especialistas no Interior com base em Bolsas e IVS.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "output" / "revisao_literatura" / "rubrica_ranking_papers.json"
DOC_PATH = ROOT / "docs" / "09_rubrica_avaliacao_papers.md"
OUT_MD_PATH = ROOT / "output" / "revisao_literatura" / "matriz_rubrica_detalhada.md"

with open(JSON_PATH, "r", encoding="utf-8") as f:
    papers = json.load(f)

# Classificação e ordenação
papers_teorico = sorted(papers, key=lambda x: x["ntp_ponderada"], reverse=True)
papers_empirico = sorted(papers, key=lambda x: x["nep_ponderada"], reverse=True)

md = r"""# 09. Rúbrica Estratégica de Avaliação de Literatura, Auditoria Individual e Ranking

> **Projeto:** Avaliação de Impacto e Economia da Saúde — Programa Mais Médicos Especialistas (PMM-E / Lei nº 15.233/2025)  
> **Tema Central:** *Atração e Retenção de Médicos Especialistas em Cidades do Interior com base nas Diferentes Bolsas e no IVS (Índice de Vulnerabilidade Social).*  
> **Objetivo:** Estabelecer uma rúbrica quantitativa e qualitativa multidimensional para auditar 18 papers candidatos, avaliar suas contribuições teóricas e empíricas específicas para o PMM-E, e derivar a seleção ótima dos **papers com maior contribuição ponderada pelo tamanho e aderência ao tema de interior/bolsa/IVS**.  
> **Data:** 31 de Agosto de 2026  

---

## 1. Arquitetura da Rúbrica Estratégica de Avaliação

A avaliação de cada paper foi estruturada em duas dimensões substantivas e uma métrica de custo cognitivo/operacional de leitura:

```mermaid
graph TD
    subgraph "Dimensão 1: Contribuição Teórica (0 a 100)"
        T1["T1: Formalização Microeconômica Espacial/WTA (25%)"]
        T2["T2: Aderência a Bolsas, IVS e Interior (35%)"]
        T3["T3: Previsões Testáveis & Worker Flows (25%)"]
        T4["T4: Clareza & Digestibilidade Pedagógica (15%)"]
    end
    
    subgraph "Dimensão 2: Contribuição Empírica & Métodos (0 a 100)"
        E1["E1: Aderência a Provimento e Interior (30%)"]
        E2["E2: Rigor de Identificação Causal/Sobrevida (30%)"]
        E3["E3: Mensuração de Atração/Retenção (25%)"]
        E4["E4: Espelhamento Visual de Tabelas e Gráficos (15%)"]
    end
    
    subgraph "Dimensão 3: Custo de Leitura da Equipe"
        P["Páginas de Foco Prioritário (P)"]
        FC["Fator de Concisão = 1 / [1 + 0.30 * ln(max(1, P/10))]"]
    end
    
    T1 & T2 & T3 & T4 --> CT["Nota Teórica Bruta (CT)"]
    E1 & E2 & E3 & E4 --> CE["Nota Empírica Bruta (CE)"]
    
    CT & FC --> NTP["Nota Teórica Ponderada (NTP = CT * FC)"]
    CE & FC --> NEP["Nota Empírica Ponderada (NEP = CE * FC)"]
```

### 1.1 Critérios Detalhados da Rúbrica

#### A. Dimensão Teórica ($CT \in [0, 100]$):
* **T1 — Formalização Microeconômica Espacial e WTA (Peso 25%):** Modelagem matemática explícita de equilíbrio hedônico espacial, preferências locacionais sob utilidade aleatória, escolhas de insumos hospitalares ou matching com subsídios.
* **T2 — Aderência aos Mecanismos do PMM-E no Interior (Peso 35%):** Capacidade de modelar diretamente:
  1. Diferenciais salariais compensatórios ($\Delta w$) indexados à vulnerabilidade social e desamenidades (IVS 2010);
  2. Sensibilidade da oferta e atração a escalonamento financeiro de bolsas;
  3. Complementaridade entre perícia médica e infraestrutura hospitalar física ($K$) no interior;
  4. Fricções espaciais e papel coordenador de editais centralizados de matching;
  5. *Crowding-out* fiscal sobre contratos médicos municipais preexistentes.
* **T3 — Derivação de Previsões Testáveis e Equações de Fluxo (Peso 25%):** O modelo gera equações estimáveis para taxas brutas de entrada (atração), saída (evasão), permanência ou RDD em limiares de bolsa.
* **T4 — Clareza e Poder Pedagógico (Peso 15%):** Elegância e facilidade de transmissão didática para a redação do artigo científico.

#### B. Dimensão Empírica ($CE \in [0, 100]$):
* **E1 — Aderência a Políticas de Provimento e Interior (Peso 30%):** Uso de dados administrativos de recursos humanos em saúde (CNES, DATASUS, MABEL, coortes) em áreas remotas e vulneráveis.
* **E2 — Rigor de Identificação Causal e Sobrevivência (Peso 30%):** Desenhos quase-experimentais limpos (RDD, DDD, Estudos de Evento, Modelos de Cox com Efeitos Fixos).
* **E3 — Mensuração de Worker Flows e Retenção (Peso 25%):** Decomposição de entradas, saídas, rotatividade e censura de sobrevida após o término de bolsas ativas.
* **E4 — Espelhamento Visual (Peso 15%):** Figuras e tabelas de referência metodológica (curvas de sobrevida, coeficientes dinâmicos).

---

## 2. Auditoria Individual e Avaliação Detalhada dos 18 Papers

Auditamos individualmente cada obra sob o foco estrito de atração e retenção no interior:

"""

for p in papers:
    md += f"""### [{p['id']}] {p['autores']} ({p['ano']}) — *{p['titulo']}*
- **Periódico/Veículo:** {p['periodico']} ({p['vol_pp']}) | **DOI:** [{p['doi']}](https://doi.org/{p['doi']})
- **Classificação:** {p['tipo']}
- **Extensão:** **{p['paginas_totais']} páginas totais** | **Foco Recomendado:** **{p['paginas_foco']} páginas**
- **Notas da Rúbrica:**
  - *Teórica Bruta ($CT$):* **{p['ct_bruta']}/100** | *Empírica Bruta ($CE$):* **{p['ce_bruta']}/100**
  - *Fator de Concisão:* **{p['fator_concisao']}**
  - *Nota Teórica Ponderada ($NTP$):* **{p['ntp_ponderada']}**
  - *Nota Empírica Ponderada ($NEP$):* **{p['nep_ponderada']}**
- **Auditoria de Conteúdo & Mecanismo Lido:** {p['resumo_leitura']}

---
"""

md += """
## 3. Ranking Geral Consolidado (18 Papers)

| Rank T | ID | Autores (Ano) | Periódico | Foco (pp) | CT Bruta | Fator | NTP (Ponderada) | Rank E | CE Bruta | NEP (Ponderada) |
|:---:|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
"""

for i, p in enumerate(papers_teorico):
    r_emp = next(idx + 1 for idx, x in enumerate(papers_empirico) if x["id"] == p["id"])
    md += f"| **{i+1}** | `{p['id']}` | {p['autores'].split(';')[0]} et al. ({p['ano']}) | *{p['periodico']}* | {p['paginas_foco']}p | {p['ct_bruta']} | {p['fator_concisao']} | **{p['ntp_ponderada']}** | {r_emp} | {p['ce_bruta']} | {p['nep_ponderada']} |\n"

md += """
---

## 4. Seleção e Síntese dos Principais Papers Teóricos e Empíricos

A composição ótima de literatura para fundamentar a avaliação do PMM-E no interior é estruturada da seguinte forma:

```mermaid
graph TD
    subgraph "Núcleo Teórico: Atração, WTA e Equilíbrio Espacial"
        T1["Roback (1982) & Sivey et al. (2012)<br/>Diferenciais Compensatórios por IVS e Estimação de WTA para o Interior"]
        T2["Agarwal (2015) & Gravelle et al. (2018)<br/>Matching Centralizado sob Bolsas e Decomposição de Worker Flows"]
        T3["Baicker & Staiger (2005) & Acemoglu & Finkelstein (2008)<br/>Crowding-Out Fiscal e Complementaridade Trabalho-Capital Hospitalar"]
    end
    
    subgraph "Núcleo Empírico: Sobrevivência, Painel CNES e Quase-Experimentos"
        E1["Russell et al. (2021) & Pathman et al. (2004)<br/>Análise de Sobrevida de Cox e Coortes sob Bolsa Ativa vs Pós-Obrigação"]
        E2["Bärnighausen & Bloom (2009) & Somville (2020)<br/>Benchmark Global de Return-of-Service e Escalas de Incentivo Financeiro"]
        E3["Sliwa Ruiz et al. (2024), Fontes et al. (2018) & Olden & Møen (2022)<br/>Painel Mensal do CNES, Heterogeneidade por Escassez e Identificação DDD"]
    end
    
    T1 & T2 & T3 --> FUND["Fundamentação Teórica Robusta (PMM-E)"]
    E1 & E2 & E3 --> METOD["Estratégia Econométrica e Worker Flows"]
```

### Racional da Composição:
1. **Roback (1982) e Sivey et al. (2012):** Estabelecem por que municípios com alto IVS exigem adicionais compensatórios de bolsa e fornecem a parametrização do WTA monetário dos médicos.
2. **Gravelle et al. (2018) e Russell et al. (2021):** Fornecem o modelo conceitual e empírico de decomposição entre atração (entradas) e retenção (saídas/sobrevida).
3. **Pathman et al. (2004) e Bärnighausen & Bloom (2009):** Documentam internacionalmente a dinâmica de retenção durante a bolsa versus a evasão esperada pós-obrigação.
4. **Sliwa Ruiz et al. (2024) e Olden & Møen (2022):** Validam o uso do CNES mensal como painel de alta frequência para rastrear estoques e rotatividade sob o estimador DDD e prospectivo RDD.
"""

with open(DOC_PATH, "w", encoding="utf-8") as f:
    f.write(md)

with open(OUT_MD_PATH, "w", encoding="utf-8") as f:
    f.write(md)

print("docs/09_rubrica_avaliacao_papers.md e output/revisao_literatura/matriz_rubrica_detalhada.md gerados com sucesso.")

