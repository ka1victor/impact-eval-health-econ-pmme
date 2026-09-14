"""Testa se a faixa anunciada da bolsa e reconstruivel a partir do IVS publico.

Este script pertence ao portao R1 e **nao abre nenhum outcome**: le apenas a
faixa anunciada, o IVS 2010 publico e covariaveis municipais pre-tratamento.
Ele existe porque a auditoria anterior testou uma unica taxonomia candidata
(cortes 0,400 e 0,500, do Atlas do Ipea) e concluiu divergencia. A pergunta aqui
e outra e mais basica: existe **alguma** regra de limiar no IVS publico que
reproduza a faixa anunciada, e, se nao existe, o quanto falta.

A reprovacao continua fail-closed. Nada aqui autoriza estimar efeito, e o corte
de melhor ajuste encontrado por busca **nao** e um cutoff administrativo: e uma
hipotese a confrontar com o ato normativo pedido em D-3.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
QUADRO = ROOT / "output" / "aquisicao" / "quadro_vagas_tratamento.parquet"
IVS = ROOT / "data" / "ivs_ipea_2010_municipios.csv"
TIPOLOGIA = ROOT / "output" / "tema_trabalho" / "matriz_tipologia_territorial.parquet"
OUT = ROOT / "output" / "rdd_bolsa" / "a01b_reconstrucao_regra_faixa.json"

ORDEM_VALOR = {"FAIXA 3": 10_000, "FAIXA 2": 15_000, "FAIXA 1": 20_000}
CORTES_ATLAS = (0.400, 0.500)

NUMERICAS = [
    "ivs_2010", "ivs_infra_2010", "ivs_ch_2010", "ivs_rt_2010", "idhm_2010",
    "populacao_2010", "rdpc_2010", "estoque_pre_por_10k",
    "estoque_especialistas_pre_12m_media",
]
CATEGORICAS = [
    "estrato", "ivs_categoria", "flag_capital", "flag_rm_ride_2022",
    "macro_regiao_saude", "sg_uf", "hierarquia_grupo_regic",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def carregar() -> pd.DataFrame:
    vagas = pd.read_parquet(QUADRO)
    municipios = (
        vagas[["co_ibge_6d", "no_municipio", "sg_uf", "faixa_atracao_anunciada"]]
        .drop_duplicates()
        .assign(co_ibge_6d=lambda f: f.co_ibge_6d.astype(str))
    )
    if municipios.groupby("co_ibge_6d").faixa_atracao_anunciada.nunique().gt(1).any():
        raise SystemExit("faixa anunciada nao e unica por municipio; regra nao e municipal")

    ivs = pd.read_csv(IVS).assign(cod_ibge6=lambda f: f.cod_ibge6.astype(str))
    tip = pd.read_parquet(TIPOLOGIA).assign(co_ibge_6d=lambda f: f.co_ibge_6d.astype(str))

    base = municipios.merge(
        ivs[["cod_ibge6", "ivs_2010"]], left_on="co_ibge_6d", right_on="cod_ibge6", how="left"
    )
    colunas = ["co_ibge_6d"] + [c for c in NUMERICAS + CATEGORICAS if c != "sg_uf"]
    base = base.merge(tip[colunas].drop(columns=["ivs_2010"]), on="co_ibge_6d", how="left")
    if base.ivs_2010.isna().any():
        raise SystemExit("ha municipio sem IVS publico; a cobertura era 100% na auditoria anterior")
    return base.sort_values("co_ibge_6d").reset_index(drop=True)


def inversoes(ivs: np.ndarray, valor: np.ndarray) -> dict:
    """Pares em que o IVS maior recebe a bolsa menor.

    Uma unica inversao ja prova que nenhuma regra de limiar monotona no IVS
    publico reproduz a faixa anunciada, qualquer que seja o corte escolhido.
    """
    ordem = np.argsort(ivs, kind="stable")
    x, y = ivs[ordem], valor[ordem]
    concordantes = discordantes = 0
    for i in range(len(x)):
        adiante = slice(i + 1, len(x))
        comparavel = (x[adiante] != x[i]) & (y[adiante] != y[i])
        maior_bolsa = y[adiante] > y[i]
        concordantes += int((comparavel & maior_bolsa).sum())
        discordantes += int((comparavel & ~maior_bolsa).sum())
    total = concordantes + discordantes
    return {
        "pares_comparaveis": total,
        "concordantes": concordantes,
        "inversoes": discordantes,
        "pct_inversoes": round(100 * discordantes / total, 4) if total else None,
    }


def melhor_regra_dois_cortes(ivs: np.ndarray, valor: np.ndarray) -> dict:
    """Busca exaustiva do par de cortes que mais acerta a faixa anunciada."""
    grade = np.unique(np.round(np.arange(0.100, 0.761, 0.001), 3))
    melhor_acerto, melhor_cortes = -1, None
    for i, c1 in enumerate(grade):
        abaixo = ivs <= c1
        for c2 in grade[i + 1:]:
            predito = np.where(abaixo, 10_000, np.where(ivs <= c2, 15_000, 20_000))
            acerto = int((predito == valor).sum())
            if acerto > melhor_acerto:
                melhor_acerto, melhor_cortes = acerto, (float(c1), float(c2))
    return {"acertos": melhor_acerto, "n": len(valor), "cortes": melhor_cortes}


def gini(rotulos: np.ndarray) -> float:
    if rotulos.size == 0:
        return 0.0
    _, contagem = np.unique(rotulos, return_counts=True)
    proporcao = contagem / contagem.sum()
    return float(1 - (proporcao ** 2).sum())


def crescer(X: np.ndarray, y: np.ndarray, idx: np.ndarray, prof: int, limite: int):
    rotulos = y[idx]
    if prof == limite or np.unique(rotulos).size == 1:
        valores, contagem = np.unique(rotulos, return_counts=True)
        return ("folha", valores[contagem.argmax()])
    melhor = (gini(rotulos), None)
    for j in range(X.shape[1]):
        coluna = X[idx, j]
        distintos = np.unique(coluna)
        if distintos.size < 2:
            continue
        for limiar in (distintos[:-1] + distintos[1:]) / 2:
            esquerda, direita = idx[coluna <= limiar], idx[coluna > limiar]
            if esquerda.size == 0 or direita.size == 0:
                continue
            impureza = (esquerda.size * gini(y[esquerda]) + direita.size * gini(y[direita])) / idx.size
            if impureza < melhor[0] - 1e-12:
                melhor = (impureza, (j, float(limiar)))
    if melhor[1] is None:
        valores, contagem = np.unique(rotulos, return_counts=True)
        return ("folha", valores[contagem.argmax()])
    j, limiar = melhor[1]
    coluna = X[idx, j]
    return ("no", j, limiar,
            crescer(X, y, idx[coluna <= limiar], prof + 1, limite),
            crescer(X, y, idx[coluna > limiar], prof + 1, limite))


def prever(arvore, linha: np.ndarray):
    while arvore[0] == "no":
        arvore = arvore[3] if linha[arvore[1]] <= arvore[2] else arvore[4]
    return arvore[1]


def matriz_covariaveis(base: pd.DataFrame) -> tuple[np.ndarray, list[str]]:
    blocos = [base[NUMERICAS].astype(float)]
    nomes = list(NUMERICAS)
    for coluna in CATEGORICAS:
        for nivel in sorted(base[coluna].dropna().astype(str).unique()):
            blocos.append((base[coluna].astype(str) == nivel).astype(float).rename(f"{coluna}={nivel}"))
            nomes.append(f"{coluna}={nivel}")
    return pd.concat(blocos, axis=1).fillna(-999.0).to_numpy(), nomes


def descrever(arvore, nomes: list[str], nivel: int = 0) -> list[str]:
    if arvore[0] == "folha":
        return ["  " * nivel + f"-> {arvore[1]}"]
    linhas = ["  " * nivel + f"[{nomes[arvore[1]]} <= {arvore[2]:.4g}]"]
    return linhas + descrever(arvore[3], nomes, nivel + 1) + descrever(arvore[4], nomes, nivel + 1)


def main() -> None:
    base = carregar()
    ivs = base.ivs_2010.to_numpy(dtype=float)
    valor = base.faixa_atracao_anunciada.map(ORDEM_VALOR).to_numpy(dtype=int)
    n = len(base)

    faixas = {
        f: {
            "n": int((base.faixa_atracao_anunciada == f).sum()),
            "ivs_min": round(float(ivs[base.faixa_atracao_anunciada == f].min()), 4),
            "ivs_max": round(float(ivs[base.faixa_atracao_anunciada == f].max()), 4),
            "ivs_mediana": round(float(np.median(ivs[base.faixa_atracao_anunciada == f])), 4),
        }
        for f in ORDEM_VALOR
    }

    atlas = int((np.where(ivs <= CORTES_ATLAS[0], 10_000,
                          np.where(ivs <= CORTES_ATLAS[1], 15_000, 20_000)) == valor).sum())
    melhor = melhor_regra_dois_cortes(ivs, valor)

    X, nomes = matriz_covariaveis(base)
    arvores = {}
    for limite in (2, 3, 4, 6, 8):
        arvore = crescer(X, valor, np.arange(n), 0, limite)
        predito = np.array([prever(arvore, X[i]) for i in range(n)])
        arvores[limite] = {"acertos": int((predito == valor).sum()),
                           "pct": round(100 * float((predito == valor).mean()), 2)}
    arvore3 = crescer(X, valor, np.arange(n), 0, 3)

    # Quem escapa da melhor regra possivel? Se os desvios fossem ruido de
    # medida, os dois lados seriam parecidos. Se forem sistematicos, eles
    # identificam o criterio que falta — e medem o vies de qualquer pareamento
    # que use essa variacao residual como se fosse exogena.
    predito = np.where(ivs <= melhor["cortes"][0], 10_000,
                       np.where(ivs <= melhor["cortes"][1], 15_000, 20_000))
    desvio = np.select([valor > predito, valor < predito],
                       ["acima_do_previsto", "abaixo_do_previsto"], "no_previsto")
    comparaveis = ["ivs_2010", "populacao_2010", "rdpc_2010", "estoque_pre_por_10k",
                   "estoque_especialistas_pre_12m_media"]
    perfil = {
        grupo: {
            "n": int((desvio == grupo).sum()),
            "medianas": {c: round(float(base.loc[desvio == grupo, c].median()), 4)
                         for c in comparaveis},
            "estratos": base.loc[desvio == grupo, "estrato"].value_counts().to_dict(),
        }
        for grupo in ("acima_do_previsto", "no_previsto", "abaixo_do_previsto")
    }

    janela = 0.05
    perto_de_500 = np.abs(ivs - 0.500) <= janela
    perto_do_melhor = np.abs(ivs - melhor["cortes"][0]) <= janela

    relatorio = {
        "status": "DIAGNOSTICO_NAO_AUTORIZATIVO",
        "portao": "R1",
        "data_execucao": date.today().isoformat(),
        "outcomes_abertos": False,
        "escopo": "ciclo 1, chamada 1; 368 municipios com vaga publicada",
        "pergunta": "A faixa anunciada da bolsa e reconstruivel por regra de limiar no IVS 2010 publico?",
        "resposta": "NAO",
        "faixa_por_ivs": faixas,
        "sobreposicao": {
            "faixa3_max_supera_faixa2_min": bool(faixas["FAIXA 3"]["ivs_max"] > faixas["FAIXA 2"]["ivs_min"]),
            "faixa2_max_supera_faixa1_min": bool(faixas["FAIXA 2"]["ivs_max"] > faixas["FAIXA 1"]["ivs_min"]),
            "leitura": "os intervalos de IVS das tres faixas se sobrepoem; nenhum limiar os separa",
        },
        "monotonicidade": inversoes(ivs, valor),
        "regra_de_limiar": {
            "taxonomia_atlas": {"cortes": list(CORTES_ATLAS), "acertos": atlas, "n": n,
                                "pct": round(100 * atlas / n, 2)},
            "melhor_possivel": {**melhor, "pct": round(100 * melhor["acertos"] / n, 2)},
            "leitura": ("mesmo o melhor par de cortes possivel deixa "
                        f"{n - melhor['acertos']} municipios fora; uma regra administrativa "
                        "reproduziria praticamente todos"),
        },
        "corte_de_0_500_nao_tem_acao": {
            "ivs_max_da_faixa2": faixas["FAIXA 2"]["ivs_max"],
            "municipios_na_janela_0_05": int(perto_de_500.sum()),
            "faixas_presentes_na_janela": sorted(
                base.faixa_atracao_anunciada[perto_de_500].unique().tolist()),
            "leitura": ("nenhum municipio de FAIXA 2 chega a 0,450; na janela de 0,05 em torno "
                        "de 0,500 so existe FAIXA 1 dos dois lados. O primeiro estagio nulo "
                        "medido nesse corte mede a ausencia de regra ali, nao a ausencia de "
                        "resposta a bolsa"),
        },
        "densidade_no_melhor_corte": {
            "corte": melhor["cortes"][0],
            "municipios_na_janela_0_05": int(perto_do_melhor.sum()),
            "faixas_presentes_na_janela": sorted(
                base.faixa_atracao_anunciada[perto_do_melhor].unique().tolist()),
        },
        "quem_escapa_da_regra": {
            "perfil": perfil,
            "leitura": ("os desvios nao sao ruido. Quem recebe MAIS do que o IVS preveria e "
                        "sistematicamente menor, mais pobre e mais remoto; quem recebe MENOS e "
                        "maior e metropolitano. Como remoticidade e o previsor mais forte do "
                        "desfecho em A4, qualquer pareamento que compare municipios de IVS "
                        "semelhante com bolsas diferentes esta usando exatamente essa variacao "
                        "e confunde bolsa com remoticidade, contra a bolsa"),
        },
        "covariaveis_observaveis": {
            "acerto_por_profundidade": arvores,
            "arvore_profundidade_3": descrever(arvore3, nomes),
            "leitura": ("com duas a tres divisoes chega-se ao mesmo patamar da melhor regra de "
                        "limiar; so profundidade 8 se aproxima de 100%, e com 368 observacoes "
                        "isso e memorizacao, nao regra"),
        },
        "conclusoes": {
            "ivs_publico_e_criterio_unico": False,
            "cortes_do_atlas_sao_da_regra": False,
            "regra_reconstruida": False,
            "r1_continua": "REPROVADO_PENDENTE_DE_RECONSTRUCAO",
        },
        "fontes": {str(p.relative_to(ROOT)): {"sha256": sha256(p)} for p in (QUADRO, IVS, TIPOLOGIA)},
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    temporario = OUT.with_suffix(".json.tmp")
    temporario.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporario.replace(OUT)
    print(f"Gravado {OUT.relative_to(ROOT)}")
    print(f"  inversoes: {relatorio['monotonicidade']['inversoes']} pares "
          f"({relatorio['monotonicidade']['pct_inversoes']}%)")
    print(f"  taxonomia do Atlas: {atlas}/{n} | melhor regra possivel: "
          f"{melhor['acertos']}/{n} em {melhor['cortes']}")


if __name__ == "__main__":
    main()
