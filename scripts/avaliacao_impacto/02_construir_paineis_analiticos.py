"""Valida e publica os painéis analíticos construídos na aquisição.

A agregação individual e a deduplicação ocorrem em
``scripts/aquisicao/05_integrar_painel_analitico.py``. Esta etapa impede que a
estimação prossiga com painel incompleto, duplicado ou fora das definições.
"""

from __future__ import annotations

import json
from pathlib import Path
import shutil

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output"
DEST = OUT / "avaliacao_impacto"
DADOS = DEST / "dados"
RELATORIOS = DEST / "relatorios"

SOURCES = {
    "municipal": OUT / "painel_municipio_curso_mensal.parquet",
    "cnes": OUT / "painel_cnes_especialidade_mensal.parquet",
    "regional": OUT / "painel_regiao_curso_mensal.parquet",
}
DESTINATIONS = {
    "municipal": DADOS / "painel_municipio_curso_mes.parquet",
    "cnes": DADOS / "painel_cnes_curso_mes.parquet",
    "regional": DADOS / "painel_regiao_curso_mes.parquet",
}
AUDIT_FILE = OUT / "aquisicao" / "auditoria_painel_final.json"


def main() -> None:
    DADOS.mkdir(parents=True, exist_ok=True)
    RELATORIOS.mkdir(parents=True, exist_ok=True)
    with AUDIT_FILE.open("r", encoding="utf-8") as handle:
        audit = json.load(handle)
    if audit.get("status") != "APROVADO_PARA_ESTIMACAO":
        raise RuntimeError("O portão de integridade do painel não aprovou a estimação.")

    for name, source in SOURCES.items():
        if not source.exists():
            raise FileNotFoundError(source)
        dst = DESTINATIONS[name]
        try:
            shutil.copy2(str(source), str(dst))
        except Exception:
            pd.read_parquet(source).to_parquet(dst)

    muni = pd.read_parquet(DESTINATIONS["municipal"])
    cnes = pd.read_parquet(DESTINATIONS["cnes"])
    reg = pd.read_parquet(DESTINATIONS["regional"])
    checks = {
        "26_competencias_municipais": int(muni["competencia"].nunique()) == 26,
        "municipal_sem_duplicatas": not muni.duplicated(["co_ibge_6d", "cod_curso", "competencia"]).any(),
        "cnes_sem_duplicatas": not cnes.duplicated(["co_cnes_7d", "cod_curso", "competencia"]).any(),
        "regional_sem_duplicatas": not reg.duplicated(["region_id", "cod_curso", "competencia"]).any(),
        "outcome_primario_presente": "especialistas_mst" in muni.columns,
        "mecanismos_com_censura": bool(muni["n_entradas_6m"].isna().any() and muni["n_saidas_confirmadas_3m"].isna().any()),
    }
    if not all(checks.values()):
        raise RuntimeError(f"Validação dos painéis falhou: {[k for k, v in checks.items() if not v]}")

    cells = muni.drop_duplicates(["co_ibge_6d", "cod_curso"])
    report = {
        "status": "APROVADO",
        "periodo": {"inicio": str(muni["competencia"].min()), "fim": str(muni["competencia"].max()), "meses": 26},
        "painel_municipal": {
            "linhas": int(len(muni)),
            "municipios": int(muni["co_ibge_6d"].nunique()),
            "celulas": int(len(cells)),
            "celulas_confirmatorias": int(cells["amostra_confirmatoria"].sum()),
            "municipios_identificadores_confirmatorios": int(cells.loc[cells["within_muni_var_confirmatoria"], "co_ibge_6d"].nunique()),
            "modalidades": {str(k): int(v) for k, v in cells["modalidade_ms"].value_counts().items()},
        },
        "painel_cnes": {"linhas": int(len(cnes)), "cnes": int(cnes["co_cnes_7d"].nunique())},
        "painel_regional": {"linhas": int(len(reg)), "regioes": int(reg["region_id"].nunique())},
        "checks": checks,
        "observacao": "O painel municipal usa todos os CNES dos municípios e deduplica CO_PROFISSIONAL_SUS; CNES e região são diagnósticos, não novos estimandos causais.",
    }
    out = RELATORIOS / "02_relatorio_painel_amostra.json"
    with out.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(f"[OK] Painéis validados. Amostra confirmatória: {report['painel_municipal']['celulas_confirmatorias']} células.")


if __name__ == "__main__":
    main()
