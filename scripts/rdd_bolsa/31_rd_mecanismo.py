"""P6 (protocolo 56): alocado por pouco contra não alocado por pouco — estimação (R1–R6), balanço e doc 57f.

Protocolo: `docs/06_execucao/56_protocolo_P6_mecanismo_alocacao.md`, congelado em 19/10/2026 antes de ligar os
candidatos ao painel CNES e de abrir outcomes. Estatuto: `EXPLORATORIO_P6`; `natureza_dos_dados = EMPIRICO`.

O contraste é ser ALOCADO na 1ª opção do PMM-E para candidatos de ampla concorrência perto da nota de corte da
célula (r = nota − nota de corte; r ∈ {−2, −1} contra r ∈ {+1, +2}). Não é o efeito da bolsa, nem do PMM-E sobre o
município. Os outcomes são cadastros no CNES: vínculo cadastrado não é presença nem retenção.

Entradas (todas versionadas): `P6_amostra.parquet`, `P6_celulas.csv`, `P6_cobertura_mensal.csv` e
`P6_passo0_resumo.json`, gravados pelo script 30 a partir do cache privado. Este script não lê o cache.

Especificações (§4)
-------------------
- R1 (principal): diferença de médias r ∈ {+1, +2} contra r ∈ {−1, −2} com efeito fixo de célula (regressão no
  indicador de r > 0 com as variáveis centradas na célula); p por permutação do indicador dentro da célula (999,
  semente 20261019); IC 95% com EP agrupado por célula (CR1, graus de liberdade sem os efeitos fixos).
- R2: Wald = forma reduzida ÷ primeiro estágio (D = alocado na 1ª opção), mesma amostra; EP agrupado pela
  linearização do estimador de VI com efeito fixo; p de Anderson–Rubin = p da permutação do R1.
- R3: tendência linear em r de cada lado, efeito fixo de célula, EP agrupado, r ∈ [−3, +3] sem 0.
- R4: inclui r = 0; indicador de tratamento = r > 0 ou (r = 0 e ganhou o desempate), com indicador de r = 0.
- R5: R1 com a ligação só por nome.
- R6: escore de propensão do mecanismo — não executado (motivo no CSV e no doc).
Balanço: R1 nas covariáveis pré e na taxa de ligação ao CNES. Família do BKY e do Holm: R1, regra principal, Y1–Y5
× {último mês, média do seguimento} (10 testes), fixada antes de abrir os outcomes.

Uso
---
    python3 scripts/rdd_bolsa/31_rd_mecanismo.py
    python3 scripts/rdd_bolsa/31_rd_mecanismo.py --atualizar-doc
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
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
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    sys.dont_write_bytecode = bytecode
    return mod


L = _importar(DIR_RDD / "rdd_lib.py", "rdd_lib_p6")
P0 = _importar(DIR_RDD / "30_mecanismo_alocacao.py", "passo0_p6")

OUT = ROOT / "output" / "rdd_bolsa"
NOME_EST = "P6_estimativas.csv"
NOME_RESUMO = "P6_resumo.json"
DIR_FIG = "P6_figuras"
DOC = ROOT / "docs" / "06_execucao" / "57f_resultados_P6_mecanismo.md"
PROTOCOLO_MD = P0.PROTOCOLO_MD

DATA_EXECUCAO = P0.DATA_EXECUCAO
ESTATUTO = P0.ESTATUTO
NATUREZA = P0.NATUREZA
REGRAS = P0.REGRAS
ROTULO_REGRA = P0.ROTULO_REGRA
B_PERM = 999
SEMENTE = 20261019
JANELA_R1 = (-2, -1, 1, 2)
JANELA_R3 = (-3, -2, -1, 1, 2, 3)
JANELA_R4 = (-2, -1, 0, 1, 2)
R_FIGURA = tuple(range(-3, 4))
F_LIMIAR_T63 = 10.0
Z = L.Z_975
MEDIDAS = {"ultimo": "último mês (202608)", "media": "média dos meses de seguimento"}
OUTCOMES = P0.OUTCOMES
ROT_Y = {c: f"{i}: {r}" for c, i, r, _ in OUTCOMES}
UNI_Y = {c: u for c, _, _, u in OUTCOMES}
COVS = P0.COVARIAVEIS
ROT_COV = {c: r for c, r, _ in COVS} | {"ligado": "ligado ao CNES pelo G1"}
UNI_COV = {c: u for c, _, u in COVS} | {"ligado": "fração"}

COLUNAS = ["especificacao", "regra_ligacao", "amostra", "outcome", "medida", "r", "estimativa", "ep", "ic95_inf",
           "ic95_sup", "p_valor", "tipo_p", "p_perm", "p_cluster", "q_bky", "p_holm", "entra_familia", "n_obs",
           "n_acima", "n_abaixo", "n_celulas", "n_celulas_dois_lados", "estatistica_f", "unidade", "status", "nota",
           "leitura", "natureza_dos_dados", "estatuto"]

LEITURA = {
    "PE_por_r": "descritivo (proporção alocada por valor de r)",
    "PE": "primeiro estágio (R1 aplicado ao tratamento)",
    "BAL": "balanço de covariáveis pré-determinadas (R1); exploratório",
    "R1": "efeito de ser alocado perto do corte (forma reduzida, randomização local); exploratório",
    "R2": "efeito de ser alocado para os que obedecem à alocação (Wald); exploratório",
    "R3": "robustez com tendência linear em r; exploratório",
    "R4": "sensibilidade com os empatados no corte (desempate determinístico); exploratório",
    "R5": "sensibilidade com a ligação só por nome; exploratório",
    "R6": "não executado",
    "T6.3": "não executado",
    "medias_por_r": "descritivo (médias por valor de r, sem efeito fixo)",
}


class FalhaValidacao(RuntimeError):
    """Conferência de integridade que falhou: o script para sem gravar."""


rotulo = P0.rotulo
sha256 = P0.sha256
gravar_json = P0.gravar_json
_nan_none = P0._nan_none


def nova_linha(**kw) -> dict:
    base = {c: np.nan for c in COLUNAS}
    base.update({"entra_familia": False, "status": "EXECUTADO", "nota": "", "tipo_p": "",
                 "natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO})
    base.update(kw)
    if not isinstance(base.get("leitura"), str) or not base["leitura"]:
        base["leitura"] = LEITURA.get(str(base["especificacao"]), "")
    return base


# ---------------------------------------------------------------------------
# 1. Estimadores
# ---------------------------------------------------------------------------

def _centrar(x: np.ndarray, cel: np.ndarray) -> np.ndarray:
    s = pd.Series(x).groupby(cel).transform("mean").to_numpy()
    return x - s


def _cr1(score_g: np.ndarray, n: int, k: int) -> float:
    G = score_g.shape[0]
    return (G / (G - 1)) * ((n - 1) / (n - k)) if G > 1 and n > k else np.nan


def r1(y: np.ndarray, z: np.ndarray, cel: np.ndarray, *, b_perm: int = B_PERM, semente: int = SEMENTE,
       permutar: bool = True) -> dict:
    """Diferença de médias com efeito fixo de célula, EP CR1 por célula e p por permutação dentro da célula.

    Só as células com os dois lados identificam o efeito; as demais são contadas e saem (não mudam a estimativa)."""
    y, z, cel = np.asarray(y, float), np.asarray(z, float), np.asarray(cel).astype(str)
    ok = np.isfinite(y) & np.isfinite(z)
    y, z, cel = y[ok], z[ok], cel[ok]
    out = {"n_obs": int(y.size), "n_acima": int((z == 1).sum()), "n_abaixo": int((z == 0).sum()),
           "n_celulas": int(len(set(cel))), "estimativa": np.nan, "ep": np.nan, "p_cluster": np.nan,
           "p_perm": np.nan, "n_celulas_dois_lados": 0, "nota": ""}
    if y.size == 0:
        out["nota"] = "sem observações"
        return out
    zm = pd.Series(z).groupby(cel).agg(["min", "max"])
    dois = set(zm.index[(zm["min"] == 0) & (zm["max"] == 1)])
    out["n_celulas_dois_lados"] = len(dois)
    m = np.array([c in dois for c in cel])
    if m.sum() < 2 or len(dois) < 2:
        out["nota"] = f"menos de 2 células com os dois lados ({len(dois)})"
        return out
    y, z, cel = y[m], z[m], cel[m]
    out["n_acima"], out["n_abaixo"] = int((z == 1).sum()), int((z == 0).sum())   # só células com os dois lados
    yt, zt = _centrar(y, cel), _centrar(z, cel)
    szz = float(zt @ zt)
    tau = float(zt @ yt) / szz
    e = yt - tau * zt
    _, idx = np.unique(cel, return_inverse=True)
    G = int(idx.max()) + 1
    sg = np.zeros(G)
    np.add.at(sg, idx, zt * e)
    v = float(sg @ sg) / szz ** 2 * _cr1(sg[:, None], y.size, 1)
    ep = math.sqrt(v) if v > 0 else np.nan
    out.update(estimativa=tau, ep=ep, p_cluster=L.p_normal(tau / ep) if ep and np.isfinite(ep) else np.nan,
               n_obs_efetivo=int(y.size))
    if permutar:
        rng = np.random.default_rng(semente)
        grupos = [np.flatnonzero(idx == g) for g in range(G)]
        zb = z.copy()
        cont = 0
        for _ in range(b_perm):
            for gi in grupos:
                zb[gi] = z[gi][rng.permutation(gi.size)]
            tb = float(_centrar(zb, cel) @ yt) / szz
            cont += abs(tb) >= abs(tau) - 1e-12
        out["p_perm"] = (1 + cont) / (b_perm + 1)
    return out


def wald(y: np.ndarray, d: np.ndarray, z: np.ndarray, cel: np.ndarray) -> dict:
    """VI com efeito fixo de célula (instrumento z, tratamento d), EP CR1 por célula."""
    y, d, z, cel = (np.asarray(y, float), np.asarray(d, float), np.asarray(z, float), np.asarray(cel).astype(str))
    ok = np.isfinite(y) & np.isfinite(d) & np.isfinite(z)
    y, d, z, cel = y[ok], d[ok], z[ok], cel[ok]
    zm = pd.Series(z).groupby(cel).agg(["min", "max"])
    dois = set(zm.index[(zm["min"] == 0) & (zm["max"] == 1)])
    m = np.array([c in dois for c in cel])
    out = {"n_obs": int(ok.sum()), "n_acima": int((z == 1).sum()), "n_abaixo": int((z == 0).sum()),
           "n_celulas": int(len(set(cel))), "n_celulas_dois_lados": len(dois), "estimativa": np.nan, "ep": np.nan,
           "p_cluster": np.nan, "primeiro_estagio": np.nan, "nota": ""}
    if len(dois) < 2:
        out["nota"] = "menos de 2 células com os dois lados"
        return out
    y, d, z, cel = y[m], d[m], z[m], cel[m]
    out["n_acima"], out["n_abaixo"] = int((z == 1).sum()), int((z == 0).sum())
    yt, dt, zt = _centrar(y, cel), _centrar(d, cel), _centrar(z, cel)
    szd = float(zt @ dt)
    if abs(szd) < 1e-12:
        out["nota"] = "primeiro estágio nulo"
        return out
    beta = float(zt @ yt) / szd
    u = yt - beta * dt
    _, idx = np.unique(cel, return_inverse=True)
    G = int(idx.max()) + 1
    sg = np.zeros(G)
    np.add.at(sg, idx, zt * u)
    v = float(sg @ sg) / szd ** 2 * _cr1(sg[:, None], y.size, 1)
    ep = math.sqrt(v) if v > 0 else np.nan
    out.update(estimativa=beta, ep=ep, p_cluster=L.p_normal(beta / ep) if ep and np.isfinite(ep) else np.nan,
               primeiro_estagio=szd / float(zt @ zt))
    return out


def regressao_fe(y: np.ndarray, X: np.ndarray, nomes: list[str], cel: np.ndarray) -> dict:
    """MQO com efeito fixo de célula (centragem) e EP CR1 por célula (rdd_lib.mqp_sanduiche); coef. da 1ª coluna."""
    y, X, cel = np.asarray(y, float), np.asarray(X, float), np.asarray(cel).astype(str)
    ok = np.isfinite(y) & np.isfinite(X).all(axis=1)
    y, X, cel = y[ok], X[ok], cel[ok]
    out = {"n_obs": int(y.size), "n_celulas": int(len(set(cel))), "estimativa": np.nan, "ep": np.nan,
           "p_cluster": np.nan, "nota": ""}
    if y.size < 3:
        out["nota"] = "observações insuficientes"
        return out
    yt = _centrar(y, cel)
    Xt = np.column_stack([_centrar(X[:, j], cel) for j in range(X.shape[1])])
    fit = L.mqp_sanduiche(Xt, yt, np.ones(y.size), nomes=nomes, protegidas={nomes[0]}, cluster=cel)
    if "erro" in fit:
        out["nota"] = fit["erro"]
        return out
    j = fit["nomes"].index(nomes[0])
    b = float(fit["beta"][j])
    ep = float(math.sqrt(fit["V"][j, j]))
    out.update(estimativa=b, ep=ep, p_cluster=L.p_normal(b / ep) if ep > 0 else np.nan, n_celulas=int(fit["G"]),
               descartadas=fit["descartadas"])
    if fit["descartadas"]:
        out["nota"] = "colunas descartadas por colinearidade: " + ", ".join(fit["descartadas"])
    return out


# ---------------------------------------------------------------------------
# 2. Especificações
# ---------------------------------------------------------------------------

def ler_amostra() -> pd.DataFrame:
    am = pd.read_parquet(OUT / P0.ARQ_AMOSTRA.name)
    if not ((am["natureza_dos_dados"] == NATUREZA).all() and (am["estatuto"] == ESTATUTO).all()):
        raise FalhaValidacao("amostra sem rótulo")
    am["z"] = (am["r"] > 0).astype(float)
    return am


def _janela(am: pd.DataFrame, regra: str, janela: tuple[int, ...], ligados: bool = True) -> pd.DataFrame:
    d = am[(am["regra_ligacao"] == regra) & am["r"].isin(janela)]
    if ligados:
        d = d[d["ligado"] == 1]
    return d.reset_index(drop=True)


def _ic(est: float, ep: float) -> tuple[float, float]:
    if not (np.isfinite(est) and np.isfinite(ep)):
        return np.nan, np.nan
    return est - Z * ep, est + Z * ep


def linha_r1(res: dict, **kw) -> dict:
    lo, hi = _ic(res["estimativa"], res["ep"])
    st = "EXECUTADO" if np.isfinite(res["estimativa"]) else "SEM_ESTIMATIVA"
    p = res.get("p_perm", np.nan)
    return nova_linha(estimativa=res["estimativa"], ep=res["ep"], ic95_inf=lo, ic95_sup=hi,
                      p_valor=p if np.isfinite(p) else res["p_cluster"],
                      tipo_p="permutação dentro da célula (999)" if np.isfinite(p) else "normal, EP agrupado",
                      p_perm=p, p_cluster=res["p_cluster"], n_obs=res["n_obs"], n_acima=res.get("n_acima"),
                      n_abaixo=res.get("n_abaixo"), n_celulas=res.get("n_celulas"),
                      n_celulas_dois_lados=res.get("n_celulas_dois_lados"), status=st,
                      nota=L._juntar_notas(res.get("nota", ""), "IC 95% com EP agrupado por célula (CR1)"), **kw)


def primeiro_estagio(am: pd.DataFrame) -> list[dict]:
    linhas = []
    r0 = REGRAS[0]
    for amostra, lig in (("ligados", True), ("todos", False)):
        d = am[am["regra_ligacao"] == r0]
        if lig:
            d = d[d["ligado"] == 1]
        for r in sorted(d["r"].unique()):
            g = d[d["r"] == r]
            for t in ("d_alocado_1a_opcao", "d_alocado_pmme"):
                k, n = int(g[t].sum()), int(len(g))
                p, lo, hi = _wilson(k, n)
                linhas.append(nova_linha(especificacao="PE_por_r", regra_ligacao=r0, amostra=amostra, outcome=t,
                                         medida="fracao", r=int(r), estimativa=p, ic95_inf=lo, ic95_sup=hi,
                                         n_obs=n, unidade="fração", nota=f"{k} de {n}; IC de Wilson"))
        dj = d[d["r"].isin(JANELA_R1)]
        for t in ("d_alocado_1a_opcao", "d_alocado_pmme"):
            res = r1(dj[t].to_numpy(float), dj["z"].to_numpy(), dj["celula"].to_numpy(), permutar=False)
            lin = linha_r1(res, especificacao="PE", regra_ligacao=r0, amostra=amostra, outcome=t, medida="R1",
                           unidade="fração")
            f = (res["estimativa"] / res["ep"]) ** 2 if np.isfinite(res["ep"]) and res["ep"] > 0 else np.nan
            lin["estatistica_f"] = f
            if not np.isfinite(f):
                lin["nota"] = L._juntar_notas(lin["nota"], "EP zero ou indefinido: primeiro estágio determinístico "
                                                           "na janela (F não definido)")
            linhas.append(lin)
    return linhas


def _wilson(k: int, n: int) -> tuple[float, float, float]:
    if n == 0:
        return np.nan, np.nan, np.nan
    p = k / n
    d = 1 + Z ** 2 / n
    c = (p + Z ** 2 / (2 * n)) / d
    h = Z * math.sqrt(p * (1 - p) / n + Z ** 2 / (4 * n ** 2)) / d
    return p, c - h, c + h


def balanco(am: pd.DataFrame) -> list[dict]:
    linhas = []
    r0 = REGRAS[0]
    d = _janela(am, r0, JANELA_R1)
    for c, _, u in COVS:
        res = r1(d[c].to_numpy(float), d["z"].to_numpy(), d["celula"].to_numpy())
        lin = linha_r1(res, especificacao="BAL", regra_ligacao=r0, amostra="ligados", outcome=c, medida="R1",
                       unidade=u)
        for lado, zv in (("acima", 1.0), ("abaixo", 0.0)):
            x = d.loc[d["z"] == zv, c].to_numpy(float)
            x = x[np.isfinite(x)]
            lin[f"nota"] = L._juntar_notas(lin["nota"], f"média {lado} (bruta) = {x.mean():.4g}" if x.size else
                                           f"sem observação {lado}")
        linhas.append(lin)
    dt = _janela(am, r0, JANELA_R1, ligados=False)
    for regra in REGRAS:
        dt = _janela(am, regra, JANELA_R1, ligados=False)
        res = r1(dt["ligado"].astype(float).to_numpy(), dt["z"].to_numpy(), dt["celula"].to_numpy())
        lin = linha_r1(res, especificacao="BAL", regra_ligacao=regra, amostra="todos", outcome="ligado",
                       medida="R1", unidade="fração")
        linhas.append(lin)
        for lado, zv in (("acima", 1.0), ("abaixo", 0.0)):
            g = dt[dt["z"] == zv]
            k, n = int(g["ligado"].sum()), int(len(g))
            p, lo, hi = _wilson(k, n)
            linhas.append(nova_linha(especificacao="BAL", regra_ligacao=regra, amostra="todos", outcome="ligado",
                                     medida=f"taxa_{lado}", estimativa=p, ic95_inf=lo, ic95_sup=hi, n_obs=n,
                                     unidade="fração", nota=f"{k} de {n}; IC de Wilson; sem efeito fixo",
                                     leitura="descritivo (taxa de ligação por lado)"))
    return linhas


def outcomes(am: pd.DataFrame) -> list[dict]:
    linhas = []
    r0 = REGRAS[0]
    d1 = _janela(am, r0, JANELA_R1)
    d3 = _janela(am, r0, JANELA_R3)
    d4 = _janela(am, r0, JANELA_R4)
    d5 = _janela(am, REGRAS[1], JANELA_R1)
    if d4["r"].eq(0).any() and d4.loc[d4["r"] == 0, "ganhou_desempate"].isna().any():
        raise FalhaValidacao("empatado sem indicador de desempate")
    z4 = ((d4["r"] > 0) | ((d4["r"] == 0) & (d4["ganhou_desempate"] == 1))).astype(float).to_numpy()
    for col, _, _, u in OUTCOMES:
        for med in MEDIDAS:
            y = f"{col}_{med}"
            res = r1(d1[y].to_numpy(float), d1["z"].to_numpy(), d1["celula"].to_numpy())
            linhas.append(linha_r1(res, especificacao="R1", regra_ligacao=r0, amostra="ligados", outcome=col,
                                   medida=med, unidade=u, entra_familia=True))
            w = wald(d1[y].to_numpy(float), d1["d_alocado_1a_opcao"].to_numpy(float), d1["z"].to_numpy(),
                     d1["celula"].to_numpy())
            lo, hi = _ic(w["estimativa"], w["ep"])
            linhas.append(nova_linha(especificacao="R2", regra_ligacao=r0, amostra="ligados", outcome=col, medida=med,
                                     estimativa=w["estimativa"], ep=w["ep"], ic95_inf=lo, ic95_sup=hi,
                                     p_valor=res["p_perm"], tipo_p="Anderson–Rubin = permutação do R1",
                                     p_perm=res["p_perm"], p_cluster=w["p_cluster"], n_obs=w["n_obs"],
                                     n_acima=w["n_acima"], n_abaixo=w["n_abaixo"], n_celulas=w["n_celulas"],
                                     n_celulas_dois_lados=w["n_celulas_dois_lados"], unidade=u,
                                     status="EXECUTADO" if np.isfinite(w["estimativa"]) else "SEM_ESTIMATIVA",
                                     nota=L._juntar_notas(w["nota"], f"primeiro estágio na amostra = "
                                                          f"{w['primeiro_estagio']:.4g}; IC 95% com EP agrupado")))
            r = d3["r"].to_numpy(float)
            z3 = d3["z"].to_numpy(float)
            g3 = regressao_fe(d3[y].to_numpy(float), np.column_stack([z3, r, z3 * r]), ["acima", "r", "acima_x_r"],
                              d3["celula"].to_numpy())
            lo, hi = _ic(g3["estimativa"], g3["ep"])
            linhas.append(nova_linha(especificacao="R3", regra_ligacao=r0, amostra="ligados", outcome=col, medida=med,
                                     estimativa=g3["estimativa"], ep=g3["ep"], ic95_inf=lo, ic95_sup=hi,
                                     p_valor=g3["p_cluster"], tipo_p="normal, EP agrupado", p_cluster=g3["p_cluster"],
                                     n_obs=g3["n_obs"], n_acima=int((z3 == 1).sum()), n_abaixo=int((z3 == 0).sum()),
                                     n_celulas=g3["n_celulas"], unidade=u,
                                     status="EXECUTADO" if np.isfinite(g3["estimativa"]) else "SEM_ESTIMATIVA",
                                     nota=L._juntar_notas(g3["nota"], "r ∈ [−3, +3] sem 0; salto no corte entre "
                                                          "as retas de cada lado")))
            e0 = (d4["r"] == 0).astype(float).to_numpy()
            g4 = regressao_fe(d4[y].to_numpy(float), np.column_stack([z4, e0]), ["tratado", "empatado"],
                              d4["celula"].to_numpy())
            lo, hi = _ic(g4["estimativa"], g4["ep"])
            linhas.append(nova_linha(especificacao="R4", regra_ligacao=r0, amostra="ligados", outcome=col, medida=med,
                                     estimativa=g4["estimativa"], ep=g4["ep"], ic95_inf=lo, ic95_sup=hi,
                                     p_valor=g4["p_cluster"], tipo_p="normal, EP agrupado", p_cluster=g4["p_cluster"],
                                     n_obs=g4["n_obs"], n_acima=int((z4 == 1).sum()), n_abaixo=int((z4 == 0).sum()),
                                     n_celulas=g4["n_celulas"], unidade=u,
                                     status="EXECUTADO" if np.isfinite(g4["estimativa"]) else "SEM_ESTIMATIVA",
                                     nota=L._juntar_notas(g4["nota"], "r ∈ [−2, +2]; tratado = r > 0 ou empatado que "
                                                          "ganhou o desempate (UF, idade: regra fixa, não sorteio)")))
            res5 = r1(d5[y].to_numpy(float), d5["z"].to_numpy(), d5["celula"].to_numpy())
            linhas.append(linha_r1(res5, especificacao="R5", regra_ligacao=REGRAS[1], amostra="ligados", outcome=col,
                                   medida=med, unidade=u))
    for col, _, _, u in OUTCOMES:
        for med in MEDIDAS:
            linhas.append(nova_linha(especificacao="R6", regra_ligacao=r0, amostra="ligados", outcome=col,
                                     medida=med, unidade=u, status="NAO_EXECUTADO",
                                     nota=MOTIVO_R6))
    linhas.append(nova_linha(especificacao="T6.3", regra_ligacao=r0, amostra="-", outcome="municipio", medida="-",
                             status="NAO_EXECUTADO", nota=MOTIVO_T63))
    return linhas


MOTIVO_R6 = ("o escore de propensão do mecanismo (Abdulkadiroğlu et al., 2017) pressupõe desempate por sorteio ou um "
             "escore contínuo com banda; aqui a nota é inteira e o desempate é regra fixa (UF, idade), e com até duas "
             "opções e a prioridade da 1ª opção o escore local da 1ª opção vale 0 abaixo, 1 acima e é indefinido no "
             "empate: coincide com o R1 e não é uma forma de cálculo distinta e estável (§4: 'se a forma de calcular "
             "for estável')")
MOTIVO_T63 = ("o §4 diz que o T6.3 não roda neste protocolo; só entra depois, se o primeiro estágio do R1 for forte "
              "(F > 10) e houver células suficientes")


def medias_por_r(am: pd.DataFrame) -> list[dict]:
    linhas = []
    r0 = REGRAS[0]
    d = am[(am["regra_ligacao"] == r0) & am["r"].isin(R_FIGURA)]
    dl = d[d["ligado"] == 1]
    vars_ = ([(f"{c}_{m}", u, "ligados") for c, _, _, u in OUTCOMES for m in MEDIDAS]
             + [(c, u, "ligados") for c, _, u in COVS] + [("ligado", "fração", "todos")])
    for v, u, amostra in vars_:
        base = dl if amostra == "ligados" else d
        for r in R_FIGURA:
            x = base.loc[base["r"] == r, v].astype(float).to_numpy()
            x = x[np.isfinite(x)]
            n = x.size
            mu = float(x.mean()) if n else np.nan
            ep = float(x.std(ddof=1) / math.sqrt(n)) if n > 1 else np.nan
            lo, hi = _ic(mu, ep)
            linhas.append(nova_linha(especificacao="medias_por_r", regra_ligacao=r0, amostra=amostra, outcome=v,
                                     medida="media", r=r, estimativa=mu, ep=ep, ic95_inf=lo, ic95_sup=hi, n_obs=n,
                                     unidade=u, status="EXECUTADO" if n else "SEM_ESTIMATIVA",
                                     nota="sem efeito fixo de célula; r = 0 fora do R1" if n else
                                     "nenhum candidato com esse r"))
    return linhas


def aplicar_familia(est: pd.DataFrame) -> pd.DataFrame:
    est = est.copy()
    sel = est["entra_familia"].astype(bool) & (est["status"] == "EXECUTADO")
    est.loc[sel, "q_bky"] = L.qvalores_bky(est.loc[sel, "p_valor"].to_numpy(float))
    est.loc[sel, "p_holm"] = L.holm(est.loc[sel, "p_valor"].to_numpy(float))
    return est


# ---------------------------------------------------------------------------
# 3. Figuras (sem texto embutido; legenda simples; "Como ler" no doc e no resumo)
# ---------------------------------------------------------------------------

COR = ["#2a78d6", "#eb6834", "#1baf7a"]
COR_TEXTO = "#52514e"
COMO_LER = {
    "P6_primeiro_estagio.png": "Cada ponto é a fração de candidatos alocados na 1ª opção (azul) e em qualquer célula "
                               "(laranja) para cada distância r da nota de corte. À direita do zero, a nota passou "
                               "do corte; r = 0 são os empatados, decididos por regra fixa.",
    "P6_outcomes_media.png": "Média de cada outcome nos meses de seguimento, por r, entre os candidatos ligados ao "
                             "CNES. Um degrau entre r = −1 e r = +1 sugere efeito de ser alocado; barras são IC de "
                             "95% sem efeito fixo de célula.",
    "P6_outcomes_ultimo.png": "Mesma leitura, com o valor de cada outcome no último mês, 202608.",
    "P6_balanco.png": "Covariáveis de antes do programa e taxa de ligação ao CNES, por r. Sem diferença entre os "
                      "dois lados do corte, a comparação dos outcomes é mais crível.",
}
DESCRICAO_FIGURAS = {
    "P6_primeiro_estagio.png": "Primeiro estágio: alocação por r (regra principal, todos os candidatos)",
    "P6_outcomes_media.png": "Outcomes Y1–Y5, média do seguimento, por r (regra principal)",
    "P6_outcomes_ultimo.png": "Outcomes Y1–Y5 em 202608, por r (regra principal)",
    "P6_balanco.png": "Balanço: covariáveis pré e taxa de ligação, por r (regra principal)",
}


def _eixo(ax, ylabel: str, xlabel: str = "r = nota − nota de corte") -> None:
    ax.axvline(0, color="#b5b4ae", ls="--", lw=0.8, zorder=0)
    ax.grid(axis="y", color="#e6e5e0", lw=0.6)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.set_ylabel(ylabel, color=COR_TEXTO, fontsize=9)
    ax.set_xlabel(xlabel, color=COR_TEXTO, fontsize=9)
    ax.tick_params(colors=COR_TEXTO, labelsize=8)
    ax.set_xticks(list(R_FIGURA))
    ax.set_axisbelow(True)


def _sel(est: pd.DataFrame, **f) -> pd.DataFrame:
    s = est
    for k, v in f.items():
        s = s[s[k] == v]
    return s


def gerar_figuras(est: pd.DataFrame, dir_fig: Path) -> list[dict]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "DejaVu Sans", "svg.hashsalt": "p6"})
    dir_fig.mkdir(parents=True, exist_ok=True)
    figs = []

    def salvar(fig, nome):
        caminho = dir_fig / nome
        fig.savefig(caminho, dpi=150, bbox_inches="tight", metadata={"Software": None})
        plt.close(fig)
        figs.append({"arquivo": rotulo(caminho), "descricao": DESCRICAO_FIGURAS[nome], "como_ler": COMO_LER[nome]})

    def pontos(ax, s, cor, rot=None, desloc=0.0):
        s = s[s["status"] == "EXECUTADO"].sort_values("r")
        x = s["r"].to_numpy(float) + desloc
        y = s["estimativa"].to_numpy(float)
        lo = (s["estimativa"] - s["ic95_inf"]).fillna(0).to_numpy(float)
        hi = (s["ic95_sup"] - s["estimativa"]).fillna(0).to_numpy(float)
        cheio = s["r"].to_numpy() != 0
        ax.errorbar(x[cheio], y[cheio], yerr=[lo[cheio], hi[cheio]], fmt="o", ms=4, color=cor, ecolor=cor,
                    elinewidth=1.1, capsize=0, label=rot)
        if (~cheio).any():
            ax.errorbar(x[~cheio], y[~cheio], yerr=[lo[~cheio], hi[~cheio]], fmt="o", ms=4, mfc="white", color=cor,
                        ecolor=cor, elinewidth=1.1, capsize=0)

    fig, ax = plt.subplots(figsize=(5.5, 3.4))
    pe = _sel(est, especificacao="PE_por_r", amostra="todos")
    pe = pe[pe["r"].isin(R_FIGURA)]
    pontos(ax, _sel(pe, outcome="d_alocado_1a_opcao"), COR[0], "alocado na 1ª opção", -0.08)
    pontos(ax, _sel(pe, outcome="d_alocado_pmme"), COR[1], "alocado em qualquer célula", 0.08)
    _eixo(ax, "fração alocada")
    ax.set_ylim(-0.05, 1.05)
    ax.legend(frameon=False, fontsize=8, loc="center right")
    salvar(fig, "P6_primeiro_estagio.png")

    for med, nome in (("media", "P6_outcomes_media.png"), ("ultimo", "P6_outcomes_ultimo.png")):
        fig, axs = plt.subplots(1, 5, figsize=(14, 3.0))
        for ax, (col, i, r, u) in zip(axs, OUTCOMES):
            pontos(ax, _sel(est, especificacao="medias_por_r", outcome=f"{col}_{med}"), COR[0])
            _eixo(ax, f"{i} ({u})")
        fig.tight_layout()
        salvar(fig, nome)

    fig, axs = plt.subplots(1, 5, figsize=(14, 3.0))
    for ax, (c, u) in zip(axs, [(c, u) for c, _, u in COVS] + [("ligado", "fração")]):
        pontos(ax, _sel(est, especificacao="medias_por_r", outcome=c), COR[2])
        _eixo(ax, f"{ROT_COV[c]} ({u})" if len(ROT_COV[c]) < 28 else f"{c.replace('cov_', '')} ({u})")
    fig.tight_layout()
    salvar(fig, "P6_balanco.png")
    for f in figs:
        f["sha256"] = sha256(ROOT / f["arquivo"])
    return figs


# ---------------------------------------------------------------------------
# 4. Documento 57f, gerado inteiro a partir das saídas
# ---------------------------------------------------------------------------

def _n(v, casas: int = 1, sinal: bool = False) -> str:
    if v is None or (isinstance(v, float) and not np.isfinite(v)) or pd.isna(v):
        return "—"
    s = f"{v:+,.{casas}f}" if sinal else f"{v:,.{casas}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def _pct(v, casas: int = 1) -> str:
    return "—" if v is None or pd.isna(v) or not np.isfinite(v) else _n(100 * v, casas) + "%"


def _i(v) -> str:
    return "—" if v is None or pd.isna(v) else _n(float(v), 0)


def _p(v) -> str:
    if v is None or pd.isna(v):
        return "—"
    return "< 0,001" if v < 0.001 else _n(v, 3)


def _casas(u: str) -> int:
    return 1 if u in ("h/sem", "km") else 3


def _ic_txt(r, casas: int) -> str:
    if pd.isna(r["ic95_inf"]):
        return "—"
    return f"[{_n(r['ic95_inf'], casas, True)}; {_n(r['ic95_sup'], casas, True)}]"


def _tab(cab: list[str], linhas: list[list[str]]) -> str:
    return "\n".join(["| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)]
                     + ["| " + " | ".join(l) + " |" for l in linhas])


def _um(est, **f) -> pd.Series:
    s = _sel(est, **f)
    if len(s) != 1:
        raise FalhaValidacao(f"esperada uma linha para {f}, há {len(s)}")
    return s.iloc[0]


def tabela_celulas(p0: dict) -> str:
    cm = p0["contagens"]["celulas_por_motivo"]
    motivos = sorted({m for k in cm for m in cm[k]})
    linhas = [[m, _i(cm.get("1", {}).get(m, 0)), _i(cm.get("2", {}).get(m, 0))] for m in motivos]
    return _tab(["Motivo", "Ciclo 1", "Ciclo 2"], linhas)


def tabela_candidatos(p0: dict) -> str:
    c = p0["contagens"]["candidatos"]
    itens = [("candidatos_1a_chamada", "candidatos da 1ª chamada"),
             ("nao_elegiveis_sem_pontuacao", "sem pontuação (sem pré-requisito)"),
             ("1a_opcao_fora_das_celulas_elegiveis", "1ª opção fora das células elegíveis"),
             ("inscritos_em_reserva_na_celula_elegivel", "inscritos em reserva (ER, PCD) na célula elegível"),
             ("sub_judice_na_celula_elegivel", "sub judice na célula elegível"),
             ("no_universo_p6", "no universo do P6 (ampla concorrência, célula elegível)")]
    return _tab(["Etapa", "Ciclo 1", "Ciclo 2"], [[r, _i(c["1"][k]), _i(c["2"][k])] for k, r in itens])


def tabela_janela(am: pd.DataFrame) -> str:
    linhas = []
    for regra in REGRAS:
        d = am[am["regra_ligacao"] == regra]
        for r in sorted(d["r"].unique()):
            g = d[d["r"] == r]
            linhas.append([ROTULO_REGRA[regra], _i(r), _i(len(g)), _i(g["ligado"].sum()),
                           _pct(g["ligado"].mean()), _i(g["celula"].nunique())])
    return _tab(["Regra", "r", "Candidatos", "Ligados", "Taxa de ligação", "Células"], linhas)


def tabela_pe(est: pd.DataFrame) -> str:
    linhas = []
    s = _sel(est, especificacao="PE_por_r", amostra="todos")
    for r in sorted(s["r"].dropna().unique()):
        a = _um(s, r=r, outcome="d_alocado_1a_opcao")
        b = _um(s, r=r, outcome="d_alocado_pmme")
        linhas.append([_i(r), _i(a["n_obs"]), _pct(a["estimativa"]), _pct(b["estimativa"])])
    return _tab(["r", "Candidatos", "P(D = 1 | r): alocado na 1ª opção", "P(D' = 1 | r): alocado no PMM-E"],
                linhas)


def tabela_pe_r1(est: pd.DataFrame) -> str:
    linhas = []
    for amostra in ("todos", "ligados"):
        for t, rot in (("d_alocado_1a_opcao", "D (1ª opção)"), ("d_alocado_pmme", "D' (qualquer célula)")):
            r = _um(est, especificacao="PE", amostra=amostra, outcome=t)
            linhas.append([amostra, rot, _n(r["estimativa"], 3, True), _ic_txt(r, 3), _n(r["estatistica_f"], 1),
                           _i(r["n_acima"]), _i(r["n_abaixo"]), _i(r["n_celulas_dois_lados"])])
    return _tab(["Amostra", "Tratamento", "Salto (R1)", "IC 95%", "F", "Acima", "Abaixo", "Células com os dois lados"],
                linhas)


def tabela_balanco(est: pd.DataFrame) -> str:
    linhas = []
    for c, rot, u in COVS:
        r = _um(est, especificacao="BAL", amostra="ligados", outcome=c, medida="R1")
        linhas.append([rot, _n(r["estimativa"], _casas(u), True), _ic_txt(r, _casas(u)), _p(r["p_perm"]),
                       _i(r["n_obs"]), _i(r["n_celulas_dois_lados"])])
    for regra in REGRAS:
        r = _um(est, especificacao="BAL", regra_ligacao=regra, outcome="ligado", medida="R1")
        a = _um(est, especificacao="BAL", regra_ligacao=regra, outcome="ligado", medida="taxa_acima")
        b = _um(est, especificacao="BAL", regra_ligacao=regra, outcome="ligado", medida="taxa_abaixo")
        linhas.append([f"ligado ao CNES, {ROTULO_REGRA[regra]} (acima {_pct(a['estimativa'])}, abaixo "
                       f"{_pct(b['estimativa'])})", _n(r["estimativa"], 3, True), _ic_txt(r, 3), _p(r["p_perm"]),
                       _i(r["n_obs"]), _i(r["n_celulas_dois_lados"])])
    return _tab(["Covariável", "Diferença acima − abaixo (R1)", "IC 95%", "p (permutação)", "n",
                 "Células com os dois lados"], linhas)


def tabela_r1(est: pd.DataFrame) -> str:
    linhas = []
    for col, i, rot, u in OUTCOMES:
        for med in MEDIDAS:
            r = _um(est, especificacao="R1", outcome=col, medida=med)
            linhas.append([f"{i}: {rot}", MEDIDAS[med], _n(r["estimativa"], _casas(u), True), _ic_txt(r, _casas(u)),
                           _p(r["p_perm"]), _n(r["q_bky"], 3), _n(r["p_holm"], 3), _i(r["n_acima"]),
                           _i(r["n_abaixo"])])
    return _tab(["Outcome", "Medida", "Efeito (R1)", "IC 95%", "p (permutação)", "q BKY", "p Holm", "Acima",
                 "Abaixo"], linhas)


def tabela_robustez(est: pd.DataFrame) -> str:
    linhas = []
    for col, i, rot, u in OUTCOMES:
        cel = [f"{i}"]
        for esp in ("R1", "R2", "R3", "R4", "R5"):
            r = _um(est, especificacao=esp, outcome=col, medida="media")
            cel.append(f"{_n(r['estimativa'], _casas(u), True)} {_ic_txt(r, _casas(u))}")
        linhas.append(cel)
    return _tab(["Outcome (média do seguimento)", "R1", "R2 (Wald)", "R3 (tendência)", "R4 (com empatados)",
                 "R5 (só nome)"], linhas)


def tabela_robustez_ultimo(est: pd.DataFrame) -> str:
    linhas = []
    for col, i, rot, u in OUTCOMES:
        cel = [f"{i}"]
        for esp in ("R1", "R2", "R3", "R4", "R5"):
            r = _um(est, especificacao=esp, outcome=col, medida="ultimo")
            cel.append(f"{_n(r['estimativa'], _casas(u), True)} {_ic_txt(r, _casas(u))}")
        linhas.append(cel)
    return _tab(["Outcome (202608)", "R1", "R2 (Wald)", "R3 (tendência)", "R4 (com empatados)", "R5 (só nome)"],
                linhas)


def tabela_cobertura(p0: dict) -> str:
    linhas = []
    for k, v in sorted(p0["cobertura_universo"].items()):
        regra, ciclo = k.split("|")
        linhas.append([ROTULO_REGRA[regra], ciclo, _i(v["candidatos_ligados"]), _pct(v["min"]), _pct(v["max"])])
    return _tab(["Regra", "Ciclo", "Ligados no universo", "Com vínculo médico: menor fração mensal",
                 "maior fração mensal"], linhas)


def leitura(est: pd.DataFrame, resumo: dict) -> str:
    fam = est[est["entra_familia"].astype(bool) & (est["status"] == "EXECUTADO")]
    n_p05 = int((fam["p_valor"] < 0.05).sum())
    n_holm = int((fam["p_holm"] < 0.05).sum())
    n_q = int((fam["q_bky"] <= 0.05).sum())
    pe = _um(est, especificacao="PE", amostra="ligados", outcome="d_alocado_1a_opcao")
    bal = est[(est["especificacao"] == "BAL") & (est["medida"] == "R1")]
    bal_rej = [f"{ROT_COV.get(o, o)} ({ROTULO_REGRA[g] if o == 'ligado' else 'regra principal'}, p = {_p(p)})"
               for o, g, p in zip(bal["outcome"], bal["regra_ligacao"], bal["p_perm"]) if pd.notna(p) and p < 0.05]
    lig = _um(est, especificacao="BAL", regra_ligacao=REGRAS[0], outcome="ligado", medida="R1")
    lig_a = _um(est, especificacao="BAL", regra_ligacao=REGRAS[0], outcome="ligado", medida="taxa_acima")
    lig_b = _um(est, especificacao="BAL", regra_ligacao=REGRAS[0], outcome="ligado", medida="taxa_abaixo")
    dist = _um(est, especificacao="BAL", outcome="cov_dist_km", medida="R1")
    am = resumo["amostra"]
    largura = []
    for col, i, rot, u in OUTCOMES:
        r = _um(est, especificacao="R1", outcome=col, medida="media")
        largura.append(f"{i} {_ic_txt(r, _casas(u))}")
    txt = [
        f"- **Amostra pequena.** A janela do R1 tem {_i(am['principal']['acima'])} candidatos ligados logo acima do "
        f"corte e {_i(am['principal']['abaixo'])} logo abaixo; o efeito vem só das "
        f"{_i(am['principal']['celulas_dois_lados'])} células com os dois lados, com "
        f"{_i(am['principal']['acima_efetivo'])} acima e {_i(am['principal']['abaixo_efetivo'])} abaixo. Os "
        "intervalos são largos: média do seguimento, " + "; ".join(largura) + ".",
        f"- **Primeiro estágio.** Na janela do R1, ser aprovado por pouco muda a alocação na 1ª opção em "
        f"{_n(pe['estimativa'], 3, True)} (fração): a regra é cumprida, porque o corte vem da própria alocação "
        "publicada. Por isso o R2 (Wald) repete o R1.",
        f"- **Outcomes.** Na família do R1 (Y1–Y5 × último mês e média, {_i(len(fam))} testes), {_i(n_p05)} têm p de "
        f"permutação < 0,05, {_i(n_holm)} rejeitam zero depois do Holm e {_i(n_q)} têm q de BKY ≤ 0,05.",
        "- **Balanço.** " + ("Nenhuma covariável pré nem a taxa de ligação tem diferença com p < 0,05 entre os lados."
                             if not bal_rej else "Diferença com p < 0,05 em: " + "; ".join(bal_rej) +
                             ". Nessas, os lados já diferiam antes da alocação e o contraste fica menos crível.")
        + f" Desequilíbrios declarados mesmo sem p < 0,05: a distância origem–1ª opção difere em "
          f"{_n(dist['estimativa'], 0, True)} km {_ic_txt(dist, 0)} (p = {_p(dist['p_perm'])}), com os de cima vindo "
          f"de {'mais longe' if dist['estimativa'] > 0 else 'mais perto'}; e a taxa de ligação ao CNES difere em {_n(lig['estimativa'], 3, True)} {_ic_txt(lig, 3)} "
          f"(p = {_p(lig['p_perm'])}; acima {_pct(lig_a['estimativa'])}, abaixo {_pct(lig_b['estimativa'])}). A "
          "ligação diferencial pode enviesar os outcomes, que só existem para os ligados.",
        "- **Y1 é quase mecânico.** Ser alocado num posto cria um vínculo cadastrado no município da 1ª opção; o "
        "salto em Y1 mostra que a alocação aparece no CNES, não que o médico fique ou trabalhe lá.",
        "- **O que o contraste identifica.** O efeito de SER ALOCADO na 1ª opção do PMM-E, para candidatos de ampla "
        "concorrência perto da nota de corte de células com corte efetivo, sobre a trajetória cadastrada no CNES. "
        "Não é o efeito da bolsa, nem o do PMM-E sobre a oferta do município, nem retenção: vínculo cadastrado não é "
        "presença.",
        "- **Validade externa.** As células elegíveis são as poucas com mais de uma vaga e corte abaixo da maior nota "
        "(todas com vaga reservada), quase todas do ciclo 2; o resultado não se estende às células de uma vaga.",
    ]
    return "\n".join(txt)


def gerar_doc(est: pd.DataFrame, resumo: dict, p0: dict, am: pd.DataFrame) -> str:
    figs = resumo["saidas"]["figuras"]
    rep = p0["reproducao_a16"]
    lg = p0["ligacao"]["reproducao_g1"]
    up = p0["universo_principal"]
    pr = resumo["amostra"]["principal"]
    partes = [
        "# 57f. Resultados do P6: alocado por pouco contra não alocado por pouco",
        "",
        f"> **Data:** {DATA_EXECUCAO}.<br>",
        "> **Protocolo:** [`56_protocolo_P6_mecanismo_alocacao.md`](56_protocolo_P6_mecanismo_alocacao.md), congelado "
        "em 19/10/2026 antes de ligar os candidatos ao painel CNES e de abrir outcomes.<br>",
        "> **Scripts:** `scripts/rdd_bolsa/30_mecanismo_alocacao.py` (amostra e passo 0) e "
        "`scripts/rdd_bolsa/31_rd_mecanismo.py` (estimação; gera este documento inteiro).<br>",
        "> **Saídas:** `output/rdd_bolsa/P6_amostra.parquet`, `P6_celulas.csv`, `P6_cobertura_mensal.csv`, "
        "`P6_passo0_resumo.json`, `P6_estimativas.csv`, `P6_resumo.json` e `P6_figuras/`.<br>",
        "> **Testes:** `tests/test_mecanismo_alocacao.py`.<br>",
        f"> **Estatuto:** `{ESTATUTO}`; toda linha tem `natureza_dos_dados = {NATUREZA}`.",
        "",
        "Este documento é gerado pelo script a partir de `output/`; não edite à mão. O teste confere que ele é igual "
        "ao que o script gera.",
        "",
        "## 1. O que se pergunta e o que o contraste identifica",
        "",
        "Perto da nota de corte de cada célula, quem passou por um ou dois pontos foi alocado e quem ficou um ou dois "
        "pontos abaixo não foi. Comparar os dois grupos mede o efeito de **ser alocado** sobre a trajetória "
        "cadastrada do médico no CNES.",
        "",
        "- **Não é o efeito da bolsa.** O contraste é ser alocado na 1ª opção do PMM-E, para candidatos de ampla "
        "concorrência perto do corte; a bolsa é a mesma para todos os alocados da mesma célula.",
        "- **Vínculo cadastrado não é presença nem retenção.** Os outcomes são cadastros no CNES (vínculo, horas "
        "cadastradas, municípios).",
        "- **Resultado exploratório.** O desempate no corte é regra fixa (UF, idade), não sorteio; a nota é inteira. "
        "O principal exclui os empatados (r = 0).",
        "",
        "## 2. Passo 0: cache privado, ligação e cobertura",
        "",
        "O cache privado do a16 e o dicionário do G1 não existiam neste ambiente e foram refeitos pelos próprios "
        "scripts, com os mesmos ZIPs do CNES (SHA-256 igual ao do a09 e ao do manifesto do a16). Os caminhos estão "
        "no `.gitignore`; nada com código do profissional, nome ou CPF sai do cache. Antes de usar o cache:",
        "",
        f"- a ligação da X1 refeita do cache reproduz `X1_medicos.parquet` em 100%, e o painel médico × mês do a16 "
        f"refeito é idêntico ao versionado ({_i(rep['linhas_painel_medico_mes'])} linhas);",
        "- a ligação dos candidatos pela regra do G1, refeita do cache, é idêntica a `G1_candidatos_origem.parquet` "
        "nas duas regras e nos três ciclos (" + "; ".join(
            f"{ROTULO_REGRA[k]}: {_i(v['ligados'])} ligados de {_i(v['candidatos'])}" for k, v in lg.items()) + ");",
        f"- o painel dos candidatos, montado em memória, tem horas e municípios iguais aos da agregação do a16 "
        f"({_i(p0['conferencia_agregacao_a16']['linhas_conferidas'])} candidato-mês conferidos).",
        "",
        "Cobertura mensal no universo do P6 (sem quebra por r): fração dos ligados com vínculo médico cadastrado em "
        "cada competência de 202406 a 202608. Detalhe em `P6_cobertura_mensal.csv`.",
        "",
        tabela_cobertura(p0),
        "",
        "## 3. Amostra",
        "",
        "Células dos ciclos 1 e 2 (1ª chamada) por motivo de exclusão. A unidade do corte é a célula × ampla "
        "concorrência (adendo de 23/10/2026, seção 11).",
        "",
        tabela_celulas(p0),
        "",
        f"Todas as {_i(p0['contagens']['celulas_elegiveis_com_vaga_reservada'])} células elegíveis têm vaga "
        "reservada; os inscritos em reserva ficam fora porque o corte das vagas reservadas não é reconstruído.",
        "",
        tabela_candidatos(p0),
        "",
        f"Universo do P6 (regra principal): {_i(up['candidatos'])} candidatos em {_i(up['celulas'])} células. "
        "Candidatos, ligação ao CNES e células por valor de r:",
        "",
        tabela_janela(am),
        "",
        f"Janela principal do R1 (r ∈ {{−2, −1, +1, +2}}, ligados, regra principal): {_i(pr['acima'])} acima e "
        f"{_i(pr['abaixo'])} abaixo, em {_i(pr['celulas'])} células, das quais {_i(pr['celulas_dois_lados'])} têm os "
        f"dois lados e identificam o efeito ({_i(pr['acima_efetivo'])} acima e {_i(pr['abaixo_efetivo'])} abaixo). "
        "Nas tabelas, as colunas Acima e Abaixo contam só essas células.",
        "",
        "## 4. Primeiro estágio",
        "",
        "P(D = 1 | r) entre todos os candidatos do universo (ligados ou não):",
        "",
        tabela_pe(est),
        "",
        "Salto na janela do R1, com efeito fixo de célula:",
        "",
        tabela_pe_r1(est),
        "",
        "Quando a alocação na janela é determinística (todos acima alocados, ninguém abaixo), o EP é zero e o F não "
        "se define; o T6.3 não roda neste protocolo de qualquer forma (seção 8).",
        "",
        "## 5. Balanço de covariáveis pré-determinadas",
        "",
        "R1 aplicado às covariáveis de antes do programa (candidatos ligados) e à taxa de ligação ao CNES (todos os "
        "candidatos da janela). p por permutação dentro da célula.",
        "",
        tabela_balanco(est),
        "",
        "## 6. Efeito de ser alocado (R1, principal)",
        "",
        "Diferença entre r ∈ {+1, +2} e r ∈ {−1, −2}, com efeito fixo de célula; candidatos ligados, regra principal. "
        "p por permutação dentro da célula (999, semente 20261019); IC 95% com EP agrupado por célula. q de BKY e p "
        "de Holm na família de 10 testes desta tabela.",
        "",
        tabela_r1(est),
        "",
        "## 7. Robustez e sensibilidades (R2–R5)",
        "",
        "Efeito e IC 95%. R2 = Wald (efeito para os que obedecem); R3 = tendência linear em r de cada lado, "
        "r ∈ [−3, +3] sem 0; R4 = inclui os empatados, com indicador do desempate; R5 = ligação só por nome.",
        "",
        tabela_robustez(est),
        "",
        tabela_robustez_ultimo(est),
        "",
        "## 8. O que não foi executado",
        "",
        f"- **R6 (escore de propensão do mecanismo).** {MOTIVO_R6[0].upper() + MOTIVO_R6[1:]}.",
        f"- **T6.3 (variação do mecanismo como instrumento no município).** "
        f"{MOTIVO_T63[0].upper() + MOTIVO_T63[1:]}.",
        "- **Homologação** como primeiro estágio (doc 51, T6.2) não está no protocolo 56 e não foi calculada.",
        "",
        "## 9. Figuras",
        "",
    ]
    for f in figs:
        nome = Path(f["arquivo"]).name
        partes += [f"### {f['descricao']}", "", f"![{nome}](../../{f['arquivo']})", "",
                   f"**Como ler.** {f['como_ler']}", ""]
    partes += ["## 10. Leitura", "", leitura(est, resumo), "", "## 11. Decisões e desvios", ""]
    partes += [f"- **{d['item']}** ({d['data']}). {d['descricao']}" for d in resumo["desvios"]]
    partes += ["", "## 12. Limitações", "",
               "- Poucas células têm corte efetivo: com uma vaga, o corte é a maior nota e ninguém fica acima dele.",
               "- O desempate no corte é regra fixa (UF de residência ou nascimento, idade); os candidatos logo acima "
               "e logo abaixo diferem em um ou dois pontos de barema, não por sorteio.",
               "- Candidatos não ligados ao CNES ficam fora dos outcomes; a diferença da taxa de ligação entre os "
               "lados está na seção 5.",
               "- Ser alocado na 1ª opção não impede quem ficou abaixo de ser alocado na 2ª opção (D' na seção 4).",
               "- O seguimento é curto (ciclo 2: 202604–202608) e só vai até 202608.",
               "- Cadastro no CNES não é trabalho efetivo; mudança cadastral não se distingue de mudança real.",
               ""]
    return "\n".join(partes)


def ler_saidas() -> tuple[pd.DataFrame, dict, dict, pd.DataFrame]:
    est = pd.read_csv(OUT / NOME_EST, keep_default_na=True)
    est["nota"] = est["nota"].fillna("")
    resumo = json.loads((OUT / NOME_RESUMO).read_text(encoding="utf-8"))
    p0 = json.loads(P0.ARQ_PASSO0.read_text(encoding="utf-8"))
    am = pd.read_parquet(P0.ARQ_AMOSTRA)
    return est, resumo, p0, am


def atualizar_doc() -> None:
    est, resumo, p0, am = ler_saidas()
    DOC.write_text(gerar_doc(est, resumo, p0, am), encoding="utf-8")
    print(f"doc gerado: {rotulo(DOC)}")


# ---------------------------------------------------------------------------
# 5. Execução
# ---------------------------------------------------------------------------

DESVIOS_31 = [
    {"data": "2026-10-23", "item": "Família do BKY e do Holm",
     "descricao": "O §5 pede BKY entre Y1 e Y5 no R1 e o §3 pede cada outcome no último mês e em média no seguimento. "
                  "A família é a dos 10 testes do R1 (Y1–Y5 × duas medidas), regra principal; o Holm, pedido no "
                  "relato, usa a mesma família. Fixado antes de abrir os outcomes."},
    {"data": "2026-10-23", "item": "Inferência do R1 e do R2",
     "descricao": "O p principal do R1 é o da permutação dentro da célula (999, semente 20261019; estatística = o "
                  "próprio coeficiente com efeito fixo). O IC usa EP agrupado por célula (CR1, graus de liberdade "
                  "sem os efeitos fixos). O R2 usa o mesmo p (Anderson–Rubin) e EP agrupado da VI com efeito fixo."},
    {"data": "2026-10-23", "item": "R4",
     "descricao": "Tratamento = r > 0 ou (r = 0 e ganhou o desempate), com indicador de r = 0 e efeito fixo de "
                  "célula, r ∈ [−2, +2]; EP agrupado, sem permutação (o desempate não é sorteio)."},
    {"data": "2026-10-23", "item": "R6 não executado", "descricao": MOTIVO_R6 + "."},
]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--atualizar-doc", action="store_true", help="só regrava o doc 57f a partir das saídas")
    args = ap.parse_args(argv)
    if args.atualizar_doc:
        atualizar_doc()
        return 0
    P0.etapa_verificar()
    am = ler_amostra()
    p0 = json.loads(P0.ARQ_PASSO0.read_text(encoding="utf-8"))
    linhas = primeiro_estagio(am) + balanco(am) + outcomes(am) + medias_por_r(am)
    est = pd.DataFrame(linhas)[COLUNAS]
    est = aplicar_familia(est)
    sem_nota = est[est["estimativa"].isna() & (est["nota"].fillna("") == "")]
    if len(sem_nota):
        raise FalhaValidacao(f"{len(sem_nota)} linhas sem estimativa e sem nota")
    if not ((est["natureza_dos_dados"] == NATUREZA).all() and (est["estatuto"] == ESTATUTO).all()):
        raise FalhaValidacao("linha sem rótulo")
    OUT.mkdir(parents=True, exist_ok=True)
    est.to_csv(OUT / NOME_EST, index=False, float_format="%.10g")
    est = pd.read_csv(OUT / NOME_EST)
    est["nota"] = est["nota"].fillna("")
    figs = gerar_figuras(est, OUT / DIR_FIG)
    d1 = _janela(am, REGRAS[0], JANELA_R1)
    cel2 = d1.groupby("celula")["z"].agg(["min", "max"])
    amostra = {"principal": {"acima": int((d1["z"] == 1).sum()), "abaixo": int((d1["z"] == 0).sum()),
                             "celulas": int(d1["celula"].nunique()),
                             "celulas_dois_lados": int(((cel2["min"] == 0) & (cel2["max"] == 1)).sum()),
                             "acima_efetivo": int(d1.loc[d1["celula"].isin(cel2.index[(cel2["min"] == 0)
                                                                                   & (cel2["max"] == 1)]), "z"]
                                                  .eq(1).sum()),
                             "abaixo_efetivo": int(d1.loc[d1["celula"].isin(cel2.index[(cel2["min"] == 0)
                                                                                    & (cel2["max"] == 1)]), "z"]
                                                   .eq(0).sum()),
                             "por_ciclo": {str(k): int(n) for k, n in d1["ciclo"].value_counts().sort_index().items()},
                             "acima_todos": int(((am["regra_ligacao"] == REGRAS[0]) & am["r"].isin([1, 2])).sum()),
                             "abaixo_todos": int(((am["regra_ligacao"] == REGRAS[0]) & am["r"].isin([-2, -1])).sum())}}
    d5 = _janela(am, REGRAS[1], JANELA_R1)
    amostra["so_nome"] = {"acima": int((d5["z"] == 1).sum()), "abaixo": int((d5["z"] == 0).sum())}
    fam = est[est["entra_familia"].astype(bool)]

    def pick(**f):
        r = _um(est, **f)
        return {k: (None if pd.isna(r[k]) else float(r[k])) for k in ("estimativa", "ic95_inf", "ic95_sup",
                                                                        "p_valor", "q_bky", "p_holm", "n_obs")}
    principais = {f"R1_{c}_{m}": pick(especificacao="R1", outcome=c, medida=m) for c, _, _, _ in OUTCOMES
                  for m in MEDIDAS}
    principais["PE_d_alocado_1a_opcao"] = pick(especificacao="PE", amostra="ligados", outcome="d_alocado_1a_opcao")
    principais["BAL_ligado"] = pick(especificacao="BAL", regra_ligacao=REGRAS[0], outcome="ligado", medida="R1")
    resumo = {
        "etapa": "P6_mecanismo_alocacao",
        "natureza_dos_dados": NATUREZA,
        "estatuto": ESTATUTO,
        "data_execucao": DATA_EXECUCAO,
        "script": rotulo(Path(__file__)),
        "documento": rotulo(DOC),
        "protocolo": {"arquivo": rotulo(PROTOCOLO_MD), "sha256": sha256(PROTOCOLO_MD)},
        "contraste": "ser alocado na 1ª opção do PMM-E, candidatos de ampla concorrência perto da nota de corte da "
                     "célula (r ∈ {−2, −1} contra {+1, +2}); não é o efeito da bolsa nem do PMM-E sobre o município; "
                     "vínculo cadastrado não é presença nem retenção",
        "leitura": LEITURA,
        "parametros": {"janela_R1": list(JANELA_R1), "janela_R3": list(JANELA_R3), "janela_R4": list(JANELA_R4),
                       "permutacoes": B_PERM, "semente": SEMENTE, "regras": list(REGRAS),
                       "familia": "R1, regra principal, Y1–Y5 × {ultimo, media}", "limiar_F_T63": F_LIMIAR_T63},
        "amostra": amostra,
        "familia": {"testes": int(len(fam)), "p_menor_005": int((fam["p_valor"] < 0.05).sum()),
                    "holm_menor_005": int((fam["p_holm"] < 0.05).sum()),
                    "q_bky_ate_005": int((fam["q_bky"] <= 0.05).sum())},
        "principais": principais,
        "desvios": p0["adendo"] + DESVIOS_31,
        "entradas": [{"caminho": rotulo(p), "sha256": sha256(p)} for p in
                     (P0.ARQ_AMOSTRA, P0.ARQ_CELULAS, P0.ARQ_COBERTURA, P0.ARQ_PASSO0, PROTOCOLO_MD)],
        "contagens": {"linhas": int(len(est)),
                      "por_especificacao": {k: int(v) for k, v in est["especificacao"].value_counts().sort_index()
                                            .items()},
                      "por_status": {k: int(v) for k, v in est["status"].value_counts().sort_index().items()}},
        "saidas": {NOME_EST: {"arquivo": rotulo(OUT / NOME_EST), "sha256": sha256(OUT / NOME_EST)},
                   "figuras": figs},
        "como_ler": {Path(f["arquivo"]).name: f["como_ler"] for f in figs},
        "integridade": "nada simulado ou imputado; não ligados ficam fora dos outcomes e são contados; nenhuma "
                       "competência >= 202609; o arquivo local de IVS não é lido; sem nome, CPF, CNS, CRM ou código "
                       "do profissional nas saídas",
    }
    gravar_json(OUT / NOME_RESUMO, resumo)
    atualizar_doc()
    print(json.dumps(_nan_none({"amostra": amostra, "familia": resumo["familia"]}), ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except FalhaValidacao as erro:
        print(f"FALHA DE VALIDACAO: {erro}", file=sys.stderr)
        sys.exit(2)
