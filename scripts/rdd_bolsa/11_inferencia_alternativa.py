"""E5 — inferência alternativa para a RDD da bolsa. EXPLORATÓRIO, PÓS-RESULTADO.

Rótulo e escopo
---------------
Escrito em 18/10/2026, DEPOIS de o E3 (protocolo congelado de 14/10/2026) ter
sido estimado e lido: preenchimento −12,8 p.p. [−45,5; +19,8] em 0,300 e
−5,1 p.p. [−36,5; +26,2] em 0,400. Tudo aqui é exploratório e pós-resultado.
O principal continua sendo o do protocolo (local linear, kernel triangular,
h = 0,050, EP HC1; `output/rdd_bolsa/E3_estimativas.csv`). Nenhuma
especificação deste script substitui o principal. Todas as especificações
listadas abaixo são calculadas e gravadas, qualquer que seja o resultado;
nenhuma é escolhida pelo tamanho do IC ou pelo p.

A lista de especificações abaixo foi escrita antes da primeira execução com
dados reais e não é alterada depois de ver números. Correção de erro de
código, se houver, é registrada no documento
`docs/06_execucao/39_inferencia_alternativa_rdd_bolsa.md`, sem mudar a lista.

Pergunta: por que os ICs do E3 são largos, se dá para estreitá-los e se outro
desenho daria inferência melhor ou diferente.

Contraste: incentivo marginal anunciado de R$ 5 mil (Faixa 3 -> 2 em 0,300;
Faixa 2 -> 1 em 0,400), possivelmente um pacote se outra política mudar no
mesmo corte. Não é efeito do PMM-E nem do Agora Tem Especialistas.

Elementos comuns
----------------
- Running variable: IVS 2010 oficial do Ipea em milésimos (s), de
  `output/rdd_bolsa/escore_completo_ivs2010_oficial.csv` (= base a08); cortes
  c em {0,300; 0,400}; o corte pertence ao lado inferior; T = 1[s > c];
  x = s - c.
- Janela h = 0,050: lado inferior (c - h, c], superior (c, c + h]; kernel
  triangular w = max(0, 1 - |x|/h) (o ponto s = c + h tem peso zero).
- Outcomes:
  Y1  fração das células CNES-curso do quadro da 1a chamada do ciclo 1 com
      alguma confirmação ou homologação (P1: 368 municípios, 1.295 células;
      `output/rdd_bolsa/E4_proporcao_municipio.csv`, coluna y1, conferida
      contra a matriz do funil e contra as células canônicas). Outcome da
      hipótese.
  D1  especialista ativo do ciclo 1 no município em 09/10/2026 (P1). Secundário.
  D2  especialista ativo do ciclo 2 no município em 09/10/2026 (P2: 454
      municípios). Secundário.
- IC 95% e p bicaudal pela normal, exceto em D (permutação).
- Em toda especificação: limites unilaterais de 95% (superior e inferior);
  p do teste unilateral de H0: tau >= Delta; p do TOST (equivalência em
  [-Delta, +Delta]) para Delta = 0,10, 0,15 e 0,20; MDE = 2,8 x EP (80% de
  poder, 5% bicaudal).

Especificações
--------------
S0  Principal congelado, reproduzido (não é especificação nova): local linear,
    triangular, h = 0,050, HC1. Tem de igualar `E3_estimativas.csv`; se não
    igualar, o script para. Y1, D1, D2.
A   Local constante: diferença das médias ponderadas pelo kernel triangular,
    h = 0,050 (MQP de y em [1, T]), HC1. Y1, D1, D2.
B   Cortes empilhados: x = s - c; interceptos e inclinações por corte x lado,
    salto tau comum; triangular h = 0,050. As janelas (0,250; 0,350] e
    (0,350; 0,450] não se sobrepõem; o script confere: sem município repetido,
    HC1; com repetição, CR1 por município. Estimando: média ponderada dos dois
    saltos locais (Cattaneo, Keele, Titiunik e Vazquez-Bare, 2016). Y1, D1, D2.
C1  Local linear com covariáveis pré (Calonico, Cattaneo, Farrell e Titiunik,
    2019), triangular h = 0,050, HC1. Z1 = estrato territorial (capital,
    metropolitano, interior próximo de polo; referência interior remoto),
    macrorregião pelo 1o dígito do código IBGE (NE, SE, S, CO; referência N)
    e log da população 2010 (a08). Y1, D1, D2.
C2  C1 + IDHM 2010 (a08). Y1, D1, D2.
    Fora de C1/C2: o IVS e seus três subíndices (componentes mecânicos da
    running variable); renda per capita (insumo do IDHM-renda, redundante com
    o IDHM de C2); UF (27 categorias para cerca de 110 municípios); e as
    colunas de IVS, IDHM, população, renda e estoque da tipologia, que vêm do
    arquivo local errado (auditoria 16). Da tipologia só se usa o estrato.
    Coluna sem variação na amostra, ou colinear, é descartada na ordem da
    lista e registrada.
D   Local randomization (Cattaneo, Frandsen e Titiunik, 2015; Cattaneo,
    Titiunik e Vazquez-Bare, 2016).
    - Janelas candidatas simétricas em mass points de 0,001:
      W(w) = (c - w, c] U (c, c + w], w = 0,002; 0,003; ...; 0,020.
      Viável: pelo menos 2 municípios de cada lado.
    - Seleção SÓ por balanço, gravada em `E5_lr_selecao_janela.csv` ANTES de
      qualquer outcome ser lido. Covariáveis: log população 2010 e IDHM 2010
      (numéricas: |diferença de médias|); estrato e macrorregião (categóricas:
      qui-quadrado de Pearson da tabela 2 x K). p de Fisher por 10.000
      permutações da indicadora de lado dentro da janela,
      p = (1 + #{T_perm >= T_obs}) / (R + 1).
      Regra: w* = maior w viável tal que o p mínimo de balanço é >= 0,15 em
      W(w) e em toda janela viável menor. Janela inviável não reprova nem pode
      ser escolhida. Se a menor janela viável reprovar, não há janela.
    - Inferência: diferença de médias simples na janela; p de Fisher bicaudal
      (|T|) com 10.000 permutações; IC 95% por inversão do teste sob efeito
      aditivo constante, grade de -1 a +1 com passo 0,001; limites
      unilaterais e TOST pelos testes unilaterais de permutação. A coluna
      "ep" de D é o desvio-padrão da distribuição de permutação sob o nulo
      exato (só para comparar precisão; MDE = 2,8 x esse valor).
    - Sementes: numpy default_rng((20261018, k da população, corte em
      milésimos, w em milésimos)).
    - Sensibilidade: o mesmo para todas as janelas viáveis
      (`E5_lr_sensibilidade_janelas.csv`). Y1, D1, D2.
E0  Município, peso = kernel triangular x número de células (sensibilidade
    prevista no adendo E4), HC1. Só Y1. Estimando: salto médio ponderado por
    célula.
E1  Célula CNES-curso (1.295 células em 368 municípios, reconstituídas pela
    fonte canônica de `08a_reconstruir_proporcao_preenchida.py` e conferidas
    contra Y1), y da célula binário, peso = kernel do município, EP CR1 por
    município. Mesmo ponto que E0. Só Y1.
E2  E1 + efeitos fixos de curso (especialidade). Só Y1.
F1  Presença, ciclos empilhados em cada corte: D1 em P1 e D2 em P2; intercepto
    e inclinações por ciclo x lado; tau comum; triangular h = 0,050; CR1 por
    município (o mesmo município pode estar em P1 e em P2).
F2  Presença, ciclos e cortes empilhados: interceptos e inclinações por
    ciclo x corte x lado; tau comum; CR1 por município.

Decomposição da largura do IC (Y1, cada corte, mesma amostra do principal:
municípios com peso triangular positivo)
- DM: diferença de médias simples (kernel uniforme, grau 0), HC1;
- LC: local constante triangular (= A);
- LLU: local linear com kernel uniforme;
- LLT: local linear triangular (= principal).
Fatores: kernel = LC/DM; inclinações = LLT/LC; total = LLT/DM; e o caminho
DM -> LLU -> LLT. Referência teórica para desenho uniforme: raiz(4/3) = 1,155;
raiz(3,6) = 1,897; raiz(4,8) = 2,191. Por lado: n, n efetivo de Kish, média e
desvio-padrão de Y1, médias ponderadas de x e de Y1, intercepto no corte e
inclinação. Identidade: média ponderada acima - abaixo = tau + (b + d) x1 - b x0.
Cenários ilustrativos de poder (rotulados; não são observações): EP e MDE
escalados por raiz(1/n0 + 1/n1) para (i) P1 U P2 na janela e (ii) todos os
municípios do Brasil na janela; n necessário para MDE de 10 p.p.

Avaliação de outros desenhos (controle sintético, DiD, extrapolação com
múltiplos cortes, RD geográfica, mais ciclos): só no documento 39, sem
estimação.

Saídas em output/rdd_bolsa/
---------------------------
E5_lr_selecao_janela.csv (gravado antes dos outcomes), E5_especificacoes.csv,
E5_lr_sensibilidade_janelas.csv, E5_decomposicao_ic.csv,
E5_decomposicao_lados.csv e E5_resumo.json (fontes, hashes, regras).

Uso
---
    python3 scripts/rdd_bolsa/11_inferencia_alternativa.py
    python3 scripts/rdd_bolsa/11_inferencia_alternativa.py --escore CAMINHO.csv

As funções são importáveis pelo teste sintético
(`tests/test_e5_inferencia_sintetico.py`). Dados sintéticos só podem ser
gravados fora de `output/` e `data/` (guarda em `executar`).
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SCRIPT_E3 = ROOT / "scripts" / "rdd_bolsa" / "07_estimar_E3_rdd_completa.py"
SCRIPT_E4A = ROOT / "scripts" / "rdd_bolsa" / "08a_reconstruir_proporcao_preenchida.py"


def _importar(caminho: Path, nome: str):
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


E3 = _importar(SCRIPT_E3, "e3_rdd_completa_para_e5")

PROTOCOLO = ROOT / "output" / "rdd_bolsa" / "protocolo_escore_administrativo.json"
ADENDO_E4 = ROOT / "output" / "rdd_bolsa" / "protocolo_E4_adendo_proporcao.json"
ESCORE_PADRAO = ROOT / "output" / "rdd_bolsa" / "escore_completo_ivs2010_oficial.csv"
A08 = ROOT / "output" / "aquisicao" / "a08_ivs_2010_oficial_municipio.csv"
TIPOLOGIA = ROOT / "output" / "tema_trabalho" / "matriz_tipologia_territorial.parquet"
E4_MUNICIPIO = ROOT / "output" / "rdd_bolsa" / "E4_proporcao_municipio.csv"
FUNIL = ROOT / "output" / "tema_trabalho" / "matriz_funil_ciclo1.parquet"
QUADRO_CANONICO = ROOT / "output" / "aquisicao" / "quadro_vagas_tratamento.parquet"
ATIVOS_ZIP = ROOT / "data" / "raw" / "aquisicao" / "ivs_administrativo" / "tb_profissionais_ativos_pmme_csv.zip"
E3_ESTIMATIVAS = ROOT / "output" / "rdd_bolsa" / "E3_estimativas.csv"
SAIDA_DIR = ROOT / "output" / "rdd_bolsa"

NOME_LR_SELECAO = "E5_lr_selecao_janela.csv"
NOME_ESPEC = "E5_especificacoes.csv"
NOME_LR_SENS = "E5_lr_sensibilidade_janelas.csv"
NOME_DECOMP = "E5_decomposicao_ic.csv"
NOME_LADOS = "E5_decomposicao_lados.csv"
NOME_RESUMO = "E5_resumo.json"

DATA_EXECUCAO = "2026-10-18"
ROTULO = "EXPLORATORIO_POS_RESULTADO"
ROTULO_S0 = "PRINCIPAL_CONGELADO_REPRODUZIDO"

CORTES_MIL = (300, 400)
H_MIL = 50
LR_JANELAS_MIL = tuple(range(2, 21))
LR_LIMIAR_BALANCO = 0.15
LR_N_MIN_LADO = 2
N_PERMUTACOES = 10_000
SEMENTE = 20261018
GRADE_TAU = np.round(np.arange(-1000, 1001) / 1000.0, 3)
MARGENS = (0.10, 0.15, 0.20)
ALFA = 0.05
Z_975 = E3.Z_975
Z_95 = 1.6448536269514722
FATOR_MDE = 2.8
TOL = 1e-10
SALTO_ANUNCIADO_BRL = 5_000

OUTCOMES = {
    "Y1": {"populacao": "P1", "ciclo": 1, "papel": "outcome da hipotese",
           "descricao": "fracao das celulas CNES-curso do quadro da 1a chamada do ciclo 1 com alguma "
                        "confirmacao ou homologacao (E4 y1)"},
    "D1": {"populacao": "P1", "ciclo": 1, "papel": "secundario",
           "descricao": "especialista ativo do ciclo 1 no municipio em 09/10/2026"},
    "D2": {"populacao": "P2", "ciclo": 2, "papel": "secundario (replicacao)",
           "descricao": "especialista ativo do ciclo 2 no municipio em 09/10/2026"},
}

ESTRATOS_DUMMIES = ["estrato_capital", "estrato_metropolitano", "estrato_interior_proximo_polo"]
REGIOES = {"1": "N", "2": "NE", "3": "SE", "4": "S", "5": "CO"}
REGIOES_DUMMIES = ["regiao_NE", "regiao_SE", "regiao_S", "regiao_CO"]
COV_C1 = ESTRATOS_DUMMIES + REGIOES_DUMMIES + ["log_populacao_2010"]
COV_C2 = COV_C1 + ["idhm_2010"]
COV_LR = (("log_populacao_2010", "numerica"), ("idhm_2010", "numerica"),
          ("estrato", "categorica"), ("regiao", "categorica"))

ESPECIFICACOES = [
    {"id": "S0", "outcomes": ["Y1", "D1", "D2"], "unidade": "municipio",
     "descricao": "principal congelado reproduzido: local linear, triangular, h=0,050, HC1"},
    {"id": "A", "outcomes": ["Y1", "D1", "D2"], "unidade": "municipio",
     "descricao": "local constante: diferenca de medias ponderadas pelo kernel triangular, h=0,050, HC1"},
    {"id": "B", "outcomes": ["Y1", "D1", "D2"], "unidade": "municipio",
     "descricao": "cortes empilhados: x=s-c, interceptos e inclinacoes por corte x lado, tau comum, triangular h=0,050"},
    {"id": "C1", "outcomes": ["Y1", "D1", "D2"], "unidade": "municipio",
     "descricao": "local linear triangular h=0,050 + estrato, macrorregiao, log populacao 2010 (a08), HC1"},
    {"id": "C2", "outcomes": ["Y1", "D1", "D2"], "unidade": "municipio",
     "descricao": "C1 + IDHM 2010 (a08), HC1"},
    {"id": "D", "outcomes": ["Y1", "D1", "D2"], "unidade": "municipio",
     "descricao": "local randomization: janela por balanco de covariaveis; diferenca de medias; Fisher; IC por inversao"},
    {"id": "E0", "outcomes": ["Y1"], "unidade": "municipio",
     "descricao": "local linear triangular h=0,050, peso kernel x n_celulas, HC1"},
    {"id": "E1", "outcomes": ["Y1"], "unidade": "celula CNES-curso",
     "descricao": "celula CNES-curso, peso kernel do municipio, CR1 por municipio"},
    {"id": "E2", "outcomes": ["Y1"], "unidade": "celula CNES-curso",
     "descricao": "E1 + efeitos fixos de curso, CR1 por municipio"},
    {"id": "F1", "outcomes": ["D1+D2"], "unidade": "municipio x ciclo",
     "descricao": "presenca, ciclos 1 e 2 empilhados por corte; intercepto e inclinacoes por ciclo x lado; tau comum; CR1"},
    {"id": "F2", "outcomes": ["D1+D2"], "unidade": "municipio x ciclo",
     "descricao": "presenca, ciclos e cortes empilhados; interceptos e inclinacoes por ciclo x corte x lado; tau comum; CR1"},
]

CONTRASTE = (
    "incentivo marginal anunciado de R$ 5 mil (Faixa 3->2 em 0,300; Faixa 2->1 em 0,400), "
    "possivelmente pacote se outra politica mudar no mesmo corte; nao e efeito do PMM-E "
    "nem do Agora Tem Especialistas"
)


# ---------------------------------------------------------------------------
# Utilitários
# ---------------------------------------------------------------------------

def sha256(path: Path) -> str:
    return E3.sha256(Path(path))


def rotulo(path: Path) -> str:
    return E3.rotulo(Path(path))


def cdf_normal(z: float) -> float:
    return 0.5 * math.erfc(-z / math.sqrt(2.0))


def sf_normal(z: float) -> float:
    return 0.5 * math.erfc(z / math.sqrt(2.0))


def _tag(delta: float) -> str:
    return f"{int(round(delta * 100)):03d}"


def _nan_para_none(obj):
    if isinstance(obj, dict):
        return {k: _nan_para_none(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_nan_para_none(v) for v in obj]
    if isinstance(obj, (np.floating,)):
        obj = float(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, float) and not math.isfinite(obj):
        return None
    return obj


def _gravar_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(_nan_para_none(obj), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _gravar_csv(path: Path, df: pd.DataFrame) -> None:
    df.to_csv(path, index=False, lineterminator="\n")


def _guarda_saida(saida_dir: Path, natureza: str, root: Path) -> None:
    if natureza == "EMPIRICO":
        return
    alvo = Path(saida_dir).resolve()
    for proibido in (root / "output", root / "data"):
        p = proibido.resolve()
        if alvo == p or p in alvo.parents:
            raise ValueError(f"dados {natureza} nao podem ser gravados em {rotulo(p)}")


# ---------------------------------------------------------------------------
# Mínimos quadrados ponderados com variância sanduíche (numpy)
# ---------------------------------------------------------------------------

def mqp_robusto(X, y, w, nomes: list[str], protegidas: set[str], cluster=None) -> dict:
    """MQP com EP HC1 (sem cluster) ou CR1 (cluster).

    Colunas não protegidas sem variação ou colineares são descartadas na ordem
    dada (determinístico). Coluna protegida colinear devolve erro.
    HC1: V = B M B * n/(n-k). CR1: V = B M_g B * G/(G-1) * (n-1)/(n-k).
    """
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    w = np.asarray(w, dtype=float)
    n = len(y)
    sw = np.sqrt(w)
    manter: list[int] = []
    descartadas: list[str] = []
    for j in range(X.shape[1]):
        cand = manter + [j]
        M = X[:, cand] * sw[:, None]
        normas = np.linalg.norm(M, axis=0)
        ok = bool(normas[-1] > 0) and np.linalg.matrix_rank(M / np.where(normas > 0, normas, 1.0), tol=1e-9) == len(cand)
        if ok:
            manter.append(j)
        elif nomes[j] in protegidas:
            return {"erro": f"coluna protegida '{nomes[j]}' sem variacao ou colinear"}
        else:
            descartadas.append(nomes[j])
    k = len(manter)
    if n <= k:
        return {"erro": "graus de liberdade insuficientes"}
    Xk = X[:, manter]
    XtWX = Xk.T @ (Xk * w[:, None])
    bread = np.linalg.inv(XtWX)
    beta = bread @ (Xk.T @ (w * y))
    e = y - Xk @ beta
    score = Xk * (w * e)[:, None]
    G = None
    if cluster is None:
        V = bread @ (score.T @ score) @ bread * (n / (n - k))
    else:
        _, idx = np.unique(np.asarray(cluster).astype(str), return_inverse=True)
        G = int(idx.max()) + 1
        if G < 2:
            return {"erro": "menos de 2 clusters"}
        S = np.zeros((G, k))
        np.add.at(S, idx, score)
        V = bread @ (S.T @ S) @ bread * (G / (G - 1)) * ((n - 1) / (n - k))
    nomes_k = [nomes[j] for j in manter]
    return {"beta": dict(zip(nomes_k, beta.tolist())), "V": V, "nomes": nomes_k, "n": n, "k": k,
            "G": G, "descartadas": descartadas, "residuos": e}


def pesos_kernel(x_mil: np.ndarray, h_mil: int, kernel: str) -> np.ndarray:
    """Peso do kernel na amostra do principal: -h < x < h (s = c + h fica fora)."""
    x_mil = np.asarray(x_mil, dtype=float)
    dentro = (x_mil > -h_mil) & (x_mil < h_mil)
    if kernel == "triangular":
        return np.where(dentro, 1.0 - np.abs(x_mil) / h_mil, 0.0)
    if kernel == "uniforme":
        return dentro.astype(float)
    raise ValueError(f"kernel desconhecido: {kernel}")


def _resultado_vazio() -> dict:
    return {"tau": float("nan"), "ep": float("nan"), "ic95_inf": float("nan"), "ic95_sup": float("nan"),
            "p_valor": float("nan"), "n_abaixo": 0, "n_acima": 0, "n_obs": 0, "n_clusters": None,
            "covariaveis_descartadas": "", "nota": ""}


def _preencher_inferencia_normal(res: dict, fit: dict, nome_coef: str = "T") -> dict:
    i = fit["nomes"].index(nome_coef)
    tau = float(fit["beta"][nome_coef])
    ep = float(math.sqrt(max(fit["V"][i, i], 0.0)))
    res.update({"tau": tau, "ep": ep, "ic95_inf": tau - Z_975 * ep, "ic95_sup": tau + Z_975 * ep,
                "p_valor": E3.p_normal(tau / ep) if ep > 0 else float("nan"),
                "n_clusters": fit["G"], "covariaveis_descartadas": ";".join(fit["descartadas"])})
    if not ep > 0:
        res["nota"] = "EP nulo"
    return res


def rd_local(s_mil, y, corte_mil: int, h_mil: int = H_MIL, *, grau: int = 1, kernel: str = "triangular",
             Z=None, nomes_z=(), peso=None, cluster=None) -> dict:
    """RDD sharp local (grau 0 ou 1) com covariáveis opcionais, pesos extras e cluster.

    y = a + b*x + tau*T + d*T*x + Z'g (grau 1) ou y = a + tau*T + Z'g (grau 0),
    MQP com pesos do kernel (vezes `peso`), x = s - c em unidades de IVS.
    `n_abaixo`/`n_acima` contam municípios (clusters distintos, se houver
    cluster); `n_obs` conta linhas.
    """
    s = np.asarray(s_mil, dtype=int)
    yv = np.asarray(y, dtype=float)
    x_mil = s - corte_mil
    w = pesos_kernel(x_mil, h_mil, kernel)
    if peso is not None:
        w = w * np.asarray(peso, dtype=float)
    x = x_mil / 1000.0
    t = (x_mil > 0).astype(float)
    cols, nomes = [np.ones_like(x)], ["const"]
    if grau == 1:
        cols.append(x)
        nomes.append("x")
    cols.append(t)
    nomes.append("T")
    if grau == 1:
        cols.append(t * x)
        nomes.append("T_x")
    protegidas = set(nomes)
    nomes_z = list(nomes_z)
    if Z is not None and nomes_z:
        Zm = np.asarray(Z, dtype=float).reshape(len(s), len(nomes_z))
        cols.extend(Zm[:, j] for j in range(len(nomes_z)))
        nomes.extend(nomes_z)
    X = np.column_stack(cols)
    usa = (w > 0) & np.isfinite(yv) & np.isfinite(X).all(axis=1)
    ab, ac = usa & (x_mil <= 0), usa & (x_mil > 0)
    ids = np.asarray(cluster).astype(str) if cluster is not None else None
    res = _resultado_vazio()
    res.update({
        "n_abaixo": int(np.unique(ids[ab]).size) if ids is not None else int(ab.sum()),
        "n_acima": int(np.unique(ids[ac]).size) if ids is not None else int(ac.sum()),
        "n_obs": int(usa.sum()),
        "mass_points_abaixo": int(np.unique(s[ab]).size),
        "mass_points_acima": int(np.unique(s[ac]).size),
    })
    minimo = 2 if grau == 1 else 1
    if res["mass_points_abaixo"] < minimo or res["mass_points_acima"] < minimo:
        res["nota"] = "suporte insuficiente"
        return res
    fit = mqp_robusto(X[usa], yv[usa], w[usa], nomes, protegidas, cluster=ids[usa] if ids is not None else None)
    if "erro" in fit:
        res["nota"] = fit["erro"]
        return res
    _preencher_inferencia_normal(res, fit)
    res["_fit"] = fit
    res["_usa"] = usa
    res["_w"] = w
    return res


def rd_empilhado(s_mil, y, corte_mil, grupo, *, h_mil: int = H_MIL, cluster=None, ids_municipio=None) -> dict:
    """Saltos empilhados: interceptos e inclinações por grupo x lado; tau comum.

    Cada linha tem seu corte (`corte_mil`) e seu grupo (corte, ciclo ou
    ciclo x corte). Kernel triangular h. `ids_municipio` conta municípios
    distintos por lado; `cluster` (ou None para HC1) define o EP.
    """
    s = np.asarray(s_mil, dtype=int)
    c = np.asarray(corte_mil, dtype=int)
    yv = np.asarray(y, dtype=float)
    g = np.asarray(grupo).astype(str)
    x_mil = s - c
    w = pesos_kernel(x_mil, h_mil, "triangular")
    x = x_mil / 1000.0
    t = (x_mil > 0).astype(float)
    cols, nomes = [], []
    for grp in sorted(np.unique(g)):
        ind = (g == grp).astype(float)
        cols.extend([ind, ind * x, ind * t * x])
        nomes.extend([f"const[{grp}]", f"x[{grp}]", f"T_x[{grp}]"])
    cols.append(t)
    nomes.append("T")
    X = np.column_stack(cols)
    usa = (w > 0) & np.isfinite(yv)
    ab, ac = usa & (x_mil <= 0), usa & (x_mil > 0)
    ids = np.asarray(ids_municipio).astype(str) if ids_municipio is not None else None
    res = _resultado_vazio()
    res.update({
        "n_abaixo": int(np.unique(ids[ab]).size) if ids is not None else int(ab.sum()),
        "n_acima": int(np.unique(ids[ac]).size) if ids is not None else int(ac.sum()),
        "n_obs": int(usa.sum()),
    })
    cl = np.asarray(cluster).astype(str)[usa] if cluster is not None else None
    fit = mqp_robusto(X[usa], yv[usa], w[usa], nomes, set(nomes), cluster=cl)
    if "erro" in fit:
        res["nota"] = fit["erro"]
        return res
    _preencher_inferencia_normal(res, fit)
    res["_fit"] = fit
    return res


def equivalencia_normal(tau: float, ep: float) -> dict:
    """Limites unilaterais de 95%, H0: tau >= Delta e TOST em [-Delta, +Delta]."""
    out = {"lim_sup_unilateral_95": tau + Z_95 * ep, "lim_inf_unilateral_95": tau - Z_95 * ep,
           "mde_80": FATOR_MDE * ep}
    for d in MARGENS:
        if ep > 0 and math.isfinite(tau):
            p_ge = cdf_normal((tau - d) / ep)   # H0: tau >= +d contra H1: tau < +d
            p_le = sf_normal((tau + d) / ep)    # H0: tau <= -d contra H1: tau > -d
        else:
            p_ge = p_le = float("nan")
        out[f"p_unilateral_tau_ge_{_tag(d)}"] = p_ge
        out[f"p_tost_{_tag(d)}"] = max(p_ge, p_le) if math.isfinite(p_ge) else float("nan")
    return out


# ---------------------------------------------------------------------------
# Local randomization
# ---------------------------------------------------------------------------

def id_populacao(nome_pop: str) -> int:
    return int(str(nome_pop).lstrip("P"))


def janela_lr(s_mil, corte_mil: int, w_mil: int) -> tuple[np.ndarray, np.ndarray]:
    x = np.asarray(s_mil, dtype=int) - corte_mil
    return (x > -w_mil) & (x <= w_mil), (x > 0)


def matriz_permutacao(n: int, n1: int, r: int, semente: tuple) -> np.ndarray:
    """R x n indicadoras de "tratado" sob permutação completa (n1 fixo)."""
    rng = np.random.default_rng(list(semente))
    ordem = np.argsort(rng.random((r, n)), axis=1, kind="stable")
    P = np.zeros((r, n))
    np.put_along_axis(P, ordem[:, :n1], 1.0, axis=1)
    return P


def p_permutacao_maior(perm: np.ndarray, obs: float) -> float:
    return float((1 + np.sum(perm >= obs - TOL)) / (len(perm) + 1))


def estatistica_balanco(P: np.ndarray, z: np.ndarray, t: np.ndarray, tipo: str) -> tuple[np.ndarray, float]:
    t = np.asarray(t, dtype=bool)
    n = len(t)
    n1 = int(t.sum())
    n0 = n - n1
    if tipo == "numerica":
        z = np.asarray(z, dtype=float)
        sz = P @ z
        tot = z.sum()
        perm = np.abs(sz / n1 - (tot - sz) / n0)
        obs = abs(z[t].mean() - z[~t].mean())
        return perm, float(obs)
    z = np.asarray(z).astype(str)
    niveis = sorted(set(z.tolist()))
    if len(niveis) < 2:
        return np.zeros(P.shape[0]), 0.0
    ind = np.column_stack([(z == k).astype(float) for k in niveis])
    nk = ind.sum(axis=0)
    e1, e0 = n1 * nk / n, n0 * nk / n
    o1 = P @ ind
    perm = (((o1 - e1) ** 2) / e1 + (((nk - o1) - e0) ** 2) / e0).sum(axis=1)
    o1_obs = ind[t].sum(axis=0)
    obs = float((((o1_obs - e1) ** 2) / e1 + (((nk - o1_obs) - e0) ** 2) / e0).sum())
    return perm, obs


def selecionar_janela(pop_cov: pd.DataFrame, nome_pop: str, n_perm: int = N_PERMUTACOES) -> pd.DataFrame:
    """Seleção da janela de local randomization SÓ com covariáveis pré.

    `pop_cov` tem co_ibge, s_mil e as colunas de COV_LR; nenhum outcome.
    """
    linhas = []
    s = pop_cov["s_mil"].to_numpy(dtype=int)
    for corte in CORTES_MIL:
        alguma_reprovou = False
        for w in LR_JANELAS_MIL:
            dentro, trat = janela_lr(s, corte, w)
            n1 = int((dentro & trat).sum())
            n0 = int((dentro & ~trat).sum())
            viavel = n0 >= LR_N_MIN_LADO and n1 >= LR_N_MIN_LADO
            linha = {"populacao": nome_pop, "corte": corte / 1000, "w": w / 1000,
                     "janela_inf_exclusivo": (corte - w) / 1000, "janela_sup_inclusivo": (corte + w) / 1000,
                     "n_abaixo": n0, "n_acima": n1, "viavel": viavel}
            if viavel:
                sub = pop_cov.loc[dentro]
                t_sub = trat[dentro]
                P = matriz_permutacao(len(sub), n1, n_perm, (SEMENTE, id_populacao(nome_pop), corte, w))
                ps = {}
                for nome_cov, tipo in COV_LR:
                    perm, obs = estatistica_balanco(P, sub[nome_cov].to_numpy(), t_sub, tipo)
                    ps[nome_cov] = p_permutacao_maior(perm, obs)
                    linha[f"p_{nome_cov}"] = ps[nome_cov]
                linha["p_min"] = min(ps.values())
                linha["passa"] = bool(linha["p_min"] >= LR_LIMIAR_BALANCO)
                if not linha["passa"]:
                    alguma_reprovou = True
            else:
                for nome_cov, _ in COV_LR:
                    linha[f"p_{nome_cov}"] = float("nan")
                linha["p_min"] = float("nan")
                linha["passa"] = None
            linha["todas_ate_aqui_passam"] = not alguma_reprovou
            linhas.append(linha)
    df = pd.DataFrame(linhas)
    df["selecionada"] = False
    for corte in CORTES_MIL:
        cand = df[(df["corte"] == corte / 1000) & df["viavel"] & df["todas_ate_aqui_passam"]]
        if len(cand):
            df.loc[cand.index[-1], "selecionada"] = True
    return df


def p_fisher_dif_medias(y: np.ndarray, t: np.ndarray, P: np.ndarray) -> float:
    """p de Fisher bicaudal (|diferença de médias|) sob o nulo exato de efeito zero."""
    y = np.asarray(y, dtype=float)
    t = np.asarray(t, dtype=bool)
    n1 = int(t.sum())
    n0 = len(y) - n1
    sy = P @ y
    perm = np.abs(sy / n1 - (y.sum() - sy) / n0)
    return p_permutacao_maior(perm, abs(float(y[t].mean() - y[~t].mean())))


def inferencia_lr(y: np.ndarray, t: np.ndarray, P: np.ndarray) -> dict:
    """Fisher (bicaudal |T|), IC por inversão sob efeito constante, unilaterais e TOST.

    Sob H0: tau = tau0 (efeito aditivo constante), y - tau0*T são os outcomes
    potenciais sem tratamento, fixos sob permutação. Para a permutação pi, a
    estatística é a_pi + tau0*b_pi (linear em tau0); a observada é dif - tau0.
    """
    y = np.asarray(y, dtype=float)
    t = np.asarray(t, dtype=bool)
    n = len(y)
    n1 = int(t.sum())
    n0 = n - n1
    r = P.shape[0]
    media_ac, media_ab = float(y[t].mean()), float(y[~t].mean())
    dif = media_ac - media_ab
    sy = P @ y
    st = P @ t.astype(float)
    tot = y.sum()
    a = sy / n1 - (tot - sy) / n0          # estatística permutada sob tau0 = 0
    b = -st / n1 + (n1 - st) / n0          # derivada em tau0

    def pvals(taus: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        stats = a[None, :] + taus[:, None] * b[None, :]
        obs = (dif - taus)[:, None]
        p2 = (1 + (np.abs(stats) >= np.abs(obs) - TOL).sum(axis=1)) / (r + 1)
        p_le = (1 + (stats <= obs + TOL).sum(axis=1)) / (r + 1)   # H1: tau < tau0
        p_ge = (1 + (stats >= obs - TOL).sum(axis=1)) / (r + 1)   # H1: tau > tau0
        return p2, p_le, p_ge

    p2s, ples, pges = [], [], []
    for i in range(0, len(GRADE_TAU), 200):
        p2, ple, pge = pvals(GRADE_TAU[i:i + 200])
        p2s.append(p2)
        ples.append(ple)
        pges.append(pge)
    p2 = np.concatenate(p2s)
    ple = np.concatenate(ples)
    pge = np.concatenate(pges)
    aceitos = np.flatnonzero(p2 > ALFA)
    p_fisher = float(pvals(np.array([0.0]))[0][0])
    res = {
        "media_abaixo": media_ab, "media_acima": media_ac, "tau": dif,
        "ep": float(np.std(a, ddof=1)), "p_valor": p_fisher,
        "ic95_inf": float(GRADE_TAU[aceitos.min()]) if aceitos.size else float("nan"),
        "ic95_sup": float(GRADE_TAU[aceitos.max()]) if aceitos.size else float("nan"),
        "ic_contiguo": bool(aceitos.size and (aceitos.max() - aceitos.min() + 1 == aceitos.size)),
        "ic_toca_borda_da_grade": bool(aceitos.size and (aceitos.min() == 0 or aceitos.max() == len(GRADE_TAU) - 1)),
        "lim_sup_unilateral_95": float(GRADE_TAU[ple > ALFA].max()) if (ple > ALFA).any() else float("nan"),
        "lim_inf_unilateral_95": float(GRADE_TAU[pge > ALFA].min()) if (pge > ALFA).any() else float("nan"),
    }
    res["mde_80"] = FATOR_MDE * res["ep"]
    for d in MARGENS:
        _, ple_d, _ = pvals(np.array([d]))
        _, _, pge_md = pvals(np.array([-d]))
        res[f"p_unilateral_tau_ge_{_tag(d)}"] = float(ple_d[0])
        res[f"p_tost_{_tag(d)}"] = float(max(ple_d[0], pge_md[0]))
    return res


# ---------------------------------------------------------------------------
# Covariáveis (pré) e outcomes (reais)
# ---------------------------------------------------------------------------

def preparar_covariaveis(base: pd.DataFrame) -> pd.DataFrame:
    """Recebe co_ibge, log_populacao_2010, idhm_2010, estrato, regiao; cria dummies."""
    cov = base.copy()
    cov["co_ibge"] = cov["co_ibge"].astype(str)
    for nome in ESTRATOS_DUMMIES:
        cov[nome] = (cov["estrato"].astype(str) == nome.removeprefix("estrato_")).astype(float)
    for nome in REGIOES_DUMMIES:
        cov[nome] = (cov["regiao"].astype(str) == nome.removeprefix("regiao_")).astype(float)
    return cov


def carregar_covariaveis_e5(root: Path = ROOT) -> tuple[pd.DataFrame, dict]:
    a08_path = root / "output" / "aquisicao" / "a08_ivs_2010_oficial_municipio.csv"
    tip_path = root / "output" / "tema_trabalho" / "matriz_tipologia_territorial.parquet"
    a08 = pd.read_csv(a08_path, dtype={"co_ibge": str})
    a08["co_ibge"] = E3.normalizar_ibge(a08["co_ibge"]).str.zfill(6)
    pop = pd.to_numeric(a08["populacao"], errors="raise")
    base = pd.DataFrame({
        "co_ibge": a08["co_ibge"],
        "log_populacao_2010": np.where(pop > 0, np.log(pop.where(pop > 0)), np.nan),
        "idhm_2010": pd.to_numeric(a08["idhm"], errors="raise"),
        "regiao": a08["co_ibge"].str[0].map(REGIOES),
    })
    tip = pd.read_parquet(tip_path, columns=["co_ibge_6d", "estrato"])
    tip["co_ibge"] = tip["co_ibge_6d"].astype(str).str.replace(r"\D", "", regex=True).str.zfill(6)
    base = base.merge(tip[["co_ibge", "estrato"]], on="co_ibge", how="left", validate="one_to_one")
    notas = {
        rotulo(a08_path): {
            "sha256": sha256(a08_path),
            "fonte": "Atlas da Vulnerabilidade Social (Ipea), base completa, linha Total/Total/Total de 2010 (a08)",
            "data_referencia": "Censo 2010",
            "cobertura": f"{len(a08)} municipios (malha 2010)",
            "unidade": "municipio", "chaves": "co_ibge (6 digitos)",
            "colunas_usadas": ["co_ibge", "populacao (log)", "idhm"],
            "filtros": "nenhum",
        },
        rotulo(tip_path): {
            "sha256": sha256(tip_path),
            "fonte": "tipologia territorial A2 (capitais, RM/RIDE 2022, REGIC 2018)",
            "data_referencia": "REGIC 2018; RM/RIDE 2022",
            "cobertura": f"{len(tip)} municipios",
            "unidade": "municipio", "chaves": "co_ibge_6d",
            "colunas_usadas": ["co_ibge_6d", "estrato"],
            "filtros": "nenhum",
            "nota": "so o estrato; as colunas de IVS, IDHM, populacao, renda e estoque da tipologia vem do "
                    "arquivo local errado (auditoria 16) e nao sao lidas",
        },
        "macrorregiao": "1o digito do codigo IBGE (1=N, 2=NE, 3=SE, 4=S, 5=CO)",
    }
    return preparar_covariaveis(base), notas


def carregar_outcomes_reais(root: Path = ROOT) -> Callable[[pd.Series, pd.Series], dict]:
    """Devolve o leitor de outcomes; nada é lido até ele ser chamado."""

    def leitor(municipios_p1: pd.Series, municipios_p2: pd.Series) -> dict:
        fontes: dict = {}
        verificacoes: dict = {}
        # Y1 municipal (E4) e verificação contra a matriz do funil usada no E3.
        e4_path = root / "output" / "rdd_bolsa" / "E4_proporcao_municipio.csv"
        e4 = pd.read_csv(e4_path, dtype={"co_ibge": str})
        e4["co_ibge"] = E3.normalizar_ibge(e4["co_ibge"]).str.zfill(6)
        funil_path = root / "output" / "tema_trabalho" / "matriz_funil_ciclo1.parquet"
        frac_e3 = E3.preenchimento_ch1_por_municipio(E3.ler_funil(funil_path), municipios_p1)
        comp = e4.set_index("co_ibge")["y1"].reindex(frac_e3.index)
        dif = float(np.nanmax(np.abs(comp.to_numpy(dtype=float) - frac_e3.to_numpy(dtype=float))))
        if comp.isna().any() or dif > 1e-9:
            raise ValueError(f"Y1 do E4 difere do outcome do E3 (max |dif| = {dif})")
        verificacoes["y1_e4_igual_outcome_e3"] = {"municipios": int(len(comp)), "max_abs_dif": dif}
        # Células canônicas (mesma fonte do 08a).
        e4a = _importar(SCRIPT_E4A, "e4a_reconstrucao_para_e5")
        canon = e4a.carregar_canonica()
        celulas = pd.DataFrame({
            "co_ibge": canon["co_ibge_6d"].astype(str).str.zfill(6),
            "co_cnes_7d": canon["co_cnes_7d"].astype(str),
            "cod_curso": canon["cod_curso"].astype(int),
            "y": canon["y1"].astype(float),
        })
        y1 = e4[["co_ibge", "y1", "n_celulas"]].rename(columns={"y1": "y"})
        fontes[rotulo(e4_path)] = {
            "sha256": sha256(e4_path), "fonte": "08a_reconstruir_proporcao_preenchida.py (fonte canonica do A1/A4)",
            "data_referencia": "1a chamada do ciclo 1 (quadro de 24/07/2025; alocacao e homologados publicados)",
            "cobertura": "P1: 368 municipios, 1.295 celulas", "unidade": "municipio", "chaves": "co_ibge",
            "colunas_usadas": ["co_ibge", "y1", "n_celulas"], "filtros": "nenhum"}
        fontes[rotulo(funil_path)] = {
            "sha256": sha256(funil_path), "fonte": "matriz do funil do ciclo 1 (A1)",
            "data_referencia": "2026-09-01 (A1)", "cobertura": "ciclo 1, chamadas 1 e 2",
            "unidade": "celula CNES-curso x chamada", "chaves": "co_cnes_7d, cod_curso, chamada",
            "colunas_usadas": ["chamada", "in_quadro_ch1_original", "co_ibge_6d", "co_cnes_7d", "cod_curso",
                               "outcome_alguma_confirmacao_ou_homologacao", "n_confirmacoes_ch1",
                               "n_homologacoes_ch1", "n_homologacoes_novas_ch2"],
            "filtros": "chamada 1 (Y1); usada para conferir Y1 e para as celulas de E1/E2"}
        qpath = root / "output" / "aquisicao" / "quadro_vagas_tratamento.parquet"
        fontes[rotulo(qpath)] = {
            "sha256": sha256(qpath), "fonte": "quadro de vagas da 1a chamada do ciclo 1 (tratamento, A1/A4)",
            "data_referencia": "quadro original publicado em 24/07/2025", "cobertura": "1.295 celulas, 368 municipios",
            "unidade": "celula CNES-curso", "chaves": "co_cnes_7d, cod_curso",
            "colunas_usadas": ["co_cnes_7d", "cod_curso", "co_ibge_6d", "faixa_atracao_anunciada"],
            "filtros": "nenhum (quadro completo)"}
        # Presença D1 e D2: relação nominal de 09/10/2026, versão fixada no protocolo.
        zp = root / "data" / "raw" / "aquisicao" / "ivs_administrativo" / "tb_profissionais_ativos_pmme_csv.zip"
        h = sha256(zp)
        if h != E3.SHA256_ATIVOS_PROTOCOLO:
            raise ValueError(f"relacao nominal com SHA-256 {h}, diferente da fixada no protocolo")
        ativos = E3.ler_ativos(zp)
        d1 = E3.construir_d_k(municipios_p1, ativos, 1)
        d2 = E3.construir_d_k(municipios_p2, ativos, 2)
        fontes[rotulo(zp)] = {
            "sha256": h, "fonte": "Relacao Nominal Ativos - PMM-E (dados abertos do MS)",
            "data_referencia": "2026-10-09", "cobertura": "profissionais ativos de todos os ciclos",
            "unidade": "profissional ativo", "chaves": "co_ibge, ciclo",
            "colunas_usadas": ["co_ibge", "ciclo"], "filtros": "ciclo == k; agregado a 1 se ha ao menos um ativo",
            "sha256_confere_protocolo": True}
        return {"Y1": y1, "celulas": celulas, "D1": d1, "D2": d2, "fontes": fontes, "verificacoes": verificacoes}

    return leitor


def carregar_referencia_e3(path: Path = E3_ESTIMATIVAS) -> pd.DataFrame:
    e3 = pd.read_csv(path)
    e3 = e3[e3["especificacao"] == "principal"].copy()
    mapa = {("P1", E3.OUTCOME_D): "D1", ("P2", E3.OUTCOME_D): "D2", ("P1", E3.OUTCOME_PREENCHIMENTO): "Y1"}
    e3["outcome_e5"] = [mapa.get((p, o)) for p, o in zip(e3["populacao"], e3["outcome"])]
    return e3.dropna(subset=["outcome_e5"])[["outcome_e5", "corte", "tau", "ep", "n_abaixo", "n_acima"]]


# ---------------------------------------------------------------------------
# Especificações
# ---------------------------------------------------------------------------

def _linha_spec(spec_id: str, outcome: str, populacao: str, corte, res: dict, *, unidade: str,
                inferencia: str, natureza: str, janela: str = "h=0,050", extra: dict | None = None) -> dict:
    linha = {
        "natureza_dos_dados": natureza,
        "rotulo": ROTULO_S0 if spec_id == "S0" else ROTULO,
        "especificacao": spec_id,
        "descricao": next(e["descricao"] for e in ESPECIFICACOES if e["id"] == spec_id),
        "outcome": outcome,
        "populacao": populacao,
        "corte": corte,
        "janela": janela,
        "unidade": unidade,
        "inferencia": inferencia,
        "n_abaixo": res.get("n_abaixo"),
        "n_acima": res.get("n_acima"),
        "n_obs": res.get("n_obs"),
        "n_clusters": res.get("n_clusters"),
        "tau": res.get("tau"),
        "ep": res.get("ep"),
        "ic95_inf": res.get("ic95_inf"),
        "ic95_sup": res.get("ic95_sup"),
        "p_valor": res.get("p_valor"),
    }
    if "lim_sup_unilateral_95" in res:
        eq = {k: res[k] for k in res if k.startswith(("lim_", "p_unilateral", "p_tost", "mde"))}
    else:
        eq = equivalencia_normal(res["tau"], res["ep"]) if math.isfinite(res.get("ep", float("nan"))) else {}
    linha.update(eq)
    for d in MARGENS:
        p = linha.get(f"p_unilateral_tau_ge_{_tag(d)}", float("nan"))
        linha[f"descarta_tau_ge_{_tag(d)}"] = bool(p < ALFA) if p is not None and math.isfinite(p) else None
        pt = linha.get(f"p_tost_{_tag(d)}", float("nan"))
        linha[f"equivalencia_{_tag(d)}"] = bool(pt < ALFA) if pt is not None and math.isfinite(pt) else None
    linha["covariaveis_descartadas"] = res.get("covariaveis_descartadas", "")
    linha["nota"] = res.get("nota", "")
    if extra:
        linha.update(extra)
    return linha


def estimar_especificacoes(dados: dict, celulas: pd.DataFrame, selecao: pd.DataFrame,
                           natureza: str, n_perm: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Todas as especificações; devolve (especificações, sensibilidade LR)."""
    linhas, sens = [], []
    inf_hc1 = "normal, EP HC1 por municipio"
    for oc, meta in OUTCOMES.items():
        m = dados[oc]
        s, y = m["s_mil"].to_numpy(dtype=int), m["y"].to_numpy(dtype=float)
        pop = meta["populacao"]
        for corte in CORTES_MIL:
            c = corte / 1000
            r = rd_local(s, y, corte)
            linhas.append(_linha_spec("S0", oc, pop, c, r, unidade="municipio", inferencia=inf_hc1, natureza=natureza))
            r = rd_local(s, y, corte, grau=0)
            linhas.append(_linha_spec("A", oc, pop, c, r, unidade="municipio", inferencia=inf_hc1, natureza=natureza))
            for sid, covs in (("C1", COV_C1), ("C2", COV_C2)):
                r = rd_local(s, y, corte, Z=m[covs].to_numpy(dtype=float), nomes_z=covs)
                linhas.append(_linha_spec(sid, oc, pop, c, r, unidade="municipio", inferencia=inf_hc1,
                                          natureza=natureza))
        # B: cortes empilhados.
        partes = []
        for corte in CORTES_MIL:
            p = m[["co_ibge", "s_mil", "y"]].copy()
            p["corte_mil"] = corte
            partes.append(p)
        emp = pd.concat(partes, ignore_index=True)
        x_mil = emp["s_mil"] - emp["corte_mil"]
        com_peso = emp[(x_mil > -H_MIL) & (x_mil < H_MIL)]
        repetidos = int(com_peso["co_ibge"].duplicated().sum())
        r = rd_empilhado(emp["s_mil"], emp["y"], emp["corte_mil"], emp["corte_mil"].astype(str),
                         cluster=emp["co_ibge"] if repetidos else None, ids_municipio=emp["co_ibge"])
        linhas.append(_linha_spec("B", oc, pop, "0,300+0,400", r, unidade="municipio",
                                  inferencia=inf_hc1 if not repetidos else "normal, EP CR1 por municipio",
                                  natureza=natureza,
                                  extra={"municipios_em_duas_janelas": repetidos}))
        # D: local randomization (janela selecionada) e sensibilidade.
        for corte in CORTES_MIL:
            sel = selecao[(selecao["populacao"] == pop) & (selecao["corte"] == corte / 1000)]
            escolhida = sel[sel["selecionada"]]
            for _, jan in sel[sel["viavel"]].iterrows():
                w = int(round(jan["w"] * 1000))
                dentro, trat = janela_lr(s, corte, w)
                P = matriz_permutacao(int(dentro.sum()), int((dentro & trat).sum()), n_perm,
                                      (SEMENTE, id_populacao(pop), corte, w))
                inf = inferencia_lr(y[dentro], trat[dentro], P)
                sens.append({"natureza_dos_dados": natureza, "rotulo": ROTULO, "outcome": oc, "populacao": pop,
                             "corte": corte / 1000, "w": w / 1000, "n_abaixo": int(jan["n_abaixo"]),
                             "n_acima": int(jan["n_acima"]), "balanco_p_min": jan["p_min"],
                             "selecionada": bool(jan["selecionada"]), **inf})
            if len(escolhida):
                jan = escolhida.iloc[0]
                inf = next(x for x in sens if x["outcome"] == oc and x["corte"] == corte / 1000
                           and x["w"] == jan["w"])
                notas = []
                if not inf["ic_contiguo"]:
                    notas.append("regiao de aceitacao nao contigua: IC = envoltoria")
                if inf["ic_toca_borda_da_grade"]:
                    notas.append("IC toca a borda da grade [-1, 1] (efeito fora dela e impossivel para outcome em [0, 1])")
                res = {"n_abaixo": inf["n_abaixo"], "n_acima": inf["n_acima"],
                       "n_obs": inf["n_abaixo"] + inf["n_acima"], "n_clusters": None, **inf,
                       "nota": "; ".join(notas)}
                janela_txt = f"+-{jan['w']:.3f} (lado inferior inclui o corte)"
            else:
                res = _resultado_vazio()
                res["nota"] = "nenhuma janela candidata passou no balanco"
                for k in ("lim_sup_unilateral_95", "lim_inf_unilateral_95", "mde_80"):
                    res[k] = float("nan")
                for d in MARGENS:
                    res[f"p_unilateral_tau_ge_{_tag(d)}"] = float("nan")
                    res[f"p_tost_{_tag(d)}"] = float("nan")
                janela_txt = "nenhuma"
            linhas.append(_linha_spec(
                "D", oc, pop, corte / 1000, res, unidade="municipio", janela=janela_txt, natureza=natureza,
                inferencia=f"Fisher por {n_perm} permutacoes; IC por inversao (efeito constante); "
                           "ep = DP da distribuicao de permutacao sob o nulo"))
    # E0, E1, E2: Y1 por célula.
    m = dados["Y1"]
    cel = celulas.merge(m[["co_ibge", "s_mil"]], on="co_ibge", how="left", validate="many_to_one")
    if cel["s_mil"].isna().any():
        raise ValueError("celula sem escore do municipio")
    cursos = sorted(cel["cod_curso"].unique().tolist())
    fe_nomes = [f"curso_{k:02d}" for k in cursos[1:]]
    fe = np.column_stack([(cel["cod_curso"] == k).astype(float) for k in cursos[1:]]) if len(cursos) > 1 else None
    for corte in CORTES_MIL:
        c = corte / 1000
        r = rd_local(m["s_mil"].to_numpy(dtype=int), m["y"].to_numpy(dtype=float), corte,
                     peso=m["n_celulas"].to_numpy(dtype=float))
        linhas.append(_linha_spec("E0", "Y1", "P1", c, r, unidade="municipio (peso kernel x n_celulas)",
                                  inferencia=inf_hc1, natureza=natureza))
        r = rd_local(cel["s_mil"].to_numpy(dtype=int), cel["y"].to_numpy(dtype=float), corte,
                     cluster=cel["co_ibge"].to_numpy())
        linhas.append(_linha_spec("E1", "Y1", "P1", c, r, unidade="celula CNES-curso",
                                  inferencia="normal, EP CR1 por municipio", natureza=natureza))
        r = rd_local(cel["s_mil"].to_numpy(dtype=int), cel["y"].to_numpy(dtype=float), corte,
                     Z=fe, nomes_z=fe_nomes if fe is not None else (), cluster=cel["co_ibge"].to_numpy())
        linhas.append(_linha_spec("E2", "Y1", "P1", c, r, unidade="celula CNES-curso",
                                  inferencia="normal, EP CR1 por municipio", natureza=natureza))
    # F1, F2: presença empilhada por ciclo.
    pres = []
    for oc in ("D1", "D2"):
        p = dados[oc][["co_ibge", "s_mil", "y"]].copy()
        p["ciclo"] = OUTCOMES[oc]["ciclo"]
        pres.append(p)
    pres = pd.concat(pres, ignore_index=True)
    for corte in CORTES_MIL:
        p = pres.copy()
        p["corte_mil"] = corte
        r = rd_empilhado(p["s_mil"], p["y"], p["corte_mil"], "ciclo" + p["ciclo"].astype(str),
                         cluster=p["co_ibge"], ids_municipio=p["co_ibge"])
        linhas.append(_linha_spec("F1", "D1+D2", "P1+P2", corte / 1000, r, unidade="municipio x ciclo",
                                  inferencia="normal, EP CR1 por municipio", natureza=natureza))
    partes = []
    for corte in CORTES_MIL:
        p = pres.copy()
        p["corte_mil"] = corte
        partes.append(p)
    p = pd.concat(partes, ignore_index=True)
    grupo = "ciclo" + p["ciclo"].astype(str) + "_corte" + p["corte_mil"].astype(str)
    r = rd_empilhado(p["s_mil"], p["y"], p["corte_mil"], grupo, cluster=p["co_ibge"], ids_municipio=p["co_ibge"])
    linhas.append(_linha_spec("F2", "D1+D2", "P1+P2", "0,300+0,400", r, unidade="municipio x ciclo",
                              inferencia="normal, EP CR1 por municipio", natureza=natureza))
    return pd.DataFrame(linhas), pd.DataFrame(sens)


# ---------------------------------------------------------------------------
# Decomposição da largura do IC
# ---------------------------------------------------------------------------

FATORES_TEORICOS = {"DM_simples": 1.0, "LC_triangular": math.sqrt(4 / 3), "LL_uniforme": 2.0,
                    "LL_triangular_principal": math.sqrt(4.8)}


def decompor_ic(s_mil, y, n_cel, corte_mil: int, h_mil: int = H_MIL) -> tuple[list[dict], list[dict], dict]:
    s = np.asarray(s_mil, dtype=int)
    y = np.asarray(y, dtype=float)
    n_cel = np.asarray(n_cel, dtype=float)
    comps = {
        "DM_simples": rd_local(s, y, corte_mil, h_mil, grau=0, kernel="uniforme"),
        "LC_triangular": rd_local(s, y, corte_mil, h_mil, grau=0, kernel="triangular"),
        "LL_uniforme": rd_local(s, y, corte_mil, h_mil, grau=1, kernel="uniforme"),
        "LL_triangular_principal": rd_local(s, y, corte_mil, h_mil, grau=1, kernel="triangular"),
    }
    ep_dm = comps["DM_simples"]["ep"]
    x_mil = s - corte_mil
    w_tri = pesos_kernel(x_mil, h_mil, "triangular")
    usa = w_tri > 0
    ab, ac = usa & (x_mil <= 0), usa & (x_mil > 0)
    linhas = []
    for nome, r in comps.items():
        linhas.append({
            "corte": corte_mil / 1000, "componente": nome,
            "estimador": {"DM_simples": "diferenca de medias simples (grau 0, kernel uniforme)",
                          "LC_triangular": "local constante, kernel triangular (= A)",
                          "LL_uniforme": "local linear, kernel uniforme",
                          "LL_triangular_principal": "local linear, kernel triangular (= principal)"}[nome],
            "n_abaixo": r["n_abaixo"], "n_acima": r["n_acima"], "tau": r["tau"], "ep": r["ep"],
            "ic95_inf": r["ic95_inf"], "ic95_sup": r["ic95_sup"], "p_valor": r["p_valor"],
            "mde_80": FATOR_MDE * r["ep"], "razao_ep_vs_dm_simples": r["ep"] / ep_dm,
            "razao_teorica_desenho_uniforme": FATORES_TEORICOS[nome],
        })
    fit = comps["LL_triangular_principal"]["_fit"]
    a, b = fit["beta"]["const"], fit["beta"]["x"]
    tau, d = fit["beta"]["T"], fit["beta"]["T_x"]
    e = np.full(len(y), np.nan)
    e[comps["LL_triangular_principal"]["_usa"]] = fit["residuos"]
    lados = []
    medias_w = {}
    for lado, msk, inter, incl in (("abaixo", ab, a, b), ("acima", ac, a + tau, b + d)):
        ww = w_tri[msk]
        xm = x_mil[msk] / 1000.0
        yy = y[msk]
        xw = float(np.sum(ww * xm) / np.sum(ww))
        yw = float(np.sum(ww * yy) / np.sum(ww))
        medias_w[lado] = (xw, yw, inter, incl)
        lados.append({
            "corte": corte_mil / 1000, "lado": lado, "n": int(msk.sum()),
            "n_efetivo_kish_triangular": float(np.sum(ww) ** 2 / np.sum(ww ** 2)),
            "media_bruta_y": float(yy.mean()), "dp_y": float(yy.std(ddof=1)),
            "media_ponderada_x": xw, "media_ponderada_y": yw,
            "intercepto_no_corte": float(inter), "inclinacao_por_unidade_ivs": float(incl),
            "valor_ajustado_na_media_ponderada_x": float(inter + incl * xw),
            "dp_residual_ponderado": float(np.sqrt(np.sum(ww * e[msk] ** 2) / np.sum(ww))),
            "share_municipios_1_celula": float(np.mean(n_cel[msk] == 1)),
            "media_n_celulas": float(np.mean(n_cel[msk])),
        })
    x0, y0, _, b0 = medias_w["abaixo"]
    x1, y1, _, b1 = medias_w["acima"]
    sd_pool = float(np.sqrt(((ab.sum() - 1) * y[ab].var(ddof=1) + (ac.sum() - 1) * y[ac].var(ddof=1))
                            / (ab.sum() + ac.sum() - 2)))
    ep_llt = comps["LL_triangular_principal"]["ep"]
    resumo = {
        "corte": corte_mil / 1000,
        "dp_y_combinado": sd_pool,
        "ep_formula_dm": sd_pool * math.sqrt(1 / ab.sum() + 1 / ac.sum()),
        "ep_dm_simples": ep_dm,
        "ep_lc_triangular": comps["LC_triangular"]["ep"],
        "ep_ll_uniforme": comps["LL_uniforme"]["ep"],
        "ep_ll_triangular_principal": ep_llt,
        "fator_kernel_constante": comps["LC_triangular"]["ep"] / ep_dm,
        "fator_inclinacoes_triangular": ep_llt / comps["LC_triangular"]["ep"],
        "fator_inclinacoes_uniforme": comps["LL_uniforme"]["ep"] / ep_dm,
        "fator_kernel_linear": ep_llt / comps["LL_uniforme"]["ep"],
        "fator_total": ep_llt / ep_dm,
        "fatores_teoricos_desenho_uniforme": {"kernel_constante": math.sqrt(4 / 3), "inclinacoes_triangular": math.sqrt(3.6),
                                              "inclinacoes_uniforme": 2.0, "kernel_linear": math.sqrt(1.2),
                                              "total": math.sqrt(4.8)},
        "mde_80_principal": FATOR_MDE * ep_llt,
        "media_ponderada_acima_menos_abaixo": y1 - y0,
        "identidade": {
            "salto_tau": tau,
            "contribuicao_inclinacao_acima_(b+d)*x1": b1 * x1,
            "contribuicao_inclinacao_abaixo_-b*x0": -b0 * x0,
            "soma": tau + b1 * x1 - b0 * x0,
        },
        "media_bruta_acima_menos_abaixo": float(y[ac].mean() - y[ab].mean()),
    }
    return linhas, lados, resumo


def cenarios_poder(resumo: dict, n_obs: tuple[int, int], cenarios: dict[str, tuple[int, int]]) -> dict:
    """CENÁRIO ILUSTRATIVO (não é observação): escala o EP por raiz(1/n0 + 1/n1)."""
    n0, n1 = n_obs
    base = math.sqrt(1 / n0 + 1 / n1)
    ep = resumo["ep_ll_triangular_principal"]
    out = {"rotulo": "CENARIO_ILUSTRATIVO: nao e observacao; supoe mesmo desvio-padrao e mesmo desenho",
           "corte": resumo["corte"], "n_observado": {"abaixo": n0, "acima": n1}, "ep_observado": ep,
           "mde_80_observado": FATOR_MDE * ep}
    for nome, (m0, m1) in cenarios.items():
        ep_c = ep * math.sqrt(1 / m0 + 1 / m1) / base
        out[nome] = {"n_abaixo": m0, "n_acima": m1, "ep": ep_c, "mde_80": FATOR_MDE * ep_c}
    alvo = 0.10 / FATOR_MDE
    fator = (ep / alvo) ** 2
    out["n_para_mde_10pp"] = {"fator_sobre_n_observado": fator, "n_abaixo": n0 * fator, "n_acima": n1 * fator}
    return out


# ---------------------------------------------------------------------------
# Execução
# ---------------------------------------------------------------------------

def _contar_janela(s_mil: np.ndarray, corte: int) -> tuple[int, int]:
    x = np.asarray(s_mil, dtype=int) - corte
    return int(((x > -H_MIL) & (x <= 0)).sum()), int(((x > 0) & (x < H_MIL)).sum())


def executar(escore: pd.DataFrame, populacoes: dict[str, pd.DataFrame], covariaveis: pd.DataFrame,
             carregar_outcomes_fn: Callable[[pd.Series, pd.Series], dict], *, saida_dir: Path, natureza: str,
             meta: dict | None = None, referencia_e3: pd.DataFrame | None = None, n_perm: int = N_PERMUTACOES,
             root: Path = ROOT) -> dict:
    """Roda o E5. Os outcomes só são lidos depois de gravada a seleção da janela LR."""
    _guarda_saida(saida_dir, natureza, root)
    saida_dir = Path(saida_dir)
    saida_dir.mkdir(parents=True, exist_ok=True)
    status: dict = {
        "etapa": "E5_inferencia_alternativa",
        "rotulo": ROTULO,
        "aviso": ("EXPLORATORIO, pos-resultado: escrito depois de o E3 ser lido. O principal continua sendo o "
                  "do protocolo congelado (local linear, triangular, h = 0,050, HC1). Nenhuma especificacao "
                  "daqui substitui o principal; todas sao relatadas, qualquer que seja o resultado."),
        "natureza_dos_dados": natureza,
        "data_execucao": DATA_EXECUCAO,
        **(meta or {}),
        "contraste": CONTRASTE,
        "especificacoes": ESPECIFICACOES,
        "outcomes": OUTCOMES,
        "regras": {
            "cortes": [c / 1000 for c in CORTES_MIL], "h": H_MIL / 1000,
            "lado_do_corte": "o proprio corte pertence ao lado inferior; T = 1[s > c]",
            "kernel": "triangular, w = max(0, 1 - |x|/h); amostra -h < x < h",
            "covariaveis_C1": COV_C1, "covariaveis_C2": COV_C2,
            "local_randomization": {
                "janelas_candidatas": [w / 1000 for w in LR_JANELAS_MIL],
                "forma": "(c - w, c] U (c, c + w]",
                "viavel": f"pelo menos {LR_N_MIN_LADO} municipios de cada lado",
                "covariaveis_balanco": [c for c, _ in COV_LR],
                "estatisticas_balanco": "numerica: |diferenca de medias|; categorica: qui-quadrado de Pearson 2 x K",
                "limiar_p_min": LR_LIMIAR_BALANCO,
                "regra": "maior janela viavel com p minimo >= limiar nela e em toda janela viavel menor",
                "permutacoes": n_perm, "semente": SEMENTE,
                "semente_por_janela": "default_rng((semente, k da populacao, corte em milesimos, w em milesimos))",
                "p_valor": "(1 + #{T_perm >= T_obs}) / (R + 1)",
                "ic": "inversao do teste de Fisher sob efeito aditivo constante; grade -1 a +1, passo 0,001",
            },
            "margens_equivalencia": list(MARGENS),
            "mde": "2,8 x EP (80% de poder, 5% bicaudal)",
            "ic_normal": "tau +- 1,96 EP; limites unilaterais tau +- 1,645 EP",
        },
    }

    pops_s = {
        nome: pop.drop_duplicates("co_ibge")[["co_ibge"]].merge(escore[["co_ibge", "s_mil"]], on="co_ibge",
                                                                how="inner").sort_values("co_ibge")
        .reset_index(drop=True)
        for nome, pop in populacoes.items()
    }
    pe = {nome: E3.primeiro_estagio(pop, escore) for nome, pop in populacoes.items()}
    status["primeiro_estagio"] = pe
    cob = {nome: {"municipios": int(pop["co_ibge"].nunique()), "com_escore": int(len(pops_s[nome]))}
           for nome, pop in populacoes.items()}
    status["cobertura_do_escore"] = cob
    if not all(v["sharp"] for v in pe.values()) or any(v["municipios"] != v["com_escore"] for v in cob.values()):
        raise ValueError("escore incompleto ou regra nao sharp: o E5 nao roda (mesma condicao do E3)")

    pops_cov = {}
    for nome, p in pops_s.items():
        m = p.merge(covariaveis, on="co_ibge", how="left", validate="one_to_one")
        faltam = m[[c for c, _ in COV_LR] + COV_C2].isna().any(axis=1)
        if faltam.any():
            raise ValueError(f"{int(faltam.sum())} municipios de {nome} sem covariavel pre")
        pops_cov[nome] = m

    # (1) Seleção da janela LR só com covariáveis; gravada antes de qualquer outcome.
    selecao = pd.concat([selecionar_janela(pops_cov[nome], nome, n_perm) for nome in sorted(pops_cov)],
                        ignore_index=True)
    selecao.insert(0, "natureza_dos_dados", natureza)
    selecao.insert(1, "rotulo", ROTULO)
    _gravar_csv(saida_dir / NOME_LR_SELECAO, selecao)
    status["selecao_janela_lr"] = {
        "arquivo": NOME_LR_SELECAO,
        "sha256": sha256(saida_dir / NOME_LR_SELECAO),
        "gravada_antes_de_ler_outcomes": True,
        "selecionadas": [
            {"populacao": r["populacao"], "corte": r["corte"], "w": r["w"], "n_abaixo": r["n_abaixo"],
             "n_acima": r["n_acima"], "p_min": r["p_min"]}
            for _, r in selecao[selecao["selecionada"]].iterrows()
        ],
        "cortes_sem_janela": [
            {"populacao": p, "corte": c / 1000}
            for p in sorted(pops_cov) for c in CORTES_MIL
            if not selecao[(selecao["populacao"] == p) & (selecao["corte"] == c / 1000)]["selecionada"].any()
        ],
    }

    # (2) Outcomes.
    lido = carregar_outcomes_fn(pops_s["P1"]["co_ibge"], pops_s["P2"]["co_ibge"])
    dados = {}
    for oc, meta_oc in OUTCOMES.items():
        base = pops_cov[meta_oc["populacao"]]
        if oc == "Y1":
            serie = lido["Y1"][["co_ibge", "y", "n_celulas"]]
        else:
            serie = lido[oc].rename("y").reset_index()
        m = base.merge(serie, on="co_ibge", how="left", validate="one_to_one")
        if m["y"].isna().any():
            raise ValueError(f"{int(m['y'].isna().sum())} municipios sem outcome {oc}")
        dados[oc] = m
    celulas = lido["celulas"].copy()
    agg = celulas.groupby("co_ibge").agg(n=("y", "size"), soma=("y", "sum"))
    conf = dados["Y1"].set_index("co_ibge")[["y", "n_celulas"]].join(agg, how="outer")
    if conf.isna().any().any() or (conf["n"] != conf["n_celulas"]).any() or \
            (np.abs(conf["soma"] / conf["n"] - conf["y"]) > 1e-9).any():
        raise ValueError("celulas nao reproduzem Y1 por municipio")
    verificacoes = dict(lido.get("verificacoes", {}))
    verificacoes["celulas_reproduzem_y1"] = {"celulas": int(len(celulas)), "municipios": int(len(agg))}
    status["fontes_outcomes"] = lido.get("fontes", {})
    status["outcomes_lidos"] = list(OUTCOMES)

    # (3) Especificações.
    espec, sens = estimar_especificacoes(dados, celulas, selecao, natureza, n_perm)

    # (4) Reprodução do principal (S0) contra o E3.
    if referencia_e3 is not None:
        s0 = espec[espec["especificacao"] == "S0"]
        comp = s0.merge(referencia_e3.rename(columns={"outcome_e5": "outcome"}), on=["outcome", "corte"],
                        suffixes=("", "_e3"))
        if len(comp) != len(s0):
            raise ValueError("S0 sem linha correspondente no E3")
        dmax = float(max(np.abs(comp["tau"] - comp["tau_e3"]).max(), np.abs(comp["ep"] - comp["ep_e3"]).max()))
        if dmax > 1e-9 or (comp["n_abaixo"] != comp["n_abaixo_e3"]).any() or \
                (comp["n_acima"] != comp["n_acima_e3"]).any():
            raise ValueError(f"S0 nao reproduz o E3 (max |dif| = {dmax})")
        verificacoes["s0_reproduz_e3"] = {"linhas": int(len(comp)), "max_abs_dif_tau_ep": dmax}
    status["verificacoes"] = verificacoes

    # (5) Decomposição (Y1).
    dec, lados, resumos = [], [], []
    m = dados["Y1"]
    for corte in CORTES_MIL:
        l1, l2, rs = decompor_ic(m["s_mil"], m["y"], m["n_celulas"], corte)
        dec.extend(l1)
        lados.extend(l2)
        resumos.append(rs)
    dec = pd.DataFrame(dec)
    lados = pd.DataFrame(lados)
    for df in (dec, lados):
        df.insert(0, "natureza_dos_dados", natureza)
        df.insert(1, "rotulo", ROTULO)

    # Cenários ilustrativos (rotulados): mesma janela com P1 U P2 e com o Brasil.
    cen = []
    for rs in resumos:
        corte = int(round(rs["corte"] * 1000))
        n_obs = _contar_janela(dados["Y1"]["s_mil"], corte)
        p2 = _contar_janela(pops_s["P2"]["s_mil"], corte)
        br = _contar_janela(escore["s_mil"], corte)
        cen.append(cenarios_poder(rs, n_obs, {
            "ciclos_1_e_2_independentes": (n_obs[0] + p2[0], n_obs[1] + p2[1]),
            "todos_municipios_do_brasil_na_janela": br,
        }))

    _gravar_csv(saida_dir / NOME_ESPEC, espec)
    _gravar_csv(saida_dir / NOME_LR_SENS, sens)
    _gravar_csv(saida_dir / NOME_DECOMP, dec)
    _gravar_csv(saida_dir / NOME_LADOS, lados)

    y1 = espec[espec["outcome"] == "Y1"]
    status.update({
        "status": "CONCLUIDO",
        "saidas": {nome: sha256(saida_dir / nome) for nome in
                   (NOME_LR_SELECAO, NOME_ESPEC, NOME_LR_SENS, NOME_DECOMP, NOME_LADOS)},
        "decomposicao_ic_y1": resumos,
        "cenarios_ilustrativos_rotulados": cen,
        "resumo_y1": [
            {k: r[k] for k in ("especificacao", "corte", "janela", "n_abaixo", "n_acima", "n_obs", "tau", "ep",
                               "ic95_inf", "ic95_sup", "p_valor", "lim_sup_unilateral_95",
                               "p_unilateral_tau_ge_010", "p_unilateral_tau_ge_015", "p_unilateral_tau_ge_020",
                               "p_tost_010", "p_tost_015", "p_tost_020", "nota")}
            for r in y1.to_dict("records")
        ],
        "linguagem": ("exploratorio e pos-resultado; descritivo quando nao houver identificacao; intervalo "
                      "que contem zero e nao exclui efeitos relevantes e inconclusivo, nao ausencia de efeito"),
        "regra_de_relato": ("todas as especificacoes listadas no cabecalho do script sao relatadas; nenhuma "
                            "substitui o principal; nenhuma foi escolhida pelo tamanho do IC"),
    })
    _gravar_json(saida_dir / NOME_RESUMO, status)
    return status


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="E5: inferencia alternativa (exploratorio, pos-resultado)")
    ap.add_argument("--escore", type=Path, default=ESCORE_PADRAO,
                    help="CSV com co_ibge e ivs_admin (padrao: IVS 2010 oficial completo)")
    args = ap.parse_args(argv)
    escore_path = args.escore.resolve()
    escore = E3.ler_escore(escore_path)
    populacoes = E3.carregar_populacoes(ROOT)
    covariaveis, notas_cov = carregar_covariaveis_e5(ROOT)
    meta = {
        "script": {"arquivo": rotulo(Path(__file__)), "sha256": sha256(Path(__file__))},
        "funcoes_importadas": {rotulo(SCRIPT_E3): sha256(SCRIPT_E3), rotulo(SCRIPT_E4A): sha256(SCRIPT_E4A)},
        "protocolos": {rotulo(PROTOCOLO): sha256(PROTOCOLO), rotulo(ADENDO_E4): sha256(ADENDO_E4)},
        "entradas": {
            rotulo(escore_path): {
                "sha256": sha256(escore_path),
                "fonte": "IVS 2010 oficial do Ipea (a08), gravado por 04b_validar_ivs_oficial_escore_administrativo.py",
                "data_referencia": "Censo 2010 (Atlas IVS, base de 28/02/2024)",
                "cobertura": f"{len(escore)} municipios", "unidade": "municipio", "chaves": "co_ibge",
                "colunas_usadas": ["co_ibge", "ivs_admin"], "filtros": "nenhum"},
            **{q: {"sha256": sha256(ROOT / q), "fonte": "quadro de vagas publicado pelo MS (PMM-E)",
                   "data_referencia": "edital do ciclo correspondente", "cobertura": f"populacao {nome}",
                   "unidade": "linha do quadro", "chaves": "IBGE, FAIXA",
                   "colunas_usadas": ["IBGE", "FAIXA"], "filtros": "municipios distintos"}
               for nome, spec in E3.POPULACOES.items() for q in spec["quadros"]},
            **notas_cov,
            rotulo(E3_ESTIMATIVAS): {"sha256": sha256(E3_ESTIMATIVAS), "fonte": "E3 (07_estimar_E3_rdd_completa.py)",
                                     "papel": "referencia para conferir a reproducao do principal (S0)",
                                     "data_referencia": "2026-10-14", "cobertura": "P1 e P2",
                                     "unidade": "estimativa", "chaves": "populacao, outcome, corte, h",
                                     "filtros": "especificacao == principal"},
        },
    }
    status = executar(escore, populacoes, covariaveis, carregar_outcomes_reais(ROOT), saida_dir=SAIDA_DIR,
                      natureza="EMPIRICO", meta=meta, referencia_e3=carregar_referencia_e3(E3_ESTIMATIVAS))
    print(json.dumps(_nan_para_none({
        "status": status["status"],
        "janelas_lr": status["selecao_janela_lr"]["selecionadas"],
        "verificacoes": status["verificacoes"],
    }), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
