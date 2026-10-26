"""Protocolo 60, parte B (H4): oferta local de especialistas depois da chegada do 1º médico do PMM-E.

Protocolo congelado: `docs/06_execucao/60_protocolo_equivalencia_e_oferta_local.md`, parte B. Estatuto de toda
saída: `PROTOCOLO_60_POS_RESULTADO`; `natureza_dos_dados = EMPIRICO`.

Pergunta: quando o 1º especialista do PMM-E começa no município, a oferta cadastrada de especialistas do município
sobe? E a dos outros especialistas, que não são do programa, cai?

Desenho (protocolo 60, parte B)
-------------------------------
- Unidade: município × mês, 202406–202608. Nenhuma competência >= 202609 é lida.
- Amostra: municípios de U (IVS oficial a08 e população 2022 > 0) que ofereceram célula em algum ciclo (1, 2 ou 3;
  `outcomes_V_municipio`).
- Tratamento: mês de início do 1º médico do PMM-E no município, pela lista nominal (ciclos 1 e 2), lida pela função
  do D2 (`22_chegada_pmme_evento.ler_chegadas`: só co_ibge, dt_inicio_atividade, ciclo e dt_referencia). Coorte g =
  mês da chegada.
- Controles: nunca tratados e ainda não tratados (G > max(t, b)), inclusive os municípios do ciclo 3 antes do início
  do ciclo 3 (data de início pela lista de ativos de 11/09/2026, lida só nas colunas ciclo, co_ibge e
  dt_inicio_atividade): a partir do mês de início eles saem dos controles e não formam coorte.
- Estimador: Callaway e Sant'Anna, base universal b = g − 1, agregação por e ∈ [−6, +6] com pesos de coorte; funções
  do script 22 (`att_gt`, `agregar_evento`, `estimar_cs`, `wald_pre`, `pesos_mammen`), sem reimplementar.
  Bootstrap multiplicador de Mammen por município, B = 9.999, semente 20261026.
- Outcomes por 10 mil hab. (Censo 2022), painel CNES nacional a09 e definições do E7 (protocolo 40, F3):
  B1 vínculos nas CBO-alvo (F3.1), B2 horas SUS semanais nas CBO-alvo (F3.3), B3 = B2 sem as horas SUS, em CBO-alvo,
  dos médicos do PMM-E ligados ao CNES (a16, regra D1 da X1) em estabelecimento do município no mês, B4 horas totais
  nas CBO-alvo, B5 vínculos de generalistas (F3.P1, placebo). Holm em B1 e B2; BKY em B3, B4 e B5.
- Diagnósticos: Wald conjunto do pré (e = −6..−2) e Rambachan–Roth Δ^RM na média do pós (e = 0..6), M̄ ∈ {0; 0,5;
  1; 1,5; 2}, teste condicional e híbrido (`honestdid_lib.py`, protocolo 59), com ponto de ruptura.

Portões de coerência (antes de abrir resultado; falha fechada, nada é gravado)
------------------------------------------------------------------------------
1. Coortes: a amostra e as chegadas do D2, refeitas pelas funções do script 22, reproduzem as coortes trimestrais
   gravadas em `K_D2_resumo.json` (datas e contagens de municípios e especialistas), e as chegadas mensais deste
   bloco, levadas ao trimestre pela regra do D2, reproduzem as mesmas coortes.
2. Definições: B1 e B2 construídos aqui reproduzem o F3.1 e o F3.3 do E7 (`14_estimar_E7_dird_cnes.serie_outcome`)
   em 202506 (mês do pré), município a município, inclusive nos ausentes.

Leitura: ATT sob tendências paralelas da chegada. Não é efeito da bolsa nem da participação no programa como
política; vínculo cadastrado não é presença; a chegada depende da escolha do candidato.

Saídas: output/rdd_bolsa/OL_estimativas.csv, OL_ligacao_municipio.csv, OL_resumo.json, OL_figuras/*.png; blocos
entre marcadores `<!-- OL:...:inicio/fim -->` de docs/06_execucao/57k_resultados_oferta_local.md.

Uso
---
    python3 scripts/rdd_bolsa/37_oferta_local_chegada.py
    python3 scripts/rdd_bolsa/37_oferta_local_chegada.py --atualizar-doc
"""

from __future__ import annotations

import argparse
import importlib.util
import io
import json
import math
import re
import sys
import textwrap
import zipfile
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
D2M = _importar(DIR_RDD / "22_chegada_pmme_evento.py", "d2_para_ol")
H = _importar(DIR_RDD / "honestdid_lib.py", "honestdid_lib")
sys.dont_write_bytecode = _bytecode
K1M = D2M.K1M
E7 = K1M.E7
L = K1M.L

# ---------------------------------------------------------------------------
# Caminhos e parâmetros do protocolo
# ---------------------------------------------------------------------------

OUT = ROOT / "output" / "rdd_bolsa"
AQ = ROOT / "output" / "aquisicao"
PROTOCOLO_MD = ROOT / "docs" / "06_execucao" / "60_protocolo_equivalencia_e_oferta_local.md"
DOC = ROOT / "docs" / "06_execucao" / "57k_resultados_oferta_local.md"
PAINEL = E7.PAINEL
MANIF_A09 = E7.MANIFESTO_A09
POP22 = E7.POP22
A08 = E7.A08
ARQ_VM = E7.ARQ_VM
NOMINAL = D2M.NOMINAL
ATIVOS_ZIP = ROOT / "data" / "raw" / "aquisicao" / "ivs_administrativo" / "tb_profissionais_ativos_pmme_csv.zip"
DIR_A16 = AQ / "cnes_profissional"
ARQ_VINC = DIR_A16 / "painel_vinculo_mes.parquet"
ARQ_CHAVES = DIR_A16 / "chaves_origem.parquet"
MANIF_A16 = DIR_A16 / "a16_manifesto_cnes_profissional.json"
ARQ_X1 = OUT / "X1_medicos.parquet"
D2_RESUMO = OUT / "K_D2_resumo.json"

NOME_EST = "OL_estimativas.csv"
NOME_LIG = "OL_ligacao_municipio.csv"
NOME_RESUMO = "OL_resumo.json"
DIR_FIG = "OL_figuras"

DATA_EXECUCAO = "2026-10-26"
ESTATUTO = "PROTOCOLO_60_POS_RESULTADO"
NATUREZA = "EMPIRICO"
COMP_INI, COMP_FIM = "202406", "202608"
LIMITE_EXCLUSIVO = "202609"
MESES = K1M._meses(COMP_INI, COMP_FIM)
E_MIN, E_MAX = -6, 6
B_BOOT = 9_999
SEMENTE = 20261026
MES_PORTAO_DEFINICOES = "202506"
REGRA_LIGACAO = "d1_pos_hoc"              # regra principal da X1 (a mesma do P4)
CICLOS_TRATAMENTO = ("1", "2")
ALFA = 0.05
GRADE_RM = (0.0, 0.5, 1.0, 1.5, 2.0)
MAX_RM, TOL_RM = 4.0, 0.01
METODOS_RM = ("condicional", "hibrido")
ESCALA_HAB = 1e4
COLUNAS_ATIVOS = ["ciclo", "co_ibge", "dt_inicio_atividade"]
TOL_PORTAO = 1e-9

# Outcomes (protocolo 60, parte B). col = coluna do painel a09; grupo = grupo de CBO do a09.
OUTCOMES = [
    {"id": "B1", "grupo": "alvo_pmme", "col": "n_vinculos", "papel": "primaria", "familia": "holm",
     "desc": "vínculos nas CBO-alvo", "curto": "vínculos de especialistas (CBO-alvo)",
     "unidade": "vínculos por 10 mil hab. (Censo 2022)", "e7": "F3.1"},
    {"id": "B2", "grupo": "alvo_pmme", "col": "horas_sus_semanais", "papel": "primaria", "familia": "holm",
     "desc": "horas SUS semanais nas CBO-alvo", "curto": "horas SUS semanais de especialistas (CBO-alvo)",
     "unidade": "horas SUS semanais por 10 mil hab. (Censo 2022)", "e7": "F3.3"},
    {"id": "B3", "grupo": "alvo_pmme", "col": "horas_sus_semanais", "papel": "secundaria", "familia": "bky",
     "desc": "horas SUS semanais nas CBO-alvo sem as dos médicos do PMM-E ligados (os outros especialistas)",
     "curto": "horas SUS semanais dos outros especialistas (sem os do PMM-E)",
     "unidade": "horas SUS semanais por 10 mil hab. (Censo 2022)", "e7": None},
    {"id": "B4", "grupo": "alvo_pmme", "col": "horas_totais", "papel": "secundaria", "familia": "bky",
     "desc": "horas totais (SUS e não SUS; ambulatorial, hospitalar e outras) nas CBO-alvo",
     "curto": "horas totais de especialistas (CBO-alvo)",
     "unidade": "horas semanais por 10 mil hab. (Censo 2022)", "e7": None},
    {"id": "B5", "grupo": "generalistas", "col": "n_vinculos", "papel": "secundaria (placebo)", "familia": "bky",
     "desc": "placebo: vínculos de generalistas (225125, 225142, 225170)", "curto": "vínculos de generalistas",
     "unidade": "vínculos por 10 mil hab. (Censo 2022)", "e7": "F3.P1"},
]
IDS = [o["id"] for o in OUTCOMES]
SPEC = {o["id"]: o for o in OUTCOMES}
FIGURAS = ("B1", "B2", "B3")

CONTRASTE = ("ATT da chegada do 1º médico do PMM-E ao município (Callaway-Sant'Anna, município x mês, controles "
             "nunca tratados e ainda não tratados) sob tendências paralelas; não é efeito da bolsa, nem do incentivo "
             "marginal, nem da participação no PMM-E como política")

DESVIOS = [
    {"data": DATA_EXECUCAO, "tipo": "esclarecimento", "item": "coorte mensal",
     "descricao": "o protocolo 60 fixa o mês de início do 1º médico como tratamento; o D2 agrupava as chegadas em "
                  "trimestres. Aqui g = mês da chegada (base g − 1 = mês anterior à chegada). O portão de coortes "
                  "leva as chegadas mensais ao trimestre pela regra do D2 e confere datas e contagens."},
    {"data": DATA_EXECUCAO, "tipo": "esclarecimento", "item": "amostra",
     "descricao": "U (IVS oficial a08 e população 2022 > 0) com célula em algum ciclo (1 a 3). Município da lista "
                  "nominal sem célula nos ciclos 1 ou 2 (fora da amostra do D2) não é coorte do D2 nem pode ser "
                  "controle, porque recebeu médico: fica fora e é contado no resumo."},
    {"data": DATA_EXECUCAO, "tipo": "esclarecimento", "item": "ciclo 3 nos controles",
     "descricao": "a lista de ativos de 11/09/2026 (só ciclo, co_ibge e dt_inicio_atividade lidos) mostra o início do "
                  "ciclo 3 em 202608 (e 202609). O município sem chegada dos ciclos 1 e 2 na lista nominal deixa de "
                  "ser controle a partir do 1º início registrado na lista de ativos, de qualquer ciclo, e não forma "
                  "coorte (protocolo: controles 'inclusive o ciclo 3 antes do início')."},
    {"data": DATA_EXECUCAO, "tipo": "esclarecimento", "item": "B3: quem é subtraído",
     "descricao": "subtraem-se, em todos os meses, as horas SUS (ambulatorial + hospitalar, TP_SUS_NAO_SUS = 'S') em "
                  "CBO-alvo dos médicos do PMM-E ligados ao CNES pela regra D1 da X1 (ciclos 1 a 3), nos vínculos em "
                  "estabelecimento do próprio município da unidade. O conjunto de pessoas é fixo: subtrair só depois "
                  "do início criaria uma queda mecânica igual às horas que o médico já tinha no município antes de "
                  "entrar no programa (45-51% já estavam lá, X1). Médico não ligado não é subtraído (nada é "
                  "imputado); vínculo ligado com hora em branco deixa B3 ausente naquele mês."},
    {"data": DATA_EXECUCAO, "tipo": "esclarecimento", "item": "B4",
     "descricao": "coluna horas_totais do a09: ambulatorial + hospitalar + outras, todos os vínculos (SUS e não SUS) "
                  "das CBO-alvo; ausente se algum vínculo tem campo de hora em branco."},
    {"data": DATA_EXECUCAO, "tipo": "esclarecimento", "item": "regras de leitura",
     "descricao": "'sobe' = ATT médio do pós > 0 com p de Holm < 0,05 (B1, B2); 'pré passa' = p do Wald do pré >= "
                  "0,05; 'ruptura >= 1' = ponto de ruptura de Δ^RM >= 1 no teste condicional e no híbrido. 'B3 cai' "
                  "= ATT < 0 com q BKY < 0,05; 'B3 não se distingue de zero' = q BKY >= 0,05."},
    {"data": DATA_EXECUCAO, "tipo": "esclarecimento", "item": "Rambachan-Roth",
     "descricao": "β = θ(e) de e = −6..−2 (5 do pré) e 0..6 (7 do pós); Σ = covariância analítica das funções de "
                  "influência (IF'IF/N²), como no protocolo 59; alvo = média do pós. Ruptura por bisseção em M̄ ∈ "
                  "[0; 4], tolerância 0,01."},
]


class FalhaValidacao(RuntimeError):
    """Portão ou validação obrigatória falhou: o script para sem gravar."""


rotulo = K1M.rotulo
sha256 = K1M.sha256
_gravar_json = K1M._gravar_json


# ---------------------------------------------------------------------------
# 1. Amostra, chegadas e índices de coorte
# ---------------------------------------------------------------------------

def ler_amostra(base: pd.DataFrame) -> tuple[pd.Index, dict]:
    """U com célula em algum ciclo (1 a 3)."""
    vm = pd.read_parquet(ARQ_VM, columns=["ciclo", "co_ibge"])
    vm["co_ibge"] = K1M._ibge6(vm["co_ibge"])
    por_ciclo = {int(c): set(g["co_ibge"]) for c, g in vm.groupby("ciclo")}
    cods = set(vm["co_ibge"])
    fora = sorted(cods - set(base.index))
    return pd.Index(sorted(cods & set(base.index)), name="co_ibge"), {
        "municipios_com_celula_algum_ciclo": len(cods), "fora_de_U": fora,
        "municipios_com_celula_por_ciclo": {str(k): len(v) for k, v in sorted(por_ciclo.items())},
        "so_ciclo_3_em_U": len((por_ciclo.get(3, set()) - por_ciclo.get(1, set()) - por_ciclo.get(2, set()))
                               & set(base.index))}


def ler_inicio_ativos() -> tuple[pd.Series, dict]:
    """1º início registrado por município na lista de ativos (qualquer ciclo); só três colunas lidas."""
    with zipfile.ZipFile(ATIVOS_ZIP) as z:
        nomes = [n for n in z.namelist() if n.lower().endswith(".csv")]
        if len(nomes) != 1:
            raise FalhaValidacao(f"esperado um CSV em {rotulo(ATIVOS_ZIP)}")
        a = pd.read_csv(io.BytesIO(z.read(nomes[0])), sep=";", dtype=str, encoding="latin1",
                        usecols=COLUNAS_ATIVOS)
    a["co_ibge"] = K1M._ibge6(a["co_ibge"])
    a["comp"] = pd.to_datetime(a["dt_inicio_atividade"].str.strip(), format="%d/%m/%Y", errors="raise").dt.strftime("%Y%m")
    por_ciclo = {str(c): {k: int(v) for k, v in g["comp"].value_counts().sort_index().items()}
                 for c, g in a.groupby("ciclo")}
    return a.groupby("co_ibge")["comp"].min(), {"registros": int(len(a)), "inicios_por_ciclo_e_mes": por_ciclo,
                                                "colunas_lidas": COLUNAS_ATIVOS, "membro_zip": nomes[0]}


def indices(chegadas: pd.DataFrame, inicio_ativos: pd.Series, amostra: pd.Index
            ) -> tuple[np.ndarray, list[int], dict, np.ndarray]:
    """G por município: índice do mês da chegada (coorte) para os tratados da lista nominal, −1 para os demais.

    `saida`: para quem não é coorte, o índice do 1º início na lista de ativos (qualquer ciclo) até 202608, −1 se não
    há. A partir desse mês o município deixa de ser controle (`censurar`); ele nunca entra numa coorte. Não se usa G
    para isso porque `att_gt` do D2 trata como coorte g toda unidade com G == g.
    """
    pos = {m: i for i, m in enumerate(MESES)}
    G = np.full(len(amostra), -1, dtype=int)
    saida = np.full(len(amostra), -1, dtype=int)
    tratado = np.zeros(len(amostra), dtype=bool)
    censurado = np.zeros(len(amostra), dtype=bool)
    ch = chegadas.reindex(amostra)["chegada"]
    ini = inicio_ativos.reindex(amostra)
    for i, (c, a) in enumerate(zip(ch.to_numpy(), ini.to_numpy())):
        if isinstance(c, str):
            if c > MESES[-1]:
                continue
            if c not in pos or pos[c] < 1:
                raise FalhaValidacao(f"chegada {c} sem mês-base no painel")
            G[i] = pos[c]
            tratado[i] = True
        elif isinstance(a, str) and a <= MESES[-1]:
            if a not in pos:
                raise FalhaValidacao(f"início {a} antes do painel")
            saida[i] = pos[a]
            censurado[i] = True
    coortes = sorted({int(g) for g in G[tratado]})
    info = {"n_tratados": int(tratado.sum()), "n_controles_censurados": int(censurado.sum()),
            "n_nunca_tratados_no_horizonte": int(((G < 0) & ~censurado).sum()),
            "controles_censurados_por_mes": {MESES[s]: int((saida == s).sum()) for s in sorted(set(saida[censurado]))},
            "coortes_mensais": {MESES[g]: int((G == g).sum()) for g in coortes}}
    return G, coortes, info, saida


def censurar(Y: np.ndarray, saida: np.ndarray) -> np.ndarray:
    """Tira dos controles, a partir do mês de saída, quem tem início fora das coortes (ciclo 3 etc.).

    Com Y_t ausente para t >= saída, `att_gt` só usa a unidade como controle quando t e a base b são anteriores à
    saída: é a regra 'ainda não tratado' (G > max(t, b)). Não é dado ausente da fonte nem imputação: a série
    observada só deixa de entrar na comparação.
    """
    Y = Y.copy()
    for i in np.flatnonzero(saida >= 0):
        Y[i, saida[i]:] = np.nan
    return Y


def portao_coortes(base: pd.DataFrame, amostra: pd.Index, chegadas: pd.DataFrame) -> dict:
    """Portão 1: coortes do D2 refeitas e conferidas com K_D2_resumo.json; chegadas deste bloco no trimestre."""
    d2 = json.loads(D2_RESUMO.read_text(encoding="utf-8"))
    am_d2, _ = D2M.ler_amostra(base)
    ch_d2, info_d2 = D2M.ler_chegadas(am_d2)
    t = ch_d2[ch_d2["coorte"].notna()]
    refeitas = {c: {"municipios": int(len(g)), "especialistas": int(g["n_especialistas"].sum())}
                for c, g in t.groupby("coorte")}
    # Chegadas deste bloco: tratados da amostra deste bloco, levados ao trimestre pela regra do D2.
    meu = chegadas.reindex(amostra)
    meu = meu[meu["chegada"].notna()]
    trimestre = meu["chegada"].map(D2M.trimestre_inicio)
    deste = {c: {"municipios": int(len(g)), "especialistas": int(g["n_especialistas"].sum())}
             for c, g in meu.assign(tri=trimestre).groupby("tri")}
    mesmas_chegadas = bool(set(meu.index) == set(t.index)
                           and (meu["chegada"].sort_index() == t["chegada"].sort_index()).all())
    ok = {
        "coortes_d2_refeitas_iguais_ao_resumo": refeitas == d2["coortes"],
        "coortes_deste_bloco_iguais_ao_d2": deste == d2["coortes"],
        "mesmos_municipios_e_meses_de_chegada": mesmas_chegadas,
        "n_tratados_igual": int(len(meu)) == int(d2["amostra"]["n_tratados"]),
        "fora_da_amostra_igual": int(info_d2["municipios_com_ativo_fora_da_amostra"])
        == int(d2["amostra"]["municipios_com_ativo_fora_da_amostra"]),
    }
    res = {"referencia": rotulo(D2_RESUMO), "coortes_d2_gravadas": d2["coortes"], "coortes_deste_bloco": deste,
           "conferencias": ok, "aprovado": all(ok.values())}
    if not res["aprovado"]:
        raise FalhaValidacao(f"portão de coortes não reproduz o D2: {ok}")
    return res


# ---------------------------------------------------------------------------
# 2. Outcomes
# ---------------------------------------------------------------------------

def ler_painel(amostra: pd.Index) -> pd.DataFrame:
    cols = ["co_ibge", "competencia", "grupo", "n_vinculos", "horas_sus_semanais", "horas_totais",
            "n_vinculos_horas_ausentes", "natureza_dos_dados"]
    p = pd.read_parquet(PAINEL, columns=cols,
                        filters=[("grupo", "in", ["alvo_pmme", "generalistas"]), ("competencia", ">=", COMP_INI),
                                 ("competencia", "<", LIMITE_EXCLUSIVO)])
    p["co_ibge"] = p["co_ibge"].astype(str)
    p["competencia"] = p["competencia"].astype(str)
    if (p["competencia"] >= LIMITE_EXCLUSIVO).any():
        raise FalhaValidacao("a09 com competência >= 202609")
    if set(p["natureza_dos_dados"].astype(str).str.upper()) != {"EMPIRICO"}:
        raise FalhaValidacao("a09 sem natureza EMPIRICO")
    if sorted(p["competencia"].unique()) != list(MESES):
        raise FalhaValidacao("a09 sem todas as competências 202406–202608")
    if p.duplicated(["co_ibge", "competencia", "grupo"]).any():
        raise FalhaValidacao("a09 com chave repetida")
    return p[p["co_ibge"].isin(set(amostra))].reset_index(drop=True)


def contagem(p: pd.DataFrame, grupo: str, col: str, amostra: pd.Index) -> pd.DataFrame:
    """Município × mês em nível (contagem ou horas); célula ausente na fonte fica NaN."""
    s = p[p["grupo"] == grupo].pivot(index="co_ibge", columns="competencia", values=col)
    return s.apply(pd.to_numeric, errors="coerce").astype(float).reindex(index=amostra, columns=list(MESES))


def cbos_alvo() -> list[str]:
    m = json.loads(MANIF_A09.read_text(encoding="utf-8"))
    cbos = sorted(m["ponte"]["cbos_alvo"])
    if not cbos:
        raise FalhaValidacao("manifesto a09 sem CBO-alvo")
    return cbos


def ler_ligados() -> tuple[set[str], pd.DataFrame, dict]:
    """id_prof dos médicos do PMM-E ligados (regra D1 da X1, todos os ciclos) e registros da X1 por posto."""
    ch = pd.read_parquet(ARQ_CHAVES)
    ch = ch[(ch["origem"] == "X1") & (ch["regra_ligacao"] == REGRA_LIGACAO)]
    x1 = pd.read_parquet(ARQ_X1, columns=["id_medico", "regra_ligacao", "ciclo", "co_ibge", "ligado"])
    x1 = x1[x1["regra_ligacao"] == REGRA_LIGACAO].copy()
    x1["co_ibge"] = K1M._ibge6(x1["co_ibge"])
    lig = set(x1.loc[x1["ligado"] == 1, "id_medico"])
    if set(ch["id_externo"]) != lig:
        raise FalhaValidacao("chaves do a16 (regra D1) diferem dos registros ligados da X1")
    info = {"registros_x1": int(len(x1)), "registros_ligados": int(len(lig)),
            "medicos_distintos_ligados": int(ch["id_prof"].nunique()),
            "registros_por_ciclo": {str(k): int(v) for k, v in x1["ciclo"].value_counts().sort_index().items()},
            "ligados_por_ciclo": {str(k): int(v) for k, v in
                                  x1.loc[x1["ligado"] == 1, "ciclo"].value_counts().sort_index().items()}}
    return set(ch["id_prof"]), x1, info


def horas_ligados(ids: set[str], cbos: list[str], amostra: pd.Index) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Horas SUS (amb + hosp, TP_SUS_NAO_SUS = 'S') em CBO-alvo dos ligados, por município do estabelecimento × mês.

    Competência lida sem vínculo ligado = 0 observado; vínculo com hora em branco deixa a célula NaN (nunca zero).
    """
    v = pd.read_parquet(ARQ_VINC, columns=["id_prof", "competencia", "co_municipio", "co_cbo", "tp_sus_nao_sus",
                                           "qt_ch_ambulatorial", "qt_ch_hosp_sus"])
    v["competencia"] = v["competencia"].astype(str)
    if (v["competencia"] >= LIMITE_EXCLUSIVO).any() or not set(v["competencia"]) <= set(MESES):
        raise FalhaValidacao("a16 com competência fora de 202406–202608")
    a16 = json.loads(MANIF_A16.read_text(encoding="utf-8"))
    if a16.get("competencias_nao_obtidas") or sorted(a16["competencias_obtidas"]) != list(MESES):
        raise FalhaValidacao("a16 sem todas as competências: zero não seria observado")
    v = v[v["id_prof"].astype(str).isin(ids) & v["co_cbo"].astype(str).isin(cbos)
          & (v["tp_sus_nao_sus"].astype(str) == "S")].copy()
    v["co_municipio"] = v["co_municipio"].astype(str)
    h = v["qt_ch_ambulatorial"].astype("Float64") + v["qt_ch_hosp_sus"].astype("Float64")
    v["h"] = h.astype(float)
    v["ausente"] = v["h"].isna().astype(int)
    g = v.groupby(["co_municipio", "competencia"]).agg(h=("h", "sum"), ausente=("ausente", "sum"),
                                                       n=("h", "size"), medicos=("id_prof", "nunique"))
    S = g["h"].unstack().reindex(index=amostra, columns=list(MESES)).fillna(0.0)
    aus = g["ausente"].unstack().reindex(index=amostra, columns=list(MESES)).fillna(0)
    S = S.mask(aus > 0)
    med = g["medicos"].unstack().reindex(index=amostra, columns=list(MESES)).fillna(0)
    info = {"vinculos_ligados_sus_cbo_alvo": int(len(v)), "vinculos_com_hora_em_branco": int(v["ausente"].sum()),
            "vinculos_fora_da_amostra": int((~v["co_municipio"].isin(set(amostra))).sum()),
            "celulas_municipio_mes_com_subtracao": int((S.fillna(0) > 0).to_numpy().sum())}
    return S, med, info


def portao_definicoes(p: pd.DataFrame, base: pd.DataFrame, amostra: pd.Index, niveis: dict) -> dict:
    """Portão 2: B1 e B2 (nível ÷ população) iguais a F3.1 e F3.3 do E7 em 202506, município a município."""
    pop = base.loc[amostra, ["s_mil", "populacao_2022"]].rename_axis("co_ibge").reset_index()
    res = {"mes": MES_PORTAO_DEFINICOES, "municipios": int(len(amostra))}
    ok = True
    for oid, fid in (("B1", "F3.1"), ("B2", "F3.3")):
        spec = next(c for c in E7.CATALOGO if c["id"] == fid)
        s = E7.serie_outcome(p[p["competencia"] == MES_PORTAO_DEFINICOES], spec, pop)
        ref = s.set_index("co_ibge")["y"].reindex(amostra).to_numpy(float)
        pp = base.loc[amostra, "populacao_2022"].to_numpy(float)
        meu = niveis[oid][MES_PORTAO_DEFINICOES].to_numpy(float) / pp * ESCALA_HAB
        mesmo_na = bool((np.isnan(ref) == np.isnan(meu)).all())
        dif = float(np.nanmax(np.abs(ref - meu))) if np.isfinite(ref).any() else 0.0
        tot_ref = float(np.nansum(ref * pp / ESCALA_HAB))
        tot_meu = float(np.nansum(niveis[oid][MES_PORTAO_DEFINICOES].to_numpy(float)))
        r = {"outcome_e7": fid, "dif_max_por_10mil": dif, "mesmos_ausentes": mesmo_na,
             "ausentes": int(np.isnan(meu).sum()), "total_e7": tot_ref, "total_deste_bloco": tot_meu,
             "aprovado": bool(mesmo_na and dif <= TOL_PORTAO and abs(tot_ref - tot_meu) <= 1e-6 * max(1, tot_ref))}
        ok &= r["aprovado"]
        res[oid] = r
    res["aprovado"] = bool(ok)
    if not ok:
        raise FalhaValidacao(f"portão de definições: B1/B2 não reproduzem F3.1/F3.3 do E7 em {MES_PORTAO_DEFINICOES}: {res}")
    return res


# ---------------------------------------------------------------------------
# 3. Estimação
# ---------------------------------------------------------------------------

def sensibilidade_rm(theta: np.ndarray, IFe: np.ndarray, es: np.ndarray) -> list[dict]:
    """Δ^RM na média do pós (e = 0..6) com β do pré e = −6..−2; condicional e híbrido; ruptura."""
    N = IFe.shape[0]
    pre = [e for e in range(E_MIN, -1) if e <= -2]
    pos = list(range(0, E_MAX + 1))
    idx = [int(np.flatnonzero(es == e)[0]) for e in pre + pos]
    beta = theta[idx]
    psi = IFe[:, idx]
    if not (np.isfinite(beta).all() and np.isfinite(psi).all()):
        return [{"medida": "RM_nao_calculado", "nota": "θ(e) ausente na janela"}]
    Sig = psi.T @ psi / N ** 2
    Sig = (Sig + Sig.T) / 2
    Tp, Tq = len(pre), len(pos)
    l = np.ones(Tq) / Tq
    est = float(l @ beta[Tp:])
    u = math.sqrt(Sig[Tp, Tp])
    linhas = [{"medida": "RM_descritivo_pre", "valor": H.max_primeira_diferenca_pre(beta, Tp) / u,
               "nota": f"maior |1ª diferença| do pré ÷ u (EP analítico de θ(0) = {u:.6g})"}]
    for metodo in METODOS_RM:
        cache: dict[float, tuple[float, float]] = {}

        def ic(mb: float) -> tuple[float, float]:
            k = round(mb, 6)
            if k not in cache:
                r = H.ic_rm(beta, Sig, Tp, Tq, l, mb, ALFA, metodo=metodo)
                cache[k] = (r["ic_inf"], r["ic_sup"])
            return cache[k]

        for mb in GRADE_RM:
            lo, hi = ic(mb)
            ids = H.conjunto_identificado_rm(beta, Tp, Tq, l, mb)
            linhas.append({"medida": f"RM_{metodo}", "Mbar": mb, "valor": est, "ic95_inf": lo, "ic95_sup": hi,
                           "nota": (f"IC robusto (envelope dos poliedros); conjunto identificado "
                                    f"[{ids[0]:.6g}; {ids[1]:.6g}]" if ids else "conjunto identificado vazio")
                           + ("; exclui zero" if H.exclui_zero(lo, hi) else "; inclui zero")})
        br = H.ruptura(ic, MAX_RM, TOL_RM)
        linhas.append({"medida": f"RM_{metodo}_ruptura", "valor": br["ruptura"],
                       "nota": f"maior M̄ em [0; {MAX_RM:g}] com IC que exclui zero; {br['censura'] or 'interior'}"})
    return linhas


def estimar(Y: np.ndarray, G: np.ndarray, coortes: list[int], xi: np.ndarray) -> dict:
    r = D2M.estimar_cs(Y, G, coortes, xi, e_min=E_MIN, e_max=E_MAX)
    tab, IF = D2M.att_gt(Y, G, coortes, e_min=E_MIN, e_max=E_MAX)
    ev, IFe = D2M.agregar_evento(tab, IF, G, e_min=E_MIN, e_max=E_MAX)
    th = ev["theta"].to_numpy(float)
    if not np.allclose(th, r["evento"]["theta"].to_numpy(float), equal_nan=True, rtol=0, atol=0):
        raise FalhaValidacao("θ(e) da agregação difere do estimar_cs")
    r["rm"] = sensibilidade_rm(th, IFe, ev["e"].to_numpy())
    r["n_controles_por_e"] = {int(e): int(tab.loc[tab["e"] == e, "n_controles"].min()) if (tab["e"] == e).any() else 0
                              for e in range(E_MIN, E_MAX + 1)}
    return r


COLUNAS_EST = ["natureza_dos_dados", "estatuto", "outcome_id", "descricao_outcome", "papel", "medida", "e", "Mbar",
               "valor", "ep", "ep_analitico", "ic95_inf", "ic95_sup", "banda_unif_inf", "banda_unif_sup", "p_valor",
               "p_holm", "q_bky", "gl", "n_coortes", "n_tratados", "n_municipios", "unidade", "contraste", "nota"]


def linhas_outcome(oid: str, r: dict, G: np.ndarray, coortes: list[int]) -> list[dict]:
    o = SPEC[oid]
    base = {"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "outcome_id": oid, "descricao_outcome": o["desc"],
            "papel": o["papel"], "unidade": o["unidade"], "contraste": CONTRASTE, "n_municipios": int(len(G))}
    out = []
    for rec in r["evento"].to_dict("records"):
        out.append({**base, "medida": "att_e", "e": rec["e"], "valor": rec["theta"], "ep": rec["ep"],
                    "ep_analitico": rec["ep_analitico"], "ic95_inf": rec["ic95_inf"], "ic95_sup": rec["ic95_sup"],
                    "banda_unif_inf": rec["banda_unif_inf"], "banda_unif_sup": rec["banda_unif_sup"],
                    "p_valor": rec["p_valor"], "n_coortes": rec["n_coortes"], "n_tratados": rec["n_tratados"],
                    "nota": rec["nota"] or ("base universal b = g − 1" if rec["referencia"] else
                                            f"controles (mínimo entre coortes) = {r['n_controles_por_e'][rec['e']]}")})
    pos = r["pos"]
    n_trat = int(sum((G == g).sum() for g in coortes))
    out.append({**base, "medida": "att_pos_medio", "valor": pos["att"], "ep": pos["ep"],
                "ep_analitico": pos["ep_analitico"], "ic95_inf": pos["ic95_inf"], "ic95_sup": pos["ic95_sup"],
                "p_valor": pos["p_valor"], "n_coortes": len(coortes), "n_tratados": n_trat,
                "nota": f"média de θ(e) em e = {pos['e_min']}..{pos['e_max']} ({pos['n_e']} tempos de evento); "
                        "EP bootstrap (Mammen, cluster no município)"})
    pt = r["pre"]
    out.append({**base, "medida": "pretendencia_wald", "valor": pt["wald"], "gl": pt["gl"], "p_valor": pt["p_wald"],
                "n_coortes": len(coortes), "n_tratados": n_trat,
                "nota": f"Wald conjunto de θ(e) = 0 em e = {E_MIN}..−2 ({pt['k']} tempos), covariância IF'IF/N²"})
    out.append({**base, "medida": "pretendencia_supt", "p_valor": pt["p_supt"], "n_coortes": len(coortes),
                "n_tratados": n_trat, "nota": "p do sup-t do bootstrap para θ(e) = 0 em todo o pré"})
    for x in r["rm"]:
        out.append({**base, "n_coortes": len(coortes), "n_tratados": n_trat, **x})
    return out


def aplicar_multiplos(est: pd.DataFrame) -> pd.DataFrame:
    est = est.copy()
    est["p_holm"] = np.nan
    est["q_bky"] = np.nan
    pos = est["medida"] == "att_pos_medio"
    for fam, col, fn in (("holm", "p_holm", L.holm), ("bky", "q_bky", L.qvalores_bky)):
        m = pos & est["outcome_id"].map(lambda o: SPEC[o]["familia"] == fam)
        est.loc[m, col] = fn(est.loc[m, "p_valor"].to_numpy(float))
    return est


# ---------------------------------------------------------------------------
# 4. Ligação (B3)
# ---------------------------------------------------------------------------

def tabela_ligacao(x1: pd.DataFrame, amostra: pd.Index, G: np.ndarray, coortes: list[int], b2: pd.DataFrame,
                   S: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Por município tratado: registros dos ciclos 1 e 2 da X1 no posto, não ligados, e parcela das horas
    subtraídas (Σ subtraído ÷ Σ B2 em nível) no pré (e = −6..−1) e no pós (e = 0..6)."""
    x = x1[x1["ciclo"].astype(str).isin(CICLOS_TRATAMENTO)]
    reg = x.groupby("co_ibge").agg(n_registros=("ligado", "size"), n_ligados=("ligado", "sum"))
    linhas = []
    B = b2.to_numpy(float)
    Sm = S.to_numpy(float)
    for i, m in enumerate(amostra):
        if G[i] < 0 or G[i] not in coortes:
            continue
        g = G[i]
        rr = reg.loc[m] if m in reg.index else None
        n = int(rr["n_registros"]) if rr is not None else 0
        nl = int(rr["n_ligados"]) if rr is not None else 0
        jan = {"pre": range(max(0, g + E_MIN), g), "pos": range(g, min(len(MESES), g + E_MAX + 1))}
        rec = {"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "co_ibge": m, "mes_chegada": MESES[g],
               "n_registros_x1_ciclos_1_2": n, "n_ligados": nl, "n_nao_ligados": n - nl,
               "fracao_nao_ligados": (n - nl) / n if n else np.nan}
        for k, cols in jan.items():
            cols = list(cols)
            s, b = Sm[i, cols], B[i, cols]
            ok = np.isfinite(s) & np.isfinite(b)
            rec[f"horas_subtraidas_{k}"] = float(s[ok].sum()) if ok.any() else np.nan
            rec[f"horas_b2_{k}"] = float(b[ok].sum()) if ok.any() else np.nan
            rec[f"parcela_subtraida_{k}"] = (float(s[ok].sum() / b[ok].sum()) if ok.any() and b[ok].sum() > 0
                                             else np.nan)
            rec[f"meses_{k}"] = int(ok.sum())
        rec["nota"] = ("" if n else "nenhum registro da X1 dos ciclos 1-2 com posto no município (chegada da lista "
                                    "nominal; o médico pode estar só na lista de agosto ou ter outro co_ibge na X1)")
        linhas.append(rec)
    t = pd.DataFrame(linhas)
    com = t[t["n_registros_x1_ciclos_1_2"] > 0]

    def q(s):
        s = s.dropna()
        return {"media": float(s.mean()), "mediana": float(s.median()), "p90": float(s.quantile(0.9)),
                "max": float(s.max())} if len(s) else {}

    resumo = {
        "municipios_tratados": int(len(t)),
        "municipios_sem_registro_x1": int((t["n_registros_x1_ciclos_1_2"] == 0).sum()),
        "registros_x1_ciclos_1_2_nos_tratados": int(com["n_registros_x1_ciclos_1_2"].sum()),
        "nao_ligados_nos_tratados": int(com["n_nao_ligados"].sum()),
        "fracao_nao_ligados_agregada": float(com["n_nao_ligados"].sum() / com["n_registros_x1_ciclos_1_2"].sum())
        if len(com) else np.nan,
        "municipios_com_algum_nao_ligado": int((com["n_nao_ligados"] > 0).sum()),
        "municipios_com_todos_nao_ligados": int((com["n_ligados"] == 0).sum()),
        "fracao_nao_ligados_por_municipio": q(com["fracao_nao_ligados"]),
        "parcela_subtraida_agregada_pre": float(t["horas_subtraidas_pre"].sum() / t["horas_b2_pre"].sum()),
        "parcela_subtraida_agregada_pos": float(t["horas_subtraidas_pos"].sum() / t["horas_b2_pos"].sum()),
        "parcela_subtraida_por_municipio_pre": q(t["parcela_subtraida_pre"]),
        "parcela_subtraida_por_municipio_pos": q(t["parcela_subtraida_pos"]),
        "definicao": "registros = linhas da X1 (regra D1), ciclos 1 e 2, com posto no município; parcela = Σ horas "
                     "SUS subtraídas ÷ Σ horas SUS das CBO-alvo (B2 em nível) nos meses com os dois observados",
    }
    return t, resumo


# ---------------------------------------------------------------------------
# 5. Figuras
# ---------------------------------------------------------------------------

def como_ler(oid: str) -> str:
    o = SPEC[oid]
    extra = {"B1": "",
             "B2": "",
             "B3": " Aqui saem as horas dos médicos do PMM-E ligados ao CNES: sobra o que os outros especialistas "
                   "cadastram. Ponto abaixo de zero no pós seria sinal de que eles perderam horas."}[oid]
    return ("COMO LER. Cada ponto é quanto a mudança em " + o["curto"] + ", desde o mês antes da chegada (−1, zero "
            "por construção), foi maior (acima de zero) ou menor (abaixo) nos municípios que receberam o 1º "
            "médico do PMM-E do que nos que ainda não tinham recebido. Antes do 0 os pontos deveriam ficar perto de "
            "zero. Barra = IC 95% do mês; faixa = banda de 95% para todos os meses juntos." + extra +
            " É associação da chegada sob tendências paralelas, não efeito da bolsa; vínculo cadastrado não é "
            "presença.")


def figura(oid: str, est: pd.DataFrame, caminho: Path) -> dict:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    S = K1M
    e = est[(est["outcome_id"] == oid) & (est["medida"] == "att_e")].sort_values("e")
    x = e["e"].to_numpy(int)
    th = e["valor"].to_numpy(float)
    lo, hi = e["ic95_inf"].to_numpy(float), e["ic95_sup"].to_numpy(float)
    bl, bh = e["banda_unif_inf"].to_numpy(float), e["banda_unif_sup"].to_numpy(float)
    g = est[est["outcome_id"] == oid].set_index("medida")
    pos, pre = g.loc["att_pos_medio"], g.loc["pretendencia_wald"]
    rup = {m: g.loc[f"RM_{m}_ruptura", "valor"] if f"RM_{m}_ruptura" in g.index else np.nan for m in METODOS_RM}
    fig = plt.figure(figsize=(13.33, 7.5), facecolor=S.SUPERFICIE)
    ax = fig.add_axes([0.09, 0.39, 0.88, 0.42])
    ax.set_facecolor(S.SUPERFICIE)
    ax.axvspan(-0.5, E_MAX + 0.5, color="#efece4", linewidth=0, zorder=0)
    okb = np.isfinite(bl) & np.isfinite(bh)
    ax.fill_between(x[okb], bl[okb], bh[okb], color=S.COR_IC, alpha=0.15, linewidth=0, step="mid", zorder=1)
    ax.axhline(0, color=S.TINTA_2, linewidth=1.0)
    ax.axvline(-0.5, color=S.COR_ATO, linestyle="--", linewidth=1.2)
    ok = np.isfinite(lo) & np.isfinite(hi)
    ax.errorbar(x[ok], th[ok], yerr=[th[ok] - lo[ok], hi[ok] - th[ok]], fmt="none", ecolor=S.COR_IC,
                elinewidth=2.0, alpha=0.8, zorder=2)
    ref = x == -1
    ax.plot(x[~ref], th[~ref], "o", color=S.COR_PONTO, markersize=9, zorder=3)
    ax.plot(x[ref], th[ref], "s", color=S.TINTA, markersize=10, zorder=4)
    fmt = lambda v, c=2: _n(v, c)  # noqa: E731
    ax.set_title(f"Média depois da chegada (meses 0 a 6) = {fmt(pos['valor'])} [IC 95%: {fmt(pos['ic95_inf'])}; "
                 f"{fmt(pos['ic95_sup'])}], {_p_igual(pos['p_valor'])}\nteste do pré (meses −6 a −2): "
                 f"{_p_igual(pre['p_valor'])}  |  ruptura M̄ de Rambachan–Roth = {_n(rup['condicional'], 2, sinal=False)}",
                 fontsize=13, color=S.TINTA, loc="left")
    ax.set_xlabel("meses desde a chegada do 1º médico do PMM-E (0 = mês da chegada)", fontsize=14, color=S.TINTA_2)
    ax.set_ylabel(f"diferença na mudança desde o mês −1\n({SPEC[oid]['unidade']})", fontsize=13, color=S.TINTA_2)
    ax.set_xticks(range(E_MIN, E_MAX + 1))
    ax.grid(axis="y", alpha=0.3, linewidth=0.7)
    ax.tick_params(colors=S.TINTA_2, labelsize=13)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",").replace("-", "−")))
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}".replace("-", "−")))
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    handles = [Line2D([], [], marker="o", linestyle="", color=S.COR_PONTO, markersize=9,
                      label="diferença no mês (chegou − ainda não)"),
               Line2D([], [], color=S.COR_IC, linewidth=2, label="IC 95% do mês"),
               Patch(color=S.COR_IC, alpha=0.15, label="banda de 95% (todos os meses)"),
               Line2D([], [], marker="s", linestyle="", color=S.TINTA, markersize=10, label="mês −1 = base (zero)"),
               Patch(color="#efece4", label="a partir da chegada")]
    fig.legend(handles=handles, loc="center", ncol=3, fontsize=12, frameon=False, bbox_to_anchor=(0.5, 0.255))
    fig.suptitle(f"{oid} — {SPEC[oid]['curto']}, por 10 mil hab.", fontsize=18, color=S.TINTA, x=0.09, y=0.965,
                 ha="left")
    texto = "\n".join(textwrap.wrap(como_ler(oid), 150))
    fig.text(0.02, 0.02, texto, fontsize=11.5, color=S.TINTA_2, va="bottom", ha="left", linespacing=1.3,
             parse_math=False)
    fig.savefig(caminho, dpi=150, facecolor=S.SUPERFICIE)
    plt.close(fig)
    return {"arquivo": rotulo(caminho), "outcome_id": oid, "sha256": sha256(caminho), "como_ler": como_ler(oid)}


# ---------------------------------------------------------------------------
# 6. Doc 57k (blocos entre marcadores)
# ---------------------------------------------------------------------------

def _n(v, casas: int = 2, sinal: bool = True) -> str:
    if v is None or (isinstance(v, float) and not math.isfinite(v)) or pd.isna(v):
        return "—"
    s = f"{float(v):+.{casas}f}" if sinal else f"{float(v):.{casas}f}"
    return s.replace("-", "−").replace(".", ",")


def _p(v) -> str:
    if v is None or pd.isna(v):
        return "—"
    return "< 0,001" if float(v) < 0.001 else f"{float(v):.3f}".replace(".", ",")


def _p_igual(v) -> str:
    """'p = 0,123' ou 'p < 0,001'."""
    t = _p(v)
    return f"p {t}" if t.startswith("<") else f"p = {t}"


def _pct(v) -> str:
    return "—" if v is None or pd.isna(v) else f"{100 * float(v):.1f}%".replace(".", ",")


def _g(est: pd.DataFrame, oid: str) -> pd.DataFrame:
    return est[est["outcome_id"] == oid].set_index("medida", drop=False)


def _rup(g: pd.DataFrame, metodo: str) -> float:
    k = f"RM_{metodo}_ruptura"
    return float(g.loc[k, "valor"]) if k in g.index else float("nan")


def classificar(est: pd.DataFrame) -> dict:
    """Leitura pré-registrada do protocolo 60, parte B (regras no DESVIOS 'regras de leitura')."""
    c = {}
    for oid in IDS:
        g = _g(est, oid)
        pos, pre = g.loc["att_pos_medio"], g.loc["pretendencia_wald"]
        p_aj = pos["p_holm"] if SPEC[oid]["familia"] == "holm" else pos["q_bky"]
        rup = min(_rup(g, "condicional"), _rup(g, "hibrido"))
        c[oid] = {"att": float(pos["valor"]), "p_ajustado": float(p_aj), "pre_passa": bool(pre["p_valor"] >= ALFA),
                  "ruptura_min": rup, "significativo": bool(p_aj < ALFA),
                  "sobe": bool(pos["valor"] > 0 and p_aj < ALFA), "cai": bool(pos["valor"] < 0 and p_aj < ALFA)}
        c[oid]["sobe_com_diagnosticos"] = bool(c[oid]["sobe"] and c[oid]["pre_passa"] and rup >= 1.0)
    return c


ROTULO_PAPEL = {"primaria": "primária", "secundaria": "secundária", "secundaria (placebo)": "secundária (placebo)"}
ROTULO_METODO = {"condicional": "condicional", "hibrido": "híbrido"}


def nota_pre(est: pd.DataFrame) -> str:
    """Descritivo: outcomes com algum θ(e) do pré cujo IC 95% exclui zero (o Wald conjunto pode não rejeitar)."""
    casos = []
    for oid in IDS:
        g = est[(est["outcome_id"] == oid) & (est["medida"] == "att_e") & (est["e"] <= -2)].sort_values("e")
        fora = g[(g["ic95_inf"] > 0) | (g["ic95_sup"] < 0)]
        if len(fora):
            casos.append(f"{oid} ({len(fora)} de {len(g)} meses; θ(−6) = {_n(g['valor'].iloc[0])})")
    if not casos:
        return ""
    return (" No pré, há meses com IC que exclui zero em " + "; ".join(casos) + ": a diferença já vinha mudando "
            "antes da chegada, em relação ao mês-base, e o teste conjunto do pré tem pouco poder contra uma tendência "
            "suave. É mais uma razão para não ler a diferença do pós como causada pela chegada.")


def nota_rm_nao_monotono(est: pd.DataFrame) -> str:
    """Outcomes em que algum M̄ > 0 da grade exclui zero com ruptura 0 (o IC em M̄ = 0 já inclui zero).

    A ruptura segue `honestdid_lib.ruptura` (protocolo 59), que supõe IC monotônico em M̄; o teste de ARP pode dar
    IC mais largo em M̄ = 0 que em M̄ = 0,5 (doc 57h). A regra de leitura usa a ruptura como definida; isto só relata.
    """
    casos = []
    for oid in IDS:
        g = est[est["outcome_id"] == oid]
        for met in METODOS_RM:
            r = g[g["medida"] == f"RM_{met}_ruptura"]
            if not len(r) or float(r["valor"].iloc[0]) > 0:
                continue
            s = g[(g["medida"] == f"RM_{met}") & (g["Mbar"] > 0)]
            exc = s[(s["ic95_inf"] > 0) | (s["ic95_sup"] < 0)]
            if len(exc):
                casos.append(f"{oid} ({ROTULO_METODO[met]}: M̄ = " + ", ".join(_n(m, 1, False) for m in exc["Mbar"]) + ")")
    if not casos:
        return ""
    txt = (" Em " + "; ".join(casos) + ", o IC robusto exclui zero em algum M̄ > 0 da grade, embora inclua zero em "
           "M̄ = 0: o teste de Andrews, Roth e Pakes não é monotônico em M̄ (doc 57h). A ruptura fica 0, como a "
           "biblioteca do protocolo 59 a define")
    em_1 = [c.split(" ")[0] for c in casos if _exclui_em(est, c.split(" ")[0], 1.0)]
    return txt + (f"; em M̄ = 1 o IC exclui zero em {', '.join(sorted(set(em_1)))}." if em_1 else
                  "; em M̄ = 1 o IC inclui zero em todos eles.")


def _exclui_em(est: pd.DataFrame, oid: str, mb: float) -> bool:
    s = est[(est["outcome_id"] == oid) & est["medida"].isin([f"RM_{m}" for m in METODOS_RM]) & (est["Mbar"] == mb)]
    return bool(((s["ic95_inf"] > 0) | (s["ic95_sup"] < 0)).any())


def gerar_leitura(est: pd.DataFrame) -> str:
    c = classificar(est)
    frases = []
    nomes = {"B1": "os vínculos de especialistas nas CBO-alvo (B1)", "B2": "as horas SUS desses especialistas (B2)",
             "B3": "as horas SUS dos outros especialistas, sem os do PMM-E (B3)",
             "B4": "as horas totais, SUS e não SUS (B4)", "B5": "os vínculos de generalistas, o placebo (B5)"}
    for oid in IDS:
        x = c[oid]
        aj = "p de Holm" if SPEC[oid]["familia"] == "holm" else "q BKY"
        if x["sobe_com_diagnosticos"]:
            verbo = "ficaram maiores do que nos comparáveis, com pré que passa e ruptura M̄ ≥ 1"
        elif x["sobe"] or x["cai"]:
            lado = "maiores" if x["sobe"] else "menores"
            falta = [t for t, f in (("o pré não passa", not x["pre_passa"]),
                                    ("a ruptura M̄ fica abaixo de 1", not (x["ruptura_min"] >= 1.0))) if f]
            verbo = f"ficaram {lado} do que nos comparáveis" + (f", mas {' e '.join(falta)}" if falta else "")
        else:
            verbo = "não se distinguem do que se vê nos comparáveis"
        t = _p(x["p_ajustado"])
        frases.append(f"{nomes[oid]} {verbo} ({aj} {t if t.startswith('<') else '= ' + t})")
    b1, b2, b3 = c["B1"], c["B2"], c["B3"]
    if b1["sobe_com_diagnosticos"] or b2["sobe_com_diagnosticos"]:
        quais = " e ".join(o for o in ("B1", "B2") if c[o]["sobe_com_diagnosticos"])
        conclusao = (f"Pela leitura pré-registrada, {quais} indica associação da chegada com mais oferta cadastrada "
                     "local.")
    else:
        conclusao = ("Pela leitura pré-registrada, não dá para falar em aumento da oferta cadastrada local: nenhuma "
                     "primária sobe com pré que passa e ruptura M̄ ≥ 1.")
    if b3["cai"]:
        conclusao += " B3 cai: há sinal de deslocamento dos outros especialistas."
    elif not b3["significativo"] and b2["sobe_com_diagnosticos"]:
        conclusao += (" B3 não se distingue de zero e B2 sobe: o ganho vem dos médicos do programa, sem deslocamento "
                      "detectável dos outros especialistas.")
    elif not b3["significativo"]:
        conclusao += " B3 não se distingue de zero: não há sinal detectável de deslocamento dos outros especialistas."
    else:
        conclusao += (" B3 não cai: a mudança das horas dos outros especialistas fica acima da dos comparáveis (sem "
                      "ruptura M̄ ≥ 1), então não há sinal de deslocamento.")
    if c["B5"]["significativo"]:
        conclusao += (" O placebo (B5) também se move, o que sugere que os municípios que recebem médico já mudavam "
                      "por outro motivo.")
    conclusao += nota_pre(est) + nota_rm_nao_monotono(est)
    return ("Depois que o 1º médico do PMM-E começou no município, em média nos meses 0 a 6: " + "; ".join(frases)
            + ". " + conclusao + " Tudo é ATT sob tendências paralelas da chegada, não efeito da bolsa nem da "
            "participação no programa; vínculo cadastrado não é presença.")


def gerar_tabelas_doc(est: pd.DataFrame, lig: pd.DataFrame, resumo: dict) -> dict[str, str]:
    t = {}
    a, co = resumo["amostra"], resumo["coortes"]
    linhas = ["| Item | Valor |", "|---|---|",
              f"| municípios de U com célula em algum ciclo (1 a 3) | {a['municipios_em_U_com_celula']} |",
              f"| fora: tratados da lista nominal sem célula nos ciclos 1 ou 2 | {a['excluidos_tratados_fora_d2']} |",
              f"| amostra (municípios) | {a['n_municipios']} |",
              f"| tratados (1º médico dos ciclos 1 e 2 até {COMP_FIM}) | {co['n_tratados']} |",
              f"| controles que saem no início registrado na lista de ativos (ciclo 3 ou fora da lista nominal) | "
              f"{co['n_controles_censurados']} |",
              f"| nunca tratados no horizonte | {co['n_nunca_tratados_no_horizonte']} |"]
    for m, n in co["controles_censurados_por_mes"].items():
        linhas.append(f"| controles que saem em {m[:4]}-{m[4:]} | {n} |")
    t["amostra"] = "\n".join(linhas)
    linhas = ["| Coorte (mês da chegada) | Municípios |", "|---|---|"]
    for m, n in co["coortes_mensais"].items():
        linhas.append(f"| {m[:4]}-{m[4:]} | {n} |")
    t["coortes"] = "\n".join(linhas)
    p1, p2 = resumo["portoes"]["coortes"], resumo["portoes"]["definicoes"]
    linhas = ["| Portão | Conferência | Resultado |", "|---|---|---|"]
    for c, v in p1["conferencias"].items():
        linhas.append(f"| 1. coortes do D2 | {c.replace('_', ' ')} | {'sim' if v else 'NÃO'} |")
    for oid in ("B1", "B2"):
        r = p2[oid]
        linhas.append(f"| 2. definições ({p2['mes']}) | {oid} = {r['outcome_e7']} do E7: diferença máxima "
                      f"{r['dif_max_por_10mil']:.1e} por 10 mil, ausentes iguais ({r['ausentes']}), total "
                      f"{_n(r['total_deste_bloco'], 0, False)} | {'sim' if r['aprovado'] else 'NÃO'} |")
    linhas.append("")
    linhas.append("| Coorte trimestral do D2 | D2 (municípios / especialistas) | Este bloco |")
    linhas.append("|---|---|---|")
    for c, v in p1["coortes_d2_gravadas"].items():
        w = p1["coortes_deste_bloco"].get(c, {})
        linhas.append(f"| {c[:4]}-{c[4:]} | {v['municipios']} / {v['especialistas']} | "
                      f"{w.get('municipios')} / {w.get('especialistas')} |")
    t["portoes"] = "\n".join(linhas)
    t["leitura"] = gerar_leitura(est)
    linhas = ["| Id | Outcome | Papel | ATT médio do pós (e = 0..6) | IC 95% (bootstrap) | p | p Holm / q BKY | "
              "Pré: Wald (gl), p | Ruptura M̄ (cond. / híbr.) |", "|---|---|---|---|---|---|---|---|---|"]
    for oid in IDS:
        g = _g(est, oid)
        pos, pre = g.loc["att_pos_medio"], g.loc["pretendencia_wald"]
        aj = (f"{_p(pos['p_holm'])} (Holm)" if SPEC[oid]["familia"] == "holm" else f"{_p(pos['q_bky'])} (BKY)")
        linhas.append(f"| {oid} | {SPEC[oid]['desc']} | {ROTULO_PAPEL[SPEC[oid]['papel']]} | {_n(pos['valor'])} | "
                      f"[{_n(pos['ic95_inf'])}; {_n(pos['ic95_sup'])}] | {_p(pos['p_valor'])} | {aj} | "
                      f"{_n(pre['valor'], 1, False)} ({int(pre['gl'])}), {_p(pre['p_valor'])} | "
                      f"{_n(_rup(g, 'condicional'), 2, False)} / {_n(_rup(g, 'hibrido'), 2, False)} |")
    t["principal"] = "\n".join(linhas)
    linhas = ["| Id | Método | " + " | ".join(f"M̄ = {_n(m, 1, False)}" for m in GRADE_RM) + " |",
              "|---|---|" + "---|" * len(GRADE_RM)]
    for oid in IDS:
        g = est[est["outcome_id"] == oid]
        for met in METODOS_RM:
            s = g[g["medida"] == f"RM_{met}"].set_index("Mbar")
            cel = [f"[{_n(s.loc[m, 'ic95_inf'])}; {_n(s.loc[m, 'ic95_sup'])}]" if m in s.index else "—"
                   for m in GRADE_RM]
            linhas.append(f"| {oid} | {ROTULO_METODO[met]} | " + " | ".join(cel) + " |")
    t["rr"] = "\n".join(linhas)
    linhas = ["| e | " + " | ".join(IDS) + " |", "|---|" + "---|" * len(IDS)]
    for e in range(E_MIN, E_MAX + 1):
        cel = []
        for oid in IDS:
            r = est[(est["outcome_id"] == oid) & (est["medida"] == "att_e") & (est["e"] == e)].iloc[0]
            cel.append("0 (base)" if e == -1 else f"{_n(r['valor'])} [{_n(r['ic95_inf'])}; {_n(r['ic95_sup'])}]")
        linhas.append(f"| {e} | " + " | ".join(cel) + " |")
    t["evento"] = "\n".join(linhas)
    lg = resumo["ligacao"]
    fq, pp, pq = lg["fracao_nao_ligados_por_municipio"], lg["parcela_subtraida_por_municipio_pre"], \
        lg["parcela_subtraida_por_municipio_pos"]
    linhas = ["| Item | Valor |", "|---|---|",
              f"| municípios tratados | {lg['municipios_tratados']} |",
              f"| tratados sem registro da X1 dos ciclos 1-2 com posto no município | {lg['municipios_sem_registro_x1']} |",
              f"| registros da X1 (ciclos 1-2) com posto nos tratados / não ligados | "
              f"{lg['registros_x1_ciclos_1_2_nos_tratados']} / {lg['nao_ligados_nos_tratados']} "
              f"({_pct(lg['fracao_nao_ligados_agregada'])}) |",
              f"| municípios com algum não ligado / com todos não ligados | {lg['municipios_com_algum_nao_ligado']} / "
              f"{lg['municipios_com_todos_nao_ligados']} |",
              f"| fração de não ligados por município: média / mediana / p90 / máx. | {_pct(fq.get('media'))} / "
              f"{_pct(fq.get('mediana'))} / {_pct(fq.get('p90'))} / {_pct(fq.get('max'))} |",
              f"| parcela das horas SUS das CBO-alvo subtraída, agregada: pré (e = −6..−1) / pós (e = 0..6) | "
              f"{_pct(lg['parcela_subtraida_agregada_pre'])} / {_pct(lg['parcela_subtraida_agregada_pos'])} |",
              f"| parcela subtraída por município, pré: média / mediana / p90 / máx. | {_pct(pp.get('media'))} / "
              f"{_pct(pp.get('mediana'))} / {_pct(pp.get('p90'))} / {_pct(pp.get('max'))} |",
              f"| parcela subtraída por município, pós: média / mediana / p90 / máx. | {_pct(pq.get('media'))} / "
              f"{_pct(pq.get('mediana'))} / {_pct(pq.get('p90'))} / {_pct(pq.get('max'))} |",
              f"| vínculos ligados SUS em CBO-alvo com hora em branco (B3 ausente no mês) | "
              f"{resumo['b3']['vinculos_com_hora_em_branco']} |"]
    t["ligacao"] = "\n".join(linhas)
    linhas = []
    for f in resumo["figuras"]:
        linhas += [f"**{f['outcome_id']}.** ![{f['outcome_id']}](../../{f['arquivo']})", "",
                   f"Como ler: {f['como_ler'].removeprefix('COMO LER. ')}", ""]
    t["figuras"] = "\n".join(linhas).rstrip()
    linhas = ["| Data | Tipo | Item | Descrição |", "|---|---|---|---|"]
    for dv in resumo["desvios"]:
        linhas.append(f"| {dv['data']} | {dv['tipo']} | {dv['item']} | {dv['descricao']} |")
    t["desvios"] = "\n".join(linhas)
    return t


MARCA = re.compile(r"(<!-- OL:(?P<nome>[A-Za-z0-9_]+):inicio -->\n)(?P<corpo>.*?)(\n<!-- OL:(?P=nome):fim -->)", re.S)


def aplicar_tabelas_doc(texto: str, tabelas: dict[str, str]) -> str:
    def sub(m):
        nome = m.group("nome")
        if nome not in tabelas:
            raise KeyError(f"bloco {nome} não gerado")
        return m.group(1) + tabelas[nome] + m.group(4)
    return MARCA.sub(sub, texto)


def tabelas_no_doc(texto: str) -> dict[str, str]:
    return {m.group("nome"): m.group("corpo") for m in MARCA.finditer(texto)}


def ler_saidas():
    est = pd.read_csv(OUT / NOME_EST, dtype={"outcome_id": str})
    lig = pd.read_csv(OUT / NOME_LIG, dtype={"co_ibge": str})
    resumo = json.loads((OUT / NOME_RESUMO).read_text(encoding="utf-8"))
    return est, lig, resumo


def atualizar_doc() -> None:
    if not DOC.exists():
        print(f"{rotulo(DOC)} não existe: blocos não gravados")
        return
    est, lig, resumo = ler_saidas()
    texto = DOC.read_text(encoding="utf-8")
    tabelas = gerar_tabelas_doc(est, lig, resumo)
    faltam = set(tabelas) - set(tabelas_no_doc(texto))
    if faltam:
        raise FalhaValidacao(f"doc sem marcadores para {sorted(faltam)}")
    DOC.write_text(aplicar_tabelas_doc(texto, tabelas), encoding="utf-8")
    print(f"blocos OL regravados: {rotulo(DOC)}")


# ---------------------------------------------------------------------------
# 7. Execução
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--atualizar-doc", action="store_true")
    args = ap.parse_args(argv)
    if args.atualizar_doc:
        atualizar_doc()
        return 0
    try:
        base, _ = K1M.ler_universo()
        am_total, info_am = ler_amostra(base)
        ch_total, info_ch = D2M.ler_chegadas(am_total)
        am_d2, _ = D2M.ler_amostra(base)
        # Tratado da lista nominal fora da amostra do D2 (sem célula nos ciclos 1-2): nem coorte nem controle.
        excl = sorted(set(ch_total.index[ch_total["chegada"].notna()]) - set(am_d2))
        amostra = am_total.difference(pd.Index(excl))
        chegadas = ch_total.reindex(amostra)
        portao1 = portao_coortes(base, amostra, chegadas)
        inicio_ativos, info_ativos = ler_inicio_ativos()
        G, coortes, info_G, saida = indices(chegadas, inicio_ativos, amostra)
        p = ler_painel(amostra)
        niveis = {oid: contagem(p, SPEC[oid]["grupo"], SPEC[oid]["col"], amostra) for oid in IDS if oid != "B3"}
        portao2 = portao_definicoes(p, base, amostra, niveis)
        # Os dois portões passaram: só agora os outcomes por tempo de evento são construídos.
        ids, x1, info_lig = ler_ligados()
        cbos = cbos_alvo()
        S, _, info_b3 = horas_ligados(ids, cbos, amostra)
        b2 = niveis["B2"]
        viol = (S - b2).to_numpy(float)
        if np.nanmax(np.where(np.isfinite(viol), viol, -np.inf)) > 1e-9:
            raise FalhaValidacao("horas subtraídas maiores que as horas SUS das CBO-alvo do a09 numa célula")
        niveis["B3"] = b2 - S                         # NaN se B2 ou a subtração é ausente
        pop = base.loc[amostra, "populacao_2022"].to_numpy(float)
        xi = D2M.pesos_mammen(B_BOOT, len(amostra), SEMENTE)
        linhas = []
        for oid in IDS:
            Y = censurar(niveis[oid].to_numpy(float) / pop[:, None] * ESCALA_HAB, saida)
            r = estimar(Y, G, coortes, xi)
            linhas += linhas_outcome(oid, r, G, coortes)
            print(f"{oid}: ATT pós {r['pos']['att']:.3f} p={r['pos']['p_valor']:.3f}", flush=True)
        del xi
        lig, resumo_lig = tabela_ligacao(x1, amostra, G, coortes, b2, S)
    except (FalhaValidacao, K1M.FalhaValidacao, D2M.FalhaValidacao) as erro:
        print(f"FALHA DE VALIDAÇÃO (nada gravado): {erro}", file=sys.stderr)
        return 2
    est = aplicar_multiplos(pd.DataFrame(linhas).reindex(columns=COLUNAS_EST))
    OUT.mkdir(parents=True, exist_ok=True)
    est.to_csv(OUT / NOME_EST, index=False)
    lig.to_csv(OUT / NOME_LIG, index=False)
    dir_fig = OUT / DIR_FIG
    dir_fig.mkdir(parents=True, exist_ok=True)
    for antigo in dir_fig.glob("*.png"):
        antigo.unlink()
    figuras = [figura(oid, est, dir_fig / f"OL_evento_{oid}.png") for oid in FIGURAS]
    resumo = {
        "natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "gerador": rotulo(Path(__file__)),
        "data_execucao": DATA_EXECUCAO,
        "protocolo": {"texto": rotulo(PROTOCOLO_MD), "sha256_texto": sha256(PROTOCOLO_MD), "secao": "Parte B (H4)"},
        "contraste": CONTRASTE,
        "parametros": {"meses": [COMP_INI, COMP_FIM], "e_min": E_MIN, "e_max": E_MAX, "base": "universal, b = g − 1",
                       "coorte": "mês da chegada do 1º médico do PMM-E (lista nominal, ciclos 1 e 2)",
                       "controles": "nunca tratados + ainda não tratados (G > max(t, b)); quem tem início na lista "
                                    "de ativos sai dos controles nesse mês",
                       "bootstrap": {"B": B_BOOT, "pesos": "Mammen", "semente": SEMENTE, "cluster": "município"},
                       "holm": ["B1", "B2"], "bky": ["B3", "B4", "B5"],
                       "rambachan_roth": {"restricao": "Δ^RM", "grade": list(GRADE_RM), "metodos": list(METODOS_RM),
                                          "alvo": "média do pós (e = 0..6)", "pre": "e = −6..−2",
                                          "ruptura": [0, MAX_RM, TOL_RM]},
                       "regra_ligacao": REGRA_LIGACAO, "cbos_alvo": cbos},
        "amostra": {**info_am, "municipios_em_U_com_celula": int(len(am_total)), "excluidos_tratados_fora_d2": len(excl),
                    "n_municipios": int(len(amostra)), "lista_nominal": info_ch, "lista_ativos": info_ativos},
        "coortes": info_G,
        "portoes": {"coortes": portao1, "definicoes": portao2},
        "b3": {**info_b3, "ligacao_x1": info_lig},
        "ligacao": resumo_lig,
        "leitura": classificar(est),
        "entradas": [
            E7.bloco_entrada(PAINEL, "outcomes B1, B2, B4, B5 e base de B3", "CNES nacional (a09)", "202406-202608",
                             "municipios do a08", "municipio x grupo de CBO x mes", "co_ibge, competencia, grupo",
                             "grupos alvo_pmme e generalistas; competencias 202406-202608"),
            E7.bloco_entrada(MANIF_A09, "CBO-alvo (ponte) e definições", "a09", "", "", "", "", ""),
            E7.bloco_entrada(POP22, "população (por 10 mil hab.)", "IBGE, Censo 2022", "2022", "Brasil", "municipio",
                             "co_ibge", ""),
            E7.bloco_entrada(A08, "universo U (só a lista de municípios)", "Ipea (a08)", "2010", "Brasil", "municipio",
                             "co_ibge", "IVS não é usado como variável"),
            E7.bloco_entrada(ARQ_VM, "amostra (célula em algum ciclo)", "tarefa B (12)", "ciclos 1-3", "V1, V2, V3",
                             "municipio x ciclo", "ciclo, co_ibge", ""),
            E7.bloco_entrada(NOMINAL, "tratamento: menor dt_inicio_atividade", "MS, lista nominal do PMM-E",
                             ", ".join(info_ch["dt_referencia"]), "ciclos 1 e 2", "especialista", "co_ibge",
                             "só co_ibge, dt_inicio_atividade, ciclo, dt_referencia; nenhum nome lido"),
            E7.bloco_entrada(ATIVOS_ZIP, "início do ciclo 3 (saída dos controles)", "MS, lista de ativos",
                             "2026-09-11", "ciclos 1-3", "especialista", "co_ibge",
                             "só ciclo, co_ibge, dt_inicio_atividade; nenhum nome lido"),
            E7.bloco_entrada(ARQ_VINC, "B3: horas SUS dos ligados", "CNES profissional (a16)", "202406-202608",
                             "médicos ligados pela X1", "vinculo x mes", "id_prof, competencia",
                             "regra D1; CBO-alvo; TP_SUS_NAO_SUS = 'S'"),
            E7.bloco_entrada(ARQ_CHAVES, "B3: médicos ligados (pseudônimos, só em memória)", "a16", "", "", "medico",
                             "id_prof, id_externo", "origem X1, regra D1"),
            E7.bloco_entrada(MANIF_A16, "competências obtidas do a16", "a16", "", "", "", "", ""),
            E7.bloco_entrada(ARQ_X1, "registros da X1 por posto (fração de não ligados)", "X1 (17)", "", "", "registro",
                             "id_medico", "regra D1"),
            E7.bloco_entrada(D2_RESUMO, "portão de coortes", "D2 (22)", "", "", "", "", ""),
        ],
        "desvios": DESVIOS,
        "figuras": figuras,
        "saidas": [{"arquivo": rotulo(OUT / n), "sha256": sha256(OUT / n)} for n in (NOME_EST, NOME_LIG)],
    }
    _gravar_json(OUT / NOME_RESUMO, resumo)
    atualizar_doc()
    return 0


if __name__ == "__main__":
    sys.exit(main())
