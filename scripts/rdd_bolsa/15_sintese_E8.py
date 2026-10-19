"""E8 do protocolo multi-outcome da bolsa: síntese, Holm das primárias e tabela por elo da cadeia.

Protocolo congelado: `docs/06_execucao/40_protocolo_multioutcome_rdd_bolsa.md`
(§7: duas hipóteses primárias com Holm; secundárias com q BKY por família;
equivalência contra +10 p.p. de preenchimento e +25% de candidaturas; §11:
tarefa E8) e `output/rdd_bolsa/protocolo_E6_multioutcome.json`.

O que este script faz
---------------------
- Lê as saídas já auditadas do E3, E5, E6, E7 e E9 (`output/rdd_bolsa/`). Não
  estima nada de novo. A única conta inferencial é o ajuste de Holm (1979) sobre
  os dois p primários do protocolo: P1 (índice de atração-presença, E6,
  `p1_para_holm`, conferido contra a linha principal empilhada do CSV) e P2 (F3.1
  por DiRD em U, cortes empilhados, E7, `p2_para_holm`, conferido contra o CSV).
  Usa `rdd_lib.holm`.
- Copia das saídas, sem recalcular, as estimativas principais empilhadas de cada
  família, os IC e os q BKY; compara os limites superiores dos IC com as
  referências do protocolo (+10 p.p. e +25%); conta, nos CSV do E9 e do E7, os
  fatos de robustez e do estudo de evento que a síntese cita.
- Lê citações de magnitude da literatura só de
  `docs/03_literatura_empirica/20_*.md` e do protocolo (texto copiado da linha da
  tabela; falha fechada se a linha não existir).
- Grava `output/rdd_bolsa/E8_resumo.json` e `output/rdd_bolsa/E8_tabela_sintese.csv`
  (natureza dos dados: EMPIRICO) e regrava os blocos gerados de
  `docs/06_execucao/44_sintese_rdd_bolsa_multioutcome.md`. Os blocos do doc são
  gerados só a partir das duas saídas do E8.

Contraste
---------
RDD em nível (E6): pacote do corte (bolsa anunciada + outras regras federais nos
mesmos cortes, auditoria 18). DiRD (E7): bolsa + variação, entre pré e pós, das
descontinuidades das outras políticas. E9: degrau da bolsa na escolha da 1ª
opção entre células, com o IVS em spline contínuo (realocação, não total de
candidatos). Nenhum é efeito da participação no PMM-E nem do Agora Tem
Especialistas.

Falha fechada
-------------
Para se: uma entrada faltar ou não for EMPIRICO; o p de P1 ou de P2 do resumo
diferir da linha do CSV; uma citação da literatura não for encontrada; uma
afirmação qualitativa da síntese deixar de valer nos dados (por exemplo, o Holm
rejeitar uma primária). Nesse caso o texto da síntese tem de ser revisto pelo
autor; o script não troca a redação sozinho.

Uso
---
    python3 scripts/rdd_bolsa/15_sintese_E8.py                 # saídas + blocos do doc 44
    python3 scripts/rdd_bolsa/15_sintese_E8.py --atualizar-doc # só regrava os blocos do doc 44
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
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DIR_RDD = ROOT / "scripts" / "rdd_bolsa"


def _importar(caminho: Path, nome: str):
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    return mod


L = _importar(DIR_RDD / "rdd_lib.py", "rdd_lib_e8")

OUT = ROOT / "output" / "rdd_bolsa"
E3_EST = OUT / "E3_estimativas.csv"
E3_STATUS = OUT / "E3_status.json"
E5_RESUMO = OUT / "E5_resumo.json"
E6_EST = OUT / "E6_estimativas.csv"
E6_DIAG = OUT / "E6_diagnosticos.csv"
E6_RESUMO = OUT / "E6_resumo.json"
E7_EST = OUT / "E7_estimativas.csv"
E7_EVENTO = OUT / "E7_estudo_evento.csv"
E7_RESUMO = OUT / "E7_resumo.json"
E9_EST = OUT / "E9_estimativas.csv"
E9_EFM = OUT / "E9_efeitos_marginais.csv"
E9_ROB = OUT / "E9_robustez_pos_auditoria.csv"
E9_RESUMO = OUT / "E9_resumo.json"
PROTOCOLO_MD = ROOT / "docs" / "06_execucao" / "40_protocolo_multioutcome_rdd_bolsa.md"
PROTOCOLO_JSON = OUT / "protocolo_E6_multioutcome.json"
LITERATURA = ROOT / "docs" / "03_literatura_empirica" / "20_evidencia_empirica_hipotese_remuneracao_preenchimento.md"
DOC44 = ROOT / "docs" / "06_execucao" / "44_sintese_rdd_bolsa_multioutcome.md"

NOME_RESUMO = "E8_resumo.json"
NOME_TABELA = "E8_tabela_sintese.csv"

# Parâmetros do protocolo (§6, §7). Não são resultados.
ALFA = 0.05
REF_PREENCHIMENTO = 0.10      # +10 p.p. (§7)
REF_CANDIDATURAS = 0.25       # +25% (§7)
CORTES = ("0.300", "0.400")
EMPILHADO = "empilhado"
ESPEC_CONVENCIONAIS_F1 = ("principal", "sensibilidade_h", "S2_donut", "ponderado_celulas", "nivel_celula")
JANELAS_ANTES_REF = ("pre_extra", "entre_pre_extra_e_pre", "pre")

# Literatura: só linhas da tabela-resumo do doc 20 da seção 03 (texto copiado da fonte, conferido aqui).
LIT_IDS = ("A1", "A2", "A8", "B1", "B3", "C1", "C2")
# Trechos fora da tabela, procurados literalmente na fonte.
LIT_TRECHOS = (
    (LITERATURA, "candidaturas **+26%**", "Dal Bó, Finan & Rossi (2013): efeito do salário alto sobre candidaturas"),
    (PROTOCOLO_MD, "Dal Bó, Finan e Rossi, 2013:\n+15 p.p. de aceitação com +33% de salário",
     "protocolo §1: maior efeito plausível pela literatura"),
)

PRINCIPAL_E9 = "spline_linear__bolsa_linear"
COND = "logit_condicional_1a_opcao"


# ---------------------------------------------------------------------------
# Utilitários
# ---------------------------------------------------------------------------

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def rotulo(path: Path) -> str:
    p = Path(path).resolve()
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


class FalhaFechada(RuntimeError):
    """Uma validação ou uma afirmação da síntese não vale nos dados."""


def exigir(cond: bool, msg: str) -> None:
    if not cond:
        raise FalhaFechada(msg)


def f(v) -> float:
    return float("nan") if v is None or pd.isna(v) else float(v)


def ler_csv(path: Path) -> pd.DataFrame:
    exigir(path.exists(), f"entrada ausente: {rotulo(path)}")
    d = pd.read_csv(path, dtype={"corte": str, "ciclo": str, "competencia": str})
    if "natureza_dos_dados" in d.columns:
        exigir(set(d["natureza_dos_dados"].unique()) == {"EMPIRICO"}, f"{rotulo(path)} tem linha nao EMPIRICO")
    return d


def ler_json(path: Path) -> dict:
    exigir(path.exists(), f"entrada ausente: {rotulo(path)}")
    d = json.loads(path.read_text(encoding="utf-8"))
    if "natureza_dos_dados" in d:
        exigir(d["natureza_dos_dados"] == "EMPIRICO", f"{rotulo(path)} nao e EMPIRICO")
    return d


def uma(df: pd.DataFrame, msg: str) -> pd.Series:
    exigir(len(df) == 1, f"{msg}: esperado 1 linha, achadas {len(df)}")
    return df.iloc[0]


# ---------------------------------------------------------------------------
# Entradas
# ---------------------------------------------------------------------------

ENTRADAS = [
    (E3_EST, "E3: ancora do ciclo 1 (F1.3 e presenca por corte)", "07_estimar_E3_rdd_completa.py", "2026-10-14",
     "P1 (ciclo 1) e P2 (ciclo 2)", "populacao x outcome x corte x h", "populacao, outcome, corte, h",
     "especificacao == principal"),
    (E3_STATUS, "E3: status e contraste", "07_estimar_E3_rdd_completa.py", "2026-10-14", "-", "-", "-", "status"),
    (E5_RESUMO, "E5: MDE de 80% do F1.3 do ciclo 1 (exploratorio, pos-resultado)", "11_inferencia_alternativa.py",
     "2026-10-18", "P1", "corte", "corte", "decomposicao_ic_y1.mde_80_principal"),
    (E6_EST, "E6: F0, F1, F2, F4 e P1 (RDD em nivel = pacote do corte)", "13_estimar_E6_funil.py", "2026-10-18",
     "U, G3, V1-V3", "linha de especificacao", "familia, outcome, populacao, ciclo, corte, especificacao, h",
     "principal, sensibilidade_h, S2_donut, ponderado_celulas, nivel_celula, poisson_local, ic_honesto (fator_M = 1)"),
    (E6_DIAG, "E6: densidade e balanco de V1 em 0,400", "13_estimar_E6_funil.py", "2026-10-18", "U, G3, V1-V3",
     "populacao x corte x diagnostico", "populacao, corte, diagnostico, variavel",
     "populacao == V1, corte == 0.400, especificacao == principal"),
    (E6_RESUMO, "E6: p de P1 para o Holm e contraste", "13_estimar_E6_funil.py", "2026-10-18", "-", "-", "-",
     "p1_para_holm, contraste"),
    (E7_EST, "E7: F3 (DiRD no CNES) e niveis", "14_estimar_E7_dird_cnes.py", "2026-10-19",
     "U (5565 municipios) e V1", "linha de especificacao", "outcome, populacao, corte, especificacao, h",
     "principal, nivel_pre, nivel_pre_extra, placebo_pre, S5_pre_menos_pre_extra, ic_honesto (fator_M = 1)"),
    (E7_EVENTO, "E7: estudo de evento da DiRD", "14_estimar_E7_dird_cnes.py", "2026-10-19", "competencias 202201-202608",
     "outcome x populacao x corte x competencia", "outcome_id, populacao, corte, competencia",
     "F3.1 (U, V1) e F3.P1 (U)"),
    (E7_RESUMO, "E7: p de P2 para o Holm e contraste", "14_estimar_E7_dird_cnes.py", "2026-10-19", "-", "-", "-",
     "p2_para_holm, contraste"),
    (E9_EST, "E9: logit condicional da 1a opcao (coeficiente da bolsa)", "16_estimar_E9_escolha.py", "2026-10-18",
     "ciclos 1, 2, 3 e empilhado", "modelo x conjunto x especificacao x termo", "ciclo, modelo, conjunto, especificacao, termo",
     "termo == bolsa_mil; modelo condicional; conjunto principal"),
    (E9_EFM, "E9: razao de chances e efeito na probabilidade por +R$ 5 mil", "16_estimar_E9_escolha.py",
     "2026-10-18", "ciclos 1, 2, 3 e empilhado", "modelo x conjunto x especificacao x quantidade",
     "ciclo, modelo, conjunto, especificacao, quantidade", "especificacao principal; termo == bolsa_mil"),
    (E9_ROB, "E9: robustez pos-auditoria (fora do protocolo)", "16_estimar_E9_escolha.py", "2026-10-18",
     "ciclos 1, 2, 3, empilhado, 1+3", "analise x ciclo x estatistica", "analise, ciclo, estatistica",
     "todas as linhas (no_protocolo = False)"),
    (E9_RESUMO, "E9: mapa faixa -> bolsa e natureza", "16_estimar_E9_escolha.py", "2026-10-18", "-", "-", "-",
     "mapa_faixa_bolsa.mapa_faixa_para_bolsa_mil"),
    (PROTOCOLO_MD, "protocolo congelado (texto canonico)", "doc 40", "2026-10-18", "§§1-16", "documento", "-",
     "§7 (Holm, BKY, referencias); §1 (citacao de Dal Bo et al.)"),
    (PROTOCOLO_JSON, "protocolo congelado (maquina)", "protocolo_E6_multioutcome.json", "2026-10-18", "-",
     "documento", "-", "-"),
    (LITERATURA, "citacoes de magnitude da literatura (texto, nao resultado)", "docs/03_literatura_empirica/20",
     "2026-10-05", "tabela-resumo", "linha da tabela", "id do estudo", f"ids {', '.join(LIT_IDS)}"),
]


def bloco_entradas() -> list[dict]:
    out = []
    for path, papel, fonte, data_ref, cobertura, unidade, chaves, filtros in ENTRADAS:
        exigir(path.exists(), f"entrada ausente: {rotulo(path)}")
        out.append({"caminho": rotulo(path), "sha256": sha256(path), "bytes": path.stat().st_size, "papel": papel,
                    "fonte": fonte, "data_referencia": data_ref, "cobertura": cobertura, "unidade": unidade,
                    "chaves": chaves, "filtros": filtros})
    return out


# ---------------------------------------------------------------------------
# Leitura das linhas
# ---------------------------------------------------------------------------

def linha_e6(e6: pd.DataFrame, outcome: str, populacao: str, ciclo: str, corte: str = EMPILHADO,
             espec: str = "principal", h: float | None = None, fator_M: float | None = None) -> pd.Series:
    m = ((e6["outcome"] == outcome) | (e6["outcome_id"] == outcome)) & (e6["populacao"] == populacao) \
        & (e6["ciclo"] == ciclo) & (e6["corte"] == corte) & (e6["especificacao"] == espec)
    if h is not None:
        m &= np.isclose(e6["h"].astype(float), h)
    if fator_M is not None:
        m &= np.isclose(e6["fator_M"].astype(float), fator_M)
    return uma(e6[m], f"E6 {outcome} {populacao} {ciclo} {corte} {espec} h={h}")


def linha_e7(e7: pd.DataFrame, outcome_id: str, populacao: str, corte: str = EMPILHADO, espec: str = "principal",
             fator_M: float | None = None) -> pd.Series:
    m = (e7["outcome_id"] == outcome_id) & (e7["populacao"] == populacao) & (e7["corte"] == corte) \
        & (e7["especificacao"] == espec)
    if fator_M is not None:
        m &= np.isclose(e7["fator_M"].astype(float), fator_M)
    return uma(e7[m], f"E7 {outcome_id} {populacao} {corte} {espec}")


def est_basica(r: pd.Series) -> dict:
    return {"tau": f(r["tau"]), "ic95_inf": f(r["ic95_inf"]), "ic95_sup": f(r["ic95_sup"]), "p_valor": f(r["p_valor"])}


def resumo_linha(r: pd.Series, fonte: str) -> dict:
    d = {"familia": r["familia"], "outcome_id": r["outcome_id"], "outcome": r["outcome"], "populacao": r["populacao"],
         "ciclo": str(r["ciclo"]) if "ciclo" in r.index else "-", "corte": r["corte"],
         "n_abaixo": f(r["n_abaixo"]), "n_acima": f(r["n_acima"]), **est_basica(r),
         "q_bky": f(r.get("q_bky")), "unidade": r["unidade"], "fonte": fonte}
    return d


# ---------------------------------------------------------------------------
# Holm das primárias
# ---------------------------------------------------------------------------

def holm_primarias(e6: pd.DataFrame, r6: dict, e7: pd.DataFrame, r7: dict) -> dict:
    p1 = linha_e6(e6, "P1", "V1+V2+V3", "1+2+3")
    p2 = linha_e7(e7, "F3.1", "U")
    # Conferência: o p do resumo é o da linha do CSV.
    for k in ("tau", "p_valor", "ic95_inf", "ic95_sup"):
        exigir(math.isclose(f(p1[k]), r6["p1_para_holm"][k], rel_tol=1e-12, abs_tol=1e-15),
               f"P1: {k} do E6_resumo difere do CSV")
        exigir(math.isclose(f(p2[k]), r7["p2_para_holm"][k], rel_tol=1e-12, abs_tol=1e-15),
               f"P2: {k} do E7_resumo difere do CSV")
    ps = [f(p1["p_valor"]), f(p2["p_valor"])]
    adj = L.holm(ps)
    out = {
        "metodo": "Holm (1979), m = 2, alfa = 0,05 (protocolo §7); rdd_lib.holm",
        "P1": {"hipotese": "índice de atração-presença (KLK de F1.1, F1.2, F1.3 e F2.1), ciclos e cortes empilhados, "
                            "V1+V2+V3, h = 0,050, CR1 por município",
               "fonte": f"{rotulo(E6_RESUMO)}: p1_para_holm = {rotulo(E6_EST)}: outcome_id == P1, populacao == "
                        "V1+V2+V3, corte == empilhado, especificacao == principal",
               "contraste": "pacote do corte (RDD em nível)", "unidade": str(p1["unidade"]),
               **est_basica(p1), "p_holm": float(adj[0]), "rejeita_holm_5pct": bool(adj[0] < ALFA)},
        "P2": {"hipotese": "F3.1 (vínculos nas CBO-alvo por 10 mil hab.) por DiRD em U, cortes empilhados",
               "fonte": f"{rotulo(E7_RESUMO)}: p2_para_holm = {rotulo(E7_EST)}: outcome_id == F3.1, populacao == U, "
                        "corte == empilhado, especificacao == principal",
               "contraste": "DiRD: bolsa + variação, entre pré e pós, das descontinuidades das co-políticas",
               "unidade": str(p2["unidade"]), **est_basica(p2), "p_holm": float(adj[1]),
               "rejeita_holm_5pct": bool(adj[1] < ALFA)},
    }
    out["alguma_rejeitada"] = out["P1"]["rejeita_holm_5pct"] or out["P2"]["rejeita_holm_5pct"]
    return out


# ---------------------------------------------------------------------------
# Famílias
# ---------------------------------------------------------------------------

def resumo_testes(df: pd.DataFrame) -> dict:
    b = df[(df["especificacao"] == "principal") & (df["entra_bky"] == True)]  # noqa: E712
    return {"linhas_principais_no_bky": int(len(b)), "p_menor_005": int((b["p_valor"] < ALFA).sum()),
            "q_menor_005": int((b["q_bky"] < ALFA).sum()), "menor_p": f(b["p_valor"].min()),
            "menor_q": f(b["q_bky"].min()), "salto_negativo": int((b["tau"] < 0).sum()),
            "outcomes_com_p_menor_005": sorted(set(b.loc[b["p_valor"] < ALFA, "outcome"].astype(str)))}


def familias(e6: pd.DataFrame, e7: pd.DataFrame) -> dict:
    out = {}
    for fam in ("F0", "F1", "F2", "F4"):
        sub = e6[e6["familia"] == fam]
        emp = sub[(sub["especificacao"] == "principal") & (sub["corte"] == EMPILHADO) & (sub["entra_bky"] == True)]  # noqa: E712
        out[fam] = {"resumo_testes": resumo_testes(sub),
                    "linhas_empilhadas": [resumo_linha(r, rotulo(E6_EST)) for _, r in emp.iterrows()]}
    f3 = e7[e7["familia"] == "F3"]
    emp = f3[(f3["especificacao"] == "principal") & (f3["corte"] == EMPILHADO) & (f3["entra_bky"] == True)]  # noqa: E712
    out["F3"] = {"resumo_testes": resumo_testes(f3),
                 "linhas_empilhadas": [resumo_linha(r, rotulo(E7_EST)) for _, r in emp.iterrows()]}
    return out


# ---------------------------------------------------------------------------
# O que fica descartado (§7)
# ---------------------------------------------------------------------------

def descarte(e6: pd.DataFrame, e3: pd.DataFrame, e5: dict) -> dict:
    out = {"referencias": {"preenchimento_pp": REF_PREENCHIMENTO, "candidaturas_relativo": REF_CANDIDATURAS},
           "condicoes": ["IC 95% convencional (HC1/CR1 por municipio), nao o IC honesto",
                         "aproximacao local linear adequada no corte (sem vies de suavizacao relevante)",
                         "contraste = pacote do corte, nao a bolsa isolada"],
           "preenchimento": [], "candidaturas_poisson": []}
    alvos = [("F1.3", "V1+V2+V3", "1+2+3"), ("F1.4", "V1+V2", "1+2"),
             ("F1.3", "V1", "1"), ("F1.3", "V2", "2"), ("F1.3", "V3", "3"), ("F1.4", "V1", "1"), ("F1.4", "V2", "2")]
    for oid, pop, cic in alvos:
        r = linha_e6(e6, oid, pop, cic)
        hon = linha_e6(e6, oid, pop, cic, espec="ic_honesto", fator_M=1.0)
        conv = e6[(e6["outcome_id"] == oid) & (e6["populacao"] == pop) & (e6["ciclo"] == cic)
                  & (e6["corte"] == EMPILHADO) & (e6["especificacao"].isin(ESPEC_CONVENCIONAIS_F1))
                  & (e6["no_protocolo"] == True)]  # noqa: E712
        maior_sup = conv.loc[conv["ic95_sup"].idxmax()]
        out["preenchimento"].append({
            "outcome_id": oid, "populacao": pop, "ciclo": cic, "corte": EMPILHADO, **est_basica(r),
            "exclui_referencia": bool(f(r["ic95_sup"]) < REF_PREENCHIMENTO),
            "ic_honesto_sup_M1": f(hon["ic_honesto_sup"]),
            "ic_honesto_exclui_referencia": bool(f(hon["ic_honesto_sup"]) < REF_PREENCHIMENTO),
            "especificacoes_convencionais": sorted(set(conv["especificacao"])),
            "n_especificacoes_convencionais": int(len(conv)),
            "maior_ic95_sup_convencional": f(maior_sup["ic95_sup"]),
            "especificacao_do_maior_sup": f"{maior_sup['especificacao']}, h = {f(maior_sup['h']):.3f}",
            "todas_convencionais_excluem_referencia": bool((conv["ic95_sup"] < REF_PREENCHIMENTO).all()),
            "convencionais_com_p_menor_005": [
                {"especificacao": x["especificacao"], "h": f(x["h"]), **est_basica(x)}
                for _, x in conv[conv["p_valor"] < ALFA].sort_values(["especificacao", "h"]).iterrows()],
            "convencionais_todas_com_salto_negativo": bool((conv["tau"] < 0).all()),
        })
    pois = e6[(e6["outcome_id"] == "F1.1") & (e6["especificacao"] == "poisson_local")]
    for _, r in pois.sort_values(["ciclo", "corte"]).iterrows():
        out["candidaturas_poisson"].append({
            "populacao": r["populacao"], "ciclo": r["ciclo"], "corte": r["corte"],
            "efeito_relativo": f(r["efeito_relativo"]), "ic95_inf": f(r["efeito_relativo_ic95_inf"]),
            "ic95_sup": f(r["efeito_relativo_ic95_sup"]), "p_valor": f(r["p_valor"]),
            "exclui_referencia": bool(f(r["efeito_relativo_ic95_sup"]) < REF_CANDIDATURAS)})
    out["candidaturas_poisson_n"] = len(out["candidaturas_poisson"])
    out["candidaturas_poisson_n_excluem"] = int(sum(x["exclui_referencia"] for x in out["candidaturas_poisson"]))
    out["candidaturas_nota"] = ("o Poisson local so existe por ciclo e corte (a rdd_lib nao tem versao empilhada); "
                                "nao ha linha empilhada de candidaturas em escala relativa")
    # Âncora: E3 (F1.3 do ciclo 1, por corte) e MDE do E5.
    anc = []
    for c in (0.3, 0.4):
        r = uma(e3[(e3["outcome"] == "fracao_celulas_ch1_com_confirmacao_ou_homologacao") & (e3["populacao"] == "P1")
                   & (e3["especificacao"] == "principal") & np.isclose(e3["corte"].astype(float), c)], f"E3 {c}")
        mde = [d for d in e5["decomposicao_ic_y1"] if math.isclose(float(d["corte"]), c)]
        exigir(len(mde) == 1, f"E5 MDE {c}")
        anc.append({"corte": f"{c:.3f}", **est_basica(r), "mde_80": float(mde[0]["mde_80_principal"]),
                    "exclui_referencia": bool(f(r["ic95_sup"]) < REF_PREENCHIMENTO)})
    out["ancora_E3_ciclo1"] = anc
    return out


# ---------------------------------------------------------------------------
# E9: escolha
# ---------------------------------------------------------------------------

def e9_sintese(e9: pd.DataFrame, efm: pd.DataFrame, rob: pd.DataFrame) -> dict:
    out = {"contraste": "degrau de +R$ 5 mil na escolha da 1a opcao entre celulas do mesmo curso e ciclo "
                        "(logit condicional; IVS em spline continuo com nos em 0,300 e 0,400); realocacao entre "
                        "celulas, condicional a candidatar-se; nao e efeito sobre o total de candidatos",
           "estado": "secundario e exploratorio (protocolo §12); robustez pos-auditoria fora do protocolo",
           "principal": {}}
    base = e9[(e9["modelo"] == COND) & (e9["conjunto"] == "principal") & (e9["termo"] == "bolsa_mil")]
    for cic in ("1", "2", "3", "empilhado"):
        r = uma(base[(base["ciclo"] == cic) & (base["especificacao"] == PRINCIPAL_E9)], f"E9 {cic}")
        q = efm[(efm["modelo"] == COND) & (efm["conjunto"] == "principal") & (efm["especificacao"] == PRINCIPAL_E9)
                & (efm["termo"] == "bolsa_mil") & (efm["ciclo"] == cic)].set_index("quantidade")
        rc, dp, pb, vr = (q.loc[k] for k in ("razao_chances_por_5mil", "variacao_prob_media_pp", "prob_media_base_pp",
                                             "variacao_relativa_media"))
        out["principal"][cic] = {
            "coef_por_mil": f(r["coef"]), "ic95_inf": f(r["ic95_inf"]), "ic95_sup": f(r["ic95_sup"]), "p": f(r["p"]),
            "g_conjuntos": f(r["g_conjuntos"]), "n_candidatos": f(r["n_candidatos"]),
            "rc_5mil": f(rc["estimativa"]), "rc_5mil_ic95": [f(rc["ic95_inf"]), f(rc["ic95_sup"])],
            "dprob_pp": f(dp["estimativa"]), "dprob_pp_ic95": [f(dp["ic95_inf"]), f(dp["ic95_sup"])],
            "prob_base_pp": f(pb["estimativa"]),
            "variacao_relativa": f(vr["estimativa"]), "variacao_relativa_ic95": [f(vr["ic95_inf"]), f(vr["ic95_sup"])],
            "ic_exclui_zero": bool(f(r["ic95_inf"]) > 0 or f(r["ic95_sup"]) < 0)}

    def rv(analise, ciclo, estat, col="valor"):
        return f(uma(rob[(rob["analise"] == analise) & (rob["ciclo"] == ciclo) & (rob["estatistica"] == estat)],
                     f"E9 rob {analise} {ciclo} {estat}")[col])

    def rob_row(analise, ciclo, estat):
        return uma(rob[(rob["analise"] == analise) & (rob["ciclo"] == ciclo) & (rob["estatistica"] == estat)],
                   f"E9 rob {analise} {ciclo} {estat}")

    def esp(cic, nome):
        return uma(base[(base["ciclo"] == cic) & (base["especificacao"] == f"ROBUSTEZ_POS_AUDITORIA:{nome}")],
                   f"E9 {cic} {nome}")

    def placebo(cic):
        a = "placebo_cortes"
        return {"n_placebos": rv(a, cic, "n_placebos"), "t_real": rv(a, cic, "t_real"),
                "fracao_abs_t_maior_1_96": rv(a, cic, "fracao_abs_t_placebo_maior_que_1_96"),
                "n_abs_t_placebo_ge_real": rv(a, cic, "n_abs_t_placebo_maior_ou_igual_ao_real"),
                "p_posto": rv(a, cic, "p_posto")}

    janelas_lin = ("nos_cada_0050__spline_linear__bolsa_linear", "janela_0100__spline_linear__bolsa_linear",
                   "janela_0050__spline_linear__bolsa_linear", "janela_0025__spline_linear__bolsa_linear")
    c2 = {
        "p_cr1": out["principal"]["2"]["p"],
        "p_cv3": rv("cv3_cluster_conjunto", "2", "coef_ep_cv3", "p"),
        "p_score_rademacher": rv("score_bootstrap_rademacher_cluster_conjunto", "2", "p_H0_beta_igual_0", "p"),
        "p_score_webb": rv("score_bootstrap_webb_cluster_conjunto", "2", "p_H0_beta_igual_0", "p"),
        "ic_inversao": [f(rob_row("ic_inversao_score_rademacher_cluster_conjunto", "2", "coef_ic95_inversao")[k])
                        for k in ("ic95_inf", "ic95_sup")],
        "placebo": placebo("2"),
        "spline_cubico": {k: f(esp("2", "spline_cubico__bolsa_linear")[k]) for k in ("coef", "ic95_inf", "ic95_sup", "p")},
        "spline_linear_janelas_p": {j: f(esp("2", j)["p"]) for j in janelas_lin},
    }
    c2["robusto_inferencia_poucos_clusters"] = bool(
        max(c2["p_cr1"], c2["p_cv3"], c2["p_score_rademacher"], c2["p_score_webb"]) < ALFA and c2["ic_inversao"][0] > 0)
    c2["nenhum_placebo_supera"] = bool(c2["placebo"]["n_abs_t_placebo_ge_real"] == 0)
    c2["sobrevive_spline_linear_flexivel_e_janelas"] = bool(max(c2["spline_linear_janelas_p"].values()) < ALFA)
    c2["ic_cubico_contem_zero"] = bool(c2["spline_cubico"]["ic95_inf"] <= 0 <= c2["spline_cubico"]["ic95_sup"])
    out["ciclo2"] = c2

    c13 = uma(base[(base["ciclo"] == "1+3")], "E9 ciclos 1+3")
    emp = {
        "placebo": placebo("empilhado"),
        "spline_cubico": {k: f(esp("empilhado", "spline_cubico__bolsa_linear")[k])
                          for k in ("coef", "ic95_inf", "ic95_sup", "p")},
        "ciclos_1_e_3": {k: f(c13[k]) for k in ("coef", "ic95_inf", "ic95_sup", "p")},
        "cochran_Q": {"valor": rv("heterogeneidade_ciclos", "1,2,3", "cochran_Q"),
                      "p": rv("heterogeneidade_ciclos", "1,2,3", "cochran_Q", "p")},
        "z_ciclo2_menos_ciclo3": {"valor": rv("heterogeneidade_ciclos", "2 vs 3", "z_ciclo2_menos_ciclo3"),
                                  "p": rv("heterogeneidade_ciclos", "2 vs 3", "z_ciclo2_menos_ciclo3", "p")},
        "cluster_curso": {
            "p_score_rademacher": rv("score_bootstrap_rademacher_cluster_curso", "empilhado", "p_H0_beta_igual_0", "p"),
            "p_score_webb": rv("score_bootstrap_webb_cluster_curso", "empilhado", "p_H0_beta_igual_0", "p"),
            "ic_inversao": [f(rob_row("ic_inversao_score_rademacher_cluster_curso", "empilhado",
                                      "coef_ic95_inversao")[k]) for k in ("ic95_inf", "ic95_sup")]},
    }
    emp["placebo_acima_do_nominal"] = bool(emp["placebo"]["fracao_abs_t_maior_1_96"] > ALFA)
    emp["p_posto_acima_005"] = bool(emp["placebo"]["p_posto"] > ALFA)
    emp["ic_cubico_contem_zero"] = bool(emp["spline_cubico"]["ic95_inf"] <= 0 <= emp["spline_cubico"]["ic95_sup"])
    emp["ciclos_1_e_3_ic_contem_zero"] = bool(emp["ciclos_1_e_3"]["ic95_inf"] <= 0 <= emp["ciclos_1_e_3"]["ic95_sup"])
    emp["heterogeneidade_rejeitada"] = bool(emp["cochran_Q"]["p"] < ALFA)
    emp["fragil"] = bool(emp["p_posto_acima_005"] or emp["ic_cubico_contem_zero"] or emp["ciclos_1_e_3_ic_contem_zero"])
    out["empilhado"] = emp
    out["ciclos_1_e_3_principal_ic_contem_zero"] = bool(
        not out["principal"]["1"]["ic_exclui_zero"] and not out["principal"]["3"]["ic_exclui_zero"])
    return out


# ---------------------------------------------------------------------------
# E7: estudo de evento e ameaças
# ---------------------------------------------------------------------------

def _rodadas(serie: pd.DataFrame) -> list[pd.DataFrame]:
    s = serie.sort_values("competencia").reset_index(drop=True)
    sig = (s["p_valor"] < ALFA).fillna(False).to_numpy()
    rod, ini = [], None
    for i, v in enumerate(sig):
        if v and ini is None:
            ini = i
        if (not v or i == len(sig) - 1) and ini is not None:
            fim = i if v else i - 1
            rod.append(s.iloc[ini:fim + 1])
            ini = None
    return rod


def _comp(c: str) -> str:
    return f"{c[:4]}-{c[4:]}"


def e7_sintese(e7: pd.DataFrame, ev: pd.DataFrame) -> dict:
    out = {}
    s = ev[(ev["outcome_id"] == "F3.1") & (ev["populacao"] == "U") & (ev["corte"] == "0.300")
           & ev["tau"].notna()].sort_values("competencia")
    rod = _rodadas(s)
    exigir(len(rod) >= 1, "E7: nenhum mes com p < 0,05 em F3.1 U 0,300")
    maior = max(rod, key=len)
    antes = s[s["janela"].isin(JANELAS_ANTES_REF)]
    pos = s[s["janela"] == "pos"]
    apos = pos[pos["competencia"] > maior["competencia"].max()]
    out["f31_U_0300"] = {
        "maior_sequencia_p_menor_005": {"n_meses": int(len(maior)), "inicio": _comp(maior["competencia"].min()),
                                        "fim": _comp(maior["competencia"].max()),
                                        "janela": sorted(maior["janela"].unique().tolist()),
                                        "tau_min": f(maior["tau"].min()), "tau_max": f(maior["tau"].max()),
                                        "p_max": f(maior["p_valor"].max())},
        "meses_pos_depois_da_sequencia": int(len(apos)),
        "meses_pos_depois_da_sequencia_p_menor_005": int((apos["p_valor"] < ALFA).sum()),
        "meses_antes_da_referencia": int(len(antes)),
        "meses_antes_da_referencia_p_menor_005": int((antes["p_valor"] < ALFA).sum()),
        "media_tau_pre_extra": f(s[s["janela"] == "pre_extra"]["tau"].mean()),
        "media_tau_pre": f(s[s["janela"] == "pre"]["tau"].mean()),
        "primeiro_mes_pos": _comp(pos["competencia"].min()),
        "media_tau_pos": f(pos["tau"].mean()),
        "dird_principal": est_basica(linha_e7(e7, "F3.1", "U", "0.300")),
        "nivel_pre_extra": est_basica(linha_e7(e7, "F3.1", "U", "0.300", "nivel_pre_extra")),
        "nivel_pre": est_basica(linha_e7(e7, "F3.1", "U", "0.300", "nivel_pre")),
    }
    o = out["f31_U_0300"]
    o["descontinuidade_preexistente"] = bool(o["nivel_pre_extra"]["ic95_sup"] < 0 and o["nivel_pre"]["ic95_sup"] < 0)
    s4 = ev[(ev["outcome_id"] == "F3.1") & (ev["populacao"] == "U") & (ev["corte"] == "0.400") & ev["tau"].notna()]
    out["f31_U_0400_pos_p_menor_005"] = int((s4[s4["janela"] == "pos"]["p_valor"] < ALFA).sum())
    # Generalistas em 0,400.
    g = ev[(ev["outcome_id"] == "F3.P1") & (ev["populacao"] == "U") & (ev["corte"] == "0.400") & ev["tau"].notna()]
    gpe = g[g["janela"] == "pre_extra"].sort_values("competencia")
    out["generalistas_U_0400"] = {
        "pre_extra_meses": int(len(gpe)), "pre_extra_p_menor_005": int((gpe["p_valor"] < ALFA).sum()),
        "primeiro_mes": _comp(gpe["competencia"].iloc[0]), "tau_primeiro_mes": f(gpe["tau"].iloc[0]),
        "p_primeiro_mes": f(gpe["p_valor"].iloc[0]),
        "media_tau_pre": f(g[g["janela"] == "pre"]["tau"].mean()),
        "s5_pre_menos_pre_extra": est_basica(linha_e7(e7, "F3.P1", "U", "0.400", "S5_pre_menos_pre_extra")),
        "dird_principal": est_basica(linha_e7(e7, "F3.P1", "U", "0.400")),
    }
    # V1 em 0,300: pré-tendência.
    v = ev[(ev["outcome_id"] == "F3.1") & (ev["populacao"] == "V1") & (ev["corte"] == "0.300") & ev["tau"].notna()]
    vv = v[v["janela"].isin(("pre_extra", "entre_pre_extra_e_pre"))]
    out["v1_0300"] = {
        "meses_pre_extra_e_entre": int(len(vv)), "meses_pre_extra_e_entre_p_menor_005": int((vv["p_valor"] < ALFA).sum()),
        "meses_pre_extra_e_entre_tau_positivo": int((vv["tau"] > 0).sum()),
        "placebo_pre": est_basica(linha_e7(e7, "F3.1", "V1", "0.300", "placebo_pre")),
        "s5_pre_menos_pre_extra": est_basica(linha_e7(e7, "F3.1", "V1", "0.300", "S5_pre_menos_pre_extra")),
        "dird_principal": est_basica(linha_e7(e7, "F3.1", "V1", "0.300")),
    }
    # Magnitude: limite superior de P2 contra a média bruta do pré abaixo do corte, na janela.
    p2 = linha_e7(e7, "F3.1", "U")
    rel = {}
    for c in CORTES:
        base = f(linha_e7(e7, "F3.1", "U", c, "nivel_pre")["media_bruta_abaixo"])
        rel[c] = {"media_bruta_pre_abaixo": base, "razao_sup_p2": f(p2["ic95_sup"]) / base}
    out["p2_sup_relativo_media_pre"] = rel
    hon = linha_e7(e7, "F3.1", "U", EMPILHADO, "ic_honesto", fator_M=1.0)
    out["p2_ic_honesto_M1"] = [f(hon["ic_honesto_inf"]), f(hon["ic_honesto_sup"])]
    return out


# ---------------------------------------------------------------------------
# Seleção em V1 0,400
# ---------------------------------------------------------------------------

def selecao_v1(e6: pd.DataFrame, diag: pd.DataFrame) -> dict:
    vag = linha_e6(e6, "f0_2_vagas_imediatas_por_10k_c1", "U", "1", "0.400")
    vag_emp = linha_e6(e6, "f0_2_vagas_imediatas_por_10k_c1", "U", "1", EMPILHADO)
    d = diag[(diag["populacao"] == "V1") & (diag["corte"] == "0.400") & (diag["especificacao"] == "principal")]
    dens = uma(d[d["diagnostico"] == "densidade_poisson_mass_points"], "densidade V1 0,400")
    bal = d[(d["diagnostico"] == "balanco_covariavel_pre") & d["p_valor"].notna()]
    p1 = linha_e6(e6, "P1", "V1+V2+V3", "1+2+3")
    pesos = json.loads(p1["pesos_grupos"])
    return {
        "vagas_imediatas_c1_0400": {**est_basica(vag), "q_bky": f(vag["q_bky"])},
        "vagas_imediatas_c1_empilhado": {**est_basica(vag_emp), "q_bky": f(vag_emp["q_bky"])},
        "densidade_V1_0400": {"razao": f(dens["rho"]), "ic95": [f(dens["rho_ic95_inf"]), f(dens["rho_ic95_sup"])],
                              "p_valor": f(dens["p_valor"])},
        "balanco_V1_0400": {"covariaveis_testadas": int(len(bal)), "p_menor_005": int((bal["p_valor"] < ALFA).sum()),
                            "quais": sorted(bal.loc[bal["p_valor"] < ALFA, "variavel"].tolist())},
        "peso_c1_400_no_P1": float(pesos["c1_400"]),
    }


# ---------------------------------------------------------------------------
# Literatura (texto, não resultado)
# ---------------------------------------------------------------------------

def literatura() -> dict:
    texto = LITERATURA.read_text(encoding="utf-8")
    linhas = []
    for i in LIT_IDS:
        # Só a tabela-resumo (6 colunas: id, estudo, país, método, conclusão, classificação).
        cand = [ln for ln in texto.splitlines()
                if ln.startswith(f"| {i} |") and len(ln.strip().strip("|").split("|")) == 6]
        exigir(len(cand) == 1, f"literatura: linha {i} da tabela-resumo nao encontrada uma vez no doc 20")
        cel = [c.strip() for c in cand[0].strip().strip("|").split("|")]
        linhas.append({"id": cel[0], "estudo": cel[1], "pais": cel[2], "metodo": cel[3], "conclusao": cel[4],
                       "classificacao_doc20": cel[5], "linha_fonte": cand[0], "fonte": rotulo(LITERATURA)})
    trechos = []
    for path, trecho, papel in LIT_TRECHOS:
        exigir(trecho in path.read_text(encoding="utf-8"), f"literatura: trecho ausente em {rotulo(path)}: {trecho!r}")
        trechos.append({"fonte": rotulo(path), "trecho": trecho, "papel": papel})
    return {"estudos": linhas, "trechos": trechos,
            "regra": "so o que esta no doc 20 da secao 03 ou no protocolo; nenhum numero novo"}


def degrau_relativo(r9: dict) -> dict:
    m = r9["mapa_faixa_bolsa"]["mapa_faixa_para_bolsa_mil"]
    b3, b2, b1 = (float(m[k]) for k in ("FAIXA 3", "FAIXA 2", "FAIXA 1"))
    return {"0.300": {"de_mil": b3, "para_mil": b2, "relativo": (b2 - b3) / b3},
            "0.400": {"de_mil": b2, "para_mil": b1, "relativo": (b1 - b2) / b2},
            "fonte": f"{rotulo(E9_RESUMO)}: mapa_faixa_bolsa.mapa_faixa_para_bolsa_mil (grades dos editais)"}


# ---------------------------------------------------------------------------
# Tabela-síntese por elo da cadeia
# ---------------------------------------------------------------------------

ELOS = {"F0": "implementação e seleção", "F1": "atração", "E9": "escolha", "F2": "presença",
        "F3": "oferta no CNES", "F4": "seleção de quem chega"}
CONTR_NIVEL = "pacote no corte (RDD em nível)"
CONTR_DIRD = "DiRD: bolsa + variação das co-políticas"
CONTR_E9 = "degrau da bolsa na escolha entre células"


def _leitura(est, inf, sup, p, q, holm=None) -> str:
    if holm is not None:
        return ("primária; Holm rejeita" if holm < ALFA else "primária; Holm não rejeita") + \
               ("; IC contém zero" if inf <= 0 <= sup else "")
    if inf <= 0 <= sup:
        return "IC contém zero"
    if q is None or not math.isfinite(q):
        return "IC exclui zero; fora do BKY"
    return "IC exclui zero; q BKY ≥ 0,05" if q >= ALFA else "IC exclui zero; q BKY < 0,05"


def tabela_sintese(e6: pd.DataFrame, e7: pd.DataFrame, holm: dict, e9: dict) -> pd.DataFrame:
    linhas = []

    def add_e6(fam, outcome, pop, cic, rotulo_outcome, holm_p=None):
        r = linha_e6(e6, outcome, pop, cic)
        q = f(r.get("q_bky"))
        linhas.append({"elo": ELOS[fam], "familia": fam, "outcome_id": r["outcome_id"], "outcome": rotulo_outcome,
                       "populacao": pop, "ciclo": cic, "corte": EMPILHADO, "contraste": CONTR_NIVEL,
                       "estimativa": f(r["tau"]), "ic95_inf": f(r["ic95_inf"]), "ic95_sup": f(r["ic95_sup"]),
                       "p_valor": f(r["p_valor"]), "q_bky": q, "p_holm": holm_p if holm_p is not None else np.nan,
                       "unidade": r["unidade"],
                       "leitura": _leitura(r["tau"], f(r["ic95_inf"]), f(r["ic95_sup"]), f(r["p_valor"]), q, holm_p),
                       "fonte": f"{rotulo(E6_EST)}: outcome == {r['outcome']}, populacao == {pop}, ciclo == {cic}, "
                                "corte == empilhado, especificacao == principal"})

    def add_e7(outcome_id, pop, rotulo_outcome, holm_p=None):
        r = linha_e7(e7, outcome_id, pop)
        q = f(r.get("q_bky"))
        linhas.append({"elo": ELOS["F3"], "familia": "F3", "outcome_id": outcome_id, "outcome": rotulo_outcome,
                       "populacao": pop, "ciclo": "pós 2025-10..2026-08", "corte": EMPILHADO, "contraste": CONTR_DIRD,
                       "estimativa": f(r["tau"]), "ic95_inf": f(r["ic95_inf"]), "ic95_sup": f(r["ic95_sup"]),
                       "p_valor": f(r["p_valor"]), "q_bky": q, "p_holm": holm_p if holm_p is not None else np.nan,
                       "unidade": r["unidade"],
                       "leitura": _leitura(r["tau"], f(r["ic95_inf"]), f(r["ic95_sup"]), f(r["p_valor"]), q, holm_p),
                       "fonte": f"{rotulo(E7_EST)}: outcome_id == {outcome_id}, populacao == {pop}, corte == empilhado, "
                                "especificacao == principal"})

    for cic in ("1", "2", "3"):
        add_e6("F0", f"f0_1_tem_celula_c{cic}", "U", cic, f"F0.1 município tem célula no quadro (ciclo {cic})")
    add_e6("F0", "f0_2_vagas_imediatas_por_10k_c1", "U", "1", "F0.2 vagas imediatas por 10 mil hab. (ciclo 1)")
    add_e6("F1", "P1", "V1+V2+V3", "1+2+3", "P1 índice de atração-presença", holm["P1"]["p_holm"])
    add_e6("F1", "F1.1", "V1+V2+V3", "1+2+3", "F1.1 candidatos de 1ª opção por célula")
    add_e6("F1", "F1.2", "V1+V2+V3", "1+2+3", "F1.2 fração de células com candidato")
    add_e6("F1", "F1.3", "V1+V2+V3", "1+2+3", "F1.3 fração de células preenchidas na 1ª chamada")
    add_e6("F1", "F1.4", "V1+V2", "1+2", "F1.4 fração de células preenchidas até a 2ª chamada")
    for cic, nome in (("empilhado", "1+2+3"), ("2", "2")):
        p = e9["principal"][cic]
        if cic == "empilhado":
            leit = "IC exclui zero; frágil (placebos, spline cúbico, sem o ciclo 2)" if e9["empilhado"]["fragil"] \
                else "IC exclui zero"
        else:
            partes = ["IC exclui zero" if p["ic_exclui_zero"] else "IC contém zero"]
            if e9["ciclo2"]["robusto_inferencia_poucos_clusters"] and e9["ciclo2"]["nenhum_placebo_supera"]:
                partes.append("robusto a poucos clusters e a placebos")
            if e9["ciclo2"]["ic_cubico_contem_zero"]:
                partes.append("IC contém zero com spline cúbico")
            leit = "; ".join(partes)
        linhas.append({"elo": ELOS["E9"], "familia": "E9", "outcome_id": "E9", "outcome":
                       "E9 escolha da 1ª opção (razão de chances por +R$ 5 mil)", "populacao": "candidatos de 1ª opção",
                       "ciclo": nome, "corte": "0,300 e 0,400 (degrau linear)", "contraste": CONTR_E9,
                       "estimativa": p["rc_5mil"], "ic95_inf": p["rc_5mil_ic95"][0], "ic95_sup": p["rc_5mil_ic95"][1],
                       "p_valor": p["p"], "q_bky": np.nan, "p_holm": np.nan, "unidade": "razão de chances",
                       "leitura": leit,
                       "fonte": f"{rotulo(E9_EFM)} e {rotulo(E9_EST)}: modelo condicional, conjunto principal, "
                                f"{PRINCIPAL_E9}, ciclo == {cic}"})
    add_e6("F2", "F2.1", "V1+V2", "1+2", "F2.1 especialistas ativos por célula")
    add_e6("F2", "f2_2_ativos_pmme_por_10k_c1", "U", "1", "F2.2 especialistas ativos por 10 mil hab. (ciclo 1)")
    add_e6("F2", "f2_2_ativos_pmme_por_10k_c2", "U", "2", "F2.2 especialistas ativos por 10 mil hab. (ciclo 2)")
    add_e6("F2", "F2.3", "V1+V2", "1+2", "F2.3 algum especialista ativo do ciclo")
    add_e7("F3.1", "U", "P2 F3.1 vínculos nas CBO-alvo por 10 mil hab.", holm["P2"]["p_holm"])
    add_e7("F3.1", "V1", "F3.1 vínculos nas CBO-alvo por 10 mil hab.")
    add_e7("F3.2", "U", "F3.2 município com especialista nas CBO-alvo")
    add_e7("F3.3", "U", "F3.3 horas SUS nas CBO-alvo por 10 mil hab.")
    add_e7("F3.P1", "U", "F3.P1 placebo: generalistas por 10 mil hab.")
    add_e7("F3.P2", "U", "F3.P2 placebo: especialistas fora das CBO-alvo")
    add_e6("F4", "F4.1", "V1+V2+V3", "1+2+3", "F4.1 nota média dos alocados")
    add_e6("F4", "F4.2", "V1+V2+V3", "1+2+3", "F4.2 nota média dos candidatos de 1ª opção")
    t = pd.DataFrame(linhas)
    t.insert(0, "ordem", range(1, len(t) + 1))
    t.insert(0, "natureza_dos_dados", "EMPIRICO")
    return t


# ---------------------------------------------------------------------------
# Afirmações da síntese (falha fechada se deixarem de valer)
# ---------------------------------------------------------------------------

def conferir_afirmacoes(r: dict) -> dict:
    h, d, e9, e7, sel = r["holm"], r["descarte"], r["e9"], r["e7"], r["selecao_v1_0400"]
    pre = {x["outcome_id"] + "|" + x["populacao"]: x for x in d["preenchimento"]}
    af = {
        "holm_nao_rejeita_nenhuma_primaria": not h["alguma_rejeitada"],
        "p1_ic_contem_zero": h["P1"]["ic95_inf"] <= 0 <= h["P1"]["ic95_sup"],
        "p2_ic_contem_zero": h["P2"]["ic95_inf"] <= 0 <= h["P2"]["ic95_sup"],
        "f13_empilhado_exclui_10pp_convencional": pre["F1.3|V1+V2+V3"]["exclui_referencia"],
        "f13_empilhado_exclui_10pp_em_todas_convencionais": pre["F1.3|V1+V2+V3"]["todas_convencionais_excluem_referencia"],
        "f13_empilhado_honesto_nao_exclui": not pre["F1.3|V1+V2+V3"]["ic_honesto_exclui_referencia"],
        "f13_empilhado_convencionais_todas_negativas": pre["F1.3|V1+V2+V3"]["convencionais_todas_com_salto_negativo"],
        "f13_por_ciclo_1_e_2_nao_exclui_10pp": not pre["F1.3|V1"]["exclui_referencia"]
                                                and not pre["F1.3|V2"]["exclui_referencia"],
        "p2_honesto_nao_informa": r["e7"]["p2_ic_honesto_M1"][0] < 0 < r["e7"]["p2_ic_honesto_M1"][1],
        "f31_0400_sem_mes_pos_significativo": r["e7"]["f31_U_0400_pos_p_menor_005"] == 0,
        "f14_empilhado_exclui_10pp_convencional": pre["F1.4|V1+V2"]["exclui_referencia"],
        "f14_nao_robusto_a_todas_convencionais": not pre["F1.4|V1+V2"]["todas_convencionais_excluem_referencia"],
        "ancora_e3_nao_exclui_10pp": not any(x["exclui_referencia"] for x in d["ancora_E3_ciclo1"]),
        "f1_nenhum_q_menor_005": r["familias"]["F1"]["resumo_testes"]["q_menor_005"] == 0,
        "f2_nenhum_q_menor_005": r["familias"]["F2"]["resumo_testes"]["q_menor_005"] == 0,
        "f3_nenhum_q_menor_005": r["familias"]["F3"]["resumo_testes"]["q_menor_005"] == 0,
        "f4_nenhum_q_menor_005": r["familias"]["F4"]["resumo_testes"]["q_menor_005"] == 0,
        "f0_nenhum_q_menor_005": r["familias"]["F0"]["resumo_testes"]["q_menor_005"] == 0,
        "e9_ciclo2_ic_exclui_zero_e_positivo": e9["principal"]["2"]["ic95_inf"] > 0,
        "e9_ciclo2_robusto_inferencia": e9["ciclo2"]["robusto_inferencia_poucos_clusters"],
        "e9_ciclo2_nenhum_placebo_supera": e9["ciclo2"]["nenhum_placebo_supera"],
        "e9_ciclo2_ic_cubico_contem_zero": e9["ciclo2"]["ic_cubico_contem_zero"],
        "e9_ciclos_1_e_3_ic_contem_zero": e9["ciclos_1_e_3_principal_ic_contem_zero"],
        "e9_empilhado_ic_exclui_zero": e9["principal"]["empilhado"]["ic95_inf"] > 0,
        "e9_empilhado_fragil": e9["empilhado"]["fragil"],
        "e9_heterogeneidade_rejeitada": e9["empilhado"]["heterogeneidade_rejeitada"],
        "e7_sequencia_pos_significativa": "pos" in e7["f31_U_0300"]["maior_sequencia_p_menor_005"]["janela"]
                                          and e7["f31_U_0300"]["maior_sequencia_p_menor_005"]["janela"] == ["pos"],
        "e7_nenhum_mes_antes_da_referencia_significativo": e7["f31_U_0300"]["meses_antes_da_referencia_p_menor_005"] == 0,
        "e7_descontinuidade_preexistente_0300": e7["f31_U_0300"]["descontinuidade_preexistente"],
        "e7_dird_0300_ic_contem_zero": e7["f31_U_0300"]["dird_principal"]["ic95_inf"] <= 0
                                       <= e7["f31_U_0300"]["dird_principal"]["ic95_sup"],
        "e7_generalistas_0400_deriva_pre_extra": e7["generalistas_U_0400"]["pre_extra_p_menor_005"] > 0,
        "e7_v1_0300_pretendencia": e7["v1_0300"]["meses_pre_extra_e_entre_p_menor_005"]
                                   == e7["v1_0300"]["meses_pre_extra_e_entre"]
                                   and e7["v1_0300"]["placebo_pre"]["p_valor"] < ALFA,
        "selecao_v1_0400_vagas_imediatas_negativas": sel["vagas_imediatas_c1_0400"]["ic95_sup"] < 0,
        "selecao_v1_0400_densidade_abaixo_de_um_e_desequilibrios": sel["densidade_V1_0400"]["razao"] < 1
                                                                  and sel["balanco_V1_0400"]["p_menor_005"] > 0,
        # §5.1 do doc 44
        "f13_empilhado_p_menor_005_so_ponderado_e_celula": sorted(
            x["especificacao"] for x in pre["F1.3|V1+V2+V3"]["convencionais_com_p_menor_005"])
                                                           == ["nivel_celula", "ponderado_celulas"],
        "f14_maior_sup_vem_da_janela": pre["F1.4|V1+V2"]["especificacao_do_maior_sup"].startswith("sensibilidade_h"),
        "candidaturas_so_algumas_excluem": 0 < d["candidaturas_poisson_n_excluem"] < d["candidaturas_poisson_n"],
        # §5.2
        "e9_ciclo2_sobrevive_spline_linear_flexivel_e_janelas": e9["ciclo2"]["sobrevive_spline_linear_flexivel_e_janelas"],
        "e9_empilhado_placebo_bem_acima_do_nominal": e9["empilhado"]["placebo"]["fracao_abs_t_maior_1_96"] > 2 * ALFA,
        "e9_empilhado_p_posto_acima_005": e9["empilhado"]["p_posto_acima_005"],
        "e9_empilhado_cubico_contem_zero": e9["empilhado"]["ic_cubico_contem_zero"],
        "e9_ciclos_1_e_3_juntos_contem_zero": e9["empilhado"]["ciclos_1_e_3_ic_contem_zero"],
        "e9_cluster_curso_p_pouco_abaixo_de_005": all(
            0.01 < e9["empilhado"]["cluster_curso"][k] < ALFA for k in ("p_score_rademacher", "p_score_webb")),
        # §5.3
        "e7_sequencia_comeca_no_primeiro_mes_do_pos": e7["f31_U_0300"]["maior_sequencia_p_menor_005"]["inicio"]
                                                      == e7["f31_U_0300"]["primeiro_mes_pos"],
        "e7_sequencia_se_desfaz": e7["f31_U_0300"]["meses_pos_depois_da_sequencia"] > 0
                                  and e7["f31_U_0300"]["meses_pos_depois_da_sequencia_p_menor_005"] == 0,
        "e7_referencia_num_vale": e7["f31_U_0300"]["media_tau_pre"] < min(e7["f31_U_0300"]["media_tau_pre_extra"],
                                                                         e7["f31_U_0300"]["media_tau_pos"]),
        "e7_pos_parecido_com_pre_extra": 0.5 < e7["f31_U_0300"]["media_tau_pos"]
                                         / e7["f31_U_0300"]["media_tau_pre_extra"] < 2.0,
        # §5.5 e §7.2
        "p_menor_005_isolados_sao_vagas_presenca_c2_e_nota": sorted(
            o for fam in ("F0", "F1", "F2", "F3", "F4") for o in r["familias"][fam]["resumo_testes"]["outcomes_com_p_menor_005"])
            == ["f0_2_vagas_imediatas_por_10k_c1", "f2_2_ativos_pmme_por_10k_c2", "f4_2_pontuacao_media_cand_1a_opcao"],
        "f1_f2_maioria_dos_saltos_negativos": sum(r["familias"][k]["resumo_testes"]["salto_negativo"] for k in ("F1", "F2"))
            > 0.5 * sum(r["familias"][k]["resumo_testes"]["linhas_principais_no_bky"] for k in ("F1", "F2")),
        # §6
        # O "+N%" do sorteio de Dal Bó et al. é lido da linha A2 do doc 20, não digitado.
        "degrau_0400_igual_ao_de_dal_bo": [round(100 * r["degrau_relativo_bolsa"]["0.400"]["relativo"])]
            == [int(m) for x in r["literatura"]["estudos"] if x["id"] == "A2"
                for m in re.findall(r"\+(\d+)%", x["metodo"])],
        "degrau_0300_maior": r["degrau_relativo_bolsa"]["0.300"]["relativo"] > r["degrau_relativo_bolsa"]["0.400"]["relativo"],
        "f4_sem_selecao_positiva": all(x["ic95_inf"] <= 0 for x in r["familias"]["F4"]["linhas_empilhadas"]),
    }
    af = {k: bool(v) for k, v in af.items()}
    falsas = [k for k, v in af.items() if not v]
    exigir(not falsas, f"afirmacoes da sintese que nao valem mais nos dados (rever o doc 44): {falsas}")
    return af


# ---------------------------------------------------------------------------
# Montagem
# ---------------------------------------------------------------------------

def construir() -> tuple[dict, pd.DataFrame]:
    e3 = ler_csv(E3_EST)
    st3 = ler_json(E3_STATUS)
    r5 = ler_json(E5_RESUMO)
    e6 = ler_csv(E6_EST)
    diag = ler_csv(E6_DIAG)
    r6 = ler_json(E6_RESUMO)
    e7 = ler_csv(E7_EST)
    ev = ler_csv(E7_EVENTO)
    r7 = ler_json(E7_RESUMO)
    e9 = ler_csv(E9_EST)
    efm = ler_csv(E9_EFM)
    rob = ler_csv(E9_ROB)
    r9 = ler_json(E9_RESUMO)
    exigir(st3.get("status") == "CONCLUIDO", "E3 nao concluido")
    # Protocolo: o texto e a máquina são os que o E6, o E7 e o E9 declararam.
    sha_md, sha_js = sha256(PROTOCOLO_MD), sha256(PROTOCOLO_JSON)
    exigir(r6["protocolo"]["sha256_texto_canonico"] == sha_md and r6["protocolo"]["sha256"] == sha_js,
           "protocolo difere do declarado no E6")
    exigir(r7["protocolo"]["sha256_texto"] == sha_md and r7["protocolo"]["sha256_maquina"] == sha_js,
           "protocolo difere do declarado no E7")
    exigir(r9["protocolo"]["sha256_texto_canonico"] == sha_md, "protocolo difere do declarado no E9")

    holm = holm_primarias(e6, r6, e7, r7)
    resumo = {
        "etapa": "E8_sintese",
        "natureza_dos_dados": "EMPIRICO",
        "data_execucao": dt.date.today().isoformat(),
        "script": "scripts/rdd_bolsa/15_sintese_E8.py",
        "protocolo": {"texto": rotulo(PROTOCOLO_MD), "sha256_texto": sha_md, "maquina": rotulo(PROTOCOLO_JSON),
                      "sha256_maquina": sha_js, "secoes": "§7 (Holm, BKY, referencias de magnitude), §11 (E8)"},
        "regra": "nenhuma estimacao nova; a unica conta inferencial e o Holm sobre os p de P1 e P2. Todo o resto e "
                 "copiado das saidas do E3, E5, E6, E7 e E9 ou contado nelas.",
        "contraste": {"nivel": r6["contraste"], "dird": r7["contraste"]["dird"],
                      "escolha": "E9: degrau da bolsa anunciada na escolha da 1a opcao entre celulas (realocacao); "
                                 "nao e efeito sobre o total de candidatos",
                      "nao_e": "participacao no PMM-E; Agora Tem Especialistas; bolsa pura (salvo no E9, sob a "
                               "hipotese de que nenhum outro atributo da celula salta no corte)"},
        "entradas": bloco_entradas(),
        "holm": holm,
        "familias": familias(e6, e7),
        "descarte": descarte(e6, e3, r5),
        "e9": e9_sintese(e9, efm, rob),
        "e7": e7_sintese(e7, ev),
        "selecao_v1_0400": selecao_v1(e6, diag),
        "degrau_relativo_bolsa": degrau_relativo(r9),
        "literatura": literatura(),
    }
    resumo["afirmacoes_conferidas"] = conferir_afirmacoes(resumo)
    tabela = tabela_sintese(e6, e7, holm, resumo["e9"])
    exigir(set(tabela["natureza_dos_dados"]) == {"EMPIRICO"}, "tabela com natureza nao EMPIRICO")
    return resumo, tabela


def _sem_nan(x):
    """NaN e infinito viram null no JSON (ausente, nunca zero)."""
    if isinstance(x, dict):
        return {k: _sem_nan(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_sem_nan(v) for v in x]
    if isinstance(x, float) and not math.isfinite(x):
        return None
    return x


def gravar(resumo: dict, tabela: pd.DataFrame) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    tabela.to_csv(OUT / NOME_TABELA, index=False, lineterminator="\n")
    resumo["saidas"] = {NOME_TABELA: {"caminho": rotulo(OUT / NOME_TABELA), "sha256": sha256(OUT / NOME_TABELA),
                                      "linhas": int(len(tabela))}}
    (OUT / NOME_RESUMO).write_text(json.dumps(_sem_nan(resumo), ensure_ascii=False, indent=2, allow_nan=False) + "\n",
                                   encoding="utf-8")


def ler_saidas() -> tuple[dict, pd.DataFrame]:
    resumo = json.loads((OUT / NOME_RESUMO).read_text(encoding="utf-8"))
    tabela = pd.read_csv(OUT / NOME_TABELA, dtype={"ciclo": str, "corte": str})
    return resumo, tabela


# ---------------------------------------------------------------------------
# Blocos do doc 44 (gerados só a partir de E8_resumo.json e E8_tabela_sintese.csv)
# ---------------------------------------------------------------------------

def _num(v, casas=3, sinal=True) -> str:
    if v is None or (isinstance(v, float) and not math.isfinite(v)):
        return "—"
    txt = f"{float(v):+.{casas}f}" if sinal else f"{float(v):.{casas}f}"
    return txt.replace("-", "−").replace(".", ",")


def _pp(v, casas=1, sinal=True) -> str:
    return "—" if v is None or not math.isfinite(float(v)) else _num(100 * float(v), casas, sinal) + " p.p."


def _pct(v, casas=1, sinal=True) -> str:
    return "—" if v is None or not math.isfinite(float(v)) else _num(100 * float(v), casas, sinal) + " %"


def _p(v) -> str:
    if v is None or not math.isfinite(float(v)):
        return "—"
    return "< 0,001" if float(v) < 0.001 else f"{float(v):.3f}".replace(".", ",")


def _peq(v) -> str:
    """'p = x' ou 'p < 0,001'."""
    t = _p(v)
    return f"p {t}" if t.startswith("<") else f"p = {t}"


def _ic(a, b, fmt) -> str:
    return f"[{fmt(a)}; {fmt(b)}]"


def _fmt_unidade(unidade: str):
    if unidade.startswith("fracao"):
        return lambda v: _pp(v)
    if unidade.startswith("razão de chances"):
        return lambda v: _num(v, 2, sinal=False)
    if unidade.startswith("desvios"):
        return lambda v: _num(v, 2) + " DP"
    if unidade.startswith("horas"):
        return lambda v: _num(v, 1)
    return lambda v: _num(v, 3)


def _corte_txt(c: str) -> str:
    return {"0.300": "0,300", "0.400": "0,400", "empilhado": "empilhado"}.get(c, c)


def blocos_doc(resumo: dict, tabela: pd.DataFrame) -> dict[str, str]:
    h, d, e9, e7, sel = resumo["holm"], resumo["descarte"], resumo["e9"], resumo["e7"], resumo["selecao_v1_0400"]
    pre = {x["outcome_id"] + "|" + x["populacao"]: x for x in d["preenchimento"]}
    f13, f14 = pre["F1.3|V1+V2+V3"], pre["F1.4|V1+V2"]
    c2, emp = e9["principal"]["2"], e9["principal"]["empilhado"]
    b = {}

    b["resposta_curta"] = (
        f"Sob o protocolo congelado, nenhum dos dois testes primários rejeita zero depois do Holm: o índice de "
        f"atração-presença (P1) tem p ajustado {_p(h['P1']['p_holm'])}, e a oferta de especialistas nas CBO-alvo no "
        f"CNES por DiRD (P2) tem p ajustado {_p(h['P2']['p_holm'])}. Com ciclos e cortes empilhados, o IC 95% "
        f"convencional do preenchimento na 1ª chamada vai até {_pp(f13['ic95_sup'])}, abaixo da referência de "
        f"{_pp(d['referencias']['preenchimento_pp'], 0)} do protocolo; esse descarte vale só sob a aproximação local "
        f"linear, porque o IC honesto não descarta nada. O único sinal que resiste a vários testes está na escolha: no "
        f"ciclo 2, a bolsa "
        f"anunciada desloca a 1ª opção dos candidatos para células de bolsa maior (razão de chances "
        f"{_num(c2['rc_5mil'], 2, False)} por +R$ 5 mil), mas o efeito não aparece nos ciclos 1 e 3 e o empilhado "
        f"(razão {_num(emp['rc_5mil'], 2, False)}) não resiste a placebos nem a um spline mais flexível. Os contrastes "
        f"são o pacote do corte (RDD em nível), a bolsa mais a variação das co-políticas (DiRD) e o degrau da bolsa "
        f"na escolha entre células (E9); nenhum é efeito da participação no PMM-E nem do Agora Tem Especialistas. Leitura: no corte, o degrau de R$ 5 mil não tem efeito detectável sobre "
        f"preenchimento, presença ou oferta local, e o que se detecta é compatível com realocação de candidatos "
        f"entre vagas, não com expansão líquida.")

    # Tabela-síntese.
    cab = ("| Elo | Outcome | População | Ciclo | Contraste | Estimativa | IC 95% | p | q BKY | p Holm | Leitura |\n"
           "|---|---|---|---|---|---|---|---|---|---|---|")
    linhas = [cab]
    for _, r in tabela.sort_values("ordem").iterrows():
        fm = _fmt_unidade(str(r["unidade"]))
        linhas.append(f"| {r['elo']} | {r['outcome']} | {r['populacao']} | {r['ciclo']} | {r['contraste']} | "
                      f"{fm(f(r['estimativa']))} | {_ic(f(r['ic95_inf']), f(r['ic95_sup']), fm)} | "
                      f"{_p(f(r['p_valor']))} | {_p(f(r['q_bky']))} | {_p(f(r['p_holm']))} | {r['leitura']} |")
    b["tabela_sintese"] = "\n".join(linhas)

    # Famílias: contagem de testes.
    linhas = ["| Família | Linhas principais no BKY | p < 0,05 | q BKY < 0,05 | menor p | menor q |",
              "|---|---|---|---|---|---|"]
    for fam in ("F0", "F1", "F2", "F3", "F4"):
        t = resumo["familias"][fam]["resumo_testes"]
        linhas.append(f"| {fam} | {t['linhas_principais_no_bky']} | {t['p_menor_005']} | {t['q_menor_005']} | "
                      f"{_p(t['menor_p'])} | {_p(t['menor_q'])} |")
    b["familias_testes"] = "\n".join(linhas)

    # Holm.
    linhas = ["| Primária | Contraste | Salto | IC 95% | p | p Holm | Rejeita a 5%? |", "|---|---|---|---|---|---|---|"]
    for k in ("P1", "P2"):
        x = h[k]
        fm = _fmt_unidade(x["unidade"])
        linhas.append(f"| {k}: {x['hipotese']} | {x['contraste']} | {fm(x['tau'])} | "
                      f"{_ic(x['ic95_inf'], x['ic95_sup'], fm)} | {_p(x['p_valor'])} | {_p(x['p_holm'])} | "
                      f"{'sim' if x['rejeita_holm_5pct'] else 'não'} |")
    b["holm"] = "\n".join(linhas)

    # Descarte.
    linhas = ["| Outcome | População | Ciclo | Salto | IC 95% | Exclui +10 p.p.? | Maior limite superior entre as "
              "especificações convencionais | Todas excluem? | IC honesto (M do protocolo) exclui? |",
              "|---|---|---|---|---|---|---|---|---|"]
    for x in d["preenchimento"]:
        linhas.append(f"| {x['outcome_id']} | {x['populacao']} | {x['ciclo']} | {_pp(x['tau'])} | "
                      f"{_ic(x['ic95_inf'], x['ic95_sup'], _pp)} | {'sim' if x['exclui_referencia'] else 'não'} | "
                      f"{_pp(x['maior_ic95_sup_convencional'])} ({x['especificacao_do_maior_sup'].replace('.', ',')}) | "
                      f"{'sim' if x['todas_convencionais_excluem_referencia'] else 'não'} | "
                      f"{'sim' if x['ic_honesto_exclui_referencia'] else 'não'} |")
    for x in (f13, f14):
        neg = x["convencionais_com_p_menor_005"]
        linhas.append("")
        linhas.append(f"{x['outcome_id']} ({x['populacao']}): {x['n_especificacoes_convencionais']} especificações "
                      f"convencionais do protocolo ({', '.join(x['especificacoes_convencionais'])}); todas com salto "
                      f"{'negativo' if x['convencionais_todas_com_salto_negativo'] else 'de sinal variado'}; com "
                      f"p < 0,05: " + ("; ".join(
                          f"{y['especificacao']}, h = {_num(y['h'], 3, False)}: {_pp(y['tau'])} "
                          f"{_ic(y['ic95_inf'], y['ic95_sup'], _pp)}" for y in neg) if neg else "nenhuma") + ".")
    linhas.append("")
    linhas.append("| Âncora (E3, ciclo 1, F1.3) | Salto | IC 95% | Exclui +10 p.p.? | MDE de 80% (E5) |")
    linhas.append("|---|---|---|---|---|")
    for x in d["ancora_E3_ciclo1"]:
        linhas.append(f"| corte {_corte_txt(x['corte'])} | {_pp(x['tau'])} | {_ic(x['ic95_inf'], x['ic95_sup'], _pp)} | "
                      f"{'sim' if x['exclui_referencia'] else 'não'} | {_pp(x['mde_80'], 1, False)} |")
    linhas.append("")
    linhas.append(f"Candidaturas (F1.1, Poisson local, referência de {_pct(d['referencias']['candidaturas_relativo'], 0)}): "
                  f"{d['candidaturas_poisson_n_excluem']} de {d['candidaturas_poisson_n']} linhas por ciclo e corte "
                  f"têm limite superior abaixo da referência ("
                  + "; ".join(f"ciclo {x['ciclo']}, {_corte_txt(x['corte'])}: até {_pct(x['ic95_sup'])}"
                              for x in d["candidaturas_poisson"]) + "). Não há linha empilhada em escala relativa.")
    rel = e7["p2_sup_relativo_media_pre"]
    linhas.append("")
    linhas.append(f"Oferta no CNES (P2): o limite superior do IC 95% é {_num(h['P2']['ic95_sup'], 3)} vínculo por 10 "
                  f"mil hab., ou " + "; ".join(
                      f"{_pct(rel[c]['razao_sup_p2'], 1, False)} da média bruta do pré abaixo do corte "
                      f"{_corte_txt(c)} ({_num(rel[c]['media_bruta_pre_abaixo'], 3, False)})" for c in sorted(rel))
                  + f". O IC honesto com o M do protocolo é {_ic(*e7['p2_ic_honesto_M1'], lambda v: _num(v, 3))}.")
    b["descarte"] = "\n".join(linhas)

    # E9.
    linhas = ["| Ciclo | Coef. por R$ mil | IC 95% | p | Razão de chances por +R$ 5 mil [IC 95%] | "
              "Δ prob. média, p.p. [IC 95%] | Prob. base, p.p. | Variação relativa média [IC 95%] |",
              "|---|---|---|---|---|---|---|---|"]
    for cic in ("1", "2", "3", "empilhado"):
        x = e9["principal"][cic]
        linhas.append(f"| {cic} | {_num(x['coef_por_mil'], 4)} | {_ic(x['ic95_inf'], x['ic95_sup'], lambda v: _num(v, 4))} | "
                      f"{_p(x['p'])} | {_num(x['rc_5mil'], 2, False)} "
                      f"{_ic(*x['rc_5mil_ic95'], lambda v: _num(v, 2, False))} | {_num(x['dprob_pp'], 3)} "
                      f"{_ic(*x['dprob_pp_ic95'], lambda v: _num(v, 3))} | {_num(x['prob_base_pp'], 3, False)} | "
                      f"{_pct(x['variacao_relativa'])} {_ic(*x['variacao_relativa_ic95'], _pct)} |")
    c2r, er = e9["ciclo2"], e9["empilhado"]
    linhas.append("")
    linhas.append("| Teste de robustez (pós-auditoria, fora do protocolo) | Ciclo 2 | Empilhado |")
    linhas.append("|---|---|---|")
    linhas.append(f"| p do score bootstrap (Rademacher / Webb), cluster por conjunto | {_p(c2r['p_score_rademacher'])} / "
                  f"{_p(c2r['p_score_webb'])} | — |")
    linhas.append(f"| p do CV3 | {_p(c2r['p_cv3'])} | — |")
    linhas.append(f"| IC por inversão do score | {_ic(*c2r['ic_inversao'], lambda v: _num(v, 4))} | — |")
    linhas.append(f"| cortes placebo: fração com abs(t) > 1,96 | {_num(c2r['placebo']['fracao_abs_t_maior_1_96'], 3, False)} | "
                  f"{_num(er['placebo']['fracao_abs_t_maior_1_96'], 3, False)} |")
    linhas.append(f"| cortes placebo: nº com abs(t) ≥ t real, de {int(er['placebo']['n_placebos'])} | "
                  f"{int(c2r['placebo']['n_abs_t_placebo_ge_real'])} | {int(er['placebo']['n_abs_t_placebo_ge_real'])} |")
    linhas.append(f"| p por posto contra os placebos | {_p(c2r['placebo']['p_posto'])} | {_p(er['placebo']['p_posto'])} |")
    linhas.append(f"| spline cúbico: coef. [IC 95%]; p | {_num(c2r['spline_cubico']['coef'], 4)} "
                  f"{_ic(c2r['spline_cubico']['ic95_inf'], c2r['spline_cubico']['ic95_sup'], lambda v: _num(v, 4))}; "
                  f"{_p(c2r['spline_cubico']['p'])} | {_num(er['spline_cubico']['coef'], 4)} "
                  f"{_ic(er['spline_cubico']['ic95_inf'], er['spline_cubico']['ic95_sup'], lambda v: _num(v, 4))}; "
                  f"{_p(er['spline_cubico']['p'])} |")
    linhas.append(f"| maior p entre spline linear com nós a cada 0,05 e janelas de ±0,10, ±0,05 e ±0,025 | "
                  f"{_p(max(c2r['spline_linear_janelas_p'].values()))} | — |")
    linhas.append(f"| ciclos 1 e 3 empilhados, sem o 2: coef. [IC 95%]; p | — | {_num(er['ciclos_1_e_3']['coef'], 4)} "
                  f"{_ic(er['ciclos_1_e_3']['ic95_inf'], er['ciclos_1_e_3']['ic95_sup'], lambda v: _num(v, 4))}; "
                  f"{_p(er['ciclos_1_e_3']['p'])} |")
    linhas.append(f"| Q de Cochran (ciclos 1, 2, 3); p | — | {_num(er['cochran_Q']['valor'], 2, False)}; "
                  f"{_p(er['cochran_Q']['p'])} |")
    linhas.append(f"| cluster por curso: p do score (Rademacher / Webb) | — | "
                  f"{_p(er['cluster_curso']['p_score_rademacher'])} / {_p(er['cluster_curso']['p_score_webb'])} |")
    b["e9"] = "\n".join(linhas)

    # E7.
    o, g, v = e7["f31_U_0300"], e7["generalistas_U_0400"], e7["v1_0300"]
    s = o["maior_sequencia_p_menor_005"]
    b["e7"] = "\n".join([
        f"- **F3.1 em U, corte 0,300:** {s['n_meses']} meses consecutivos com p < 0,05, de {s['inicio']} a {s['fim']} "
        f"(saltos de {_num(s['tau_min'], 3)} a {_num(s['tau_max'], 3)}, relativos a 2025-06; maior p {_p(s['p_max'])}). "
        f"Nos {o['meses_pos_depois_da_sequencia']} meses seguintes do pós, {o['meses_pos_depois_da_sequencia_p_menor_005']} "
        f"têm p < 0,05. Antes da referência, {o['meses_antes_da_referencia_p_menor_005']} de "
        f"{o['meses_antes_da_referencia']} meses têm p < 0,05. Salto médio no pré extra {_num(o['media_tau_pre_extra'], 3)}; "
        f"no pós {_num(o['media_tau_pos'], 3)}. DiRD principal {_num(o['dird_principal']['tau'], 3)} "
        f"{_ic(o['dird_principal']['ic95_inf'], o['dird_principal']['ic95_sup'], lambda x: _num(x, 3))}, "
        f"{_peq(o['dird_principal']['p_valor'])}.",
        f"- **Descontinuidade pré-existente (F3.1, U, 0,300, RDD em nível):** pré extra "
        f"{_num(o['nivel_pre_extra']['tau'], 3)} {_ic(o['nivel_pre_extra']['ic95_inf'], o['nivel_pre_extra']['ic95_sup'], lambda x: _num(x, 3))}; "
        f"pré principal {_num(o['nivel_pre']['tau'], 3)} {_ic(o['nivel_pre']['ic95_inf'], o['nivel_pre']['ic95_sup'], lambda x: _num(x, 3))}.",
        f"- **F3.1 em U, corte 0,400:** meses do pós com p < 0,05: {e7['f31_U_0400_pos_p_menor_005']}.",
        f"- **Generalistas (F3.P1), U, 0,400:** {g['pre_extra_p_menor_005']} de {g['pre_extra_meses']} meses do pré extra "
        f"com p < 0,05; em {g['primeiro_mes']} o salto relativo a 2025-06 é {_num(g['tau_primeiro_mes'], 3)} "
        f"({_peq(g['p_primeiro_mes'])}), e a média no pré principal é {_num(g['media_tau_pre'], 3)}. S5 (pré menos pré "
        f"extra) {_num(g['s5_pre_menos_pre_extra']['tau'], 3)} ({_peq(g['s5_pre_menos_pre_extra']['p_valor'])}). DiRD "
        f"principal {_num(g['dird_principal']['tau'], 3)} ({_peq(g['dird_principal']['p_valor'])}).",
        f"- **V1, corte 0,300:** {v['meses_pre_extra_e_entre_p_menor_005']} de {v['meses_pre_extra_e_entre']} meses do "
        f"pré extra e do trecho até o pré principal com p < 0,05 ({v['meses_pre_extra_e_entre_tau_positivo']} com salto "
        f"positivo). Placebo dentro do pré {_num(v['placebo_pre']['tau'], 3)} ({_peq(v['placebo_pre']['p_valor'])}); "
        f"S5 {_num(v['s5_pre_menos_pre_extra']['tau'], 3)} ({_peq(v['s5_pre_menos_pre_extra']['p_valor'])}).",
    ])

    # Seleção em V1 0,400.
    va, ve = sel["vagas_imediatas_c1_0400"], sel["vagas_imediatas_c1_empilhado"]
    ds, bl = sel["densidade_V1_0400"], sel["balanco_V1_0400"]
    b["selecao"] = "\n".join([
        f"- vagas imediatas do ciclo 1 por 10 mil hab., em U: 0,400 {_num(va['tau'], 3)} "
        f"{_ic(va['ic95_inf'], va['ic95_sup'], lambda x: _num(x, 3))} ({_peq(va['p_valor'])}; q BKY = {_p(va['q_bky'])}); "
        f"empilhado {_num(ve['tau'], 3)} {_ic(ve['ic95_inf'], ve['ic95_sup'], lambda x: _num(x, 3))} "
        f"({_peq(ve['p_valor'])}; q BKY = {_p(ve['q_bky'])});",
        f"- razão de densidades de V1 em 0,400: {_num(ds['razao'], 2, False)} "
        f"{_ic(*ds['ic95'], lambda x: _num(x, 2, False))} ({_peq(ds['p_valor'])});",
        f"- balanço de V1 em 0,400: {bl['p_menor_005']} de {bl['covariaveis_testadas']} covariáveis com p < 0,05 "
        f"({', '.join(bl['quais'])});",
        f"- peso do grupo ciclo 1 × 0,400 no P1 empilhado: {_pct(sel['peso_c1_400_no_P1'], 1, False)}.",
    ])

    # Literatura.
    dg = resumo["degrau_relativo_bolsa"]
    lit = resumo["literatura"]
    linhas = [f"Degrau relativo da bolsa neste desenho (grades dos editais): em 0,300, de R$ "
              f"{int(dg['0.300']['de_mil'])} mil para R$ {int(dg['0.300']['para_mil'])} mil "
              f"({_pct(dg['0.300']['relativo'], 0)}); em 0,400, de R$ {int(dg['0.400']['de_mil'])} mil para R$ "
              f"{int(dg['0.400']['para_mil'])} mil ({_pct(dg['0.400']['relativo'], 0)}).", "",
              "| Estudo (doc 20) | País | Desenho | Conclusão |", "|---|---|---|---|"]
    for x in lit["estudos"]:
        linhas.append(f"| {x['id']}. {x['estudo']} | {x['pais']} | {x['metodo']} | {x['conclusao']} |")
    linhas.append("")
    for t in lit["trechos"]:
        linhas.append(f"- {t['papel']} (`{t['fonte']}`): \"{' '.join(t['trecho'].replace('**', '').split())}\".")
    b["literatura"] = "\n".join(linhas)

    # Entradas.
    linhas = ["| Entrada | SHA-256 (início) | Papel |", "|---|---|---|"]
    for e in resumo["entradas"]:
        linhas.append(f"| `{e['caminho']}` | `{e['sha256'][:16]}…` | {e['papel']} |")
    b["entradas"] = "\n".join(linhas)
    return b


MARCA = re.compile(r"(<!-- E8:(?P<nome>[A-Za-z0-9_]+):inicio -->\n)(?P<corpo>.*?)(\n<!-- E8:(?P=nome):fim -->)", re.S)


def aplicar_blocos(texto: str, blocos: dict[str, str]) -> str:
    def sub(m):
        nome = m.group("nome")
        if nome not in blocos:
            raise KeyError(f"bloco {nome} nao gerado")
        return m.group(1) + blocos[nome] + m.group(4)
    return MARCA.sub(sub, texto)


def blocos_no_doc(texto: str) -> dict[str, str]:
    return {m.group("nome"): m.group("corpo") for m in MARCA.finditer(texto)}


def atualizar_doc() -> None:
    if not DOC44.exists():
        print(f"{rotulo(DOC44)} nao existe: blocos nao gravados")
        return
    resumo, tabela = ler_saidas()
    DOC44.write_text(aplicar_blocos(DOC44.read_text(encoding="utf-8"), blocos_doc(resumo, tabela)), encoding="utf-8")
    print(f"blocos do doc 44 regravados: {rotulo(DOC44)}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--atualizar-doc", action="store_true", help="so regrava os blocos do doc 44 a partir das saidas")
    args = ap.parse_args(argv)
    if args.atualizar_doc:
        atualizar_doc()
        return 0
    try:
        resumo, tabela = construir()
    except FalhaFechada as e:
        print(f"FALHA FECHADA: {e}", file=sys.stderr)
        return 1
    gravar(resumo, tabela)
    print(f"gravado: {rotulo(OUT / NOME_RESUMO)}; {rotulo(OUT / NOME_TABELA)} ({len(tabela)} linhas)")
    h = resumo["holm"]
    print(f"Holm: P1 p = {h['P1']['p_valor']:.4f} -> {h['P1']['p_holm']:.4f}; "
          f"P2 p = {h['P2']['p_valor']:.4f} -> {h['P2']['p_holm']:.4f}")
    atualizar_doc()
    return 0


if __name__ == "__main__":
    sys.exit(main())
