"""a12b_safra_v2_sia.py — segunda safra (v2) do SIA nos meses 202509–202607, com a lógica do a12.

Adendo §12.1 do protocolo 47 (``docs/06_execucao/47_protocolo_producao_especializada.md``):
o DATASUS revisou as AIH de 202509 a 202607 entre extrações feitas no mesmo dia
(``docs/auditorias/aquisicao/A15_sih_residencia.md``, §5). O SIA pode ter sido
revisto na mesma janela. A extração do a12 (``output/aquisicao/sia/``) continua
sendo a principal; esta safra datada é a sensibilidade. Este script só adquire,
valida e compara: não lê IVS, não calcula nada por faixa, lado de corte, bolsa,
tratamento ou chegada e não estima nada.

Embrulho fino: importa ``a12_adquirir_sia_tabnet.py`` e redireciona os caminhos do
módulo para ``output/aquisicao/sia_v2/``. Consultas, leitor, conjuntos de CBO,
validações V1–V7, regras de zero e ausência e esquema do painel são os do a12,
sem cópia. O a12 não muda: rodado sozinho, continua gravando em
``output/aquisicao/sia/`` com os 55 meses.

Duas adaptações, fixadas antes de baixar a v2:
- meses: só 202509–202607 (onde a revisão é plausível); nada >= 202609;
- conferência célula a célula de AC e RR (V5 do a12): o mês fixado no a12 (202506)
  fica fora da janela; na v2 ela usa o primeiro mês da janela, 202509.

Depois da consolidação, compara a v2 com a v1 célula a célula (município × mês ×
subgrupo × conjunto de CBO) e resume as revisões por mês × conjunto, por UF × mês ×
conjunto e por subgrupo × mês × conjunto.

Modos (``--etapa``): ``verificar`` (padrão, usado pelo ``run_all.py``) confere as
saídas da v2 contra o manifesto, sem rede e sem gravar; ``baixar`` grava as
respostas brutas no cache da v2 (fora do Git); ``consolidar`` valida, grava e
compara; ``tudo`` faz os dois.

Saídas (``output/aquisicao/sia_v2/``): as do a12 com os mesmos nomes e colunas,
restritas aos 11 meses, e mais ``comparacao_v2_v1_mes_conjunto.csv``,
``comparacao_v2_v1_uf_mes_conjunto.csv``, ``comparacao_v2_v1_subgrupo_mes_conjunto.csv``,
``comparacao_v2_v1_celulas_diferentes.parquet`` e ``comparacao_v2_v1_resumo.json``;
``brutos/`` fica fora do Git.
"""

from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[2]
A12_FILE = Path(__file__).resolve().parent / "a12_adquirir_sia_tabnet.py"
_SPEC = importlib.util.spec_from_file_location("a12_adquirir_sia_tabnet", A12_FILE)
a12 = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(a12)

SAFRA = "v2"
PRIMEIRA_V2 = "202509"
ULTIMA_V2 = "202607"
COMPETENCIAS_V2 = [c for c in a12.COMPETENCIAS if PRIMEIRA_V2 <= c <= ULTIMA_V2]
assert len(COMPETENCIAS_V2) == 11 and all(c < a12.LIMITE_EXCLUSIVO for c in COMPETENCIAS_V2)
MES_CONFERENCIA_UF_V2 = PRIMEIRA_V2

V1_DIR = ROOT / "output" / "aquisicao" / "sia"
V1_PAINEL = V1_DIR / "painel_sia_municipio_mes_subgrupo_cbo.parquet"
V1_MANIFESTO = V1_DIR / "manifesto_sia.json"
OUT_DIR = ROOT / "output" / "aquisicao" / "sia_v2"
COMP_MES_FILE = OUT_DIR / "comparacao_v2_v1_mes_conjunto.csv"
COMP_UF_FILE = OUT_DIR / "comparacao_v2_v1_uf_mes_conjunto.csv"
COMP_SUB_FILE = OUT_DIR / "comparacao_v2_v1_subgrupo_mes_conjunto.csv"
COMP_CEL_FILE = OUT_DIR / "comparacao_v2_v1_celulas_diferentes.parquet"
COMP_RESUMO_FILE = OUT_DIR / "comparacao_v2_v1_resumo.json"
CHAVE = ["co_ibge", "competencia_processamento", "subgrupo", "conjunto_cbo"]


def redirecionar() -> None:
    """Aponta os caminhos e o plano de meses do módulo a12 para a safra v2 (nada do a12 é reescrito)."""
    a12.OUT_DIR = OUT_DIR
    a12.CACHE_DIR = OUT_DIR / "brutos"
    a12.PAINEL_FILE = OUT_DIR / "painel_sia_municipio_mes_subgrupo_cbo.parquet"
    a12.IGNORADOS_FILE = OUT_DIR / "sia_municipio_ignorado_mes_subgrupo_cbo.parquet"
    a12.UF_FILE = OUT_DIR / "sia_uf_mes_subgrupo_todos.parquet"
    a12.CBO_FILE = OUT_DIR / "sia_nacional_cbo_mes_subgrupo.parquet"
    a12.SUBGRUPOS_FILE = OUT_DIR / "sia_subgrupos_por_consulta.csv"
    a12.COBERTURA_FILE = OUT_DIR / "sia_cobertura_mes.csv"
    a12.CONJUNTOS_FILE = OUT_DIR / "sia_conjuntos_cbo.csv"
    a12.MUNICIPIOS_FILE = OUT_DIR / "sia_municipios_tabnet.csv"
    a12.MANIFESTO_FILE = OUT_DIR / "manifesto_sia.json"
    a12.RESUMO_FILE = OUT_DIR / "a12_resumo.md"
    a12.COMPETENCIAS = list(COMPETENCIAS_V2)
    a12.MES_CONFERENCIA_UF = MES_CONFERENCIA_UF_V2


def _rel(p: Path) -> str:
    return Path(p).resolve().relative_to(ROOT).as_posix()


# ---------------------------------------------------------------- comparação v2 × v1

def _ler_mes(path: Path, comp: str) -> pd.DataFrame:
    t = pq.read_table(path, columns=CHAVE + ["qtd_aprovada", "status"],
                      filters=[("competencia_processamento", "=", comp)])
    df = t.to_pandas()
    for c in CHAVE + ["status"]:
        df[c] = df[c].astype(str)
    return df


def comparar_mes(comp: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Célula a célula num mês: devolve (todas as células com situação, só as diferentes)."""
    v1 = _ler_mes(V1_PAINEL, comp)
    v2 = _ler_mes(a12.PAINEL_FILE, comp)
    if v1.empty:
        raise RuntimeError(f"{comp}: mês ausente do painel v1")
    m = v1.merge(v2, on=CHAVE, how="outer", suffixes=("_v1", "_v2"), indicator=True)
    q1 = m["qtd_aprovada_v1"].astype("float64")
    q2 = m["qtd_aprovada_v2"].astype("float64")
    aus1 = m["status_v1"] == a12.STATUS_AUSENTE
    aus2 = m["status_v2"] == a12.STATUS_AUSENTE
    sit = np.select(
        [m["_merge"] == "left_only", m["_merge"] == "right_only", aus1 & aus2, aus1, aus2, q1 == q2],
        ["subgrupo_so_na_v1", "subgrupo_so_na_v2", "ausente_nas_duas", "ausente_so_na_v1", "ausente_so_na_v2", "igual"],
        default="diferente")
    m["situacao"] = sit
    # subgrupo sem coluna numa safra: sem linha (regra do a12); para a soma, conta como 0 só no relato
    m["q1"] = q1.fillna(0.0)
    m["q2"] = q2.fillna(0.0)
    m.loc[m["situacao"] == "subgrupo_so_na_v1", "q2"] = 0.0
    m.loc[m["situacao"] == "subgrupo_so_na_v2", "q1"] = 0.0
    m["uf"] = m["co_ibge"].str[:2]
    dif = m.loc[~m["situacao"].isin(["igual", "ausente_nas_duas"])
                & ~((m["situacao"].str.startswith("subgrupo_so")) & (m["q1"] == 0) & (m["q2"] == 0))]
    dif = dif[CHAVE + ["qtd_aprovada_v1", "qtd_aprovada_v2", "status_v1", "status_v2", "situacao"]].copy()
    return m, dif


def comparar() -> dict[str, Any]:
    reg_mes, reg_uf, reg_sub, difs = [], [], [], []
    for comp in COMPETENCIAS_V2:
        m, dif = comparar_mes(comp)
        m["difere"] = ~m["situacao"].isin(["igual", "ausente_nas_duas"]) & ~(
            m["situacao"].str.startswith("subgrupo_so") & (m["q1"] == 0) & (m["q2"] == 0))
        for conj, g in m.groupby("conjunto_cbo", sort=True):
            cont = g["situacao"].value_counts()
            reg_mes.append({
                "competencia_processamento": comp, "conjunto_cbo": conj, "celulas": int(len(g)),
                "celulas_iguais": int(cont.get("igual", 0)), "celulas_diferentes": int(g["difere"].sum()),
                "celulas_valor_diferente": int(cont.get("diferente", 0)),
                "celulas_subgrupo_so_na_v1": int(cont.get("subgrupo_so_na_v1", 0)),
                "celulas_subgrupo_so_na_v2": int(cont.get("subgrupo_so_na_v2", 0)),
                "celulas_ausentes_v1": int(cont.get("ausente_so_na_v1", 0) + cont.get("ausente_nas_duas", 0)),
                "celulas_ausentes_v2": int(cont.get("ausente_so_na_v2", 0) + cont.get("ausente_nas_duas", 0)),
                "municipios_com_diferenca": int(g.loc[g["difere"], "co_ibge"].nunique()),
                "qtd_v1": int(g["q1"].sum()), "qtd_v2": int(g["q2"].sum()),
                "dif_qtd": int(g["q2"].sum() - g["q1"].sum()),
                "dif_relativa": round(float((g["q2"].sum() - g["q1"].sum()) / g["q1"].sum()), 6) if g["q1"].sum() else None,
                "soma_abs_dif_celulas": int((g["q2"] - g["q1"]).abs().sum()),
            })
        u = m.groupby(["uf", "conjunto_cbo"], sort=True).agg(
            celulas_diferentes=("difere", "sum"), qtd_v1=("q1", "sum"), qtd_v2=("q2", "sum")).reset_index()
        u["competencia_processamento"] = comp
        reg_uf.append(u)
        s = m.groupby(["subgrupo", "conjunto_cbo"], sort=True).agg(
            celulas_diferentes=("difere", "sum"), qtd_v1=("q1", "sum"), qtd_v2=("q2", "sum")).reset_index()
        s["competencia_processamento"] = comp
        reg_sub.append(s)
        difs.append(dif)
        a12.log(f"{comp}: {int(m['difere'].sum()):,} células diferentes entre v1 e v2")
    tab_mes = pd.DataFrame(reg_mes)
    tab_mes["mes_conjunto_revisado"] = tab_mes["celulas_diferentes"] > 0
    tab_mes["natureza_dos_dados"] = "EMPIRICO"

    def fechar(df: pd.DataFrame, chave: list[str]) -> pd.DataFrame:
        df = pd.concat(df, ignore_index=True)
        df["dif_qtd"] = df["qtd_v2"] - df["qtd_v1"]
        for c in ("celulas_diferentes", "qtd_v1", "qtd_v2", "dif_qtd"):
            df[c] = df[c].astype("int64")
        df["natureza_dos_dados"] = "EMPIRICO"
        return df[["competencia_processamento"] + chave + ["celulas_diferentes", "qtd_v1", "qtd_v2", "dif_qtd",
                                                           "natureza_dos_dados"]]
    tab_uf = fechar(reg_uf, ["uf", "conjunto_cbo"])
    tab_sub = fechar(reg_sub, ["subgrupo", "conjunto_cbo"])
    cel = pd.concat(difs, ignore_index=True)
    for c in ("qtd_aprovada_v1", "qtd_aprovada_v2"):
        cel[c] = cel[c].astype("Int64")
    cel["natureza_dos_dados"] = "EMPIRICO"
    cel = cel.sort_values(CHAVE, kind="mergesort").reset_index(drop=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tab_mes.to_csv(COMP_MES_FILE, index=False, lineterminator="\n")
    tab_uf.to_csv(COMP_UF_FILE, index=False, lineterminator="\n")
    tab_sub.to_csv(COMP_SUB_FILE, index=False, lineterminator="\n")
    cel.to_parquet(COMP_CEL_FILE, index=False, compression="zstd")

    man1 = json.loads(V1_MANIFESTO.read_text(encoding="utf-8"))
    man2 = json.loads(a12.MANIFESTO_FILE.read_text(encoding="utf-8"))
    hora1 = sorted(q["data_hora_utc"] for q in man1["consultas"]["lista"]
                   if q["competencia"] in COMPETENCIAS_V2 and q.get("data_hora_utc"))
    meses_rev = sorted(tab_mes.loc[tab_mes["mes_conjunto_revisado"], "competencia_processamento"].unique().tolist())
    resumo = {
        "gerador": "scripts/aquisicao/a12b_safra_v2_sia.py",
        "protocolo": "docs/06_execucao/47_protocolo_producao_especializada.md (adendo §12.1)",
        "estatuto": "PROTOCOLO_47_ADENDO_12_POS_RESULTADO",
        "natureza_dos_dados": "EMPIRICO",
        "data_execucao": dt.date.today().isoformat(),
        "meses": COMPETENCIAS_V2,
        "safra_v1": {"diretorio": _rel(V1_DIR), "painel_sha256": a12.sha256_arquivo(V1_PAINEL),
                     "manifesto_sha256": a12.sha256_arquivo(V1_MANIFESTO),
                     "consultas_dos_meses_primeira_utc": hora1[0] if hora1 else None,
                     "consultas_dos_meses_ultima_utc": hora1[-1] if hora1 else None},
        "safra_v2": {"diretorio": _rel(OUT_DIR), "painel_sha256": a12.sha256_arquivo(a12.PAINEL_FILE),
                     "consultas_primeira_utc": man2["consultas"]["primeira_utc"],
                     "consultas_ultima_utc": man2["consultas"]["ultima_utc"]},
        "unidade_da_comparacao": "célula município × mês de processamento × subgrupo × conjunto de CBO do painel",
        "regra_situacao": {
            "igual": "mesma quantidade (inclui zero_tabnet nas duas)",
            "diferente": "quantidade diferente nas duas safras",
            "subgrupo_so_na_v1 / subgrupo_so_na_v2": "o subgrupo é coluna da resposta numa safra e não na outra (sem linha, regra do a12); só conta como diferença se a quantidade da safra que tem a linha for > 0",
            "ausente_*": "município ausente da resposta numa safra (qtd nula, nunca zero)",
        },
        "meses_com_revisao": meses_rev,
        "meses_sem_revisao": [c for c in COMPETENCIAS_V2 if c not in meses_rev],
        "celulas_comparadas": int(tab_mes["celulas"].sum()),
        "celulas_diferentes": int(tab_mes["celulas_diferentes"].sum()),
        "por_mes_conjunto": tab_mes.drop(columns=["natureza_dos_dados"]).to_dict(orient="records"),
        "saidas": {_rel(p): {"sha256": a12.sha256_arquivo(p)} for p in (COMP_MES_FILE, COMP_UF_FILE, COMP_SUB_FILE,
                                                                        COMP_CEL_FILE)},
        "cegamento": "nada por IVS, faixa da bolsa, lado de corte, tratamento ou chegada; o IVS não é lido",
    }
    COMP_RESUMO_FILE.write_text(json.dumps(resumo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return resumo


def anotar_manifesto_e_resumo(resumo: dict[str, Any]) -> None:
    man = json.loads(a12.MANIFESTO_FILE.read_text(encoding="utf-8"))
    man["estatuto"] = "PROTOCOLO_47_ADENDO_12_POS_RESULTADO"
    man["safra"] = {
        "versao": SAFRA,
        "gerador_da_safra": "scripts/aquisicao/a12b_safra_v2_sia.py (embrulho do a12; caminhos e meses redirecionados)",
        "script_a12_sha256": a12.sha256_arquivo(A12_FILE),
        "protocolo": "docs/06_execucao/47_protocolo_producao_especializada.md (adendo §12.1)",
        "papel": "sensibilidade; a safra v1 (output/aquisicao/sia/, 55 meses) continua sendo a principal",
        "meses": COMPETENCIAS_V2,
        "conferencia_uf_mes": MES_CONFERENCIA_UF_V2,
        "nota_conferencia_uf": "o a12 fixou 202506 para a conferência de AC e RR; fora da janela da v2, ela usa 202509, o primeiro mês da janela (fixado antes de baixar)",
        "extracao_primeira_utc": resumo["safra_v2"]["consultas_primeira_utc"],
        "extracao_ultima_utc": resumo["safra_v2"]["consultas_ultima_utc"],
        "comparacao_com_v1": {_rel(COMP_RESUMO_FILE): {"sha256": a12.sha256_arquivo(COMP_RESUMO_FILE)},
                              **resumo["saidas"]},
        "meses_com_revisao_frente_a_v1": resumo["meses_com_revisao"],
    }
    a12.MANIFESTO_FILE.write_text(json.dumps(man, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    texto = a12.RESUMO_FILE.read_text(encoding="utf-8")
    texto = texto.replace("# A12 — resumo gerado do SIA/SUS (TabNet)", "# A12 safra v2 — resumo gerado do SIA/SUS (TabNet)", 1)
    texto = texto.replace("Gerado por `scripts/aquisicao/a12_adquirir_sia_tabnet.py`",
                          "Gerado por `scripts/aquisicao/a12b_safra_v2_sia.py` (lógica do a12)", 1)
    linhas = ["", "## Safra v2 frente à v1 (adendo §12.1 do protocolo 47)", "",
              f"Consultas da v2 entre {resumo['safra_v2']['consultas_primeira_utc']} e "
              f"{resumo['safra_v2']['consultas_ultima_utc']} (UTC); as da v1 nesses meses entre "
              f"{resumo['safra_v1']['consultas_dos_meses_primeira_utc']} e "
              f"{resumo['safra_v1']['consultas_dos_meses_ultima_utc']}.", "",
              f"Células comparadas: {resumo['celulas_comparadas']}; diferentes: {resumo['celulas_diferentes']}. "
              f"Meses com revisão: {', '.join(resumo['meses_com_revisao']) or 'nenhum'}.", "",
              "| Mês | Conjunto | Células | Diferentes | Municípios com diferença | Qtd v1 | Qtd v2 | Diferença | Relativa |",
              "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for r in resumo["por_mes_conjunto"]:
        rel = f"{r['dif_relativa']:.4%}" if r["dif_relativa"] is not None else ""
        linhas.append(f"| {r['competencia_processamento']} | {r['conjunto_cbo']} | {r['celulas']} | {r['celulas_diferentes']} | "
                      f"{r['municipios_com_diferenca']} | {r['qtd_v1']} | {r['qtd_v2']} | {r['dif_qtd']} | {rel} |")
    a12.RESUMO_FILE.write_text(texto.rstrip("\n") + "\n" + "\n".join(linhas) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- verificação sem rede

def verificar() -> int:
    a12.verificar()
    man = json.loads(a12.MANIFESTO_FILE.read_text(encoding="utf-8"))
    saf = man.get("safra") or {}
    erros = []
    if saf.get("versao") != SAFRA or saf.get("meses") != COMPETENCIAS_V2:
        erros.append("manifesto da v2 sem o bloco 'safra' ou com meses diferentes do plano")
    for rel, info in (saf.get("comparacao_com_v1") or {}).items():
        p = ROOT / rel
        if not p.exists() or a12.sha256_arquivo(p) != info.get("sha256"):
            erros.append(f"comparação ausente ou diferente do manifesto: {rel}")
    if COMP_RESUMO_FILE.exists():
        res = json.loads(COMP_RESUMO_FILE.read_text(encoding="utf-8"))
        if res["safra_v1"]["painel_sha256"] != a12.sha256_arquivo(V1_PAINEL):
            erros.append("o painel da v1 mudou desde a comparação; refaça com --etapa consolidar")
    else:
        erros.append(f"{_rel(COMP_RESUMO_FILE)} ausente")
    if erros:
        for e in erros:
            a12.log(f"VERIFICAÇÃO REPROVADA: {e}")
        raise SystemExit("verificar: safra v2 do SIA não confere; refaça com --etapa consolidar ou tudo")
    a12.log(f"safra v2 do SIA conferida sem rede; meses com revisão frente à v1: {saf['meses_com_revisao_frente_a_v1']}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--etapa", choices=["verificar", "baixar", "consolidar", "tudo"], default="verificar")
    args = ap.parse_args()
    redirecionar()
    if args.etapa == "verificar":
        return verificar()
    if args.etapa in ("baixar", "tudo"):
        t0 = time.time()
        codigo = a12.etapa_baixar(list(COMPETENCIAS_V2), refazer=False)
        a12.log(f"download da v2 em {time.time() - t0:.0f}s")
        if args.etapa == "baixar" or codigo != 0:
            return codigo
    codigo = a12.consolidar(list(COMPETENCIAS_V2))
    if codigo != 0:
        return codigo
    resumo = comparar()
    anotar_manifesto_e_resumo(resumo)
    a12.log(f"comparação v2 × v1: meses com revisão {resumo['meses_com_revisao']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
