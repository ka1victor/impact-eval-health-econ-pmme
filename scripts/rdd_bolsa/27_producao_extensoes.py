"""P3, extensões do adendo §12 do protocolo 47 (T3.2–T3.5 do doc 51): especialidade, residência, revisão, controles e região.

Protocolo congelado: `docs/06_execucao/47_protocolo_producao_especializada.md`, adendo §12 (12.1–12.5), escrito
depois dos portões G3 e G4 e **depois** de vistos os resultados D1 e D2 (doc 50). Toda linha sai com
`estatuto = PROTOCOLO_47_ADENDO_12_POS_RESULTADO` e `natureza_dos_dados = EMPIRICO`. Nada aqui muda o Holm de
K1–K3; o adendo tem BKY próprio.

Itens, na ordem de prioridade pedida pelo autor
-----------------------------------------------
- 12.2 (T3.2): produção da especialidade que chegou. Unidade = par município × curso (cursos da classe
  ESPECIFICO do G4). Outcome = quantidade aprovada no SIA (a17) nas formas de organização típicas do curso
  (coluna `tipica` do mapa do G4), executada pelas CBO do curso, por 10 mil hab. Tratado = 1ª chegada de
  especialista do curso c em m (lista nominal); controles = pares do mesmo curso que ofereceram célula e ainda
  não receberam (Callaway–Sant'Anna como no D2, controles dentro do curso). Principal = θ agregado com peso pelo
  número de pares tratados de cada curso e coorte; também por curso. Inferência com cluster no município.
- 12.4 (T3.4): K2r = AIH do grupo 04 de residentes (a15) e K2r_tot = todas as AIH de residentes (grupos 02–05),
  por 10 mil hab.; D1 (DiRD nos cortes) e D2 (chegada), com as janelas de K2. Mede acesso dos residentes, não
  oferta local.
- 12.1: sensibilidade da revisão da fonte. K2 com a safra v2 do SIH (a13b) em D1 e D2, lado a lado com a v1
  (recalculada e conferida contra K_D1/K_D2). K1 só se a safra v2 do SIA (a12b) tiver revisão: o a12b relata
  zero células diferentes, então K1 não é reestimado (linha NAO_EXECUTADO com o motivo).
- 12.3 (T3.3): (a) D2 de K1 no município só com controles cujas células ficaram vazias (nunca tratados);
  (b) diferenças em diferenças sintéticas (Arkhangelsky et al., 2021) para K1, por coorte, agregadas pelo número
  de tratados; (c) heterogeneidade pela fração de chegados que já tinham vínculo no município antes do início
  (X1, regra D1, `b_mesmo_mun_ultimo_pre`), em tercis da distribuição entre os municípios tratados.
- 12.5 (T3.5): K1 e K2 somados nos **outros** municípios da mesma região de saúde (CIR do TabNet), por 10 mil
  hab. da região sem o município; D2 com as mesmas coortes. Negativo = deslocamento; positivo = referência.

Leitura: D2, 12.2, 12.3 e 12.5 medem ATT sob tendências paralelas (a chegada depende da escolha do candidato;
não há fonte de exogeneidade validada); pré não plano -> associação. D1 mede o incentivo marginal dentro do
pacote dos cortes. Expansão líquida e deslocamento são separados pela leitura conjunta de 12.2/K1 (município) e
12.5 (região).

Integridade: nada imputado; ausente fica ausente (NaN) com motivo; nenhum mês CNES é lido; SIA e SIH até 202607
(séries até 202605, adendo §10.1); a lista nominal é lida só nas colunas co_ibge, curso, dt_inicio_atividade,
ciclo e dt_referencia (nenhum nome); o arquivo local de IVS da auditoria 16 não é lido; `data/` só é lido.

Saídas: output/rdd_bolsa/K_X_estimativas.csv, K_X_estudo_evento.csv, K_X_att_gt.csv, K_X_resumo.json e
K_X_figuras/*.png; doc gerado inteiro: docs/06_execucao/57c_resultados_P3_extensoes.md.

Uso
---
    python3 scripts/rdd_bolsa/27_producao_extensoes.py
    python3 scripts/rdd_bolsa/27_producao_extensoes.py --atualizar-doc
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

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
K1M = _importar(DIR_RDD / "21_producao_dird.py", "k21_para_kx")
D2M = _importar(DIR_RDD / "22_chegada_pmme_evento.py", "k22_para_kx")
sys.dont_write_bytecode = _bytecode
L, E7 = K1M.L, K1M.E7

# ---------------------------------------------------------------------------
# Caminhos e parâmetros (constantes permitidas: janelas, sementes, rótulos)
# ---------------------------------------------------------------------------

OUT = K1M.OUT
AQ = K1M.AQ
NOME_EST = "K_X_estimativas.csv"
NOME_EVENTO = "K_X_estudo_evento.csv"
NOME_ATT = "K_X_att_gt.csv"
NOME_RESUMO = "K_X_resumo.json"
DIR_FIG = "K_X_figuras"
DOC = ROOT / "docs" / "06_execucao" / "57c_resultados_P3_extensoes.md"
PROTOCOLO_MD = K1M.PROTOCOLO_MD

A17_DIR = AQ / "sia_forma_curso"
A17_PAINEL = A17_DIR / "painel_sia_municipio_mes_forma_curso.parquet"
A17_MANIF = A17_DIR / "manifesto_sia_forma_curso.json"
A17_PRES = A17_DIR / "sia_forma_curso_formas_por_consulta.csv"
A17_TIPICAS = A17_DIR / "sia_forma_curso_formas_tipicas.csv"
A17_CURSOS = A17_DIR / "sia_forma_curso_cursos.csv"
G4_RESUMO = OUT / "G4_resumo.json"
G4_MAPA = OUT / "G4_mapa_especialidade_procedimento.csv"
SIH_V2 = AQ / "sih_v2" / "painel_sih_municipio_mes_grupo.parquet"
SIH_V2_MANIF = AQ / "sih_v2" / "manifesto_sih.json"
SIH_V2_COMP = AQ / "sih_v2" / "comparacao_v2_v1_resumo.json"
SIA_V2_COMP = AQ / "sia_v2" / "comparacao_v2_v1_resumo.json"
A15_PAINEL = AQ / "sih_residencia" / "painel_sih_residencia_municipio_mes_grupo.parquet"
A15_MANIF = AQ / "sih_residencia" / "manifesto_sih_residencia.json"
CIR_CNV = ROOT / "data" / "raw" / "aquisicao" / "territorio" / "datasus_tabnet_br_regsaud.cnv"
X1_MEDICOS = OUT / "X1_medicos.parquet"
V_CELULA = OUT / "outcomes" / "outcomes_V_celula.parquet"
NOMINAL = D2M.NOMINAL
K_D1_EST = OUT / K1M.NOME_EST
K_D2_EST = OUT / D2M.NOME_EST

DATA_EXECUCAO = "2026-10-23"
ESTATUTO = "PROTOCOLO_47_ADENDO_12_POS_RESULTADO"
NATUREZA = "EMPIRICO"
E_MIN, E_MAX = D2M.E_MIN, D2M.E_MAX
B_BOOT = D2M.B_BOOT
SEMENTE = D2M.SEMENTE
B_SDID = 200                         # replicações do bootstrap do synthdid (padrão do pacote)
SEMENTE_SDID = 20261023
INICIO = D2M.INICIO                  # 202201
FIM = "202605"                       # séries de SIA e SIH (adendo §10.1)
LIMITE_SIA_SIH = K1M.LIMITE_SIA_SIH  # 202607: nenhum mês posterior é lido
MESES = K1M._meses(INICIO, FIM)
MESES_LEITURA = K1M._meses(INICIO, LIMITE_SIA_SIH)
COMP_PRE = K1M.COMP_PRE
POS_K2 = K1M.POS_K1                  # 202510-202605 (o pós de K2)
POS_ATE = K1M.POS_ATE_202607
GRUPOS_SIH = ("02", "03", "04", "05")
COLUNAS_NOMINAL = ["co_ibge", "curso", "dt_inicio_atividade", "ciclo", "dt_referencia"]
STATUS_A17_OK = ("valor_tabnet", "zero_tabnet")
STATUS_A15_AUS = ("ausente_uf_mes_sem_dado", "ausente_uf_internacao_sem_dado")
UNIDADE = "por 10 mil hab. por mes (Censo 2022)"
TODOS = "todos_os_cursos"
FATOR_MDE = K1M.FATOR_MDE

CONTRASTE_D2 = ("ATT da chegada sob tendencias paralelas (Callaway-Sant'Anna, base universal g-1); nao e efeito com "
                "fonte de exogeneidade validada nem efeito do incentivo marginal")
CONTRASTE_D1 = K1M.CONTRASTE_DIRD
CONTRASTE_SDID = ("ATT da chegada por diferencas em diferencas sinteticas (pesos de unidade e de tempo), sob a hipotese "
                  "de que a combinacao ponderada dos nunca tratados reproduz a trajetoria sem chegada")


class FalhaValidacao(RuntimeError):
    """Validação obrigatória falhou: o script para sem gravar."""


sha256, rotulo, _ibge6 = K1M.sha256, K1M.rotulo, K1M._ibge6

# ---------------------------------------------------------------------------
# 1. Callaway–Sant'Anna generalizado (funções puras; testadas com dados sintéticos em memória)
# ---------------------------------------------------------------------------


def att_gt_geral(Y: np.ndarray, G: np.ndarray, coortes, *, grupo: np.ndarray | None = None,
                 elegivel: np.ndarray | None = None, controles: str = "ainda_nao", e_min: int = E_MIN,
                 e_max: int = E_MAX, min_controles: int = 2) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    """ATT(g, t) com base universal b = g - 1.

    Y: N x T (NaN = ausente). G: índice do período de tratamento (-1 = não tratado no horizonte).
    coortes: lista de (grupo, g) — com grupo None quando não há grupos.
    grupo: rótulo por unidade; os controles de uma coorte são só do mesmo grupo (12.2: o curso).
    elegivel: máscara das unidades tratadas que formam coortes (12.3c: o tercil); as demais tratadas continuam
    controles antes de serem tratadas.
    controles: "ainda_nao" (nunca tratados + G > max(t, b)) ou "nunca" (só G < 0).
    Devolve a tabela das células, a matriz IF (N x células; ATT^ - ATT ~ média de IF) e a chave de coorte por
    unidade (para os pesos da agregação).
    """
    N, T = Y.shape
    grp = np.zeros(N, dtype=object) if grupo is None else np.asarray(grupo, dtype=object)
    eleg = np.ones(N, dtype=bool) if elegivel is None else np.asarray(elegivel, dtype=bool)
    chave = np.array([f"{a}|{g}" if (g >= 0 and e) else "" for a, g, e in zip(grp, G, eleg)], dtype=object)
    linhas, ifs = [], []
    for gv, g in coortes:
        gv = 0 if grupo is None else gv
        b = g - 1
        if b < 0:
            continue
        mesmo = grp == gv
        tratada = (G == g) & eleg & mesmo
        n_g_total = int(tratada.sum())
        for t in range(max(0, g + e_min), min(T, g + e_max + 1)):
            if t == b:
                continue
            ok = np.isfinite(Y[:, t]) & np.isfinite(Y[:, b])
            dy = Y[:, t] - Y[:, b]
            if controles == "nunca":
                ctrl = (G < 0) & mesmo
            else:
                ctrl = ((G < 0) | (G > max(t, b))) & (G != g) & mesmo
            mt, mc = tratada & ok, ctrl & ok
            n1, n0 = int(mt.sum()), int(mc.sum())
            reg = {"g": f"{gv}|{g}", "grupo": gv, "gi": g, "t": t, "e": t - g, "n_tratados": n1, "n_controles": n0,
                   "n_coorte": n_g_total, "att": np.nan, "ep": np.nan, "nota": ""}
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
    tab = pd.DataFrame(linhas, columns=["g", "grupo", "gi", "t", "e", "n_tratados", "n_controles", "n_coorte",
                                        "att", "ep", "nota"])
    return tab, (np.column_stack(ifs) if ifs else np.zeros((N, 0))), chave


def somar_cluster(IF: np.ndarray, cluster: np.ndarray) -> tuple[np.ndarray, int]:
    """Soma as funções de influência por cluster e reescala por M/N, para que as funções do D2 (que dividem por
    linhas) deem EP com cluster: perturbação = xi_M @ IF_c / N. Colunas sem estimativa ficam NaN."""
    N = IF.shape[0]
    codes, uniq = pd.factorize(np.asarray(cluster), sort=True)
    M = len(uniq)
    nan_col = ~np.isfinite(IF).all(axis=0)
    out = np.zeros((M, IF.shape[1]))
    np.add.at(out, codes, np.nan_to_num(IF))
    out *= M / N
    out[:, nan_col] = np.nan
    return out, M


def estimar_cs_cluster(Y: np.ndarray, G: np.ndarray, coortes, cluster: np.ndarray, *, grupo=None, elegivel=None,
                       controles: str = "ainda_nao", semente: int = SEMENTE, B: int = B_BOOT,
                       e_min: int = E_MIN, e_max: int = E_MAX) -> dict:
    """CS com agregação por tempo de evento (pesos = tamanho de cada coorte × grupo) e inferência com cluster."""
    tab, IF, chave = att_gt_geral(Y, G, coortes, grupo=grupo, elegivel=elegivel, controles=controles,
                                  e_min=e_min, e_max=e_max)
    ev, IFe = D2M.agregar_evento(tab, IF, chave, e_min=e_min, e_max=e_max)
    IFc, M = somar_cluster(IFe, cluster)
    xi = D2M.pesos_mammen(B, M, semente)
    th = ev["theta"].to_numpy(dtype=float)
    inf = D2M.inferencia(th, IFc, xi)
    ev["ep"] = inf["ep_boot"]
    ev["ep_analitico"] = inf["ep_analitico"]
    ev["ic95_inf"] = th - L.Z_975 * ev["ep"]
    ev["ic95_sup"] = th + L.Z_975 * ev["ep"]
    ev["banda_unif_inf"] = th - inf["crit_uniforme"] * ev["ep"]
    ev["banda_unif_sup"] = th + inf["crit_uniforme"] * ev["ep"]
    ev["p_valor"] = [L.p_normal(a / b) if np.isfinite(a) and np.isfinite(b) and b > 0 else np.nan
                     for a, b in zip(th, ev["ep"])]
    ev.loc[ev["referencia"], ["ep", "ep_analitico", "ic95_inf", "ic95_sup", "banda_unif_inf", "banda_unif_sup",
                              "p_valor"]] = np.nan
    e = ev["e"].to_numpy()
    pre = e <= -2
    post = (e >= 0) & np.isfinite(th)
    pt = D2M.wald_pre(th, IFc, pre, xi)
    res = {"att_gt": tab, "evento": ev, "pre": pt, "n_clusters": M, "xi": xi}
    if post.any():
        psi = IFc[:, post].mean(axis=1)
        val = float(th[post].mean())
        pert = xi @ psi / M
        q75, q25 = np.percentile(pert, [75, 25])
        ep = float((q75 - q25) / D2M.Z_IQR)
        res["psi_pos"] = psi
        res["pos"] = {"att": val, "ep": ep, "ep_analitico": float(math.sqrt(np.sum(psi ** 2)) / M),
                      "ic95_inf": val - L.Z_975 * ep, "ic95_sup": val + L.Z_975 * ep,
                      "p_valor": L.p_normal(val / ep) if ep > 0 else np.nan,
                      "e_min": int(e[post].min()), "e_max": int(e[post].max()), "n_e": int(post.sum())}
    else:
        res["psi_pos"] = None
        res["pos"] = {"att": np.nan, "ep": np.nan, "ep_analitico": np.nan, "ic95_inf": np.nan, "ic95_sup": np.nan,
                      "p_valor": np.nan, "e_min": None, "e_max": None, "n_e": 0}
    return res


def diferenca_pos(r1: dict, r0: dict) -> dict:
    """Diferença dos ATT médios do pós (r1 - r0) estimados sobre as MESMAS unidades e os mesmos pesos xi."""
    if r1["psi_pos"] is None or r0["psi_pos"] is None:
        return {"att": np.nan, "ep": np.nan, "ic95_inf": np.nan, "ic95_sup": np.nan, "p_valor": np.nan}
    psi = r1["psi_pos"] - r0["psi_pos"]
    M = psi.size
    val = r1["pos"]["att"] - r0["pos"]["att"]
    pert = r1["xi"] @ psi / M
    q75, q25 = np.percentile(pert, [75, 25])
    ep = float((q75 - q25) / D2M.Z_IQR)
    return {"att": float(val), "ep": ep, "ic95_inf": val - L.Z_975 * ep, "ic95_sup": val + L.Z_975 * ep,
            "p_valor": L.p_normal(val / ep) if ep > 0 else np.nan}


# ---------------------------------------------------------------------------
# 2. Diferenças em diferenças sintéticas (Arkhangelsky et al., 2021; algoritmo do pacote synthdid)
# ---------------------------------------------------------------------------


def fw_pesos(Ymat: np.ndarray, zeta: float, *, intercepto: bool = True, lam: np.ndarray | None = None,
             min_decrease: float = 1e-5, max_iter: int = 10_000) -> np.ndarray:
    """Frank–Wolfe do `sc.weight.fw` do synthdid: min ||A·lam − b||²/N0 + zeta²||lam||², lam no simplex.

    Ymat: N0 x (T0 + 1), com o alvo b na última coluna.
    """
    N0, T1 = Ymat.shape
    T0 = T1 - 1
    lam = np.full(T0, 1.0 / T0) if lam is None else np.asarray(lam, dtype=float).copy()
    Ym = Ymat - Ymat.mean(axis=0) if intercepto else Ymat
    A, b = Ym[:, :T0], Ym[:, T0]
    eta = N0 * zeta ** 2
    # Atualizações incrementais (A·lam e A'A·lam), algebricamente iguais ao passo do pacote e muito mais baratas.
    gram = A.T @ A
    Atb = A.T @ b
    Ax = A @ lam
    g1 = A.T @ Ax
    z2 = zeta ** 2
    vals: list[float] = []
    it = 0
    while it < max_iter and (it < 2 or vals[-2] - vals[-1] > min_decrease ** 2):
        it += 1
        meio_grad = g1 - Atb + eta * lam
        i = int(meio_grad.argmin())
        if lam[i] == 1.0:                      # direção nula: o pacote devolve o mesmo vetor
            vals.append(vals[-1] if vals else 0.0)
            continue
        dx = -lam
        dx[i] += 1.0
        derr = A[:, i] - Ax
        passo = -float(meio_grad @ dx) / (float(derr @ derr) + eta * float(dx @ dx))
        passo = min(1.0, max(0.0, passo))
        lam = lam + passo * dx
        Ax = Ax + passo * derr
        g1 = g1 + passo * (gram[:, i] - g1)
        err = Ax - b
        vals.append(z2 * float(lam @ lam) + float(err @ err) / N0)
    return lam


def _esparsificar(v: np.ndarray) -> np.ndarray:
    v = v.copy()
    v[v <= v.max() / 4] = 0
    return v / v.sum()


def sdid(Y: np.ndarray, N0: int, T0: int, *, zetas: tuple[float, float, float] | None = None,
         pesos_ini: tuple[np.ndarray, np.ndarray] | None = None) -> dict:
    """Estimador synthdid: Y = (N0 controles + N1 tratados) x (T0 pré + T1 pós), sem ausentes.

    zetas = (zeta_omega, zeta_lambda, min_decrease); se None, calculados como no pacote (nível de ruído = DP das
    primeiras diferenças dos controles no pré; eta_omega = (N1 T1)^(1/4); eta_lambda = 1e-6).
    """
    N, T = Y.shape
    N1, T1 = N - N0, T - T0
    if zetas is None:
        ruido = float(np.std(np.diff(Y[:N0, :T0], axis=1), ddof=1))
        eta_o = (N1 * T1) ** 0.25
        zetas = (eta_o * ruido, 1e-6 * ruido, 1e-5 * ruido)
    z_o, z_l, md = zetas
    Yc = np.zeros((N0 + 1, T0 + 1))
    Yc[:N0, :T0] = Y[:N0, :T0]
    Yc[:N0, T0] = Y[:N0, T0:].mean(axis=1)
    Yc[N0, :T0] = Y[N0:, :T0].mean(axis=0)
    Yc[N0, T0] = Y[N0:, T0:].mean()
    lam0 = None if pesos_ini is None else pesos_ini[1]
    om0 = None if pesos_ini is None else pesos_ini[0]
    lam = fw_pesos(Yc[:N0, :], z_l, lam=lam0, min_decrease=md, max_iter=100)
    lam = fw_pesos(Yc[:N0, :], z_l, lam=_esparsificar(lam), min_decrease=md)
    om = fw_pesos(Yc[:, :T0].T, z_o, lam=om0, min_decrease=md, max_iter=100)
    om = fw_pesos(Yc[:, :T0].T, z_o, lam=_esparsificar(om), min_decrease=md)
    vu = np.concatenate([-om, np.full(N1, 1.0 / N1)])
    vt = np.concatenate([-lam, np.full(T1, 1.0 / T1)])
    return {"tau": float(vu @ Y @ vt), "omega": om, "lambda": lam, "zetas": zetas}


# ---------------------------------------------------------------------------
# 3. Leitura das fontes (filtros cedo; SHA-256 conferido contra os manifestos)
# ---------------------------------------------------------------------------


def _conferir(caminho: Path, esperado: str | None, nome: str) -> None:
    K1M.conferir_sha(caminho, esperado, nome)


def ler_sih_v2(universo: pd.Index) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """K2 com a safra v2 (a13b): mesmas regras do leitor da v1 (`21.ler_sih`)."""
    import pyarrow.parquet as pq
    man = json.loads(SIH_V2_MANIF.read_text(encoding="utf-8"))
    _conferir(SIH_V2, man["saidas"]["painel"]["sha256"], "painel SIH v2")
    df = pq.read_table(SIH_V2, columns=["co_ibge", "uf", "competencia", "grupo", "aih_aprovadas", "status",
                                        "uf_mes_atipico", "natureza_dos_dados"],
                       filters=[("grupo", "=", "04")]).to_pandas()
    if set(df["natureza_dos_dados"].astype(str)) != {NATUREZA}:
        raise FalhaValidacao("SIH v2 com natureza diferente de EMPIRICO")
    if df["competencia"].max() > LIMITE_SIA_SIH or set(MESES_LEITURA) - set(df["competencia"]):
        raise FalhaValidacao("SIH v2: meses fora do limite ou ausentes")
    if df.duplicated(["co_ibge", "competencia"]).any():
        raise FalhaValidacao("SIH v2 com chave repetida")
    aus = df["status"] == K1M.STATUS_SIH_AUSENTE
    if (df["aih_aprovadas"].isna() != aus).any():
        raise FalhaValidacao("SIH v2: aih_aprovadas nula sem status de ausencia (ou o contrario)")
    df["q"] = pd.to_numeric(df["aih_aprovadas"], errors="coerce").astype(float)
    larga = df.pivot(index="co_ibge", columns="competencia", values="q").reindex(columns=list(MESES_LEITURA))
    atip = df.pivot(index="co_ibge", columns="competencia", values="uf_mes_atipico").reindex(columns=list(MESES_LEITURA))
    info = {"municipios_painel": int(larga.shape[0]),
            "municipios_de_U_fora_do_painel": sorted(set(universo) - set(larga.index)),
            "uf_meses_sem_dado": sorted({f"{u}|{c}" for u, c in df.loc[aus, ["uf", "competencia"]].itertuples(index=False)}),
            "uf_meses_atipicos": sorted({f"{u}|{c}" for u, c in df.loc[df["uf_mes_atipico"], ["uf", "competencia"]]
                                        .itertuples(index=False)}),
            "celulas_ausentes": int(aus.sum())}
    return larga.reindex(universo), atip.reindex(universo).fillna(False).astype(bool), info


def ler_sih_residencia(universo: pd.Index) -> tuple[dict, pd.DataFrame, dict]:
    """a15: {K2r: grupo 04, K2r_tot: soma dos grupos 02-05} por município de residência x mês de processamento."""
    import pyarrow.parquet as pq
    man = json.loads(A15_MANIF.read_text(encoding="utf-8"))
    _conferir(A15_PAINEL, man["saidas"]["painel"]["sha256"], "painel SIH por residencia (a15)")
    df = pq.read_table(A15_PAINEL, columns=["co_ibge", "uf", "competencia", "grupo", "aih_aprovadas", "status",
                                            "uf_mes_atipico", "mes_com_falta_em_outra_uf",
                                            "natureza_dos_dados"]).to_pandas()
    if set(df["natureza_dos_dados"].astype(str)) != {NATUREZA}:
        raise FalhaValidacao("a15 com natureza diferente de EMPIRICO")
    if df["competencia"].max() > LIMITE_SIA_SIH or set(MESES_LEITURA) - set(df["competencia"]):
        raise FalhaValidacao("a15: meses fora do limite ou ausentes")
    if set(df["grupo"]) != set(GRUPOS_SIH):
        raise FalhaValidacao(f"a15: grupos {sorted(set(df['grupo']))} diferentes de {GRUPOS_SIH}")
    if df.duplicated(["co_ibge", "competencia", "grupo"]).any():
        raise FalhaValidacao("a15 com chave repetida")
    aus = df["status"].isin(STATUS_A15_AUS)
    if (df["aih_aprovadas"].isna() != aus).any():
        raise FalhaValidacao("a15: aih_aprovadas nula sem status de ausencia (ou o contrario)")
    df["q"] = pd.to_numeric(df["aih_aprovadas"], errors="coerce").astype(float)
    larg = {g: df[df["grupo"] == g].pivot(index="co_ibge", columns="competencia", values="q")
            .reindex(columns=list(MESES_LEITURA)) for g in GRUPOS_SIH}
    tot = larg[GRUPOS_SIH[0]].copy()
    for g in GRUPOS_SIH[1:]:
        tot = tot + larg[g]            # grupo ausente deixa o total ausente
    g4 = df[df["grupo"] == "04"]
    atip = g4.pivot(index="co_ibge", columns="competencia", values="uf_mes_atipico").reindex(columns=list(MESES_LEITURA))
    falta = g4.pivot(index="co_ibge", columns="competencia", values="mes_com_falta_em_outra_uf").reindex(
        columns=list(MESES_LEITURA))
    info = {"municipios_painel": int(larg["04"].shape[0]),
            "municipios_de_U_fora_do_painel": sorted(set(universo) - set(larg["04"].index)),
            "celulas_ausentes": int(aus.sum()),
            "uf_meses_atipicos": sorted({f"{u}|{c}" for u, c in g4.loc[g4["uf_mes_atipico"], ["uf", "competencia"]]
                                        .itertuples(index=False)}),
            "meses_com_falta_em_outra_uf": sorted(set(g4.loc[g4["mes_com_falta_em_outra_uf"], "competencia"])),
            "grupos_somados_em_K2r_tot": list(GRUPOS_SIH)}
    out = {"K2r": larg["04"].reindex(universo), "K2r_tot": tot.reindex(universo)}
    return out, atip.reindex(universo).fillna(False).astype(bool), {**info, "mascara_falta": falta}


def ler_cursos_especificos() -> tuple[list[int], dict[int, list[str]], dict[int, str], dict]:
    """Cursos ESPECIFICO do G4, formas típicas do mapa do G4 (conferidas contra o a17) e conjunto de CBO do a17."""
    g4 = json.loads(G4_RESUMO.read_text(encoding="utf-8"))
    cursos = sorted(int(c) for c in g4["classes_dos_cursos"]["ESPECIFICO"])
    mapa = pd.read_csv(G4_MAPA, dtype={"co_forma": str})
    mapa = mapa[mapa["tipica"].astype(str).str.lower() == "true"]
    tip = {c: sorted(mapa.loc[mapa["cod_curso"] == c, "co_forma"].str.zfill(6)) for c in cursos}
    a17t = pd.read_csv(A17_TIPICAS, dtype={"co_forma": str})
    a17t_d = {c: sorted(a17t.loc[a17t["cod_curso"] == c, "co_forma"].str.zfill(6)) for c in cursos}
    if tip != a17t_d:
        raise FalhaValidacao("formas tipicas do mapa do G4 diferem das do a17")
    cur = pd.read_csv(A17_CURSOS)
    conj = {int(r.cod_curso): str(r.conjunto_cbo) for r in cur.itertuples()}
    if sorted(conj) != cursos or set(cur["natureza_dos_dados"]) != {NATUREZA}:
        raise FalhaValidacao("cursos do a17 diferentes dos cursos ESPECIFICO do G4")
    info = {"cursos": cursos, "formas_tipicas": {str(c): tip[c] for c in cursos},
            "conjunto_cbo": {str(c): conj[c] for c in cursos},
            "cbos": {str(int(r.cod_curso)): str(r.cbos) for r in cur.itertuples()}}
    return cursos, tip, conj, info


def ler_a17(cursos: list[int], tip: dict[int, list[str]], conj: dict[int, str], universo: pd.Index
            ) -> tuple[dict[int, pd.DataFrame], dict]:
    """{curso: município x mês} da quantidade aprovada nas formas típicas do curso (202201-202605).

    `-` do TabNet é zero (zero_tabnet); forma típica que não veio como coluna da consulta é zero daquela consulta
    (regra do a12/a17, conferida em formas_por_consulta); forma que veio como coluna precisa ter linha para todo
    município do formulário (exibirlz); município ausente da resposta ficaria NaN (o a17 não tem nenhum).
    """
    import pyarrow.parquet as pq
    man = json.loads(A17_MANIF.read_text(encoding="utf-8"))
    _conferir(A17_PAINEL, man["saidas"][rotulo(A17_PAINEL)]["sha256"], "painel a17")
    formas = sorted({f for c in cursos for f in tip[c]})
    tab = pq.read_table(A17_PAINEL, columns=["co_ibge", "competencia_processamento", "cod_curso", "forma",
                                             "qtd_aprovada", "status", "natureza_dos_dados"],
                        filters=[("forma", "in", formas), ("competencia_processamento", "in", list(MESES)),
                                 ("cod_curso", "in", cursos)])
    df = tab.to_pandas()
    del tab
    if set(df["natureza_dos_dados"].astype(str).unique()) != {NATUREZA}:
        raise FalhaValidacao("a17 com natureza diferente de EMPIRICO")
    if not set(df["status"].astype(str).unique()) <= set(STATUS_A17_OK) | {K1M.STATUS_SIA_AUSENTE}:
        raise FalhaValidacao("a17 com status fora do vocabulario")
    df["forma"] = df["forma"].astype(str)
    df["co_ibge"] = df["co_ibge"].astype(str)
    df["comp"] = df["competencia_processamento"].astype(str)
    chave_tip = {(c, f) for c in cursos for f in tip[c]}
    df = df[[(c, f) in chave_tip for c, f in zip(df["cod_curso"].astype(int), df["forma"])]]
    pres = pd.read_csv(A17_PRES, dtype={"competencia_processamento": str, "forma": str, "conjunto_cbo": str})
    pres["forma"] = pres["forma"].str.zfill(6)
    pres_ok = set(pres.loc[pres["presente_na_resposta"].astype(str).str.lower() == "true",
                           ["competencia_processamento", "conjunto_cbo", "forma"]].itertuples(index=False, name=None))
    n_mun = int(man["municipios_do_formulario"])
    cont = df.groupby(["cod_curso", "forma", "comp"]).size()
    zeros_coluna = 0
    for c in cursos:
        for f in tip[c]:
            for m in MESES:
                n = int(cont.get((c, f, m), 0))
                if (m, conj[c], f) in pres_ok:
                    if n != n_mun:
                        raise FalhaValidacao(f"a17 curso {c} forma {f} {m}: {n} linhas, esperado {n_mun}")
                elif n:
                    raise FalhaValidacao(f"a17 curso {c} forma {f} {m}: linhas sem a forma presente na consulta")
                else:
                    zeros_coluna += 1
    df["q"] = df["qtd_aprovada"].astype(float).where(df["status"].astype(str) != K1M.STATUS_SIA_AUSENTE)
    df["nan"] = df["q"].isna().astype(np.int64)
    agg = df.groupby(["cod_curso", "co_ibge", "comp"]).agg(q=("q", "sum"), nan=("nan", "sum")).reset_index()
    agg.loc[agg["nan"] > 0, "q"] = np.nan          # forma típica ausente deixa o total do curso ausente
    out = {}
    for c in cursos:
        a = agg[agg["cod_curso"] == c]
        larga = a.pivot(index="co_ibge", columns="comp", values="q").reindex(columns=list(MESES))
        # mês em que nenhuma forma típica veio como coluna: zero daquela consulta para todos os municípios
        for m in MESES:
            if larga[m].isna().all() and not any((m, conj[c], f) in pres_ok for f in tip[c]):
                larga[m] = 0.0
        out[c] = larga.reindex(universo)
    info = {"linhas_lidas": int(len(df)), "municipios_formulario": n_mun,
            "celulas_curso_forma_mes_sem_coluna_zero": zeros_coluna,
            "municipios_de_U_fora_do_a17": sorted(set(universo) - set(agg["co_ibge"])),
            "celulas_ausentes": int(sum(int(v.isna().sum().sum()) for v in out.values())),
            "meses": [MESES[0], MESES[-1]]}
    return out, info


def ler_cir() -> tuple[pd.Series, dict]:
    """Município (6 dígitos) -> região de saúde (CIR) da tabela do TabNet (mesmo leitor do P5, script 29)."""
    linhas = CIR_CNV.read_bytes().decode("latin1").splitlines()
    padrao = re.compile(r"^\s*(\d+)\s+(\d{5})\s+(.*?)\s+(\d{6})\s*$")
    reg, ignorado, outras = [], 0, []
    for ln in linhas[1:]:
        m = padrao.match(ln)
        if m:
            reg.append((m.group(4), m.group(2)))
        elif "Ignorado" in ln:
            ignorado += 1
        elif ln.strip():
            outras.append(ln)
    if outras:
        raise FalhaValidacao(f"linhas da CIR fora do formato esperado: {outras[:3]}")
    cir = pd.DataFrame(reg, columns=["co_ibge", "co_cir"])
    if not cir["co_ibge"].is_unique:
        raise FalhaValidacao("municipio com mais de uma CIR na tabela do TabNet")
    return cir.set_index("co_ibge")["co_cir"], {"codigos": int(len(cir)), "regioes": int(cir["co_cir"].nunique()),
                                                "linhas_ignorado": ignorado}


def ler_pares(base: pd.DataFrame, cursos: list[int]) -> tuple[pd.DataFrame, dict]:
    """Pares município x curso com célula do curso nos ciclos 1 ou 2, em U; chegada por curso (lista nominal)."""
    vc = pd.read_parquet(V_CELULA, columns=["ciclo", "co_ibge", "cod_curso"])
    vc = vc[vc["ciclo"].isin([1, 2]) & vc["cod_curso"].isin(cursos)]
    vc["co_ibge"] = _ibge6(vc["co_ibge"])
    pares = vc.drop_duplicates(["co_ibge", "cod_curso"])[["co_ibge", "cod_curso"]]
    fora_u = sorted(set(pares["co_ibge"]) - set(base.index))
    pares = pares[pares["co_ibge"].isin(base.index)]
    nom = pd.read_csv(NOMINAL, usecols=COLUNAS_NOMINAL, dtype=str)
    if not nom["curso"].str.match(r"^\d{2}\. ").all():
        raise FalhaValidacao("curso da lista nominal fora do formato 'NN. NOME'")
    nom["co_ibge"] = _ibge6(nom["co_ibge"])
    nom["cod_curso"] = nom["curso"].str[:2].astype(int)
    d = pd.to_datetime(nom["dt_inicio_atividade"], format="%Y-%m-%d", errors="coerce")
    sem_data = int(d.isna().sum())
    nom = nom.assign(comp=d.dt.strftime("%Y%m"))[d.notna()]
    if (nom["comp"] >= K1M.LIMITE_CNES).any():
        raise FalhaValidacao("lista nominal com inicio >= 202609")
    nom = nom[nom["cod_curso"].isin(cursos)]
    ch = nom.groupby(["co_ibge", "cod_curso"]).agg(chegada=("comp", "min"), n_especialistas=("comp", "size")
                                                   ).reset_index()
    ch["coorte"] = ch["chegada"].map(D2M.trimestre_inicio)
    m = pares.merge(ch, on=["co_ibge", "cod_curso"], how="left", validate="one_to_one")
    fora = ch.merge(pares, on=["co_ibge", "cod_curso"], how="left", indicator=True)
    fora = fora[fora["_merge"] == "left_only"]
    m = m.sort_values(["cod_curso", "co_ibge"]).reset_index(drop=True)
    info = {"pares": int(len(m)), "pares_tratados": int(m["chegada"].notna().sum()),
            "pares_tratados_ate_fim_serie": int((m["chegada"] <= FIM).sum()),
            "pares_com_chegada_depois_do_fim": int((m["chegada"] > FIM).sum()),
            "municipios_com_celula_fora_de_U": fora_u,
            "pares_da_lista_nominal_sem_celula_do_curso_nos_ciclos_1_2": int(len(fora)),
            "especialistas_nesses_pares": int(fora["n_especialistas"].sum()),
            "linhas_lista_nominal_sem_data": sem_data,
            "por_curso": {str(c): {"pares": int((m["cod_curso"] == c).sum()),
                                   "tratados_ate_fim": int(((m["cod_curso"] == c) & (m["chegada"] <= FIM)).sum()),
                                   "municipios": int(m.loc[m["cod_curso"] == c, "co_ibge"].nunique())}
                          for c in cursos},
            "colunas_lidas_lista_nominal": COLUNAS_NOMINAL}
    return m, info


def ler_fracao_incumbentes(amostra: pd.Index) -> tuple[pd.Series, dict]:
    """12.3c: fração dos médicos ligados (X1, regra D1, ciclos 1-2) com vínculo no município antes do início."""
    x = pd.read_parquet(X1_MEDICOS, columns=["regra_ligacao", "ciclo", "co_ibge", "ligado", "b_mesmo_mun_ultimo_pre",
                                             "natureza_dos_dados"])
    if set(x["natureza_dos_dados"]) != {NATUREZA}:
        raise FalhaValidacao("X1 com natureza diferente de EMPIRICO")
    x = x[(x["regra_ligacao"] == "d1_pos_hoc") & x["ciclo"].isin([1, 2]) & (x["ligado"] == 1)]
    sem = int(x["b_mesmo_mun_ultimo_pre"].isna().sum())
    x = x[x["b_mesmo_mun_ultimo_pre"].notna()].copy()
    x["co_ibge"] = _ibge6(x["co_ibge"])
    fr = x.groupby("co_ibge")["b_mesmo_mun_ultimo_pre"].agg(["mean", "size"])
    info = {"medicos_ligados_ciclos_1_2_regra_d1": int(len(x) + sem), "medicos_sem_competencia_pre_fora": sem,
            "municipios_com_fracao": int(len(fr)),
            "municipios_com_fracao_fora_da_amostra_D2": int(len(set(fr.index) - set(amostra)))}
    return fr["mean"].reindex(amostra), info


# ---------------------------------------------------------------------------
# 4. Estimação por item
# ---------------------------------------------------------------------------

COLUNAS_EST = ["natureza_dos_dados", "estatuto", "item", "desenho", "outcome_id", "descricao_outcome", "versao_fonte",
               "variante", "recorte", "corte", "estatistica", "valor", "ep", "ic95_inf", "ic95_sup", "p_valor", "gl",
               "mde", "media_referencia", "efeito_relativo", "n_unidades", "n_tratados", "n_controles_nunca",
               "n_coortes", "n_clusters", "n_abaixo", "n_acima", "e_min", "e_max", "entra_bky", "q_bky", "status",
               "unidade", "contraste", "nota"]
COLUNAS_EVENTO = ["natureza_dos_dados", "estatuto", "item", "desenho", "outcome_id", "versao_fonte", "variante",
                  "recorte", "e", "theta", "ep", "ep_analitico", "ic95_inf", "ic95_sup", "banda_unif_inf",
                  "banda_unif_sup", "p_valor", "n_coortes", "n_tratados", "referencia", "janela", "unidade", "nota"]
COLUNAS_ATT = ["natureza_dos_dados", "estatuto", "item", "outcome_id", "versao_fonte", "variante", "recorte", "grupo",
               "coorte", "competencia", "e", "n_coorte", "n_tratados", "n_controles", "att", "ep", "nota"]

DESCRICAO = {
    "K_esp": "produção SUS ambulatorial (SIA, a17) do curso, nas formas típicas do G4, executada pelas CBO do curso",
    "K2": "cirurgias SUS hospitalares: AIH aprovadas do grupo 04 por local de internação",
    "K2r": "AIH aprovadas do grupo 04 (cirúrgico) de residentes do município (a15)",
    "K2r_tot": "todas as AIH aprovadas (grupos 02-05) de residentes do município (a15)",
    "K1": "produção SUS ambulatorial executada pelas CBO-alvo (consultas 0301 + exames 02 + cirurgias 04 + OCI 09)",
    "K1_reg": "K1 somado nos outros municípios da região de saúde, por 10 mil hab. da região sem o município",
    "K2_reg": "K2 somado nos outros municípios da região de saúde, por 10 mil hab. da região sem o município",
}


def _linha(**kw) -> dict:
    ln = {c: np.nan for c in COLUNAS_EST}
    ln.update({"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "variante": "principal", "recorte": "",
               "corte": "", "versao_fonte": "", "entra_bky": False, "status": "EXECUTADO", "unidade": UNIDADE,
               "nota": ""})
    ln.update(kw)
    if ln.get("outcome_id") in DESCRICAO and not isinstance(ln.get("descricao_outcome"), str):
        ln["descricao_outcome"] = DESCRICAO[ln["outcome_id"]]
    if ln["status"] == "EXECUTADO" and not np.isfinite(float(ln["valor"])) and ln["estatistica"] != "pretendencia_supt":
        ln["status"] = "SEM_ESTIMATIVA"
        ln["nota"] = K1M._juntar(ln["nota"], "estimativa indefinida")
    return ln


def media_pre_tratados(Y: np.ndarray, G: np.ndarray, meses: list[str], elegivel=None) -> float:
    idx = [i for i, m in enumerate(meses) if m in COMP_PRE]
    trat = G >= 0
    if elegivel is not None:
        trat = trat & elegivel
    if not trat.any():
        return np.nan
    sub = Y[np.ix_(trat, idx)]
    n = np.isfinite(sub).sum(axis=1)
    v = np.nansum(sub, axis=1)[n > 0] / n[n > 0]       # município sem nenhum mês do pré com dado fica fora
    return float(v.mean()) if v.size else np.nan


def linhas_d2(r: dict, meta: dict, *, n_unidades: int, n_trat: int, n_nunca: int, n_coortes: int,
              media_ref: float) -> tuple[list[dict], list[dict], list[dict]]:
    """Linhas do resumo (att_pos_medio, pretendências), do estudo de evento e de ATT(g, t) de uma estimação CS."""
    comum = {**meta, "desenho": meta.get("desenho", "D2"), "n_unidades": n_unidades, "n_tratados": n_trat,
             "n_controles_nunca": n_nunca, "n_coortes": n_coortes, "n_clusters": r["n_clusters"],
             "contraste": meta.get("contraste", CONTRASTE_D2)}
    pos, pt = r["pos"], r["pre"]
    est = [
        _linha(**comum, estatistica="att_pos_medio", valor=pos["att"], ep=pos["ep"], ic95_inf=pos["ic95_inf"],
               ic95_sup=pos["ic95_sup"], p_valor=pos["p_valor"], e_min=pos["e_min"], e_max=pos["e_max"],
               mde=FATOR_MDE * pos["ep"] if np.isfinite(pos["ep"]) else np.nan, media_referencia=media_ref,
               efeito_relativo=pos["att"] / media_ref if np.isfinite(media_ref) and media_ref != 0 else np.nan,
               nota=K1M._juntar(f"media de theta(e) em {pos['n_e']} tempos de evento do pos; media_referencia = "
                                "media do pre 202406-202506 dos tratados", meta.get("nota", ""))),
        _linha(**comum, estatistica="pretendencia_wald", valor=pt["wald"], p_valor=pt["p_wald"], gl=pt["gl"],
               e_min=E_MIN, e_max=-2,
               nota=f"Wald conjunto de theta(e) = 0 em {pt['k']} tempos de evento do pre" if pt["k"] else
               "sem pre estimavel"),
        _linha(**comum, estatistica="pretendencia_supt", valor=np.nan, p_valor=pt["p_supt"], e_min=E_MIN, e_max=-2,
               nota="p do sup-t (bootstrap multiplicador) para theta(e) = 0 em todo o pre"),
    ]
    ev = []
    for rec in r["evento"].to_dict("records"):
        ev.append({**{k: meta.get(k, "") for k in ("item", "outcome_id", "versao_fonte", "variante", "recorte")},
                   "natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "desenho": comum["desenho"],
                   "variante": meta.get("variante", "principal"),
                   **{k: rec.get(k) for k in ("e", "theta", "ep", "ep_analitico", "ic95_inf", "ic95_sup",
                                              "banda_unif_inf", "banda_unif_sup", "p_valor", "n_coortes",
                                              "n_tratados", "referencia", "nota")},
                   "janela": "base" if rec["e"] == -1 else ("pre" if rec["e"] < -1 else "pos"), "unidade": UNIDADE})
    att = []
    for rec in r["att_gt"].to_dict("records"):
        att.append({"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO,
                    **{k: meta.get(k, "") for k in ("item", "outcome_id", "versao_fonte", "recorte")},
                    "variante": meta.get("variante", "principal"), "grupo": rec["grupo"], "coorte": meta["_meses"][rec["gi"]], "competencia": meta["_meses"][rec["t"]],
                    **{k: rec[k] for k in ("e", "n_coorte", "n_tratados", "n_controles", "att", "ep", "nota")}})
    for ln in est:
        ln.pop("_meses", None)
    return est, ev, att


def serie_taxa(num: pd.DataFrame, pop: pd.Series, amostra: pd.Index) -> np.ndarray:
    R = num.reindex(amostra).div(pop.reindex(amostra), axis=0) * K1M.ESCALA_HAB
    return R.reindex(columns=list(MESES)).to_numpy(dtype=float)


def d2_municipio(num: pd.DataFrame, D, amostra: pd.Index, chegadas: pd.DataFrame, meta: dict, *,
                 controles: str = "ainda_nao", elegivel=None, Y: np.ndarray | None = None) -> tuple:
    pop = D.base["populacao_2022"].astype(float)
    if Y is None:
        Y = serie_taxa(num, pop, amostra)
    G, coortes = D2M.indices_coorte(chegadas, list(MESES))
    if elegivel is not None:
        coortes = sorted({int(g) for g in G[(G >= 0) & elegivel]})
    r = estimar_cs_cluster(Y, G, [(None, g) for g in coortes], amostra.to_numpy(), elegivel=elegivel,
                           controles=controles)
    trat = np.isin(G, coortes) & (elegivel if elegivel is not None else True)
    est, ev, att = linhas_d2(r, {**meta, "_meses": list(MESES)}, n_unidades=len(G), n_trat=int(trat.sum()),
                             n_nunca=int((G < 0).sum()), n_coortes=len(coortes),
                             media_ref=media_pre_tratados(Y, G, list(MESES), elegivel))
    return est, ev, att, r, G


def d1_linhas(num: pd.DataFrame, D, meta: dict, atip: pd.DataFrame | None = None) -> tuple[list[dict], dict]:
    """DiRD de K2 (ou K2r) como no D1: principal, média completa, pós até 202607 e sem UF-mês atípico; U."""
    base_u = D.base
    pop, s_mil = base_u["populacao_2022"].astype(float), base_u["s_mil"].astype(float)
    num = num.reindex(base_u.index)
    d = K1M.base_janelas(num, None, pop, s_mil, POS_K2)
    dc = K1M.base_janelas(num, None, pop, s_mil, POS_K2, completo=True)
    da = K1M.base_janelas(num, None, pop, s_mil, POS_ATE)
    dm = K1M.base_janelas(num.mask(atip.reindex(base_u.index).to_numpy()), None, pop, s_mil, POS_K2) \
        if atip is not None else None
    linhas, guarda = [], {}
    for corte in (*K1M.CORTES, K1M.EMPILHADO):
        rot = K1M.ROTULO_CORTE[corte]
        media = K1M.media_abaixo(d, corte)
        for var, dd, jan in (("principal", d, POS_K2), ("media_completa", dc, POS_K2),
                             ("pos_ate_202607", da, POS_ATE), ("sem_uf_mes_atipico", dm, POS_K2)):
            if dd is None:
                continue
            r = E7.rd_delta(dd, "y_pos", "y_pre", corte)
            ep = r.get("ep", np.nan)
            ln = _linha(**meta, desenho="D1", corte=rot, variante=var, estatistica="salto_dird", valor=r.get("tau"),
                        ep=ep, ic95_inf=r.get("ic95_inf"), ic95_sup=r.get("ic95_sup"), p_valor=r.get("p_valor"),
                        n_abaixo=r.get("n_abaixo"), n_acima=r.get("n_acima"), n_clusters=r.get("n_clusters"),
                        n_unidades=int(np.isfinite(dd["delta_principal"].to_numpy(dtype=float)).sum()),
                        mde=FATOR_MDE * ep if ep is not None and np.isfinite(ep) else np.nan, media_referencia=media,
                        efeito_relativo=(r.get("tau") / media) if np.isfinite(media) and media != 0 else np.nan,
                        contraste=CONTRASTE_D1,
                        nota=K1M._juntar(f"pre {COMP_PRE[0]}-{COMP_PRE[-1]}, pos {jan[0]}-{jan[-1]}; h = 0,050; "
                                         "media_referencia = media do pre abaixo do corte", r.get("nota", "")))
            linhas.append(ln)
            guarda[(rot, var)] = ln
    return linhas, guarda


def serie_regional(num: pd.DataFrame, pop: pd.Series, cir: pd.Series, amostra: pd.Index) -> tuple[np.ndarray, dict]:
    """Y_reg(m, t) = soma das contagens dos outros municípios da região / soma da população deles x 1e4.

    Só municípios de U (com população) entram; qualquer município da região sem dado no mês deixa o valor
    ausente (nunca zero); região sem outro município deixa o município sem outcome."""
    reg = cir.reindex(num.index)
    sem_cir = sorted(num.index[reg.isna()])
    df = num.reindex(columns=list(MESES))
    soma = df.groupby(reg).sum(min_count=1)
    nan_reg = df.isna().groupby(reg).sum()
    pop_reg = pop.reindex(num.index).groupby(reg).sum()
    n_reg = reg.groupby(reg).size()
    out = np.full((len(amostra), len(MESES)), np.nan)
    sozinhos, sem_reg = [], []
    for i, m in enumerate(amostra):
        r = reg.get(m)
        if not isinstance(r, str):
            sem_reg.append(m)
            continue
        if n_reg[r] <= 1:
            sozinhos.append(m)
            continue
        own = df.loc[m].to_numpy(dtype=float)
        nan_outros = nan_reg.loc[r].to_numpy() - np.isnan(own).astype(int)
        s = soma.loc[r].to_numpy(dtype=float) - np.nan_to_num(own)
        p = float(pop_reg[r] - pop[m])
        v = s / p * K1M.ESCALA_HAB
        v[nan_outros > 0] = np.nan
        out[i] = v
    info = {"municipios_de_U_sem_cir": sem_cir, "municipios_da_amostra_sem_cir": sem_reg,
            "municipios_da_amostra_sozinhos_na_regiao": sozinhos,
            "celulas_ausentes_na_amostra": int(np.isnan(out).sum())}
    return out, info


# ---------------------------------------------------------------------------
# 5. Figuras (sem texto embutido: o "Como ler" está no doc e no resumo)
# ---------------------------------------------------------------------------

COMO_LER = {
    "K_X_12_2_evento.png": "Cada ponto compara, mês a mês desde a chegada, a produção típica da especialidade nos "
                           "pares município × curso que receberam o especialista com a dos pares que ofereceram a vaga "
                           "e ainda não tinham recebido; à esquerda do zero os pontos deveriam ficar perto de zero.",
    "K_X_12_2_cursos.png": "Cada linha é um curso: o ponto é a diferença média depois da chegada e o traço é o "
                           "intervalo de 95%; traço que cruza a linha vertical do zero não distingue a diferença de "
                           "zero.",
    "K_X_12_4_residentes.png": "Mês a mês desde a chegada, a diferença nas internações de residentes (cirúrgicas à "
                               "esquerda, todas à direita) entre municípios que receberam o especialista e os "
                               "comparáveis; mede uso pelos moradores, não oferta local.",
    "K_X_12_1_versoes.png": "Cada par de pontos é a mesma estimativa de K2 com a versão antiga (v1) e a revisada (v2) "
                            "do SIH; pontos próximos indicam que a revisão da fonte não muda a conclusão.",
    "K_X_12_3_controles.png": "Cada linha é uma forma diferente de comparar os municípios que receberam especialista "
                              "com os que não receberam, para a produção K1; se as linhas concordam, o resultado não "
                              "depende da escolha do grupo de comparação.",
    "K_X_12_5_regiao.png": "Mês a mês desde a chegada, a diferença na produção dos outros municípios da mesma região "
                           "de saúde; o sinal é uma pista e não separa expansão líquida de deslocamento.",
}
DESCRICAO_FIGURAS = {
    "K_X_12_2_evento.png": "12.2: estudo de evento agregado entre os cursos específicos",
    "K_X_12_2_cursos.png": "12.2: ATT médio do pós por curso e agregado",
    "K_X_12_4_residentes.png": "12.4: estudo de evento de K2r e K2r_tot (D2)",
    "K_X_12_1_versoes.png": "12.1: K2 com a safra v1 e a v2 do SIH, D1 empilhado e D2",
    "K_X_12_3_controles.png": "12.3: K1 sob controles alternativos, DiD sintético e tercis de incumbência",
    "K_X_12_5_regiao.png": "12.5: estudo de evento de K1_reg e K2_reg (D2)",
}


def _eixo(ax):
    S = K1M
    ax.set_facecolor(S.SUPERFICIE)
    ax.grid(alpha=0.25, linewidth=0.6)
    ax.tick_params(colors=S.TINTA_2, labelsize=8)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    import matplotlib
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",").replace("-", "−")))


def _evento(ax, ev: pd.DataFrame, rotulo_y: str):
    S = K1M
    e = ev.sort_values("e")
    x = e["e"].to_numpy()
    th = e["theta"].to_numpy(dtype=float)
    lo, hi = e["ic95_inf"].to_numpy(dtype=float), e["ic95_sup"].to_numpy(dtype=float)
    ylo, yhi, cortado = D2M.limites_eixo(th, lo, hi)
    ok = np.isfinite(lo) & np.isfinite(hi)
    if np.isfinite(th).any():
        ax.axvspan(-0.5, x[np.isfinite(th)].max() + 0.5, color=D2M.COR_POS_D2, linewidth=0, zorder=0)
    ax.axhline(0, color=S.TINTA_2, linewidth=0.9)
    lo_c, hi_c = np.clip(lo, ylo, yhi), np.clip(hi, ylo, yhi)
    ax.errorbar(x[ok], th[ok], yerr=[th[ok] - lo_c[ok], hi_c[ok] - th[ok]], fmt="none", ecolor=S.COR_IC,
                elinewidth=1.2, alpha=0.7, zorder=2)
    ref = e["referencia"].astype(bool).to_numpy()
    ax.plot(x[~ref], th[~ref], "o", color=S.COR_PONTO, markersize=4, zorder=3)
    ax.plot(x[ref], th[ref], "s", color=S.TINTA, markersize=6, zorder=4)
    ax.set_ylim(ylo, yhi)
    ax.set_xlabel("meses desde o início do trimestre de chegada", fontsize=9, color=S.TINTA_2)
    ax.set_ylabel(rotulo_y, fontsize=9, color=S.TINTA_2)
    _eixo(ax)
    return cortado


def _forest(ax, rotulos: list[str], vals, los, his, cores=None):
    S = K1M
    y = np.arange(len(rotulos))[::-1]
    vals, los, his = (np.asarray(v, dtype=float) for v in (vals, los, his))
    cores = cores or [S.COR_PONTO] * len(rotulos)
    ax.axvline(0, color=S.TINTA_2, linewidth=0.9)
    for yi, v, a, b, c in zip(y, vals, los, his, cores):
        if np.isfinite(a) and np.isfinite(b):
            ax.plot([a, b], [yi, yi], color=c, linewidth=1.4, alpha=0.8)
        if np.isfinite(v):
            ax.plot([v], [yi], "o", color=c, markersize=5)
    ax.set_yticks(y)
    ax.set_yticklabels(rotulos, fontsize=8)
    _eixo(ax)
    import matplotlib
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",").replace("-", "−")))
    ax.yaxis.set_major_formatter(matplotlib.ticker.FixedFormatter(rotulos))


AVISO_CORTE = " O eixo vertical foi limitado: intervalos que o ultrapassam aparecem cortados na borda."


def _salvar(fig, caminho: Path, cortado: bool = False) -> dict:
    fig.savefig(caminho, dpi=120, facecolor=K1M.SUPERFICIE, metadata={"Software": None})
    import matplotlib.pyplot as plt
    plt.close(fig)
    return {"arquivo": rotulo(caminho), "descricao": DESCRICAO_FIGURAS[caminho.name],
            "como_ler": COMO_LER[caminho.name] + (AVISO_CORTE if cortado else ""), "eixo_cortado": bool(cortado),
            "sha256": sha256(caminho)}


def gerar_figuras(est: pd.DataFrame, ev: pd.DataFrame, dir_fig: Path) -> list[dict]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    S = K1M
    dir_fig.mkdir(parents=True, exist_ok=True)
    for antigo in dir_fig.glob("*.png"):
        antigo.unlink()
    figs = []

    def sel_ev(**f):
        m = np.ones(len(ev), dtype=bool)
        for k, v in f.items():
            m &= (ev[k].astype(str) == str(v)).to_numpy()
        return ev[m]

    def sel_est(**f):
        m = np.ones(len(est), dtype=bool)
        for k, v in f.items():
            m &= (est[k].astype(str) == str(v)).to_numpy()
        return est[m]

    fig, ax = plt.subplots(figsize=(9, 4.2), facecolor=S.SUPERFICIE)
    cort = _evento(ax, sel_ev(item="12.2", recorte=TODOS, variante="principal"), "diferença na mudança desde o mês −1,\n"
                   "por 10 mil hab. por mês")
    fig.tight_layout()
    figs.append(_salvar(fig, dir_fig / "K_X_12_2_evento.png", cort))

    s = sel_est(item="12.2", estatistica="att_pos_medio", variante="principal")
    ordem = [TODOS] + [r for r in s["recorte"] if r != TODOS]
    s = s.set_index("recorte").loc[ordem]
    rot = ["todos os cursos (peso = pares tratados)"] + [f"curso {r.split('_')[1]}" for r in ordem[1:]]
    fig, ax = plt.subplots(figsize=(8, 0.42 * len(rot) + 1.2), facecolor=S.SUPERFICIE)
    _forest(ax, rot, s["valor"], s["ic95_inf"], s["ic95_sup"], [S.TINTA] + [S.COR_PONTO] * (len(rot) - 1))
    ax.set_xlabel("ATT médio depois da chegada, por 10 mil hab. por mês", fontsize=9, color=S.TINTA_2)
    fig.tight_layout()
    figs.append(_salvar(fig, dir_fig / "K_X_12_2_cursos.png"))

    fig, axs = plt.subplots(1, 2, figsize=(12, 4.2), facecolor=S.SUPERFICIE)
    cort = False
    for ax, oid in zip(axs, ("K2r", "K2r_tot")):
        cort |= _evento(ax, sel_ev(item="12.4", outcome_id=oid, variante="principal"), f"{oid}: diferença desde o mês −1,\n"
                        "por 10 mil hab. por mês")
    fig.tight_layout()
    figs.append(_salvar(fig, dir_fig / "K_X_12_4_residentes.png", cort))

    linhas = []
    for desenho, est_nome, corte in (("D1", "salto_dird", "empilhado"), ("D2", "att_pos_medio", "")):
        for v in ("a13_v1", "a13b_v2"):
            r = sel_est(item="12.1", outcome_id="K2", desenho=desenho, versao_fonte=v, estatistica=est_nome,
                        variante="principal", corte=corte)
            if len(r) == 1:
                linhas.append((f"{desenho} ({'empilhado' if desenho == 'D1' else 'chegada'}), {v}", r.iloc[0]))
    fig, ax = plt.subplots(figsize=(8, 2.6), facecolor=S.SUPERFICIE)
    _forest(ax, [a for a, _ in linhas], [b["valor"] for _, b in linhas], [b["ic95_inf"] for _, b in linhas],
            [b["ic95_sup"] for _, b in linhas],
            [S.COR_PONTO if "v1" in a else S.COR_ATO for a, _ in linhas])
    ax.set_xlabel("K2: estimativa, AIH cirúrgicas por 10 mil hab. por mês", fontsize=9, color=S.TINTA_2)
    fig.tight_layout()
    figs.append(_salvar(fig, dir_fig / "K_X_12_1_versoes.png"))

    linhas = []
    for rotl, f in (("D2 do doc 50 (ainda não tratados)", dict(item="12.3", recorte="D2_doc50")),
                    ("(a) só nunca tratados", dict(item="12.3", recorte="a_nunca_tratados")),
                    ("(b) DiD sintético, agregado", dict(item="12.3", recorte="b_sdid_agregado")),
                    ("(c) tercil 1 de incumbência", dict(item="12.3", recorte="c_tercil_1")),
                    ("(c) tercil 2 de incumbência", dict(item="12.3", recorte="c_tercil_2")),
                    ("(c) tercil 3 de incumbência", dict(item="12.3", recorte="c_tercil_3"))):
        r = sel_est(**f)
        r = r[r["estatistica"].isin(["att_pos_medio", "att_sdid"])]
        if len(r) == 1:
            linhas.append((rotl, r.iloc[0]))
    fig, ax = plt.subplots(figsize=(8, 0.45 * len(linhas) + 1.2), facecolor=S.SUPERFICIE)
    _forest(ax, [a for a, _ in linhas], [b["valor"] for _, b in linhas], [b["ic95_inf"] for _, b in linhas],
            [b["ic95_sup"] for _, b in linhas])
    ax.set_xlabel("K1: diferença depois da chegada, por 10 mil hab. por mês", fontsize=9, color=S.TINTA_2)
    fig.tight_layout()
    figs.append(_salvar(fig, dir_fig / "K_X_12_3_controles.png"))

    fig, axs = plt.subplots(1, 2, figsize=(12, 4.2), facecolor=S.SUPERFICIE)
    cort = False
    for ax, oid in zip(axs, ("K1_reg", "K2_reg")):
        cort |= _evento(ax, sel_ev(item="12.5", outcome_id=oid, variante="principal"), f"{oid}: diferença desde o mês −1,\n"
                        "por 10 mil hab. da região por mês")
    fig.tight_layout()
    figs.append(_salvar(fig, dir_fig / "K_X_12_5_regiao.png", cort))
    return figs


# ---------------------------------------------------------------------------
# 6. Doc 57c (gerado inteiro a partir das saídas; nenhum número digitado)
# ---------------------------------------------------------------------------

_n, _p, _fi = E7._n, E7._p, E7._fmt_int


def _esc(t) -> str:
    return str(t).replace("|", "\\|")


def _tabela(cab: list[str], linhas: list[list[str]]) -> str:
    out = ["| " + " | ".join(cab) + " |", "|" + "|".join("---" for _ in cab) + "|"]
    out += ["| " + " | ".join(_esc(c) for c in ln) + " |" for ln in linhas]
    return "\n".join(out)


def _ic(r) -> str:
    return f"[{_n(r['ic95_inf'], 2)}; {_n(r['ic95_sup'], 2)}]"


def _sel(est: pd.DataFrame, **f) -> pd.DataFrame:
    m = np.ones(len(est), dtype=bool)
    for k, v in f.items():
        m &= (est[k].fillna("").astype(str) == str(v)).to_numpy()
    return est[m]


def _um(est, **f):
    s = _sel(est, **f)
    return s.iloc[0].to_dict() if len(s) == 1 else None


def classificar(r) -> str:
    if r is None or not np.isfinite(float(r["ic95_inf"])):
        return "sem estimativa"
    if float(r["ic95_inf"]) > 0:
        return "acima de zero"
    if float(r["ic95_sup"]) < 0:
        return "abaixo de zero"
    return "inclui zero"


def _pre_txt(est, **f) -> str:
    w = _um(est, **f, estatistica="pretendencia_wald")
    if w is None or not np.isfinite(float(w["p_valor"])):
        return "—"
    return f"{_p(w['p_valor'])} ({'compatível com plano' if w['p_valor'] >= 0.05 else 'não plano'})"


def theta_pre(ev: pd.DataFrame, r: dict) -> tuple[float, float]:
    """θ médio do pré (e de −24 a −2) e dos 12 meses antes do mês-base (−13 a −2) da estimação da linha `r`
    (mesma regra do doc 50 e da auditoria 21)."""
    m = ((ev["item"] == r["item"]) & (ev["outcome_id"] == r["outcome_id"]) & (ev["desenho"] == r["desenho"])
         & (ev["recorte"] == r["recorte"]) & (ev["versao_fonte"] == r["versao_fonte"])
         & (ev["variante"] == r["variante"]))
    th = ev[m].set_index("e")["theta"].astype(float)
    th = th[np.isfinite(th)]
    a, b = th[th.index <= -2], th[(th.index <= -2) & (th.index >= -13)]
    return (float(a.mean()) if len(a) else np.nan, float(b.mean()) if len(b) else np.nan)


def classe_pre(valor: float, mp: float, mp12: float) -> str:
    """'parecido': o θ médio do pré (inteiro ou dos 12 meses antes do mês-base) tem o sinal e pelo menos metade do
    tamanho do ATT do pós; 'oposto': sinal contrário e pelo menos metade (só o pré inteiro, como no doc 50)."""
    if not np.isfinite(valor) or valor == 0:
        return "neutro"

    def mesmo(m):
        return np.isfinite(m) and np.sign(m) == np.sign(valor) and abs(m) >= 0.5 * abs(valor)
    if mesmo(mp) or mesmo(mp12):
        return "parecido"
    if np.isfinite(mp) and np.sign(mp) == -np.sign(valor) and abs(mp) >= 0.5 * abs(valor):
        return "oposto"
    return "neutro"


def tabela_d2(est: pd.DataFrame, ev: pd.DataFrame, filtros: list[tuple[str, dict]]) -> str:
    linhas = []
    for rot, f in filtros:
        r = _um(est, **f, estatistica="att_pos_medio")
        if r is None:
            continue
        mp, mp12 = theta_pre(ev, r)
        linhas.append([rot, f"{_fi(r['n_tratados'])} / {_fi(r['n_controles_nunca'])}", _fi(r["n_coortes"]),
                       _n(r["valor"], 2), _ic(r), _p(r["p_valor"]), _n(r["mde"], 2, sinal=False),
                       _n(r["media_referencia"], 2, sinal=False), _pre_txt(est, **f),
                       _p(_um(est, **f, estatistica="pretendencia_supt")["p_valor"]),
                       f"{_n(mp, 2)} / {_n(mp12, 2)}"])
    return _tabela(["Linha", "Tratados / não tratados no horizonte", "Coortes", "ATT médio do pós", "IC 95%", "p",
                    "MDE (2,8 × EP)", "Média do pré dos tratados", "Pré: p do Wald", "Pré: p sup-t",
                    "θ médio do pré (−24 a −2 / −13 a −2)"], linhas)


def tabela_d1(est: pd.DataFrame, item: str, oids: list[str], versao: str = "") -> str:
    linhas = []
    for oid in oids:
        for var in ("principal", "media_completa", "pos_ate_202607", "sem_uf_mes_atipico"):
            for corte in ("0.300", "0.400", "empilhado"):
                f = dict(item=item, outcome_id=oid, desenho="D1", variante=var, corte=corte)
                if versao:
                    f["versao_fonte"] = versao
                r = _um(est, **f)
                if r is None:
                    continue
                linhas.append([oid, var, corte.replace(".", ","), _n(r["valor"], 2), _ic(r), _p(r["p_valor"]),
                               f"{_fi(r['n_abaixo'])} / {_fi(r['n_acima'])}", _n(r["mde"], 2, sinal=False),
                               _n(r["efeito_relativo"], 1, pp=True) + " %" if np.isfinite(float(r["efeito_relativo"]))
                               else "—"])
    return _tabela(["Outcome", "Variante", "Corte", "Salto na mudança (DiRD)", "IC 95%", "p", "n abaixo / acima",
                    "MDE", "Relativo à média do pré abaixo"], linhas)


def tabela_bky(est: pd.DataFrame) -> str:
    s = est[est["entra_bky"].astype(bool)]
    linhas = [[r["item"], r["outcome_id"], r["desenho"], r["recorte"] or "—", r["corte"] or "—", _n(r["valor"], 2),
               _ic(r), _p(r["p_valor"]), _p(r["q_bky"])] for r in s.to_dict("records")]
    return _tabela(["Item", "Outcome", "Desenho", "Recorte", "Corte", "Estimativa", "IC 95%", "p", "q (BKY)"], linhas)


def tabela_amostras(resumo: dict) -> str:
    a = resumo["amostras"]
    p = a["12.2_pares"]
    linhas = [["12.2: pares município × curso (cursos específicos, ciclos 1–2, em U)", _fi(p["pares"])],
              ["12.2: pares com chegada até 2026-05", _fi(p["pares_tratados_ate_fim_serie"])],
              ["12.2: pares com 1ª chegada depois de 2026-05 (ainda não tratados no horizonte)",
               _fi(p["pares_com_chegada_depois_do_fim"])],
              ["12.2: pares da lista nominal sem célula do curso nos ciclos 1–2 (fora)",
               _fi(p["pares_da_lista_nominal_sem_celula_do_curso_nos_ciclos_1_2"])],
              ["D2 municipal (12.1, 12.3, 12.4, 12.5): municípios da amostra", _fi(a["d2"]["n_municipios"])],
              ["D2 municipal: tratados até 2026-05 / sem chegada no horizonte",
               f"{_fi(a['d2']['n_tratados_horizonte'])} / {_fi(a['d2']['n_nao_tratados_horizonte'])}"],
              ["12.3a e 12.3b: chegadas depois de 2026-05 retiradas (célula não ficou vazia)",
               _fi(a["12.3"]["retirados_chegada_depois_do_fim"])],
              ["12.3b: unidades sem série completa de K1 (fora do DiD sintético)",
               _fi(a["12.3"]["sdid_sem_serie_completa"])],
              ["12.3c: tratados com fração de incumbência / sem (fora dos tercis)",
               f"{_fi(a['12.3']['tratados_com_fracao'])} / {_fi(a['12.3']['tratados_sem_fracao'])}"],
              ["12.5: municípios da amostra sozinhos na região de saúde (sem outcome)",
               _fi(len(a["12.5"]["municipios_da_amostra_sozinhos_na_regiao"]))],
              ["12.5: municípios da amostra sem região de saúde na tabela do TabNet",
               _fi(len(a["12.5"]["municipios_da_amostra_sem_cir"]))]]
    for c, v in p["por_curso"].items():
        linhas.append([f"12.2: curso {c}: pares / tratados até 2026-05", f"{v['pares']} / {v['tratados_ate_fim']}"])
    return _tabela(["Item", "Valor"], linhas)


def _rotulo_linha(r: dict) -> str:
    rec, it = r["recorte"], r["item"]
    if it == "12.2":
        return "12.2, " + ("todos os cursos (ATT agregado)" if rec == TODOS else rec.replace("curso_", "curso "))
    if it == "12.3":
        return {"D2_doc50": "12.3, D2 do doc 50", "a_nunca_tratados": "12.3a, só nunca tratados"}.get(
            rec, "12.3c, " + rec.replace("c_tercil_", "tercil "))
    if it == "12.1":
        return f"12.1, K2 ({r['versao_fonte']})"
    return f"{it}, {r['outcome_id']} (D2)"


def alertas_pre(est: pd.DataFrame, ev: pd.DataFrame) -> str:
    """Toda estimação D2 principal cujo IC exclui zero é lida junto com o pré: pré não plano (Wald), diferença que já
    aparecia antes da chegada ou pré de sinal oposto (convenção do doc 50 e da auditoria 21)."""
    nao_plano, parecido, oposto, limpos, n_supt = [], [], [], [], 0
    todas = est[(est["estatistica"] == "att_pos_medio") & (est["variante"] == "principal")
                & (est["status"] == "EXECUTADO")]
    for r in todas.to_dict("records"):
        if classificar(r) not in ("acima de zero", "abaixo de zero"):
            continue
        f = {k: r[k] for k in ("item", "outcome_id", "desenho", "versao_fonte", "recorte", "variante")}
        w = _um(est, **f, estatistica="pretendencia_wald")
        st = _um(est, **f, estatistica="pretendencia_supt")
        mp, mp12 = theta_pre(ev, r)
        rot = f"{_rotulo_linha(r)}: ATT {_n(r['valor'], 2)}, IC 95% {_ic(r)}"
        if w is not None and np.isfinite(float(w["p_valor"])) and float(w["p_valor"]) < 0.05:
            n_supt += int(float(st["p_valor"]) < 0.05)
            nao_plano.append(f"{rot}; Wald do pré p = {_p(w['p_valor'])}, sup-t p = {_p(st['p_valor'])}")
            continue
        cl = classe_pre(float(r["valor"]), mp, mp12)
        if cl == "parecido":
            parecido.append(f"{rot}; θ médio do pré {_n(mp, 2)} (−13 a −2: {_n(mp12, 2)})")
        elif cl == "oposto":
            oposto.append(f"{rot}; θ médio do pré {_n(mp, 2)}")
        else:
            limpos.append(_rotulo_linha(r))
    txt = ""
    if nao_plano:
        txt += (" Pré não plano (Wald p < 0,05), então a diferença é só uma associação e não se lê como mudança causada "
                "pela chegada: " + "; ".join(nao_plano) + ". O sup-t, menos potente contra tendências suaves, "
                + ("não rejeita em nenhuma delas" if n_supt == 0 else f"rejeita em {n_supt} delas")
                + "; vale o Wald, que é a regra do doc 50, e a ressalva fica.")
    if parecido:
        txt += (" Pré compatível com plano pelo Wald, mas com o θ médio do pré de mesmo sinal e pelo menos metade do "
                "ATT do pós (boa parte da diferença já aparecia antes da chegada, em relação ao mês-base): "
                + "; ".join(parecido) + ".")
    if oposto:
        txt += (" θ médio do pré com sinal oposto ao do ATT e pelo menos metade do tamanho (o ATT depende do mês-base): "
                + "; ".join(oposto) + ".")
    if limpos:
        txt += (" Sem ressalva do pré, mas ainda ATT sob tendências paralelas, sem exogeneidade validada: "
                + "; ".join(limpos) + ".")
    n_ic = len(nao_plano) + len(parecido) + len(oposto) + len(limpos)
    return txt + (f" São {n_ic} ATT principais com IC fora de zero entre {len(todas)} estimações D2 principais, sem "
                  "correção para múltiplos testes fora das 8 linhas do BKY." if n_ic else "")


def leitura(est: pd.DataFrame, ev: pd.DataFrame) -> str:
    def frase(rot, r, pre_f):
        if r is None:
            return f"{rot}: sem estimativa"
        c = classificar(r)
        pre = _um(est, **pre_f, estatistica="pretendencia_wald")
        plano = pre is not None and np.isfinite(float(pre["p_valor"])) and pre["p_valor"] >= 0.05
        txt = f"{rot}: {_n(r['valor'], 2)} (IC 95% {_ic(r)}; o intervalo {c})"
        if pre is not None and not plano:
            txt += "; o pré não é plano, então é só uma associação"
        return txt

    partes = []
    f22 = dict(item="12.2", recorte=TODOS, variante="principal")
    partes.append(frase("12.2, produção típica da especialidade no par que recebeu o especialista (ATT agregado)",
                        _um(est, **f22, estatistica="att_pos_medio"), f22))
    for oid, nome in (("K2r", "12.4, internações cirúrgicas de residentes"), ("K2r_tot", "12.4, todas as internações "
                                                                                       "de residentes")):
        f = dict(item="12.4", outcome_id=oid, desenho="D2", variante="principal")
        partes.append(frase(f"{nome} (D2)", _um(est, **f, estatistica="att_pos_medio"), f))
        r1 = _um(est, item="12.4", outcome_id=oid, desenho="D1", variante="principal", corte="empilhado")
        if r1 is not None:
            partes.append(f"{nome} (D1, empilhado): {_n(r1['valor'], 2)} (IC 95% {_ic(r1)}; o intervalo "
                          f"{classificar(r1)})")
    for oid, nome in (("K1_reg", "12.5, produção K1 nos outros municípios da região"),
                      ("K2_reg", "12.5, cirurgias K2 nos outros municípios da região")):
        f = dict(item="12.5", outcome_id=oid, variante="principal")
        partes.append(frase(nome, _um(est, **f, estatistica="att_pos_medio"), f))
    texto = "; ".join(partes) + "." + alertas_pre(est, ev)
    r_k1 = _um(est, item="12.3", recorte="D2_doc50", estatistica="att_pos_medio")
    r_reg = _um(est, item="12.5", outcome_id="K1_reg", variante="principal", estatistica="att_pos_medio")
    w_reg = _um(est, item="12.5", outcome_id="K1_reg", variante="principal", estatistica="pretendencia_wald")
    c_k1, c_reg = classificar(r_k1), classificar(r_reg)
    pre_reg = ("o pré não é plano" if w_reg is not None and float(w_reg["p_valor"]) < 0.05
               else "o pré é compatível com plano")
    texto += (f" Expansão líquida e deslocamento não ficam separados: K1 no município (D2 do doc 50): o intervalo "
              f"{c_k1}; K1 nos outros municípios da região: o intervalo {c_reg} e {pre_reg}. A leitura do protocolo "
              "(negativo nos vizinhos = deslocamento de produção; positivo = atendimento de referência) vale só como "
              "hipótese: sem exogeneidade validada, o sinal nos vizinhos também pode ser tendência regional comum, e "
              "pacientes que migram de município não são observados na produção por município de execução (os "
              "residentes do 12.4 olham só as internações).")
    sig = est[est["entra_bky"].astype(bool) & (est["q_bky"] < 0.05)]
    texto += (f" Depois do BKY do adendo, {len(sig)} de {int(est['entra_bky'].astype(bool).sum())} linhas têm q < 0,05"
              + (f" ({', '.join(f'{a} {b}' for a, b in zip(sig['item'], sig['outcome_id']))})" if len(sig) else "")
              + ". Tudo isso é ATT sob tendências paralelas (ou, no D1, o incentivo marginal dentro do pacote dos "
              "cortes), relatado depois de vistos os resultados do doc 50.")
    return texto


def gerar_doc(est: pd.DataFrame, ev: pd.DataFrame, resumo: dict) -> str:
    figs = {Path(f["arquivo"]).name: f for f in resumo["figuras"]}

    def fig(nome):
        f = figs[nome]
        return (f"![{f['descricao']}](../../{f['arquivo']})\n\n**Como ler.** {f['como_ler']}")

    cursos = resumo["amostras"]["cursos_especificos"]["cursos"]
    f22 = [("todos os cursos (peso = pares tratados)", dict(item="12.2", recorte=TODOS, variante="principal"))] + \
          [(f"curso {c}", dict(item="12.2", recorte=f"curso_{c}", variante="principal")) for c in cursos]
    f24 = [(f"{o} (D2)", dict(item="12.4", outcome_id=o, desenho="D2", variante="principal"))
           for o in ("K2r", "K2r_tot")]
    f21 = [(f"K2, {v} (D2)", dict(item="12.1", outcome_id="K2", desenho="D2", versao_fonte=v, variante="principal"))
           for v in ("a13_v1", "a13b_v2")]
    f23 = [("D2 do doc 50 (controles ainda não tratados, recalculado)", dict(item="12.3", recorte="D2_doc50")),
           ("(a) controles só nunca tratados (células que ficaram vazias)", dict(item="12.3", recorte="a_nunca_tratados"))]
    f23c = [(f"(c) tercil {k}", dict(item="12.3", recorte=f"c_tercil_{k}")) for k in (1, 2, 3)]
    f25 = [(o, dict(item="12.5", outcome_id=o, variante="principal")) for o in ("K1_reg", "K2_reg")]
    sd = [r for r in est.to_dict("records") if r["item"] == "12.3" and r["estatistica"] == "att_sdid"]
    t_sd = _tabela(["Recorte", "Tratados", "Controles (nunca tratados)", "ATT (DiD sintético)", "IC 95% (bootstrap)", "p"],
                   [[r["recorte"], _fi(r["n_tratados"]), _fi(r["n_controles_nunca"]), _n(r["valor"], 2), _ic(r),
                     _p(r["p_valor"])] for r in sd])
    dif = _um(est, item="12.3", estatistica="diferenca_att_pos")
    terc = resumo["amostras"]["12.3"]["cortes_tercis"]
    k1v2 = _um(est, item="12.1", outcome_id="K1")
    desv = _tabela(["Data", "Tipo", "Item", "Descrição"],
                   [[d["data"], d["tipo"], d["item"], d["descricao"]] for d in resumo["desvios"]])
    ent = _tabela(["Arquivo", "Papel", "SHA-256 (12 primeiros)"],
                  [[e["caminho"], e["papel"], e["sha256"][:12]] for e in resumo["entradas"]])
    nao = [r for r in est.to_dict("records") if r["status"] == "NAO_EXECUTADO"]
    t_nao = _tabela(["Item", "Outcome", "Motivo"], [[r["item"], r["outcome_id"], r["nota"]] for r in nao]) if nao \
        else "Nenhum item ficou sem execução."
    partes = [
        "# 57c — Resultados do P3: extensões da produção especializada (adendo §12 do protocolo 47)",
        "",
        f"> **Gerado por** `{resumo['gerador']}` em {resumo['data_execucao']}. Não editar à mão: o script regrava o "
        "arquivo inteiro a partir das saídas `output/rdd_bolsa/K_X_*`, e o teste "
        "`tests/test_producao_extensoes.py` confere que o arquivo é igual ao gerado.<br>",
        f"> **Protocolo:** `{resumo['protocolo']['texto']}`, adendo §12 (12.1–12.5).<br>",
        f"> **Estatuto:** `{ESTATUTO}`, natureza `{NATUREZA}`. Os resultados D1 e D2 do doc 50 já tinham sido vistos "
        "quando o adendo foi escrito; nada aqui muda o Holm de K1–K3.<br>",
        "> **Nome do doc:** o adendo pede os resultados no \"doc 57, seção P3\"; o doc 57 é a síntese da onda 5. Para "
        "evitar conflito, a seção P3 fica neste doc 57c (desvio registrado na seção 9).",
        "",
        "## 1. O que se mede e o que não se mede",
        "",
        "- **D2, 12.2, 12.3 e 12.5** medem o **ATT da chegada do especialista sob tendências paralelas**: a chegada "
        "depende da escolha do candidato e não há fonte de exogeneidade validada. Onde o pré não é plano, a diferença "
        "é só uma associação.",
        "- **D1** (12.1 e 12.4) mede, no máximo, o incentivo marginal de R$ 5 mil dentro do pacote de regras dos "
        "cortes 0,300 e 0,400 (auditoria 18), não a participação no PMM-E.",
        "- **12.4** mede o uso de internação pelos residentes (acesso), não a oferta local.",
        "- **12.5** não separa expansão líquida de deslocamento: o protocolo lê negativo nos vizinhos como "
        "deslocamento de produção e positivo como atendimento de referência, mas isso é hipótese, não teste; a "
        "produção por município de execução não vê o paciente que migra.",
        "- Produção não é saúde nem espera: a fila não é pública e continua fora.",
        "",
        "## 2. Amostras e dados",
        "",
        tabela_amostras(resumo),
        "",
        "Ausências: nenhum mês posterior a 2026-07 é lido; as séries terminam em 2026-05 (adendo §10.1). Célula "
        "ausente na fonte fica ausente e não vira zero; no 12.5, basta um município da região sem dado no mês para o "
        "outcome regional daquele mês ficar ausente.",
        "",
        "## 3. 12.2 — Produção da especialidade que chegou (município × curso)",
        "",
        "Outcome: quantidade aprovada no SIA (a17) nas formas de organização típicas do curso (mapa do G4), executada "
        "pelas CBO do curso, por 10 mil habitantes. Controles: pares do mesmo curso que ofereceram célula e ainda não "
        "tinham recebido especialista. Inferência com cluster no município.",
        "",
        tabela_d2(est, ev, f22),
        "",
        fig("K_X_12_2_evento.png"),
        "",
        fig("K_X_12_2_cursos.png"),
        "",
        "## 4. 12.4 — Internações dos residentes",
        "",
        "K2r: AIH do grupo 04 (cirúrgico) de residentes; K2r_tot: todas as AIH de residentes (grupos 02–05). Mesmas "
        "janelas de K2 (pré 2024-06 a 2025-06, pós 2025-10 a 2026-05).",
        "",
        "### 4.1 D2 (chegada)",
        "",
        tabela_d2(est, ev, f24),
        "",
        "### 4.2 D1 (DiRD nos cortes, população U)",
        "",
        tabela_d1(est, "12.4", ["K2r", "K2r_tot"]),
        "",
        fig("K_X_12_4_residentes.png"),
        "",
        "## 5. 12.1 — Revisão da fonte (sensibilidade)",
        "",
        "A safra v1 (a13) continua a principal. A v2 (a13b) foi extraída depois da revisão do DATASUS nos meses "
        f"{', '.join(resumo['revisao_fonte']['sih_meses_revisados'])}. A linha v1 abaixo foi recalculada por este "
        "script e conferida contra o doc 50.",
        "",
        "### 5.1 D2",
        "",
        tabela_d2(est, ev, f21),
        "",
        "### 5.2 D1 (v1 e v2)",
        "",
        tabela_d1(est, "12.1", ["K2"], "a13_v1"),
        "",
        tabela_d1(est, "12.1", ["K2"], "a13b_v2"),
        "",
        f"K1 com a safra v2 do SIA: {k1v2['nota'] if k1v2 else '—'}",
        "",
        fig("K_X_12_1_versoes.png"),
        "",
        "## 6. 12.3 — Controles alternativos e heterogeneidade (K1)",
        "",
        "### 6.1 (a) Só controles cujas células ficaram vazias",
        "",
        tabela_d2(est, ev, f23),
        "",
        "### 6.2 (b) Diferenças em diferenças sintéticas, por coorte",
        "",
        t_sd,
        "",
        "### 6.3 (c) Fração dos chegados que já tinham vínculo no município antes do início",
        "",
        f"Tercis pela distribuição entre os municípios tratados (cortes: {_n(terc[0], 3, sinal=False)} e "
        f"{_n(terc[1], 3, sinal=False)}); a condição é anterior ao início de cada médico (X1, regra D1).",
        "",
        tabela_d2(est, ev, f23c),
        "",
        (f"Diferença tercil 3 − tercil 1: {_n(dif['valor'], 2)} (IC 95% {_ic(dif)}; p = {_p(dif['p_valor'])})."
         if dif else "Diferença tercil 3 − tercil 1: sem estimativa."),
        "",
        fig("K_X_12_3_controles.png"),
        "",
        "## 7. 12.5 — Transbordamento para os outros municípios da região de saúde",
        "",
        tabela_d2(est, ev, f25),
        "",
        fig("K_X_12_5_regiao.png"),
        "",
        "## 8. Teste múltiplo (BKY dentro do adendo) e leitura",
        "",
        tabela_bky(est),
        "",
        leitura(est, ev),
        "",
        "### 8.1 Itens não executados",
        "",
        t_nao,
        "",
        "## 9. Desvios e esclarecimentos",
        "",
        desv,
        "",
        "## 10. Entradas",
        "",
        ent,
        "",
        "## 11. Reprodução",
        "",
        "```bash",
        "python3 scripts/rdd_bolsa/27_producao_extensoes.py",
        "python3 -m pytest tests/test_producao_extensoes.py",
        "```",
        "",
    ]
    return "\n".join(partes)


def ler_saidas():
    est, ev = ler_tabelas()
    resumo = json.loads((OUT / NOME_RESUMO).read_text(encoding="utf-8"))
    return est, ev, resumo


def ler_tabelas():
    est = pd.read_csv(OUT / NOME_EST, dtype={"item": str, "corte": str, "recorte": str, "versao_fonte": str, "variante": str},
                      keep_default_na=True)
    for c in ("corte", "recorte", "versao_fonte"):
        est[c] = est[c].fillna("")
    ev = pd.read_csv(OUT / NOME_EVENTO, dtype={"item": str, "recorte": str, "versao_fonte": str})
    for c in ("recorte", "versao_fonte"):
        ev[c] = ev[c].fillna("")
    return est, ev


def atualizar_doc() -> None:
    est, ev, resumo = ler_saidas()
    DOC.write_text(gerar_doc(est, ev, resumo), encoding="utf-8")
    print(f"doc regravado: {rotulo(DOC)}")


# ---------------------------------------------------------------------------
# 7. Execução
# ---------------------------------------------------------------------------

DESVIOS = [
    {"data": DATA_EXECUCAO, "tipo": "desvio", "item": "local do resultado",
     "descricao": "o adendo §12 pede os resultados no 'doc 57, secao P3'; o doc 57 e a sintese da onda 5 (doc 51, §5). "
                  "Os resultados ficam em docs/06_execucao/57c_resultados_P3_extensoes.md, gerado inteiro pelo script."},
    {"data": DATA_EXECUCAO, "tipo": "esclarecimento", "item": "12.2: peso da agregacao",
     "descricao": "'media dos ATT entre cursos, com peso pelo numero de pares' foi lido como o theta(e) agregado sobre "
                  "todas as celulas curso x coorte com peso = numero de pares tratados (o ATT dos pares tratados), "
                  "fixado antes de estimar; os ATT por curso sao relatados a parte."},
    {"data": DATA_EXECUCAO, "tipo": "esclarecimento", "item": "12.2: cursos 10 e 11",
     "descricao": "os dois cursos tem o mesmo conjunto de CBO e as mesmas formas tipicas: o outcome de um par (m, 10) e "
                  "igual ao de (m, 11). Os pares ficam separados (tratamento por curso), e o cluster no municipio "
                  "absorve a correlacao."},
    {"data": DATA_EXECUCAO, "tipo": "esclarecimento", "item": "12.2: celulas e chegadas",
     "descricao": "par = municipio x curso com celula do curso no quadro dos ciclos 1 ou 2 (outcomes_V_celula) e em U; "
                  "chegada = menor dt_inicio_atividade da lista nominal no curso e municipio; especialista da lista "
                  "num par sem celula do curso fica fora (contado). Chegada depois de 202605 = ainda nao tratado no "
                  "horizonte, como no D2."},
    {"data": DATA_EXECUCAO, "tipo": "esclarecimento", "item": "12.3a no nivel do municipio",
     "descricao": "'so municipios com celula do mesmo curso e ciclo que ficou vazia' foi implementado no municipio como "
                  "D2 de K1 com controles = nunca tratados (nenhum especialista da lista nominal, celulas vazias); os "
                  "municipios com 1a chegada depois de 202605 saem (a celula nao ficou vazia). O pareamento por curso "
                  "e o 12.2."},
    {"data": DATA_EXECUCAO, "tipo": "esclarecimento", "item": "12.3b: DiD sintetico",
     "descricao": "algoritmo do pacote synthdid (Frank-Wolfe com intercepto, zeta_omega = (N1 T1)^(1/4) x DP das "
                  "primeiras diferencas dos controles no pre, zeta_lambda = 1e-6 x esse DP, esparsificacao em max/4); "
                  "por coorte trimestral, pre = 202201 ate o mes antes da coorte, pos = coorte ate 202605; controles = "
                  "nunca tratados; so unidades com a serie completa de K1. Agregado = media das coortes com peso pelo "
                  "numero de tratados. EP: bootstrap de municipios com reposicao (B = 200, semente fixa), sorteio "
                  "conjunto para todas as coortes, pesos reestimados a partir dos originais e zetas fixos (como no "
                  "pacote); sorteio sem tratado de alguma coorte ou com menos de 2 controles e refeito."},
    {"data": DATA_EXECUCAO, "tipo": "esclarecimento", "item": "12.3c: fracao e tercis",
     "descricao": "fracao = media de b_mesmo_mun_ultimo_pre (vinculo no municipio do posto na ultima competencia antes "
                  "do inicio) dos medicos ligados na X1, regra D1, ciclos 1 e 2; tercis pelos quantis 1/3 e 2/3 entre os "
                  "municipios tratados da amostra D2 com fracao (tercil 1: <= q1; 2: (q1, q2]; 3: > q2). Cada tercil "
                  "usa como controles os nunca tratados e os ainda nao tratados de qualquer tercil; diferenca tercil 3 - "
                  "tercil 1 com os mesmos pesos do bootstrap. A composicao da fracao inclui chegadas posteriores a 1a "
                  "(limite: a condicao e pre-tratamento para cada medico, nao para o municipio)."},
    {"data": DATA_EXECUCAO, "tipo": "esclarecimento", "item": "12.4: D1",
     "descricao": "K2r e K2r_tot em D1 como K2: DiRD local linear triangular h = 0,050, populacao U, cortes 0,300, 0,400 "
                  "e empilhado; variantes media completa, pos ate 202607 e sem UF-mes atipico (alerta do a15). V1, IC "
                  "honesto e Poisson do D1 nao foram repetidos."},
    {"data": DATA_EXECUCAO, "tipo": "esclarecimento", "item": "12.4: meses com falta em outra UF",
     "descricao": "o a15 sinaliza meses em que outra UF de internacao esta sem arquivo ou atipica (residentes internados "
                  "la podem faltar); o valor nao e alterado, como no a15, e os meses sinalizados vao no resumo."},
    {"data": DATA_EXECUCAO, "tipo": "esclarecimento", "item": "12.5: regiao de saude",
     "descricao": "CIR da tabela do TabNet (br_regsaud.cnv, o mesmo leitor do P5); so municipios de U entram no numerador "
                  "e no denominador; municipio sozinho na regiao ou sem CIR fica sem outcome (contado); outros "
                  "municipios tratados da mesma regiao continuam no somatorio (limite)."},
    {"data": DATA_EXECUCAO, "tipo": "esclarecimento", "item": "BKY do adendo",
     "descricao": "BKY entre as linhas principais novas: 12.2 agregado; K2r e K2r_tot em D1 (U, empilhado) e em D2; "
                  "12.3c (tercil 3 - tercil 1); K1_reg e K2_reg. 12.1 e 12.3a/b sao sensibilidades de estimativas ja "
                  "relatadas e ficam fora."},
    {"data": DATA_EXECUCAO, "tipo": "esclarecimento", "item": "12.3c: ligacao do medico (auditoria 25)",
     "descricao": "a ligacao da lista nominal ao CNES (X1, regra D1) usa as seis competencias do CNES lidas pela ponte 17 (202406, "
                  "202501, 202506, 202510, 202602 e 202608), algumas posteriores ao inicio; quem entra na fracao pode depender de "
                  "informacao posterior a chegada, embora o valor de cada medico use so a ultima competencia anterior ao "
                  "inicio. Os tercis tem tamanhos desiguais porque o corte inferior (0,000) agrupa todos os municipios "
                  "sem incumbente. Limite declarado; a diferenca entre tercis e descritiva."},
    {"data": DATA_EXECUCAO, "tipo": "esclarecimento", "item": "leitura do pre e do 12.5 (auditoria 25)",
     "descricao": "a leitura segue o doc 50: alem do Wald do pre (5%), cada ATT com IC fora de zero e lido com o theta medio "
                  "do pre (pre inteiro ou 12 meses antes do mes-base) de mesmo sinal ou sinal oposto e pelo menos metade do "
                  "ATT do pos; as colunas do doc mostram esses theta. Do 12.5, so a hipotese do protocolo (negativo = "
                  "deslocamento, positivo = referencia) e relatada, como hipotese: o K1 do municipio e o K1 regional nao "
                  "separam expansao liquida de deslocamento."},
    {"data": DATA_EXECUCAO, "tipo": "esclarecimento", "item": "12.1: K1",
     "descricao": "o adendo manda reestimar K1 so se a safra v2 do SIA tiver revisao; o a12b relata zero celulas "
                  "diferentes, entao K1 nao foi reestimado (linha NAO_EXECUTADO com o motivo)."},
]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--atualizar-doc", action="store_true", help="so regrava o doc 57c a partir das saidas")
    args = ap.parse_args(argv)
    if args.atualizar_doc:
        atualizar_doc()
        return 0
    try:
        est, ev, att, resumo = executar()
    except (FalhaValidacao, K1M.FalhaValidacao, D2M.FalhaValidacao) as erro:
        print(f"FALHA DE VALIDACAO (nada gravado): {erro}", file=sys.stderr)
        return 2
    OUT.mkdir(parents=True, exist_ok=True)
    est.to_csv(OUT / NOME_EST, index=False)
    ev.to_csv(OUT / NOME_EVENTO, index=False)
    att.to_csv(OUT / NOME_ATT, index=False)
    est, ev = ler_tabelas()
    resumo["figuras"] = gerar_figuras(est, ev, OUT / DIR_FIG)
    resumo["saidas"] = {n: {"arquivo": rotulo(OUT / n), "sha256": sha256(OUT / n)} for n in (NOME_EST, NOME_EVENTO,
                                                                                               NOME_ATT)}
    K1M._gravar_json(OUT / NOME_RESUMO, resumo)
    atualizar_doc()
    p = est[est["entra_bky"].astype(bool)]
    print("K_X (BKY): " + "; ".join(f"{r.item} {r.outcome_id} {r.desenho} {r.valor:.3f} p={r.p_valor:.3f} q={r.q_bky:.3f}"
                                    for r in p.itertuples()))
    return 0


def executar():
    base, conf_pop = K1M.ler_universo()
    universo = base.index
    sia, info_sia = K1M.ler_sia(universo)
    sih1, sih1_atip, info_sih1 = K1M.ler_sih(universo)
    D = K1M.Dados(base, sia, sih1, sih1_atip, None, None, None, None, None, {})
    pop = base["populacao_2022"].astype(float)
    amostra, info_am = D2M.ler_amostra(base)
    chegadas, info_ch = D2M.ler_chegadas(amostra)
    G_d2, _ = D2M.indices_coorte(chegadas, list(MESES))
    est_l, ev_l, att_l = [], [], []

    def juntar(trip):
        est_l.extend(trip[0])
        ev_l.extend(trip[1])
        att_l.extend(trip[2])

    # ---- 12.2 -------------------------------------------------------------------------------------------
    cursos, tip, conj, info_cur = ler_cursos_especificos()
    a17, info_a17 = ler_a17(cursos, tip, conj, universo)
    pares, info_pares = ler_pares(base, cursos)
    taxas = {c: serie_taxa(a17[c], pop, universo) for c in cursos}
    pos_u = {m: i for i, m in enumerate(universo)}
    Yp = np.vstack([taxas[c][pos_u[m]] for m, c in zip(pares["co_ibge"], pares["cod_curso"])])
    Gp, _ = D2M.indices_coorte(pares, list(MESES))
    grupo = pares["cod_curso"].to_numpy()
    clus = pares["co_ibge"].to_numpy()
    coortes_p = sorted({(int(c), int(g)) for c, g in zip(grupo, Gp) if g >= 0})
    meta = {"item": "12.2", "outcome_id": "K_esp", "desenho": "D2", "versao_fonte": "a17", "_meses": list(MESES)}
    r = estimar_cs_cluster(Yp, Gp, coortes_p, clus, grupo=grupo)
    juntar(linhas_d2(r, {**meta, "recorte": TODOS}, n_unidades=len(Gp), n_trat=int((Gp >= 0).sum()),
                     n_nunca=int((Gp < 0).sum()), n_coortes=len(coortes_p),
                     media_ref=media_pre_tratados(Yp, Gp, list(MESES))))
    for c in cursos:
        m = grupo == c
        cs = [(cc, g) for cc, g in coortes_p if cc == c]
        if not cs:
            est_l.append(_linha(**{k: v for k, v in meta.items() if k != "_meses"}, recorte=f"curso_{c}",
                                estatistica="att_pos_medio", valor=np.nan, status="SEM_ESTIMATIVA",
                                n_unidades=int(m.sum()), n_tratados=0, contraste=CONTRASTE_D2,
                                nota="nenhum par do curso com chegada ate 202605"))
            continue
        rc = estimar_cs_cluster(Yp[m], Gp[m], cs, clus[m], grupo=grupo[m])
        juntar(linhas_d2(rc, {**meta, "recorte": f"curso_{c}"}, n_unidades=int(m.sum()),
                         n_trat=int((Gp[m] >= 0).sum()), n_nunca=int((Gp[m] < 0).sum()), n_coortes=len(cs),
                         media_ref=media_pre_tratados(Yp[m], Gp[m], list(MESES))))

    # ---- 12.4 -------------------------------------------------------------------------------------------
    resid, resid_atip, info_a15 = ler_sih_residencia(universo)
    mascara_falta = info_a15.pop("mascara_falta")
    for oid in ("K2r", "K2r_tot"):
        meta = {"item": "12.4", "outcome_id": oid, "versao_fonte": "a15"}
        linhas, _ = d1_linhas(resid[oid], D, meta, resid_atip)
        est_l.extend(linhas)
        e, v, a, _, _ = d2_municipio(resid[oid], D, amostra, chegadas, {**meta, "desenho": "D2"})
        juntar((e, v, a))

    # ---- 12.1 -------------------------------------------------------------------------------------------
    sih2, sih2_atip, info_sih2 = ler_sih_v2(universo)
    comp_sih = json.loads(SIH_V2_COMP.read_text(encoding="utf-8"))
    comp_sia = json.loads(SIA_V2_COMP.read_text(encoding="utf-8"))
    kd1 = pd.read_csv(K_D1_EST, dtype={"corte": str})
    kd2 = pd.read_csv(K_D2_EST)
    for versao, num, atip in (("a13_v1", sih1, sih1_atip), ("a13b_v2", sih2, sih2_atip)):
        meta = {"item": "12.1", "outcome_id": "K2", "versao_fonte": versao}
        linhas, guarda = d1_linhas(num, D, meta, atip)
        est_l.extend(linhas)
        e, v, a, rr, _ = d2_municipio(num, D, amostra, chegadas, {**meta, "desenho": "D2"})
        juntar((e, v, a))
        if versao == "a13_v1":
            for corte in ("0.300", "0.400", "empilhado"):
                ref = kd1[(kd1["outcome_id"] == "K2") & (kd1["populacao"] == "U") & (kd1["corte"] == corte)
                          & (kd1["especificacao"] == "principal")]["tau"]
                if len(ref) != 1 or abs(float(ref.iloc[0]) - float(guarda[(corte, "principal")]["valor"])) > 1e-9:
                    raise FalhaValidacao(f"K2 v1 D1 {corte} nao reproduz K_D1_estimativas")
            ref = kd2[(kd2["outcome_id"] == "K2") & (kd2["variante"] == "principal")
                      & (kd2["estatistica"] == "att_pos_medio")]["valor"]
            if len(ref) != 1 or abs(float(ref.iloc[0]) - rr["pos"]["att"]) > 1e-9:
                raise FalhaValidacao("K2 v1 D2 nao reproduz K_D2_estimativas")
    if int(comp_sia["celulas_diferentes"]) == 0:
        est_l.append(_linha(item="12.1", outcome_id="K1", versao_fonte="a12b_v2", desenho="D1 e D2",
                            estatistica="nao_executado", valor=np.nan, status="NAO_EXECUTADO", contraste="",
                            descricao_outcome=DESCRICAO["K1"],
                            nota=f"sem revisao na fonte: o a12b compara {comp_sia['celulas_comparadas']} celulas "
                                 f"municipio x mes x subgrupo x conjunto e nenhuma difere da v1; K1 com a v2 seria "
                                 "identico ao do doc 50"))
    else:
        raise FalhaValidacao("a safra v2 do SIA tem revisao: o adendo manda reestimar K1 (nao implementado)")

    # ---- 12.3 -------------------------------------------------------------------------------------------
    num_k1 = D.sia_soma(("alvo_pmme",), K1M.TIPOS_K1)
    meta = {"item": "12.3", "outcome_id": "K1", "versao_fonte": "a12"}
    e, v, a, r_d2, G = d2_municipio(num_k1, D, amostra, chegadas, {**meta, "recorte": "D2_doc50"})
    ref = kd2[(kd2["outcome_id"] == "K1") & (kd2["variante"] == "principal") & (kd2["estatistica"] == "att_pos_medio")]
    if len(ref) != 1 or abs(float(ref["valor"].iloc[0]) - r_d2["pos"]["att"]) > 1e-9:
        raise FalhaValidacao("K1 D2 nao reproduz K_D2_estimativas")
    juntar((e, v, a))
    tarde = chegadas.index[(chegadas["chegada"] > FIM).fillna(False).to_numpy()]
    am_a = amostra.difference(tarde)
    ch_a = chegadas.reindex(am_a)
    juntar(d2_municipio(num_k1, D, am_a, ch_a, {**meta, "recorte": "a_nunca_tratados"}, controles="nunca")[:3])
    # (b) DiD sintético
    Ya = serie_taxa(num_k1, pop, am_a)
    Ga, coortes_a = D2M.indices_coorte(ch_a, list(MESES))
    completo = np.isfinite(Ya).all(axis=1)
    info_sdid = {"sem_serie_completa": int((~completo).sum())}
    sd_l, sd_info = sdid_coortes(Ya[completo], Ga[completo], coortes_a, am_a[completo])
    for ln in sd_l:
        est_l.append(_linha(**meta, **ln))
    info_sdid.update(sd_info)
    # (c) tercis de incumbência
    frac, info_fr = ler_fracao_incumbentes(amostra)
    tratados_h = G >= 0
    fv = frac.to_numpy(dtype=float)
    com = tratados_h & np.isfinite(fv)
    q1, q2 = (float(x) for x in np.quantile(fv[com], [1 / 3, 2 / 3]))
    terc = np.where(fv <= q1, 1, np.where(fv <= q2, 2, 3))
    res_t = {}
    for k in (1, 2, 3):
        eleg = com & (terc == k)
        if not eleg.any():
            est_l.append(_linha(**meta, recorte=f"c_tercil_{k}", desenho="D2", estatistica="att_pos_medio",
                                valor=np.nan, status="SEM_ESTIMATIVA", contraste=CONTRASTE_D2,
                                nota=f"tercil vazio com os cortes {q1:.3f} e {q2:.3f} (empates)"))
            continue
        e, v, a, rk, _ = d2_municipio(num_k1, D, amostra, chegadas, {**meta, "recorte": f"c_tercil_{k}"},
                                      elegivel=eleg)
        juntar((e, v, a))
        res_t[k] = rk
    if 1 in res_t and 3 in res_t:
        d = diferenca_pos(res_t[3], res_t[1])
        est_l.append(_linha(**meta, recorte="c_tercil_3_menos_1", desenho="D2", estatistica="diferenca_att_pos",
                            valor=d["att"], ep=d["ep"], ic95_inf=d["ic95_inf"], ic95_sup=d["ic95_sup"],
                            p_valor=d["p_valor"], n_unidades=len(amostra), n_clusters=len(amostra),
                            contraste="diferenca de ATT sob tendencias paralelas entre tercis de incumbencia "
                                      "(heterogeneidade descritiva por condicao pre-tratamento)",
                            nota="mesmos pesos do bootstrap nos dois tercis"))
    info_terc = {"cortes_tercis": [q1, q2], "tratados_com_fracao": int(com.sum()),
                 "tratados_sem_fracao": int((tratados_h & ~np.isfinite(fv)).sum()),
                 "tratados_por_tercil": {str(k): int((com & (terc == k)).sum()) for k in (1, 2, 3)}, **info_fr}

    # ---- 12.5 -------------------------------------------------------------------------------------------
    cir, info_cir = ler_cir()
    reg_info = {}
    for oid, num in (("K1_reg", num_k1), ("K2_reg", sih1)):
        Yr, ir = serie_regional(num, pop, cir, amostra)
        reg_info[oid] = ir
        juntar(d2_municipio(num, D, amostra, chegadas, {"item": "12.5", "outcome_id": oid, "desenho": "D2",
                                                        "versao_fonte": "a12" if oid == "K1_reg" else "a13_v1"},
                            Y=Yr)[:3])

    # ---- montagem e BKY ---------------------------------------------------------------------------------
    est = pd.DataFrame(est_l)
    for c in COLUNAS_EST:
        if c not in est:
            est[c] = np.nan
    est = est[COLUNAS_EST]
    est["entra_bky"] = False
    mb = ((est["estatistica"] == "att_pos_medio") & (est["variante"] == "principal")
          & (((est["item"] == "12.2") & (est["recorte"] == TODOS))
             | ((est["item"] == "12.4") & (est["desenho"] == "D2"))
             | (est["item"] == "12.5"))) \
        | ((est["item"] == "12.4") & (est["desenho"] == "D1") & (est["corte"] == "empilhado")
           & (est["variante"] == "principal")) \
        | ((est["item"] == "12.3") & (est["estatistica"] == "diferenca_att_pos"))
    mb &= est["status"] == "EXECUTADO"
    if int(mb.sum()) != 8:
        raise FalhaValidacao(f"BKY: {int(mb.sum())} linhas (esperadas 8)")
    est.loc[mb, "entra_bky"] = True
    est["q_bky"] = np.nan
    est.loc[mb, "q_bky"] = L.qvalores_bky(est.loc[mb, "p_valor"].to_numpy(dtype=float))
    sem_nota = est[est["valor"].isna() & (est["estatistica"] != "pretendencia_supt") & (est["nota"].fillna("") == "")]
    if len(sem_nota):
        raise FalhaValidacao(f"{len(sem_nota)} linhas sem estimativa e sem nota")
    ev = pd.DataFrame(ev_l)[COLUNAS_EVENTO]
    att = pd.DataFrame(att_l)[COLUNAS_ATT]

    resumo = {
        "etapa": "K_X_extensoes_P3", "natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO,
        "gerador": rotulo(Path(__file__)), "data_execucao": DATA_EXECUCAO,
        "protocolo": {"texto": rotulo(PROTOCOLO_MD), "sha256_texto": sha256(PROTOCOLO_MD), "secao": "adendo §12"},
        "doc": rotulo(DOC),
        "leitura": "D2, 12.2, 12.3 e 12.5: ATT sob tendencias paralelas (chegada depende da escolha do candidato); D1: "
                   "incentivo marginal dentro do pacote dos cortes; 12.4: acesso dos residentes, nao oferta local; "
                   "12.5: leitura do protocolo (negativo = deslocamento, positivo = referencia) e so hipotese; expansao liquida e "
                   "deslocamento nao ficam separados",
        "parametros": {"e_min": E_MIN, "e_max": E_MAX, "inicio": INICIO, "fim_da_serie": FIM,
                       "bootstrap_cs": {"B": B_BOOT, "pesos": "Mammen", "semente": SEMENTE, "cluster": "municipio"},
                       "bootstrap_sdid": {"B": B_SDID, "semente": SEMENTE_SDID, "unidade": "municipio"},
                       "pos_K2": [POS_K2[0], POS_K2[-1]], "pre": [COMP_PRE[0], COMP_PRE[-1]]},
        "amostras": {
            "cursos_especificos": info_cur, "12.2_pares": info_pares, "a17": info_a17,
            "d2": {**info_am, **{k: v for k, v in info_ch.items() if k != "colunas_lidas"},
                   "n_municipios": int(len(amostra)), "n_tratados_horizonte": int((G_d2 >= 0).sum()),
                   "n_nao_tratados_horizonte": int((G_d2 < 0).sum())},
            "12.3": {"retirados_chegada_depois_do_fim": int(len(tarde)),
                     "sdid_sem_serie_completa": info_sdid["sem_serie_completa"], "sdid": info_sdid, **info_terc},
            "12.4": info_a15, "12.5": {**reg_info["K1_reg"], "K2_reg": reg_info["K2_reg"], "cir": info_cir},
            "sia": info_sia, "sih_v1": info_sih1, "sih_v2": info_sih2, "populacoes": conf_pop},
        "revisao_fonte": {"sih_meses_revisados": comp_sih["meses_revisados"],
                          "sih_contagem_situacao_uf_mes_grupo": comp_sih["contagem_situacao_uf_mes_grupo"],
                          "sia_celulas_comparadas": comp_sia["celulas_comparadas"],
                          "sia_celulas_diferentes": comp_sia["celulas_diferentes"]},
        "desvios": DESVIOS,
        "entradas": entradas(),
        "contagens": {"linhas_estimativas": int(len(est)), "linhas_evento": int(len(ev)), "linhas_att_gt": int(len(att)),
                      "por_status": est["status"].value_counts().sort_index().to_dict(),
                      "linhas_bky": int(est["entra_bky"].sum())},
        "validacoes": {"K2_v1_D1_reproduz_doc50": True, "K2_v1_D2_reproduz_doc50": True, "K1_D2_reproduz_doc50": True,
                       "formas_tipicas_G4_iguais_a17": True, "sha256_iguais_manifestos": True},
        "integridade": "nada imputado; ausente nao vira zero; SIA e SIH lidos ate 202607 (series ate 202605); nenhum mes "
                       "CNES lido; lista nominal sem nomes; o arquivo local de IVS da auditoria 16 nao e lido",
    }
    return est, ev, att, resumo


def sdid_coortes(Y: np.ndarray, G: np.ndarray, coortes: list[int], ids: pd.Index) -> tuple[list[dict], dict]:
    """DiD sintético por coorte e agregado (peso = tratados), com bootstrap conjunto de municípios."""
    ctrl = np.flatnonzero(G < 0)
    ests, pesos, ini, info = {}, {}, {}, {}
    for g in coortes:
        tr = np.flatnonzero(G == g)
        Yg = np.vstack([Y[ctrl], Y[tr]])
        r = sdid(Yg, len(ctrl), g)
        ests[g], pesos[g] = r["tau"], len(tr)
        ini[g] = (r["omega"], r["lambda"], r["zetas"])
        info[MESES[g]] = {"tratados": int(len(tr)), "controles": int(len(ctrl)), "meses_pre": int(g),
                          "meses_pos": int(len(MESES) - g), "controles_com_peso": int((r["omega"] > 0).sum()),
                          "maior_peso_unidade": float(r["omega"].max())}
    W = np.array([pesos[g] for g in coortes], dtype=float)
    agg = float(np.sum(W * np.array([ests[g] for g in coortes])) / W.sum())
    rng = np.random.default_rng(SEMENTE_SDID)
    N = len(G)
    boot = []
    refeitos = 0
    while len(boot) < B_SDID:
        ind = np.sort(rng.integers(0, N, N))
        Gb = G[ind]
        c_b = ind[Gb < 0]
        if len(c_b) < 2 or any((Gb == g).sum() == 0 for g in coortes):
            refeitos += 1
            continue
        vals = []
        w_ctrl = {i: k for k, i in enumerate(ctrl)}
        for g in coortes:
            tr_b = ind[Gb == g]
            Yg = np.vstack([Y[c_b], Y[tr_b]])
            om0 = ini[g][0][[w_ctrl[i] for i in c_b]]
            om0 = om0 / om0.sum() if om0.sum() > 0 else np.full(len(c_b), 1 / len(c_b))
            vals.append(sdid(Yg, len(c_b), g, zetas=ini[g][2], pesos_ini=(om0, ini[g][1]))["tau"])
        vals = np.array(vals)
        boot.append(np.concatenate([vals, [np.sum(W * vals) / W.sum()]]))
    boot = np.array(boot)
    se = np.sqrt((B_SDID - 1) / B_SDID) * boot.std(axis=0, ddof=1)
    linhas = []
    for j, (rec, val, n_t) in enumerate([(f"b_sdid_coorte_{MESES[g]}", ests[g], pesos[g]) for g in coortes]
                                        + [("b_sdid_agregado", agg, int(W.sum()))]):
        ep = float(se[j])
        linhas.append({"recorte": rec, "desenho": "SDID", "estatistica": "att_sdid", "valor": val, "ep": ep,
                       "ic95_inf": val - L.Z_975 * ep, "ic95_sup": val + L.Z_975 * ep,
                       "p_valor": L.p_normal(val / ep) if ep > 0 else np.nan, "n_unidades": int(N),
                       "n_tratados": int(n_t), "n_controles_nunca": int(len(ctrl)), "n_clusters": int(N),
                       "n_coortes": len(coortes) if rec == "b_sdid_agregado" else 1, "contraste": CONTRASTE_SDID,
                       "nota": "agregado = media das coortes com peso pelo numero de tratados" if rec == "b_sdid_agregado"
                       else f"pre 202201 ate o mes antes da coorte; pos ate {FIM}"})
    return linhas, {"por_coorte": info, "bootstrap_sorteios_refeitos": refeitos}


def entradas() -> list[dict]:
    b = E7.bloco_entrada
    return [
        b(PROTOCOLO_MD, "protocolo congelado (adendo §12)", "doc 47", "2026-10-19", "-", "-", "-", "-"),
        b(A17_PAINEL, "12.2: SIA por forma x curso", "DATASUS TabNet qabr.def (a17)", "processamento 202201-202607",
          "municipios do formulario", "municipio x mes x curso x forma", "co_ibge, competencia_processamento, cod_curso, "
          "forma", "cursos ESPECIFICO; formas tipicas do G4; meses 202201-202605"),
        b(A17_MANIF, "manifesto do a17 (SHA-256 do painel)", "a17", "2026-10-19", "-", "-", "-", "saidas"),
        b(A17_PRES, "12.2: formas presentes por consulta (zero de forma omitida)", "a17", "202201-202607", "consultas",
          "mes x conjunto x forma", "competencia_processamento, conjunto_cbo, forma", "presente_na_resposta"),
        b(A17_TIPICAS, "12.2: formas tipicas (conferencia com o G4)", "a17", "2026-10-19", "cursos", "curso x forma",
          "cod_curso, co_forma", "-"),
        b(A17_CURSOS, "12.2: conjunto de CBO por curso", "a17", "2026-10-19", "cursos", "curso", "cod_curso", "-"),
        b(G4_RESUMO, "12.2: cursos da classe ESPECIFICO", "portao G4", "2026-10-19", "16 cursos", "curso", "cod_curso",
          "classes_dos_cursos.ESPECIFICO"),
        b(G4_MAPA, "12.2: formas tipicas por curso", "portao G4", "SIA 2024", "curso x forma", "curso x forma",
          "cod_curso, co_forma", "tipica == True"),
        b(V_CELULA, "12.2: celulas por curso nos ciclos 1-2", "tarefa B (12)", "ciclos 1-2", "celulas",
          "celula", "ciclo, co_ibge, cod_curso", "ciclo in (1, 2); cursos ESPECIFICO"),
        b(NOMINAL, "chegada por municipio (D2) e por municipio x curso (12.2)", "MS, lista nominal do PMM-E (retrato)",
          "2026-08-12", "especialistas ativos", "especialista", "co_ibge, curso",
          f"so as colunas {', '.join(COLUNAS_NOMINAL)}; nenhum nome lido"),
        b(A15_PAINEL, "12.4: SIH por residencia", "DATASUS TabNet qrbr.def (a15)", "processamento 202201-202607",
          "municipios do formulario", "municipio x mes x grupo", "co_ibge, competencia, grupo", "grupos 02-05"),
        b(A15_MANIF, "manifesto do a15", "a15", "2026-10-19", "-", "-", "-", "saidas.painel"),
        b(SIH_V2, "12.1: SIH safra v2", "DATASUS TabNet qibr.def (a13b)", "processamento 202201-202607",
          "municipios do formulario", "municipio x mes x grupo", "co_ibge, competencia, grupo", "grupo == 04"),
        b(SIH_V2_MANIF, "manifesto da safra v2 do SIH", "a13b", "2026-10-19", "-", "-", "-", "saidas.painel"),
        b(SIH_V2_COMP, "12.1: meses revisados do SIH", "a13b", "2026-10-19", "-", "UF x mes x grupo", "-", "-"),
        b(SIA_V2_COMP, "12.1: revisao do SIA (celulas diferentes)", "a12b", "2026-10-19", "-", "celula", "-", "-"),
        b(K1M.SIA, "K1 (12.3) e K1_reg (12.5)", "DATASUS TabNet qabr.def (a12)", "processamento 202201-202607",
          "municipios do formulario", "municipio x mes x subgrupo x conjunto", "co_ibge, competencia_processamento, "
          "subgrupo, conjunto_cbo", "alvo_pmme; subgrupos 0301, 02, 04, 09"),
        b(K1M.MANIF_SIA, "manifesto do a12", "a12", "2026-10-19", "-", "-", "-", "saidas"),
        b(K1M.SIH, "K2 v1 (12.1) e K2_reg (12.5)", "DATASUS TabNet qibr.def (a13)", "processamento 202201-202607",
          "municipios do formulario", "municipio x mes x grupo", "co_ibge, competencia, grupo", "grupo == 04"),
        b(K1M.MANIF_SIH, "manifesto do a13", "a13", "2026-10-19", "-", "-", "-", "saidas.painel"),
        b(CIR_CNV, "12.5: regiao de saude (CIR)", "DATASUS/TabNet br_regsaud.cnv (bruto, somente lido)", "corrente",
          "municipios", "municipio", "co_ibge", "linhas 'Ignorado' fora"),
        b(X1_MEDICOS, "12.3c: vinculo no municipio antes do inicio", "X1 (17)", "ciclos 1-3", "medicos ligados",
          "medico", "id_medico", "regra d1_pos_hoc; ciclos 1-2; ligado == 1"),
        b(K1M.A08, "universo U e running variable do D1 (IVS 2010 oficial)", "Ipea (a08)", "Censo 2010", "municipios",
          "municipio", "co_ibge", "co_ibge, ivs"),
        b(K1M.POP22, "denominador por 10 mil hab.", "IBGE Censo 2022", "2022", "municipios", "municipio", "co_ibge_6d",
          "populacao_2022"),
        b(K1M.ARQ_VM, "amostra do D2 (celulas nos ciclos 1-2)", "tarefa B (12)", "ciclos 1-2", "V1, V2",
          "municipio x ciclo", "ciclo, co_ibge", "ciclo in (1, 2)"),
        b(K_D1_EST, "conferencia: K2 v1 em D1", "21", "2026-10-19", "-", "-", "-", "K2, U, principal"),
        b(K_D2_EST, "conferencia: K1 e K2 v1 em D2", "22", "2026-10-19", "-", "-", "-", "att_pos_medio, principal"),
    ]


if __name__ == "__main__":
    sys.exit(main())
