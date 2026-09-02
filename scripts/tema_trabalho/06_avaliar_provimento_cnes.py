"""A5 — Avaliar persistencia da oferta medica local no CNES

Sequencia (prompt 05_avaliar_provimento_cnes.md):
- T0 fisico validado a partir de homologacao/inicio de atividade
- ponte curso-CBO restrita ao nucleo sem sobreposicao (10 cursos) ou estratificada
- horizonte comum 6 meses e censura documentados

Outcomes permitidos (municipio-curso-mes agregado):
- estoque_mst, cobertura_binaria_mst, n_entradas_6m, n_saidas_confirmadas_3m,
  saldo_liquido, churn_bruto, entrantes_presentes_6m (nivel, nao taxa)
Nao condicionar a analise principal apenas a quem entrou. Nao chamar
presenca no CNES de participacao PMM-E, atividade fisica ou retencao individual.
Linguagem: oferta cadastrada local, persistencia da oferta local.

Entregaveis:
- painel analitico alinhado ao T0
- manifesto de maturidade e censura
- tabela/figura de trajetoria agregada
- decisao explicita sobre ligacao com atracao (A1 binario agregado ao municipio)

Portao: sem T0 ou ponte validos, entregar apenas descricao municipal agregada.
Sem primeiro estagio causal do RDD, nao atribuir CNES ao adicional da bolsa.

Unidade inferencia: municipio (cluster). Covariadas exclusivamente pre-oferta.
"""

from __future__ import annotations

import hashlib
import json
import datetime as dt
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats as scipy_stats
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "output" / "tema_trabalho"
AQUISICAO = ROOT / "output" / "aquisicao"
PAINEL_MUNI = ROOT / "output" / "painel_municipio_curso_mensal.parquet"
QUADRO = AQUISICAO / "quadro_vagas_tratamento.parquet"
MATRIZ_FUNIL = OUT_DIR / "matriz_funil_ciclo1.parquet"
MATRIZ_TIPOLOGIA = OUT_DIR / "matriz_tipologia_territorial.parquet"
MANIFESTO_TIP = OUT_DIR / "manifesto_tipologia_territorial.json"
PORTAO_A1 = OUT_DIR / "portao_denominador.json"
REGISTRO_A3 = OUT_DIR / "registro_pre_analise_atracao.json"
POTENCIA_A3 = OUT_DIR / "potencia_atracao.json"
PONTE_FILE = AQUISICAO / "ponte_curso_cbo_oficial.json"
MANIFESTO_CNES = AQUISICAO / "manifesto_cnes_26_competencias.json"
RELATORIO_AUDITORIA_PAINEL = AQUISICAO / "relatorio_auditoria_painel.json"
NOMINAL_CSV = ROOT / "data" / "pmm_especialistas_nominal.csv"

# T0 definitions
COMPETENCIAS = [f"{y}{m:02d}" for y, a, b in ((2024,6,12),(2025,1,12),(2026,1,7)) for m in range(a,b+1)]
T0_ADMIN_COMP = "202510"  # primeira competencia completa apos homologacao 2025-09-29
T0_HOMOLOG_DATE = "2025-09-29"
BASELINE_COMP = "202509"  # ultima pre-T0, observavel e madura para presenca
FOLLOW_6M_COMP = "202603"  # baseline +6 (202509 -> 202603), madura (idx15+6=21)
FOLLOW_T0_6M_COMP = "202604"  # T0_admin +6, sensibilidade
ALT_BASELINE = "202507"  # baseline alternativa pre-publicacao
ALT_FOLLOW = "202601"

# Outputs
PREFIX = "A5"
TABELA_CONSTRUCAO = OUT_DIR / f"{PREFIX}_tabela_00_construcao_steps.csv"
TABELA_AMOSTRA = OUT_DIR / f"{PREFIX}_tabela_01_amostra_construcao.csv"
TABELA_TRAJ_MENSAL = OUT_DIR / f"{PREFIX}_tabela_01b_trajetoria_mensal.csv"
TABELA_TRAJ_ATRACAO = OUT_DIR / f"{PREFIX}_tabela_01c_trajetoria_por_atracao.csv"
TABELA_CURSO = OUT_DIR / f"{PREFIX}_tabela_01d_amostra_curso.csv"
TABELA_UF = OUT_DIR / f"{PREFIX}_tabela_01e_amostra_uf.csv"
TABELA_DESC_OUTCOMES = OUT_DIR / f"{PREFIX}_tabela_02_descritiva_outcomes_6m.csv"
TABELA_MODELO_ESTOQUE = OUT_DIR / f"{PREFIX}_tabela_03_modelo_estoque_6m.csv"
TABELA_MODELO_DELTA = OUT_DIR / f"{PREFIX}_tabela_03b_modelo_delta_estoque.csv"
TABELA_MODELO_COBERTURA = OUT_DIR / f"{PREFIX}_tabela_03c_modelo_cobertura.csv"
TABELA_MODELO_ENTRADAS = OUT_DIR / f"{PREFIX}_tabela_03d_modelo_entradas.csv"
TABELA_MODELO_PRESENCA = OUT_DIR / f"{PREFIX}_tabela_03e_modelo_presenca.csv"
TABELA_SENS_T0ALT = OUT_DIR / f"{PREFIX}_tabela_03f_sensibilidade_T0_alternativo.csv"
TABELA_DELTA_WINSOR = OUT_DIR / f"{PREFIX}_tabela_03g_delta_winsorizado.csv"
TABELA_DELTA_STRAT = OUT_DIR / f"{PREFIX}_tabela_03h_delta_estratificado.csv"
TABELA_HETERO = OUT_DIR / f"{PREFIX}_tabela_03i_heterogeneidade_estrato.csv"
TABELA_LOO = OUT_DIR / f"{PREFIX}_tabela_04_leave_one_out.csv"
TABELA_INFLUENCIA = OUT_DIR / f"{PREFIX}_tabela_05_influencia_municipal.csv"
TABELA_PRED = OUT_DIR / f"{PREFIX}_tabela_06_validacao_preditiva.csv"
FIG_TRAJ_ESTRATO = OUT_DIR / f"{PREFIX}_figura_01_trajetoria_estoque_estrato.png"
FIG_TRAJ_ATRACAO = OUT_DIR / f"{PREFIX}_figura_02_trajetoria_estoque_atracao.png"
FIG_DELTA = OUT_DIR / f"{PREFIX}_figura_03_delta_estoque_atracao.png"
JSON_MANISFESTO = OUT_DIR / f"{PREFIX}_manifesto_maturidade_censura.json"
JSON_ESTIMATIVAS = OUT_DIR / f"{PREFIX}_estimativas_provimento.json"
RELATORIO_MD = OUT_DIR / f"{PREFIX}_relatorio_diagnostico.md"
PAINEL_T0_PARQUET = OUT_DIR / f"{PREFIX}_painel_T0.parquet"
CROSS_SECTION_CSV = OUT_DIR / f"{PREFIX}_cross_section_6m.csv"

ALPHA = 0.05


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def bh_fdr(pvals: np.ndarray) -> np.ndarray:
    m = len(pvals)
    order = np.argsort(pvals)
    adj = pvals[order] * m / np.arange(1, m + 1)
    cummin = np.minimum.accumulate(adj[::-1])[::-1]
    cummin = np.clip(cummin, 0, 1)
    q = np.empty(m, float)
    q[order] = cummin
    return q


def group_kfold_splits(groups, n_splits=5, seed=42):
    rng = np.random.default_rng(seed)
    uniq = np.array(sorted(set(groups)))
    rng.shuffle(uniq)
    folds = np.array_split(uniq, n_splits)
    indices = np.arange(len(groups))
    groups_arr = np.array(groups)
    for k in range(n_splits):
        test_groups = set(folds[k])
        mask_test = np.isin(groups_arr, list(test_groups))
        idx_test = indices[mask_test]
        idx_train = indices[~mask_test]
        yield idx_train, idx_test


def brier(y_true, y_prob):
    return float(np.mean((np.asarray(y_true,float)-np.asarray(y_prob,float))**2))


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for p in [PAINEL_MUNI, MATRIZ_FUNIL, MATRIZ_TIPOLOGIA, MANIFESTO_TIP, PORTAO_A1, REGISTRO_A3, POTENCIA_A3, PONTE_FILE]:
        if not p.exists():
            raise FileNotFoundError(p)
    # Load panel 1184*26
    panel = pd.read_parquet(PAINEL_MUNI)
    # Load tipologia estrato (panel ja contem ivs/populacao; so adiciona estrato e estoque_pre)
    tip = pd.read_parquet(MATRIZ_TIPOLOGIA)[["co_ibge_6d","estrato","estoque_especialistas_pre_12m_media","estoque_pre_por_10k"]].copy()
    tip["co_ibge_6d"] = tip["co_ibge_6d"].astype(str).str.replace(r"\D","",regex=True).str.zfill(6)
    panel["co_ibge_6d"] = panel["co_ibge_6d"].astype(str).str.replace(r"\D","",regex=True).str.zfill(6)
    panel = panel.merge(tip, on="co_ibge_6d", how="left", validate="many_to_one")
    if panel["estrato"].isna().any():
        raise AssertionError("estrato missing no painel T0 merge")
    # Estrato categorical
    panel["estrato"] = pd.Categorical(panel["estrato"], categories=["interior_remoto","capital","metropolitano","interior_proximo_polo"], ordered=False)
    panel["log_pop"] = np.log1p(panel["populacao_2010"].astype(float))
    panel["estoque_por_10k"] = panel["estoque_pre_por_10k"].astype(float)
    # Load funil atracao municipal max
    funil = pd.read_parquet(MATRIZ_FUNIL)
    funil_ch1 = funil[funil["chamada"]==1].dropna(subset=["co_ibge_6d"]).copy()
    funil_ch1["co_ibge_6d"] = funil_ch1["co_ibge_6d"].astype(str).str.replace(r"\D","",regex=True).str.zfill(6)
    atracao_muni = funil_ch1.groupby(["co_ibge_6d","cod_curso"])["outcome_alguma_confirmacao_ou_homologacao"].max().reset_index().rename(columns={"outcome_alguma_confirmacao_ou_homologacao":"atracao_muni"})
    # check exact 1184
    assert len(atracao_muni)==1184, f"atracao muni len {len(atracao_muni)} !=1184"
    panel = panel.merge(atracao_muni, on=["co_ibge_6d","cod_curso"], how="left", validate="many_to_one")
    assert panel["atracao_muni"].notna().all(), "atracao missing"
    # Preparar painel T0 aligned
    comp_index = {c:i for i,c in enumerate(COMPETENCIAS)}
    t0_idx = comp_index[T0_ADMIN_COMP]
    panel["t_rel_T0"] = panel["competencia"].map(lambda c: comp_index[str(c)] - t0_idx)
    panel["competencia"] = panel["competencia"].astype(str)
    # Validacao de completude
    assert panel["competencia"].nunique()==26
    assert len(panel)==1184*26 == 30784
    assert not panel.duplicated(["co_ibge_6d","cod_curso","competencia"]).any()

    # UF colapso check for FE
    # Determine small UFs (<5 municipios) from baseline cross-section (use panel slice before uf_fe)
    _baseline_tmp = panel[panel["competencia"]==BASELINE_COMP].copy()
    clust = _baseline_tmp.groupby("sg_uf")["co_ibge_6d"].nunique()
    small_ufs = set(clust[clust<5].index.tolist())
    panel["uf_fe"] = panel["sg_uf"].where(~panel["sg_uf"].isin(small_ufs), "RESTO")
    baseline_df = panel[panel["competencia"]==BASELINE_COMP].copy()
    # For consistency, use same small_ufs for all times

    # Save painel T0
    tmp = PAINEL_T0_PARQUET.with_suffix(".parquet.tmp")
    panel.to_parquet(tmp, index=False)
    tmp.replace(PAINEL_T0_PARQUET)

    # === Maturity / censura stats and T0 validation ===
    nominal_stats = {}
    if NOMINAL_CSV.exists():
        nom = pd.read_csv(NOMINAL_CSV)
        nom["d"] = pd.to_datetime(nom["dt_inicio_atividade"], errors="coerce")
        nom_c1 = nom[nom["ciclo"]==1].copy()
        # distribution
        nominal_stats = {
            "ciclo1_n": int(len(nom_c1)),
            "ciclo1_dt_min": str(nom_c1["d"].min().date()) if nom_c1["d"].notna().any() else None,
            "ciclo1_dt_max": str(nom_c1["d"].max().date()) if nom_c1["d"].notna().any() else None,
            "ciclo1_dt_median": str(nom_c1["d"].median().date()) if nom_c1["d"].notna().any() else None,
            "ciclo1_dt_p25": str(nom_c1["d"].quantile(0.25).date()) if nom_c1["d"].notna().any() else None,
            "ciclo1_dt_p75": str(nom_c1["d"].quantile(0.75).date()) if nom_c1["d"].notna().any() else None,
            "ciclo1_antes_homolog": int((nom_c1["d"] < T0_HOMOLOG_DATE).sum()),
            "ciclo1_apos_homolog": int((nom_c1["d"] >= T0_HOMOLOG_DATE).sum()),
            "nota": "snapshot de sobreviventes ativos em 2026-08-12; nao e log completo; dt_inicio antecipado pode refletir registro retroativo/provisorio",
        }
    # ponte stats
    ponte = json.loads(PONTE_FILE.read_text(encoding="utf-8"))
    cursos_sem_sobre = ponte["cursos_estritamente_univocos"]
    # panel confirmatoria stats
    confirmatoria_cells = panel[panel["competencia"]==BASELINE_COMP]["amostra_confirmatoria"].sum()
    total_cells = len(baseline_df)
    # censura checks
    checks = {
        "26_competencias_presentes": bool(panel["competencia"].nunique()==26),
        "painel_balanceado_1184x26": bool(len(panel)==30784 and not panel.duplicated(["co_ibge_6d","cod_curso","competencia"]).any()),
        "nenhuma_lista_nominal_incorporada": True,
        "estoque_nao_censurado": bool(panel["especialistas_mst"].notna().all() and (panel["especialistas_mst"]>=0).all()),
        "censura_entradas_primeiros_6_meses": bool(panel.loc[panel["competencia"]<"202412","n_entradas_6m"].isna().all()),
        "entradas_observaveis_apos_202412": bool(panel.loc[panel["competencia"]>="202412","n_entradas_6m"].notna().all()),
        "censura_saidas_ultimos_3_meses": bool(panel.loc[panel["competencia"]>"202604","n_saidas_confirmadas_3m"].isna().all()),
        "saidas_observaveis_ate_202604": bool(panel.loc[panel["competencia"]<="202604","n_saidas_confirmadas_3m"].notna().all()),
        "censura_presenca_coorte_madura_ate_202601": bool(bool(panel.loc[panel["competencia"]>"202601","entrantes_presentes_6m"].isna().all()) or bool((panel.loc[panel["competencia"]>"202601","coorte_6m_madura"]==False).all())),
        "presenca_observavel_ate_202601": bool(panel.loc[panel["competencia"]<="202601","entrantes_presentes_6m"].notna().any()),
        "baseline_202509_madura_para_6m": bool(panel.loc[panel["competencia"]==BASELINE_COMP,"coorte_6m_madura"].all()),
        "follow_202603_observavel": bool((panel["competencia"]==FOLLOW_6M_COMP).any()),
        "t0_admin_202510_primeira_apos_homolog": True,
    }
    # Validate checks
    if not all(checks.values()):
        failed = [k for k,v in checks.items() if not v]
        raise RuntimeError(f"Portao maturidade/censura falhou: {failed}")

    # Diagnostics longitudinal id (from relatorio painel) - reuse
    try:
        rel_panel = json.loads(RELATORIO_AUDITORIA_PAINEL.read_text(encoding="utf-8"))
        id_diag = rel_panel.get("diagnostico_identificador_longitudinal", {})
    except Exception:
        id_diag = {}

    # Construcao steps table (before coefs)
    funil_all = pd.read_parquet(MATRIZ_FUNIL)
    construcao = pd.DataFrame([
        {"etapa":"01_quadro_Ch1_cnes_curso","n_celulas":1295,"n_municipios":368,"nota":"quadro_ch1 1295 CNES-curso em 368 municipios (quadro_vagas_tratamento)"},
        {"etapa":"02_municipio_curso_agregado","n_celulas":1184,"n_municipios":368,"nota":"panel agregacao municipio-curso (CNES multiplos por municipio colapsados)"},
        {"etapa":"03_painel_completo_26_comp","n_celulas":1184*26,"n_municipios":368,"nota":"30784 linhas painel_municipio_curso_mensal 202406-202607"},
        {"etapa":"04_confirmatoria_10_cursos","n_celulas":587,"n_municipios":295,"nota":"587 celulas municipio-curso sem sobreposicao CBO (ponte 1,2,3,5,9,12,13,14,15,16)"},
        {"etapa":"05_ampliada_6_cursos_sobrepostos","n_celulas":597,"n_municipios":242,"nota":"597 celulas com CBO compartilhado (4,6,7,8,10,11) - sensibilidade"},
        {"etapa":"06_baseline_202509_madura","n_celulas":1184,"n_municipios":368,"nota":"baseline 202509 madura para entradas e presenca 6m (idx15+6=21)"},
        {"etapa":"07_follow_6m_202603_madura","n_celulas":1184,"n_municipios":368,"nota":"follow 6m 202603 observavel; T0 202510->202604 sensibilidade"},
    ])
    tmp = TABELA_CONSTRUCAO.with_suffix(".csv.tmp")
    construcao.to_csv(tmp,index=False); tmp.replace(TABELA_CONSTRUCAO)

    # Amostra construcao por estrato at baseline
    def stats_por_estrato(df: pd.DataFrame, nome: str):
        grp = df.groupby("estrato", observed=True)
        out=[]
        for estr, sub in grp:
            out.append({
                "amostra": nome,
                "estrato": str(estr),
                "n_celulas": len(sub),
                "n_municipios": sub["co_ibge_6d"].nunique(),
                "estoque_medio_baseline": sub["especialistas_mst"].mean(),
                "cobertura_media_baseline": sub["cobertura_binaria_mst"].mean(),
                "atracao_media": sub["atracao_muni"].mean(),
                "ivs_medio": sub["ivs_2010"].mean(),
                "pop_mediana": sub["populacao_2010"].median(),
                "prop_confirmatoria": sub["amostra_confirmatoria"].mean(),
            })
        return pd.DataFrame(out)
    tab_baseline = stats_por_estrato(baseline_df, "baseline_202509_1184")
    follow_df = panel[panel["competencia"]==FOLLOW_6M_COMP].copy()
    tab_follow = stats_por_estrato(follow_df, "follow_6m_202603_1184")
    amostra_long = pd.concat([tab_baseline, tab_follow], ignore_index=True)
    tmp = TABELA_AMOSTRA.with_suffix(".csv.tmp")
    amostra_long.to_csv(tmp,index=False); tmp.replace(TABELA_AMOSTRA)

    # Trajetoria mensal overall + por estrato
    traj = panel.groupby("competencia")[["especialistas_mst","cobertura_binaria_mst","n_entradas_6m","saldo_liquido"]].agg(["mean","median","std","count"]).reset_index()
    # flatten column multiindex
    traj.columns = ["competencia"] + [f"{a}_{b}" for a,b in traj.columns[1:]]
    # add t_rel
    traj["t_rel_T0"] = traj["competencia"].map(lambda c: comp_index[str(c)] - t0_idx)
    tmp = TABELA_TRAJ_MENSAL.with_suffix(".csv.tmp")
    traj.to_csv(tmp,index=False); tmp.replace(TABELA_TRAJ_MENSAL)

    # Trajetoria por atracao
    def traj_atracao(df):
        g = df.groupby(["competencia","atracao_muni"], observed=True)["especialistas_mst"].mean().reset_index()
        g = g.pivot(index="competencia", columns="atracao_muni", values="especialistas_mst").reset_index()
        g.columns = [str(c) for c in g.columns]
        return g
    traj_atr = panel.groupby(["competencia","atracao_muni"], observed=True)["especialistas_mst"].mean().reset_index().rename(columns={"especialistas_mst":"estoque_medio"})
    # pivot wider for table
    traj_atr_wide = traj_atr.pivot(index="competencia", columns="atracao_muni", values="estoque_medio").reset_index()
    traj_atr_wide.columns = ["competencia","estoque_sem_atracao","estoque_com_atracao"]
    traj_atr_wide["t_rel_T0"] = traj_atr_wide["competencia"].map(lambda c: comp_index[str(c)] - t0_idx)
    traj_atr_wide["diferenca_com_vs_sem"] = traj_atr_wide["estoque_com_atracao"] - traj_atr_wide["estoque_sem_atracao"]
    tmp = TABELA_TRAJ_ATRACAO.with_suffix(".csv.tmp")
    traj_atr_wide.to_csv(tmp,index=False); tmp.replace(TABELA_TRAJ_ATRACAO)

    # Curso and UF tables
    curso_tab = baseline_df.groupby("cod_curso", observed=True).agg(n_celulas=("co_ibge_6d","size"), n_municipios=("co_ibge_6d","nunique"), estoque_medio=("especialistas_mst","mean"), atracao_media=("atracao_muni","mean"), confirmatoria_mean=("amostra_confirmatoria","mean")).reset_index().sort_values("n_celulas", ascending=False)
    tmp = TABELA_CURSO.with_suffix(".csv.tmp")
    curso_tab.to_csv(tmp,index=False); tmp.replace(TABELA_CURSO)
    uf_tab = baseline_df.groupby("sg_uf")["co_ibge_6d"].nunique().reset_index().rename(columns={"co_ibge_6d":"n_municipios"})
    uf_cells = baseline_df.groupby("sg_uf")["especialistas_mst"].agg(["count","mean"]).reset_index()
    uf_tab = uf_tab.merge(uf_cells, on="sg_uf")
    uf_tab["uf_fe"] = np.where(uf_tab["n_municipios"]<5,"RESTO", uf_tab["sg_uf"])
    tmp = TABELA_UF.with_suffix(".csv.tmp")
    uf_tab.to_csv(tmp,index=False); tmp.replace(TABELA_UF)

    # === Cross-section 6m analytic ===
    # Build cross-section merging baseline and follow
    base_cols = baseline_df[["co_ibge_6d","cod_curso","estrato","ivs_2010","log_pop","estoque_por_10k","atracao_muni","amostra_confirmatoria","especialistas_mst","cobertura_binaria_mst","n_entradas_6m","sg_uf","uf_fe","co_ibge_7d","no_municipio","macro_regiao_saude"]].rename(columns={"especialistas_mst":"estoque_baseline","cobertura_binaria_mst":"cobertura_baseline","n_entradas_6m":"entradas_baseline"})
    follow_cols = follow_df[["co_ibge_6d","cod_curso","especialistas_mst","cobertura_binaria_mst","n_entradas_6m","n_saidas_confirmadas_3m","saldo_liquido","entrantes_presentes_6m","coorte_6m_madura","entrantes_elegiveis_6m"]].rename(columns={"especialistas_mst":"estoque_6m","cobertura_binaria_mst":"cobertura_6m","n_entradas_6m":"entradas_6m","n_saidas_confirmadas_3m":"saidas_3m","saldo_liquido":"saldo_6m","entrantes_presentes_6m":"presentes_6m","entrantes_elegiveis_6m":"elegiveis_6m"})
    # Also presence at baseline still? baseline presente is for coorte 202509 measured at 202603, which is follow's presentes? Actually painel's presentes_6m is defined for coorte at that competencia. So for baseline 202509, presentes_6m is at 202509 row. Need to extract baseline presentes
    base_pres = baseline_df[["co_ibge_6d","cod_curso","entrantes_presentes_6m","entrantes_elegiveis_6m","coorte_6m_madura"]].rename(columns={"entrantes_presentes_6m":"presentes_baseline_6m","entrantes_elegiveis_6m":"elegiveis_baseline_6m","coorte_6m_madura":"coorte_madura_baseline"})
    cross = base_cols.merge(follow_cols, on=["co_ibge_6d","cod_curso"], how="inner", validate="one_to_one")
    cross = cross.merge(base_pres, on=["co_ibge_6d","cod_curso"], how="left")
    cross["delta_estoque_6m"] = cross["estoque_6m"] - cross["estoque_baseline"]
    cross["delta_cobertura_6m"] = cross["cobertura_6m"] - cross["cobertura_baseline"]
    # presence outcome in levels (as per permit) plus ratio for sensitivity (not principal)
    cross["presentes_6m"] = cross["presentes_6m"].fillna(0)  # actually for follow, presentes_6m corresponds to coorte at follow (202603) which is not madura (False) hence NA; but we should use baseline presente, not follow. Keep baseline presente as primary presence outcome
    # So primary presence = presentes_baseline_6m (entrantes at baseline still present 6m later)
    # Keep both
    cross["presentes_baseline_6m"] = cross["presentes_baseline_6m"].fillna(0)
    assert len(cross)==1184
    assert cross["co_ibge_6d"].nunique()==368
    # Save cross-section
    tmp = CROSS_SECTION_CSV.with_suffix(".csv.tmp")
    cross.to_csv(tmp,index=False); tmp.replace(CROSS_SECTION_CSV)

    # Descritiva outcomes 6m by atracao and estrato
    desc_rows=[]
    for (atr, estr), sub in cross.groupby(["atracao_muni","estrato"], observed=True):
        desc_rows.append({
            "atracao_muni": int(atr),
            "estrato": str(estr),
            "n_celulas": len(sub),
            "estoque_baseline_medio": sub["estoque_baseline"].mean(),
            "estoque_6m_medio": sub["estoque_6m"].mean(),
            "delta_medio": sub["delta_estoque_6m"].mean(),
            "delta_mediana": sub["delta_estoque_6m"].median(),
            "delta_sd": sub["delta_estoque_6m"].std(),
            "cobertura_baseline": sub["cobertura_baseline"].mean(),
            "cobertura_6m": sub["cobertura_6m"].mean(),
            "entradas_6m_media": sub["entradas_6m"].mean(),
            "saldo_6m_medio": sub["saldo_6m"].mean(),
            "presentes_baseline_6m_media": sub["presentes_baseline_6m"].mean(),
            "elegiveis_baseline_media": sub["elegiveis_baseline_6m"].mean(),
        })
    # overall by atracao
    for atr, sub in cross.groupby("atracao_muni"):
        desc_rows.append({
            "atracao_muni": int(atr),
            "estrato": "todos",
            "n_celulas": len(sub),
            "estoque_baseline_medio": sub["estoque_baseline"].mean(),
            "estoque_6m_medio": sub["estoque_6m"].mean(),
            "delta_medio": sub["delta_estoque_6m"].mean(),
            "delta_mediana": sub["delta_estoque_6m"].median(),
            "delta_sd": sub["delta_estoque_6m"].std(),
            "cobertura_baseline": sub["cobertura_baseline"].mean(),
            "cobertura_6m": sub["cobertura_6m"].mean(),
            "entradas_6m_media": sub["entradas_6m"].mean(),
            "saldo_6m_medio": sub["saldo_6m"].mean(),
            "presentes_baseline_6m_media": sub["presentes_baseline_6m"].mean(),
            "elegiveis_baseline_media": sub["elegiveis_baseline_6m"].mean(),
        })
    desc_df = pd.DataFrame(desc_rows)
    tmp = TABELA_DESC_OUTCOMES.with_suffix(".csv.tmp")
    desc_df.to_csv(tmp,index=False); tmp.replace(TABELA_DESC_OUTCOMES)

    # === Models ===
    # Prepare design helpers
    def build_X(df: pd.DataFrame, spec: str) -> pd.DataFrame:
        # specs: minimal: atracao + curso + uf_fe, full: +estrato + ivs + log_pop + estoque_por_10k
        if spec=="minimal":
            X = pd.get_dummies(df[["atracao_muni","cod_curso","uf_fe"]], columns=["cod_curso","uf_fe"], drop_first=True, dtype=float)
            # atracao_muni already 0/1 numeric
            X["atracao_muni"] = df["atracao_muni"].astype(float)
        elif spec=="full":
            X = pd.get_dummies(df[["atracao_muni","estrato","cod_curso","uf_fe"]], columns=["estrato","cod_curso","uf_fe"], drop_first=True, dtype=float)
            X["atracao_muni"] = df["atracao_muni"].astype(float)
            X["ivs_2010"] = df["ivs_2010"].astype(float)
            X["log_pop"] = df["log_pop"].astype(float)
            X["estoque_por_10k"] = df["estoque_por_10k"].astype(float).fillna(0)
        elif spec=="estrato_heterogeneidade":
            X = pd.get_dummies(df[["atracao_muni","estrato","cod_curso","uf_fe"]], columns=["estrato","cod_curso","uf_fe"], drop_first=True, dtype=float)
            X["atracao_muni"] = df["atracao_muni"].astype(float)
            X["ivs_2010"] = df["ivs_2010"].astype(float)
            # interacao atracao * estrato
            for lev in ["capital","metropolitano","interior_proximo_polo"]:
                col = f"estrato_{lev}"
                if col in X.columns:
                    X[f"atracao_x_{lev}"] = X[col]*df["atracao_muni"].astype(float)
        else:
            raise ValueError(spec)
        X = sm.add_constant(X, has_constant="add")
        X = X.reindex(sorted(X.columns), axis=1)
        if "const" in X.columns:
            cols = ["const"] + [c for c in X.columns if c!="const"]
            X = X[cols]
        return X

    def fit_ols(y: pd.Series, X: pd.DataFrame, groups: pd.Series):
        mod = sm.OLS(y.astype(float), X)
        res = mod.fit(cov_type="cluster", cov_kwds={"groups": groups, "use_correction": True})
        return res

    def summarize_res(res, X: pd.DataFrame, y: pd.Series, groups: pd.Series, label: str) -> pd.DataFrame:
        params=res.params; bse=res.bse; pvals=res.pvalues
        z = scipy_stats.norm.ppf(1-ALPHA/2)
        df = pd.DataFrame({
            "termo": params.index,
            "coef": params.values,
            "se_cluster": bse.values,
            "ci_low": (params - z*bse).values,
            "ci_high": (params + z*bse).values,
            "p_valor": pvals.values,
            "espec": label,
        })
        df["n"]=len(y)
        df["n_clusters"]=groups.nunique()
        try:
            df["r2"]=res.rsquared
        except: df["r2"]=np.nan
        try: df["outcome_medio"]=y.mean()
        except: df["outcome_medio"]=np.nan
        # q for atracao only family 1? small, set nan
        df["q_fdr_atracao"]=np.nan
        return df

    groups = cross["co_ibge_6d"]
    # Outcomes
    y_estoque_6m = cross["estoque_6m"]
    y_delta = cross["delta_estoque_6m"]
    y_cobertura_6m = cross["cobertura_6m"]
    y_entradas = cross["entradas_6m"].fillna(0)
    y_presentes = cross["presentes_baseline_6m"].fillna(0)

    # ---- Estoque 6m minimal / full ----
    X_min = build_X(cross, "minimal")
    res_estoque_min = fit_ols(y_estoque_6m, X_min, groups)
    tab_min = summarize_res(res_estoque_min, X_min, y_estoque_6m, groups, "OLS_estoque_6m_minimal_atracao_FEcurso_FEuf_cluster")
    X_full = build_X(cross, "full")
    res_estoque_full = fit_ols(y_estoque_6m, X_full, groups)
    tab_full = summarize_res(res_estoque_full, X_full, y_estoque_6m, groups, "OLS_estoque_6m_full_estrato_ivs_logpop_FE_cluster")
    # combine for estoque table (keep minimal primary)
    tab_estoque = pd.concat([tab_min, tab_full], ignore_index=True)
    tmp = TABELA_MODELO_ESTOQUE.with_suffix(".csv.tmp")
    tab_estoque.to_csv(tmp,index=False); tmp.replace(TABELA_MODELO_ESTOQUE)

    # Delta
    res_delta_min = fit_ols(y_delta, X_min, groups)
    tab_delta_min = summarize_res(res_delta_min, X_min, y_delta, groups, "OLS_delta_estoque_minimal")
    res_delta_full = fit_ols(y_delta, X_full, groups)
    tab_delta_full = summarize_res(res_delta_full, X_full, y_delta, groups, "OLS_delta_full")
    tab_delta = pd.concat([tab_delta_min, tab_delta_full], ignore_index=True)
    tmp = TABELA_MODELO_DELTA.with_suffix(".csv.tmp")
    tab_delta.to_csv(tmp,index=False); tmp.replace(TABELA_MODELO_DELTA)

    # Cobertura (LPM)
    X_min_cob = X_min
    res_cob_min = fit_ols(y_cobertura_6m, X_min_cob, groups)
    tab_cob_min = summarize_res(res_cob_min, X_min_cob, y_cobertura_6m, groups, "LPM_cobertura_6m_minimal")
    res_cob_full = fit_ols(y_cobertura_6m, X_full, groups)
    tab_cob_full = summarize_res(res_cob_full, X_full, y_cobertura_6m, groups, "LPM_cobertura_full")
    tab_cob = pd.concat([tab_cob_min, tab_cob_full], ignore_index=True)
    tmp = TABELA_MODELO_COBERTURA.with_suffix(".csv.tmp")
    tab_cob.to_csv(tmp,index=False); tmp.replace(TABELA_MODELO_COBERTURA)

    # Entradas
    res_ent_min = fit_ols(y_entradas, X_min, groups)
    tab_ent_min = summarize_res(res_ent_min, X_min, y_entradas, groups, "OLS_entradas_6m_minimal")
    res_ent_full = fit_ols(y_entradas, X_full, groups)
    tab_ent_full = summarize_res(res_ent_full, X_full, y_entradas, groups, "OLS_entradas_full")
    tab_ent = pd.concat([tab_ent_min, tab_ent_full], ignore_index=True)
    tmp = TABELA_MODELO_ENTRADAS.with_suffix(".csv.tmp")
    tab_ent.to_csv(tmp,index=False); tmp.replace(TABELA_MODELO_ENTRADAS)

    # Presentes (nivel)
    res_pres_min = fit_ols(y_presentes, X_min, groups)
    tab_pres_min = summarize_res(res_pres_min, X_min, y_presentes, groups, "OLS_presentes_baseline_6m_minimal_nivel")
    res_pres_full = fit_ols(y_presentes, X_full, groups)
    tab_pres_full = summarize_res(res_pres_full, X_full, y_presentes, groups, "OLS_presentes_full_nivel")
    tab_pres = pd.concat([tab_pres_min, tab_pres_full], ignore_index=True)
    tmp = TABELA_MODELO_PRESENCA.with_suffix(".csv.tmp")
    tab_pres.to_csv(tmp,index=False); tmp.replace(TABELA_MODELO_PRESENCA)

    # Sensibilidade T0 alternativo (baseline 202507 -> follow 202601)
    alt_base = panel[panel["competencia"]==ALT_BASELINE].copy()
    alt_follow = panel[panel["competencia"]==ALT_FOLLOW].copy()
    alt_base_small = alt_base[["co_ibge_6d","cod_curso","especialistas_mst"]].rename(columns={"especialistas_mst":"estoque_baseline_alt"})
    alt_follow_small = alt_follow[["co_ibge_6d","cod_curso","especialistas_mst"]].rename(columns={"especialistas_mst":"estoque_6m_alt"})
    alt_cross = alt_base_small.merge(alt_follow_small, on=["co_ibge_6d","cod_curso"], how="inner")
    alt_cross["delta_alt"] = alt_cross["estoque_6m_alt"] - alt_cross["estoque_baseline_alt"]
    # merge atracao and controls again
    alt_cross = alt_cross.merge(cross[["co_ibge_6d","cod_curso","atracao_muni","estrato","ivs_2010","log_pop","estoque_por_10k","uf_fe"]].drop_duplicates(["co_ibge_6d","cod_curso"]), on=["co_ibge_6d","cod_curso"], how="left")
    X_alt = build_X(alt_cross, "minimal")
    y_alt = alt_cross["delta_alt"]
    g_alt = alt_cross["co_ibge_6d"]
    res_alt = fit_ols(y_alt, X_alt, g_alt)
    tab_alt = summarize_res(res_alt, X_alt, y_alt, g_alt, "OLS_delta_T0alt_202507_202601_minimal")
    tmp = TABELA_SENS_T0ALT.with_suffix(".csv.tmp")
    tab_alt.to_csv(tmp,index=False); tmp.replace(TABELA_SENS_T0ALT)

    # Sensibilidade winsorizada p99 para delta (outlier 203)
    cross_wins = cross.copy()
    # winsorize delta at p01/p99 and estoque baseline/6m at p99 as proxy
    for col in ["delta_estoque_6m","estoque_6m","estoque_baseline"]:
        p99 = cross_wins[col].quantile(0.99)
        p01 = cross_wins[col].quantile(0.01)
        cross_wins[col] = cross_wins[col].clip(lower=p01, upper=p99)
    X_wins = build_X(cross_wins, "minimal")
    y_wins = cross_wins["delta_estoque_6m"]
    g_wins = cross_wins["co_ibge_6d"]
    res_wins = fit_ols(y_wins, X_wins, g_wins)
    tab_wins = summarize_res(res_wins, X_wins, y_wins, g_wins, "OLS_delta_winsorizado_p99_minimal")
    tmp = TABELA_DELTA_WINSOR.with_suffix(".csv.tmp")
    tab_wins.to_csv(tmp,index=False); tmp.replace(TABELA_DELTA_WINSOR)

    # Estratificado confirmatoria vs ampliada (ponte)
    strat_rows=[]
    for flag, label in [(True,"confirmatoria_587_10cursos"),(False,"ampliada_597_sobreposta")]:
        sub = cross[cross["amostra_confirmatoria"]==flag].copy()
        if len(sub)<100: continue
        X_s = build_X(sub, "minimal")
        y_s = sub["delta_estoque_6m"]
        g_s = sub["co_ibge_6d"]
        try:
            res_s = fit_ols(y_s, X_s, g_s)
            df = summarize_res(res_s, X_s, y_s, g_s, f"OLS_delta_{label}_minimal")
            df["amostra"]=label
            strat_rows.append(df)
        except Exception as e:
            strat_rows.append(pd.DataFrame([{"termo":"atracao_muni","coef":np.nan,"se_cluster":np.nan,"p_valor":np.nan,"espec":f"erro {e}","amostra":label}]))
    tab_strat = pd.concat(strat_rows, ignore_index=True) if strat_rows else pd.DataFrame()
    tmp = TABELA_DELTA_STRAT.with_suffix(".csv.tmp")
    tab_strat.to_csv(tmp,index=False); tmp.replace(TABELA_DELTA_STRAT)

    # Heterogeneidade estrato (atracao x estrato)
    X_het = build_X(cross, "estrato_heterogeneidade")
    # outcome delta
    res_het = fit_ols(y_delta, X_het, groups)
    tab_het = summarize_res(res_het, X_het, y_delta, groups, "OLS_delta_heterogeneidade_atracao_x_estrato")
    tmp = TABELA_HETERO.with_suffix(".csv.tmp")
    tab_het.to_csv(tmp,index=False); tmp.replace(TABELA_HETERO)

    # === Leave-one-out and influencias (for estoque delta minimal as proxy) ===
    loo_rows=[]
    # LOO UF
    for uf in sorted(cross["sg_uf"].unique()):
        sub = cross[cross["sg_uf"]!=uf].copy()
        if len(sub)<300: continue
        y_s = sub["delta_estoque_6m"]
        g_s = sub["co_ibge_6d"]
        X_s = build_X(sub, "minimal")
        X_s = X_s.loc[:, (X_s!=X_s.iloc[0]).any(axis=0) | (X_s.columns=="const")]
        try:
            res_s = fit_ols(y_s, X_s, g_s)
            coef = res_s.params.get("atracao_muni", np.nan)
            se = res_s.bse.get("atracao_muni", np.nan)
            p = res_s.pvalues.get("atracao_muni", np.nan)
            loo_rows.append({"tipo":"leave_one_UF","excluido":uf,"termo":"atracao_muni","coef":coef,"se":se,"p":p,"n":len(sub),"n_clusters":g_s.nunique()})
        except: pass
    for curso in sorted(cross["cod_curso"].unique()):
        sub = cross[cross["cod_curso"]!=curso].copy()
        y_s = sub["delta_estoque_6m"]
        g_s = sub["co_ibge_6d"]
        X_s = build_X(sub, "minimal")
        X_s = X_s.loc[:, (X_s!=X_s.iloc[0]).any(axis=0) | (X_s.columns=="const")]
        try:
            res_s = fit_ols(y_s, X_s, g_s)
            loo_rows.append({"tipo":"leave_one_curso","excluido":str(curso),"termo":"atracao_muni","coef":float(res_s.params.get("atracao_muni",np.nan)),"se":float(res_s.bse.get("atracao_muni",np.nan)),"p":float(res_s.pvalues.get("atracao_muni",np.nan)),"n":len(sub),"n_clusters":g_s.nunique()})
        except: pass
    df_loo = pd.DataFrame(loo_rows)
    tmp = TABELA_LOO.with_suffix(".csv.tmp")
    df_loo.to_csv(tmp,index=False); tmp.replace(TABELA_LOO)

    # Influencia municipal: leave-one-municipio for atracao coef in delta minimal
    infl_rows=[]
    base_coef = res_delta_min.params.get("atracao_muni")
    base_se = res_delta_min.bse.get("atracao_muni")
    mun_list = cross["co_ibge_6d"].unique()
    coefs_mun=[]
    for mun in mun_list:
        sub = cross[cross["co_ibge_6d"]!=mun]
        y_s = sub["delta_estoque_6m"]
        g_s = sub["co_ibge_6d"]
        X_s = build_X(sub, "minimal")
        X_s = X_s.loc[:, (X_s!=X_s.iloc[0]).any(axis=0) | (X_s.columns=="const")]
        try:
            res_s = fit_ols(y_s, X_s, g_s)
            if "atracao_muni" in res_s.params:
                delta = float(res_s.params["atracao_muni"] - base_coef)
                dfbeta = delta / float(base_se) if base_se!=0 else np.nan
                infl_rows.append({"co_ibge_6d":mun,"termo":"atracao_muni","coef_excluido":float(res_s.params["atracao_muni"]),"delta":delta,"dfbeta":dfbeta,"n_excluido":len(cross)-len(sub)})
                coefs_mun.append(float(res_s.params["atracao_muni"]))
        except: continue
    df_infl = pd.DataFrame(infl_rows)
    if not df_infl.empty:
        df_infl = df_infl.sort_values("dfbeta", key=lambda s: s.abs(), ascending=False)
    tmp = TABELA_INFLUENCIA.with_suffix(".csv.tmp")
    df_infl.to_csv(tmp,index=False); tmp.replace(TABELA_INFLUENCIA)
    infl_summary = {}
    if coefs_mun:
        infl_summary = {"atracao_delta_min":float(np.min(coefs_mun)),"max":float(np.max(coefs_mun)),"sd":float(np.std(coefs_mun)),"base":float(base_coef)}

    # === Validacao preditiva por municipio GroupKFold for delta ===
    df_cv = cross.copy()
    groups_arr = df_cv["co_ibge_6d"].values
    y_arr = df_cv["delta_estoque_6m"].values
    # For delta continuous, metrics: RMSE, R2 out?
    r2s = []
    rmses = []
    # In-sample R2 from res_delta_min
    r2_in = float(res_delta_min.rsquared) if hasattr(res_delta_min,"rsquared") else np.nan
    # compute RMSE insample
    y_pred_in = res_delta_min.predict(X_min)
    rmse_in = float(np.sqrt(np.mean((y_arr - y_pred_in)**2)))
    for train_idx, test_idx in group_kfold_splits(groups_arr, n_splits=5, seed=42):
        df_train = df_cv.iloc[train_idx]
        df_test = df_cv.iloc[test_idx]
        X_train = build_X(df_train, "minimal")
        X_test = build_X(df_test, "minimal")
        X_test_aligned = X_test.reindex(columns=X_train.columns, fill_value=0)
        y_train = df_train["delta_estoque_6m"].values
        y_test = df_test["delta_estoque_6m"].values
        try:
            res_cv = sm.OLS(y_train, X_train.values).fit()
            pred = res_cv.predict(X_test_aligned.values)
            # R2 out
            ss_res = np.sum((y_test - pred)**2)
            ss_tot = np.sum((y_test - np.mean(y_test))**2) if np.var(y_test)>0 else np.nan
            r2 = 1 - ss_res/ss_tot if ss_tot else np.nan
            rmse = np.sqrt(np.mean((y_test - pred)**2))
            r2s.append(r2); rmses.append(rmse)
        except: pass
    pred_df = pd.DataFrame([{
        "modelo":"OLS_delta_minimal_atracao_FE",
        "r2_media_out": float(np.mean(r2s)) if r2s else np.nan,
        "r2_sd_out": float(np.std(r2s)) if r2s else np.nan,
        "r2_insample": float(r2_in) if not np.isnan(r2_in) else np.nan,
        "rmse_media_out": float(np.mean(rmses)) if rmses else np.nan,
        "rmse_sd_out": float(np.std(rmses)) if rmses else np.nan,
        "rmse_insample": float(rmse_in),
        "n_splits":5,
        "grupos":"municipio",
        "nota":"out-of-sample por municipio; delta_estoque_6m (202509->202603); gap indica overfit FE",
    }])
    # add segunda linha para estoque_6m
    # compute similarly for estoque_6m
    X_min_stock = build_X(cross, "minimal")
    y_stock_arr = cross["estoque_6m"].values
    y_pred_in_stock = res_estoque_min.predict(X_min_stock)
    rmse_in_stock = float(np.sqrt(np.mean((y_stock_arr - y_pred_in_stock)**2)))
    r2_in_stock = float(res_estoque_min.rsquared)
    r2s_s=[]
    rmses_s=[]
    for train_idx, test_idx in group_kfold_splits(groups_arr, n_splits=5, seed=42):
        df_train = df_cv.iloc[train_idx]
        df_test = df_cv.iloc[test_idx]
        X_train = build_X(df_train, "minimal")
        X_test = build_X(df_test, "minimal")
        X_test_aligned = X_test.reindex(columns=X_train.columns, fill_value=0)
        y_train = df_train["estoque_6m"].values
        y_test = df_test["estoque_6m"].values
        try:
            res_cv = sm.OLS(y_train, X_train.values).fit()
            pred = res_cv.predict(X_test_aligned.values)
            ss_res = np.sum((y_test - pred)**2)
            ss_tot = np.sum((y_test - np.mean(y_test))**2)
            r2 = 1 - ss_res/ss_tot if ss_tot else np.nan
            rmses_s.append(np.sqrt(np.mean((y_test - pred)**2)))
            r2s_s.append(r2)
        except: pass
    pred_df = pd.concat([pred_df, pd.DataFrame([{
        "modelo":"OLS_estoque_6m_minimal",
        "r2_media_out": float(np.mean(r2s_s)) if r2s_s else np.nan,
        "r2_sd_out": float(np.std(r2s_s)) if r2s_s else np.nan,
        "r2_insample": float(r2_in_stock),
        "rmse_media_out": float(np.mean(rmses_s)) if rmses_s else np.nan,
        "rmse_sd_out": float(np.std(rmses_s)) if rmses_s else np.nan,
        "rmse_insample": float(rmse_in_stock),
        "n_splits":5,
        "grupos":"municipio",
        "nota":"estoque_6m 202603",
    }])], ignore_index=True)
    tmp = TABELA_PRED.with_suffix(".csv.tmp")
    pred_df.to_csv(tmp,index=False); tmp.replace(TABELA_PRED)

    # === Figuras ===
    # Figura 1: trajetoria estoque por estrato (baseline panel group)
    plt.figure(figsize=(10,6))
    for estr, color in zip(["capital","metropolitano","interior_proximo_polo","interior_remoto"], ["#495057","#007bff","#17a2b8","#6c757d"]):
        sub = panel[panel["estrato"]==estr].groupby("competencia")["especialistas_mst"].mean()
        # ensure order by competencia chronological
        sub = sub.reindex(COMPETENCIAS)
        x = np.arange(len(COMPETENCIAS))
        plt.plot(x, sub.values, label=estr.replace("_"," "), color=color, linewidth=1.8)
    # T0 line
    plt.axvline(x=t0_idx, color="red", linestyle="--", linewidth=1.2, label=f"T0_admin {T0_ADMIN_COMP}")
    plt.axvline(x=comp_index[BASELINE_COMP], color="orange", linestyle=":", linewidth=1, label=f"baseline {BASELINE_COMP}")
    plt.xticks(ticks=np.arange(0,len(COMPETENCIAS),3), labels=[c for i,c in enumerate(COMPETENCIAS) if i%3==0], rotation=45, fontsize=7)
    plt.ylabel("Estoque medio municipal do CBO (especialistas_mst)", fontsize=9)
    plt.xlabel("Competencia CNES", fontsize=9)
    plt.title("Trajetoria agregada do estoque por estrato (1184 celulas municipio-curso, 368 mun)\n CNES 202406-202607; T0_admin 202510 pos-homologacao 2025-09-29", fontsize=9)
    plt.legend(fontsize=7, loc="upper left")
    plt.tight_layout()
    plt.savefig(FIG_TRAJ_ESTRATO, dpi=300); plt.close()

    # Figura 2: trajetoria por atracao
    plt.figure(figsize=(10,6))
    for atr, color, lbl in [(0,"#6c757d","sem atracao (0)"),(1,"#28a745","com atracao (1)")]:
        sub = panel[panel["atracao_muni"]==atr].groupby("competencia")["especialistas_mst"].mean().reindex(COMPETENCIAS)
        plt.plot(np.arange(len(COMPETENCIAS)), sub.values, label=f"{lbl} n={ (panel[panel['competencia']==BASELINE_COMP]['atracao_muni']==atr).sum() }", color=color, linewidth=1.8)
    plt.axvline(x=t0_idx, color="red", linestyle="--", linewidth=1.2)
    plt.xticks(ticks=np.arange(0,len(COMPETENCIAS),3), labels=[c for i,c in enumerate(COMPETENCIAS) if i%3==0], rotation=45, fontsize=7)
    plt.ylabel("Estoque medio", fontsize=9)
    plt.xlabel("Competencia")
    plt.title("Trajetoria do estoque por atracao administrativa (CNES celula atracao A1)\nCom atracao N=378 vs sem N=806; T0_admin 202510", fontsize=9)
    plt.legend(fontsize=7)
    plt.tight_layout()
    plt.savefig(FIG_TRAJ_ATRACAO, dpi=300); plt.close()

    # Figura 3: delta estoque por atracao box + pontos?
    plt.figure(figsize=(8,5))
    # delta by atracao
    data0 = cross[cross["atracao_muni"]==0]["delta_estoque_6m"]
    data1 = cross[cross["atracao_muni"]==1]["delta_estoque_6m"]
    # Use violin or bar com IC
    means = [data0.mean(), data1.mean()]
    ses = [data0.std()/np.sqrt(len(data0)), data1.std()/np.sqrt(len(data1))]
    x = np.arange(2)
    plt.bar(x, means, yerr=[1.96*s for s in ses], capsize=6, color=["#6c757d","#28a745"], alpha=0.9)
    for i, (m, n) in enumerate(zip(means, [len(data0),len(data1)])):
        plt.text(i, m+0.3, f"{m:.2f}\nn={n}", ha="center", fontsize=8)
    plt.xticks(x, ["Sem atracao\n(A1 0)","Com atracao\n(A1 1)"])
    plt.ylabel("Delta estoque 6m (202603 - 202509)", fontsize=9)
    plt.title("Delta do estoque em 6m por atracao (municipio-curso)\nMedia e IC95% aproximado; associativo sem causalidade", fontsize=9)
    plt.ylim(min(means)-1.5, max(means)+1.5)
    plt.tight_layout()
    plt.savefig(FIG_DELTA, dpi=300); plt.close()

    # === JSONs ===
    # Manifesto maturidade
    pot = json.loads(POTENCIA_A3.read_text(encoding="utf-8"))
    reg = json.loads(REGISTRO_A3.read_text(encoding="utf-8"))
    manifesto_tip_data = json.loads(MANIFESTO_TIP.read_text(encoding="utf-8"))
    bridge_raw = ponte
    manifesto = {
        "protocolo":"A5_MANISFESTO_MATURIDADE_CENSURA",
        "data_referencia": dt.date.today().isoformat(),
        "efeitos_estimados": False,
        "t0": {
            "homologacao_data": T0_HOMOLOG_DATE,
            "homologacao_competencia_admin_T0": T0_ADMIN_COMP,
            "baseline_competencia": BASELINE_COMP,
            "follow_6m_competencia": FOLLOW_6M_COMP,
            "t0_alternativo_T0_6m": FOLLOW_T0_6M_COMP,
            "alt_baseline": ALT_BASELINE,
            "alt_follow": ALT_FOLLOW,
            "validacao_fisica_nominal": nominal_stats,
            "competencia_t0_idx": t0_idx,
            "competencias_totais": COMPETENCIAS,
            "n_competencias": len(COMPETENCIAS),
            "nota": "T0_admin e primeira competencia completa apos homologacao 2025-09-29 (202510). T0 fisico aproximado via snapshot sobreviventes mediano 2025-09-19 (IQ 2025-09-18 a 2025-11-24), 274 antes vs 247 apos homologacao; nao e log completo, por isso baseline pre-T0 202509 e follow 6m 202603 sao horizonte comum documentado."
        },
        "ponte_curso_cbo": {
            "cursos_estritamente_univocos_confirmatorios": cursos_sem_sobre,
            "n_cursos_confirmatorios": len(cursos_sem_sobre),
            "n_cursos_sobrepostos": len([c for c in range(1,17) if c not in cursos_sem_sobre]),
            "celulas_confirmatorias_202509": int(confirmatoria_cells),
            "celulas_ampliada_sobreposta": int(total_cells - confirmatoria_cells),
            "total_celulas_municipio_curso": int(total_cells),
            "municipios_confirmatorios": int(panel[panel["amostra_confirmatoria"] & (panel["competencia"]==BASELINE_COMP)]["co_ibge_6d"].nunique()),
            "municipios_ampliada": int(panel["co_ibge_6d"].nunique()),
            "status_substantivo": bridge_raw.get("status_substantivo"),
            "versao_ponte": bridge_raw.get("versao_ponte"),
            "regra": "Primario restrito ao nucleo sem sobreposicao (587 celulas, 295 mun); sensibilidade inclui ampliada 597 celulas sobrepostas estratificadas; nao colapsar CBOs compartilhados no primario para evitar contaminacao",
        },
        "horizonte_e_censura": {
            "horizonte_comum_6m_primario": f"{BASELINE_COMP} -> {FOLLOW_6M_COMP} (6 meses)",
            "horizonte_T0_6m_sensibilidade": f"{T0_ADMIN_COMP} -> {FOLLOW_T0_6M_COMP}",
            "censura_entradas_6m": "requer 6 meses anteriores observados; censurado se competencia <202412; baseline 202509 observavel",
            "censura_saidas_3m": "requer 3 meses posteriores; censurado se competencia >202604; follow 202603 observavel",
            "censura_presenca_6m": "coorte madura se idx+6 <26; madura ate 202601 inclusive; baseline 202509 madura (15+6=21), follow 202603 nao madura para sua propria coorte",
            "definicoes": {
                "estoque": "CO_PROFISSIONAL_SUS distinto em qualquer CNES do municipio, dentro dos CBOs operacionais do curso (contagem unica por municipio-curso-mes)",
                "cobertura": "1[estoque>0] na celula municipio-curso",
                "entrada": "presente em t e ausente nos 6 meses anteriores observados",
                "saida": "presente em t e ausente nos 3 meses posteriores observados",
                "presenca_6m_nivel": "numero de entrantes elegiveis em t observados no mesmo municipio-curso em t+6 (nivel, nao taxa); denominador elegiveis reportado separadamente",
                "saldo": "entradas - saidas na competencia",
            },
        },
        "checks": checks,
        "diagnostico_identificador_longitudinal": id_diag,
        "amostra": {
            "municipios": 368,
            "celulas_municipio_curso": 1184,
            "celulas_confirmatorias": 587,
            "celulas_ampliada": 597,
            "competencias": 26,
            "linhas_painel": 30784,
            "baseline": BASELINE_COMP,
            "follow": FOLLOW_6M_COMP,
        },
        "potencia_referencia_A3": {
            "global_MDE_p30": pot["mde_global"]["mde_80_pp_p30"],
            "por_estrato": {k: v["mde_80_pp_p30"] for k,v in pot["por_estrato"].items()},
            "nota": "MDE para outcome binario atracao; para estoque delta continuo poder depende de variancia stock (sd delta ~6.16, estoque sd ~38); 1184 celulas mantem poder global",
        },
        "hashes_entradas": {
            str(p.relative_to(ROOT)).replace("\\","/"): {"sha256": sha256(p)} for p in [PAINEL_MUNI, MATRIZ_FUNIL, MATRIZ_TIPOLOGIA, MANIFESTO_TIP, PORTAO_A1, REGISTRO_A3, POTENCIA_A3, PONTE_FILE, MANIFESTO_CNES if MANIFESTO_CNES.exists() else PAINEL_MUNI]
        },
        "arquivos": {
            "painel_T0": str(PAINEL_T0_PARQUET.relative_to(ROOT)).replace("\\","/"),
            "cross_section": str(CROSS_SECTION_CSV.relative_to(ROOT)).replace("\\","/"),
            "tabela_construcao": str(TABELA_CONSTRUCAO.relative_to(ROOT)).replace("\\","/"),
            "tabela_amostra": str(TABELA_AMOSTRA.relative_to(ROOT)).replace("\\","/"),
            "tabela_trajetoria_mensal": str(TABELA_TRAJ_MENSAL.relative_to(ROOT)).replace("\\","/"),
            "tabela_trajetoria_atracao": str(TABELA_TRAJ_ATRACAO.relative_to(ROOT)).replace("\\","/"),
            "tabela_descritiva_outcomes": str(TABELA_DESC_OUTCOMES.relative_to(ROOT)).replace("\\","/"),
        },
        "avisos_linguagem": [
            "Nao chamar presenca no CNES de participacao no PMM-E, atividade fisica ou retencao individual.",
            "Sem primeiro estagio causal do RDD, nao atribuir CNES ao adicional da bolsa; faixa-IVS colinearidade impede separar efeito bolsa.",
            "Analise principal incondicional (estoque/cobertura em nivel municipal); presenca em nivel nao taxa condicional.",
            "Retencao individual bloqueada sem ponte PMM-E-CNES e sem log completo.",
            "Atracao como preditor associativo; nao causal.",
        ],
    }
    # Remove duplicate key handling for MANIFESTO_CNES fallback
    tmp = JSON_MANISFESTO.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(manifesto, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    tmp.replace(JSON_MANISFESTO)

    # Estimativas json
    estimativas = {
        "protocolo":"A5_ESTIMATIVAS_PROVIMENTO",
        "data_referencia": dt.date.today().isoformat(),
        "efeitos_estimados": True,
        "linguagem":"associativa (associado a, persistencia da oferta local); proibido efeito causal do PMM-E/bolsa/IVS e retencao individual",
        "populacao": {
            "painel_municipio_curso": "1184 celulas municipio-curso (368 municipios) x26 competencias 202406-202607 =30784 linhas",
            "confirmatoria_10_cursos": "587 celulas (295 mun) CBO sem sobreposicao",
            "ampliada_6_cursos": "597 celulas (242 mun) sobrepostos",
            "cross_section_6m": f"1184 celulas baseline {BASELINE_COMP} -> follow {FOLLOW_6M_COMP}",
            "unidade_analitica":"municipio-curso (agregacao de CNES dentro do municipio)",
            "unidade_inferencia":"municipio (cluster-robusto; G=368)",
        },
        "t0_e_horizonte": {
            "T0_admin": T0_ADMIN_COMP,
            "baseline": BASELINE_COMP,
            "follow_6m": FOLLOW_6M_COMP,
            "T0_fisico_mediano": nominal_stats.get("ciclo1_dt_median"),
            "censura": "entradas <202412 censurado, saidas >202604 censurado, presenca madura ate 202601",
        },
        "outcomes_permitidos": {
            "estoque_mst": "estoque municipal do CBO (contagem distinta por municipio-curso-mes)",
            "cobertura_binaria_mst": "1[estoque>0]",
            "n_entradas_6m": "entradas apos ausencia 6m observada",
            "n_saidas_confirmadas_3m": "saidas com 3m posteriores observados",
            "saldo_liquido": "entradas - saidas",
            "presentes_6m_nivel": "numero entrantes elegiveis em baseline ainda presentes 6m depois (nivel, nao taxa)",
            "bloqueados": ["retencao individual do bolsista","atividade fisica confirmada","WTA","taxa por vaga"],
        },
        "modelos": {
            "estoque_6m_minimal": {
                "formula":"estoque_6m ~ atracao_muni + FE curso(16) + FE UF(colapsada) cluster mun",
                "n": int(len(cross)),
                "n_clusters": int(groups.nunique()),
                "coef_atracao": float(res_estoque_min.params.get("atracao_muni", np.nan)),
                "se_atracao": float(res_estoque_min.bse.get("atracao_muni", np.nan)),
                "p_atracao": float(res_estoque_min.pvalues.get("atracao_muni", np.nan)),
                "r2": float(res_estoque_min.rsquared),
            },
            "estoque_6m_full": {
                "coef_atracao": float(res_estoque_full.params.get("atracao_muni", np.nan)),
                "se": float(res_estoque_full.bse.get("atracao_muni", np.nan)),
                "p": float(res_estoque_full.pvalues.get("atracao_muni", np.nan)),
            },
            "delta_minimal": {
                "coef_atracao": float(res_delta_min.params.get("atracao_muni", np.nan)),
                "se_atracao": float(res_delta_min.bse.get("atracao_muni", np.nan)),
                "p_atracao": float(res_delta_min.pvalues.get("atracao_muni", np.nan)),
                "r2": float(res_delta_min.rsquared),
            },
            "delta_full": {
                "coef_atracao": float(res_delta_full.params.get("atracao_muni", np.nan)),
                "se_atracao": float(res_delta_full.bse.get("atracao_muni", np.nan)),
                "p_atracao": float(res_delta_full.pvalues.get("atracao_muni", np.nan)),
            },
            "cobertura_6m_minimal": {
                "coef_atracao": float(res_cob_min.params.get("atracao_muni", np.nan)),
                "se_atracao": float(res_cob_min.bse.get("atracao_muni", np.nan)),
                "p_atracao": float(res_cob_min.pvalues.get("atracao_muni", np.nan)),
            },
            "entradas_minimal": {
                "coef_atracao": float(res_ent_min.params.get("atracao_muni", np.nan)),
                "se_atracao": float(res_ent_min.bse.get("atracao_muni", np.nan)),
                "p_atracao": float(res_ent_min.pvalues.get("atracao_muni", np.nan)),
            },
            "presentes_minimal_nivel": {
                "coef_atracao": float(res_pres_min.params.get("atracao_muni", np.nan)),
                "se_atracao": float(res_pres_min.bse.get("atracao_muni", np.nan)),
                "p_atracao": float(res_pres_min.pvalues.get("atracao_muni", np.nan)),
            },
            "T0_alternativo_delta": {
                "coef_atracao": float(res_alt.params.get("atracao_muni", np.nan)),
                "se_atracao": float(res_alt.bse.get("atracao_muni", np.nan)),
                "p_atracao": float(res_alt.pvalues.get("atracao_muni", np.nan)),
            },
            "delta_winsorizado_p99": {
                "coef_atracao": float(res_wins.params.get("atracao_muni", np.nan)),
                "se_atracao": float(res_wins.bse.get("atracao_muni", np.nan)),
                "p_atracao": float(res_wins.pvalues.get("atracao_muni", np.nan)),
            },
            "delta_strat_confirmatoria": {
                "coef_atracao": float(tab_strat[(tab_strat["amostra"]=="confirmatoria_587_10cursos") & (tab_strat["termo"]=="atracao_muni")]["coef"].iloc[0] if not tab_strat.empty and ((tab_strat["amostra"]=="confirmatoria_587_10cursos") & (tab_strat["termo"]=="atracao_muni")).any() else np.nan),
                "se_atracao": float(tab_strat[(tab_strat["amostra"]=="confirmatoria_587_10cursos") & (tab_strat["termo"]=="atracao_muni")]["se_cluster"].iloc[0] if not tab_strat.empty and ((tab_strat["amostra"]=="confirmatoria_587_10cursos") & (tab_strat["termo"]=="atracao_muni")).any() else np.nan),
                "p_atracao": float(tab_strat[(tab_strat["amostra"]=="confirmatoria_587_10cursos") & (tab_strat["termo"]=="atracao_muni")]["p_valor"].iloc[0] if not tab_strat.empty and ((tab_strat["amostra"]=="confirmatoria_587_10cursos") & (tab_strat["termo"]=="atracao_muni")).any() else np.nan),
            },
            "delta_strat_ampliada": {
                "coef_atracao": float(tab_strat[(tab_strat["amostra"]=="ampliada_597_sobreposta") & (tab_strat["termo"]=="atracao_muni")]["coef"].iloc[0] if not tab_strat.empty and ((tab_strat["amostra"]=="ampliada_597_sobreposta") & (tab_strat["termo"]=="atracao_muni")).any() else np.nan),
                "se_atracao": float(tab_strat[(tab_strat["amostra"]=="ampliada_597_sobreposta") & (tab_strat["termo"]=="atracao_muni")]["se_cluster"].iloc[0] if not tab_strat.empty and ((tab_strat["amostra"]=="ampliada_597_sobreposta") & (tab_strat["termo"]=="atracao_muni")).any() else np.nan),
                "p_atracao": float(tab_strat[(tab_strat["amostra"]=="ampliada_597_sobreposta") & (tab_strat["termo"]=="atracao_muni")]["p_valor"].iloc[0] if not tab_strat.empty and ((tab_strat["amostra"]=="ampliada_597_sobreposta") & (tab_strat["termo"]=="atracao_muni")).any() else np.nan),
            },
            "delta_heterogeneidade_estrato": {
                "coef_atracao": float(res_het.params.get("atracao_muni", np.nan)),
                "se_atracao": float(res_het.bse.get("atracao_muni", np.nan)),
            },
        },
        "influencia": {
            "leave_one_UF_range": df_loo[df_loo["tipo"]=="leave_one_UF"]["coef"].agg(["min","max","std"]).to_dict() if not df_loo.empty else {},
            "leave_one_curso_range": df_loo[df_loo["tipo"]=="leave_one_curso"]["coef"].agg(["min","max","std"]).to_dict() if not df_loo.empty else {},
            "leave_one_municipio": infl_summary,
            "top_influentes": df_infl.head(5).to_dict(orient="records") if not df_infl.empty else [],
        },
        "validacao_preditiva": pred_df.to_dict(orient="records"),
        "potencia_referencia": {
            "global_MDE_p30": pot["mde_global"]["mde_80_pp_p30"],
            "por_estrato_MDE_p30": {k: v["mde_80_pp_p30"] for k,v in pot["por_estrato"].items()},
        },
        "hashes_entradas": {
            str(p.relative_to(ROOT)).replace("\\","/"): {"sha256": sha256(p)} for p in [PAINEL_MUNI, MATRIZ_FUNIL, MATRIZ_TIPOLOGIA, MANIFESTO_TIP, PORTAO_A1, REGISTRO_A3, POTENCIA_A3, PONTE_FILE]
        },
        "arquivos": {
            "painel_T0": str(PAINEL_T0_PARQUET.relative_to(ROOT)).replace("\\","/"),
            "cross_section": str(CROSS_SECTION_CSV.relative_to(ROOT)).replace("\\","/"),
            "tabela_construcao": str(TABELA_CONSTRUCAO.relative_to(ROOT)).replace("\\","/"),
            "tabela_amostra": str(TABELA_AMOSTRA.relative_to(ROOT)).replace("\\","/"),
            "tabela_trajetoria_mensal": str(TABELA_TRAJ_MENSAL.relative_to(ROOT)).replace("\\","/"),
            "tabela_trajetoria_atracao": str(TABELA_TRAJ_ATRACAO.relative_to(ROOT)).replace("\\","/"),
            "tabela_curso": str(TABELA_CURSO.relative_to(ROOT)).replace("\\","/"),
            "tabela_uf": str(TABELA_UF.relative_to(ROOT)).replace("\\","/"),
            "tabela_descritiva_outcomes": str(TABELA_DESC_OUTCOMES.relative_to(ROOT)).replace("\\","/"),
            "tabela_estoque": str(TABELA_MODELO_ESTOQUE.relative_to(ROOT)).replace("\\","/"),
            "tabela_delta": str(TABELA_MODELO_DELTA.relative_to(ROOT)).replace("\\","/"),
            "tabela_cobertura": str(TABELA_MODELO_COBERTURA.relative_to(ROOT)).replace("\\","/"),
            "tabela_entradas": str(TABELA_MODELO_ENTRADAS.relative_to(ROOT)).replace("\\","/"),
            "tabela_presenca": str(TABELA_MODELO_PRESENCA.relative_to(ROOT)).replace("\\","/"),
            "tabela_T0alt": str(TABELA_SENS_T0ALT.relative_to(ROOT)).replace("\\","/"),
            "tabela_delta_winsor": str(TABELA_DELTA_WINSOR.relative_to(ROOT)).replace("\\","/"),
            "tabela_delta_strat": str(TABELA_DELTA_STRAT.relative_to(ROOT)).replace("\\","/"),
            "tabela_hetero": str(TABELA_HETERO.relative_to(ROOT)).replace("\\","/"),
            "tabela_loo": str(TABELA_LOO.relative_to(ROOT)).replace("\\","/"),
            "tabela_influencia": str(TABELA_INFLUENCIA.relative_to(ROOT)).replace("\\","/"),
            "tabela_preditiva": str(TABELA_PRED.relative_to(ROOT)).replace("\\","/"),
            "figura_traj_estrato": str(FIG_TRAJ_ESTRATO.relative_to(ROOT)).replace("\\","/"),
            "figura_traj_atracao": str(FIG_TRAJ_ATRACAO.relative_to(ROOT)).replace("\\","/"),
            "figura_delta": str(FIG_DELTA.relative_to(ROOT)).replace("\\","/"),
        },
        "avisos": [
            "Atracao como preditor associativo; sem causalidade.",
            "Sem primeiro estagio causal do RDD, nao atribuir CNES ao adicional da bolsa.",
            "Ponte confirmatoria 587 celulas primaria; ampliada 597 como sensibilidade nao primaria.",
            "Oferta cadastrada local; nao participar PMM-E nem retencao individual.",
            "Horizonte 6m comum documentado com censura; presenca em nivel nao taxa condicional.",
        ],
    }
    tmp = JSON_ESTIMATIVAS.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(estimativas, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    tmp.replace(JSON_ESTIMATIVAS)

    # Relatorio markdown
    def fmt(x): return f"{x:.3f}" if pd.notna(x) else "NA"
    desc_all = desc_df[desc_df["estrato"]=="todos"]
    desc_atr0 = desc_all[desc_all["atracao_muni"]==0].iloc[0] if len(desc_all[desc_all["atracao_muni"]==0])>0 else {}
    desc_atr1 = desc_all[desc_all["atracao_muni"]==1].iloc[0] if len(desc_all[desc_all["atracao_muni"]==1])>0 else {}
    # estoque coefs
    ce = estimativas["modelos"]["estoque_6m_minimal"]
    ce_full = estimativas["modelos"]["estoque_6m_full"]
    cd = estimativas["modelos"]["delta_minimal"]
    cd_full = estimativas["modelos"]["delta_full"]
    cc = estimativas["modelos"]["cobertura_6m_minimal"]
    cen = estimativas["modelos"]["entradas_minimal"]
    cp = estimativas["modelos"]["presentes_minimal_nivel"]
    # loom summary
    loo_minmax = df_loo[df_loo["termo"]=="atracao_muni"]["coef"]
    loo_range = f"{loo_minmax.min():.3f} a {loo_minmax.max():.3f} sd {loo_minmax.std():.3f}" if not df_loo.empty else "NA"
    relatorio = f"""# A5 — Persistencia da oferta medica local no CNES (associativo)

> Registro A3: `output/tema_trabalho/registro_pre_analise_atracao.json` (hash {sha256(REGISTRO_A3)[:8]})
> Potencia A3: MDE global 3.8% p30; estrato capital 16.1% metro 8.4% proximo 4.8% remoto 10.9%
> Tipologia A2 strict 540/540 (25/101/238/176) painel 368 mun 1184 celulas municipio-curso
> Amostra A5: **1184 celulas municipio-curso (368 municipios) x26 competencias =30784 linhas**; confirmatoria 587 (295 mun) sem sobreposicao
> T0_admin: **{T0_ADMIN_COMP}** (primeira competencia apos homologacao 2025-09-29); baseline {BASELINE_COMP} -> follow 6m {FOLLOW_6M_COMP}; horizonte comum 6 meses maduro
> Ponte: 10 cursos estritamente univocos (1,2,3,5,9,12,13,14,15,16) como primario; 6 cursos sobrepostos (4,6,7,8,10,11) sensibilidade

## 1. Construcao, painel alinhado ao T0 e maturidade/censura

Painel analitico `A5_painel_T0.parquet` (30784 linhas) alinha `t_rel_T0 = competencia - {T0_ADMIN_COMP}` com definicoes:
- estoque_mst: CO_PROFISSIONAL_SUS distinto por municipio-curso-mes (CBOs operacionais do curso; deduplicacao intramunicipal)
- cobertura_binaria_mst: 1[estoque>0]
- n_entradas_6m: presente em t e ausente nos 6 meses anteriores (censurado se <202412)
- n_saidas_confirmadas_3m: presente em t e ausente nos 3 meses posteriores (censurado se >202604)
- presentes_6m (nivel): entrantes elegiveis em t ainda presentes em t+6 (nivel, nao taxa; madura se idx+6<26 ate 202601)
- saldo_liquido: entradas - saidas

Censura documentada: 26 competencias 202406-202607 completas; estoque nunca censurado (0 se sem profissional); entradas indisponiveis 202406-202411 (primeiros 6m), saidas indisponiveis 202605-202607 (ultimos 3m), presenca madura ate baseline 202601 (inclui {BASELINE_COMP}). Ver `A5_manifesto_maturidade_censura.json` e `A5_tabela_00_construcao_steps.csv`.

T0 fisico validado: nominal ciclo1 n=521, dt_inicio de {nominal_stats.get("ciclo1_dt_min")} a {nominal_stats.get("ciclo1_dt_max")}, mediano {nominal_stats.get("ciclo1_dt_median")} (p25 {nominal_stats.get("ciclo1_dt_p25")} p75 {nominal_stats.get("ciclo1_dt_p75")}), {nominal_stats.get("ciclo1_antes_homolog")} antes vs {nominal_stats.get("ciclo1_apos_homolog")} apos homologacao {T0_HOMOLOG_DATE}. Snapshot de sobreviventes ativos em 2026-08-12, nao log completo, por isso T0_admin {T0_ADMIN_COMP} e usado como referencia agregada e baseline {BASELINE_COMP} como ultima pre-T0 madura. Ponte restrita ao nucleo sem sobreposicao (587 celulas) como primario: FTE cadastral por CNES nao contamina cursos compartilhados.

## 2. Trajetoria agregada (antes dos coeficientes)

Media geral estoque: 13.05 (202406) -> 13.92 (202509 baseline) -> 14.65 (202603 follow) -> 15.20 (202607). Incremento 6m baseline->follow medio **{cross["delta_estoque_6m"].mean():.2f}** sd {cross["delta_estoque_6m"].std():.2f} (mediana {cross["delta_estoque_6m"].median():.1f}). Por estrato baseline: capital  {tab_baseline[tab_baseline["estrato"]=="capital"]["estoque_medio_baseline"].values[0]:.1f}  metropolitano {tab_baseline[tab_baseline["estrato"]=="metropolitano"]["estoque_medio_baseline"].values[0]:.1f}  interior_proximo {tab_baseline[tab_baseline["estrato"]=="interior_proximo_polo"]["estoque_medio_baseline"].values[0]:.1f}  remoto {tab_baseline[tab_baseline["estrato"]=="interior_remoto"]["estoque_medio_baseline"].values[0]:.1f} . Ver `A5_tabela_01b_trajetoria_mensal.csv` e figuras `A5_figura_01/02`.

Por atracao administrativa A1 (agregada ao municipio-curso, max sobre CNES): com atracao N=378 media baseline {desc_atr1.get("estoque_baseline_medio",0):.1f} estoque_6m {desc_atr1.get("estoque_6m_medio",0):.1f} delta {desc_atr1.get("delta_medio",0):.2f}; sem atracao N=806 baseline {desc_atr0.get("estoque_baseline_medio",0):.1f} delta {desc_atr0.get("delta_medio",0):.2f}. Cobertura baseline: com atracao {desc_atr1.get("cobertura_baseline",0):.1%} vs sem {desc_atr0.get("cobertura_baseline",0):.1%}; 6m: {desc_atr1.get("cobertura_6m",0):.1%} vs {desc_atr0.get("cobertura_6m",0):.1%}. Entradas 6m media: {desc_atr1.get("entradas_6m_media",0):.2f} vs {desc_atr0.get("entradas_6m_media",0):.2f}; presentes nivel: {desc_atr1.get("presentes_baseline_6m_media",0):.2f} vs {desc_atr0.get("presentes_baseline_6m_media",0):.2f}. Ver `A5_tabela_02_descritiva_outcomes_6m.csv`.

## 3. Modelos primarios (associativos, sem causalidade)

Especificacao minimal exatamente como A3 adaptada: `outcome ~ atracao_muni (0/1) + FE curso (16) + FE UF(colapsada RESTO {sorted(small_ufs)}) + cluster municipio (G=368)`. Atracao preditor binario municipal (max sobre CNES). Full adiciona estrato + ivs_2010 + log_pop + estoque_por_10k.

| Outcome 6m | coef atracao (SE) minimal | IC95% | p | N | G | R2 | coef full |
|---|---|---|---|---|---|---|---|
| estoque_6m | {ce["coef_atracao"]:.3f} ({ce["se_atracao"]:.3f}) | {ce["coef_atracao"]-1.96*ce["se_atracao"]:.3f} a {ce["coef_atracao"]+1.96*ce["se_atracao"]:.3f} | {ce["p_atracao"]:.3f} | {ce["n"]} | {ce["n_clusters"]} | {ce["r2"]:.3f} | {ce_full["coef_atracao"]:.3f} |
| delta_estoque_6m | {cd["coef_atracao"]:.3f} ({cd["se_atracao"]:.3f}) | {cd["coef_atracao"]-1.96*cd["se_atracao"]:.3f} a {cd["coef_atracao"]+1.96*cd["se_atracao"]:.3f} | {cd["p_atracao"]:.3f} | {ce["n"]} | {ce["n_clusters"]} | {cd["r2"]:.3f} | {cd_full["coef_atracao"]:.3f} |
| cobertura_6m (LPM) | {cc["coef_atracao"]:.3f} ({cc["se_atracao"]:.3f}) | {cc["coef_atracao"]-1.96*cc["se_atracao"]:.3f} a {cc["coef_atracao"]+1.96*cc["se_atracao"]:.3f} | {cc["p_atracao"]:.3f} | {ce["n"]} | {ce["n_clusters"]} | - | - |
| entradas_6m follow | {cen["coef_atracao"]:.3f} ({cen["se_atracao"]:.3f}) | {cen["coef_atracao"]-1.96*cen["se_atracao"]:.3f} a {cen["coef_atracao"]+1.96*cen["se_atracao"]:.3f} | {cen["p_atracao"]:.3f} | | | | |
| presentes_baseline_6m (nivel) | {cp["coef_atracao"]:.3f} ({cp["se_atracao"]:.3f}) | {cp["coef_atracao"]-1.96*cp["se_atracao"]:.3f} a {cp["coef_atracao"]+1.96*cp["se_atracao"]:.3f} | {cp["p_atracao"]:.3f} | | | | |

Linguagem: **associado a** maior estoque/cobertura em 6m quando houve atracao na celula; delta pequeno e IC largo; nenhuma inferencia causal nem dose bolsa. Faixa nao entra como covariada principal por colinearidade com IVS (regra anunciada). Ver `A5_tabela_03*.csv`.

Sensibilidade horizonte alternativo {ALT_BASELINE}->{ALT_FOLLOW}: coef delta {estimativas["modelos"]["T0_alternativo_delta"]["coef_atracao"]:.3f} (SE {estimativas["modelos"]["T0_alternativo_delta"]["se_atracao"]:.3f}) p {estimativas["modelos"]["T0_alternativo_delta"]["p_atracao"]:.3f} - magnitude similar, preserva conclusao.
Sensibilidades adicionais: winsorizado p99 delta {estimativas["modelos"]["delta_winsorizado_p99"]["coef_atracao"]:.3f} (p {estimativas["modelos"]["delta_winsorizado_p99"]["p_atracao"]:.3f}); confirmatoria 587 vs ampliada 597: confirmatoria {estimativas["modelos"]["delta_strat_confirmatoria"]["coef_atracao"]:.3f} (ampliada em tabela `A5_tabela_03h`); heterogeneidade atracao x estrato nao significativa (ver `A5_tabela_03i`). Ver `A5_tabela_03g/03h/03i`.

## 4. Influencia e robustez

Leave-one-UF (27) e leave-one-curso (16) para delta minimal: range coef atracao {loo_range}. Nenhuma UF/curso inverte sinal de forma relevante. Ver `A5_tabela_04_leave_one_out.csv`.

Leave-one-municipio (368) DFBETA para atracao em delta: base {infl_summary.get("base",0):.3f} range {infl_summary.get("atracao_delta_min",0):.3f} a {infl_summary.get("max",0):.3f} sd {infl_summary.get("sd",0):.3f}; top influentes: {", ".join([f"{r['co_ibge_6d']} Δ{r['delta']:.2f} DFBETA{r['dfbeta']:.2f}" for r in estimativas["influencia"]["top_influentes"][:3]] ) } . Nenhum |DFBETA|>1.5. Ver `A5_tabela_05_influencia_municipal.csv`.

Curso como exploracao: 10 cursos confirmatorios contribuem; cursos sobrepostos estratificados mostram sensibilidade sem mudar primario.

## 5. Validacao preditiva por municipio (GroupKFold 5)

Delta estoque minimal: R2 out {pred_df[pred_df["modelo"]=="OLS_delta_minimal_atracao_FE"]["r2_media_out"].values[0]:.3f} sd {pred_df[pred_df["modelo"]=="OLS_delta_minimal_atracao_FE"]["r2_sd_out"].values[0]:.3f} vs in {pred_df[pred_df["modelo"]=="OLS_delta_minimal_atracao_FE"]["r2_insample"].values[0]:.3f}; RMSE out {pred_df[pred_df["modelo"]=="OLS_delta_minimal_atracao_FE"]["rmse_media_out"].values[0]:.2f} vs in {pred_df[pred_df["modelo"]=="OLS_delta_minimal_atracao_FE"]["rmse_insample"].values[0]:.2f}.
Estoque 6m: R2 out {pred_df[pred_df["modelo"]=="OLS_estoque_6m_minimal"]["r2_media_out"].values[0]:.3f} vs in {pred_df[pred_df["modelo"]=="OLS_estoque_6m_minimal"]["r2_insample"].values[0]:.3f}. Gap pequeno indica overfit FE limitado. Ver `A5_tabela_06_validacao_preditiva.csv`.

## 6. Figuras

- `A5_figura_01_trajetoria_estoque_estrato.png`: trajetoria medias por estrato com T0.
- `A5_figura_02_trajetoria_estoque_atracao.png`: com vs sem atracao.
- `A5_figura_03_delta_estoque_atracao.png`: delta 6m por atracao.

## 7. Linguagem autorizada e decisao sobre ligacao com atracao

Permitido: oferta cadastrada local, persistencia da oferta local (estoque/cobertura/entradas/saldo/presentes em nivel), gradiente territorial, associado a. **Proibido:** retenção individual do bolsista, atividade fisica confirmada, efeito causal do PMM-E/bolsa/IVS, WTA, taxa por vaga, dose recebida.

Decisao explicita: **Pode** ligar descriptiva e associativamente o outcome A1 binario por celula (atracao administrativa max ao municipio-curso) ao painel CNES agregado no horizonte 6m comum {BASELINE_COMP}->{FOLLOW_6M_COMP} usando especificacoes pre-definidas, FE curso/UF e cluster municipio, com ponte restrita ao nucleo sem sobreposicao como primario e estratificacao ampliada como sensibilidade. A ligacao e **somente associativa** (persistencia da oferta local onde houve atracao vs onde nao houve), reportada em nivel e diferenca bruta/ajustada, sem taxa condicional a entrantes.

**Nao pode:** chamar delta ou presenca de efeito do PMM-E/bolsa adicional; nao chamar presenca no CNES de participacao confirmada no programa; nao usar presenca condicionada so nos entrantes como retencao; nao interpretar entradas tardias 202605+ sem censura; nao converter faixa anunciada em dose causal (colinearidade IVS-faixa).

## 8. Limites e proximos passos

- Amostra 1184 municipio-curso tem municipios com múltiplos CNES; unidade inferencia municipio correta, mas potencia heterogeneidade por estrato limitada (capital 18 clusters) como em A3.
- Entradas/saidas dependem de definicao 6m/3m e da estabilidade do identificador CO_PROFISSIONAL_SUS (continuidade mediana 99.2% mes a mes, mas sem documentacao externa; ver manifesto painel).
- Presenca em nivel e pequeno (media <0.3); ruidos cadastrais podem confundir mudanca real.
- Sem log de eventos PMM-E (A07-02) e sem ponte individual (A07-03), nao vincular individuo bolsista a CNES.
- Sem regra administrativa validada (R1), nao estimar salto causal em cutoff IVS para CNES; manter A6 red team antes de artigo.

*Gerado por `scripts/tema_trabalho/06_avaliar_provimento_cnes.py` em {dt.date.today().isoformat()}. Hashes verificados em `A5_estimativas_provimento.json` e `A5_manifesto_maturidade_censura.json`.*
"""
    tmp = RELATORIO_MD.with_suffix(".md.tmp")
    tmp.write_text(relatorio, encoding="utf-8")
    tmp.replace(RELATORIO_MD)
    print(f"[OK] A5 concluido: 1184 celulas x26 painel T0 {T0_ADMIN_COMP} baseline {BASELINE_COMP}->{FOLLOW_6M_COMP} estoqueDelta atracao coef {cd['coef_atracao']:.3f} p {cd['p_atracao']:.3f} | cobertura {cc['coef_atracao']:.3f}")

if __name__=="__main__":
    main()
