"""Gera as figuras da apresentação da banca 1.

Saída: output/apresentacao_banca1/

Figuras:

1. `bolsa_por_faixa.png` — valor mensal da bolsa-formação por faixa de
   atração, conforme a Lei nº 15.233/2025 e o edital de 2025.

2. `oferta_pre_por_faixa.png` — especialistas por 100 mil habitantes em
   junho de 2025 (última competência anterior à publicação da oferta), nos
   municípios com vaga no ciclo 1, agrupados pela faixa de bolsa de 2025.

3. `oferta_antes_depois_por_faixa.png` — a mesma taxa, mensal, de junho de
   2024 a julho de 2026, com marcos da oferta e da homologação.

Numerador: `especialistas_mst` do painel município–curso–mês, restrito aos
cursos com correspondência unívoca curso–CBO (evita contar a mesma pessoa em
dois cursos). É presença cadastral no CNES nos CBOs do programa, não
participação no PMM-E.

Denominador: população residente do Censo 2022 (IBGE/SIDRA), adquirida por
`scripts/aquisicao/06_adquirir_populacao_censo2022.py`. A coluna
`populacao_2010` do repositório não é população residente e não é usada.

Leitura permitida: descritiva. Os 368 municípios são os que receberam vaga;
não há grupo de comparação fora do programa.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib
import matplotlib.ticker
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAIZ = Path(__file__).resolve().parents[2]
PAINEL = RAIZ / "output" / "avaliacao_impacto" / "dados" / "painel_municipio_curso_mes.parquet"
POPULACAO = RAIZ / "output" / "aquisicao" / "populacao_censo2022_municipios.csv"
SAIDA = RAIZ / "output" / "apresentacao_banca1"

VERDE_ESCURO = "#1F4022"
VERDE_MEDIO = "#8FAF95"
VERDE_CLARO = "#DCE6DC"
VERDE_CLARO_LINHA = "#A9C4AC"
TINTA = "#1A1A1A"
TINTA_SUAVE = "#5A5A5A"
GRADE = "#D8D8D8"

# Grade de 2025: Edital SGTES/MS nº 3/2025.
FAIXA_2025 = {
    "MUITO_ALTA": "Faixa 1",
    "ALTA": "Faixa 2",
    "MEDIA": "Faixa 3",
    "BAIXA": "Faixa 3",
    "MUITO_BAIXA": "Faixa 3",
}
ORDEM_FAIXAS = ["Faixa 3", "Faixa 2", "Faixa 1"]
ROTULO_FAIXA = {
    "Faixa 3": "Faixa 3\nR$ 10 mil\nmédia, baixa ou muito baixa",
    "Faixa 2": "Faixa 2\nR$ 15 mil\nalta",
    "Faixa 1": "Faixa 1\nR$ 20 mil\nmuito alta",
}
COR_FAIXA = {"Faixa 3": VERDE_CLARO_LINHA, "Faixa 2": VERDE_MEDIO, "Faixa 1": VERDE_ESCURO}
COR_BARRA = {"Faixa 3": VERDE_CLARO, "Faixa 2": VERDE_MEDIO, "Faixa 1": VERDE_ESCURO}

ULTIMA_PRE = "202506"      # última competência anterior à publicação da oferta
PRIMEIRA_POS = "202510"    # primeira competência integralmente pós-homologação

BOLSA_POR_FAIXA = [
    ("Faixa 3\nmédia, baixa\nou muito baixa", 10_000),
    ("Faixa 2\nalta", 15_000),
    ("Faixa 1\nmuito alta", 20_000),
]


def _hash(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def _limpar_moldura(ax) -> None:
    ax.yaxis.set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",")))
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color(GRADE)
    ax.tick_params(axis="both", length=0, colors=TINTA_SUAVE, labelsize=10)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color=GRADE, linewidth=0.8, linestyle=(0, (4, 4)))


def _rodape(fig, texto: str, y: float = -0.06) -> None:
    fig.text(0.5, y, texto, ha="center", fontsize=8.5, color=TINTA_SUAVE, wrap=True)


def _fmt(valor: float) -> str:
    return f"{valor:.1f}".replace(".", ",")


def taxas_por_faixa() -> tuple[pd.DataFrame, dict]:
    """Especialistas por 100 mil habitantes, por competência e faixa de 2025."""
    painel = pd.read_parquet(PAINEL)
    painel = painel[painel["curso_sem_sobreposicao"] == 1]
    pop = pd.read_csv(POPULACAO, dtype={"co_ibge_7d": str})

    municipio_mes = (
        painel.groupby(["competencia", "co_ibge_7d", "ivs_categoria"], as_index=False)
        ["especialistas_mst"].sum()
        .merge(pop[["co_ibge_7d", "populacao_2022"]], on="co_ibge_7d", how="left")
    )
    assert municipio_mes["populacao_2022"].notna().all(), "município sem população"
    municipio_mes["faixa"] = municipio_mes["ivs_categoria"].map(FAIXA_2025)

    agregado = (
        municipio_mes.groupby(["competencia", "faixa"])
        .agg(especialistas=("especialistas_mst", "sum"),
             populacao=("populacao_2022", "sum"),
             municipios=("co_ibge_7d", "nunique"))
        .reset_index()
    )
    agregado["por_100k"] = agregado["especialistas"] / agregado["populacao"] * 1e5

    detalhe_categoria = (
        municipio_mes[municipio_mes["competencia"] == ULTIMA_PRE]
        .groupby("ivs_categoria")
        .agg(especialistas=("especialistas_mst", "sum"),
             populacao=("populacao_2022", "sum"),
             municipios=("co_ibge_7d", "nunique"))
    )
    detalhe_categoria["por_100k"] = (
        detalhe_categoria["especialistas"] / detalhe_categoria["populacao"] * 1e5
    )
    meta = {
        "municipios": int(municipio_mes["co_ibge_7d"].nunique()),
        "cursos_unívocos": sorted(int(c) for c in painel["cod_curso"].unique()),
        "competencias": [str(painel["competencia"].min()), str(painel["competencia"].max())],
        "detalhe_por_categoria_ivs_em_202506": {
            k: {"municipios": int(v["municipios"]), "por_100k": round(float(v["por_100k"]), 2)}
            for k, v in detalhe_categoria.to_dict("index").items()
        },
    }
    return agregado, meta


def figura_bolsa_por_faixa() -> Path:
    fig, ax = plt.subplots(figsize=(8.4, 4.0), dpi=200)
    rotulos = [r for r, _ in BOLSA_POR_FAIXA]
    valores = [v for _, v in BOLSA_POR_FAIXA]
    barras = ax.bar(rotulos, valores, 0.55, color=[VERDE_CLARO, VERDE_MEDIO, VERDE_ESCURO])
    for barra, valor in zip(barras, valores):
        ax.annotate(f"R$ {valor:,.0f}".replace(",", "."),
                    (barra.get_x() + barra.get_width() / 2, valor),
                    textcoords="offset points", xytext=(0, 5),
                    ha="center", fontsize=12, color=VERDE_ESCURO, fontweight="bold")
    ax.set_ylabel("Bolsa mensal (R$)", fontsize=10.5, color=TINTA_SUAVE)
    ax.set_ylim(0, 24_000)
    _limpar_moldura(ax)
    ax.set_yticks([0, 5_000, 10_000, 15_000, 20_000])
    ax.set_yticklabels(["0", "5.000", "10.000", "15.000", "20.000"])
    ax.tick_params(axis="x", labelsize=10.5)
    _rodape(fig, "Faixa de atração pela categoria de vulnerabilidade do município (IVS 2010, Ipea). "
                 "Edital SGTES/MS nº 3/2025.", y=-0.08)
    destino = SAIDA / "bolsa_por_faixa.png"
    fig.savefig(destino, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return destino


def figura_oferta_pre(agregado: pd.DataFrame) -> Path:
    pre = agregado[agregado["competencia"] == ULTIMA_PRE].set_index("faixa").loc[ORDEM_FAIXAS]
    fig, ax = plt.subplots(figsize=(8.4, 4.2), dpi=200)
    barras = ax.bar([ROTULO_FAIXA[f] for f in ORDEM_FAIXAS], pre["por_100k"], 0.55,
                    color=[COR_BARRA[f] for f in ORDEM_FAIXAS])
    for barra, (faixa, linha) in zip(barras, pre.iterrows()):
        ax.annotate(_fmt(linha["por_100k"]),
                    (barra.get_x() + barra.get_width() / 2, linha["por_100k"]),
                    textcoords="offset points", xytext=(0, 5),
                    ha="center", fontsize=12.5, color=VERDE_ESCURO, fontweight="bold")
        ax.annotate(f"{int(linha['municipios'])} municípios",
                    (barra.get_x() + barra.get_width() / 2, 0),
                    textcoords="offset points", xytext=(0, 6),
                    ha="center", fontsize=8.5,
                    color="white" if faixa != "Faixa 3" else TINTA_SUAVE)
    ax.set_ylabel("Especialistas por 100 mil habitantes", fontsize=10.5, color=TINTA_SUAVE)
    ax.set_ylim(0, pre["por_100k"].max() * 1.22)
    _limpar_moldura(ax)
    ax.tick_params(axis="x", labelsize=10)
    _rodape(fig, "Junho de 2025, última competência anterior à publicação da oferta. Presença cadastral no "
                 "CNES nos CBOs dos cursos do programa com correspondência unívoca, nos municípios com vaga "
                 "no ciclo 1. População residente do Censo 2022.", y=-0.10)
    destino = SAIDA / "oferta_pre_por_faixa.png"
    fig.savefig(destino, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return destino


def figura_oferta_antes_depois(agregado: pd.DataFrame) -> Path:
    largo = agregado.pivot(index="competencia", columns="faixa", values="por_100k").sort_index()
    x = list(range(len(largo.index)))
    fig, ax = plt.subplots(figsize=(10.4, 4.6), dpi=200)

    for faixa in ORDEM_FAIXAS:
        serie = largo[faixa]
        ax.plot(x, serie.values, color=COR_FAIXA[faixa], linewidth=2.2, label=faixa)
        ax.annotate(f"{faixa}  {_fmt(serie.iloc[-1])}", (x[-1], serie.iloc[-1]),
                    textcoords="offset points", xytext=(6, 0), va="center",
                    fontsize=9.5, color=TINTA)
        ax.annotate(_fmt(serie.iloc[0]), (x[0], serie.iloc[0]),
                    textcoords="offset points", xytext=(-6, 0), va="center", ha="right",
                    fontsize=9, color=TINTA_SUAVE)

    idx = {c: i for i, c in enumerate(largo.index)}
    topo = largo.values.max() * 1.18
    for comp, texto, lado in ((ULTIMA_PRE, "última competência\npré-oferta (jun/25)", "right"),
                              (PRIMEIRA_POS, "primeira competência\npós-homologação (out/25)", "left")):
        ax.axvline(idx[comp], color=TINTA_SUAVE, linewidth=0.9, linestyle=(0, (3, 3)))
        deslocamento = -5 if lado == "right" else 5
        ax.annotate(texto, (idx[comp], topo * 0.99), textcoords="offset points",
                    xytext=(deslocamento, 0), ha=lado, va="top", fontsize=8.5, color=TINTA_SUAVE)

    rotulos = [c[4:] + "/" + c[2:4] if c.endswith(("01", "07")) else "" for c in largo.index]
    ax.set_xticks(x)
    ax.set_xticklabels(rotulos, fontsize=9)
    ax.set_xlim(-1.5, len(x) + 3.5)
    ax.set_ylim(0, largo.values.max() * 1.18)
    ax.set_ylabel("Especialistas por 100 mil habitantes", fontsize=10.5, color=TINTA_SUAVE)
    _limpar_moldura(ax)
    _rodape(fig, "Mensal, junho de 2024 a julho de 2026. Mesma definição da figura anterior. Sem grupo de comparação: "
                 "todos os municípios receberam vaga. Leitura descritiva.", y=-0.06)
    destino = SAIDA / "oferta_antes_depois_por_faixa.png"
    fig.savefig(destino, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return destino


def main() -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    antigo = SAIDA / "distribuicao_regional.png"
    if antigo.exists():
        antigo.unlink()   # substituída pelas figuras por habitante

    agregado, meta = taxas_por_faixa()
    gerados = [
        figura_bolsa_por_faixa(),
        figura_oferta_pre(agregado),
        figura_oferta_antes_depois(agregado),
    ]

    serie = agregado.pivot(index="competencia", columns="faixa", values="por_100k").round(2)
    manifesto = {
        "entradas": {
            "painel": {"caminho": str(PAINEL.relative_to(RAIZ)), "sha256": _hash(PAINEL),
                       "filtro": "curso_sem_sobreposicao == 1"},
            "populacao": {"caminho": str(POPULACAO.relative_to(RAIZ)), "sha256": _hash(POPULACAO),
                          "fonte": "IBGE, Censo 2022, SIDRA tabela 4709"},
        },
        "regra_de_faixa": {"grade": "Edital SGTES/MS nº 3/2025", "mapeamento": FAIXA_2025},
        "marcos": {"ultima_pre": ULTIMA_PRE, "primeira_pos": PRIMEIRA_POS},
        "cobertura": meta,
        "serie_por_100k": {faixa: serie[faixa].to_dict() for faixa in ORDEM_FAIXAS},
        "leitura": "descritiva; sem grupo de comparação; presença cadastral, não participação",
        "figuras": [str(c.relative_to(RAIZ)) for c in gerados],
    }
    (SAIDA / "manifesto_figuras.json").write_text(
        json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for c in gerados:
        print("gerado:", c.relative_to(RAIZ))
    print(serie.loc[[ULTIMA_PRE, PRIMEIRA_POS, serie.index.max()]].to_string())


if __name__ == "__main__":
    main()
