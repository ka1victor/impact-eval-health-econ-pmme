"""A5 — diagnóstico descritivo da pré-tendência dos cursos 2 e 16 no CNES pré.

DIAGNÓSTICO DESCRITIVO. Nada aqui é estimativa de efeito, nada alimenta regra,
amostra, filtro ou heterogeneidade de A5, e nenhum artefato de A5 ou A6 é
regravado.

Protocolo congelado em 01/10/2026, antes deste código, em
`docs/06_execucao/36_backlog_pos_auditoria.md`, seção "Diagnóstico cadastral
dos cursos 2 e 16 — 01/10/2026". Pergunta: a rejeição da pré-tendência nos
cursos 2 e 16 da `A5_tabela_13` tem assinatura de mudança cadastral ou de
oferta no CNES pré-tratamento?

D1 — decomposição exata, em nível, dos 12 coeficientes pré do estudo de evento
     por curso (mesma especificação da `A5_tabela_13`) entre o estoque dos CNES
     ofertantes da célula e o restante do município. Os coeficientes pós dos
     componentes entram no cálculo, porque o estimador usa as 26 competências,
     mas não são gravados nem impressos.
D2 — fluxos de pessoas na janela 202412–202506: saldo duradouro
     (entradas após seis meses de ausência menos saídas confirmadas por três)
     contra saldo intermitente (o resto da variação do estoque).
D3 — célula–mês pré em que o estoque do único CNES ofertante supera o estoque
     municipal, o que só ocorre se o `co_municipio_gestor` dos vínculos não for
     o município da célula.

Insumos, todos versionados e com SHA-256 conferido contra a âncora:
- `output/tema_trabalho/A5_painel_T0.parquet` (âncora: manifesto A6);
- `output/painel_cnes_especialidade_mensal.parquet` (âncora: manifesto da
  tipologia territorial);
- `output/avaliacao_impacto/dados/painel_municipio_curso_mes.parquet`, cópia do
  painel mensal (âncora: hash registrado em A5 para o painel mensal), usado só
  para conferir que o estoque e os fluxos do T0 são os do painel mensal;
- `output/tema_trabalho/A5_tabela_13_pretendencia_por_curso.csv`, alvo de
  reprodução do estoque.

Determinístico: sem sorteio e sem data de execução nos artefatos.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import warnings
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.append(str(ROOT / "scripts" / "avaliacao_impacto"))
from utils.ambiente import verificar_ambiente  # noqa: E402
from model_utils import fit_absorbed_ols  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "ameacas_c7", ROOT / "scripts" / "tema_trabalho" / "06b_ameacas_a5_placebo_pretendencia_deslocamento.py"
)
c7 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(c7)  # type: ignore[union-attr]

OUT_DIR = ROOT / "output" / "tema_trabalho"
PAINEL_T0_REL = "output/tema_trabalho/A5_painel_T0.parquet"
PAINEL_CNES_REL = "output/painel_cnes_especialidade_mensal.parquet"
PAINEL_MENSAL_COPIA_REL = "output/avaliacao_impacto/dados/painel_municipio_curso_mes.parquet"
PAINEL_MENSAL_DECLARADO_REL = "output/painel_municipio_curso_mensal.parquet"
TABELA_13_REL = "output/tema_trabalho/A5_tabela_13_pretendencia_por_curso.csv"
MANIFESTO_A6_REL = "output/tema_trabalho/A6_manifesto_reproducao.json"
MANIFESTO_TIPOLOGIA_REL = "output/tema_trabalho/manifesto_tipologia_territorial.json"
A5_ESTIMATIVAS_REL = "output/tema_trabalho/A5_estimativas_provimento.json"

TABELA_16 = OUT_DIR / "A5_tabela_16_decomposicao_estabelecimento_pre.csv"
TABELA_17 = OUT_DIR / "A5_tabela_17_fluxos_intermitencia_pre.csv"
JSON_SAIDA = OUT_DIR / "A5_diagnostico_cadastral_cursos_2_16.json"

ROTULO = "diagnostico_descritivo"
PROTOCOLO_EM = "2026-10-01"
CURSOS_FOCO = (2, 16)
BASELINE = c7.BASELINE_COMP  # 202506
COMPETENCIAS = c7.COMPETENCIAS
PRE = [m for m in COMPETENCIAS if m < BASELINE]  # 12 coeficientes pre
JANELA_PRE_COM_REF = [m for m in COMPETENCIAS if m <= BASELINE]  # 202406-202506
JANELA_FLUXO = [m for m in COMPETENCIAS if "202412" <= m <= BASELINE]  # D2
LIMIAR_PHI = 2.0 / 3.0
TOL_DECOMPOSICAO = 1e-6
TOL_REPRODUCAO = 1e-9
TOL_REPRODUCAO_POSTO_BAIXO = 1e-2
LIMIAR_POSTO_ESTRITO = 8
COMPONENTES = {
    "estoque_municipal": "especialistas_mst",
    "cnes_ofertantes": "y_of",
    "restante_municipio": "y_resto",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def conferir_hashes() -> dict[str, dict[str, Any]]:
    """Confere cada insumo contra a âncora registrada; aborta se divergir."""
    a6 = json.loads((ROOT / MANIFESTO_A6_REL).read_text(encoding="utf-8"))["hashes_entradas_e_artefatos"]
    tip = json.loads((ROOT / MANIFESTO_TIPOLOGIA_REL).read_text(encoding="utf-8"))
    tip_hashes = tip.get("hashes_entradas") or tip.get("hashes") or {}
    if PAINEL_CNES_REL not in tip_hashes:
        # O manifesto da tipologia guarda os hashes num bloco cujo nome pode variar;
        # procura a chave em qualquer bloco de primeiro nível.
        for bloco in tip.values():
            if isinstance(bloco, dict) and PAINEL_CNES_REL in bloco:
                tip_hashes = bloco
                break
    a5 = json.loads((ROOT / A5_ESTIMATIVAS_REL).read_text(encoding="utf-8"))["hashes_entradas"]
    ancoras = {
        PAINEL_T0_REL: (a6.get(PAINEL_T0_REL, {}).get("sha256"), MANIFESTO_A6_REL),
        PAINEL_CNES_REL: (tip_hashes.get(PAINEL_CNES_REL, {}).get("sha256"), MANIFESTO_TIPOLOGIA_REL),
        PAINEL_MENSAL_COPIA_REL: (
            a5.get(PAINEL_MENSAL_DECLARADO_REL, {}).get("sha256_registrado_em_execucao_anterior"),
            f"{A5_ESTIMATIVAS_REL} ({PAINEL_MENSAL_DECLARADO_REL}, sha256_registrado_em_execucao_anterior)",
        ),
    }
    hashes: dict[str, dict[str, Any]] = {}
    for rel, (registrado, fonte) in ancoras.items():
        observado = sha256(ROOT / rel)
        if registrado is None or registrado != observado:
            raise RuntimeError(f"{rel}: sem âncora ou divergente (registrado {registrado}, observado {observado})")
        hashes[rel] = {"sha256": observado, "conferido_contra": fonte}
    hashes[TABELA_13_REL] = {"sha256": sha256(ROOT / TABELA_13_REL), "papel": "alvo de reproducao do estoque (D1)"}
    return hashes


def carregar() -> tuple[pd.DataFrame, pd.DataFrame]:
    panel = pd.read_parquet(ROOT / PAINEL_T0_REL)
    panel["competencia"] = panel["competencia"].astype(str)
    panel["co_ibge_6d"] = panel["co_ibge_6d"].astype(str).str.zfill(6)
    panel["cod_curso"] = panel["cod_curso"].astype(int)
    assert len(panel) == 30784 and panel["competencia"].nunique() == 26

    # O T0 traz o estoque e os fluxos do painel mensal: confere célula a célula.
    mensal = pd.read_parquet(ROOT / PAINEL_MENSAL_COPIA_REL)
    mensal["competencia"] = mensal["competencia"].astype(str)
    mensal["co_ibge_6d"] = mensal["co_ibge_6d"].astype(str).str.zfill(6)
    chave = ["co_ibge_6d", "cod_curso", "competencia"]
    cols = ["especialistas_mst", "n_entradas_6m", "n_saidas_confirmadas_3m"]
    m = panel[chave + cols].merge(mensal[chave + cols], on=chave, suffixes=("", "_mensal"), validate="one_to_one")
    if len(m) != len(panel):
        raise RuntimeError("T0 e painel mensal não cobrem as mesmas célula-mês")
    for c in cols:
        a, b = m[c].to_numpy(float), m[f"{c}_mensal"].to_numpy(float)
        if not np.array_equal(np.isnan(a), np.isnan(b)) or not np.array_equal(a[~np.isnan(a)], b[~np.isnan(b)]):
            raise RuntimeError(f"{c} do T0 diverge do painel mensal")

    cnes = pd.read_parquet(ROOT / PAINEL_CNES_REL)
    cnes["competencia"] = cnes["competencia"].astype(str)
    cnes["co_ibge_6d"] = cnes["co_ibge_6d"].astype(str).str.zfill(6)
    cnes["cod_curso"] = cnes["cod_curso"].astype(int)
    if cnes.duplicated(["co_cnes_7d", "cod_curso", "competencia"]).any():
        raise RuntimeError("Painel CNES não é único em CNES-curso-mês")
    return panel, cnes


def montar_amostra(panel: pd.DataFrame, cnes: pd.DataFrame) -> pd.DataFrame:
    conf = panel[panel["amostra_confirmatoria"].astype(bool)].copy()
    assert conf[["co_ibge_6d", "cod_curso"]].drop_duplicates().shape[0] == 587
    of = (
        cnes.groupby(["co_ibge_6d", "cod_curso", "competencia"], as_index=False)
        .agg(y_of=("especialistas_ist", "sum"), n_cnes_painel=("co_cnes_7d", "nunique"))
    )
    conf = conf.merge(of, on=["co_ibge_6d", "cod_curso", "competencia"], how="left", validate="one_to_one")
    # Portão de cobertura: toda célula confirmatória tem todos os seus CNES ofertantes.
    if conf["y_of"].isna().any() or not (conf["n_cnes_painel"] == conf["n_cnes_ofertantes"]).all():
        raise RuntimeError("Cobertura incompleta dos CNES ofertantes nas células confirmatórias")
    conf["y_of"] = conf["y_of"].astype(float)
    conf["y_resto"] = conf["especialistas_mst"].astype(float) - conf["y_of"]
    return conf


def ajustar_pre(ev: pd.DataFrame, terms: list[str], outcome: str) -> dict[str, Any]:
    """Mesma estimação de `ajustar` em 06b, para qualquer desfecho; só o pré sai."""
    fes = ["cell_id", "course_month", "uf_month"]
    k_fe = c7.n_fe(ev, fes)
    modelo, _ = fit_absorbed_ols(ev, outcome, terms, fes, "co_ibge_6d", n_absorbed=k_fe)
    pre_terms = [f"event_{m}" for m in PRE]
    restr = np.zeros((len(pre_terms), len(terms)))
    for i, t in enumerate(pre_terms):
        restr[i, terms.index(t)] = 1.0
    cov = restr @ np.asarray(modelo.cov_params()) @ restr.T
    posto = int(np.linalg.matrix_rank(cov))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        ftest = modelo.f_test(restr)
    return {
        "beta_pre": np.array([float(modelo.params[t]) for t in pre_terms]),
        "se_pre": np.array([float(modelo.bse[t]) for t in pre_terms]),
        "pre_F_gl_fe": float(np.asarray(ftest.fvalue).item()),
        "pre_p_gl_fe": float(np.asarray(ftest.pvalue).item()),
        "pre_F_posto_covariancia": posto,
        "pre_F_confiavel": bool(posto == len(pre_terms)),
        "n_obs": int(len(ev)),
        "n_unidades": int(ev["cell_id"].nunique()),
        "n_clusters": int(ev["co_ibge_6d"].nunique()),
    }


def leitura_phi(phi_of: float) -> str:
    if phi_of >= LIMIAR_PHI:
        return "carregada_pelos_cnes_ofertantes"
    if 1.0 - phi_of >= LIMIAR_PHI:
        return "carregada_pelo_restante_do_municipio"
    return "repartida"


def d1_decomposicao(conf: pd.DataFrame, tab13: pd.DataFrame) -> tuple[pd.DataFrame, dict[int, dict[str, Any]]]:
    linhas: list[dict[str, Any]] = []
    resumo: dict[int, dict[str, Any]] = {}
    alvo = tab13[(tab13["escala"] == "nivel") & (tab13["cod_curso"] >= 0)].set_index("cod_curso")
    pre_janela = conf[conf["competencia"].isin(JANELA_PRE_COM_REF)]
    for curso in sorted(conf["cod_curso"].unique()):
        sub = conf[conf["cod_curso"] == curso]
        ev, terms = c7.preparar(sub, "atracao_muni", ["co_ibge_6d", "cod_curso"])
        ev["_trat"] = ev["atracao_muni"].astype(float)
        res = {nome: ajustar_pre(ev, terms, col) for nome, col in COMPONENTES.items()}
        tot = res["estoque_municipal"]
        # Portão 1: o estoque reproduz a A5_tabela_13. Estrito (1e-9 relativo)
        # nos cursos de foco e onde a covariância das restrições tem posto
        # completo. Onde o posto é muito baixo, o F passa por pseudo-inversa de
        # matriz singular e a tabela publicada, gravada sob outro ambiente
        # (o A6 registra Python 3.11 / numpy 2.4.6), difere a partir da 4ª
        # casa; ali exige-se a mesma decisão a 5% e diferença relativa < 1e-2,
        # e a discrepância é publicada.
        repro: dict[str, Any] = {}
        for campo in ("pre_F_gl_fe", "pre_p_gl_fe"):
            publicado = float(alvo.loc[curso, campo])
            rel = abs(tot[campo] - publicado) / max(1e-300, abs(publicado))
            repro[campo] = {"publicado": publicado, "reproduzido": tot[campo], "diferenca_relativa": rel}
            estrito = int(curso) in CURSOS_FOCO or tot["pre_F_confiavel"] or tot["pre_F_posto_covariancia"] >= LIMIAR_POSTO_ESTRITO
            if estrito and rel > TOL_REPRODUCAO:
                raise RuntimeError(f"curso {curso}: {campo} não reproduz a A5_tabela_13 (dif. relativa {rel:.3e})")
            if not estrito and rel > TOL_REPRODUCAO_POSTO_BAIXO:
                raise RuntimeError(f"curso {curso}: {campo} diverge da A5_tabela_13 além do tolerado (dif. relativa {rel:.3e})")
        if (tot["pre_p_gl_fe"] < c7.ALPHA_PRE) != bool(alvo.loc[curso, "pre_rejeita_5pct"]):
            raise RuntimeError(f"curso {curso}: decisão a 5% da pré-tendência não reproduz a A5_tabela_13")
        repro["portao"] = "estrito" if estrito else "posto_baixo_mesma_decisao_e_dif_relativa_lt_1e-2"
        # Portão 2: a decomposição fecha.
        erro = float(np.max(np.abs(tot["beta_pre"] - res["cnes_ofertantes"]["beta_pre"] - res["restante_municipio"]["beta_pre"])))
        if erro > TOL_DECOMPOSICAO:
            raise RuntimeError(f"curso {curso}: decomposição não fecha (erro {erro})")
        b = tot["beta_pre"]
        ss = float(b @ b)
        phi_of = float(res["cnes_ofertantes"]["beta_pre"] @ b / ss)
        pj = pre_janela[pre_janela["cod_curso"] == curso]
        n_resto_neg = int((pj["y_resto"] < 0).sum())
        resumo[int(curso)] = {
            "phi_cnes_ofertantes": phi_of,
            "phi_restante_municipio": 1.0 - phi_of,
            "leitura_d1": leitura_phi(phi_of),
            "soma_quadrados_beta_pre_estoque": ss,
            "erro_maximo_decomposicao": erro,
            "reproducao_tabela_13": repro,
            "celula_mes_pre_com_resto_negativo": n_resto_neg,
            "por_componente": {
                nome: {k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in r.items()}
                for nome, r in res.items()
            },
        }
        for nome, r in res.items():
            linha = {
                "rotulo": ROTULO,
                "cod_curso": int(curso),
                "componente": nome,
                "escala": "nivel",
                "n_obs": r["n_obs"],
                "n_celulas": r["n_unidades"],
                "n_clusters": r["n_clusters"],
                "pre_F_gl_fe": r["pre_F_gl_fe"],
                "pre_p_gl_fe": r["pre_p_gl_fe"],
                "pre_F_posto_covariancia": r["pre_F_posto_covariancia"],
                "pre_F_confiavel": r["pre_F_confiavel"],
                "parcela_projecao_phi": {"estoque_municipal": 1.0, "cnes_ofertantes": phi_of, "restante_municipio": 1.0 - phi_of}[nome],
                "leitura_d1": resumo[int(curso)]["leitura_d1"],
                "celula_mes_pre_com_resto_negativo": n_resto_neg,
            }
            for m, beta, se in zip(PRE, r["beta_pre"], r["se_pre"], strict=True):
                linha[f"beta_{m}"] = float(beta)
                linha[f"se_{m}"] = float(se)
            linhas.append(linha)
    return pd.DataFrame(linhas), resumo


def d2_d3_fluxos(conf: pd.DataFrame) -> tuple[pd.DataFrame, dict[int, dict[str, Any]]]:
    conf = conf.sort_values(["co_ibge_6d", "cod_curso", "competencia"]).copy()
    g = conf.groupby(["co_ibge_6d", "cod_curso"], sort=False)
    conf["S_ant"] = g["especialistas_mst"].shift(1)
    conf["saidas_ant"] = g["n_saidas_confirmadas_3m"].shift(1)
    conf["dS"] = conf["especialistas_mst"] - conf["S_ant"]
    conf["D"] = conf["n_entradas_6m"] - conf["saidas_ant"]
    conf["N"] = conf["dS"] - conf["D"]
    jan = conf[conf["competencia"].isin(JANELA_FLUXO)].copy()
    if jan[["dS", "D", "N", "n_entradas_6m", "saidas_ant"]].isna().any().any():
        raise RuntimeError("Janela D2 com entrada ou saída censurada")
    if not np.allclose(jan["dS"], jan["D"] + jan["N"]):
        raise RuntimeError("Identidade dS = D + N falhou")
    por_celula = (
        jan.assign(absN=jan["N"].abs())
        .groupby(["cod_curso", "co_ibge_6d", "atracao_muni"], as_index=False)
        .agg(soma_D=("D", "sum"), soma_N=("N", "sum"), soma_absN=("absN", "sum"), soma_S=("especialistas_mst", "sum"), soma_dS=("dS", "sum"))
    )
    # D3: célula-mês pré em que o estoque do CNES ofertante supera o municipal.
    pre = conf[conf["competencia"].isin(JANELA_PRE_COM_REF)].copy()
    pre["excede"] = pre["y_of"] > pre["especialistas_mst"]
    pre["um_cnes"] = pre["n_cnes_ofertantes"] == 1

    linhas: list[dict[str, Any]] = []
    resumo: dict[int, dict[str, Any]] = {}
    for curso in sorted(conf["cod_curso"].unique()):
        grupos: dict[int, dict[str, Any]] = {}
        for trat in (1, 0):
            pc = por_celula[(por_celula["cod_curso"] == curso) & (por_celula["atracao_muni"] == trat)]
            pp = pre[(pre["cod_curso"] == curso) & (pre["atracao_muni"] == trat)]
            um = pp[pp["um_cnes"]]
            multi = pp[~pp["um_cnes"]]
            grupos[trat] = {
                "n_celulas": int(len(pc)),
                "media_soma_D": float(pc["soma_D"].mean()),
                "media_soma_N": float(pc["soma_N"].mean()),
                "media_soma_absN": float(pc["soma_absN"].mean()),
                "media_soma_dS": float(pc["soma_dS"].mean()),
                "taxa_intermitencia_absN_sobre_S": float(pc["soma_absN"].sum() / pc["soma_S"].sum()) if pc["soma_S"].sum() > 0 else float("nan"),
                "d3_celulas_um_cnes": int(um[["co_ibge_6d"]].drop_duplicates().shape[0]),
                "d3_celula_mes_um_cnes_ofertante_excede_municipal": int(um["excede"].sum()),
                "d3_celulas_um_cnes_com_excesso": int(um.loc[um["excede"], "co_ibge_6d"].nunique()),
                "d3_celula_mes_multi_cnes_excede_ambiguo": int(multi["excede"].sum()),
            }
            linhas.append({"rotulo": ROTULO, "cod_curso": int(curso), "grupo": "com_atracao" if trat else "sem_atracao", **grupos[trat]})
        dif_D = grupos[1]["media_soma_D"] - grupos[0]["media_soma_D"]
        dif_N = grupos[1]["media_soma_N"] - grupos[0]["media_soma_N"]
        dif_dS = grupos[1]["media_soma_dS"] - grupos[0]["media_soma_dS"]
        leitura_d2 = "intermitente" if abs(dif_N) > abs(dif_D) else "fluxo_duradouro"
        d3_total = grupos[1]["d3_celula_mes_um_cnes_ofertante_excede_municipal"] + grupos[0]["d3_celula_mes_um_cnes_ofertante_excede_municipal"]
        taxa_total = float(
            por_celula.loc[por_celula["cod_curso"] == curso, "soma_absN"].sum()
            / por_celula.loc[por_celula["cod_curso"] == curso, "soma_S"].sum()
        )
        linhas.append({
            "rotulo": ROTULO, "cod_curso": int(curso), "grupo": "diferencial_com_menos_sem",
            "n_celulas": grupos[1]["n_celulas"] + grupos[0]["n_celulas"],
            "media_soma_D": dif_D, "media_soma_N": dif_N, "media_soma_dS": dif_dS,
            "taxa_intermitencia_absN_sobre_S": taxa_total,
            "d3_celula_mes_um_cnes_ofertante_excede_municipal": d3_total,
            "leitura_d2": leitura_d2,
        })
        resumo[int(curso)] = {
            "grupos": {"com_atracao": grupos[1], "sem_atracao": grupos[0]},
            "diferencial_media_soma_D": dif_D,
            "diferencial_media_soma_N": dif_N,
            "diferencial_media_soma_dS": dif_dS,
            "taxa_intermitencia_curso": taxa_total,
            "leitura_d2": leitura_d2,
            "d3_celula_mes_um_cnes_ofertante_excede_municipal": d3_total,
        }
    return pd.DataFrame(linhas), resumo


def observacoes(curso: int, r1: dict[int, dict[str, Any]], r23: dict[int, dict[str, Any]]) -> dict[str, Any]:
    """Fatos que o protocolo não previa ler, publicados como tais e sem leitura nova.

    (i) componentes em sentidos opostos: phi_of fora de [0, 1] quer dizer que um
    componente se move mais que o estoque municipal e o outro na direção
    contrária; (ii) sinal do diferencial bruto da janela D2 contra o ajustado
    pelo estimador (0 - beta_202411), que pode divergir por causa do UF-mês.
    """
    phi = r1[curso]["phi_cnes_ofertantes"]
    b = r1[curso]["por_componente"]
    i11 = PRE.index("202411")
    ajustado = -float(b["estoque_municipal"]["beta_pre"][i11])
    bruto = float(r23[curso]["diferencial_media_soma_dS"])
    cursos_opostos = sorted(c for c in r1 if not 0.0 <= r1[c]["phi_cnes_ofertantes"] <= 1.0)
    return {
        "componentes_em_sentidos_opostos": bool(not 0.0 <= phi <= 1.0),
        "cursos_com_componentes_em_sentidos_opostos": cursos_opostos,
        "janela_d2_diferencial_bruto_dS": bruto,
        "janela_d2_diferencial_ajustado_menos_beta_202411": ajustado,
        "janela_d2_bruto_e_ajustado_mesmo_sinal": bool(np.sign(bruto) == np.sign(ajustado)),
    }


def gravar_csv(frame: pd.DataFrame, path: Path) -> None:
    tmp = path.with_suffix(".csv.tmp")
    frame.to_csv(tmp, index=False, lineterminator="\n")
    tmp.replace(path)


def main() -> None:
    verificar_ambiente(estrito=True)
    hashes = conferir_hashes()
    panel, cnes = carregar()
    conf = montar_amostra(panel, cnes)
    tab13 = pd.read_csv(ROOT / TABELA_13_REL)

    tab16, r1 = d1_decomposicao(conf, tab13)
    tab17, r23 = d2_d3_fluxos(conf)
    gravar_csv(tab16, TABELA_16)
    gravar_csv(tab17, TABELA_17)

    outros = [c for c in sorted(r23) if c not in CURSOS_FOCO]
    taxas_outros = [r23[c]["taxa_intermitencia_curso"] for c in outros]
    foco: dict[str, Any] = {}
    for curso in CURSOS_FOCO:
        d3 = r23[curso]["d3_celula_mes_um_cnes_ofertante_excede_municipal"]
        d2 = r23[curso]["leitura_d2"]
        if d3 > 0 or d2 == "intermitente":
            combinada = "assinatura_cadastral"
        else:
            combinada = "compativel_com_oferta"
        taxa = r23[curso]["taxa_intermitencia_curso"]
        foco[str(curso)] = {
            "d1": {k: v for k, v in r1[curso].items() if k != "por_componente"},
            "d1_por_componente_pre_F": {
                nome: {k: r1[curso]["por_componente"][nome][k] for k in ("pre_F_gl_fe", "pre_p_gl_fe", "pre_F_posto_covariancia", "pre_F_confiavel")}
                for nome in COMPONENTES
            },
            "d2": {k: v for k, v in r23[curso].items() if k != "grupos"},
            "d2_d3_por_grupo": r23[curso]["grupos"],
            "taxa_intermitencia_vs_outros_oito": {
                "curso": taxa,
                "min_outros": float(min(taxas_outros)),
                "max_outros": float(max(taxas_outros)),
                "acima_do_maximo_dos_outros": bool(taxa > max(taxas_outros)),
            },
            "leitura_combinada": combinada,
            "observacoes_posteriores_ao_protocolo": observacoes(curso, r1, r23),
            "ressalva": "assinatura, nao classificacao: so os microdados do CNES (D-4) distinguem cadastro de oferta",
        }

    saida = {
        "protocolo": "A5_DIAGNOSTICO_CADASTRAL_CURSOS_2_16",
        "rotulo": ROTULO,
        "protocolo_congelado_em": f"{PROTOCOLO_EM}, docs/06_execucao/36_backlog_pos_auditoria.md, secao 'Diagnostico cadastral dos cursos 2 e 16', antes do codigo",
        "linguagem": "descritiva; nenhuma estimativa de efeito; nada alimenta regra, amostra ou estimador de A5",
        "o_que_nao_muda": [
            "amostra confirmatoria de 587 celulas",
            "regra de exclusao pre-registrada sobre o p cru da escala proporcional (cursos 2 e 16)",
            "q do C-7b como leitura, nao criterio",
            "especificacao primaria proporcional e todas as tabelas de A5; nenhum artefato de A5 ou A6 regravado",
        ],
        "janelas": {
            "d1_coeficientes_pre": PRE,
            "d1_referencia": BASELINE,
            "d1_nota": "o estimador usa as 26 competencias; coeficientes pos dos componentes nao sao gravados",
            "d2": JANELA_FLUXO,
            "d3": JANELA_PRE_COM_REF,
        },
        "definicoes": {
            "y_of": "soma, sobre os CNES ofertantes da celula, de CO_PROFISSIONAL_SUS distinto no CNES (painel CNES-curso-mes)",
            "y_resto": "especialistas_mst - y_of; pode ser negativo por dupla contagem entre CNES ofertantes ou por co_municipio_gestor",
            "phi": "parcela de projecao sum(b_comp * b) / sum(b^2) sobre os 12 coeficientes pre em nivel; phi_of + phi_resto = 1",
            "D": "entradas apos 6 meses de ausencia em t menos saidas confirmadas por 3 meses em t-1",
            "N": "variacao do estoque menos D: retornos apos ausencia curta menos afastamentos curtos (saldo)",
            "d3": "celula com um unico CNES ofertante e y_of > especialistas_mst: so possivel se o co_municipio_gestor dos vinculos nao for o municipio da celula",
        },
        "leituras_fixadas": {
            "d1": f"phi_of >= {LIMIAR_PHI:.4f}: carregada pelos CNES ofertantes; phi_resto >= {LIMIAR_PHI:.4f}: pelo restante do municipio; senao repartida. Diz onde, nao por que",
            "d2": "|dif soma N| > |dif soma D|: intermitente (compativel com cadastro); senao fluxo duradouro (compativel com oferta, sem excluir cadastro em lote)",
            "d3": "ocorrencia e evidencia de artefato de atribuicao cadastral; zero nao prova ausencia",
            "combinada": "assinatura cadastral se d3 > 0 ou d2 intermitente; compativel com oferta se d2 duradouro e d3 = 0",
        },
        "portoes": {
            "estoque_reproduz_tabela_13_pre_F_e_pre_p": True,
            "tolerancia_reproducao_relativa": TOL_REPRODUCAO,
            "tolerancia_reproducao_posto_baixo": TOL_REPRODUCAO_POSTO_BAIXO,
            "posto_minimo_para_portao_estrito": LIMIAR_POSTO_ESTRITO,
            "reproducao_por_curso": {str(c): r1[c]["reproducao_tabela_13"] for c in sorted(r1)},
            "decomposicao_fecha_tolerancia": TOL_DECOMPOSICAO,
            "erro_maximo_decomposicao_observado": float(max(r1[c]["erro_maximo_decomposicao"] for c in r1)),
            "t0_igual_ao_painel_mensal_em_estoque_entradas_saidas": True,
            "cnes_ofertantes_cobrem_587_celulas": True,
            "identidade_dS_igual_D_mais_N": True,
        },
        "cursos_foco": foco,
        "comparacao_outros_oito": {
            str(c): {
                "phi_cnes_ofertantes": r1[c]["phi_cnes_ofertantes"],
                "leitura_d1": r1[c]["leitura_d1"],
                "leitura_d2": r23[c]["leitura_d2"],
                "taxa_intermitencia_curso": r23[c]["taxa_intermitencia_curso"],
                "d3_celula_mes_um_cnes_ofertante_excede_municipal": r23[c]["d3_celula_mes_um_cnes_ofertante_excede_municipal"],
            }
            for c in outros
        },
        "limites": [
            "sem microdados (D-4): reclassificacao de CBO, origem de quem entra, tipo de vinculo, carga horaria e CNES fora dos ofertantes nao sao observaveis",
            "D2 cobre 7 dos 12 coeficientes pre (202412-202505); 202406-202411 ficam sem decomposicao de fluxo",
            "a saida confirmada de 202505 usa presenca ate 202508, antes do T0 administrativo de 202510",
            "N e saldo, nao volume bruto de intermitencia",
            "curso 16: posto incompleto da covariancia das restricoes pre; F pouco confiavel em qualquer componente",
        ],
        "hashes_entradas": hashes,
        "arquivos": {
            "tabela_16": str(TABELA_16.relative_to(ROOT)),
            "tabela_17": str(TABELA_17.relative_to(ROOT)),
        },
    }
    tmp = JSON_SAIDA.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(saida, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(JSON_SAIDA)

    for curso in CURSOS_FOCO:
        f = foco[str(curso)]
        print(
            f"[{ROTULO}] curso {curso}: phi_of {f['d1']['phi_cnes_ofertantes']:.3f} ({f['d1']['leitura_d1']}); "
            f"dif soma D {f['d2']['diferencial_media_soma_D']:+.3f}, dif soma N {f['d2']['diferencial_media_soma_N']:+.3f} ({f['d2']['leitura_d2']}); "
            f"D3 {f['d2']['d3_celula_mes_um_cnes_ofertante_excede_municipal']}; leitura combinada: {f['leitura_combinada']}"
        )


if __name__ == "__main__":
    main()
