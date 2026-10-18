"""Valida o IVS 2010 oficial do Ipea como o escore administrativo completo.

Compara a base oficial (a08) com o escore publicado pelo MS para 404
municípios (a07) e com a categoria administrativa dos 5.570 municípios.
Se bater, grava o escore completo no formato do E3 e refaz o R1 com
cobertura total das populações P1 e P2. Não abre outcome.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OFICIAL = ROOT / "output" / "aquisicao" / "a08_ivs_2010_oficial_municipio.csv"
ADMIN = ROOT / "output" / "aquisicao" / "a07_ivs_administrativo_municipio.csv"
CATEGORIA = ROOT / "output" / "aquisicao" / "a07_categoria_ivs_pmmb_municipio.csv"
MATRIZ = ROOT / "output" / "rdd_bolsa" / "matriz_municipio_escore_administrativo.csv"
LOCAL = ROOT / "data" / "ivs_ipea_2010_municipios.csv"
OUT_ESCORE = ROOT / "output" / "rdd_bolsa" / "escore_completo_ivs2010_oficial.csv"
OUT_JSON = ROOT / "output" / "rdd_bolsa" / "portao_r1_ivs_oficial.json"

POPULACOES = {"P1": ["c1_ch1"], "P2": ["c2_ch1", "c2_ch2"], "ciclo_3_congelado": ["c3_ch1"]}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while bloco := f.read(65536):
            h.update(bloco)
    return h.hexdigest()


def categoria(s_mil: int) -> str:
    if s_mil <= 200:
        return "MUITO BAIXA VULNERABILIDADE"
    if s_mil <= 300:
        return "BAIXA VULNERABILIDADE"
    if s_mil <= 400:
        return "MEDIA VULNERABILIDADE"
    if s_mil <= 500:
        return "ALTA VULNERABILIDADE"
    return "MUITO ALTA VULNERABILIDADE"


def faixa(s_mil: int) -> str:
    return "FAIXA 3" if s_mil <= 300 else ("FAIXA 2" if s_mil <= 400 else "FAIXA 1")


def milesimos(valores: pd.Series) -> pd.Series:
    """IVS em milésimos inteiros (três casas decimais)."""
    return np.round(valores * 1000).astype(int)


def conferir_escore_administrativo(of: pd.DataFrame, adm: pd.DataFrame, cat: pd.DataFrame) -> dict:
    """Confere o IVS oficial contra o escore e a categoria administrativos.

    `of` traz `co_ibge` e `s_mil` (IVS oficial em milésimos); `adm`, `co_ibge` e
    `s_mil_adm`; `cat`, `co_ibge` e `categoria_ivs_admin`. Município do escore
    administrativo sem IVS oficial conta como divergência. A categoria é
    conferida nos municípios presentes nas duas bases.
    """
    j = adm.merge(of[["co_ibge", "s_mil"]], on="co_ibge", how="left")
    k = cat.merge(of[["co_ibge", "s_mil"]], on="co_ibge", how="inner")
    return {
        "valores_iguais": int((j["s_mil"] == j["s_mil_adm"]).sum()),
        "valores_comparados": int(len(adm)),
        "categorias_iguais": int((k["s_mil"].map(categoria) == k["categoria_ivs_admin"]).sum()),
        "categorias_comparadas": int(len(k)),
    }


def escore_confere(conferencia: dict) -> bool:
    return (conferencia["valores_iguais"] == conferencia["valores_comparados"]
            and conferencia["categorias_iguais"] == conferencia["categorias_comparadas"])


def reproduzir_regra(matriz: pd.DataFrame, of: pd.DataFrame, populacoes: dict = POPULACOES) -> dict:
    """Cobertura do IVS oficial e reprodução da faixa anunciada em cada população.

    `matriz` traz `quadro`, `co_ibge` e `faixa_anunciada`; município sem IVS
    oficial entra em `sem_ivs_oficial` e não em `regra_reproduz`.
    """
    pops = {}
    for nome, quadros in populacoes.items():
        q = matriz[matriz["quadro"].isin(quadros)].drop_duplicates("co_ibge")[["co_ibge", "faixa_anunciada"]]
        q = q.merge(of[["co_ibge", "s_mil"]], on="co_ibge", how="left")
        com = q[q["s_mil"].notna()].copy()
        com["s_mil"] = com["s_mil"].astype(int)
        pops[nome] = {
            "municipios": int(len(q)),
            "com_ivs_oficial": int(len(com)),
            "sem_ivs_oficial": sorted(q.loc[q["s_mil"].isna(), "co_ibge"].tolist()),
            "regra_reproduz": int((com["s_mil"].map(faixa) == com["faixa_anunciada"]).sum()),
        }
    return pops


def decidir_r1(conferencia: dict, pops: dict) -> str:
    """APROVADO_SHARP só com escore conferido e P1 e P2 completas e reproduzidas.

    O ciclo 3, prospectivo e congelado, é relatado e não entra na decisão.
    """
    completo = all(pops[p]["com_ivs_oficial"] == pops[p]["municipios"] for p in ("P1", "P2"))
    sharp = all(pops[p]["regra_reproduz"] == pops[p]["com_ivs_oficial"] for p in ("P1", "P2"))
    return "APROVADO_SHARP" if (escore_confere(conferencia) and completo and sharp) else "REPROVADO"


def main() -> None:
    of = pd.read_csv(OFICIAL, dtype={"co_ibge": str})
    of["s_mil"] = milesimos(of["ivs"])
    adm = pd.read_csv(ADMIN, dtype={"co_ibge": str})
    adm["s_mil_adm"] = milesimos(adm["ivs_admin"])
    cat = pd.read_csv(CATEGORIA, dtype={"co_ibge": str})

    conferencia = conferir_escore_administrativo(of, adm, cat)

    local = pd.read_csv(LOCAL, dtype={"cod_ibge6": str})
    lj = local.merge(of[["co_ibge", "ivs", "s_mil"]], left_on="cod_ibge6", right_on="co_ibge")
    lj["local_mil"] = milesimos(lj["ivs_2010"])

    matriz = pd.read_csv(MATRIZ, dtype={"co_ibge": str})
    pops = reproduzir_regra(matriz, of)

    valido = escore_confere(conferencia)
    decisao = decidir_r1(conferencia, pops)

    if valido:
        saida = of[["co_ibge"]].copy()
        saida["ivs_admin"] = of["s_mil"] / 1000
        saida.to_csv(OUT_ESCORE, index=False, float_format="%.3f")

    resultado = {
        "status": "PORTAO_CAUSAL",
        "portao": "R1",
        "data_execucao": "2026-10-14",
        "outcomes_abertos": False,
        "decisao_r1": decisao,
        "escore_administrativo_e_ivs_2010_oficial": {
            "valores_iguais_3_casas": f"{conferencia['valores_iguais']}/{conferencia['valores_comparados']}",
            "categorias_iguais": f"{conferencia['categorias_iguais']}/{conferencia['categorias_comparadas']}",
        },
        "populacoes": pops,
        "arquivo_local_ivs_2010": {
            "arquivo": str(LOCAL.relative_to(ROOT)),
            "correlacao_com_oficial": round(float(lj[["ivs_2010", "ivs"]].corr().iloc[0, 1]), 3),
            "pct_iguais_3_casas": round(100 * float((lj["local_mil"] == lj["s_mil"]).mean()), 1),
            "leitura": "não é o IVS do município: é, em cada município, a última linha de subgrupo com IVS preenchido da mesma base (sobretudo mulheres negras urbanas) (output/rdd_bolsa/identificacao_arquivo_local_ivs.json); ver docs/auditorias/16_ivs_2010_oficial_e_arquivo_local.md",
        },
        "running_variable": "IVS 2010 oficial do Ipea (= escore administrativo do MS); cortes 0,300 e 0,400",
        "saida_escore_completo": str(OUT_ESCORE.relative_to(ROOT)) if valido else None,
        "fontes": {str(p.relative_to(ROOT)): sha256(p) for p in (OFICIAL, ADMIN, CATEGORIA, MATRIZ, LOCAL)},
    }
    OUT_JSON.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: resultado[k] for k in ("decisao_r1", "escore_administrativo_e_ivs_2010_oficial")},
                     ensure_ascii=False))
    for p, v in pops.items():
        print(p, v["municipios"], v["com_ivs_oficial"], v["regra_reproduz"], v["sem_ivs_oficial"])


if __name__ == "__main__":
    main()
