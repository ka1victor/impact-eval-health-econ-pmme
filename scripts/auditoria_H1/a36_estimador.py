"""Estimador próprio da auditoria 36: local linear com kernel triangular, saltos empilhados e EP CR1.

Escrito do zero (não importa `scripts/rdd_bolsa/rdd_lib.py`). Convenções iguais às declaradas nos
protocolos 40/48 para que a comparação com o gravado seja limpa:
- running variable em milésimos de IVS; x = IVS_mil − corte_mil; peso = max(0, 1 − |x|/h) para −h < x < h;
- lado de cima: x > 0 (o próprio corte fica embaixo);
- uma reta de cada lado por grupo (ciclo), salto comum T;
- efeitos fixos como dummies (colunas colineares descartadas na ordem dada);
- EP CR1 por município: (G/(G−1))·((n−1)/(n−k)); IC normal 95%.
"""
from __future__ import annotations

import math

import numpy as np

Z95 = 1.959963984540054


def p_normal(z: float) -> float:
    return math.erfc(abs(z) / math.sqrt(2.0))


def _colunas_independentes(X: np.ndarray, w: np.ndarray, protegidas: list[int]) -> list[int]:
    sw = np.sqrt(w)
    manter: list[int] = []
    for j in range(X.shape[1]):
        cand = manter + [j]
        M = X[:, cand] * sw[:, None]
        nrm = np.linalg.norm(M, axis=0)
        if nrm[-1] <= 0:
            if j in protegidas:
                raise ValueError(f"coluna protegida {j} sem variação")
            continue
        if np.linalg.matrix_rank(M / np.where(nrm > 0, nrm, 1), tol=1e-9) == len(cand):
            manter.append(j)
        elif j in protegidas:
            raise ValueError(f"coluna protegida {j} colinear")
    return manter


def mqp_cr1(X, y, w, cluster):
    X = np.asarray(X, float)
    y = np.asarray(y, float)
    w = np.asarray(w, float)
    n, k = X.shape
    bread = np.linalg.inv(X.T @ (X * w[:, None]))
    beta = bread @ (X.T @ (w * y))
    e = y - X @ beta
    sc = X * (w * e)[:, None]
    _, ids = np.unique(np.asarray(cluster).astype(str), return_inverse=True)
    G = ids.max() + 1
    S = np.zeros((G, k))
    np.add.at(S, ids, sc)
    V = bread @ (S.T @ S) @ bread * (G / (G - 1)) * ((n - 1) / (n - k))
    return beta, V, G


def rd(ivs_mil, y, corte_mil, *, grupo, cluster, h_mil=50.0, peso=None, fe=None, Z=None, grau=1,
       ids=None):
    """Salto comum T. `grupo`: rótulo por linha (ciclo); `fe`: lista de vetores de rótulos (cada um vira
    dummies sem a primeira categoria); `Z`: matriz de covariáveis por grupo já expandida pelo chamador."""
    s = np.asarray(ivs_mil, float)
    y = np.asarray(y, float)
    c = np.broadcast_to(np.asarray(corte_mil, float), s.shape)
    x_mil = s - c
    kern = np.where((x_mil > -h_mil) & (x_mil < h_mil), 1 - np.abs(x_mil) / h_mil, 0.0)
    w = kern * (np.asarray(peso, float) if peso is not None else 1.0)
    g = np.asarray(grupo).astype(str)
    usa = (w > 0) & np.isfinite(y)
    x = x_mil / 1000.0
    t = (x_mil > 0).astype(float)
    cols, nomes = [], []
    for gr in sorted(np.unique(g[usa])):
        ind = (g == gr).astype(float)
        cols += [ind]
        nomes += [f"c[{gr}]"]
        if grau >= 1:
            cols += [ind * x, ind * t * x]
            nomes += [f"x[{gr}]", f"Tx[{gr}]"]
    cols.append(t)
    nomes.append("T")
    prot = list(range(len(cols)))
    for f in (fe or []):
        f = np.asarray(f).astype(str)
        for nv in sorted(np.unique(f[usa]))[1:]:
            cols.append((f == nv).astype(float))
            nomes.append(f"fe[{nv}]")
    if Z is not None:
        Zm = np.asarray(Z, float).reshape(len(s), -1)
        for j in range(Zm.shape[1]):
            cols.append(Zm[:, j])
            nomes.append(f"z{j}")
    X = np.column_stack(cols)[usa]
    manter = _colunas_independentes(X, w[usa], prot)
    beta, V, G = mqp_cr1(X[:, manter], y[usa], w[usa], np.asarray(cluster).astype(str)[usa])
    i = [nomes[j] for j in manter].index("T")
    tau, ep = float(beta[i]), float(math.sqrt(max(V[i, i], 0)))
    un = np.asarray(ids if ids is not None else cluster).astype(str)
    return {
        "salto": tau, "ep": ep, "ic_inf": tau - Z95 * ep, "ic_sup": tau + Z95 * ep,
        "p": p_normal(tau / ep) if ep > 0 else float("nan"),
        "n_obs": int(usa.sum()), "n_mun_abaixo": int(np.unique(un[usa & (x_mil <= 0)]).size),
        "n_mun_acima": int(np.unique(un[usa & (x_mil > 0)]).size), "G": int(G),
    }


def dif_medias(ivs_mil, y, corte_mil, *, janela_mil, cluster, peso=None, grupo=None, fe=None):
    """Média de cima menos média de baixo na janela −janela < x < janela (sem reta), EP CR1 por município.
    Com `grupo`, intercepto por grupo (ciclo) e diferença comum; com `peso`, médias ponderadas."""
    s = np.asarray(ivs_mil, float)
    y = np.asarray(y, float)
    x = s - corte_mil
    dentro = (np.abs(x) < janela_mil - 1e-9) & np.isfinite(y)
    w = np.where(dentro, np.asarray(peso, float) if peso is not None else 1.0, 0.0)
    t = (x > 0).astype(float)
    cols = []
    if grupo is None:
        cols.append(np.ones_like(s))
    else:
        g = np.asarray(grupo).astype(str)
        for gr in sorted(np.unique(g[dentro])):
            cols.append((g == gr).astype(float))
    cols.append(t)
    prot = list(range(len(cols)))
    for f in (fe or []):
        f = np.asarray(f).astype(str)
        for nv in sorted(np.unique(f[dentro]))[1:]:
            cols.append((f == nv).astype(float))
    X = np.column_stack(cols)[dentro]
    manter = _colunas_independentes(X, w[dentro], prot)
    beta, V, G = mqp_cr1(X[:, manter], y[dentro], w[dentro], np.asarray(cluster).astype(str)[dentro])
    i = manter.index(len(prot) - 1)
    tau, ep = float(beta[i]), float(math.sqrt(max(V[i, i], 0)))
    cl = np.asarray(cluster).astype(str)
    ww = w[dentro]
    yy = y[dentro]
    tt = t[dentro]
    return {
        "salto": tau, "ep": ep, "ic_inf": tau - Z95 * ep, "ic_sup": tau + Z95 * ep,
        "p": p_normal(tau / ep) if ep > 0 else float("nan"),
        "media_abaixo": float(np.average(yy[tt == 0], weights=ww[tt == 0])) if (tt == 0).any() else float("nan"),
        "media_acima": float(np.average(yy[tt == 1], weights=ww[tt == 1])) if (tt == 1).any() else float("nan"),
        "n_obs": int(dentro.sum()),
        "n_mun_abaixo": int(np.unique(cl[dentro & (x <= 0)]).size),
        "n_mun_acima": int(np.unique(cl[dentro & (x > 0)]).size),
    }
