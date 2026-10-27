"""Adendo 48h: H1 pareada pela localização da unidade (exato na UF e em capital) e dos médicos (raio de 100 km).

Especificação congelada antes das contas: `docs/06_execucao/48h_adendo_pareamento_localizacao_unidade_e_medicos.md`
(27/10/2026, commit 243160d). SHA-256 conferido abaixo. Estatuto: `ADENDO_48H_POS_RESULTADO`;
`natureza_dos_dados = EMPIRICO` em toda saída. As decisões de implementação estão na seção 0 do doc 57w, escritas e
versionadas antes de qualquer estimativa (commit f5fbebf).

Importa o script 44 (adendo 48d) e o script 45 (adendo 48e) e não os reescreve: bases da H1, covariáveis, janela,
escore de propensão, *caliper*, suporte, inferência pareada, balanço, RDD com covariáveis e montagem das linhas são as
funções do 44; a regra 2, a amostra do pareamento e a regra literal são as do 45. Este script acrescenta:
- o estoque de especialistas das CBO-alvo do curso num raio de 50, 100 e 200 km (sem o próprio município), por
  10 mil hab. do raio, com os centroides e a distância do script 17; na unidade município × ciclo, a média das
  taxas dos cursos com vaga imediata, ponderada pelas vagas imediatas;
- o pareamento exato em UF e capital (PH-3: região de saúde e capital), aplicado às candidatas do 44 antes da regra
  literal do 45; a regra 2 do 45 com a UF no lugar da macrorregião;
- a origem dos médicos (X1, script 17) como outcome da PH-5, nunca como controle.
As trocas nas funções do 44 e do 45 são feitas só durante a chamada e desfeitas depois (como o 45 faz).

O que faz, na ordem
-------------------
1. Confere o SHA-256 do adendo 48h e guarda o SHA-256 das saídas `HI_*`, `CL_*`, `PM_*`, `PO_*` e `X1_*`.
2. Portão: refaz o PM-1 do 48e em 0,300 com as funções do 45, sem troca, e compara com `PM_estimativas.csv`
   (<= 1e-8) e com os pares de `PM_resumo.json`; confere o SHA-256 dos centroides contra o manifesto do 17 e contra
   `X1_ligacao_resumo.json`, e o da X1. Se falhar, para sem gravar nada.
3. PH-1 (Holm entre as quatro), PH-2, PH-3 e PH-5 (BKY entre as 16), PH-4 (RDD com EF de UF e raio) e PH-6
   (balanço e quem saiu pela regra 2).
4. Leitura do §3 do adendo pelas regras fixadas (decisões 19 a 23 do 57w), figuras com "Como ler" e blocos do doc
   57w (`--atualizar-doc`).

Integridade: o arquivo local de IVS da auditoria 16 não é lido (running variable = IVS 2010 oficial, a08); nenhuma
competência do CNES >= 202609; nada é escrito em `data/`; nome, CRM e UF do CRM das listas do PMM-E ficam só em
memória e são descartados na leitura (função do 17).

Uso
---
    python3 scripts/rdd_bolsa/49_pareamento_localizacao.py                 # estima e grava PL_*
    python3 scripts/rdd_bolsa/49_pareamento_localizacao.py --atualizar-doc # idem e regrava os blocos do 57w
    python3 scripts/rdd_bolsa/49_pareamento_localizacao.py --so-doc        # só regrava os blocos do 57w
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
import textwrap
from contextlib import contextmanager, nullcontext
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


# O 44 com o mesmo nome de módulo que o 45 usa: uma instância só, a que o 45 chama.
CL = _importar(DIR_RDD / "44_controles_localizacao_medicos.py", "controles_localizacao_medicos_para_pm")
PM = _importar(DIR_RDD / "45_pareamento_regra_literal.py", "pareamento_regra_literal_para_pl")
X1M = _importar(DIR_RDD / "17_ponte_pmme_cnes.py", "ponte_pmme_cnes_para_pl")    # centroides, haversine, listas
if PM.CL is not CL:
    raise RuntimeError("o 45 não usa a mesma instância do 44")
L = CL.L
T40 = CL.T40

# ---------------------------------------------------------------------------
# Parâmetros do adendo
# ---------------------------------------------------------------------------

OUT = CL.OUT
ADENDO = ROOT / "docs" / "06_execucao" / "48h_adendo_pareamento_localizacao_unidade_e_medicos.md"
DOC = ROOT / "docs" / "06_execucao" / "57w_resultados_pareamento_localizacao.md"
X1_MED = OUT / "X1_medicos.parquet"
X1_RES = OUT / "X1_ligacao_resumo.json"
COORD = X1M.COORD_JSON
COORD_MANIF = X1M.COORD_MANIFESTO

NOME_EST = "PL_estimativas.csv"
NOME_BAL = "PL_balanco.csv"
NOME_EXC = "PL_excluidos.csv"
NOME_RESUMO = "PL_resumo.json"
DIR_FIG = OUT / "PL_figuras"

DATA_EXECUCAO = "2026-10-27"
ESTATUTO = "ADENDO_48H_POS_RESULTADO"
NATUREZA = "EMPIRICO"
COMMIT_CONGELAMENTO = "243160d"
COMMIT_DECISOES = "f5fbebf"
SHA_ADENDO = "a2d342331149cfed49497c04301acb1eaae59a98e95cc0703aa8004100ec7d9a"
CORTES = CL.CORTES
CICLOS = CL.CICLOS
JANELA = CL.JANELA_PAR                     # 0,050
RAIO = 100                                 # km (principal)
RAIOS = (50, 100, 200)                     # PH-2: 50 e 200
TOL_PORTAO = 1e-8
LIMIAR_SAIDA = 0.25                        # 3ª linha do §3
ALFA = CL.ALFA
PROTEGIDOS = ("HI_", "CL_", "PM_", "PO_", "X1_")
TXT_CORTE = CL.TXT_CORTE
ROT_CORTE = CL.ROT_CORTE
BOLSA = CL.BOLSA
REGRA_X1 = "d1_pos_hoc"                    # regra principal da X1 (script 28)
LISTA_X1 = "ativos_2026-09-11"             # lista do painel municipal do 17
CICLOS_X1 = (1, 2)                         # a X1 não tem origem no ciclo 3
ORIGEM_MESMA_UF = ("mesmo_municipio", "mesma_regiao_saude", "mesma_uf")
ORIGEM_OUTRA_UF = ("outra_uf",)
VARS_ESCORE = ("log_pop", "med", "esp", "raio")
CURSOS_PONTE = tuple(range(1, 17))

OUT_H1 = CL.OUT_PAR_H1                     # H1M-FRAC (Y1), H1M-ALOC (Y2)
OUT_PH5 = {
    "H1M-MESMA-UF": {"desc": "medicos ativos ligados (X1, regra D1) em celulas com vaga imediata com origem na mesma "
                             "UF da vaga, por vaga imediata, por municipio x ciclo (ciclos 1 e 2)",
                     "unidade": CL.UN_VAGA, "col": "orig_mesma_uf_por_vi"},
    "H1M-OUTRA-UF": {"desc": "medicos ativos ligados (X1, regra D1) em celulas com vaga imediata com origem em outra "
                             "UF, por vaga imediata, por municipio x ciclo (ciclos 1 e 2)",
                     "unidade": CL.UN_VAGA, "col": "orig_outra_uf_por_vi"},
}
NOME_OUT = {**CL.NOME_OUT, "H1M-MESMA-UF": "alocados de origem na mesma UF por vaga imediata (X1)",
            "H1M-OUTRA-UF": "alocados de origem em outra UF por vaga imediata (X1)"}
NOME_CURTO = {"H1M-FRAC": "fração de células preenchidas", "H1M-ALOC": "alocados por vaga imediata",
              "H1M-MESMA-UF": "de origem na mesma UF", "H1M-OUTRA-UF": "de origem em outra UF"}

PRINCIPAIS = ("PH-1",)
BKY = ("PH-2", "PH-3", "PH-5")
N_HOLM, N_BKY = 4, 16
PAPEL = {"PH-1": "principal", "PH-2": "sensibilidade", "PH-3": "sensibilidade", "PH-4": "comparacao_com_a_reta",
         "PH-5": "secundaria_descritiva"}
DESC_BLOCO = {
    "PH-1": "H1 por PSM, exato em UF e capital, escore com o raio de 100 km, regra literal, regra 2 na UF, janela 0,050",
    "PH-2": "PH-1 com raio de 50 km e de 200 km",
    "PH-3": "PH-1 com exato na regiao de saude (CIR) e capital, onde houver pares",
    "PH-4": "RDD do 48b (HI-1, HI-2) com efeito fixo de UF e o raio de 100 km como covariavel (CCFT)",
    "PH-5": "Y2 dividido pela origem do medico (X1): mesma UF e outra UF, nos pares da PH-1",
}

CONTRASTE = CL.CONTRASTE
COLUNAS = CL.COLUNAS + ["raio_km", "exato", "regra_pareamento", "regra2", "saiu_regra2_abaixo", "saiu_regra2_acima",
                        "lado_que_procura", "pares_sem_outcome"]
COLUNAS_BAL = CL.COLUNAS_BAL + ["raio_km", "exato"]
COLUNAS_EXC = PM.COLUNAS_EXC + ["bloco", "raio_km"]


class FalhaValidacao(RuntimeError):
    """Portão ou validação obrigatória falhou: o script para sem gravar."""


sha256 = CL.sha256
rotulo = CL.rotulo
_f = CL._f
_juntar = CL._juntar
fn, fp, fv, fic, fint = CL.fn, CL.fp, CL.fv, CL.fic, CL.fint
_tab = CL._tab


# ---------------------------------------------------------------------------
# 1. Dados: bases do 44 e raio (decisões 1 a 6)
# ---------------------------------------------------------------------------

def hashes_protegidos() -> dict[str, str]:
    out = {}
    for pref in PROTEGIDOS:
        for p in sorted(OUT.glob(pref + "*")):
            arqs = sorted(x for x in p.rglob("*") if x.is_file()) if p.is_dir() else [p]
            for a in arqs:
                out[rotulo(a)] = sha256(a)
    return out


def conferir_centroides() -> dict:
    """Decisão 3: SHA-256 do arquivo de centroides = manifesto do 17 = entrada de X1_ligacao_resumo.json."""
    atual = sha256(COORD)
    man = json.loads(COORD_MANIF.read_text(encoding="utf-8"))
    x1 = json.loads(X1_RES.read_text(encoding="utf-8"))
    ent = [e for e in x1["entradas"] if e["caminho"] == rotulo(COORD)]
    if len(ent) != 1:
        raise FalhaValidacao("X1_ligacao_resumo.json sem a entrada do arquivo de centroides")
    ok = atual == man["sha256"] == ent[0]["sha256"]
    if not ok:
        raise FalhaValidacao(f"centroides: SHA-256 {atual} difere do manifesto do 17 ou da X1")
    sx1 = sha256(X1_MED)
    if sx1 != x1["saidas"][rotulo(X1_MED)]:
        raise FalhaValidacao("X1_medicos.parquet difere do registrado em X1_ligacao_resumo.json")
    return {"arquivo": rotulo(COORD), "sha256": atual, "manifesto_17": rotulo(COORD_MANIF),
            "sha256_manifesto_17": man["sha256"], "sha256_x1_ligacao_resumo": ent[0]["sha256"],
            "malha": man.get("malha_periodo_verificado"), "confere": True,
            "x1_medicos": {"arquivo": rotulo(X1_MED), "sha256": sx1, "confere_com_x1_ligacao_resumo": True}}


def contagens_por_curso(universo: pd.Index, curso_44: pd.DataFrame, pop: pd.Series) -> dict[int, pd.Series]:
    """Média mensal de vínculos (2024-06 a 2025-06, a09) nas CBO-alvo de cada curso, pela `_media_pre` do 44.

    Conferida contra a taxa do curso no município que o 44 monta (`esp_curso`)."""
    pontes = CL.ponte_cursos()
    cbos = sorted({c for v in pontes.values() for c in v})
    grupos = [f"cbo_{c}" for c in cbos]
    p = pd.read_parquet(CL.PAINEL, columns=["co_ibge", "competencia", "grupo", "n_vinculos", "natureza_dos_dados"],
                        filters=[("grupo", "in", grupos), ("competencia", "in", list(CL.COMP_PRE))])
    p["co_ibge"] = p["co_ibge"].astype(str)
    p["competencia"] = p["competencia"].astype(str)
    if (p["competencia"] >= CL.LIMITE_CNES).any():
        raise FalhaValidacao("a09 com competência >= 202609")
    if sorted(p["competencia"].unique()) != list(CL.COMP_PRE):
        raise FalhaValidacao("a09 sem todas as competências do pré (202406–202506)")
    if set(p["natureza_dos_dados"].astype(str).str.upper()) != {"EMPIRICO"}:
        raise FalhaValidacao("a09 sem natureza EMPIRICO")
    medias = {g: CL._media_pre(p, g, universo)[0] for g in grupos}
    out = {}
    for k, cb in pontes.items():
        cnt = sum(medias[f"cbo_{c}"] for c in cb)
        taxa = (cnt / pop * CL.ESCALA_HAB).where(pop > 0)
        ref = curso_44[curso_44["cod_curso"] == k].set_index("co_ibge")["esp_curso"].reindex(universo)
        dif = np.nanmax(np.abs(taxa.to_numpy(float) - ref.to_numpy(float)))
        if not (np.isnan(taxa.to_numpy(float)) == np.isnan(ref.to_numpy(float))).all() or dif > 1e-9:
            raise FalhaValidacao(f"curso {k}: contagem difere da taxa do 44 (máx. dif. {dif})")
        out[k] = cnt
    return out


def taxas_raio(universo: pd.Index, cnt: dict[int, pd.Series], pop: pd.Series) -> tuple[pd.DataFrame, dict]:
    """Decisão 4: por município do a08 e curso, a taxa de especialistas do curso nos vizinhos a até R km (sem o
    próprio), por 10 mil hab. dos vizinhos, para R em RAIOS. Ausente sem vizinho ou com vizinho sem média ou
    população (regra do `_resto_regiao` do 44)."""
    co, info_co = X1M.ler_coordenadas()
    if info_co.get("status") != "OBTIDO":
        raise FalhaValidacao("centroides do IBGE indisponíveis")
    xy = co.set_index("co_ibge").reindex(universo)
    if xy[["lon", "lat"]].isna().any().any():
        raise FalhaValidacao(f"{int(xy['lon'].isna().sum())} município(s) do a08 sem centroide")
    lon, lat = xy["lon"].to_numpy(float), xy["lat"].to_numpy(float)
    cursos = sorted(cnt)
    C = np.column_stack([cnt[k].reindex(universo).to_numpy(float) for k in cursos])
    c_nan = np.isnan(C).astype(float)
    C0 = np.nan_to_num(C)
    P = pop.reindex(universo).to_numpy(float)
    p_ok = P > 0
    P0 = np.where(p_ok, P, 0.0)
    p_bad = (~p_ok).astype(float)
    n = len(universo)
    res = {R: {"est": np.full((n, len(cursos)), np.nan), "nviz": np.zeros(n, int)} for R in RAIOS}
    passo = 400
    for i0 in range(0, n, passo):
        i1 = min(n, i0 + passo)
        D = X1M.haversine_km(lon[i0:i1, None], lat[i0:i1, None], lon[None, :], lat[None, :])
        D[np.arange(i1 - i0), np.arange(i0, i1)] = np.inf          # sem o próprio município
        for R in RAIOS:
            M = (D <= R).astype(float)
            nviz = M.sum(axis=1)
            soma_c = M @ C0
            falta_c = M @ c_nan
            soma_p = M @ P0
            falta_p = M @ p_bad
            ok = (nviz > 0)[:, None] & (falta_c == 0) & (falta_p == 0)[:, None] & (soma_p > 0)[:, None]
            with np.errstate(invalid="ignore", divide="ignore"):
                taxa = soma_c / soma_p[:, None] * CL.ESCALA_HAB
            res[R]["est"][i0:i1] = np.where(ok, taxa, np.nan)
            res[R]["nviz"][i0:i1] = nviz.astype(int)
    linhas = []
    info = {"centroides": {k: info_co[k] for k in ("municipios", "sha256", "sha256_atual") if k in info_co},
            "universo_a08": int(n), "por_raio": {}}
    for R in RAIOS:
        df = pd.DataFrame(res[R]["est"], columns=cursos)
        df["co_ibge"] = universo
        lg = df.melt(id_vars="co_ibge", var_name="cod_curso", value_name=f"raio_{R}")
        linhas.append(lg.set_index(["co_ibge", "cod_curso"]))
        nv = res[R]["nviz"]
        info["por_raio"][str(R)] = {"municipios_sem_vizinho": int((nv == 0).sum()),
                                    "vizinhos_mediana": float(np.median(nv)), "vizinhos_p10": float(np.percentile(nv, 10)),
                                    "vizinhos_p90": float(np.percentile(nv, 90)),
                                    "municipios_com_taxa_ausente": int(np.isnan(res[R]["est"]).any(axis=1).sum())}
    tab = pd.concat(linhas, axis=1).reset_index()
    tab["cod_curso"] = tab["cod_curso"].astype(int)
    return tab, info


def raio_unidades(b: dict, tab: pd.DataFrame) -> tuple[pd.DataFrame, dict[int, pd.DataFrame], dict]:
    """Decisões 5 e 6: raio da unidade município × ciclo (média ponderada pelas vagas imediatas das células com vaga
    imediata, só cursos da ponte) e raio da célula (taxa do curso da célula)."""
    imed_t = ("so_imed", "mista")
    partes, ck_raio, info = [], {}, {}
    for k in CICLOS:
        c = b["CK"][k].merge(tab, on=["co_ibge", "cod_curso"], how="left", validate="many_to_one")
        if len(c) != len(b["CK"][k]):
            raise FalhaValidacao(f"V{k}: merge do raio mudou o número de células")
        ck_raio[k] = c
        im = c[c["tipo_celula"].isin(imed_t)].copy()
        im["w"] = im["vagas_imediatas"].astype(float)
        im["na_ponte"] = im["cod_curso"].isin(CURSOS_PONTE)
        tot = im.groupby("co_ibge")["w"].sum()
        mk = b["MK"][k].set_index("co_ibge")
        vi = mk.loc[tot.index, "vi_imed"].astype(float)
        if (np.abs(tot - vi) > 1e-9).any():
            raise FalhaValidacao(f"V{k}: soma das vagas imediatas das células difere de vi_imed")
        u = pd.DataFrame(index=tot.index)
        u["vi_fora_da_ponte"] = im[~im["na_ponte"]].groupby("co_ibge")["w"].sum().reindex(u.index).fillna(0.0)
        u["cel_fora_da_ponte"] = im[~im["na_ponte"]].groupby("co_ibge").size().reindex(u.index).fillna(0).astype(int)
        p = im[im["na_ponte"]]
        for R in RAIOS:
            col = f"raio_{R}"
            num = (p["w"] * p[col]).groupby(p["co_ibge"]).sum(min_count=1)
            den = p.groupby("co_ibge")["w"].sum()
            falta = p[col].isna().groupby(p["co_ibge"]).any()
            val = (num / den).where((den > 0) & ~falta)
            u[col] = val.reindex(u.index)
        u["ciclo"] = k
        partes.append(u.reset_index())
        info[f"ciclo_{k}"] = {"municipios_com_vaga_imediata": int(len(u)),
                              "com_celula_fora_da_ponte": int((u["cel_fora_da_ponte"] > 0).sum()),
                              "celulas_com_vaga_imediata_fora_da_ponte": int(u["cel_fora_da_ponte"].sum()),
                              "so_cursos_fora_da_ponte": int((u["vi_fora_da_ponte"] >= tot.reindex(u.index)).sum()),
                              **{f"raio_{R}_ausente": int(u[f"raio_{R}"].isna().sum()) for R in RAIOS}}
    un = pd.concat(partes, ignore_index=True)
    return un, ck_raio, info


def origem_x1(b: dict) -> tuple[pd.DataFrame, dict]:
    """Decisões 14 a 16: por município × ciclo (ciclos 1 e 2), médicos ativos ligados (X1, regra D1) em células com
    vaga imediata, pela origem. A célula vem das listas do 17 (nome, CRM e UF do CRM descartados na hora)."""
    x1 = pd.read_parquet(X1_MED, columns=["id_medico", "regra_ligacao", "ciclo", "fonte_lista", "co_ibge", "ligado",
                                          "c_origem", "natureza_dos_dados"])
    if set(x1["natureza_dos_dados"]) != {NATUREZA}:
        raise FalhaValidacao("X1 sem natureza EMPIRICO")
    li, _ = X1M.ler_listas_pmme()
    li = li[["id_medico", "ciclo", "co_cnes", "co_ibge", "cod_curso", "fonte_lista"]].copy()
    d = x1.merge(li, on="id_medico", how="left", suffixes=("", "_l"), validate="many_to_one")
    if d["ciclo_l"].isna().any():
        raise FalhaValidacao("id_medico da X1 sem registro nas listas reconstruídas")
    dif = {k: int((d[k].astype(str) != d[k + "_l"].astype(str)).sum()) for k in ("ciclo", "co_ibge", "fonte_lista")}
    if any(dif.values()):
        raise FalhaValidacao(f"listas reconstruídas não batem com X1_medicos: {dif}")
    x = d[(d["regra_ligacao"] == REGRA_X1) & (d["fonte_lista"] == LISTA_X1) & d["ciclo"].isin(CICLOS_X1)].copy()
    cel = pd.concat([b["CK"][k].assign(ciclo=k) for k in CICLOS_X1], ignore_index=True)
    cel = cel[["ciclo", "co_ibge", "co_cnes_7d", "cod_curso", "tipo_celula"]].rename(columns={"co_ibge": "co_ibge_cel"})
    x["cod_curso"] = x["cod_curso"].astype(int)
    x = x.merge(cel, left_on=["ciclo", "co_cnes", "cod_curso"], right_on=["ciclo", "co_cnes_7d", "cod_curso"],
                how="left", validate="many_to_one")
    no_quadro = x["tipo_celula"].notna()
    if (x.loc[no_quadro, "co_ibge_cel"].astype(str) != x.loc[no_quadro, "co_ibge"].astype(str)).any():
        raise FalhaValidacao("X1: município da lista difere do município da célula do quadro")
    x["co_ibge"] = x["co_ibge"].astype(str)
    x["imed"] = x["tipo_celula"].isin(["so_imed", "mista"])
    lig = x["ligado"] == 1
    x["origem"] = np.where(lig & x["c_origem"].isin(ORIGEM_MESMA_UF), "mesma_uf",
                           np.where(lig & x["c_origem"].isin(ORIGEM_OUTRA_UF), "outra_uf", "desconhecida"))
    xi = x[x["imed"]]
    cont = xi.groupby(["ciclo", "co_ibge", "origem"]).size().unstack("origem", fill_value=0)
    for c in ("mesma_uf", "outra_uf", "desconhecida"):
        if c not in cont.columns:
            cont[c] = 0
    cont = cont[["mesma_uf", "outra_uf", "desconhecida"]].reset_index()
    info = {"fonte": rotulo(X1_MED), "sha256": sha256(X1_MED), "regra_ligacao": REGRA_X1, "lista": LISTA_X1,
            "ciclos": list(CICLOS_X1), "conferencia_listas": dif,
            "registros": int(len(x)), "ligados": int(lig.sum()),
            "sem_celula_no_quadro": int((~no_quadro).sum()),
            "em_celula_so_cadastro_reserva": int((no_quadro & ~x["imed"]).sum()),
            "em_celula_com_vaga_imediata": int(x["imed"].sum()),
            "origem_em_celula_com_vaga_imediata": {k: int(v) for k, v in xi["origem"].value_counts().sort_index().items()},
            "c_origem_desconhecida_detalhe": {str(k): int(v) for k, v in xi.loc[xi["origem"] == "desconhecida",
                                              "c_origem"].fillna("ausente ou nao ligado").value_counts().items()},
            "definicao": {"mesma_uf": list(ORIGEM_MESMA_UF), "outra_uf": list(ORIGEM_OUTRA_UF),
                          "desconhecida": "sem vinculo medico anterior, origem ausente na X1 ou medico nao ligado"}}
    return cont, info


def montar_unidades(b: dict, un_raio: pd.DataFrame, orig: pd.DataFrame, cov: pd.DataFrame) -> pd.DataFrame:
    par = b["par"].copy()
    n0 = len(par)
    par = par.merge(un_raio[["co_ibge", "ciclo"] + [f"raio_{R}" for R in RAIOS] + ["cel_fora_da_ponte"]],
                    on=["co_ibge", "ciclo"], how="left", validate="one_to_one")
    par = par.merge(orig, on=["ciclo", "co_ibge"], how="left", validate="one_to_one")
    if len(par) != n0:
        raise FalhaValidacao("unidades da H1 mudaram ao juntar raio e origem")
    x1c = par["ciclo"].isin(CICLOS_X1)
    for c in ("mesma_uf", "outra_uf", "desconhecida"):
        par[c] = np.where(x1c, par[c].fillna(0.0), np.nan)
    vi = par["vi_imed"].astype(float).where(par["vi_imed"] > 0)
    par["orig_mesma_uf_por_vi"] = par["mesma_uf"] / vi
    par["orig_outra_uf_por_vi"] = par["outra_uf"] / vi
    par["orig_desconhecida_por_vi"] = par["desconhecida"] / vi
    par["regiao_saude"] = par["co_ibge"].map(cov["regiao_saude"])
    return par


def carregar() -> dict:
    cov, curso, info_cov = CL.construir_covariaveis()
    CL.UFS = sorted(cov["cd_uf"].unique().tolist())
    b = CL.bases_h1(cov, curso)
    universo = cov.index
    pop = cov["populacao_2022"].astype(float)
    cnt = contagens_por_curso(universo, curso, pop)
    tab, info_raio = taxas_raio(universo, cnt, pop)
    un, ck_raio, info_un = raio_unidades(b, tab)
    orig, info_x1 = origem_x1(b)
    par = montar_unidades(b, un, orig, cov)
    # PH-4: célula com o raio do curso; município × ciclo com o raio da unidade.
    ck4 = {k: ck_raio[k].assign(raio=ck_raio[k][f"raio_{RAIO}"]) for k in CICLOS}
    mk4 = {}
    for k in CICLOS:
        m = b["MK"][k].merge(un.loc[un["ciclo"] == k, ["co_ibge", f"raio_{RAIO}"]], on="co_ibge", how="left",
                             validate="one_to_one")
        mk4[k] = m.assign(raio=m[f"raio_{RAIO}"])
    info_raio["unidades_municipio_ciclo"] = info_un
    return {"b": b, "par": par, "ck4": ck4, "mk4": mk4, "cov": cov,
            "info_cov": {k: info_cov[k] for k in ("referencia_ibge", "populacao", "regiao_saude", "painel_a09")},
            "info_raio": info_raio, "info_x1": info_x1}


# ---------------------------------------------------------------------------
# 2. Regra 2 na UF e exato (decisões 7 a 12): trocas durante a chamada
# ---------------------------------------------------------------------------

def categorias_uf(d: pd.DataFrame) -> list[tuple[str, np.ndarray]]:
    """Decisão 7: capital, não capital e cada UF presente (a UF no lugar da macrorregião do 45)."""
    cats = [("capital", (d["capital"] == 1).to_numpy()), ("nao capital", (d["capital"] == 0).to_numpy())]
    return cats + [(f"uf[{u}]", (d["cd_uf"] == u).to_numpy()) for u in sorted(d["cd_uf"].astype(str).unique())]


def vars_balanco(d: pd.DataFrame) -> tuple[str, ...]:
    return ("capital",) + tuple(f"uf_{u}" for u in sorted(d["cd_uf"].astype(str).unique())) + VARS_ESCORE


def _col_bal_pl(d: pd.DataFrame, v: str) -> np.ndarray:
    if v.startswith("uf_"):
        return (d["cd_uf"].astype(str) == v[3:]).to_numpy(float)
    return d[v].to_numpy(float)


@contextmanager
def trocas(vars_bal: tuple):
    """Troca, só durante a chamada: o conjunto do escore do 44 (L+M -> X do 48h), as variáveis e a coluna do
    balanço do 44 e a lista de categorias da regra 2 do 45 (decisão 12). Devolve tudo depois."""
    orig = (CL.CONJUNTOS, CL.VARS_BAL, CL._col_bal, PM.categorias)
    CL.CONJUNTOS = {**orig[0], "L+M": VARS_ESCORE}
    CL.VARS_BAL = vars_bal
    CL._col_bal = _col_bal_pl
    PM.categorias = categorias_uf
    try:
        yield
    finally:
        CL.CONJUNTOS, CL.VARS_BAL, CL._col_bal, PM.categorias = orig


def funcao_exato_literal(d2: pd.DataFrame, exato: str):
    """Decisão 10: candidatas do 44 filtradas para o mesmo estrato exato (UF ou CIR, e capital) e a regra literal
    do 45 (lado com menos unidades por ciclo, ordem decrescente do escore)."""
    ids = d2["id"].tolist()
    acima = dict(zip(ids, d2["acima"].astype(bool)))
    grupo = dict(zip(ids, d2["ciclo"]))
    lp, _ = CL.escore_propensao(d2)
    if lp is None:
        return None
    chave = {i: (-float(x), i) for i, x in zip(ids, lp)}
    est = {}
    for i, e, cap in zip(ids, d2[exato], d2["capital"]):
        est[i] = None if pd.isna(e) or str(e).strip() == "" else f"{e}|{int(cap)}"

    def f(cand):
        cand2 = [x for x in cand if est[x[1]] is not None and est[x[1]] == est[x[2]]]
        return PM.regra_literal(cand2, acima, grupo, chave)
    return f


def rodar(unid: pd.DataFrame, outcomes: dict, corte: int, bloco: str, raio_km: int, exato: str,
          nomes: pd.DataFrame) -> tuple[list[dict], list[dict], dict, list[dict]]:
    """Uma linha do adendo: amostra com a regra 2 na UF (45) e `pareamentos` do 44 com exato + regra literal."""
    u = unid.assign(raio=unid[f"raio_{raio_km}"])
    d_jan = CL._janela(u, corte, JANELA)
    with trocas(vars_balanco(d_jan)):
        d2, am, exc = PM.amostra(u, corte, JANELA, True, nomes, "H1")
        am["lados_que_procuram"] = PM.lados_que_procuram(d2, True)
        uso = u[~u["id"].isin({e["id"] for e in exc})]
        f = funcao_exato_literal(d2, exato)
        with (PM.trocar_pareamento(f) if f is not None else nullcontext()):
            ln, bl, rg = CL.pareamentos(uso, "H1", outcomes, corte, JANELA, True, ("PSM",), {"PSM": bloco},
                                        {"PSM": PAPEL[bloco]})
        ids44 = CL._janela(uso, corte, JANELA)
        ids44 = set(ids44.loc[CL._completo(ids44), "id"])
    if ids44 != set(d2["id"]):
        raise FalhaValidacao(f"{bloco} {TXT_CORTE[corte]}: amostra do 44 difere da amostra da regra 2")
    procura = ";".join(f"{k}: {x['procura']}" for k, x in am["lados_que_procuram"].items())
    for x in ln:
        x.update({"estatuto": ESTATUTO, "conjunto": f"exato {_nome_exato(exato)} + escore com raio {raio_km} km",
                  "populacao": f"H1 municipio x ciclo (48b); janela 0.050; regra 2 na UF; raio {raio_km} km",
                  "raio_km": raio_km, "exato": f"{exato};capital;ciclo", "regra_pareamento": "literal",
                  "regra2": True, "saiu_regra2_abaixo": am.get("saiu_regra2", {}).get("abaixo", 0),
                  "saiu_regra2_acima": am.get("saiu_regra2", {}).get("acima", 0), "lado_que_procura": procura})
        m = re.search(r"(\d+) par\(es\) sem outcome", str(x["nota"]))
        x["pares_sem_outcome"] = int(m.group(1)) if m else 0
        x["nota"] = _juntar(x["nota"], DESC_BLOCO[bloco])
    for x in bl:
        x.update({"estatuto": ESTATUTO, "raio_km": raio_km, "exato": f"{exato};capital;ciclo"})
    for e in exc:
        e.update({"estatuto": ESTATUTO, "bloco": bloco, "raio_km": raio_km})
    rg.update({"bloco": bloco, "metodo": "PSM", "regra_pareamento": "literal", "raio_km": raio_km, "exato": exato,
               "amostra_48h": am})
    return ln, bl, rg, exc


def _nome_exato(exato: str) -> str:
    return {"cd_uf": "na UF", "regiao_saude": "na regiao de saude"}[exato]


def _nome_exato_doc(exato: str) -> str:
    return {"cd_uf": "na UF", "regiao_saude": "na região de saúde"}[exato]


def specs() -> list[dict]:
    s = []
    for c in CORTES:
        s.append({"bloco": "PH-1", "corte": c, "raio": RAIO, "exato": "cd_uf", "outs": {**OUT_H1, **OUT_PH5}})
        for R in (50, 200):
            s.append({"bloco": "PH-2", "corte": c, "raio": R, "exato": "cd_uf", "outs": OUT_H1})
        s.append({"bloco": "PH-3", "corte": c, "raio": RAIO, "exato": "regiao_saude", "outs": OUT_H1})
    return s


def media_pares(par: pd.DataFrame, pares: list[dict], col: str, lado: str) -> float:
    y = par.set_index("id")[col]
    v = np.array([y[p[lado]] for p in pares], float)
    a = np.array([y[p["acima"]] for p in pares], float)
    bb = np.array([y[p["abaixo"]] for p in pares], float)
    ok = np.isfinite(a) & np.isfinite(bb)
    return float(v[ok].mean()) if ok.any() else float("nan")


def todas_as_linhas(dados: dict, nomes: pd.DataFrame) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    linhas, bal, regs, exc = [], [], [], []
    par = dados["par"]
    for s in specs():
        ln, bl, rg, ex = rodar(par, s["outs"], s["corte"], s["bloco"], s["raio"], s["exato"], nomes)
        for x in ln:
            if x["outcome"] in OUT_PH5:                       # PH-5: os mesmos pares da PH-1
                x["bloco"], x["papel"] = "PH-5", PAPEL["PH-5"]
                pares = (rg.get("PSM") or {}).get("pares") or []
                x["media_abaixo"] = media_pares(par, pares, OUT_PH5[x["outcome"]]["col"], "abaixo") if pares \
                    else np.nan
                x["nota"] = _juntar(x["nota"], DESC_BLOCO["PH-5"])
        linhas += ln
        bal += bl
        regs.append(rg)
        if s["bloco"] in ("PH-1", "PH-2"):                     # PH-3 e PH-5 usam a amostra da PH-1
            exc += ex
    return linhas, bal, regs, exc


def linhas_ph4(dados: dict) -> list[dict]:
    """Decisão 13: RDD do 48b com EF de UF e o raio de 100 km (CCFT), e o sem-controle na mesma amostra."""
    imed = T40.filtro_tipos("so_imed", "mista")
    mun_imed = T40.filtro_coluna_positiva("n_cel_imed")
    vars_ = ("uf", "raio")
    out = []
    for c in CORTES:
        base = {"HI-1": T40.amostra(dados["ck4"], CICLOS, c, imed), "HI-2": T40.amostra(dados["mk4"], CICLOS, c, mun_imed)}
        for oid, a in base.items():
            jan = CL._janela_kernel(a.s, a.c, CL.H)
            ab = (L.normalizar_s_mil(a.s) - a.c) <= 0
            m = CL.mascara_completa(a.d, vars_)
            asub = a.subconjunto(m)
            r = CL.rd_h1(asub, oid, vars_)
            r0 = CL.rd_h1(asub, oid, ())
            ln = CL.nova_linha("PH-4", PAPEL["PH-4"], "H1", oid, CL.OUT_H1[oid]["desc"],
                               CL.OUT_H1[oid]["unidade_analise"], "V1+V2+V3 (48b)", c, CL.H, "UF+raio 100 km",
                               vars_, "RDD", CL.EST_RD[oid], CL.OUT_H1[oid]["unidade"],
                               nota=DESC_BLOCO["PH-4"])
            ln = CL.preencher_rd(ln, r, r0)
            CL._saidas(ln, a, jan, ab, m, oid)
            ln.update({"estatuto": ESTATUTO, "raio_km": RAIO, "exato": "", "regra_pareamento": "", "regra2": False,
                       "lado_que_procura": ""})
            out.append(ln)
    return out


# ---------------------------------------------------------------------------
# 3. Portão (decisão 24)
# ---------------------------------------------------------------------------

def portao(dados: dict, nomes: pd.DataFrame) -> dict:
    est_pm, _, _, res_pm = PM.ler_saidas()
    ln, _, rg, _ = PM.rodar(dados["b"]["par"], "H1", PM.OUT_H1, 300, PM.JANELA_PAR, "PSM", "literal", True, "PM-1",
                            nomes)
    ref_reg = next(x for x in res_pm["pareamento"] if x["bloco"] == "PM-1" and x["parte"] == "H1"
                   and x["corte"] == "0.300")
    mesmos = ({(p["acima"], p["abaixo"]) for p in rg["PSM"]["pares"]}
              == {(p["acima"], p["abaixo"]) for p in ref_reg["PSM"]["pares"]})
    out = {"referencia": rotulo(OUT / PM.NOME_EST), "sha256_referencia": sha256(OUT / PM.NOME_EST),
           "tolerancia": TOL_PORTAO, "linhas": []}
    for x in ln:
        ref = CL._uma(est_pm, bloco="PM-1", outcome=x["outcome"], corte="0.300")
        difs = {k: abs(_f(x[k]) - _f(ref[k])) for k in ("tau", "p_valor", "ic95_inf", "ic95_sup", "ic_t_inf",
                                                         "ic_t_sup")}
        n_ok = int(x["n_pares"]) == int(ref["n_pares"])
        ok = all(np.isfinite(v) and v <= TOL_PORTAO for v in difs.values()) and n_ok and mesmos
        out["linhas"].append({"linha": "PM-1", "outcome": x["outcome"], "corte": "0.300", "tau_48e": _f(ref["tau"]),
                              "tau_refeito": _f(x["tau"]), "max_abs_dif": max(difs.values()),
                              "n_pares_48e": int(ref["n_pares"]), "n_pares_refeito": int(x["n_pares"]),
                              "mesmos_pares": bool(mesmos), "reproduz": bool(ok)})
        if not ok:
            raise FalhaValidacao(f"portão: PM-1 {x['outcome']} em 0,300 não reproduz o 48e: {difs}, pares "
                                 f"{x['n_pares']} x {ref['n_pares']}, mesmos pares: {mesmos}")
    out["max_abs_dif"] = max(x["max_abs_dif"] for x in out["linhas"])
    out["centroides"] = conferir_centroides()
    out["aprovado"] = True
    return out


# ---------------------------------------------------------------------------
# 4. Multiplicidade e leitura (decisões 17 e 19 a 23)
# ---------------------------------------------------------------------------

def aplicar_multiplicidade(est: pd.DataFrame) -> pd.DataFrame:
    est = est.copy()
    est["entra_holm"] = est["bloco"].isin(PRINCIPAIS)
    est["entra_bky"] = est["bloco"].isin(BKY)
    est["multiplicidade_provisoria"] = False
    for fam, col, fn_, n_esp in (("entra_holm", "p_holm", L.holm, N_HOLM), ("entra_bky", "q_bky", L.qvalores_bky,
                                                                             N_BKY)):
        m = est[fam].to_numpy(bool)
        if int(m.sum()) != n_esp:
            raise FalhaValidacao(f"família {col}: {int(m.sum())} linhas (esperadas {n_esp})")
        exe = (est["status"] == "EXECUTADO").to_numpy()
        p = np.where(exe[m], est.loc[m, "p_valor"].astype(float).to_numpy(), 1.0)
        est.loc[m, col] = np.where(exe[m], fn_(p), np.nan)
    return est


def _contem_zero(r) -> bool:
    return _f(r["ic95_inf"]) <= 0.0 <= _f(r["ic95_sup"])


def _am(resumo: dict, bloco: str, corte: str, raio: int = RAIO) -> dict:
    return next(x["amostra_48h"] for x in resumo["pareamento"] if x["bloco"] == bloco and x["corte"] == corte
                and int(x["raio_km"]) == raio)


def leituras(est: pd.DataFrame, regs: list[dict]) -> dict:
    out = {"linhas": [], "geral": None, "parte_comparavel": [], "ph5": []}
    for _, r in est[est["bloco"] == "PH-1"].iterrows():
        if r["status"] != "EXECUTADO":
            cod = "SEM_ESTIMATIVA"
        elif _f(r["p_holm"]) < ALFA:
            cod = "REJEITA_ZERO_DEPOIS_DO_HOLM"
        elif not _contem_zero(r):
            cod = "IC_EXCLUI_ZERO_SEM_HOLM"
        elif r["comparacao_limpa"] != "SIM":
            cod = "BALANCO_NAO_LIMPO"
        else:
            cod = "IC_CONTEM_ZERO_BALANCO_LIMPO"
        out["linhas"].append({"bloco": "PH-1", "outcome": r["outcome"], "corte": r["corte"], "codigo": cod,
                              "tau": _f(r["tau"]), "p_holm": _f(r["p_holm"])})
    cods = [x["codigo"] for x in out["linhas"]]
    if any(c == "REJEITA_ZERO_DEPOIS_DO_HOLM" for c in cods):
        out["geral"] = "REJEITA_ZERO_DEPOIS_DO_HOLM"
    elif len(cods) == N_HOLM and all(c == "IC_CONTEM_ZERO_BALANCO_LIMPO" for c in cods):
        out["geral"] = "NAO_SE_DETECTA_DIFERENCA"
    else:
        out["geral"] = "PRIMEIRA_LEITURA_NAO_SE_APLICA"
    for rg in regs:
        if rg["bloco"] != "PH-1":
            continue
        am = rg["amostra_48h"]
        fr = am["fracao_saiu_regra2"]
        lados = [lado for lado in ("abaixo", "acima") if fr[lado] > LIMIAR_SAIDA]
        if lados:
            out["parte_comparavel"].append({"corte": am["corte"], "lados": lados, "fracao": {k: fr[k] for k in lados},
                                            "categorias": [c["categoria"] for c in am["categorias_um_lado"]],
                                            "codigo": "VALE_SO_PARA_UFS_DOS_DOIS_LADOS"})
    for c in CORTES:
        r = CL._uma(est, bloco="PH-5", outcome="H1M-OUTRA-UF", corte=ROT_CORTE[c])
        indicio = r["status"] == "EXECUTADO" and _f(r["tau"]) > 0 and not _contem_zero(r)
        out["ph5"].append({"corte": ROT_CORTE[c], "tau": _f(r["tau"]), "q_bky": _f(r["q_bky"]),
                           "codigo": "INDICIO_ATRAI_DE_LONGE" if indicio else "SEM_INDICIO_DE_ATRAIR_DE_LONGE"})
    return out


# ---------------------------------------------------------------------------
# 5. Formatação e blocos do doc 57w
# ---------------------------------------------------------------------------

def _corte_txt(ct) -> str:
    return TXT_CORTE[int(round(_f(ct) * 1000))]


UF_SIGLA: dict[str, str] = {}


def _uf_txt(cat: str) -> str:
    if cat == "capital":
        return "capitais"
    if cat == "nao capital":
        return "não capitais"
    cod = cat.replace("uf[", "").rstrip("]")
    return UF_SIGLA.get(cod, cod)


def _pct(x: float) -> str:
    return fn(100 * x, 0, False) + "%"


def bloco(nome: str, corpo: str) -> str:
    return f"<!-- PL:{nome}:inicio -->\n{corpo.rstrip()}\n<!-- PL:{nome}:fim -->"


def _limpa(r) -> str:
    return (f"{fn(r['max_abs_dp_depois'], 2, False)} ({'limpa' if r['comparacao_limpa'] == 'SIM' else 'não limpa'})"
            if np.isfinite(_f(r["max_abs_dp_depois"])) else "—")


def tab_linhas(est: pd.DataFrame, blocos: tuple) -> str:
    linhas = []
    for _, r in est[est["bloco"].isin(blocos)].iterrows():
        rot = f"{r['bloco']}" + (f" ({int(r['raio_km'])} km)" if r["bloco"] == "PH-2" else "")
        if r["status"] != "EXECUTADO":
            motivo = "escore não estimado" if "escore" in str(r["nota"]) else (
                "sem pares" if _f(r["n_pares"]) == 0 else "menos de 2 pares")
            linhas.append([rot, NOME_OUT[r["outcome"]], _corte_txt(r["corte"]), f"{r['status']} ({motivo})",
                           fint(r["n_pares"])] + ["—"] * 7)
            continue
        mult = ("Holm " + fp(r["p_holm"])) if r["entra_holm"] else ("BKY " + fp(r["q_bky"])) if r["entra_bky"] else "—"
        sem = f"{fint(r['sem_par_abaixo'])} / {fint(r['sem_par_acima'])}"
        sem += f" (fora do suporte: {fint(r['fora_suporte_abaixo'])} / {fint(r['fora_suporte_acima'])})"
        pares = fint(r["n_pares"]) + (f" (+{int(r['pares_sem_outcome'])} sem outcome)"
                                      if _f(r["pares_sem_outcome"]) > 0 else "")
        linhas.append([rot, NOME_OUT[r["outcome"]], _corte_txt(r["corte"]), r["status"], pares, sem, fv(r), fic(r),
                       fic(r, "ic_t_inf", "ic_t_sup"), fp(r["p_valor"]), mult, _limpa(r)])
    return _tab(["Linha", "Outcome", "Corte", "Status", "Pares", "Sem par abaixo / acima",
                 "Diferença média (acima − abaixo)", "IC 95% permutação", "IC 95% t pareado", "p",
                 "p Holm ou q BKY", "Maior DP absoluta depois"], linhas)


def tab_portao(resumo: dict) -> str:
    p = resumo["portao"]
    linhas = [[x["linha"], NOME_OUT[x["outcome"]], _corte_txt(x["corte"]), fn(x["tau_48e"], 6), fn(x["tau_refeito"], 6),
               f"{x['max_abs_dif']:.1e}", f"{x['n_pares_48e']} / {x['n_pares_refeito']}",
               "sim" if x["mesmos_pares"] else "não", "sim" if x["reproduz"] else "não"] for x in p["linhas"]]
    t = _tab(["Linha do 48e", "Outcome", "Corte", "Diferença média em PM_estimativas.csv", "Refeita aqui",
              "máx. dif. absoluta (estimativa, p, IC)", "Pares (48e / refeito)", "Mesmos pares", "Reproduz"], linhas)
    c = p["centroides"]
    t += (f"\n\nCentroides (`{c['arquivo']}`, malha {c['malha']}): SHA-256 `{c['sha256'][:16]}…`, igual ao do manifesto do "
          f"17 e ao de `X1_ligacao_resumo.json`. `X1_medicos.parquet`: SHA-256 `{c['x1_medicos']['sha256'][:16]}…`, igual "
          "ao registrado pela X1.")
    return t


def tab_raio(resumo: dict) -> str:
    ir = resumo["raio"]
    linhas = []
    for R in RAIOS:
        x = ir["por_raio"][str(R)]
        linhas.append([f"{R} km", fint(x["municipios_sem_vizinho"]), fn(x["vizinhos_p10"], 0, False),
                       fn(x["vizinhos_mediana"], 0, False), fn(x["vizinhos_p90"], 0, False),
                       fint(x["municipios_com_taxa_ausente"])])
    t1 = _tab(["Raio", "Municípios do a08 sem vizinho no raio", "Vizinhos (p10)", "Vizinhos (mediana)",
               "Vizinhos (p90)", "Municípios com alguma taxa ausente"], linhas)
    linhas = []
    for k in CICLOS:
        x = ir["unidades_municipio_ciclo"][f"ciclo_{k}"]
        linhas.append([str(k), fint(x["municipios_com_vaga_imediata"]), fint(x["com_celula_fora_da_ponte"]),
                       fint(x["celulas_com_vaga_imediata_fora_da_ponte"]), fint(x["so_cursos_fora_da_ponte"]),
                       " / ".join(fint(x[f"raio_{R}_ausente"]) for R in RAIOS)])
    t2 = _tab(["Ciclo", "Municípios com vaga imediata", "Com célula de curso fora da ponte (17 a 20)",
               "Células com vaga imediata fora da ponte", "Só com cursos fora da ponte",
               "Raio ausente (50 / 100 / 200 km)"], linhas)
    return (t1 + "\n\nNa unidade município × ciclo (média ponderada pelas vagas imediatas; decisão 5):\n\n" + t2)


def tab_regra2(resumo: dict, exc: pd.DataFrame) -> str:
    linhas = []
    for rg in resumo["pareamento"]:
        if rg["bloco"] not in ("PH-1", "PH-2"):
            continue
        x = rg["amostra_48h"]
        cats = ", ".join(f"{_uf_txt(c['categoria'])} ({c['unidades']}, todas {c['lado']})"
                         for c in x["categorias_um_lado"]) or "nenhuma"
        dep = ", ".join(_uf_txt(c["categoria"]) for c in x["categorias_um_lado_depois"]) or "nenhuma"
        linhas.append([rg["bloco"], f"{rg['raio_km']} km", _corte_txt(x["corte"]),
                       f"{x['apos_covariavel']['abaixo']} / {x['apos_covariavel']['acima']}", cats,
                       f"{x['saiu_regra2']['abaixo']} / {x['saiu_regra2']['acima']}",
                       f"{_pct(x['fracao_saiu_regra2']['abaixo'])} / {_pct(x['fracao_saiu_regra2']['acima'])}", dep])
    t1 = _tab(["Linha", "Raio", "Corte", "Unidades com todas as covariáveis (abaixo / acima)",
               "Categorias de um lado só (unidades)", "Saíram pela regra 2 (abaixo / acima)",
               "Fração que saiu (abaixo / acima)", "De um lado só depois da saída"], linhas)
    sub = exc[exc["bloco"] == "PH-1"]
    if sub.empty:
        return t1 + "\n\nNa PH-1, ninguém saiu pela regra 2."
    linhas = []
    for (ct,), g in sub.groupby(["corte"], sort=True):
        por = g.groupby(["uf", "lado"], sort=True)
        for (uf, lado), gg in por:
            muns = gg.groupby(["municipio", "co_ibge"], sort=True)["ciclo"].apply(
                lambda s: ", ".join(str(int(c)) for c in sorted(s.dropna())))
            lista = "; ".join(f"{m} (ciclo {c})" if "," not in c else f"{m} (ciclos {c})" for (m, _), c in muns.items())
            linhas.append([_corte_txt(ct), uf, lado, str(len(gg)), lista,
                           ", ".join(sorted({"capital de um lado só" if c == "capital" else
                                             "não capital de um lado só" if c == "nao capital" else
                                             "UF de um lado só" for cs in gg["categorias"] for c in cs.split(";")}))])
    t2 = _tab(["Corte", "UF", "Lado", "Linhas município × ciclo", "Municípios (ciclos)", "Por quê"], linhas)
    return (t1 + "\n\nQuem saiu na PH-1, por UF (lista completa, com a PH-2, em `output/rdd_bolsa/PL_excluidos.csv`):"
            "\n\n" + t2)


def tab_amostra(resumo: dict) -> str:
    linhas = []
    for rg in resumo["pareamento"]:
        x = rg["amostra_48h"]
        procura = "; ".join(f"{k}: {v['procura']} ({v['abaixo']} / {v['acima']})"
                            for k, v in x["lados_que_procuram"].items())
        ps = rg.get("PSM") or {}
        linhas.append([rg["bloco"], f"{rg['raio_km']} km", _nome_exato_doc(rg["exato"]), _corte_txt(x["corte"]),
                       f"{x['na_janela']['abaixo']} / {x['na_janela']['acima']}",
                       f"{x['sem_covariavel']['abaixo']} / {x['sem_covariavel']['acima']}",
                       f"{x['amostra_pareamento']['abaixo']} / {x['amostra_pareamento']['acima']}", procura,
                       fint(len(ps.get("pares") or [])) if "pares" in ps else "—"])
    return _tab(["Linha", "Raio", "Exato", "Corte", "Na janela (abaixo / acima)",
                 "Sem alguma covariável (abaixo / acima)", "No pareamento (abaixo / acima)",
                 "Lado que procura par, por ciclo (abaixo / acima)", "Pares formados"], linhas)


def tab_comparacao(est: pd.DataFrame, pm_est: pd.DataFrame, cl_est: pd.DataFrame) -> str:
    linhas = []
    for c in CORTES:
        ct = ROT_CORTE[c]
        for oid in OUT_H1:
            cel = []
            for r in (CL._uma(cl_est, bloco="PS-1", outcome=oid, corte=ct), CL._uma(pm_est, bloco="PM-1", outcome=oid,
                                                                                    corte=ct),
                      CL._uma(est, bloco="PH-1", outcome=oid, corte=ct),
                      CL._uma(est, bloco="PH-3", outcome=oid, corte=ct)):
                cel.append(f"{fv(r)} {fic(r)} ({fint(r['n_pares'])} pares)" if r["status"] == "EXECUTADO"
                           else "sem estimativa")
            linhas.append([NOME_OUT[oid], _corte_txt(ct)] + cel)
    return _tab(["Outcome", "Corte", "48d: macrorregião no escore, gulosa (PS-1)",
                 "48e: macrorregião no escore, literal, regra 2 (PM-1)",
                 "48h: exato na UF + raio de 100 km (PH-1, principal)", "48h: exato na região de saúde (PH-3)"],
                linhas)


def tab_rdd(est: pd.DataFrame, hi: pd.DataFrame) -> str:
    linhas = []
    for c in CORTES:
        ct = ROT_CORTE[c]
        for oid in ("HI-1", "HI-2"):
            ref = T40._uma(hi, linha=oid, outcome=oid, variante="principal", corte=ct)
            r = CL._uma(est, bloco="PH-4", outcome=oid, corte=ct)
            linhas.append([oid, _corte_txt(ct), f"{_fv_hi(ref)} {_fic_hi(ref)}",
                           f"{fint(r['n_abaixo'])} / {fint(r['n_acima'])}",
                           f"{fint(r['saiu_ausencia_abaixo'])} / {fint(r['saiu_ausencia_acima'])}",
                           f"{fv(r, 'tau_sem_controle')} {fic(r, 'ic_sem_controle_inf', 'ic_sem_controle_sup')}",
                           f"{fv(r)} {fic(r)}", fp(r["p_valor"]), fv(r, "variacao_abs")])
    return _tab(["Linha do 48b", "Corte", "48b (HI_estimativas.csv)", "n abaixo / acima (com UF e raio)",
                 "Saíram por raio ausente (abaixo / acima; células na HI-1)", "Sem controle, mesma amostra",
                 "Com EF de UF e raio (PH-4)", "p", "Variação vs. sem controle"], linhas)


def _fv_hi(r) -> str:
    e, k, u = (100.0, 1, " p.p.") if r["outcome"] == "HI-1" else (1.0, 2, "")
    return fn(e * _f(r["tau"]), k) + u


def _fic_hi(r) -> str:
    e, k = (100.0, 1) if r["outcome"] == "HI-1" else (1.0, 2)
    return f"[{fn(e * _f(r['ic95_inf']), k)}; {fn(e * _f(r['ic95_sup']), k)}]"


def tab_origem(est: pd.DataFrame, resumo: dict) -> str:
    ix = resumo["x1"]
    o = ix["origem_em_celula_com_vaga_imediata"]
    t0 = (f"Médicos ativos ligados da X1 (regra D1, lista de 11/09/2026, ciclos 1 e 2): {ix['registros']} registros; "
          f"{ix['em_celula_com_vaga_imediata']} em células com vaga imediata do quadro, dos quais "
          f"{o.get('mesma_uf', 0)} com origem na mesma UF, {o.get('outra_uf', 0)} de outra UF e "
          f"{o.get('desconhecida', 0)} com origem desconhecida; {ix['em_celula_so_cadastro_reserva']} em células só de "
          f"cadastro reserva e {ix['sem_celula_no_quadro']} sem célula no quadro (fora da PH-5).")
    linhas = []
    for x in resumo["ph5_medias"]:
        linhas.append([_corte_txt(x["corte"]), fint(x["pares_ciclos_1_2"]),
                       f"{fn(x['abaixo']['mesma_uf'], 2, False)} / {fn(x['acima']['mesma_uf'], 2, False)}",
                       f"{fn(x['abaixo']['outra_uf'], 2, False)} / {fn(x['acima']['outra_uf'], 2, False)}",
                       f"{fn(x['abaixo']['desconhecida'], 2, False)} / {fn(x['acima']['desconhecida'], 2, False)}",
                       f"{fn(x['abaixo']['aloc'], 2, False)} / {fn(x['acima']['aloc'], 2, False)}"])
    t1 = _tab(["Corte", "Pares dos ciclos 1 e 2", "Mesma UF por vaga imediata (abaixo / acima)",
               "Outra UF por vaga imediata (abaixo / acima)", "Origem desconhecida por vaga imediata (abaixo / acima)",
               "Y2: alocados da 1ª chamada por vaga imediata (abaixo / acima)"], linhas)
    linhas = []
    for x in resumo["ph5_medias"]:
        for oid in OUT_PH5:
            g = x["sinais"][oid]
            linhas.append([_corte_txt(x["corte"]), NOME_CURTO[oid], fint(g["pares"]), fint(g["diferentes_de_zero"]),
                           fint(g["acima_maior"]), fint(g["abaixo_maior"]), fp(g["p_minimo_permutacao"])])
    t2 = _tab(["Corte", "Origem", "Pares com outcome", "Pares com diferença", "Lado de bolsa maior com mais",
               "Lado de bolsa menor com mais", "Menor p possível no teste de sinais"], linhas)
    return (t0 + "\n\nMédia nos pares da PH-1 (descritivo):\n\n" + t1 + "\n\nEm quantos pares há diferença (o teste "
            "de permutação só usa esses pares; com poucos, o p não consegue ficar abaixo de certo valor):\n\n" + t2
            + "\n\n" + tab_linhas(est, ("PH-5",)))


ROT_BAL = {"capital": "capital", "log_pop": "log(população)", "med": "médicos /10 mil (município)",
           "esp": "especialistas CBO-alvo /10 mil (município)", "raio": "especialistas do curso /10 mil (raio)",
           "uf": "UF (maior DP absoluta entre as UFs)"}


def resumo_balanco(bal: pd.DataFrame, bloco_: str, corte: str, raio: int, exato: str) -> list[dict]:
    g = bal[(bal["bloco"] == bloco_) & (bal["corte"].astype(str) == corte) & (bal["raio_km"].astype(int) == raio)
            & (bal["exato"].astype(str).str.startswith(exato))]
    out = []
    for v in ("log_pop", "med", "esp", "raio", "capital"):
        x = g[g["variavel"] == v]
        out.append({"variavel": v, "antes": _f(x["dp_antes"].iloc[0]) if len(x) else np.nan,
                    "depois": _f(x["dp_depois"].iloc[0]) if len(x) else np.nan})
    u = g[g["variavel"].astype(str).str.startswith("uf_")]
    out.append({"variavel": "uf", "antes": float(u["dp_antes"].abs().max()) if len(u) else np.nan,
                "depois": float(u["dp_depois"].abs().max()) if len(u) and u["dp_depois"].notna().any() else np.nan})
    return out


def tab_balanco(bal: pd.DataFrame, est: pd.DataFrame) -> str:
    linhas = []
    for s in specs():
        ct = ROT_CORTE[s["corte"]]
        rb = resumo_balanco(bal, s["bloco"], ct, s["raio"], s["exato"])
        r = CL._uma(est, bloco=s["bloco"], outcome="H1M-FRAC", corte=ct, raio_km=s["raio"])
        linhas.append([s["bloco"], f"{s['raio']} km", _nome_exato_doc(s["exato"]), _corte_txt(ct), fint(r["n_pares"])]
                      + [f"{fn(abs(x['antes']), 2, False)} → {fn(abs(x['depois']), 2, False)}" for x in rb]
                      + [_limpa(r)])
    return _tab(["Linha", "Raio", "Exato", "Corte", "Pares"] + [ROT_BAL[v] for v in ("log_pop", "med", "esp", "raio",
                                                                                     "capital", "uf")]
                + ["Maior DP absoluta depois"], linhas)


def leitura_txt(resumo: dict) -> str:
    le = resumo["leitura"]
    linhas = [["§3, 1ª e 2ª linhas", f"PH-1 {NOME_OUT[x['outcome']]}", _corte_txt(x["corte"]), f"`{x['codigo']}`"]
              for x in le["linhas"]]
    linhas.append(["§3, 1ª linha (as quatro juntas)", "PH-1", "0,300 e 0,400", f"`{le['geral']}`"])
    for x in le["parte_comparavel"]:
        linhas.append(["§3, 3ª linha", "PH-1", _corte_txt(x["corte"]), f"`{x['codigo']}` (lado {', '.join(x['lados'])})"])
    if not le["parte_comparavel"]:
        linhas.append(["§3, 3ª linha", "PH-1", "0,300 e 0,400", "a regra 2 não tira mais de 25% de nenhum lado"])
    for x in le["ph5"]:
        linhas.append(["§3, 4ª linha", "PH-5 outra UF", _corte_txt(x["corte"]), f"`{x['codigo']}`"])
    return _tab(["Regra", "Linha", "Corte", "Código"], linhas)


def _frase(r) -> str:
    if r["status"] != "EXECUTADO":
        return f"{NOME_CURTO[r['outcome']]}: sem estimativa"
    limpa = "balanço limpo" if r["comparacao_limpa"] == "SIM" else "balanço **não** limpo (|DP| > 0,25 depois)"
    return (f"{NOME_CURTO[r['outcome']]} {fv(r)} (IC {fic(r)}; p Holm {fp(r['p_holm'])}; {fint(r['n_pares'])} pares; "
            f"{limpa})")


def _saida_uf(resumo: dict, exc: pd.DataFrame, corte: str) -> str:
    am = _am(resumo, "PH-1", corte)
    n_ab, n_ac = am["saiu_regra2"]["abaixo"], am["saiu_regra2"]["acima"]
    if n_ab + n_ac == 0:
        return "ninguém saiu"
    sub = exc[(exc["bloco"] == "PH-1") & (exc["corte"].astype(str) == corte)]
    partes = []
    for lado in ("abaixo", "acima"):
        g = sub[sub["lado"] == lado]
        if g.empty:
            continue
        ufs = ", ".join(f"{uf} ({n})" for uf, n in g.groupby("uf").size().sort_index().items())
        partes.append(f"{len(g)} do lado {'de bolsa menor' if lado == 'abaixo' else 'de bolsa maior'} "
                      f"({_pct(am['fracao_saiu_regra2'][lado])} desse lado): {ufs}")
    return "; ".join(partes)


def resposta_curta(est: pd.DataFrame, exc: pd.DataFrame, resumo: dict, pm_est: pd.DataFrame,
                   hi: pd.DataFrame) -> str:
    le = resumo["leitura"]
    partes = []
    if le["geral"] == "NAO_SE_DETECTA_DIFERENCA":
        cab = ("**Comparando municípios da mesma UF e com o mesmo estoque de especialistas no entorno, não se detecta "
               "diferença de preenchimento nos dois cortes.** As quatro linhas principais (PH-1) têm intervalo que "
               "contém zero e balanço limpo depois do pareamento.")
    elif le["geral"] == "REJEITA_ZERO_DEPOIS_DO_HOLM":
        rej = [x for x in le["linhas"] if x["codigo"] == "REJEITA_ZERO_DEPOIS_DO_HOLM"]
        cab = ("**Alguma linha principal rejeita zero depois do Holm**: " + "; ".join(
            f"{NOME_OUT[x['outcome']]} em {_corte_txt(x['corte'])} ({'maior' if x['tau'] > 0 else 'menor'} do lado de "
            f"bolsa maior; p Holm {fp(x['p_holm'])})" for x in rej) + ". O que se mede é o pacote do corte.")
    else:
        motivos = {"SEM_ESTIMATIVA": "sem estimativa", "BALANCO_NAO_LIMPO": "balanço não limpo",
                   "IC_EXCLUI_ZERO_SEM_HOLM": "intervalo sem zero, mas sem rejeitar zero depois do Holm"}
        fora = [x for x in le["linhas"] if x["codigo"] != "IC_CONTEM_ZERO_BALANCO_LIMPO"]
        cab = ("**Nenhuma linha principal rejeita zero depois do Holm, mas a primeira leitura do §3 não vale para as "
               "quatro**: " + "; ".join(f"{NOME_OUT[x['outcome']]} em {_corte_txt(x['corte'])}: {motivos[x['codigo']]}"
                                       for x in fora) + ".")
    partes.append(cab)
    for c in CORTES:
        ct = ROT_CORTE[c]
        fr = [_frase(CL._uma(est, bloco="PH-1", outcome=oid, corte=ct)) for oid in OUT_H1]
        partes.append(f"- **Corte {TXT_CORTE[c]}** ({BOLSA[c]}), lado de bolsa maior − lado de bolsa menor: "
                      + "; ".join(fr) + ".")
    # Em palavras simples.
    simples = []
    for c in CORTES:
        ct = ROT_CORTE[c]
        r1 = CL._uma(est, bloco="PH-1", outcome="H1M-FRAC", corte=ct)
        r2 = CL._uma(est, bloco="PH-1", outcome="H1M-ALOC", corte=ct)
        if r1["status"] == "EXECUTADO" and r2["status"] == "EXECUTADO":
            simples.append(
                f"em {TXT_CORTE[c]}, entre municípios parecidos, o lado de bolsa maior preencheu "
                f"{fn(abs(100 * _f(r1['tau'])), 1, False)} p.p. {'a mais' if _f(r1['tau']) > 0 else 'a menos'} das "
                f"células com vaga imediata (intervalo de {fn(100 * _f(r1['ic95_inf']), 1)} a "
                f"{fn(100 * _f(r1['ic95_sup']), 1)} p.p., que " + ("inclui" if _contem_zero(r1) else "não inclui")
                + f" o zero) e teve {fn(abs(_f(r2['tau'])), 2, False)} médico por vaga imediata "
                f"{'a mais' if _f(r2['tau']) > 0 else 'a menos'} (intervalo de {fn(_f(r2['ic95_inf']), 2)} a "
                f"{fn(_f(r2['ic95_sup']), 2)}, que " + ("inclui" if _contem_zero(r2) else "não inclui") + " o zero)")
    if simples:
        partes.append("**Em palavras simples:** " + "; ".join(simples) + ". Intervalo que inclui o zero quer dizer "
                      "que os dados não distinguem a diferença de zero; não quer dizer que ela seja zero.")
    partes.append("**Quem saiu pela regra 2 (UF ou capital que só aparece de um lado do corte):** " + " ".join(
        f"Em {TXT_CORTE[c]}, {_saida_uf(resumo, exc, ROT_CORTE[c])}." for c in CORTES)
        + " A lista com os nomes está na seção 2.")
    if le["parte_comparavel"]:
        partes.append("**A comparação vale só para as UFs presentes dos dois lados:** " + "; ".join(
            f"em {_corte_txt(x['corte'])}, a regra 2 tirou mais de 25% do lado "
            f"{' e do lado '.join('de bolsa menor' if l_ == 'abaixo' else 'de bolsa maior' for l_ in x['lados'])} "
            f"({', '.join(_pct(v) for v in x['fracao'].values())})" for x in le["parte_comparavel"])
            + ". Ali, o resultado não fala dos municípios dessas UFs.")
    else:
        partes.append("**Parte comparável:** em nenhum corte a regra 2 tirou mais de 25% de um lado; mesmo assim, a "
                      "comparação vale só para as UFs (e a condição de capital) presentes dos dois lados do corte.")
    # 48e × 48h.
    comp = []
    for c in CORTES:
        ct = ROT_CORTE[c]
        for oid in OUT_H1:
            a = CL._uma(pm_est, bloco="PM-1", outcome=oid, corte=ct)
            r = CL._uma(est, bloco="PH-1", outcome=oid, corte=ct)
            if a["status"] == "EXECUTADO" and r["status"] == "EXECUTADO":
                comp.append(f"{NOME_CURTO[oid]} em {TXT_CORTE[c]}: {fv(a)} no 48e → {fv(r)} aqui")
    mesma = all(_contem_zero(CL._uma(pm_est, bloco="PM-1", outcome=o, corte=ROT_CORTE[c]))
                == _contem_zero(CL._uma(est, bloco="PH-1", outcome=o, corte=ROT_CORTE[c]))
                for c in CORTES for o in OUT_H1)
    troca = [f"{NOME_CURTO[o]} em {TXT_CORTE[c]}" for c in CORTES for o in OUT_H1
             if _f(CL._uma(pm_est, bloco="PM-1", outcome=o, corte=ROT_CORTE[c])["tau"])
             * _f(CL._uma(est, bloco="PH-1", outcome=o, corte=ROT_CORTE[c])["tau"]) < 0]
    partes.append("**Do 48e (macrorregião) para o 48h (UF + entorno):** " + "; ".join(comp) + ". "
                  + ("A conclusão sobre o zero é a mesma nas quatro linhas: apertar a localização não muda a leitura."
                     if mesma else "A conclusão sobre o zero muda em alguma linha; ver a seção 4.1.")
                  + (" O sinal do ponto muda em " + ", ".join(troca) + (
                      "; como os intervalos dos dois lados contêm zero, a troca de sinal não é informativa."
                      if mesma and all(_contem_zero(CL._uma(est, bloco="PH-1", outcome=o, corte=ROT_CORTE[c]))
                                       for c in CORTES for o in OUT_H1) else ".") if troca else ""))
    # PH-4.
    ph4 = []
    for c in CORTES:
        ct = ROT_CORTE[c]
        for oid in ("HI-1", "HI-2"):
            r = CL._uma(est, bloco="PH-4", outcome=oid, corte=ct)
            ph4.append(f"{oid} em {TXT_CORTE[c]}: {fv(r, 'tau_sem_controle')} sem controle → {fv(r)} {fic(r)} com UF e "
                       "raio")
    partes.append("**Com a reta (RDD do 48b com efeito fixo de UF e o raio, PH-4):** " + "; ".join(ph4) + ".")
    # PH-5.
    f5 = []
    for c in CORTES:
        ct = ROT_CORTE[c]
        m = CL._uma(est, bloco="PH-5", outcome="H1M-MESMA-UF", corte=ct)
        o = CL._uma(est, bloco="PH-5", outcome="H1M-OUTRA-UF", corte=ct)
        cod = next(x["codigo"] for x in le["ph5"] if x["corte"] == ct)
        if o["status"] != "EXECUTADO":
            f5.append(f"em {TXT_CORTE[c]}, sem estimativa")
            continue
        g = next(x for x in resumo["ph5_medias"] if x["corte"] == ct)["sinais"]["H1M-OUTRA-UF"]
        f5.append(f"em {TXT_CORTE[c]}, médicos de outra UF por vaga imediata {fv(o)} (IC {fic(o)}; p "
                  f"{fp(o['p_valor'])}; q BKY {fp(o['q_bky'])}) e da mesma UF {fv(m)} (IC {fic(m)}), em "
                  f"{fint(o['n_pares'])} pares dos ciclos 1 e 2; só {g['diferentes_de_zero']} pares têm alguma diferença "
                  f"de médicos de outra UF ({g['acima_maior']} com mais do lado de bolsa maior, {g['abaixo_maior']} do "
                  f"lado de bolsa menor) (`{cod}`)")
    algum = any(x["codigo"] == "INDICIO_ATRAI_DE_LONGE" for x in le["ph5"])
    partes.append("**De onde vem o médico (PH-5, descritiva):** " + "; ".join(f5) + ". "
                  + ("Há indício de que o lado de bolsa maior recebe mais médicos de outra UF, mesmo sem mudar o "
                     "total." if algum else "Pela regra do §3 não há indício de que o lado de bolsa maior receba mais "
                     "médicos de outra UF: nenhum intervalo exclui o zero.")
                  + (" " + _frase_ph5_poder(est, resumo) if not algum and _frase_ph5_poder(est, resumo) else "")
                  + " A origem vem da X1 (ativos em 11/09/2026), não exatamente dos alocados da 1ª chamada.")
    partes.append("Tudo é robustez pós-resultado e se refere ao pacote do corte, não à bolsa isolada. O principal da H1 "
                  "continua o 48b.")
    return "\n\n".join(partes)


def _largura(r) -> float:
    return _f(r["ic95_sup"]) - _f(r["ic95_inf"])


def _mde(r) -> float:
    """Diferença mínima detectável (80% de poder, 5% bicaudal) pelo t pareado: (t_0,975 + t_0,80) × EP, com o EP
    tirado do IC t gravado. Auditoria 47: só texto, calculado das saídas."""
    from scipy import stats
    n = int(_f(r["n_pares"]))
    if r["status"] != "EXECUTADO" or n < 2:
        return float("nan")
    tc = float(stats.t.ppf(0.975, n - 1))
    ep = (_f(r["ic_t_sup"]) - _f(r["ic_t_inf"])) / (2 * tc)
    return (tc + float(stats.t.ppf(0.80, n - 1))) * ep


def _pares_por_ciclo(rg: dict) -> dict[int, int]:
    out = {k: 0 for k in CICLOS}
    for p in (rg.get("PSM") or {}).get("pares") or []:
        out[int(p["acima"].split("|c")[1])] += 1
    return out


def _pares_possiveis_sem_caliper(rg: dict) -> int:
    """Máximo de pares no estrato exato (UF, capital, ciclo) entre as unidades no suporte comum, sem o caliper:
    soma, por estrato, do menor lado. Auditoria 47 (só contagem; nenhum outcome)."""
    caps = set(CL.T41.A36.CAPITAIS)
    e = rg["escore_por_unidade"]
    lo, hi = rg["PSM"]["suporte_comum"]
    cont: dict[str, list[int]] = {}
    for i, a, p in zip(e["id"], e["acima"], e["escore"]):
        if not (lo - 1e-9 <= p <= hi + 1e-9):
            continue
        k = f"{i[:2]}|{int(i[:6] in caps)}|{i.split('|c')[1]}"
        cont.setdefault(k, [0, 0])[0 if a else 1] += 1
    return sum(min(v) for v in cont.values())


def _frase_ponto(est: pd.DataFrame, res: dict) -> str:
    """O ponto da fração preenchida comparado com a diferença mínima detectável e com os pares do 48e (auditoria
    47): o ponto de poucos pares não é tamanho de efeito."""
    pm_res = PM.ler_saidas()[3]
    itens = []
    for c in CORTES:
        ct = ROT_CORTE[c]
        r = CL._uma(est, bloco="PH-1", outcome="H1M-FRAC", corte=ct)
        if r["status"] != "EXECUTADO" or not abs(_f(r["tau"])) < _mde(r):
            continue
        a = next(x for x in pm_res["pareamento"] if x["bloco"] == "PM-1" and x["parte"] == "H1" and x["corte"] == ct)
        h = next(x for x in res["pareamento"] if x["bloco"] == "PH-1" and x["corte"] == ct)
        comuns = len({(p["acima"], p["abaixo"]) for p in a["PSM"]["pares"]}
                     & {(p["acima"], p["abaixo"]) for p in h["PSM"]["pares"]})
        itens.append(f"{fv(r)} em {TXT_CORTE[c]}, com {comuns} {'par' if comuns == 1 else 'pares'} em comum com os "
                     f"{len(a['PSM']['pares'])} do 48e")
    if not itens:
        return ""
    return (" O ponto da fração preenchida fica abaixo dessa diferença mínima e vem de outro conjunto de pares: "
            + "; ".join(itens) + ". Ele não deve ser lido como tamanho de efeito.")


def _frase_ph5_poder(est: pd.DataFrame, resumo: dict) -> str:
    """Quando todos os pares com diferença vão no mesmo sentido e o menor p possível passa de 5%, diz isso: o teste
    não rejeita, mas o dado também não mostra ausência (auditoria 47)."""
    partes = []
    for x in resumo["ph5_medias"]:
        g = x["sinais"]["H1M-OUTRA-UF"]
        if g["diferentes_de_zero"] == 0 or g["p_minimo_permutacao"] <= ALFA:
            continue
        if g["abaixo_maior"] == 0 or g["acima_maior"] == 0:
            lado = "de bolsa maior" if g["abaixo_maior"] == 0 else "de bolsa menor"
            o = CL._uma(est, bloco="PH-5", outcome="H1M-OUTRA-UF", corte=x["corte"])
            lim = (" O limite do intervalo mostrado como 0,00 é o próprio zero: o teste não o rejeita."
                   if abs(_f(o["ic95_inf"])) < 0.005 or abs(_f(o["ic95_sup"])) < 0.005 else "")
            partes.append(f"Em {_corte_txt(x['corte'])}, os {g['diferentes_de_zero']} pares com alguma diferença têm "
                          f"todos mais médicos de outra UF do lado {lado}; com {g['diferentes_de_zero']} pares, o "
                          f"menor p possível é {fn(g['p_minimo_permutacao'], 4, False)}, acima de 5%. O teste não "
                          "consegue separar esse padrão do acaso, e o dado também não mostra que ele não exista." + lim)
    return " ".join(partes)


def interpretacao(est: pd.DataFrame, resumo: dict, pm_est: pd.DataFrame, hi: pd.DataFrame) -> str:
    """O que dá para dizer e o que não dá, em linguagem simples, por regras fixas sobre as saídas."""
    le = resumo["leitura"]
    itens = []
    itens.append("**A pergunta.** A diferença de preenchimento no corte poderia vir de comparar municípios de lugares "
                 "diferentes (outra UF, capital × interior) ou com mais ou menos especialistas por perto. Aqui cada "
                 "município só é comparado com outro da mesma UF, na mesma condição de capital e parecido em população, "
                 "médicos e especialistas a até 100 km.")
    sinais = []
    for c in CORTES:
        r = CL._uma(est, bloco="PH-1", outcome="H1M-FRAC", corte=ROT_CORTE[c])
        if r["status"] == "EXECUTADO":
            sinais.append(f"em {TXT_CORTE[c]} o ponto da fração preenchida é "
                          f"{'positivo' if _f(r['tau']) > 0 else 'negativo'}, {fv(r)}")
    if le["geral"] == "NAO_SE_DETECTA_DIFERENCA":
        itens.append("**O resultado.** Feita essa comparação, não aparece diferença que se distinga de zero em nenhum "
                     "dos dois cortes, nem na fração de vagas preenchidas nem nos médicos por vaga (" + "; ".join(sinais)
                     + ")." + "".join(
                         f" A queda da RDD do 48b em {TXT_CORTE[c]} ({_fv_hi(h_)} na célula) não reaparece."
                         for c in CORTES for h_ in [T40._uma(hi, linha="HI-1", outcome="HI-1", variante="principal",
                                                             corte=ROT_CORTE[c])]
                         if _f(h_["tau"]) < 0 and not _contem_zero(h_)))
    elif le["geral"] == "REJEITA_ZERO_DEPOIS_DO_HOLM":
        itens.append("**O resultado.** Alguma linha principal se distingue de zero depois do Holm (" + "; ".join(sinais)
                     + "); ver a seção 4.")
    else:
        itens.append("**O resultado.** Nenhuma linha principal se distingue de zero depois do Holm, mas a primeira "
                     "leitura do §3 não vale para todas (" + "; ".join(sinais) + "); ver a seção 9.")
    pares, larg, possiveis, ciclos, mdes = [], [], [], [], []
    for c in CORTES:
        ct = ROT_CORTE[c]
        a = CL._uma(pm_est, bloco="PM-1", outcome="H1M-FRAC", corte=ct)
        r = CL._uma(est, bloco="PH-1", outcome="H1M-FRAC", corte=ct)
        r2 = CL._uma(est, bloco="PH-1", outcome="H1M-ALOC", corte=ct)
        rg = next(x for x in resumo["pareamento"] if x["bloco"] == "PH-1" and x["corte"] == ct)
        pares.append(f"{fint(r['n_pares'])} pares em {TXT_CORTE[c]} (no 48e, {fint(a['n_pares'])})")
        possiveis.append(f"até {_pares_possiveis_sem_caliper(rg)} em {TXT_CORTE[c]}")
        pc = _pares_por_ciclo(rg)
        ciclos.append(f"{' / '.join(str(pc[k]) for k in CICLOS)} em {TXT_CORTE[c]}")
        mdes.append(f"em {TXT_CORTE[c]}, cerca de {fn(100 * _mde(r), 0, False)} p.p. na fração preenchida (o lado de "
                    f"baixo dos pares preencheu {fn(100 * _f(r['media_abaixo']), 0, False)}% das células) e "
                    f"{fn(_mde(r2), 2, False)} médico por vaga imediata")
        if np.isfinite(_largura(a)) and _largura(a) > 0 and np.isfinite(_largura(r)):
            larg.append(f"{fn(_largura(r) / _largura(a), 1, False)} vezes a largura do 48e em {TXT_CORTE[c]}")
    itens.append("**O preço.** Comparar dentro da mesma UF, com o *caliper* do 48e (0,2 desvio-padrão do logit do "
                 "escore), deixa poucos pares: " + "; ".join(pares) + ". Sem o *caliper*, a mesma UF, capital e ciclo "
                 "permitiriam " + "; ".join(possiveis) + ": o que mais corta pares é o *caliper*, estreito porque o "
                 "escore varia pouco. Os pares ficam sobretudo no ciclo 2 (ciclos 1 / 2 / 3: " + "; ".join(ciclos)
                 + "). O intervalo da fração preenchida fica com " + "; ".join(larg)
                 + ". Com esses pares, a menor diferença com 80% de chance de aparecer como diferente de zero (a 5%) "
                   "fica assim: "
                 + "; ".join(mdes) + ". Não detectar diferença com tão poucos pares é um resultado fraco: diz que os "
                 "dados não mostram diferença, não que ela não exista." + _frase_ponto(est, resumo))
    p2 = est[est["bloco"] == "PH-2"]
    p3 = est[est["bloco"] == "PH-3"]
    z2 = all(r["status"] == "EXECUTADO" and _contem_zero(r) for _, r in p2.iterrows())
    nl2 = [f"{int(r['raio_km'])} km ({_corte_txt(r['corte'])})" for _, r in p2.iterrows()
           if r["outcome"] == "H1M-FRAC" and r["comparacao_limpa"] != "SIM"]
    itens.append("**Outros raios e a região de saúde.** " + (
        "Com raio de 50 ou de 200 km (PH-2), todos os intervalos contêm zero." if z2 else
        "Com raio de 50 ou de 200 km (PH-2), algum intervalo não contém zero (seção 5).")
        + (" O balanço não fica limpo (alguma |DP| acima de 0,25 depois) com " + ", ".join(nl2) + "." if nl2 else "")
        + " Exigir a mesma região de saúde (PH-3) quase não forma par ("
        + "; ".join(f"{fint(r['n_pares'])} em {_corte_txt(r['corte'])}" for _, r in p3.iterrows()
                    if r["outcome"] == "H1M-FRAC") + "): na mesma região de saúde e dentro do *caliper* quase não "
        "sobra par dos dois lados do corte, e a PH-3 não informa.")
    rd = []
    for c in CORTES:
        ct = ROT_CORTE[c]
        for oid in ("HI-1", "HI-2"):
            ref = T40._uma(hi, linha=oid, outcome=oid, variante="principal", corte=ct)
            r = CL._uma(est, bloco="PH-4", outcome=oid, corte=ct)
            z0, z1 = _contem_zero(ref), _contem_zero(r)
            if not z0 and z1:
                rd.append(f"{oid} em {TXT_CORTE[c]} tinha intervalo sem zero no 48b ({_fv_hi(ref)}) e passa a conter "
                          f"zero com UF e raio ({fv(r)} {fic(r)}); na mesma amostra, sem controle, ainda é "
                          f"{fv(r, 'tau_sem_controle')} {fic(r, 'ic_sem_controle_inf', 'ic_sem_controle_sup')}, então "
                          "o que muda é o controle, não a amostra")
            elif not z0 and not z1:
                rd.append(f"{oid} em {TXT_CORTE[c]} continua com intervalo sem zero com UF e raio ({fv(r)} {fic(r)})")
            elif z0 and not z1:
                rd.append(f"{oid} em {TXT_CORTE[c]} passa a ter intervalo sem zero com UF e raio ({fv(r)} {fic(r)})")
    itens.append("**E a reta (RDD)?** " + ("; ".join(rd) + "." if rd else "Na RDD com efeito fixo de UF e o raio, "
                                          "nenhuma das quatro linhas muda de leitura sobre o zero em relação ao 48b.")
                 + " A RDD usa todos os municípios da janela, com peso maior perto do corte; o pareamento usa só os "
                   "pares formados.")
    algum = any(x["codigo"] == "INDICIO_ATRAI_DE_LONGE" for x in le["ph5"])
    g = {x["corte"]: x["sinais"]["H1M-OUTRA-UF"] for x in resumo["ph5_medias"]}
    itens.append("**De onde vem o médico.** " + (
        "Há indício de que o lado de bolsa maior recebe mais médicos de outra UF." if algum else
        "Não há indício firme de que o lado de bolsa maior receba mais médicos de outra UF.") + " Médico de outra UF é raro nos "
        "pares: " + "; ".join(f"em {_corte_txt(k)}, só {v['diferentes_de_zero']} de {v['pares']} pares têm alguma "
                              f"diferença ({v['acima_maior']} com mais do lado de bolsa maior)" for k, v in g.items())
        + ". Com tão poucos pares informativos, o teste não tem como ser conclusivo."
        + (" " + _frase_ph5_poder(est, resumo) if not algum and _frase_ph5_poder(est, resumo) else ""))
    itens.append("**O que não dá para dizer.** Que a bolsa não tem efeito (não detectar não é zero); que o resultado "
                 "isola os R$ 5 mil (em 0,300 e 0,400 muda um pacote de regras); que vale para as UFs que só aparecem "
                 "de um lado do corte (saíram pela regra 2).")
    return "\n".join(f"- {x}" for x in itens)


def gerar_blocos(est, bal, exc, resumo, pm_est, cl_est, hi) -> dict[str, str]:
    figs = "\n\n".join(f"![{Path(f['arquivo']).stem}](../../{f['arquivo']})\n\n**{f['como_ler']}**"
                       for f in resumo["figuras"])
    lim = [
        "**Pós-resultado.** A H1 e os pareamentos por macrorregião (48d, 48e) já tinham sido vistos quando o 48h foi "
        "congelado. As regras foram fixadas antes destas contas, mas a pergunta não é cega ao resultado.",
        "**Pacote do corte.** Em 0,300 e 0,400 mudam a bolsa e outras regras federais (auditoria 18). Nem a RDD nem o "
        "pareamento removem esse pacote nem isolam o incentivo de R$ 5 mil.",
        "**O que o pareamento supõe.** Que, perto do corte, na mesma UF e com população, médicos e entorno parecidos, "
        "estar de um lado ou do outro é como sorteado (randomização local condicional). O IVS não entra no escore; a "
        "suposição inclui que a diferença de IVS entre os lados, dentro da janela, não pesa no outcome.",
        "**Exato na UF reduz quem é comparado.** Só formam par municípios de UFs (e condição de capital) presentes dos "
        "dois lados. O estimando é a média nos pares formados, não a de toda a janela.",
        "**O raio é uma medida de oferta no entorno, não de mercado de trabalho.** Conta vínculos do CNES (um médico "
        "em dois estabelecimentos conta duas vezes), nos municípios cujo centroide está a até 100 km, sem olhar "
        "estradas ou tempo de viagem. Municípios criados depois de 2010 (fora do a08) não entram, como no 44.",
        "**Cursos fora da ponte.** Os cursos 17 a 20 do ciclo 3 não têm CBO-alvo na ponte do a09 e ficam fora da média "
        "do raio da unidade (seção 1.2). O município × ciclo que só tem vaga imediata nesses cursos fica sem o raio e "
        "sai do pareamento (entra em \"sem alguma covariável\", seção 3); a auditoria 47 conta essa perda por lado do "
        "corte. Ela ajuda a explicar por que quase não há par do ciclo 3.",
        "**PH-5 não é a divisão exata de Y2.** Y2 conta os alocados da 1ª chamada; a origem vem da X1, que liga os "
        "médicos ativos em 11/09/2026 ao CNES (regra D1). Só ciclos 1 e 2; parte dos médicos tem origem desconhecida. "
        "É descritiva.",
        "**IC de permutação com muitos pares iguais.** Na PH-5, a maioria dos pares não tem médico de outra UF nos dois "
        "lados (diferença zero). O teste de sinais só usa os pares com diferença, e com poucos deles o p não consegue "
        "ficar baixo (seção 7); já fora do zero todos os pares passam a contar, e o IC pode sair estreito mesmo com p "
        "alto. Ler o p e a contagem de pares com diferença junto com o IC.",
        "**Poucos municípios e o mesmo município em ciclos diferentes.** A permutação trata os pares como "
        "independentes, e um município pode estar em pares de ciclos diferentes.",
    ]
    return {
        "resposta_curta": resposta_curta(est, exc, resumo, pm_est, hi),
        "interpretacao": interpretacao(est, resumo, pm_est, hi),
        "portao": tab_portao(resumo),
        "raio": tab_raio(resumo),
        "regra2": tab_regra2(resumo, exc),
        "amostra": tab_amostra(resumo),
        "principais": tab_linhas(est, ("PH-1",)),
        "comparacao": tab_comparacao(est, pm_est, cl_est),
        "sensibilidades": tab_linhas(est, ("PH-2", "PH-3")),
        "rdd": tab_rdd(est, hi),
        "origem": tab_origem(est, resumo),
        "balanco": tab_balanco(bal, est),
        "leitura": leitura_txt(resumo),
        "figuras": figs,
        "limites": "\n".join(f"- {x}" for x in lim),
    }


MARCA = re.compile(r"<!-- PL:(?P<nome>[A-Za-z0-9_]+):inicio -->\n(?P<corpo>.*?)\n?<!-- PL:(?P=nome):fim -->", re.S)


def atualizar_doc(est, bal, exc, resumo, pm_est, cl_est, hi) -> None:
    txt = DOC.read_text(encoding="utf-8")
    blocos = gerar_blocos(est, bal, exc, resumo, pm_est, cl_est, hi)
    falta = set(blocos) - {m.group("nome") for m in MARCA.finditer(txt)}
    if falta:
        raise FalhaValidacao(f"doc 57w sem os marcadores {sorted(falta)}")
    DOC.write_text(MARCA.sub(lambda m: bloco(m.group("nome"), blocos[m.group("nome")]) if m.group("nome") in blocos
                             else m.group(0), txt), encoding="utf-8")


# ---------------------------------------------------------------------------
# 6. Figuras
# ---------------------------------------------------------------------------

FONTE = ("Fonte: outcomes do 12 (ciclos 1–3; ciclo 2 pelo quadro de 13/02/2026), CNES a09 (2024-06 a 2025-06), Censo "
         "2022, centroides do IBGE (malha 2022), X1 (17), IVS 2010 oficial (a08); HI_ (48b) e PM_ (48e). EMPIRICO · "
         "scripts/rdd_bolsa/49_pareamento_localizacao.py")
COMO_LER = {
    "PL_principal.png": (
        "Como ler: cada ponto é a diferença entre o lado de bolsa maior e o de bolsa menor; a barra é o IC 95%. Em cada "
        "painel, de cima para baixo: a RDD do 48b sem controle (reta local de cada lado), a RDD com efeito fixo de UF e "
        "o raio (PH-4), o pareamento do 48e (macrorregião e médicos da região no escore) e o pareamento deste adendo "
        "(mesma UF e mesma condição de capital, com os especialistas a até 100 km no escore; o principal). A RDD de "
        "alocados mede médicos por município (com controle das vagas) e fica num painel à parte; o pareamento mede "
        "médicos por vaga imediata. Barra que cruza o zero: não se detecta diferença, o que não quer dizer que ela "
        "seja zero. Pacote do corte, não só a bolsa."),
    "PL_balanco.png": (
        "Como ler: diferença padronizada (lado de cima − lado de baixo, em desvios-padrão, em valor absoluto) de cada "
        "variável, antes do pareamento (cinza) e depois do pareamento deste adendo (azul), janela de 0,050. Na linha "
        "da UF, a maior diferença entre as UFs. Linhas tracejadas: meta de 0,10 e limite de 0,25; acima de 0,25 a "
        "comparação não é lida como limpa. Capital e UF ficam em zero depois porque o par é feito dentro da mesma UF."),
    "PL_origem.png": (
        "Como ler: nos pares da PH-1 dos ciclos 1 e 2, médicos ativos (X1) em células com vaga imediata por vaga "
        "imediata, pela origem antes do programa: da mesma UF da vaga (azul), de outra UF (laranja) e de origem "
        "desconhecida (cinza). Cada barra é a média de um lado do corte. O texto à direita traz a diferença (lado de "
        "bolsa maior − lado de bolsa menor) de médicos de outra UF e da mesma UF, com IC 95% de permutação. "
        "Descritivo; a X1 conta ativos em 11/09/2026, não exatamente os alocados da 1ª chamada."),
}


def _rodape(fig, texto: str, W: float, H_: float, largura: int) -> None:
    linhas = textwrap.wrap(texto, largura)
    yy = 0.24 + 0.24 * len(linhas)
    for t in linhas:
        fig.text(0.1 / W, yy / H_, t, fontsize=10.5, color=CL.TINTA, va="top")
        yy -= 0.24
    fig.text(0.1 / W, 0.04 / H_, FONTE, fontsize=7.5, color=CL.CINZA, va="bottom")


def _it(r, rot: str, esc: float, casas: int) -> dict:
    it = CL._it(r, rot, esc, casas)
    if r["status"] != "EXECUTADO":
        it["valor"] = "sem estimativa"
    return it


def _it_rdd(r, rot: str, esc: float, casas: int, col="tau", lo="ic95_inf", hi_="ic95_sup") -> dict:
    x = {"status": r["status"], "tau": r[col], "ic95_inf": r[lo], "ic95_sup": r[hi_]}
    return CL._it(pd.Series(x), rot, esc, casas)


def gerar_figuras(est: pd.DataFrame, bal: pd.DataFrame, resumo: dict, pm_est: pd.DataFrame,
                  hi: pd.DataFrame) -> list[dict]:
    plt = CL._plt()
    DIR_FIG.mkdir(parents=True, exist_ok=True)
    feitas = []
    # (1) principal.
    nome = "PL_principal.png"
    W, H_ = 17.0, 9.8
    fig = plt.figure(figsize=(W, H_))
    fig.text(0.1 / W, (H_ - 0.12) / H_, "H1 no corte: RDD sem controle, PSM do 48e (macrorregião) e PSM do 48h (mesma UF "
             "+ especialistas a até 100 km)", fontsize=13.5, weight="bold", va="top")
    for j, c in enumerate(CORTES):
        ct = ROT_CORTE[c]
        x0 = 3.3 + j * 8.2
        hi1 = T40._uma(hi, linha="HI-1", outcome="HI-1", variante="principal", corte=ct)
        hi2 = T40._uma(hi, linha="HI-2", outcome="HI-2", variante="principal", corte=ct)
        p4a = CL._uma(est, bloco="PH-4", outcome="HI-1", corte=ct)
        p4b = CL._uma(est, bloco="PH-4", outcome="HI-2", corte=ct)
        paineis = [
            ([_it(hi1, "RDD sem controle (célula)", 100, 1), _it(p4a, "RDD com UF + raio (PH-4)", 100, 1),
              _it(CL._uma(pm_est, bloco="PM-1", outcome="H1M-FRAC", corte=ct), "PSM 48e (macrorregião)", 100, 1),
              _it(CL._uma(est, bloco="PH-1", outcome="H1M-FRAC", corte=ct), "PSM 48h (UF + raio)", 100, 1)],
             f"Corte {TXT_CORTE[c]} ({BOLSA[c]})\nVaga imediata preenchida", "diferença (p.p.)"),
            ([_it(hi2, "RDD sem controle", 1, 2), _it(p4b, "RDD com UF + raio (PH-4)", 1, 2)],
             "Alocados por município (RDD, com controle das vagas)", "médicos por município"),
            ([_it(CL._uma(pm_est, bloco="PM-1", outcome="H1M-ALOC", corte=ct), "PSM 48e (macrorregião)", 1, 2),
              _it(CL._uma(est, bloco="PH-1", outcome="H1M-ALOC", corte=ct), "PSM 48h (UF + raio)", 1, 2)],
             "Alocados por vaga imediata (pareado)", "médicos por vaga imediata"),
        ]
        y = H_ - 0.95
        for its, tit, eixo in paineis:
            h = 0.42 * len(its)
            y0 = y - 0.75 - h
            ax = fig.add_axes([x0 / W, y0 / H_, 3.0 / W, h / H_])
            CL._floresta(ax, its, tit, eixo)
            y = y0 - 0.55
    _rodape(fig, COMO_LER[nome], W, H_, 190)
    fig.savefig(DIR_FIG / nome, dpi=170, facecolor="white", metadata={"Software": None})
    plt.close(fig)
    feitas.append({"arquivo": rotulo(DIR_FIG / nome), "como_ler": COMO_LER[nome],
                   "fonte": "HI_estimativas.csv (HI-1, HI-2), PM_estimativas.csv (PM-1), PL_estimativas.csv (PH-1, PH-4)"})
    # (2) balanço.
    nome = "PL_balanco.png"
    W, H_ = 14.0, 6.6
    fig = plt.figure(figsize=(W, H_))
    fig.text(0.1 / W, (H_ - 0.12) / H_, "Balanço antes e depois do pareamento (PH-1, janela de 0,050)", fontsize=14,
             weight="bold", va="top")
    ordem = ("log_pop", "med", "esp", "raio", "capital", "uf")
    for j, c in enumerate(CORTES):
        rb = {x["variavel"]: x for x in resumo_balanco(bal, "PH-1", ROT_CORTE[c], RAIO, "cd_uf")}
        ax = fig.add_axes([(3.6 + j * 6.9) / W, 1.7 / H_, 3.3 / W, 4.2 / H_])
        for k, v in enumerate(ordem):
            ax.scatter([abs(rb[v]["antes"])], [k], color=CL.CINZA, s=40)
            if np.isfinite(rb[v]["depois"]):
                ax.scatter([abs(rb[v]["depois"])], [k], color=CL.AZUL, s=40)
        ax.set_yticks(range(len(ordem)))
        ax.set_yticklabels([ROT_BAL[v] for v in ordem] if j == 0 else [""] * len(ordem), fontsize=9.5)
        ax.set_ylim(len(ordem) - 0.5, -0.5)
        for lim in (CL.LIMIAR_DP_META, CL.LIMIAR_DP_LIMPA):
            ax.axvline(lim, color=CL.TINTA2, lw=1, ls=(0, (4, 3)))
        ax.set_xlabel("|diferença padronizada|", fontsize=9.5)
        ax.set_title(f"Corte {TXT_CORTE[c]}", fontsize=11, loc="left", weight="bold")
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)
    fig.legend(handles=[plt.Line2D([], [], color=CL.CINZA, marker="o", ls="", label="antes"),
                        plt.Line2D([], [], color=CL.AZUL, marker="o", ls="", label="depois (PH-1)")],
               loc="upper right", fontsize=10, frameon=False)
    _rodape(fig, COMO_LER[nome], W, H_, 160)
    fig.savefig(DIR_FIG / nome, dpi=170, facecolor="white", metadata={"Software": None})
    plt.close(fig)
    feitas.append({"arquivo": rotulo(DIR_FIG / nome), "como_ler": COMO_LER[nome],
                   "fonte": "PL_balanco.csv: PH-1, janela 0,050"})
    # (3) origem dos alocados por lado (PH-5).
    nome = "PL_origem.png"
    W, H_ = 15.0, 6.2
    fig = plt.figure(figsize=(W, H_))
    fig.text(0.1 / W, (H_ - 0.12) / H_, "De onde vêm os médicos, por lado do corte (pares da PH-1, ciclos 1 e 2)",
             fontsize=14, weight="bold", va="top")
    cores = {"mesma_uf": CL.AZUL, "outra_uf": CL.LARANJA, "desconhecida": "#c9c7c1"}
    rotc = {"mesma_uf": "mesma UF", "outra_uf": "outra UF", "desconhecida": "origem desconhecida"}
    for j, x in enumerate(resumo["ph5_medias"]):
        ax = fig.add_axes([(2.3 + j * 7.0) / W, 2.0 / H_, 3.0 / W, 3.3 / H_])
        for i, lado in enumerate(("abaixo", "acima")):
            esq = 0.0
            for k in ("mesma_uf", "outra_uf", "desconhecida"):
                v = x[lado][k]
                if np.isfinite(v) and v > 0:
                    ax.barh(i, v, left=esq, color=cores[k], height=0.55)
                    esq += v
            ax.text(esq + 0.01, i, fn(esq, 2, False), va="center", fontsize=9)
        ax.set_yticks([0, 1])
        ax.set_yticklabels(["bolsa menor\n(abaixo)", "bolsa maior\n(acima)"], fontsize=9.5)
        ax.set_ylim(1.6, -0.6)
        ax.set_xlabel("médicos ativos por vaga imediata", fontsize=9.5)
        ct = x["corte"]
        o = CL._uma(est, bloco="PH-5", outcome="H1M-OUTRA-UF", corte=ct)
        m = CL._uma(est, bloco="PH-5", outcome="H1M-MESMA-UF", corte=ct)
        ax.set_title(f"Corte {_corte_txt(ct)} ({fint(x['pares_ciclos_1_2'])} pares)", fontsize=11, loc="left",
                     weight="bold")
        txt = (f"outra UF: {fv(o)} {fic(o)}\nmesma UF: {fv(m)} {fic(m)}" if o["status"] == "EXECUTADO"
               else "sem estimativa")
        ax.text(1.04, 0.5, "diferença (acima − abaixo):\n" + txt, transform=ax.transAxes, va="center", fontsize=9.5)
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)
    fig.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=cores[k], label=rotc[k]) for k in cores],
               loc="upper right", fontsize=10, frameon=False, ncol=3)
    _rodape(fig, COMO_LER[nome], W, H_, 170)
    fig.savefig(DIR_FIG / nome, dpi=170, facecolor="white", metadata={"Software": None})
    plt.close(fig)
    feitas.append({"arquivo": rotulo(DIR_FIG / nome), "como_ler": COMO_LER[nome],
                   "fonte": "PL_resumo.json (ph5_medias) e PL_estimativas.csv (PH-5)"})
    return feitas


# ---------------------------------------------------------------------------
# 7. Resumo, gravação e execução
# ---------------------------------------------------------------------------

def medias_ph5(par: pd.DataFrame, regs: list[dict]) -> list[dict]:
    """Média, por lado, nos pares da PH-1 dos ciclos 1 e 2 (descritivo da figura)."""
    y = par.set_index("id")
    out = []
    for rg in regs:
        if rg["bloco"] != "PH-1":
            continue
        pares = [p for p in ((rg.get("PSM") or {}).get("pares") or [])
                 if int(y.loc[p["acima"], "ciclo"]) in CICLOS_X1]
        x = {"corte": rg["corte"], "pares_ciclos_1_2": len(pares), "sinais": {}}
        for oid, spec in OUT_PH5.items():
            dif = np.array([y.loc[p["acima"], spec["col"]] - y.loc[p["abaixo"], spec["col"]] for p in pares], float)
            dif = dif[np.isfinite(dif)]
            x["sinais"][oid] = {"pares": int(dif.size), "diferentes_de_zero": int((dif != 0).sum()),
                                "acima_maior": int((dif > 0).sum()), "abaixo_maior": int((dif < 0).sum()),
                                "p_minimo_permutacao": float(2.0 ** (1 - int((dif != 0).sum())))
                                if (dif != 0).any() else 1.0}
        for lado in ("abaixo", "acima"):
            ids = [p[lado] for p in pares]
            x[lado] = {k: float(y.loc[ids, col].mean()) if ids else np.nan
                       for k, col in (("mesma_uf", "orig_mesma_uf_por_vi"), ("outra_uf", "orig_outra_uf_por_vi"),
                                      ("desconhecida", "orig_desconhecida_por_vi"), ("aloc", "aloc_por_vi"))}
        out.append(x)
    return out


def _finalizar(linhas: list[dict], bal_l: list[dict], exc_l: list[dict]):
    est = pd.DataFrame(linhas).reindex(columns=COLUNAS)
    est["id_linha"] = (est["bloco"] + "|" + est["outcome"] + "|" + est["corte"] + "|w=0.050|raio="
                       + est["raio_km"].astype(int).astype(str) + "|exato=" + est["exato"].fillna("").astype(str))
    if est["id_linha"].duplicated().any():
        raise FalhaValidacao(f"id_linha duplicado: {est.loc[est['id_linha'].duplicated(), 'id_linha'].tolist()}")
    for c in ("entra_holm", "entra_bky", "multiplicidade_provisoria", "regra2"):
        est[c] = est[c].fillna(False).astype(bool)
    est = aplicar_multiplicidade(est)
    bal = pd.DataFrame(bal_l).reindex(columns=COLUNAS_BAL)
    exc = pd.DataFrame(exc_l).reindex(columns=COLUNAS_EXC)
    exc["ciclo"] = exc["ciclo"].astype("Int64")
    return est, bal, exc


def entradas() -> list[dict]:
    arqs = [ADENDO, PM.ADENDO, OUT / PM.NOME_EST, OUT / PM.NOME_RESUMO, COORD, COORD_MANIF, X1_MED, X1_RES,
            X1M.ATIVOS_ZIP, X1M.NOMINAL_CSV]
    return [{"arquivo": rotulo(p), "sha256": sha256(p)} for p in arqs] + CL.entradas()


def montar_resumo(est, bal, exc, regs, prt, dados, protegidos) -> dict:
    return {
        "etapa": "Adendo 48h: H1 pareada pela localizacao da unidade (UF) e dos medicos (raio de 100 km)",
        "natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "data_execucao": DATA_EXECUCAO,
        "script": "scripts/rdd_bolsa/49_pareamento_localizacao.py",
        "adendo": {"arquivo": rotulo(ADENDO), "sha256": sha256(ADENDO), "commit_congelamento": COMMIT_CONGELAMENTO,
                   "commit_decisoes_57w": COMMIT_DECISOES},
        "contraste": CONTRASTE,
        "parametros": {"cortes": [0.300, 0.400], "janela": JANELA / 1000, "raio_km": RAIO, "raios_km": list(RAIOS),
                       "escore": list(VARS_ESCORE), "exato": ["UF (PH-1, PH-2) ou regiao de saude (PH-3)", "capital",
                                                              "ciclo"],
                       "caliper_psm": CL.CALIPER_PS, "n_permutacoes": CL.N_PERM, "semente": CL.SEMENTE,
                       "tolerancia_portao": TOL_PORTAO, "limiar_saida_regra2": LIMIAR_SAIDA,
                       "competencias_pre": list(CL.COMP_PRE), "regra_ligacao_x1": REGRA_X1, "lista_x1": LISTA_X1},
        "blocos": DESC_BLOCO,
        "entradas": entradas(),
        "saidas_protegidas_sha256": protegidos,
        "covariaveis": dados["info_cov"],
        "raio": dados["info_raio"],
        "x1": dados["info_x1"],
        "portao": prt,
        "pareamento": regs,
        "ph5_medias": medias_ph5(dados["par"], regs),
        "excluidos_regra2": int(len(exc)),
        "contagens": {"linhas": int(len(est)), "por_bloco": est["bloco"].value_counts().sort_index().to_dict(),
                      "por_status": est["status"].value_counts().sort_index().to_dict(),
                      "holm": {"n_familia": int(est["entra_holm"].sum())},
                      "bky": {"n_familia": int(est["entra_bky"].sum())}},
        "leitura": leituras(est, regs),
        "integridade": {"ivs": "IVS 2010 oficial (a08); o arquivo local de IVS da auditoria 16 nao e lido",
                        "cnes": "competencias 202406-202506 (covariaveis e raio); nenhuma >= 202609",
                        "imputacao": "nada imputado; ausente fica ausente e e contado",
                        "origem_x1": "so outcome (PH-5); nao entra no escore, no exato nem na amostra",
                        "dados_pessoais": "nome, CRM e UF do CRM das listas so em memoria; nenhum id de medico gravado",
                        "saidas_nao_regravadas": ["HI_*", "CL_*", "PM_*", "PO_*", "X1_*"]},
        "saidas": {"estimativas": rotulo(OUT / NOME_EST), "balanco": rotulo(OUT / NOME_BAL),
                   "excluidos": rotulo(OUT / NOME_EXC), "resumo": rotulo(OUT / NOME_RESUMO),
                   "figuras": rotulo(DIR_FIG), "doc": rotulo(DOC)},
        "linguagem": "pacote do corte; 'nao se detecta' nao e 'zero'; nunca 'causa'",
    }


def gravar(est, bal, exc, resumo) -> None:
    est.to_csv(OUT / NOME_EST, index=False)
    bal.to_csv(OUT / NOME_BAL, index=False)
    exc.to_csv(OUT / NOME_EXC, index=False)
    (OUT / NOME_RESUMO).write_text(json.dumps(CL._nan_none(resumo), ensure_ascii=False, indent=1) + "\n",
                                   encoding="utf-8")


def ler_saidas():
    est = pd.read_csv(OUT / NOME_EST, dtype={"corte": str, "comparacao_limpa": str})
    for c in ("entra_holm", "entra_bky", "multiplicidade_provisoria", "regra2"):
        est[c] = est[c].astype(str).str.lower().isin(["true", "1"])
    for c in ("nota", "covariaveis_descartadas", "comparacao_limpa", "variaveis", "regra_pareamento",
              "lado_que_procura", "exato"):
        est[c] = est[c].fillna("")
    bal = pd.read_csv(OUT / NOME_BAL, dtype={"corte": str})
    bal["nota"] = bal["nota"].fillna("")
    exc = pd.read_csv(OUT / NOME_EXC, dtype={"corte": str, "co_ibge": str, "uf": str})
    return est, bal, exc, json.loads((OUT / NOME_RESUMO).read_text(encoding="utf-8"))


def referencias() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    pm_est = PM.ler_saidas()[0]
    cl_est = CL.ler_saidas()[0]
    hi = pd.read_csv(CL.HI_EST, dtype={"corte": str, "ciclo": str}, low_memory=False)
    return pm_est, cl_est, hi


def _carregar_siglas() -> None:
    nm = PM.nomes_municipios()
    UF_SIGLA.update({cod[:2]: uf for cod, uf in nm["uf"].items()})


def executar(atualizar: bool) -> int:
    if sha256(ADENDO) != SHA_ADENDO:
        raise FalhaValidacao("o adendo 48h mudou depois do congelamento")
    if sha256(PM.ADENDO) != PM.SHA_ADENDO or sha256(CL.ADENDO) != CL.SHA_ADENDO:
        raise FalhaValidacao("o adendo 48e ou o 48d mudou depois do congelamento")
    protegidos = hashes_protegidos()
    print("Bases da H1 (funções do 44), raio e origem (X1)...", flush=True)
    dados = carregar()
    nomes = PM.nomes_municipios()
    _carregar_siglas()
    print("Portão: PM-1 do 48e em 0,300; centroides e X1...", flush=True)
    prt = portao(dados, nomes)
    print(f"  reproduz (máx |dif| = {prt['max_abs_dif']:.1e}); centroides conferem", flush=True)
    print("PH-1, PH-2, PH-3, PH-5 e PH-4...", flush=True)
    linhas, bal_l, regs, exc_l = todas_as_linhas(dados, nomes)
    linhas += linhas_ph4(dados)
    est, bal, exc = _finalizar(linhas, bal_l, exc_l)
    resumo = montar_resumo(est, bal, exc, regs, prt, dados, protegidos)
    pm_est, cl_est, hi = referencias()
    resumo["figuras"] = gerar_figuras(est, bal, resumo, pm_est, hi)
    if hashes_protegidos() != protegidos:
        raise FalhaValidacao("saídas HI_, CL_, PM_, PO_ ou X1_ mudaram durante a execução")
    gravar(est, bal, exc, resumo)
    if atualizar:
        e2, b2, x2, r2 = ler_saidas()
        atualizar_doc(e2, b2, x2, r2, pm_est, cl_est, hi)
        print(f"Doc regravado: {rotulo(DOC)}")
    for _, r in est[est["bloco"].isin(["PH-1", "PH-5"])].iterrows():
        print(f"  {r['bloco']} {r['outcome']} {r['corte']}: {r['status']} tau={_f(r['tau']):.4f} "
              f"[{_f(r['ic95_inf']):.4f}; {_f(r['ic95_sup']):.4f}] p={_f(r['p_valor']):.4f} "
              f"p_holm={_f(r['p_holm']):.4f} q={_f(r['q_bky']):.4f} pares={_f(r['n_pares']):.0f}")
    print(f"Gravado: {rotulo(OUT / NOME_EST)} ({len(est)} linhas), {NOME_BAL}, {NOME_EXC} ({len(exc)}), "
          f"{NOME_RESUMO}, {rotulo(DIR_FIG)}/")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--atualizar-doc", action="store_true", help="regrava os blocos do doc 57w")
    ap.add_argument("--so-doc", action="store_true", help="só regrava os blocos do doc 57w das saídas")
    args = ap.parse_args(argv)
    try:
        if args.so_doc:
            _carregar_siglas()
            atualizar_doc(*ler_saidas(), *referencias())
            return 0
        return executar(args.atualizar_doc)
    except (FalhaValidacao, PM.FalhaValidacao, CL.FalhaValidacao, CL.T40.FalhaValidacao, CL.T41.FalhaValidacao,
            CL.T37.FalhaValidacao, CL.T43.FalhaValidacao, CL.K1M.FalhaValidacao, CL.D2M.FalhaValidacao) as erro:
        print(f"FALHA (nada gravado): {erro}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
