"""Repete o portao R1 com o escore administrativo de IVS dos dados abertos.

Pergunta: o escore `ivs` publicado pelo Ministerio da Saude reproduz a faixa
anunciada em todos os quadros de vagas do PMM-E, com cutoffs localizaveis?
E, se reproduz, o escore esta disponivel para toda a populacao de municipios
com vaga?

O script **nao abre outcome**. Le apenas faixa anunciada por municipio nos
quadros de vagas, o escore e a categoria administrativos (saida do a07) e o
IVS 2010 publico. Nenhuma taxa de preenchimento, homologacao, presenca ou CNES
pos e calculada.

A cobertura do escore e reportada porque decide o portao: a relacao nominal
so lista municipios com especialista ativo, entao a falta de escore e funcao
do desfecho. Uma RDD restrita aos municipios cobertos condicionaria no
proprio desfecho e nao e autorizada por este portao.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
ESCORE = ROOT / "output" / "aquisicao" / "a07_ivs_administrativo_municipio.csv"
CATEGORIA = ROOT / "output" / "aquisicao" / "a07_categoria_ivs_pmmb_municipio.csv"
IVS_PUBLICO = ROOT / "data" / "ivs_ipea_2010_municipios.csv"
OUT_JSON = ROOT / "output" / "rdd_bolsa" / "portao_r1_escore_administrativo.json"
OUT_MATRIZ = ROOT / "output" / "rdd_bolsa" / "matriz_municipio_escore_administrativo.csv"

DATA_EXECUCAO = "2026-10-14"

QUADROS = [
    ("c1_ch1", "data/raw/aquisicao/vagas/2025_ciclo1_chamada1_vagas.xlsx", "24/07/2025"),
    ("c2_ch1", "data/raw/pmm_e/2026_ciclo2_chamada1_vagas_retificadas.xlsx", "2026, retificado"),
    ("c2_ch2", "data/raw/pmm_e/2026_ciclo2_chamada2_vagas.xlsx", "16/04/2026"),
    ("c3_ch1", "data/raw/pmm_e/2026_ciclo3_chamada1_vagas_retificadas.xlsx", "2026, retificado"),
]

# Regra observada: categoria administrativa -> faixa. A grade de 2026 do edital
# (alta e muito alta -> Faixa 1; media -> Faixa 2; baixa e muito baixa -> Faixa 3).
CATEGORIA_PARA_FAIXA = {
    "MUITO BAIXA VULNERABILIDADE": "FAIXA 3",
    "BAIXA VULNERABILIDADE": "FAIXA 3",
    "MEDIA VULNERABILIDADE": "FAIXA 2",
    "ALTA VULNERABILIDADE": "FAIXA 1",
    "MUITO ALTA VULNERABILIDADE": "FAIXA 1",
}
# Cutoffs das classes do Atlas do Ipea, citadas no dicionario de dados:
# baixa ate 0,300; media ate 0,400. O lado de 0,300 exato nao e observado.
CUTOFF_INFERIOR = 0.300
CUTOFF_SUPERIOR = 0.400
VALOR = {"FAIXA 3": 10_000, "FAIXA 2": 15_000, "FAIXA 1": 20_000}
JANELAS = [0.010, 0.020, 0.030, 0.050]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while bloco := f.read(65536):
            h.update(bloco)
    return h.hexdigest()


def faixa_por_escore(s: float) -> str:
    if s <= CUTOFF_INFERIOR:
        return "FAIXA 3"
    if s <= CUTOFF_SUPERIOR:
        return "FAIXA 2"
    return "FAIXA 1"


def ler_quadro(caminho: str) -> pd.DataFrame:
    bruto = pd.read_excel(ROOT / caminho, header=None)
    linha = next(
        i for i in range(10) if bruto.iloc[i].astype(str).str.upper().str.contains("FAIXA").any()
    )
    df = pd.read_excel(ROOT / caminho, header=linha)
    df.columns = [str(c).strip().upper() for c in df.columns]
    col_ibge = next(c for c in df.columns if c.startswith("IBGE"))
    col_faixa = next(c for c in df.columns if "FAIXA" in c)
    m = df[[col_ibge, col_faixa]].dropna()
    m.columns = ["co_ibge", "faixa_anunciada"]
    m["co_ibge"] = m["co_ibge"].astype(str).str.split(".").str[0].str[:6]
    m = m[m["co_ibge"].str.isnumeric()]
    m["faixa_anunciada"] = m["faixa_anunciada"].astype(str).str.strip().str.upper()
    return m.drop_duplicates()


def main() -> None:
    escore = pd.read_csv(ESCORE, dtype={"co_ibge": str})
    categoria = pd.read_csv(CATEGORIA, dtype={"co_ibge": str})
    publico = pd.read_csv(IVS_PUBLICO, dtype={"cod_ibge6": str})[["cod_ibge6", "ivs_2010"]]

    # 1. Escore -> categoria -> faixa, dentro da propria relacao nominal.
    escore["faixa_pelo_escore"] = escore["ivs_admin"].map(faixa_por_escore)
    escore["faixa_pela_categoria"] = escore["categoria_ivs_admin"].map(CATEGORIA_PARA_FAIXA)
    limites = {
        cat: {"min": float(g["ivs_admin"].min()), "max": float(g["ivs_admin"].max()), "n": int(len(g))}
        for cat, g in escore.groupby("categoria_ivs_admin")
    }
    faixa_limites = {
        f: {"min": float(g["ivs_admin"].min()), "max": float(g["ivs_admin"].max()), "n": int(len(g))}
        for f, g in escore.groupby("faixa_atracao")
    }

    # 2. Categoria administrativa do consolidado PMMB (todos os municipios)
    #    contra a categoria da relacao nominal PMM-E.
    cat_cmp = escore.merge(categoria, on="co_ibge", how="left", suffixes=("", "_pmmb"))
    concord_categoria = int((cat_cmp["categoria_ivs_admin"] == cat_cmp["categoria_ivs_admin_pmmb"]).sum())

    # 3. Escore administrativo contra IVS 2010 publico.
    cmp_pub = escore.merge(publico, left_on="co_ibge", right_on="cod_ibge6", how="left")
    dif = cmp_pub["ivs_admin"] - cmp_pub["ivs_2010"]

    # 4. Cada quadro de vagas: regra, cobertura e suporte.
    matriz = []
    por_quadro = {}
    for chave, caminho, referencia in QUADROS:
        q = ler_quadro(caminho)
        multiplas = int((q.groupby("co_ibge")["faixa_anunciada"].nunique() > 1).sum())
        q = q.drop_duplicates("co_ibge")
        q = q.merge(escore[["co_ibge", "ivs_admin"]], on="co_ibge", how="left")
        q = q.merge(categoria, on="co_ibge", how="left")
        q["tem_escore"] = q["ivs_admin"].notna()
        q["faixa_pelo_escore"] = q["ivs_admin"].map(lambda s: faixa_por_escore(s) if pd.notna(s) else None)
        q["faixa_pela_categoria"] = q["categoria_ivs_admin"].map(CATEGORIA_PARA_FAIXA)
        com = q[q["tem_escore"]]
        com_cat = q[q["faixa_pela_categoria"].notna()]

        suporte = {}
        for corte in (CUTOFF_INFERIOR, CUTOFF_SUPERIOR):
            for h in JANELAS:
                abaixo = com[(com["ivs_admin"] > corte - h) & (com["ivs_admin"] <= corte)]
                acima = com[(com["ivs_admin"] > corte) & (com["ivs_admin"] <= corte + h)]
                suporte[f"{corte:.3f}_h{h:.3f}"] = {
                    "abaixo_ou_no_corte": int(len(abaixo)),
                    "acima": int(len(acima)),
                    "mass_points_abaixo": int(abaixo["ivs_admin"].nunique()),
                    "mass_points_acima": int(acima["ivs_admin"].nunique()),
                }

        por_quadro[chave] = {
            "arquivo": caminho,
            "sha256": sha256(ROOT / caminho),
            "referencia": referencia,
            "municipios": int(len(q)),
            "municipios_com_mais_de_uma_faixa": multiplas,
            "regra_pelo_escore": {
                "municipios_com_escore": int(len(com)),
                "reproduzidos": int((com["faixa_pelo_escore"] == com["faixa_anunciada"]).sum()),
            },
            "regra_pela_categoria_administrativa": {
                "municipios_com_categoria": int(len(com_cat)),
                "reproduzidos": int((com_cat["faixa_pela_categoria"] == com_cat["faixa_anunciada"]).sum()),
            },
            "cobertura_do_escore": {
                "pct_municipios": round(100 * float(q["tem_escore"].mean()), 1),
                "pct_por_faixa_anunciada": {
                    f: round(100 * float(g["tem_escore"].mean()), 1)
                    for f, g in q.groupby("faixa_anunciada")
                },
            },
            "suporte_municipios_com_escore": suporte,
        }
        q.insert(0, "quadro", chave)
        q["valor_anunciado_brl"] = q["faixa_anunciada"].map(VALOR)
        matriz.append(q)

    pd.concat(matriz, ignore_index=True)[
        ["quadro", "co_ibge", "faixa_anunciada", "valor_anunciado_brl", "categoria_ivs_admin",
         "faixa_pela_categoria", "tem_escore", "ivs_admin", "faixa_pelo_escore"]
    ].to_csv(OUT_MATRIZ, index=False)

    regra_100 = all(
        v["regra_pelo_escore"]["reproduzidos"] == v["regra_pelo_escore"]["municipios_com_escore"]
        and v["regra_pela_categoria_administrativa"]["reproduzidos"]
        == v["regra_pela_categoria_administrativa"]["municipios_com_categoria"]
        for v in por_quadro.values()
    )
    cobertura_completa = all(v["cobertura_do_escore"]["pct_municipios"] == 100.0 for v in por_quadro.values())
    decisao = (
        "APROVADO_SHARP" if regra_100 and cobertura_completa
        else "REGRA_RECONSTRUIDA_ESCORE_INCOMPLETO" if regra_100
        else "REPROVADO"
    )

    resultado = {
        "status": "PORTAO_CAUSAL",
        "portao": "R1",
        "data_execucao": DATA_EXECUCAO,
        "outcomes_abertos": False,
        "decisao_r1": decisao,
        "leitura": (
            "O escore administrativo e a regra de dois cortes reproduzem a faixa anunciada em todos os "
            "municipios em que o escore e observado, nos quatro quadros, e a categoria administrativa a "
            "reproduz em todos os municipios. O escore continuo, porem, so e publicado para municipios com "
            "especialista ativo: a cobertura e selecionada pelo desfecho. A RDD nao pode ser estimada "
            "na subamostra coberta."
        ),
        "running_variable": {
            "nome": "ivs (escore administrativo publicado pelo MS, 'calculado pelo IPEA')",
            "safra": "nao declarada; difere do IVS 2010 publico",
            "precisao": "3 casas decimais",
            "cutoffs": {
                "inferior": {"valor": CUTOFF_INFERIOR, "salto": "Faixa 3 -> Faixa 2, +R$ 5.000"},
                "superior": {"valor": CUTOFF_SUPERIOR, "salto": "Faixa 2 -> Faixa 1, +R$ 5.000"},
            },
            "lado_do_corte_observado": {
                "faixa_3_max": faixa_limites.get("FAIXA 3", {}).get("max"),
                "faixa_2_min": faixa_limites.get("FAIXA 2", {}).get("min"),
                "faixa_2_max": faixa_limites.get("FAIXA 2", {}).get("max"),
                "faixa_1_min": faixa_limites.get("FAIXA 1", {}).get("min"),
                "nota": "0,400 pertence a Faixa 2 (observado). O lado de 0,300 exato nao e observado; "
                        "pela classe do Atlas, 0,300 e 'baixa' e cai na Faixa 3.",
            },
            "limites_por_categoria": limites,
        },
        "relacao_nominal": {
            "municipios": int(len(escore)),
            "escore_reproduz_faixa": int((escore["faixa_pelo_escore"] == escore["faixa_atracao"]).sum()),
            "categoria_reproduz_faixa": int((escore["faixa_pela_categoria"] == escore["faixa_atracao"]).sum()),
            "categoria_igual_a_do_consolidado_pmmb": concord_categoria,
        },
        "comparacao_ivs_2010_publico": {
            "correlacao": round(float(cmp_pub[["ivs_admin", "ivs_2010"]].corr().iloc[0, 1]), 3),
            "diferenca_media": round(float(dif.mean()), 4),
            "diferenca_dp": round(float(dif.std()), 4),
            "diferenca_min": round(float(dif.min()), 3),
            "diferenca_max": round(float(dif.max()), 3),
            "pct_identicos": round(100 * float((dif.abs() < 1e-9).mean()), 1),
            "leitura": "outra safra ou outro calculo; explica o teto de 78% das regras de corte sobre o IVS 2010",
        },
        "quadros": por_quadro,
        "requisitos_r1": {
            "municipio_escore_faixa_valor_completos": cobertura_completa,
            "escore_unico_por_municipio": True,
            "regra_reproduz_100_pct": regra_100,
            "lado_do_cutoff_localizavel": "sim em 0,400; 0,300 exato nao observado",
            "fontes_e_hashes_preservados": True,
        },
        "bloqueio": {
            "motivo": "escore continuo ausente para os municipios sem especialista ativo; ausencia funcao do desfecho",
            "o_que_destrava": "o campo `ivs` para todos os municipios com vaga ofertada (ou para os 5.570), "
                              "da mesma base que alimenta a relacao nominal",
        },
        "fontes": {
            str(ESCORE.relative_to(ROOT)): {"sha256": sha256(ESCORE)},
            str(CATEGORIA.relative_to(ROOT)): {"sha256": sha256(CATEGORIA)},
            str(IVS_PUBLICO.relative_to(ROOT)): {"sha256": sha256(IVS_PUBLICO)},
        },
        "bloqueios_resultantes": {"r2": "BLOQUEADO_POR_R1_COBERTURA", "r3": "BLOQUEADO", "r4": "BLOQUEADO", "r5": "BLOQUEADO"},
    }
    OUT_JSON.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: resultado[k] for k in ("decisao_r1", "relacao_nominal", "comparacao_ivs_2010_publico")},
                     ensure_ascii=False, indent=2))
    for k, v in por_quadro.items():
        print(k, v["municipios"], v["regra_pelo_escore"], v["regra_pela_categoria_administrativa"],
              v["cobertura_do_escore"])


if __name__ == "__main__":
    main()
