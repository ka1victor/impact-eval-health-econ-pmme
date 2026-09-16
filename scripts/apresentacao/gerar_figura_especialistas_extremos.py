# -*- coding: utf-8 -*-
"""Razão de especialistas por 100 mil habitantes: só os valores reportados.

Saída: output/apresentacao_banca1/especialistas_extremos_uf.png

Por que só quatro unidades da federação. A fonte é a `Demografia Médica no
Brasil 2025` (Scheffer et al., FMUSP/AMB). O PDF integral não foi baixado por
este projeto; o que está conferido, e registrado em
`docs/07_apresentacoes/banca1/03_proveniencia_figuras_e_numeros.md`, é a
cobertura que reporta as duas maiores e as duas menores razões do país:
Distrito Federal 453 e São Paulo 244; Maranhão 68 e Pará 70.

O template de apresentação trazia um gráfico com as 16 unidades ordenadas, mas
as catorze barras intermediárias eram números redondos interpolados, e duas
delas contradiziam a própria fonte (São Paulo aparecia em 414 e Pará em 145).
Esta figura mostra apenas o que a fonte reporta.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAIZ = Path(__file__).resolve().parents[2]
SAIDA = RAIZ / "output" / "apresentacao_banca1" / "especialistas_extremos_uf.png"

VERDE_ESCURO = "#114719"
VERDE_MEDIO = "#6E9E74"
VERDE_CLARO = "#BFD5C6"
TINTA = "#3A3A3A"
CINZA = "#7F7F7F"

# Conferido na cobertura da Agência Brasil sobre a Demografia Médica 2025.
VALORES = [
    ("DF", 453, VERDE_ESCURO),
    ("SP", 244, VERDE_MEDIO),
    ("PA", 70, VERDE_CLARO),
    ("MA", 68, VERDE_CLARO),
]


def main() -> None:
    fig, ax = plt.subplots(figsize=(9.0, 3.5), dpi=300)
    rotulos = [uf for uf, _, _ in VALORES]
    alturas = [v for _, v, _ in VALORES]
    cores = [c for _, _, c in VALORES]
    barras = ax.bar(rotulos, alturas, color=cores, width=0.58)
    for barra, valor in zip(barras, alturas):
        ax.text(barra.get_x() + barra.get_width() / 2, valor + 12, str(valor),
                ha="center", va="bottom", fontsize=17, fontweight="bold",
                color=VERDE_ESCURO)

    ax.text(0.5, 570, "as duas maiores razões do país", ha="center", fontsize=12.5,
            color=CINZA)
    ax.text(2.5, 570, "as duas menores", ha="center", fontsize=12.5, color=CINZA)
    ax.plot([-0.35, 1.35], [552, 552], color=CINZA, lw=0.9)
    ax.plot([1.65, 3.35], [552, 552], color=CINZA, lw=0.9)

    ax.set_ylim(0, 640)
    ax.set_yticks([0, 100, 200, 300, 400])
    ax.tick_params(axis="x", labelsize=16, colors=TINTA, length=0)
    ax.tick_params(axis="y", labelsize=12, colors=CINZA, length=0)
    ax.set_ylabel("Especialistas por\n100 mil habitantes", fontsize=13, color=TINTA)
    ax.grid(axis="y", linestyle=":", color="#D8D8D8", zorder=0)
    ax.set_axisbelow(True)
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color("#D8D8D8")

    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(SAIDA, bbox_inches="tight", pad_inches=0.08, facecolor="white")
    plt.close(fig)
    print(f"figura gravada em {SAIDA}")


if __name__ == "__main__":
    main()
