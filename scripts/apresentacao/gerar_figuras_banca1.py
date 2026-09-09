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

4. `retaguarda_por_faixa.png` — colegas da mesma especialidade que o médico
   encontraria no município, por faixa de 2025.

5. `vagas_ciclo1_por_regiao.png` — células estabelecimento–curso e vagas
   imediatas do ciclo 1 (chamada 1) por grande região, do quadro de vagas.

6. `preenchimento_ciclo1.png` — proporção de células com alguma confirmação ou
   homologação, por faixa anunciada e por estrato territorial, lida das tabelas
   descritivas do módulo A4 (`output/tema_trabalho/`). Leitura descritiva.

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
QUADRO = RAIZ / "output" / "aquisicao" / "quadro_vagas_tratamento.parquet"
A4_ESTRATO = RAIZ / "output" / "tema_trabalho" / "A4_tabela_01_amostra_construcao.csv"
A4_FAIXA = RAIZ / "output" / "tema_trabalho" / "A4_tabela_01b_amostra_faixa.csv"

REGIAO_UF = {
    "Norte": ["AC", "AM", "AP", "PA", "RO", "RR", "TO"],
    "Nordeste": ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"],
    "Centro-Oeste": ["DF", "GO", "MS", "MT"],
    "Sudeste": ["ES", "MG", "RJ", "SP"],
    "Sul": ["PR", "RS", "SC"],
}
ORDEM_REGIOES = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]
ROTULO_ESTRATO = {
    "capital": "Capital",
    "metropolitano": "Metropolitano",
    "interior_proximo_polo": "Interior\nconectado a polo",
    "interior_remoto": "Interior\nremoto",
}
ORDEM_ESTRATOS = ["capital", "metropolitano", "interior_proximo_polo", "interior_remoto"]

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


def figura_retaguarda_por_faixa() -> Path:
    """Quantos colegas da mesma especialidade o médico encontraria no município."""
    painel = pd.read_parquet(PAINEL)
    painel = painel[(painel["curso_sem_sobreposicao"] == 1) & (painel["competencia"] == ULTIMA_PRE)]
    painel = painel.assign(faixa=painel["ivs_categoria"].map(FAIXA_2025))
    resumo = painel.groupby("faixa").agg(
        celulas=("especialistas_mst", "size"),
        mediana=("especialistas_mst", "median"),
        ate_um=("especialistas_mst", lambda s: (s <= 1).mean() * 100),
    ).loc[ORDEM_FAIXAS]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.0, 4.0), dpi=200)

    barras = ax1.bar([ROTULO_FAIXA[f] for f in ORDEM_FAIXAS], resumo["mediana"], 0.55,
                     color=[COR_BARRA[f] for f in ORDEM_FAIXAS])
    for barra, valor in zip(barras, resumo["mediana"]):
        ax1.annotate(f"{valor:.0f}", (barra.get_x() + barra.get_width() / 2, valor),
                     textcoords="offset points", xytext=(0, 5), ha="center",
                     fontsize=13, color=VERDE_ESCURO, fontweight="bold")
    ax1.set_ylabel("Colegas da mesma especialidade\n(mediana por município)", fontsize=10, color=TINTA_SUAVE)
    ax1.set_ylim(0, resumo["mediana"].max() * 1.3)
    _limpar_moldura(ax1)

    barras = ax2.bar([ROTULO_FAIXA[f] for f in ORDEM_FAIXAS], resumo["ate_um"], 0.55,
                     color=[COR_BARRA[f] for f in ORDEM_FAIXAS])
    for barra, (faixa, linha) in zip(barras, resumo.iterrows()):
        ax2.annotate(f"{linha['ate_um']:.0f}%".replace(".", ","),
                     (barra.get_x() + barra.get_width() / 2, linha["ate_um"]),
                     textcoords="offset points", xytext=(0, 5), ha="center",
                     fontsize=13, color=VERDE_ESCURO, fontweight="bold")
        ax2.annotate(f"n = {int(linha['celulas'])}",
                     (barra.get_x() + barra.get_width() / 2, 0),
                     textcoords="offset points", xytext=(0, 6), ha="center",
                     fontsize=8.5, color="white" if faixa != "Faixa 3" else TINTA_SUAVE)
    ax2.set_ylabel("Sozinho ou com um único colega\n(% dos municípios)", fontsize=10, color=TINTA_SUAVE)
    ax2.set_ylim(0, resumo["ate_um"].max() * 1.35)
    _limpar_moldura(ax2)

    for eixo in (ax1, ax2):
        eixo.tick_params(axis="x", labelsize=9.5)

    _rodape(fig, "Junho de 2025. Especialistas da mesma especialidade cadastrados no município, "
                 "por par município–especialidade. Faixa 1 tem apenas 19 pares: a proporção é frágil, "
                 "a mediana é robusta.", y=-0.14)
    destino = SAIDA / "retaguarda_por_faixa.png"
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


def figura_vagas_por_regiao() -> tuple[Path, dict]:
    """Células e vagas imediatas do ciclo 1 por grande região."""
    quadro = pd.read_parquet(QUADRO)
    uf_para_regiao = {uf: r for r, ufs in REGIAO_UF.items() for uf in ufs}
    quadro = quadro.assign(regiao=quadro["sg_uf"].map(uf_para_regiao))
    assert quadro["regiao"].notna().all(), "UF sem região"
    resumo = quadro.groupby("regiao").agg(
        celulas=("co_cnes_7d", "size"),
        imediatas=("qt_vagas_imediatas", "sum"),
        reserva=("qt_vagas_reserva", "sum"),
        municipios=("co_ibge_6d", "nunique"),
    ).loc[ORDEM_REGIOES]

    fig, ax = plt.subplots(figsize=(9.0, 4.2), dpi=200)
    x = list(range(len(ORDEM_REGIOES)))
    largura = 0.38
    b1 = ax.bar([i - largura / 2 for i in x], resumo["celulas"], largura,
                color=VERDE_MEDIO, label="Células estabelecimento–curso")
    b2 = ax.bar([i + largura / 2 for i in x], resumo["imediatas"], largura,
                color=VERDE_ESCURO, label="Vagas imediatas")
    for barras in (b1, b2):
        for barra in barras:
            ax.annotate(f"{int(barra.get_height())}",
                        (barra.get_x() + barra.get_width() / 2, barra.get_height()),
                        textcoords="offset points", xytext=(0, 4), ha="center",
                        fontsize=10, color=TINTA)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{r}\n{int(resumo.loc[r, 'municipios'])} municípios" for r in ORDEM_REGIOES],
                       fontsize=9.5)
    ax.set_ylim(0, resumo["celulas"].max() * 1.2)
    ax.legend(frameon=False, fontsize=9.5, loc="upper right")
    _limpar_moldura(ax)
    _rodape(fig, "Ciclo 1, chamada 1: 1.295 células em 460 estabelecimentos e 368 municípios; 678 vagas "
                 "imediatas e 1.145 posições de cadastro de reserva. Quadro de vagas do Edital SGTES/MS nº 3/2025.",
            y=-0.10)
    destino = SAIDA / "vagas_ciclo1_por_regiao.png"
    fig.savefig(destino, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return destino, {r: {k: int(v) for k, v in linha.items()} for r, linha in resumo.to_dict("index").items()}


def figura_preenchimento_ciclo1() -> tuple[Path, dict]:
    """Proporção de células com alguma confirmação ou homologação, por faixa anunciada e por estrato."""
    faixa = pd.read_csv(A4_FAIXA).set_index("faixa")
    faixa = faixa.loc[["FAIXA 3", "FAIXA 2", "FAIXA 1"]]
    estrato = pd.read_csv(A4_ESTRATO)
    estrato = estrato[estrato["amostra"] == "primaria_1295_Ch1"].set_index("estrato").loc[ORDEM_ESTRATOS]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.4, 4.2), dpi=200,
                                   gridspec_kw={"width_ratios": [3, 4]})

    rot_faixa = {"FAIXA 3": "Faixa 3\nR$ 10 mil", "FAIXA 2": "Faixa 2\nR$ 15 mil", "FAIXA 1": "Faixa 1\nR$ 20 mil"}
    cores = [VERDE_CLARO, VERDE_MEDIO, VERDE_ESCURO]
    barras = ax1.bar([rot_faixa[f] for f in faixa.index], faixa["outcome_medio"] * 100, 0.55, color=cores)
    for barra, (nome, linha) in zip(barras, faixa.iterrows()):
        ax1.annotate(f"{linha['outcome_medio'] * 100:.1f}%".replace(".", ","),
                     (barra.get_x() + barra.get_width() / 2, linha["outcome_medio"] * 100),
                     textcoords="offset points", xytext=(0, 5), ha="center",
                     fontsize=12.5, color=VERDE_ESCURO, fontweight="bold")
        ax1.annotate(f"n = {int(linha['n_celulas'])}", (barra.get_x() + barra.get_width() / 2, 0),
                     textcoords="offset points", xytext=(0, 6), ha="center", fontsize=8.5,
                     color="white" if nome != "FAIXA 3" else TINTA_SUAVE)
    ax1.set_title("Por faixa de bolsa anunciada", fontsize=10.5, color=TINTA, loc="left")
    ax1.set_ylabel("Células com alguma confirmação\nou homologação (%)", fontsize=10, color=TINTA_SUAVE)
    ax1.set_ylim(0, 60)
    _limpar_moldura(ax1)

    barras = ax2.bar([ROTULO_ESTRATO[e] for e in ORDEM_ESTRATOS], estrato["outcome_medio"] * 100, 0.55,
                     color=[VERDE_ESCURO, VERDE_ESCURO, VERDE_MEDIO, VERDE_CLARO])
    for barra, (nome, linha) in zip(barras, estrato.iterrows()):
        ax2.annotate(f"{linha['outcome_medio'] * 100:.1f}%".replace(".", ","),
                     (barra.get_x() + barra.get_width() / 2, linha["outcome_medio"] * 100),
                     textcoords="offset points", xytext=(0, 5), ha="center",
                     fontsize=12.5, color=VERDE_ESCURO, fontweight="bold")
        ax2.annotate(f"n = {int(linha['n_celulas'])}", (barra.get_x() + barra.get_width() / 2, 0),
                     textcoords="offset points", xytext=(0, 6), ha="center", fontsize=8.5,
                     color="white" if nome in ("capital", "metropolitano") else TINTA_SUAVE)
    ax2.set_title("Por estrato territorial", fontsize=10.5, color=TINTA, loc="left")
    ax2.set_ylim(0, 60)
    _limpar_moldura(ax2)
    for eixo in (ax1, ax2):
        eixo.tick_params(axis="x", labelsize=9.5)

    _rodape(fig, "Ciclo 1, chamada 1: 1.295 células estabelecimento–curso em 368 municípios; média geral de 30,3%. "
                 "Faixa é a publicada na vaga. Estratos pela REGIC 2018 e composição de RMs/RIDEs 2022 (IBGE). "
                 "Leitura descritiva: proporções brutas, sem ajuste.", y=-0.12)
    destino = SAIDA / "preenchimento_ciclo1.png"
    fig.savefig(destino, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    meta = {
        "por_faixa": {f: {"n": int(l["n_celulas"]), "pct": round(float(l["outcome_medio"]) * 100, 1)}
                      for f, l in faixa.iterrows()},
        "por_estrato": {e: {"n": int(l["n_celulas"]), "pct": round(float(l["outcome_medio"]) * 100, 1)}
                        for e, l in estrato.iterrows()},
    }
    return destino, meta


def main() -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    antigo = SAIDA / "distribuicao_regional.png"
    if antigo.exists():
        antigo.unlink()   # substituída pelas figuras por habitante

    agregado, meta = taxas_por_faixa()
    fig_regiao, meta_regiao = figura_vagas_por_regiao()
    fig_preench, meta_preench = figura_preenchimento_ciclo1()
    gerados = [
        figura_bolsa_por_faixa(),
        figura_oferta_pre(agregado),
        figura_retaguarda_por_faixa(),
        figura_oferta_antes_depois(agregado),
        fig_regiao,
        fig_preench,
    ]

    serie = agregado.pivot(index="competencia", columns="faixa", values="por_100k").round(2)
    manifesto = {
        "entradas": {
            "painel": {"caminho": str(PAINEL.relative_to(RAIZ)), "sha256": _hash(PAINEL),
                       "filtro": "curso_sem_sobreposicao == 1"},
            "populacao": {"caminho": str(POPULACAO.relative_to(RAIZ)), "sha256": _hash(POPULACAO),
                          "fonte": "IBGE, Censo 2022, SIDRA tabela 4709"},
            "quadro_vagas": {"caminho": str(QUADRO.relative_to(RAIZ)), "sha256": _hash(QUADRO)},
            "a4_estrato": {"caminho": str(A4_ESTRATO.relative_to(RAIZ)), "sha256": _hash(A4_ESTRATO)},
            "a4_faixa": {"caminho": str(A4_FAIXA.relative_to(RAIZ)), "sha256": _hash(A4_FAIXA)},
        },
        "vagas_ciclo1_por_regiao": meta_regiao,
        "preenchimento_ciclo1": meta_preench,
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
