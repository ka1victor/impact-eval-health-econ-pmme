"""Reconstrói como foi gerado o arquivo local de IVS a partir da base oficial do Ipea.

A base completa da Plataforma IVS tem, para cada município e ano, uma linha
por combinação de cor (Total, Branco, Negro), sexo (Total, Homem, Mulher) e
situação de domicílio (Total, Urbano, Rural). O IVS do município é a linha
"Total/Total/Total". Linhas de subgrupos pequenos podem vir sem valor.

O script testa mecanismos de extração contra `data/ivs_ipea_2010_municipios.csv`
em todas as colunas e em todos os municípios. Uma coluna sem valor na base
conta como divergência; nada é descartado da comparação. Grava o mecanismo que
reproduz o arquivo e qual linha ele pegou em cada município.

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
TOL = {"populacao": 0.5, "renda_per_capita": 0.005}  # demais: 0,0005 (3 casas)
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


def ler_linhas_municipais_2010() -> pd.DataFrame:
    """Todas as linhas municipais de 2010, na ordem da planilha (coluna id)."""
    wb = openpyxl.load_workbook(XLSX, read_only=True)
    linhas = wb["Dados brutos IVS"].iter_rows(values_only=True)
    cab = list(next(linhas))
    ix = {c: i for i, c in enumerate(cab)}
    regs = []
    for r in linhas:
        if r[ix["ano"]] != "2010" or r[ix["nivel"]] != "regiao,uf,rm,municipio":
            continue
        reg = {
            "id": int(r[ix["id"]]),
            "co_ibge": str(r[ix["municipio_6digt"]]).strip()[:6],
            "cor": str(r[ix["label_cor"]]),
            "sexo": str(r[ix["label_sexo"]]),
            "situacao": str(r[ix["label_sit_dom"]]),
        }
        for c in PARES.values():
            reg[c] = numero(r[ix[c]])
        regs.append(reg)
    wb.close()
    base = pd.DataFrame(regs).sort_values("id").reset_index(drop=True)
    base["linha"] = base["cor"] + " / " + base["sexo"] + " / " + base["situacao"]
    return base


def ultima_linha_preenchida(base: pd.DataFrame) -> pd.DataFrame:
    """Mecanismo testado: por município, a última linha com IVS preenchido.

    `base` vem na ordem da planilha (coluna `id`), como em
    `ler_linhas_municipais_2010`. Não filtra cor, sexo nem situação = Total.
    """
    return base.dropna(subset=["ivs"]).drop_duplicates("co_ibge", keep="last")


def ultima_linha(base: pd.DataFrame) -> pd.DataFrame:
    """Alternativa: por município, a última linha, mesmo com IVS vazio."""
    return base.drop_duplicates("co_ibge", keep="last")


def linha_total(base: pd.DataFrame) -> pd.DataFrame:
    """Alternativa: a linha Total / Total / Total, que é o IVS do município."""
    return base[base["linha"].str.count("Total") == 3]


def conferir(local: pd.DataFrame, candidato: pd.DataFrame) -> dict:
    """Compara coluna a coluna em todos os municípios do arquivo local; vazio conta como divergência."""
    j = local.merge(candidato, left_on="cod_ibge6", right_on="co_ibge", how="left")
    res = {"municipios": int(len(j))}
    for col_local, col_of in PARES.items():
        a = pd.to_numeric(j[col_local], errors="coerce")
        b = j[col_of]
        iguais = (a - b).abs() <= TOL.get(col_of, 0.0005)
        res[col_local] = {"iguais": int(iguais.sum()), "base_vazia": int(b.isna().sum())}
    return res


def main() -> None:
    local = pd.read_csv(LOCAL, dtype={"cod_ibge6": str})
    base = ler_linhas_municipais_2010()

    # Mecanismo testado: para cada município, a última linha (na ordem da planilha) com IVS preenchido.
    ultima_preenchida = ultima_linha_preenchida(base)
    mecanismo = conferir(local, ultima_preenchida)
    reproduz_tudo = all(mecanismo[c]["iguais"] == len(local) for c in PARES)
    escolhidas = ultima_preenchida.set_index("co_ibge").loc[local["cod_ibge6"], "linha"]

    # Alternativas, para registro: última linha sem filtrar vazios; linha Total do município.
    ultima_qualquer = ultima_linha(base)
    total = linha_total(base)

    nmu = base[base["linha"] == "Negro / Mulher / Urbano"]
    soma_total = float(total["populacao"].sum())

    resultado = {
        "data_execucao": "2026-10-14",
        "pergunta": "como data/ivs_ipea_2010_municipios.csv foi gerado a partir da base oficial do Ipea?",
        "mecanismo": {
            "descricao": ("para cada município, a última linha de 2010 na ordem da planilha cujo IVS está "
                          "preenchido, sem filtrar cor, sexo e situação de domicílio = Total"),
            "reproduz_o_arquivo_inteiro": reproduz_tudo,
            "conferencia_por_coluna": mecanismo,
            "linha_escolhida_por_municipio": {k: int(v) for k, v in escolhidas.value_counts().items()},
        },
        "alternativas": {
            "ultima_linha_sem_filtrar_vazios": conferir(local, ultima_qualquer),
            "linha_total_do_municipio": conferir(local, total),
        },
        "linha_negro_mulher_urbano": {
            "municipios_com_a_linha": int(nmu["co_ibge"].nunique()),
            "municipios_com_ivs_vazio_nessa_linha": int(nmu["ivs"].isna().sum()),
            "municipios_sem_a_linha": int(local["cod_ibge6"].nunique() - nmu["co_ibge"].nunique()),
        },
        "populacao": {
            "soma_arquivo_local": int(pd.to_numeric(local["populacao_2010"], errors="coerce").sum()),
            "soma_linha_total_da_base": int(soma_total),
            "censo_2010_brasil": CENSO_2010_BRASIL,
            "linha_total_igual_ao_censo": int(soma_total) == CENSO_2010_BRASIL,
        },
        "fontes": {str(XLSX.relative_to(ROOT)): sha256(XLSX), str(LOCAL.relative_to(ROOT)): sha256(LOCAL)},
    }
    OUT.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: resultado[k] for k in ("mecanismo", "linha_negro_mulher_urbano", "populacao")},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
