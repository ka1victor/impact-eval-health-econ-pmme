"""Adendo §7 do protocolo 48: abertura de vagas como seleção (A1–A4).

Protocolo: `docs/06_execucao/48_protocolo_contagem_vagas_preenchidas.md`, §7
(congelado em 19/10/2026, antes de estimar) e a correção do §8 (quando a faixa
da bolsa ficou conhecida, por ciclo). Estatuto pós-resultado: toda linha sai
com `estatuto = PROTOCOLO_48_ADENDO_7_POS_RESULTADO` e `natureza_dos_dados =
EMPIRICO`. Nada aqui muda as linhas S-a a S-j, o Holm do §3, as saídas `N_*`
nem E3–E9.

Análises
--------
- A1: efeito total por habitante, sem condicionar na abertura. População U
  (todos os municípios com IVS 2010 oficial), com zero estrutural onde o
  município não teve célula no quadro (sem célula = zero vaga oferecida e zero
  vaga preenchida: é zero verdadeiro, não imputação). Outcomes: vagas
  preenchidas (N1, `n_alocados_ch1`) e oferecidas (imediatas + cadastro
  reserva) por 10 mil habitantes do Censo 2022. Robustez: Poisson local das
  contagens com offset log(população).
- A2: limites de Lee (2009) para a abertura.
  * margem intensiva, no nível da vaga: taxa de seleção de cada lado = vagas
    oferecidas por 10 mil habitantes no corte (intercepto local linear de cada
    lado, em U); p = (s_maior − s_menor) / s_maior no lado com mais vagas por
    habitante; outcome binário "vaga preenchida", com as vagas preenchidas da
    célula = min(alocados, vagas oferecidas da célula); f = taxa de
    preenchimento no corte (local linear da fração do município ponderada
    pelas vagas, em V); limites inferior = max(0, (f − p)/(1 − p)), superior =
    min(1, f/(1 − p)) no lado aparado; IC de Imbens e Manski (2004) com EP dos
    limites por bootstrap de municípios (semente fixa, 999 reamostras);
  * margem extensiva: seleção = ter ≥ 1 vaga (célula) no quadro; outcome =
    vagas preenchidas ÷ oferecidas do município (mesma contagem limitada);
    aparo de Lee pelo topo e pela base (`rdd_lib.limites_lee_rd` com um corte;
    no empilhado, o mesmo algoritmo com aparo dentro de cada grupo).
  Monotonicidade: a abertura muda num só sentido no corte (toda vaga que
  existiria do lado de menor abertura também existiria do outro).
- A3: unidade = célula (estabelecimento × curso) do quadro da 1ª chamada,
  RDD no IVS do município, cluster por município, efeitos fixos de curso ×
  ciclo e de tipo de vaga (imediata ou só cadastro reserva). O tipo de prática
  não existe nas células do quadro: a lacuna é registrada, nada é imputado.
- A4: S-b (N1 em V) e A1 com covariáveis pré-determinadas (CCFT 2019): log da
  população de 2022 e estoque CNES pré-programa (`202406`–`202506`, média
  mensal de profissionais distintos) das CBO-alvo e de generalistas. O painel
  do CNES não traz estabelecimentos hospitalares: lacuna registrada.

Base comum (§7): local linear, kernel triangular, h = 0,050, ciclos 1–3,
cortes separados e empilhados (intercepto e inclinações por ciclo × corte,
salto comum), CR1 por município. Salto = lado com bolsa maior menos lado com
bolsa menor; o corte fica no lado de baixo.

Integridade: nada simulado ou imputado; ausente fica ausente (o município sai
da linha e é contado); o único zero criado é o zero estrutural de U do
protocolo. A running variable é o IVS 2010 oficial (a08), conferido contra a
coluna `ivs_2010_oficial` dos outcomes; o arquivo local de IVS da auditoria 16
não é lido. O painel CNES é lido só nas competências pré-programa.

Uso
---
    python3 scripts/rdd_bolsa/24_abertura_vagas_selecao.py
    python3 scripts/rdd_bolsa/24_abertura_vagas_selecao.py --atualizar-doc
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
from scipy import optimize, stats

ROOT = Path(__file__).resolve().parents[2]
DIR_RDD = ROOT / "scripts" / "rdd_bolsa"


def _importar(caminho: Path, nome: str):
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    return mod


_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
T23 = _importar(DIR_RDD / "23_estimar_contagem_vagas.py", "contagem_vagas_para_na")
sys.dont_write_bytecode = _bytecode
L = T23.L
E6 = T23.E6

# ---------------------------------------------------------------------------
# Caminhos e parâmetros do protocolo (constantes permitidas: cortes, h, semente, reamostras)
# ---------------------------------------------------------------------------

OUT = T23.OUT
OUTC = T23.OUTC
ARQ_VM, ARQ_VC, ARQ_U = T23.ARQ_VM, T23.ARQ_VC, T23.ARQ_U
A08 = T23.A08
ARQ_POP = ROOT / "output" / "aquisicao" / "populacao_censo2022_municipios.csv"
ARQ_CNES = ROOT / "output" / "aquisicao" / "cnes_nacional" / "painel_municipio_cbo_mes.parquet"
ARQ_E9 = OUT / "E9_resumo.json"
ARQ_N_EST = OUT / "N_estimativas.csv"
PROTOCOLO_MD = T23.PROTOCOLO_MD
DOC49 = T23.DOC49

NOME_EST = "NA_estimativas.csv"
NOME_RESUMO = "NA_resumo.json"
DIR_FIG = "NA_figuras"

DATA_EXECUCAO = "2026-10-19"
ESTATUTO = "PROTOCOLO_48_ADENDO_7_POS_RESULTADO"
NATUREZA = "EMPIRICO"
FAMILIA = "N_ADENDO_7"   # nao "NA": o pandas leria o rotulo como ausente
CORTES = T23.CORTES
H = T23.H
H_SENS = T23.H_SENS
CICLOS = (1, 2, 3)
POR_HAB = 10_000.0
N_BOOT = 999
SEMENTE_BOOT = (L.SEMENTE, 48, 7)           # semente fixa do bootstrap de municípios (protocolo 48, adendo §7)
COMP_PRE = ("202406", "202506")             # competências pré-programa do CNES (adendo §7, A4)
GRUPOS_CNES = {"alvo_pmme": "estoque_alvo_pre", "generalistas": "estoque_gen_pre"}
ALFA = 0.05
ROTULO_CORTE = T23.ROTULO_CORTE
EMPILHADO = T23.EMPILHADO
CONTRASTE = T23.CONTRASTE
ROTULO_FORA = "SENSIBILIDADE_FORA_DO_ADENDO (nao pedida pelo §7; relatada para leitura)"

FalhaValidacao = T23.FalhaValidacao
sha256, rotulo, _nan_none = T23.sha256, T23.rotulo, T23._nan_none
_juntar = T23._juntar
_n, _p, _ic = T23._n, T23._p, T23._ic

COLUNAS = T23.COLUNAS + [
    "covariaveis", "efeitos_fixos", "taxa_selecao_abaixo", "taxa_selecao_acima", "lee_p_aparo", "lee_lado_aparado",
    "taxa_preench_abaixo", "taxa_preench_acima", "lee_limite_inf", "lee_limite_sup", "ep_boot_limite_inf",
    "ep_boot_limite_sup", "ic_im_inf", "ic_im_sup", "n_boot", "n_boot_validos",
]

UN_10K = "vagas por 10 mil habitantes"
UN_FRAC = "fracao (x100 = p.p.)"
UN_CONT = "vagas preenchidas por municipio"

A1_OUTCOMES = [
    {"id": "A1_PREENCH_10K", "col": "preench_10k", "contagem": "preench",
     "desc": "vagas preenchidas na 1a chamada (N1) por 10 mil habitantes; U, zero fora do quadro", "no_protocolo": True},
    {"id": "A1_OFERT_10K", "col": "ofert_10k", "contagem": "ofert",
     "desc": "vagas oferecidas (imediatas + cadastro reserva) por 10 mil habitantes; U, zero fora do quadro",
     "no_protocolo": True},
    {"id": "A1_PREENCH_LIM_10K", "col": "preench_lim_10k", "contagem": "preench_lim",
     "desc": "vagas preenchidas limitadas as vagas de cada celula (contagem do A2) por 10 mil habitantes; ponte A1-A2",
     "no_protocolo": False},
]
A3_OUTCOMES = [
    {"id": "A3_PREENCHIDA", "col": "preenchida", "desc": "celula com >= 1 alocado na 1a chamada", "un": UN_FRAC,
     "no_protocolo": True},
    {"id": "A3_ALOC_POR_VAGA", "col": "aloc_por_vaga", "desc": "alocados / vagas oferecidas da celula (imediatas + CR)",
     "un": "alocados por vaga oferecida", "no_protocolo": True},
    {"id": "A3_CAND_1A_OPCAO", "col": "cand1", "desc": "candidatos de 1a opcao da celula", "un": "candidatos por celula",
     "no_protocolo": True},
    {"id": "A3_TEM_CAND_1A_OPCAO", "col": "tem_cand1", "desc": "celula com >= 1 candidato de 1a opcao (ponte com o E9)",
     "un": UN_FRAC, "no_protocolo": False},
    {"id": "A3_ALOC_POR_VAGA_LIM", "col": "aloc_por_vaga_lim",
     "desc": "min(alocados, vagas) / vagas da celula (contagem do A2)", "un": "alocados por vaga oferecida",
     "no_protocolo": False},
    {"id": "A3_PREENCHIDA_E3", "col": "preenchida_e3",
     "desc": "celula preenchida na definicao do E3 (F1.3: no ciclo 1, confirmacao ou homologacao)", "un": UN_FRAC,
     "no_protocolo": False},
]
COV_CONTAGEM = ["log_pop22", "estoque_alvo_pre", "estoque_gen_pre"]
COV_POR_HAB = ["log_pop22", "estoque_alvo_pre_10k", "estoque_gen_pre_10k"]
COV_DESC = {
    "log_pop22": "log da populacao do Censo 2022",
    "estoque_alvo_pre": "estoque CNES pre-programa de especialistas das CBO-alvo (media mensal de profissionais distintos, 202406-202506)",
    "estoque_gen_pre": "estoque CNES pre-programa de generalistas (media mensal de profissionais distintos, 202406-202506)",
    "estoque_alvo_pre_10k": "estoque CNES pre-programa das CBO-alvo por 10 mil habitantes",
    "estoque_gen_pre_10k": "estoque CNES pre-programa de generalistas por 10 mil habitantes",
}
MOTIVO_HOSPITALAR = ("numero de estabelecimentos hospitalares no CNES pre nao executado: o painel nacional do a09 "
                     "(painel_municipio_cbo_mes.parquet) e municipio x grupo de CBO x mes e nao traz estabelecimentos; "
                     "lacuna registrada, nada imputado (protocolo 48, §7, A4)")
MOTIVO_PRATICA = ("efeito fixo de tipo de pratica nao executado: o quadro da 1a chamada (outcomes_V_celula.parquet) "
                  "nao tem atributo de tipo de pratica (ele so existe na relacao nominal de ativos, depois da "
                  "alocacao); lacuna registrada, nada imputado (protocolo 48, §7, A3)")
MONOTONICIDADE = (
    "Monotonicidade de Lee (2009): no corte, a abertura muda num so sentido. Na margem intensiva, toda vaga que "
    "existiria do lado com menos vagas por habitante tambem existiria do lado com mais (as vagas a mais sao todas "
    "'marginais'); na margem extensiva, todo municipio que abriria celula do lado de menor taxa de abertura tambem "
    "abriria do outro. Sob essa suposicao, aparar a fracao p do lado de maior abertura deixa so as vagas (ou "
    "municipios) 'sempre abertas', comparaveis dos dois lados. Os limites nao valem se a faixa fizer alguns "
    "gestores abrirem mais e outros menos.")


# ---------------------------------------------------------------------------
# Linhas de saída
# ---------------------------------------------------------------------------

def nova_linha(meta: dict, esp: str, variante: str, estimador: str, *, h_mil=H, unidade: str, controle: str = "",
               no_protocolo: bool = True, rot: str = "", covariaveis: str = "", efeitos_fixos: str = "") -> dict:
    linha = T23.nova_linha(meta, esp, variante, estimador, h_mil=h_mil, unidade=unidade, controle=controle,
                           no_protocolo=no_protocolo, rot=rot)
    for c in COLUNAS:
        linha.setdefault(c, np.nan)
    linha.update({"estatuto": ESTATUTO, "natureza_dos_dados": NATUREZA, "familia": FAMILIA,
                  "covariaveis": covariaveis, "efeitos_fixos": efeitos_fixos})
    return linha


def preencher(linha: dict, res: dict | None, *, media: float | None = None) -> dict:
    return T23.preencher(linha, res, media=media)


def nao_executado(meta: dict, esp: str, variante: str, motivo: str, *, unidade: str) -> dict:
    linha = nova_linha(meta, esp, variante, "-", unidade=unidade)
    linha["status"] = "NAO_EXECUTADO"
    linha["nota"] = motivo
    return linha


def _est(a, base: str) -> str:
    return T23._est(a, base)


# ---------------------------------------------------------------------------
# Leitura e montagem (só output/; a running variable é o IVS oficial)
# ---------------------------------------------------------------------------

def ler_estoques_cnes(universo: list[str]) -> tuple[pd.DataFrame, dict]:
    """Média mensal (202406–202506) de profissionais distintos das CBO-alvo e de generalistas por município.

    Só as competências pré-programa são lidas (filtro na leitura). Município sem as 13 competências fica com
    estoque ausente (sai da linha de A4 e é contado), nunca zero. O zero do painel é o do a09: competência lida
    com sucesso e nenhum vínculo do grupo no município.
    """
    import pyarrow.parquet as pq
    t = pq.read_table(ARQ_CNES, columns=["co_ibge", "competencia", "grupo", "n_profissionais_distintos"],
                      filters=[("competencia", ">=", COMP_PRE[0]), ("competencia", "<=", COMP_PRE[1]),
                               ("grupo", "in", list(GRUPOS_CNES))]).to_pandas()
    comps = sorted(t["competencia"].unique().tolist())
    if not comps or comps[0] < COMP_PRE[0] or comps[-1] > COMP_PRE[1]:
        raise FalhaValidacao(f"competencias do CNES fora da janela pre-programa: {comps[:1]}..{comps[-1:]}")
    n_comp = len(comps)
    g = t.groupby(["co_ibge", "grupo"])["n_profissionais_distintos"].agg(["mean", "count"]).reset_index()
    g.loc[g["count"] != n_comp, "mean"] = np.nan
    wide = g.pivot(index="co_ibge", columns="grupo", values="mean").rename(columns=GRUPOS_CNES).reset_index()
    wide["co_ibge"] = wide["co_ibge"].astype(str).str.zfill(6)
    cov = pd.DataFrame({"co_ibge": universo}).merge(wide, on="co_ibge", how="left", validate="one_to_one")
    info = {"competencias": comps, "n_competencias": n_comp,
            "municipios_sem_estoque_completo": {c: int(cov[c].isna().sum()) for c in GRUPOS_CNES.values()},
            "medida": "media mensal de n_profissionais_distintos no municipio-grupo (a09)",
            "estabelecimentos_hospitalares": "ausentes do painel: lacuna registrada"}
    return cov, info


def carregar_tudo() -> dict:
    rv = E6.ler_running_variable()
    pops, conf_pop = E6.chaves_populacoes(rv)
    V, U, info = T23.carregar(rv, pops)
    u = T23.colunas_u(U, V)
    # População do Censo 2022: a coluna de U tem de ser igual ao arquivo do a06.
    p22 = pd.read_csv(ARQ_POP, dtype={"co_ibge_6d": str})
    p22["co_ibge"] = p22["co_ibge_6d"].str.zfill(6)
    m = u[["co_ibge", "populacao_2022"]].merge(p22[["co_ibge", "populacao_2022"]], on="co_ibge", how="left",
                                               suffixes=("", "_csv"), validate="one_to_one")
    dif = int(((m["populacao_2022"] - m["populacao_2022_csv"]).abs() > 0).sum())
    if dif or m["populacao_2022_csv"].isna().any():
        raise FalhaValidacao(f"populacao_2022 de U difere do Censo 2022 (a06) em {dif} municipios")
    pop = u["populacao_2022"].astype(float).where(u["populacao_2022"] > 0)
    # Células: vagas oferecidas da célula e alocados limitados a elas.
    cel = pd.read_parquet(ARQ_VC)
    cel["vic"] = cel["vagas_imediatas"].astype(float) + cel["vagas_cr"].astype(float)
    cel["aloc"] = cel["n_alocados_ch1"].astype(float)
    cel["aloc_lim"] = np.minimum(cel["aloc"], cel["vic"])
    agg = cel.groupby(["ciclo", "co_ibge"])[["vic", "aloc", "aloc_lim"]].sum().reset_index()
    conf_cel = {}
    for k, d in V.items():
        a = d[["co_ibge", "vagas_imediatas_mais_cr", "n_alocados_ch1"]].merge(
            agg[agg["ciclo"] == k], on="co_ibge", how="left", validate="one_to_one")
        if a["vic"].isna().any() or (a["vic"] != a["vagas_imediatas_mais_cr"]).any() or \
                (a["aloc"] != a["n_alocados_ch1"]).any():
            raise FalhaValidacao(f"V{k}: soma das celulas difere do municipio (vagas ou alocados)")
        conf_cel[f"V{k}"] = {"soma_celulas_igual_municipio": True,
                             "celulas_com_alocados_acima_das_vagas": int(((cel["ciclo"] == k)
                                                                          & (cel["aloc"] > cel["vic"])).sum()),
                             "alocados_cortados_pelo_limite": float((cel.loc[cel["ciclo"] == k, "aloc"]
                                                                     - cel.loc[cel["ciclo"] == k, "aloc_lim"]).sum())}
    if (cel["vic"] <= 0).any():
        raise FalhaValidacao("celula do quadro sem vaga oferecida")
    cov, info_cnes = ler_estoques_cnes(u["co_ibge"].tolist())
    cov = cov.set_index("co_ibge")
    base = pd.DataFrame({"co_ibge": u["co_ibge"], "s_mil": u["s_mil"].astype(float), "pop": pop.to_numpy()})
    base["log_pop22"] = np.log(base["pop"])
    for c in GRUPOS_CNES.values():
        base[c] = base["co_ibge"].map(cov[c]).astype(float)
        base[f"{c}_10k"] = base[c] / base["pop"] * POR_HAB
    UK, VK = {}, {}
    for k, d in V.items():
        idx = d.set_index("co_ibge")
        no_quadro = u["co_ibge"].isin(idx.index)
        lim = agg[agg["ciclo"] == k].set_index("co_ibge")["aloc_lim"]
        f = base.copy()
        f["preench"] = u[f"n_alocados_ch1_c{k}"].to_numpy(dtype=float)
        f["ofert"] = u[f"vagas_imediatas_mais_cr_c{k}"].to_numpy(dtype=float)
        # Zero estrutural do protocolo fora do quadro (sem célula: zero vaga oferecida e zero preenchida).
        f["preench_lim"] = np.where(no_quadro, u["co_ibge"].map(lim).astype(float), 0.0)
        f["tem_celula"] = u[f"f0_1_tem_celula_c{k}"].astype(float).to_numpy()
        if ((f["tem_celula"] == 1) != (f["ofert"] > 0)).any() or (no_quadro.to_numpy() != (f["tem_celula"] == 1)).any():
            raise FalhaValidacao(f"U ciclo {k}: ter celula, ter vaga e estar no quadro divergem")
        # Fração só existe onde há vaga (seleção de Lee): fora do quadro fica ausente, nunca zero.
        f["frac_lim"] = np.where(f["ofert"] > 0, f["preench_lim"] / np.where(f["ofert"] > 0, f["ofert"], 1.0), np.nan)
        for c in ("preench", "ofert", "preench_lim"):
            f[f"{c}_10k"] = f[c] / f["pop"] * POR_HAB
        UK[k] = f
        v = d.copy()
        v["preench"] = v["n_alocados_ch1"].astype(float)
        v["ofert"] = v["vagas_imediatas_mais_cr"].astype(float)
        v["preench_lim"] = v["co_ibge"].map(lim).astype(float)
        v["frac_lim"] = v["preench_lim"] / v["ofert"]
        for c in ["log_pop22", "pop"] + list(GRUPOS_CNES.values()):
            v[c] = v["co_ibge"].map(base.set_index("co_ibge")[c]).astype(float)
        VK[k] = v
    # Células com o IVS oficial do município (chave do V_k); célula de município sem IVS sai e é contada.
    CK, fora_cel = {}, {}
    for k in sorted(V):
        c = cel[cel["ciclo"] == k].merge(pops[f"V{k}"], on="co_ibge", how="left", validate="many_to_one")
        fora_cel[f"V{k}"] = int(c["s_mil"].isna().sum())
        c = c[c["s_mil"].notna()].copy()
        if (E6.s_mil_de_ivs(c["ivs_2010_oficial"]) != c["s_mil"]).any():
            raise FalhaValidacao(f"V{k}: IVS da celula difere do IVS oficial do municipio")
        c["preenchida"] = (c["aloc"] >= 1).astype(float)
        c["aloc_por_vaga"] = c["aloc"] / c["vic"]
        c["aloc_por_vaga_lim"] = c["aloc_lim"] / c["vic"]
        c["cand1"] = c["n_cand_1a_opcao"].astype(float)
        c["tem_cand1"] = (c["n_cand_1a_opcao"] > 0).astype(float)
        c["preenchida_e3"] = c["f1_3_preenchida_ch1"].astype(float)
        c["fe_curso_ciclo"] = f"c{k}_curso" + c["cod_curso"].astype(int).astype(str).str.zfill(2)
        c["tipo_vaga_imediata"] = c["com_vagas_imediatas"].astype(float)
        CK[k] = c.reset_index(drop=True)
    atributos = {
        "existem": {"curso": "cod_curso", "tipo_de_vaga": "com_vagas_imediatas (1 = tem vaga imediata; 0 = so cadastro "
                                                         "reserva; igual a situacao_vagas)",
                    "regiao": "regiao (nao pedida pelo §7)"},
        "ausentes": {"tipo_de_pratica": MOTIVO_PRATICA},
        "usados_como_efeito_fixo": ["curso x ciclo (fe_curso_ciclo)", "tipo de vaga (tipo_vaga_imediata)"],
        "conferencia_tipo_vaga": bool(((cel["com_vagas_imediatas"] == 1)
                                       == (cel["situacao_vagas"] == "COM VAGAS IMEDIATAS")).all()),
    }
    if not atributos["conferencia_tipo_vaga"]:
        raise FalhaValidacao("com_vagas_imediatas difere de situacao_vagas")
    return {"rv": rv, "pops": pops, "conf_pop": conf_pop, "V": V, "U": U, "info": info, "UK": UK, "VK": VK,
            "CK": CK, "cel": cel, "conf_cel": conf_cel, "fora_cel": fora_cel, "cnes": info_cnes,
            "atributos": atributos, "base": base}


# ---------------------------------------------------------------------------
# Grade de amostras (mesma convenção do script 23)
# ---------------------------------------------------------------------------

def grade(frames: dict[int, pd.DataFrame], rot, ks=CICLOS) -> list[tuple[dict, "T23.Amostra"]]:
    """Por ciclo: cada corte e cortes empilhados; ciclos empilhados: por corte (grupo = ciclo) e tudo (ciclo × corte)."""
    out = []
    for k in ks:
        d = frames[k]
        for c in CORTES:
            out.append(({"populacao": rot(k), "ciclo": str(k), "corte": ROTULO_CORTE[c]},
                        T23.montar_amostra([(d, c, str(c))], empilhada=False)))
        out.append(({"populacao": rot(k), "ciclo": str(k), "corte": EMPILHADO},
                    T23.montar_amostra([(d, c, str(c)) for c in CORTES], empilhada=True)))
    if len(ks) > 1:
        ck = "+".join(str(k) for k in ks)
        for c in CORTES:
            out.append(({"populacao": rot(ks), "ciclo": ck, "corte": ROTULO_CORTE[c]},
                        T23.montar_amostra([(frames[k], c, f"c{k}") for k in ks], empilhada=True)))
        out.append(({"populacao": rot(ks), "ciclo": ck, "corte": EMPILHADO},
                    T23.montar_amostra([(frames[k], c, f"c{k}_{c}") for k in ks for c in CORTES], empilhada=True)))
    return out


def rot_u(k) -> str:
    return "U"


def rot_v(k) -> str:
    return "+".join(f"V{x}" for x in k) if isinstance(k, (list, tuple)) else f"V{k}"


def rot_c(k) -> str:
    return rot_v(k) + " (celulas)"


# ---------------------------------------------------------------------------
# Regressão rápida para o bootstrap (mesmo modelo da rdd_lib; conferida contra ela com pesos unitários)
# ---------------------------------------------------------------------------

class Desenho:
    """Local linear (um grupo) ou empilhado (intercepto e inclinações por grupo × lado, salto comum), só na janela.

    `ajustar` resolve o MQP com peso = kernel × peso extra × multiplicidade do município no bootstrap e devolve o
    salto, os interceptos do lado de baixo por grupo e os pesos omega_g de Cattaneo, Keele, Titiunik e
    Vazquez-Bare (2016), como `rd_empilhado`. Sem `m`, reproduz a rdd_lib (conferido em `conferir_desenho`).
    """

    def __init__(self, a, mapa_mun: dict[str, int], h=H):
        s = L.normalizar_s_mil(a.s)
        x_mil = s - a.c
        k = L.pesos_kernel(x_mil, h)
        j = k > 0
        self.idx = np.flatnonzero(j)
        self.k, self.s, self.x_mil = k[j], s[j], x_mil[j]
        self.t = (self.x_mil > 0).astype(float)
        x = self.x_mil / 1000.0
        self.g = a.g[j]
        self.grupos = sorted(np.unique(self.g).tolist())
        cols, self.i_const = [], {}
        for gl in self.grupos:
            ind = (self.g == gl).astype(float)
            self.i_const[gl] = len(cols)
            cols.extend([ind, ind * x, ind * self.t * x])
        cols.append(self.t)
        self.X = np.column_stack(cols)
        self.i_T = self.X.shape[1] - 1
        self.mun = np.array([mapa_mun[c] for c in a.cl[j]], dtype=int)
        self.mascara_g = {gl: self.g == gl for gl in self.grupos}

    def janela(self, v) -> np.ndarray:
        return np.asarray(v, dtype=float)[self.idx]

    def ajustar_janela(self, y: np.ndarray, peso: np.ndarray | None = None, m: np.ndarray | None = None) -> dict | None:
        w = self.k.copy()
        if peso is not None:
            w = w * peso
        if m is not None:
            w = w * m[self.mun]
        ok = np.isfinite(w) & (w > 0) & np.isfinite(y)
        for gl, mg in self.mascara_g.items():
            for lado in (0.0, 1.0):
                if np.unique(self.s[ok & mg & (self.t == lado)]).size < 2:
                    return None
        X, ww, yy = self.X[ok], w[ok], y[ok]
        A = X.T @ (X * ww[:, None])
        try:
            beta = np.linalg.solve(A, X.T @ (ww * yy))
            e = np.zeros(A.shape[0])
            e[self.i_T] = 1.0
            aT = np.linalg.solve(A, e)
        except np.linalg.LinAlgError:
            return None
        aw = (X @ aT) * ww
        tt, gg = self.t[ok], self.g[ok]
        omega = {gl: float(np.sum(aw[gg == gl] * tt[gg == gl])) for gl in self.grupos}
        return {"tau": float(beta[self.i_T]), "const": {gl: float(beta[i]) for gl, i in self.i_const.items()},
                "omega": omega}

    def ajustar(self, y, peso=None, m=None) -> dict | None:
        return self.ajustar_janela(self.janela(y), None if peso is None else self.janela(peso), m)


def media_lado_baixo(r: dict, omega: dict) -> float:
    return float(sum(omega[g] * r["const"][g] for g in omega))


def interceptos_lib(r: dict, empilhada: bool) -> tuple[dict, dict]:
    """Interceptos do lado de baixo e pesos omega de um resultado da rdd_lib com `detalhes=True`."""
    coef = r["_detalhes"]["fit"]["coef"]
    if not empilhada:
        return {"_": float(coef["const"])}, {"_": 1.0}
    const = {k[len("const["):-1]: float(v) for k, v in coef.items() if k.startswith("const[")}
    return const, dict(r["pesos_grupos"])


def conferir_desenho(D: Desenho, a, y, peso, ref: dict, tol: float = 1e-8) -> None:
    """O MQP rápido (multiplicidade 1) tem de reproduzir o salto, os interceptos e os pesos da rdd_lib."""
    meu = D.ajustar(y, peso)
    if meu is None or not np.isfinite(ref["tau"]):
        if meu is None and not np.isfinite(ref["tau"]):
            return
        raise FalhaValidacao(f"desenho rapido e rdd_lib divergem na estimabilidade: {ref.get('nota')}")
    const_r, om_r = interceptos_lib(ref, a.empilhada)
    pares = [(meu["tau"], ref["tau"])]
    if a.empilhada:
        pares += [(meu["const"][g], const_r[g]) for g in const_r] + [(meu["omega"][g], om_r[g]) for g in om_r]
    else:
        pares += [(next(iter(meu["const"].values())), const_r["_"])]
    for x, z in pares:
        if not abs(x - z) <= tol * max(1.0, abs(z)):
            raise FalhaValidacao(f"desenho rapido diverge da rdd_lib: {x} vs {z}")


# ---------------------------------------------------------------------------
# Limites de Lee
# ---------------------------------------------------------------------------

def limites_binario(f: float, p: float) -> tuple[float, float]:
    """Protocolo 48, §7 (A2): taxa de preenchimento das vagas 'sempre abertas' do lado aparado.

    inferior = max(0, (f − p)/(1 − p)); superior = min(1, f/(1 − p)).
    """
    if not (np.isfinite(f) and np.isfinite(p)) or p < 0 or p >= 1:
        return float("nan"), float("nan")
    return max(0.0, (f - p) / (1.0 - p)), min(1.0, f / (1.0 - p))


def lee_intensivo(s0: float, s1: float, f0: float, f1: float) -> dict:
    """Limites de Lee no nível da vaga. s = vagas oferecidas por habitante no corte (abaixo, acima); f = taxa de
    preenchimento no corte. Apara p = (s_maior − s_menor)/s_maior do lado com mais vagas por habitante.
    Salto = acima − abaixo."""
    res = {"p": float("nan"), "lado": None, "inf": float("nan"), "sup": float("nan"), "ingenuo": f1 - f0, "nota": ""}
    if not all(np.isfinite(v) for v in (s0, s1, f0, f1)):
        res["nota"] = "taxa de selecao ou de preenchimento indefinida"
        return res
    if not (s0 > 0 and s1 > 0):
        res["nota"] = "taxa de selecao estimada nao positiva em algum lado: limites indefinidos"
        return res
    if s1 >= s0:
        p = (s1 - s0) / s1
        lo, hi = limites_binario(f1, p)
        res.update({"p": p, "lado": "acima", "inf": lo - f0, "sup": hi - f0})
    else:
        p = (s0 - s1) / s0
        lo, hi = limites_binario(f0, p)
        res.update({"p": p, "lado": "abaixo", "inf": f1 - hi, "sup": f1 - lo})
    if not (0 <= f0 <= 1 and 0 <= f1 <= 1):
        res["nota"] = "taxa de preenchimento estimada fora de [0, 1] em algum lado (extrapolacao do local linear)"
    return res


def lee_intensivo_desenho(DU: Desenho, DV: Desenho, ys: np.ndarray, ps: np.ndarray | None, yf: np.ndarray,
                          pf: np.ndarray, m: np.ndarray | None) -> dict | None:
    """s no U (vagas oferecidas por 10 mil hab.), f no V (fração limitada ponderada pelas vagas); interceptos do
    empilhado agregados com os pesos omega da regressão de s (os mesmos para s e f)."""
    rs = DU.ajustar_janela(ys, ps, m)
    rf = DV.ajustar_janela(yf, pf, m)
    if rs is None or rf is None or set(rs["const"]) != set(rf["const"]):
        return None
    s0 = media_lado_baixo(rs, rs["omega"])
    f0 = media_lado_baixo(rf, rs["omega"])
    out = lee_intensivo(s0, s0 + rs["tau"], f0, f0 + rf["tau"])
    out.update({"s0": s0, "s1": s0 + rs["tau"], "f0": f0, "f1": f0 + rf["tau"]})
    return out


def lee_extensivo_desenho(D: Desenho, sel: np.ndarray, y: np.ndarray, m: np.ndarray | None) -> dict | None:
    """Lee na margem extensiva, mesmo algoritmo de `rdd_lib.limites_lee_rd` (seleção local linear, aparo da massa de
    kernel pelo topo e pela base do lado de maior seleção, local linear nos selecionados); no empilhado, p0 = soma
    omega_g x intercepto_g e o aparo é feito dentro de cada grupo com a mesma fração. Janela: arrays já cortados."""
    rs = D.ajustar_janela(sel, None, m)
    if rs is None:
        return None
    p0 = media_lado_baixo(rs, rs["omega"])
    p1 = p0 + rs["tau"]
    if not (p0 > 0 and p1 > 0):
        return None
    acima = p1 >= p0
    q = (p1 - p0) / p1 if acima else (p0 - p1) / p0
    ok = (sel == 1) & np.isfinite(y)
    wk = D.k * (m[D.mun] if m is not None else 1.0)
    lado_t = 1.0 if acima else 0.0
    ingenuo = D.ajustar_janela(np.where(ok, y, np.nan), None, m)
    taus = []
    for de_cima in (True, False):
        mult = np.ones(len(y))
        for gl, mg in D.mascara_g.items():
            lado = ok & (wk > 0) & mg & (D.t == lado_t)
            if lado.any():
                mult[lado] = L._multiplicador_aparo(y[lado], wk[lado], q, de_cima)
        r = D.ajustar_janela(np.where(ok, y, np.nan), mult, m)
        if r is None:
            return None
        taus.append(r["tau"])
    if ingenuo is None:
        return None
    return {"p0": p0, "p1": p1, "q": q, "lado": "acima" if acima else "abaixo", "inf": min(taus), "sup": max(taus),
            "ingenuo": ingenuo["tau"]}


def ic_imbens_manski(inf: float, sup: float, ep_inf: float, ep_sup: float, alfa: float = ALFA) -> tuple[float, float]:
    """IC de Imbens e Manski (2004) para o parâmetro identificado no intervalo [inf, sup].

    c resolve Phi(c + Delta / max(ep)) − Phi(−c) = 1 − alfa, Delta = sup − inf; IC = [inf − c ep_inf, sup + c ep_sup].
    """
    if not all(np.isfinite(v) for v in (inf, sup, ep_inf, ep_sup)):
        return float("nan"), float("nan")
    sig = max(ep_inf, ep_sup)
    if sig <= 0:
        return inf, sup
    delta = max(sup - inf, 0.0) / sig
    c = optimize.brentq(lambda c: stats.norm.cdf(c + delta) - stats.norm.cdf(-c) - (1 - alfa), 0.0, 10.0)
    return inf - c * ep_inf, sup + c * ep_sup


# ---------------------------------------------------------------------------
# A1
# ---------------------------------------------------------------------------

def a1_linhas(meta: dict, a) -> list[dict]:
    linhas = []
    logpop = a.col("log_pop22")
    for o in A1_OUTCOMES:
        mo = {**meta, "outcome_id": o["id"], "outcome": o["col"], "descricao_outcome": o["desc"]}
        rot = "" if o["no_protocolo"] else ROTULO_FORA
        y = a.col(o["col"])
        for h in (H,) + tuple(H_SENS):
            var = "principal" if h == H else f"h={h / 1000:.3f}"
            linhas.append(preencher(nova_linha(mo, "A1", var, _est(a, "sem controle; U, zero estrutural fora do quadro"),
                                               h_mil=h, unidade=UN_10K, no_protocolo=o["no_protocolo"], rot=rot),
                                    T23.ajustar(a, y, h)))
        cnt = a.col(o["contagem"])
        rp = T23.poisson(a, cnt, H, offset=logpop)
        if not a.empilhada:
            T23.conferir_poisson_lib(a, cnt, logpop, rp)
        linhas.append(preencher(nova_linha(mo, "A1", "poisson_offset_log_populacao",
                                           "Poisson local (IRLS) da contagem com offset log(populacao 2022), kernel "
                                           "triangular" + ("; CR1 por municipio" if a.empilhada else "; EP HC1"),
                                           unidade=E6.UNIDADE_LOG, no_protocolo=o["no_protocolo"], rot=rot), rp))
    return linhas


# ---------------------------------------------------------------------------
# A2
# ---------------------------------------------------------------------------

def a2_pontual(meta: dict, aU, aV, mapa: dict) -> tuple[list[dict], dict]:
    """Estimativas pontuais com a rdd_lib (conferidas contra o desenho rápido) e os desenhos do bootstrap."""
    DU, DV = Desenho(aU, mapa), Desenho(aV, mapa)
    ys, pop = aU.col("ofert_10k"), aU.col("pop")
    yf, pf = aV.col("frac_lim"), aV.col("ofert")
    sel, ye = aU.col("tem_celula"), aU.col("frac_lim")
    rs = T23.ajustar(aU, ys, H)
    rsp = T23.ajustar(aU, ys, H, peso=pop)
    rf = T23.ajustar(aV, yf, H, peso=pf)
    re_ = T23.ajustar(aU, ye, H)
    conferir_desenho(DU, aU, ys, None, rs)
    conferir_desenho(DU, aU, ys, pop, rsp)
    conferir_desenho(DV, aV, yf, pf, rf)
    conferir_desenho(DU, aU, ye, None, re_)
    # Pontual com o algoritmo do bootstrap (multiplicidade 1); com um corte, extensivo = rdd_lib.limites_lee_rd.
    args = {"int": (DU.janela(ys), None, DV.janela(yf), DV.janela(pf)),
            "int_pop": (DU.janela(ys), DU.janela(pop), DV.janela(yf), DV.janela(pf)),
            "ext": (DU.janela(sel), DU.janela(ye))}
    pont = {"int": lee_intensivo_desenho(DU, DV, *args["int"], None),
            "int_pop": lee_intensivo_desenho(DU, DV, *args["int_pop"], None),
            "ext": lee_extensivo_desenho(DU, *args["ext"], None)}
    conf_lee = None
    if not aU.empilhada:
        ref = L.limites_lee_rd(aU.s, ye, sel, aU.corte_unico, H)
        meu = pont["ext"]
        if meu is None:
            if np.isfinite(ref["tau_inf"]):
                raise FalhaValidacao(f"Lee extensivo indefinido aqui e definido na rdd_lib em {meta}")
        else:
            for x, z in ((meu["inf"], ref["tau_inf"]), (meu["sup"], ref["tau_sup"]), (meu["q"], ref["q_aparo"]),
                         (meu["p0"], ref["p0_selecao"]), (meu["p1"], ref["p1_selecao"]),
                         (meu["ingenuo"], ref["tau_selecionados"])):
                if not abs(x - z) <= 1e-8 * max(1.0, abs(z)):
                    raise FalhaValidacao(f"Lee extensivo diverge de rdd_lib.limites_lee_rd em {meta}: {x} vs {z}")
            conf_lee = True
    return [], {"DU": DU, "DV": DV, "args": args, "pont": pont, "rs": rs, "rsp": rsp, "rf": rf, "re": re_,
                "conf_lee_rdd_lib": conf_lee}


def bootstrap_a2(estado: list[dict], n_mun: int, n_boot: int = N_BOOT, semente=SEMENTE_BOOT, log=print) -> None:
    """Bootstrap de municípios (com reposição; multiplicidade como peso de frequência) para os limites de Lee."""
    rng = np.random.default_rng(list(semente))
    for e in estado:
        e["boot"] = {k: {"inf": [], "sup": []} for k in ("int", "int_pop", "ext")}
    for b in range(n_boot):
        m = np.bincount(rng.integers(0, n_mun, n_mun), minlength=n_mun).astype(float)
        for e in estado:
            DU, DV, ar = e["DU"], e["DV"], e["args"]
            for k, r in (("int", lee_intensivo_desenho(DU, DV, *ar["int"], m)),
                         ("int_pop", lee_intensivo_desenho(DU, DV, *ar["int_pop"], m)),
                         ("ext", lee_extensivo_desenho(DU, *ar["ext"], m))):
                if r is not None and np.isfinite(r["inf"]) and np.isfinite(r["sup"]):
                    e["boot"][k]["inf"].append(r["inf"])
                    e["boot"][k]["sup"].append(r["sup"])
        if (b + 1) % 200 == 0:
            log(f"  bootstrap A2: {b + 1}/{n_boot}")


def a2_linhas(meta: dict, e: dict, n_boot: int = N_BOOT) -> list[dict]:
    linhas = []
    aU = e["aU"]
    defs = [
        ("int", "A2_INTENSIVA", "margem_intensiva_vaga", True, "", e["rf"],
         "limites de Lee no nivel da vaga: s = vagas oferecidas por 10 mil hab. no corte (U, local linear, sem peso); "
         "f = taxa de preenchimento no corte (V, fracao limitada ponderada pelas vagas); aparo p no lado com mais vagas "
         "por habitante; IC de Imbens-Manski com bootstrap de municipios",
         "vagas preenchidas limitadas / vagas oferecidas (nivel da vaga)"),
        ("int_pop", "A2_INTENSIVA", "margem_intensiva_vaga_selecao_ponderada_pela_populacao", False, ROTULO_FORA, e["rf"],
         "como a margem intensiva, com s estimado com peso = populacao (vagas por habitante agregadas no corte)",
         "vagas preenchidas limitadas / vagas oferecidas (nivel da vaga)"),
        ("ext", "A2_EXTENSIVA", "margem_extensiva_abertura", True, "", e["re"],
         "limites de Lee na margem extensiva: selecao = ter >= 1 vaga no quadro (U); outcome = vagas preenchidas "
         "limitadas / oferecidas do municipio; aparo pelo topo e pela base (rdd_lib.limites_lee_rd; no empilhado, "
         "aparo dentro de cada grupo); IC de Imbens-Manski com bootstrap de municipios",
         "vagas preenchidas limitadas / oferecidas do municipio aberto"),
    ]
    for chave, oid, var, no_prot, rot, ingenuo, est, desc in defs:
        mo = {**meta, "outcome_id": oid, "outcome": "frac_lim", "descricao_outcome": desc}
        ln = preencher(nova_linha(mo, "A2", var, est + (" (empilhado: interceptos agregados com os pesos omega da "
                                                        "regressao de selecao)" if aU.empilhada else ""),
                                  unidade=UN_FRAC, no_protocolo=no_prot, rot=rot), ingenuo)
        ln["n_abaixo"], ln["n_acima"] = e["rs"]["n_abaixo"], e["rs"]["n_acima"]
        r = e["pont"][chave]
        bt = e["boot"][chave]
        ln["n_boot"], ln["n_boot_validos"] = n_boot, len(bt["inf"])
        if r is None:
            ln["nota"] = _juntar(ln["nota"], "limites de Lee indefinidos na amostra (taxa de selecao nao positiva ou "
                                             "suporte insuficiente)")
            linhas.append(ln)
            continue
        if chave == "ext":
            ln.update({"taxa_selecao_abaixo": r["p0"], "taxa_selecao_acima": r["p1"], "lee_p_aparo": r["q"]})
        else:
            ln.update({"taxa_selecao_abaixo": r["s0"], "taxa_selecao_acima": r["s1"], "lee_p_aparo": r["p"],
                       "taxa_preench_abaixo": r["f0"], "taxa_preench_acima": r["f1"]})
            if abs(r["ingenuo"] - float(ln["tau"])) > 1e-8:
                raise FalhaValidacao(f"salto ingenuo do Lee difere da regressao de f em {meta}")
        ln.update({"lee_lado_aparado": r["lado"], "lee_limite_inf": r["inf"], "lee_limite_sup": r["sup"]})
        if len(bt["inf"]) >= 2:
            ei, es = float(np.std(bt["inf"], ddof=1)), float(np.std(bt["sup"], ddof=1))
            ln["ep_boot_limite_inf"], ln["ep_boot_limite_sup"] = ei, es
            ln["ic_im_inf"], ln["ic_im_sup"] = ic_imbens_manski(r["inf"], r["sup"], ei, es)
        notas = [r.get("nota", ""), f"bootstrap de municipios: {len(bt['inf'])} de {n_boot} reamostras validas, "
                                    f"semente {list(SEMENTE_BOOT)}"]
        if chave == "ext" and not (r["inf"] - 1e-12 <= float(ln["tau"]) <= r["sup"] + 1e-12):
            notas.append("salto ingenuo fora dos limites: com reta local, aparar pelo quantil do meio-janela muda "
                         "tambem a inclinacao, e os limites nao contem o ingenuo por construcao (aproximacao (i) de "
                         "rdd_lib.limites_lee_rd)")
        if len(bt["inf"]) < 0.9 * n_boot:
            notas.append("menos de 90% das reamostras validas: EP dos limites menos confiavel")
        ln["nota"] = _juntar(ln["nota"], *notas)
        linhas.append(ln)
    return linhas


# ---------------------------------------------------------------------------
# A3 (célula)
# ---------------------------------------------------------------------------

def ajustar_celula(a, y: np.ndarray, h, *, fe: bool, tipo: bool) -> dict:
    r = L.rd_empilhado(a.s, y, a.c, grupo=a.g, h_mil=h, cluster=a.cl, ids_unidade=a.cl,
                       efeitos_fixos=a.d["fe_curso_ciclo"].to_numpy() if fe else None,
                       Z=a.col("tipo_vaga_imediata") if tipo else None,
                       nomes_z=["tipo_vaga_imediata"] if tipo else None, detalhes=True)
    r["media_abaixo"] = float("nan")
    if "_detalhes" in r:
        d = r["_detalhes"]
        ab = d["usa"] & (d["x_mil"] <= 0)
        r["media_abaixo"] = float(np.mean(y[ab])) if ab.any() else float("nan")
    return r


def a3_linhas(meta: dict, a, *, principal_amostra: bool) -> list[dict]:
    linhas = []
    est = ("celula do quadro; RDD no IVS do municipio; intercepto e inclinacoes por grupo x lado, salto comum; "
           "CR1 por municipio")
    variantes = [("principal", True, True, H), ("so_curso_x_ciclo", True, False, H), ("sem_efeitos_fixos", False, False, H)]
    variantes += [(f"h={h / 1000:.3f}", True, True, h) for h in H_SENS]
    for o in A3_OUTCOMES:
        mo = {**meta, "outcome_id": o["id"], "outcome": o["col"], "descricao_outcome": o["desc"]}
        y = a.col(o["col"])
        rot = "" if o["no_protocolo"] else ROTULO_FORA
        for var, fe, tipo, h in variantes:
            efs = ", ".join(x for x, ok in (("curso x ciclo", fe), ("tipo de vaga (imediata ou so CR)", tipo)) if ok)
            ln = preencher(nova_linha(mo, "A3", var, est + (f"; efeitos fixos: {efs}" if efs else "; sem efeitos fixos"),
                                      h_mil=h, unidade=o["un"], no_protocolo=o["no_protocolo"], rot=rot,
                                      efeitos_fixos=efs), ajustar_celula(a, y, h, fe=fe, tipo=tipo))
            ln["nota"] = _juntar(ln["nota"], f"{int(ln['n_obs']) if pd.notna(ln['n_obs']) else 0} celulas; n abaixo/acima "
                                             "= municipios")
            linhas.append(ln)
        if principal_amostra:
            linhas.append(nao_executado(mo, "A3", "efeito_fixo_tipo_pratica", MOTIVO_PRATICA, unidade=o["un"]))
    return linhas


# ---------------------------------------------------------------------------
# A4 (covariáveis pré-determinadas)
# ---------------------------------------------------------------------------

def ajustar_cov(a, y: np.ndarray, h, covs: list[str], *, unico: bool = False) -> dict:
    """Covariáveis lineares comuns aos dois lados (CCFT 2019), centradas na média de kernel da janela; no empilhado,
    um coeficiente por grupo (ciclo × corte), como o controle do script 23 (`unico=True`: um só)."""
    k = T23._kern(a, h)
    vals = {c: a.col(c) for c in covs}
    ok = (k > 0) & np.isfinite(y)
    for v in vals.values():
        ok &= np.isfinite(v)
    cols, nomes = [], []
    grupos = [T23.COEF_UNICO] if (unico or not a.empilhada) else sorted(np.unique(a.g).tolist())
    for c, v in vals.items():
        for gl in grupos:
            m = np.ones(len(y), dtype=bool) if gl == T23.COEF_UNICO else a.g == gl
            okg = ok & m
            vb = float(np.sum(k[okg] * v[okg]) / np.sum(k[okg])) if okg.any() else float("nan")
            cols.append(np.where(m, v - vb, 0.0))
            nomes.append(f"{c}[{gl}]" if a.empilhada and gl != T23.COEF_UNICO else c)
    Z = np.column_stack(cols)
    if a.empilhada:
        r = L.rd_empilhado(a.s, y, a.c, grupo=a.g, h_mil=h, cluster=a.cl, ids_unidade=a.cl, Z=Z, nomes_z=nomes,
                           detalhes=True)
    else:
        r = L.rd_local_linear(a.s, y, a.corte_unico, h, Z=Z, nomes_z=nomes, detalhes=True)
    r["media_abaixo"] = float("nan")
    if "_detalhes" in r:
        d = r["_detalhes"]
        ab = d["usa"] & (d["x_mil"] <= 0)
        r["media_abaixo"] = float(np.mean(y[ab])) if ab.any() else float("nan")
    r["n_descartadas_covariavel_ausente"] = int(((k > 0) & np.isfinite(y) & ~ok).sum())
    return r


def a4_linhas(meta: dict, a, specs: list[tuple[str, str, str, str, list[str]]]) -> list[dict]:
    linhas = []
    for oid, col, desc, un, covs in specs:
        mo = {**meta, "outcome_id": oid, "outcome": col, "descricao_outcome": desc}
        y = a.col(col)
        okc = np.ones(len(y), dtype=bool)
        for c in covs:
            okc &= np.isfinite(a.col(c))
        sub = a.subconjunto(okc)
        lb = preencher(nova_linha(mo, "A4", "sem_covariaveis_mesma_amostra",
                                  _est(a, "sem covariaveis, na amostra com covariaveis completas"), unidade=un),
                       T23.ajustar(sub, sub.col(col), H))
        lb["nota"] = _juntar(lb["nota"], f"{int((~okc).sum())} linhas sem covariavel completa fora da amostra")
        linhas.append(lb)
        rc = ajustar_cov(a, y, H, covs)
        lc = preencher(nova_linha(mo, "A4", "com_covariaveis",
                                  _est(a, "covariaveis pre-determinadas lineares, comuns aos dois lados (CCFT 2019)"
                                       + ("; um coeficiente por grupo ciclo x corte" if a.empilhada else "")),
                                  unidade=un, covariaveis=";".join(covs), controle=";".join(covs)), rc)
        lc["n_descartadas_controle_ausente"] = rc["n_descartadas_covariavel_ausente"]
        linhas.append(lc)
        if a.empilhada:
            ru = ajustar_cov(a, y, H, covs, unico=True)
            lu = preencher(nova_linha(mo, "A4", "com_covariaveis_coeficiente_unico",
                                      _est(a, "covariaveis pre-determinadas, um so coeficiente para todos os grupos"),
                                      unidade=un, covariaveis=";".join(covs), controle=";".join(covs),
                                      no_protocolo=False, rot=ROTULO_FORA), ru)
            lu["n_descartadas_controle_ausente"] = ru["n_descartadas_covariavel_ausente"]
            linhas.append(lu)
    return linhas


def a4_balanco(meta: dict, a, covs: list[str]) -> list[dict]:
    out = []
    for c in covs:
        mo = {**meta, "outcome_id": f"COV_{c}", "outcome": c, "descricao_outcome": COV_DESC[c]}
        out.append(preencher(nova_linha(mo, "A4", "covariavel_como_outcome", _est(a, "covariavel pre-determinada como "
                                                                                     "outcome (balanco)"),
                                        unidade=c), T23.ajustar(a, a.col(c), H)))
    return out


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def estimar_tudo(dados: dict, *, n_boot: int = N_BOOT, log=print) -> tuple[pd.DataFrame, dict]:
    UK, VK, CK = dados["UK"], dados["VK"], dados["CK"]
    universo = sorted(UK[CICLOS[0]]["co_ibge"].tolist())
    mapa = {c: i for i, c in enumerate(universo)}
    linhas: list[dict] = []
    gU, gV = grade(UK, rot_u), grade(VK, rot_v)
    # A1.
    for meta, a in gU:
        linhas.extend(a1_linhas(meta, a))
    log(f"  A1: {len(linhas)} linhas")
    # A2.
    estado, conf_lee = [], []
    for (mu, aU), (mv, aV) in zip(gU, gV):
        if (mu["ciclo"], mu["corte"]) != (mv["ciclo"], mv["corte"]):
            raise FalhaValidacao("grades de U e V desalinhadas")
        _, e = a2_pontual(mu, aU, aV, mapa)
        e.update({"meta": mu, "aU": aU})
        estado.append(e)
        if e["conf_lee_rdd_lib"]:
            conf_lee.append(f"{mu['ciclo']}|{mu['corte']}")
    bootstrap_a2(estado, len(universo), n_boot=n_boot, log=log)
    for e in estado:
        linhas.extend(a2_linhas(e["meta"], e, n_boot=n_boot))
    log(f"  A2: {len(linhas)} linhas")
    # A3.
    principal_c = (rot_c(CICLOS), "+".join(str(k) for k in CICLOS), EMPILHADO)
    for meta, a in grade(CK, rot_c):
        linhas.extend(a3_linhas(meta, a, principal_amostra=(meta["populacao"], meta["ciclo"], meta["corte"]) == principal_c))
    log(f"  A3: {len(linhas)} linhas")
    # A4.
    specs_v = [("N1", "preench", "S-b do doc 49: N1 sem controle das vagas oferecidas (V)", UN_CONT, COV_CONTAGEM)]
    specs_u = [(o["id"], o["col"], o["desc"], UN_10K, COV_POR_HAB) for o in A1_OUTCOMES if o["no_protocolo"]]
    for meta, a in gV:
        linhas.extend(a4_linhas(meta, a, specs_v))
    for meta, a in gU:
        linhas.extend(a4_linhas(meta, a, specs_u))
    for c in CORTES:
        meta = {"populacao": "U", "ciclo": "-", "corte": ROTULO_CORTE[c]}
        linhas.extend(a4_balanco(meta, T23.montar_amostra([(UK[CICLOS[0]], c, str(c))], empilhada=False),
                                 COV_CONTAGEM + COV_POR_HAB[1:]))
    linhas.extend(a4_balanco({"populacao": "U", "ciclo": "-", "corte": EMPILHADO},
                             T23.montar_amostra([(UK[CICLOS[0]], c, str(c)) for c in CORTES], empilhada=True),
                             COV_CONTAGEM + COV_POR_HAB[1:]))
    for meta, a in gV:
        linhas.extend(a4_balanco(meta, a, COV_CONTAGEM))
    principal_v = {"populacao": rot_v(CICLOS), "ciclo": "+".join(str(k) for k in CICLOS), "corte": EMPILHADO}
    for oid, col, desc, un, _ in specs_v + specs_u:
        linhas.append(nao_executado({**principal_v, "outcome_id": oid, "outcome": col, "descricao_outcome": desc}
                                    if oid == "N1" else {**principal_v, "populacao": "U", "outcome_id": oid,
                                                         "outcome": col, "descricao_outcome": desc},
                                    "A4", "covariavel_estabelecimentos_hospitalares", MOTIVO_HOSPITALAR, unidade=un))
    log(f"  A4: {len(linhas)} linhas")
    est = pd.DataFrame(linhas)[COLUNAS]
    est["entra_holm"] = False
    est["p_holm"] = np.nan
    extras = {"conf_lee_rdd_lib": conf_lee, "n_universo_bootstrap": len(universo),
              "boot_validos": {f"{e['meta']['ciclo']}|{e['meta']['corte']}": {k: len(v["inf"]) for k, v in e["boot"].items()}
                               for e in estado}}
    return est, extras


# ---------------------------------------------------------------------------
# Figuras
# ---------------------------------------------------------------------------

def _fmt(v, casas=2, sinal=True) -> str:
    return T23._fmt(v, casas, sinal)


def _titulo(r: dict, unidade: str, casas: int = 2, pp: bool = False) -> str:
    f = 100.0 if pp else 1.0
    return (f"salto = {_fmt(r['tau'] * f, casas)} {unidade}  [IC 95%: {_fmt(r['ic95_inf'] * f, casas)}; "
            f"{_fmt(r['ic95_sup'] * f, casas)}],  p = {_fmt(r['p_valor'], 3, False)}")


def curva_empilhada_fe(r: dict, a) -> tuple[dict, np.ndarray]:
    """Como `T23.curva_empilhada`, somando aos interceptos a média (peso de kernel) das colunas de efeito fixo e de
    tipo de vaga: a reta é a da célula com a composição média da janela; pontos = reta + resíduo."""
    d = r["_detalhes"]
    fit, usa, w = d["fit"], d["usa"], d["w"]
    grupos = sorted(np.unique(a.g).tolist())
    peso = {gl: float(np.sum(w[usa & (a.g == gl)])) for gl in grupos}
    tot = sum(peso.values())
    peso = {g: v / tot for g, v in peso.items()}
    estrut = {"T"} | {f"{p}[{g}]" for g in grupos for p in ("const", "x", "T_x")}
    extras = [(nm, float(np.sum(fit["w"] * fit["X"][:, j]) / np.sum(fit["w"])))
              for j, nm in enumerate(fit["nomes"]) if nm not in estrut]

    def coef(x, t):
        cs = [("T", t)] + extras
        for gl in grupos:
            cs += [(f"const[{gl}]", peso[gl]), (f"x[{gl}]", peso[gl] * x), (f"T_x[{gl}]", peso[gl] * t * x)]
        return cs

    out = {}
    for lado, gr in (("abaixo", np.linspace(-H + 1, 0, 50)), ("acima", np.linspace(1e-9, H - 1, 50))):
        t = 1.0 if lado == "acima" else 0.0
        pr, lo, hi = [], [], []
        for g in gr:
            val, ep = T23._linha_prevista(fit, coef(g / 1000.0, t), fit["V"])
            pr.append(val)
            lo.append(val - L.Z_975 * ep)
            hi.append(val + L.Z_975 * ep)
        out[lado] = (gr, np.array(pr), np.array(lo), np.array(hi))
    xu, tu = d["x"][usa], d["t"][usa]
    media = np.array([T23._linha_prevista(fit, coef(xx, tt), fit["V"])[0] for xx, tt in zip(xu, tu)])
    y_p = np.full(len(a.s), np.nan)
    y_p[usa] = media + fit["residuos"]
    return out, y_p


COMO_LER_A1 = (
    "COMO LER. Cada painel junta os ciclos 1 a 3 e os cortes 0,300 e 0,400: o eixo horizontal é a distância do IVS "
    "2010 oficial do município ao corte (à direita, bolsa maior; à esquerda, bolsa menor). Entram todos os municípios "
    "com IVS oficial, inclusive os que não tiveram nenhuma vaga no quadro (esses valem zero: sem célula, nenhuma vaga "
    "oferecida e nenhuma preenchida). O eixo vertical é o número de vagas por 10 mil habitantes do Censo 2022: à "
    "esquerda, vagas preenchidas na 1ª chamada; à direita, vagas oferecidas (imediatas + cadastro reserva). Cada ponto "
    "é a média de uma faixa de 0,010 de distância (reta média + resíduo médio dos municípios da faixa); o tamanho conta "
    "linhas município × ciclo. A reta é a média ponderada das retas de cada ciclo × corte (local linear, kernel "
    "triangular, h = 0,050), e a faixa clara é o IC 95%. A seta laranja é o salto comum no corte, com valor, IC 95% "
    "(CR1 por município) e p no título. É o efeito total da faixa por habitante, sem condicionar em ter aberto vaga. "
    "O salto mede o pacote do corte (bolsa anunciada +R$ 5 mil e outras regras que mudam no mesmo IVS). EMPIRICO.")
COMO_LER_A3 = (
    "COMO LER. Aqui a unidade é a célula (estabelecimento × curso) do quadro da 1ª chamada, nos ciclos 1 a 3 e nos "
    "cortes 0,300 e 0,400 empilhados; o eixo horizontal é a distância do IVS 2010 oficial do município da célula ao "
    "corte. O eixo vertical é a probabilidade de a célula ter pelo menos um médico alocado na 1ª chamada, ajustada "
    "pelos efeitos fixos de curso × ciclo e de tipo de vaga (imediata ou só cadastro reserva): a reta é a da célula "
    "com a composição média de cursos e tipos de vaga da janela. Cada ponto é essa reta mais o resíduo médio das "
    "células de uma faixa de 0,010 de distância; o tamanho conta células. A faixa clara é o IC 95% da reta (CR1 por "
    "município), e a seta laranja é o salto no corte, com valor em pontos percentuais, IC 95% e p no título. Só "
    "entram células que foram abertas: o salto é condicional à abertura, e os limites de Lee do A2 dizem quanto a "
    "seleção na abertura poderia movê-lo. O tipo de prática não existe no quadro e não entra. EMPIRICO.")


def gerar_figuras(dados: dict, dir_fig: Path) -> list[dict]:
    dir_fig.mkdir(parents=True, exist_ok=True)
    for antigo in dir_fig.glob("*.png"):
        antigo.unlink()
    UK, CK = dados["UK"], dados["CK"]
    ks = CICLOS
    feitas = []
    a = T23.montar_amostra([(UK[k], c, f"c{k}_{c}") for k in ks for c in CORTES], empilhada=True)
    x = L.normalizar_s_mil(a.s) - a.c
    paineis, meta = [], []
    for oid, col, rot_p in (("A1_PREENCH_10K", "preench_10k", "Vagas preenchidas na 1ª chamada por 10 mil hab."),
                            ("A1_OFERT_10K", "ofert_10k", "Vagas oferecidas (imediatas + CR) por 10 mil hab.")):
        r = T23.ajustar(a, a.col(col), H)
        cur, y_p, pesos = T23.curva_empilhada(r, a)
        dentro = np.isfinite(y_p)
        paineis.append({"x": np.where(dentro, x, np.nan), "y": y_p, "dentro": dentro, "corte": 0, "curva": cur,
                        "rotulo": f"{rot_p} (U, ciclos 1, 2 e 3, cortes empilhados)",
                        "titulo": _titulo(r, "por 10 mil hab.", casas=3)})
        meta.append({"outcome_id": oid, "populacao": "U", "ciclo": "+".join(map(str, ks)), "corte": EMPILHADO,
                     "especificacao": "A1", "variante": "principal", "tau": r["tau"], "ic95_inf": r["ic95_inf"],
                     "ic95_sup": r["ic95_sup"], "p_valor": r["p_valor"]})
    nome = "NA_A1_por_10k_empilhado.png"
    T23.desenhar(paineis, "A1 — vagas preenchidas e oferecidas por 10 mil habitantes, todos os municípios (U), ciclos "
                          "e cortes empilhados", "Vagas por 10 mil habitantes", "distância ao corte (IVS 2010 oficial − corte)",
                 COMO_LER_A1, dir_fig / nome, unidade_n=("linha município × ciclo", "linhas município × ciclo"))
    feitas.append({"arquivo": rotulo(dir_fig / nome), "paineis": meta})
    # A3: célula preenchida, empilhado, com efeitos fixos (especificação principal).
    a = T23.montar_amostra([(CK[k], c, f"c{k}_{c}") for k in ks for c in CORTES], empilhada=True)
    r = ajustar_celula(a, a.col("preenchida"), H, fe=True, tipo=True)
    cur, y_p = curva_empilhada_fe(r, a)
    x = L.normalizar_s_mil(a.s) - a.c
    dentro = np.isfinite(y_p)
    nome = "NA_A3_celula_preenchida_empilhado.png"
    T23.desenhar([{"x": np.where(dentro, x, np.nan), "y": y_p, "dentro": dentro, "corte": 0, "curva": cur,
                   "rotulo": "Células do quadro, ciclos 1, 2 e 3 e cortes 0,300 e 0,400 empilhados",
                   "titulo": _titulo(r, "p.p.", casas=1, pp=True)}],
                 "A3 — probabilidade de a célula aberta ser preenchida na 1ª chamada (efeitos fixos de curso × ciclo e "
                 "tipo de vaga)", "Probabilidade de célula preenchida\n(ajustada pelos efeitos fixos)",
                 "distância ao corte (IVS 2010 oficial do município − corte)", COMO_LER_A3, dir_fig / nome,
                 unidade_n=("célula", "células"))
    feitas.append({"arquivo": rotulo(dir_fig / nome), "paineis": [
        {"outcome_id": "A3_PREENCHIDA", "populacao": rot_c(ks), "ciclo": "+".join(map(str, ks)), "corte": EMPILHADO,
         "especificacao": "A3", "variante": "principal", "tau": r["tau"], "ic95_inf": r["ic95_inf"],
         "ic95_sup": r["ic95_sup"], "p_valor": r["p_valor"]}]})
    return feitas


# ---------------------------------------------------------------------------
# Doc 49 (blocos gerados; nenhum número digitado)
# ---------------------------------------------------------------------------

MARCA = re.compile(r"(<!-- NA:(?P<nome>[A-Za-z0-9_]+):inicio -->\n)(?P<corpo>.*?)(\n<!-- NA:(?P=nome):fim -->)", re.S)


def aplicar_tabelas_doc(texto: str, tabelas: dict[str, str]) -> str:
    def sub(m):
        nome = m.group("nome")
        if nome not in tabelas:
            raise KeyError(f"tabela {nome} nao gerada")
        return m.group(1) + tabelas[nome] + m.group(4)
    return MARCA.sub(sub, texto)


def tabelas_no_doc(texto: str) -> dict[str, str]:
    return {m.group("nome"): m.group("corpo") for m in MARCA.finditer(texto)}


def _casas(un: str) -> tuple[int, bool, str]:
    if un == UN_10K:
        return 3, False, ""
    return T23._casas(un)


def _tau(r):
    c, pp, u = _casas(r["unidade"])
    return f"{_n(r['tau'], c, pp)}{u}"


def _icr(r, a="ic95_inf", b="ic95_sup"):
    c, pp, _ = _casas(r["unidade"])
    return _ic(r[a], r[b], c, pp)


def _rel(r, col="efeito_relativo_media_abaixo"):
    v = r.get(col)
    return "—" if v is None or pd.isna(v) else _n(v, 1, pp=True) + " %"


def _media(r):
    c, pp, _ = _casas(r["unidade"])
    return _n(r["media_abaixo"], c, pp, sinal=False) + (" %" if pp else "")


def _corte(r):
    return str(r["corte"]).replace(".", ",")


def _nab(r):
    return T23._nab(r)


def _tab(sub: pd.DataFrame, cab: list[str], cols) -> str:
    return T23._tab(sub, cab, cols)


def _exclui(lo, hi) -> bool:
    return bool(np.isfinite(lo) and np.isfinite(hi) and (lo > 0 or hi < 0))


def _sel(est: pd.DataFrame, **f) -> pd.DataFrame:
    m = np.ones(len(est), dtype=bool)
    for k, v in f.items():
        m &= est[k].astype(str) == str(v)
    return est[m]


def _uma(est: pd.DataFrame, **f) -> dict | None:
    s = _sel(est, **f)
    return s.iloc[0].to_dict() if len(s) == 1 else None


TODOS = "+".join(str(k) for k in CICLOS)


def leitura_conjunta(est: pd.DataFrame, n_est: pd.DataFrame | None) -> str:
    """Leitura por regra fixa (nenhum número digitado no doc): o que A1–A4 dizem juntos, com o ciclo 1 à parte."""

    def frase(r, nome, un=""):
        if r is None or not np.isfinite(r["tau"]):
            return f"{nome}: sem estimativa"
        sinal = "negativo" if r["tau"] < 0 else "positivo"
        return (f"{nome}: salto {sinal} ({_tau(r)}{un}; IC 95% {_icr(r)}), que "
                f"{'exclui' if _exclui(r['ic95_inf'], r['ic95_sup']) else 'contém'} zero")

    def lee(r, nome):
        if r is None or not np.isfinite(r["lee_limite_inf"]):
            return f"{nome}: limites indefinidos"
        cont = r["lee_limite_inf"] <= 0 <= r["lee_limite_sup"]
        im = (f"; o IC de Imbens–Manski {_ic(r['ic_im_inf'], r['ic_im_sup'], 1, True)} "
              f"{'exclui' if _exclui(r['ic_im_inf'], r['ic_im_sup']) else 'contém'} zero"
              if np.isfinite(r["ic_im_inf"]) else "")
        return (f"{nome}: aparando {_n(r['lee_p_aparo'], 1, True, False)} % do lado {r['lee_lado_aparado']} "
                f"(o de maior abertura), o salto no preenchimento fica entre {_n(r['lee_limite_inf'], 1, True)} e "
                f"{_n(r['lee_limite_sup'], 1, True)} p.p., intervalo que {'contém' if cont else 'não contém'} "
                f"zero{im}")

    blocos = {}
    for rotulo_c, ck, popv, popc in (("todos os ciclos empilhados", TODOS, rot_v(CICLOS), rot_c(CICLOS)),
                                     ("ciclo 1", "1", "V1", rot_c(1))):
        a1f = _uma(est, especificacao="A1", outcome_id="A1_PREENCH_10K", variante="principal", ciclo=ck, corte=EMPILHADO)
        a1o = _uma(est, especificacao="A1", outcome_id="A1_OFERT_10K", variante="principal", ciclo=ck, corte=EMPILHADO)
        a2i = _uma(est, especificacao="A2", outcome_id="A2_INTENSIVA", variante="margem_intensiva_vaga", ciclo=ck,
                   corte=EMPILHADO)
        a2e = _uma(est, especificacao="A2", outcome_id="A2_EXTENSIVA", variante="margem_extensiva_abertura", ciclo=ck,
                   corte=EMPILHADO)
        a3 = _uma(est, especificacao="A3", outcome_id="A3_PREENCHIDA", variante="principal", populacao=popc,
                  corte=EMPILHADO)
        a4s = _uma(est, especificacao="A4", outcome_id="N1", variante="com_covariaveis", populacao=popv, corte=EMPILHADO)
        a4b = _uma(est, especificacao="A4", outcome_id="N1", variante="sem_covariaveis_mesma_amostra", populacao=popv,
                   corte=EMPILHADO)
        a4f = _uma(est, especificacao="A4", outcome_id="A1_PREENCH_10K", variante="com_covariaveis", ciclo=ck,
                   corte=EMPILHADO, populacao="U")
        sa = None
        if n_est is not None:
            sa = _uma(n_est, especificacao="S-a", variante="principal", outcome_id="N1", populacao=popv, corte=EMPILHADO)
        blocos[rotulo_c] = {"a1f": a1f, "a1o": a1o, "a2i": a2i, "a2e": a2e, "a3": a3, "a4s": a4s, "a4b": a4b,
                            "a4f": a4f, "sa": sa}
    out = []
    for rotulo_c, b in blocos.items():
        out.append(f"**{rotulo_c.capitalize()}** (corte empilhado):")
        out.append(f"- A1, {frase(b['a1f'], 'vagas preenchidas por 10 mil habitantes')}; "
                   f"{frase(b['a1o'], 'vagas oferecidas por 10 mil habitantes')}.")
        out.append(f"- A2, margem intensiva — {lee(b['a2i'], 'vagas')}.")
        out.append(f"- A2, margem extensiva — {lee(b['a2e'], 'municípios')}.")
        out.append(f"- A3, {frase(b['a3'], 'probabilidade de a célula aberta ser preenchida (efeitos fixos)')}.")
        if b["a4s"] is not None and b["a4b"] is not None:
            out.append(f"- A4, N1 sem controle das vagas: {frase(b['a4b'], 'sem covariáveis')}; "
                       f"{frase(b['a4s'], 'com covariáveis pré-determinadas')}; "
                       f"{frase(b['a4f'], 'vagas preenchidas por 10 mil hab. com covariáveis')}.")
        if rotulo_c == "ciclo 1" and b["sa"] is not None:
            out.append(f"- No ciclo 1 a oferta não pode ter respondido à faixa em si (protocolo 48, §8), e "
                       f"condicionar nas vagas oferecidas é mais defensável: S-a do doc 49 (N1 dado as vagas), "
                       f"{frase(b['sa'], 'vagas por município')}.")
        a1f, a1o, a2i, a3 = b["a1f"], b["a1o"], b["a2i"], b["a3"]
        if None in (a1f, a1o, a3):
            continue
        ef = _exclui(a1f["ic95_inf"], a1f["ic95_sup"])
        eo = _exclui(a1o["ic95_inf"], a1o["ic95_sup"])
        e3 = _exclui(a3["ic95_inf"], a3["ic95_sup"])
        eim = a2i is not None and _exclui(a2i["ic_im_inf"], a2i["ic_im_sup"])
        eb = b["a4b"] is not None and _exclui(b["a4b"]["ic95_inf"], b["a4b"]["ic95_sup"])
        ec = b["a4s"] is not None and _exclui(b["a4s"]["ic95_inf"], b["a4s"]["ic95_sup"])
        if ef and e3 and eim and np.sign(a1f["tau"]) == np.sign(a3["tau"]):
            concl = ("as três leituras do preenchimento (por habitante, nas vagas sempre abertas e por célula aberta) "
                     "excluem zero com o mesmo sinal: há indício de efeito do pacote do corte sobre o preenchimento, "
                     "não só sobre a abertura")
        elif eo and not (e3 or eim):
            concl = ("a oferta por habitante salta, mas o preenchimento condicional à abertura não se distingue de "
                     "zero: o que muda no corte é a abertura ou o porte, não o preenchimento das vagas abertas")
        elif not (ef or eo or e3 or eim or ec):
            concl = ("nenhuma leitura por habitante (A1), nas vagas sempre abertas (A2), por célula aberta (A3) ou com "
                     "covariáveis pré-determinadas (A4) distingue de zero, com a precisão relatada, um efeito do pacote "
                     "do corte sobre o preenchimento, nem sobre a abertura por habitante")
            if eb:
                concl += ("; o único salto que exclui zero é o de N1 em contagem por município sem covariáveis (S-b), "
                          "que deixa de excluir zero com o porte e a capacidade instalada pré-existentes e não aparece "
                          "por habitante: é compatível com diferença de porte entre os lados do corte, não com efeito "
                          "sobre o preenchimento")
        else:
            partes = [n for n, v in (("o preenchimento por habitante (A1)", ef), ("a oferta por habitante (A1)", eo),
                                     ("o preenchimento por célula aberta (A3)", e3),
                                     ("o IC de Imbens–Manski da margem intensiva (A2)", eim),
                                     ("N1 com covariáveis pré-determinadas (A4)", ec)) if v]
            concl = ("as leituras não concordam: só " + ", ".join(partes) + " exclui(em) zero; não há base para "
                     "separar efeito sobre o preenchimento de efeito sobre a abertura")
        out.append(f"- **Leitura conjunta ({rotulo_c}):** {concl}. É descrição com a precisão relatada, do pacote do "
                   f"corte, e não efeito da participação no PMM-E.")
        out.append("")
    return "\n".join(out).rstrip()


def gerar_tabelas_doc(est: pd.DataFrame, resumo: dict, n_est: pd.DataFrame | None = None,
                      e9: dict | None = None) -> dict[str, str]:
    t: dict[str, str] = {}
    at = resumo.get("atributos_celula", {})
    linhas = ["| Atributo da célula | Situação | Coluna ou motivo |", "|---|---|---|"]
    for k, v in at.get("existem", {}).items():
        linhas.append(f"| {k.replace('_', ' ')} | existe | {v} |")
    for k, v in at.get("ausentes", {}).items():
        linhas.append(f"| {k.replace('_', ' ')} | **ausente** | {v} |")
    linhas.append(f"| estabelecimentos hospitalares (A4) | **ausente** | {MOTIVO_HOSPITALAR} |")
    t["atributos"] = "\n".join(linhas)
    f = (est["especificacao"] == "A1") & est["variante"].isin(["principal", "poisson_offset_log_populacao"]) & \
        est["outcome_id"].isin(["A1_PREENCH_10K", "A1_OFERT_10K"])
    t["a1"] = _tab(est[f], ["Outcome", "Variante", "Ciclo", "Corte", "n abaixo / acima", "Média abaixo", "Salto",
                            "IC 95%", "p", "Salto / média abaixo", "Efeito relativo (Poisson)"],
                   [lambda r: r["outcome_id"], lambda r: r["variante"], lambda r: r["ciclo"], _corte, _nab,
                    lambda r: _media(r) if r["variante"] == "principal" else "—", _tau, _icr,
                    lambda r: _p(r["p_valor"]), _rel,
                    lambda r: _rel(r, "efeito_relativo") if pd.notna(r["efeito_relativo"]) else "—"])
    f = est["especificacao"] == "A2"
    t["a2"] = _tab(est[f], ["Margem", "Variante", "Ciclo", "Corte", "Seleção abaixo / acima", "p aparado (lado)",
                            "Preench. abaixo / acima", "Salto ingênuo [IC 95%]", "Limites de Lee", "IC Imbens–Manski",
                            "Reamostras válidas"],
                   [lambda r: "intensiva (vaga)" if r["outcome_id"] == "A2_INTENSIVA" else "extensiva (abertura)",
                    lambda r: "principal" if r["no_protocolo"] in (True, "True") else "seleção ponderada pela população "
                                                                                       "(fora do adendo)",
                    lambda r: r["ciclo"], _corte,
                    lambda r: (f"{_n(r['taxa_selecao_abaixo'], 3, sinal=False)} / {_n(r['taxa_selecao_acima'], 3, sinal=False)}"
                               + (" por 10 mil" if r["outcome_id"] == "A2_INTENSIVA" else " (prob.)")),
                    lambda r: (f"{_n(r['lee_p_aparo'], 1, True, False)} % ({r['lee_lado_aparado']})"
                               if pd.notna(r["lee_p_aparo"]) else "—"),
                    lambda r: (f"{_n(r['taxa_preench_abaixo'], 1, True, False)} / {_n(r['taxa_preench_acima'], 1, True, False)} %"
                               if pd.notna(r["taxa_preench_abaixo"]) else "—"),
                    lambda r: f"{_n(r['tau'], 1, True)} p.p. {_icr(r)}",
                    lambda r: _ic(r["lee_limite_inf"], r["lee_limite_sup"], 1, True),
                    lambda r: _ic(r["ic_im_inf"], r["ic_im_sup"], 1, True),
                    lambda r: f"{T23._fi(r['n_boot_validos'])} / {T23._fi(r['n_boot'])}"])
    f = (est["especificacao"] == "A3") & (est["status"] == "EXECUTADO") & \
        (est["variante"].isin(["principal", "so_curso_x_ciclo", "sem_efeitos_fixos"])) & \
        est["outcome_id"].isin(["A3_PREENCHIDA", "A3_ALOC_POR_VAGA", "A3_CAND_1A_OPCAO", "A3_TEM_CAND_1A_OPCAO"])
    sub = est[f & ((est["corte"] == EMPILHADO) | (est["variante"] == "principal"))]
    t["a3"] = _tab(sub, ["Outcome", "Variante", "População", "Corte", "Células", "Municípios abaixo / acima",
                         "Média abaixo", "Salto", "IC 95% (CR1)", "p"],
                   [lambda r: r["outcome_id"], lambda r: r["variante"], lambda r: r["populacao"], _corte,
                    lambda r: T23._fi(r["n_obs"]), _nab, _media, _tau, _icr, lambda r: _p(r["p_valor"])])
    # Ponte com o E9.
    linhas = ["| Ciclo | E9: razão de chances da 1ª opção por +R$ 5 mil (p) | E9: variação média da probabilidade, p.p. "
              "[IC 95%] | A3: célula com candidato de 1ª opção, salto [IC 95%] | A3: célula preenchida, salto [IC 95%] |",
              "|---|---|---|---|---|"]
    rp = (e9 or {}).get("resultado_principal", {})
    for k in [str(x) for x in CICLOS] + ["empilhado"]:
        ck = TODOS if k == "empilhado" else k
        pop = rot_c(CICLOS) if k == "empilhado" else rot_c(int(k))
        rc = _uma(est, especificacao="A3", outcome_id="A3_TEM_CAND_1A_OPCAO", variante="principal", populacao=pop,
                  corte=EMPILHADO)
        rf = _uma(est, especificacao="A3", outcome_id="A3_PREENCHIDA", variante="principal", populacao=pop,
                  corte=EMPILHADO)
        e = rp.get(k, {})
        ic9 = e.get("variacao_prob_media_pp_ic95") or [None, None]
        linhas.append(f"| {ck} | {_n(e.get('razao_chances_por_5mil'), 2, sinal=False)} ({_p(e.get('p'))}) | "
                      f"{_n(e.get('variacao_prob_media_pp'), 2)} [{_n(ic9[0], 2)}; {_n(ic9[1], 2)}] | "
                      f"{(_tau(rc) + ' ' + _icr(rc)) if rc else '—'} | {(_tau(rf) + ' ' + _icr(rf)) if rf else '—'} |")
    t["a3_ponte_e9"] = "\n".join(linhas)
    f = (est["especificacao"] == "A4") & est["variante"].isin(
        ["sem_covariaveis_mesma_amostra", "com_covariaveis", "com_covariaveis_coeficiente_unico"]) & \
        (est["status"] == "EXECUTADO") & ((est["corte"] == EMPILHADO))
    t["a4"] = _tab(est[f], ["Outcome", "Variante", "População", "Ciclo", "n abaixo / acima", "Salto", "IC 95%", "p",
                            "Salto / média abaixo"],
                   [lambda r: r["outcome_id"], lambda r: r["variante"], lambda r: r["populacao"], lambda r: r["ciclo"],
                    _nab, _tau, _icr, lambda r: _p(r["p_valor"]), _rel])
    f = (est["especificacao"] == "A4") & (est["variante"] == "covariavel_como_outcome") & \
        ((est["populacao"] == "U") | (est["corte"] == EMPILHADO))
    t["a4_balanco"] = _tab(est[f], ["Covariável", "População", "Ciclo", "Corte", "n abaixo / acima", "Média abaixo",
                                    "Salto", "IC 95%", "p"],
                           [lambda r: r["outcome"], lambda r: r["populacao"], lambda r: r["ciclo"], _corte, _nab,
                            lambda r: _n(r["media_abaixo"], 2, sinal=False), lambda r: _n(r["tau"], 2),
                            lambda r: _ic(r["ic95_inf"], r["ic95_sup"], 2), lambda r: _p(r["p_valor"])])
    t["leitura_conjunta"] = leitura_conjunta(est, n_est)
    figs = resumo.get("saidas", {}).get("figuras", [])
    linhas = ["| Figura | Outcome | População | Salto no título | IC 95% | p |", "|---|---|---|---|---|---|"]
    for fg in figs:
        for p in fg["paineis"]:
            pp = p["outcome_id"].startswith("A3")
            cs = 1 if pp else 3
            linhas.append(f"| `{Path(fg['arquivo']).name}` | {p['outcome_id']} | {p['populacao']} | "
                          f"{_n(p['tau'], cs, pp)} | {_ic(p['ic95_inf'], p['ic95_sup'], cs, pp)} | "
                          f"{_p(p['p_valor'])} |")
    t["figuras"] = "\n".join(linhas)
    q, v = resumo.get("contagens", {}), resumo.get("validacoes", {})
    bt = resumo.get("bootstrap", {})
    t["validacoes"] = "\n".join([
        "| Conferência | Resultado |", "|---|---|",
        f"| linhas em NA_estimativas.csv | {q.get('linhas')} |",
        f"| EXECUTADO / SEM_ESTIMATIVA / NAO_EXECUTADO | {q.get('executado')} / {q.get('sem_estimativa')} / {q.get('nao_executado')} |",
        f"| MQP rápido do bootstrap = rdd_lib (salto, interceptos, pesos omega), todas as amostras do A2 | {v.get('desenho_rapido_igual_rdd_lib')} |",
        f"| Lee extensivo daqui = rdd_lib.limites_lee_rd (cortes únicos) | {v.get('lee_extensivo_igual_rdd_lib')} amostras |",
        f"| Poisson local daqui = rdd_lib (um corte, offset) | {v.get('poisson_igual_rdd_lib')} |",
        f"| soma das células = município (vagas e alocados), V1–V3 | {v.get('soma_celulas_igual_municipio')} |",
        f"| população de U = Censo 2022 do a06 | {v.get('populacao_igual_censo2022')} |",
        f"| bootstrap: reamostras, semente, municípios reamostrados | {bt.get('n_boot')}, {bt.get('semente')}, {bt.get('n_municipios')} |",
        f"| células de município sem IVS oficial (fora da RDD) | {q.get('celulas_sem_ivs_fora')} |",
        "| municípios sem estoque CNES completo (fora do A4) | " + "; ".join(
            f"{k}: {v}" for k, v in (q.get("municipios_sem_estoque_cnes") or {}).items()) + " |",
    ])
    return t


def ler_saidas() -> tuple[pd.DataFrame, dict]:
    est = pd.read_csv(OUT / NOME_EST, dtype={"corte": str, "ciclo": str})
    resumo = json.loads((OUT / NOME_RESUMO).read_text(encoding="utf-8"))
    return est, resumo


def ler_auxiliares() -> tuple[pd.DataFrame | None, dict | None]:
    n_est = pd.read_csv(ARQ_N_EST, dtype={"corte": str, "ciclo": str}) if ARQ_N_EST.exists() else None
    e9 = json.loads(ARQ_E9.read_text(encoding="utf-8")) if ARQ_E9.exists() else None
    return n_est, e9


def atualizar_doc() -> None:
    texto = DOC49.read_text(encoding="utf-8")
    if not tabelas_no_doc(texto):
        raise FalhaValidacao(f"{rotulo(DOC49)} sem marcadores <!-- NA:... -->")
    est, resumo = ler_saidas()
    n_est, e9 = ler_auxiliares()
    DOC49.write_text(aplicar_tabelas_doc(texto, gerar_tabelas_doc(est, resumo, n_est, e9)), encoding="utf-8")
    print(f"blocos NA do doc 49 regravados: {rotulo(DOC49)}")


# ---------------------------------------------------------------------------
# Execução
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--atualizar-doc", action="store_true", help="so regrava os blocos NA do doc 49 a partir das saidas")
    args = ap.parse_args(argv)
    if args.atualizar_doc:
        atualizar_doc()
        return 0
    dados = carregar_tudo()
    est, extras = estimar_tudo(dados)
    nucleo = ["tau", "ep", "ic95_inf", "ic95_sup", "p_valor"]
    sem_nota = est[est[nucleo].isna().any(axis=1) & (est["nota"].fillna("") == "")]
    if len(sem_nota):
        raise FalhaValidacao(f"{len(sem_nota)} linhas com NaN sem nota")
    if not ((est["natureza_dos_dados"] == NATUREZA).all() and (est["estatuto"] == ESTATUTO).all()):
        raise FalhaValidacao("linha sem rotulo de natureza ou estatuto")
    OUT.mkdir(parents=True, exist_ok=True)
    est.to_csv(OUT / NOME_EST, index=False)
    figs = gerar_figuras(dados, OUT / DIR_FIG)
    for fg in figs:
        for p in fg["paineis"]:
            r = _uma(est, outcome_id=p["outcome_id"], populacao=p["populacao"], ciclo=p["ciclo"], corte=p["corte"],
                     especificacao=p["especificacao"], variante=p["variante"])
            if r is None or abs(r["tau"] - p["tau"]) > 1e-10:
                raise FalhaValidacao(f"titulo da figura {fg['arquivo']} nao bate com o CSV")
    q = {"linhas": int(len(est)), "executado": int((est["status"] == "EXECUTADO").sum()),
         "sem_estimativa": int((est["status"] == "SEM_ESTIMATIVA").sum()),
         "nao_executado": int((est["status"] == "NAO_EXECUTADO").sum()),
         "por_especificacao": est["especificacao"].value_counts().sort_index().to_dict(),
         "celulas_sem_ivs_fora": sum(dados["fora_cel"].values()),
         "municipios_sem_estoque_cnes": dados["cnes"]["municipios_sem_estoque_completo"]}
    n_est, e9 = ler_auxiliares()
    entradas = [
        E6.bloco_entrada(PROTOCOLO_MD, "protocolo 48 com o adendo §7 e a correcao §8 (somente lido)",
                         "pipeline do repositorio", "2026-10-19", "§7, §8", "documento", "-", "-"),
        E6.bloco_entrada(A08, "running variable (IVS 2010 oficial)", "Ipea, Atlas da Vulnerabilidade Social (a08)",
                         "Censo 2010", f"{len(dados['rv'])} municipios", "municipio", "co_ibge", "ivs"),
        E6.bloco_entrada(ARQ_U, "populacao U (A1, A2, A4), zero estrutural fora do quadro", "tarefa B", "ver dicionario",
                         f"{len(dados['U'])} municipios", "municipio", "co_ibge", "nenhum"),
        E6.bloco_entrada(ARQ_VM, "V1-V3 (A2, A4)", "tarefa B", "ver dicionario",
                         ", ".join(f"V{k}: {len(d)}" for k, d in dados["V"].items()), "municipio x ciclo",
                         "ciclo, co_ibge", "municipios sem IVS oficial fora"),
        E6.bloco_entrada(ARQ_VC, "celulas do quadro (A2: alocados limitados as vagas; A3)", "tarefa B", "ver dicionario",
                         f"{len(dados['cel'])} celulas", "celula CNES x curso x ciclo", "ciclo, co_cnes_7d, cod_curso",
                         "celulas de municipio sem IVS oficial fora do A3"),
        E6.bloco_entrada(ARQ_POP, "populacao do Censo 2022 (conferencia de populacao_2022)", "IBGE, Censo 2022 (a06)",
                         "2022", "municipios", "municipio", "co_ibge_6d", "nenhum"),
        E6.bloco_entrada(ARQ_CNES, "estoques CNES pre-programa (A4)", "CNES nacional (a09)", f"{COMP_PRE[0]}-{COMP_PRE[1]}",
                         f"{dados['cnes']['n_competencias']} competencias", "municipio x grupo de CBO x mes",
                         "co_ibge, competencia, grupo",
                         f"competencia entre {COMP_PRE[0]} e {COMP_PRE[1]}; grupos {', '.join(GRUPOS_CNES)}"),
        E6.bloco_entrada(T23.DICIONARIO, "dicionario dos outcomes da tarefa B (somente lido)", "tarefa B", "2026-10-18",
                         "-", "documento", "-", "-"),
    ]
    if n_est is not None:
        entradas.append(E6.bloco_entrada(ARQ_N_EST, "S-a do ciclo 1 na leitura conjunta (somente lido)",
                                         "23_estimar_contagem_vagas.py", "2026-10-19", f"{len(n_est)} linhas",
                                         "linha de estimativa", "outcome_id, populacao, corte", "S-a principal N1"))
    if e9 is not None:
        entradas.append(E6.bloco_entrada(ARQ_E9, "ponte do A3 com o E9 (somente lido)", "16_estimar_E9_escolha.py",
                                         "2026-10-18", "ciclos 1-3 e empilhado", "resumo", "resultado_principal", "-"))
    resumo = {
        "etapa": "NA_abertura_vagas_selecao",
        "natureza_dos_dados": NATUREZA,
        "estatuto": ESTATUTO,
        "data_execucao": DATA_EXECUCAO,
        "script": rotulo(Path(__file__)),
        "protocolo": {"arquivo": rotulo(PROTOCOLO_MD), "sha256": sha256(PROTOCOLO_MD), "secoes": ["§7", "§8"]},
        "contraste": CONTRASTE,
        "salto": "tau = lado com bolsa maior (s > c) menos lado com bolsa menor; o corte pertence ao lado inferior",
        "entradas": entradas,
        "atributos_celula": dados["atributos"],
        "cnes_pre": dados["cnes"],
        "monotonicidade": MONOTONICIDADE,
        "bootstrap": {"n_boot": N_BOOT, "semente": list(SEMENTE_BOOT), "unidade": "municipio (com reposicao; a "
                      "multiplicidade entra como peso de frequencia em todas as regressoes da reamostra)",
                      "n_municipios": extras["n_universo_bootstrap"], "validos": extras["boot_validos"],
                      "ic": "Imbens e Manski (2004): [inf - c ep_inf; sup + c ep_sup], c de Phi(c + Delta/max ep) - "
                            "Phi(-c) = 0,95, ep = DP bootstrap de cada limite"},
        "ciclo_1": "protocolo 48, §8: no ciclo 1 a adesao dos gestores precedeu o anuncio da faixa; a oferta nao pode "
                   "ter respondido a faixa em si; o doc 49 relata o ciclo 1 a parte na leitura conjunta",
        "decisoes": [
            "A1: vagas preenchidas = N1 (n_alocados_ch1, como no doc 49); vagas oferecidas = imediatas + cadastro "
            "reserva (forma principal do doc 49); por 10 mil habitantes do Censo 2022; zero estrutural fora do quadro. "
            "A versao com alocados limitados as vagas da celula (contagem do A2) e ponte, fora do adendo.",
            "A2 intensiva: s = intercepto local linear (sem peso) das vagas oferecidas por 10 mil hab. em U de cada "
            "lado; f = intercepto local linear da fracao limitada do municipio com peso = vagas oferecidas (equivale "
            "ao outcome binario no nivel da vaga) em V; no empilhado, interceptos agregados com os pesos omega_g da "
            "regressao de s (os mesmos para s e f) e lado de cima = lado de baixo + salto comum. Variante com s "
            "ponderado pela populacao, fora do adendo.",
            "A2 extensiva: rdd_lib.limites_lee_rd com um corte (selecao = ter >= 1 celula, que no quadro equivale a ter "
            ">= 1 vaga; outcome = fracao limitada); no empilhado, o mesmo algoritmo com a fracao de aparo comum e o "
            "aparo dentro de cada grupo ciclo x corte.",
            "A2 extensiva: o aparo usa o quantil ponderado do meio-janela com reta local (aproximacao (i) da "
            "rdd_lib); por isso, ao contrario da margem intensiva, os limites podem nao conter o salto ingenuo, o que "
            "fica anotado na linha.",
            "A2 bootstrap: municipios de U reamostrados com reposicao (o mesmo sorteio serve a todas as amostras e "
            "ciclos da reamostra, preservando o cluster); reamostra sem suporte (menos de 2 mass points num lado de "
            "algum grupo) ou com taxa de selecao nao positiva e descartada e contada.",
            "A3: celula preenchida = >= 1 alocado na 1a chamada (n_alocados_ch1); alocados / vagas sem limite (como o "
            "§7 diz) e, fora do adendo, limitado; candidatos de 1a opcao e, como ponte com o E9, ter >= 1 candidato de "
            "1a opcao; efeitos fixos de curso x ciclo (efeitos_fixos da rdd_lib) e tipo de vaga (covariavel linear "
            "nao interagida); variantes sem tipo de vaga (o tipo de vaga tambem e decisao de quem monta o quadro) e "
            "sem efeitos fixos.",
            "A4: covariaveis centradas na media de kernel da janela, comuns aos dois lados, um coeficiente por grupo "
            "ciclo x corte no empilhado (como o controle do script 23) e, fora do adendo, um so coeficiente. Para "
            "contagens (S-b), estoques em nivel; para outcomes por habitante (A1), estoques por 10 mil habitantes; log "
            "da populacao nos dois. Estoque = media mensal de profissionais distintos (a09) de 202406 a 202506.",
            "O adendo nao define Holm: nenhuma linha entra em Holm (entra_holm = False).",
        ],
        "desvios": [
            {"data": DATA_EXECUCAO, "item": "tipo de pratica (A3)", "situacao": "ausente do quadro da 1a chamada",
             "resolucao": "linha NAO_EXECUTADO com o motivo; nada imputado"},
            {"data": DATA_EXECUCAO, "item": "estabelecimentos hospitalares (A4)",
             "situacao": "o painel nacional do CNES (a09) nao traz estabelecimentos",
             "resolucao": "linha NAO_EXECUTADO com o motivo; nada imputado"},
            {"data": DATA_EXECUCAO, "item": "Lee empilhado",
             "situacao": "a rdd_lib so tem limites_lee_rd com um corte",
             "resolucao": "algoritmo identico implementado aqui (conferido contra a rdd_lib em todo corte unico); no "
                          "empilhado, aparo por grupo com fracao comum"},
        ],
        "contagens": q,
        "validacoes": {"populacoes": dados["conf_pop"], "desenho_rapido_igual_rdd_lib": True,
                       "lee_extensivo_igual_rdd_lib": len(extras["conf_lee_rdd_lib"]),
                       "poisson_igual_rdd_lib": True, "soma_celulas_igual_municipio": True,
                       "celulas": dados["conf_cel"], "populacao_igual_censo2022": True, "linhas_com_nan_sem_nota": 0},
        "saidas": {NOME_EST: {"arquivo": rotulo(OUT / NOME_EST), "sha256": sha256(OUT / NOME_EST)}, "figuras": figs},
        "linguagem": "RDD em nivel = pacote do corte; A3 e condicional a abertura; os limites de Lee valem sob "
                     "monotonicidade; resultado nulo e falta de evidencia com a precisao relatada, nao ausencia de "
                     "efeito; nada aqui e efeito da participacao no PMM-E",
    }
    T23._gravar_json(OUT / NOME_RESUMO, resumo)
    atualizar_doc()
    principais = est[(est["corte"] == EMPILHADO) & (est["variante"].isin(["principal", "margem_intensiva_vaga",
                                                                            "margem_extensiva_abertura"]))
                     & est["ciclo"].isin([TODOS, "1"])]
    print(principais[["especificacao", "outcome_id", "ciclo", "tau", "ic95_inf", "ic95_sup", "p_valor",
                      "lee_limite_inf", "lee_limite_sup", "ic_im_inf", "ic_im_sup"]].to_string())
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except FalhaValidacao as erro:
        print(f"FALHA DE VALIDACAO: {erro}", file=sys.stderr)
        sys.exit(2)
