# -*- coding: utf-8 -*-
"""Versão de projeção da curva de custo laboral de Choné & Ma (2011).

Saída: output/apresentacao_banca1/custo_laboral_deck.png

Mesma construção conceitual de `scripts/utils/gerar_grafico_custo_laboral.py`,
que produz a figura do documento de teoria. Muda só o que a projeção exige:
proporção larga e baixa, paleta do deck e tipografia legível do fundo da sala.
A figura do documento continua como está e não é tocada aqui.

Ilustração conceitual: não há escala cardinal nem dado observado. C(q) é o
cansaço (C' > 0, C'' > 0), alpha*B(q) a satisfação (B' > 0, B'' < 0) e
c(q) = C(q) - alpha*B(q) o custo laboral líquido, em U.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

RAIZ = Path(__file__).resolve().parents[2]
SAIDA = RAIZ / "output" / "apresentacao_banca1" / "custo_laboral_deck.png"

VERDE_ESCURO = "#114719"
VERDE_MEDIO = "#6E9E74"
CINZA = "#8A8A8A"
CINZA_TINTA = "#3A3A3A"
ZONA_A = "#E7F1EA"
ZONA_B = "#F4F1E6"
ZONA_C = "#F2E9E9"


def main() -> None:
    q = np.linspace(0, 58, 600)
    cansaco = 0.4 * q + 0.035 * q**2
    satisfacao = 3.0 * (1 - np.exp(-0.06 * q)) * 30
    liquido = cansaco - satisfacao

    i_min = int(np.argmin(liquido))
    q_min = float(q[i_min])
    q_zero = float(np.interp(0, liquido[i_min:], q[i_min:]))

    fig, ax = plt.subplots(figsize=(9.0, 4.0), dpi=300)
    ax.axvspan(0, q_min, color=ZONA_A, zorder=0)
    ax.axvspan(q_min, q_zero, color=ZONA_B, zorder=0)
    ax.axvspan(q_zero, 58, color=ZONA_C, zorder=0)
    ax.axhline(0, color=CINZA, lw=1.0, zorder=1)

    ax.plot(q, cansaco, color=CINZA, lw=2.6, zorder=3)
    ax.plot(q, satisfacao, color=VERDE_MEDIO, lw=2.6, zorder=3)
    ax.plot(q, liquido, color=VERDE_ESCURO, lw=4.0, zorder=4)

    ax.plot([q_min, q_min], [-78, liquido[i_min]], color=CINZA, ls=":", lw=1.2, zorder=2)
    ax.plot([q_zero, q_zero], [-78, 0], color=CINZA, ls=":", lw=1.2, zorder=2)
    ax.scatter([q_min, q_zero], [liquido[i_min], 0], color=VERDE_ESCURO, s=70,
               zorder=6, edgecolors="white", linewidth=1.4)

    ax.text(58.8, cansaco[-1], "Cansaço\n$C(q)$", color=CINZA, fontsize=13,
            fontweight="bold", va="center")
    ax.text(58.8, satisfacao[-1], "Satisfação\n" + r"$\alpha B(q)$", color=VERDE_MEDIO,
            fontsize=13, fontweight="bold", va="center")
    ax.text(58.8, liquido[-1], "Custo líquido\n" + r"$c^{\rm laboral}(q)$",
            color=VERDE_ESCURO, fontsize=13, fontweight="bold", va="center")

    zonas = [
        (q_min / 2, "atender mais\nreduz o custo", VERDE_ESCURO),
        ((q_min + q_zero) / 2, "o custo volta\na subir", CINZA_TINTA),
        ((q_zero + 58) / 2, "exaustão:\ncansaço > satisfação", CINZA_TINTA),
    ]
    for x, texto, cor in zonas:
        ax.text(x, -64, texto, ha="center", va="center", fontsize=12.5, color=cor,
                linespacing=1.25, zorder=7)

    ax.set_xticks([q_min, q_zero])
    ax.set_xticklabels([r"$q$ de custo mínimo", r"$c = 0$"], fontsize=13)
    ax.set_yticks([0])
    ax.set_yticklabels(["0"], fontsize=13)
    ax.set_xlim(0, 58)
    ax.set_ylim(-78, 150)
    ax.set_xlabel("Volume de atendimentos  $q$", fontsize=14, labelpad=6, color=CINZA_TINTA)
    ax.set_ylabel("Custo laboral\nlíquido", fontsize=14, labelpad=8, color=CINZA_TINTA)
    ax.tick_params(colors=CINZA_TINTA, length=0)
    for lado in ("top", "right", "left", "bottom"):
        ax.spines[lado].set_visible(False)

    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(SAIDA, bbox_inches="tight", pad_inches=0.08, facecolor="white")
    plt.close(fig)
    print(f"figura gravada em {SAIDA}")


if __name__ == "__main__":
    main()
