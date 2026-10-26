"""Adendo 48d: H1 e oferta local no corte com controles de localização (L) e de médicos na região (M), e pareamento.

Especificação congelada antes das contas: `docs/06_execucao/48d_adendo_controles_localizacao_e_medicos.md`
(26/10/2026, commit 148479c), com a nota §3.2 (commit ff62365: o pareamento por escore de propensão, PS-1 e PS-2,
passa a ser o principal; controles somados e Mahalanobis viram secundários). SHA-256 conferido abaixo. Estatuto:
`ADENDO_48D_POS_RESULTADO`; `natureza_dos_dados = EMPIRICO` em toda saída. As decisões de implementação estão na
seção 0 do doc 57r, escritas antes de qualquer estimativa (commit 05830ac).

O que faz, na ordem
-------------------
1. Portão: reproduz HI-1 e HI-2 do adendo 48b (`HI_estimativas.csv`, script 40) nos dois cortes, com diferença
   <= 1e-8, pelas funções do script 40 e pela função com covariáveis deste script sem covariável. Se falhar, para sem
   gravar nada.
2. Covariáveis pré-determinadas (só `output/`):
   - L: capital e macrorregião (referência do IBGE do 48c, lida pela função do script 41), log(população do Censo
     2022, a mesma do E7);
   - M: médicos (CBO 2251, 2252, 2253) e especialistas nas CBO-alvo por 10 mil hab. no município e especialistas
     nas CBO-alvo no resto da região de saúde, média de 2024-06 a 2025-06 do painel a09.
   Nada imputado: ausente fica ausente e a unidade sai das linhas que usam a variável, contada.
3. H1 (48b) por corte: CL-0 (balanço), CL-1 (L+M), CL-2 (L; M; L-UF + M), CL-3 (cada variável), CL-4 (sem controle
   na amostra de L+M); pareamento por Mahalanobis (CL-7, CL-9 da H1) e por escore de propensão (PS-1, PS-3 e PS-4
   da H1).
4. Oferta local (protocolo 64): CL-5, CL-6, CL-8, CL-9 da oferta local, PS-2 e PS-3/PS-4 da oferta local só rodam
   quando as saídas `OC_*` do protocolo 64 existem, depois de reproduzir OC-A1 em 0,300 (<= 1e-8); ΔB1–ΔB5 vêm das
   funções do script 43, importadas. Sem elas, essas
   linhas ficam `PENDENTE_OC`, sem número, contadas. `--so-oferta-local` roda só essa parte sobre as saídas H1 já
   gravadas.
5. Holm nas principais (PS-1 e PS-2); BKY nas secundárias (CL-1, CL-2, CL-3, CL-5, CL-6, CL-7, CL-8). Com linha
   pendente, os dois são provisórios (pendentes contadas com p = 1).
6. Figuras com "Como ler" e os blocos do doc 57r (`--atualizar-doc`).

Integridade: o arquivo local de IVS da auditoria 16 não é lido (running variable = IVS 2010 oficial, a08); a região de
saúde vem da tabela oficial da CIR (função do script 19; a malha de regiões, que traz IVS, IDHM e renda, não é
lida); nenhuma
competência do CNES >= 202609; nada é escrito em `data/`; as saídas HI_, HC_, OC_, E7_ e do protocolo 60 não são
regravadas.

Uso
---
    python3 scripts/rdd_bolsa/44_controles_localizacao_medicos.py                   # H1 (+ oferta local se OC_*)
    python3 scripts/rdd_bolsa/44_controles_localizacao_medicos.py --atualizar-doc   # idem e regrava os blocos do 57r
    python3 scripts/rdd_bolsa/44_controles_localizacao_medicos.py --so-oferta-local # só a parte do protocolo 64
    python3 scripts/rdd_bolsa/44_controles_localizacao_medicos.py --so-doc          # só regrava os blocos do 57r
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import re
import sys
import textwrap
import warnings
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


T40 = _importar(DIR_RDD / "40_h1_vagas_imediatas.py", "h1_vagas_imediatas_para_cl")
T41 = _importar(DIR_RDD / "41_h1_capitais_uf.py", "h1_capitais_uf_para_cl")
T37 = _importar(DIR_RDD / "37_oferta_local_chegada.py", "oferta_local_chegada_para_cl")
T43 = _importar(DIR_RDD / "43_oferta_local_corte.py", "oferta_local_corte_para_cl")
T19 = _importar(DIR_RDD / "19_escolha_heterogeneidade.py", "escolha_heterogeneidade_para_cl")   # CIR oficial
T23 = T40.T23
L = T40.L
E7 = T37.E7
K1M = T37.K1M
D2M = T37.D2M

# ---------------------------------------------------------------------------
# Parâmetros do adendo
# ---------------------------------------------------------------------------

OUT = ROOT / "output" / "rdd_bolsa"
AQ = ROOT / "output" / "aquisicao"
ADENDO = ROOT / "docs" / "06_execucao" / "48d_adendo_controles_localizacao_e_medicos.md"
DOC = ROOT / "docs" / "06_execucao" / "57r_resultados_controles_localizacao_medicos.md"
HI_EST = OUT / "HI_estimativas.csv"
OC_EST = OUT / "OC_estimativas.csv"
OC_RES = OUT / "OC_resumo.json"
OL_RES = OUT / "OL_resumo.json"
PAINEL = E7.PAINEL
MANIF_A09 = E7.MANIFESTO_A09
POP22 = E7.POP22
A08 = E7.A08
CIR_BRUTO = T19.CIR_BRUTO                 # tabela oficial município -> CIR (TabNet/DATASUS), só lida
CIR_MANIF = T19.OUT_MANIFESTO_CIR
REF_IBGE = T41.REF_CSV
REF_MANIF = T41.REF_MANIFESTO

NOME_EST = "CL_estimativas.csv"
NOME_BAL = "CL_balanco.csv"
NOME_RESUMO = "CL_resumo.json"
DIR_FIG = OUT / "CL_figuras"

DATA_EXECUCAO = "2026-10-26"
ESTATUTO = "ADENDO_48D_POS_RESULTADO"
NATUREZA = "EMPIRICO"
COMMIT_CONGELAMENTO = "148479c"
COMMIT_NOTA_32 = "ff62365"
COMMIT_DECISOES = "05830ac"
SHA_ADENDO = "d0b255d31f2cb2f3783ca5c44752dadb713aa7c39c25f003eb03835d97ef730f"   # com a nota §3.2
CORTES = (300, 400)
H = 50                                  # h = 0,050 (48b e protocolo 64)
CICLOS = (1, 2, 3)
JANELA_PAR = 50                         # pareamento: |IVS - corte| <= 0,050
JANELA_SENS = 20                        # CL-9 e PS-3: <= 0,020
CALIPER_MAH = 0.25
CALIPER_PS = 0.2
APARO_IPW = (0.05, 0.95)
N_PERM = 9_999
SEMENTE = 20261026
TOL_PORTAO = 1e-8
ALFA = 0.05
LIMIAR_DP_META = 0.10
LIMIAR_DP_LIMPA = 0.25
ESCALA_HAB = 1e4
LIMITE_CNES = "202609"
COMP_PRE = tuple(E7.COMP_PRE)           # 202406 a 202506 (13 competências)
COMP_POS = tuple(E7.COMP_POS)           # 202510 a 202608
REGIOES = ("Centro-Oeste", "Nordeste", "Norte", "Sudeste", "Sul")
REGIAO_REF = "Centro-Oeste"
TXT_CORTE = {300: "0,300", 400: "0,400"}
ROT_CORTE = {300: "0.300", 400: "0.400"}
BOLSA = {300: "R$ 10 mil → R$ 15 mil", 400: "R$ 15 mil → R$ 20 mil"}
GRUPOS_MED = ("alvo_pmme", "generalistas", "especialistas_nao_alvo")    # = CBO 2251, 2252, 2253 (disjuntos)
STATUS_PEND = "PENDENTE_OC"

VARIAVEIS = ("capital", "regiao", "log_pop", "med", "esp", "esp_resto")
NOME_VAR = {"capital": "capital", "regiao": "macrorregião (efeito fixo)", "uf": "UF (efeito fixo)",
            "log_pop": "log(população 2022)", "med": "médicos por 10 mil hab. no município",
            "esp": "especialistas nas CBO-alvo por 10 mil hab. no município",
            "esp_resto": "especialistas nas CBO-alvo por 10 mil hab. no resto da região de saúde"}
CONJUNTOS = {"L": ("capital", "regiao", "log_pop"), "M": ("med", "esp", "esp_resto"),
             "L+M": ("capital", "regiao", "log_pop", "med", "esp", "esp_resto"),
             "LUF+M": ("capital", "uf", "log_pop", "med", "esp", "esp_resto")}
CONTINUAS = ("log_pop", "med", "esp", "esp_resto")

UN_FRAC = "fracao (x100 = p.p.)"
UN_CONT = "medicos alocados por municipio"
UN_VAGA = "medicos alocados por vaga imediata"
UN_OC = "por 10 mil hab. (Censo 2022), media pos - media pre"

OUT_H1 = {
    "HI-1": {"desc": "celula com vaga imediata preenchida na 1a chamada (48b)", "unidade": UN_FRAC,
             "unidade_analise": "celula", "y": "preenchida"},
    "HI-2": {"desc": "medicos alocados na 1a chamada em celulas com vaga imediata, por municipio, controle = vagas "
                     "imediatas por ciclo (48b)", "unidade": UN_CONT, "unidade_analise": "municipio x ciclo",
             "y": "aloc_imed"},
}
OUT_PAR_H1 = {
    "H1M-FRAC": {"desc": "fracao das celulas com vaga imediata preenchidas na 1a chamada, por municipio x ciclo",
                 "unidade": UN_FRAC, "col": "frac_preenchida", "rdd": "HI-1"},
    "H1M-ALOC": {"desc": "medicos alocados na 1a chamada em celulas com vaga imediata por vaga imediata, por "
                         "municipio x ciclo", "unidade": UN_VAGA, "col": "aloc_por_vi", "rdd": "HI-2"},
}
OUT_OC = {
    "dB1": {"oc": "OC-A1", "b": "B1", "desc": "Delta vinculos de especialistas nas CBO-alvo (B1)"},
    "dB2": {"oc": "OC-A2", "b": "B2", "desc": "Delta horas SUS semanais nas CBO-alvo (B2)"},
    "dB3": {"oc": "OC-A3", "b": "B3", "desc": "Delta horas SUS dos outros especialistas, sem os do PMM-E (B3)"},
    "dB4": {"oc": "OC-A4", "b": "B4", "desc": "Delta horas totais nas CBO-alvo (B4)"},
    "dB5": {"oc": "OC-A5", "b": "B5", "desc": "Delta vinculos de generalistas, placebo (B5)"},
}

CONTRASTE = ("pacote do corte: em 0,300 a bolsa anunciada sobe de R$ 10 mil para R$ 15 mil e em 0,400 de R$ 15 mil "
             "para R$ 20 mil, mas outras regras federais mudam nos mesmos cortes (auditoria 18); nao e efeito da "
             "participacao no PMM-E nem do Agora Tem Especialistas")

COLUNAS = [
    "natureza_dos_dados", "estatuto", "id_linha", "bloco", "papel", "parte", "outcome", "descricao_outcome",
    "unidade_analise", "populacao", "corte", "janela", "conjunto", "variaveis", "metodo", "estimador", "status",
    "tau", "ep", "ic95_inf", "ic95_sup", "p_valor", "ic_t_inf", "ic_t_sup", "p_t", "n_abaixo", "n_acima", "n_obs",
    "n_clusters", "media_abaixo", "tau_sem_controle", "ic_sem_controle_inf", "ic_sem_controle_sup",
    "p_sem_controle", "variacao_abs", "variacao_pct", "saiu_ausencia_abaixo", "saiu_ausencia_acima",
    "n_pares", "sem_par_abaixo", "sem_par_acima", "fora_suporte_abaixo", "fora_suporte_acima", "max_abs_dp_antes",
    "max_abs_dp_depois", "comparacao_limpa", "entra_holm", "p_holm", "entra_bky", "q_bky",
    "multiplicidade_provisoria", "covariaveis_descartadas", "unidade", "nota",
]
COLUNAS_BAL = [
    "natureza_dos_dados", "estatuto", "tipo", "bloco", "parte", "populacao", "unidade_analise", "corte", "janela",
    "metodo", "variavel", "media_acima_antes", "media_abaixo_antes", "dp_antes", "media_acima_depois",
    "media_abaixo_depois", "dp_depois", "n_acima_antes", "n_abaixo_antes", "n_acima_depois", "n_abaixo_depois",
    "tau", "ep", "ic95_inf", "ic95_sup", "p_valor", "dp_janela", "salto_padronizado", "n_abaixo", "n_acima",
    "n_obs", "status", "nota",
]


class FalhaValidacao(RuntimeError):
    """Portão ou validação obrigatória falhou: o script para sem gravar."""


sha256 = T23.sha256
rotulo = T23.rotulo
_nan_none = T40._nan_none


def _juntar(*notas) -> str:
    return "; ".join(str(n) for n in notas if n)


def _f(x) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return float("nan")
    return v


# ---------------------------------------------------------------------------
# 1. Covariáveis pré-determinadas (L e M)
# ---------------------------------------------------------------------------

def ler_referencia_ibge() -> tuple[pd.DataFrame, dict]:
    """Capitais e macrorregião: função do script 41 (SHA-256 contra o manifesto, 27 UFs com uma capital cada),
    conferida aqui de novo contra o a08 e a lista da auditoria 36."""
    ref, man = T41.carregar_referencias()
    a08 = pd.read_csv(A08, dtype={"co_ibge": str})
    cods = set(K1M._ibge6(a08["co_ibge"]))
    if not set(ref["capital_co_ibge_6d"]) <= cods:
        raise FalhaValidacao("capital da referência do IBGE fora do IVS oficial a08")
    if set(ref["capital_co_ibge_6d"]) != set(T41.A36.CAPITAIS):
        raise FalhaValidacao("capitais da referência do IBGE diferem da lista da auditoria 36")
    if ref["cd_uf"].duplicated().any() or set(ref["nome_regiao"]) != set(REGIOES):
        raise FalhaValidacao("referência do IBGE sem 27 UFs ou sem as 5 Grandes Regiões")
    return ref, {"arquivo": rotulo(REF_IBGE), "sha256": sha256(REF_IBGE), "manifesto": rotulo(REF_MANIF),
                 "capitais": 27, "conferida_contra": "a08 e A36.CAPITAIS (auditoria 36)"}


def ponte_cursos() -> dict[int, list[str]]:
    """CBO-alvo de cada curso pela ponte do manifesto a09 (cbo_para_cursos)."""
    m = json.loads(MANIF_A09.read_text(encoding="utf-8"))
    out: dict[int, list[str]] = {}
    for cbo, cursos in m["ponte"]["cbo_para_cursos"].items():
        for k in cursos:
            out.setdefault(int(k), []).append(str(cbo))
    if sorted(out) != list(range(1, 17)):
        raise FalhaValidacao(f"ponte do a09 sem os cursos 1 a 16: {sorted(out)}")
    cbos = sorted({c for v in out.values() for c in v})
    if cbos != sorted(m["ponte"]["cbos_alvo"]):
        raise FalhaValidacao("ponte do a09: CBO dos cursos diferem das CBO-alvo")
    return {k: sorted(v) for k, v in sorted(out.items())}


def _media_pre(p: pd.DataFrame, grupo: str, universo: pd.Index) -> tuple[pd.Series, pd.DataFrame]:
    """Média de n_vinculos nas 13 competências do pré; sem todas as competências (ou com valor ausente), NaN."""
    s = p[p["grupo"] == grupo].pivot(index="co_ibge", columns="competencia", values="n_vinculos")
    s = s.apply(pd.to_numeric, errors="coerce").astype(float).reindex(index=universo, columns=list(COMP_PRE))
    completo = s.notna().all(axis=1)
    return s.mean(axis=1).where(completo), s


def _resto_regiao(cnt: pd.Series, pop: pd.Series, regiao: pd.Series) -> tuple[pd.Series, dict]:
    """(vínculos da região − do município) ÷ (população da região − do município) × 10 mil.

    Região de um município só, município sem região, ou outro município da região sem a média: NaN."""
    d = pd.DataFrame({"cnt": cnt, "pop": pop, "reg": regiao})
    tem_reg = d["reg"].notna()
    g = d[tem_reg].groupby("reg")
    n = g["cnt"].transform("size")
    falta = g["cnt"].transform(lambda v: int(v.isna().sum())) + g["pop"].transform(lambda v: int(
        (~(v > 0)).sum()))
    pop_ok = d["pop"].where(d["pop"] > 0)
    tot_c = g["cnt"].transform("sum")                       # soma sem os ausentes
    tot_p = pop_ok[tem_reg].groupby(d.loc[tem_reg, "reg"]).transform("sum")
    resto_c = tot_c - d.loc[tem_reg, "cnt"].fillna(0.0)     # o próprio ausente não entra na soma
    resto_p = tot_p - pop_ok[tem_reg].fillna(0.0)
    # NaN se a região tem só o município, se falta média ou população de algum outro (o próprio ausente já é NaN).
    proprio_falta = d.loc[tem_reg, "cnt"].isna().astype(int) + (~(d.loc[tem_reg, "pop"] > 0)).astype(int)
    ok = (n > 1) & ((falta - proprio_falta) == 0) & (resto_p > 0)
    val = (resto_c / resto_p * ESCALA_HAB).where(ok)
    out = pd.Series(np.nan, index=d.index)
    out.loc[val.index] = val
    so_um = int(((n == 1)).sum())
    info = {"municipios_sem_regiao": int((~tem_reg).sum()), "municipios_em_regiao_de_um_so": so_um,
            "municipios_com_resto_ausente": int(out.isna().sum())}
    return out, info


def construir_covariaveis() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Por município do a08: L e M; por município × curso (1 a 16): especialistas do curso no município e no resto."""
    rv = E7.ler_running_variable()
    pop = E7.ler_populacao()
    base = rv.merge(pop, on="co_ibge", how="left", validate="one_to_one").set_index("co_ibge").sort_index()
    universo = base.index
    ref, info_ref = ler_referencia_ibge()
    por_uf = ref.set_index("cd_uf")
    cov = pd.DataFrame(index=universo)
    cov["cd_uf"] = universo.str[:2]
    if not cov["cd_uf"].isin(por_uf.index).all():
        raise FalhaValidacao("município do a08 com UF fora da referência do IBGE")
    cov["regiao"] = cov["cd_uf"].map(por_uf["nome_regiao"])
    cov["capital"] = universo.isin(set(ref["capital_co_ibge_6d"])).astype(float)
    p22 = base["populacao_2022"].astype(float)
    cov["populacao_2022"] = p22
    cov["log_pop"] = np.where(p22 > 0, np.log(p22.where(p22 > 0)), np.nan)
    # Região de saúde: CIR oficial do TabNet/DATASUS (função do script 19; SHA-256 conferido, sem rede).
    man_cir = T19.adquirir_cir(False)
    cir, info_cir = T19.ler_cir()
    cir["co_ibge"] = K1M._ibge6(cir["co_ibge"])
    if cir["co_ibge"].duplicated().any():
        raise FalhaValidacao("CIR com município duplicado")
    reg = cir.set_index("co_ibge")["co_cir"].astype(str).reindex(universo)
    if (reg.dropna().str[:2] != pd.Series(reg.dropna().index.str[:2], index=reg.dropna().index)).any():
        raise FalhaValidacao("CIR com código de UF diferente do município")
    cov["regiao_saude"] = reg
    # Painel a09: só o pré, só n_vinculos.
    pontes = ponte_cursos()
    grupos = list(GRUPOS_MED) + ["todos_medicos"] + [f"cbo_{c}" for c in sorted({c for v in pontes.values()
                                                                                 for c in v})]
    p = pd.read_parquet(PAINEL, columns=["co_ibge", "competencia", "grupo", "n_vinculos", "natureza_dos_dados"],
                        filters=[("grupo", "in", grupos), ("competencia", "in", list(COMP_PRE))])
    p["co_ibge"] = p["co_ibge"].astype(str)
    p["competencia"] = p["competencia"].astype(str)
    if (p["competencia"] >= LIMITE_CNES).any():
        raise FalhaValidacao("a09 com competência >= 202609")
    if sorted(p["competencia"].unique()) != list(COMP_PRE):
        raise FalhaValidacao("a09 sem todas as competências do pré (202406–202506)")
    if set(p["natureza_dos_dados"].astype(str).str.upper()) != {"EMPIRICO"}:
        raise FalhaValidacao("a09 sem natureza EMPIRICO")
    if p.duplicated(["co_ibge", "competencia", "grupo"]).any():
        raise FalhaValidacao("a09 com chave repetida")
    medias, larg = {}, {}
    for g in grupos:
        medias[g], larg[g] = _media_pre(p, g, universo)
    soma_med = sum(larg[g] for g in GRUPOS_MED)
    excesso = (soma_med - larg["todos_medicos"]).to_numpy(float)
    if np.nanmax(excesso) > 1e-9:
        raise FalhaValidacao("médicos 2251/2252/2253 maiores que todos_medicos do a09 em algum município × mês")
    cnt_med = sum(medias[g] for g in GRUPOS_MED)          # NaN se algum grupo ausente
    cnt_esp = medias["alvo_pmme"]
    taxa = lambda c: (c / p22 * ESCALA_HAB).where(p22 > 0)   # noqa: E731
    cov["med"] = taxa(cnt_med)
    cov["esp"] = taxa(cnt_esp)
    cov["esp_resto"], info_resto = _resto_regiao(cnt_esp, p22, reg)
    cov["cnt_med_pre"] = cnt_med
    cov["cnt_esp_pre"] = cnt_esp
    # Por curso.
    linhas = []
    info_curso = {}
    for k, cbos in pontes.items():
        cnt = sum(medias[f"cbo_{c}"] for c in cbos)
        resto, inf = _resto_regiao(cnt, p22, reg)
        linhas.append(pd.DataFrame({"co_ibge": universo, "cod_curso": k, "esp_curso": taxa(cnt).to_numpy(),
                                    "esp_curso_resto": resto.to_numpy()}))
        info_curso[str(k)] = {"cbos": cbos, **inf}
    curso = pd.concat(linhas, ignore_index=True)
    info = {
        "referencia_ibge": info_ref,
        "populacao": {"arquivo": rotulo(POP22), "sha256": sha256(POP22),
                      "municipios_sem_populacao_2022": int((~(p22 > 0)).sum())},
        "regiao_saude": {"fonte": "tabela oficial municipio -> CIR do TabNet/DATASUS (funcao ler_cir do script 19)",
                         "arquivo": rotulo(CIR_BRUTO), "sha256": sha256(CIR_BRUTO), "manifesto": rotulo(CIR_MANIF),
                         "sha256_manifesto": man_cir.get("sha256"), "regioes": int(reg.dropna().nunique()),
                         "municipios_a08_sem_cir": int(reg.isna().sum()), "leitura_cir": info_cir, **info_resto},
        "painel_a09": {"arquivo": rotulo(PAINEL), "sha256": sha256(PAINEL), "manifesto": rotulo(MANIF_A09),
                       "competencias": list(COMP_PRE), "grupos": grupos, "medida": "n_vinculos (media mensal)",
                       "medicos": "alvo_pmme + generalistas + especialistas_nao_alvo (= CBO 2251, 2252, 2253)",
                       "municipios_med_ausente": int(cov["med"].isna().sum()),
                       "municipios_esp_ausente": int(cov["esp"].isna().sum())},
        "ponte_cursos": {str(k): v for k, v in pontes.items()},
        "por_curso": info_curso,
        "universo_a08": int(len(universo)),
    }
    return cov, curso, info


# ---------------------------------------------------------------------------
# 2. Bases da H1 (48b) com as covariáveis
# ---------------------------------------------------------------------------

def bases_h1(cov: pd.DataFrame, curso: pd.DataFrame) -> dict:
    todos = T40.carregar()
    dados = todos["13fev"]
    colc = ["capital", "regiao", "cd_uf", "log_pop", "med", "esp", "esp_resto"]
    CK, MK, PAR = {}, {}, []
    for k in CICLOS:
        c0 = dados["CK"][k].rename(columns={"regiao": "regiao_quadro"})      # a do IBGE vem da referência
        c = c0.merge(cov[colc], left_on="co_ibge", right_index=True, how="left", validate="many_to_one")
        c = c.merge(curso, on=["co_ibge", "cod_curso"], how="left", validate="many_to_one")
        if len(c) != len(dados["CK"][k]) or c["capital"].isna().any():
            raise FalhaValidacao(f"V{k}: célula sem covariável de localização")
        # Na célula, M usa as CBO do curso.
        c["esp_mun"], c["esp_resto_mun"] = c["esp"], c["esp_resto"]
        c["esp"], c["esp_resto"] = c["esp_curso"], c["esp_curso_resto"]
        CK[k] = c
        m0 = dados["MK"][k].rename(columns={c_: f"{c_}_quadro" for c_ in colc if c_ in dados["MK"][k].columns})
        m = m0.merge(cov[colc], left_on="co_ibge", right_index=True, how="left", validate="one_to_one")
        if m["capital"].isna().any():
            raise FalhaValidacao(f"V{k}: município sem covariável de localização")
        imed = c[c["tipo_celula"].isin(["so_imed", "mista"])]
        fr = imed.groupby("co_ibge")["preenchida"].agg(["mean", "size"])
        m["frac_preenchida"] = m["co_ibge"].map(fr["mean"])
        m["n_cel_imed_conf"] = m["co_ibge"].map(fr["size"]).fillna(0)
        if (np.abs(m["n_cel_imed_conf"] - m["n_cel_imed"]) > 1e-9).any():
            raise FalhaValidacao(f"V{k}: células com vaga imediata do município não batem")
        m["aloc_por_vi"] = np.where(m["vi_imed"] > 0, m["aloc_imed"] / m["vi_imed"].where(m["vi_imed"] > 0), np.nan)
        MK[k] = m
        u = m[m["n_cel_imed"] > 0].copy()
        u["ciclo"] = k
        PAR.append(u)
    par = pd.concat(PAR, ignore_index=True)
    par["id"] = par["co_ibge"].astype(str) + "|c" + par["ciclo"].astype(str)
    return {"dados": dados, "CK": CK, "MK": MK, "par": par}


def base_v(cov: pd.DataFrame) -> tuple[pd.DataFrame, dict, pd.DataFrame]:
    """V do protocolo 64 = a amostra do doc 57k (script 37: U com célula em algum ciclo, menos os tratados fora da
    amostra do D2), conferida contra `OL_resumo.json`."""
    base, _ = K1M.ler_universo()
    am_total, info_am = T37.ler_amostra(base)
    ch_total, _ = D2M.ler_chegadas(am_total)
    am_d2, _ = D2M.ler_amostra(base)
    excl = sorted(set(ch_total.index[ch_total["chegada"].notna()]) - set(am_d2))
    amostra = am_total.difference(pd.Index(excl))
    ol = json.loads(OL_RES.read_text(encoding="utf-8"))["amostra"]
    if len(amostra) != int(ol["n_municipios"]) or len(excl) != int(ol["excluidos_tratados_fora_d2"]):
        raise FalhaValidacao(f"V ({len(amostra)}) difere da amostra do doc 57k ({ol['n_municipios']})")
    v = cov.loc[amostra].copy()
    v["s_mil"] = base.loc[amostra, "s_mil"].astype(float)
    v["populacao_2022"] = base.loc[amostra, "populacao_2022"].astype(float)
    v = v.rename_axis("co_ibge").reset_index()
    v["id"] = v["co_ibge"]
    return v, {"n_municipios": int(len(amostra)), "excluidos_tratados_fora_d2": excl,
               "conferido_contra": rotulo(OL_RES)}, base


# ---------------------------------------------------------------------------
# 3. Estimadores RDD com covariáveis (rdd_lib; um coeficiente por covariável)
# ---------------------------------------------------------------------------

def colunas_brutas(vars_: tuple) -> list[str]:
    return ["cd_uf" if v == "uf" else v for v in vars_]


def matriz_z(d: pd.DataFrame, vars_: tuple) -> tuple[np.ndarray | None, list[str]]:
    cols, nomes = [], []
    for v in vars_:
        if v == "regiao":
            for r in REGIOES:
                if r != REGIAO_REF:
                    cols.append((d["regiao"] == r).to_numpy(float))
                    nomes.append(f"regiao[{r}]")
        elif v == "uf":
            for u in UFS[1:]:
                cols.append((d["cd_uf"] == u).to_numpy(float))
                nomes.append(f"uf[{u}]")
        else:
            cols.append(d[v].to_numpy(float))
            nomes.append(v)
    if not cols:
        return None, []
    return np.column_stack(cols), nomes


UFS: list[str] = []          # preenchido em `executar` a partir da referência do IBGE (27 UFs, ordem do código)


def rd_h1(a, oid: str, vars_: tuple, h: int = H) -> dict:
    """HI-1: célula, EF de curso × ciclo; HI-2: município × ciclo, controle das vagas imediatas por ciclo (S-a do
    23). Covariáveis lineares, um coeficiente comum aos dois lados e aos ciclos; CR1 por município."""
    y = a.col(OUT_H1[oid]["y"])
    Z, nomes = matriz_z(a.d, vars_)
    if oid == "HI-1":
        r = L.rd_empilhado(a.s, y, a.c, grupo=a.g, h_mil=h, cluster=a.cl, ids_unidade=a.cl,
                           efeitos_fixos=a.d["fe_curso_ciclo"].to_numpy(), Z=Z, nomes_z=nomes or None, detalhes=True)
    else:
        Zc, nc, _, _ = T23.colunas_controle(a, y, a.col("vi_imed"), h)
        ZZ = Zc if Z is None else np.column_stack([Zc, Z])
        r = L.rd_empilhado(a.s, y, a.c, grupo=a.g, h_mil=h, cluster=a.cl, ids_unidade=a.cl, Z=ZZ,
                           nomes_z=nc + nomes, detalhes=True)
    r["media_abaixo"] = float("nan")
    det = r.pop("_detalhes", None)
    if det is not None:
        ab = det["usa"] & (det["x_mil"] <= 0)
        r["media_abaixo"] = float(np.mean(y[ab])) if ab.any() else float("nan")
        r["coef_covariaveis"] = {n: float(det["fit"]["coef"][n]) for n in nomes if n in det["fit"]["coef"]}
    return r


def rd_v(d: pd.DataFrame, y: np.ndarray, corte: int, vars_: tuple, h: int = H) -> dict:
    """Um município por linha (V do protocolo 64): local linear, HC1, covariáveis lineares (rd_local_linear)."""
    Z, nomes = matriz_z(d, vars_)
    r = L.rd_local_linear(d["s_mil"].to_numpy(float), y, corte, h, Z=Z, nomes_z=nomes or None, detalhes=True)
    det = r.pop("_detalhes", None)
    r["media_abaixo"] = float("nan")
    if det is not None:
        ab = det["usa"] & (det["x_mil"] <= 0)
        r["media_abaixo"] = float(np.mean(np.asarray(y, float)[ab])) if ab.any() else float("nan")
    return r


def mascara_completa(d: pd.DataFrame, vars_: tuple) -> np.ndarray:
    cols = colunas_brutas(vars_)
    if not cols:
        return np.ones(len(d), dtype=bool)
    m = np.ones(len(d), dtype=bool)
    for c in cols:
        v = d[c]
        m &= (np.isfinite(v.to_numpy(float)) if pd.api.types.is_numeric_dtype(v)
              else (v.notna() & (v.astype(str).str.strip() != "")).to_numpy())
    return m


def _janela_kernel(s: np.ndarray, c, h: int) -> np.ndarray:
    return L.pesos_kernel(L.normalizar_s_mil(s) - c, h) > 0


# ---------------------------------------------------------------------------
# 4. Portão: HI-1 e HI-2 do 48b
# ---------------------------------------------------------------------------

def portao_hi(b: dict) -> dict:
    hi = pd.read_csv(HI_EST, dtype={"corte": str, "ciclo": str}, low_memory=False)
    imed = T40.filtro_tipos("so_imed", "mista")
    mun_imed = T40.filtro_coluna_positiva("n_cel_imed")
    out = {"referencia": rotulo(HI_EST), "sha256_referencia": sha256(HI_EST), "tolerancia": TOL_PORTAO,
           "linhas": []}
    for c in CORTES:
        ref = {oid: T40._uma(hi, linha=oid, outcome=oid, variante="principal", corte=ROT_CORTE[c])
               for oid in ("HI-1", "HI-2")}
        a1 = T40.amostra(b["CK"], CICLOS, c, imed)
        a2 = T40.amostra(b["MK"], CICLOS, c, mun_imed)
        pares = {"HI-1": (a1, T40.est_celula(a1, a1.col("preenchida"))),
                 "HI-2": (a2, T40.est_municipio(a2, a2.col("aloc_imed"), v=a2.col("vi_imed")))}
        for oid, (a, r40) in pares.items():
            r44 = rd_h1(a, oid, ())
            difs = {}
            for k in ("tau", "ep", "p_valor", "ic95_inf", "ic95_sup"):
                difs[f"{k}_40_vs_csv"] = abs(float(r40[k]) - float(ref[oid][k]))
                difs[f"{k}_44_vs_csv"] = abs(float(r44[k]) - float(ref[oid][k]))
            cont = {k: (int(r44[k]), int(ref[oid][k])) for k in ("n_abaixo", "n_acima", "n_obs")}
            ok = all(v <= TOL_PORTAO for v in difs.values()) and all(x == y for x, y in cont.values())
            out["linhas"].append({"linha": oid, "corte": ROT_CORTE[c], "tau_csv": float(ref[oid]["tau"]),
                                  "tau_44": float(r44["tau"]), "max_abs_dif": max(difs.values()),
                                  "contagens": {k: list(v) for k, v in cont.items()}, "reproduz": bool(ok)})
            if not ok:
                raise FalhaValidacao(f"portão: {oid} em {TXT_CORTE[c]} não reproduz o 48b: {difs} {cont}")
    out["max_abs_dif"] = max(x["max_abs_dif"] for x in out["linhas"])
    out["aprovado"] = True
    return out


# ---------------------------------------------------------------------------
# 5. Linhas
# ---------------------------------------------------------------------------

def nova_linha(bloco: str, papel: str, parte: str, outcome: str, desc: str, unidade_analise: str, populacao: str,
               corte: int, janela: int, conjunto: str, vars_: tuple, metodo: str, estimador: str, unidade: str,
               nota: str = "") -> dict:
    ln = {c: np.nan for c in COLUNAS}
    ln.update({"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "bloco": bloco, "papel": papel,
               "parte": parte, "outcome": outcome, "descricao_outcome": desc, "unidade_analise": unidade_analise,
               "populacao": populacao, "corte": ROT_CORTE[corte], "janela": janela / 1000.0, "conjunto": conjunto,
               "variaveis": ";".join(vars_), "metodo": metodo, "estimador": estimador, "status": "EXECUTADO",
               "entra_holm": False, "entra_bky": False, "multiplicidade_provisoria": False,
               "covariaveis_descartadas": "", "comparacao_limpa": "", "unidade": unidade, "nota": nota})
    ln["id_linha"] = "|".join([bloco, outcome, ROT_CORTE[corte], f"w={janela / 1000:.3f}", conjunto, metodo])
    return ln


def preencher_rd(ln: dict, r: dict, r0: dict | None) -> dict:
    for k in ("tau", "ep", "ic95_inf", "ic95_sup", "p_valor", "n_abaixo", "n_acima", "n_obs", "n_clusters",
              "media_abaixo"):
        if r.get(k) is not None:
            ln[k] = r[k]
    ln["covariaveis_descartadas"] = r.get("covariaveis_descartadas", "") or ""
    ln["nota"] = _juntar(ln["nota"], r.get("nota", ""))
    if r0 is not None:
        ln["tau_sem_controle"], ln["ic_sem_controle_inf"] = r0["tau"], r0["ic95_inf"]
        ln["ic_sem_controle_sup"], ln["p_sem_controle"] = r0["ic95_sup"], r0["p_valor"]
        if np.isfinite(_f(r["tau"])) and np.isfinite(_f(r0["tau"])):
            ln["variacao_abs"] = float(r["tau"]) - float(r0["tau"])
            ln["variacao_pct"] = 100.0 * ln["variacao_abs"] / abs(float(r0["tau"])) if r0["tau"] != 0 else np.nan
    if not np.isfinite(_f(ln["tau"])):
        ln["status"] = "SEM_ESTIMATIVA"
    return ln


EST_RD = {"HI-1": "celula; local linear, kernel triangular, h = 0,050; intercepto e inclinacoes por ciclo x lado, "
                  "salto comum; EF de curso x ciclo; covariaveis lineares com um coeficiente comum aos dois lados e "
                  "aos ciclos; CR1 por municipio (rdd_lib.rd_empilhado)",
          "HI-2": "municipio x ciclo; local linear, kernel triangular, h = 0,050; intercepto e inclinacoes por ciclo "
                  "x lado, salto comum; controle = vagas imediatas com coeficiente por ciclo (S-a); covariaveis "
                  "lineares com um coeficiente comum; CR1 por municipio (rdd_lib.rd_empilhado)",
          "V": "municipio (V do protocolo 64); local linear, kernel triangular, h = 0,050; DeltaY; covariaveis "
               "lineares com o mesmo coeficiente dos dois lados; HC1 (rdd_lib.rd_local_linear)"}


def linhas_rdd_h1(b: dict) -> tuple[list[dict], dict]:
    imed = T40.filtro_tipos("so_imed", "mista")
    mun_imed = T40.filtro_coluna_positiva("n_cel_imed")
    linhas, amostras = [], {}
    specs = [("CL-1", "secundaria", "L+M", CONJUNTOS["L+M"]),
             ("CL-2", "secundaria", "L", CONJUNTOS["L"]), ("CL-2", "secundaria", "M", CONJUNTOS["M"]),
             ("CL-2", "secundaria", "LUF+M", CONJUNTOS["LUF+M"])]
    specs += [("CL-3", "secundaria", v, (v,)) for v in VARIAVEIS]
    for c in CORTES:
        base = {"HI-1": T40.amostra(b["CK"], CICLOS, c, imed), "HI-2": T40.amostra(b["MK"], CICLOS, c, mun_imed)}
        for oid, a in base.items():
            jan = _janela_kernel(a.s, a.c, H)
            ab = (L.normalizar_s_mil(a.s) - a.c) <= 0
            # CL-4: sem controle na amostra de L+M.
            m_lm = mascara_completa(a.d, CONJUNTOS["L+M"])
            al = a.subconjunto(m_lm)
            r4 = rd_h1(al, oid, ())
            ln = nova_linha("CL-4", "referencia", "H1", oid, OUT_H1[oid]["desc"], OUT_H1[oid]["unidade_analise"],
                            "V1+V2+V3 (48b)", c, H, "sem", (), "RDD", EST_RD[oid], OUT_H1[oid]["unidade"],
                            nota="sem controle, na amostra comum das linhas com L+M")
            ln = preencher_rd(ln, r4, None)
            _saidas(ln, a, jan, ab, m_lm, oid)
            linhas.append(ln)
            amostras[(oid, c)] = {"linhas_na_janela": int(jan.sum()),
                                  "saiu_ausencia_L+M": int((jan & ~m_lm).sum()),
                                  "municipios_que_sairam_L+M": sorted(set(a.d.loc[jan & ~m_lm, "co_ibge"]))}
            for bloco, papel, conj, vars_ in specs:
                m = mascara_completa(a.d, vars_)
                asub = a.subconjunto(m)
                r = rd_h1(asub, oid, vars_)
                r0 = r4 if conj == "L+M" else rd_h1(asub, oid, ())
                ln = nova_linha(bloco, papel, "H1", oid, OUT_H1[oid]["desc"], OUT_H1[oid]["unidade_analise"],
                                "V1+V2+V3 (48b)", c, H, conj, vars_, "RDD", EST_RD[oid], OUT_H1[oid]["unidade"])
                ln = preencher_rd(ln, r, r0)
                _saidas(ln, a, jan, ab, m, oid)
                ln["entra_bky"] = ln["status"] == "EXECUTADO"
                linhas.append(ln)
    return linhas, amostras


def _saidas(ln: dict, a, jan: np.ndarray, ab: np.ndarray, m: np.ndarray, oid: str) -> None:
    """Quem saiu por covariável ausente, na janela: linhas (células ou município × ciclo) por lado."""
    ln["saiu_ausencia_abaixo"] = int((jan & ~m & ab).sum())
    ln["saiu_ausencia_acima"] = int((jan & ~m & ~ab).sum())
    if ln["saiu_ausencia_abaixo"] or ln["saiu_ausencia_acima"]:
        un = "celulas" if oid == "HI-1" else "municipio x ciclo"
        ln["nota"] = _juntar(ln["nota"], f"saiu por covariavel ausente ({un} na janela): "
                                         f"{ln['saiu_ausencia_abaixo']} abaixo / {ln['saiu_ausencia_acima']} acima")


# ---------------------------------------------------------------------------
# 6. CL-0: balanço no corte
# ---------------------------------------------------------------------------

VARS_BAL = ("capital",) + tuple(f"regiao_{r}" for r in REGIOES) + CONTINUAS


def _col_bal(d: pd.DataFrame, v: str) -> np.ndarray:
    if v.startswith("regiao_"):
        return (d["regiao"] == v[len("regiao_"):]).to_numpy(float)
    return d[v].to_numpy(float)


def linhas_cl0(b: dict, v: pd.DataFrame | None) -> list[dict]:
    imed = T40.filtro_tipos("so_imed", "mista")
    mun_imed = T40.filtro_coluna_positiva("n_cel_imed")
    out = []
    for c in CORTES:
        alvos = [("H1 (municipio x ciclo, amostra da HI-2)", "municipio x ciclo",
                  T40.amostra(b["MK"], CICLOS, c, mun_imed), VARS_BAL, "empilhado"),
                 ("H1 (celula, amostra da HI-1)", "celula", T40.amostra(b["CK"], CICLOS, c, imed),
                  ("esp", "esp_resto"), "empilhado")]
        if v is not None:
            alvos.append(("V (protocolo 64, um municipio por linha)", "municipio", v, VARS_BAL, "V"))
        for pop, un, a, vars_b, tipo in alvos:
            for var in vars_b:
                if tipo == "empilhado":
                    y = _col_bal(a.d, var)
                    r = T23.ajustar(a, y, H) if un != "celula" else L.rd_empilhado(
                        a.s, y, a.c, grupo=a.g, h_mil=H, cluster=a.cl, ids_unidade=a.cl)
                    s, cc = a.s, a.c
                else:
                    y = _col_bal(a, var)
                    r = L.rd_local_linear(a["s_mil"].to_numpy(float), y, c, H)
                    s, cc = a["s_mil"].to_numpy(float), np.full(len(a), c, float)
                r.pop("_detalhes", None)
                jan = _janela_kernel(s, cc, H) & np.isfinite(y)
                dp = float(np.std(y[jan], ddof=1)) if jan.sum() > 1 else float("nan")
                nome = var if not (un == "celula") else f"{var}_curso"
                ln = {k: np.nan for k in COLUNAS_BAL}
                ln.update({"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "tipo": "salto_no_corte",
                           "bloco": "CL-0", "parte": "H1" if tipo == "empilhado" else "oferta_local",
                           "populacao": pop, "unidade_analise": un, "corte": ROT_CORTE[c], "janela": H / 1000,
                           "metodo": ("local linear, kernel triangular, h = 0,050, ciclos empilhados, CR1 por "
                                      "municipio" if tipo == "empilhado" else
                                      "local linear, kernel triangular, h = 0,050, HC1"),
                           "variavel": nome, "dp_janela": dp, "status": "EXECUTADO", "nota": r.get("nota", "") or ""})
                for k in ("tau", "ep", "ic95_inf", "ic95_sup", "p_valor", "n_abaixo", "n_acima", "n_obs"):
                    if r.get(k) is not None:
                        ln[k] = r[k]
                if np.isfinite(_f(ln["tau"])) and np.isfinite(dp) and dp > 0:
                    ln["salto_padronizado"] = float(ln["tau"]) / dp
                if not np.isfinite(_f(ln["tau"])):
                    ln["status"] = "SEM_ESTIMATIVA"
                out.append(ln)
    return out


# ---------------------------------------------------------------------------
# 7. Pareamento (Mahalanobis e escore de propensão) e inferência pareada
# ---------------------------------------------------------------------------

def guloso_global(cand: list[tuple[float, str, str]]) -> list[tuple[str, str, float]]:
    """1:1 sem reposição: o par de menor distância primeiro; empates pela ordem dos identificadores."""
    usados_a, usados_b, pares = set(), set(), []
    for dist, ia, ib in sorted(cand):
        if ia in usados_a or ib in usados_b:
            continue
        usados_a.add(ia)
        usados_b.add(ib)
        pares.append((ia, ib, dist))
    return pares


def _janela(df: pd.DataFrame, corte: int, w: int) -> pd.DataFrame:
    x = L.normalizar_s_mil(df["s_mil"].to_numpy(float)) - corte
    d = df[np.abs(x) <= w].copy()
    d["acima"] = (L.normalizar_s_mil(d["s_mil"].to_numpy(float)) - corte) > 0
    return d


def _completo(d: pd.DataFrame) -> np.ndarray:
    return mascara_completa(d, CONJUNTOS["L+M"])


def parear_mahalanobis(d: pd.DataFrame, por_ciclo: bool) -> tuple[list, dict]:
    """Exato em macrorregião e capital (e ciclo na H1); Mahalanobis em log(pop) e M; caliper 0,25 × DP das
    distâncias de todos os pares admissíveis; covariância da janela (os dois lados), por corte e ciclo."""
    cand, info = [], {"caliper": {}, "covariancia_singular": []}
    grupos = d.groupby("ciclo") if por_ciclo else [(None, d)]
    for k, g in grupos:
        X = g[list(CONTINUAS)].to_numpy(float)
        S = np.cov(X, rowvar=False)
        if np.linalg.matrix_rank(S) < S.shape[0]:
            info["covariancia_singular"].append(str(k))
        Si = np.linalg.pinv(S)
        est = g["regiao"].astype(str) + "|" + g["capital"].astype(int).astype(str)
        A, B = g[g["acima"]], g[~g["acima"]]
        dists = []
        for e in sorted(set(est[g["acima"]]) & set(est[~g["acima"]])):
            a, bb = A[est[g["acima"]] == e], B[est[~g["acima"]] == e]
            Xa, Xb = a[list(CONTINUAS)].to_numpy(float), bb[list(CONTINUAS)].to_numpy(float)
            dif = Xa[:, None, :] - Xb[None, :, :]
            D = np.sqrt(np.maximum(np.einsum("ijk,kl,ijl->ij", dif, Si, dif), 0.0))
            for i, ia in enumerate(a["id"]):
                for j, ib in enumerate(bb["id"]):
                    dists.append((float(D[i, j]), ia, ib))
        if not dists:
            info["caliper"][str(k)] = None
            continue
        sd = float(np.std([x[0] for x in dists], ddof=1)) if len(dists) > 1 else 0.0
        cal = CALIPER_MAH * sd
        info["caliper"][str(k)] = cal
        cand += [x for x in dists if x[0] <= cal + 1e-12]
    return guloso_global(cand), info


def escore_propensao(d: pd.DataFrame) -> tuple[np.ndarray | None, dict]:
    """Logit de P(acima | L+M) na janela (statsmodels, Newton); colunas sem variação ou colineares saem antes."""
    import statsmodels.api as sm
    cols, nomes = [np.ones(len(d))], ["const"]
    Z, nz = matriz_z(d, CONJUNTOS["L+M"])
    tiradas = []
    for j, n in enumerate(nz):
        cand = np.column_stack(cols + [Z[:, j]])
        if np.std(Z[:, j]) == 0 or np.linalg.matrix_rank(cand) < cand.shape[1]:
            tiradas.append(n)
            continue
        cols.append(Z[:, j])
        nomes.append(n)
    X = np.column_stack(cols)
    y = d["acima"].to_numpy(float)
    # Diagnóstico de separação: categoria binária presente só de um lado da janela.
    so_um_lado = []
    for j, n in enumerate(nz):
        z = Z[:, j]
        if set(np.unique(z)) <= {0.0, 1.0} and z.sum() > 0:
            if y[z == 1].min() == y[z == 1].max():
                so_um_lado.append({"variavel": n, "unidades": int(z.sum()),
                                   "lado": "acima" if y[z == 1][0] == 1 else "abaixo"})
    info = {"colunas": nomes, "tiradas_sem_variacao_ou_colineares": tiradas, "n": int(len(d)),
            "n_acima": int(y.sum()), "n_abaixo": int((1 - y).sum()), "categorias_so_de_um_lado": so_um_lado}
    if y.sum() < 2 or (1 - y).sum() < 2:
        info["erro"] = "menos de 2 unidades em algum lado"
        return None, info
    with warnings.catch_warnings(record=True) as avisos:
        warnings.simplefilter("always")
        try:
            fit = sm.Logit(y, X).fit(method="newton", maxiter=200, disp=0)
        except Exception as erro:          # separação perfeita ou matriz singular
            info["erro"] = f"logit nao ajustou: {type(erro).__name__}: {erro}"
            return None, info
    info["convergiu"] = bool(fit.mle_retvals.get("converged", False))
    info["avisos"] = sorted({str(a.message)[:200] for a in avisos})
    info["coef"] = dict(zip(nomes, map(float, fit.params)))
    lp = X @ fit.params
    p = 1.0 / (1.0 + np.exp(-lp))
    info["separacao_quase_perfeita"] = bool(((p < 1e-6) | (p > 1 - 1e-6)).any())
    if not info["convergiu"]:
        info["erro"] = "logit nao convergiu"
        return None, info
    return lp, info


def parear_psm(d: pd.DataFrame, lp: np.ndarray, por_ciclo: bool) -> tuple[list, dict]:
    p = 1.0 / (1.0 + np.exp(-lp))
    acima = d["acima"].to_numpy(bool)
    lo = max(p[acima].min(), p[~acima].min())
    hi = min(p[acima].max(), p[~acima].max())
    sup = (p >= lo) & (p <= hi)
    cal = CALIPER_PS * float(np.std(lp, ddof=1))
    dd = d.assign(_lp=lp, _p=p, _sup=sup)
    cand = []
    grupos = dd.groupby("ciclo") if por_ciclo else [(None, dd)]
    for _, g in grupos:
        g = g[g["_sup"]]
        A, B = g[g["acima"]], g[~g["acima"]]
        if A.empty or B.empty:
            continue
        D = np.abs(A["_lp"].to_numpy()[:, None] - B["_lp"].to_numpy()[None, :])
        ia, ib = A["id"].to_numpy(), B["id"].to_numpy()
        for i, j in zip(*np.nonzero(D <= cal + 1e-12)):
            cand.append((float(D[i, j]), ia[i], ib[j]))
    fora = dd[~dd["_sup"]]
    info = {"suporte_comum": [float(lo), float(hi)], "caliper_logit": cal,
            "fora_suporte_acima": int((fora["acima"]).sum()), "fora_suporte_abaixo": int((~fora["acima"]).sum()),
            "fora_suporte": _quem(fora)}
    return guloso_global(cand), info


def _quem(d: pd.DataFrame) -> list[dict]:
    return [{"id": r["id"], "lado": "acima" if r["acima"] else "abaixo", "capital": bool(r["capital"] == 1),
             "regiao": r["regiao"]} for _, r in d.sort_values("id").iterrows()]


def inferencia_pareada(dif: np.ndarray) -> dict:
    """Média das diferenças; permutação de sinais (9.999, semente fixa) e IC por inversão; IC t pareado."""
    from scipy import stats
    dif = np.asarray(dif, float)
    n = dif.size
    out = {"n_pares": int(n), "tau": float(np.mean(dif)) if n else float("nan")}
    if n < 2:
        out["nota"] = "menos de 2 pares"
        return out
    rng = np.random.default_rng(SEMENTE)
    S = rng.choice(np.array([-1.0, 1.0]), size=(N_PERM, n))

    def pval(t0: float) -> float:
        e = dif - t0
        obs = abs(e.mean())
        perm = np.abs(S @ e) / n
        tol = 1e-10 * max(1.0, obs)            # empate numérico (todos os sinais iguais) conta como ">="
        return float((1 + np.sum(perm >= obs - tol)) / (N_PERM + 1))

    out["p_valor"] = pval(0.0)
    escala = float(np.max(np.abs(dif - dif.mean()))) + float(np.std(dif)) + 1e-9

    def limite(sinal: int) -> float:
        dentro = out["tau"]
        fora = out["tau"] + sinal * escala
        k = 0
        while pval(fora) > ALFA and k < 60:
            fora = out["tau"] + sinal * (abs(fora - out["tau"]) * 2)
            k += 1
        if pval(fora) > ALFA:          # com poucos pares o teste nunca rejeita: IC não limitado
            return sinal * math.inf
        for _ in range(80):
            meio = 0.5 * (dentro + fora)
            if pval(meio) > ALFA:
                dentro = meio
            else:
                fora = meio
            if abs(fora - dentro) <= 1e-10 * max(1.0, abs(out["tau"])):
                break
        return dentro

    out["ic95_inf"], out["ic95_sup"] = limite(-1), limite(+1)
    sd = float(np.std(dif, ddof=1))
    ep = sd / math.sqrt(n)
    tcrit = float(stats.t.ppf(0.975, n - 1))
    out["ep"] = ep
    out["ic_t_inf"], out["ic_t_sup"] = out["tau"] - tcrit * ep, out["tau"] + tcrit * ep
    out["p_t"] = float(2 * stats.t.sf(abs(out["tau"] / ep), n - 1)) if ep > 0 else float("nan")
    return out


def ipw(d: pd.DataFrame, lp: np.ndarray, y: np.ndarray, cluster: bool) -> dict:
    p = 1.0 / (1.0 + np.exp(-lp))
    ok = (p >= APARO_IPW[0]) & (p <= APARO_IPW[1]) & np.isfinite(y)
    t = d["acima"].to_numpy(float)
    w = np.where(t == 1, 1.0, p / (1 - p))
    X = np.column_stack([np.ones(int(ok.sum())), t[ok]])
    fit = L.mqp_sanduiche(X, y[ok], w[ok], nomes=["const", "T"],
                          cluster=d["co_ibge"].to_numpy()[ok] if cluster else None)
    res = {"aparados_acima": int(((~ok) & (t == 1)).sum()), "aparados_abaixo": int(((~ok) & (t == 0)).sum()),
           "n_acima": int((ok & (t == 1)).sum()), "n_abaixo": int((ok & (t == 0)).sum()), "n_obs": int(ok.sum())}
    if "erro" in fit:
        res["nota"] = fit["erro"]
        return res
    i = fit["nomes"].index("T")
    tau, ep = float(fit["beta"][i]), float(math.sqrt(max(fit["V"][i, i], 0.0)))
    res.update({"tau": tau, "ep": ep, "ic95_inf": tau - 1.959963984540054 * ep,
                "ic95_sup": tau + 1.959963984540054 * ep, "p_valor": L.p_normal(tau / ep) if ep > 0 else np.nan,
                "n_clusters": fit["G"]})
    return res


def balanco(d: pd.DataFrame, pares_ids: tuple[set, set] | None) -> list[dict]:
    """Diferença padronizada antes e depois; denominador = DP combinado antes do pareamento."""
    out = []
    A0, B0 = d[d["acima"]], d[~d["acima"]]
    if pares_ids is not None:
        A1, B1 = d[d["id"].isin(pares_ids[0])], d[d["id"].isin(pares_ids[1])]
    for v in VARS_BAL:
        a0, b0 = _col_bal(A0, v), _col_bal(B0, v)
        den = math.sqrt((np.var(a0, ddof=1) + np.var(b0, ddof=1)) / 2) if len(a0) > 1 and len(b0) > 1 else np.nan
        x = {"variavel": v, "media_acima_antes": float(a0.mean()) if len(a0) else np.nan,
             "media_abaixo_antes": float(b0.mean()) if len(b0) else np.nan, "n_acima_antes": int(len(a0)),
             "n_abaixo_antes": int(len(b0))}
        x["dp_antes"] = _dp(x["media_acima_antes"] - x["media_abaixo_antes"], den)
        if pares_ids is not None:
            a1, b1 = _col_bal(A1, v), _col_bal(B1, v)
            x.update({"media_acima_depois": float(a1.mean()) if len(a1) else np.nan,
                      "media_abaixo_depois": float(b1.mean()) if len(b1) else np.nan,
                      "n_acima_depois": int(len(a1)), "n_abaixo_depois": int(len(b1))})
            x["dp_depois"] = _dp(x["media_acima_depois"] - x["media_abaixo_depois"], den)
        out.append(x)
    return out


def _dp(dif: float, den: float) -> float:
    if not np.isfinite(dif):
        return float("nan")
    if not np.isfinite(den) or den == 0:
        return 0.0 if dif == 0 else float("nan")
    return float(dif / den)


def pareamentos(unid: pd.DataFrame, parte: str, outcomes: dict, corte: int, janela: int, por_ciclo: bool,
                metodos: tuple, blocos: dict, papel: dict) -> tuple[list[dict], list[dict], dict]:
    """Pareamento numa janela de um corte: devolve linhas de estimativa, de balanço e o registro (quem saiu)."""
    d = _janela(unid, corte, janela)
    comp = _completo(d)
    reg = {"corte": ROT_CORTE[corte], "janela": janela / 1000, "parte": parte,
           "na_janela_acima": int(d["acima"].sum()), "na_janela_abaixo": int((~d["acima"]).sum()),
           "sem_covariavel_acima": int((~comp & d["acima"].to_numpy()).sum()),
           "sem_covariavel_abaixo": int((~comp & ~d["acima"].to_numpy()).sum()),
           "sem_covariavel": _quem(d[~comp])}
    d = d[comp].copy()
    reg["lado_com_menos_unidades"] = "acima" if d["acima"].sum() < (~d["acima"]).sum() else "abaixo"
    linhas, bal = [], []
    lp, info_ps = (None, {})
    if "PSM" in metodos or "IPW" in metodos:
        lp, info_ps = escore_propensao(d)
        reg["escore"] = info_ps
        if lp is not None:
            reg["escore_por_unidade"] = {"id": d["id"].tolist(), "acima": d["acima"].astype(int).tolist(),
                                         "escore": (1 / (1 + np.exp(-lp))).round(10).tolist()}
    for met in metodos:
        info, pares = {}, None
        if met == "MAH":
            pares, info = parear_mahalanobis(d, por_ciclo)
        elif met == "PSM" and lp is not None:
            pares, info = parear_psm(d, lp, por_ciclo)
        reg[met] = info
        ids_a = {p[0] for p in pares} if pares is not None else set()
        ids_b = {p[1] for p in pares} if pares is not None else set()
        if pares is not None:
            reg[met]["sem_par"] = _quem(d[d["acima"] & ~d["id"].isin(ids_a) | (~d["acima"] & ~d["id"].isin(ids_b))])
            reg[met]["pares"] = [{"acima": a, "abaixo": b_, "distancia": round(dist, 10)} for a, b_, dist in pares]
            bb = balanco(d, (ids_a, ids_b))
            mx_a = max(abs(x["dp_antes"]) for x in bb if np.isfinite(x["dp_antes"]))
            dps = [abs(x["dp_depois"]) for x in bb if np.isfinite(_f(x.get("dp_depois")))]
            mx_d = max(dps) if dps and len(pares) else float("nan")
            for x in bb:
                bal.append({**{k: np.nan for k in COLUNAS_BAL}, **x, "natureza_dos_dados": NATUREZA,
                            "estatuto": ESTATUTO, "tipo": "dif_padronizada", "bloco": blocos[met], "parte": parte,
                            "populacao": "H1 municipio x ciclo" if parte == "H1" else "V (protocolo 64)",
                            "unidade_analise": "municipio x ciclo" if parte == "H1" else "municipio",
                            "corte": ROT_CORTE[corte], "janela": janela / 1000,
                            "metodo": {"MAH": "Mahalanobis", "PSM": "escore de propensao"}[met],
                            "status": "EXECUTADO", "nota": ""})
        for oid, spec in outcomes.items():
            ln = nova_linha(blocos[met], papel[met], parte, oid, spec["desc"],
                            "municipio x ciclo" if parte == "H1" else "municipio",
                            "H1 municipio x ciclo (48b)" if parte == "H1" else "V (protocolo 64)", corte, janela,
                            "L+M", CONJUNTOS["L+M"], {"MAH": "pareamento_mahalanobis", "PSM": "pareamento_psm",
                                                     "IPW": "ipw"}[met], EST_PAR[met], spec["unidade"])
            if met == "IPW":
                if lp is None:
                    ln["status"], ln["nota"] = "SEM_ESTIMATIVA", _juntar("escore nao estimado", info_ps.get("erro"))
                else:
                    r = ipw(d, lp, d[spec["col"]].to_numpy(float), cluster=(parte == "H1"))
                    for k in ("tau", "ep", "ic95_inf", "ic95_sup", "p_valor", "n_abaixo", "n_acima", "n_obs",
                              "n_clusters"):
                        if r.get(k) is not None:
                            ln[k] = r[k]
                    ln["nota"] = _juntar(f"aparados (escore fora de [0,05; 0,95]): {r['aparados_abaixo']} abaixo / "
                                         f"{r['aparados_acima']} acima", r.get("nota", ""))
            elif pares is None:
                ln["status"], ln["nota"] = "SEM_ESTIMATIVA", _juntar("escore nao estimado", info_ps.get("erro"))
            else:
                ya = d.set_index("id")[spec["col"]]
                dif = np.array([ya[a] - ya[b_] for a, b_, _ in pares], float)
                ok = np.isfinite(dif)
                r = inferencia_pareada(dif[ok])
                if r["n_pares"] < 2:
                    r = {"n_pares": r["n_pares"], "nota": "menos de 2 pares: sem estimativa (decisao 18)"}
                if not (np.isfinite(_f(r.get("ic95_inf"))) and np.isfinite(_f(r.get("ic95_sup")))) and \
                        r["n_pares"] >= 2:
                    r["nota"] = _juntar(r.get("nota", ""), "IC de permutacao nao limitado: com tao poucos pares o "
                                                           "teste de sinais nunca rejeita a 5%")
                for k in ("tau", "ep", "ic95_inf", "ic95_sup", "p_valor", "ic_t_inf", "ic_t_sup", "p_t",
                          "n_pares"):
                    if r.get(k) is not None:
                        ln[k] = r[k]
                ln["n_acima"] = ln["n_abaixo"] = ln["n_obs"] = int(ok.sum())
                ln["n_obs"] = 2 * int(ok.sum())
                ln["sem_par_acima"] = int((d["acima"] & ~d["id"].isin(ids_a)).sum())
                ln["sem_par_abaixo"] = int((~d["acima"] & ~d["id"].isin(ids_b)).sum())
                if met == "PSM":
                    ln["fora_suporte_acima"] = info["fora_suporte_acima"]
                    ln["fora_suporte_abaixo"] = info["fora_suporte_abaixo"]
                ln["max_abs_dp_antes"], ln["max_abs_dp_depois"] = mx_a, mx_d
                ln["comparacao_limpa"] = ("" if not pares else
                                          "SIM" if np.isfinite(mx_d) and mx_d <= LIMIAR_DP_LIMPA else "NAO")
                ln["media_abaixo"] = float(np.mean([ya[b_] for _, b_, _ in pares])) if pares else np.nan
                ln["nota"] = _juntar(r.get("nota", ""), f"{int((~ok).sum())} par(es) sem outcome" if (~ok).any()
                                     else "", "IC = inversao do teste de permutacao de sinais; p do Holm/BKY = "
                                              "permutacao")
            ln["saiu_ausencia_abaixo"] = reg["sem_covariavel_abaixo"]
            ln["saiu_ausencia_acima"] = reg["sem_covariavel_acima"]
            if not np.isfinite(_f(ln["tau"])):
                ln["status"] = "SEM_ESTIMATIVA"
            linhas.append(ln)
    return linhas, bal, reg


EST_PAR = {"MAH": "pareamento 1:1 sem reposicao, exato em macrorregiao e capital (e ciclo na H1), Mahalanobis em "
                  "log(pop) e M, caliper 0,25 DP das distancias; media das diferencas nos pares; IC por permutacao "
                  "de sinais (9.999, semente 20261026) e t pareado",
           "PSM": "escore de propensao: logit de P(acima | L+M) na janela; 1:1 no logit, sem reposicao, caliper 0,2 "
                  "DP do logit (exato no ciclo na H1), suporte comum min-max; media das diferencas nos pares; IC por "
                  "permutacao de sinais (9.999, semente 20261026) e t pareado",
           "IPW": "ponderacao pelo inverso do escore (ATT: 1 acima, e/(1-e) abaixo), escore aparado em [0,05; 0,95]; "
                  "MQP de y em 1 e no lado, EP sanduiche (CR1 por municipio na H1; HC1 em V), escore fixo"}


def linhas_pareamento_h1(b: dict) -> tuple[list[dict], list[dict], list[dict]]:
    linhas, bal, regs = [], [], []
    unid = b["par"]
    for c in CORTES:
        for janela, blocos, papel, metodos in (
                (JANELA_PAR, {"MAH": "CL-7", "PSM": "PS-1", "IPW": "PS-4"},
                 {"MAH": "secundaria", "PSM": "principal", "IPW": "sensibilidade"}, ("MAH", "PSM", "IPW")),
                (JANELA_SENS, {"MAH": "CL-9", "PSM": "PS-3"}, {"MAH": "sensibilidade", "PSM": "sensibilidade"},
                 ("MAH", "PSM"))):
            ln, bl, rg = pareamentos(unid, "H1", OUT_PAR_H1, c, janela, True, metodos, blocos, papel)
            for x in ln:
                if x["bloco"] == "PS-1":
                    x["entra_holm"] = True
                elif x["bloco"] == "CL-7" and x["status"] == "EXECUTADO":
                    x["entra_bky"] = True
            linhas += ln
            bal += bl
            regs.append(rg)
    return linhas, bal, regs


# ---------------------------------------------------------------------------
# 8. Oferta local (protocolo 64): pendente sem OC_*
# ---------------------------------------------------------------------------

def specs_oferta() -> list[dict]:
    """Todas as linhas de oferta local deste adendo (CL-5, CL-6, CL-8, CL-9, PS-2, PS-3, PS-4)."""
    out = []
    for c in CORTES:
        for oid in ("dB1", "dB2"):
            out.append({"bloco": "CL-5", "papel": "secundaria", "oid": oid, "corte": c, "janela": H,
                        "conjunto": "L+M", "metodo": "RDD", "bky": True})
        for oid in OUT_OC:
            for conj in ("L", "M"):
                out.append({"bloco": "CL-6", "papel": "secundaria", "oid": oid, "corte": c, "janela": H,
                            "conjunto": conj, "metodo": "RDD", "bky": True})
        for oid in OUT_OC:
            out.append({"bloco": "CL-8", "papel": "secundaria", "oid": oid, "corte": c, "janela": JANELA_PAR,
                        "conjunto": "L+M", "metodo": "pareamento_mahalanobis", "bky": True})
            out.append({"bloco": "CL-9", "papel": "sensibilidade", "oid": oid, "corte": c, "janela": JANELA_SENS,
                        "conjunto": "L+M", "metodo": "pareamento_mahalanobis", "bky": False})
        for oid in ("dB1", "dB2"):
            out.append({"bloco": "PS-2", "papel": "principal", "oid": oid, "corte": c, "janela": JANELA_PAR,
                        "conjunto": "L+M", "metodo": "pareamento_psm", "holm": True})
            out.append({"bloco": "PS-3", "papel": "sensibilidade", "oid": oid, "corte": c, "janela": JANELA_SENS,
                        "conjunto": "L+M", "metodo": "pareamento_psm"})
            out.append({"bloco": "PS-4", "papel": "sensibilidade", "oid": oid, "corte": c, "janela": JANELA_PAR,
                        "conjunto": "L+M", "metodo": "ipw"})
    return out


def _desc_oc(oid: str) -> str:
    return f"{OUT_OC[oid]['desc']}; {OUT_OC[oid]['oc']} do protocolo 64"


def linhas_pendentes() -> list[dict]:
    out = []
    for s in specs_oferta():
        est = EST_RD["V"] if s["metodo"] == "RDD" else EST_PAR[{"pareamento_mahalanobis": "MAH",
                                                                "pareamento_psm": "PSM", "ipw": "IPW"}[s["metodo"]]]
        ln = nova_linha(s["bloco"], s["papel"], "oferta_local", s["oid"], _desc_oc(s["oid"]), "municipio",
                        "V (protocolo 64)", s["corte"], s["janela"], s["conjunto"], CONJUNTOS[s["conjunto"]],
                        s["metodo"], est, UN_OC,
                        nota="PENDENTE_OC: as saidas OC_* do protocolo 64 nao existiam nesta execucao; rodar "
                             "--so-oferta-local depois delas")
        ln["status"] = STATUS_PEND
        ln["entra_holm"] = bool(s.get("holm", False))
        ln["entra_bky"] = bool(s.get("bky", False))
        out.append(ln)
    return out


def construir_delta_b(v: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """ΔB1–ΔB5 em V com as funções do script 43 (protocolo 64), importadas: `carregar` (U, V e níveis do a09 pelas
    funções do 37), `completar_b3` (horas dos ligados do a16) e `deltas(taxa(...))` (janelas do E7, exigir_completo).
    V do 43 tem de ser a mesma V deste script."""
    dados = T43.carregar()
    T43.completar_b3(dados)
    V = dados["V"]
    if set(V) != set(v["co_ibge"]):
        raise FalhaValidacao("V do script 43 difere da V deste script")
    out = pd.DataFrame({"co_ibge": list(V)})
    info = {"funcoes": "43_oferta_local_corte.carregar, completar_b3, deltas, taxa", "ausentes": {}}
    for k, spec in OUT_OC.items():
        d = T43.deltas(T43.taxa(dados["niveis"][spec["b"]].reindex(V), dados["pop"]))
        out[k] = out["co_ibge"].map(d["delta"])
        info["ausentes"][k] = int(out[k].isna().sum())
    info["b3"] = dados.get("info_b3")
    return out, info


def _linha_oc(oc: pd.DataFrame, id_oc: str, corte: int) -> pd.Series:
    """Linha do protocolo 64 (script 43): id_oc, população V, corte, especificação principal, h = 0,050."""
    sel = oc[(oc["id_oc"].astype(str) == id_oc) & (oc["populacao"].astype(str) == "V")
             & (oc["corte"].astype(str) == ROT_CORTE[corte]) & (oc["especificacao"].astype(str) == "principal")
             & (np.abs(pd.to_numeric(oc["h"], errors="coerce") - H / 1000) < 1e-12)]
    if len(sel) != 1:
        raise FalhaValidacao(f"OC_estimativas.csv: {len(sel)} linhas {id_oc} em V, {TXT_CORTE[corte]}, principal "
                             "(esperada 1)")
    return sel.iloc[0]


def portao_oc(v: pd.DataFrame) -> dict:
    oc = pd.read_csv(OC_EST, dtype={"corte": str, "id_oc": str, "populacao": str}, low_memory=False)
    ref = _linha_oc(oc, "OC-A1", 300)
    r = rd_v(v, v["dB1"].to_numpy(float), 300, ())
    difs = {k: abs(float(r[k]) - float(ref[k])) for k in ("tau", "ep", "p_valor", "ic95_inf", "ic95_sup")}
    cont = {k: (int(r[k]), int(ref[k])) for k in ("n_abaixo", "n_acima")}
    ok = all(x <= TOL_PORTAO for x in difs.values()) and all(a == b for a, b in cont.values())
    res = {"referencia": rotulo(OC_EST), "sha256_referencia": sha256(OC_EST), "linha": "OC-A1 em V, 0,300",
           "tau_oc": float(ref["tau"]), "tau_44": float(r["tau"]), "difs": difs,
           "contagens": {k: list(x) for k, x in cont.items()}, "tolerancia": TOL_PORTAO,
           "aprovado": bool(ok)}
    if not ok:
        raise FalhaValidacao(f"portão OC: OC-A1 em 0,300 não reproduz o protocolo 64: {difs}")
    return res


def linhas_oferta(v: pd.DataFrame) -> tuple[list[dict], list[dict], list[dict]]:
    """Todas as linhas de oferta local (depois do portão OC)."""
    linhas, bal, regs = [], [], []
    for c in CORTES:
        jan = _janela_kernel(v["s_mil"].to_numpy(float), c, H)
        ab = (L.normalizar_s_mil(v["s_mil"].to_numpy(float)) - c) <= 0
        for s in [x for x in specs_oferta() if x["metodo"] == "RDD" and x["corte"] == c]:
            vars_ = CONJUNTOS[s["conjunto"]]
            m = mascara_completa(v, vars_)
            d = v[m]
            y = d[s["oid"]].to_numpy(float)
            r = rd_v(d, y, c, vars_)
            r0 = rd_v(d, y, c, ())
            ln = nova_linha(s["bloco"], s["papel"], "oferta_local", s["oid"], _desc_oc(s["oid"]), "municipio",
                            "V (protocolo 64)", c, H, s["conjunto"], vars_, "RDD", EST_RD["V"], UN_OC)
            ln = preencher_rd(ln, r, r0)
            ln["saiu_ausencia_abaixo"] = int((jan & ~m & ab).sum())
            ln["saiu_ausencia_acima"] = int((jan & ~m & ~ab).sum())
            ln["entra_bky"] = ln["status"] == "EXECUTADO"
            linhas.append(ln)
        outs = {k: {"desc": _desc_oc(k), "unidade": UN_OC, "col": k} for k in OUT_OC}
        outs_ps = {k: outs[k] for k in ("dB1", "dB2")}
        # Mahalanobis: ΔB1–ΔB5 nas duas janelas.
        for janela, bloco, papel in ((JANELA_PAR, "CL-8", "secundaria"), (JANELA_SENS, "CL-9", "sensibilidade")):
            ln, bl, rg = pareamentos(v, "oferta_local", outs, c, janela, False, ("MAH",), {"MAH": bloco},
                                     {"MAH": papel})
            for x in ln:
                x["entra_bky"] = bloco == "CL-8" and x["status"] == "EXECUTADO"
            linhas += ln
            bal += bl
            regs.append(rg)
        # PSM e IPW: ΔB1 e ΔB2.
        ln, bl, rg = pareamentos(v, "oferta_local", outs_ps, c, JANELA_PAR, False, ("PSM", "IPW"),
                                 {"PSM": "PS-2", "IPW": "PS-4"}, {"PSM": "principal", "IPW": "sensibilidade"})
        for x in ln:
            x["entra_holm"] = x["bloco"] == "PS-2"
        linhas += ln
        bal += bl
        regs.append(rg)
        ln, bl, rg = pareamentos(v, "oferta_local", outs_ps, c, JANELA_SENS, False, ("PSM",), {"PSM": "PS-3"},
                                 {"PSM": "sensibilidade"})
        linhas += ln
        bal += bl
        regs.append(rg)
    return linhas, bal, regs


# ---------------------------------------------------------------------------
# 9. Multiplicidade e leituras (regras fixas, seção 0 do doc 57r)
# ---------------------------------------------------------------------------

def aplicar_multiplicidade(est: pd.DataFrame) -> pd.DataFrame:
    est = est.copy()
    pend = est["status"] == STATUS_PEND
    for fam, col_out, fn in (("entra_holm", "p_holm", L.holm), ("entra_bky", "q_bky", L.qvalores_bky)):
        m = est[fam].astype(bool) & (est["status"].isin(["EXECUTADO", STATUS_PEND]))
        p = est.loc[m, "p_valor"].astype(float).to_numpy()
        p = np.where(est.loc[m, "status"].to_numpy() == STATUS_PEND, 1.0, p)
        adj = fn(p)
        est.loc[m, col_out] = adj
        est.loc[m & pend, col_out] = np.nan
        prov = bool((m & pend).any())
        est.loc[m, "multiplicidade_provisoria"] = prov
    return est


def _contem_zero(r) -> bool:
    return _f(r["ic95_inf"]) <= 0.0 <= _f(r["ic95_sup"])


def _uma(df: pd.DataFrame, **kw) -> pd.Series:
    m = np.ones(len(df), dtype=bool)
    for k, v in kw.items():
        m &= (df[k].astype(str) == str(v)).to_numpy()
    sel = df[m]
    if len(sel) != 1:
        raise FalhaValidacao(f"linha não única ({len(sel)}): {kw}")
    return sel.iloc[0]


def _concorda(a, b) -> bool:
    za, zb = _contem_zero(a), _contem_zero(b)
    if za and zb:
        return True
    if not za and not zb:
        return np.sign(_f(a["tau"])) == np.sign(_f(b["tau"]))
    return False


def leituras(est: pd.DataFrame, bal: pd.DataFrame) -> dict:
    out = {"cl0": {}, "rdd_h1": {}, "psm": [], "concordancia": [], "oferta_local": {}}
    cl0 = bal[bal["tipo"] == "salto_no_corte"]
    for c in CORTES:
        sub = cl0[(cl0["corte"].astype(str) == ROT_CORTE[c]) & (cl0["status"] == "EXECUTADO")]
        out["cl0"][ROT_CORTE[c]] = {pop: sorted(g.loc[~g.apply(_contem_zero, axis=1), "variavel"].tolist())
                                    for pop, g in sub.groupby("populacao")}
    for c in CORTES:
        ct = ROT_CORTE[c]
        salto_cl0 = any(len(v) for v in out["cl0"][ct].values() if v is not None) and bool(
            [x for p, x in out["cl0"][ct].items() if p.startswith("H1") and x])
        for oid in ("HI-1", "HI-2"):
            r1 = _uma(est, bloco="CL-1", outcome=oid, corte=ct)
            r4 = _uma(est, bloco="CL-4", outcome=oid, corte=ct)
            parecido = (_f(r4["ic95_inf"]) <= _f(r1["tau"]) <= _f(r4["ic95_sup"])
                        and np.sign(_f(r1["tau"])) == np.sign(_f(r4["tau"])))
            ic_menor = (_f(r1["ic95_sup"]) - _f(r1["ic95_inf"])) < (_f(r4["ic95_sup"]) - _f(r4["ic95_inf"]))
            perto_zero = _contem_zero(r1) and abs(_f(r1["tau"])) <= 0.5 * abs(_f(r4["tau"]))
            if salto_cl0 and perto_zero and not _contem_zero(r4):
                cod = "ANDA_JUNTO_COM_LOCALIZACAO_OU_MEDICOS"
            elif not salto_cl0 and parecido and ic_menor:
                cod = "CONTROLES_MELHORAM_PRECISAO_SEM_MUDAR"
            else:
                cod = "RELATAR_COMO_ESTA"
            out["rdd_h1"][f"{oid} {ct}"] = {
                "codigo": cod, "cl0_com_salto_na_H1": bool(salto_cl0), "parecido_ao_sem_controle": bool(parecido),
                "ic_menor": bool(ic_menor), "perto_de_zero": bool(perto_zero),
                "cl4_ic_contem_zero": bool(_contem_zero(r4)), "cl1_ic_contem_zero": bool(_contem_zero(r1)),
                "cl1_q_bky_menor_que_005": bool(_f(r1["q_bky"]) < ALFA)}
    for _, r in est[est["bloco"].isin(["PS-1", "PS-2"])].iterrows():
        if r["status"] == STATUS_PEND:
            cod = STATUS_PEND
        elif r["status"] != "EXECUTADO":
            cod = "SEM_ESTIMATIVA"
        elif _f(r["p_holm"]) < ALFA:
            cod = "REJEITA_ZERO_DEPOIS_DO_HOLM"
        elif _contem_zero(r):
            cod = "IC_CONTEM_ZERO"
        else:
            cod = "IC_EXCLUI_ZERO_SEM_HOLM"
        out["psm"].append({"bloco": r["bloco"], "outcome": r["outcome"], "corte": r["corte"], "codigo": cod,
                           "comparacao_limpa": r["comparacao_limpa"],
                           "holm_provisorio": bool(r["multiplicidade_provisoria"])})
    for c in CORTES:
        ct = ROT_CORTE[c]
        for oid, spec in OUT_PAR_H1.items():
            for bl in ("PS-1", "CL-7"):
                r = _uma(est, bloco=bl, outcome=oid, corte=ct)
                if r["status"] != "EXECUTADO":
                    continue
                for ref in ("CL-4", "CL-1"):
                    rr = _uma(est, bloco=ref, outcome=spec["rdd"], corte=ct)
                    out["concordancia"].append({"pareado": bl, "outcome": oid, "rdd": f"{ref} {spec['rdd']}",
                                                "corte": ct, "concorda": bool(_concorda(r, rr))})
    for c in CORTES:
        ct = ROT_CORTE[c]
        for oid in ("dB1", "dB2"):
            r = _uma(est, bloco="CL-5", outcome=oid, corte=ct)
            if r["status"] == STATUS_PEND:
                out["oferta_local"][f"{oid} {ct}"] = {"codigo": STATUS_PEND}
                continue
            sem = {"tau": r["tau_sem_controle"], "ic95_inf": r["ic_sem_controle_inf"],
                   "ic95_sup": r["ic_sem_controle_sup"]}
            out["oferta_local"][f"{oid} {ct}"] = {
                "codigo": "CONTEM_ZERO" if _contem_zero(r) else "EXCLUI_ZERO",
                "difere_do_sem_controle": not _concorda(r, sem)}
    return out


# ---------------------------------------------------------------------------
# 10. Formatação e doc 57r (blocos gerados)
# ---------------------------------------------------------------------------

MENOS = "−"


def fn(x, casas=2, sinal=True) -> str:
    x = _f(x)
    if not math.isfinite(x):
        return "—"
    v = round(x, casas)
    s = f"{abs(v):.{casas}f}".replace(".", ",")
    if v < 0:
        return MENOS + s
    return ("+" if sinal and v > 0 else "") + s


def fp(p) -> str:
    p = _f(p)
    if not math.isfinite(p):
        return "—"
    return "< 0,001" if p < 0.001 else f"{p:.3f}".replace(".", ",")


def _esc(r) -> tuple[float, int, str]:
    if r["unidade"] == UN_FRAC:
        return 100.0, 1, " p.p."
    return 1.0, 2, ""


def fv(r, col="tau") -> str:
    e, k, u = _esc(r)
    return fn(e * _f(r[col]), k) + u


def fic(r, a="ic95_inf", b="ic95_sup") -> str:
    e, k, _ = _esc(r)
    lo, hi = _f(r[a]), _f(r[b])
    if math.isinf(lo) or math.isinf(hi):
        return "não limitado"
    return f"[{fn(e * lo, k)}; {fn(e * hi, k)}]"


def fint(x) -> str:
    x = _f(x)
    return "—" if not np.isfinite(x) else f"{int(x)}"


def _tab(cab: list[str], linhas: list[list[str]]) -> str:
    out = ["| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)]
    out += ["| " + " | ".join(l) + " |" for l in linhas]
    return "\n".join(out)


def _corte_txt(ct) -> str:
    return TXT_CORTE[int(round(_f(ct) * 1000))]


NOME_OUT = {"HI-1": "HI-1 célula preenchida", "HI-2": "HI-2 alocados por município",
            "H1M-FRAC": "fração de células preenchidas (município × ciclo)",
            "H1M-ALOC": "alocados por vaga imediata (município × ciclo)",
            "dB1": "ΔB1 vínculos de especialistas", "dB2": "ΔB2 horas SUS de especialistas",
            "dB3": "ΔB3 horas SUS dos outros especialistas", "dB4": "ΔB4 horas totais", "dB5": "ΔB5 generalistas"}
NOME_CONJ = {"sem": "sem controle", "L": "L", "M": "M", "L+M": "L+M", "LUF+M": "L-UF + M",
             **{v: NOME_VAR[v] for v in VARIAVEIS}}
ROT_BAL = {"capital": "capital", **{f"regiao_{r}": f"região {r}" for r in REGIOES}, "log_pop": "log(população)",
            "med": "médicos /10 mil (município)", "esp": "especialistas CBO-alvo /10 mil (município)",
            "esp_resto": "especialistas CBO-alvo /10 mil (resto da região)",
            "esp_curso": "especialistas do curso /10 mil (município)",
            "esp_resto_curso": "especialistas do curso /10 mil (resto da região)"}


def _var_txt(r) -> str:
    if not np.isfinite(_f(r["variacao_abs"])):
        return "—"
    e, k, u = _esc(r)
    return f"{fn(e * _f(r['variacao_abs']), k)}{u} ({fn(r['variacao_pct'], 0)}%)"


def bloco(nome: str, corpo: str) -> str:
    return f"<!-- CL:{nome}:inicio -->\n{corpo.rstrip()}\n<!-- CL:{nome}:fim -->"


def tab_psm(est: pd.DataFrame, blocos: tuple) -> str:
    linhas = []
    for _, r in est[est["bloco"].isin(blocos)].iterrows():
        if r["status"] != "EXECUTADO":
            motivo = "escore não estimado (separação)" if "escore" in str(r["nota"]) else (
                "sem pares (caliper)" if _f(r["n_pares"]) == 0 else
                ("menos de 2 pares" if _f(r["n_pares"]) == 1 else ""))
            linhas.append([r["bloco"], NOME_OUT[r["outcome"]], _corte_txt(r["corte"]), fn(r["janela"], 3, False),
                           r["status"] + (f" ({motivo})" if motivo else ""),
                           fint(r["n_pares"]) if r["metodo"] != "ipw" else "—",
                           (f"{fint(r['sem_par_abaixo'])} / {fint(r['sem_par_acima'])}" if np.isfinite(
                               _f(r["sem_par_abaixo"])) else "—")] + ["—"] * 6)
            continue
        if r["metodo"] == "ipw":
            pares = f"{fint(r['n_abaixo'])} / {fint(r['n_acima'])} (ponderados)"
            sem = "—"
        else:
            pares = fint(r["n_pares"])
            sem = f"{fint(r['sem_par_abaixo'])} / {fint(r['sem_par_acima'])}"
            if r["metodo"] == "pareamento_psm":
                sem += f" (fora do suporte: {fint(r['fora_suporte_abaixo'])} / {fint(r['fora_suporte_acima'])})"
        if r["entra_holm"]:
            mult = "Holm " + fp(r["p_holm"]) + (" (provisório)" if r["multiplicidade_provisoria"] else "")
        elif r["entra_bky"]:
            mult = "BKY " + fp(r["q_bky"]) + (" (provisório)" if r["multiplicidade_provisoria"] else "")
        else:
            mult = "— (sensibilidade)"
        linhas.append([r["bloco"], NOME_OUT[r["outcome"]], _corte_txt(r["corte"]), fn(r["janela"], 3, False),
                       r["status"], pares, sem, fv(r), fic(r),
                       fic(r, "ic_t_inf", "ic_t_sup") if r["metodo"] != "ipw" else "—", fp(r["p_valor"]),
                       mult,
                       (f"{fn(r['max_abs_dp_depois'], 2, False)} ({'limpa' if r['comparacao_limpa'] == 'SIM' else 'não limpa'})"
                        if r["metodo"] != "ipw" else "—")])
    return _tab(["Linha", "Outcome", "Corte", "Janela", "Status", "Pares (ou n abaixo / acima)",
                 "Sem par abaixo / acima", "Diferença média (acima − abaixo)", "IC 95% permutação (IPW: normal)",
                 "IC 95% t pareado", "p", "p Holm ou q BKY", "Maior DP absoluta depois"], linhas)


def tab_rdd(est: pd.DataFrame, parte: str, blocos: tuple) -> str:
    linhas = []
    sub = est[(est["parte"] == parte) & est["bloco"].isin(blocos) & (est["metodo"] == "RDD")]
    for _, r in sub.iterrows():
        if r["status"] == STATUS_PEND:
            linhas.append([r["bloco"], NOME_OUT[r["outcome"]], _corte_txt(r["corte"]), NOME_CONJ[r["conjunto"]],
                           STATUS_PEND] + ["—"] * 6)
            continue
        q = fp(r["q_bky"]) + (" (prov.)" if r["multiplicidade_provisoria"] else "") if r["entra_bky"] else "—"
        linhas.append([r["bloco"], NOME_OUT[r["outcome"]], _corte_txt(r["corte"]), NOME_CONJ[r["conjunto"]],
                       f"{fint(r['n_abaixo'])} / {fint(r['n_acima'])}",
                       f"{fint(r['saiu_ausencia_abaixo'])} / {fint(r['saiu_ausencia_acima'])}", fv(r), fic(r),
                       fp(r["p_valor"]), q, _var_txt(r)])
    return _tab(["Linha", "Outcome", "Corte", "Controles", "Municípios abaixo / acima",
                 "Saíram por ausência (abaixo / acima)", "Salto", "IC 95%", "p", "q BKY",
                 "Variação vs. sem controle na mesma amostra"], linhas)


def tab_cl0(bal: pd.DataFrame) -> str:
    linhas = []
    sub = bal[bal["tipo"] == "salto_no_corte"]
    for _, r in sub.iterrows():
        dps = "—" if not np.isfinite(_f(r["salto_padronizado"])) else fn(r["salto_padronizado"], 2)
        marca = "" if _contem_zero(r) else " **(IC sem zero)**"
        unidade_pp = r["variavel"] == "capital" or str(r["variavel"]).startswith("regiao_")
        tau = (fn(100 * _f(r["tau"]), 1) + " p.p.") if unidade_pp else fn(r["tau"], 2)
        ic = (f"[{fn(100 * _f(r['ic95_inf']), 1)}; {fn(100 * _f(r['ic95_sup']), 1)}]" if unidade_pp else
              f"[{fn(r['ic95_inf'], 2)}; {fn(r['ic95_sup'], 2)}]")
        linhas.append([r["populacao"], _corte_txt(r["corte"]), ROT_BAL.get(r["variavel"], r["variavel"]),
                       f"{fint(r['n_abaixo'])} / {fint(r['n_acima'])}", tau + marca, ic, fp(r["p_valor"]), dps])
    return _tab(["Amostra", "Corte", "Variável", "n abaixo / acima", "Salto no corte", "IC 95%", "p",
                 "Salto ÷ DP na janela"], linhas)


def tab_balanco(bal: pd.DataFrame) -> str:
    sub = bal[bal["tipo"] == "dif_padronizada"]
    linhas = []
    for (bl, parte, ct, jan), g in sub.groupby(["bloco", "parte", "corte", "janela"], sort=False):
        antes = g["dp_antes"].abs()
        depois = g["dp_depois"].abs()
        pior = g.loc[depois.idxmax(), "variavel"] if depois.notna().any() else "—"
        sem_par = not depois.notna().any()
        linhas.append([bl, "H1" if parte == "H1" else "oferta local", _corte_txt(ct), fn(jan, 3, False),
                       fint(g["n_acima_depois"].max()) if not sem_par else "0",
                       fn(antes.max(), 2, False), fn(depois.max(), 2, False), ROT_BAL.get(pior, pior),
                       "—" if sem_par else str(int((depois > LIMIAR_DP_META).sum())),
                       "—" if sem_par else str(int((depois > LIMIAR_DP_LIMPA).sum()))])
    return _tab(["Linha", "Parte", "Corte", "Janela", "Pares", "Maior DP absoluta antes", "Maior DP absoluta depois",
                 "Pior variável depois", "Variáveis com DP absoluta > 0,10", "Variáveis com DP absoluta > 0,25"],
                linhas)


def tab_variaveis(resumo: dict) -> str:
    v = resumo["variaveis"]
    linhas = [[x["variavel"], x["conjunto"], x["situacao"], x["motivo"]] for x in v["lista"]]
    return _tab(["Variável", "Conjunto", "Situação", "Observação"], linhas)


def tab_amostra(resumo: dict) -> str:
    am = resumo["amostra"]["rdd_h1"]
    linhas = []
    for k, x in am.items():
        oid, ct = k.split(" ")
        linhas.append([oid, _corte_txt(ct), fint(x["linhas_na_janela"]), fint(x["saiu_ausencia_L+M"]),
                       fint(len(x["municipios_que_sairam_L+M"]))])
    t1 = _tab(["Linha", "Corte", "Na janela h = 0,050 (células ou município × ciclo)",
               "Saíram de L+M por variável ausente", "Municípios distintos que saíram"], linhas)
    linhas, vistos = [], set()
    for x in resumo["amostra"]["pareamento"]:
        chave = (x["parte"], x["corte"], x["janela"])
        if chave in vistos:
            continue
        vistos.add(chave)
        linhas.append(["H1" if x["parte"] == "H1" else "oferta local", _corte_txt(x["corte"]), fn(x["janela"], 3, False),
                       f"{x['na_janela_abaixo']} / {x['na_janela_acima']}",
                       f"{x['sem_covariavel_abaixo']} / {x['sem_covariavel_acima']}", x["lado_com_menos_unidades"]])
    t2 = _tab(["Parte", "Corte", "Janela", "Na janela (abaixo / acima)", "Sem alguma covariável (abaixo / acima)",
               "Lado com menos unidades"], linhas)
    return t1 + "\n\nPareamento (unidades: município × ciclo na H1; município em V):\n\n" + t2


def tab_portao(resumo: dict) -> str:
    p = resumo["portao_hi"]
    linhas = [[x["linha"], _corte_txt(x["corte"]), fn(x["tau_csv"], 6), fn(x["tau_44"], 6), f"{x['max_abs_dif']:.1e}",
               "sim" if x["reproduz"] else "não"] for x in p["linhas"]]
    t = _tab(["Linha do 48b", "Corte", "Salto em HI_estimativas.csv", "Salto refeito aqui", "máx. dif. absoluta", "Reproduz"],
             linhas)
    oc = resumo.get("portao_oc") or {}
    if oc.get("aprovado"):
        t += (f"\n\nPortão do protocolo 64: OC-A1 em V, 0,300, salto {fn(oc['tau_oc'], 6)} em "
              f"`{oc['referencia']}` e {fn(oc['tau_44'], 6)} refeito aqui (máx. dif. absoluta "
              f"{max(oc['difs'].values()):.1e}): reproduz.")
    else:
        t += ("\n\nPortão do protocolo 64 (OC-A1 em 0,300): **não rodado**, porque as saídas `OC_*` não existiam nesta "
              "execução. As linhas de oferta local estão `PENDENTE_OC`.")
    return t


def _psm_frase(est: pd.DataFrame, oid: str, c: int) -> str:
    r = _uma(est, bloco="PS-1", outcome=oid, corte=ROT_CORTE[c])
    if r["status"] != "EXECUTADO":
        return f"{NOME_OUT[oid]}: sem estimativa ({r['nota']})"
    limpa = "balanço limpo" if r["comparacao_limpa"] == "SIM" else "balanço **não** limpo (|DP| > 0,25 depois)"
    return (f"{NOME_OUT[oid]}: {fv(r)} (IC permutação {fic(r)}; p Holm {fp(r['p_holm'])}"
            + (" provisório" if r["multiplicidade_provisoria"] else "") + f"; {fint(r['n_pares'])} pares; {limpa})")


def resumo_separacao(resumo: dict, parte: str) -> str:
    """Categorias presentes só de um lado na janela de 0,050 dos cortes sem escore (separação no logit)."""
    frases = []
    for x in resumo["amostra"]["pareamento"]:
        e = x.get("escore") or {}
        if x["parte"] != parte or abs(x["janela"] - JANELA_PAR / 1000) > 1e-9 or not e.get("erro"):
            continue
        cats = e.get("categorias_so_de_um_lado") or []
        if cats:
            frases.append(f"em {_corte_txt(x['corte'])}, " + ", ".join(
                f"{'capital' if c['variavel'] == 'capital' else c['variavel'].replace('regiao[', 'região ').rstrip(']')}"
                f" ({c['unidades']} unidade(s), todas {'acima' if c['lado'] == 'acima' else 'abaixo'} do corte)"
                for c in cats))
        else:
            frases.append(f"em {_corte_txt(x['corte'])}, {e['erro']}")
    return ("há categoria de L presente só de um lado da janela (separação): " + "; ".join(frases)) if frases else \
        "o logit não ajustou"


def resposta_curta(est: pd.DataFrame, bal: pd.DataFrame, resumo: dict) -> str:
    le = resumo["leitura"]
    partes = []
    ps = [x for x in le["psm"] if x["bloco"] == "PS-1"]
    exe = [x for x in ps if x["codigo"] not in ("SEM_ESTIMATIVA", STATUS_PEND)]
    sem = [x for x in ps if x["codigo"] == "SEM_ESTIMATIVA"]
    rejeita = [x for x in exe if x["codigo"] == "REJEITA_ZERO_DEPOIS_DO_HOLM"]
    exclui = [x for x in exe if x["codigo"] == "IC_EXCLUI_ZERO_SEM_HOLM"]
    cortes_exe = sorted({_corte_txt(x["corte"]) for x in exe})
    if rejeita:
        cab = ("**Pareando por escore de propensão (principal deste adendo), alguma linha da H1 rejeita zero depois "
               "do Holm**: relatam-se sinal e tamanho, com as ressalvas do diagnóstico 61 e do pacote do corte.")
    elif exclui:
        cab = ("**Pareando por escore de propensão (principal deste adendo), nenhuma linha da H1 rejeita zero depois "
               "do Holm**, mas o IC de permutação exclui zero em " + ", ".join(
                   f"{NOME_OUT[x['outcome']]} em {_corte_txt(x['corte'])}" for x in exclui) + ".")
    elif exe:
        cab = ("**Pareando por escore de propensão (principal deste adendo), a H1 não se distingue de zero em "
               + " e ".join(cortes_exe) + "**: comparando municípios parecidos em localização e em médicos na região, "
               "dos dois lados do corte, o preenchimento das vagas imediatas não difere de forma detectável.")
    else:
        cab = "**Pareando por escore de propensão (principal deste adendo), não houve estimativa da H1.**"
    if sem:
        cortes_sem = sorted({_corte_txt(x["corte"]) for x in sem})
        cab += (" Em " + " e ".join(cortes_sem) + " o PSM **não tem estimativa**: pela regra fixada antes (decisão 13), "
                "o logit não convergiu porque " + resumo_separacao(resumo, "H1") + ".")
    partes.append(cab)
    for c in CORTES:
        partes.append(f"- **Corte {TXT_CORTE[c]}** ({BOLSA[c]}): " + "; ".join(
            _psm_frase(est, oid, c) for oid in OUT_PAR_H1) + ".")
    nao_limpas = [x for x in ps if x["comparacao_limpa"] == "NAO"]
    if nao_limpas:
        partes.append("Pela regra fixada, as linhas com balanço não limpo não são lidas como comparação limpa: "
                      + ", ".join(f"{NOME_OUT[x['outcome']]} em {_corte_txt(x['corte'])}" for x in nao_limpas) + ".")
    ps2 = [x for x in le["psm"] if x["bloco"] == "PS-2"]
    if ps2 and all(x["codigo"] == STATUS_PEND for x in ps2):
        pass
    elif ps2:
        frases2 = []
        for c in CORTES:
            for oid in ("dB1", "dB2"):
                r = _uma(est, bloco="PS-2", outcome=oid, corte=ROT_CORTE[c])
                frases2.append(f"{NOME_OUT[oid]} em {TXT_CORTE[c]}: " + (
                    f"{fv(r)} (IC permutação {fic(r)}; p Holm {fp(r['p_holm'])}; {fint(r['n_pares'])} pares)"
                    if r["status"] == "EXECUTADO" else "sem estimativa"))
        falta2 = any(x["codigo"] == "SEM_ESTIMATIVA" for x in ps2)
        partes.append("**Oferta local pareada (PS-2, principal deste adendo para o protocolo 64):** "
                      + "; ".join(frases2) + "." + (" Onde falta estimativa, o motivo é o mesmo: "
                                                    + resumo_separacao(resumo, "oferta_local") + "." if falta2 else ""))
    # Controles na regressão (§4).
    frases = []
    for c in CORTES:
        ct = ROT_CORTE[c]
        for oid in ("HI-1", "HI-2"):
            r1 = _uma(est, bloco="CL-1", outcome=oid, corte=ct)
            r4 = _uma(est, bloco="CL-4", outcome=oid, corte=ct)
            frases.append(f"{oid} em {TXT_CORTE[c]}: sem controle {fv(r4)} {fic(r4)}, com L+M {fv(r1)} {fic(r1)} "
                          f"(`{le['rdd_h1'][f'{oid} {ct}']['codigo']}`)")
    partes.append("**Controles somados na regressão (CL-1, secundária), na mesma amostra:** " + "; ".join(frases) + ".")
    cl0 = le["cl0"]
    saltos = []
    for ct, por_pop in cl0.items():
        for pop, vs in por_pop.items():
            if vs and pop.startswith("H1"):
                saltos.append(f"em {_corte_txt(ct)} ({pop.split(' (')[0]}, {pop.split('(')[1].rstrip(')')}): "
                              + ", ".join(ROT_BAL.get(v, v) for v in vs))
    partes.append("**Balanço no corte (CL-0):** " + ("as variáveis com salto (IC sem zero) na amostra da H1 são "
                                                     + "; ".join(saltos) + "." if saltos else
                                                     "na amostra da H1, nenhuma variável de L ou M tem salto com IC "
                                                     "sem zero."))
    conc = le["concordancia"]
    if conc:
        disc = [x for x in conc if not x["concorda"]]
        partes.append("**Pareado × RDD:** " + (
            "nas comparações pela regra fixada, o pareado e a RDD chegam à mesma conclusão sobre o zero."
            if not disc else "discordam em " + "; ".join(f"{x['pareado']} {NOME_OUT[x['outcome']]} × {x['rdd']} em "
                                                         f"{_corte_txt(x['corte'])}" for x in disc)
            + ". Relatam-se as duas: o pareado supõe randomização local condicional; a RDD supõe continuidade. "
              "Nenhuma passa a ser a principal da H1 por isso."))
    n_pend = int((est["status"] == STATUS_PEND).sum())
    if n_pend:
        partes.append(f"**Oferta local (protocolo 64): {n_pend} linhas `PENDENTE_OC`**, sem número, porque as saídas "
                      "`OC_*` do protocolo 64 não existiam nesta execução. O Holm das PS-1 e o BKY são provisórios "
                      "até elas rodarem.")
    partes.append("Tudo é robustez pós-resultado da H1 e se refere ao pacote do corte, não à bolsa isolada. O principal "
                  "da H1 continua o 48b.")
    return "\n\n".join(partes)


def leitura_txt(resumo: dict) -> str:
    le = resumo["leitura"]
    linhas = []
    for k, x in le["rdd_h1"].items():
        oid, ct = k.split(" ")
        linhas.append(["§4 (CL-1 × CL-4)", oid, _corte_txt(ct), f"`{x['codigo']}`",
                       f"CL-0 com salto na H1: {'sim' if x['cl0_com_salto_na_H1'] else 'não'}; parecido: "
                       f"{'sim' if x['parecido_ao_sem_controle'] else 'não'}; IC menor: "
                       f"{'sim' if x['ic_menor'] else 'não'}; perto de zero: {'sim' if x['perto_de_zero'] else 'não'}; "
                       f"q BKY < 0,05: {'sim' if x['cl1_q_bky_menor_que_005'] else 'não'}"])
    for x in le["psm"]:
        linhas.append(["§3.2 (PSM)", f"{x['bloco']} {NOME_OUT[x['outcome']]}", _corte_txt(x["corte"]),
                       f"`{x['codigo']}`", f"comparação limpa: {x['comparacao_limpa'] or '—'}"
                       + ("; Holm provisório" if x["holm_provisorio"] else "")])
    for x in le["concordancia"]:
        linhas.append(["§3.1 (pareado × RDD)", f"{x['pareado']} {NOME_OUT[x['outcome']]} × {x['rdd']}",
                       _corte_txt(x["corte"]), "`CONCORDA`" if x["concorda"] else "`DISCORDA`", ""])
    for k, x in le["oferta_local"].items():
        oid, ct = k.split(" ")
        linhas.append(["§4 (CL-5)", NOME_OUT[oid], _corte_txt(ct), f"`{x['codigo']}`",
                       "" if x["codigo"] == STATUS_PEND else
                       f"difere do sem controle: {'sim' if x['difere_do_sem_controle'] else 'não'}"])
    return _tab(["Regra", "Linha", "Corte", "Código", "Detalhe"], linhas)


def tab_pendentes(est: pd.DataFrame) -> str:
    p = est[est["status"] == STATUS_PEND]
    if p.empty:
        return "Nenhuma linha pendente: as saídas `OC_*` existiam e o portão de OC-A1 passou."
    cont = p.groupby("bloco").size()
    return ("Linhas `PENDENTE_OC` (sem número), por bloco: " + "; ".join(f"{b}: {int(n)}" for b, n in cont.items())
            + f". Total: {len(p)}. Rodar `44_controles_localizacao_medicos.py --so-oferta-local` depois que o "
              "protocolo 64 gravar `OC_estimativas.csv`.")


def gerar_blocos(est: pd.DataFrame, bal: pd.DataFrame, resumo: dict) -> dict[str, str]:
    figs = "\n\n".join(f"![{Path(f['arquivo']).stem}](../../{f['arquivo']})\n\n**{f['como_ler']}**"
                       for f in resumo["figuras"])
    lim = [
        "**Pós-resultado na H1.** Os saltos da H1 já tinham sido vistos (48b e 48c). As variáveis e o pareamento foram "
        "congelados antes destas contas, mas a pergunta não é cega ao resultado.",
        "**Pacote do corte.** Em 0,300 e 0,400 mudam a bolsa e outras regras federais (auditoria 18). Nem a RDD nem "
        "o pareamento isolam o incentivo de R$ 5 mil.",
        "**O que o pareamento supõe.** Que, perto do corte e com o mesmo L+M, estar de um lado ou do outro é como "
        "sorteado. A RDD supõe continuidade e usa a reta. Nenhuma das duas é a principal da H1 por concordar ou não.",
        "**Poucos municípios.** Perto de cada corte há poucas unidades; o pareamento descarta quem não tem par, e o "
        "estimando passa a ser a média nos pares formados, não em todo o lado de cima.",
        "**Mesmo município em ciclos diferentes.** Na H1 pareada, um município pode aparecer em pares de ciclos "
        "diferentes; a permutação trata os pares como independentes.",
        "**Variáveis que ficaram fora.** " + resumo["variaveis"]["fora_txt"],
        "**Cursos fora da ponte.** " + resumo["variaveis"]["cursos_fora_txt"],
        "**Médicos é vínculo, não pessoa.** M conta vínculos do CNES (um médico em dois estabelecimentos conta duas "
        "vezes), como o B1 do protocolo 64.",
    ]
    return {
        "resposta_curta": resposta_curta(est, bal, resumo),
        "portao": tab_portao(resumo),
        "variaveis": tab_variaveis(resumo),
        "amostra": tab_amostra(resumo),
        "psm_h1": tab_psm(est, ("PS-1",)),
        "psm_oferta": tab_psm(est, ("PS-2",)),
        "psm_sens": tab_psm(est, ("PS-3", "PS-4")),
        "balanco_pareamento": tab_balanco(bal),
        "cl0": tab_cl0(bal),
        "rdd_h1": tab_rdd(est, "H1", ("CL-4", "CL-1", "CL-2", "CL-3")),
        "mahalanobis": tab_psm(est, ("CL-7", "CL-8", "CL-9")),
        "oferta_rdd": tab_rdd(est, "oferta_local", ("CL-5", "CL-6")),
        "pendentes": tab_pendentes(est),
        "leitura": leitura_txt(resumo),
        "figuras": figs,
        "limites": "\n".join(f"- {x}" for x in lim),
    }


MARCA = re.compile(r"<!-- CL:(?P<nome>[A-Za-z0-9_]+):inicio -->\n(?P<corpo>.*?)\n?<!-- CL:(?P=nome):fim -->", re.S)


def atualizar_doc(est: pd.DataFrame, bal: pd.DataFrame, resumo: dict) -> None:
    txt = DOC.read_text(encoding="utf-8")
    blocos = gerar_blocos(est, bal, resumo)
    achados = {m.group("nome") for m in MARCA.finditer(txt)}
    falta = set(blocos) - achados
    if falta:
        raise FalhaValidacao(f"doc 57r sem os marcadores {sorted(falta)}")
    txt = MARCA.sub(lambda m: bloco(m.group("nome"), blocos[m.group("nome")]) if m.group("nome") in blocos
                    else m.group(0), txt)
    DOC.write_text(txt, encoding="utf-8")


# ---------------------------------------------------------------------------
# 11. Figuras
# ---------------------------------------------------------------------------

AZUL = "#2a78d6"
LARANJA = "#eb6834"
CINZA = "#898781"
VERDE = "#1f8a4c"
ROXO = "#7a4fb5"
TINTA = "#0b0b0b"
TINTA2 = "#52514e"
FONTE = ("Fonte: outcomes do 12 (ciclos 1–3; ciclo 2 pelo quadro de 13/02/2026), CNES a09 (2024-06 a 2025-06), Censo "
         "2022, IBGE, IVS 2010 oficial (a08). EMPIRICO · scripts/rdd_bolsa/44_controles_localizacao_medicos.py")

COMO_LER = {
    "CL_principal.png": (
        "Como ler: cada ponto é a diferença no corte entre o lado de bolsa maior e o de bolsa menor; a barra é o IC "
        "95%. Em cima e no meio, a RDD (reta local de cada lado) sem controle (na amostra de L+M) e com L, M e L+M "
        "somados na regressão. Embaixo e nas linhas 'PSM' e 'Mahalanobis', o pareamento: municípios parecidos em "
        "localização e médicos na região, dos dois lados, comparados par a par, sem reta. O PSM é o principal deste "
        "adendo. Barra que cruza o zero: não se detecta diferença, o que não quer dizer que ela seja zero. Pacote do "
        "corte, não só a bolsa."),
    "CL_balanco_corte.png": (
        "Como ler: salto de cada variável de localização e de médicos no corte (RDD sem controle), dividido pelo "
        "desvio-padrão da variável na janela, para pôr todas na mesma escala. Azul: IC 95% exclui zero (a variável "
        "muda no corte); cinza: contém zero. Variável que salta no corte é explicação candidata para a queda da H1."),
    "CL_balanco_pareamento.png": (
        "Como ler: diferença padronizada (lado de cima − lado de baixo, em desvios-padrão) de cada variável, antes do "
        "pareamento (cinza), depois do PSM (azul) e depois do Mahalanobis (laranja), janela de 0,050 da H1. Linhas "
        "tracejadas: meta de 0,10 e limite de 0,25; acima de 0,25 a comparação não é lida como limpa."),
    "CL_escore.png": (
        "Como ler: distribuição do escore de propensão (chance estimada de estar acima do corte, dado L+M) dos dois "
        "lados, na janela de 0,050 da H1 (município × ciclo). Azul: lado de bolsa menor; laranja: lado de bolsa maior. "
        "Onde as barras não se sobrepõem não há com quem comparar (fora do suporte comum)."),
}


def _plt():
    import matplotlib
    matplotlib.use("Agg")
    matplotlib.rcParams["text.parse_math"] = False
    import matplotlib.pyplot as plt
    return plt


def _rodape(fig, texto: str, W: float, H_: float, largura: int = 150) -> None:
    yy = 0.12 + 0.24 * len(textwrap.wrap(texto, largura))
    for t in textwrap.wrap(texto, largura):
        fig.text(0.1 / W, yy / H_, t, fontsize=10.5, color=TINTA, va="top")
        yy -= 0.24
    fig.text(0.1 / W, 0.04 / H_, FONTE, fontsize=7.5, color=CINZA, va="bottom")


def _floresta(ax, itens: list[dict], titulo: str, eixo: str) -> None:
    n = len(itens)
    vals = [0.0] + [x for it in itens for x in (it["lo"], it["hi"]) if np.isfinite(x)]
    lo, hi = min(vals), max(vals)
    pad = 0.08 * (hi - lo if hi > lo else 1.0)
    ax.set_xlim(lo - pad, hi + pad)
    ax.set_ylim(n - 0.5, -0.5)
    ax.axvline(0, color="#2b2b2b", lw=1.1)
    for i, it in enumerate(itens):
        if not np.isfinite(it["tau"]):
            ax.text(0.5, i, it["valor"], transform=ax.get_yaxis_transform(), ha="center", va="center", fontsize=9,
                    color=CINZA)
        else:
            ax.plot([it["lo"], it["hi"]], [i, i], color=it["cor"], lw=2.6, solid_capstyle="butt")
            ax.scatter([it["tau"]], [i], s=55, color=it["cor"], edgecolor="white", zorder=3)
        ax.text(-0.02, i, it["rot"], transform=ax.get_yaxis_transform(), ha="right", va="center", fontsize=9.5)
        ax.text(1.02, i, it["valor"] if np.isfinite(it["tau"]) else "", transform=ax.get_yaxis_transform(),
                ha="left", va="center", fontsize=9)
    ax.set_yticks([])
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.set_title(titulo, fontsize=11, loc="left", color=TINTA, weight="bold")
    ax.set_xlabel(eixo, fontsize=9.5, color=TINTA2)
    ax.tick_params(axis="x", labelsize=9)


def _it(r, rot: str, esc: float, casas: int) -> dict:
    ok = r["status"] == "EXECUTADO"
    cor = CINZA if (not ok or _contem_zero(r)) else AZUL
    lo, hi = esc * _f(r["ic95_inf"]), esc * _f(r["ic95_sup"])
    tau = esc * _f(r["tau"]) if ok else np.nan
    if ok and not (np.isfinite(lo) and np.isfinite(hi)):
        return {"rot": rot, "tau": tau, "lo": tau, "hi": tau, "cor": CINZA,
                "valor": f"{fn(tau, casas)} [IC não limitado; {fint(r['n_pares'])} pares]"}
    sufixo = f" ({fint(r['n_pares'])} pares)" if ok and np.isfinite(_f(r.get("n_pares"))) else ""
    return {"rot": rot, "tau": tau, "lo": lo, "hi": hi, "cor": cor,
            "valor": (f"{fn(tau, casas)} [{fn(lo, casas)}; {fn(hi, casas)}]{sufixo}") if ok else
            ("sem estimativa" if r["status"] == "SEM_ESTIMATIVA" else r["status"])}


def gerar_figuras(est: pd.DataFrame, bal: pd.DataFrame, regs: list[dict]) -> list[dict]:
    plt = _plt()
    DIR_FIG.mkdir(parents=True, exist_ok=True)
    feitas = []
    # (1) principal: por corte, RDD sem/L/M/L+M e pareados PSM/Mahalanobis.
    nome = "CL_principal.png"
    W, H_ = 15.0, 11.0
    fig = plt.figure(figsize=(W, H_))
    fig.text(0.1 / W, (H_ - 0.12) / H_, "H1 no corte: sem controle, com L, M e L+M na regressão, e pareada (PSM e "
             "Mahalanobis)", fontsize=14, weight="bold", va="top")
    for j, c in enumerate(CORTES):
        ct = ROT_CORTE[c]
        x0 = 2.6 + j * 7.4
        sel = lambda **k: _uma(est, corte=ct, **k)   # noqa: E731
        rdd = [("CL-4", "sem", "sem controle"), ("CL-2", "L", "L"), ("CL-2", "M", "M"), ("CL-1", "L+M", "L+M")]
        p1 = [_it(sel(bloco=b_, outcome="HI-1", conjunto=cj), f"RDD {rt}", 100, 1) for b_, cj, rt in rdd]
        p1 += [_it(sel(bloco="PS-1", outcome="H1M-FRAC"), "PSM (municipal)", 100, 1),
               _it(sel(bloco="CL-7", outcome="H1M-FRAC"), "Mahalanobis (munic.)", 100, 1)]
        p2 = [_it(sel(bloco=b_, outcome="HI-2", conjunto=cj), f"RDD {rt}", 1, 2) for b_, cj, rt in rdd]
        p3 = [_it(sel(bloco="PS-1", outcome="H1M-ALOC"), "PSM", 1, 2),
              _it(sel(bloco="CL-7", outcome="H1M-ALOC"), "Mahalanobis", 1, 2)]
        alt = [len(p1), len(p2), len(p3)]
        y = H_ - 0.95
        for k, (its, tit, eixo) in enumerate((
                (p1, f"Corte {TXT_CORTE[c]} ({BOLSA[c]})\nCélula com vaga imediata preenchida",
                 "diferença no corte (p.p.)"),
                (p2, "Médicos alocados por município (RDD, com controle das vagas)", "médicos por município"),
                (p3, "Médicos alocados por vaga imediata (pareado)", "médicos por vaga imediata"))):
            h = 0.42 * alt[k]
            y0 = y - 0.75 - h
            ax = fig.add_axes([x0 / W, y0 / H_, 3.0 / W, h / H_])
            _floresta(ax, its, tit, eixo)
            y = y0 - 0.55
    _rodape(fig, COMO_LER[nome], W, H_, 170)
    fig.savefig(DIR_FIG / nome, dpi=170, facecolor="white", metadata={"Software": None})
    plt.close(fig)
    feitas.append({"arquivo": rotulo(DIR_FIG / nome), "como_ler": COMO_LER[nome],
                   "fonte": "CL_estimativas.csv: CL-4, CL-2 (L, M), CL-1, PS-1 e CL-7"})
    # (2) balanço no corte (CL-0).
    nome = "CL_balanco_corte.png"
    cl0 = bal[(bal["tipo"] == "salto_no_corte") & (bal["parte"] == "H1")]
    W, H_ = 14.0, 7.6
    fig = plt.figure(figsize=(W, H_))
    fig.text(0.1 / W, (H_ - 0.12) / H_, "Balanço no corte (CL-0): salto de cada variável, em desvios-padrão da janela",
             fontsize=14, weight="bold", va="top")
    for j, c in enumerate(CORTES):
        sub = cl0[cl0["corte"].astype(str) == ROT_CORTE[c]]
        its = []
        for _, r in sub.iterrows():
            dp = _f(r["dp_janela"])
            ok = np.isfinite(_f(r["tau"])) and np.isfinite(dp) and dp > 0
            its.append({"rot": ROT_BAL.get(r["variavel"], r["variavel"]), "tau": _f(r["tau"]) / dp if ok else np.nan,
                        "lo": _f(r["ic95_inf"]) / dp if ok else np.nan, "hi": _f(r["ic95_sup"]) / dp if ok else np.nan,
                        "cor": CINZA if _contem_zero(r) else AZUL,
                        "valor": f"{fn(_f(r['tau']) / dp, 2)} DP" if ok else "—"})
        ax = fig.add_axes([(3.3 + j * 6.9) / W, 1.55 / H_, 2.9 / W, 5.2 / H_])
        _floresta(ax, its, f"Corte {TXT_CORTE[c]}", "salto ÷ DP da variável na janela")
    _rodape(fig, COMO_LER[nome], W, H_, 160)
    fig.savefig(DIR_FIG / nome, dpi=170, facecolor="white", metadata={"Software": None})
    plt.close(fig)
    feitas.append({"arquivo": rotulo(DIR_FIG / nome), "como_ler": COMO_LER[nome],
                   "fonte": "CL_balanco.csv: tipo salto_no_corte, amostras da H1"})
    # (3) balanço do pareamento (Love plot).
    nome = "CL_balanco_pareamento.png"
    db = bal[(bal["tipo"] == "dif_padronizada") & (bal["parte"] == "H1") & (np.abs(bal["janela"] - JANELA_PAR / 1000)
                                                                           < 1e-9)]
    W, H_ = 14.0, 7.2
    fig = plt.figure(figsize=(W, H_))
    fig.text(0.1 / W, (H_ - 0.12) / H_, "Balanço antes e depois do pareamento (H1, janela de 0,050)", fontsize=14,
             weight="bold", va="top")
    for j, c in enumerate(CORTES):
        ax = fig.add_axes([(3.3 + j * 6.9) / W, 1.5 / H_, 3.3 / W, 5.0 / H_])
        sub = db[db["corte"].astype(str) == ROT_CORTE[c]]
        for k, v in enumerate(VARS_BAL):
            g = sub[sub["variavel"] == v]
            ps = g[g["bloco"] == "PS-1"]
            mh = g[g["bloco"] == "CL-7"]
            if len(ps):
                ax.scatter([abs(_f(ps["dp_antes"].iloc[0]))], [k], color=CINZA, s=40)
                ax.scatter([abs(_f(ps["dp_depois"].iloc[0]))], [k], color=AZUL, s=40)
            if len(mh):
                ax.scatter([abs(_f(mh["dp_depois"].iloc[0]))], [k], color=LARANJA, s=40, marker="D")
        ax.set_yticks(range(len(VARS_BAL)))
        ax.set_yticklabels([ROT_BAL[v] for v in VARS_BAL] if j == 0 else [""] * len(VARS_BAL), fontsize=9.5)
        ax.set_ylim(len(VARS_BAL) - 0.5, -0.5)
        for lim in (LIMIAR_DP_META, LIMIAR_DP_LIMPA):
            ax.axvline(lim, color=TINTA2, lw=1, ls=(0, (4, 3)))
        ax.set_xlabel("|diferença padronizada|", fontsize=9.5)
        ax.set_title(f"Corte {TXT_CORTE[c]}", fontsize=11, loc="left", weight="bold")
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)
    fig.legend(handles=[plt.Line2D([], [], color=CINZA, marker="o", ls="", label="antes"),
                        plt.Line2D([], [], color=AZUL, marker="o", ls="", label="depois do PSM"),
                        plt.Line2D([], [], color=LARANJA, marker="D", ls="", label="depois do Mahalanobis")],
               loc="upper right", fontsize=10, frameon=False)
    _rodape(fig, COMO_LER[nome], W, H_, 160)
    fig.savefig(DIR_FIG / nome, dpi=170, facecolor="white", metadata={"Software": None})
    plt.close(fig)
    feitas.append({"arquivo": rotulo(DIR_FIG / nome), "como_ler": COMO_LER[nome],
                   "fonte": "CL_balanco.csv: tipo dif_padronizada, PS-1 e CL-7, janela 0,050"})
    # (4) escore de propensão dos dois lados.
    nome = "CL_escore.png"
    W, H_ = 14.0, 6.0
    fig = plt.figure(figsize=(W, H_))
    fig.text(0.1 / W, (H_ - 0.12) / H_, "Escore de propensão dos dois lados (H1, janela de 0,050)", fontsize=14,
             weight="bold", va="top")
    for j, c in enumerate(CORTES):
        rg = next((x for x in regs if x["parte"] == "H1" and x["corte"] == ROT_CORTE[c]
                   and abs(x["janela"] - JANELA_PAR / 1000) < 1e-9), None)
        ax = fig.add_axes([(0.9 + j * 6.9) / W, 1.6 / H_, 5.8 / W, 3.6 / H_])
        if rg and rg.get("escore_por_unidade"):
            e = np.array(rg["escore_por_unidade"]["escore"])
            a = np.array(rg["escore_por_unidade"]["acima"]).astype(bool)
            bins = np.linspace(0, 1, 21)
            ax.hist(e[~a], bins=bins, color=AZUL, alpha=0.6, label="abaixo do corte (bolsa menor)")
            ax.hist(e[a], bins=bins, color=LARANJA, alpha=0.6, label="acima do corte (bolsa maior)")
            ax.legend(fontsize=9, frameon=False)
        else:
            cats = ((rg or {}).get("escore") or {}).get("categorias_so_de_um_lado") or []
            txt = "escore não estimado (o logit não convergiu)"
            if cats:
                txt += "\nseparação: " + ", ".join(
                    ("capital" if c_["variavel"] == "capital" else c_["variavel"].replace("regiao[", "região ")
                     .rstrip("]")) + f" só {'acima' if c_['lado'] == 'acima' else 'abaixo'} do corte" for c_ in cats)
            ax.text(0.5, 0.5, txt, ha="center", va="center", transform=ax.transAxes, fontsize=10.5)
            ax.set_yticks([])
        ax.set_title(f"Corte {TXT_CORTE[c]}", fontsize=11, loc="left", weight="bold")
        ax.set_xlabel("escore de propensão (chance de estar acima, dado L+M)", fontsize=9.5)
        ax.set_ylabel("município × ciclo", fontsize=9.5)
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)
    _rodape(fig, COMO_LER[nome], W, H_, 160)
    fig.savefig(DIR_FIG / nome, dpi=170, facecolor="white", metadata={"Software": None})
    plt.close(fig)
    feitas.append({"arquivo": rotulo(DIR_FIG / nome), "como_ler": COMO_LER[nome],
                   "fonte": "CL_resumo.json: amostra.pareamento (escore por unidade), H1, janela 0,050"})
    return feitas


# ---------------------------------------------------------------------------
# 12. Resumo, gravação e execução
# ---------------------------------------------------------------------------

def descrever_variaveis(info_cov: dict, cov: pd.DataFrame, b: dict) -> dict:
    cel = pd.concat([b["CK"][k] for k in CICLOS], ignore_index=True)
    imed = cel[cel["tipo_celula"].isin(["so_imed", "mista"])]
    fora_curso = imed[~imed["cod_curso"].isin(range(1, 17))]
    lista = [
        {"variavel": "capital", "conjunto": "L", "situacao": "entrou", "motivo": "referência do IBGE (48c), 27 capitais"},
        {"variavel": "macrorregião (efeito fixo)", "conjunto": "L", "situacao": "entrou",
         "motivo": "5 Grandes Regiões, referência do IBGE; quatro dummies (Centro-Oeste de referência)"},
        {"variavel": "UF (efeito fixo)", "conjunto": "L-UF (sensibilidade, CL-2)", "situacao": "entrou",
         "motivo": "no lugar da macrorregião, só na linha L-UF + M"},
        {"variavel": "log(população 2022)", "conjunto": "L", "situacao": "entrou",
         "motivo": f"Censo 2022; municípios do a08 sem população > 0: {info_cov['populacao']['municipios_sem_populacao_2022']}"},
        {"variavel": "médicos por 10 mil hab. (município)", "conjunto": "M", "situacao": "entrou",
         "motivo": f"vínculos CBO 2251/2252/2253, média 2024-06 a 2025-06; ausente em "
                   f"{info_cov['painel_a09']['municipios_med_ausente']} município(s) do a08"},
        {"variavel": "especialistas nas CBO-alvo por 10 mil hab. (município)", "conjunto": "M", "situacao": "entrou",
         "motivo": "na célula, CBO do curso (ponte do a09); no município, todas as CBO-alvo"},
        {"variavel": "especialistas nas CBO-alvo por 10 mil hab. (resto da região de saúde)", "conjunto": "M",
         "situacao": "entrou", "motivo": f"região de saúde = CIR oficial do TabNet/DATASUS; "
                                          f"{info_cov['regiao_saude']['regioes']} CIR; municípios do a08 sem CIR: "
                                          f"{info_cov['regiao_saude']['municipios_a08_sem_cir']}; em CIR de um só "
                                          f"(resto ausente): {info_cov['regiao_saude']['municipios_em_regiao_de_um_so']}"},
    ]
    fora = ("Do registro 63, ficaram fora deste adendo por não estarem no repositório ou não serem pré-determinadas: "
            "escola médica e residência (e-MEC, CNRM), beneficiários de plano (ANS), PIB e receita municipal, homicídios "
            "e leitos (não adquiridos; nada foi adquirido aqui); REGIC (testado no 61, não está no conjunto congelado); "
            "tipo de vaga, concorrência, candidatos e vagas oferecidas (podem responder ao corte). PIB, IDHM e renda não "
            "entram (não podem substituir o IVS).")
    cursos = (f"Na célula, as variáveis de especialistas usam as CBO do curso; os cursos 17 a 20 do ciclo 3 não estão "
              f"na ponte do a09: {len(fora_curso)} células com vaga imediata desses cursos ficam fora das linhas da HI-1 "
              "que usam M (contadas na seção 1).")
    return {"lista": lista, "fora_txt": fora, "cursos_fora_txt": cursos,
            "celulas_imed_cursos_fora_da_ponte": int(len(fora_curso)),
            "celulas_imed_cursos_fora_da_ponte_por_ciclo": {str(k): int(v) for k, v in
                                                            fora_curso.groupby("ciclo").size().items()}}


def entradas() -> list[dict]:
    arqs = [ADENDO, HI_EST, A08, POP22, PAINEL, MANIF_A09, CIR_BRUTO, CIR_MANIF, REF_IBGE, REF_MANIF, OL_RES, T23.ARQ_VC, T23.ARQ_VM,
            T40.ARQ_C2_13FEV]
    if OC_EST.exists():
        arqs.append(OC_EST)
    return [{"arquivo": rotulo(p), "sha256": sha256(p)} for p in arqs]


def gravar(est: pd.DataFrame, bal: pd.DataFrame, resumo: dict) -> None:
    est.to_csv(OUT / NOME_EST, index=False)
    bal.to_csv(OUT / NOME_BAL, index=False)
    (OUT / NOME_RESUMO).write_text(json.dumps(_nan_none(resumo), ensure_ascii=False, indent=1) + "\n",
                                   encoding="utf-8")


def ler_saidas() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    est = pd.read_csv(OUT / NOME_EST, dtype={"corte": str, "comparacao_limpa": str}, keep_default_na=True)
    for c in ("entra_holm", "entra_bky", "multiplicidade_provisoria"):
        est[c] = est[c].astype(str).str.lower().isin(["true", "1"])
    for c in ("nota", "covariaveis_descartadas", "comparacao_limpa", "variaveis"):
        est[c] = est[c].fillna("")
    bal = pd.read_csv(OUT / NOME_BAL, dtype={"corte": str})
    bal["nota"] = bal["nota"].fillna("")
    return est, bal, json.loads((OUT / NOME_RESUMO).read_text(encoding="utf-8"))


def _finalizar(linhas: list[dict], bal_l: list[dict]) -> tuple[pd.DataFrame, pd.DataFrame]:
    est = pd.DataFrame(linhas).reindex(columns=COLUNAS)
    for c in ("entra_holm", "entra_bky", "multiplicidade_provisoria"):
        est[c] = est[c].astype(bool)
    est = aplicar_multiplicidade(est)
    if est["id_linha"].duplicated().any():
        raise FalhaValidacao(f"id_linha duplicado: {est.loc[est['id_linha'].duplicated(), 'id_linha'].tolist()}")
    bal = pd.DataFrame(bal_l).reindex(columns=COLUNAS_BAL)
    return est, bal


def _contagens(est: pd.DataFrame) -> dict:
    return {"linhas": int(len(est)), "por_status": est["status"].value_counts().sort_index().to_dict(),
            "por_bloco": est["bloco"].value_counts().sort_index().to_dict(),
            "pendentes_oc": int((est["status"] == STATUS_PEND).sum()),
            "holm": {"n_familia": int(est["entra_holm"].sum()),
                     "provisorio": bool((est["entra_holm"] & (est["status"] == STATUS_PEND)).any())},
            "bky": {"n_familia": int(est["entra_bky"].sum()),
                    "provisorio": bool((est["entra_bky"] & (est["status"] == STATUS_PEND)).any())}}


def executar(atualizar: bool) -> int:
    global UFS
    if sha256(ADENDO) != SHA_ADENDO:
        raise FalhaValidacao("o adendo 48d mudou depois do congelamento (com a nota §3.2)")
    print("Covariáveis L e M (a08, Censo 2022, IBGE, CIR, a09 pré)...", flush=True)
    cov, curso, info_cov = construir_covariaveis()
    UFS = sorted(cov["cd_uf"].unique().tolist())
    print("Base da H1 (48b, ciclo 2 pelo quadro de 13/02/2026)...", flush=True)
    b = bases_h1(cov, curso)
    print("Portão: HI-1 e HI-2 do 48b...", flush=True)
    portao = portao_hi(b)
    print(f"  reproduz (máx |dif| = {portao['max_abs_dif']:.1e})", flush=True)
    v, info_v, base = base_v(cov)
    print("CL-0 a CL-4 (H1)...", flush=True)
    lin_rdd, am_rdd = linhas_rdd_h1(b)
    bal_l = linhas_cl0(b, v)
    print("Pareamento da H1 (Mahalanobis, PSM, IPW)...", flush=True)
    lin_par, bal_par, regs = linhas_pareamento_h1(b)
    linhas = lin_rdd + lin_par
    bal_l += bal_par
    portao_oc_res, info_oc = None, None
    if OC_EST.exists():
        print("Saídas OC_* presentes: parte do protocolo 64...", flush=True)
        dB, info_oc = construir_delta_b(v)
        vv = v.merge(dB, on="co_ibge", how="left", validate="one_to_one")
        portao_oc_res = portao_oc(vv)
        lo, bo, ro = linhas_oferta(vv)
        linhas += lo
        bal_l += bo
        regs += ro
    else:
        print("Saídas OC_* ausentes: linhas da oferta local ficam PENDENTE_OC.", flush=True)
        linhas += linhas_pendentes()
    est, bal = _finalizar(linhas, bal_l)
    resumo = montar_resumo(est, bal, info_cov, portao, portao_oc_res, info_oc, info_v, am_rdd, regs,
                           descrever_variaveis(info_cov, cov, b))
    resumo["figuras"] = gerar_figuras(est, bal, regs)
    gravar(est, bal, resumo)
    if atualizar:
        atualizar_doc(est, bal, resumo)
        print(f"Doc regravado: {rotulo(DOC)}")
    for _, r in est[est["entra_holm"]].iterrows():
        print(f"  {r['bloco']} {r['outcome']} {r['corte']}: {r['status']} tau={_f(r['tau']):.4f} "
              f"[{_f(r['ic95_inf']):.4f}; {_f(r['ic95_sup']):.4f}] p={_f(r['p_valor']):.4f} p_holm={_f(r['p_holm']):.4f}")
    print(f"Gravado: {rotulo(OUT / NOME_EST)} ({len(est)} linhas), {NOME_BAL}, {NOME_RESUMO}, {rotulo(DIR_FIG)}/")
    return 0


def montar_resumo(est, bal, info_cov, portao, portao_oc_res, info_oc, info_v, am_rdd, regs, variaveis) -> dict:
    resumo = {
        "etapa": "Adendo 48d: H1 e oferta local no corte com controles L e M e pareamento (PSM principal, nota §3.2)",
        "natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "data_execucao": DATA_EXECUCAO,
        "script": "scripts/rdd_bolsa/44_controles_localizacao_medicos.py",
        "adendo": {"arquivo": rotulo(ADENDO), "sha256": sha256(ADENDO), "commit_congelamento": COMMIT_CONGELAMENTO,
                   "commit_nota_3_2": COMMIT_NOTA_32, "commit_decisoes_57r": COMMIT_DECISOES},
        "contraste": CONTRASTE,
        "parametros": {"cortes": [0.300, 0.400], "h": H / 1000, "janela_pareamento": JANELA_PAR / 1000,
                       "janela_sensibilidade": JANELA_SENS / 1000, "caliper_mahalanobis": CALIPER_MAH,
                       "caliper_psm": CALIPER_PS, "aparo_ipw": list(APARO_IPW), "n_permutacoes": N_PERM,
                       "semente": SEMENTE, "tolerancia_portao": TOL_PORTAO, "competencias_pre": list(COMP_PRE),
                       "competencias_pos_oferta_local": list(COMP_POS)},
        "entradas": entradas(),
        "covariaveis": info_cov,
        "variaveis": variaveis,
        "portao_hi": portao,
        "portao_oc": portao_oc_res,
        "oferta_local": {"status": "EXECUTADA" if portao_oc_res else STATUS_PEND, "V": info_v,
                         "construcao_delta_b": info_oc},
        "amostra": {"rdd_h1": {f"{k[0]} {ROT_CORTE[k[1]]}": x for k, x in am_rdd.items()}, "pareamento": regs},
        "contagens": _contagens(est),
        "leitura": leituras(est, bal),
        "integridade": {"ivs": "IVS 2010 oficial (a08); o arquivo local de IVS da auditoria 16 nao e lido",
                        "regiao_saude": "CIR oficial (data/raw, so lida); a malha de regioes (que traz IVS, IDHM e "
                                        "renda) nao e lida",
                        "cnes": "competencias 202406-202506 (covariaveis) e 202406-202608 (oferta local); nenhuma "
                                ">= 202609",
                        "imputacao": "nada imputado; ausente fica ausente e e contado",
                        "saidas_nao_regravadas": ["HI_*", "HC_*", "OC_*", "E7_*", "OL_*", "EQ_*"]},
        "saidas": {"estimativas": rotulo(OUT / NOME_EST), "balanco": rotulo(OUT / NOME_BAL),
                   "resumo": rotulo(OUT / NOME_RESUMO), "figuras": rotulo(DIR_FIG), "doc": rotulo(DOC)},
        "linguagem": "pacote do corte; 'anda junto com', nunca 'causa'; 'nao se detecta' nao e 'zero'",
    }
    return resumo


def executar_so_oferta(atualizar: bool) -> int:
    global UFS
    if not OC_EST.exists():
        print("PENDENTE_OC: output/rdd_bolsa/OC_estimativas.csv ainda não existe; nada foi estimado nem gravado.")
        return 0
    if sha256(ADENDO) != SHA_ADENDO:
        raise FalhaValidacao("o adendo 48d mudou depois do congelamento (com a nota §3.2)")
    est0, bal0, resumo = ler_saidas()
    pend = est0["status"] == STATUS_PEND
    if not pend.any():
        print("Nenhuma linha PENDENTE_OC nas saídas: nada a fazer.")
        return 0
    cov, _curso, _ = construir_covariaveis()
    UFS = sorted(cov["cd_uf"].unique().tolist())
    v, info_v, base = base_v(cov)
    dB, info_oc = construir_delta_b(v)
    vv = v.merge(dB, on="co_ibge", how="left", validate="one_to_one")
    portao_oc_res = portao_oc(vv)
    lo, bo, ro = linhas_oferta(vv)
    novas = pd.DataFrame(lo).reindex(columns=COLUNAS)
    if set(novas["id_linha"]) != set(est0.loc[pend, "id_linha"]):
        raise FalhaValidacao("linhas de oferta local não batem com as PENDENTE_OC gravadas")
    manter = est0[~pend].to_dict("records")
    est, bal = _finalizar(manter + lo, bal0.to_dict("records") + bo)
    resumo["portao_oc"] = portao_oc_res
    resumo["oferta_local"] = {"status": "EXECUTADA", "V": info_v, "construcao_delta_b": info_oc}
    resumo["amostra"]["pareamento"] = resumo["amostra"]["pareamento"] + ro
    resumo["contagens"] = _contagens(est)
    resumo["leitura"] = leituras(est, bal)
    resumo["entradas"] = entradas()
    resumo["figuras"] = gerar_figuras(est, bal, resumo["amostra"]["pareamento"])
    gravar(est, bal, resumo)
    if atualizar:
        atualizar_doc(est, bal, resumo)
    print(f"Oferta local estimada; portão OC-A1 reproduz. Gravado {rotulo(OUT / NOME_EST)}.")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--atualizar-doc", action="store_true", help="regrava os blocos do doc 57r")
    ap.add_argument("--so-oferta-local", action="store_true", help="só a parte do protocolo 64 (exige OC_*)")
    ap.add_argument("--so-doc", action="store_true", help="só regrava os blocos do doc 57r das saídas")
    args = ap.parse_args(argv)
    try:
        if args.so_doc:
            atualizar_doc(*ler_saidas())
            return 0
        if args.so_oferta_local:
            return executar_so_oferta(True)
        return executar(args.atualizar_doc)
    except (FalhaValidacao, T40.FalhaValidacao, T41.FalhaValidacao, T37.FalhaValidacao, T43.FalhaValidacao,
            K1M.FalhaValidacao, D2M.FalhaValidacao) as erro:
        print(f"FALHA (nada gravado): {erro}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
