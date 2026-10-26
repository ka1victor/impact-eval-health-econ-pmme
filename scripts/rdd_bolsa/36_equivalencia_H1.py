"""Protocolo 60, parte A: equivalência no preenchimento (H1) por TOST, só com as estimativas gravadas.

Protocolo congelado: `docs/06_execucao/60_protocolo_equivalencia_e_oferta_local.md` (26/10/2026, commit f47624f,
antes de qualquer conta). Estatuto de toda saída: `PROTOCOLO_60_POS_RESULTADO`; `natureza_dos_dados = EMPIRICO`.
Os IC 95% de A3 e N1 já eram públicos (docs 49 e 57): pelos IC publicados, o resultado era previsível em boa parte.

O que faz
---------
- Lê `output/rdd_bolsa/NA_estimativas.csv` (A3, script 24) e `N_estimativas.csv` (N1, script 23). Nada é
  reestimado.
- Antes de calcular, confere que os valores lidos reproduzem os números citados no doc 57: as seis linhas de
  preenchimento de A3 do §4.2 e a linha de N1 do §4.1 (o §4.2 não traz N1). Se não reproduzirem, para.
- TOST (dois testes unilaterais a 5%) com as margens do protocolo: A3 ±10 p.p.; N1 ±25% da média abaixo do corte
  na mesma amostra (`media_abaixo` gravada pelo bloco; se faltar, para).
    teste do aumento   H0: salto ≥ +m    p = Φ((τ̂ − m + B) / EP)
    teste da queda     H0: salto ≤ −m    p = Φ((−m − τ̂ + B) / EP)
  com B = 0 no IC convencional (EP CR1 gravado) e B = viés máximo gravado no IC honesto (Armstrong–Kolesár,
  regra do E6). O IC 90% que corresponde ao TOST é τ̂ ∓ (B + z₀,₉₅ · EP); a margem mínima de equivalência é o
  menor m com o IC 90% dentro de [−m; +m], isto é |τ̂| + B + z₀,₉₅ · EP.
- Holm entre as duas primárias (A3 e N1 empilhados), em cada um dos três p (aumento, queda, TOST = máximo dos
  dois). Secundárias e IC honesto sem ajuste.

Saídas
------
`output/rdd_bolsa/EQ_estimativas.csv`, `EQ_resumo.json`, `EQ_figuras/EQ_tost_ic90.png`; com `--atualizar-doc`,
também `docs/06_execucao/57j_resultados_equivalencia_H1.md`, gerado inteiro a partir de `output/` (blocos entre
marcadores `<!-- EQ:... -->`).

Integridade: nada simulado nem imputado; o arquivo local de IVS da auditoria 16 não é lido; nenhum CNES é lido;
as saídas dos blocos anteriores não são regravadas.

Uso
---
    python3 scripts/rdd_bolsa/36_equivalencia_H1.py                  # calcula e grava as saídas
    python3 scripts/rdd_bolsa/36_equivalencia_H1.py --atualizar-doc  # idem e regrava o doc 57j
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
DIR_RDD = ROOT / "scripts" / "rdd_bolsa"


def _importar(caminho: Path, nome: str):
    if nome in sys.modules:
        return sys.modules[nome]
    bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    sys.dont_write_bytecode = bytecode
    return mod


L = _importar(DIR_RDD / "rdd_lib.py", "rdd_lib")

# ---------------------------------------------------------------------------
# Parâmetros fixados pelo protocolo 60, parte A
# ---------------------------------------------------------------------------

OUT = ROOT / "output" / "rdd_bolsa"
NA_EST = OUT / "NA_estimativas.csv"
N_EST = OUT / "N_estimativas.csv"
DOC57 = ROOT / "docs" / "06_execucao" / "57_sintese_perguntas_reformuladas.md"
PROTOCOLO_MD = ROOT / "docs" / "06_execucao" / "60_protocolo_equivalencia_e_oferta_local.md"
PROTOCOLO_40 = ROOT / "docs" / "06_execucao" / "40_protocolo_multioutcome_rdd_bolsa.md"
DOC = ROOT / "docs" / "06_execucao" / "57j_resultados_equivalencia_H1.md"
NOME_EST = "EQ_estimativas.csv"
NOME_RESUMO = "EQ_resumo.json"
DIR_FIG = OUT / "EQ_figuras"
NOME_FIG = "EQ_tost_ic90.png"

DATA_EXECUCAO = "2026-10-26"
ESTATUTO = "PROTOCOLO_60_POS_RESULTADO"
NATUREZA = "EMPIRICO"
COMMIT_CONGELAMENTO = "f47624f"
SHA_PROTOCOLO_CONGELADO = "4c7cb1d096805a01189f611e3d54ef3a97fb4f9030055af1f688625fa505699b"
ALFA = 0.05
Z = float(stats.norm.ppf(1.0 - ALFA))  # 1,645: cada teste unilateral a 5% ⇔ IC 90%
MARGEM_A3 = 0.10  # fração (±10 p.p.)
FRACAO_N1 = 0.25  # ±25% da média abaixo do corte na mesma amostra
VARIANTE_HONESTA_PRINCIPAL = "S-a: ic_honesto_M_x1"
VARIANTES_HONESTAS = [("S-a: ic_honesto_M_x1", "honesto_M_x1", "regra do E6 (M = regra de bolso), a do bloco"),
                      ("S-a: ic_honesto_M_x0.5", "honesto_M_x0.5", "metade do M da regra do E6"),
                      ("S-a: ic_honesto_M_x2", "honesto_M_x2", "o dobro do M da regra do E6"),
                      ("S-a: ic_honesto_pos_resultado", "honesto_pos_resultado",
                       "suporte POS_RESULTADO do bloco (fora do protocolo 48)")]

# Linhas do protocolo: (id, outcome, papel, população no arquivo, ciclo, corte, rótulo legível).
LINHAS = [
    ("A3-emp-123", "A3", "primaria", "V1+V2+V3 (celulas)", "1+2+3", "empilhado", "ciclos 1–3, cortes empilhados"),
    ("N1-emp-123", "N1", "primaria", "V1+V2+V3", "1+2+3", "empilhado", "ciclos 1–3, cortes empilhados"),
    ("A3-300-123", "A3", "secundaria", "V1+V2+V3 (celulas)", "1+2+3", "0.300", "ciclos 1–3, corte 0,300"),
    ("A3-400-123", "A3", "secundaria", "V1+V2+V3 (celulas)", "1+2+3", "0.400", "ciclos 1–3, corte 0,400"),
    ("A3-300-c1", "A3", "secundaria", "V1 (celulas)", "1", "0.300", "ciclo 1, corte 0,300"),
    ("A3-400-c1", "A3", "secundaria", "V1 (celulas)", "1", "0.400", "ciclo 1, corte 0,400"),
    ("A3-emp-c1", "A3", "secundaria", "V1 (celulas)", "1", "empilhado", "ciclo 1, cortes empilhados"),
    ("N1-300-123", "N1", "secundaria", "V1+V2+V3", "1+2+3", "0.300", "ciclos 1–3, corte 0,300"),
    ("N1-400-123", "N1", "secundaria", "V1+V2+V3", "1+2+3", "0.400", "ciclos 1–3, corte 0,400"),
]
DESCRICAO = {"A3": "célula aberta preenchida na 1ª chamada (A3_PREENCHIDA, unidade = célula do quadro)",
             "N1": "vagas preenchidas na 1ª chamada por município, com controle linear das vagas oferecidas (S-a)"}
UNIDADE = {"A3": "fração (×100 = p.p.)", "N1": "vagas por município"}
REGRA_MARGEM = {"A3": "±10 p.p. (protocolo 60, parte A; referência do protocolo 40, §7)",
                "N1": "±25% da média abaixo do corte na mesma amostra (protocolo 60, parte A; referência do "
                      "protocolo 40, §7)"}

COLUNAS = ["natureza_dos_dados", "estatuto", "id_linha", "outcome", "descricao_outcome", "papel", "populacao",
           "ciclo", "corte", "amostra", "tipo_ic", "nota_ic", "arquivo_origem", "especificacao_origem",
           "variante_origem", "unidade", "n_abaixo", "n_acima", "tau", "ep", "vies_max", "ic95_inf", "ic95_sup",
           "media_abaixo", "margem", "regra_margem", "ic90_inf", "ic90_sup", "p_aumento", "p_queda", "p_tost",
           "entra_holm", "p_holm_aumento", "p_holm_queda", "p_holm_tost", "base_decisao", "rejeita_aumento",
           "rejeita_queda", "equivalente", "leitura_codigo", "leitura", "margem_minima",
           "margem_minima_relativa_media", "nota"]

CHAVES_57 = {  # rótulo da linha no doc 57, §4.2 (preenchimento) -> id da linha
    "ciclos 1–3, corte 0,300": "A3-300-123", "ciclos 1–3, corte 0,400": "A3-400-123",
    "ciclos 1–3, cortes empilhados": "A3-emp-123", "ciclo 1, corte 0,300": "A3-300-c1",
    "ciclo 1, corte 0,400": "A3-400-c1", "ciclo 1, cortes empilhados": "A3-emp-c1"}
ROTULO_N1_57 = "N1 vagas preenchidas (protocolo 48)"


class FalhaValidacao(RuntimeError):
    """Conferência obrigatória falhou: o script para sem gravar."""


def rotulo(p: Path) -> str:
    return Path(p).resolve().relative_to(ROOT).as_posix()


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with Path(p).open("rb") as f:
        for bloco in iter(lambda: f.read(1 << 22), b""):
            h.update(bloco)
    return h.hexdigest()


def _nan_none(o):
    if isinstance(o, dict):
        return {str(k): _nan_none(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_nan_none(v) for v in o]
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, (np.floating, float)):
        return None if not np.isfinite(o) else float(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


def gravar_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(_nan_none(obj), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# 1. TOST (funções puras; conferidas em caso sintético em tests/test_equivalencia_H1.py)
# ---------------------------------------------------------------------------

def tost(tau: float, ep: float, margem: float, vies_max: float = 0.0, z: float = Z) -> dict:
    """Dois testes unilaterais de equivalência com viés limitado por `vies_max` (0 no IC convencional).

    Aumento: H0 salto ≥ +m, p = Φ((τ̂ − m + B)/EP). Queda: H0 salto ≤ −m, p = Φ((−m − τ̂ + B)/EP).
    Com B > 0, o pior caso do viés empurra a estimativa na direção de H0 (teste honesto unilateral).
    """
    if not (ep > 0 and math.isfinite(tau) and margem > 0 and vies_max >= 0):
        raise ValueError("tost: EP, margem e viés têm de ser válidos")
    b = float(vies_max)
    p_aum = float(stats.norm.cdf((tau - margem + b) / ep))
    p_que = float(stats.norm.cdf((-margem - tau + b) / ep))
    semi = b + z * ep
    lo, hi = tau - semi, tau + semi
    return {"ic90_inf": lo, "ic90_sup": hi, "p_aumento": p_aum, "p_queda": p_que, "p_tost": max(p_aum, p_que),
            "margem_minima": max(abs(lo), abs(hi))}


LEITURAS = {
    "EQUIVALENTE": "os dois testes rejeitam: o salto está dentro de ±{m}",
    "SO_AUMENTO": "só o teste do aumento rejeita: não houve aumento de {m} ou mais, mas uma queda de {m} não fica "
                  "descartada",
    "SO_QUEDA": "só o teste da queda rejeita: não houve queda de {m} ou mais, mas um aumento de {m} não fica "
                "descartado",
    "INCONCLUSIVO": "nenhum teste rejeita: inconclusivo",
}


def classificar(rej_aumento: bool, rej_queda: bool) -> str:
    """Leitura pré-registrada do protocolo 60 (o caso só-queda é o espelho do só-aumento)."""
    if rej_aumento and rej_queda:
        return "EQUIVALENTE"
    if rej_aumento:
        return "SO_AUMENTO"
    if rej_queda:
        return "SO_QUEDA"
    return "INCONCLUSIVO"


def texto_margem(outcome: str, margem: float, media: float) -> str:
    if outcome == "A3":
        return f"{_n(100 * margem, 0, False)} p.p."
    return f"{_n(100 * margem / media, 0, False)}% da média ({_n(margem, 2, False)} vaga por município)"


# ---------------------------------------------------------------------------
# 2. Leitura e conferência dos insumos
# ---------------------------------------------------------------------------

def _num(txt: str) -> float:
    t = txt.strip().replace("−", "-").replace("+", "").replace("%", "").replace(".", "").replace(",", ".")
    return float(t)


def _bloco(texto: str, nome: str) -> str:
    m = re.search(rf"<!-- S57:{nome}:inicio -->\n(.*?)\n<!-- S57:{nome}:fim -->", texto, re.S)
    if not m:
        raise FalhaValidacao(f"doc 57: bloco S57:{nome} não encontrado")
    return m.group(1)


def _celulas(linha: str) -> list[str]:
    return [c.strip() for c in linha.strip().strip("|").split("|")]


def ler_doc57(texto: str) -> dict:
    """Números do doc 57: A3 de preenchimento (§4.2) e N1 (§4.1). Devolve {id_linha: {campo: valor}}."""
    bloco = _bloco(texto, "pergunta_central")
    m = re.search(r"\*\*Preenchimento.*?\n(.*?)\n\*\*Atração", bloco, re.S)
    if not m:
        raise FalhaValidacao("doc 57, §4.2: tabela de preenchimento não encontrada")
    out = {}
    for linha in m.group(1).splitlines():
        cel = _celulas(linha) if linha.startswith("|") else []
        if len(cel) == 5 and cel[0] in CHAVES_57:
            mm = re.match(r"(\S+) \[(\S+); (\S+)\]", cel[2])
            out[CHAVES_57[cel[0]]] = {"media_abaixo": _num(cel[1]), "tau": _num(mm.group(1)),
                                      "ic95_inf": _num(mm.group(2)), "ic95_sup": _num(mm.group(3)),
                                      "maior_aumento": _num(cel[3]), "mde": _num(cel[4]), "casas": 1}
    for linha in _bloco(texto, "poder").splitlines():
        cel = _celulas(linha) if linha.startswith("|") else []
        if cel and cel[0] == ROTULO_N1_57:
            mm = re.match(r"\[(\S+); (\S+)\]", cel[3])
            out["N1-emp-123"] = {"tau": _num(cel[2]), "ic95_inf": _num(mm.group(1)), "ic95_sup": _num(mm.group(2)),
                                 "maior_aumento": _num(cel[4]), "mde": _num(cel[5]), "casas": 2}
    faltam = sorted((set(CHAVES_57.values()) | {"N1-emp-123"}) - set(out))
    if faltam:
        raise FalhaValidacao(f"doc 57: linhas não encontradas: {faltam}")
    return out


def selecionar(na: pd.DataFrame, n: pd.DataFrame) -> dict:
    """Uma linha gravada por linha do protocolo (e as linhas do IC honesto de N1). Para se faltar ou duplicar."""
    sel = {}
    for idl, oc, papel, pop, ciclo, corte, _ in LINHAS:
        if oc == "A3":
            m = ((na["outcome_id"] == "A3_PREENCHIDA") & (na["especificacao"] == "A3") & (na["variante"] == "principal")
                 & (na["populacao"] == pop) & (na["ciclo"] == ciclo) & (na["corte"] == corte))
            d = na[m]
        else:
            m = ((n["outcome_id"] == "N1") & (n["familia"] == "N") & (n["especificacao"] == "S-a")
                 & (n["variante"] == "principal") & (n["populacao"] == pop) & (n["ciclo"] == ciclo)
                 & (n["corte"] == corte))
            d = n[m]
        if len(d) != 1:
            raise FalhaValidacao(f"{idl}: {len(d)} linhas gravadas (esperado 1)")
        r = d.iloc[0]
        if r["status"] != "EXECUTADO" or r["natureza_dos_dados"] != NATUREZA:
            raise FalhaValidacao(f"{idl}: status {r['status']}, natureza {r['natureza_dos_dados']}")
        for c in ("tau", "ep", "media_abaixo"):
            if not np.isfinite(float(r[c])):
                raise FalhaValidacao(f"{idl}: {c} não gravado pelo bloco; parar e relatar (protocolo 60)")
        hon = {}
        if oc == "N1":
            for var, tipo, _nota in VARIANTES_HONESTAS:
                h = n[(n["outcome_id"] == "N1") & (n["familia"] == "N") & (n["especificacao"] == "S-g")
                      & (n["variante"] == var) & (n["populacao"] == pop) & (n["ciclo"] == ciclo) & (n["corte"] == corte)]
                if len(h) != 1:
                    raise FalhaValidacao(f"{idl}: IC honesto {var}: {len(h)} linhas")
                hon[tipo] = h.iloc[0]
        sel[idl] = {"linha": r, "honesto": hon}
    return sel


def conferir(sel: dict, doc57: dict) -> dict:
    """Confere os valores lidos contra o doc 57 e a coerência interna das linhas gravadas. Para se falhar."""
    erros, itens = [], []
    for idl, ref in sorted(doc57.items()):
        r = sel[idl]["linha"]
        f = 100.0 if idl.startswith("A3") else 1.0
        casas = ref["casas"]
        tol = 0.5 * 10 ** (-casas) + 1e-9
        lido = {"tau": f * r["tau"], "ic95_inf": f * r["ic95_inf"], "ic95_sup": f * r["ic95_sup"],
                "maior_aumento": f * r["ic95_sup"], "mde": f * r["mde"]}
        if "media_abaixo" in ref:
            lido["media_abaixo"] = f * r["media_abaixo"]
        for campo, v in lido.items():
            ok = abs(round(v, casas) - ref[campo]) <= tol
            itens.append({"linha": idl, "campo": campo, "doc57": ref[campo], "lido": round(float(v), 6), "confere": ok})
            if not ok:
                erros.append(f"{idl}.{campo}: doc 57 {ref[campo]} contra lido {v:.4f}")
    coer = []
    for idl, s in sel.items():
        r = s["linha"]
        lo, hi = r["tau"] - 1.959963984540054 * r["ep"], r["tau"] + 1.959963984540054 * r["ep"]
        d_ic = max(abs(lo - r["ic95_inf"]), abs(hi - r["ic95_sup"]))
        d_p = abs(L.p_normal(r["tau"] / r["ep"]) - r["p_valor"])
        coer.append({"linha": idl, "dif_ic95_normal": d_ic, "dif_p_normal": d_p})
        if d_ic > 1e-6 or d_p > 1e-6:
            erros.append(f"{idl}: IC 95% ou p gravados não são τ̂ ± 1,96·EP pela normal (dif {d_ic:.2e}, {d_p:.2e})")
        for tipo, h in s["honesto"].items():
            cv = L.cv_honesto(h["vies_max"] / h["ep"])
            d_h = max(abs(h["tau"] - cv * h["ep"] - h["ic95_inf"]), abs(h["tau"] + cv * h["ep"] - h["ic95_sup"]))
            d_tau = abs(h["tau"] - r["tau"])
            d_med = abs(h["media_abaixo"] - r["media_abaixo"])
            coer.append({"linha": idl, "ic": tipo, "dif_ic_honesto_reconstruido": d_h, "dif_tau": d_tau,
                         "dif_media": d_med})
            if d_h > 1e-6 * max(1.0, abs(h["ic95_sup"])) or d_tau > 1e-9 or d_med > 1e-12:
                erros.append(f"{idl} {tipo}: IC honesto, τ̂ ou média não conferem")
            if tipo == "honesto_M_x1":
                d_p = max(abs(h["ic95_inf"] - r["ic_honesto_inf"]), abs(h["ic95_sup"] - r["ic_honesto_sup"]))
                if d_p > 1e-9:
                    erros.append(f"{idl}: IC honesto da linha principal difere da S-g M×1")
    if erros:
        raise FalhaValidacao("conferência falhou; parar e relatar:\n  " + "\n  ".join(erros))
    return {"doc57": itens, "coerencia_interna": coer}


# ---------------------------------------------------------------------------
# 3. Contas
# ---------------------------------------------------------------------------

def linha_tost(idl: str, s: dict, tipo: str, h=None, nota_ic: str = "") -> dict:
    spec = next(x for x in LINHAS if x[0] == idl)
    _, oc, papel, pop, ciclo, corte, legivel = spec
    r = s["linha"]
    media = float(r["media_abaixo"])
    margem = MARGEM_A3 if oc == "A3" else FRACAO_N1 * media
    if h is None:
        tau, ep, b = float(r["tau"]), float(r["ep"]), 0.0
        ic95 = (float(r["ic95_inf"]), float(r["ic95_sup"]))
        esp, var = str(r["especificacao"]), str(r["variante"])
    else:
        tau, ep, b = float(h["tau"]), float(h["ep"]), float(h["vies_max"])
        ic95 = (float(h["ic95_inf"]), float(h["ic95_sup"]))
        esp, var = str(h["especificacao"]), str(h["variante"])
    t = tost(tau, ep, margem, b)
    return {
        "natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "id_linha": idl, "outcome": oc,
        "descricao_outcome": DESCRICAO[oc], "papel": papel if h is None else "sensibilidade_ic_honesto",
        "populacao": pop, "ciclo": ciclo, "corte": corte, "amostra": legivel, "tipo_ic": tipo, "nota_ic": nota_ic,
        "arquivo_origem": rotulo(NA_EST if oc == "A3" else N_EST), "especificacao_origem": esp,
        "variante_origem": var, "unidade": UNIDADE[oc], "n_abaixo": float(r["n_abaixo"]),
        "n_acima": float(r["n_acima"]), "tau": tau, "ep": ep, "vies_max": b, "ic95_inf": ic95[0],
        "ic95_sup": ic95[1], "media_abaixo": media, "margem": margem, "regra_margem": REGRA_MARGEM[oc], **t,
        "margem_minima_relativa_media": t["margem_minima"] / media, "entra_holm": False, "nota": "",
    }


def calcular(sel: dict) -> pd.DataFrame:
    linhas = []
    for idl, *_ in LINHAS:
        s = sel[idl]
        linhas.append(linha_tost(idl, s, "convencional_CR1",
                                 nota_ic="EP CR1 por município gravado pelo bloco; aproximação local linear sem "
                                         "correção de viés"))
        for var, tipo, nota in VARIANTES_HONESTAS:
            if tipo in s["honesto"]:
                linhas.append(linha_tost(idl, s, tipo, s["honesto"][tipo],
                                         nota_ic=f"IC honesto Armstrong–Kolesár gravado pelo bloco ({nota}); "
                                                 "TOST honesto unilateral com o viés máximo gravado"))
    est = pd.DataFrame(linhas)
    prim = (est["papel"] == "primaria") & (est["tipo_ic"] == "convencional_CR1")
    est["entra_holm"] = prim
    for c in ("aumento", "queda", "tost"):
        est[f"p_holm_{c}"] = np.nan
        est.loc[prim, f"p_holm_{c}"] = L.holm(est.loc[prim, f"p_{c}"].to_numpy())
    pa = np.where(prim, est["p_holm_aumento"], est["p_aumento"])
    pq = np.where(prim, est["p_holm_queda"], est["p_queda"])
    est["base_decisao"] = np.where(prim, "Holm entre as duas primárias (a 5%)",
                                   np.where(est["papel"] == "secundaria", "sem ajuste (secundária, a 5%)",
                                            "sem ajuste (sensibilidade, a 5%)"))
    est["rejeita_aumento"] = pa < ALFA
    est["rejeita_queda"] = pq < ALFA
    est["equivalente"] = est["rejeita_aumento"] & est["rejeita_queda"]
    # Holm do TOST e o par de Holm por direção levam à mesma decisão de equivalência (conferido).
    if not (est.loc[prim, "equivalente"] == (est.loc[prim, "p_holm_tost"] < ALFA)).all():
        raise FalhaValidacao("Holm do p do TOST e Holm por direção discordam na equivalência das primárias")
    est["leitura_codigo"] = [classificar(a, q) for a, q in zip(est["rejeita_aumento"], est["rejeita_queda"])]
    est["leitura"] = [LEITURAS[c].format(m=texto_margem(o, m, me)) for c, o, m, me in
                      zip(est["leitura_codigo"], est["outcome"], est["margem"], est["media_abaixo"])]
    est["nota"] = np.where(est["tipo_ic"] == "honesto_pos_resultado",
                           "POS_RESULTADO no bloco de origem (fora do protocolo 48); só registro", "")
    return est[COLUNAS]


# ---------------------------------------------------------------------------
# 4. Figura
# ---------------------------------------------------------------------------

def gerar_figura(est: pd.DataFrame, caminho: Path) -> dict:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    conv = est[est["tipo_ic"] == "convencional_CR1"]
    paineis = [("A3", "A3: célula aberta preenchida na 1ª chamada\n(salto em p.p.; faixa = ±10 p.p.)", 100.0, 10.0),
               ("N1", "N1: vagas preenchidas por município, com controle (S-a)\n(salto em % da média abaixo do corte;"
                      " faixa = ±25%)", None, 25.0)]
    alturas = [int((conv["outcome"] == oc).sum()) for oc, *_ in paineis]
    fig, axs = plt.subplots(2, 1, figsize=(8.2, 7.2), gridspec_kw={"height_ratios": alturas})
    tinta, sec, faixa, cor = "#1f1f1f", "#5c5c5c", "#d9d9d9", "#2a78d6"
    for ax, (oc, titulo, escala, m) in zip(axs, paineis):
        d = conv[conv["outcome"] == oc].reset_index(drop=True)
        k = 100.0 / d["media_abaixo"].to_numpy() if escala is None else np.full(len(d), escala)
        y = np.arange(len(d))[::-1]
        ax.axvspan(-m, m, color=faixa, alpha=0.6, lw=0, zorder=0)
        ax.axvline(0, color=sec, lw=0.8, zorder=1)
        lo, hi, tau = d["ic90_inf"] * k, d["ic90_sup"] * k, d["tau"] * k
        ax.hlines(y, lo, hi, color=cor, lw=2.2, zorder=2)
        ax.plot(tau, y, "o", color=cor, ms=6, mec="white", mew=1.2, zorder=3)
        rot = [("primária — " if p == "primaria" else "") + a for p, a in zip(d["papel"], d["amostra"])]
        ax.set_yticks(y)
        ax.set_yticklabels(rot, fontsize=8, color=tinta)
        for t, p in zip(ax.get_yticklabels(), d["papel"]):
            if p == "primaria":
                t.set_fontweight("bold")
        lim = max(m * 1.6, float(np.nanmax(np.abs(np.concatenate([lo, hi])))) * 1.08)
        ax.set_xlim(-lim, lim)
        ax.set_ylim(-0.7, len(d) - 0.3)
        ax.set_title(titulo, fontsize=9, color=tinta, loc="left")
        ax.tick_params(axis="x", labelsize=8, colors=sec)
        ax.grid(axis="x", color="#eeeeee", lw=0.6, zorder=0)
        for sp in ("top", "right", "left"):
            ax.spines[sp].set_visible(False)
        ax.spines["bottom"].set_color(sec)
    axs[-1].set_xlabel("salto no corte (lado de bolsa maior menos lado de bolsa menor); ponto = estimativa, "
                       "barra = IC 90%", fontsize=8, color=sec)
    fig.suptitle("Equivalência (TOST): o IC 90% cabe na faixa cinza?", fontsize=10, color=tinta, x=0.01, ha="left")
    fig.tight_layout()
    caminho.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(caminho, dpi=150, metadata={"Software": None})
    plt.close(fig)
    return {"arquivo": rotulo(caminho), "sha256": sha256(caminho)}


# ---------------------------------------------------------------------------
# 5. Documento 57j, só a partir de output/
# ---------------------------------------------------------------------------

def _n(v, casas=1, sinal=True) -> str:
    if v is None or not np.isfinite(v):
        return "—"
    s = f"{abs(v):,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    if round(abs(v), casas) == 0:
        return s
    return ("−" if v < 0 else "+" if sinal else "") + s


def _p(v) -> str:
    if v is None or not np.isfinite(v):
        return "—"
    return "< 0,001" if v < 0.001 else _n(v, 3, False)


def _sim(b) -> str:
    return "sim" if bool(b) else "não"


def bloco(nome: str, corpo: str) -> str:
    return f"<!-- EQ:{nome}:inicio -->\n{corpo}\n<!-- EQ:{nome}:fim -->"


def _val(r, col):
    """Valor na unidade de leitura: p.p. em A3; vagas por município em N1."""
    return 100.0 * r[col] if r["outcome"] == "A3" else r[col]


def _casas(r) -> int:
    return 1 if r["outcome"] == "A3" else 2


def _margem_txt(r) -> str:
    if r["outcome"] == "A3":
        return "±10 p.p."
    return f"±{_n(r['margem'], 2, False)} (25% de {_n(r['media_abaixo'], 2, False)})"


def _media_txt(r) -> str:
    return f"{_n(100 * r['media_abaixo'], 1, False)}%" if r["outcome"] == "A3" else _n(r["media_abaixo"], 2, False)


def _mm_txt(r) -> str:
    c = _casas(r)
    base = _n(_val(r, "margem_minima"), c, False)
    if r["outcome"] == "A3":
        return f"{base} p.p."
    return f"{base} ({_n(100 * r['margem_minima_relativa_media'], 0, False)}% da média)"


def tabela(est: pd.DataFrame, filtro) -> str:
    cab = ["Outcome", "Amostra", "Média abaixo", "Salto", "EP", "Margem", "IC 90%",
           "Aumento < margem? p (p Holm)", "Queda < margem? p (p Holm)", "Margem mínima", "Leitura"]
    out = ["| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)]
    for _, r in est[filtro].iterrows():
        c = _casas(r)
        un = " p.p." if r["outcome"] == "A3" else ""
        pa = _p(r["p_aumento"]) + (f" ({_p(r['p_holm_aumento'])})" if r["entra_holm"] else "")
        pq = _p(r["p_queda"]) + (f" ({_p(r['p_holm_queda'])})" if r["entra_holm"] else "")
        pa += " — rejeita" if r["rejeita_aumento"] else " — não rejeita"
        pq += " — rejeita" if r["rejeita_queda"] else " — não rejeita"
        out.append("| " + " | ".join([
            r["outcome"], r["amostra"], _media_txt(r), _n(_val(r, "tau"), c) + un, _n(_val(r, "ep"), c, False),
            _margem_txt(r), f"[{_n(_val(r, 'ic90_inf'), c)}; {_n(_val(r, 'ic90_sup'), c)}]", pa, pq, _mm_txt(r),
            {"EQUIVALENTE": "equivalência", "SO_AUMENTO": "só o aumento", "SO_QUEDA": "só a queda",
             "INCONCLUSIVO": "inconclusivo"}[r["leitura_codigo"]]]) + " |")
    return "\n".join(out)


def tabela_honesta(est: pd.DataFrame) -> str:
    cab = ["Amostra", "IC honesto", "Salto", "EP", "Viés máximo (B)", "Margem", "IC 90% (τ̂ ∓ (B + 1,645·EP))",
           "p aumento", "p queda", "Margem mínima", "Leitura"]
    out = ["| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)]
    nomes = {"honesto_M_x1": "M da regra do E6 (o do bloco)", "honesto_M_x0.5": "M × 0,5", "honesto_M_x2": "M × 2",
             "honesto_pos_resultado": "suporte pós-resultado"}
    for _, r in est[est["tipo_ic"] != "convencional_CR1"].iterrows():
        out.append("| " + " | ".join([
            r["amostra"], nomes[r["tipo_ic"]], _n(r["tau"], 2), _n(r["ep"], 2, False), _n(r["vies_max"], 2, False),
            _margem_txt(r), f"[{_n(r['ic90_inf'], 2)}; {_n(r['ic90_sup'], 2)}]", _p(r["p_aumento"]),
            _p(r["p_queda"]), _mm_txt(r),
            {"EQUIVALENTE": "equivalência", "SO_AUMENTO": "só o aumento", "SO_QUEDA": "só a queda",
             "INCONCLUSIVO": "inconclusivo"}[r["leitura_codigo"]]]) + " |")
    return "\n".join(out)


def _frase(r) -> str:
    c = _casas(r)
    un = " p.p." if r["outcome"] == "A3" else (" vaga por município" if r["outcome"] == "N1" else "")
    m = texto_margem(r["outcome"], r["margem"], r["media_abaixo"])
    ic = f"[{_n(_val(r, 'ic90_inf'), c)}; {_n(_val(r, 'ic90_sup'), c)}]"
    base = (f"salto {_n(_val(r, 'tau'), c)}{un}, IC 90% {ic}, margem ±{m}, margem mínima de equivalência "
            f"{_mm_txt(r)}")
    cod = r["leitura_codigo"]
    if cod == "EQUIVALENTE":
        txt = (f"os dois testes rejeitam; o salto está dentro de ±{m}: não mudou além disso, para o pacote do corte "
               "e sob a aproximação local linear")
    elif cod == "SO_AUMENTO":
        txt = f"só o teste do aumento rejeita; não houve aumento de {m} ou mais, mas uma queda de {m} não fica descartada"
    elif cod == "SO_QUEDA":
        txt = f"só o teste da queda rejeita; não houve queda de {m} ou mais, mas um aumento de {m} não fica descartado"
    else:
        txt = "nenhum teste rejeita; inconclusivo"
    return f"{base} — **leitura:** {txt}."


def leitura(est: pd.DataFrame) -> str:
    conv = est[est["tipo_ic"] == "convencional_CR1"].set_index("id_linha")
    a3, n1 = conv.loc["A3-emp-123"], conv.loc["N1-emp-123"]
    linhas = [
        "**Primárias (Holm entre as duas).**",
        "",
        f"- **A3, preenchimento da célula aberta (ciclos 1–3, cortes empilhados):** {_frase(a3)}",
        f"- **N1, vagas preenchidas por município com controle das vagas oferecidas (ciclos 1–3, cortes "
        f"empilhados):** {_frase(n1)}",
    ]
    if n1["tau"] < -n1["margem"]:
        linhas.append(f"  - A estimativa pontual de N1 ({_n(n1['tau'], 2)}, {_n(100 * n1['tau'] / n1['media_abaixo'], 0)}% "
                      "da média) já fica abaixo de −25%. O teste da queda não rejeita, mas isso não é evidência de "
                      "queda: o teste de zero do bloco não rejeita depois do Holm (doc 49, §3), e o sinal negativo vem "
                      "em boa parte do corte de 0,300 no ciclo 2, onde o placebo acusa forma não linear (doc 49, §9).")
    linhas += ["", "**Secundárias (sem ajuste).**", ""]
    for idl in [x[0] for x in LINHAS if x[2] == "secundaria"]:
        r = conv.loc[idl]
        linhas.append(f"- **{r['outcome']}, {r['amostra']}:** {_frase(r)}")
    hon = est[(est["tipo_ic"] == "honesto_M_x1")]
    if len(hon):
        bmin = float(hon["vies_max"].min())
        n_rej = int((hon["rejeita_aumento"] | hon["rejeita_queda"]).sum())
        nao_cabe = bool((hon["vies_max"] > hon["margem"]).all())
        linhas += ["", "**IC honesto (N1).** Com o viés máximo da regra do E6 gravado pelo bloco, "
                   + (f"nenhum dos dois testes rejeita em nenhuma das {len(hon)} linhas de N1"
                      if n_rej == 0 else f"{n_rej} de {len(hon)} linhas de N1 rejeitam algum dos testes")
                   + (f": o viés máximo (B ≥ {_n(bmin, 1, False)} vagas por município) já é maior que a margem, e "
                      "nenhum IC honesto cabe nela" if nao_cabe else "")
                   + ". O doc 49 (§3, motivo ii) já registrava que esse IC é largo demais para informar. Ele não muda "
                   "a leitura do IC convencional, mas mostra que ela vale sob a aproximação local linear. A3 não tem IC "
                   "honesto gravado (o bloco não o calculou)."]
    n_eq = int(conv["equivalente"].sum())
    p = conv[conv["papel"] == "primaria"]
    if n_eq == 0 and (p["leitura_codigo"] == "SO_AUMENTO").all():
        frase = ("Nenhuma linha mostra equivalência. Nas duas primárias, os dados descartam um aumento do tamanho das "
                 "margens (+10 p.p. no preenchimento da célula; +25% da média nas vagas preenchidas; protocolo 60, "
                 "a partir das referências de magnitude do protocolo 40): não houve aumento desse tamanho ou mais. "
                 "Mas não permitem dizer que \"não mudou nada\", porque uma queda do mesmo tamanho não fica "
                 "descartada.")
    else:
        cont = conv["leitura_codigo"].value_counts()
        frase = ("Contagem das leituras no IC convencional: "
                 + "; ".join(f"{k}: {int(v)}" for k, v in sorted(cont.items())) + ". Primárias: "
                 + "; ".join(f"{r['outcome']} {r['leitura']}" for _, r in p.iterrows()) + ".")
    linhas += ["", "**Em uma frase.** " + frase + " É o pacote do corte, não a bolsa isolada, e nada aqui diz que a "
               "bolsa \"funciona\" ou \"não funciona\"."]
    return "\n".join(linhas)


def gerar_doc(est: pd.DataFrame, resumo: dict) -> str:
    conf = resumo["conferencia"]
    n_itens = len(conf["doc57"])
    cab = f"""# 57j. Resultados do protocolo 60, parte A: equivalência no preenchimento (H1)

> **Gerado por** `scripts/rdd_bolsa/36_equivalencia_H1.py --atualizar-doc` a partir de `output/rdd_bolsa/EQ_*`; não editar à mão (o teste `tests/test_equivalencia_H1.py` confere que este arquivo é igual ao gerado).<br>
> **Protocolo:** [`60_protocolo_equivalencia_e_oferta_local.md`](60_protocolo_equivalencia_e_oferta_local.md), parte A, congelado em 26/10/2026 (commit `{COMMIT_CONGELAMENTO}`) antes de calcular; estatuto `{ESTATUTO}`.<br>
> **O que já tinha sido visto:** as estimativas pontuais e os IC 95% de A3 e N1 (docs 49 e 57). Pelos IC publicados, o resultado era previsível em boa parte; este bloco só faz o teste formal de equivalência com margens fixadas antes.<br>
> **Saídas:** `output/rdd_bolsa/EQ_estimativas.csv`, `EQ_resumo.json` e `EQ_figuras/{NOME_FIG}`; toda linha tem `natureza_dos_dados = EMPIRICO`. Nada é reestimado e nenhuma saída anterior é regravada."""
    s1 = """## 1. O que se testa

**Pergunta (H1).** Os dados permitem dizer que o salto no corte de IVS (0,300 e 0,400, lado de bolsa maior menos lado de bolsa menor) está dentro de uma margem pequena, nos dois sentidos? Ou só que não houve um aumento grande?

**Por que um teste novo.** Um IC 95% que contém zero não quer dizer "não mudou nada": quer dizer só que zero é compatível com os dados, como também podem ser valores grandes. O teste de equivalência (TOST, dois testes unilaterais) inverte a pergunta: a hipótese nula é "o salto é grande" e só se rejeita se os dados descartarem um salto grande.

**Margens** (protocolo 60, a partir das referências de magnitude do protocolo 40, §1 e §7):

| Outcome | O que mede | Margem de equivalência |
|---|---|---|
| A3 | probabilidade de a célula aberta ser preenchida na 1ª chamada (unidade: célula do quadro) | ±10 p.p. |
| N1 | vagas preenchidas na 1ª chamada por município, com controle linear das vagas oferecidas (S-a) | ±25% da média abaixo do corte na mesma amostra |

**Os dois testes, a 5% cada:**
- **teste do aumento** — H0: o salto é +margem ou mais. Rejeitar quer dizer "não houve aumento do tamanho da margem ou mais";
- **teste da queda** — H0: o salto é −margem ou menos. Rejeitar quer dizer "não houve queda do tamanho da margem ou mais".

Rejeitar os dois equivale a o IC 90% inteiro ficar dentro da margem. A **margem mínima de equivalência** é o menor m tal que o IC 90% fica em [−m; +m]: diz o que os dados conseguem afirmar (descritiva).

**Linhas.** Primárias, com Holm entre as duas: A3 empilhado (ciclos 1–3, cortes empilhados) e N1 empilhado. Secundárias, sem ajuste: A3 por corte nos ciclos 1–3 e A3 no ciclo 1 (por corte e empilhado), que são as outras cinco linhas de preenchimento do doc 57, §4.2; N1 por corte. No ciclo 1, a faixa saiu depois do pedido dos gestores (doc 57, §4.2).

**Contas.** Com a estimativa τ̂ e o EP gravados pelo bloco (CR1 por município), p do aumento = Φ((τ̂ − m)/EP) e p da queda = Φ((−m − τ̂)/EP), pela normal, como o bloco calcula o p. O Holm é aplicado, entre as duas primárias, ao p de cada teste e ao p do TOST (o maior dos dois); as duas formas dão a mesma decisão de equivalência (conferido no script).

**IC honesto.** Onde o bloco gravou o IC honesto (Armstrong–Kolesár, regra do E6; só em N1), o TOST é refeito com o viés máximo B gravado: p do aumento = Φ((τ̂ − m + B)/EP) e p da queda = Φ((−m − τ̂ + B)/EP), e o IC 90% correspondente é τ̂ ∓ (B + 1,645·EP). A3 não tem IC honesto gravado.

**Leitura pré-registrada** (protocolo 60):

| Resultado do TOST | O que se pode dizer |
|---|---|
| os dois testes rejeitam | o salto está dentro de ±margem: "não mudou além de X", para o pacote do corte e sob a aproximação local linear |
| só o teste do aumento rejeita | "não houve aumento de X ou mais", mas uma queda de X não fica descartada |
| nenhum rejeita | inconclusivo |

O caso "só o teste da queda rejeita", que o protocolo não lista, é lido como o espelho: "não houve queda de X ou mais", mas um aumento de X não fica descartado.

**Conferência dos insumos.** Antes de calcular, o script confere que os valores lidos de `NA_estimativas.csv` e `N_estimativas.csv` reproduzem os números citados no doc 57 (as seis linhas de preenchimento de A3 do §4.2 e a linha de N1 do §4.1, onde o §4.2 não a traz), que o IC 95% e o p gravados são τ̂ ± 1,96·EP pela normal e que o IC honesto gravado se reconstrói do viés máximo e do EP. Se algo não conferir, o script para."""
    conf_txt = ("Resultado da conferência: "
                f"{sum(i['confere'] for i in conf['doc57'])} de {n_itens} números do doc 57 reproduzidos na casa "
                "decimal publicada; IC 95% e p gravados iguais a τ̂ ± 1,96·EP pela normal e IC honesto gravado "
                "reconstruído do viés máximo e do EP (diferença ≤ 1e−6).")
    prim = (est["papel"] == "primaria")
    sec = (est["papel"] == "secundaria")
    s2 = ("## 2. Tabela\n\nSalto = lado de bolsa maior menos lado de bolsa menor. A3 em p.p.; N1 em vagas por "
          "município. \"Aumento < margem?\" é o teste do aumento (H0: salto ≥ +margem); \"Queda < margem?\" é o teste "
          "da queda (H0: salto ≤ −margem); \"rejeita\" é a 5%, com o p de Holm nas primárias e o p sem ajuste nas "
          "secundárias. Margem mínima = menor m com o IC 90% dentro de [−m; +m].\n\n### 2.1 Primárias\n\n"
          + bloco("primarias", tabela(est, prim)) + "\n\n### 2.2 Secundárias\n\n"
          + bloco("secundarias", tabela(est, sec)) + "\n\n### 2.3 TOST com o IC honesto (N1)\n\n"
          "O bloco gravou quatro variantes do IC honesto de N1; a do protocolo 48 é a regra do E6 (a que vai na "
          "linha principal de `N_estimativas.csv`). As outras ficam como registro; a de suporte pós-resultado é "
          "POS_RESULTADO no bloco de origem.\n\n" + bloco("honesto", tabela_honesta(est)) + "\n\n"
          + bloco("conferencia", conf_txt))
    s3 = ("## 3. Leitura em linguagem simples\n\nPela leitura pré-registrada do protocolo 60.\n\n"
          + bloco("leitura", leitura(est)))
    fig_rel = f"../../output/rdd_bolsa/EQ_figuras/{NOME_FIG}"
    s4 = f"""## 4. Figura

![IC 90% contra a faixa de ±margem]({fig_rel})

**Como ler.**
- Cada linha é uma amostra. O ponto é o salto estimado no corte; a barra azul é o IC 90%.
- A faixa cinza é a margem de equivalência: ±10 p.p. em A3 (painel de cima) e ±25% da média abaixo do corte em N1 (painel de baixo; ali o salto e o IC estão divididos pela média abaixo do corte da mesma amostra, para que a faixa seja a mesma em todas as linhas).
- **Barra inteira dentro da faixa:** equivalência. Não mudou além da margem, para o pacote do corte.
- **Barra que passa da faixa só do lado esquerdo:** não houve aumento do tamanho da margem ou mais, mas uma queda desse tamanho não fica descartada.
- **Barra que passa dos dois lados:** inconclusivo.
- A barra é o IC 90% (não o de 95% dos docs 49 e 57) porque cada um dos dois testes é a 5% num só sentido.
- As linhas em negrito são as primárias. A figura usa o IC convencional; o IC honesto de N1 é tão largo que não caberia na escala (tabela 2.3)."""
    s5 = """## 5. Limites

- **Pacote do corte.** Em 0,300 e 0,400 mudam também outras regras federais (auditoria 18). O salto mede o pacote: a bolsa anunciada maior e as outras regras juntas. Não é o efeito isolado dos R$ 5 mil nem da participação no PMM-E.
- **Aproximação local linear.** O IC convencional supõe que a reta local capta a forma do outcome perto do corte. O IC honesto, onde existe (N1), não permite afirmar equivalência nem descartar aumento: com o M da regra do E6, o viés máximo é muitas vezes a margem. A conclusão "não houve aumento de X ou mais" vale sob a aproximação local linear.
- **Pós-resultado.** As margens foram fixadas depois de ver as estimativas e os IC 95% (docs 49 e 57); o resultado era em boa parte previsível pelos IC publicados. O teste é formal, mas não é confirmatório.
- **Seleção.** A3 é condicional à célula aberta, e a abertura de vagas pode responder ao corte (doc 49, §15); N1 controla as vagas oferecidas, que são decididas antes do preenchimento.
- **Primeira chamada.** Preenchimento na 1ª chamada não é presença do médico, permanência nem oferta líquida local.
- **Linguagem.** Nenhum resultado aqui diz que a bolsa "funciona" ou "não funciona". "Não houve aumento de X ou mais" só vale onde o teste do aumento rejeita; equivalência só onde os dois testes rejeitam."""
    ent = "\n".join(f"| `{e['caminho']}` | {e['papel']} | `{e['sha256'][:16]}…` |" for e in resumo["entradas"])
    s6 = ("## 6. Proveniência e reprodução\n\n" + bloco("proveniencia",
          "| Arquivo | Papel | SHA-256 |\n|---|---|---|\n" + ent + "\n\n"
          f"Protocolo: SHA-256 do texto atual `{resumo['protocolo']['sha256_texto'][:16]}…`; do texto congelado "
          f"(commit `{COMMIT_CONGELAMENTO}`) `{SHA_PROTOCOLO_CONGELADO[:16]}…`.")
          + "\n\n```\npython3 scripts/rdd_bolsa/36_equivalencia_H1.py --atualizar-doc\n"
          "python3 -m unittest tests/test_equivalencia_H1.py\n```")
    return "\n\n".join([cab, s1, s2, s3, s4, s5, s6]) + "\n"


def ler_saidas() -> tuple[pd.DataFrame, dict]:
    est = pd.read_csv(OUT / NOME_EST, dtype={"ciclo": str, "corte": str})
    res = json.loads((OUT / NOME_RESUMO).read_text(encoding="utf-8"))
    return est, res


def atualizar_doc() -> None:
    est, res = ler_saidas()
    DOC.write_text(gerar_doc(est, res), encoding="utf-8")


# ---------------------------------------------------------------------------
# 6. Execução
# ---------------------------------------------------------------------------

DECISOES = [
    {"item": "secundárias de A3", "decisao": "\"A3 por corte e no ciclo 1\" = as cinco outras linhas de preenchimento "
     "da tabela do doc 57, §4.2: ciclos 1–3 por corte (0,300 e 0,400) e ciclo 1 por corte e empilhado"},
    {"item": "conferência de N1", "decisao": "o doc 57, §4.2 não traz N1; a conferência de N1 usa a linha do §4.1 "
     "(mesma síntese), e a de A3 o §4.2"},
    {"item": "Holm", "decisao": "entre as duas primárias, aplicado ao p de cada teste unilateral e ao p do TOST; a "
     "decisão de equivalência é a mesma pelas duas vias (conferido)"},
    {"item": "IC honesto", "decisao": "TOST honesto unilateral com o viés máximo gravado: IC 90% = τ̂ ∓ (B + "
     "1,645·EP); a variante do protocolo 48 (M da regra do E6) é a principal, as outras três ficam como registro; "
     "sem Holm (A3 não tem IC honesto)"},
    {"item": "caso só-queda", "decisao": "não listado no protocolo; lido como o espelho do só-aumento"},
]


def entradas() -> list[dict]:
    lista = [(PROTOCOLO_MD, "protocolo congelado (parte A)"), (PROTOCOLO_40, "referências de magnitude (§7)"),
             (NA_EST, "A3 (script 24, adendo §7 do protocolo 48)"), (N_EST, "N1 S-a e IC honesto (script 23)"),
             (DOC57, "conferência dos números citados (§4.1 e §4.2)")]
    return [{"caminho": rotulo(p), "sha256": sha256(p), "papel": papel} for p, papel in lista]


def executar(atualizar: bool) -> int:
    for p in (NA_EST, N_EST, DOC57, PROTOCOLO_MD):
        if not p.exists():
            raise SystemExit(f"{rotulo(p)} ausente")
    na = pd.read_csv(NA_EST, dtype={"ciclo": str, "corte": str})
    n = pd.read_csv(N_EST, dtype={"ciclo": str, "corte": str})
    sel = selecionar(na, n)
    conf = conferir(sel, ler_doc57(DOC57.read_text(encoding="utf-8")))
    est = calcular(sel)
    OUT.mkdir(parents=True, exist_ok=True)
    est.to_csv(OUT / NOME_EST, index=False, float_format="%.10g")
    fig = gerar_figura(est, DIR_FIG / NOME_FIG)
    conv = est[est["tipo_ic"] == "convencional_CR1"]
    resumo = {
        "etapa": "EQ_equivalencia_H1", "natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO,
        "gerador": rotulo(Path(__file__)), "data_execucao": DATA_EXECUCAO,
        "protocolo": {"texto": rotulo(PROTOCOLO_MD), "secao": "Parte A", "sha256_texto": sha256(PROTOCOLO_MD),
                      "sha256_texto_congelado": SHA_PROTOCOLO_CONGELADO, "commit_congelamento": COMMIT_CONGELAMENTO},
        "margens": {"A3": {"valor": MARGEM_A3, "unidade": "fração (±10 p.p.)"},
                    "N1": {"fracao_da_media_abaixo": FRACAO_N1, "media_abaixo": "gravada pelo bloco, mesma amostra"}},
        "metodo": {"teste": "TOST, dois testes unilaterais a 5% (IC 90%)", "alfa_unilateral": ALFA, "z": Z,
                   "p_aumento": "Φ((τ̂ − m + B)/EP)", "p_queda": "Φ((−m − τ̂ + B)/EP)",
                   "ic90": "τ̂ ∓ (B + z·EP)", "margem_minima": "|τ̂| + B + z·EP",
                   "B": "0 no IC convencional; viés máximo gravado no IC honesto",
                   "holm": "entre A3-emp-123 e N1-emp-123, em p_aumento, p_queda e p_tost",
                   "secundarias": "sem ajuste"},
        "conferencia": conf,
        "primarias": {r["id_linha"]: {k: r[k] for k in ("tau", "ep", "margem", "ic90_inf", "ic90_sup", "p_aumento",
                                                         "p_queda", "p_tost", "p_holm_aumento", "p_holm_queda",
                                                         "p_holm_tost", "rejeita_aumento", "rejeita_queda",
                                                         "equivalente", "leitura_codigo", "margem_minima")}
                      for _, r in conv[conv["papel"] == "primaria"].iterrows()},
        "contagem_leituras": {"convencional": conv["leitura_codigo"].value_counts().sort_index().to_dict(),
                              "honesto": est[est["tipo_ic"] != "convencional_CR1"]["leitura_codigo"]
                              .value_counts().sort_index().to_dict()},
        "linhas": int(len(est)),
        "saidas": {rotulo(OUT / NOME_EST): sha256(OUT / NOME_EST)},
        "figuras": [fig],
        "entradas": entradas(),
        "decisoes": DECISOES,
        "contraste": "pacote do corte (bolsa anunciada maior e outras regras federais nos mesmos cortes); não é o "
                     "incentivo marginal isolado nem a participação no PMM-E",
        "integridade": "lê só estimativas gravadas; nada reestimado, simulado ou imputado; o arquivo local de IVS "
                       "não é lido; nenhum CNES lido; saídas anteriores não regravadas",
    }
    gravar_json(OUT / NOME_RESUMO, resumo)
    if atualizar:
        atualizar_doc()
    for _, r in conv.iterrows():
        print(f"EQ {r['id_linha']}: IC90 [{r['ic90_inf']:.4f}; {r['ic90_sup']:.4f}], p aumento {r['p_aumento']:.4g}, "
              f"p queda {r['p_queda']:.4g}, margem mínima {r['margem_minima']:.4f} -> {r['leitura_codigo']}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--atualizar-doc", action="store_true", help="também regrava o doc 57j a partir de output/")
    args = ap.parse_args(argv)
    try:
        return executar(args.atualizar_doc)
    except FalhaValidacao as e:
        print(f"FALHA: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
