"""Executa o portão R1 público da RDD da bolsa, sem abrir outcomes.

O IVS Ipea 2010 disponível no repositório é tratado apenas como candidato à
running variable administrativa. O script produz uma matriz municipal
auditável e reprova o portão quando a faixa publicada não é integralmente
reproduzida. A reprovação é deliberadamente fail-closed: ela impede R2--R4,
mas não afirma que o desenho seria inviável com o escore administrativo real.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
QUADRO = ROOT / "output" / "aquisicao" / "quadro_vagas_tratamento.parquet"
IVS = ROOT / "data" / "ivs_ipea_2010_municipios.csv"
OUT_DIR = ROOT / "output" / "rdd_bolsa"
OUT_MATRIX = OUT_DIR / "matriz_municipio_regra_ivs.csv"
OUT_GATE = OUT_DIR / "portao_regra_ivs.json"
OUT_REPORT = ROOT / "docs" / "auditorias" / "07_portao_rdd_bolsa.md"

VALOR_POR_FAIXA = {
    "FAIXA 1": 20_000,
    "FAIXA 2": 15_000,
    "FAIXA 3": 10_000,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def faixa_taxonomia_externa(ivs: float) -> str:
    """Mapeamento candidato do Atlas; não representa regra PMM-E comprovada."""

    if ivs <= 0.400:
        return "FAIXA 3"
    if ivs <= 0.500:
        return "FAIXA 2"
    return "FAIXA 1"


def atomic_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(value, encoding="utf-8")
    temporary.replace(path)


def atomic_csv(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    frame.to_csv(temporary, index=False, encoding="utf-8")
    temporary.replace(path)


def _matriz_cruzamento(frame: pd.DataFrame) -> dict[str, dict[str, int]]:
    crossing = pd.crosstab(
        frame["faixa_anunciada"], frame["faixa_recalculada_taxonomia_externa"]
    ).reindex(index=VALOR_POR_FAIXA, columns=VALOR_POR_FAIXA, fill_value=0)
    return {
        row: {column: int(crossing.loc[row, column]) for column in crossing.columns}
        for row in crossing.index
    }


def _relatorio_markdown(report: dict[str, Any]) -> str:
    crossing = report["diagnostico_publico"]["matriz_faixa_anunciada_por_recalculada"]
    lines = [
        "# Portão R1 — regra administrativa da bolsa pelo IVS",
        "",
        f"> **Execução:** {report['data_execucao']}.",
        f"> **Decisão:** `{report['decisao_r1']}`.",
        "> Este portão usa o IVS público apenas como candidato e não abre outcomes de atração.",
        "",
        "## Resultado",
        "",
        (
            f"Foram auditados {report['diagnostico_publico']['n_municipios']} municípios "
            f"com ofertas do ciclo 1 de 2025. A taxonomia externa reproduz "
            f"{report['diagnostico_publico']['n_reproduzidos']} faixas e diverge em "
            f"{report['diagnostico_publico']['n_divergentes']} "
            f"({report['diagnostico_publico']['pct_divergentes']:.1f}%)."
        ),
        "",
        "| Faixa anunciada | Recalculada 1 | Recalculada 2 | Recalculada 3 |",
        "|---|---:|---:|---:|",
    ]
    for row in VALOR_POR_FAIXA:
        lines.append(
            f"| {row.title()} | {crossing[row]['FAIXA 1']} | "
            f"{crossing[row]['FAIXA 2']} | {crossing[row]['FAIXA 3']} |"
        )
    lines.extend(
        [
            "",
            "A correspondência não chega a 100% e as divergências não possuem exceção "
            "normativa prévia identificada. Além disso, o arquivo público não prova a "
            "vintagem, a precisão, o arredondamento nem o escore efetivamente usado pela "
            "SGTES/MS. Portanto, R1 está reprovado com os dados públicos atuais.",
            "",
            "## Consequência econométrica",
            "",
            "- R2, R3 e R4 permanecem bloqueados; nenhum outcome é consultado por este módulo.",
            "- A matriz pública é diagnóstico de incompatibilidade, não instrumento fuzzy.",
            "- A RDD pode ser reaberta apenas com escore e regra administrativos, ou com "
            "exceções normativas previamente documentadas.",
            "",
            "## Dados que destravam R1",
            "",
            "1. escore IVS aplicado em sua precisão original;",
            "2. vintagem e arquivo de origem;",
            "3. arredondamento e inclusão nos cutoffs;",
            "4. categoria, faixa, valor, vigência e exceções por vaga ou município;",
            "5. histórico de versões e fontes administrativas.",
            "",
            "A especificação do pedido está em "
            "[`docs/pedidos_dados/vagas_e_regra_ivs.md`](../pedidos_dados/vagas_e_regra_ivs.md).",
            "",
            "## Artefatos reproduzíveis",
            "",
            "- `output/rdd_bolsa/matriz_municipio_regra_ivs.csv`;",
            "- `output/rdd_bolsa/portao_regra_ivs.json`;",
            "- `scripts/rdd_bolsa/01_auditar_regra_e_suporte.py`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    for path in (QUADRO, IVS):
        if not path.exists():
            raise FileNotFoundError(path)

    quadro = pd.read_parquet(QUADRO)
    required = {
        "co_ibge_6d",
        "sg_uf",
        "no_municipio",
        "co_cnes_7d",
        "cod_curso",
        "qt_vagas_total",
        "faixa_atracao_anunciada",
    }
    missing = sorted(required - set(quadro.columns))
    if missing:
        raise ValueError(f"Colunas ausentes no quadro de vagas: {missing}")

    quadro = quadro.copy()
    quadro["co_ibge_6d"] = quadro["co_ibge_6d"].astype("string").str.zfill(6)
    faixa_por_municipio = quadro[
        ["co_ibge_6d", "faixa_atracao_anunciada"]
    ].drop_duplicates()
    if faixa_por_municipio["co_ibge_6d"].duplicated().any():
        raise ValueError("Há município com mais de uma faixa anunciada no ciclo 1.")

    municipio = (
        quadro.groupby("co_ibge_6d", as_index=False)
        .agg(
            sg_uf=("sg_uf", "first"),
            no_municipio=("no_municipio", "first"),
            faixa_anunciada=("faixa_atracao_anunciada", "first"),
            n_celulas_publicadas=("cod_curso", "size"),
            n_cursos=("cod_curso", "nunique"),
            n_cnes=("co_cnes_7d", "nunique"),
            qt_vagas_total=("qt_vagas_total", "sum"),
        )
        .sort_values("co_ibge_6d")
        .reset_index(drop=True)
    )
    municipio["valor_anunciado_mensal_brl"] = municipio["faixa_anunciada"].map(
        VALOR_POR_FAIXA
    )
    if municipio["valor_anunciado_mensal_brl"].isna().any():
        invalid = sorted(municipio.loc[
            municipio["valor_anunciado_mensal_brl"].isna(), "faixa_anunciada"
        ].unique())
        raise ValueError(f"Faixas anunciadas sem valor mapeado: {invalid}")

    ivs = pd.read_csv(IVS, dtype={"cod_ibge6": "string"})
    ivs["cod_ibge6"] = ivs["cod_ibge6"].str.zfill(6)
    if ivs["cod_ibge6"].duplicated().any():
        raise ValueError("O arquivo IVS público contém municípios duplicados.")
    municipio = municipio.merge(
        ivs[["cod_ibge6", "ivs_2010"]],
        left_on="co_ibge_6d",
        right_on="cod_ibge6",
        how="left",
        validate="one_to_one",
    ).drop(columns="cod_ibge6")
    if municipio["ivs_2010"].isna().any():
        raise ValueError("Há município ofertante sem IVS público 2010.")

    municipio = municipio.rename(columns={"ivs_2010": "ivs_publico_2010"})
    municipio["faixa_recalculada_taxonomia_externa"] = municipio[
        "ivs_publico_2010"
    ].map(faixa_taxonomia_externa)
    municipio["valor_recalculado_taxonomia_externa_brl"] = municipio[
        "faixa_recalculada_taxonomia_externa"
    ].map(VALOR_POR_FAIXA)
    municipio["reproduz_faixa"] = (
        municipio["faixa_anunciada"]
        == municipio["faixa_recalculada_taxonomia_externa"]
    )
    municipio["reproduz_valor"] = (
        municipio["valor_anunciado_mensal_brl"]
        == municipio["valor_recalculado_taxonomia_externa_brl"]
    )
    municipio["distancia_corte_0_400"] = municipio["ivs_publico_2010"] - 0.400
    municipio["distancia_corte_0_500"] = municipio["ivs_publico_2010"] - 0.500
    municipio["score_administrativo_comprovado"] = False
    municipio["fonte_running_variable"] = "IVS_IPEA_2010_PUBLICO_CANDIDATO"

    reproduced = int(municipio["reproduz_faixa"].sum())
    divergent = int((~municipio["reproduz_faixa"]).sum())
    total = int(len(municipio))
    crossing = _matriz_cruzamento(municipio)
    report: dict[str, Any] = {
        "status": "PORTAO_CAUSAL",
        "data_execucao": date.today().isoformat(),
        "escopo": "ciclo 1, chamada 1, ofertas publicadas em 24/07/2025",
        "unidade_atribuicao": "municipio",
        "outcomes_abertos": False,
        "decisao_r1": "REPROVADO_PENDENTE_DE_RECONSTRUCAO",
        "motivo_decisao": (
            "A taxonomia externa aplicada ao IVS público não reproduz 100% das "
            "faixas anunciadas e não comprova a running variable administrativa."
        ),
        "requisitos_r1": {
            "municipio_escore_faixa_valor_vigencia_completos": False,
            "escore_unico_por_municipio_vigencia": "NAO_AVALIAVEL_SEM_ESCORE_ADMINISTRATIVO",
            "regra_reproduz_100_pct_ou_excecoes_previas": False,
            "tratamento_dos_mass_points_de_cutoff_documentado": False,
            "fontes_e_hashes_preservados": True,
        },
        "diagnostico_publico": {
            "n_municipios": total,
            "n_reproduzidos": reproduced,
            "n_divergentes": divergent,
            "pct_divergentes": 100 * divergent / total,
            "matriz_faixa_anunciada_por_recalculada": crossing,
            "running_variable": "IVS Ipea 2010 público candidato",
            "taxonomia_externa": {
                "ivs_ate_0_400": "FAIXA 3",
                "ivs_0_401_a_0_500": "FAIXA 2",
                "ivs_acima_0_500": "FAIXA 1",
            },
        },
        "fontes": {
            str(QUADRO.relative_to(ROOT)).replace("\\", "/"): {"sha256": sha256(QUADRO)},
            str(IVS.relative_to(ROOT)).replace("\\", "/"): {"sha256": sha256(IVS)},
        },
        "bloqueios_resultantes": {
            "r2": "BLOQUEADO_POR_R1",
            "r3": "BLOQUEADO_POR_R1",
            "r4": "BLOQUEADO_POR_R1",
            "r5": "BLOQUEADO_POR_R1",
        },
        "proximo_passo": (
            "Submeter o pedido focal de escore/regra e repetir R1 com o pacote "
            "administrativo, preservando exceções documentadas antes dos outcomes."
        ),
    }

    atomic_csv(OUT_MATRIX, municipio)
    atomic_text(OUT_GATE, json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    atomic_text(OUT_REPORT, _relatorio_markdown(report))
    print(
        "[R1 REPROVADO] "
        f"{divergent}/{total} municípios divergem; outcomes não foram abertos."
    )


if __name__ == "__main__":
    main()
