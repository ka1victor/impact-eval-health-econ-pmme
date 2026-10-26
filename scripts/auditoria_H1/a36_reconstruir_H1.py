"""Auditoria 36: reconstrução independente, a partir dos arquivos brutos, das bases da H1 (A3, N1, taxa).

Pergunta do autor: "A gente não entendeu errado ou fez alguma besteira com os dados?"

O script não importa nenhum script de `scripts/rdd_bolsa/` nem de `scripts/aquisicao/`. Ele lê:
- os quadros e resultados públicos em `data/raw/` (somente leitura), listados em
  `docs/auditorias/aquisicao/A01_vagas_e_versionamento.md` e no manifesto a11;
- o IVS 2010 oficial em `output/aquisicao/a08_ivs_2010_oficial_municipio.csv`;
- para comparar, as bases do pipeline em `output/rdd_bolsa/outcomes/` e as estimativas gravadas
  (`N_estimativas.csv`, `NA_estimativas.csv`, `ND_estimativas.csv`), sem alterá-las.

Saídas em `output/auditoria_H1/` (rótulo AUDITORIA_36_RECONSTRUCAO, natureza EMPIRICO). Nenhuma
saída tem nome, CPF ou CRM: só contagens por célula e por município.

Uso: python scripts/auditoria_H1/a36_reconstruir_H1.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from a36_estimador import dif_medias, rd  # noqa: E402
from a36_leitura import (ARQ, IVS_OFICIAL, RAIZ, faixa_regra, ler_ivs, ler_quadro,  # noqa: E402
                         ler_resultado, opcao, sha256)

OUT = RAIZ / "output" / "auditoria_H1"
ROTULO = "AUDITORIA_36_RECONSTRUCAO"
NAT = "EMPIRICO"
PIPE_CEL = RAIZ / "output" / "rdd_bolsa" / "outcomes" / "outcomes_V_celula.parquet"
PIPE_MUN = RAIZ / "output" / "rdd_bolsa" / "outcomes" / "outcomes_V_municipio.parquet"
PIPE_EST = {k: RAIZ / "output" / "rdd_bolsa" / f"{k}_estimativas.csv" for k in ("N", "NA", "ND")}
CORTES = (300, 400)
# Capitais das 27 UFs (IBGE, 6 dígitos). O quadro do ciclo 3 marca 'CAPITAL' e é conferido contra esta lista.
CAPITAIS = set("110020 120040 130260 140010 150140 160030 172100 211130 221100 230440 240810 250750 261160 "
               "270430 280030 292740 310620 320530 330455 355030 410690 420540 431490 500270 510340 520870 "
               "530010".split())
H = 50.0


def alocado(sit) -> bool:
    return str(sit).upper().startswith("ALOCADO")


# ---------------------------------------------------------------------------
# 1. Quadros e resultados, por ciclo
# ---------------------------------------------------------------------------
def montar_ciclo1(reg: dict) -> pd.DataFrame:
    q = ler_quadro(ARQ["c1_quadro"])
    a = ler_resultado(ARQ["c1_aloc_sj"])
    a_ret = ler_resultado(ARQ["c1_aloc"])
    a["op"] = a["ORDEM DE PRIORIDADE ESCOLHIDA"].map(opcao)
    a["conf"] = a["ALOCACAO"].astype(str).str.startswith("LOCAL DE ATUACAO CONFIRMADO")
    a["desc"] = a["ALOCACAO"].astype(str).str.contains("DESCONSIDERADO")
    a["classif"] = a["RESULTADO"].astype(str).str.startswith("CLASSIFICACAO")
    r = ler_resultado(ARQ["c1_realoc"])
    h = ler_resultado(ARQ["c1_homol"])
    a["k"] = a["id_nome"] + "_" + a["chave"]
    h["k"] = h["id_nome"] + "_" + h["chave"]
    r["k"] = r["id_nome"] + "_" + r["chave"]
    reg["ciclo1"] = {
        "linhas_alocacao": int(len(a)), "pessoas": int(a["id_cand"].nunique()),
        "classificados": int(a["classif"].sum()), "confirmados": int(a["conf"].sum()),
        "desconsiderados_quadro2": int(a["desc"].sum()),
        "classificado_igual_confirmado_ou_desconsiderado": bool((a["classif"] == (a["conf"] | a["desc"])).all()),
        "pessoas_com_mais_de_uma_confirmacao": int((a[a["conf"]].groupby("id_cand").size() > 1).sum()),
        "confirmados_por_opcao": {str(k): int(v) for k, v in a[a["conf"]]["op"].value_counts().sort_index().items()},
        "versao_sub_judice_igual_retificada_exceto_marca": bool(
            (a[["chave", "RESULTADO", "ALOCACAO"]].values == a_ret[["chave", "RESULTADO", "ALOCACAO"]].values).all()),
        "linhas_marcadas_sub_judice": int(a.filter(like="_col").notna().any(axis=1).sum()),
        "realocados_quadro2": int(len(r)),
        "realocados_em_celula_fora_do_quadro": int((~r["chave"].isin(q["chave"])).sum()),
        "realocados_em_celula_so_cr": int(r["chave"].map(q.set_index("chave")["vagas_imediatas"]).eq(0).sum()),
        "realocados_sao_os_desconsiderados": int(r["id_nome"].isin(a.loc[a["desc"], "id_nome"]).sum()),
        "homologados": int(len(h)),
        "homologados_mesma_pessoa_e_celula_confirmada": int(h["k"].isin(a.loc[a["conf"], "k"]).sum()),
        "homologados_mesma_pessoa_e_celula_realocada": int(h["k"].isin(r["k"]).sum()),
        "homologados_outros": int((~h["k"].isin(a.loc[a["conf"], "k"]) & ~h["k"].isin(r["k"])).sum()),
        "homologados_em_celula_fora_do_quadro": int((~h["chave"].isin(q["chave"])).sum()),
        "confirmados_nao_homologados": int((~a.loc[a["conf"], "k"].isin(h["k"])).sum()),
    }
    cel = q.copy()
    cel["ciclo"] = 1
    g = lambda m: a[m].groupby("chave").size()  # noqa: E731
    cel["n_cand_1a"] = cel["chave"].map(g(a["op"] == 1)).fillna(0).astype(int)
    cel["n_alocados"] = cel["chave"].map(g(a["conf"])).fillna(0).astype(int)
    cel["n_desconsiderados"] = cel["chave"].map(g(a["desc"])).fillna(0).astype(int)
    cel["n_realocados_q2"] = cel["chave"].map(r.groupby("chave").size()).fillna(0).astype(int)
    cel["n_homologados"] = cel["chave"].map(h.groupby("chave").size()).fillna(0).astype(int)
    cel["n_alocados_sj"] = cel["n_alocados"]
    cel["vagas_imediatas_pre"] = cel["vagas_imediatas"]
    cel["vagas_imediatas_pipe_versao"] = cel["vagas_imediatas"]
    cel["versao_quadro"] = "original 24/07/2025 (único quadro da 1a chamada)"
    return cel, a, r, h, q


def montar_ciclo2(reg: dict):
    q0 = ler_quadro(ARQ["c2_quadro_orig"]).set_index("chave")
    q1 = ler_quadro(ARQ["c2_quadro_ret1"]).set_index("chave")
    q2 = ler_quadro(ARQ["c2_quadro_ret2"]).set_index("chave")
    f = ler_resultado(ARQ["c2_final"])
    p = ler_resultado(ARQ["c2_prelim"])
    f["aloc"] = f["SITUACAO"].map(alocado)
    p["aloc"] = p["SITUACAO"].map(alocado)
    f["op"] = f["ORDEM DE PRIORIDADE ESCOLHIDA"].map(opcao)
    rem9 = ler_resultado(ARQ["c2_reman9"])
    rem81 = ler_resultado(ARQ["c2_reman81"])
    cel = q2.reset_index().copy()
    cel["ciclo"] = 2
    cel["vagas_imediatas_pipe_versao"] = cel["vagas_imediatas"]
    cel["vagas_imediatas_19mar"] = cel["vagas_imediatas"]
    cel["vagas_cr_19mar"] = cel["vagas_cr"]
    cel["vagas_imediatas_13fev"] = cel["chave"].map(q1["vagas_imediatas"])
    cel["vagas_cr_13fev"] = cel["chave"].map(q1["vagas_cr"])
    cel["vagas_imediatas_03fev"] = cel["chave"].map(q0["vagas_imediatas"])
    cel["vagas_cr_03fev"] = cel["chave"].map(q0["vagas_cr"])
    cel["vagas_imediatas_pre"] = cel["vagas_imediatas_13fev"]
    cel["versao_quadro"] = "retificado 19/03/2026 (células e total); tipo pré-alocação: retificado 13/02/2026"
    g = lambda d, m: d[m].groupby("chave").size()  # noqa: E731
    cel["n_cand_1a"] = cel["chave"].map(g(f, f["op"] == 1)).fillna(0).astype(int)
    cel["n_alocados"] = cel["chave"].map(g(f, f["aloc"])).fillna(0).astype(int)
    cel["n_alocados_prelim"] = cel["chave"].map(g(p, p["aloc"])).fillna(0).astype(int)
    cel["n_remanescentes_9"] = cel["chave"].map(rem9.groupby("chave").size()).fillna(0).astype(int)
    cel["n_remanescentes_81"] = cel["chave"].map(rem81.groupby("chave").size()).fillna(0).astype(int)
    cel["n_alocados_sj"] = cel["n_alocados"]
    alo = f[f["aloc"]].groupby("chave").size()
    alp = p[p["aloc"]].groupby("chave").size()

    def em_cr(al, q):
        im = q.reindex(al.index)["vagas_imediatas"]
        return {"alocados": int(al.sum()), "fora_do_quadro": int(im.isna().sum()),
                "alocados_em_celula_so_cr": int(al[im == 0].sum()), "celulas_so_cr_com_alocado": int((im == 0).sum()),
                "alocados_acima_das_imediatas": int((al - im).clip(lower=0).sum())}
    conv = cel["vagas_imediatas_19mar"] - cel["vagas_imediatas_13fev"]
    so_cr_13 = cel["vagas_imediatas_13fev"] == 0
    reg["ciclo2_versoes"] = {
        "datas": {"original": "03/02/2026", "retificado_servicos": "13/02/2026",
                  "resultado_preliminar": "planilha criada 10/03/2026; recurso 12-13/03/2026 (manifesto a11)",
                  "retificado_final": "19/03/2026", "resultado_final": "24/03/2026 (comunicado oficial)"},
        "vagas": {"03fev": [int(q0.vagas_imediatas.sum()), int(q0.vagas_cr.sum())],
                  "13fev": [int(q1.vagas_imediatas.sum()), int(q1.vagas_cr.sum())],
                  "19mar": [int(q2.vagas_imediatas.sum()), int(q2.vagas_cr.sum())]},
        "celulas": {"03fev": int(len(q0)), "13fev": int(len(q1)), "19mar": int(len(q2))},
        "celulas_19mar_fora_de_13fev": int((~q2.index.isin(q1.index)).sum()),
        "celulas_com_total_diferente_13fev_19mar": int(((q1.vagas_imediatas + q1.vagas_cr).reindex(q2.index)
                                                        != (q2.vagas_imediatas + q2.vagas_cr)).sum()),
        "final_contra_03fev": em_cr(alo, q0), "final_contra_13fev": em_cr(alo, q1), "final_contra_19mar": em_cr(alo, q2),
        "preliminar_contra_13fev": em_cr(alp, q1), "preliminar_contra_19mar": em_cr(alp, q2),
        "celulas_so_cr_em_13fev": int(so_cr_13.sum()),
        "dessas_convertidas_em_imediatas_19mar": int((so_cr_13 & (cel["vagas_imediatas_19mar"] > 0)).sum()),
        "convertidas_com_alocado_final": int((so_cr_13 & (cel["vagas_imediatas_19mar"] > 0) & (cel["n_alocados"] > 0)).sum()),
        "nao_convertidas_com_alocado_final": int((so_cr_13 & (cel["vagas_imediatas_19mar"] == 0) & (cel["n_alocados"] > 0)).sum()),
        "celulas_com_conversao": int((conv > 0).sum()), "vagas_convertidas": int(conv.clip(lower=0).sum()),
        "celulas_com_conversao_e_alocado": int(((conv > 0) & (cel["n_alocados"] > 0)).sum()),
        "imediatas_19mar_maior_ou_igual_alocados_em_todas": bool((cel["vagas_imediatas_19mar"] >= cel["n_alocados"]).all()),
    }
    return cel, f, p, q0, q1, q2


def montar_ciclo3(reg: dict):
    qo = ler_quadro(ARQ["c3_quadro_orig"]).set_index("chave")
    q = ler_quadro(ARQ["c3_quadro_ret"])
    r = ler_resultado(ARQ["c3_result_sj"])
    r["op"] = r["ORDEM DE PRIORIDADE ESCOLHIDA"].map(opcao)
    r["aloc"] = r["SITUACAO"].map(alocado)
    r["sj"] = r["SITUACAO"].astype(str).str.upper().str.startswith("SUB JUDICE")
    cel = q.copy()
    cel["ciclo"] = 3
    g = lambda m: r[m].groupby("chave").size()  # noqa: E731
    cel["n_cand_1a"] = cel["chave"].map(g(r["op"] == 1)).fillna(0).astype(int)
    cel["n_alocados"] = cel["chave"].map(g(r["aloc"])).fillna(0).astype(int)
    cel["n_sub_judice"] = cel["chave"].map(g(r["sj"])).fillna(0).astype(int)
    cel["n_alocados_sj"] = cel["n_alocados"] + cel["n_sub_judice"]
    cel["vagas_imediatas_pre"] = cel["vagas_imediatas"]
    cel["vagas_imediatas_pipe_versao"] = cel["vagas_imediatas"]
    cel["vagas_imediatas_16jul"] = cel["chave"].map(qo["vagas_imediatas"])
    cel["versao_quadro"] = "retificado 24/07/2026 (antes do resultado de 25/08/2026)"
    ufs_q = set(q["uf"])
    ufs_r = set(r["uf"])
    aloc_c = r[r["aloc"]].groupby("chave").size()
    im = q.set_index("chave").reindex(aloc_c.index)["vagas_imediatas"]
    reg["ciclo3"] = {
        "linhas_resultado": int(len(r)), "alocados": int(r["aloc"].sum()), "sub_judice": int(r["sj"].sum()),
        "situacoes": {k: int(v) for k, v in r["SITUACAO"].value_counts().items()},
        "ufs_no_quadro": sorted(ufs_q), "ufs_no_resultado": sorted(ufs_r),
        "ufs_do_quadro_sem_nenhuma_linha_no_resultado": sorted(ufs_q - ufs_r),
        "celulas_de_uf_sem_resultado": int(q["uf"].isin(ufs_q - ufs_r).sum()),
        "cursos_no_quadro": sorted(int(c) for c in q["cod_curso"].unique()),
        "cursos_sem_linha_no_resultado": sorted(int(c) for c in set(q["cod_curso"]) - set(r["cod_curso"])),
        "alocados_em_celula_so_cr": int(aloc_c[im == 0].sum()),
        "celulas_vagas_imediatas_mudaram_16jul_24jul": int((cel["vagas_imediatas"] != cel["vagas_imediatas_16jul"]).sum()),
        "pessoas_com_mais_de_um_alocado": int((r[r["aloc"]].groupby("id_cand").size() > 1).sum()),
        "alocados_por_opcao": {str(k): int(v) for k, v in r[r["aloc"]]["op"].value_counts().sort_index().items()},
    }
    return cel, r, q


# ---------------------------------------------------------------------------
# 2. Chaves
# ---------------------------------------------------------------------------
def auditar_chaves(quadros: dict, resultados: dict) -> dict:
    out = {}
    for nome, q in quadros.items():
        q = q.reset_index() if "chave" not in q.columns else q
        out[nome] = {
            "linhas": int(len(q)), "chaves_unicas": int(q["chave"].nunique()),
            "ibge_digitos": {str(k): int(v) for k, v in q["ibge_ndig"].value_counts().items()},
            "cnes_em_mais_de_um_municipio": int((q.groupby("cnes")["ibge_impresso"].nunique() > 1).sum()),
            "municipio_com_mais_de_uma_faixa": int((q.groupby("ibge_impresso")["faixa_impressa"].nunique() > 1).sum()),
            "codigo_de_curso_com_mais_de_um_nome": int((q.groupby("cod_curso")["nome_curso"].nunique() > 1).sum()),
        }
    for nome, (r, q) in resultados.items():
        qq = q.reset_index() if "chave" not in q.columns else q
        qi = qq.set_index("chave")
        dentro = r["chave"].isin(qi.index)
        nomes_q = qq.groupby("cod_curso")["nome_curso"].first()
        bloco = {
            "linhas": int(len(r)), "linhas_fora_do_quadro": int((~dentro).sum()),
            "celulas_do_resultado_fora_do_quadro": int(r.loc[~dentro, "chave"].nunique()),
            "celulas_do_quadro_sem_linha_no_resultado": int((~qi.index.isin(r["chave"])).sum()),
            "codigo_de_curso_com_nome_diferente_do_quadro": int(
                (r.drop_duplicates("cod_curso").set_index("cod_curso")["nome_curso"]
                 != nomes_q.reindex(r.drop_duplicates("cod_curso")["cod_curso"]).values).sum()),
        }
        if "aloc" in r.columns:
            bloco["alocados_fora_do_quadro"] = int((r["aloc"] & ~dentro).sum())
        if "conf" in r.columns:
            bloco["confirmados_fora_do_quadro"] = int((r["conf"] & ~dentro).sum())
        if r["ibge_impresso"].notna().any():
            ib_q = r.loc[dentro, "chave"].map(qi["ibge_impresso"])
            bloco["ibge_impresso_digitos"] = {str(k): int(v) for k, v in r["ibge_ndig"].value_counts().items()}
            bloco["linhas_com_ibge_impresso_diferente_do_quadro"] = int((r.loc[dentro, "ibge_impresso"] != ib_q).sum())
        bloco["cnes_do_resultado_em_mais_de_um_municipio_no_quadro"] = int(
            (qq[qq["cnes"].isin(r["cnes"])].groupby("cnes")["ibge_impresso"].nunique() > 1).sum())
        out[nome] = bloco
    # mesmo CNES em municípios diferentes entre ciclos
    tudo = pd.concat([q.reset_index()[["cnes", "ibge_impresso"]] if "chave" not in q.columns
                      else q[["cnes", "ibge_impresso"]] for q in quadros.values()])
    out["cnes_em_mais_de_um_municipio_entre_todos_os_quadros"] = int(
        (tudo.drop_duplicates().groupby("cnes")["ibge_impresso"].nunique() > 1).sum())
    return out


# ---------------------------------------------------------------------------
# 3. Comparação com o pipeline
# ---------------------------------------------------------------------------
def comparar(cel: pd.DataFrame, mun: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    pc = pd.read_parquet(PIPE_CEL)
    pm = pd.read_parquet(PIPE_MUN)
    pc["chave"] = pc["co_cnes_7d"].astype(str).str.zfill(7) + "_" + pc["cod_curso"].astype(int).astype(str).str.zfill(2)
    meus = ["co_ibge", "faixa_impressa", "ivs", "vagas_imediatas_pipe_versao", "vagas_cr_pipe", "n_cand_1a",
            "n_alocados", "preenchida_pipe_def", "preenchida", "com_imediata_versao_pipe"]
    cel = cel[["ciclo", "chave"] + meus].rename(columns={c: f"a_{c}" for c in meus})
    pc = pc.rename(columns={c: f"p_{c}" for c in pc.columns if c not in ("ciclo", "chave")})
    a = cel.merge(pc, on=["ciclo", "chave"], how="outer", indicator=True)
    div = []
    for _, l in a[a["_merge"] != "both"].iterrows():
        div.append({"nivel": "celula", "ciclo": l["ciclo"], "chave": l["chave"], "campo": "presenca",
                    "auditoria": l["_merge"] != "right_only", "pipeline": l["_merge"] != "left_only"})
    b = a[a["_merge"] == "both"].copy()
    b["p_faixa_anunciada"] = b["p_faixa_anunciada"].astype(str).str.extract(r"(\d)")[0].astype(float)
    pares = [("co_ibge", "co_ibge"), ("faixa_impressa", "faixa_anunciada"), ("ivs", "ivs_2010_oficial"),
             ("vagas_imediatas_pipe_versao", "vagas_imediatas"), ("vagas_cr_pipe", "vagas_cr"),
             ("n_cand_1a", "n_cand_1a_opcao"), ("n_alocados", "n_alocados_ch1"),
             ("preenchida_pipe_def", "f1_3_preenchida_ch1"), ("preenchida", "f1_3_preenchida_ch1_A3"),
             ("com_imediata_versao_pipe", "com_vagas_imediatas")]
    b = b.copy()
    b["p_f1_3_preenchida_ch1_A3"] = (b["p_n_alocados_ch1"] >= 1).astype(int)
    for meu, dele in pares:
        x, y = b["a_" + meu], b["p_" + dele]
        if meu == "ivs":
            dif = ~np.isclose(x.astype(float), y.astype(float), equal_nan=True)
        elif meu == "co_ibge":
            dif = x.astype(str) != y.astype(str).str[:6]
        else:
            dif = ~np.isclose(pd.to_numeric(x, errors="coerce").astype(float),
                              pd.to_numeric(y, errors="coerce").astype(float), equal_nan=True)
        for _, l in b[dif].iterrows():
            div.append({"nivel": "celula", "ciclo": l["ciclo"], "chave": l["chave"], "campo": f"{meu} x {dele}",
                        "auditoria": l["a_" + meu], "pipeline": l["p_" + dele]})
    # municípios
    pm = pm.copy()
    pm["co_ibge"] = pm["co_ibge"].astype(str).str[:6]
    pm["faixa_anunciada"] = pm["faixa_anunciada"].astype(str).str.extract(r"(\d)")[0].astype(float)
    pm = pm.rename(columns={c: f"p_{c}" for c in pm.columns if c not in ("ciclo", "co_ibge")})
    mun = mun.rename(columns={c: f"a_{c}" for c in mun.columns if c not in ("ciclo", "co_ibge")})
    m = mun.merge(pm, on=["ciclo", "co_ibge"], how="outer", indicator=True)
    for _, l in m[m["_merge"] != "both"].iterrows():
        div.append({"nivel": "municipio", "ciclo": l["ciclo"], "chave": l["co_ibge"], "campo": "presenca",
                    "auditoria": l["_merge"] != "right_only", "pipeline": l["_merge"] != "left_only"})
    mb = m[m["_merge"] == "both"]
    for meu, dele in [("n_celulas", "n_celulas"), ("vagas_imediatas_pipe_versao", "vagas_imediatas"),
                      ("vagas_cr_pipe", "vagas_cr"), ("n_alocados", "n_alocados_ch1"),
                      ("n_celulas_preenchidas", "n_celulas_preenchidas_ch1"),
                      ("n_cand_1a", "n_cand_1a_opcao"), ("faixa_impressa", "faixa_anunciada"),
                      ("ivs", "ivs_2010_oficial")]:
        dif = ~np.isclose(mb["a_" + meu].astype(float), mb["p_" + dele].astype(float), equal_nan=True)
        for _, l in mb[dif].iterrows():
            div.append({"nivel": "municipio", "ciclo": l["ciclo"], "chave": l["co_ibge"], "campo": f"{meu} x {dele}",
                        "auditoria": l["a_" + meu], "pipeline": l["p_" + dele]})
    dv = pd.DataFrame(div, columns=["nivel", "ciclo", "chave", "campo", "auditoria", "pipeline"])
    resumo = {
        "celulas_auditoria": int(len(cel)), "celulas_pipeline": int(len(pc)),
        "celulas_em_ambos": int((a["_merge"] == "both").sum()),
        "municipios_auditoria": int(len(mun)), "municipios_pipeline": int(len(pm)),
        "municipios_em_ambos": int((m["_merge"] == "both").sum()),
        "divergencias_por_campo": {f"{n}|{c}|ciclo{k}": int(v) for (n, c, k), v in
                                   dv.groupby(["nivel", "campo", "ciclo"]).size().items()},
    }
    return dv, resumo


# ---------------------------------------------------------------------------
# 4. Estimativas
# ---------------------------------------------------------------------------
def estimativas(cel: pd.DataFrame, mun: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    c = cel[cel["ivs"].notna()].copy()
    m = mun[mun["ivs"].notna()].copy()
    c["s"] = np.round(c["ivs"] * 1000)
    m["s"] = np.round(m["ivs"] * 1000)
    c["fe_cc"] = c["ciclo"].astype(str) + "_" + c["cod_curso"].astype(str)

    def add(**kw):
        linhas.append(kw)

    defs_cel = {
        # outcome, rótulo
        "A3_pipeline (>=1 alocado; c1 = confirmado)": "preenchida",
        "A3_definicao_ciclo1_pipeline_F1.3 (c1 = confirmado ou homologado)": "preenchida_pipe_def",
        "A3_c1_com_realocados_quadro2 (c1 = confirmado ou realocado)": "preenchida_c1_realoc",
        "A3_c1_classificado (c1 = confirmado ou desconsiderado na celula original)": "preenchida_c1_classif",
        "A3_c3_com_sub_judice": "preenchida_sj",
    }
    ciclos_sets = {"1+2+3": (1, 2, 3), "1": (1,), "2": (2,), "3": (3,)}
    for corte in CORTES:
        for rot_c, ks in ciclos_sets.items():
            cc = c[c["ciclo"].isin(ks)]
            mm = m[m["ciclo"].isin(ks)]
            # --- célula ---
            for nome_out, col in defs_cel.items():
                for var, fe, filtro in [
                    ("FE curso x ciclo + tipo de vaga (versão do pipeline: c2 = 19/03)", ["fe_cc", "com_imediata_versao_pipe"], None),
                    ("FE curso x ciclo + tipo de vaga pré-alocação (c2 = 13/02)", ["fe_cc", "com_imediata_pre"], None),
                    ("FE curso x ciclo", ["fe_cc"], None),
                    ("sem FE", [], None),
                    ("só células com vaga imediata pré-alocação (c2 = 13/02); FE curso x ciclo", ["fe_cc"], "com_imediata_pre"),
                    ("só células com vaga imediata na versão do pipeline (c2 = 19/03); FE curso x ciclo", ["fe_cc"], "com_imediata_versao_pipe"),
                ]:
                    if col != "preenchida" and not var.startswith("FE curso x ciclo + tipo de vaga (versão"):
                        continue
                    d = cc if filtro is None else cc[cc[filtro] == 1]
                    try:
                        r = rd(d["s"], d[col], corte, grupo=d["ciclo"], cluster=d["co_ibge"], h_mil=H,
                               fe=[d[f] for f in fe])
                    except Exception as e:  # noqa: BLE001
                        add(unidade="celula", outcome=nome_out, variante=var, ciclo=rot_c, corte=corte, nota=str(e))
                        continue
                    add(unidade="celula", outcome=nome_out, variante=var, ciclo=rot_c, corte=corte,
                        metodo="local linear h=0,050, reta por ciclo, CR1 municipio", **r)
            # alocados por vaga (célula)
            for var, filtro in [("todas as células", None), ("só células com vaga imediata pré-alocação", "com_imediata_pre")]:
                d = cc if filtro is None else cc[cc[filtro] == 1]
                r = rd(d["s"], d["n_alocados"] / d["vic"], corte, grupo=d["ciclo"], cluster=d["co_ibge"],
                       fe=[d["fe_cc"], d["com_imediata_versao_pipe"]] if filtro is None else [d["fe_cc"]])
                add(unidade="celula", outcome="A3_ALOC_POR_VAGA", variante=var, ciclo=rot_c, corte=corte,
                    metodo="local linear h=0,050", **r)
            # --- município ---
            Z = np.column_stack([(mm["ciclo"] == k).astype(float) * mm["vic"] for k in ks])
            r = rd(mm["s"], mm["n_alocados"], corte, grupo=mm["ciclo"], cluster=mm["co_ibge"], Z=Z)
            add(unidade="municipio", outcome="N1 com controle VIC (S-a/Q1)", variante="pipeline", ciclo=rot_c,
                corte=corte, metodo="local linear h=0,050", **r)
            r = rd(mm["s"], mm["n_alocados"], corte, grupo=mm["ciclo"], cluster=mm["co_ibge"])
            add(unidade="municipio", outcome="N1 sem controle (S-b)", variante="pipeline", ciclo=rot_c,
                corte=corte, metodo="local linear h=0,050", **r)
            r = rd(mm["s"], mm["n_alocados"] / mm["vic"], corte, grupo=mm["ciclo"], cluster=mm["co_ibge"], peso=mm["vic"])
            add(unidade="municipio", outcome="taxa N1/VIC ponderada (Q2)", variante="pipeline", ciclo=rot_c,
                corte=corte, metodo="local linear h=0,050", **r)
            Zi = np.column_stack([(mm["ciclo"] == k).astype(float) * mm["vi_pre"] for k in ks])
            r = rd(mm["s"], mm["n_alocados"], corte, grupo=mm["ciclo"], cluster=mm["co_ibge"], Z=Zi)
            add(unidade="municipio", outcome="N1 com controle VIC (S-a/Q1)",
                variante="controle = só vagas imediatas pré-alocação", ciclo=rot_c, corte=corte,
                metodo="local linear h=0,050", **r)
            mi = mm[mm["vic_em_imediata_pre"] > 0]
            r = rd(mi["s"], mi["n_alocados_em_imediata_pre"] / mi["vic_em_imediata_pre"], corte, grupo=mi["ciclo"],
                   cluster=mi["co_ibge"], peso=mi["vic_em_imediata_pre"])
            add(unidade="municipio", outcome="taxa N1/VIC ponderada (Q2)",
                variante="só células com vaga imediata pré-alocação (alocados nelas / vagas delas)", ciclo=rot_c,
                corte=corte, metodo="local linear h=0,050", **r)
            Zc = np.column_stack([(mm["ciclo"] == k).astype(float) * mm["vic"] for k in ks])
            r = rd(mm["s"], mm["n_classif"], corte, grupo=mm["ciclo"], cluster=mm["co_ibge"], Z=Zc)
            add(unidade="municipio", outcome="N1 com controle VIC (S-a/Q1)",
                variante="c1 = classificado (confirmado + desconsiderado)", ciclo=rot_c, corte=corte,
                metodo="local linear h=0,050", **r)
            r = rd(mm["s"], mm["n_classif"] / mm["vic"], corte, grupo=mm["ciclo"], cluster=mm["co_ibge"], peso=mm["vic"])
            add(unidade="municipio", outcome="taxa N1/VIC ponderada (Q2)",
                variante="c1 = classificado (confirmado + desconsiderado)", ciclo=rot_c, corte=corte,
                metodo="local linear h=0,050", **r)
            r = rd(mm["s"], mm["capital"], corte, grupo=mm["ciclo"], cluster=mm["co_ibge"])
            add(unidade="municipio", outcome="composicao", variante="município é capital", ciclo=rot_c, corte=corte,
                metodo="local linear h=0,050, sem FE", **r)
            # --- sem capitais (lista das 27 capitais) ---
            cs_ = cc[cc["capital"] == 0]
            ms_ = mm[mm["capital"] == 0]
            r = rd(cs_["s"], cs_["preenchida"], corte, grupo=cs_["ciclo"], cluster=cs_["co_ibge"],
                   fe=[cs_["fe_cc"], cs_["com_imediata_versao_pipe"]])
            add(unidade="celula", outcome="A3_pipeline (>=1 alocado; c1 = confirmado)",
                variante="sem capitais; FE do pipeline", ciclo=rot_c, corte=corte, metodo="local linear h=0,050", **r)
            r = rd(ms_["s"], ms_["n_alocados"] / ms_["vic"], corte, grupo=ms_["ciclo"], cluster=ms_["co_ibge"],
                   peso=ms_["vic"])
            add(unidade="municipio", outcome="taxa N1/VIC ponderada (Q2)", variante="sem capitais", ciclo=rot_c,
                corte=corte, metodo="local linear h=0,050", **r)
            Zs = np.column_stack([(ms_["ciclo"] == k).astype(float) * ms_["vic"] for k in ks])
            r = rd(ms_["s"], ms_["n_alocados"], corte, grupo=ms_["ciclo"], cluster=ms_["co_ibge"], Z=Zs)
            add(unidade="municipio", outcome="N1 com controle VIC (S-a/Q1)", variante="sem capitais", ciclo=rot_c,
                corte=corte, metodo="local linear h=0,050", **r)
            r = rd(cc["s"], cc["preenchida"], corte, grupo=cc["ciclo"], cluster=cc["co_ibge"],
                   fe=[cc["fe_cc"], cc["com_imediata_versao_pipe"], cc["capital"]])
            add(unidade="celula", outcome="A3_pipeline (>=1 alocado; c1 = confirmado)",
                variante="FE do pipeline + dummy de capital", ciclo=rot_c, corte=corte,
                metodo="local linear h=0,050", **r)
            r = rd(mm["s"], mm["n_alocados"] / mm["vic"], corte, grupo=mm["ciclo"], cluster=mm["co_ibge"],
                   peso=mm["vic"], fe=[mm["capital"]])
            add(unidade="municipio", outcome="taxa N1/VIC ponderada (Q2)", variante="com dummy de capital",
                ciclo=rot_c, corte=corte, metodo="local linear h=0,050", **r)
            Zk = np.column_stack([(mm["ciclo"] == k).astype(float) * mm["vic"] for k in ks] + [mm["capital"]])
            r = rd(mm["s"], mm["n_alocados"], corte, grupo=mm["ciclo"], cluster=mm["co_ibge"], Z=Zk)
            add(unidade="municipio", outcome="N1 com controle VIC (S-a/Q1)", variante="com dummy de capital",
                ciclo=rot_c, corte=corte, metodo="local linear h=0,050", **r)
            # --- composição: célula só de CR, nas duas versões (célula, sem FE) ---
            for var, col in (("célula só de CR, versão pré-alocação (c2 = 13/02)", "so_cr_pre"),
                             ("célula só de CR, versão do pipeline (c2 = 19/03)", "so_cr_pipe"),
                             ("célula em capital", "capital")):
                r = rd(cc["s"], cc[col], corte, grupo=cc["ciclo"], cluster=cc["co_ibge"])
                add(unidade="celula", outcome="composicao", variante=var, ciclo=rot_c, corte=corte,
                    metodo="local linear h=0,050, sem FE", **r)
            # --- médias cruas nas janelas ---
            for jan in (10, 20, 50):
                r = dif_medias(cc["s"], cc["preenchida"], corte, janela_mil=jan, cluster=cc["co_ibge"])
                add(unidade="celula", outcome="A3_pipeline (>=1 alocado; c1 = confirmado)",
                    variante=f"média crua cima − baixo, |IVS − corte| < {jan/1000:.3f}", ciclo=rot_c, corte=corte,
                    metodo="diferença de médias, CR1 municipio", **r)
                r = dif_medias(cc["s"], cc["preenchida"], corte, janela_mil=jan, cluster=cc["co_ibge"],
                               grupo=cc["ciclo"], fe=[cc["fe_cc"]])
                add(unidade="celula", outcome="A3_pipeline (>=1 alocado; c1 = confirmado)",
                    variante=f"diferença na janela ±{jan/1000:.3f} com FE curso x ciclo", ciclo=rot_c, corte=corte,
                    metodo="diferença de médias com FE, CR1 municipio", **r)
                cn = cc[cc["capital"] == 0]
                r = dif_medias(cn["s"], cn["preenchida"], corte, janela_mil=jan, cluster=cn["co_ibge"])
                add(unidade="celula", outcome="A3_pipeline (>=1 alocado; c1 = confirmado)",
                    variante=f"média crua sem capitais, ±{jan/1000:.3f}", ciclo=rot_c, corte=corte,
                    metodo="diferença de médias, CR1 municipio", **r)
                mn = mm[mm["capital"] == 0]
                r = dif_medias(mn["s"], mn["n_alocados"] / mn["vic"], corte, janela_mil=jan, cluster=mn["co_ibge"],
                               peso=mn["vic"])
                add(unidade="municipio", outcome="taxa N1/VIC ponderada (Q2)",
                    variante=f"média crua sem capitais, ±{jan/1000:.3f}", ciclo=rot_c, corte=corte,
                    metodo="diferença de médias ponderada por vagas, CR1 municipio", **r)
                ci = cc[cc["com_imediata_pre"] == 1]
                r = dif_medias(ci["s"], ci["preenchida"], corte, janela_mil=jan, cluster=ci["co_ibge"])
                add(unidade="celula", outcome="A3_pipeline (>=1 alocado; c1 = confirmado)",
                    variante=f"média crua só células com imediata pré-alocação, ±{jan/1000:.3f}", ciclo=rot_c,
                    corte=corte, metodo="diferença de médias, CR1 municipio", **r)
                r = dif_medias(mm["s"], mm["n_alocados"] / mm["vic"], corte, janela_mil=jan, cluster=mm["co_ibge"],
                               peso=mm["vic"])
                add(unidade="municipio", outcome="taxa N1/VIC ponderada (Q2)",
                    variante=f"média crua cima − baixo, ±{jan/1000:.3f}", ciclo=rot_c, corte=corte,
                    metodo="diferença de médias ponderada por vagas, CR1 municipio", **r)
                r = dif_medias(mm["s"], mm["n_alocados"], corte, janela_mil=jan, cluster=mm["co_ibge"])
                add(unidade="municipio", outcome="N1 sem controle (S-b)",
                    variante=f"média crua cima − baixo, ±{jan/1000:.3f}", ciclo=rot_c, corte=corte,
                    metodo="diferença de médias, CR1 municipio", **r)
            # sem reta (grau 0) na janela 0,050 com kernel triangular
            r = rd(cc["s"], cc["preenchida"], corte, grupo=cc["ciclo"], cluster=cc["co_ibge"], grau=0,
                   fe=[cc["fe_cc"], cc["com_imediata_versao_pipe"]])
            add(unidade="celula", outcome="A3_pipeline (>=1 alocado; c1 = confirmado)",
                variante="local constante (sem reta), kernel triangular h=0,050, FE do pipeline", ciclo=rot_c,
                corte=corte, metodo="local constante", **r)
    # --- influência: tirar um município por vez (0,300, ciclos empilhados) ---
    for corte in CORTES:
        cc, mm = c, m
        base_a3 = rd(cc["s"], cc["preenchida"], corte, grupo=cc["ciclo"], cluster=cc["co_ibge"],
                     fe=[cc["fe_cc"], cc["com_imediata_versao_pipe"]])["salto"]
        base_q2 = rd(mm["s"], mm["n_alocados"] / mm["vic"], corte, grupo=mm["ciclo"], cluster=mm["co_ibge"],
                     peso=mm["vic"])["salto"]
        janela = mm.loc[(mm["s"] - corte).abs() < H, "co_ibge"].unique()
        for ib in janela:
            c1_ = cc[cc["co_ibge"] != ib]
            m1_ = mm[mm["co_ibge"] != ib]
            a3 = rd(c1_["s"], c1_["preenchida"], corte, grupo=c1_["ciclo"], cluster=c1_["co_ibge"],
                    fe=[c1_["fe_cc"], c1_["com_imediata_versao_pipe"]])["salto"]
            q2 = rd(m1_["s"], m1_["n_alocados"] / m1_["vic"], corte, grupo=m1_["ciclo"], cluster=m1_["co_ibge"],
                    peso=m1_["vic"])["salto"]
            add(unidade="influencia", outcome="sem um municipio", variante=str(ib), ciclo="1+2+3", corte=corte,
                metodo="local linear h=0,050; salto refeito sem o municipio",
                salto_A3_sem=a3, salto_A3_com=base_a3, salto_Q2_sem=q2, salto_Q2_com=base_q2,
                ivs=float(mm.loc[mm["co_ibge"] == ib, "ivs"].iloc[0]),
                celulas=int((cc["co_ibge"] == ib).sum()), vic=int(mm.loc[mm["co_ibge"] == ib, "vic"].sum()))
    est = pd.DataFrame(linhas)
    est["natureza_dos_dados"] = NAT
    est["rotulo"] = ROTULO
    return est


def gravado_contra_refeito(est: pd.DataFrame) -> pd.DataFrame:
    """Linhas do pipeline (N, NA) contra as mesmas linhas refeitas aqui, dos arquivos brutos."""
    na = pd.read_csv(PIPE_EST["NA"], dtype=str)
    n = pd.read_csv(PIPE_EST["N"], dtype=str)
    pops = {"1": "V1", "2": "V2", "3": "V3", "1+2+3": "V1+V2+V3"}
    out = []
    for ciclo, pop in pops.items():
        for corte in CORTES:
            cs = f"{corte/1000:.3f}"
            alvo = [
                ("A3 célula preenchida", na[(na["outcome_id"] == "A3_PREENCHIDA") & (na["variante"] == "principal")
                                            & (na["populacao"] == f"{pop} (celulas)") & (na["corte"] == cs)],
                 ("celula", "A3_pipeline (>=1 alocado; c1 = confirmado)",
                  "FE curso x ciclo + tipo de vaga (versão do pipeline: c2 = 19/03)")),
                ("N1 com controle (S-a)", n[(n["especificacao"] == "S-a") & (n["outcome_id"] == "N1")
                                            & (n["variante"] == "principal") & (n["populacao"] == pop)
                                            & (n["corte"] == cs)],
                 ("municipio", "N1 com controle VIC (S-a/Q1)", "pipeline")),
                ("taxa por vaga (S-e/Q2)", n[(n["especificacao"] == "S-e") & (n["outcome_id"] == "N1")
                                             & (n["populacao"] == pop) & (n["corte"] == cs)],
                 ("municipio", "taxa N1/VIC ponderada (Q2)", "pipeline")),
                ("N1 sem controle (S-b)", n[(n["especificacao"] == "S-b") & (n["outcome_id"] == "N1")
                                            & (n["variante"] == "principal") & (n["populacao"] == pop)
                                            & (n["corte"] == cs)],
                 ("municipio", "N1 sem controle (S-b)", "pipeline")),
            ]
            for nome, g, (un, oc, var) in alvo:
                r = est[(est["unidade"] == un) & (est["outcome"] == oc) & (est["variante"] == var)
                        & (est["ciclo"] == ciclo) & (est["corte"] == corte)]
                if g.empty or r.empty:
                    out.append({"linha": nome, "ciclo": ciclo, "corte": corte, "nota": "sem linha correspondente"})
                    continue
                gv = float(g["tau"].iloc[0])
                rv = float(r["salto"].iloc[0])
                out.append({"linha": nome, "ciclo": ciclo, "corte": corte, "gravado": gv, "refeito": rv,
                            "dif_abs": abs(gv - rv), "ep_gravado": float(g["ep"].iloc[0]), "ep_refeito": float(r["ep"].iloc[0])})
    d = pd.DataFrame(out)
    d["natureza_dos_dados"] = NAT
    d["rotulo"] = ROTULO
    return d


def vizinhos(mun: pd.DataFrame, cel: pd.DataFrame) -> pd.DataFrame:
    out = []
    m = mun[mun["ivs"].notna()].copy()
    m["s"] = np.round(m["ivs"] * 1000)
    for corte in CORTES:
        base = m.groupby("co_ibge").agg(s=("s", "first"), nome=("nome_municipio_uf", "first"),
                                        faixa=("faixa_impressa", "first")).reset_index()
        base["dist"] = base["s"] - corte
        ab = base[base["dist"] <= 0].sort_values("dist", ascending=False).head(5)
        ac = base[base["dist"] > 0].sort_values("dist").head(5)
        for lado, bb in (("abaixo", ab), ("acima", ac)):
            for _, b in bb.iterrows():
                for k in (1, 2, 3):
                    l = m[(m["co_ibge"] == b["co_ibge"]) & (m["ciclo"] == k)]
                    if l.empty:
                        out.append({"corte": corte, "lado": lado, "co_ibge": b["co_ibge"], "municipio": b["nome"],
                                    "ivs": b["s"] / 1000, "faixa_impressa": b["faixa"], "ciclo": k,
                                    "no_quadro": False})
                        continue
                    l = l.iloc[0]
                    out.append({"corte": corte, "lado": lado, "co_ibge": b["co_ibge"], "municipio": b["nome"],
                                "ivs": b["s"] / 1000, "faixa_impressa": b["faixa"], "ciclo": k, "no_quadro": True,
                                "n_celulas": int(l["n_celulas"]), "celulas_so_cr_pre": int(l["n_celulas"] - l["n_cel_imediata_pre"]),
                                "vagas_imediatas_pre": int(l["vi_pre"]), "vagas_imediatas_mais_cr": int(l["vic"]),
                                "cand_1a_opcao": int(l["n_cand_1a"]), "alocados": int(l["n_alocados"]),
                                "celulas_preenchidas": int(l["n_celulas_preenchidas"]),
                                "taxa_por_vaga": float(l["n_alocados"] / l["vic"]),
                                "alocados_ciclo1_desconsiderados_q2": int(l.get("n_desconsiderados", 0) or 0),
                                "homologados_ciclo1": int(l.get("n_homologados", 0) or 0)})
    v = pd.DataFrame(out)
    v["natureza_dos_dados"] = NAT
    v["rotulo"] = ROTULO
    return v


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    reg: dict = {"rotulo": ROTULO, "natureza_dos_dados": NAT,
                 "scripts": ["scripts/auditoria_H1/a36_reconstruir_H1.py", "scripts/auditoria_H1/a36_leitura.py",
                             "scripts/auditoria_H1/a36_estimador.py"],
                 "nao_importa": "scripts/rdd_bolsa/* (12, 23, 24, 38, rdd_lib) nem scripts/aquisicao/*"}
    c1, a1, r1, h1, q1 = montar_ciclo1(reg)
    c2, f2, p2, q20, q21, q22 = montar_ciclo2(reg)
    c3, r3, q3 = montar_ciclo3(reg)
    ivs = ler_ivs().set_index("co_ibge")
    cel = pd.concat([c1, c2, c3], ignore_index=True, sort=False)
    cel["co_ibge"] = cel["ibge_impresso"]
    cel["ivs"] = cel["co_ibge"].map(ivs["ivs"])
    cel["nome_municipio_uf"] = cel["co_ibge"].map(ivs["nome_municipio_uf"])
    cel["faixa_regra_ivs_oficial"] = cel["ivs"].map(faixa_regra)
    cel["vagas_cr_pipe"] = cel["vagas_cr"]
    cel["vic"] = cel["vagas_imediatas"] + cel["vagas_cr"]
    cel["com_imediata_versao_pipe"] = (cel["vagas_imediatas_pipe_versao"] > 0).astype(int)
    cel["com_imediata_pre"] = (cel["vagas_imediatas_pre"] > 0).astype(int)
    cel["preenchida"] = (cel["n_alocados"] >= 1).astype(int)
    cel["preenchida_pipe_def"] = np.where(cel["ciclo"] == 1,
                                          ((cel["n_alocados"] + cel["n_homologados"].fillna(0)) >= 1).astype(int),
                                          cel["preenchida"])
    cel["preenchida_c1_realoc"] = np.where(cel["ciclo"] == 1,
                                           ((cel["n_alocados"] + cel["n_realocados_q2"].fillna(0)) >= 1).astype(int),
                                           cel["preenchida"])
    cel["preenchida_sj"] = (cel["n_alocados_sj"] >= 1).astype(int)
    cel["n_alocados_em_imediata_pre"] = np.where(cel["com_imediata_pre"] == 1, cel["n_alocados"], 0)
    cel["vic_em_imediata_pre"] = np.where(cel["com_imediata_pre"] == 1, cel["vic"], 0)
    cel["n_classif"] = cel["n_alocados"] + np.where(cel["ciclo"] == 1, cel["n_desconsiderados"].fillna(0), 0)
    cel["preenchida_c1_classif"] = (cel["n_classif"] >= 1).astype(int)
    capitais_c3 = set(cel.loc[cel["tipo_municipio"].astype(str) == "CAPITAL", "ibge_impresso"])
    if not capitais_c3 <= CAPITAIS:
        raise SystemExit("capital do quadro do ciclo 3 fora da lista de capitais")
    capitais = CAPITAIS
    reg["capitais"] = {"lista": "27 capitais (códigos IBGE de 6 dígitos)", "marcadas_CAPITAL_no_quadro_c3": len(capitais_c3),
                       "capitais_em_algum_quadro": int(cel["ibge_impresso"].isin(capitais).groupby(cel["ibge_impresso"]).first().sum())}
    cel["capital"] = cel["ibge_impresso"].isin(capitais).astype(int)
    cel["so_cr_pre"] = 1 - cel["com_imediata_pre"]
    cel["so_cr_pipe"] = 1 - cel["com_imediata_versao_pipe"]
    # Município × ciclo
    agg = {"n_celulas": ("chave", "size"), "vagas_imediatas_pipe_versao": ("vagas_imediatas_pipe_versao", "sum"),
           "vagas_cr_pipe": ("vagas_cr", "sum"), "vic": ("vic", "sum"), "vi_pre": ("vagas_imediatas_pre", "sum"),
           "n_cel_imediata_pre": ("com_imediata_pre", "sum"), "n_alocados": ("n_alocados", "sum"),
           "n_alocados_em_imediata_pre": ("n_alocados_em_imediata_pre", "sum"),
           "vic_em_imediata_pre": ("vic_em_imediata_pre", "sum"), "n_classif": ("n_classif", "sum"),
           "n_celulas_preenchidas": ("preenchida", "sum"), "n_cand_1a": ("n_cand_1a", "sum"),
           "faixa_impressa": ("faixa_impressa", "first"), "ivs": ("ivs", "first"), "capital": ("capital", "first"),
           "nome_municipio_uf": ("nome_municipio_uf", "first"),
           "n_desconsiderados": ("n_desconsiderados", "sum"), "n_homologados": ("n_homologados", "sum")}
    mun = cel.groupby(["ciclo", "co_ibge"]).agg(**agg).reset_index()
    # 5. faixa e IVS
    mm = mun.drop_duplicates(["ciclo", "co_ibge"])
    reg["faixa_e_ivs"] = {
        "regra": "IVS ≤ 0,300 → faixa 3; 0,300 < IVS ≤ 0,400 → faixa 2; IVS > 0,400 → faixa 1",
        "municipios_por_ciclo": {str(k): int(v) for k, v in mm.groupby("ciclo").size().items()},
        "sem_ivs_oficial": mm[mm["ivs"].isna()][["ciclo", "co_ibge"]].astype(str).values.tolist(),
        "faixa_impressa_diferente_da_regra": int((mm["ivs"].notna() & (mm["faixa_impressa"]
                                                                        != mm["ivs"].map(faixa_regra))).sum()),
        "ivs_errado_lido_por_esta_auditoria": False,
    }
    # Chaves
    quadros = {"c1_original": q1, "c2_03fev": q20, "c2_13fev": q21, "c2_19mar": q22, "c3_24jul": q3,
               "c3_16jul": ler_quadro(ARQ["c3_quadro_orig"]),
               "c2_ch2_quadro": ler_quadro(ARQ["c2_ch2_quadro"]),
               "c1_ch2_quadro_cr": ler_quadro(ARQ["c1_ch2_quadro_aloc"], sheet="VAGAS - CADASTRO RESERVA")}
    rc22 = ler_resultado(ARQ["c2_ch2_result"])
    rc22["aloc"] = rc22["SITUACAO"].map(alocado)
    resultados = {"c1_alocacao_sub_judice": (a1, q1), "c1_realocacao_quadro2": (r1, q1),
                  "c1_homologados": (h1, q1), "c2_resultado_final": (f2, q22), "c2_resultado_preliminar": (p2, q22),
                  "c2_ch2_resultado_contra_quadro_ch1": (rc22, q22), "c3_resultado_sub_judice": (r3, q3)}
    p2["aloc"] = p2["SITUACAO"].map(alocado)
    reg["chaves"] = auditar_chaves(quadros, resultados)
    # 8. alocado em 2a opção: pessoa com mais de um alocado e linha alocada é a da célula
    reg["segunda_opcao"] = {
        "c1_confirmados_2a_opcao": int(((a1["op"] == 2) & a1["conf"]).sum()),
        "c2_alocados_2a_opcao": int(((f2["op"] == 2) & f2["aloc"]).sum()),
        "c3_alocados_2a_opcao": int(((r3["op"] == 2) & r3["aloc"]).sum()),
        "c2_pessoas_com_mais_de_um_alocado": int((f2[f2["aloc"]].groupby("id_cand").size() > 1).sum()),
        "nota": "cada linha do resultado é candidato × opção com a célula da opção; a linha marcada ALOCADO/"
                "CONFIRMADO é a da célula onde a pessoa ficou; contar por essa linha atribui o alocado de 2a opção "
                "à célula da 2a opção",
    }
    # Comparação com o pipeline
    dv, res_cmp = comparar(cel, mun)
    reg["comparacao_pipeline"] = res_cmp
    # Conferência: o caminho da H1 não lê o IVS errado
    scripts_h1 = ["scripts/rdd_bolsa/12_construir_outcomes_funil.py", "scripts/rdd_bolsa/23_estimar_contagem_vagas.py",
                  "scripts/rdd_bolsa/24_abertura_vagas_selecao.py", "scripts/rdd_bolsa/38_diagnostico_queda_0300.py",
                  "scripts/rdd_bolsa/13_estimar_E6_funil.py", "scripts/rdd_bolsa/rdd_lib.py"]
    reg["ivs_errado_no_caminho_H1"] = {s: ("ivs_ipea_2010_municipios" in (RAIZ / s).read_text(encoding="utf-8"))
                                       for s in scripts_h1}
    # Estimativas
    est = estimativas(cel, mun)
    viz = vizinhos(mun, cel)
    gr = gravado_contra_refeito(est)
    gr.to_csv(OUT / "a36_gravado_contra_refeito.csv", index=False)
    reg["gravado_contra_refeito"] = {"linhas": int(gr["gravado"].notna().sum()),
                                     "maior_diferenca_absoluta": float(gr["dif_abs"].max()),
                                     "sem_correspondente": int(gr["gravado"].isna().sum())}
    # Entradas
    reg["entradas"] = {k: {"caminho": str(p.relative_to(RAIZ)), "sha256": sha256(p)} for k, p in ARQ.items()}
    reg["entradas"]["ivs_oficial"] = {"caminho": str(IVS_OFICIAL.relative_to(RAIZ)), "sha256": sha256(IVS_OFICIAL)}
    reg["entradas"]["pipeline_celula"] = {"caminho": str(PIPE_CEL.relative_to(RAIZ)), "sha256": sha256(PIPE_CEL)}
    reg["entradas"]["pipeline_municipio"] = {"caminho": str(PIPE_MUN.relative_to(RAIZ)), "sha256": sha256(PIPE_MUN)}
    # Gravar (sem colunas pessoais; só contagens)
    cols_cel = ["ciclo", "chave", "cnes", "cod_curso", "co_ibge", "uf", "faixa_impressa", "ivs", "faixa_regra_ivs_oficial",
                "vagas_imediatas", "vagas_cr", "vagas_imediatas_pre", "vagas_imediatas_pipe_versao",
                "vagas_imediatas_13fev", "vagas_cr_13fev", "vagas_imediatas_03fev", "vagas_imediatas_16jul",
                "com_imediata_pre", "com_imediata_versao_pipe", "n_cand_1a", "n_alocados", "n_alocados_prelim",
                "n_desconsiderados", "n_realocados_q2", "n_homologados", "n_sub_judice", "n_remanescentes_9",
                "n_remanescentes_81", "preenchida", "preenchida_pipe_def", "preenchida_c1_realoc", "preenchida_sj",
                "versao_quadro"]
    out_cel = cel[cols_cel].copy()
    for c in out_cel.columns:
        if out_cel[c].dtype == object:
            out_cel[c] = out_cel[c].astype(str)
    out_cel["natureza_dos_dados"] = NAT
    out_cel["rotulo"] = ROTULO
    out_mun = mun.copy()
    out_mun["natureza_dos_dados"] = NAT
    out_mun["rotulo"] = ROTULO
    out_cel.to_csv(OUT / "a36_celulas.csv", index=False)
    out_mun.to_csv(OUT / "a36_municipios.csv", index=False)
    dv["natureza_dos_dados"] = NAT
    dv["rotulo"] = ROTULO
    dv.to_csv(OUT / "a36_divergencias_pipeline.csv", index=False)
    est.to_csv(OUT / "a36_estimativas.csv", index=False)
    viz.to_csv(OUT / "a36_vizinhos_0300_0400.csv", index=False)
    reg["saidas"] = {p.name: sha256(p) for p in sorted(OUT.glob("a36_*.csv"))}
    (OUT / "a36_resumo.json").write_text(json.dumps(reg, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps({k: reg[k] for k in ("ciclo1", "ciclo2_versoes", "ciclo3", "faixa_e_ivs", "segunda_opcao",
                                           "comparacao_pipeline", "ivs_errado_no_caminho_H1")},
                     ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main()
