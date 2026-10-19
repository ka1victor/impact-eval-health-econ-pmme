"""X6 do protocolo exploratório pós-síntese: poder, efeito mínimo detectável e o que cada IC descarta.

Protocolo: `docs/06_execucao/45_protocolo_exploratorio_pos_sintese.md`, §3 X6
(congelado em 19/10/2026, depois da síntese E8 e antes de abrir os outcomes X).
Estatuto: **exploratório e pós-resultado**. Nada aqui é teste confirmatório,
nada muda o protocolo 40, os resultados E3–E9 nem o Holm das primárias. Toda
linha leva `estatuto = EXPLORATORIO_POS_SINTESE`.

O que este script faz
---------------------
Nenhuma estimação nova. Lê as saídas já auditadas do E6, E7 e E9
(`output/rdd_bolsa/`) e, para cada linha principal, calcula só aritmética sobre
o EP e o IC já publicados:

- **MDE de 80%** (poder 80%, teste bicaudal a 5%): 2,8 × EP, a mesma convenção
  do E5 (`11_inferencia_alternativa.py`, `FATOR_MDE`);
- **IC 95% convencional** (copiado) e **IC 90%** (τ ± z₀,₉₅ × EP);
- **equivalência (TOST a 5%)**: a menor margem simétrica δ tal que o IC 90% fica
  dentro de [−δ, +δ], isto é, δ = |τ| + z₀,₉₅ × EP. Para toda margem maior que δ,
  os dois testes unilaterais rejeitam a 5%;
- os mesmos números **relativos à média abaixo do corte** na janela
  (`media_bruta_abaixo`). Nas linhas empilhadas, a base é a média das médias
  abaixo de cada grupo ponderada por `pesos_grupos`, os mesmos pesos que definem
  o estimando empilhado (Σ ω_g τ_g). No E7 (DiRD), a base é a média bruta do
  **pré** abaixo do corte (linha `nivel_pre`), como no doc 44;
- comparação com as referências do protocolo 40, §7 (+10 p.p. de preenchimento,
  +25% de candidaturas) e com magnitudes da literatura lidas **só** do doc 20 da
  seção 03 (trecho literal procurado no texto; o número é extraído do trecho por
  expressão regular; falha fechada se o trecho não existir);
- se o IC honesto (Armstrong e Kolesár, M do protocolo, fator 1, copiado da
  linha principal) é informativo.

Linhas cobertas:
- E6: todas as linhas `principal` de P1, F0, F1, F2 e F4 (cada corte e
  empilhado; ciclos empilhados onde definidos) e as linhas `poisson_local` de
  F1.1 (escala relativa, comparável aos +25% do protocolo);
- E7: linhas `principal` (DiRD) da família F3 (F3.1 em U e V1, F3.2, F3.3,
  F3.P1, F3.P2), cada corte e empilhado;
- E9: coeficiente da bolsa no modelo principal (logit condicional da 1ª opção,
  conjunto principal, spline linear + bolsa linear), ciclos 1, 2, 3 e
  empilhado, em coeficiente por R$ mil, log da razão de chances e razão de
  chances por +R$ 5 mil, variação média da probabilidade (p.p. e relativa) e a
  elasticidade-arco implícita da escolha em cada corte (variação relativa sobre
  o degrau relativo da bolsa do E8).

Contraste
---------
E6 (RDD em nível): pacote do corte. E7 (DiRD): bolsa + variação das
co-políticas. E9: degrau da bolsa na escolha da 1ª opção entre células
(realocação, não total de candidatos). Nenhum é efeito da participação no PMM-E
nem do Agora Tem Especialistas.

Falha fechada
-------------
Para se: uma entrada faltar ou não for EMPIRICO; o IC 95% copiado não for
τ ± 1,96 × EP (então 2,8 × EP não seria o MDE da mesma inferência); o IC
honesto da linha principal diferir da linha `ic_honesto` com fator 1; os pesos
de um grupo empilhado não somarem 1; um trecho da literatura não existir no doc
20. Base relativa que não existe fica vazia com o motivo, nunca imputada.

Uso
---
    python3 scripts/rdd_bolsa/20_poder_descartes.py                 # saídas, figura e bloco X6 do doc 46
    python3 scripts/rdd_bolsa/20_poder_descartes.py --atualizar-doc # só regrava os blocos X6 do doc 46
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from statistics import NormalDist

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "rdd_bolsa"
E6_EST = OUT / "E6_estimativas.csv"
E7_EST = OUT / "E7_estimativas.csv"
E9_EST = OUT / "E9_estimativas.csv"
E9_EFM = OUT / "E9_efeitos_marginais.csv"
E8_RESUMO = OUT / "E8_resumo.json"
PROTOCOLO_X = ROOT / "docs" / "06_execucao" / "45_protocolo_exploratorio_pos_sintese.md"
PROTOCOLO_40 = ROOT / "docs" / "06_execucao" / "40_protocolo_multioutcome_rdd_bolsa.md"
LITERATURA = ROOT / "docs" / "03_literatura_empirica" / "20_evidencia_empirica_hipotese_remuneracao_preenchimento.md"
DOC46 = ROOT / "docs" / "06_execucao" / "46_resultados_exploratorios_pos_sintese.md"

NOME_CSV = "X6_poder_descartes.csv"
NOME_RESUMO = "X6_resumo.json"
DIR_FIG = OUT / "X6_figuras"
NOME_FIG = "X6_descartes.png"

ESTATUTO = "EXPLORATORIO_POS_SINTESE"

# Parâmetros (protocolo 40, §6–§7; protocolo 45, §3 X6; convenção do E5). Não são resultados.
ALFA = 0.05
PODER = 0.80
FATOR_MDE = 2.8                                  # 2,8 × EP: 80% de poder, 5% bicaudal (E5, FATOR_MDE)
Z95 = NormalDist().inv_cdf(1 - ALFA / 2)          # IC 95% bicaudal
Z90 = NormalDist().inv_cdf(1 - ALFA)              # IC 90% = TOST a 5%
REF_PREENCHIMENTO = 0.10                          # +10 p.p. (protocolo 40, §7)
REF_CANDIDATURAS = 0.25                           # +25% (protocolo 40, §7)
EMPILHADO = "empilhado"
FAMILIAS_E6 = ("P1", "F0", "F1", "F2", "F4")
OUTCOMES_E7 = ("F3.1", "F3.2", "F3.3", "F3.P1", "F3.P2")
COND = "logit_condicional_1a_opcao"
PRINCIPAL_E9 = "spline_linear__bolsa_linear"
CICLOS_E9 = ("1", "2", "3", "empilhado")
TOL = 1e-6

CONTRASTE = {
    "E6": "pacote do corte (RDD em nível): bolsa anunciada + outras regras federais nos mesmos cortes",
    "E7": "DiRD: bolsa + variação, entre pré e pós, das descontinuidades das co-políticas",
    "E9": "degrau da bolsa na escolha da 1a opção entre células do mesmo curso e ciclo (realocação, "
          "condicional a candidatar-se; não é total de candidatos)",
}

# Literatura: trecho literal do doc 20 da seção 03; o número sai do trecho pela regex (nada digitado).
# `fator` converte a escala do trecho para a escala da linha (p.p. -> fração; % -> fração; por 100 mil -> por 10 mil).
LIT = (
    {"id": "A2_aceitacao", "estudo": "Dal Bó, Finan & Rossi (2013)", "trecho": "aceitação +15,1 p.p.",
     "regex": r"\+(\d+,\d+) p\.p\.", "fator": "pp", "aplica": "preenchimento", "escala": "fracao (absoluta)",
     "nota": "aceitação da oferta com salário anunciado sorteado (+33%); servidores públicos, México; "
             "outcome e população diferentes (doc 44, §6)"},
    {"id": "A1_preenchimento", "estudo": "Bobba et al. (NBER 2021, rev. 2026)",
     "trecho": "preenchimento (0,063, EP 0,048)", "regex": r"\((\d+,\d+), EP", "fator": "unidade",
     "aplica": "preenchimento", "escala": "fracao (absoluta)",
     "nota": "estimativa pontual NÃO significativa na fonte; adicional de +13% por regra (RDD), professores, Peru"},
    {"id": "A2_candidaturas", "estudo": "Dal Bó, Finan & Rossi (2013)", "trecho": "candidaturas **+26%**",
     "regex": r"\+(\d+)%", "fator": "pct", "aplica": "candidaturas", "escala": "relativa",
     "nota": "tamanho do pool de candidatos com +33% de salário; aqui, candidatos de 1a opção por célula"},
    {"id": "C2_liquido_pmm", "estudo": "Hone et al. (2020)",
     "trecho": "**+15,1** médicos do programa por 100 mil habitantes, mas **líquido de só +5,7**",
     "regex": r"líquido de só \+(\d+,\d+)", "fator": "por_100mil_para_10mil", "aplica": "oferta_cnes",
     "escala": "por 10 mil hab. (absoluta)",
     "nota": "efeito líquido do Mais Médicos inteiro (2013) sobre médicos de APS em tempo integral; só ordem de "
             "grandeza: programa inteiro, generalistas e outra medida (aqui, vínculos de especialistas)"},
    {"id": "A2_elasticidade", "estudo": "Dal Bó, Finan & Rossi (2013)", "trecho": "elasticidade ≈ 2;",
     "regex": r"≈ (\d+(?:,\d+)?)", "fator": "unidade", "aplica": "elasticidade_escolha", "escala": "elasticidade",
     "nota": "elasticidade-arco da oferta de candidatos ao salário (pool), não da repartição entre vagas"},
    {"id": "C1_elasticidade", "estudo": "Costa, Nunes & Sanches (2024)", "trecho": "elasticidade 0,4–0,7",
     "regex": r"(\d+,\d+)–(\d+,\d+)", "fator": "unidade", "aplica": "elasticidade_escolha", "escala": "elasticidade",
     "nota": "elasticidade-salário da escolha locacional de médicos no Brasil (logit estrutural); a mais próxima "
             "do E9, mas para o salário total, não um degrau de bolsa"},
)


# ---------------------------------------------------------------------------
# Utilitários
# ---------------------------------------------------------------------------

class FalhaFechada(RuntimeError):
    """Uma validação não passou; a saída não é gravada."""


def exigir(cond: bool, msg: str) -> None:
    if not cond:
        raise FalhaFechada(msg)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for bloco in iter(lambda: fh.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def rotulo(path: Path) -> str:
    p = Path(path).resolve()
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


def f(v) -> float:
    return float("nan") if v is None or (not isinstance(v, str) and pd.isna(v)) else float(v)


def fin(v) -> bool:
    return v is not None and isinstance(v, (int, float)) and math.isfinite(float(v))


def ler_csv(path: Path) -> pd.DataFrame:
    exigir(path.exists(), f"entrada ausente: {rotulo(path)}")
    d = pd.read_csv(path, dtype={"corte": str, "ciclo": str})
    exigir("natureza_dos_dados" in d.columns, f"{rotulo(path)} sem natureza_dos_dados")
    exigir(set(d["natureza_dos_dados"].unique()) == {"EMPIRICO"}, f"{rotulo(path)} tem linha nao EMPIRICO")
    return d


def ler_json(path: Path) -> dict:
    exigir(path.exists(), f"entrada ausente: {rotulo(path)}")
    d = json.loads(path.read_text(encoding="utf-8"))
    exigir(d.get("natureza_dos_dados") == "EMPIRICO", f"{rotulo(path)} nao e EMPIRICO")
    return d


# ---------------------------------------------------------------------------
# Fórmulas (testadas com números sintéticos em tests/test_x6_poder.py)
# ---------------------------------------------------------------------------

def mde(ep: float) -> float:
    """Efeito mínimo detectável com 80% de poder e teste bicaudal a 5%: 2,8 × EP."""
    return FATOR_MDE * ep


def ic90(tau: float, ep: float) -> tuple[float, float]:
    return tau - Z90 * ep, tau + Z90 * ep


def delta_tost(tau: float, ep: float) -> float:
    """Menor δ com o IC 90% dentro de [−δ, +δ] (TOST a 5%): |τ| + z₀,₉₅ × EP."""
    a, b = ic90(tau, ep)
    return max(abs(a), abs(b))


def p_tost(tau: float, ep: float, delta: float) -> float:
    """p do TOST pela normal: o maior dos dois p unilaterais (H0: θ ≤ −δ; H0: θ ≥ +δ)."""
    nd = NormalDist()
    p_inf = 1.0 - nd.cdf((tau + delta) / ep)
    p_sup = nd.cdf((tau - delta) / ep)
    return max(p_inf, p_sup)


def poder_bicaudal(efeito: float, ep: float) -> float:
    nd = NormalDist()
    z = efeito / ep
    return nd.cdf(z - Z95) + nd.cdf(-z - Z95)


def base_empilhada(pesos: dict[str, float], bases: dict[str, float]) -> float:
    """Σ ω_g m_g com os pesos do estimando empilhado; NaN se algum grupo não tem base."""
    exigir(abs(sum(pesos.values()) - 1.0) < 1e-6, f"pesos_grupos nao somam 1: {pesos}")
    vals = [bases.get(g, float("nan")) for g in pesos]
    if not all(math.isfinite(v) for v in vals):
        return float("nan")
    return float(sum(w * v for w, v in zip(pesos.values(), vals)))


def posicao(inf: float, sup: float, v_inf: float, v_sup: float) -> str:
    """Onde a referência [v_inf, v_sup] fica em relação ao intervalo [inf, sup]."""
    if not (fin(inf) and fin(sup)):
        return "NAO_AVALIAVEL"
    if sup < v_inf:
        return "IC_ABAIXO_DA_REFERENCIA"
    if inf > v_sup:
        return "IC_ACIMA_DA_REFERENCIA"
    return "IC_CONTEM_REFERENCIA"


def num_br(txt: str) -> float:
    return float(txt.replace(",", "."))


# ---------------------------------------------------------------------------
# Literatura
# ---------------------------------------------------------------------------

def literatura() -> dict[str, dict]:
    texto = LITERATURA.read_text(encoding="utf-8")
    out = {}
    for item in LIT:
        exigir(texto.count(item["trecho"]) >= 1, f"literatura: trecho ausente no doc 20: {item['trecho']!r}")
        m = re.search(item["regex"], item["trecho"])
        exigir(m is not None, f"literatura: regex nao casa no trecho {item['trecho']!r}")
        brutos = [num_br(g) for g in m.groups()]
        if item["fator"] == "pp" or item["fator"] == "pct":
            fator = 1 / 100
        elif item["fator"] == "por_100mil_para_10mil":
            mm = re.search(r"por (\d+) mil habitantes", item["trecho"])
            exigir(mm is not None, "literatura: unidade 'por N mil habitantes' ausente no trecho C2")
            fator = 10 / float(mm.group(1))            # por N mil -> por 10 mil
        else:
            fator = 1.0
        v = [x * fator for x in brutos]
        out[item["id"]] = {**{k: item[k] for k in ("id", "estudo", "trecho", "regex", "aplica", "escala", "nota")},
                           "fonte": rotulo(LITERATURA), "valores_no_trecho": brutos, "fator_escala": fator,
                           "valor_inf": min(v), "valor_sup": max(v)}
    return out


def lit_aplicaveis(lit: dict, aplica: str) -> list[dict]:
    return [x for x in lit.values() if x["aplica"] == aplica]


# ---------------------------------------------------------------------------
# Leitura das linhas
# ---------------------------------------------------------------------------

def conferir_ic95(df: pd.DataFrame, nome: str, col_tau="tau", col_ep="ep") -> None:
    z_sup = (df["ic95_sup"] - df[col_tau]) / df[col_ep]
    z_inf = (df[col_tau] - df["ic95_inf"]) / df[col_ep]
    exigir(bool(np.allclose(z_sup, Z95, atol=1e-6) and np.allclose(z_inf, Z95, atol=1e-6)),
           f"{nome}: IC 95% nao e tau +- 1,96 x EP; o MDE de 2,8 x EP nao seria da mesma inferencia")


def conferir_honesto(df: pd.DataFrame, todos: pd.DataFrame, chaves: list[str], nome: str) -> None:
    hon = todos[(todos["especificacao"] == "ic_honesto") & np.isclose(todos["fator_M"].astype(float), 1.0)]
    m = df.merge(hon, on=chaves, how="left", suffixes=("", "_h"), validate="one_to_one")
    ok = np.allclose(m["ic_honesto_inf"], m["ic_honesto_inf_h"], equal_nan=True) and \
        np.allclose(m["ic_honesto_sup"], m["ic_honesto_sup_h"], equal_nan=True)
    exigir(bool(ok), f"{nome}: IC honesto da linha principal difere da linha ic_honesto (fator 1)")


def bases_e6(e6p: pd.DataFrame) -> dict[tuple, float]:
    """Média bruta abaixo do corte das linhas por grupo (um ciclo, um corte)."""
    out = {}
    for _, r in e6p.iterrows():
        if r["corte"] != EMPILHADO and "+" not in str(r["ciclo"]):
            out[(r["outcome"], r["populacao"], r["ciclo"], r["corte"])] = f(r["media_bruta_abaixo"])
    return out


def base_relativa_e6(r: pd.Series, bases: dict[tuple, float]) -> tuple[float, str]:
    if r["familia"] == "P1":
        return float("nan"), ("NAO_SE_APLICA: indice padronizado pelo lado abaixo do corte (media ~0 por construcao); "
                              "a escala ja e relativa (DP)")
    if fin(f(r["media_bruta_abaixo"])):
        return f(r["media_bruta_abaixo"]), "media_bruta_abaixo (linha; janela h, lado de bolsa menor)"
    exigir(isinstance(r["pesos_grupos"], str), f"E6 {r['outcome']} {r['populacao']} {r['corte']}: sem base nem pesos")
    pesos = json.loads(r["pesos_grupos"])
    grupos = {}
    for g in pesos:
        if g in ("300", "400"):
            grupos[g] = (r["outcome"], r["populacao"], r["ciclo"], f"0.{g}")
        else:
            mm = re.fullmatch(r"c(\d)(?:_(\d{3}))?", g)
            exigir(mm is not None, f"E6: grupo de empilhamento inesperado {g}")
            corte = f"0.{mm.group(2)}" if mm.group(2) else r["corte"]
            grupos[g] = (r["outcome"], f"V{mm.group(1)}", mm.group(1), corte)
    b = base_empilhada(pesos, {g: bases.get(k, float("nan")) for g, k in grupos.items()})
    if not math.isfinite(b):
        return b, "INDISPONIVEL: algum grupo do empilhamento sem media_bruta_abaixo"
    return b, "media das media_bruta_abaixo dos grupos ponderada por pesos_grupos (estimando empilhado)"


def bases_e7(e7: pd.DataFrame) -> dict[tuple, float]:
    pre = e7[(e7["especificacao"] == "nivel_pre") & (e7["corte"] != EMPILHADO)]
    return {(r["outcome_id"], r["populacao"], r["corte"]): f(r["media_bruta_abaixo"]) for _, r in pre.iterrows()}


def base_relativa_e7(r: pd.Series, bases: dict[tuple, float]) -> tuple[float, str]:
    if r["corte"] != EMPILHADO:
        b = bases.get((r["outcome_id"], r["populacao"], r["corte"]), float("nan"))
        tipo = "media bruta do pre principal abaixo do corte (linha nivel_pre)"
    else:
        pesos = json.loads(r["pesos_grupos"])
        b = base_empilhada(pesos, {g: bases.get((r["outcome_id"], r["populacao"], f"0.{g}"), float("nan"))
                                   for g in pesos})
        tipo = "media bruta do pre abaixo do corte (nivel_pre) dos cortes, ponderada por pesos_grupos"
    if not math.isfinite(b):
        return b, "INDISPONIVEL: sem linha nivel_pre com media_bruta_abaixo"
    return b, tipo


# ---------------------------------------------------------------------------
# Montagem de uma linha
# ---------------------------------------------------------------------------

def _rel(v: float, base: float) -> float:
    return v / base if fin(v) and fin(base) and base > 0 else float("nan")


def linha(meta: dict, tau: float, ep: float, ic95: tuple[float, float], p: float,
          hon: tuple[float, float], base: float, base_tipo: str, escala_rel: str,
          ref: dict | None, lits: list[dict], col_lit: str, eh_fracao: bool) -> dict:
    """escala_rel: 'base' (divide pela base), 'log' (exp(.) - 1), 'ja_relativa' (copia) ou 'nenhuma'."""
    m80 = mde(ep)
    a90, b90 = ic90(tau, ep)
    dl = delta_tost(tau, ep)
    hi, hs = hon
    out = {**meta, "tau": tau, "ep": ep, "ic95_inf": ic95[0], "ic95_sup": ic95[1], "p_valor": p,
           "mde80": m80, "ic90_inf": a90, "ic90_sup": b90, "delta_tost": dl,
           "ic_honesto_inf": hi, "ic_honesto_sup": hs,
           "ic_honesto_contem_zero": (bool(hi <= 0 <= hs) if fin(hi) and fin(hs) else None),
           "ic_honesto_cobre_todo_salto_possivel": (bool(hi <= -1 and hs >= 1) if eh_fracao and fin(hi) and fin(hs)
                                                    else None),
           "base_relativa": base, "base_relativa_tipo": base_tipo, "escala_relativa": escala_rel}
    if escala_rel == "base":
        rel = {"mde80_rel": _rel(m80, base), "ic95_inf_rel": _rel(ic95[0], base), "ic95_sup_rel": _rel(ic95[1], base),
               "tau_rel": _rel(tau, base), "delta_tost_rel": _rel(dl, base), "ic_honesto_inf_rel": _rel(hi, base),
               "ic_honesto_sup_rel": _rel(hs, base)}
    elif escala_rel == "log":
        ex = lambda v: math.exp(v) - 1 if fin(v) else float("nan")  # noqa: E731
        rel = {"mde80_rel": ex(m80), "ic95_inf_rel": ex(ic95[0]), "ic95_sup_rel": ex(ic95[1]), "tau_rel": ex(tau),
               "delta_tost_rel": ex(dl), "ic_honesto_inf_rel": ex(hi), "ic_honesto_sup_rel": ex(hs)}
    elif escala_rel == "ja_relativa":
        rel = {"mde80_rel": m80, "ic95_inf_rel": ic95[0], "ic95_sup_rel": ic95[1], "tau_rel": tau,
               "delta_tost_rel": dl, "ic_honesto_inf_rel": hi, "ic_honesto_sup_rel": hs}
    else:
        rel = {k: float("nan") for k in ("mde80_rel", "ic95_inf_rel", "ic95_sup_rel", "tau_rel", "delta_tost_rel",
                                          "ic_honesto_inf_rel", "ic_honesto_sup_rel")}
    out.update(rel)

    def cols(escala: str) -> tuple[float, float, float, float, float, float]:
        if escala == "rel":
            return (out["ic95_inf_rel"], out["ic95_sup_rel"], out["mde80_rel"], out["delta_tost_rel"],
                    out["ic_honesto_inf_rel"], out["ic_honesto_sup_rel"])
        return ic95[0], ic95[1], m80, dl, hi, hs

    informativo, criterios = None, []
    if ref is not None:
        i95, s95, mm, dd, h_i, h_s = cols(ref["coluna"])
        v = ref["valor"]
        out.update({"ref_protocolo": ref["nome"], "ref_protocolo_valor": v, "ref_protocolo_escala": ref["escala"],
                    "ic95_exclui_ref_protocolo": (bool(s95 < v) if fin(s95) else None),
                    "mde80_abaixo_ref_protocolo": (bool(mm < v) if fin(mm) else None),
                    "tost_dentro_ref_protocolo": (bool(dd < v) if fin(dd) else None),
                    "ic_honesto_exclui_ref_protocolo": (bool(h_s < v) if fin(h_s) else None)})
        if fin(h_s):
            criterios.append(("ref_protocolo", bool(h_s < v)))
    else:
        out.update({"ref_protocolo": "NAO_SE_APLICA", "ref_protocolo_valor": float("nan"), "ref_protocolo_escala": "",
                    "ic95_exclui_ref_protocolo": None, "mde80_abaixo_ref_protocolo": None,
                    "tost_dentro_ref_protocolo": None, "ic_honesto_exclui_ref_protocolo": None})
    for k in (1, 2):
        x = lits[k - 1] if len(lits) >= k else None
        if x is None:
            out.update({f"lit{k}_id": "", f"lit{k}_valor_inf": float("nan"), f"lit{k}_valor_sup": float("nan"),
                        f"lit{k}_escala": "", f"lit{k}_posicao_ic95": "", f"lit{k}_mde80_abaixo": None,
                        f"lit{k}_tost_dentro": None, f"lit{k}_posicao_ic_honesto": ""})
            continue
        i95, s95, mm, dd, h_i, h_s = cols(col_lit)
        vi, vs = x["valor_inf"], x["valor_sup"]
        alvo = min(abs(vi), abs(vs))
        out.update({f"lit{k}_id": x["id"], f"lit{k}_valor_inf": vi, f"lit{k}_valor_sup": vs,
                    f"lit{k}_escala": x["escala"], f"lit{k}_posicao_ic95": posicao(i95, s95, vi, vs),
                    f"lit{k}_mde80_abaixo": (bool(mm < alvo) if fin(mm) else None),
                    f"lit{k}_tost_dentro": (bool(dd < alvo) if fin(dd) else None),
                    f"lit{k}_posicao_ic_honesto": posicao(h_i, h_s, vi, vs) if fin(h_i) else "NAO_SE_APLICA"})
        if fin(h_i) and fin(h_s):
            criterios.append((x["id"], posicao(h_i, h_s, vi, vs) != "IC_CONTEM_REFERENCIA"))
    bh_i, bh_s = out["ic_honesto_inf_rel"], out["ic_honesto_sup_rel"]
    if escala_rel == "base" and fin(bh_i) and fin(bh_s):
        criterios.append(("dentro_de_mais_menos_100pct_da_base", bool(bh_i > -1 and bh_s < 1)))
    if fin(hi) and fin(hs):
        informativo = bool(any(v for _, v in criterios)) if criterios else None
    out["ic_honesto_informativo"] = informativo
    out["ic_honesto_criterios"] = "; ".join(f"{n}={'sim' if v else 'nao'}" for n, v in criterios) if criterios else (
        "NAO_SE_APLICA: sem IC honesto" if not (fin(hi) and fin(hs)) else "NAO_AVALIAVEL: sem referencia nem base")
    return out


def _meta(etapa: str, r: dict, **kw) -> dict:
    return {"natureza_dos_dados": "EMPIRICO", "estatuto": ESTATUTO, "etapa_origem": etapa,
            "contraste": CONTRASTE[etapa], **r, **kw}


# ---------------------------------------------------------------------------
# E6, E7, E9
# ---------------------------------------------------------------------------

def linhas_e6(e6: pd.DataFrame, lit: dict) -> list[dict]:
    princ = e6[(e6["especificacao"] == "principal") & e6["familia"].isin(FAMILIAS_E6)].copy()
    pois = e6[(e6["especificacao"] == "poisson_local") & (e6["outcome_id"] == "F1.1")].copy()
    exigir(len(princ) > 0 and len(pois) > 0, "E6: linhas principais ou Poisson de F1.1 ausentes")
    conferir_ic95(princ, "E6 principal")
    conferir_ic95(pois, "E6 poisson_local F1.1")
    conferir_honesto(princ, e6, ["familia", "outcome", "populacao", "ciclo", "corte"], "E6")
    exigir(bool(np.allclose(np.exp(pois["ic95_sup"]) - 1, pois["efeito_relativo_ic95_sup"], atol=1e-9)),
           "E6 Poisson: efeito_relativo_ic95_sup != exp(ic95_sup) - 1")
    bases = bases_e6(e6[e6["especificacao"] == "principal"])
    out = []
    for _, r in pd.concat([princ, pois]).iterrows():
        eh_pois = r["especificacao"] == "poisson_local"
        oid = r["outcome_id"]
        meta = _meta("E6", {
            "familia": r["familia"], "outcome_id": oid, "outcome": r["outcome"],
            "descricao_outcome": r["descricao_outcome"], "populacao": r["populacao"], "ciclo": r["ciclo"],
            "corte": r["corte"], "especificacao": r["especificacao"], "estimador": r["estimador"],
            "no_protocolo": bool(r["no_protocolo"]), "h": f(r["h"]), "n_obs": f(r["n_obs"]),
            "escala": "log (Poisson local)" if eh_pois else "absoluta",
            "unidade": "log da razao de taxas" if eh_pois else r["unidade"],
            "quantidade": "salto"})
        if eh_pois:
            base, btipo, esc = float("nan"), "NAO_SE_APLICA: escala log (relativo = exp(.) - 1)", "log"
        else:
            base, btipo = base_relativa_e6(r, bases)
            esc = "base" if math.isfinite(base) else "nenhuma"
        ref, lits, col = None, [], "abs"
        if oid in ("F1.3", "F1.4") and not eh_pois:
            ref = {"nome": "preenchimento +10 p.p. (protocolo 40, §7)", "valor": REF_PREENCHIMENTO,
                   "escala": "fracao (absoluta)", "coluna": "abs"}
            lits, col = lit_aplicaveis(lit, "preenchimento"), "abs"
        elif oid == "F1.1":
            ref = {"nome": "candidaturas +25% (protocolo 40, §7)", "valor": REF_CANDIDATURAS, "escala": "relativa",
                   "coluna": "rel"}
            lits, col = lit_aplicaveis(lit, "candidaturas"), "rel"
        out.append(linha(meta, f(r["tau"]), f(r["ep"]), (f(r["ic95_inf"]), f(r["ic95_sup"])), f(r["p_valor"]),
                         (f(r["ic_honesto_inf"]), f(r["ic_honesto_sup"])), base, btipo, esc, ref, lits, col,
                         eh_fracao=(not eh_pois and str(r["unidade"]).startswith("fracao"))))
        if not eh_pois:
            out[-1]["nota"] = ("ESPECIFICACAO_ADICIONAL_AO_PROTOCOLO" if not bool(r["no_protocolo"]) else "")
        else:
            out[-1]["nota"] = "Poisson local por ciclo e corte; nao ha versao empilhada (doc 44, §5.1)"
    return out


def linhas_e7(e7: pd.DataFrame, lit: dict) -> list[dict]:
    princ = e7[(e7["especificacao"] == "principal") & e7["outcome_id"].isin(OUTCOMES_E7)].copy()
    exigir(len(princ) == len(OUTCOMES_E7) * 3 + 3, f"E7: esperadas {len(OUTCOMES_E7) * 3 + 3} linhas, achadas {len(princ)}")
    conferir_ic95(princ, "E7 principal")
    conferir_honesto(princ, e7, ["outcome_id", "populacao", "corte"], "E7")
    bases = bases_e7(e7)
    out = []
    for _, r in princ.iterrows():
        meta = _meta("E7", {
            "familia": r["familia"], "outcome_id": r["outcome_id"], "outcome": r["outcome"],
            "descricao_outcome": r["descricao_outcome"], "populacao": r["populacao"], "ciclo": "pos 2025-10..2026-08",
            "corte": r["corte"], "especificacao": r["especificacao"], "estimador": r["estimador"],
            "no_protocolo": bool(r["no_protocolo"]), "h": f(r["h"]), "n_obs": f(r["n_obs"]), "escala": "absoluta",
            "unidade": r["unidade"], "quantidade": "DiRD (salto da variacao pos - pre)"})
        base, btipo = base_relativa_e7(r, bases)
        lits = lit_aplicaveis(lit, "oferta_cnes") if r["outcome_id"] == "F3.1" else []
        out.append(linha(meta, f(r["tau"]), f(r["ep"]), (f(r["ic95_inf"]), f(r["ic95_sup"])), f(r["p_valor"]),
                         (f(r["ic_honesto_inf"]), f(r["ic_honesto_sup"])), base, btipo,
                         "base" if math.isfinite(base) else "nenhuma", None, lits, "abs",
                         eh_fracao=str(r["unidade"]).startswith("fracao")))
        out[-1]["nota"] = str(r["papel"])
    return out


def linhas_e9(e9: pd.DataFrame, efm: pd.DataFrame, degrau: dict, lit: dict) -> list[dict]:
    base = e9[(e9["modelo"] == COND) & (e9["conjunto"] == "principal") & (e9["termo"] == "bolsa_mil")
              & (e9["especificacao"] == PRINCIPAL_E9)]
    q = efm[(efm["modelo"] == COND) & (efm["conjunto"] == "principal") & (efm["termo"] == "bolsa_mil")
            & (efm["especificacao"] == PRINCIPAL_E9)]
    out = []
    sem_hon = (float("nan"), float("nan"))
    nota_e9 = "E9 nao tem IC honesto; inferencia com EP cluster por conjunto (doc 42; robustez no doc 44, §5.2)"
    for cic in CICLOS_E9:
        rs = base[base["ciclo"] == cic]
        exigir(len(rs) == 1, f"E9 ciclo {cic}: esperada 1 linha principal, achadas {len(rs)}")
        r = rs.iloc[0]
        qq = q[q["ciclo"] == cic].set_index("quantidade")
        for k in ("log_razao_chances_por_5mil", "razao_chances_por_5mil", "variacao_prob_media_pp",
                  "prob_media_base_pp", "variacao_relativa_media"):
            exigir(k in qq.index, f"E9 ciclo {cic}: quantidade {k} ausente")
        comum = {"familia": "E9", "outcome_id": "E9", "outcome": "escolha da 1a opcao (logit condicional)",
                 "descricao_outcome": "coeficiente da bolsa anunciada (R$ mil) na utilidade da celula",
                 "populacao": "candidatos de 1a opcao", "ciclo": cic, "corte": "spline continuo (nos em 0,300 e 0,400)",
                 "especificacao": PRINCIPAL_E9, "estimador": "logit condicional, EP cluster por conjunto",
                 "no_protocolo": bool(r["no_protocolo"]), "h": float("nan"), "n_obs": f(r["n_candidatos"])}
        # (a) coeficiente por R$ mil
        rr = pd.DataFrame([{"tau": f(r["coef"]), "ep": f(r["ep_cluster_conjunto"]), "ic95_inf": f(r["ic95_inf"]),
                            "ic95_sup": f(r["ic95_sup"])}])
        conferir_ic95(rr, f"E9 {cic} coef")
        out.append(linha(_meta("E9", comum, escala="coeficiente", unidade="log-utilidade por R$ mil",
                               quantidade="coef_por_mil"),
                         f(r["coef"]), f(r["ep_cluster_conjunto"]), (f(r["ic95_inf"]), f(r["ic95_sup"])), f(r["p"]),
                         sem_hon, float("nan"), "NAO_SE_APLICA", "nenhuma", None, [], "abs", False))
        # (b) log da razão de chances por +R$ 5 mil
        lo = qq.loc["log_razao_chances_por_5mil"]
        rr = pd.DataFrame([{"tau": f(lo["estimativa"]), "ep": f(lo["ep_cluster_conjunto"]),
                            "ic95_inf": f(lo["ic95_inf"]), "ic95_sup": f(lo["ic95_sup"])}])
        conferir_ic95(rr, f"E9 {cic} log RC")
        exigir(abs(f(lo["estimativa"]) - 5 * f(r["coef"])) < TOL, f"E9 {cic}: log RC != 5 x coef")
        out.append(linha(_meta("E9", comum, escala="log razao de chances", unidade="log RC por +R$ 5 mil",
                               quantidade="log_razao_chances_por_5mil"),
                         f(lo["estimativa"]), f(lo["ep_cluster_conjunto"]), (f(lo["ic95_inf"]), f(lo["ic95_sup"])),
                         f(r["p"]), sem_hon, float("nan"), "NAO_SE_APLICA", "nenhuma", None, [], "abs", False))
        # (c) razão de chances: MDE, IC 90% e δ do TOST são exp dos valores em log
        rc = qq.loc["razao_chances_por_5mil"]
        ep_log = f(lo["ep_cluster_conjunto"])
        tau_log = f(lo["estimativa"])
        exigir(abs(math.exp(f(lo["ic95_sup"])) - f(rc["ic95_sup"])) < 1e-6, f"E9 {cic}: IC da RC != exp(IC do log)")
        d_log = delta_tost(tau_log, ep_log)
        a90, b90 = ic90(tau_log, ep_log)
        out.append({**_meta("E9", comum, escala="razao de chances", unidade="razao de chances por +R$ 5 mil",
                            quantidade="razao_chances_por_5mil"),
                    "tau": f(rc["estimativa"]), "ep": f(rc["ep_cluster_conjunto"]), "ic95_inf": f(rc["ic95_inf"]),
                    "ic95_sup": f(rc["ic95_sup"]), "p_valor": f(r["p"]), "mde80": math.exp(mde(ep_log)),
                    "ic90_inf": math.exp(a90), "ic90_sup": math.exp(b90), "delta_tost": math.exp(d_log),
                    "ic_honesto_inf": float("nan"), "ic_honesto_sup": float("nan"), "ic_honesto_contem_zero": None,
                    "ic_honesto_cobre_todo_salto_possivel": None, "base_relativa": float("nan"),
                    "base_relativa_tipo": "NAO_SE_APLICA: razao de chances (MDE e delta_tost sao exp dos valores em "
                                          "log; equivalencia em [1/delta, delta])",
                    "escala_relativa": "nenhuma", "ref_protocolo": "NAO_COMPARAVEL: reparticao de um pool dado, nao "
                                                                   "tamanho do pool (doc 44, §5.2)",
                    "ic_honesto_informativo": None, "ic_honesto_criterios": "NAO_SE_APLICA: sem IC honesto"})
        # (d) variação média da probabilidade (p.p.) relativa à probabilidade-base
        dp, pb = qq.loc["variacao_prob_media_pp"], qq.loc["prob_media_base_pp"]
        rr = pd.DataFrame([{"tau": f(dp["estimativa"]), "ep": f(dp["ep_cluster_conjunto"]),
                            "ic95_inf": f(dp["ic95_inf"]), "ic95_sup": f(dp["ic95_sup"])}])
        conferir_ic95(rr, f"E9 {cic} delta prob")
        out.append(linha(_meta("E9", comum, escala="absoluta", unidade="p.p. de probabilidade de escolha",
                               quantidade="variacao_prob_media_pp"),
                         f(dp["estimativa"]), f(dp["ep_cluster_conjunto"]), (f(dp["ic95_inf"]), f(dp["ic95_sup"])),
                         f(r["p"]), sem_hon, f(pb["estimativa"]),
                         "prob_media_base_pp (media de 1/(celulas do conjunto); referencia sem incerteza)", "base",
                         None, [], "abs", False))
        # (e) variação relativa média e (f) elasticidade-arco implícita em cada corte
        vr = qq.loc["variacao_relativa_media"]
        rr = pd.DataFrame([{"tau": f(vr["estimativa"]), "ep": f(vr["ep_cluster_conjunto"]),
                            "ic95_inf": f(vr["ic95_inf"]), "ic95_sup": f(vr["ic95_sup"])}])
        conferir_ic95(rr, f"E9 {cic} variacao relativa")
        out.append(linha(_meta("E9", comum, escala="relativa", unidade="variacao relativa da probabilidade",
                               quantidade="variacao_relativa_media"),
                         f(vr["estimativa"]), f(vr["ep_cluster_conjunto"]), (f(vr["ic95_inf"]), f(vr["ic95_sup"])),
                         f(r["p"]), sem_hon, float("nan"), "NAO_SE_APLICA: ja relativa", "ja_relativa", None, [],
                         "abs", False))
        for corte in ("0.300", "0.400"):
            g = float(degrau[corte]["relativo"])
            out.append(linha(_meta("E9", comum, escala="elasticidade", unidade="elasticidade-arco da escolha",
                                   quantidade=f"elasticidade_implicita_degrau_{corte}"),
                             f(vr["estimativa"]) / g, f(vr["ep_cluster_conjunto"]) / g,
                             (f(vr["ic95_inf"]) / g, f(vr["ic95_sup"]) / g), f(r["p"]), sem_hon, float("nan"),
                             "NAO_SE_APLICA: elasticidade", "nenhuma", None,
                             lit_aplicaveis(lit, "elasticidade_escolha"), "abs", False))
            out[-1]["nota"] = (f"variacao_relativa_media / degrau relativo da bolsa no corte {corte} "
                               f"(E8_resumo.degrau_relativo_bolsa); aritmetica, nao estimacao nova")
        for x in out[-7:]:
            if not x.get("nota"):
                x["nota"] = nota_e9
    for x in out:
        x["ref_protocolo"] = "NAO_COMPARAVEL: reparticao de um pool dado, nao tamanho do pool (doc 44, §5.2)"
    return out


# ---------------------------------------------------------------------------
# Construção
# ---------------------------------------------------------------------------

ENTRADAS = [
    (E6_EST, "E6: linhas principais de P1, F0-F4 e Poisson local de F1.1", "13_estimar_E6_funil.py", "2026-10-18",
     "U, G3, V1-V3; ciclos 1-3", "linha de especificacao", "familia, outcome, populacao, ciclo, corte, especificacao",
     "especificacao in (principal, poisson_local [so F1.1], ic_honesto [fator_M = 1, conferencia]); familia in "
     "(P1, F0, F1, F2, F4)"),
    (E7_EST, "E7: DiRD principal da familia F3 e bases do pre (nivel_pre)", "14_estimar_E7_dird_cnes.py", "2026-10-19",
     "U (5565 municipios) e V1; pre 2024-06..2025-06, pos 2025-10..2026-08", "linha de especificacao",
     "outcome_id, populacao, corte, especificacao",
     "especificacao in (principal, nivel_pre, ic_honesto [fator_M = 1]); outcome_id in (F3.1, F3.2, F3.3, F3.P1, F3.P2)"),
    (E9_EST, "E9: coeficiente da bolsa, modelo principal", "16_estimar_E9_escolha.py", "2026-10-18",
     "ciclos 1, 2, 3 e empilhado", "ciclo x modelo x conjunto x especificacao x termo",
     "ciclo, modelo, conjunto, especificacao, termo",
     "modelo = logit_condicional_1a_opcao; conjunto = principal; especificacao = spline_linear__bolsa_linear; "
     "termo = bolsa_mil"),
    (E9_EFM, "E9: razao de chances e efeitos na probabilidade por +R$ 5 mil", "16_estimar_E9_escolha.py",
     "2026-10-18", "ciclos 1, 2, 3 e empilhado", "ciclo x modelo x conjunto x especificacao x quantidade",
     "ciclo, modelo, conjunto, especificacao, termo, quantidade", "mesmos filtros do E9; termo = bolsa_mil"),
    (E8_RESUMO, "E8: degrau relativo da bolsa por corte (grades dos editais)", "15_sintese_E8.py", "2026-10-19",
     "cortes 0,300 e 0,400", "corte", "corte", "degrau_relativo_bolsa"),
    (LITERATURA, "magnitudes da literatura (texto, nao resultado)", "docs/03_literatura_empirica/20", "2026-10-05",
     "tabela-resumo e fichas A1, A2, C1, C2", "trecho literal", "id do estudo", "trechos em LIT"),
    (PROTOCOLO_X, "protocolo exploratorio pos-sintese (X6)", "doc 45", "2026-10-19", "§3 X6", "documento", "-", "-"),
    (PROTOCOLO_40, "protocolo 40 (referencias +10 p.p. e +25%, §7)", "doc 40", "2026-10-18", "§7", "documento", "-",
     "-"),
]


def bloco_entradas() -> list[dict]:
    out = []
    for path, papel, fonte, data_ref, cobertura, unidade, chaves, filtros in ENTRADAS:
        exigir(path.exists(), f"entrada ausente: {rotulo(path)}")
        out.append({"caminho": rotulo(path), "sha256": sha256(path), "bytes": path.stat().st_size, "papel": papel,
                    "fonte": fonte, "data_referencia": data_ref, "cobertura": cobertura, "unidade": unidade,
                    "chaves": chaves, "filtros": filtros})
    return out


COLUNAS = [
    "natureza_dos_dados", "estatuto", "etapa_origem", "contraste", "familia", "outcome_id", "outcome",
    "descricao_outcome", "populacao", "ciclo", "corte", "especificacao", "estimador", "no_protocolo", "quantidade",
    "escala", "unidade", "h", "n_obs", "tau", "ep", "ic95_inf", "ic95_sup", "p_valor", "mde80", "ic90_inf",
    "ic90_sup", "delta_tost", "ic_honesto_inf", "ic_honesto_sup", "ic_honesto_contem_zero",
    "ic_honesto_cobre_todo_salto_possivel", "base_relativa", "base_relativa_tipo", "escala_relativa", "tau_rel",
    "mde80_rel", "ic95_inf_rel", "ic95_sup_rel", "delta_tost_rel", "ic_honesto_inf_rel", "ic_honesto_sup_rel",
    "ref_protocolo", "ref_protocolo_valor", "ref_protocolo_escala", "ic95_exclui_ref_protocolo",
    "mde80_abaixo_ref_protocolo", "tost_dentro_ref_protocolo", "ic_honesto_exclui_ref_protocolo",
    "lit1_id", "lit1_valor_inf", "lit1_valor_sup", "lit1_escala", "lit1_posicao_ic95", "lit1_mde80_abaixo",
    "lit1_tost_dentro", "lit1_posicao_ic_honesto", "lit2_id", "lit2_valor_inf", "lit2_valor_sup", "lit2_escala",
    "lit2_posicao_ic95", "lit2_mde80_abaixo", "lit2_tost_dentro", "lit2_posicao_ic_honesto",
    "ic_honesto_informativo", "ic_honesto_criterios", "nota",
]


def construir() -> tuple[dict, pd.DataFrame]:
    e6, e7, e9, efm = ler_csv(E6_EST), ler_csv(E7_EST), ler_csv(E9_EST), ler_csv(E9_EFM)
    r8 = ler_json(E8_RESUMO)
    degrau = r8["degrau_relativo_bolsa"]
    for c in ("0.300", "0.400"):
        exigir(c in degrau and float(degrau[c]["relativo"]) > 0, f"E8: degrau relativo do corte {c} ausente")
    lit = literatura()
    linhas = linhas_e6(e6, lit) + linhas_e7(e7, lit) + linhas_e9(e9, efm, degrau, lit)
    tab = pd.DataFrame(linhas)
    for c in COLUNAS:
        if c not in tab.columns:
            tab[c] = None
    tab = tab[COLUNAS]
    exigir(set(tab["natureza_dos_dados"]) == {"EMPIRICO"} and set(tab["estatuto"]) == {ESTATUTO}, "rotulos")
    chave = ["etapa_origem", "outcome", "populacao", "ciclo", "corte", "especificacao", "quantidade"]
    exigir(not tab.duplicated(chave).any(), "linhas duplicadas na chave do X6")

    def conta(m) -> int:
        return int(m.sum())

    com_ref = tab[tab["ref_protocolo"].astype(str).str.contains(r"\(protocolo 40", regex=True)]
    hon = tab["ic_honesto_informativo"]
    resumo = {
        "etapa": "X6_poder_descartes",
        "natureza_dos_dados": "EMPIRICO",
        "estatuto": ESTATUTO,
        "data_execucao": dt.date.today().isoformat(),
        "script": "scripts/rdd_bolsa/20_poder_descartes.py",
        "protocolo": {"texto": rotulo(PROTOCOLO_X), "sha256": sha256(PROTOCOLO_X), "secao": "§3 X6",
                      "referencias": {"texto": rotulo(PROTOCOLO_40), "sha256": sha256(PROTOCOLO_40), "secao": "§7"}},
        "regra": "nenhuma estimacao nova: so aritmetica sobre EP, IC e medias ja publicados no E6, E7, E8 e E9",
        "parametros": {"alfa": ALFA, "poder": PODER, "fator_mde": FATOR_MDE, "z95": Z95, "z90": Z90,
                       "ref_preenchimento_fracao": REF_PREENCHIMENTO, "ref_candidaturas_relativo": REF_CANDIDATURAS,
                       "poder_exato_com_fator_mde": poder_bicaudal(FATOR_MDE, 1.0)},
        "definicoes": {
            "mde80": "2,8 x EP (80% de poder, bicaudal a 5%; convencao do E5). Na razao de chances: exp(2,8 x EP do log)",
            "delta_tost": "menor margem simetrica delta com o IC 90% (tau +- z95unilateral x EP) dentro de [-delta, "
                          "+delta]; = |tau| + 1,645 x EP. Para toda margem maior, o TOST rejeita nao-equivalencia a 5%",
            "relativos": "valor / base_relativa (escala_relativa = base); exp(.) - 1 (escala_relativa = log); copia "
                         "(ja_relativa)",
            "base_relativa": "E6: media_bruta_abaixo da linha; empilhadas: medias dos grupos ponderadas por "
                             "pesos_grupos. E7: media bruta do pre abaixo do corte (nivel_pre), idem no empilhado. "
                             "E9: probabilidade-base de escolha",
            "ic95_exclui_ref_protocolo": "limite superior do IC 95% convencional abaixo da referencia",
            "mde80_abaixo_ref_protocolo": "o desenho tem ao menos 80% de poder contra a referencia",
            "tost_dentro_ref_protocolo": "equivalencia a 5% dentro de +-referencia",
            "lit_posicao_ic95": "IC_ABAIXO_DA_REFERENCIA = o IC descarta a magnitude da literatura pelo lado de cima; "
                                "IC_ACIMA = descarta pelo lado de baixo; IC_CONTEM = nao descarta",
            "ic_honesto_informativo": "True se o IC honesto (M do protocolo, fator 1) exclui a referencia do protocolo, "
                                      "ou uma magnitude da literatura aplicavel, ou fica dentro de +-100% da base; "
                                      "False se nenhuma dessas; null se nao ha IC honesto (Poisson, E9) ou nada a "
                                      "comparar",
        },
        "contraste": CONTRASTE,
        "selecao": {
            "E6": "especificacao = principal e familia in (P1, F0, F1, F2, F4); mais poisson_local de F1.1",
            "E7": "especificacao = principal e outcome_id in (F3.1, F3.2, F3.3, F3.P1, F3.P2)",
            "E9": "modelo principal, ciclos 1, 2, 3 e empilhado",
            "excluidas": "E6 S1 (suplementar PMMB); E7 S6 e sensibilidades F3.3.* (fora do BKY); E3 (ancora ja no "
                         "doc 44 com MDE do E5)",
        },
        "entradas": bloco_entradas(),
        "literatura": list(lit.values()),
        "degrau_relativo_bolsa": {c: degrau[c] for c in ("0.300", "0.400")},
        "contagens": {
            "linhas": int(len(tab)),
            "por_etapa": {k: int(v) for k, v in tab["etapa_origem"].value_counts().sort_index().items()},
            "com_referencia_do_protocolo": int(len(com_ref)),
            "ic95_exclui_ref_protocolo": conta(com_ref["ic95_exclui_ref_protocolo"] == True),  # noqa: E712
            "mde80_abaixo_ref_protocolo": conta(com_ref["mde80_abaixo_ref_protocolo"] == True),  # noqa: E712
            "tost_dentro_ref_protocolo": conta(com_ref["tost_dentro_ref_protocolo"] == True),  # noqa: E712
            "ic_honesto_exclui_ref_protocolo": conta(com_ref["ic_honesto_exclui_ref_protocolo"] == True),  # noqa: E712
            "com_ic_honesto": conta(tab["ic_honesto_inf"].notna()),
            "ic_honesto_informativo": conta(hon == True),  # noqa: E712
            "ic_honesto_nao_informativo": conta(hon == False),  # noqa: E712
            "ic_honesto_nao_avaliavel": conta(tab["ic_honesto_inf"].notna() & hon.isna()),
            "fracoes_com_ic_honesto_cobrindo_todo_salto_possivel":
                conta(tab["ic_honesto_cobre_todo_salto_possivel"] == True),  # noqa: E712
            "fracoes_com_ic_honesto": conta(tab["ic_honesto_cobre_todo_salto_possivel"].notna()),
            "bases_indisponiveis": conta(tab["base_relativa_tipo"].astype(str).str.startswith("INDISPONIVEL")),
        },
    }
    return resumo, tab


def _sem_nan(x):
    if isinstance(x, dict):
        return {k: _sem_nan(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_sem_nan(v) for v in x]
    if isinstance(x, float) and not math.isfinite(x):
        return None
    return x


def gravar(resumo: dict, tab: pd.DataFrame) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    tab.to_csv(OUT / NOME_CSV, index=False, lineterminator="\n")
    fig = gravar_figura(tab)
    resumo["saidas"] = {
        NOME_CSV: {"caminho": rotulo(OUT / NOME_CSV), "sha256": sha256(OUT / NOME_CSV), "linhas": int(len(tab))},
        NOME_FIG: {"caminho": rotulo(fig), "sha256": sha256(fig)},
    }
    (OUT / NOME_RESUMO).write_text(json.dumps(_sem_nan(resumo), ensure_ascii=False, indent=2, allow_nan=False) + "\n",
                                   encoding="utf-8")


def ler_saidas() -> tuple[dict, pd.DataFrame]:
    resumo = json.loads((OUT / NOME_RESUMO).read_text(encoding="utf-8"))
    tab = pd.read_csv(OUT / NOME_CSV, dtype={"ciclo": str, "corte": str})
    return resumo, tab


# ---------------------------------------------------------------------------
# Seleções usadas na figura e no doc (só leitura do CSV do X6)
# ---------------------------------------------------------------------------

PRINCIPAIS_EMPILHADAS = (  # (etapa, outcome_id, populacao, ciclo): linhas empilhadas que a síntese lê
    ("E6", "F1.1", "V1+V2+V3", "1+2+3"), ("E6", "F1.2", "V1+V2+V3", "1+2+3"), ("E6", "F1.3", "V1+V2+V3", "1+2+3"),
    ("E6", "F1.4", "V1+V2", "1+2"), ("E6", "F2.1", "V1+V2", "1+2"), ("E6", "F2.2", "U", "1"), ("E6", "F2.2", "U", "2"),
    ("E6", "F2.3", "V1+V2", "1+2"), ("E6", "F4.1", "V1+V2+V3", "1+2+3"), ("E6", "F4.2", "V1+V2+V3", "1+2+3"),
    ("E6", "P1", "V1+V2+V3", "1+2+3"),
    ("E7", "F3.1", "U", None), ("E7", "F3.1", "V1", None), ("E7", "F3.2", "U", None), ("E7", "F3.3", "U", None),
    ("E7", "F3.P1", "U", None), ("E7", "F3.P2", "U", None),
)
ROTULO_CURTO = {
    "F1.1": "F1.1 candidatos de 1ª opção por célula", "F1.2": "F1.2 células com candidato",
    "F1.3": "F1.3 preenchidas na 1ª chamada", "F1.4": "F1.4 preenchidas até a 2ª chamada",
    "F2.1": "F2.1 ativos por célula", "F2.2": "F2.2 ativos por 10 mil hab.", "F2.3": "F2.3 algum ativo do ciclo",
    "F4.1": "F4.1 nota dos alocados", "F4.2": "F4.2 nota dos candidatos", "P1": "P1 índice atração-presença",
    "F3.1": "F3.1 vínculos CBO-alvo / 10 mil", "F3.2": "F3.2 tem especialista CBO-alvo",
    "F3.3": "F3.3 horas SUS CBO-alvo / 10 mil", "F3.P1": "F3.P1 placebo generalistas",
    "F3.P2": "F3.P2 placebo não-alvo",
}


def sel_principais(tab: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    for et, oid, pop, cic in PRINCIPAIS_EMPILHADAS:
        m = (tab["etapa_origem"] == et) & (tab["outcome_id"] == oid) & (tab["populacao"] == pop) \
            & (tab["corte"] == EMPILHADO) & (tab["especificacao"] == "principal")
        if cic is not None:
            m &= tab["ciclo"] == cic
        s = tab[m]
        exigir(len(s) == 1, f"selecao {et} {oid} {pop} {cic}: {len(s)} linhas")
        linhas.append(s.iloc[0])
    return pd.DataFrame(linhas)


def sel_e9(tab: pd.DataFrame, quantidade: str) -> pd.DataFrame:
    s = tab[(tab["etapa_origem"] == "E9") & (tab["quantidade"] == quantidade)]
    return s.set_index("ciclo").loc[list(CICLOS_E9)].reset_index()


# ---------------------------------------------------------------------------
# Figura
# ---------------------------------------------------------------------------

def gravar_figura(tab: pd.DataFrame) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    COR, COR_REF, COR_LIT, CINZA, GRADE = "#2a78d6", "#eb6834", "#1baf7a", "#52514e", "#e6e5e0"
    LIM = 1.5  # janela do eixo relativo (±150%), só exibição; o que sai dela recebe seta
    s = sel_principais(tab)
    s = s[s["escala_relativa"] == "base"].iloc[::-1]
    e9e = tab[(tab["etapa_origem"] == "E9") & tab["quantidade"].str.startswith("elasticidade_implicita")]

    fig, (ax, bx) = plt.subplots(1, 2, figsize=(14, 7.8), gridspec_kw={"width_ratios": [1.6, 1]})
    y = np.arange(len(s))
    for yi, (_, r) in zip(y, s.iterrows()):
        a, b, t = r["ic95_inf_rel"], r["ic95_sup_rel"], r["tau_rel"]
        a90, b90 = r["ic90_inf"] / r["base_relativa"], r["ic90_sup"] / r["base_relativa"]
        ax.plot([max(a, -LIM), min(b, LIM)], [yi, yi], color=COR, lw=1.4)
        ax.plot([max(a90, -LIM), min(b90, LIM)], [yi, yi], color=COR, lw=3.2, alpha=0.55)
        if -LIM <= t <= LIM:
            ax.plot(t, yi, "o", color=COR, ms=5)
        for lado, v in ((-1, a), (1, b)):
            if lado * v > LIM:
                ax.annotate("", xy=(lado * LIM, yi), xytext=(lado * (LIM - 0.12), yi),
                            arrowprops={"arrowstyle": "->", "color": COR, "lw": 1.2})
        # Referências só na linha a que se aplicam (relativas: divididas pela base quando a referência é absoluta).
        if "(protocolo 40" in str(r["ref_protocolo"]):
            v = r["ref_protocolo_valor"] if r["ref_protocolo_escala"] == "relativa" else \
                r["ref_protocolo_valor"] / r["base_relativa"]
            ax.plot(v, yi, "D", color=COR_REF, ms=6, zorder=5)
        for k in (1, 2):
            lid = r[f"lit{k}_id"]
            if lid in ("A2_aceitacao", "A2_candidaturas", "C2_liquido_pmm"):
                v = r[f"lit{k}_valor_sup"] if r[f"lit{k}_escala"] == "relativa" else \
                    r[f"lit{k}_valor_sup"] / r["base_relativa"]
                ax.plot(v, yi, "s" if lid == "C2_liquido_pmm" else "x", color=COR_LIT, ms=6, mew=2, zorder=5,
                        mfc="none" if lid == "C2_liquido_pmm" else None)
    ax.axvline(0, color=CINZA, lw=0.8)
    ax.plot([], [], "D", color=COR_REF, label="protocolo 40: +10 p.p. de preenchimento / média abaixo (F1.3, F1.4); "
                                               "+25% (F1.1)")
    ax.plot([], [], "x", color=COR_LIT, mew=2, label="Dal Bó, Finan e Rossi (doc 20): aceitação / média abaixo "
                                                      "(F1.3, F1.4); candidaturas (F1.1)")
    ax.plot([], [], "s", color=COR_LIT, mfc="none", mew=2, label="Hone et al. (doc 20): líquido do Mais Médicos / "
                                                                 "média do pré (F3.1; só ordem de grandeza)")
    ax.plot([], [], color=COR, lw=1.4, label="IC 95% convencional")
    ax.plot([], [], color=COR, lw=3.2, alpha=0.55, label="IC 90% (TOST a 5%)")
    ax.set_yticks(y)
    ax.set_yticklabels([f"{ROTULO_CURTO[r['outcome_id']]} ({r['populacao']}"
                        + (f", ciclo {r['ciclo']})" if r["etapa_origem"] == "E6" else ", DiRD)")
                        for _, r in s.iterrows()], fontsize=8.5)
    ax.set_xlim(-LIM, LIM)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{100 * v:+.0f}%".replace("-", "−")))
    ax.set_xlabel("salto relativo à média abaixo do corte (E6) ou à média do pré abaixo do corte (E7)")
    ax.set_title("(a) RDD em nível (E6) e DiRD (E7), cortes empilhados", fontsize=10.5)
    ax.grid(True, axis="x", color=GRADE, lw=0.5)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(loc="upper left", bbox_to_anchor=(-0.55, -0.1), ncol=2, fontsize=7.5, frameon=False)

    yb, rot = [], []
    for i, (_, r) in enumerate(e9e.sort_values(["ciclo", "quantidade"]).iterrows()):
        yi = -i
        corte = r["quantidade"].rsplit("_", 1)[-1].replace(".", ",")
        bx.plot([r["ic95_inf"], r["ic95_sup"]], [yi, yi], color=COR, lw=1.4)
        bx.plot([r["ic90_inf"], r["ic90_sup"]], [yi, yi], color=COR, lw=3.2, alpha=0.55)
        bx.plot(r["tau"], yi, "o", color=COR, ms=5)
        yb.append(yi)
        rot.append(f"{'empilhado' if r['ciclo'] == 'empilhado' else 'ciclo ' + r['ciclo']}, degrau de {corte}")
    lit = literatura()
    c1, a2 = lit["C1_elasticidade"], lit["A2_elasticidade"]
    bx.axvspan(c1["valor_inf"], c1["valor_sup"], color=COR_LIT, alpha=0.18, lw=0,
               label="Costa, Nunes e Sanches (doc 20): escolha locacional, Brasil")
    bx.axvline(a2["valor_sup"], color=COR_REF, lw=1, ls="--", label="Dal Bó, Finan e Rossi (doc 20): pool")
    bx.axvline(0, color=CINZA, lw=0.8)
    bx.set_yticks(yb)
    bx.set_yticklabels(rot, fontsize=8.5)
    bx.set_xlabel("elasticidade-arco implícita (1ª opção)")
    bx.set_title("(b) E9: escolha entre células (realocação)", fontsize=10.5)
    bx.grid(True, axis="x", color=GRADE, lw=0.5)
    bx.spines[["top", "right"]].set_visible(False)
    bx.legend(loc="upper left", bbox_to_anchor=(0.0, -0.1), ncol=1, fontsize=7.5, frameon=False)

    fig.suptitle("X6 (exploratório, pós-síntese): o que cada IC descarta; dados EMPÍRICOS, sem estimação nova\n"
                 "contrastes: pacote do corte (E6), bolsa + variação das co-políticas (E7), degrau da bolsa na escolha "
                 "(E9); não é efeito da participação no PMM-E", fontsize=10)
    fig.tight_layout(rect=(0, 0.0, 1, 0.97))
    DIR_FIG.mkdir(parents=True, exist_ok=True)
    caminho = DIR_FIG / NOME_FIG
    fig.savefig(caminho, dpi=150, bbox_inches="tight", metadata={"Software": None})
    plt.close(fig)
    return caminho


# ---------------------------------------------------------------------------
# Doc 46, seção X6 (blocos gerados só a partir do CSV e do JSON do X6)
# ---------------------------------------------------------------------------

def _num(v, casas=3, sinal=True) -> str:
    if v is None or (isinstance(v, float) and not math.isfinite(v)):
        return "—"
    txt = f"{float(v):+.{casas}f}" if sinal else f"{float(v):.{casas}f}"
    return txt.replace("-", "−").replace(".", ",")


def _pp(v, casas=1, sinal=True) -> str:
    return "—" if not fin(v) else _num(100 * float(v), casas, sinal) + " p.p."


def _pct(v, casas=0, sinal=True) -> str:
    return "—" if not fin(v) else _num(100 * float(v), casas, sinal) + " %"


def _fmt(unidade: str, escala: str = "absoluta"):
    if escala == "razao de chances":
        return lambda v, sinal=True: _num(v, 2, False)
    if escala == "relativa":
        return lambda v, sinal=True: _pct(v, 0, sinal)
    if escala == "elasticidade":
        return lambda v, sinal=True: _num(v, 2, sinal)
    if str(unidade).startswith("fracao"):
        return lambda v, sinal=True: _pp(v, 1, sinal)
    if str(unidade).startswith("p.p."):
        return lambda v, sinal=True: _num(v, 3, sinal) + " p.p."
    if str(unidade).startswith("desvios"):
        return lambda v, sinal=True: _num(v, 2, sinal) + " DP"
    if str(unidade).startswith("horas") or str(unidade).startswith("pontos"):
        return lambda v, sinal=True: _num(v, 2, sinal)
    return lambda v, sinal=True: _num(v, 3, sinal)


def _simnao(v) -> str:
    if v is None or (isinstance(v, float) and not math.isfinite(v)):
        return "—"
    return "sim" if str(v) in ("True", "true", "1", "1.0") else "não"


def _b(v):
    """Booleano lido do CSV (True/False/NaN)."""
    if v is None or (isinstance(v, float) and not math.isfinite(v)):
        return None
    return str(v) in ("True", "true", "1", "1.0")


POSICAO_TXT = {"IC_ABAIXO_DA_REFERENCIA": "descarta (IC abaixo)", "IC_ACIMA_DA_REFERENCIA": "descarta (IC acima)",
               "IC_CONTEM_REFERENCIA": "não descarta", "NAO_AVALIAVEL": "—", "NAO_SE_APLICA": "—"}


def _ciclo_txt(r) -> str:
    return "pós" if r["etapa_origem"] == "E7" else str(r["ciclo"])


def blocos_doc(resumo: dict, tab: pd.DataFrame) -> dict[str, str]:
    blocos = {}
    lit = {x["id"]: x for x in resumo["literatura"]}

    # 1. Tabela principal (linhas empilhadas que a síntese lê + E9)
    s = sel_principais(tab)
    L = ["| Outcome | Pop. | Ciclo | Contraste | Salto | EP | MDE 80% | IC 95% | Média abaixo | IC 95% relativo "
         "| MDE relativo | δ TOST (abs.; rel.) | IC honesto informativo? |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for _, r in s.iterrows():
        fm = _fmt(r["unidade"])
        rel = r["escala_relativa"] == "base"
        L.append(" | ".join([
            f"| {ROTULO_CURTO[r['outcome_id']]}", r["populacao"], _ciclo_txt(r),
            "pacote (nível)" if r["etapa_origem"] == "E6" else "DiRD", fm(r["tau"]), fm(r["ep"], False),
            fm(r["mde80"], False), f"[{fm(r['ic95_inf'])}; {fm(r['ic95_sup'])}]",
            fm(r["base_relativa"], False) if rel else "—",
            f"[{_pct(r['ic95_inf_rel'])}; {_pct(r['ic95_sup_rel'])}]" if rel else "—",
            _pct(r["mde80_rel"], 0, False) if rel else "—",
            f"{fm(r['delta_tost'], False)}; " + (_pct(r["delta_tost_rel"], 0, False) if rel else "—"),
            _simnao(r["ic_honesto_informativo"]) + " |"]))
    rc = sel_e9(tab, "razao_chances_por_5mil")
    dp = sel_e9(tab, "variacao_prob_media_pp")
    for (_, r), (_, d) in zip(rc.iterrows(), dp.iterrows()):
        L.append(" | ".join([
            "| E9 escolha da 1ª opção (RC por +R$ 5 mil)", "candidatos de 1ª opção", r["ciclo"], "degrau na escolha",
            _num(r["tau"], 2, False), "—", _num(r["mde80"], 2, False),
            f"[{_num(r['ic95_inf'], 2, False)}; {_num(r['ic95_sup'], 2, False)}]",
            f"{_num(d['base_relativa'], 3, False)} p.p. (prob. base)",
            f"[{_pct(d['ic95_inf_rel'])}; {_pct(d['ic95_sup_rel'])}] (Δ prob.)",
            _pct(d["mde80_rel"], 0, False) + " (Δ prob.)",
            f"RC em [{_num(1 / r['delta_tost'], 2, False)}; {_num(r['delta_tost'], 2, False)}]; "
            + _pct(d["delta_tost_rel"], 0, False) + " (Δ prob.)", "— (sem IC honesto) |"]))
    blocos["tabela_poder"] = "\n".join(L)

    # 2. Referências do protocolo (+10 p.p. e +25%)
    L = ["| Outcome | Pop. | Ciclo | Corte | Escala | EP | MDE 80% | IC 95% (sup.) | δ TOST | Referência "
         "| IC exclui? | MDE < ref.? | TOST dentro? | IC honesto exclui? |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    ref = tab[tab["ref_protocolo"].astype(str).str.contains(r"\(protocolo 40", regex=True)].copy()
    ref = ref[(ref["corte"] == EMPILHADO) | (ref["especificacao"] == "poisson_local")]
    ordem = {"F1.3": 0, "F1.4": 1, "F1.1": 2}
    ref["_o"] = ref["outcome_id"].map(ordem)
    ref["_e"] = (ref["especificacao"] == "poisson_local").astype(int)
    ref["_m"] = ref["populacao"].str.contains(r"\+").map({True: 0, False: 1})
    for _, r in ref.sort_values(["_o", "_e", "_m", "ciclo", "corte"]).iterrows():
        if r["outcome_id"] == "F1.1":
            esc = "relativa (Poisson)" if r["especificacao"] == "poisson_local" else "relativa (linear / média abaixo)"
            fv = lambda v, sinal=True: _pct(v, 0, sinal)  # noqa: E731
            vals = (r["mde80_rel"], r["ic95_sup_rel"], r["delta_tost_rel"])
            refv = f"+{_pct(r['ref_protocolo_valor'], 0, False)}"
        else:
            esc = "p.p."
            fv = lambda v, sinal=True: _pp(v, 1, sinal)  # noqa: E731
            vals = (r["mde80"], r["ic95_sup"], r["delta_tost"])
            refv = f"+{_pp(r['ref_protocolo_valor'], 0, False)}"
        L.append(" | ".join([f"| {r['outcome_id']}", r["populacao"], r["ciclo"], r["corte"].replace(".", ","), esc,
                             (_num(r["ep"], 3, False) if r["especificacao"] == "poisson_local" else
                              (_pp(r["ep"], 1, False) if esc == "p.p." else _pct(r["ep"] / r["base_relativa"], 0, False))),
                             fv(vals[0], False), fv(vals[1]), fv(vals[2], False), refv,
                             _simnao(r["ic95_exclui_ref_protocolo"]), _simnao(r["mde80_abaixo_ref_protocolo"]),
                             _simnao(r["tost_dentro_ref_protocolo"]),
                             _simnao(r["ic_honesto_exclui_ref_protocolo"]) + " |"]))
    blocos["referencias_protocolo"] = "\n".join(L)

    # 3. Literatura
    L = ["| Outcome | Pop. | Ciclo / corte | Estimativa [IC 95%] | MDE 80% | Magnitude da literatura (doc 20) "
         "| IC 95% | MDE < magnitude? | IC honesto |",
         "|---|---|---|---|---|---|---|---|---|"]
    litrows = tab[(tab["lit1_id"].fillna("") != "") & ((tab["corte"] == EMPILHADO)
                                                        | (tab["etapa_origem"] == "E9")
                                                        | (tab["especificacao"] == "poisson_local"))].copy()
    litrows = litrows[(litrows["etapa_origem"] != "E6") | litrows["populacao"].str.contains(r"\+")
                      | (litrows["especificacao"] == "poisson_local")]
    for _, r in litrows.iterrows():
        for k in (1, 2):
            lid = r[f"lit{k}_id"]
            if not isinstance(lid, str) or not lid:
                continue
            x = lit[lid]
            if x["escala"] == "relativa":
                fv = lambda v, sinal=True: _pct(v, 0, sinal)  # noqa: E731
                est = f"{fv(r['tau_rel'])} [{fv(r['ic95_inf_rel'])}; {fv(r['ic95_sup_rel'])}]"
                m80 = fv(r["mde80_rel"], False)
                mag = fv(x["valor_sup"])
            elif x["escala"] == "elasticidade":
                fv = lambda v, sinal=True: _num(v, 2, sinal)  # noqa: E731
                est = f"{fv(r['tau'])} [{fv(r['ic95_inf'])}; {fv(r['ic95_sup'])}]"
                m80 = fv(r["mde80"], False)
                mag = (f"{fv(x['valor_inf'], False)} a {fv(x['valor_sup'], False)}" if x["valor_inf"] != x["valor_sup"]
                       else f"≈ {fv(x['valor_sup'], False)}")
            else:
                fv = _fmt(r["unidade"])
                est = f"{fv(r['tau'])} [{fv(r['ic95_inf'])}; {fv(r['ic95_sup'])}]"
                m80 = fv(r["mde80"], False)
                mag = fv(x["valor_sup"])
            if r["etapa_origem"] == "E9":
                cc = (("empilhado" if r["ciclo"] == "empilhado" else f"ciclo {r['ciclo']}") + ", degrau de "
                      + r["quantidade"].rsplit("_", 1)[-1].replace(".", ","))
                nome = "E9 elasticidade implícita"
            else:
                cc = f"{_ciclo_txt(r)} / {r['corte'].replace('.', ',')}"
                nome = r["outcome_id"] + (" (Poisson)" if r["especificacao"] == "poisson_local" else "")
            L.append(" | ".join([f"| {nome}", r["populacao"], cc, est, m80, f"{x['estudo']}: {mag}",
                                 POSICAO_TXT.get(r[f"lit{k}_posicao_ic95"], "—"), _simnao(r[f"lit{k}_mde80_abaixo"]),
                                 POSICAO_TXT.get(r[f"lit{k}_posicao_ic_honesto"], "—") + " |"]))
    L.append("")
    L.append("Trechos copiados do doc 20 (o número de cada linha sai deste texto): "
             + "; ".join(f"{x['estudo']}: \"{x['trecho'].replace('**', '')}\"" for x in resumo["literatura"]) + ".")
    blocos["literatura"] = "\n".join(L)

    # 4. Contagens
    c = resumo["contagens"]
    pe = c["por_etapa"]
    blocos["contagens"] = "\n".join([
        f"- Linhas no CSV: {c['linhas']} (E6: {pe.get('E6', 0)}; E7: {pe.get('E7', 0)}; E9: {pe.get('E9', 0)}).",
        f"- Linhas com referência do protocolo (F1.1, F1.3 e F1.4, por ciclo, por corte e empilhadas, mais o Poisson "
        f"local de F1.1): {c['com_referencia_do_protocolo']}. O IC 95% convencional exclui a referência em "
        f"{c['ic95_exclui_ref_protocolo']}; o MDE de 80% fica abaixo dela em {c['mde80_abaixo_ref_protocolo']}; o "
        f"TOST declara equivalência dentro de ± a referência em {c['tost_dentro_ref_protocolo']}; o IC honesto a "
        f"exclui em {c['ic_honesto_exclui_ref_protocolo']}.",
        f"- IC honesto: existe em {c['com_ic_honesto']} linhas. É informativo (critério na coluna "
        f"`ic_honesto_criterios`) em {c['ic_honesto_informativo']}, não informativo em "
        f"{c['ic_honesto_nao_informativo']} e não avaliável em {c['ic_honesto_nao_avaliavel']} (índice P1: sem "
        f"referência nem base). Entre as {c['fracoes_com_ic_honesto']} linhas de fração com IC honesto, "
        f"{c['fracoes_com_ic_honesto_cobrindo_todo_salto_possivel']} cobrem todo salto logicamente possível "
        f"([−100 p.p.; +100 p.p.]).",
        f"- Bases relativas indisponíveis: {c['bases_indisponiveis']}.",
    ])

    # 5. Leitura gerada: frases com números e com o sentido decidido pelos dados (nada fixo no texto)
    def um(et, oid, pop, cic, corte=EMPILHADO, espec="principal"):
        m = (tab["etapa_origem"] == et) & (tab["outcome_id"] == oid) & (tab["populacao"] == pop) \
            & (tab["corte"] == corte) & (tab["especificacao"] == espec)
        if cic is not None:
            m &= tab["ciclo"] == cic
        x = tab[m]
        exigir(len(x) == 1, f"doc: {et} {oid} {pop} {cic} {corte}")
        return x.iloc[0]

    def acima(v, ref) -> str:
        return "acima" if v > ref else "abaixo"

    f13 = um("E6", "F1.3", "V1+V2+V3", "1+2+3")
    f13c = [um("E6", "F1.3", f"V{k}", str(k)) for k in (1, 2, 3)]
    f11 = um("E6", "F1.1", "V1+V2+V3", "1+2+3")
    pois = tab[(tab["outcome_id"] == "F1.1") & (tab["especificacao"] == "poisson_local")]
    p2 = um("E7", "F3.1", "U", None)
    p1 = um("E6", "P1", "V1+V2+V3", "1+2+3")
    rc = sel_e9(tab, "razao_chances_por_5mil").set_index("ciclo")
    el = tab[(tab["etapa_origem"] == "E9") & tab["quantidade"].str.startswith("elasticidade_implicita")]
    el2 = el[el["ciclo"] == "2"]
    c1, a2a = lit["C1_elasticidade"], lit["A2_aceitacao"]
    mde_ciclo = [x["mde80"] for x in f13c]
    princ = sel_principais(tab)
    princ_rel = princ[princ["escala_relativa"] == "base"]
    mais_preciso = princ_rel.loc[princ_rel["mde80_rel"].idxmin()]

    excl = _b(f13["ic95_exclui_ref_protocolo"])
    tem_poder = _b(f13["mde80_abaixo_ref_protocolo"])
    if excl and not tem_poder and f13["tau"] < 0:
        porque = ("mas porque a estimativa pontual é negativa (" + _pp(f13["tau"]) + "), não porque o desenho tenha "
                  "poder de 80% contra ela")
    elif excl:
        porque = "e o desenho tem poder de 80% contra ela"
    else:
        porque = "e não a exclui"
    frase_pos = {"IC_ABAIXO_DA_REFERENCIA": "fica acima do limite superior do IC 95% (descartada sob o IC convencional)",
                 "IC_ACIMA_DA_REFERENCIA": "fica abaixo do limite inferior do IC 95%",
                 "IC_CONTEM_REFERENCIA": "fica dentro do IC 95% (não descartada)"}
    pos_a2 = frase_pos[f13["lit1_posicao_ic95"] if f13["lit1_id"] == "A2_aceitacao" else f13["lit2_posicao_ic95"]]
    L = [
        f"- **Preenchimento na 1ª chamada (F1.3), ciclos e cortes empilhados:** MDE de 80% = "
        f"{_pp(f13['mde80'], 1, False)}, {acima(f13['mde80'], REF_PREENCHIMENTO)} da referência do protocolo. O IC 95% "
        f"convencional vai até {_pp(f13['ic95_sup'])}{' e exclui a referência' if excl else ''}, {porque}. A "
        f"equivalência a 5% só vale com margem de ±{_pp(f13['delta_tost'], 1, False)} ou mais. A aceitação de Dal Bó, "
        f"Finan e Rossi ({_pp(a2a['valor_sup'], 1)}) {pos_a2}.",
        f"- **Por ciclo**, o MDE de F1.3 vai de {_pp(min(mde_ciclo), 1, False)} a {_pp(max(mde_ciclo), 1, False)}; "
        f"{sum(m < REF_PREENCHIMENTO for m in mde_ciclo)} de {len(mde_ciclo)} ciclos isolados têm poder de 80% contra "
        f"a referência de preenchimento.",
        f"- **Candidaturas (F1.1), linear empilhado relativo à média abaixo:** MDE de "
        f"{_pct(f11['mde80_rel'], 0, False)}; IC 95% relativo [{_pct(f11['ic95_inf_rel'])}; "
        f"{_pct(f11['ic95_sup_rel'])}]. No Poisson local por ciclo e corte, o MDE relativo vai de "
        f"{_pct(pois['mde80_rel'].min(), 0, False)} a {_pct(pois['mde80_rel'].max(), 0, False)}; "
        f"{int((pois['mde80_rel'] < REF_CANDIDATURAS).sum())} de {len(pois)} linhas têm poder de 80% contra a "
        f"referência de candidaturas.",
        f"- **P1 (índice):** MDE de {_num(p1['mde80'], 2, False)} DP; equivalência a 5% só com margem de "
        f"±{_num(p1['delta_tost'], 2, False)} DP ou mais.",
        f"- **P2 (F3.1 por DiRD em U, empilhado):** MDE de {_num(p2['mde80'], 3, False)} vínculo por 10 mil hab., "
        f"{_pct(p2['mde80_rel'], 1, False)} da média do pré abaixo do corte ({_num(p2['base_relativa'], 3, False)}); "
        f"IC 95% relativo [{_pct(p2['ic95_inf_rel'], 1)}; {_pct(p2['ic95_sup_rel'], 1)}]; IC honesto informativo: "
        f"{_simnao(p2['ic_honesto_informativo'])}.",
        f"- **Menor MDE relativo** entre as linhas empilhadas da tabela de X6.2: "
        f"{ROTULO_CURTO[mais_preciso['outcome_id']]} ({mais_preciso['populacao']}, "
        f"{'DiRD' if mais_preciso['etapa_origem'] == 'E7' else 'nível'}), {_pct(mais_preciso['mde80_rel'], 1, False)} "
        f"da base.",
        f"- **E9 (escolha):** a menor razão de chances detectável com 80% de poder é "
        f"{_num(rc.loc['2', 'mde80'], 2, False)} no ciclo 2 (estimada {_num(rc.loc['2', 'tau'], 2, False)}) e "
        f"{_num(rc.loc['empilhado', 'mde80'], 2, False)} no empilhado (estimada "
        f"{_num(rc.loc['empilhado', 'tau'], 2, False)}). A elasticidade-arco implícita do ciclo 2 vai de "
        f"{_num(el2['tau'].min(), 2, False)} a {_num(el2['tau'].max(), 2, False)} conforme o degrau do corte, contra "
        f"{_num(c1['valor_inf'], 1, False)} a {_num(c1['valor_sup'], 1, False)} em Costa, Nunes e Sanches. "
        f"{int((el['lit2_mde80_abaixo'].map(_b) == True).sum())} de {len(el)} linhas de elasticidade "  # noqa: E712
        f"têm MDE abaixo do limite inferior dessa faixa.",
    ]
    blocos["leitura"] = "\n".join(L)

    # 6. O que o X6 acrescenta às propostas do doc 44 (§7), com o sentido decidido pelos dados
    nref, nmde = c["com_referencia_do_protocolo"], c["mde80_abaixo_ref_protocolo"]
    nhon, ninf = c["com_ic_honesto"] - c["ic_honesto_nao_avaliavel"], c["ic_honesto_informativo"]
    el_c1 = el.apply(lambda r: r["lit2_posicao_ic95"] if r["lit2_id"] == "C1_elasticidade" else r["lit1_posicao_ic95"],
                     axis=1)
    blocos["acrescenta"] = "\n".join([
        f"- **Proposta C (quanto e em que margem):** em {nmde} de {nref} linhas com referência do protocolo o MDE de "
        f"80% fica abaixo da referência. Os nulos de preenchimento e candidaturas não são efeito zero: o desenho "
        f"entre municípios {'não tem' if nmde == 0 else 'tem só em parte'} poder contra as magnitudes do protocolo, "
        f"e o que se descarta vem do sinal das estimativas pontuais, sob o IC convencional.",
        f"- **IC honesto:** informativo em {ninf} de {nhon} linhas avaliáveis; a precisão relatada depende da "
        f"aproximação local linear.",
        f"- **Propostas A e B:** a elasticidade implícita da escolha fica acima da faixa de Costa, Nunes e Sanches em "
        f"{int((el_c1 == 'IC_ACIMA_DA_REFERENCIA').sum())} de {len(el)} linhas, abaixo em "
        f"{int((el_c1 == 'IC_ABAIXO_DA_REFERENCIA').sum())} e a contém nas demais; nenhum ciclo tem MDE abaixo dessa "
        f"faixa, de modo que um nulo da escolha também não descarta elasticidades da ordem da literatura brasileira."
        if int((el['lit2_mde80_abaixo'].map(_b) == True).sum()) == 0 else  # noqa: E712
        f"- **Propostas A e B:** a elasticidade implícita da escolha fica acima da faixa de Costa, Nunes e Sanches em "
        f"{int((el_c1 == 'IC_ACIMA_DA_REFERENCIA').sum())} de {len(el)} linhas e abaixo em "
        f"{int((el_c1 == 'IC_ABAIXO_DA_REFERENCIA').sum())}.",
    ])
    return blocos


MARCA = re.compile(r"(<!-- X6:(?P<nome>[A-Za-z0-9_]+):inicio -->\n)(?P<corpo>.*?)(\n<!-- X6:(?P=nome):fim -->)", re.S)

TITULO_DOC46 = "# 46 — Resultados exploratórios pós-síntese (X1–X6)"

SECAO_X6 = """## X6 — Poder e o que se descarta

> **Protocolo:** [`45_protocolo_exploratorio_pos_sintese.md`](45_protocolo_exploratorio_pos_sintese.md), §3 X6,
> congelado em 19/10/2026.<br>
> **Estatuto:** exploratório e pós-resultado (`estatuto = EXPLORATORIO_POS_SINTESE`). Não muda o protocolo 40, os
> resultados E3–E9 nem o Holm das primárias.<br>
> **Script:** `scripts/rdd_bolsa/20_poder_descartes.py`. Nenhuma estimação nova: só aritmética sobre o EP, o IC e as
> médias já publicados no E6, E7, E8 e E9.<br>
> **Saídas:** `output/rdd_bolsa/X6_poder_descartes.csv`, `output/rdd_bolsa/X6_resumo.json` (natureza dos dados:
> **EMPIRICO**; entradas com SHA-256) e `output/rdd_bolsa/X6_figuras/X6_descartes.png`.<br>
> **Testes:** `tests/test_x6_poder.py`. Todo número desta seção está entre marcadores `<!-- X6:... -->`, gerados
> só a partir das saídas do X6 por `python3 scripts/rdd_bolsa/20_poder_descartes.py --atualizar-doc`; o teste
> confere os blocos e que a prosa fora deles só tem parâmetros.

### X6.1 Pergunta e definições

A síntese (doc 44) relata IC, mas não uma tabela de poder comparável entre outcomes. Para cada linha principal do
E6 (P1 e F0–F4, cada corte e empilhado, ciclos empilhados onde definidos, mais o Poisson local de F1.1), do E7
(DiRD da família F3) e do E9 (coeficiente da bolsa, por ciclo e empilhado), o X6 calcula:

- **MDE de 80%:** o menor salto que o desenho detecta com 80% de poder num teste bicaudal a 5%, 2,8 × EP (a
  convenção do E5). Na razão de chances, é a exponencial de 2,8 × EP do log;
- **o que o IC 95% convencional descarta**, em termos absolutos e relativos à média abaixo do corte na janela. Nas
  linhas empilhadas, a base é a média das médias abaixo de cada grupo ponderada pelos mesmos pesos que definem o
  estimando empilhado. No E7, a base é a média do pré abaixo do corte, como no doc 44;
- **equivalência:** a menor margem simétrica δ tal que o IC 90% fica dentro de [−δ, +δ]; para toda margem maior que
  δ, o TOST a 5% declara o efeito equivalente a zero;
- **comparação** com as referências do protocolo 40 (+10 p.p. de preenchimento, +25% de candidaturas) e com
  magnitudes da literatura lidas do doc 20 da seção 03;
- **se o IC honesto é informativo:** se, com o M do protocolo, ele exclui a referência, uma magnitude da literatura
  aplicável, ou fica dentro de ±100% da base.

**Contraste.** E6: pacote do corte (bolsa anunciada e outras regras federais nos mesmos cortes). E7: bolsa mais a
variação das co-políticas. E9: degrau da bolsa na repartição da 1ª opção entre células, não no total de
candidatos. Nenhum é efeito da participação no PMM-E nem do Agora Tem Especialistas.

**Como ler.** "Descartar" quer dizer que o limite do IC fica do outro lado da magnitude, sob o IC convencional e a
aproximação local linear. Um IC que descarta +10 p.p. porque a estimativa pontual é negativa não equivale a um
desenho com poder contra +10 p.p.: a coluna do MDE separa as duas coisas.

### X6.2 Poder e descartes nas linhas que a síntese lê

Linhas empilhadas (cortes e ciclos) e o E9. A tabela completa, com cada corte e cada ciclo, está no CSV.

<!-- X6:tabela_poder:inicio -->

<!-- X6:tabela_poder:fim -->

### X6.3 Referências do protocolo

<!-- X6:referencias_protocolo:inicio -->

<!-- X6:referencias_protocolo:fim -->

### X6.4 Magnitudes da literatura

A comparação é de ordem de grandeza. Outcome, população e degrau diferem (doc 44, §6): a aceitação de Dal Bó, Finan
e Rossi é de servidores públicos sorteados para um salário maior; o número de Bobba et al. é uma estimativa não
significativa; o líquido de Hone et al. é do Mais Médicos inteiro, sobre generalistas. A elasticidade do E9 é da
repartição da 1ª opção entre células, calculada como a variação relativa média da probabilidade sobre o degrau
relativo da bolsa em cada corte.

<!-- X6:literatura:inicio -->

<!-- X6:literatura:fim -->

### X6.5 Contagens

<!-- X6:contagens:inicio -->

<!-- X6:contagens:fim -->

### X6.6 Leitura

<!-- X6:leitura:inicio -->

<!-- X6:leitura:fim -->

O que o X6 acrescenta à síntese, para as propostas A, B e C do doc 44 (§7):

<!-- X6:acrescenta:inicio -->

<!-- X6:acrescenta:fim -->

![X6: IC relativos à média abaixo do corte e elasticidades do E9](../../output/rdd_bolsa/X6_figuras/X6_descartes.png)
"""


def aplicar_blocos(texto: str, blocos: dict[str, str]) -> str:
    def sub(m):
        nome = m.group("nome")
        if nome not in blocos:
            raise KeyError(f"bloco {nome} nao gerado")
        return m.group(1) + blocos[nome] + m.group(4)
    return MARCA.sub(sub, texto)


def blocos_no_doc(texto: str) -> dict[str, str]:
    return {m.group("nome"): m.group("corpo") for m in MARCA.finditer(texto)}


def secao_x6(texto: str) -> str:
    """Texto da seção '## X6' do doc 46 (até o próximo '## ' ou o fim)."""
    m = re.search(r"(?ms)^## X6\b.*?(?=^## (?!X6)|\Z)", texto)
    return m.group(0) if m else ""


def atualizar_doc() -> None:
    resumo, tab = ler_saidas()
    texto = DOC46.read_text(encoding="utf-8") if DOC46.exists() else TITULO_DOC46 + "\n"
    atual = secao_x6(texto)
    if atual:  # a seção X6 é deste script: é regravada inteira; as outras seções do doc ficam intactas
        fim = "\n\n" if not texto.endswith(atual) else "\n"
        texto = texto.replace(atual, SECAO_X6.rstrip("\n") + fim)
    else:
        texto = texto.rstrip("\n") + "\n\n" + SECAO_X6
    DOC46.write_text(aplicar_blocos(texto, blocos_doc(resumo, tab)), encoding="utf-8")
    print(f"secao X6 regravada: {rotulo(DOC46)}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--atualizar-doc", action="store_true", help="so regrava os blocos X6 do doc 46")
    args = ap.parse_args(argv)
    if args.atualizar_doc:
        atualizar_doc()
        return 0
    try:
        resumo, tab = construir()
        gravar(resumo, tab)
    except FalhaFechada as e:
        print(f"FALHA FECHADA: {e}", file=sys.stderr)
        return 1
    print(f"gravado: {rotulo(OUT / NOME_CSV)} ({len(tab)} linhas); {rotulo(OUT / NOME_RESUMO)}; "
          f"{rotulo(DIR_FIG / NOME_FIG)}")
    atualizar_doc()
    return 0


if __name__ == "__main__":
    sys.exit(main())
