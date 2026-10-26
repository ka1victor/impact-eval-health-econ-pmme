"""Protocolo 59, parte B: grupo de comparação alternativo do P3 (P3-CA) e do P4 (P4-CA).

Protocolo congelado: `docs/06_execucao/59_protocolo_P3P4_sensibilidade_comparacao.md` (25/10/2026, commitado
sozinho antes de qualquer estimativa). Estatuto de toda linha: `PROTOCOLO_59_POS_RESULTADO`;
`natureza_dos_dados = EMPIRICO`.

P3-CA (§3)
----------
ATT da chegada do 1º especialista no par município × curso sobre K_esp (o outcome do 12.2, doc 57c), com
controles = pares em U que pediram o curso na adesão do ciclo 3, sem nenhuma linha priorizada do curso no
município e sem chegada da lista nominal no par. Callaway–Sant'Anna do 12.2 (`att_gt_geral` do script 27), só o
grupo alternativo como controle, controles do mesmo curso, base g − 1, cluster no município, Mammen B = 9.999,
semente 20261019. Cursos sem tratado ou com menos de 2 controles ficam fora e são contados. S1: controles = todos
os pedidos do ciclo 3 sem chegada; S2: por curso.

P4-CA (§4)
----------
Alocado contra não alocado perto da nota de corte (universo do P6), em diferenças: para cada e, MQO de
ΔY = Y(t₀+e) − Y(t₀−1) em D com efeito fixo de célula; EP agrupado por célula (G/(G − 1)); p da primária por
permutação de D dentro da célula (999, semente 20261019); pré: Wald de θ(e) = 0, e = −12..−2, com p por
permutação. t₀ = 1º mês de início da lista nominal no ciclo (202509, 202603). O painel mensal dos candidatos é
refeito em memória a partir do cache privado do a16 e do dicionário do G1, com as funções e as conferências do
script 30; o script confere que ele reproduz os agregados versionados do P6 (`P6_amostra.parquet`).

Dados pessoais: código do profissional, nome e CPF ficam só em memória e no cache privado ignorado pelo Git. As
saídas têm só estatísticas por e, por grupo e por especificação.

Uso
---
    python3 scripts/rdd_bolsa/35_comparacao_alternativa_P3P4.py --etapa estimar   # precisa do cache privado
    python3 scripts/rdd_bolsa/35_comparacao_alternativa_P3P4.py                   # verificar (padrão)
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


# ---------------------------------------------------------------------------
# Parâmetros fixados pelo protocolo 59
# ---------------------------------------------------------------------------

OUT = ROOT / "output" / "rdd_bolsa"
PROTOCOLO_MD = ROOT / "docs" / "06_execucao" / "59_protocolo_P3P4_sensibilidade_comparacao.md"
NOME_EST = "CA_estimativas.csv"
NOME_EVENTO = "CA_estudo_evento.csv"
NOME_COV = "CA_covariancia.csv"
NOME_RESUMO = "CA_resumo.json"
DIR_FIG = "CA_figuras"
P6_AMOSTRA = OUT / "P6_amostra.parquet"
NOMINAL = ROOT / "data" / "pmm_especialistas_nominal.csv"

DATA_EXECUCAO = "2026-10-25"
ESTATUTO = "PROTOCOLO_59_POS_RESULTADO"
NATUREZA = "EMPIRICO"
SEMENTE = 20261019
B_PERM = 999
LIMITE_EXCLUSIVO = "202609"
# P3-CA
E3_MIN, E3_MAX = -24, 9
# P4-CA
E4_MIN, E4_MAX = -12, 5
T0 = {1: "202509", 2: "202603"}
JANELA_PRINCIPAL = (-2, -1, 1, 2)
REGRA_PRINCIPAL, REGRA_NOME = "g1_cpf_nome", "g1_so_nome"
OUT4_PRIM = [("horas_totais", "horas totais", "h/sem"),
             ("horas_mun_1a", "horas no município da 1ª opção", "h/sem"),
             ("horas_fora_1a", "horas fora do município da 1ª opção", "h/sem")]
OUT4_SEC = [("horas_sus", "horas SUS", "h/sem"),
            ("n_municipios", "número de municípios com vínculo", "municípios"),
            ("vinculo_mun_1a", "tem vínculo no município da 1ª opção (quase mecânico)", "fração"),
            ("n_vinculos", "número de vínculos", "vínculos")]
ROTULO4 = {o: r for o, r, _ in OUT4_PRIM + OUT4_SEC}
UNID4 = {o: u for o, _, u in OUT4_PRIM + OUT4_SEC}
CONTRASTE_P3 = ("ATT da chegada contra pares que pediram o curso no ciclo 3 e não foram priorizados, sob tendências "
                "paralelas entre os dois grupos; priorização entre quem pediu, não participação no PMM-E nem bolsa")
CONTRASTE_P4 = ("efeito de ser alocado na 1ª opção perto da nota de corte sobre a trajetória cadastrada, em "
                "diferenças, sob tendências paralelas locais; não é efeito da bolsa nem do PMM-E no município")
COLUNAS_PROIBIDAS = ("nome", "cpf", "cns", "crm", "co_profissional_sus", "id_prof", "chave", "id_candidato")

COLUNAS_EST = ["natureza_dos_dados", "estatuto", "pergunta", "id_linha", "especificacao", "amostra", "outcome",
               "descricao_outcome", "unidade", "estatistica", "valor", "ep", "ic95_inf", "ic95_sup", "p_valor",
               "tipo_p", "p_qui2", "gl", "mde", "familia", "p_holm", "q_bky", "passa_pre", "n_tratados",
               "n_controles", "n_unidades", "n_clusters", "n_coortes", "e_min", "e_max", "status", "contraste",
               "nota"]
COLUNAS_EVENTO = ["natureza_dos_dados", "estatuto", "pergunta", "id_linha", "especificacao", "amostra", "outcome",
                  "e", "theta", "ep", "ic95_inf", "ic95_sup", "n_tratados", "n_controles", "referencia", "nota"]


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


def nova_linha(**kw) -> dict:
    base = {c: np.nan for c in COLUNAS_EST}
    base.update({"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "status": "EXECUTADO", "nota": ""})
    base.update(kw)
    return base


def p_normal(z: float) -> float:
    return float(2 * stats.norm.sf(abs(z))) if np.isfinite(z) else np.nan


def holm(p: np.ndarray) -> np.ndarray:
    p = np.asarray(p, float)
    o = np.argsort(p)
    m = p.size
    adj = np.empty(m)
    run = 0.0
    for k, i in enumerate(o):
        run = max(run, (m - k) * p[i])
        adj[i] = min(run, 1.0)
    return adj


# ---------------------------------------------------------------------------
# 1. Estimador do P4-CA (funções puras; testadas com dados sintéticos em memória)
# ---------------------------------------------------------------------------

def _centrar(x: np.ndarray, idx: np.ndarray, G: int) -> np.ndarray:
    s = np.zeros(G)
    n = np.zeros(G)
    np.add.at(s, idx, x)
    np.add.at(n, idx, 1.0)
    return x - (s / np.where(n > 0, n, 1.0))[idx]


def did_celula(dY: np.ndarray, D: np.ndarray, cel: np.ndarray, W: np.ndarray | None = None,
               contar: bool = True) -> dict:
    """θ(e) por MQO de ΔY(e) em D (e covariáveis W) com efeito fixo de célula, para cada coluna e de dY.

    dY: n × E (NaN = fora naquele e); D: n (0/1); cel: rótulo da célula; W: n × k covariáveis adicionais.
    Devolve θ (E), a matriz de funções de influência por célula (G × E; θ̂ − θ ≈ soma das linhas) e contagens.
    Só células com os dois lados identificam; as demais não mudam a estimativa."""
    n, E = dY.shape
    _, idx = np.unique(np.asarray(cel).astype(str), return_inverse=True)
    G = int(idx.max()) + 1 if n else 0
    theta = np.full(E, np.nan)
    IFg = np.zeros((G, E))
    n1 = np.zeros(E, dtype=int)
    n0 = np.zeros(E, dtype=int)
    for j in range(E):
        ok = np.isfinite(dY[:, j])
        if ok.sum() < 3:
            IFg[:, j] = np.nan
            continue
        ii = idx[ok]
        X = D[ok].astype(float)[:, None] if W is None else np.column_stack([D[ok].astype(float), W[ok]])
        Xt = np.column_stack([_centrar(X[:, c], ii, G) for c in range(X.shape[1])])
        yt = _centrar(dY[ok, j], ii, G)
        XtX = Xt.T @ Xt
        if abs(XtX[0, 0]) < 1e-12 or np.linalg.matrix_rank(XtX) < XtX.shape[0]:
            IFg[:, j] = np.nan
            continue
        inv = np.linalg.inv(XtX)
        b = inv @ (Xt.T @ yt)
        res = yt - Xt @ b
        psi = (Xt * res[:, None]) @ inv[:, 0]
        np.add.at(IFg[:, j], ii, psi)
        theta[j] = b[0]
        if not contar:
            continue
        # contagem só nas células com os dois lados
        dmin = pd.Series(D[ok]).groupby(ii).transform("min").to_numpy()
        dmax = pd.Series(D[ok]).groupby(ii).transform("max").to_numpy()
        dois = (dmin == 0) & (dmax == 1)
        n1[j] = int(((D[ok] == 1) & dois).sum())
        n0[j] = int(((D[ok] == 0) & dois).sum())
    return {"theta": theta, "IFg": IFg, "G": G, "n1": n1, "n0": n0}


def cov_cluster(IFg: np.ndarray) -> np.ndarray:
    G = IFg.shape[0]
    fator = G / (G - 1) if G > 1 else np.nan
    X = np.nan_to_num(IFg)
    return fator * (X.T @ X)


def wald(theta: np.ndarray, V: np.ndarray) -> tuple[float, int]:
    ok = np.isfinite(theta)
    th = theta[ok]
    Vs = V[np.ix_(ok, ok)]
    gl = int(np.linalg.matrix_rank(Vs))
    return float(th @ np.linalg.pinv(Vs) @ th), gl


def estimar_p4ca(dY: np.ndarray, D: np.ndarray, cel: np.ndarray, es: np.ndarray, *, W: np.ndarray | None = None,
                 b_perm: int = B_PERM, semente: int = SEMENTE) -> dict:
    """θ(e), média do pós, Wald do pré e p por permutação de D dentro da célula (mesmos sorteios para tudo)."""
    pre = es <= -2
    pos = es >= 0
    r = did_celula(dY, D, cel, W)
    V = cov_cluster(r["IFg"])
    th = r["theta"]
    ep = np.sqrt(np.clip(np.diag(V), 0, None))
    l = pos & np.isfinite(th)
    media = float(th[l].mean()) if l.any() else np.nan
    w = l.astype(float) / max(l.sum(), 1)
    ep_media = float(math.sqrt(max(w @ V @ w, 0)))
    wpre, gl = wald(np.where(pre, th, np.nan), V)
    p_qui2 = float(stats.chi2.sf(wpre, gl)) if gl else np.nan
    _, idx = np.unique(np.asarray(cel).astype(str), return_inverse=True)
    grupos = [np.flatnonzero(idx == g) for g in range(int(idx.max()) + 1)]
    rng = np.random.default_rng(semente)
    Db = D.copy()
    c_med, c_wald = 0, 0
    for _ in range(b_perm):
        for gi in grupos:
            Db[gi] = D[gi][rng.permutation(gi.size)]
        rb = did_celula(dY, Db, cel, W, contar=False)
        tb = rb["theta"]
        mb = float(tb[l].mean()) if l.any() else np.nan
        c_med += abs(mb) >= abs(media) - 1e-12
        wb, _ = wald(np.where(pre, tb, np.nan), cov_cluster(rb["IFg"]))
        c_wald += wb >= wpre - 1e-9
    return {"theta": th, "ep": ep, "V": V, "media": media, "ep_media": ep_media,
            "p_perm_media": (1 + c_med) / (b_perm + 1), "wald_pre": wpre, "gl_pre": gl, "p_qui2_pre": p_qui2,
            "p_perm_pre": (1 + c_wald) / (b_perm + 1), "G": r["G"], "n1": r["n1"], "n0": r["n0"],
            "IFg": r["IFg"]}


# ---------------------------------------------------------------------------
# 2. P3-CA
# ---------------------------------------------------------------------------

def modulos_p3():
    k27 = _importar(DIR_RDD / "27_producao_extensoes.py", "k27_para_ca")
    m12 = _importar(DIR_RDD / "12_construir_outcomes_funil.py", "m12_para_ca")
    return k27, m12


def ler_pedidos_ciclo3(m12, k27, cursos: list[int]) -> tuple[pd.DataFrame, dict]:
    """Pares município × curso com linha na adesão do ciclo 3; priorizado = alguma linha com priorizadas > 0."""
    ad, diag = m12.ler_adesao()
    ad = ad.copy()
    ad["co_ibge"] = k27._ibge6(ad["co_ibge"].astype(str))
    ad = ad[ad["cod_curso"].isin(cursos)]
    if ((ad["priorizadas"] > 0) & (ad["nao_priorizadas"] > 0)).any():
        raise FalhaValidacao("adesão com linha parcialmente priorizada (a regra tudo ou nada não vale)")
    pp = ad.groupby(["co_ibge", "cod_curso"]).agg(priorizado=("priorizadas", lambda s: bool((s > 0).any())),
                                                  linhas=("priorizadas", "size")).reset_index()
    return pp, {"linhas_adesao": int(diag.get("linhas_aba_principal", len(ad))),
                "pares_pedidos_cursos_especificos": int(len(pp)),
                "pares_priorizados": int(pp["priorizado"].sum()),
                "pares_nao_priorizados": int((~pp["priorizado"]).sum())}


def chegadas_pares(k27) -> set[tuple[str, int]]:
    nom = pd.read_csv(NOMINAL, usecols=["co_ibge", "curso", "dt_inicio_atividade"], dtype=str)
    nom["co_ibge"] = k27._ibge6(nom["co_ibge"])
    nom["cod_curso"] = nom["curso"].str[:2].astype(int)
    if (pd.to_datetime(nom["dt_inicio_atividade"], errors="coerce").dt.strftime("%Y%m") >= LIMITE_EXCLUSIVO).any():
        raise FalhaValidacao("lista nominal com início >= 202609")
    return set(zip(nom["co_ibge"], nom["cod_curso"]))


def cs_com_if(k27, Y, G, coortes, clus, grupo, controles="nunca") -> dict:
    """CS do 12.2 (inferência por bootstrap do script 27) e a covariância analítica das funções de influência."""
    r = k27.estimar_cs_cluster(Y, G, coortes, clus, grupo=grupo, controles=controles, e_min=E3_MIN, e_max=E3_MAX)
    tab, IF, chave = k27.att_gt_geral(Y, G, coortes, grupo=grupo, controles=controles, e_min=E3_MIN, e_max=E3_MAX)
    ev, IFe = k27.D2M.agregar_evento(tab, IF, chave, e_min=E3_MIN, e_max=E3_MAX)
    IFc, M = k27.somar_cluster(IFe, clus)
    th = ev["theta"].to_numpy(float)
    if not np.allclose(th, r["evento"]["theta"].to_numpy(float), equal_nan=True, atol=1e-12):
        raise FalhaValidacao("θ(e) da covariância difere do estimar_cs_cluster")
    ok = np.isfinite(IFc).all(axis=0)
    V = np.full((th.size, th.size), np.nan)
    V[np.ix_(ok, ok)] = IFc[:, ok].T @ IFc[:, ok] / M ** 2
    r["V"] = V
    return r


def p3ca() -> tuple[list[dict], list[dict], list[dict], dict]:
    k27, m12 = modulos_p3()
    K1M, D2M = k27.K1M, k27.D2M
    base, _ = K1M.ler_universo()
    universo = base.index
    pop = base["populacao_2022"].astype(float)
    cursos, tip, conj, _ = k27.ler_cursos_especificos()
    a17, info_a17 = k27.ler_a17(cursos, tip, conj, universo)
    pares, info_pares = k27.ler_pares(base, cursos)
    pedidos, info_ped = ler_pedidos_ciclo3(m12, k27, cursos)
    cheg = chegadas_pares(k27)
    meses = list(k27.MESES)
    fim = k27.FIM
    taxas = {c: k27.serie_taxa(a17[c], pop, universo) for c in cursos}
    pos_u = {m: i for i, m in enumerate(universo)}

    trat = pares[pares["chegada"].notna() & (pares["chegada"] <= fim)].copy()
    ped = pedidos[pedidos["co_ibge"].isin(set(universo))].copy()
    ped["chegou"] = [(m, c) in cheg for m, c in zip(ped["co_ibge"], ped["cod_curso"])]
    fora_u = int(len(pedidos) - len(ped))
    ctrl_sets = {"principal": ped[(~ped["priorizado"]) & (~ped["chegou"])],
                 "S1_todos_pedidos": ped[~ped["chegou"]]}
    est, ev_l, cov_l = [], [], []
    info = {"pedidos": info_ped, "pedidos_fora_de_U": fora_u, "tratados_12_2_ate_fim": int(len(trat)),
            "a17": {k: info_a17[k] for k in ("municipios_formulario", "celulas_ausentes", "meses")},
            "por_especificacao": {}}

    def montar(ctrl: pd.DataFrame, cursos_ok: list[int]):
        t = trat[trat["cod_curso"].isin(cursos_ok)][["co_ibge", "cod_curso", "coorte", "chegada"]]
        c = ctrl[ctrl["cod_curso"].isin(cursos_ok)][["co_ibge", "cod_curso"]].assign(coorte=np.nan, chegada=np.nan)
        u = pd.concat([t, c], ignore_index=True).sort_values(["cod_curso", "co_ibge"]).reset_index(drop=True)
        if u.duplicated(["co_ibge", "cod_curso"]).any():
            raise FalhaValidacao("par tratado e controle ao mesmo tempo")
        Y = np.vstack([taxas[cc][pos_u[m]] for m, cc in zip(u["co_ibge"], u["cod_curso"])])
        G, _ = D2M.indices_coorte(u, meses)
        return u, Y, G

    def rodar(id_linha: str, esp: str, amostra: str, ctrl: pd.DataFrame, cursos_cand: list[int]):
        n_t = trat.groupby("cod_curso").size()
        n_c = ctrl.groupby("cod_curso").size()
        ok = [c for c in cursos_cand if n_t.get(c, 0) >= 1 and n_c.get(c, 0) >= 2]
        fora = {str(c): {"tratados": int(n_t.get(c, 0)), "controles": int(n_c.get(c, 0))}
                for c in cursos_cand if c not in ok}
        if not ok:
            est.append(nova_linha(pergunta="P3", id_linha=id_linha, especificacao=esp, amostra=amostra,
                                  outcome="K_esp", estatistica="att_pos_medio", status="SEM_ESTIMATIVA",
                                  contraste=CONTRASTE_P3, nota=f"nenhum curso com tratado e 2 controles: {fora}"))
            return None
        u, Y, G = montar(ctrl, ok)
        grupo = u["cod_curso"].to_numpy()
        clus = u["co_ibge"].to_numpy()
        coortes = sorted({(int(c), int(g)) for c, g in zip(grupo, G) if g >= 0})
        r = cs_com_if(k27, Y, G, coortes, clus, grupo)
        ev = r["evento"]
        pos = r["pos"]
        pre = r["pre"]
        mde = 2.8 * pos["ep"] if np.isfinite(pos["ep"]) else np.nan
        n_tr, n_ct = int((G >= 0).sum()), int((G < 0).sum())
        info["por_especificacao"][id_linha] = {"cursos": ok, "cursos_fora": fora, "tratados": n_tr,
                                               "controles": n_ct, "municipios": int(len(set(clus))),
                                               "coortes": len(coortes)}
        comum = dict(pergunta="P3", id_linha=id_linha, especificacao=esp, amostra=amostra, outcome="K_esp",
                     descricao_outcome="produção típica do curso (SIA, formas típicas do G4, CBO do curso)",
                     unidade="por 10 mil hab. por mês", n_tratados=n_tr, n_controles=n_ct, n_unidades=len(G),
                     n_clusters=r["n_clusters"], n_coortes=len(coortes), contraste=CONTRASTE_P3)
        thv = ev["theta"].to_numpy(float)
        es = ev["e"].to_numpy()
        m_pre = (es >= -24) & (es <= -2) & np.isfinite(thv)
        m_pre12 = (es >= -13) & (es <= -2) & np.isfinite(thv)
        th_pre = float(thv[m_pre].mean()) if m_pre.any() else np.nan
        th_pre12 = float(thv[m_pre12].mean()) if m_pre12.any() else np.nan
        passa = bool(np.isfinite(pre["p_wald"]) and pre["p_wald"] >= 0.05)
        ressalva = ""
        att = pos["att"]
        for rot, v in (("pré inteiro", th_pre), ("−13 a −2", th_pre12)):
            if np.isfinite(v) and np.isfinite(att) and abs(v) >= 0.5 * abs(att):
                ressalva += (f"θ médio do pré ({rot}) {'de mesmo sinal' if np.sign(v) == np.sign(att) else 'de sinal oposto'}"
                             f" e ≥ metade do ATT; ")
        est.append(nova_linha(**comum, estatistica="att_pos_medio", valor=att, ep=pos["ep"],
                              ic95_inf=pos["ic95_inf"], ic95_sup=pos["ic95_sup"], p_valor=pos["p_valor"],
                              tipo_p="normal, EP bootstrap Mammen (cluster município)", mde=mde,
                              familia="holm_CA" if id_linha == "P3-CA" else "", passa_pre=passa,
                              e_min=pos["e_min"], e_max=pos["e_max"], nota=ressalva.strip()))
        est.append(nova_linha(**comum, estatistica="wald_pre", valor=pre["wald"], gl=pre["gl"],
                              p_valor=pre["p_wald"], tipo_p="qui-quadrado, covariância analítica com cluster",
                              passa_pre=passa, e_min=-24, e_max=-2,
                              nota=f"p do sup-t do bootstrap = {pre['p_supt']:.3f}"))
        est.append(nova_linha(**comum, estatistica="theta_medio_pre", valor=th_pre, e_min=-24, e_max=-2,
                              nota=f"θ médio de −13 a −2 = {th_pre12:.3f}"))
        for rec in ev.itertuples(index=False):
            ev_l.append({"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "pergunta": "P3", "id_linha": id_linha,
                         "especificacao": esp, "amostra": amostra, "outcome": "K_esp", "e": int(rec.e),
                         "theta": rec.theta, "ep": rec.ep, "ic95_inf": rec.ic95_inf, "ic95_sup": rec.ic95_sup,
                         "n_tratados": rec.n_tratados, "n_controles": np.nan, "referencia": bool(rec.referencia),
                         "nota": rec.nota})
        V = r["V"]
        for i, ei in enumerate(es):
            for j, ej in enumerate(es):
                if np.isfinite(V[i, j]):
                    cov_l.append({"natureza_dos_dados": NATUREZA, "pergunta": "P3", "id_linha": id_linha,
                                  "outcome": "K_esp", "e_i": int(ei), "e_j": int(ej), "cov": float(V[i, j])})
        return r

    rodar("P3-CA", "P3-CA principal", "controles: pedidos no ciclo 3, não priorizados, sem chegada",
          ctrl_sets["principal"], cursos)
    rodar("P3-CA-S1", "P3-CA S1", "controles: todos os pedidos no ciclo 3 sem chegada", ctrl_sets["S1_todos_pedidos"],
          cursos)
    for c in cursos:
        rodar(f"P3-CA-S2-curso{c}", "P3-CA S2 (por curso)", f"curso {c}, controles da regra principal",
              ctrl_sets["principal"], [c])
    return est, ev_l, cov_l, info


# ---------------------------------------------------------------------------
# 3. P4-CA: painel mensal dos candidatos (cache privado) e estimação
# ---------------------------------------------------------------------------

def painel_candidatos(v: pd.DataFrame, cmap: pd.DataFrame, comps: list[str]) -> pd.DataFrame:
    """Outcomes por candidato (`chave`) × competência. Mês lido sem vínculo médico = zero; hora vazia em algum
    vínculo deixa as horas do mês ausentes (regra do a16, do P4 e do P6)."""
    vc = v.merge(cmap[["chave", "co_profissional_sus", "co_ibge_1a_opcao"]], on="co_profissional_sus", how="inner")
    h = sum(vc[c].astype("Float64") for c in ("qt_ch_ambulatorial", "qt_ch_hosp_sus", "qt_ch_outros"))
    vc["h"] = h.astype(float)
    vc["h_aus"] = vc["h"].isna()
    vc["no_mun_1a"] = (vc["co_municipio"] == vc["co_ibge_1a_opcao"]).fillna(False).astype(bool)
    vc["h_mun"] = np.where(vc["no_mun_1a"], vc["h"], 0.0)
    vc["h_fora"] = np.where(~vc["no_mun_1a"], vc["h"], 0.0)
    vc["h_sus"] = np.where(vc["tp_sus_nao_sus"] == "S", vc["h"], 0.0)
    g = vc.groupby(["chave", "competencia"], sort=True)
    agg = pd.DataFrame({"n_vinculos": g.size().astype(float), "horas_totais": g["h"].sum(min_count=1),
                        "horas_mun_1a": g["h_mun"].sum(min_count=1), "horas_fora_1a": g["h_fora"].sum(min_count=1),
                        "horas_sus": g["h_sus"].sum(min_count=1), "_aus": g["h_aus"].any(),
                        "vinculo_mun_1a": g["no_mun_1a"].any().astype(float),
                        "n_municipios": g["co_municipio"].nunique().astype(float)})
    grade = pd.MultiIndex.from_product([sorted(cmap["chave"].unique()), comps], names=["chave", "competencia"])
    p = agg.reindex(grade)
    tem = p["n_vinculos"].notna()
    aus = p["_aus"].fillna(False).astype(bool)
    for c in ("n_vinculos", "horas_totais", "horas_mun_1a", "horas_fora_1a", "horas_sus", "vinculo_mun_1a",
              "n_municipios"):
        p[c] = p[c].where(tem, 0.0)
    p.loc[aus, ["horas_totais", "horas_mun_1a", "horas_fora_1a", "horas_sus"]] = np.nan
    return p.drop(columns="_aus").reset_index()


def matriz_evento(p: pd.DataFrame, base: pd.DataFrame, col: str, comps: list[str]) -> np.ndarray:
    """Y alinhado no tempo de evento (linhas = base, colunas = e de E4_MIN a E4_MAX)."""
    larga = p.pivot(index="chave", columns="competencia", values=col).reindex(index=base["chave"], columns=comps)
    pos = {c: i for i, c in enumerate(comps)}
    out = np.full((len(base), E4_MAX - E4_MIN + 1), np.nan)
    arr = larga.to_numpy(float)
    for i, ciclo in enumerate(base["ciclo"].to_numpy()):
        i0 = pos[T0[int(ciclo)]]
        for j, e in enumerate(range(E4_MIN, E4_MAX + 1)):
            t = i0 + e
            if 0 <= t < len(comps):
                out[i, j] = arr[i, t]
    return out


def dados_p4(m30) -> tuple[dict, dict]:
    """Refaz o painel mensal dos candidatos do universo do P6 (duas regras) a partir do cache privado."""
    a16, g1 = m30.modulos()
    comps = m30.competencias()
    git = m30.conferir_gitignore()
    info_cache = m30.conferir_cache_a16(a16)
    rep_a16 = m30.reproduzir_a16(a16)
    ligs, _, info_g1 = m30.ligar_candidatos(a16, g1)
    am = pd.read_parquet(P6_AMOSTRA)
    if set(am["natureza_dos_dados"]) != {NATUREZA}:
        raise FalhaValidacao("P6_amostra com natureza diferente de EMPIRICO")
    bases, cmaps = {}, []
    for regra in (REGRA_PRINCIPAL, REGRA_NOME):
        a = am[(am["regra_ligacao"] == regra) & (am["ligado"] == 1)].copy()
        lg = ligs[regra][["ciclo", "id_candidato", "co_profissional_sus", "ligado"]]
        a = a.merge(lg, on=["ciclo", "id_candidato"], how="left", suffixes=("", "_lig"), validate="one_to_one")
        if (a["ligado_lig"] != 1).any() or a["co_profissional_sus"].isna().any():
            raise FalhaValidacao(f"{regra}: candidato ligado no P6 sem ligação refeita")
        a["chave"] = regra + "|" + a["ciclo"].astype(str) + "|" + a["id_candidato"].astype(str)
        bases[regra] = a
        cmaps.append(a[["chave", "co_profissional_sus", "co_ibge_1a_opcao"]].astype("string"))
    cmap = pd.concat(cmaps, ignore_index=True)
    profs = sorted(set(cmap["co_profissional_sus"].dropna()))
    v = m30.ler_vinculos_candidatos(a16, profs)
    p = painel_candidatos(v, cmap, comps)
    # conferência: médias do seguimento e horas pré iguais às do P6 versionado
    dif = {}
    for regra, a in bases.items():
        pp = p[p["chave"].isin(set(a["chave"]))]
        for cciclo, (ini, fim) in m30.SEGUIMENTO.items():
            ch = set(a.loc[a["ciclo"] == cciclo, "chave"])
            s = pp[pp["chave"].isin(ch) & (pp["competencia"] >= ini) & (pp["competencia"] <= fim)]
            mm = s.groupby("chave")[["horas_totais", "horas_sus", "vinculo_mun_1a", "n_municipios"]].mean()
            ref = a.set_index("chave").loc[sorted(ch), ["y3_horas_totais_media", "y2_horas_sus_media",
                                                         "y1_vinculo_mun_1a_opcao_media", "y5_n_municipios_media"]]
            mm = mm.reindex(ref.index)
            for c1, c2 in zip(mm.columns, ref.columns):
                d = ~np.isclose(mm[c1].to_numpy(float), ref[c2].to_numpy(float), equal_nan=True, atol=1e-9)
                dif[f"{regra}|{cciclo}|{c1}"] = int(d.sum())
        pre = pp[(pp["competencia"] >= m30.PRE_HORAS[0]) & (pp["competencia"] <= m30.PRE_HORAS[1])]
        hp = pre.groupby("chave")["horas_totais"].mean().reindex(a["chave"])
        d = ~np.isclose(hp.to_numpy(float), a["cov_horas_pre"].to_numpy(float), equal_nan=True, atol=1e-9)
        dif[f"{regra}|cov_horas_pre"] = int(d.sum())
    if any(dif.values()):
        raise FalhaValidacao(f"painel refeito não reproduz P6_amostra: {dif}")
    soma = p["horas_mun_1a"] + p["horas_fora_1a"]
    if not np.allclose(soma.to_numpy(float), p["horas_totais"].to_numpy(float), equal_nan=True):
        raise FalhaValidacao("horas no município da 1ª opção + fora ≠ horas totais")
    del v, cmap
    info = {"gitignore": git, "cache_a16": info_cache, "reproducao_a16": rep_a16,
            "reproducao_g1": info_g1["reproducao_g1"], "conferencia_P6_amostra": dif,
            "linhas_painel_candidato_mes": int(len(p)), "competencias": [comps[0], comps[-1]]}
    return {"bases": bases, "painel": p, "comps": comps}, info


def p4ca(m30) -> tuple[list[dict], list[dict], list[dict], dict]:
    dados, info = dados_p4(m30)
    p, comps = dados["painel"], dados["comps"]
    es = np.arange(E4_MIN, E4_MAX + 1)
    j_ref = int(np.flatnonzero(es == -1)[0])
    est, ev_l, cov_l = [], [], []
    info["por_especificacao"] = {}

    def amostra(regra: str, rs: set[int] | None) -> pd.DataFrame:
        a = dados["bases"][regra]
        a = a[a["r"].isin(rs)] if rs is not None else a
        g = a.groupby("celula")["d_alocado_1a_opcao"].agg(["min", "max"])
        dois = set(g.index[(g["min"] == 0) & (g["max"] == 1)])
        return a[a["celula"].isin(dois)].sort_values(["ciclo", "celula", "id_candidato"]).reset_index(drop=True)

    specs = [("P4-CA", "P4-CA principal", REGRA_PRINCIPAL, set(JANELA_PRINCIPAL), False,
              OUT4_PRIM + OUT4_SEC, "r ∈ {−2, −1, +1, +2}, células com os dois lados"),
             ("P4-CA-Sb", "P4-CA S(b)", REGRA_PRINCIPAL, set(range(-4, 6)) - {0}, False, OUT4_PRIM,
              "r ∈ [−4, +5] sem 0, células com os dois lados"),
             ("P4-CA-Sc", "P4-CA S(c)", REGRA_PRINCIPAL, set(range(-4, 6)), True, OUT4_PRIM,
              "inclui os empatados (r = 0) com indicador de empate"),
             ("P4-CA-Sd", "P4-CA S(d)", REGRA_NOME, set(JANELA_PRINCIPAL), False, OUT4_PRIM,
              "ligação só por nome, r ∈ {−2, −1, +1, +2}")]
    for id_linha, esp, regra, rs, com_empate, outs, rot in specs:
        a = amostra(regra, rs)
        D = a["d_alocado_1a_opcao"].to_numpy(int)
        cel = a["celula"].astype(str).to_numpy()
        W = a[["empatado_no_corte"]].to_numpy(float) if com_empate else None
        info["por_especificacao"][id_linha] = {
            "regra": regra, "r": sorted(rs), "candidatos": int(len(a)), "alocados": int(D.sum()),
            "nao_alocados": int((D == 0).sum()), "celulas": int(len(set(cel))),
            "por_ciclo": {str(k): int(v) for k, v in a["ciclo"].value_counts().sort_index().items()},
            "empatados": int(a["empatado_no_corte"].sum())}
        for o, _, _ in outs:
            Ye = matriz_evento(p, a, o, comps)
            dY = Ye - Ye[:, [j_ref]]
            dY[:, j_ref] = np.nan
            r = estimar_p4ca(dY, D, cel, es, W=W)
            prim = id_linha == "P4-CA" and o in {x for x, _, _ in OUT4_PRIM}
            sec = id_linha == "P4-CA" and o in {x for x, _, _ in OUT4_SEC}
            passa = bool(r["p_perm_pre"] >= 0.05)
            th = r["theta"]
            comum = dict(pergunta="P4", id_linha=id_linha, especificacao=esp, amostra=rot, outcome=o,
                         descricao_outcome=ROTULO4[o], unidade=UNID4[o], n_tratados=int(D.sum()),
                         n_controles=int((D == 0).sum()), n_unidades=int(len(D)), n_clusters=r["G"],
                         contraste=CONTRASTE_P4)
            lo = r["media"] - stats.norm.ppf(0.975) * r["ep_media"]
            hi = r["media"] + stats.norm.ppf(0.975) * r["ep_media"]
            m_pre = (es >= -6) & (es <= -2) & np.isfinite(th)
            th_pre = float(th[m_pre].mean()) if m_pre.any() else np.nan
            ressalva = ""
            if np.isfinite(th_pre) and abs(th_pre) >= 0.5 * abs(r["media"]):
                ressalva = (f"θ médio do pré (−6 a −2) {'de mesmo sinal' if np.sign(th_pre) == np.sign(r['media']) else 'de sinal oposto'}"
                            " e ≥ metade do efeito médio do pós")
            est.append(nova_linha(**comum, estatistica="efeito_pos_medio", valor=r["media"], ep=r["ep_media"],
                                  ic95_inf=lo, ic95_sup=hi, p_valor=r["p_perm_media"],
                                  tipo_p="permutação de D dentro da célula (999)",
                                  p_qui2=p_normal(r["media"] / r["ep_media"]) if r["ep_media"] > 0 else np.nan,
                                  mde=2.8 * r["ep_media"], familia="holm_CA" if prim else ("bky_P4CA_sec" if sec else ""),
                                  passa_pre=passa, e_min=0, e_max=E4_MAX, nota=ressalva))
            est.append(nova_linha(**comum, estatistica="wald_pre", valor=r["wald_pre"], gl=r["gl_pre"],
                                  p_valor=r["p_perm_pre"], tipo_p="permutação do Wald dentro da célula (999)",
                                  p_qui2=r["p_qui2_pre"], passa_pre=passa, e_min=E4_MIN, e_max=-2))
            est.append(nova_linha(**comum, estatistica="theta_medio_pre", valor=th_pre, e_min=-6, e_max=-2))
            for j, e in enumerate(es):
                ref = e == -1
                ev_l.append({"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "pergunta": "P4",
                             "id_linha": id_linha, "especificacao": esp, "amostra": rot, "outcome": o, "e": int(e),
                             "theta": 0.0 if ref else th[j], "ep": np.nan if ref else r["ep"][j],
                             "ic95_inf": np.nan if ref else th[j] - stats.norm.ppf(0.975) * r["ep"][j],
                             "ic95_sup": np.nan if ref else th[j] + stats.norm.ppf(0.975) * r["ep"][j],
                             "n_tratados": int(r["n1"][j]), "n_controles": int(r["n0"][j]), "referencia": bool(ref),
                             "nota": "referência e = −1: zero por construção" if ref else ""})
            if id_linha == "P4-CA":
                V = r["V"]
                for i, ei in enumerate(es):
                    for j, ej in enumerate(es):
                        if ei != -1 and ej != -1 and np.isfinite(V[i, j]):
                            cov_l.append({"natureza_dos_dados": NATUREZA, "pergunta": "P4", "id_linha": id_linha,
                                          "outcome": o, "e_i": int(ei), "e_j": int(ej), "cov": float(V[i, j])})
    return est, ev_l, cov_l, info


# ---------------------------------------------------------------------------
# 4. Multiplicidade, figuras e gravação
# ---------------------------------------------------------------------------

def aplicar_multiplicidade(est: pd.DataFrame) -> pd.DataFrame:
    L = _importar(DIR_RDD / "rdd_lib.py", "rdd_lib_ca")
    m = (est["familia"] == "holm_CA") & est["p_valor"].notna()
    if int(m.sum()) not in (1, 4):
        raise FalhaValidacao(f"família de Holm com {int(m.sum())} linhas (esperadas 4, ou 1 sem o P4-CA)")
    est.loc[m, "p_holm"] = holm(est.loc[m, "p_valor"].to_numpy(float))
    b = (est["familia"] == "bky_P4CA_sec") & est["p_valor"].notna()
    if b.any():
        est.loc[b, "q_bky"] = L.qvalores_bky(est.loc[b, "p_valor"].to_numpy(float))
    return est


def gerar_figuras(ev: pd.DataFrame, dir_fig: Path) -> list[dict]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    dir_fig.mkdir(parents=True, exist_ok=True)
    figs = []
    cor = "#2a78d6"

    def painel(ax, s, titulo, ylabel):
        s = s.sort_values("e")
        ax.axhline(0, color="#999", lw=0.8)
        ax.axvline(-0.5, color="#999", lw=0.8, ls=":")
        ax.fill_between(s["e"], s["ic95_inf"], s["ic95_sup"], color=cor, alpha=0.18, lw=0)
        ax.plot(s["e"], s["theta"], "o-", color=cor, ms=3, lw=1)
        ax.set_title(titulo, fontsize=9)
        ax.set_xlabel("meses desde a chegada / o início", fontsize=8)
        ax.set_ylabel(ylabel, fontsize=8)
        ax.tick_params(labelsize=7)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)

    s = ev[(ev["id_linha"] == "P3-CA") & (ev["outcome"] == "K_esp")]
    if len(s):
        fig, ax = plt.subplots(figsize=(6.4, 3.4))
        painel(ax, s, "P3-CA: K_esp, chegada contra pedidos não priorizados", "por 10 mil hab. por mês")
        fig.tight_layout()
        caminho = dir_fig / "CA_P3_evento.png"
        fig.savefig(caminho, dpi=150, metadata={"Software": None})
        plt.close(fig)
        figs.append({"arquivo": rotulo(caminho), "sha256": sha256(caminho)})
    s4 = ev[ev["id_linha"] == "P4-CA"]
    if len(s4):
        fig, axs = plt.subplots(1, 3, figsize=(10, 3.2), sharey=True)
        for ax, (o, rot, u) in zip(axs, OUT4_PRIM):
            painel(ax, s4[s4["outcome"] == o], rot, "h/sem cadastradas")
        fig.tight_layout()
        caminho = dir_fig / "CA_P4_evento.png"
        fig.savefig(caminho, dpi=150, metadata={"Software": None})
        plt.close(fig)
        figs.append({"arquivo": rotulo(caminho), "sha256": sha256(caminho)})
    return figs


def entradas(com_p4: bool) -> list[dict]:
    k27, _ = modulos_p3()
    lista = [(PROTOCOLO_MD, "protocolo congelado"),
             (k27.A17_PAINEL, "K_esp: SIA por forma × curso (a17)"),
             (k27.V_CELULA, "células dos ciclos 1–2 (pares do 12.2)"),
             (k27.G4_RESUMO, "cursos ESPECÍFICO do G4"), (k27.G4_MAPA, "formas típicas"),
             (ROOT / "output" / "aquisicao" / "a08_ivs_2010_oficial_municipio.csv", "universo U (IVS 2010 oficial)"),
             (ROOT / "output" / "aquisicao" / "populacao_censo2022_municipios.csv", "população 2022"),
             (ROOT / "data" / "raw" / "pmm_e" / "2026_ciclo3_adesao_gestores_resultado_final.xlsx",
              "adesão do ciclo 3 (pedido e priorização)"),
             (NOMINAL, "chegadas e t₀ (só município, curso, data de início)")]
    if com_p4:
        lista += [(P6_AMOSTRA, "universo do P6: r, D, célula, ligação (pseudônimo)"),
                  (ROOT / "output" / "aquisicao" / "cnes_profissional" / "a16_manifesto_cnes_profissional.json",
                   "manifesto do a16 (conferência do cache privado)"),
                  (OUT / "G1_candidatos_origem.parquet", "ligação do G1 (conferência)")]
    return [{"caminho": rotulo(p), "sha256": sha256(p), "papel": papel} for p, papel in lista if Path(p).exists()]


def executar() -> int:
    est_l, ev_l, cov_l, info3 = p3ca()
    m30 = _importar(DIR_RDD / "30_mecanismo_alocacao.py", "m30_para_ca")
    info4, com_p4 = {}, True
    try:
        e4, v4, c4, info4 = p4ca(m30)
        est_l += e4
        ev_l += v4
        cov_l += c4
    except SystemExit as exc:
        com_p4 = False
        info4 = {"status": "NAO_EXECUTADO", "motivo": str(exc)}
        est_l.append(nova_linha(pergunta="P4", id_linha="P4-CA", especificacao="P4-CA principal",
                                estatistica="efeito_pos_medio", status="NAO_EXECUTADO", contraste=CONTRASTE_P4,
                                nota=f"cache privado indisponível: {exc}"))
    est = pd.DataFrame(est_l)[COLUNAS_EST]
    est = aplicar_multiplicidade(est)
    ev = pd.DataFrame(ev_l)[COLUNAS_EVENTO]
    cov = pd.DataFrame(cov_l)
    for df in (est, ev, cov):
        if any(c.lower() in COLUNAS_PROIBIDAS for c in df.columns):
            raise FalhaValidacao("coluna proibida")
        if set(df["natureza_dos_dados"]) != {NATUREZA}:
            raise FalhaValidacao("rótulo ausente")
    OUT.mkdir(parents=True, exist_ok=True)
    est.to_csv(OUT / NOME_EST, index=False, float_format="%.10g")
    ev.to_csv(OUT / NOME_EVENTO, index=False, float_format="%.10g")
    cov.to_csv(OUT / NOME_COV, index=False, float_format="%.12g")
    figs = gerar_figuras(ev, OUT / DIR_FIG)
    resumo = {
        "etapa": "CA_comparacao_alternativa_P3P4", "natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO,
        "gerador": rotulo(Path(__file__)), "data_execucao": DATA_EXECUCAO,
        "protocolo": {"texto": rotulo(PROTOCOLO_MD), "sha256_texto": sha256(PROTOCOLO_MD), "secoes": "§3, §4, §6"},
        "leitura": {"P3-CA": CONTRASTE_P3, "P4-CA": CONTRASTE_P4},
        "parametros": {"P3": {"e": [E3_MIN, E3_MAX], "controles": "nunca (só o grupo alternativo), mesmo curso",
                              "bootstrap": {"B": 9999, "pesos": "Mammen", "semente": SEMENTE, "cluster": "município"}},
                       "P4": {"e": [E4_MIN, E4_MAX], "t0": T0, "referencia": -1, "permutacao": {"B": B_PERM,
                              "semente": SEMENTE, "dentro": "célula"}, "ep": "agrupado por célula, G/(G-1)"}},
        "amostras": {"P3": info3, "P4": info4},
        "saidas": {rotulo(OUT / n): sha256(OUT / n) for n in (NOME_EST, NOME_EVENTO, NOME_COV)},
        "figuras": figs,
        "entradas": entradas(com_p4),
        "dados_pessoais": "código do profissional, nome e CPF só em memória e no cache privado (gitignore); saídas "
                          "só com estatísticas por e e por especificação",
        "integridade": "nada imputado; ausente não vira zero; CNES < 202609; SIA até 202605; o arquivo local de IVS "
                       "não é lido; nenhum outcome do ciclo 3 é lido",
        "desvios": DESVIOS,
    }
    gravar_json(OUT / NOME_RESUMO, resumo)
    print(f"CA: {len(est)} linhas de estimativas, {len(ev)} de evento; P4-CA executado: {com_p4}")
    return 0


DESVIOS: list[dict] = []


def verificar() -> int:
    res = OUT / NOME_RESUMO
    if not res.exists():
        raise SystemExit(f"{rotulo(res)} ausente; rode --etapa estimar")
    r = json.loads(res.read_text(encoding="utf-8"))
    ruins = [k for k, h in r["saidas"].items() if not (ROOT / k).exists() or sha256(ROOT / k) != h]
    ruins += [f["arquivo"] for f in r["figuras"] if sha256(ROOT / f["arquivo"]) != f["sha256"]]
    if ruins:
        raise SystemExit(f"verificar: saídas do CA não conferem: {ruins}")
    est = pd.read_csv(OUT / NOME_EST)
    if set(est["natureza_dos_dados"]) != {NATUREZA}:
        raise SystemExit("verificar: natureza diferente de EMPIRICO")
    print("CA: saídas conferem com o resumo")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--etapa", choices=("verificar", "estimar"), default="verificar")
    args = ap.parse_args(argv)
    return executar() if args.etapa == "estimar" else verificar()


if __name__ == "__main__":
    sys.exit(main())
