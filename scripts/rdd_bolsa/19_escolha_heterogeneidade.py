"""X4 e X5 do protocolo exploratório pós-síntese: heterogeneidade e deslocamento na escolha dos candidatos.

Protocolo: `docs/06_execucao/45_protocolo_exploratorio_pos_sintese.md` (§2 e §3, X4 e X5), congelado em
19/10/2026 antes de abrir estes outcomes. Toda saída leva `estatuto = EXPLORATORIO_POS_SINTESE`: nada aqui
é teste confirmatório, e nada muda o protocolo 40, o E9 ou o Holm das primárias.

Base comum
----------
O modelo de partida é o principal do E9 (protocolo 40, §14 e §15): logit condicional da 1a opção no conjunto
principal (todas as células do curso e ciclo), spline linear contínuo do IVS com nós em 0,300 e 0,400, bolsa
linear em R$ mil e os demais atributos do E9. Preparação dos dados, verossimilhança, sanduíche por cluster e
score bootstrap são importados de `scripts/rdd_bolsa/16_estimar_E9_escolha.py`, sem cópia. O script para se
a reestimação do principal não reproduzir o coeficiente e o EP de `output/rdd_bolsa/E9_estimativas.csv`.

X4 — heterogeneidade da resposta à bolsa
-----------------------------------------
Interações da bolsa com quatro dimensões, cada uma em um modelo próprio, por ciclo e empilhado:
- (a) tercil da pontuação do candidato dentro do ciclo (a pontuação do F4: barema geral nos ciclos 1 e 3,
  pontuação final no ciclo 2). Os tercis são calculados antes da estimação, sobre os candidatos de 1a opção
  do ciclo com pontuação numérica; empate no ponto de corte vai para o tercil de baixo. Quem não tem
  pontuação (os "SEM PRÉ-REQUISITO" do ciclo 1) forma o grupo `sem_pontuacao`: não é imputado. Como a
  pontuação é do candidato, cada conjunto de escolha é replicado por grupo de candidatos (mesmas células,
  coluna de interação própria); a verossimilhança é idêntica à do E9 quando as interações são zero (conferido).
- (b) curso: cada curso com ao menos 100 candidatos de 1a opção na amostra do modelo; os demais juntos
  (`demais_cursos`). O curso é constante dentro do conjunto (curso × ciclo), e o efeito próprio do curso
  varia só nos conjuntos dele: com cluster por conjunto ou curso, o G efetivo de cada termo é 1 por ciclo
  (até 3 empilhado). A inferência por cluster dessa dimensão é degenerada; as linhas são relatadas com o EP
  de máxima verossimilhança e o de cluster por candidato ao lado, ficam marcadas e fora da família BKY.
- (c) escassez pré-programa da especialidade no município da célula: vínculos das CBO do curso
  (`cbos_elegiveis` da ponte curso–CBO) por 10 mil habitantes (Censo 2022), média de 202406 a 202506 no
  painel CNES nacional. Tercis dentro do conjunto de escolha (o candidato compara as células que vê), com
  empate no corte para o tercil de baixo; tercil 1 = mais escasso. Cursos sem ponte (os novos do ciclo 3)
  formam o grupo `sem_ponte_curso_cbo`; município sem cobertura completa no painel, `cobertura_incompleta`.
  Os indicadores de grupo entram também como efeito principal (atributo da célula).
- (d) estrato territorial A2 (base capital, como no E9; os efeitos principais já estão no E9).

Parametrização: bolsa (inclinação do grupo de base) + bolsa × 1[grupo] para os demais. Relatam-se a inclinação
de cada grupo (combinação linear), os termos de interação (diferença para a base) com p do score bootstrap de
Kline–Santos e o Wald da igualdade de todas as inclinações. EPs: cluster por conjunto (principal do E9), por
curso (no empilhado; por ciclo coincide com o conjunto), de máxima verossimilhança e por candidato.

X5 — deslocamento regional
--------------------------
Região de saúde (CIR) do município da célula, da tabela oficial de conversão do TabNet/DATASUS
(`br_regsaud.cnv`, baixada com `--baixar-regioes`; URL, data e SHA-256 em
`output/rdd_bolsa/X5_manifesto_regioes_saude_cir.json`). A malha do repositório só traz a região dos
municípios com ativo do PMM-E (contagem em `conferencias.cir_contra_malha`); usar essa cobertura
condicionaria a um resultado pós-tratamento, e ela fica só como conferência. Município sem CIR na tabela oficial fica fora da amostra do X5 (suas células e
quem as escolheu), sem imputação; o principal do E9 é reestimado nessa amostra para a comparação.
- (i) logit aninhado, ninhos = CIR dentro do curso × ciclo, um parâmetro de dissimilaridade lambda comum,
  estimado por máxima verossimilhança própria (otimização quase-Newton e polimento por Newton com
  hessiana numérica). Relatam-se lambda, a bolsa, o Wald de lambda = 1 e a razão de verossimilhança contra o
  logit condicional. Lambda fora de (0, 1] não é compatível com maximização de utilidade aleatória.
- (ii) atributos de vizinhança: número de outras células da mesma CIR e do mesmo conjunto com bolsa maior;
  variante com o número total de outras células da mesma CIR e do mesmo conjunto como controle; variante com
  a fração (definida só com vizinho; o indicador de ter vizinho entra junto, e a fração vale 0 sem vizinho,
  o que é parametrização e não dado). A proposta A prevê coeficiente negativo.
O coeficiente da bolsa é relatado com e sem esses termos, na mesma amostra.

Testes múltiplos: q de Benjamini–Krieger–Yekutieli (`rdd_lib.qvalores_bky`) dentro do X4 (termos de
interação e Wald, cluster por conjunto, sem a dimensão curso) e dentro do X5 (termos de vizinhança e
Wald de lambda = 1).

Integridade: só lê `output/` e o arquivo bruto oficial da CIR; nada é simulado, imputado ou preenchido. As
constantes são parâmetros do protocolo (cortes, meses do painel, mínimo de 100 candidatos, tercis) e
numéricos. Saídas: `output/rdd_bolsa/X4_estimativas.csv`, `X5_estimativas.csv`, `X4X5_resumo.json` e
`X4X5_tabelas_relato.md`.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import math
import re
import sys
import unicodedata
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import optimize, stats

ROOT = Path(__file__).resolve().parents[2]
DIR_RDD = ROOT / "scripts" / "rdd_bolsa"


def _importar(caminho: Path, nome: str):
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


E9 = _importar(DIR_RDD / "16_estimar_E9_escolha.py", "e9_escolha_x4x5")
L = _importar(DIR_RDD / "rdd_lib.py", "rdd_lib_x4x5")

PROTOCOLO_X = ROOT / "docs" / "06_execucao" / "45_protocolo_exploratorio_pos_sintese.md"
E9_ESTIMATIVAS = ROOT / "output" / "rdd_bolsa" / "E9_estimativas.csv"
E9_RESUMO = ROOT / "output" / "rdd_bolsa" / "E9_resumo.json"
PAINEL_CNES = ROOT / "output" / "aquisicao" / "cnes_nacional" / "painel_municipio_cbo_mes.parquet"
MANIFESTO_PAINEL = ROOT / "output" / "aquisicao" / "a09_manifesto_cnes_nacional.json"
PONTE = ROOT / "output" / "aquisicao" / "ponte_curso_cbo_oficial.json"
MALHA = ROOT / "output" / "aquisicao" / "malha_municipios_regioes_saude.parquet"
CIR_BRUTO = ROOT / "data" / "raw" / "aquisicao" / "territorio" / "datasus_tabnet_br_regsaud.cnv"
CIR_URL = "http://tabnet.datasus.gov.br/cgi/territorio/br_regsaud.cnv"

OUT_DIR = ROOT / "output" / "rdd_bolsa"
OUT_X4 = OUT_DIR / "X4_estimativas.csv"
OUT_X5 = OUT_DIR / "X5_estimativas.csv"
OUT_RESUMO = OUT_DIR / "X4X5_resumo.json"
OUT_TABELAS = OUT_DIR / "X4X5_tabelas_relato.md"
OUT_MANIFESTO_CIR = OUT_DIR / "X5_manifesto_regioes_saude_cir.json"

DATA_EXECUCAO = "2026-10-19"
NATUREZA = "EMPIRICO"
ESTATUTO = "EXPLORATORIO_POS_SINTESE"
Z95 = E9.Z95
CICLOS = E9.CICLOS

# Parâmetros do protocolo (doc 45, §3).
MIN_CANDIDATOS_CURSO = 100
COMPETENCIAS_ESCASSEZ = tuple(f"{a}{m:02d}" for a, m in [(2024, m) for m in range(6, 13)] + [(2025, m) for m in range(1, 7)])
N_TERCIS = 3
POR_HABITANTES = 10_000.0
# Numérica (logit aninhado).
LAMBDA_LIMITES = (1e-3, 50.0)
TOL_GRAD_NL = 1e-5

DIMENSOES = ("nota_tercil", "curso", "escassez_tercil", "estrato")
ROTULO_DIM = {"nota_tercil": "(a) tercil da pontuação do candidato no ciclo",
              "curso": "(b) curso (≥ 100 candidatos de 1a opção; demais juntos)",
              "escassez_tercil": "(c) tercil da escassez pré-programa da especialidade no município (dentro do conjunto)",
              "estrato": "(d) estrato territorial A2"}

sha256_arquivo = E9.sha256_arquivo
rel = E9.rel


def _ciclos_int(ciclo: str) -> list[int]:
    return [1, 2, 3] if ciclo == "empilhado" else [int(ciclo)]


def _p_norm(z: float) -> float:
    return float(2 * stats.norm.sf(abs(z))) if math.isfinite(z) else float("nan")


# --------------------------------------------------------------------------
# Região de saúde (CIR): tabela oficial do TabNet/DATASUS
# --------------------------------------------------------------------------

def adquirir_cir(baixar: bool) -> dict:
    """Baixa a tabela de conversão município → CIR (só com --baixar-regioes) ou confere o arquivo existente."""
    if not CIR_BRUTO.exists():
        if not baixar:
            raise FileNotFoundError(f"{rel(CIR_BRUTO)} ausente: rode com --baixar-regioes (download público do DATASUS)")
        CIR_BRUTO.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(CIR_URL, timeout=120) as resp:
            status = resp.status
            corpo = resp.read()
        if status != 200 or not re.match(rb"^\d+ \d+\s", corpo[:20]):
            raise RuntimeError(f"download da CIR falhou ou veio em formato inesperado (HTTP {status})")
        CIR_BRUTO.write_bytes(corpo)
        manifesto = {"natureza_dos_dados": NATUREZA, "fonte": "DATASUS/MS, TabNet: arquivo de conversão "
                     "territorio/br_regsaud.cnv (Região de Saúde – CIR), referenciado pela definição "
                     "cnes/cnv/estabbr.def ('Região de Saúde (CIR), CODUFMUN, territorio\\br_regsaud.cnv')",
                     "url": CIR_URL, "http_status": status,
                     "data_download_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                     "arquivo": rel(CIR_BRUTO), "sha256": hashlib.sha256(corpo).hexdigest(), "bytes": len(corpo),
                     "nota": ("o FTP do DATASUS (base territorial) não responde pelo proxy; o HTTPS do TabNet recusou a "
                              "conexão; o arquivo veio por HTTP do próprio TabNet. Versão corrente da base "
                              "territorial do TabNet na data do download (não é competência do CNES)"),
                     "script": rel(Path(__file__))}
        OUT_MANIFESTO_CIR.write_text(json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not OUT_MANIFESTO_CIR.exists():
        raise AssertionError(f"{rel(CIR_BRUTO)} sem manifesto de download ({rel(OUT_MANIFESTO_CIR)})")
    manifesto = json.loads(OUT_MANIFESTO_CIR.read_text(encoding="utf-8"))
    if sha256_arquivo(CIR_BRUTO) != manifesto["sha256"]:
        raise AssertionError(f"{rel(CIR_BRUTO)} difere do SHA-256 do manifesto")
    return manifesto


def ler_cir() -> tuple[pd.DataFrame, dict]:
    """Município (6 dígitos) → código e nome da CIR. Linhas 'Ignorado' (faixas de códigos) não entram."""
    linhas = CIR_BRUTO.read_bytes().decode("latin1").splitlines()
    padrao = re.compile(r"^\s*(\d+)\s+(\d{5})\s+(.*?)\s+(\d{6})\s*$")
    reg, ignorado, outras = [], 0, []
    for ln in linhas[1:]:
        m = padrao.match(ln)
        if m:
            reg.append((m.group(4), m.group(2), m.group(3).strip()))
        elif "Ignorado" in ln:
            ignorado += 1
        elif ln.strip():
            outras.append(ln)
    if outras:
        raise AssertionError(f"linhas da CIR fora do formato esperado: {outras[:5]}")
    cir = pd.DataFrame(reg, columns=["co_ibge", "co_cir", "no_cir"])
    if not cir["co_ibge"].is_unique:
        raise AssertionError("município com mais de uma CIR na tabela oficial")
    return cir, {"municipios": int(len(cir)), "regioes": int(cir["co_cir"].nunique()),
                 "linhas_ignorado_faixas": ignorado, "cabecalho": linhas[0].strip()}


def conferir_cir_contra_malha(cir: pd.DataFrame) -> dict:
    """Conferência estrutural: nos municípios em que a malha tem região (só os com ativo do PMM-E), cada região
    da malha cai numa só CIR oficial? (Nomes diferem por convenção; compara-se a partição.)"""
    m = pd.read_parquet(MALHA, columns=["co_ibge_6d", "sg_uf", "no_regiao_saude"])
    m = m[m["no_regiao_saude"].str.strip() != ""]
    x = m.merge(cir, left_on="co_ibge_6d", right_on="co_ibge", how="left")
    sem = x[x["co_cir"].isna()]
    x = x[x["co_cir"].notna()]
    por_reg = x.groupby(["sg_uf", "no_regiao_saude"])["co_cir"].nunique()
    por_cir = x.groupby("co_cir")["no_regiao_saude"].nunique()

    def norm(s: str) -> str:
        return re.sub(r"[^A-Z0-9]", "", unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().upper())

    return {"municipios_com_regiao_na_malha": int(len(m)),
            "municipios_da_malha_sem_cir_oficial": sorted(sem["co_ibge_6d"].tolist()),
            "regioes_da_malha": int(len(por_reg)),
            "regioes_da_malha_em_mais_de_uma_cir": {f"{k[0]}|{k[1]}": int(v) for k, v in por_reg[por_reg > 1].items()},
            "cir_com_mais_de_uma_regiao_da_malha": int((por_cir > 1).sum()),
            "fracao_nomes_iguais_normalizados": float(np.mean([norm(a) == norm(b) for a, b in
                                                               zip(x["no_regiao_saude"], x["no_cir"])])),
            "leitura": "a malha só é conferência (cobertura condicionada a ter ativo do PMM-E); a CIR do X5 é a oficial"}


# --------------------------------------------------------------------------
# Escassez pré-programa (painel CNES nacional)
# --------------------------------------------------------------------------

def escassez_por_celula(conj: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Vínculos das CBO do curso por 10 mil habitantes, média de 202406 a 202506, por célula (município × curso)."""
    ponte = json.loads(PONTE.read_text(encoding="utf-8"))
    cbos = {int(c["cod_curso"]): [str(x) for x in c["cbos_elegiveis"]] for c in ponte["catalogo_cursos"]}
    grupos_cbo = sorted({f"cbo_{x}" for v in cbos.values() for x in v})
    painel = pd.read_parquet(PAINEL_CNES, columns=["co_ibge", "competencia", "grupo", "n_vinculos", "natureza_dos_dados"],
                             filters=[("grupo", "in", grupos_cbo), ("competencia", "in", list(COMPETENCIAS_ESCASSEZ))])
    if not (painel["natureza_dos_dados"] == NATUREZA).all():
        raise AssertionError("painel CNES com natureza diferente de EMPIRICO")
    faltam_grupos = sorted(set(grupos_cbo) - set(painel["grupo"]))
    if faltam_grupos:
        raise AssertionError(f"grupos CBO da ponte ausentes do painel: {faltam_grupos}")
    if painel.duplicated(["co_ibge", "competencia", "grupo"]).any():
        raise AssertionError("painel CNES com chave (co_ibge, competencia, grupo) repetida")
    comps_lidas = sorted(painel["competencia"].unique())
    if tuple(comps_lidas) != COMPETENCIAS_ESCASSEZ:
        raise AssertionError(f"competências do painel diferentes das do protocolo: {comps_lidas}")
    tab = painel.pivot_table(index=["co_ibge", "competencia"], columns="grupo", values="n_vinculos", aggfunc="sum")
    pares = conj[["co_ibge", "cod_curso"]].drop_duplicates()
    linhas = []
    for co_ibge, curso in pares.itertuples(index=False):
        if int(curso) not in cbos:
            linhas.append((co_ibge, curso, np.nan, "sem_ponte_curso_cbo", 0))
            continue
        cols = [f"cbo_{x}" for x in cbos[int(curso)]]
        if co_ibge not in tab.index.get_level_values(0):
            linhas.append((co_ibge, curso, np.nan, "cobertura_incompleta", 0))
            continue
        sub = tab.loc[co_ibge, cols]
        if len(sub) != len(COMPETENCIAS_ESCASSEZ) or sub.isna().any().any():
            linhas.append((co_ibge, curso, np.nan, "cobertura_incompleta", int(sub.notna().all(axis=1).sum())))
            continue
        linhas.append((co_ibge, curso, float(sub.sum(axis=1).mean()), "ok", len(sub)))
    esc = pd.DataFrame(linhas, columns=["co_ibge", "cod_curso", "vinculos_cbo_curso_media", "status_escassez",
                                        "meses_completos"])
    out = conj[["co_ibge", "cod_curso", "populacao_2022"]].merge(esc, on=["co_ibge", "cod_curso"], how="left")
    out["vinculos_por_10mil"] = out["vinculos_cbo_curso_media"] / out["populacao_2022"] * POR_HABITANTES
    diag = {"cbos_por_curso": {str(k): v for k, v in sorted(cbos.items())},
            "cursos_com_cbo_compartilhada": ponte["cursos_sobrepostos"],
            "competencias": list(COMPETENCIAS_ESCASSEZ),
            "pares_municipio_curso": int(len(esc)),
            "status": esc["status_escassez"].value_counts().to_dict(),
            "definicao": (f"soma de n_vinculos das cbos_elegiveis do curso no município, média dos "
                          f"{len(COMPETENCIAS_ESCASSEZ)} meses de {COMPETENCIAS_ESCASSEZ[0]} a {COMPETENCIAS_ESCASSEZ[-1]}, "
                          "por 10 mil habitantes do Censo 2022 (populacao_2022 do conjunto de escolha)")}
    return out.set_index(conj.index), diag


def tercis(x: pd.Series) -> tuple[pd.Series, list[float]]:
    """Tercil 1, 2, 3 pelos pontos de corte de 1/3 e 2/3 (quantil linear); empate no corte vai para baixo."""
    q1, q2 = (float(v) for v in np.quantile(x.to_numpy(dtype=float), [1 / 3, 2 / 3]))
    t = np.where(x <= q1, 1, np.where(x <= q2, 2, 3))
    return pd.Series(t, index=x.index), [q1, q2]


# --------------------------------------------------------------------------
# Ajuste genérico do logit condicional (funções do E9)
# --------------------------------------------------------------------------

def ajustar(X: pd.DataFrame, conj_cel: np.ndarray, grupos: pd.DataFrame) -> dict:
    """Mesmo procedimento do `estimar` do E9 sobre uma matriz de atributos dada: retira colunas sem variação
    dentro dos conjuntos usados, restringe às células desses conjuntos, ajusta e calcula as covariâncias."""
    esc = grupos["idx_escolhida"].to_numpy()
    exc = np.full(len(esc), -1)
    conj_usados = np.unique(conj_cel[esc])
    usadas = np.flatnonzero(np.isin(conj_cel, conj_usados))
    omitidas = E9.colunas_sem_variacao(X, conj_cel, usadas)
    X = X.drop(columns=omitidas)
    remap = -np.ones(len(conj_cel), dtype=int)
    remap[usadas] = np.arange(len(usadas))
    Xu = X.iloc[usadas].reset_index(drop=True)
    _, conj_u = np.unique(conj_cel[usadas], return_inverse=True)
    esc_u = remap[esc]
    Xa = Xu.to_numpy(dtype=float)
    base = {"termos": list(Xu.columns), "omitidas": omitidas, "n_alternativas": int(len(usadas)),
            "n_conjuntos_virtuais": int(len(conj_usados)), "n_escolhas": int(len(esc)),
            "_usadas": usadas}
    posto = np.linalg.matrix_rank(Xa - pd.DataFrame(Xa).groupby(conj_u).transform("mean").to_numpy())
    if posto < Xa.shape[1]:
        return {**base, "ok": False, "nota": f"X sem posto completo ({posto} < {Xa.shape[1]})"}
    try:
        fit = E9.ajustar_logit(Xa, conj_u, esc_u, exc)
    except (np.linalg.LinAlgError, FloatingPointError) as erro:
        return {**base, "ok": False, "nota": f"estimação falhou ({type(erro).__name__})"}
    if not fit["convergiu"]:
        return {**base, "ok": False, "nota": "Newton–Raphson não convergiu", "iteracoes": fit["iteracoes"]}
    info_inv = np.linalg.inv(fit["info"])
    out = {**base, "ok": True, "nota": "", "theta": fit["theta"], "ll": fit["ll"], "iteracoes": fit["iteracoes"],
           "V_mle": info_inv, "_X": Xa, "_conj": conj_u, "_esc": esc_u, "_exc": exc, "_grupos": grupos,
           "_scores": fit["scores"], "_info_inv": info_inv}
    for nome, col in (("conj", "cluster_conjunto"), ("curso", "cluster_curso"), ("cand", "cluster_candidato")):
        V, G = E9.covariancia_cluster(info_inv, fit["scores"], grupos[col].to_numpy())
        out[f"V_{nome}"], out[f"G_{nome}"] = V, G
    return out


def desenho_e9(conj_c: pd.DataFrame, cand_c: pd.DataFrame, macros: list[str], estratos: list[str]) -> dict:
    """Matriz do principal do E9 (spline linear, bolsa linear) e os grupos de escolha da 1a opção."""
    grupos, diag = E9.montar_grupos(cand_c, conj_c, E9.MODELO_COND, "principal")
    _, conj_cel = np.unique(conj_c["id_conjunto_escolha"].to_numpy(), return_inverse=True)
    X = E9.matriz_atributos(conj_c, 1, "linear", macros, estratos)
    r1 = cand_c[cand_c["opcao_rank"] == 1].reset_index(drop=True)
    if not (r1["id_candidato"].to_numpy() == grupos["cluster_candidato"].to_numpy()).all():
        raise AssertionError("ordem dos grupos de escolha diferente da das linhas de 1a opção")
    return {"X": X, "conj_cel": conj_cel, "grupos": grupos, "r1": r1, "diag": diag}


def expandir_por_grupo_de_candidato(X: pd.DataFrame, conj_cel: np.ndarray, grupos: pd.DataFrame,
                                    rotulo_cand: np.ndarray) -> tuple[pd.DataFrame, np.ndarray, pd.DataFrame, np.ndarray]:
    """Replica cada conjunto por grupo de candidato presente nele: os candidatos do grupo g escolhem entre as
    cópias (conjunto, g). Devolve X expandido, conjunto virtual, grupos reindexados e o rótulo de cada linha."""
    esc = grupos["idx_escolhida"].to_numpy()
    pares = pd.DataFrame({"s": conj_cel[esc], "g": rotulo_cand}).drop_duplicates().sort_values(["s", "g"])
    cel_por_conj = pd.Series(np.arange(len(conj_cel))).groupby(conj_cel).apply(np.array)
    blocos, conj_v, rot_v, inicio = [], [], [], {}
    pos = 0
    for k, (s, g) in enumerate(pares.itertuples(index=False)):
        idx = cel_por_conj[s]
        inicio[(s, g)] = (pos, idx)
        blocos.append(idx)
        conj_v.append(np.full(len(idx), k))
        rot_v.append(np.full(len(idx), g, dtype=object))
        pos += len(idx)
    linhas = np.concatenate(blocos)
    Xe = X.iloc[linhas].reset_index(drop=True)
    novo_esc = np.empty(len(esc), dtype=int)
    for i, (j, g) in enumerate(zip(esc, rotulo_cand)):
        p0, idx = inicio[(conj_cel[j], g)]
        novo_esc[i] = p0 + int(np.flatnonzero(idx == j)[0])
    ge = grupos.copy()
    ge["idx_escolhida"] = novo_esc
    return Xe, np.concatenate(conj_v), ge, np.concatenate(rot_v)


# --------------------------------------------------------------------------
# Combinações lineares, Wald e score bootstrap
# --------------------------------------------------------------------------

VS = (("conj", "cluster por conjunto"), ("curso", "cluster por curso"), ("mle", "máxima verossimilhança"),
      ("cand", "cluster por candidato"))


def combinacao(r: dict, a: np.ndarray) -> dict:
    b = float(a @ r["theta"])
    out = {"coef": b}
    for nome, _ in VS:
        ep = math.sqrt(max(float(a @ r[f"V_{nome}"] @ a), 0.0))
        out[f"ep_{nome}"] = ep
        out[f"p_{nome}"] = _p_norm(b / ep) if ep > 0 else float("nan")
    ep = out["ep_conj"]
    out.update({"ic95_inf": b - Z95 * ep, "ic95_sup": b + Z95 * ep,
                "p_t_g_menos_1": float(2 * stats.t.sf(abs(b / ep), r["G_conj"] - 1)) if ep > 0 else float("nan")})
    return out


def wald(r: dict, R: np.ndarray) -> dict:
    d = R @ r["theta"]
    out = {"coef": float("nan")}
    for nome, _ in VS:
        M = R @ r[f"V_{nome}"] @ R.T
        ev = np.linalg.eigvalsh(M)
        posto = int((ev > ev.max() * 1e-10).sum()) if ev.max() > 0 else 0
        W = float(d @ np.linalg.pinv(M, rcond=1e-10) @ d) if posto else float("nan")
        out[f"wald_{nome}"] = W
        out[f"gl_{nome}"] = posto
        out[f"p_{nome}"] = float(stats.chi2.sf(W, posto)) if posto else float("nan")
    G = r["G_conj"]
    q = out["gl_conj"]
    out["p_f_g_menos_1"] = (float(stats.f.sf(out["wald_conj"] / q, q, G - 1)) if q and G - 1 > 0 else float("nan"))
    out["gl_completo"] = int(R.shape[0])
    return out


def score_bootstrap(r: dict, k: int, coluna_cluster: str) -> dict:
    cl = r["_grupos"][coluna_cluster].to_numpy()
    sc = E9.score_efetivo_por_cluster(r["_X"], r["_conj"], r["_esc"], r["_exc"], k, 0.0, cl)
    out = {"g": len(sc)}
    for tipo in ("rademacher", "webb"):
        p, metodo, n = E9.p_score_bootstrap(sc, tipo)
        out[tipo] = p
        out[f"metodo_{tipo}"] = metodo
    return out


def g_efetivo(r: dict, coluna: str, coluna_cluster: str) -> int:
    """Número de clusters em que o termo varia dentro de algum conjunto (virtual) usado."""
    k = r["termos"].index(coluna)
    x = r["_X"][:, k]
    amp = pd.Series(x).groupby(r["_conj"]).agg(lambda s: s.max() - s.min()).to_numpy()
    conj_var = set(np.flatnonzero(amp > 0))
    cl = r["_grupos"][coluna_cluster].to_numpy()
    s_esc = r["_conj"][r["_esc"]]
    return int(len({c for c, s in zip(cl, s_esc) if s in conj_var}))


# --------------------------------------------------------------------------
# X4
# --------------------------------------------------------------------------

def rotular_grupos(dim: str, ciclo: str, des: dict, conj_c: pd.DataFrame, esc_cel: pd.DataFrame) -> dict:
    """Rótulo de grupo por candidato (nível 'candidato') ou por célula (nível 'celula'); base; descrição."""
    r1 = des["r1"]
    if dim == "nota_tercil":
        rot = pd.Series("sem_pontuacao", index=r1.index, dtype=object)
        cortes = {}
        for c in sorted(r1["ciclo"].unique()):
            m = (r1["ciclo"] == c) & r1["pontuacao"].notna()
            t, q = tercis(r1.loc[m, "pontuacao"])
            rot.loc[m] = [f"tercil{int(v)}" for v in t]
            cortes[str(int(c))] = q
        return {"nivel": "candidato", "rotulo": rot.to_numpy(), "base": "tercil1", "cortes": cortes,
                "ordem": ["tercil1", "tercil2", "tercil3", "sem_pontuacao"]}
    if dim == "curso":
        n = r1.groupby("cod_curso").size()
        grandes = sorted(int(k) for k, v in n.items() if v >= MIN_CANDIDATOS_CURSO)
        rot = np.array([f"curso{int(k):02d}" if int(k) in grandes else "demais_cursos" for k in conj_c["cod_curso"]],
                       dtype=object)
        cont = pd.Series([f"curso{int(k):02d}" if int(k) in grandes else "demais_cursos" for k in r1["cod_curso"]]).value_counts()
        base = sorted(cont.index, key=lambda g: (-int(cont[g]), g))[0]
        return {"nivel": "celula", "rotulo": rot, "base": base,
                "ordem": [f"curso{k:02d}" for k in grandes] + ["demais_cursos"],
                "cursos_com_100": grandes, "candidatos_por_curso": {str(int(k)): int(v) for k, v in n.items()}}
    if dim == "escassez_tercil":
        rot = pd.Series(esc_cel["status_escassez"].to_numpy(), index=conj_c.index, dtype=object)
        ok = esc_cel["status_escassez"].to_numpy() == "ok"
        cortes = {}
        for s, idx in conj_c[ok].groupby("id_conjunto_escolha").groups.items():
            t, q = tercis(esc_cel.loc[idx, "vinculos_por_10mil"])
            rot.loc[idx] = [f"tercil{int(v)}" for v in t]
            cortes[s] = q
        return {"nivel": "celula", "rotulo": rot.to_numpy(), "base": "tercil1", "cortes": cortes,
                "ordem": ["tercil1", "tercil2", "tercil3", "sem_ponte_curso_cbo", "cobertura_incompleta"]}
    if dim == "estrato":
        return {"nivel": "celula", "rotulo": conj_c["estrato_territorial"].to_numpy(dtype=object),
                "base": E9.BASE_ESTRATO,
                "ordem": [E9.BASE_ESTRATO] + sorted(set(conj_c["estrato_territorial"]) - {E9.BASE_ESTRATO})}
    raise ValueError(dim)


def estimar_x4(dim: str, ciclo: str, conj_c: pd.DataFrame, cand_c: pd.DataFrame, esc_cel: pd.DataFrame,
               macros: list[str], estratos: list[str]) -> tuple[list[dict], dict]:
    des = desenho_e9(conj_c, cand_c, macros, estratos)
    info = rotular_grupos(dim, ciclo, des, conj_c, esc_cel)
    X, conj_cel, grupos = des["X"].copy(), des["conj_cel"], des["grupos"]
    if info["nivel"] == "candidato":
        X, conj_cel, grupos, rot_linha = expandir_por_grupo_de_candidato(X, conj_cel, grupos, info["rotulo"])
        rot_cand = info["rotulo"]
    else:
        rot_linha = info["rotulo"]
        rot_cand = rot_linha[grupos["idx_escolhida"].to_numpy()]
    presentes = [g for g in info["ordem"] if g in set(rot_linha)]
    base = info["base"]
    if base not in presentes:
        raise AssertionError(f"grupo de base {base} ausente em {dim}, ciclo {ciclo}")
    outros = [g for g in presentes if g != base]
    bolsa = X["bolsa_mil"].to_numpy()
    if dim == "escassez_tercil":  # efeito principal dos grupos de escassez (atributo da célula)
        for g in outros:
            X[f"escassez_{g}"] = (rot_linha == g).astype(float)
    for g in outros:
        X[f"bolsa_x_{g}"] = bolsa * (rot_linha == g)
    r = ajustar(X, conj_cel, grupos)
    resumo = {"dimensao": dim, "ciclo": ciclo, "nivel": info["nivel"], "base": base, "grupos": presentes,
              "ok": r["ok"], "nota": r["nota"], "omitidas": r["omitidas"], "iteracoes": r.get("iteracoes"),
              "n_candidatos": int(len(grupos)), "n_alternativas_originais": int(len(des["X"])),
              "n_conjuntos": int(len(np.unique(grupos["cluster_conjunto"]))),
              **{k: v for k, v in info.items() if k in ("cortes", "cursos_com_100", "candidatos_por_curso")}}
    if not r["ok"]:
        raise AssertionError(f"X4 {dim} ciclo {ciclo}: {r['nota']}")
    degenerada = dim == "curso"
    termos = r["termos"]
    kb = termos.index("bolsa_mil")
    cont_cand = pd.Series(rot_cand).value_counts()
    usadas_rot = rot_linha[r["_usadas"]]
    cont_alt = pd.Series(usadas_rot).value_counts()
    linhas = []
    comuns = {"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "analise": "X4", "dimensao": dim, "ciclo": ciclo,
              "modelo": "logit_condicional_1a_opcao", "conjunto": "principal",
              "especificacao_base": "E9 principal: spline_linear__bolsa_linear", "grupo_base": base,
              "nivel_do_grupo": info["nivel"], "n_candidatos": int(len(grupos)), "g_conjuntos": r["G_conj"],
              "g_cursos": r["G_curso"], "log_verossimilhanca": r["ll"], "iteracoes": r["iteracoes"],
              "inferencia_cluster_degenerada": degenerada}
    nota_deg = ("dimensão curso: cada efeito próprio varia só nos conjuntos do curso (G efetivo na coluna "
                "g_efetivo_conjunto); EP e p por cluster não são confiáveis; ver EP de MV e por candidato")
    for g in presentes:
        a = np.zeros(len(termos))
        a[kb] = 1.0
        if g != base:
            a[termos.index(f"bolsa_x_{g}")] = 1.0
        c = combinacao(r, a)
        linhas.append({**comuns, "tipo_linha": "inclinacao_do_grupo", "termo": f"bolsa_mil|{g}", "grupo": g,
                       **c, "rc_por_5mil": math.exp(5 * c["coef"]),
                       "n_candidatos_grupo": int(cont_cand.get(g, 0)), "n_alternativas_grupo": int(cont_alt.get(g, 0)),
                       "entra_bky": False,
                       "nota": "; ".join(x for x in ["inclinação da bolsa (por R$ 1 mil) no grupo",
                                                     nota_deg if degenerada else ""] if x)})
    R = []
    for g in outros:
        t = f"bolsa_x_{g}"
        k = termos.index(t)
        a = np.zeros(len(termos))
        a[k] = 1.0
        R.append(a)
        c = combinacao(r, a)
        sb = score_bootstrap(r, k, "cluster_conjunto")
        linha = {**comuns, "tipo_linha": "interacao", "termo": t, "grupo": g, **c,
                 "p_score_rademacher_conjunto": sb["rademacher"], "p_score_webb_conjunto": sb["webb"],
                 "metodo_score_conjunto": sb["metodo_rademacher"],
                 "g_efetivo_conjunto": g_efetivo(r, t, "cluster_conjunto"),
                 "n_candidatos_grupo": int(cont_cand.get(g, 0)), "n_alternativas_grupo": int(cont_alt.get(g, 0)),
                 "entra_bky": not degenerada,
                 "nota": "; ".join(x for x in [f"diferença da inclinação do grupo {g} para a do grupo {base}",
                                               nota_deg if degenerada else ""] if x)}
        if ciclo == "empilhado":
            sc = score_bootstrap(r, k, "cluster_curso")
            linha.update({"p_score_rademacher_curso": sc["rademacher"], "p_score_webb_curso": sc["webb"],
                          "g_efetivo_curso": g_efetivo(r, t, "cluster_curso")})
        linhas.append(linha)
    if R:
        w = wald(r, np.array(R))
        linhas.append({**comuns, "tipo_linha": "wald_igualdade", "termo": "wald_inclinacoes_iguais",
                       "grupo": "todos", "coef": float("nan"), "estatistica_wald": w["wald_conj"],
                       "gl": w["gl_conj"], "gl_completo": w["gl_completo"], "p": w["p_conj"],
                       "p_conj": w["p_conj"], "p_curso": w["p_curso"], "p_mle": w["p_mle"], "p_cand": w["p_cand"],
                       "estatistica_wald_curso": w["wald_curso"], "gl_curso": w["gl_curso"],
                       "estatistica_wald_mle": w["wald_mle"], "estatistica_wald_cand": w["wald_cand"],
                       "p_f_g_menos_1": w["p_f_g_menos_1"], "entra_bky": not degenerada,
                       "nota": "; ".join(x for x in [
                           f"Wald de H0: inclinações iguais nos {len(presentes)} grupos (qui-quadrado; gl = posto da "
                           "covariância das diferenças; p_f_g_menos_1 = F(gl, G − 1) com cluster por conjunto)",
                           (f"covariância por conjunto com posto {w['gl_conj']} < {w['gl_completo']} diferenças"
                            if w["gl_conj"] < w["gl_completo"] else ""),
                           nota_deg if degenerada else ""] if x)})
    for ln in linhas:
        if "p" not in ln:
            ln["p"] = ln["p_conj"]
    resumo["n_candidatos_por_grupo"] = {g: int(cont_cand.get(g, 0)) for g in presentes}
    resumo["n_alternativas_por_grupo"] = {g: int(cont_alt.get(g, 0)) for g in presentes}
    return linhas, resumo


DIM_ADICAO = "estrato_com_inclinacao_por_ciclo"
NOTA_ADICAO = ("adição pós-auditoria (19/10/2026), fora do doc 45: empilhado com inclinação da bolsa própria de cada "
               "ciclo e diferenças por estrato comuns aos ciclos; separa estrato de composição por ciclo; fora do BKY")


def estimar_estrato_por_ciclo(conj_c: pd.DataFrame, cand_c: pd.DataFrame, macros: list[str],
                              estratos: list[str]) -> list[dict]:
    """Adição pós-auditoria: bolsa × ciclo (inclinação de base, capital, por ciclo) + bolsa × estrato (comum)."""
    des = desenho_e9(conj_c, cand_c, macros, estratos)
    X = des["X"].copy()
    bolsa = X["bolsa_mil"].to_numpy()
    ciclo_cel = conj_c["ciclo"].to_numpy()
    estr = conj_c["estrato_territorial"].to_numpy()
    ciclos = sorted(set(int(c) for c in ciclo_cel))
    for c in ciclos[1:]:
        X[f"bolsa_x_ciclo{c}"] = bolsa * (ciclo_cel == c)
    outros = [g for g in sorted(set(estr)) if g != E9.BASE_ESTRATO]
    for g in outros:
        X[f"bolsa_x_{g}"] = bolsa * (estr == g)
    r = ajustar(X, des["conj_cel"], des["grupos"])
    if not r["ok"]:
        raise AssertionError(f"adição estrato × ciclo: {r['nota']}")
    termos = r["termos"]
    comuns = {"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "analise": "X4", "dimensao": DIM_ADICAO,
              "ciclo": "empilhado", "modelo": "logit_condicional_1a_opcao", "conjunto": "principal",
              "especificacao_base": "E9 principal + bolsa × ciclo + bolsa × estrato", "grupo_base": E9.BASE_ESTRATO,
              "nivel_do_grupo": "celula", "n_candidatos": int(len(des["grupos"])), "g_conjuntos": r["G_conj"],
              "g_cursos": r["G_curso"], "log_verossimilhanca": r["ll"], "iteracoes": r["iteracoes"],
              "inferencia_cluster_degenerada": False, "adicao_pos_auditoria": True, "entra_bky": False}
    linhas = []
    kb = termos.index("bolsa_mil")
    for c in ciclos:
        a = np.zeros(len(termos))
        a[kb] = 1.0
        if c != ciclos[0]:
            a[termos.index(f"bolsa_x_ciclo{c}")] = 1.0
        cc = combinacao(r, a)
        linhas.append({**comuns, "tipo_linha": "inclinacao_base_do_ciclo", "termo": f"bolsa_mil|ciclo{c}",
                       "grupo": f"{E9.BASE_ESTRATO}, ciclo {c}", **cc, "p": cc["p_conj"],
                       "nota": f"inclinação da bolsa do estrato de base no ciclo {c}; {NOTA_ADICAO}"})
    R = []
    for g in outros:
        k = termos.index(f"bolsa_x_{g}")
        a = np.zeros(len(termos))
        a[k] = 1.0
        R.append(a)
        cc = combinacao(r, a)
        sb = score_bootstrap(r, k, "cluster_conjunto")
        sc = score_bootstrap(r, k, "cluster_curso")
        linhas.append({**comuns, "tipo_linha": "interacao", "termo": f"bolsa_x_{g}", "grupo": g, **cc,
                       "p": cc["p_conj"], "p_score_rademacher_conjunto": sb["rademacher"],
                       "p_score_webb_conjunto": sb["webb"], "metodo_score_conjunto": sb["metodo_rademacher"],
                       "p_score_rademacher_curso": sc["rademacher"], "p_score_webb_curso": sc["webb"],
                       "nota": f"diferença da inclinação do estrato {g} para a da capital, comum aos ciclos; {NOTA_ADICAO}"})
    w = wald(r, np.array(R))
    linhas.append({**comuns, "tipo_linha": "wald_igualdade", "termo": "wald_inclinacoes_iguais", "grupo": "todos",
                   "coef": float("nan"), "estatistica_wald": w["wald_conj"], "gl": w["gl_conj"],
                   "gl_completo": w["gl_completo"], "p": w["p_conj"], "p_conj": w["p_conj"], "p_curso": w["p_curso"],
                   "p_mle": w["p_mle"], "p_cand": w["p_cand"], "estatistica_wald_curso": w["wald_curso"],
                   "gl_curso": w["gl_curso"], "estatistica_wald_mle": w["wald_mle"],
                   "estatistica_wald_cand": w["wald_cand"], "p_f_g_menos_1": w["p_f_g_menos_1"],
                   "nota": f"Wald de H0: mesmas diferenças por estrato nulas, com inclinação própria por ciclo; {NOTA_ADICAO}"})
    return linhas


# --------------------------------------------------------------------------
# X5
# --------------------------------------------------------------------------

def atributos_vizinhanca(conj_c: pd.DataFrame) -> pd.DataFrame:
    """Por célula: outras células da mesma CIR e do mesmo conjunto; quantas têm bolsa maior; fração."""
    out = pd.DataFrame(index=conj_c.index)
    chave = [conj_c["id_conjunto_escolha"], conj_c["co_cir"]]
    out["n_outras_celulas_regiao"] = conj_c.groupby(chave)["bolsa_mil"].transform("size").to_numpy() - 1

    def maiores(s: pd.Series) -> pd.Series:
        v = s.to_numpy()
        return pd.Series((v[None, :] > v[:, None]).sum(axis=1), index=s.index)

    out["n_vizinhos_bolsa_maior"] = conj_c.groupby(chave)["bolsa_mil"].transform(maiores).astype(float)
    tem = out["n_outras_celulas_regiao"] > 0
    out["tem_vizinho_regiao"] = tem.astype(float)
    out["fracao_vizinhos_bolsa_maior"] = np.where(tem, out["n_vizinhos_bolsa_maior"] /
                                                  out["n_outras_celulas_regiao"].where(tem, 1), 0.0)
    out["n_outras_celulas_regiao"] = out["n_outras_celulas_regiao"].astype(float)
    return out


ESPEC_X5 = {
    "sem_vizinhanca": [],
    "vizinhos_contagem": ["n_vizinhos_bolsa_maior"],
    "vizinhos_contagem_e_total": ["n_vizinhos_bolsa_maior", "n_outras_celulas_regiao"],
    "vizinhos_fracao": ["fracao_vizinhos_bolsa_maior", "tem_vizinho_regiao", "n_outras_celulas_regiao"],
}
TERMO_TESTE_X5 = {"vizinhos_contagem": "n_vizinhos_bolsa_maior", "vizinhos_contagem_e_total": "n_vizinhos_bolsa_maior",
                  "vizinhos_fracao": "fracao_vizinhos_bolsa_maior"}


def _logp_aninhado(params: np.ndarray, X: np.ndarray, conj: np.ndarray, ninho: np.ndarray, ninho_conj: np.ndarray,
                   esc: np.ndarray) -> np.ndarray:
    """log P da célula escolhida no logit aninhado (um lambda comum); vetor por candidato."""
    K = X.shape[1]
    lam = params[K]
    a = (X @ params[:K]) / lam
    n_n, n_c = int(ninho_conj.shape[0]), int(conj.max()) + 1
    amax = np.full(n_n, -np.inf)
    np.maximum.at(amax, ninho, a)
    iv = amax + np.log(np.bincount(ninho, weights=np.exp(a - amax[ninho]), minlength=n_n))
    b = lam * iv
    bmax = np.full(n_c, -np.inf)
    np.maximum.at(bmax, ninho_conj, b)
    lse = bmax + np.log(np.bincount(ninho_conj, weights=np.exp(b - bmax[ninho_conj]), minlength=n_c))
    n_j = ninho[esc]
    return a[esc] - iv[n_j] + lam * iv[n_j] - lse[conj[esc]]


def _jac_num(f, p: np.ndarray) -> np.ndarray:
    cols = []
    for k in range(len(p)):
        h = 1e-6 * max(1.0, abs(p[k]))
        pp, pm = p.copy(), p.copy()
        pp[k] += h
        pm[k] -= h
        cols.append((f(pp) - f(pm)) / (2 * h))
    return np.column_stack(cols)


def estimar_aninhado(r_cl: dict, ninho_u: np.ndarray) -> dict:
    """Logit aninhado sobre as células e escolhas do ajuste condicional `r_cl` (mesma amostra e atributos)."""
    X, conj, esc = r_cl["_X"], r_cl["_conj"], r_cl["_esc"]
    _, ninho = np.unique(np.column_stack([conj, ninho_u]), axis=0, return_inverse=True)
    ninho = ninho.ravel()
    ninho_conj = np.zeros(int(ninho.max()) + 1, dtype=int)
    ninho_conj[ninho] = conj
    tam = np.bincount(ninho)
    K = X.shape[1]

    def f(p):
        return _logp_aninhado(p, X, conj, ninho, ninho_conj, esc)

    def negll(p):
        return -float(f(p).sum())

    def grad(p):
        return -_jac_num(lambda q: np.array([f(q).sum()]), p).ravel()

    p0 = np.concatenate([r_cl["theta"], [1.0]])
    limites = [(None, None)] * K + [LAMBDA_LIMITES]
    res = optimize.minimize(negll, p0, jac=grad, method="L-BFGS-B", bounds=limites,
                            options={"maxiter": 2000, "gtol": 1e-9, "ftol": 1e-15})
    p = res.x
    # Polimento por Newton com hessiana numérica (sem limites), só se lambda ficou no interior.
    no_limite = bool(min(abs(p[K] - LAMBDA_LIMITES[0]), abs(p[K] - LAMBDA_LIMITES[1])) < 1e-6)
    H = None
    for _ in range(20):
        g = -grad(p)
        H = _jac_num(lambda q: -grad(q), p)
        H = 0.5 * (H + H.T)
        if no_limite or not np.all(np.linalg.eigvalsh(-H) > 0):
            break
        passo = np.linalg.solve(-H, g)
        t = 1.0
        while t > 1e-8 and negll(p + t * passo) > negll(p) + 1e-12 * abs(negll(p)):
            t /= 2
        p = p + t * passo
        if p[K] <= 0 or np.max(np.abs(t * passo)) < 1e-10:
            break
    g = -grad(p)
    H = _jac_num(lambda q: -grad(q), p)
    H = 0.5 * (H + H.T)
    ev = np.linalg.eigvalsh(-H)
    def_pos = bool(np.all(ev > 0))
    convergiu = bool(def_pos and np.max(np.abs(g)) < TOL_GRAD_NL and not no_limite and np.all(np.isfinite(p)))
    out = {"theta": p, "ll": -negll(p), "convergiu": convergiu, "grad_max": float(np.max(np.abs(g))),
           "lambda_no_limite": no_limite, "hessiana_definida": def_pos,
           "autovalor_min_informacao": float(ev.min()), "otimizador": str(res.message),
           "n_ninhos": int(len(tam)), "n_ninhos_unitarios": int((tam == 1).sum()),
           "celulas_por_ninho_media": float(tam.mean()), "termos": r_cl["termos"] + ["lambda"]}
    if def_pos:
        info_inv = np.linalg.inv(-H)
        scores = _jac_num(f, p)
        out["V_mle"] = info_inv
        for nome, col in (("conj", "cluster_conjunto"), ("curso", "cluster_curso"), ("cand", "cluster_candidato")):
            V, G = E9.covariancia_cluster(info_inv, scores, r_cl["_grupos"][col].to_numpy())
            out[f"V_{nome}"], out[f"G_{nome}"] = V, G
    return out


def estimar_x5(ciclo: str, conj_c: pd.DataFrame, cand_c: pd.DataFrame, macros: list[str], estratos: list[str]
               ) -> tuple[list[dict], dict]:
    des = desenho_e9(conj_c, cand_c, macros, estratos)
    viz = atributos_vizinhanca(conj_c)
    linhas, resumo = [], {"ciclo": ciclo, "n_candidatos": int(len(des["grupos"])), "n_alternativas": int(len(conj_c)),
                          "n_conjuntos": int(conj_c["id_conjunto_escolha"].nunique()),
                          "celulas_com_vizinho_na_regiao": int(viz["tem_vizinho_regiao"].sum()),
                          "celulas_com_vizinho_de_bolsa_maior": int((viz["n_vizinhos_bolsa_maior"] > 0).sum())}
    comuns = {"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "analise": "X5", "ciclo": ciclo,
              "conjunto": "principal (sem células de município sem CIR oficial)",
              "n_candidatos": int(len(des["grupos"]))}
    resultados = {}
    for espec, cols in ESPEC_X5.items():
        X = des["X"].copy()
        for c in cols:
            X[c] = viz[c].to_numpy()
        r = ajustar(X, des["conj_cel"], des["grupos"])
        if not r["ok"]:
            raise AssertionError(f"X5 {espec} ciclo {ciclo}: {r['nota']}")
        resultados[espec] = r
        teste = TERMO_TESTE_X5.get(espec)
        for t in ["bolsa_mil"] + cols:
            k = r["termos"].index(t)
            a = np.zeros(len(r["termos"]))
            a[k] = 1.0
            c = combinacao(r, a)
            linha = {**comuns, "modelo": "logit_condicional_1a_opcao", "especificacao": espec,
                     "tipo_linha": ("bolsa" if t == "bolsa_mil" else ("vizinhanca" if t == teste else "controle")),
                     "termo": t, **c, "p": c["p_conj"], "g_conjuntos": r["G_conj"], "g_cursos": r["G_curso"],
                     "n_alternativas": r["n_alternativas"], "log_verossimilhanca": r["ll"],
                     "iteracoes": r["iteracoes"], "entra_bky": t == teste,
                     "nota": ("coeficiente da bolsa sem termos de vizinhança (principal do E9 na amostra do X5)"
                              if espec == "sem_vizinhanca" else "")}
            if t == teste:
                sb = score_bootstrap(r, k, "cluster_conjunto")
                linha.update({"p_score_rademacher_conjunto": sb["rademacher"], "p_score_webb_conjunto": sb["webb"],
                              "metodo_score_conjunto": sb["metodo_rademacher"]})
                if ciclo == "empilhado":
                    sc = score_bootstrap(r, k, "cluster_curso")
                    linha.update({"p_score_rademacher_curso": sc["rademacher"], "p_score_webb_curso": sc["webb"]})
                linha["nota"] = ("proposta A prevê coeficiente negativo: bolsa maior na vizinhança regional tira "
                                 "escolha da célula além da substituição proporcional do logit")
            linhas.append(linha)
    # (i) logit aninhado por CIR dentro do curso × ciclo.
    r_cl = resultados["sem_vizinhanca"]
    cir_codigos = pd.factorize(conj_c["co_cir"])[0]
    nl = estimar_aninhado(r_cl, cir_codigos[r_cl["_usadas"]])
    resumo["aninhado"] = {k: v for k, v in nl.items() if not k.startswith("V_") and k != "theta"}
    nota_nl = "; ".join(x for x in [
        "" if nl["convergiu"] else "logit aninhado sem convergência limpa (ver lambda_no_limite, hessiana e gradiente)",
        f"{nl['n_ninhos']} ninhos (CIR × conjunto), {nl['n_ninhos_unitarios']} com uma só célula"] if x)
    lr = 2 * (nl["ll"] - r_cl["ll"])
    for t in ("bolsa_mil", "lambda"):
        k = nl["termos"].index(t)
        if "V_mle" in nl:
            a = np.zeros(len(nl["termos"]))
            a[k] = 1.0
            c = combinacao(nl, a)
            if t == "lambda":  # p de H0: lambda = 0 não tem sentido; o teste é lambda = 1 (linha própria)
                for campo in ("p_conj", "p_curso", "p_mle", "p_cand", "p_t_g_menos_1"):
                    c[campo] = float("nan")
        else:
            c = {"coef": float(nl["theta"][k])}
        linhas.append({**comuns, "modelo": "logit_aninhado_cir", "especificacao": "aninhado_cir",
                       "tipo_linha": "bolsa" if t == "bolsa_mil" else "lambda", "termo": t, **c,
                       "p": c.get("p_conj", float("nan")) if t == "bolsa_mil" else float("nan"),
                       "g_conjuntos": nl.get("G_conj"), "g_cursos": nl.get("G_curso"),
                       "n_alternativas": r_cl["n_alternativas"], "log_verossimilhanca": nl["ll"],
                       "convergiu": nl["convergiu"], "entra_bky": False,
                       "nota": "; ".join(x for x in [nota_nl, ("lambda: parâmetro de dissimilaridade; 1 = logit "
                                                              "condicional; < 1 = mais substituição dentro da CIR; o p "
                                                              "desta linha (H0: lambda = 0) não é relatado")
                                                     if t == "lambda" else "utilidade na escala do logit (V = x'b)"] if x)})
    if "V_mle" in nl:
        k = nl["termos"].index("lambda")
        lam = float(nl["theta"][k])
        reg = {"coef": lam - 1.0}
        for nome, _ in VS:
            ep = math.sqrt(nl[f"V_{nome}"][k, k])
            reg[f"ep_{nome}"] = ep
            reg[f"p_{nome}"] = _p_norm((lam - 1.0) / ep)
        ep = reg["ep_conj"]
        reg.update({"ic95_inf": lam - 1.0 - Z95 * ep, "ic95_sup": lam - 1.0 + Z95 * ep,
                    "p_t_g_menos_1": float(2 * stats.t.sf(abs((lam - 1.0) / ep), nl["G_conj"] - 1))})
        linhas.append({**comuns, "modelo": "logit_aninhado_cir", "especificacao": "aninhado_cir",
                       "tipo_linha": "teste_lambda_igual_1", "termo": "lambda_menos_1", **reg, "p": reg["p_conj"],
                       "razao_verossimilhanca": lr, "p_razao_verossimilhanca": float(stats.chi2.sf(max(lr, 0.0), 1)),
                       "g_conjuntos": nl["G_conj"], "g_cursos": nl["G_curso"],
                       "n_alternativas": r_cl["n_alternativas"], "log_verossimilhanca": nl["ll"],
                       "convergiu": nl["convergiu"], "entra_bky": bool(nl["convergiu"]),
                       "nota": "; ".join(x for x in [nota_nl, "Wald de H0: lambda = 1 (cluster por conjunto); LR contra o "
                                                              "logit condicional (MV, ignora cluster)"] if x)})
    else:
        linhas.append({**comuns, "modelo": "logit_aninhado_cir", "especificacao": "aninhado_cir",
                       "tipo_linha": "teste_lambda_igual_1", "termo": "lambda_menos_1", "coef": float("nan"),
                       "p": float("nan"), "razao_verossimilhanca": lr, "convergiu": False, "entra_bky": False,
                       "nota": "; ".join([nota_nl, "informação não definida positiva: lambda não identificado"])})
    return linhas, resumo


# --------------------------------------------------------------------------
# Tabelas de relato (geradas dos CSVs)
# --------------------------------------------------------------------------

fmt, fmt_p = E9.fmt, E9.fmt_p


def _ic(lo: float, hi: float, casas: int = 3) -> str:
    return f"[{fmt(lo, casas)}; {fmt(hi, casas)}]"


MARCAS = {"X4": ("<!-- X4_TABELAS_INICIO -->", "<!-- X4_TABELAS_FIM -->"),
          "X5": ("<!-- X5_TABELAS_INICIO -->", "<!-- X5_TABELAS_FIM -->")}
CABECALHO_GERADO = "<!-- gerado por scripts/rdd_bolsa/19_escolha_heterogeneidade.py; não editar à mão -->"


def tabelas_relato(x4: pd.DataFrame, x5: pd.DataFrame, res: dict) -> str:
    """Dois blocos marcados (X4 e X5), copiados como estão para as seções do doc 46."""
    L_ = [MARCAS["X4"][0], CABECALHO_GERADO, ""]
    def inferencia(r) -> tuple[str, str, str]:
        """IC, p e rótulo: cluster por conjunto; na dimensão curso (cluster degenerado), máxima verossimilhança."""
        if bool(r.inferencia_cluster_degenerada):
            return (_ic(r.coef - Z95 * r.ep_mle, r.coef + Z95 * r.ep_mle, 4), fmt_p(r.p_mle),
                    "MV (cluster degenerado)")
        return _ic(r.ic95_inf, r.ic95_sup, 4), fmt_p(r.p_conj), "cluster por conjunto"

    proto = x4[~x4.adicao_pos_auditoria.astype(bool)]
    L_.append("**Tabela X4.1. Inclinação da bolsa por grupo (coef. por R$ 1 mil; logit condicional, principal do E9 "
              "com interações).** IC 95% e p pela normal com EP de cluster por conjunto; na dimensão curso, em que o "
              "EP por cluster é degenerado, com o EP de máxima verossimilhança (MV), que ignora o choque comum do "
              "conjunto (coluna inferência).")
    L_.append("")
    L_.append("| dimensão | ciclo | grupo | candidatos | coef. | IC 95% | p | inferência |")
    L_.append("|---|---|---|---:|---:|---|---:|---|")
    for r in proto[proto.tipo_linha == "inclinacao_do_grupo"].itertuples():
        ic, p_, rot = inferencia(r)
        L_.append(f"| {r.dimensao} | {r.ciclo} | {r.grupo} | {int(r.n_candidatos_grupo)} | {fmt(r.coef, 4)} | "
                  f"{ic} | {p_} | {rot} |")
    L_.append("")
    L_.append("**Tabela X4.2. Termos de interação (diferença para o grupo de base) e Wald da igualdade das "
              "inclinações.** IC e p como na Tabela X4.1 (na dimensão curso, MV; o Wald de curso também é o de MV); "
              "p do score bootstrap (Rademacher, enumeração completa com G ≤ 24, senão sorteios) com cluster por "
              "conjunto e, no empilhado, por curso; não relatado na dimensão curso. q de BKY dentro do X4 (linhas "
              "fora da família: —).")
    L_.append("")
    L_.append("| dimensão | ciclo | termo | base | coef. | IC 95% | p | p score (conjunto) | p score (curso) | q BKY | "
              "inferência |")
    L_.append("|---|---|---|---|---:|---|---:|---:|---:|---:|---|")
    for r in proto[proto.tipo_linha.isin(["interacao", "wald_igualdade"])].itertuples():
        deg = bool(r.inferencia_cluster_degenerada)
        if r.tipo_linha == "wald_igualdade":
            if deg:
                termo = f"Wald MV (χ², {int(r.gl_completo)} gl) = {fmt(r.estatistica_wald_mle, 2)}"
                p_, rot = fmt_p(r.p_mle), "MV (cluster degenerado)"
            else:
                termo = f"Wald (χ², {int(r.gl)} gl) = {fmt(r.estatistica_wald, 2)}"
                p_, rot = fmt_p(r.p), "cluster por conjunto"
            coef, ic, psc, psc2 = "—", "—", "—", "—"
        else:
            termo = r.termo
            coef = fmt(r.coef, 4)
            ic, p_, rot = inferencia(r)
            psc = "—" if deg else fmt_p(r.p_score_rademacher_conjunto)
            psc2 = fmt_p(r.p_score_rademacher_curso) if (r.ciclo == "empilhado" and not deg) else "—"
        q = fmt(r.q_bky, 3) if bool(r.entra_bky) else "—"
        L_.append(f"| {r.dimensao} | {r.ciclo} | {termo} | {r.grupo_base} | {coef} | {ic} | {p_} | "
                  f"{psc} | {psc2} | {q} | {rot} |")
    L_.append("")
    L_.append("**Tabela X4.3. Pontos de corte dos tercis da pontuação (1/3 e 2/3, quantil linear; empate no corte vai "
              "para o tercil de baixo).**")
    L_.append("")
    L_.append("| ciclo | corte 1/3 | corte 2/3 | tercil 1 | tercil 2 | tercil 3 | sem pontuação |")
    L_.append("|---|---:|---:|---:|---:|---:|---:|")
    for ciclo in ("1", "2", "3"):
        d = res["x4_por_modelo"][f"nota_tercil|{ciclo}"]
        q1, q2 = d["cortes"][ciclo]
        n = d["n_candidatos_por_grupo"]
        L_.append(f"| {ciclo} | {fmt(q1, 2)} | {fmt(q2, 2)} | {n.get('tercil1', 0)} | {n.get('tercil2', 0)} | "
                  f"{n.get('tercil3', 0)} | {n.get('sem_pontuacao', 0)} |")
    L_.append("")
    L_.append("**Tabela X4.4. Estrato: candidatos de 1a opção por ciclo e inclinação da bolsa de cada estrato no "
              "modelo do ciclo (Tabela X4.1).** A fração no ciclo 3 mostra a composição que o empilhado, com uma só "
              "inclinação para os três ciclos, mistura com o estrato. Em cada ciclo, * marca a menor inclinação.")
    L_.append("")
    L_.append("| estrato | ciclo 1 | ciclo 2 | ciclo 3 | fração no ciclo 3 | coef. ciclo 1 | coef. ciclo 2 | "
              "coef. ciclo 3 |")
    L_.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    est = proto[(proto.dimensao == "estrato") & (proto.tipo_linha == "inclinacao_do_grupo") &
                (proto.ciclo.astype(str) != "empilhado")]
    n = est.pivot(index="grupo", columns="ciclo", values="n_candidatos_grupo")
    b_ = est.pivot(index="grupo", columns="ciclo", values="coef")
    n.columns, b_.columns = [str(c) for c in n.columns], [str(c) for c in b_.columns]
    for g in n.index:
        tot = float(n.loc[g].sum())
        coefs = [fmt(b_.loc[g, c], 4) + ("*" if b_.loc[g, c] == b_[c].min() else "") for c in ("1", "2", "3")]
        L_.append(f"| {g} | {int(n.loc[g, '1'])} | {int(n.loc[g, '2'])} | {int(n.loc[g, '3'])} | "
                  f"{fmt(n.loc[g, '3'] / tot, 3)} | " + " | ".join(coefs) + " |")
    L_.append("")
    ad = x4[x4.adicao_pos_auditoria.astype(bool)]
    L_.append("**Tabela X4.5. Adição pós-auditoria (fora do doc 45 e do BKY): empilhado com inclinação da bolsa "
              "própria de cada ciclo (estrato de base, capital) e diferenças por estrato comuns aos ciclos.** IC e p "
              "com cluster por conjunto; p do score bootstrap com cluster por conjunto e por curso.")
    L_.append("")
    L_.append("| termo | coef. | IC 95% | p | p score (conjunto) | p score (curso) |")
    L_.append("|---|---:|---|---:|---:|---:|")
    for r in ad.itertuples():
        if r.tipo_linha == "wald_igualdade":
            L_.append(f"| Wald (χ², {int(r.gl)} gl) = {fmt(r.estatistica_wald, 2)} | — | — | {fmt_p(r.p)} | — | — |")
        elif r.tipo_linha == "interacao":
            L_.append(f"| {r.termo} | {fmt(r.coef, 4)} | {_ic(r.ic95_inf, r.ic95_sup, 4)} | {fmt_p(r.p)} | "
                      f"{fmt_p(r.p_score_rademacher_conjunto)} | {fmt_p(r.p_score_rademacher_curso)} |")
        else:
            L_.append(f"| {r.grupo} | {fmt(r.coef, 4)} | {_ic(r.ic95_inf, r.ic95_sup, 4)} | {fmt_p(r.p)} | — | — |")
    L_.append("")
    L_.append("**Tabela X4.6. Cursos sem ponte curso → CBO (grupo sem_ponte_curso_cbo da escassez) e curso de menor "
              "inclinação no ciclo 3 (Tabela X4.1).**")
    L_.append("")
    c3 = proto[(proto.dimensao == "curso") & (proto.ciclo.astype(str) == "3") &
               (proto.tipo_linha == "inclinacao_do_grupo")].sort_values("coef")
    L_.append("| cursos sem ponte | curso de menor inclinação no ciclo 3 |")
    L_.append("|---|---|")
    L_.append(f"| {', '.join(str(c) for c in res['cursos_sem_ponte'])} | {c3.iloc[0].grupo} |")
    L_ += ["", MARCAS["X4"][1], "", MARCAS["X5"][0], CABECALHO_GERADO, ""]
    L_.append("**Tabela X5.1. Bolsa com e sem termos de vizinhança, termos de vizinhança e logit aninhado por região "
              "de saúde (CIR).** Amostra do X5 (sem células de município sem CIR oficial). EP e IC 95% com cluster "
              "por conjunto; p pela normal; p do score bootstrap Rademacher (cluster por conjunto) nos termos de "
              "vizinhança. Na linha lambda − 1, o p é o do Wald de H0: lambda = 1. q de BKY dentro do X5.")
    L_.append("")
    L_.append("| ciclo | especificação | termo | coef. | IC 95% | p | p score (conjunto) | q BKY |")
    L_.append("|---|---|---|---:|---|---:|---:|---:|")
    for r in x5[x5.tipo_linha.isin(["bolsa", "vizinhanca", "lambda", "teste_lambda_igual_1"])].itertuples():
        if r.tipo_linha == "lambda":
            ic = _ic(r.ic95_inf, r.ic95_sup, 4) if pd.notna(r.ic95_inf) else "—"
            L_.append(f"| {r.ciclo} | {r.especificacao} | lambda | {fmt(r.coef, 4)} | {ic} | — | — | — |")
            continue
        psc = fmt_p(r.p_score_rademacher_conjunto) if r.tipo_linha == "vizinhanca" else "—"
        q = fmt(r.q_bky, 3) if bool(r.entra_bky) else "—"
        ic = _ic(r.ic95_inf, r.ic95_sup, 4) if pd.notna(r.ic95_inf) else "—"
        L_.append(f"| {r.ciclo} | {r.especificacao} | {r.termo} | {fmt(r.coef, 4)} | {ic} | {fmt_p(r.p)} | {psc} | {q} |")
    L_.append("")
    L_.append("**Tabela X5.2. Amostra, ninhos e convergência do logit aninhado.**")
    L_.append("")
    L_.append("| ciclo | candidatos | células | células com vizinho na CIR | ninhos | ninhos de uma célula | "
              "lambda no limite | convergiu | LR contra o condicional | p LR |")
    L_.append("|---|---:|---:|---:|---:|---:|---|---|---:|---:|")
    lr = x5[x5.tipo_linha == "teste_lambda_igual_1"].set_index("ciclo")
    for ciclo in CICLOS:
        d = res["x5_por_ciclo"][ciclo]
        a = d["aninhado"]
        L_.append(f"| {ciclo} | {d['n_candidatos']} | {d['n_alternativas']} | {d['celulas_com_vizinho_na_regiao']} | "
                  f"{a['n_ninhos']} | {a['n_ninhos_unitarios']} | {'sim' if a['lambda_no_limite'] else 'não'} | "
                  f"{'sim' if a['convergiu'] else 'não'} | {fmt(lr.loc[ciclo, 'razao_verossimilhanca'], 2)} | "
                  f"{fmt_p(lr.loc[ciclo, 'p_razao_verossimilhanca'])} |")
    L_.append("")
    r_ = res["x5_retirados"]
    L_.append("**Tabela X5.3. Fora do X5 por falta de CIR oficial (sem imputação).**")
    L_.append("")
    L_.append("| ciclo | células retiradas | candidatos de 1a opção retirados |")
    L_.append("|---|---:|---:|")
    for ciclo in ("1", "2", "3"):
        L_.append(f"| {ciclo} | {r_['celulas_retiradas_por_ciclo'].get(ciclo, 0)} | "
                  f"{r_['candidatos_de_1a_opcao_retirados_por_ciclo'].get(ciclo, 0)} |")
    L_ += ["", MARCAS["X5"][1], ""]
    return "\n".join(L_)


def bloco_do_texto(texto: str, chave: str) -> str:
    ini, fim = MARCAS[chave]
    return texto[texto.index(ini):texto.index(fim) + len(fim)]


# --------------------------------------------------------------------------
# Execução
# --------------------------------------------------------------------------

def bloco_entrada(caminho: Path, papel: str, fonte: str, data_ref: str, cobertura: str, unidade: str, chaves: str,
                  filtros: str) -> dict:
    return {"caminho": rel(caminho), "sha256": sha256_arquivo(caminho), "bytes": caminho.stat().st_size,
            "papel": papel, "fonte": fonte, "data_referencia": data_ref, "cobertura": cobertura, "unidade": unidade,
            "chaves": chaves, "filtros": filtros}


def conferir_reproducao_e9(conj_p: pd.DataFrame, cand: pd.DataFrame, macros: list[str], estratos: list[str]) -> dict:
    """O ajuste genérico reproduz o principal do E9 gravado (coef. e EP cluster por conjunto da bolsa)."""
    e9 = pd.read_csv(E9_ESTIMATIVAS)
    out = {}
    for ciclo in CICLOS:
        conj_c = conj_p[conj_p["ciclo"].isin(_ciclos_int(ciclo))].reset_index(drop=True)
        cand_c = cand[cand["ciclo"].isin(_ciclos_int(ciclo))]
        des = desenho_e9(conj_c, cand_c, macros, estratos)
        r = ajustar(des["X"], des["conj_cel"], des["grupos"])
        k = r["termos"].index("bolsa_mil")
        alvo = e9[(e9.ciclo.astype(str) == ciclo) & (e9.modelo == E9.MODELO_COND) & (e9.conjunto == "principal") &
                  (e9.especificacao == E9.ESPEC_PRINCIPAL) & (e9.termo == "bolsa_mil")].iloc[0]
        b, ep = float(r["theta"][k]), math.sqrt(r["V_conj"][k, k])
        ok = bool(np.isclose(b, alvo.coef, rtol=1e-6, atol=1e-9) and
                  np.isclose(ep, alvo.ep_cluster_conjunto, rtol=1e-6, atol=1e-9))
        out[ciclo] = {"coef": b, "ep_cluster_conjunto": ep, "coef_E9": float(alvo.coef),
                      "ep_E9": float(alvo.ep_cluster_conjunto), "igual": ok}
        if not ok:
            raise AssertionError(f"reestimação do principal do E9 não reproduz o gravado no ciclo {ciclo}: {out[ciclo]}")
        # Expansão por grupo de candidato sem interações: mesma verossimilhança e mesmo coeficiente.
        r1 = des["r1"]
        rot = np.where(r1["pontuacao"].notna(), np.where(r1["pontuacao"] > r1["pontuacao"].median(), "a", "b"), "c")
        Xe, ce, ge, _ = expandir_por_grupo_de_candidato(des["X"], des["conj_cel"], des["grupos"], rot)
        re_ = ajustar(Xe, ce, ge)
        okx = bool(np.isclose(re_["ll"], r["ll"], rtol=1e-10) and
                   np.allclose(re_["theta"], r["theta"], rtol=1e-7, atol=1e-9))
        out[ciclo]["expansao_por_grupo_de_candidato_igual"] = okx
        if not okx:
            raise AssertionError(f"expansão por grupo de candidato muda a verossimilhança no ciclo {ciclo}")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--baixar-regioes", action="store_true",
                    help="baixa a tabela oficial município → CIR do TabNet/DATASUS se ainda não estiver em data/raw")
    args = ap.parse_args(argv)

    dic = json.loads(E9.DICIONARIO.read_text(encoding="utf-8"))
    conferencias = E9.conferir_insumos(dic)
    mapa, _ = E9.mapa_bolsa_por_faixa()
    ivs = E9.carregar_ivs()
    cand = pd.read_parquet(E9.ESCOLHAS)
    if not (cand["natureza_dos_dados"] == NATUREZA).all():
        raise AssertionError("escolhas com natureza diferente de EMPIRICO")
    conj_p, diag_p = E9.preparar_conjunto(pd.read_parquet(E9.CONJ_PRINCIPAL), ivs, mapa)
    for d in diag_p["alternativas_retiradas_sem_ivs"]:
        hit = cand[(cand.ciclo == d["ciclo"]) & (cand.co_cnes_7d == d["co_cnes_7d"]) & (cand.cod_curso == d["cod_curso"])]
        if len(hit):
            raise AssertionError(f"célula sem IVS escolhida por candidato: {d}")
    macros = sorted(conj_p["macrorregiao"].unique())
    estratos = sorted(conj_p["estrato_territorial"].unique())

    reproducao = conferir_reproducao_e9(conj_p, cand, macros, estratos)
    print("reprodução do principal do E9: ok", flush=True)

    # ------------------------------------------------------------------ X4
    esc_cel, diag_esc = escassez_por_celula(conj_p)
    cursos_sem_ponte = sorted(int(c) for c in set(conj_p["cod_curso"]) if str(int(c)) not in diag_esc["cbos_por_curso"])
    x4_linhas, x4_resumo = [], {}
    for dim in DIMENSOES:
        for ciclo in CICLOS:
            m = conj_p["ciclo"].isin(_ciclos_int(ciclo)).to_numpy()
            conj_c = conj_p[m].reset_index(drop=True)
            esc_c = esc_cel[m].reset_index(drop=True)
            cand_c = cand[cand["ciclo"].isin(_ciclos_int(ciclo))]
            linhas, resumo = estimar_x4(dim, ciclo, conj_c, cand_c, esc_c, macros, estratos)
            x4_linhas += linhas
            x4_resumo[f"{dim}|{ciclo}"] = resumo
            print(f"X4 {dim:16s} ciclo {ciclo:9s} grupos={resumo['grupos']} it={resumo['iteracoes']}", flush=True)
    # Adição pós-auditoria (fora do doc 45 e do BKY): estrato com inclinação da bolsa própria de cada ciclo.
    x4_linhas += estimar_estrato_por_ciclo(conj_p, cand, macros, estratos)
    x4 = pd.DataFrame(x4_linhas)
    x4["adicao_pos_auditoria"] = x4["adicao_pos_auditoria"].fillna(False).astype(bool)
    fam = x4["entra_bky"].astype(bool) & x4["p"].notna()
    x4["q_bky"] = np.nan
    x4.loc[fam, "q_bky"] = L.qvalores_bky(x4.loc[fam, "p"].to_numpy())

    # ------------------------------------------------------------------ X5
    manifesto_cir = adquirir_cir(args.baixar_regioes)
    cir, diag_cir = ler_cir()
    conf_malha = conferir_cir_contra_malha(cir)
    conj_p["co_cir"] = conj_p["co_ibge"].map(cir.set_index("co_ibge")["co_cir"])
    sem_cir = conj_p[conj_p["co_cir"].isna()]
    r1_all = cand[cand["opcao_rank"] == 1]
    chaves_sem = set(zip(sem_cir["ciclo"], sem_cir["co_cnes_7d"], sem_cir["cod_curso"]))
    escolheu_sem = r1_all[[k in chaves_sem for k in zip(r1_all["ciclo"], r1_all["co_cnes_7d"], r1_all["cod_curso"])]]
    retirados_x5 = {"municipios_sem_cir_oficial": sorted(sem_cir["co_ibge"].unique().tolist()),
                    "celulas_retiradas_por_ciclo": {str(int(k)): int(v) for k, v in sem_cir.groupby("ciclo").size().items()},
                    "candidatos_de_1a_opcao_retirados_por_ciclo": {str(int(k)): int(v) for k, v in
                                                                   escolheu_sem.groupby("ciclo").size().items()},
                    "motivo": "município ausente da tabela oficial de CIR do TabNet; não se imputa região (a malha do "
                              "repositório não é usada para preencher)"}
    conj_x5 = conj_p[conj_p["co_cir"].notna()].reset_index(drop=True)
    ids_fora = set(escolheu_sem["id_candidato"])
    cand_x5 = cand[~cand["id_candidato"].isin(ids_fora)]
    x5_linhas, x5_resumo = [], {}
    for ciclo in CICLOS:
        conj_c = conj_x5[conj_x5["ciclo"].isin(_ciclos_int(ciclo))].reset_index(drop=True)
        cand_c = cand_x5[cand_x5["ciclo"].isin(_ciclos_int(ciclo))]
        linhas, resumo = estimar_x5(ciclo, conj_c, cand_c, macros, estratos)
        x5_linhas += linhas
        x5_resumo[ciclo] = resumo
        print(f"X5 ciclo {ciclo:9s} lambda={resumo['aninhado']} ", flush=True)
    x5 = pd.DataFrame(x5_linhas)
    fam5 = x5["entra_bky"].astype(bool) & x5["p"].notna()
    x5["q_bky"] = np.nan
    x5.loc[fam5, "q_bky"] = L.qvalores_bky(x5.loc[fam5, "p"].to_numpy())

    for nome, df in (("X4", x4), ("X5", x5)):
        sem = df[df["coef"].isna() & ~df["tipo_linha"].isin(["wald_igualdade"]) & (df["nota"].fillna("") == "")]
        if len(sem):
            raise AssertionError(f"{nome}: {len(sem)} linhas com coef. NaN sem nota")
        if not ((df["natureza_dos_dados"] == NATUREZA) & (df["estatuto"] == ESTATUTO)).all():
            raise AssertionError(f"{nome}: rótulo de natureza ou estatuto ausente")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ordem4 = ["natureza_dos_dados", "estatuto", "analise", "dimensao", "ciclo", "tipo_linha", "termo", "grupo",
              "grupo_base", "nivel_do_grupo", "coef", "ep_conj", "ic95_inf", "ic95_sup", "p", "p_t_g_menos_1",
              "q_bky", "entra_bky", "p_conj", "ep_curso", "p_curso", "ep_mle", "p_mle", "ep_cand", "p_cand",
              "p_score_rademacher_conjunto", "p_score_webb_conjunto", "metodo_score_conjunto",
              "p_score_rademacher_curso", "p_score_webb_curso", "g_efetivo_conjunto", "g_efetivo_curso",
              "estatistica_wald", "gl", "gl_completo", "p_f_g_menos_1", "estatistica_wald_curso", "gl_curso",
              "estatistica_wald_mle", "estatistica_wald_cand", "rc_por_5mil", "n_candidatos", "n_candidatos_grupo",
              "n_alternativas_grupo", "g_conjuntos", "g_cursos", "inferencia_cluster_degenerada", "adicao_pos_auditoria",
              "modelo",
              "conjunto", "especificacao_base", "log_verossimilhanca", "iteracoes", "nota"]
    x4 = x4.reindex(columns=ordem4)
    ordem5 = ["natureza_dos_dados", "estatuto", "analise", "ciclo", "modelo", "especificacao", "tipo_linha", "termo",
              "coef", "ep_conj", "ic95_inf", "ic95_sup", "p", "p_t_g_menos_1", "q_bky", "entra_bky", "p_conj",
              "ep_curso", "p_curso", "ep_mle", "p_mle", "ep_cand", "p_cand", "p_score_rademacher_conjunto",
              "p_score_webb_conjunto", "metodo_score_conjunto", "p_score_rademacher_curso", "p_score_webb_curso",
              "razao_verossimilhanca", "p_razao_verossimilhanca", "g_conjuntos", "g_cursos", "n_candidatos",
              "n_alternativas", "conjunto", "log_verossimilhanca", "iteracoes", "convergiu", "nota"]
    x5 = x5.reindex(columns=ordem5)
    x4.to_csv(OUT_X4, index=False, float_format="%.10g")
    x5.to_csv(OUT_X5, index=False, float_format="%.10g")
    # Relê os CSVs para que as tabelas saiam exatamente do que foi gravado.
    x4r, x5r = pd.read_csv(OUT_X4), pd.read_csv(OUT_X5)
    res_tab = {"x5_por_ciclo": x5_resumo, "x4_por_modelo": x4_resumo, "x5_retirados": retirados_x5,
               "cursos_sem_ponte": cursos_sem_ponte}
    OUT_TABELAS.write_text(tabelas_relato(x4r, x5r, res_tab), encoding="utf-8")

    painel_meta = json.loads(MANIFESTO_PAINEL.read_text(encoding="utf-8"))
    n_cursos_ponte = len(json.loads(PONTE.read_text(encoding="utf-8"))["catalogo_cursos"])
    entradas = [
        bloco_entrada(PROTOCOLO_X, "protocolo exploratório congelado (X4, X5)", "repositório", "2026-10-19", "-",
                      "documento", "-", "-"),
        bloco_entrada(E9.PROTOCOLO_MD, "protocolo 40 (§14, §15: forma do E9; SHA conferido contra o congelado)",
                      "repositório", "2026-10-18", "-", "documento", "-", "-"),
        bloco_entrada(E9.PROTOCOLO_JSON, "protocolo 40 congelado (JSON)", "repositório", "2026-10-18", "-",
                      "documento", "-", "-"),
        bloco_entrada(E9.DICIONARIO, "dicionário da tarefa B (SHA-256 das tabelas de escolha conferido)",
                      "pipeline do repositório", "2026-10-18", "-", "documento", "-", "-"),
        bloco_entrada(E9.ESCOLHAS, "escolhas dos candidatos (1a opção) e pontuação do F4",
                      "pipeline do repositório (tarefa B)", "resultados da 1a chamada dos ciclos 1-3",
                      f"{len(cand)} linhas", "candidato × opção", "ciclo, id_candidato, opcao_rank",
                      "posto 1; pontuacao para os tercis (X4a)"),
        bloco_entrada(E9.CONJ_PRINCIPAL, "conjunto de escolha principal (§14)", "pipeline do repositório (tarefa B)",
                      "quadros da 1a chamada", f"{len(conj_p) + len(diag_p['alternativas_retiradas_sem_ivs'])} células",
                      "célula CNES × curso × ciclo", "ciclo, co_cnes_7d, cod_curso",
                      "retiradas as células sem IVS oficial (como no E9)"),
        bloco_entrada(E9.IVS_OFICIAL, "running variable: IVS 2010 oficial (a08)", "Ipea, Atlas da Vulnerabilidade "
                      "Social", "Censo 2010", f"{len(ivs)} municípios", "município", "co_ibge", "co_ibge, ivs"),
        bloco_entrada(E9.GRADES_EDITAIS, "mapa faixa → bolsa (como no E9)", "editais (a03)", "2025-2026",
                      "3 faixas", "faixa", "faixa", "mapeamento_regras_por_edital"),
        bloco_entrada(E9.GRADE_2025, "conferência do mapa faixa → bolsa (como no E9)", "FAQ do edital 3/2025 (a04)",
                      "2025", "3 faixas", "faixa", "faixa_atracao", "-"),
        bloco_entrada(E9_ESTIMATIVAS, "alvo da conferência de reprodução do principal do E9", "pipeline (E9)",
                      "2026-10-19", "linhas do principal", "especificação × termo", "ciclo, modelo, conjunto, "
                      "especificacao, termo", "condicional, principal, spline_linear__bolsa_linear, bolsa_mil"),
        bloco_entrada(PAINEL_CNES, "escassez pré-programa (X4c): vínculos por município × CBO × mês",
                      f"CNES nacional, DATASUS ({painel_meta['fonte']['nome']}), via a09", "202406 a 202506",
                      "todos os municípios da malha 2010", "município × grupo CBO × competência",
                      "co_ibge, competencia, grupo", "grupos cbo_* das cbos_elegiveis da ponte; competências 202406 "
                      "a 202506; coluna n_vinculos"),
        bloco_entrada(MANIFESTO_PAINEL, "manifesto do painel CNES nacional (fonte e URLs)", "pipeline (a09)",
                      "2026-10-19", "-", "documento", "-", "-"),
        bloco_entrada(PONTE, "ponte curso → CBO (cbos_elegiveis)", "repositório (ponte operacional auditada)",
                      "2026-08-30", f"{n_cursos_ponte} cursos", "curso", "cod_curso", "catalogo_cursos.cbos_elegiveis"),
        bloco_entrada(MALHA, "só conferência da CIR oficial (região da malha só existe onde houve ativo do PMM-E)",
                      "pipeline (04_harmonizar_territorio_ibge)", "série histórica e lista nominal do PMM-E",
                      f"{conf_malha['municipios_com_regiao_na_malha']} municípios com região", "município",
                      "co_ibge_6d", "no_regiao_saude não vazio"),
        bloco_entrada(CIR_BRUTO, "região de saúde (CIR) por município (X5)", f"DATASUS/TabNet, {CIR_URL}",
                      f"base territorial corrente do TabNet, baixada em {manifesto_cir['data_download_utc']}",
                      f"{diag_cir['municipios']} municípios, {diag_cir['regioes']} CIR", "município",
                      "co_ibge (6 dígitos) → código CIR (5 dígitos)", "linhas 'Ignorado' (faixas) fora"),
        bloco_entrada(OUT_MANIFESTO_CIR, "manifesto do download da CIR", "este script", manifesto_cir["data_download_utc"],
                      "-", "documento", "-", "-"),
    ]
    q4 = x4[x4.entra_bky.astype(bool)]
    q5 = x5[x5.entra_bky.astype(bool)]
    resumo = {
        "natureza_dos_dados": NATUREZA,
        "estatuto": ESTATUTO,
        "documento": "X4 (heterogeneidade da escolha) e X5 (deslocamento regional) do protocolo exploratório 45",
        "data_execucao": DATA_EXECUCAO,
        "script": rel(Path(__file__)),
        "protocolo": {"arquivo": rel(PROTOCOLO_X), "sha256": sha256_arquivo(PROTOCOLO_X), "secoes": ["§2", "§3 X4", "§3 X5"]},
        "conferencias": {**conferencias, "reproducao_principal_E9": reproducao,
                         "faixa_impressa_igual_regra_ivs": diag_p["faixa_impressa_igual_regra_ivs"],
                         "cir_contra_malha": conf_malha},
        "estimando": ("variação da resposta da ESCOLHA da 1a opção à bolsa anunciada (+R$ 1 mil) entre grupos (X4) e "
                      "substituição adicional entre células da mesma região de saúde (X5), condicional a candidatar-se "
                      "ao curso; não é efeito sobre o total de candidatos nem sobre a oferta líquida"),
        "x4": {"dimensoes": ROTULO_DIM, "por_modelo": x4_resumo, "escassez": diag_esc,
               "cursos_sem_ponte": cursos_sem_ponte, "adicao_pos_auditoria": NOTA_ADICAO,
               "familia_bky": {"linhas": int(len(q4)), "regra": "termos de interação e Wald da igualdade, p cluster "
                               "por conjunto; dimensão curso fora (inferência por cluster degenerada)"}},
        "x5": {"regioes_saude": {"manifesto": manifesto_cir, "leitura": diag_cir}, "retirados": retirados_x5,
               "por_ciclo": x5_resumo, "especificacoes": {k: v for k, v in ESPEC_X5.items()},
               "familia_bky": {"linhas": int(len(q5)), "regra": "termos de vizinhança (contagem, contagem com total, "
                               "fração) e Wald de lambda = 1 do aninhado convergido, p cluster por conjunto"}},
        "decisoes_de_construcao": [
            "X4a: tercis da pontuação dentro do ciclo, sobre candidatos de 1a opção com pontuação numérica; empate no "
            "corte vai para o tercil de baixo; sem pontuação = grupo próprio (sem imputação)",
            "X4a: conjunto replicado por grupo de candidato (verossimilhança idêntica à do E9 sem interações; conferido)",
            "X4b: limiar de 100 candidatos de 1a opção contado na amostra de cada modelo (ciclo ou empilhado); base = "
            "grupo com mais candidatos",
            "X4c: tercis dentro do conjunto de escolha (curso × ciclo), sobre as células com escassez calculada; "
            "tercil 1 = menos vínculos por habitante (mais escasso); indicadores de grupo também como efeito principal",
            "X4d: base capital, como no E9",
            "X5: CIR oficial do TabNet/DATASUS, não a da malha (cobertura condicionada a ter ativo do PMM-E)",
            "X5: fração de vizinhos com bolsa maior vale 0 sem vizinho, sempre com o indicador de ter vizinho no modelo",
            "X5: a variante com o total de outras células da CIR separa 'ter vizinhos' de 'ter vizinhos de bolsa maior'",
            "X5: logit aninhado iniciado no condicional (lambda = 1), lambda limitado a [0,001; 50] na otimização",
        ],
        "desvios": [
            {"item": "região de saúde", "situacao": "a malha indicada traz região só para municípios com ativo do PMM-E",
             "resolucao": "download público da tabela oficial de CIR (TabNet/DATASUS), permitido pelo §2 do doc 45; "
                          "malha usada só como conferência"},
            {"item": "município sem CIR oficial", "situacao": "município do quadro ausente da tabela de CIR",
             "resolucao": "células e candidatos que as escolheram fora do X5 (contagens em x5.retirados); o principal "
                          "do E9 é reestimado na amostra do X5 (linhas sem_vizinhanca)"},
            {"item": "curso como dimensão", "situacao": "termo próprio do curso só varia nos conjuntos do curso",
             "resolucao": "inferência por cluster marcada como degenerada; EP de MV e por candidato ao lado; fora do BKY"},
            {"item": "cursos sem ponte curso → CBO", "situacao": "cursos fora do catálogo da ponte (lista em x4.cursos_sem_ponte)",
             "resolucao": "grupo sem_ponte_curso_cbo na escassez, sem imputação"},
            {"item": "adição pós-auditoria: estrato com inclinação por ciclo",
             "situacao": "a auditoria independente de X4/X5 observou que o empilhado tem uma só inclinação para os "
                         "três ciclos e que a composição de candidatos por estrato difere entre ciclos",
             "resolucao": f"linhas dimensao = {DIM_ADICAO}, adicao_pos_auditoria = True, fora do BKY; não substituem "
                          "as do doc 45"},
            {"item": "CIR por HTTP", "situacao": "o TabNet não serviu o arquivo por HTTPS",
             "resolucao": "integridade conferida pelo SHA-256 do manifesto a cada execução; o script para se o "
                          "arquivo mudar"},
        ],
        "entradas": entradas,
        "saidas": {rel(p): sha256_arquivo(p) for p in (OUT_X4, OUT_X5, OUT_TABELAS)},
        "linguagem": ("exploratório e pós-resultado: diferenças entre grupos e termos de vizinhança são descritivas da "
                      "escolha, com p e q exploratórios; nenhuma linha é teste confirmatório"),
    }
    OUT_RESUMO.write_text(json.dumps(resumo, ensure_ascii=False, indent=2, default=float) + "\n", encoding="utf-8")
    print(f"gravado: {rel(OUT_X4)}, {rel(OUT_X5)}, {rel(OUT_RESUMO)}, {rel(OUT_TABELAS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
