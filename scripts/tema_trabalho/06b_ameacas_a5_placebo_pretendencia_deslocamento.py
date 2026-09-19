"""A5 — três ameaças do red team (item C-7): placebo, pré-tendência por curso e deslocamento.

Protocolo congelado em 16/09/2026, antes da execução, em
`docs/06_execucao/36_backlog_pos_auditoria.md`, item C-7. Este script o
implementa sem reescolher amostra, janela ou estimador depois de ver o efeito.

Insumo: `output/tema_trabalho/A5_painel_T0.parquet`, com o SHA-256 conferido
contra o manifesto A6. O painel mensal do CNES não está no repositório (D-4),
e este script não o exige.

Comum aos três testes: amostra confirmatória (587 células, dez cursos com CBO
não compartilhado); duas escalas (nível e log1p); efeitos fixos de célula,
curso–mês e UF–mês; erros agrupados por município; referência 202506; a
inferência citada é a da convenção que conta os efeitos fixos absorvidos
(`_gl_fe`).

1. Placebo: células sem atração em municípios com atração em alguma das suas
   1.184 células, contra células sem atração em municípios sem nenhuma.
2. Heterogeneidade de pré-tendência: o estudo de evento dentro de cada curso,
   com o teste conjunto dos doze coeficientes pré; regra fixada de antemão:
   listar os cursos com pré-p < 0,05 na escala proporcional e reportar 202603
   excluindo-os, nas duas escalas.
3. Deslocamento: (a) transbordo sobre células sem atração expostas a outro
   município da mesma região de saúde, dentro do painel, com atração no mesmo
   curso; (b) oferta líquida por região–curso–mês, com tratamento = região–curso
   tem ao menos uma célula com atração, cluster por região.

Linguagem: tudo aqui é associativo. Atração é resultado administrativo
realizado, não tratamento atribuído.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "scripts" / "avaliacao_impacto"))
from model_utils import fit_absorbed_ols  # noqa: E402

OUT_DIR = ROOT / "output" / "tema_trabalho"
PAINEL_T0 = OUT_DIR / "A5_painel_T0.parquet"
PAINEL_T0_REL = "output/tema_trabalho/A5_painel_T0.parquet"
MANIFESTO_A6 = OUT_DIR / "A6_manifesto_reproducao.json"
A5_ESTIMATIVAS = OUT_DIR / "A5_estimativas_provimento.json"

TABELA_PLACEBO = OUT_DIR / "A5_tabela_12_placebo_municipio_com_atracao.csv"
TABELA_PRETENDENCIA = OUT_DIR / "A5_tabela_13_pretendencia_por_curso.csv"
TABELA_DESLOCAMENTO = OUT_DIR / "A5_tabela_14_deslocamento_regional.csv"
JSON_AMEACAS = OUT_DIR / "A5_ameacas_c7.json"

COMPETENCIAS = [f"{y}{m:02d}" for y, a, b in ((2024, 6, 12), (2025, 1, 12), (2026, 1, 7)) for m in range(a, b + 1)]
BASELINE_COMP = "202506"
FOLLOW_COMP = "202603"
T0_ADMIN_COMP = "202510"
ESCALAS = {"nivel": "estoque em nivel", "proporcional": "log1p do estoque"}
ALPHA_PRE = 0.05

# Comparacoes declaradas no protocolo: o que a reauditoria independente mediu
# por conta propria. Nao sao alvos: sao a referencia contra a qual a leitura e
# feita, registrada antes de rodar.
REAUDITORIA = {
    "placebo_nivel": {"beta": 0.092, "se": 0.303, "p": 0.761, "pre_F": 0.81},
    "pretendencia_por_curso_nivel": {"14": {"F": 2.46, "p": 0.007}, "16": {"F": 11.90}, "2": {"F": 6.85}},
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def carregar_painel() -> tuple[pd.DataFrame, str]:
    if not PAINEL_T0.exists():
        raise FileNotFoundError(PAINEL_T0)
    registrado = json.loads(MANIFESTO_A6.read_text(encoding="utf-8"))["hashes_entradas_e_artefatos"].get(PAINEL_T0_REL, {}).get("sha256")
    observado = sha256(PAINEL_T0)
    if registrado is None or registrado != observado:
        raise RuntimeError(f"{PAINEL_T0_REL} sem ancora no A6 ou divergente: registrado {registrado}, observado {observado}")
    panel = pd.read_parquet(PAINEL_T0)
    panel["competencia"] = panel["competencia"].astype(str)
    panel["co_ibge_6d"] = panel["co_ibge_6d"].astype(str).str.zfill(6)
    panel["cod_curso"] = panel["cod_curso"].astype(int)
    panel["region_id"] = panel["region_id"].astype(str)
    assert len(panel) == 30784 and panel["competencia"].nunique() == 26
    return panel, observado


def preparar(sample: pd.DataFrame, tratamento: str, unidade: list[str], fe_unidade: str = "cell_id") -> tuple[pd.DataFrame, list[str]]:
    ev = sample.copy()
    ev[fe_unidade] = ev[unidade].astype(str).agg("_".join, axis=1)
    ev["course_month"] = ev["cod_curso"].astype(str) + "_" + ev["competencia"]
    ev["uf_month"] = ev["sg_uf"].astype(str) + "_" + ev["competencia"]
    ev["log_estoque_mst"] = np.log1p(ev["especialistas_mst"].astype(float))
    terms = []
    for comp in COMPETENCIAS:
        if comp == BASELINE_COMP:
            continue
        term = f"event_{comp}"
        ev[term] = ev[tratamento].astype(float) * (ev["competencia"] == comp).astype(float)
        terms.append(term)
    return ev, terms


def n_fe(frame: pd.DataFrame, fes: list[str]) -> int:
    return int(sum(frame[fe].nunique() for fe in fes) - (len(fes) - 1))


def ajustar(ev: pd.DataFrame, terms: list[str], escala: str, fes: list[str], cluster: str) -> dict[str, Any]:
    outcome = "especialistas_mst" if escala == "nivel" else "log_estoque_mst"
    k_fe = n_fe(ev, fes)
    modelo, diag = fit_absorbed_ols(ev, outcome, terms, fes, cluster, n_absorbed=k_fe)
    pre_terms = [t for t in terms if t.replace("event_", "") < BASELINE_COMP]
    restr = np.zeros((len(pre_terms), len(terms)))
    for i, t in enumerate(pre_terms):
        restr[i, terms.index(t)] = 1.0
    # Em subamostras pequenas a covariancia das restricoes pode nao ter posto
    # completo (poucos clusters); o F conjunto e entao pouco confiavel, e o
    # posto e publicado para que a leitura nao dependa de um aviso no console.
    cov_restr = restr @ np.asarray(modelo.cov_params()) @ restr.T
    posto_pre = int(np.linalg.matrix_rank(cov_restr))
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        ftest = modelo.f_test(restr)
    term = f"event_{FOLLOW_COMP}"
    lo, hi = [float(x) for x in modelo.conf_int().loc[term]]
    return {
        "escala": escala,
        "outcome": outcome,
        "n_obs": int(len(ev)),
        "n_unidades": int(ev[fes[0]].nunique()),
        "n_clusters": int(ev[cluster].nunique()),
        "n_parametros_fe_absorvidos": k_fe,
        "n_tratadas": int(ev.loc[ev["competencia"] == BASELINE_COMP, "_trat"].sum()),
        "n_controle": int((ev.loc[ev["competencia"] == BASELINE_COMP, "_trat"] == 0).sum()),
        "mar2026_beta": float(modelo.params[term]),
        "mar2026_se_gl_fe": float(modelo.bse[term]),
        "mar2026_p_gl_fe": float(modelo.pvalues[term]),
        "mar2026_ci_low_gl_fe": lo,
        "mar2026_ci_high_gl_fe": hi,
        "pre_F_gl_fe": float(np.asarray(ftest.fvalue).item()),
        "pre_p_gl_fe": float(np.asarray(ftest.pvalue).item()),
        "n_coef_pre": len(pre_terms),
        "pre_F_posto_covariancia": posto_pre,
        "pre_F_confiavel": bool(posto_pre == len(pre_terms)),
        "coeficientes": [
            {
                "competencia": t.replace("event_", ""),
                "beta": float(modelo.params[t]),
                "se_gl_fe": float(modelo.bse[t]),
                "p_gl_fe": float(modelo.pvalues[t]),
            }
            for t in terms
        ],
    }


def rodar(sample: pd.DataFrame, tratamento: str, unidade: list[str], fes: list[str], cluster: str, rotulo: str) -> list[dict[str, Any]]:
    ev, terms = preparar(sample, tratamento, unidade)
    ev["_trat"] = ev[tratamento].astype(float)
    saidas = []
    for escala in ESCALAS:
        r = ajustar(ev, terms, escala, fes, cluster)
        r["teste"] = rotulo
        r["tratamento"] = tratamento
        saidas.append(r)
    return saidas


def linha(r: dict[str, Any], **extra) -> dict[str, Any]:
    base = {k: v for k, v in r.items() if k != "coeficientes"}
    base.update(extra)
    return base


def main() -> None:
    panel, hash_painel = carregar_painel()
    conf = panel[panel["amostra_confirmatoria"].astype(bool)].copy()
    assert conf[["co_ibge_6d", "cod_curso"]].drop_duplicates().shape[0] == 587
    fes_celula = ["cell_id", "course_month", "uf_month"]

    # ------------------------------------------------------------------
    # 1. Placebo: celulas sem atracao em municipios com atracao (em alguma
    #    das 1.184 celulas) contra celulas sem atracao em municipios sem.
    # ------------------------------------------------------------------
    muni_com_atracao = panel.groupby("co_ibge_6d")["atracao_muni"].max().rename("muni_com_atracao")
    sem_atracao = conf[conf["atracao_muni"] == 0].merge(muni_com_atracao, left_on="co_ibge_6d", right_index=True, how="left")
    assert sem_atracao["muni_com_atracao"].notna().all()
    placebo = rodar(sem_atracao, "muni_com_atracao", ["co_ibge_6d", "cod_curso"], fes_celula, "co_ibge_6d", "placebo_celulas_sem_atracao_em_municipio_com_atracao")
    tab_placebo = pd.DataFrame([linha(r, comparacao_reauditoria_nivel=json.dumps(REAUDITORIA["placebo_nivel"])) for r in placebo])
    tmp = TABELA_PLACEBO.with_suffix(".csv.tmp")
    tab_placebo.to_csv(tmp, index=False)
    tmp.replace(TABELA_PLACEBO)

    # ------------------------------------------------------------------
    # 2. Heterogeneidade de pre-tendencia por curso.
    # ------------------------------------------------------------------
    linhas_curso = []
    por_curso: dict[str, dict[str, Any]] = {}
    for curso in sorted(conf["cod_curso"].unique()):
        sub = conf[conf["cod_curso"] == curso]
        # Dentro do curso, curso-mes colapsa em mes; UF-mes permanece.
        try:
            res = rodar(sub, "atracao_muni", ["co_ibge_6d", "cod_curso"], fes_celula, "co_ibge_6d", f"pretendencia_curso_{int(curso):02d}")
        except RuntimeError as exc:  # posto incompleto em subamostra pequena
            for escala in ESCALAS:
                linhas_curso.append({"teste": f"pretendencia_curso_{int(curso):02d}", "cod_curso": int(curso), "escala": escala, "erro": str(exc)})
            continue
        por_curso[str(int(curso))] = {r["escala"]: r for r in res}
        for r in res:
            linhas_curso.append(linha(r, cod_curso=int(curso), pre_rejeita_5pct=bool(r["pre_p_gl_fe"] < ALPHA_PRE)))
    tab_pre = pd.DataFrame(linhas_curso)
    cursos_rejeitam_prop = sorted(int(c) for c, esc in por_curso.items() if esc["proporcional"]["pre_p_gl_fe"] < ALPHA_PRE)
    cursos_rejeitam_nivel = sorted(int(c) for c, esc in por_curso.items() if esc["nivel"]["pre_p_gl_fe"] < ALPHA_PRE)
    # Regra fixada no protocolo: excluir os cursos com pre-p < 0,05 na escala
    # proporcional e reportar 202603 nas duas escalas.
    restante = conf[~conf["cod_curso"].isin(cursos_rejeitam_prop)]
    sens_excl = rodar(restante, "atracao_muni", ["co_ibge_6d", "cod_curso"], fes_celula, "co_ibge_6d", "sensibilidade_excluindo_cursos_pre_p_lt_0_05_proporcional") if len(cursos_rejeitam_prop) else []
    completo = rodar(conf, "atracao_muni", ["co_ibge_6d", "cod_curso"], fes_celula, "co_ibge_6d", "amostra_confirmatoria_completa_referencia")
    for r in completo:
        linhas_curso.append(linha(r, cod_curso=-1, pre_rejeita_5pct=bool(r["pre_p_gl_fe"] < ALPHA_PRE), cursos_incluidos="todos_10"))
    for r in sens_excl:
        linhas_curso.append(linha(r, cod_curso=-1, pre_rejeita_5pct=bool(r["pre_p_gl_fe"] < ALPHA_PRE), cursos_incluidos=";".join(str(c) for c in sorted(restante["cod_curso"].unique())), cursos_excluidos=";".join(str(c) for c in cursos_rejeitam_prop)))
    tab_pre = pd.DataFrame(linhas_curso)
    tmp = TABELA_PRETENDENCIA.with_suffix(".csv.tmp")
    tab_pre.to_csv(tmp, index=False)
    tmp.replace(TABELA_PRETENDENCIA)

    # ------------------------------------------------------------------
    # 3. Deslocamento dentro da regiao de saude.
    # ------------------------------------------------------------------
    # (a) transbordo: celulas sem atracao expostas a OUTRO municipio da mesma
    #     regiao, dentro do painel, com atracao no mesmo curso.
    base = conf[conf["competencia"] == BASELINE_COMP][["co_ibge_6d", "cod_curso", "region_id", "atracao_muni"]].copy()
    atr_reg = base[base["atracao_muni"] == 1].groupby(["region_id", "cod_curso"])["co_ibge_6d"].apply(set).to_dict()

    def exposto(row) -> int:
        outros = atr_reg.get((row["region_id"], row["cod_curso"]), set()) - {row["co_ibge_6d"]}
        return int(len(outros) > 0)

    base["vizinho_regiao_com_atracao_mesmo_curso"] = base.apply(exposto, axis=1)
    sem_atr_cells = conf[conf["atracao_muni"] == 0].merge(
        base[["co_ibge_6d", "cod_curso", "vizinho_regiao_com_atracao_mesmo_curso"]], on=["co_ibge_6d", "cod_curso"], how="left"
    )
    assert sem_atr_cells["vizinho_regiao_com_atracao_mesmo_curso"].notna().all()
    transbordo = rodar(sem_atr_cells, "vizinho_regiao_com_atracao_mesmo_curso", ["co_ibge_6d", "cod_curso"], fes_celula, "co_ibge_6d", "transbordo_celulas_sem_atracao_com_vizinho_atraido_mesmo_curso")

    # (b) oferta liquida regional: soma do estoque por regiao-curso-mes.
    reg = (
        conf.groupby(["region_id", "cod_curso", "competencia"], as_index=False)
        .agg(especialistas_mst=("especialistas_mst", "sum"), regiao_com_atracao=("atracao_muni", "max"), n_municipios_painel=("co_ibge_6d", "nunique"), sg_uf=("sg_uf", "first"))
    )
    assert reg.groupby(["region_id", "cod_curso"])["competencia"].nunique().eq(26).all()
    reg["cell_id_placeholder"] = 0
    ev_reg, terms_reg = preparar(reg, "regiao_com_atracao", ["region_id", "cod_curso"], fe_unidade="cell_id")
    ev_reg["_trat"] = ev_reg["regiao_com_atracao"].astype(float)
    regional = []
    for escala in ESCALAS:
        r = ajustar(ev_reg, terms_reg, escala, ["cell_id", "course_month", "uf_month"], "region_id")
        r["teste"] = "oferta_liquida_regiao_curso"
        r["tratamento"] = "regiao_com_atracao"
        regional.append(r)
    n_reg_multi = int((reg[reg["competencia"] == BASELINE_COMP]["n_municipios_painel"] > 1).sum())
    tab_desl = pd.DataFrame(
        [linha(r, nivel_agregacao="celula_municipio_curso", limite="vizinho = outro municipio do quadro na mesma regiao de saude; municipios fora do quadro nao sao observados") for r in transbordo]
        + [linha(r, nivel_agregacao="regiao_curso", limite=f"estoque somado apenas sobre municipios do painel; {n_reg_multi} regiao-curso com mais de um municipio na referencia") for r in regional]
    )
    tmp = TABELA_DESLOCAMENTO.with_suffix(".csv.tmp")
    tab_desl.to_csv(tmp, index=False)
    tmp.replace(TABELA_DESLOCAMENTO)

    # ------------------------------------------------------------------
    # JSON com protocolo, resultados e leitura pre-especificada.
    # ------------------------------------------------------------------
    def resumo(rs: list[dict[str, Any]]) -> dict[str, Any]:
        return {r["escala"]: {k: v for k, v in r.items() if k not in ("coeficientes",)} | {"coeficientes": r["coeficientes"]} for r in rs}

    principal = json.loads(A5_ESTIMATIVAS.read_text(encoding="utf-8"))["modelos"]
    saida = {
        "protocolo": "A5_AMEACAS_C7",
        "data_referencia": dt.date.today().isoformat(),
        "protocolo_congelado_em": "2026-09-16, docs/06_execucao/36_backlog_pos_auditoria.md, item C-7, antes da execucao",
        "linguagem": "associativa; atracao e resultado realizado; nenhum efeito causal",
        "amostra": {"celulas_confirmatorias": 587, "municipios": int(conf["co_ibge_6d"].nunique()), "cursos": sorted(int(c) for c in conf["cod_curso"].unique())},
        "convencao_inferencia": "erros agrupados por municipio (ou regiao, no teste regional) com graus de liberdade que contam os efeitos fixos absorvidos (_gl_fe)",
        "referencia_principal_a5": {
            "proporcional_mar2026_beta": principal["principal_proporcional_confirmatorio"]["mar2026_beta"],
            "proporcional_mar2026_p_gl_fe": principal["principal_proporcional_confirmatorio"]["mar2026_p_gl_fe"],
            "nivel_mar2026_beta": principal["principal_dinamico_confirmatorio"]["mar2026_beta"],
            "nivel_mar2026_p_gl_fe": principal["principal_dinamico_confirmatorio"]["mar2026_p_gl_fe"],
        },
        "placebo": {
            "definicao": "celulas confirmatorias sem atracao; placebo = municipio com atracao em alguma das suas 1.184 celulas",
            "leitura_pre_especificada": "coeficiente pos distinguivel de zero indicaria choque municipal correlacionado com atrair; indistinguivel de zero sustenta que o resultado principal e da celula",
            "comparacao_reauditoria_nivel": REAUDITORIA["placebo_nivel"],
            "resultado": resumo(placebo),
        },
        "pretendencia_por_curso": {
            "definicao": "estudo de evento dentro de cada curso; teste conjunto dos 12 coeficientes pre",
            "regra_pre_especificada": "listar cursos com pre-p < 0,05 na escala proporcional e reportar 202603 excluindo-os, nas duas escalas",
            "comparacao_reauditoria_nivel": REAUDITORIA["pretendencia_por_curso_nivel"],
            "cursos_pre_p_lt_0_05_proporcional": cursos_rejeitam_prop,
            "cursos_pre_p_lt_0_05_nivel": cursos_rejeitam_nivel,
            "por_curso": {c: {esc: {k: v for k, v in r.items() if k != "coeficientes"} for esc, r in escs.items()} for c, escs in por_curso.items()},
            "amostra_completa": resumo(completo),
            "sensibilidade_excluindo_cursos_rejeitados": resumo(sens_excl),
        },
        "deslocamento": {
            "definicao_a": "transbordo: celulas confirmatorias sem atracao; exposicao = outro municipio do painel na mesma regiao de saude com atracao no mesmo curso",
            "definicao_b": "oferta liquida: estoque somado por regiao-curso-mes sobre municipios do painel; tratamento = regiao-curso com ao menos uma celula com atracao; FE regiao-curso, curso-mes, UF-mes; cluster regiao",
            "leitura_pre_especificada": "em (a), coeficiente pos negativo indica deslocamento a partir de vizinhos; em (b), coeficiente zero indicaria pura realocacao dentro da regiao e positivo indicaria expansao liquida",
            "limite": "o painel contem apenas os 368 municipios do quadro; vizinho e vizinho dentro do quadro",
            "n_regioes": int(reg["region_id"].nunique()),
            "n_regiao_curso": int(reg[["region_id", "cod_curso"]].drop_duplicates().shape[0]),
            "n_regiao_curso_com_mais_de_um_municipio": n_reg_multi,
            "transbordo": resumo(transbordo),
            "oferta_liquida_regional": resumo(regional),
        },
        "hashes_entradas": {
            PAINEL_T0_REL: {"sha256": hash_painel, "conferido_contra": "output/tema_trabalho/A6_manifesto_reproducao.json"},
            "output/tema_trabalho/A5_estimativas_provimento.json": {"sha256": sha256(A5_ESTIMATIVAS)},
        },
        "arquivos": {
            "tabela_placebo": str(TABELA_PLACEBO.relative_to(ROOT)).replace("\\", "/"),
            "tabela_pretendencia": str(TABELA_PRETENDENCIA.relative_to(ROOT)).replace("\\", "/"),
            "tabela_deslocamento": str(TABELA_DESLOCAMENTO.relative_to(ROOT)).replace("\\", "/"),
        },
    }
    tmp = JSON_AMEACAS.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(saida, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(JSON_AMEACAS)

    pl = {r["escala"]: r for r in placebo}
    tr = {r["escala"]: r for r in transbordo}
    rg = {r["escala"]: r for r in regional}
    print(
        "[OK] C-7: placebo nivel {:.3f} (EP {:.3f}; p {:.3f}; pre-F {:.2f}), proporcional {:.4f} (p {:.3f}); "
        "cursos com pre-p<0,05 (proporcional): {}; (nivel): {}; "
        "transbordo nivel {:.3f} (p {:.3f}) proporcional {:.4f} (p {:.3f}); "
        "oferta liquida regional nivel {:.3f} (p {:.3f}) proporcional {:.4f} (p {:.3f})".format(
            pl["nivel"]["mar2026_beta"], pl["nivel"]["mar2026_se_gl_fe"], pl["nivel"]["mar2026_p_gl_fe"], pl["nivel"]["pre_F_gl_fe"],
            pl["proporcional"]["mar2026_beta"], pl["proporcional"]["mar2026_p_gl_fe"],
            cursos_rejeitam_prop, cursos_rejeitam_nivel,
            tr["nivel"]["mar2026_beta"], tr["nivel"]["mar2026_p_gl_fe"], tr["proporcional"]["mar2026_beta"], tr["proporcional"]["mar2026_p_gl_fe"],
            rg["nivel"]["mar2026_beta"], rg["nivel"]["mar2026_p_gl_fe"], rg["proporcional"]["mar2026_beta"], rg["proporcional"]["mar2026_p_gl_fe"],
        )
    )


if __name__ == "__main__":
    main()
