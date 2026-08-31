# -*- coding: utf-8 -*-
import json

with open("output/revisao_literatura/matriz_evidencias_artigos_expandida.json", "r", encoding="utf-8") as f:
    papers = json.load(f)

md = """# Matriz Consolidada e Expandida de Evidências — PMM-E

> Mapeamento estruturado de 14 papers curados (7 Teóricos / Teoria+Empiria + 7 Empíricos) com abordagem Acemoglu e foco operacional para a equipe.

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
## 2. Literatura Empírica e Quase-Experimentos Análogos (7 Artigos)

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

with open("output/revisao_literatura/matriz_evidencias_artigos_expandida.md", "w", encoding="utf-8") as f:
    f.write(md)

print("output/revisao_literatura/matriz_evidencias_artigos_expandida.md atualizado com sucesso.")
