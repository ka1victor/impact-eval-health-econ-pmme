"""Gera as figuras da apresentação da banca 1.

Saída: output/apresentacao_banca1/

Duas figuras são produzidas aqui:

1. `distribuicao_regional.png` — participação regional dos especialistas
   existentes (2024) contra os profissionais ativos no ciclo 1 do PMM-E.
   A série do PMM-E é calculada de `data/pmm_especialistas_nominal.csv`.
   A série de estoque é constante externa declarada abaixo, de Demografia
   Médica no Brasil 2025, e NÃO é reproduzível a partir do repositório.

2. `bolsa_por_faixa.png` — valor mensal da bolsa-formação por faixa de
   atração, conforme a Lei nº 15.233/2025 e o edital do PMM-E.

Motivo de existir: a figura equivalente do material anterior não reproduzia
nas bases. Ver docs/04_dados/02_inventario_dados_por_outcome.md, seção 4.1.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAIZ = Path(__file__).resolve().parents[2]
ENTRADA = RAIZ / "data" / "pmm_especialistas_nominal.csv"
SAIDA = RAIZ / "output" / "apresentacao_banca1"

VERDE_ESCURO = "#1F4022"
VERDE_MEDIO = "#8FAF95"
VERDE_CLARO = "#DCE6DC"
TINTA = "#1A1A1A"
TINTA_SUAVE = "#5A5A5A"
GRADE = "#D8D8D8"

REGIOES = ["Nordeste", "Norte", "Centro-Oeste", "Sudeste", "Sul"]

# Fonte externa, não reproduzível no repositório:
# Scheffer, M. (coord.). Demografia Médica no Brasil 2025.
ESTOQUE_2024_EXTERNO = {
    "Nordeste": 14.5,
    "Norte": 6.1,
    "Centro-Oeste": 7.5,
    "Sudeste": 55.3,
    "Sul": 16.6,
}

# Lei nº 15.233/2025 e edital do PMM-E.
BOLSA_POR_FAIXA = [
    ("Faixa 3\nmédia, baixa\nou muito baixa", 10_000),
    ("Faixa 2\nalta", 15_000),
    ("Faixa 1\nmuito alta", 20_000),
]


def _hash(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def _limpar_moldura(ax) -> None:
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color(GRADE)
    ax.tick_params(axis="both", length=0, colors=TINTA_SUAVE, labelsize=10)
    ax.set_axisbelow(True)


def participacao_pmme_ciclo1() -> tuple[dict[str, float], int, str]:
    """Participação regional dos ativos do ciclo 1, em porcentagem."""
    with ENTRADA.open(encoding="utf-8") as arquivo:
        linhas = [linha for linha in csv.DictReader(arquivo) if linha["ciclo"] == "1"]
    contagem = Counter(linha["regiao"] for linha in linhas)
    total = len(linhas)
    participacao = {
        regiao: 100 * contagem[regiao.upper().replace("Ç", "C")] / total
        for regiao in REGIOES
    }
    referencia = {linha["dt_referencia"] for linha in linhas}.pop()
    return participacao, total, referencia


def figura_distribuicao_regional(participacao, total, referencia) -> Path:
    fig, ax = plt.subplots(figsize=(9.6, 4.4), dpi=200)
    posicoes = range(len(REGIOES))
    largura = 0.38

    estoque = [ESTOQUE_2024_EXTERNO[r] for r in REGIOES]
    pmme = [participacao[r] for r in REGIOES]

    barras_a = ax.bar([p - largura / 2 for p in posicoes], estoque, largura,
                      color=VERDE_MEDIO, label="Especialistas existentes (2024)")
    barras_b = ax.bar([p + largura / 2 for p in posicoes], pmme, largura,
                      color=VERDE_ESCURO, label="PMM-E, ativos do ciclo 1")

    for barras in (barras_a, barras_b):
        for barra in barras:
            ax.annotate(f"{barra.get_height():.1f}%".replace(".", ","),
                        (barra.get_x() + barra.get_width() / 2, barra.get_height()),
                        textcoords="offset points", xytext=(0, 4),
                        ha="center", fontsize=9.5, color=TINTA, fontweight="medium")

    ax.set_xticks(list(posicoes))
    ax.set_xticklabels(REGIOES, fontsize=11, color=TINTA)
    ax.set_ylabel("Participação (%)", fontsize=10.5, color=TINTA_SUAVE)
    ax.set_ylim(0, 70)
    ax.set_yticks([0, 20, 40, 60])
    ax.yaxis.grid(True, color=GRADE, linewidth=0.8, linestyle=(0, (4, 4)))
    _limpar_moldura(ax)
    ax.legend(frameon=False, fontsize=10, loc="upper center",
              bbox_to_anchor=(0.5, 1.14), ncols=2, labelcolor=TINTA)

    fig.text(0.5, -0.06,
             f"PMM-E: {total} profissionais ativos do ciclo 1, referência {referencia}. "
             "Estoque 2024: Demografia Médica no Brasil 2025.",
             ha="center", fontsize=8.5, color=TINTA_SUAVE)

    destino = SAIDA / "distribuicao_regional.png"
    fig.savefig(destino, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return destino


def figura_bolsa_por_faixa() -> Path:
    fig, ax = plt.subplots(figsize=(8.4, 4.0), dpi=200)
    rotulos = [r for r, _ in BOLSA_POR_FAIXA]
    valores = [v for _, v in BOLSA_POR_FAIXA]

    barras = ax.bar(rotulos, valores, 0.55,
                    color=[VERDE_CLARO, VERDE_MEDIO, VERDE_ESCURO])
    for barra, valor in zip(barras, valores):
        ax.annotate(f"R$ {valor:,.0f}".replace(",", "."),
                    (barra.get_x() + barra.get_width() / 2, valor),
                    textcoords="offset points", xytext=(0, 5),
                    ha="center", fontsize=12, color=VERDE_ESCURO, fontweight="bold")

    ax.set_ylabel("Bolsa mensal (R$)", fontsize=10.5, color=TINTA_SUAVE)
    ax.set_ylim(0, 24_000)
    ax.set_yticks([0, 5_000, 10_000, 15_000, 20_000])
    ax.set_yticklabels(["0", "5.000", "10.000", "15.000", "20.000"])
    ax.yaxis.grid(True, color=GRADE, linewidth=0.8, linestyle=(0, (4, 4)))
    _limpar_moldura(ax)
    ax.tick_params(axis="x", labelsize=10.5)

    ax.annotate("", xy=(2.42, 20_000), xytext=(2.42, 10_000),
                arrowprops=dict(arrowstyle="<->", color=TINTA_SUAVE, linewidth=1))
    ax.text(2.5, 15_000, "o dobro\nda Faixa 3", fontsize=10,
            color=TINTA, va="center", linespacing=1.4)
    ax.set_xlim(-0.6, 3.2)

    fig.text(0.5, -0.08,
             "Faixa de atração pela vulnerabilidade declarada do município. "
             "Lei nº 15.233/2025 e edital do PMM-E.",
             ha="center", fontsize=8.5, color=TINTA_SUAVE)

    destino = SAIDA / "bolsa_por_faixa.png"
    fig.savefig(destino, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return destino


def main() -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    participacao, total, referencia = participacao_pmme_ciclo1()

    gerados = [
        figura_distribuicao_regional(participacao, total, referencia),
        figura_bolsa_por_faixa(),
    ]

    manifesto = {
        "entrada": {
            "caminho": str(ENTRADA.relative_to(RAIZ)),
            "sha256": _hash(ENTRADA),
            "dt_referencia": referencia,
            "recorte": "ciclo == 1",
            "registros": total,
        },
        "constantes_externas": {
            "estoque_2024": {
                "valores": ESTOQUE_2024_EXTERNO,
                "fonte": "Scheffer, M. (coord.). Demografia Médica no Brasil 2025",
                "reproduzivel_no_repositorio": False,
            },
            "bolsa_por_faixa": {
                "valores": {r.split("\n")[0]: v for r, v in BOLSA_POR_FAIXA},
                "fonte": "Lei nº 15.233/2025 e edital do PMM-E",
            },
        },
        "participacao_pmme_ciclo1_pct": {
            regiao: round(valor, 1) for regiao, valor in participacao.items()
        },
        "figuras": [str(caminho.relative_to(RAIZ)) for caminho in gerados],
    }
    (SAIDA / "manifesto_figuras.json").write_text(
        json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    for caminho in gerados:
        print("gerado:", caminho.relative_to(RAIZ))
    print("participação PMM-E ciclo 1:", manifesto["participacao_pmme_ciclo1_pct"])


if __name__ == "__main__":
    main()
