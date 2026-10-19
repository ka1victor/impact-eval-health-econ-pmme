"""D2 do protocolo 47 (exploratório): chegada do especialista do PMM-E e produção especializada, Callaway–Sant'Anna.

Protocolo congelado: `docs/06_execucao/47_protocolo_producao_especializada.md`, §5 D2 (e adendos §10 e §11
para as definições dos outcomes, que vêm do D1, `21_producao_dird.py`). Rótulo de toda linha:
`estatuto = EXPLORATORIO_PARTICIPACAO`, `natureza_dos_dados = EMPIRICO`.

Desenho
-------
- Amostra: municípios que ofereceram células nos ciclos 1 ou 2 (`outcomes_V_municipio`, ciclos 1 e 2) e estão
  em U (IVS oficial e população 2022).
- Tratado: município com >= 1 especialista ativo na lista nominal (`data/pmm_especialistas_nominal.csv`, só
  leitura; só as colunas co_ibge, dt_inicio_atividade, ciclo e dt_referencia são lidas, nenhum nome).
- Mês de chegada: o menor `dt_inicio_atividade` do município. Coorte g = trimestre da chegada, datado pelo
  primeiro mês do trimestre; o município conta como tratado a partir desse mês (conservador: a chegada pode
  ser no 2º ou 3º mês do trimestre).
- Estimador: Callaway e Sant'Anna (2021), ATT(g, t) sem covariáveis, com período-base universal b = g − 1 e
  controles "ainda não tratados": nunca tratados mais as coortes g' > max(t, b), sem a própria coorte.
  ATT(g, t) = [média(Y_t − Y_b | G = g)] − [média(Y_t − Y_b | controles)], só com unidades que têm Y_t e Y_b.
- Agregação por tempo de evento e = t − g, de −24 a +9 meses, com pesos = tamanho da coorte entre as coortes
  com ATT(g, g + e) definido; e = −1 é a base (zero por construção). ATT médio do pós = média de θ(e) para
  e = 0..9 definidos.
- Inferência: funções de influência por município (cada município é uma unidade com toda a sua série, logo o
  bootstrap é com cluster no município), incluindo a estimação dos pesos de coorte; bootstrap multiplicador
  com pesos de Mammen, B = 9.999, semente fixa 20261019; EP = intervalo interquartil / (z_0,75 − z_0,25), como
  em Callaway e Sant'Anna; IC 95% pontual normal e banda uniforme (sup-t) sobre e = −24..9.
- Pré-tendência: teste de Wald conjunto de θ(e) = 0 para e = −24..−2, covariância analítica das funções de
  influência (V = IF'IF / N²); também o p do sup-t do bootstrap nos mesmos e.
- Outcomes (taxas mensais por 10 mil hab., definições do D1): K1, K1a, K1b, K1c, K1d, K2, KP1, KP2, K4
  (vínculos e horas não SUS); K3 só com as coortes g <= 202512 (o TISS vai até 202512).
- Fim da série: 202605 para SIA, SIH e CNES (o mesmo pós principal do D1, §10.1); 202512 para K3.
- Sensibilidade (§5 D2): sem os municípios com alocado na 1ª chamada (X2) e sem especialista ativo.
- Dose (descritiva): ATT médio do pós ÷ número médio de especialistas da lista nominal por município tratado.

Leitura: ATT sob tendências paralelas condicionais a nada, não efeito com fonte de exogeneidade validada; a
chegada depende da escolha do candidato. Pré não plano -> linguagem associativa.

Saídas: output/rdd_bolsa/K_D2_att_gt.csv, K_D2_estudo_evento.csv, K_D2_estimativas.csv, K_D2_resumo.json,
K_D2_figuras/*.png; tabelas entre marcadores `<!-- KD2:...:inicio/fim -->` do doc 50.

Uso
---
    python3 scripts/rdd_bolsa/22_chegada_pmme_evento.py
    python3 scripts/rdd_bolsa/22_chegada_pmme_evento.py --atualizar-doc
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import re
import sys
import textwrap
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
DIR_RDD = ROOT / "scripts" / "rdd_bolsa"


def _importar(caminho: Path, nome: str):
    if nome in sys.modules:
        return sys.modules[nome]
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    return mod


_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
K1M = _importar(DIR_RDD / "21_producao_dird.py", "k21_para_d2")
sys.dont_write_bytecode = _bytecode

OUT = K1M.OUT
NOMINAL = ROOT / "data" / "pmm_especialistas_nominal.csv"
ARQ_VM = K1M.ARQ_VM
X2_MUN = OUT / "X2_municipios.csv"
DOC50 = K1M.DOC50
PROTOCOLO_MD = K1M.PROTOCOLO_MD

NOME_ATT = "K_D2_att_gt.csv"
NOME_EVENTO = "K_D2_estudo_evento.csv"
NOME_EST = "K_D2_estimativas.csv"
NOME_RESUMO = "K_D2_resumo.json"
DIR_FIG = "K_D2_figuras"

DATA_EXECUCAO = "2026-10-19"
ESTATUTO = "EXPLORATORIO_PARTICIPACAO"
NATUREZA = "EMPIRICO"
E_MIN, E_MAX = -24, 9
B_BOOT = 9_999
SEMENTE = 20261019
INICIO = "202201"
FIM = {"SIA": "202605", "SIH": "202605", "CNES": "202605", "K3": "202512"}
COORTE_MAX_K3 = "202512"
COLUNAS_NOMINAL = ["co_ibge", "dt_inicio_atividade", "ciclo", "dt_referencia"]
OUTCOMES_D2 = ("K1", "K1a", "K1b", "K1c", "K1d", "K2", "KP1", "KP2", "K4.vinculos", "K4.horas", "K3")
VARIANTES = {"principal": "amostra do protocolo (ofereceu célula nos ciclos 1 ou 2)",
             "sem_alocado_sem_ativo": "§5 D2: sem os municípios com alocado na 1ª chamada (X2, ciclos 1 e 2) e sem "
                                      "especialista ativo na lista nominal"}
_meses = K1M._meses
Z_IQR = stats.norm.ppf(0.75) - stats.norm.ppf(0.25)

DESVIOS = [
    {"data": DATA_EXECUCAO, "tipo": "esclarecimento", "item": "data da coorte",
     "descricao": "coorte trimestral datada pelo primeiro mês do trimestre da chegada; tempo de evento em meses a "
                  "partir desse mês; base universal b = g - 1 (o mês antes do trimestre), que é anterior à chegada de "
                  "todos da coorte."},
    {"data": DATA_EXECUCAO, "tipo": "esclarecimento", "item": "fim da série",
     "descricao": "SIA, SIH e CNES até 202605 (o pós principal do D1 pelo adendo §10.1, meses imaturos fora); K3 até "
                  "202512 (TISS). Nenhum mês CNES >= 202609 é lido."},
    {"data": DATA_EXECUCAO, "tipo": "esclarecimento", "item": "K4 no D2",
     "descricao": "K4 entra como duas linhas, vínculos e horas não SUS; o CNES é trimestral antes de 202406, então "
                  "tempos de evento sem competência ficam sem ATT (não são preenchidos)."},
    {"data": DATA_EXECUCAO, "tipo": "esclarecimento", "item": "inferência",
     "descricao": "bootstrap multiplicador (Mammen) implementado no script, sem pacote externo; a unidade do bootstrap "
                  "é o município, que é o cluster pedido. O IF de θ(e) inclui o termo da estimação dos pesos de coorte."},
    {"data": DATA_EXECUCAO, "tipo": "esclarecimento", "item": "tratado fora da amostra",
     "descricao": "município da lista nominal que não ofereceu célula nos ciclos 1 ou 2 (ou sem IVS/população) fica fora "
                  "e é contado no resumo."},
    {"data": "2026-10-19", "tipo": "correcao (auditoria 21)", "item": "chegada depois do fim da série",
     "descricao": "município cuja 1ª chegada é posterior ao último mês da série do outcome (202605 em SIA, SIH e CNES) "
                  "fica como ainda não tratado em todo o horizonte, como pede o §5 D2 (controles: ainda não tratados). "
                  "A versão anterior testava o início do trimestre e contava como tratadas, desde 202604, as chegadas "
                  "de 202606. A correção não olha resultado: segue a regra que o próprio script declarava."},
]


class FalhaValidacao(RuntimeError):
    """Validação obrigatória falhou: o script para sem gravar."""


# ---------------------------------------------------------------------------
# 1. Estimador de Callaway–Sant'Anna (funções puras; testadas com dados sintéticos em memória)
# ---------------------------------------------------------------------------

def att_gt(Y: np.ndarray, G: np.ndarray, coortes: list[int], *, e_min: int = E_MIN, e_max: int = E_MAX,
           min_controles: int = 2) -> tuple[pd.DataFrame, np.ndarray]:
    """ATT(g, t) com base universal b = g - 1 e controles ainda não tratados.

    Y: N x T (NaN = ausente). G: índice do período de tratamento de cada unidade (-1 = nunca tratada no
    horizonte). Devolve a tabela das células e a matriz de funções de influência N x células (escala: ATT^ - ATT
    ~ média de IF).
    """
    N, T = Y.shape
    linhas, ifs = [], []
    for g in coortes:
        b = g - 1
        if b < 0:
            continue
        tratada = G == g
        n_g_total = int(tratada.sum())
        for t in range(max(0, g + e_min), min(T, g + e_max + 1)):
            if t == b:
                continue
            ok = np.isfinite(Y[:, t]) & np.isfinite(Y[:, b])
            dy = Y[:, t] - Y[:, b]
            ctrl = ((G < 0) | (G > max(t, b))) & (G != g)
            mt, mc = tratada & ok, ctrl & ok
            n1, n0 = int(mt.sum()), int(mc.sum())
            reg = {"g": g, "t": t, "e": t - g, "n_tratados": n1, "n_controles": n0, "n_coorte": n_g_total,
                   "att": np.nan, "ep": np.nan, "nota": ""}
            psi = np.zeros(N)
            if n1 < 1 or n0 < min_controles:
                reg["nota"] = f"sem suporte: {n1} tratados e {n0} controles com Y_t e Y_b"
            else:
                mu1, mu0 = dy[mt].mean(), dy[mc].mean()
                reg["att"] = float(mu1 - mu0)
                psi[mt] = N * (dy[mt] - mu1) / n1
                psi[mc] = -N * (dy[mc] - mu0) / n0
                reg["ep"] = float(math.sqrt(np.sum(psi ** 2)) / N)
            linhas.append(reg)
            ifs.append(psi)
    tab = pd.DataFrame(linhas)
    return tab, (np.column_stack(ifs) if ifs else np.zeros((N, 0)))


def agregar_evento(tab: pd.DataFrame, IF: np.ndarray, G: np.ndarray, *, e_min: int = E_MIN, e_max: int = E_MAX
                   ) -> tuple[pd.DataFrame, np.ndarray]:
    """θ(e) = soma_g w_g ATT(g, g+e), w_g = n_g / soma das coortes com célula definida; IF com o termo dos pesos."""
    N = IF.shape[0]
    linhas, ifs = [], []
    for e in range(e_min, e_max + 1):
        if e == -1:
            linhas.append({"e": e, "theta": 0.0, "n_coortes": int((tab["e"] == e).sum()) if len(tab) else 0,
                           "n_tratados": 0, "referencia": True, "nota": "base universal b = g - 1: zero por construção"})
            ifs.append(np.zeros(N))
            continue
        sel = tab.index[(tab["e"] == e) & tab["att"].notna()] if len(tab) else []
        if len(sel) == 0:
            linhas.append({"e": e, "theta": np.nan, "n_coortes": 0, "n_tratados": 0, "referencia": False,
                           "nota": "nenhuma coorte com ATT(g, g+e) definido"})
            ifs.append(np.full(N, np.nan))
            continue
        gs = tab.loc[sel, "g"].to_numpy()
        pi = np.array([np.mean(G == g) for g in gs])
        S = pi.sum()
        w = pi / S
        att = tab.loc[sel, "att"].to_numpy(dtype=float)
        theta = float(np.sum(w * att))
        psi = IF[:, sel] @ w
        # IF dos pesos: w_g = pi_g / S, com pi_g estimado pela fração de unidades da coorte.
        D = np.column_stack([(G == g).astype(float) - p for g, p in zip(gs, pi)])   # N x k
        psi_w = D / S - np.outer(D.sum(axis=1), pi) / S ** 2
        psi = psi + psi_w @ att
        linhas.append({"e": e, "theta": theta, "n_coortes": int(len(sel)),
                       "n_tratados": int(tab.loc[sel, "n_tratados"].sum()), "referencia": False, "nota": ""})
        ifs.append(psi)
    return pd.DataFrame(linhas), np.column_stack(ifs)


def pesos_mammen(B: int, N: int, semente: int) -> np.ndarray:
    rng = np.random.default_rng(semente)
    r5 = math.sqrt(5.0)
    p = (r5 + 1) / (2 * r5)
    return np.where(rng.random((B, N)) < p, (1 - r5) / 2, (1 + r5) / 2)


def inferencia(theta: np.ndarray, IF: np.ndarray, xi: np.ndarray) -> dict:
    """EP bootstrap (IQR), EP analítico, IC pontual e banda uniforme sup-t sobre os elementos finitos."""
    N = IF.shape[0]
    ok = np.isfinite(theta) & np.isfinite(IF).all(axis=0)
    k = theta.size
    ep_b = np.full(k, np.nan)
    ep_a = np.full(k, np.nan)
    crit = np.nan
    if ok.any():
        pert = xi @ np.nan_to_num(IF[:, ok]) / N                         # B x k_ok
        q75, q25 = np.percentile(pert, [75, 25], axis=0)
        ep_b[ok] = (q75 - q25) / Z_IQR
        ep_a[ok] = np.sqrt(np.sum(IF[:, ok] ** 2, axis=0)) / N
        pos = ep_b[ok] > 0
        if pos.any():
            tstat = np.abs(pert[:, pos]) / ep_b[ok][pos]
            crit = float(np.percentile(tstat.max(axis=1), 95))
    return {"ep_boot": ep_b, "ep_analitico": ep_a, "crit_uniforme": crit, "ok": ok}


def wald_pre(theta: np.ndarray, IF: np.ndarray, mascara: np.ndarray, xi: np.ndarray) -> dict:
    """Wald conjunto (covariância IF'IF/N²) e p do sup-t do bootstrap para θ(e) = 0 nos e da máscara."""
    N = IF.shape[0]
    m = mascara & np.isfinite(theta) & np.isfinite(IF).all(axis=0)
    if m.sum() == 0:
        return {"wald": np.nan, "gl": 0, "p_wald": np.nan, "p_supt": np.nan, "k": 0}
    th = theta[m]
    psi = IF[:, m]
    V = psi.T @ psi / N ** 2
    inv = np.linalg.pinv(V)
    W = float(th @ inv @ th)
    gl = int(np.linalg.matrix_rank(V))
    pert = xi @ psi / N
    se = np.sqrt(np.diag(V))
    pos = se > 0
    p_supt = float(np.mean(np.max(np.abs(pert[:, pos]) / se[pos], axis=1) >= np.max(np.abs(th[pos]) / se[pos])))
    return {"wald": W, "gl": gl, "p_wald": float(stats.chi2.sf(W, gl)) if gl else np.nan, "p_supt": p_supt,
            "k": int(m.sum())}


def estimar_cs(Y: np.ndarray, G: np.ndarray, coortes: list[int], xi: np.ndarray, *, e_min=E_MIN, e_max=E_MAX) -> dict:
    tab, IF = att_gt(Y, G, coortes, e_min=e_min, e_max=e_max)
    ev, IFe = agregar_evento(tab, IF, G, e_min=e_min, e_max=e_max)
    th = ev["theta"].to_numpy(dtype=float)
    inf = inferencia(th, IFe, xi)
    ev["ep"] = inf["ep_boot"]
    ev["ep_analitico"] = inf["ep_analitico"]
    ev["ic95_inf"] = th - K1M.L.Z_975 * ev["ep"]
    ev["ic95_sup"] = th + K1M.L.Z_975 * ev["ep"]
    ev["banda_unif_inf"] = th - inf["crit_uniforme"] * ev["ep"]
    ev["banda_unif_sup"] = th + inf["crit_uniforme"] * ev["ep"]
    ev["p_valor"] = [K1M.L.p_normal(a / b) if np.isfinite(a) and np.isfinite(b) and b > 0 else np.nan
                     for a, b in zip(th, ev["ep"])]
    ev.loc[ev["referencia"], ["ep", "ep_analitico", "ic95_inf", "ic95_sup", "banda_unif_inf", "banda_unif_sup",
                              "p_valor"]] = np.nan
    e = ev["e"].to_numpy()
    pre = (e <= -2)
    post = (e >= 0) & np.isfinite(th)
    pt = wald_pre(th, IFe, pre, xi)
    res = {"att_gt": tab, "evento": ev, "pre": pt, "crit_uniforme": inf["crit_uniforme"]}
    if post.any():
        psi = IFe[:, post].mean(axis=1)
        val = float(th[post].mean())
        pert = xi @ psi / len(psi)
        q75, q25 = np.percentile(pert, [75, 25])
        ep = float((q75 - q25) / Z_IQR)
        res["pos"] = {"att": val, "ep": ep, "ep_analitico": float(math.sqrt(np.sum(psi ** 2)) / len(psi)),
                      "ic95_inf": val - K1M.L.Z_975 * ep, "ic95_sup": val + K1M.L.Z_975 * ep,
                      "p_valor": K1M.L.p_normal(val / ep) if ep > 0 else np.nan,
                      "e_min": int(e[post].min()), "e_max": int(e[post].max()), "n_e": int(post.sum())}
    else:
        res["pos"] = {"att": np.nan, "ep": np.nan, "ep_analitico": np.nan, "ic95_inf": np.nan, "ic95_sup": np.nan,
                      "p_valor": np.nan, "e_min": None, "e_max": None, "n_e": 0}
    return res


# ---------------------------------------------------------------------------
# 2. Amostra, chegada e coortes
# ---------------------------------------------------------------------------

def trimestre_inicio(comp: str) -> str:
    a, m = int(comp[:4]), int(comp[4:])
    return f"{a}{(3 * ((m - 1) // 3) + 1):02d}"


def ler_chegadas(amostra: pd.Index) -> tuple[pd.DataFrame, dict]:
    """Por município da amostra: menor dt_inicio_atividade, coorte trimestral e número de especialistas."""
    nom = pd.read_csv(NOMINAL, usecols=COLUNAS_NOMINAL, dtype=str)
    nom["co_ibge"] = K1M._ibge6(nom["co_ibge"])
    d = pd.to_datetime(nom["dt_inicio_atividade"], format="%Y-%m-%d", errors="coerce")
    sem_data = int(d.isna().sum())
    nom = nom.assign(dt=d)[d.notna()]
    nom["comp"] = nom["dt"].dt.strftime("%Y%m")
    if (nom["comp"] >= K1M.LIMITE_CNES).any():
        raise FalhaValidacao("lista nominal com inicio >= 202609")
    por = nom.groupby("co_ibge").agg(chegada=("comp", "min"), n_especialistas=("comp", "size"),
                                     n_ciclo1=("ciclo", lambda v: int((v == "1").sum())),
                                     n_ciclo2=("ciclo", lambda v: int((v == "2").sum())))
    por["coorte"] = por["chegada"].map(trimestre_inicio)
    fora = sorted(set(por.index) - set(amostra))
    info = {"linhas_lista_nominal": int(len(nom) + sem_data), "linhas_sem_data_fora": sem_data,
            "dt_referencia": sorted(nom["dt_referencia"].dropna().unique().tolist()),
            "municipios_com_ativo": int(len(por)), "municipios_com_ativo_fora_da_amostra": len(fora),
            "especialistas_em_municipios_fora_da_amostra": int(por.loc[fora, "n_especialistas"].sum()),
            "colunas_lidas": COLUNAS_NOMINAL}
    return por.reindex(amostra), info


def ler_amostra(base: pd.DataFrame) -> tuple[pd.Index, dict]:
    vm = pd.read_parquet(ARQ_VM, columns=["ciclo", "co_ibge"])
    vm = vm[vm["ciclo"].isin([1, 2])]
    cods = set(K1M._ibge6(vm["co_ibge"]))
    fora = sorted(cods - set(base.index))
    return pd.Index(sorted(cods & set(base.index)), name="co_ibge"), {
        "municipios_ciclos_1_2": len(cods), "fora_de_U": fora}


def ler_alocados_sem_ativo(chegadas: pd.DataFrame) -> list[str]:
    x2 = pd.read_csv(X2_MUN, dtype={"co_ibge": str})
    x2 = x2[x2["ciclo"].isin([1, 2])]
    x2["co_ibge"] = K1M._ibge6(x2["co_ibge"])
    aloc = set(x2.loc[x2["n_alocados"] > 0, "co_ibge"])
    sem_ativo = set(chegadas.index[chegadas["chegada"].isna()])
    return sorted(aloc & sem_ativo)


# ---------------------------------------------------------------------------
# 3. Outcomes mensais
# ---------------------------------------------------------------------------

def fonte_d2(spec: dict) -> str:
    return {"SIA": "SIA", "SIH": "SIH", "CNES": "CNES", "K3": "K3"}[spec["fonte"]]


def serie(D, spec: dict, amostra: pd.Index) -> tuple[np.ndarray, list[str]]:
    num, den, _ = K1M.contagens(D, spec)
    pop = D.base.loc[amostra, "populacao_2022"].astype(float)
    R = K1M.serie_mensal(num.reindex(amostra), den.reindex(amostra) if den is not None else None, pop)
    meses = list(_meses(INICIO, FIM[fonte_d2(spec)]))
    R = R.reindex(columns=meses)          # competência sem dado (CNES trimestral) fica NaN, nunca zero
    return R.to_numpy(dtype=float), meses


def indices_coorte(chegadas: pd.DataFrame, meses: list[str], *, coorte_max: str | None = None) -> tuple[np.ndarray, list[int]]:
    pos = {m: i for i, m in enumerate(meses)}
    G = np.full(len(chegadas), -1, dtype=int)
    for i, (c, ch) in enumerate(zip(chegadas["coorte"].to_numpy(), chegadas["chegada"].to_numpy())):
        if isinstance(c, str):
            if ch > meses[-1]:
                # 1ª chegada depois do fim da série: ainda não tratado no horizonte. O teste é no mês da chegada,
                # não no início do trimestre (auditoria 21: chegadas de 202606 caíam na coorte 202604 e contavam
                # como tratadas em 202604-202605, sem nenhum mês de exposição na série que acaba em 202605).
                G[i] = -1
            elif c in pos:
                G[i] = pos[c]
            else:
                raise FalhaValidacao(f"coorte {c} antes do início da série")
    coortes = sorted({int(g) for g, c in zip(G, chegadas["coorte"]) if g >= 0
                      and (coorte_max is None or c <= coorte_max)})
    return G, coortes


# ---------------------------------------------------------------------------
# 4. Execução
# ---------------------------------------------------------------------------

COLUNAS_EVENTO = ["natureza_dos_dados", "estatuto", "familia", "desenho", "outcome_id", "variante", "e", "theta",
                  "ep", "ep_analitico", "ic95_inf", "ic95_sup", "banda_unif_inf", "banda_unif_sup", "p_valor",
                  "n_coortes", "n_tratados", "referencia", "janela", "unidade", "nota"]
COLUNAS_ATT = ["natureza_dos_dados", "estatuto", "familia", "desenho", "outcome_id", "variante", "coorte",
               "competencia", "e", "n_coorte", "n_tratados", "n_controles", "att", "ep", "nota"]
COLUNAS_EST = ["natureza_dos_dados", "estatuto", "familia", "desenho", "outcome_id", "descricao_outcome", "variante",
               "estatistica", "valor", "ep", "ep_analitico", "ic95_inf", "ic95_sup", "p_valor", "gl", "e_min", "e_max",
               "n_municipios", "n_tratados", "n_nunca_tratados", "n_coortes", "unidade", "contraste", "nota"]
CONTRASTE = ("ATT da chegada do 1º especialista do PMM-E (Callaway-Sant'Anna, controles ainda não tratados) sob "
             "tendências paralelas; não é efeito com fonte de exogeneidade validada nem efeito do incentivo marginal")


def rodar(D, amostra: pd.Index, chegadas: pd.DataFrame, xi: np.ndarray, variante: str) -> tuple[list, list, list]:
    ev_l, att_l, est_l = [], [], []
    base_meta = {"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "familia": "K", "desenho": "D2",
                 "variante": variante}
    for oid in OUTCOMES_D2:
        spec = next(c for c in K1M.CATALOGO if c["id"] == oid)
        Y, meses = serie(D, spec, amostra)
        cmax = COORTE_MAX_K3 if oid == "K3" else None
        G, coortes = indices_coorte(chegadas, meses, coorte_max=cmax)
        r = estimar_cs(Y, G, coortes, xi)
        un = K1M.UNIDADES[spec["unidade"]]
        meta = {**base_meta, "outcome_id": oid, "unidade": un}
        for rec in r["att_gt"].to_dict("records"):
            att_l.append({**base_meta, "outcome_id": oid, "coorte": meses[rec["g"]], "competencia": meses[rec["t"]],
                          **{k: rec[k] for k in ("e", "n_coorte", "n_tratados", "n_controles", "att", "ep", "nota")}})
        for rec in r["evento"].to_dict("records"):
            ev_l.append({**meta, **rec, "janela": "base" if rec["e"] == -1 else ("pre" if rec["e"] < -1 else "pos")})
        n_trat = int(sum((G == g).sum() for g in coortes))
        n_nunca = int((G < 0).sum())
        comum = {**meta, "descricao_outcome": spec["desc"], "n_municipios": int(len(G)), "n_tratados": n_trat,
                 "n_nunca_tratados": n_nunca, "n_coortes": len(coortes), "contraste": CONTRASTE}
        pos = r["pos"]
        est_l.append({**comum, "estatistica": "att_pos_medio", "valor": pos["att"], "ep": pos["ep"],
                      "ep_analitico": pos["ep_analitico"], "ic95_inf": pos["ic95_inf"], "ic95_sup": pos["ic95_sup"],
                      "p_valor": pos["p_valor"], "gl": np.nan, "e_min": pos["e_min"], "e_max": pos["e_max"],
                      "nota": f"média de θ(e) em {pos['n_e']} tempos de evento do pós"})
        pt = r["pre"]
        est_l.append({**comum, "estatistica": "pretendencia_wald", "valor": pt["wald"], "ep": np.nan,
                      "ep_analitico": np.nan, "ic95_inf": np.nan, "ic95_sup": np.nan, "p_valor": pt["p_wald"],
                      "gl": pt["gl"], "e_min": E_MIN, "e_max": -2,
                      "nota": f"Wald conjunto de θ(e) = 0 em {pt['k']} tempos de evento do pré; p sup-t do "
                              f"bootstrap = {pt['p_supt']:.4f}" if np.isfinite(pt["p_supt"]) else "sem pré estimável"})
        est_l.append({**comum, "estatistica": "pretendencia_supt", "valor": np.nan, "ep": np.nan,
                      "ep_analitico": np.nan, "ic95_inf": np.nan, "ic95_sup": np.nan, "p_valor": pt["p_supt"],
                      "gl": np.nan, "e_min": E_MIN, "e_max": -2,
                      "nota": "p do sup-t (bootstrap multiplicador) para θ(e) = 0 em todo o pré"})
        # Dose descritiva: ATT médio do pós / número médio de especialistas por município tratado das coortes usadas.
        trat = np.isin(G, coortes)
        n_esp = chegadas["n_especialistas"].to_numpy(dtype=float)[trat]
        media_esp = float(np.nanmean(n_esp)) if trat.any() else np.nan
        est_l.append({**comum, "estatistica": "dose_por_especialista", "valor": pos["att"] / media_esp
                      if np.isfinite(media_esp) and media_esp > 0 else np.nan,
                      "ep": np.nan, "ep_analitico": np.nan, "ic95_inf": pos["ic95_inf"] / media_esp,
                      "ic95_sup": pos["ic95_sup"] / media_esp, "p_valor": np.nan, "gl": np.nan,
                      "e_min": pos["e_min"], "e_max": pos["e_max"],
                      "nota": f"DESCRITIVO: ATT médio do pós ÷ {media_esp:.3f} especialistas por município tratado "
                              "(lista nominal); IC = IC do ATT ÷ a mesma média (a média tratada como fixa)"})
    return ev_l, att_l, est_l


# ---------------------------------------------------------------------------
# 5. Figuras
# ---------------------------------------------------------------------------

COR_POS_D2 = "#efece4"      # fundo do pós no D2: neutro, distinto da banda azul (auditoria 21)


def limites_eixo(th: np.ndarray, lo: np.ndarray, hi: np.ndarray) -> tuple[float, float, bool]:
    """Limites do eixo vertical: todos os θ e os IC 95% dos meses típicos; IC muito mais largo que os outros é cortado.

    Auditoria 21: um único mês com IC enorme (K1, e = −12) achatava todos os outros pontos. Mês "atípico" = meia
    largura do IC maior que 4 x a mediana das meias larguras. Todos os θ ficam sempre visíveis.
    """
    ok = np.isfinite(lo) & np.isfinite(hi) & np.isfinite(th)
    fin = np.isfinite(th)
    if not ok.any():
        v = th[fin] if fin.any() else np.array([0.0])
        return float(v.min()) - 1, float(v.max()) + 1, False
    meia = (hi - lo)[ok] / 2
    tip = meia <= 4 * np.median(meia)
    vals = np.concatenate([th[fin], lo[ok][tip], hi[ok][tip], [0.0]])
    a, b = float(vals.min()), float(vals.max())
    pad = 0.06 * (b - a if b > a else 1.0)
    ylo, yhi = a - pad, b + pad
    cortado = bool((lo[ok] < ylo).any() or (hi[ok] > yhi).any())
    return ylo, yhi, cortado


def legenda(oid: str, spec: dict, *, cortado: bool = False) -> str:
    corte_txt = (" O eixo vertical foi limitado para que um mês muito incerto não esconda os outros: triângulo na ponta "
                 "da barra = o IC 95% daquele mês vai além do limite, e a banda também é cortada nesse limite (valores "
                 "completos no CSV)." if cortado else "")
    return (
        "COMO LER. Cada ponto é a diferença média entre os municípios que receberam o 1º especialista do PMM-E e os "
        f"que ainda não tinham recebido (ou nunca receberam) na mudança {K1M._o_que(spec)}, em cada mês contado a "
        "partir do trimestre de chegada (0 = primeiro mês do trimestre em que o 1º especialista começou; como ele pode "
        "ter começado no 2º ou no 3º mês do trimestre, os meses 0 e 1 podem ainda ser anteriores à chegada). O mês −1 "
        "é a base (quadrado preto, zero por construção): tudo é medido como mudança em relação a ele. A barra vertical "
        "é o IC 95% de cada mês e a faixa azul clara é a banda de 95% para todos os meses ao mesmo tempo; o fundo bege "
        "marca os meses a partir do trimestre de chegada." + corte_txt + " À esquerda do zero "
        "(antes da chegada) os pontos deveriam ficar em torno de zero; se não ficam, os municípios que receberam "
        "especialista já vinham mudando de outro jeito e a diferença depois da chegada não pode ser atribuída a ela. "
        "À direita, pontos acima de zero indicam valores maiores (mais produção ou mais capacidade, conforme o "
        "outcome) depois da chegada do que nos comparáveis. É uma "
        "comparação sob a hipótese de tendências paralelas (exploratória), não um efeito com exogeneidade validada. "
        "EMPIRICO.")


def figura(oid: str, spec: dict, ev: pd.DataFrame, est: pd.DataFrame, caminho: Path) -> dict:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    S = K1M
    e = ev.sort_values("e")
    x = e["e"].to_numpy()
    th = e["theta"].to_numpy(dtype=float)
    lo, hi = e["ic95_inf"].to_numpy(dtype=float), e["ic95_sup"].to_numpy(dtype=float)
    bl, bh = e["banda_unif_inf"].to_numpy(dtype=float), e["banda_unif_sup"].to_numpy(dtype=float)
    ylo, yhi, cortado = limites_eixo(th, lo, hi)
    cortado = cortado or bool(((bl < ylo) | (bh > yhi))[np.isfinite(bl) & np.isfinite(bh)].any())
    texto = textwrap.wrap(legenda(oid, spec, cortado=cortado), 180)
    h_txt = 0.16 * len(texto) + 0.3
    h_leg, h_xlab, h_plot, h_tit = 0.6, 0.6, 4.0, 1.05
    altura = h_txt + h_leg + h_xlab + h_plot + h_tit
    fig = plt.figure(figsize=(11.5, altura), facecolor=S.SUPERFICIE)
    ax = fig.add_axes([0.09, (h_txt + h_leg + h_xlab) / altura, 0.88, h_plot / altura])
    ax.set_facecolor(S.SUPERFICIE)
    # Fundo do pós em tom neutro, distinto da banda azul (auditoria 21: azul sobre azul escondia a banda no pós).
    ax.axvspan(-0.5, x[np.isfinite(th)].max() + 0.5, color=COR_POS_D2, linewidth=0, zorder=0)
    okb = np.isfinite(bl) & np.isfinite(bh)
    ok = np.isfinite(lo) & np.isfinite(hi)
    ax.fill_between(x[okb], np.clip(bl[okb], ylo, yhi), np.clip(bh[okb], ylo, yhi), color=S.COR_IC, alpha=0.16,
                    linewidth=0, step="mid", zorder=1)
    ax.axhline(0, color=S.TINTA_2, linewidth=0.9)
    ax.axvline(-0.5, color=S.COR_ATO, linestyle="--", linewidth=1.0)
    lo_c, hi_c = np.clip(lo, ylo, yhi), np.clip(hi, ylo, yhi)
    ax.errorbar(x[ok], th[ok], yerr=[th[ok] - lo_c[ok], hi_c[ok] - th[ok]], fmt="none", ecolor=S.COR_IC,
                elinewidth=1.3, alpha=0.7, zorder=2)
    for xi_, lo_i, hi_i in zip(x[ok], lo[ok], hi[ok]):
        if hi_i > yhi:
            ax.plot([xi_], [yhi], marker="^", color=S.COR_IC, markersize=6, zorder=3, clip_on=False)
        if lo_i < ylo:
            ax.plot([xi_], [ylo], marker="v", color=S.COR_IC, markersize=6, zorder=3, clip_on=False)
    ax.set_ylim(ylo, yhi)
    ref = e["referencia"].astype(bool).to_numpy()
    ax.plot(x[~ref], th[~ref], "o", color=S.COR_PONTO, markersize=4.5, zorder=3)
    ax.plot(x[ref], th[ref], "s", color=S.TINTA, markersize=6.5, zorder=4)
    g = est[(est["outcome_id"] == oid) & (est["variante"] == "principal")].set_index("estatistica")
    pos, pre = g.loc["att_pos_medio"], g.loc["pretendencia_wald"]
    ax.set_title(f"ATT médio depois da chegada = {S._fmt(pos['valor'])} [IC 95%: {S._fmt(pos['ic95_inf'])}; "
                 f"{S._fmt(pos['ic95_sup'])}]; teste do pré (todos os meses antes = 0): p = {S._fmt(pre['p_valor'], 3, False)}",
                 fontsize=9.5, color=S.TINTA)
    ax.set_xlabel("meses desde o início do trimestre de chegada do 1º especialista do PMM-E", fontsize=9,
                  color=S.TINTA_2)
    ax.set_ylabel(f"diferença na mudança desde o mês −1,\n{S._rotulo_unidade(spec)}", fontsize=9, color=S.TINTA_2)
    ax.grid(alpha=0.25, linewidth=0.6)
    ax.tick_params(colors=S.TINTA_2, labelsize=8)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",").replace("-", "−")))
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}".replace("-", "−")))
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    handles = [Line2D([], [], marker="o", linestyle="", color=S.COR_PONTO, label="diferença no mês (chegou − comparáveis)"),
               Line2D([], [], color=S.COR_IC, linewidth=1.3, label="IC 95% do mês"),
               Patch(color=S.COR_IC, alpha=0.16, label="banda de 95% para todos os meses"),
               Line2D([], [], marker="s", linestyle="", color=S.TINTA, label="mês −1 = base (zero)"),
               Patch(color=COR_POS_D2, label="a partir do trimestre de chegada")]
    if ((lo < ylo) | (hi > yhi))[ok].any():
        handles.append(Line2D([], [], marker="^", linestyle="", color=S.COR_IC, label="IC além do limite do eixo"))
    fig.legend(handles=handles, loc="center", ncol=3, fontsize=8, frameon=False,
               bbox_to_anchor=(0.5, (h_txt + h_leg / 2) / altura))
    fig.suptitle(f"{oid} — {spec['desc']}\nD2 exploratório: chegada do especialista do PMM-E (Callaway–Sant'Anna)",
                 fontsize=10.5, color=S.TINTA, y=1 - 0.08 / altura)
    fig.text(0.015, 0.1 / altura, "\n".join(texto), fontsize=7.6, color=S.TINTA_2, va="bottom", ha="left",
             linespacing=1.25, parse_math=False)
    fig.savefig(caminho, dpi=120, facecolor=S.SUPERFICIE)
    plt.close(fig)
    return {"arquivo": K1M.rotulo(caminho), "outcome_id": oid, "variante": "principal"}


# ---------------------------------------------------------------------------
# 6. Tabelas do doc 50 (marcadores KD2)
# ---------------------------------------------------------------------------

_n, _p, _tab = K1M._n, K1M._p, K1M._tab
ORDEM = {o: i for i, o in enumerate(OUTCOMES_D2)}


def _fmt_int(v) -> str:
    return "—" if v is None or pd.isna(v) else str(int(v))


def gerar_tabelas_doc(est: pd.DataFrame, ev: pd.DataFrame, resumo: dict) -> dict[str, str]:
    t = {}
    a = resumo.get("amostra", {})
    coortes = resumo.get("coortes", {})
    linhas = ["| Item | Valor |", "|---|---|",
              f"| municípios com célula nos ciclos 1 ou 2 e em U | {a.get('n_municipios')} |",
              f"| municípios com célula fora de U (fora) | {len(a.get('fora_de_U', []))} |",
              f"| municípios tratados (≥ 1 especialista ativo) na amostra | {a.get('n_tratados')} |",
              f"| municípios nunca tratados na amostra | {a.get('n_nunca_tratados')} |",
              f"| tratados com 1ª chegada depois de {a.get('fim_serie_sia')} (fim da série de SIA, SIH e CNES): "
              f"ainda não tratados no horizonte desses outcomes | {a.get('n_chegada_depois_fim_serie_sia')} |",
              f"| tratados com 1ª chegada depois de {a.get('fim_serie_k3')} (fim da série de K3): ainda não "
              f"tratados no horizonte de K3 | {a.get('n_chegada_depois_fim_serie_k3')} |",
              f"| municípios da lista nominal fora da amostra (fora) | {a.get('municipios_com_ativo_fora_da_amostra')} |",
              f"| especialistas da lista nominal nesses municípios | {a.get('especialistas_em_municipios_fora_da_amostra')} |",
              f"| sensibilidade: municípios com alocado e sem ativo (excluídos) | {a.get('n_alocado_sem_ativo')} |"]
    for c, v in coortes.items():
        linhas.append(f"| coorte {c[:4]}-{c[4:]} (trimestre): municípios / especialistas | {v['municipios']} / "
                      f"{v['especialistas']} |")
    t["amostra"] = "\n".join(linhas)
    piv = est[est["variante"] == "principal"].copy()
    linhas = ["| Outcome | Tratados / nunca tratados | Coortes | ATT médio do pós | IC 95% (bootstrap) | p | "
              "θ médio do pré (−24 a −2) | Pré: Wald (gl), p | Pré: p sup-t | Dose por especialista (descritivo) |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    for oid in OUTCOMES_D2:
        g = piv[piv["outcome_id"] == oid].set_index("estatistica")
        if not len(g):
            continue
        pos, w, s, d = g.loc["att_pos_medio"], g.loc["pretendencia_wald"], g.loc["pretendencia_supt"], \
            g.loc["dose_por_especialista"]
        linhas.append(f"| {oid} | {_fmt_int(pos['n_tratados'])} / {_fmt_int(pos['n_nunca_tratados'])} | "
                      f"{_fmt_int(pos['n_coortes'])} | {_n(pos['valor'], 2)} | [{_n(pos['ic95_inf'], 2)}; "
                      f"{_n(pos['ic95_sup'], 2)}] | {_p(pos['p_valor'])} | {_n(media_pre(ev, oid), 2)} | "
                      f"{_n(w['valor'], 1, sinal=False)} "
                      f"({_fmt_int(w['gl'])}), {_p(w['p_valor'])} | {_p(s['p_valor'])} | {_n(d['valor'], 2)} |")
    t["att"] = "\n".join(linhas)
    sen = est[(est["variante"] != "principal") & (est["estatistica"].isin(["att_pos_medio", "pretendencia_wald"]))]
    linhas = ["| Outcome | Variante | ATT médio do pós | IC 95% | p | Pré: p Wald | Tratados / nunca tratados |",
              "|---|---|---|---|---|---|---|"]
    for oid in OUTCOMES_D2:
        g = sen[sen["outcome_id"] == oid]
        for var, gg in g.groupby("variante", sort=False):
            gg = gg.set_index("estatistica")
            pos, w = gg.loc["att_pos_medio"], gg.loc["pretendencia_wald"]
            linhas.append(f"| {oid} | {var} | {_n(pos['valor'], 2)} | [{_n(pos['ic95_inf'], 2)}; "
                          f"{_n(pos['ic95_sup'], 2)}] | {_p(pos['p_valor'])} | {_p(w['p_valor'])} | "
                          f"{_fmt_int(pos['n_tratados'])} / {_fmt_int(pos['n_nunca_tratados'])} |")
    t["sensibilidade"] = "\n".join(linhas)
    e = ev[(ev["variante"] == "principal") & ~ev["referencia"].astype(bool)]
    linhas = ["| Outcome | Janela | Tempos de evento estimados | p < 0,05 | maior abs(θ) | θ médio |",
              "|---|---|---|---|---|---|"]
    for oid in OUTCOMES_D2:
        for j in ("pre", "pos"):
            g = e[(e["outcome_id"] == oid) & (e["janela"] == j) & np.isfinite(e["theta"].astype(float))]
            linhas.append(f"| {oid} | {j} | {len(g)} | {int((g['p_valor'] < 0.05).sum())} | "
                          f"{_n(g['theta'].abs().max() if len(g) else np.nan, 2, sinal=False)} | "
                          f"{_n(g['theta'].mean() if len(g) else np.nan, 2)} |")
    t["evento"] = "\n".join(linhas)
    linhas = ["| Data | Tipo | Item | Descrição |", "|---|---|---|---|"]
    for dv in resumo.get("desvios", []):
        linhas.append(f"| {dv['data']} | {dv['tipo']} | {dv['item']} | {dv['descricao']} |")
    t["desvios"] = "\n".join(linhas)
    t.update(gerar_leitura(est, ev))
    return t


def media_pre(ev: pd.DataFrame, oid: str, var: str = "principal", *, e_min: int = E_MIN) -> float:
    g = ev[(ev["outcome_id"] == oid) & (ev["variante"] == var) & (ev["e"] <= -2) & (ev["e"] >= e_min)]["theta"].astype(float)
    g = g[np.isfinite(g)]
    return float(g.mean()) if len(g) else float("nan")


def _pos(est, oid, var="principal"):
    g = est[(est["outcome_id"] == oid) & (est["variante"] == var)].set_index("estatistica")
    return (g.loc["att_pos_medio"].to_dict(), g.loc["pretendencia_wald"].to_dict()) if len(g) else (None, None)


def gerar_leitura(est: pd.DataFrame, ev: pd.DataFrame) -> dict[str, str]:
    t = {}
    partes = []
    planos = 0
    for oid in OUTCOMES_D2:
        pos, pre = _pos(est, oid)
        if pos is None:
            continue
        plano = np.isfinite(pre["p_valor"]) and pre["p_valor"] >= 0.05
        planos += int(plano)
        partes.append(f"{oid}: ATT médio do pós {_n(pos['valor'], 2)} por 10 mil hab. por mês (IC 95% "
                      f"[{_n(pos['ic95_inf'], 2)}; {_n(pos['ic95_sup'], 2)}], p = {_p(pos['p_valor'])}); pré "
                      + ("compatível com plano" if plano else "não plano") + f" (p do Wald = {_p(pre['p_valor'])})")
    def pre_parecido(oid):
        """θ médio do pré com o mesmo sinal e >= metade do ATT do pós (diferença já presente antes da chegada).

        Vale o pré inteiro (−24 a −2) ou os 12 meses antes do mês-base (−13 a −2): a auditoria 21 acrescentou a
        segunda média, só no sentido de pôr ressalva (nunca de tirá-la), porque meses distantes e ruidosos podiam
        diluir uma diferença que já estava presente no ano anterior à chegada.
        """
        pos, _ = _pos(est, oid)
        mp, mp12 = media_pre(ev, oid), media_pre(ev, oid, e_min=-13)

        def parecido(m):
            return (pos is not None and np.isfinite(m) and np.isfinite(pos["valor"]) and pos["valor"] != 0
                    and np.sign(m) == np.sign(pos["valor"]) and abs(m) >= 0.5 * abs(pos["valor"]))
        return parecido(mp) or parecido(mp12), mp, mp12, pos

    base_alta, base_oposta = [], []
    for oid in OUTCOMES_D2:
        sim, mp, mp12, pos = pre_parecido(oid)
        if sim:
            base_alta.append(f"{oid} (θ médio do pré {_n(mp, 2)}; nos 12 meses antes do mês-base {_n(mp12, 2)}; "
                             f"ATT do pós {_n(pos['valor'], 2)})")
        elif (pos is not None and np.isfinite(mp) and np.isfinite(pos["valor"]) and pos["valor"] != 0
              and np.sign(mp) == -np.sign(pos["valor"]) and abs(mp) >= 0.5 * abs(pos["valor"])):
            base_oposta.append(f"{oid} (θ médio do pré {_n(mp, 2)}; ATT do pós {_n(pos['valor'], 2)})")
    nota_base = ("" if not base_alta else
                 " Em " + "; ".join(base_alta) + ", o θ médio do pré (inteiro ou nos 12 meses antes do mês-base) tem o "
                 "mesmo sinal e pelo menos metade do tamanho do ATT do pós: boa parte da diferença do pós já aparece "
                 "antes da chegada, em relação ao mês-base, e não pode ser lida como mudança causada pela chegada.")
    if base_oposta:
        nota_base += (" Em " + "; ".join(base_oposta) + ", o θ médio do pré tem sinal oposto ao do ATT do pós e pelo "
                      "menos metade do tamanho (auditoria 21): o ATT depende do mês-base (−1); contra a média do pré a "
                      "diferença seria maior, e uma subida (ou queda) que começou antes da chegada não é descartada "
                      "pelo teste conjunto, que tem pouco poder contra tendências suaves.")
    sig = [oid for oid in OUTCOMES_D2 if (p := _pos(est, oid)[0]) is not None and np.isfinite(p["p_valor"])
           and p["p_valor"] < 0.05]
    nota_mult = (f" O D2 não tem correção para múltiplos testes: {len(sig)} de {len(partes)} ATT médios do pós têm "
                 f"p < 0,05 ({', '.join(sig) or 'nenhum'}), e por acaso, a 5%, esperam-se cerca de "
                 f"{_n(0.05 * len(partes), 1, sinal=False)} (auditoria 21).")
    t["leitura_d2"] = ("; ".join(partes) + f". {planos} de {len(partes)} outcomes têm pré compatível com tendências "
                       "paralelas pelo teste conjunto a 5%. Onde o pré não é plano, a diferença do pós é só uma "
                       "associação; onde é plano, continua sendo ATT sob tendências paralelas, porque a chegada depende "
                       "da escolha do candidato, sem fonte de exogeneidade validada." + nota_base + nota_mult)

    def linha(oid):
        pos, _ = _pos(est, oid)
        return None if pos is None else {"ic95_inf": pos["ic95_inf"], "ic95_sup": pos["ic95_sup"]}

    pares = {"sus": linha("K1"), "privado_vinculos": linha("K4.vinculos"), "privado_horas": linha("K4.horas"),
             "total": linha("K3"), "nao_alvo": linha("KP2")}
    simples = []
    for oid, nome in (("K1", "produção SUS dos especialistas-alvo"), ("K2", "cirurgias com internação no SUS"),
                      ("K4.vinculos", "vínculos privados (não SUS) dos especialistas-alvo"),
                      ("K3", "consultas SUS + planos dos especialistas-alvo")):
        pos, pre = _pos(est, oid)
        if pos is None:
            continue
        c = K1M.classificar({"ic95_inf": pos["ic95_inf"], "ic95_sup": pos["ic95_sup"]})
        verbo = {"sobe": "ficou maior do que nos comparáveis", "cai": "ficou menor do que nos comparáveis",
                 "indeterminado": "não se distingue da dos comparáveis"}.get(c, "não tem estimativa")
        plano = np.isfinite(pre["p_valor"]) and pre["p_valor"] >= 0.05
        aviso = ""
        if not plano:
            aviso = " (mas o município já vinha diferente antes da chegada)"
        elif pre_parecido(oid)[0] and c != "indeterminado":
            aviso = " (mas boa parte dessa diferença já aparecia antes da chegada, em relação ao mês-base)"
        simples.append(f"{nome} ({oid}): a mudança {verbo}{aviso}")
    t["leitura_simples_d2"] = (
        "Em linguagem simples, depois que o 1º especialista do PMM-E começou no município: "
        + "; ".join(simples) + ". Os comparáveis são municípios que também ofereceram vaga e ainda não tinham "
        "recebido especialista. Como quem chega escolhe o município, isso é uma comparação, não a prova de um efeito.")
    t["leitura_substituicao_d2"] = K1M.leitura_substituicao(pares, desenho="D2 (chegada, ATT médio do pós)").replace(
        "consultas SUS + planos nas CBO-alvo (K3)", "consultas SUS + planos nas CBO-alvo (K3, coortes até 2025-12)")
    ressalva = [oid for oid, k in (("K1", "sus"), ("K4.vinculos", "privado_vinculos"), ("K4.horas", "privado_horas"),
                                   ("K3", "total"), ("KP2", "nao_alvo"))
                if pares[k] is not None and K1M.classificar(pares[k]) in ("sobe", "cai") and pre_parecido(oid)[0]]
    if ressalva:
        t["leitura_substituicao_d2"] += (
            " Ressalva (auditoria 21): em " + ", ".join(ressalva) + " o θ médio do pré (inteiro ou nos 12 meses antes "
            "do mês-base) tem o mesmo sinal e pelo menos metade do ATT do pós, então o sinal dessa margem não se lê "
            "como mudança causada pela chegada.")
    return t


MARCA = re.compile(r"(<!-- KD2:(?P<nome>[A-Za-z0-9_]+):inicio -->\n)(?P<corpo>.*?)(\n<!-- KD2:(?P=nome):fim -->)", re.S)


def aplicar_tabelas_doc(texto: str, tabelas: dict[str, str]) -> str:
    def sub(m):
        nome = m.group("nome")
        if nome not in tabelas:
            raise KeyError(f"tabela {nome} nao gerada")
        return m.group(1) + tabelas[nome] + m.group(4)
    return MARCA.sub(sub, texto)


def tabelas_no_doc(texto: str) -> dict[str, str]:
    return {m.group("nome"): m.group("corpo") for m in MARCA.finditer(texto)}


def ler_saidas():
    est = pd.read_csv(OUT / NOME_EST)
    ev = pd.read_csv(OUT / NOME_EVENTO)
    resumo = json.loads((OUT / NOME_RESUMO).read_text(encoding="utf-8"))
    return est, ev, resumo


def atualizar_doc() -> None:
    if not DOC50.exists():
        print(f"{K1M.rotulo(DOC50)} nao existe: tabelas nao gravadas")
        return
    est, ev, resumo = ler_saidas()
    DOC50.write_text(aplicar_tabelas_doc(DOC50.read_text(encoding="utf-8"), gerar_tabelas_doc(est, ev, resumo)),
                     encoding="utf-8")
    print(f"tabelas KD2 do doc 50 regravadas: {K1M.rotulo(DOC50)}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--atualizar-doc", action="store_true")
    args = ap.parse_args(argv)
    if args.atualizar_doc:
        atualizar_doc()
        return 0
    try:
        D = K1M.carregar_dados()
        amostra, info_am = ler_amostra(D.base)
        chegadas, info_ch = ler_chegadas(amostra)
        aloc_sem = ler_alocados_sem_ativo(chegadas)
        xi = pesos_mammen(B_BOOT, len(amostra), SEMENTE)
        ev_l, att_l, est_l = rodar(D, amostra, chegadas, xi, "principal")
        am2 = amostra.difference(pd.Index(aloc_sem))
        ch2 = chegadas.reindex(am2)
        xi2 = pesos_mammen(B_BOOT, len(am2), SEMENTE)
        a, b, c = rodar(D, am2, ch2, xi2, "sem_alocado_sem_ativo")
        ev_l += a
        att_l += b
        est_l += c
    except (FalhaValidacao, K1M.FalhaValidacao) as erro:
        print(f"FALHA DE VALIDACAO (nada gravado): {erro}", file=sys.stderr)
        return 2
    ev = pd.DataFrame(ev_l)[COLUNAS_EVENTO]
    att = pd.DataFrame(att_l)[COLUNAS_ATT]
    est = pd.DataFrame(est_l)[COLUNAS_EST]
    OUT.mkdir(parents=True, exist_ok=True)
    att.to_csv(OUT / NOME_ATT, index=False)
    ev.to_csv(OUT / NOME_EVENTO, index=False)
    est.to_csv(OUT / NOME_EST, index=False)
    dir_fig = OUT / DIR_FIG
    dir_fig.mkdir(parents=True, exist_ok=True)
    for antigo in dir_fig.glob("*.png"):
        antigo.unlink()
    figuras = []
    for oid in OUTCOMES_D2:
        spec = next(c for c in K1M.CATALOGO if c["id"] == oid)
        figuras.append(figura(oid, spec, ev[(ev["outcome_id"] == oid) & (ev["variante"] == "principal")], est,
                              dir_fig / f"K_D2_evento_{oid.replace('.', '_')}.png"))
    trat = chegadas[chegadas["coorte"].notna()]
    coortes = {c: {"municipios": int(len(g)), "especialistas": int(g["n_especialistas"].sum())}
               for c, g in trat.groupby("coorte")}
    resumo = {
        "natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "gerador": K1M.rotulo(Path(__file__)),
        "data_execucao": DATA_EXECUCAO,
        "protocolo": {"texto": K1M.rotulo(PROTOCOLO_MD), "sha256_texto": K1M.sha256(PROTOCOLO_MD), "secao": "§5 D2"},
        "contraste": CONTRASTE,
        "parametros": {"e_min": E_MIN, "e_max": E_MAX, "bootstrap": {"B": B_BOOT, "pesos": "Mammen", "semente": SEMENTE,
                                                                     "cluster": "municipio (unidade)"},
                       "base": "universal, b = g - 1", "controles": "nunca tratados + ainda nao tratados (G > max(t, b))",
                       "fim_da_serie": FIM, "coorte_max_K3": COORTE_MAX_K3, "inicio": INICIO},
        "amostra": {**info_am, **info_ch, "n_municipios": int(len(amostra)),
                    "n_tratados": int(chegadas["coorte"].notna().sum()),
                    "n_nunca_tratados": int(chegadas["coorte"].isna().sum()),
                    "n_alocado_sem_ativo": len(aloc_sem),
                    "fim_serie_sia": FIM["SIA"], "fim_serie_k3": FIM["K3"],
                    "n_chegada_depois_fim_serie_sia": int((chegadas["chegada"] > FIM["SIA"]).sum()),
                    "n_chegada_depois_fim_serie_k3": int((chegadas["chegada"] > FIM["K3"]).sum())},
        "coortes": coortes,
        "variantes": VARIANTES,
        "entradas": [K1M.E7.bloco_entrada(NOMINAL, "tratamento: menor dt_inicio_atividade por municipio",
                                          "MS, lista nominal do PMM-E (retrato)", ", ".join(info_ch["dt_referencia"]),
                                          "especialistas ativos no retrato", "especialista", "co_ibge",
                                          f"so as colunas {', '.join(COLUNAS_NOMINAL)}; nenhum nome lido ou gravado"),
                     K1M.E7.bloco_entrada(ARQ_VM, "amostra (celulas nos ciclos 1 ou 2)", "tarefa B (12)", "ciclos 1-2",
                                          "V1, V2", "municipio x ciclo", "ciclo, co_ibge", "ciclo in (1, 2)"),
                     K1M.E7.bloco_entrada(X2_MUN, "sensibilidade: alocados na 1a chamada", "X2 (18)", "ciclos 1-2",
                                          "municipios com celula", "municipio x ciclo", "ciclo, co_ibge",
                                          "n_alocados > 0"),
                     *[b for b in K1M.entradas() if b["caminho"] in {K1M.rotulo(p) for p in (
                         K1M.SIA, K1M.SIH, K1M.TISS, K1M.CNES, K1M.POP22, K1M.A08)}]],
        "desvios": DESVIOS,
        "contagens": {"linhas_att_gt": int(len(att)), "linhas_evento": int(len(ev)), "linhas_estimativas": int(len(est))},
        "figuras": figuras,
        "saidas": [K1M.rotulo(OUT / n) for n in (NOME_ATT, NOME_EVENTO, NOME_EST, NOME_RESUMO)],
    }
    K1M._gravar_json(OUT / NOME_RESUMO, resumo)
    atualizar_doc()
    p = est[(est["variante"] == "principal") & (est["estatistica"] == "att_pos_medio")]
    print("D2: " + "; ".join(f"{r.outcome_id} {r.valor:.2f} p={r.p_valor:.3f}" for r in p.itertuples()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
