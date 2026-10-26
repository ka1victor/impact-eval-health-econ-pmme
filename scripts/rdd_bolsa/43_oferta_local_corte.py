"""Protocolo 64: oferta local de especialistas comparada no corte de IVS (DiRD e RDD fuzzy da chegada).

Protocolo congelado: `docs/06_execucao/64_protocolo_oferta_local_no_corte.md`. Estatuto de toda saída:
`PROTOCOLO_64_POS_RESULTADO`; `natureza_dos_dados = EMPIRICO`. Decisões de implementação (D1–D16): seção 9 de
`docs/06_execucao/57q_resultados_oferta_local_corte.md`, gravadas antes de qualquer estimativa.

O que muda em relação ao doc 57k (script 37): a fonte de variação. Em vez do mês da chegada do 1º médico do PMM-E,
o lado do corte de IVS (0,300 e 0,400), que decide a bolsa e também outras regras federais (auditoria 18). O
contraste da forma reduzida é o **pacote do corte**; a razão fuzzy só é "efeito de receber médico" sob exclusão.

Desenho (protocolo 64, §3)
--------------------------
- Running variable: IVS 2010 oficial do Ipea (a08), lido pela função do E7 (script 14). O arquivo local de IVS da
  auditoria 16 não é lido.
- RDD local linear, kernel triangular, h = 0,050, cada corte separado, um município por linha, EP HC1
  (`rdd_lib.rd_local_linear` / `rd_dird_delta`). ΔY = média(202510–202608) − média(202406–202506).
- Outcomes B1–B5 e amostra V: funções importadas do script 37, sem reescrever.
- Parte A: forma reduzida em V (A1 e A2 primárias, Holm entre as 4) e em U; parte B: primeiro estágio (D1, D2) e
  razão fuzzy com IC de Anderson–Rubin por inversão em grade; parte C: estudo de evento no corte; parte D: ATT da
  chegada (estimador e bootstrap do 37) abaixo e acima de cada corte; parte E: salto de ter célula em U.
- Sensibilidades: h = 0,030 e 0,080; IC honesto; média do pós com a do pré como covariável.

Portão de reprodução (falha fechada, nada é gravado)
----------------------------------------------------
Antes de qualquer conta nova: B1 em U (funções do 37) → ΔB1 → `rd_dird_delta` em 0,300 reproduz o F3.1 em U,
0,300, `principal`, de `E7_estimativas.csv` com diferença ≤ 1e−8.

Saídas: output/rdd_bolsa/OC_estimativas.csv, OC_estudo_evento.csv, OC_resumo.json, OC_figuras/*.png; blocos entre
marcadores `<!-- OC:...:inicio/fim -->` do doc 57q. Não regrava E7_*, OL_* nem EQ_*.

Uso
---
    python3 scripts/rdd_bolsa/43_oferta_local_corte.py
    python3 scripts/rdd_bolsa/43_oferta_local_corte.py --atualizar-doc
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
OL = _importar(DIR_RDD / "37_oferta_local_chegada.py", "ol37_para_oc")
sys.dont_write_bytecode = _bytecode
D2M = OL.D2M
K1M = OL.K1M
E7 = OL.E7
L = OL.L

# ---------------------------------------------------------------------------
# Caminhos e parâmetros do protocolo
# ---------------------------------------------------------------------------

OUT = ROOT / "output" / "rdd_bolsa"
PROTOCOLO_MD = ROOT / "docs" / "06_execucao" / "64_protocolo_oferta_local_no_corte.md"
DOC = ROOT / "docs" / "06_execucao" / "57q_resultados_oferta_local_corte.md"
E7_EST = OUT / "E7_estimativas.csv"
OL_RESUMO = OUT / "OL_resumo.json"

NOME_EST = "OC_estimativas.csv"
NOME_EVENTO = "OC_estudo_evento.csv"
NOME_RESUMO = "OC_resumo.json"
DIR_FIG = "OC_figuras"

DATA_EXECUCAO = "2026-10-26"
ESTATUTO = "PROTOCOLO_64_POS_RESULTADO"
NATUREZA = "EMPIRICO"
LIMITE_EXCLUSIVO = "202609"
CORTES = L.CORTES_MIL                     # (300, 400)
H = L.H_PRINCIPAL_MIL                     # 50
H_SENS = L.H_SENSIBILIDADE_MIL            # (30, 80)
ROTULO_CORTE = {300: "0.300", 400: "0.400"}
MESES = OL.MESES                          # 202406–202608
COMP_PRE = E7.COMP_PRE                    # 202406–202506
COMP_POS = E7.COMP_POS                    # 202510–202608
COMP_REF = E7.COMP_REF                    # 202506
MESES_PRE_PLANO = tuple(m for m in MESES if m < COMP_REF)       # 202406–202505 (12 meses)
ESCALA_HAB = OL.ESCALA_HAB
ALFA = 0.05
TOL_PORTAO = 1e-8
GRADE_AR_N = 4001
GRADE_AR_FATOR = 2.0
BISSECAO_AR = 60
F_FRACO = 10.0
B_BOOT = OL.B_BOOT                        # 9.999 (script 37)
SEMENTE = OL.SEMENTE                      # 20261026 (script 37)
E_MIN, E_MAX = OL.E_MIN, OL.E_MAX         # −6, +6
LARGURA_COMO_LER = 150

IDS = OL.IDS                              # B1–B5
SPEC = OL.SPEC
ID_OC = {"B1": "OC-A1", "B2": "OC-A2", "B3": "OC-A3", "B4": "OC-A4", "B5": "OC-A5"}
PRIMARIAS = ("B1", "B2")
OUTCOMES_EVENTO = ("B1", "B2", "B3")
OUTCOMES_D = ("B1", "B2", "B3")

CONTRASTE_A = ("DiRD no corte: pacote do corte (bolsa R$ 5 mil maior + outras regras federais nos mesmos cortes, "
               "auditoria 18) sobre a mudança pós − pré; remove só a parte das outras regras constante no tempo; não é "
               "efeito da participação no PMM-E nem do Agora Tem Especialistas")
CONTRASTE_B0 = "primeiro estágio: salto, no corte, de receber médico do PMM-E (D1) ou da intensidade (D2)"
CONTRASTE_B = ("razão fuzzy: efeito de receber médico do PMM-E para quem recebe por causa do corte, só sob exclusão "
               "(o corte só move a oferta pelo médico do programa); o pacote do corte pode violar a exclusão")
CONTRASTE_C = "estudo de evento no corte: salto de Y_t − Y_202506 (pacote do corte, mês a mês)"
CONTRASTE_D = ("ATT da chegada (Callaway-Sant'Anna do doc 57k) só com os tratados perto do corte; diferença entre "
               "lados = heterogeneidade por condição pré-tratamento, não efeito da bolsa")
CONTRASTE_E = "salto, no corte, de ter célula em algum ciclo (seleção de V)"

DESVIOS: list[dict] = []                  # nenhum desvio do protocolo; as decisões estão na seção 9 do 57q


class FalhaValidacao(RuntimeError):
    """Portão ou validação obrigatória falhou: o script para sem gravar."""


rotulo = K1M.rotulo
sha256 = K1M.sha256
_gravar_json = K1M._gravar_json


# ---------------------------------------------------------------------------
# 1. Dados: amostra, chegadas e outcomes (funções do script 37)
# ---------------------------------------------------------------------------

def taxa(nivel: pd.DataFrame, pop: pd.Series) -> pd.DataFrame:
    """Nível município × mês ÷ população 2022 × 10 mil (como no 37); ausente continua ausente."""
    return nivel.div(pop.reindex(nivel.index).astype(float), axis=0) * ESCALA_HAB


def _longa(larga: pd.DataFrame) -> pd.DataFrame:
    """Município × mês em linhas (co_ibge, competencia, y); ausente continua ausente."""
    return (larga.rename_axis(index="co_ibge", columns=None).reset_index()
            .melt(id_vars="co_ibge", var_name="competencia", value_name="y"))


def deltas(larga: pd.DataFrame) -> pd.DataFrame:
    """y_pre, y_pos e delta por município (`diferenca_pos_pre`, exigir_completo = True, como no E7)."""
    longa = _longa(larga)
    d = L.diferenca_pos_pre(longa, col_unidade="co_ibge", col_periodo="competencia", col_y="y",
                            periodos_pre=COMP_PRE, periodos_pos=COMP_POS, exigir_completo=True)
    out = d.set_index("co_ibge").reindex(larga.index)
    out.attrs.update(d.attrs)
    return out


def contar_d2(x1: pd.DataFrame, cbos: list[str], U: pd.Index, comp_ini: str) -> tuple[pd.Series, dict]:
    """D2 (decisão D6): médicos distintos ligados (regra D1 da X1, registro do ciclo 1 ou 2) com vínculo SUS em
    CBO-alvo em estabelecimento do município entre `comp_ini` e 202608. Zero é observado (o a16 tem todas as
    competências, conferido por `horas_ligados` do 37 antes desta função)."""
    ch = pd.read_parquet(OL.ARQ_CHAVES)
    ch = ch[(ch["origem"] == "X1") & (ch["regra_ligacao"] == OL.REGRA_LIGACAO)]
    ext = set(x1.loc[(x1["ligado"] == 1) & x1["ciclo"].astype(str).isin(OL.CICLOS_TRATAMENTO), "id_medico"])
    ids = set(ch.loc[ch["id_externo"].isin(ext), "id_prof"].astype(str))
    v = pd.read_parquet(OL.ARQ_VINC, columns=["id_prof", "competencia", "co_municipio", "co_cbo", "tp_sus_nao_sus"])
    v["competencia"] = v["competencia"].astype(str)
    if (v["competencia"] >= LIMITE_EXCLUSIVO).any():
        raise FalhaValidacao("a16 com competência >= 202609")
    v = v[(v["competencia"] >= comp_ini) & (v["competencia"] <= MESES[-1]) & v["id_prof"].astype(str).isin(ids)
          & v["co_cbo"].astype(str).isin(cbos) & (v["tp_sus_nao_sus"].astype(str) == "S")]
    n = v.groupby(v["co_municipio"].astype(str))["id_prof"].nunique()
    info = {"medicos_ligados_ciclos_1_2": len(ids), "medicos_com_vinculo_no_periodo": int(v["id_prof"].nunique()),
            "municipios_com_medico": int((n > 0).sum()), "fora_de_U": int(len(set(n.index) - set(U))),
            "meses": [comp_ini, MESES[-1]]}
    return n.reindex(U).fillna(0).astype(float), info


def carregar() -> dict:
    """Refaz U, V, chegadas e B1–B5 com as funções do script 37 (decisões D1, D2, D5)."""
    base, conf_u = K1M.ler_universo()
    U = pd.Index(base.index, name="co_ibge")
    am_total, info_am = OL.ler_amostra(base)
    ch_total, info_ch = D2M.ler_chegadas(am_total)
    am_d2, _ = D2M.ler_amostra(base)
    excl = sorted(set(ch_total.index[ch_total["chegada"].notna()]) - set(am_d2))
    V = am_total.difference(pd.Index(excl))
    ol = json.loads(OL_RESUMO.read_text(encoding="utf-8"))
    if int(len(V)) != int(ol["amostra"]["n_municipios"]):
        raise FalhaValidacao(f"V com {len(V)} municípios; OL_resumo.json tem {ol['amostra']['n_municipios']}")
    ch_U, info_ch_U = D2M.ler_chegadas(U)
    inicio_ativos, info_ativos = OL.ler_inicio_ativos()
    G, coortes, info_G, saida = OL.indices(ch_total.reindex(V), inicio_ativos, V)
    if info_G["n_tratados"] != ol["coortes"]["n_tratados"]:
        raise FalhaValidacao("número de tratados em V difere do OL_resumo.json")
    p = OL.ler_painel(U)
    niveis = {oid: OL.contagem(p, SPEC[oid]["grupo"], SPEC[oid]["col"], U) for oid in IDS if oid != "B3"}
    pop = base["populacao_2022"].astype(float)
    return {"base": base, "conf_u": conf_u, "U": U, "V": V, "am_total": am_total, "info_am": info_am,
            "info_ch": info_ch, "info_ch_U": info_ch_U, "excl": excl, "ch_total": ch_total, "ch_U": ch_U,
            "G": G, "coortes": coortes, "info_G": info_G, "saida": saida, "info_ativos": info_ativos,
            "painel": p, "niveis": niveis, "pop": pop}


def completar_b3(dados: dict) -> None:
    """B3 = B2 − horas SUS em CBO-alvo dos ligados (funções do 37), em U."""
    ids, x1, info_lig = OL.ler_ligados()
    cbos = OL.cbos_alvo()
    S, _, info_b3 = OL.horas_ligados(ids, cbos, dados["U"])
    b2 = dados["niveis"]["B2"]
    viol = (S - b2).to_numpy(float)
    if np.nanmax(np.where(np.isfinite(viol), viol, -np.inf)) > 1e-9:
        raise FalhaValidacao("horas subtraídas maiores que as horas SUS das CBO-alvo do a09 numa célula")
    dados["niveis"]["B3"] = b2 - S
    dados.update({"x1": x1, "cbos": cbos, "info_lig": info_lig, "info_b3": info_b3})


# ---------------------------------------------------------------------------
# 2. Portão de reprodução (F3.1 do E7 em U, 0,300)
# ---------------------------------------------------------------------------

def portao_reproducao(dados: dict) -> dict:
    U, base = dados["U"], dados["base"]
    d = deltas(taxa(dados["niveis"]["B1"], dados["pop"]))
    s = base.loc[U, "s_mil"].to_numpy(float)
    r = L.rd_dird_delta(s, d["y_pos"].to_numpy(float), d["y_pre"].to_numpy(float), 300, H)
    e7 = pd.read_csv(E7_EST, dtype={"corte": str, "outcome_id": str})
    ref = e7[(e7["outcome_id"] == "F3.1") & (e7["populacao"] == "U") & (e7["corte"] == "0.300")
             & (e7["especificacao"] == "principal")]
    if len(ref) != 1:
        raise FalhaValidacao(f"E7: {len(ref)} linhas F3.1/U/0.300/principal")
    ref = ref.iloc[0]
    res = {"referencia": "E7_estimativas.csv: F3.1, U, 0.300, principal (doc 43)",
           "funcao": "rdd_lib.rd_dird_delta (h = 0,050, kernel triangular, HC1)",
           "tau_e7": float(ref["tau"]), "tau_reproduzido": float(r["tau"]),
           "dif_tau": abs(float(ref["tau"]) - float(r["tau"])),
           "ep_e7": float(ref["ep"]), "ep_reproduzido": float(r["ep"]),
           "dif_ep": abs(float(ref["ep"]) - float(r["ep"])),
           "n_e7": [int(ref["n_abaixo"]), int(ref["n_acima"])], "n_reproduzido": [int(r["n_abaixo"]), int(r["n_acima"])],
           "tolerancia": TOL_PORTAO}
    res["aprovado"] = bool(res["dif_tau"] <= TOL_PORTAO and res["dif_ep"] <= TOL_PORTAO
                           and res["n_e7"] == res["n_reproduzido"])
    if not res["aprovado"]:
        raise FalhaValidacao(f"portão de reprodução do F3.1 (U, 0,300) falhou: {res}")
    return res


# ---------------------------------------------------------------------------
# 3. Estimadores (chamadas à rdd_lib)
# ---------------------------------------------------------------------------

COLUNAS_EST = ["natureza_dos_dados", "estatuto", "parte", "id_oc", "outcome_id", "descricao_outcome", "papel",
               "populacao", "corte", "especificacao", "h", "n_abaixo", "n_acima", "n_obs", "n_fora_sem_dado", "tau",
               "ep", "ic95_inf", "ic95_sup", "p_valor", "gl", "f_robusto", "tau_forma_reduzida",
               "tau_primeiro_estagio", "ar_ic_inf", "ar_ic_sup", "ar_aberto_inf", "ar_aberto_sup", "ar_n_intervalos",
               "ar_ilimitado", "ar_p_beta0", "ar_grade_L", "ar_grade_n", "M", "vies_max", "n_tratados", "familia_multipla", "p_holm", "q_bky",
               "unidade", "contraste", "nota"]

COLUNAS_EVENTO = ["natureza_dos_dados", "estatuto", "outcome_id", "populacao", "corte", "competencia", "janela",
                  "referencia", "h", "n_abaixo", "n_acima", "tau", "ep", "ic95_inf", "ic95_sup", "p_valor", "unidade",
                  "nota"]


def linha(parte: str, id_oc: str, outcome_id: str, populacao: str, corte, especificacao: str, *, papel: str = "",
          desc: str = "", unidade: str = "", contraste: str = "", h_mil=H, res: dict | None = None, **extra) -> dict:
    ln = {c: np.nan for c in COLUNAS_EST}
    ln.update({"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "parte": parte, "id_oc": id_oc,
               "outcome_id": outcome_id, "descricao_outcome": desc, "papel": papel, "populacao": populacao,
               "corte": ROTULO_CORTE.get(corte, corte), "especificacao": especificacao,
               "h": h_mil / 1000.0 if h_mil is not None else np.nan, "unidade": unidade, "contraste": contraste,
               "familia_multipla": "", "nota": ""})
    if res is not None:
        for k in ("tau", "ep", "ic95_inf", "ic95_sup", "p_valor", "n_abaixo", "n_acima", "n_obs"):
            v = res.get(k)
            if v is not None:
                ln[k] = v
        ln["n_fora_sem_dado"] = res.get("n_descartadas_y_ausente", np.nan)
        ln["nota"] = res.get("nota", "") or ""
    for k, v in extra.items():
        ln[k] = v
    return ln


def janela_de(comp: str) -> str:
    if comp == COMP_REF:
        return "referencia"
    if comp in COMP_PRE:
        return "pre"
    if comp in COMP_POS:
        return "pos"
    return "transicao"


def anderson_rubin(s: np.ndarray, dy: np.ndarray, d: np.ndarray, corte: int, h_mil=H) -> dict:
    """IC de Anderson–Rubin por inversão em grade (decisão D8): β aceito se o p de `rd_local_linear` de
    ΔY − β·D (mesmo kernel, h e HC1) é ≥ 0,05."""
    ok = np.isfinite(dy) & np.isfinite(d)
    x = s - corte
    dentro = ok & (x > -h_mil) & (x < h_mil)
    s, dy, d = s[dentro], dy[dentro], d[dentro]
    Lg = GRADE_AR_FATOR * float(np.max(np.abs(dy))) if dy.size else float("nan")
    out = {"ar_grade_L": Lg, "ar_grade_n": GRADE_AR_N}
    if not (np.isfinite(Lg) and Lg > 0):
        out.update({"ar_ic_inf": np.nan, "ar_ic_sup": np.nan, "ar_n_intervalos": 0, "p_beta0": np.nan,
                    "ar_aberto_inf": False, "ar_aberto_sup": False, "nota_ar": "grade indefinida (ΔY sem variação)"})
        return out

    def p(b: float) -> float:
        return float(L.rd_local_linear(s, dy - b * d, corte, h_mil)["p_valor"])

    grade = np.linspace(-Lg, Lg, GRADE_AR_N)
    pv = np.array([p(b) for b in grade])
    aceita = pv >= ALFA
    out["p_beta0"] = p(0.0)
    if not aceita.any():
        out.update({"ar_ic_inf": np.nan, "ar_ic_sup": np.nan, "ar_n_intervalos": 0, "ar_aberto_inf": False,
                    "ar_aberto_sup": False, "nota_ar": "nenhum β da grade aceito"})
        return out

    def fronteira(a: float, r: float) -> float:
        """Bisseção entre um β aceito (a) e um rejeitado (r)."""
        for _ in range(BISSECAO_AR):
            m = (a + r) / 2
            if p(m) >= ALFA:
                a = m
            else:
                r = m
        return a

    i = np.flatnonzero(aceita)
    runs = np.split(i, np.flatnonzero(np.diff(i) > 1) + 1)
    lo_i, hi_i = runs[0][0], runs[-1][-1]
    aberto_inf, aberto_sup = bool(lo_i == 0), bool(hi_i == GRADE_AR_N - 1)
    lo = grade[0] if aberto_inf else fronteira(grade[lo_i], grade[lo_i - 1])
    hi = grade[-1] if aberto_sup else fronteira(grade[hi_i], grade[hi_i + 1])
    nota = []
    if aberto_inf or aberto_sup:
        nota.append("conjunto aceito toca a borda da grade: aberto do lado " +
                    " e ".join(t for t, f in (("de baixo", aberto_inf), ("de cima", aberto_sup)) if f))
    if len(runs) > 1:
        nota.append(f"conjunto aceito com {len(runs)} intervalos na grade; relatada a envoltória")
    out.update({"ar_ic_inf": float(lo), "ar_ic_sup": float(hi), "ar_n_intervalos": int(len(runs)),
                "ar_aberto_inf": aberto_inf, "ar_aberto_sup": aberto_sup, "nota_ar": "; ".join(nota)})
    return out


NOTA_FRACO = "instrumento_fraco_F<10"


def ar_para_csv(ar: dict) -> dict:
    """Forma do IC de AR no CSV (auditoria 39, achado B1): o lado aberto não grava a borda da grade como limite.
    Aberto dos dois lados num só intervalo = reta inteira na grade: `ar_ilimitado = True` e os dois limites vazios."""
    out = dict(ar)
    ab_inf, ab_sup = bool(ar.get("ar_aberto_inf")), bool(ar.get("ar_aberto_sup"))
    out["ar_ilimitado"] = bool(ab_inf and ab_sup and ar.get("ar_n_intervalos") == 1)
    if ab_inf:
        out["ar_ic_inf"] = np.nan
    if ab_sup:
        out["ar_ic_sup"] = np.nan
    if out["ar_ilimitado"]:
        out["nota_ar"] = ("ar_ilimitado = True: o conjunto de AR aceita todo β da grade (reta inteira); ar_ic_inf e "
                          "ar_ic_sup vazios, a borda da grade (ar_grade_L) não é limite do IC")
    elif ab_inf or ab_sup:
        out["nota_ar"] = ((ar.get("nota_ar") or "") + "; o limite do lado aberto fica vazio (a borda da grade não é "
                          "limite do IC)").lstrip("; ")
    return out


def wald_pre_corte(s: np.ndarray, larga: pd.DataFrame, corte: int) -> dict:
    """Wald conjunto do pré do OC-C (decisão D11): τ_t = 0 nos 12 meses de 202406 a 202505, covariância HC1
    conjunta das regressões mensais de `rd_local_linear` (pesos lineares da biblioteca), nos municípios com todos
    esses meses e a referência observados."""
    Y = larga[list(MESES_PRE_PLANO)].to_numpy(float) - larga[[COMP_REF]].to_numpy(float)
    ok = np.isfinite(Y).all(axis=1)
    taus, res, a0, usa0, fator = [], [], None, None, None
    for j in range(Y.shape[1]):
        r = L.rd_local_linear(s[ok], Y[ok, j], corte, H, detalhes=True)
        det = r["_detalhes"]
        fit = det["fit"]
        a = L._pesos_lineares(fit)
        if a0 is None:
            a0, usa0, fator = a, det["usa"], fit["fator"]
        elif not (np.array_equal(usa0, det["usa"]) and np.allclose(a, a0, rtol=0, atol=1e-12)):
            raise FalhaValidacao("Wald do pré: amostra ou pesos diferem entre meses")
        tau = float(a @ fit["y"])
        if abs(tau - r["tau"]) > 1e-9 * max(1.0, abs(tau)):
            raise FalhaValidacao("Wald do pré: pesos lineares não reproduzem o salto")
        taus.append(tau)
        res.append(fit["residuos"])
    E = np.column_stack(res)
    Vm = fator * (E * (a0 ** 2)[:, None]).T @ E
    ep = np.sqrt(np.diag(Vm))
    ep_lib = np.array([L.rd_local_linear(s[ok], Y[ok, j], corte, H)["ep"] for j in range(Y.shape[1])])
    if not np.allclose(ep, ep_lib, rtol=1e-9, atol=1e-12):
        raise FalhaValidacao("Wald do pré: covariância conjunta não reproduz o EP HC1 de cada mês")
    t = np.array(taus)
    W = float(t @ np.linalg.pinv(Vm) @ t)
    gl = int(np.linalg.matrix_rank(Vm))
    return {"wald": W, "gl": gl, "p_valor": float(stats.chi2.sf(W, gl)) if gl else np.nan,
            "n_municipios_completos": int(ok.sum()), "n_municipios_fora": int((~ok).sum()),
            "n_na_janela": int(usa0.sum())}


def att_pos(Y: np.ndarray, G: np.ndarray, coortes: list[int], xi: np.ndarray) -> tuple[dict, np.ndarray]:
    """ATT médio do pós (e = 0..6) e sua função de influência, com as funções do script 22 (as do 37)."""
    r = D2M.estimar_cs(Y, G, coortes, xi, e_min=E_MIN, e_max=E_MAX)
    tab, IF = D2M.att_gt(Y, G, coortes, e_min=E_MIN, e_max=E_MAX)
    ev, IFe = D2M.agregar_evento(tab, IF, G, e_min=E_MIN, e_max=E_MAX)
    th = ev["theta"].to_numpy(float)
    e = ev["e"].to_numpy()
    post = (e >= 0) & np.isfinite(th)
    psi = IFe[:, post].mean(axis=1) if post.any() else np.full(Y.shape[0], np.nan)
    if post.any():
        pert = xi @ psi / len(psi)
        q75, q25 = np.percentile(pert, [75, 25])
        if abs((q75 - q25) / D2M.Z_IQR - r["pos"]["ep"]) > 1e-12 or abs(th[post].mean() - r["pos"]["att"]) > 1e-12:
            raise FalhaValidacao("função de influência do ATT médio do pós não reproduz o estimar_cs")
    return r["pos"], psi


# ---------------------------------------------------------------------------
# 4. Partes A–E
# ---------------------------------------------------------------------------

def parte_a(dados: dict, pop_nome: str, amostra: pd.Index) -> tuple[list[dict], dict, dict]:
    """Forma reduzida (principal) e sensibilidades de ΔB1–ΔB5 numa população."""
    s = dados["base"].loc[amostra, "s_mil"].to_numpy(float)
    linhas, bases, faltas = [], {}, {}
    for oid in IDS:
        d = deltas(taxa(dados["niveis"][oid].reindex(amostra), dados["pop"]))
        bases[oid] = d
        faltas[oid] = {"sem_todos_os_meses_do_pre": int(d.attrs.get("n_unidades_incompletas_pre", 0)),
                       "sem_todos_os_meses_do_pos": int(d.attrs.get("n_unidades_incompletas_pos", 0)),
                       "sem_delta": int(d["delta"].isna().sum())}
        yp, yr = d["y_pos"].to_numpy(float), d["y_pre"].to_numpy(float)
        meta = dict(desc=SPEC[oid]["desc"], unidade=SPEC[oid]["unidade"], contraste=CONTRASTE_A)
        id_oc = ID_OC[oid] if pop_nome == "V" else "OC-A-U"
        papel = (("primaria" if oid in PRIMARIAS else "secundaria") if pop_nome == "V" else "sensibilidade")
        for corte in CORTES:
            r = L.rd_dird_delta(s, yp, yr, corte, H)
            ln = linha("A", id_oc, oid, pop_nome, corte, "principal", papel=papel, res=r, **meta)
            if pop_nome == "V":
                ln["familia_multipla"] = "holm" if oid in PRIMARIAS else "bky"
            linhas.append(ln)
            for h in H_SENS:
                linhas.append(linha("A", id_oc, oid, pop_nome, corte, "sensibilidade_h", papel="sensibilidade",
                                    h_mil=h, res=L.rd_dird_delta(s, yp, yr, corte, h), **meta))
            tab = L.rd_honesto_relato(s, yp - yr, corte, fatores_M=(1.0,), cortes_vizinhos=CORTES)
            hf = tab[tab["especificacao"] == "h_fixo"].iloc[0].to_dict()
            linhas.append(linha("A", id_oc, oid, pop_nome, corte, "ic_honesto", papel="sensibilidade",
                                res={k: hf.get(k) for k in ("tau", "ep", "ic95_inf", "ic95_sup", "p_valor",
                                                            "n_abaixo", "n_acima", "nota")},
                                M=hf.get("M"), vies_max=hf.get("vies_max"), **meta))
            rc = L.rd_local_linear(s, yp, corte, H, Z=yr.reshape(-1, 1), nomes_z=["y_pre"])
            linhas.append(linha("A", id_oc, oid, pop_nome, corte, "pos_com_pre_covariavel", papel="sensibilidade",
                                res=rc, **meta))
    return linhas, bases, faltas


def primeiro_estagio(s: np.ndarray, d: np.ndarray, corte: int) -> dict:
    r = L.rd_local_linear(s, d, corte, H)
    r["f_robusto"] = (r["tau"] / r["ep"]) ** 2 if np.isfinite(r["ep"]) and r["ep"] > 0 else np.nan
    return r


def parte_b(dados: dict, bases_V: dict, bases_U: dict) -> tuple[list[dict], dict]:
    """Primeiro estágio (B0) e razão fuzzy com IC de Anderson–Rubin (B1–B5)."""
    base, U, V = dados["base"], dados["U"], dados["V"]
    D1_U = (dados["ch_U"]["chegada"].notna() & (dados["ch_U"]["chegada"].fillna("999999") <= MESES[-1])).astype(float)
    D1_V = D1_U.reindex(V)
    if not np.array_equal(D1_V.to_numpy() == 1, dados["G"] >= 0):
        raise FalhaValidacao("D1 em V difere dos tratados do script 37")
    comp_ini = min(dados["ch_total"]["chegada"].dropna())
    n_d2, info_d2 = contar_d2(dados["x1"], dados["cbos"], U, comp_ini)
    D2_U = n_d2 / dados["pop"].reindex(U) * ESCALA_HAB
    endog = {("D1", "V"): D1_V, ("D1", "U"): D1_U, ("D2", "V"): D2_U.reindex(V)}
    info = {"D1_V_tratados": int(D1_V.sum()), "D1_U_tratados": int(D1_U.sum()), "D2": info_d2}
    linhas = []
    fs = {}
    for (dn, pn), D in endog.items():
        amostra = V if pn == "V" else U
        s = base.loc[amostra, "s_mil"].to_numpy(float)
        desc = ("D1: recebeu >= 1 médico do PMM-E dos ciclos 1 e 2 até 202608" if dn == "D1" else
                "D2: médicos do PMM-E (ciclos 1 e 2) ligados ao CNES em estabelecimento do município, por 10 mil hab.")
        un = "fração (x100 = p.p.)" if dn == "D1" else "médicos por 10 mil hab. (Censo 2022)"
        for corte in CORTES:
            r = primeiro_estagio(s, D.to_numpy(float), corte)
            fs[(dn, pn, corte)] = r
            principal = dn == "D1" and pn == "V"
            ln = linha("B", "OC-B0", dn, pn, corte, "primeiro_estagio", papel="secundaria" if principal else
                       "sensibilidade", desc=desc, unidade=un, contraste=CONTRASTE_B0, res=r, f_robusto=r["f_robusto"])
            if principal:
                ln["familia_multipla"] = "bky"
            linhas.append(ln)
    for (dn, pn), D in endog.items():
        amostra = V if pn == "V" else U
        bases = bases_V if pn == "V" else bases_U
        s = base.loc[amostra, "s_mil"].to_numpy(float)
        dv = D.to_numpy(float)
        principal = dn == "D1" and pn == "V"
        for oid in IDS:
            dy = bases[oid]["delta"].to_numpy(float)
            ok = np.isfinite(dy)
            for corte in CORTES:
                rf = L.rd_local_linear(s[ok], dy[ok], corte, H)
                fsr = primeiro_estagio(s[ok], dv[ok], corte)
                ar = anderson_rubin(s, dy, dv, corte)
                if np.isfinite(ar["p_beta0"]) and abs(ar["p_beta0"] - rf["p_valor"]) > 1e-12:
                    raise FalhaValidacao("AR em β = 0 difere do p da forma reduzida na mesma amostra")
                razao = rf["tau"] / fsr["tau"] if np.isfinite(fsr["tau"]) and fsr["tau"] != 0 else np.nan
                fraco = not (fsr["f_robusto"] >= F_FRACO)
                ar_csv = ar_para_csv(ar)
                nota = "; ".join(t for t in (
                    f"{NOTA_FRACO}: tau, ep, IC convencional e p vazios (razão sem estimativa pontual utilizável); "
                    "só o IC de AR" if fraco else "", ar_csv["nota_ar"],
                    "p de Anderson-Rubin em β = 0 (= p da forma reduzida na mesma amostra) em ar_p_beta0; é o p que "
                    "entra no BKY") if t)
                # Auditoria 39, achado B1 (correção de formato pedida pelo autor em 26/10/2026): com instrumento
                # fraco a linha não grava ponto, EP, IC convencional nem p; o p de AR em β = 0 fica em ar_p_beta0.
                res_b = {"n_abaixo": rf["n_abaixo"], "n_acima": rf["n_acima"], "n_obs": rf["n_obs"], "nota": nota}
                if not fraco:
                    res_b.update({"tau": razao, "p_valor": ar["p_beta0"]})
                ln = linha("B", f"OC-B{oid[1]}", oid, pn, corte, f"fuzzy_{dn}",
                           papel="secundaria" if principal else "sensibilidade", desc=SPEC[oid]["desc"],
                           unidade=f"{SPEC[oid]['unidade']} por município que recebe médico" if dn == "D1" else
                           f"{SPEC[oid]['unidade']} por médico do PMM-E por 10 mil hab.",
                           contraste=CONTRASTE_B, res=res_b,
                           f_robusto=fsr["f_robusto"], tau_forma_reduzida=rf["tau"], tau_primeiro_estagio=fsr["tau"],
                           n_fora_sem_dado=int((~ok & (np.abs(s - corte) < H)).sum()), ar_p_beta0=ar["p_beta0"],
                           **{k: ar_csv[k] for k in ("ar_ic_inf", "ar_ic_sup", "ar_aberto_inf", "ar_aberto_sup",
                                                     "ar_n_intervalos", "ar_ilimitado", "ar_grade_L", "ar_grade_n")})
                if principal:
                    ln["familia_multipla"] = "bky"
                linhas.append(ln)
                print(f"B {dn}/{pn} {oid} {corte}: AR feito", flush=True)
    return linhas, info


def parte_c(dados: dict) -> tuple[list[dict], list[dict], dict]:
    """Estudo de evento no corte (rd_estudo_evento) e Wald conjunto do pré, em V."""
    V, base = dados["V"], dados["base"]
    s = base.loc[V, "s_mil"].to_numpy(float)
    ev_linhas, est_linhas, pre = [], [], {}
    for oid in OUTCOMES_EVENTO:
        larga = taxa(dados["niveis"][oid].reindex(V), dados["pop"])
        longa = _longa(larga)
        longa["s_mil"] = longa["co_ibge"].map(base["s_mil"]).astype(float)
        for corte in CORTES:
            ev = L.rd_estudo_evento(longa, col_unidade="co_ibge", col_periodo="competencia", col_y="y", col_s="s_mil",
                                    corte_mil=corte, periodo_ref=COMP_REF, h_mil=H, periodos=list(MESES))
            for r in ev.to_dict("records"):
                ev_linhas.append({"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "outcome_id": oid,
                                  "populacao": "V", "corte": ROTULO_CORTE[corte], "competencia": r["periodo"],
                                  "janela": janela_de(r["periodo"]), "referencia": bool(r["referencia"]),
                                  "unidade": SPEC[oid]["unidade"],
                                  **{k: r[k] for k in ("h", "n_abaixo", "n_acima", "tau", "ep", "ic95_inf",
                                                       "ic95_sup", "p_valor", "nota")}})
            w = wald_pre_corte(s, larga, corte)
            pre[(oid, corte)] = w
            est_linhas.append(linha("C", "OC-C", oid, "V", corte, "pre_wald", papel="diagnostico",
                                    desc=SPEC[oid]["desc"], unidade="estatística de Wald (qui-quadrado)",
                                    contraste=CONTRASTE_C, tau=w["wald"], gl=w["gl"], p_valor=w["p_valor"],
                                    n_obs=w["n_na_janela"], n_fora_sem_dado=w["n_municipios_fora"],
                                    nota=f"Wald conjunto de τ_t = 0 nos {len(MESES_PRE_PLANO)} meses de "
                                         f"{MESES_PRE_PLANO[0]} a {MESES_PRE_PLANO[-1]} (referência {COMP_REF}); "
                                         f"covariância HC1 conjunta; {w['n_municipios_completos']} municípios de V "
                                         "com todos os meses"))
    return ev_linhas, est_linhas, pre


def parte_d(dados: dict) -> tuple[list[dict], dict]:
    """ATT da chegada abaixo e acima de cada corte (decisão D12) e a diferença acima − abaixo."""
    V, base, G, saida = dados["V"], dados["base"], dados["G"], dados["saida"]
    s = base.loc[V, "s_mil"].to_numpy(float)
    pop = dados["pop"].reindex(V).to_numpy(float)
    xi = D2M.pesos_mammen(B_BOOT, len(V), SEMENTE)
    tratado = G >= 0
    linhas, info = [], {}
    taxas = {oid: dados["niveis"][oid].reindex(V).to_numpy(float) / pop[:, None] * ESCALA_HAB for oid in OUTCOMES_D}
    for corte in CORTES:
        x = s - corte
        grupos = {"abaixo": tratado & (x > -H) & (x <= 0), "acima": tratado & (x > 0) & (x < H)}
        info[ROTULO_CORTE[corte]] = {k: int(m.sum()) for k, m in grupos.items()}
        for oid in OUTCOMES_D:
            res, psis = {}, {}
            for lado, m in grupos.items():
                Gs, ss = G.copy(), saida.copy()
                fora = tratado & ~m
                ss[fora] = G[fora]          # tratado fora do grupo: controle até a chegada, depois sai
                Gs[fora] = -1
                coortes = sorted({int(g) for g in Gs[Gs >= 0]})
                Y = OL.censurar(taxas[oid], ss)
                if not coortes:
                    res[lado] = {"att": np.nan, "ep": np.nan, "ic95_inf": np.nan, "ic95_sup": np.nan,
                                 "p_valor": np.nan}
                    psis[lado] = np.full(len(V), np.nan)
                else:
                    res[lado], psis[lado] = att_pos(Y, Gs, coortes, xi)
                r = res[lado]
                linhas.append(linha("D", "OC-D", oid, "V", corte, f"chegada_{lado}", papel="secundaria (componente)",
                                    desc=SPEC[oid]["desc"], unidade=SPEC[oid]["unidade"], contraste=CONTRASTE_D,
                                    h_mil=H, tau=r["att"], ep=r["ep"], ic95_inf=r["ic95_inf"], ic95_sup=r["ic95_sup"],
                                    p_valor=r["p_valor"], n_tratados=int(m.sum()),
                                    nota=f"ATT médio de e = 0..6 (Callaway-Sant'Anna do 37); tratados com "
                                         f"{'−0,050 < IVS − corte ≤ 0' if lado == 'abaixo' else '0 < IVS − corte < 0,050'}"
                                         "; EP bootstrap de Mammen" + ("" if coortes else "; sem tratados no grupo")))
            val = res["acima"]["att"] - res["abaixo"]["att"]
            psi = psis["acima"] - psis["abaixo"]
            if np.isfinite(psi).all() and np.isfinite(val):
                pert = xi @ psi / len(psi)
                q75, q25 = np.percentile(pert, [75, 25])
                ep = float((q75 - q25) / D2M.Z_IQR)
            else:
                ep = np.nan
            p = L.p_normal(val / ep) if np.isfinite(ep) and ep > 0 else np.nan
            ln = linha("D", "OC-D", oid, "V", corte, "chegada_diferenca", papel="secundaria", desc=SPEC[oid]["desc"],
                       unidade=SPEC[oid]["unidade"], contraste=CONTRASTE_D, tau=val, ep=ep,
                       ic95_inf=val - L.Z_975 * ep, ic95_sup=val + L.Z_975 * ep, p_valor=p,
                       n_tratados=int(sum(m.sum() for m in grupos.values())),
                       nota="acima − abaixo; EP bootstrap de Mammen (B = 9.999, semente 20261026) sobre a diferença "
                            "das funções de influência, com os mesmos pesos")
            ln["familia_multipla"] = "bky"
            linhas.append(ln)
            print(f"D {oid} {corte}: dif {val:.3f}", flush=True)
    del xi
    return linhas, info


def parte_e(dados: dict) -> tuple[list[dict], dict]:
    U, base = dados["U"], dados["base"]
    s = base.loc[U, "s_mil"].to_numpy(float)
    cel = pd.Series(U.isin(dados["am_total"]), index=U).astype(float)
    linhas = []
    for corte in CORTES:
        r = L.rd_local_linear(s, cel.to_numpy(float), corte, H)
        linhas.append(linha("E", "OC-E", "celula_algum_ciclo", "U", corte, "principal", papel="diagnostico",
                            desc="município com célula em algum ciclo (1 a 3)", unidade="fração (x100 = p.p.)",
                            contraste=CONTRASTE_E, res=r))
    return linhas, {"U_com_celula": int(cel.sum()), "U": int(len(U))}


def p_familia(est: pd.DataFrame) -> pd.Series:
    """p que entra em Holm/BKY: `p_valor`; nas linhas fuzzy (D10), o p de AR em β = 0 (`ar_p_beta0`), que fica fora
    de `p_valor` quando o instrumento é fraco (auditoria 39, B1). A família e os p usados não mudam."""
    fuzzy = est["especificacao"].astype(str).str.startswith("fuzzy")
    return est["p_valor"].where(~fuzzy, est["ar_p_beta0"]).astype(float)


def aplicar_multiplos(est: pd.DataFrame) -> pd.DataFrame:
    est = est.copy()
    est["p_holm"] = np.nan
    est["q_bky"] = np.nan
    p_fam = p_familia(est)
    for fam, col, fn in (("holm", "p_holm", L.holm), ("bky", "q_bky", L.qvalores_bky)):
        m = est["familia_multipla"] == fam
        est.loc[m, col] = fn(p_fam[m].to_numpy(float))
    return est


# ---------------------------------------------------------------------------
# 5. Leitura pré-registrada (protocolo 64, §4; decisões D14 e D15)
# ---------------------------------------------------------------------------

def _sel(est: pd.DataFrame, **kw) -> pd.DataFrame:
    m = np.ones(len(est), dtype=bool)
    for k, v in kw.items():
        m &= (est[k] == v).to_numpy()
    return est[m]


def _um(est: pd.DataFrame, **kw) -> pd.Series:
    r = _sel(est, **kw)
    if len(r) != 1:
        raise KeyError(f"{len(r)} linhas para {kw}")
    return r.iloc[0]


def _contem_zero(r) -> bool:
    return bool(r["ic95_inf"] <= 0 <= r["ic95_sup"])


def classificar(est: pd.DataFrame) -> dict:
    c = {"primarias": {}, "placebo_rejeita": {}, "pre_plano": {}, "f_robusto": {}, "fraco": {}, "d": {}, "e": {}}
    for oid in PRIMARIAS:
        for corte in CORTES:
            r = _um(est, parte="A", outcome_id=oid, populacao="V", corte=ROTULO_CORTE[corte], especificacao="principal")
            c["primarias"][f"{oid}|{ROTULO_CORTE[corte]}"] = {
                "tau": float(r["tau"]), "contem_zero": _contem_zero(r), "p_holm": float(r["p_holm"]),
                "rejeita_holm": bool(r["p_holm"] < ALFA)}
    for corte in CORTES:
        k = ROTULO_CORTE[corte]
        r5 = _um(est, parte="A", outcome_id="B5", populacao="V", corte=k, especificacao="principal")
        c["placebo_rejeita"][k] = bool(r5["q_bky"] < ALFA)
        for oid in OUTCOMES_EVENTO:
            w = _um(est, parte="C", outcome_id=oid, corte=k, especificacao="pre_wald")
            c["pre_plano"][f"{oid}|{k}"] = bool(w["p_valor"] >= ALFA)
        fs = _um(est, parte="B", outcome_id="D1", populacao="V", corte=k, especificacao="primeiro_estagio")
        c["f_robusto"][k] = float(fs["f_robusto"])
        c["fraco"][k] = bool(not (fs["f_robusto"] >= F_FRACO))
        for oid in OUTCOMES_D:
            d = _um(est, parte="D", outcome_id=oid, corte=k, especificacao="chegada_diferenca")
            c["d"][f"{oid}|{k}"] = {"contem_zero": _contem_zero(d)}
        e = _um(est, parte="E", corte=k)
        c["e"][k] = bool(e["p_valor"] < ALFA)
    a3 = [ROTULO_CORTE[k] for k in CORTES
          if (lambda r: r["tau"] < 0 and r["ic95_sup"] < 0)(_um(est, parte="A", outcome_id="B3", populacao="V",
                                                                corte=ROTULO_CORTE[k], especificacao="principal"))]
    c["a3_deslocamento_cortes"] = a3
    prim = c["primarias"]
    rejeitam = [k for k, v in prim.items() if v["rejeita_holm"]]
    if all(v["contem_zero"] for v in prim.values()):
        caso = "nulo"
    elif rejeitam:
        limpos = [k for k in rejeitam if not c["placebo_rejeita"][k.split("|")[1]] and c["pre_plano"][k]]
        caso = "pacote" if limpos else "nao_ler"
        c["rejeitam_limpos"] = limpos
    else:
        caso = "descritivo"
    c["caso_primarias"] = caso
    c["rejeitam_holm"] = rejeitam
    c["v_selecionada"] = any(c["e"].values())
    return c


def _n(v, casas: int = 2, sinal: bool = True) -> str:
    return OL._n(v, casas, sinal)


def _p(v) -> str:
    return OL._p(v)


def _p_igual(v) -> str:
    return OL._p_igual(v)


def _ic(lo, hi, casas: int = 2) -> str:
    return f"[{_n(lo, casas)}; {_n(hi, casas)}]"


def _corte_txt(k: str) -> str:
    return k.replace(".", ",")


NOME_CURTO = {"B1": "vínculos de especialistas (B1)", "B2": "horas SUS de especialistas (B2)",
              "B3": "horas SUS dos outros especialistas (B3)", "B4": "horas totais (B4)",
              "B5": "vínculos de generalistas, o placebo (B5)"}


def _verdade(v) -> bool:
    return v is True or isinstance(v, (bool, np.bool_)) and bool(v) or str(v) == "True"


def _ar_txt(r) -> str:
    if not (r["ar_n_intervalos"] >= 1):
        return "vazio na grade"
    if _verdade(r["ar_ilimitado"]):
        return f"ilimitado (aceita todo β da grade, ±{_n(r['ar_grade_L'], 2, False)})"
    lo = "−∞ (aberto)" if _verdade(r["ar_aberto_inf"]) else _n(r["ar_ic_inf"])
    hi = "+∞ (aberto)" if _verdade(r["ar_aberto_sup"]) else _n(r["ar_ic_sup"])
    extra = f", {int(r['ar_n_intervalos'])} intervalos" if r["ar_n_intervalos"] > 1 else ""
    return f"[{lo}; {hi}]{extra}"


def gerar_leitura(est: pd.DataFrame) -> str:
    c = classificar(est)
    f = []
    prim = []
    for oid in PRIMARIAS:
        for corte in CORTES:
            k = ROTULO_CORTE[corte]
            r = _um(est, parte="A", outcome_id=oid, populacao="V", corte=k, especificacao="principal")
            prim.append(f"{NOME_CURTO[oid]} em {_corte_txt(k)}: {_n(r['tau'])} {_ic(r['ic95_inf'], r['ic95_sup'])}, "
                        f"p de Holm {_p(r['p_holm'])}")
    f.append("Parte A, primárias em V (salto da mudança pós − pré, lado de cima menos lado de baixo): "
             + "; ".join(prim) + ".")
    caso = c["caso_primarias"]
    if caso == "nulo":
        f.append("Os quatro IC contêm zero. Pela leitura pré-registrada: comparando os dois lados do corte, a mudança "
                 "na oferta local de especialistas não se distingue; o corte não detecta efeito do pacote sobre a "
                 "oferta local.")
    elif caso == "pacote":
        quais = ", ".join(c["rejeitam_limpos"])
        f.append(f"Rejeita zero depois do Holm, com placebo que não rejeita e pré plano: {quais}. Pela leitura "
                 "pré-registrada, o sinal e o tamanho são do pacote do corte sobre a mudança na oferta local, não da "
                 "bolsa sozinha.")
    elif caso == "nao_ler":
        f.append("Alguma primária rejeita zero depois do Holm, mas o placebo (B5) também rejeita ou o pré do estudo de "
                 "evento não é plano. Pela leitura pré-registrada, isso não é lido como efeito da bolsa nem da "
                 "chegada: pode ser outra regra no corte ou tendência.")
    else:
        f.append("Algum IC das primárias exclui zero, mas nenhuma rejeita zero depois do Holm. Isso fica como "
                 "descrição, sem leitura de efeito do pacote (decisão D15).")
    pl = []
    for corte in CORTES:
        k = ROTULO_CORTE[corte]
        r = _um(est, parte="A", outcome_id="B5", populacao="V", corte=k, especificacao="principal")
        pl.append(f"{_corte_txt(k)}: {_n(r['tau'])} {_ic(r['ic95_inf'], r['ic95_sup'])}, q BKY {_p(r['q_bky'])}")
    f.append("Placebo de generalistas (OC-A5): " + "; ".join(pl) + ". "
             + ("O placebo se move em algum corte: as outras regras do corte podem estar mexendo na oferta."
                if any(c["placebo_rejeita"].values()) else "O placebo não se distingue de zero nos dois cortes."))
    a3 = []
    for corte in CORTES:
        k = ROTULO_CORTE[corte]
        r = _um(est, parte="A", outcome_id="B3", populacao="V", corte=k, especificacao="principal")
        a3.append(f"{_corte_txt(k)}: {_n(r['tau'])} {_ic(r['ic95_inf'], r['ic95_sup'])}")
    f.append("Outros especialistas (OC-A3): " + "; ".join(a3) + ". "
             + (f"Negativo com IC abaixo de zero em {', '.join(_corte_txt(k) for k in c['a3_deslocamento_cortes'])}: "
                "sinal de deslocamento dos outros especialistas no corte."
                if c["a3_deslocamento_cortes"] else "Não há sinal de deslocamento dos outros especialistas no corte."))
    pre = []
    for oid in OUTCOMES_EVENTO:
        for corte in CORTES:
            k = ROTULO_CORTE[corte]
            w = _um(est, parte="C", outcome_id=oid, corte=k, especificacao="pre_wald")
            pre.append(f"{oid} em {_corte_txt(k)} {_p_igual(w['p_valor'])}")
    planos = [k for k, v in c["pre_plano"].items() if not v]
    f.append("Estudo de evento no corte (OC-C), teste conjunto do pré: " + "; ".join(pre) + ". "
             + ("O pré é plano em todos." if not planos else
                "O pré não é plano em " + ", ".join(x.replace("|", " em ").replace(".", ",") for x in planos) + "."))
    fs = []
    for corte in CORTES:
        k = ROTULO_CORTE[corte]
        r = _um(est, parte="B", outcome_id="D1", populacao="V", corte=k, especificacao="primeiro_estagio")
        fs.append(f"{_corte_txt(k)}: salto de {_n(100 * r['tau'], 1)} p.p. em receber médico "
                  f"{_ic(100 * r['ic95_inf'], 100 * r['ic95_sup'], 1)}, F robusto = {_n(r['f_robusto'], 1, False)}")
    f.append("Primeiro estágio (OC-B0, D1 em V): " + "; ".join(fs) + ".")
    for corte in CORTES:
        k = ROTULO_CORTE[corte]
        if c["fraco"][k]:
            ars = []
            for oid in PRIMARIAS:
                r = _um(est, parte="B", outcome_id=oid, populacao="V", corte=k, especificacao="fuzzy_D1")
                ars.append(f"{oid} {_ar_txt(r)}")
            f.append(f"Em {_corte_txt(k)} o instrumento é fraco (F robusto < 10): a razão fuzzy não tem estimativa "
                     "pontual utilizável. Só o IC de Anderson–Rubin vale: " + "; ".join(ars) + ".")
        else:
            rs = []
            for oid in PRIMARIAS:
                r = _um(est, parte="B", outcome_id=oid, populacao="V", corte=k, especificacao="fuzzy_D1")
                rs.append(f"{oid} {_n(r['tau'])} (IC de Anderson–Rubin {_ar_txt(r)})")
            f.append(f"Em {_corte_txt(k)} o primeiro estágio tem F robusto ≥ 10. Razão fuzzy: " + "; ".join(rs)
                     + ". Só vale como efeito de receber médico para quem recebe por causa do corte se o corte mexer "
                       "na oferta apenas pelo médico do programa; o pacote do corte pode violar isso.")
    dz = [k for k, v in c["d"].items() if not v["contem_zero"]]
    f.append("Chegada abaixo e acima do corte (OC-D): "
             + ("a diferença entre lados tem IC que contém zero em B1, B2 e B3 nos dois cortes; não se detecta que a "
                "chegada mude a oferta de forma diferente onde a bolsa é maior. São poucos tratados perto de cada "
                "corte (seção 5.6)." if not dz else
                "a diferença entre lados exclui zero em " + ", ".join(x.replace("|", " em ").replace(".", ",")
                                                                    for x in dz)
                + "; é heterogeneidade por lado do corte, com poucos tratados, não efeito da bolsa."))
    e = []
    for corte in CORTES:
        k = ROTULO_CORTE[corte]
        r = _um(est, parte="E", corte=k)
        e.append(f"{_corte_txt(k)}: {_n(100 * r['tau'], 1)} p.p. {_ic(100 * r['ic95_inf'], 100 * r['ic95_sup'], 1)}, "
                 f"{_p_igual(r['p_valor'])}")
    f.append("Seleção de V (OC-E, ter célula em algum ciclo, em U): " + "; ".join(e) + ". "
             + ("V é selecionada em algum corte: dar peso à parte A em U (seção 5.2)." if c["v_selecionada"] else
                "Não se detecta salto: a seleção de V pelo corte não aparece nesse teste."))
    f.append("Tudo aqui compara os lados do corte, que mudam a bolsa e outras regras federais ao mesmo tempo; nada é "
             "efeito da participação no PMM-E como política; vínculo cadastrado não é presença.")
    return " ".join(f)


# ---------------------------------------------------------------------------
# 6. Tabelas do doc 57q
# ---------------------------------------------------------------------------

ROTULO_ESP = {"principal": "principal (h = 0,050)", "sensibilidade_h": "h", "ic_honesto": "IC honesto (h = 0,050)",
              "pos_com_pre_covariavel": "pós com pré como covariável"}


def gerar_tabelas_doc(est: pd.DataFrame, ev: pd.DataFrame, resumo: dict) -> dict[str, str]:
    t = {}
    a = resumo["amostra"]
    linhas = ["| Item | Valor |", "|---|---|",
              f"| U: municípios do IVS oficial (a08) com população 2022 > 0 | {a['U']} |",
              f"| U: municípios do a08 sem população 2022 > 0 (fora) | {a['U_sem_populacao']} |",
              f"| municípios de U com célula em algum ciclo (1 a 3) | {a['U_com_celula']} |",
              f"| fora de V: tratados da lista nominal sem célula nos ciclos 1 ou 2 | {a['excluidos_tratados_fora_d2']} |",
              f"| V (municípios) | {a['V']} |",
              f"| V: receberam médico do PMM-E dos ciclos 1 e 2 até 2026-08 (D1 = 1) | {a['V_tratados']} |"]
    for pn in ("V", "U"):
        for oid in IDS:
            x = a["fora_por_falta_de_mes"][pn][oid]
            linhas.append(f"| {pn}, {oid}: fora por falta de mês (pré / pós / sem ΔY) | {x['sem_todos_os_meses_do_pre']} / "
                          f"{x['sem_todos_os_meses_do_pos']} / {x['sem_delta']} |")
    linhas += ["", "| Corte | V abaixo / acima (h = 0,050) | U abaixo / acima (h = 0,050) |", "|---|---|---|"]
    for corte in CORTES:
        k = ROTULO_CORTE[corte]
        rv = _um(est, parte="A", outcome_id="B1", populacao="V", corte=k, especificacao="principal")
        ru = _um(est, parte="A", outcome_id="B1", populacao="U", corte=k, especificacao="principal")
        linhas.append(f"| {_corte_txt(k)} | {int(rv['n_abaixo'])} / {int(rv['n_acima'])} | {int(ru['n_abaixo'])} / "
                      f"{int(ru['n_acima'])} |")
    t["amostra"] = "\n".join(linhas)
    p = resumo["portao"]
    dif = lambda v: f"{v:.1e}".replace(".", ",")  # noqa: E731
    t["portao"] = "\n".join([
        "| Conferência | E7 (doc 43) | Este script | Diferença | Resultado |", "|---|---|---|---|---|",
        f"| salto do F3.1, U, 0,300 | {_n(p['tau_e7'], 6)} | {_n(p['tau_reproduzido'], 6)} | {dif(p['dif_tau'])} | "
        f"{'sim' if p['dif_tau'] <= p['tolerancia'] else 'NÃO'} |",
        f"| EP HC1 | {_n(p['ep_e7'], 6, False)} | {_n(p['ep_reproduzido'], 6, False)} | {dif(p['dif_ep'])} | "
        f"{'sim' if p['dif_ep'] <= p['tolerancia'] else 'NÃO'} |",
        f"| municípios abaixo / acima | {p['n_e7'][0]} / {p['n_e7'][1]} | {p['n_reproduzido'][0]} / "
        f"{p['n_reproduzido'][1]} | — | {'sim' if p['n_e7'] == p['n_reproduzido'] else 'NÃO'} |"])
    t["leitura"] = gerar_leitura(est)
    linhas = ["| Id | Outcome | Corte | Salto | IC 95% | p | p Holm / q BKY | n abaixo / acima |",
              "|---|---|---|---|---|---|---|---|"]
    for oid in IDS:
        for corte in CORTES:
            k = ROTULO_CORTE[corte]
            r = _um(est, parte="A", outcome_id=oid, populacao="V", corte=k, especificacao="principal")
            aj = f"{_p(r['p_holm'])} (Holm)" if oid in PRIMARIAS else f"{_p(r['q_bky'])} (BKY)"
            linhas.append(f"| {ID_OC[oid]} | {SPEC[oid]['curto']} | {_corte_txt(k)} | {_n(r['tau'])} | "
                          f"{_ic(r['ic95_inf'], r['ic95_sup'])} | {_p(r['p_valor'])} | {aj} | "
                          f"{int(r['n_abaixo'])} / {int(r['n_acima'])} |")
    t["principal"] = "\n".join(linhas) + ("\n\nUnidades: B1 e B5 em vínculos por 10 mil hab.; B2 e B3 em horas SUS "
                                         "semanais por 10 mil hab.; B4 em horas semanais por 10 mil hab.")
    linhas = ["| Outcome | Pop. | Corte | Principal | h = 0,030 | h = 0,080 | IC honesto (M) | Pós com pré covariável |",
              "|---|---|---|---|---|---|---|---|"]
    for oid in IDS:
        for pn in ("V", "U"):
            for corte in CORTES:
                k = ROTULO_CORTE[corte]
                g = _sel(est, parte="A", outcome_id=oid, populacao=pn, corte=k)
                pr = _um(g, especificacao="principal")
                hs = {round(float(r["h"]), 3): r for _, r in _sel(g, especificacao="sensibilidade_h").iterrows()}
                ho = _um(g, especificacao="ic_honesto")
                cv = _um(g, especificacao="pos_com_pre_covariavel")
                cel = lambda r: f"{_n(r['tau'])} {_ic(r['ic95_inf'], r['ic95_sup'])}"  # noqa: E731
                linhas.append(f"| {oid} | {pn} | {_corte_txt(k)} | {cel(pr)} | {cel(hs[0.03])} | {cel(hs[0.08])} | "
                              f"{_ic(ho['ic95_inf'], ho['ic95_sup'])} ({_n(ho['M'], 1, False)}) | {cel(cv)} |")
    t["sensibilidades"] = "\n".join(linhas) + ("\n\nIC honesto: Armstrong–Kolesár, M da regra de bolso (fator 1), "
                                              "como no E7. Nenhuma linha desta tabela entra no Holm ou no BKY.")
    linhas = ["| Variável | Pop. | Corte | Salto | IC 95% | p | q BKY | F robusto | n abaixo / acima |",
              "|---|---|---|---|---|---|---|---|---|"]
    for dn, pn in (("D1", "V"), ("D1", "U"), ("D2", "V")):
        for corte in CORTES:
            k = ROTULO_CORTE[corte]
            r = _um(est, parte="B", outcome_id=dn, populacao=pn, corte=k, especificacao="primeiro_estagio")
            esc, cas = (100, 1) if dn == "D1" else (1, 3)
            linhas.append(f"| {dn} | {pn} | {_corte_txt(k)} | {_n(esc * r['tau'], cas)} | "
                          f"{_ic(esc * r['ic95_inf'], esc * r['ic95_sup'], cas)} | {_p(r['p_valor'])} | "
                          f"{_p(r['q_bky'])} | {_n(r['f_robusto'], 1, False)} | {int(r['n_abaixo'])} / "
                          f"{int(r['n_acima'])} |")
    t["primeiro_estagio"] = "\n".join(linhas) + (
        "\n\nD1 em pontos percentuais (fração de municípios que receberam médico); D2 em médicos do PMM-E ligados por "
        "10 mil hab. A linha principal é D1 em V; as outras são sensibilidade. F robusto = (salto ÷ EP HC1)².")
    linhas = ["| Id | Outcome | Variável / pop. | Corte | F robusto | Forma reduzida | Primeiro estágio | Razão | "
              "IC de Anderson–Rubin | p (β = 0) | q BKY |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for dn, pn in (("D1", "V"), ("D1", "U"), ("D2", "V")):
        for oid in IDS:
            for corte in CORTES:
                k = ROTULO_CORTE[corte]
                r = _um(est, parte="B", outcome_id=oid, populacao=pn, corte=k, especificacao=f"fuzzy_{dn}")
                fraco = not (r["f_robusto"] >= F_FRACO)
                razao = "— (fraco)" if fraco else _n(r["tau"])
                linhas.append(f"| {r['id_oc']} | {oid} | {dn} / {pn} | {_corte_txt(k)} | {_n(r['f_robusto'], 1, False)} | "
                              f"{_n(r['tau_forma_reduzida'])} | {_n(r['tau_primeiro_estagio'], 3)} | {razao} | "
                              f"{_ar_txt(r)} | {_p(r['ar_p_beta0'])} | {_p(r['q_bky'])} |")
    g = resumo["parametros"]["anderson_rubin"]
    t["fuzzy"] = "\n".join(linhas) + (
        f"\n\nRazão = forma reduzida ÷ primeiro estágio, na amostra com ΔY observado. Com F robusto < 10 a razão não "
        f"tem ponto utilizável: a tabela mostra só o IC, e no CSV a linha leva a nota `{NOTA_FRACO}`, com `tau`, "
        f"`ep`, IC convencional e `p_valor` vazios. IC de Anderson–Rubin: β aceito se o p da RDD de ΔY − β·D é "
        f"≥ 0,05; grade de {g['n_pontos']} pontos em [−L; L], L = {_n(g['fator_L'], 0, False)} × o maior |ΔY| na "
        f"janela, fronteiras refinadas por bisseção ({g['bissecao']} passos). 'Ilimitado' = o conjunto aceita todo β "
        "da grade (reta inteira); no CSV, `ar_ilimitado = True` e `ar_ic_inf`/`ar_ic_sup` vazios, porque a borda da "
        "grade não é limite do IC. '(aberto)' = o conjunto toca a borda daquele lado. p (β = 0) = p de "
        "Anderson–Rubin em β = 0 (coluna `ar_p_beta0`), igual ao p da forma reduzida na mesma amostra. Só D1 em V "
        "entra no BKY.")
    linhas = ["| Outcome | Corte | Wald do pré (gl) | p | Municípios com todos os meses | Fora por falta de mês |",
              "|---|---|---|---|---|---|"]
    for oid in OUTCOMES_EVENTO:
        for corte in CORTES:
            k = ROTULO_CORTE[corte]
            w = _um(est, parte="C", outcome_id=oid, corte=k, especificacao="pre_wald")
            pe = resumo["evento_pre"][f"{oid}|{k}"]
            linhas.append(f"| {oid} | {_corte_txt(k)} | {_n(w['tau'], 1, False)} ({int(w['gl'])}) | {_p(w['p_valor'])} "
                          f"| {pe['n_municipios_completos']} | {pe['n_municipios_fora']} |")
    linhas += ["", "| Mês | " + " | ".join(f"{o} em {_corte_txt(ROTULO_CORTE[c])}" for o in OUTCOMES_EVENTO
                                          for c in CORTES) + " |",
               "|---|" + "---|" * (len(OUTCOMES_EVENTO) * len(CORTES))]
    for m in MESES:
        cel = []
        for oid in OUTCOMES_EVENTO:
            for corte in CORTES:
                r = ev[(ev["outcome_id"] == oid) & (ev["corte"] == ROTULO_CORTE[corte]) & (ev["competencia"] == m)]
                r = r.iloc[0]
                cel.append("0 (ref.)" if bool(r["referencia"]) else f"{_n(r['tau'])} {_ic(r['ic95_inf'], r['ic95_sup'])}")
        linhas.append(f"| {m[:4]}-{m[4:]} | " + " | ".join(cel) + " |")
    t["evento"] = "\n".join(linhas)
    linhas = ["| Outcome | Corte | Tratados abaixo / acima | ATT abaixo | ATT acima | Diferença (acima − abaixo) | p | q BKY |",
              "|---|---|---|---|---|---|---|---|"]
    for oid in OUTCOMES_D:
        for corte in CORTES:
            k = ROTULO_CORTE[corte]
            ab = _um(est, parte="D", outcome_id=oid, corte=k, especificacao="chegada_abaixo")
            ac = _um(est, parte="D", outcome_id=oid, corte=k, especificacao="chegada_acima")
            di = _um(est, parte="D", outcome_id=oid, corte=k, especificacao="chegada_diferenca")
            linhas.append(f"| {oid} | {_corte_txt(k)} | {int(ab['n_tratados'])} / {int(ac['n_tratados'])} | "
                          f"{_n(ab['tau'])} {_ic(ab['ic95_inf'], ab['ic95_sup'])} | "
                          f"{_n(ac['tau'])} {_ic(ac['ic95_inf'], ac['ic95_sup'])} | "
                          f"{_n(di['tau'])} {_ic(di['ic95_inf'], di['ic95_sup'])} | {_p(di['p_valor'])} | "
                          f"{_p(di['q_bky'])} |")
    t["chegada_lados"] = "\n".join(linhas)
    linhas = ["| Corte | Salto em ter célula (p.p.) | IC 95% | p | n abaixo / acima |", "|---|---|---|---|---|"]
    for corte in CORTES:
        k = ROTULO_CORTE[corte]
        r = _um(est, parte="E", corte=k)
        linhas.append(f"| {_corte_txt(k)} | {_n(100 * r['tau'], 1)} | {_ic(100 * r['ic95_inf'], 100 * r['ic95_sup'], 1)} "
                      f"| {_p(r['p_valor'])} | {int(r['n_abaixo'])} / {int(r['n_acima'])} |")
    t["selecao"] = "\n".join(linhas)
    linhas = []
    for fg in resumo["figuras"]:
        linhas += [f"**{fg['titulo']}** ![{fg['titulo']}](../../{fg['arquivo']})", "",
                   f"Como ler: {fg['como_ler'].removeprefix('COMO LER. ')}", ""]
    t["figuras"] = "\n".join(linhas).rstrip()
    if resumo["desvios"]:
        linhas = ["| Data | Tipo | Item | Descrição |", "|---|---|---|---|"]
        for dv in resumo["desvios"]:
            linhas.append(f"| {dv['data']} | {dv['tipo']} | {dv['item']} | {dv['descricao']} |")
        t["desvios"] = "\n".join(linhas)
    else:
        t["desvios"] = "Nenhum desvio registrado na execução."
    return t


MARCA = re.compile(r"(<!-- OC:(?P<nome>[A-Za-z0-9_]+):inicio -->\n)(?P<corpo>.*?)(\n?<!-- OC:(?P=nome):fim -->)", re.S)


def aplicar_tabelas_doc(texto: str, tabelas: dict[str, str]) -> str:
    def sub(m):
        nome = m.group("nome")
        if nome not in tabelas:
            raise KeyError(f"bloco {nome} não gerado")
        return m.group(1) + tabelas[nome] + "\n" + f"<!-- OC:{nome}:fim -->"
    return MARCA.sub(sub, texto)


def tabelas_no_doc(texto: str) -> dict[str, str]:
    return {m.group("nome"): m.group("corpo") for m in MARCA.finditer(texto)}


def ler_saidas():
    est = pd.read_csv(OUT / NOME_EST, dtype={"outcome_id": str, "corte": str, "populacao": str})
    ev = pd.read_csv(OUT / NOME_EVENTO, dtype={"outcome_id": str, "corte": str, "competencia": str})
    resumo = json.loads((OUT / NOME_RESUMO).read_text(encoding="utf-8"))
    for c in ("familia_multipla", "nota"):
        est[c] = est[c].fillna("")
    return est, ev, resumo


def atualizar_doc() -> None:
    if not DOC.exists():
        print(f"{rotulo(DOC)} não existe: blocos não gravados")
        return
    est, ev, resumo = ler_saidas()
    texto = DOC.read_text(encoding="utf-8")
    tabelas = gerar_tabelas_doc(est, ev, resumo)
    faltam = set(tabelas) - set(tabelas_no_doc(texto))
    if faltam:
        raise FalhaValidacao(f"doc sem marcadores para {sorted(faltam)}")
    DOC.write_text(aplicar_tabelas_doc(texto, tabelas), encoding="utf-8")
    print(f"blocos OC regravados: {rotulo(DOC)}")


# ---------------------------------------------------------------------------
# 7. Figuras
# ---------------------------------------------------------------------------

FONTE = ("Fonte: CNES nacional (a09) e CNES profissional (a16), lista nominal do PMM-E, IVS 2010 oficial do Ipea "
         "(a08), Censo 2022; script 43, protocolo 64.")

COMO_LER = {
    "salto": ("COMO LER. Cada ponto é o salto, no corte, da mudança na oferta entre o pré (2024-06 a 2025-06) e o pós "
              "(2025-10 a 2026-08): municípios logo acima do corte (bolsa R$ 5 mil maior) menos os logo abaixo. Barra "
              "= IC 95%. Ponto cheio = V (ofereceram vaga); vazado = U (todos). Barra que cruza o zero: a diferença "
              "entre os lados não se distingue de zero. É o pacote do corte (bolsa e outras regras federais), não o "
              "efeito da participação no PMM-E; vínculo cadastrado não é presença."),
    "evento": ("COMO LER. Cada ponto é o salto, no corte, da mudança desde 2025-06 (referência, zero por construção): "
               "municípios logo acima do corte menos os logo abaixo, mês a mês, em V. Barra = IC 95%. Antes da "
               "referência os pontos deveriam ficar perto de zero (pré plano); a faixa clara marca o pós (2025-10 a "
               "2026-08). É o pacote do corte, não o efeito da participação no PMM-E; vínculo cadastrado não é "
               "presença."),
    "primeiro_estagio": ("COMO LER. Cada ponto é a fração de municípios de V que receberam médico do PMM-E (ciclos 1 "
                         "e 2, até 2026-08), em faixas de 0,010 de IVS. As linhas são a reta local (kernel "
                         "triangular, h = 0,050) de cada lado do corte; o degrau entre elas é o primeiro estágio. "
                         "Degrau pequeno ou F robusto < 10 = instrumento fraco: a razão fuzzy não tem ponto "
                         "utilizável. Descreve a chegada, não efeito."),
}
TITULOS = {"salto": "Salto no corte da mudança na oferta (ΔB1–ΔB5)",
           "evento": "Estudo de evento no corte (B1–B3, V)",
           "primeiro_estagio": "Primeiro estágio: receber médico do PMM-E (D1) no corte"}


def _texto_figura(fig, chave: str) -> None:
    S = K1M
    txt = "\n".join(textwrap.wrap(COMO_LER[chave], LARGURA_COMO_LER))
    fig.text(0.02, 0.055, txt, fontsize=10, color=S.TINTA_2, va="bottom", ha="left", linespacing=1.3, parse_math=False)
    fig.text(0.02, 0.015, FONTE, fontsize=9, color=S.TINTA_2, va="bottom", ha="left", parse_math=False)


def _fmt_eixo(ax):
    import matplotlib
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
        lambda v, _: f"{v:g}".replace(".", ",").replace("-", "−")))


def figura_salto(est: pd.DataFrame, caminho: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    S = K1M
    fig, axs = plt.subplots(1, len(IDS), figsize=(14, 6.6), facecolor=S.SUPERFICIE)
    fig.subplots_adjust(left=0.05, right=0.99, top=0.74, bottom=0.30, wspace=0.45)
    for ax, oid in zip(axs, IDS):
        ax.set_facecolor(S.SUPERFICIE)
        ax.axhline(0, color=S.TINTA_2, linewidth=0.9)
        for j, corte in enumerate(CORTES):
            for dx, pn, cheio in ((-0.12, "V", True), (0.12, "U", False)):
                r = _um(est, parte="A", outcome_id=oid, populacao=pn, corte=ROTULO_CORTE[corte],
                        especificacao="principal")
                xv = j + dx
                ax.errorbar([xv], [r["tau"]], yerr=[[r["tau"] - r["ic95_inf"]], [r["ic95_sup"] - r["tau"]]],
                            fmt="none", ecolor=S.COR_IC, elinewidth=2)
                ax.plot([xv], [r["tau"]], "o", markersize=8, color=S.COR_PONTO,
                        markerfacecolor=S.COR_PONTO if cheio else S.SUPERFICIE, markeredgewidth=2)
        ax.set_xticks(range(len(CORTES)))
        ax.set_xticklabels([_corte_txt(ROTULO_CORTE[c]) for c in CORTES], fontsize=11)
        ax.set_xlim(-0.6, len(CORTES) - 0.4)
        ax.set_title(oid + "\n" + "\n".join(textwrap.wrap(SPEC[oid]["curto"], 24)), fontsize=10.5, color=S.TINTA)
        ax.set_ylabel(SPEC[oid]["unidade"], fontsize=9, color=S.TINTA_2)
        ax.tick_params(colors=S.TINTA_2, labelsize=9)
        ax.grid(axis="y", alpha=0.3, linewidth=0.7)
        _fmt_eixo(ax)
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)
    from matplotlib.lines import Line2D
    fig.legend(handles=[Line2D([], [], marker="o", linestyle="", color=S.COR_PONTO, label="V (ofereceram vaga)"),
                        Line2D([], [], marker="o", linestyle="", color=S.COR_PONTO, markerfacecolor=S.SUPERFICIE,
                               markeredgewidth=2, label="U (todos os municípios)"),
                        Line2D([], [], color=S.COR_IC, linewidth=2, label="IC 95% (HC1)")],
               loc="center", ncol=3, frameon=False, fontsize=10, bbox_to_anchor=(0.5, 0.905))
    fig.suptitle(TITULOS["salto"] + ", por corte de IVS", fontsize=15, color=S.TINTA, x=0.05, ha="left", y=0.975)
    _texto_figura(fig, "salto")
    fig.savefig(caminho, dpi=150, facecolor=S.SUPERFICIE)
    plt.close(fig)


def figura_evento(ev: pd.DataFrame, caminho: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    S = K1M
    fig, axs = plt.subplots(len(OUTCOMES_EVENTO), len(CORTES), figsize=(14, 9.6), facecolor=S.SUPERFICIE,
                            sharex=True, squeeze=False)
    fig.subplots_adjust(left=0.08, right=0.99, top=0.90, bottom=0.20, hspace=0.35, wspace=0.18)
    idx = {m: i for i, m in enumerate(MESES)}
    for i, oid in enumerate(OUTCOMES_EVENTO):
        for j, corte in enumerate(CORTES):
            ax = axs[i, j]
            ax.set_facecolor(S.SUPERFICIE)
            e = ev[(ev["outcome_id"] == oid) & (ev["corte"] == ROTULO_CORTE[corte])].sort_values("competencia")
            x = e["competencia"].map(idx).to_numpy(int)
            ref = e["referencia"].astype(bool).to_numpy()
            tau = np.where(ref, 0.0, e["tau"].to_numpy(float))
            lo, hi = e["ic95_inf"].to_numpy(float), e["ic95_sup"].to_numpy(float)
            ax.axvspan(idx[COMP_POS[0]] - 0.5, idx[COMP_POS[-1]] + 0.5, color="#efece4", linewidth=0, zorder=0)
            ax.axhline(0, color=S.TINTA_2, linewidth=0.9)
            ok = ~ref & np.isfinite(lo)
            ax.errorbar(x[ok], tau[ok], yerr=[tau[ok] - lo[ok], hi[ok] - tau[ok]], fmt="none", ecolor=S.COR_IC,
                        elinewidth=1.6, alpha=0.85)
            ax.plot(x[~ref], tau[~ref], "o", color=S.COR_PONTO, markersize=5)
            ax.plot(x[ref], tau[ref], "s", color=S.TINTA, markersize=7)
            ax.set_title(f"{oid} — {SPEC[oid]['curto']}, corte {_corte_txt(ROTULO_CORTE[corte])}", fontsize=10.5,
                         color=S.TINTA, loc="left")
            ax.grid(axis="y", alpha=0.3, linewidth=0.7)
            ax.tick_params(colors=S.TINTA_2, labelsize=9)
            _fmt_eixo(ax)
            for lado in ("top", "right"):
                ax.spines[lado].set_visible(False)
            if j == 0:
                ax.set_ylabel("por 10 mil hab.", fontsize=9, color=S.TINTA_2)
    ticks = [i for i, m in enumerate(MESES) if m[4:] in ("01", "06")]
    for ax in axs[-1]:
        ax.set_xticks(ticks)
        ax.set_xticklabels([f"{MESES[i][:4]}-{MESES[i][4:]}" for i in ticks], fontsize=9)
    fig.suptitle(TITULOS["evento"] + ": salto de Y_t − Y_2025-06", fontsize=15, color=S.TINTA, x=0.08, ha="left",
                 y=0.975)
    _texto_figura(fig, "evento")
    fig.savefig(caminho, dpi=150, facecolor=S.SUPERFICIE)
    plt.close(fig)


def figura_primeiro_estagio(dados: dict, est: pd.DataFrame, caminho: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    S = K1M
    V, base = dados["V"], dados["base"]
    s = base.loc[V, "s_mil"].to_numpy(float)
    d1 = (dados["G"] >= 0).astype(float)
    fig, axs = plt.subplots(1, len(CORTES), figsize=(14, 6.4), facecolor=S.SUPERFICIE, squeeze=False)
    fig.subplots_adjust(left=0.07, right=0.99, top=0.84, bottom=0.27, wspace=0.18)
    for ax, corte in zip(axs[0], CORTES):
        ax.set_facecolor(S.SUPERFICIE)
        x = s - corte
        bordas = np.arange(-100, 101, 10)
        cx, my, nn = [], [], []
        for a, b in zip(bordas[:-1], bordas[1:]):
            m = (x > a) & (x <= b)
            if m.any():
                cx.append((a + b) / 2 / 1000 + corte / 1000)
                my.append(d1[m].mean())
                nn.append(int(m.sum()))
        ax.scatter(cx, my, s=[12 + 2 * n for n in nn], color=S.COR_PONTO, alpha=0.75, zorder=3)
        r = L.rd_local_linear(s, d1, corte, H, detalhes=True)
        co = r["_detalhes"]["fit"]["coef"]
        for lado in (-1, 1):
            xs = np.linspace(-H + 0.5, 0, 30) if lado < 0 else np.linspace(0.5, H - 0.5, 30)
            xx = xs / 1000
            t = 1.0 if lado > 0 else 0.0
            yy = co["const"] + co["x"] * xx + t * (co["T"] + co.get("T_x", 0.0) * xx)
            ax.plot(corte / 1000 + xx, yy, color=S.TINTA, linewidth=2)
        ax.axvline(corte / 1000, color=S.COR_ATO, linestyle="--", linewidth=1.2)
        fs = _um(est, parte="B", outcome_id="D1", populacao="V", corte=ROTULO_CORTE[corte],
                 especificacao="primeiro_estagio")
        ax.set_title(f"Corte {_corte_txt(ROTULO_CORTE[corte])}: salto {_n(100 * fs['tau'], 1)} p.p. "
                     f"{_ic(100 * fs['ic95_inf'], 100 * fs['ic95_sup'], 1)}, F robusto = {_n(fs['f_robusto'], 1, False)}",
                     fontsize=11, color=S.TINTA, loc="left")
        ax.set_xlabel("IVS 2010 oficial (Ipea)", fontsize=10, color=S.TINTA_2)
        ax.set_ylabel("fração que recebeu médico do PMM-E", fontsize=10, color=S.TINTA_2)
        ax.grid(axis="y", alpha=0.3, linewidth=0.7)
        ax.tick_params(colors=S.TINTA_2, labelsize=9)
        ax.set_xticks(np.arange(corte - 100, corte + 101, 25) / 1000)
        ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:.3f}".replace(".", ",")))
        _fmt_eixo(ax)
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)
    fig.suptitle(TITULOS["primeiro_estagio"] + ", em V", fontsize=15, color=S.TINTA, x=0.07, ha="left", y=0.975)
    _texto_figura(fig, "primeiro_estagio")
    fig.savefig(caminho, dpi=150, facecolor=S.SUPERFICIE)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 8. Execução
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--atualizar-doc", action="store_true")
    args = ap.parse_args(argv)
    if args.atualizar_doc:
        atualizar_doc()
        return 0
    try:
        dados = carregar()
        portao = portao_reproducao(dados)          # antes de qualquer conta nova
        print(f"portão: tau E7 {portao['tau_e7']:.12f}, reproduzido {portao['tau_reproduzido']:.12f}", flush=True)
        completar_b3(dados)
        la_V, bases_V, faltas_V = parte_a(dados, "V", dados["V"])
        la_U, bases_U, faltas_U = parte_a(dados, "U", dados["U"])
        lb, info_b = parte_b(dados, bases_V, bases_U)
        ev_linhas, lc, pre = parte_c(dados)
        ld, info_d = parte_d(dados)
        le, info_e = parte_e(dados)
    except (FalhaValidacao, OL.FalhaValidacao, K1M.FalhaValidacao, D2M.FalhaValidacao) as erro:
        print(f"FALHA DE VALIDAÇÃO (nada gravado): {erro}", file=sys.stderr)
        return 2
    est = aplicar_multiplos(pd.DataFrame(la_V + la_U + lb + lc + ld + le).reindex(columns=COLUNAS_EST))
    if int((est["familia_multipla"] == "holm").sum()) != 4 or int((est["familia_multipla"] == "bky").sum()) != 24:
        print("FALHA DE VALIDAÇÃO: famílias de Holm (4) e BKY (24) com tamanho errado", file=sys.stderr)
        return 2
    ev = pd.DataFrame(ev_linhas).reindex(columns=COLUNAS_EVENTO)
    OUT.mkdir(parents=True, exist_ok=True)
    est.to_csv(OUT / NOME_EST, index=False)
    ev.to_csv(OUT / NOME_EVENTO, index=False)
    dir_fig = OUT / DIR_FIG
    dir_fig.mkdir(parents=True, exist_ok=True)
    for antigo in dir_fig.glob("*.png"):
        antigo.unlink()
    est_l = est.copy()
    est_l["familia_multipla"] = est_l["familia_multipla"].fillna("")
    figuras = []
    for chave, fn, arg in (("salto", figura_salto, est_l), ("evento", figura_evento, ev),
                           ("primeiro_estagio", None, None)):
        caminho = dir_fig / f"OC_{chave}.png"
        if chave == "primeiro_estagio":
            figura_primeiro_estagio(dados, est_l, caminho)
        else:
            fn(arg, caminho)
        figuras.append({"arquivo": rotulo(caminho), "chave": chave, "titulo": TITULOS[chave],
                        "sha256": sha256(caminho), "como_ler": COMO_LER[chave], "fonte": FONTE})
    a = dados["conf_u"]
    resumo = {
        "natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "gerador": rotulo(Path(__file__)),
        "data_execucao": DATA_EXECUCAO,
        "protocolo": {"texto": rotulo(PROTOCOLO_MD), "sha256_texto": sha256(PROTOCOLO_MD)},
        "decisoes_de_implementacao": f"{rotulo(DOC)}, seção 9 (D1–D16), gravadas antes de qualquer estimativa",
        "contrastes": {"A": CONTRASTE_A, "B0": CONTRASTE_B0, "B": CONTRASTE_B, "C": CONTRASTE_C, "D": CONTRASTE_D,
                       "E": CONTRASTE_E},
        "parametros": {"cortes_mil": list(CORTES), "h_mil": H, "h_sensibilidade_mil": list(H_SENS),
                       "kernel": "triangular", "ep": "HC1", "pre": [COMP_PRE[0], COMP_PRE[-1]],
                       "pos": [COMP_POS[0], COMP_POS[-1]], "referencia_evento": COMP_REF,
                       "meses_lidos": [MESES[0], MESES[-1]], "limite_exclusivo": LIMITE_EXCLUSIVO,
                       "meses_pre_plano": list(MESES_PRE_PLANO),
                       "anderson_rubin": {"n_pontos": GRADE_AR_N, "fator_L": GRADE_AR_FATOR, "bissecao": BISSECAO_AR,
                                          "regra": "beta aceito se p de rd_local_linear(dY - beta*D) >= 0,05; grade "
                                                   "uniforme em [-L, L], L = fator x max|dY| na janela do kernel"},
                       "f_fraco": F_FRACO,
                       "bootstrap_parte_d": {"B": B_BOOT, "pesos": "Mammen", "semente": SEMENTE, "cluster": "município"},
                       "holm": "OC-A1 e OC-A2 em V, dois cortes (4)",
                       "bky": "OC-A3–A5 (6), OC-B0 D1 (2), OC-B1–B5 D1 (10), OC-D diferença (6), em V"},
        "portao": portao,
        "amostra": {"U": int(len(dados["U"])), "U_sem_populacao": len(a.get("U_excluidos_sem_populacao", [])),
                    "U_com_celula": int(len(dados["am_total"])),
                    "excluidos_tratados_fora_d2": len(dados["excl"]), "V": int(len(dados["V"])),
                    "V_tratados": int(dados["info_G"]["n_tratados"]),
                    "fora_por_falta_de_mes": {"V": faltas_V, "U": faltas_U},
                    "lista_nominal": dados["info_ch"], "lista_ativos": dados["info_ativos"]},
        "primeiro_estagio": info_b,
        "evento_pre": {f"{k[0]}|{ROTULO_CORTE[k[1]]}": v for k, v in pre.items()},
        "chegada_por_lado_tratados": info_d,
        "selecao": info_e,
        "b3": {**dados["info_b3"], "ligacao_x1": dados["info_lig"]},
        "leitura": classificar(est_l),
        "entradas": [
            E7.bloco_entrada(OL.PAINEL, "outcomes B1, B2, B4, B5 e base de B3", "CNES nacional (a09)", "202406-202608",
                             "municipios do a08", "municipio x grupo de CBO x mes", "co_ibge, competencia, grupo",
                             "grupos alvo_pmme e generalistas; competencias 202406-202608"),
            E7.bloco_entrada(OL.MANIF_A09, "CBO-alvo (ponte) e definições", "a09", "", "", "", "", ""),
            E7.bloco_entrada(OL.POP22, "população (por 10 mil hab.)", "IBGE, Censo 2022", "2022", "Brasil",
                             "municipio", "co_ibge", ""),
            E7.bloco_entrada(OL.A08, "running variable (IVS 2010 oficial) e universo U", "Ipea (a08)", "2010",
                             "Brasil", "municipio", "co_ibge", "IVS em milésimos"),
            E7.bloco_entrada(OL.ARQ_VM, "amostra V e OC-E (célula em algum ciclo)", "tarefa B (12)", "ciclos 1-3",
                             "V1, V2, V3", "municipio x ciclo", "ciclo, co_ibge", ""),
            E7.bloco_entrada(OL.NOMINAL, "D1 (menor dt_inicio_atividade) e coortes da parte D",
                             "MS, lista nominal do PMM-E", ", ".join(dados["info_ch"]["dt_referencia"]),
                             "ciclos 1 e 2", "especialista", "co_ibge",
                             "só co_ibge, dt_inicio_atividade, ciclo, dt_referencia; nenhum nome lido"),
            E7.bloco_entrada(OL.ATIVOS_ZIP, "início do ciclo 3 (saída dos controles, parte D)", "MS, lista de ativos",
                             "2026-09-11", "ciclos 1-3", "especialista", "co_ibge",
                             "só ciclo, co_ibge, dt_inicio_atividade; nenhum nome lido"),
            E7.bloco_entrada(OL.ARQ_VINC, "B3 e D2: vínculos dos ligados", "CNES profissional (a16)", "202406-202608",
                             "médicos ligados pela X1", "vinculo x mes", "id_prof, competencia",
                             "regra D1; CBO-alvo; TP_SUS_NAO_SUS = 'S'"),
            E7.bloco_entrada(OL.ARQ_CHAVES, "B3 e D2: médicos ligados (pseudônimos, só em memória)", "a16", "", "",
                             "medico", "id_prof, id_externo", "origem X1, regra D1"),
            E7.bloco_entrada(OL.MANIF_A16, "competências obtidas do a16", "a16", "", "", "", "", ""),
            E7.bloco_entrada(OL.ARQ_X1, "ciclo dos médicos ligados (D2)", "X1 (17)", "", "", "registro", "id_medico",
                             "regra D1"),
            E7.bloco_entrada(E7_EST, "portão de reprodução (F3.1, U, 0,300)", "E7 (14)", "", "", "", "", ""),
            E7.bloco_entrada(OL_RESUMO, "conferência do tamanho de V e dos tratados", "script 37", "", "", "", "", ""),
            E7.bloco_entrada(OL.D2_RESUMO, "lida pelas funções do 37 (coortes do D2)", "D2 (22)", "", "", "", "", ""),
        ],
        "desvios": DESVIOS,
        "figuras": figuras,
        "saidas": [{"arquivo": rotulo(OUT / n), "sha256": sha256(OUT / n)} for n in (NOME_EST, NOME_EVENTO)],
    }
    _gravar_json(OUT / NOME_RESUMO, resumo)
    atualizar_doc()
    return 0


if __name__ == "__main__":
    sys.exit(main())
