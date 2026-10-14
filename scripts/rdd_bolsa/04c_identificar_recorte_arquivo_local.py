"""Identifica de que recorte da base oficial do Ipea vem o arquivo local de IVS.

A base completa da Plataforma IVS tem, para cada município e ano, uma linha
por combinação de cor (Total, Branco, Negro), sexo (Total, Homem, Mulher) e
situação de domicílio (Total, Urbano, Rural). O IVS do município é a linha
"Total/Total/Total". Este script compara `data/ivs_ipea_2010_municipios.csv`
com todos os recortes municipais e grava qual deles o arquivo reproduz.

Não abre outcome. Lê a planilha extraída por
`scripts/aquisicao/a08_adquirir_ivs_2010_oficial.py`.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import openpyxl
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
XLSX = ROOT / "data" / "raw" / "aquisicao" / "ivs_oficial" / "atlasivs_dadosbrutos_pt_v2.xlsx"
LOCAL = ROOT / "data" / "ivs_ipea_2010_municipios.csv"
OUT = ROOT / "output" / "rdd_bolsa" / "identificacao_arquivo_local_ivs.json"

PARES = {  # coluna do arquivo local -> coluna da base oficial
    "ivs_2010": "ivs",
    "ivs_infra_2010": "ivs_infraestrutura_urbana",
    "ivs_ch_2010": "ivs_capital_humano",
    "ivs_rt_2010": "ivs_renda_e_trabalho",
    "idhm_2010": "idhm",
    "populacao_2010": "populacao",
    "rdpc_2010": "renda_per_capita",
}
CENSO_2010_BRASIL = 190_755_799  # IBGE, Censo Demográfico 2010, população residente


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while bloco := f.read(1 << 20):
            h.update(bloco)
    return h.hexdigest()


def numero(v):
    if v is None or v in ("", "-"):
        return np.nan
    if isinstance(v, (int, float)):
        return float(v)
    return float(str(v).replace(",", "."))


def ler_recortes_municipais_2010() -> pd.DataFrame:
    wb = openpyxl.load_workbook(XLSX, read_only=True)
    linhas = wb["Dados brutos IVS"].iter_rows(values_only=True)
    cab = list(next(linhas))
    ix = {c: i for i, c in enumerate(cab)}
    regs = []
    for r in linhas:
        if r[ix["ano"]] != "2010" or r[ix["nivel"]] != "regiao,uf,rm,municipio":
            continue
        reg = {
            "co_ibge": str(r[ix["municipio_6digt"]]).strip()[:6],
            "cor": r[ix["label_cor"]],
            "sexo": r[ix["label_sexo"]],
            "situacao": r[ix["label_sit_dom"]],
        }
        for c in PARES.values():
            reg[c] = numero(r[ix[c]])
        regs.append(reg)
    wb.close()
    return pd.DataFrame(regs)


def comparar(local: pd.DataFrame, recorte: pd.DataFrame) -> dict:
    j = local.merge(recorte, left_on="cod_ibge6", right_on="co_ibge", how="inner")
    res = {"municipios_pareados": int(len(j))}
    for col_local, col_of in PARES.items():
        a = pd.to_numeric(j[col_local], errors="coerce")
        b = j[col_of]
        ok = a.notna() & b.notna()
        if ok.sum() == 0:
            continue
        dif = (a[ok] - b[ok]).abs()
        escala = 1000 if col_of not in ("populacao", "renda_per_capita") else 1
        res[col_local] = {
            "pct_iguais": round(100 * float((np.round(a[ok] * escala) == np.round(b[ok] * escala)).mean()), 1),
            "dif_abs_max": round(float(dif.max()), 4),
            "correlacao": round(float(np.corrcoef(a[ok], b[ok])[0, 1]), 4),
        }
    return res


def main() -> None:
    local = pd.read_csv(LOCAL, dtype={"cod_ibge6": str})
    base = ler_recortes_municipais_2010()

    tabela = []
    for (cor, sexo, sit), g in base.groupby(["cor", "sexo", "situacao"]):
        c = comparar(local, g)
        if "ivs_2010" in c:
            tabela.append({"cor": cor, "sexo": sexo, "situacao": sit, **c})
    tabela.sort(key=lambda r: -r["ivs_2010"]["pct_iguais"])
    melhor = tabela[0]
    total = next(r for r in tabela if all(str(r[k]).startswith("Total") for k in ("cor", "sexo", "situacao")))

    resultado = {
        "data_execucao": "2026-10-14",
        "pergunta": "de que recorte da base oficial do Ipea vem data/ivs_ipea_2010_municipios.csv?",
        "recorte_reproduzido": {k: melhor[k] for k in ("cor", "sexo", "situacao")},
        "comparacao_com_recorte_reproduzido": melhor,
        "comparacao_com_total_do_municipio": total,
        "soma_populacao_arquivo_local": int(pd.to_numeric(local["populacao_2010"], errors="coerce").sum()),
        "populacao_brasil_censo_2010": CENSO_2010_BRASIL,
        "todos_os_recortes": tabela,
        "fontes": {str(XLSX.relative_to(ROOT)): sha256(XLSX), str(LOCAL.relative_to(ROOT)): sha256(LOCAL)},
    }
    OUT.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: resultado[k] for k in ("recorte_reproduzido", "comparacao_com_recorte_reproduzido",
                                                  "comparacao_com_total_do_municipio")}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
