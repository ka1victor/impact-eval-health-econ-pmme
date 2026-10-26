"""Protocolo 62: por que o preenchimento da célula aberta sobe com o IVS dentro das faixas da bolsa? (descritivo)

Especificação: `docs/06_execucao/62_protocolo_gradiente_dentro_das_faixas.md`, congelado em 26/10/2026 antes de
qualquer conta. Estatuto `DESCRITIVO_62_POS_RESULTADO`: não é contraste causal e não muda nenhum protocolo anterior.
Toda linha sai com `natureza_dos_dados = EMPIRICO`.

O que o script faz, na ordem
----------------------------
1. Carrega a base de células abertas do A3 (adendo §7 do protocolo 48), ciclos 1–3, com os atributos que o diagnóstico
   61 já constrói (composição, concorrência, REGIC), importando `carregar()` do script 38 sem alterá-lo. Confere que a
   faixa da bolsa de cada célula (pelo IVS 2010 oficial) é a faixa anunciada no quadro.
2. Constrói o único atributo novo, o G-b: candidatos do mesmo curso e ciclo com origem (G1, regra principal) na mesma UF
   e na mesma região de saúde da célula, por vaga oferecida do mesmo curso e ciclo nesse mercado.
3. Para cada faixa (R$ 10 mil: IVS até 0,300; R$ 15 mil: 0,301 a 0,400; R$ 20 mil: acima de 0,400), estima um modelo de
   probabilidade linear da célula preenchida na 1ª chamada no IVS contínuo, com efeito fixo de ciclo e EP agrupado por
   município (CR1). Inclinação por 0,100 de IVS, em toda a faixa e na janela de 0,050 junto ao corte superior.
4. Acrescenta, um a um e depois todos juntos, os fatores G-a a G-e; para cada um, a inclinação depois do fator e a
   inclinação original na mesma amostra. G-f é só relato. BKY entre todas as inclinações.
5. Monta a tabela "quanto da subida cada fator leva", aplica a leitura pré-registrada (§3), grava as figuras e o doc 57m.

Integridade
-----------
Nada imputado nem simulado; ausente fica ausente e é contado. Running variable = IVS 2010 oficial (a08); o arquivo local
de IVS da auditoria 16 não é lido. O CNES só é lido no pré (202406–202506), pelo script 38. As listas de candidatos (G1,
escolhas) só são usadas agregadas, em memória: nenhum identificador de pessoa vai para `output/`. As saídas de outros
blocos não são regravadas. Tudo é descritivo e pós-resultado: diz com o que a subida anda junto, não por quê.

Uso
---
    python3 scripts/rdd_bolsa/39_gradiente_faixas.py
    python3 scripts/rdd_bolsa/39_gradiente_faixas.py --atualizar-doc
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DIR_RDD = ROOT / "scripts" / "rdd_bolsa"


def _importar(caminho: Path, nome: str):
    if nome in sys.modules:
        return sys.modules[nome]
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    return mod


_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
DQ = _importar(DIR_RDD / "38_diagnostico_queda_0300.py", "dq_para_gf")
sys.dont_write_bytecode = _bytecode
L, T23, T24, T29, T32, E6 = DQ.L, DQ.T23, DQ.T24, DQ.T29, DQ.T32, DQ.E6

# ---------------------------------------------------------------------------
# Caminhos e parâmetros do protocolo 62
# ---------------------------------------------------------------------------

OUT = ROOT / "output" / "rdd_bolsa"
NOME_EST = "GF_estimativas.csv"
NOME_RESUMO = "GF_resumo.json"
DIR_FIG = "GF_figuras"
DOC = ROOT / "docs" / "06_execucao" / "57m_gradiente_faixas.md"
PROTOCOLO_MD = ROOT / "docs" / "06_execucao" / "62_protocolo_gradiente_dentro_das_faixas.md"
AUDITORIA_18 = ROOT / "docs" / "auditorias" / "18_politicas_nos_mesmos_cortes_ivs.md"
DIR_AUDITORIAS = ROOT / "docs" / "auditorias"
PADRAO_AUDITORIA_GF = "35_*"          # G-f: pesquisa documental do mesmo dia, em paralelo
FIGURA_ORIGEM = ROOT / "output" / "apresentacao_banca2" / "exp_rdd_crua.png"
G1_ORIGEM = DQ.G1_ORIGEM
ESCOLHAS = DQ.ESCOLHAS

DATA_EXECUCAO = "2026-10-26"
ESTATUTO = "DESCRITIVO_62_POS_RESULTADO"
NATUREZA = "EMPIRICO"
UNIDADE_X_MIL = 100      # inclinação por 0,100 de IVS
JANELA_MIL = 50          # janela de 0,050 junto ao corte superior da faixa
BIN_MIL = 10             # médias por faixa de IVS de 0,010 (figura)
LIMIAR_METADE = 0.5
REGRA_LIGACAO = "g1_cpf_nome"
UNIDADE = "fracao de celulas preenchidas por 0,100 de IVS (x100 = p.p. por 0,100)"
FAIXAS = [
    {"faixa": "R$10mil", "bolsa_mil": 10, "lo": None, "hi": 300, "faixa_anunciada": "FAIXA 3",
     "rotulo": "R$ 10 mil (IVS até 0,300)"},
    {"faixa": "R$15mil", "bolsa_mil": 15, "lo": 300, "hi": 400, "faixa_anunciada": "FAIXA 2",
     "rotulo": "R$ 15 mil (IVS de 0,301 a 0,400)"},
    {"faixa": "R$20mil", "bolsa_mil": 20, "lo": 400, "hi": None, "faixa_anunciada": "FAIXA 1",
     "rotulo": "R$ 20 mil (IVS acima de 0,400)"},
]
JANELAS = ("faixa_inteira", "janela_0050_corte_superior")
MACRO = {"1": "NORTE", "2": "NORDESTE", "3": "SUDESTE", "4": "SUL", "5": "CENTRO OESTE"}

EXPLICACOES = [
    {"id": "G-a", "nome": "regiao", "explicacao": "IVS maior está mais no Norte e no Nordeste, onde há mais candidatos "
     "que ficam perto de casa", "fator": "efeito fixo de macrorregiao; depois, de UF"},
    {"id": "G-b", "nome": "oferta de candidatos por perto", "explicacao": "mais candidatos do curso por perto da "
     "celula, por vaga", "fator": "n de candidatos do mesmo curso e ciclo com origem (G1) na mesma UF e na mesma regiao "
     "de saude da celula, por vaga oferecida"},
    {"id": "G-c", "nome": "composicao das vagas", "explicacao": "celulas de IVS maior sao de cursos, tipos de vaga ou "
     "estabelecimentos que preenchem mais", "fator": "efeito fixo de curso x ciclo; celula so de cadastro reserva; tipo "
     "e gestao do estabelecimento"},
    {"id": "G-d", "nome": "porte e hierarquia urbana", "explicacao": "IVS anda junto com porte e posicao na rede "
     "urbana", "fator": "log(populacao 2022); REGIC"},
    {"id": "G-e", "nome": "concorrencia", "explicacao": "menos celulas do mesmo curso competindo pelos mesmos "
     "candidatos", "fator": "n de celulas do mesmo curso e ciclo na regiao de saude"},
    {"id": "G-f", "nome": "outras politicas que variam com o IVS", "explicacao": "regras federais ligadas ao IVS",
     "fator": "sem fator testavel no nivel da celula; relato da pesquisa documental"},
]

# Variantes: (explicacao, variante, efeitos fixos extras, covariáveis contínuas, principal da explicação, descrição).
# O efeito fixo de ciclo está sempre no modelo. Categóricas viram indicadores (a 1ª categoria em ordem é a base);
# indicador colinear com outro (p. ex. ciclo dentro de curso x ciclo) é descartado de forma determinística.
VARIANTES = [
    ("G-a", "macrorregiao", ("macro",), (), False, "efeito fixo de macrorregiao"),
    ("G-a", "uf", ("uf",), (), True, "efeito fixo de UF"),
    ("G-b", "uf", (), ("cand_uf_por_vaga",), False, "candidatos com origem na UF da celula por vaga oferecida na UF"),
    ("G-b", "cir", (), ("cand_cir_por_vaga",), False, "candidatos com origem na regiao de saude da celula por vaga "
     "oferecida na regiao"),
    ("G-b", "uf_e_cir", (), ("cand_uf_por_vaga", "cand_cir_por_vaga"), True, "as duas medidas juntas"),
    ("G-c", "curso_x_ciclo", ("fe_curso_ciclo",), (), False, "efeito fixo de curso x ciclo"),
    ("G-c", "so_cr", (), ("so_cr",), False, "indicador de celula so de cadastro reserva"),
    ("G-c", "tipo_e_gestao", ("tipo_estab", "gestao"), (), False, "tipo e gestao do estabelecimento"),
    ("G-c", "todos", ("fe_curso_ciclo", "tipo_estab", "gestao"), ("so_cr",), True, "os tres juntos"),
    ("G-d", "log_pop", (), ("log_pop22",), False, "log da populacao do Censo 2022"),
    ("G-d", "regic", ("regic_cat",), (), False, "nivel REGIC 2018 (efeito fixo)"),
    ("G-d", "log_pop_e_regic", ("regic_cat",), ("log_pop22",), True, "os dois juntos"),
    ("G-e", "n_celulas_cir", (), ("n_conc_cir",), True, "outras celulas do mesmo curso e ciclo na regiao de saude"),
    ("TODOS", "todos_juntos", ("uf", "fe_curso_ciclo", "tipo_estab", "gestao", "regic_cat"),
     ("cand_uf_por_vaga", "cand_cir_por_vaga", "so_cr", "log_pop22", "n_conc_cir"), True,
     "G-a (UF), G-b, G-c, G-d e G-e juntos"),
]
BALANCO = [
    ("G-a", "norte_ou_nordeste", "celula no Norte ou no Nordeste", "fracao"),
    ("G-b", "cand_uf_por_vaga", "candidatos com origem na UF por vaga oferecida na UF", "candidatos por vaga"),
    ("G-b", "cand_cir_por_vaga", "candidatos com origem na regiao de saude por vaga oferecida na regiao",
     "candidatos por vaga"),
    ("G-c", "so_cr", "celula so de cadastro reserva", "fracao"),
    ("G-c", "hospital_geral", "estabelecimento hospital geral (cardapio do ciclo 3)", "fracao"),
    ("G-c", "gestao_estadual", "gestao estadual do estabelecimento", "fracao"),
    ("G-d", "log_pop22", "log da populacao 2022", "log"),
    ("G-d", "regic_nivel", "nivel REGIC (1 metropole ... 5 centro local)", "nivel"),
    ("G-e", "n_conc_cir", "outras celulas do mesmo curso e ciclo na regiao de saude", "celulas"),
]
COLS_FATOR = {
    "macro": "macrorregiao", "uf": "UF", "fe_curso_ciclo": "curso x ciclo", "tipo_estab": "tipo do estabelecimento",
    "gestao": "gestao do estabelecimento", "regic_cat": "nivel REGIC", "cand_uf_por_vaga": "candidatos na UF por vaga",
    "cand_cir_por_vaga": "candidatos na CIR por vaga", "so_cr": "so cadastro reserva", "log_pop22": "log(populacao 2022)",
    "n_conc_cir": "celulas concorrentes na CIR",
}

COLUNAS = [
    "natureza_dos_dados", "estatuto", "id_linha", "tipo_linha", "faixa", "bolsa_mil", "janela", "ivs_min", "ivs_max",
    "explicacao", "variante", "principal_da_explicacao", "descricao", "efeitos_fixos", "covariaveis", "estimador",
    "status", "n_obs", "n_municipios", "n_fora", "motivo_fora", "inclinacao", "ep", "ic95_inf", "ic95_sup", "p_valor",
    "q_bky", "inclinacao_original_mesma_amostra", "ep_original_mesma_amostra", "inclinacao_original",
    "fracao_da_subida_levada", "reduz_metade", "media_preenchida", "media_ivs", "bin_ivs_inf", "bin_ivs_sup",
    "n_celulas_bin", "unidade", "nota",
]
ESTIMADOR = ("MQO (probabilidade linear) da celula preenchida no IVS/0,100 com efeito fixo de ciclo; EP CR1 agrupado "
             "por municipio; IC e p pela normal")


class FalhaValidacao(RuntimeError):
    """Conferência que falhou: o script para sem gravar."""


sha256, rotulo = E6.sha256, E6.rotulo


def _juntar(*notas) -> str:
    return "; ".join(str(n) for n in notas if n)


# ---------------------------------------------------------------------------
# Dados
# ---------------------------------------------------------------------------

def faixa_de(s_mil: np.ndarray) -> np.ndarray:
    s = np.asarray(s_mil, dtype=float)
    return np.where(s <= 300, "R$10mil", np.where(s <= 400, "R$15mil", "R$20mil"))


def mascara(d: pd.DataFrame, fx: dict, janela: str) -> np.ndarray:
    s = d["s_mil"].to_numpy(dtype=float)
    m = np.ones(len(d), dtype=bool)
    if fx["lo"] is not None:
        m &= s > fx["lo"]
    if fx["hi"] is not None:
        m &= s <= fx["hi"]
    if janela == "janela_0050_corte_superior":
        if fx["hi"] is None:
            return np.zeros(len(d), dtype=bool)
        m &= s > fx["hi"] - JANELA_MIL
    return m


def contar_por_perto(o: pd.DataFrame, q: pd.DataFrame, cel: pd.DataFrame) -> pd.DataFrame:
    """Conta pura do G-b (sem ler arquivo).

    o: candidato × curso com origem (ciclo, cod_curso, id_candidato, uf_o, cir_o; cir_o pode faltar);
    q: células do quadro (ciclo, cod_curso, vic, uf, cir); cel: células da análise (ciclo, cod_curso, uf, cir).
    Célula sem CIR fica com a medida da CIR ausente; mercado sem candidato com origem conhecida = zero verdadeiro.
    """
    n_uf = o.groupby(["ciclo", "cod_curso", "uf_o"])["id_candidato"].nunique()
    n_cir = o[o["cir_o"].notna()].groupby(["ciclo", "cod_curso", "cir_o"])["id_candidato"].nunique()
    v_uf = q.groupby(["ciclo", "cod_curso", "uf"])["vic"].sum()
    v_cir = q[q["cir"].notna()].groupby(["ciclo", "cod_curso", "cir"])["vic"].sum()
    ch_uf = list(zip(cel["ciclo"].astype(int), cel["cod_curso"].astype(int), cel["uf"]))
    ch_cir = list(zip(cel["ciclo"].astype(int), cel["cod_curso"].astype(int), cel["cir"]))
    out = pd.DataFrame(index=cel.index)
    out["cand_uf"] = [float(n_uf.get(k, 0)) for k in ch_uf]
    out["vagas_uf"] = [float(v_uf.get(k, np.nan)) for k in ch_uf]
    out["cand_cir"] = [float(n_cir.get(k, 0)) if isinstance(k[2], str) else np.nan for k in ch_cir]
    out["vagas_cir"] = [float(v_cir.get(k, np.nan)) if isinstance(k[2], str) else np.nan for k in ch_cir]
    if (out["vagas_uf"] <= 0).any() or out["vagas_uf"].isna().any() or (out["vagas_cir"].dropna() <= 0).any() \
            or (out["cand_cir"].notna() & out["vagas_cir"].isna()).any():
        raise FalhaValidacao("G-b: mercado da celula sem vaga oferecida")
    out["cand_uf_por_vaga"] = out["cand_uf"] / out["vagas_uf"]
    out["cand_cir_por_vaga"] = out["cand_cir"] / out["vagas_cir"]
    return out


def candidatos_por_perto(cel: pd.DataFrame, quadro: pd.DataFrame, cir: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """G-b: candidatos do mesmo curso e ciclo com origem na UF e na CIR da célula, por vaga oferecida no mercado.

    Candidatos do curso = quem pôs alguma opção naquele curso no ciclo (tabela de escolhas do 12, como no D-e do 38).
    Origem = município principal de vínculo médico na competência de referência do G1 (regra g1_cpf_nome). Candidato
    sem origem não entra na contagem (contado). Vagas oferecidas = vagas imediatas + cadastro reserva de todas as
    células do quadro da 1ª chamada do mesmo curso e ciclo no mesmo mercado (a própria célula incluída). Só agregados.
    """
    g1 = pd.read_parquet(G1_ORIGEM, columns=["regra_ligacao", "ciclo", "id_candidato", "co_ibge_origem",
                                             "natureza_dos_dados"])
    if set(g1["natureza_dos_dados"].astype(str)) != {NATUREZA}:
        raise FalhaValidacao("G1 com natureza diferente de EMPIRICO")
    g1 = g1[g1["regra_ligacao"] == REGRA_LIGACAO]
    if g1.duplicated(["ciclo", "id_candidato"]).any():
        raise FalhaValidacao("G1 com candidato repetido no ciclo")
    esc = pd.read_parquet(ESCOLHAS, columns=["ciclo", "id_candidato", "cod_curso"]).drop_duplicates()
    o = esc.merge(g1[["ciclo", "id_candidato", "co_ibge_origem"]], on=["ciclo", "id_candidato"], how="left",
                  validate="many_to_one")
    sem_g1 = int(o["co_ibge_origem"].isna().sum())
    cand_ciclo = o.drop_duplicates(["ciclo", "id_candidato"])
    sem_origem = {int(k): int(v) for k, v in cand_ciclo["co_ibge_origem"].isna().groupby(cand_ciclo["ciclo"]).sum().items()}
    total = {int(k): int(v) for k, v in cand_ciclo.groupby("ciclo").size().items()}
    o = o[o["co_ibge_origem"].notna()].copy()
    o["co_ibge_origem"] = DQ._normal_ibge(o["co_ibge_origem"])
    mapa_cir = cir.set_index("co_ibge")["co_cir"]
    o["uf_o"] = o["co_ibge_origem"].str[:2]
    o["cir_o"] = o["co_ibge_origem"].map(mapa_cir)
    origem_sem_cir = int(o.drop_duplicates(["ciclo", "id_candidato"])["cir_o"].isna().sum())
    q = quadro[["ciclo", "co_ibge", "cod_curso", "vic"]].copy()
    q["co_ibge"] = q["co_ibge"].astype(str).str.zfill(6)
    q["uf"] = q["co_ibge"].str[:2]
    q["cir"] = q["co_ibge"].map(mapa_cir)
    out = contar_por_perto(o[["ciclo", "cod_curso", "id_candidato", "uf_o", "cir_o"]], q, cel)
    info = {"regra_ligacao": f"{REGRA_LIGACAO} (principal do G1)",
            "candidatos_por_ciclo": total, "candidatos_sem_origem_por_ciclo": sem_origem,
            "linhas_curso_candidato_sem_g1_ou_origem": sem_g1,
            "candidatos_com_origem_sem_cir": origem_sem_cir,
            "celulas_sem_cir": int(out["cand_cir"].isna().sum()),
            "definicao": "n de candidatos (com alguma opcao no curso e ciclo da celula e origem principal conhecida no "
                         "G1) cujo municipio de origem esta na mesma UF (ou regiao de saude) da celula, dividido pelas "
                         "vagas oferecidas (imediatas + CR) de todas as celulas do mesmo curso e ciclo nessa UF (ou "
                         "regiao de saude), a propria celula incluida",
            "ressalva": "o conjunto de candidatos se forma depois do anuncio da faixa; candidato sem origem conhecida "
                        "nao entra (a medida e um piso)"}
    return out, info


def preparar(B: dict) -> tuple[pd.DataFrame, dict]:
    cel = pd.concat(B["CK"].values(), ignore_index=True)
    info: dict = {}
    s = cel["s_mil"].to_numpy(dtype=float)
    if not np.all(np.isfinite(s)) or not np.all(s == np.round(s)):
        raise FalhaValidacao("IVS da celula ausente ou fora da grade de milesimos")
    cel["faixa"] = faixa_de(s)
    mapa_fx = {f["faixa"]: f["faixa_anunciada"] for f in FAIXAS}
    if (cel["faixa"].map(mapa_fx) != cel["faixa_anunciada"].astype(str)).any():
        raise FalhaValidacao("faixa pelo IVS oficial difere da faixa anunciada no quadro")
    cel["co_ibge"] = cel["co_ibge"].astype(str).str.zfill(6)
    cel["uf"] = cel["co_ibge"].str[:2]
    cel["macro"] = cel["co_ibge"].str[0].map(MACRO)
    if (cel["macro"] != cel["regiao"].astype(str)).any():
        raise FalhaValidacao("macrorregiao pelo codigo IBGE difere da regiao do quadro")
    base = B["dados"]["base"].set_index("co_ibge")
    cel["log_pop22"] = cel["co_ibge"].map(base["log_pop22"]).astype(float)
    cel["norte_ou_nordeste"] = cel["macro"].isin(["NORTE", "NORDESTE"]).astype(float)
    cel["regic_cat"] = cel["regic_nivel"].map(lambda v: f"n{int(v)}" if np.isfinite(v) else np.nan)
    cir, info["cir"] = T29.ler_cir()
    cel["cir"] = cel["co_ibge"].map(cir.set_index("co_ibge")["co_cir"])
    gb, info["G-b"] = candidatos_por_perto(cel, B["dados"]["cel"], cir)
    for c in gb.columns:
        cel[c] = gb[c].to_numpy()
    info["celulas_por_faixa"] = {f["faixa"]: int((cel["faixa"] == f["faixa"]).sum()) for f in FAIXAS}
    info["celulas_por_ciclo"] = {int(k): int(v) for k, v in cel.groupby("ciclo").size().items()}
    info["ausentes"] = {c: int(cel[c].isna().sum()) for c in sorted(COLS_FATOR)}
    info["fontes_dos_atributos"] = {
        "base_de_celulas": "adendo §7 do protocolo 48 (A3), via carregar() do script 38 -> carregar_tudo() do 24",
        "macro_e_uf": "codigo IBGE do municipio da celula (conferido contra a coluna regiao do quadro)",
        "curso_x_ciclo_e_so_cr": "fe_curso_ciclo e tipo_vaga_imediata do 24",
        "tipo_estab": DQ.__name__ + ".tipo_por_celula (cardapio de gestores do ciclo 3; fora dele = ausente)",
        "gestao": DQ.__name__ + ".gestao_por_celula (quadro da 1a chamada)",
        "log_pop22": "Censo 2022 (a06), via 24",
        "regic": "REGIC 2018 (IBGE), via 29",
        "n_conc_cir": "script 32 (protocolo 58): outras celulas do mesmo curso e ciclo na CIR",
        "G-b": "G1 (origem) + escolhas do 12 + quadro do 12 + CIR do TabNet (via 29)"}
    return cel, info


# ---------------------------------------------------------------------------
# Modelo
# ---------------------------------------------------------------------------

def _indicadores(v: pd.Series, nome: str) -> tuple[list[np.ndarray], list[str]]:
    niveis = sorted(v.astype(str).unique().tolist())
    return ([(v.astype(str) == n).to_numpy(dtype=float) for n in niveis[1:]], [f"{nome}[{n}]" for n in niveis[1:]])


def ajustar(d: pd.DataFrame, fe: tuple = (), z: tuple = (), y: str = "preenchida") -> dict:
    """MQO de `y` (padrão: célula preenchida) em IVS/0,100 + efeito fixo de ciclo (+ fatores); CR1 por município.

    `d` já vem sem ausentes nas colunas usadas. Devolve a inclinação por 0,100 de IVS.
    """
    y = d[y].to_numpy(dtype=float)
    cols = [np.ones(len(d)), d["s_mil"].to_numpy(dtype=float) / UNIDADE_X_MIL]
    nomes = ["const", "ivs_por_0100"]
    for cat in ("ciclo",) + tuple(fe):
        c, n = _indicadores(d[cat], cat)
        cols += c
        nomes += n
    for col in z:
        cols.append(d[col].to_numpy(dtype=float))
        nomes.append(col)
    X = np.column_stack(cols)
    r = L.mqp_sanduiche(X, y, np.ones(len(d)), nomes=nomes, protegidas={"const", "ivs_por_0100"},
                        cluster=d["co_ibge"].to_numpy())
    if "erro" in r:
        return {"erro": r["erro"], "n_obs": len(d), "n_municipios": int(d["co_ibge"].nunique())}
    i = r["nomes"].index("ivs_por_0100")
    b, ep = float(r["beta"][i]), float(math.sqrt(r["V"][i, i]))
    descart = [c for c in r["descartadas"] if not c.startswith("ciclo[")]
    return {"inclinacao": b, "ep": ep, "ic95_inf": b - L.Z_975 * ep, "ic95_sup": b + L.Z_975 * ep,
            "p_valor": L.p_normal(b / ep) if ep > 0 else float("nan"), "n_obs": int(r["n"]),
            "n_municipios": int(r["G"]), "descartadas": descart,
            "descartadas_ciclo": [c for c in r["descartadas"] if c.startswith("ciclo[")]}


def nova(tipo: str, fx: dict, janela: str, expl: str, var: str, **kw) -> dict:
    ln = {c: np.nan for c in COLUNAS}
    ln.update({"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "tipo_linha": tipo, "faixa": fx["faixa"],
               "bolsa_mil": fx["bolsa_mil"], "janela": janela, "explicacao": expl, "variante": var,
               "principal_da_explicacao": "", "descricao": "", "efeitos_fixos": "", "covariaveis": "",
               "estimador": "", "status": "EXECUTADO", "motivo_fora": "", "reduz_metade": "", "unidade": "",
               "nota": ""})
    ln.update(kw)
    b = "" if pd.isna(ln["bin_ivs_inf"]) else f"{float(ln['bin_ivs_inf']):.3f}"
    ln["id_linha"] = "|".join(str(x) for x in (tipo, fx["faixa"], janela, expl, var, b))
    return ln


def _preencher(ln: dict, r: dict) -> dict:
    if "erro" in r:
        ln["status"] = "SEM_ESTIMATIVA"
        ln["nota"] = _juntar(ln["nota"], r["erro"])
        ln["n_obs"], ln["n_municipios"] = r["n_obs"], r["n_municipios"]
        return ln
    for k in ("inclinacao", "ep", "ic95_inf", "ic95_sup", "p_valor", "n_obs", "n_municipios"):
        ln[k] = r[k]
    if r["descartadas"]:
        ln["nota"] = _juntar(ln["nota"], f"indicadores colineares descartados: {', '.join(r['descartadas'])}")
    return ln


def fracao_levada(b_depois: float, b_orig: float) -> float:
    """Quanto da subida o fator leva: 1 - depois/original (na mesma amostra); só existe se a subida original > 0."""
    if not (np.isfinite(b_depois) and np.isfinite(b_orig)) or b_orig <= 0:
        return float("nan")
    return 1.0 - b_depois / b_orig


def estimar_linhas(cel: pd.DataFrame) -> list[dict]:
    linhas = []
    for fx in FAIXAS:
        for jan in JANELAS:
            m = mascara(cel, fx, jan)
            if not m.any():
                linhas.append(nova("inclinacao", fx, jan, "ORIGINAL", "principal", status="NAO_SE_APLICA",
                                   descricao="inclinacao original", unidade=UNIDADE, estimador=ESTIMADOR,
                                   nota="faixa sem corte superior: nao ha janela de 0,050 junto ao corte"))
                continue
            d = cel[m]
            r0 = ajustar(d)
            orig = _preencher(nova("inclinacao", fx, jan, "ORIGINAL", "principal", principal_da_explicacao="sim",
                                   descricao="inclinacao original (so efeito fixo de ciclo)", unidade=UNIDADE,
                                   estimador=ESTIMADOR, n_fora=0, ivs_min=float(d["s_mil"].min()) / 1000,
                                   ivs_max=float(d["s_mil"].max()) / 1000,
                                   media_preenchida=float(d["preenchida"].mean()),
                                   media_ivs=float(d["s_mil"].mean()) / 1000), r0)
            linhas.append(orig)
            b_full = float(orig["inclinacao"])
            for expl, var, fe, z, princ, desc in VARIANTES:
                usadas = list(fe) + list(z)
                ok = d[usadas].notna().all(axis=1).to_numpy()
                sub = d[ok]
                fora = int((~ok).sum())
                motivo = "; ".join(f"{COLS_FATOR[c]} ausente: {int(d[c].isna().sum())}" for c in usadas
                                   if d[c].isna().any())
                ln = nova("inclinacao", fx, jan, expl, var, principal_da_explicacao="sim" if princ else "nao",
                          descricao=desc, efeitos_fixos=", ".join(["ciclo"] + [COLS_FATOR[c] for c in fe]),
                          covariaveis=", ".join(COLS_FATOR[c] for c in z), unidade=UNIDADE, estimador=ESTIMADOR,
                          n_fora=fora, motivo_fora=motivo, inclinacao_original=b_full,
                          ivs_min=float(sub["s_mil"].min()) / 1000 if len(sub) else np.nan,
                          ivs_max=float(sub["s_mil"].max()) / 1000 if len(sub) else np.nan)
                rf = ajustar(sub, fe, z)
                ln = _preencher(ln, rf)
                rb = r0 if fora == 0 else ajustar(sub)
                if "erro" not in rb:
                    ln["inclinacao_original_mesma_amostra"] = rb["inclinacao"]
                    ln["ep_original_mesma_amostra"] = rb["ep"]
                if ln["status"] == "EXECUTADO":
                    f = fracao_levada(float(ln["inclinacao"]), float(ln["inclinacao_original_mesma_amostra"]))
                    ln["fracao_da_subida_levada"] = f
                    ln["reduz_metade"] = ("nao_se_aplica" if not np.isfinite(f)
                                          else ("sim" if f >= LIMIAR_METADE else "nao"))
                    if not np.isfinite(f):
                        ln["nota"] = _juntar(ln["nota"], "inclinacao original na mesma amostra <= 0: nao ha subida a "
                                                         "explicar")
                linhas.append(ln)
        # Médias por faixa de IVS de 0,010 (fechada à direita, como a faixa da bolsa), para a figura.
        d = cel[mascara(cel, fx, "faixa_inteira")]
        b = np.ceil(d["s_mil"].to_numpy(dtype=float) / BIN_MIL).astype(int)
        for k in sorted(set(b)):
            g = d[b == k]
            linhas.append(nova("media_bin", fx, "faixa_inteira", "DADOS_CRUS", "media", bin_ivs_inf=(k - 1) * BIN_MIL
                               / 1000, bin_ivs_sup=k * BIN_MIL / 1000, n_celulas_bin=int(len(g)),
                               media_preenchida=float(g["preenchida"].mean()),
                               media_ivs=float(g["s_mil"].mean()) / 1000, n_municipios=int(g["co_ibge"].nunique()),
                               descricao="fracao de celulas preenchidas na faixa de IVS (inf; sup], ciclos 1-3, sem "
                                         "controles", unidade="fracao (x100 = %)"))
        # G-a, descritivo: onde estão as células da faixa e quanto preenchem, por macrorregião.
        for mac in sorted(d["macro"].unique()):
            g = d[d["macro"] == mac]
            linhas.append(nova("regiao", fx, "faixa_inteira", "G-a", mac, n_obs=int(len(g)),
                               n_municipios=int(g["co_ibge"].nunique()), media_preenchida=float(g["preenchida"].mean()),
                               media_ivs=float(g["s_mil"].mean()) / 1000,
                               descricao="celulas da faixa na macrorregiao: n, IVS medio e fracao preenchida (sem "
                                         "controles)", unidade="fracao (x100 = %)"))
        # Balanço: o próprio fator anda junto com o IVS dentro da faixa? (mesmo modelo, fator no lugar do outcome)
        for jan in JANELAS:
            m = mascara(cel, fx, jan)
            if not m.any():
                continue
            dj = cel[m]
            for expl, col, desc, un in BALANCO:
                ok = dj[col].notna().to_numpy()
                ln = nova("balanco", fx, jan, expl, col, descricao=desc, unidade=f"{un} por 0,100 de IVS",
                          estimador=ESTIMADOR.replace("da celula preenchida", "do fator"), n_fora=int((~ok).sum()),
                          media_preenchida=np.nan, media_ivs=float(dj["s_mil"].mean()) / 1000,
                          nota=f"media do fator na amostra: {float(dj.loc[ok, col].mean()):.6g}")
                linhas.append(_preencher(ln, ajustar(dj[ok], y=col)))
    return linhas


def linha_gf(resumo_gf: dict) -> dict:
    fx = {"faixa": "todas", "bolsa_mil": np.nan}
    return nova("relato", fx, "-", "G-f", "relato", status="SEM_FATOR_TESTAVEL",
                descricao="outras politicas que variam com o IVS: sem fator testavel no nivel da celula",
                nota=resumo_gf["situacao"])


def aplicar_bky(est: pd.DataFrame) -> pd.DataFrame:
    est["q_bky"] = np.nan
    m = (est["tipo_linha"] == "inclinacao") & est["p_valor"].notna()
    est.loc[m, "q_bky"] = L.qvalores_bky(est.loc[m, "p_valor"].to_numpy(dtype=float))
    return est


def relato_gf() -> dict:
    """G-f: o que a pesquisa documental do mesmo dia achou, se já estiver no repositório (docs/auditorias/35_*)."""
    achados = sorted(p for p in DIR_AUDITORIAS.glob(PADRAO_AUDITORIA_GF) if p.is_file())
    if achados:
        return {"situacao": "pesquisa documental arquivada: " + ", ".join(rotulo(p) for p in achados),
                "arquivos": [{"caminho": rotulo(p), "sha256": sha256(p)} for p in achados]}
    return {"situacao": "pesquisa documental em andamento em paralelo; quando existir, fica em "
                        f"docs/auditorias/{PADRAO_AUDITORIA_GF} (nao existia na execucao)", "arquivos": []}


def leitura_preregistrada(est: pd.DataFrame) -> dict:
    """§3: um fator que reduz a inclinação pela metade ou mais descreve a subida (associação); nenhum -> não se explica.

    Aplicada em cada faixa × janela com subida original > 0. "Todos juntos" é relatado, mas não é um fator.
    """
    out = {}
    for fx in FAIXAS:
        for jan in JANELAS:
            o = est[(est["tipo_linha"] == "inclinacao") & (est["faixa"] == fx["faixa"]) & (est["janela"] == jan)
                    & (est["explicacao"] == "ORIGINAL")].iloc[0]
            chave = f"{fx['faixa']}|{jan}"
            if o["status"] != "EXECUTADO":
                out[chave] = {"leitura": "NAO_SE_APLICA", "motivo": o["nota"]}
                continue
            b = float(o["inclinacao"])
            ic_exclui = float(o["ic95_inf"]) > 0 or float(o["ic95_sup"]) < 0
            fx_l = est[(est["tipo_linha"] == "inclinacao") & (est["faixa"] == fx["faixa"]) & (est["janela"] == jan)
                       & est["explicacao"].str.startswith("G-") & (est["status"] == "EXECUTADO")]
            if b <= 0:
                out[chave] = {"leitura": "SEM_SUBIDA", "inclinacao_original": b, "ic_exclui_zero": ic_exclui,
                              "fatores_que_reduzem_metade": []}
                continue
            red = fx_l[fx_l["reduz_metade"] == "sim"]
            fatores = sorted(set(red["explicacao"]))
            todos = est[(est["tipo_linha"] == "inclinacao") & (est["faixa"] == fx["faixa"]) & (est["janela"] == jan)
                        & (est["explicacao"] == "TODOS")].iloc[0]
            out[chave] = {"leitura": "FATOR_DESCREVE_A_SUBIDA" if fatores else "SUBIDA_NAO_SE_EXPLICA_COM_OS_DADOS",
                          "inclinacao_original": b, "ic_exclui_zero": ic_exclui,
                          "fatores_que_reduzem_metade": fatores,
                          "variantes_que_reduzem_metade": sorted(f"{r.explicacao} ({r.variante})"
                                                                 for r in red.itertuples()),
                          "todos_juntos_fracao": float(todos["fracao_da_subida_levada"]),
                          "todos_juntos_reduz_metade": todos["reduz_metade"]}
    return out


def estimar_tudo(log=print) -> tuple[pd.DataFrame, dict]:
    B = DQ.carregar()
    log("  dados carregados (script 38)")
    cel, info = preparar(B)
    log(f"  celulas: {len(cel)}; por faixa: {info['celulas_por_faixa']}")
    linhas = estimar_linhas(cel)
    gf = relato_gf()
    linhas.append(linha_gf(gf))
    est = pd.DataFrame(linhas)[COLUNAS]
    if est["id_linha"].duplicated().any():
        raise FalhaValidacao(f"id_linha duplicado: {est.loc[est['id_linha'].duplicated(), 'id_linha'].tolist()[:5]}")
    est = aplicar_bky(est)
    leitura = leitura_preregistrada(est)
    return est, {"info_dados": info, "G-f": gf, "leitura": leitura}




# ---------------------------------------------------------------------------
# Formatação (números sempre lidos das saídas)
# ---------------------------------------------------------------------------

_num, _p, _tab, _int = DQ._num, DQ._p, DQ._tab, DQ._int
FX = {f["faixa"]: f for f in FAIXAS}
ROT_FX = {"R$10mil": "R$ 10 mil", "R$15mil": "R$ 15 mil", "R$20mil": "R$ 20 mil"}
ROT_JAN = {"faixa_inteira": "faixa inteira", "janela_0050_corte_superior": "últimos 0,050 antes do corte"}
TRECHO = {("R$10mil", "faixa_inteira"): "até 0,300", ("R$10mil", "janela_0050_corte_superior"): "0,251 a 0,300",
          ("R$15mil", "faixa_inteira"): "0,301 a 0,400", ("R$15mil", "janela_0050_corte_superior"): "0,351 a 0,400",
          ("R$20mil", "faixa_inteira"): "acima de 0,400"}
NOME_EXPL = {"G-a": "região", "G-b": "candidatos por perto", "G-c": "composição das vagas",
             "G-d": "porte e hierarquia urbana", "G-e": "concorrência", "G-f": "outras políticas",
             "TODOS": "todos juntos"}
ROT_VAR = {("G-a", "macrorregiao"): "macrorregião", ("G-a", "uf"): "UF",
           ("G-b", "uf"): "candidatos na UF por vaga", ("G-b", "cir"): "candidatos na região de saúde por vaga",
           ("G-b", "uf_e_cir"): "os dois", ("G-c", "curso_x_ciclo"): "curso × ciclo",
           ("G-c", "so_cr"): "só cadastro reserva", ("G-c", "tipo_e_gestao"): "tipo e gestão do estabelecimento",
           ("G-c", "todos"): "os três", ("G-d", "log_pop"): "log(população 2022)", ("G-d", "regic"): "REGIC",
           ("G-d", "log_pop_e_regic"): "os dois", ("G-e", "n_celulas_cir"): "células do mesmo curso na região",
           ("TODOS", "todos_juntos"): "G-a (UF) + G-b + G-c + G-d + G-e"}
ROT_BAL = {"norte_ou_nordeste": ("célula no Norte ou Nordeste", "pct"),
           "cand_uf_por_vaga": ("candidatos com origem na UF, por vaga", "num"),
           "cand_cir_por_vaga": ("candidatos com origem na região de saúde, por vaga", "num"),
           "so_cr": ("célula só de cadastro reserva", "pct"), "hospital_geral": ("hospital geral", "pct"),
           "gestao_estadual": ("gestão estadual", "pct"), "log_pop22": ("log(população 2022)", "num"),
           "regic_nivel": ("nível REGIC (1 metrópole … 5 centro local)", "num"),
           "n_conc_cir": ("outras células do curso na região de saúde", "num")}
# Linhas da figura de barras e do topo da tabela-resumo: a variante principal de cada explicação (G-a nas duas).
LINHAS_RESUMO = [("G-a", "macrorregiao"), ("G-a", "uf"), ("G-b", "uf_e_cir"), ("G-c", "todos"),
                 ("G-d", "log_pop_e_regic"), ("G-e", "n_celulas_cir"), ("TODOS", "todos_juntos")]
COMBOS = [(f, j) for f in ("R$10mil", "R$15mil", "R$20mil") for j in JANELAS
          if not (f == "R$20mil" and j == "janela_0050_corte_superior")]

# G-f: o que a auditoria 18 já registra sobre regras de IVS dentro das faixas (âncoras conferidas no teste).
REGRAS_GF = [
    {"texto": "Na faixa de R$ 15 mil (0,301 a 0,400) todo município está na mesma classe de IVS (\"média\"): as regras "
              "por classe que a auditoria 18 lista (estrato do IED no cofinanciamento da APS, incentivo de nutrição, "
              "priorização de eMulti) não mudam dentro dela.",
     "secao": "§2.5 e §2.7", "ancora": "código 3 vai de\n  0,301 a 0,400"},
    {"texto": "Dentro da faixa de R$ 10 mil há um degrau em 0,200 (muito baixa → baixa): o estrato do IED muda no "
              "porte 1 (até 20 mil hab.). Dentro da faixa de R$ 20 mil há um degrau em 0,500 (alta → muito alta), nos "
              "portes 1 a 3 do IED. São degraus, não uma subida contínua, e nenhum cai nos últimos 0,050 antes de "
              "0,300 ou de 0,400.",
     "secao": "§2.5", "ancora": "| 1 — até 20 mil | 1 | 2 | 3 | 3 | 4 |"},
    {"texto": "A priorização de eMulti (Portaria 635/2023) tem cortes em 0,2, 0,3, 0,4 e 0,5: também degraus, em 0,200 "
              "dentro da faixa de R$ 10 mil e em 0,500 dentro da de R$ 20 mil.",
     "secao": "§2.7", "ancora": "0,2/0,3/0,4/0,5"},
    {"texto": "O único índice contínuo citado é o ICSD do SUS Digital, que não é o IVS e está marcado como não "
              "verificado.", "secao": "§2.7", "ancora": "índice ICSD contínuo, sem corte"},
]


def _ppx(v, casas=1, sinal=True) -> str:
    try:
        return _num(float(v) * 100, casas, sinal)
    except (TypeError, ValueError):
        return "—"


def _ic(r) -> str:
    return f"[{_ppx(r['ic95_inf'])}; {_ppx(r['ic95_sup'])}]"


def _pct(f) -> str:
    try:
        f = float(f)
    except (TypeError, ValueError):
        return "—"
    if not math.isfinite(f):
        return "—"
    return f"{f * 100:.0f}%".replace("-", "−")


def _bloco(nome: str, corpo: str) -> str:
    return f"<!-- GF:{nome}:inicio -->\n{corpo.strip()}\n<!-- GF:{nome}:fim -->"


def _sel(est: pd.DataFrame, **f) -> pd.DataFrame:
    m = np.ones(len(est), dtype=bool)
    for k, v in f.items():
        m &= (est[k].astype(str) == str(v)).to_numpy()
    return est[m]


def _um(est: pd.DataFrame, **f) -> pd.Series:
    s = _sel(est, **f)
    if len(s) != 1:
        raise FalhaValidacao(f"esperada 1 linha para {f}, achadas {len(s)}")
    return s.iloc[0]


def _orig(est, fx, jan) -> pd.Series:
    return _um(est, tipo_linha="inclinacao", faixa=fx, janela=jan, explicacao="ORIGINAL")


def _var(est, fx, jan, expl, var) -> pd.Series:
    return _um(est, tipo_linha="inclinacao", faixa=fx, janela=jan, explicacao=expl, variante=var)


def _excl(r) -> bool:
    return float(r["ic95_inf"]) > 0 or float(r["ic95_sup"]) < 0


def _sim(r) -> str:
    return {"sim": "**sim**", "nao": "não", "nao_se_aplica": "não se aplica (sem subida)"}.get(r["reduz_metade"], "—")


def _principal(expl: str) -> str:
    return [x[1] for x in VARIANTES if x[0] == expl and x[4]][0]


# ---------------------------------------------------------------------------
# Figuras (legíveis em slide; "Como ler" vai na imagem, no doc e no resumo)
# ---------------------------------------------------------------------------

COR_ORIG = "#eb6834"
COR_AJUST = "#2a78d6"
CINZA = "#a3a29c"
CINZA_CLARO = "#d9d8d3"
TINTA = "#0b0b0b"
TINTA_2 = "#52514e"
SUPERF = "#fcfcfb"
COMO_LER = {
    "GF_medias_por_ivs.png": "Cada ponto é a fração de células abertas preenchidas na 1ª chamada numa faixa de IVS de "
                             "0,010 (tamanho = número de células). A linha laranja é a reta da faixa inteira; a azul "
                             "tracejada tem a inclinação que sobra depois de comparar só células parecidas em região "
                             "(UF), candidatos por perto, composição, porte e concorrência; as duas passam pelo ponto "
                             "médio da faixa. A linha preta pontilhada é a reta só nos últimos 0,050 antes do corte. "
                             "Dentro de uma faixa a bolsa é a mesma.",
    "GF_inclinacao_fatores.png": "Cada par de barras mostra quanto o preenchimento sobe a cada 0,100 de IVS dentro da "
                                 "faixa: a barra cinza é a subida original (na mesma amostra) e a azul, a subida depois de comparar só "
                                 "células iguais naquele fator (mesma amostra). Se a azul fica com metade ou menos da "
                                 "cinza, a subida anda junto com aquele fator. Traço = IC 95%.",
    "GF_inclinacao_fatores_janela.png": "Igual à figura anterior, mas só com as células dos últimos 0,050 de IVS antes "
                                        "do corte (0,251 a 0,300 e 0,351 a 0,400), o trecho que a RDD usa do lado de "
                                        "baixo. A faixa de R$ 20 mil não tem corte de cima.",
}
DETALHE_FIG = {
    "GF_medias_por_ivs.png": "Médias de GF_estimativas.csv (tipo_linha = media_bin; faixas de 0,010 fechadas à direita, "
                             "como as faixas da bolsa). Retas: inclinação de tipo_linha = inclinacao (ORIGINAL e TODOS), "
                             "MQO com efeito fixo de ciclo, ancoradas na média de IVS e de preenchimento da amostra "
                             "(faixa inteira ou janela). A reta 'todos juntos' é estimada nas células com todos os "
                             "fatores definidos.",
    "GF_inclinacao_fatores.png": "Inclinação em p.p. por 0,100 de IVS (MQO, efeito fixo de ciclo, CR1 por município). "
                                 "Barra cinza = inclinacao_original_mesma_amostra; barra azul = inclinacao depois do "
                                 "fator (GF_estimativas.csv). G-b, G-c e G-d na variante principal (todos os itens).",
    "GF_inclinacao_fatores_janela.png": "Como GF_inclinacao_fatores.png, com janela = janela_0050_corte_superior.",
}


def _barras(ax, est, fx, jan, mostrar_rotulos: bool) -> None:
    o = _orig(est, fx, jan)
    rot = ["Original"] + [f"{e} {ROT_VAR[(e, v)]}" if e == "G-a" else
                          ("Todos juntos" if e == "TODOS" else f"{e} {NOME_EXPL[e]}") for e, v in LINHAS_RESUMO]
    ys = np.arange(len(rot))[::-1].astype(float)
    ax.axvline(0, color=TINTA_2, lw=1)
    b0 = float(o["inclinacao"]) * 100
    ax.barh(ys[0], b0, height=0.6, color=COR_ORIG)
    ax.errorbar(b0, ys[0], xerr=[[b0 - float(o["ic95_inf"]) * 100], [float(o["ic95_sup"]) * 100 - b0]],
                color=TINTA_2, lw=1.4, capsize=0)
    for y, (e, v) in zip(ys[1:], LINHAS_RESUMO):
        r = _var(est, fx, jan, e, v)
        antes, depois = float(r["inclinacao_original_mesma_amostra"]) * 100, float(r["inclinacao"]) * 100
        ax.barh(y + 0.19, antes, height=0.36, color=CINZA_CLARO, edgecolor=CINZA)
        ax.barh(y - 0.19, depois, height=0.36, color=COR_AJUST)
        ax.errorbar(depois, y - 0.19, xerr=[[depois - float(r["ic95_inf"]) * 100],
                                            [float(r["ic95_sup"]) * 100 - depois]], color=TINTA_2, lw=1.2, capsize=0)
    ax.set_yticks(ys)
    if mostrar_rotulos:
        ax.set_yticklabels(rot)
    else:
        ax.tick_params(labelleft=False)
    ax.set_title(f"{ROT_FX[fx]}: IVS {TRECHO[(fx, jan)]}")
    ax.set_xlabel("p.p. por 0,100 de IVS")
    from matplotlib.ticker import FuncFormatter
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",").replace("-", "−")))
    ax.spines[["top", "right"]].set_visible(False)


def _rodape(fig, nome: str, largura: int) -> None:
    import textwrap
    fig.text(0.012, 0.015, "\n".join(textwrap.wrap("Como ler: " + COMO_LER[nome], largura)), fontsize=13,
             color=TINTA, va="bottom", ha="left")


def gerar_figuras(est: pd.DataFrame, dir_fig: Path) -> list[dict]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    from matplotlib.ticker import FuncFormatter
    dir_fig.mkdir(parents=True, exist_ok=True)
    for antigo in dir_fig.glob("*.png"):
        antigo.unlink()
    plt.rcParams.update({"font.size": 14, "axes.titlesize": 16, "axes.labelsize": 14, "xtick.labelsize": 13,
                         "ytick.labelsize": 13, "axes.edgecolor": TINTA_2, "axes.labelcolor": TINTA,
                         "text.color": TINTA, "xtick.color": TINTA_2, "ytick.color": TINTA_2,
                         "figure.facecolor": SUPERF, "axes.facecolor": SUPERF, "savefig.facecolor": SUPERF})
    virgula = FuncFormatter(lambda v, _: f"{v:.2f}".replace(".", ","))
    feitas = []
    # (1) médias por faixa de IVS de 0,010, reta original e ajustada
    nome = "GF_medias_por_ivs.png"
    fig, eixos = plt.subplots(1, 3, figsize=(18, 8.4), sharey=True, gridspec_kw={"width_ratios": [2.0, 1.0, 3.3]})
    for ax, fx in zip(eixos, ("R$10mil", "R$15mil", "R$20mil")):
        b = _sel(est, tipo_linha="media_bin", faixa=fx)
        x = (b["bin_ivs_inf"].astype(float) + b["bin_ivs_sup"].astype(float)) / 2
        ax.scatter(x, b["media_preenchida"].astype(float) * 100, s=b["n_celulas_bin"].astype(float) * 1.6 + 8,
                   color=TINTA_2, alpha=0.5, edgecolors=SUPERF, lw=0.8, zorder=2)
        o = _orig(est, fx, "faixa_inteira")
        t = _var(est, fx, "faixa_inteira", "TODOS", "todos_juntos")
        xs = np.array([float(o["ivs_min"]), float(o["ivs_max"])])
        x0, y0 = float(o["media_ivs"]), float(o["media_preenchida"])
        ax.plot(xs, (y0 + float(o["inclinacao"]) * (xs - x0) * 10) * 100, color=COR_ORIG, lw=3.2, zorder=3)
        ax.plot(xs, (y0 + float(t["inclinacao"]) * (xs - x0) * 10) * 100, color=COR_AJUST, lw=3.2, ls="--", zorder=3)
        if FX[fx]["hi"] is not None:
            w = _orig(est, fx, "janela_0050_corte_superior")
            xw = np.array([float(w["ivs_min"]), float(w["ivs_max"])])
            ax.plot(xw, (float(w["media_preenchida"]) + float(w["inclinacao"]) * (xw - float(w["media_ivs"])) * 10)
                    * 100, color=TINTA, lw=2.6, ls=":", zorder=4)
            ax.axvline(FX[fx]["hi"] / 1000, color=TINTA_2, lw=1, ls="--")
        ax.set_title(f"{ROT_FX[fx]}\n{_ppx(o['inclinacao'])} → {_ppx(t['inclinacao'])} p.p. por 0,100", fontsize=16)
        ax.set_xlabel("IVS 2010")
        ax.xaxis.set_major_formatter(virgula)
        ax.spines[["top", "right"]].set_visible(False)
        ax.set_ylim(0, 100)
    eixos[0].set_ylabel("células preenchidas na 1ª chamada (%)")
    leg = [Line2D([], [], color=COR_ORIG, lw=3.2, label="reta da faixa (original)"),
           Line2D([], [], color=COR_AJUST, lw=3.2, ls="--", label="depois de todos os fatores"),
           Line2D([], [], color=TINTA, lw=2.6, ls=":", label="reta nos últimos 0,050 antes do corte"),
           Line2D([], [], marker="o", color=TINTA_2, alpha=0.5, lw=0, markersize=11, label="média a cada 0,010")]
    fig.legend(handles=leg, loc="upper center", ncol=4, frameon=False, fontsize=13, bbox_to_anchor=(0.5, 0.945))
    fig.suptitle("Dentro de cada faixa a bolsa é a mesma: como o preenchimento muda com o IVS", fontsize=19, y=0.99)
    fig.tight_layout(rect=(0, 0.13, 1, 0.9))
    _rodape(fig, nome, 165)
    fig.savefig(dir_fig / nome, dpi=150)
    plt.close(fig)
    feitas.append(nome)
    # (2) e (3) barras: inclinação antes e depois de cada fator
    leg = [Patch(color=COR_ORIG, label="subida original"),
           Patch(facecolor=CINZA_CLARO, edgecolor=CINZA, label="original na mesma amostra"),
           Patch(color=COR_AJUST, label="depois do fator")]
    for nome, jan, faixas, tam, titulo, larg in (
            ("GF_inclinacao_fatores.png", "faixa_inteira", ("R$10mil", "R$15mil", "R$20mil"), (18, 8.6),
             "Quanto da subida com o IVS sobra depois de cada fator (faixa inteira)", 185),
            ("GF_inclinacao_fatores_janela.png", "janela_0050_corte_superior", ("R$10mil", "R$15mil"), (16, 8.6),
             "Quanto da subida sobra depois de cada fator (últimos 0,050 antes do corte)", 150)):
        fig, eixos = plt.subplots(1, len(faixas), figsize=tam)
        for i, (ax, fx) in enumerate(zip(eixos, faixas)):
            _barras(ax, est, fx, jan, i == 0)
        fig.legend(handles=leg, loc="upper center", ncol=3, frameon=False, fontsize=13, bbox_to_anchor=(0.5, 0.945))
        fig.suptitle(titulo, fontsize=19, y=0.99)
        fig.tight_layout(rect=(0, 0.1, 1, 0.9))
        _rodape(fig, nome, larg)
        fig.savefig(dir_fig / nome, dpi=150)
        plt.close(fig)
        feitas.append(nome)
    return [{"arquivo": rotulo(dir_fig / f), "como_ler": COMO_LER[f], "detalhe_tecnico": DETALHE_FIG[f]}
            for f in feitas]


# ---------------------------------------------------------------------------
# Documento 57m (gerado inteiro a partir das saídas)
# ---------------------------------------------------------------------------

NOME_MACRO = {"NORTE": "Norte", "NORDESTE": "Nordeste", "SUDESTE": "Sudeste", "SUL": "Sul",
              "CENTRO OESTE": "Centro-Oeste"}


def regiao_destaque(est, fx) -> dict:
    """Macrorregião que mais preenche na faixa, se ela também tem o maior IVS médio (lido das linhas `regiao`)."""
    reg = _sel(est, tipo_linha="regiao", faixa=fx).copy()
    reg["p"], reg["i"] = reg["media_preenchida"].astype(float), reg["media_ivs"].astype(float)
    top = reg.loc[reg["p"].idxmax()]
    outras = reg[reg["variante"] != top["variante"]]
    return {"nome": NOME_MACRO[top["variante"]], "p": float(top["p"]), "ivs": float(top["i"]),
            "n": int(top["n_obs"]), "mun": int(top["n_municipios"]), "maior_ivs": bool(top["i"] >= reg["i"].max()),
            "p_min": float(outras["p"].min()), "p_max": float(outras["p"].max()),
            "ivs_max_outras": float(outras["i"].max())}


def _fatores(lr) -> str:
    return ", ".join(f"{f} ({NOME_EXPL[f]})" for f in lr.get("fatores_que_reduzem_metade", [])) or "nenhum"


def resposta_curta(est: pd.DataFrame, resumo: dict) -> str:
    lt = resumo["leitura"]
    o10, o10j = _orig(est, "R$10mil", "faixa_inteira"), _orig(est, "R$10mil", "janela_0050_corte_superior")
    o15, o15j = _orig(est, "R$15mil", "faixa_inteira"), _orig(est, "R$15mil", "janela_0050_corte_superior")
    o20 = _orig(est, "R$20mil", "faixa_inteira")
    uf10 = _var(est, "R$10mil", "faixa_inteira", "G-a", "uf")
    mac10 = _var(est, "R$10mil", "faixa_inteira", "G-a", "macrorregiao")
    t10 = _var(est, "R$10mil", "faixa_inteira", "TODOS", "todos_juntos")
    t10j = _var(est, "R$10mil", "janela_0050_corte_superior", "TODOS", "todos_juntos")
    bal = _um(est, tipo_linha="balanco", faixa="R$10mil", janela="faixa_inteira", variante="norte_ou_nordeste")
    l10, l10j = lt["R$10mil|faixa_inteira"], lt["R$10mil|janela_0050_corte_superior"]
    l15, l15j = lt["R$15mil|faixa_inteira"], lt["R$15mil|janela_0050_corte_superior"]
    regiao10 = "G-a" in l10.get("fatores_que_reduzem_metade", [])
    rd = regiao_destaque(est, "R$10mil")
    janela_sem = l10j["leitura"] == "SUBIDA_NAO_SE_EXPLICA_COM_OS_DADOS"
    par = [
        f"**Faixa de R$ 10 mil (IVS até 0,300).** A fração de células abertas preenchidas na 1ª chamada sobe "
        f"{_ppx(o10['inclinacao'])} p.p. a cada 0,100 de IVS (IC 95% {_ic(o10)}; {_int(o10['n_obs'])} células). "
        + (f"Quase toda essa subida anda junto com a **região**: comparando só células da mesma UF, sobram "
           f"{_ppx(uf10['inclinacao'])} p.p. ({_pct(uf10['fracao_da_subida_levada'])} da subida some); só com a "
           f"macrorregião, sobram {_ppx(mac10['inclinacao'])} p.p. Na faixa, o {rd['nome']} é a região que mais "
           f"preenche ({_ppx(rd['p'], 0, False)}% das células, contra {_ppx(rd['p_min'], 0, False)}% a "
           f"{_ppx(rd['p_max'], 0, False)}% nas outras) e "
           + (f"a de IVS médio mais alto ({_num(rd['ivs'], 3, False)}, contra no máximo "
              f"{_num(rd['ivs_max_outras'], 3, False)} nas outras)" if rd["maior_ivs"] else
              f"tem IVS médio de {_num(rd['ivs'], 3, False)}")
           + f"; são {rd['n']} células em só {rd['mun']} municípios. Cada 0,100 de IVS a mais vem com "
           f"{_ppx(bal['inclinacao'], 0)} p.p. a mais de células no Norte ou no Nordeste. "
           if regiao10 else f"Fatores que reduzem a subida pela metade: {_fatores(l10)}. ")
        + f"Com todos os fatores juntos, sobram {_ppx(t10['inclinacao'])} p.p.",
        f"**Perto do corte de 0,300 (IVS de 0,251 a 0,300)** a subida é mais forte: {_ppx(o10j['inclinacao'])} p.p. "
        f"por 0,100 (IC 95% {_ic(o10j)}). "
        + (f"Ali nenhum fator a reduz pela metade; com todos juntos ainda sobram {_ppx(t10j['inclinacao'])} p.p. "
           f"({_pct(t10j['fracao_da_subida_levada'])} levados). Esse trecho não se explica com os dados disponíveis. "
           if janela_sem else
           f"Fatores que a reduzem pela metade: {_fatores(l10j)}; com todos juntos sobram "
           f"{_ppx(t10j['inclinacao'])} p.p. ")
        + "É o mesmo trecho que a RDD usa do lado de baixo de 0,300: quanto mais íngreme ele é, mais alto fica o "
          "ponto de partida do lado de R$ 10 mil no corte.",
        f"**Faixa de R$ 15 mil (0,301 a 0,400).** A subida é menor e incerta: {_ppx(o15['inclinacao'])} p.p. por "
        f"0,100 (IC 95% {_ic(o15)}{'' if _excl(o15) else ', que inclui zero'}); nos últimos 0,050, "
        f"{_ppx(o15j['inclinacao'])} p.p. (IC 95% {_ic(o15j)}). Fatores que a reduzem pela metade: na faixa inteira, "
        f"{_fatores(l15)}; nos últimos 0,050, {_fatores(l15j)}.",
        f"**Faixa de R$ 20 mil (acima de 0,400).** Não há subida: o preenchimento cai "
        f"{_ppx(-float(o20['inclinacao']), 1, False)} p.p. a cada 0,100 de IVS (IC 95% {_ic(o20)}).",
    ]
    if regiao10 and janela_sem and rd["maior_ivs"]:
        par.append("**Para dizer na banca:** \"Dentro da faixa de R$ 10 mil, onde a bolsa é a mesma, os municípios "
                   "mais vulneráveis preenchem mais vagas. Isso anda junto com a região: os de IVS mais alto da faixa "
                   f"estão mais no {rd['nome']}, onde as vagas preenchem mais, e comparando municípios da mesma UF a "
                   "subida quase some. "
                   "Só nos últimos 0,050 antes de 0,300 sobra uma subida forte que nenhum dado nosso acompanha. Na "
                   "faixa de R$ 15 mil a subida é pequena e incerta; na de R$ 20 mil o preenchimento cai. É "
                   "descrição: mostra com o que a subida anda junto, não por quê.\"")
    else:
        par.append("**Para dizer na banca:** ver a tabela da seção 9 e a leitura da seção 10; tudo é descritivo.")
    return "\n\n".join(par)


def tabela_original(est) -> str:
    linhas = []
    for fx, jan in COMBOS:
        o = _orig(est, fx, jan)
        linhas.append([ROT_FX[fx], TRECHO[(fx, jan)], _int(o["n_obs"]), _int(o["n_municipios"]),
                       _ppx(o["media_preenchida"], 1, False), f"**{_ppx(o['inclinacao'])}**", _ic(o), _p(o["p_valor"]),
                       _p(o["q_bky"])])
    linhas.append(["R$ 20 mil", "últimos 0,050", "—", "—", "—", "—", "—", "—", "não se aplica (sem corte de cima)"])
    return _tab(["Faixa", "IVS", "Células", "Municípios", "Preenchidas (%)", "Inclinação (p.p. por 0,100)", "IC 95%",
                 "p", "q BKY"], linhas)


def tabela_fator(est, expl) -> str:
    linhas = []
    for fx, jan in COMBOS:
        for x in VARIANTES:
            if x[0] != expl:
                continue
            r = _var(est, fx, jan, expl, x[1])
            linhas.append([ROT_FX[fx], TRECHO[(fx, jan)], ROT_VAR[(expl, x[1])], _int(r["n_obs"]),
                           _ppx(r["inclinacao_original_mesma_amostra"]), f"**{_ppx(r['inclinacao'])}**", _ic(r),
                           _pct(r["fracao_da_subida_levada"]), _sim(r), _p(r["q_bky"])])
    return _tab(["Faixa", "IVS", "Fator", "Células", "Original (mesma amostra)", "Depois do fator", "IC 95%",
                 "Quanto da subida leva", "Reduz pela metade?", "q BKY"], linhas)


def tabela_balanco(est, expl) -> str:
    linhas = []
    for fx, jan in COMBOS:
        for _, r in _sel(est, tipo_linha="balanco", faixa=fx, janela=jan, explicacao=expl).iterrows():
            rot, tipo = ROT_BAL[r["variante"]]
            media = float(str(r["nota"]).split(": ")[-1])
            if tipo == "pct":
                vals = [_ppx(media, 1, False) + "%"] + [_ppx(r[k]) + " p.p." for k in ("inclinacao", "ic95_inf",
                                                                                         "ic95_sup")]
            else:
                vals = [_num(media, 2, False)] + [_num(r[k], 3) for k in ("inclinacao", "ic95_inf", "ic95_sup")]
            linhas.append([ROT_FX[fx], TRECHO[(fx, jan)], rot, vals[0], vals[1], f"[{vals[2]}; {vals[3]}]",
                           _int(r["n_fora"])])
    return _tab(["Faixa", "IVS", "Fator", "Média na amostra", "Variação do fator por 0,100 de IVS", "IC 95%",
                 "Células sem o fator"], linhas)


def tabela_regiao(est) -> str:
    linhas = []
    for fx in ("R$10mil", "R$15mil", "R$20mil"):
        for _, r in _sel(est, tipo_linha="regiao", faixa=fx).iterrows():
            linhas.append([ROT_FX[fx], r["variante"].title().replace("Centro Oeste", "Centro-Oeste"), _int(r["n_obs"]),
                           _int(r["n_municipios"]), _num(r["media_ivs"], 3, False),
                           _ppx(r["media_preenchida"], 1, False)])
    return _tab(["Faixa", "Macrorregião", "Células", "Municípios", "IVS médio", "Preenchidas (%)"], linhas)


def frase_fator(est, expl) -> str:
    princ = _principal(expl)
    partes = []
    for fx, jan in COMBOS:
        r = _var(est, fx, jan, expl, princ)
        if r["reduz_metade"] != "nao_se_aplica":
            partes.append(f"{ROT_FX[fx]}, {ROT_JAN[jan]}: de {_ppx(r['inclinacao_original_mesma_amostra'])} para "
                          f"{_ppx(r['inclinacao'])} p.p. ({_pct(r['fracao_da_subida_levada'])} da subida"
                          f"{', reduz pela metade' if r['reduz_metade'] == 'sim' else ''})")
    return f"**Leitura (variante principal: {ROT_VAR[(expl, princ)]}).** " + "; ".join(partes) + "."


def tabela_quanto(est) -> str:
    cab = ["Fator"] + [f"{ROT_FX[f]}, IVS {TRECHO[(f, j)]}" for f, j in COMBOS]
    linhas = [["**Subida original** (p.p. por 0,100)"] + [_ppx(_orig(est, f, j)["inclinacao"]) for f, j in COMBOS]]
    ordem = [(x[0], x[1]) for x in VARIANTES]
    for e, v in ordem:
        cel = []
        for f, j in COMBOS:
            r = _var(est, f, j, e, v)
            t = _pct(r["fracao_da_subida_levada"])
            cel.append(f"**{t}**" if r["reduz_metade"] == "sim" else t)
        rot = (f"{e} {NOME_EXPL[e]}: {ROT_VAR[(e, v)]}" if e != "TODOS"
               else f"Todos juntos ({ROT_VAR[(e, v)]}; não é um fator)")
        linhas.append([rot] + cel)
    return _tab(cab, linhas)


ROT_LEITURA = {"FATOR_DESCREVE_A_SUBIDA": "o fator descreve a subida (associação)",
               "SUBIDA_NAO_SE_EXPLICA_COM_OS_DADOS": "a subida não se explica com os dados disponíveis",
               "SEM_SUBIDA": "não há subida (a inclinação é negativa)", "NAO_SE_APLICA": "não se aplica"}


def tabela_leitura(est, resumo) -> str:
    linhas = []
    for fx in ("R$10mil", "R$15mil", "R$20mil"):
        for jan in JANELAS:
            lr = resumo["leitura"][f"{fx}|{jan}"]
            if lr["leitura"] == "NAO_SE_APLICA":
                linhas.append([ROT_FX[fx], ROT_JAN[jan], "—", "—", "—", ROT_LEITURA[lr["leitura"]]])
                continue
            o = _orig(est, fx, jan)
            linhas.append([ROT_FX[fx], ROT_JAN[jan], f"{_ppx(o['inclinacao'])} {_ic(o)}",
                           ", ".join(lr.get("variantes_que_reduzem_metade", [])) or "nenhum",
                           _pct(lr["todos_juntos_fracao"]) if "todos_juntos_fracao" in lr else "—",
                           f"**{ROT_LEITURA[lr['leitura']]}**"])
    return _tab(["Faixa", "Trecho", "Subida original [IC 95%]", "Fatores que reduzem pela metade",
                 "Todos juntos levam", "Leitura (§3)"], linhas)


def secao_gf(resumo) -> str:
    gf = resumo["G-f"]
    linhas = [f"- **Pesquisa documental do mesmo dia:** {gf['situacao_doc']}"]
    linhas += [f"- {r['texto']} ([auditoria 18](../auditorias/18_politicas_nos_mesmos_cortes_ivs.md), {r['secao']})"
               for r in resumo["regras_gf_auditoria_18"]]
    return "Não há fator testável no nível da célula. Relato:\n\n" + "\n".join(linhas)


LIMITES = [
    "- **Descritivo e pós-resultado.** A subida foi vista na figura de dados crus antes de o protocolo ser escrito. "
    "Nenhuma linha é primária; o BKY corre entre todas as inclinações do preenchimento (coluna `q_bky`).",
    "- **Não é contraste causal.** Dentro da faixa a bolsa é constante: a inclinação compara células com a mesma "
    "bolsa e IVS diferente. \"Reduz pela metade\" quer dizer que a subida anda junto com o fator, não que o fator a "
    "produz.",
    "- **Fatores formados depois do anúncio.** Candidatos por perto (G-b), composição das vagas (G-c) e concorrência "
    "(G-e) se formam depois de a faixa ser conhecida. Comparar células iguais nesses fatores descreve, não isola.",
    "- **Região é um rótulo largo.** O efeito fixo de UF compara células da mesma UF; tudo o que muda entre UFs "
    "(mercado médico, rede, gestão estadual, outras políticas) sai junto.",
    "- **Fração da subida levada.** É 1 − (depois ÷ original na mesma amostra) e só existe quando a subida original é "
    "positiva. Passa de 100% quando a inclinação troca de sinal; com subida original pequena e incerta (faixa de "
    "R$ 15 mil), a fração é instável.",
    "- **Ausências registradas, nada imputado:** tipo do estabelecimento fora do cardápio do ciclo 3; células de "
    "município sem região de saúde (G-b na região de saúde e G-e); candidatos sem origem no G1 não entram na contagem "
    "do G-b.",
]

DECISOES = [
    "Base: celulas abertas do A3 (adendo §7 do protocolo 48), ciclos 1-3 juntos, lidas por carregar() do script 38 "
    "(que chama carregar_tudo() do 24); faixa pelo IVS 2010 oficial (s <= 0,300; 0,301-0,400; > 0,400), conferida "
    "contra a faixa anunciada do quadro.",
    "Modelo: MQO da celula preenchida (>= 1 alocado na 1a chamada) em IVS/0,100 com efeito fixo de ciclo; EP CR1 "
    "agrupado por municipio; IC e p pela normal (como a rdd_lib).",
    "Janela de 0,050 junto ao corte superior: 0,250 < IVS <= 0,300 e 0,350 < IVS <= 0,400 (|IVS - corte| < 0,050, "
    "como a janela da RDD); a faixa de R$ 20 mil nao tem corte superior (linha NAO_SE_APLICA).",
    "Fatores: indicadores para as categoricas (1a categoria em ordem = base; indicador colinear descartado de forma "
    "deterministica e anotado); continuas em nivel. Cada fator e comparado com a inclinacao original na mesma amostra "
    "(celulas com o fator definido).",
    "G-a: macrorregiao e UF pelo codigo IBGE (conferidas contra a regiao do quadro). Variante principal (e a usada em "
    "'todos juntos'): UF.",
    "G-b: candidatos com alguma opcao no curso e ciclo, origem principal do G1 (regra g1_cpf_nome) na mesma UF ou "
    "CIR da celula, divididos pelas vagas oferecidas (imediatas + CR) do mesmo curso e ciclo naquela UF ou CIR (a "
    "propria celula incluida). 'Por vaga oferecida' lido como razao do mercado, nao da celula.",
    "G-c: efeito fixo de curso x ciclo; indicador de celula so de cadastro reserva; tipo (cardapio do ciclo 3) e "
    "gestao (quadro da 1a chamada) do estabelecimento, como no D-b do script 38.",
    "G-d: log(populacao 2022) e nivel REGIC 2018 como efeito fixo. G-e: outras celulas do mesmo curso e ciclo na CIR "
    "(exposicao 'mesmo_curso' do script 32).",
    "Fracao da subida levada = 1 - depois / original na mesma amostra, so com original > 0; reduz pela metade = "
    "fracao >= 0,5. Leitura do §3 por faixa x trecho; 'todos juntos' e relatado, mas nao conta como fator.",
    "BKY entre todas as inclinacoes do preenchimento (originais e depois de cada fator); balancos e medias nao entram.",
    "Balanco (fora do protocolo, descritivo): cada fator continuo ou indicador no lugar do preenchimento, mesmo modelo, "
    "para mostrar se o proprio fator anda junto com o IVS dentro da faixa.",
    "G-f: relato. A pesquisa documental do mesmo dia roda em paralelo; o script procura docs/auditorias/35_* na "
    "execucao e registra o que achou no resumo.",
]


def gerar_doc(est: pd.DataFrame, resumo: dict) -> str:
    figs = resumo["saidas"]["figuras"]
    info = resumo["info_dados"]
    d = DATA_EXECUCAO
    partes = [f"""# 57m. Por que o preenchimento sobe com o IVS dentro das faixas da bolsa? (descritivo, protocolo 62)

> **Data:** {d[8:]}/{d[5:7]}/{d[:4]}.<br>
> **Protocolo:** [`62_protocolo_gradiente_dentro_das_faixas.md`](62_protocolo_gradiente_dentro_das_faixas.md),
> congelado antes de qualquer conta (SHA-256 em `protocolo` de `GF_resumo.json`).<br>
> **Origem:** a figura de dados crus do deck (`output/apresentacao_banca2/exp_rdd_crua.png`), em que o preenchimento
> parece subir com o IVS nas faixas de R$ 10 e de R$ 15 mil.<br>
> **Estatuto:** `{ESTATUTO}`. **Descritivo e pós-resultado**: não é contraste causal e não muda nenhum protocolo
> anterior. Dentro de cada faixa a bolsa é constante; nada aqui é efeito da bolsa, da participação no PMM-E ou do
> Agora Tem Especialistas. Toda linha de `GF_estimativas.csv` tem `natureza_dos_dados = EMPIRICO`.<br>
> **Script:** `scripts/rdd_bolsa/39_gradiente_faixas.py`. **Saídas:** `output/rdd_bolsa/GF_estimativas.csv`,
> `GF_resumo.json`, `GF_figuras/`. **Testes:** `tests/test_gradiente_faixas.py`.<br>
> **Números:** nenhum é digitado. Os blocos entre marcadores `<!-- GF:... -->` são regravados das saídas por
> `39_gradiente_faixas.py --atualizar-doc`; o teste confere que o documento é idêntico ao gerado."""]
    partes.append("## 1. Resposta curta\n\n" + _bloco("resposta_curta", resposta_curta(est, resumo)))
    partes.append(
        "## 2. O que se mede\n\n"
        "Células abertas (estabelecimento × curso) do quadro da 1ª chamada dos ciclos 1–3, a mesma base do A3 (adendo "
        "§7 do protocolo 48). Para cada faixa da bolsa, um modelo de probabilidade linear da célula preenchida (≥ 1 "
        "alocado na 1ª chamada) no IVS 2010 oficial contínuo, com efeito fixo de ciclo e erro-padrão agrupado por "
        "município. A inclinação é a variação, em pontos percentuais, a cada 0,100 de IVS, na faixa inteira e nos "
        "últimos 0,050 antes do corte de cima.\n\n" + _bloco("original", tabela_original(est)))
    secoes = [
        ("G-a", "3. G-a — região",
         "Efeito fixo de macrorregião e, depois, de UF: a inclinação passa a comparar só células da mesma região. Depois "
         "da tabela: onde estão as células de cada faixa e quanto preenchem (sem controles)."),
        ("G-b", "4. G-b — candidatos por perto",
         "Para cada célula: candidatos do mesmo curso e ciclo cuja origem (município principal de vínculo no CNES na "
         "competência de referência do G1, regra principal) está na mesma UF ou na mesma região de saúde da célula, "
         "divididos pelas vagas oferecidas do mesmo curso e ciclo nesse mercado. Candidato sem origem conhecida não "
         "entra; o conjunto de candidatos se forma depois do anúncio da faixa."),
        ("G-c", "5. G-c — composição das vagas",
         "Efeito fixo de curso × ciclo; indicador de célula só de cadastro reserva; tipo do estabelecimento (cardápio "
         "de gestores do ciclo 3; fora dele fica ausente) e gestão (quadro da 1ª chamada)."),
        ("G-d", "6. G-d — porte e hierarquia urbana",
         "Log da população do Censo 2022 e nível REGIC 2018 (1 metrópole … 5 centro local) como efeito fixo."),
        ("G-e", "7. G-e — concorrência",
         "Número de outras células do mesmo curso e ciclo na mesma região de saúde (exposição do script 32, protocolo "
         "58). Célula de município sem região de saúde fica de fora (contada)."),
    ]
    for expl, tit, txt in secoes:
        k = expl[2]
        corpo = (txt + "\n\n" + _bloco(f"{k}_tabela", tabela_fator(est, expl)) + "\n\n"
                 + _bloco(f"{k}_leitura", frase_fator(est, expl)))
        if expl == "G-a":
            corpo += "\n\n" + _bloco("a_regiao", tabela_regiao(est))
        corpo += ("\n\nO próprio fator anda junto com o IVS dentro da faixa? Mesmo modelo, com o fator no lugar do "
                  "preenchimento (descritivo, fora do BKY):\n\n" + _bloco(f"{k}_balanco", tabela_balanco(est, expl)))
        partes.append(f"## {tit}\n\n" + corpo)
    partes.append("## 8. G-f — outras políticas que variam com o IVS (só relato)\n\n"
                  + _bloco("f_relato", secao_gf(resumo)))
    partes.append(
        "## 9. Quanto da subida cada fator leva\n\n"
        "Cada célula da tabela é 1 − (inclinação depois do fator ÷ inclinação original na mesma amostra). Em negrito, "
        "50% ou mais: o fator reduz a subida pela metade ou mais. \"—\" = não há subida a explicar (inclinação "
        "original ≤ 0). Acima de 100%: a inclinação troca de sinal. Negativo: a subida aumenta com o fator.\n\n"
        + _bloco("tabela_quanto", tabela_quanto(est)))
    partes.append(
        "## 10. Leitura pré-registrada (§3)\n\n"
        "Regra: um fator que reduz a inclinação pela metade ou mais descreve a subida (associação); se nenhum reduz, a "
        "subida não se explica com os dados disponíveis. Aplicada a cada faixa e trecho com subida (inclinação "
        "original > 0). Em qualquer caso é descritivo: diz com o que a subida anda junto, não por quê.\n\n"
        + _bloco("leitura", tabela_leitura(est, resumo)))
    figtxt = [f"![{Path(f['arquivo']).name}](../../{f['arquivo']})\n\n**Como ler:** {f['como_ler']}\n\n"
              f"*Detalhe técnico:* {f['detalhe_tecnico']}" for f in figs]
    partes.append("## 11. Figuras\n\n" + _bloco("figuras", "\n\n".join(figtxt)))
    partes.append("## 12. Limites\n\n" + _bloco("limites", "\n".join(LIMITES)))
    gb = info["G-b"]
    v = resumo["validacoes"]
    tab_v = _tab(["Conferência", "Resultado"], [
        ["células (ciclos 1–3)", str(sum(info["celulas_por_ciclo"].values()))],
        ["células por faixa", ", ".join(f"{ROT_FX[k]}: {n}" for k, n in info["celulas_por_faixa"].items())],
        ["faixa pelo IVS oficial = faixa anunciada", "sim (o script para se não for)"],
        ["macrorregião pelo código IBGE = região do quadro", "sim (o script para se não for)"],
        ["linhas em GF_estimativas.csv", str(v["linhas"])],
        ["inclinações EXECUTADO / SEM_ESTIMATIVA / NAO_SE_APLICA",
         f"{v['executado']} / {v['sem_estimativa']} / {v['nao_se_aplica']}"],
        ["células sem tipo do estabelecimento", str(info["ausentes"]["tipo_estab"])],
        ["células sem região de saúde (G-b na região, G-e)", str(info["ausentes"]["cand_cir_por_vaga"])],
        ["candidatos sem origem no G1, por ciclo", ", ".join(f"ciclo {k}: {n} de {gb['candidatos_por_ciclo'][k]}"
                                                            for k, n in gb["candidatos_sem_origem_por_ciclo"].items())],
    ])
    partes.append("## 13. Decisões e validações\n\n"
                  + _bloco("decisoes", "\n".join(f"- {x}" for x in resumo["decisoes"])) + "\n\n"
                  + _bloco("validacoes", tab_v + "\n\nNada imputado ou simulado; IVS 2010 oficial (a08); o arquivo "
                           "local de IVS da auditoria 16 não é lido; `data/` é só lido; nenhum identificador de pessoa "
                           "em `output/`."))
    return "\n\n".join(partes) + "\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def ler_saidas() -> tuple[pd.DataFrame, dict]:
    est = pd.read_csv(OUT / NOME_EST, dtype={"faixa": str, "janela": str, "explicacao": str, "variante": str})
    for c in ("principal_da_explicacao", "descricao", "efeitos_fixos", "covariaveis", "estimador", "motivo_fora",
              "reduz_metade", "unidade", "nota"):
        est[c] = est[c].fillna("")
    resumo = json.loads((OUT / NOME_RESUMO).read_text(encoding="utf-8"))
    return est, resumo


def atualizar_doc() -> None:
    est, resumo = ler_saidas()
    DOC.write_text(gerar_doc(est, resumo), encoding="utf-8")


def entradas() -> list[dict]:
    b = E6.bloco_entrada
    return [
        b(PROTOCOLO_MD, "protocolo 62 (congelado antes de rodar)", "docs/06_execucao", "2026-10-26", "-", "texto", "-",
          "-"),
        b(FIGURA_ORIGEM, "figura de dados crus que motivou o protocolo (so citada)", "deck banca 2", "2026-10-26", "-",
          "imagem", "-", "nao lida pelo script"),
        b(Path(DQ.__file__), "script 38 (carregar() importado, nao alterado)", "scripts/rdd_bolsa", "2026-10-26", "-",
          "codigo", "-", "-"),
        b(T23.A08, "running variable (IVS 2010 oficial)", "Ipea (a08)", "Censo 2010", "Brasil", "municipio", "co_ibge",
          "ivs"),
        b(T23.ARQ_VC, "celulas do quadro da 1a chamada (A3) e vagas do G-b", "tarefa B (12)", "ciclos 1-3",
          "5135 celulas", "celula x ciclo", "ciclo, co_cnes_7d, cod_curso", "celulas sem IVS fora da analise"),
        b(T23.ARQ_VM, "municipios do quadro (conferencias do 24 e do 38)", "tarefa B (12)", "ciclos 1-3",
          "municipios do quadro", "municipio x ciclo", "ciclo, co_ibge", "-"),
        b(T23.ARQ_U, "U (todos os municipios), via 24", "tarefa B (12)", "-", "Brasil", "municipio", "co_ibge", "-"),
        b(T24.ARQ_POP, "populacao 2022 (G-d)", "IBGE (a06)", "Censo 2022", "Brasil", "municipio", "co_ibge_6d", "-"),
        b(ESCOLHAS, "escolhas dos candidatos: cursos de cada candidato (G-b)", "tarefa B (12)", "ciclos 1-3", "-",
          "candidato x opcao", "ciclo, id_candidato", "so agregado, em memoria"),
        b(G1_ORIGEM, "municipio de origem dos candidatos (G-b)", "portao G1", "competencia de referencia do ciclo", "-",
          "candidato", "ciclo, id_candidato", "regra g1_cpf_nome; so agregado"),
        b(DQ.QUADRO_CONSOLIDADO, "gestao do estabelecimento (G-c), via 38", "aquisicao (02)", "quadros 1a chamada", "-",
          "linha do quadro", "ciclo, co_cnes_7d", "OFERTA_VAGAS, chamada 1"),
        b(T29.CARDAPIO, "tipo do estabelecimento (G-c), via 38 e 29", "MS", "ciclo 3", "-", "planilha", "CNES", "-"),
        b(DQ.ARQ_CNES, "CNES pre lido pelo carregar() do 38 (nao usado nos fatores do 62)", "a09", "202406-202506",
          "Brasil", "municipio x grupo x mes", "co_ibge, competencia, grupo", "so 202406-202506"),
        b(T32.V_CELULA, "concorrencia (G-e), via script 32", "tarefa B (12)", "ciclos 1-3", "-", "celula",
          "ciclo, co_cnes_7d, cod_curso", "celulas com IVS e CIR"),
        b(T29.CIR_CNV, "regiao de saude (G-b, G-e)", "DATASUS/TabNet", "base corrente", "Brasil", "municipio",
          "co_ibge", "-"),
        b(T29.REGIC_XLSX, "hierarquia urbana (G-d)", "IBGE", "2018", "Brasil", "municipio", "codmun", "-"),
        b(AUDITORIA_18, "regras de IVS (G-f)", "auditoria 18", "2026-10-18", "-", "texto", "-", "-"),
    ]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--atualizar-doc", action="store_true", help="so regrava o doc 57m a partir das saidas")
    args = ap.parse_args(argv)
    if args.atualizar_doc:
        atualizar_doc()
        return 0
    est, extras = estimar_tudo()
    incl = est[(est["tipo_linha"] == "inclinacao") & (est["status"] == "EXECUTADO")]
    if incl.empty or incl[["inclinacao", "ep", "p_valor"]].isna().any().any():
        raise FalhaValidacao("inclinacao executada sem estimativa")
    if {"id_candidato", "cpf", "nome", "co_profissional_sus"} & set(c.lower() for c in est.columns):
        raise FalhaValidacao("coluna de identificador pessoal na saida")
    OUT.mkdir(parents=True, exist_ok=True)
    est.to_csv(OUT / NOME_EST, index=False)
    est_lido =pd.read_csv(OUT / NOME_EST, dtype={"faixa": str, "janela": str, "explicacao": str, "variante": str})
    est_lido["reduz_metade"] = est_lido["reduz_metade"].fillna("")
    figs = gerar_figuras(est_lido, OUT / DIR_FIG)
    v_incl = est[est["tipo_linha"] == "inclinacao"]
    gf = dict(extras["G-f"])
    gf["situacao_doc"] = ("arquivada em " + ", ".join(f"`{a['caminho']}`" for a in gf["arquivos"]) + "."
                          if gf["arquivos"] else
                          f"em andamento em paralelo; quando existir, fica em `docs/auditorias/{PADRAO_AUDITORIA_GF}` "
                          "(não existia nesta execução).")
    resumo = {
        "etapa": "GF_gradiente_dentro_das_faixas",
        "natureza_dos_dados": NATUREZA,
        "estatuto": ESTATUTO,
        "data_execucao": DATA_EXECUCAO,
        "script": rotulo(Path(__file__)),
        "protocolo": {"texto": rotulo(PROTOCOLO_MD), "sha256": sha256(PROTOCOLO_MD)},
        "contraste": "nenhum contraste causal: dentro de cada faixa a bolsa e constante; a inclinacao compara celulas "
                     "com a mesma bolsa e IVS diferente (descritivo)",
        "quantidade": "inclinacao da probabilidade de a celula aberta ser preenchida na 1a chamada por 0,100 de IVS, "
                      "por faixa da bolsa, na faixa inteira e na janela de 0,050 junto ao corte superior",
        "faixas": FAIXAS,
        "explicacoes": EXPLICACOES,
        "variantes": [{"explicacao": e, "variante": v, "efeitos_fixos": list(fe), "covariaveis": list(z),
                       "principal": p, "descricao": dsc} for e, v, fe, z, p, dsc in VARIANTES],
        "parametros": {"unidade_x_mil": UNIDADE_X_MIL, "janela_mil": JANELA_MIL, "bin_mil": BIN_MIL,
                       "limiar_metade": LIMIAR_METADE, "regra_ligacao_g1": REGRA_LIGACAO},
        "leitura": extras["leitura"],
        "G-f": gf,
        "regras_gf_auditoria_18": REGRAS_GF,
        "info_dados": extras["info_dados"],
        "decisoes": DECISOES,
        "entradas": entradas(),
        "validacoes": {"linhas": int(len(est)),
                       "executado": int((v_incl["status"] == "EXECUTADO").sum()),
                       "sem_estimativa": int((v_incl["status"] == "SEM_ESTIMATIVA").sum()),
                       "nao_se_aplica": int((v_incl["status"] == "NAO_SE_APLICA").sum())},
        "saidas": {NOME_EST: {"arquivo": rotulo(OUT / NOME_EST), "sha256": sha256(OUT / NOME_EST)},
                   "figuras": [dict(f, sha256=sha256(ROOT / f["arquivo"])) for f in figs]},
        "linguagem": "descritivo e pos-resultado: diz com o que a subida anda junto, nao por que",
    }
    T23._gravar_json(OUT / NOME_RESUMO, DQ._chaves_tuplas(resumo))
    atualizar_doc()
    print(f"GF: {len(est)} linhas; leitura {json.dumps({k: v['leitura'] for k, v in extras['leitura'].items()})}; "
          f"doc {rotulo(DOC)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except FalhaValidacao as erro:
        print(f"FALHA DE VALIDACAO: {erro}", file=sys.stderr)
        sys.exit(2)
