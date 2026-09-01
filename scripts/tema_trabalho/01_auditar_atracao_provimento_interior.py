"""Audita a viabilidade do tema atração e provimento no interior.

Esta rotina não estima efeitos. Ela reconcilia, em nível agregado, a oferta
inicial do ciclo 1 com as listas públicas de alocação e homologação e verifica
o suporte temporal do painel CNES. O objetivo é decidir quais perguntas podem
ser prometidas antes da pré-análise.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
QUADRO = ROOT / "output" / "aquisicao" / "quadro_vagas_tratamento.parquet"
ALOCACAO = (
    ROOT
    / "data"
    / "raw"
    / "aquisicao"
    / "vagas"
    / "2025_ciclo1_chamada1_alocacao_retificada.xlsx"
)
HOMOLOGADOS = (
    ROOT
    / "data"
    / "raw"
    / "pmm_e"
    / "2025_ciclo1_chamada1_homologados.xlsx"
)
PAINEL_CNES = (
    ROOT
    / "output"
    / "avaliacao_impacto"
    / "dados"
    / "painel_municipio_curso_mes.parquet"
)
DIAGNOSTICO_RDD = (
    ROOT / "output" / "rdd_bolsa" / "diagnostico_viabilidade_salario_ivs.json"
)
OUT_DIR = ROOT / "output" / "tema_trabalho"
OUT_JSON = OUT_DIR / "diagnostico_atracao_provimento_interior.json"


# Definição operacional mínima e auditável. Não equivale a ruralidade,
# remoticidade ou exclusão de região metropolitana.
CAPITAIS_IBGE6 = {
    "110020",  # Porto Velho
    "120040",  # Rio Branco
    "130260",  # Manaus
    "140010",  # Boa Vista
    "150140",  # Belém
    "160030",  # Macapá
    "172100",  # Palmas
    "211130",  # São Luís
    "221100",  # Teresina
    "230440",  # Fortaleza
    "240810",  # Natal
    "250750",  # João Pessoa
    "261160",  # Recife
    "270430",  # Maceió
    "280030",  # Aracaju
    "292740",  # Salvador
    "310620",  # Belo Horizonte
    "320530",  # Vitória
    "330455",  # Rio de Janeiro
    "355030",  # São Paulo
    "410690",  # Curitiba
    "420540",  # Florianópolis
    "431490",  # Porto Alegre
    "500270",  # Campo Grande
    "510340",  # Cuiabá
    "520870",  # Goiânia
    "530010",  # Brasília
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_id(value: object, width: int) -> str:
    if pd.isna(value):
        return ""
    digits = re.sub(r"\D", "", str(value))
    if not digits:
        return ""
    return digits[:width].zfill(width)


def course_id(value: object) -> int | None:
    if pd.isna(value):
        return None
    match = re.match(r"^\s*(\d{1,2})", str(value))
    if not match:
        return None
    parsed = int(match.group(1))
    return parsed if 1 <= parsed <= 16 else None


def find_column(frame: pd.DataFrame, fragment: str) -> str:
    matches = [column for column in frame.columns if fragment in str(column).upper()]
    if len(matches) != 1:
        raise ValueError(f"Coluna contendo {fragment!r}: encontradas {matches}")
    return matches[0]


def territory(code: object) -> str:
    return "capital" if normalize_id(code, 6) in CAPITAIS_IBGE6 else "fora_capital"


def rate(numerator: float, denominator: float) -> float | None:
    return float(numerator / denominator) if denominator else None


def summarize_offer(group: pd.DataFrame) -> dict[str, Any]:
    immediate = group[group["qt_vagas_imediatas"] > 0]
    return {
        "municipios_oferta": int(group["co_ibge_6d"].nunique()),
        "municipios_vaga_imediata": int(immediate["co_ibge_6d"].nunique()),
        "celulas_cnes_curso": int(len(group)),
        "celulas_com_vaga_imediata": int(len(immediate)),
        "vagas_imediatas": int(immediate["qt_vagas_imediatas"].sum()),
        "alocacoes_confirmadas_compativeis": int(immediate["n_alocados_confirmados"].sum()),
        "homologacoes_compativeis": int(immediate["n_homologados"].sum()),
        "taxa_alocacao_sobre_vagas_imediatas": rate(
            immediate["n_alocados_confirmados"].sum(),
            immediate["qt_vagas_imediatas"].sum(),
        ),
        "taxa_homologacao_sobre_vagas_imediatas": rate(
            immediate["n_homologados"].sum(),
            immediate["qt_vagas_imediatas"].sum(),
        ),
    }


def load_public_outcome(
    path: Path,
    *,
    outcome_name: str,
    confirmed_only: bool,
) -> pd.DataFrame:
    frame = pd.read_excel(path, dtype=object)
    cnes_col = find_column(frame, "CNES")
    course_col = find_column(frame, "CURSO")
    frame["co_cnes_7d"] = frame[cnes_col].map(lambda value: normalize_id(value, 7))
    frame["cod_curso"] = frame[course_col].map(course_id)

    if confirmed_only:
        allocation_col = find_column(frame, "ALOCA")
        normalized = frame[allocation_col].fillna("").astype(str).str.upper()
        frame = frame[
            normalized.str.contains("LOCAL DE ATUA", regex=False)
            & normalized.str.contains("CONFIRMADO", regex=False)
        ].copy()

    frame = frame[(frame["co_cnes_7d"] != "") & frame["cod_curso"].notna()].copy()
    frame["cod_curso"] = frame["cod_curso"].astype(int)
    return (
        frame.groupby(["co_cnes_7d", "cod_curso"], as_index=False)
        .size()
        .rename(columns={"size": outcome_name})
    )


def main() -> None:
    inputs = [QUADRO, ALOCACAO, HOMOLOGADOS, PAINEL_CNES, DIAGNOSTICO_RDD]
    for path in inputs:
        if not path.exists():
            raise FileNotFoundError(path)

    offer = pd.read_parquet(QUADRO).copy()
    offer["co_ibge_6d"] = offer["co_ibge_6d"].map(lambda value: normalize_id(value, 6))
    offer["co_cnes_7d"] = offer["co_cnes_7d"].map(lambda value: normalize_id(value, 7))
    offer["territorio_operacional"] = offer["co_ibge_6d"].map(territory)

    allocations = load_public_outcome(
        ALOCACAO,
        outcome_name="n_alocados_confirmados",
        confirmed_only=True,
    )
    homologations = load_public_outcome(
        HOMOLOGADOS,
        outcome_name="n_homologados",
        confirmed_only=False,
    )

    keys = ["co_cnes_7d", "cod_curso"]
    offer_keys = offer[keys].drop_duplicates()
    allocation_check = allocations.merge(offer_keys, on=keys, how="left", indicator=True)
    homologation_check = homologations.merge(offer_keys, on=keys, how="left", indicator=True)

    offer = offer.merge(allocations, on=keys, how="left", validate="one_to_one")
    offer = offer.merge(homologations, on=keys, how="left", validate="one_to_one")
    offer[["n_alocados_confirmados", "n_homologados"]] = offer[
        ["n_alocados_confirmados", "n_homologados"]
    ].fillna(0).astype(int)

    immediate = offer[offer["qt_vagas_imediatas"] > 0].copy()
    capacity_violations = immediate[
        immediate["n_alocados_confirmados"] > immediate["qt_vagas_imediatas"]
    ]
    homologation_capacity_violations = immediate[
        immediate["n_homologados"] > immediate["qt_vagas_imediatas"]
    ]

    offer_by_territory = {
        label: summarize_offer(group)
        for label, group in offer.groupby("territorio_operacional", sort=True)
    }
    offer_by_territory["total"] = summarize_offer(offer)
    offer_by_modality = {
        str(label): {
            "celulas_cnes_curso": int(len(group)),
            "vagas_imediatas": int(group["qt_vagas_imediatas"].sum()),
            "vagas_reserva": int(group["qt_vagas_reserva"].sum()),
            "alocacoes_confirmadas": int(group["n_alocados_confirmados"].sum()),
            "homologacoes": int(group["n_homologados"].sum()),
        }
        for label, group in offer.groupby("modalidade_original", sort=True)
    }

    municipality_course = (
        offer.groupby(
            [
                "co_ibge_6d",
                "cod_curso",
                "territorio_operacional",
                "faixa_atracao_anunciada",
            ],
            as_index=False,
        )[
            [
                "qt_vagas_imediatas",
                "qt_vagas_reserva",
                "n_alocados_confirmados",
                "n_homologados",
            ]
        ]
        .sum()
    )

    panel = pd.read_parquet(PAINEL_CNES).copy()
    panel["co_ibge_6d"] = panel["co_ibge_6d"].map(lambda value: normalize_id(value, 6))
    panel["territorio_operacional"] = panel["co_ibge_6d"].map(territory)
    panel["competencia"] = panel["competencia"].astype(str)
    matured = panel[panel["coorte_6m_madura"].fillna(False)].copy()
    matured_post_publication = matured[matured["post_t"] == 1].copy()
    latest = panel[panel["competencia"] == panel["competencia"].max()].copy()

    panel_by_territory: dict[str, Any] = {}
    for label, group in panel.groupby("territorio_operacional", sort=True):
        mature_group = matured[matured["territorio_operacional"] == label]
        mature_post_group = matured_post_publication[
            matured_post_publication["territorio_operacional"] == label
        ]
        latest_group = latest[latest["territorio_operacional"] == label]
        panel_by_territory[label] = {
            "municipios": int(group["co_ibge_6d"].nunique()),
            "celulas_municipio_curso": int(
                group[["co_ibge_6d", "cod_curso"]].drop_duplicates().shape[0]
            ),
            "competencias": int(group["competencia"].nunique()),
            "linhas_coorte_6m_madura": int(len(mature_group)),
            "municipios_com_coorte_6m_madura": int(mature_group["co_ibge_6d"].nunique()),
            "celulas_com_coorte_6m_madura": int(
                mature_group[["co_ibge_6d", "cod_curso"]].drop_duplicates().shape[0]
            ),
            "linhas_pos_publicacao_com_coorte_6m_madura": int(len(mature_post_group)),
            "competencias_pos_publicacao_com_coorte_6m_madura": sorted(
                mature_post_group["competencia"].unique().tolist()
            ),
            "celulas_com_especialista_na_ultima_competencia": int(
                (latest_group["especialistas_mst"] > 0).sum()
            ),
            "ultima_competencia": str(group["competencia"].max()),
        }

    rdd = json.loads(DIAGNOSTICO_RDD.read_text(encoding="utf-8"))

    module_rows = [
        {
            "modulo": "oferta",
            "status": "VIAVEL",
            "evidencia": (
                f"{len(offer)} células CNES-curso, "
                f"{offer['co_ibge_6d'].nunique()} municípios e "
                f"{int(offer['qt_vagas_imediatas'].sum())} vagas imediatas"
            ),
            "linguagem_maxima": "oferta publicada",
        },
        {
            "modulo": "atracao_alocacao",
            "status": "VIAVEL_COM_RECONCILIACAO",
            "evidencia": (
                f"{int(allocations['n_alocados_confirmados'].sum())} alocações confirmadas; "
                f"{int((allocation_check['_merge'] != 'both').sum())} células sem chave na oferta original"
            ),
            "linguagem_maxima": "preenchimento administrativo, não universo de procura",
        },
        {
            "modulo": "homologacao",
            "status": "VIAVEL_COM_RECONCILIACAO",
            "evidencia": (
                f"{int(homologations['n_homologados'].sum())} homologações; "
                f"{int((homologation_check['_merge'] != 'both').sum())} células sem chave na oferta original"
            ),
            "linguagem_maxima": "homologação, não início em atividade",
        },
        {
            "modulo": "procura_candidaturas",
            "status": "BLOQUEADO",
            "evidencia": "lista publicada não comprova o universo de inscrições válidas",
            "linguagem_maxima": "não estimar candidaturas por vaga sem A07-02",
        },
        {
            "modulo": "interior",
            "status": "VIAVEL_COM_DEFINICAO_MINIMA",
            "evidencia": "código municipal permite separar capitais e não capitais",
            "linguagem_maxima": "fora das capitais; interior remoto exige tipologia adicional",
        },
        {
            "modulo": "oferta_local_cnes",
            "status": "VIAVEL_AGREGADO",
            "evidencia": (
                f"{panel['competencia'].nunique()} competências, "
                f"{panel['co_ibge_6d'].nunique()} municípios e "
                f"{panel[['co_ibge_6d', 'cod_curso']].drop_duplicates().shape[0]} células"
            ),
            "linguagem_maxima": "persistência da oferta médica local",
        },
        {
            "modulo": "retencao_individual_bolsista",
            "status": "BLOQUEADO",
            "evidencia": "sem ponte PMM-E-CNES e sem spells administrativos completos",
            "linguagem_maxima": "não chamar estoque ou presença cadastral de retenção do bolsista",
        },
        {
            "modulo": "rdd_bolsa",
            "status": "BLOQUEADO_R1",
            "evidencia": (
                f"{rdd['running_variable']['municipios_faixa_divergente']} de "
                f"{rdd['oferta_e_bolsa']['municipios']} municípios divergem da regra candidata"
            ),
            "linguagem_maxima": "upgrade causal somente após R1-R3",
        },
    ]

    report: dict[str, Any] = {
        "protocolo": "AUDITORIA_TEMA_ATRACAO_PROVIMENTO_INTERIOR",
        "data_referencia": "2026-08-31",
        "efeitos_estimados": False,
        "pergunta_recomendada": (
            "Em que medida as vagas do primeiro ciclo do PMM-E foram preenchidas fora "
            "das capitais, quais características territoriais estão associadas ao "
            "preenchimento e se ele foi acompanhado por persistência da oferta médica local?"
        ),
        "definicao_territorial": {
            "principal_atual": "fora_capital = município cujo código IBGE não pertence às 27 capitais",
            "limite": (
                "não capital não significa necessariamente interior remoto; municípios "
                "metropolitanos permanecem neste grupo"
            ),
            "upgrade_planejado": (
                "tipologia capital/região metropolitana/interior próximo/interior remoto, "
                "congelada antes da estimação"
            ),
        },
        "fontes": {
            str(path.relative_to(ROOT)).replace("\\", "/"): {"sha256": sha256(path)}
            for path in inputs
        },
        "oferta_e_resultados_publicos": {
            "por_territorio": offer_by_territory,
            "por_modalidade_original": offer_by_modality,
            "celulas_municipio_curso": int(len(municipality_course)),
            "alocacoes_confirmadas_publicadas": int(
                allocations["n_alocados_confirmados"].sum()
            ),
            "alocacoes_confirmadas_em_chave_da_oferta_original": int(
                allocation_check.loc[
                    allocation_check["_merge"] == "both", "n_alocados_confirmados"
                ].sum()
            ),
            "celulas_alocacao_sem_chave_da_oferta_original": int(
                (allocation_check["_merge"] != "both").sum()
            ),
            "homologacoes_publicadas": int(homologations["n_homologados"].sum()),
            "homologacoes_em_chave_da_oferta_original": int(
                homologation_check.loc[
                    homologation_check["_merge"] == "both", "n_homologados"
                ].sum()
            ),
            "celulas_homologacao_sem_chave_da_oferta_original": int(
                (homologation_check["_merge"] != "both").sum()
            ),
            "celulas_alocacao_acima_da_capacidade_publicada": int(len(capacity_violations)),
            "celulas_homologacao_acima_da_capacidade_publicada": int(
                len(homologation_capacity_violations)
            ),
            "nota": (
                "A lista de alocação fecha nas chaves CNES-curso da oferta, mas 211 "
                "confirmações pertencem a células originalmente só de reserva. As taxas "
                "sobre vagas imediatas são apenas diagnóstico e não devem ser promovidas "
                "a preenchimento antes de reconciliar versões, reapresentações e capacidade."
            ),
        },
        "painel_cnes": {
            "competencia_inicial": str(panel["competencia"].min()),
            "competencia_final": str(panel["competencia"].max()),
            "por_territorio": panel_by_territory,
            "cursos_sem_sobreposicao_cbo": int(
                panel.loc[panel["curso_sem_sobreposicao"], "cod_curso"].nunique()
            ),
            "retencao_individual_identificada": False,
            "horizonte_seis_meses_apos_homologacao": (
                "tecnicamente coberto até 2026-07; o T0 físico ainda deve ser validado"
            ),
            "interpretação": (
                "o painel sustenta outcomes agregados de estoque, entrada e presença "
                "posterior; não identifica o bolsista nem a permanência na vaga"
            ),
        },
        "decisao_por_modulo": module_rows,
        "veredito": {
            "tema_faz_sentido": True,
            "formulacao_defensavel": (
                "atração administrativa e persistência da oferta médica local fora das capitais"
            ),
            "formulacao_nao_defensavel_hoje": (
                "efeito total do PMM-E na atração e retenção individual de médicos do interior"
            ),
            "nucleo_garantido": "econometria associativa de implementação e preenchimento",
            "upgrade_causal": "RDD do adicional da bolsa condicionado a R1-R3",
        },
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tmp = OUT_JSON.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(OUT_JSON)

    print(
        "[OK] Tema auditado: atração administrativa e oferta local agregada são viáveis; "
        "retenção individual e RDD permanecem bloqueadas."
    )


if __name__ == "__main__":
    main()
