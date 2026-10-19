"""a13b_safra_v2_sih.py — segunda safra (v2) do SIH por local de internação, com a lógica do a13.

Adendo §12.1 do protocolo 47 (``docs/06_execucao/47_protocolo_producao_especializada.md``):
o DATASUS revisou as AIH de 202509 a 202607 entre a extração do a13 e a do a15
(``docs/auditorias/aquisicao/A15_sih_residencia.md``, §5). A versão do a13
(``output/aquisicao/sih/``) continua sendo a principal; esta safra datada é a
sensibilidade. Este script só adquire, valida e compara: não lê IVS, não calcula
nada por faixa, lado de corte, bolsa, tratamento ou chegada e não estima nada.

Embrulho fino: importa ``a13_adquirir_sih_tabnet.py`` e redireciona os caminhos do
módulo para ``output/aquisicao/sih_v2/``. Consultas, leitor, validações (v1–v7),
regras de zero, ausência e UF-mês atípico, esquema do painel e manifesto são os
do a13, sem cópia. O a13 não muda: rodado sozinho, continua gravando em
``output/aquisicao/sih/``. Meses: 202201–202607 (o plano do a13); nada >= 202609.

Depois da consolidação do a13, este script compara a v2 com a v1 versionada:
- UF × mês × grupo: AIH aprovadas, internações e valor total, somando municípios e
  "município ignorado" da UF (a mesma soma que reproduz a linha da UF no TabNet);
  status de cada lado (UF-mês sem dado) e número de municípios com célula diferente;
- mês: total nacional nas duas safras, diferença e sinal de mês revisado.

Modos (``--etapa``): ``verificar`` (padrão, usado pelo ``run_all.py``) confere as
saídas da v2 contra o manifesto, sem rede e sem gravar; ``baixar`` grava as
respostas brutas no cache da v2 (fora do Git); ``consolidar`` valida, grava e
compara; ``tudo`` faz os dois.

Saídas (``output/aquisicao/sih_v2/``): as do a13 com os mesmos nomes e colunas
(``painel_sih_municipio_mes_grupo.parquet``, ``painel_sih_municipio_mes_carater_g04.parquet``,
``ignorados_sih_uf_mes_grupo.parquet``, ``a13_validacoes.json``, ``a13_resumo.md``,
``manifesto_sih.json``) e mais ``comparacao_v2_v1_uf_mes_grupo.csv``,
``comparacao_v2_v1_mes.csv`` e ``comparacao_v2_v1_resumo.json``; ``cache_tabnet/``
fica fora do Git.
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

ROOT = Path(__file__).resolve().parents[2]
A13_FILE = Path(__file__).resolve().parent / "a13_adquirir_sih_tabnet.py"
_SPEC = importlib.util.spec_from_file_location("a13_adquirir_sih_tabnet", A13_FILE)
a13 = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(a13)

SAFRA = "v2"
V1_DIR = ROOT / "output" / "aquisicao" / "sih"
V1_PAINEL = V1_DIR / "painel_sih_municipio_mes_grupo.parquet"
V1_IGNORADOS = V1_DIR / "ignorados_sih_uf_mes_grupo.parquet"
V1_MANIFESTO = V1_DIR / "manifesto_sih.json"
A15_VALIDACOES = ROOT / "output" / "aquisicao" / "sih_residencia" / "a15_validacoes.json"

OUT_DIR = ROOT / "output" / "aquisicao" / "sih_v2"
COMP_UF_FILE = OUT_DIR / "comparacao_v2_v1_uf_mes_grupo.csv"
COMP_MES_FILE = OUT_DIR / "comparacao_v2_v1_mes.csv"
COMP_RESUMO_FILE = OUT_DIR / "comparacao_v2_v1_resumo.json"
# Meses em que a revisão é plausível (A15 §5): só para leitura do relato; a comparação cobre os 55 meses.
MESES_REVISAO_A15 = [c for c in a13.COMPETENCIAS if "202509" <= c <= "202607"]
# Tolerância do valor total (R$): o a13 soma células arredondadas a centavos.
TOL_VALOR = 0.011


def redirecionar() -> None:
    """Aponta os caminhos do módulo a13 para a pasta da safra v2 (nada do a13 é reescrito)."""
    a13.OUT_DIR = OUT_DIR
    a13.CACHE_DIR = OUT_DIR / "cache_tabnet"
    a13.FORM_FILE = a13.CACHE_DIR / "formulario_qibr.html"
    a13.FORM_META = a13.CACHE_DIR / "formulario_qibr.json"
    a13.PAINEL_FILE = OUT_DIR / "painel_sih_municipio_mes_grupo.parquet"
    a13.CARATER_FILE = OUT_DIR / "painel_sih_municipio_mes_carater_g04.parquet"
    a13.IGNORADOS_FILE = OUT_DIR / "ignorados_sih_uf_mes_grupo.parquet"
    a13.VALIDACOES_FILE = OUT_DIR / "a13_validacoes.json"
    a13.RESUMO_FILE = OUT_DIR / "a13_resumo.md"
    a13.MANIFESTO_FILE = OUT_DIR / "manifesto_sih.json"


def _rel(p: Path) -> str:
    return Path(p).resolve().relative_to(ROOT).as_posix()


# ---------------------------------------------------------------- comparação v2 × v1

def _por_uf(painel: pd.DataFrame, ign: pd.DataFrame) -> pd.DataFrame:
    """Soma por UF × mês × grupo (municípios + ignorado da UF); UF-mês ausente fica marcado, nunca zero."""
    p = painel[["uf", "competencia", "grupo", "aih_aprovadas", "internacoes", "valor_total", "status"]]
    i = ign.loc[ign["uf"] != "00", ["uf", "competencia", "grupo", "aih_aprovadas", "internacoes", "valor_total", "status"]]
    x = pd.concat([p, i], ignore_index=True)
    x["ausente"] = x["status"] == "ausente_uf_mes_sem_dado"
    g = x.groupby(["uf", "competencia", "grupo"], observed=True)
    out = g.agg(aih=("aih_aprovadas", lambda s: s.astype("float64").sum(min_count=1)),
                internacoes=("internacoes", lambda s: s.astype("float64").sum(min_count=1)),
                valor=("valor_total", lambda s: s.sum(min_count=1)),
                ausente=("ausente", "any")).reset_index()
    out.loc[out["ausente"], ["aih", "internacoes", "valor"]] = np.nan
    return out


def comparar() -> dict[str, Any]:
    """Compara a v2 (recém-gravada) com a v1 versionada. Só agregados por UF e nacionais saem daqui."""
    cols = ["co_ibge", "uf", "competencia", "grupo", "aih_aprovadas", "internacoes", "valor_total", "status"]
    v1 = pd.read_parquet(V1_PAINEL, columns=cols)
    v2 = pd.read_parquet(a13.PAINEL_FILE, columns=cols)
    i1 = pd.read_parquet(V1_IGNORADOS)
    i2 = pd.read_parquet(a13.IGNORADOS_FILE)
    u1, u2 = _por_uf(v1, i1), _por_uf(v2, i2)
    m = u1.merge(u2, on=["uf", "competencia", "grupo"], how="outer", suffixes=("_v1", "_v2"), indicator=True)
    m["grupo_so_em_uma_safra"] = m["_merge"] != "both"
    # grupo sem linha numa safra (coluna nunca devolvida no período) é zero por construção do a13 (coluna omitida)
    for k in ("aih", "internacoes", "valor"):
        for s in ("v1", "v2"):
            sem = m["_merge"] == ("right_only" if s == "v1" else "left_only")
            m.loc[sem, f"{k}_{s}"] = 0.0
    m["ausente_v1"] = m["ausente_v1"].fillna(False).astype(bool)
    m["ausente_v2"] = m["ausente_v2"].fillna(False).astype(bool)
    for k in ("aih", "internacoes", "valor"):
        m[f"dif_{k}"] = m[f"{k}_v2"] - m[f"{k}_v1"]
    # municípios com célula diferente (AIH), por UF × mês × grupo
    j = v1.merge(v2, on=["co_ibge", "competencia", "grupo"], how="outer", suffixes=("_v1", "_v2"))
    j["uf"] = j["co_ibge"].str[:2]
    a1 = j["aih_aprovadas_v1"].astype("float64")
    a2 = j["aih_aprovadas_v2"].astype("float64")
    j["difere"] = ~((a1 == a2) | (a1.isna() & a2.isna()))
    nmun = j.groupby(["uf", "competencia", "grupo"])["difere"].sum().rename("municipios_com_aih_diferente").reset_index()
    m = m.merge(nmun, on=["uf", "competencia", "grupo"], how="left")
    m["municipios_com_aih_diferente"] = m["municipios_com_aih_diferente"].fillna(0).astype(int)

    def situacao(r) -> str:
        if r["ausente_v1"] or r["ausente_v2"]:
            if r["ausente_v1"] and r["ausente_v2"]:
                return "ausente_nas_duas"
            return "ausente_so_na_v1" if r["ausente_v1"] else "ausente_so_na_v2"
        igual = (r["dif_aih"] == 0 and r["dif_internacoes"] == 0 and abs(r["dif_valor"]) <= TOL_VALOR * max(1, r["municipios_com_aih_diferente"] + 1)
                 and r["municipios_com_aih_diferente"] == 0)
        return "igual" if igual else "diferente"
    m["situacao"] = m.apply(situacao, axis=1)
    m["uf_sigla"] = m["uf"].map(a13.UF_CODIGO_SIGLA)
    m["natureza_dos_dados"] = "EMPIRICO"
    tab = m[["uf", "uf_sigla", "competencia", "grupo", "aih_v1", "aih_v2", "dif_aih", "internacoes_v1", "internacoes_v2",
             "dif_internacoes", "valor_v1", "valor_v2", "dif_valor", "ausente_v1", "ausente_v2",
             "municipios_com_aih_diferente", "grupo_so_em_uma_safra", "situacao", "natureza_dos_dados"]]
    tab = tab.sort_values(["competencia", "uf", "grupo"], kind="mergesort").reset_index(drop=True)
    for k in ("aih_v1", "aih_v2", "dif_aih", "internacoes_v1", "internacoes_v2", "dif_internacoes"):
        tab[k] = tab[k].astype("Int64")
    for k in ("valor_v1", "valor_v2", "dif_valor"):
        tab[k] = tab[k].round(2)

    # mês: total nacional (municípios + todos os ignorados, inclusive exterior), das validações de cada safra
    val1 = json.loads((V1_DIR / "a13_validacoes.json").read_text(encoding="utf-8"))
    val2 = json.loads(a13.VALIDACOES_FILE.read_text(encoding="utf-8"))
    # total por local de internação consultado pelo a15 (mesmo formulário qibr, ~20h UTC de 19/10/2026)
    val15 = json.loads(A15_VALIDACOES.read_text(encoding="utf-8")) if A15_VALIDACOES.exists() else None
    meses = []
    for c in a13.COMPETENCIAS:
        t1 = val1["por_competencia"][c]["total_aih_por_grupo"]
        t2 = val2["por_competencia"][c]["total_aih_por_grupo"]
        t15 = (val15 or {}).get("por_competencia", {}).get(c, {}).get("total_aih_internacao_contemporaneo")
        parte = tab.loc[tab["competencia"] == c]
        n_dif = int((parte["situacao"] != "igual").sum())
        meses.append({
            "competencia": c, "aih_total_v1": int(t1["total"]), "aih_total_v2": int(t2["total"]),
            "dif_aih_total": int(t2["total"]) - int(t1["total"]),
            "dif_relativa": round((int(t2["total"]) - int(t1["total"])) / int(t1["total"]), 6) if t1["total"] else None,
            "aih_g04_v1": int(t1.get("04", 0)), "aih_g04_v2": int(t2.get("04", 0)),
            "dif_aih_g04": int(t2.get("04", 0)) - int(t1.get("04", 0)),
            "celulas_uf_grupo_diferentes": n_dif,
            "ufs_com_diferenca": ",".join(sorted(parte.loc[parte["situacao"] != "igual", "uf_sigla"].dropna().unique())),
            "municipios_com_aih_diferente": int(parte["municipios_com_aih_diferente"].sum()),
            "mes_revisado": bool(n_dif > 0 or t1 != t2),
            "total_v2_igual_internacao_do_a15": (None if t15 is None else
                                                 {k: int(t15.get(k, 0)) for k in t2} == {k: int(v) for k, v in t2.items()}),
            "natureza_dos_dados": "EMPIRICO",
        })
    tab_mes = pd.DataFrame(meses)
    a13.OUT_DIR.mkdir(parents=True, exist_ok=True)
    tab.to_csv(COMP_UF_FILE, index=False, lineterminator="\n")
    tab_mes.to_csv(COMP_MES_FILE, index=False, lineterminator="\n")
    revisados = tab_mes.loc[tab_mes["mes_revisado"], "competencia"].tolist()
    man1 = json.loads(V1_MANIFESTO.read_text(encoding="utf-8"))
    man2 = json.loads(a13.MANIFESTO_FILE.read_text(encoding="utf-8"))
    hora = lambda man: sorted(q["data_hora_utc"] for q in man["consultas_realizadas"])  # noqa: E731
    resumo = {
        "gerador": "scripts/aquisicao/a13b_safra_v2_sih.py",
        "protocolo": "docs/06_execucao/47_protocolo_producao_especializada.md (adendo §12.1)",
        "estatuto": "PROTOCOLO_47_ADENDO_12_POS_RESULTADO",
        "natureza_dos_dados": "EMPIRICO",
        "data_execucao": dt.date.today().isoformat(),
        "safra_v1": {"diretorio": _rel(V1_DIR), "manifesto_sha256": a13.sha256_arquivo(V1_MANIFESTO),
                     "painel_sha256": a13.sha256_arquivo(V1_PAINEL),
                     "consultas_primeira_utc": hora(man1)[0], "consultas_ultima_utc": hora(man1)[-1]},
        "safra_v2": {"diretorio": _rel(a13.OUT_DIR), "painel_sha256": a13.sha256_arquivo(a13.PAINEL_FILE),
                     "consultas_primeira_utc": hora(man2)[0], "consultas_ultima_utc": hora(man2)[-1]},
        "unidade_da_comparacao": "UF × mês de processamento × grupo (municípios + 'MUNICIPIO IGNORADO' da UF); "
                                 "mês = total nacional das validações (inclui exterior)",
        "regra_situacao": "igual: AIH e internações idênticas, valor dentro do arredondamento e nenhum município com AIH "
                          "diferente; diferente: o resto; ausente_*: UF-mês sem dado numa safra (NaN, nunca zero)",
        "meses_comparados": len(a13.COMPETENCIAS),
        "meses_revisados": revisados,
        "meses_revisados_fora_da_janela_do_a15": [c for c in revisados if c not in MESES_REVISAO_A15],
        "meses_da_janela_do_a15_sem_revisao": [c for c in MESES_REVISAO_A15 if c not in revisados],
        "conferencia_com_a15": {
            "arquivo": _rel(A15_VALIDACOES) if A15_VALIDACOES.exists() else None,
            "sha256": a13.sha256_arquivo(A15_VALIDACOES) if A15_VALIDACOES.exists() else None,
            "descricao": "total nacional por grupo da v2 contra o total por local de internação que o a15 consultou "
                         "no mesmo formulário (qibr) por volta das 20h UTC de 19/10/2026 (validação v8 do a15)",
            "meses_iguais": sum(1 for r in meses if r["total_v2_igual_internacao_do_a15"]),
            "meses_diferentes": [r["competencia"] for r in meses if r["total_v2_igual_internacao_do_a15"] is False],
        },
        "contagem_situacao_uf_mes_grupo":{k: int(v) for k, v in tab["situacao"].value_counts().sort_index().items()},
        "uf_mes_sem_dado": {"v1": man1.get("uf_meses_sem_dado"), "v2": man2.get("uf_meses_sem_dado")},
        "uf_mes_atipico": {"v1": [(r["competencia"], r["sigla"]) for r in man1.get("uf_meses_atipicos", [])],
                           "v2": [(r["competencia"], r["sigla"]) for r in man2.get("uf_meses_atipicos", [])]},
        "por_mes": meses,
        "saidas": {_rel(p): {"sha256": a13.sha256_arquivo(p)} for p in (COMP_UF_FILE, COMP_MES_FILE)},
        "cegamento": "nada por IVS, faixa da bolsa, lado de corte, tratamento ou chegada; o IVS não é lido",
    }
    COMP_RESUMO_FILE.write_text(json.dumps(resumo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return resumo


def anotar_manifesto_e_resumo(resumo: dict[str, Any]) -> None:
    """Marca o manifesto e o resumo gerados pelo a13 como safra v2 e registra a comparação."""
    man = json.loads(a13.MANIFESTO_FILE.read_text(encoding="utf-8"))
    man["safra"] = {
        "versao": SAFRA,
        "gerador_da_safra": "scripts/aquisicao/a13b_safra_v2_sih.py (embrulho do a13; caminhos redirecionados)",
        "script_a13_sha256": a13.sha256_arquivo(A13_FILE),
        "protocolo": "docs/06_execucao/47_protocolo_producao_especializada.md (adendo §12.1)",
        "estatuto": "PROTOCOLO_47_ADENDO_12_POS_RESULTADO",
        "papel": "sensibilidade; a safra v1 (output/aquisicao/sih/) continua sendo a principal",
        "extracao_primeira_utc": resumo["safra_v2"]["consultas_primeira_utc"],
        "extracao_ultima_utc": resumo["safra_v2"]["consultas_ultima_utc"],
        "comparacao_com_v1": {_rel(COMP_RESUMO_FILE): {"sha256": a13.sha256_arquivo(COMP_RESUMO_FILE)},
                              **resumo["saidas"]},
        "meses_revisados_frente_a_v1": resumo["meses_revisados"],
    }
    a13.MANIFESTO_FILE.write_text(json.dumps(man, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    texto = a13.RESUMO_FILE.read_text(encoding="utf-8")
    texto = texto.replace("# A13 — resumo gerado do SIH/SUS (TabNet)",
                          "# A13 safra v2 — resumo gerado do SIH/SUS (TabNet)", 1)
    texto = texto.replace("Gerado por `scripts/aquisicao/a13_adquirir_sih_tabnet.py`",
                          "Gerado por `scripts/aquisicao/a13b_safra_v2_sih.py` (lógica do a13)", 1)
    linhas = ["", "## Safra v2 frente à v1 (adendo §12.1 do protocolo 47)", "",
              f"Consultas da v2 entre {resumo['safra_v2']['consultas_primeira_utc']} e "
              f"{resumo['safra_v2']['consultas_ultima_utc']} (UTC); v1 entre "
              f"{resumo['safra_v1']['consultas_primeira_utc']} e {resumo['safra_v1']['consultas_ultima_utc']}.", "",
              f"Meses revisados: {', '.join(resumo['meses_revisados']) or 'nenhum'}.", "",
              "| Competência | AIH v1 | AIH v2 | Diferença | Relativa | Grupo 04 v1 | Grupo 04 v2 | UF × grupo diferentes | "
              "Municípios com AIH diferente | UFs |",
              "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|"]
    for r in resumo["por_mes"]:
        rel = f"{r['dif_relativa']:.4%}" if r["dif_relativa"] is not None else ""
        linhas.append(f"| {r['competencia']} | {r['aih_total_v1']} | {r['aih_total_v2']} | {r['dif_aih_total']} | {rel} | "
                      f"{r['aih_g04_v1']} | {r['aih_g04_v2']} | {r['celulas_uf_grupo_diferentes']} | "
                      f"{r['municipios_com_aih_diferente']} | {r['ufs_com_diferenca']} |")
    a13.RESUMO_FILE.write_text(texto.rstrip("\n") + "\n" + "\n".join(linhas) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- verificação sem rede

def verificar() -> int:
    a13.verificar_versionado()
    man = json.loads(a13.MANIFESTO_FILE.read_text(encoding="utf-8"))
    erros = []
    saf = man.get("safra") or {}
    if saf.get("versao") != SAFRA:
        erros.append("manifesto da v2 sem o bloco 'safra'")
    for rel, info in (saf.get("comparacao_com_v1") or {}).items():
        p = ROOT / rel
        if not p.exists() or a13.sha256_arquivo(p) != info.get("sha256"):
            erros.append(f"comparação ausente ou diferente do manifesto: {rel}")
    if COMP_RESUMO_FILE.exists():
        res = json.loads(COMP_RESUMO_FILE.read_text(encoding="utf-8"))
        if res["safra_v1"]["painel_sha256"] != a13.sha256_arquivo(V1_PAINEL):
            erros.append("o painel da v1 mudou desde a comparação; refaça a comparação (--etapa consolidar)")
    else:
        erros.append(f"{_rel(COMP_RESUMO_FILE)} ausente")
    if erros:
        for e in erros:
            a13.log(f"VERIFICAÇÃO REPROVADA: {e}")
        raise SystemExit("verificar: safra v2 do SIH não confere; refaça com --etapa consolidar ou tudo")
    a13.log(f"safra v2 do SIH conferida sem rede; meses revisados frente à v1: {len(saf['meses_revisados_frente_a_v1'])}")
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
        r = a13.etapa_baixar(a13.COMPETENCIAS, list(a13.CONSULTAS))
        a13.log(f"Download v2: {r['contagem']}, {len(r['falhas'])} falhas, {time.time() - t0:.0f}s")
        if r["falhas"]:
            for k, e in r["falhas"].items():
                a13.log(f"FALHA {k}: {e}")
            return 3
        if args.etapa == "baixar":
            return 0
    codigo = a13.etapa_consolidar()
    if codigo != 0:
        return codigo
    resumo = comparar()
    anotar_manifesto_e_resumo(resumo)
    a13.log(f"comparação v2 × v1: meses revisados {resumo['meses_revisados']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
