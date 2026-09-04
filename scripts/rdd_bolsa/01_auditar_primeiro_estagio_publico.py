"""Audita o primeiro estágio público entre o IVS 2010 e a bolsa anunciada.

O exercício é deliberadamente diagnóstico. Ele verifica se a faixa publicada
salta nos limites externos da taxonomia do IVS, mas não substitui a confirmação
do escore administrativo nem autoriza, sozinho, uma interpretação causal.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm


ROOT = Path(__file__).resolve().parents[2]
QUADRO = ROOT / "output" / "aquisicao" / "quadro_vagas_tratamento.parquet"
IVS = ROOT / "data" / "ivs_ipea_2010_municipios.csv"
OUT_DIR = ROOT / "output" / "rdd_bolsa"
OUT_CSV = OUT_DIR / "a01_primeiro_estagio_publico.csv"
OUT_JSON = OUT_DIR / "a01_primeiro_estagio_publico.json"

VALOR_POR_FAIXA = {
    "FAIXA 1": 20_000.0,
    "FAIXA 2": 15_000.0,
    "FAIXA 3": 10_000.0,
}


def _estimativa_local_linear(
    frame: pd.DataFrame, boundary: float, bandwidth: float
) -> dict[str, float | int]:
    sample = frame.loc[
        frame["ivs_2010"].between(boundary - bandwidth, boundary + bandwidth)
    ].copy()
    sample["acima"] = (sample["ivs_2010"] >= boundary).astype(float)
    sample["x_c"] = sample["ivs_2010"] - boundary
    sample["acima_x_c"] = sample["acima"] * sample["x_c"]

    n_abaixo = int((sample["acima"] == 0).sum())
    n_acima = int((sample["acima"] == 1).sum())
    if min(n_abaixo, n_acima) < 2:
        raise ValueError(
            f"Suporte insuficiente em boundary={boundary}, bandwidth={bandwidth}."
        )

    design = sm.add_constant(sample[["acima", "x_c", "acima_x_c"]])
    weights = np.maximum(0.0, 1.0 - sample["x_c"].abs() / bandwidth)
    model = sm.WLS(sample["valor_anunciado_mensal_brl"] / 1_000, design, weights=weights)
    fit = model.fit(cov_type="HC1")

    media_abaixo = float(
        sample.loc[sample["acima"] == 0, "valor_anunciado_mensal_brl"].mean()
        / 1_000
    )
    media_acima = float(
        sample.loc[sample["acima"] == 1, "valor_anunciado_mensal_brl"].mean()
        / 1_000
    )
    return {
        "corte_taxonomia": float(boundary - 0.0005),
        "fronteira_discreta": boundary,
        "bandwidth": bandwidth,
        "n_abaixo": n_abaixo,
        "n_acima": n_acima,
        "n_total": int(len(sample)),
        "media_abaixo_mil_brl": media_abaixo,
        "media_acima_mil_brl": media_acima,
        "diferenca_bruta_mil_brl": media_acima - media_abaixo,
        "salto_local_linear_mil_brl": float(fit.params["acima"]),
        "erro_padrao_hc1_mil_brl": float(fit.bse["acima"]),
        "p_valor": float(fit.pvalues["acima"]),
    }


def main() -> None:
    quadro = pd.read_parquet(QUADRO)
    municipios = quadro[["co_ibge_6d", "faixa_atracao_anunciada"]].drop_duplicates()
    if municipios["co_ibge_6d"].duplicated().any():
        raise ValueError("Há município com mais de uma faixa anunciada no quadro de 2025.")

    ivs = pd.read_csv(IVS, dtype={"cod_ibge6": "string"})
    ivs["cod_ibge6"] = ivs["cod_ibge6"].str.zfill(6)
    municipios = municipios.merge(
        ivs[["cod_ibge6", "ivs_2010"]],
        left_on="co_ibge_6d",
        right_on="cod_ibge6",
        how="left",
        validate="one_to_one",
    )
    if municipios["ivs_2010"].isna().any():
        raise ValueError("Há município do quadro de vagas sem IVS 2010 local.")

    municipios["valor_anunciado_mensal_brl"] = municipios[
        "faixa_atracao_anunciada"
    ].map(VALOR_POR_FAIXA)
    if municipios["valor_anunciado_mensal_brl"].isna().any():
        raise ValueError("Há faixa anunciada sem valor mapeado.")

    estimativas = [
        _estimativa_local_linear(municipios, boundary, bandwidth)
        for boundary in (0.4005, 0.5005)
        for bandwidth in (0.010, 0.020, 0.030, 0.050, 0.080)
    ]
    tabela = pd.DataFrame(estimativas)

    cruzamento = pd.crosstab(
        municipios["faixa_atracao_anunciada"],
        pd.cut(
            municipios["ivs_2010"],
            bins=[-np.inf, 0.400, 0.500, np.inf],
            labels=["ivs_ate_0_400", "ivs_0_401_a_0_500", "ivs_acima_0_500"],
        ),
    )
    relatorio = {
        "status": "DIAGNOSTICO_NAO_AUTORIZATIVO",
        "unidade": "municipio com vaga publicada no ciclo 1 de 2025",
        "n_municipios": int(len(municipios)),
        "tratamento": "valor mensal anunciado, em milhares de reais",
        "running_variable_candidata": "IVS Ipea 2010 disponível localmente",
        "nota_fronteira": (
            "Como o IVS observado tem três casas decimais, a fronteira numérica entre "
            "0,400 e 0,401 é representada por 0,4005. O mesmo vale para 0,500/0,501."
        ),
        "matriz_faixa_anunciada_por_intervalo_ivs": {
            str(row): {str(col): int(cruzamento.loc[row, col]) for col in cruzamento.columns}
            for row in cruzamento.index
        },
        "estimativas": estimativas,
        "interpretacao": (
            "Um salto anunciado robusto é condição necessária para uma RDD fuzzy pública, "
            "mas não suficiente. Ainda é preciso justificar institucionalmente que o corte "
            "da taxonomia afeta a faixa, auditar continuidade das covariáveis e excluir "
            "ou documentar outros componentes que também mudem no mesmo corte."
        ),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tabela.to_csv(OUT_CSV, index=False)
    OUT_JSON.write_text(
        json.dumps(relatorio, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(tabela.to_string(index=False))


if __name__ == "__main__":
    main()
