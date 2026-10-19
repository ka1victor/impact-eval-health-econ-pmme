"""E9 do protocolo multi-outcome da bolsa: escolha revelada dos candidatos do PMM-E.

Protocolo congelado: `docs/06_execucao/40_protocolo_multioutcome_rdd_bolsa.md`,
§12 (E9), §13 (políticas nos mesmos cortes), §14 (conjunto de escolha) e §15
(forma funcional), e `output/rdd_bolsa/protocolo_E6_multioutcome.json`.
Insumos construídos pela tarefa B (`docs/06_execucao/41a_construcao_outcomes_funil.md`).

Modelo
------
Logit condicional (McFadden, 1974) da 1a opção de cada candidato entre as
células (CNES × curso) do seu curso e ciclo no quadro da 1a chamada. A utilidade
da célula j é

    V_j = beta * bolsa_j + f(IVS_j) + gamma' z_j,

- `bolsa_j`: bolsa mensal anunciada em R$ mil, lida da faixa impressa no quadro
  (Faixa 3 = 10, Faixa 2 = 15, Faixa 1 = 20). O mapa faixa → valor vem das
  grades dos editais já extraídas em `output/aquisicao/a03_matriz_regra_tratamento.json`
  (grades de 2025 e de 2026) e `output/aquisicao/a04_grade_anunciada_2025.csv`;
  o script para se as fontes divergirem. Também para se a faixa impressa não
  reproduzir a regra de dois cortes sobre o IVS 2010 oficial (portão R1:
  T = 1[s > c], o corte pertence ao lado inferior).
- `f(IVS)`: spline contínuo com nós em 0,300 e 0,400 (§15): inclinações livres
  por faixa e nenhum salto de nível. Base linear: (s − 0,3), (s − 0,3)+ e
  (s − 0,4)+, em unidades de 0,1 de IVS. Variante quadrática: acrescenta os
  quadrados dos três termos, também contínuos nos nós. Como f é contínua, a
  bolsa só é identificada pelos degraus em 0,300 e 0,400.
- `z_j`: tem_vaga_imediata, log(vagas imediatas + 1), log da população do Censo
  2022, macrorregião (base SUDESTE) e estrato territorial A2 (base capital).

Especificações (todas fixadas no protocolo e todas relatadas):
- conjunto principal (§14: todas as células do curso e ciclo) e de
  sensibilidade (só células com vaga imediata e candidatos cuja 1a opção está
  nelas; aí tem_vaga_imediata é constante e sai do modelo);
- spline linear (principal) e quadrático (variante);
- bolsa linear (principal) e um indicador de degrau por corte (sensibilidade,
  com teste de Wald da igualdade dos dois degraus);
- logit explodido (ranking 1a > 2a opção) no conjunto principal. O conjunto do
  posto 2 é o do curso da 2a opção, sem a célula da 1a opção quando os cursos
  coincidem (dicionário da tarefa B, `id_conjunto_escolha`);
- ciclos 1, 2 e 3 separados e empilhados (verossimilhança conjunta, mesmos
  coeficientes; os conjuntos de cada ciclo já são grupos distintos).

Inferência: EP de máxima verossimilhança (inversa da informação), sanduíche com
cluster por conjunto de escolha (curso × ciclo; principal, §15) e por
candidato, ambos com fator G/(G − 1). IC 95% e p pela normal com o EP de
cluster por conjunto; também o p pela t com G − 1 graus de liberdade, porque há
poucos conjuntos (16 a 24 por ciclo). Efeito sobre a probabilidade: para cada
candidato e cada célula do seu conjunto, a probabilidade é recalculada com a
bolsa daquela célula R$ 5 mil maior e o resto fixo; a média das diferenças é o
efeito. IC pelo método delta (gradiente numérico central), com a matriz de
cluster por conjunto.

Estimando: efeito da bolsa anunciada sobre a ESCOLHA entre vagas (realocação
entre municípios), não sobre o total de candidatos. Sem residência do
candidato, a distância não entra. Nas outras políticas nos mesmos cortes (§13,
auditoria 18), nenhum ato arquivado paga o especialista do PMM-E por faixa,
mas o +20% de teto da MAC em IVS > 0,3 pode mudar a estrutura do serviço (o
degrau em 0,300 pode carregar isso), e fica sem verificação se a ajuda de
custo do PMMB, que muda em 0,400, alcança o participante do PMM-E.

Integridade: só lê `output/`; nenhum dado é simulado, imputado ou preenchido.
Alternativa sem IVS oficial é retirada do conjunto e contada; candidato cuja
escolha não está no conjunto faz o script parar. As únicas constantes são
parâmetros do protocolo (cortes, passo de R$ 5 mil) e de parametrização
(escala do spline, categorias de base, tolerâncias numéricas).
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]

PROTOCOLO_JSON = ROOT / "output" / "rdd_bolsa" / "protocolo_E6_multioutcome.json"
PROTOCOLO_MD = ROOT / "docs" / "06_execucao" / "40_protocolo_multioutcome_rdd_bolsa.md"
DIR_OUTCOMES = ROOT / "output" / "rdd_bolsa" / "outcomes"
DICIONARIO = DIR_OUTCOMES / "dicionario_outcomes_funil.json"
ESCOLHAS = DIR_OUTCOMES / "escolhas_candidatos.parquet"
CONJ_PRINCIPAL = DIR_OUTCOMES / "escolhas_conjunto_principal.parquet"
CONJ_SENSIBILIDADE = DIR_OUTCOMES / "escolhas_conjunto_sensibilidade_vaga_imediata.parquet"
IVS_OFICIAL = ROOT / "output" / "aquisicao" / "a08_ivs_2010_oficial_municipio.csv"
GRADES_EDITAIS = ROOT / "output" / "aquisicao" / "a03_matriz_regra_tratamento.json"
GRADE_2025 = ROOT / "output" / "aquisicao" / "a04_grade_anunciada_2025.csv"
MANIFESTO_A11 = ROOT / "output" / "aquisicao" / "a11_manifesto_ciclo2_chamada1.json"
# Quadros da 1a chamada (os mesmos da tarefa B), lidos só para conferir que o código do curso tem o mesmo rótulo
# nos três ciclos (condição do cluster por curso da robustez pós-auditoria).
QUADROS_1A_CHAMADA = {1: ROOT / "data" / "raw" / "aquisicao" / "vagas" / "2025_ciclo1_chamada1_vagas.xlsx",
                      2: ROOT / "data" / "raw" / "pmm_e" / "2026_ciclo2_chamada1_vagas_retificadas.xlsx",
                      3: ROOT / "data" / "raw" / "pmm_e" / "2026_ciclo3_chamada1_vagas_retificadas.xlsx"}

OUT_DIR = ROOT / "output" / "rdd_bolsa"
OUT_ESTIMATIVAS = OUT_DIR / "E9_estimativas.csv"
OUT_EFEITOS = OUT_DIR / "E9_efeitos_marginais.csv"
OUT_RESUMO = OUT_DIR / "E9_resumo.json"
OUT_TABELAS = OUT_DIR / "E9_tabelas_relato.md"
OUT_ROBUSTEZ = OUT_DIR / "E9_robustez_pos_auditoria.csv"
OUT_FIG_DIR = OUT_DIR / "E9_figuras"
OUT_FIGURA = OUT_FIG_DIR / "E9_utilidade_ivs.png"

DATA_EXECUCAO = "2026-10-18"
NATUREZA = "EMPIRICO"

# Parâmetros do protocolo (§3, §15).
CORTES_MIL = (300, 400)
PASSO_BOLSA_MIL = 5.0  # +R$ 5 mil por degrau
# Parametrização (não muda o ajuste, só a escala dos coeficientes do spline).
ESCALA_IVS = 10.0  # termos do spline por 0,1 de IVS
CENTRO_IVS_MIL = 300
BASE_MACRO = "SUDESTE"
BASE_ESTRATO = "capital"
# Numérica.
TOL_PASSO = 1e-10
TOL_DECREMENTO = 1e-14
LIMITE_EP_SEPARACAO = 1e4  # EP de MV acima disso = termo divergente (separação); só gera nota
MAX_ITER = 200
Z95 = float(stats.norm.ppf(0.975))

CICLOS = ("1", "2", "3", "empilhado")
MODELO_COND = "logit_condicional_1a_opcao"
MODELO_EXPL = "logit_explodido_1a_2a_opcao"
ESPECIFICACOES = {
    # nome: (grau do spline, forma da bolsa)
    "spline_linear__bolsa_linear": (1, "linear"),
    "spline_quadratico__bolsa_linear": (2, "linear"),
    "spline_linear__degraus_por_corte": (1, "degraus"),
    "spline_quadratico__degraus_por_corte": (2, "degraus"),
}
# (modelo, conjunto) estimados; o explodido usa só o conjunto principal (§12 + §14).
COMBINACOES = ((MODELO_COND, "principal"), (MODELO_COND, "sensibilidade"), (MODELO_EXPL, "principal"))

# Robustez pós-auditoria (pós-resultado, fora do protocolo). Pedida pela auditoria independente do E9
# (commit 9646b57), depois de ver os resultados; nenhuma destas linhas substitui as do protocolo.
TAG_ROB = "ROBUSTEZ_POS_AUDITORIA"
PAPEL_ROB = ("robustez pós-auditoria: pós-resultado, fora do protocolo, pedida pela auditoria independente "
             "de 18/10/2026")
ESPEC_PRINCIPAL = "spline_linear__bolsa_linear"
SEMENTE_BOOT = 20261018
N_REAMOSTRAS = 199_999
G_MAX_ENUMERACAO = 24
PESOS_WEBB = np.array([-math.sqrt(1.5), -1.0, -math.sqrt(0.5), math.sqrt(0.5), 1.0, math.sqrt(1.5)])
JANELAS_MIL = (100, 50, 25)
NOS_EXTRAS_MIL = tuple(n for n in range(150, 701, 50) if n not in CORTES_MIL)
PLACEBOS_MIL = tuple(c for c in range(190, 511, 10) if all(abs(c - k) > 10 for k in CORTES_MIL))


def papel_no_protocolo(modelo: str, conjunto: str, espec: str) -> str:
    if espec.startswith(TAG_ROB):
        return PAPEL_ROB
    grau, forma = ESPECIFICACOES[espec]
    if modelo == MODELO_COND and conjunto == "principal" and grau == 1 and forma == "linear":
        return "principal (§14, §15)"
    partes = []
    if conjunto == "sensibilidade":
        partes.append("sensibilidade do conjunto (§12, §14)")
    if modelo == MODELO_EXPL:
        partes.append("sensibilidade 2a opção, logit explodido (§12)")
    if grau == 2:
        partes.append("variante quadrática do spline (§15)")
    if forma == "degraus":
        partes.append("sensibilidade degrau por corte (§15)")
    return "; ".join(partes)


# --------------------------------------------------------------------------
# Utilitários
# --------------------------------------------------------------------------

def sha256_arquivo(caminho: Path) -> str:
    h = hashlib.sha256()
    with caminho.open("rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def rel(caminho: Path) -> str:
    return str(caminho.resolve().relative_to(ROOT))


def fmt(x: float, casas: int = 3) -> str:
    """Número com vírgula decimal (padrão dos documentos do repositório)."""
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return "—"
    return f"{x:.{casas}f}".replace("-", "−").replace(".", ",")


def fmt_p(p: float) -> str:
    if p is None or not math.isfinite(p):
        return "—"
    if p < 0.001:
        return "< 0,001"
    return fmt(p, 3)


# --------------------------------------------------------------------------
# Insumos
# --------------------------------------------------------------------------

def mapa_bolsa_por_faixa() -> tuple[dict[str, float], dict[str, Any]]:
    """Faixa impressa → bolsa em R$ mil, das grades dos editais; para se as fontes divergem."""
    grades = json.loads(GRADES_EDITAIS.read_text(encoding="utf-8"))["mapeamento_regras_por_edital"]
    por_grade: dict[str, dict[str, float]] = {}
    rotulo_valor: dict[str, list[str]] = {}
    for nome, grade in grades.items():
        if not isinstance(grade, dict):
            continue
        m = {}
        for k, v in grade.items():
            if k.startswith("faixa_") and isinstance(v, dict):
                chave = "bolsa_mensal_anunciada" if "bolsa_mensal_anunciada" in v else "bolsa_mensal_liquida_anunciada"
                m[f"FAIXA {k.split('_')[1]}"] = float(v[chave]) / 1000.0
                rotulo_valor.setdefault(nome, [])
                if chave not in rotulo_valor[nome]:
                    rotulo_valor[nome].append(chave)
        por_grade[nome] = m
    g25 = pd.read_csv(GRADE_2025)
    por_grade["a04_grade_anunciada_2025"] = {
        f"FAIXA {int(r.faixa_atracao)}": float(r.valor_anunciado_mensal_brl) / 1000.0 for r in g25.itertuples()}
    mapas = list(por_grade.values())
    if len(mapas) < 3 or any(m != mapas[0] for m in mapas):
        raise AssertionError(f"grades de faixa → bolsa divergentes entre fontes: {por_grade}")
    mapa = mapas[0]
    if sorted(mapa) != ["FAIXA 1", "FAIXA 2", "FAIXA 3"]:
        raise AssertionError(f"faixas inesperadas: {mapa}")
    return mapa, {"mapa_faixa_para_bolsa_mil": mapa, "grades_conferidas": por_grade,
                  "conferencia": "as grades de 2025 e 2026 (a03) e a grade de 2025 da FAQ (a04) dão o mesmo valor por faixa",
                  "rotulo_do_valor_por_grade": rotulo_valor,
                  "nota_bruto_liquido": ("o valor de 2025 vem rotulado como 'anunciado' (sem 'líquido'; a FAQ e o edital "
                                         "3/2025 não dizem líquido) e o de 2026 como 'líquido anunciado'; a auditoria 01 "
                                         "(§6.1) registra que a retificação do edital 3/2025 esclareceu que os valores eram "
                                         "líquidos. Os números por faixa são iguais; a diferença de rótulo fica registrada "
                                         "e não muda a codificação")}


def rotulos_cursos() -> dict[str, Any]:
    """Rótulo de cada código de curso nos quadros da 1a chamada; para se um código mudar de rótulo entre ciclos."""
    import re
    import unicodedata

    def norm(x: object) -> str:
        t = unicodedata.normalize("NFKD", str(x)).encode("ascii", "ignore").decode().upper()
        return re.sub(r"\s+", " ", t).strip()

    por_codigo: dict[int, dict[int, str]] = {}
    for ciclo, caminho in QUADROS_1A_CHAMADA.items():
        bruto = pd.read_excel(caminho, sheet_name=0, header=None, dtype=str)
        pos = [(i, j) for i in range(min(10, len(bruto))) for j in range(bruto.shape[1])
               if norm(bruto.iat[i, j]) == "CURSO"]
        if len(pos) != 1:
            raise AssertionError(f"{rel(caminho)}: cabeçalho CURSO não localizado de forma única")
        i0, j0 = pos[0]
        for v in bruto.iloc[i0 + 1:, j0].dropna().unique():
            m = re.match(r"\s*(\d+)\s*[.\-–]\s*(.*)", str(v))
            if m:
                rot = norm(m.group(2))
                anterior = por_codigo.setdefault(int(m.group(1)), {}).get(ciclo)
                if anterior is not None and anterior != rot:
                    raise AssertionError(f"curso {m.group(1)} com dois rótulos no ciclo {ciclo}")
                por_codigo[int(m.group(1))][ciclo] = rot
    divergentes = {k: v for k, v in por_codigo.items() if len(set(v.values())) > 1}
    if divergentes:
        raise AssertionError(f"código de curso com rótulos diferentes entre ciclos: {divergentes}")
    return {"codigos": {str(k): {"ciclos": sorted(v), "rotulo": next(iter(v.values()))} for k, v in sorted(por_codigo.items())},
            "conferencia": "cada código de curso tem o mesmo rótulo (normalizado) em todos os ciclos em que aparece"}


def carregar_ivs() -> pd.Series:
    ivs = pd.read_csv(IVS_OFICIAL, dtype={"co_ibge": str}, usecols=["co_ibge", "ivs"])
    ivs["co_ibge"] = ivs["co_ibge"].str.zfill(6)
    if not ivs["co_ibge"].is_unique:
        raise AssertionError("a08: co_ibge repetido")
    return ivs.set_index("co_ibge")["ivs"].astype(float)


def faixa_pela_regra(s_mil: np.ndarray) -> np.ndarray:
    """Regra do portão R1: Faixa 3 até 0,300; Faixa 2 até 0,400; Faixa 1 acima (o corte fica embaixo)."""
    return np.where(s_mil > CORTES_MIL[1], "FAIXA 1", np.where(s_mil > CORTES_MIL[0], "FAIXA 2", "FAIXA 3"))


def preparar_conjunto(conj: pd.DataFrame, ivs: pd.Series, mapa: dict[str, float]) -> tuple[pd.DataFrame, dict]:
    """Junta IVS oficial e bolsa; retira (e conta) alternativas sem IVS; confere a faixa contra a regra."""
    c = conj.copy()
    if not (c["natureza_dos_dados"] == NATUREZA).all():
        raise AssertionError("conjunto de escolha com natureza diferente de EMPIRICO")
    c["ivs"] = c["co_ibge"].map(ivs)
    sem_ivs = c[c["ivs"].isna()]
    retiradas = [{"ciclo": int(r.ciclo), "id_conjunto_escolha": r.id_conjunto_escolha, "co_cnes_7d": r.co_cnes_7d,
                  "cod_curso": int(r.cod_curso), "co_ibge": r.co_ibge, "faixa_anunciada": r.faixa_anunciada,
                  "motivo": "município sem IVS 2010 oficial (criado depois de 2010); alternativa retirada do conjunto"}
                 for r in sem_ivs.itertuples()]
    c = c[c["ivs"].notna()].copy()
    c["s_mil"] = np.round(c["ivs"].to_numpy() * 1000.0)
    if c["faixa_anunciada"].isna().any() or not set(c["faixa_anunciada"]) <= set(mapa):
        raise AssertionError(f"faixa impressa fora do mapa: {sorted(set(c['faixa_anunciada'].dropna()))}")
    c["bolsa_mil"] = c["faixa_anunciada"].map(mapa).astype(float)
    regra = faixa_pela_regra(c["s_mil"].to_numpy())
    discord = int((regra != c["faixa_anunciada"].to_numpy()).sum())
    if discord:
        raise AssertionError(f"faixa impressa difere da regra de dois cortes do IVS oficial em {discord} células")
    for col in ("populacao_2022", "vagas_imediatas", "log_vagas_imediatas_mais_1", "tem_vaga_imediata",
                "macrorregiao", "estrato_territorial"):
        if c[col].isna().any():
            raise AssertionError(f"{col} ausente no conjunto de escolha (não é preenchido)")
    c = c.reset_index(drop=True)
    diag = {"alternativas_retiradas_sem_ivs": retiradas, "faixa_impressa_igual_regra_ivs": {
        "celulas": int(len(c)), "discordantes": discord}}
    return c, diag


def base_spline(s_mil: np.ndarray, grau: int, nos_extras_mil: tuple[int, ...] = ()) -> pd.DataFrame:
    """Spline contínuo em IVS com nós em 0,300 e 0,400 (unidades de 0,1 de IVS); sem salto de nível.

    Base de potências truncadas: grau 1 (principal), 2 (variante do §15) ou 3 (robustez pós-auditoria).
    `nos_extras_mil` acrescenta nós lineares (robustez pós-auditoria); todos os termos são contínuos.
    """
    s = np.asarray(s_mil, dtype=float)
    u = (s - CENTRO_IVS_MIL) / 1000.0 * ESCALA_IVS
    a = np.maximum(s - CORTES_MIL[0], 0.0) / 1000.0 * ESCALA_IVS
    b = np.maximum(s - CORTES_MIL[1], 0.0) / 1000.0 * ESCALA_IVS
    cols = {"ivs_inclinacao": u, "ivs_mudanca_inclinacao_0300": a, "ivs_mudanca_inclinacao_0400": b}
    if grau >= 2:
        cols.update({"ivs_quadrado": u ** 2, "ivs_quadrado_apos_0300": a ** 2, "ivs_quadrado_apos_0400": b ** 2})
    if grau >= 3:
        cols.update({"ivs_cubo": u ** 3, "ivs_cubo_apos_0300": a ** 3, "ivs_cubo_apos_0400": b ** 3})
    for n in nos_extras_mil:
        cols[f"ivs_mudanca_inclinacao_{int(n):04d}"] = np.maximum(s - n, 0.0) / 1000.0 * ESCALA_IVS
    return pd.DataFrame(cols, index=getattr(s_mil, "index", None))


def termos_bolsa(c: pd.DataFrame, forma: str) -> pd.DataFrame:
    if forma == "linear":
        return pd.DataFrame({"bolsa_mil": c["bolsa_mil"].to_numpy()}, index=c.index)
    # Degraus pela faixa impressa (= regra do IVS, conferida): Faixa 2 ou 1 passa 0,300; Faixa 1 passa 0,400.
    f = c["faixa_anunciada"]
    return pd.DataFrame({"degrau_0300": f.isin(["FAIXA 2", "FAIXA 1"]).astype(float).to_numpy(),
                         "degrau_0400": (f == "FAIXA 1").astype(float).to_numpy()}, index=c.index)


def matriz_atributos(c: pd.DataFrame, grau: int, forma: str, macros: list[str], estratos: list[str],
                     nos_extras_mil: tuple[int, ...] = (), placebo_mil: int | None = None) -> pd.DataFrame:
    X = pd.concat([termos_bolsa(c, forma), base_spline(c["s_mil"], grau, nos_extras_mil).set_index(c.index)], axis=1)
    if placebo_mil is not None:  # robustez pós-auditoria: degrau falso + nó no corte falso
        X["degrau_placebo"] = (c["s_mil"] > placebo_mil).astype(float).to_numpy()
        X["ivs_mudanca_inclinacao_placebo"] = np.maximum(c["s_mil"].to_numpy() - placebo_mil, 0.0) / 1000.0 * ESCALA_IVS
    X["tem_vaga_imediata"] = c["tem_vaga_imediata"].astype(float)
    X["log_vagas_imediatas_mais_1"] = c["log_vagas_imediatas_mais_1"].astype(float)
    X["log_populacao_2022"] = np.log(c["populacao_2022"].astype(float))
    for m in macros:
        if m != BASE_MACRO:
            X[f"macro_{m.lower().replace(' ', '_')}"] = (c["macrorregiao"] == m).astype(float)
    for e in estratos:
        if e != BASE_ESTRATO:
            X[f"estrato_{e}"] = (c["estrato_territorial"] == e).astype(float)
    return X


# --------------------------------------------------------------------------
# Grupos de escolha
# --------------------------------------------------------------------------

def montar_grupos(cand: pd.DataFrame, conj: pd.DataFrame, modelo: str, conjunto: str) -> tuple[pd.DataFrame, dict]:
    """Um grupo por candidato × posto. Colunas: idx_escolhida, idx_excluida (−1 se nenhuma), cluster_conjunto,
    cluster_candidato, posto. Para se uma escolha cair fora do conjunto."""
    pos = pd.Series(np.arange(len(conj)), index=pd.MultiIndex.from_frame(conj[["ciclo", "co_cnes_7d", "cod_curso"]]))
    cand = cand[cand["ciclo"].isin(conj["ciclo"].unique())]
    r1 = cand[cand["opcao_rank"] == 1].copy()
    r2 = cand[cand["opcao_rank"] == 2].copy()
    diag: dict[str, Any] = {}
    sem_1a = sorted(set(r2["id_candidato"]) - set(r1["id_candidato"]))
    diag["candidatos_sem_linha_de_1a_opcao_excluidos"] = len(sem_1a)
    if conjunto == "sensibilidade":
        fora = int((r1["celula_com_vaga_imediata"] != 1).sum())
        diag["candidatos_com_1a_opcao_sem_vaga_imediata_excluidos"] = fora
        r1 = r1[r1["celula_com_vaga_imediata"] == 1]

    def localizar(df: pd.DataFrame) -> np.ndarray:
        chave = pd.MultiIndex.from_frame(df[["ciclo", "co_cnes_7d", "cod_curso"]])
        idx = pos.reindex(chave)
        if idx.isna().any():
            raise AssertionError(f"{int(idx.isna().sum())} escolhas fora do conjunto de escolha ({modelo}, {conjunto})")
        return idx.to_numpy(dtype=int)

    g1 = pd.DataFrame({"idx_escolhida": localizar(r1), "idx_excluida": -1,
                       "cluster_conjunto": r1["id_conjunto_escolha"].to_numpy(),
                       "cluster_candidato": r1["id_candidato"].to_numpy(), "posto": 1,
                       "cluster_curso": [f"curso{int(k):02d}" for k in r1["cod_curso"]]})
    if modelo == MODELO_COND:
        return g1.reset_index(drop=True), diag
    r2 = r2[r2["id_candidato"].isin(set(r1["id_candidato"]))]
    escolhida1 = pd.Series(g1["idx_escolhida"].to_numpy(), index=g1["cluster_candidato"].to_numpy())
    conj1 = pd.Series(g1["cluster_conjunto"].to_numpy(), index=g1["cluster_candidato"].to_numpy())
    idx2 = localizar(r2)
    mesmo_curso = conj1.reindex(r2["id_candidato"]).to_numpy() == r2["id_conjunto_escolha"].to_numpy()
    excl = np.where(mesmo_curso, escolhida1.reindex(r2["id_candidato"]).to_numpy(), -1)
    if (excl == idx2).any():
        raise AssertionError("2a opção igual à 1a opção")
    g2 = pd.DataFrame({"idx_escolhida": idx2, "idx_excluida": excl.astype(int),
                       "cluster_conjunto": r2["id_conjunto_escolha"].to_numpy(),
                       "cluster_candidato": r2["id_candidato"].to_numpy(), "posto": 2,
                       "cluster_curso": [f"curso{int(k):02d}" for k in r2["cod_curso"]]})
    diag["grupos_posto_2"] = int(len(g2))
    diag["grupos_posto_2_em_curso_diferente_da_1a"] = int((~mesmo_curso).sum())
    return pd.concat([g1, g2], ignore_index=True), diag


# --------------------------------------------------------------------------
# Logit condicional (e explodido) por máxima verossimilhança
# --------------------------------------------------------------------------

def _estatisticas(theta: np.ndarray, X: np.ndarray, conj_cel: np.ndarray, esc: np.ndarray, exc: np.ndarray,
                  com_hess: bool = True, offset: np.ndarray | None = None) -> dict:
    """Log-verossimilhança, scores por grupo e informação, sem expandir o formato longo.

    Cada grupo escolhe `esc` entre as células do conjunto de `esc`, menos `exc` (se >= 0).
    """
    n_conj = int(conj_cel.max()) + 1
    v = X @ theta if offset is None else X @ theta + offset
    vmax = np.full(n_conj, -np.inf)
    np.maximum.at(vmax, conj_cel, v)
    e = np.exp(v - vmax[conj_cel])
    D = np.bincount(conj_cel, weights=e, minlength=n_conj)
    M1 = np.zeros((n_conj, X.shape[1]))
    np.add.at(M1, conj_cel, e[:, None] * X)
    S = conj_cel[esc]
    tem_exc = exc >= 0
    exc_ = np.where(tem_exc, exc, 0)
    e_exc = np.where(tem_exc, e[exc_], 0.0)
    Dg = D[S] - e_exc
    if np.any(Dg <= D[S] * 1e-12):
        raise FloatingPointError("denominador degenerado ao retirar a 1a opção do conjunto do posto 2")
    M1g = M1[S] - e_exc[:, None] * X[exc_]
    mbar = M1g / Dg[:, None]
    scores = X[esc] - mbar
    ll = float(np.sum(v[esc] - vmax[S] - np.log(Dg)))
    out = {"ll": ll, "scores": scores, "grad": scores.sum(axis=0)}
    if com_hess:
        M2 = np.zeros((n_conj, X.shape[1], X.shape[1]))
        np.add.at(M2, conj_cel, e[:, None, None] * X[:, :, None] * X[:, None, :])
        w = np.bincount(S, weights=1.0 / Dg, minlength=n_conj)
        info = np.einsum("s,sij->ij", w, M2)
        xe = X[exc_] * np.sqrt(e_exc / Dg)[:, None]
        info -= xe.T @ xe
        info -= mbar.T @ mbar
        out["info"] = info
    return out


def ajustar_logit(X: np.ndarray, conj_cel: np.ndarray, esc: np.ndarray, exc: np.ndarray | None = None,
                  offset: np.ndarray | None = None) -> dict:
    """Newton–Raphson com meio-passo; a log-verossimilhança é côncava. `offset` entra na utilidade com
    coeficiente fixo (usado no ajuste restrito do score bootstrap)."""
    exc = np.full(len(esc), -1) if exc is None else np.asarray(exc, dtype=int)
    theta = np.zeros(X.shape[1])
    est = _estatisticas(theta, X, conj_cel, esc, exc, offset=offset)
    convergiu, it = False, 0
    for it in range(1, MAX_ITER + 1):
        passo = np.linalg.solve(est["info"], est["grad"])
        decremento = float(est["grad"] @ passo)  # decremento de Newton: invariante à escala de X
        if decremento < TOL_DECREMENTO:
            convergiu = True
            break
        # Tolerância relativa no teste de subida: abaixo dela a diferença de log-verossimilhança é arredondamento.
        tol_ll = 1e-12 * max(1.0, abs(est["ll"]))
        t = 1.0
        while True:
            novo = _estatisticas(theta + t * passo, X, conj_cel, esc, exc, offset=offset)
            if novo["ll"] >= est["ll"] - tol_ll or t < 1e-8:
                break
            t /= 2.0
        theta = theta + t * passo
        est = novo
        if np.max(np.abs(t * passo)) < TOL_PASSO:
            convergiu = True
            break
    est = _estatisticas(theta, X, conj_cel, esc, exc, offset=offset)
    dec_final = float(est["grad"] @ np.linalg.solve(est["info"], est["grad"]))
    return {"theta": theta, "ll": est["ll"], "info": est["info"], "scores": est["scores"], "grad": est["grad"],
            "iteracoes": it, "decremento_final": dec_final,
            "convergiu": bool(convergiu and dec_final < 1e-8 and np.all(np.isfinite(theta)))}


def covariancia_cluster(info_inv: np.ndarray, scores: np.ndarray, clusters: np.ndarray) -> tuple[np.ndarray, int]:
    """Sanduíche CR com fator G/(G − 1)."""
    codigos, idx = np.unique(clusters, return_inverse=True)
    G = len(codigos)
    sc = np.zeros((G, scores.shape[1]))
    np.add.at(sc, idx, scores)
    meio = sc.T @ sc
    return (G / (G - 1.0)) * info_inv @ meio @ info_inv, G


def efeito_probabilidade(theta: np.ndarray, X: np.ndarray, conj_cel: np.ndarray, esc_r1: np.ndarray,
                         log_razao: float) -> dict:
    """Média, sobre candidatos (posto 1) e células do seu conjunto, da variação da probabilidade de escolher a
    célula quando a sua utilidade sobe `log_razao` (= 5·beta para +R$ 5 mil), o resto fixo."""
    n_conj = int(conj_cel.max()) + 1
    v = X @ theta
    vmax = np.full(n_conj, -np.inf)
    np.maximum.at(vmax, conj_cel, v)
    e = np.exp(v - vmax[conj_cel])
    D = np.bincount(conj_cel, weights=e, minlength=n_conj)
    P = e / D[conj_cel]
    OR = math.exp(log_razao)
    P1 = P * OR / (1.0 + P * (OR - 1.0))
    dP = P1 - P
    N = np.bincount(conj_cel[esc_r1], minlength=n_conj).astype(float)  # candidatos por conjunto
    w = N[conj_cel]  # cada célula pesa o número de candidatos que a têm no conjunto
    pares = w.sum()
    media_dp = float((w * dP).sum() / pares)
    media_p = float((w * P).sum() / pares)
    return {"variacao_prob_media": media_dp, "prob_media_base": media_p,
            "variacao_relativa_media": float((w * dP / P).sum() / pares),
            "razao_variacao_media_por_prob_media": media_dp / media_p, "pares_candidato_celula": float(pares)}


def gradiente_numerico(f, theta: np.ndarray) -> np.ndarray:
    g = np.zeros_like(theta)
    for k in range(len(theta)):
        h = 1e-5 * max(1.0, abs(theta[k]))
        tp, tm = theta.copy(), theta.copy()
        tp[k] += h
        tm[k] -= h
        g[k] = (f(tp) - f(tm)) / (2 * h)
    return g


# --------------------------------------------------------------------------
# Estimação de uma especificação
# --------------------------------------------------------------------------

def colunas_sem_variacao(X: pd.DataFrame, conj_cel: np.ndarray, usadas: np.ndarray) -> list[str]:
    """Colunas sem variação dentro de nenhum conjunto usado (não identificadas no logit condicional)."""
    fora = []
    sub = X.iloc[usadas]
    cc = conj_cel[usadas]
    for col in X.columns:
        x = sub[col].to_numpy()
        mx = pd.Series(x).groupby(cc).agg(lambda s: s.max() - s.min())
        if float(mx.max()) == 0.0:
            fora.append(col)
    return fora


def diagnostico_colinearidade(X: pd.DataFrame, conj_cel: np.ndarray, termos_bolsa_: list[str]) -> dict:
    """R² e VIF de cada termo da bolsa contra os demais atributos, com X centrado dentro do conjunto
    (a variação que o logit condicional usa)."""
    Xc = X - X.groupby(conj_cel).transform("mean")
    out = {"numero_condicao_X_centrado": float(np.linalg.cond(Xc.to_numpy()))}
    for t in termos_bolsa_:
        y = Xc[t].to_numpy()
        Z = Xc.drop(columns=termos_bolsa_).to_numpy()
        coef, *_ = np.linalg.lstsq(Z, y, rcond=None)
        r2 = 1.0 - float(((y - Z @ coef) ** 2).sum() / (y ** 2).sum())
        out[t] = {"r2_contra_spline_e_controles": r2, "vif": (1.0 / (1.0 - r2)) if r2 < 1 else float("inf")}
    return out


def estimar(conj: pd.DataFrame, cand: pd.DataFrame, modelo: str, conjunto: str, espec: str,
            macros: list[str], estratos: list[str], *, grau: int | None = None, forma: str | None = None,
            nos_extras_mil: tuple[int, ...] = (), placebo_mil: int | None = None) -> dict:
    if grau is None or forma is None:
        grau, forma = ESPECIFICACOES[espec]
    grupos, diag = montar_grupos(cand, conj, modelo, conjunto)
    chave_conj = conj["id_conjunto_escolha"].to_numpy()
    codigos, conj_cel = np.unique(chave_conj, return_inverse=True)
    X = matriz_atributos(conj, grau, forma, macros, estratos, nos_extras_mil, placebo_mil)
    esc = grupos["idx_escolhida"].to_numpy()
    exc = grupos["idx_excluida"].to_numpy()
    conj_usados = np.unique(conj_cel[esc])
    usadas = np.flatnonzero(np.isin(conj_cel, conj_usados))
    omitidas = colunas_sem_variacao(X, conj_cel, usadas)
    notas = []
    if omitidas:
        notas.append("omitidas por não variarem dentro de nenhum conjunto: " + ", ".join(omitidas))
    X = X.drop(columns=omitidas)
    # Só as células dos conjuntos usados entram (os demais conjuntos não têm candidato).
    remap = -np.ones(len(conj), dtype=int)
    remap[usadas] = np.arange(len(usadas))
    Xu = X.iloc[usadas].reset_index(drop=True)
    _, conj_u = np.unique(conj_cel[usadas], return_inverse=True)
    esc_u = remap[esc]
    exc_u = np.where(exc >= 0, remap[np.where(exc >= 0, exc, 0)], -1)
    Xa = Xu.to_numpy(dtype=float)
    posto = np.linalg.matrix_rank(Xa - pd.DataFrame(Xa).groupby(conj_u).transform("mean").to_numpy())
    termos_b = [c for c in Xu.columns if c in ("bolsa_mil", "degrau_0300", "degrau_0400")]
    base = {"modelo": modelo, "conjunto": conjunto, "especificacao": espec, "termos": list(Xu.columns),
            "n_candidatos": int(grupos.loc[grupos["posto"] == 1, "cluster_candidato"].nunique()),
            "n_grupos_escolha": int(len(grupos)), "n_conjuntos": int(len(conj_usados)),
            "n_alternativas": int(len(usadas)), "diag_grupos": diag, "omitidas": omitidas,
            "colinearidade": diagnostico_colinearidade(Xu, conj_u, termos_b)}
    if posto < Xa.shape[1]:
        base.update({"ok": False, "nota": "; ".join(notas + [f"X sem posto completo ({posto} < {Xa.shape[1]})"])})
        return base
    try:
        fit = ajustar_logit(Xa, conj_u, esc_u, exc_u)
    except (np.linalg.LinAlgError, FloatingPointError) as erro:
        base.update({"ok": False, "nota": "; ".join(notas + [f"estimação falhou: informação singular ou denominador "
                                                             f"degenerado ({type(erro).__name__}); provável separação "
                                                             f"(atributo que nenhum candidato escolhe)"])})
        return base
    if not fit["convergiu"]:
        base.update({"ok": False, "nota": "; ".join(notas + ["Newton–Raphson não convergiu"]),
                     "iteracoes": fit["iteracoes"]})
        return base
    info_inv = np.linalg.inv(fit["info"])
    divergentes = [t for t, v in zip(Xu.columns, np.diag(info_inv)) if math.sqrt(max(v, 0.0)) > LIMITE_EP_SEPARACAO]
    if divergentes:
        notas.append("possível separação: EP de máxima verossimilhança explode em " + ", ".join(divergentes) +
                     " (coef. divergente; o EP desse termo não tem sentido)")
    V_conj, G_conj = covariancia_cluster(info_inv, fit["scores"], grupos["cluster_conjunto"].to_numpy())
    V_cand, G_cand = covariancia_cluster(info_inv, fit["scores"], grupos["cluster_candidato"].to_numpy())
    base.update({"ok": True, "nota": "; ".join(notas), "theta": fit["theta"], "ll": fit["ll"],
                 "iteracoes": fit["iteracoes"], "grad_max": float(np.max(np.abs(fit["grad"]))),
                 "V_mle": info_inv, "V_conj": V_conj, "V_cand": V_cand, "G_conj": G_conj, "G_cand": G_cand,
                 "_X": Xa, "_conj": conj_u, "_esc_r1": esc_u[grupos["posto"].to_numpy() == 1],
                 "_esc": esc_u, "_exc": exc_u, "_grupos": grupos, "_scores": fit["scores"], "_info_inv": info_inv,
                 "_s_mil_min": float(conj["s_mil"].iloc[usadas].min()),
                 "_s_mil_max": float(conj["s_mil"].iloc[usadas].max())})
    return base


# --------------------------------------------------------------------------
# Linhas de saída
# --------------------------------------------------------------------------

def linhas_estimativas(ciclo: str, r: dict) -> list[dict]:
    comuns = {"natureza_dos_dados": NATUREZA, "ciclo": ciclo, "conjunto": r["conjunto"], "modelo": r["modelo"],
              "especificacao": r["especificacao"], "no_protocolo": not r["especificacao"].startswith(TAG_ROB),
              "papel_no_protocolo": papel_no_protocolo(r["modelo"], r["conjunto"], r["especificacao"]),
              "n_candidatos": r["n_candidatos"], "n_grupos_escolha": r["n_grupos_escolha"],
              "n_conjuntos": r["n_conjuntos"], "n_alternativas": r["n_alternativas"]}
    if not r["ok"]:
        return [{**comuns, "termo": t, "coef": np.nan, "ep_cluster_conjunto": np.nan, "ep_mle": np.nan,
                 "ep_cluster_candidato": np.nan, "ic95_inf": np.nan, "ic95_sup": np.nan, "ic95": "",
                 "p": np.nan, "p_t_g_menos_1": np.nan, "g_conjuntos": np.nan, "g_candidatos": np.nan,
                 "log_verossimilhanca": np.nan, "iteracoes": r.get("iteracoes", np.nan), "convergiu": False,
                 "nota": r["nota"]} for t in r["termos"]]
    out = []
    G = r["G_conj"]
    for k, t in enumerate(r["termos"]):
        b = float(r["theta"][k])
        ep = math.sqrt(r["V_conj"][k, k])
        z = b / ep
        lo, hi = b - Z95 * ep, b + Z95 * ep
        out.append({**comuns, "termo": t, "coef": b, "ep_cluster_conjunto": ep, "ep_mle": math.sqrt(r["V_mle"][k, k]),
                    "ep_cluster_candidato": math.sqrt(r["V_cand"][k, k]), "ic95_inf": lo, "ic95_sup": hi,
                    "ic95": f"[{lo:.6f}; {hi:.6f}]", "p": float(2 * stats.norm.sf(abs(z))),
                    "p_t_g_menos_1": float(2 * stats.t.sf(abs(z), G - 1)), "g_conjuntos": G,
                    "g_candidatos": r["G_cand"], "log_verossimilhanca": r["ll"], "iteracoes": r["iteracoes"],
                    "convergiu": True, "nota": r["nota"]})
    if "degrau_0300" in r["termos"] and "degrau_0400" in r["termos"]:
        i, j = r["termos"].index("degrau_0300"), r["termos"].index("degrau_0400")
        a = np.zeros(len(r["termos"]))
        a[i], a[j] = 1.0, -1.0
        d = float(a @ r["theta"])
        ep = math.sqrt(a @ r["V_conj"] @ a)
        lo, hi = d - Z95 * ep, d + Z95 * ep
        out.append({**comuns, "termo": "teste_igualdade_degraus_0300_menos_0400", "coef": d,
                    "ep_cluster_conjunto": ep, "ep_mle": math.sqrt(a @ r["V_mle"] @ a),
                    "ep_cluster_candidato": math.sqrt(a @ r["V_cand"] @ a), "ic95_inf": lo, "ic95_sup": hi,
                    "ic95": f"[{lo:.6f}; {hi:.6f}]", "p": float(2 * stats.norm.sf(abs(d / ep))),
                    "p_t_g_menos_1": float(2 * stats.t.sf(abs(d / ep), G - 1)), "g_conjuntos": G,
                    "g_candidatos": r["G_cand"], "log_verossimilhanca": r["ll"], "iteracoes": r["iteracoes"],
                    "convergiu": True,
                    "nota": "; ".join(x for x in [r["nota"], "Wald de H0: degrau_0300 = degrau_0400 (qui-quadrado 1 gl "
                                                  "= z²); coef = diferença dos degraus"] if x)})
    return out


def linhas_efeitos(ciclo: str, r: dict) -> list[dict]:
    comuns = {"natureza_dos_dados": NATUREZA, "ciclo": ciclo, "conjunto": r["conjunto"], "modelo": r["modelo"],
              "especificacao": r["especificacao"],
              "papel_no_protocolo": papel_no_protocolo(r["modelo"], r["conjunto"], r["especificacao"]),
              "n_candidatos": r["n_candidatos"], "n_conjuntos": r["n_conjuntos"], "n_alternativas": r["n_alternativas"]}
    termos = [t for t in ("bolsa_mil", "degrau_0300", "degrau_0400") if t in r["termos"]]
    if not r["ok"]:
        return [{**comuns, "termo": t, "quantidade": q, "estimativa": np.nan, "ep_cluster_conjunto": np.nan,
                 "ep_mle": np.nan, "ic95_inf": np.nan, "ic95_sup": np.nan, "metodo_ic": "", "nota": r["nota"]}
                for t in termos for q in ("razao_chances_por_5mil", "variacao_prob_media_pp")]
    out = []
    for t in termos:
        k = r["termos"].index(t)
        fator = PASSO_BOLSA_MIL if t == "bolsa_mil" else 1.0  # degrau já é +R$ 5 mil
        b = float(r["theta"][k])
        ep = math.sqrt(r["V_conj"][k, k])
        ep_mle = math.sqrt(r["V_mle"][k, k])
        rotulo = "por +R$ 5 mil (5 × coef. da bolsa em R$ mil)" if t == "bolsa_mil" else f"{t}: um degrau de +R$ 5 mil"
        out.append({**comuns, "termo": t, "quantidade": "log_razao_chances_por_5mil", "estimativa": fator * b,
                    "ep_cluster_conjunto": fator * ep, "ep_mle": fator * ep_mle,
                    "ic95_inf": fator * (b - Z95 * ep), "ic95_sup": fator * (b + Z95 * ep),
                    "metodo_ic": "normal, EP cluster por conjunto", "nota": rotulo})
        out.append({**comuns, "termo": t, "quantidade": "razao_chances_por_5mil", "estimativa": math.exp(fator * b),
                    "ep_cluster_conjunto": math.exp(fator * b) * fator * ep, "ep_mle": math.exp(fator * b) * fator * ep_mle,
                    "ic95_inf": math.exp(fator * (b - Z95 * ep)), "ic95_sup": math.exp(fator * (b + Z95 * ep)),
                    "metodo_ic": "exp do IC do log (EP cluster por conjunto); EP pelo delta", "nota": rotulo})

        def f_media(th: np.ndarray, campo: str, k=k, fator=fator) -> float:
            return efeito_probabilidade(th, r["_X"], r["_conj"], r["_esc_r1"], fator * th[k])[campo]

        ef = efeito_probabilidade(r["theta"], r["_X"], r["_conj"], r["_esc_r1"], fator * b)
        for q, campo, escala in (("variacao_prob_media_pp", "variacao_prob_media", 100.0),
                                 ("prob_media_base_pp", "prob_media_base", 100.0),
                                 ("variacao_relativa_media", "variacao_relativa_media", 1.0),
                                 ("variacao_media_sobre_prob_media", "razao_variacao_media_por_prob_media", 1.0)):
            est = escala * ef[campo]
            if q == "prob_media_base_pp":
                out.append({**comuns, "termo": t, "quantidade": q, "estimativa": est, "ep_cluster_conjunto": np.nan,
                            "ep_mle": np.nan, "ic95_inf": np.nan, "ic95_sup": np.nan, "metodo_ic": "",
                            "nota": "média de 1/(células do conjunto) sobre candidatos × células: referência, "
                                    "sem incerteza (não depende de parâmetros)"})
                continue
            g = escala * gradiente_numerico(lambda th, c=campo: f_media(th, c), r["theta"])
            e1 = math.sqrt(g @ r["V_conj"] @ g)
            e2 = math.sqrt(g @ r["V_mle"] @ g)
            out.append({**comuns, "termo": t, "quantidade": q, "estimativa": est, "ep_cluster_conjunto": e1,
                        "ep_mle": e2, "ic95_inf": est - Z95 * e1, "ic95_sup": est + Z95 * e1,
                        "metodo_ic": "delta (gradiente numérico central), EP cluster por conjunto",
                        "nota": f"{rotulo}; média sobre {int(ef['pares_candidato_celula'])} pares candidato × célula "
                                f"(candidatos de 1a opção), resto fixo"})
    return out


# --------------------------------------------------------------------------
# Figura
# --------------------------------------------------------------------------

def curva_utilidade(r: dict, s_grade: np.ndarray, grau: int, mapa: dict[str, float]) -> tuple[np.ndarray, np.ndarray]:
    """u(s) − u(0,300) = spline + bolsa pela regra, demais atributos fixos; EP pelo delta (cluster por conjunto)."""
    termos = r["termos"]
    faixa_s = faixa_pela_regra(s_grade)
    bolsa_s = pd.Series(faixa_s).map(mapa).to_numpy(dtype=float)
    B = base_spline(s_grade, grau)
    B0 = base_spline(np.array([float(CORTES_MIL[0])]), grau)
    A = np.zeros((len(s_grade), len(termos)))
    for col in B.columns:
        A[:, termos.index(col)] = B[col].to_numpy() - B0[col].to_numpy()[0]
    if "bolsa_mil" in termos:
        A[:, termos.index("bolsa_mil")] = bolsa_s - mapa["FAIXA 3"]
    else:
        A[:, termos.index("degrau_0300")] = np.isin(faixa_s, ["FAIXA 2", "FAIXA 1"]).astype(float)
        A[:, termos.index("degrau_0400")] = (faixa_s == "FAIXA 1").astype(float)
    u = A @ r["theta"]
    ep = np.sqrt(np.einsum("ij,jk,ik->i", A, r["V_conj"], A))
    return u, ep


def gravar_figura(resultados: dict, mapa: dict[str, float]) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    series = {  # especificação: (cor, estilo, rótulo); paleta categórica fixa (slots 1, 2, 3)
        "spline_linear__bolsa_linear": ("#2a78d6", "-", "spline linear + bolsa linear (principal), com IC 95% cluster"),
        "spline_quadratico__bolsa_linear": ("#eb6834", "-", "spline quadrático + bolsa linear (variante)"),
        "spline_linear__degraus_por_corte": ("#1baf7a", "--", "spline linear + degrau por corte (sensibilidade)"),
    }
    fig, eixos = plt.subplots(2, 2, figsize=(11, 8.6), sharey=False)
    for ax, ciclo in zip(eixos.ravel(), CICLOS):
        for espec, (cor, estilo, rotulo) in series.items():
            r = resultados[(ciclo, MODELO_COND, "principal", espec)]
            if not r["ok"]:
                continue
            grau = ESPECIFICACOES[espec][0]
            lo_s, hi_s = r["_s_mil_min"], r["_s_mil_max"]
            segmentos = [(lo_s, CORTES_MIL[0]), (CORTES_MIL[0] + 1e-6, CORTES_MIL[1]), (CORTES_MIL[1] + 1e-6, hi_s)]
            for i, (a, b) in enumerate(segmentos):
                if b <= a:
                    continue
                s = np.linspace(a, b, 120)
                u, ep = curva_utilidade(r, s, grau, mapa)
                ax.plot(s / 1000, u, color=cor, lw=2, ls=estilo, label=rotulo if (i == 0 and ciclo == CICLOS[0]) else None)
                if espec == "spline_linear__bolsa_linear":
                    ax.fill_between(s / 1000, u - Z95 * ep, u + Z95 * ep, color=cor, alpha=0.15, lw=0)
        for c in CORTES_MIL:
            ax.axvline(c / 1000, color="#52514e", lw=0.8, ls=":")
        ax.axhline(0, color="#52514e", lw=0.6)
        ax.set_title("empilhado" if ciclo == "empilhado" else f"ciclo {ciclo}", fontsize=11)
        ax.set_xlabel("IVS 2010 oficial do município da célula")
        ax.set_ylabel("utilidade relativa a IVS = 0,300 (logit)")
        ax.grid(True, color="#e6e5e0", lw=0.5)
        ax.spines[["top", "right"]].set_visible(False)
    fig.legend(loc="lower center", ncol=2, fontsize=8.5, frameon=False)
    fig.suptitle("E9: utilidade estimada da célula contra o IVS (spline contínuo + bolsa pela faixa)\n"
                 "logit condicional da 1a opção, conjunto principal; demais atributos fixos; dados EMPÍRICOS",
                 fontsize=11)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    OUT_FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_FIGURA, dpi=150, metadata={"Software": None})
    plt.close(fig)


# --------------------------------------------------------------------------
# Tabelas de relato (fragmento Markdown copiado no doc 42 e conferido por teste)
# --------------------------------------------------------------------------

def tabelas_relato(est: pd.DataFrame, efe: pd.DataFrame, diag_ciclo: dict, coli: dict,
                   rob: pd.DataFrame | None = None) -> str:
    L = ["<!-- gerado por scripts/rdd_bolsa/16_estimar_E9_escolha.py; não editar à mão -->", ""]
    L += ["**Tabela 1. Amostra por ciclo (conjunto principal, logit condicional da 1ª opção).**", "",
          "| ciclo | candidatos | conjuntos | alternativas | alternativas por conjunto (mín.–mediana–máx.) |"
          " candidatos sem linha de 1ª opção (excluídos) |", "|---|---:|---:|---:|---|---:|"]
    for c in CICLOS:
        d = diag_ciclo[c]
        L.append(f"| {c} | {d['n_candidatos']} | {d['n_conjuntos']} | {d['n_alternativas']} | "
                 f"{d['alt_min']}–{fmt(d['alt_mediana'], 1)}–{d['alt_max']} | {d['sem_1a_opcao']} |")
    L += ["", "**Tabela 2. Bolsa linear: coeficiente (por R$ 1 mil), razão de chances por +R$ 5 mil e variação "
              "média da probabilidade de escolha da célula (p.p.) quando a sua bolsa sobe R$ 5 mil.** EP e IC 95% "
              "com cluster por conjunto de escolha; p pela normal e pela t com G − 1 gl.", "",
          "| ciclo | modelo | conjunto | spline | coef. | EP | IC 95% | p | p (t, G−1) | RC por +R$ 5 mil [IC 95%] |"
          " Δ prob. média, p.p. [IC 95%] | prob. média base, p.p. |", "|---|---|---|---|---:|---:|---|---:|---:|---|---|---:|"]
    nome_modelo = {MODELO_COND: "condicional", MODELO_EXPL: "explodido"}
    for (modelo, conjunto) in COMBINACOES:
        for espec in ("spline_linear__bolsa_linear", "spline_quadratico__bolsa_linear"):
            for c in CICLOS:
                e = est[(est.ciclo == c) & (est.modelo == modelo) & (est.conjunto == conjunto) &
                        (est.especificacao == espec) & (est.termo == "bolsa_mil")].iloc[0]
                f = efe[(efe.ciclo == c) & (efe.modelo == modelo) & (efe.conjunto == conjunto) &
                        (efe.especificacao == espec) & (efe.termo == "bolsa_mil")].set_index("quantidade")
                rc, dp, pb = f.loc["razao_chances_por_5mil"], f.loc["variacao_prob_media_pp"], f.loc["prob_media_base_pp"]
                L.append(f"| {c} | {nome_modelo[modelo]} | {conjunto} | {'linear' if '_linear__' in espec else 'quadrático'} | "
                         f"{fmt(e.coef, 4)} | {fmt(e.ep_cluster_conjunto, 4)} | [{fmt(e.ic95_inf, 4)}; {fmt(e.ic95_sup, 4)}] | "
                         f"{fmt_p(e.p)} | {fmt_p(e.p_t_g_menos_1)} | {fmt(rc.estimativa, 3)} [{fmt(rc.ic95_inf, 3)}; "
                         f"{fmt(rc.ic95_sup, 3)}] | {fmt(dp.estimativa, 4)} [{fmt(dp.ic95_inf, 4)}; {fmt(dp.ic95_sup, 4)}] | "
                         f"{fmt(pb.estimativa, 4)} |")
    L += ["", "**Tabela 3. Principal (condicional, conjunto principal, spline linear, bolsa linear): os três EPs do "
              "coeficiente da bolsa.**", "",
          "| ciclo | coef. | EP cluster por conjunto (G) | EP máxima verossimilhança | EP cluster por candidato |",
          "|---|---:|---:|---:|---:|"]
    for c in CICLOS:
        e = est[(est.ciclo == c) & (est.modelo == MODELO_COND) & (est.conjunto == "principal") &
                (est.especificacao == "spline_linear__bolsa_linear") & (est.termo == "bolsa_mil")].iloc[0]
        L.append(f"| {c} | {fmt(e.coef, 4)} | {fmt(e.ep_cluster_conjunto, 4)} ({int(e.g_conjuntos)}) | {fmt(e.ep_mle, 4)} | "
                 f"{fmt(e.ep_cluster_candidato, 4)} |")
    L += ["", "**Tabela 4. Degraus por corte (cada degrau = +R$ 5 mil; coeficiente em log da razão de chances) e "
              "teste de igualdade.** EP cluster por conjunto.", "",
          "| ciclo | modelo | conjunto | spline | degrau 0,300 [IC 95%] | degrau 0,400 [IC 95%] | diferença | p igualdade |"
          " p igualdade (t, G−1) |", "|---|---|---|---|---|---|---:|---:|---:|"]
    for (modelo, conjunto) in COMBINACOES:
        for espec in ("spline_linear__degraus_por_corte", "spline_quadratico__degraus_por_corte"):
            for c in CICLOS:
                sel = est[(est.ciclo == c) & (est.modelo == modelo) & (est.conjunto == conjunto) &
                          (est.especificacao == espec)].set_index("termo")
                a, b, t = sel.loc["degrau_0300"], sel.loc["degrau_0400"], sel.loc["teste_igualdade_degraus_0300_menos_0400"]
                L.append(f"| {c} | {nome_modelo[modelo]} | {conjunto} | {'linear' if '_linear__' in espec else 'quadrático'} | "
                         f"{fmt(a.coef, 3)} [{fmt(a.ic95_inf, 3)}; {fmt(a.ic95_sup, 3)}] | {fmt(b.coef, 3)} "
                         f"[{fmt(b.ic95_inf, 3)}; {fmt(b.ic95_sup, 3)}] | {fmt(t.coef, 3)} | {fmt_p(t.p)} | "
                         f"{fmt_p(t.p_t_g_menos_1)} |")
    L += ["", "**Tabela 5. Colinearidade da bolsa (principal, spline linear): R² da bolsa contra o spline e os "
              "controles, com X centrado dentro do conjunto de escolha.**", "",
          "| ciclo | R² | VIF | nº de condição de X centrado |", "|---|---:|---:|---:|"]
    for c in CICLOS:
        d = coli[c]
        L.append(f"| {c} | {fmt(d['bolsa_mil']['r2_contra_spline_e_controles'], 3)} | {fmt(d['bolsa_mil']['vif'], 2)} | "
                 f"{fmt(d['numero_condicao_X_centrado'], 1)} |")
    if rob is not None:
        L += tabelas_robustez(est, rob)
    return "\n".join(L) + "\n"


def _rob(rob: pd.DataFrame, analise: str, ciclo: str, estatistica: str | None = None) -> pd.Series:
    sel = rob[(rob.analise == analise) & (rob.ciclo == ciclo)]
    if estatistica is not None:
        sel = sel[sel.estatistica == estatistica]
    if len(sel) != 1:
        raise AssertionError(f"robustez: {analise} {ciclo} {estatistica}: {len(sel)} linhas")
    return sel.iloc[0]


def tabelas_robustez(est: pd.DataFrame, rob: pd.DataFrame) -> list[str]:
    """Tabelas 6–10: robustez pós-auditoria (pós-resultado, fora do protocolo)."""
    L = ["", "**Robustez pós-auditoria (tabelas 6 a 10).** Pós-resultado e fora do protocolo; linhas "
             f"`{TAG_ROB}` com `no_protocolo = False`. Não substituem as tabelas 1 a 5.", ""]
    principal = est[(est.modelo == MODELO_COND) & (est.conjunto == "principal") & (est.especificacao == ESPEC_PRINCIPAL)
                    & (est.termo == "bolsa_mil")].set_index("ciclo")
    L += ["**Tabela 6. Inferência com poucos clusters (principal: condicional, conjunto principal, spline linear, bolsa "
          "linear).** p do score bootstrap de Kline–Santos sob H0: coef. = 0; Rademacher por enumeração completa "
          f"quando G ≤ {G_MAX_ENUMERACAO}, senão {N_REAMOSTRAS} sorteios; Webb sempre por sorteio. CV3 com IC e p "
          "pela t com G − 1 gl. IC por inversão do score bootstrap Rademacher.", "",
          "| ciclo | cluster | G | coef. | EP CR1 | p CR1 | EP CV3 | p CV3 | p score (Rademacher) | p score (Webb) |"
          " IC 95% por inversão |", "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|"]
    for c in CICLOS:
        for nome in (("conjunto", "curso") if c == "empilhado" else ("conjunto",)):
            e = principal.loc[c]
            if nome == "conjunto":
                ep, pp, G = e.ep_cluster_conjunto, e.p, int(e.g_conjuntos)
            else:
                cc = rob[(rob.analise == "cluster_curso") & (rob.ciclo == c) & (rob.modelo == MODELO_COND) &
                         (rob.conjunto == "principal") & (rob.especificacao_base == ESPEC_PRINCIPAL) &
                         (rob.termo == "bolsa_mil")].iloc[0]
                ep, pp, G = cc.ep, cc.p, int(cc.g)
            cv3 = _rob(rob, f"cv3_cluster_{nome}", c)
            rad = _rob(rob, f"score_bootstrap_rademacher_cluster_{nome}", c)
            web = _rob(rob, f"score_bootstrap_webb_cluster_{nome}", c)
            sel = rob[(rob.analise == f"ic_inversao_score_rademacher_cluster_{nome}") & (rob.ciclo == c)]
            ic = f"[{fmt(sel.iloc[0].ic95_inf, 4)}; {fmt(sel.iloc[0].ic95_sup, 4)}]" if len(sel) else "—"
            L.append(f"| {c} | {nome} | {G} | {fmt(e.coef, 4)} | {fmt(ep, 4)} | {fmt_p(pp)} | {fmt(cv3.ep, 4)} | "
                     f"{fmt_p(cv3.p)} | {fmt_p(rad.p)} | {fmt_p(web.p)} | {ic} |")
    L += ["", "**Tabela 7. Forma funcional e conjuntos restritos a janelas em torno dos cortes (condicional, bolsa "
              "linear).** EP cluster por conjunto. Janela: só células com |IVS − corte| ≤ h e candidatos com a 1ª "
              "opção nelas.", "",
          "| ciclo | especificação | coef. | EP | IC 95% | p | candidatos | alternativas |",
          "|---|---|---:|---:|---|---:|---:|---:|"]
    rotulo = {"spline_cubico__bolsa_linear": "spline cúbico",
              "nos_cada_0050__spline_linear__bolsa_linear": "spline linear, nós a cada 0,05"}
    for h in JANELAS_MIL:
        rotulo[f"janela_{h:04d}__spline_linear__bolsa_linear"] = f"janela ±{fmt(h / 1000, 3)}, spline linear"
        rotulo[f"janela_{h:04d}__spline_cubico__bolsa_linear"] = f"janela ±{fmt(h / 1000, 3)}, spline cúbico"
    for nome, rot in rotulo.items():
        for c in CICLOS:
            sel = est[(est.ciclo == c) & (est.especificacao == f"{TAG_ROB}:{nome}") & (est.termo == "bolsa_mil")]
            if len(sel) != 1:
                L.append(f"| {c} | {rot} | — | — | — | — | — | — |")
                continue
            e = sel.iloc[0]
            L.append(f"| {c} | {rot} | {fmt(e.coef, 4)} | {fmt(e.ep_cluster_conjunto, 4)} | [{fmt(e.ic95_inf, 4)}; "
                     f"{fmt(e.ic95_sup, 4)}] | {fmt_p(e.p)} | {int(e.n_candidatos)} | {int(e.n_alternativas)} |")
    L += ["", "**Tabela 8. Cortes placebo** (degrau falso e nó no corte falso, com a bolsa verdadeira no modelo; cortes "
              "de 0,190 a 0,510 a cada 0,010, sem 0,290–0,310 e 0,390–0,410). t com EP cluster por conjunto. "
              "p por posto = (1 + nº de |t placebo| ≥ |t real|)/(1 + N).", "",
          "| ciclo | N | média do t placebo | dp do t placebo | fração com |t| > 1,96 | máx. |t| placebo | t real |"
          " nº |t placebo| ≥ |t real| | p por posto |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for c in CICLOS:
        g = lambda n: _rob(rob, "placebo_cortes", c, n).valor  # noqa: E731
        L.append(f"| {c} | {int(g('n_placebos'))} | {fmt(g('t_placebo_media'), 2)} | {fmt(g('t_placebo_dp'), 2)} | "
                 f"{fmt(g('fracao_abs_t_placebo_maior_que_1_96'), 3)} | {fmt(g('abs_t_placebo_max'), 2)} | "
                 f"{fmt(g('t_real'), 2)} | {int(g('n_abs_t_placebo_maior_ou_igual_ao_real'))} | {fmt(g('p_posto'), 3)} |")
    e13 = est[(est.ciclo == "1+3") & (est.termo == "bolsa_mil")].iloc[0]
    q = _rob(rob, "heterogeneidade_ciclos", "1,2,3")
    z = _rob(rob, "heterogeneidade_ciclos", "2 vs 3")
    L += ["", "**Tabela 9. Heterogeneidade entre ciclos (principal).**", "",
          "| teste | estimativa | EP | IC 95% | p |", "|---|---:|---:|---|---:|",
          f"| ciclos 1 e 3 empilhados, coef. da bolsa (G = {int(e13.g_conjuntos)}) | {fmt(e13.coef, 4)} | "
          f"{fmt(e13.ep_cluster_conjunto, 4)} | [{fmt(e13.ic95_inf, 4)}; {fmt(e13.ic95_sup, 4)}] | {fmt_p(e13.p)} |",
          f"| Q de Cochran, ciclos 1, 2 e 3 ({int(q.g)} gl) | {fmt(q.valor, 2)} | — | — | {fmt_p(q.p)} |",
          f"| z, ciclo 2 menos ciclo 3 | {fmt(z.valor, 2)} | {fmt(z.ep, 4)} | — | {fmt_p(z.p)} |"]
    L += ["", "**Tabela 10. Empilhado: EP com cluster por conjunto (protocolo) e por curso (robustez).**", "",
          "| modelo | conjunto | especificação | termo | coef. | EP conjunto (G) | p conjunto | EP curso (G) | p curso |",
          "|---|---|---|---|---:|---:|---:|---:|---:|"]
    nome_modelo = {MODELO_COND: "condicional", MODELO_EXPL: "explodido"}
    cc = rob[(rob.analise == "cluster_curso") & (rob.ciclo == "empilhado")]
    for x in cc.itertuples():
        e = est[(est.ciclo == "empilhado") & (est.modelo == x.modelo) & (est.conjunto == x.conjunto) &
                (est.especificacao == x.especificacao_base) & (est.termo == x.termo)].iloc[0]
        L.append(f"| {nome_modelo[x.modelo]} | {x.conjunto} | {x.especificacao_base} | {x.termo} | {fmt(e.coef, 4)} | "
                 f"{fmt(e.ep_cluster_conjunto, 4)} ({int(e.g_conjuntos)}) | {fmt_p(e.p)} | {fmt(x.ep, 4)} ({int(x.g)}) | "
                 f"{fmt_p(x.p)} |")
    return L


# --------------------------------------------------------------------------
# Robustez pós-auditoria (pós-resultado; fora do protocolo)
# --------------------------------------------------------------------------

def score_efetivo_por_cluster(X: np.ndarray, conj: np.ndarray, esc: np.ndarray, exc: np.ndarray, k: int,
                              beta0: float, clusters: np.ndarray) -> np.ndarray:
    """Score de Kline e Santos (2012) para H0: theta_k = beta0, somado por cluster.

    Ajusta o modelo restrito (theta_k fixo em beta0, como offset), avalia scores e informação no ponto
    restrito e projeta o score de theta_k fora dos parâmetros de incômodo: s~ = s_k − I_kη I_ηη⁻¹ s_η.
    """
    K = X.shape[1]
    outros = [j for j in range(K) if j != k]
    fit = ajustar_logit(X[:, outros], conj, esc, exc, offset=beta0 * X[:, k])
    if not fit["convergiu"]:
        raise FloatingPointError(f"ajuste restrito não convergiu em beta0 = {beta0}")
    theta = np.empty(K)
    theta[outros] = fit["theta"]
    theta[k] = beta0
    est = _estatisticas(theta, X, conj, esc, exc)
    info, S = est["info"], est["scores"]
    a = np.linalg.solve(info[np.ix_(outros, outros)], info[outros, k])
    st = S[:, k] - S[:, outros] @ a
    _, idx = np.unique(clusters, return_inverse=True)
    return np.bincount(idx, weights=st)


def p_rademacher_exato(sc: np.ndarray) -> float:
    """p bicaudal do score bootstrap com Rademacher, enumerando os 2^G sinais (encontro no meio).

    Com pesos ±1 o denominador studentizado é constante, e basta comparar |soma ponderada| com |soma|."""
    G = len(sc)
    alvo = abs(float(sc.sum())) * (1 - 1e-12)
    if alvo == 0:
        return 1.0

    def somas(v: np.ndarray) -> np.ndarray:
        out = np.zeros(1)
        for x in v:
            out = np.concatenate([out + x, out - x])
        return out

    h = G // 2
    A = somas(sc[:h])
    B = np.sort(somas(sc[h:]))
    n_ge = len(B) - np.searchsorted(B, alvo - A, side="left")
    n_le = np.searchsorted(B, -alvo - A, side="right")
    return float((n_ge + n_le).sum()) / float(2 ** G)


_PESOS_CACHE: dict[tuple[str, int], np.ndarray] = {}


def matriz_pesos(tipo: str, G: int) -> np.ndarray:
    """N_REAMOSTRAS sorteios fixos (semente SEMENTE_BOOT, G e tipo) de pesos Rademacher ou Webb."""
    chave = (tipo, G)
    if chave not in _PESOS_CACHE:
        rng = np.random.default_rng([SEMENTE_BOOT, G, 1 if tipo == "rademacher" else 6])
        if tipo == "rademacher":
            W = rng.choice(np.array([-1.0, 1.0]), size=(N_REAMOSTRAS, G))
        else:
            W = rng.choice(PESOS_WEBB, size=(N_REAMOSTRAS, G))
        _PESOS_CACHE[chave] = W
    return _PESOS_CACHE[chave]


def p_score_bootstrap(sc: np.ndarray, tipo: str) -> tuple[float, str, int]:
    """p bicaudal studentizado; Rademacher exato se G <= G_MAX_ENUMERACAO, senão sorteios fixos."""
    G = len(sc)
    if tipo == "rademacher" and G <= G_MAX_ENUMERACAO:
        return p_rademacher_exato(sc), "enumeração completa dos 2^G sinais", 2 ** G
    W = matriz_pesos(tipo, G)
    t_obs = abs(sc.sum()) / math.sqrt((sc ** 2).sum())
    t_b = np.abs(W @ sc) / np.sqrt((W ** 2) @ (sc ** 2))
    return float(np.mean(t_b >= t_obs * (1 - 1e-12))), f"{N_REAMOSTRAS} sorteios, semente {SEMENTE_BOOT}", N_REAMOSTRAS


def ic_inversao_score(r: dict, k: int, clusters: np.ndarray, tipo: str = "rademacher",
                      alfa: float = 0.05) -> tuple[float, float, str]:
    """IC 95% por inversão do score bootstrap: {beta0 : p(beta0) >= alfa}, fronteiras por bissecção a partir
    da estimativa (p = 1 no ótimo), com os mesmos pesos em todo beta0."""
    b = float(r["theta"][k])
    ep = math.sqrt(r["V_conj"][k, k])

    def p(b0: float) -> float:
        sc = score_efetivo_por_cluster(r["_X"], r["_conj"], r["_esc"], r["_exc"], k, b0, clusters)
        return p_score_bootstrap(sc, tipo)[0]

    lados = []
    for sinal in (-1.0, 1.0):
        dentro, passo = b, 2.0 * ep
        fora = b + sinal * passo
        n = 0
        while p(fora) >= alfa:
            dentro, passo = fora, 2.0 * passo
            fora = b + sinal * passo
            n += 1
            if n > 12:
                return float("nan"), float("nan"), "região de aceitação ilimitada na grade de busca"
        for _ in range(40):
            m = 0.5 * (dentro + fora)
            if p(m) >= alfa:
                dentro = m
            else:
                fora = m
            if abs(fora - dentro) < 1e-6:
                break
        lados.append(dentro)
    return lados[0], lados[1], "bissecção, tolerância 1e-6; supõe região de aceitação conexa"


def ep_cv3(r: dict, k: int, clusters: np.ndarray) -> tuple[float, int, str]:
    """CV3 (jackknife por cluster): ((G − 1)/G) Σ (b_(−g) − média)²."""
    codigos = np.unique(clusters)
    bs = []
    for g in codigos:
        m = clusters != g
        try:
            fit = ajustar_logit(r["_X"], r["_conj"], r["_esc"][m], r["_exc"][m])
        except np.linalg.LinAlgError:
            return float("nan"), len(codigos), f"informação singular sem o cluster {g}"
        if not fit["convergiu"]:
            return float("nan"), len(codigos), f"sem convergência sem o cluster {g}"
        bs.append(fit["theta"][k])
    bs = np.array(bs)
    G = len(bs)
    return float(math.sqrt((G - 1) / G * ((bs - bs.mean()) ** 2).sum())), G, ""


def _linha_rob(analise: str, ciclo: str, estatistica: str, valor: float, *, modelo: str = MODELO_COND,
               conjunto: str = "principal", especificacao_base: str = ESPEC_PRINCIPAL, termo: str = "bolsa_mil",
               ep: float = float("nan"), ic95_inf: float = float("nan"), ic95_sup: float = float("nan"),
               p: float = float("nan"), g: float = float("nan"), n_reamostras: float = float("nan"),
               metodo: str = "", nota: str = "") -> dict:
    return {"natureza_dos_dados": NATUREZA, "no_protocolo": False, "papel_no_protocolo": PAPEL_ROB,
            "especificacao": f"{TAG_ROB}:{analise}", "analise": analise, "ciclo": ciclo, "modelo": modelo,
            "conjunto": conjunto, "especificacao_base": especificacao_base, "termo": termo,
            "estatistica": estatistica, "valor": valor, "ep": ep, "ic95_inf": ic95_inf, "ic95_sup": ic95_sup,
            "p": p, "g": g, "n_reamostras": n_reamostras, "metodo": metodo, "nota": nota}


def _ciclos_int(ciclo: str) -> list[int]:
    return {"empilhado": [1, 2, 3], "1+3": [1, 3]}.get(ciclo, [int(ciclo)] if ciclo.isdigit() else [])


def _rotular(r: dict, nome: str) -> dict:
    r["especificacao"] = f"{TAG_ROB}:{nome}"
    return r


def robustez_pos_auditoria(conj_p: pd.DataFrame, cand: pd.DataFrame, macros: list[str], estratos: list[str],
                           resultados: dict) -> tuple[list[dict], list[dict], dict]:
    """Itens 1–5 da auditoria independente do E9. Devolve (linhas de estimativas, linhas de robustez, resumo)."""
    est_rows: list[dict] = []
    rob: list[dict] = []
    resumo: dict[str, Any] = {}

    def principal(ciclo: str) -> dict:
        return resultados[(ciclo, MODELO_COND, "principal", ESPEC_PRINCIPAL)]

    # 1. Empilhado com cluster por curso (a mesma célula CNES × curso aparece em mais de um ciclo).
    for (ciclo, modelo, conjunto, espec), r in resultados.items():
        if ciclo != "empilhado" or not r["ok"]:
            continue
        V, G = covariancia_cluster(r["_info_inv"], r["_scores"], r["_grupos"]["cluster_curso"].to_numpy())
        for t in ("bolsa_mil", "degrau_0300", "degrau_0400"):
            if t not in r["termos"]:
                continue
            k = r["termos"].index(t)
            b, e = float(r["theta"][k]), math.sqrt(V[k, k])
            rob.append(_linha_rob("cluster_curso", ciclo, "coef_ep_cluster_curso", b, modelo=modelo, conjunto=conjunto,
                                  especificacao_base=espec, termo=t, ep=e, ic95_inf=b - Z95 * e, ic95_sup=b + Z95 * e,
                                  p=float(2 * stats.norm.sf(abs(b / e))), g=G,
                                  metodo="CR1 por curso (código do curso, mesmo rótulo nos três ciclos)",
                                  nota=f"p pela t com G − 1 gl: {float(2 * stats.t.sf(abs(b / e), G - 1)):.6g}; "
                                       f"EP cluster por conjunto no protocolo: {math.sqrt(r['V_conj'][k, k]):.6g}"))

    # 2. Inferência com poucos clusters (especificação principal).
    for ciclo in CICLOS:
        r = principal(ciclo)
        k = r["termos"].index("bolsa_mil")
        variantes = [("conjunto", "cluster_conjunto")]
        if ciclo == "empilhado":
            variantes.append(("curso", "cluster_curso"))
        for nome, col in variantes:
            cl = r["_grupos"][col].to_numpy()
            sc = score_efetivo_por_cluster(r["_X"], r["_conj"], r["_esc"], r["_exc"], k, 0.0, cl)
            G = len(sc)
            t_score = float(sc.sum() / math.sqrt((sc ** 2).sum()))
            for tipo in ("rademacher", "webb"):
                pb, metodo, n = p_score_bootstrap(sc, tipo)
                rob.append(_linha_rob(f"score_bootstrap_{tipo}_cluster_{nome}", ciclo, "p_H0_beta_igual_0", pb,
                                      p=pb, g=G, n_reamostras=n,
                                      metodo=f"Kline–Santos, pesos {tipo}, studentizado; {metodo}",
                                      nota=f"estatística de score observada (t) = {t_score:.6g}"))
            e3, G3, nota3 = ep_cv3(r, k, cl)
            b = float(r["theta"][k])
            ok3 = nota3 == ""
            rob.append(_linha_rob(f"cv3_cluster_{nome}", ciclo, "coef_ep_cv3", b, ep=e3, g=G3,
                                  ic95_inf=b - stats.t.ppf(0.975, G3 - 1) * e3 if ok3 else float("nan"),
                                  ic95_sup=b + stats.t.ppf(0.975, G3 - 1) * e3 if ok3 else float("nan"),
                                  p=float(2 * stats.t.sf(abs(b / e3), G3 - 1)) if ok3 else float("nan"),
                                  metodo="jackknife por cluster (CV3); IC e p pela t com G − 1 gl",
                                  nota=nota3 or f"p pela normal: {float(2 * stats.norm.sf(abs(b / e3))):.6g}"))
            if ciclo in ("2", "empilhado"):
                lo, hi, nota_ic = ic_inversao_score(r, k, cl, "rademacher")
                rob.append(_linha_rob(f"ic_inversao_score_rademacher_cluster_{nome}", ciclo, "coef_ic95_inversao", b,
                                      ic95_inf=lo, ic95_sup=hi, g=G,
                                      n_reamostras=2 ** G if G <= G_MAX_ENUMERACAO else N_REAMOSTRAS,
                                      metodo="inversão do score bootstrap Rademacher (mesmos pesos em todo beta0)",
                                      nota=nota_ic))

    # 3. Forma funcional: segmentos cúbicos, nós a cada 0,05, conjuntos restritos a janelas em torno dos cortes.
    variantes_ff = [("spline_cubico__bolsa_linear", 3, (), None),
                    ("nos_cada_0050__spline_linear__bolsa_linear", 1, NOS_EXTRAS_MIL, None)]
    for h in JANELAS_MIL:
        variantes_ff += [(f"janela_{h:04d}__spline_linear__bolsa_linear", 1, (), h),
                         (f"janela_{h:04d}__spline_cubico__bolsa_linear", 3, (), h)]
    contagem_janelas: dict[str, dict] = {}
    for ciclo in CICLOS:
        conj_c = conj_p[conj_p["ciclo"].isin(_ciclos_int(ciclo))].reset_index(drop=True)
        cand_c = cand[cand["ciclo"].isin(_ciclos_int(ciclo))]
        for nome, grau, nos, h in variantes_ff:
            if h is None:
                cj, cd, nota_j = conj_c, cand_c, ""
                if nos:
                    ultimo = max(nos)
                    r1 = cand_c[cand_c["opcao_rank"] == 1].merge(conj_c[["ciclo", "co_cnes_7d", "cod_curso", "s_mil"]],
                                                                 on=["ciclo", "co_cnes_7d", "cod_curso"], how="left")
                    nota_j = (f"acima do último nó ({ultimo / 1000:.3f}): {int((conj_c['s_mil'] > ultimo).sum())} células, "
                              f"{int((r1['s_mil'] > ultimo).sum())} escolhidas como 1a opção")
            else:
                dentro = np.zeros(len(conj_c), dtype=bool)
                for c in CORTES_MIL:
                    dentro |= (conj_c["s_mil"] - c).abs().to_numpy() <= h
                cj = conj_c[dentro].reset_index(drop=True)
                chaves = set(zip(cj["ciclo"], cj["co_cnes_7d"], cj["cod_curso"]))
                r1 = cand_c[cand_c["opcao_rank"] == 1]
                no_jan = np.array([(a, b_, c_) in chaves
                                   for a, b_, c_ in zip(r1["ciclo"], r1["co_cnes_7d"], r1["cod_curso"])], dtype=bool)
                cd = r1[no_jan]
                nota_j = (f"janela |IVS − corte| <= {h / 1000:.3f}: {int(dentro.sum())} de {len(conj_c)} células; "
                          f"{int(no_jan.sum())} de {len(r1)} candidatos com a 1a opção na janela")
                contagem_janelas[f"{ciclo}|{nome}"] = {"celulas": int(dentro.sum()), "candidatos": int(no_jan.sum())}
            r = estimar(cj, cd, MODELO_COND, "principal", nome, macros, estratos, grau=grau, forma="linear",
                        nos_extras_mil=nos)
            r = _rotular(r, nome)
            vif = r["colinearidade"].get("bolsa_mil", {}).get("vif", float("nan"))
            nota_j = "; ".join(x for x in (nota_j, f"VIF da bolsa contra spline e controles = {vif:.4g}") if x)
            r["nota"] = "; ".join(x for x in (r["nota"], nota_j) if x)
            est_rows += linhas_estimativas(ciclo, r)
    resumo["janelas"] = contagem_janelas

    # 4. Cortes placebo: degrau falso + nó no corte falso, com a bolsa verdadeira no modelo.
    placebo_resumo = {}
    for ciclo in CICLOS:
        conj_c = conj_p[conj_p["ciclo"].isin(_ciclos_int(ciclo))].reset_index(drop=True)
        cand_c = cand[cand["ciclo"].isin(_ciclos_int(ciclo))]
        ts = []
        for c in PLACEBOS_MIL:
            nome = f"placebo_{c:04d}__spline_linear__bolsa_linear"
            r = _rotular(estimar(conj_c, cand_c, MODELO_COND, "principal", nome, macros, estratos, grau=1,
                                 forma="linear", placebo_mil=c), nome)
            linhas = [x for x in linhas_estimativas(ciclo, r) if x["termo"] in ("degrau_placebo", "bolsa_mil")]
            est_rows += linhas
            lp = [x for x in linhas if x["termo"] == "degrau_placebo"]
            if lp and np.isfinite(lp[0]["coef"]):
                ts.append(lp[0]["coef"] / lp[0]["ep_cluster_conjunto"])
        rp = principal(ciclo)
        kb = rp["termos"].index("bolsa_mil")
        t_real = float(rp["theta"][kb] / math.sqrt(rp["V_conj"][kb, kb]))
        ts = np.array(ts)
        n_maior = int((np.abs(ts) >= abs(t_real)).sum())
        p_posto = (1 + n_maior) / (1 + len(ts))
        placebo_resumo[ciclo] = {"n_placebos": int(len(ts)), "t_real": t_real, "t_placebo_media": float(ts.mean()),
                                 "t_placebo_dp": float(ts.std(ddof=1)),
                                 "fracao_abs_t_placebo_maior_que_1_96": float(np.mean(np.abs(ts) > Z95)),
                                 "n_abs_t_placebo_maior_ou_igual_ao_real": n_maior, "p_posto": p_posto,
                                 "abs_t_placebo_max": float(np.abs(ts).max())}
        for est_nome, v in placebo_resumo[ciclo].items():
            rob.append(_linha_rob("placebo_cortes", ciclo, est_nome, v,
                                  p=p_posto if est_nome == "p_posto" else float("nan"),
                                  metodo=("cortes falsos de 0,190 a 0,510 a cada 0,010, sem 0,290–0,310 e 0,390–0,410; "
                                          "t do degrau falso com EP cluster por conjunto; t real = t da bolsa no "
                                          "principal; p por posto = (1 + #|t_placebo| >= |t_real|)/(1 + N)")))
    resumo["placebos_mil"] = list(PLACEBOS_MIL)

    # 5. Heterogeneidade entre ciclos.
    nome13 = "ciclos_1_e_3_empilhados__spline_linear__bolsa_linear"
    conj_13 = conj_p[conj_p["ciclo"].isin([1, 3])].reset_index(drop=True)
    r13 = _rotular(estimar(conj_13, cand[cand["ciclo"].isin([1, 3])], MODELO_COND, "principal", nome13, macros,
                           estratos, grau=1, forma="linear"), nome13)
    est_rows += linhas_estimativas("1+3", r13)
    bs, es = [], []
    for ciclo in ("1", "2", "3"):
        r = principal(ciclo)
        k = r["termos"].index("bolsa_mil")
        bs.append(float(r["theta"][k]))
        es.append(math.sqrt(r["V_conj"][k, k]))
    bs, es = np.array(bs), np.array(es)
    w = 1 / es ** 2
    bbar = float((w * bs).sum() / w.sum())
    Q = float((w * (bs - bbar) ** 2).sum())
    gl = len(bs) - 1
    pQ = float(stats.chi2.sf(Q, gl))
    I2 = max(0.0, (Q - gl) / Q) if Q > 0 else 0.0
    rob.append(_linha_rob("heterogeneidade_ciclos", "1,2,3", "cochran_Q", Q, p=pQ, g=gl,
                          metodo="Q de Cochran com pesos 1/EP² (EP cluster por conjunto); g = graus de liberdade",
                          nota=f"média ponderada = {bbar:.6g}; I² = {I2:.6g}"))
    z = float((bs[1] - bs[2]) / math.sqrt(es[1] ** 2 + es[2] ** 2))
    rob.append(_linha_rob("heterogeneidade_ciclos", "2 vs 3", "z_ciclo2_menos_ciclo3", z,
                          ep=float(math.sqrt(es[1] ** 2 + es[2] ** 2)), p=float(2 * stats.norm.sf(abs(z))),
                          metodo="z = (b2 − b3)/sqrt(EP2² + EP3²), EP cluster por conjunto; trata os ciclos como "
                                 "amostras independentes (candidatos distintos; células podem se repetir)",
                          nota=f"b2 − b3 = {bs[1] - bs[2]:.6g}"))
    resumo["placebo"] = placebo_resumo
    resumo["cochran_Q"] = {"Q": Q, "gl": gl, "p": pQ, "I2": I2}
    return est_rows, rob, resumo


# --------------------------------------------------------------------------
# Execução
# --------------------------------------------------------------------------

def bloco_entrada(caminho: Path, papel: str, data_ref: str, cobertura: str, unidade: str, chaves: str,
                  filtros: str) -> dict:
    return {"caminho": rel(caminho), "sha256": sha256_arquivo(caminho), "bytes": caminho.stat().st_size,
            "papel": papel, "fonte": "pipeline do repositório", "data_referencia": data_ref, "cobertura": cobertura,
            "unidade": unidade, "chaves": chaves, "filtros": filtros}


def conferir_insumos(dic: dict) -> dict:
    """Os parquets da tarefa B têm de ser os do dicionário (SHA-256); o protocolo, o congelado."""
    out = {}
    for nome, caminho in (("escolhas_candidatos", ESCOLHAS), ("escolhas_conjunto_principal", CONJ_PRINCIPAL),
                          ("escolhas_conjunto_sensibilidade_vaga_imediata", CONJ_SENSIBILIDADE)):
        sha = sha256_arquivo(caminho)
        if sha != dic["saidas"][nome]["sha256"]:
            raise AssertionError(f"{rel(caminho)} difere do SHA-256 registrado no dicionário da tarefa B")
        out[nome] = True
    prot = json.loads(PROTOCOLO_JSON.read_text(encoding="utf-8"))
    if sha256_arquivo(PROTOCOLO_MD) != prot["sha256_texto_canonico"]:
        raise AssertionError("texto do protocolo 40 difere do SHA-256 congelado no JSON")
    if not any(a.get("antes_de_estimar_E9") and "E9_forma_funcional" in a for a in prot["adendos"]):
        raise AssertionError("protocolo sem o adendo de forma funcional do E9 (§15)")
    out["protocolo_texto_igual_ao_congelado"] = True
    return out


def main() -> int:
    dic = json.loads(DICIONARIO.read_text(encoding="utf-8"))
    conferencias = conferir_insumos(dic)
    mapa, prov_mapa = mapa_bolsa_por_faixa()
    ivs = carregar_ivs()
    cand = pd.read_parquet(ESCOLHAS)
    if not (cand["natureza_dos_dados"] == NATUREZA).all():
        raise AssertionError("escolhas com natureza diferente de EMPIRICO")
    conj_p, diag_p = preparar_conjunto(pd.read_parquet(CONJ_PRINCIPAL), ivs, mapa)
    conj_s, diag_s = preparar_conjunto(pd.read_parquet(CONJ_SENSIBILIDADE), ivs, mapa)
    if (conj_s["tem_vaga_imediata"] != 1).any():
        raise AssertionError("conjunto de sensibilidade com célula sem vaga imediata")
    macros = sorted(conj_p["macrorregiao"].unique())
    estratos = sorted(conj_p["estrato_territorial"].unique())
    cursos = rotulos_cursos()
    faltam = sorted(set(map(str, conj_p["cod_curso"].unique())) - set(cursos["codigos"]))
    if faltam:
        raise AssertionError(f"códigos de curso do conjunto sem rótulo nos quadros: {faltam}")
    # Escolha de célula retirada (sem IVS) faz parar: não se descarta escolha observada em silêncio.
    for d in diag_p["alternativas_retiradas_sem_ivs"]:
        hit = cand[(cand.ciclo == d["ciclo"]) & (cand.co_cnes_7d == d["co_cnes_7d"]) & (cand.cod_curso == d["cod_curso"])]
        d["linhas_de_escolha_nessa_celula"] = int(len(hit))
        if len(hit):
            raise AssertionError(f"célula sem IVS escolhida por candidato: {d}")

    conjuntos = {"principal": conj_p, "sensibilidade": conj_s}
    resultados: dict[tuple, dict] = {}
    est_linhas: list[dict] = []
    efe_linhas: list[dict] = []
    for ciclo in CICLOS:
        ciclos_int = [1, 2, 3] if ciclo == "empilhado" else [int(ciclo)]
        for modelo, conjunto in COMBINACOES:
            conj = conjuntos[conjunto]
            conj_c = conj[conj["ciclo"].isin(ciclos_int)].reset_index(drop=True)
            cand_c = cand[cand["ciclo"].isin(ciclos_int)]
            for espec in ESPECIFICACOES:
                r = estimar(conj_c, cand_c, modelo, conjunto, espec, macros, estratos)
                resultados[(ciclo, modelo, conjunto, espec)] = r
                est_linhas += linhas_estimativas(ciclo, r)
                efe_linhas += linhas_efeitos(ciclo, r)
                print(f"ciclo {ciclo:9s} {modelo:28s} {conjunto:13s} {espec:38s} ok={r['ok']} "
                      f"it={r.get('iteracoes')} n={r['n_candidatos']}", flush=True)

    # Robustez pós-auditoria (pós-resultado, fora do protocolo): linhas próprias, rotuladas.
    est_rob, rob_linhas, resumo_rob = robustez_pos_auditoria(conj_p, cand, macros, estratos, resultados)
    est_linhas += est_rob
    rob = pd.DataFrame(rob_linhas)
    sem = rob[rob[["valor"]].isna().any(axis=1) & (rob["nota"].fillna("") == "")]
    if len(sem):
        raise AssertionError(f"robustez: {len(sem)} linhas com NaN sem nota")
    print(f"robustez pós-auditoria: {len(est_rob)} linhas de estimativas, {len(rob)} linhas de inferência/resumo")

    est = pd.DataFrame(est_linhas)
    efe = pd.DataFrame(efe_linhas)
    # Nenhum NaN sem nota.
    for nome, df, cols in (("estimativas", est, ["coef", "ep_cluster_conjunto", "ep_mle", "ep_cluster_candidato", "p"]),
                           ("efeitos", efe, ["estimativa"])):
        sem = df[df[cols].isna().any(axis=1) & (df["nota"].fillna("") == "")]
        if len(sem):
            raise AssertionError(f"{nome}: {len(sem)} linhas com NaN sem nota")
    ordem_est = ["natureza_dos_dados", "ciclo", "conjunto", "modelo", "especificacao", "no_protocolo",
                 "papel_no_protocolo", "termo", "coef", "ep_cluster_conjunto", "ep_mle", "ep_cluster_candidato",
                 "ic95", "ic95_inf", "ic95_sup", "p", "p_t_g_menos_1", "g_conjuntos", "g_candidatos", "n_candidatos",
                 "n_grupos_escolha", "n_conjuntos", "n_alternativas", "log_verossimilhanca", "iteracoes", "convergiu",
                 "nota"]
    est = est[ordem_est]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    est.to_csv(OUT_ESTIMATIVAS, index=False, float_format="%.10g")
    efe.to_csv(OUT_EFEITOS, index=False, float_format="%.10g")
    rob.to_csv(OUT_ROBUSTEZ, index=False, float_format="%.10g")

    # Diagnósticos por ciclo (principal).
    diag_ciclo, coli, convergencia = {}, {}, {}
    for ciclo in CICLOS:
        ciclos_int = [1, 2, 3] if ciclo == "empilhado" else [int(ciclo)]
        r = resultados[(ciclo, MODELO_COND, "principal", "spline_linear__bolsa_linear")]
        conj_c = conj_p[conj_p["ciclo"].isin(ciclos_int)]
        tam = conj_c.groupby("id_conjunto_escolha").size()
        diag_ciclo[ciclo] = {"n_candidatos": r["n_candidatos"], "n_conjuntos": r["n_conjuntos"],
                             "n_alternativas": r["n_alternativas"], "alt_min": int(tam.min()),
                             "alt_mediana": float(tam.median()), "alt_max": int(tam.max()),
                             "sem_1a_opcao": r["diag_grupos"]["candidatos_sem_linha_de_1a_opcao_excluidos"],
                             "alternativas_por_conjunto": {k: int(v) for k, v in tam.items()}}
        coli[ciclo] = r["colinearidade"]
        for (cc, m, cj, e), rr in resultados.items():
            if cc == ciclo:
                convergencia[f"{cc}|{m}|{cj}|{e}"] = {"ok": rr["ok"], "iteracoes": rr.get("iteracoes"),
                                                      "grad_max": rr.get("grad_max"), "omitidas": rr["omitidas"],
                                                      "diag_grupos": rr["diag_grupos"]}

    # Continuidade do spline por construção: salto de nível nos nós é zero.
    eps = 1e-9
    continuidade = {}
    for grau in (1, 2, 3):
        for c in CORTES_MIL:
            esq = base_spline(np.array([c - eps]), grau).to_numpy()[0]
            dir_ = base_spline(np.array([c + eps]), grau).to_numpy()[0]
            continuidade[f"grau{grau}_no_{c}"] = float(np.max(np.abs(dir_ - esq)))
    for c in NOS_EXTRAS_MIL:
        esq = base_spline(np.array([c - eps]), 1, NOS_EXTRAS_MIL).to_numpy()[0]
        dir_ = base_spline(np.array([c + eps]), 1, NOS_EXTRAS_MIL).to_numpy()[0]
        continuidade[f"nos_extras_no_{c}"] = float(np.max(np.abs(dir_ - esq)))
    if max(continuidade.values()) > 1e-6:
        raise AssertionError(f"spline com salto de nível: {continuidade}")

    # Bolsa × faixa: a bolsa é função exata da faixa impressa, logo bolsa linear e indicadores de faixa não entram
    # juntos; o modelo de degraus é o de indicadores de faixa (bolsa = 10 + 5·d300 + 5·d400).
    td = termos_bolsa(conj_p, "degraus")
    recomposta = mapa["FAIXA 3"] + PASSO_BOLSA_MIL * td["degrau_0300"] + PASSO_BOLSA_MIL * td["degrau_0400"]
    M = np.column_stack([conj_p["bolsa_mil"], np.ones(len(conj_p)), td["degrau_0300"], td["degrau_0400"]])
    bolsa_faixa = {"bolsa_igual_faixa3_mais_5_d300_mais_5_d400": bool(np.allclose(recomposta, conj_p["bolsa_mil"])),
                   "posto_de_[bolsa, 1, d300, d400]": int(np.linalg.matrix_rank(M)),
                   "leitura": "a bolsa é função exata da faixa (3 valores); a especificação de degraus é a de "
                              "indicadores de faixa, e a bolsa linear impõe degraus iguais"}
    if not bolsa_faixa["bolsa_igual_faixa3_mais_5_d300_mais_5_d400"]:
        raise AssertionError("bolsa não se recompõe pelos degraus")

    gravar_figura(resultados, mapa)
    tabelas = tabelas_relato(est, efe, diag_ciclo, coli, rob)
    OUT_TABELAS.write_text(tabelas, encoding="utf-8")

    entradas = [
        bloco_entrada(PROTOCOLO_JSON, "protocolo congelado (E9: §12, §14, §15)", "2026-10-18", "-", "documento", "-", "-"),
        bloco_entrada(PROTOCOLO_MD, "texto canônico do protocolo 40", "2026-10-18", "-", "documento", "-", "-"),
        bloco_entrada(DICIONARIO, "dicionário da tarefa B (SHA-256 das tabelas de escolha conferido)", "2026-10-18",
                      "-", "documento", "-", "-"),
        bloco_entrada(ESCOLHAS, "escolhas dos candidatos (1a e 2a opção) da 1a chamada dos ciclos 1-3",
                      "resultados da 1a chamada (ver dicionário)", f"{len(cand)} linhas", "candidato × opção",
                      "ciclo, id_candidato, opcao_rank, co_cnes_7d, cod_curso",
                      "posto 1 (condicional); postos 1 e 2 (explodido); sensibilidade: 1a opção com vaga imediata"),
        bloco_entrada(CONJ_PRINCIPAL, "conjunto de escolha principal (§14)", "quadros da 1a chamada (ver dicionário)",
                      f"{len(conj_p) + len(diag_p['alternativas_retiradas_sem_ivs'])} células", "célula CNES × curso × ciclo",
                      "ciclo, co_cnes_7d, cod_curso", "retiradas as células sem IVS oficial (listadas)"),
        bloco_entrada(CONJ_SENSIBILIDADE, "conjunto de sensibilidade: só vaga imediata (§12, §14)",
                      "quadros da 1a chamada (ver dicionário)",
                      f"{len(conj_s) + len(diag_s['alternativas_retiradas_sem_ivs'])} células",
                      "célula CNES × curso × ciclo", "ciclo, co_cnes_7d, cod_curso",
                      "retiradas as células sem IVS oficial (listadas)"),
        bloco_entrada(IVS_OFICIAL, "running variable: IVS 2010 oficial do Ipea (a08)", "IVS 2010",
                      f"{len(ivs)} municípios", "município", "co_ibge", "colunas co_ibge e ivs"),
        bloco_entrada(GRADES_EDITAIS, "grades faixa → bolsa dos editais 2025 e 2026 (só mapeamento_regras_por_edital; "
                      "nenhum IVS deste arquivo é lido)", "editais 3/2025, 1/2026 e 28/2026", "3 faixas × 2 grades",
                      "faixa", "faixa_1..3", "bloco mapeamento_regras_por_edital"),
        bloco_entrada(GRADE_2025, "grade 2025 da FAQ do edital 3/2025 (conferência do mapa faixa → bolsa)",
                      "FAQ do Chamamento SGTES/MS 3/2025", "3 faixas", "faixa", "faixa_atracao",
                      "valor_anunciado_mensal_brl"),
        bloco_entrada(MANIFESTO_A11, "manifesto da aquisição do resultado da 1a chamada do ciclo 2 (condição do §12 "
                      "para o ciclo 2: fonte oficial)", "captura de 2026-10-18", "1 publicação", "documento", "-", "-"),
    ] + [bloco_entrada(caminho, f"quadro da 1a chamada do ciclo {k}: só a coluna CURSO, para conferir que o código do "
                       "curso tem o mesmo rótulo nos três ciclos (cluster por curso, robustez pós-auditoria)",
                       f"quadro da 1a chamada do ciclo {k}", "todas as linhas", "linha do quadro", "CURSO",
                       "coluna CURSO") for k, caminho in QUADROS_1A_CHAMADA.items()]
    prot = json.loads(PROTOCOLO_JSON.read_text(encoding="utf-8"))
    principal = {}
    for ciclo in CICLOS:
        e = est[(est.ciclo == ciclo) & (est.modelo == MODELO_COND) & (est.conjunto == "principal") &
                (est.especificacao == "spline_linear__bolsa_linear") & (est.termo == "bolsa_mil")].iloc[0]
        f = efe[(efe.ciclo == ciclo) & (efe.modelo == MODELO_COND) & (efe.conjunto == "principal") &
                (efe.especificacao == "spline_linear__bolsa_linear") & (efe.termo == "bolsa_mil")].set_index("quantidade")
        principal[ciclo] = {"coef_bolsa_por_mil": e.coef, "ep_cluster_conjunto": e.ep_cluster_conjunto, "p": e.p,
                            "p_t_g_menos_1": e.p_t_g_menos_1,
                            "razao_chances_por_5mil": f.loc["razao_chances_por_5mil", "estimativa"],
                            "variacao_prob_media_pp": f.loc["variacao_prob_media_pp", "estimativa"],
                            "variacao_prob_media_pp_ic95": [f.loc["variacao_prob_media_pp", "ic95_inf"],
                                                            f.loc["variacao_prob_media_pp", "ic95_sup"]]}
    resumo = {
        "natureza_dos_dados": NATUREZA,
        "documento": "E9 do protocolo 40: escolha revelada dos candidatos (logit condicional e explodido)",
        "data_execucao": DATA_EXECUCAO,
        "script": rel(Path(__file__)),
        "protocolo": {"arquivo": rel(PROTOCOLO_JSON), "sha256": sha256_arquivo(PROTOCOLO_JSON),
                      "texto_canonico": rel(PROTOCOLO_MD), "sha256_texto_canonico": sha256_arquivo(PROTOCOLO_MD),
                      "sha256_texto_canonico_congelado": prot["sha256_texto_canonico"],
                      "secoes": ["§12", "§13", "§14", "§15"]},
        "conferencias": {**conferencias, "faixa_impressa_igual_regra_ivs_principal": diag_p["faixa_impressa_igual_regra_ivs"],
                         "faixa_impressa_igual_regra_ivs_sensibilidade": diag_s["faixa_impressa_igual_regra_ivs"],
                         "spline_continuo_salto_maximo_nos_nos": continuidade,
                         "bolsa_contra_faixa": bolsa_faixa},
        "estimando": ("efeito da bolsa anunciada (+R$ 5 mil, incentivo marginal) sobre a ESCOLHA da 1a opção entre as "
                      "células do mesmo curso e ciclo (realocação entre municípios); não é efeito sobre o total de "
                      "candidatos, nem efeito da participação no PMM-E ou do Agora Tem Especialistas"),
        "identificacao": ("a bolsa é identificada só pelos degraus em 0,300 e 0,400, porque o IVS entra como spline "
                          "contínuo (sem salto de nível); a faixa impressa reproduz a regra de dois cortes do IVS "
                          "oficial em todas as células"),
        "limites": [
            "sem residência do candidato: distância não entra",
            "outras políticas nos mesmos cortes (protocolo §13, auditoria 18): nos atos arquivados, nenhuma além da "
            "bolsa paga o especialista do PMM-E por faixa de IVS; o +20% de teto de emendas e custeio da MAC com "
            "IVS > 0,3 pode mudar a estrutura do serviço (o degrau em 0,300 pode carregar isso); fica aberta, não "
            "verificada, a ajuda de custo do PMMB, que muda em 0,400, alcançar o participante do PMM-E (art. 22-D, "
            "§ 2º, da Lei 12.871), o que somaria remuneração ao degrau de 0,400",
            "poucos conjuntos de escolha por ciclo (G pequeno): o EP de cluster por conjunto é impreciso; relata-se "
            "também o p pela t com G − 1 gl, o EP de máxima verossimilhança e o de cluster por candidato",
            "IIA do logit condicional; o explodido acrescenta a hipótese de que a 2a opção é a melhor do restante",
        ],
        "mapa_faixa_bolsa": prov_mapa,
        "categorias_de_base": {"macrorregiao": BASE_MACRO, "estrato_territorial": BASE_ESTRATO,
                               "macrorregioes": macros, "estratos": estratos},
        "parametrizacao_spline": {"unidade": "0,1 de IVS", "centro": CENTRO_IVS_MIL / 1000, "nos": [c / 1000 for c in CORTES_MIL],
                                  "linear": ["ivs_inclinacao", "ivs_mudanca_inclinacao_0300", "ivs_mudanca_inclinacao_0400"],
                                  "quadratico_acrescenta": ["ivs_quadrado", "ivs_quadrado_apos_0300", "ivs_quadrado_apos_0400"]},
        "inferencia": {"principal": "sanduíche com cluster por conjunto de escolha (curso × ciclo), fator G/(G−1); "
                                    "IC 95% e p pela normal; p também pela t com G − 1 gl",
                       "adicionais": ["máxima verossimilhança (inversa da informação)", "cluster por candidato"],
                       "efeito_probabilidade": "delta com gradiente numérico central e a matriz de cluster por conjunto",
                       "razao_chances": "exp do IC do log da razão de chances"},
        "diagnosticos_por_ciclo": diag_ciclo,
        "colinearidade_principal": coli,
        "alternativas_retiradas": {"principal": diag_p["alternativas_retiradas_sem_ivs"],
                                   "sensibilidade": diag_s["alternativas_retiradas_sem_ivs"]},
        "convergencia": convergencia,
        "resultado_principal": principal,
        "n_modelos": int(len(resultados)),
        "n_modelos_ok": int(sum(r["ok"] for r in resultados.values())),
        "desvios": [
            {"data": "2026-10-18", "item": "alternativa sem IVS oficial",
             "situacao": "uma célula do quadro do ciclo 3 fica num município sem IVS 2010 oficial (criado depois de 2010)",
             "resolucao": "retirada do conjunto de escolha (principal e, se houver, sensibilidade) e listada em "
                          "alternativas_retiradas; ninguém a escolheu (conferido; o script para se alguém a tiver escolhido)"},
            {"data": "2026-10-18", "item": "candidatos sem linha de 1a opção",
             "situacao": "pessoas listadas só com a linha de 2a opção no resultado publicado (dicionário da tarefa B)",
             "resolucao": "excluídas de todos os modelos: a 1a opção é desconhecida; contagem por ciclo em diagnosticos_por_ciclo"},
            {"data": "2026-10-18", "item": "tem_vaga_imediata no conjunto de sensibilidade",
             "situacao": "constante (= 1) por construção do conjunto (§14)",
             "resolucao": "omitida do modelo nesse conjunto (não identificada); registrada na nota de cada linha"},
            {"data": "2026-10-18", "item": "logit explodido",
             "situacao": "o §12 fixa a 2a opção como sensibilidade; o §14 trocou o conjunto principal",
             "resolucao": "explodido estimado no conjunto principal; a combinação explodido × conjunto só com vaga "
                          "imediata não é estimada (não listada no protocolo)"},
            {"data": "2026-10-18", "item": "p pela t com G − 1 gl",
             "situacao": "não previsto no §15",
             "resolucao": "relatado ao lado do p normal por causa do número pequeno de conjuntos; não substitui o principal"},
            {"data": "2026-10-19", "item": "robustez pós-auditoria",
             "situacao": "a auditoria independente do E9 (commit 9646b57) reproduziu os números e pediu, depois de ver "
                         "os resultados, cluster por curso, score bootstrap, CV3, IC por inversão, forma funcional, "
                         "janelas, cortes placebo e heterogeneidade entre ciclos",
             "resolucao": f"estimado e gravado em linhas '{TAG_ROB}' com no_protocolo = False; não substitui o protocolo"},
            {"data": "2026-10-19", "item": "critério de parada do Newton–Raphson",
             "situacao": "o critério de gradiente absoluto declarava não convergência por arredondamento em dois "
                         "placebos do empilhado",
             "resolucao": "parada pelo decremento de Newton e teste de subida com tolerância relativa; as estimativas "
                          "do protocolo não mudam além do arredondamento da gravação"},
            {"data": "2026-10-19", "item": "spline com nós a cada 0,05, ciclo 3",
             "situacao": "nenhuma célula acima do último nó (0,700) foi escolhida como 1a opção",
             "resolucao": "o termo desse trecho diverge (separação); a linha é relatada com nota, sem retirar o nó"},
        ],
        "entradas": entradas,
        "saidas": {rel(p): sha256_arquivo(p) for p in (OUT_ESTIMATIVAS, OUT_EFEITOS, OUT_ROBUSTEZ, OUT_TABELAS,
                                                         OUT_FIGURA)},
        "robustez_pos_auditoria": {
            "estado": PAPEL_ROB,
            "rotulo": f"linhas com especificacao começando por '{TAG_ROB}' e no_protocolo = False, em "
                      f"{rel(OUT_ESTIMATIVAS)} (modelos) e {rel(OUT_ROBUSTEZ)} (inferência e resumos)",
            "itens": ["1: empilhado com cluster por curso", "2: score bootstrap de Kline–Santos (Rademacher, Webb), "
                      "CV3 e IC por inversão", "3: segmentos cúbicos, nós a cada 0,05 e janelas de ±0,10, ±0,05 e "
                      "±0,025 em torno dos cortes", "4: cortes placebo", "5: ciclos 1 e 3 empilhados, Q de Cochran, "
                      "z do ciclo 2 contra o 3"],
            "semente": SEMENTE_BOOT, "reamostras_quando_nao_enumera": N_REAMOSTRAS,
            "g_max_enumeracao_rademacher": G_MAX_ENUMERACAO,
            "rotulos_cursos": cursos, **resumo_rob},
        "condicao_s12_ciclo2": {"condicao": "§12: ciclo 2 entra se a 1a chamada for obtida de fonte oficial",
                                "cumprida": True,
                                "evidencia": [f["url"] for f in json.loads(MANIFESTO_A11.read_text(encoding="utf-8"))["fontes"]
                                              if f.get("caminho") == "data/raw/pmm_e/resultado-final-pmme-2o-ciclo-25-05.xlsx"],
                                "manifesto": rel(MANIFESTO_A11)},
        "linguagem": ("resultado do E9 é secundário e exploratório (§12); o coeficiente é efeito da bolsa anunciada "
                      "sobre a escolha condicional a candidatar-se, identificado pelos degraus da regra"),
    }
    OUT_RESUMO.write_text(json.dumps(resumo, ensure_ascii=False, indent=2, default=float) + "\n", encoding="utf-8")
    print(f"gravado: {rel(OUT_ESTIMATIVAS)}, {rel(OUT_EFEITOS)}, {rel(OUT_RESUMO)}, {rel(OUT_TABELAS)}, {rel(OUT_FIGURA)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
