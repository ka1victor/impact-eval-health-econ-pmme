"""Protocolo 59, parte A: sensibilidade de Rambachan–Roth (2023) dos estudos de evento do P3, do P4 e do CA.

Protocolo congelado: `docs/06_execucao/59_protocolo_P3P4_sensibilidade_comparacao.md`, §2. Rótulo de toda linha:
`SENSIBILIDADE` (estatuto `PROTOCOLO_59_POS_RESULTADO`); `natureza_dos_dados = EMPIRICO`. Não muda nenhuma
estimativa pontual.

- θ(e) e as funções de influência são recalculados com as funções dos scripts 22, 27 e 28 (as saídas versionadas
  não guardam a covariância); o script para se os θ(e) não baterem com `K_X_estudo_evento.csv` e
  `P4_estimativas.csv` (≤ 1e−8) ou se o EP analítico não bater com o versionado no P3.
- Σ = covariância analítica das funções de influência (cluster no município no P3, no médico no P4); no CA, a
  covariância gravada pelo script 35 (`CA_covariancia.csv`).
- Restrições Δ^RM(M̄) (teste condicional ARP, união dos poliedros) e Δ^SD(M) (FLCI), alvos média do pós e θ(0),
  pontos de ruptura; implementação em `honestdid_lib.py` (validada em `tests/test_honestdid.py`).
- Gera também `docs/06_execucao/57h_resultados_P3P4_sensibilidade.md`, a partir de `output/` (H_* e CA_*).

Uso
---
    python3 scripts/rdd_bolsa/34_sensibilidade_honestdid.py --etapa estimar    # recalcula (demorado)
    python3 scripts/rdd_bolsa/34_sensibilidade_honestdid.py --etapa doc        # só regera o doc 57h
    python3 scripts/rdd_bolsa/34_sensibilidade_honestdid.py                    # verificar (padrão)
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

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


H = _importar(DIR_RDD / "honestdid_lib.py", "honestdid_lib")

OUT = ROOT / "output" / "rdd_bolsa"
PROTOCOLO_MD = ROOT / "docs" / "06_execucao" / "59_protocolo_P3P4_sensibilidade_comparacao.md"
DOC = ROOT / "docs" / "06_execucao" / "57h_resultados_P3P4_sensibilidade.md"
NOME_EST = "H_estimativas.csv"
NOME_COEF = "H_coeficientes.csv"
NOME_RESUMO = "H_resumo.json"
DIR_FIG = "H_figuras"
KX_EVENTO = OUT / "K_X_estudo_evento.csv"
KX_EST = OUT / "K_X_estimativas.csv"
P4_EST = OUT / "P4_estimativas.csv"
CA_EST = OUT / "CA_estimativas.csv"
CA_EVENTO = OUT / "CA_estudo_evento.csv"
CA_COV = OUT / "CA_covariancia.csv"
CA_RESUMO = OUT / "CA_resumo.json"

DATA_EXECUCAO = "2026-10-26"
DATA_ADENDO = "2026-10-25"  # data do adendo ao protocolo 59, não da execução
ESTATUTO = "PROTOCOLO_59_POS_RESULTADO"
ROTULO = "SENSIBILIDADE"
NATUREZA = "EMPIRICO"
ALPHA = 0.05
GRADE_RM = (0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0)
GRADE_SD = (0.0, 0.05, 0.1, 0.25, 0.5, 1.0)
MAX_RM, TOL_RM = 4.0, 0.01
MAX_SD, TOL_SD = 4.0, 0.01
TOL_REPRODUCAO = 1e-8
WORKERS = 4

P3_LINHAS = [("H-P3-K_esp", "12.2", "K_esp", "todos_os_cursos", "produção típica da especialidade no par (12.2)",
              "principal"),
             ("H-P3-K2r", "12.4", "K2r", "", "internações cirúrgicas de residentes (12.4, D2)", "secundária"),
             ("H-P3-K2r_tot", "12.4", "K2r_tot", "", "todas as internações de residentes (12.4, D2)", "secundária"),
             ("H-P3-K1_reg", "12.5", "K1_reg", "", "K1 nos outros municípios da região (12.5)", "secundária"),
             ("H-P3-K2_reg", "12.5", "K2_reg", "", "K2 nos outros municípios da região (12.5)", "secundária")]
P3_PRE, P3_POS = (-12, -2), (0, 9)
P4_PRE, P4_POS = (-6, -2), (0, 6)
P4_PRINCIPAIS = ("horas_totais", "horas_mun_posto", "horas_fora_mun_posto")
CA_PRE = {"P3": (-12, -2), "P4": (-12, -2)}
CA_POS = {"P3": (0, 9), "P4": (0, 5)}

COLUNAS = ["natureza_dos_dados", "estatuto", "rotulo", "id_linha", "pergunta", "origem", "outcome", "descricao",
           "leitura", "alvo", "restricao", "parametro", "M_absoluto", "estimativa", "ep_analitico", "ic_inf",
           "ic_sup", "exclui_zero", "id_inf", "id_sup", "id_vazio", "censura", "T_pre", "T_pos", "e_pre", "e_pos",
           "u", "metodo", "nota"]


class FalhaValidacao(RuntimeError):
    """Validação obrigatória falhou: o script para sem gravar."""


def rotulo(p: Path) -> str:
    return Path(p).resolve().relative_to(ROOT).as_posix()


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with Path(p).open("rb") as f:
        for bloco in iter(lambda: f.read(1 << 22), b""):
            h.update(bloco)
    return h.hexdigest()


def _nan_none(o):
    if isinstance(o, dict):
        return {str(k): _nan_none(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_nan_none(v) for v in o]
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, (np.floating, float)):
        return None if not np.isfinite(o) else float(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


def gravar_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(_nan_none(obj), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# 1. Estudos de evento: θ(e) e Σ recalculados e conferidos
# ---------------------------------------------------------------------------

def _conferir_theta(nome: str, es: np.ndarray, th: np.ndarray, ref: pd.Series) -> float:
    r = ref.reindex(es).to_numpy(float)
    ok = np.isfinite(th) | np.isfinite(r)
    dif = np.nanmax(np.abs(np.where(ok, th - r, 0.0))) if ok.any() else 0.0
    if not np.isfinite(dif) or dif > TOL_REPRODUCAO or (np.isfinite(th) != np.isfinite(r)).any():
        raise FalhaValidacao(f"{nome}: θ(e) recalculado não bate com o versionado (dif {dif})")
    return float(dif)


def estudos_p3() -> tuple[list[dict], dict]:
    k27 = _importar(DIR_RDD / "27_producao_extensoes.py", "k27_para_h")
    K1M, D2M = k27.K1M, k27.D2M
    base, _ = K1M.ler_universo()
    universo = base.index
    pop = base["populacao_2022"].astype(float)
    sia, _ = K1M.ler_sia(universo)
    sih1, sih1_atip, _ = K1M.ler_sih(universo)
    D = K1M.Dados(base, sia, sih1, sih1_atip, None, None, None, None, None, {})
    amostra, _ = D2M.ler_amostra(base)
    chegadas, _ = D2M.ler_chegadas(amostra)
    meses = list(k27.MESES)
    ref = pd.read_csv(KX_EVENTO, dtype={"item": str})
    ref = ref[ref["variante"] == "principal"]
    out, conf = [], {}

    def guardar(id_linha, item, oid, recorte, desc, leitura, tab, IF, chave, clus):
        ev, IFe = D2M.agregar_evento(tab, IF, chave, e_min=D2M.E_MIN, e_max=D2M.E_MAX)
        IFc, M = k27.somar_cluster(IFe, clus)
        es = ev["e"].to_numpy()
        th = ev["theta"].to_numpy(float)
        r = ref[(ref["item"] == item) & (ref["outcome_id"] == oid)]
        if recorte:
            r = r[r["recorte"] == recorte]
        else:
            r = r[r["desenho"] == "D2"]
        rr = r.set_index("e")
        if rr.index.duplicated().any():
            raise FalhaValidacao(f"{id_linha}: mais de uma série versionada")
        dif = _conferir_theta(id_linha, es, th, rr["theta"])
        ok = np.isfinite(IFc).all(axis=0)
        V = np.full((es.size, es.size), np.nan)
        V[np.ix_(ok, ok)] = IFc[:, ok].T @ IFc[:, ok] / M ** 2
        ep_a = np.sqrt(np.diag(V))
        ref_ep = rr["ep_analitico"].reindex(es).to_numpy(float)
        m = np.isfinite(ref_ep) & np.isfinite(ep_a) & (es != -1)
        dif_ep = float(np.max(np.abs(ep_a[m] - ref_ep[m]))) if m.any() else 0.0
        if dif_ep > 1e-6:
            raise FalhaValidacao(f"{id_linha}: EP analítico recalculado não bate com o versionado ({dif_ep})")
        conf[id_linha] = {"dif_max_theta": dif, "dif_max_ep_analitico": dif_ep, "n_clusters": int(M)}
        out.append({"id_linha": id_linha, "pergunta": "P3", "origem": f"57c, {item}", "outcome": oid,
                    "descricao": desc, "leitura": leitura, "e": es, "theta": th, "V": V,
                    "pre": P3_PRE, "pos": P3_POS})

    # 12.2
    cursos, tip, conj, _ = k27.ler_cursos_especificos()
    a17, _ = k27.ler_a17(cursos, tip, conj, universo)
    pares, _ = k27.ler_pares(base, cursos)
    taxas = {c: k27.serie_taxa(a17[c], pop, universo) for c in cursos}
    pos_u = {m: i for i, m in enumerate(universo)}
    Yp = np.vstack([taxas[c][pos_u[m]] for m, c in zip(pares["co_ibge"], pares["cod_curso"])])
    Gp, _ = D2M.indices_coorte(pares, meses)
    grupo = pares["cod_curso"].to_numpy()
    coortes_p = sorted({(int(c), int(g)) for c, g in zip(grupo, Gp) if g >= 0})
    tab, IF, chave = k27.att_gt_geral(Yp, Gp, coortes_p, grupo=grupo)
    guardar(*P3_LINHAS[0], tab, IF, chave, pares["co_ibge"].to_numpy())
    # 12.4 e 12.5 (D2 municipal)
    resid, _, _ = k27.ler_sih_residencia(universo)
    num_k1 = D.sia_soma(("alvo_pmme",), K1M.TIPOS_K1)
    cir, _ = k27.ler_cir()
    G, coortes = D2M.indices_coorte(chegadas, meses)
    series = {"K2r": k27.serie_taxa(resid["K2r"], pop, amostra),
              "K2r_tot": k27.serie_taxa(resid["K2r_tot"], pop, amostra),
              "K1_reg": k27.serie_regional(num_k1, pop, cir, amostra)[0],
              "K2_reg": k27.serie_regional(sih1, pop, cir, amostra)[0]}
    for linha in P3_LINHAS[1:]:
        Y = series[linha[2]]
        tab, IF, chave = k27.att_gt_geral(Y, G, [(None, g) for g in coortes])
        guardar(*linha, tab, IF, chave, amostra.to_numpy())
    return out, conf


def estudos_p4() -> tuple[list[dict], dict]:
    P4M = _importar(DIR_RDD / "28_trajetoria_medicos.py", "p4_para_h")
    dados = P4M.carregar()
    comps = dados["comps"]
    m, _ = P4M.medicos_da_regra("d1_pos_hoc", dados["li"], dados["x1"], dados["chaves"], comps)
    p = P4M.painel_medico(m, dados["v"], comps)
    G = m["G"].to_numpy()
    trat = m["tratavel"].to_numpy()
    coortes = sorted(int(g) for g in np.unique(G[trat]) if g >= 1)
    membro = {g: (G == g) & trat for g in coortes}
    ref = pd.read_csv(P4_EST)
    ref = ref[(ref["especificacao"] == "T4.1b") & (ref["regra_ligacao"] == "d1_pos_hoc")
              & (ref["janela"] == "[-6,6]") & (ref["medida"] == "att_e")]
    out, conf = [], {}
    for o, rot, _ in P4M.OUTCOMES:
        Y = P4M.matriz(p, m, o, comps)
        tab, IF = P4M.att_gt(Y, G, trat, coortes, e_min=-6, e_max=6)
        ev, IFe = P4M.agregar_evento(tab, IF, membro, e_min=-6, e_max=6)
        es = ev["e"].to_numpy()
        th = ev["theta"].to_numpy(float)
        rr = ref[ref["outcome"] == o].set_index("e")["estimativa"]
        rr = rr.reindex(es)
        rr.loc[-1] = 0.0
        dif = _conferir_theta(f"P4 {o}", es, th, rr)
        N = IFe.shape[0]
        ok = np.isfinite(IFe).all(axis=0)
        V = np.full((es.size, es.size), np.nan)
        V[np.ix_(ok, ok)] = IFe[:, ok].T @ IFe[:, ok] / N ** 2
        conf[f"H-P4-{o}"] = {"dif_max_theta": dif, "n_medicos": int(N)}
        out.append({"id_linha": f"H-P4-{o}", "pergunta": "P4", "origem": "57d, T4.1b (D1, janela principal)",
                    "outcome": o, "descricao": rot, "leitura": "principal" if o in P4_PRINCIPAIS else "secundária",
                    "e": es, "theta": th, "V": V, "pre": P4_PRE, "pos": P4_POS})
    return out, conf


def estudos_ca() -> list[dict]:
    est = pd.read_csv(CA_EST)
    ev = pd.read_csv(CA_EVENTO)
    cov = pd.read_csv(CA_COV)
    prim = est[(est["familia"] == "holm_CA") & (est["status"] == "EXECUTADO")]
    out = []
    for r in prim.itertuples(index=False):
        s = ev[(ev["id_linha"] == r.id_linha) & (ev["outcome"] == r.outcome)].sort_values("e")
        c = cov[(cov["id_linha"] == r.id_linha) & (cov["outcome"] == r.outcome)]
        es = s["e"].to_numpy()
        pos = {e: i for i, e in enumerate(es)}
        V = np.full((es.size, es.size), np.nan)
        for x in c.itertuples(index=False):
            V[pos[x.e_i], pos[x.e_j]] = x.cov
        out.append({"id_linha": f"H-CA-{r.pergunta}-{r.outcome}", "pergunta": f"CA-{r.pergunta}",
                    "origem": f"57h, {r.id_linha} (protocolo 59 §{3 if r.pergunta == 'P3' else 4})",
                    "outcome": r.outcome, "descricao": r.descricao_outcome, "leitura": "secundária",
                    "e": es, "theta": s["theta"].to_numpy(float), "V": V,
                    "pre": CA_PRE[r.pergunta], "pos": CA_POS[r.pergunta]})
    return out


# ---------------------------------------------------------------------------
# 2. Sensibilidade por estudo de evento (paralelizável; determinística)
# ---------------------------------------------------------------------------

def recortar(est: dict) -> tuple[np.ndarray, np.ndarray, list[int], list[int], str]:
    es, th, V = est["e"], est["theta"], est["V"]
    pos = {int(e): i for i, e in enumerate(es)}
    nota = ""
    pre = []
    for e in range(-2, est["pre"][0] - 1, -1):
        i = pos.get(e)
        if i is None or not np.isfinite(th[i]) or not np.isfinite(V[i, i]):
            nota = f"pré truncado em e = {e + 1} (θ ausente em e = {e})"
            break
        pre.append(e)
    pre = sorted(pre)
    post = []
    for e in range(est["pos"][0], est["pos"][1] + 1):
        i = pos.get(e)
        if i is None or not np.isfinite(th[i]) or not np.isfinite(V[i, i]):
            nota += f"; pós truncado em e = {e - 1}"
            break
        post.append(e)
    idx = [pos[e] for e in pre + post]
    beta = th[idx]
    Sig = V[np.ix_(idx, idx)]
    Sig = (Sig + Sig.T) / 2
    return beta, Sig, pre, post, nota.strip("; ")


def tarefas(estudos: list[dict]) -> list[tuple[dict, str, str]]:
    """(estudo, alvo, método do Δ^RM): o condicional (congelado) em todas as linhas; o híbrido (adendo) nas
    principais e nas do CA."""
    out = []
    for est in estudos:
        for alvo in ("media_pos", "theta0"):
            out.append((est, alvo, "condicional"))
            if est["leitura"] == "principal" or est["pergunta"].startswith("CA"):
                out.append((est, alvo, "hibrido"))
    return out


def analisar(tarefa: tuple[dict, str, str]) -> list[dict]:
    est, alvo, metodo = tarefa
    beta, Sig, pre, post, nota = recortar(est)
    Tp, Tq = len(pre), len(post)
    u = math.sqrt(Sig[Tp, Tp])
    comum = {"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "rotulo": ROTULO, "id_linha": est["id_linha"],
             "pergunta": est["pergunta"], "origem": est["origem"], "outcome": est["outcome"],
             "descricao": est["descricao"], "leitura": est["leitura"], "T_pre": Tp, "T_pos": Tq,
             "e_pre": f"{pre[0]}..{pre[-1]}", "e_pos": f"{post[0]}..{post[-1]}", "u": u, "nota": nota}
    linhas = []
    z = stats.norm.ppf(1 - ALPHA / 2)
    l = np.ones(Tq) / Tq if alvo == "media_pos" else np.eye(Tq)[0]
    est_pt = float(l @ beta[Tp:])
    if metodo == "condicional":
        max2 = H.max_segunda_diferenca_pre(beta, Tp)
        max1 = H.max_primeira_diferenca_pre(beta, Tp)
        ep = math.sqrt(float(l @ Sig[Tp:, Tp:] @ l))
        linhas.append({**comum, "alvo": alvo, "restricao": "original", "parametro": np.nan, "M_absoluto": np.nan,
                       "estimativa": est_pt, "ep_analitico": ep, "ic_inf": est_pt - z * ep, "ic_sup": est_pt + z * ep,
                       "exclui_zero": H.exclui_zero(est_pt - z * ep, est_pt + z * ep),
                       "metodo": "IC normal com a covariância analítica (referência; não é o IC bootstrap do doc)",
                       "id_inf": np.nan, "id_sup": np.nan, "id_vazio": np.nan, "censura": ""})
        linhas.append({**comum, "alvo": alvo, "restricao": "descritivo_pre", "parametro": max1 / u,
                       "M_absoluto": max2, "estimativa": est_pt, "metodo":
                       "parametro = maior |1ª diferença| do pré / u; M_absoluto = maior |2ª diferença| do pré",
                       "censura": ""})
    rot_rm = "RM" if metodo == "condicional" else "RM_hibrido"
    desc_rm = ("teste condicional ARP (congelado no protocolo), união dos poliedros" if metodo == "condicional" else
               "híbrido condicional–LF de ARP (κ = α/10, 1.000 simulações; adendo de 25/10/2026), união dos poliedros")
    cache_rm: dict[float, tuple[float, float]] = {}

    def ic_rm(mb: float) -> tuple[float, float]:
        k = round(mb, 6)
        if k not in cache_rm:
            r = H.ic_rm(beta, Sig, Tp, Tq, l, mb, ALPHA, metodo=metodo)
            cache_rm[k] = (r["ic_inf"], r["ic_sup"])
        return cache_rm[k]

    for mb in GRADE_RM:
        lo, hi = ic_rm(mb)
        ids = H.conjunto_identificado_rm(beta, Tp, Tq, l, mb)
        linhas.append({**comum, "alvo": alvo, "restricao": rot_rm, "parametro": mb, "M_absoluto": np.nan,
                       "estimativa": est_pt, "ic_inf": lo, "ic_sup": hi, "exclui_zero": H.exclui_zero(lo, hi),
                       "id_inf": ids[0] if ids else np.nan, "id_sup": ids[1] if ids else np.nan,
                       "id_vazio": ids is None, "metodo": desc_rm, "censura": ""})
    br = H.ruptura(ic_rm, MAX_RM, TOL_RM)
    linhas.append({**comum, "alvo": alvo, "restricao": f"{rot_rm}_ruptura", "parametro": br["ruptura"],
                   "estimativa": est_pt, "censura": br["censura"], "metodo": f"bisseção em M̄ ∈ [0; 4]; {desc_rm}"})
    if metodo != "condicional":
        return linhas
    cache_sd: dict[float, tuple[float, float]] = {}

    def ic_sd(k: float) -> tuple[float, float]:
        kk = round(k, 6)
        if kk not in cache_sd:
            cache_sd[kk] = H.flci_sd(beta, Sig, Tp, Tq, l, k * u, ALPHA).ic
        return cache_sd[kk]

    for k in GRADE_SD:
        lo, hi = ic_sd(k)
        ids = H.conjunto_identificado_sd(beta, Tp, Tq, l, k * u)
        linhas.append({**comum, "alvo": alvo, "restricao": "SD", "parametro": k, "M_absoluto": k * u,
                       "estimativa": est_pt, "ic_inf": lo, "ic_sup": hi, "exclui_zero": H.exclui_zero(lo, hi),
                       "id_inf": ids[0] if ids else np.nan, "id_sup": ids[1] if ids else np.nan,
                       "id_vazio": ids is None, "metodo": "FLCI", "censura": ""})
    bs = H.ruptura(ic_sd, MAX_SD, TOL_SD)
    linhas.append({**comum, "alvo": alvo, "restricao": "SD_ruptura", "parametro": bs["ruptura"],
                   "M_absoluto": bs["ruptura"] * u, "estimativa": est_pt, "censura": bs["censura"],
                   "metodo": "bisseção em M/u ∈ [0; 4]"})
    return linhas


def coeficientes(est: dict) -> list[dict]:
    beta, Sig, pre, post, _ = recortar(est)
    es = pre + post
    out = []
    for i, ei in enumerate(es):
        for j, ej in enumerate(es):
            out.append({"natureza_dos_dados": NATUREZA, "id_linha": est["id_linha"], "e_i": ei, "e_j": ej,
                        "theta_i": beta[i], "cov": Sig[i, j]})
    return out


# ---------------------------------------------------------------------------
# 3. Figuras
# ---------------------------------------------------------------------------

def gerar_figuras(tab: pd.DataFrame, dir_fig: Path) -> list[dict]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    dir_fig.mkdir(parents=True, exist_ok=True)
    figs = []
    principais = tab[(tab["leitura"] == "principal") & (tab["alvo"] == "media_pos")]["id_linha"].unique().tolist()
    principais += sorted(tab[tab["pergunta"].str.startswith("CA")]["id_linha"].unique())
    for restr, xlab, nome in (("RM", "M̄ (magnitude relativa)", "H_rm.png"), ("SD", "M / u (suavidade)", "H_sd.png")):
        restr_h = "RM_hibrido" if restr == "RM" else None
        n = len(principais)
        cols = 4
        rows = math.ceil(n / cols)
        fig, axs = plt.subplots(rows, cols, figsize=(11, 2.6 * rows), squeeze=False)
        for ax, idl in zip(axs.ravel(), principais):
            s = tab[(tab["id_linha"] == idl) & (tab["alvo"] == "media_pos") & (tab["restricao"] == restr)]
            o = tab[(tab["id_linha"] == idl) & (tab["alvo"] == "media_pos") & (tab["restricao"] == "original")]
            x = s["parametro"].to_numpy(float)
            ax.axhline(0, color="#999", lw=0.8)
            ax.vlines(x, s["ic_inf"], s["ic_sup"], color="#2a78d6", lw=2)
            if restr_h:
                sh = tab[(tab["id_linha"] == idl) & (tab["alvo"] == "media_pos") & (tab["restricao"] == restr_h)]
                if len(sh):
                    dx = 0.06 * (x.max() if x.size and x.max() > 0 else 1)
                    ax.vlines(sh["parametro"].to_numpy(float) + dx, sh["ic_inf"], sh["ic_sup"], color="#1baf7a",
                              lw=2)
            if len(o):
                ax.errorbar([-0.08 * (x.max() if x.size and x.max() > 0 else 1)], o["estimativa"],
                            yerr=[[float(o["estimativa"].iloc[0] - o["ic_inf"].iloc[0])],
                                  [float(o["ic_sup"].iloc[0] - o["estimativa"].iloc[0])]],
                            fmt="o", color="#eb6834", ms=3, lw=1.5)
            ax.set_title(idl.replace("H-", ""), fontsize=8)
            ax.set_xlabel(xlab, fontsize=7)
            ax.tick_params(labelsize=7)
            for sp in ("top", "right"):
                ax.spines[sp].set_visible(False)
        for ax in axs.ravel()[n:]:
            ax.axis("off")
        fig.tight_layout()
        caminho = dir_fig / nome
        fig.savefig(caminho, dpi=150, metadata={"Software": None})
        plt.close(fig)
        figs.append({"arquivo": rotulo(caminho), "sha256": sha256(caminho)})
    return figs


# ---------------------------------------------------------------------------
# 4. Documento de resultados (57h), só a partir de output/
# ---------------------------------------------------------------------------

def _n(v, casas=2, sinal=True) -> str:
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return "—"
    s = f"{v:+,.{casas}f}" if sinal else f"{v:,.{casas}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".").replace("-", "−")


def _p(v) -> str:
    if v is None or not np.isfinite(v):
        return "—"
    return "< 0,001" if v < 0.001 else _n(v, 3, False)


def _ic(lo, hi, casas=2) -> str:
    return f"[{_n(lo, casas)}; {_n(hi, casas)}]"


def _tab(cab, linhas) -> str:
    return "\n".join(["| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)] +
                     ["| " + " | ".join(str(x) for x in l) + " |" for l in linhas])


def _rupt(tab, idl, alvo, restr) -> str:
    s = tab[(tab["id_linha"] == idl) & (tab["alvo"] == alvo) & (tab["restricao"] == restr)]
    if not len(s):
        return "—"
    r = s.iloc[0]
    v = _n(float(r["parametro"]), 2, False)
    if r["censura"] == "maior_ou_igual_ao_maximo":
        return f"≥ {v}"
    if r["censura"] == "ic_inclui_zero_em_0":
        return "0 (IC já inclui zero)"
    return v


def tabela_h(tab: pd.DataFrame, filtro) -> str:
    linhas = []
    for idl in tab[filtro]["id_linha"].unique():
        o = tab[(tab["id_linha"] == idl) & (tab["alvo"] == "media_pos") & (tab["restricao"] == "original")].iloc[0]
        d = tab[(tab["id_linha"] == idl) & (tab["alvo"] == "media_pos") & (tab["restricao"] == "descritivo_pre")].iloc[0]
        rm1 = tab[(tab["id_linha"] == idl) & (tab["alvo"] == "media_pos") & (tab["restricao"] == "RM")
                  & (np.isclose(tab["parametro"], 1.0))].iloc[0]
        casas = 2 if abs(o["estimativa"]) < 100 else 1
        h1 = tab[(tab["id_linha"] == idl) & (tab["alvo"] == "media_pos") & (tab["restricao"] == "RM_hibrido")
                 & (np.isclose(tab["parametro"], 1.0))]
        ic_h1 = _ic(h1["ic_inf"].iloc[0], h1["ic_sup"].iloc[0], casas) if len(h1) else "não calculado"
        linhas.append([o["descricao"], o["leitura"], f"{o['e_pre']} / {o['e_pos']}", _n(o["estimativa"], casas),
                       _ic(o["ic_inf"], o["ic_sup"], casas), _ic(rm1["ic_inf"], rm1["ic_sup"], casas), ic_h1,
                       _rupt(tab, idl, "media_pos", "RM_ruptura"), _rupt(tab, idl, "media_pos", "RM_hibrido_ruptura"),
                       _rupt(tab, idl, "theta0", "RM_ruptura"), _rupt(tab, idl, "theta0", "RM_hibrido_ruptura"),
                       _rupt(tab, idl, "media_pos", "SD_ruptura"), _n(d["M_absoluto"] / o["u"], 2, False)])
    return _tab(["Outcome", "Leitura", "e pré / pós", "Média do pós", "IC 95% (analítico)",
                 "Δ^RM(1), condicional", "Δ^RM(1), híbrido", "Ruptura M̄, média (cond.)", "Ruptura M̄, média (híbr.)",
                 "Ruptura M̄, θ(0) (cond.)", "Ruptura M̄, θ(0) (híbr.)", "Ruptura M/u, Δ^SD (média)",
                 "Maior |2ª dif.| do pré / u"], linhas)


def tabela_grade(tab: pd.DataFrame, idl: str, restr: str) -> str:
    s = tab[(tab["id_linha"] == idl) & (tab["alvo"] == "media_pos") & (tab["restricao"] == restr)]
    linhas = []
    for r in s.itertuples(index=False):
        casas = 2 if abs(r.estimativa) < 100 else 1
        idt = "vazio" if r.id_vazio is True else _ic(r.id_inf, r.id_sup, casas)
        linhas.append([_n(r.parametro, 2, False), _ic(r.ic_inf, r.ic_sup, casas), "sim" if r.exclui_zero else "não",
                       idt])
    return _tab(["M/u" if restr == "SD" else "M̄", "IC robusto 95%", "Exclui zero", "Conjunto identificado em β̂"],
                linhas)


def gerar_doc() -> str:
    tab = pd.read_csv(OUT / NOME_EST)
    res = json.loads((OUT / NOME_RESUMO).read_text(encoding="utf-8"))
    ca = pd.read_csv(CA_EST)
    car = json.loads(CA_RESUMO.read_text(encoding="utf-8"))
    linhas = []
    A = linhas.append
    A("# 57h. Resultados do protocolo 59: sensibilidade de Rambachan–Roth e comparação alternativa do P3/P4")
    A("")
    A(f"> **Data:** {DATA_EXECUCAO}.<br>")
    A("> **Protocolo:** [`59_protocolo_P3P4_sensibilidade_comparacao.md`](59_protocolo_P3P4_sensibilidade_comparacao.md), "
      "congelado e commitado sozinho antes de qualquer estimativa nova.<br>")
    A("> **Scripts:** `scripts/rdd_bolsa/35_comparacao_alternativa_P3P4.py` (parte B) e "
      "`scripts/rdd_bolsa/34_sensibilidade_honestdid.py` (parte A; gera este documento inteiro a partir de `output/`).<br>")
    A("> **Saídas:** `output/rdd_bolsa/H_*` e `CA_*`; toda linha tem `natureza_dos_dados = EMPIRICO`.<br>")
    A("> **Testes:** `tests/test_honestdid.py` e `tests/test_comparacao_alternativa_P3P4.py`.<br>")
    A("> **Estatuto:** `PROTOCOLO_59_POS_RESULTADO`. A parte A é `SENSIBILIDADE`: não muda nenhuma estimativa. "
      "Nada aqui tem fonte de exogeneidade validada.")
    A("")
    A("Este documento é gerado pelo script 34; não edite à mão.")
    A("")
    # --- leitura curta
    A("## 1. Resposta curta")
    A("")
    A(leitura_curta(tab, ca))
    A("")
    # --- parte A
    A("## 2. Parte A: sensibilidade de Rambachan–Roth")
    A("")
    A("Como ler: \"ruptura M̄ = x\" quer dizer que o IC robusto exclui zero enquanto a variação do viés entre meses "
      "consecutivos do pós não passa de x vezes a maior variação vista no pré (M̄ = 1: do mesmo tamanho). Ruptura 0 = "
      "o IC já inclui zero sem nenhuma violação além da do pré. Δ^SD: limite M na segunda diferença do viés, em "
      "múltiplos de u (EP analítico de θ(0)). A sensibilidade não transforma associação em efeito.")
    A("")
    A("Método: Δ^RM pelo teste condicional de Andrews, Roth e Pakes (congelado no protocolo) e, nas linhas "
      "principais e do CA, também pelo híbrido condicional–LF (adendo datado do protocolo 59; padrão do pacote "
      "HonestDiD); Δ^SD pelo FLCI. Implementação própria em scipy (`honestdid_lib.py`), validada em casos sintéticos. "
      "Σ = covariância analítica das funções de influência; o IC \"analítico\" da tabela é a referência com essa Σ "
      "e pode diferir um pouco do IC bootstrap dos docs 57c e 57d.")
    A("")
    A("Por que o IC de Δ^RM pode ser largo já em M̄ = 0: em M̄ = 0 os passos do pós são forçados a zero, então a "
      "largura não vem de repartir o desvio em passos mensais. Ela vem do teste de ARP, que é do tipo sup-t sobre "
      "muitos momentos (um por diferença mensal do pós: 10 no P3, 6 a 7 no P4): válido, mas pouco potente para a "
      "média do pós quando os θ(e) mensais são ruidosos (nas horas totais do P4, o IC em M̄ = 0 tem cerca de 3 vezes "
      "a largura do convencional; auditoria 30, A1). O híbrido não muda isso nestes dados (as duas colunas quase "
      "coincidem). Por isso a ruptura 0 do P3 reflete em parte essa perda de potência; a fragilidade do P3 se "
      "sustenta pelo FLCI de Δ^SD (M/u = 0,02), que não depende desse teste e é a leitura mais informativa quando o "
      "Δ^RM sai largo.")
    A("")
    A("### 2.1 P3 (doc 57c)")
    A("")
    A(tabela_h(tab, tab["pergunta"] == "P3"))
    A("")
    A("### 2.2 P4 (doc 57d, T4.1b, regra D1)")
    A("")
    A(tabela_h(tab, tab["pergunta"] == "P4"))
    A("")
    A("### 2.3 Comparação alternativa (parte B)")
    A("")
    if (tab["pergunta"].str.startswith("CA")).any():
        A(tabela_h(tab, tab["pergunta"].str.startswith("CA")))
    else:
        A("Sem linhas: a parte B não gravou estudos de evento primários.")
    A("")
    A("### 2.4 Grades das linhas principais (média do pós)")
    A("")
    for idl in tab[tab["leitura"] == "principal"]["id_linha"].unique():
        d = tab[tab["id_linha"] == idl].iloc[0]["descricao"]
        A(f"**{d}** (`{idl}`), Δ^RM, teste condicional (congelado):")
        A("")
        A(tabela_grade(tab, idl, "RM"))
        A("")
        if ((tab["id_linha"] == idl) & (tab["restricao"] == "RM_hibrido")).any():
            A("Δ^RM, híbrido condicional–LF (adendo):")
            A("")
            A(tabela_grade(tab, idl, "RM_hibrido"))
            A("")
        A("Δ^SD:")
        A("")
        A(tabela_grade(tab, idl, "SD"))
        A("")
    A("![Δ^RM: IC robusto por M̄](../../output/rdd_bolsa/H_figuras/H_rm.png)")
    A("")
    A("**Como ler.** Cada painel é um outcome principal; os traços são o IC robusto de 95% da média do pós para cada "
      "M̄ (azul: teste condicional congelado; verde: híbrido do adendo), e o ponto laranja à esquerda é a estimativa "
      "original. Traço que cruza o zero: a conclusão não aguenta aquela violação.")
    A("")
    A("![Δ^SD: FLCI por M/u](../../output/rdd_bolsa/H_figuras/H_sd.png)")
    A("")
    A("**Como ler.** Mesma leitura, com o limite na curvatura do viés (M em múltiplos de u).")
    A("")
    # --- parte B
    A("## 3. Parte B: grupo de comparação alternativo")
    A("")
    A(secao_ca(ca, car))
    A("")
    A("## 4. Desvios e decisões")
    A("")
    for dv in res.get("desvios", []) + car.get("desvios", []):
        A(f"- **{dv['item']}** ({dv['data']}). {dv['descricao']}")
    A("")
    A("## 5. Limitações")
    A("")
    A("- Parte A: Σ é a covariância analítica; o teste condicional puro pode ser menos potente que o híbrido do "
      "pacote; a janela do pré do P3 é −12..−2 (custo da união de poliedros), não a do Wald do doc 57c (−24..−2).")
    A("- P3-CA: a priorização da SGTES não é sorteio (doc 57e); o pedido do ciclo 3 é decisão do gestor em 2026, "
      "depois do início dos ciclos 1–2; cursos sem controle ficam fora.")
    A("- P4-CA: poucas células com os dois lados; desequilíbrio de distância e ligação do P6; vínculo cadastrado não "
      "é presença; t₀ comum por ciclo ignora diferenças de início dentro do ciclo. Com 27 células e 11 coeficientes "
      "do pré, o p qui-quadrado do Wald (coluna p_qui2 de CA_estimativas.csv) pode divergir do p por permutação, "
      "que é a regra do protocolo; os dois estão gravados.")
    A("")
    A("## 6. Entradas")
    A("")
    A(_tab(["Arquivo", "Papel", "SHA-256 (12)"], [[e["caminho"], e["papel"], e["sha256"][:12]]
                                                   for e in res["entradas"] + car["entradas"]]))
    A("")
    A("## 7. Reprodução")
    A("")
    A("```bash\npython3 scripts/rdd_bolsa/35_comparacao_alternativa_P3P4.py --etapa estimar   # cache privado\n"
      "python3 scripts/rdd_bolsa/34_sensibilidade_honestdid.py --etapa estimar\n"
      "python3 -m pytest tests/test_honestdid.py tests/test_comparacao_alternativa_P3P4.py\n```")
    A("")
    return "\n".join(linhas)


def leitura_curta(tab: pd.DataFrame, ca: pd.DataFrame) -> str:
    frases = []
    for idl in tab[tab["leitura"] == "principal"]["id_linha"].unique():
        o = tab[(tab["id_linha"] == idl) & (tab["alvo"] == "media_pos") & (tab["restricao"] == "original")].iloc[0]
        frases.append(f"{o['descricao']}: média do pós {_n(o['estimativa'])}; ruptura de Δ^RM em M̄ = "
                      f"{_rupt(tab, idl, 'media_pos', 'RM_ruptura')} pelo teste condicional e "
                      f"{_rupt(tab, idl, 'media_pos', 'RM_hibrido_ruptura')} pelo híbrido "
                      f"(Δ^SD: M/u = {_rupt(tab, idl, 'media_pos', 'SD_ruptura')})")
    txt = "**Parte A (sensibilidade).** " + "; ".join(frases) + ". "
    princ = tab[tab["leitura"] == "principal"]["id_linha"].unique()
    rob_c = [idl for idl in princ if _num_rupt(tab, idl, "RM_ruptura") >= 1.0]
    rob_h = [idl for idl in princ if _num_rupt(tab, idl, "RM_hibrido_ruptura") >= 1.0]
    txt += ("Com M̄ = 1 (violações do pós do tamanho das do pré), o IC robusto da média do pós exclui zero em: "
            + (", ".join(rob_c) if rob_c else "nenhuma linha principal") + " (condicional); "
            + (", ".join(rob_h) if rob_h else "nenhuma linha principal") + " (híbrido). ")
    prim = ca[(ca["familia"] == "holm_CA")]
    partes = []
    for r in prim.itertuples(index=False):
        if r.status != "EXECUTADO":
            partes.append(f"{r.id_linha}: não executado ({r.nota})")
            continue
        pre = ca[(ca["id_linha"] == r.id_linha) & (ca["outcome"] == r.outcome) & (ca["estatistica"] == "wald_pre")]
        ppre = float(pre["p_valor"].iloc[0]) if len(pre) else np.nan
        partes.append(f"{r.id_linha} {r.descricao_outcome}: {_n(r.valor)} {_ic(r.ic95_inf, r.ic95_sup)}, p = "
                      f"{_p(r.p_valor)}, p Holm = {_p(r.p_holm)}, pré p = {_p(ppre)} "
                      f"({'passa' if r.passa_pre else 'não passa'})")
    txt += "**Parte B (comparação alternativa).** " + "; ".join(partes) + ". "
    ok = prim[(prim["p_holm"] < 0.05) & (prim["passa_pre"] == True)]  # noqa: E712
    rot = {"P3": "H-CA-P3-", "P4": "H-CA-P4-"}
    completos = [r.id_linha + " " + r.outcome for r in ok.itertuples(index=False)
                 if min(_num_rupt(tab, rot[r.pergunta] + r.outcome, "RM_ruptura"),
                        _num_rupt(tab, rot[r.pergunta] + r.outcome, "RM_hibrido_ruptura")) >= 1.0]
    txt += (f"Primárias que rejeitam zero depois do Holm com pré que passa: {len(ok)} de {len(prim)}"
            + (f" ({', '.join(r.id_linha + ' ' + r.outcome for r in ok.itertuples(index=False))})" if len(ok) else "")
            + ". Com a exigência adicional do §6 do protocolo (ruptura de Δ^RM ≥ 1 na média do pós): "
            + (", ".join(completos) if completos else "nenhuma") + ". "
            "As horas no município da 1ª opção são em parte mecânicas (ser alocado cria o vínculo cadastrado no "
            "município da vaga, como o Y1 do P6), e vínculo cadastrado não é presença. Nada aqui é efeito da bolsa nem "
            "da participação no PMM-E.")
    return txt


def _num_rupt(tab, idl, restr: str = "RM_ruptura") -> float:
    s = tab[(tab["id_linha"] == idl) & (tab["alvo"] == "media_pos") & (tab["restricao"] == restr)]
    return float(s["parametro"].iloc[0]) if len(s) else 0.0


def secao_ca(ca: pd.DataFrame, car: dict) -> str:
    L = []
    A = L.append
    am3 = car["amostras"]["P3"]
    A("### 3.1 P3-CA: chegada contra pares que pediram o curso no ciclo 3 e não foram priorizados")
    A("")
    A("O contraste é a priorização entre quem pediu, sob tendências paralelas entre os grupos; não é efeito da "
      "participação no PMM-E nem da bolsa. Nenhum outcome do ciclo 3 é lido (série até 202605).")
    A("")
    sp = am3["por_especificacao"]
    A(_tab(["Especificação", "Cursos", "Cursos fora (tratados / controles)", "Tratados", "Controles", "Municípios"],
           [[k, ", ".join(str(c) for c in v["cursos"]),
             "; ".join(f"{c}: {x['tratados']}/{x['controles']}" for c, x in v["cursos_fora"].items()) or "—",
             v["tratados"], v["controles"], v["municipios"]] for k, v in sp.items()]))
    A("")
    A(tabela_ca(ca[ca["pergunta"] == "P3"]))
    A("")
    A("![P3-CA: estudo de evento](../../output/rdd_bolsa/CA_figuras/CA_P3_evento.png)")
    A("")
    A("**Como ler.** Cada ponto compara, mês a mês desde a chegada, a produção típica do curso nos pares que receberam "
      "o especialista com a dos pares que pediram o curso no ciclo 3 e não foram priorizados; à esquerda do zero os "
      "pontos deveriam ficar perto de zero.")
    A("")
    A("### 3.2 P4-CA: alocado contra não alocado perto da nota de corte")
    A("")
    am4 = car["amostras"]["P4"]
    if am4.get("status") == "NAO_EXECUTADO":
        A(f"Não executado: {am4.get('motivo')}.")
        return "\n".join(L)
    A("O contraste é ser alocado na 1ª opção perto do corte, em diferenças (mês do evento − mês de referência), sob "
      "tendências paralelas locais; não é efeito da bolsa. Horas são cadastradas, não trabalhadas.")
    A("")
    A(_tab(["Especificação", "Candidatos", "Alocados", "Não alocados", "Células", "Por ciclo"],
           [[k, v["candidatos"], v["alocados"], v["nao_alocados"], v["celulas"],
             ", ".join(f"ciclo {c}: {n}" for c, n in v["por_ciclo"].items())]
            for k, v in am4["por_especificacao"].items()]))
    A("")
    A(tabela_ca(ca[ca["pergunta"] == "P4"]))
    A("")
    A("![P4-CA: estudo de evento](../../output/rdd_bolsa/CA_figuras/CA_P4_evento.png)")
    A("")
    A("**Como ler.** Cada ponto é a diferença, entre quem passou e quem não passou por 1 ou 2 pontos, na variação das "
      "horas cadastradas desde o mês anterior ao início do ciclo; à esquerda do zero os pontos deveriam ficar perto "
      "de zero.")
    A("")
    A("Conferências do painel refeito do cache privado: reproduz o a16 e o G1 versionados e as médias de "
      "seguimento e as horas pré de `P6_amostra.parquet` (diferenças por coluna: todas 0).")
    return "\n".join(L)


def tabela_ca(ca: pd.DataFrame) -> str:
    linhas = []
    pos = ca[ca["estatistica"].isin(["att_pos_medio", "efeito_pos_medio"])]
    for r in pos.itertuples(index=False):
        if r.status != "EXECUTADO":
            linhas.append([r.id_linha, r.descricao_outcome if isinstance(r.descricao_outcome, str) else r.outcome,
                           "—", "—", "—", "—", "—", "—", "—", r.status])
            continue
        pre = ca[(ca["id_linha"] == r.id_linha) & (ca["outcome"] == r.outcome) & (ca["estatistica"] == "wald_pre")]
        ppre = float(pre["p_valor"].iloc[0]) if len(pre) else np.nan
        casas = 2 if abs(r.valor) < 100 else 1
        mult = (f"Holm {_p(r.p_holm)}" if r.familia == "holm_CA" else
                (f"BKY q {_p(r.q_bky)}" if r.familia == "bky_P4CA_sec" else "—"))
        linhas.append([r.id_linha, r.descricao_outcome, _n(r.valor, casas), _ic(r.ic95_inf, r.ic95_sup, casas),
                       _p(r.p_valor), mult, _n(r.mde, casas, False), _p(ppre),
                       "passa" if r.passa_pre else "**não passa**", (r.nota if isinstance(r.nota, str) else "")])
    return _tab(["Linha", "Outcome", "Média do pós", "IC 95%", "p", "Multiplicidade", "MDE", "Pré: p",
                 "Pré", "Ressalva"], linhas)


def atualizar_doc() -> None:
    DOC.write_text(gerar_doc(), encoding="utf-8")


# ---------------------------------------------------------------------------
# 5. Execução
# ---------------------------------------------------------------------------

DESVIOS: list[dict] = [
    {"data": DATA_ADENDO, "tipo": "adendo", "item": "híbrido condicional–LF (parte A)",
     "descricao": "o teste condicional puro congelado no §2.4 fica muito conservador quando outro momento está perto "
                  "de ativo (caso sintético em tests/test_honestdid.py; IC em M̄ = 0 mais largo que em M̄ = 0,25 na "
                  "primeira linha real). O condicional continua em todas as linhas; o híbrido de ARP (padrão do "
                  "HonestDiD) é acrescentado nas linhas principais e no CA. Adendo datado no protocolo 59."},
    {"data": DATA_ADENDO, "tipo": "esclarecimento", "item": "covariância",
     "descricao": "Σ analítica das funções de influência; o EP analítico recalculado bate com a coluna ep_analitico "
                  "do K_X_estudo_evento.csv (diferença ≤ 1e−6) e os θ(e) com o versionado (≤ 1e−8)."},
]


def entradas() -> list[dict]:
    lista = [(PROTOCOLO_MD, "protocolo congelado"), (KX_EVENTO, "conferência dos θ(e) do P3 (doc 57c)"),
             (P4_EST, "conferência dos θ(e) do P4 (doc 57d)"), (CA_EST, "primárias da parte B"),
             (CA_EVENTO, "θ(e) da parte B"), (CA_COV, "covariância da parte B"),
             (ROOT / "output" / "aquisicao" / "sia_forma_curso" / "painel_sia_municipio_mes_forma_curso.parquet",
              "K_esp (a17)"),
             (ROOT / "output" / "aquisicao" / "sih_residencia" / "painel_sih_residencia_municipio_mes_grupo.parquet",
              "K2r, K2r_tot (a15)"),
             (ROOT / "output" / "aquisicao" / "sia" / "painel_sia_municipio_mes_subgrupo_cbo.parquet", "K1_reg (a12)"),
             (ROOT / "output" / "aquisicao" / "sih" / "painel_sih_municipio_mes_grupo.parquet", "K2_reg (a13)"),
             (ROOT / "output" / "aquisicao" / "cnes_profissional" / "painel_vinculo_mes.parquet", "P4 (a16)"),
             (ROOT / "output" / "aquisicao" / "a08_ivs_2010_oficial_municipio.csv", "universo U")]
    return [{"caminho": rotulo(p), "sha256": sha256(p), "papel": papel} for p, papel in lista if Path(p).exists()]


def executar() -> int:
    if not CA_EST.exists():
        raise SystemExit("CA_estimativas.csv ausente: rode o script 35 antes (protocolo 59, §7)")
    p3, conf3 = estudos_p3()
    p4, conf4 = estudos_p4()
    ca = estudos_ca()
    todos = p3 + p4 + ca
    tk = tarefas(todos)
    # as tarefas do híbrido são as mais longas: começam primeiro (a ordem não muda o resultado)
    ordem = sorted(range(len(tk)), key=lambda i: (tk[i][2] != "hibrido", i))
    with concurrent.futures.ProcessPoolExecutor(max_workers=WORKERS) as ex:
        res_o = list(ex.map(analisar, [tk[i] for i in ordem]))
    res = [None] * len(tk)
    for i, r in zip(ordem, res_o):
        res[i] = r
    tab = pd.DataFrame([l for r in res for l in r])
    for c in COLUNAS:
        if c not in tab:
            tab[c] = np.nan
    tab = tab[COLUNAS]
    coef = pd.DataFrame([l for e in todos for l in coeficientes(e)])
    OUT.mkdir(parents=True, exist_ok=True)
    tab.to_csv(OUT / NOME_EST, index=False, float_format="%.10g")
    coef.to_csv(OUT / NOME_COEF, index=False, float_format="%.12g")
    figs = gerar_figuras(tab, OUT / DIR_FIG)
    resumo = {
        "etapa": "H_sensibilidade_rambachan_roth", "natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO,
        "rotulo": ROTULO, "gerador": rotulo(Path(__file__)), "data_execucao": DATA_EXECUCAO,
        "protocolo": {"texto": rotulo(PROTOCOLO_MD), "sha256_texto": sha256(PROTOCOLO_MD), "secao": "§2", "sha256_texto_congelado": "f039e3f573e8acd504a7b2e9a6371428439a09ae05218d244956c2e434b8d4ed", "commit_congelamento": "1cc4d68", "nota_hash": "sha256_texto é o arquivo atual, já com o adendo datado; sha256_texto_congelado é o texto do commit de congelamento"},
        "metodo": {"RM": "teste condicional ARP (Andrews, Roth e Pakes, 2023), união dos poliedros, envelope",
                   "RM_hibrido": "híbrido condicional–LF de ARP, κ = α/10, 1.000 simulações (adendo de 25/10/2026; "
                                 "linhas principais e CA)",
                   "SD": "FLCI (Armstrong e Kolesár, 2018)", "alpha": ALPHA, "grade_RM": GRADE_RM,
                   "grade_SD_em_u": GRADE_SD, "ruptura": {"RM": [0, MAX_RM, TOL_RM], "SD_em_u": [0, MAX_SD, TOL_SD]},
                   "covariancia": "analítica das funções de influência (P3: cluster município; P4: médico; CA: script 35)",
                   "biblioteca": rotulo(DIR_RDD / "honestdid_lib.py"),
                   "referencia": "Rambachan, A.; Roth, J. (2023). A more credible approach to parallel trends. "
                                 "Review of Economic Studies 90(5)."},
        "conferencias": {"P3": conf3, "P4": conf4},
        "linhas": int(tab["id_linha"].nunique()),
        "saidas": {rotulo(OUT / n): sha256(OUT / n) for n in (NOME_EST, NOME_COEF)},
        "figuras": figs,
        "entradas": entradas(),
        "desvios": DESVIOS,
        "integridade": "não muda estimativa pontual; nenhum dado novo; o arquivo local de IVS não é lido",
    }
    gravar_json(OUT / NOME_RESUMO, resumo)
    atualizar_doc()
    print(f"H: {len(tab)} linhas, {tab['id_linha'].nunique()} estudos de evento")
    return 0


def verificar() -> int:
    res = OUT / NOME_RESUMO
    if not res.exists():
        raise SystemExit(f"{rotulo(res)} ausente; rode --etapa estimar")
    r = json.loads(res.read_text(encoding="utf-8"))
    ruins = [k for k, h in r["saidas"].items() if not (ROOT / k).exists() or sha256(ROOT / k) != h]
    ruins += [f["arquivo"] for f in r["figuras"] if sha256(ROOT / f["arquivo"]) != f["sha256"]]
    if ruins:
        raise SystemExit(f"verificar: saídas do H não conferem: {ruins}")
    if DOC.read_text(encoding="utf-8") != gerar_doc():
        raise SystemExit("verificar: o doc 57h difere do gerado a partir de output/")
    print("H: saídas e doc 57h conferem")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--etapa", choices=("verificar", "estimar", "doc"), default="verificar")
    a = ap.parse_args(argv)
    if a.etapa == "estimar":
        return executar()
    if a.etapa == "doc":
        atualizar_doc()
        return 0
    return verificar()


if __name__ == "__main__":
    sys.exit(main())
