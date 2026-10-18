"""Biblioteca de estimação da RDD da bolsa do PMM-E (tarefa A do protocolo E6–E9).

Protocolo: `docs/06_execucao/40_protocolo_multioutcome_rdd_bolsa.md` e
`output/rdd_bolsa/protocolo_E6_multioutcome.json` (congelados em 18/10/2026).
Esta biblioteca não lê dado nenhum: recebe vetores e devolve dicionários ou
tabelas. Os scripts E6–E8 (`13_*`, `14_*`, `15_*`) leem os insumos e gravam as
saídas; os testes sintéticos estão em `tests/test_rdd_lib.py`.

Convenções comuns
-----------------
- Running variable em milésimos de IVS (`s_mil`, inteiros ou floats). Valores a
  menos de 1e-6 de um inteiro são arredondados para o inteiro, para que
  1000 * 0,3 = 300,00000000000006 não caia no lado errado do corte.
- Cortes em milésimos (`corte_mil`, 300 e 400). T = 1[s > c]: o próprio corte
  pertence ao lado inferior. x = s - c; nas regressões x entra em unidades de
  IVS (x_mil / 1000), como no E3.
- Salto (`tau`) = lado com bolsa maior (s > c) menos lado com bolsa menor.
- Janela de largura h (em milésimos, `h_mil`; principal 50): amostra com peso
  de kernel positivo, -h < x < h. Kernel triangular max(0, 1 - |x|/h)
  (principal) ou uniforme. O ponto s = c + h tem peso zero e fica fora.
- EP HC1 (uma linha por unidade) ou CR1 por cluster:
  HC1: V = B M B * n/(n-k); CR1: V = B M_g B * G/(G-1) * (n-1)/(n-k).
  `pequena_amostra=False` devolve HC0/CR0 (usado no teste de identidade da
  DiRD).
- IC 95% e p bicaudal pela normal, salvo nos IC honestos e na permutação.
- Todo resultado é um dicionário com `tau`, `ep`, `ic95_inf`, `ic95_sup`,
  `p_valor`, `n_abaixo`, `n_acima`, `n_obs`, `n_clusters`, `h`, `h_mil` e
  `nota` (texto; vazio quando nada a registrar). `n_abaixo`/`n_acima` contam
  unidades distintas quando há cluster (ou `ids_unidade`), e linhas sem isso.
  Com `detalhes=True` vem também `_detalhes` (matrizes do ajuste), que não é
  para gravar.
- Determinística: não há aleatoriedade fora da permutação de Fisher, cuja
  semente é argumento.
- Integridade: a biblioteca não contém dado, não lê nem grava arquivo e não
  devolve valor de reserva. Estimação que falha (suporte insuficiente, lado
  sem eventos, IRLS sem convergência, M indefinido, taxa de seleção não
  positiva) devolve NaN com `nota` explicando o motivo; contagens de amostra
  não estimada ficam None. As únicas constantes são parâmetros do protocolo
  (cortes, h, semente, número de permutações) e a grade de h do IC honesto.

Funções (ver docstrings)
------------------------
1. `rd_local_linear`: RDD sharp local (grau 1 ou 0), kernel triangular ou
   uniforme, pesos extras, cluster, covariáveis à Calonico, Cattaneo, Farrell e
   Titiunik (2019). Com kernel triangular, grau 1, sem pesos, cluster nem
   covariáveis, reproduz exatamente `rdd_local_linear` do E3 (07).
2. `rd_empilhado`: cortes (e ciclos) empilhados com intercepto e inclinações
   por grupo x lado, tau comum, efeitos fixos opcionais e cluster. Com
   grupo = corte, reproduz `rd_empilhado` do E5 (11).
3. `cv_honesto`, `p_honesto`, `m_regra_de_bolso`, `variancia_vizinhos`,
   `rd_honesto`, `rd_honesto_h_otimo`, `rd_empilhado_honesto`,
   `rd_honesto_relato`: IC com viés limitado (Armstrong e Kolesár, 2018, 2020).
4. `rd_poisson_local`: Poisson local com kernel (IRLS, ligação log, offset).
5. `diferenca_pos_pre`, `rd_dird_delta`, `rd_dird_painel`,
   `rd_estudo_evento`: diferença em descontinuidades e estudo de evento.
6. `mascara_referencia`, `indice_klk`: índice de Kling, Liebman e Katz (2007)
   e a variante de Anderson (2008).
7. `holm`, `qvalores_bky`: Holm e q-valores aguçados de Benjamini, Krieger e
   Yekutieli (2006) pelo algoritmo de Anderson (2008).
8. `limites_lee_rd`: limites de Lee (2009) locais no corte.
9. `matriz_permutacao`, `fisher_dif_medias`, `rl_janela`: local randomization
   com p de Fisher (mesmo algoritmo e mesma semente que o E5).

Contraste identificado pela RDD em nível: incentivo marginal anunciado de
R$ 5 mil em cada corte, ou o pacote bolsa + teto do PMMB se a Portaria GM/MS
752/2023 mudar no mesmo corte (seção 4 do protocolo). Nunca é efeito da
participação no PMM-E nem do Agora Tem Especialistas.
"""

from __future__ import annotations

import math
from typing import Sequence

import numpy as np
import pandas as pd
from scipy import optimize, stats

CORTES_MIL = (300, 400)
H_PRINCIPAL_MIL = 50
H_SENSIBILIDADE_MIL = (30, 80)
GRADE_H_MIL = tuple(range(20, 155, 5))
Z_975 = 1.959963984540054
SEMENTE = 20261018
N_PERMUTACOES = 10_000
TOL_PERM = 1e-10
J_VIZINHOS = 3

__all__ = [
    "CORTES_MIL", "H_PRINCIPAL_MIL", "H_SENSIBILIDADE_MIL", "GRADE_H_MIL", "Z_975",
    "normalizar_s_mil", "pesos_kernel", "p_normal", "mqp_sanduiche",
    "rd_local_linear", "rd_empilhado",
    "cv_honesto", "p_honesto", "m_regra_de_bolso", "variancia_vizinhos", "rd_honesto",
    "rd_honesto_h_otimo", "rd_empilhado_honesto", "rd_honesto_relato",
    "rd_poisson_local",
    "diferenca_pos_pre", "rd_dird_delta", "rd_dird_painel", "rd_estudo_evento",
    "mascara_referencia", "indice_klk",
    "holm", "qvalores_bky",
    "limites_lee_rd",
    "matriz_permutacao", "fisher_dif_medias", "rl_janela",
]


# ---------------------------------------------------------------------------
# Utilitários
# ---------------------------------------------------------------------------

def normalizar_s_mil(s_mil) -> np.ndarray:
    """Running variable em milésimos como float; quase-inteiros viram inteiros exatos."""
    s = np.asarray(s_mil, dtype=float)
    r = np.round(s)
    return np.where(np.abs(s - r) < 1e-6, r, s)


def pesos_kernel(x_mil, h_mil: float, kernel: str = "triangular") -> np.ndarray:
    """Peso do kernel em -h < x < h (o ponto x = h fica fora, como no E3 e no E5)."""
    x = np.asarray(x_mil, dtype=float)
    dentro = (x > -h_mil) & (x < h_mil)
    if kernel == "triangular":
        return np.where(dentro, 1.0 - np.abs(x) / h_mil, 0.0)
    if kernel == "uniforme":
        return dentro.astype(float)
    raise ValueError(f"kernel desconhecido: {kernel}")


def p_normal(z: float) -> float:
    """p bicaudal pela normal."""
    return math.erfc(abs(z) / math.sqrt(2.0)) if math.isfinite(z) else float("nan")


def _vetor(v, n: int, nome: str) -> np.ndarray:
    a = np.asarray(v, dtype=float)
    if a.ndim == 0:
        a = np.full(n, float(a))
    if a.shape != (n,):
        raise ValueError(f"{nome} com tamanho {a.shape}, esperado ({n},)")
    return a


def _rotulos(v, n: int) -> np.ndarray | None:
    if v is None:
        return None
    a = np.asarray(v)
    if a.ndim == 0:
        a = np.full(n, a)
    a = a.astype(str)
    if a.shape != (n,):
        raise ValueError(f"rotulos com tamanho {a.shape}, esperado ({n},)")
    return a


def _contar(ids: np.ndarray | None, mascara: np.ndarray) -> int:
    if ids is None:
        return int(mascara.sum())
    return int(np.unique(ids[mascara]).size)


def _juntar_notas(*notas: str) -> str:
    return "; ".join(n for n in notas if n)


def _resultado_vazio(h_mil: float) -> dict:
    return {
        "tau": float("nan"), "ep": float("nan"), "ic95_inf": float("nan"), "ic95_sup": float("nan"),
        "p_valor": float("nan"), "n_abaixo": None, "n_acima": None, "n_obs": None, "n_clusters": None,
        "h": h_mil / 1000.0, "h_mil": h_mil, "nota": "",
    }


def _inferencia_normal(res: dict, tau: float, ep: float) -> dict:
    res.update({"tau": tau, "ep": ep, "ic95_inf": tau - Z_975 * ep, "ic95_sup": tau + Z_975 * ep})
    if ep > 0:
        res["p_valor"] = p_normal(tau / ep)
    else:
        res["nota"] = _juntar_notas(res.get("nota", ""), "EP nulo: outcome sem variacao residual na janela")
    return res


# ---------------------------------------------------------------------------
# Mínimos quadrados ponderados com variância sanduíche
# ---------------------------------------------------------------------------

def mqp_sanduiche(X, y, w, *, nomes: Sequence[str] | None = None, protegidas: set[str] | None = None,
                  cluster=None, pequena_amostra: bool = True) -> dict:
    """MQP com EP HC1 (sem cluster) ou CR1 (com cluster); HC0/CR0 se `pequena_amostra=False`.

    Colunas não protegidas sem variação ou colineares são descartadas na ordem
    dada (determinístico, como `mqp_robusto` do E5); coluna protegida nessa
    situação devolve {"erro": ...}. Sem `protegidas`, todas são protegidas.
    As operações matriciais seguem a ordem do E3 para reproduzir seus números.
    """
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    w = np.asarray(w, dtype=float)
    n = len(y)
    nomes = list(nomes) if nomes is not None else [f"b{j}" for j in range(X.shape[1])]
    protegidas = set(nomes) if protegidas is None else set(protegidas)
    sw = np.sqrt(w)
    manter: list[int] = []
    descartadas: list[str] = []
    for j in range(X.shape[1]):
        cand = manter + [j]
        M = X[:, cand] * sw[:, None]
        normas = np.linalg.norm(M, axis=0)
        ok = bool(normas[-1] > 0) and np.linalg.matrix_rank(
            M / np.where(normas > 0, normas, 1.0), tol=1e-9) == len(cand)
        if ok:
            manter.append(j)
        elif nomes[j] in protegidas:
            return {"erro": f"coluna protegida '{nomes[j]}' sem variacao ou colinear"}
        else:
            descartadas.append(nomes[j])
    k = len(manter)
    if n <= k:
        return {"erro": "graus de liberdade insuficientes"}
    # Ordem C: a seleção de colunas por índice devolve ordem Fortran, que muda
    # o caminho do BLAS e o último bit em relação ao E3.
    Xk = np.ascontiguousarray(X[:, manter])
    XtWX = Xk.T @ (Xk * w[:, None])
    bread = np.linalg.inv(XtWX)
    beta = bread @ (Xk.T @ (w * y))
    e = y - Xk @ beta
    score = Xk * (w * e)[:, None]
    G = None
    ids = None
    if cluster is None:
        fator = n / (n - k) if pequena_amostra else 1.0
        V = bread @ (score.T @ score) @ bread * fator
    else:
        _, ids = np.unique(np.asarray(cluster).astype(str), return_inverse=True)
        G = int(ids.max()) + 1
        if G < 2:
            return {"erro": "menos de 2 clusters"}
        S = np.zeros((G, k))
        np.add.at(S, ids, score)
        fator = (G / (G - 1)) * ((n - 1) / (n - k)) if pequena_amostra else 1.0
        V = bread @ (S.T @ S) @ bread * fator
    nomes_k = [nomes[j] for j in manter]
    return {"beta": beta, "coef": dict(zip(nomes_k, beta.tolist())), "V": V, "bread": bread, "X": Xk,
            "w": w, "y": y, "residuos": e, "nomes": nomes_k, "n": n, "k": k, "G": G,
            "cluster_idx": ids, "fator": fator, "descartadas": descartadas}


def _pesos_lineares(fit: dict, nome: str = "T") -> np.ndarray:
    """Pesos a_i tais que o coeficiente `nome` = sum_i a_i y_i."""
    i = fit["nomes"].index(nome)
    return (fit["bread"][i] @ fit["X"].T) * fit["w"]


# ---------------------------------------------------------------------------
# 1. Local linear sharp em um corte
# ---------------------------------------------------------------------------

def rd_local_linear(s_mil, y, corte_mil: float, h_mil: float = H_PRINCIPAL_MIL, *, kernel: str = "triangular",
                    grau: int = 1, peso=None, cluster=None, ids_unidade=None, Z=None,
                    nomes_z: Sequence[str] | None = None, pequena_amostra: bool = True,
                    detalhes: bool = False) -> dict:
    """RDD sharp local em um corte.

    Grau 1: y = a + b*x + tau*T + d*T*x [+ Z'g]; grau 0: y = a + tau*T [+ Z'g].
    MQP com peso = kernel(x; h) x `peso` (por exemplo, número de células).
    Covariáveis (Calonico, Cattaneo, Farrell e Titiunik, 2019): as mesmas dos
    dois lados, lineares e não interagidas com T; coluna sem variação ou
    colinear é descartada na ordem dada e registrada. EP HC1 ou CR1 por
    `cluster`. Exige 2 mass points com peso positivo em cada lado (1 no grau 0).
    """
    s = normalizar_s_mil(s_mil)
    n = len(s)
    yv = _vetor(y, n, "y")
    x_mil = s - corte_mil
    w = pesos_kernel(x_mil, h_mil, kernel)
    if peso is not None:
        w = w * _vetor(peso, n, "peso")
    x = x_mil / 1000.0
    t = (x_mil > 0).astype(float)
    cols, nomes = [np.ones_like(x)], ["const"]
    if grau == 1:
        cols.append(x)
        nomes.append("x")
    elif grau != 0:
        raise ValueError("grau deve ser 0 ou 1")
    cols.append(t)
    nomes.append("T")
    if grau == 1:
        cols.append(t * x)
        nomes.append("T_x")
    protegidas = set(nomes)
    nomes_z = list(nomes_z or [])
    if Z is not None:
        Zm = np.asarray(Z, dtype=float).reshape(n, -1)
        if not nomes_z:
            nomes_z = [f"z{j}" for j in range(Zm.shape[1])]
        if len(nomes_z) != Zm.shape[1]:
            raise ValueError("nomes_z nao bate com o numero de colunas de Z")
        cols.extend(Zm[:, j] for j in range(Zm.shape[1]))
        nomes.extend(nomes_z)
    X = np.column_stack(cols)
    usa = (w > 0) & np.isfinite(yv) & np.isfinite(X).all(axis=1)
    if peso is not None:
        usa &= np.isfinite(w)
    ab, ac = usa & (x_mil <= 0), usa & (x_mil > 0)
    cl = _rotulos(cluster, n)
    ids = _rotulos(ids_unidade, n) if ids_unidade is not None else cl
    res = _resultado_vazio(h_mil)
    res.update({
        "corte_mil": corte_mil, "kernel": kernel, "grau": grau,
        "n_abaixo": _contar(ids, ab), "n_acima": _contar(ids, ac), "n_obs": int(usa.sum()),
        "mass_points_abaixo": int(np.unique(s[ab]).size), "mass_points_acima": int(np.unique(s[ac]).size),
        "media_bruta_abaixo": float(yv[ab].mean()) if ab.any() else float("nan"),
        "media_bruta_acima": float(yv[ac].mean()) if ac.any() else float("nan"),
        "covariaveis_descartadas": "",
    })
    minimo = 2 if grau == 1 else 1
    if res["mass_points_abaixo"] < minimo or res["mass_points_acima"] < minimo:
        res["nota"] = f"suporte insuficiente: menos de {minimo} mass points com peso positivo em algum lado"
        return res
    fit = mqp_sanduiche(X[usa], yv[usa], w[usa], nomes=nomes, protegidas=protegidas,
                        cluster=cl[usa] if cl is not None else None, pequena_amostra=pequena_amostra)
    if "erro" in fit:
        res["nota"] = fit["erro"]
        return res
    i = fit["nomes"].index("T")
    _inferencia_normal(res, float(fit["beta"][i]), float(math.sqrt(max(fit["V"][i, i], 0.0))))
    res["n_clusters"] = fit["G"]
    res["covariaveis_descartadas"] = ";".join(fit["descartadas"])
    if detalhes:
        res["_detalhes"] = {"fit": fit, "usa": usa, "x": x, "x_mil": x_mil, "t": t, "w": w, "s": s, "y": yv}
    return res


# ---------------------------------------------------------------------------
# 2. Cortes e ciclos empilhados
# ---------------------------------------------------------------------------

def rd_empilhado(s_mil, y, corte_mil, *, grupo=None, h_mil: float = H_PRINCIPAL_MIL, kernel: str = "triangular",
                 peso=None, cluster=None, ids_unidade=None, efeitos_fixos=None, Z=None,
                 nomes_z: Sequence[str] | None = None, pequena_amostra: bool = True,
                 detalhes: bool = False) -> dict:
    """Saltos empilhados: r = s - c da linha; intercepto e inclinações por grupo x lado; tau comum.

    y = sum_g 1[g](a_g + b_g r + d_g T r) + tau T [+ EF] [+ Z'g]. O lado
    superior do grupo g tem intercepto a_g + tau. `grupo` (padrão: o corte da
    linha) pode ser corte, ciclo ou ciclo x corte. A mesma unidade pode
    aparecer em mais de uma linha (nas duas janelas ou em vários ciclos):
    nesse caso passe `cluster` = município. `efeitos_fixos` (por exemplo, o
    ciclo quando `grupo` é o corte) entra como dummies não protegidas sem a
    categoria de referência (a primeira em ordem). O estimando é a média dos
    saltos por grupo com pesos omega_g = sum_{i em g} a_i T_i (somam 1),
    devolvidos em `pesos_grupos` (Cattaneo, Keele, Titiunik e Vazquez-Bare,
    2016).
    """
    s = normalizar_s_mil(s_mil)
    n = len(s)
    c = _vetor(corte_mil, n, "corte_mil")
    yv = _vetor(y, n, "y")
    g = _rotulos(grupo, n) if grupo is not None else np.array([f"{v:g}" for v in c])
    x_mil = s - c
    w = pesos_kernel(x_mil, h_mil, kernel)
    if peso is not None:
        w = w * _vetor(peso, n, "peso")
    x = x_mil / 1000.0
    t = (x_mil > 0).astype(float)
    cols, nomes = [], []
    grupos = sorted(np.unique(g).tolist())
    for grp in grupos:
        ind = (g == grp).astype(float)
        cols.extend([ind, ind * x, ind * t * x])
        nomes.extend([f"const[{grp}]", f"x[{grp}]", f"T_x[{grp}]"])
    cols.append(t)
    nomes.append("T")
    protegidas = set(nomes)
    if efeitos_fixos is not None:
        ef = _rotulos(efeitos_fixos, n)
        for nivel in sorted(np.unique(ef).tolist())[1:]:
            cols.append((ef == nivel).astype(float))
            nomes.append(f"ef[{nivel}]")
    nomes_z = list(nomes_z or [])
    if Z is not None:
        Zm = np.asarray(Z, dtype=float).reshape(n, -1)
        if not nomes_z:
            nomes_z = [f"z{j}" for j in range(Zm.shape[1])]
        cols.extend(Zm[:, j] for j in range(Zm.shape[1]))
        nomes.extend(nomes_z)
    X = np.column_stack(cols)
    usa = (w > 0) & np.isfinite(yv) & np.isfinite(X).all(axis=1)
    ab, ac = usa & (x_mil <= 0), usa & (x_mil > 0)
    cl = _rotulos(cluster, n)
    ids = _rotulos(ids_unidade, n) if ids_unidade is not None else cl
    res = _resultado_vazio(h_mil)
    res.update({"kernel": kernel, "n_abaixo": _contar(ids, ab), "n_acima": _contar(ids, ac),
                "n_obs": int(usa.sum()), "grupos": ";".join(grupos), "covariaveis_descartadas": "",
                "pesos_grupos": {}})
    notas = []
    if ids_unidade is not None and cl is None and np.unique(ids[usa]).size < int(usa.sum()):
        notas.append("unidade repetida sem cluster: EP HC1 trata linhas repetidas como independentes")
    for grp in grupos:
        em = usa & (g == grp)
        if np.unique(s[em & (x_mil <= 0)]).size < 2 or np.unique(s[em & (x_mil > 0)]).size < 2:
            res["nota"] = _juntar_notas(*notas, f"suporte insuficiente no grupo {grp}: menos de 2 mass points "
                                                f"com peso positivo em algum lado")
            return res
    fit = mqp_sanduiche(X[usa], yv[usa], w[usa], nomes=nomes, protegidas=protegidas,
                        cluster=cl[usa] if cl is not None else None, pequena_amostra=pequena_amostra)
    if "erro" in fit:
        res["nota"] = _juntar_notas(*notas, fit["erro"])
        return res
    i = fit["nomes"].index("T")
    res["nota"] = _juntar_notas(*notas)
    _inferencia_normal(res, float(fit["beta"][i]), float(math.sqrt(max(fit["V"][i, i], 0.0))))
    a = _pesos_lineares(fit)
    tu, gu = t[usa], g[usa]
    res["pesos_grupos"] = {grp: float(np.sum(a[gu == grp] * tu[gu == grp])) for grp in grupos}
    res["n_clusters"] = fit["G"]
    res["covariaveis_descartadas"] = ";".join(fit["descartadas"])
    if detalhes:
        res["_detalhes"] = {"fit": fit, "usa": usa, "x": x, "x_mil": x_mil, "t": t, "w": w, "s": s, "y": yv,
                            "grupo": g, "corte": c, "a": a}
    return res


# ---------------------------------------------------------------------------
# 3. Inferência com viés limitado (Armstrong e Kolesár)
# ---------------------------------------------------------------------------

def cv_honesto(t: float, alfa: float = 0.05) -> float:
    """Valor crítico cv_alfa(t): resolve Phi(c - t) - Phi(-c - t) = 1 - alfa (quantil de |N(t, 1)|).

    t = viés máximo / EP. cv_0,05(0) = 1,96.
    """
    t = abs(float(t))
    if not math.isfinite(t):
        return float("nan")
    alvo = 1.0 - alfa

    def f(c: float) -> float:
        return stats.norm.cdf(c - t) - stats.norm.cdf(-c - t) - alvo

    sup = t + stats.norm.ppf(1.0 - alfa / 2.0) + 5.0
    return float(optimize.brentq(f, 0.0, sup, xtol=1e-14, rtol=1e-15, maxiter=500))


def p_honesto(tau: float, ep: float, vies_max: float) -> float:
    """p do teste de tau = 0 que inverte o IC honesto: P(|N(t, 1)| >= |tau|/ep), t = vies/ep."""
    if not (ep > 0) or not math.isfinite(tau):
        return float("nan")
    z = abs(tau) / ep
    t = abs(vies_max) / ep
    return float(stats.norm.sf(z - t) + stats.norm.cdf(-z - t))


def m_regra_de_bolso(s_mil, y, corte_mil: float, *, suporte_mil: tuple[float, float] | None = None,
                     peso=None) -> dict:
    """Limite M de |f''| pela regra de bolso de Armstrong e Kolesár (2020) / RDHonest.

    Em cada lado (o corte no inferior), quártica global de y em r = (s - c)/1000
    por MQO (ou MQP com `peso`); M_lado = máx |f''(r)| no suporte do lado, com
    f''(r) = 2 b2 + 6 b3 r + 12 b4 r^2 (máximo nas pontas ou no extremo
    r* = -b3/(4 b4)). M = máx(M_abaixo, M_acima). `suporte_mil = (lo, hi)`
    restringe os dados (inclusive); com dois cortes, use-o para que a quártica
    de um corte não atravesse o outro (por exemplo, (150, 400) em 0,300).
    M está em unidades de y por IVS^2.
    """
    s = normalizar_s_mil(s_mil)
    n = len(s)
    yv = _vetor(y, n, "y")
    pv = _vetor(peso, n, "peso") if peso is not None else np.ones(n)
    ok = np.isfinite(yv) & np.isfinite(pv) & (pv > 0)
    if suporte_mil is not None:
        ok &= (s >= suporte_mil[0]) & (s <= suporte_mil[1])
    r = (s - corte_mil) / 1000.0
    out: dict = {"corte_mil": corte_mil, "suporte_mil": suporte_mil, "nota": ""}
    notas = []
    for lado, m in (("abaixo", ok & (r <= 0)), ("acima", ok & (r > 0))):
        rr, yy, ww = r[m], yv[m], np.sqrt(pv[m])
        if np.unique(rr).size < 5:
            out[f"M_{lado}"] = float("nan")
            out[f"coef_{lado}"] = []
            notas.append(f"lado {lado} com menos de 5 mass points: quartica nao identificada")
            continue
        P = np.column_stack([rr ** p for p in range(5)])
        b = np.linalg.lstsq(P * ww[:, None], yy * ww, rcond=None)[0]

        def f2(u, b=b):
            return abs(2 * b[2] + 6 * b[3] * u + 12 * b[4] * u ** 2)

        lo, hi = float(rr.min()), float(rr.max())
        cand = [f2(lo), f2(hi)]
        if abs(b[4]) > 1e-10:
            ext = -b[3] / (4 * b[4])
            if lo < ext < hi:
                cand.append(f2(ext))
        out[f"M_{lado}"] = float(max(cand))
        out[f"coef_{lado}"] = b.tolist()
        out[f"n_{lado}"] = int(m.sum())
    out["M"] = float(max(out["M_abaixo"], out["M_acima"])) if all(
        math.isfinite(out[f"M_{l}"]) for l in ("abaixo", "acima")) else float("nan")
    out["nota"] = _juntar_notas(*notas)
    return out


def variancia_vizinhos(x, y, celula=None, J: int = J_VIZINHOS) -> np.ndarray:
    """sigma^2_i pelos J vizinhos mais próximos na mesma célula (lado, ou grupo x lado).

    Como em RDHonest (`sigmaNN`): vizinhos = todas as outras observações da
    célula com |x_j - x_i| <= distância do J-ésimo vizinho (empates entram);
    sigma^2_i = J_i/(J_i + 1) (y_i - média dos vizinhos)^2. Célula com uma
    observação devolve NaN.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(x)
    cel = _rotulos(celula, n) if celula is not None else np.zeros(n).astype(str)
    sig = np.full(n, np.nan)
    for c in sorted(np.unique(cel).tolist()):
        idx = np.flatnonzero(cel == c)
        m = idx.size
        if m < 2:
            continue
        xi, yi = x[idx], y[idx]
        jef = min(J, m - 1)
        bloco = max(1, 2_000_000 // m)
        for ini in range(0, m, bloco):
            fim = min(m, ini + bloco)
            d = np.abs(xi[ini:fim, None] - xi[None, :])
            d[np.arange(fim - ini), np.arange(ini, fim)] = np.inf
            dj = np.partition(d, jef - 1, axis=1)[:, jef - 1]
            viz = d <= dj[:, None] + 1e-12
            nv = viz.sum(axis=1)
            media = (viz @ yi) / nv
            sig[idx[ini:fim]] = nv / (nv + 1.0) * (yi[ini:fim] - media) ** 2
    return sig


def _variancia_estimador(a: np.ndarray, fit: dict, variancia: str, x: np.ndarray, y: np.ndarray,
                         celula: np.ndarray, J: int) -> float:
    """Var(sum a_i y_i): vizinhos ("nn"), EHW com fator HC1 ("ehw") ou CR1 ("cluster")."""
    n, k = fit["n"], fit["k"]
    if variancia == "nn":
        sig = variancia_vizinhos(x, y, celula, J)
        if not np.isfinite(sig).all():
            raise ValueError("celula com uma observacao: variancia por vizinhos indefinida")
        return float(np.sum(a ** 2 * sig))
    e = fit["residuos"]
    if variancia == "ehw":
        return float(np.sum(a ** 2 * e ** 2) * n / (n - k))
    if variancia == "cluster":
        if fit["cluster_idx"] is None:
            raise ValueError("variancia='cluster' exige cluster")
        G = fit["G"]
        S = np.bincount(fit["cluster_idx"], weights=a * e, minlength=G)
        return float(np.sum(S ** 2) * (G / (G - 1)) * ((n - 1) / (n - k)))
    raise ValueError(f"variancia desconhecida: {variancia}")


def _honesto_de_pesos(res: dict, a: np.ndarray, r: np.ndarray, M: float, var: float) -> dict:
    ep = math.sqrt(max(var, 0.0))
    vies = 0.5 * M * float(np.sum(np.abs(a) * r ** 2))
    tau = res["tau"]
    t = vies / ep if ep > 0 else float("inf")
    cv = cv_honesto(t) if ep > 0 else float("nan")
    out = {
        "tau": tau, "ep": ep, "ep_convencional": res["ep"], "M": M, "vies_max": vies, "razao_vies_ep": t,
        "cv": cv, "ic95_inf": tau - cv * ep, "ic95_sup": tau + cv * ep, "semi_amplitude": cv * ep,
        "p_valor": p_honesto(tau, ep, vies),
    }
    return out


def rd_honesto(s_mil, y, corte_mil: float, h_mil: float = H_PRINCIPAL_MIL, *, M: float | None = None,
               kernel: str = "triangular", peso=None, cluster=None, ids_unidade=None,
               variancia: str | None = None, J: int = J_VIZINHOS,
               suporte_mil: tuple[float, float] | None = None) -> dict:
    """IC honesto (viés limitado) do local linear, Armstrong e Kolesár (2018, 2020).

    O estimador é o mesmo de `rd_local_linear` (tau = sum a_i y_i). Classe de
    Taylor com |f''| <= M de cada lado: viés máximo
    B = (M/2) sum_i |a_i| r_i^2 (r em IVS). É mais conservador que a classe de
    Hölder padrão do RDHonest. IC: tau +- cv_0,05(B/ep) ep. ep: vizinhos
    (J = 3, mesmo lado; padrão sem cluster), "ehw" (resíduos com fator HC1:
    com M = 0 reproduz o IC HC1) ou "cluster" (CR1; padrão com cluster).
    M = None usa `m_regra_de_bolso` (com `suporte_mil`). Covariáveis não são
    aceitas aqui.
    """
    if variancia is None:
        variancia = "cluster" if cluster is not None else "nn"
    if variancia == "nn" and cluster is not None:
        raise ValueError("variancia por vizinhos supoe observacoes independentes; use 'cluster'")
    base = rd_local_linear(s_mil, y, corte_mil, h_mil, kernel=kernel, peso=peso, cluster=cluster,
                           ids_unidade=ids_unidade, detalhes=True)
    regra = None
    if M is None:
        regra = m_regra_de_bolso(s_mil, y, corte_mil, suporte_mil=suporte_mil)
        M = regra["M"]
    res = {k: v for k, v in base.items() if k != "_detalhes"}
    res.update({"M": M, "M_origem": "regra_de_bolso" if regra is not None else "informado",
                "variancia": variancia, "classe": "Taylor (|f''| <= M por lado)",
                "ep_convencional": base["ep"], "vies_max": float("nan"), "razao_vies_ep": float("nan"),
                "cv": float("nan"), "semi_amplitude": float("nan")})
    if regra is not None:
        res["M_abaixo"], res["M_acima"] = regra["M_abaixo"], regra["M_acima"]
        res["nota"] = _juntar_notas(res["nota"], regra["nota"])
    if "_detalhes" not in base or not math.isfinite(M):
        res.update({"tau": base["tau"], "ep": float("nan"), "ic95_inf": float("nan"), "ic95_sup": float("nan"),
                    "p_valor": float("nan")})
        if not math.isfinite(M):
            res["nota"] = _juntar_notas(res["nota"], "M indefinido")
        return res
    d = base["_detalhes"]
    usa = d["usa"]
    a = _pesos_lineares(d["fit"])
    r = d["x"][usa]
    celula = np.where(d["t"][usa] > 0, "acima", "abaixo")
    var = _variancia_estimador(a, d["fit"], variancia, r, d["y"][usa], celula, J)
    res.update(_honesto_de_pesos(base, a, r, M, var))
    return res


def rd_honesto_h_otimo(s_mil, y, corte_mil: float, *, M: float | None = None,
                       grade_h_mil: Sequence[float] = GRADE_H_MIL, h_fixo_mil: float = H_PRINCIPAL_MIL,
                       suporte_mil: tuple[float, float] | None = None, **kw) -> dict:
    """h que minimiza a semi-amplitude do IC honesto numa grade (Armstrong e Kolesár, 2020).

    M é fixado uma vez (regra de bolso se None), antes da grade. Empate: o
    menor h. Devolve {"h_fixo": resultado em h_fixo, "h_otimo": resultado no
    h escolhido, "grade": DataFrame com h e semi-amplitude}.
    """
    if M is None:
        M = m_regra_de_bolso(s_mil, y, corte_mil, suporte_mil=suporte_mil)["M"]
    linhas, resultados = [], {}
    for h in sorted(set(grade_h_mil) | {h_fixo_mil}):
        r = rd_honesto(s_mil, y, corte_mil, h, M=M, **kw)
        resultados[h] = r
        linhas.append({"h_mil": h, "h": h / 1000.0, "tau": r["tau"], "ep": r["ep"], "vies_max": r["vies_max"],
                       "semi_amplitude": r["semi_amplitude"], "nota": r["nota"]})
    grade = pd.DataFrame(linhas)
    validas = grade[np.isfinite(grade["semi_amplitude"].to_numpy(dtype=float))
                    & grade["h_mil"].isin(list(grade_h_mil))]
    if len(validas):
        h_ot = float(validas.sort_values(["semi_amplitude", "h_mil"], kind="stable").iloc[0]["h_mil"])
        h_ot = next(h for h in resultados if float(h) == h_ot)
        otimo = resultados[h_ot]
    else:
        otimo = {**_resultado_vazio(float("nan")), "nota": "nenhum h da grade com IC honesto definido"}
    return {"h_fixo": resultados[h_fixo_mil], "h_otimo": otimo, "grade": grade, "M": M}


def rd_empilhado_honesto(s_mil, y, corte_mil, *, grupo=None, h_mil: float = H_PRINCIPAL_MIL,
                         M: float | None = None, kernel: str = "triangular", peso=None, cluster=None,
                         ids_unidade=None, efeitos_fixos=None, variancia: str | None = None,
                         J: int = J_VIZINHOS) -> dict:
    """IC honesto do estimador empilhado, com os pesos a_i da regressão empilhada.

    Estimando: sum_g omega_g tau_g (`pesos_grupos`). Viés máximo
    B = (M/2) sum_i |a_i| r_i^2 sob |f_g''| <= M em cada grupo e lado; o resto
    do modelo (EF aditivos, inclinações comuns dentro do grupo) é suposto
    correto. M = None: máximo da regra de bolso por grupo, calculada com as
    linhas daquele grupo (o chamador restringe o suporte pelas linhas que
    passa). Variância: "cluster" (padrão com cluster; obrigatória quando há
    unidade repetida), "ehw" ou "nn" (vizinhos na célula grupo x lado).
    """
    if variancia is None:
        variancia = "cluster" if cluster is not None else "nn"
    if variancia == "nn" and cluster is not None:
        raise ValueError("variancia por vizinhos supoe observacoes independentes; use 'cluster'")
    base = rd_empilhado(s_mil, y, corte_mil, grupo=grupo, h_mil=h_mil, kernel=kernel, peso=peso, cluster=cluster,
                        ids_unidade=ids_unidade, efeitos_fixos=efeitos_fixos, detalhes=True)
    res = {k: v for k, v in base.items() if k != "_detalhes"}
    origem = "informado"
    if M is None and "_detalhes" in base:
        d = base["_detalhes"]
        ms = {}
        for grp in sorted(np.unique(d["grupo"]).tolist()):
            em = d["grupo"] == grp
            cortes = np.unique(d["corte"][em])
            if cortes.size != 1:
                raise ValueError(f"grupo {grp} com mais de um corte: M por grupo indefinido")
            ms[grp] = m_regra_de_bolso(d["s"][em], d["y"][em], float(cortes[0]))["M"]
        res["M_por_grupo"] = ms
        M = float(max(ms.values())) if all(math.isfinite(v) for v in ms.values()) else float("nan")
        origem = "regra_de_bolso (maximo entre grupos)"
    res.update({"M": M, "M_origem": origem, "variancia": variancia, "classe": "Taylor (|f''| <= M por grupo e lado)",
                "ep_convencional": base["ep"]})
    if "_detalhes" not in base or M is None or not math.isfinite(M):
        res.update({"ep": float("nan"), "ic95_inf": float("nan"), "ic95_sup": float("nan"), "p_valor": float("nan")})
        return res
    d = base["_detalhes"]
    usa = d["usa"]
    r = d["x"][usa]
    celula = np.char.add(d["grupo"][usa], np.where(d["t"][usa] > 0, "|acima", "|abaixo"))
    var = _variancia_estimador(d["a"], d["fit"], variancia, r, d["y"][usa], celula, J)
    res.update(_honesto_de_pesos(base, d["a"], r, M, var))
    return res


def rd_honesto_relato(s_mil, y, corte_mil: float, *, M: float | None = None, fatores_M: Sequence[float] = (0.5, 1.0, 2.0),
                      h_fixo_mil: float = H_PRINCIPAL_MIL, grade_h_mil: Sequence[float] = GRADE_H_MIL,
                      suporte_mil: tuple[float, float] | None = None, **kw) -> pd.DataFrame:
    """Tabela do protocolo: IC honesto em h fixo e em h ótimo, para M x {0,5; 1; 2}.

    M base = regra de bolso (se None). Para cada fator, o h ótimo é escolhido
    de novo na grade com aquele M.
    """
    regra = None
    if M is None:
        regra = m_regra_de_bolso(s_mil, y, corte_mil, suporte_mil=suporte_mil)
        M = regra["M"]
    linhas = []
    for f in fatores_M:
        r = rd_honesto_h_otimo(s_mil, y, corte_mil, M=f * M, grade_h_mil=grade_h_mil, h_fixo_mil=h_fixo_mil, **kw)
        for esp in ("h_fixo", "h_otimo"):
            x = r[esp]
            linhas.append({
                "especificacao": esp, "fator_M": f, "M": f * M, "M_base": M,
                "M_origem": "regra_de_bolso" if regra is not None else "informado",
                "h": x.get("h"), "h_mil": x.get("h_mil"), "tau": x.get("tau"), "ep": x.get("ep"),
                "ep_convencional": x.get("ep_convencional"), "vies_max": x.get("vies_max"), "cv": x.get("cv"),
                "ic95_inf": x.get("ic95_inf"), "ic95_sup": x.get("ic95_sup"), "semi_amplitude": x.get("semi_amplitude"),
                "p_valor": x.get("p_valor"), "n_abaixo": x.get("n_abaixo"), "n_acima": x.get("n_acima"),
                "variancia": x.get("variancia"), "nota": x.get("nota", ""),
            })
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------------------
# 4. Poisson local
# ---------------------------------------------------------------------------

def rd_poisson_local(s_mil, y, corte_mil: float, h_mil: float = H_PRINCIPAL_MIL, *, offset=None,
                     kernel: str = "triangular", peso=None, cluster=None, ids_unidade=None,
                     pequena_amostra: bool = True, max_iter: int = 200, tol: float = 1e-10) -> dict:
    """RDD com Poisson local: log mu = offset + a + b x + tau T + d T x, pseudo-verossimilhança ponderada.

    Pesos = kernel x `peso`; Newton/IRLS com meio-passo quando a
    pseudo-verossimilhança cai. `offset` = log(células) ou log(população).
    tau é o salto em log (exp(tau) - 1 é comparável aos +26% de Dal Bó, Finan
    e Rossi, 2013). EP sanduíche com o mesmo fator do MQP (HC1/CR1; HC0/CR0
    se `pequena_amostra=False`). Lado sem eventos (soma ponderada de y nula):
    o MLE do intercepto daquele lado é -infinito; devolve NaN com nota.
    """
    s = normalizar_s_mil(s_mil)
    n = len(s)
    yv = _vetor(y, n, "y")
    off = _vetor(offset, n, "offset") if offset is not None else np.zeros(n)
    x_mil = s - corte_mil
    w = pesos_kernel(x_mil, h_mil, kernel)
    if peso is not None:
        w = w * _vetor(peso, n, "peso")
    x = x_mil / 1000.0
    t = (x_mil > 0).astype(float)
    usa = (w > 0) & np.isfinite(yv) & np.isfinite(off) & np.isfinite(w)
    if (yv[usa] < 0).any():
        raise ValueError("Poisson local exige y >= 0")
    ab, ac = usa & (x_mil <= 0), usa & (x_mil > 0)
    cl = _rotulos(cluster, n)
    ids = _rotulos(ids_unidade, n) if ids_unidade is not None else cl
    res = _resultado_vazio(h_mil)
    res.update({"corte_mil": corte_mil, "kernel": kernel, "n_abaixo": _contar(ids, ab), "n_acima": _contar(ids, ac),
                "n_obs": int(usa.sum()), "mass_points_abaixo": int(np.unique(s[ab]).size),
                "mass_points_acima": int(np.unique(s[ac]).size), "eventos_abaixo": float(np.sum(yv[ab])),
                "eventos_acima": float(np.sum(yv[ac])), "efeito_relativo": float("nan"),
                "efeito_relativo_ic95_inf": float("nan"), "efeito_relativo_ic95_sup": float("nan"),
                "convergiu": False, "iteracoes": 0})
    if res["mass_points_abaixo"] < 2 or res["mass_points_acima"] < 2:
        res["nota"] = "suporte insuficiente: menos de 2 mass points com peso positivo em algum lado"
        return res
    sem = [lado for lado, m in (("abaixo", ab), ("acima", ac)) if np.sum(w[m] * yv[m]) <= 0]
    if sem:
        res["nota"] = f"lado sem eventos ({', '.join(sem)}): salto em log nao identificado (MLE em -infinito)"
        return res
    X = np.column_stack([np.ones(n), x, t, t * x])[usa]
    yy, ww, oo = yv[usa], w[usa], off[usa]

    def pseudo_ll(b: np.ndarray) -> float:
        with np.errstate(over="ignore"):
            eta = oo + X @ b
            return float(np.sum(ww * (yy * eta - np.exp(eta))))

    beta = np.zeros(4)
    beta[0] = math.log(np.sum(ww * yy) / np.sum(ww * np.exp(oo)))
    ll = pseudo_ll(beta)
    convergiu = False
    it = 0
    for it in range(1, max_iter + 1):
        mu = np.exp(oo + X @ beta)
        grad = X.T @ (ww * (yy - mu))
        H = X.T @ (X * (ww * mu)[:, None])
        passo = np.linalg.solve(H, grad)
        fator = 1.0
        while True:
            novo = beta + fator * passo
            ll_novo = pseudo_ll(novo)
            if (math.isfinite(ll_novo) and ll_novo >= ll - 1e-12 * abs(ll)) or fator < 1e-8:
                break
            fator /= 2.0
        beta, ll = novo, ll_novo
        if np.max(np.abs(fator * passo)) < tol:
            convergiu = True
            break
    res["iteracoes"] = it
    res["convergiu"] = convergiu
    if not convergiu or not np.isfinite(beta).all():
        res["nota"] = "IRLS nao convergiu (possivel separacao: eventos concentrados em poucos mass points)"
        return res
    mu = np.exp(oo + X @ beta)
    bread = np.linalg.inv(X.T @ (X * (ww * mu)[:, None]))
    score = X * (ww * (yy - mu))[:, None]
    m_obs, k = len(yy), 4
    if cl is None:
        meat = score.T @ score
        fator = m_obs / (m_obs - k) if pequena_amostra else 1.0
    else:
        _, idx = np.unique(cl[usa], return_inverse=True)
        G = int(idx.max()) + 1
        if G < 2:
            res["nota"] = "menos de 2 clusters"
            return res
        S = np.zeros((G, k))
        np.add.at(S, idx, score)
        meat = S.T @ S
        fator = (G / (G - 1)) * ((m_obs - 1) / (m_obs - k)) if pequena_amostra else 1.0
        res["n_clusters"] = G
    V = bread @ meat @ bread * fator
    _inferencia_normal(res, float(beta[2]), float(math.sqrt(max(V[2, 2], 0.0))))
    res.update({"efeito_relativo": math.expm1(res["tau"]),
                "efeito_relativo_ic95_inf": math.expm1(res["ic95_inf"]),
                "efeito_relativo_ic95_sup": math.expm1(res["ic95_sup"]),
                "intercepto_abaixo_log": float(beta[0])})
    return res


# ---------------------------------------------------------------------------
# 5. Diferença em descontinuidades
# ---------------------------------------------------------------------------

def diferenca_pos_pre(painel: pd.DataFrame, *, col_unidade: str, col_periodo: str, col_y: str,
                      periodos_pre: Sequence, periodos_pos: Sequence, exigir_completo: bool = True) -> pd.DataFrame:
    """Por unidade: y_pre = média(pré), y_pos = média(pós), delta = y_pos - y_pre.

    Com `exigir_completo`, unidade sem todos os períodos de pré ou de pós (ou
    com y ausente) fica com delta NaN (ausência não vira zero).
    """
    p = painel[[col_unidade, col_periodo, col_y]]
    if p.duplicated([col_unidade, col_periodo]).any():
        raise ValueError("painel com unidade-periodo repetido")
    out = pd.DataFrame(index=pd.Index(sorted(p[col_unidade].unique()), name=col_unidade))
    for nome, periodos in (("pre", list(periodos_pre)), ("pos", list(periodos_pos))):
        sub = p[p[col_periodo].isin(periodos)]
        agg = sub.groupby(col_unidade)[col_y].agg(["mean", "count"])
        out[f"y_{nome}"] = agg["mean"].reindex(out.index)
        out[f"n_{nome}"] = agg["count"].reindex(out.index).fillna(0).astype(int)
        if exigir_completo:
            out.loc[out[f"n_{nome}"] < len(periodos), f"y_{nome}"] = np.nan
    out["delta"] = out["y_pos"] - out["y_pre"]
    return out.reset_index()


def rd_dird_delta(s_mil, y_pos, y_pre, corte_mil: float, h_mil: float = H_PRINCIPAL_MIL, **kw) -> dict:
    """DiRD (a): `rd_local_linear` sobre delta = y_pos - y_pre (uma linha por unidade).

    Remove a parte fixa no tempo de qualquer descontinuidade no corte (por
    exemplo, o teto do PMMB anterior ao PMM-E). Aceita os argumentos de
    `rd_local_linear`.
    """
    yp = np.asarray(y_pos, dtype=float)
    yr = np.asarray(y_pre, dtype=float)
    res = rd_local_linear(s_mil, yp - yr, corte_mil, h_mil, **kw)
    res["estimador"] = "DiRD: RDD local linear sobre delta = media(pos) - media(pre)"
    return res


def rd_dird_painel(s_mil, y, pos, corte_mil: float, unidade, h_mil: float = H_PRINCIPAL_MIL, *,
                   kernel: str = "triangular", peso=None, pequena_amostra: bool = True,
                   detalhes: bool = False) -> dict:
    """DiRD (b): painel empilhado unidade x período, tau = coeficiente de T x pós.

    y_it = a + b x + g T + d T x + pos (a' + b' x + tau T + d' T x) + e, com
    peso de kernel da unidade (x `peso`), cluster por unidade (CR1). Com painel
    balanceado e os mesmos pesos, o ponto é idêntico ao de `rd_dird_delta`, e
    o EP CR0 (`pequena_amostra=False`) é idêntico ao HC0 de (a).
    """
    s = normalizar_s_mil(s_mil)
    n = len(s)
    yv = _vetor(y, n, "y")
    pv = _vetor(pos, n, "pos")
    if not np.isin(pv, (0.0, 1.0)).all():
        raise ValueError("pos deve ser 0/1")
    uni = _rotulos(unidade, n)
    x_mil = s - corte_mil
    w = pesos_kernel(x_mil, h_mil, kernel)
    if peso is not None:
        w = w * _vetor(peso, n, "peso")
    x = x_mil / 1000.0
    t = (x_mil > 0).astype(float)
    X = np.column_stack([np.ones(n), x, t, t * x, pv, pv * x, t * pv, t * pv * x])
    nomes = ["const", "x", "T", "T_x", "pos", "pos_x", "T_pos", "T_pos_x"]
    usa = (w > 0) & np.isfinite(yv)
    ab, ac = usa & (x_mil <= 0), usa & (x_mil > 0)
    res = _resultado_vazio(h_mil)
    res.update({"corte_mil": corte_mil, "kernel": kernel, "n_abaixo": _contar(uni, ab), "n_acima": _contar(uni, ac),
                "n_obs": int(usa.sum()), "tau_pre": float("nan"),
                "estimador": "DiRD em painel: coeficiente de T x pos, CR1 por unidade"})
    for per in (0.0, 1.0):
        em = usa & (pv == per)
        if np.unique(s[em & (x_mil <= 0)]).size < 2 or np.unique(s[em & (x_mil > 0)]).size < 2:
            res["nota"] = "suporte insuficiente: menos de 2 mass points por lado em pre ou pos"
            return res
    fit = mqp_sanduiche(X[usa], yv[usa], w[usa], nomes=nomes, cluster=uni[usa], pequena_amostra=pequena_amostra)
    if "erro" in fit:
        res["nota"] = fit["erro"]
        return res
    i = fit["nomes"].index("T_pos")
    _inferencia_normal(res, float(fit["beta"][i]), float(math.sqrt(max(fit["V"][i, i], 0.0))))
    res["n_clusters"] = fit["G"]
    res["tau_pre"] = float(fit["coef"]["T"])
    if detalhes:
        res["_detalhes"] = {"fit": fit, "usa": usa}
    return res


def rd_estudo_evento(painel: pd.DataFrame, *, col_unidade: str, col_periodo: str, col_y: str, col_s: str,
                     corte_mil: float, periodo_ref, h_mil: float = H_PRINCIPAL_MIL, periodos: Sequence | None = None,
                     col_peso: str | None = None, **kw) -> pd.DataFrame:
    """DiRD (c): para cada período t, RDD de (y_t - y_ref) por unidade; uma linha por período.

    A linha do período de referência é marcada (`referencia = True`) e não é
    estimada: tau e EP ficam NaN (a normalização a zero cabe ao gráfico).
    Unidade sem y em t ou em ref fica fora daquele período. `col_s` (e
    `col_peso`) deve ser constante dentro da unidade.
    """
    cols = [col_unidade, col_periodo, col_y, col_s] + ([col_peso] if col_peso else [])
    p = painel[cols]
    for c in [col_s] + ([col_peso] if col_peso else []):
        if (p.groupby(col_unidade)[c].nunique(dropna=False) > 1).any():
            raise ValueError(f"{c} varia dentro da unidade")
    larga = p.pivot(index=col_unidade, columns=col_periodo, values=col_y)
    if periodo_ref not in larga.columns:
        raise ValueError(f"periodo de referencia {periodo_ref} ausente do painel")
    unid = p.drop_duplicates(col_unidade).set_index(col_unidade).reindex(larga.index)
    s = unid[col_s].to_numpy(dtype=float)
    pe = unid[col_peso].to_numpy(dtype=float) if col_peso else None
    ref = larga[periodo_ref].to_numpy(dtype=float)
    linhas = []
    for per in (sorted(larga.columns) if periodos is None else list(periodos)):
        if per == periodo_ref:
            linhas.append({"periodo": per, "referencia": True, "tau": float("nan"), "ep": float("nan"),
                           "ic95_inf": float("nan"), "ic95_sup": float("nan"), "p_valor": float("nan"),
                           "n_abaixo": None, "n_acima": None, "h": h_mil / 1000.0,
                           "nota": "periodo de referencia: normalizado (y_ref - y_ref), nao estimado"})
            continue
        d = larga[per].to_numpy(dtype=float) - ref
        r = rd_local_linear(s, d, corte_mil, h_mil, peso=pe, **kw)
        linhas.append({"periodo": per, "referencia": False, "tau": r["tau"], "ep": r["ep"],
                       "ic95_inf": r["ic95_inf"], "ic95_sup": r["ic95_sup"], "p_valor": r["p_valor"],
                       "n_abaixo": r["n_abaixo"], "n_acima": r["n_acima"], "h": r["h"], "nota": r["nota"]})
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------------------
# 6. Índices (Kling, Liebman e Katz, 2007; Anderson, 2008)
# ---------------------------------------------------------------------------

def mascara_referencia(s_mil, corte_mil, h_mil: float = H_PRINCIPAL_MIL) -> np.ndarray:
    """Unidades de referência para padronizar: lado abaixo do corte dentro da janela, -h < x <= 0."""
    s = normalizar_s_mil(s_mil)
    x = s - _vetor(corte_mil, len(s), "corte_mil")
    return (x > -h_mil) & (x <= 0)


def indice_klk(dados: pd.DataFrame, componentes: Sequence[str], *, referencia, sinais: dict | None = None,
               grupo=None, metodo: str = "klk", ddof: int = 1) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Índice de z-scores padronizados pelo grupo de referência, por grupo.

    Para cada grupo (por exemplo, ciclo x corte) e componente k:
    z_ik = sinal_k (y_ik - média_ref) / dp_ref, com média e desvio-padrão
    (ddof) das linhas de `referencia` do grupo (lado abaixo do corte na
    janela). Sinal pré-especificado: +1 = mais provimento (desistência e tempo
    até preencher entram com -1).
    - "klk": média dos z não ausentes da linha (Kling, Liebman e Katz, 2007).
    - "anderson": média ponderada com pesos = somas das linhas da inversa da
      covariância dos z no grupo de referência (Anderson, 2008), calculada com
      pares completos; com ausência, sum w_k z_k / sum w_k sobre os
      componentes presentes.
    Componente sem variação na referência (ou com menos de 2 valores) fica
    ausente naquele grupo e é registrado. Devolve (saída alinhada a `dados`
    com z_<k>, indice e n_componentes; parâmetros por grupo x componente).
    """
    if metodo not in ("klk", "anderson"):
        raise ValueError("metodo deve ser 'klk' ou 'anderson'")
    n = len(dados)
    componentes = list(componentes)
    sinais = {k: 1.0 for k in componentes} | {k: float(v) for k, v in (sinais or {}).items()}
    if any(v not in (1.0, -1.0) for v in sinais.values()):
        raise ValueError("sinais devem ser +1 ou -1")
    ref = np.asarray(referencia, dtype=bool)
    if ref.shape != (n,):
        raise ValueError("referencia com tamanho errado")
    g = _rotulos(grupo, n) if grupo is not None else np.full(n, "todos")
    K = len(componentes)
    Zs = np.full((n, K), np.nan)
    W = np.full((n, K), np.nan)
    params = []
    for grp in sorted(np.unique(g).tolist()):
        em = g == grp
        r = em & ref
        for j, comp in enumerate(componentes):
            v = dados[comp].to_numpy(dtype=float)
            vr = v[r & np.isfinite(v)]
            mu = float(vr.mean()) if vr.size else float("nan")
            dp = float(vr.std(ddof=ddof)) if vr.size > ddof else float("nan")
            nota = ""
            if vr.size < 2 or not (dp > 0):
                nota = "componente sem variacao (ou < 2 valores) na referencia do grupo: ausente no indice"
            else:
                Zs[em, j] = sinais[comp] * (v[em] - mu) / dp
            params.append({"grupo": grp, "componente": comp, "sinal": sinais[comp], "media_ref": mu, "dp_ref": dp,
                           "n_ref": int(vr.size), "peso_anderson": float("nan"), "nota": nota})
        if metodo == "anderson":
            validos = [j for j in range(K) if np.isfinite(Zs[em, j]).any()]
            cov = pd.DataFrame(Zs[r][:, validos]).cov(min_periods=2, ddof=ddof).to_numpy()
            try:
                inv = np.linalg.inv(cov)
                nota_inv = ""
            except np.linalg.LinAlgError:
                inv = np.linalg.pinv(cov)
                nota_inv = "covariancia singular: pseudo-inversa"
            pesos = inv.sum(axis=1)
            for jj, j in enumerate(validos):
                W[em, j] = pesos[jj]
                linha = next(p for p in params if p["grupo"] == grp and p["componente"] == componentes[j])
                linha["peso_anderson"] = float(pesos[jj])
                linha["nota"] = _juntar_notas(linha["nota"], nota_inv)
    presentes = np.isfinite(Zs)
    n_comp = presentes.sum(axis=1)
    if metodo == "klk":
        with np.errstate(invalid="ignore", divide="ignore"):
            indice = np.where(n_comp > 0, np.nansum(Zs, axis=1) / np.maximum(n_comp, 1), np.nan)
    else:
        Wp = np.where(presentes, W, 0.0)
        soma_w = Wp.sum(axis=1)
        with np.errstate(invalid="ignore", divide="ignore"):
            indice = np.where((n_comp > 0) & (soma_w > 0), np.nansum(np.where(presentes, Zs * W, 0.0), axis=1) / soma_w,
                              np.nan)
    saida = pd.DataFrame({f"z_{c}": Zs[:, j] for j, c in enumerate(componentes)}, index=dados.index)
    saida["indice"] = indice
    saida["n_componentes"] = n_comp
    return saida, pd.DataFrame(params)


# ---------------------------------------------------------------------------
# 7. Testes múltiplos
# ---------------------------------------------------------------------------

def holm(pvalores) -> np.ndarray:
    """p ajustados de Holm (1979); NaN fica NaN e não conta em m."""
    p = np.asarray(pvalores, dtype=float)
    out = np.full(p.shape, np.nan)
    idx = np.flatnonzero(np.isfinite(p))
    m = idx.size
    if m == 0:
        return out
    ordem = idx[np.argsort(p[idx], kind="stable")]
    adj = np.minimum(1.0, (m - np.arange(m)) * p[ordem])
    out[ordem] = np.maximum.accumulate(adj)
    return out


def qvalores_bky(pvalores) -> np.ndarray:
    """q-valores aguçados de Benjamini, Krieger e Yekutieli (2006), algoritmo de Anderson (2008).

    Para q = 1,000; 0,999; ...; 0,001: q1 = q/(1+q); 1o estágio step-up com
    q1 rejeita R1; q2 = q1 m/(m - R1); 2o estágio step-up com q2 rejeita R2;
    as R2 menores hipóteses recebem q. O q-valor é o menor q da grade em que a
    hipótese é rejeitada (1 se nunca). NaN fica NaN e não conta em m.
    """
    p = np.asarray(pvalores, dtype=float)
    out = np.full(p.shape, np.nan)
    idx = np.flatnonzero(np.isfinite(p))
    m = idx.size
    if m == 0:
        return out
    ordem = idx[np.argsort(p[idx], kind="stable")]
    ps = p[ordem]
    rank = np.arange(1, m + 1)
    q_out = np.ones(m)
    for k in range(1000, 0, -1):
        q = k / 1000.0
        q1 = q / (1.0 + q)
        rej1 = ps <= q1 * rank / m
        R1 = int(rank[rej1].max()) if rej1.any() else 0
        q2 = q1 * m / (m - R1) if R1 < m else float("inf")
        rej2 = ps <= q2 * rank / m
        R2 = int(rank[rej2].max()) if rej2.any() else 0
        q_out[rank <= R2] = q
    out[ordem] = q_out
    return out


# ---------------------------------------------------------------------------
# 8. Limites de Lee no corte
# ---------------------------------------------------------------------------

def _multiplicador_aparo(y: np.ndarray, w: np.ndarray, q: float, de_cima: bool) -> np.ndarray:
    """Multiplicador em [0, 1] que retira exatamente a fração q da massa de peso, pelo topo ou pela base de y."""
    chave = -y if de_cima else y
    ordem = np.lexsort((np.arange(len(y)), chave))
    wo = w[ordem]
    antes = np.cumsum(wo) - wo
    alvo = q * wo.sum()
    removido = np.clip(alvo - antes, 0.0, wo)
    mult_o = np.where(wo > 0, 1.0 - removido / np.where(wo > 0, wo, 1.0), 1.0)
    mult = np.empty_like(mult_o)
    mult[ordem] = mult_o
    return mult


def limites_lee_rd(s_mil, y, selecionado, corte_mil: float, h_mil: float = H_PRINCIPAL_MIL, *,
                   kernel: str = "triangular", peso=None, cluster=None, ids_unidade=None) -> dict:
    """Limites de Lee (2009) locais para outcome observado só nos selecionados (ex.: barema dos alocados).

    Passos (versão local, com aproximações registradas):
    1. Taxas de seleção no corte: p0 = intercepto do local linear de S pelo
       lado abaixo; p1 = p0 + salto. Monotonicidade de Lee: o tratamento só
       acrescenta (ou só retira) selecionados.
    2. Fração aparada q = |p1 - p0| / máx(p0, p1) no lado de maior seleção.
    3. Entre os selecionados daquele meio-janela, retira-se a fração q da
       massa de peso do kernel pelo topo de y (e, no outro limite, pela base),
       com aparo fracionário da observação de fronteira.
    4. Local linear de y nos selecionados (aparados de um lado) dá os dois
       limites; tau_inf = menor, tau_sup = maior.
    Aproximações: (i) o quantil condicional de y no corte é aproximado pelo
    quantil ponderado pelo kernel no meio-janela (ignora a variação de y com x
    dentro da janela); (ii) o EP de cada limite é o do local linear na amostra
    aparada e não incorpora a incerteza de q nem do quantil; (iii) o IC
    95% relatado é conservador: [tau_inf - 1,96 ep_inf; tau_sup + 1,96 ep_sup].
    """
    s = normalizar_s_mil(s_mil)
    n = len(s)
    yv = _vetor(y, n, "y")
    sel = _vetor(selecionado, n, "selecionado")
    if not np.isin(sel[np.isfinite(sel)], (0.0, 1.0)).all():
        raise ValueError("selecionado deve ser 0/1")
    pv = _vetor(peso, n, "peso") if peso is not None else np.ones(n)
    comuns = dict(kernel=kernel, cluster=cluster, ids_unidade=ids_unidade)
    rs = rd_local_linear(s, sel, corte_mil, h_mil, peso=pv, detalhes=True, **comuns)
    res = {"tau_inf": float("nan"), "tau_sup": float("nan"), "ep_inf": float("nan"), "ep_sup": float("nan"),
           "ic95_inf": float("nan"), "ic95_sup": float("nan"), "p0_selecao": float("nan"),
           "p1_selecao": float("nan"), "salto_selecao": rs["tau"], "q_aparo": float("nan"), "lado_aparado": None,
           "tau_selecionados": float("nan"), "ep_selecionados": float("nan"), "n_abaixo": None, "n_acima": None,
           "h": h_mil / 1000.0, "h_mil": h_mil, "nota": ""}
    if "_detalhes" not in rs:
        res["nota"] = f"taxa de selecao nao estimada: {rs['nota']}"
        return res
    p0 = float(rs["_detalhes"]["fit"]["coef"]["const"])
    p1 = p0 + float(rs["tau"])
    res.update({"p0_selecao": p0, "p1_selecao": p1})
    if not (p0 > 0 and p1 > 0):
        res["nota"] = "taxa de selecao estimada nao positiva em algum lado: limites indefinidos"
        return res
    ok = (sel == 1) & np.isfinite(yv)
    cl_ok = np.asarray(cluster)[ok] if cluster is not None else None
    ids_ok = np.asarray(ids_unidade)[ok] if ids_unidade is not None else None
    ingenuo = rd_local_linear(s[ok], yv[ok], corte_mil, h_mil, peso=pv[ok], kernel=kernel, cluster=cl_ok,
                              ids_unidade=ids_ok)
    res.update({"tau_selecionados": ingenuo["tau"], "ep_selecionados": ingenuo["ep"],
                "n_abaixo": ingenuo["n_abaixo"], "n_acima": ingenuo["n_acima"]})
    acima = p1 >= p0
    q = (p1 - p0) / p1 if acima else (p0 - p1) / p0
    res.update({"q_aparo": q, "lado_aparado": "acima" if acima else "abaixo"})
    x_mil = s - corte_mil
    wk = pesos_kernel(x_mil, h_mil, kernel) * pv
    lado = ok & (wk > 0) & ((x_mil > 0) if acima else (x_mil <= 0))
    limites = []
    for de_cima in (True, False):
        mult = np.ones(n)
        mult[lado] = _multiplicador_aparo(yv[lado], wk[lado], q, de_cima)
        r = rd_local_linear(s[ok], yv[ok], corte_mil, h_mil, peso=(pv * mult)[ok], kernel=kernel,
                            cluster=cl_ok, ids_unidade=ids_ok)
        limites.append((r["tau"], r["ep"], r["nota"]))
    (t_a, e_a, n_a), (t_b, e_b, n_b) = limites
    (t_inf, e_inf), (t_sup, e_sup) = sorted([(t_a, e_a), (t_b, e_b)], key=lambda z: z[0])
    res.update({"tau_inf": t_inf, "tau_sup": t_sup, "ep_inf": e_inf, "ep_sup": e_sup,
                "ic95_inf": t_inf - Z_975 * e_inf, "ic95_sup": t_sup + Z_975 * e_sup,
                "nota": _juntar_notas(n_a, n_b, "aproximacoes: quantil no meio-janela; EP sem incerteza de q; "
                                                  "IC conservador")})
    return res


# ---------------------------------------------------------------------------
# 9. Local randomization
# ---------------------------------------------------------------------------

def matriz_permutacao(n: int, n1: int, r: int, semente: Sequence[int]) -> np.ndarray:
    """R x n indicadoras de "tratado" sob permutação completa (n1 fixo). Igual à do E5 (11)."""
    rng = np.random.default_rng(list(semente))
    ordem = np.argsort(rng.random((r, n)), axis=1, kind="stable")
    P = np.zeros((r, n))
    np.put_along_axis(P, ordem[:, :n1], 1.0, axis=1)
    return P


def fisher_dif_medias(y, t, *, n_perm: int = N_PERMUTACOES, semente: Sequence[int] = (SEMENTE,),
                      bloco_max: int = 5_000_000) -> dict:
    """Diferença de médias (acima - abaixo) e p de Fisher bicaudal sob o nulo exato de efeito zero.

    p = (1 + #{|T_perm| >= |T_obs|}) / (R + 1). As permutações são geradas em
    blocos de linhas com o mesmo fluxo aleatório de `matriz_permutacao`
    (resultado idêntico ao do E5 com a mesma semente, sem montar a matriz
    inteira). `ep_permutacao` = desvio-padrão da estatística permutada.
    """
    yv = np.asarray(y, dtype=float)
    tv = np.asarray(t, dtype=bool)
    ok = np.isfinite(yv)
    yv, tv = yv[ok], tv[ok]
    n, n1 = len(yv), int(tv.sum())
    n0 = n - n1
    res = {"tau": float("nan"), "p_valor": float("nan"), "ep_permutacao": float("nan"), "n_abaixo": n0,
           "n_acima": n1, "n_perm": n_perm, "semente": list(semente), "nota": ""}
    if n0 < 1 or n1 < 1:
        res["nota"] = "lado vazio"
        return res
    obs = float(yv[tv].mean() - yv[~tv].mean())
    rng = np.random.default_rng(list(semente))
    tamanho = max(1, bloco_max // max(n, 1))
    stats_perm = []
    tot = yv.sum()
    feitos = 0
    while feitos < n_perm:
        rr = min(tamanho, n_perm - feitos)
        ordem = np.argsort(rng.random((rr, n)), axis=1, kind="stable")
        P = np.zeros((rr, n))
        np.put_along_axis(P, ordem[:, :n1], 1.0, axis=1)
        sy = P @ yv
        stats_perm.append(sy / n1 - (tot - sy) / n0)
        feitos += rr
    perm = np.concatenate(stats_perm)
    res.update({"tau": obs, "p_valor": float((1 + np.sum(np.abs(perm) >= abs(obs) - TOL_PERM)) / (n_perm + 1)),
                "ep_permutacao": float(np.std(perm, ddof=1)) if n_perm > 1 else float("nan")})
    return res


def rl_janela(s_mil, y, corte_mil: float, w_mil: float, *, n_perm: int = N_PERMUTACOES,
              semente: Sequence[int] | None = None) -> dict:
    """Local randomization na janela (c - w, c] U (c, c + w]: diferença de médias e Fisher.

    Semente padrão: (20261018, corte_mil, w_mil).
    """
    s = normalizar_s_mil(s_mil)
    yv = _vetor(y, len(s), "y")
    x = s - corte_mil
    dentro = (x > -w_mil) & (x <= w_mil) & np.isfinite(yv)
    sem = tuple(semente) if semente is not None else (SEMENTE, int(round(corte_mil)), int(round(w_mil)))
    res = fisher_dif_medias(yv[dentro], x[dentro] > 0, n_perm=n_perm, semente=sem)
    res.update({"corte_mil": corte_mil, "w_mil": w_mil, "h": w_mil / 1000.0, "h_mil": w_mil,
                "estimador": "local randomization: diferenca de medias, p de Fisher"})
    return res
