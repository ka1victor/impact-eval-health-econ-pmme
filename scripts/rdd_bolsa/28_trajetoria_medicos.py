"""P4 (protocolo 54): trajetória individual dos médicos do PMM-E, origem e contabilidade líquida (T4.1–T4.3).

Protocolo: `docs/06_execucao/54_protocolo_P4_oferta_substituicao.md`, congelado em 19/10/2026 antes de abrir o
painel a16 por tempo de evento. Estatuto de toda linha: `EXPLORATORIO_P4`; `natureza_dos_dados = EMPIRICO`.
Nada aqui tem fonte de exogeneidade validada. O contraste é a entrada do médico no PMM-E (datas de início
diferentes entre médicos), não a bolsa nem o efeito do PMM-E sobre o município.

Unidade e amostra (§1)
----------------------
- Médico do PMM-E ligado ao CNES na X1 (regra D1 principal; literal como sensibilidade) × mês, 202406–202608.
  Nenhuma competência >= 202609 é lida. A chave longitudinal é o código do profissional no CNES (`id_prof` do
  a16), não o CRM (portão G5, C5).
- Início, ciclo, curso, estabelecimento e município do posto vêm das listas nominais do PMM-E, lidas só em
  memória pela função `ler_listas_pmme` da X1 (script 17), que dá o mesmo `id_medico`. Nome, CRM e UF são
  descartados logo após a leitura; nada identificável é gravado. A faixa e a origem (X1 b) vêm de
  `X1_medicos.parquet`. O IVS não é lido (as faixas da lista já foram conferidas com o IVS oficial pela X1).
- e = mês − mês de início. Janela principal e ∈ [−6, +6]; janela longa e ∈ [−12, +10]; subamostra balanceada
  = início entre 202412 e 202602 (todos os meses de −6 a +6).

Outcomes por médico × mês (§2): horas semanais cadastradas (total, SUS, não SUS, ambulatorial, hospitalar), número
de vínculos, de estabelecimentos e de municípios; horas no estabelecimento do posto, no município do posto e fora
dele; horas em estabelecimentos públicos (natureza jurídica 1xxx) e privados com fins (2xxx) e sem fins lucrativos
(3xxx). São horas cadastradas, não trabalhadas.

Especificações (§3)
-------------------
- T4.1a: médias por tempo de evento, por ciclo (1, 2 e 1+2), na amostra completa (janela longa) e na balanceada.
- T4.1b: Callaway–Sant'Anna no nível do médico: coortes = mês de início (ciclos 1 e 2), controles = médicos ainda
  não iniciados (início posterior, inclusive o ciclo 3 até 202608), base universal g − 1, agregação por e com pesos
  de coorte, teste conjunto dos pré, bootstrap multiplicador (Mammen) por médico, semente 20261019.
- T4.1c: T4.1b separado pela origem (X1 b: já tinha vínculo no município do posto na última competência pré-início).
- T4.2: quem mudou de município: horas que deixou no município de origem e variação das horas da mesma CBO nesse
  município no CNES nacional (a09), entre o pré e o pós.
- T4.3: contabilidade líquida: Δ no município do posto, Δ fora dele e saldo, somados por curso e por faixa (só
  tabulação, sem contraste no corte).
BKY dentro do T4.1b e do T4.1c (§4), uma família por regra de ligação.

Uso
---
    python3 scripts/rdd_bolsa/28_trajetoria_medicos.py
    python3 scripts/rdd_bolsa/28_trajetoria_medicos.py --atualizar-doc
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
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    return mod


_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
L = _importar(DIR_RDD / "rdd_lib.py", "rdd_lib_p4")
X1M = _importar(DIR_RDD / "17_ponte_pmme_cnes.py", "ponte_x1_para_p4")
sys.dont_write_bytecode = _bytecode

# ---------------------------------------------------------------------------
# Caminhos e parâmetros do protocolo
# ---------------------------------------------------------------------------

OUT = ROOT / "output" / "rdd_bolsa"
NOME_EST = "P4_estimativas.csv"
NOME_RESUMO = "P4_resumo.json"
DIR_FIG = "P4_figuras"
PROTOCOLO_MD = ROOT / "docs" / "06_execucao" / "54_protocolo_P4_oferta_substituicao.md"
DOC = ROOT / "docs" / "06_execucao" / "57d_resultados_P4_trajetoria.md"

DIR_A16 = ROOT / "output" / "aquisicao" / "cnes_profissional"
ARQ_VINC = DIR_A16 / "painel_vinculo_mes.parquet"
ARQ_MED = DIR_A16 / "painel_medico_mes.parquet"
ARQ_CHAVES = DIR_A16 / "chaves_origem.parquet"
MANIF_A16 = DIR_A16 / "a16_manifesto_cnes_profissional.json"
G5_RESUMO = OUT / "G5_resumo.json"
ARQ_X1 = OUT / "X1_medicos.parquet"
ARQ_NAC = ROOT / "output" / "aquisicao" / "cnes_nacional" / "painel_municipio_cbo_mes.parquet"
PONTE = ROOT / "output" / "aquisicao" / "ponte_curso_cbo_oficial.json"
CACHE_PRIVADO = DIR_A16 / "cache_privado"

DATA_EXECUCAO = "2026-10-23"
ESTATUTO = "EXPLORATORIO_P4"
NATUREZA = "EMPIRICO"
LIMITE_EXCLUSIVO = "202609"
COMP_INICIAL, COMP_FINAL = "202406", "202608"
E_PRINC = (-6, 6)
E_LONGA = (-12, 10)
BAL_INICIO = ("202412", "202602")
CICLOS_TRATADOS = (1, 2)
REGRAS = ("d1_pos_hoc", "literal_doc45")          # a primeira é a principal
ROTULO_REGRA = {"d1_pos_hoc": "D1 (principal)", "literal_doc45": "literal (sensibilidade)"}
B_BOOT = 9_999
SEMENTE = 20261019
MIN_CONTROLES = 30                                  # fixado antes de abrir os dados por tempo de evento
Z = L.Z_975
Z_IQR = stats.norm.ppf(0.75) - stats.norm.ppf(0.25)
ORIGENS = {1: "ja_no_municipio", 0: "novo_no_municipio"}
ROTULO_ORIGEM = {"ja_no_municipio": "já tinha vínculo no município do posto",
                 "novo_no_municipio": "novo no município do posto"}

# Outcomes do §2 (entram no BKY) e complementares (fora do BKY), com rótulo e unidade.
OUTCOMES = [
    ("horas_totais", "horas totais", "h/sem"),
    ("horas_sus", "horas em vínculos SUS", "h/sem"),
    ("horas_nao_sus", "horas em vínculos não SUS", "h/sem"),
    ("horas_amb", "horas ambulatoriais", "h/sem"),
    ("horas_hosp", "horas hospitalares", "h/sem"),
    ("n_vinculos", "número de vínculos", "vínculos"),
    ("n_estabelecimentos", "número de estabelecimentos", "estabelecimentos"),
    ("n_municipios", "número de municípios", "municípios"),
    ("horas_estab_posto", "horas no estabelecimento do posto", "h/sem"),
    ("horas_mun_posto", "horas no município do posto", "h/sem"),
    ("horas_fora_mun_posto", "horas fora do município do posto", "h/sem"),
    ("horas_publico", "horas em estabelecimentos públicos", "h/sem"),
    ("horas_privado_com_fins", "horas em privados com fins lucrativos", "h/sem"),
    ("horas_privado_sem_fins", "horas em privados sem fins lucrativos", "h/sem"),
]
COMPLEMENTARES = [
    ("com_vinculo_medico", "tem vínculo médico cadastrado no mês", "fração"),
    ("horas_resto_mun_posto", "horas no município do posto fora do estabelecimento do posto", "h/sem"),
    ("horas_outra_natureza", "horas em outras naturezas jurídicas (pessoa física etc.)", "h/sem"),
]
ROTULO = {o: r for o, r, _ in OUTCOMES + COMPLEMENTARES}
UNIDADE = {o: u for o, _, u in OUTCOMES + COMPLEMENTARES}
OUT_PROTOCOLO = [o for o, _, _ in OUTCOMES]
OUT_TODOS = OUT_PROTOCOLO + [o for o, _, _ in COMPLEMENTARES]
ROTULO_COMPLEMENTAR = "COMPLEMENTAR (fora do §2 e do BKY; relatado para leitura)"

COLUNAS = ["especificacao", "regra_ligacao", "amostra", "janela", "grupo_tipo", "grupo", "outcome", "medida", "e",
           "estimativa", "ep", "ic95_inf", "ic95_sup", "p_valor", "q_bky", "entra_bky", "n_obs", "n_tratados",
           "n_controles", "n_coortes", "unidade", "status", "nota", "leitura", "natureza_dos_dados", "estatuto"]

LEITURA = {
    "T4.1a": "descritivo (médias por tempo de evento; horas cadastradas)",
    "T4.1b": "associado à entrada no PMM-E, sob tendências paralelas entre médicos que entram em datas diferentes; "
             "exploratório",
    "T4.1c": "associado à entrada, por origem pré-tratamento (X1 b); exploratório",
    "T4.2": "descritivo do deslocamento",
    "T4.3": "descritivo (contabilidade pré × pós sem grupo de comparação)",
    "origem": "descritivo (composição dos médicos pela origem)",
}


class FalhaValidacao(RuntimeError):
    """Conferência de integridade que falhou: o script para sem gravar."""


def rotulo(p: Path) -> str:
    return Path(p).resolve().relative_to(ROOT).as_posix()


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with Path(p).open("rb") as f:
        for bloco in iter(lambda: f.read(1 << 22), b""):
            h.update(bloco)
    return h.hexdigest()


def bloco_entrada(path: Path, papel: str, fonte: str, data_ref: str, cobertura: str, unidade: str, chaves: str,
                  filtros: str) -> dict:
    return {"caminho": rotulo(path), "sha256": sha256(path), "bytes": Path(path).stat().st_size, "papel": papel,
            "fonte": fonte, "data_referencia": data_ref, "cobertura": cobertura, "unidade": unidade,
            "chaves": chaves, "filtros": filtros}


def _nan_none(o):
    if isinstance(o, dict):
        return {str(k): _nan_none(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_nan_none(v) for v in o]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating, float)):
        return None if not np.isfinite(o) else float(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


def gravar_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(_nan_none(obj), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def nova_linha(**kw) -> dict:
    base = {c: np.nan for c in COLUNAS}
    base.update({"q_bky": np.nan, "entra_bky": False, "status": "EXECUTADO", "nota": "",
                 "natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO})
    base.update(kw)
    if not base.get("leitura") or (isinstance(base.get("leitura"), float)):
        base["leitura"] = LEITURA.get(str(base["especificacao"]).split("_")[0], "")
    return base


# ---------------------------------------------------------------------------
# 1. Callaway–Sant'Anna no nível do médico (adaptado de 22_chegada_pmme_evento.py, com máscara de tratados)
# ---------------------------------------------------------------------------

def att_gt(Y: np.ndarray, G: np.ndarray, trat: np.ndarray, coortes: list[int], *, e_min: int, e_max: int,
           min_controles: int = MIN_CONTROLES) -> tuple[pd.DataFrame, np.ndarray]:
    """ATT(g, t) com base universal b = g − 1 e controles ainda não iniciados.

    Y: N × T (NaN = ausente). G: índice do mês de início de cada médico (−1 = início depois do horizonte).
    trat: máscara dos médicos que podem ser tratados (ciclos 1 e 2 e, no T4.1c, a origem); os controles são todos
    os médicos com G > max(t, b) ou G = −1, fora da própria coorte, qualquer que seja a máscara.
    Devolve as células e a matriz N × células de funções de influência (escala: ATT^ − ATT ≈ média de IF).
    """
    N, T = Y.shape
    linhas, ifs = [], []
    for g in coortes:
        b = g - 1
        if b < 0:
            continue
        tratada = (G == g) & trat
        n_g = int(tratada.sum())
        if n_g == 0:
            continue
        for t in range(max(0, g + e_min), min(T, g + e_max + 1)):
            if t == b:
                continue
            ok = np.isfinite(Y[:, t]) & np.isfinite(Y[:, b])
            dy = Y[:, t] - Y[:, b]
            ctrl = ((G < 0) | (G > max(t, b))) & (G != g)
            mt, mc = tratada & ok, ctrl & ok
            n1, n0 = int(mt.sum()), int(mc.sum())
            reg = {"g": g, "t": t, "e": t - g, "n_tratados": n1, "n_controles": n0, "n_coorte": n_g,
                   "att": np.nan, "nota": ""}
            psi = np.zeros(N)
            if n1 < 1 or n0 < min_controles:
                reg["nota"] = f"sem suporte: {n1} tratados e {n0} controles (mínimo {min_controles})"
            else:
                mu1, mu0 = dy[mt].mean(), dy[mc].mean()
                reg["att"] = float(mu1 - mu0)
                psi[mt] = N * (dy[mt] - mu1) / n1
                psi[mc] = -N * (dy[mc] - mu0) / n0
            linhas.append(reg)
            ifs.append(psi)
    tab = pd.DataFrame(linhas, columns=["g", "t", "e", "n_tratados", "n_controles", "n_coorte", "att", "nota"])
    return tab, (np.column_stack(ifs) if ifs else np.zeros((N, 0)))


def agregar_evento(tab: pd.DataFrame, IF: np.ndarray, membro: dict[int, np.ndarray], *, e_min: int, e_max: int
                   ) -> tuple[pd.DataFrame, np.ndarray]:
    """θ(e) = Σ_g w_g ATT(g, g+e), w_g ∝ tamanho da coorte entre as coortes com célula definida; IF com os pesos."""
    N = IF.shape[0]
    linhas, ifs = [], []
    for e in range(e_min, e_max + 1):
        if e == -1:
            linhas.append({"e": e, "theta": 0.0, "n_coortes": 0, "n_tratados": 0, "n_controles_min": 0,
                           "referencia": True, "nota": "base universal b = g − 1: zero por construção"})
            ifs.append(np.zeros(N))
            continue
        sel = tab.index[(tab["e"] == e) & tab["att"].notna()] if len(tab) else []
        if len(sel) == 0:
            linhas.append({"e": e, "theta": np.nan, "n_coortes": 0, "n_tratados": 0, "n_controles_min": 0,
                           "referencia": False, "nota": "nenhuma coorte com ATT(g, g+e) definido"})
            ifs.append(np.full(N, np.nan))
            continue
        gs = tab.loc[sel, "g"].to_numpy()
        pi = np.array([membro[g].mean() for g in gs])
        S = pi.sum()
        w = pi / S
        att = tab.loc[sel, "att"].to_numpy(dtype=float)
        psi = IF[:, sel] @ w
        D = np.column_stack([membro[g].astype(float) - p for g, p in zip(gs, pi)])
        psi_w = D / S - np.outer(D.sum(axis=1), pi) / S ** 2
        psi = psi + psi_w @ att
        linhas.append({"e": e, "theta": float(np.sum(w * att)), "n_coortes": int(len(sel)),
                       "n_tratados": int(tab.loc[sel, "n_tratados"].sum()),
                       "n_controles_min": int(tab.loc[sel, "n_controles"].min()), "referencia": False, "nota": ""})
        ifs.append(psi)
    return pd.DataFrame(linhas), np.column_stack(ifs)


def pesos_mammen(B: int, N: int, semente: int) -> np.ndarray:
    rng = np.random.default_rng(semente)
    r5 = math.sqrt(5.0)
    p = (r5 + 1) / (2 * r5)
    return np.where(rng.random((B, N)) < p, (1 - r5) / 2, (1 + r5) / 2)


def ep_bootstrap(IF: np.ndarray, xi: np.ndarray) -> np.ndarray:
    """EP = intervalo interquartil das perturbações do bootstrap multiplicador / (z_0,75 − z_0,25)."""
    N = IF.shape[0]
    pert = xi @ np.nan_to_num(IF) / N
    q75, q25 = np.percentile(pert, [75, 25], axis=0)
    return (q75 - q25) / Z_IQR


def wald_pre(theta: np.ndarray, IF: np.ndarray, mascara: np.ndarray) -> dict:
    """Wald conjunto de θ(e) = 0 nos e da máscara, covariância IF'IF/N²."""
    N = IF.shape[0]
    m = mascara & np.isfinite(theta) & np.isfinite(IF).all(axis=0)
    if m.sum() == 0:
        return {"wald": np.nan, "gl": 0, "p_wald": np.nan, "k": 0}
    psi = IF[:, m]
    V = psi.T @ psi / N ** 2
    W = float(theta[m] @ np.linalg.pinv(V) @ theta[m])
    gl = int(np.linalg.matrix_rank(V))
    return {"wald": W, "gl": gl, "p_wald": float(stats.chi2.sf(W, gl)) if gl else np.nan, "k": int(m.sum())}


def estimar_cs(Y: np.ndarray, G: np.ndarray, trat: np.ndarray, xi: np.ndarray, *, e_min: int, e_max: int,
               min_controles: int = MIN_CONTROLES) -> dict:
    coortes = sorted(int(g) for g in np.unique(G[trat]) if g >= 1)
    membro = {g: (G == g) & trat for g in coortes}
    tab, IF = att_gt(Y, G, trat, coortes, e_min=e_min, e_max=e_max, min_controles=min_controles)
    ev, IFe = agregar_evento(tab, IF, membro, e_min=e_min, e_max=e_max)
    th = ev["theta"].to_numpy(dtype=float)
    ok = np.isfinite(th) & np.isfinite(IFe).all(axis=0) & ~ev["referencia"].to_numpy()
    ep = np.full(th.size, np.nan)
    if ok.any():
        ep[ok] = ep_bootstrap(IFe[:, ok], xi)
    ev["ep"] = ep
    ev["ic95_inf"] = th - Z * ep
    ev["ic95_sup"] = th + Z * ep
    ev["p_valor"] = [L.p_normal(a / b) if np.isfinite(a) and np.isfinite(b) and b > 0 else np.nan
                     for a, b in zip(th, ep)]
    e = ev["e"].to_numpy()
    pre = wald_pre(th, IFe, e <= -2)
    post = (e >= 0) & ok
    pos = {"att": np.nan, "ep": np.nan, "ic95_inf": np.nan, "ic95_sup": np.nan, "p_valor": np.nan, "n_e": 0}
    if post.any():
        psi = IFe[:, post].mean(axis=1)
        val = float(th[post].mean())
        epp = float(ep_bootstrap(psi[:, None], xi)[0])
        pos = {"att": val, "ep": epp, "ic95_inf": val - Z * epp, "ic95_sup": val + Z * epp,
               "p_valor": L.p_normal(val / epp) if epp > 0 else np.nan, "n_e": int(post.sum())}
    return {"att_gt": tab, "evento": ev, "pre": pre, "pos": pos, "n_coortes": len(coortes)}


# ---------------------------------------------------------------------------
# 2. Leitura das entradas e montagem do painel médico × mês
# ---------------------------------------------------------------------------

def competencias() -> list[str]:
    g5 = json.loads(G5_RESUMO.read_text(encoding="utf-8"))
    comps = list(g5["competencias_obtidas"])
    if g5.get("competencias_nao_obtidas"):
        raise FalhaValidacao("o a16 tem competências não obtidas; o P4 não preenche meses ausentes da fonte")
    esperadas = [c for c in pd.period_range(COMP_INICIAL[:4] + "-" + COMP_INICIAL[4:],
                                            COMP_FINAL[:4] + "-" + COMP_FINAL[4:], freq="M").strftime("%Y%m")]
    if comps != esperadas:
        raise FalhaValidacao("competências do a16 diferem de 202406–202608")
    if any(c >= LIMITE_EXCLUSIVO for c in comps):
        raise FalhaValidacao("competência >= 202609")
    return comps


def ler_listas() -> tuple[pd.DataFrame, dict]:
    """Listas do PMM-E pela função da X1 (mesmo id_medico); nome, CRM e UF descartados na hora."""
    li, diag = X1M.ler_listas_pmme()
    li = li[["id_medico", "ciclo", "co_cnes", "co_ibge", "cod_curso", "mes_inicio", "fonte_lista",
             "faixa_atracao"]].copy()
    return li, diag


def ler_x1() -> pd.DataFrame:
    return pd.read_parquet(ARQ_X1, columns=["id_medico", "regra_ligacao", "ciclo", "fonte_lista", "co_ibge", "faixa",
                                            "ligado", "b_mesmo_mun_ultimo_pre"])


def conferir_listas_x1(li: pd.DataFrame, x1: pd.DataFrame) -> dict:
    d = x1.merge(li, on="id_medico", how="left", suffixes=("", "_l"), validate="many_to_one")
    if d["ciclo_l"].isna().any():
        raise FalhaValidacao("id_medico da X1 sem registro nas listas reconstruídas")
    dif = {k: int((d[k].astype(str) != d[k + "_l"].astype(str)).sum()) for k in ("ciclo", "co_ibge", "fonte_lista")}
    tem = d["faixa"].notna() & (d["faixa"].astype(str) != "")
    dif["faixa"] = int((d.loc[tem, "faixa"].astype(str) != d.loc[tem, "faixa_atracao"].astype(str)).sum())
    if any(dif.values()):
        raise FalhaValidacao(f"listas reconstruídas não batem com X1_medicos: {dif}")
    return {"registros_x1": int(len(x1)), "diferencas": dif}


def medicos_da_regra(regra: str, li: pd.DataFrame, x1: pd.DataFrame, chaves: pd.DataFrame,
                     comps: list[str]) -> tuple[pd.DataFrame, dict]:
    """Um registro por id_prof: o da lista de ativos (11/09/2026) antes da lista de agosto; depois o início mais
    antigo; depois o menor id_medico (regra fixada antes de abrir os dados por tempo de evento)."""
    c = chaves[(chaves["origem"] == "X1") & (chaves["regra_ligacao"] == regra)][["id_prof", "id_externo"]]
    c = c.rename(columns={"id_externo": "id_medico"})
    xr = x1[x1["regra_ligacao"] == regra][["id_medico", "ligado", "faixa", "b_mesmo_mun_ultimo_pre"]]
    m = c.merge(li, on="id_medico", how="left", validate="one_to_one").merge(xr, on="id_medico", how="left",
                                                                           validate="one_to_one")
    if m["ciclo"].isna().any() or (m["ligado"] != 1).any():
        raise FalhaValidacao(f"{regra}: chave do a16 sem registro ligado na X1")
    m["_ordem_fonte"] = (m["fonte_lista"] != "ativos_2026-09-11").astype(int)
    m = m.sort_values(["id_prof", "_ordem_fonte", "mes_inicio", "id_medico"])
    dup = m[m["id_prof"].duplicated(keep=False)]
    diag = {"registros_ligados": int(len(m)), "medicos_distintos": int(m["id_prof"].nunique()),
            "medicos_com_mais_de_um_registro": int(dup["id_prof"].nunique()),
            "registros_descartados_na_deduplicacao": int(len(m) - m["id_prof"].nunique()),
            "deduplicados_com_ciclo_diferente": int(dup.groupby("id_prof")["ciclo"].nunique().gt(1).sum()),
            "deduplicados_com_inicio_diferente": int(dup.groupby("id_prof")["mes_inicio"].nunique().gt(1).sum())}
    m = m.drop_duplicates("id_prof", keep="first").drop(columns="_ordem_fonte").reset_index(drop=True)
    if (m["mes_inicio"] < comps[0]).any():
        raise FalhaValidacao("início antes de 202406")
    idx = {cmp: i for i, cmp in enumerate(comps)}
    m["G"] = [idx.get(s, -1) for s in m["mes_inicio"]]          # −1: início depois de 202608
    m["tratavel"] = m["ciclo"].isin(CICLOS_TRATADOS) & (m["G"] >= 1)
    b = m["b_mesmo_mun_ultimo_pre"]
    m["origem"] = np.where(b == 1, ORIGENS[1], np.where(b == 0, ORIGENS[0], None))
    diag["por_ciclo"] = {str(k): int(v) for k, v in m["ciclo"].value_counts().sort_index().items()}
    diag["inicio_depois_do_horizonte"] = int((m["G"] < 0).sum())
    diag["tratados_ciclos_1_2"] = int(m["tratavel"].sum())
    diag["ciclos_1_2_sem_origem_x1"] = int((m["tratavel"] & m["origem"].isna()).sum())
    return m.sort_values("id_prof").reset_index(drop=True), diag


def ler_vinculos(comps: list[str]) -> pd.DataFrame:
    v = pd.read_parquet(ARQ_VINC, columns=["id_prof", "competencia", "co_cnes", "co_municipio", "co_cbo",
                                           "tp_sus_nao_sus", "qt_ch_ambulatorial", "qt_ch_hosp_sus", "qt_ch_outros",
                                           "co_natureza_jur"])
    v["competencia"] = v["competencia"].astype(str)
    if (v["competencia"] >= LIMITE_EXCLUSIVO).any() or not set(v["competencia"]) <= set(comps):
        raise FalhaValidacao("vínculo fora de 202406–202608")
    for c in ("id_prof", "co_cnes", "co_municipio", "co_cbo", "tp_sus_nao_sus", "co_natureza_jur"):
        v[c] = v[c].astype("string")
    return v


def painel_medico(m: pd.DataFrame, v: pd.DataFrame, comps: list[str]) -> pd.DataFrame:
    """Outcomes por id_prof × competência. Mês em que o médico não aparece (competência lida) = zero vínculos e
    zero horas, com `com_vinculo_medico = 0`. Hora vazia em algum vínculo deixa as horas do mês ausentes."""
    vv = v.merge(m[["id_prof", "co_cnes", "co_ibge"]].rename(columns={"co_cnes": "cnes_posto",
                                                                     "co_ibge": "ibge_posto"}),
                 on="id_prof", how="inner")
    h = vv["qt_ch_ambulatorial"].astype("Float64") + vv["qt_ch_hosp_sus"].astype("Float64") \
        + vv["qt_ch_outros"].astype("Float64")
    nat = vv["co_natureza_jur"].fillna("").str[:1]
    no_mun = (vv["co_municipio"] == vv["ibge_posto"]).fillna(False).to_numpy()
    no_estab = (vv["co_cnes"] == vv["cnes_posto"]).fillna(False).to_numpy()
    hf = h.astype(float).to_numpy()
    col = {
        "horas_totais": hf,
        "horas_sus": np.where(vv["tp_sus_nao_sus"] == "S", hf, 0.0),
        "horas_nao_sus": np.where(vv["tp_sus_nao_sus"] == "N", hf, 0.0),
        "horas_amb": vv["qt_ch_ambulatorial"].astype(float).to_numpy(),
        "horas_hosp": vv["qt_ch_hosp_sus"].astype(float).to_numpy(),
        "horas_estab_posto": np.where(no_estab, hf, 0.0),
        "horas_mun_posto": np.where(no_mun, hf, 0.0),
        "horas_fora_mun_posto": np.where(~no_mun, hf, 0.0),
        "horas_resto_mun_posto": np.where(no_mun & ~no_estab, hf, 0.0),
        "horas_publico": np.where(nat == "1", hf, 0.0),
        "horas_privado_com_fins": np.where(nat == "2", hf, 0.0),
        "horas_privado_sem_fins": np.where(nat == "3", hf, 0.0),
        "horas_outra_natureza": np.where(~nat.isin(["1", "2", "3"]), hf, 0.0),
        "n_vinc_mun_posto": no_mun.astype(float),
        "_hora_ausente": np.isnan(hf).astype(float),
    }
    base = pd.DataFrame({"id_prof": vv["id_prof"].to_numpy(), "competencia": vv["competencia"].to_numpy(), **col})
    base.loc[base["_hora_ausente"] > 0, [k for k in col if k.startswith("horas")]] = np.nan
    agg = base.groupby(["id_prof", "competencia"], sort=True).sum(min_count=1)
    agg["n_vinculos"] = vv.groupby(["id_prof", "competencia"]).size()
    agg["n_estabelecimentos"] = vv.groupby(["id_prof", "competencia"])["co_cnes"].nunique()
    agg["n_municipios"] = vv.groupby(["id_prof", "competencia"])["co_municipio"].nunique()
    ausente = agg["_hora_ausente"] > 0
    agg.loc[ausente, [k for k in col if k.startswith("horas")]] = np.nan
    grade = pd.MultiIndex.from_product([m["id_prof"].tolist(), comps], names=["id_prof", "competencia"])
    p = agg.reindex(grade)
    p["com_vinculo_medico"] = p["n_vinculos"].notna().astype(float)
    p = p.fillna({c: 0.0 for c in p.columns if c != "com_vinculo_medico" and c != "_hora_ausente"})
    p.loc[ausente.reindex(grade, fill_value=False).to_numpy(), [k for k in col if k.startswith("horas")]] = np.nan
    return p.drop(columns="_hora_ausente").reset_index()


def conferir_com_a16(p: pd.DataFrame) -> dict:
    """O painel refeito dos vínculos tem de reproduzir o painel médico × mês do a16 (fail closed)."""
    a = pd.read_parquet(ARQ_MED)
    a["competencia"] = a["competencia"].astype(str)
    a = a.set_index(["id_prof", "competencia"])
    q = p.set_index(["id_prof", "competencia"])
    a = a.loc[q.index]
    sus = a[["horas_amb_vinc_sus", "horas_hosp_vinc_sus", "horas_outros_vinc_sus"]].astype(float).sum(axis=1)
    nsus = a[["horas_amb_vinc_nao_sus", "horas_hosp_vinc_nao_sus", "horas_outros_vinc_nao_sus"]].astype(float).sum(axis=1)
    pares = {"n_vinculos": a["n_vinculos"], "n_estabelecimentos": a["n_estabelecimentos"],
             "n_municipios": a["n_municipios"], "horas_totais": a["horas_totais"].astype(float),
             "horas_sus": sus, "horas_nao_sus": nsus, "com_vinculo_medico": a["tem_vinculo_medico"].astype(float)}
    dif = {k: int((~np.isclose(q[k].to_numpy(float), ref.to_numpy(float), equal_nan=True)).sum())
           for k, ref in pares.items()}
    if any(dif.values()):
        raise FalhaValidacao(f"painel refeito difere do painel_medico_mes do a16: {dif}")
    return {"linhas_conferidas": int(len(q)), "diferencas": dif}


def matriz(p: pd.DataFrame, m: pd.DataFrame, col: str, comps: list[str]) -> np.ndarray:
    w = p.pivot(index="id_prof", columns="competencia", values=col).reindex(index=m["id_prof"], columns=comps)
    return w.to_numpy(dtype=float)


# ---------------------------------------------------------------------------
# 3. Especificações
# ---------------------------------------------------------------------------

def t41a(regra: str, m: pd.DataFrame, Ys: dict[str, np.ndarray], comps: list[str]) -> list[dict]:
    linhas = []
    G = m["G"].to_numpy()
    T = len(comps)
    bal = (m["mes_inicio"] >= BAL_INICIO[0]) & (m["mes_inicio"] <= BAL_INICIO[1])
    for amostra, (e0, e1), extra in (("completa", E_LONGA, np.ones(len(m), bool)),
                                     ("balanceada", E_PRINC, bal.to_numpy())):
        for ciclo in ("1", "2", "1+2"):
            sel = m["tratavel"].to_numpy() & extra
            if ciclo != "1+2":
                sel &= (m["ciclo"] == int(ciclo)).to_numpy()
            ids = np.flatnonzero(sel)
            for o in OUT_TODOS:
                Y = Ys[o]
                for e in range(e0, e1 + 1):
                    t = G[ids] + e
                    dentro = (t >= 0) & (t < T)
                    y = Y[ids[dentro], t[dentro]]
                    y = y[np.isfinite(y)]
                    n = int(y.size)
                    r = nova_linha(especificacao="T4.1a", regra_ligacao=regra, amostra=amostra,
                                   janela=f"[{e0},{e1}]", grupo_tipo="ciclo", grupo=ciclo, outcome=o, medida="media",
                                   e=e, n_obs=n, unidade=UNIDADE[o])
                    if o in dict((c, 1) for c, _, _ in COMPLEMENTARES):
                        r["nota"] = ROTULO_COMPLEMENTAR
                    if n == 0:
                        r.update(status="SEM_ESTIMATIVA", nota=L._juntar_notas(r["nota"], "sem médico com esse e no "
                                                                               "painel 202406–202608"))
                    else:
                        mu = float(y.mean())
                        ep = float(y.std(ddof=1) / math.sqrt(n)) if n > 1 else np.nan
                        r.update(estimativa=mu, ep=ep, ic95_inf=mu - Z * ep, ic95_sup=mu + Z * ep)
                        if n == 1:
                            r["nota"] = L._juntar_notas(r["nota"], "um médico: sem EP")
                    linhas.append(r)
    return linhas


def linhas_cs(res: dict, *, esp: str, regra: str, janela: str, grupo_tipo: str, grupo: str, o: str,
              bky: bool) -> list[dict]:
    out = []
    comp = o not in OUT_PROTOCOLO
    ev = res["evento"]
    for _, r in ev.iterrows():
        e = int(r["e"])
        lin = nova_linha(especificacao=esp, regra_ligacao=regra, amostra="completa", janela=janela,
                         grupo_tipo=grupo_tipo, grupo=grupo, outcome=o, medida="att_e", e=e,
                         estimativa=r["theta"], ep=r["ep"], ic95_inf=r["ic95_inf"], ic95_sup=r["ic95_sup"],
                         p_valor=r["p_valor"], n_tratados=r["n_tratados"], n_controles=r["n_controles_min"],
                         n_coortes=r["n_coortes"], unidade=UNIDADE[o], nota=r["nota"])
        if r["referencia"]:
            lin.update(status="REFERENCIA", estimativa=0.0, ep=np.nan, ic95_inf=np.nan, ic95_sup=np.nan,
                       p_valor=np.nan)
        elif not np.isfinite(r["theta"]):
            lin["status"] = "SEM_ESTIMATIVA"
        lin["entra_bky"] = bool(bky and not comp and e >= 0 and lin["status"] == "EXECUTADO")
        if comp:
            lin["nota"] = L._juntar_notas(lin["nota"], ROTULO_COMPLEMENTAR)
        if lin["status"] == "EXECUTADO":
            lin["nota"] = L._juntar_notas(lin["nota"], "n_controles = menor número de controles entre as células")
        out.append(lin)
    pr = res["pre"]
    out.append(nova_linha(especificacao=esp, regra_ligacao=regra, amostra="completa", janela=janela,
                          grupo_tipo=grupo_tipo, grupo=grupo, outcome=o, medida="wald_pre", estimativa=pr["wald"],
                          p_valor=pr["p_wald"], n_obs=pr["k"], unidade="estatística qui-quadrado",
                          status="EXECUTADO" if np.isfinite(pr["wald"]) else "SEM_ESTIMATIVA",
                          nota=L._juntar_notas(f"teste conjunto θ(e) = 0 para e <= −2; gl = {pr['gl']}",
                                               ROTULO_COMPLEMENTAR if comp else "")))
    po = res["pos"]
    out.append(nova_linha(especificacao=esp, regra_ligacao=regra, amostra="completa", janela=janela,
                          grupo_tipo=grupo_tipo, grupo=grupo, outcome=o, medida="att_pos_medio",
                          estimativa=po["att"], ep=po["ep"], ic95_inf=po["ic95_inf"], ic95_sup=po["ic95_sup"],
                          p_valor=po["p_valor"], n_obs=po["n_e"], unidade=UNIDADE[o],
                          status="EXECUTADO" if np.isfinite(po["att"]) else "SEM_ESTIMATIVA",
                          nota=L._juntar_notas("média de θ(e) nos e >= 0 definidos; fora do BKY",
                                               ROTULO_COMPLEMENTAR if comp else "")))
    return out


def t41bc(regra: str, m: pd.DataFrame, Ys: dict[str, np.ndarray], xi: np.ndarray) -> tuple[list[dict], dict]:
    linhas, diag = [], {}
    G = m["G"].to_numpy()
    trat = m["tratavel"].to_numpy()
    for o in OUT_TODOS:
        for janela, (e0, e1), bky in (("principal", E_PRINC, True), ("longa", E_LONGA, False)):
            res = estimar_cs(Ys[o], G, trat, xi, e_min=e0, e_max=e1)
            linhas += linhas_cs(res, esp="T4.1b", regra=regra, janela=f"[{e0},{e1}]", grupo_tipo="todos",
                                grupo="ciclos 1 e 2", o=o, bky=bky)
            if o == "horas_totais":
                diag[f"coortes_{janela}"] = res["n_coortes"]
                diag[f"celulas_att_gt_{janela}"] = int(len(res["att_gt"]))
                diag[f"celulas_sem_suporte_{janela}"] = int(res["att_gt"]["att"].isna().sum())
        for k, origem in ORIGENS.items():
            tr = trat & (m["origem"] == origem).to_numpy()
            res = estimar_cs(Ys[o], G, tr, xi, e_min=E_PRINC[0], e_max=E_PRINC[1])
            linhas += linhas_cs(res, esp="T4.1c", regra=regra, janela=f"[{E_PRINC[0]},{E_PRINC[1]}]",
                                grupo_tipo="origem", grupo=origem, o=o, bky=True)
    return linhas, diag


def media_ic(x: np.ndarray) -> tuple[float, float, float, float]:
    x = x[np.isfinite(x)]
    n = x.size
    if n == 0:
        return np.nan, np.nan, np.nan, np.nan
    mu = float(x.mean())
    ep = float(x.std(ddof=1) / math.sqrt(n)) if n > 1 else np.nan
    return mu, ep, mu - Z * ep, mu + Z * ep


def razao_ic(a: np.ndarray, b: np.ndarray, semente: int) -> tuple[float, float, float]:
    """−Σa/Σb com IC percentil do bootstrap multiplicador (Mammen) por médico."""
    n = a.size
    Sa, Sb = a.sum(), b.sum()
    if n < 2 or Sb <= 0:
        return np.nan, np.nan, np.nan
    xi = pesos_mammen(B_BOOT, n, semente)
    Sa_b = Sa + xi @ (a - a.mean())
    Sb_b = Sb + xi @ (b - b.mean())
    r = -Sa_b / Sb_b
    lo, hi = np.percentile(r[np.isfinite(r)], [2.5, 97.5])
    return float(-Sa / Sb), float(lo), float(hi)


def wilson(k: int, n: int) -> tuple[float, float, float]:
    if n == 0:
        return np.nan, np.nan, np.nan
    p = k / n
    d = 1 + Z ** 2 / n
    c = (p + Z ** 2 / (2 * n)) / d
    h = Z * math.sqrt(p * (1 - p) / n + Z ** 2 / (4 * n ** 2)) / d
    return p, c - h, c + h


def janela_media(Y: np.ndarray, G: np.ndarray, ids: np.ndarray, e0: int, e1: int) -> np.ndarray:
    T = Y.shape[1]
    out = np.full(ids.size, np.nan)
    for j, i in enumerate(ids):
        ts = [G[i] + e for e in range(e0, e1 + 1) if 0 <= G[i] + e < T]
        y = Y[i, ts] if ts else np.array([])
        out[j] = np.nanmean(y) if np.isfinite(y).any() else np.nan
    return out


def origem_desc(regra: str, m: pd.DataFrame, Ys: dict[str, np.ndarray]) -> tuple[list[dict], dict]:
    linhas = []
    G = m["G"].to_numpy()
    trat = m["tratavel"].to_numpy()
    ids_all = np.flatnonzero(trat)
    vm1 = np.array([Ys["n_vinc_mun_posto"][i, G[i] - 1] for i in ids_all])
    cv1 = np.array([Ys["com_vinculo_medico"][i, G[i] - 1] for i in ids_all])
    info = {}
    grupos = [("todos", "ciclos 1 e 2", np.ones(ids_all.size, bool))]
    grupos += [("ciclo", str(k), (m["ciclo"].to_numpy()[ids_all] == k)) for k in CICLOS_TRATADOS]
    grupos += [("faixa", f, (m["faixa"].to_numpy()[ids_all] == f)) for f in ("FAIXA 1", "FAIXA 2", "FAIXA 3")]
    for gt, g, sel in grupos:
        o = m["origem"].to_numpy()[ids_all][sel]
        n_def = int(pd.notna(o).sum())
        for nome, k, n, nota in (
                ("fracao_ja_no_municipio_x1b", int((o == ORIGENS[1]).sum()), n_def,
                 "X1 b: vínculo médico no município do posto na última competência pré-início (seis competências)"),
                ("fracao_novos_x1b", int((o == ORIGENS[0]).sum()), n_def, "1 − X1 b"),
                ("fracao_no_municipio_em_e_menos_1", int((vm1[sel] > 0).sum()), int(sel.sum()),
                 "painel mensal do a16: vínculo médico no município do posto no mês antes do início (complementar)"),
                ("fracao_sem_vinculo_medico_em_e_menos_1", int((cv1[sel] == 0).sum()), int(sel.sum()),
                 "painel mensal do a16: sem vínculo médico cadastrado no mês antes do início (complementar)")):
            p, lo, hi = wilson(k, n)
            linhas.append(nova_linha(especificacao="origem", regra_ligacao=regra, amostra="completa",
                                     grupo_tipo=gt, grupo=g, outcome=nome, medida="fracao", estimativa=p,
                                     ic95_inf=lo, ic95_sup=hi, n_obs=n, unidade="fração",
                                     nota=L._juntar_notas(nota, f"{k} de {n}; IC de Wilson"),
                                     status="EXECUTADO" if n else "SEM_ESTIMATIVA"))
            if gt == "todos":
                info[nome] = {"k": k, "n": n, "fracao": p}
        if gt == "todos":
            info["sem_origem_x1"] = int(sel.sum() - n_def)
    return linhas, info


def t42(regra: str, m: pd.DataFrame, v: pd.DataFrame, comps: list[str], nac: pd.DataFrame) -> tuple[list[dict], dict]:
    """Quem mudou: novo no município (X1 b = 0) com vínculo médico em outro município no mês antes do início."""
    G = m["G"].to_numpy()
    T = len(comps)
    idx = {c: i for i, c in enumerate(comps)}
    v = v.copy()
    v["t"] = v["competencia"].map(idx)
    v["h"] = (v["qt_ch_ambulatorial"].astype(float) + v["qt_ch_hosp_sus"].astype(float)
              + v["qt_ch_outros"].astype(float))
    mm = m[m["tratavel"] & (m["origem"] == ORIGENS[0])][["id_prof", "G", "co_ibge"]]
    v = v.merge(mm, on="id_prof", how="inner")
    v["e"] = v["t"] - v["G"]
    orig = v[(v["e"] == -1) & (v["co_municipio"] != v["co_ibge"])]
    pares = orig[["id_prof", "co_municipio", "co_cbo"]].drop_duplicates()
    movers = pares["id_prof"].unique()
    grupos_nac = set(nac["grupo"].unique())
    nac_i = nac.set_index(["co_ibge", "grupo", "competencia"])["horas_totais"]
    reg = []
    for (pid, mun, cbo) in pares.sort_values(["id_prof", "co_municipio", "co_cbo"]).itertuples(index=False):
        g = int(mm.loc[mm["id_prof"] == pid, "G"].iloc[0])
        pre_t = [g + e for e in range(-6, 0) if 0 <= g + e < T]
        pos_t = [g + e for e in range(0, 7) if 0 <= g + e < T]
        vv = v[(v["id_prof"] == pid) & (v["co_municipio"] == mun) & (v["co_cbo"] == cbo)]
        hs = vv.groupby("t")["h"].sum()
        pre_own = float(np.mean([hs.get(t, 0.0) for t in pre_t]))
        pos_own = float(np.mean([hs.get(t, 0.0) for t in pos_t]))
        grupo = f"cbo_{cbo}" if f"cbo_{cbo}" in grupos_nac else ("mfc_225130" if cbo == "225130" else None)
        d_nac, motivo = np.nan, ""
        if grupo is None:
            motivo = "CBO sem série própria no painel do a09"
        else:
            serie = [nac_i.get((mun, grupo, comps[t]), np.nan) for t in pre_t + pos_t]
            if any(pd.isna(s) for s in serie):
                motivo = "horas ausentes no painel do a09 em algum mês"
            else:
                s = np.array(serie, dtype=float)
                d_nac = float(s[len(pre_t):].mean() - s[:len(pre_t)].mean())
        reg.append({"id_prof": pid, "d_own": pos_own - pre_own, "pre_own": pre_own, "pos_own": pos_own,
                    "d_nac": d_nac, "motivo": motivo})
    r = pd.DataFrame(reg, columns=["id_prof", "d_own", "pre_own", "pos_own", "d_nac", "motivo"])
    linhas, info = [], {"novos_ciclos_1_2": int(len(mm)), "mudaram_com_origem_em_e_menos_1": int(len(movers)),
                        "pares_medico_municipio_cbo": int(len(r)),
                        "pares_sem_serie_a09": {k: int(v_) for k, v_ in r["motivo"].value_counts().items() if k}}
    base = dict(especificacao="T4.2", regra_ligacao=regra, amostra="completa", janela="pré [-6,-1] × pós [0,6]",
                grupo_tipo="mudaram", grupo="novos no município com vínculo em outro município em e = −1",
                unidade="h/sem")
    if len(r) == 0:
        linhas.append(nova_linha(**base, outcome="horas_deixadas_na_origem", medida="media_por_medico",
                                 status="SEM_ESTIMATIVA", nota="nenhum médico que mudou"))
        return linhas, info
    por_med = r.groupby("id_prof").agg(d_own=("d_own", "sum"), pre_own=("pre_own", "sum"),
                                       pos_own=("pos_own", "sum"))
    for nome, x, nota in (("horas_na_origem_pre", por_med["pre_own"].to_numpy(), "média por médico das horas nos "
                           "municípios de origem (pré); soma sobre os pares município × CBO de e = −1"),
                          ("horas_na_origem_pos", por_med["pos_own"].to_numpy(), "idem no pós"),
                          ("delta_horas_na_origem", por_med["d_own"].to_numpy(), "pós − pré; negativo = horas que o "
                           "médico deixou na origem")):
        mu, ep, lo, hi = media_ic(x)
        linhas.append(nova_linha(**base, outcome=nome, medida="media_por_medico", estimativa=mu, ep=ep, ic95_inf=lo,
                                 ic95_sup=hi, n_obs=int(np.isfinite(x).sum()), nota=nota))
    k = int((por_med["pos_own"] > 0).sum())
    p, lo, hi = wilson(k, len(por_med))
    linhas.append(nova_linha(**{**base, "unidade": "fração"}, outcome="fracao_mantem_horas_na_origem",
                             medida="fracao", estimativa=p, ic95_inf=lo, ic95_sup=hi, n_obs=len(por_med),
                             nota=f"médicos com horas na origem no pós (média > 0): {k} de {len(por_med)}; Wilson"))
    rr = r[np.isfinite(r["d_nac"])].copy()
    rr["d_outros"] = rr["d_nac"] - rr["d_own"]
    for nome, col, nota in (("delta_horas_cbo_municipio_origem", "d_nac", "variação pós − pré das horas totais da "
                             "mesma CBO no município de origem (CNES nacional, a09), por par médico × município × CBO"),
                            ("delta_horas_cbo_origem_sem_o_medico", "d_outros", "a mesma variação menos a do próprio "
                             "médico: as horas dos outros médicos da CBO no município de origem"),
                            ("delta_horas_do_medico_no_par", "d_own", "variação das horas do próprio médico nos "
                             "mesmos pares (conferência)")):
        mu, ep, lo, hi = media_ic(rr[col].to_numpy())
        linhas.append(nova_linha(**{**base, "grupo": "pares médico × município de origem × CBO com série no a09"},
                                 outcome=nome, medida="media_por_par", estimativa=mu, ep=ep, ic95_inf=lo,
                                 ic95_sup=hi, n_obs=int(len(rr)),
                                 nota=L._juntar_notas(nota, "IC ignora a repetição do mesmo município entre pares")))
    info["pares_com_serie_a09"] = int(len(rr))
    return linhas, info


ROTULO_T42 = {
    "horas_na_origem_pre": "horas do médico nos municípios de origem, pré",
    "horas_na_origem_pos": "horas do médico nos municípios de origem, pós",
    "delta_horas_na_origem": "variação das horas do médico na origem (pós − pré)",
    "fracao_mantem_horas_na_origem": "fração com horas na origem em algum mês de 0 a +6 (critério frouxo)",
    "delta_horas_cbo_municipio_origem": "variação das horas da mesma CBO no município de origem (a09)",
    "delta_horas_cbo_origem_sem_o_medico": "a mesma variação sem as horas do próprio médico",
    "delta_horas_do_medico_no_par": "variação das horas do médico nesses pares (conferência)",
}

COMPONENTES_T43 = [("horas_estab_posto", "Δ estabelecimento do posto"),
                   ("horas_resto_mun_posto", "Δ resto do município do posto"),
                   ("horas_mun_posto", "Δ município do posto"),
                   ("horas_fora_mun_posto", "Δ fora do município do posto"),
                   ("horas_totais", "saldo (Δ município do posto + Δ fora)")]


def t43(regra: str, m: pd.DataFrame, Ys: dict[str, np.ndarray], cursos: dict[int, str]) -> tuple[list[dict], dict]:
    G = m["G"].to_numpy()
    linhas, info = [], {}
    bal = ((m["mes_inicio"] >= BAL_INICIO[0]) & (m["mes_inicio"] <= BAL_INICIO[1])).to_numpy()
    for amostra, extra in (("completa", np.ones(len(m), bool)), ("balanceada", bal)):
        ids = np.flatnonzero(m["tratavel"].to_numpy() & extra)
        d = {}
        for o, _ in COMPONENTES_T43:
            d[o] = janela_media(Ys[o], G, ids, 0, 6) - janela_media(Ys[o], G, ids, -6, -1)
        soma = d["horas_mun_posto"] + d["horas_fora_mun_posto"]
        if not np.allclose(soma, d["horas_totais"], equal_nan=True):
            raise FalhaValidacao("T4.3: Δ município + Δ fora difere de Δ total")
        sub = m.iloc[ids]
        grupos = [("todos", "ciclos 1 e 2", np.ones(ids.size, bool))]
        grupos += [("ciclo", str(k), (sub["ciclo"] == k).to_numpy()) for k in CICLOS_TRATADOS]
        grupos += [("faixa", f, (sub["faixa"] == f).to_numpy()) for f in ("FAIXA 1", "FAIXA 2", "FAIXA 3")]
        grupos += [("origem", o, (sub["origem"] == o).to_numpy()) for o in ORIGENS.values()]
        grupos += [("curso", f"{c:02d} {cursos.get(c, 'curso ' + str(c))}", (sub["cod_curso"] == c).to_numpy())
                   for c in sorted(sub["cod_curso"].unique())]
        for gt, g, sel in grupos:
            n = int(sel.sum())
            base = dict(especificacao="T4.3", regra_ligacao=regra, amostra=amostra, janela="pré [-6,-1] × pós [0,6]",
                        grupo_tipo=gt, grupo=g, n_obs=n, unidade="h/sem")
            for o, rot in COMPONENTES_T43:
                x = d[o][sel]
                linhas.append(nova_linha(**base, outcome=f"delta_{o}", medida="soma", estimativa=float(np.nansum(x)),
                                         nota=f"{rot}; soma sobre os médicos das médias pós − pré"))
                mu, ep, lo, hi = media_ic(x)
                linhas.append(nova_linha(**base, outcome=f"delta_{o}", medida="media_por_medico", estimativa=mu,
                                         ep=ep, ic95_inf=lo, ic95_sup=hi,
                                         status="EXECUTADO" if n else "SEM_ESTIMATIVA",
                                         nota=f"{rot}; média por médico" + ("; um médico: sem EP" if n == 1 else "")))
            fr, lo, hi = razao_ic(d["horas_fora_mun_posto"][sel], d["horas_mun_posto"][sel], SEMENTE)
            linhas.append(nova_linha(**{**base, "unidade": "fração"}, outcome="fracao_do_ganho_compensada_fora",
                                     medida="razao", estimativa=fr, ic95_inf=lo, ic95_sup=hi,
                                     status="EXECUTADO" if np.isfinite(fr) else "SEM_ESTIMATIVA",
                                     nota="−ΣΔ fora / ΣΔ município do posto; IC percentil do bootstrap multiplicador "
                                          "por médico" + ("" if np.isfinite(fr) else
                                                          "; sem ganho positivo no município ou n < 2")))
            if gt == "todos":
                info[amostra] = {"n": n, "soma_delta_mun_posto": float(np.nansum(d["horas_mun_posto"][sel])),
                                 "soma_delta_fora": float(np.nansum(d["horas_fora_mun_posto"][sel])),
                                 "soma_saldo": float(np.nansum(d["horas_totais"][sel]))}
    return linhas, info


def aplicar_bky(est: pd.DataFrame) -> pd.DataFrame:
    est = est.copy()
    for (esp, regra), _ in est[est["entra_bky"]].groupby(["especificacao", "regra_ligacao"]):
        sel = est["entra_bky"] & (est["especificacao"] == esp) & (est["regra_ligacao"] == regra)
        est.loc[sel, "q_bky"] = L.qvalores_bky(est.loc[sel, "p_valor"].to_numpy(float))
    return est


# ---------------------------------------------------------------------------
# 4. Execução das especificações
# ---------------------------------------------------------------------------

def ler_cursos() -> dict[int, str]:
    d = json.loads(PONTE.read_text(encoding="utf-8"))
    return {int(c["cod_curso"]): str(c["especialidade_cfm"]) for c in d["catalogo_cursos"]}


def ler_nacional(municipios: set[str]) -> pd.DataFrame:
    nac = pd.read_parquet(ARQ_NAC, columns=["co_ibge", "competencia", "grupo", "horas_totais"],
                          filters=[("competencia", ">=", COMP_INICIAL), ("competencia", "<", LIMITE_EXCLUSIVO)])
    nac["co_ibge"] = nac["co_ibge"].astype(str)
    nac["competencia"] = nac["competencia"].astype(str)
    if (nac["competencia"] >= LIMITE_EXCLUSIVO).any():
        raise FalhaValidacao("a09 com competência >= 202609")
    return nac[nac["co_ibge"].isin(municipios)].reset_index(drop=True)


def carregar() -> dict:
    comps = competencias()
    li, diag_listas = ler_listas()
    x1 = ler_x1()
    conf_x1 = conferir_listas_x1(li, x1)
    chaves = pd.read_parquet(ARQ_CHAVES)
    v = ler_vinculos(comps)
    return {"comps": comps, "li": li, "x1": x1, "chaves": chaves, "v": v, "cursos": ler_cursos(),
            "diag_listas": diag_listas, "conf_x1": conf_x1}


def estimar_regra(regra: str, dados: dict) -> tuple[list[dict], dict]:
    comps = dados["comps"]
    m, diag_m = medicos_da_regra(regra, dados["li"], dados["x1"], dados["chaves"], comps)
    p = painel_medico(m, dados["v"], comps)
    conf = conferir_com_a16(p)
    Ys = {c: matriz(p, m, c, comps) for c in OUT_TODOS + ["n_vinc_mun_posto"]}
    xi = pesos_mammen(B_BOOT, len(m), SEMENTE)
    linhas = t41a(regra, m, Ys, comps)
    l_bc, diag_cs = t41bc(regra, m, Ys, xi)
    del xi
    linhas += l_bc
    l_or, info_or = origem_desc(regra, m, Ys)
    linhas += l_or
    nac = ler_nacional(set(dados["v"]["co_municipio"].dropna().astype(str)))
    l42, info42 = t42(regra, m, dados["v"], comps, nac)
    linhas += l42
    l43, info43 = t43(regra, m, Ys, dados["cursos"])
    linhas += l43
    sem_vinc = {str(e): None for e in range(E_PRINC[0], E_PRINC[1] + 1)}
    G = m["G"].to_numpy()
    ids = np.flatnonzero(m["tratavel"].to_numpy())
    for e in range(E_PRINC[0], E_PRINC[1] + 1):
        t = G[ids] + e
        ok = (t >= 0) & (t < len(comps))
        cv = Ys["com_vinculo_medico"][ids[ok], t[ok]]
        sem_vinc[str(e)] = {"medicos": int(ok.sum()), "sem_vinculo_medico": int((cv == 0).sum())}
    info = {"medicos": diag_m, "conferencia_a16": conf, "cs": diag_cs, "origem": info_or, "t42": info42,
            "t43": info43, "meses_sem_vinculo_medico_por_e": sem_vinc,
            "horas_ausentes_medico_mes": int(np.isnan(Ys["horas_totais"]).sum())}
    return linhas, info


# ---------------------------------------------------------------------------
# 5. Figuras (sem texto embutido; o "Como ler" fica no doc e no resumo)
# ---------------------------------------------------------------------------

COR = ["#2a78d6", "#eb6834", "#1baf7a"]
COR_TEXTO = "#52514e"

COMO_LER = {
    "P4_T41a_medias_evento.png": "Cada linha mostra, mês a mês em torno do início no programa, a média das horas "
                                 "cadastradas pelos médicos de um ciclo. O mês 0 é o do início; a faixa clara é o "
                                 "intervalo de 95%.",
    "P4_T41b_evento_horas.png": "Cada ponto compara a variação das horas de quem já começou com a de quem ainda vai "
                                "começar, a cada mês desde o início; o mês −1 é a referência e vale zero. Pontos "
                                "antes do mês 0 perto de zero dão mais confiança na comparação.",
    "P4_T41b_evento_tipo.png": "Mesma leitura da figura anterior, para horas em vínculos SUS e não SUS e em "
                               "estabelecimentos públicos e privados com fins lucrativos.",
    "P4_T41c_origem.png": "A mesma comparação, separando quem já tinha vínculo no município do posto antes de "
                          "começar (azul) de quem chegou de fora ou sem vínculo (laranja).",
    "P4_T43_contabilidade.png": "Barras: variação média, por médico, das horas cadastradas no estabelecimento do "
                                "posto, no resto do município do posto e fora dele, entre os seis meses antes e os "
                                "sete a partir do início; o losango é o saldo. Não há grupo de comparação.",
}
DESCRICAO_FIGURAS = {
    "P4_T41a_medias_evento.png": "T4.1a: médias por tempo de evento, ciclos 1 e 2, amostra completa, regra D1",
    "P4_T41b_evento_horas.png": "T4.1b: θ(e) das horas totais, no município do posto e fora dele, regra D1",
    "P4_T41b_evento_tipo.png": "T4.1b: θ(e) das horas SUS, não SUS, públicas e privadas com fins, regra D1",
    "P4_T41c_origem.png": "T4.1c: θ(e) das horas no município do posto e totais, por origem, regra D1",
    "P4_T43_contabilidade.png": "T4.3: componentes da contabilidade líquida por faixa e no total, regra D1",
}


def _eixo(ax, ylabel: str, xlabel: str = "meses desde o início") -> None:
    ax.axhline(0, color="#b5b4ae", lw=0.8, zorder=0)
    ax.grid(axis="y", color="#e6e5e0", lw=0.6)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.set_ylabel(ylabel, color=COR_TEXTO, fontsize=9)
    ax.set_xlabel(xlabel, color=COR_TEXTO, fontsize=9)
    ax.tick_params(colors=COR_TEXTO, labelsize=8)
    ax.set_axisbelow(True)


def _sel(est: pd.DataFrame, **f) -> pd.DataFrame:
    s = est
    for k, val in f.items():
        s = s[s[k] == val]
    return s


def gerar_figuras(est: pd.DataFrame, dir_fig: Path) -> list[dict]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "DejaVu Sans", "svg.hashsalt": "p4"})
    dir_fig.mkdir(parents=True, exist_ok=True)
    regra = REGRAS[0]
    figs = []

    def salvar(fig, nome):
        caminho = dir_fig / nome
        fig.savefig(caminho, dpi=150, bbox_inches="tight", metadata={"Software": None})
        plt.close(fig)
        figs.append({"arquivo": rotulo(caminho), "descricao": DESCRICAO_FIGURAS[nome], "como_ler": COMO_LER[nome]})

    # T4.1a
    fig, axs = plt.subplots(1, 3, figsize=(11, 3.4), sharex=True)
    for ax, o in zip(axs, ("horas_totais", "horas_mun_posto", "horas_fora_mun_posto")):
        for j, ciclo in enumerate(("1", "2")):
            s = _sel(est, especificacao="T4.1a", regra_ligacao=regra, amostra="completa", grupo=ciclo, outcome=o)
            s = s[s["status"] == "EXECUTADO"].sort_values("e")
            ax.plot(s["e"], s["estimativa"], color=COR[j], lw=2, marker="o", ms=3, label=f"ciclo {ciclo}")
            ax.fill_between(s["e"], s["ic95_inf"], s["ic95_sup"], color=COR[j], alpha=0.15, lw=0)
        ax.axvline(-0.5, color="#b5b4ae", ls="--", lw=0.8)
        _eixo(ax, f"{ROTULO[o]} (h/sem)")
        ax.set_ylim(bottom=0)
    axs[0].legend(frameon=False, fontsize=8)
    salvar(fig, "P4_T41a_medias_evento.png")

    def painel_cs(ax, o, esp="T4.1b", grupos=(("todos", "ciclos 1 e 2"),)):
        for j, (gt, g) in enumerate(grupos):
            s = _sel(est, especificacao=esp, regra_ligacao=regra, janela=f"[{E_PRINC[0]},{E_PRINC[1]}]",
                     grupo=g, outcome=o, medida="att_e")
            s = s[s["status"].isin(["EXECUTADO", "REFERENCIA"])].sort_values("e")
            x = s["e"].to_numpy(float) + (j - (len(grupos) - 1) / 2) * 0.18
            ax.errorbar(x, s["estimativa"], yerr=[s["estimativa"] - s["ic95_inf"], s["ic95_sup"] - s["estimativa"]],
                        fmt="o", ms=4, color=COR[j], ecolor=COR[j], elinewidth=1.2, capsize=0,
                        label=ROTULO_ORIGEM.get(g, g))
        ax.axvline(-0.5, color="#b5b4ae", ls="--", lw=0.8)
        _eixo(ax, f"{ROTULO[o]} (h/sem)")

    fig, axs = plt.subplots(1, 3, figsize=(11, 3.4), sharex=True)
    for ax, o in zip(axs, ("horas_totais", "horas_mun_posto", "horas_fora_mun_posto")):
        painel_cs(ax, o)
    salvar(fig, "P4_T41b_evento_horas.png")

    fig, axs = plt.subplots(2, 2, figsize=(9, 6), sharex=True)
    for ax, o in zip(axs.ravel(), ("horas_sus", "horas_nao_sus", "horas_publico", "horas_privado_com_fins")):
        painel_cs(ax, o)
    salvar(fig, "P4_T41b_evento_tipo.png")

    fig, axs = plt.subplots(1, 2, figsize=(9, 3.4), sharex=True)
    for ax, o in zip(axs, ("horas_mun_posto", "horas_totais")):
        painel_cs(ax, o, esp="T4.1c", grupos=tuple(("origem", g) for g in ORIGENS.values()))
    axs[0].legend(frameon=False, fontsize=8)
    salvar(fig, "P4_T41c_origem.png")

    fig, ax = plt.subplots(figsize=(8, 3.6))
    grupos = ["FAIXA 1", "FAIXA 2", "FAIXA 3", "ciclos 1 e 2"]
    comps = [("horas_estab_posto", "estabelecimento do posto"), ("horas_resto_mun_posto", "resto do município"),
             ("horas_fora_mun_posto", "fora do município")]
    for j, (o, rot) in enumerate(comps):
        vals = []
        for g in grupos:
            s = _sel(est, especificacao="T4.3", regra_ligacao=regra, amostra="completa", grupo=g,
                     outcome=f"delta_{o}", medida="media_por_medico")
            vals.append(float(s["estimativa"].iloc[0]))
        ax.bar(np.arange(len(grupos)) + (j - 1) * 0.25, vals, width=0.23, color=COR[j], label=rot)
    sal = [float(_sel(est, especificacao="T4.3", regra_ligacao=regra, amostra="completa", grupo=g,
                      outcome="delta_horas_totais", medida="media_por_medico")["estimativa"].iloc[0]) for g in grupos]
    ax.scatter(np.arange(len(grupos)), sal, marker="D", s=40, color="#0b0b0b", zorder=3, label="saldo")
    ax.set_xticks(np.arange(len(grupos)), ["faixa 1", "faixa 2", "faixa 3", "todos"])
    _eixo(ax, "variação média por médico (h/sem)", xlabel="")
    ax.legend(frameon=False, fontsize=8, ncol=4, loc="lower center", bbox_to_anchor=(0.5, 1.0))
    salvar(fig, "P4_T43_contabilidade.png")
    for f in figs:
        f["sha256"] = sha256(ROOT / f["arquivo"])
    return figs


# ---------------------------------------------------------------------------
# 6. Documento 57d, gerado inteiro a partir das saídas
# ---------------------------------------------------------------------------

def _n(v, casas: int = 1, sinal: bool = False) -> str:
    if v is None or (isinstance(v, float) and not np.isfinite(v)) or pd.isna(v):
        return "—"
    s = f"{v:+,.{casas}f}" if sinal else f"{v:,.{casas}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def _pct(v, casas: int = 1) -> str:
    return "—" if v is None or not np.isfinite(v) else _n(100 * v, casas) + "%"


def _ic(r, casas: int = 1, pct: bool = False) -> str:
    if pct:
        return f"[{_pct(r['ic95_inf'], casas)}; {_pct(r['ic95_sup'], casas)}]"
    return f"[{_n(r['ic95_inf'], casas, True)}; {_n(r['ic95_sup'], casas, True)}]"


def _p(v) -> str:
    if v is None or pd.isna(v):
        return "—"
    return "< 0,001" if v < 0.001 else _n(v, 3)


def _p_pre(v) -> str:
    """p do teste dos pré; em negrito e com rótulo quando rejeita zero (p < 0,05)."""
    if v is None or pd.isna(v):
        return "—"
    return f"**{_p(v)} (rejeita)**" if v < 0.05 else _p(v)


def _i(v) -> str:
    return "—" if v is None or pd.isna(v) else _n(float(v), 0)


def _tab(cab: list[str], linhas: list[list[str]]) -> str:
    return "\n".join(["| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)] + ["| " + " | ".join(l) + " |"
                                                                              for l in linhas])


def _um(est, **f) -> pd.Series:
    s = _sel(est, **f)
    if len(s) != 1:
        raise FalhaValidacao(f"esperada uma linha para {f}, há {len(s)}")
    return s.iloc[0]


def _exclui_zero(r) -> bool:
    return np.isfinite(r["ic95_inf"]) and (r["ic95_inf"] > 0 or r["ic95_sup"] < 0)


def tabela_origem(est, regra) -> str:
    linhas = []
    for gt, g in [("todos", "ciclos 1 e 2"), ("ciclo", "1"), ("ciclo", "2"), ("faixa", "FAIXA 1"),
                  ("faixa", "FAIXA 2"), ("faixa", "FAIXA 3")]:
        a = _um(est, especificacao="origem", regra_ligacao=regra, grupo_tipo=gt, grupo=g,
                outcome="fracao_ja_no_municipio_x1b")
        b = _um(est, especificacao="origem", regra_ligacao=regra, grupo_tipo=gt, grupo=g, outcome="fracao_novos_x1b")
        c = _um(est, especificacao="origem", regra_ligacao=regra, grupo_tipo=gt, grupo=g,
                outcome="fracao_no_municipio_em_e_menos_1")
        d = _um(est, especificacao="origem", regra_ligacao=regra, grupo_tipo=gt, grupo=g,
                outcome="fracao_sem_vinculo_medico_em_e_menos_1")
        linhas.append([g.replace("FAIXA", "faixa"), _i(a["n_obs"]), f"{_pct(a['estimativa'])} {_ic(a, pct=True)}",
                       f"{_pct(b['estimativa'])} {_ic(b, pct=True)}", f"{_pct(c['estimativa'])} {_ic(c, pct=True)}",
                       f"{_pct(d['estimativa'])}"])
    return _tab(["Grupo", "Médicos com X1 b", "Já no município (X1 b)", "Novos (1 − X1 b)",
                 "No município no mês −1 (painel mensal)", "Sem vínculo médico no mês −1"], linhas)


def tabela_t41a(est, regra) -> str:
    linhas = []
    for ciclo in ("1", "2"):
        for o in ("horas_totais", "horas_mun_posto", "horas_fora_mun_posto", "n_vinculos", "com_vinculo_medico"):
            cel = []
            for e in (-6, -1, 0, 3, 6):
                r = _um(est, especificacao="T4.1a", regra_ligacao=regra, amostra="completa", grupo=ciclo, outcome=o,
                        e=e)
                casas = 2 if o in ("n_vinculos", "com_vinculo_medico") else 1
                cel.append(f"{_n(r['estimativa'], casas)} (n = {_i(r['n_obs'])})")
            linhas.append([ciclo, ROTULO[o]] + cel)
    return _tab(["Ciclo", "Outcome", "e = −6", "e = −1", "e = 0", "e = +3", "e = +6"], linhas)


def tabela_t41b(est, regra, esp="T4.1b", grupo="ciclos 1 e 2") -> str:
    linhas = []
    jan = f"[{E_PRINC[0]},{E_PRINC[1]}]"
    for o in OUT_PROTOCOLO:
        pos = _um(est, especificacao=esp, regra_ligacao=regra, janela=jan, grupo=grupo, outcome=o,
                  medida="att_pos_medio")
        e0 = _um(est, especificacao=esp, regra_ligacao=regra, janela=jan, grupo=grupo, outcome=o, medida="att_e", e=0)
        e6 = _um(est, especificacao=esp, regra_ligacao=regra, janela=jan, grupo=grupo, outcome=o, medida="att_e", e=6)
        pre = _um(est, especificacao=esp, regra_ligacao=regra, janela=jan, grupo=grupo, outcome=o, medida="wald_pre")
        casas = 2 if UNIDADE[o] != "h/sem" else 1
        q6 = "—" if not np.isfinite(e6["q_bky"]) else _n(e6["q_bky"], 3)
        linhas.append([ROTULO[o], f"{_n(e0['estimativa'], casas, True)} {_ic(e0, casas)}",
                       f"{_n(e6['estimativa'], casas, True)} {_ic(e6, casas)}", q6,
                       f"{_n(pos['estimativa'], casas, True)} {_ic(pos, casas)}", _p_pre(pre["p_valor"])])
    return _tab(["Outcome", "θ(0) [IC 95%]", "θ(+6) [IC 95%]", "q BKY de θ(+6)", "média de θ(0..+6) [IC 95%]",
                 "p do pré (Wald)"], linhas)


def tabela_t41c(est, regra) -> str:
    linhas = []
    jan = f"[{E_PRINC[0]},{E_PRINC[1]}]"
    for o in ("horas_totais", "horas_sus", "horas_nao_sus", "horas_estab_posto", "horas_mun_posto",
              "horas_fora_mun_posto", "n_vinculos", "n_municipios"):
        cel = [ROTULO[o]]
        for g in ORIGENS.values():
            pos = _um(est, especificacao="T4.1c", regra_ligacao=regra, janela=jan, grupo=g, outcome=o,
                      medida="att_pos_medio")
            pre = _um(est, especificacao="T4.1c", regra_ligacao=regra, janela=jan, grupo=g, outcome=o,
                      medida="wald_pre")
            casas = 2 if UNIDADE[o] != "h/sem" else 1
            cel += [f"{_n(pos['estimativa'], casas, True)} {_ic(pos, casas)}", _p_pre(pre["p_valor"])]
        linhas.append(cel)
    return _tab(["Outcome", "já no município: média θ(0..+6)", "p do pré", "novos: média θ(0..+6)", "p do pré"], linhas)


def tabela_bky(est) -> str:
    linhas = []
    for regra in REGRAS:
        for esp in ("T4.1b", "T4.1c"):
            s = est[(est["especificacao"] == esp) & (est["regra_ligacao"] == regra) & est["entra_bky"]]
            linhas.append([ROTULO_REGRA[regra], esp, _i(len(s)), _i((s["p_valor"] < 0.05).sum()),
                           _i((s["q_bky"] <= 0.05).sum()), _i((s["q_bky"] <= 0.10).sum())])
    return _tab(["Regra", "Especificação", "Linhas no BKY", "p < 0,05", "q <= 0,05", "q <= 0,10"], linhas)


def tabela_t42(est, regra) -> str:
    s = est[(est["especificacao"] == "T4.2") & (est["regra_ligacao"] == regra)]
    linhas = []
    for _, r in s.iterrows():
        val = _pct(r["estimativa"]) if r["unidade"] == "fração" else _n(r["estimativa"], 1, True)
        ic = _ic(r, pct=r["unidade"] == "fração")
        linhas.append([ROTULO_T42[r["outcome"]], r["medida"].replace("_", " "), _i(r["n_obs"]), f"{val} {ic}"])
    return _tab(["Quantidade", "Medida", "n", "Valor [IC 95%]"], linhas)


def tabela_t43(est, regra, amostra, tipos) -> str:
    linhas = []
    s = est[(est["especificacao"] == "T4.3") & (est["regra_ligacao"] == regra) & (est["amostra"] == amostra)
            & est["grupo_tipo"].isin(tipos)]
    for (gt, g), _ in s.groupby(["grupo_tipo", "grupo"], sort=False):
        def v(o, med="media_por_medico"):
            return _um(s, grupo_tipo=gt, grupo=g, outcome=o, medida=med)
        n = v("delta_horas_totais")["n_obs"]
        fr = v("fracao_do_ganho_compensada_fora", "razao")
        sal = v("delta_horas_totais")
        linhas.append([ROTULO_ORIGEM.get(g, g).replace("FAIXA", "faixa"), _i(n),
                       _n(v("delta_horas_estab_posto", "soma")["estimativa"], 0),
                       _n(v("delta_horas_resto_mun_posto", "soma")["estimativa"], 0),
                       _n(v("delta_horas_mun_posto", "soma")["estimativa"], 0),
                       _n(v("delta_horas_fora_mun_posto", "soma")["estimativa"], 0),
                       _n(v("delta_horas_totais", "soma")["estimativa"], 0),
                       f"{_n(sal['estimativa'], 1, True)} {_ic(sal)}",
                       f"{_pct(fr['estimativa'])} {_ic(fr, pct=True)}" if np.isfinite(fr["estimativa"]) else "—"])
    return _tab(["Grupo", "Médicos", "ΣΔ estab. do posto", "ΣΔ resto do município", "ΣΔ município do posto",
                 "ΣΔ fora", "Σ saldo", "saldo médio por médico [IC 95%]", "fração do ganho compensada fora [IC]"],
                linhas)


def tabela_sensibilidade(est) -> str:
    linhas = []
    jan = f"[{E_PRINC[0]},{E_PRINC[1]}]"
    for o in ("horas_totais", "horas_mun_posto", "horas_fora_mun_posto", "horas_sus", "horas_nao_sus"):
        cel = [ROTULO[o]]
        for regra in REGRAS:
            r = _um(est, especificacao="T4.1b", regra_ligacao=regra, janela=jan, outcome=o, medida="att_pos_medio")
            cel.append(f"{_n(r['estimativa'], 1, True)} {_ic(r)}")
        r = _um(est, especificacao="T4.1b", regra_ligacao=REGRAS[0], janela=f"[{E_LONGA[0]},{E_LONGA[1]}]",
                outcome=o, medida="att_pos_medio")
        p = _um(est, especificacao="T4.1b", regra_ligacao=REGRAS[0], janela=f"[{E_LONGA[0]},{E_LONGA[1]}]",
                outcome=o, medida="wald_pre")
        cel += [f"{_n(r['estimativa'], 1, True)} {_ic(r)}", _p_pre(p["p_valor"])]
        linhas.append(cel)
    return _tab(["Outcome", "D1, janela principal", "literal, janela principal", "D1, janela longa (média θ(0..+10))",
                 "p do pré, janela longa"], linhas)


def tabela_amostra(resumo) -> str:
    linhas = []
    for regra in REGRAS:
        i = resumo["por_regra"][regra]
        md = i["medicos"]
        linhas.append([ROTULO_REGRA[regra], _i(md["registros_ligados"]), _i(md["medicos_distintos"]),
                       _i(md["registros_descartados_na_deduplicacao"]), _i(md["tratados_ciclos_1_2"]),
                       _i(md["por_ciclo"].get("3", 0)), _i(md["ciclos_1_2_sem_origem_x1"]),
                       _i(i["horas_ausentes_medico_mes"])])
    return _tab(["Regra", "Registros ligados", "Médicos (id_prof)", "Registros descartados (deduplicação)",
                 "Tratados (ciclos 1 e 2)", "Ciclo 3 (só controles)", "Ciclos 1–2 sem X1 b", "Médico-mês com hora "
                 "ausente"], linhas)


def tabela_sem_vinculo(resumo) -> str:
    sv = resumo["por_regra"][REGRAS[0]]["meses_sem_vinculo_medico_por_e"]
    es = [str(e) for e in range(E_PRINC[0], E_PRINC[1] + 1)]
    return _tab(["e"] + es, [["médicos"] + [_i(sv[e]["medicos"]) for e in es],
                             ["sem vínculo médico cadastrado"] + [_i(sv[e]["sem_vinculo_medico"]) for e in es]])


def leitura(est, resumo) -> str:
    r0 = REGRAS[0]
    jan = f"[{E_PRINC[0]},{E_PRINC[1]}]"
    orig = resumo["por_regra"][r0]["origem"]
    a = _um(est, especificacao="origem", regra_ligacao=r0, grupo_tipo="todos", outcome="fracao_ja_no_municipio_x1b")
    tot = _um(est, especificacao="T4.1b", regra_ligacao=r0, janela=jan, outcome="horas_totais",
              medida="att_pos_medio")
    mun = _um(est, especificacao="T4.1b", regra_ligacao=r0, janela=jan, outcome="horas_mun_posto",
              medida="att_pos_medio")
    fora = _um(est, especificacao="T4.1b", regra_ligacao=r0, janela=jan, outcome="horas_fora_mun_posto",
               medida="att_pos_medio")
    pre_tot = _um(est, especificacao="T4.1b", regra_ligacao=r0, janela=jan, outcome="horas_totais",
                  medida="wald_pre")
    sal = _um(est, especificacao="T4.3", regra_ligacao=r0, amostra="completa", grupo_tipo="todos",
              outcome="delta_horas_totais", medida="media_por_medico")
    fr = _um(est, especificacao="T4.3", regra_ligacao=r0, amostra="completa", grupo_tipo="todos",
             outcome="fracao_do_ganho_compensada_fora", medida="razao")
    q = est[(est["regra_ligacao"] == r0) & est["entra_bky"]]
    pr = est[(est["especificacao"] == "T4.1b") & (est["regra_ligacao"] == r0) & (est["janela"] == jan)
             & (est["medida"] == "wald_pre") & est["outcome"].isin(OUT_PROTOCOLO) & (est["p_valor"] < 0.05)]
    pre_rej = "; ".join(f"{ROTULO[o]} (p {_p(pv) if pv < 0.001 else '= ' + _p(pv)})"
                        for o, pv in zip(pr["outcome"], pr["p_valor"])) or "nenhum"
    pc = est[(est["especificacao"] == "T4.1c") & (est["regra_ligacao"] == r0) & (est["janela"] == jan)
             & (est["medida"] == "wald_pre") & est["outcome"].isin(OUT_PROTOCOLO) & (est["p_valor"] < 0.05)]
    pre_rej_c = "; ".join(f"{ROTULO[o]}, {ROTULO_ORIGEM[g]} (p {_p(pv) if pv < 0.001 else '= ' + _p(pv)})"
                          for o, g, pv in zip(pc["outcome"], pc["grupo"], pc["p_valor"])) or "nenhum"

    def pre_de(o):
        r = _um(est, especificacao="T4.1b", regra_ligacao=r0, janela=jan, outcome=o, medida="wald_pre")
        return ("; **o teste dos pré rejeita zero (p " + (_p(r["p_valor"]) if r["p_valor"] < 0.001
                                                        else "= " + _p(r["p_valor"])) + "): leitura menos confiável**"
                ) if r["p_valor"] < 0.05 else f"; teste dos pré sem rejeição (p = {_p(r['p_valor'])})"

    def dir_(r):
        if not _exclui_zero(r):
            return "o IC 95% inclui zero"
        return "o IC 95% exclui zero"
    txt = [
        f"- **Origem (descritivo).** Na regra D1, {_pct(a['estimativa'])} {_ic(a, pct=True)} dos "
        f"{_i(a['n_obs'])} médicos dos ciclos 1 e 2 com X1 b já tinham vínculo médico cadastrado no município do "
        f"posto na última competência pré-início; {_pct(1 - a['estimativa'])} eram novos no município. "
        f"{_i(orig['sem_origem_x1'])} médicos não têm X1 b e ficam fora do T4.1c.",
        f"- **Horas totais (T4.1b).** A média de θ(0..+6) das horas totais cadastradas é "
        f"{_n(tot['estimativa'], 1, True)} h/sem {_ic(tot)}; {dir_(tot)}. O teste conjunto dos pré tem "
        f"p = {_p(pre_tot['p_valor'])}.",
        f"- **Falha de pré-tendência (T4.1b).** O teste conjunto dos pré rejeita zero (p < 0,05) em: {pre_rej}. Nesses "
        "outcomes a comparação entre coortes é menos confiável. No T4.1c, por origem, rejeita em: "
        f"{pre_rej_c}.",
        f"- **Onde estão as horas (T4.1b).** No município do posto: {_n(mun['estimativa'], 1, True)} h/sem "
        f"{_ic(mun)} ({dir_(mun)}{pre_de('horas_mun_posto')}); fora dele: {_n(fora['estimativa'], 1, True)} h/sem "
        f"{_ic(fora)} ({dir_(fora)}{pre_de('horas_fora_mun_posto')}). "
        "Como horas totais = município do posto + fora, o saldo associado à entrada é a soma das duas.",
        f"- **Contabilidade pré × pós (T4.3, sem grupo de comparação).** O saldo médio por médico é "
        f"{_n(sal['estimativa'], 1, True)} h/sem {_ic(sal)}; a fração do ganho no município do posto compensada por "
        f"perda fora dele é {_pct(fr['estimativa'])} {_ic(fr, pct=True)}. Essa conta inclui qualquer tendência "
        "comum a todos os médicos; o T4.1b a desconta usando quem ainda não começou.",
        f"- **Teste múltiplo.** Das {_i(len(q))} linhas da regra D1 no BKY (T4.1b e T4.1c), "
        f"{_i((q['q_bky'] <= 0.05).sum())} têm q <= 0,05; essa conta inclui outcomes cujo teste dos pré rejeita zero "
        "(acima).",
        "- **O que o contraste identifica.** No máximo a associação entre entrar no PMM-E e as horas cadastradas "
        "do próprio médico, sob tendências paralelas entre médicos que entram em meses diferentes. Não é o efeito "
        "da bolsa, nem do PMM-E sobre a oferta do município (que exige o teste município–mês), nem retenção "
        "individual: vínculo cadastrado não é presença.",
    ]
    return "\n".join(txt)


def gerar_doc(est: pd.DataFrame, resumo: dict) -> str:
    r0, r1 = REGRAS
    figs = resumo["saidas"]["figuras"]
    partes = [
        "# 57d. Resultados do P4: o programa cria oferta nova ou só passa a pagar quem já estava lá?",
        "",
        f"> **Data:** {DATA_EXECUCAO}.<br>",
        "> **Protocolo:** [`54_protocolo_P4_oferta_substituicao.md`](54_protocolo_P4_oferta_substituicao.md), "
        "congelado em 19/10/2026 antes de abrir o painel a16 por tempo de evento.<br>",
        "> **Script:** `scripts/rdd_bolsa/28_trajetoria_medicos.py` (gera este documento inteiro).<br>",
        "> **Saídas:** `output/rdd_bolsa/P4_estimativas.csv`, `P4_resumo.json` e `P4_figuras/`.<br>",
        "> **Testes:** `tests/test_trajetoria_medicos.py`.<br>",
        f"> **Estatuto:** `{ESTATUTO}`; toda linha tem `natureza_dos_dados = {NATUREZA}`. Nada aqui tem fonte de "
        "exogeneidade validada.",
        "",
        "Este documento é gerado pelo script a partir de `output/`; não edite à mão. O teste confere que ele é "
        "igual ao que o script gera.",
        "",
        "## 1. O que se pergunta e o que o contraste identifica",
        "",
        "O P4 acompanha, mês a mês, as horas e os vínculos **cadastrados** no CNES de cada médico do PMM-E ligado na "
        "X1, antes e depois do início no programa. A pergunta é se o médico soma horas, troca privado por SUS, "
        "muda de município ou só passa a ser registrado no posto onde já estava.",
        "",
        "- **Contraste:** entrada no PMM-E, comparando médicos que começam em meses diferentes (T4.1b e T4.1c). "
        "Mede associação sob tendências paralelas; não é o efeito da bolsa nem do PMM-E sobre o município.",
        "- **Resultado exploratório.** Nenhuma fonte de exogeneidade foi validada para a data de entrada; os "
        "números descrevem o que está associado à entrada, não provam efeito.",
        "- **Vínculo não é presença.** Horas cadastradas não são horas trabalhadas, e permanecer no cadastro não "
        "é retenção individual.",
        "- **Heterogeneidade só por condição pré-tratamento:** a origem (X1 b) e a faixa da lista.",
        "- **T4.2 e T4.3 são descritivos.**",
        "",
        "## 2. Amostra",
        "",
        "A chave longitudinal é o código do profissional no CNES (`id_prof`, a16). Um médico com mais de um "
        "registro nas listas fica com um só: o da lista de ativos de 11/09/2026, depois o início mais antigo. O "
        "ciclo 3 entra só como controle ainda não iniciado; o efeito sobre ele segue o plano prospectivo.",
        "",
        tabela_amostra(resumo),
        "",
        "Meses sem vínculo médico cadastrado entre os tratados (regra D1). Contam como zero vínculos e zero horas, "
        "porque a competência foi lida; nenhuma competência falta na fonte.",
        "",
        tabela_sem_vinculo(resumo),
        "",
        "## 3. Origem: novos e já presentes (descritivo)",
        "",
        f"Regra {ROTULO_REGRA[r0]}. IC de Wilson. Faixas da lista: faixa 1 = IVS 2010 acima de 0,400; faixa 2 = "
        "acima de 0,300 até 0,400; faixa 3 = até 0,300. A diferença entre faixas é descritiva: a faixa anda com "
        "o IVS, o porte e a oferta prévia do município.",
        "",
        tabela_origem(est, r0),
        "",
        "## 4. Médias por tempo de evento (T4.1a, descritivo)",
        "",
        "Amostra completa, regra D1. Todas as janelas, a subamostra balanceada e a regra literal estão no CSV.",
        "",
        tabela_t41a(est, r0),
        "",
        "## 5. Entrada no PMM-E e horas do médico (T4.1b)",
        "",
        "Callaway–Sant'Anna no nível do médico, janela principal, regra D1. θ(e) em horas semanais cadastradas "
        "(ou unidades do outcome); IC 95% do bootstrap multiplicador por médico; q de BKY dentro do T4.1b.",
        "",
        tabela_t41b(est, r0),
        "",
        "**Atenção.** Onde o p do pré está em negrito, o teste conjunto dos pré rejeita zero: nesses outcomes as "
        "coortes já diferiam antes do início e a leitura de θ(e) como associada à entrada é menos confiável.",
        "",
        "## 6. Por origem (T4.1c)",
        "",
        "Mesma especificação, separando quem já tinha vínculo no município do posto antes do início (X1 b = 1) de "
        "quem não tinha. Os controles são todos os médicos ainda não iniciados.",
        "",
        tabela_t41c(est, r0),
        "",
        "**Atenção.** O p do pré em negrito rejeita zero (p < 0,05); vale a mesma ressalva do T4.1b.",
        "",
        "## 7. Teste múltiplo (BKY)",
        "",
        tabela_bky(est),
        "",
        "Os q de BKY corrigem o número de testes, não a falha de pré-tendência: linhas de outcomes cujo teste dos "
        "pré rejeita zero entram nas contagens acima e não devem ser lidas como confirmadas.",
        "",
        "## 8. Quem mudou de município (T4.2, descritivo)",
        "",
        "Médicos novos no município do posto (X1 b = 0) com vínculo médico em outro município no mês antes do "
        "início. Pré = média dos meses −6 a −1; pós = média dos meses 0 a +6 disponíveis. A variação da CBO no "
        "município de origem é em horas totais do município (CNES nacional, a09): a média por par pesa mais os "
        "municípios grandes e inclui a tendência local, sem grupo de comparação. Pares com CBO sem série própria "
        "no a09 ficam fora dessas três linhas (contagens no resumo).",
        "",
        tabela_t42(est, r0),
        "",
        "## 9. Contabilidade líquida (T4.3, descritivo)",
        "",
        "Variação entre a média dos meses −6 a −1 e a dos meses 0 a +6 disponíveis, em horas semanais "
        "cadastradas, somada sobre os médicos. Saldo = Δ município do posto + Δ fora (= Δ horas totais). Sem grupo "
        "de comparação e sem contraste no corte.",
        "",
        "Amostra completa, por faixa, origem e ciclo:",
        "",
        tabela_t43(est, r0, "completa", ["todos", "ciclo", "faixa", "origem"]),
        "",
        "Por curso (amostra completa):",
        "",
        tabela_t43(est, r0, "completa", ["curso"]),
        "",
        "Subamostra balanceada (início entre 202412 e 202602):",
        "",
        tabela_t43(est, r0, "balanceada", ["todos", "faixa", "origem"]),
        "",
        "## 10. Sensibilidades",
        "",
        tabela_sensibilidade(est),
        "",
        "p do pré em negrito rejeita zero (p < 0,05).",
        "",
        "## 11. Figuras",
        "",
    ]
    for f in figs:
        nome = Path(f["arquivo"]).name
        partes += [f"### {f['descricao']}", "", f"![{nome}](../../{f['arquivo']})", "",
                   f"**Como ler.** {f['como_ler']}", ""]
        if nome in ("P4_T41b_evento_horas.png", "P4_T41c_origem.png"):
            partes += ["**Atenção.** Pontos antes do mês 0 longe de zero indicam falha de pré-tendência; os p do "
                       "teste conjunto dos pré estão nas seções 5 e 6, e nos outcomes em que ele rejeita a leitura "
                       "é menos confiável.", ""]
    partes += ["## 12. Leitura", "", leitura(est, resumo), "",
               "## 13. Decisões e desvios", ""]
    partes += [f"- **{d['item']}** ({d['data']}). {d['descricao']}" for d in resumo["desvios"]]
    partes += ["", "## 14. Limitações", "",
               "- Só vínculos com CBO médica; outras ocupações do mesmo médico ficam fora.",
               "- Médicos não ligados na X1 não estão no painel; a ligação falha para uma parte (taxas na X1).",
               "- O retrato de ativos exclui quem saiu antes de 11/09/2026; a lista de agosto recupera só parte.",
               "- Quem entra no PMM-E e quando não é aleatório: tendências paralelas entre coortes podem falhar.",
               "- A origem usa a última de seis competências esparsas (X1 b); o painel mensal dá outra leitura, "
               "relatada ao lado.",
               "- Migração cadastral (o mesmo trabalho registrado em outro estabelecimento ou município) não se "
               "distingue de mudança real com dados de cadastro.",
               ""]
    return "\n".join(partes)


def ler_saidas() -> tuple[pd.DataFrame, dict]:
    est = pd.read_csv(OUT / NOME_EST, dtype={"grupo": str, "e": "Int64"}, keep_default_na=True)
    est["e"] = est["e"].astype("float")
    est["nota"] = est["nota"].fillna("")
    resumo = json.loads((OUT / NOME_RESUMO).read_text(encoding="utf-8"))
    return est, resumo


def atualizar_doc() -> None:
    est, resumo = ler_saidas()
    DOC.write_text(gerar_doc(est, resumo), encoding="utf-8")
    print(f"doc gerado: {rotulo(DOC)}")


# ---------------------------------------------------------------------------
# 7. Execução
# ---------------------------------------------------------------------------

DESVIOS = [
    {"data": "2026-10-23", "item": "Um registro por médico",
     "descricao": "Na X1 um mesmo id_prof pode estar ligado a mais de um registro das listas (o médico aparece na "
                  "lista de agosto com outro estabelecimento, ou em dois cursos ou ciclos). O protocolo fala em "
                  "médico × mês; fica o registro da lista de ativos de 11/09/2026, depois o início mais antigo, "
                  "depois o menor id_medico. Regra fixada antes de abrir os dados por tempo de evento; contagens "
                  "no resumo."},
    {"data": "2026-10-23", "item": "Ciclo 3",
     "descricao": "Pelo §3, os médicos do ciclo 3 são controles ainda não iniciados até 202608. Eles não entram "
                  "como coorte tratada (o início do ciclo 3 é 202608 ou 202609): outcomes do ciclo 3 depois do "
                  "início seguem o plano prospectivo do CLAUDE.md. O T4.1a, o T4.2 e o T4.3 são só dos ciclos 1 "
                  "e 2."},
    {"data": "2026-10-23", "item": "Mínimo de controles por célula",
     "descricao": f"ATT(g, t) só é estimado com pelo menos {MIN_CONTROLES} controles; em 202608 os únicos ainda "
                  "não iniciados são os poucos médicos com início em 202609, e essas células ficam sem estimativa "
                  "(nota no CSV). Fixado antes de abrir os dados."},
    {"data": "2026-10-23", "item": "Inferência do T4.1b",
     "descricao": f"Bootstrap multiplicador com pesos de Mammen, B = {B_BOOT}, semente {SEMENTE}, unidade = médico; "
                  "EP = intervalo interquartil / (z_0,75 − z_0,25), como no D2 (script 22); a função de influência "
                  "de θ(e) inclui a estimação dos pesos de coorte. Teste dos pré: Wald conjunto de θ(e) = 0 para "
                  "e <= −2 com a covariância das funções de influência."},
    {"data": "2026-10-23", "item": "Controles do T4.1c",
     "descricao": "O §3 separa os tratados pela origem. Os controles continuam sendo todos os médicos ainda não "
                  "iniciados, de qualquer origem, porque a X1 só calcula a origem dos ciclos 1 e 2."},
    {"data": "2026-10-23", "item": "BKY",
     "descricao": "Família = θ(e) para e de 0 a +6, janela principal, os 14 outcomes do §2, uma família no T4.1b e "
                  "outra no T4.1c, por regra de ligação. Os pré, a média do pós, a janela longa e os outcomes "
                  "complementares ficam fora."},
    {"data": "2026-10-23", "item": "Natureza jurídica",
     "descricao": "Público = natureza jurídica 1xxx (administração pública); privado com fins = 2xxx (entidades "
                  "empresariais); sem fins = 3xxx. Pessoa física (4xxx) e outras ficam num outcome complementar, "
                  "para que as partes somem as horas totais."},
    {"data": "2026-10-23", "item": "Sinal da contabilidade líquida (T4.3)",
     "descricao": "O §3 escreve 'Δ horas no município do posto − Δ horas fora dele'; o doc 51 diz 'ganho no "
                  "destino menos perda na origem'. Como a perda fora é −Δ fora, o saldo relatado é Δ município do "
                  "posto + Δ fora (= Δ horas totais), com as duas parcelas também relatadas."},
    {"data": "2026-10-23", "item": "Janelas do pré e do pós no T4.2 e no T4.3",
     "descricao": "O protocolo diz 'entre o pré e o pós' sem fixar meses. Pré = média dos meses −6 a −1; pós = "
                  "média dos meses 0 a +6 disponíveis até 202608 (a janela principal)."},
    {"data": "2026-10-23", "item": "Mudança de município e CBO no T4.2",
     "descricao": "Mudou = novo no município pela X1 b com vínculo médico em outro município no mês −1 do painel "
                  "mensal. A série do CNES nacional é a da CBO do vínculo na origem; CBO sem série própria no a09 "
                  "fica ausente, com motivo."},
    {"data": "2026-10-23", "item": "Cache privado do a16",
     "descricao": "O cache privado (`output/aquisicao/cnes_profissional/cache_privado/`) não existe neste "
                  "ambiente e não é necessário: o P4 usa os painéis e as chaves pseudônimas versionados e lê as "
                  "listas nominais só em memória, sem gravar nome, CPF, CNS ou CRM."},
    {"data": "2026-10-23", "item": "Local do resultado",
     "descricao": "O protocolo indica docs/06_execucao/57d_resultados_P4_trajetoria.md; seguido."},
]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--atualizar-doc", action="store_true", help="só regrava o doc 57d a partir das saídas")
    args = ap.parse_args(argv)
    if args.atualizar_doc:
        atualizar_doc()
        return 0
    dados = carregar()
    linhas, por_regra = [], {}
    for regra in REGRAS:
        lr, info = estimar_regra(regra, dados)
        linhas += lr
        por_regra[regra] = info
    est = pd.DataFrame(linhas)[COLUNAS]
    est = aplicar_bky(est)
    nucleo = ["estimativa"]
    sem_nota = est[est[nucleo].isna().any(axis=1) & (est["nota"].fillna("") == "")]
    if len(sem_nota):
        raise FalhaValidacao(f"{len(sem_nota)} linhas sem estimativa e sem nota")
    if not ((est["natureza_dos_dados"] == NATUREZA).all() and (est["estatuto"] == ESTATUTO).all()):
        raise FalhaValidacao("linha sem rótulo de natureza ou estatuto")
    OUT.mkdir(parents=True, exist_ok=True)
    est.to_csv(OUT / NOME_EST, index=False, float_format="%.10g")
    est = pd.read_csv(OUT / NOME_EST, dtype={"grupo": str})
    est["nota"] = est["nota"].fillna("")
    figs = gerar_figuras(est, OUT / DIR_FIG)
    dl = dados["diag_listas"]
    entradas = [
        bloco_entrada(PROTOCOLO_MD, "protocolo 54 (somente lido)", "repositório", "2026-10-19", "§1–§6", "documento",
                      "-", "-"),
        bloco_entrada(ARQ_VINC, "vínculos médicos por médico × mês (horas, estabelecimento, município, natureza)",
                      "CNES/DATASUS, a16 (portão G5)", "202406–202608", "27 competências", "vínculo × competência",
                      "id_prof, competencia, co_cnes, co_cbo", "nenhuma competência >= 202609"),
        bloco_entrada(ARQ_MED, "conferência do painel refeito (fail closed)", "a16", "202406–202608",
                      "27 competências", "médico × competência", "id_prof, competencia", "nenhum"),
        bloco_entrada(ARQ_CHAVES, "ponte id_prof ↔ id_medico da X1, por regra", "a16", "2026-10-19", "X1",
                      "registro × regra", "id_prof, id_externo, regra_ligacao", "origem = X1"),
        bloco_entrada(G5_RESUMO, "competências obtidas e veredito do portão", "a16", "2026-10-19", "27 competências",
                      "-", "-", "-"),
        bloco_entrada(ARQ_X1, "ligação, faixa e origem (X1 b)", "X1 (script 17)", "listas de 12/08 e 11/09/2026",
                      "1.990 registros × 2 regras", "registro × regra", "id_medico, regra_ligacao",
                      "colunas id_medico, regra_ligacao, ciclo, fonte_lista, co_ibge, faixa, ligado, "
                      "b_mesmo_mun_ultimo_pre"),
        bloco_entrada(X1M.ATIVOS_ZIP, "início, ciclo, curso, estabelecimento e município do posto (só em memória; "
                      "nome, CRM e UF descartados)", "SGTES/MS, relação nominal de ativos", "2026-09-11",
                      f"{dl['registros_ativos_2026_09_11']} registros", "registro", "ciclo, CRM, UF, CNES, curso",
                      "nenhum"),
        bloco_entrada(X1M.NOMINAL_CSV, "idem, registros só da lista de agosto (só em memória)",
                      "SGTES/MS, lista nominal", "2026-08-12", f"{dl['registros_so_na_nominal']} registros só nela",
                      "registro", "ciclo, CRM, UF, CNES, curso", "nenhum"),
        bloco_entrada(ARQ_NAC, "T4.2: horas da mesma CBO no município de origem", "CNES nacional (a09)",
                      "202406–202608", "municípios dos vínculos do painel", "município × grupo de CBO × mês",
                      "co_ibge, grupo, competencia", "competência entre 202406 e 202608 (filtro na leitura)"),
        bloco_entrada(PONTE, "rótulo dos cursos 1–16", "ponte curso–CBO (aquisição/01)", "2026-08-30",
                      "16 cursos", "curso", "cod_curso", "só especialidade_cfm"),
    ]
    contagens = {"linhas": int(len(est)),
                 "por_especificacao": {k: int(v) for k, v in est["especificacao"].value_counts().sort_index().items()},
                 "executado": int((est["status"] == "EXECUTADO").sum()),
                 "sem_estimativa": int((est["status"] == "SEM_ESTIMATIVA").sum()),
                 "referencia": int((est["status"] == "REFERENCIA").sum()),
                 "linhas_bky": int(est["entra_bky"].astype(bool).sum())}
    r0 = REGRAS[0]
    jan = f"[{E_PRINC[0]},{E_PRINC[1]}]"

    def pick(**f):
        r = _um(est, **f)
        return {k: (None if pd.isna(r[k]) else float(r[k])) for k in ("estimativa", "ic95_inf", "ic95_sup",
                                                                        "p_valor", "n_obs")}
    principais = {
        "fracao_ja_no_municipio_x1b": pick(especificacao="origem", regra_ligacao=r0, grupo_tipo="todos",
                                           outcome="fracao_ja_no_municipio_x1b"),
        "fracao_novos_x1b": pick(especificacao="origem", regra_ligacao=r0, grupo_tipo="todos",
                                 outcome="fracao_novos_x1b"),
        "att_pos_medio_horas_totais": pick(especificacao="T4.1b", regra_ligacao=r0, janela=jan,
                                           outcome="horas_totais", medida="att_pos_medio"),
        "att_pos_medio_horas_mun_posto": pick(especificacao="T4.1b", regra_ligacao=r0, janela=jan,
                                              outcome="horas_mun_posto", medida="att_pos_medio"),
        "att_pos_medio_horas_fora_mun_posto": pick(especificacao="T4.1b", regra_ligacao=r0, janela=jan,
                                                   outcome="horas_fora_mun_posto", medida="att_pos_medio"),
        "t43_saldo_medio_por_medico": pick(especificacao="T4.3", regra_ligacao=r0, amostra="completa",
                                           grupo_tipo="todos", outcome="delta_horas_totais",
                                           medida="media_por_medico"),
        "t43_fracao_do_ganho_compensada_fora": pick(especificacao="T4.3", regra_ligacao=r0, amostra="completa",
                                                    grupo_tipo="todos", outcome="fracao_do_ganho_compensada_fora",
                                                    medida="razao"),
    }
    resumo = {
        "etapa": "P4_trajetoria_medicos",
        "natureza_dos_dados": NATUREZA,
        "estatuto": ESTATUTO,
        "data_execucao": DATA_EXECUCAO,
        "script": rotulo(Path(__file__)),
        "documento": rotulo(DOC),
        "protocolo": {"arquivo": rotulo(PROTOCOLO_MD), "sha256": sha256(PROTOCOLO_MD)},
        "contraste": "entrada do médico no PMM-E, entre médicos que começam em meses diferentes (T4.1b/T4.1c); não é "
                     "o efeito da bolsa, nem do PMM-E sobre o município, nem retenção individual",
        "leitura": LEITURA,
        "parametros": {"competencias": [dados["comps"][0], dados["comps"][-1]], "limite_exclusivo": LIMITE_EXCLUSIVO,
                       "janela_principal": list(E_PRINC), "janela_longa": list(E_LONGA),
                       "balanceada_inicio": list(BAL_INICIO), "regras": list(REGRAS), "regra_principal": REGRAS[0],
                       "bootstrap": {"B": B_BOOT, "pesos": "Mammen", "semente": SEMENTE, "unidade": "médico"},
                       "min_controles": MIN_CONTROLES, "ciclos_tratados": list(CICLOS_TRATADOS)},
        "outcomes": {o: {"rotulo": r, "unidade": u, "bky": True} for o, r, u in OUTCOMES}
                    | {o: {"rotulo": r, "unidade": u, "bky": False, "nota": ROTULO_COMPLEMENTAR}
                       for o, r, u in COMPLEMENTARES},
        "entradas": entradas,
        "listas_pmme": {k: dl[k] for k in ("registros_ativos_2026_09_11", "registros_nominal_2026_08_12",
                                           "registros_so_na_nominal", "registros_uniao")},
        "conferencia_listas_x1": dados["conf_x1"],
        "cache_privado_a16": {"existe": CACHE_PRIVADO.exists(), "necessario": False},
        "por_regra": por_regra,
        "principais": principais,
        "desvios": DESVIOS,
        "contagens": contagens,
        "saidas": {NOME_EST: {"arquivo": rotulo(OUT / NOME_EST), "sha256": sha256(OUT / NOME_EST)},
                   "figuras": figs},
        "como_ler": {Path(f["arquivo"]).name: f["como_ler"] for f in figs},
        "integridade": "nada simulado ou imputado; mês em que o médico não aparece numa competência lida = zero "
                       "vínculos, com rótulo; nenhuma competência >= 202609; o arquivo local de IVS não é lido; sem "
                       "nome, CPF, CNS, CRM ou código de profissional nas saídas; só agregados",
    }
    gravar_json(OUT / NOME_RESUMO, resumo)
    atualizar_doc()
    print(json.dumps(_nan_none(principais), ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except FalhaValidacao as erro:
        print(f"FALHA DE VALIDACAO: {erro}", file=sys.stderr)
        sys.exit(2)
