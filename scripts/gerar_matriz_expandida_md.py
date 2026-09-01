# -*- coding: utf-8 -*-
"""
scripts/gerar_matriz_expandida_md.py
Gera o markdown output/revisao_literatura/matriz_evidencias_artigos_expandida.md
com os 14 papers fundamentais (7 teóricos + 7 empíricos) focados na
Atração e Retenção de Especialistas no Interior com base em Bolsas e IVS.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "output" / "revisao_literatura" / "matriz_evidencias_artigos_expandida.json"
OUT_MD_PATH = ROOT / "output" / "revisao_literatura" / "matriz_evidencias_artigos_expandida.md"

with open(JSON_PATH, "r", encoding="utf-8") as f:
    papers = json.load(f)

md = """# Matriz Consolidada e Expandida de Evidências — PMM-E

> **Tema Central:** Avaliação de Impacto da Atração e Retenção de Médicos Especialistas em Cidades do Interior com base nas Diferentes Bolsas e IVS (Índice de Vulnerabilidade Social).  
> **Mapeamento Estruturado:** 14 papers curados (7 Teóricos / Teoria+Empiria + 7 Empíricos / Métodos) com rigor metodológico e foco operacional para a equipe.

---

## 1. Fundamentação Teórica e "Teoria + Empiria" (7 Artigos)

"""

for p in papers:
    if "Teorica" in p["categoria"]:
        md += f"""### [{p['id']}] {p['autores']} ({p['ano']}) — *{p['titulo']}*
- **Periódico:** {p['periodico']} ({p['volume_edicao']})
- **DOI:** [{p['doi']}](https://doi.org/{p['doi']})
- **Tipo de Artigo:** {p['tipo_artigo']}
- **Extensão Total:** **{p['paginas']} páginas** | **Foco Recomendado:** **{p['paginas_foco']}**
- **Subtema:** {p['subtema']}
- **Mecanismo Teórico / Econômico:** {p['mecanismo_teorico']}
- **Implicação Direta para o PMM-E:** {p['implicacao_pmme']}
- **Roteiro para a Leitura da Equipe:** {p['roteiro_leitura']}

---
"""

md += """
## 2. Literatura Empírica, Sobrevivência e Worker Flows (7 Artigos)

"""

for p in papers:
    if p["categoria"] == "Empirica":
        md += f"""### [{p['id']}] {p['autores']} ({p['ano']}) — *{p['titulo']}*
- **Periódico:** {p['periodico']} ({p['volume_edicao']})
- **DOI:** [{p['doi']}](https://doi.org/{p['doi']})
- **Tipo de Artigo:** {p['tipo_artigo']}
- **Extensão Total:** **{p['paginas']} páginas** | **Foco Recomendado:** **{p['paginas_foco']}**
- **Subtema:** {p['subtema']}
- **Mecanismo Empírico / Identificação:** {p['mecanismo_teorico']}
- **Implicação Direta para o PMM-E:** {p['implicacao_pmme']}
- **Roteiro para a Leitura da Equipe:** {p['roteiro_leitura']}

---
"""

with open(OUT_MD_PATH, "w", encoding="utf-8") as f:
    f.write(md)

print("output/revisao_literatura/matriz_evidencias_artigos_expandida.md atualizado com sucesso.")

