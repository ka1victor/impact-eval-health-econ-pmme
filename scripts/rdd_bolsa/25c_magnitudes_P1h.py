"""P1h (protocolo 52b): o peso da bolsa contra o custo do lugar na escolha (H3).

Protocolo congelado: `docs/06_execucao/52b_protocolo_P1h_magnitudes.md` (26/10/2026, antes de calcular), com
estatuto `PROTOCOLO_52B_POS_RESULTADO`: os coeficientes do M1 e os seus IC já estavam publicados no doc 57a, e a
conta aproximada da linha primária já tinha sido feita. Não é teste confirmatório novo: acrescenta a inferência
formal da diferença, com a covariância conjunta, e a amplitude da bolsa em km com IC.

Estimandos (protocolo §3)
-------------------------
- P1h-1 (primária): D_UF = θ_UF − 10·β; H0: D_UF ≤ 0 contra H1: D_UF > 0, unilateral a 5%; Holm numa família
  de um teste.
- P1h-2a: K5 = 100 · 5β / (−γ), km equivalentes a um degrau da bolsa (R$ 5 mil); IC delta e Fieller.
- P1h-2b: K10 = 100 · 10β / (−γ), km equivalentes a toda a amplitude (R$ 10 mil); idem.
- P1h-3 (sensibilidade): D_UF em M2, M4, M5 (por ciclo) e M7; BKY entre essas linhas (p unilateral).
- Pesos da figura (descritivos): 5β, 10β, −γ, θ_UF, θ_UF + θ_reg, θ_UF + θ_reg + θ_mun, todos no M1 e com a
  covariância conjunta; gravados no CSV para que a figura seja lida de `output/`.

β = `bolsa_mil` (por R$ 1 mil/mês); γ = `distancia_100km`; θ_UF = `mesma_uf`; θ_reg = `mesma_regiao_saude`
(incremento sobre a mesma UF); θ_mun = `mesmo_municipio` (incremento sobre a mesma região).

Linguagem
---------
θ é preferência revelada condicional ao modelo (mistura família, rede, registro profissional e outros motivos
ligados à origem), não efeito causal da geografia. β é o peso da bolsa identificado pelos saltos nos cortes de
IVS, com o IVS em spline contínua: mede o pacote do corte. Nada aqui diz se a bolsa "funciona" ou "não funciona".

Reuso e portão
--------------
As funções de amostra, desenho e ajuste vêm do script 25 (importado, sem alteração). O M1 e as especificações
M2, M4, M5 (ciclos 1, 2, 3) e M7 são reestimados na mesma amostra e no mesmo conjunto de escolha só para obter a
covariância conjunta, que o script 25 não gravou. Portão: coeficientes e EP com cluster por conjunto de todas as
especificações iguais aos de `output/rdd_bolsa/P1_estimativas.csv` com diferença máxima ≤ 1e−8; se alguma
falhar, a execução para com `FALHA_REPRODUCAO_<especificação>` e nada é calculado. As saídas `P1_*` não são
regravadas.

Integridade
-----------
Só lê `output/` e, sem alterar, a tabela de CIR e os centroides do IBGE (pelas funções do script 25). O IVS
2010 oficial vem do a08; o arquivo local de IVS da auditoria 16 não é lido. Nenhum mês do CNES é lido. Nada é
simulado, imputado ou digitado como observação; toda saída leva `natureza_dos_dados = EMPIRICO`; sem nome, CPF
ou CRM em `output/` (só agregados).

Uso
---
    python3 scripts/rdd_bolsa/25c_magnitudes_P1h.py
    python3 scripts/rdd_bolsa/25c_magnitudes_P1h.py --atualizar-doc   # só regrava o doc 57i a partir das saídas
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
DIR_RDD = ROOT / "scripts" / "rdd_bolsa"


def _importar(caminho: Path, nome: str):
    bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    sys.dont_write_bytecode = bytecode
    return mod


P1 = _importar(DIR_RDD / "25_escolha_dap.py", "p1_escolha_para_p1h")
L = P1.L

# ---------------------------------------------------------------------------
# Caminhos
# ---------------------------------------------------------------------------

SCRIPT_25 = DIR_RDD / "25_escolha_dap.py"
PROTOCOLO_MD = ROOT / "docs" / "06_execucao" / "52b_protocolo_P1h_magnitudes.md"
DOC = ROOT / "docs" / "06_execucao" / "57i_resultados_P1h_magnitudes.md"
OUT = ROOT / "output" / "rdd_bolsa"
P1_EST = OUT / "P1_estimativas.csv"
OUT_CSV = OUT / "P1h_magnitudes.csv"
OUT_RESUMO = OUT / "P1h_resumo.json"
DIR_FIG = OUT / "P1h_figuras"
FIG = DIR_FIG / "P1h_magnitudes.png"

# ---------------------------------------------------------------------------
# Parâmetros (protocolo 52b; nenhum é dado)
# ---------------------------------------------------------------------------

DATA_EXECUCAO = "2026-10-26"
NATUREZA = "EMPIRICO"
ESTATUTO = "PROTOCOLO_52B_POS_RESULTADO"
TOL_REPRODUCAO = 1e-8
ALFA = 0.05
Z95 = float(stats.norm.ppf(0.975))          # IC 95% bilateral
Z95_UNI = float(stats.norm.ppf(0.95))       # limite inferior unilateral de 95%
AMPLITUDE_MIL = 10.0                        # de R$ 10 mil para R$ 20 mil por mês
DEGRAU_MIL = 5.0                            # um degrau de faixa
KM_POR_UNIDADE = 100.0                      # γ é por 100 km
EMPILHADO = P1.EMPILHADO

B = P1.TERMO_BOLSA                          # β
G = P1.TERMO_DIST                           # γ
UF, REG, MUN = "mesma_uf", "mesma_regiao_saude", "mesmo_municipio"
TERMOS_CHAVE = [B, G, UF, REG, MUN]

# (chave, modelo no CSV do P1, ciclo no CSV do P1). M1 primeiro: se ele falhar, a falha é FALHA_REPRODUCAO_M1.
ESPECS = [("M1", "M1", EMPILHADO), ("M2", "M2", EMPILHADO), ("M4", "M4", EMPILHADO), ("M5_1", "M5", "1"),
          ("M5_2", "M5", "2"), ("M5_3", "M5", "3"), ("M7", "M7", EMPILHADO)]
SENSIBILIDADES = [k for k, _, _ in ESPECS if k != "M1"]

ROTULO_ESPEC = {
    "M1": "M1 (principal): ciclos 1–3, distância/100 km, mesma UF, mesma região, mesmo município, capital",
    "M2": "M2: M1 com log(1 + distância em km)",
    "M4": "M4: M1 com efeito fixo de UF da vaga",
    "M5_1": "M5: M1 só no ciclo 1",
    "M5_2": "M5: M1 só no ciclo 2",
    "M5_3": "M5: M1 só no ciclo 3",
    "M7": "M7: logit explodido (1ª e 2ª opção) com M1",
}

COLUNAS = ["natureza_dos_dados", "estatuto", "id_linha", "papel", "modelo", "ciclo", "componente", "estimando",
           "unidade", "metodo_inferencia", "estimativa", "ep_cluster_conjunto", "ep_mle", "ep_cluster_candidato",
           "ic95_inf", "ic95_sup", "li95_unilateral", "p_unilateral", "p_unilateral_t_g_menos_1",
           "p_unilateral_mle", "p_unilateral_cluster_candidato", "ic95_fieller_inf", "ic95_fieller_sup",
           "li95_unilateral_fieller", "fieller_forma", "entra_holm", "p_holm", "entra_bky", "q_bky",
           "rejeita_h0_5pct", "g_conjuntos", "g_candidatos", "n_candidatos", "n_grupos_escolha",
           "n_linhas_candidato_celula", "n_conjuntos", "nota"]

# Pesos da figura (M1), de cima para baixo: (componente, rótulo, grupo, vetor como {termo: peso}).
PESOS_FIGURA = [
    ("5β", "Bolsa: um degrau (+R$ 5 mil/mês)", "bolsa", {B: DEGRAU_MIL}),
    ("10β", "Bolsa: toda a amplitude (R$ 10 → 20 mil)", "bolsa", {B: AMPLITUDE_MIL}),
    ("−γ", "Vaga 100 km mais perto da origem", "lugar", {G: -1.0}),
    ("θ_UF", "Vaga na mesma UF da origem", "lugar", {UF: 1.0}),
    ("θ_UF + θ_reg", "Vaga na mesma região de saúde", "lugar", {UF: 1.0, REG: 1.0}),
    ("θ_UF + θ_reg + θ_mun", "Vaga no mesmo município", "lugar", {UF: 1.0, REG: 1.0, MUN: 1.0}),
]

COMO_LER = ("Cada ponto é o peso de um atributo da vaga na utilidade da escolha da 1ª opção, no modelo principal "
            "(M1, ciclos 1–3), em log-chance; a barra é o IC 95% com cluster por conjunto de escolha. Todos os pesos "
            "estão na mesma escala: comparar a distância de cada ponto ao zero é comparar quanto cada atributo move a "
            "escolha. Um peso de 1 multiplica por e ≈ 2,7 a razão entre a probabilidade de escolher a vaga e a de "
            "escolher qualquer outra do conjunto, mantido o resto. As linhas de lugar são cumulativas (a região inclui "
            "a UF; o município inclui a região e a UF) e são preferência revelada condicional ao modelo, não efeito "
            "causal da geografia; as da bolsa são identificadas pelos cortes de IVS (pacote do corte). As linhas não "
            "incluem a distância, que entra à parte.")


class FalhaValidacao(RuntimeError):
    pass


rel = P1.rel
sha256 = P1.sha256
gravar_json = P1.gravar_json

# ---------------------------------------------------------------------------
# Inferência: combinação linear, delta e Fieller (funções puras, testadas em caso sintético)
# ---------------------------------------------------------------------------


def _p_uni(est: float, ep: float) -> float:
    """p unilateral de H0: parâmetro ≤ 0 contra H1: > 0, pela normal."""
    return float(stats.norm.sf(est / ep)) if ep > 0 and math.isfinite(est) else float("nan")


def _inferencia(est: float, eps: dict[str, float], g_conj: int | None) -> dict:
    ep = eps["conj"]
    z = est / ep if ep > 0 else float("nan")
    return {"estimativa": est, "ep_cluster_conjunto": ep, "ep_mle": eps["mle"], "ep_cluster_candidato": eps["cand"],
            "ic95_inf": est - Z95 * ep, "ic95_sup": est + Z95 * ep, "li95_unilateral": est - Z95_UNI * ep,
            "p_unilateral": _p_uni(est, ep),
            "p_unilateral_t_g_menos_1": (float(stats.t.sf(z, g_conj - 1)) if g_conj and math.isfinite(z)
                                         else float("nan")),
            "p_unilateral_mle": _p_uni(est, eps["mle"]), "p_unilateral_cluster_candidato": _p_uni(est, eps["cand"])}


def _ep(v: np.ndarray, V: np.ndarray) -> float:
    return math.sqrt(max(float(v @ V @ v), 0.0))


def combinacao_linear(theta: np.ndarray, Vs: dict[str, np.ndarray], a: np.ndarray, g_conj: int | None = None) -> dict:
    """a'θ com EP √(a'Va) para cada covariância (conj, mle, cand)."""
    est = float(a @ theta)
    return _inferencia(est, {k: _ep(a, V) for k, V in Vs.items()}, g_conj)


def gradiente_razao(theta: np.ndarray, a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Gradiente de (a'θ)/(b'θ) em θ."""
    num, den = float(a @ theta), float(b @ theta)
    return a / den - num * b / den ** 2


def razao_delta(theta: np.ndarray, Vs: dict[str, np.ndarray], a: np.ndarray, b: np.ndarray,
                g_conj: int | None = None) -> dict:
    """(a'θ)/(b'θ) com EP pelo método delta para cada covariância."""
    est = float(a @ theta) / float(b @ theta)
    g = gradiente_razao(theta, a, b)
    return _inferencia(est, {k: _ep(g, V) for k, V in Vs.items()}, g_conj)


def fieller(num: float, den: float, v_nn: float, v_dd: float, v_nd: float, z: float) -> tuple[float, float, str]:
    """Conjunto de Fieller de ρ = num/den: {ρ : (num − ρ·den)² ≤ z²·(v_nn − 2ρ·v_nd + ρ²·v_dd)}.

    Devolve (inferior, superior, forma). forma = 'limitado' quando den²  > z²·v_dd (denominador distinto de zero
    ao nível do teste) e o conjunto é um intervalo; 'complemento' (dois raios, (−∞; inf] ∪ [sup; ∞)) ou 'reta'
    (toda a reta) quando não é limitado.
    """
    A = den ** 2 - z ** 2 * v_dd
    Bq = num * den - z ** 2 * v_nd
    C = num ** 2 - z ** 2 * v_nn
    disc = Bq ** 2 - A * C
    if A > 0:
        r = math.sqrt(max(disc, 0.0))
        return (Bq - r) / A, (Bq + r) / A, "limitado"
    if disc < 0:
        return float("-inf"), float("inf"), "reta"
    r = math.sqrt(disc)
    lo, hi = sorted(((Bq - r) / A, (Bq + r) / A)) if A != 0 else (float("nan"), float("nan"))
    return lo, hi, "complemento"


def vetor(termos: list[str], pesos: dict[str, float]) -> np.ndarray:
    a = np.zeros(len(termos))
    for t, w in pesos.items():
        a[termos.index(t)] = w
    return a


# ---------------------------------------------------------------------------
# Reestimação (funções do script 25) e portão de reprodução
# ---------------------------------------------------------------------------

def _enxugar(r: dict) -> dict:
    """Guarda só o que o P1h usa (as matrizes do desenho ocupam centenas de MB)."""
    for k in ("_A", "_D", "_scores", "_info"):
        r.pop(k, None)
    return r


def reestimar(dados: dict, log=print) -> tuple[dict[str, dict], dict]:
    conj = dados["conj_p1"]
    D = P1.montar_desenho(conj, dados["r1_p1"], None, dados)
    conf_dist = P1.conferir_distancias(D)
    res: dict[str, dict] = {}
    amostra = "P1 (G1 com origem)"
    for m in ("M1", "M2", "M4"):
        res[m] = _enxugar(P1.estimar(P1.matriz_modelo(D, dados, m), D, modelo=m, ciclo=EMPILHADO, amostra=amostra))
        log(f"{m}: ok={res[m]['ok']} it={res[m].get('iteracoes')}")
    del D
    for k in P1.CICLOS:
        Dk = P1.montar_desenho(conj[conj["ciclo"] == k].reset_index(drop=True),
                               dados["r1_p1"][dados["r1_p1"]["ciclo"] == k], None, dados)
        res[f"M5_{k}"] = _enxugar(P1.estimar(P1.matriz_modelo(Dk, dados, "M1"), Dk, modelo="M5", ciclo=str(k),
                                             amostra=amostra))
        log(f"M5 ciclo {k}: ok={res[f'M5_{k}']['ok']}")
    De = P1.montar_desenho(conj, dados["r1_p1"], dados["r2_p1"], dados)
    P1.conferir_distancias(De)
    res["M7"] = _enxugar(P1.estimar(P1.matriz_modelo(De, dados, "M1"), De, modelo="M7", ciclo=EMPILHADO,
                                    amostra="P1 (G1 com origem), 1ª e 2ª opção"))
    log(f"M7: ok={res['M7']['ok']}")
    return res, conf_dist


def portao(res: dict[str, dict], est: pd.DataFrame) -> dict:
    """Coeficientes e EP com cluster por conjunto de cada especificação contra P1_estimativas.csv."""
    linhas = []
    falha = None
    for chave, modelo, ciclo in ESPECS:
        r = res[chave]
        g = est[(est["modelo"] == modelo) & (est["ciclo"] == ciclo) & (est["tipo_linha"] == "coeficiente")]
        g = g.set_index("termo")
        info = {"especificacao": chave, "modelo_no_csv": modelo, "ciclo": ciclo, "convergiu": bool(r["ok"]),
                "termos_reestimados": len(r["termos"]), "termos_gravados": int(len(g)),
                "mesmos_termos_na_mesma_ordem": bool(r["ok"] and list(g.index) == list(r["termos"]))}
        if info["mesmos_termos_na_mesma_ordem"]:
            ep = lambda V: np.sqrt(np.diag(V))  # noqa: E731
            info.update({
                "dif_max_coef": float(np.max(np.abs(r["theta"] - g["coef"].to_numpy()))),
                "dif_max_ep_cluster_conjunto": float(np.max(np.abs(ep(r["V_conj"]) - g["ep_cluster_conjunto"].to_numpy()))),
                "dif_max_ep_mle_informativo": float(np.max(np.abs(ep(r["V_mle"]) - g["ep_mle"].to_numpy()))),
                "dif_max_ep_cluster_candidato_informativo": float(np.max(np.abs(ep(r["V_cand"]) -
                                                                                 g["ep_cluster_candidato"].to_numpy()))),
            })
            info["passou"] = bool(info["dif_max_coef"] <= TOL_REPRODUCAO and
                                  info["dif_max_ep_cluster_conjunto"] <= TOL_REPRODUCAO)
        else:
            info["passou"] = False
        if not info["passou"] and falha is None:
            falha = f"FALHA_REPRODUCAO_{chave}"
        linhas.append(info)
    return {"status": "PASSOU" if falha is None else falha, "tolerancia": TOL_REPRODUCAO,
            "regra": ("coeficientes e EP com cluster por conjunto de todos os termos de cada especificação contra "
                      "P1_estimativas.csv (gravado com 10 algarismos significativos); diferença máxima ≤ 1e−8; os EP "
                      "de MV e por candidato são registrados, sem entrar no portão"),
            "especificacoes": linhas}


# ---------------------------------------------------------------------------
# Linhas de saída
# ---------------------------------------------------------------------------

def _linha(**kw) -> dict:
    base = {c: np.nan for c in COLUNAS}
    base.update({"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "entra_holm": False, "entra_bky": False,
                 "rejeita_h0_5pct": None, "fieller_forma": "", "nota": ""})
    base.update(kw)
    return base


def _comuns(chave: str, r: dict) -> dict:
    modelo, ciclo = next((m, c) for k, m, c in ESPECS if k == chave)
    return {"modelo": modelo, "ciclo": ciclo, "g_conjuntos": r["G_conj"], "g_candidatos": r["G_cand"],
            "n_candidatos": r["n_candidatos"], "n_grupos_escolha": r["n_grupos"],
            "n_linhas_candidato_celula": r["n_linhas"], "n_conjuntos": r["n_conjuntos"]}


def _Vs(r: dict) -> dict[str, np.ndarray]:
    return {"conj": r["V_conj"], "mle": r["V_mle"], "cand": r["V_cand"]}


def linha_dif_uf(chave: str, r: dict, id_linha: str, papel: str) -> dict:
    a = vetor(r["termos"], {UF: 1.0, B: -AMPLITUDE_MIL})
    return _linha(id_linha=id_linha, papel=papel, componente="D_UF", **_comuns(chave, r),
                  estimando="D_UF = θ_UF − 10·β (mesma UF contra toda a amplitude da bolsa, R$ 10 → 20 mil/mês)",
                  unidade="peso na utilidade (log-chance)", metodo_inferencia="combinação linear, covariância conjunta",
                  **combinacao_linear(r["theta"], _Vs(r), a, r["G_conj"]),
                  nota=("H0: D_UF ≤ 0 contra H1: D_UF > 0 (unilateral); " +
                        ("Holm numa família de um teste" if id_linha == "P1h-1" else
                         "sensibilidade; BKY entre as linhas P1h-3")))


def linha_km(r: dict, passo: float, id_linha: str, componente: str) -> dict:
    a = vetor(r["termos"], {B: KM_POR_UNIDADE * passo})
    b = vetor(r["termos"], {G: -1.0})
    d = razao_delta(r["theta"], _Vs(r), a, b, r["G_conj"])
    num, den = float(a @ r["theta"]), float(b @ r["theta"])
    V = r["V_conj"]
    f95 = fieller(num, den, float(a @ V @ a), float(b @ V @ b), float(a @ V @ b), Z95)
    f90 = fieller(num, den, float(a @ V @ a), float(b @ V @ b), float(a @ V @ b), Z95_UNI)
    return _linha(id_linha=id_linha, papel="secundaria_descritiva", componente=componente, **_comuns("M1", r),
                  estimando=f"{componente} = 100 · {passo:g}β / (−γ): km a menos de distância com o mesmo peso de "
                            f"R$ {passo:g} mil/mês de bolsa",
                  unidade="km", metodo_inferencia="método delta (EP, IC, p); Fieller (IC e limite unilateral)", **d,
                  ic95_fieller_inf=f95[0], ic95_fieller_sup=f95[1], li95_unilateral_fieller=f90[0],
                  fieller_forma=f95[2] if f95[2] == f90[2] else f"{f95[2]} (95%) / {f90[2]} (90%)",
                  nota=("descritiva, sem teste confirmatório; p unilateral de H0: K ≤ 0 pelo delta; pelo Fieller, "
                        "H0: K ≤ 0 equivale a H0: β ≤ 0 (γ < 0)"))


def linhas_figura(r: dict) -> list[dict]:
    out = []
    for comp, rotulo, grupo, pesos in PESOS_FIGURA:
        a = vetor(r["termos"], pesos)
        out.append(_linha(id_linha="FIG", papel="peso_na_utilidade_figura", componente=comp, **_comuns("M1", r),
                          estimando=rotulo, unidade="peso na utilidade (log-chance)",
                          metodo_inferencia="combinação linear, covariância conjunta",
                          **combinacao_linear(r["theta"], _Vs(r), a, r["G_conj"]),
                          nota=f"descritivo (figura); grupo {grupo}; p unilateral de H0: peso ≤ 0, sem teste"))
    return out


def montar_linhas(res: dict[str, dict]) -> pd.DataFrame:
    r1 = res["M1"]
    linhas = [linha_dif_uf("M1", r1, "P1h-1", "primaria"),
              linha_km(r1, DEGRAU_MIL, "P1h-2a", "K5"),
              linha_km(r1, AMPLITUDE_MIL, "P1h-2b", "K10")]
    linhas += [linha_dif_uf(k, res[k], "P1h-3", "sensibilidade") for k in SENSIBILIDADES]
    linhas += linhas_figura(r1)
    est = pd.DataFrame(linhas)[COLUNAS]
    mh = est["id_linha"] == "P1h-1"
    est.loc[mh, "entra_holm"] = True
    est.loc[mh, "p_holm"] = L.holm(est.loc[mh, "p_unilateral"].to_numpy())
    est.loc[mh, "rejeita_h0_5pct"] = bool(est.loc[mh, "p_holm"].iloc[0] < ALFA)
    mb = est["id_linha"] == "P1h-3"
    est.loc[mb, "entra_bky"] = True
    est.loc[mb, "q_bky"] = L.qvalores_bky(est.loc[mb, "p_unilateral"].to_numpy())
    est.loc[mb, "rejeita_h0_5pct"] = (est.loc[mb, "q_bky"] < ALFA).to_numpy()
    est["entra_holm"] = est["entra_holm"].astype(bool)
    est["entra_bky"] = est["entra_bky"].astype(bool)
    return est


def covariancias_chave(res: dict[str, dict]) -> dict:
    """θ e os blocos das covariâncias dos termos usados, para recálculo independente nos testes."""
    out = {}
    for chave, _, _ in ESPECS:
        r = res[chave]
        termos = [t for t in TERMOS_CHAVE if t in r["termos"]]
        k = [r["termos"].index(t) for t in termos]
        out[chave] = {"termos": termos, "theta": r["theta"][k].tolist(),
                      **{nome: r[V][np.ix_(k, k)].tolist() for nome, V in
                         (("V_cluster_conjunto", "V_conj"), ("V_mle", "V_mle"), ("V_cluster_candidato", "V_cand"))},
                      "g_conjuntos": r["G_conj"], "g_candidatos": r["G_cand"]}
    return out


# ---------------------------------------------------------------------------
# Figura
# ---------------------------------------------------------------------------

def _plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 13, "svg.hashsalt": "p1h"})
    return plt


def titulo_figura(est: pd.DataFrame) -> str:
    p = est[est["id_linha"] == "P1h-1"].iloc[0]
    if bool(p["rejeita_h0_5pct"]):
        return "Na escolha da vaga, ficar na UF de origem pesa mais\nque toda a amplitude da bolsa (R$ 10 → 20 mil)"
    return "Na escolha da vaga, os dados não separam o peso da UF de origem\ndo de toda a amplitude da bolsa"


def figura(est: pd.DataFrame) -> dict:
    plt = _plt()
    DIR_FIG.mkdir(parents=True, exist_ok=True)
    f = est[est["id_linha"] == "FIG"].set_index("componente").loc[[c for c, *_ in PESOS_FIGURA]].reset_index()
    cores = {"bolsa": "#2a78d6", "lugar": "#c4561d"}
    fig, ax = plt.subplots(figsize=(12.0, 6.75))
    y = np.arange(len(f))[::-1].astype(float)
    xmax = float(f["ic95_sup"].max())
    for yi, (comp, rotulo, grupo, _), r in zip(y, PESOS_FIGURA, f.itertuples()):
        ax.plot([r.ic95_inf, r.ic95_sup], [yi, yi], color=cores[grupo], lw=3.0, solid_capstyle="round")
        ax.plot([r.estimativa], [yi], "o", color=cores[grupo], ms=10, mec="white", mew=1.5, zorder=3)
        ax.text(r.ic95_sup + 0.06 * xmax, yi, f"{_n(r.estimativa, 2)}  [{_n(r.ic95_inf, 2)}; {_n(r.ic95_sup, 2)}]",
                va="center", ha="left", fontsize=12, color="#2b2b29")
    ax.axvline(0, color="#52514e", lw=1.0)
    ax.set_yticks(y)
    ax.set_yticklabels([rot for _, rot, _, _ in PESOS_FIGURA], fontsize=13)
    ax.set_xlim(min(-0.15, float(f["ic95_inf"].min()) - 0.1), xmax * 1.45)
    ax.set_xlabel("peso na utilidade (log-chance), IC 95%", fontsize=13)
    fig.text(0.015, 0.975, titulo_figura(est), fontsize=16, ha="left", va="top", color="#1f1f1d")
    fig.text(0.015, 0.025, f"M1, ciclos 1–3, {int(f['n_candidatos'].iloc[0])} candidatos; IC 95% com cluster por "
             "conjunto de escolha (curso × ciclo).\nLugar: preferência revelada condicional ao modelo, não efeito "
             "causal; bolsa: identificada pelos cortes de IVS (pacote do corte).",
             fontsize=10.5, color="#52514e", ha="left", va="bottom")
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color="#e6e5e0", lw=0.6)
    ax.set_axisbelow(True)
    fig.subplots_adjust(left=0.33, right=0.98, top=0.83, bottom=0.22)
    fig.savefig(FIG, dpi=150, metadata={"Software": None})
    plt.close(fig)
    return {"arquivo": rel(FIG), "sha256": sha256(FIG), "como_ler": COMO_LER, "titulo": titulo_figura(est),
            "descricao": "pesos na utilidade, na mesma escala, de um degrau e da amplitude da bolsa, 100 km a menos, "
                         "mesma UF, mesma região e mesmo município (M1, IC 95% cluster por conjunto)"}


# ---------------------------------------------------------------------------
# Documento 57i
# ---------------------------------------------------------------------------

_n = P1._n
_p = P1._p
_peq = P1._peq
_ic = P1._ic
_tab = P1._tab


def _km(v) -> str:
    return _n(v, 0)


def _linha_um(est: pd.DataFrame, id_linha: str, modelo: str | None = None, ciclo: str | None = None) -> pd.Series:
    s = est[est["id_linha"] == id_linha]
    if modelo is not None:
        s = s[(s["modelo"] == modelo) & (s["ciclo"] == ciclo)]
    if len(s) != 1:
        raise FalhaValidacao(f"esperava 1 linha {id_linha} {modelo} {ciclo}, achei {len(s)}")
    return s.iloc[0]


def _fig(est: pd.DataFrame, comp: str) -> pd.Series:
    return est[(est["id_linha"] == "FIG") & (est["componente"] == comp)].iloc[0]


def _verdadeiro(v) -> bool:
    return str(v).strip().lower() in ("true", "1")


def bloco(nome: str, corpo: str) -> list[str]:
    return [f"<!-- P1h:{nome}:inicio -->", corpo, f"<!-- P1h:{nome}:fim -->"]


def texto_portao(resumo: dict) -> str:
    p = resumo["portao"]
    def sci(e: dict, k: str) -> str:
        v = e.get(k)
        return "—" if v is None else f"{v:.1e}".replace(".", ",").replace("-", "−")

    linhas = []
    for e in p["especificacoes"]:
        linhas.append([ROTULO_ESPEC[e["especificacao"]], f"{e['termos_reestimados']} / {e['termos_gravados']}",
                       sci(e, "dif_max_coef"), sci(e, "dif_max_ep_cluster_conjunto"),
                       sci(e, "dif_max_ep_mle_informativo"), sci(e, "dif_max_ep_cluster_candidato_informativo"),
                       "passou" if e["passou"] else "**falhou**"])
    a = resumo["amostra"]
    t = [
        f"- Amostra: a do P1 (candidatos de 1ª opção com município de origem ligado no G1 e com região de saúde), "
        f"{a['n_candidatos_M1']} candidatos, {a['n_conjuntos_M1']} conjuntos de escolha (curso × ciclo), "
        f"{a['n_linhas_M1']} linhas candidato × célula no M1; no M7, {a['n_linhas_M7']} linhas (1ª e 2ª opção). "
        f"Por ciclo (M5): {a['n_candidatos_M5']['1']}, {a['n_candidatos_M5']['2']} e {a['n_candidatos_M5']['3']} "
        "candidatos.",
        f"- Distâncias das células escolhidas iguais às do G1: {a['conferencia_distancia']['escolhas_conferidas']} "
        f"escolhas, diferença máxima {_n(a['conferencia_distancia']['diferenca_maxima_km'], 9)} km.",
        f"- **Portão de reprodução: {p['status']}.** Tolerância 1e−8 na diferença máxima dos "
        "coeficientes e dos EP com cluster por conjunto, em todos os termos de cada especificação, contra "
        "`output/rdd_bolsa/P1_estimativas.csv` (gravado com 10 algarismos significativos). Os EP de máxima "
        "verossimilhança e por candidato vão ao lado, só como registro.",
        "",
        _tab(["Especificação", "Termos (reestimados / gravados)", "Dif. máx. coef.", "Dif. máx. EP cluster",
              "Dif. máx. EP MV", "Dif. máx. EP candidato", "Portão"], linhas),
    ]
    if p["status"] != "PASSOU":
        t += ["", f"A execução parou em `{p['status']}`: nenhuma linha do P1h foi calculada (protocolo 52b, §2)."]
    return "\n".join(t)


def texto_leitura(est: pd.DataFrame, resumo: dict) -> str:
    d = _linha_um(est, "P1h-1")
    k5, k10 = _linha_um(est, "P1h-2a"), _linha_um(est, "P1h-2b")
    b10, uf = _fig(est, "10β"), _fig(est, "θ_UF")
    beta = resumo["beta_M1"]
    txt = []
    abre = (f"No M1, toda a amplitude da bolsa (de R$ 10 mil para R$ 20 mil por mês, 10·β) pesa "
            f"{_n(b10['estimativa'], 2)} na utilidade da escolha (IC 95% {_ic(b10['ic95_inf'], b10['ic95_sup'], 2)}); "
            f"a vaga ficar na UF de origem pesa {_n(uf['estimativa'], 2)} "
            f"(IC {_ic(uf['ic95_inf'], uf['ic95_sup'], 2)}). A diferença D_UF = θ_UF − 10·β é "
            f"{_n(d['estimativa'], 2)} (EP {_n(d['ep_cluster_conjunto'], 3)}; IC 95% "
            f"{_ic(d['ic95_inf'], d['ic95_sup'], 2)}; limite inferior unilateral de 95% {_n(d['li95_unilateral'], 2)}; "
            f"{_peq(d['p_unilateral'])}, unilateral; família de um teste, p de Holm = p).")
    if _verdadeiro(d["rejeita_h0_5pct"]):
        txt.append(f"**P1h-1: rejeita H0 depois do Holm.** {abre} No modelo de escolha, a amplitude inteira da bolsa "
                   "pesa menos que a vaga ficar na UF de origem. Isso vale condicional a se candidatar e dentro das "
                   "vagas abertas. Não diz que a bolsa não tem efeito nem que a geografia causa a escolha: o peso da "
                   "UF é preferência revelada condicional ao modelo, e o da bolsa é o do pacote do corte.")
    else:
        txt.append(f"**P1h-1: não rejeita H0; inconclusivo.** {abre} Com esse intervalo, os dados não permitem dizer "
                   "se a amplitude da bolsa pesa mais ou menos que a vaga ficar na UF de origem.")
    beta_zero = beta["ic95_inf"] <= 0 <= beta["ic95_sup"]
    k5_zero = (k5["ic95_inf"] <= 0 <= k5["ic95_sup"]) and (k5["ic95_fieller_inf"] <= 0 <= k5["ic95_fieller_sup"])
    k10_zero = (k10["ic95_inf"] <= 0 <= k10["ic95_sup"]) and (k10["ic95_fieller_inf"] <= 0 <= k10["ic95_fieller_sup"])
    km = (f"**P1h-2 (km equivalentes, descritivo).** Um degrau da bolsa (R$ 5 mil por mês) pesa na escolha o mesmo "
          f"que a vaga ficar {_km(k5['estimativa'])} km mais perto da origem (IC 95% delta "
          f"{_ic(k5['ic95_inf'], k5['ic95_sup'], 0)}; Fieller {_ic(k5['ic95_fieller_inf'], k5['ic95_fieller_sup'], 0)}); "
          f"toda a amplitude (R$ 10 mil), {_km(k10['estimativa'])} km (delta "
          f"{_ic(k10['ic95_inf'], k10['ic95_sup'], 0)}; Fieller "
          f"{_ic(k10['ic95_fieller_inf'], k10['ic95_fieller_sup'], 0)}).")
    if beta_zero and k5_zero and k10_zero:
        km += (f" O IC 95% de β contém zero ({_ic(beta['ic95_inf'], beta['ic95_sup'], 4)}), e por isso o IC de K5 e "
               "o de K10 também contêm zero: os dados não descartam que a bolsa não valha nenhum km, nem que um degrau "
               f"valha até cerca de {_km(max(k5['ic95_sup'], k5['ic95_fieller_sup']))} km.")
    elif beta_zero:
        km += (f" O IC 95% de β contém zero ({_ic(beta['ic95_inf'], beta['ic95_sup'], 4)}); o IC de K5 ou de K10 por "
               "algum dos métodos não contém zero, e a tabela mostra qual.")
    else:
        km += f" O IC 95% de β não contém zero ({_ic(beta['ic95_inf'], beta['ic95_sup'], 4)})."
    km += (f" Pelo lado unilateral (H0: K ≤ 0), o limite inferior de 95% de K5 é {_km(k5['li95_unilateral'])} km pelo "
           f"delta e {_km(k5['li95_unilateral_fieller'])} km pelo Fieller ({_peq(k5['p_unilateral'])}, delta). Essas "
           "linhas são descritivas: o P1a foi pré-registrado como teste bilateral de β (protocolo 52, Holm; "
           f"{_peq(beta['p_bilateral'])}), e o lado unilateral das linhas de km não o substitui.")
    txt.append(km)
    sens = est[est["id_linha"] == "P1h-3"]
    partes = []
    for chave in SENSIBILIDADES:
        m, c = next((m, c) for k, m, c in ESPECS if k == chave)
        r = sens[(sens["modelo"] == m) & (sens["ciclo"] == c)].iloc[0]
        partes.append(f"{chave.replace('_', ' ciclo ')}: {_n(r['estimativa'], 2)} (IC {_ic(r['ic95_inf'], r['ic95_sup'], 2)}; "
                      f"{_peq(r['p_unilateral'])}; q BKY = {_n(r['q_bky'], 3)})")
    n_rej = int(sens["rejeita_h0_5pct"].map(_verdadeiro).sum())
    txt.append(f"**P1h-3 (sensibilidade, BKY entre as {len(sens)} linhas).** D_UF em " + "; ".join(partes) +
               f". Com q BKY < 0,05, {n_rej} de {len(sens)} especificações rejeitam H0: D_UF ≤ 0. O M2 mede a "
               "distância em log, então o seu θ_UF fica condicional a outra forma da distância; no M5, cada ciclo tem "
               "o seu β, e no ciclo em que β é perto de zero a diferença é quase só θ_UF.")
    txt.append("Tudo acima é escolha condicional a candidatar-se, dentro do conjunto de vagas abertas. Nada aqui diz "
               "se a bolsa \"funciona\" ou \"não funciona\": o contraste compara dois pesos dentro do mesmo modelo de "
               "escolha.")
    return "\n\n".join(txt)


def texto_tabela(est: pd.DataFrame) -> str:
    linhas = []
    for r in est[est["id_linha"] != "FIG"].itertuples():
        km = r.unidade == "km"
        cas = 0 if km else 3
        fiel = (f"{_ic(r.ic95_fieller_inf, r.ic95_fieller_sup, 0)}; LI {_n(r.li95_unilateral_fieller, 0)}"
                if km else "—")
        rej = "sim" if _verdadeiro(r.rejeita_h0_5pct) else ("não" if r.id_linha in ("P1h-1", "P1h-3") else "—")
        linhas.append([r.id_linha, f"{r.modelo}" + (f" ciclo {r.ciclo}" if r.ciclo != EMPILHADO else ""),
                       r.componente, _n(r.estimativa, cas), _n(r.ep_cluster_conjunto, cas), _n(r.ep_mle, cas),
                       _n(r.ep_cluster_candidato, cas), _ic(r.ic95_inf, r.ic95_sup, cas), _n(r.li95_unilateral, cas),
                       _p(r.p_unilateral), _p(r.p_unilateral_t_g_menos_1), fiel,
                       _p(r.p_holm) if r.entra_holm else (_n(r.q_bky, 3) if r.entra_bky else "—"), rej])
    t = _tab(["Linha", "Modelo", "Estimando", "Estimativa", "EP cluster", "EP MV", "EP candidato", "IC 95%",
              "LI unilateral 95%", "p unilateral", "p unil. (t, G−1)", "Fieller: IC 95%; LI 95%",
              "p Holm / q BKY", "Rejeita H0 a 5%"], linhas)
    figs = []
    for comp, rot, _, _ in PESOS_FIGURA:
        r = _fig(est, comp)
        figs.append([rot, comp, _n(r["estimativa"], 3), _n(r["ep_cluster_conjunto"], 3),
                     _ic(r["ic95_inf"], r["ic95_sup"], 3)])
    t2 = _tab(["Peso (M1)", "Combinação", "Estimativa", "EP cluster", "IC 95%"], figs)
    return "\n".join([
        "EP cluster = sanduíche com cluster por conjunto de escolha (curso × ciclo), a inferência principal; EP MV = "
        "máxima verossimilhança; EP candidato = cluster por candidato. IC, limite inferior (LI) unilateral e p "
        "unilateral (H0: estimando ≤ 0) usam o EP cluster pela normal; ao lado, o p unilateral pela t com G − 1 graus "
        "de liberdade. Linhas de km: estimativa, EP, IC e p pelo método delta; Fieller ao lado. Holm só no P1h-1 "
        "(família de um teste); BKY só entre as linhas P1h-3.",
        "", t, "",
        "Pesos da figura (M1, descritivos, mesma escala da utilidade):", "", t2])


def texto_figura(resumo: dict) -> str:
    f = resumo["figura"]
    return "\n".join([
        f"![{f['titulo'].replace(chr(10), ' ')}](../../{f['arquivo']})", "",
        f"Arquivo: `{f['arquivo']}`. Título da figura: \"{f['titulo'].replace(chr(10), ' ')}\".", "",
        f"**Como ler.** {f['como_ler']}"])


DESVIOS = [
    {"data": "2026-10-26", "item": "Linhas da figura no CSV",
     "situacao": "O §5 pede a figura dos pesos na mesma escala, mas o §3 só lista P1h-1 a P1h-3.",
     "resolucao": "Os seis pesos da figura (5β, 10β, −γ, θ_UF, θ_UF + θ_reg, θ_UF + θ_reg + θ_mun) vão para o CSV "
                  "com id_linha = FIG e papel descritivo, sem teste nem correção múltipla, para que a figura seja "
                  "lida de output/ (regra de proveniência)."},
    {"data": "2026-10-26", "item": "p unilateral das linhas de km",
     "situacao": "O §3 pede p unilateral em toda linha; para K5 e K10 o protocolo não diz o método.",
     "resolucao": "p de H0: K ≤ 0 pelo método delta, como o EP e o IC dessas linhas; o Fieller dá o IC 95% e o "
                  "limite inferior unilateral (conjunto de 90%). Pelo Fieller, H0: K ≤ 0 equivale a H0: β ≤ 0, porque "
                  "γ < 0. As linhas são descritivas e não substituem o teste bilateral do P1a."},
    {"data": "2026-10-26", "item": "Alcance do portão",
     "situacao": "O §2 manda conferir 'os coeficientes e os EP com cluster por conjunto'; o §3 aplica o mesmo portão "
                 "às sensibilidades.",
     "resolucao": "Todos os termos de cada especificação (M1, M2, M4, M5 por ciclo, M7) entram no portão; os EP de "
                  "MV e por candidato são registrados sem entrar nele. Qualquer falha para a execução inteira, com o "
                  "código da primeira especificação que falhou, e nada é calculado."},
    {"data": "2026-10-26", "item": "Rejeição nas sensibilidades",
     "situacao": "O §3 manda BKY entre as linhas P1h-3 sem dizer o nível.",
     "resolucao": "q BKY e a marca 'rejeita a 5%' (q < 0,05) são registrados como leitura de robustez; a única linha "
                  "com decisão é o P1h-1."},
]


def texto_desvios(resumo: dict) -> str:
    def data_br(iso: str) -> str:
        a, m, d = iso.split("-")
        return f"{d}/{m}/{a}"
    t = ["Nenhum desvio forçado pelos dados: a execução seguiu o protocolo 52b. Abaixo, as decisões de "
         "implementação onde o protocolo não fixava o detalhe, tomadas antes de ver os números do P1h.", ""]
    for i, d in enumerate(resumo["desvios"], 1):
        t.append(f"{i}. **{d['item']}** ({data_br(d['data'])}). {d['situacao']} *Resolução:* {d['resolucao']}")
    return "\n".join(t)


def gerar_doc(est: pd.DataFrame | None, resumo: dict) -> str:
    ok = resumo["portao"]["status"] == "PASSOU"
    Lh = [
        "# 57i. Resultados do P1h: o peso da bolsa contra o custo do lugar na escolha (H3)",
        "",
        "> **Gerado por** `scripts/rdd_bolsa/25c_magnitudes_P1h.py` a partir de `output/rdd_bolsa/P1h_*`; não editar "
        "à mão (o teste `tests/test_P1h_magnitudes.py` confere que este arquivo é igual ao gerado).<br>",
        "> **Protocolo:** [`52b_protocolo_P1h_magnitudes.md`](52b_protocolo_P1h_magnitudes.md), congelado em "
        "26/10/2026 antes de calcular; estatuto `PROTOCOLO_52B_POS_RESULTADO`.<br>",
        "> **O que já tinha sido visto:** os coeficientes do M1 e os seus IC (doc 57a, protocolo 52, auditoria 26) e a "
        "conta aproximada da linha primária (conversa de 26/10/2026). Este bloco acrescenta a inferência formal da "
        "diferença, com a covariância conjunta, e a bolsa em km com IC. Não é teste confirmatório novo.<br>",
        "> **Saídas:** `output/rdd_bolsa/P1h_magnitudes.csv`, `P1h_resumo.json` e "
        "`P1h_figuras/P1h_magnitudes.png`; toda saída tem `natureza_dos_dados = EMPIRICO`. As saídas do P1 (`P1_*`) "
        "não são regravadas.",
        "",
        "## 1. O que se mede e o que não se pode dizer",
        "",
        "- **Pergunta (H3, incentivo limitado).** No modelo de escolha do P1 (M1), o peso de toda a amplitude da "
        "bolsa que a política oferece (de R$ 10 mil para R$ 20 mil por mês, 10·β) é menor que o peso de a vaga "
        "ficar na UF de origem do candidato (θ_UF)?",
        "- **É uma comparação de pesos na utilidade da escolha**, não de efeitos causais do lugar. Os dois pesos "
        "estão na mesma escala (log-chance) e saem do mesmo modelo, por isso podem ser subtraídos.",
        "- **A bolsa (β)** é identificada pelos saltos da bolsa nos cortes de IVS (0,300 e 0,400), com o IVS em "
        "spline contínua: mede o pacote do corte (a bolsa e outras regras federais que mudam no mesmo IVS, "
        "auditoria 18) e o incentivo marginal, não a participação no PMM-E.",
        "- **A origem (θ)** é preferência revelada condicional ao modelo. Mistura família, rede, registro "
        "profissional e outros motivos ligados à origem. Não é efeito causal da geografia nem de mudar alguém de "
        "lugar.",
        "- **Escolha condicional.** Tudo vale para quem se candidatou, dentro do conjunto de vagas abertas do seu "
        "curso e ciclo. Nada sobre quem não se candidatou.",
        "- **O que não se pode dizer.** Nada aqui diz se a bolsa \"funciona\" ou \"não funciona\". Um peso menor que "
        "o da UF de origem não é efeito nulo da bolsa, e um peso grande da UF não diz que a geografia causa a "
        "escolha.",
        "",
        "Notação: β = `bolsa_mil` (por R$ 1 mil/mês); γ = `distancia_100km` (negativo); θ_UF = `mesma_uf`; θ_reg = "
        "`mesma_regiao_saude` (incremento sobre a mesma UF); θ_mun = `mesmo_municipio` (incremento sobre a mesma "
        "região).",
        "",
        "## 2. Amostra e portão de reprodução",
        "",
        *bloco("portao", texto_portao(resumo)),
        "",
    ]
    if ok:
        Lh += [
            "## 3. Leitura em linguagem simples",
            "",
            "Segue a leitura pré-registrada do §4 do protocolo 52b.",
            "",
            *bloco("leitura", texto_leitura(est, resumo)),
            "",
            "## 4. Tabela",
            "",
            *bloco("tabela", texto_tabela(est)),
            "",
            "## 5. Figura",
            "",
            *bloco("figura", texto_figura(resumo)),
            "",
        ]
    else:
        Lh += ["## 3. Resultado", "", *bloco("leitura", "Nada calculado: o portão de reprodução falhou."), ""]
    Lh += [
        "## 6. Desvios e decisões de implementação",
        "",
        *bloco("desvios", texto_desvios(resumo)),
        "",
        "## 7. Limites",
        "",
        "- **Pós-resultado.** Os coeficientes do M1 já eram conhecidos; o P1h formaliza uma comparação cuja resposta "
        "era previsível pelos IC publicados. Não é teste confirmatório novo.",
        "- **Escolha condicional.** Os pesos descrevem como quem se candidatou ordena as vagas abertas; não medem "
        "entrada no programa, oferta líquida de especialistas nem permanência.",
        "- **θ não é causal.** A origem é o município do estabelecimento de vínculo médico no CNES, não a residência, "
        "e o peso da UF de origem junta tudo o que a origem carrega (família, rede, registro profissional e outros "
        "motivos).",
        "- **β é pacote do corte e é impreciso.** O IC de β no M1 contém zero; as razões em km herdam essa "
        "imprecisão. A bolsa entra linear entre R$ 10 e R$ 20 mil: 10·β supõe que os dois degraus pesam o mesmo.",
        "- **Distância linear.** K5 e K10 usam a distância linear do M1; com a distância em log (M2), um km não vale "
        "o mesmo em toda distância, e a conversão não se aplica.",
        "- **Poucos conjuntos.** São 56 conjuntos de escolha (curso × ciclo); o EP com cluster por conjunto é "
        "impreciso, e o p pela t com G − 1 graus de liberdade vai ao lado.",
        "- **IIA e especificações fora.** O logit condicional supõe independência de alternativas irrelevantes. O "
        "logit misto (M8) e o aninhado (M9) ficaram fora do P1h (o M8 é caro de reestimar); o M3 não foi estimado no "
        "P1.",
    ]
    return "\n".join(Lh) + "\n"


# ---------------------------------------------------------------------------
# Execução
# ---------------------------------------------------------------------------

def entradas(dados: dict) -> list[dict]:
    E9, X45, X1 = P1.E9, P1.X45, P1.X1
    be = P1.bloco_entrada
    return [
        be(PROTOCOLO_MD, "protocolo 52b (somente lido)", "repositório", "2026-10-26", "§1–§6", "documento", "-", "-"),
        be(P1_EST, "alvo do portão de reprodução (coeficientes e EP do P1)", "script 25 (P1)", "2026-10-23",
           "M1, M2, M4, M5 (ciclos 1–3), M7", "especificação × termo", "modelo, ciclo, tipo_linha, termo",
           "tipo_linha = coeficiente"),
        be(SCRIPT_25, "funções de amostra, desenho e ajuste (importadas sem alteração)", "repositório", "2026-10-23",
           "-", "código", "-", "-"),
        be(E9.ESCOLHAS, "escolhas dos candidatos (1ª e 2ª opção)", "tarefa B (script 12)",
           "resultados da 1ª chamada dos ciclos 1–3", f"{len(dados['cand'])} linhas", "candidato × opção",
           "ciclo, id_candidato, opcao_rank", "postos 1 e 2"),
        be(E9.CONJ_PRINCIPAL, "conjunto de escolha principal (E9 §14)", "tarefa B (script 12)", "quadros da 1ª chamada",
           f"{len(dados['conj'])} células com IVS", "célula CNES × curso × ciclo", "ciclo, co_cnes_7d, cod_curso",
           "sem IVS oficial e sem CIR fora (como no P1)"),
        be(E9.IVS_OFICIAL, "IVS 2010 oficial (a08): spline e regra das faixas", "Ipea (a08)", "Censo 2010",
           f"{len(dados['ivs'])} municípios", "município", "co_ibge", "co_ibge, ivs"),
        be(E9.GRADES_EDITAIS, "mapa faixa → bolsa", "editais (a03)", "2025–2026", "3 faixas", "faixa", "faixa",
           "mapeamento_regras_por_edital"),
        be(E9.GRADE_2025, "conferência do mapa faixa → bolsa", "FAQ 3/2025 (a04)", "2025", "3 faixas", "faixa",
           "faixa_atracao", "-"),
        be(E9.DICIONARIO, "dicionário da tarefa B (hash das tabelas de escolha conferido)", "pipeline", "2026-10-18",
           "-", "documento", "-", "-"),
        be(P1.G1_ORIGEM, "município de origem dos candidatos (G1)", "portão G1", "referências 202506, 202510, 202602",
           f"{len(dados['org'])} candidatos (regra principal)", "candidato", "ciclo, id_candidato",
           f"regra_ligacao = {P1.REGRA_G1}"),
        be(P1.G1_DIST, "conferência das distâncias das células escolhidas", "portão G1", "idem",
           "linhas candidato × opção", "candidato × opção", "ciclo, id_candidato, opcao_rank",
           f"regra_ligacao = {P1.REGRA_G1}"),
        be(P1.G1_RESUMO, "resumo do G1 (lido pela função de carga do script 25)", "portão G1", "2026-10-19", "-",
           "documento", "-", "-"),
        be(X45.CIR_BRUTO, "região de saúde (CIR) por município (só lido)", "DATASUS/TabNet (manifesto da X5)",
           dados["manifesto_cir"]["data_download_utc"], f"{dados['diag_cir']['municipios']} municípios", "município",
           "co_ibge → co_cir", "linhas 'Ignorado' fora"),
        be(X1.COORD_JSON, "centroides municipais do IBGE (distância, só lido)", "IBGE, API de malhas v3",
           str(dados["diag_coord"].get("data_download", "")), f"{dados['diag_coord'].get('municipios')} municípios",
           "município", "id (7 dígitos)", "centroide"),
    ]


def remover_saidas_calculadas() -> None:
    for p in (OUT_CSV, FIG):
        if p.exists():
            p.unlink()
    if DIR_FIG.exists() and not any(DIR_FIG.iterdir()):
        DIR_FIG.rmdir()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--atualizar-doc", action="store_true", help="só regrava o doc 57i a partir das saídas")
    args = ap.parse_args(argv)
    if args.atualizar_doc:
        atualizar_doc()
        return 0
    t0 = time.time()

    def log(m: str) -> None:
        print(f"[{time.time() - t0:7.0f}s] {m}", flush=True)

    dados = P1.carregar()
    log("insumos do P1 carregados")
    res, conf_dist = reestimar(dados, log)
    est_p1 = pd.read_csv(P1_EST, dtype={"ciclo": str})
    port = portao(res, est_p1)
    log(f"portão: {port['status']}")
    resumo = {
        "etapa": "P1h_magnitudes",
        "natureza_dos_dados": NATUREZA,
        "estatuto": ESTATUTO,
        "data_execucao": DATA_EXECUCAO,
        "script": rel(Path(__file__)),
        "protocolo": {"arquivo": rel(PROTOCOLO_MD), "sha256": sha256(PROTOCOLO_MD)},
        "portao": port,
        "amostra": {"n_candidatos_M1": res["M1"]["n_candidatos"], "n_conjuntos_M1": res["M1"]["n_conjuntos"],
                    "n_linhas_M1": res["M1"]["n_linhas"], "n_linhas_M7": res["M7"]["n_linhas"],
                    "n_candidatos_M5": {str(k): res[f"M5_{k}"]["n_candidatos"] for k in P1.CICLOS},
                    "conferencia_distancia": conf_dist},
        "desvios": DESVIOS,
        "entradas": entradas(dados),
        "integridade": ("nada simulado, imputado ou digitado como observação; IVS do a08 (o arquivo local de IVS da "
                        "auditoria 16 não é lido); nenhum mês do CNES é lido; só agregados em output/ (sem nome, CPF, "
                        "CRM nem pseudônimo de candidato); data/ só lido; saídas P1_* não regravadas"),
        "linguagem": ("θ é preferência revelada condicional ao modelo, não efeito causal da geografia; β é o peso da "
                      "bolsa identificado pelos cortes (pacote do corte); escolha condicional a candidatar-se, dentro "
                      "das vagas abertas; nada aqui diz se a bolsa 'funciona' ou 'não funciona'"),
        "tempo_execucao_nao_registrado": "o tempo de execução fica fora do resumo para que duas execuções deem o mesmo hash",
    }
    if port["status"] != "PASSOU":
        remover_saidas_calculadas()
        resumo["saidas"] = {}
        gravar_json(OUT_RESUMO, resumo)
        atualizar_doc()
        print(f"{port['status']}: nada calculado (protocolo 52b, §2)", file=sys.stderr)
        return 3

    est = montar_linhas(res)
    sem_valor = est[est["estimativa"].isna() | est["ep_cluster_conjunto"].isna()]
    if len(sem_valor):
        raise FalhaValidacao(f"{len(sem_valor)} linhas sem estimativa ou EP")
    est.to_csv(OUT_CSV, index=False, float_format="%.10g")
    est = ler_est()
    d = _linha_um(est, "P1h-1")
    r1 = res["M1"]
    kb = r1["termos"].index(B)
    b, eb = float(r1["theta"][kb]), math.sqrt(r1["V_conj"][kb, kb])
    resumo["beta_M1"] = {"coef": b, "ep_cluster_conjunto": eb, "ic95_inf": b - Z95 * eb, "ic95_sup": b + Z95 * eb,
                         "p_bilateral": float(2 * stats.norm.sf(abs(b / eb)))}
    resumo["resultado_principal"] = {
        "id": "P1h-1", "estimando": "D_UF = θ_UF − 10·β", "modelo": "M1", "estimativa": d["estimativa"],
        "ep_cluster_conjunto": d["ep_cluster_conjunto"], "ic95": [d["ic95_inf"], d["ic95_sup"]],
        "li95_unilateral": d["li95_unilateral"], "p_unilateral": d["p_unilateral"], "p_holm": d["p_holm"],
        "rejeita_h0_5pct": _verdadeiro(d["rejeita_h0_5pct"]),
        "leitura_pre_registrada": ("rejeita: a amplitude inteira da bolsa pesa menos que a vaga ficar na UF de origem, "
                                   "condicional a se candidatar e dentro das vagas abertas" if
                                   _verdadeiro(d["rejeita_h0_5pct"]) else "inconclusivo")}
    resumo["covariancias"] = covariancias_chave(res)
    resumo["inferencia"] = {"principal": "sanduíche com cluster por conjunto de escolha (curso × ciclo), fator G/(G−1)",
                            "adicionais": ["máxima verossimilhança", "cluster por candidato",
                                           "p unilateral pela t com G − 1 gl"],
                            "z_bilateral_95": Z95, "z_unilateral_95": Z95_UNI,
                            "holm": "só P1h-1, família de um teste", "bky": "só entre as linhas P1h-3 (p unilateral)",
                            "km": "delta (EP, IC, p) e Fieller (IC 95% e limite unilateral pelo conjunto de 90%)"}
    resumo["figura"] = figura(est)
    resumo["como_ler"] = {FIG.name: COMO_LER}
    resumo["saidas"] = {rel(OUT_CSV): sha256(OUT_CSV), rel(FIG): resumo["figura"]["sha256"]}
    gravar_json(OUT_RESUMO, resumo)
    atualizar_doc()
    log(f"gravado: {rel(OUT_CSV)}, {rel(OUT_RESUMO)}, {rel(FIG)}, {rel(DOC)}")
    return 0


def ler_est() -> pd.DataFrame:
    return pd.read_csv(OUT_CSV, dtype={"ciclo": str})


def ler_resumo() -> dict:
    return json.loads(OUT_RESUMO.read_text(encoding="utf-8"))


def atualizar_doc() -> None:
    resumo = ler_resumo()
    est = ler_est() if resumo["portao"]["status"] == "PASSOU" else None
    DOC.write_text(gerar_doc(est, resumo), encoding="utf-8")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except FalhaValidacao as erro:
        print(f"FALHA DE VALIDACAO: {erro}", file=sys.stderr)
        sys.exit(2)
