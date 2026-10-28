"""Adendo 52g: VL-1 do adendo 52e (escolha da 1ª opção com efeito fixo de UF de origem × UF da vaga) nos ciclos 1 e 3.

Adendo congelado: `docs/06_execucao/52g_adendo_VL1_por_ciclo.md` (28/10/2026, antes de rodar; commit `e9740a5`), com
estatuto `ADENDO_52G_POS_RESULTADO`. Toda saída leva `natureza_dos_dados = EMPIRICO`.

Decisão do autor (28/10/2026)
-----------------------------
"A hipótese é simplesmente sobre o efeito bolsa → 1ª opção", com "só comparação entre municípios da mesma UF". A
especificação que compara só vagas da mesma UF é o VL-1 do 52e (doc 57x), já estimado nos ciclos 1–3 empilhados e no
ciclo 2. Este script roda o mesmo VL-1 nos ciclos 1 e 3 separados.

O que o script faz
------------------
1. **Portão (VG-R).** Reestima, com as funções do script 50 importadas sem alteração (`estimar_linha`), o VL-1 dos
   ciclos 1–3 e do ciclo 2 e compara com `VL_estimativas.csv` e `VL_resumo.json` (≤ 1e−8; relativa quando o valor
   gravado passa de 1 em módulo; contagens de identificação iguais). Se falhar, para (`FALHA_REPRODUCAO_<linha>`) e
   nada novo é estimado.
2. **VG-1 e VG-3.** O VL-1 no ciclo 1 e no ciclo 3: mesma amostra do P1 (tipo de vaga do ciclo 2 pelo quadro de
   13/02/2026, que não toca os ciclos 1 e 3), mesmo desenho do efeito fixo do par (`desenho_ef`, com a retirada de
   pares sem escolha e de efeitos fixos separados), mesma matriz (`matriz_vl`), mesmo ponto de partida
   (`estimar_ef`) e o mesmo score bootstrap (`score_bootstrap`).
3. **VG-4 e VG-5.** km equivalentes de +R$ 5 mil e +R$ 10 mil (função `linha_km` do 25c, como no VL-4) e contagens
   de pares de UF e de candidatos que identificam (as do `desenho_ef`).
4. **Leitura do §2** por regra fixada no código (`regra_linha`, `leitura`), commitada antes das estimativas.

Contraste: pacote do corte e incentivo marginal da bolsa na escolha condicional a candidatar-se, dentro das vagas
abertas. Não é efeito da participação no PMM-E nem do Agora Tem Especialistas. A origem é preferência revelada, não
efeito causal.

Integridade
-----------
Só lê `data/` (pelas funções do 50, 42 e 25) e `output/`; não escreve em `data/`. IVS 2010 oficial do a08; o arquivo
local de IVS da auditoria 16 não é lido. Nada simulado nem imputado. Sem identificador de candidato em `output/`. As
saídas `VL_*` e as demais não são regravadas.

Uso
---
    python3 scripts/rdd_bolsa/53_VL1_por_ciclo.py
    python3 scripts/rdd_bolsa/53_VL1_por_ciclo.py --atualizar-doc   # só regrava o doc 57z
    python3 scripts/rdd_bolsa/53_VL1_por_ciclo.py --pre-registro    # doc 57z só com as decisões
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


# O 50 importa o 42, que importa o 25c, o 25 e o 16: usam-se os mesmos objetos, sem reescrever nenhum deles.
VL = _importar(DIR_RDD / "50_escolha_localizacao_par.py", "escolha_localizacao_par_para_vg")
P1, P1H, VC, E9, L = VL.P1, VL.P1H, VL.VC, VL.E9, VL.L

# ---------------------------------------------------------------------------
# Caminhos
# ---------------------------------------------------------------------------

SCRIPT_50 = DIR_RDD / "50_escolha_localizacao_par.py"
ADENDO_MD = ROOT / "docs" / "06_execucao" / "52g_adendo_VL1_por_ciclo.md"
ADENDO_52E = VL.ADENDO_MD
DOC_57X = VL.DOC
DOC = ROOT / "docs" / "06_execucao" / "57z_VL1_por_ciclo.md"
OUT = ROOT / "output" / "rdd_bolsa"
VL_CSV = VL.OUT_CSV
VL_RESUMO = VL.OUT_RESUMO
OUT_CSV = OUT / "VG_estimativas.csv"
OUT_RESUMO = OUT / "VG_resumo.json"

# ---------------------------------------------------------------------------
# Parâmetros (adendo 52g e 52e; nenhum é dado)
# ---------------------------------------------------------------------------

DATA_EXECUCAO = "2026-10-28"
NATUREZA = "EMPIRICO"
ESTATUTO = "ADENDO_52G_POS_RESULTADO"
COMMIT_ADENDO = "e9740a5"
TOL_REPRODUCAO = VL.TOL_REPRODUCAO
ALFA = 0.05
B, DIST = VL.B, VL.DIST
PREFIXO_EF = VL.PREFIXO_EF
AMOSTRA = VL.AMOSTRA
FAMILIA_HOLM = "VG por ciclo (adendo 52g, decisão 4): VG-1 (ciclo 1) e VG-3 (ciclo 3); coluna descritiva"

# VG-1 e VG-3 copiam a especificação do VL-1 do 50 e só trocam o ciclo (decisão 1).
_BASE_VL1 = {k: v for k, v in VL.ESPECS["VL1_c2"].items() if k not in ("id_vl", "papel", "ciclo", "referencia")}
ESPECS: dict[str, dict] = {
    "VG1": {**_BASE_VL1, "id_vg": "VG-1", "papel": "robustez_por_ciclo", "ciclo": "1"},
    "VG3": {**_BASE_VL1, "id_vg": "VG-3", "papel": "robustez_por_ciclo", "ciclo": "3"},
}
REPRODUZIDAS = ("VL1_c2", "VL1_emp")       # VG-R: chaves do 50, estimadas pela `estimar_linha` dele
NOVAS = ("VG1", "VG3")
ORDEM = ("VG1", "VL1_c2", "VG3", "VL1_emp")  # ordem das tabelas
ROTULO = {"VG1": "VG-1: VL-1 no ciclo 1", "VG3": "VG-3: VL-1 no ciclo 3", "VL1_c2": "VL-1 no ciclo 2 (reproduzido)",
          "VL1_emp": "VL-1 nos ciclos 1–3 (reproduzido)"}
ROTULO_CURTO = {"VG1": "ciclo 1", "VG3": "ciclo 3", "VL1_c2": "ciclo 2", "VL1_emp": "ciclos 1–3"}
REFERENCIA_SINAL = "VL1_c2"                 # decisão 5: "mesmo sinal" = o do VL-1 do ciclo 2

COLUNAS = ["natureza_dos_dados", "estatuto", "id_vg", "papel", "chave_modelo", "modelo", "ciclo", "efeito_fixo",
           "distancia", "tipo_linha", "termo", "estimativa", "ep_cluster_conjunto", "ep_mle", "ep_cluster_candidato",
           "ic95_inf", "ic95_sup", "p", "p_t_g_menos_1", "p_mle", "p_score_rademacher", "p_score_webb",
           "metodo_score_rademacher", "ic95_fieller_inf", "ic95_fieller_sup", "entra_holm", "familia_holm", "p_holm",
           "p_holm_score_rademacher", "g_conjuntos", "g_candidatos", "n_candidatos", "n_linhas_candidato_celula",
           "n_conjuntos", "n_efeitos_fixos", "status", "nota"]


class FalhaValidacao(RuntimeError):
    pass


rel, sha256, gravar_json = P1.rel, P1.sha256, P1.gravar_json
_n, _p, _ic, _tab = P1._n, P1._p, P1._ic, P1._tab
_int, _dif_rel = VL._int, VL._dif_rel


# ---------------------------------------------------------------------------
# Decisões de implementação (registradas e commitadas antes de qualquer estimativa)
# ---------------------------------------------------------------------------

DECISOES = [
    {"data": "2026-10-28", "item": "O que é o VL-1 num ciclo",
     "situacao": "O §1 manda rodar \"exatamente o VL-1 do 52e\" em cada ciclo separado.",
     "resolucao": "VG-1 e VG-3 são a especificação `VL1_c2` do script 50 com o ciclo trocado para 1 e 3: a amostra é a "
                  "do P1 restrita ao ciclo (função `subconjunto` do 50, como o M5 do script 25); o efeito fixo de UF de "
                  "origem × UF da vaga é montado só com os candidatos e as vagas daquele ciclo (`desenho_ef` do 50, "
                  "com as decisões 1 a 3 do 57x: indicadores de par menos uma base por componente, retirada de pares "
                  "sem escolha e de efeitos fixos separados até não mudar, candidato com uma só alternativa sai); a "
                  "matriz é a do 50 (`matriz_vl`: M1 com distância linear por 100 km, sem `mesma_uf` e sem "
                  "macrorregiões); a estimação é a `estimar_ef` do 50 (mesmo ponto de partida do Newton, nota de "
                  "execução 1 do 57x). Nada é reescrito: o script 53 importa o 50."},
    {"data": "2026-10-28", "item": "Tipo de vaga nos ciclos 1 e 3",
     "situacao": "O 52e usa o conjunto do P1 com o tipo de vaga do ciclo 2 pelo quadro de 13/02/2026 (função "
                 "`corrigir` do 42).",
     "resolucao": "Usa-se o mesmo conjunto corrigido. A correção só muda células do ciclo 2; nos ciclos 1 e 3 o "
                  "conjunto é o do P1. O resumo grava a contagem de células por ciclo para conferência."},
    {"data": "2026-10-28", "item": "Portão VG-R",
     "situacao": "O §1 pede reproduzir o VL-1 do ciclo 2 e dos ciclos 1–3 com diferença ≤ 1e−8 antes do resto.",
     "resolucao": "Antes de qualquer conta nova, `estimar_linha` do 50 (sem alteração, com as chaves `VL1_c2` e "
                  "`VL1_emp`) reestima as duas linhas. Compara-se com `VL_estimativas.csv`: todos os coeficientes "
                  "que não são indicadores de par, com os três EP (mesmos termos, na mesma ordem); a razão de chances "
                  "(estimativa, três EP, IC, p, p com t de G − 1, p de MV, p do score bootstrap Rademacher e Webb); "
                  "K5 e K10 (estimativa, três EP, IC delta e Fieller); e G de conjuntos e de candidatos e o número de "
                  "candidatos. Compara-se com `VL_resumo.json`: as contagens de identificação (iguais) e o resultado "
                  "do score bootstrap. Diferença absoluta ≤ 1e−8 se o valor gravado tem módulo até 1, relativa se "
                  "maior; NaN só casa com NaN (`_dif_rel` do 50, decisão 12 do 57x). Falhou, a execução para em "
                  "`FALHA_REPRODUCAO_<linha>`, nada novo é estimado e só o resumo do portão é gravado. O portão VL-5 "
                  "do 50 (M1, P1h e M4) não é refeito: o VG-R é o portão que o 52g pede."},
    {"data": "2026-10-28", "item": "Inferência e poucos clusters",
     "situacao": "O §1 pede inferência como no 52e e, com poucos conjuntos num ciclo, relatar o número de clusters e "
                 "dar peso ao score bootstrap. O 52g não fixa família de testes.",
     "resolucao": "Como no 52e: sanduíche CR1 por conjunto de escolha (curso × ciclo; num ciclo só, é o curso), fator "
                  "G/(G − 1), IC 95% e p pela normal; também o p com t de G − 1 graus de liberdade. Score bootstrap de "
                  "Kline–Santos (`score_bootstrap` do 50: ajuste restrito sob β = 0 partindo da estimativa irrestrita "
                  "sem a bolsa; Rademacher por enumeração completa se G ≤ 24, senão 199.999 sorteios com a semente "
                  "do 16; Webb também). Cada linha relata G de conjuntos. Não há família confirmatória nova (o 52g "
                  "chama VG-1 e VG-3 de robustez por ciclo); Holm nas duas (com o p por cluster e com o p do score) "
                  "vai como coluna descritiva."},
    {"data": "2026-10-28", "item": "Leitura do §2 por regra",
     "situacao": "O §2 lê o IC de VG-1 e VG-3 contra 1 e fala em \"mesmo sinal\" sem dizer de quê; e pede peso ao "
                 "score bootstrap.",
     "resolucao": "Para VG-1 e VG-3: IC 95% (CR1) que contém 1 → `IC_CONTEM_1`; IC que exclui 1 com o log da razão de "
                  "chances do mesmo sinal que o do VL-1 do ciclo 2 reproduzido → `EXCLUI_1_MESMO_SINAL`; do sinal "
                  "oposto → `EXCLUI_1_SINAL_OPOSTO`; sem estimativa → `SEM_ESTIMATIVA`. Leitura geral: algum "
                  "`EXCLUI_1_SINAL_OPOSTO` → `DEPENDE_DA_COMPOSICAO` (3ª linha do §2); senão, algum "
                  "`EXCLUI_1_MESMO_SINAL` → `APARECE_TAMBEM_EM_OUTRO_CICLO` (2ª linha, com o ciclo); senão, os dois "
                  "`IC_CONTEM_1` → `FORTE_SO_NO_CICLO_2` (1ª linha); com alguma linha sem estimativa, "
                  "`INCOMPLETA`. Peso ao score: para cada linha, `score_concorda` = (p do score Rademacher < 0,05) "
                  "igual a (IC exclui 1). Quando não concorda, o doc diz, na resposta curta, que a classificação "
                  "daquele ciclo não se confirma pelo score bootstrap; a regra não muda."},
    {"data": "2026-10-28", "item": "km equivalentes (VG-4)",
     "situacao": "O §1 pede os km equivalentes de +R$ 5 mil em VG-1 e VG-3, como no VL-4.",
     "resolucao": "Como no VL-4: K5 e K10 pela função `linha_km` do 25c (100 · passo · β / (−γ)), IC pelo método "
                  "delta e por Fieller, descritivos, sem teste. Se o IC do β contém zero, o doc diz que o IC dos km "
                  "também contém e que os km ficam instáveis."},
    {"data": "2026-10-28", "item": "Quem identifica (VG-5)",
     "situacao": "O §1 pede a contagem de pares de UF e de candidatos que identificam em cada ciclo.",
     "resolucao": "As contagens do `desenho_ef` do 50, as mesmas da seção 3 do 57x: pares no desenho e no modelo, "
                  "pares com variação de bolsa, alternativas e candidatos retirados, candidatos no modelo, candidatos "
                  "com variação de bolsa dentro de algum par e com a 1ª opção num par com variação, colunas de efeito "
                  "fixo. Para os quatro VL-1 (ciclos 1, 2, 3 e 1–3), com G de conjuntos."},
    {"data": "2026-10-28", "item": "Falha de convergência",
     "situacao": "Num ciclo só há menos candidatos por par; o Newton pode não convergir ou a matriz pode perder posto.",
     "resolucao": "Como no 50: a linha fica `NAO_CONVERGIU` com a nota da `estimar_ef`, sem trocar partida, "
                  "especificação ou amostra; a leitura dela é `SEM_ESTIMATIVA`. Coluna sem variação dentro de nenhum "
                  "candidato é omitida, como no 25, e a omissão vai na nota."},
    {"data": "2026-10-28", "item": "Saídas e figura",
     "situacao": "O §3 lista script, `VG_estimativas.csv`, `VG_resumo.json`, doc 57z e testes; não lista figura.",
     "resolucao": "Não há figura. O CSV tem, por linha estimada, os coeficientes fora dos indicadores de par, a razão "
                  "de chances por +R$ 5 mil e K5 e K10; as linhas reproduzidas (VL-1 dos ciclos 2 e 1–3) entram com "
                  "`papel = reproducao_VG-R`. `VL_*` não são regravadas."},
    {"data": "2026-10-28", "item": "Números do doc 57z",
     "situacao": "O pedido exige números só em blocos gerados.",
     "resolucao": "Todo número de resultado do 57z vem de `VG_*` por `--atualizar-doc`, entre marcadores "
                  "`<!-- VG:... -->`; o teste confere o doc contra o gerado e que não há número de resultado fora dos "
                  "blocos. A redação da resposta curta é escolhida por regra (`leitura`), sem texto escrito depois de "
                  "ver os números."},
]


# ---------------------------------------------------------------------------
# Estimação (funções do 50, sem alteração)
# ---------------------------------------------------------------------------

def ajustar_vg(chave: str, X: pd.DataFrame, D: dict, ef: dict, log=print) -> dict:
    """O `ajustar` do 50 para uma linha com par (estimar_ef + influência + score bootstrap), com o ciclo do VG."""
    e = ESPECS[chave]
    r = VL.estimar_ef(X, D, ef, modelo=chave, ciclo=e["ciclo"], amostra=AMOSTRA)
    r["n_efeitos_fixos"] = int(sum(1 for t in r["termos"] if t.startswith(PREFIXO_EF)))
    if r["ok"]:
        r["score_bootstrap"] = VL.score_bootstrap(r)
    for k in ("_A", "_D", "_scores", "_info"):
        r.pop(k, None)
    log(f"{chave}: ok={r['ok']} it={r.get('iteracoes')} termos={len(r['termos'])} candidatos={r['n_candidatos']} "
        f"G={r.get('G_conj')} grad_max={r.get('grad_max')}")
    return r


def estimar_vg(chave: str, dados: dict, conj_p1: pd.DataFrame, log=print) -> tuple[dict, dict]:
    """Os passos do `estimar_linha` do 50 (sem janela, efeito fixo de UF de origem × UF da vaga) no ciclo do VG."""
    e = ESPECS[chave]
    dv = {**dados, "conj_p1": conj_p1}
    conj, r1 = VL.subconjunto(conj_p1, dados["r1_p1"], e["ciclo"])
    D0 = P1.montar_desenho(conj, r1, None, dv)
    D, ef, diag_id = VL.desenho_ef(D0, dados, e["ef"])
    del D0
    X = VL.matriz_vl(D, dv, e, ef)
    r = ajustar_vg(chave, X, D, ef, log)
    del X, D
    gc.collect()
    return r, {"identificacao": diag_id}


def info(chave: str) -> dict:
    if chave in ESPECS:
        e = ESPECS[chave]
        return {"id_vg": e["id_vg"], "papel": e["papel"], "ciclo": e["ciclo"], "ef": e["ef"], "dist": e["dist"]}
    e = VL.ESPECS[chave]
    return {"id_vg": "VG-R", "papel": "reproducao_VG-R", "ciclo": e["ciclo"], "ef": e["ef"], "dist": e["dist"]}


# ---------------------------------------------------------------------------
# Linhas de saída
# ---------------------------------------------------------------------------

def _base(chave: str, r: dict, **kw) -> dict:
    i = info(chave)
    b = {c: np.nan for c in COLUNAS}
    b.update({"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "id_vg": i["id_vg"], "papel": i["papel"],
              "chave_modelo": chave, "modelo": ROTULO[chave], "ciclo": i["ciclo"], "efeito_fixo": i["ef"],
              "distancia": i["dist"], "entra_holm": False, "familia_holm": "", "metodo_score_rademacher": "",
              "g_conjuntos": r.get("G_conj"), "g_candidatos": r.get("G_cand"), "n_candidatos": r.get("n_candidatos"),
              "n_linhas_candidato_celula": r.get("n_linhas"), "n_conjuntos": r.get("n_conjuntos"),
              "n_efeitos_fixos": r.get("n_efeitos_fixos", 0), "status": r.get("status", "EXECUTADO"), "nota": ""})
    b.update(kw)
    return b


def linhas_coef(chave: str, r: dict) -> list[dict]:
    """Coeficientes fora dos indicadores de par, como no `linhas_modelo` do 50."""
    out = []
    nota_ef = f"{r['n_efeitos_fixos']} indicadores de par (decisão 1 do 57x), não relatados um a um"
    for t in r["termos"]:
        if t.startswith(PREFIXO_EF):
            continue
        c = P1.combinacao(r, P1.vetor(r, t))
        out.append(_base(chave, r, tipo_linha="coeficiente", termo=t, estimativa=c["coef"],
                         **{k: c[k] for k in ("ep_cluster_conjunto", "ep_mle", "ep_cluster_candidato", "ic95_inf",
                                              "ic95_sup", "p", "p_t_g_menos_1", "p_mle")},
                         nota=P1._juntar("coeficiente da utilidade" + (" por R$ 1 mil/mês" if t == B else ""),
                                         r.get("nota", ""), nota_ef)))
    return out


def linha_rc(chave: str, r: dict) -> dict:
    sb = r.get("score_bootstrap", {})
    return _base(chave, r, tipo_linha="razao_chances_por_5mil", termo=B, **VL.linha_rc(chave, r),
                 p_score_rademacher=sb.get("p_rademacher", np.nan), p_score_webb=sb.get("p_webb", np.nan),
                 metodo_score_rademacher=sb.get("metodo_rademacher", ""),
                 nota="exp(5·β), IC = exp do IC do log, EP pelo delta; p = o do β (cluster por conjunto)")


def linhas_km(chave: str, r: dict) -> list[dict]:
    out = []
    for comp, passo in (("K5", 5.0), ("K10", 10.0)):
        k = P1H.linha_km(r, passo, "VG-4", comp)
        out.append(_base(chave, r, id_vg="VG-4" if chave in ESPECS else "VG-R", tipo_linha="km_equivalentes",
                         termo=comp, **{c: k[c] for c in ("estimativa", "ep_cluster_conjunto", "ep_mle",
                                                          "ep_cluster_candidato", "ic95_inf", "ic95_sup",
                                                          "ic95_fieller_inf", "ic95_fieller_sup")},
                         nota=f"{comp} = 100 · {passo:g}β / (−γ), km; delta e Fieller (forma: {k['fieller_forma']}); "
                              "descritiva, sem teste"))
    return out


def linhas_modelo(chave: str, r: dict) -> list[dict]:
    if not r["ok"]:
        return [_base(chave, r, tipo_linha="razao_chances_por_5mil", termo=B, status="NAO_CONVERGIU",
                      nota=r.get("nota", ""))]
    return linhas_coef(chave, r) + [linha_rc(chave, r)] + linhas_km(chave, r)


def montar(res: dict) -> pd.DataFrame:
    linhas = []
    for chave in ORDEM:
        linhas += linhas_modelo(chave, res[chave])
    est = pd.DataFrame(linhas)[COLUNAS]
    mh = (est["tipo_linha"] == "razao_chances_por_5mil") & est["chave_modelo"].isin(NOVAS) & est["p"].notna()
    est.loc[mh, "entra_holm"] = True
    est.loc[mh, "familia_holm"] = FAMILIA_HOLM
    if mh.any():
        est.loc[mh, "p_holm"] = L.holm(est.loc[mh, "p"].to_numpy(dtype=float))
        est.loc[mh, "p_holm_score_rademacher"] = L.holm(est.loc[mh, "p_score_rademacher"].to_numpy(dtype=float))
    est["entra_holm"] = est["entra_holm"].astype(bool)
    return est


# ---------------------------------------------------------------------------
# Portão VG-R
# ---------------------------------------------------------------------------

COLS_RC = ["estimativa", "ep_cluster_conjunto", "ep_mle", "ep_cluster_candidato", "ic95_inf", "ic95_sup", "p",
           "p_t_g_menos_1", "p_mle", "p_score_rademacher", "p_score_webb"]
COLS_KM = ["estimativa", "ep_cluster_conjunto", "ep_mle", "ep_cluster_candidato", "ic95_inf", "ic95_sup",
           "ic95_fieller_inf", "ic95_fieller_sup"]
COLS_COEF = ["estimativa", "ep_cluster_conjunto", "ep_mle", "ep_cluster_candidato"]
COLS_N = ["g_conjuntos", "g_candidatos", "n_candidatos"]


def portao(novas: pd.DataFrame, vl: pd.DataFrame, res: dict, idt: dict, vl_resumo: dict,
           tol: float = TOL_REPRODUCAO) -> dict:
    """Compara as linhas reproduzidas (`novas`, no formato de `montar`) com `VL_estimativas.csv` e `VL_resumo.json`."""
    linhas, falha = [], None
    for chave in REPRODUZIDAS:
        difs: dict[str, float] = {}
        casou = bool(res[chave].get("ok"))
        a = novas[novas["chave_modelo"] == chave]
        g = vl[vl["chave_modelo"] == chave]
        for tipo, cols in (("coeficiente", COLS_COEF), ("razao_chances_por_5mil", COLS_RC + COLS_N),
                           ("km_equivalentes", COLS_KM)):
            at, gt = a[a["tipo_linha"] == tipo], g[g["tipo_linha"] == tipo]
            if list(at["termo"]) != list(gt["termo"]) or at.empty:
                casou = False
                continue
            for c in cols:
                difs[f"{tipo}_{c}"] = _dif_rel(at[c].to_numpy(dtype=float), gt[c].to_numpy(dtype=float))
        ida = idt.get(chave, {}).get("identificacao", {})
        idg = vl_resumo["identificacao"][chave]["identificacao"]
        iguais = ida == idg
        sb_a = res[chave].get("score_bootstrap", {})
        sb_g = vl_resumo["score_bootstrap"][chave]
        for k in ("g", "t_score", "p_rademacher", "p_webb", "n_rademacher", "n_webb"):
            difs[f"score_{k}"] = _dif_rel([sb_a.get(k, np.nan)], [sb_g.get(k, np.nan)])
        mesmo_metodo = (sb_a.get("metodo_rademacher") == sb_g.get("metodo_rademacher")
                        and sb_a.get("metodo_webb") == sb_g.get("metodo_webb"))
        passou = bool(casou and iguais and mesmo_metodo and difs and all(x <= tol for x in difs.values()))
        linhas.append({"linha": chave, "contra": "VL_estimativas.csv (coeficientes, razão de chances, K5, K10) e "
                                                 "VL_resumo.json (identificação, score bootstrap)",
                       "casou": casou, "identificacao_igual": bool(iguais), "metodo_score_igual": bool(mesmo_metodo),
                       **{f"dif_max_{k}": v for k, v in difs.items()}, "passou": passou})
        if not passou and falha is None:
            falha = f"FALHA_REPRODUCAO_{chave}"
    return {"status": "PASSOU" if falha is None else falha, "tolerancia": tol,
            "regra": ("VL-1 do ciclo 2 e dos ciclos 1–3 reestimados com a estimar_linha do 50 contra VL_estimativas.csv "
                      "(coeficientes fora dos pares e três EP; razão de chances com IC, p, p com t de G − 1, p de MV e "
                      "p do score bootstrap; K5 e K10 com delta e Fieller; G e candidatos) e VL_resumo.json "
                      "(contagens de identificação iguais; score bootstrap); diferença absoluta ≤ 1e−8 se o valor "
                      "gravado tem módulo ≤ 1, relativa se maior; NaN só casa com NaN"),
            "linhas": linhas}


# ---------------------------------------------------------------------------
# Leitura (regra fixada antes de rodar; decisão 5)
# ---------------------------------------------------------------------------

def _sel(est: pd.DataFrame, chave: str, tipo: str, termo: str | None = None) -> pd.Series:
    s = est[(est["chave_modelo"] == chave) & (est["tipo_linha"] == tipo)]
    if termo is not None:
        s = s[s["termo"] == termo]
    if len(s) != 1:
        raise FalhaValidacao(f"esperava 1 linha {chave} {tipo} {termo}, achei {len(s)}")
    return s.iloc[0]


def regra_linha(l: pd.Series, ref: pd.Series) -> str:
    """§2: IC da razão de chances de um ciclo contra 1; sinal contra o do VL-1 do ciclo 2."""
    if pd.isna(l["estimativa"]) or pd.isna(l["ic95_inf"]):
        return "SEM_ESTIMATIVA"
    if l["ic95_inf"] <= 1.0 <= l["ic95_sup"]:
        return "IC_CONTEM_1"
    if np.sign(math.log(l["estimativa"])) == np.sign(math.log(ref["estimativa"])):
        return "EXCLUI_1_MESMO_SINAL"
    return "EXCLUI_1_SINAL_OPOSTO"


def score_concorda(l: pd.Series) -> bool | None:
    if pd.isna(l["p_score_rademacher"]) or pd.isna(l["ic95_inf"]):
        return None
    return bool((l["p_score_rademacher"] < ALFA) == (not (l["ic95_inf"] <= 1.0 <= l["ic95_sup"])))


def leitura(est: pd.DataFrame) -> dict:
    ref = _sel(est, REFERENCIA_SINAL, "razao_chances_por_5mil")
    out = {}
    for chave in NOVAS:
        l = _sel(est, chave, "razao_chances_por_5mil")
        out[chave] = {"regra": regra_linha(l, ref), "ciclo": ESPECS[chave]["ciclo"],
                      "ic_contem_1": None if pd.isna(l["ic95_inf"]) else bool(l["ic95_inf"] <= 1.0 <= l["ic95_sup"]),
                      "score_concorda": score_concorda(l),
                      "g_conjuntos": None if pd.isna(l["g_conjuntos"]) else int(l["g_conjuntos"])}
    regras = [out[k]["regra"] for k in NOVAS]
    if "SEM_ESTIMATIVA" in regras:
        geral = "INCOMPLETA"
    elif "EXCLUI_1_SINAL_OPOSTO" in regras:
        geral = "DEPENDE_DA_COMPOSICAO"
    elif "EXCLUI_1_MESMO_SINAL" in regras:
        geral = "APARECE_TAMBEM_EM_OUTRO_CICLO"
    else:
        geral = "FORTE_SO_NO_CICLO_2"
    km = {}
    for chave in NOVAS:
        if out[chave]["regra"] == "SEM_ESTIMATIVA":
            continue
        b = _sel(est, chave, "coeficiente", B)
        km[chave] = {"km": float(_sel(est, chave, "km_equivalentes", "K5")["estimativa"]),
                     "ic_beta_contem_0": bool(b["ic95_inf"] <= 0 <= b["ic95_sup"])}
    return {"linhas": out, "geral": geral, "referencia_do_sinal": REFERENCIA_SINAL,
            "ciclos_que_excluem_1_mesmo_sinal": [ESPECS[k]["ciclo"] for k in NOVAS
                                                 if out[k]["regra"] == "EXCLUI_1_MESMO_SINAL"],
            "VG4": km}


# ---------------------------------------------------------------------------
# Documento 57z
# ---------------------------------------------------------------------------

def bloco(nome: str, corpo: str) -> list[str]:
    return [f"<!-- VG:{nome}:inicio -->", corpo, f"<!-- VG:{nome}:fim -->"]


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
         "números). As 13 decisões do 57x continuam valendo; em qualquer ambiguidade nova, vale a leitura mais "
         "próxima do script 50.", ""]
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
    t = [f"**Portão de reprodução (VG-R): {p['status']}.** Antes de qualquer conta nova, as funções do script 50, "
         "importadas sem alteração, reproduzem o VL-1 já gravado. A coluna mostra a maior diferença entre todas as "
         "quantidades comparadas da linha (absoluta quando o valor gravado tem módulo até 1, relativa acima disso); a "
         "lista completa está em `portao` de `VG_resumo.json`.", "",
         _tab(["Linha", "Dif. máx.", "Contagens de identificação iguais", "Portão"], linhas)]
    if p["status"] != "PASSOU":
        t += ["", f"A execução parou em `{p['status']}`: nada novo foi estimado (adendo 52g)."]
    return "\n".join(t)


def texto_identificacao(est: pd.DataFrame, resumo: dict) -> str:
    idt = resumo["identificacao"]
    linhas = []
    for chave in ORDEM:
        d = idt[chave]["identificacao"]
        r = _sel(est, chave, "razao_chances_por_5mil")
        linhas.append([ROTULO_CURTO[chave], _int(r["g_conjuntos"]),
                       f"{d['pares_no_desenho']} → {d['pares_no_modelo']}", f"{d['pares_com_variacao_de_bolsa']}",
                       f"{d['origens_com_algum_par_com_variacao']} de {d['origens_no_modelo']}",
                       f"{d['alternativas_retiradas_par_sem_escolha']} + {d['alternativas_retiradas_por_separacao']} "
                       f"de {d['alternativas_no_desenho']}",
                       f"{d['candidatos_retirados_uma_so_alternativa']}", f"{d['candidatos_no_modelo']}",
                       f"{d['candidatos_com_variacao_de_bolsa_em_algum_par']}",
                       f"{d['candidatos_com_1a_opcao_em_par_com_variacao']}", f"{d['colunas_de_efeito_fixo']}"])
    frases = []
    for chave in NOVAS:
        d = idt[chave]["identificacao"]
        r = _sel(est, chave, "razao_chances_por_5mil")
        frases.append(f"no {ROTULO_CURTO[chave]}, {d['pares_com_variacao_de_bolsa']} pares (UF de origem, UF da vaga) "
                      f"com bolsas diferentes, {d['candidatos_com_variacao_de_bolsa_em_algum_par']} dos "
                      f"{d['candidatos_no_modelo']} candidatos do modelo veem essa variação e "
                      f"{_int(r['g_conjuntos'])} conjuntos de escolha (cursos)")
    return "\n".join([
        "**Quem identifica o peso da bolsa em cada ciclo (VG-5).** O peso vem só de candidatos que veem, dentro de "
        "uma mesma UF, vagas com bolsas diferentes: " + "; ".join(frases) + ".", "",
        "Colunas: G = conjuntos de escolha (clusters); pares no desenho → pares que ficam no modelo (os sem escolha "
        "saem, decisão 2 do 57x); pares com variação de bolsa; UFs de origem com algum par com variação; alternativas "
        "retiradas por par sem escolha + por separação; candidatos retirados por ficarem com uma só alternativa; "
        "candidatos no modelo; candidatos com variação de bolsa dentro de algum par; candidatos com a 1ª opção num "
        "par com variação; colunas de efeito fixo.", "",
        _tab(["Ciclo", "G", "Pares (desenho → modelo)", "Pares com variação", "Origens com variação",
              "Alternativas retiradas", "Candidatos retirados", "Candidatos no modelo", "Candidatos com variação",
              "1ª opção em par com variação", "Colunas de efeito fixo"], linhas)])


def tabela_principais(est: pd.DataFrame) -> str:
    linhas = []
    for chave in ORDEM:
        r = _sel(est, chave, "razao_chances_por_5mil")
        linhas.append([ROTULO[chave], _int(r["n_candidatos"]), _int(r["g_conjuntos"]), _rc(r), _p(r["p"]),
                       _p(r["p_t_g_menos_1"]), _p(r["p_score_rademacher"]), _p(r["p_score_webb"]),
                       str(r["metodo_score_rademacher"]) if isinstance(r["metodo_score_rademacher"], str) else "—",
                       _p(r["p_holm"]) if r["entra_holm"] else "—",
                       _p(r["p_holm_score_rademacher"]) if r["entra_holm"] else "—"])
    return "\n".join([
        "Razão de chances da 1ª opção por +R$ 5 mil de bolsa, comparando só vagas da mesma UF vistas por médicos da "
        "mesma UF de origem. IC 95% e p (H0: β = 0) com cluster por conjunto de escolha (curso × ciclo); p com t de "
        "G − 1; p do score bootstrap (Kline–Santos, Rademacher e Webb), que pesa mais quando G é pequeno; Holm "
        "descritivo nas duas linhas novas (decisão 4). As linhas do ciclo 2 e dos ciclos 1–3 são o VL-1 do 57x, "
        "reproduzido pelo portão.", "",
        _tab(["Linha", "Candidatos", "Conjuntos (G)", "RC [IC 95%]", "p", "p (t, G − 1)", "p score (Rademacher)",
              "p score (Webb)", "Score: método", "p Holm", "p Holm (score)"], linhas)])


def tabela_km(est: pd.DataFrame) -> str:
    linhas = []
    for chave in ORDEM:
        for comp in ("K5", "K10"):
            s = est[(est["chave_modelo"] == chave) & (est["tipo_linha"] == "km_equivalentes") & (est["termo"] == comp)]
            if s.empty:
                linhas.append([ROTULO[chave], comp, "— (NAO_CONVERGIU)", "—", "—"])
                continue
            r = s.iloc[0]
            linhas.append([ROTULO[chave], comp, f"{_n(r['estimativa'], 0)} km", _ic(r["ic95_inf"], r["ic95_sup"], 0),
                           _ic(r["ic95_fieller_inf"], r["ic95_fieller_sup"], 0)])
    return "\n".join([
        "VG-4: quantos km a menos de distância origem–vaga pesam na escolha como +R$ 5 mil (K5) ou +R$ 10 mil (K10), "
        "comparando vagas da mesma UF: 100 · passo · β / (−γ), com γ o peso da distância por 100 km. IC pelo método "
        "delta e por Fieller; descritivo, sem teste. Fieller com limite infinito quer dizer que o IC do β contém "
        "zero.", "",
        _tab(["Linha", "Passo", "km equivalentes", "IC 95% (delta)", "IC 95% (Fieller)"], linhas)])


def tabela_controles(est: pd.DataFrame) -> str:
    termos = list(est[(est["chave_modelo"] == "VL1_emp") & (est["tipo_linha"] == "coeficiente")]["termo"])
    linhas = []
    for t in termos:
        cel = []
        for chave in ORDEM:
            s = est[(est["chave_modelo"] == chave) & (est["tipo_linha"] == "coeficiente") & (est["termo"] == t)]
            cel.append("—" if s.empty else f"{_n(s.iloc[0]['estimativa'], 3)} "
                                           f"{_ic(s.iloc[0]['ic95_inf'], s.iloc[0]['ic95_sup'], 3)}")
        linhas.append([f"`{t}`"] + cel)
    return "\n".join([
        "Os coeficientes que não são indicadores de par (log-chance; IC 95% com cluster por conjunto). \"—\" é termo "
        "omitido por não variar dentro de nenhum candidato naquele ciclo. Todas as linhas estão em "
        "`VG_estimativas.csv`.", "",
        _tab(["Termo"] + [ROTULO_CURTO[k] for k in ORDEM], linhas)])


ROTULO_REGRA = {
    "IC_CONTEM_1": "IC que contém 1",
    "EXCLUI_1_MESMO_SINAL": "IC que exclui 1, do mesmo lado que no ciclo 2",
    "EXCLUI_1_SINAL_OPOSTO": "IC que exclui 1, do lado oposto ao do ciclo 2",
    "SEM_ESTIMATIVA": "sem estimativa",
}


def texto_resposta(est: pd.DataFrame, resumo: dict) -> str:
    lei = resumo["leitura"]
    ciclos = " e ".join(f"no ciclo {c}" for c in lei["ciclos_que_excluem_1_mesmo_sinal"])
    geral = {
        "FORTE_SO_NO_CICLO_2": "**Comparando só vagas da mesma UF, o peso da bolsa na escolha da 1ª opção é forte só "
                               "no ciclo 2.** Nos ciclos 1 e 3, separados, o IC da razão de chances contém 1 (1ª "
                               "linha do §2 do adendo, como na especificação base).",
        "APARECE_TAMBEM_EM_OUTRO_CICLO": f"**Comparando só vagas da mesma UF, o peso da bolsa na escolha da 1ª opção "
                                         f"aparece também {ciclos}, do mesmo lado que no ciclo 2** (2ª linha do §2 do "
                                         "adendo).",
        "DEPENDE_DA_COMPOSICAO": "**Em algum ciclo, comparando só vagas da mesma UF, a bolsa maior pesa contra a "
                                 "escolha, com IC que exclui 1.** A leitura empilhada passa a depender da composição "
                                 "dos ciclos (3ª linha do §2 do adendo).",
        "INCOMPLETA": "**A leitura está incompleta: algum ciclo ficou sem estimativa** (ver a seção 4).",
    }[lei["geral"]]
    t = [geral]
    for chave in ("VG1", "VL1_c2", "VG3", "VL1_emp"):
        r = _sel(est, chave, "razao_chances_por_5mil")
        frase = (f"- **{ROTULO_CURTO[chave].capitalize()}:** razão de chances {_rc(r)}, p {_p(r['p'])}, p do score "
                 f"bootstrap {_p(r['p_score_rademacher'])}, com {_int(r['g_conjuntos'])} conjuntos de escolha")
        if chave in NOVAS:
            li = lei["linhas"][chave]
            frase += f"; {ROTULO_REGRA[li['regra']]}."
            if li["score_concorda"] is False:
                frase += (" O score bootstrap não confirma essa classificação: "
                          + ("o p dele fica abaixo de 5% mesmo com o IC contendo 1." if li["ic_contem_1"] else
                             "o p dele fica acima de 5% mesmo com o IC excluindo 1.")
                          + " Com poucos conjuntos, o score bootstrap merece mais peso (§1 do adendo).")
        else:
            frase += " (VL-1 do 57x, reproduzido)."
        t.append(frase)
    km = lei["VG4"]
    partes = []
    for chave in NOVAS:
        if chave not in km:
            continue
        k5 = _sel(est, chave, "km_equivalentes", "K5")
        p = (f"{_n(k5['estimativa'], 0)} km no {ROTULO_CURTO[chave]} (IC delta "
             f"{_ic(k5['ic95_inf'], k5['ic95_sup'], 0)})")
        if km[chave]["ic_beta_contem_0"]:
            p += ", com IC do β que contém zero: o IC dos km também contém zero e o número é instável"
        partes.append(p)
    k2 = _sel(est, "VL1_c2", "km_equivalentes", "K5")
    if partes:
        t.append("**km (VG-4).** Comparando vagas da mesma UF, +R$ 5 mil pesam como " + "; e ".join(partes) +
                 f". No ciclo 2, {_n(k2['estimativa'], 0)} km.")
    t.append("**Em linguagem simples.** A pergunta era se o que se vê no ciclo 2 (o candidato escolhe mais a vaga com "
             "bolsa maior, mesmo comparando só vagas da mesma UF) também aparece nos ciclos 1 e 3, olhados um de "
             "cada vez. Cada ciclo tem poucos cursos, e o cluster é o curso: por isso o número de conjuntos vai ao "
             "lado de cada linha e o score bootstrap pesa. A bolsa aqui é o pacote do corte de IVS (bolsa e outras "
             "regras federais que mudam nos mesmos cortes), não a participação no PMM-E; a origem do candidato é "
             "preferência revelada, não efeito causal; e tudo vale para quem se candidatou, dentro das vagas "
             "abertas.")
    return "\n\n".join(t)


def texto_leitura(resumo: dict) -> str:
    lei = resumo["leitura"]
    linhas = []
    for chave in NOVAS:
        li = lei["linhas"][chave]
        linhas.append([ROTULO[chave], f"`{li['regra']}`", "—" if li["ic_contem_1"] is None else
                       ("sim" if li["ic_contem_1"] else "não"),
                       "—" if li["score_concorda"] is None else ("sim" if li["score_concorda"] else "**não**"),
                       _int(li["g_conjuntos"])])
    return "\n".join([
        f"Regra fixada no código antes de rodar (decisão 5). Sinal de referência: o do VL-1 do ciclo 2. Leitura geral: "
        f"`{lei['geral']}`.", "",
        _tab(["Linha", "Regra", "IC contém 1", "Score bootstrap concorda", "Conjuntos (G)"], linhas)])


PENDENTE = "*Pendente: preenchido pelo script depois do portão de reprodução.*"


def gerar_doc(est: pd.DataFrame | None, resumo: dict | None) -> str:
    """Doc 57z. Sem resumo (pré-registro), só cabeçalho, decisões e limites."""
    tem_portao = resumo is not None and "portao" in resumo
    ok = tem_portao and resumo["portao"]["status"] == "PASSOU" and est is not None
    Lh = [
        "# 57z. Escolha da 1ª opção com o par de UFs fixado, ciclo a ciclo (adendo 52g)",
        "",
        "> **Gerado por** `scripts/rdd_bolsa/53_VL1_por_ciclo.py` a partir de `output/rdd_bolsa/VG_*`; não editar à mão "
        "(o teste `tests/test_VL1_por_ciclo.py` confere que este arquivo é igual ao gerado; `--atualizar-doc` o "
        "regrava das saídas).<br>",
        f"> **Adendo:** [`52g_adendo_VL1_por_ciclo.md`](52g_adendo_VL1_por_ciclo.md), congelado em 28/10/2026 antes de "
        f"rodar (commit `{COMMIT_ADENDO}`); SHA-256 em `adendo` de `VG_resumo.json`, conferido pelo teste. Especificação "
        "de origem: VL-1 do adendo [52e](52e_adendo_escolha_localizacao_par.md), doc "
        "[57x](57x_resultados_escolha_localizacao_par.md), com as 13 decisões de implementação de lá.<br>",
        "> **Estatuto:** `ADENDO_52G_POS_RESULTADO`. O VL-1 dos ciclos 1–3 e do ciclo 2 já tinha sido visto; isto é "
        "robustez por ciclo, não teste confirmatório novo. Toda linha de `VG_estimativas.csv` e o resumo têm "
        "`natureza_dos_dados = EMPIRICO`.<br>",
        "> **Decisão do autor (28/10/2026):** \"a hipótese é simplesmente sobre o efeito bolsa → 1ª opção\", com \"só "
        "comparação entre municípios da mesma UF\".<br>",
        "> **Saídas:** `output/rdd_bolsa/VG_estimativas.csv` e `VG_resumo.json`. As saídas `VL_*` não são regravadas, e o "
        "doc 57x não é editado.<br>",
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
    Lh += ["## 2. Portão de reprodução (VG-R)", ""]
    Lh += [*bloco("portao", texto_portao(resumo)), ""] if tem_portao else [PENDENTE, ""]
    if ok:
        Lh += [
            "## 3. Quem identifica em cada ciclo (VG-5)",
            "",
            *bloco("identificacao", texto_identificacao(est, resumo)),
            "",
            "## 4. Resultados",
            "",
            "### 4.1 Razão de chances por ciclo (VG-1 e VG-3)",
            "",
            *bloco("principais", tabela_principais(est)),
            "",
            "### 4.2 km equivalentes (VG-4)",
            "",
            *bloco("km", tabela_km(est)),
            "",
            "### 4.3 Os outros pesos do modelo",
            "",
            *bloco("controles", tabela_controles(est)),
            "",
            "## 5. Leitura do §2 por regra",
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
        "- **Pós-resultado.** O VL-1 empilhado e o do ciclo 2 já eram conhecidos. O adendo foi congelado antes de "
        "rodar, mas isto é robustez por ciclo, não teste confirmatório novo.",
        "- **Poucos conjuntos por ciclo.** Num ciclo só, o cluster é o curso, e são poucos. O IC com cluster pode ser "
        "otimista; por isso o score bootstrap vai ao lado, e o número de conjuntos de cada linha está na tabela.",
        "- **Identificação estreita.** Com o par de UFs, o peso da bolsa vem só de UFs que têm vagas de faixas "
        "diferentes e de candidatos que veem essa variação (seção 3). Num ciclo só, são menos pares e menos "
        "candidatos.",
        "- **Pares sem escolha saem.** As vagas de pares que ninguém daquela origem escolheu naquele ciclo saem do "
        "conjunto (decisão 2 do 57x); o conjunto de escolha do modelo fica menor que o do M1.",
        "- **Escolha condicional.** Tudo vale para quem se candidatou, dentro das vagas abertas do seu curso e ciclo; "
        "IIA do logit condicional.",
        "- **Pacote do corte.** O peso da bolsa é identificado pelos saltos nos cortes de IVS, com o IVS em spline "
        "contínua; nos mesmos cortes mudam outras regras federais (auditoria 18). Não é efeito da participação no "
        "PMM-E nem do Agora Tem Especialistas.",
        "- **Origem não é causal.** A origem é o município do vínculo médico no CNES (G1), não a residência; o peso da "
        "origem é preferência revelada, não efeito causal.",
        "- **km são razões.** Com o peso da bolsa perto de zero, os km equivalentes ficam instáveis e não são preço.",
    ]
    return "\n".join(Lh) + "\n"


# ---------------------------------------------------------------------------
# Execução
# ---------------------------------------------------------------------------

def entradas(dados: dict) -> list[dict]:
    be = P1.bloco_entrada
    base = VL.entradas(dados)
    return [
        be(ADENDO_MD, "adendo 52g (especificação, somente lido)", "repositório", "2026-10-28", "§1–§4", "documento",
           "-", "-"),
        be(VL_CSV, "alvo do portão VG-R (VL-1 dos ciclos 2 e 1–3)", "script 50", "2026-10-27", "VL1_c2, VL1_emp",
           "especificação × termo", "chave_modelo, tipo_linha, termo", "-"),
        be(VL_RESUMO, "alvo do portão VG-R (identificação e score bootstrap)", "script 50", "2026-10-27",
           "VL1_c2, VL1_emp", "linha", "identificacao, score_bootstrap", "-"),
        be(SCRIPT_50, "funções do adendo 52e (importadas sem alteração)", "repositório", "-", "-", "código", "-", "-"),
        *base,
    ]


def remover_saidas_calculadas() -> None:
    if OUT_CSV.exists():
        OUT_CSV.unlink()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--atualizar-doc", action="store_true", help="só regrava o doc 57z a partir das saídas")
    ap.add_argument("--pre-registro", action="store_true",
                    help="grava o doc 57z só com as decisões (antes de qualquer estimativa)")
    args = ap.parse_args(argv)
    if args.pre_registro:
        if OUT_RESUMO.exists():
            raise FalhaValidacao("VG_resumo.json já existe: o pré-registro só vale antes das estimativas")
        DOC.write_text(gerar_doc(None, None), encoding="utf-8")
        return 0
    if args.atualizar_doc:
        atualizar_doc()
        return 0
    t0 = time.time()

    def log(m: str) -> None:
        print(f"[{time.time() - t0:7.0f}s] {m}", flush=True)

    hash_vl = {rel(p): sha256(p) for p in (VL_CSV, VL_RESUMO)}
    dados = P1.carregar()
    log("insumos do P1 carregados")
    q1302, q1903 = VC.ler_quadros_c2()
    conf_antiga = VC.conferir_versao_antiga(dados["conj"], q1903)
    conf_a36 = VC.conferir_contra_a36(q1302)
    conj_p1_c, corr = VC.corrigir(dados["conj_p1"], q1302)
    log("quadro de 13/02 conferido e conjunto do P1 corrigido")
    celulas = {str(c): int(n) for c, n in conj_p1_c["ciclo"].value_counts().sort_index().items()}
    resumo = {
        "etapa": "VG_VL1_por_ciclo",
        "natureza_dos_dados": NATUREZA,
        "estatuto": ESTATUTO,
        "data_execucao": DATA_EXECUCAO,
        "script": rel(Path(__file__)),
        "adendo": {"arquivo": rel(ADENDO_MD), "sha256": sha256(ADENDO_MD), "commit_de_congelamento": COMMIT_ADENDO},
        "protocolos": {rel(p): sha256(p) for p in (ADENDO_52E, VL.PROTOCOLO_52, VL.PROTOCOLO_52B, VL.ADENDO_52C)},
        "conferencias": {"versao_antiga_do_conjunto": conf_antiga, "quadro_1302_contra_a36": conf_a36,
                         "correcao_ciclo2": {k: corr[k] for k in ("celulas_ciclo2_no_conjunto",
                                                                  "celulas_sem_linha_no_quadro_1302",
                                                                  "celulas_com_vagas_imediatas_diferentes",
                                                                  "imputadas")},
                         "celulas_por_ciclo_no_conjunto_do_P1": celulas},
        "decisoes": DECISOES,
        "especificacoes": {**{k: VL.ESPECS[k] for k in REPRODUZIDAS}, **ESPECS},
        "entradas": entradas(dados),
        "integridade": ("nada simulado nem imputado; data/ só lido; IVS do a08 (o arquivo local de IVS da auditoria 16 "
                        "não é lido); só agregados em output/ (sem nome, CPF, CRM nem pseudônimo de candidato); saídas "
                        "VL_* e demais não regravadas"),
        "linguagem": ("escolha condicional a se candidatar, dentro das vagas abertas; a bolsa mede o pacote do corte e o "
                      "incentivo marginal; a origem é preferência revelada, não efeito causal; não é efeito da "
                      "participação no PMM-E"),
        "tempo_execucao_nao_registrado": "fora do resumo para que duas execuções deem o mesmo hash",
    }

    # Portão (VG-R): nada novo antes dele.
    res: dict[str, dict] = {}
    idt: dict[str, dict] = {}
    for chave in REPRODUZIDAS:
        res[chave], idt[chave] = VL.estimar_linha(chave, dados, conj_p1_c, log)
    vl = pd.read_csv(VL_CSV, dtype={"ciclo": str})
    vl_resumo = json.loads(VL_RESUMO.read_text(encoding="utf-8"))
    novas = pd.DataFrame([x for k in REPRODUZIDAS for x in linhas_modelo(k, res[k])])
    port = portao(novas, vl, res, idt, vl_resumo)
    resumo["portao"] = port
    log(f"portão: {port['status']}")
    if port["status"] != "PASSOU":
        remover_saidas_calculadas()
        resumo["saidas"] = {}
        gravar_json(OUT_RESUMO, resumo)
        atualizar_doc()
        print(f"{port['status']}: nada novo estimado (adendo 52g)", file=sys.stderr)
        return 3

    for chave in NOVAS:
        res[chave], idt[chave] = estimar_vg(chave, dados, conj_p1_c, log)
    est = montar(res)
    sem = est[est["estimativa"].isna() & (est["status"] == "EXECUTADO")]
    if len(sem):
        raise FalhaValidacao(f"{len(sem)} linhas executadas sem estimativa")
    est.to_csv(OUT_CSV, index=False, float_format="%.10g")
    est = ler_est()
    if {rel(p): sha256(p) for p in (VL_CSV, VL_RESUMO)} != hash_vl:
        raise FalhaValidacao("VL_* mudou durante a execução")
    resumo["identificacao"] = idt
    resumo["score_bootstrap"] = {k: res[k].get("score_bootstrap", {}) for k in ORDEM}
    resumo["convergencia"] = {k: {"ok": bool(r["ok"]), "status": r.get("status"), "iteracoes": r.get("iteracoes"),
                                  "omitidas": r.get("omitidas", []), "n_efeitos_fixos": r.get("n_efeitos_fixos", 0),
                                  "grad_max": r.get("grad_max"), "decremento_final": r.get("decremento_final"),
                                  "partida": r.get("partida"),
                                  "termos_sem_efeito_fixo": [t for t in r["termos"] if not t.startswith(PREFIXO_EF)],
                                  "nota": r.get("nota", "")} for k, r in res.items()}
    resumo["covariancias"] = VL.covariancias({k: res[k] for k in REPRODUZIDAS})
    resumo["covariancias"].update(covariancias_vg(res))
    resumo["leitura"] = leitura(est)
    resumo["inferencia"] = {"principal": "sanduíche com cluster por conjunto de escolha (curso × ciclo), fator G/(G−1)",
                            "holm": FAMILIA_HOLM,
                            "score_bootstrap": "Kline–Santos, H0: β = 0, Rademacher e Webb (funções do script 50/16)",
                            "z_bilateral_95": VL.Z95}
    resumo["vl_nao_regravado"] = hash_vl
    resumo["saidas"] = {rel(OUT_CSV): sha256(OUT_CSV)}
    gravar_json(OUT_RESUMO, resumo)
    atualizar_doc()
    log(f"gravado: {rel(OUT_CSV)}, {rel(OUT_RESUMO)}, {rel(DOC)}")
    return 0


def covariancias_vg(res: dict) -> dict:
    """θ e bloco da covariância de bolsa e distância das linhas novas, para recálculo nos testes."""
    out = {}
    for chave in NOVAS:
        r = res[chave]
        if not r.get("ok"):
            continue
        termos = [t for t in (B, DIST) if t in r["termos"]]
        k = [r["termos"].index(t) for t in termos]
        out[chave] = {"termos": termos, "theta": np.asarray(r["theta"])[k].tolist(),
                      "V_cluster_conjunto": np.asarray(r["V_conj"])[np.ix_(k, k)].tolist(),
                      "g_conjuntos": r["G_conj"]}
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
