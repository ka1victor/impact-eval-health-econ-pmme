"""Adendo 52h: VL-1 do adendo 52e (escolha da 1ª opção com efeito fixo de UF de origem × UF da vaga) com um degrau
por corte de IVS (0,300 e 0,400) no lugar da bolsa linear.

Adendo congelado: `docs/06_execucao/52h_adendo_VL1_por_corte.md` (28/10/2026, antes de rodar; commit `2c8b964`), com
estatuto `ADENDO_52H_POS_RESULTADO`. Toda saída leva `natureza_dos_dados = EMPIRICO`.

Pedido do autor (28/10/2026)
----------------------------
O grupo perguntou se o efeito da bolsa vale nos dois cortes; o autor pediu "Faz aí a análise nova p termos ctz":
separar o efeito por corte, comparando só vagas da mesma UF. A bolsa é função exata do IVS 2010 oficial (bolsa = 10 +
5·1[IVS > 0,300] + 5·1[IVS > 0,400], R$ mil), e a bolsa linear do VL-1 força o mesmo salto nos dois cortes; o VK solta
essa restrição e nada mais.

O que o script faz
------------------
1. **Portão (VK-R).** Reestima, com `estimar_linha` do script 50 (sem alteração), o VL-1 dos ciclos 1–3 e do ciclo 2 e
   compara com `VL_estimativas.csv` e `VL_resumo.json` pela função `portao` do script 53 (adendo 52g), ≤ 1e−8. Se
   falhar, para (`FALHA_REPRODUCAO_<linha>`) e nada novo é estimado.
2. **VK-1, VK-2, VK-3.** O desenho do VL-1 (ou do VL-3, no VK-3), com a matriz do 50 (`matriz_vl`) e a coluna da bolsa
   trocada, na mesma posição, pelos degraus do E9 (`termos_bolsa(..., "degraus")` do script 16), conferidos célula a
   célula contra a regra do IVS oficial. Estimação pela `estimar_ef` do 50; score bootstrap pela `score_bootstrap` do
   50, que aceita um termo qualquer.
3. **VK-D.** Wald da igualdade dos degraus e razão das razões de chances; score bootstrap da igualdade por
   reparametrização (o modelo restrito é o VL-1).
4. **VK-5.** Quem identifica cada degrau: candidatos, pares de UF e conjuntos com vagas dos dois lados de cada corte
   dentro do mesmo par.
5. **Leitura do §4** por regra fixada no código (`regra_modelo`), commitada antes das estimativas.

Contraste: pacote do corte (bolsa e outras regras federais que mudam no mesmo corte) e incentivo marginal na escolha
da vaga marcada como 1ª opção, condicional a candidatar-se, dentro das vagas abertas. Não é efeito da participação no
PMM-E nem do Agora Tem Especialistas, nem a ida ao município. A origem é preferência revelada, não efeito causal.

Integridade
-----------
Só lê `data/` (pelas funções do 50, 42, 25 e 16) e `output/`; não escreve em `data/`. IVS 2010 oficial do a08; o
arquivo local de IVS da auditoria 16 não é lido. Nada simulado nem imputado. Sem identificador de candidato em
`output/`. `VL_*` e `VG_*` não são regravadas.

Uso
---
    python3 scripts/rdd_bolsa/54_VL1_por_corte.py
    python3 scripts/rdd_bolsa/54_VL1_por_corte.py --atualizar-doc   # só regrava o doc 57za
    python3 scripts/rdd_bolsa/54_VL1_por_corte.py --pre-registro    # doc 57za só com as decisões
"""

from __future__ import annotations

import argparse
import gc
import importlib.util
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DIR_RDD = ROOT / "scripts" / "rdd_bolsa"


def _importar(caminho: Path, nome: str):
    bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    sys.dont_write_bytecode = bytecode
    return mod


# O 53 importa o 50, que importa o 42, o 25c, o 25 e o 16: usam-se os mesmos objetos, sem reescrever nenhum deles.
VG = _importar(DIR_RDD / "53_VL1_por_ciclo.py", "VL1_por_ciclo_para_vk")
VL = VG.VL
P1, VC, E9, L = VL.P1, VL.VC, VL.E9, VL.L

# ---------------------------------------------------------------------------
# Caminhos
# ---------------------------------------------------------------------------

SCRIPT_50 = DIR_RDD / "50_escolha_localizacao_par.py"
SCRIPT_53 = DIR_RDD / "53_VL1_por_ciclo.py"
SCRIPT_16 = DIR_RDD / "16_estimar_E9_escolha.py"
ADENDO_MD = ROOT / "docs" / "06_execucao" / "52h_adendo_VL1_por_corte.md"
DOC_38 = ROOT / "docs" / "06_execucao" / "38_estado_e_pendencias_rdd_bolsa.md"
DOC = ROOT / "docs" / "06_execucao" / "57za_VL1_por_corte.md"
OUT = ROOT / "output" / "rdd_bolsa"
VL_CSV = VL.OUT_CSV
VL_RESUMO = VL.OUT_RESUMO
VG_CSV = VG.OUT_CSV
VG_RESUMO = VG.OUT_RESUMO
OUT_CSV = OUT / "VK_estimativas.csv"
OUT_RESUMO = OUT / "VK_resumo.json"

# ---------------------------------------------------------------------------
# Parâmetros (adendo 52h e 52e; nenhum é dado)
# ---------------------------------------------------------------------------

DATA_EXECUCAO = "2026-10-28"
NATUREZA = "EMPIRICO"
ESTATUTO = "ADENDO_52H_POS_RESULTADO"
COMMIT_ADENDO = "2c8b964"
TOL_REPRODUCAO = VL.TOL_REPRODUCAO
ALFA = 0.05
B, DIST = VL.B, VL.DIST
PREFIXO_EF = VL.PREFIXO_EF
AMOSTRA = VL.AMOSTRA
EMPILHADO = VL.EMPILHADO
D300, D400 = "degrau_0300", "degrau_0400"   # nomes do E9 (script 16, `termos_bolsa`)
DEGRAUS = (D300, D400)
DIF = "degrau_0300_menos_0400"
CORTE = {D300: "0,300", D400: "0,400"}
FAMILIA_HOLM = ("VK principais (adendo 52h, §3; doc 38 §3 D4, família só da hipótese): degraus 0,300 e 0,400 de "
                "VK-1 (ciclos 1–3) e VK-2 (ciclo 2)")

# VK-1 e VK-2 copiam o VL-1 do 50; VK-3 copia o VL-3 do VL-1 (ciclos 1–3). Só a bolsa muda (decisão 1).
_SEM = ("id_vl", "papel", "referencia")
ESPECS: dict[str, dict] = {
    "VK1": {**{k: v for k, v in VL.ESPECS["VL1_emp"].items() if k not in _SEM}, "id_vk": "VK-1",
            "papel": "principal", "base_vl": "VL1_emp"},
    "VK2": {**{k: v for k, v in VL.ESPECS["VL1_c2"].items() if k not in _SEM}, "id_vk": "VK-2",
            "papel": "principal", "base_vl": "VL1_c2"},
    "VK3": {**{k: v for k, v in VL.ESPECS["VL3_VL1_emp"].items() if k not in _SEM}, "id_vk": "VK-3",
            "papel": "sensibilidade", "base_vl": "VL3_VL1_emp"},
}
REPRODUZIDAS = VG.REPRODUZIDAS            # ("VL1_c2", "VL1_emp"): chaves do 50
NOVAS = ("VK1", "VK2", "VK3")
PRINCIPAIS = ("VK1", "VK2")
COM_SCORE = PRINCIPAIS                    # decisão 4: como no 50, sem score no VL-3
REF_SINAL = {"VK1": "VL1_emp", "VK2": "VL1_c2", "VK3": "VL1_emp"}  # decisão 8
ORDEM = ("VK1", "VL1_emp", "VK2", "VL1_c2", "VK3")
ROTULO = {"VK1": "VK-1: degraus, ciclos 1–3", "VK2": "VK-2: degraus, ciclo 2",
          "VK3": "VK-3: degraus, região de saúde de origem × UF da vaga, ciclos 1–3",
          "VL1_emp": "VL-1, ciclos 1–3 (bolsa linear, reproduzido)", "VL1_c2": "VL-1, ciclo 2 (bolsa linear, reproduzido)"}
ROTULO_CURTO = {"VK1": "VK-1 (ciclos 1–3)", "VK2": "VK-2 (ciclo 2)", "VK3": "VK-3 (região de saúde, ciclos 1–3)",
                "VL1_emp": "VL-1 (ciclos 1–3)", "VL1_c2": "VL-1 (ciclo 2)"}

COLUNAS = ["natureza_dos_dados", "estatuto", "id_vk", "papel", "chave_modelo", "modelo", "ciclo", "efeito_fixo",
           "distancia", "tipo_linha", "termo", "corte", "estimativa", "ep_cluster_conjunto", "ep_mle",
           "ep_cluster_candidato", "ic95_inf", "ic95_sup", "p", "p_t_g_menos_1", "p_mle", "p_score_rademacher",
           "p_score_webb", "metodo_score_rademacher", "entra_holm", "familia_holm", "p_holm",
           "p_holm_score_rademacher", "g_conjuntos", "g_candidatos", "n_candidatos", "n_linhas_candidato_celula",
           "n_conjuntos", "n_efeitos_fixos", "status", "nota"]


class FalhaValidacao(RuntimeError):
    pass


rel, sha256, gravar_json = P1.rel, P1.sha256, P1.gravar_json
_n, _p, _ic, _tab = P1._n, P1._p, P1._ic, P1._tab
_int = VL._int


# ---------------------------------------------------------------------------
# Decisões de implementação (registradas e commitadas antes de qualquer estimativa)
# ---------------------------------------------------------------------------

DECISOES = [
    {"data": "2026-10-28", "item": "O que é o VK",
     "situacao": "O §2 pede o VL-1 com `bolsa_mil` trocada por dois degraus e o resto idêntico.",
     "resolucao": "Desenho, amostra e efeito fixo são os do 50, sem alteração: `subconjunto` (VK-1 e VK-3: ciclos "
                  "1–3; VK-2: ciclo 2), `montar_desenho` do 25 e `desenho_ef` do 50 (indicadores de par menos uma base "
                  "por componente, retirada de pares sem escolha e de efeitos fixos separados, candidato com uma só "
                  "alternativa sai). Como o desenho não depende da coluna da bolsa, o de VK-1 e VK-2 é o mesmo do VL-1 "
                  "(conferido pelas contagens de identificação, iguais às de `VL_resumo.json`). A matriz é a "
                  "`matriz_vl` do 50 (M1 com distância linear por 100 km, sem `mesma_uf` e sem macrorregiões, com o "
                  "spline do IVS com mudança de inclinação em 0,300 e 0,400) com a coluna `bolsa_mil` substituída, na "
                  "mesma posição, por `degrau_0300` e `degrau_0400`. Estimação pela `estimar_ef` do 50 (mesma partida "
                  "do Newton). No logit condicional, a constante 10 some; o VL-1 é o VK com δ300 = δ400 = 5β. Nada é "
                  "reescrito: o script 54 importa o 53, e por ele o 50."},
    {"data": "2026-10-28", "item": "Codificação dos degraus",
     "situacao": "O pedido manda reusar uma codificação de degraus já existente; o E9 (script 16) tem uma, usada no "
                 "doc 42 e no 52f.",
     "resolucao": "Reusa-se `termos_bolsa(conj, \"degraus\")` do script 16: `degrau_0300` = faixa impressa 2 ou 1, "
                  "`degrau_0400` = faixa impressa 1. Antes de estimar, confere-se em todas as células do conjunto do P1 "
                  "corrigido: (a) `degrau_0300` = 1[IVS oficial > 0,300] e `degrau_0400` = 1[IVS oficial > 0,400], com "
                  "o IVS do a08 tanto bruto quanto em milésimos arredondados (`s_mil`, como no E9); (b) `bolsa_mil` = "
                  "10 + 5·`degrau_0300` + 5·`degrau_0400`; (c) em cada matriz, a coluna da bolsa que sai é exatamente "
                  "essa combinação. Qualquer discordância para a execução (`FalhaValidacao`). As contagens vão ao "
                  "resumo."},
    {"data": "2026-10-28", "item": "Portão VK-R",
     "situacao": "O §2 pede reproduzir o VL-1 dos ciclos 1–3 e do ciclo 2 com tolerância ≤ 1e−8 antes de qualquer "
                 "conta nova.",
     "resolucao": "Como no 52g, com as funções dele: `estimar_linha` do 50 (chaves `VL1_c2` e `VL1_emp`), linhas no "
                  "formato do 53 (`linhas_modelo`) e a função `portao` do 53, que compara coeficientes fora dos pares "
                  "com os três EP, a razão de chances (estimativa, EP, IC, p, p com t de G − 1, p de MV, score "
                  "bootstrap Rademacher e Webb), K5 e K10, G e candidatos, contra `VL_estimativas.csv`, e as contagens "
                  "de identificação e o score bootstrap contra `VL_resumo.json` (diferença absoluta ≤ 1e−8 se o valor "
                  "gravado tem módulo até 1, relativa se maior; NaN só casa com NaN). Falhou, a execução para em "
                  "`FALHA_REPRODUCAO_<linha>`, nada novo é estimado e só o resumo do portão é gravado."},
    {"data": "2026-10-28", "item": "Inferência, score bootstrap e Holm",
     "situacao": "O §3 pede inferência como no 52e, score bootstrap de Rademacher por degrau se o 50 permitir para um "
                 "termo arbitrário, e Holm nos quatro degraus principais.",
     "resolucao": "Sanduíche CR1 por conjunto de escolha (curso × ciclo), fator G/(G − 1), IC 95% e p pela normal; p "
                  "com t de G − 1 também. A `score_bootstrap` do 50 tem o parâmetro `termo`: o ajuste restrito tira só "
                  "a coluna daquele degrau (o outro degrau fica livre) e parte da estimativa irrestrita sem ela; "
                  "Rademacher por enumeração completa se G ≤ 24, senão 199.999 sorteios com a semente do 16; Webb "
                  "também. Calcula-se para cada degrau de VK-1 e VK-2. No VK-3 não (como o VL-3 no 50, que não tem "
                  "score; o ajuste restrito com o efeito fixo de região de saúde é o mais caro). Holm nos quatro "
                  "degraus de VK-1 e VK-2 com o p por cluster; Holm nos p do score bootstrap como coluna de robustez. "
                  "Razão de chances de um degrau = exp(δ) (um degrau = +R$ 5 mil), IC = exp do IC de δ."},
    {"data": "2026-10-28", "item": "Teste de igualdade (VK-D)",
     "situacao": "O §2 pede Wald com cluster por conjunto e a razão das razões de chances com IC.",
     "resolucao": "d = δ300 − δ400, EP CR1 de a'V a com a = (+1, −1); Wald z = d/EP (qui-quadrado 1 gl = z²), p pela "
                  "normal e com t de G − 1; razão das razões de chances exp(d), IC 95% exp(d ± 1,96·EP). Como "
                  "robustez descritiva, fora da regra de leitura e do Holm: score bootstrap da igualdade por "
                  "reparametrização exata (colunas `degrau_0300` e `degrau_0300 + degrau_0400`; o coeficiente da "
                  "primeira é d, e o modelo restrito d = 0 é o VL-1), com a mesma `score_bootstrap` do 50, em VK-1 e "
                  "VK-2."},
    {"data": "2026-10-28", "item": "VK-3",
     "situacao": "O §2 pede VK-1 com efeito fixo de região de saúde de origem × UF da vaga, como o VL-3.",
     "resolucao": "Desenho e matriz do `VL3_VL1_emp` do 50 (região de saúde de origem × UF da vaga, ciclos 1–3) com os "
                  "degraus no lugar da bolsa. Sensibilidade: fora do Holm, sem score bootstrap (decisão 4); a regra "
                  "de leitura é aplicada como descrição, sem entrar na leitura geral."},
    {"data": "2026-10-28", "item": "Quem identifica cada degrau (VK-5)",
     "situacao": "O §2 pede quantos conjuntos, pares de UF e candidatos têm vagas dos dois lados de cada corte dentro "
                 "da mesma UF.",
     "resolucao": "No desenho final de cada VK (depois da retirada de pares sem escolha), por candidato e par (origem, "
                  "UF da vaga): dos dois lados de 0,300 = vê no par vaga com IVS ≤ 0,300 e vaga com IVS > 0,300; dos "
                  "dois lados de 0,400 = vaga com IVS ≤ 0,400 e vaga com IVS > 0,400. Contam-se, por corte: "
                  "candidatos com isso em algum par, candidatos com a 1ª opção num par assim, pares (origem, UF da "
                  "vaga) com algum candidato assim, UFs de origem e conjuntos de escolha (G) com algum candidato "
                  "assim. Como a faixa acima de 0,400 também passa 0,300, conta-se à parte quem vê faixas vizinhas no "
                  "mesmo par (só aquele corte entre elas: faixas 3 e 2 para 0,300; 2 e 1 para 0,400), e quem vê as "
                  "três faixas. Junto, as contagens do `desenho_ef` do 50 (as da seção 3 do 57x)."},
    {"data": "2026-10-28", "item": "Leitura do §4 por regra",
     "situacao": "A tabela do §4 tem linhas que se sobrepõem (por exemplo, dois degraus com RC > 1, um com IC que "
                 "exclui 1) e não diz contra que sinal se lê \"sinal oposto\".",
     "resolucao": "Para cada degrau: `EXCLUI_1_MESMO_LADO`, `EXCLUI_1_LADO_OPOSTO` (lado contra o do VL-1 reproduzido "
                  "na mesma amostra: ciclos 1–3 para VK-1 e VK-3, ciclo 2 para VK-2) ou `CONTEM_1`. Para cada modelo, "
                  "nesta ordem: algum degrau `EXCLUI_1_LADO_OPOSTO` → `SINAL_OPOSTO` (4ª linha); senão, IC da razão "
                  "das razões de chances que exclui 1 → `DIFERE_ENTRE_CORTES` (3ª linha, com o corte de RC maior); "
                  "senão, exatamente um degrau `EXCLUI_1_MESMO_LADO` → `APARECE_NUM_CORTE` (2ª linha, com o corte); "
                  "senão, os dois degraus com RC > 1 → `VALE_NOS_DOIS_CORTES` (1ª linha), e, se nenhum dos dois IC "
                  "exclui 1, o doc diz que nenhum degrau, sozinho, se distingue de 1; senão → `FORA_DA_TABELA` "
                  "(relatado linha a linha); sem estimativa → `SEM_ESTIMATIVA`. A 2ª linha vem antes da 1ª porque "
                  "dizer que vale nos dois cortes com um IC contendo 1 seria dizer mais do que o dado mostra. Leitura "
                  "geral: a de VK-1 e a de VK-2, lado a lado; VK-3 é descritivo. Peso ao score: por degrau, "
                  "`score_concorda` = (p do score Rademacher < 0,05) igual a (IC exclui 1); quando não concorda, o "
                  "doc diz; a regra não muda."},
    {"data": "2026-10-28", "item": "Falha de convergência",
     "situacao": "Com dois degraus no lugar de uma coluna, a matriz pode perder posto num desenho com pouca variação.",
     "resolucao": "Como no 50: a linha fica `NAO_CONVERGIU` com a nota da `estimar_ef`, sem trocar partida, "
                  "especificação ou amostra; a leitura dela é `SEM_ESTIMATIVA`."},
    {"data": "2026-10-28", "item": "Saídas",
     "situacao": "O §5 lista script, `VK_estimativas.csv`, `VK_resumo.json`, doc 57za e testes; não lista figura nem km.",
     "resolucao": "Não há figura nem km equivalentes. O CSV tem, por modelo VK: os coeficientes fora dos indicadores de "
                  "par, a razão de chances de cada degrau e a razão das razões de chances (VK-D); e a razão de chances "
                  "por +R$ 5 mil do VL-1 reproduzido (`papel = reproducao_VK-R`). `VL_*` e `VG_*` não são regravadas "
                  "(hash conferido antes e depois)."},
    {"data": "2026-10-28", "item": "Números do doc 57za",
     "situacao": "O pedido exige números só em blocos gerados.",
     "resolucao": "Todo número de resultado do 57za vem de `VK_*` por `--atualizar-doc`, entre marcadores "
                  "`<!-- VK:... -->`; o teste confere o doc contra o gerado e que não há número de resultado fora dos "
                  "blocos. A resposta curta é escolhida por regra (`leitura`), sem texto escrito depois de ver os "
                  "números."},
]


# ---------------------------------------------------------------------------
# Degraus e matriz
# ---------------------------------------------------------------------------

def degraus_celula(conj: pd.DataFrame) -> pd.DataFrame:
    """Degraus do E9 (faixa impressa), por célula do conjunto."""
    return E9.termos_bolsa(conj, "degraus").reset_index(drop=True)


def conferir_degraus(conj: pd.DataFrame) -> dict:
    """Decisão 2: degraus = regra do IVS oficial (bruto e em milésimos) e bolsa = 10 + 5·D300 + 5·D400."""
    dg = degraus_celula(conj)
    d3, d4 = dg[D300].to_numpy(), dg[D400].to_numpy()
    ivs = conj["ivs"].to_numpy(dtype=float)
    s = conj["s_mil"].to_numpy(dtype=float)
    bolsa = conj["bolsa_mil"].to_numpy(dtype=float)
    out = {"celulas": int(len(conj)),
           "discordantes_degrau_0300_ivs_bruto": int((d3 != (ivs > 0.300)).sum()),
           "discordantes_degrau_0400_ivs_bruto": int((d4 != (ivs > 0.400)).sum()),
           "discordantes_degrau_0300_s_mil": int((d3 != (s > 300)).sum()),
           "discordantes_degrau_0400_s_mil": int((d4 != (s > 400)).sum()),
           "discordantes_bolsa_10_mais_5_degraus": int((np.abs(bolsa - (10 + 5 * d3 + 5 * d4)) > 0).sum()),
           "celulas_por_faixa": {"ate_0300": int(((d3 == 0) & (d4 == 0)).sum()),
                                 "0300_a_0400": int(((d3 == 1) & (d4 == 0)).sum()),
                                 "acima_0400": int(((d3 == 1) & (d4 == 1)).sum()),
                                 "degrau_0400_sem_0300": int(((d3 == 0) & (d4 == 1)).sum())}}
    ruins = {k: v for k, v in out.items() if k.startswith("discordantes") and v}
    if ruins or out["celulas_por_faixa"]["degrau_0400_sem_0300"]:
        raise FalhaValidacao(f"degraus discordam da regra do IVS oficial: {ruins or out['celulas_por_faixa']}")
    return out


def matriz_vk(D: dict, dv: dict, espec: dict, ef: dict) -> pd.DataFrame:
    """`matriz_vl` do 50 com `bolsa_mil` trocada, na mesma posição, por `degrau_0300` e `degrau_0400`."""
    X = VL.matriz_vl(D, dv, espec, ef)
    dg = degraus_celula(D["conj"]).to_numpy(dtype=float)[D["cel"]]
    if np.max(np.abs(X[B].to_numpy() - (10 + 5 * dg[:, 0] + 5 * dg[:, 1]))) > 0:
        raise FalhaValidacao("coluna da bolsa da matriz difere de 10 + 5·degraus")
    k = list(X.columns).index(B)
    X = X.drop(columns=[B])
    X.insert(k, D400, dg[:, 1])
    X.insert(k, D300, dg[:, 0])
    return X


# ---------------------------------------------------------------------------
# Estimação (funções do 50, sem alteração)
# ---------------------------------------------------------------------------

def score_igualdade(r: dict) -> dict:
    """Score bootstrap de H0: δ300 = δ400 por reparametrização exata (decisão 5): utilidade δ300·D300 + δ400·D400 =
    (δ300 − δ400)·D300 + δ400·(D300 + D400). O modelo restrito é o VL-1."""
    i, j = r["termos"].index(D300), r["termos"].index(D400)
    A = np.array(r["_A"], copy=True)
    A[:, j] = A[:, i] + A[:, j]
    th = np.array(r["theta"], dtype=float, copy=True)
    th[i], th[j] = th[i] - th[j], th[j]
    termos = list(r["termos"])
    termos[i], termos[j] = DIF, "soma_degraus"
    return VL.score_bootstrap({"_A": A, "_D": r["_D"], "theta": th, "termos": termos}, DIF)


def ajustar_vk(chave: str, X: pd.DataFrame, D: dict, ef: dict, log=print) -> dict:
    e = ESPECS[chave]
    r = VL.estimar_ef(X, D, ef, modelo=chave, ciclo=e["ciclo"], amostra=AMOSTRA)
    r["n_efeitos_fixos"] = int(sum(1 for t in r["termos"] if t.startswith(PREFIXO_EF)))
    if r["ok"] and chave in COM_SCORE and all(t in r["termos"] for t in DEGRAUS):
        r["score_bootstrap"] = {t: VL.score_bootstrap(r, t) for t in DEGRAUS}
        r["score_bootstrap"][DIF] = score_igualdade(r)
    for k in ("_A", "_D", "_scores", "_info"):
        r.pop(k, None)
    log(f"{chave}: ok={r['ok']} it={r.get('iteracoes')} termos={len(r['termos'])} candidatos={r['n_candidatos']} "
        f"G={r.get('G_conj')} grad_max={r.get('grad_max')}")
    return r


def contagens_degraus(D: dict, ef: dict) -> dict:
    """VK-5 (decisão 7): quem vê, no mesmo par (origem, UF da vaga), vagas dos dois lados de cada corte."""
    dg = degraus_celula(D["conj"]).to_numpy(dtype=int)[D["cel"]]
    faixa = dg[:, 0] + dg[:, 1]                     # 0: até 0,300; 1: 0,300–0,400; 2: acima de 0,400
    G = D["grupos"]
    clus = G["cluster_conjunto"].astype(str).to_numpy()
    df = pd.DataFrame({"grp": D["grp"], "par": ef["par_lin"], "f0": faixa == 0, "f1": faixa == 1, "f2": faixa == 2})
    tem = df.groupby(["grp", "par"], sort=True)[["f0", "f1", "f2"]].any()
    criterios = {
        "dois_lados_0300": tem["f0"] & (tem["f1"] | tem["f2"]),
        "dois_lados_0400": tem["f2"] & (tem["f0"] | tem["f1"]),
        "vizinhas_0300": tem["f0"] & tem["f1"],
        "vizinhas_0400": tem["f1"] & tem["f2"],
        "tres_faixas": tem["f0"] & tem["f1"] & tem["f2"],
    }
    par_esc = pd.MultiIndex.from_arrays([np.arange(len(D["starts"])), ef["par_lin"][D["esc"]]])
    out = {"candidatos_no_modelo": int(len(D["starts"])), "pares_no_modelo": int(len(np.unique(ef["par_lin"]))),
           "conjuntos_no_modelo": int(len(np.unique(clus))),
           "origens_no_modelo": int(pd.Series(ef["par_lin"]).str.split("|").str[0].nunique())}
    for nome, m in criterios.items():
        sel = m[m]
        grp = np.unique(sel.index.get_level_values(0))
        pares = np.unique(sel.index.get_level_values(1))
        out[nome] = {"candidatos": int(len(grp)), "candidatos_com_1a_opcao_no_par": int(par_esc.isin(sel.index).sum()),
                     "pares": int(len(pares)),
                     "origens": int(pd.Series(pares, dtype=object).str.split("|").str[0].nunique()),
                     "conjuntos": int(len(np.unique(clus[grp]))) if len(grp) else 0}
    return out


def estimar_vk(chave: str, dados: dict, conj_p1: pd.DataFrame, log=print) -> tuple[dict, dict]:
    """Os passos do `estimar_linha` do 50 (sem janela; efeito fixo do par) com a matriz de degraus."""
    e = ESPECS[chave]
    dv = {**dados, "conj_p1": conj_p1}
    conj, r1 = VL.subconjunto(conj_p1, dados["r1_p1"], e["ciclo"])
    D0 = P1.montar_desenho(conj, r1, None, dv)
    D, ef, diag_id = VL.desenho_ef(D0, dados, e["ef"])
    del D0
    diag_deg = contagens_degraus(D, ef)
    X = matriz_vk(D, dv, e, ef)
    r = ajustar_vk(chave, X, D, ef, log)
    del X, D
    gc.collect()
    return r, {"identificacao": diag_id, "degraus": diag_deg}


# ---------------------------------------------------------------------------
# Linhas de saída
# ---------------------------------------------------------------------------

def info(chave: str) -> dict:
    if chave in ESPECS:
        e = ESPECS[chave]
        return {"id_vk": e["id_vk"], "papel": e["papel"], "ciclo": e["ciclo"], "ef": e["ef"], "dist": e["dist"]}
    e = VL.ESPECS[chave]
    return {"id_vk": "VK-R", "papel": "reproducao_VK-R", "ciclo": e["ciclo"], "ef": e["ef"], "dist": e["dist"]}


def _base(chave: str, r: dict, **kw) -> dict:
    i = info(chave)
    b = {c: np.nan for c in COLUNAS}
    b.update({"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "id_vk": i["id_vk"], "papel": i["papel"],
              "chave_modelo": chave, "modelo": ROTULO[chave], "ciclo": i["ciclo"], "efeito_fixo": i["ef"],
              "distancia": i["dist"], "corte": "", "entra_holm": False, "familia_holm": "",
              "metodo_score_rademacher": "", "g_conjuntos": r.get("G_conj"), "g_candidatos": r.get("G_cand"),
              "n_candidatos": r.get("n_candidatos"), "n_linhas_candidato_celula": r.get("n_linhas"),
              "n_conjuntos": r.get("n_conjuntos"), "n_efeitos_fixos": r.get("n_efeitos_fixos", 0),
              "status": r.get("status", "EXECUTADO"), "nota": ""})
    b.update(kw)
    return b


def _exp(c: dict) -> dict:
    """Razão de chances de uma combinação linear c (do `combinacao` do 25): exp, IC = exp do IC, EP pelo delta."""
    o = math.exp(c["coef"])
    return {"estimativa": o, "ep_cluster_conjunto": o * c["ep_cluster_conjunto"], "ep_mle": o * c["ep_mle"],
            "ep_cluster_candidato": o * c["ep_cluster_candidato"], "ic95_inf": math.exp(c["ic95_inf"]),
            "ic95_sup": math.exp(c["ic95_sup"]), "p": c["p"], "p_t_g_menos_1": c["p_t_g_menos_1"], "p_mle": c["p_mle"]}


def _score(r: dict, termo: str) -> dict:
    sb = r.get("score_bootstrap", {}).get(termo, {})
    return {"p_score_rademacher": sb.get("p_rademacher", np.nan), "p_score_webb": sb.get("p_webb", np.nan),
            "metodo_score_rademacher": sb.get("metodo_rademacher", "")}


def linhas_vk(chave: str, r: dict) -> list[dict]:
    if not r["ok"] or not all(t in r["termos"] for t in DEGRAUS):
        return [_base(chave, r, tipo_linha="razao_chances_degrau", termo=t, corte=CORTE[t], status="NAO_CONVERGIU",
                      nota=r.get("nota", "") or "degrau omitido") for t in DEGRAUS]
    out = []
    nota_ef = f"{r['n_efeitos_fixos']} indicadores de par (decisão 1 do 57x), não relatados um a um"
    for t in r["termos"]:
        if t.startswith(PREFIXO_EF):
            continue
        c = P1.combinacao(r, P1.vetor(r, t))
        out.append(_base(chave, r, tipo_linha="coeficiente", termo=t, corte=CORTE.get(t, ""), estimativa=c["coef"],
                         **{k: c[k] for k in ("ep_cluster_conjunto", "ep_mle", "ep_cluster_candidato", "ic95_inf",
                                              "ic95_sup", "p", "p_t_g_menos_1", "p_mle")},
                         nota=P1._juntar("coeficiente da utilidade" + (" (um degrau = +R$ 5 mil/mês)" if t in DEGRAUS
                                                                        else ""), r.get("nota", ""), nota_ef)))
    for t in DEGRAUS:
        c = P1.combinacao(r, P1.vetor(r, t))
        out.append(_base(chave, r, tipo_linha="razao_chances_degrau", termo=t, corte=CORTE[t], **_exp(c),
                         **_score(r, t), nota=f"exp(δ) do degrau em {CORTE[t]} (+R$ 5 mil); IC = exp do IC de δ; "
                                              "p de H0: δ = 0 (cluster por conjunto)"))
    a = P1.vetor(r, D300) - P1.vetor(r, D400)
    c = P1.combinacao(r, a)
    out.append(_base(chave, r, tipo_linha="razao_razoes_chances", termo=DIF, corte="0,300 ÷ 0,400", **_exp(c),
                     **_score(r, DIF), nota="VK-D: exp(δ300 − δ400); Wald de H0: δ300 = δ400 (qui-quadrado 1 gl = z²), "
                                            "cluster por conjunto; score bootstrap por reparametrização (decisão 5)"))
    return out


def linha_vl(chave: str, r: dict) -> dict:
    sb = r.get("score_bootstrap", {})
    return _base(chave, r, tipo_linha="razao_chances_por_5mil", termo=B, **VL.linha_rc(chave, r),
                 p_score_rademacher=sb.get("p_rademacher", np.nan), p_score_webb=sb.get("p_webb", np.nan),
                 metodo_score_rademacher=sb.get("metodo_rademacher", ""),
                 nota="VL-1 reproduzido (portão VK-R): exp(5·β), IC = exp do IC do log")


def montar(res: dict) -> pd.DataFrame:
    linhas = []
    for chave in ORDEM:
        linhas += linhas_vk(chave, res[chave]) if chave in ESPECS else [linha_vl(chave, res[chave])]
    est = pd.DataFrame(linhas)[COLUNAS]
    mh = (est["tipo_linha"] == "razao_chances_degrau") & est["chave_modelo"].isin(PRINCIPAIS)
    est.loc[mh, "entra_holm"] = True
    est.loc[mh, "familia_holm"] = FAMILIA_HOLM
    p = est.loc[mh, "p"].to_numpy(dtype=float)
    est.loc[mh, "p_holm"] = L.holm(np.where(np.isnan(p), 1.0, p))
    ps = est.loc[mh, "p_score_rademacher"].to_numpy(dtype=float)
    est.loc[mh, "p_holm_score_rademacher"] = L.holm(np.where(np.isnan(ps), 1.0, ps))
    est["entra_holm"] = est["entra_holm"].astype(bool)
    return est


# ---------------------------------------------------------------------------
# Leitura (regra fixada antes de rodar; decisão 8)
# ---------------------------------------------------------------------------

def _sel(est: pd.DataFrame, chave: str, tipo: str, termo: str | None = None) -> pd.Series:
    s = est[(est["chave_modelo"] == chave) & (est["tipo_linha"] == tipo)]
    if termo is not None:
        s = s[s["termo"] == termo]
    if len(s) != 1:
        raise FalhaValidacao(f"esperava 1 linha {chave} {tipo} {termo}, achei {len(s)}")
    return s.iloc[0]


def _contem_1(l: pd.Series) -> bool:
    return bool(l["ic95_inf"] <= 1.0 <= l["ic95_sup"])


def regra_degrau(l: pd.Series, ref: pd.Series) -> str:
    if pd.isna(l["estimativa"]) or pd.isna(l["ic95_inf"]):
        return "SEM_ESTIMATIVA"
    if _contem_1(l):
        return "CONTEM_1"
    if np.sign(math.log(l["estimativa"])) == np.sign(math.log(ref["estimativa"])):
        return "EXCLUI_1_MESMO_LADO"
    return "EXCLUI_1_LADO_OPOSTO"


def regra_modelo(d3: pd.Series, d4: pd.Series, razao: pd.Series, ref: pd.Series) -> dict:
    """§4 do adendo, na ordem da decisão 8."""
    r3, r4 = regra_degrau(d3, ref), regra_degrau(d4, ref)
    out = {"degrau_0300": r3, "degrau_0400": r4, "corte": None, "nenhum_degrau_exclui_1": None,
           "razao_contem_1": None if pd.isna(razao["ic95_inf"]) else _contem_1(razao)}
    if "SEM_ESTIMATIVA" in (r3, r4) or pd.isna(razao["ic95_inf"]):
        out["regra"] = "SEM_ESTIMATIVA"
    elif "EXCLUI_1_LADO_OPOSTO" in (r3, r4):
        out["regra"] = "SINAL_OPOSTO"
        out["corte"] = [CORTE[t] for t, x in ((D300, r3), (D400, r4)) if x == "EXCLUI_1_LADO_OPOSTO"]
    elif not out["razao_contem_1"]:
        out["regra"] = "DIFERE_ENTRE_CORTES"
        out["corte"] = CORTE[D300] if d3["estimativa"] > d4["estimativa"] else CORTE[D400]
    elif sorted((r3, r4)) == ["CONTEM_1", "EXCLUI_1_MESMO_LADO"]:
        out["regra"] = "APARECE_NUM_CORTE"
        out["corte"] = CORTE[D300] if r3 == "EXCLUI_1_MESMO_LADO" else CORTE[D400]
    elif d3["estimativa"] > 1.0 and d4["estimativa"] > 1.0:
        out["regra"] = "VALE_NOS_DOIS_CORTES"
        out["nenhum_degrau_exclui_1"] = bool(r3 == "CONTEM_1" and r4 == "CONTEM_1")
    else:
        out["regra"] = "FORA_DA_TABELA"
    return out


def score_concorda(l: pd.Series) -> bool | None:
    if pd.isna(l["p_score_rademacher"]) or pd.isna(l["ic95_inf"]):
        return None
    return bool((l["p_score_rademacher"] < ALFA) == (not _contem_1(l)))


def leitura(est: pd.DataFrame) -> dict:
    out = {}
    for chave in NOVAS:
        ref = _sel(est, REF_SINAL[chave], "razao_chances_por_5mil")
        d3 = _sel(est, chave, "razao_chances_degrau", D300)
        d4 = _sel(est, chave, "razao_chances_degrau", D400)
        rz = _sel(est, chave, "razao_razoes_chances", DIF)
        o = regra_modelo(d3, d4, rz, ref)
        o["referencia_do_sinal"] = REF_SINAL[chave]
        o["score_concorda"] = {D300: score_concorda(d3), D400: score_concorda(d4), DIF: score_concorda(rz)}
        o["papel"] = ESPECS[chave]["papel"]
        out[chave] = o
    return {"linhas": out, "geral": {k: out[k]["regra"] for k in PRINCIPAIS}}


# ---------------------------------------------------------------------------
# Documento 57za
# ---------------------------------------------------------------------------

def bloco(nome: str, corpo: str) -> list[str]:
    return [f"<!-- VK:{nome}:inicio -->", corpo, f"<!-- VK:{nome}:fim -->"]


def _data_br(iso: str) -> str:
    a, m, d = iso.split("-")
    return f"{d}/{m}/{a}"


def _rc(r: pd.Series, casas: int = 2) -> str:
    if pd.isna(r["estimativa"]):
        return f"— ({r['status']})"
    return f"{_n(r['estimativa'], casas)} {_ic(r['ic95_inf'], r['ic95_sup'], casas)}"


def texto_decisoes() -> str:
    t = ["Decisões de implementação onde o adendo não fixava o detalhe. Foram registradas e commitadas antes de "
         "qualquer estimativa deste adendo (o histórico do Git mostra o commit deste bloco antes do commit dos "
         "números). As 13 decisões do 57x e as do 57z continuam valendo; em qualquer ambiguidade nova, vale a leitura "
         "mais próxima do script 50.", ""]
    for i, d in enumerate(DECISOES, 1):
        t.append(f"{i}. **{d['item']}** ({_data_br(d['data'])}). {d['situacao']} *Resolução:* {d['resolucao']}")
    return "\n".join(t)


def texto_portao(resumo: dict) -> str:
    p = resumo["portao"]
    linhas = []
    for e in p["linhas"]:
        difs = [v for k, v in e.items() if k.startswith("dif_max_")]
        linhas.append([ROTULO[e["linha"]], VL._sci(max(difs)) if difs else "—",
                       "sim" if e["identificacao_igual"] else "**não**",
                       "passou" if e["passou"] else "**falhou**"])
    t = [f"**Portão de reprodução (VK-R): {p['status']}.** Antes de qualquer conta nova, as funções do script 50 e o "
         "portão do script 53, importados sem alteração, reproduzem o VL-1 já gravado. A coluna mostra a maior "
         "diferença entre todas as quantidades comparadas da linha (absoluta quando o valor gravado tem módulo até 1, "
         "relativa acima disso); a lista completa está em `portao` de `VK_resumo.json`.", "",
         _tab(["Linha", "Dif. máx.", "Contagens de identificação iguais", "Portão"], linhas)]
    if p["status"] != "PASSOU":
        t += ["", f"A execução parou em `{p['status']}`: nada novo foi estimado (adendo 52h)."]
    else:
        c = resumo["conferencias"]["degraus"]
        t += ["", f"**Degraus conferidos (decisão 2).** Nas {c['celulas']} células do conjunto, os degraus do E9 batem "
                  "com a regra do IVS oficial (bruto e em milésimos) e com bolsa = 10 + 5·degraus: "
                  f"{c['discordantes_degrau_0300_ivs_bruto'] + c['discordantes_degrau_0400_ivs_bruto']} "
                  "discordâncias. O desenho de VK-1 e VK-2 é o do VL-1: "
                  + ("contagens de identificação iguais às de `VL_resumo.json`."
                     if resumo["conferencias"]["desenho_igual_ao_VL1"] else "**contagens diferentes**.")]
    return "\n".join(t)


def texto_identificacao(resumo: dict) -> str:
    idt = resumo["identificacao"]
    linhas = []
    for chave in NOVAS:
        d = idt[chave]["degraus"]
        for crit, rot in (("dois_lados_0300", "dois lados de 0,300"), ("vizinhas_0300", "faixas 3 e 2 (só 0,300)"),
                          ("dois_lados_0400", "dois lados de 0,400"), ("vizinhas_0400", "faixas 2 e 1 (só 0,400)"),
                          ("tres_faixas", "as três faixas")):
            x = d[crit]
            linhas.append([ROTULO_CURTO[chave], rot, f"{x['conjuntos']} de {d['conjuntos_no_modelo']}",
                           f"{x['pares']} de {d['pares_no_modelo']}", f"{x['origens']} de {d['origens_no_modelo']}",
                           f"{x['candidatos']} de {d['candidatos_no_modelo']}", f"{x['candidatos_com_1a_opcao_no_par']}"])
    frases = []
    for chave in PRINCIPAIS:
        d = idt[chave]["degraus"]
        frases.append(f"no {ROTULO_CURTO[chave]}, {d['dois_lados_0300']['candidatos']} candidatos veem vagas dos dois "
                      f"lados de 0,300 e {d['dois_lados_0400']['candidatos']} dos dois lados de 0,400 (de "
                      f"{d['candidatos_no_modelo']}), em {d['dois_lados_0300']['conjuntos']} e "
                      f"{d['dois_lados_0400']['conjuntos']} conjuntos de escolha")
    return "\n".join([
        "**Quem identifica cada degrau (VK-5).** O peso de um degrau vem só de candidatos que veem, dentro do mesmo par "
        "(UF de origem, UF da vaga), vagas dos dois lados daquele corte: " + "; ".join(frases) + ".", "",
        "Colunas: conjuntos de escolha (clusters), pares (origem, UF da vaga), UFs (ou regiões de saúde, no VK-3) de "
        "origem e candidatos com o critério em algum par, sobre o total do modelo; e candidatos cuja 1ª opção está "
        "num par com o critério. \"Faixas vizinhas\" separa quem compara vagas com só aquele corte entre elas; quem "
        "compara a faixa até 0,300 com a acima de 0,400 passa os dois cortes de uma vez.", "",
        _tab(["Modelo", "Critério", "Conjuntos", "Pares", "Origens", "Candidatos", "1ª opção no par"], linhas)])


def tabela_principais(est: pd.DataFrame) -> str:
    linhas = []
    for chave in ORDEM:
        if chave in ESPECS:
            termos = [(t, "razao_chances_degrau") for t in DEGRAUS]
        else:
            termos = [(B, "razao_chances_por_5mil")]
        for t, tipo in termos:
            r = _sel(est, chave, tipo, t)
            linhas.append([ROTULO_CURTO[chave], f"degrau {CORTE[t]}" if t in DEGRAUS else "bolsa linear (+R$ 5 mil)",
                           _int(r["n_candidatos"]), _int(r["g_conjuntos"]), _rc(r), _p(r["p"]),
                           _p(r["p_t_g_menos_1"]), _p(r["p_score_rademacher"]),
                           _p(r["p_holm"]) if r["entra_holm"] else "—",
                           _p(r["p_holm_score_rademacher"]) if r["entra_holm"] else "—"])
    return "\n".join([
        "Razão de chances da 1ª opção por degrau de bolsa (+R$ 5 mil no corte), comparando só vagas da mesma UF vistas "
        "por médicos da mesma UF de origem (no VK-3, da mesma região de saúde de origem), com o IVS em spline contínua. "
        "IC 95% e p (H0: δ = 0) com cluster por conjunto de escolha (curso × ciclo); p com t de G − 1; p do score "
        "bootstrap (Kline–Santos, Rademacher), que pesa mais quando G é pequeno; Holm nos quatro degraus de VK-1 e VK-2 "
        "(decisão 4). As linhas do VL-1 são as do 57x, reproduzidas pelo portão, para comparar.", "",
        _tab(["Modelo", "Termo", "Candidatos", "Conjuntos (G)", "RC [IC 95%]", "p", "p (t, G − 1)",
              "p score (Rademacher)", "p Holm", "p Holm (score)"], linhas)])


def tabela_igualdade(est: pd.DataFrame) -> str:
    linhas = []
    for chave in NOVAS:
        r = _sel(est, chave, "razao_razoes_chances", DIF)
        # EP do log da razão = EP delta da razão ÷ razão; Wald = z².
        z = math.log(r["estimativa"]) / (r["ep_cluster_conjunto"] / r["estimativa"]) if pd.notna(r["estimativa"]) \
            else float("nan")
        linhas.append([ROTULO_CURTO[chave], _rc(r), _n(z * z, 2), _p(r["p"]), _p(r["p_t_g_menos_1"]),
                       _p(r["p_score_rademacher"]), _int(r["g_conjuntos"])])
    return "\n".join([
        "VK-D: razão das razões de chances, RC(0,300) ÷ RC(0,400) = exp(δ300 − δ400). Igual a 1 quer dizer o mesmo "
        "efeito nos dois cortes (o VL-1). Wald com cluster por conjunto (qui-quadrado com 1 gl); p com t de G − 1; p "
        "do score bootstrap da igualdade (decisão 5, descritivo).", "",
        _tab(["Modelo", "Razão [IC 95%]", "Wald (χ², 1 gl)", "p", "p (t, G − 1)", "p score (Rademacher)",
              "Conjuntos (G)"], linhas)])


def tabela_controles(est: pd.DataFrame) -> str:
    termos = list(est[(est["chave_modelo"] == "VK1") & (est["tipo_linha"] == "coeficiente")]["termo"])
    linhas = []
    for t in termos:
        cel = []
        for chave in NOVAS:
            s = est[(est["chave_modelo"] == chave) & (est["tipo_linha"] == "coeficiente") & (est["termo"] == t)]
            cel.append("—" if s.empty else f"{_n(s.iloc[0]['estimativa'], 3)} "
                                           f"{_ic(s.iloc[0]['ic95_inf'], s.iloc[0]['ic95_sup'], 3)}")
        linhas.append([f"`{t}`"] + cel)
    return "\n".join([
        "Os coeficientes que não são indicadores de par (log-chance; IC 95% com cluster por conjunto). \"—\" é termo "
        "omitido. Todas as linhas estão em `VK_estimativas.csv`.", "",
        _tab(["Termo"] + [ROTULO_CURTO[k] for k in NOVAS], linhas)])


ROTULO_REGRA = {
    "VALE_NOS_DOIS_CORTES": "1ª linha do §4: o efeito por +R$ 5 mil vale nos dois cortes; o efeito linear é adequado",
    "APARECE_NUM_CORTE": "2ª linha do §4: o efeito aparece num corte; não dá para dizer que difere entre cortes",
    "DIFERE_ENTRE_CORTES": "3ª linha do §4: o efeito difere entre cortes",
    "SINAL_OPOSTO": "4ª linha do §4: sinal oposto com IC que exclui 1; o efeito linear esconde heterogeneidade",
    "FORA_DA_TABELA": "fora das linhas do §4 (relatado linha a linha)",
    "SEM_ESTIMATIVA": "sem estimativa",
}


def frase_modelo(est: pd.DataFrame, lei: dict, chave: str) -> str:
    li = lei["linhas"][chave]
    d3 = _sel(est, chave, "razao_chances_degrau", D300)
    d4 = _sel(est, chave, "razao_chances_degrau", D400)
    rz = _sel(est, chave, "razao_razoes_chances", DIF)
    t = (f"- **{ROTULO_CURTO[chave]}:** degrau 0,300, razão de chances {_rc(d3)} (p {_p(d3['p'])}"
         + (f", Holm {_p(d3['p_holm'])}" if d3["entra_holm"] else "")
         + f"); degrau 0,400, {_rc(d4)} (p {_p(d4['p'])}"
         + (f", Holm {_p(d4['p_holm'])}" if d4["entra_holm"] else "")
         + f"); razão entre eles {_rc(rz)} (p {_p(rz['p'])}); {_int(d3['g_conjuntos'])} conjuntos de escolha. "
         f"Leitura: `{li['regra']}` ({ROTULO_REGRA[li['regra']]}")
    if li["regra"] in ("APARECE_NUM_CORTE", "DIFERE_ENTRE_CORTES"):
        t += f"; corte {'de RC maior' if li['regra'] == 'DIFERE_ENTRE_CORTES' else 'em que aparece'}: {li['corte']}"
    if li["regra"] == "SINAL_OPOSTO":
        t += f"; corte: {', '.join(li['corte'])}"
    t += ")."
    if li.get("nenhum_degrau_exclui_1"):
        t += " Nenhum degrau, sozinho, tem IC que exclui 1: a leitura vem de os dois estarem acima de 1 e de a razão " \
             "entre eles conter 1."
    nao = [CORTE.get(k, "da razão") for k, v in li["score_concorda"].items() if v is False]
    if nao:
        t += (" O score bootstrap não confirma a classificação do IC em: " + ", ".join(nao) +
              " (com poucos conjuntos, ele merece mais peso).")
    return t


def texto_resposta(est: pd.DataFrame, resumo: dict) -> str:
    lei = resumo["leitura"]
    g1, g2 = lei["geral"]["VK1"], lei["geral"]["VK2"]
    cab = {
        "VALE_NOS_DOIS_CORTES": "o efeito por +R$ 5 mil aparece nos dois cortes, sem diferença detectável entre eles",
        "APARECE_NUM_CORTE": "o efeito aparece num corte só, sem que dê para dizer que difere do outro",
        "DIFERE_ENTRE_CORTES": "o efeito difere entre os cortes",
        "SINAL_OPOSTO": "um degrau pesa contra a escolha, com IC que exclui 1",
        "FORA_DA_TABELA": "o resultado fica fora das linhas pré-registradas",
        "SEM_ESTIMATIVA": "falta estimativa",
    }
    t = [f"**Comparando só vagas da mesma UF, nos ciclos 1–3 (VK-1) {cab[g1]}; no ciclo 2 (VK-2), {cab[g2]}.**"]
    for chave in NOVAS:
        t.append(frase_modelo(est, lei, chave) + (" *(sensibilidade, fora do Holm)*" if chave == "VK3" else ""))
    for chave in REPRODUZIDAS[::-1]:
        r = _sel(est, chave, "razao_chances_por_5mil")
        t.append(f"- Para comparar, {ROTULO_CURTO[chave]} com a bolsa linear: razão de chances por +R$ 5 mil {_rc(r)}.")
    t.append("**Em linguagem simples.** A pergunta do grupo era se o peso da bolsa na escolha vale nos dois cortes de "
             "IVS ou só num deles. Aqui cada corte tem o seu peso, e se compara vaga com vaga dentro da mesma UF. "
             "Cada degrau é o pacote do corte (bolsa e outras regras federais que mudam no mesmo ponto), não a "
             "participação no PMM-E; mede a vaga marcada como 1ª opção na inscrição, não a ida ao município; vale "
             "para quem se candidatou, dentro das vagas abertas; e é pós-resultado: o VL-1 já era conhecido antes "
             "deste adendo.")
    return "\n\n".join(t)


def texto_leitura(resumo: dict) -> str:
    lei = resumo["leitura"]
    linhas = []
    for chave in NOVAS:
        li = lei["linhas"][chave]
        sc = li["score_concorda"]
        linhas.append([ROTULO_CURTO[chave], f"`{li['degrau_0300']}`", f"`{li['degrau_0400']}`",
                       "—" if li["razao_contem_1"] is None else ("sim" if li["razao_contem_1"] else "não"),
                       f"`{li['regra']}`", " / ".join("—" if sc[k] is None else ("sim" if sc[k] else "**não**")
                                                     for k in (D300, D400, DIF))])
    return "\n".join([
        "Regra fixada no código antes de rodar (decisão 8). Sinal de referência: o do VL-1 reproduzido na mesma "
        f"amostra. Leitura geral: VK-1 `{lei['geral']['VK1']}`; VK-2 `{lei['geral']['VK2']}`; VK-3 é descritivo.", "",
        _tab(["Modelo", "Degrau 0,300", "Degrau 0,400", "IC da razão contém 1", "Regra",
              "Score concorda (0,300 / 0,400 / razão)"], linhas)])


PENDENTE = "*Pendente: preenchido pelo script depois do portão de reprodução.*"


def gerar_doc(est: pd.DataFrame | None, resumo: dict | None) -> str:
    """Doc 57za. Sem resumo (pré-registro), só cabeçalho, decisões e limites."""
    tem_portao = resumo is not None and "portao" in resumo
    ok = tem_portao and resumo["portao"]["status"] == "PASSOU" and est is not None
    Lh = [
        "# 57za. Escolha da 1ª opção com o par de UFs fixado, degrau por degrau (adendo 52h)",
        "",
        "> **Gerado por** `scripts/rdd_bolsa/54_VL1_por_corte.py` a partir de `output/rdd_bolsa/VK_*`; não editar à mão "
        "(o teste `tests/test_VL1_por_corte.py` confere que este arquivo é igual ao gerado; `--atualizar-doc` o "
        "regrava das saídas).<br>",
        f"> **Adendo:** [`52h_adendo_VL1_por_corte.md`](52h_adendo_VL1_por_corte.md), congelado em 28/10/2026 antes de "
        f"rodar (commit `{COMMIT_ADENDO}`); SHA-256 em `adendo` de `VK_resumo.json`, conferido pelo teste. Especificação "
        "de origem: VL-1 do adendo [52e](52e_adendo_escolha_localizacao_par.md), doc "
        "[57x](57x_resultados_escolha_localizacao_par.md); por ciclo no [57z](57z_VL1_por_ciclo.md).<br>",
        "> **Estatuto:** `ADENDO_52H_POS_RESULTADO`. O VL-1 já tinha sido visto; isto separa o efeito por corte, não é "
        "teste confirmatório novo. Toda linha de `VK_estimativas.csv` e o resumo têm `natureza_dos_dados = EMPIRICO`.<br>",
        "> **Pedido do autor (28/10/2026):** \"Faz aí a análise nova p termos ctz\" — separar o efeito da bolsa por "
        "corte (0,300 e 0,400), comparando vagas da mesma UF.<br>",
        "> **Saídas:** `output/rdd_bolsa/VK_estimativas.csv` e `VK_resumo.json`. `VL_*` e `VG_*` não são regravadas; os "
        "docs 57x e 57z não são editados.<br>",
        "> **Auditoria:** pendente. A resposta curta é escolhida por regra fixada no código (`leitura`) no commit das "
        "decisões, antes das estimativas.",
        "",
        "## 1. Resposta curta",
        "",
    ]
    if ok:
        Lh += [*bloco("resposta", texto_resposta(est, resumo)), ""]
    elif tem_portao:
        Lh += [*bloco("resposta", f"Nada novo estimado: `{resumo['portao']['status']}`."), ""]
    else:
        Lh += [PENDENTE, ""]
    Lh += ["## 2. Portão de reprodução (VK-R)", ""]
    Lh += [*bloco("portao", texto_portao(resumo)), ""] if tem_portao else [PENDENTE, ""]
    if ok:
        Lh += [
            "## 3. Quem identifica cada degrau (VK-5)",
            "",
            *bloco("identificacao", texto_identificacao(resumo)),
            "",
            "## 4. Resultados",
            "",
            "### 4.1 Razão de chances por degrau (VK-1, VK-2, VK-3)",
            "",
            *bloco("principais", tabela_principais(est)),
            "",
            "### 4.2 Teste de igualdade dos degraus (VK-D)",
            "",
            *bloco("igualdade", tabela_igualdade(est)),
            "",
            "### 4.3 Os outros pesos do modelo",
            "",
            *bloco("controles", tabela_controles(est)),
            "",
            "## 5. Leitura do §4 por regra",
            "",
            *bloco("leitura", texto_leitura(resumo)),
            "",
        ]
    else:
        Lh += ["## 3. Resultados", "", PENDENTE, ""]
    Lh += [
        "## 6. Decisões de implementação",
        "",
        *bloco("decisoes", texto_decisoes()),
        "",
        "## 7. Limites",
        "",
        "- **Pós-resultado.** O VL-1 empilhado, o do ciclo 2 e o por ciclo já eram conhecidos. O adendo foi congelado "
        "antes de rodar, mas separar por corte depois de ver o efeito linear não é teste confirmatório novo.",
        "- **Pacote do corte.** Cada degrau é identificado pelo salto no seu corte de IVS, com o IVS em spline contínua; "
        "nos mesmos cortes mudam outras regras federais (auditoria 18). Não é efeito da participação no PMM-E nem do "
        "Agora Tem Especialistas.",
        "- **Identificação estreita.** O peso de cada degrau vem só de candidatos que veem, na mesma UF, vagas dos dois "
        "lados daquele corte (seção 3); quem compara a faixa até 0,300 com a acima de 0,400 passa os dois cortes de "
        "uma vez, e o modelo separa os degraus pela faixa do meio e pelo spline.",
        "- **Poucos conjuntos.** O cluster é o conjunto de escolha (curso × ciclo); no ciclo 2 são poucos. O IC com "
        "cluster pode ser otimista; por isso o score bootstrap vai ao lado.",
        "- **Escolha condicional.** Tudo vale para quem se candidatou, dentro das vagas abertas do seu curso e ciclo, e "
        "mede a vaga marcada como 1ª opção, não a ida ao município; IIA do logit condicional.",
        "- **Origem não é causal.** A origem é o município do vínculo médico no CNES (G1), não a residência; o peso da "
        "origem é preferência revelada, não efeito causal.",
    ]
    return "\n".join(Lh) + "\n"


# ---------------------------------------------------------------------------
# Execução
# ---------------------------------------------------------------------------

def entradas(dados: dict) -> list[dict]:
    be = P1.bloco_entrada
    return [
        be(ADENDO_MD, "adendo 52h (especificação, somente lido)", "repositório", "2026-10-28", "§1–§6", "documento",
           "-", "-"),
        be(DOC_38, "doc 38 (regra de família D4, somente lido)", "repositório", "-", "§3", "documento", "-", "-"),
        be(VL_CSV, "alvo do portão VK-R (VL-1 dos ciclos 2 e 1–3)", "script 50", "2026-10-27", "VL1_c2, VL1_emp",
           "especificação × termo", "chave_modelo, tipo_linha, termo", "-"),
        be(VL_RESUMO, "alvo do portão VK-R (identificação e score bootstrap)", "script 50", "2026-10-27",
           "VL1_c2, VL1_emp", "linha", "identificacao, score_bootstrap", "-"),
        be(SCRIPT_53, "portão do adendo 52g (importado sem alteração)", "repositório", "-", "-", "código", "-", "-"),
        be(SCRIPT_50, "funções do adendo 52e (importadas sem alteração)", "repositório", "-", "-", "código", "-", "-"),
        be(SCRIPT_16, "degraus do E9 (`termos_bolsa`, importado sem alteração)", "repositório", "-", "-", "código",
           "-", "-"),
        *VL.entradas(dados),
    ]


def remover_saidas_calculadas() -> None:
    if OUT_CSV.exists():
        OUT_CSV.unlink()


def _hash_protegidos() -> dict:
    return {rel(p): sha256(p) for p in (VL_CSV, VL_RESUMO, VG_CSV, VG_RESUMO)}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--atualizar-doc", action="store_true", help="só regrava o doc 57za a partir das saídas")
    ap.add_argument("--pre-registro", action="store_true",
                    help="grava o doc 57za só com as decisões (antes de qualquer estimativa)")
    args = ap.parse_args(argv)
    if args.pre_registro:
        if OUT_RESUMO.exists():
            raise FalhaValidacao("VK_resumo.json já existe: o pré-registro só vale antes das estimativas")
        DOC.write_text(gerar_doc(None, None), encoding="utf-8")
        return 0
    if args.atualizar_doc:
        atualizar_doc()
        return 0
    t0 = time.time()

    def log(m: str) -> None:
        print(f"[{time.time() - t0:7.0f}s] {m}", flush=True)

    hash_prot = _hash_protegidos()
    dados = P1.carregar()
    log("insumos do P1 carregados")
    q1302, q1903 = VC.ler_quadros_c2()
    conf_antiga = VC.conferir_versao_antiga(dados["conj"], q1903)
    conf_a36 = VC.conferir_contra_a36(q1302)
    conj_p1_c, corr = VC.corrigir(dados["conj_p1"], q1302)
    conf_deg = conferir_degraus(conj_p1_c)
    log("quadro de 13/02 conferido, conjunto do P1 corrigido e degraus conferidos")
    resumo = {
        "etapa": "VK_VL1_por_corte",
        "natureza_dos_dados": NATUREZA,
        "estatuto": ESTATUTO,
        "data_execucao": DATA_EXECUCAO,
        "script": rel(Path(__file__)),
        "adendo": {"arquivo": rel(ADENDO_MD), "sha256": sha256(ADENDO_MD), "commit_de_congelamento": COMMIT_ADENDO},
        "protocolos": {rel(p): sha256(p) for p in (VG.ADENDO_MD, VL.ADENDO_MD, VL.PROTOCOLO_52, VL.PROTOCOLO_52B,
                                                    VL.ADENDO_52C)},
        "conferencias": {"versao_antiga_do_conjunto": conf_antiga, "quadro_1302_contra_a36": conf_a36,
                         "correcao_ciclo2": {k: corr[k] for k in ("celulas_ciclo2_no_conjunto",
                                                                  "celulas_sem_linha_no_quadro_1302",
                                                                  "celulas_com_vagas_imediatas_diferentes",
                                                                  "imputadas")},
                         "degraus": conf_deg},
        "decisoes": DECISOES,
        "especificacoes": {**{k: VL.ESPECS[k] for k in REPRODUZIDAS}, **ESPECS},
        "entradas": entradas(dados),
        "integridade": ("nada simulado nem imputado; data/ só lido; IVS do a08 (o arquivo local de IVS da auditoria 16 "
                        "não é lido); só agregados em output/ (sem nome, CPF, CRM nem pseudônimo de candidato); saídas "
                        "VL_* e VG_* não regravadas"),
        "linguagem": ("escolha da vaga marcada como 1ª opção, condicional a se candidatar, dentro das vagas abertas (não "
                      "a ida ao município); cada degrau mede o pacote do corte; a origem é preferência revelada, não "
                      "efeito causal; não é efeito da participação no PMM-E; pós-resultado"),
        "tempo_execucao_nao_registrado": "fora do resumo para que duas execuções deem o mesmo hash",
    }

    # Portão (VK-R): nada novo antes dele.
    res: dict[str, dict] = {}
    idt: dict[str, dict] = {}
    for chave in REPRODUZIDAS:
        res[chave], idt[chave] = VL.estimar_linha(chave, dados, conj_p1_c, log)
    vl = pd.read_csv(VL_CSV, dtype={"ciclo": str})
    vl_resumo = json.loads(VL_RESUMO.read_text(encoding="utf-8"))
    novas = pd.DataFrame([x for k in REPRODUZIDAS for x in VG.linhas_modelo(k, res[k])])
    port = VG.portao(novas, vl, res, idt, vl_resumo)
    port["regra"] = port["regra"] + " (função `portao` do script 53, adendo 52g)"
    resumo["portao"] = port
    log(f"portão: {port['status']}")
    if port["status"] != "PASSOU":
        remover_saidas_calculadas()
        resumo["saidas"] = {}
        gravar_json(OUT_RESUMO, resumo)
        atualizar_doc()
        print(f"{port['status']}: nada novo estimado (adendo 52h)", file=sys.stderr)
        return 3

    for chave in NOVAS:
        res[chave], idt[chave] = estimar_vk(chave, dados, conj_p1_c, log)
    resumo["conferencias"]["desenho_igual_ao_VL1"] = bool(
        idt["VK1"]["identificacao"] == vl_resumo["identificacao"]["VL1_emp"]["identificacao"]
        and idt["VK2"]["identificacao"] == vl_resumo["identificacao"]["VL1_c2"]["identificacao"])
    resumo["conferencias"]["desenho_VK3_igual_ao_VL3"] = bool(
        idt["VK3"]["identificacao"] == vl_resumo["identificacao"]["VL3_VL1_emp"]["identificacao"])
    est = montar(res)
    sem = est[est["estimativa"].isna() & (est["status"] == "EXECUTADO")]
    if len(sem):
        raise FalhaValidacao(f"{len(sem)} linhas executadas sem estimativa")
    est.to_csv(OUT_CSV, index=False, float_format="%.10g")
    est = ler_est()
    if _hash_protegidos() != hash_prot:
        raise FalhaValidacao("VL_* ou VG_* mudou durante a execução")
    resumo["identificacao"] = idt
    resumo["score_bootstrap"] = {k: res[k].get("score_bootstrap", {}) for k in ORDEM}
    resumo["convergencia"] = {k: {"ok": bool(r["ok"]), "status": r.get("status"), "iteracoes": r.get("iteracoes"),
                                  "omitidas": r.get("omitidas", []), "n_efeitos_fixos": r.get("n_efeitos_fixos", 0),
                                  "grad_max": r.get("grad_max"), "decremento_final": r.get("decremento_final"),
                                  "partida": r.get("partida"),
                                  "termos_sem_efeito_fixo": [t for t in r["termos"] if not t.startswith(PREFIXO_EF)],
                                  "nota": r.get("nota", "")} for k, r in res.items()}
    resumo["covariancias"] = covariancias_vk(res)
    resumo["leitura"] = leitura(est)
    resumo["inferencia"] = {"principal": "sanduíche com cluster por conjunto de escolha (curso × ciclo), fator G/(G−1)",
                            "holm": FAMILIA_HOLM,
                            "score_bootstrap": ("Kline–Santos, `score_bootstrap` do 50 com termo = cada degrau (VK-1 e "
                                                "VK-2) e igualdade por reparametrização; Rademacher e Webb"),
                            "z_bilateral_95": VL.Z95}
    resumo["protegidos_nao_regravados"] = hash_prot
    resumo["saidas"] = {rel(OUT_CSV): sha256(OUT_CSV)}
    gravar_json(OUT_RESUMO, resumo)
    atualizar_doc()
    log(f"gravado: {rel(OUT_CSV)}, {rel(OUT_RESUMO)}, {rel(DOC)}")
    return 0


def covariancias_vk(res: dict) -> dict:
    """θ e bloco da covariância dos dois degraus, para recálculo nos testes."""
    out = {}
    for chave in NOVAS:
        r = res[chave]
        if not r.get("ok") or not all(t in r["termos"] for t in DEGRAUS):
            continue
        k = [r["termos"].index(t) for t in DEGRAUS]
        out[chave] = {"termos": list(DEGRAUS), "theta": np.asarray(r["theta"])[k].tolist(),
                      "V_cluster_conjunto": np.asarray(r["V_conj"])[np.ix_(k, k)].tolist(),
                      "V_mle": np.asarray(r["V_mle"])[np.ix_(k, k)].tolist(), "g_conjuntos": r["G_conj"]}
    return out


def ler_est() -> pd.DataFrame:
    return pd.read_csv(OUT_CSV, dtype={"ciclo": str}, keep_default_na=True)


def ler_resumo() -> dict:
    return json.loads(OUT_RESUMO.read_text(encoding="utf-8"))


def atualizar_doc() -> None:
    resumo = ler_resumo()
    ok = resumo.get("portao", {}).get("status") == "PASSOU" and OUT_CSV.exists()
    DOC.write_text(gerar_doc(ler_est() if ok else None, resumo), encoding="utf-8")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except FalhaValidacao as erro:
        print(f"FALHA DE VALIDACAO: {erro}", file=sys.stderr)
        sys.exit(2)
