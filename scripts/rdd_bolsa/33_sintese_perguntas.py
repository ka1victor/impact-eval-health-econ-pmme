"""33 — Síntese das perguntas reformuladas (doc 57, onda 5 do doc 51).

Plano: `docs/06_execucao/51_plano_perguntas_reformuladas.md`, §5 (onda 5). Formato e regra de Holm
herdados da síntese anterior (`docs/06_execucao/44_sintese_rdd_bolsa_multioutcome.md`).

O que este script faz
---------------------
- Lê só saídas já auditadas em `output/` (P1, P3x, P4, P5, P6, realocação, T1.6, famílias N, NA e K,
  E6, E7, E8 e E9). Não estima nada de novo e não lê `data/`.
- Recalcula, com código próprio, o Holm de cada família de primárias definida nos protocolos (40, 47, 48,
  52, 58) e o da família do relato do P6 (protocolo 56), e o BKY de cada família de secundárias, a partir
  dos p gravados; compara com o que cada bloco gravou e lista as divergências, sem corrigir nada.
- Monta a tabela por pergunta, o quadro de poder (limite do IC e MDE de 80%) e a resposta à pergunta
  central do autor (os R$ 5 mil a mais aumentam a atração ou o preenchimento?), sempre como pacote do
  corte.
- Grava `output/rdd_bolsa/S57_resumo.json`, `S57_tabela_perguntas.csv`, `S57_multiplicidade.csv` e
  `S57_poder.csv` (natureza dos dados: EMPIRICO) e gera o doc 57 inteiro a partir do resumo.

Rastreio dos números
--------------------
Todo número do doc sai de um objeto de valor com a fonte (arquivo de `output/`, linha selecionada,
coluna e transformação declarada: ×100, ×5, exp, ×2,8) ou de uma conta derivada declarada (Holm, BKY,
diferença). O gerador do doc grava a lista `rastreio` (texto exibido → fonte) no resumo; o teste
refaz cada valor da fonte e confere o texto.

Falha fechada
-------------
Para se: uma entrada faltar ou não tiver o rótulo esperado; uma seleção não achar exatamente uma
linha; uma afirmação qualitativa do texto (força da evidência, IC que contém zero, falha de validação)
deixar de valer nos dados. Nesse caso o texto tem de ser revisto; o script não troca a redação sozinho.

Uso
---
    python3 scripts/rdd_bolsa/33_sintese_perguntas.py                 # saídas + doc 57
    python3 scripts/rdd_bolsa/33_sintese_perguntas.py --atualizar-doc # só regrava o doc a partir do resumo
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs" / "06_execucao" / "57_sintese_perguntas_reformuladas.md"
SAIDA = "output/rdd_bolsa"
NOME_RESUMO = "S57_resumo.json"
NOME_TABELA = "S57_tabela_perguntas.csv"
NOME_MULT = "S57_multiplicidade.csv"
NOME_PODER = "S57_poder.csv"
DATA_DOC = "24/10/2026"

# Parâmetros (não são resultados).
ALFA = 0.05
FATOR_MDE = 2.8          # MDE de 80% bilateral a 5% ≈ 2,8 × EP (regra dos blocos K, N e NA)
TOL_HOLM = 1e-6          # divergência de Holm: |recalculado − gravado| acima disto
TOL_BKY = 0.0011         # divergência de BKY: acima de um passo da grade de 0,001
LIMIAR_R_P1 = 0.10       # protocolo 58, §9: 10 p.p. por R$ 5 mil
LIMIAR_R_P2 = 0.25       # protocolo 58, §9: 0,25 candidato por R$ 5 mil

# Entradas (todas em output/).
E6 = "output/rdd_bolsa/E6_estimativas.csv"
E7 = "output/rdd_bolsa/E7_estimativas.csv"
E8R = "output/rdd_bolsa/E8_resumo.json"
E9M = "output/rdd_bolsa/E9_efeitos_marginais.csv"
P1E = "output/rdd_bolsa/P1_estimativas.csv"
P1R = "output/rdd_bolsa/P1_resumo.json"
NA = "output/rdd_bolsa/NA_estimativas.csv"
NE = "output/rdd_bolsa/N_estimativas.csv"
KD1 = "output/rdd_bolsa/K_D1_estimativas.csv"
KD2 = "output/rdd_bolsa/K_D2_estimativas.csv"
KX = "output/rdd_bolsa/K_X_estimativas.csv"
P4E = "output/rdd_bolsa/P4_estimativas.csv"
P4R = "output/rdd_bolsa/P4_resumo.json"
P5E = "output/rdd_bolsa/P5_estimativas.csv"
P5R = "output/rdd_bolsa/P5_resumo.json"
P6E = "output/rdd_bolsa/P6_estimativas.csv"
P6R = "output/rdd_bolsa/P6_resumo.json"
RE = "output/rdd_bolsa/R_estimativas.csv"
RR = "output/rdd_bolsa/R_resumo.json"
CENR = "output/cenarios/P1_cenarios_resumo.json"
CENV = "output/cenarios/P1_cenarios_validacao_base.csv"

ENTRADAS = [
    (E6, "E6: P1 (primária do protocolo 40), F1.1 e F1.3 empilhados; BKY de F0, F1, F2 e F4"),
    (E7, "E7: P2 (primária do protocolo 40), F3.1 por DiRD; BKY de F3"),
    (E8R, "E8: p de Holm gravados de P1 e P2 (protocolo 40)"),
    (E9M, "E9: razão de chances por +R$ 5 mil no ciclo 2"),
    (P1E, "P1 (protocolo 52): M1, M5, Holm de P1a e BKY de P1d–P1f"),
    (P1R, "P1: estatuto"),
    (NA, "NA (adendo §7 do protocolo 48): A3 por célula aberta, por corte e ciclo"),
    (NE, "N (protocolo 48): N1–N4 com Holm"),
    (KD1, "K D1 (protocolo 47): K1–K3 com Holm; BKY das secundárias"),
    (KD2, "K D2 (protocolo 47): chegada do especialista, ATT e pré-tendência"),
    (KX, "P3x (adendo §12 do protocolo 47): 12.2, 12.4, 12.5 e BKY do adendo"),
    (P4E, "P4 (protocolo 54): trajetória, origem, contabilidade líquida e BKY"),
    (P4R, "P4: estatuto"),
    (P5E, "P5 (protocolo 55): associações do IVS, T5.2 e BKY"),
    (P5R, "P5: estatuto"),
    (P6E, "P6 (protocolo 56): R1, BKY e Holm da família de 10 testes"),
    (P6R, "P6: estatuto"),
    (RE, "realocação (protocolo 58): principal, Holm e MDE"),
    (RR, "realocação: leitura pré-registrada"),
    (CENR, "T1.6: status da validação de base (só o status; nenhum número simulado é copiado)"),
    (CENV, "T1.6: linhas da validação de base (só o veredito por linha)"),
]

ESTATUTOS_ESPERADOS = {P1R: "PROTOCOLO_52_POS_RESULTADO", P4R: "EXPLORATORIO_P4", P5R: "PROTOCOLO_55_DESCRITIVO",
                       P6R: "EXPLORATORIO_P6"}


class FalhaFechada(RuntimeError):
    """Uma validação ou uma afirmação do texto não vale nos dados."""


def exigir(cond: bool, msg: str) -> None:
    if not cond:
        raise FalhaFechada(msg)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for bloco in iter(lambda: fh.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Leitura com fonte
# ---------------------------------------------------------------------------

_CSV: dict[str, pd.DataFrame] = {}
_JSON: dict[str, dict] = {}


def tabela(rel: str) -> pd.DataFrame:
    exigir(rel.startswith("output/"), f"entrada fora de output/: {rel}")
    if rel not in _CSV:
        p = ROOT / rel
        exigir(p.exists(), f"entrada ausente: {rel}")
        d = pd.read_csv(p, dtype=str, low_memory=False)
        if "natureza_dos_dados" in d.columns:
            esperado = "CENARIO_CONTRAFACTUAL" if rel.startswith("output/cenarios/") else "EMPIRICO"
            exigir(set(d["natureza_dos_dados"].dropna().unique()) == {esperado}, f"{rel}: rótulo diferente de {esperado}")
        _CSV[rel] = d
    return _CSV[rel]


def documento(rel: str) -> dict:
    exigir(rel.startswith("output/"), f"entrada fora de output/: {rel}")
    if rel not in _JSON:
        p = ROOT / rel
        exigir(p.exists(), f"entrada ausente: {rel}")
        d = json.loads(p.read_text(encoding="utf-8"))
        if "natureza_dos_dados" in d:
            esperado = "CENARIO_CONTRAFACTUAL" if rel.startswith("output/cenarios/") else "EMPIRICO"
            exigir(d["natureza_dos_dados"] == esperado, f"{rel}: rótulo diferente de {esperado}")
        _JSON[rel] = d
    return _JSON[rel]


def linha(rel: str, sel: dict) -> pd.Series:
    d = tabela(rel)
    if "__linha__" in sel:
        exigir(len(sel) == 1, "seleção por linha não aceita outros filtros")
        return d.iloc[int(sel["__linha__"])]
    m = np.ones(len(d), dtype=bool)
    for k, v in sel.items():
        exigir(k in d.columns, f"{rel}: coluna {k} ausente")
        m &= (d[k] == v).to_numpy()
    sub = d[m]
    exigir(len(sub) == 1, f"{rel} {sel}: esperada 1 linha, achadas {len(sub)}")
    return sub.iloc[0]


def aplicar(x: float, transf) -> float:
    for op in transf:
        if op[0] == "mul":
            x = x * float(op[1])
        elif op[0] == "exp":
            x = math.exp(x)
        else:
            raise ValueError(f"transformação desconhecida: {op}")
    return x


def V(rel: str, sel: dict, col: str, transf=()) -> dict:
    """Valor lido de um CSV de output/, com a fonte."""
    r = linha(rel, sel)
    exigir(col in r.index, f"{rel}: coluna {col} ausente")
    x = float(r[col])
    exigir(math.isfinite(x), f"{rel} {sel} {col}: valor ausente")
    t = [list(o) for o in transf]
    return {"v": aplicar(x, t), "arquivo": rel, "sel": dict(sel), "col": col, "transf": t}


def VJ(rel: str, caminho: list, transf=()) -> dict:
    """Valor lido de um JSON de output/, com a fonte."""
    obj = documento(rel)
    for k in caminho:
        obj = obj[k]
    t = [list(o) for o in transf]
    return {"v": aplicar(float(obj), t), "arquivo": rel, "caminho": list(caminho), "transf": t}


def VD(v: float, tipo: str, **ref) -> dict:
    """Valor derivado (Holm, BKY, diferença), refeito pelo teste."""
    return {"v": float(v), "derivado": tipo, **ref}


def sel_linhas(rel: str, filtro: dict) -> list[int]:
    d = tabela(rel)
    m = np.ones(len(d), dtype=bool)
    for k, v in filtro.items():
        m &= (d[k] == v).to_numpy()
    return [int(i) for i in np.flatnonzero(m)]


# ---------------------------------------------------------------------------
# Holm e BKY (código próprio; não importa a rdd_lib)
# ---------------------------------------------------------------------------

def holm(p) -> np.ndarray:
    p = np.asarray(p, dtype=float)
    m = len(p)
    ordem = np.argsort(p, kind="stable")
    adj = np.maximum.accumulate(np.minimum(1.0, (m - np.arange(m)) * p[ordem]))
    out = np.empty(m)
    out[ordem] = adj
    return out


def _bh_rejeicoes(p: np.ndarray, q: float) -> int:
    m = len(p)
    ordenado = np.sort(p)
    k = np.flatnonzero(ordenado <= q * np.arange(1, m + 1) / m)
    return 0 if len(k) == 0 else int(k.max()) + 1


def bky(p) -> np.ndarray:
    """q-valores aguçados de Benjamini, Krieger e Yekutieli (2006), grade de 0,001 (Anderson, 2008)."""
    p = np.asarray(p, dtype=float)
    m = len(p)
    out = np.ones(m)
    for i in range(1000, 0, -1):
        q = i / 1000
        q1 = q / (1 + q)
        r1 = _bh_rejeicoes(p, q1)
        if r1 == 0:
            continue
        r2 = m if r1 == m else _bh_rejeicoes(p, q1 * m / (m - r1))
        if r2 > 0:
            out[p <= np.sort(p)[r2 - 1]] = q
    return out


# ---------------------------------------------------------------------------
# Famílias
# ---------------------------------------------------------------------------

def _sel_e6(oid: str, pop: str, cic: str) -> dict:
    return {"outcome_id": oid, "populacao": pop, "ciclo": cic, "corte": "empilhado", "especificacao": "principal"}


SEL_E7_P2 = {"outcome_id": "F3.1", "populacao": "U", "corte": "empilhado", "especificacao": "principal"}

# Famílias de Holm: (id, protocolo, descrição, membros) — membros por CSV (filtro) ou explícitos.
FAMILIAS_HOLM_CSV = [
    ("H47", "47", "família K (D1): K1, K2 e K3, U, cortes empilhados", KD1, {"entra_holm": "True"},
     "p_valor", "p_holm", ("outcome_id",)),
    ("H48", "48", "família N: N1–N4 com controle das vagas oferecidas (S-a), empilhados", NE, {"entra_holm": "True"},
     "p_valor", "p_holm", ("outcome_id",)),
    ("H52", "52", "P1a: coeficiente da bolsa no M1 (família de um teste)", P1E, {"entra_holm": "True"},
     "p", "p_holm", ("modelo", "termo")),
    ("H58", "58", "realocação: R-P1 e R-P2 na principal", RE, {"especificacao": "PRINCIPAL", "outcome_id": "R_P1"},
     "p", "p_holm", ("outcome_id",)),
    ("H56", "56, relato", "P6: Y1–Y5 × último mês e média no R1 (Holm pedido no relato; o protocolo pede BKY)", P6E,
     {"entra_familia": "True"}, "p_valor", "p_holm", ("outcome", "medida")),
]

FAMILIAS_BKY = [
    ("B40-F0", "40", "E6, família F0 (implementação e seleção)", E6, {"familia": "F0", "entra_bky": "True"}, "p_valor", "q_bky"),
    ("B40-F1", "40", "E6, família F1 (atração)", E6, {"familia": "F1", "entra_bky": "True"}, "p_valor", "q_bky"),
    ("B40-F2", "40", "E6, família F2 (presença)", E6, {"familia": "F2", "entra_bky": "True"}, "p_valor", "q_bky"),
    ("B40-F4", "40", "E6, família F4 (seleção de quem chega)", E6, {"familia": "F4", "entra_bky": "True"}, "p_valor", "q_bky"),
    ("B40-F3", "40", "E7, família F3 (oferta no CNES)", E7, {"familia": "F3", "entra_bky": "True"}, "p_valor", "q_bky"),
    ("B47-K", "47", "K D1, secundárias", KD1, {"entra_bky": "True"}, "p_valor", "q_bky"),
    ("B47-12", "47 §12", "P3x, linhas principais do adendo", KX, {"entra_bky": "True"}, "p_valor", "q_bky"),
    ("B52", "52", "P1, secundárias P1d–P1f", P1E, {"entra_bky": "True"}, "p", "q_bky"),
    ("B54-T41b", "54", "P4, T4.1b (regra D1)", P4E, {"entra_bky": "True", "especificacao": "T4.1b", "regra_ligacao": "d1_pos_hoc"},
     "p_valor", "q_bky"),
    ("B54-T41c", "54", "P4, T4.1c (regra D1)", P4E, {"entra_bky": "True", "especificacao": "T4.1c", "regra_ligacao": "d1_pos_hoc"},
     "p_valor", "q_bky"),
    ("B54-T41b-lit", "54", "P4, T4.1b (regra literal, sensibilidade)", P4E,
     {"entra_bky": "True", "especificacao": "T4.1b", "regra_ligacao": "literal_doc45"}, "p_valor", "q_bky"),
    ("B54-T41c-lit", "54", "P4, T4.1c (regra literal, sensibilidade)", P4E,
     {"entra_bky": "True", "especificacao": "T4.1c", "regra_ligacao": "literal_doc45"}, "p_valor", "q_bky"),
    ("B55", "55", "P5, T5.2 (cortes, com e sem covariáveis)", P5E, {"entra_bky": "True"}, "p_valor", "q_bky"),
    ("B56", "56", "P6, Y1–Y5 no R1", P6E, {"entra_familia": "True"}, "p_valor", "q_bky"),
]


def familias_holm() -> list[dict]:
    fams = []
    # Protocolo 40: P1 (E6) e P2 (E7); gravado no E8.
    membros = [
        {"rotulo": "P1 índice de atração-presença (E6)",
         "p": V(E6, _sel_e6("P1", "V1+V2+V3", "1+2+3"), "p_valor"), "gravado": VJ(E8R, ["holm", "P1", "p_holm"])},
        {"rotulo": "P2 vínculos nas CBO-alvo por DiRD (E7)",
         "p": V(E7, SEL_E7_P2, "p_valor"), "gravado": VJ(E8R, ["holm", "P2", "p_holm"])},
    ]
    fams.append({"id": "H40", "protocolo": "40", "descricao": "rodada multi-outcome: P1 (E6) e P2 (E7)",
                 "membros": membros})
    for fid, prot, desc, rel, filtro, pcol, hcol, rotcols in FAMILIAS_HOLM_CSV:
        if fid == "H58":
            idx = sel_linhas(rel, {"especificacao": "PRINCIPAL"})
            idx = [i for i in idx if tabela(rel).iloc[i]["outcome_id"] in ("R_P1", "R_P2")]
        else:
            idx = sel_linhas(rel, filtro)
        exigir(len(idx) > 0, f"{fid}: família vazia")
        d = tabela(rel)
        membros = [{"rotulo": " · ".join(str(d.iloc[i][c]) for c in rotcols),
                    "p": V(rel, {"__linha__": i}, pcol), "gravado": V(rel, {"__linha__": i}, hcol)} for i in idx]
        fams.append({"id": fid, "protocolo": prot, "descricao": desc, "membros": membros})
    for f in fams:
        rec = holm([m["p"]["v"] for m in f["membros"]])
        for k, m in enumerate(f["membros"]):
            m["recalculado"] = VD(rec[k], "holm", familia=f["id"], indice=k)
            m["dif"] = VD(abs(rec[k] - m["gravado"]["v"]), "dif_holm", familia=f["id"], indice=k)
            m["rejeita_recalculado"] = bool(rec[k] < ALFA)
            m["rejeita_gravado"] = bool(m["gravado"]["v"] < ALFA)
    return fams


def familias_bky() -> list[dict]:
    fams = []
    for fid, prot, desc, rel, filtro, pcol, qcol in FAMILIAS_BKY:
        idx = sel_linhas(rel, filtro)
        exigir(len(idx) > 0, f"{fid}: família vazia")
        d = tabela(rel)
        p = np.array([float(d.iloc[i][pcol]) for i in idx])
        qg = np.array([float(d.iloc[i][qcol]) for i in idx])
        exigir(np.isfinite(p).all() and np.isfinite(qg).all(), f"{fid}: p ou q ausente")
        qr = bky(p)
        dif = np.abs(qr - qg)
        fams.append({"id": fid, "protocolo": prot, "descricao": desc, "arquivo": rel, "filtro": filtro,
                     "pcol": pcol, "qcol": qcol, "linhas": idx, "n": len(idx),
                     "n_q_gravado_menor_005": int((qg < ALFA).sum()), "n_q_recalculado_menor_005": int((qr < ALFA).sum()),
                     "max_dif": VD(float(dif.max()), "bky_max_dif", familia=fid),
                     "q_recalculado": [float(x) for x in qr], "q_gravado": [float(x) for x in qg]})
    return fams


def divergencias(fh: list[dict], fb: list[dict]) -> list[str]:
    out = []
    for f in fh:
        for m in f["membros"]:
            if m["dif"]["v"] > TOL_HOLM or m["rejeita_recalculado"] != m["rejeita_gravado"]:
                out.append(f"Holm {f['id']} ({m['rotulo']}): gravado {m['gravado']['v']:.6f}, "
                           f"recalculado {m['recalculado']['v']:.6f}")
    for f in fb:
        if f["max_dif"]["v"] > TOL_BKY or f["n_q_gravado_menor_005"] != f["n_q_recalculado_menor_005"]:
            out.append(f"BKY {f['id']}: maior diferença {f['max_dif']['v']:.4f}; q < 0,05 gravado "
                       f"{f['n_q_gravado_menor_005']}, recalculado {f['n_q_recalculado_menor_005']}")
    return out


# ---------------------------------------------------------------------------
# Valores nomeados
# ---------------------------------------------------------------------------

PP = (("mul", 100),)
RC5 = (("mul", 5), ("exp",))
MDE = (("mul", FATOR_MDE),)
MDE_PP = (("mul", FATOR_MDE), ("mul", 100))
MDE_RC5 = (("mul", FATOR_MDE * 5), ("exp",))


def _sel_a3(oid: str, pop: str, cic: str, corte: str) -> dict:
    return {"outcome_id": oid, "populacao": pop, "ciclo": cic, "corte": corte, "especificacao": "A3",
            "variante": "principal"}


def valores() -> dict:
    v: dict[str, dict] = {}
    # Protocolo 40.
    s = _sel_e6("P1", "V1+V2+V3", "1+2+3")
    for k, c in (("tau", "tau"), ("lo", "ic95_inf"), ("hi", "ic95_sup"), ("p", "p_valor")):
        v[f"e6_p1_{k}"] = V(E6, s, c)
    v["e6_p1_mde"] = V(E6, s, "ep", MDE)
    for k, c in (("tau", "tau"), ("lo", "ic95_inf"), ("hi", "ic95_sup"), ("p", "p_valor")):
        v[f"e7_p2_{k}"] = V(E7, SEL_E7_P2, c)
    v["e7_p2_mde"] = V(E7, SEL_E7_P2, "ep", MDE)
    v["e8_p1_holm"] = VJ(E8R, ["holm", "P1", "p_holm"])
    v["e8_p2_holm"] = VJ(E8R, ["holm", "P2", "p_holm"])
    s = _sel_e6("F1.1", "V1+V2+V3", "1+2+3")
    for k, c in (("tau", "tau"), ("lo", "ic95_inf"), ("hi", "ic95_sup")):
        v[f"f11_{k}"] = V(E6, s, c)
    v["f11_mde"] = V(E6, s, "ep", MDE)
    s = _sel_e6("F1.3", "V1+V2+V3", "1+2+3")
    for k, c in (("tau", "tau"), ("lo", "ic95_inf"), ("hi", "ic95_sup")):
        v[f"f13_{k}"] = V(E6, s, c, PP)
    # A3 (célula aberta) por corte.
    for oid, nome in (("A3_PREENCHIDA", "a3p"), ("A3_TEM_CAND_1A_OPCAO", "a3c")):
        for pop, cic, pn in (("V1+V2+V3 (celulas)", "1+2+3", "todos"), ("V1 (celulas)", "1", "c1")):
            for corte, cn in (("0.300", "300"), ("0.400", "400"), ("empilhado", "emp")):
                s = _sel_a3(oid, pop, cic, corte)
                b = f"{nome}_{pn}_{cn}"
                v[f"{b}_tau"] = V(NA, s, "tau", PP)
                v[f"{b}_lo"] = V(NA, s, "ic95_inf", PP)
                v[f"{b}_hi"] = V(NA, s, "ic95_sup", PP)
                v[f"{b}_mde"] = V(NA, s, "mde", PP)
                v[f"{b}_media"] = V(NA, s, "media_abaixo", PP)
                v[f"{b}_p"] = V(NA, s, "p_valor")
    # N.
    for n in ("N1", "N2", "N3", "N4"):
        s = {"outcome_id": n, "entra_holm": "True"}
        for k, c in (("tau", "tau"), ("lo", "ic95_inf"), ("hi", "ic95_sup"), ("mde", "mde"), ("p", "p_valor"),
                     ("holm", "p_holm")):
            v[f"n_{n}_{k}"] = V(NE, s, c)
    # P1.
    s = {"modelo": "M1", "ciclo": "empilhado", "termo": "bolsa_mil", "tipo_linha": "coeficiente"}
    v["m1_coef"] = V(P1E, s, "coef")
    v["m1_lo"] = V(P1E, s, "ic95_inf")
    v["m1_hi"] = V(P1E, s, "ic95_sup")
    v["m1_p"] = V(P1E, s, "p")
    v["m1_holm"] = V(P1E, s, "p_holm")
    v["m1_mde"] = V(P1E, s, "ep_cluster_conjunto", MDE)
    v["m1_rc"] = V(P1E, s, "coef", RC5)
    v["m1_rc_lo"] = V(P1E, s, "ic95_inf", RC5)
    v["m1_rc_hi"] = V(P1E, s, "ic95_sup", RC5)
    v["m1_rc_mde"] = V(P1E, s, "ep_cluster_conjunto", MDE_RC5)
    s = {"modelo": "M5", "ciclo": "2", "termo": "bolsa_mil", "tipo_linha": "coeficiente"}
    v["m5c2_rc"] = V(P1E, s, "coef", RC5)
    v["m5c2_rc_lo"] = V(P1E, s, "ic95_inf", RC5)
    v["m5c2_rc_hi"] = V(P1E, s, "ic95_sup", RC5)
    s = {"ciclo": "2", "modelo": "logit_condicional_1a_opcao", "conjunto": "principal",
         "especificacao": "spline_linear__bolsa_linear", "termo": "bolsa_mil", "quantidade": "razao_chances_por_5mil"}
    v["e9c2_rc"] = V(E9M, s, "estimativa")
    v["e9c2_rc_lo"] = V(E9M, s, "ic95_inf")
    v["e9c2_rc_hi"] = V(E9M, s, "ic95_sup")
    # K D1.
    for k_ in ("K1", "K2", "K3"):
        s = {"outcome_id": k_, "populacao": "U", "corte": "empilhado", "especificacao": "principal", "entra_holm": "True"}
        for k, c in (("tau", "tau"), ("lo", "ic95_inf"), ("hi", "ic95_sup"), ("mde", "mde"), ("p", "p_valor"),
                     ("holm", "p_holm"), ("media", "media_pre_abaixo")):
            v[f"kd1_{k_}_{k}"] = V(KD1, s, c)
    # K D2.
    for k_ in ("K1", "K2", "K4.vinculos"):
        s = {"outcome_id": k_, "variante": "principal", "estatistica": "att_pos_medio"}
        nm = k_.replace(".", "_")
        v[f"kd2_{nm}_att"] = V(KD2, s, "valor")
        v[f"kd2_{nm}_lo"] = V(KD2, s, "ic95_inf")
        v[f"kd2_{nm}_hi"] = V(KD2, s, "ic95_sup")
        v[f"kd2_{nm}_pre"] = V(KD2, {**s, "estatistica": "pretendencia_wald"}, "p_valor")
    # P3x.
    for nm, s in (("x122", {"item": "12.2", "outcome_id": "K_esp", "variante": "principal", "recorte": "todos_os_cursos"}),
                  ("x124", {"item": "12.4", "outcome_id": "K2r_tot", "desenho": "D2", "variante": "principal"}),
                  ("x125", {"item": "12.5", "outcome_id": "K1_reg", "variante": "principal"})):
        a = {**s, "estatistica": "att_pos_medio"}
        v[f"{nm}_att"] = V(KX, a, "valor")
        v[f"{nm}_lo"] = V(KX, a, "ic95_inf")
        v[f"{nm}_hi"] = V(KX, a, "ic95_sup")
        v[f"{nm}_pre"] = V(KX, {**s, "estatistica": "pretendencia_wald"}, "p_valor")
    # P4.
    base4 = {"especificacao": "T4.1b", "regra_ligacao": "d1_pos_hoc", "amostra": "completa", "janela": "[-6,6]",
             "grupo": "ciclos 1 e 2"}
    for o, nm in (("horas_totais", "ht"), ("horas_mun_posto", "hm"), ("horas_fora_mun_posto", "hf"),
                  ("horas_nao_sus", "hn")):
        s = {**base4, "outcome": o, "medida": "att_pos_medio"}
        v[f"p4_{nm}_att"] = V(P4E, s, "estimativa")
        v[f"p4_{nm}_lo"] = V(P4E, s, "ic95_inf")
        v[f"p4_{nm}_hi"] = V(P4E, s, "ic95_sup")
        v[f"p4_{nm}_pre"] = V(P4E, {**base4, "outcome": o, "medida": "wald_pre"}, "p_valor")
    s = {"especificacao": "origem", "regra_ligacao": "d1_pos_hoc", "grupo_tipo": "todos",
         "outcome": "fracao_ja_no_municipio_x1b"}
    v["p4_origem"] = V(P4E, s, "estimativa", PP)
    v["p4_origem_lo"] = V(P4E, s, "ic95_inf", PP)
    v["p4_origem_hi"] = V(P4E, s, "ic95_sup", PP)
    s = {"especificacao": "T4.3", "regra_ligacao": "d1_pos_hoc", "amostra": "completa", "grupo": "ciclos 1 e 2",
         "outcome": "fracao_do_ganho_compensada_fora"}
    v["p4_comp"] = V(P4E, s, "estimativa", PP)
    v["p4_comp_lo"] = V(P4E, s, "ic95_inf", PP)
    v["p4_comp_hi"] = V(P4E, s, "ic95_sup", PP)
    s = {"especificacao": "T4.2", "regra_ligacao": "d1_pos_hoc", "outcome": "delta_horas_na_origem"}
    v["p4_origem_delta"] = V(P4E, s, "estimativa")
    v["p4_origem_delta_lo"] = V(P4E, s, "ic95_inf")
    v["p4_origem_delta_hi"] = V(P4E, s, "ic95_sup")
    # P5.
    for nm, et, o in (("e1", "E1", "pedida"), ("e2", "E2", "priorizada")):
        s = {"especificacao": "T5.1c", "etapa": et, "outcome": o, "variante": "principal", "termo": "ivs"}
        v[f"p5_ivs_{nm}"] = V(P5E, s, "estimativa_por_dp", PP)
        v[f"p5_ivs_{nm}_lo"] = V(P5E, s, "ic95_inf_por_dp", PP)
        v[f"p5_ivs_{nm}_hi"] = V(P5E, s, "ic95_sup_por_dp", PP)
    s = {"especificacao": "T5.2a", "unidade_analise": "celula", "outcome": "E1_pedida", "corte": "empilhado"}
    v["p5_ped"] = V(P5E, s, "estimativa", PP)
    v["p5_ped_lo"] = V(P5E, s, "ic95_inf", PP)
    v["p5_ped_hi"] = V(P5E, s, "ic95_sup", PP)
    v["p5_ped_q"] = V(P5E, s, "q_bky")
    s = {"especificacao": "T5.2a", "unidade_analise": "celula", "outcome": "E2_priorizada", "corte": "empilhado"}
    v["p5_pri"] = V(P5E, s, "estimativa", PP)
    v["p5_pri_lo"] = V(P5E, s, "ic95_inf", PP)
    v["p5_pri_hi"] = V(P5E, s, "ic95_sup", PP)
    # P6.
    for o, nm in (("y1_vinculo_mun_1a_opcao", "y1"), ("y2_horas_sus", "y2"), ("y3_horas_totais", "y3"),
                  ("y4_vinculo_fora_origem", "y4"), ("y5_n_municipios", "y5")):
        for med in ("ultimo", "media"):
            s = {"entra_familia": "True", "outcome": o, "medida": med}
            b = f"p6_{nm}_{med}"
            for k, c in (("est", "estimativa"), ("lo", "ic95_inf"), ("hi", "ic95_sup"), ("p", "p_valor"),
                         ("q", "q_bky"), ("holm", "p_holm")):
                v[f"{b}_{k}"] = V(P6E, s, c)
            v[f"{b}_mde"] = V(P6E, s, "ep", MDE)
    # Realocação.
    for r_ in ("R_P1", "R_P2"):
        s = {"especificacao": "PRINCIPAL", "outcome_id": r_}
        t = PP if r_ == "R_P1" else ()
        v[f"{r_}_c5"] = V(RE, s, "coef_por_5mil", t)
        v[f"{r_}_lo"] = V(RE, s, "ic95_inf_5mil", t)
        v[f"{r_}_hi"] = V(RE, s, "ic95_sup_5mil", t)
        v[f"{r_}_mde"] = V(RE, s, "mde_por_5mil", t)
        v[f"{r_}_p"] = V(RE, s, "p")
        v[f"{r_}_holm"] = V(RE, s, "p_holm")
    return v


# ---------------------------------------------------------------------------
# Afirmações qualitativas (falha fechada)
# ---------------------------------------------------------------------------

def _contem_zero(v: dict, lo: str, hi: str) -> bool:
    return v[lo]["v"] <= 0 <= v[hi]["v"]


def checar_afirmacoes(v: dict, fh: list[dict]) -> dict:
    a = {}
    # P1: M1 com IC que contém zero (inconclusivo).
    exigir(_contem_zero(v, "m1_lo", "m1_hi"), "P1: o IC do M1 deixou de conter zero; revisar a força da evidência")
    exigir(v["e9c2_rc_lo"]["v"] > 1, "E9 ciclo 2: o IC deixou de excluir 1")
    # P2: A3 empilhado contém zero; nenhum Holm de N rejeita.
    for pn in ("todos", "c1"):
        for cn in ("300", "400", "emp"):
            exigir(_contem_zero(v, f"a3p_{pn}_{cn}_lo", f"a3p_{pn}_{cn}_hi"), f"A3 {pn} {cn}: IC deixou de conter zero")
            exigir(_contem_zero(v, f"a3c_{pn}_{cn}_lo", f"a3c_{pn}_{cn}_hi"), f"A3 cand {pn} {cn}: IC deixou de conter zero")
    exigir(_contem_zero(v, "f11_lo", "f11_hi"), "F1.1: IC deixou de conter zero")
    rej = {f["id"]: [m["rotulo"] for m in f["membros"] if m["rejeita_recalculado"]] for f in fh}
    for fid in ("H40", "H47", "H48", "H52", "H58"):
        exigir(rej[fid] == [], f"{fid}: alguma primária rejeita depois do Holm; revisar o texto")
    exigir(len(rej["H56"]) > 0 and all(r.startswith("y1_") for r in rej["H56"]),
           "H56: o que rejeita depois do Holm deixou de ser só o Y1")
    a["rejeitam_holm"] = rej
    # P3 D1: K1–K3 com IC que contém zero.
    for k_ in ("K1", "K2", "K3"):
        exigir(_contem_zero(v, f"kd1_{k_}_lo", f"kd1_{k_}_hi"), f"K D1 {k_}: IC deixou de conter zero")
    # P3 D2 e P3x: pré falhando em parte.
    exigir(v["x122_pre"]["v"] < ALFA, "12.2: o pré deixou de rejeitar; revisar a força")
    exigir(v["kd2_K2_pre"]["v"] < ALFA, "K2 D2: o pré deixou de rejeitar")
    exigir(v["x125_pre"]["v"] < ALFA, "12.5: o pré deixou de rejeitar")
    exigir(_contem_zero(v, "kd2_K1_lo", "kd2_K1_hi"), "K1 D2: IC deixou de conter zero")
    # P4: pré falhando nas horas no município do posto; horas totais com pré plano.
    exigir(v["p4_hm_pre"]["v"] < ALFA, "P4: o pré das horas no município do posto deixou de rejeitar")
    exigir(v["p4_ht_pre"]["v"] >= ALFA, "P4: o pré das horas totais passou a rejeitar")
    # Estatutos.
    for rel, est in ESTATUTOS_ESPERADOS.items():
        exigir(documento(rel).get("estatuto") == est, f"{rel}: estatuto diferente de {est}")
    # Realocação: leitura pré-registrada inconclusiva.
    for r_, lim in (("R_P1", LIMIAR_R_P1 * 100), ("R_P2", LIMIAR_R_P2)):
        exigir(documento(RR)["leitura"][r_]["classe"] == "INCONCLUSIVO", f"{r_}: leitura deixou de ser inconclusiva")
        exigir(_contem_zero(v, f"{r_}_lo", f"{r_}_hi") and v[f"{r_}_mde"]["v"] > lim, f"{r_}: regra do inconclusivo")
    # T1.6: falha de validação.
    cen = documento(CENR)
    exigir(cen.get("status") == "FALHA_VALIDACAO_BASE" and cen["validacao_base"]["passou"] is False,
           "T1.6: status diferente de FALHA_VALIDACAO_BASE")
    cv = tabela(CENV)
    falhas = cv[cv["passa"] != "True"]
    exigir(len(falhas) >= 1, "T1.6: nenhuma linha reprovada na validação")
    a["t16_falhas"] = [f"ciclo {r['ciclo']}, {r['faixa'].lower()}" for _, r in falhas.iterrows()]
    a["t16_linhas"] = int(len(cv))
    a["t16_status"] = cen["status"]
    return a


# ---------------------------------------------------------------------------
# Construção
# ---------------------------------------------------------------------------

def construir() -> dict:
    entradas = []
    for rel, papel in ENTRADAS:
        p = ROOT / rel
        exigir(p.exists(), f"entrada ausente: {rel}")
        if rel.endswith(".csv"):
            tabela(rel)
        else:
            documento(rel)
        entradas.append({"caminho": rel, "sha256": sha256(p), "bytes": p.stat().st_size, "papel": papel})
    fh = familias_holm()
    fb = familias_bky()
    v = valores()
    af = checar_afirmacoes(v, fh)
    return {
        "natureza_dos_dados": "EMPIRICO",
        "estatuto": "SINTESE_ONDA_5",
        "script": "scripts/rdd_bolsa/33_sintese_perguntas.py",
        "doc": "docs/06_execucao/57_sintese_perguntas_reformuladas.md",
        "data_doc": DATA_DOC,
        "parametros": {"alfa": ALFA, "fator_mde": FATOR_MDE, "tol_holm": TOL_HOLM, "tol_bky": TOL_BKY,
                       "limiar_R_P1_por_5mil": LIMIAR_R_P1, "limiar_R_P2_por_5mil": LIMIAR_R_P2},
        "entradas": entradas,
        "holm": fh,
        "bky": fb,
        "divergencias": divergencias(fh, fb),
        "afirmacoes": af,
        "v": v,
    }


# ---------------------------------------------------------------------------
# Formatação com rastreio
# ---------------------------------------------------------------------------

def fmt_num(x: float, casas: int, sinal: bool = True) -> str:
    txt = f"{abs(x):.{casas}f}"
    if float(txt) == 0:
        return txt.replace(".", ",")
    txt = txt.replace(".", ",")
    if x < 0:
        return "−" + txt
    return ("+" if sinal else "") + txt


def fmt_p(x: float) -> str:
    return "< 0,001" if x < 0.001 else f"{x:.3f}".replace(".", ",")


class Fmt:
    def __init__(self) -> None:
        self.rastreio: list[dict] = []

    def _reg(self, val: dict, texto: str, modo: str, casas: int, sinal: bool) -> str:
        self.rastreio.append({"texto": texto, "modo": modo, "casas": casas, "sinal": sinal, "fonte": val})
        return texto

    def n(self, val: dict, casas: int, sinal: bool = True) -> str:
        return self._reg(val, fmt_num(val["v"], casas, sinal), "num", casas, sinal)

    def p(self, val: dict) -> str:
        return self._reg(val, fmt_p(val["v"]), "p", 3, False)

    def ic(self, lo: dict, hi: dict, casas: int, sinal: bool = True) -> str:
        return f"[{self.n(lo, casas, sinal)}; {self.n(hi, casas, sinal)}]"


def bloco(nome: str, corpo: str) -> str:
    return f"<!-- S57:{nome}:inicio -->\n{corpo}\n<!-- S57:{nome}:fim -->"


# Forças da evidência (categorias fixas do pedido do autor).
FORCA_CAUSAL = "causal-limpo"
FORCA_ATT = "ATT sob tendências paralelas com pré falhando"
FORCA_EXPL = "exploratório"
FORCA_DESC = "descritivo"
FORCA_INC = "inconclusivo"
FORCA_FALHA = "falha de validação"

# Contrastes (categorias fixas).
C_MARG = "incentivo marginal"
C_PAC = "pacote do corte"
C_ALOC = "ser alocado"
C_CHEG = "chegada do especialista"
C_DESC = "descritivo"


def gerar_doc(r: dict) -> tuple[str, list[dict], list[dict]]:
    """Gera o doc 57 só a partir do resumo. Devolve (texto, rastreio, segmentos de linguagem)."""
    F = Fmt()
    v = r["v"]
    af = r["afirmacoes"]
    seg: list[dict] = []

    def S(forcas: list[str], texto: str) -> str:
        seg.append({"forcas": forcas, "texto": texto})
        return texto

    n, p, ic = F.n, F.p, F.ic
    partes: list[str] = []

    # Cabeçalho.
    partes.append(f"""# 57. Síntese das perguntas reformuladas (P1–P6, realocação e T1.6)

> **Data:** {r['data_doc']}.<br>
> **Plano:** [doc 51](51_plano_perguntas_reformuladas.md), §5 (onda 5). Formato e regra de Holm herdados da síntese anterior ([doc 44](44_sintese_rdd_bolsa_multioutcome.md)).<br>
> **Gerado por** `scripts/rdd_bolsa/33_sintese_perguntas.py`, que lê só de `output/`; não editar à mão. O teste `tests/test_sintese_perguntas.py` confere que este arquivo é igual ao gerado, que todo número volta a um arquivo de `output/` e que o Holm e o BKY batem com os p gravados.<br>
> **Saídas:** `output/rdd_bolsa/S57_resumo.json`, `S57_tabela_perguntas.csv`, `S57_multiplicidade.csv` e `S57_poder.csv`; natureza dos dados `EMPIRICO`.<br>
> **Estatuto:** síntese. Nada é estimado de novo. As únicas contas são o Holm e o BKY refeitos dos p gravados, o MDE como 2,8 × EP onde o bloco não gravou o MDE, a razão de chances por +R$ 5 mil a partir do coeficiente por R$ 1 mil e a passagem de fração para p.p.<br>
> **Hipótese central:** a escolha é do autor. A seção 7 traz uma proposta, rotulada como proposta; nada aqui a adota.

Todo resultado mede, no máximo, o **pacote do corte** (a bolsa anunciada +R$ 5 mil e as outras regras federais que mudam nos mesmos cortes de IVS, [auditoria 18](../auditorias/18_politicas_nos_mesmos_cortes_ivs.md)), o incentivo marginal dentro desse pacote (DiRD), a chegada do especialista sob tendências paralelas, o fato de ser alocado perto da nota de corte, ou é descritivo. Nenhum é efeito da participação no PMM-E nem do Agora Tem Especialistas.""")

    # 1. Resposta curta.
    rej56 = af["rejeitam_holm"]["H56"]
    txt = (
        "Nenhuma pergunta tem hoje evidência causal limpa de mudança no resultado medido. Nas cinco famílias "
        f"de primárias com Holm definidas nos protocolos (40, 47, 48, 52 e 58), nenhuma linha rejeita zero; na "
        f"família do relato do P6, só as {len(rej56)} linhas do Y1 rejeitam, e o Y1 é quase mecânico (ser alocado "
        "cria o vínculo cadastrado no município da vaga).\n\n"
        "**Pergunta central do autor: os R$ 5 mil a mais aumentam a atração ou o preenchimento?** Como pacote do "
        "corte, não se detecta aumento em nenhuma das duas margens, e os dados só descartam aumentos grandes em "
        "parte. Na célula aberta, com ciclos e cortes empilhados, o salto da probabilidade de preenchimento é "
        f"{n(v['a3p_todos_emp_tau'], 1)} p.p. {ic(v['a3p_todos_emp_lo'], v['a3p_todos_emp_hi'], 1)}: o maior aumento "
        f"compatível com os dados é {n(v['a3p_todos_emp_hi'], 1)} p.p., e o desenho só detectaria com 80% de poder um "
        f"salto de {n(v['a3p_todos_emp_mde'], 1, False)} p.p. Por corte, o limite superior é {n(v['a3p_todos_300_hi'], 1)} "
        f"p.p. em 0,300 e {n(v['a3p_todos_400_hi'], 1)} p.p. em 0,400. Na atração, a probabilidade de a célula ter "
        f"candidato de 1ª opção salta {n(v['a3c_todos_emp_tau'], 1)} p.p. {ic(v['a3c_todos_emp_lo'], v['a3c_todos_emp_hi'], 1)}. "
        "Na escolha entre vagas já abertas, o coeficiente principal do P1 (M1) não se distingue de zero (razão de "
        f"chances por +R$ 5 mil {n(v['m1_rc'], 2, False)} {ic(v['m1_rc_lo'], v['m1_rc_hi'], 2, False)}); o sinal que "
        f"resiste a vários testes continua só no ciclo 2 (E9: {n(v['e9c2_rc'], 2, False)} "
        f"{ic(v['e9c2_rc_lo'], v['e9c2_rc_hi'], 2, False)}), e escolha entre vagas não é preenchimento. A realocação "
        "entre concorrentes é inconclusiva, e os cenários do T1.6 não existem, porque a validação de base falhou.\n\n"
        "Produção, horas e vínculos depois da chegada do especialista (P3 D2, P3x e P4) aparecem como associações "
        "sob tendências paralelas, com o pré falhando em parte das linhas; nos cortes (P3 D1), nada se distingue de "
        "zero. A abertura de vagas (P5) é descrita, não explicada: o IVS contínuo não se distingue de zero no pedido "
        "nem na priorização."
    )
    partes.append("## 1. Resposta curta\n\n" + bloco("resposta_curta", S([FORCA_INC, FORCA_ATT, FORCA_DESC, FORCA_EXPL, FORCA_FALHA], txt)))

    # 2. Tabela por pergunta.
    linhas_p = []

    def lp(pergunta, estimando, desenho, unidade, contraste, resultado, forca, docs):
        S([forca], f"{estimando} {resultado}")
        linhas_p.append({"pergunta": pergunta, "estimando": estimando, "desenho": desenho, "unidade": unidade,
                         "contraste": contraste, "resultado": resultado, "forca": forca, "docs": docs})

    lp("P1 — quanto a bolsa move a escolha de onde trabalhar",
       "peso da bolsa (por R$ 1 mil/mês) na escolha da 1ª opção entre as vagas abertas do curso e ciclo",
       "logit condicional; IVS em spline contínua com nós em 0,300 e 0,400; distância e origem controladas (M1)",
       "candidato × vaga do conjunto de escolha, ciclos 1–3",
       C_PAC,
       f"M1: {n(v['m1_coef'], 4)} {ic(v['m1_lo'], v['m1_hi'], 4)} por R$ 1 mil (razão de chances por +R$ 5 mil "
       f"{n(v['m1_rc'], 2, False)} {ic(v['m1_rc_lo'], v['m1_rc_hi'], 2, False)}); p de Holm {p(v['m1_holm'])}. "
       f"Ciclo 2 (E9): {n(v['e9c2_rc'], 2, False)} {ic(v['e9c2_rc_lo'], v['e9c2_rc_hi'], 2, False)}",
       FORCA_INC, "[57a](57a_resultados_P1_escolha.md); [aud. 26](../auditorias/26_auditoria_P1_escolha.md)")
    lp("P2 — a bolsa maior preenche mais a vaga já aberta",
       "salto, no corte, da probabilidade de a célula aberta ser preenchida na 1ª chamada; número de vagas preenchidas por município dado o número oferecido",
       "RDD sharp local linear nos cortes de IVS; efeitos fixos de curso × ciclo e tipo de vaga (A3); controle pelas vagas oferecidas (N, S-a)",
       "célula aberta (A3); município (N); ciclos 1–3",
       C_PAC,
       f"A3, empilhado: {n(v['a3p_todos_emp_tau'], 1)} p.p. {ic(v['a3p_todos_emp_lo'], v['a3p_todos_emp_hi'], 1)}; "
       f"N1: {n(v['n_N1_tau'], 2)} {ic(v['n_N1_lo'], v['n_N1_hi'], 2)} vagas por município, p de Holm {p(v['n_N1_holm'])}",
       FORCA_INC, "[49](49_resultados_contagem_vagas_preenchidas.md) §3 e §15; [aud. 20](../auditorias/20_auditoria_contagem_vagas_N.md), [aud. 22](../auditorias/22_auditoria_abertura_vagas_NA.md)")
    lp("P3 (D1) — produção especializada nos cortes",
       "salto, no corte, da mudança entre pré e pós da produção SUS (K1), das cirurgias (K2) e das consultas SUS + planos (K3)",
       "DiRD local linear nos cortes (remove só a parte fixa no tempo das outras políticas)",
       "município × mês (médias do pré e do pós), U",
       C_MARG,
       f"K1: {n(v['kd1_K1_tau'], 2)} {ic(v['kd1_K1_lo'], v['kd1_K1_hi'], 2)} por 10 mil hab./mês; K2: "
       f"{n(v['kd1_K2_tau'], 2)} {ic(v['kd1_K2_lo'], v['kd1_K2_hi'], 2)}; K3: {n(v['kd1_K3_tau'], 2)} "
       f"{ic(v['kd1_K3_lo'], v['kd1_K3_hi'], 2)}; p de Holm {p(v['kd1_K1_holm'])} nas três",
       FORCA_INC, "[50](50_resultados_producao_especializada.md); [aud. 21](../auditorias/21_auditoria_producao_K.md)")
    lp("P3 (D2 e P3x) — produção depois da chegada do especialista",
       "diferença média do pós na produção entre municípios (ou pares município × curso) que receberam o especialista e os que ainda não tinham recebido",
       "Callaway–Sant'Anna; controles ainda não tratados; pré testado (Wald)",
       "município × mês; município × curso × mês (12.2)",
       C_CHEG,
       f"K1 (D2): {n(v['kd2_K1_att'], 2)} {ic(v['kd2_K1_lo'], v['kd2_K1_hi'], 2)}; produção típica da "
       f"especialidade (12.2): {n(v['x122_att'], 2)} {ic(v['x122_lo'], v['x122_hi'], 2)}, pré com p do Wald "
       f"{p(v['x122_pre'])}; K2 (D2): pré com p do Wald {p(v['kd2_K2_pre'])}",
       FORCA_ATT, "[50](50_resultados_producao_especializada.md) §7, [57c](57c_resultados_P3_extensoes.md); [aud. 21](../auditorias/21_auditoria_producao_K.md), [aud. 25](../auditorias/25_auditoria_P3_extensoes.md)")
    lp("P4 — oferta nova ou pagamento a quem já estava",
       "variação das horas e vínculos cadastrados do médico associada à entrada no PMM-E",
       "Callaway–Sant'Anna no médico (coortes de entrada); contabilidade pré × pós sem comparação",
       "médico × mês, ciclos 1 e 2",
       C_CHEG,
       f"horas totais, média de θ(0..+6): {n(v['p4_ht_att'], 1)} h/sem {ic(v['p4_ht_lo'], v['p4_ht_hi'], 1)} (pré: p "
       f"{p(v['p4_ht_pre'])}); no município do posto: {n(v['p4_hm_att'], 1)} {ic(v['p4_hm_lo'], v['p4_hm_hi'], 1)} "
       f"(pré: p {p(v['p4_hm_pre'])}); já estavam no município: {n(v['p4_origem'], 1, False)}% "
       f"{ic(v['p4_origem_lo'], v['p4_origem_hi'], 1, False)}",
       FORCA_ATT, "[57d](57d_resultados_P4_trajetoria.md); [aud. 24](../auditorias/24_auditoria_P4_trajetoria.md)")
    lp("P5 — onde o Ministério abre vagas",
       "associação de características pré-determinadas com o pedido do gestor e a priorização da SGTES",
       "logit descritivo com efeito fixo de curso (T5.1); RDD nos cortes do pedido e da priorização (T5.2)",
       "célula do cardápio do ciclo 3; município nos ciclos 1–2",
       C_DESC,
       f"IVS contínuo no pedido: {n(v['p5_ivs_e1'], 1)} p.p. por DP {ic(v['p5_ivs_e1_lo'], v['p5_ivs_e1_hi'], 1)}; na "
       f"priorização: {n(v['p5_ivs_e2'], 1)} {ic(v['p5_ivs_e2_lo'], v['p5_ivs_e2_hi'], 1)}; célula pedida no corte "
       f"(T5.2a, empilhado): {n(v['p5_ped'], 1)} p.p. {ic(v['p5_ped_lo'], v['p5_ped_hi'], 1)}, q BKY {p(v['p5_ped_q'])}",
       FORCA_DESC, "[57e](57e_resultados_P5_abertura.md); [aud. 23](../auditorias/23_auditoria_P5_abertura.md)")
    lp("P6 — alocado por pouco contra não alocado por pouco",
       "diferença na trajetória cadastrada no CNES entre candidatos logo acima e logo abaixo da nota de corte da 1ª opção",
       "comparação local na nota de corte com efeito fixo de célula; p por permutação; desempate por regra fixa, não sorteio",
       "candidato de ampla concorrência, ciclos 1 e 2",
       C_ALOC,
       f"Y1 (vínculo no município da vaga, média): {n(v['p6_y1_media_est'], 3)} {ic(v['p6_y1_media_lo'], v['p6_y1_media_hi'], 3)}, "
       f"p de Holm {p(v['p6_y1_media_holm'])} (quase mecânico); Y3 (horas totais, média): {n(v['p6_y3_media_est'], 1)} "
       f"{ic(v['p6_y3_media_lo'], v['p6_y3_media_hi'], 1)}, p de Holm {p(v['p6_y3_media_holm'])}",
       FORCA_EXPL, "[57f](57f_resultados_P6_mecanismo.md); [aud. 27](../auditorias/27_auditoria_P6_mecanismo.md)")
    lp("Realocação — a bolsa das concorrentes desloca candidatos",
       "mudança no preenchimento e nos candidatos de 1ª opção da célula quando a bolsa média das concorrentes do mesmo curso e ciclo na região de saúde sobe",
       "regressão na célula com o IVS próprio e o das concorrentes em spline contínua; cluster por região de saúde",
       "célula aberta, ciclos 1–3",
       C_PAC,
       f"R-P1 por +R$ 5 mil: {n(v['R_P1_c5'], 1)} p.p. {ic(v['R_P1_lo'], v['R_P1_hi'], 1)}, p de Holm "
       f"{p(v['R_P1_holm'])}, MDE {n(v['R_P1_mde'], 1, False)} p.p.; R-P2: {n(v['R_P2_c5'], 3)} "
       f"{ic(v['R_P2_lo'], v['R_P2_hi'], 3)}, p de Holm {p(v['R_P2_holm'])}",
       FORCA_INC, "[57g](57g_resultados_realocacao.md); [aud. 28](../auditorias/28_auditoria_realocacao.md)")
    lp("T1.6 — cenários de bolsa com o modelo de escolha",
       "vagas preenchidas na 1ª chamada sob grades de bolsa alternativas, com candidatos e vagas fixos (cenário, não observação)",
       "simulação com o M1 e o mecanismo de alocação do G2",
       "candidato × célula, 1ª chamada dos ciclos 1–3",
       C_PAC,
       f"validação de base reprovada ({'; '.join(af['t16_falhas'])}); cenários não calculados",
       FORCA_FALHA, "[57b](57b_cenarios_P1_bolsa.md); sem auditoria própria (a execução parou na validação)")

    cab = ("| Pergunta | Estimando | Desenho | Unidade | Contraste identificado | Resultado principal [IC 95%] | "
           "Força da evidência | Doc e auditoria |\n|---|---|---|---|---|---|---|---|")
    corpo = "\n".join(f"| {x['pergunta']} | {x['estimando']} | {x['desenho']} | {x['unidade']} | {x['contraste']} | "
                      f"{x['resultado']} | {x['forca']} | {x['docs']} |" for x in linhas_p)
    exigir(not any(x["forca"] == FORCA_CAUSAL for x in linhas_p), "nenhuma linha é causal-limpa neste estado")
    partes.append(
        "## 2. Tabela por pergunta\n\n"
        "**Como ler.** \"Contraste identificado\" diz o que a comparação mede no melhor caso. \"Força da evidência\" "
        "usa seis categorias fixas: causal-limpo; ATT sob tendências paralelas com pré falhando; exploratório; "
        "descritivo; inconclusivo; falha de validação. Nenhuma linha está hoje na primeira. \"Inconclusivo\" quer "
        "dizer que o desenho identifica o contraste, mas o IC contém zero: não é evidência de ausência.\n\n"
        + bloco("perguntas", cab + "\n" + corpo))

    # 3. Multiplicidade.
    lin = ["| Família (protocolo) | Linha | p gravado | p de Holm gravado | p de Holm recalculado | Diferença | Rejeita a 5%? |",
           "|---|---|---|---|---|---|---|"]
    for f in r["holm"]:
        for m in f["membros"]:
            lin.append(f"| {f['id']} ({f['protocolo']}): {f['descricao']} | {m['rotulo']} | {p(m['p'])} | "
                       f"{p(m['gravado'])} | {p(m['recalculado'])} | {n(m['dif'], 6, False)} | "
                       f"{'sim' if m['rejeita_recalculado'] else 'não'} |")
    holm_txt = "\n".join(lin)
    lin = ["| Família (protocolo) | Linhas | q < 0,05 gravado | q < 0,05 recalculado | Maior diferença de q |",
           "|---|---|---|---|---|"]
    for f in r["bky"]:
        lin.append(f"| {f['id']} ({f['protocolo']}): {f['descricao']} | {f['n']} | {f['n_q_gravado_menor_005']} | "
                   f"{f['n_q_recalculado_menor_005']} | {n(f['max_dif'], 4, False)} |")
    bky_txt = "\n".join(lin)
    if r["divergencias"]:
        div_txt = "Divergências encontradas (relatadas, não corrigidas):\n\n" + "\n".join(f"- {d}" for d in r["divergencias"])
    else:
        div_txt = ("Nenhuma divergência: em todas as famílias, o Holm recalculado bate com o gravado dentro da "
                   "tolerância e o BKY recalculado bate com o gravado dentro de um passo da grade, com a mesma "
                   "decisão a 5% em toda linha.")
    partes.append(
        "## 3. Holm nas primárias e BKY nas secundárias\n\n"
        "Cada família é a que o protocolo do bloco definiu. Os p são os gravados nas saídas de cada bloco; o Holm "
        "e o BKY (Benjamini, Krieger e Yekutieli, grade de 0,001 de Anderson, 2008) foram refeitos aqui com código "
        "próprio e comparados com o que o bloco gravou. Fora destas famílias, nada tem correção: o D2 da família K, "
        "as leituras por ciclo da realocação e as linhas do adendo NA são relatados sem ajuste, como nos docs de "
        "origem.\n\n"
        "### 3.1 Holm\n\n"
        "O protocolo 56 (P6) pede BKY; o Holm do P6 foi pedido no relato e aparece como família à parte.\n\n"
        + bloco("holm", holm_txt) + "\n\n### 3.2 BKY\n\n" + bloco("bky", bky_txt)
        + "\n\n### 3.3 Divergências\n\n" + bloco("divergencias", div_txt))

    # 4. Poder.
    def lpod(nome, contraste, est, lo, hi, mde, unidade, casas, fonte_mde, sinal=True):
        return (f"| {nome} | {contraste} | {n(est, casas, sinal)} | {ic(lo, hi, casas, sinal)} | {n(hi, casas, sinal)} | "
                f"{n(mde, casas, False)} | {unidade} | {fonte_mde} |")

    G, C = "gravado pelo bloco", "2,8 × EP (aqui)"
    lin = ["| Primária | Contraste | Estimativa | IC 95% | Maior valor compatível (limite superior) | MDE 80% | Unidade | MDE |",
           "|---|---|---|---|---|---|---|---|"]
    lin.append(lpod("P1 índice de atração-presença (protocolo 40)", C_PAC, v["e6_p1_tau"], v["e6_p1_lo"], v["e6_p1_hi"],
                    v["e6_p1_mde"], "desvios-padrão", 2, C))
    lin.append(lpod("P2 vínculos nas CBO-alvo, DiRD (protocolo 40)", C_MARG, v["e7_p2_tau"], v["e7_p2_lo"], v["e7_p2_hi"],
                    v["e7_p2_mde"], "vínculos por 10 mil hab.", 3, C))
    for k_, rot in (("K1", "K1 produção SUS das CBO-alvo"), ("K2", "K2 cirurgias SUS"), ("K3", "K3 consultas SUS + planos")):
        lin.append(lpod(f"{rot} (protocolo 47)", C_MARG, v[f"kd1_{k_}_tau"], v[f"kd1_{k_}_lo"], v[f"kd1_{k_}_hi"],
                        v[f"kd1_{k_}_mde"], "por 10 mil hab./mês", 2, G))
    for n_, rot in (("N1", "N1 vagas preenchidas"), ("N2", "N2 células com alocado"), ("N3", "N3 células com alocado até a 2ª chamada"),
                    ("N4", "N4 especialistas ativos")):
        lin.append(lpod(f"{rot} (protocolo 48)", C_PAC, v[f"n_{n_}_tau"], v[f"n_{n_}_lo"], v[f"n_{n_}_hi"],
                        v[f"n_{n_}_mde"], "por município", 2, G))
    lin.append(lpod("P1a coeficiente da bolsa, M1 (protocolo 52)", C_PAC, v["m1_coef"], v["m1_lo"], v["m1_hi"], v["m1_mde"],
                    "log-chance por R$ 1 mil", 4, C))
    lin.append(lpod("P1a em razão de chances (protocolo 52)", C_PAC, v["m1_rc"], v["m1_rc_lo"], v["m1_rc_hi"], v["m1_rc_mde"],
                    "razão de chances por +R$ 5 mil", 2, "exp(5 × 2,8 × EP) (aqui)", sinal=False))
    lin.append(lpod("R-P1 célula preenchida (protocolo 58)", C_PAC, v["R_P1_c5"], v["R_P1_lo"], v["R_P1_hi"], v["R_P1_mde"],
                    "p.p. por +R$ 5 mil das concorrentes", 1, G))
    lin.append(lpod("R-P2 candidatos de 1ª opção (protocolo 58)", C_PAC, v["R_P2_c5"], v["R_P2_lo"], v["R_P2_hi"],
                    v["R_P2_mde"], "candidatos por +R$ 5 mil das concorrentes", 3, G))
    for y, rot, cas, un in (("y1", "Y1 vínculo no município da vaga", 3, "fração"), ("y2", "Y2 horas SUS", 1, "h/sem"),
                            ("y3", "Y3 horas totais", 1, "h/sem"), ("y4", "Y4 vínculo fora da origem", 3, "fração"),
                            ("y5", "Y5 número de municípios", 3, "municípios")):
        for med, mrot in (("ultimo", "202608"), ("media", "média do seguimento")):
            b = f"p6_{y}_{med}"
            lin.append(lpod(f"{rot}, {mrot} (protocolo 56)", C_ALOC, v[f"{b}_est"], v[f"{b}_lo"], v[f"{b}_hi"],
                            v[f"{b}_mde"], un, cas, C))
    poder_txt = "\n".join(lin)

    def lcen(rot, b, casas=1):
        return (f"| {rot} | {n(v[b + '_media'], casas, False)}% | {n(v[b + '_tau'], casas)} {ic(v[b + '_lo'], v[b + '_hi'], casas)} | "
                f"{n(v[b + '_hi'], casas)} | {n(v[b + '_mde'], casas, False)} |")

    cen = ["**Preenchimento: probabilidade de a célula aberta ser preenchida na 1ª chamada (A3, p.p.)**", "",
           "| Amostra e corte | Média abaixo do corte | Salto [IC 95%] | Maior aumento compatível | MDE 80% |",
           "|---|---|---|---|---|"]
    for pn, prot in (("todos", "ciclos 1–3"), ("c1", "ciclo 1")):
        for cn, crot in (("300", "corte 0,300"), ("400", "corte 0,400"), ("emp", "cortes empilhados")):
            cen.append(lcen(f"{prot}, {crot}", f"a3p_{pn}_{cn}"))
    cen += ["", "**Atração: probabilidade de a célula aberta ter candidato de 1ª opção (A3, p.p.)**", "",
            "| Amostra e corte | Média abaixo do corte | Salto [IC 95%] | Maior aumento compatível | MDE 80% |",
            "|---|---|---|---|---|"]
    for pn, prot in (("todos", "ciclos 1–3"), ("c1", "ciclo 1")):
        for cn, crot in (("300", "corte 0,300"), ("400", "corte 0,400"), ("emp", "cortes empilhados")):
            cen.append(lcen(f"{prot}, {crot}", f"a3c_{pn}_{cn}"))
    cen += ["", f"Candidatos de 1ª opção por célula (E6, F1.1, ciclos e cortes empilhados): {n(v['f11_tau'], 3)} "
            f"{ic(v['f11_lo'], v['f11_hi'], 3)}; maior aumento compatível {n(v['f11_hi'], 3)} candidato; MDE 80% "
            f"{n(v['f11_mde'], 3, False)} (2,8 × EP, aqui).", "",
            "**Escolha entre vagas abertas (razão de chances por +R$ 5 mil)**", "",
            "| Modelo | Razão de chances [IC 95%] | Maior valor compatível | Leitura |", "|---|---|---|---|",
            f"| P1, M1 (ciclos 1–3, com distância; primária) | {n(v['m1_rc'], 2, False)} {ic(v['m1_rc_lo'], v['m1_rc_hi'], 2, False)} | "
            f"{n(v['m1_rc_hi'], 2, False)} | IC contém 1; MDE 80% em razão de chances {n(v['m1_rc_mde'], 2, False)} |",
            f"| P1, M5 (só o ciclo 2) | {n(v['m5c2_rc'], 2, False)} {ic(v['m5c2_rc_lo'], v['m5c2_rc_hi'], 2, False)} | "
            f"{n(v['m5c2_rc_hi'], 2, False)} | IC exclui 1; secundária |",
            f"| E9 (ciclo 2, sem distância) | {n(v['e9c2_rc'], 2, False)} {ic(v['e9c2_rc_lo'], v['e9c2_rc_hi'], 2, False)} | "
            f"{n(v['e9c2_rc_hi'], 2, False)} | IC exclui 1; exploratório |", "",
            "**Realocação entre concorrentes (por +R$ 5 mil na bolsa média das concorrentes)**", "",
            f"- R-P1, célula preenchida: {n(v['R_P1_c5'], 1)} p.p. {ic(v['R_P1_lo'], v['R_P1_hi'], 1)}; MDE "
            f"{n(v['R_P1_mde'], 1, False)} p.p., acima do limiar do protocolo: inconclusivo.",
            f"- R-P2, candidatos de 1ª opção: {n(v['R_P2_c5'], 3)} {ic(v['R_P2_lo'], v['R_P2_hi'], 3)}; MDE "
            f"{n(v['R_P2_mde'], 3, False)}, acima do limiar do protocolo: inconclusivo.", "",
            "**T1.6 (cenários)**", "",
            f"- Status `{af['t16_status']}`: a reconstrução sem mudança de bolsa não reproduziu as vagas publicadas "
            f"dentro da tolerância em todas as réplicas ({'; '.join(af['t16_falhas'])}). Os cenários não foram "
            "calculados; não há resposta simulada à pergunta do total de vagas.",
            "- Mesmo validado, o modelo de escolha não responderia à margem extensiva: no logit condicional só "
            "diferenças de utilidade entre vagas contam, então somar o mesmo valor à bolsa de todas as vagas não "
            "muda nenhuma escolha com o grupo de candidatos fixo. Um aumento uniforme só poderia mover quem entra "
            "no programa, e isso o modelo não vê."]
    cen_txt = "\n".join(cen)
    S([FORCA_INC, FORCA_FALHA], cen_txt)
    partes.append(
        "## 4. Poder e efeito mínimo detectável\n\n"
        "**Como ler.** O limite superior do IC 95% é o maior valor que os dados ainda admitem, com o IC "
        "convencional e a aproximação local linear; quando a estimativa pontual é negativa, esse limite fica perto "
        "de zero mesmo com pouca precisão. O MDE de 80% é o menor salto que o desenho detectaria com 80% de poder "
        "num teste bilateral a 5% (cerca de 2,8 × EP): diz quanto o desenho enxerga, independentemente do sinal "
        "observado. Os dois números juntos dizem o que fica descartado e o que ainda passaria despercebido.\n\n"
        "### 4.1 Primárias\n\n" + bloco("poder", poder_txt)
        + "\n\n### 4.2 A pergunta central: os R$ 5 mil a mais aumentam a atração ou o preenchimento?\n\n"
        "Tudo abaixo é o **pacote do corte**: a bolsa anunciada maior junto com as outras regras federais nos "
        "mesmos cortes. O ciclo 1 aparece à parte porque nele a faixa saiu depois do pedido dos gestores.\n\n"
        + bloco("pergunta_central", cen_txt))

    # 5. Cadeia.
    elos = []

    def elo(nome, forcas, sabe, falta, rotulo_forca=None):
        S(forcas, sabe)
        elos.append(f"**{nome}.** {sabe} *Força:* {rotulo_forca or ', '.join(forcas)}. *O que falta:* {falta}")

    elo("Implementação (abertura de vagas)", [FORCA_DESC, FORCA_INC],
        "O pedido do gestor e a priorização da SGTES andam junto com macrorregião, porte e capacidade instalada; o "
        f"IVS contínuo não se distingue de zero no pedido ({n(v['p5_ivs_e1'], 1)} p.p. por DP "
        f"{ic(v['p5_ivs_e1_lo'], v['p5_ivs_e1_hi'], 1)}) nem na priorização ({n(v['p5_ivs_e2'], 1)} "
        f"{ic(v['p5_ivs_e2_lo'], v['p5_ivs_e2_hi'], 1)}). No corte, a célula pedida salta {n(v['p5_ped'], 1)} p.p. "
        f"{ic(v['p5_ped_lo'], v['p5_ped_hi'], 1)}, sem passar no BKY (q {p(v['p5_ped_q'])}); a priorizada, "
        f"{n(v['p5_pri'], 1)} p.p. {ic(v['p5_pri_lo'], v['p5_pri_hi'], 1)}.",
        "o critério oficial de priorização não é publicado; a abertura dos ciclos 1–2 só se vê no quadro final.")
    elo("Força de trabalho (escolha, alocação e entrada)", [FORCA_INC, FORCA_EXPL],
        f"Na escolha entre vagas abertas, o M1 dá razão de chances por +R$ 5 mil de {n(v['m1_rc'], 2, False)} "
        f"{ic(v['m1_rc_lo'], v['m1_rc_hi'], 2, False)}; só o ciclo 2 tem IC que exclui 1 (E9: {n(v['e9c2_rc'], 2, False)} "
        f"{ic(v['e9c2_rc_lo'], v['e9c2_rc_hi'], 2, False)}). Ser alocado por pouco cria o vínculo cadastrado no "
        f"município da vaga ({n(v['p6_y1_media_est'], 3)} {ic(v['p6_y1_media_lo'], v['p6_y1_media_hi'], 3)}, quase "
        f"mecânico); horas e permanência não se distinguem entre os lados. Dos médicos que entraram, "
        f"{n(v['p4_origem'], 1, False)}% {ic(v['p4_origem_lo'], v['p4_origem_hi'], 1, False)} já tinham vínculo no "
        "município do posto antes do início (descritivo).",
        "o universo de inscritos e quem não se candidatou (margem extensiva, pedido externo); a remuneração paga; "
        "a replicação da escolha no ciclo 3.")
    elo("Capacidade (vínculos e horas)", [FORCA_INC, FORCA_ATT],
        f"Nos cortes, a DiRD dos vínculos nas CBO-alvo dá {n(v['e7_p2_tau'], 3)} {ic(v['e7_p2_lo'], v['e7_p2_hi'], 3)} por "
        f"10 mil hab. (p de Holm {p(v['e8_p2_holm'])}). Entre médicos que entram em meses diferentes, as horas totais "
        f"cadastradas sobem {n(v['p4_ht_att'], 1)} h/sem {ic(v['p4_ht_lo'], v['p4_ht_hi'], 1)} associadas à entrada (pré "
        f"com p {p(v['p4_ht_pre'])}); as horas no município do posto, {n(v['p4_hm_att'], 1)} "
        f"{ic(v['p4_hm_lo'], v['p4_hm_hi'], 1)}, com o pré falhando (p {p(v['p4_hm_pre'])}); as horas fora dele, "
        f"{n(v['p4_hf_att'], 1)} {ic(v['p4_hf_lo'], v['p4_hf_hi'], 1)}. Na contabilidade sem comparação, "
        f"{n(v['p4_comp'], 1, False)}% {ic(v['p4_comp_lo'], v['p4_comp_hi'], 1, False)} do ganho no município do posto "
        "é compensado por perda fora dele (descritivo). Horas cadastradas não são horas trabalhadas.",
        "o CNES do ciclo 3 em 202703 (município–mês como teste de oferta líquida local); a presença real (folha "
        "de pagamento, pedido externo).")
    elo("Acesso (produção)", [FORCA_INC, FORCA_ATT],
        f"Nos cortes, K1 dá {n(v['kd1_K1_tau'], 2)} {ic(v['kd1_K1_lo'], v['kd1_K1_hi'], 2)} por 10 mil hab./mês, com MDE "
        f"de {n(v['kd1_K1_mde'], 2, False)} sobre uma média do pré de {n(v['kd1_K1_media'], 2, False)}; K2 e K3 também "
        f"têm IC que contém zero (p de Holm {p(v['kd1_K1_holm'])}). Depois da chegada, K1 difere "
        f"{n(v['kd2_K1_att'], 2)} {ic(v['kd2_K1_lo'], v['kd2_K1_hi'], 2)}; a produção típica da especialidade que chegou, "
        f"{n(v['x122_att'], 2)} {ic(v['x122_lo'], v['x122_hi'], 2)}, mas com o pré falhando (p {p(v['x122_pre'])}); "
        f"todas as internações dos residentes, {n(v['x124_att'], 2)} {ic(v['x124_lo'], v['x124_hi'], 2)}, com boa parte "
        "da diferença já presente antes da chegada (doc 57c).",
        "espera e fila (a regulação não é pública, pedido externo); meses maduros do SIA e do SIH; o ciclo 3.")
    elo("Saúde", [FORCA_INC],
        "Nada foi medido. As internações dos residentes aproximam o uso, não o estado de saúde.",
        "horizonte longo; desfechos de saúde por residência depois da maturidade do ciclo 3.",
        rotulo_forca="não medido")
    elo("Custos e bem-estar", [FORCA_FALHA],
        "Nada foi estimado. O custo por candidato ou vaga adicional dependia dos cenários do T1.6, que não foram "
        "calculados porque a validação de base falhou.",
        "decisão do autor sobre a revalidação do T1.6; folha de pagamento (pedido externo); gasto do bolso não tem fonte "
        "municipal.", rotulo_forca="não estimado (o T1.6, que daria o custo, é falha de validação)")
    elo("Equidade e spillovers", [FORCA_ATT, FORCA_INC, FORCA_DESC],
        f"Nos outros municípios da região de saúde, a produção K1 difere {n(v['x125_att'], 2)} "
        f"{ic(v['x125_lo'], v['x125_hi'], 2)} depois da chegada, com o pré falhando (p {p(v['x125_pre'])}): não separa "
        "atendimento de referência de deslocamento. A realocação entre concorrentes é inconclusiva "
        f"({n(v['R_P1_c5'], 1)} p.p. {ic(v['R_P1_lo'], v['R_P1_hi'], 1)}). Entre os médicos que mudaram, as horas "
        f"cadastradas na origem variam {n(v['p4_origem_delta'], 1)} h/sem "
        f"{ic(v['p4_origem_delta_lo'], v['p4_origem_delta_hi'], 1)} (descritivo, sem comparação).",
        "o universo de inscritos (para ver quem deixa de se candidatar onde); o ciclo 3 para replicar fora da "
        "amostra que gerou a hipótese.")
    partes.append(
        "## 5. Leitura em linguagem simples, pela cadeia\n\n"
        "A ordem é a do `CLAUDE.md`: implementação → força de trabalho → capacidade → acesso → saúde → custos e "
        "bem-estar → equidade e spillovers. Em cada elo: o que se sabe, com que força e o que falta.\n\n"
        + bloco("cadeia", "\n\n".join(elos)))

    # 6. Lacunas (texto fixo, sem número de resultado).
    partes.append("""## 6. Lacunas e próximos passos

Nenhum item abaixo foi executado. Custo e valor são juízos qualitativos desta síntese, para o autor decidir.

| Item | O que resolveria | Custo | Valor | Quem decide |
|---|---|---|---|---|
| Pedido do universo de inscritos e do conjunto de escolha efetivo (pedido 2 em [`pedidos_dados/`](../pedidos_dados/README.md)) | a margem extensiva: se a bolsa traz candidatos novos ou só reordena quem já se candidatou; é a única forma de responder à atração no sentido de Dal Bó, Finan e Rossi | baixo para o projeto (ofício já redigido), alto em prazo (depende do Ministério) | alto: a pergunta central fica sem resposta sem ele | autor (envio do pedido) |
| Ciclo 3 em 202703 (seis meses só com a competência publicada, completa e madura) | replicação fora da amostra do sinal de escolha do ciclo 2; oferta líquida município–mês; mais células para o preenchimento | baixo (plano prospectivo congelado) | alto: é o único teste novo sem pedido externo | calendário (maturidade dos dados) |
| Revalidação do T1.6 (uma das quatro opções do [doc 57b](57b_cenarios_P1_bolsa.md), §4, por adendo datado que registre a falha já vista) | o cenário de quantas vagas a mais com +R$ 5 mil, com vagas e candidatos fixos | médio (nova execução e auditoria) | médio: mesmo validado, o modelo não vê a margem extensiva e herda o IC largo do M1 | autor (pendente) |
| P3 e P4 com pré-tendências falhando: sensibilidade de Rambachan e Roth (HonestDiD) | quanto da diferença do pós sobrevive a violações de tendências paralelas do tamanho das vistas no pré (magnitude relativa M̄ ou suavidade) | baixo a médio (pós-resultado, rotulado como sensibilidade) | médio: diz se as associações de horas e produção são frágeis, sem criar identificação | autor (protocolo antes de rodar) |
| P3 e P4: outro grupo de comparação | células pedidas e não priorizadas (P5) ou candidatos não alocados por pouco (P6) como comparação da chegada e da trajetória; coortes do ciclo 3 como ainda não tratadas depois de 202703 | médio (protocolo novo, congelado antes de abrir) | médio a alto: a comparação pela priorização ou pela nota é menos dependente da escolha do candidato | autor (protocolo antes de rodar) |
| Folha de pagamento mensal (pedido 3) | se o anunciado é o recebido; presença efetiva em vez de vínculo cadastrado | baixo para o projeto, alto em prazo | médio | autor (envio do pedido) |
| Espera e fila (regulação) | o elo do acesso que a produção não mede | alto (fonte não pública) | alto para a política, baixo no curto prazo | autor (pedido externo) |

Sobre o P3 e o P4, as duas propostas acima são só propostas: escolher outro grupo de comparação ou outra
janela depois de ver o pré seria seleção retrospectiva, a menos que o protocolo fixe a regra antes de abrir os
outcomes. A sensibilidade de Rambachan e Roth não muda a estimativa; ela diz até onde a conclusão aguenta
uma tendência que o pré já mostrou.""")

    # 7. Proposta.
    partes.append("""## 7. Proposta ao autor sobre a hipótese central (PROPOSTA, não decisão)

> **Estatuto.** Nada aqui foi adotado. A escolha da hipótese central é do autor (doc 44, §7; doc 46; doc 51).

**Proposta.** Tratar como pergunta central a P1 (quanto a bolsa move a escolha entre vagas, relativa à distância
e à origem), com o preenchimento como teste de consistência, e não o contrário. Motivos:
- é a pergunta em que a bolsa age diretamente e em que o desenho compara vagas já abertas (doc 51, §1);
- é a única margem com sinal que resiste a vários testes, ainda que só no ciclo 2;
- o preenchimento, a presença e a oferta no CNES não se distinguem de zero com MDEs grandes, e o ciclo 3 é o
  próximo teste natural para as duas leituras.

**Alternativa.** Manter a hipótese original (H1 do doc 44: mais bolsa, mais preenchimento) e relatar o resultado como
inconclusivo, com os limites superiores e os MDEs da seção 4 por corte. A leitura correta, nos dois casos, é
"não se detecta, e os dados descartam só aumentos grandes", não "a bolsa é ineficaz".

**O que não muda em nenhum caso:** o contraste é o pacote do corte (ou o incentivo marginal na DiRD), não a
participação no PMM-E nem o Agora Tem Especialistas; os protocolos e os resultados dos blocos não são
reescritos; os pedidos externos e o ciclo 3 seguem como estão.""")

    # 8. Proveniência.
    lin = ["| Entrada | SHA-256 (início) | Papel |", "|---|---|---|"]
    for e in r["entradas"]:
        lin.append(f"| `{e['caminho']}` | `{e['sha256'][:16]}…` | {e['papel']} |")
    partes.append("## 8. Proveniência\n\n" + bloco("entradas", "\n".join(lin)))

    partes.append("""## 9. Reprodução

```bash
python3 scripts/rdd_bolsa/33_sintese_perguntas.py                  # saídas S57_* e este doc
python3 scripts/rdd_bolsa/33_sintese_perguntas.py --atualizar-doc  # só o doc, a partir do resumo
python3 -m pytest tests/test_sintese_perguntas.py
```""")
    texto = "\n\n".join(partes) + "\n"
    return texto, F.rastreio, seg, linhas_p


# ---------------------------------------------------------------------------
# Gravação
# ---------------------------------------------------------------------------

def _csv_mult(r: dict) -> pd.DataFrame:
    rows = []
    for f in r["holm"]:
        for m in f["membros"]:
            rows.append({"natureza_dos_dados": "EMPIRICO", "tipo": "holm", "familia": f["id"], "protocolo": f["protocolo"],
                         "descricao": f["descricao"], "linha": m["rotulo"], "p_gravado": m["p"]["v"],
                         "ajustado_gravado": m["gravado"]["v"], "ajustado_recalculado": m["recalculado"]["v"],
                         "diferenca": m["dif"]["v"], "rejeita_5pct": m["rejeita_recalculado"]})
    for f in r["bky"]:
        d = tabela(f["arquivo"])
        for k, i in enumerate(f["linhas"]):
            rows.append({"natureza_dos_dados": "EMPIRICO", "tipo": "bky", "familia": f["id"], "protocolo": f["protocolo"],
                         "descricao": f["descricao"], "linha": f"{f['arquivo']}#{i}",
                         "p_gravado": float(d.iloc[i][f["pcol"]]), "ajustado_gravado": f["q_gravado"][k],
                         "ajustado_recalculado": f["q_recalculado"][k],
                         "diferenca": abs(f["q_recalculado"][k] - f["q_gravado"][k]),
                         "rejeita_5pct": bool(f["q_recalculado"][k] < ALFA)})
    return pd.DataFrame(rows)


def _csv_poder(r: dict) -> pd.DataFrame:
    v = r["v"]
    rows = []
    specs = [("P1 (protocolo 40)", "e6_p1_tau", "e6_p1_lo", "e6_p1_hi", "e6_p1_mde"),
             ("P2 (protocolo 40)", "e7_p2_tau", "e7_p2_lo", "e7_p2_hi", "e7_p2_mde")]
    specs += [(f"{k} (protocolo 47)", f"kd1_{k}_tau", f"kd1_{k}_lo", f"kd1_{k}_hi", f"kd1_{k}_mde") for k in ("K1", "K2", "K3")]
    specs += [(f"{k} (protocolo 48)", f"n_{k}_tau", f"n_{k}_lo", f"n_{k}_hi", f"n_{k}_mde") for k in ("N1", "N2", "N3", "N4")]
    specs += [("P1a M1 (protocolo 52)", "m1_coef", "m1_lo", "m1_hi", "m1_mde"),
              ("P1a M1, razão de chances por +R$ 5 mil", "m1_rc", "m1_rc_lo", "m1_rc_hi", "m1_rc_mde"),
              ("R-P1 por +R$ 5 mil, p.p. (protocolo 58)", "R_P1_c5", "R_P1_lo", "R_P1_hi", "R_P1_mde"),
              ("R-P2 por +R$ 5 mil (protocolo 58)", "R_P2_c5", "R_P2_lo", "R_P2_hi", "R_P2_mde")]
    for y in ("y1", "y2", "y3", "y4", "y5"):
        for med in ("ultimo", "media"):
            b = f"p6_{y}_{med}"
            specs.append((f"P6 {y} {med} (protocolo 56)", f"{b}_est", f"{b}_lo", f"{b}_hi", f"{b}_mde"))
    for pn in ("todos", "c1"):
        for oid in ("a3p", "a3c"):
            for cn in ("300", "400", "emp"):
                b = f"{oid}_{pn}_{cn}"
                specs.append((f"pergunta central: {b} (p.p.)", f"{b}_tau", f"{b}_lo", f"{b}_hi", f"{b}_mde"))
    specs.append(("pergunta central: F1.1 empilhado", "f11_tau", "f11_lo", "f11_hi", "f11_mde"))
    for rot, a, lo, hi, mde in specs:
        rows.append({"natureza_dos_dados": "EMPIRICO", "linha": rot, "estimativa": v[a]["v"], "ic95_inf": v[lo]["v"],
                     "ic95_sup": v[hi]["v"], "maior_valor_compativel": v[hi]["v"], "mde_80": v[mde]["v"],
                     "fonte": v[a]["arquivo"]})
    return pd.DataFrame(rows)


def gravar(r: dict) -> None:
    texto, rastreio, seg, linhas_p = gerar_doc(r)
    out = ROOT / SAIDA
    r = dict(r)
    r["rastreio"] = rastreio
    r["segmentos_linguagem"] = seg
    (out / NOME_RESUMO).write_text(json.dumps(r, ensure_ascii=False, indent=1, sort_keys=False) + "\n", encoding="utf-8")
    pd.DataFrame([{"natureza_dos_dados": "EMPIRICO", **x} for x in linhas_p]).to_csv(out / NOME_TABELA, index=False)
    _csv_mult(r).to_csv(out / NOME_MULT, index=False, float_format="%.10g")
    _csv_poder(r).to_csv(out / NOME_PODER, index=False, float_format="%.10g")
    DOC.write_text(texto, encoding="utf-8")


def ler_resumo() -> dict:
    r = json.loads((ROOT / SAIDA / NOME_RESUMO).read_text(encoding="utf-8"))
    r.pop("rastreio", None)
    r.pop("segmentos_linguagem", None)
    return r


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--atualizar-doc", action="store_true", help="só regrava o doc a partir do resumo gravado")
    args = ap.parse_args(argv)
    if args.atualizar_doc:
        texto, _, _, _ = gerar_doc(ler_resumo())
        DOC.write_text(texto, encoding="utf-8")
        print(f"doc regravado: {DOC.relative_to(ROOT)}")
        return 0
    try:
        r = construir()
    except FalhaFechada as e:
        print(f"FALHA FECHADA: {e}", file=sys.stderr)
        return 1
    gravar(r)
    print(f"gravado: {SAIDA}/{NOME_RESUMO}, {NOME_TABELA}, {NOME_MULT}, {NOME_PODER}; {DOC.relative_to(ROOT)}")
    print(f"divergências de Holm/BKY: {len(r['divergencias'])}")
    for d in r["divergencias"]:
        print(f"  - {d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
