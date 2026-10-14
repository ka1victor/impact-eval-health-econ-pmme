"""Portao R1 com o IVS administrativo da SGTES: a faixa da bolsa e reproduzida?

Este script pertence ao portao R1 e **nao abre nenhum outcome**: le apenas o
IVS publicado pela SGTES no quadro do PMMB 2026, a faixa anunciada nos quadros
de vagas do PMM-E, o rotulo de IVS da serie historica e o IVS 2010 do Atlas.

O R1 publico (`01_auditar_regra_e_suporte.py`, `01b_reconstruir_regra_faixa.py`)
reprovou porque testou o IVS 2010 do Atlas, e esse diagnostico continua
verdadeiro: o IVS 2010 nao reproduz a faixa. A pergunta aqui e se o IVS que a
propria SGTES publica reproduz. A regra testada e a do item 11.2 do Edital
SGTES/MS n. 28/2026, com os cortes das categorias do Atlas aplicados ao IVS
administrativo:

    IVS <= 0,300          -> Faixa 3, R$ 10 mil (baixa ou muito baixa)
    0,300 < IVS <= 0,400  -> Faixa 2, R$ 15 mil (media)
    IVS > 0,400           -> Faixa 1, R$ 20 mil (alta ou muito alta)

O portao so aprova sharp se a regra acertar todos os municipios de todas as
ondas de oferta, sem excecao.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import re
import unicodedata
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "aquisicao" / "ivs_regra"
PMMB = RAW / "pmmb_2026_quadro_de_vagas.xlsx"
EDITAL_2026 = RAW / "edital_sgtes_06_2026_edital_28_2026_ciclo3.html"
FAQ_2025 = RAW / "edital_sgtes_03_2025_faq_bolsa.html"
QUADRO = ROOT / "output" / "aquisicao" / "quadro_vagas_consolidado.parquet"
SERIE = ROOT / "data" / "pmm_especialistas_serie_historica.csv"
IVS_2010 = ROOT / "data" / "ivs_ipea_2010_municipios.csv"
OUT_JSON = ROOT / "output" / "rdd_bolsa" / "a01c_regra_ivs_administrativo.json"
OUT_MATRIZ = ROOT / "output" / "rdd_bolsa" / "matriz_municipio_ivs_administrativo.csv"

ABA_PMMB = "Lista de Municípios-Tipo Equipe"
CORTES_CATEGORIA = (0.200, 0.300, 0.400, 0.500)
CATEGORIAS = (
    "MUITO BAIXA VULNERABILIDADE",
    "BAIXA VULNERABILIDADE",
    "MEDIA VULNERABILIDADE",
    "ALTA VULNERABILIDADE",
    "MUITO ALTA VULNERABILIDADE",
)
# Item 11.2 do Edital SGTES/MS n. 28/2026 (ciclo 3).
FAIXA_POR_CATEGORIA = {
    "MUITO BAIXA VULNERABILIDADE": "FAIXA 3",
    "BAIXA VULNERABILIDADE": "FAIXA 3",
    "MEDIA VULNERABILIDADE": "FAIXA 2",
    "ALTA VULNERABILIDADE": "FAIXA 1",
    "MUITO ALTA VULNERABILIDADE": "FAIXA 1",
}
# FAQ do Chamamento SGTES/MS n. 3/2025: o texto que a auditoria anterior leu
# como a regra de 2025.
FAIXA_POR_CATEGORIA_FAQ_2025 = {
    "MUITO BAIXA VULNERABILIDADE": "FAIXA 3",
    "BAIXA VULNERABILIDADE": "FAIXA 3",
    "MEDIA VULNERABILIDADE": "FAIXA 3",
    "ALTA VULNERABILIDADE": "FAIXA 2",
    "MUITO ALTA VULNERABILIDADE": "FAIXA 1",
}
VALOR = {"FAIXA 3": 10_000, "FAIXA 2": 15_000, "FAIXA 1": 20_000}
CLAUSULA_11_2_EDITAL_28_2026 = (
    "11.2. Para fins de alocacao dos medicos especialistas no ambito do PMM-E, foi "
    "estabelecido o criterio de faixa de atracao com base na categorizacao municipal do "
    "indice de Vulnerabilidade Social - IVS, com os seguintes valores liquidos: a) "
    "Municipios classificados como de muito alta ou alta vulnerabilidade social serao "
    "enquadrados na Faixa 1: bolsa mensal no valor de R$ 20.000,00; b) Municipios "
    "classificados como de media vulnerabilidade social serao enquadrados na Faixa 2: "
    "bolsa mensal no valor de R$ 15.000,00; e, c) Municipios classificados como de baixa "
    "ou muito baixa vulnerabilidade social na Faixa 3: bolsa mensal no valor de "
    "R$ 10.000,00, mantendo o valor fixo da bolsa."
)

# Ondas de oferta: (rotulo, ciclo, chamada, versoes). A segunda chamada de 2025
# so tem faixa por extenso na aba de cadastro de reserva.
ONDAS = (
    ("2025_c1_ch1", 1, 1, ("original",)),
    ("2025_c1_ch2", 1, 2, ("oficial",)),
    ("2026_c2_ch1", 2, 1, ("original", "retificada_servicos", "retificada_final")),
    ("2026_c2_ch2", 2, 2, ("oficial",)),
    ("2026_c3_ch1", 3, 1, ("original", "retificada")),
)
VERSAO_CANONICA = {
    "2025_c1_ch1": "original",
    "2025_c1_ch2": "oficial",
    "2026_c2_ch1": "retificada_final",
    "2026_c2_ch2": "oficial",
    "2026_c3_ch1": "retificada",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fonte(path: Path) -> dict:
    return {"arquivo": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(path)}


def normalizar_categoria(texto: object) -> str:
    texto = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode().upper()
    texto = re.sub(r"^\d\s*-\s*", "", texto)
    texto = re.sub(r"[^A-Z ]", "", texto).strip()
    # A serie grava "Media" com o acento corrompido em quatro competencias
    # ("MDIA", "MADIA", "MAADIA", conforme a dupla codificacao).
    texto = re.sub(r"^M[A-Z]{0,3}DIA ", "MEDIA ", texto)
    if texto not in CATEGORIAS:
        raise ValueError(f"Categoria de IVS desconhecida: {texto!r}")
    return texto


def categoria_do_ivs(valor: float) -> str:
    return CATEGORIAS[int(np.searchsorted(CORTES_CATEGORIA, round(valor, 3), side="left"))]


def carregar_ivs_administrativo() -> pd.DataFrame:
    bruto = pd.read_excel(PMMB, sheet_name=ABA_PMMB, dtype=str)
    # Os rotulos de tres colunas estao deslocados em relacao aos dados (a coluna
    # "Regiao" guarda o codigo IBGE). A chave e localizada pelo conteudo, nao
    # pelo rotulo, e a troca e verificada.
    col_ibge = [c for c in bruto.columns if bruto[c].str.fullmatch(r"\d{6}").all()]
    col_uf = [c for c in bruto.columns if bruto[c].str.fullmatch(r"[A-Z]{2}").all()]
    if len(col_ibge) != 1 or len(col_uf) != 1:
        raise ValueError(f"Chave IBGE/UF ambigua no quadro do PMMB: {col_ibge}, {col_uf}")
    tabela = pd.DataFrame(
        {
            "co_ibge_6d": bruto[col_ibge[0]],
            "sg_uf": bruto[col_uf[0]],
            "no_municipio": bruto["MUNICÍPIO"].str.strip(),
            "ivs_adm": pd.to_numeric(bruto["IVS"], errors="raise"),
            "categoria_publicada": bruto["CATEGORIA IVS"].map(normalizar_categoria),
            "amazonia_legal": bruto["AMAZONIA LEGAL"].str.strip().eq("Amazônia Legal"),
            "faixa_fronteira": bruto["FAIXA DE FRONTEIRA"].str.strip().eq("Faixa de Fronteira"),
        }
    )
    # Ha linhas repetidas por tipo de equipe; o atributo municipal tem de ser unico.
    atributos = ["ivs_adm", "categoria_publicada", "amazonia_legal", "faixa_fronteira", "sg_uf"]
    conflito = tabela.groupby("co_ibge_6d")[atributos].nunique().gt(1).any(axis=1)
    if conflito.any():
        raise ValueError(f"Municipios com IVS ou categoria conflitante: {list(conflito[conflito].index)}")
    # Situacao e vagas da equipe de Saude da Familia no PMMB 2026: entram no R2
    # como cointervencao candidata nos mesmos cortes, nao como outcome do PMM-E.
    esf = bruto["TIPO DE EQUIPE"].str.startswith("70")
    pmmb = pd.DataFrame(
        {
            "co_ibge_6d": bruto.loc[esf, col_ibge[0]],
            "pmmb_situacao_esf": bruto.loc[esf, "SITUACAO"].str.strip(),
            "pmmb_vagas_esf": pd.to_numeric(bruto.loc[esf, "VAGAS TOTAL"], errors="raise"),
        }
    )
    if pmmb.co_ibge_6d.duplicated().any():
        raise ValueError("Mais de uma linha de eSF por municipio no quadro do PMMB")
    return (
        tabela.drop_duplicates("co_ibge_6d")
        .merge(pmmb, on="co_ibge_6d", how="left", validate="one_to_one")
        .set_index("co_ibge_6d")
        .sort_index()
    )


def carregar_ofertas() -> pd.DataFrame:
    quadro = pd.read_parquet(QUADRO)
    quadro["co_ibge_6d"] = quadro.co_ibge_6d.astype(str).str[:6]
    quadro = quadro[quadro.faixa_atracao_anunciada.isin(VALOR)]
    linhas = []
    for onda, ciclo, chamada, versoes in ONDAS:
        recorte = quadro[(quadro.ciclo == ciclo) & (quadro.chamada == chamada)]
        recorte = recorte[recorte.tipo_documento.isin(["OFERTA_VAGAS", "OFERTA_E_ALOCADOS"])]
        for versao in versoes:
            parte = recorte[recorte.versao_edital == versao]
            if parte.empty:
                raise ValueError(f"Onda sem linhas de oferta: {onda} {versao}")
            faixas = parte.groupby("co_ibge_6d").faixa_atracao_anunciada.agg(lambda x: "|".join(sorted(set(x))))
            linhas.append(faixas.rename("faixa_anunciada").reset_index().assign(onda=onda, versao=versao))
    return pd.concat(linhas, ignore_index=True)


def carregar_rotulo_serie() -> pd.Series:
    serie = pd.read_csv(SERIE, encoding="latin-1", dtype=str, usecols=["co_ibge", "ivs"])
    serie["co_ibge_6d"] = serie.co_ibge.str[:6]
    serie["categoria"] = serie.ivs.map(normalizar_categoria)
    por_municipio = serie.groupby("co_ibge_6d").categoria.agg(lambda x: sorted(set(x)))
    if por_municipio.map(len).gt(1).any():
        raise ValueError("Rotulo de IVS da serie muda dentro do municipio")
    return por_municipio.map(lambda x: x[0]).rename("rotulo_serie")


def auditar_serie(rotulo: pd.Series) -> dict:
    """Constancia temporal do rotulo e da faixa na serie; nao le quantidade de ativos."""
    serie = pd.read_csv(SERIE, encoding="latin-1", dtype=str, usecols=["co_ibge", "competencia", "faixa_atracao"])
    serie["co_ibge_6d"] = serie.co_ibge.str[:6]
    serie["faixa_regra"] = serie.co_ibge_6d.map(rotulo).map(FAIXA_POR_CATEGORIA)
    serie["diverge"] = serie.faixa_atracao.ne(serie.faixa_regra)
    por_comp = (
        serie.drop_duplicates(["co_ibge_6d", "competencia", "faixa_atracao"])
        .groupby("competencia")
        .agg(municipios=("co_ibge_6d", "nunique"), linhas_divergentes=("diverge", "sum"))
    )
    return {
        "nota": (
            "Campo de faixa da serie historica de bolsistas ativos, usado so para "
            "checar consistencia. Em dez/2025 e jan/2026 ele diverge da regra e do "
            "quadro anunciado; nas demais competencias coincide. Nao ha pagamento "
            "observado que permita ler a divergencia como mudanca de valor recebido."
        ),
        "por_competencia": {
            comp: {"municipios": int(l.municipios), "linhas_divergentes": int(l.linhas_divergentes)}
            for comp, l in por_comp.iterrows()
        },
    }


def main() -> None:
    adm = carregar_ivs_administrativo()
    adm["categoria_recalculada"] = adm.ivs_adm.map(categoria_do_ivs)
    adm["faixa_regra"] = adm.categoria_recalculada.map(FAIXA_POR_CATEGORIA)
    adm["valor_bolsa_regra"] = adm.faixa_regra.map(VALOR)
    categoria_ok = adm.categoria_publicada.eq(adm.categoria_recalculada)

    ofertas = carregar_ofertas()
    ofertas = ofertas.join(adm[["ivs_adm", "faixa_regra"]], on="co_ibge_6d")
    sem_ivs = ofertas[ofertas.ivs_adm.isna()]
    if not sem_ivs.empty:
        raise ValueError(f"Municipios ofertados sem IVS administrativo: {sorted(sem_ivs.co_ibge_6d.unique())}")
    ofertas["reproduz"] = ofertas.faixa_anunciada.eq(ofertas.faixa_regra)
    ofertas["reproduz_faq_2025"] = ofertas.faixa_anunciada.eq(
        ofertas.co_ibge_6d.map(adm.categoria_recalculada).map(FAIXA_POR_CATEGORIA_FAQ_2025)
    )
    reproducao = {}
    for (onda, versao), g in ofertas.groupby(["onda", "versao"], sort=False):
        reproducao[f"{onda}/{versao}"] = {
            "municipios": int(len(g)),
            "com_mais_de_uma_faixa": int(g.faixa_anunciada.str.contains("|", regex=False).sum()),
            "reproduzidos_regra_edital_28_2026": int(g.reproduz.sum()),
            "reproduzidos_texto_faq_2025": int(g.reproduz_faq_2025.sum()),
        }
    total = int(len(ofertas))
    acertos = int(ofertas.reproduz.sum())

    # Constancia da faixa anunciada entre ondas, na versao canonica de cada uma.
    canon = ofertas[ofertas.apply(lambda r: VERSAO_CANONICA[r.onda] == r.versao, axis=1)]
    largo = canon.pivot(index="co_ibge_6d", columns="onda", values="faixa_anunciada")
    mudancas = {}
    for a, b in itertools.combinations([o[0] for o in ONDAS], 2):
        par = largo[[a, b]].dropna()
        mudancas[f"{a}|{b}"] = {"municipios_em_ambas": int(len(par)), "faixa_muda": int(par[a].ne(par[b]).sum())}

    rotulo = carregar_rotulo_serie()
    comparacao = adm.join(rotulo, how="inner")
    ivs2010 = pd.read_csv(IVS_2010, dtype={"cod_ibge6": str}).set_index("cod_ibge6")
    adm = adm.join(ivs2010[["ivs_2010"]])
    com_2010 = adm.dropna(subset=["ivs_2010"])
    cat_2010 = com_2010.ivs_2010.map(categoria_do_ivs)
    ordem = {c: i for i, c in enumerate(CATEGORIAS)}
    deslocamento = (com_2010.categoria_recalculada.map(ordem) - cat_2010.map(ordem)).value_counts().sort_index()

    decisao = (
        "APROVADO_SHARP"
        if acertos == total and bool(categoria_ok.all()) and not any(v["faixa_muda"] for v in mudancas.values())
        else "REPROVADO"
    )

    # Matriz municipal: uma linha por municipio do pais, ofertado ou nao.
    matriz = adm.copy()
    for onda, _, _, _ in ONDAS:
        recorte = canon[canon.onda == onda].set_index("co_ibge_6d")
        matriz[f"ofertado_{onda}"] = matriz.index.isin(recorte.index)
        matriz[f"faixa_anunciada_{onda}"] = recorte.faixa_anunciada.reindex(matriz.index)
    matriz["ofertado_alguma_onda"] = matriz[[f"ofertado_{o[0]}" for o in ONDAS]].any(axis=1)
    matriz = matriz.reset_index()
    OUT_MATRIZ.parent.mkdir(parents=True, exist_ok=True)
    matriz.to_csv(OUT_MATRIZ, index=False, float_format="%.3f")

    relatorio = {
        "portao": "R1",
        "running_variable": "IVS administrativo publicado pela SGTES no quadro do PMMB 2026",
        "data_execucao": date.today().isoformat(),
        "outcomes_abertos": False,
        "decisao_r1": decisao,
        "regra": {
            "cortes": {"faixa3_para_faixa2": 0.300, "faixa2_para_faixa1": 0.400},
            "lado_do_corte": "o valor igual ao corte fica abaixo: 0,300 e Faixa 3; 0,301 e Faixa 2",
            "precisao": "tres casas decimais",
            "clausula": CLAUSULA_11_2_EDITAL_28_2026,
            "cortes_sem_mudanca_de_bolsa": [0.200, 0.500],
        },
        "ivs_administrativo": {
            "municipios": int(len(adm)),
            "minimo": float(adm.ivs_adm.min()),
            "maximo": float(adm.ivs_adm.max()),
            "categoria_publicada_igual_a_recalculada": int(categoria_ok.sum()),
            "municipios_por_categoria": {c: int(n) for c, n in adm.categoria_recalculada.value_counts().reindex(CATEGORIAS).items()},
        },
        "reproducao_da_faixa_anunciada": {
            "total_municipio_onda_versao": total,
            "acertos": acertos,
            "por_onda_versao": reproducao,
            "leitura_faq_2025": (
                "O texto do FAQ de 2025 aplicado ao mesmo IVS acerta so os municipios de "
                "faixa 3 e muito alta; a regra efetiva ja em 2025 e a que o edital de 2026 "
                "escreve."
            ),
        },
        "faixa_entre_ondas": {
            "pares": mudancas,
            "leitura": "nenhum municipio mudou de faixa entre 2025 e 2026; nao ha variacao temporal da bolsa",
        },
        "rotulo_da_serie_historica": {
            "municipios_com_rotulo": int(len(comparacao)),
            "rotulo_igual_categoria_administrativa": int(comparacao.rotulo_serie.eq(comparacao.categoria_recalculada).sum()),
            "limite": "o rotulo so existe para municipios que tiveram bolsista ativo; serve de conferencia, nao de base",
            "consistencia_do_campo_faixa": auditar_serie(rotulo),
        },
        "comparacao_ivs_2010_atlas": {
            "municipios": int(len(com_2010)),
            "valor_identico": int(com_2010.ivs_adm.sub(com_2010.ivs_2010).abs().lt(0.0005).sum()),
            "correlacao": round(float(com_2010[["ivs_adm", "ivs_2010"]].corr().iloc[0, 1]), 4),
            "diferenca_media": round(float(com_2010.ivs_adm.sub(com_2010.ivs_2010).mean()), 4),
            "diferenca_dp": round(float(com_2010.ivs_adm.sub(com_2010.ivs_2010).std()), 4),
            "mesma_categoria": int(cat_2010.eq(com_2010.categoria_recalculada).sum()),
            "deslocamento_de_categoria_adm_menos_2010": {str(int(k)): int(v) for k, v in deslocamento.items()},
            "leitura": (
                "o IVS administrativo nao e o IVS 2010 do Atlas; e por isso que o R1 publico "
                "reprovou. A safra do IVS administrativo nao e publicada."
            ),
        },
        "fontes": {
            "ivs_administrativo": fonte(PMMB),
            "edital_28_2026": fonte(EDITAL_2026),
            "faq_2025": fonte(FAQ_2025),
            "quadro_vagas_consolidado": fonte(QUADRO),
            "serie_historica": fonte(SERIE),
            "ivs_2010_atlas": fonte(IVS_2010),
        },
        "o_que_nao_autoriza": (
            "Nao abre outcomes nem escolhe janela. Autoriza executar o R2 (suporte, "
            "selecao na oferta, balanco e cointervencoes) sem outcomes."
        ),
    }
    OUT_JSON.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[R1-ADM] {decisao}: {acertos}/{total} municipio-onda-versao reproduzidos; matriz com {len(matriz)} municipios.")


if __name__ == "__main__":
    main()
