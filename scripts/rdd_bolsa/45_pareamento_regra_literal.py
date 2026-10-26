"""Adendo 48e: pareamento pela regra literal do 48d e PSM em 0,400 sem as categorias de um lado só.

Especificação congelada antes das contas: `docs/06_execucao/48e_adendo_pareamento_regra_literal_e_0400.md`
(26/10/2026, commit f97e1ca). SHA-256 conferido abaixo. Estatuto: `ADENDO_48E_POS_RESULTADO`;
`natureza_dos_dados = EMPIRICO` em toda saída. As decisões de implementação estão na seção 0 do doc 57s, escritas e
versionadas antes de qualquer estimativa (commit d01d873).

Importa o script 44 (adendo 48d) e não o reescreve: bases, covariáveis, janela, escore de propensão, distâncias,
*caliper*, suporte, inferência pareada, IPW, balanço e montagem das linhas são as funções do 44. Este script muda só:
- a regra 2 do 48e: antes do logit, saem as unidades das categorias de macrorregião ou de capital que, na janela,
  só aparecem de um lado do corte (quem sai é listado em `PM_excluidos.csv`);
- a regra 1 do 48e: o lado com menos unidades procura par, uma unidade por vez (PSM em ordem decrescente do escore;
  Mahalanobis em ordem do código IBGE e do ciclo), no lugar do guloso global do 44. A troca é feita só no último
  passo (`guloso_global` do 44), durante a chamada, e desfeita depois.

O que faz, na ordem
-------------------
1. Confere o SHA-256 do adendo 48e e guarda o SHA-256 das saídas `CL_*`, `HI_*` e `OC_*` (não são regravadas).
2. Portão: refaz, com as funções do 44 sem troca, o PS-1 e o PS-2 do 48d em 0,300 (regra gulosa, sem a regra 2) e
   compara com `CL_estimativas.csv` (<= 1e-8) e com os pares de `CL_resumo.json` (86 na H1; 88 no ΔB1). Se falhar,
   para sem gravar nada.
3. PM-1 e PM-2 (principais; Holm entre as oito), PM-3 a PM-7 (BKY) e PM-F (só para a figura).
4. Leitura do §3 do adendo pelas regras fixadas (decisões 20 a 24 do 57s), figuras com "Como ler" e blocos do doc
   57s (`--atualizar-doc`).

Integridade: o arquivo local de IVS da auditoria 16 não é lido (running variable = IVS 2010 oficial, a08); nenhuma
competência do CNES >= 202609 (conferências do 44 e do 43); nada é escrito em `data/`.

Uso
---
    python3 scripts/rdd_bolsa/45_pareamento_regra_literal.py                 # estima e grava PM_*
    python3 scripts/rdd_bolsa/45_pareamento_regra_literal.py --atualizar-doc # idem e regrava os blocos do 57s
    python3 scripts/rdd_bolsa/45_pareamento_regra_literal.py --so-doc        # só regrava os blocos do 57s
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from contextlib import contextmanager
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DIR_RDD = ROOT / "scripts" / "rdd_bolsa"


def _importar(caminho: Path, nome: str):
    if nome in sys.modules:
        return sys.modules[nome]
    bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec = importlib.util.spec_from_file_location(nome, caminho)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[nome] = mod
        spec.loader.exec_module(mod)
    finally:
        sys.dont_write_bytecode = bytecode
    return mod


CL = _importar(DIR_RDD / "44_controles_localizacao_medicos.py", "controles_localizacao_medicos_para_pm")
L = CL.L

# ---------------------------------------------------------------------------
# Parâmetros do adendo
# ---------------------------------------------------------------------------

OUT = CL.OUT
ADENDO = ROOT / "docs" / "06_execucao" / "48e_adendo_pareamento_regra_literal_e_0400.md"
DOC = ROOT / "docs" / "06_execucao" / "57s_resultados_pareamento_regra_literal.md"
CL_EST = OUT / CL.NOME_EST
CL_RES = OUT / CL.NOME_RESUMO

NOME_EST = "PM_estimativas.csv"
NOME_BAL = "PM_balanco.csv"
NOME_EXC = "PM_excluidos.csv"
NOME_RESUMO = "PM_resumo.json"
DIR_FIG = OUT / "PM_figuras"

DATA_EXECUCAO = "2026-10-26"
ESTATUTO = "ADENDO_48E_POS_RESULTADO"
NATUREZA = "EMPIRICO"
COMMIT_CONGELAMENTO = "f97e1ca"
COMMIT_DECISOES = "d01d873"
SHA_ADENDO = "35cb89833934332b7cdbdc22eb3561cfe0beac9da4e2106ad3a2d9defd86ed8b"
CORTES = CL.CORTES
JANELA_PAR = CL.JANELA_PAR                 # 0,050
JANELA_SENS = CL.JANELA_SENS               # 0,020
TOL_PORTAO = 1e-8
PARES_48D = {"H1": 86, "dB1": 88}          # contagem de pares do 48d em 0,300 (§4 do adendo)
LIMIAR_SAIDA = 0.25                        # 3ª linha do §3: a regra 2 tira mais de 25% de um lado
ALFA = CL.ALFA
PROTEGIDOS = ("CL_", "HI_", "OC_")
TXT_CORTE = CL.TXT_CORTE
ROT_CORTE = CL.ROT_CORTE
BOLSA = CL.BOLSA

OUT_H1 = CL.OUT_PAR_H1                     # H1M-FRAC, H1M-ALOC (decisão 10 do 57r)
OUT_OC = {k: {"desc": CL._desc_oc(k), "unidade": CL.UN_OC, "col": k} for k in CL.OUT_OC}
OUT_OC_PRINC = {k: OUT_OC[k] for k in ("dB1", "dB2")}
OUT_OC_SEC = {k: OUT_OC[k] for k in ("dB3", "dB4", "dB5")}
PRINCIPAIS = ("PM-1", "PM-2")
BKY = ("PM-3", "PM-4", "PM-5", "PM-6", "PM-7")

PAPEL = {"PM-1": "principal", "PM-2": "principal", "PM-3": "sensibilidade", "PM-4": "sensibilidade",
         "PM-5": "sensibilidade", "PM-6": "sensibilidade", "PM-7": "secundaria", "PM-F": "figura"}
DESC_BLOCO = {
    "PM-1": "H1 por PSM, regra literal, com a regra 2, janela 0,050",
    "PM-2": "oferta local (ΔB1, ΔB2) por PSM, regra literal, com a regra 2, janela 0,050",
    "PM-3": "PM-1 e PM-2 com a regra gulosa global do 48d, com a regra 2",
    "PM-4": "PM-1 e PM-2 na janela 0,020 (regra literal, regra 2 refeita na janela)",
    "PM-5": "IPW (escore aparado em [0,05; 0,95]) na amostra da regra 2, janela 0,050",
    "PM-6": "Mahalanobis com a regra literal e o caliper do 48d, com a regra 2, janela 0,050",
    "PM-7": "ΔB3–ΔB5 da oferta local por PSM, regra literal, com a regra 2, janela 0,050",
    "PM-F": "PSM pela regra literal sem a regra 2 (só para a figura principal; fora do Holm, do BKY e da leitura)",
}

CONTRASTE = CL.CONTRASTE
COLUNAS = CL.COLUNAS + ["regra_pareamento", "regra2", "saiu_regra2_abaixo", "saiu_regra2_acima",
                        "lado_que_procura"]
COLUNAS_BAL = CL.COLUNAS_BAL + ["regra_pareamento", "regra2"]
COLUNAS_EXC = ["natureza_dos_dados", "estatuto", "parte", "corte", "janela", "id", "co_ibge", "municipio", "uf",
               "ciclo", "lado", "categorias", "capital", "regiao", "ivs_2010_oficial"]


class FalhaValidacao(RuntimeError):
    """Portão ou validação obrigatória falhou: o script para sem gravar."""


sha256 = CL.sha256
rotulo = CL.rotulo
_f = CL._f
_juntar = CL._juntar


# ---------------------------------------------------------------------------
# 1. Dados (funções do 44)
# ---------------------------------------------------------------------------

def hashes_protegidos() -> dict[str, str]:
    """SHA-256 de cada arquivo das saídas CL_*, HI_* e OC_* (inclusive figuras)."""
    out = {}
    for pref in PROTEGIDOS:
        for p in sorted(OUT.glob(pref + "*")):
            arqs = sorted(x for x in p.rglob("*") if x.is_file()) if p.is_dir() else [p]
            for a in arqs:
                out[rotulo(a)] = sha256(a)
    return out


def nomes_municipios() -> pd.DataFrame:
    """Nome e UF do município pela coluna `nome_municipio_uf` do a08 (IVS 2010 oficial), só para listar quem saiu."""
    a08 = pd.read_csv(CL.A08, dtype={"co_ibge": str}, usecols=["co_ibge", "nome_municipio_uf", "ivs"])
    a08["co_ibge"] = CL.K1M._ibge6(a08["co_ibge"])
    m = a08["nome_municipio_uf"].astype(str).str.extract(r"^(?P<municipio>.*) \((?P<uf>[A-Z]{2})\)$")
    if m.isna().any().any():
        raise FalhaValidacao("a08: nome_municipio_uf fora do formato 'Nome (UF)'")
    return pd.concat([a08[["co_ibge", "ivs"]], m], axis=1).set_index("co_ibge")


def carregar() -> dict:
    cov, curso, info_cov = CL.construir_covariaveis()
    CL.UFS = sorted(cov["cd_uf"].unique().tolist())
    b = CL.bases_h1(cov, curso)
    v, info_v, _ = CL.base_v(cov)
    dB, info_oc = CL.construir_delta_b(v)
    vv = v.merge(dB, on="co_ibge", how="left", validate="one_to_one")
    return {"h1": b["par"], "v": vv, "info_v": info_v, "info_oc": info_oc,
            "info_cov": {k: info_cov[k] for k in ("referencia_ibge", "populacao", "regiao_saude", "painel_a09")}}


# ---------------------------------------------------------------------------
# 2. Regra 2: categorias de um lado só (decisões 2 a 6)
# ---------------------------------------------------------------------------

def categorias(d: pd.DataFrame) -> list[tuple[str, np.ndarray]]:
    cats = [("capital", (d["capital"] == 1).to_numpy()), ("nao capital", (d["capital"] == 0).to_numpy())]
    return cats + [(f"regiao[{r}]", (d["regiao"] == r).to_numpy()) for r in CL.REGIOES]


def categorias_um_lado(d: pd.DataFrame) -> list[dict]:
    acima = d["acima"].to_numpy(bool)
    out = []
    for nome, z in categorias(d):
        if z.sum() > 0 and acima[z].min() == acima[z].max():
            out.append({"categoria": nome, "unidades": int(z.sum()), "municipios": int(d.loc[z, "co_ibge"].nunique()),
                        "lado": "acima" if acima[z][0] else "abaixo"})
    return out


def regra2(d: pd.DataFrame) -> tuple[np.ndarray, list[dict], dict[str, list[str]]]:
    """Uma passada (decisão 3): devolve quem fica, as categorias de um lado só e, por unidade que sai, quais."""
    cats = categorias_um_lado(d)
    nomes = {c["categoria"] for c in cats}
    sai = np.zeros(len(d), dtype=bool)
    por_id: dict[str, list[str]] = {}
    for nome, z in categorias(d):
        if nome in nomes:
            sai |= z
            for i in d.loc[z, "id"]:
                por_id.setdefault(i, []).append(nome)
    return ~sai, cats, por_id


def _por_grupo(d: pd.DataFrame, por_ciclo: bool):
    return d.groupby("ciclo") if por_ciclo else [(None, d)]


def lados_que_procuram(d: pd.DataFrame, por_ciclo: bool) -> dict:
    """Decisão 7: por grupo (ciclo na H1), o lado com menos unidades procura; empate, o de cima."""
    out = {}
    for k, g in _por_grupo(d, por_ciclo):
        na, nb = int(g["acima"].sum()), int((~g["acima"]).sum())
        out["todos" if k is None else f"ciclo {int(k)}"] = {"acima": na, "abaixo": nb,
                                                            "procura": "acima" if na <= nb else "abaixo"}
    return out


def amostra(unid: pd.DataFrame, corte: int, janela: int, aplica: bool, nomes: pd.DataFrame, parte: str
            ) -> tuple[pd.DataFrame, dict, list[dict]]:
    """Janela -> sem covariável ausente -> regra 2 (se `aplica`). Devolve a amostra do pareamento, o registro e a
    lista de quem saiu pela regra 2."""
    d = CL._janela(unid, corte, janela)
    comp = CL._completo(d)
    dc = d[comp].copy()
    reg = {"parte": parte, "corte": ROT_CORTE[corte], "janela": janela / 1000, "regra2": bool(aplica),
           "na_janela": {"abaixo": int((~d["acima"]).sum()), "acima": int(d["acima"].sum())},
           "sem_covariavel": {"abaixo": int((~comp & ~d["acima"].to_numpy()).sum()),
                              "acima": int((~comp & d["acima"].to_numpy()).sum())},
           "apos_covariavel": {"abaixo": int((~dc["acima"]).sum()), "acima": int(dc["acima"].sum())}}
    exc = []
    if aplica:
        fica, cats, por_id = regra2(dc)
        d2 = dc[fica].copy()
        sai = dc[~fica]
        reg["categorias_um_lado"] = cats
        reg["saiu_regra2"] = {"abaixo": int((~sai["acima"]).sum()), "acima": int(sai["acima"].sum())}
        reg["fracao_saiu_regra2"] = {
            lado: (reg["saiu_regra2"][lado] / reg["apos_covariavel"][lado] if reg["apos_covariavel"][lado] else 0.0)
            for lado in ("abaixo", "acima")}
        reg["categorias_um_lado_depois"] = categorias_um_lado(d2)
        for _, r in sai.sort_values("id").iterrows():
            nm = nomes.loc[r["co_ibge"]]
            exc.append({"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "parte": parte,
                        "corte": ROT_CORTE[corte], "janela": janela / 1000, "id": r["id"], "co_ibge": r["co_ibge"],
                        "municipio": nm["municipio"], "uf": nm["uf"],
                        "ciclo": int(r["ciclo"]) if "ciclo" in r.index and pd.notna(r.get("ciclo")) else np.nan,
                        "lado": "acima" if r["acima"] else "abaixo", "categorias": ";".join(por_id[r["id"]]),
                        "capital": int(r["capital"]), "regiao": r["regiao"], "ivs_2010_oficial": float(nm["ivs"])})
    else:
        d2 = dc
    reg["amostra_pareamento"] = {"abaixo": int((~d2["acima"]).sum()), "acima": int(d2["acima"].sum())}
    return d2, reg, exc


# ---------------------------------------------------------------------------
# 3. Regra literal (decisões 7 a 10)
# ---------------------------------------------------------------------------

def regra_literal(cand: list[tuple[float, str, str]], acima: dict[str, bool], grupo: dict[str, object],
                  chave: dict[str, tuple]) -> list[tuple[str, str, float]]:
    """1:1 sem reposição: em cada grupo, o lado com menos unidades procura (empate: o de cima), na ordem de `chave`;
    cada unidade fica com a candidata livre mais próxima (empate: menor identificador).

    `cand` traz (distância, id de cima, id de baixo) dos pares admissíveis, como o 44 monta. `acima`, `grupo` e
    `chave` cobrem toda a amostra do pareamento (inclusive quem não tem candidata)."""
    cont: dict[object, list[int]] = {}
    for i, a in acima.items():
        c = cont.setdefault(grupo[i], [0, 0])
        c[0 if a else 1] += 1
    procura_acima = {g: c[0] <= c[1] for g, c in cont.items()}
    viz: dict[str, list[tuple[float, str]]] = {}
    for dist, ia, ib in cand:
        viz.setdefault(ia, []).append((dist, ib))
        viz.setdefault(ib, []).append((dist, ia))
    buscam = sorted((i for i in acima if acima[i] == procura_acima[grupo[i]]), key=lambda i: chave[i])
    usados: set[str] = set()
    pares = []
    for i in buscam:
        livres = sorted((x for x in viz.get(i, []) if x[1] not in usados), key=lambda x: (x[0], x[1]))
        if not livres:
            continue
        dist, j = livres[0]
        usados.update((i, j))
        pares.append((i, j, dist) if acima[i] else (j, i, dist))
    return pares


@contextmanager
def trocar_pareamento(fn):
    """Troca o último passo do pareamento do 44 (`guloso_global`) durante a chamada e o devolve depois."""
    original = CL.guloso_global
    CL.guloso_global = fn
    try:
        yield
    finally:
        CL.guloso_global = original


def funcao_literal(d: pd.DataFrame, metodo: str, por_ciclo: bool):
    ids = d["id"].tolist()
    acima = dict(zip(ids, d["acima"].astype(bool)))
    grupo = dict(zip(ids, d["ciclo"])) if por_ciclo else {i: None for i in ids}
    if metodo == "PSM":
        lp, _ = CL.escore_propensao(d)
        if lp is None:
            return None
        chave = {i: (-float(x), i) for i, x in zip(ids, lp)}      # decrescente no escore; empate pelo id
    else:
        chave = {i: (i,) for i in ids}                              # crescente no código IBGE (e ciclo)
    return lambda cand: regra_literal(cand, acima, grupo, chave)


# ---------------------------------------------------------------------------
# 4. Linhas
# ---------------------------------------------------------------------------

def rodar(unid: pd.DataFrame, parte: str, outcomes: dict, corte: int, janela: int, metodo: str, regra: str,
          aplica: bool, bloco: str, nomes: pd.DataFrame) -> tuple[list[dict], list[dict], dict, list[dict]]:
    """Uma linha do adendo: amostra (com ou sem a regra 2) e `pareamentos` do 44 com a regra pedida."""
    por_ciclo = parte == "H1"
    d2, am, exc = amostra(unid, corte, janela, aplica, nomes, parte)
    am["lados_que_procuram"] = lados_que_procuram(d2, por_ciclo)
    uso = unid[~unid["id"].isin({e["id"] for e in exc})]          # sem quem saiu pela regra 2 (se aplicada)
    args = (uso, parte, outcomes, corte, janela, por_ciclo, (metodo,), {metodo: bloco}, {metodo: PAPEL[bloco]})
    f_par = funcao_literal(d2, metodo, por_ciclo) if (regra == "literal" and metodo in ("PSM", "MAH")) else None
    if f_par is not None:
        with trocar_pareamento(f_par):
            ln, bl, rg = CL.pareamentos(*args)
    else:
        ln, bl, rg = CL.pareamentos(*args)
    if set(_ids_pareamento(uso, corte, janela)) != set(d2["id"]):
        raise FalhaValidacao(f"{bloco} {parte} {TXT_CORTE[corte]}: amostra do 44 difere da amostra da regra 2")
    procura = ";".join(f"{k}: {x['procura']}" for k, x in am["lados_que_procuram"].items())
    for x in ln:
        x.update({"estatuto": ESTATUTO, "populacao": _pop(parte, aplica, janela),
                  "regra_pareamento": "" if metodo == "IPW" else regra, "regra2": bool(aplica),
                  "saiu_regra2_abaixo": am.get("saiu_regra2", {}).get("abaixo", 0),
                  "saiu_regra2_acima": am.get("saiu_regra2", {}).get("acima", 0),
                  "lado_que_procura": procura if (regra == "literal" and metodo != "IPW") else ""})
        x["nota"] = _juntar(x["nota"], DESC_BLOCO[bloco])
    for x in bl:
        x.update({"estatuto": ESTATUTO, "regra_pareamento": regra, "regra2": bool(aplica)})
    rg.update({"bloco": bloco, "metodo": metodo, "regra_pareamento": regra, "amostra_48e": am})
    return ln, bl, rg, exc


def _ids_pareamento(unid: pd.DataFrame, corte: int, janela: int) -> list[str]:
    d = CL._janela(unid, corte, janela)
    return d.loc[CL._completo(d), "id"].tolist()


def _pop(parte: str, aplica: bool, janela: int) -> str:
    base = "H1 municipio x ciclo (48b)" if parte == "H1" else "V (protocolo 64)"
    return f"{base}; janela {janela / 1000:.3f}" + ("; sem as categorias de um lado so (regra 2)" if aplica else "")


def specs() -> list[dict]:
    """Todas as linhas do adendo (decisões 12 a 14)."""
    s = []
    for c in CORTES:
        for parte, outs in (("H1", OUT_H1), ("oferta_local", OUT_OC_PRINC)):
            princ = "PM-1" if parte == "H1" else "PM-2"
            s += [{"bloco": princ, "parte": parte, "outs": outs, "corte": c, "janela": JANELA_PAR, "metodo": "PSM",
                   "regra": "literal", "regra2": True},
                  {"bloco": "PM-3", "parte": parte, "outs": outs, "corte": c, "janela": JANELA_PAR, "metodo": "PSM",
                   "regra": "gulosa", "regra2": True},
                  {"bloco": "PM-4", "parte": parte, "outs": outs, "corte": c, "janela": JANELA_SENS, "metodo": "PSM",
                   "regra": "literal", "regra2": True},
                  {"bloco": "PM-5", "parte": parte, "outs": outs, "corte": c, "janela": JANELA_PAR, "metodo": "IPW",
                   "regra": "", "regra2": True},
                  {"bloco": "PM-6", "parte": parte, "outs": outs, "corte": c, "janela": JANELA_PAR, "metodo": "MAH",
                   "regra": "literal", "regra2": True},
                  {"bloco": "PM-F", "parte": parte, "outs": outs, "corte": c, "janela": JANELA_PAR, "metodo": "PSM",
                   "regra": "literal", "regra2": False}]
        s.append({"bloco": "PM-7", "parte": "oferta_local", "outs": OUT_OC_SEC, "corte": c, "janela": JANELA_PAR,
                  "metodo": "PSM", "regra": "literal", "regra2": True})
    return s


def todas_as_linhas(dados: dict, nomes: pd.DataFrame) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    linhas, bal, regs, exc, vistos = [], [], [], [], set()
    for s in specs():
        unid = dados["h1"] if s["parte"] == "H1" else dados["v"]
        ln, bl, rg, ex = rodar(unid, s["parte"], s["outs"], s["corte"], s["janela"], s["metodo"], s["regra"],
                               s["regra2"], s["bloco"], nomes)
        linhas += ln
        if s["metodo"] != "IPW":
            bal += bl
        regs.append(rg)
        chave = (s["parte"], s["corte"], s["janela"])
        if s["regra2"] and chave not in vistos:      # a lista de quem saiu é a mesma em todas as linhas da janela
            vistos.add(chave)
            exc += ex
    return linhas, bal, regs, exc


# ---------------------------------------------------------------------------
# 5. Portão (§4 do adendo; decisão 15)
# ---------------------------------------------------------------------------

def portao(dados: dict, cl_est: pd.DataFrame, cl_res: dict) -> dict:
    out = {"referencia": rotulo(CL_EST), "sha256_referencia": sha256(CL_EST), "tolerancia": TOL_PORTAO,
           "linhas": []}
    for parte, unid, outs, bloco in (("H1", dados["h1"], OUT_H1, "PS-1"),
                                     ("oferta_local", dados["v"], OUT_OC_PRINC, "PS-2")):
        ln, _, rg = CL.pareamentos(unid, parte, outs, 300, JANELA_PAR, parte == "H1", ("PSM",), {"PSM": bloco},
                                   {"PSM": "principal"})
        ref_reg = next(x for x in cl_res["amostra"]["pareamento"]
                       if x["parte"] == parte and x["corte"] == "0.300"
                       and abs(x["janela"] - JANELA_PAR / 1000) < 1e-12 and "pares" in (x.get("PSM") or {}))
        mesmos_pares = ({(p["acima"], p["abaixo"]) for p in rg["PSM"]["pares"]}
                        == {(p["acima"], p["abaixo"]) for p in ref_reg["PSM"]["pares"]})
        for x in ln:
            ref = CL._uma(cl_est, bloco=bloco, outcome=x["outcome"], corte="0.300")
            difs = {k: abs(_f(x[k]) - _f(ref[k])) for k in ("tau", "p_valor", "ic95_inf", "ic95_sup", "ic_t_inf",
                                                             "ic_t_sup")}
            n_ok = int(x["n_pares"]) == int(ref["n_pares"])
            esperado = PARES_48D.get("H1" if parte == "H1" else x["outcome"])
            if esperado is not None:
                n_ok = n_ok and int(x["n_pares"]) == esperado
            ok = all(np.isfinite(v) and v <= TOL_PORTAO for v in difs.values()) and n_ok and mesmos_pares
            out["linhas"].append({"linha": bloco, "parte": parte, "outcome": x["outcome"], "corte": "0.300",
                                  "tau_48d": _f(ref["tau"]), "tau_refeito": _f(x["tau"]),
                                  "max_abs_dif": max(difs.values()), "n_pares_48d": int(ref["n_pares"]),
                                  "n_pares_refeito": int(x["n_pares"]), "n_pares_adendo": esperado,
                                  "mesmos_pares": bool(mesmos_pares), "reproduz": bool(ok)})
            if not ok:
                raise FalhaValidacao(f"portão: {bloco} {x['outcome']} em 0,300 não reproduz o 48d: {difs}, pares "
                                     f"{x['n_pares']} x {ref['n_pares']} (esperado {esperado}), mesmos pares: "
                                     f"{mesmos_pares}")
    out["max_abs_dif"] = max(x["max_abs_dif"] for x in out["linhas"])
    out["aprovado"] = True
    return out


# ---------------------------------------------------------------------------
# 6. Multiplicidade e leitura (decisões 18 e 20 a 24)
# ---------------------------------------------------------------------------

def aplicar_multiplicidade(est: pd.DataFrame) -> pd.DataFrame:
    """Holm nas 8 de PM-1/PM-2 e BKY nas 38 de PM-3 a PM-7, famílias de tamanho fixo (sem estimativa: p = 1)."""
    est = est.copy()
    est["entra_holm"] = est["bloco"].isin(PRINCIPAIS)
    est["entra_bky"] = est["bloco"].isin(BKY)
    est["multiplicidade_provisoria"] = False
    for fam, col, fn, n_esp in (("entra_holm", "p_holm", L.holm, 8), ("entra_bky", "q_bky", L.qvalores_bky, 38)):
        m = est[fam].to_numpy(bool)
        if int(m.sum()) != n_esp:
            raise FalhaValidacao(f"família {col}: {int(m.sum())} linhas (esperadas {n_esp})")
        exe = (est["status"] == "EXECUTADO").to_numpy()
        p = np.where(exe[m], est.loc[m, "p_valor"].astype(float).to_numpy(), 1.0)
        adj = fn(p)
        est.loc[m, col] = np.where(exe[m], adj, np.nan)
    return est


def _contem_zero(r) -> bool:
    return _f(r["ic95_inf"]) <= 0.0 <= _f(r["ic95_sup"])


def leituras(est: pd.DataFrame, regs: list[dict]) -> dict:
    out = {"linhas": [], "geral": None, "parte_comparavel": [], "depende_da_regra": []}
    princ = est[est["bloco"].isin(PRINCIPAIS)]
    for _, r in princ.iterrows():
        if r["status"] != "EXECUTADO":
            cod = "SEM_ESTIMATIVA"
        elif _f(r["p_holm"]) < ALFA:
            cod = "REJEITA_ZERO_DEPOIS_DO_HOLM"
        elif not _contem_zero(r):
            cod = "IC_EXCLUI_ZERO_SEM_HOLM"
        elif r["comparacao_limpa"] != "SIM":
            cod = "BALANCO_NAO_LIMPO"
        else:
            cod = "IC_CONTEM_ZERO_BALANCO_LIMPO"
        out["linhas"].append({"bloco": r["bloco"], "outcome": r["outcome"], "corte": r["corte"], "codigo": cod,
                              "tau": _f(r["tau"]), "p_holm": _f(r["p_holm"])})
        g = CL._uma(est, bloco="PM-3", outcome=r["outcome"], corte=r["corte"])
        if r["status"] == "EXECUTADO" and g["status"] == "EXECUTADO":
            opostos = _f(r["tau"]) * _f(g["tau"]) < 0
            if opostos and _contem_zero(r) and _contem_zero(g):
                out["depende_da_regra"].append({"outcome": r["outcome"], "corte": r["corte"],
                                                "codigo": "PONTO_DEPENDE_DA_REGRA"})
    cods = [x["codigo"] for x in out["linhas"]]
    if any(c == "REJEITA_ZERO_DEPOIS_DO_HOLM" for c in cods):
        out["geral"] = "REJEITA_ZERO_DEPOIS_DO_HOLM"
    elif len(cods) == 8 and all(c == "IC_CONTEM_ZERO_BALANCO_LIMPO" for c in cods):
        out["geral"] = "NAO_SE_DETECTA_DIFERENCA"
    else:
        out["geral"] = "PRIMEIRA_LEITURA_NAO_SE_APLICA"
    vistos = set()
    for rg in regs:
        am = rg["amostra_48e"]
        chave = (am["parte"], am["corte"])
        if not am["regra2"] or abs(am["janela"] - JANELA_PAR / 1000) > 1e-12 or chave in vistos:
            continue
        vistos.add(chave)
        fr = am["fracao_saiu_regra2"]
        lados = [lado for lado in ("abaixo", "acima") if fr[lado] > LIMIAR_SAIDA]
        if lados:
            out["parte_comparavel"].append({"parte": am["parte"], "corte": am["corte"], "lados": lados,
                                            "fracao": {k: fr[k] for k in lados},
                                            "categorias": [c["categoria"] for c in am["categorias_um_lado"]],
                                            "codigo": "VALE_SO_PARA_PARTE_COMPARAVEL"})
    return out


# ---------------------------------------------------------------------------
# 7. Formatação e blocos do doc 57s
# ---------------------------------------------------------------------------

fn, fp, fv, fic, fint = CL.fn, CL.fp, CL.fv, CL.fic, CL.fint
_tab = CL._tab
NOME_OUT = CL.NOME_OUT
NOME_PARTE = {"H1": "H1", "oferta_local": "oferta local"}


def _corte_txt(ct) -> str:
    return TXT_CORTE[int(round(_f(ct) * 1000))]


def _cat_txt(c: str) -> str:
    return {"capital": "capitais", "nao capital": "não capitais"}.get(c, c.replace("regiao[", "região ").rstrip("]"))


def _pct(x: float) -> str:
    return fn(100 * x, 0, False) + "%"


def bloco(nome: str, corpo: str) -> str:
    return f"<!-- PM:{nome}:inicio -->\n{corpo.rstrip()}\n<!-- PM:{nome}:fim -->"


def _am(resumo: dict, parte: str, corte: str, janela: float) -> dict:
    return next(x for x in resumo["amostras"] if x["parte"] == parte and x["corte"] == corte
                and abs(x["janela"] - janela) < 1e-12 and x["regra2"])


def tab_portao(resumo: dict) -> str:
    p = resumo["portao"]
    linhas = [[x["linha"], NOME_OUT[x["outcome"]], _corte_txt(x["corte"]), fn(x["tau_48d"], 6), fn(x["tau_refeito"], 6),
               f"{x['max_abs_dif']:.1e}", f"{x['n_pares_48d']} / {x['n_pares_refeito']}",
               "sim" if x["mesmos_pares"] else "não", "sim" if x["reproduz"] else "não"] for x in p["linhas"]]
    return _tab(["Linha do 48d", "Outcome", "Corte", "Diferença média em CL_estimativas.csv", "Refeita aqui",
                 "máx. dif. absoluta (estimativa, p, IC)", "Pares (48d / refeito)", "Mesmos pares", "Reproduz"],
                linhas)


def tab_regra2(resumo: dict, exc: pd.DataFrame) -> str:
    linhas = []
    for x in resumo["amostras"]:
        if not x["regra2"]:
            continue
        cats = ", ".join(f"{_cat_txt(c['categoria'])} ({c['unidades']}, todas {c['lado']})"
                         for c in x["categorias_um_lado"]) or "nenhuma"
        dep = ", ".join(_cat_txt(c["categoria"]) for c in x["categorias_um_lado_depois"]) or "nenhuma"
        linhas.append([NOME_PARTE[x["parte"]], _corte_txt(x["corte"]), fn(x["janela"], 3, False),
                       f"{x['apos_covariavel']['abaixo']} / {x['apos_covariavel']['acima']}", cats,
                       f"{x['saiu_regra2']['abaixo']} / {x['saiu_regra2']['acima']}",
                       f"{_pct(x['fracao_saiu_regra2']['abaixo'])} / {_pct(x['fracao_saiu_regra2']['acima'])}", dep])
    t1 = _tab(["Amostra", "Corte", "Janela", "Unidades com todas as covariáveis (abaixo / acima)",
               "Categorias de um lado só", "Saíram pela regra 2 (abaixo / acima)", "Fração que saiu (abaixo / acima)",
               "Categorias de um lado só depois da saída"], linhas)
    if exc.empty:
        return t1 + "\n\nNinguém saiu pela regra 2."
    linhas = []
    for (parte, ct, jan), g in exc.groupby(["parte", "corte", "janela"], sort=False):
        por_mun = g.groupby(["co_ibge", "municipio", "uf", "lado", "categorias"], sort=True)["ciclo"]
        for (cod, mun, uf, lado, cats), cic in por_mun:
            ciclos = ", ".join(str(int(c)) for c in sorted(cic.dropna())) if cic.notna().any() else "—"
            linhas.append([NOME_PARTE[parte], _corte_txt(ct), fn(jan, 3, False), f"{mun} ({uf})", cod, ciclos, lado,
                           ", ".join(_cat_txt(c) for c in cats.split(";"))])
    t2 = _tab(["Amostra", "Corte", "Janela", "Município", "Código IBGE", "Ciclos", "Lado", "Por quê"], linhas)
    return t1 + "\n\nQuem saiu (lista completa em `output/rdd_bolsa/PM_excluidos.csv`):\n\n" + t2


def tab_amostra(resumo: dict) -> str:
    linhas, vistos = [], set()
    for x in resumo["amostras"]:
        chave = (x["parte"], x["corte"], x["janela"], x["regra2"])
        if chave in vistos:
            continue
        vistos.add(chave)
        procura = "; ".join(f"{k}: {v['procura']} ({v['abaixo']} / {v['acima']})"
                            for k, v in x["lados_que_procuram"].items())
        linhas.append([NOME_PARTE[x["parte"]], _corte_txt(x["corte"]), fn(x["janela"], 3, False),
                       "sim" if x["regra2"] else "não", f"{x['na_janela']['abaixo']} / {x['na_janela']['acima']}",
                       f"{x['sem_covariavel']['abaixo']} / {x['sem_covariavel']['acima']}",
                       f"{x['amostra_pareamento']['abaixo']} / {x['amostra_pareamento']['acima']}", procura])
    return _tab(["Amostra", "Corte", "Janela", "Regra 2", "Na janela (abaixo / acima)",
                 "Sem alguma covariável (abaixo / acima)", "No pareamento (abaixo / acima)",
                 "Lado que procura par, por grupo (abaixo / acima)"], linhas)


def tab_comparacao(est: pd.DataFrame, cl_est: pd.DataFrame) -> str:
    linhas = []
    for c in CORTES:
        ct = ROT_CORTE[c]
        for oid in list(OUT_H1) + list(OUT_OC_PRINC):
            bl48 = "PS-1" if oid in OUT_H1 else "PS-2"
            princ = "PM-1" if oid in OUT_H1 else "PM-2"
            cel = []
            for r in (CL._uma(cl_est, bloco=bl48, outcome=oid, corte=ct), CL._uma(est, bloco="PM-F", outcome=oid, corte=ct),
                      CL._uma(est, bloco="PM-3", outcome=oid, corte=ct), CL._uma(est, bloco=princ, outcome=oid, corte=ct)):
                cel.append(f"{fv(r)} {fic(r)} ({fint(r['n_pares'])} pares)" if r["status"] == "EXECUTADO"
                           else "sem estimativa")
            linhas.append([NOME_OUT[oid], _corte_txt(ct)] + cel)
    return _tab(["Outcome", "Corte", "48d: gulosa, sem a regra 2 (PS-1/PS-2)", "48e: literal, sem a regra 2 (PM-F)",
                 "48e: gulosa, com a regra 2 (PM-3)", "48e: literal, com a regra 2 (PM-1/PM-2, principal)"], linhas)


def leitura_txt(resumo: dict) -> str:
    le = resumo["leitura"]
    linhas = [["§3, 1ª e 2ª linhas", f"{x['bloco']} {NOME_OUT[x['outcome']]}", _corte_txt(x["corte"]),
               f"`{x['codigo']}`"] for x in le["linhas"]]
    linhas.append(["§3, 1ª linha (as oito juntas)", "PM-1 e PM-2", "0,300 e 0,400", f"`{le['geral']}`"])
    for x in le["parte_comparavel"]:
        linhas.append(["§3, 3ª linha", NOME_PARTE[x["parte"]], _corte_txt(x["corte"]),
                       f"`{x['codigo']}` (lado {', '.join(x['lados'])})"])
    if not le["parte_comparavel"]:
        linhas.append(["§3, 3ª linha", "H1 e oferta local", "0,300 e 0,400", "a regra 2 não tira mais de 25% de nenhum "
                       "lado"])
    for x in le["depende_da_regra"]:
        linhas.append(["§3, 4ª linha", NOME_OUT[x["outcome"]], _corte_txt(x["corte"]), f"`{x['codigo']}`"])
    if not le["depende_da_regra"]:
        linhas.append(["§3, 4ª linha", "PM-3 × PM-1/PM-2", "0,300 e 0,400",
                       "nenhuma linha com sinais opostos e os dois IC contendo zero"])
    return _tab(["Regra", "Linha", "Corte", "Código"], linhas)


def _frase_linha(r) -> str:
    if r["status"] != "EXECUTADO":
        return f"{NOME_OUT[r['outcome']]}: sem estimativa ({r['nota'].split(';')[0]})"
    limpa = "balanço limpo" if r["comparacao_limpa"] == "SIM" else "balanço **não** limpo (|DP| > 0,25 depois)"
    return (f"{NOME_OUT[r['outcome']]}: {fv(r)} (IC permutação {fic(r)}; p Holm {fp(r['p_holm'])}; "
            f"{fint(r['n_pares'])} pares; {limpa})")


def _saida_txt(resumo: dict, corte: str) -> str:
    partes = []
    for parte in ("H1", "oferta_local"):
        x = _am(resumo, parte, corte, JANELA_PAR / 1000)
        n = x["saiu_regra2"]["abaixo"] + x["saiu_regra2"]["acima"]
        if not n:
            partes.append(f"na {NOME_PARTE[parte]}, ninguém")
            continue
        un = "linhas município × ciclo" if parte == "H1" else "municípios"
        cats = ", ".join(_cat_txt(c["categoria"]) for c in x["categorias_um_lado"])
        partes.append(f"na {NOME_PARTE[parte]}, {n} {un} ({x['saiu_regra2']['abaixo']} de "
                      f"{x['apos_covariavel']['abaixo']} abaixo, {_pct(x['fracao_saiu_regra2']['abaixo'])}; "
                      f"{x['saiu_regra2']['acima']} de {x['apos_covariavel']['acima']} acima, "
                      f"{_pct(x['fracao_saiu_regra2']['acima'])}): {cats}")
    return "; ".join(partes)


def resposta_curta(est: pd.DataFrame, resumo: dict) -> str:
    le = resumo["leitura"]
    partes = []
    if le["geral"] == "NAO_SE_DETECTA_DIFERENCA":
        cab = ("**Pareando pela regra literal e sem as categorias de um lado só, não se detecta diferença nos dois "
               "cortes**: comparando municípios parecidos em localização e em médicos na região, perto do corte, não "
               "se detecta diferença no preenchimento das vagas imediatas nem na oferta local de especialistas. "
               "Todas as oito linhas principais têm IC que contém zero e balanço limpo depois do pareamento.")
    elif le["geral"] == "REJEITA_ZERO_DEPOIS_DO_HOLM":
        rej = [x for x in le["linhas"] if x["codigo"] == "REJEITA_ZERO_DEPOIS_DO_HOLM"]
        cab = ("**Alguma linha principal rejeita zero depois do Holm**: " + "; ".join(
            f"{NOME_OUT[x['outcome']]} em {_corte_txt(x['corte'])} "
            f"({'lado de bolsa maior acima' if x['tau'] > 0 else 'lado de bolsa maior abaixo'}; p Holm "
            f"{fp(x['p_holm'])})" for x in rej) + ". O que se mede é o pacote do corte, e a comparação vale para "
            "as unidades que ficaram depois da regra 2.")
    else:
        motivos = {"SEM_ESTIMATIVA": "sem estimativa", "BALANCO_NAO_LIMPO": "balanço não limpo",
                   "IC_EXCLUI_ZERO_SEM_HOLM": "IC de permutação sem zero, mas sem rejeitar zero depois do Holm"}
        fora = [x for x in le["linhas"] if x["codigo"] != "IC_CONTEM_ZERO_BALANCO_LIMPO"]
        cab = ("**Nenhuma linha principal rejeita zero depois do Holm, mas a primeira leitura do §3 não vale para "
               "todas as oito**: " + "; ".join(f"{NOME_OUT[x['outcome']]} em {_corte_txt(x['corte'])}: "
                                               f"{motivos[x['codigo']]}" for x in fora) + ".")
    partes.append(cab)
    for c in CORTES:
        ct = ROT_CORTE[c]
        frases = [_frase_linha(CL._uma(est, bloco="PM-1" if oid in OUT_H1 else "PM-2", outcome=oid, corte=ct))
                  for oid in list(OUT_H1) + list(OUT_OC_PRINC)]
        partes.append(f"- **Corte {TXT_CORTE[c]}** ({BOLSA[c]}): " + "; ".join(frases) + ".")
    partes.append("**Quem saiu pela regra 2 (janela de 0,050):** " + " ".join(
        f"Em {TXT_CORTE[c]}, {_saida_txt(resumo, ROT_CORTE[c])}." for c in CORTES)
        + " A lista com nomes está na seção 2.")
    if le["parte_comparavel"]:
        partes.append("**Comparação só para a parte comparável:** " + "; ".join(
            f"em {_corte_txt(x['corte'])}, na {NOME_PARTE[x['parte']]}, a regra 2 tirou mais de 25% do lado "
            f"{' e do lado '.join(x['lados'])} ({', '.join(_pct(v) for v in x['fracao'].values())}). Ali a "
            f"comparação vale só para os municípios sem {', '.join(_cat_txt(k) for k in x['categorias'])}"
            for x in le["parte_comparavel"]) + ".")
    else:
        partes.append("**Parte comparável:** em nenhum corte a regra 2 tirou mais de 25% de um lado. Mesmo assim, a "
                      "comparação vale só para as unidades que ficaram (quem saiu está na seção 2).")
    dif = []
    for c in CORTES:
        ct = ROT_CORTE[c]
        for oid in list(OUT_H1) + list(OUT_OC_PRINC):
            r = CL._uma(est, bloco="PM-1" if oid in OUT_H1 else "PM-2", outcome=oid, corte=ct)
            g = CL._uma(est, bloco="PM-3", outcome=oid, corte=ct)
            if r["status"] == "EXECUTADO" and g["status"] == "EXECUTADO" and _f(r["tau"]) * _f(g["tau"]) < 0:
                dif.append(f"{NOME_OUT[oid]} em {TXT_CORTE[c]} (gulosa {fv(g)}, literal {fv(r)})")
    if le["depende_da_regra"]:
        partes.append("**O ponto depende da regra de pareamento:** a regra gulosa (PM-3) e a literal dão sinais "
                      "opostos, com os dois IC contendo zero, em " + "; ".join(dif)
                      + ". Nessas linhas, ler só o intervalo, não o ponto.")
    elif dif:
        partes.append("**Regra gulosa × literal:** os sinais diferem em " + "; ".join(dif)
                      + ", mas não com os dois IC contendo zero.")
    else:
        partes.append("**Regra gulosa × literal:** nas oito linhas principais, as duas regras dão o mesmo sinal.")
    partes.append("Tudo é robustez pós-resultado do 48d e se refere ao pacote do corte, não à bolsa isolada. O principal "
                  "da H1 continua o 48b, e o da oferta local, o protocolo 64 sem controle.")
    return "\n\n".join(partes)


def gerar_blocos(est: pd.DataFrame, bal: pd.DataFrame, exc: pd.DataFrame, resumo: dict,
                 cl_est: pd.DataFrame) -> dict[str, str]:
    figs = "\n\n".join(f"![{Path(f['arquivo']).stem}](../../{f['arquivo']})\n\n**{f['como_ler']}**"
                       for f in resumo["figuras"])
    lim = [
        "**Pós-resultado.** Os resultados do 48d e a auditoria 40 (inclusive o PSM em 0,300 refeito com o lado menor "
        "procurando par) já tinham sido vistos quando o 48e foi congelado. As regras foram fixadas antes destas contas, "
        "mas a pergunta não é cega ao resultado.",
        "**Pacote do corte.** Em 0,300 e 0,400 mudam a bolsa e outras regras federais (auditoria 18). O pareamento não "
        "isola o incentivo de R$ 5 mil.",
        "**A regra 2 muda quem é comparado.** Onde ela tira unidades, a comparação vale só para quem ficou (por exemplo, "
        "municípios que não são capitais e de regiões presentes dos dois lados), não para toda a janela.",
        "**O que o pareamento supõe.** Que, perto do corte e com o mesmo L+M, estar de um lado ou do outro é como "
        "sorteado. Não usa a reta da RDD.",
        "**O ponto depende da ordem.** Com poucas unidades, a ordem em que se procura par muda quem forma par e a "
        "estimativa pontual; por isso a regra gulosa (PM-3) é relatada ao lado.",
        "**Poucos municípios e o mesmo município em ciclos diferentes.** O estimando é a média nos pares formados, e na "
        "H1 um município pode estar em pares de ciclos diferentes; a permutação trata os pares como independentes.",
        "**Mahalanobis com *caliper* apertado.** O *caliper* do 48d deixa quase nenhum par (auditoria 40, achado 10); "
        "a PM-6 herda isso.",
    ]
    return {
        "resposta_curta": resposta_curta(est, resumo),
        "portao": tab_portao(resumo),
        "regra2": tab_regra2(resumo, exc),
        "amostra": tab_amostra(resumo),
        "principais": CL.tab_psm(est, PRINCIPAIS),
        "comparacao": tab_comparacao(est, cl_est),
        "sensibilidades": CL.tab_psm(est, ("PM-3", "PM-4", "PM-5", "PM-6")),
        "secundaria": CL.tab_psm(est, ("PM-7",)),
        "figura_sem_regra2": CL.tab_psm(est, ("PM-F",)).replace("— (sensibilidade)", "— (só para a figura)"),
        "balanco": CL.tab_balanco(bal),
        "leitura": leitura_txt(resumo),
        "figuras": figs,
        "limites": "\n".join(f"- {x}" for x in lim),
    }


MARCA = re.compile(r"<!-- PM:(?P<nome>[A-Za-z0-9_]+):inicio -->\n(?P<corpo>.*?)\n?<!-- PM:(?P=nome):fim -->", re.S)


def atualizar_doc(est, bal, exc, resumo, cl_est) -> None:
    txt = DOC.read_text(encoding="utf-8")
    blocos = gerar_blocos(est, bal, exc, resumo, cl_est)
    falta = set(blocos) - {m.group("nome") for m in MARCA.finditer(txt)}
    if falta:
        raise FalhaValidacao(f"doc 57s sem os marcadores {sorted(falta)}")
    DOC.write_text(MARCA.sub(lambda m: bloco(m.group("nome"), blocos[m.group("nome")]) if m.group("nome") in blocos
                             else m.group(0), txt), encoding="utf-8")


# ---------------------------------------------------------------------------
# 8. Figuras
# ---------------------------------------------------------------------------

FONTE = ("Fonte: outcomes do 12 (ciclos 1–3; ciclo 2 pelo quadro de 13/02/2026), CNES a09, a16, Censo 2022, IBGE, IVS "
         "2010 oficial (a08); CL_estimativas.csv (48d). EMPIRICO · scripts/rdd_bolsa/45_pareamento_regra_literal.py")
COMO_LER = {
    "PM_principal.png": (
        "Como ler: cada ponto é a diferença média nos pares (lado de bolsa maior − lado de bolsa menor); a barra é o "
        "IC 95% de permutação. Em cada painel, de cima para baixo: o 48d (regra gulosa, com todas as unidades), o 48e "
        "pela regra literal com todas as unidades e o 48e pela regra literal sem as categorias de região ou capital que "
        "só aparecem de um lado do corte (o principal). 'Sem estimativa': o escore não pôde ser estimado (há categorias "
        "de um lado só). Barra que cruza o zero: não se detecta diferença, o que não quer dizer que ela seja zero. "
        "Pacote do corte, não só a bolsa."),
    "PM_escore_0400.png": (
        "Como ler: distribuição do escore de propensão (chance estimada de estar acima do corte, dado localização e "
        "médicos na região) dos dois lados, no corte de 0,400, janela de 0,050, depois de tirar as categorias de um "
        "lado só. Azul: lado de bolsa menor; laranja: lado de bolsa maior. As linhas tracejadas marcam o suporte comum; "
        "fora delas não há com quem comparar."),
}


def _rodape(fig, texto: str, W: float, H_: float, largura: int) -> None:
    """Como o `_rodape` do 44, com a fonte deste script."""
    import textwrap
    linhas = textwrap.wrap(texto, largura)
    yy = 0.12 + 0.24 * len(linhas)
    for t in linhas:
        fig.text(0.1 / W, yy / H_, t, fontsize=10.5, color=CL.TINTA, va="top")
        yy -= 0.24
    fig.text(0.1 / W, 0.04 / H_, FONTE, fontsize=7.5, color=CL.CINZA, va="bottom")


def _it(r, rot: str, esc: float, casas: int) -> dict:
    it = CL._it(r, rot, esc, casas)
    if r["status"] != "EXECUTADO":
        it["valor"] = "sem estimativa"
    return it


def gerar_figuras(est: pd.DataFrame, cl_est: pd.DataFrame, regs: list[dict]) -> list[dict]:
    plt = CL._plt()
    DIR_FIG.mkdir(parents=True, exist_ok=True)
    feitas = []
    nome = "PM_principal.png"
    W, H_ = 17.0, 12.5
    fig = plt.figure(figsize=(W, H_))
    fig.text(0.1 / W, (H_ - 0.12) / H_, "Pareamento por escore de propensão: 48d (gulosa) × 48e (literal) × 48e "
             "(literal, sem as categorias de um lado só)", fontsize=13.5, weight="bold", va="top")
    oids = list(OUT_H1) + list(OUT_OC_PRINC)
    eixos = {"H1M-FRAC": "diferença (p.p.)", "H1M-ALOC": "médicos por vaga imediata",
             "dB1": "vínculos por 10 mil hab.", "dB2": "horas SUS por 10 mil hab."}
    for j, c in enumerate(CORTES):
        ct = ROT_CORTE[c]
        x0 = 2.9 + j * 8.4
        y = H_ - 0.9
        for oid in oids:
            esc, casas = (100.0, 1) if oid == "H1M-FRAC" else (1.0, 2)
            bl48 = "PS-1" if oid in OUT_H1 else "PS-2"
            princ = "PM-1" if oid in OUT_H1 else "PM-2"
            its = [_it(CL._uma(cl_est, bloco=bl48, outcome=oid, corte=ct), "48d gulosa", esc, casas),
                   _it(CL._uma(est, bloco="PM-F", outcome=oid, corte=ct), "48e literal", esc, casas),
                   _it(CL._uma(est, bloco=princ, outcome=oid, corte=ct), "48e literal, sem um lado só", esc, casas)]
            h = 0.42 * len(its)
            y0 = y - 0.75 - h
            ax = fig.add_axes([x0 / W, y0 / H_, 3.0 / W, h / H_])
            tit = (f"Corte {TXT_CORTE[c]} ({BOLSA[c]})\n" if oid == oids[0] else "") + NOME_OUT[oid]
            CL._floresta(ax, its, tit, eixos[oid])
            y = y0 - 0.55
    _rodape(fig, COMO_LER[nome], W, H_, 190)
    fig.savefig(DIR_FIG / nome, dpi=170, facecolor="white", metadata={"Software": None})
    plt.close(fig)
    feitas.append({"arquivo": rotulo(DIR_FIG / nome), "como_ler": COMO_LER[nome],
                   "fonte": "CL_estimativas.csv (PS-1, PS-2) e PM_estimativas.csv (PM-F, PM-1, PM-2)"})
    nome = "PM_escore_0400.png"
    W, H_ = 14.0, 6.0
    fig = plt.figure(figsize=(W, H_))
    fig.text(0.1 / W, (H_ - 0.12) / H_, "Escore de propensão em 0,400, sem as categorias de um lado só (janela de "
             "0,050)", fontsize=14, weight="bold", va="top")
    for j, (parte, princ, un) in enumerate((("H1", "PM-1", "município × ciclo"),
                                            ("oferta_local", "PM-2", "município"))):
        rg = next(x for x in regs if x["bloco"] == princ and x["corte"] == "0.400")
        ax = fig.add_axes([(0.9 + j * 6.9) / W, 1.6 / H_, 5.8 / W, 3.6 / H_])
        if rg.get("escore_por_unidade"):
            e = np.array(rg["escore_por_unidade"]["escore"])
            a = np.array(rg["escore_por_unidade"]["acima"]).astype(bool)
            bins = np.linspace(0, 1, 21)
            ax.hist(e[~a], bins=bins, color=CL.AZUL, alpha=0.6, label="abaixo do corte (bolsa menor)")
            ax.hist(e[a], bins=bins, color=CL.LARANJA, alpha=0.6, label="acima do corte (bolsa maior)")
            for lim in (rg.get("PSM") or {}).get("suporte_comum") or []:
                ax.axvline(lim, color=CL.TINTA2, lw=1, ls=(0, (4, 3)))
            ax.legend(fontsize=9, frameon=False)
        else:
            ax.text(0.5, 0.5, "escore não estimado (o logit não convergiu)", ha="center", va="center",
                    transform=ax.transAxes, fontsize=10.5)
        ax.set_title(f"{NOME_PARTE[parte].capitalize() if parte == 'H1' else 'Oferta local'}", fontsize=11, loc="left",
                     weight="bold")
        ax.set_xlabel("escore de propensão (chance de estar acima, dado L+M)", fontsize=9.5)
        ax.set_ylabel(un, fontsize=9.5)
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)
    _rodape(fig, COMO_LER[nome], W, H_, 160)
    fig.savefig(DIR_FIG / nome, dpi=170, facecolor="white", metadata={"Software": None})
    plt.close(fig)
    feitas.append({"arquivo": rotulo(DIR_FIG / nome), "como_ler": COMO_LER[nome],
                   "fonte": "PM_resumo.json: pareamento (escore por unidade), PM-1 e PM-2, 0,400, janela 0,050"})
    return feitas


# ---------------------------------------------------------------------------
# 9. Resumo, gravação e execução
# ---------------------------------------------------------------------------

def _finalizar(linhas: list[dict], bal_l: list[dict], exc_l: list[dict]):
    est = pd.DataFrame(linhas).reindex(columns=COLUNAS)
    est["id_linha"] = (est["bloco"] + "|" + est["parte"] + "|" + est["outcome"] + "|" + est["corte"] + "|w="
                       + est["janela"].map(lambda x: f"{x:.3f}") + "|" + est["metodo"])
    if est["id_linha"].duplicated().any():
        raise FalhaValidacao(f"id_linha duplicado: {est.loc[est['id_linha'].duplicated(), 'id_linha'].tolist()}")
    for c in ("entra_holm", "entra_bky", "multiplicidade_provisoria", "regra2"):
        est[c] = est[c].astype(bool)
    est = aplicar_multiplicidade(est)
    bal = pd.DataFrame(bal_l).reindex(columns=COLUNAS_BAL)
    exc = pd.DataFrame(exc_l, columns=COLUNAS_EXC)
    exc["ciclo"] = exc["ciclo"].astype("Int64")
    if est["status"].isin(["PENDENTE_OC"]).any():
        raise FalhaValidacao("linha PENDENTE_OC: o 48e exige as saídas OC_*")
    return est, bal, exc


def entradas() -> list[dict]:
    arqs = [ADENDO, CL.ADENDO, CL_EST, CL_RES]
    return [{"arquivo": rotulo(p), "sha256": sha256(p)} for p in arqs] + CL.entradas()


def _amostras(regs: list[dict]) -> list[dict]:
    out, vistos = [], set()
    for rg in regs:
        am = rg["amostra_48e"]
        chave = (am["parte"], am["corte"], am["janela"], am["regra2"])
        if chave not in vistos:
            vistos.add(chave)
            out.append(am)
    return out


def montar_resumo(est, regs, exc, prt, dados, protegidos) -> dict:
    return {
        "etapa": "Adendo 48e: pareamento pela regra literal do 48d e PSM em 0,400 sem as categorias de um lado so",
        "natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "data_execucao": DATA_EXECUCAO,
        "script": "scripts/rdd_bolsa/45_pareamento_regra_literal.py",
        "adendo": {"arquivo": rotulo(ADENDO), "sha256": sha256(ADENDO), "commit_congelamento": COMMIT_CONGELAMENTO,
                   "commit_decisoes_57s": COMMIT_DECISOES},
        "contraste": CONTRASTE,
        "parametros": {"cortes": [0.300, 0.400], "janela_pareamento": JANELA_PAR / 1000,
                       "janela_sensibilidade": JANELA_SENS / 1000, "caliper_psm": CL.CALIPER_PS,
                       "caliper_mahalanobis": CL.CALIPER_MAH, "aparo_ipw": list(CL.APARO_IPW),
                       "n_permutacoes": CL.N_PERM, "semente": CL.SEMENTE, "tolerancia_portao": TOL_PORTAO,
                       "limiar_saida_regra2": LIMIAR_SAIDA, "competencias_pre": list(CL.COMP_PRE),
                       "competencias_pos_oferta_local": list(CL.COMP_POS)},
        "blocos": DESC_BLOCO,
        "entradas": entradas(),
        "saidas_protegidas_sha256": protegidos,
        "covariaveis": dados["info_cov"],
        "oferta_local": {"V": dados["info_v"], "construcao_delta_b": dados["info_oc"]},
        "portao": prt,
        "amostras": _amostras(regs),
        "pareamento": regs,
        "excluidos_regra2": int(len(exc)),
        "contagens": {"linhas": int(len(est)), "por_bloco": est["bloco"].value_counts().sort_index().to_dict(),
                      "por_status": est["status"].value_counts().sort_index().to_dict(),
                      "holm": {"n_familia": int(est["entra_holm"].sum())},
                      "bky": {"n_familia": int(est["entra_bky"].sum())}},
        "leitura": leituras(est, regs),
        "integridade": {"ivs": "IVS 2010 oficial (a08); o arquivo local de IVS da auditoria 16 nao e lido",
                        "cnes": "competencias 202406-202506 (covariaveis) e 202406-202608 (oferta local); nenhuma "
                                ">= 202609",
                        "imputacao": "nada imputado; ausente fica ausente e e contado",
                        "saidas_nao_regravadas": ["CL_*", "HI_*", "OC_*"]},
        "saidas": {"estimativas": rotulo(OUT / NOME_EST), "balanco": rotulo(OUT / NOME_BAL),
                   "excluidos": rotulo(OUT / NOME_EXC), "resumo": rotulo(OUT / NOME_RESUMO),
                   "figuras": rotulo(DIR_FIG), "doc": rotulo(DOC)},
        "linguagem": "pacote do corte; 'nao se detecta' nao e 'zero'; nunca 'causa'",
    }


def gravar(est, bal, exc, resumo) -> None:
    est.to_csv(OUT / NOME_EST, index=False)
    bal.to_csv(OUT / NOME_BAL, index=False)
    exc.to_csv(OUT / NOME_EXC, index=False)
    (OUT / NOME_RESUMO).write_text(json.dumps(CL._nan_none(resumo), ensure_ascii=False, indent=1) + "\n",
                                   encoding="utf-8")


def ler_saidas():
    est = pd.read_csv(OUT / NOME_EST, dtype={"corte": str, "comparacao_limpa": str})
    for c in ("entra_holm", "entra_bky", "multiplicidade_provisoria", "regra2"):
        est[c] = est[c].astype(str).str.lower().isin(["true", "1"])
    for c in ("nota", "covariaveis_descartadas", "comparacao_limpa", "variaveis", "regra_pareamento",
              "lado_que_procura"):
        est[c] = est[c].fillna("")
    bal = pd.read_csv(OUT / NOME_BAL, dtype={"corte": str})
    bal["nota"] = bal["nota"].fillna("")
    exc = pd.read_csv(OUT / NOME_EXC, dtype={"corte": str, "co_ibge": str})
    return est, bal, exc, json.loads((OUT / NOME_RESUMO).read_text(encoding="utf-8"))


def ler_cl() -> tuple[pd.DataFrame, dict]:
    est, _, res = CL.ler_saidas()
    return est, res


def executar(atualizar: bool) -> int:
    if sha256(ADENDO) != SHA_ADENDO:
        raise FalhaValidacao("o adendo 48e mudou depois do congelamento")
    if sha256(CL.ADENDO) != CL.SHA_ADENDO:
        raise FalhaValidacao("o adendo 48d mudou depois do congelamento")
    if not CL.OC_EST.exists():
        raise FalhaValidacao("saídas OC_* do protocolo 64 ausentes: o 48e exige a oferta local")
    protegidos = hashes_protegidos()
    cl_est, cl_res = ler_cl()
    print("Bases do 48d (funções do 44)...", flush=True)
    dados = carregar()
    nomes = nomes_municipios()
    print("Portão: PS-1 e PS-2 do 48d em 0,300...", flush=True)
    prt = portao(dados, cl_est, cl_res)
    print(f"  reproduz (máx |dif| = {prt['max_abs_dif']:.1e})", flush=True)
    print("PM-1 a PM-7 e PM-F...", flush=True)
    linhas, bal_l, regs, exc_l = todas_as_linhas(dados, nomes)
    est, bal, exc = _finalizar(linhas, bal_l, exc_l)
    resumo = montar_resumo(est, regs, exc, prt, dados, protegidos)
    resumo["figuras"] = gerar_figuras(est, cl_est, regs)
    if hashes_protegidos() != protegidos:
        raise FalhaValidacao("saídas CL_*, HI_* ou OC_* mudaram durante a execução")
    gravar(est, bal, exc, resumo)
    if atualizar:                       # o doc sai das saídas gravadas, como o teste o refaz
        atualizar_doc(*ler_saidas(), cl_est)
        print(f"Doc regravado: {rotulo(DOC)}")
    for _, r in est[est["entra_holm"]].iterrows():
        print(f"  {r['bloco']} {r['outcome']} {r['corte']}: {r['status']} tau={_f(r['tau']):.4f} "
              f"[{_f(r['ic95_inf']):.4f}; {_f(r['ic95_sup']):.4f}] p={_f(r['p_valor']):.4f} "
              f"p_holm={_f(r['p_holm']):.4f} pares={_f(r['n_pares']):.0f}")
    print(f"Gravado: {rotulo(OUT / NOME_EST)} ({len(est)} linhas), {NOME_BAL}, {NOME_EXC} ({len(exc)}), "
          f"{NOME_RESUMO}, {rotulo(DIR_FIG)}/")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--atualizar-doc", action="store_true", help="regrava os blocos do doc 57s")
    ap.add_argument("--so-doc", action="store_true", help="só regrava os blocos do doc 57s das saídas")
    args = ap.parse_args(argv)
    try:
        if args.so_doc:
            est, bal, exc, resumo = ler_saidas()
            atualizar_doc(est, bal, exc, resumo, ler_cl()[0])
            return 0
        return executar(args.atualizar_doc)
    except (FalhaValidacao, CL.FalhaValidacao, CL.T40.FalhaValidacao, CL.T41.FalhaValidacao, CL.T37.FalhaValidacao,
            CL.T43.FalhaValidacao, CL.K1M.FalhaValidacao, CL.D2M.FalhaValidacao) as erro:
        print(f"FALHA (nada gravado): {erro}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
