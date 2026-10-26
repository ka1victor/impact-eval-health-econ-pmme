"""Adendo 48f: seleção pelo tipo de vaga na H1 (tipo como outcome, balanço na amostra selecionada, limites de Lee).

Especificação congelada antes das contas: `docs/06_execucao/48f_adendo_selecao_tipo_de_vaga.md` (26/10/2026, commit
f97e1ca; SHA-256 conferido abaixo). Estatuto: `ADENDO_48F_POS_RESULTADO`; `natureza_dos_dados = EMPIRICO` em toda
saída. As decisões de implementação estão na seção 0 do doc 57t, registradas em commit antes de qualquer estimativa
(commit efdeece).

O que faz, na ordem
-------------------
1. Portão: reproduz HI-1 e HI-2 do 48b nos dois cortes (função `portao_hi` do script 44, <= 1e-8 contra
   `HI_estimativas.csv`) e a parte de células só de cadastro reserva do doc 57l (D-b: "célula só de CR" e "parte das
   células só de CR", por ciclo e com os ciclos juntos), com o quadro do ciclo 2 de 19/03/2026 que o 57l usou (<= 1e-8
   contra `DQ_estimativas.csv`). Se algo não bater, para sem gravar nada. A diferença de definição (S em vez da parte
   de células só de CR; ciclo 2 pelo quadro de 13/02/2026) é relatada.
2. SV-1: RDD de S (município × ciclo com >= 1 célula com vaga imediata) e de "célula tem vaga imediata" (célula, EF de
   curso × ciclo), por corte.
3. SV-2: salto das covariáveis L e M do 48d entre S = 1 e na amostra toda (confere as linhas de S = 1 contra o CL-0).
4. SV-3: limites de Lee (versão de randomização local, §3 do adendo) para Y1 e Y2, por corte, com IC de Imbens–Manski
   por bootstrap em blocos de município (1.999 reamostras, semente 20261026, aparagem refeita em cada reamostra).
5. SV-4 (janela 0,020) e SV-5 (com a reta: aparagem nos resíduos).
6. Leitura pelo §4 do adendo (regras fixas no código), figuras com "Como ler" e blocos do doc 57t.

Integridade: running variable = IVS 2010 oficial (a08), pelas funções dos scripts 40 e 44; o arquivo local de IVS da
auditoria 16 não é lido; nenhuma competência do CNES >= 202609 (covariáveis do 44: 202406–202506); nada é escrito em
`data/`; Y de unidade sem vaga imediata fica ausente, nunca zero; as saídas `HI_*`, `CL_*` e `DQ_*` só são lidas.

Uso
---
    python3 scripts/rdd_bolsa/46_selecao_tipo_vaga.py                  # calcula e grava as saídas
    python3 scripts/rdd_bolsa/46_selecao_tipo_vaga.py --atualizar-doc  # idem e regrava os blocos do 57t
    python3 scripts/rdd_bolsa/46_selecao_tipo_vaga.py --so-doc         # só regrava os blocos do 57t
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

ROOT = Path(__file__).resolve().parents[2]
DIR_RDD = ROOT / "scripts" / "rdd_bolsa"


def _importar(caminho: Path, nome: str):
    if nome in sys.modules:
        return sys.modules[nome]
    bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec = importlib.util.spec_from_file_location(nome, caminho)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[nome] = mod
        spec.loader.exec_module(mod)
    finally:
        sys.dont_write_bytecode = bytecode
    return mod


# O 44 importa o 40 com este nome; importar com o mesmo nome reaproveita o módulo (um só 40, um só 23).
T44 = _importar(DIR_RDD / "44_controles_localizacao_medicos.py", "controles_localizacao_medicos_para_sv")
T40 = _importar(DIR_RDD / "40_h1_vagas_imediatas.py", "h1_vagas_imediatas_para_cl")
T24 = _importar(DIR_RDD / "24_abertura_vagas_selecao.py", "abertura_para_sv")      # ic_imbens_manski
T23 = T40.T23
L = T40.L

# ---------------------------------------------------------------------------
# Parâmetros do adendo
# ---------------------------------------------------------------------------

OUT = ROOT / "output" / "rdd_bolsa"
ADENDO = ROOT / "docs" / "06_execucao" / "48f_adendo_selecao_tipo_de_vaga.md"
DOC = ROOT / "docs" / "06_execucao" / "57t_resultados_selecao_tipo_vaga.md"
HI_EST = OUT / "HI_estimativas.csv"
CL_BAL = OUT / "CL_balanco.csv"
DQ_EST = OUT / "DQ_estimativas.csv"
NOME_EST = "SV_estimativas.csv"
NOME_BAL = "SV_balanco.csv"
NOME_RESUMO = "SV_resumo.json"
DIR_FIG = OUT / "SV_figuras"

DATA_EXECUCAO = "2026-10-26"
ESTATUTO = "ADENDO_48F_POS_RESULTADO"
NATUREZA = "EMPIRICO"
COMMIT_CONGELAMENTO = "f97e1ca"
COMMIT_DECISOES = "efdeece"
SHA_ADENDO = "b96bbd2d2b1650281291ab8712360a99eb3412b2a5a591778fb1a8da0f51575c"
CORTES = (300, 400)
CICLOS = (1, 2, 3)
H = 50                      # h = 0,050 (especificação comum; janela do SV-3 e do SV-5)
H_SV4 = 20                  # SV-4: janela 0,020
N_BOOT = 1_999
SEMENTE = 20261026
TOL = 1e-8
ALFA = 0.05
LIMIAR_Q = 0.05             # §4: "taxas de seleção parecidas (q < 0,05)"
Z975 = 1.959963984540054
EMPATES = "proporcional"    # decisão 12 (auditoria 22)
TXT_CORTE = {300: "0,300", 400: "0,400"}
ROT_CORTE = {300: "0.300", 400: "0.400"}
BOLSA = {300: "R$ 10 mil → R$ 15 mil", 400: "R$ 15 mil → R$ 20 mil"}
VARS_BAL = T44.VARS_BAL     # capital, 5 macrorregiões, log_pop, med, esp, esp_resto
ROT_BAL = T44.ROT_BAL

UN_FRAC = T44.UN_FRAC       # "fracao (x100 = p.p.)"
UN_VAGA = T44.UN_VAGA       # "medicos alocados por vaga imediata"
OUTCOMES = {
    "Y1": {"col": "frac_preenchida", "unidade": UN_FRAC, "par_44": "H1M-FRAC",
           "desc": "fracao das celulas com vaga imediata do municipio x ciclo preenchidas na 1a chamada (H1M-FRAC do "
                   "48d; versao municipal da HI-1)",
           "nome": "Y1 · fração das células com vaga imediata preenchidas"},
    "Y2": {"col": "aloc_por_vi", "unidade": UN_VAGA, "par_44": "H1M-ALOC",
           "desc": "medicos alocados na 1a chamada em celulas com vaga imediata por vaga imediata, por municipio x "
                   "ciclo (H1M-ALOC do 48d; versao municipal da HI-2 sem regressao)",
           "nome": "Y2 · médicos alocados por vaga imediata"},
}
VERSOES = {"SV-3": {"janela": H, "reta": False, "papel": "principal",
                    "metodo": "Lee (randomizacao local), janela 0,050"},
           "SV-4": {"janela": H_SV4, "reta": False, "papel": "sensibilidade",
                    "metodo": "Lee (randomizacao local), janela 0,020"},
           "SV-5": {"janela": H, "reta": True, "papel": "sensibilidade",
                    "metodo": "Lee com a reta (aparagem nos residuos), janela 0,050"}}
CONTRASTE = T44.CONTRASTE

COLUNAS = [
    "natureza_dos_dados", "estatuto", "id_linha", "linha", "papel", "tipo_linha", "outcome", "descricao_outcome",
    "unidade_analise", "amostra", "ciclo", "corte", "janela", "metodo", "estimador", "status",
    "tau", "ep", "ic95_inf", "ic95_sup", "p_valor", "n_abaixo", "n_acima", "n_obs", "n_clusters",
    "media_abaixo", "media_acima", "p_abaixo", "p_acima", "q", "lado_aparado", "n_selecionados", "peso_ciclo",
    "limite_inf", "limite_sup", "ep_limite_inf", "ep_limite_sup", "ic_im_inf", "ic_im_sup",
    "dif_sem_aparo", "ep_dif_sem_aparo", "ic_sem_aparo_inf", "ic_sem_aparo_sup", "n_reamostras",
    "n_reamostras_validas", "ciclos_fora", "unidade", "nota",
]
COLUNAS_BAL = [
    "natureza_dos_dados", "estatuto", "linha", "amostra", "corte", "janela", "variavel", "tau", "ep", "ic95_inf",
    "ic95_sup", "p_valor", "n_abaixo", "n_acima", "n_obs", "dp_janela_amostra_toda", "salto_padronizado",
    "ic_exclui_zero", "confere_cl0", "status", "nota",
]


class FalhaValidacao(RuntimeError):
    """Portão ou validação obrigatória falhou: o script para sem gravar."""


sha256 = T23.sha256
rotulo = T23.rotulo
_nan_none = T40._nan_none


def _f(x) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return float("nan")


def _juntar(*notas) -> str:
    return "; ".join(str(n) for n in notas if n)


# ---------------------------------------------------------------------------
# 1. Bases (construtores do 44 e do 40)
# ---------------------------------------------------------------------------

def carregar() -> dict:
    """MK município × ciclo com S, Y1, Y2 e covariáveis (ciclo 2 pelo quadro de 13/02) e, para o portão do D-b, as
    bases do 40 com o quadro do ciclo 2 de 19/03 (o do 57l)."""
    cov, curso, info_cov = T44.construir_covariaveis()
    T44.UFS = sorted(cov["cd_uf"].unique().tolist())
    b = T44.bases_h1(cov, curso)
    MK, contagem = {}, {}
    for k in CICLOS:
        d = b["MK"][k].copy()
        ncel = d["n_cel_imed"].astype(float) + d["n_cel_cr"].astype(float)
        if (ncel < 1).any():
            raise FalhaValidacao(f"V{k}: municipio x ciclo sem celula no quadro")
        d["S"] = (d["n_cel_imed"] > 0).astype(float)
        for oid, spec in OUTCOMES.items():
            y = d[spec["col"]].astype(float)
            obs = np.isfinite(y.to_numpy())
            if not np.array_equal(obs, d["S"].to_numpy() == 1):
                raise FalhaValidacao(f"V{k}: {oid} observado fora de S = 1 ou ausente com S = 1")
        MK[k] = d
        contagem[f"V{k}"] = {"municipio_ciclo": int(len(d)), "com_vaga_imediata_S1": int((d["S"] == 1).sum()),
                             "so_cadastro_reserva_S0": int((d["S"] == 0).sum())}
    d19 = T40.carregar()["19mar"]
    return {"MK": MK, "CK": b["CK"], "b": b, "d19": d19, "d13": b["dados"], "info_cov": info_cov,
            "contagem": contagem}


def medias_lados(r: dict, y: np.ndarray, peso: np.ndarray | None = None) -> tuple[float, float]:
    """Média (ponderada por `peso`, se houver) do outcome nas linhas usadas de cada lado (= ND.medias_lados do 23b)."""
    if "_detalhes" not in r:
        return float("nan"), float("nan")
    d = r["_detalhes"]
    out = []
    for m in (d["usa"] & (d["x_mil"] <= 0), d["usa"] & (d["x_mil"] > 0)):
        if not m.any():
            out.append(float("nan"))
        elif peso is None:
            out.append(float(np.mean(y[m])))
        else:
            out.append(float(np.sum(peso[m] * y[m]) / np.sum(peso[m])))
    return out[0], out[1]


# ---------------------------------------------------------------------------
# 2. Portão
# ---------------------------------------------------------------------------

def _db_celula(CK: dict, c: int, ks: tuple) -> tuple[dict, np.ndarray]:
    a = T23.montar_amostra([(CK[k], c, f"c{k}") for k in ks], empilhada=True)       # = am_cel do 38
    y = 1.0 - a.col("tipo_vaga_imediata")
    r = L.rd_empilhado(a.s, y, a.c, grupo=a.g, h_mil=H, cluster=a.cl, ids_unidade=a.cl, detalhes=True)
    return r, medias_lados(r, y)


def _db_municipio(MK: dict, c: int, ks: tuple) -> tuple[dict, tuple]:
    partes = []
    for k in ks:
        d = MK[k].copy()
        n_cel = d["n_cel_imed"].astype(float) + d["n_cel_cr"].astype(float)
        d["frac_cel_so_cr"] = d["n_cel_cr"].astype(float) / n_cel
        partes.append((d, c, f"c{k}" if len(ks) > 1 else str(c)))                   # = am_mun do 38
    a = T23.montar_amostra(partes, empilhada=len(ks) > 1)
    y = a.col("frac_cel_so_cr")
    pw = np.where(np.isfinite(y), a.col("n_celulas"), np.nan)
    r = T23.ajustar(a, y, H, peso=pw)
    return r, medias_lados(r, y, pw)


def portao_db(d19: dict, d13: dict) -> dict:
    """D-b do 57l: reproduz com o quadro do ciclo 2 de 19/03 (o do 57l); relata a mesma medida com o de 13/02."""
    dq = pd.read_csv(DQ_EST, dtype={"corte": str, "ciclo": str}, low_memory=False)
    out = {"referencia": rotulo(DQ_EST), "sha256_referencia": sha256(DQ_EST), "tolerancia": TOL, "linhas": []}
    for c in CORTES:
        for ks in ((1,), (2,), (3,), CICLOS):
            cl = "+".join(str(k) for k in ks)
            for quant, fun, base in (("so_cr", _db_celula, "CK"), ("frac_cel_so_cr", _db_municipio, "MK")):
                ref = dq[(dq["explicacao"] == "D-b") & (dq["bloco"] == "composicao") & (dq["quantidade"] == quant)
                         & (dq["ciclo"] == cl) & (dq["corte"] == ROT_CORTE[c])]
                if len(ref) != 1:
                    raise FalhaValidacao(f"D-b {quant} {cl} {ROT_CORTE[c]}: {len(ref)} linhas de referencia")
                ref = ref.iloc[0]
                r19, (ma19, mc19) = fun(d19[base], c, ks)
                meu = {"tau": r19["tau"], "ep": r19["ep"], "n_abaixo": r19["n_abaixo"], "n_acima": r19["n_acima"],
                       "n_obs": r19["n_obs"], "media_abaixo": ma19, "media_acima": mc19}
                difs = {k: abs(float(v) - float(ref[k])) for k, v in meu.items()}
                ok = all(v <= TOL for v in difs.values())
                if not ok:
                    raise FalhaValidacao(f"portao D-b: {quant} ciclos {cl} em {TXT_CORTE[c]} nao reproduz o 57l: {difs}")
                r13, (ma13, mc13) = fun(d13[base], c, ks)
                out["linhas"].append({
                    "quantidade": quant, "ciclo": cl, "corte": ROT_CORTE[c], "reproduz": True,
                    "max_abs_dif": max(difs.values()),
                    "c2_19mar": {"tau": float(r19["tau"]), "ic95_inf": float(r19["ic95_inf"]),
                                 "ic95_sup": float(r19["ic95_sup"]), "media_abaixo": ma19, "media_acima": mc19,
                                 "n_abaixo": int(r19["n_abaixo"]), "n_acima": int(r19["n_acima"])},
                    "c2_13fev": {"tau": float(r13["tau"]), "ic95_inf": float(r13["ic95_inf"]),
                                 "ic95_sup": float(r13["ic95_sup"]), "media_abaixo": ma13, "media_acima": mc13,
                                 "n_abaixo": int(r13["n_abaixo"]), "n_acima": int(r13["n_acima"])}})
    out["max_abs_dif"] = max(x["max_abs_dif"] for x in out["linhas"])
    out["aprovado"] = True
    out["diferenca_de_definicao"] = (
        "o D-b do 57l mede a parte das celulas so de cadastro reserva (celula, ou fracao das celulas do municipio "
        "ponderada pelas celulas) com o quadro do ciclo 2 de 19/03/2026; o 48f mede S = municipio x ciclo com >= 1 "
        "celula com vaga imediata e usa, no ciclo 2, o quadro de 13/02/2026 (48b, par. 7)")
    return out


def portao(dados: dict) -> dict:
    p_hi = T44.portao_hi(dados["b"])
    p_db = portao_db(dados["d19"], dados["d13"])
    return {"hi": p_hi, "db": p_db, "aprovado": bool(p_hi["aprovado"] and p_db["aprovado"])}


# ---------------------------------------------------------------------------
# 3. Linhas
# ---------------------------------------------------------------------------

def nova_linha(linha: str, papel: str, tipo: str, outcome: str, desc: str, unidade_analise: str, amostra: str,
               ciclo: str, corte: int, janela: int, metodo: str, estimador: str, unidade: str, nota: str = "") -> dict:
    ln = {c: np.nan for c in COLUNAS}
    ln.update({"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "linha": linha, "papel": papel,
               "tipo_linha": tipo, "outcome": outcome, "descricao_outcome": desc, "unidade_analise": unidade_analise,
               "amostra": amostra, "ciclo": ciclo, "corte": ROT_CORTE[corte], "janela": janela / 1000.0,
               "metodo": metodo, "estimador": estimador, "status": "EXECUTADO", "lado_aparado": "",
               "ciclos_fora": "", "unidade": unidade, "nota": nota})
    ln["id_linha"] = "|".join([linha, tipo, outcome, ciclo, ROT_CORTE[corte], f"w={janela / 1000:.3f}"])
    return ln


EST_S = ("municipio x ciclo; local linear, kernel triangular, h = 0,050; intercepto e inclinacoes por ciclo x lado, "
         "salto comum; CR1 por municipio (ajustar do script 23)")
EST_CEL = ("celula (todas, qualquer tipo); local linear, kernel triangular, h = 0,050; intercepto e inclinacoes por "
           "ciclo x lado, salto comum; EF de curso x ciclo; CR1 por municipio (est_celula do script 40)")


def linhas_sv1(dados: dict) -> list[dict]:
    out = []
    for c in CORTES:
        a = T40.amostra(dados["MK"], CICLOS, c)
        y = a.col("S")
        r = T23.ajustar(a, y, H)
        ma, mc = medias_lados(r, y)
        ln = nova_linha("SV-1", "principal", "salto", "S", "municipio x ciclo com >= 1 celula com vaga imediata (so "
                        "imediata ou mista); ciclo 2 pelo quadro de 13/02/2026", "municipio x ciclo",
                        "todo municipio x ciclo com celula no quadro (qualquer tipo)", "1+2+3", c, H, "RDD", EST_S,
                        UN_FRAC)
        out.append(_preencher(ln, r, ma, mc))
        a = T40.amostra(dados["CK"], CICLOS, c)
        y = a.col("tipo_vaga_imediata")
        r = T40.est_celula(a, y)
        ma, mc = medias_lados(r, y)
        ln = nova_linha("SV-1", "principal", "salto", "CELULA_IMEDIATA", "celula tem vaga imediata (so imediata ou "
                        "mista); ciclo 2 pelo quadro de 13/02/2026", "celula", "todas as celulas do quadro (qualquer "
                        "tipo)", "1+2+3", c, H, "RDD", EST_CEL, UN_FRAC,
                        nota="n_abaixo/n_acima = municipios; n_obs = celulas")
        out.append(_preencher(ln, r, ma, mc))
    return out


def _preencher(ln: dict, r: dict, ma: float, mc: float) -> dict:
    for k in ("tau", "ep", "ic95_inf", "ic95_sup", "p_valor", "n_abaixo", "n_acima", "n_obs", "n_clusters"):
        if r.get(k) is not None:
            ln[k] = r[k]
    ln["media_abaixo"], ln["media_acima"] = ma, mc
    ln["nota"] = _juntar(ln["nota"], r.get("nota", ""))
    if not np.isfinite(_f(ln["tau"])):
        ln["status"] = "SEM_ESTIMATIVA"
    return ln


# ---------------------------------------------------------------------------
# 4. SV-2: balanço entre S = 1 e na amostra toda
# ---------------------------------------------------------------------------

def linhas_sv2(dados: dict) -> list[dict]:
    cl = pd.read_csv(CL_BAL, dtype={"corte": str})
    cl0 = cl[(cl["tipo"] == "salto_no_corte") & (cl["bloco"] == "CL-0")
             & (cl["populacao"] == "H1 (municipio x ciclo, amostra da HI-2)")]
    filtro_s1 = T40.filtro_coluna_positiva("n_cel_imed")
    out = []
    for c in CORTES:
        toda = T40.amostra(dados["MK"], CICLOS, c)
        s1 = T40.amostra(dados["MK"], CICLOS, c, filtro_s1)
        jan = L.pesos_kernel(L.normalizar_s_mil(toda.s) - toda.c, H) > 0
        for var in VARS_BAL:
            yt = T44._col_bal(toda.d, var)
            ok = jan & np.isfinite(yt)
            dp = float(np.std(yt[ok], ddof=1)) if ok.sum() > 1 else float("nan")
            for nome, a in (("S=1 (amostra da H1 / HI-2)", s1), ("amostra toda (todo municipio x ciclo do quadro)",
                                                                 toda)):
                y = T44._col_bal(a.d, var)
                r = T23.ajustar(a, y, H)
                ln = {k: np.nan for k in COLUNAS_BAL}
                ln.update({"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "linha": "SV-2", "amostra": nome,
                           "corte": ROT_CORTE[c], "janela": H / 1000, "variavel": var, "dp_janela_amostra_toda": dp,
                           "status": "EXECUTADO", "nota": r.get("nota", "") or "", "confere_cl0": ""})
                for k in ("tau", "ep", "ic95_inf", "ic95_sup", "p_valor", "n_abaixo", "n_acima", "n_obs"):
                    if r.get(k) is not None:
                        ln[k] = r[k]
                if not np.isfinite(_f(ln["tau"])):
                    ln["status"] = "SEM_ESTIMATIVA"
                else:
                    ln["ic_exclui_zero"] = bool(not (_f(ln["ic95_inf"]) <= 0.0 <= _f(ln["ic95_sup"])))
                    if np.isfinite(dp) and dp > 0:
                        ln["salto_padronizado"] = float(ln["tau"]) / dp
                if nome.startswith("S=1"):
                    ref = cl0[(cl0["corte"] == ROT_CORTE[c]) & (cl0["variavel"] == var)]
                    if len(ref) != 1:
                        raise FalhaValidacao(f"CL-0 sem linha unica para {var} em {ROT_CORTE[c]}")
                    dif = max(abs(_f(ln[k]) - _f(ref.iloc[0][k])) for k in ("tau", "ep"))
                    if not dif <= TOL:
                        raise FalhaValidacao(f"SV-2 entre S = 1 nao reproduz o CL-0 do 48d ({var}, {ROT_CORTE[c]}): {dif}")
                    ln["confere_cl0"] = "sim"
                out.append(ln)
    return out


# ---------------------------------------------------------------------------
# 5. Limites de Lee (§3 do adendo; decisões 9 a 21)
# ---------------------------------------------------------------------------

def _wmedia(y: np.ndarray, w: np.ndarray) -> float:
    sw = float(np.sum(w))
    return float(np.sum(w * y) / sw) if sw > 0 else float("nan")


def _reta(x: np.ndarray, y: np.ndarray, w: np.ndarray) -> tuple[float, np.ndarray] | None:
    """MQP de y em (1, x) com pesos w; devolve (intercepto em x = 0, resíduos). Menos de 2 x distintos: None."""
    if np.unique(x[w > 0]).size < 2:
        return None
    X = np.column_stack([np.ones(len(x)), x / 1000.0])
    sw = np.sqrt(w)
    beta = np.linalg.lstsq(X * sw[:, None], y * sw, rcond=None)[0]
    return float(beta[0]), y - X @ beta


def limites_lee_ciclo(x: np.ndarray, acima: np.ndarray, w: np.ndarray, s: np.ndarray, y: np.ndarray,
                      reta: bool = False) -> dict | None:
    """Limites de Lee num ciclo (§3 do adendo, passos 1 a 3), versão de randomização local.

    `w` = peso do kernel (× multiplicidade no bootstrap); `s` = seleção 0/1; `y` observado quando s = 1.
    Salto = acima − abaixo. Lado aparado = o de taxa de seleção maior; q = (p_maior − p_menor) / p_maior.
    Lado aparado de cima: limite inferior tira as de MAIOR y, superior as de MENOR y. Lado aparado de baixo: limite
    inferior tira as de MENOR y, superior as de MAIOR y. Com `reta=True` (SV-5), y é trocado pelos resíduos da reta de
    cada lado e o salto da reta (diferença dos interceptos) é somado. Sem unidade selecionada com peso positivo em
    algum lado, devolve None (ciclo fora, contado).
    """
    x, acima, w, s, y = (np.asarray(v, dtype=float) for v in (x, acima, w, s, y))
    acima = acima.astype(bool)
    wa_tot, wb_tot = float(np.sum(w[acima])), float(np.sum(w[~acima]))
    if wa_tot <= 0 or wb_tot <= 0:
        return None
    pa = float(np.sum(w[acima] * s[acima]) / wa_tot)
    pb = float(np.sum(w[~acima] * s[~acima]) / wb_tot)
    sel_a = acima & (s == 1) & (w > 0)
    sel_b = ~acima & (s == 1) & (w > 0)
    if not (sel_a.any() and sel_b.any()):
        return None
    if not (np.isfinite(y[sel_a]).all() and np.isfinite(y[sel_b]).all()):
        raise FalhaValidacao("Lee: unidade selecionada sem y")
    wa, wb = w[sel_a], w[sel_b]
    base = 0.0
    ya, yb = y[sel_a], y[sel_b]
    if reta:
        fa = _reta(x[sel_a], ya, wa)
        fb = _reta(x[sel_b], yb, wb)
        if fa is None or fb is None:
            return None
        base = fa[0] - fb[0]
        ya, yb = fa[1], fb[1]
    ma, mb = _wmedia(ya, wa), _wmedia(yb, wb)
    sem = base + ma - mb
    if pa > pb:
        lado, q = "acima", (pa - pb) / pa
    elif pb > pa:
        lado, q = "abaixo", (pb - pa) / pb
    else:
        lado, q = "nenhum", 0.0
    if lado == "acima":
        m_inf = L._multiplicador_aparo(ya, wa, q, True, EMPATES)      # tira as de maior y
        m_sup = L._multiplicador_aparo(ya, wa, q, False, EMPATES)     # tira as de menor y
        inf = base + _wmedia(ya, wa * m_inf) - mb
        sup = base + _wmedia(ya, wa * m_sup) - mb
    elif lado == "abaixo":
        m_inf = L._multiplicador_aparo(yb, wb, q, False, EMPATES)     # tira as de menor y (sobe a média de baixo)
        m_sup = L._multiplicador_aparo(yb, wb, q, True, EMPATES)      # tira as de maior y
        inf = base + ma - _wmedia(yb, wb * m_inf)
        sup = base + ma - _wmedia(yb, wb * m_sup)
    else:
        inf = sup = sem
    return {"p_acima": pa, "p_abaixo": pb, "q": q, "lado": lado, "inf": inf, "sup": sup, "sem_aparo": sem}


def _n_sel(mult: np.ndarray, s: np.ndarray, kern: np.ndarray) -> float:
    """Número de unidades com S = 1 e peso positivo (com multiplicidade no bootstrap): o peso do ciclo (decisão 15)."""
    return float(np.sum(mult[(s == 1) & (kern > 0) & (mult > 0)]))


def preparar(J: pd.DataFrame) -> dict:
    """Arrays por ciclo da janela (para não refazer a seleção de colunas a cada reamostra)."""
    P = {}
    for k in CICLOS:
        m = J["ciclo"].to_numpy() == k
        P[k] = {"m": m, "x": J["x"].to_numpy(float)[m], "acima": J["acima"].to_numpy(bool)[m],
                "kern": J["kern"].to_numpy(float)[m], "S": J["S"].to_numpy(float)[m]}
    return P


def lee_combinado(P: dict, y: np.ndarray, mult: np.ndarray, reta: bool) -> dict:
    """Limites por ciclo e combinação com pesos n_k (decisões 15 e 16)."""
    por, fora = {}, []
    for k in CICLOS:
        p = P[k]
        mk = mult[p["m"]]
        r = limites_lee_ciclo(p["x"], p["acima"], p["kern"] * mk, p["S"], y[p["m"]], reta)
        if r is None:
            fora.append(k)
            continue
        r["n_k"] = _n_sel(mk, p["S"], p["kern"])
        por[k] = r
    if not por:
        return {"por_ciclo": por, "fora": fora, "inf": np.nan, "sup": np.nan, "sem_aparo": np.nan,
                "p_acima": np.nan, "p_abaixo": np.nan, "q": np.nan, "lado": ""}
    nk = np.array([por[k]["n_k"] for k in por])
    pk = nk / nk.sum()
    comb = {c_: float(np.sum(pk * np.array([por[k][c_] for k in por])))
            for c_ in ("inf", "sup", "sem_aparo", "p_acima", "p_abaixo")}
    pa, pb = comb["p_acima"], comb["p_abaixo"]
    q = (max(pa, pb) - min(pa, pb)) / max(pa, pb) if max(pa, pb) > 0 else np.nan
    lado = "acima" if pa > pb else "abaixo" if pb > pa else "nenhum"
    for k, w_ in zip(por, pk):
        por[k]["peso"] = float(w_)
    return {"por_ciclo": por, "fora": fora, **comb, "q": q, "lado": lado}


def janela(dados: dict, c: int, w: int) -> pd.DataFrame:
    partes = []
    for k in CICLOS:
        d = dados["MK"][k]
        x = L.normalizar_s_mil(d["s_mil"].to_numpy(float)) - c
        kern = L.pesos_kernel(x, w)
        m = kern > 0
        partes.append(pd.DataFrame({"co_ibge": d.loc[m, "co_ibge"].astype(str).to_numpy(), "ciclo": k,
                                    "x": x[m], "acima": x[m] > 0, "kern": kern[m], "S": d.loc[m, "S"].to_numpy(float),
                                    **{oid: d.loc[m, spec["col"]].to_numpy(float) for oid, spec in OUTCOMES.items()}}))
    J = pd.concat(partes, ignore_index=True)
    if J.groupby("co_ibge")["acima"].nunique().max() > 1:
        raise FalhaValidacao("municipio dos dois lados do corte")
    return J


def bootstrap(J: pd.DataFrame, specs: list[tuple[str, bool]], n_boot: int = N_BOOT, semente: int = SEMENTE) -> dict:
    """Bootstrap em blocos de município, estratificado pelo lado (decisões 17 e 18). Um gerador novo com a semente
    por corte × janela; os mesmos sorteios para todos os (outcome, reta) de `specs`."""
    rng = np.random.default_rng(semente)
    lados = {}
    for lado in (False, True):
        muns = np.array(sorted(J.loc[J["acima"] == lado, "co_ibge"].unique()))
        pos = {m: i for i, m in enumerate(muns)}
        lados[lado] = (len(muns), np.array([pos.get(m, -1) for m in J["co_ibge"]]))
    acima = J["acima"].to_numpy()
    P = preparar(J)
    ys = {oid: J[oid].to_numpy(float) for oid in OUTCOMES}
    res = {sp: {"inf": [], "sup": [], "sem_aparo": []} for sp in specs}
    invalidas = {sp: 0 for sp in specs}
    for _ in range(n_boot):
        mult = np.zeros(len(J))
        for lado in (False, True):
            n, idx = lados[lado]
            cont = np.bincount(rng.integers(0, n, n), minlength=n).astype(float)
            m = acima == lado
            mult[m] = cont[idx[m]]
        for sp in specs:
            oid, reta = sp
            r = lee_combinado(P, ys[oid], mult, reta)
            if np.isfinite(r["inf"]) and np.isfinite(r["sup"]):
                for k in ("inf", "sup", "sem_aparo"):
                    res[sp][k].append(r[k])
            else:
                invalidas[sp] += 1
    return {sp: {**{k: np.array(v) for k, v in res[sp].items()}, "invalidas": invalidas[sp]} for sp in specs}


EST_LEE = ("municipio x ciclo com S = 1 na janela |IVS - corte| < h, peso = kernel triangular; taxas de selecao por "
           "lado e ciclo; aparo de q no lado de taxa maior (quantis ponderados, empates proporcionais); limites = "
           "diferenca de medias ponderadas (acima - abaixo); ciclos combinados pelo n de unidades com S = 1; IC de "
           "Imbens-Manski com EP de bootstrap em blocos de municipio (1.999, semente 20261026, estratificado pelo lado, "
           "aparo refeito em cada reamostra)")
EST_LEE_RETA = ("como o SV-3, mas com a reta de Y em IVS por ciclo x lado (MQP com o kernel) entre S = 1; aparo nos "
                "residuos; limite = salto da reta + diferenca das medias ponderadas dos residuos que ficaram")


def linhas_lee(dados: dict) -> tuple[list[dict], dict]:
    out, reg = [], {}
    for c in CORTES:
        for jan_w in sorted({v["janela"] for v in VERSOES.values()}, reverse=True):
            J = janela(dados, c, jan_w)
            versoes = [(lid, v) for lid, v in VERSOES.items() if v["janela"] == jan_w]
            specs = [(oid, v["reta"]) for _, v in versoes for oid in OUTCOMES]
            boot = bootstrap(J, specs)
            um = np.ones(len(J))
            P = preparar(J)
            reg[f"{ROT_CORTE[c]}|w={jan_w / 1000:.3f}"] = {
                "unidades_na_janela": int(len(J)), "municipios_abaixo": int(J.loc[~J["acima"], "co_ibge"].nunique()),
                "municipios_acima": int(J.loc[J["acima"], "co_ibge"].nunique()),
                "S1_abaixo": int(((J["S"] == 1) & ~J["acima"]).sum()), "S1_acima": int(((J["S"] == 1) & J["acima"]).sum())}
            for lid, v in versoes:
                for oid, spec in OUTCOMES.items():
                    r = lee_combinado(P, J[oid].to_numpy(float), um, v["reta"])
                    b = boot[(oid, v["reta"])]
                    out += _linhas_lee_uma(lid, v, oid, spec, c, jan_w, J, r, b)
                # taxas de seleção (uma vez por versão; iguais para Y1 e Y2 na mesma janela)
                if not v["reta"]:
                    r = lee_combinado(P, J["Y1"].to_numpy(float), um, False)
                    out += _linhas_taxa(lid, c, jan_w, J, r)
    return out, reg


def _linhas_taxa(lid: str, c: int, jan_w: int, J: pd.DataFrame, r: dict) -> list[dict]:
    out = []
    linha = "SV-1" if lid == "SV-3" else lid
    for k in list(CICLOS) + ["1+2+3"]:
        ln = nova_linha(linha, "principal" if linha == "SV-1" else "sensibilidade", "taxa_selecao", "S",
                        "taxa de selecao na janela (media de S ponderada pelo kernel, por lado)", "municipio x ciclo",
                        "todo municipio x ciclo com celula no quadro, na janela", str(k), c, jan_w,
                        "taxa de selecao (Lee, passo 1)", "media de S ponderada pelo kernel triangular em cada lado; "
                        "ciclos combinados pelo n de unidades com S = 1", UN_FRAC)
        if k == "1+2+3":
            m = np.ones(len(J), dtype=bool)
            ln.update({"p_acima": r["p_acima"], "p_abaixo": r["p_abaixo"], "q": r["q"], "lado_aparado": r["lado"],
                       "ciclos_fora": ";".join(str(x) for x in r["fora"])})
        else:
            m = (J["ciclo"] == k).to_numpy()
            pc = r["por_ciclo"].get(k)
            if pc is None:
                ln["status"], ln["nota"] = "SEM_ESTIMATIVA", "ciclo sem unidade com S = 1 e peso positivo em algum lado"
            else:
                ln.update({"p_acima": pc["p_acima"], "p_abaixo": pc["p_abaixo"], "q": pc["q"],
                           "lado_aparado": pc["lado"], "peso_ciclo": pc["peso"]})
        ln["n_abaixo"] = int(J.loc[m & ~J["acima"].to_numpy(), "co_ibge"].nunique())
        ln["n_acima"] = int(J.loc[m & J["acima"].to_numpy(), "co_ibge"].nunique())
        ln["n_obs"] = int(m.sum())
        ln["n_selecionados"] = int((m & (J["S"].to_numpy() == 1)).sum())
        out.append(ln)
    return out


def _linhas_lee_uma(lid: str, v: dict, oid: str, spec: dict, c: int, jan_w: int, J: pd.DataFrame, r: dict,
                    b: dict) -> list[dict]:
    est = EST_LEE_RETA if v["reta"] else EST_LEE
    out = []
    ln = nova_linha(lid, v["papel"], "limites_lee", oid, spec["desc"], "municipio x ciclo", "S = 1 na janela",
                    "1+2+3", c, jan_w, v["metodo"], est, spec["unidade"])
    sel = (J["S"] == 1).to_numpy()
    ln["n_abaixo"] = int(J.loc[sel & ~J["acima"].to_numpy(), "co_ibge"].nunique())
    ln["n_acima"] = int(J.loc[sel & J["acima"].to_numpy(), "co_ibge"].nunique())
    ln["n_obs"] = int(sel.sum())
    ln["n_selecionados"] = int(sel.sum())
    ln.update({"p_acima": r["p_acima"], "p_abaixo": r["p_abaixo"], "q": r["q"], "lado_aparado": r["lado"],
               "limite_inf": r["inf"], "limite_sup": r["sup"], "dif_sem_aparo": r["sem_aparo"],
               "ciclos_fora": ";".join(str(x) for x in r["fora"]), "n_reamostras": N_BOOT,
               "n_reamostras_validas": int(len(b["inf"]))})
    if not (np.isfinite(r["inf"]) and np.isfinite(r["sup"])):
        ln["status"], ln["nota"] = "SEM_ESTIMATIVA", "nenhum ciclo com S = 1 dos dois lados"
    elif len(b["inf"]) >= 2:
        ei, es = float(np.std(b["inf"], ddof=1)), float(np.std(b["sup"], ddof=1))
        em = float(np.std(b["sem_aparo"], ddof=1))
        lo, hi = T24.ic_imbens_manski(r["inf"], r["sup"], ei, es, ALFA)
        ln.update({"ep_limite_inf": ei, "ep_limite_sup": es, "ic_im_inf": lo, "ic_im_sup": hi,
                   "ep_dif_sem_aparo": em, "ic_sem_aparo_inf": r["sem_aparo"] - Z975 * em,
                   "ic_sem_aparo_sup": r["sem_aparo"] + Z975 * em})
    if b["invalidas"]:
        ln["nota"] = _juntar(ln["nota"], f"{b['invalidas']} reamostra(s) sem limite definido, descartadas")
    out.append(ln)
    for k in CICLOS:
        pc = r["por_ciclo"].get(k)
        lk = nova_linha(lid, v["papel"], "limites_lee_ciclo", oid, spec["desc"], "municipio x ciclo",
                        "S = 1 na janela (componente do ciclo, sem IC)", str(k), c, jan_w, v["metodo"], est,
                        spec["unidade"])
        m = (J["ciclo"] == k).to_numpy() & sel
        lk["n_abaixo"] = int(J.loc[m & ~J["acima"].to_numpy(), "co_ibge"].nunique())
        lk["n_acima"] = int(J.loc[m & J["acima"].to_numpy(), "co_ibge"].nunique())
        lk["n_obs"] = lk["n_selecionados"] = int(m.sum())
        if pc is None:
            lk["status"], lk["nota"] = "SEM_ESTIMATIVA", ("ciclo fora da combinacao: sem unidade com S = 1 e peso "
                                                          "positivo em algum lado" + (" ou sem 2 valores de x para a "
                                                                                     "reta" if v["reta"] else ""))
        else:
            lk.update({"p_acima": pc["p_acima"], "p_abaixo": pc["p_abaixo"], "q": pc["q"], "lado_aparado": pc["lado"],
                       "limite_inf": pc["inf"], "limite_sup": pc["sup"], "dif_sem_aparo": pc["sem_aparo"],
                       "peso_ciclo": pc["peso"]})
        out.append(lk)
    return out


# ---------------------------------------------------------------------------
# 6. Leituras (§4 do adendo; regras fixas, decisões 24 e 27 a 29)
# ---------------------------------------------------------------------------

def _uma(df: pd.DataFrame, **kw) -> pd.Series:
    m = np.ones(len(df), dtype=bool)
    for k, v in kw.items():
        m &= (df[k].astype(str) == str(v)).to_numpy()
    sel = df[m]
    if len(sel) != 1:
        raise FalhaValidacao(f"linha nao unica ({len(sel)}): {kw}")
    return sel.iloc[0]


def _contem_zero(lo, hi) -> bool:
    return _f(lo) <= 0.0 <= _f(hi)


def _taxa(est: pd.DataFrame, c: int, linha: str = "SV-1", w: int = H) -> pd.Series:
    return _uma(est, linha=linha, tipo_linha="taxa_selecao", ciclo="1+2+3", corte=ROT_CORTE[c], janela=w / 1000.0)


def _lee(est: pd.DataFrame, lid: str, oid: str, c: int) -> pd.Series:
    return _uma(est, linha=lid, tipo_linha="limites_lee", outcome=oid, corte=ROT_CORTE[c])


def leitura_sv1(est: pd.DataFrame) -> dict:
    out = {}
    for c in CORTES:
        s = _uma(est, linha="SV-1", tipo_linha="salto", outcome="S", corte=ROT_CORTE[c])
        cel = _uma(est, linha="SV-1", tipo_linha="salto", outcome="CELULA_IMEDIATA", corte=ROT_CORTE[c])
        q = _f(_taxa(est, c)["q"])
        if not _contem_zero(s["ic95_inf"], s["ic95_sup"]):
            cod = "TIPO_RESPONDE_AO_CORTE"
        elif q < LIMIAR_Q:
            cod = "SELECAO_PEQUENA"
        else:
            cod = "IC_CONTEM_ZERO_MAS_TAXAS_DIFEREM"
        out[ROT_CORTE[c]] = {"codigo": cod, "q": q, "ic_s_contem_zero": _contem_zero(s["ic95_inf"], s["ic95_sup"]),
                             "ic_celula_contem_zero": _contem_zero(cel["ic95_inf"], cel["ic95_sup"]),
                             "celula_discorda": _contem_zero(s["ic95_inf"], s["ic95_sup"]) != _contem_zero(
                                 cel["ic95_inf"], cel["ic95_sup"])}
    return out


def leitura_lee(est: pd.DataFrame) -> dict:
    out = {}
    for lid in VERSOES:
        for oid in OUTCOMES:
            for c in CORTES:
                r = _lee(est, lid, oid, c)
                if r["status"] != "EXECUTADO":
                    cod = "SEM_ESTIMATIVA"
                elif _contem_zero(r["limite_inf"], r["limite_sup"]):
                    cod = "NAO_SE_DETECTA_DIFERENCA"
                else:
                    cod = "INTERVALO_DE_UM_LADO_DO_ZERO"
                out[f"{lid}|{oid}|{ROT_CORTE[c]}"] = {
                    "codigo": cod, "intervalo_contem_zero": _contem_zero(r["limite_inf"], r["limite_sup"]),
                    "ic_im_contem_zero": _contem_zero(r["ic_im_inf"], r["ic_im_sup"]),
                    "sinal": ("" if cod != "INTERVALO_DE_UM_LADO_DO_ZERO" else
                              "positivo" if _f(r["limite_inf"]) > 0 else "negativo")}
    return out


def leitura_sv2(bal: pd.DataFrame) -> dict:
    out = {}
    for c in CORTES:
        sub = bal[bal["corte"].astype(str) == ROT_CORTE[c]]
        s1 = sub[sub["amostra"].str.startswith("S=1")]
        td = sub[sub["amostra"].str.startswith("amostra toda")]
        n1 = int(s1["ic_exclui_zero"].astype(str).str.lower().eq("true").sum())
        nt = int(td["ic_exclui_zero"].astype(str).str.lower().eq("true").sum())
        out[ROT_CORTE[c]] = {
            "codigo": "DESBALANCO_MAIOR_EM_S1" if n1 > nt else "DESBALANCO_NAO_MAIOR_EM_S1",
            "n_ic_sem_zero_S1": n1, "n_ic_sem_zero_toda": nt,
            "vars_ic_sem_zero_S1": s1.loc[s1["ic_exclui_zero"].astype(str).str.lower().eq("true"), "variavel"].tolist(),
            "vars_ic_sem_zero_toda": td.loc[td["ic_exclui_zero"].astype(str).str.lower().eq("true"),
                                            "variavel"].tolist(),
            "media_abs_padronizado_S1": float(np.nanmean(np.abs(s1["salto_padronizado"].astype(float)))),
            "media_abs_padronizado_toda": float(np.nanmean(np.abs(td["salto_padronizado"].astype(float))))}
    return out


def leituras(est: pd.DataFrame, bal: pd.DataFrame) -> dict:
    return {"sv1": leitura_sv1(est), "lee": leitura_lee(est), "sv2": leitura_sv2(bal),
            "regras": {
                "sv1": "IC 95% da RDD de S (municipio x ciclo) sem zero -> TIPO_RESPONDE_AO_CORTE; com zero e q < 0,05 "
                       "-> SELECAO_PEQUENA; com zero e q >= 0,05 -> IC_CONTEM_ZERO_MAS_TAXAS_DIFEREM (fora da tabela "
                       "do par. 4)",
                "lee": "[inf; sup] contem zero -> NAO_SE_DETECTA_DIFERENCA; inteiro de um lado -> "
                       "INTERVALO_DE_UM_LADO_DO_ZERO (sinal relatado como robusto a selecao, dizendo se o IC de "
                       "Imbens-Manski exclui zero)",
                "sv2": "n de covariaveis com IC 95% sem zero entre S = 1 > o da amostra toda -> DESBALANCO_MAIOR_EM_S1"}}


# ---------------------------------------------------------------------------
# 7. Formatação (pt-BR; a do 44)
# ---------------------------------------------------------------------------

fn, fp, fint, _tab = T44.fn, T44.fp, T44.fint, T44._tab


def _esc(unidade: str) -> tuple[float, int, str]:
    return (100.0, 1, " p.p.") if unidade == UN_FRAC else (1.0, 2, "")


def fv(r, col="tau") -> str:
    e, k, u = _esc(r["unidade"])
    return fn(e * _f(r[col]), k) + u


def fic(r, a="ic95_inf", b="ic95_sup") -> str:
    e, k, _ = _esc(r["unidade"])
    return f"[{fn(e * _f(r[a]), k)}; {fn(e * _f(r[b]), k)}]"


def fpct(x, casas=1) -> str:
    return fn(100.0 * _f(x), casas, sinal=False) + "%"


def bloco(nome: str, corpo: str) -> str:
    return f"<!-- SV:{nome}:inicio -->\n{corpo.rstrip()}\n<!-- SV:{nome}:fim -->"


LADO_TXT = {"acima": "de cima (bolsa maior)", "abaixo": "de baixo (bolsa menor)", "nenhum": "nenhum (taxas iguais)"}
NOME_Y = {oid: spec["nome"] for oid, spec in OUTCOMES.items()}


# ---------------------------------------------------------------------------
# 8. Blocos do doc 57t
# ---------------------------------------------------------------------------

def _frase_sv1(est: pd.DataFrame, c: int, le: dict) -> str:
    s = _uma(est, linha="SV-1", tipo_linha="salto", outcome="S", corte=ROT_CORTE[c])
    cel = _uma(est, linha="SV-1", tipo_linha="salto", outcome="CELULA_IMEDIATA", corte=ROT_CORTE[c])
    t = _taxa(est, c)
    x = le["sv1"][ROT_CORTE[c]]
    return (f"chance de o município × ciclo ter vaga imediata: salto {fv(s)} (IC 95% {fic(s)}; abaixo do corte, "
            f"{fpct(s['media_abaixo'])} dos municípios × ciclo têm); chance de a célula ter vaga imediata: {fv(cel)} "
            f"(IC {fic(cel)}); na janela, {fpct(t['p_abaixo'])} abaixo e {fpct(t['p_acima'])} acima, q = "
            f"{fn(t['q'], 3, False)} (código `{x['codigo']}`)")


def _frase_lee(r, le_cod: dict) -> str:
    e, k, u = _esc(r["unidade"])
    if r["status"] != "EXECUTADO":
        return "sem estimativa"
    return (f"limites [{fn(e * _f(r['limite_inf']), k)}; {fn(e * _f(r['limite_sup']), k)}]{u} (IC de Imbens–Manski "
            f"[{fn(e * _f(r['ic_im_inf']), k)}; {fn(e * _f(r['ic_im_sup']), k)}]; sem aparo {fn(e * _f(r['dif_sem_aparo']), k)}"
            f"{u}; código `{le_cod['codigo']}`)")


def _frase_ciclos(est: pd.DataFrame) -> str:
    """Taxas por ciclo: o q dos ciclos juntos pode esconder diferenças de sentido oposto entre ciclos."""
    fr = []
    for c in CORTES:
        qs, lados = [], {"acima": [], "abaixo": []}
        for k in CICLOS:
            r = _uma(est, linha="SV-1", tipo_linha="taxa_selecao", ciclo=str(k), corte=ROT_CORTE[c])
            if r["status"] == "EXECUTADO":
                qs.append(_f(r["q"]))
                if r["lado_aparado"] in lados:
                    lados[r["lado_aparado"]].append(str(k))
        t = _taxa(est, c)
        muda = bool(lados["acima"]) and bool(lados["abaixo"])
        fr.append(f"em {TXT_CORTE[c]}, q vai de {fn(min(qs), 3, False)} a {fn(max(qs), 3, False)} nos ciclos (ciclos "
                  f"juntos: {fn(t['q'], 3, False)})"
                  + (f", e o lado com mais vaga imediata muda de ciclo para ciclo (de cima no(s) ciclo(s) "
                     f"{', '.join(lados['acima'])}; de baixo no(s) ciclo(s) {', '.join(lados['abaixo'])}): as "
                     "diferenças se compensam ao juntar os ciclos" if muda else
                     f", sempre com mais vaga imediata do lado {'de cima' if lados['acima'] else 'de baixo'}"))
    txt = ("**Por ciclo.** " + "; ".join(fr)[0].upper() + "; ".join(fr)[1:] + ". Os limites de Lee aparam com o q "
           "de cada ciclo, não com o dos ciclos juntos; a regra do §4 usa o dos ciclos juntos (decisão 16).")
    # Auditoria 44, achado 1: "seleção pequena" pelo q dos ciclos juntos não quer dizer pequena dentro do ciclo.
    pequenos = [TXT_CORTE[c] for c in CORTES if _q_ciclos_max(est, c) >= LIMIAR_Q and _f(_taxa(est, c)["q"]) < LIMIAR_Q]
    if pequenos:
        txt += (f" Por isso, em {', '.join(pequenos)}, o código `SELECAO_PEQUENA` vem da regra fixada antes das contas "
                "e **não** quer dizer que a seleção seja pequena dentro de cada ciclo. O 48b compara dentro do ciclo "
                "(intercepto e inclinações por ciclo), e uma seleção de um sentido num ciclo e do outro sentido em outro "
                "não se anula necessariamente na H1. O que protege a H1 da seleção nesse corte são os limites de Lee, que aparam com o q "
                "de cada ciclo.")
    return txt


def _q_ciclos_max(est: pd.DataFrame, c: int) -> float:
    qs = [_f(_uma(est, linha="SV-1", tipo_linha="taxa_selecao", ciclo=str(k), corte=ROT_CORTE[c])["q"])
          for k in CICLOS]
    qs = [q for q in qs if np.isfinite(q)]
    return max(qs) if qs else float("nan")


def _nota_sens(est: pd.DataFrame, lid: str, oid: str, c: int, le: dict) -> str:
    """Peso de uma sensibilidade que muda de leitura (auditoria 44, achado 2)."""
    x = le["lee"][f"{lid}|{oid}|{ROT_CORTE[c]}"]
    txt = ". Pela decisão 29 isso não muda a leitura do SV-3"
    if x["codigo"] == "INTERVALO_DE_UM_LADO_DO_ZERO":
        r = _lee(est, lid, oid, c)
        e, k, u = _esc(r["unidade"])
        perto = _f(r["limite_sup"]) if x["sinal"] == "negativo" else _f(r["limite_inf"])
        txt += (f"; o limite mais perto de zero fica em {fn(e * perto, k)}{u}"
                + (", e, com o IC de Imbens–Manski contendo zero, o sinal não se distingue do acaso"
                   if x["ic_im_contem_zero"] else ""))
    if lid == "SV-5":
        r3, r5 = _lee(est, "SV-3", oid, c), _lee(est, "SV-5", oid, c)
        e, k, u = _esc(r5["unidade"])
        txt += (f". O SV-5 tira a reta de Y no IVS, como a HI-1 e a HI-2 do 48b: a diferença sem aparo passa de "
                f"{fn(e * _f(r3['dif_sem_aparo']), k)}{u} (SV-3, sem a reta) para {fn(e * _f(r5['dif_sem_aparo']), k)}{u}; "
                "a leitura do SV-3 depende da hipótese de randomização local na janela (seção 9)")
        if oid == "Y2":
            ref = _p_holm_hi()
            hi2 = _referencia_hi2(c)
            if np.sign(hi2) == np.sign(_f(r5["dif_sem_aparo"])):
                txt += (f". O sentido é o da HI-2 do 48b nesse corte ({fn(hi2, 2)} médicos por município, p Holm "
                        f"{fp(ref[(ROT_CORTE[c], 'HI-2')])}), em outra escala")
    return txt


def _referencia_hi2(c: int) -> float:
    hi = pd.read_csv(HI_EST, dtype={"corte": str, "ciclo": str}, low_memory=False)
    return _f(T40._uma(hi, linha="HI-2", outcome="HI-2", variante="principal", corte=ROT_CORTE[c])["tau"])


def _p_holm_hi() -> dict:
    """p de Holm das quatro primárias do 48b (só lido de HI_estimativas.csv; auditoria 44)."""
    hi = pd.read_csv(HI_EST, dtype={"corte": str, "ciclo": str}, low_memory=False)
    return {(ROT_CORTE[c], oid): _f(T40._uma(hi, linha=oid, outcome=oid, variante="principal",
                                             corte=ROT_CORTE[c])["p_holm"])
            for c in CORTES for oid in ("HI-1", "HI-2")}


def resposta_curta(est: pd.DataFrame, bal: pd.DataFrame, resumo: dict) -> str:
    le = resumo["leitura"]
    partes = []
    cods1 = {ct: le["sv1"][ct]["codigo"] for ct in le["sv1"]}
    resp = []
    for c in CORTES:
        cod = cods1[ROT_CORTE[c]]
        ressalva = ""
        if cod == "SELECAO_PEQUENA" and _q_ciclos_max(est, c) >= LIMIAR_Q:      # auditoria 44, achado 1
            ressalva = (". Isso vale só com os ciclos juntos: dentro de cada ciclo as taxas diferem mais (q de até "
                        f"{fn(_q_ciclos_max(est, c), 3, False)}; ver \"Por ciclo\")")
        resp.append(f"em {TXT_CORTE[c]}, " + {
            "TIPO_RESPONDE_AO_CORTE": "o tipo de vaga **responde ao corte** (o IC do salto de S exclui zero): a amostra "
                                      "só com vagas imediatas é selecionada, e os limites de Lee pesam mais",
            "SELECAO_PEQUENA": "a seleção pelo tipo de vaga é **pequena** (IC do salto de S com zero e q < 0,05): o "
                               "48b não é muito afetado por ela",
            "IC_CONTEM_ZERO_MAS_TAXAS_DIFEREM": "não se detecta salto no tipo de vaga (IC de S com zero), mas as taxas "
                                                "de seleção na janela **diferem** (q ≥ 0,05): a seleção não é pequena "
                                                "o bastante para ser ignorada, e os limites de Lee pesam mais",
        }[cod] + ressalva)
    partes.append("**O tipo de vaga responde ao corte? (SV-1)** Pela regra pré-registrada, " + "; ".join(resp) + ".")
    partes += [f"- **Corte {TXT_CORTE[c]}** ({BOLSA[c]}): {_frase_sv1(est, c, le)}." for c in CORTES]
    partes.append(_frase_ciclos(est))
    lee = []
    for c in CORTES:
        for oid in OUTCOMES:
            r = _lee(est, "SV-3", oid, c)
            lee.append(f"- **{TXT_CORTE[c]}, {NOME_Y[oid]}:** {_frase_lee(r, le['lee'][f'SV-3|{oid}|{ROT_CORTE[c]}'])}.")
    cods3 = [le["lee"][f"SV-3|{oid}|{ROT_CORTE[c]}"]["codigo"] for c in CORTES for oid in OUTCOMES]
    if all(x == "NAO_SE_DETECTA_DIFERENCA" for x in cods3):
        cab = ("**Limites de Lee (SV-3, principal).** Nos dois cortes e nos dois outcomes, o intervalo identificado "
               "contém zero: mesmo sem supor nada sobre como o Ministério escolheu o tipo de vaga (além da "
               "monotonicidade), **não se detecta diferença de preenchimento no corte**. O intervalo é largo, e não "
               "detectar não é mostrar que a diferença é zero.")
    else:
        um_lado = [f"{NOME_Y[oid]} em {TXT_CORTE[c]}" for c in CORTES for oid in OUTCOMES
                   if le["lee"][f"SV-3|{oid}|{ROT_CORTE[c]}"]["codigo"] == "INTERVALO_DE_UM_LADO_DO_ZERO"]
        cab = ("**Limites de Lee (SV-3, principal).** O intervalo identificado fica inteiro de um lado do zero em "
               + ", ".join(um_lado) + ": pela leitura pré-registrada, esse sinal é relatado como robusto à seleção "
               "pelo tipo de vaga, para o pacote do corte (ver se o IC de Imbens–Manski também exclui zero, abaixo). "
               "Nos demais, o intervalo contém zero e não se detecta diferença.")
    partes.append(cab)
    partes += lee
    ref = resumo["referencia_hi"]
    ph = _p_holm_hi()                                                       # auditoria 44, achado 4
    partes.append("Para referência (outra conta: célula com a reta, e médicos por município com controle das vagas), a "
                  "H1 do 48b é " + "; ".join(
                      f"em {TXT_CORTE[c]}, HI-1 {fn(100 * ref[ROT_CORTE[c]]['HI-1']['tau'], 1)} p.p. "
                      f"[{fn(100 * ref[ROT_CORTE[c]]['HI-1']['ic95_inf'], 1)}; "
                      f"{fn(100 * ref[ROT_CORTE[c]]['HI-1']['ic95_sup'], 1)}] (p Holm {fp(ph[(ROT_CORTE[c], 'HI-1')])}) e "
                      f"HI-2 {fn(ref[ROT_CORTE[c]]['HI-2']['tau'], 2)} [{fn(ref[ROT_CORTE[c]]['HI-2']['ic95_inf'], 2)}; "
                      f"{fn(ref[ROT_CORTE[c]]['HI-2']['ic95_sup'], 2)}] (p Holm {fp(ph[(ROT_CORTE[c], 'HI-2')])})"
                      for c in CORTES) + "."
                  + (" Nenhuma das quatro rejeita zero depois do Holm do 48b." if min(ph.values()) >= ALFA else ""))
    s2 = le["sv2"]
    fr2 = []
    for c in CORTES:
        x = s2[ROT_CORTE[c]]
        fr2.append(f"{'em' if fr2 else 'Em'} {TXT_CORTE[c]}, {x['n_ic_sem_zero_S1']} covariável(is) com IC sem zero entre S = 1 contra "
                   f"{x['n_ic_sem_zero_toda']} na amostra toda (`{x['codigo']}`)")
    partes.append("**Balanço (SV-2).** " + "; ".join(fr2) + ".")
    sens = []
    for lid in ("SV-4", "SV-5"):
        difere = [f"{NOME_Y[oid]} em {TXT_CORTE[c]}" for c in CORTES for oid in OUTCOMES
                  if le["lee"][f"{lid}|{oid}|{ROT_CORTE[c]}"]["codigo"] != le["lee"][f"SV-3|{oid}|{ROT_CORTE[c]}"][
                      "codigo"]]
        det = []
        for c in CORTES:
            for oid in OUTCOMES:
                if le["lee"][f"{lid}|{oid}|{ROT_CORTE[c]}"]["codigo"] != le["lee"][f"SV-3|{oid}|{ROT_CORTE[c]}"]["codigo"]:
                    r = _lee(est, lid, oid, c)
                    det.append(f"{NOME_Y[oid]} em {TXT_CORTE[c]}: {_frase_lee(r, le['lee'][f'{lid}|{oid}|{ROT_CORTE[c]}'])}"
                               + (", com IC de Imbens–Manski que contém zero" if le["lee"][
                                   f"{lid}|{oid}|{ROT_CORTE[c]}"]["ic_im_contem_zero"] else "")
                               + _nota_sens(est, lid, oid, c, le))
        sens.append(f"{lid} ({'janela 0,020' if lid == 'SV-4' else 'com a reta'}): "
                    + ("mesma leitura do SV-3 em tudo" if not difere else "leitura diferente da do SV-3 em "
                       + "; ".join(det)))
    partes.append("**Sensibilidades.** " + "; ".join(sens) + ".")
    partes.append("Tudo depende da premissa de monotonicidade (seção 9) e se refere ao pacote do corte, não à bolsa "
                  "isolada. O principal da H1 continua o 48b.")
    return "\n\n".join(partes)


def tab_portao(resumo: dict, est: pd.DataFrame) -> str:
    p = resumo["portao"]
    linhas = [[x["linha"], T44._corte_txt(x["corte"]), fn(x["tau_csv"], 6), fn(x["tau_44"], 6),
               f"{x['max_abs_dif']:.1e}", "sim" if x["reproduz"] else "não"] for x in p["hi"]["linhas"]]
    t1 = _tab(["Linha do 48b", "Corte", "Salto em HI_estimativas.csv", "Salto refeito aqui", "máx. dif. absoluta",
               "Reproduz"], linhas)
    nome_q = {"so_cr": "célula só de CR (célula)", "frac_cel_so_cr": "parte das células só de CR (municípios)"}
    linhas = []
    for x in p["db"]["linhas"]:
        a, b = x["c2_19mar"], x["c2_13fev"]
        linhas.append([nome_q[x["quantidade"]], x["ciclo"], T44._corte_txt(x["corte"]),
                       f"{fpct(a['media_abaixo'])} / {fpct(a['media_acima'])}",
                       f"{fn(100 * a['tau'], 1)} p.p. [{fn(100 * a['ic95_inf'], 1)}; {fn(100 * a['ic95_sup'], 1)}]",
                       f"{x['max_abs_dif']:.1e}",
                       f"{fpct(b['media_abaixo'])} / {fpct(b['media_acima'])}",
                       f"{fn(100 * b['tau'], 1)} p.p. [{fn(100 * b['ic95_inf'], 1)}; {fn(100 * b['ic95_sup'], 1)}]"])
    t2 = _tab(["Medida do D-b", "Ciclos", "Corte", "Abaixo / acima (19/03, como no 57l)", "Salto [IC 95%] (19/03)",
               "máx. dif. contra o 57l", "Abaixo / acima (13/02)", "Salto [IC 95%] (13/02)"], linhas)
    return (t1 + f"\n\nResultado: **reproduz** (máx. dif. {p['hi']['max_abs_dif']:.1e}).\n\n" + t2
            + f"\n\nResultado: as {len(p['db']['linhas'])} linhas do D-b com o quadro de 19/03 **reproduzem** o 57l "
              f"(máx. dif. {p['db']['max_abs_dif']:.1e}). **Diferença de definição:** o D-b mede a parte das células "
              "só de cadastro reserva com o quadro do ciclo 2 de 19/03/2026; o 48f mede S (município × ciclo com "
              "alguma vaga imediata) e usa no ciclo 2 o quadro de 13/02/2026. As colunas \"13/02\" mostram a mesma "
              "medida do D-b com o quadro de 13/02 (descritivo). \"Abaixo / acima\" são as médias simples (célula) "
              "ou ponderadas pelas células (municípios) nas linhas usadas de cada lado da janela."
            + _reconciliar_db(p, est))


def _reconciliar_db(p: dict, est: pd.DataFrame) -> str:
    """Por que o D-b do 57l mostrava salto no tipo de vaga e o SV-1 não (auditoria 44, achado 3). Descritivo."""
    fr = []
    for c in CORTES:
        x = [l for l in p["db"]["linhas"] if l["quantidade"] == "so_cr" and l["ciclo"] == "1+2+3"
             and l["corte"] == ROT_CORTE[c]][0]
        a, b = x["c2_19mar"], x["c2_13fev"]
        cel = _uma(est, linha="SV-1", tipo_linha="salto", outcome="CELULA_IMEDIATA", corte=ROT_CORTE[c])
        fr.append(f"em {TXT_CORTE[c]}, a parte das células só de CR salta {fn(100 * a['tau'], 1)} p.p. "
                  f"[{fn(100 * a['ic95_inf'], 1)}; {fn(100 * a['ic95_sup'], 1)}] com o quadro de 19/03 e "
                  f"{fn(100 * b['tau'], 1)} p.p. [{fn(100 * b['ic95_inf'], 1)}; {fn(100 * b['ic95_sup'], 1)}] com o de "
                  f"13/02, sem efeitos fixos; com efeitos fixos de curso × ciclo (linha da célula do SV-1), o salto na "
                  f"parte só de CR é {fn(-100 * _f(cel['tau']), 1)} p.p. [{fn(-100 * _f(cel['ic95_sup']), 1)}; "
                  f"{fn(-100 * _f(cel['ic95_inf']), 1)}]")
    return ("\n\n**Por que o D-b mostrava salto no tipo de vaga e o SV-1 não (auditoria 44).** Na célula, ter vaga "
            "imediata é 1 menos ser só de CR, então as duas medidas são a mesma com o sinal trocado. Com os ciclos "
            "juntos, " + "; ".join(fr) + ". Duas coisas mudam do 57l para cá: o quadro do ciclo 2 (o de 19/03 foi refeito "
            "depois do resultado preliminar) e a comparação dentro do mesmo curso e ciclo, que reduz o salto: a parte só "
            "de CR varia por curso, e a mistura de cursos não é a mesma dos dois lados do corte (descritivo). A linha principal do SV-1, S, é outra margem: o município × ciclo ter alguma vaga imediata.")


def tab_amostra(resumo: dict) -> str:
    cc = resumo["amostra"]["contagem"]
    t1 = _tab(["Ciclo", "Município × ciclo no quadro (com IVS oficial)", "Com vaga imediata (S = 1)",
               "Só cadastro reserva (S = 0; Y ausente)"],
              [[str(k), fint(cc[f"V{k}"]["municipio_ciclo"]), fint(cc[f"V{k}"]["com_vaga_imediata_S1"]),
                fint(cc[f"V{k}"]["so_cadastro_reserva_S0"])] for k in CICLOS])
    jj = resumo["amostra"]["janelas"]
    linhas = []
    for chave, x in jj.items():
        ct, w = chave.split("|")
        linhas.append([T44._corte_txt(ct), fn(float(w[2:]), 3, False), fint(x["unidades_na_janela"]),
                       f"{x['municipios_abaixo']} / {x['municipios_acima']}", f"{x['S1_abaixo']} / {x['S1_acima']}"])
    t2 = _tab(["Corte", "Janela", "Município × ciclo na janela", "Municípios abaixo / acima",
               "Município × ciclo com S = 1 abaixo / acima"], linhas)
    return (t1 + "\n\nNa janela de cada corte (peso do kernel triangular positivo), ciclos 1–3 juntos:\n\n" + t2)


def tab_sv1(est: pd.DataFrame) -> str:
    linhas = []
    for c in CORTES:
        for oid, nome in (("S", "município × ciclo tem vaga imediata (S)"),
                          ("CELULA_IMEDIATA", "célula tem vaga imediata (EF de curso × ciclo)")):
            r = _uma(est, linha="SV-1", tipo_linha="salto", outcome=oid, corte=ROT_CORTE[c])
            linhas.append([nome, TXT_CORTE[c], f"{fint(r['n_abaixo'])} / {fint(r['n_acima'])}", fint(r["n_obs"]),
                           f"{fpct(r['media_abaixo'])} / {fpct(r['media_acima'])}", fv(r), fic(r), fp(r["p_valor"])])
    t1 = _tab(["Outcome", "Corte", "Municípios abaixo / acima", "Linhas", "Média abaixo / acima (linhas usadas)",
               "Salto", "IC 95% (CR1)", "p"], linhas)
    linhas = []
    for c in CORTES:
        for k in list(CICLOS) + ["1+2+3"]:
            r = _uma(est, linha="SV-1", tipo_linha="taxa_selecao", ciclo=str(k), corte=ROT_CORTE[c])
            if r["status"] != "EXECUTADO":
                linhas.append([TXT_CORTE[c], str(k), "—", "—", "—", "—", "—"])
                continue
            linhas.append([TXT_CORTE[c], "combinados" if k == "1+2+3" else str(k),
                           f"{fint(r['n_abaixo'])} / {fint(r['n_acima'])}", fpct(r["p_abaixo"]), fpct(r["p_acima"]),
                           fn(r["q"], 3, False), LADO_TXT.get(r["lado_aparado"], r["lado_aparado"])])
    t2 = _tab(["Corte", "Ciclo", "Municípios abaixo / acima", "p_abaixo", "p_acima", "q", "Lado aparado"], linhas)
    return (t1 + "\n\nTaxas de seleção na janela de 0,050 (média de S ponderada pelo kernel triangular, por lado; os "
                 "ciclos combinados com o peso de cada ciclo no número de municípios × ciclo com S = 1):\n\n" + t2)


def tab_sv2(bal: pd.DataFrame, resumo: dict) -> str:
    linhas = []
    for c in CORTES:
        sub = bal[bal["corte"].astype(str) == ROT_CORTE[c]]
        for var in VARS_BAL:
            g = sub[sub["variavel"] == var]
            s1 = g[g["amostra"].str.startswith("S=1")].iloc[0]
            td = g[g["amostra"].str.startswith("amostra toda")].iloc[0]
            linhas.append([TXT_CORTE[c], ROT_BAL.get(var, var),
                           f"{fn(td['tau'], 3)} [{fn(td['ic95_inf'], 3)}; {fn(td['ic95_sup'], 3)}]",
                           fn(td["salto_padronizado"], 2),
                           f"{fn(s1['tau'], 3)} [{fn(s1['ic95_inf'], 3)}; {fn(s1['ic95_sup'], 3)}]",
                           fn(s1["salto_padronizado"], 2)])
    t = _tab(["Corte", "Covariável", "Amostra toda: salto [IC 95%]", "Amostra toda: em DP",
              "S = 1: salto [IC 95%]", "S = 1: em DP"], linhas)
    le = resumo["leitura"]["sv2"]
    fr = []
    for c in CORTES:
        x = le[ROT_CORTE[c]]
        fr.append(f"Em {TXT_CORTE[c]}: IC sem zero em {x['n_ic_sem_zero_S1']} covariável(is) entre S = 1 ("
                  + (", ".join(ROT_BAL.get(v, v) for v in x["vars_ic_sem_zero_S1"]) or "nenhuma") + ") e em "
                  f"{x['n_ic_sem_zero_toda']} na amostra toda ("
                  + (", ".join(ROT_BAL.get(v, v) for v in x["vars_ic_sem_zero_toda"]) or "nenhuma")
                  + f"); média do |salto em DP| {fn(x['media_abs_padronizado_S1'], 2, False)} entre S = 1 e "
                  f"{fn(x['media_abs_padronizado_toda'], 2, False)} na amostra toda. Código `{x['codigo']}`.")
    return (t + "\n\n\"Em DP\" = salto ÷ desvio-padrão da covariável na janela da amostra toda (o mesmo denominador nas "
                "duas colunas). As linhas de S = 1 são as do CL-0 do 48d (amostra da HI-2), conferidas contra "
                "`CL_balanco.csv`.\n\n" + "\n\n".join(fr))


def tab_lee(est: pd.DataFrame, lids: tuple) -> str:
    linhas = []
    for lid in lids:
        for c in CORTES:
            for oid in OUTCOMES:
                r = _lee(est, lid, oid, c)
                e, k, u = _esc(r["unidade"])
                lim = (f"[{fn(e * _f(r['limite_inf']), k)}; {fn(e * _f(r['limite_sup']), k)}]{u}"
                       if r["status"] == "EXECUTADO" else "sem estimativa")
                im = (f"[{fn(e * _f(r['ic_im_inf']), k)}; {fn(e * _f(r['ic_im_sup']), k)}]"
                      if np.isfinite(_f(r["ic_im_inf"])) else "—")
                sem = (f"{fn(e * _f(r['dif_sem_aparo']), k)}{u} [{fn(e * _f(r['ic_sem_aparo_inf']), k)}; "
                       f"{fn(e * _f(r['ic_sem_aparo_sup']), k)}]" if np.isfinite(_f(r["ic_sem_aparo_inf"])) else "—")
                linhas.append([lid, TXT_CORTE[c], NOME_Y[oid], f"{fint(r['n_abaixo'])} / {fint(r['n_acima'])}",
                               fn(r["q"], 3, False), LADO_TXT.get(r["lado_aparado"], r["lado_aparado"]), sem, lim, im,
                               f"{fint(r['n_reamostras_validas'])} / {fint(r['n_reamostras'])}",
                               r["ciclos_fora"] if isinstance(r["ciclos_fora"], str) and r["ciclos_fora"] else "—"])
    t = _tab(["Linha", "Corte", "Outcome", "Municípios com S = 1 abaixo / acima", "q (ciclos juntos)",
              "Lado de taxa maior (ciclos juntos)",
              "Sem aparo [IC 95%]", "Limites de Lee", "IC 95% Imbens–Manski", "Reamostras válidas", "Ciclos fora"],
             linhas)
    linhas = []
    for lid in lids:
        for c in CORTES:
            for oid in OUTCOMES:
                for kk in CICLOS:
                    r = _uma(est, linha=lid, tipo_linha="limites_lee_ciclo", outcome=oid, ciclo=str(kk),
                             corte=ROT_CORTE[c])
                    e, k, u = _esc(r["unidade"])
                    if r["status"] != "EXECUTADO":
                        linhas.append([lid, TXT_CORTE[c], NOME_Y[oid], str(kk), "—", "—", "—", "—", "—"])
                        continue
                    linhas.append([lid, TXT_CORTE[c], NOME_Y[oid], str(kk),
                                   f"{fpct(r['p_abaixo'])} / {fpct(r['p_acima'])}", fn(r["q"], 3, False),
                                   fn(r["peso_ciclo"], 2, False), f"{fn(e * _f(r['dif_sem_aparo']), k)}{u}",
                                   f"[{fn(e * _f(r['limite_inf']), k)}; {fn(e * _f(r['limite_sup']), k)}]{u}"])
    t2 = _tab(["Linha", "Corte", "Outcome", "Ciclo", "p_abaixo / p_acima", "q", "Peso do ciclo", "Sem aparo",
               "Limites do ciclo"], linhas)
    return t + "\n\nComponentes por ciclo (sem IC; o limite do corte é a média ponderada deles):\n\n" + t2


def leitura_txt(resumo: dict, est: pd.DataFrame) -> str:
    le = resumo["leitura"]
    out = []
    txt1 = {"TIPO_RESPONDE_AO_CORTE": "o tipo de vaga responde ao corte (ou a algo que muda nele): a amostra do 48b é "
                                      "selecionada; dar peso aos limites de SV-3",
            "SELECAO_PEQUENA": "a seleção pelo tipo de vaga é pequena no corte; o 48b não é muito afetado por ela",
            "IC_CONTEM_ZERO_MAS_TAXAS_DIFEREM": "caso fora da tabela do §4: não se detecta salto no tipo de vaga, mas "
                                                "as taxas de seleção na janela diferem (q ≥ 0,05); dar peso aos "
                                                "limites de SV-3"}
    for c in CORTES:
        x = le["sv1"][ROT_CORTE[c]]
        out.append(f"- **SV-1, {TXT_CORTE[c]}:** `{x['codigo']}` — {txt1[x['codigo']]}."
                   + (" A linha da célula discorda da do município quanto a conter zero (relatado, não muda a leitura)."
                      if x["celula_discorda"] else "")
                   + (f" Ressalva (auditoria 44): o q que entra na regra é o dos ciclos juntos; dentro de cada ciclo ele "
                      f"chega a {fn(_q_ciclos_max(est, c), 3, False)}, e os limites de Lee usam o de cada ciclo."
                      if x["codigo"] == "SELECAO_PEQUENA" and _q_ciclos_max(est, c) >= LIMIAR_Q else ""))
    for c in CORTES:
        for oid in OUTCOMES:
            x = le["lee"][f"SV-3|{oid}|{ROT_CORTE[c]}"]
            if x["codigo"] == "NAO_SE_DETECTA_DIFERENCA":
                t = ("os dois limites e o IC de Imbens–Manski contêm zero: mesmo sem supor nada sobre como o Ministério "
                     "escolheu o tipo (além da monotonicidade), não se detecta diferença de preenchimento no corte"
                     if x["ic_im_contem_zero"] else "o intervalo identificado contém zero")
            elif x["codigo"] == "INTERVALO_DE_UM_LADO_DO_ZERO":
                t = (f"o intervalo identificado fica inteiro do lado {x['sinal']} do zero: sinal relatado como robusto "
                     "à seleção pelo tipo de vaga, com o pacote do corte; o IC de Imbens–Manski "
                     + ("contém zero (o sinal não se distingue do acaso)" if x["ic_im_contem_zero"] else
                        "também exclui zero"))
            else:
                t = "sem estimativa"
            out.append(f"- **SV-3, {TXT_CORTE[c]}, {NOME_Y[oid]}:** `{x['codigo']}` — {t}.")
    for c in CORTES:
        x = le["sv2"][ROT_CORTE[c]]
        out.append(f"- **SV-2, {TXT_CORTE[c]}:** `{x['codigo']}` — "
                   + ("a restrição a vagas imediatas piora a comparabilidade no corte" if x["codigo"] ==
                      "DESBALANCO_MAIOR_EM_S1" else "a restrição a vagas imediatas não aumenta o número de covariáveis "
                                                    "desbalanceadas no corte") + ".")
    for lid in ("SV-4", "SV-5"):
        cods = ", ".join(f"{NOME_Y[oid].split(' ·')[0]} {TXT_CORTE[c]}: `{le['lee'][f'{lid}|{oid}|{ROT_CORTE[c]}']['codigo']}`"
                         for c in CORTES for oid in OUTCOMES)
        out.append(f"- **{lid} (sensibilidade):** {cods}.")
    return ("Regras fixadas no código antes de rodar (decisões 24 e 27 a 29):\n\n" + "\n".join(out))


def limites_txt(resumo: dict) -> str:
    lim = [
        "**Premissa de monotonicidade (Lee, 2009).** Os limites supõem que o corte muda a chance de um município ter "
        "vaga imediata **numa só direção para todos**: se do lado de cima a chance é maior, nenhum município que teria "
        "vaga imediata abaixo do corte deixaria de tê-la acima (e vice-versa). Com isso, os municípios com vaga "
        "imediata do lado de taxa maior são os que teriam vaga de qualquer jeito mais um excesso, e aparar esse "
        "excesso nas duas pontas de Y dá o pior e o melhor caso. A premissa **não é testável** com estes dados; é "
        "relatada. Se o Ministério deu vaga imediata a alguns municípios por estarem acima do corte e tirou de outros "
        "pelo mesmo motivo, os limites não valem. **Para quem vale o intervalo:** para os municípios × ciclo que "
        "teriam vaga imediata dos dois lados do corte (os \"sempre selecionados\" de Lee), não para todo município "
        "com vaga imediata.",
        "**Pós-resultado.** A H1 do 48b e o salto da parte de células só de reserva (57l) já tinham sido vistos. As "
        "regras foram congeladas antes destas contas, mas a pergunta não é cega ao resultado.",
        "**Pacote do corte.** Em 0,300 e 0,400 mudam a bolsa e outras regras federais (auditoria 18). Nada aqui isola "
        "o incentivo de R$ 5 mil.",
        "**Randomização local.** O SV-3 e o SV-4 comparam médias ponderadas dentro da janela, sem a reta: supõem que, "
        "perto do corte, Y não varia com o IVS entre os selecionados. O SV-5 tira a reta de cada lado e mostra o que "
        "muda; a HI-1 e a HI-2 do 48b usam a reta.",
        "**Escalas diferentes das do 48b.** Y1 é a fração das células com vaga imediata do município (cada município × "
        "ciclo pesa igual), não a célula da HI-1; Y2 é médicos por vaga imediata, não médicos por município com "
        "controle das vagas (HI-2). As figuras põem a HI ao lado como referência, não como a mesma conta.",
        "**Células mistas.** A base não diz em que tipo de vaga cada alocado entrou: nas células mistas contam todos "
        "os alocados da célula (limite herdado do 48b).",
        "**Poucos municípios e mesmo município em ciclos diferentes.** A janela tem poucas unidades com vaga imediata "
        "de cada lado; o bootstrap sorteia municípios inteiros (todas as suas linhas município × ciclo), por isso "
        "a dependência entre ciclos do mesmo município entra no EP. O IC de Imbens–Manski usa EP de bootstrap e não "
        "leva em conta a incerteza de q além da que o bootstrap capta ao refazer a aparagem.",
        "**Combinação dos ciclos.** Os limites são calculados dentro de cada ciclo e combinados pelo número de "
        "unidades com S = 1; os limites de cada ciclo estão na seção 5. A monotonicidade é usada dentro de cada "
        "ciclo: o sentido da seleção pode mudar de um ciclo para outro (seção 3), mas dentro do ciclo tem de valer "
        "para todos os municípios. Juntar os ciclos num só conjunto, com um q só, exigiria o mesmo sentido em todos "
        "os ciclos, o que os dados não mostram em todos os cortes (seção 3). A troca de sentido entre ciclos também é compatível com "
        "acaso: cada ciclo tem poucos municípios na janela, e o lado aparado em cada ciclo é o da taxa estimada.",
        "**q dos ciclos juntos.** A regra \"q < 0,05\" do §4 é aplicada ao q dos ciclos juntos (decisão 16). Quando "
        "os ciclos têm seleção em sentidos opostos, esse q fica pequeno mesmo com q grande em cada ciclo; por isso "
        "o q de cada ciclo é relatado ao lado e é ele que entra nos limites.",
    ]
    return "\n".join(f"- {x}" for x in lim)


def gerar_blocos(est: pd.DataFrame, bal: pd.DataFrame, resumo: dict) -> dict[str, str]:
    figs = "\n\n".join(f"![{Path(f['arquivo']).stem}](../../{f['arquivo']})\n\n**{f['como_ler']}**"
                       for f in resumo["figuras"])
    sv45 = tab_lee(est, ("SV-4", "SV-5"))
    t4 = []
    for c in CORTES:
        r = _taxa(est, c, "SV-4", H_SV4)
        t4.append(f"{TXT_CORTE[c]}: {fpct(r['p_abaixo'])} abaixo e {fpct(r['p_acima'])} acima, q = {fn(r['q'], 3, False)}")
    return {
        "resposta_curta": resposta_curta(est, bal, resumo),
        "portao": tab_portao(resumo, est),
        "amostra": tab_amostra(resumo),
        "sv1": tab_sv1(est),
        "sv2": tab_sv2(bal, resumo),
        "sv3": tab_lee(est, ("SV-3",)),
        "sv4_sv5": ("Taxas de seleção na janela de 0,020 (ciclos combinados): " + "; ".join(t4) + ".\n\n" + sv45),
        "leitura": leitura_txt(resumo, est),
        "figuras": figs,
        "limites": limites_txt(resumo),
    }


MARCA = re.compile(r"<!-- SV:(?P<nome>[A-Za-z0-9_]+):inicio -->\n(?P<corpo>.*?)\n?<!-- SV:(?P=nome):fim -->", re.S)


def atualizar_doc(est: pd.DataFrame, bal: pd.DataFrame, resumo: dict) -> None:
    txt = DOC.read_text(encoding="utf-8")
    blocos = gerar_blocos(est, bal, resumo)
    achados = {m.group("nome") for m in MARCA.finditer(txt)}
    falta = set(blocos) - achados
    if falta:
        raise FalhaValidacao(f"doc 57t sem os marcadores {sorted(falta)}")
    txt = MARCA.sub(lambda m: bloco(m.group("nome"), blocos[m.group("nome")]) if m.group("nome") in blocos
                    else m.group(0), txt)
    DOC.write_text(txt, encoding="utf-8")


# ---------------------------------------------------------------------------
# 9. Figuras
# ---------------------------------------------------------------------------

AZUL, LARANJA, CINZA, TINTA, TINTA2 = T44.AZUL, T44.LARANJA, T44.CINZA, T44.TINTA, T44.TINTA2
VERDE = T44.VERDE
FONTE = ("Fonte: outcomes do 12 (ciclos 1–3; ciclo 2 pelo quadro de 13/02/2026), IVS 2010 oficial (a08), HI_estimativas "
         "(48b). EMPIRICO · scripts/rdd_bolsa/46_selecao_tipo_vaga.py")
COMO_LER = {
    "SV_taxa_selecao.png": (
        "Como ler: em cada corte, a altura da barra é a parte dos municípios × ciclo perto do corte (janela de 0,050, "
        "com mais peso para quem está mais perto) que têm alguma vaga imediata. Azul: lado de bolsa menor; laranja: "
        "lado de bolsa maior. Se as barras de um par têm alturas diferentes, a chance de ter vaga imediata difere "
        "entre os lados na janela (pode ser acaso: cada ciclo tem poucos municípios), e a comparação só entre "
        "municípios com vaga imediata pode juntar grupos diferentes. O q de cada ciclo é a parte que os limites de "
        "Lee aparam no lado mais alto daquele ciclo; o q de \"juntos\" só entra na regra de leitura do §4."),
    "SV_limites_lee.png": (
        "Como ler: a barra grossa vai do limite inferior ao superior de Lee (o salto no corte, lado de bolsa maior "
        "menos o de bolsa menor, que vale qualquer que tenha sido a regra do Ministério para o tipo de vaga, se ela "
        "empurra todos na mesma direção); a linha fina é o IC 95% de Imbens–Manski. Ponto com barra fina: diferença "
        "sem aparo e H1 do 48b com IC 95%, como referência (outra conta). Faixa que cruza o zero: não se detecta "
        "diferença, o que não quer dizer que ela seja zero. Pacote do corte, não só a bolsa."),
}


def _plt():
    return T44._plt()


def _rodape(fig, texto: str, W: float, H_: float, largura: int = 150) -> None:
    T44._rodape(fig, texto, W, H_, largura)
    # A fonte do 44 é trocada pela deste script.
    for t in fig.texts:
        if t.get_text() == T44.FONTE:
            t.set_text(FONTE)


def figura_taxas(est: pd.DataFrame, destino: Path) -> None:
    plt = _plt()
    W, H_ = 14.0, 6.4
    fig = plt.figure(figsize=(W, H_))
    fig.text(0.1 / W, (H_ - 0.12) / H_, "Parte dos municípios × ciclo com vaga imediata, de cada lado do corte "
             "(janela de 0,050)", fontsize=14, weight="bold", va="top")
    for j, c in enumerate(CORTES):
        ax = fig.add_axes([(0.9 + j * 6.9) / W, 1.75 / H_, 5.9 / W, 3.6 / H_])
        rot, pa, pb, qs = [], [], [], []
        for k in list(CICLOS) + ["1+2+3"]:
            r = _uma(est, linha="SV-1", tipo_linha="taxa_selecao", ciclo=str(k), corte=ROT_CORTE[c])
            rot.append("juntos" if k == "1+2+3" else f"ciclo {k}")
            pb.append(100 * _f(r["p_abaixo"]))
            pa.append(100 * _f(r["p_acima"]))
            qs.append(_f(r["q"]))
        xs = np.arange(len(rot))
        ax.bar(xs - 0.2, pb, 0.38, color=AZUL, label="abaixo do corte (bolsa menor)")
        ax.bar(xs + 0.2, pa, 0.38, color=LARANJA, label="acima do corte (bolsa maior)")
        for i in range(len(rot)):
            for dx, v in ((-0.2, pb[i]), (0.2, pa[i])):
                if np.isfinite(v):
                    ax.text(xs[i] + dx, v + 1.5, fn(v, 0, False), ha="center", fontsize=9.5, color=TINTA)
        ax.set_xticks(xs)
        ax.set_xticklabels([f"{r_}\nq = {fn(q_, 2, False)}" if np.isfinite(q_) else r_ for r_, q_ in zip(rot, qs)],
                           fontsize=10)
        ax.set_ylim(0, 108)
        ax.set_ylabel("% com vaga imediata", fontsize=10)
        s = _uma(est, linha="SV-1", tipo_linha="salto", outcome="S", corte=ROT_CORTE[c])
        ax.set_title(f"Corte {TXT_CORTE[c]} ({BOLSA[c]}) · salto de S na RDD: {fv(s)} {fic(s)}", fontsize=11,
                     loc="left", weight="bold")
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)
        if j == 0:
            ax.legend(fontsize=9.5, frameon=False, loc="upper left")
    _rodape(fig, COMO_LER[destino.name], W, H_, 160)
    fig.savefig(destino, dpi=170, facecolor="white", metadata={"Software": None})
    plt.close(fig)


def _floresta_lee(ax, itens: list[dict], titulo: str, eixo: str) -> None:
    n = len(itens)
    vals = [0.0] + [v for it in itens for v in (it["lo"], it["hi"], it.get("a", np.nan), it.get("b", np.nan))
                    if np.isfinite(v)]
    lo, hi = min(vals), max(vals)
    pad = 0.08 * (hi - lo if hi > lo else 1.0)
    ax.set_xlim(lo - pad, hi + pad)
    ax.set_ylim(n - 0.5, -0.5)
    ax.axvline(0, color="#2b2b2b", lw=1.1)
    for i, it in enumerate(itens):
        if it["tipo"] == "lee":
            ax.plot([it["lo"], it["hi"]], [i, i], color=it["cor"], lw=1.4)
            ax.plot([it["a"], it["b"]], [i, i], color=it["cor"], lw=7, solid_capstyle="butt")
        else:
            ax.plot([it["lo"], it["hi"]], [i, i], color=it["cor"], lw=1.8)
            ax.scatter([it["tau"]], [i], s=45, color=it["cor"], edgecolor="white", zorder=3)
        ax.text(-0.02, i, it["rot"], transform=ax.get_yaxis_transform(), ha="right", va="center", fontsize=9.5)
        ax.text(1.02, i, it["valor"], transform=ax.get_yaxis_transform(), ha="left", va="center", fontsize=9)
    ax.set_yticks([])
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.set_title(titulo, fontsize=10.5, loc="left", color=TINTA, weight="bold")
    ax.set_xlabel(eixo, fontsize=9.5, color=TINTA2)
    ax.tick_params(axis="x", labelsize=9)


def _it_lee(r, rot: str, cor: str) -> dict:
    e, k, _ = _esc(r["unidade"])
    if r["status"] != "EXECUTADO":
        return {"tipo": "ponto", "rot": rot, "tau": np.nan, "lo": np.nan, "hi": np.nan, "cor": CINZA,
                "valor": "sem estimativa"}
    a, b = e * _f(r["limite_inf"]), e * _f(r["limite_sup"])
    lo, hi = e * _f(r["ic_im_inf"]), e * _f(r["ic_im_sup"])
    return {"tipo": "lee", "rot": rot, "a": a, "b": b, "lo": lo, "hi": hi, "cor": cor,
            "valor": f"[{fn(a, k)}; {fn(b, k)}] · IC [{fn(lo, k)}; {fn(hi, k)}]"}


def _it_ponto(tau, lo, hi, rot: str, unidade: str) -> dict:
    e, k, _ = _esc(unidade)
    cor = CINZA if _contem_zero(lo, hi) else AZUL
    return {"tipo": "ponto", "rot": rot, "tau": e * _f(tau), "lo": e * _f(lo), "hi": e * _f(hi), "cor": cor,
            "valor": f"{fn(e * _f(tau), k)} [{fn(e * _f(lo), k)}; {fn(e * _f(hi), k)}]"}


def figura_lee(est: pd.DataFrame, hi: pd.DataFrame, destino: Path) -> None:
    plt = _plt()
    W, H_ = 16.6, 10.6
    fig = plt.figure(figsize=(W, H_))
    fig.text(0.1 / W, (H_ - 0.12) / H_, "Limites de Lee para o salto da H1 no corte, ao lado da H1 do adendo 48b",
             fontsize=14, weight="bold", va="top")
    for j, c in enumerate(CORTES):
        x0 = 2.7 + j * 8.1
        p1, p2 = [], []
        for oid, lst in (("Y1", p1), ("Y2", p2)):
            for lid, rot, cor in (("SV-3", "Lee (SV-3, janela 0,050)", VERDE), ("SV-4", "Lee (SV-4, janela 0,020)",
                                                                                 LARANJA),
                                  ("SV-5", "Lee com a reta (SV-5)", "#7a4fb5")):
                lst.append(_it_lee(_lee(est, lid, oid, c), rot, cor))
            r = _lee(est, "SV-3", oid, c)
            lst.append(_it_ponto(r["dif_sem_aparo"], r["ic_sem_aparo_inf"], r["ic_sem_aparo_sup"],
                                 "sem aparo (S = 1)", r["unidade"]))
        h1 = T40._uma(hi, linha="HI-1", outcome="HI-1", variante="principal", corte=ROT_CORTE[c])
        h2 = T40._uma(hi, linha="HI-2", outcome="HI-2", variante="principal", corte=ROT_CORTE[c])
        p1.append(_it_ponto(h1["tau"], h1["ic95_inf"], h1["ic95_sup"], "HI-1 do 48b (célula)", UN_FRAC))
        p3 = [_it_ponto(h2["tau"], h2["ic95_inf"], h2["ic95_sup"], "HI-2 do 48b", "medicos por municipio")]
        y = H_ - 0.95
        for its, tit, eixo in (
                (p1, f"Corte {TXT_CORTE[c]} ({BOLSA[c]})\nY1 · fração das células com vaga imediata preenchidas",
                 "salto no corte (p.p.)"),
                (p2, "Y2 · médicos alocados por vaga imediata", "salto no corte (médicos por vaga imediata)"),
                (p3, "HI-2 do 48b · médicos por município (controle das vagas)",
                 "salto no corte (médicos por município)")):
            h = 0.42 * len(its)
            y0 = y - 0.75 - h
            ax = fig.add_axes([x0 / W, y0 / H_, 3.0 / W, h / H_])
            _floresta_lee(ax, its, tit, eixo)
            y = y0 - 0.6
    _rodape(fig, COMO_LER[destino.name], W, H_, 170)
    fig.savefig(destino, dpi=170, facecolor="white", metadata={"Software": None})
    plt.close(fig)


def gerar_figuras(est: pd.DataFrame) -> list[dict]:
    DIR_FIG.mkdir(parents=True, exist_ok=True)
    hi = pd.read_csv(HI_EST, dtype={"corte": str, "ciclo": str}, low_memory=False)
    feitas = []
    nome = "SV_taxa_selecao.png"
    figura_taxas(est, DIR_FIG / nome)
    feitas.append({"arquivo": rotulo(DIR_FIG / nome), "como_ler": COMO_LER[nome],
                   "fonte": "SV_estimativas.csv: SV-1 (taxa_selecao, janela 0,050; salto de S)"})
    nome = "SV_limites_lee.png"
    figura_lee(est, hi, DIR_FIG / nome)
    feitas.append({"arquivo": rotulo(DIR_FIG / nome), "como_ler": COMO_LER[nome],
                   "fonte": "SV_estimativas.csv: SV-3, SV-4, SV-5 (limites_lee); HI_estimativas.csv: HI-1 e HI-2 "
                            "principais (48b)"})
    return feitas


# ---------------------------------------------------------------------------
# 10. Resumo, gravação e execução
# ---------------------------------------------------------------------------

def entradas() -> list[dict]:
    arqs = [ADENDO, HI_EST, CL_BAL, DQ_EST, T44.A08, T44.POP22, T44.PAINEL, T44.MANIF_A09, T44.CIR_BRUTO,
            T44.CIR_MANIF, T44.REF_IBGE, T44.REF_MANIF, T23.ARQ_VC, T23.ARQ_VM, T40.ARQ_C2_13FEV,
            T23.ARQ_U, T23.E6.ARQ_G3]       # U e G3: lidos por E6.chaves_populacoes (auditoria 44)
    return [{"arquivo": rotulo(p), "sha256": sha256(p)} for p in arqs]


def montar_resumo(est, bal, dados, port, reg) -> dict:
    return {
        "etapa": "Adendo 48f: selecao pelo tipo de vaga na H1 (SV-1 a SV-5)",
        "natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "data_execucao": DATA_EXECUCAO,
        "script": "scripts/rdd_bolsa/46_selecao_tipo_vaga.py",
        "adendo": {"arquivo": rotulo(ADENDO), "sha256": sha256(ADENDO), "commit_congelamento": COMMIT_CONGELAMENTO,
                   "commit_decisoes_57t": COMMIT_DECISOES},
        "contraste": CONTRASTE,
        "salto": "lado com bolsa maior (IVS acima do corte) menos lado com bolsa menor; o corte fica no lado de baixo",
        "parametros": {"cortes": [0.300, 0.400], "h": H / 1000, "janela_sv4": H_SV4 / 1000, "n_bootstrap": N_BOOT,
                       "semente": SEMENTE, "tolerancia_portao": TOL, "limiar_q": LIMIAR_Q, "empates_aparo": EMPATES,
                       "bootstrap": "blocos de municipio, estratificado pelo lado do corte; gerador novo com a semente "
                                    "por corte x janela; mesmos sorteios para Y1, Y2, SV-3 e SV-5",
                       "ic": "Imbens e Manski (2004), funcao ic_imbens_manski do script 24"},
        "premissa": ("monotonicidade (Lee, 2009): o corte muda a chance de ter vaga imediata numa so direcao para todos "
                     "os municipios; nao testavel; relatada"),
        "entradas": entradas(),
        "portao": port,
        "amostra": {"contagem": dados["contagem"], "janelas": reg},
        "leitura": leituras(est, bal),
        "contagens": {"linhas": int(len(est)), "por_linha": est["linha"].value_counts().sort_index().to_dict(),
                      "por_status": est["status"].value_counts().sort_index().to_dict(),
                      "linhas_balanco": int(len(bal))},
        "integridade": {"ivs": "IVS 2010 oficial (a08); o arquivo local de IVS da auditoria 16 nao e lido",
                        "cnes": "covariaveis do 44: competencias 202406-202506; nenhuma >= 202609",
                        "imputacao": "nada imputado; Y de unidade com S = 0 fica ausente, nunca zero",
                        "dados": "nada escrito em data/", "saidas_nao_regravadas": ["HI_*", "CL_*", "DQ_*"]},
        "saidas": {"estimativas": rotulo(OUT / NOME_EST), "balanco": rotulo(OUT / NOME_BAL),
                   "resumo": rotulo(OUT / NOME_RESUMO), "figuras": rotulo(DIR_FIG), "doc": rotulo(DOC)},
        "linguagem": "pacote do corte; 'nao se detecta' nao e 'zero'; nada de 'a bolsa reduz'",
        "referencia_hi": referencia_hi(),
    }


def referencia_hi() -> dict:
    """HI-1 e HI-2 principais do 48b (só lidas de HI_estimativas.csv), para pôr ao lado dos limites."""
    hi = pd.read_csv(HI_EST, dtype={"corte": str, "ciclo": str}, low_memory=False)
    return {ROT_CORTE[c]: {oid: {k: float(T40._uma(hi, linha=oid, outcome=oid, variante="principal",
                                                   corte=ROT_CORTE[c])[k]) for k in ("tau", "ic95_inf", "ic95_sup")}
                           for oid in ("HI-1", "HI-2")} for c in CORTES}


def gravar(est: pd.DataFrame, bal: pd.DataFrame, resumo: dict) -> None:
    est.to_csv(OUT / NOME_EST, index=False)
    bal.to_csv(OUT / NOME_BAL, index=False)
    (OUT / NOME_RESUMO).write_text(json.dumps(_nan_none(resumo), ensure_ascii=False, indent=1) + "\n",
                                   encoding="utf-8")


def ler_saidas() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    est = pd.read_csv(OUT / NOME_EST, dtype={"corte": str, "ciclo": str, "lado_aparado": str, "ciclos_fora": str})
    for c in ("lado_aparado", "ciclos_fora", "nota"):
        est[c] = est[c].fillna("")
    bal = pd.read_csv(OUT / NOME_BAL, dtype={"corte": str, "confere_cl0": str})
    for c in ("nota", "confere_cl0"):
        bal[c] = bal[c].fillna("")
    return est, bal, json.loads((OUT / NOME_RESUMO).read_text(encoding="utf-8"))


def executar(atualizar: bool) -> int:
    if sha256(ADENDO) != SHA_ADENDO:
        raise FalhaValidacao("o adendo 48f mudou depois do congelamento")
    print("Bases: covariáveis L e M e H1 municipal (script 44; ciclo 2 pelo quadro de 13/02/2026)...", flush=True)
    dados = carregar()
    print("Portão: HI-1 e HI-2 do 48b e D-b do 57l...", flush=True)
    port = portao(dados)
    print(f"  reproduz (HI máx |dif| = {port['hi']['max_abs_dif']:.1e}; D-b máx |dif| = "
          f"{port['db']['max_abs_dif']:.1e})", flush=True)
    print("SV-1 e SV-2...", flush=True)
    linhas = linhas_sv1(dados)
    bal = pd.DataFrame(linhas_sv2(dados)).reindex(columns=COLUNAS_BAL)
    print("SV-3 a SV-5 (limites de Lee, bootstrap de 1.999 reamostras)...", flush=True)
    lee, reg = linhas_lee(dados)
    est = pd.DataFrame(linhas + lee).reindex(columns=COLUNAS)
    if est["id_linha"].duplicated().any():
        raise FalhaValidacao(f"id_linha duplicado: {est.loc[est['id_linha'].duplicated(), 'id_linha'].tolist()}")
    est.to_csv(OUT / NOME_EST, index=False)
    bal.to_csv(OUT / NOME_BAL, index=False)
    # Leitura, figuras e doc a partir do que foi gravado (o teste refaz tudo de output/).
    est = pd.read_csv(OUT / NOME_EST, dtype={"corte": str, "ciclo": str, "lado_aparado": str, "ciclos_fora": str})
    for c in ("lado_aparado", "ciclos_fora", "nota"):
        est[c] = est[c].fillna("")
    bal = pd.read_csv(OUT / NOME_BAL, dtype={"corte": str, "confere_cl0": str})
    for c in ("nota", "confere_cl0"):
        bal[c] = bal[c].fillna("")
    resumo = montar_resumo(est, bal, dados, port, reg)
    resumo["figuras"] = gerar_figuras(est)
    gravar(est, bal, resumo)
    est, bal, resumo = ler_saidas()
    if atualizar:
        atualizar_doc(est, bal, resumo)
        print(f"Doc regravado: {rotulo(DOC)}")
    print(f"Gravado: {rotulo(OUT / NOME_EST)} ({len(est)} linhas), {NOME_BAL}, {NOME_RESUMO}, {rotulo(DIR_FIG)}/")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--atualizar-doc", action="store_true", help="regrava os blocos do doc 57t")
    ap.add_argument("--so-doc", action="store_true", help="só regrava os blocos do doc 57t a partir das saídas")
    args = ap.parse_args(argv)
    try:
        if args.so_doc:
            atualizar_doc(*ler_saidas())
            return 0
        return executar(args.atualizar_doc)
    except (FalhaValidacao, T44.FalhaValidacao, T40.FalhaValidacao) as erro:
        print(f"FALHA (nada gravado): {erro}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
