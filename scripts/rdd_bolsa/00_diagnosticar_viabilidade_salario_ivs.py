"""Diagnóstico de viabilidade do desenho salário–IVS, sem abrir novos outcomes.

O script audita apenas esquema, cobertura, suporte da running variable candidata
e maturidade dos dados. Ele não aprova o RDD e não estima efeitos.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
QUADRO = ROOT / "output" / "aquisicao" / "quadro_vagas_tratamento.parquet"
IVS = ROOT / "data" / "ivs_ipea_2010_municipios.csv"
PAINEL = ROOT / "output" / "avaliacao_impacto" / "dados" / "painel_municipio_curso_mes.parquet"
PONTE = ROOT / "output" / "aquisicao" / "ponte_curso_cbo_oficial.json"
EVENTOS = ROOT / "output" / "aquisicao" / "a02_matriz_eventos_publicos.json"
DOSE = ROOT / "output" / "aquisicao" / "a04_matriz_dose_financeira.json"
PORTAO_ANTERIOR = ROOT / "output" / "avaliacao_impacto" / "relatorios" / "01_relatorio_portao_relevancia.json"
OUT = ROOT / "output" / "rdd_bolsa" / "diagnostico_viabilidade_salario_ivs.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def faixa_2025_candidata(ivs: float) -> str:
    if ivs <= 0.400:
        return "FAIXA 3"
    if ivs <= 0.500:
        return "FAIXA 2"
    return "FAIXA 1"


def suporte(x: pd.Series, cutoff: float, bandwidth: float) -> dict[str, Any]:
    inferior = int(((x >= cutoff - bandwidth) & (x <= cutoff)).sum())
    superior = int(((x >= cutoff + 0.001) & (x <= cutoff + bandwidth)).sum())
    return {
        "cutoff": cutoff,
        "janela": bandwidth,
        "lado_inferior": inferior,
        "lado_superior": superior,
        "total": inferior + superior,
    }


def main() -> None:
    inputs = [QUADRO, IVS, PAINEL, PONTE, EVENTOS, DOSE, PORTAO_ANTERIOR]
    for path in inputs:
        if not path.exists():
            raise FileNotFoundError(path)

    quadro = pd.read_parquet(QUADRO)
    required_offer = {
        "co_ibge_6d",
        "co_cnes_7d",
        "cod_curso",
        "faixa_atracao_anunciada",
        "qt_vagas_total",
    }
    missing = sorted(required_offer - set(quadro.columns))
    if missing:
        raise ValueError(f"Colunas ausentes no quadro de vagas: {missing}")

    municipio = quadro[["co_ibge_6d", "faixa_atracao_anunciada"]].drop_duplicates()
    if municipio["co_ibge_6d"].duplicated().any():
        raise ValueError("Há município com mais de uma faixa anunciada no quadro congelado.")

    ivs = pd.read_csv(IVS, dtype={"cod_ibge6": "string"})
    ivs["cod_ibge6"] = ivs["cod_ibge6"].str.zfill(6)
    municipio = municipio.merge(
        ivs[["cod_ibge6", "ivs_2010"]],
        left_on="co_ibge_6d",
        right_on="cod_ibge6",
        how="left",
        validate="one_to_one",
    )
    municipio["faixa_recalculada_taxonomia_externa"] = municipio["ivs_2010"].map(
        faixa_2025_candidata
    )
    municipio["diverge_faixa"] = (
        municipio["faixa_atracao_anunciada"]
        != municipio["faixa_recalculada_taxonomia_externa"]
    )
    confusion = pd.crosstab(
        municipio["faixa_atracao_anunciada"],
        municipio["faixa_recalculada_taxonomia_externa"],
    )

    support = [
        suporte(municipio["ivs_2010"], cutoff, bandwidth)
        for cutoff in (0.400, 0.500)
        for bandwidth in (0.010, 0.020, 0.030, 0.050)
    ]

    painel = pd.read_parquet(PAINEL)
    bridge = load_json(PONTE)
    events = load_json(EVENTOS)
    dose = load_json(DOSE)
    old_gate = load_json(PORTAO_ANTERIOR)
    event_feasibility = events["avaliacao_spells_e_cobertura"]

    announced_values = {
        int(row["faixa_atracao"]): float(row["valor_anunciado_mensal_brl"])
        for row in dose["grade_anunciada_observada"]
    }
    if set(announced_values) != {1, 2, 3}:
        raise ValueError("Grade anunciada de 2025 incompleta.")

    report: dict[str, Any] = {
        "status": "VIAVEL_COM_NUCLEO_ASSOCIATIVO_E_UPGRADE_CAUSAL_CONDICIONAL",
        "data_referencia": "2026-08-31",
        "natureza": "diagnostico de esquema, cobertura e identificacao; sem nova estimacao de efeito",
        "pergunta_recomendada": (
            "Bolsas maiores conseguem compensar as desvantagens territoriais no "
            "preenchimento e no provimento duradouro de especialistas?"
        ),
        "fontes": {
            str(path.relative_to(ROOT)).replace("\\", "/"): {"sha256": sha256(path)}
            for path in inputs
        },
        "oferta_e_bolsa": {
            "celulas_cnes_curso": int(len(quadro)),
            "municipios": int(municipio["co_ibge_6d"].nunique()),
            "cursos": int(quadro["cod_curso"].nunique()),
            "vagas_publicadas": int(quadro["qt_vagas_total"].sum()),
            "vagas_imediatas_publicadas": int(quadro["qt_vagas_imediatas"].sum()),
            "vagas_reserva_publicadas": int(quadro["qt_vagas_reserva"].sum()),
            "celulas_por_modalidade_original": {
                str(k): int(v) for k, v in quadro["modalidade_original"].value_counts().items()
            },
            "faixa_completa_pct": float(100 * quadro["faixa_atracao_anunciada"].notna().mean()),
            "municipios_por_faixa": {
                str(k): int(v)
                for k, v in municipio["faixa_atracao_anunciada"].value_counts().items()
            },
            "valor_anunciado_mensal_brl_por_faixa": announced_values,
            "valor_devido_observado": False,
            "valor_pago_vinculavel_observado": False,
        },
        "running_variable": {
            "ivs_local_cobertura_municipios_pct": float(100 * municipio["ivs_2010"].notna().mean()),
            "municipios_faixa_reproduzida": int((~municipio["diverge_faixa"]).sum()),
            "municipios_faixa_divergente": int(municipio["diverge_faixa"].sum()),
            "matriz_anunciada_vs_recalculada": {
                str(row): {str(col): int(confusion.loc[row, col]) for col in confusion.columns}
                for row in confusion.index
            },
            "suporte_preliminar_nao_autorizativo": support,
            "portao_rdd": "BLOQUEADO_R1_REGRA_E_ESCORE_NAO_RECONSTRUIDOS",
            "nota": (
                "O IVS local é candidato analítico, não o escore administrativo comprovado. "
                "As divergências não são variação exógena utilizável."
            ),
        },
        "preenchimento": {
            "status": "PARCIALMENTE_OBSERVAVEL",
            "descricao": event_feasibility["componentes_mensuraveis_vs_inobservaveis"][
                "preenchimento_inicial"
            ],
            "portao_imediata_reserva_anterior": old_gate["status_portao"],
            "universo_inscricoes_completo": False,
            "tempo_ate_preenchimento": "INOBSERVAVEL_SEM_LOG_DE_EVENTOS",
        },
        "cnes": {
            "competencia_inicial": str(painel["competencia"].min()),
            "competencia_final": str(painel["competencia"].max()),
            "competencias": int(painel["competencia"].nunique()),
            "municipios": int(painel["co_ibge_6d"].nunique()),
            "celulas_municipio_curso": int(
                painel[["co_ibge_6d", "cod_curso"]].drop_duplicates().shape[0]
            ),
            "cursos_com_ponte_sem_sobreposicao": int(
                len(bridge["cursos_estritamente_univocos"])
            ),
            "oferta_local_agregada_6m": "OBSERVAVEL_COM_CENSURA_EXPLICITA",
            "presenca_12m_coorte_entrantes_ate_202601": "AGUARDA_CNES_202701",
            "retencao_individual_bolsista": "NAO_IDENTIFICADA_SEM_PONTE_ADMINISTRATIVA",
            "nota": (
                "O CNES mede vínculo cadastral agregado. Não prova ocupação contínua da vaga, "
                "participação no PMM-E, atividade física ou pagamento."
            ),
        },
        "spells_individuais": {
            "viavel_com_fontes_publicas": bool(event_feasibility["viabilidade_spells_publicos"]),
            "bloqueios": event_feasibility["razoes_bloqueio_spells"],
            "permanencia": event_feasibility["componentes_mensuraveis_vs_inobservaveis"][
                "permanencia"
            ],
            "reocupacao": event_feasibility["componentes_mensuraveis_vs_inobservaveis"][
                "reocupacao"
            ],
        },
        "decisao_por_modulo": {
            "econometria_associativa_preenchimento": "VIAVEL_COM_LIMITES_DE_DENOMINADOR",
            "gradiente_ivs": "VIAVEL_COMO_ASSOCIACAO_TERRITORIAL",
            "efeito_causal_do_ivs": "NAO_E_ESTIMANDO_DEFENSAVEL",
            "efeito_causal_adicional_bolsa": "CONDICIONADO_A_R1_R2_R3",
            "oferta_local_persistente_6m_cnes": "VIAVEL_COMO_OUTCOME_AGREGADO",
            "retencao_individual_6m_12m": "BLOQUEADA_SEM_ID_VAGA_E_ID_PROFISSIONAL_ESTAVEIS",
            "dose_financeira_recebida": "BLOQUEADA_SEM_FOLHA_MENSAL_VINCULAVEL",
            "sih_sia": "FORA_DO_NUCLEO_E_CONDICIONADO_A_PRIMEIRO_ESTAGIO",
        },
        "veredito": {
            "trabalho_econometrico_relevante": True,
            "avaliacao_causal_rdd_garantida": False,
            "piso_publicavel": (
                "análise econométrica de implementação, preenchimento parcial e gradiente "
                "territorial, com linguagem associativa"
            ),
            "upgrade_causal": (
                "efeito local da oferta de R$ 5 mil adicionais, somente após reconstrução "
                "do escore e da regra e congelamento do protocolo"
            ),
        },
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    temporary = OUT.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(OUT)
    print(
        "[OK] Viabilidade: núcleo associativo viável; RDD bloqueado; "
        f"{report['running_variable']['municipios_faixa_divergente']} divergências de faixa."
    )


if __name__ == "__main__":
    main()
