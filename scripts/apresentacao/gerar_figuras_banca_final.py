"""Figuras da banca final (versão sobre o deck do grupo de 11/11/2026).

Gera, lendo só `output/`:
- `output/apresentacao_banca_final/figuras/coeficientes_vl1.png`: o que cada coeficiente do VL-1 (ciclos 1–3) faz
  com a chance de uma vaga contra outra, em escala multiplicativa (×), com IC 95%.
- `output/apresentacao_banca_final/figuras/robustez_vl1.png`: razão de chances por +R$ 5 mil nas variantes que
  comparam vagas da mesma UF (VL e VG). O modelo sem o par de UFs (M1) saiu da figura (pedido do autor de 14/11).
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
    ("VL", "VL1_emp", "Mesma UF, ciclos 1–3", True),
    ("VL", "VL1log_emp", "Distância em log", True),
    ("VL", "VL3_VL1_emp", "Região anterior × UF da vaga", True),
    ("VL", "VL2_emp", "Perto do corte (±0,05)", True),
    ("VG", "VG1", "Só o ciclo 1", True),
    ("VG", "VL1_c2", "Só o ciclo 2", True),
    ("VG", "VG3", "Só o ciclo 3", True),
)
# grupos da figura (versão de 14/11): título e as linhas de cada um, na ordem da leitura
# rodada 13 (15/11): "só parte dos dados" antes de "outras medidas" (pedido do autor)
GRUPOS_ROB = (("Principal", ("VL1_emp",)),
              ("Só parte dos dados", ("VL2_emp", "VG1", "VL1_c2", "VG3")),
              ("Outras medidas", ("VL1log_emp", "VL3_VL1_emp")))


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
    # versão de 14/11: maior, letra maior e menos branco (o slide usa a figura em 8,3 × 4,1 polegadas)
    fig, ax = plt.subplots(figsize=(8.3, 4.1), dpi=200)
    estilo(ax)
    ax.tick_params(axis="y", labelsize=15)
    ax.tick_params(axis="x", labelsize=12)
    ys = list(range(len(linhas)))[::-1]
    for y, l in zip(ys, linhas):
        cor = VERDE_ESC if l["termo"] == "bolsa_mil" else VERDE
        ax.plot([l["x_inf"], l["x_sup"]], [y, y], color=cor, lw=4, solid_capstyle="round")
        ax.plot(l["x"], y, "o", ms=13, color=cor, mec="white", mew=2)
        ax.text(4.6, y, f"×{virgula(l['x'])}", va="center", ha="left", fontsize=19, fontweight="bold",
                color=VERDE_ESC if l["termo"] == "bolsa_mil" else TEXTO)
    ax.set_yticks(ys, [r for _, _, r in COEFS])
    for tl in ax.get_yticklabels():
        if tl.get_text().startswith("+R$"):
            tl.set_fontweight("bold")
    ax.set_xlim(0.45, 4.4)
    ax.set_ylim(-0.5, len(linhas) - 0.5)
    ax.set_xticks([0.5, 1, 2, 4], ["×0,5", "×1", "×2", "×4"])
    ax.minorticks_off()
    ax.set_xlabel("quantas vezes a chance da vaga é multiplicada (escala log)", fontsize=12, color="#5E6660")
    fig.subplots_adjust(left=0.37, right=0.84, top=0.98, bottom=0.15)
    saida = DIR / "coeficientes_vl1.png"
    fig.savefig(saida, facecolor="white")
    plt.close(fig)
    return {"arquivo": str(saida.relative_to(ROOT)), "linhas": linhas}


# Versão do slide de resultado do colega (14/11): seis fatores, do que mais aumenta ao que mais reduz a chance.
# (termo, multiplicador, rótulo); log_populacao_2022 × ln 2 = população em dobro.
COEFS_SEIS = (
    ("mesma_regiao_saude", 1, "Vaga na mesma região de saúde"),
    ("mesmo_municipio", 1, "Mesmo município (além da região)"),
    ("bolsa_mil", 5, "+R$ 5 mil de bolsa"),
    ("log_populacao_2022", math.log(2), "Cidade com o dobro da população"),
    ("capital", 1, "Vaga em capital"),
    ("distancia_100km", 1, "+100 km de distância"),
)


def figura_seis_fatores() -> dict:
    d = pd.read_csv(VL)
    c = d[(d.chave_modelo == "VL1_emp") & (d.tipo_linha == "coeficiente")].set_index("termo")
    linhas = []
    for termo, k, rot in COEFS_SEIS:
        b, lo, hi = (float(c.loc[termo, x]) * k for x in ("estimativa", "ic95_inf", "ic95_sup"))
        linhas.append({"termo": termo, "multiplo": k, "rotulo": rot, "coef": b, "x": math.exp(b),
                       "x_inf": math.exp(lo), "x_sup": math.exp(hi), "inclui_1": lo <= 0 <= hi})
    fig, ax = plt.subplots(figsize=(7.6, 4.2), dpi=200)
    estilo(ax)
    ax.tick_params(axis="y", labelsize=12.5)
    ax.tick_params(axis="x", labelsize=10)
    ys = list(range(len(linhas)))[::-1]
    for y, l in zip(ys, linhas):
        bolsa = l["termo"] == "bolsa_mil"
        if bolsa:
            ax.axhspan(y - 0.42, y + 0.42, color="#E6EEE7", zorder=0)
        cor = CINZA if l["inclui_1"] else (VERDE_ESC if bolsa else VERDE)
        ax.plot([l["x_inf"], l["x_sup"]], [y, y], color=cor, lw=4, solid_capstyle="round", zorder=2)
        ax.plot(l["x"], y, "o", ms=11, color=cor, mec="white", mew=1.5, zorder=3)
        rot = f"×{virgula(l['x'])}" + ("  (inclui 1)" if l["inclui_1"] else "")
        ax.text(1.03, y, rot, transform=ax.get_yaxis_transform(), va="center", ha="left", fontsize=12.5,
                fontweight="bold" if bolsa else "normal", color=TEXTO)
    ax.set_yticks(ys, [l["rotulo"] for l in linhas])
    for tl in ax.get_yticklabels():
        if tl.get_text().startswith("+R$"):
            tl.set_fontweight("bold")
    ax.set_xlim(0.45, 4.4)
    ax.set_ylim(-0.6, len(linhas) - 0.4)
    ax.set_xticks([0.5, 1, 2, 4], ["×0,5", "×1", "×2", "×4"])
    ax.minorticks_off()
    fig.subplots_adjust(left=0.45, right=0.76, top=0.98, bottom=0.08)
    saida = DIR / "coeficientes_vl1_seis.png"
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
    # versão de 14/11: grupos com título, letra maior, menos branco
    por_chave = {l["chave"]: l for l in linhas}
    pos, y, titulos = {}, 0.0, []
    for tit, chaves in GRUPOS_ROB:
        titulos.append((y, tit))
        y += 0.75
        for ch in chaves:
            pos[ch] = y
            y += 1.0
        y += 0.35
    alto = y
    fig, ax = plt.subplots(figsize=(8.1, 5.6), dpi=200)
    estilo(ax)
    ax.tick_params(axis="y", labelsize=13)
    ax.tick_params(axis="x", labelsize=11)
    for ch, yy in pos.items():
        l = por_chave[ch]
        cor = VERDE if (l["exclui_1"] and l["na_mesma_uf"]) else CINZA
        ax.plot([l["inf"], l["sup"]], [yy, yy], color=cor, lw=4, solid_capstyle="round")
        ax.plot(l["rc"], yy, "o", ms=11, color=VERDE_ESC if ch == "VL1_emp" else cor, mec="white", mew=2)
        tr = ax.get_yaxis_transform()  # x em fração do eixo, y em dados
        ax.text(1.04, yy, f"×{virgula(l['rc'])}", transform=tr, va="center", ha="left", fontsize=15, color=TEXTO,
                fontweight="bold")
        ax.text(1.38, yy, f"[{virgula(l['inf'])}; {virgula(l['sup'])}]", transform=tr, va="center", ha="left",
                fontsize=11, color="#5E6660")
    for yy, tit in titulos:
        ax.text(-0.02, yy, tit.upper(), transform=ax.get_yaxis_transform(), ha="right", va="center", fontsize=10.5,
                fontweight="bold", color=VERDE_ESC)
        if yy > 0:
            ax.axhline(yy - 0.45, color=GRADE, lw=1)
    ax.set_yticks(list(pos.values()), [por_chave[ch]["rotulo"] for ch in pos])
    for tl in ax.get_yticklabels():
        if tl.get_text().startswith("Mesma UF"):
            tl.set_fontweight("bold")
    ax.set_xlim(0.6, 3.2)
    ax.set_ylim(alto - 0.2, -0.5)
    ax.set_xticks([0.75, 1, 1.5, 2, 3], ["0,75", "1", "1,5", "2", "3"])
    ax.minorticks_off()
    ax.set_xlabel("razão de chances por +R$ 5 mil (escala log); 1 = a bolsa não muda a escolha", fontsize=11,
                  color="#5E6660")
    fig.subplots_adjust(left=0.36, right=0.66, top=0.99, bottom=0.11)
    saida = DIR / "robustez_vl1.png"
    fig.savefig(saida, facecolor="white")
    plt.close(fig)
    return {"arquivo": str(saida.relative_to(ROOT)), "linhas": linhas}


def main() -> int:
    DIR.mkdir(parents=True, exist_ok=True)
    plt.rcParams["font.family"] = "DejaVu Sans"
    coef, rob, seis = figura_coeficientes(), figura_robustez(), figura_seis_fatores()
    man = {"etapa": "figuras_banca_final", "natureza_dos_dados": "EMPIRICO",
           "script": str(Path(__file__).resolve().relative_to(ROOT)),
           "entradas": {str(p.relative_to(ROOT)): sha256(p) for p in (VL, VG)},
           "coeficientes_vl1": coef, "robustez_vl1": rob, "coeficientes_vl1_seis": seis,
           "saidas": {f: sha256(ROOT / f) for f in (coef["arquivo"], rob["arquivo"], seis["arquivo"])}}
    (DIR / "manifesto_figuras.json").write_text(json.dumps(man, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"coef": [(l["rotulo"], round(l["x"], 3)) for l in coef["linhas"]],
                      "rob": [(l["rotulo"], round(l["rc"], 3)) for l in rob["linhas"]]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
