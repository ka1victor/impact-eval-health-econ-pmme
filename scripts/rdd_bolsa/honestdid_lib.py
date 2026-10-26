"""Sensibilidade de Rambachan e Roth (2023) para estudos de evento, em numpy e scipy (protocolo 59, parte A).

Não há R nem o pacote HonestDiD no ambiente; esta é uma implementação própria, validada em casos sintéticos que se
resolvem à mão (`tests/test_honestdid.py`). Funções puras: recebem β̂ e Σ e devolvem conjuntos e intervalos.

Notação (Rambachan e Roth, 2023)
--------------------------------
β = τ + δ, com o mês de referência e = −1 normalizado (β(−1) = δ(−1) = 0, fora do vetor). O vetor β̂ tem os
T_pre coeficientes do pré em ordem crescente de e (e = −T_pre−1, ..., −2) seguidos dos T_post do pós (e = 0, ...,
T_post−1). τ_pré = 0, logo δ_pré = β_pré. O alvo é θ = l′τ_pós.

Restrições
----------
- Magnitude relativa Δ^RM(M̄): |δ_{t+1} − δ_t| ≤ M̄ · max_{s<0} |δ_{s+1} − δ_s| para toda diferença consecutiva do
  pós (inclusive da referência para e = 0). É a união, sobre a diferença do pré s e o sinal ±, dos poliedros
  {δ : |δ_{t+1} − δ_t| ≤ M̄ · ±(δ_{s+1} − δ_s) ∀ t ≥ 0; ±(δ_{s+1} − δ_s) ≥ 0}.
- Suavidade Δ^SD(M): |(δ_{t+1} − δ_t) − (δ_t − δ_{t−1})| ≤ M para toda segunda diferença da sequência com a
  referência.

Inferência
----------
- Δ^SD: FLCI (Armstrong e Kolesár, 2018; Rambachan e Roth, 2023, §4). Estimador afim v′β̂ com v_pós = l; o viés
  máximo em Δ^SD(M) é M · min ‖w‖₁ sujeito a D′w = v (dual do PL), D = segundas diferenças. Meio-comprimento
  σ_v · cv_α(viés/σ_v), cv_α(b) = quantil 1 − α de |N(b, 1)|; v escolhido para minimizar o meio-comprimento.
- Δ^RM: teste condicional de Andrews, Roth e Pakes (2023) em cada poliedro; o IC é o conjunto de θ̄ não
  rejeitado em ao menos um poliedro (relata-se o envelope). Truncagem (v_lo, v_up) por dois PL
  linear-fracionários (Charnes–Cooper). Teste condicional puro (não o híbrido C-LF do pacote).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy import optimize, stats

TOL = 1e-9
N_SIM_LF = 1000          # simulações do valor crítico LF do híbrido (como no pacote HonestDiD)
SEMENTE_LF = 20261025


# ---------------------------------------------------------------------------
# Matrizes da sequência com a referência
# ---------------------------------------------------------------------------

def matriz_aumentada(T_pre: int, T_post: int) -> np.ndarray:
    """P ((T+1) × T): insere o zero da referência (e = −1) entre o pré e o pós."""
    T = T_pre + T_post
    P = np.zeros((T + 1, T))
    for i in range(T_pre):
        P[i, i] = 1.0
    for j in range(T_post):
        P[T_pre + 1 + j, T_pre + j] = 1.0
    return P


def primeiras_diferencas(T_pre: int, T_post: int) -> np.ndarray:
    """F (T × T): linha i = δ_aum[i+1] − δ_aum[i]; as T_pre primeiras são do pré, as T_post seguintes do pós."""
    T = T_pre + T_post
    F = np.zeros((T, T + 1))
    for i in range(T):
        F[i, i], F[i, i + 1] = -1.0, 1.0
    return F @ matriz_aumentada(T_pre, T_post)


def segundas_diferencas(T_pre: int, T_post: int) -> np.ndarray:
    """S ((T−1) × T): segundas diferenças da sequência aumentada, em termos de δ."""
    T = T_pre + T_post
    S = np.zeros((T - 1, T + 1))
    for i in range(T - 1):
        S[i, i], S[i, i + 1], S[i, i + 2] = 1.0, -2.0, 1.0
    return S @ matriz_aumentada(T_pre, T_post)


def pecas_rm(T_pre: int, T_post: int, Mbar: float) -> list[tuple[tuple[int, int], np.ndarray]]:
    """Poliedros {δ : A δ ≤ 0} cuja união é Δ^RM(M̄); chave (s, sinal)."""
    F = primeiras_diferencas(T_pre, T_post)
    pecas = []
    for s in range(T_pre):
        for sg in (1, -1):
            ref = sg * F[s]
            linhas = []
            for j in range(T_pre, T_pre + T_post):
                linhas.append(F[j] - Mbar * ref)
                linhas.append(-F[j] - Mbar * ref)
            linhas.append(-ref)
            pecas.append(((s, sg), np.vstack(linhas)))
    return pecas


def restricao_sd(T_pre: int, T_post: int, M: float) -> tuple[np.ndarray, np.ndarray]:
    S = segundas_diferencas(T_pre, T_post)
    return np.vstack([S, -S]), np.full(2 * S.shape[0], float(M))


# ---------------------------------------------------------------------------
# Conjunto identificado (PL)
# ---------------------------------------------------------------------------

def _limites_poliedro(beta: np.ndarray, A: np.ndarray, d: np.ndarray, T_pre: int, T_post: int,
                      l: np.ndarray) -> tuple[float, float] | None:
    """[mín, máx] de θ = l′(β_pós − δ_pós) com δ_pré = β_pré e A δ ≤ d; None se vazio."""
    T = T_pre + T_post
    A_eq = np.zeros((T_pre, T))
    A_eq[:, :T_pre] = np.eye(T_pre)
    b_eq = beta[:T_pre]
    c = np.zeros(T)
    c[T_pre:] = l
    base = float(l @ beta[T_pre:])
    lims = []
    for sinal in (1.0, -1.0):
        r = optimize.linprog(sinal * c, A_ub=A, b_ub=d, A_eq=A_eq, b_eq=b_eq, bounds=[(None, None)] * T,
                             method="highs")
        if r.status == 2:
            return None
        if r.status == 3:
            lims.append(sinal * math.inf)
            continue
        if r.status != 0:
            raise RuntimeError(f"PL do conjunto identificado: {r.message}")
        lims.append(sinal * r.fun)
    min_ld, max_ld = lims[0], lims[1]
    return base - max_ld, base - min_ld


def conjunto_identificado_rm(beta, T_pre, T_post, l, Mbar) -> tuple[float, float] | None:
    lo, hi, algum = math.inf, -math.inf, False
    for _, A in pecas_rm(T_pre, T_post, Mbar):
        r = _limites_poliedro(np.asarray(beta, float), A, np.zeros(A.shape[0]), T_pre, T_post, np.asarray(l, float))
        if r is None:
            continue
        algum = True
        lo, hi = min(lo, r[0]), max(hi, r[1])
    return (lo, hi) if algum else None


def conjunto_identificado_sd(beta, T_pre, T_post, l, M) -> tuple[float, float] | None:
    A, d = restricao_sd(T_pre, T_post, M)
    return _limites_poliedro(np.asarray(beta, float), A, d, T_pre, T_post, np.asarray(l, float))


# ---------------------------------------------------------------------------
# FLCI para Δ^SD
# ---------------------------------------------------------------------------

def cv_viesado(b: float, alpha: float = 0.05) -> float:
    """c tal que P(|N(b, 1)| ≤ c) = 1 − α."""
    b = abs(float(b))
    f = lambda c: stats.norm.cdf(c - b) - stats.norm.cdf(-c - b) - (1 - alpha)
    return float(optimize.brentq(f, 0.0, b + 10.0, xtol=1e-12))


@dataclass
class ResultadoFLCI:
    centro: float
    meio: float
    v: np.ndarray
    sd: float
    vies_max: float

    @property
    def ic(self) -> tuple[float, float]:
        return self.centro - self.meio, self.centro + self.meio


def flci_sd(beta, Sigma, T_pre: int, T_post: int, l, M: float, alpha: float = 0.05) -> ResultadoFLCI:
    beta = np.asarray(beta, float)
    Sigma = np.asarray(Sigma, float)
    l = np.asarray(l, float)
    Dm = segundas_diferencas(T_pre, T_post)          # (T−1) × T
    K = Dm.shape[0]
    B = Dm.T[T_pre:, :]                              # restrição v_pós = (D′w)_pós = l
    Q = Dm @ Sigma @ Dm.T
    Q = (Q + Q.T) / 2
    # w sem limite de norma: mínima variância
    Qi = np.linalg.pinv(Q)
    w_inf = Qi @ B.T @ np.linalg.solve(B @ Qi @ B.T, l)
    t_max = float(np.abs(w_inf).sum())
    # menor norma L1 viável
    c = np.ones(2 * K)
    r = optimize.linprog(c, A_eq=np.hstack([B, -B]), b_eq=l, bounds=[(0, None)] * (2 * K), method="highs")
    if r.status != 0:
        raise RuntimeError(f"FLCI: PL da norma mínima: {r.message}")
    t_min = float(r.fun)
    cache: dict[float, tuple[float, np.ndarray]] = {}

    def var_dada_norma(t: float) -> tuple[float, np.ndarray]:
        if t >= t_max - 1e-12:
            return float(w_inf @ Q @ w_inf), w_inf
        key = round(t, 12)
        if key in cache:
            return cache[key]
        Qb = np.block([[Q, -Q], [-Q, Q]])
        x0 = np.concatenate([np.clip(r.x[:K], 0, None), np.clip(r.x[K:], 0, None)])
        cons = [{"type": "eq", "fun": lambda x: np.hstack([B, -B]) @ x - l, "jac": lambda x: np.hstack([B, -B])},
                {"type": "ineq", "fun": lambda x: t - x.sum(), "jac": lambda x: -np.ones_like(x)}]
        sol = optimize.minimize(lambda x: x @ Qb @ x, x0, jac=lambda x: 2 * Qb @ x, constraints=cons,
                                bounds=[(0, None)] * (2 * K), method="SLSQP",
                                options={"ftol": 1e-14, "maxiter": 1000})
        w = sol.x[:K] - sol.x[K:]
        out = (float(w @ Q @ w), w)
        cache[key] = out
        return out

    def meio(t: float) -> float:
        var, _ = var_dada_norma(t)
        sd = math.sqrt(max(var, 0.0))
        if sd <= 0:
            return M * t * 1.0 if M > 0 else 0.0
        return sd * cv_viesado(M * t / sd, alpha)

    if M <= 0 or t_max - t_min < 1e-10:
        t_opt = t_max
    else:
        res = optimize.minimize_scalar(meio, bounds=(t_min, t_max), method="bounded",
                                       options={"xatol": 1e-8 * max(1.0, t_max)})
        cand = [(meio(t_min), t_min), (meio(t_max), t_max), (float(res.fun), float(res.x))]
        t_opt = min(cand)[1]
    var, w = var_dada_norma(t_opt)
    v = Dm.T @ w
    sd = math.sqrt(max(var, 0.0))
    vies = M * float(np.abs(w).sum())
    h = sd * cv_viesado(vies / sd, alpha) if sd > 0 else vies
    return ResultadoFLCI(centro=float(v @ beta), meio=float(h), v=v, sd=sd, vies_max=vies)


# ---------------------------------------------------------------------------
# Teste condicional de Andrews, Roth e Pakes (2023) e IC para Δ^RM
# ---------------------------------------------------------------------------

def _base_alvo(l: np.ndarray) -> np.ndarray:
    """Γ (T_post × T_post) invertível com 1ª linha l′ (as outras: complemento ortogonal de l)."""
    l = np.asarray(l, float)
    if l.size == 1:
        return l.reshape(1, 1)
    _, _, vt = np.linalg.svd(l.reshape(1, -1))
    return np.vstack([l, vt[1:]])


def _lp(c, A_ub=None, b_ub=None, A_eq=None, b_eq=None, n=None):
    return optimize.linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=[(0, None)] * n, method="highs")


def estatistica_lf(xi: np.ndarray, X: np.ndarray, sig: np.ndarray) -> float:
    """η̃(ξ) = máx γ′ξ s.a. γ ≥ 0, X′γ = 0, σ′γ = 1 (−∞ se inviável)."""
    k = xi.size
    eqs, beq = [sig.reshape(1, -1)], [1.0]
    if X.shape[1] > 0:
        eqs.insert(0, X.T)
        beq = [0.0] * X.shape[1] + beq
    r = _lp(-xi, A_eq=np.vstack(eqs), b_eq=np.array(beq), n=k)
    if r.status == 2:
        return -math.inf
    if r.status != 0:
        raise RuntimeError(f"ARP: LF: {r.message}")
    return float(-r.fun)


def valor_critico_lf(X: np.ndarray, SigmaY: np.ndarray, kappa: float, n_sim: int, semente: int) -> float:
    """Quantil 1 − κ de η̃ sob o nulo menos favorável (μ = 0), por simulação (estágio LF do híbrido de ARP)."""
    sig = np.sqrt(np.clip(np.diag(SigmaY), 0, None))
    sig = np.where(sig > 0, sig, 1e-12)
    rng = np.random.default_rng(semente)
    w, V = np.linalg.eigh((SigmaY + SigmaY.T) / 2)
    raiz = V * np.sqrt(np.clip(w, 0, None))
    xs = rng.standard_normal((n_sim, SigmaY.shape[0])) @ raiz.T
    vals = np.array([estatistica_lf(x, X, sig) for x in xs])
    vals = vals[np.isfinite(vals)]
    return float(np.quantile(vals, 1 - kappa)) if vals.size else math.inf


def teste_condicional(Y: np.ndarray, X: np.ndarray, SigmaY: np.ndarray, alpha: float = 0.05,
                      c_lf: float | None = None, kappa: float = 0.0) -> dict:
    """H0: existe τ̃ com E[Y] − X τ̃ ≤ 0. Estatística η̂ = mín η s.a. Y − X τ̃ ≤ η σ (dual: máx γ′Y, γ ≥ 0,
    X′γ = 0, σ′γ = 1). Condicional ao vértice ótimo γ*, η̂ ~ N(γ*′μ, γ*′Σγ*) truncada em [v_lo, v_up]; sob o
    nulo menos favorável a média é 0. Com `c_lf` (híbrido condicional–LF de ARP): rejeita se η̂ > c_lf; senão,
    teste condicional com v_up truncado em c_lf, ao nível (α − κ)/(1 − κ)."""
    k = Y.size
    sig = np.sqrt(np.clip(np.diag(SigmaY), 0, None))
    sig = np.where(sig > 0, sig, 1e-12)
    eqs = [sig.reshape(1, -1)]
    beq = [1.0]
    if X.shape[1] > 0:
        eqs.insert(0, X.T)
        beq = [0.0] * X.shape[1] + beq
    A_eq = np.vstack(eqs)
    b_eq = np.array(beq)
    r = _lp(-Y, A_eq=A_eq, b_eq=b_eq, n=k)
    if r.status == 2:
        return {"eta": -math.inf, "p": 1.0, "rejeita": False, "v_lo": -math.inf, "v_up": math.inf}
    if r.status != 0:
        raise RuntimeError(f"ARP: dual: {r.message}")
    g = r.x
    eta = float(g @ Y)
    s2 = float(g @ SigmaY @ g)
    if s2 <= 1e-14:
        rej = eta > 1e-10
        return {"eta": eta, "p": 0.0 if rej else 1.0, "rejeita": rej, "v_lo": -math.inf, "v_up": math.inf}
    if c_lf is not None and eta > c_lf:
        return {"eta": eta, "p": 0.0, "rejeita": True, "v_lo": math.nan, "v_up": math.nan}
    cvec = SigmaY @ g / s2
    S = Y - cvec * eta
    nx = X.shape[1]
    # variáveis (u, t): u ≥ 0 (k), t ≥ 0
    base_eq = np.hstack([X.T, np.zeros((nx, 1))]) if nx else np.zeros((0, k + 1))
    sig_eq = np.hstack([sig, [-1.0]]).reshape(1, -1)
    # v_lo = máx u′S s.a. X′u = 0, σ′u = t, t − c′u = 1
    A1 = np.vstack([base_eq, sig_eq, np.hstack([-cvec, [1.0]]).reshape(1, -1)])
    b1 = np.concatenate([np.zeros(nx), [0.0, 1.0]])
    r1 = _lp(np.concatenate([-S, [0.0]]), A_eq=A1, b_eq=b1, n=k + 1)
    if r1.status == 2:
        v_lo = -math.inf
    elif r1.status == 3:
        v_lo = eta
    elif r1.status == 0:
        v_lo = min(float(-r1.fun), eta)
    else:
        raise RuntimeError(f"ARP: v_lo: {r1.message}")
    # v_up = mín −u′S s.a. X′u = 0, σ′u = t, c′u − t = 1
    A2 = np.vstack([base_eq, sig_eq, np.hstack([cvec, [-1.0]]).reshape(1, -1)])
    r2 = _lp(np.concatenate([-S, [0.0]]), A_eq=A2, b_eq=b1, n=k + 1)
    if r2.status == 2:
        v_up = math.inf
    elif r2.status == 3:
        v_up = eta
    elif r2.status == 0:
        v_up = max(float(r2.fun), eta)
    else:
        raise RuntimeError(f"ARP: v_up: {r2.message}")
    nivel = alpha
    if c_lf is not None:
        v_up = min(v_up, c_lf)
        nivel = (alpha - kappa) / (1 - kappa)
    s = math.sqrt(s2)
    a, b, z = v_lo / s, v_up / s, eta / s
    if b - a < 1e-12:
        p = 1.0 if z <= a else 0.0
    else:
        # P(Z ≥ z | a ≤ Z ≤ b) com caudas estáveis
        if z >= b:
            p = 0.0
        elif a > 0:
            num = stats.norm.sf(z) - stats.norm.sf(b)
            den = stats.norm.sf(a) - stats.norm.sf(b)
            p = float(num / den) if den > 0 else 0.0
        else:
            num = stats.norm.cdf(b) - stats.norm.cdf(z)
            den = stats.norm.cdf(b) - stats.norm.cdf(a)
            p = float(num / den) if den > 0 else 0.0
    p = min(max(p, 0.0), 1.0)
    return {"eta": eta, "p": p, "rejeita": p < nivel, "v_lo": v_lo, "v_up": v_up}


class TesteRM:
    """Teste ARP de H0: θ = θ̄ e δ ∈ Δ^RM(M̄), por poliedro."""

    def __init__(self, beta, Sigma, T_pre: int, T_post: int, l, Mbar: float, alpha: float = 0.05,
                 metodo: str = "condicional", n_sim: int = N_SIM_LF, semente: int = SEMENTE_LF):
        if metodo not in ("condicional", "hibrido"):
            raise ValueError(metodo)
        self.metodo = metodo
        self.kappa = alpha / 10 if metodo == "hibrido" else 0.0
        self.beta = np.asarray(beta, float)
        self.Sigma = np.asarray(Sigma, float)
        self.T_pre, self.T_post = T_pre, T_post
        self.l = np.asarray(l, float)
        self.alpha = alpha
        T = T_pre + T_post
        Lp = np.zeros((T, T_post))
        Lp[T_pre:, :] = np.eye(T_post)
        Gi = np.linalg.inv(_base_alvo(self.l))
        self.pecas = []
        for i, (chave, A) in enumerate(pecas_rm(T_pre, T_post, Mbar)):
            Mm = A @ Lp @ Gi
            SY = A @ self.Sigma @ A.T
            c_lf = (valor_critico_lf(Mm[:, 1:], SY, self.kappa, n_sim, semente + i)
                    if metodo == "hibrido" else None)
            self.pecas.append({"chave": chave, "Y0": A @ self.beta, "a1": Mm[:, 0], "X": Mm[:, 1:],
                               "SigmaY": SY, "c_lf": c_lf,
                               "id": _limites_poliedro(self.beta, A, np.zeros(A.shape[0]), T_pre, T_post, self.l)})

    def aceita(self, theta: float) -> bool:
        # poliedros cujo conjunto identificado em β̂ contém θ̄ primeiro (saída antecipada)
        ordem = sorted(self.pecas, key=lambda p: 0 if (p["id"] and p["id"][0] <= theta <= p["id"][1]) else 1)
        for p in ordem:
            t = teste_condicional(p["Y0"] - p["a1"] * theta, p["X"], p["SigmaY"], self.alpha, c_lf=p["c_lf"],
                                  kappa=self.kappa)
            if not t["rejeita"]:
                return True
        return False


def ic_rm(beta, Sigma, T_pre: int, T_post: int, l, Mbar: float, alpha: float = 0.05, n_grade: int = 41,
          iter_bissecao: int = 14, metodo: str = "condicional", n_sim: int = N_SIM_LF) -> dict:
    """IC robusto (envelope) para θ sob Δ^RM(M̄) pelo teste condicional ARP; grade + bisseção nas bordas."""
    beta = np.asarray(beta, float)
    Sigma = np.asarray(Sigma, float)
    l = np.asarray(l, float)
    teste = TesteRM(beta, Sigma, T_pre, T_post, l, Mbar, alpha, metodo=metodo, n_sim=n_sim)
    sd = math.sqrt(float(l @ Sigma[T_pre:, T_pre:] @ l))
    centro = float(l @ beta[T_pre:])
    idset = conjunto_identificado_rm(beta, T_pre, T_post, l, Mbar)
    if idset and all(np.isfinite(idset)):
        lo0, hi0 = min(idset[0], centro), max(idset[1], centro)
    else:
        lo0, hi0 = centro, centro
    raio = 6 * sd + 0.5 * (hi0 - lo0)
    meio = (lo0 + hi0) / 2
    for _ in range(8):
        grade = np.linspace(meio - raio - 0.5 * (hi0 - lo0), meio + raio + 0.5 * (hi0 - lo0), n_grade)
        ac = np.array([teste.aceita(float(x)) for x in grade])
        if ac[0] or ac[-1]:
            raio *= 2.5
            continue
        break
    else:
        return {"ic_inf": -math.inf, "ic_sup": math.inf, "vazio": False, "conjunto_identificado": idset,
                "nota": "IC não fechou na grade expandida"}
    if not ac.any():
        # refinamento: grade fina em torno do centro antes de declarar vazio
        grade = np.linspace(grade[0], grade[-1], 8 * n_grade)
        ac = np.array([teste.aceita(float(x)) for x in grade])
        if not ac.any():
            return {"ic_inf": math.nan, "ic_sup": math.nan, "vazio": True, "conjunto_identificado": idset,
                    "nota": "nenhum θ̄ aceito na grade"}
    i0, i1 = int(np.flatnonzero(ac)[0]), int(np.flatnonzero(ac)[-1])

    def bissecao(fora: float, dentro: float) -> float:
        for _ in range(iter_bissecao):
            m = (fora + dentro) / 2
            if teste.aceita(m):
                dentro = m
            else:
                fora = m
        return dentro

    lo = bissecao(float(grade[i0 - 1]), float(grade[i0]))
    hi = bissecao(float(grade[i1 + 1]), float(grade[i1]))
    return {"ic_inf": lo, "ic_sup": hi, "vazio": False, "conjunto_identificado": idset, "nota": ""}


# ---------------------------------------------------------------------------
# Ponto de ruptura
# ---------------------------------------------------------------------------

def exclui_zero(lo: float, hi: float) -> bool:
    return bool(np.isfinite(lo) and np.isfinite(hi) and (lo > 0 or hi < 0))


def ruptura(funcao_ic, maximo: float, tol: float) -> dict:
    """Maior valor do parâmetro em [0, máximo] com IC que exclui zero (IC monotônico no parâmetro)."""
    lo0, hi0 = funcao_ic(0.0)
    if not exclui_zero(lo0, hi0):
        return {"ruptura": 0.0, "censura": "ic_inclui_zero_em_0"}
    lo1, hi1 = funcao_ic(maximo)
    if exclui_zero(lo1, hi1):
        return {"ruptura": float(maximo), "censura": "maior_ou_igual_ao_maximo"}
    a, b = 0.0, float(maximo)
    while b - a > tol:
        m = (a + b) / 2
        lo, hi = funcao_ic(m)
        if exclui_zero(lo, hi):
            a = m
        else:
            b = m
    return {"ruptura": float(a), "censura": ""}


def max_segunda_diferenca_pre(beta, T_pre: int) -> float:
    """Maior |segunda diferença| entre os coeficientes do pré e a referência (descritivo)."""
    seq = np.concatenate([np.asarray(beta, float)[:T_pre], [0.0]])
    if seq.size < 3:
        return math.nan
    return float(np.max(np.abs(np.diff(seq, n=2))))


def max_primeira_diferenca_pre(beta, T_pre: int) -> float:
    seq = np.concatenate([np.asarray(beta, float)[:T_pre], [0.0]])
    return float(np.max(np.abs(np.diff(seq)))) if seq.size >= 2 else math.nan
