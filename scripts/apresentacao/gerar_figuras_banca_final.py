"""Figuras da banca final (versão sobre o deck do grupo de 11/11/2026).

Gera, lendo só `output/`:
- `output/apresentacao_banca_final/figuras/coeficientes_vl1.png`: o que cada coeficiente do VL-1 (ciclos 1–3) faz
  com a chance de uma vaga contra outra, em escala multiplicativa (×), com IC 95%.
- `output/apresentacao_banca_final/figuras/robustez_vl1.png`: razão de chances por +R$ 5 mil nas variantes que
  comparam vagas da mesma UF (VL e VG), mais o modelo pré-registrado (M1) como referência cinza.
- `output/apresentacao_banca_final/figuras/manifesto_figuras.json`: entradas com hash e os números de cada linha.

Natureza: EMPIRICO. Nada simulado.

Uso
---
    python3 scripts/apresentacao/gerar_figuras_banca_final.py
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
VL = ROOT / "output/rdd_bolsa/VL_estimativas.csv"
VG = ROOT / "output/rdd_bolsa/VG_estimativas.csv"
DIR = ROOT / "output/apresentacao_banca_final/figuras"
VERDE, VERDE_ESC, CINZA, TEXTO, GRADE = "#2E7D46", "#114719", "#9AA59D", "#1A1A1A", "#D9DED9"
Z = 1.959963984540054

# (termo, multiplicador do coeficiente, rótulo)
COEFS = (
    ("bolsa_mil", 5, "+R$ 5 mil de bolsa"),
    ("distancia_100km", 1, "+100 km de distância"),
    ("mesma_regiao_saude", 1, "Na mesma região de saúde\nde onde trabalhava"),
    ("mesmo_municipio", 1, "No mesmo município\n(além da região)"),
)
# (arquivo, chave_modelo, rótulo, principal?)
ROBUSTEZ = (
    ("VL", "VL1_emp", "Principal: ciclos 1–3", True),
    ("VL", "VL1log_emp", "Distância em log", True),
    ("VL", "VL3_VL1_emp", "Região anterior × UF da vaga", True),
    ("VL", "VL2_emp", "Só vagas perto do corte (±0,050)", True),
    ("VG", "VG1", "Só o ciclo 1", True),
    ("VG", "VL1_c2", "Só o ciclo 2", True),
    ("VG", "VG3", "Só o ciclo 3", True),
    ("VL", "M1_emp", "Pré-registrado: sem fixar a UF", False),
)


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def virgula(x: float, casas: int = 2) -> str:
    return f"{x:.{casas}f}".replace(".", ",").replace("-", "−")


def estilo(ax) -> None:
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color(GRADE)
    ax.tick_params(axis="y", length=0, labelsize=12, colors=TEXTO)
    ax.tick_params(axis="x", colors="#5E6660", labelsize=10)
    ax.set_xscale("log")
    ax.axvline(1, color="#5E6660", lw=1)


def figura_coeficientes() -> dict:
    d = pd.read_csv(VL)
    c = d[(d.chave_modelo == "VL1_emp") & (d.tipo_linha == "coeficiente")].set_index("termo")
    linhas = []
    for termo, k, rot in COEFS:
        b, lo, hi = (float(c.loc[termo, x]) * k for x in ("estimativa", "ic95_inf", "ic95_sup"))
        linhas.append({"termo": termo, "multiplo": k, "rotulo": rot.replace("\n", " "), "coef": b,
                       "x": math.exp(b), "x_inf": math.exp(lo), "x_sup": math.exp(hi)})
    fig, ax = plt.subplots(figsize=(7.4, 3.9), dpi=200)
    estilo(ax)
    ys = list(range(len(linhas)))[::-1]
    for y, l, (_, _, rot) in zip(ys, linhas, COEFS):
        cor = VERDE_ESC if l["termo"] == "bolsa_mil" else VERDE
        ax.plot([l["x_inf"], l["x_sup"]], [y, y], color=cor, lw=3, solid_capstyle="round")
        ax.plot(l["x"], y, "o", ms=10, color=cor, mec="white", mew=2)
        coef_txt = (f"β × 5 = {virgula(l['coef'], 3)}" if l["termo"] == "bolsa_mil"
                    else f"coef. = {virgula(l['coef'], 3)}")
        ax.text(5.3, y + 0.12, f"×{virgula(l['x'])}", va="center", ha="left", fontsize=14, fontweight="bold",
                color=TEXTO)
        ax.text(5.3, y - 0.22, coef_txt, va="center", ha="left", fontsize=9.5, color="#5E6660")
    ax.set_yticks(ys, [r for _, _, r in COEFS])
    ax.set_xlim(0.45, 5.0)
    ax.set_ylim(-0.6, len(linhas) - 0.4)
    ax.set_xticks([0.5, 1, 2, 4], ["×0,5", "×1", "×2", "×4"])
    ax.minorticks_off()
    ax.set_xlabel("quantas vezes a chance de uma vaga é multiplicada, contra outra igual no resto (escala log)",
                  fontsize=9.5, color="#5E6660")
    fig.subplots_adjust(left=0.36, right=0.79, top=0.97, bottom=0.17)
    saida = DIR / "coeficientes_vl1.png"
    fig.savefig(saida, facecolor="white")
    plt.close(fig)
    return {"arquivo": str(saida.relative_to(ROOT)), "linhas": linhas}


def figura_robustez() -> dict:
    tabs = {"VL": pd.read_csv(VL), "VG": pd.read_csv(VG)}
    linhas = []
    for arq, chave, rot, princ in ROBUSTEZ:
        t = tabs[arq]
        r = t[(t.chave_modelo == chave) & (t.tipo_linha == "razao_chances_por_5mil")]
        if len(r) != 1:
            raise SystemExit(f"ERRO: esperava 1 linha de razão de chances para {chave} em {arq}")
        r = r.iloc[0]
        linhas.append({"fonte": arq, "chave": chave, "rotulo": rot, "na_mesma_uf": princ, "rc": float(r.estimativa),
                       "inf": float(r.ic95_inf), "sup": float(r.ic95_sup), "exclui_1": bool(r.ic95_inf > 1)})
    fig, ax = plt.subplots(figsize=(7.6, 4.4), dpi=200)
    estilo(ax)
    ys = [7.6, 6.6, 5.6, 4.6, 3.3, 2.3, 1.3, 0.0]
    for y, l in zip(ys, linhas):
        cor = VERDE if (l["exclui_1"] and l["na_mesma_uf"]) else CINZA
        ax.plot([l["inf"], l["sup"]], [y, y], color=cor, lw=3, solid_capstyle="round")
        ax.plot(l["rc"], y, "o", ms=9, color=VERDE_ESC if l["chave"] == "VL1_emp" else cor, mec="white", mew=2)
        ax.text(3.45, y, f"×{virgula(l['rc'])}  [{virgula(l['inf'])}; {virgula(l['sup'])}]", va="center", ha="left",
                fontsize=11, color=TEXTO, fontweight="bold" if l["chave"] == "VL1_emp" else "normal")
    ax.set_yticks(ys, [l["rotulo"] for l in linhas])
    for t in ax.get_yticklabels():
        if t.get_text().startswith("Principal"):
            t.set_fontweight("bold")
    ax.axhline(3.95, color=GRADE, lw=1)
    ax.axhline(0.65, color=GRADE, lw=1)
    ax.set_xlim(0.6, 3.3)
    ax.set_ylim(-0.6, 8.2)
    ax.set_xticks([0.75, 1, 1.5, 2, 3], ["0,75", "1", "1,5", "2", "3"])
    ax.minorticks_off()
    ax.set_xlabel("razão de chances por +R$ 5 mil (escala log); 1 = a bolsa não muda a escolha", fontsize=9.5,
                  color="#5E6660")
    fig.subplots_adjust(left=0.42, right=0.69, top=0.98, bottom=0.13)
    saida = DIR / "robustez_vl1.png"
    fig.savefig(saida, facecolor="white")
    plt.close(fig)
    return {"arquivo": str(saida.relative_to(ROOT)), "linhas": linhas}


def main() -> int:
    DIR.mkdir(parents=True, exist_ok=True)
    plt.rcParams["font.family"] = "DejaVu Sans"
    coef, rob = figura_coeficientes(), figura_robustez()
    man = {"etapa": "figuras_banca_final", "natureza_dos_dados": "EMPIRICO",
           "script": str(Path(__file__).resolve().relative_to(ROOT)),
           "entradas": {str(p.relative_to(ROOT)): sha256(p) for p in (VL, VG)},
           "coeficientes_vl1": coef, "robustez_vl1": rob,
           "saidas": {f: sha256(ROOT / f) for f in (coef["arquivo"], rob["arquivo"])}}
    (DIR / "manifesto_figuras.json").write_text(json.dumps(man, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"coef": [(l["rotulo"], round(l["x"], 3)) for l in coef["linhas"]],
                      "rob": [(l["rotulo"], round(l["rc"], 3)) for l in rob["linhas"]]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
