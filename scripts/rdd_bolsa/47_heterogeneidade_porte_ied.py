"""Adendo 48g: heterogeneidade do salto no corte entre os portes em que o estrato do IED muda e os em que não muda.

Adendo congelado antes das contas: `docs/06_execucao/48g_adendo_heterogeneidade_porte_ied.md` (26/10/2026, commit
c87ed75; SHA-256 conferido abaixo). Estatuto de toda saída: `ADENDO_48G_POS_RESULTADO`; `natureza_dos_dados =
EMPIRICO`. Decisões de implementação: seção 0 de `docs/06_execucao/57u_resultados_heterogeneidade_porte.md`,
registradas em commit (808db3a) antes de qualquer estimativa.

O que faz
---------
1. Portão (antes de qualquer conta nova; falha fechada, nada é gravado):
   - G por corte LIDO de `a10_diagnostico_cortes_normas.json` (código de IVS de cada lado do corte pelas faixas do IVS
     oficial; estrato por código × porte; G = 1 no porte em que o estrato muda); o a10 CSV confere com a regra e com o
     IVS oficial (a08) dos municípios na janela;
   - HI-1 e HI-2 do 48b (script 40) e OC-A1 do protocolo 64 (script 43) em 0,300, com as funções de base e com o
     estimador desta análise sem a divisão por grupo, contra `HI_estimativas.csv` e `OC_estimativas.csv` (≤ 1e−8).
2. PO-1 (primária, Holm entre 4): τ₁ = salto onde o estrato muda − salto onde não muda, para HI-1 e HI-2, por corte.
   `rd_empilhado` com grupo = ciclo × G, salto comum T (τ₀) e T × G (τ₁), mais o que a base já tem (EF de curso ×
   ciclo na HI-1; controle das vagas imediatas com coeficiente por ciclo na HI-2); CR1 por município.
3. PO-2 (ΔB1, ΔB2) e PO-3 (ΔB5, generalistas): τ₁ por corte em V, grupo = G, HC1; BKY entre as 6.
4. PO-4 (descritiva): τ₀ e τ₀ + τ₁ por outcome e corte, da mesma regressão.
5. PO-5 (diagnóstico): contagens por grupo × lado × corte na janela e balanço de capital e região por grupo.
6. Leitura do §4 por regra fixada no código; figura com "Como ler"; blocos `<!-- PO:... -->` do doc 57u.

Integridade: nada simulado, imputado ou adquirido; nada escrito em `data/`; a running variable é o IVS 2010 oficial
(a08), lido pelas funções dos scripts 40 e 43; nenhuma competência do CNES ≥ 202609 (conferido); `HI_*`, `OC_*`,
`CL_*` e `PM_*` não são regravados.

Uso
---
    python3 scripts/rdd_bolsa/47_heterogeneidade_porte_ied.py                  # calcula, grava e regrava o doc
    python3 scripts/rdd_bolsa/47_heterogeneidade_porte_ied.py --atualizar-doc  # só regrava os blocos do doc 57u
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


# O 44 importa o 40 e o 43 com estes nomes; importar com os mesmos nomes reaproveita os módulos (um só 40, um só 43).
T40 = _importar(DIR_RDD / "40_h1_vagas_imediatas.py", "h1_vagas_imediatas_para_cl")
T43 = _importar(DIR_RDD / "43_oferta_local_corte.py", "oferta_local_corte_para_cl")
T44 = _importar(DIR_RDD / "44_controles_localizacao_medicos.py", "controles_localizacao_medicos_para_po")
T23 = T40.T23
L = T40.L

# ---------------------------------------------------------------------------
# Parâmetros do adendo (constantes permitidas: cortes, h, limiar de contagem, rótulos)
# ---------------------------------------------------------------------------

OUT = ROOT / "output" / "rdd_bolsa"
AQ = ROOT / "output" / "aquisicao"
A10_CSV = AQ / "a10_ied_aps_2024_municipio.csv"
A10_JSON = AQ / "a10_diagnostico_cortes_normas.json"
A08 = T40.A08
ADENDO = ROOT / "docs" / "06_execucao" / "48g_adendo_heterogeneidade_porte_ied.md"
DOC = ROOT / "docs" / "06_execucao" / "57u_resultados_heterogeneidade_porte.md"
HI_EST = OUT / "HI_estimativas.csv"
HI_RES = OUT / "HI_resumo.json"
OC_EST = OUT / "OC_estimativas.csv"
OC_RES = OUT / "OC_resumo.json"
NOME_EST = "PO_estimativas.csv"
NOME_CONT = "PO_contagens.csv"
NOME_RESUMO = "PO_resumo.json"
DIR_FIG = OUT / "PO_figuras"
NOME_FIG = "PO_salto_por_grupo.png"

DATA_EXECUCAO = "2026-10-26"
ESTATUTO = "ADENDO_48G_POS_RESULTADO"
NATUREZA = "EMPIRICO"
COMMIT_CONGELAMENTO = "c87ed75"
COMMIT_DECISOES = "808db3a"
SHA_ADENDO = "5a77d7645a73a06a6a70ec51e49de54b014c12c844f39c3ccfc5d9f2515559ea"
CORTES = (300, 400)
CICLOS = (1, 2, 3)
H = 50                                  # h = 0,050
MIN_UNIDADES = 10                       # grupo × lado com menos de 10 municípios: linha sem estimativa
TOL_PORTAO = 1e-8
ALFA = 0.05
LIMITE_CNES = "202609"
ROT_CORTE = {300: "0.300", 400: "0.400"}
TXT_CORTE = {300: "0,300", 400: "0,400"}
BOLSA = {300: "R$ 10 mil → R$ 15 mil", 400: "R$ 15 mil → R$ 20 mil"}
OUTCOMES = ("HI-1", "HI-2", "B1", "B2", "B5")
ID_PO = {"HI-1": "PO-1", "HI-2": "PO-1", "B1": "PO-2", "B2": "PO-2", "B5": "PO-3"}
FAMILIA = {"PO-1": "holm", "PO-2": "bky", "PO-3": "bky"}
TERMOS = ("tau1_diferenca", "tau0_nao_muda", "tau0_mais_tau1_muda")
REGIOES = T44.REGIOES                   # as cinco macrorregiões, na ordem do 44
UN_FRAC = T40.UN_FRAC
UN_CONT = T40.UN_CONT

DESC = {
    "HI-1": "celula com vaga imediata preenchida na 1a chamada (HI-1 do 48b)",
    "HI-2": "medicos alocados na 1a chamada em celulas com vaga imediata, por municipio (HI-2 do 48b)",
    "B1": "mudanca pos - pre nos vinculos de especialistas nas CBO-alvo (OC-A1 do protocolo 64)",
    "B2": "mudanca pos - pre nas horas SUS semanais nas CBO-alvo (OC-A2 do protocolo 64)",
    "B5": "mudanca pos - pre nos vinculos de generalistas (placebo do protocolo 64; canal do IED)",
}
NOME = {"HI-1": "HI-1 · célula com vaga imediata preenchida", "HI-2": "HI-2 · alocados em vagas imediatas por município",
        "B1": "ΔB1 · vínculos de especialistas", "B2": "ΔB2 · horas SUS de especialistas",
        "B5": "ΔB5 · vínculos de generalistas"}
UNIDADE = {"HI-1": UN_FRAC, "HI-2": UN_CONT,
           "B1": "vinculos por 10 mil hab. (Censo 2022), media pos - media pre",
           "B2": "horas SUS semanais por 10 mil hab. (Censo 2022), media pos - media pre",
           "B5": "vinculos por 10 mil hab. (Censo 2022), media pos - media pre"}
NOME_TERMO = {"tau1_diferenca": "diferença (muda − não muda), τ₁", "tau0_nao_muda": "estrato não muda, τ₀",
              "tau0_mais_tau1_muda": "estrato muda, τ₀ + τ₁"}
CONTRASTE = ("pacote do corte: em 0,300 a bolsa anunciada sobe de R$ 10 mil para R$ 15 mil e em 0,400 de R$ 15 mil "
             "para R$ 20 mil, e outras regras federais mudam nos mesmos cortes (auditoria 18); tau1 compara o salto "
             "entre portes em que o estrato do IED muda e portes em que nao muda: heterogeneidade descritiva por uma "
             "condicao pre-tratamento (porte), nao efeito do IED nem da bolsa isolada")

COLUNAS = [
    "natureza_dos_dados", "estatuto", "id_linha", "id_po", "papel", "outcome", "descricao_outcome", "unidade",
    "corte", "termo", "status", "estimador", "h", "portes_G1", "portes_G0", "n_obs", "n_clusters",
    "n_mun_G0_abaixo", "n_mun_G0_acima", "n_mun_G1_abaixo", "n_mun_G1_acima", "tau", "ep", "ic95_inf", "ic95_sup",
    "p_valor", "familia", "p_holm", "q_bky", "contraste", "nota",
]
COLUNAS_CONT = [
    "natureza_dos_dados", "estatuto", "tipo", "populacao", "corte", "G", "lado", "n_municipios", "n_linhas",
    "n_celulas", "fora_sem_porte", "frac_capital", *[f"frac_{r}" for r in REGIOES], "nota",
]


class FalhaValidacao(RuntimeError):
    """Portão ou conferência obrigatória falhou: o script para sem gravar."""


sha256 = T23.sha256
rotulo = T23.rotulo


def _nan_none(o):
    return T40._nan_none(o)


def _juntar(*notas) -> str:
    return "; ".join(str(n) for n in notas if n)


# ---------------------------------------------------------------------------
# 1. G por corte, lido do a10 (decisões 1 a 3)
# ---------------------------------------------------------------------------

def regra_g() -> dict:
    """Códigos de IVS de cada lado do corte, estrato por código × porte e G por porte, todos lidos do JSON do a10."""
    js = json.loads(A10_JSON.read_text(encoding="utf-8"))
    ied = js["ied_aps_3493_2024"]
    if ied.get("regra_deterministica") is not True:
        raise FalhaValidacao("a10: regra_deterministica != true")
    faixas = {int(k): (float(v["min"]), float(v["max"])) for k, v in ied["faixa_ivs_oficial_por_codigo"].items()}
    estrato = {}
    for e in ied["estrato_ied_por_codigo_ivs_e_porte"]:
        obs = e["estratos_observados"]
        if len(obs) != 1:
            raise FalhaValidacao(f"a10: código {e['ivs_codigo']} × porte {e['porte_codigo']} com estratos {obs}")
        estrato[(int(e["ivs_codigo"]), int(e["porte_codigo"]))] = int(obs[0])
    portes = sorted(int(k) for k in ied["porte_codigo_rotulos"])
    saida = js["saidas"][rotulo(A10_CSV)]
    if sha256(A10_CSV) != saida["sha256"]:
        raise FalhaValidacao("a10 CSV com SHA-256 diferente do registrado no JSON do a10")
    out = {"json": rotulo(A10_JSON), "sha256_json": sha256(A10_JSON), "csv": rotulo(A10_CSV),
           "sha256_csv": saida["sha256"], "portes": portes,
           "rotulos_porte": {int(k): v for k, v in ied["porte_codigo_rotulos"].items()},
           "faixas_por_codigo": {k: list(v) for k, v in sorted(faixas.items())},
           "estrato": {f"{k[0]}|{k[1]}": v for k, v in sorted(estrato.items())}, "cortes": {}}
    for c in CORTES:
        cv = c / 1000.0
        de_baixo = [k for k, (lo, hi) in faixas.items() if lo - 1e-9 <= cv <= hi + 1e-9]
        if len(de_baixo) != 1:
            raise FalhaValidacao(f"corte {cv}: {len(de_baixo)} códigos com faixa que contém o corte")
        acima = sorted(((lo, k) for k, (lo, hi) in faixas.items() if lo > cv + 1e-9))
        if not acima:
            raise FalhaValidacao(f"corte {cv}: nenhum código acima")
        cod_b, cod_a = de_baixo[0], acima[0][1]
        por_porte = {}
        for p in portes:
            eb, ea = estrato[(cod_b, p)], estrato[(cod_a, p)]
            por_porte[p] = {"estrato_abaixo": eb, "estrato_acima": ea, "G": int(eb != ea)}
        out["cortes"][ROT_CORTE[c]] = {
            "codigo_ivs_abaixo": cod_b, "codigo_ivs_acima": cod_a, "por_porte": por_porte,
            "portes_G1": [p for p in portes if por_porte[p]["G"] == 1],
            "portes_G0": [p for p in portes if por_porte[p]["G"] == 0]}
    return out


def ler_a10(regra: dict) -> pd.DataFrame:
    """Porte e código de IVS por município (Anexo VI); confere o estrato gravado contra a regra do JSON."""
    a = pd.read_csv(A10_CSV, dtype={"co_ibge": str})
    if a["co_ibge"].duplicated().any() or (a["co_ibge"].str.len() != 6).any():
        raise FalhaValidacao("a10 com co_ibge duplicado ou fora de 6 dígitos")
    if set(a["natureza_dos_dados"]) != {"EMPIRICO"}:
        raise FalhaValidacao("a10 sem natureza EMPIRICO")
    esperado = [regra["estrato"].get(f"{int(c)}|{int(p)}") for c, p in zip(a["ivs_codigo_portaria"], a["porte_codigo"])]
    if any(e is None for e in esperado) or (np.array(esperado) != a["estrato_ied"].to_numpy()).any():
        raise FalhaValidacao("a10: estrato gravado difere da regra código × porte do JSON")
    return a.set_index("co_ibge")[["porte_codigo", "ivs_codigo_portaria", "estrato_ied"]]


def g_de(porte: pd.Series, regra: dict, c: int) -> pd.Series:
    g1 = set(regra["cortes"][ROT_CORTE[c]]["portes_G1"])
    return porte.map(lambda p: np.nan if pd.isna(p) else float(int(p) in g1))


def conferir_codigo_na_janela(cod: pd.Series, s_mil: pd.Series, regra: dict, c: int) -> dict:
    """Município na janela: código de IVS do Anexo VI = código de baixo se IVS oficial <= corte, de cima se maior."""
    x = L.normalizar_s_mil(s_mil.to_numpy(float)) - c
    jan = (x > -H) & (x < H)
    rc = regra["cortes"][ROT_CORTE[c]]
    esperado = np.where(x <= 0, rc["codigo_ivs_abaixo"], rc["codigo_ivs_acima"])
    ok = cod.notna().to_numpy()
    dif = jan & ok & (cod.fillna(-1).to_numpy(float) != esperado)
    if dif.any():
        raise FalhaValidacao(f"corte {c}: {int(dif.sum())} municípios na janela com código de IVS do Anexo VI do "
                             "lado errado do corte")
    return {"municipios_na_janela": int(jan.sum()), "conferidos": int((jan & ok).sum()), "divergentes": 0}


# ---------------------------------------------------------------------------
# 2. Dados (construtores dos scripts 40 e 43)
# ---------------------------------------------------------------------------

def carregar_h1() -> dict:
    todos = T40.carregar()
    return todos["13fev"]


def carregar_oc() -> dict:
    """V e ΔB1, ΔB2, ΔB5 com as funções do script 43 (taxa por 10 mil hab., diferença pós − pré, exigir completo)."""
    d = T43.carregar()
    V = pd.Index(d["V"]).astype(str)
    base = d["base"].copy()
    base.index = base.index.astype(str)
    maior = max(str(m) for oid in ("B1", "B2", "B5") for m in d["niveis"][oid].columns)
    if maior >= LIMITE_CNES:
        raise FalhaValidacao(f"painel do CNES com competência {maior} >= {LIMITE_CNES}")
    frames = {}
    for oid in ("B1", "B2", "B5"):
        dl = T43.deltas(T43.taxa(d["niveis"][oid].reindex(d["V"]), d["pop"]))
        f = pd.DataFrame({"co_ibge": V, "s_mil": base.loc[V, "s_mil"].to_numpy(float),
                          "y_pos": dl["y_pos"].to_numpy(float), "y_pre": dl["y_pre"].to_numpy(float)})
        f["y"] = f["y_pos"] - f["y_pre"]
        frames[oid] = f
    return {"V": V, "frames": frames, "maior_competencia": maior, "n_V": int(len(V))}


def amostra_h1(h1: dict, oid: str, c: int):
    if oid == "HI-1":
        return T40.amostra(h1["CK"], CICLOS, c, T40.filtro_tipos("so_imed", "mista"))
    return T40.amostra(h1["MK"], CICLOS, c, T40.filtro_coluna_positiva("n_cel_imed"))


def amostra_oc(oc: dict, oid: str, c: int):
    return T23.montar_amostra([(oc["frames"][oid], c, "V")], empilhada=False)


Y_COL = {"HI-1": "preenchida", "HI-2": "aloc_imed", "B1": "y", "B2": "y", "B5": "y"}


# ---------------------------------------------------------------------------
# 3. Estimador (rdd_lib.rd_empilhado com grupo × G e T × G)
# ---------------------------------------------------------------------------

def ajustar_po(a, oid: str, G: np.ndarray | None, h: int = H) -> dict:
    """Salto por grupo. `G=None`: sem a divisão (grupo = ciclo na H1; um grupo no OC), deve repetir a base.

    H1: CR1 por município; EF de curso × ciclo (HI-1); controle de vagas imediatas por ciclo (HI-2).
    OC: um município por linha, HC1 (como `rd_dird_delta`)."""
    y = a.col(Y_COL[oid])
    h1 = oid in ("HI-1", "HI-2")
    if G is None:
        grupo = a.g
    else:
        grupo = np.array([f"{g}|G{int(x)}" for g, x in zip(a.g, G)], dtype=object)
    cols, nomes = [], []
    if G is not None:
        cols.append(a.t * G)
        nomes.append("T_G")
    if oid == "HI-2":
        Zc, nz, _vbar, _vcg = T23.colunas_controle(a, y, a.col("vi_imed"), h)
        cols.append(Zc)
        nomes += nz
    Z = np.column_stack(cols) if cols else None
    r = L.rd_empilhado(a.s, y, a.c, grupo=grupo, h_mil=h, cluster=a.cl if h1 else None,
                       ids_unidade=a.cl if h1 else None,
                       efeitos_fixos=a.d["fe_curso_ciclo"].to_numpy() if oid == "HI-1" else None,
                       Z=Z, nomes_z=nomes or None, detalhes=True)
    return r


def termos(r: dict) -> dict:
    """τ₀ (T), τ₁ (T × G) e τ₀ + τ₁, com EP da mesma matriz sanduíche."""
    vazio = {t: {"tau": np.nan, "ep": np.nan} for t in TERMOS}
    if "_detalhes" not in r or not np.isfinite(r["tau"]):
        return {"ok": False, "motivo": r.get("nota") or "biblioteca devolveu NaN", **vazio}
    fit = r["_detalhes"]["fit"]
    if "T_G" not in fit["nomes"]:
        return {"ok": False, "motivo": "coluna T x G descartada (sem variacao ou colinear)", **vazio}
    iT, iG = fit["nomes"].index("T"), fit["nomes"].index("T_G")
    b, V = fit["beta"], fit["V"]
    t0, t1 = float(b[iT]), float(b[iG])
    if abs(t0 - r["tau"]) > 1e-12 * max(1.0, abs(t0)):
        raise FalhaValidacao("coeficiente de T difere do tau da biblioteca")
    v0, v1, c01 = float(V[iT, iT]), float(V[iG, iG]), float(V[iT, iG])
    return {"ok": True, "motivo": "",
            "tau0_nao_muda": {"tau": t0, "ep": math.sqrt(max(v0, 0.0))},
            "tau1_diferenca": {"tau": t1, "ep": math.sqrt(max(v1, 0.0))},
            "tau0_mais_tau1_muda": {"tau": t0 + t1, "ep": math.sqrt(max(v0 + v1 + 2 * c01, 0.0))},
            "cov_tau0_tau1": c01}


def inferencia(tau: float, ep: float) -> dict:
    if not (np.isfinite(tau) and np.isfinite(ep) and ep > 0):
        return {"ic95_inf": np.nan, "ic95_sup": np.nan, "p_valor": np.nan}
    return {"ic95_inf": tau - L.Z_975 * ep, "ic95_sup": tau + L.Z_975 * ep, "p_valor": L.p_normal(tau / ep)}


def contar_janela(a, oid: str, G: np.ndarray, h: int = H) -> dict:
    """Municípios distintos (e linhas; células na HI-1) com peso de kernel > 0 e outcome (e controle) observados, por
    G × lado (decisão 11)."""
    x = L.normalizar_s_mil(a.s) - a.c
    ok = (L.pesos_kernel(x, h) > 0) & np.isfinite(a.col(Y_COL[oid]))
    if oid == "HI-2":
        ok &= np.isfinite(a.col("vi_imed"))
    out = {}
    for g in (0, 1):
        for lado, m_lado in (("abaixo", x <= 0), ("acima", x > 0)):
            m = ok & (G == g) & m_lado
            out[f"G{g}_{lado}"] = {"municipios": int(np.unique(a.cl[m]).size), "linhas": int(m.sum())}
    return out


# ---------------------------------------------------------------------------
# 4. Portão de reprodução (antes de qualquer conta nova)
# ---------------------------------------------------------------------------

def _ref_hi(hi: pd.DataFrame, oid: str, c: int) -> pd.Series:
    sel = hi[(hi["linha"] == oid) & (hi["outcome"] == oid) & (hi["variante"] == "principal")
             & (hi["corte"] == ROT_CORTE[c])]
    if len(sel) != 1:
        raise FalhaValidacao(f"HI_estimativas: {len(sel)} linhas {oid} principal {c}")
    return sel.iloc[0]


def _ref_oc(oc: pd.DataFrame, oid: str, c: int) -> pd.Series:
    sel = oc[(oc["parte"] == "A") & (oc["outcome_id"] == oid) & (oc["populacao"] == "V")
             & (oc["especificacao"] == "principal") & (oc["corte"] == ROT_CORTE[c])]
    if len(sel) != 1:
        raise FalhaValidacao(f"OC_estimativas: {len(sel)} linhas {oid} V principal {c}")
    return sel.iloc[0]


def _compara(nome: str, como: str, r: dict, ref: pd.Series) -> dict:
    dt, de = abs(float(r["tau"]) - float(ref["tau"])), abs(float(r["ep"]) - float(ref["ep"]))
    nr = [int(r["n_abaixo"]), int(r["n_acima"])]
    nref = [int(ref["n_abaixo"]), int(ref["n_acima"])]
    ok = dt <= TOL_PORTAO and de <= TOL_PORTAO and nr == nref
    if not ok:
        raise FalhaValidacao(f"portão: {nome} ({como}) não reproduz: |dif tau| {dt}, |dif ep| {de}, n {nr} vs {nref}")
    return {"linha": nome, "como": como, "tau_ref": float(ref["tau"]), "tau": float(r["tau"]), "ep_ref": float(ref["ep"]),
            "ep": float(r["ep"]), "dif_tau": dt, "dif_ep": de, "n_abaixo_acima": nr, "aprovado": True}


def portao(h1: dict, oc: dict, regra: dict, a10: pd.DataFrame) -> dict:
    hi = pd.read_csv(HI_EST, dtype={"corte": str, "ciclo": str}, low_memory=False)
    ocr = pd.read_csv(OC_EST, dtype={"corte": str, "outcome_id": str, "populacao": str}, low_memory=False)
    c = 300
    linhas = []
    a1 = amostra_h1(h1, "HI-1", c)
    linhas.append(_compara("HI-1 0,300", "est_celula do 40", T40.est_celula(a1, a1.col("preenchida")),
                           _ref_hi(hi, "HI-1", c)))
    linhas.append(_compara("HI-1 0,300", "estimador do 47 sem divisao", ajustar_po(a1, "HI-1", None),
                           _ref_hi(hi, "HI-1", c)))
    a2 = amostra_h1(h1, "HI-2", c)
    linhas.append(_compara("HI-2 0,300", "est_municipio do 40",
                           T40.est_municipio(a2, a2.col("aloc_imed"), v=a2.col("vi_imed")), _ref_hi(hi, "HI-2", c)))
    linhas.append(_compara("HI-2 0,300", "estimador do 47 sem divisao", ajustar_po(a2, "HI-2", None),
                           _ref_hi(hi, "HI-2", c)))
    f = oc["frames"]["B1"]
    r = T43.L.rd_dird_delta(f["s_mil"].to_numpy(float), f["y_pos"].to_numpy(float), f["y_pre"].to_numpy(float), c, H)
    linhas.append(_compara("OC-A1 0,300", "rd_dird_delta (como o 43)", r, _ref_oc(ocr, "B1", c)))
    ao = amostra_oc(oc, "B1", c)
    linhas.append(_compara("OC-A1 0,300", "estimador do 47 sem divisao", ajustar_po(ao, "B1", None),
                           _ref_oc(ocr, "B1", c)))
    # G: lido do a10; código de IVS do Anexo VI do lado certo do corte para todo município na janela.
    s_ref = pd.concat([pd.Series(oc["frames"]["B1"].set_index("co_ibge")["s_mil"])]
                      + [pd.Series(d.set_index("co_ibge")["s_mil"]) for d in h1["MK"].values()])
    s_ref = s_ref[~s_ref.index.duplicated()]
    cod = a10["ivs_codigo_portaria"].reindex(s_ref.index)
    janela = {ROT_CORTE[cc]: conferir_codigo_na_janela(cod, s_ref, regra, cc) for cc in CORTES}
    return {"linhas": linhas, "tolerancia": TOL_PORTAO, "max_abs_dif": max(max(x["dif_tau"], x["dif_ep"])
                                                                           for x in linhas),
            "g_lido_do_a10": {"fonte": regra["json"], "estrato_do_csv_igual_a_regra": True,
                              "codigo_do_anexo_vi_na_janela": janela},
            "aprovado": True}


# ---------------------------------------------------------------------------
# 5. Estimação PO-1 a PO-4 e contagens PO-5
# ---------------------------------------------------------------------------

def _g_da_amostra(a, porte: pd.Series, regra: dict, c: int) -> tuple[object, np.ndarray, dict]:
    """Tira as linhas sem porte (contadas) e devolve a amostra, G por linha e a contagem de fora."""
    p = a.d["co_ibge"].astype(str).map(porte)
    sem = p.isna().to_numpy()
    x = L.normalizar_s_mil(a.s) - a.c
    fora = {"linhas_sem_porte": int(sem.sum()),
            "municipios_sem_porte_na_janela": int(np.unique(a.cl[sem & (np.abs(x) < H)]).size)}
    if sem.any():
        a = a.subconjunto(~sem)
        p = p[~sem]
    G = g_de(p.reset_index(drop=True), regra, c).to_numpy(float)
    return a, G, fora


def nova_linha(oid: str, c: int, termo: str, regra: dict) -> dict:
    ln = {k: np.nan for k in COLUNAS}
    rc = regra["cortes"][ROT_CORTE[c]]
    po = ID_PO[oid] if termo == "tau1_diferenca" else "PO-4"
    papel = {"PO-1": "primaria", "PO-2": "secundaria", "PO-3": "secundaria (teste do canal)",
             "PO-4": "descritiva"}[po]
    est = ("rdd_lib.rd_empilhado; local linear, kernel triangular, h = 0,050; " + (
        "grupo = ciclo x G (intercepto e inclinacoes por ciclo x G x lado); salto comum T + T x G; "
        + ("EF de curso x ciclo; " if oid == "HI-1" else "controle = vagas imediatas, um coeficiente por ciclo; ")
        + "CR1 por municipio" if oid in ("HI-1", "HI-2") else
        "grupo = G (intercepto e inclinacoes por G x lado); salto comum T + T x G; um municipio por linha; HC1"))
    ln.update({"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "id_po": po, "papel": papel, "outcome": oid,
               "descricao_outcome": DESC[oid], "unidade": UNIDADE[oid], "corte": ROT_CORTE[c], "termo": termo,
               "status": "EXECUTADO", "estimador": est, "h": H / 1000.0,
               "portes_G1": ";".join(str(p) for p in rc["portes_G1"]),
               "portes_G0": ";".join(str(p) for p in rc["portes_G0"]),
               "familia": FAMILIA.get(po, ""), "contraste": CONTRASTE, "nota": ""})
    ln["id_linha"] = "|".join([po, oid, ROT_CORTE[c], termo])
    return ln


def estimar(h1: dict, oc: dict, regra: dict, a10: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    porte = a10["porte_codigo"]
    linhas, cont, extras = [], [], {"janela": {}, "sem_estimativa": []}
    amostras = {}
    for c in CORTES:
        for oid in OUTCOMES:
            a0 = amostra_h1(h1, oid, c) if oid in ("HI-1", "HI-2") else amostra_oc(oc, oid, c)
            a, G, fora = _g_da_amostra(a0, porte, regra, c)
            amostras[(oid, c)] = (a, G)
            n = contar_janela(a, oid, G)
            x = L.normalizar_s_mil(a.s) - a.c
            for g in (0, 1):
                for lado, m_lado in (("abaixo", x <= 0), ("acima", x > 0)):
                    m = (np.abs(x) < H) & (G == g) & m_lado & np.isfinite(a.col(Y_COL[oid]))
                    cont.append({"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "tipo": "amostra",
                                 "populacao": oid, "corte": ROT_CORTE[c], "G": g, "lado": lado,
                                 "n_municipios": n[f"G{g}_{lado}"]["municipios"],
                                 "n_linhas": n[f"G{g}_{lado}"]["linhas"],
                                 "n_celulas": int(m.sum()) if oid == "HI-1" else np.nan,
                                 "fora_sem_porte": fora["municipios_sem_porte_na_janela"], "nota":
                                     "municipios distintos com peso de kernel > 0 e outcome observado" + (
                                         " (e controle)" if oid == "HI-2" else "")
                                     + ("; n_linhas = celulas" if oid == "HI-1" else
                                        "; n_linhas = municipio x ciclo" if oid == "HI-2" else "")})
            extras["janela"][f"{oid}|{ROT_CORTE[c]}"] = {**n, **fora}
            poucos = [k for k, v in n.items() if v["municipios"] < MIN_UNIDADES]
            if poucos:
                r, tt = None, {"ok": False, "motivo": f"menos de {MIN_UNIDADES} municipios em {', '.join(poucos)}"}
                status = "SEM_ESTIMATIVA_MENOS_DE_10"
            else:
                r = ajustar_po(a, oid, G)
                tt = termos(r)
                status = "EXECUTADO" if tt["ok"] else "SEM_ESTIMATIVA"
            if not tt["ok"]:
                extras["sem_estimativa"].append({"outcome": oid, "corte": ROT_CORTE[c], "status": status,
                                                 "motivo": tt["motivo"]})
            for termo in TERMOS:
                ln = nova_linha(oid, c, termo, regra)
                for g in (0, 1):
                    for lado in ("abaixo", "acima"):
                        ln[f"n_mun_G{g}_{lado}"] = n[f"G{g}_{lado}"]["municipios"]
                ln["status"] = status
                if tt["ok"]:
                    tau, ep = tt[termo]["tau"], tt[termo]["ep"]
                    ln.update({"tau": tau, "ep": ep, **inferencia(tau, ep), "n_obs": r["n_obs"],
                               "n_clusters": r["n_clusters"] if r["n_clusters"] is not None else np.nan})
                    ln["nota"] = _juntar(r.get("nota", ""), f"colunas descartadas: {r['covariaveis_descartadas']}"
                                         if r.get("covariaveis_descartadas") else "")
                else:
                    ln["nota"] = tt["motivo"]
                linhas.append(ln)
    est = pd.DataFrame(linhas)[COLUNAS]
    est = aplicar_multiplos(est)
    cont += balanco(amostras)
    co = pd.DataFrame(cont).reindex(columns=COLUNAS_CONT)
    if est["id_linha"].duplicated().any():
        raise FalhaValidacao("id_linha duplicado")
    return est, co, extras


def aplicar_multiplos(est: pd.DataFrame) -> pd.DataFrame:
    """Holm nas 4 τ₁ da PO-1; BKY nas 6 τ₁ da PO-2 e PO-3. Família de tamanho fixo: sem estimativa entra com p = 1."""
    est = est.copy()
    t1 = est["termo"] == "tau1_diferenca"
    for fam, fn, col, n in (("holm", L.holm, "p_holm", 4), ("bky", L.qvalores_bky, "q_bky", 6)):
        m = t1 & (est["familia"] == fam)
        if int(m.sum()) != n:
            raise FalhaValidacao(f"família {fam} com {int(m.sum())} linhas; esperado {n}")
        p = est.loc[m, "p_valor"].to_numpy(dtype=float)
        aj = np.asarray(fn(np.where(np.isfinite(p), p, 1.0)), dtype=float)
        est.loc[m, col] = np.where(np.isfinite(p), aj, np.nan)
    est.loc[~t1, "familia"] = ""
    return est


def balanco(amostras: dict) -> list[dict]:
    """Capital e macrorregião por corte × G × lado na janela (PO-5): populações H1 (amostra da HI-2) e V (ΔB1)."""
    ref, _info = T44.ler_referencia_ibge()
    por_uf = ref.set_index(ref["cd_uf"].astype(str))
    capitais = set(ref["capital_co_ibge_6d"].astype(str))
    out = []
    for c in CORTES:
        for pop, oid in (("H1 (municipios da amostra da HI-2, qualquer ciclo)", "HI-2"), ("V (amostra de dB1)", "B1")):
            a, G = amostras[(oid, c)]
            x = L.normalizar_s_mil(a.s) - a.c
            ok = (np.abs(x) < H) & np.isfinite(a.col(Y_COL[oid]))
            d = pd.DataFrame({"co_ibge": a.cl[ok], "G": G[ok], "acima": x[ok] > 0})
            if (d.groupby("co_ibge")[["G", "acima"]].nunique() > 1).any().any():
                raise FalhaValidacao("município com G ou lado diferente entre ciclos")
            d = d.drop_duplicates("co_ibge")
            uf = d["co_ibge"].str[:2]
            if not uf.isin(por_uf.index).all():
                raise FalhaValidacao("município com UF fora da referência do IBGE")
            d["regiao"] = uf.map(por_uf["nome_regiao"])
            d["capital"] = d["co_ibge"].isin(capitais).astype(float)
            for g in (0, 1):
                for lado, ac in (("abaixo", False), ("acima", True)):
                    s = d[(d["G"] == g) & (d["acima"] == ac)]
                    ln = {"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "tipo": "balanco", "populacao": pop,
                          "corte": ROT_CORTE[c], "G": g, "lado": lado, "n_municipios": int(len(s)),
                          "frac_capital": float(s["capital"].mean()) if len(s) else np.nan,
                          "nota": "medias simples na janela h = 0,050, sem teste (descritivo)"}
                    for rg in REGIOES:
                        ln[f"frac_{rg}"] = float((s["regiao"] == rg).mean()) if len(s) else np.nan
                    out.append(ln)
    return out


# ---------------------------------------------------------------------------
# 6. Leitura (§4 do adendo; decisões 16 a 18)
# ---------------------------------------------------------------------------

def _contem_zero(r) -> bool:
    return float(r["ic95_inf"]) <= 0.0 <= float(r["ic95_sup"])


def _linha(est: pd.DataFrame, oid: str, c, termo: str) -> pd.Series:
    ct = c if isinstance(c, str) else ROT_CORTE[c]
    sel = est[(est["outcome"] == oid) & (est["corte"] == ct) & (est["termo"] == termo)]
    if len(sel) != 1:
        raise FalhaValidacao(f"linha não única: {oid} {ct} {termo}")
    return sel.iloc[0]


def _executada(r) -> bool:
    return r["status"] == "EXECUTADO" and np.isfinite(float(r["tau"]))


def leituras(est: pd.DataFrame, co: pd.DataFrame) -> dict:
    prim = [(oid, c) for oid in ("HI-1", "HI-2") for c in CORTES]
    sem = [f"{oid} {TXT_CORTE[c]}" for oid, c in prim if not _executada(_linha(est, oid, c, "tau1_diferenca"))]
    ex = [(oid, c) for oid, c in prim if _executada(_linha(est, oid, c, "tau1_diferenca"))]
    rej, conc, ic_sem_zero = [], [], []
    for oid, c in ex:
        t1 = _linha(est, oid, c, "tau1_diferenca")
        if not _contem_zero(t1):
            ic_sem_zero.append(f"{oid} {TXT_CORTE[c]}")
        if float(t1["p_holm"]) < ALFA:
            rej.append(f"{oid} {TXT_CORTE[c]}")
            muda, nao = _linha(est, oid, c, "tau0_mais_tau1_muda"), _linha(est, oid, c, "tau0_nao_muda")
            if (not _contem_zero(muda)) and _contem_zero(nao):
                conc.append(f"{oid} {TXT_CORTE[c]}")
    if conc:
        cod = "TAU1_REJEITA_HOLM_CONCENTRADO"
    elif rej:
        cod = "TAU1_REJEITA_HOLM_SEM_CONCENTRACAO"
    elif ic_sem_zero:
        cod = "TAU1_IC_EXCLUI_ZERO_SEM_HOLM"
    else:
        cod = "TAU1_TODOS_CONTEM_ZERO"
    po1 = {"codigo": cod, "linhas_sem_estimativa": sem, "linhas_que_rejeitam_depois_do_holm": rej,
           "linhas_concentradas_onde_muda": conc, "linhas_com_ic_convencional_sem_zero": ic_sem_zero,
           "regra": "TAU1_TODOS_CONTEM_ZERO se as 4 tau1 da PO-1 tem IC 95% com zero; TAU1_REJEITA_HOLM_CONCENTRADO se "
                    "alguma tau1 tem p Holm < 0,05 e, nela, o IC de tau0 + tau1 exclui zero e o de tau0 contem zero; "
                    "TAU1_REJEITA_HOLM_SEM_CONCENTRACAO se rejeita depois do Holm sem essa concentracao; "
                    "TAU1_IC_EXCLUI_ZERO_SEM_HOLM se algum IC convencional de tau1 exclui zero e nenhum p Holm < 0,05"}
    po3 = {}
    for c in CORTES:
        muda, nao = _linha(est, "B5", c, "tau0_mais_tau1_muda"), _linha(est, "B5", c, "tau0_nao_muda")
        t1 = _linha(est, "B5", c, "tau1_diferenca")
        if not _executada(t1):
            po3[ROT_CORTE[c]] = {"codigo": "SEM_ESTIMATIVA", "q_bky_tau1": None}
            continue
        ind = (not _contem_zero(muda)) and _contem_zero(nao)
        po3[ROT_CORTE[c]] = {"codigo": "INDICIO_IED_MOVE_APS" if ind else "SEM_INDICIO",
                             "q_bky_tau1": float(t1["q_bky"]), "tau1_q_abaixo_de_0_05": bool(float(t1["q_bky"]) < ALFA)}
    am = co[co["tipo"] == "amostra"]
    sem_pot = [{"outcome": r["populacao"], "corte": r["corte"], "G": int(r["G"]), "lado": r["lado"],
                "n_municipios": int(r["n_municipios"])} for _, r in am.iterrows() if r["n_municipios"] < MIN_UNIDADES]
    menor = am.loc[am["n_municipios"].idxmin()]
    return {"po1": po1, "po3": po3,
            "potencia": {"grupos_lado_com_menos_de_10": sem_pot,
                         "menor_grupo_lado": {"outcome": menor["populacao"], "corte": menor["corte"],
                                              "G": int(menor["G"]), "lado": menor["lado"],
                                              "n_municipios": int(menor["n_municipios"])}}}


# ---------------------------------------------------------------------------
# 7. Formatação (pt-BR)
# ---------------------------------------------------------------------------

fn, fp, fint, _tab = T40.fn, T40.fp, T40.fint, T40._tab


def fv(r, col="tau") -> str:
    if r["unidade"] == UN_FRAC:
        return T40.fpp(r[col]) + " p.p."
    return fn(r[col], 2)


def fic(r) -> str:
    if not np.isfinite(float(r["ic95_inf"])):
        return "—"
    if r["unidade"] == UN_FRAC:
        return f"[{T40.fpp(r['ic95_inf'])}; {T40.fpp(r['ic95_sup'])}]"
    return f"[{fn(r['ic95_inf'])}; {fn(r['ic95_sup'])}]"


def _ct(ct: str) -> str:
    return TXT_CORTE[int(round(float(ct) * 1000))]


def _status_txt(r) -> str:
    return {"EXECUTADO": "", "SEM_ESTIMATIVA": "sem estimativa", "SEM_ESTIMATIVA_MENOS_DE_10":
            f"sem estimativa (menos de {MIN_UNIDADES} municípios num grupo × lado)"}[r["status"]]


def _ns(r) -> str:
    return (f"{fint(r['n_mun_G0_abaixo'])} / {fint(r['n_mun_G0_acima'])} · "
            f"{fint(r['n_mun_G1_abaixo'])} / {fint(r['n_mun_G1_acima'])}")


def _portes(ps) -> str:
    ps = [str(x) for x in ps]
    if len(ps) == 1:
        return f"no porte {ps[0]}"
    return "nos portes " + ", ".join(ps[:-1]) + " e " + ps[-1]


def _pct(x) -> str:
    return "—" if not np.isfinite(float(x)) else T40.fpp(x, 0, False) + " %"


def _portes_de(ps) -> str:
    ps = [str(x) for x in ps]
    if len(ps) == 1:
        return f"do porte {ps[0]}"
    return "dos portes " + ", ".join(ps[:-1]) + " e " + ps[-1]


def _composicao_g(co: pd.DataFrame, resumo: dict, c: int) -> str:
    """Quem está em cada grupo na janela (população H1 do balanço, seção 7): portes, capitais e Nordeste (auditoria
    45, A1 e A3). Só lê o que o balanço gravou."""
    b = co[(co["tipo"] == "balanco") & (co["populacao"].str.startswith("H1")) & (co["corte"] == ROT_CORTE[c])]
    v = {(int(r["G"]), r["lado"]): r for _, r in b.iterrows()}
    rc = resumo["regra_g"]["cortes"][ROT_CORTE[c]]

    def par(g, col):
        return f"{_pct(v[(g, 'abaixo')][col])} e {_pct(v[(g, 'acima')][col])}"
    return (f"em {TXT_CORTE[c]}, o grupo em que o estrato não muda é formado pelos municípios "
            f"{_portes_de(rc['portes_G0'])}, com {par(0, 'frac_capital')} de capitais e {par(0, 'frac_Nordeste')} no "
            f"Nordeste (abaixo e acima do corte), contra {par(1, 'frac_capital')} de capitais e "
            f"{par(1, 'frac_Nordeste')} no Nordeste onde o estrato muda (seção 7)")


# ---------------------------------------------------------------------------
# 8. Blocos do doc 57u
# ---------------------------------------------------------------------------

def bloco(nome: str, corpo: str) -> str:
    return f"<!-- PO:{nome}:inicio -->\n{corpo.rstrip()}\n<!-- PO:{nome}:fim -->"


MARCA = re.compile(r"<!-- PO:(?P<nome>[A-Za-z0-9_]+):inicio -->\n(?P<corpo>.*?)\n?<!-- PO:(?P=nome):fim -->", re.S)

TXT_PO1 = {
    "TAU1_TODOS_CONTEM_ZERO": (
        "**Não se detecta que o salto da H1 dependa de o estrato do IED mudar** (leitura pré-registrada do primeiro "
        "caso): nas quatro linhas da PO-1 o IC 95% da diferença τ₁ contém zero. Pelo adendo, o IED não explica o sinal "
        "da H1, com pouca potência: os grupos são pequenos (contagens na seção 3). Com IC de τ₁ tão largos, \"não "
        "explica\" quer dizer que os dados não mostram que o IED explique o salto; não quer dizer que o canal do IED "
        "esteja descartado."),
    "TAU1_REJEITA_HOLM_CONCENTRADO": (
        "**O sinal da H1 anda junto com o canal do IED** (leitura pré-registrada do segundo caso): a diferença τ₁ "
        "rejeita zero depois do Holm, com o salto concentrado onde o estrato muda. Reforça que o corte mede um pacote."),
    "TAU1_REJEITA_HOLM_SEM_CONCENTRACAO": (
        "**A diferença τ₁ rejeita zero depois do Holm, mas o salto não fica concentrado onde o estrato muda.** A "
        "leitura pré-registrada do segundo caso pede as duas coisas; aqui só se relatam sinal e tamanho."),
    "TAU1_IC_EXCLUI_ZERO_SEM_HOLM": (
        "**Depois do Holm, nenhuma diferença τ₁ da PO-1 rejeita zero**, mas o IC 95% convencional exclui zero em "
        "alguma linha. O caso fica entre os dois da leitura pré-registrada: é um sinal sem correção por comparações "
        "múltiplas, não a frase \"não se detecta\" nem um resultado confirmado."),
}


def resposta_curta(est: pd.DataFrame, co: pd.DataFrame, resumo: dict) -> str:
    le = resumo["leitura"]
    p = [TXT_PO1[le["po1"]["codigo"]]]
    if le["po1"]["linhas_com_ic_convencional_sem_zero"] and le["po1"]["codigo"] == "TAU1_IC_EXCLUI_ZERO_SEM_HOLM":
        p[0] += " Linhas com IC convencional sem zero: " + ", ".join(le["po1"]["linhas_com_ic_convencional_sem_zero"]) + "."
    if le["po1"]["linhas_sem_estimativa"]:
        p.append("Sem estimativa: " + ", ".join(le["po1"]["linhas_sem_estimativa"]) + ".")
    for c in CORTES:
        rc = resumo["regra_g"]["cortes"][ROT_CORTE[c]]
        partes = []
        for oid in ("HI-1", "HI-2"):
            t1 = _linha(est, oid, c, "tau1_diferenca")
            if not _executada(t1):
                partes.append(f"{oid}: {_status_txt(t1)}")
                continue
            m, n = _linha(est, oid, c, "tau0_mais_tau1_muda"), _linha(est, oid, c, "tau0_nao_muda")
            partes.append(f"{oid}: onde o estrato muda, {fv(m)} {fic(m)}; onde não muda, {fv(n)} {fic(n)}; "
                          f"diferença τ₁ = {fv(t1)} {fic(t1)}, p Holm {fp(t1['p_holm'])}")
        p.append(f"- **Corte {TXT_CORTE[c]}** ({BOLSA[c]}; o estrato muda {_portes(rc['portes_G1'])} e não muda "
                 f"{_portes(rc['portes_G0'])}). " + "; ".join(partes) + ".")
    hi = resumo["referencias"]["hi_leitura_primaria"]
    hi_sem_zero = resumo["referencias"]["hi_linhas_ic_convencional_sem_zero"]
    p.append("A própria H1, sem a divisão, não tem linha primária que rejeite zero depois do Holm (doc 57n, código "
             f"`{hi}`): não há um sinal firme da H1 para o IED explicar. A comparação entre grupos pergunta se o salto, "
             "seja qual for, difere entre eles.")
    for rot in hi_sem_zero:
        oid, ct = rot.split(" em ")
        c = int(round(float(ct.replace(",", ".")) * 1000))
        m, n = _linha(est, oid, c, "tau0_mais_tau1_muda"), _linha(est, oid, c, "tau0_nao_muda")
        if not (_executada(m) and _executada(n)):
            continue
        onde = [g for g, r in (("onde o estrato não muda", n), ("onde o estrato muda", m)) if not _contem_zero(r)]
        t1 = _linha(est, oid, c, "tau1_diferenca")
        dif = ("a diferença entre os grupos nessa linha (τ₁) não se distingue de zero" if _contem_zero(t1) else
               "a diferença entre os grupos nessa linha (τ₁) tem IC 95% sem zero") + (
            f" (p {fp(t1['p_valor'])}, p Holm {fp(t1['p_holm'])})")
        txt = (f"Na linha da H1 com IC convencional sem zero no 57n ({rot}), o IC 95% exclui zero "
               + (" e ".join(onde) if onde else "em nenhum dos dois grupos")
               + f" (não muda: {fv(n)} {fic(n)}; muda: {fv(m)} {fic(m)}).")
        if onde:
            txt += (" Isso é descritivo e não mostra que o salto da H1 venha de um grupo e não do outro: a PO-4 fica "
                    f"fora do Holm; {dif}; e {_composicao_g(co, resumo, c)}. A comparação entre grupos mistura o "
                    "canal do IED com porte, capital e região.")
        else:
            txt += f" Descritivo: a PO-4 fica fora do Holm; {dif}."
        p.append(txt)
    po4 = [r for _, r in est[est["termo"] != "tau1_diferenca"].iterrows() if _executada(r)]
    k4 = sum(not _contem_zero(r) for r in po4)
    if po4:
        p.append(f"Na PO-4 inteira, {k4} de {len(po4)} intervalos " + ("exclui" if k4 == 1 else "excluem")
                 + " zero; a 5%, cerca de um intervalo em vinte excluiria zero só por acaso, mesmo sem salto nenhum.")
    frases = []
    for c in CORTES:
        x = le["po3"][ROT_CORTE[c]]
        t1 = _linha(est, "B5", c, "tau1_diferenca")
        if x["codigo"] == "SEM_ESTIMATIVA":
            frases.append(f"em {TXT_CORTE[c]}, {_status_txt(t1)}")
            continue
        m, n = _linha(est, "B5", c, "tau0_mais_tau1_muda"), _linha(est, "B5", c, "tau0_nao_muda")
        txt = ("há indício de que o IED move a atenção primária no corte (salto só onde o estrato muda)"
               if x["codigo"] == "INDICIO_IED_MOVE_APS" else "não há indício de salto só onde o estrato muda")
        frases.append(f"em {TXT_CORTE[c]}, {txt}: onde muda, {fv(m)} {fic(m)}; onde não muda, {fv(n)} {fic(n)}; "
                      f"diferença {fv(t1)} {fic(t1)}, q BKY {fp(t1['q_bky'])}")
    p.append("**Generalistas (PO-3, o outcome que o IED deveria mover):** " + "; ".join(frases)
             + " (vínculos por 10 mil hab., mudança pós − pré).")
    sec = est[(est["termo"] == "tau1_diferenca") & (est["familia"] == "bky")]
    sem_zero = [r for _, r in sec.iterrows() if _executada(r) and not _contem_zero(r)]
    if sem_zero:
        p.append("Secundárias com IC 95% convencional de τ₁ sem zero: " + "; ".join(
            f"{NOME[r['outcome']]} em {_ct(r['corte'])}: {fv(r)} {fic(r)}, q BKY {fp(r['q_bky'])}" for r in sem_zero)
            + ".")
    else:
        p.append("Nas secundárias (ΔB1, ΔB2, ΔB5), nenhuma diferença τ₁ tem IC 95% convencional sem zero.")
    mg = le["potencia"]["menor_grupo_lado"]
    p.append(f"**Potência.** O menor grupo × lado tem {mg['n_municipios']} municípios ({mg['outcome']}, corte "
             f"{_ct(mg['corte'])}, {'estrato muda' if mg['G'] == 1 else 'estrato não muda'}, {mg['lado']} do corte)"
             + (f"; {len(le['potencia']['grupos_lado_com_menos_de_10'])} grupos × lado ficam abaixo de 10 e são "
                "relatados como sem potência." if le["potencia"]["grupos_lado_com_menos_de_10"] else
                "; nenhum fica abaixo de 10.") + " Não detectar diferença entre grupos não é mostrar que ela é zero.")
    p.append("**O que isto é e o que não é.** Os grupos são definidos pelo porte, uma condição anterior ao tratamento, "
             "mas diferem também em tamanho, capital e região (seção 7). A diferença entre eles descreve "
             "heterogeneidade do salto do pacote do corte; não é o efeito do IED nem da bolsa isolada.")
    return "\n\n".join(p)


def tab_portao(resumo: dict) -> str:
    pt = resumo["portao"]
    linhas = [[x["linha"], x["como"], f"{x['n_abaixo_acima'][0]} / {x['n_abaixo_acima'][1]}",
               fn(x["tau_ref"], 6), fn(x["tau"], 6), f"{x['dif_tau']:.1e}", f"{x['dif_ep']:.1e}"]
              for x in pt["linhas"]]
    t = _tab(["Linha de base", "Como foi refeita", "n abaixo / acima", "Salto gravado", "Salto refeito",
              "Diferença absoluta no salto", "Diferença absoluta no EP"], linhas)
    jan = pt["g_lido_do_a10"]["codigo_do_anexo_vi_na_janela"]
    txt = "; ".join(f"em {_ct(k)}, {v['conferidos']} municípios na janela conferidos, {v['divergentes']} divergentes"
                    for k, v in jan.items())
    return (t + f"\n\nResultado: **aprovado** (máx |dif| = {pt['max_abs_dif']:.1e}, tolerância 1e−8). G vem de "
            f"`{pt['g_lido_do_a10']['fonte']}`; o estrato gravado no CSV do a10 bate com a regra código × porte em todos "
            f"os municípios, e o código de IVS do Anexo VI está do lado certo do corte pelo IVS oficial ({txt}).")


def tab_regra(resumo: dict) -> str:
    rg = resumo["regra_g"]
    linhas = []
    for c in CORTES:
        rc = rg["cortes"][ROT_CORTE[c]]
        for p in rg["portes"]:
            x = rc["por_porte"][str(p)] if str(p) in rc["por_porte"] else rc["por_porte"][p]
            linhas.append([TXT_CORTE[c], rg["rotulos_porte"][str(p)] if str(p) in rg["rotulos_porte"] else
                           rg["rotulos_porte"][p], f"{rc['codigo_ivs_abaixo']} → {rc['codigo_ivs_acima']}",
                           f"{x['estrato_abaixo']} → {x['estrato_acima']}",
                           "**muda (G = 1)**" if x["G"] == 1 else "não muda (G = 0)"])
    return (_tab(["Corte", "Porte (Anexo VI, IBGE 2022)", "Código de IVS (abaixo → acima)",
                  "Estrato do IED (abaixo → acima)", "Grupo"], linhas)
            + "\n\nCódigo de IVS 1 = muito alta … 5 = muito baixa; estrato 1 recebe mais por equipe. Cada degrau de "
              "estrato vale R$ 2.000 por equipe de saúde da família por mês (auditoria 18, §2.5).")


def tab_contagens(co: pd.DataFrame, resumo: dict) -> str:
    am = co[co["tipo"] == "amostra"]
    linhas = []
    for oid in OUTCOMES:
        for c in CORTES:
            s = am[(am["populacao"] == oid) & (am["corte"] == ROT_CORTE[c])].set_index(["G", "lado"])

            def cel(g, lado):
                r = s.loc[(g, lado)]
                extra = (f" ({fint(r['n_linhas'])} células)" if oid == "HI-1" else
                         f" ({fint(r['n_linhas'])} mun. × ciclo)" if oid == "HI-2" else "")
                return fint(r["n_municipios"]) + extra
            fora = int(s["fora_sem_porte"].iloc[0])
            linhas.append([NOME[oid], TXT_CORTE[c], cel(0, "abaixo"), cel(0, "acima"), cel(1, "abaixo"),
                           cel(1, "acima"), str(fora)])
    return (_tab(["Outcome", "Corte", "Não muda, abaixo", "Não muda, acima", "Muda, abaixo", "Muda, acima",
                  "Fora sem porte"], linhas)
            + "\n\nMunicípios distintos na janela h = 0,050 com outcome observado (decisão 11); entre parênteses, as "
              "linhas da regressão. Grupo × lado com menos de 10 municípios deixaria a linha sem estimativa.")


def tab_po(est: pd.DataFrame, oids, holm: bool) -> str:
    linhas = []
    for oid in oids:
        for c in CORTES:
            r = _linha(est, oid, c, "tau1_diferenca")
            ajust = fp(r["p_holm"]) if holm else fp(r["q_bky"])
            linhas.append([NOME[oid], TXT_CORTE[c], _ns(r), fint(r["n_obs"]),
                           fv(r) if _executada(r) else _status_txt(r), fic(r), fp(r["p_valor"]), ajust])
    return _tab(["Outcome", "Corte", "Municípios: não muda (abaixo / acima) · muda (abaixo / acima)", "Linhas",
                 "Diferença τ₁", "IC 95%", "p", "p Holm" if holm else "q BKY"], linhas)


def tab_po4(est: pd.DataFrame) -> str:
    linhas = []
    for oid in OUTCOMES:
        for c in CORTES:
            n, m = _linha(est, oid, c, "tau0_nao_muda"), _linha(est, oid, c, "tau0_mais_tau1_muda")
            linhas.append([NOME[oid], TXT_CORTE[c], (fv(n) + " " + fic(n)) if _executada(n) else _status_txt(n),
                           fp(n["p_valor"]), (fv(m) + " " + fic(m)) if _executada(m) else _status_txt(m),
                           fp(m["p_valor"])])
    return (_tab(["Outcome", "Corte", "Salto onde o estrato não muda (τ₀) [IC 95%]", "p",
                  "Salto onde o estrato muda (τ₀ + τ₁) [IC 95%]", "p"], linhas)
            + "\n\nHI-1 em pontos percentuais; HI-2 em médicos alocados por município, comparando municípios com as "
              "mesmas vagas imediatas; ΔB1, ΔB2 e ΔB5 por 10 mil hab., mudança da média do pós menos a do pré. "
              "Descritivo: fora do Holm e do BKY.")


def tab_balanco(co: pd.DataFrame) -> str:
    b = co[co["tipo"] == "balanco"]
    linhas = []
    for _, r in b.iterrows():
        linhas.append([r["populacao"].split(" (")[0], _ct(r["corte"]), "muda" if int(r["G"]) == 1 else "não muda",
                       r["lado"], fint(r["n_municipios"]), _pct(r["frac_capital"]),
                       *[_pct(r[f"frac_{rg}"]) for rg in REGIOES]])
    return (_tab(["População", "Corte", "Estrato", "Lado", "Municípios", "Capitais", *REGIOES], linhas)
            + "\n\nH1: municípios distintos da amostra da HI-2 (qualquer ciclo) na janela; V: municípios da amostra de "
              "ΔB1 na janela. Médias simples, sem teste. Capital e região pela referência do IBGE gravada "
              "(`output/aquisicao/ibge_capitais_uf_regiao.csv`).")


def leitura_txt(resumo: dict) -> str:
    le = resumo["leitura"]
    p = [f"**PO-1:** código `{le['po1']['codigo']}`. Regra (decisão 16): `TAU1_TODOS_CONTEM_ZERO` se as quatro τ₁ "
         "têm IC 95% que contém zero; `TAU1_REJEITA_HOLM_CONCENTRADO` se alguma τ₁ tem p de Holm abaixo de 0,05 e, "
         "nela, o IC de τ₀ + τ₁ exclui zero e o de τ₀ contém zero; `TAU1_REJEITA_HOLM_SEM_CONCENTRACAO` se rejeita "
         "depois do Holm sem essa concentração; `TAU1_IC_EXCLUI_ZERO_SEM_HOLM` se algum IC convencional de τ₁ exclui "
         "zero e nenhum p de Holm fica abaixo de 0,05."]
    p.append(TXT_PO1[le["po1"]["codigo"]])
    for c in CORTES:
        x = le["po3"][ROT_CORTE[c]]
        p.append(f"**PO-3 em {TXT_CORTE[c]}:** código `{x['codigo']}`"
                 + ("" if x["codigo"] == "SEM_ESTIMATIVA" else
                    f"; τ₁ com q BKY {'abaixo' if x['tau1_q_abaixo_de_0_05'] else 'acima'} de 0,05") + ". Regra: "
                 "`INDICIO_IED_MOVE_APS` se o IC do salto de generalistas onde o estrato muda exclui zero e o IC onde "
                 "não muda contém zero; senão `SEM_INDICIO`.")
    sp = le["potencia"]["grupos_lado_com_menos_de_10"]
    p.append("**Potência:** " + ("; ".join(f"{x['outcome']} em {_ct(x['corte'])}, G = {x['G']}, {x['lado']}: "
                                           f"{x['n_municipios']} municípios, sem potência para esse grupo" for x in sp)
                                 if sp else "nenhum grupo × lado com menos de 10 municípios.")
             + " Mesmo acima de 10, cada grupo tem poucas dezenas de municípios perto do corte.")
    return "\n\n".join(p)


COMO_LER = (
    "Como ler: cada painel é um outcome; em cada corte há três linhas. \"Não muda\" é o salto no corte (lado de bolsa "
    "maior menos lado de bolsa menor) nos portes em que o estrato do IED fica igual dos dois lados; \"muda\" é o salto "
    "nos portes em que, acima do corte, o estrato passa a um degrau de repasse maior; \"diferença\" é muda menos não muda (τ₁). Ponto = estimativa; barra = "
    "IC 95%. Azul: o IC exclui zero; cinza: contém zero. Barra que cruza a linha do zero quer dizer que não se detecta "
    "diferença, não que ela seja zero. Os grupos diferem também em tamanho, capital e região: é heterogeneidade "
    "descritiva do pacote do corte, não o efeito do IED.")
FONTE = ("Fonte: outcomes do 12 (H1, ciclos 1–3; ciclo 2 pelo quadro de 13/02/2026), CNES nacional a09 (ΔB, "
         "2024-06 a 2026-08), IVS 2010 oficial (a08), Portaria 3.493/2024 Anexo VI (a10). EMPIRICO · "
         "scripts/rdd_bolsa/47_heterogeneidade_porte_ied.py")


def figura_txt(resumo: dict) -> str:
    f = resumo["figura"]
    return f"![PO_salto_por_grupo](../../{f['arquivo']})\n\n**{f['como_ler']}**"


def limites_txt(co: pd.DataFrame, resumo: dict) -> str:
    comp = "; ".join(_composicao_g(co, resumo, c) for c in CORTES)
    lim = [
        "**Descritivo, não causal do IED.** O porte é anterior ao tratamento, mas os portes em que o estrato muda "
        "diferem dos outros em tamanho, capital e região (seção 7) e em outras regras que dependem do porte. A "
        "diferença τ₁ mistura o canal do IED com tudo o que difere entre esses municípios perto do corte.",
        "**Os grupos não são os mesmos nos dois cortes.** " + comp[0].upper() + comp[1:] + ". A τ₁ de um corte e a "
        "do outro não comparam o mesmo tipo de município.",
        "**Pacote do corte.** Em 0,300 e 0,400 mudam a bolsa anunciada e outras regras federais (auditoria 18). Mesmo "
        "onde o estrato não muda, o salto é de um pacote, não da bolsa isolada; nada aqui isola o incentivo de "
        "R$ 5 mil, a participação no PMM-E ou o Agora Tem Especialistas.",
        "**Pós-resultado.** A H1 e a oferta local no corte já tinham sido vistas; só a divisão por porte é nova. A "
        "especificação e as decisões foram fixadas antes destas contas.",
        "**Potência.** Cada grupo × lado tem poucas dezenas de municípios na janela (seção 3); os IC da diferença são "
        "mais largos que os da H1 sem divisão. Não detectar diferença não é mostrar que ela é zero.",
        "**Retas por ciclo × grupo.** Na H1 cada ciclo × grupo tem retas próprias de cada lado; com poucos municípios "
        "por ciclo × grupo, as retas são imprecisas, e é isso que alarga os IC.",
        "**IED e compensação.** O art. 12-T da 3.493/2024 compensa quem perderia recursos frente às doze parcelas "
        "anteriores (auditoria 18, §2.5): o degrau de estrato pode valer menos que R$ 2.000 por equipe no curto prazo. "
        "O grupo G marca onde a regra muda o estrato, não quanto dinheiro mudou.",
        "**Porte de 2022.** O porte é o do Anexo VI (IBGE 2022). A H1 e a oferta local são de 2025–2026; um município "
        "que tenha mudado de porte depois não muda de grupo aqui.",
    ]
    return "\n".join(f"- {x}" for x in lim)


def gerar_blocos(est: pd.DataFrame, co: pd.DataFrame, resumo: dict) -> dict[str, str]:
    return {
        "resposta_curta": resposta_curta(est, co, resumo),
        "portao": tab_portao(resumo),
        "regra_g": tab_regra(resumo),
        "contagens": tab_contagens(co, resumo),
        "po1": tab_po(est, ("HI-1", "HI-2"), True)
        + "\n\nτ₁ = salto onde o estrato muda − salto onde não muda. Holm entre as quatro linhas (decisão 12).",
        "po2_po3": tab_po(est, ("B1", "B2", "B5"), False)
        + "\n\nBKY entre as seis linhas (ΔB1 e ΔB2 da PO-2; ΔB5 da PO-3). Um município por linha, EP HC1.",
        "po4": tab_po4(est),
        "balanco": tab_balanco(co),
        "leitura": leitura_txt(resumo),
        "figura": figura_txt(resumo),
        "limites": limites_txt(co, resumo),
    }


def atualizar_doc(est: pd.DataFrame, co: pd.DataFrame, resumo: dict) -> None:
    txt = DOC.read_text(encoding="utf-8")
    blocos = gerar_blocos(est, co, resumo)
    achados = {m.group("nome") for m in MARCA.finditer(txt)}
    falta = set(blocos) - achados
    if falta:
        raise FalhaValidacao(f"doc 57u sem os marcadores {sorted(falta)}")
    txt = MARCA.sub(lambda m: bloco(m.group("nome"), blocos[m.group("nome")]) if m.group("nome") in blocos
                    else m.group(0), txt)
    DOC.write_text(txt, encoding="utf-8")


# ---------------------------------------------------------------------------
# 9. Figura
# ---------------------------------------------------------------------------

AZUL, CINZA, TINTA, TINTA2 = T40.AZUL, T40.CINZA, T40.TINTA, T40.TINTA2
VERDE_ESC = T40.VERDE_ESC


def gerar_figura(est: pd.DataFrame, destino: Path) -> None:
    plt = T40._plt()
    W = 12.3
    ALT_LIN, ALT_TIT, ALT_EIXO = 0.36, 0.42, 0.55
    paineis = []
    for oid in OUTCOMES:
        esc = 100.0 if oid == "HI-1" else 1.0
        its = []
        for c in CORTES:
            for termo, rot in (("tau0_nao_muda", "não muda"), ("tau0_mais_tau1_muda", "muda"),
                               ("tau1_diferenca", "diferença")):
                r = _linha(est, oid, c, termo)
                ok = _executada(r)
                its.append({"rot": f"{TXT_CORTE[c]} · {rot}", "tau": esc * float(r["tau"]) if ok else np.nan,
                            "lo": esc * float(r["ic95_inf"]) if ok else np.nan,
                            "hi": esc * float(r["ic95_sup"]) if ok else np.nan,
                            "cor": (CINZA if _contem_zero(r) else AZUL) if ok else CINZA,
                            "valor": f"{fv(r)} {fic(r)}" if ok else _status_txt(r)})
        eixo = ("salto (p.p.)" if oid == "HI-1" else "salto (médicos por município)" if oid == "HI-2" else
                "salto (por 10 mil hab., pós − pré)")
        paineis.append({"titulo": NOME[oid], "eixo": eixo, "linhas": its})
    linhas_txt = textwrap.wrap(COMO_LER, 132)
    h_rodape = 0.30 * len(linhas_txt) + 0.45 + 0.17 * len(textwrap.wrap(FONTE, 170))
    H_ = 0.55 + sum(ALT_TIT + ALT_LIN * len(p["linhas"]) + ALT_EIXO for p in paineis) + h_rodape
    fig = plt.figure(figsize=(W, H_))
    fig.text(0.1 / W, (H_ - 0.1) / H_, "Salto no corte onde o estrato do IED muda e onde não muda",
             fontsize=15, weight="bold", color=TINTA, va="top")
    y = H_ - 0.55
    x_plot, w_plot = 2.6, 5.6
    for p in paineis:
        fig.text(0.1 / W, (y - 0.05) / H_, p["titulo"], fontsize=13, weight="bold", color=VERDE_ESC, va="top")
        n = len(p["linhas"])
        y0 = y - ALT_TIT - ALT_LIN * n
        ax = fig.add_axes([x_plot / W, y0 / H_, w_plot / W, (ALT_LIN * n) / H_])
        vals = [0.0] + [v for ln in p["linhas"] for v in (ln["lo"], ln["hi"]) if np.isfinite(v)]
        lo, hi = min(vals), max(vals)
        pad = 0.06 * (hi - lo if hi > lo else 1.0)
        ax.set_xlim(lo - pad, hi + pad)
        ax.set_ylim(n - 0.5, -0.5)
        ax.axvline(0, color="#2b2b2b", lw=1.3, zorder=1)
        for i, ln in enumerate(p["linhas"]):
            if np.isfinite(ln["tau"]):
                ax.plot([ln["lo"], ln["hi"]], [i, i], color=ln["cor"], lw=3.0, solid_capstyle="butt", zorder=2)
                ax.scatter([ln["tau"]], [i], s=80, color=ln["cor"], edgecolor="white", zorder=3)
            ax.text(-0.02, i, ln["rot"], transform=ax.get_yaxis_transform(), ha="right", va="center", fontsize=11.5,
                    color=TINTA)
            ax.text(1.02, i, ln["valor"], transform=ax.get_yaxis_transform(), ha="left", va="center", fontsize=11.5,
                    color=TINTA)
        for j in (2.5,):
            ax.axhline(j, color="#d9d8d4", lw=0.8, zorder=0)
        ax.set_yticks([])
        ax.tick_params(axis="x", labelsize=11, colors=TINTA2)
        ax.xaxis.set_major_formatter(T40._fmt_eixo())
        for lado in ("top", "right", "left"):
            ax.spines[lado].set_visible(False)
        ax.set_xlabel(p["eixo"], fontsize=11, color=TINTA2, labelpad=3)
        y = y0 - ALT_EIXO
    yy = h_rodape - 0.15
    for t in linhas_txt:
        fig.text(0.1 / W, yy / H_, t, fontsize=12, color=TINTA, va="top")
        yy -= 0.30
    for k, t in enumerate(reversed(textwrap.wrap(FONTE, 170))):
        fig.text(0.1 / W, (0.05 + 0.17 * k) / H_, t, fontsize=8.5, color=CINZA, va="bottom")
    fig.savefig(destino, dpi=200, facecolor="white", metadata={"Software": None})
    plt.close(fig)


# ---------------------------------------------------------------------------
# 10. Resumo, gravação e CLI
# ---------------------------------------------------------------------------

def entradas() -> list[dict]:
    # Auditoria 45 (A5): também as lidas pelos construtores importados (rastreio de arquivos abertos na execução):
    # U e G3 (E6.chaves_populacoes), lista nominal e lista de ativos (V do 43), manifesto da referência do IBGE.
    arqs = [A10_CSV, A10_JSON, A08, T40.ARQ_VC, T40.ARQ_VM, T40.ARQ_C2_13FEV, HI_EST, HI_RES, OC_EST, OC_RES,
            T43.OL.PAINEL, T43.OL.POP22, T43.OL_RESUMO, T44.REF_IBGE, ADENDO, T40.ARQ_U, T40.E6.ARQ_G3,
            T43.D2M.NOMINAL, T43.OL.ATIVOS_ZIP, T44.REF_MANIF]
    return [{"arquivo": rotulo(p), "sha256": sha256(p)} for p in arqs]


def montar_resumo(est, co, regra, port, extras, oc) -> dict:
    hi_res = json.loads(HI_RES.read_text(encoding="utf-8"))
    oc_res = json.loads(OC_RES.read_text(encoding="utf-8"))
    resumo = {
        "etapa": "Adendo 48g: heterogeneidade do salto pelo porte em que o estrato do IED muda (PO-1 a PO-5)",
        "natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "data_execucao": DATA_EXECUCAO,
        "script": "scripts/rdd_bolsa/47_heterogeneidade_porte_ied.py",
        "adendo": {"arquivo": rotulo(ADENDO), "sha256": sha256(ADENDO), "commit_congelamento": COMMIT_CONGELAMENTO,
                   "commit_decisoes_57u": COMMIT_DECISOES},
        "contraste": CONTRASTE,
        "parametros": {"cortes_mil": list(CORTES), "h": H / 1000.0, "kernel": "triangular",
                       "min_municipios_grupo_lado": MIN_UNIDADES, "ciclos_h1": list(CICLOS),
                       "quadro_ciclo2": "13/02/2026 (adendo 48b, nota 7)", "limite_cnes_exclusivo": LIMITE_CNES,
                       "maior_competencia_cnes_lida": oc["maior_competencia"],
                       "holm": "tau1 de HI-1 e HI-2 x dois cortes (4)",
                       "bky": "tau1 de dB1 e dB2 (PO-2) e dB5 (PO-3) x dois cortes (6)",
                       "familia_tamanho_fixo": "linha sem estimativa entra com p = 1 so no calculo"},
        "regra_g": regra,
        "portao": port,
        "amostra": {"janela": extras["janela"], "V_municipios": oc["n_V"],
                    "sem_estimativa": extras["sem_estimativa"]},
        "referencias": {"hi_leitura_primaria": hi_res["leitura_primaria"]["codigo"],
                        "hi_linhas_ic_convencional_sem_zero":
                            hi_res["leitura_primaria"]["linhas_com_ic_convencional_sem_zero"],
                        "oc_leitura": oc_res.get("leitura", {})},
        "entradas": entradas(),
        "integridade": {"ivs": "IVS 2010 oficial (a08), pelas funcoes dos scripts 40 e 43; o arquivo local de IVS da "
                               "auditoria 16 nao e lido",
                        "cnes": f"painel a09 so com competencias < {LIMITE_CNES} (conferido)",
                        "imputacao": "nada imputado, simulado ou adquirido",
                        "saidas_nao_regravadas": ["HI_*", "OC_*", "CL_*", "PM_*"],
                        "dados_pessoais": "nenhum identificador pessoal (unidades: celula e municipio)"},
        "saidas": {"estimativas": rotulo(OUT / NOME_EST), "contagens": rotulo(OUT / NOME_CONT),
                   "resumo": rotulo(OUT / NOME_RESUMO), "figuras": rotulo(DIR_FIG), "doc": rotulo(DOC)},
        "contagens": {"linhas": int(len(est)), "por_status": est["status"].value_counts().sort_index().to_dict(),
                      "por_id_po": est["id_po"].value_counts().sort_index().to_dict()},
        "linguagem": "pacote do corte; heterogeneidade descritiva; 'nao se detecta' nao e 'zero'",
    }
    resumo["leitura"] = leituras(est, co)
    resumo["primarias"] = {f"{r['outcome']} {r['corte']}": {k: (float(r[k]) if np.isfinite(float(r[k])) else None)
                                                            for k in ("tau", "ep", "ic95_inf", "ic95_sup", "p_valor",
                                                                      "p_holm")}
                           for _, r in est[(est["familia"] == "holm")].iterrows()}
    return resumo


def gravar_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(_nan_none(obj), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ler_saidas() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    est = pd.read_csv(OUT / NOME_EST, dtype={"corte": str, "portes_G1": str, "portes_G0": str})
    for c in ("familia", "nota"):
        est[c] = est[c].fillna("")
    co = pd.read_csv(OUT / NOME_CONT, dtype={"corte": str})
    co["nota"] = co["nota"].fillna("")
    return est, co, json.loads((OUT / NOME_RESUMO).read_text(encoding="utf-8"))


def executar() -> int:
    if sha256(ADENDO) != SHA_ADENDO:
        raise FalhaValidacao("o adendo 48g mudou depois do congelamento")
    print("Lendo a regra do IED (a10)...", flush=True)
    regra = regra_g()
    a10 = ler_a10(regra)
    print("Carregando a H1 (script 40) e a oferta local (script 43)...", flush=True)
    h1 = carregar_h1()
    oc = carregar_oc()
    print("Portão: HI-1, HI-2 e OC-A1 em 0,300 e G lido do a10...", flush=True)
    port = portao(h1, oc, regra, a10)
    print(f"  aprovado: máx |dif| = {port['max_abs_dif']:.2e}", flush=True)
    print("Estimando PO-1 a PO-5...", flush=True)
    est, co, extras = estimar(h1, oc, regra, a10)
    resumo = montar_resumo(est, co, regra, port, extras, oc)
    OUT.mkdir(parents=True, exist_ok=True)
    DIR_FIG.mkdir(parents=True, exist_ok=True)
    est.to_csv(OUT / NOME_EST, index=False)
    co.to_csv(OUT / NOME_CONT, index=False)
    gerar_figura(est, DIR_FIG / NOME_FIG)
    resumo["figura"] = {"arquivo": rotulo(DIR_FIG / NOME_FIG), "sha256": sha256(DIR_FIG / NOME_FIG),
                        "como_ler": COMO_LER, "fonte": FONTE}
    gravar_json(OUT / NOME_RESUMO, resumo)
    # Doc a partir do que foi gravado (mesmo caminho do --atualizar-doc).
    atualizar_doc(*ler_saidas())
    for _, r in est[est["termo"] == "tau1_diferenca"].iterrows():
        print(f"  {r['id_po']} {r['outcome']} {r['corte']}: tau1 = {r['tau']:.4f} [{r['ic95_inf']:.4f}; "
              f"{r['ic95_sup']:.4f}] p = {r['p_valor']:.4f} holm = {r['p_holm']} bky = {r['q_bky']}", flush=True)
    print(f"Gravado: {rotulo(OUT / NOME_EST)} ({len(est)} linhas), {rotulo(OUT / NOME_CONT)}, "
          f"{rotulo(OUT / NOME_RESUMO)}, {rotulo(DIR_FIG)}/, doc {rotulo(DOC)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--atualizar-doc", action="store_true", help="só regrava os blocos do doc 57u a partir das saídas")
    args = ap.parse_args(argv)
    try:
        if args.atualizar_doc:
            atualizar_doc(*ler_saidas())
            print(f"blocos PO regravados: {rotulo(DOC)}")
            return 0
        return executar()
    except (FalhaValidacao, T40.FalhaValidacao, T43.FalhaValidacao) as erro:
        print(f"FALHA (nada gravado): {erro}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
