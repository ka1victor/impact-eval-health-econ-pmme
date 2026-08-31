# -*- coding: utf-8 -*-
import json

with open("output/revisao_literatura/rubrica_ranking_papers.json", "r", encoding="utf-8") as f:
    papers = json.load(f)

# Classificação e ordenação
papers_teorico = sorted(papers, key=lambda x: x["ntp_ponderada"], reverse=True)
papers_empirico = sorted(papers, key=lambda x: x["nep_ponderada"], reverse=True)

md = """# 09. Rúbrica Estratégica de Avaliação de Literatura, Auditoria Individual e Ranking

> **Projeto:** Avaliação de Impacto e Economia da Saúde — Programa Mais Médicos Especialistas (PMM-E / Lei nº 15.233/2025)  
> **Objetivo:** Estabelecer uma rúbrica quantitativa e qualitativa multidimensional para auditar 18 papers candidatos, avaliar suas contribuições teóricas e empíricas específicas para o PMM-E, e derivar a seleção ótima dos **7 papers com maior contribuição teórica ponderada pelo tamanho**.  
> **Data:** 30 de Agosto de 2026  

---

## 1. Arquitetura da Rúbrica Estratégica de Avaliação

A avaliação de cada paper foi estruturada em duas dimensões substantivas e uma métrica de custo cognitivo/operacional de leitura:

```mermaid
graph TD
    subgraph "Dimensão 1: Contribuição Teórica (0 a 100)"
        T1["T1: Formalização Microeconômica (25%)"]
        T2["T2: Aderência aos Mecanismos do PMM-E (35%)"]
        T3["T3: Poder de Previsão Testável (25%)"]
        T4["T4: Clareza & Poder Pedagógico (15%)"]
    end
    
    subgraph "Dimensão 2: Contribuição Empírica (0 a 100)"
        E1["E1: Aderência a Dados/Contexto Análogo (30%)"]
        E2["E2: Rigor de Identificação Causal (30%)"]
        E3["E3: Métricas de Fluxo & Retenção (25%)"]
        E4["E4: Espelhamento Visual de Tabelas (15%)"]
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
* **T1 — Formalização Microeconômica (Peso 25%):** Existência de modelo matemático explícito (otimização de utilidade, minimização de custos hospitalares, equilíbrio geral espacial, matching ou agência multitarefa).
* **T2 — Aderência aos Mecanismos do PMM-E (Peso 35%):** Capacidade de modelar diretamente:
  1. Diferenciais salariais compensatórios ($\Delta w$) indexados à vulnerabilidade (IVS);
  2. Complementaridade com capital hospitalar físico (leitos cirúrgicos e tomógrafos);
  3. Fricções de coordenação e matching em editais centralizados;
  4. Agência multitarefa (dedicação assistencial vs. aprimoramento acadêmico);
  5. *Crowding-out* fiscal e substituição de contratações locais.
* **T3 — Derivação de Hipóteses Testáveis (Peso 25%):** O modelo teórico gera equações estimáveis que justificam a Tripla Diferença (DDD) e as análises de heterogeneidade.
* **T4 — Clareza e Poder Pedagógico (Peso 15%):** Elegância analítica e viabilidade de transmissão para a redação do artigo científico.

#### B. Dimensão Empírica ($CE \in [0, 100]$):
* **E1 — Aderência Institucional (Peso 30%):** Uso de microdados administrativos de médicos (CNES, DATASUS, MABEL, NRMP) e políticas de provimento em áreas desassistidas.
* **E2 — Rigor Econométrico (Peso 30%):** Desenhos quase-experimentais limpos (DiD, DDD, Estudo de Evento Dinâmico, Pareamento por Escore de Propensão, Modelos de Sobrevida).
* **E3 — Mensuração de Fluxos e Retenção (Peso 25%):** Decomposição explícita de entradas, saídas, estoques líquidos e tratamento de censura longitudinal.
* **E4 — Espelhamento de Tabelas e Gráficos (Peso 15%):** Padrão visual de figuras e tabelas diretamente aproveitáveis para nossas saídas.

#### C. Ponderação pelo Tamanho ($NTP$ e $NEP$):
* Para que cada membro da equipe consiga ler, absorver e fichar o artigo em 1 a 2 turnos, aplicamos um desconto logarítmico suave sobre as páginas de foco:
  $$Fator\_Concisao = \frac{1}{1 + 0.30 \cdot \ln\left(\max\left(1, \frac{P_{foco}}{10}\right)\right)}$$
  *Artigos de 9 a 12 páginas mantêm ~100% da nota; artigos de 18 a 22 páginas sofrem modesto ajuste de ~15% a 20%, premiando densidade de insights por página lida.*

---

## 2. Auditoria Individual e Leitura Detalhada dos 18 Papers

Auditamos e lemos individualmente cada uma das 18 obras candidatas:

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

## 4. Recomendação dos 7 Papers com Maiores Notas Teóricas Ponderadas

Com base estrita no ranking de **Nota Teórica Ponderada pelo Tamanho ($NTP$)**, os 7 papers selecionados para divisão de leitura da equipe na fundamentação teórica são:

```mermaid
graph LR
    subgraph "Top 7 Teóricos Selecionados (NTP)"
        T1["1. Gravelle et al. 2018 (NTP: 90.75 | 9p)<br/>Worker Flows & Modelagem Teórica de Entradas/Saídas"]
        T2["2. Sivey et al. 2012 (NTP: 87.76 | 14p)<br/>Modelo de Utilidade Aleatória & Escolha de Especialidade"]
        T3["3. Baicker & Staiger 2005 (NTP: 87.53 | 14p)<br/>Modelo de Federalismo Fiscal & Crowding-Out"]
        T4["4. Russell et al. 2021 (NTP: 85.75 | 10p)<br/>Modelagem de Risco de Evasão Médica & Hazard Ratios"]
        T5["5. Pathman et al. 2004 (NTP: 84.50 | 9p)<br/>Teoria de Coortes de Retenção sob Bolsa Ativa vs Pós"]
        T6["6. Holmstrom & Milgrom 1991 (NTP: 83.02 | 15p)<br/>Agência Multitarefa em Contratos Híbridos"]
        T7["7. Acemoglu & Finkelstein 2008 (NTP: 82.32 | 18p)<br/>Escolha de Insumos K/L & Capital Tecnológico Hospitalar"]
    end
```

### Justificativa da Composição Teórica Ótima:
1. **Gravelle et al. (2018, 9p - Rank 1):** Maior densidade de insights por página da literatura; modela teoricamente como incentivos monetários afetam a atração sem alterar a taxa de saída de longo prazo.
2. **Sivey et al. (2012, 14p - Rank 2):** Modela a função de utilidade e *willingness to accept* do médico especialista frente a bônus vs. localização.
3. **Baicker & Staiger (2005, 14p de foco - Rank 3):** Fornece o modelo microeconômico de comportamento municipal que explica o *crowding-out* fiscal do PMM-E.
4. **Russell et al. (2021, 10p - Rank 4):** Modela formalmente o tempo até a evasão médica em função de isolamento e infraestrutura hospitalar.
5. **Pathman et al. (2004, 9p - Rank 5):** Modela a dinâmica temporal de coortes vinculadas a incentivos públicos.
6. **Holmstrom & Milgrom (1991, 15p de foco - Rank 6):** Teoria clássica de incentivos multitarefa para contratos que combinam assistência hospitalar e título de especialista.
7. **Acemoglu & Finkelstein (2008, 18p de foco - Rank 7):** O modelo formal definitivo de complementaridade e substituição entre trabalho médico especializado e capital tecnológico hospitalar.

*(Nota: Papers seminais como **Chandra & Skinner 2012** (Rank 8, NTP: 79.91), **Roback 1982** (Rank 9, NTP: 78.78) e **Agarwal 2015** (Rank 10, NTP: 78.60) permanecem como referências de apoio no Tier 2 para consulta direta).*
"""

with open("docs/09_rubrica_avaliacao_papers.md", "w", encoding="utf-8") as f:
    f.write(md)

with open("output/revisao_literatura/matriz_rubrica_detalhada.md", "w", encoding="utf-8") as f:
    f.write(md)

print("docs/09_rubrica_avaliacao_papers.md e output/revisao_literatura/matriz_rubrica_detalhada.md gerados com sucesso.")
