"""P5 (protocolo 55): determinantes descritivos da abertura de vagas do PMM-E (T5.1–T5.3).

Protocolo: `docs/06_execucao/55_protocolo_P5_abertura_vagas.md`, congelado em 19/10/2026 antes de estimar.
Toda linha sai com `natureza_dos_dados = EMPIRICO` e `estatuto = PROTOCOLO_55_DESCRITIVO`.

Etapas (§1)
-----------
- E1, pedido do gestor (ciclo 3): unidade = célula do cardápio de gestores (CNES × curso); outcome = a célula
  tem linha no resultado final da adesão. Estimada só entre os municípios que constam do resultado: o município
  ausente do resultado fica com as variáveis de pedido AUSENTES, nunca zero (doc 41a, §5). A presença do
  município no resultado é uma linha à parte, no nível do município.
- E2, priorização da SGTES (ciclo 3): unidade = célula pedida (célula do cardápio com linha na adesão); outcome
  = célula priorizada. A priorização é tudo ou nada por linha (conferido: nenhuma linha tem priorizadas e não
  priorizadas ao mesmo tempo).
- E3, quadro publicado (ciclos 1 e 2): unidade = município; outcomes = nº de células e de vagas (imediatas +
  cadastro reserva) no quadro da 1ª chamada; município fora do quadro vale zero (zero observado no arquivo
  completo, doc 41a §5).

Especificações (§3)
-------------------
- T5.1a: logit de E1 nas covariáveis (§2), efeito fixo de curso, EP com cluster por município (CR1).
- T5.1b: logit de E2 nas covariáveis, entre células pedidas, efeito fixo de curso, cluster por município.
- T5.1c: efeitos marginais médios (método delta com a variância por cluster) e contribuição de cada bloco
  (pseudo-R² de McFadden do modelo completo menos o do modelo sem o bloco, na mesma amostra).
- T5.2a: RDD sharp nos cortes 0,300 e 0,400 (h = 0,050, kernel triangular, local linear; cortes separados e
  empilhados) da fração de células pedidas e da priorizada, por célula (cluster por município, efeito fixo de
  curso) e por município. Mede o pacote do corte, não a bolsa sozinha.
- T5.2b: T5.2a com as covariáveis pré-determinadas (Calonico, Cattaneo, Farrell e Titiunik, 2019). BKY entre as
  linhas do T5.2 (§4).
- T5.3: Poisson do nº de células e de vagas no quadro dos ciclos 1 e 2 nas mesmas covariáveis municipais, com o
  IVS contínuo; EP robusto (HC1 = CR1 com um município por cluster).

T5.1 e T5.3 são descritivos: "associado a", nunca "o Ministério escolhe por causa de". O critério oficial de
priorização não é publicado (auditoria 01; doc 51, §1). Sem teste múltiplo nas linhas descritivas.

Integridade
-----------
Nada imputado; ausente não vira zero (a linha sai da amostra e é contada por motivo); o arquivo local de IVS da
auditoria 16 não é lido (a running variable e a covariável IVS vêm do a08); o CNES é lido só de 202406 a 202506
(nenhuma competência ≥ 202609); o SIA é lido só de 202406 a 202506 (filtro na leitura). Os arquivos de `data/`
são só lidos.

Uso
---
    python3 scripts/rdd_bolsa/29_determinantes_abertura.py
    python3 scripts/rdd_bolsa/29_determinantes_abertura.py --atualizar-doc
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import special, stats

ROOT = Path(__file__).resolve().parents[2]
DIR_RDD = ROOT / "scripts" / "rdd_bolsa"


def _importar(caminho: Path, nome: str):
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    return mod


_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
T24 = _importar(DIR_RDD / "24_abertura_vagas_selecao.py", "abertura_vagas_para_p5")
M12 = _importar(DIR_RDD / "12_construir_outcomes_funil.py", "outcomes_funil_para_p5")
sys.dont_write_bytecode = _bytecode
T23, L, E6 = T24.T23, T24.L, T24.E6

# ---------------------------------------------------------------------------
# Caminhos e parâmetros do protocolo (constantes permitidas: cortes, h, janela pré, rótulos)
# ---------------------------------------------------------------------------

OUT = ROOT / "output" / "rdd_bolsa"
OUTC = OUT / "outcomes"
NOME_EST = "P5_estimativas.csv"
NOME_RESUMO = "P5_resumo.json"
DIR_FIG = "P5_figuras"
PROTOCOLO_MD = ROOT / "docs" / "06_execucao" / "55_protocolo_P5_abertura_vagas.md"
DOC = ROOT / "docs" / "06_execucao" / "57e_resultados_P5_abertura.md"

A08 = ROOT / "output" / "aquisicao" / "a08_ivs_2010_oficial_municipio.csv"
ARQ_POP = ROOT / "output" / "aquisicao" / "populacao_censo2022_municipios.csv"
ARQ_CNES = ROOT / "output" / "aquisicao" / "cnes_nacional" / "painel_municipio_cbo_mes.parquet"
AQ_SIA = ROOT / "output" / "aquisicao" / "sia"
ARQ_SIA = AQ_SIA / "painel_sia_municipio_mes_subgrupo_cbo.parquet"
SIA_SUBG = AQ_SIA / "sia_subgrupos_por_consulta.csv"
SIA_MUN = AQ_SIA / "sia_municipios_tabnet.csv"
MANIF_SIA = AQ_SIA / "manifesto_sia.json"
PONTE = ROOT / "output" / "aquisicao" / "ponte_curso_cbo_oficial.json"
TERRITORIO = ROOT / "data" / "raw" / "aquisicao" / "territorio"
REGIC_XLSX = TERRITORIO / "REGIC2018_Municipios_Hierarquia_e_regiao.xlsx"
CIR_CNV = TERRITORIO / "datasus_tabnet_br_regsaud.cnv"
TIPOLOGIA = ROOT / "output" / "tema_trabalho" / "matriz_tipologia_territorial.parquet"
ARQ_U = OUTC / "outcomes_U_municipio.parquet"
ARQ_G3 = OUTC / "outcomes_G3_municipio.parquet"
CARDAPIO = M12.CARDAPIO_C3
ADESAO = M12.ADESAO_C3

DATA_EXECUCAO = "2026-10-19"
ESTATUTO = "PROTOCOLO_55_DESCRITIVO"
NATUREZA = "EMPIRICO"
COMP_PRE = ("202406", "202506")         # §2: janela pré do CNES e do SIA
LIMITE_CNES = "202609"                   # nenhuma competência CNES >= 202609
H = L.H_PRINCIPAL_MIL                    # 50 = 0,050 (§3, T5.2a)
CORTES = L.CORTES_MIL                    # (300, 400)
EMPILHADO = "empilhado"
POR_HAB = 1e4
CICLOS_QUADRO = (1, 2)                   # T5.3
STATUS_SIA_OK = ("valor_tabnet", "zero_tabnet")
CONJUNTOS_SIA = {"alvo_pmme": "sia_alvo", "todos_profissionais": "sia_todos"}
GRUPOS_CNES_MUN = {"alvo_pmme": "vinc_alvo", "todos_medicos": "vinc_medicos"}
ROTULO_FORA = ("SENSIBILIDADE_FORA_DO_PROTOCOLO (nao pedida pelo protocolo 55; relatada para leitura)")
ROTULO_LEITURA = ("LEITURA_ALTERNATIVA (fracao priorizada sobre o cardapio, e nao sobre as celulas pedidas; fora "
                  "do BKY)")
ROTULO_COMPLEMENTAR = "COMPLEMENTAR (contribuicao por bloco no T5.3 nao pedida pelo protocolo; descritivo)"
CONTRASTE = E6.CONTRASTE
Z = float(stats.norm.ppf(0.975))

MOTIVO_CURSO_FORA_DA_PONTE = ("curso sem CBO na ponte curso-CBO do a09 (output/aquisicao/ponte_curso_cbo_oficial.json "
                              "cobre os cursos 1 a 16): vinculos do curso ausentes, nada imputado")


class FalhaValidacao(RuntimeError):
    """Conferência de integridade que falhou: o script para sem gravar."""


sha256, rotulo = T23.sha256, T23.rotulo

# ---------------------------------------------------------------------------
# Covariáveis (§2): especificação fixada antes de ler outcomes
# ---------------------------------------------------------------------------

BLOCOS = ["estabelecimento", "municipio", "capacidade_pre", "producao_pre", "escassez_regional", "ivs"]
ROTULO_BLOCO = {
    "estabelecimento": "estabelecimento (tipo, gestão, natureza jurídica)",
    "municipio": "município (população, REGIC, capital, macrorregião, polo)",
    "capacidade_pre": "capacidade pré no CNES (vínculos por 10 mil hab.)",
    "producao_pre": "produção pré no SIA (por 10 mil hab.)",
    "escassez_regional": "escassez regional (vínculos por 10 mil hab. na região de saúde)",
    "ivs": "IVS 2010 oficial",
    "efeito_fixo": "efeito fixo de curso",
}


def _c(col, bloco, tipo, desc, ref=None):
    return {"col": col, "bloco": bloco, "tipo": tipo, "desc": desc, "ref": ref}


COV_ESTAB = [
    _c("tipo", "estabelecimento", "categorica", "tipo do estabelecimento", "05 HOSPITAL GERAL"),
    _c("gestao", "estabelecimento", "categorica", "gestão", "MUNICIPAL"),
    _c("natureza", "estabelecimento", "categorica", "natureza jurídica", "PUBLICO"),
]
COV_MUN = [
    _c("log_pop22", "municipio", "continua", "log da população do Censo 2022"),
    _c("regic", "municipio", "categorica", "hierarquia urbana (REGIC 2018)", "5 CENTRO LOCAL"),
    _c("capital", "municipio", "binaria", "capital de UF"),
    _c("macro", "municipio", "categorica", "macrorregião", "SUDESTE"),
    _c("polo", "municipio", "binaria", "polo da região de saúde (maior população da região)"),
]
COV_CAP_CELULA = [
    _c("vinc_curso_10k", "capacidade_pre", "continua", "vínculos CNES pré das CBO do curso por 10 mil hab."),
    _c("vinc_medicos_10k", "capacidade_pre", "continua", "vínculos CNES pré de todos os médicos por 10 mil hab."),
]
COV_CAP_MUN = [
    _c("vinc_alvo_10k", "capacidade_pre", "continua",
       "vínculos CNES pré das CBO dos cursos (conjunto alvo) por 10 mil hab."),
    _c("vinc_medicos_10k", "capacidade_pre", "continua", "vínculos CNES pré de todos os médicos por 10 mil hab."),
]
COV_PROD = [
    _c("sia_alvo_10k", "producao_pre", "continua", "produção SIA pré das CBO-alvo por 10 mil hab. (média mensal)"),
    _c("sia_todos_10k", "producao_pre", "continua",
       "produção SIA pré de todos os profissionais por 10 mil hab. (média mensal)"),
]
COV_ESC_CELULA = [_c("vinc_curso_regiao_10k", "escassez_regional", "continua",
                     "vínculos das CBO do curso por 10 mil hab. na região de saúde")]
COV_ESC_MUN = [_c("vinc_alvo_regiao_10k", "escassez_regional", "continua",
                  "vínculos das CBO dos cursos (conjunto alvo) por 10 mil hab. na região de saúde")]
COV_IVS = [_c("ivs", "ivs", "continua", "IVS 2010 oficial (contínuo)")]

COVS_CELULA = COV_ESTAB + COV_MUN + COV_CAP_CELULA + COV_PROD + COV_ESC_CELULA + COV_IVS
COVS_CELULA_SENS = COV_ESTAB + COV_MUN + COV_CAP_MUN + COV_PROD + COV_ESC_MUN + COV_IVS
COVS_MUN = COV_MUN + COV_CAP_MUN + COV_PROD + COV_ESC_MUN + COV_IVS
# T5.2b (CCFT): as mesmas covariáveis pré-determinadas, sem o IVS (é a running variable).
COVS_CCFT_CELULA = [c for c in COVS_CELULA if c["bloco"] != "ivs"]
COVS_CCFT_MUN = [c for c in COVS_MUN if c["bloco"] != "ivs"]

COLUNAS = [
    "natureza_dos_dados", "estatuto", "especificacao", "etapa", "ciclo", "unidade_analise", "populacao", "outcome",
    "descricao_outcome", "variante", "termo", "descricao_termo", "bloco", "tipo_termo", "estimador", "corte", "h",
    "no_protocolo", "rotulo", "status", "n_obs", "n_clusters", "n_eventos", "n_abaixo", "n_acima",
    "n_descartadas", "coef", "ep_coef", "estimativa", "ep", "ic95_inf", "ic95_sup", "p_valor", "entra_bky", "q_bky",
    "dp_termo", "estimativa_por_dp", "ic95_inf_por_dp", "ic95_sup_por_dp", "pseudo_r2", "pseudo_r2_sem_bloco",
    "contribuicao_bloco", "media_outcome", "unidade_estimativa", "covariaveis", "efeitos_fixos", "nota",
]
UN_PROB = "probabilidade (x100 = p.p.)"
UN_LOGIT = "log da razao de chances (coeficiente do logit)"
UN_RT = "razao de taxas (exp do coeficiente do Poisson)"
UN_FRAC = "fracao (x100 = p.p.)"
UN_R2 = "pseudo-R2"


def nova_linha(**kw) -> dict:
    linha = {c: np.nan for c in COLUNAS}
    linha.update({"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "no_protocolo": True, "rotulo": "",
                  "status": "EXECUTADO", "entra_bky": False, "nota": "", "covariaveis": "", "efeitos_fixos": ""})
    for k, v in kw.items():
        if k not in COLUNAS:
            raise KeyError(k)
        linha[k] = v
    return linha


def _juntar(*notas) -> str:
    return "; ".join(str(n) for n in notas if n)


# ---------------------------------------------------------------------------
# Leitura (só output/ e os brutos territoriais de data/, sem gravar em data/)
# ---------------------------------------------------------------------------

def ler_ivs() -> pd.DataFrame:
    """IVS 2010 oficial (a08): running variable em milésimos e covariável contínua."""
    rv = E6.ler_running_variable()
    rv["ivs"] = rv["s_mil"].astype(float) / 1000.0
    return rv[["co_ibge", "s_mil", "ivs"]]


def ler_populacao() -> pd.Series:
    p = pd.read_csv(ARQ_POP, dtype={"co_ibge_6d": str})
    p["co_ibge"] = p["co_ibge_6d"].str.zfill(6)
    if p["co_ibge"].duplicated().any() or p["populacao_2022"].isna().any():
        raise FalhaValidacao("Censo 2022 com municipio duplicado ou populacao ausente")
    return p.set_index("co_ibge")["populacao_2022"].astype(float)


def ler_regic() -> tuple[pd.Series, dict]:
    """Nível da hierarquia urbana do REGIC 2018 (1 Metrópole ... 5 Centro Local), do bruto do IBGE."""
    import openpyxl
    wb = openpyxl.load_workbook(REGIC_XLSX, read_only=True, data_only=True)
    try:
        linhas = list(wb["Hierarquia e região"].iter_rows(values_only=True))
    finally:
        wb.close()
    cab = [str(c) if c is not None else "" for c in linhas[0]]
    i_cod, i_grupo = cab.index("codmun"), cab.index("Hierarquia - grupo")
    reg = []
    for r in linhas[1:]:
        if r[i_cod] is None:
            continue
        cod = re.sub(r"\D", "", str(r[i_cod])).zfill(7)[:6]
        m = re.match(r"\s*(\d)\s*-\s*(.+?)(?:\s*-\s*Integrante.*)?$", str(r[i_grupo] or ""))
        if not m:
            raise FalhaValidacao(f"REGIC: hierarquia fora do formato em {cod}: {r[i_grupo]!r}")
        reg.append((cod, f"{m.group(1)} {M12.texto_norm(m.group(2))}"))
    s = pd.DataFrame(reg, columns=["co_ibge", "regic"])
    if s["co_ibge"].duplicated().any():
        raise FalhaValidacao("REGIC com municipio duplicado")
    info = {"municipios": int(len(s)), "niveis": s["regic"].value_counts().sort_index().to_dict(),
            "regra": "nivel = 1o digito de 'Hierarquia - grupo' (1 Metropole ... 5 Centro Local); a marca "
                     "'Integrante de Arranjo Populacional' nao entra"}
    return s.set_index("co_ibge")["regic"], info


def ler_capital() -> pd.Series:
    t = pd.read_parquet(TIPOLOGIA, columns=["co_ibge_6d", "flag_capital"])
    t["co_ibge"] = t["co_ibge_6d"].astype(str).str.zfill(6)
    if t["co_ibge"].duplicated().any():
        raise FalhaValidacao("tipologia com municipio duplicado")
    return t.set_index("co_ibge")["flag_capital"].astype(float)


def ler_cir() -> tuple[pd.DataFrame, dict]:
    """Município (6 dígitos) → região de saúde (CIR) da tabela do TabNet; linhas 'Ignorado' (faixas) não entram."""
    linhas = CIR_CNV.read_bytes().decode("latin1").splitlines()
    padrao = re.compile(r"^\s*(\d+)\s+(\d{5})\s+(.*?)\s+(\d{6})\s*$")
    reg, ignorado, outras = [], 0, []
    for ln in linhas[1:]:
        m = padrao.match(ln)
        if m:
            reg.append((m.group(4), m.group(2)))
        elif "Ignorado" in ln:
            ignorado += 1
        elif ln.strip():
            outras.append(ln)
    if outras:
        raise FalhaValidacao(f"linhas da CIR fora do formato esperado: {outras[:3]}")
    cir = pd.DataFrame(reg, columns=["co_ibge", "co_cir"])
    if not cir["co_ibge"].is_unique:
        raise FalhaValidacao("municipio com mais de uma CIR na tabela do TabNet")
    return cir, {"codigos": int(len(cir)), "regioes": int(cir["co_cir"].nunique()), "linhas_ignorado": ignorado}


def ler_ponte() -> dict[int, list[str]]:
    raw = json.loads(PONTE.read_text(encoding="utf-8"))
    return {int(c["cod_curso"]): sorted(str(x).zfill(6) for x in c["cbos_elegiveis"]) for c in raw["catalogo_cursos"]}


def ler_cnes_pre(cbos: list[str]) -> tuple[pd.DataFrame, dict]:
    """Média mensal de vínculos (n_vinculos, a09) de 202406 a 202506 por município e grupo de CBO.

    Filtro na leitura: só a janela pré. Município sem as 13 competências fica ausente no grupo, nunca zero. O zero
    do painel é o do a09 (competência lida e nenhum vínculo do grupo no município).
    """
    import pyarrow.parquet as pq
    grupos = list(GRUPOS_CNES_MUN) + [f"cbo_{c}" for c in cbos]
    t = pq.read_table(ARQ_CNES, columns=["co_ibge", "competencia", "grupo", "n_vinculos", "natureza_dos_dados"],
                      filters=[("competencia", ">=", COMP_PRE[0]), ("competencia", "<=", COMP_PRE[1]),
                               ("grupo", "in", grupos)]).to_pandas()
    comps = sorted(t["competencia"].astype(str).unique().tolist())
    if not comps or comps[0] < COMP_PRE[0] or comps[-1] > COMP_PRE[1] or comps[-1] >= LIMITE_CNES:
        raise FalhaValidacao(f"CNES fora da janela pre: {comps[:1]}..{comps[-1:]}")
    if set(t["natureza_dos_dados"].astype(str)) != {NATUREZA}:
        raise FalhaValidacao("CNES com natureza diferente de EMPIRICO")
    faltam = sorted(set(grupos) - set(t["grupo"].astype(str)))
    if faltam:
        raise FalhaValidacao(f"grupos de CBO ausentes do painel CNES: {faltam}")
    n_comp = len(comps)
    g = t.groupby(["co_ibge", "grupo"])["n_vinculos"].agg(["mean", "count"]).reset_index()
    g.loc[g["count"] != n_comp, "mean"] = np.nan
    larga = g.pivot(index="co_ibge", columns="grupo", values="mean")
    larga.index = larga.index.astype(str).str.zfill(6)
    info = {"competencias": comps, "n_competencias": n_comp, "municipios": int(len(larga)), "grupos": grupos,
            "medida": "media mensal de n_vinculos (a09) no municipio x grupo de CBO, 202406-202506",
            "municipio_grupo_sem_competencias_completas": int(larga.isna().sum().sum())}
    return larga, info


def ler_sia_pre() -> tuple[pd.DataFrame, dict]:
    """Média mensal da quantidade aprovada (SIA, a12) de 202406 a 202506 por município, conjuntos alvo e todos.

    Lido só no pré (filtro na leitura). Município-mês com subgrupo ausente da resposta, ou sem linha, fica ausente
    e o município fica sem média (nunca zero). Município fora da lista do TabNet fica ausente.
    """
    import pyarrow.parquet as pq
    man = json.loads(MANIF_SIA.read_text(encoding="utf-8"))
    if man["saidas"][rotulo(ARQ_SIA)]["sha256"] != sha256(ARQ_SIA):
        raise FalhaValidacao("painel SIA com SHA-256 diferente do manifesto do a12")
    meses = [f"{a}{m:02d}" for a in (2024, 2025) for m in range(1, 13)]
    meses = [x for x in meses if COMP_PRE[0] <= x <= COMP_PRE[1]]
    sub = pd.read_csv(SIA_SUBG, dtype=str)
    sub = sub[sub["conjunto_cbo"].isin(CONJUNTOS_SIA) & sub["competencia_processamento"].isin(meses)]
    pres = (sub[sub["presente_na_resposta"].str.lower() == "true"]
            .groupby(["conjunto_cbo", "competencia_processamento"]).size().rename("n_presentes"))
    t = pq.read_table(ARQ_SIA, columns=["co_ibge", "competencia_processamento", "conjunto_cbo", "qtd_aprovada",
                                        "status", "natureza_dos_dados"],
                      filters=[("competencia_processamento", "in", meses),
                               ("conjunto_cbo", "in", list(CONJUNTOS_SIA))]).to_pandas()
    for c in ("co_ibge", "competencia_processamento", "conjunto_cbo", "status", "natureza_dos_dados"):
        t[c] = t[c].astype(str)
    if set(t["natureza_dos_dados"]) != {NATUREZA}:
        raise FalhaValidacao("SIA com natureza diferente de EMPIRICO")
    comps = sorted(t["competencia_processamento"].unique().tolist())
    if comps != meses:
        raise FalhaValidacao(f"SIA lido fora da janela pre ou incompleto: {comps}")
    t["ok"] = t["status"].isin(STATUS_SIA_OK) & t["qtd_aprovada"].notna()
    g = t.groupby(["conjunto_cbo", "competencia_processamento", "co_ibge"]).agg(
        q=("qtd_aprovada", "sum"), n=("qtd_aprovada", "size"), ok=("ok", "all")).reset_index()
    g = g.merge(pres.reset_index(), on=["conjunto_cbo", "competencia_processamento"], how="left")
    if g["n_presentes"].isna().any() or (g["n"] != g["n_presentes"]).any():
        raise FalhaValidacao("SIA: municipio com numero de linhas diferente dos subgrupos presentes na consulta")
    g.loc[~g["ok"], "q"] = np.nan
    munis = pd.read_csv(SIA_MUN, dtype={"co_ibge": str})["co_ibge"].str.zfill(6)
    saida = {}
    for conj, nome in CONJUNTOS_SIA.items():
        larga = g[g["conjunto_cbo"] == conj].pivot(index="co_ibge", columns="competencia_processamento", values="q")
        larga.index = larga.index.astype(str).str.zfill(6)
        larga = larga.reindex(index=munis, columns=meses)
        saida[nome] = larga.mean(axis=1, skipna=False)
    df = pd.DataFrame(saida)
    info = {"competencias": meses, "n_competencias": len(meses), "municipios_tabnet": int(len(munis)),
            "municipios_sem_media": {k: int(v) for k, v in df.isna().sum().items()},
            "status_lidos": sorted(t["status"].unique().tolist()),
            "medida": "media mensal da soma de qtd_aprovada sobre os subgrupos (municipio de atendimento), 202406-202506",
            "conjuntos": CONJUNTOS_SIA}
    return df, info


def ler_cardapio_com_atributos() -> pd.DataFrame:
    """Cardápio de gestores do ciclo 3 com tipo, gestão e natureza jurídica (colunas pelo nome do cabeçalho).

    Chaves conferidas contra `ler_cardapio` do script 12 (mesma leitura do F0.3).
    """
    cab, _, linhas = M12.ler_aba(CARDAPIO)
    ic = {n: M12.coluna(cab, n) for n in ("CNES", "APRIMORAMENTO FINAL", "IBGE", "VAGAS", "TIPO DO ESTABELECIMENTO",
                                          "GESTAO", "NATUREZA JURIDICA CATEGORIA")}
    df = pd.DataFrame([{
        "co_cnes_7d": M12.chave_cnes(M12.valor(r, ic["CNES"])),
        "cod_curso": M12.chave_curso(M12.valor(r, ic["APRIMORAMENTO FINAL"])),
        "co_ibge": M12.chave_ibge(M12.valor(r, ic["IBGE"])),
        "vagas_cardapio": M12.numero(M12.valor(r, ic["VAGAS"])),
        "tipo": M12.texto_norm(M12.valor(r, ic["TIPO DO ESTABELECIMENTO"])),
        "gestao": M12.texto_norm(M12.valor(r, ic["GESTAO"])),
        "natureza": M12.texto_norm(M12.valor(r, ic["NATUREZA JURIDICA CATEGORIA"])),
    } for r in linhas])
    ref = M12.ler_cardapio()
    cmp_ = df[M12.CHAVE + ["co_ibge", "vagas_cardapio"]].sort_values(M12.CHAVE).reset_index(drop=True)
    ref = ref.sort_values(M12.CHAVE).reset_index(drop=True)
    if not cmp_.equals(ref[M12.CHAVE + ["co_ibge", "vagas_cardapio"]]):
        raise FalhaValidacao("cardapio com atributos difere da leitura do script 12")
    for c in ("tipo", "gestao", "natureza"):
        if (df[c] == "").any():
            raise FalhaValidacao(f"cardapio com {c} vazio")
    return df


# ---------------------------------------------------------------------------
# Montagem das bases
# ---------------------------------------------------------------------------

def montar_municipios(cnes: pd.DataFrame, ponte: dict[int, list[str]], sia: pd.DataFrame, pop: pd.Series,
                      regic: pd.Series, capital: pd.Series, cir: pd.DataFrame, rv: pd.DataFrame,
                      extras: list[str]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    """Covariáveis municipais, vínculos por curso (município) e por curso na região de saúde.

    Universo: municípios do a08 mais os do cardápio e do G3 (estes podem não ter IVS; as covariáveis que faltam
    ficam ausentes). Região: soma dos vínculos e da população só entre os municípios da CIR que estão no painel do
    CNES (os demais códigos da tabela do TabNet ficam fora do numerador e do denominador; contados).
    """
    universo = sorted(set(rv["co_ibge"]) | set(extras))
    m = pd.DataFrame(index=pd.Index(universo, name="co_ibge"))
    m["pop22"] = m.index.map(pop)
    m["log_pop22"] = np.log(m["pop22"])
    m["regic"] = m.index.map(regic)
    m["capital"] = m.index.map(capital)
    m["macro"] = [M12.REGIAO_POR_DIGITO_IBGE.get(c[0]) for c in m.index]
    m["s_mil"] = m.index.map(rv.set_index("co_ibge")["s_mil"])
    m["ivs"] = m.index.map(rv.set_index("co_ibge")["ivs"])
    for g, nome in GRUPOS_CNES_MUN.items():
        m[nome] = m.index.map(cnes[g])
        m[f"{nome}_10k"] = m[nome] / m["pop22"] * POR_HAB
    for c, nome in CONJUNTOS_SIA.items():
        m[nome] = m.index.map(sia[nome])
        m[f"{nome}_10k"] = m[nome] / m["pop22"] * POR_HAB
    # Vínculos por curso (soma das CBO do curso na ponte do a09), por município.
    vc = pd.DataFrame({k: cnes[[f"cbo_{c}" for c in cbos]].sum(axis=1, min_count=len(cbos))
                       for k, cbos in sorted(ponte.items())})
    vc = vc.reindex(universo)
    # Região de saúde: polo = maior população do Censo 2022 entre os municípios da CIR com população.
    c = cir.copy()
    c["pop22"] = c["co_ibge"].map(pop)
    c["no_cnes"] = c["co_ibge"].isin(cnes.index)
    com_pop = c[c["pop22"].notna()]
    maximo = com_pop.groupby("co_cir")["pop22"].transform("max")
    polo = (com_pop["pop22"] == maximo).astype(float)
    empates = com_pop[polo == 1].groupby("co_cir").size()
    m["co_cir"] = m.index.map(cir.set_index("co_ibge")["co_cir"])
    m["polo"] = m.index.map(pd.Series(polo.to_numpy(), index=com_pop["co_ibge"]))
    reg = c[c["no_cnes"] & c["pop22"].notna()].copy()
    vc_reg = vc.reindex(reg["co_ibge"]).set_index(reg.index)
    soma_pop = reg.groupby("co_cir")["pop22"].sum()
    rc = pd.DataFrame({k: vc_reg[k].groupby(reg["co_cir"]).sum(min_count=1) for k in vc.columns})
    # Uma ausência de vínculo num município da região deixa a região ausente (nunca soma parcial).
    nan_reg = vc_reg.isna().groupby(reg["co_cir"]).any()
    rc = rc.where(~nan_reg)
    rc = rc.div(soma_pop, axis=0) * POR_HAB
    va = reg["co_ibge"].map(cnes["alvo_pmme"])
    alvo_reg = (va.groupby(reg["co_cir"]).sum(min_count=1).where(~va.isna().groupby(reg["co_cir"]).any())
                / soma_pop * POR_HAB)
    m["vinc_alvo_regiao_10k"] = m["co_cir"].map(alvo_reg)
    rc_mun = rc.reindex(m["co_cir"]).set_index(m.index)
    vc_10k = vc.div(m["pop22"], axis=0) * POR_HAB
    info = {
        "universo_municipios": int(len(m)),
        "capitais_na_tipologia": int(capital.sum()),
        "municipios_sem_ivs_oficial": sorted(m.index[m["ivs"].isna()].tolist()),
        "municipios_sem_cir": sorted(m.index[m["co_cir"].isna()].tolist()),
        "municipios_sem_regic": sorted(m.index[m["regic"].isna()].tolist()),
        "municipios_sem_cnes_pre": int(m["vinc_medicos"].isna().sum()),
        "municipios_sem_sia_pre": {n: int(m[n].isna().sum()) for n in CONJUNTOS_SIA.values()},
        "codigos_cir_fora_do_painel_cnes": sorted(c.loc[~c["no_cnes"] & c["pop22"].notna(), "co_ibge"].tolist()),
        "codigos_cir_sem_populacao": int(c["pop22"].isna().sum()),
        "regioes_com_empate_no_polo": int((empates > 1).sum()),
        "regra_polo": "polo = 1 no municipio de maior populacao (Censo 2022) da regiao de saude (tabela do TabNet); "
                      "empate: todos os empatados valem 1",
        "regra_regiao": "vinculos e populacao somados so entre os municipios da CIR presentes no painel CNES do a09; "
                        "codigos da tabela do TabNet fora do painel (municipios criados depois de 2010 sem IVS e "
                        "regioes administrativas do DF) ficam fora do numerador e do denominador",
    }
    return m, vc_10k, rc_mun, info


def montar_celulas(card: pd.DataFrame, adesao: pd.DataFrame, mun: pd.DataFrame, vc_10k: pd.DataFrame,
                   rc_mun: pd.DataFrame, ponte: dict) -> tuple[pd.DataFrame, dict]:
    """Uma linha por célula do cardápio, com E1 (pedida), E2 (priorizada | pedida) e as covariáveis."""
    cel = card.copy()
    presentes = set(adesao["co_ibge"])
    ad = adesao.set_index(M12.CHAVE)
    chave = list(zip(cel["co_cnes_7d"], cel["cod_curso"]))
    tem_linha = np.array([k in ad.index for k in chave])
    prior = np.array([float(ad.loc[k, "priorizadas"]) > 0 if k in ad.index else False for k in chave])
    if ((ad["priorizadas"] > 0) & (ad["nao_priorizadas"] > 0)).any():
        raise FalhaValidacao("adesao com linha parcialmente priorizada: a regra tudo ou nada nao vale")
    cel["municipio_consta"] = cel["co_ibge"].isin(presentes).astype(int)
    if (tem_linha & (cel["municipio_consta"] == 0)).any():
        raise FalhaValidacao("celula com linha de adesao em municipio que nao consta")
    consta = cel["municipio_consta"] == 1
    # Ausente (não zero) quando o município não consta do resultado final da adesão (doc 41a, §5).
    cel["pedida"] = np.where(consta, tem_linha.astype(float), np.nan)
    cel["priorizada"] = np.where(tem_linha, prior.astype(float), np.nan)
    cel["priorizada_cardapio"] = np.where(consta, (tem_linha & prior).astype(float), np.nan)
    for c in mun.columns:
        cel[c] = cel["co_ibge"].map(mun[c])
    cel["curso_na_ponte"] = cel["cod_curso"].isin(list(ponte)).astype(int)
    cel["vinc_curso_10k"] = [vc_10k.at[i, k] if (k in vc_10k.columns and i in vc_10k.index) else np.nan
                             for i, k in zip(cel["co_ibge"], cel["cod_curso"])]
    cel["vinc_curso_regiao_10k"] = [rc_mun.at[i, k] if (k in rc_mun.columns and i in rc_mun.index) else np.nan
                                    for i, k in zip(cel["co_ibge"], cel["cod_curso"])]
    cel["curso"] = "curso" + cel["cod_curso"].astype(int).astype(str).str.zfill(2)
    chaves_card = set(chave)
    fora = adesao[[k not in chaves_card for k in zip(adesao["co_cnes_7d"], adesao["cod_curso"])]]
    info = {
        "celulas_cardapio": int(len(cel)),
        "municipios_cardapio": int(cel["co_ibge"].nunique()),
        "municipios_que_constam": int(cel.loc[consta, "co_ibge"].nunique()),
        "celulas_em_municipios_que_constam": int(consta.sum()),
        "celulas_pedidas": int(tem_linha.sum()),
        "celulas_pedidas_priorizadas": int((tem_linha & prior).sum()),
        "linhas_adesao": int(len(adesao)),
        "linhas_adesao_fora_do_cardapio": int(len(fora)),
        "linhas_adesao_fora_do_cardapio_em_municipio_do_cardapio": int(fora["co_ibge"].isin(set(cel["co_ibge"])).sum()),
        "celulas_de_cursos_fora_da_ponte": int((cel["curso_na_ponte"] == 0).sum()),
        "celulas_de_municipio_sem_ivs_oficial": int(cel["s_mil"].isna().sum()),
        "municipios_do_cardapio_sem_ivs_oficial": sorted(cel.loc[cel["s_mil"].isna(), "co_ibge"].unique().tolist()),
        "cursos_fora_da_ponte": sorted(int(k) for k in set(cel["cod_curso"]) - set(ponte)),
        "regra_tudo_ou_nada": "nenhuma linha da adesao tem priorizadas > 0 e nao priorizadas > 0 ao mesmo tempo",
    }
    return cel, info


def montar_g3(cel: pd.DataFrame, mun: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Municípios do cardápio: consta (0/1), frações de células pedidas e priorizadas (ausentes se não consta)."""
    g = cel.groupby("co_ibge").agg(n_cardapio=("cod_curso", "size"), consta=("municipio_consta", "first"),
                                    n_pedidas=("pedida", lambda s: s.sum(min_count=1)),
                                    n_priorizadas=("priorizada_cardapio", lambda s: s.sum(min_count=1)))
    g["frac_pedidas"] = np.where(g["consta"] == 1, g["n_pedidas"] / g["n_cardapio"], np.nan)
    g["frac_priorizadas"] = np.where((g["consta"] == 1) & (g["n_pedidas"] > 0),
                                     g["n_priorizadas"] / g["n_pedidas"].where(g["n_pedidas"] > 0), np.nan)
    g["frac_priorizadas_cardapio"] = np.where(g["consta"] == 1, g["n_priorizadas"] / g["n_cardapio"], np.nan)
    for c in mun.columns:
        g[c] = g.index.map(mun[c])
    g = g.reset_index()
    ref = pd.read_parquet(ARQ_G3, columns=["co_ibge", "n_celulas_cardapio", "f0_3a_consta_do_resultado_final_adesao"])
    x = g.merge(ref, on="co_ibge", how="outer", validate="one_to_one")
    if x["n_cardapio"].isna().any() or x["n_celulas_cardapio"].isna().any() or \
            (x["n_cardapio"] != x["n_celulas_cardapio"]).any() or \
            (x["consta"] != x["f0_3a_consta_do_resultado_final_adesao"]).any():
        raise FalhaValidacao("G3 daqui difere de outcomes_G3_municipio (celulas do cardapio ou consta)")
    info = {"municipios": int(len(g)), "constam": int((g["consta"] == 1).sum()),
            "constam_sem_celula_do_cardapio_pedida": int(((g["consta"] == 1) & (g["n_pedidas"] == 0)).sum()),
            "conferido_contra_outcomes_G3": True}
    return g, info


def montar_u(mun: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """U (todos os municípios com IVS oficial): células e vagas no quadro dos ciclos 1 e 2 (zero fora do quadro)."""
    u = pd.read_parquet(ARQ_U)
    if u["co_ibge"].duplicated().any():
        raise FalhaValidacao("U com municipio duplicado")
    s_b = E6.s_mil_de_ivs(u["ivs_2010_oficial"])
    if ((u["co_ibge"].map(mun["s_mil"]) - s_b).abs() > 0).any() or u["co_ibge"].map(mun["s_mil"]).isna().any():
        raise FalhaValidacao("IVS de U difere do a08")
    d = pd.DataFrame({"co_ibge": u["co_ibge"]})
    for k in CICLOS_QUADRO:
        for c in (f"n_celulas_c{k}", f"vagas_imediatas_c{k}", f"vagas_cr_c{k}"):
            if u[c].isna().any():
                raise FalhaValidacao(f"U com {c} ausente")
        d[f"n_celulas_c{k}"] = u[f"n_celulas_c{k}"].astype(float)
        d[f"vagas_c{k}"] = u[f"vagas_imediatas_c{k}"].astype(float) + u[f"vagas_cr_c{k}"].astype(float)
        if ((d[f"n_celulas_c{k}"] > 0) != (d[f"vagas_c{k}"] > 0)).any():
            raise FalhaValidacao(f"U ciclo {k}: ter celula e ter vaga divergem")
    for c in mun.columns:
        d[c] = d["co_ibge"].map(mun[c])
    info = {"municipios": int(len(d)),
            "municipios_com_celula": {f"c{k}": int((d[f"n_celulas_c{k}"] > 0).sum()) for k in CICLOS_QUADRO},
            "zero": "municipio fora do quadro da 1a chamada = zero celula e zero vaga (zero observado no quadro "
                    "completo; doc 41a, §5)"}
    return d, info


# ---------------------------------------------------------------------------
# Logit e Poisson com variância por cluster (CR1), efeitos marginais e contribuição de blocos
# ---------------------------------------------------------------------------

def desenho(df: pd.DataFrame, covs: list[dict], fe: str | None = None) -> tuple[np.ndarray, list[str], list[dict]]:
    """Matriz com constante, covariáveis (categóricas em dummies contra a referência) e efeito fixo (dummies)."""
    n = len(df)
    cols, nomes, meta = [np.ones(n)], ["const"], [{"termo": "const", "bloco": "constante", "tipo": "constante"}]
    for c in covs:
        col = c["col"]
        if c["tipo"] in ("continua", "binaria"):
            cols.append(df[col].to_numpy(dtype=float))
            nomes.append(col)
            meta.append({"termo": col, "bloco": c["bloco"], "tipo": c["tipo"], "desc": c["desc"], "fator": None})
            continue
        niveis = sorted(df[col].dropna().astype(str).unique().tolist())
        ref = c["ref"] if c["ref"] in niveis else (niveis[0] if niveis else None)
        for nv in niveis:
            if nv == ref:
                continue
            nome = f"{col}={nv}"
            cols.append((df[col].astype(str) == nv).to_numpy(dtype=float))
            nomes.append(nome)
            meta.append({"termo": nome, "bloco": c["bloco"], "tipo": "nivel", "fator": col, "ref": ref,
                         "desc": f"{c['desc']}: {nv} (ref.: {ref})"})
    if fe is not None:
        niveis = sorted(df[fe].astype(str).unique().tolist())
        for nv in niveis[1:]:
            cols.append((df[fe].astype(str) == nv).to_numpy(dtype=float))
            nomes.append(f"ef[{nv}]")
            meta.append({"termo": f"ef[{nv}]", "bloco": "efeito_fixo", "tipo": "efeito_fixo", "fator": fe})
    return np.column_stack(cols), nomes, meta


def remover_colineares(X: np.ndarray, nomes: list[str]) -> tuple[list[int], list[str]]:
    """Ordem dada; coluna sem variação ou colinear com as anteriores é descartada (a constante é mantida)."""
    manter, fora = [], []
    normas = np.linalg.norm(X, axis=0)
    Xn = X / np.where(normas > 0, normas, 1.0)
    for j in range(X.shape[1]):
        cand = manter + [j]
        if normas[j] > 0 and np.linalg.matrix_rank(Xn[:, cand], tol=1e-9) == len(cand):
            manter.append(j)
        elif j == 0:
            raise FalhaValidacao("constante colinear")
        else:
            fora.append(nomes[j])
    return manter, fora


def loglik(familia: str, X: np.ndarray, y: np.ndarray, b: np.ndarray) -> float:
    eta = X @ b
    if familia == "logit":
        return float(np.sum(y * eta - np.logaddexp(0.0, eta)))
    return float(np.sum(y * eta - np.exp(eta) - special.gammaln(y + 1.0)))


def irls(X: np.ndarray, y: np.ndarray, familia: str, maxit: int = 200, tol: float = 1e-10) -> dict:
    """Newton-Raphson (logit ou Poisson, ligação canônica) com meia-passada se a verossimilhança cair."""
    k = X.shape[1]
    b = np.zeros(k)
    if familia == "poisson":
        b[0] = math.log(max(float(np.mean(y)), 1e-12))
    ll = loglik(familia, X, y, b)
    convergiu = False
    for it in range(1, maxit + 1):
        eta = X @ b
        mu = special.expit(eta) if familia == "logit" else np.exp(eta)
        w = mu * (1.0 - mu) if familia == "logit" else mu
        grad = X.T @ (y - mu)
        Hm = X.T @ (X * w[:, None])
        try:
            passo = np.linalg.solve(Hm, grad)
        except np.linalg.LinAlgError:
            break
        t = 1.0
        while True:
            nb = b + t * passo
            nll = loglik(familia, X, y, nb)
            if np.isfinite(nll) and nll >= ll - 1e-12 or t < 1e-8:
                break
            t /= 2.0
        b, ll_ant, ll = nb, ll, nll
        if np.max(np.abs(t * passo)) < tol * (1.0 + np.max(np.abs(b))) or abs(ll - ll_ant) < 1e-12 * (1 + abs(ll)):
            convergiu = True
            break
    eta = X @ b
    mu = special.expit(eta) if familia == "logit" else np.exp(eta)
    return {"beta": b, "mu": mu, "ll": ll, "convergiu": convergiu, "iteracoes": it,
            "max_abs_eta": float(np.max(np.abs(eta)))}


def vcov_cluster(X: np.ndarray, y: np.ndarray, mu: np.ndarray, familia: str, cluster: np.ndarray) -> tuple[np.ndarray, int]:
    """CR1: (G/(G-1)) ((n-1)/(n-k)) B^-1 (soma_g s_g s_g') B^-1; com um município por cluster é o HC1."""
    n, k = X.shape
    w = mu * (1.0 - mu) if familia == "logit" else mu
    bread = np.linalg.inv(X.T @ (X * w[:, None]))
    score = X * (y - mu)[:, None]
    _, ids = np.unique(np.asarray(cluster).astype(str), return_inverse=True)
    G = int(ids.max()) + 1
    S = np.zeros((G, k))
    np.add.at(S, ids, score)
    fator = (G / (G - 1)) * ((n - 1) / (n - k))
    return bread @ (S.T @ S) @ bread * fator, G


def ll_nulo(familia: str, y: np.ndarray) -> float:
    ybar = float(np.mean(y))
    if familia == "logit":
        return float(np.sum(y * math.log(ybar) + (1 - y) * math.log(1 - ybar)))
    return float(np.sum(y * math.log(ybar) - ybar - special.gammaln(y + 1.0)))


def deviance_poisson(y: np.ndarray, mu: np.ndarray) -> float:
    termo = np.where(y > 0, y * np.log(np.where(y > 0, y, 1.0) / mu), 0.0)
    return float(2.0 * np.sum(termo - (y - mu)))


def pseudo_r2(familia: str, X: np.ndarray, y: np.ndarray, fit: dict) -> float:
    """Logit: McFadden (1 − ll/ll0). Poisson: deviance (1 − D/D0). Resíduo numérico (|R²| < 1e-12) vira 0."""
    if familia == "logit":
        r2 = 1.0 - fit["ll"] / ll_nulo(familia, y)
    else:
        r2 = 1.0 - deviance_poisson(y, fit["mu"]) / deviance_poisson(y, np.full(len(y), float(np.mean(y))))
    return 0.0 if abs(r2) < 1e-12 else r2


def remover_separacao(df: pd.DataFrame, y: str, covs: list[dict], fe: str | None, familia: str) -> tuple[pd.DataFrame, list[dict]]:
    """Linhas de um nível (de categórica, binária ou efeito fixo) em que o outcome não varia saem e são contadas.

    É a regra usual de logit com efeitos fixos: o nível prevê o outcome com perfeição e não tem efeito marginal
    estimável. No Poisson, sai o nível com contagem sempre zero. Repetida até não haver mais nível assim.
    """
    log = []
    fatores = [c["col"] for c in covs if c["tipo"] in ("categorica", "binaria")] + ([fe] if fe else [])
    while True:
        mudou = False
        for col in fatores:
            for nv, s in df.groupby(df[col].astype(str))[y]:
                const = (s.min() == s.max()) if familia == "logit" else (s.max() == 0)
                if const and len(s) < len(df):
                    log.append({"variavel": col, "nivel": nv, "linhas": int(len(s)), "outcome_constante": float(s.iloc[0])})
                    df = df[df[col].astype(str) != nv]
                    mudou = True
                    break
            if mudou:
                break
        if not mudou:
            return df, log


def ame_logit(X: np.ndarray, b: np.ndarray, V: np.ndarray, j: int, meta_j: dict, nomes: list[str],
              meta: list[dict]) -> tuple[float, float]:
    """Efeito marginal médio e EP (método delta). Contínua: derivada; dummy: diferença discreta 1 − 0 (com os
    outros níveis do mesmo fator em zero)."""
    eta = X @ b
    p = special.expit(eta)
    f = p * (1.0 - p)
    if meta_j["tipo"] == "continua":
        ame = float(b[j] * f.mean())
        grad = (b[j] * (f * (1.0 - 2.0 * p))[:, None] * X).mean(axis=0)
        grad[j] += f.mean()
    else:
        irmaos = [i for i, m in enumerate(meta) if meta_j.get("fator") and m.get("fator") == meta_j["fator"]] or [j]
        X1, X0 = X.copy(), X.copy()
        X1[:, irmaos] = 0.0
        X0[:, irmaos] = 0.0
        X1[:, j] = 1.0
        p1, p0 = special.expit(X1 @ b), special.expit(X0 @ b)
        ame = float(np.mean(p1 - p0))
        grad = ((p1 * (1 - p1))[:, None] * X1 - (p0 * (1 - p0))[:, None] * X0).mean(axis=0)
    ep = float(math.sqrt(max(grad @ V @ grad, 0.0)))
    return ame, ep


def ajustar_glm(df: pd.DataFrame, y: str, covs: list[dict], fe: str | None, familia: str,
                cluster: str = "co_ibge") -> dict:
    """Amostra de casos completos, regra de separação, colinearidade, ajuste, variância por cluster, blocos."""
    d0 = df[df[y].notna()].copy()
    desc = {}
    resto = d0
    for c in covs:
        aus = resto[c["col"]].isna()
        desc[c["col"]] = int(aus.sum())
        resto = resto[~aus]
    d, sep = remover_separacao(resto, y, covs, fe, familia)
    X, nomes, meta = desenho(d, covs, fe)
    manter, colin = remover_colineares(X, nomes)
    X, nomes, meta = X[:, manter], [nomes[i] for i in manter], [meta[i] for i in manter]
    yv = d[y].to_numpy(dtype=float)
    fit = irls(X, yv, familia)
    V, G = vcov_cluster(X, yv, fit["mu"], familia, d[cluster].to_numpy())
    r2 = pseudo_r2(familia, X, yv, fit)
    blocos = {}
    for bl in BLOCOS + ["efeito_fixo"]:
        idx = [i for i, m in enumerate(meta) if m["bloco"] != bl]
        if len(idx) == len(meta):
            continue
        fb = irls(X[:, idx], yv, familia)
        blocos[bl] = {"pseudo_r2_sem_bloco": pseudo_r2(familia, X[:, idx], yv, fb), "convergiu": fb["convergiu"]}
    idx_fe = [i for i, m in enumerate(meta) if m["bloco"] in ("constante", "efeito_fixo")]
    f_fe = irls(X[:, idx_fe], yv, familia)
    return {"d": d, "X": X, "y": yv, "nomes": nomes, "meta": meta, "fit": fit, "V": V, "G": G, "pseudo_r2": r2,
            "blocos": blocos, "pseudo_r2_so_fe": pseudo_r2(familia, X[:, idx_fe], yv, f_fe),
            "descartadas_covariavel": desc, "separacao": sep, "colineares": colin, "n_entrada": int(len(d0)),
            "familia": familia}


def _nota_amostra(r: dict) -> str:
    partes = []
    desc = {k: v for k, v in r["descartadas_covariavel"].items() if v}
    if desc:
        partes.append("fora por covariavel ausente (na ordem): " + json.dumps(desc, ensure_ascii=False))
    if r["separacao"]:
        partes.append("fora por nivel com outcome constante: " + json.dumps(
            [f"{s['variavel']}={s['nivel']} ({s['linhas']}; y={s['outcome_constante']:g})" for s in r["separacao"]],
            ensure_ascii=False))
    if r["colineares"]:
        partes.append("colunas colineares descartadas: " + ";".join(r["colineares"]))
    if not r["fit"]["convergiu"]:
        partes.append("ajuste nao convergiu")
    return _juntar(*partes)


def linhas_logit(r: dict, base: dict, esp_coef: str) -> list[dict]:
    """T5.1a/T5.1b (coeficientes e linha do modelo) e T5.1c (efeitos marginais e blocos)."""
    fit, V, X, meta, nomes = r["fit"], r["V"], r["X"], r["meta"], r["nomes"]
    ok = fit["convergiu"]
    status = "EXECUTADO" if ok else "SEM_ESTIMATIVA"
    covs_txt = ";".join(m["termo"] for m in meta if m["bloco"] not in ("constante", "efeito_fixo"))
    comum = {**base, "n_obs": len(r["y"]), "n_clusters": r["G"], "n_eventos": float(np.sum(r["y"])),
             "n_descartadas": r["n_entrada"] - len(r["y"]), "media_outcome": float(np.mean(r["y"])),
             "covariaveis": covs_txt, "status": status}
    nota = _nota_amostra(r)
    out = [nova_linha(**comum, especificacao=esp_coef, termo="(modelo)", descricao_termo="modelo completo",
                      tipo_termo="modelo", pseudo_r2=r["pseudo_r2"], unidade_estimativa=UN_R2,
                      nota=_juntar("linha do modelo: estimativa vazia; ver pseudo_r2 e contagens", nota))]
    for j, m in enumerate(meta):
        if m["bloco"] in ("constante", "efeito_fixo"):
            continue
        b, ep = float(fit["beta"][j]), float(math.sqrt(max(V[j, j], 0.0)))
        p = L.p_normal(b / ep) if ep > 0 else float("nan")
        out.append(nova_linha(**comum, especificacao=esp_coef, termo=m["termo"], descricao_termo=m["desc"],
                              bloco=m["bloco"], tipo_termo=m["tipo"], coef=b, ep_coef=ep, estimativa=b, ep=ep,
                              ic95_inf=b - Z * ep, ic95_sup=b + Z * ep, p_valor=p, unidade_estimativa=UN_LOGIT,
                              nota=_juntar(nota, "" if ep > 0 else "EP nulo")))
        ame, ep_a = ame_logit(X, fit["beta"], V, j, m, nomes, meta)
        linha = nova_linha(**comum, especificacao="T5.1c", termo=m["termo"], descricao_termo=m["desc"],
                           bloco=m["bloco"], tipo_termo=m["tipo"], coef=b, ep_coef=ep, estimativa=ame, ep=ep_a,
                           ic95_inf=ame - Z * ep_a, ic95_sup=ame + Z * ep_a,
                           p_valor=L.p_normal(ame / ep_a) if ep_a > 0 else float("nan"),
                           unidade_estimativa=UN_PROB, nota=nota)
        if m["tipo"] == "continua":
            dp = float(np.std(X[:, j], ddof=1))
            linha.update({"dp_termo": dp, "estimativa_por_dp": ame * dp, "ic95_inf_por_dp": (ame - Z * ep_a) * dp,
                          "ic95_sup_por_dp": (ame + Z * ep_a) * dp})
        out.append(linha)
    for bl, v in r["blocos"].items():
        out.append(nova_linha(**comum, especificacao="T5.1c", termo=f"bloco:{bl}", descricao_termo=ROTULO_BLOCO[bl],
                              bloco=bl, tipo_termo="bloco", pseudo_r2=r["pseudo_r2"],
                              pseudo_r2_sem_bloco=v["pseudo_r2_sem_bloco"],
                              contribuicao_bloco=r["pseudo_r2"] - v["pseudo_r2_sem_bloco"], unidade_estimativa=UN_R2,
                              nota=_juntar("linha de bloco: contribuicao = pseudo-R2 completo menos sem o bloco, "
                                           "mesma amostra", "" if v["convergiu"] else "modelo sem o bloco nao convergiu")))
    out.append(nova_linha(**comum, especificacao="T5.1c", termo="referencia:so_efeito_fixo",
                          descricao_termo="só a constante e o efeito fixo (referência)", tipo_termo="referencia",
                          pseudo_r2=r["pseudo_r2_so_fe"], unidade_estimativa=UN_R2,
                          nota="linha de referencia: pseudo-R2 do modelo so com o efeito fixo (ou so a constante)"))
    return out


def linhas_poisson(r: dict, base: dict) -> list[dict]:
    fit, V, X, meta = r["fit"], r["V"], r["X"], r["meta"]
    status = "EXECUTADO" if fit["convergiu"] else "SEM_ESTIMATIVA"
    covs_txt = ";".join(m["termo"] for m in meta if m["bloco"] != "constante")
    comum = {**base, "n_obs": len(r["y"]), "n_clusters": r["G"], "n_eventos": float(np.sum(r["y"])),
             "n_descartadas": r["n_entrada"] - len(r["y"]), "media_outcome": float(np.mean(r["y"])),
             "covariaveis": covs_txt, "status": status}
    nota = _nota_amostra(r)
    out = [nova_linha(**comum, especificacao="T5.3", termo="(modelo)", descricao_termo="modelo completo",
                      tipo_termo="modelo", pseudo_r2=r["pseudo_r2"], unidade_estimativa=UN_R2,
                      nota=_juntar("linha do modelo: estimativa vazia; ver pseudo_r2 (deviance) e contagens", nota))]
    for j, m in enumerate(meta):
        if m["bloco"] == "constante":
            continue
        b, ep = float(fit["beta"][j]), float(math.sqrt(max(V[j, j], 0.0)))
        linha = nova_linha(**comum, especificacao="T5.3", termo=m["termo"], descricao_termo=m["desc"],
                           bloco=m["bloco"], tipo_termo=m["tipo"], coef=b, ep_coef=ep, estimativa=math.exp(b),
                           ep=math.exp(b) * ep, ic95_inf=math.exp(b - Z * ep), ic95_sup=math.exp(b + Z * ep),
                           p_valor=L.p_normal(b / ep) if ep > 0 else float("nan"), unidade_estimativa=UN_RT,
                           nota=_juntar(nota, "ep = metodo delta de exp(coef); IC = exp(coef +- 1,96 EP)"))
        if m["tipo"] == "continua":
            dp = float(np.std(X[:, j], ddof=1))
            linha.update({"dp_termo": dp, "estimativa_por_dp": math.exp(b * dp),
                          "ic95_inf_por_dp": math.exp((b - Z * ep) * dp), "ic95_sup_por_dp": math.exp((b + Z * ep) * dp)})
        out.append(linha)
    for bl, v in r["blocos"].items():
        out.append(nova_linha(**comum, especificacao="T5.3", termo=f"bloco:{bl}", descricao_termo=ROTULO_BLOCO[bl],
                              bloco=bl, tipo_termo="bloco", pseudo_r2=r["pseudo_r2"],
                              pseudo_r2_sem_bloco=v["pseudo_r2_sem_bloco"],
                              contribuicao_bloco=r["pseudo_r2"] - v["pseudo_r2_sem_bloco"], unidade_estimativa=UN_R2,
                              no_protocolo=False, rotulo=ROTULO_COMPLEMENTAR,
                              nota="linha de bloco: contribuicao = pseudo-R2 (deviance) completo menos sem o bloco"))
    return out


# ---------------------------------------------------------------------------
# T5.2: RDD nos cortes (rdd_lib.rd_empilhado; um corte = um grupo)
# ---------------------------------------------------------------------------

def matriz_z(d: pd.DataFrame, covs: list[dict]) -> tuple[np.ndarray, list[str]]:
    X, nomes, _ = desenho(d, covs, None)
    # Linha com covariável ausente: NaN na linha inteira de Z (a rdd_lib descarta e conta); nunca zero.
    aus = np.zeros(len(d), dtype=bool)
    for c in covs:
        aus |= d[c["col"]].isna().to_numpy()
    Zm = X[:, 1:].copy()
    Zm[aus, :] = np.nan
    return Zm, nomes[1:]


def rdd(d: pd.DataFrame, y: str, corte, *, fe: str | None, covs: list[dict] | None, cluster_sempre: bool) -> dict:
    cortes = CORTES if corte == EMPILHADO else (corte,)
    a = T23.montar_amostra([(d, c, str(c)) for c in cortes], empilhada=True)
    Zm = nomes = None
    if covs:
        Zm, nomes = matriz_z(a.d, covs)
    usa_cluster = cluster_sempre or corte == EMPILHADO
    r = L.rd_empilhado(a.s, a.col(y), a.c, grupo=a.g, h_mil=H, cluster=a.cl if usa_cluster else None,
                       ids_unidade=a.cl, efeitos_fixos=a.d[fe].astype(str).to_numpy() if fe else None, Z=Zm,
                       nomes_z=nomes, detalhes=True)
    r["media_abaixo"] = float("nan")
    if "_detalhes" in r:
        det = r["_detalhes"]
        ab = det["usa"] & (det["x_mil"] <= 0)
        r["media_abaixo"] = float(np.mean(det["y"][ab])) if ab.any() else float("nan")
    r["_amostra"] = a
    return r


T52_CELULA = [
    {"id": "E1_pedida", "y": "pedida", "pop": "celulas do cardapio em municipios que constam", "no_protocolo": True,
     "desc": "celula do cardapio pedida pelo gestor (tem linha no resultado final da adesao)"},
    {"id": "E2_priorizada", "y": "priorizada", "pop": "celulas pedidas", "no_protocolo": True,
     "desc": "celula pedida priorizada pela SGTES"},
    {"id": "E2_priorizada_cardapio", "y": "priorizada_cardapio", "pop": "celulas do cardapio em municipios que constam",
     "no_protocolo": False, "rot": ROTULO_LEITURA,
     "desc": "celula do cardapio pedida e priorizada (denominador = cardapio)"},
]
T52_MUN = [
    {"id": "E1_frac_pedidas", "y": "frac_pedidas", "pop": "municipios do cardapio que constam", "no_protocolo": True,
     "desc": "fracao das celulas do cardapio do municipio que foram pedidas"},
    {"id": "E2_frac_priorizadas", "y": "frac_priorizadas", "pop": "municipios que constam com >= 1 celula pedida",
     "no_protocolo": True, "desc": "fracao das celulas pedidas do municipio que foram priorizadas"},
    {"id": "E2_frac_priorizadas_cardapio", "y": "frac_priorizadas_cardapio", "pop": "municipios do cardapio que constam",
     "no_protocolo": False, "rot": ROTULO_LEITURA,
     "desc": "fracao das celulas do cardapio do municipio que foram pedidas e priorizadas"},
    {"id": "E1_presenca", "y": "consta", "pop": "municipios do cardapio (G3)", "no_protocolo": True,
     "desc": "municipio consta do resultado final da adesao (linha separada do §1)"},
]


def estimar_t52(cel: pd.DataFrame, g3: pd.DataFrame) -> list[dict]:
    linhas = []
    cel_iv = cel[cel["s_mil"].notna()].copy()
    g3_iv = g3[g3["s_mil"].notna()].copy()
    for unidade, specs, base, fe, covs in (("celula", T52_CELULA, cel_iv, "curso", COVS_CCFT_CELULA),
                                           ("municipio", T52_MUN, g3_iv, None, COVS_CCFT_MUN)):
        for o in specs:
            d = base[base[o["y"]].notna()]
            for esp, cv in (("T5.2a", None), ("T5.2b", covs)):
                nomes_z = ";".join(matriz_z(d, cv)[1]) if cv else ""
                for corte in CORTES + (EMPILHADO,):
                    r = rdd(d, o["y"], corte, fe=fe, covs=cv, cluster_sempre=(unidade == "celula"))
                    est = ("local linear sharp, kernel triangular, h = 0,050" +
                           ("; cortes empilhados (intercepto e inclinacoes por corte, salto comum)" if corte == EMPILHADO else "")
                           + ("; efeito fixo de curso" if fe else "")
                           + ("; covariaveis lineares nao interagidas (CCFT)" if cv else "")
                           + ("; CR1 por municipio" if (unidade == "celula" or corte == EMPILHADO) else "; EP HC1"))
                    tau, ep = r["tau"], r["ep"]
                    linha = nova_linha(
                        especificacao=esp, etapa=o["id"].split("_")[0], ciclo="3", unidade_analise=unidade,
                        populacao=o["pop"], outcome=o["id"], descricao_outcome=o["desc"],
                        variante="principal" if o["no_protocolo"] else "leitura_alternativa", termo="salto_no_corte",
                        descricao_termo="lado de bolsa maior menos lado de bolsa menor no corte", tipo_termo="salto",
                        estimador=est, corte=str(corte if corte == EMPILHADO else f"{corte / 1000:.3f}"),
                        h=H / 1000.0, no_protocolo=o["no_protocolo"], rotulo=o.get("rot", ""),
                        n_obs=r.get("n_obs"), n_clusters=r.get("n_clusters"), n_abaixo=r.get("n_abaixo"),
                        n_acima=r.get("n_acima"),
                        n_descartadas=int(r.get("n_descartadas_y_ausente", 0) or 0)
                        + int(r.get("n_descartadas_covariavel_ausente", 0) or 0),
                        estimativa=tau, ep=ep, ic95_inf=r["ic95_inf"], ic95_sup=r["ic95_sup"], p_valor=r["p_valor"],
                        media_outcome=r["media_abaixo"], unidade_estimativa=UN_FRAC, covariaveis=nomes_z,
                        efeitos_fixos="curso" if fe else "",
                        nota=_juntar(r.get("nota", ""),
                                     f"colunas descartadas: {r['covariaveis_descartadas']}" if r.get("covariaveis_descartadas") else "",
                                     "media_outcome = media bruta do lado de baixo na janela"))
                    if not np.isfinite(tau):
                        linha["status"] = "SEM_ESTIMATIVA"
                        linha["nota"] = _juntar(linha["nota"], "rdd_lib devolveu NaN")
                    linhas.append(linha)
    return linhas


def aplicar_bky(est: pd.DataFrame) -> pd.DataFrame:
    m = (est["especificacao"].isin(["T5.2a", "T5.2b"]) & est["no_protocolo"].astype(bool)
         & est["p_valor"].notna())
    est["entra_bky"] = m
    est.loc[m, "q_bky"] = L.qvalores_bky(est.loc[m, "p_valor"].to_numpy(dtype=float))
    return est


# ---------------------------------------------------------------------------
# Estimação completa
# ---------------------------------------------------------------------------

def carregar() -> dict:
    rv = ler_ivs()
    pop = ler_populacao()
    regic, info_regic = ler_regic()
    capital = ler_capital()
    cir, info_cir = ler_cir()
    ponte = ler_ponte()
    cbos = sorted({c for v in ponte.values() for c in v})
    cnes, info_cnes = ler_cnes_pre(cbos)
    sia, info_sia = ler_sia_pre()
    card = ler_cardapio_com_atributos()
    adesao, diag_ad = M12.ler_adesao()
    g3_ref = pd.read_parquet(ARQ_G3, columns=["co_ibge"])
    extras = sorted(set(card["co_ibge"]) | set(g3_ref["co_ibge"]))
    mun, vc_10k, rc_mun, info_mun = montar_municipios(cnes, ponte, sia, pop, regic, capital, cir, rv, extras)
    cel, info_cel = montar_celulas(card, adesao, mun, vc_10k, rc_mun, ponte)
    g3, info_g3 = montar_g3(cel, mun)
    u, info_u = montar_u(mun)
    return {"rv": rv, "mun": mun, "cel": cel, "g3": g3, "u": u, "ponte": ponte, "adesao_diag": diag_ad,
            "info": {"regic": info_regic, "cir": info_cir, "cnes_pre": info_cnes, "sia_pre": info_sia,
                     "municipios": info_mun, "celulas": info_cel, "g3": info_g3, "u": info_u}}


T51 = [
    {"etapa": "E1", "esp": "T5.1a", "y": "pedida", "base": "cel", "covs": COVS_CELULA, "fe": "curso",
     "unidade": "celula", "pop": "celulas do cardapio do ciclo 3 em municipios que constam do resultado da adesao",
     "desc": "celula pedida pelo gestor (tem linha no resultado final da adesao)", "variante": "principal"},
    {"etapa": "E2", "esp": "T5.1b", "y": "priorizada", "base": "cel", "covs": COVS_CELULA, "fe": "curso",
     "unidade": "celula", "pop": "celulas pedidas (celulas do cardapio com linha na adesao)",
     "desc": "celula pedida priorizada pela SGTES (tudo ou nada)", "variante": "principal"},
    {"etapa": "E1", "esp": "T5.1a", "y": "consta", "base": "g3", "covs": COVS_MUN, "fe": None,
     "unidade": "municipio", "pop": "municipios do cardapio do ciclo 3 (G3)",
     "desc": "municipio consta do resultado final da adesao (linha separada do §1)", "variante": "presenca_municipio"},
    {"etapa": "E1", "esp": "T5.1a", "y": "pedida", "base": "cel", "covs": COVS_CELULA_SENS, "fe": "curso",
     "unidade": "celula", "pop": "celulas do cardapio em municipios que constam (todos os cursos)",
     "desc": "celula pedida; capacidade e escassez do conjunto alvo no lugar das do curso",
     "variante": "sensibilidade_todos_os_cursos", "rot": ROTULO_FORA},
    {"etapa": "E2", "esp": "T5.1b", "y": "priorizada", "base": "cel", "covs": COVS_CELULA_SENS, "fe": "curso",
     "unidade": "celula", "pop": "celulas pedidas (todos os cursos)",
     "desc": "celula priorizada; capacidade e escassez do conjunto alvo no lugar das do curso",
     "variante": "sensibilidade_todos_os_cursos", "rot": ROTULO_FORA},
]


def estimar_tudo(dados: dict) -> tuple[pd.DataFrame, dict]:
    linhas, modelos = [], {}
    for s in T51:
        base = dados[s["base"]]
        r = ajustar_glm(base, s["y"], s["covs"], s["fe"], "logit")
        meta = {"etapa": s["etapa"], "ciclo": "3", "unidade_analise": s["unidade"], "populacao": s["pop"],
                "outcome": s["y"], "descricao_outcome": s["desc"], "variante": s["variante"],
                "estimador": "logit (Newton-Raphson), EP CR1 por municipio" + (", efeito fixo de curso" if s["fe"] else "")
                             + "; efeitos marginais medios pelo metodo delta",
                "efeitos_fixos": "curso" if s["fe"] else "", "no_protocolo": "rot" not in s, "rotulo": s.get("rot", "")}
        linhas += linhas_logit(r, meta, s["esp"])
        modelos[f"{s['esp']}|{s['etapa']}|{s['variante']}"] = _resumo_modelo(r)
    linhas += estimar_t52(dados["cel"], dados["g3"])
    for k in CICLOS_QUADRO:
        for y, desc in ((f"n_celulas_c{k}", "numero de celulas no quadro da 1a chamada"),
                        (f"vagas_c{k}", "numero de vagas (imediatas + cadastro reserva) no quadro da 1a chamada")):
            r = ajustar_glm(dados["u"], y, COVS_MUN, None, "poisson")
            meta = {"etapa": "E3", "ciclo": str(k), "unidade_analise": "municipio",
                    "populacao": "U: todos os municipios com IVS 2010 oficial (zero fora do quadro)", "outcome": y,
                    "descricao_outcome": desc, "variante": "principal",
                    "estimador": "Poisson (Newton-Raphson), EP robusto HC1 (CR1 com um municipio por cluster)"}
            linhas += linhas_poisson(r, meta)
            modelos[f"T5.3|c{k}|{y}"] = _resumo_modelo(r)
    est = pd.DataFrame(linhas, columns=COLUNAS)
    est = aplicar_bky(est)
    return est, modelos


def _resumo_modelo(r: dict) -> dict:
    return {"n_obs": int(len(r["y"])), "n_entrada": r["n_entrada"], "n_clusters": r["G"],
            "eventos_ou_soma": float(np.sum(r["y"])), "pseudo_r2": r["pseudo_r2"],
            "pseudo_r2_so_efeito_fixo": r["pseudo_r2_so_fe"], "convergiu": r["fit"]["convergiu"],
            "iteracoes": r["fit"]["iteracoes"], "max_abs_indice_linear": r["fit"]["max_abs_eta"],
            "descartadas_por_covariavel_ausente": r["descartadas_covariavel"], "separacao": r["separacao"],
            "colineares_descartadas": r["colineares"], "familia": r["familia"]}


# ---------------------------------------------------------------------------
# Figuras (com "Como ler" dentro da imagem)
# ---------------------------------------------------------------------------

def _fmt(v, casas=1, sinal=True) -> str:
    if v is None or not np.isfinite(v):
        return "—"
    return (f"{v:+.{casas}f}" if sinal else f"{v:.{casas}f}").replace("-", "−").replace(".", ",")


def _rotulo_curto(r: dict) -> str:
    d = str(r["descricao_termo"])
    if r["tipo_termo"] == "continua":
        d += " (+1 DP)"
    return d if len(d) <= 78 else d[:75] + "..."


COMO_LER_AME = (
    "COMO LER. Cada linha é uma característica medida antes do ciclo 3 (do estabelecimento, do município, da "
    "capacidade e da produção pré-programa, da região de saúde e o IVS). O ponto é o efeito marginal médio do logit: "
    "quantos pontos percentuais a probabilidade muda, em média, quando a característica sobe um desvio-padrão (para "
    "as medidas contínuas, marcadas '+1 DP') ou quando a célula tem o atributo em vez da categoria de referência "
    "(entre parênteses). Todas as características entram juntas, com efeito fixo de curso: cada ponto compara células "
    "do mesmo curso que diferem só naquele atributo, mantidas as demais. A barra é o IC 95% (EP com cluster por "
    "município). Barra que não cruza a linha do zero: associação que os dados distinguem de zero; barra que cruza: os "
    "dados não distinguem a associação de zero, o que não prova que ela seja zero. À esquerda, o pedido do gestor "
    "(entre as células do cardápio de municípios que constam do resultado); à direita, a priorização da SGTES (entre "
    "as células pedidas). É descritivo: mostra com o que o pedido e a priorização andam juntos, não por que o "
    "Ministério decide; o critério oficial de priorização não é publicado. EMPIRICO.")
COMO_LER_BLOCOS = (
    "COMO LER. Cada barra mede quanto um grupo de características ajuda a separar as células (ou municípios) que "
    "foram pedidos ou priorizados das que não foram: é a queda do pseudo-R² de McFadden quando o grupo sai do "
    "modelo, com a mesma amostra e as demais características mantidas. Barra maior: o grupo carrega informação que os "
    "outros não têm. Barra perto de zero: o que o grupo diz já está nos outros (ou não ajuda). As barras não somam o "
    "total, porque os grupos se sobrepõem. A marca vertical cinza é o pseudo-R² do modelo completo. Pedido = célula "
    "pedida pelo gestor; priorização = célula pedida priorizada pela SGTES; presença = município consta do resultado "
    "da adesão. É descritivo: não diz qual critério o Ministério usa. EMPIRICO.")
COMO_LER_T52_MUN = (
    "COMO LER. Cada painel junta os cortes 0,300 e 0,400 do IVS 2010 oficial: o eixo horizontal é a distância do IVS "
    "do município ao corte (à direita, bolsa maior; à esquerda, bolsa menor). Entram os municípios do cardápio do "
    "ciclo 3 que constam do resultado da adesão. À esquerda, a fração das células do cardápio que o gestor pediu; à "
    "direita, a fração das células pedidas que a SGTES priorizou. Cada ponto é a reta média mais o resíduo médio dos "
    "municípios de uma faixa de 0,010; o tamanho conta municípios. A reta é ajustada de cada lado (local linear, "
    "kernel triangular, h = 0,050), a faixa clara é o IC 95% (CR1 por município) e a seta laranja é o salto no "
    "corte, com valor, IC e p no título. O salto mede o pacote do corte (bolsa anunciada +R$ 5 mil e outras regras "
    "federais nos mesmos cortes), não a participação no PMM-E. Se o IC 95% contém zero, os dados não distinguem o "
    "salto de zero, o que não prova que ele seja zero. EMPIRICO.")
COMO_LER_T52_CEL = (
    "COMO LER. Aqui a unidade é a célula do cardápio do ciclo 3 (estabelecimento × curso), nos cortes 0,300 e 0,400 "
    "empilhados; o eixo horizontal é a distância do IVS 2010 oficial do município da célula ao corte. À esquerda, a "
    "probabilidade de a célula ser pedida pelo gestor (células de municípios que constam do resultado); à direita, a "
    "de a célula pedida ser priorizada pela SGTES. As retas estão ajustadas pelo efeito fixo de curso: são as da "
    "célula com a composição média de cursos da janela, e cada ponto é essa reta mais o resíduo médio das células de "
    "uma faixa de 0,010 (o tamanho conta células). A faixa clara é o IC 95% (CR1 por município) e a seta laranja é o "
    "salto no corte, com valor em pontos percentuais, IC e p no título. O salto mede o pacote do corte, não a bolsa "
    "sozinha nem a participação no PMM-E. Se o IC 95% contém zero, os dados não distinguem o salto de zero. EMPIRICO.")
COMO_LER_T53 = (
    "COMO LER. Cada linha é uma característica municipal pré-determinada; o ponto é a razão de taxas do Poisson: por "
    "quanto o número esperado de células (ou de vagas) no quadro da 1ª chamada se multiplica quando a característica "
    "sobe um desvio-padrão (medidas contínuas, '+1 DP') ou quando o município tem o atributo em vez da referência. "
    "1 = nenhuma diferença; 1,5 = 50% a mais; 0,5 = metade. Entram todos os municípios com IVS oficial, valendo zero "
    "os que não tiveram célula no quadro. A barra é o IC 95% (EP robusto). Ciclos 1 e 2 em cores diferentes. É "
    "descritivo: dá base ao A4 do P2 e não diz por que o quadro saiu assim. O eixo é logarítmico. EMPIRICO.")


def _forest(ax, linhas: list[dict], escala: float, cor: str, desloc: float = 0.0, log: bool = False, rotulos=True,
            posicao: dict | None = None):
    """Pontos e IC 95% por linha; `posicao` (termo -> y) alinha painéis com conjuntos de termos diferentes."""
    if posicao is None:
        posicao = {r["termo"]: float(len(linhas) - 1 - i) for i, r in enumerate(linhas)}
    ys = np.array([posicao[r["termo"]] for r in linhas]) + desloc
    for yv, r in zip(ys, linhas):
        cont = r["tipo_termo"] == "continua"
        v = r["estimativa_por_dp"] if cont else r["estimativa"]
        lo = r["ic95_inf_por_dp"] if cont else r["ic95_inf"]
        hi = r["ic95_sup_por_dp"] if cont else r["ic95_sup"]
        ax.plot([lo * escala, hi * escala], [yv, yv], color=cor, lw=1.6, solid_capstyle="round")
        ax.plot([v * escala], [yv], "o", color=cor, ms=5.5, mec="white", mew=0.8)
    if rotulos:
        ax.set_yticks([posicao[r["termo"]] for r in linhas])
        ax.set_yticklabels([_rotulo_curto(r) for r in linhas], fontsize=8)
    from matplotlib.ticker import FixedLocator, FuncFormatter, NullFormatter
    if log:
        ax.set_xscale("log")
        ax.axvline(1.0, color=T23.TINTA_2, lw=0.9, ls="--")
        ax.xaxis.set_major_locator(FixedLocator([0.125, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0]))
        ax.xaxis.set_minor_formatter(NullFormatter())
    else:
        ax.axvline(0.0, color=T23.TINTA_2, lw=0.9, ls="--")
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _=None: f"{v:g}".replace(".", ",").replace("-", "−")))
    ax.grid(axis="x", color="#e4e3df", lw=0.6)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)


def _como_ler(fig, texto: str, y: float = 0.01, largura: int = 205) -> None:
    import textwrap
    fig.text(0.02, y, "\n".join(textwrap.wrap(texto, largura)), fontsize=8.2, color=T23.TINTA_2, va="bottom",
             ha="left")


def _ordem(est: pd.DataFrame, filtro: dict) -> list[dict]:
    m = np.ones(len(est), dtype=bool)
    for k, v in filtro.items():
        m &= est[k].astype(str) == str(v)
    sub = est[m & est["tipo_termo"].isin(["continua", "binaria", "nivel"])]
    ordem_bloco = {b: i for i, b in enumerate(BLOCOS)}
    sub = sub.assign(_o=sub["bloco"].map(ordem_bloco)).sort_values(["_o", "termo"], kind="stable")
    return sub.drop(columns="_o").to_dict("records")


def gerar_figuras(est: pd.DataFrame, dados: dict, dir_fig: Path) -> list[dict]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    dir_fig.mkdir(parents=True, exist_ok=True)
    for antigo in dir_fig.glob("*.png"):
        antigo.unlink()
    feitas = []
    # 1. Efeitos marginais médios (T5.1c), pedido e priorização.
    filtros = [("Pedido do gestor (E1, célula do cardápio)", {"especificacao": "T5.1c", "etapa": "E1", "variante": "principal"}),
               ("Priorização da SGTES (E2, célula pedida)", {"especificacao": "T5.1c", "etapa": "E2", "variante": "principal"})]
    lin = [_ordem(est, f) for _, f in filtros]
    n = max(len(x) for x in lin)
    fig, axs = plt.subplots(1, 2, figsize=(15, 0.33 * n + 4.6), sharey=False)
    fig.patch.set_facecolor(T23.SUPERFICIE)
    for ax, (tit, _), ls in zip(axs, filtros, lin):
        _forest(ax, ls, 100.0, T23.COR_DENTRO, rotulos=True)
        ax.set_title(tit, fontsize=11)
        ax.set_xlabel("efeito marginal médio (p.p.; contínuas: +1 DP)", fontsize=9)
        ax.set_facecolor(T23.SUPERFICIE)
    fig.suptitle("P5 — com o que o pedido e a priorização das células do ciclo 3 andam juntos (descritivo)", fontsize=13)
    fig.tight_layout(rect=(0, 0.17, 1, 0.96))
    _como_ler(fig, COMO_LER_AME)
    nome = "P5_T51_efeitos_marginais.png"
    fig.savefig(dir_fig / nome, dpi=110, facecolor=fig.get_facecolor())
    plt.close(fig)
    feitas.append({"arquivo": rotulo(dir_fig / nome), "linhas": {t: len(x) for (t, _), x in zip(filtros, lin)},
                   "fonte": "P5_estimativas.csv, especificacao T5.1c, variante principal"})
    # 2. Contribuição de cada bloco.
    grupos = [("pedido", {"especificacao": "T5.1c", "etapa": "E1", "variante": "principal"}),
              ("priorização", {"especificacao": "T5.1c", "etapa": "E2", "variante": "principal"}),
              ("presença", {"especificacao": "T5.1c", "etapa": "E1", "variante": "presenca_municipio"})]
    fig, axs = plt.subplots(1, 3, figsize=(15, 5.8), sharey=True)
    fig.patch.set_facecolor(T23.SUPERFICIE)
    blocos_fig = BLOCOS + ["efeito_fixo"]
    valores = {}
    for ax, (nome_g, f) in zip(axs, grupos):
        m = np.ones(len(est), dtype=bool)
        for k, v in f.items():
            m &= est[k].astype(str) == str(v)
        sub = est[m & (est["tipo_termo"] == "bloco")].set_index("bloco")
        vals = [float(sub.at[b, "contribuicao_bloco"]) if b in sub.index else np.nan for b in blocos_fig]
        valores[nome_g] = dict(zip(blocos_fig, vals))
        ypos = np.arange(len(blocos_fig))[::-1]
        ax.barh(ypos, np.nan_to_num(vals), color=T23.COR_DENTRO, height=0.6)
        for yv, v in zip(ypos, vals):
            ax.text((v if np.isfinite(v) else 0) + 0.002, yv, _fmt(v, 3, False) if np.isfinite(v) else "não se aplica",
                    va="center", fontsize=8)
        r2 = sub["pseudo_r2"].dropna()
        sub_tit = ""
        if len(r2):
            ax.axvline(float(r2.iloc[0]), color=T23.COR_FORA, lw=1.2)
            sub_tit = f"\npseudo-R² completo = {_fmt(float(r2.iloc[0]), 3, False)} (linha cinza)"
        ax.set_yticks(ypos)
        ax.set_yticklabels([ROTULO_BLOCO[b] for b in blocos_fig], fontsize=8)
        ax.set_title(nome_g.capitalize() + sub_tit, fontsize=10)
        from matplotlib.ticker import FuncFormatter
        ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _=None: f"{v:.2f}".replace(".", ",")))
        ax.set_xlabel("queda do pseudo-R² sem o grupo", fontsize=9)
        ax.set_facecolor(T23.SUPERFICIE)
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)
    fig.suptitle("P5 — quanto cada grupo de características separa o que foi pedido, priorizado ou presente (descritivo)",
                 fontsize=12)
    fig.tight_layout(rect=(0, 0.2, 1, 0.94))
    _como_ler(fig, COMO_LER_BLOCOS)
    nome = "P5_T51_contribuicao_blocos.png"
    fig.savefig(dir_fig / nome, dpi=110, facecolor=fig.get_facecolor())
    plt.close(fig)
    feitas.append({"arquivo": rotulo(dir_fig / nome), "contribuicoes": valores,
                   "fonte": "P5_estimativas.csv, especificacao T5.1c, tipo_termo bloco"})
    # 3. RDD por município (T5.2a, empilhado).
    g3 = dados["g3"]
    g3 = g3[g3["s_mil"].notna()]
    paineis, meta = [], []
    for oid, col, rot_p in (("E1_frac_pedidas", "frac_pedidas", "Fração das células do cardápio pedidas"),
                            ("E2_frac_priorizadas", "frac_priorizadas", "Fração das células pedidas priorizadas")):
        d = g3[g3[col].notna()]
        r = rdd(d, col, EMPILHADO, fe=None, covs=None, cluster_sempre=False)
        a = r["_amostra"]
        cur, y_p, _ = T23.curva_empilhada(r, a)
        x = L.normalizar_s_mil(a.s) - a.c
        dentro = np.isfinite(y_p)
        paineis.append({"x": np.where(dentro, x, np.nan), "y": y_p, "dentro": dentro, "corte": 0, "curva": cur,
                        "rotulo": f"{rot_p} (municípios que constam, cortes empilhados)",
                        "titulo": T24._titulo(r, "p.p.", casas=1, pp=True)})
        meta.append({"outcome": oid, "unidade_analise": "municipio", "corte": EMPILHADO, "especificacao": "T5.2a",
                     "tau": r["tau"], "ic95_inf": r["ic95_inf"], "ic95_sup": r["ic95_sup"], "p_valor": r["p_valor"]})
    nome = "P5_T52_rdd_municipio_empilhado.png"
    T23.desenhar(paineis, "T5.2a — pedido e priorização nos cortes do IVS, por município (ciclo 3, cortes empilhados)",
                 "Fração de células", "distância ao corte (IVS 2010 oficial − corte)", COMO_LER_T52_MUN, dir_fig / nome,
                 unidade_n=("município", "municípios"), tamanhos_leg="auto", rotulo_salto="topo")
    feitas.append({"arquivo": rotulo(dir_fig / nome), "paineis": meta})
    # 4. RDD por célula com efeito fixo de curso (T5.2a, empilhado).
    cel = dados["cel"]
    cel = cel[cel["s_mil"].notna()]
    paineis, meta = [], []
    for oid, col, rot_p in (("E1_pedida", "pedida", "Probabilidade de a célula ser pedida"),
                            ("E2_priorizada", "priorizada", "Probabilidade de a célula pedida ser priorizada")):
        d = cel[cel[col].notna()]
        r = rdd(d, col, EMPILHADO, fe="curso", covs=None, cluster_sempre=True)
        a = r["_amostra"]
        cur, y_p = T24.curva_empilhada_fe(r, a)
        x = L.normalizar_s_mil(a.s) - a.c
        dentro = np.isfinite(y_p)
        paineis.append({"x": np.where(dentro, x, np.nan), "y": y_p, "dentro": dentro, "corte": 0, "curva": cur,
                        "rotulo": f"{rot_p} (células, cortes empilhados, efeito fixo de curso)",
                        "titulo": T24._titulo(r, "p.p.", casas=1, pp=True)})
        meta.append({"outcome": oid, "unidade_analise": "celula", "corte": EMPILHADO, "especificacao": "T5.2a",
                     "tau": r["tau"], "ic95_inf": r["ic95_inf"], "ic95_sup": r["ic95_sup"], "p_valor": r["p_valor"]})
    nome = "P5_T52_rdd_celula_empilhado.png"
    T23.desenhar(paineis, "T5.2a — pedido e priorização nos cortes do IVS, por célula (ciclo 3, efeito fixo de curso)",
                 "Probabilidade (ajustada pelo efeito fixo de curso)", "distância ao corte (IVS 2010 oficial − corte)",
                 COMO_LER_T52_CEL, dir_fig / nome, unidade_n=("célula", "células"), tamanhos_leg="auto",
                 rotulo_salto="topo")
    feitas.append({"arquivo": rotulo(dir_fig / nome), "paineis": meta})
    # 5. T5.3: razão de taxas por DP, ciclos 1 e 2.
    fig, axs = plt.subplots(1, 2, figsize=(15, 9.5), sharey=True)
    fig.patch.set_facecolor(T23.SUPERFICIE)
    cores = {1: T23.COR_DENTRO, 2: T23.COR_SALTO}
    contagem = {}
    for ax, (pref, tit) in zip(axs, (("n_celulas", "Número de células no quadro"),
                                     ("vagas", "Número de vagas no quadro (imediatas + CR)"))):
        por_ciclo = {k: _ordem(est, {"especificacao": "T5.3", "outcome": f"{pref}_c{k}"}) for k in CICLOS_QUADRO}
        termos, vistos = [], set()
        for k in CICLOS_QUADRO:
            for r in por_ciclo[k]:
                if r["termo"] not in vistos:
                    vistos.add(r["termo"])
                    termos.append(r)
        posicao = {r["termo"]: float(len(termos) - 1 - i) for i, r in enumerate(termos)}
        for i, k in enumerate(CICLOS_QUADRO):
            contagem[f"{pref}_c{k}"] = len(por_ciclo[k])
            _forest(ax, por_ciclo[k], 1.0, cores[k], desloc=0.18 * (1 - 2 * i), log=True, rotulos=False,
                    posicao=posicao)
            ax.plot([], [], "o-", color=cores[k], label=f"ciclo {k}")
        ax.set_yticks([posicao[r["termo"]] for r in termos])
        ax.set_yticklabels([_rotulo_curto(r) for r in termos], fontsize=8)
        ax.set_title(tit, fontsize=11)
        ax.set_xlabel("razão de taxas (contínuas: +1 DP; eixo log)", fontsize=9)
        ax.legend(loc="lower right", fontsize=8, frameon=False)
        ax.set_facecolor(T23.SUPERFICIE)
    fig.suptitle("T5.3 — características municipais associadas ao tamanho do quadro dos ciclos 1 e 2 (descritivo)",
                 fontsize=13)
    fig.tight_layout(rect=(0, 0.12, 1, 0.95))
    _como_ler(fig, COMO_LER_T53)
    nome = "P5_T53_razao_taxas.png"
    fig.savefig(dir_fig / nome, dpi=110, facecolor=fig.get_facecolor())
    plt.close(fig)
    feitas.append({"arquivo": rotulo(dir_fig / nome), "linhas": contagem,
                   "fonte": "P5_estimativas.csv, especificacao T5.3"})
    return feitas


# ---------------------------------------------------------------------------
# Doc 57e: blocos gerados entre marcadores (nenhum número digitado na prosa)
# ---------------------------------------------------------------------------

MARCA = re.compile(r"(<!-- P5:(?P<nome>[A-Za-z0-9_]+):inicio -->\n)(?P<corpo>.*?)(\n<!-- P5:(?P=nome):fim -->)", re.S)


def aplicar_tabelas_doc(texto: str, tabelas: dict[str, str]) -> str:
    def sub(m):
        nome = m.group("nome")
        if nome not in tabelas:
            raise KeyError(f"bloco {nome} nao gerado")
        return m.group(1) + tabelas[nome] + m.group(4)
    return MARCA.sub(sub, texto)


def tabelas_no_doc(texto: str) -> dict[str, str]:
    return {m.group("nome"): m.group("corpo") for m in MARCA.finditer(texto)}


def _n(v, casas=1, pp=False, sinal=True) -> str:
    if v is None or (isinstance(v, float) and not math.isfinite(v)) or pd.isna(v):
        return "—"
    v = float(v) * (100.0 if pp else 1.0)
    txt = f"{v:+.{casas}f}" if sinal else f"{v:.{casas}f}"
    return txt.replace("-", "−").replace(".", ",")


def _i(v) -> str:
    return "—" if v is None or pd.isna(v) else f"{int(v)}"


def _tab(cab: list[str], linhas: list[list[str]]) -> str:
    out = ["| " + " | ".join(cab) + " |", "|" + "|".join("---" for _ in cab) + "|"]
    out += ["| " + " | ".join(l) + " |" for l in linhas]
    return "\n".join(out)


def _sel(est: pd.DataFrame, **f) -> pd.DataFrame:
    m = np.ones(len(est), dtype=bool)
    for k, v in f.items():
        m &= est[k].astype(str) == str(v)
    return est[m]


def _exclui_zero(lo, hi, ref=0.0) -> bool:
    return bool(np.isfinite(lo) and np.isfinite(hi) and (lo > ref or hi < ref))


def _ame_txt(r: dict) -> tuple[str, str]:
    if r["tipo_termo"] == "continua":
        return _n(r["estimativa_por_dp"], 1, pp=True) + " p.p.", \
            f"[{_n(r['ic95_inf_por_dp'], 1, pp=True)}; {_n(r['ic95_sup_por_dp'], 1, pp=True)}]"
    return _n(r["estimativa"], 1, pp=True) + " p.p.", f"[{_n(r['ic95_inf'], 1, pp=True)}; {_n(r['ic95_sup'], 1, pp=True)}]"


def tabela_ame(est: pd.DataFrame, **f) -> str:
    sub = _sel(est, especificacao="T5.1c", **f)
    sub = sub[sub["tipo_termo"].isin(["continua", "binaria", "nivel"])]
    if sub.empty:
        return "_Sem linhas._"
    linhas = []
    ordem_bloco = {b: i for i, b in enumerate(BLOCOS)}
    sub = sub.assign(_o=sub["bloco"].map(ordem_bloco)).sort_values(["_o", "termo"], kind="stable")
    for r in sub.to_dict("records"):
        v, ic = _ame_txt(r)
        lo, hi = (r["ic95_inf_por_dp"], r["ic95_sup_por_dp"]) if r["tipo_termo"] == "continua" else (r["ic95_inf"], r["ic95_sup"])
        linhas.append([ROTULO_BLOCO[r["bloco"]].split(" (")[0], str(r["descricao_termo"]),
                       "+1 DP" + (f" (DP = {_n(r['dp_termo'], 3, sinal=False)})" if np.isfinite(r["dp_termo"]) else "")
                       if r["tipo_termo"] == "continua" else "atributo vs. referência",
                       v, ic, _n(r["p_valor"], 3, sinal=False), "sim" if _exclui_zero(lo, hi) else "não"])
    m = sub.iloc[0]
    rod = (f"\n\nAmostra: {_i(m['n_obs'])} linhas ({_i(m['n_eventos'])} com outcome = 1), {_i(m['n_clusters'])} "
           f"municípios (clusters); {_i(m['n_descartadas'])} linhas fora (motivos na coluna `nota` do CSV). Média do "
           f"outcome: {_n(m['media_outcome'], 1, pp=True, sinal=False)} %.")
    return _tab(["Grupo", "Característica", "Variação", "Efeito marginal médio", "IC 95%", "p", "IC exclui zero"],
                linhas) + rod


def tabela_blocos(est: pd.DataFrame) -> str:
    grupos = [("Pedido (E1, célula)", {"etapa": "E1", "variante": "principal"}),
              ("Priorização (E2, célula pedida)", {"etapa": "E2", "variante": "principal"}),
              ("Presença (E1, município)", {"etapa": "E1", "variante": "presenca_municipio"}),
              ("Pedido, todos os cursos (sensibilidade)", {"etapa": "E1", "variante": "sensibilidade_todos_os_cursos"}),
              ("Priorização, todos os cursos (sensibilidade)", {"etapa": "E2", "variante": "sensibilidade_todos_os_cursos"})]
    linhas = []
    for nome, f in grupos:
        sub = _sel(est, especificacao="T5.1c", **f)
        bl = sub[sub["tipo_termo"] == "bloco"].set_index("bloco")
        ref = sub[sub["tipo_termo"] == "referencia"]
        r2 = bl["pseudo_r2"].iloc[0] if len(bl) else np.nan
        cel = [nome, _n(r2, 3, sinal=False), _n(ref["pseudo_r2"].iloc[0], 3, sinal=False) if len(ref) else "—"]
        for b in BLOCOS:
            cel.append(_n(bl.at[b, "contribuicao_bloco"], 3, sinal=False) if b in bl.index else "não se aplica")
        linhas.append(cel)
    return _tab(["Modelo", "Pseudo-R² completo", "Só efeito fixo (ou constante)"]
                + [ROTULO_BLOCO[b].split(" (")[0] for b in BLOCOS], linhas)


def tabela_t52(est: pd.DataFrame) -> str:
    sub = est[est["especificacao"].isin(["T5.2a", "T5.2b"])]
    linhas = []
    for r in sub.to_dict("records"):
        linhas.append([r["especificacao"], r["unidade_analise"], str(r["outcome"]),
                       str(r["corte"]).replace(".", ","), _i(r["n_obs"]), f"{_i(r['n_abaixo'])} / {_i(r['n_acima'])}",
                       _n(r["estimativa"], 1, pp=True) + " p.p.",
                       f"[{_n(r['ic95_inf'], 1, pp=True)}; {_n(r['ic95_sup'], 1, pp=True)}]",
                       _n(r["p_valor"], 3, sinal=False), _n(r["q_bky"], 3, sinal=False),
                       _n(r["media_outcome"], 1, pp=True, sinal=False) + " %",
                       "sim" if r["no_protocolo"] else "não (leitura alternativa)"])
    return _tab(["Esp.", "Unidade", "Outcome", "Corte", "Linhas na janela", "Municípios abaixo / acima", "Salto",
                 "IC 95%", "p", "q BKY", "Média abaixo", "No protocolo"], linhas)


def tabela_t53(est: pd.DataFrame) -> str:
    linhas = []
    for k in CICLOS_QUADRO:
        for pref in ("n_celulas", "vagas"):
            sub = _sel(est, especificacao="T5.3", outcome=f"{pref}_c{k}")
            sub = sub[sub["tipo_termo"].isin(["continua", "binaria", "nivel"])]
            for r in sub.to_dict("records"):
                cont = r["tipo_termo"] == "continua"
                v = r["estimativa_por_dp"] if cont else r["estimativa"]
                lo = r["ic95_inf_por_dp"] if cont else r["ic95_inf"]
                hi = r["ic95_sup_por_dp"] if cont else r["ic95_sup"]
                linhas.append([str(k), "células" if pref == "n_celulas" else "vagas", str(r["descricao_termo"]),
                               "+1 DP" if cont else "atributo vs. referência", _n(v, 2, sinal=False),
                               f"[{_n(lo, 2, sinal=False)}; {_n(hi, 2, sinal=False)}]", _n(r["p_valor"], 3, sinal=False),
                               "sim" if _exclui_zero(lo, hi, 1.0) else "não"])
    mods = est[(est["especificacao"] == "T5.3") & (est["tipo_termo"] == "modelo")]
    rod = "\n\n" + _tab(["Ciclo", "Outcome", "Municípios", "Soma do outcome", "Pseudo-R² (deviance)", "Linhas fora"],
                        [[str(r["ciclo"]), str(r["outcome"]), _i(r["n_obs"]), _i(r["n_eventos"]),
                          _n(r["pseudo_r2"], 3, sinal=False), _i(r["n_descartadas"])] for r in mods.to_dict("records")])
    return _tab(["Ciclo", "Outcome", "Característica", "Variação", "Razão de taxas", "IC 95%", "p", "IC exclui 1"],
                linhas) + rod


def tabela_amostras(resumo: dict) -> str:
    ic = resumo["contagens"]["celulas"]
    g3 = resumo["contagens"]["g3"]
    mods = resumo["modelos"]
    linhas = [
        ["células do cardápio do ciclo 3", _i(ic["celulas_cardapio"])],
        ["municípios do cardápio", _i(ic["municipios_cardapio"])],
        ["municípios que constam do resultado da adesão", _i(ic["municipios_que_constam"])],
        ["células em municípios que constam (população do E1)", _i(ic["celulas_em_municipios_que_constam"])],
        ["células pedidas (população do E2)", _i(ic["celulas_pedidas"])],
        ["células pedidas e priorizadas", _i(ic["celulas_pedidas_priorizadas"])],
        ["linhas da adesão fora do cardápio (não entram)", _i(ic["linhas_adesao_fora_do_cardapio"])],
        ["células de cursos fora da ponte curso–CBO (cursos " + ", ".join(map(str, ic["cursos_fora_da_ponte"])) + ")",
         _i(ic["celulas_de_cursos_fora_da_ponte"])],
        ["municípios que constam sem célula do cardápio pedida", _i(g3["constam_sem_celula_do_cardapio_pedida"])],
    ]
    for chave, nome in (("T5.1a|E1|principal", "E1 (T5.1a), amostra estimada"),
                        ("T5.1b|E2|principal", "E2 (T5.1b), amostra estimada"),
                        ("T5.1a|E1|presenca_municipio", "presença (T5.1a, município), amostra estimada"),
                        ("T5.1a|E1|sensibilidade_todos_os_cursos", "E1, sensibilidade com todos os cursos"),
                        ("T5.1b|E2|sensibilidade_todos_os_cursos", "E2, sensibilidade com todos os cursos")):
        md = mods[chave]
        linhas.append([nome, f"{_i(md['n_obs'])} de {_i(md['n_entrada'])}"])
    return _tab(["Item", "Contagem"], linhas)


def _frase_ame(r: dict) -> str:
    v, ic = _ame_txt(r)
    quem = "o município" if r["unidade_analise"] == "municipio" else "a célula"
    alvo = "a característica sobe um desvio-padrão" if r["tipo_termo"] == "continua" else f"{quem} tem o atributo"
    return f"{r['descricao_termo']} (quando {alvo}: {v}, IC 95% {ic})"


def leitura(est: pd.DataFrame) -> str:
    """Leitura em linguagem simples, por regra fixa: só "associado a"; nenhuma afirmação causal."""
    partes = []
    for etapa, variante, nome in (("E1", "principal", "**Pedido do gestor (E1).**"),
                                  ("E2", "principal", "**Priorização da SGTES (E2).**"),
                                  ("E1", "presenca_municipio", "**Presença do município no resultado (E1).**")):
        sub = _sel(est, especificacao="T5.1c", etapa=etapa, variante=variante)
        termos = sub[sub["tipo_termo"].isin(["continua", "binaria", "nivel"])].to_dict("records")
        if not termos:
            partes.append(f"{nome} Sem estimativa.")
            continue
        def tam(r):
            return abs(r["estimativa_por_dp"] if r["tipo_termo"] == "continua" else r["estimativa"])
        def excl(r):
            lo, hi = (r["ic95_inf_por_dp"], r["ic95_sup_por_dp"]) if r["tipo_termo"] == "continua" else (r["ic95_inf"], r["ic95_sup"])
            return _exclui_zero(lo, hi)
        sig = sorted([r for r in termos if excl(r) and r["termo"] != "ivs"], key=tam, reverse=True)
        mais = [r for r in sig if (r["estimativa"] > 0)][:4]
        menos = [r for r in sig if (r["estimativa"] < 0)][:4]
        txt = [nome]
        if mais:
            txt.append("Probabilidade maior associada a: " + "; ".join(_frase_ame(r) for r in mais) + ".")
        if menos:
            txt.append("Probabilidade menor associada a: " + "; ".join(_frase_ame(r) for r in menos) + ".")
        if not sig:
            txt.append("Fora o IVS, nenhuma característica tem IC 95% que exclua zero.")
        ivs = [r for r in termos if r["termo"] == "ivs"]
        if ivs:
            r = ivs[0]
            v, ic = _ame_txt(r)
            txt.append(("O IVS contínuo, mantidas as demais características, está associado a uma variação de "
                        f"{v} por desvio-padrão (IC 95% {ic})" if excl(r) else
                        f"O IVS contínuo, mantidas as demais características, não se distingue de zero ({v} por "
                        f"desvio-padrão, IC 95% {ic})") + ".")
        bl = sub[sub["tipo_termo"] == "bloco"]
        bl = bl[bl["bloco"].isin(BLOCOS)]
        if len(bl):
            top = bl.sort_values("contribuicao_bloco", ascending=False).iloc[0]
            txt.append(f"O grupo que mais separa os casos é {ROTULO_BLOCO[top['bloco']]} (queda do pseudo-R² de "
                       f"{_n(top['contribuicao_bloco'], 3, sinal=False)} sem ele, num pseudo-R² completo de "
                       f"{_n(top['pseudo_r2'], 3, sinal=False)}).")
        partes.append(" ".join(txt))
    # T5.2
    t = []
    for un, oid, nome in (("municipio", "E1_frac_pedidas", "fração de células pedidas (município)"),
                          ("municipio", "E2_frac_priorizadas", "fração de pedidas priorizadas (município)"),
                          ("celula", "E1_pedida", "célula pedida"), ("celula", "E2_priorizada", "célula pedida priorizada"),
                          ("municipio", "E1_presenca", "presença do município no resultado")):
        s = _sel(est, especificacao="T5.2a", unidade_analise=un, outcome=oid, corte=EMPILHADO)
        if len(s) != 1:
            continue
        r = s.iloc[0]
        ex = _exclui_zero(r["ic95_inf"], r["ic95_sup"])
        if not ex:
            fim = ", que os dados não distinguem de zero"
        elif not (np.isfinite(r["q_bky"]) and r["q_bky"] < 0.05):
            fim = ": o IC 95% exclui zero, mas a linha não passa no BKY entre as linhas do T5.2 (q ≥ 0,05)"
        else:
            fim = ": o IC 95% exclui zero e a linha passa no BKY (q < 0,05)"
        t.append(f"{nome}: salto de {_n(r['estimativa'], 1, pp=True)} p.p. (IC 95% [{_n(r['ic95_inf'], 1, pp=True)}; "
                 f"{_n(r['ic95_sup'], 1, pp=True)}], q BKY {_n(r['q_bky'], 3, sinal=False)})" + fim)
    if t:
        partes.append("**Nos cortes (T5.2a, cortes empilhados, h = 0,050).** " + "; ".join(t) + ". Cada salto mede o "
                      "pacote do corte (bolsa anunciada +R$ 5 mil e outras regras federais nos mesmos cortes), não a "
                      "bolsa sozinha nem efeito da participação no PMM-E; IC que contém zero é falta de evidência com a "
                      "precisão relatada, não prova de ausência.")
    # T5.3
    t = []
    for k in CICLOS_QUADRO:
        for pref, nome in (("n_celulas", "células"), ("vagas", "vagas")):
            s = _sel(est, especificacao="T5.3", outcome=f"{pref}_c{k}", termo="ivs")
            if len(s) != 1:
                continue
            r = s.iloc[0]
            ex = _exclui_zero(r["ic95_inf_por_dp"], r["ic95_sup_por_dp"], 1.0)
            t.append(f"ciclo {k}, {nome}: razão de taxas de {_n(r['estimativa_por_dp'], 2, sinal=False)} por "
                     f"desvio-padrão do IVS (IC 95% [{_n(r['ic95_inf_por_dp'], 2, sinal=False)}; "
                     f"{_n(r['ic95_sup_por_dp'], 2, sinal=False)}])" + ("" if ex else ", não distinguível de 1"))
    if t:
        partes.append("**Quadro dos ciclos 1 e 2 (T5.3).** Mantidas as demais características municipais, o IVS "
                      "contínuo está associado a: " + "; ".join(t) + ". As demais razões estão na tabela da seção 7.")
    partes.append("Tudo acima é descritivo: diz com o que a abertura anda junto, não por que o Ministério decide. O "
                  "critério oficial de priorização não é publicado.")
    return "\n\n".join(partes)


def tabela_figuras(resumo: dict) -> str:
    linhas = [[f"`{Path(f['arquivo']).name}`", f.get("descricao", "")] for f in resumo["saidas"]["figuras"]]
    return _tab(["Arquivo (em `output/rdd_bolsa/P5_figuras/`)", "O que mostra"], linhas)


def tabela_desvios(resumo: dict) -> str:
    return "\n".join(f"{i}. **{d['item']}.** {d['situacao']} *Resolução:* {d['resolucao']}"
                     for i, d in enumerate(resumo["desvios"], 1))


def gerar_tabelas_doc(est: pd.DataFrame, resumo: dict) -> dict[str, str]:
    return {
        "amostras": tabela_amostras(resumo),
        "leitura": leitura(est),
        "ame_e1": tabela_ame(est, etapa="E1", variante="principal"),
        "ame_e2": tabela_ame(est, etapa="E2", variante="principal"),
        "ame_presenca": tabela_ame(est, etapa="E1", variante="presenca_municipio"),
        "ame_sensibilidade_e1": tabela_ame(est, etapa="E1", variante="sensibilidade_todos_os_cursos"),
        "ame_sensibilidade_e2": tabela_ame(est, etapa="E2", variante="sensibilidade_todos_os_cursos"),
        "blocos": tabela_blocos(est),
        "t52": tabela_t52(est),
        "t53": tabela_t53(est),
        "figuras": tabela_figuras(resumo),
        "desvios": tabela_desvios(resumo),
    }


def ler_saidas() -> tuple[pd.DataFrame, dict]:
    est = pd.read_csv(OUT / NOME_EST, dtype={"corte": str, "ciclo": str})
    resumo = json.loads((OUT / NOME_RESUMO).read_text(encoding="utf-8"))
    return est, resumo


def atualizar_doc() -> None:
    texto = DOC.read_text(encoding="utf-8")
    if not tabelas_no_doc(texto):
        raise FalhaValidacao(f"{rotulo(DOC)} sem marcadores <!-- P5:... -->")
    est, resumo = ler_saidas()
    DOC.write_text(aplicar_tabelas_doc(texto, gerar_tabelas_doc(est, resumo)), encoding="utf-8")
    print(f"blocos P5 do doc 57e regravados: {rotulo(DOC)}")


# ---------------------------------------------------------------------------
# Execução
# ---------------------------------------------------------------------------

DESCRICAO_FIGURAS = {
    "P5_T51_efeitos_marginais.png": "efeitos marginais médios do pedido (E1) e da priorização (E2), T5.1c",
    "P5_T51_contribuicao_blocos.png": "queda do pseudo-R² sem cada grupo de características (pedido, priorização, presença), T5.1c",
    "P5_T52_rdd_municipio_empilhado.png": "RDD por município, fração pedida e fração priorizada, cortes empilhados, T5.2a",
    "P5_T52_rdd_celula_empilhado.png": "RDD por célula com efeito fixo de curso, pedida e priorizada, cortes empilhados, T5.2a",
    "P5_T53_razao_taxas.png": "razões de taxas do Poisson do quadro dos ciclos 1 e 2, T5.3",
}

DECISOES = [
    "E1: outcome = a celula do cardapio tem linha no resultado final da adesao (aba principal); populacao = celulas "
    "do cardapio de municipios que constam do resultado (qualquer linha). Municipio que nao consta: pedido ausente, "
    "nunca zero (doc 41a, §5). Linhas da adesao com celula fora do cardapio nao entram (nao ha atributo do cardapio "
    "para elas) e sao contadas.",
    "E2: outcome = priorizadas > 0 na linha da adesao; populacao = celulas do cardapio com linha na adesao. A regra "
    "tudo ou nada e conferida (falha fechada).",
    "Presenca (linha separada do §1): logit no nivel do municipio (G3), com as covariaveis municipais.",
    "Estabelecimento: tipo, gestao e natureza juridica do cardapio, categoricas com referencia fixa (hospital geral, "
    "municipal, publico). Nenhuma categoria e agregada.",
    "Municipio: log da populacao do Censo 2022; nivel do REGIC 2018 (1o digito de 'Hierarquia - grupo', referencia "
    "centro local); capital de UF (flag_capital da tipologia A2); macrorregiao pelo 1o digito do IBGE (referencia "
    "Sudeste); polo = maior populacao do Censo 2022 na regiao de saude da tabela do TabNet.",
    "Capacidade pre: media mensal de n_vinculos do painel do a09 de 202406 a 202506 (13 competencias); CBO do curso "
    "pela ponte curso-CBO do a09 (soma das CBO elegiveis do curso); todos os medicos = grupo todos_medicos; por 10 mil "
    "habitantes do Censo 2022. Nos modelos municipais (presenca, T5.3 e T5.2 por municipio) a capacidade do curso "
    "vira a do conjunto alvo_pmme (uniao das CBO dos cursos), porque o municipio nao tem curso.",
    "Producao pre: media mensal (202406-202506) da quantidade aprovada no SIA (a12), conjuntos alvo_pmme e "
    "todos_profissionais, somada sobre os subgrupos, por 10 mil habitantes; municipio de atendimento.",
    "Escassez regional: vinculos das CBO do curso (ou do conjunto alvo, nos modelos municipais) por 10 mil habitantes "
    "na regiao de saude, somando numerador e populacao so entre os municipios da regiao presentes no painel CNES.",
    "Separacao: nivel de categorica, binaria ou efeito fixo em que o outcome nao varia sai da amostra (e contado na "
    "nota); colunas colineares saem na ordem do desenho. A amostra do modelo completo e a mesma de todos os modelos "
    "sem bloco (T5.1c).",
    "Efeitos marginais medios: continua = derivada media (relatada tambem por desvio-padrao da amostra); dummy = "
    "diferenca media de probabilidade com o atributo e sem ele (demais niveis do mesmo fator em zero); EP pelo metodo "
    "delta com a variancia CR1 por municipio.",
    "T5.2: rdd_lib.rd_empilhado em todos os casos (um corte = um grupo; empilhado = intercepto e inclinacoes por "
    "corte, salto comum); celula: efeito fixo de curso e CR1 por municipio; municipio: HC1 num corte, CR1 empilhado. "
    "A fracao priorizada do protocolo e lida sobre as celulas pedidas (unidade do E2, §1); sobre o cardapio, como "
    "leitura alternativa fora do BKY. T5.2b: as mesmas covariaveis do §2, sem o IVS, lineares e comuns aos dois lados.",
    "BKY (§4): q-valores de Benjamini-Krieger-Yekutieli entre todas as linhas T5.2a e T5.2b do protocolo (cortes "
    "separados e empilhados, celula e municipio); as leituras alternativas ficam fora.",
    "T5.3: Poisson por ciclo (1 e 2) do numero de celulas e do numero de vagas (imediatas + cadastro reserva) do "
    "quadro da 1a chamada em U, com zero fora do quadro; mesmas covariaveis municipais, IVS continuo; razao de taxas "
    "por desvio-padrao. A contribuicao por bloco no T5.3 e complementar (rotulada).",
    "Sem teste multiplo nas linhas descritivas (T5.1 e T5.3), como manda o §4.",
]


def montar_desvios(dados: dict) -> list[dict]:
    ic = dados["info"]["celulas"]
    im = dados["info"]["municipios"]
    cursos = ", ".join(map(str, ic["cursos_fora_da_ponte"]))
    return [
        {"data": DATA_EXECUCAO, "item": "Cursos do ciclo 3 fora da ponte curso–CBO",
         "situacao": f"A ponte do a09 cobre os cursos da grade dos ciclos 1 e 2; o cardápio do ciclo 3 tem também os "
                     f"cursos {cursos}, sem CBO na ponte, e o protocolo manda usar a ponte do a09 para a capacidade "
                     "do curso.",
         "resolucao": "Vínculos do curso e escassez regional do curso ficam ausentes nessas células (nada imputado). A "
                      "especificação principal é de casos completos e as deixa de fora (contadas). Uma sensibilidade "
                      "rotulada fora do protocolo usa a capacidade e a escassez do conjunto alvo em todos os cursos."},
        {"data": DATA_EXECUCAO, "item": "Covariáveis do curso nos modelos municipais",
         "situacao": "A presença (§1), o T5.2 por município e o T5.3 são no nível do município, que não tem curso.",
         "resolucao": "Capacidade e escassez do curso trocadas pelas do conjunto alvo_pmme (união das CBO dos cursos "
                      "da ponte); registrado nas decisões."},
        {"data": DATA_EXECUCAO, "item": "Fração priorizada no T5.2",
         "situacao": "O §3 diz 'fração de células pedidas e da priorizada' sem dizer o denominador da priorizada.",
         "resolucao": "Principal sobre as células pedidas (a unidade do E2 no §1); sobre o cardápio, como leitura "
                      "alternativa rotulada e fora do BKY."},
        {"data": DATA_EXECUCAO, "item": "Municípios sem região de saúde ou sem IVS",
         "situacao": f"Sem região de saúde na tabela do TabNet: {', '.join(im['municipios_sem_cir']) or 'nenhum'}; "
                     f"sem IVS 2010 oficial (criados depois de 2010): "
                     f"{', '.join(im['municipios_sem_ivs_oficial']) or 'nenhum'}.",
         "resolucao": "Polo e escassez regional (ou IVS) ausentes; o município e as suas células saem dos modelos que "
                      "usam a covariável e são contados; nada imputado."},
        {"data": DATA_EXECUCAO, "item": "Local do resultado",
         "situacao": "O §5 do protocolo diz 'doc 57, seção P5'; o doc 57 é a síntese da onda 5 (doc 51, §5).",
         "resolucao": "Resultados em docs/06_execucao/57e_resultados_P5_abertura.md, para entrar na síntese 57."},
    ]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--atualizar-doc", action="store_true", help="so regrava os blocos P5 do doc 57e a partir das saidas")
    args = ap.parse_args(argv)
    if args.atualizar_doc:
        atualizar_doc()
        return 0
    dados = carregar()
    est, modelos = estimar_tudo(dados)
    nucleo = ["estimativa", "ep", "ic95_inf", "ic95_sup", "p_valor"]
    sem_nota = est[est[nucleo].isna().any(axis=1) & (est["nota"].fillna("") == "")]
    if len(sem_nota):
        raise FalhaValidacao(f"{len(sem_nota)} linhas com NaN sem nota")
    if not ((est["natureza_dos_dados"] == NATUREZA).all() and (est["estatuto"] == ESTATUTO).all()):
        raise FalhaValidacao("linha sem rotulo de natureza ou estatuto")
    OUT.mkdir(parents=True, exist_ok=True)
    est.to_csv(OUT / NOME_EST, index=False)
    est = pd.read_csv(OUT / NOME_EST, dtype={"corte": str, "ciclo": str})
    figs = gerar_figuras(est, dados, OUT / DIR_FIG)
    for fg in figs:
        fg["descricao"] = DESCRICAO_FIGURAS[Path(fg["arquivo"]).name]
        for p in fg.get("paineis", []):
            s = _sel(est, especificacao=p["especificacao"], unidade_analise=p["unidade_analise"], outcome=p["outcome"],
                     corte=p["corte"])
            if len(s) != 1 or abs(float(s.iloc[0]["estimativa"]) - p["tau"]) > 1e-10:
                raise FalhaValidacao(f"titulo da figura {fg['arquivo']} nao bate com o CSV")
        fg["sha256"] = sha256(ROOT / fg["arquivo"])
    info = dados["info"]
    entradas = [
        E6.bloco_entrada(PROTOCOLO_MD, "protocolo 55 (somente lido)", "pipeline do repositorio", "2026-10-19",
                         "§1-§6", "documento", "-", "-"),
        E6.bloco_entrada(A08, "IVS 2010 oficial: running variable e covariavel continua",
                         "Ipea, Atlas da Vulnerabilidade Social (a08)", "Censo 2010", f"{len(dados['rv'])} municipios",
                         "municipio", "co_ibge", "nenhum"),
        E6.bloco_entrada(CARDAPIO, "cardapio de gestores do ciclo 3 (celulas e atributos do estabelecimento)",
                         "SGTES/MS, quadro de vagas dos gestores (somente lido)", "ciclo 3",
                         f"{info['celulas']['celulas_cardapio']} celulas", "celula CNES x curso",
                         "co_cnes_7d, cod_curso", "nenhum"),
        E6.bloco_entrada(ADESAO, "resultado final da adesao dos gestores do ciclo 3 (E1 e E2)",
                         "SGTES/MS (somente lido)", "ciclo 3", f"{info['celulas']['linhas_adesao']} linhas",
                         "celula CNES x curso", "co_cnes_7d, cod_curso", "aba RESULTADO FINAL"),
        E6.bloco_entrada(ARQ_G3, "conferencia de consta e celulas do cardapio (somente lido)", "tarefa B (12)",
                         "ver dicionario", f"{info['g3']['municipios']} municipios", "municipio", "co_ibge", "nenhum"),
        E6.bloco_entrada(ARQ_U, "T5.3: celulas e vagas do quadro dos ciclos 1 e 2 (zero fora do quadro)", "tarefa B (12)",
                         "ver dicionario", f"{info['u']['municipios']} municipios", "municipio", "co_ibge",
                         "colunas n_celulas_c1-2, vagas_imediatas_c1-2, vagas_cr_c1-2"),
        E6.bloco_entrada(ARQ_POP, "populacao do Censo 2022 (log, denominador por 10 mil, polo)", "IBGE, Censo 2022 (a06)",
                         "2022", "municipios", "municipio", "co_ibge_6d", "nenhum"),
        E6.bloco_entrada(ARQ_CNES, "capacidade pre e escassez regional", "CNES nacional (a09)",
                         f"{COMP_PRE[0]}-{COMP_PRE[1]}", f"{info['cnes_pre']['n_competencias']} competencias",
                         "municipio x grupo de CBO x mes", "co_ibge, competencia, grupo",
                         f"competencia entre {COMP_PRE[0]} e {COMP_PRE[1]} (filtro na leitura); grupos alvo_pmme, "
                         "todos_medicos e cbo_* da ponte"),
        E6.bloco_entrada(ARQ_SIA, "producao pre", "SIA/SUS no TabNet (a12)", f"{COMP_PRE[0]}-{COMP_PRE[1]}",
                         f"{info['sia_pre']['n_competencias']} competencias", "municipio x mes x subgrupo x conjunto",
                         "co_ibge, competencia_processamento, subgrupo, conjunto_cbo",
                         f"competencia_processamento entre {COMP_PRE[0]} e {COMP_PRE[1]} (filtro na leitura); "
                         "conjuntos alvo_pmme e todos_profissionais"),
        E6.bloco_entrada(SIA_SUBG, "subgrupos presentes por consulta do SIA (conferencia de linhas)", "a12",
                         f"{COMP_PRE[0]}-{COMP_PRE[1]}", "consultas", "consulta x subgrupo", "competencia, conjunto",
                         "so a janela pre"),
        E6.bloco_entrada(SIA_MUN, "municipios da lista do TabNet do SIA", "a12", "2026-10-19", "municipios",
                         "municipio", "co_ibge", "nenhum"),
        E6.bloco_entrada(PONTE, "ponte curso-CBO do a09", "repositorio (aquisicao/01)", "congelada",
                         f"{len(dados['ponte'])} cursos", "curso", "cod_curso", "cbos_elegiveis"),
        E6.bloco_entrada(REGIC_XLSX, "hierarquia urbana", "IBGE, REGIC 2018 (bruto, somente lido)", "2018",
                         f"{info['regic']['municipios']} municipios", "municipio", "codmun", "aba 'Hierarquia e regiao'"),
        E6.bloco_entrada(CIR_CNV, "regiao de saude (CIR) e polo", "DATASUS/TabNet br_regsaud.cnv (bruto, somente lido)",
                         "versao corrente na data do download (ver X5_manifesto_regioes_saude_cir.json)",
                         f"{info['cir']['codigos']} codigos", "municipio", "co_ibge", "linhas 'Ignorado' fora"),
        E6.bloco_entrada(TIPOLOGIA, "capital de UF (flag_capital)", "tipologia territorial A2 (03)", "2022",
                         f"{info['municipios']['capitais_na_tipologia']} capitais", "municipio", "co_ibge_6d",
                         "so a coluna flag_capital"),
    ]
    q = {"linhas": int(len(est)), "por_especificacao": est["especificacao"].value_counts().sort_index().to_dict(),
         "executado": int((est["status"] == "EXECUTADO").sum()),
         "sem_estimativa": int((est["status"] == "SEM_ESTIMATIVA").sum()),
         "nao_executado": int((est["status"] == "NAO_EXECUTADO").sum()),
         "linhas_bky": int(est["entra_bky"].astype(bool).sum()),
         "celulas": info["celulas"], "g3": info["g3"], "u": info["u"]}
    resumo = {
        "etapa": "P5_determinantes_abertura",
        "natureza_dos_dados": NATUREZA,
        "estatuto": ESTATUTO,
        "data_execucao": DATA_EXECUCAO,
        "script": rotulo(Path(__file__)),
        "protocolo": {"arquivo": rotulo(PROTOCOLO_MD), "sha256": sha256(PROTOCOLO_MD)},
        "leitura": "T5.1 e T5.3 descritivos ('associado a'); T5.2 mede o pacote do corte; o criterio oficial de "
                   "priorizacao nao e publicado (auditoria 01; doc 51, §1)",
        "contraste_t52": CONTRASTE,
        "salto": "tau = lado com bolsa maior (s > c) menos lado com bolsa menor; o corte pertence ao lado inferior",
        "entradas": entradas,
        "cnes_pre": info["cnes_pre"],
        "sia_pre": info["sia_pre"],
        "territorio": {"regic": info["regic"], "cir": info["cir"], "municipios": info["municipios"]},
        "adesao_diagnostico": dados["adesao_diag"],
        "covariaveis": {"celula": [c["col"] for c in COVS_CELULA], "celula_sensibilidade": [c["col"] for c in COVS_CELULA_SENS],
                        "municipio": [c["col"] for c in COVS_MUN], "t52b_celula": [c["col"] for c in COVS_CCFT_CELULA],
                        "t52b_municipio": [c["col"] for c in COVS_CCFT_MUN],
                        "descricao": {c["col"]: c["desc"] for c in COVS_CELULA + COVS_MUN}},
        "modelos": modelos,
        "decisoes": DECISOES,
        "desvios": montar_desvios(dados),
        "contagens": q,
        "validacoes": {"cardapio_igual_script_12": True, "g3_igual_outcomes_G3": True, "ivs_de_U_igual_a08": True,
                       "tudo_ou_nada": True, "linhas_com_nan_sem_nota": 0, "figuras_iguais_ao_csv": True},
        "saidas": {NOME_EST: {"arquivo": rotulo(OUT / NOME_EST), "sha256": sha256(OUT / NOME_EST)}, "figuras": figs},
        "integridade": "nada imputado; ausente nao vira zero; CNES so 202406-202506 (nenhuma competencia >= 202609); "
                       "SIA so 202406-202506; o arquivo local de IVS da auditoria 16 nao e lido",
    }
    T23._gravar_json(OUT / NOME_RESUMO, resumo)
    atualizar_doc()
    vis = est[(est["especificacao"].isin(["T5.2a"])) & (est["corte"] == EMPILHADO)]
    print(vis[["unidade_analise", "outcome", "estimativa", "ic95_inf", "ic95_sup", "p_valor", "q_bky"]].to_string())
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except FalhaValidacao as erro:
        print(f"FALHA DE VALIDACAO: {erro}", file=sys.stderr)
        sys.exit(2)
