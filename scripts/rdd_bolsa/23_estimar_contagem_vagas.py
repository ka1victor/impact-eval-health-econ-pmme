"""Família N (protocolo 48): número de vagas preenchidas, com e sem controle pelas vagas oferecidas.

Protocolo congelado em 19/10/2026, antes de estimar:
`docs/06_execucao/48_protocolo_contagem_vagas_preenchidas.md`. Estatuto
pós-resultado (a fração F1.3 já tinha sido vista em todos os ciclos): toda linha
sai com `estatuto = PROTOCOLO_48_POS_RESULTADO` e `natureza_dos_dados =
EMPIRICO`. Nada aqui altera o protocolo 40, o Holm de P1 e P2 nem as saídas
E3–E9.

Outcomes (`output/rdd_bolsa/outcomes/outcomes_V_municipio.parquet`, tarefa B)
------------------------------------------------------------------------------
- N1 (principal): `n_alocados_ch1`, vagas preenchidas na 1a chamada do ciclo k
  (médicos alocados, por município); controle = vagas oferecidas no quadro da
  1a chamada;
- N2: `n_celulas_preenchidas_ch1`; controle `n_celulas`;
- N3: `n_celulas_preenchidas_ate_ch2` (ciclos 1 e 2); controle `n_celulas`;
- N4: `n_ativos_ciclo` (ciclos 1 e 2, retrato de 09/10/2026); controle =
  vagas oferecidas.

A forma do controle principal ("imediatas + cadastro reserva" ou "só
imediatas") é decidida ANTES de estimar, pela verificação registrada em
`N_resumo.json` (`verificacao_cadastro_reserva`): se um alocado da 1a chamada
pode ocupar vaga de cadastro reserva (quadros, resultados e editais), o
controle principal é imediatas + CR; senão, só imediatas. A outra forma é
sensibilidade.

Estimadores
-----------
Os de `scripts/rdd_bolsa/rdd_lib.py` (local linear triangular, h = 0,050, EP
HC1; empilhado com intercepto e inclinações por grupo × lado, tau comum, CR1
por município; IC honesto; Fisher). O controle entra como em Calonico,
Cattaneo, Farrell e Titiunik (2019): linear, com o MESMO coeficiente dos dois
lados do corte, dentro da mesma regressão local ponderada (argumento `Z` da
rdd_lib), centrado na média ponderada pelo kernel na janela (o centro não muda
o salto). No empilhado, o coeficiente do controle é próprio de cada grupo
(ciclo × corte) e comum aos dois lados. S-f deixa a inclinação do controle
diferente de cada lado; aí o salto é o do município com o número médio de
vagas da janela.

Por construção (Frisch–Waugh–Lovell), com a mesma amostra e os mesmos pesos,
salto sem controle (S-b) = salto com controle (S-a) + soma_g gamma_g x salto
do controle no grupo g. O script calcula essa decomposição (total = oferta +
preenchimento dado as vagas) e para se a identidade não fechar.

IC honesto com controle: o outcome é residualizado na janela,
y~ = y - gamma (v - v_barra), com gamma da regressão S-a (h = 0,050); o IC
honesto (Armstrong e Kolesár, regra do E6) é aplicado a y~, tratando gamma como
fixo. O salto local linear de y~ é idêntico ao de S-a (conferido).

Integridade
-----------
Nada simulado ou imputado. Município sem vagas oferecidas sai da linha e é
contado (`n_descartadas_controle_ausente`), nunca recebe zero. O zero de U fora
do quadro é o zero estrutural do protocolo (sem célula, sem alocado). A running
variable é o IVS 2010 oficial do Ipea (a08), conferido contra a coluna
`ivs_2010_oficial` das saídas da tarefa B como no E6; o arquivo local de IVS da
auditoria 16 não é lido.

Saídas: `output/rdd_bolsa/N_estimativas.csv`, `N_resumo.json`, `N_figuras/*.png`;
tabelas entre marcadores `<!-- N:... -->` de
`docs/06_execucao/49_resultados_contagem_vagas_preenchidas.md`.

Uso
---
    python3 scripts/rdd_bolsa/23_estimar_contagem_vagas.py
    python3 scripts/rdd_bolsa/23_estimar_contagem_vagas.py --atualizar-doc
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import re
import sys
import textwrap
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2

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
L = _importar(DIR_RDD / "rdd_lib.py", "rdd_lib_n")
E6 = _importar(DIR_RDD / "13_estimar_E6_funil.py", "e6_para_n")
sys.dont_write_bytecode = _bytecode

# ---------------------------------------------------------------------------
# Caminhos e parâmetros do protocolo (constantes permitidas: cortes, h, sementes)
# ---------------------------------------------------------------------------

OUT = ROOT / "output" / "rdd_bolsa"
OUTC = OUT / "outcomes"
ARQ_VM = OUTC / "outcomes_V_municipio.parquet"
ARQ_VC = OUTC / "outcomes_V_celula.parquet"
ARQ_U = OUTC / "outcomes_U_municipio.parquet"
DICIONARIO = OUTC / "dicionario_outcomes_funil.json"
A08 = ROOT / "output" / "aquisicao" / "a08_ivs_2010_oficial_municipio.csv"
E6_LR = OUT / "E6_lr_selecao_janela.csv"
E6_EST = OUT / "E6_estimativas.csv"
PROTOCOLO_MD = ROOT / "docs" / "06_execucao" / "48_protocolo_contagem_vagas_preenchidas.md"
DOC49 = ROOT / "docs" / "06_execucao" / "49_resultados_contagem_vagas_preenchidas.md"
EDITAIS = ROOT / "data" / "raw" / "aquisicao" / "ivs_regra"
EDITAL_C1 = EDITAIS / "edital_sgtes_03_2025_dou.pdf"
EDITAL_C2 = EDITAIS / "edital_sgtes_01_2026_ciclo2.html"
EDITAL_C3 = EDITAIS / "edital_sgtes_06_2026_edital_28_2026_ciclo3.html"  # conteúdo é PDF

NOME_EST = "N_estimativas.csv"
NOME_RESUMO = "N_resumo.json"
DIR_FIG = "N_figuras"

DATA_EXECUCAO = "2026-10-19"
ESTATUTO = "PROTOCOLO_48_POS_RESULTADO"
NATUREZA = "EMPIRICO"
CORTES = L.CORTES_MIL                      # (300, 400)
H = L.H_PRINCIPAL_MIL                      # 50
H_SENS = L.H_SENSIBILIDADE_MIL             # (30, 80)
FATORES_M = (0.5, 1.0, 2.0)
DONUT_MIL = 2                              # S-j: sai |IVS - corte| < 0,002
FATOR_MDE = 2.8                            # MDE = 2,8 x EP (80% de poder, 5% bicaudal)
ROTULO_CORTE = E6.ROTULO_CORTE
EMPILHADO = E6.EMPILHADO
SUPORTE_POS = E6.SUPORTE_POS_RESULTADO
ID_SEMENTE_POP = E6.ID_SEMENTE_POP
# S-i, como no E9 (16_estimar_E9_escolha.py): grade de cortes falsos de 0,010 em 0,010 entre 0,190 e 0,510,
# a mais de 0,010 dos cortes verdadeiros; cada corte falso usa só os municípios do mesmo segmento de bolsa.
PLACEBOS_MIL = tuple(c for c in range(190, 511, 10) if all(abs(c - k) > 10 for k in CORTES))
LARGURA_FAIXA_FIG = 10                     # faixas de IVS de 0,010 nas figuras
ALCANCE_FIG = 100                          # figuras mostram até 0,100 de cada lado (sem cruzar o outro corte)

CONTRASTE = E6.CONTRASTE

CATALOGO_N = [
    {"id": "N1", "col": "n_alocados_ch1", "ciclos": (1, 2, 3), "controle": "vagas_oferecidas",
     "desc": "vagas preenchidas na 1a chamada (medicos alocados, por municipio)",
     "unidade": "vagas preenchidas por municipio"},
    {"id": "N2", "col": "n_celulas_preenchidas_ch1", "ciclos": (1, 2, 3), "controle": "n_celulas",
     "desc": "celulas (estabelecimento x curso) com >= 1 alocado na 1a chamada",
     "unidade": "celulas por municipio"},
    {"id": "N3", "col": "n_celulas_preenchidas_ate_ch2", "ciclos": (1, 2), "controle": "n_celulas",
     "desc": "celulas com >= 1 alocado ate a 2a chamada", "unidade": "celulas por municipio"},
    {"id": "N4", "col": "n_ativos_ciclo", "ciclos": (1, 2), "controle": "vagas_oferecidas",
     "desc": "especialistas ativos do ciclo no retrato de 09/10/2026", "unidade": "especialistas ativos por municipio"},
]
# Variáveis de oferta (S-c e controles). "VO" é a forma principal das vagas oferecidas, fixada pela verificação.
OFERTA = {
    "VIC": {"col": "vagas_imediatas_mais_cr", "desc": "vagas oferecidas no quadro da 1a chamada: imediatas + cadastro reserva",
            "unidade": "vagas oferecidas por municipio"},
    "VI": {"col": "vagas_imediatas", "desc": "vagas imediatas no quadro da 1a chamada",
           "unidade": "vagas oferecidas por municipio"},
    "NC": {"col": "n_celulas", "desc": "celulas (estabelecimento x curso) no quadro da 1a chamada",
           "unidade": "celulas por municipio"},
}

# Trechos dos editais (citação literal, com o item; o SHA-256 do arquivo vai para o resumo).
TRECHOS_EDITAL = [
    {"arquivo": EDITAL_C1, "edital": "Edital de Chamamento Publico SGTES/MS no 3/2025 (DOU), ciclo 1", "ciclo": "1",
     "item": "4.1.3.3",
     "trecho": "O candidato poderá escolher, dentre suas opções, município com vaga para preenchimento imediato e "
               "município que esteja em cadastro de reserva."},
    {"arquivo": EDITAL_C1, "edital": "Edital de Chamamento Publico SGTES/MS no 3/2025 (DOU), ciclo 1", "ciclo": "1",
     "item": "4.1.3.4",
     "trecho": "Considera-se em cadastro de reserva o município que, na oferta inicial, não tinha vaga imediata, mas "
               "que poderá recebê-la por remanejamento"},
    {"arquivo": EDITAL_C1, "edital": "Edital de Chamamento Publico SGTES/MS no 3/2025 (DOU), ciclo 1", "ciclo": "1",
     "item": "5.7",
     "trecho": "as vagas remanescentes poderão ser redistribuídas para municípios com cadastro de reserva e que "
               "tenham candidatos na lista de espera"},
    {"arquivo": EDITAL_C3, "edital": "Edital SGTES/MS no 28/2026, ciclo 3", "ciclo": "3", "item": "4.1.3.4",
     "trecho": "A disponibilização de vaga para esses municípios poderá ocorrer por remanejamento de vagas não "
               "ocupadas"},
    {"arquivo": EDITAL_C3, "edital": "Edital SGTES/MS no 28/2026, ciclo 3", "ciclo": "3", "item": "5.7",
     "trecho": "as vagas remanescentes poderão ser redistribuídas para municípios com cadastro de reserva e que "
               "tenham candidatos na lista de espera"},
]


class FalhaValidacao(RuntimeError):
    """Validação obrigatória falhou: o script para sem gravar estimativas."""


sha256 = E6.sha256
rotulo = E6.rotulo
_nan_none = E6._nan_none


def _gravar_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(_nan_none(obj), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _juntar(*notas) -> str:
    return "; ".join(n for n in notas if n)


# ---------------------------------------------------------------------------
# Verificação: um alocado da 1a chamada pode ocupar vaga de cadastro reserva?
# ---------------------------------------------------------------------------

def verificar_cadastro_reserva(cel: pd.DataFrame, vm: pd.DataFrame, dicionario: dict | None) -> dict:
    """Contagens por ciclo nos quadros e resultados (sem quebra por corte) e trechos dos editais.

    Regra do protocolo 48 (§1): se um alocado pode ocupar cadastro reserva, o controle principal é
    vagas imediatas + CR; senão, só imediatas. "Pode" = algum ciclo tem alocado da 1a chamada em célula
    só de cadastro reserva ou mais alocados que vagas imediatas na célula.
    """
    por_ciclo = {}
    for k, g in cel.groupby("ciclo"):
        a, vi, vc = (g[c].astype(float) for c in ("n_alocados_ch1", "vagas_imediatas", "vagas_cr"))
        mk = vm[vm["ciclo"] == k]
        por_ciclo[str(int(k))] = {
            "celulas": int(len(g)),
            "celulas_com_ausencia_em_alocados_ou_vagas": int((a.isna() | vi.isna() | vc.isna()).sum()),
            "celulas_so_cadastro_reserva": int((vi == 0).sum()),
            "alocados_ch1": float(a.sum()),
            "vagas_imediatas": float(vi.sum()),
            "vagas_cr": float(vc.sum()),
            "alocados_em_celulas_so_cadastro_reserva": float(a[vi == 0].sum()),
            "celulas_so_cadastro_reserva_com_alocado": int(((vi == 0) & (a > 0)).sum()),
            "celulas_com_alocados_acima_das_imediatas": int((a > vi).sum()),
            "alocados_acima_das_imediatas": float((a - vi).clip(lower=0).sum()),
            "celulas_com_alocados_acima_de_imediatas_mais_cr": int((a > vi + vc).sum()),
            "municipios": int(len(mk)),
            "municipios_com_N1_acima_das_imediatas": int((mk["n_alocados_ch1"] > mk["vagas_imediatas"]).sum()),
            "municipios_com_N1_acima_de_imediatas_mais_cr": int(
                (mk["n_alocados_ch1"] > mk["vagas_imediatas"] + mk["vagas_cr"]).sum()),
        }
    # Conferência com o diagnóstico da tarefa B (linhas alocadas em célula só de cadastro reserva).
    conf = {}
    if dicionario is not None:
        cas = dicionario.get("casamento_entre_arquivos", {}).get("candidaturas_contra_quadro_da_1a_chamada", {})
        for k, nome in (("2", "c2_ch1"), ("3", "c3_ch1")):
            ref = cas.get(nome, {}).get("linhas_alocadas_em_celula_so_cadastro_reserva")
            if ref is None:
                continue
            igual = float(ref) == por_ciclo[k]["alocados_em_celulas_so_cadastro_reserva"]
            if not igual:
                raise FalhaValidacao(f"ciclo {k}: alocados em celula so CR ({por_ciclo[k]['alocados_em_celulas_so_cadastro_reserva']}) "
                                     f"difere do dicionario da tarefa B ({ref})")
            conf[f"ciclo_{k}_igual_ao_dicionario_tarefa_B"] = True
    editais = []
    for t in TRECHOS_EDITAL:
        editais.append({"arquivo": rotulo(t["arquivo"]), "sha256": sha256(t["arquivo"]), "edital": t["edital"],
                        "ciclo": t["ciclo"], "item": t["item"], "trecho": t["trecho"]})
    pode_dados = {k: bool(v["alocados_em_celulas_so_cadastro_reserva"] > 0 or v["celulas_com_alocados_acima_das_imediatas"] > 0)
                  for k, v in por_ciclo.items()}
    pode = any(pode_dados.values())
    return {
        "pergunta": "um alocado da 1a chamada pode ocupar vaga de cadastro reserva?",
        "resposta": "sim" if pode else "nao",
        "pode_por_ciclo_nos_dados": pode_dados,
        "contagens_por_ciclo": por_ciclo,
        "conferencia_tarefa_B": conf,
        "editais": editais,
        "edital_ciclo_2": {"arquivo": rotulo(EDITAL_C2), "sha256": sha256(EDITAL_C2),
                           "nota": "a copia no repositorio e so a pagina do chamamento (sem o texto do edital); "
                                   "nao examinado"},
        "controle_principal": "VIC" if pode else "VI",
        "controle_sensibilidade": "VI" if pode else "VIC",
        "regra": "protocolo 48, §1: se o alocado pode ocupar cadastro reserva, vagas oferecidas = vagas_imediatas + "
                 "vagas_cr; senao, so vagas_imediatas. Decidido antes de estimar, so com contagens globais por ciclo "
                 "(sem quebra por corte, faixa ou IVS) e com o texto dos editais",
        "notas": [
            "Ciclo 1: n_alocados_ch1 = confirmacoes de local na alocacao sub judice (tarefa B); celulas com mais "
            "confirmacoes que vagas imediatas + CR ficam registradas acima e nao sao alteradas.",
            "Ciclo 1: n_celulas_preenchidas_ch1 (N2) segue o Y1 do E3 (confirmacao OU homologacao); por isso N2 pode "
            "contar celula sem confirmacao.",
            "Ciclo 2: nenhum alocado da 1a chamada em celula so de cadastro reserva; o edital 1/2026 nao foi examinado "
            "(so a pagina do chamamento esta no repositorio). A regra vale para todos os ciclos; a forma 'so imediatas' "
            "e relatada como sensibilidade.",
        ],
    }


# ---------------------------------------------------------------------------
# Amostras (um corte; ou empilhado por corte e/ou ciclo)
# ---------------------------------------------------------------------------

class Amostra:
    """Linhas de estimação: s_mil, corte_mil por linha, grupo, cluster (município) e as colunas de dados."""

    def __init__(self, d: pd.DataFrame, *, empilhada: bool):
        self.d = d.reset_index(drop=True)
        self.empilhada = empilhada
        self.s = self.d["s_mil"].to_numpy(dtype=float)
        self.c = self.d["corte_mil"].to_numpy(dtype=float)
        self.g = self.d["grupo"].astype(str).to_numpy()
        self.cl = self.d["co_ibge"].astype(str).to_numpy()
        self.t = (L.normalizar_s_mil(self.s) - self.c > 0).astype(float)

    def col(self, nome: str) -> np.ndarray:
        return self.d[nome].to_numpy(dtype=float)

    def subconjunto(self, mascara: np.ndarray) -> "Amostra":
        return Amostra(self.d[mascara], empilhada=self.empilhada)

    @property
    def corte_unico(self) -> int:
        cs = np.unique(self.c)
        if cs.size != 1:
            raise ValueError("amostra com mais de um corte")
        return int(cs[0])


def montar_amostra(partes: list[tuple[pd.DataFrame, int, str]], *, empilhada: bool) -> Amostra:
    blocos = []
    for d, corte, grupo in partes:
        b = d.copy()
        b["corte_mil"] = corte
        b["grupo"] = grupo
        blocos.append(b)
    return Amostra(pd.concat(blocos, ignore_index=True), empilhada=empilhada)


# ---------------------------------------------------------------------------
# Estimadores (chamam a rdd_lib)
# ---------------------------------------------------------------------------

def _kern(a: Amostra, h) -> np.ndarray:
    return L.pesos_kernel(L.normalizar_s_mil(a.s) - a.c, h)


COEF_UNICO = "unico"   # rótulo do "grupo" quando o controle tem um só coeficiente (sensibilidade da auditoria 20)
ROTULO_AUD20 = ("SENSIBILIDADE_AUDITORIA_20 (fora do protocolo: um so coeficiente do controle para todos os "
                "grupos ciclo x corte)")


def colunas_controle(a: Amostra, y: np.ndarray, v: np.ndarray, h, *, lados: bool = False,
                     peso: np.ndarray | None = None, unico: bool = False) -> tuple[np.ndarray, list[str], dict, dict]:
    """Controle centrado na média ponderada pelo kernel da janela, um coluna por grupo (comum aos dois lados).

    Linhas com v ausente ficam NaN na coluna do seu grupo (a rdd_lib as descarta e conta); nunca viram zero.
    `lados=True` acrescenta T x controle (S-f). `unico=True` (só na sensibilidade da auditoria 20) usa uma só
    coluna para todos os grupos. Devolve (Z, nomes, v_barra por grupo, colunas por grupo).
    """
    k = _kern(a, h)
    ok_base = (k > 0) & np.isfinite(y) & np.isfinite(v)
    if peso is not None:
        ok_base &= np.isfinite(peso) & (peso > 0)
    cols, nomes, vbar, vc_g = [], [], {}, {}
    grupos = [COEF_UNICO] if unico else sorted(np.unique(a.g).tolist())
    for gl in grupos:
        m = np.ones(len(a.g), dtype=bool) if unico else a.g == gl
        ok = ok_base & m
        vb = float(np.sum(k[ok] * v[ok]) / np.sum(k[ok])) if ok.any() else float("nan")
        vbar[gl] = vb
        vc = np.where(m, v - vb, 0.0)
        vc_g[gl] = vc
        sufixo = f"[{gl}]" if a.empilhada else ""
        cols.append(vc)
        nomes.append(f"controle{sufixo}")
        if lados:
            cols.append(a.t * vc)
            nomes.append(f"T_controle{sufixo}")
    return np.column_stack(cols), nomes, vbar, vc_g


def ajustar(a: Amostra, y: np.ndarray, h, *, v: np.ndarray | None = None, lados: bool = False,
            peso: np.ndarray | None = None, unico: bool = False) -> dict:
    """Local linear (um corte) ou empilhado (CR1 por município), com ou sem controle; devolve o resultado da rdd_lib.

    Extras: `gamma` e `ep_gamma` por grupo, `v_barra`, `vc_g` (controle centrado por grupo), `media_abaixo`
    (média simples do outcome bruto nas linhas usadas do lado de baixo) e `_detalhes`.
    """
    Z = nomes = None
    vbar, vc_g = {}, {}
    if v is not None:
        Z, nomes, vbar, vc_g = colunas_controle(a, y, v, h, lados=lados, peso=peso, unico=unico)
    if a.empilhada:
        r = L.rd_empilhado(a.s, y, a.c, grupo=a.g, h_mil=h, cluster=a.cl, ids_unidade=a.cl, Z=Z, nomes_z=nomes,
                           peso=peso, detalhes=True)
    else:
        r = L.rd_local_linear(a.s, y, a.corte_unico, h, Z=Z, nomes_z=nomes, peso=peso, detalhes=True)
    r["v_barra"] = vbar
    r["vc_g"] = vc_g
    r["gamma"], r["ep_gamma"] = {}, {}
    r["media_abaixo"] = float("nan")
    if "_detalhes" in r:
        d = r["_detalhes"]
        ab = d["usa"] & (d["x_mil"] <= 0)
        r["media_abaixo"] = float(np.mean(y[ab])) if ab.any() else float("nan")
        fit = d["fit"]
        if v is not None:
            for gl in vbar:
                nome = f"controle[{gl}]" if a.empilhada else "controle"
                if nome in fit["nomes"]:
                    i = fit["nomes"].index(nome)
                    r["gamma"][gl] = float(fit["beta"][i])
                    r["ep_gamma"][gl] = float(math.sqrt(max(fit["V"][i, i], 0.0)))
                else:
                    r["gamma"][gl] = float("nan")
                    r["ep_gamma"][gl] = float("nan")
    return r


def wald_igualdade_gamma(r: dict) -> dict | None:
    """Wald (CR1 da S-a principal) de H0: coeficientes do controle iguais entre os grupos (auditoria 20)."""
    if "_detalhes" not in r or len(r.get("gamma", {})) < 2:
        return None
    fit = r["_detalhes"]["fit"]
    idx = [fit["nomes"].index(f"controle[{g}]") for g in sorted(r["gamma"]) if f"controle[{g}]" in fit["nomes"]]
    if len(idx) < 2:
        return None
    b = fit["beta"][idx]
    R = np.zeros((len(idx) - 1, len(idx)))
    R[:, 0] = 1.0
    R[np.arange(len(idx) - 1), np.arange(1, len(idx))] = -1.0
    Vb = fit["V"][np.ix_(idx, idx)]
    w = float((R @ b) @ np.linalg.solve(R @ Vb @ R.T, R @ b))
    gl = len(idx) - 1
    return {"n_grupos": len(idx), "gl": gl, "chi2": w, "p_valor": float(chi2.sf(w, gl))}


def _nota_wald(wd: dict | None) -> str:
    if wd is None:
        return ""
    return (f"Wald (CR1) da igualdade dos coeficientes do controle entre os {wd['n_grupos']} grupos na S-a "
            f"principal: chi2({wd['gl']}) = {wd['chi2']:.4g}, p = {wd['p_valor']:.4g}")


def residualizar(y: np.ndarray, r: dict) -> np.ndarray:
    """y~ = y - sum_g gamma_g (v - v_barra_g) 1[g], com gamma da regressão S-a na janela (NaN onde v ausente)."""
    ytil = np.asarray(y, dtype=float).copy()
    for gl, vc in r["vc_g"].items():
        ytil = ytil - r["gamma"].get(gl, float("nan")) * vc
    return ytil


def honesto(a: Amostra, y: np.ndarray, *, M: float | None = None, pos_resultado: bool = False) -> dict:
    """IC honesto (Armstrong-Kolesár, classe de Taylor) com a regra de M do E6."""
    if a.empilhada:
        if pos_resultado:
            sup = {gl: SUPORTE_POS[int(cc)] for gl, cc in pd.Series(a.c, index=a.g).groupby(level=0).first().items()}
            return L.rd_empilhado_honesto(a.s, y, a.c, grupo=a.g, h_mil=H, cluster=a.cl, ids_unidade=a.cl, suporte_mil=sup)
        if M is None:
            return L.rd_empilhado_honesto(a.s, y, a.c, grupo=a.g, h_mil=H, cluster=a.cl, ids_unidade=a.cl,
                                          cortes_vizinhos=CORTES)
        return L.rd_empilhado_honesto(a.s, y, a.c, grupo=a.g, h_mil=H, M=M, cluster=a.cl, ids_unidade=a.cl)
    c = a.corte_unico
    if pos_resultado:
        return L.rd_honesto(a.s, y, c, H, suporte_mil=SUPORTE_POS[c])
    if M is None:
        return L.rd_honesto(a.s, y, c, H, cortes_vizinhos=CORTES)
    return L.rd_honesto(a.s, y, c, H, M=M)


# Poisson local com covariáveis e/ou empilhado: o mesmo algoritmo de `L.rd_poisson_local` (IRLS com meio-passo,
# critério de convergência e sanduíche HC1/CR1), com colunas extras. Com um corte, sem covariável, reproduz a
# rdd_lib (conferido a cada chamada com offset, falha fechada).

def poisson(a: Amostra, y: np.ndarray, h, *, offset: np.ndarray | None = None, covariavel: np.ndarray | None = None,
            max_iter: int = 200, tol: float = 1e-10) -> dict:
    n = len(a.s)
    yv = np.asarray(y, dtype=float)
    off = np.asarray(offset, dtype=float) if offset is not None else np.zeros(n)
    cov = np.asarray(covariavel, dtype=float) if covariavel is not None else None
    s = L.normalizar_s_mil(a.s)
    x_mil = s - a.c
    kern = L.pesos_kernel(x_mil, h)
    x = x_mil / 1000.0
    t = a.t
    grupos = sorted(np.unique(a.g).tolist())
    cols, nomes, interceptos = [], [], []
    if a.empilhada:
        for gl in grupos:
            ind = (a.g == gl).astype(float)
            interceptos.append((len(cols), a.g == gl))
            cols.extend([ind, ind * x, ind * t * x])
            nomes.extend([f"const[{gl}]", f"x[{gl}]", f"T_x[{gl}]"])
        cols.append(t)
        nomes.append("T")
    else:
        interceptos.append((0, np.ones(n, dtype=bool)))
        cols.extend([np.ones(n), x, t, t * x])
        nomes.extend(["const", "x", "T", "T_x"])
    if cov is not None:
        for gl in grupos:
            m = a.g == gl
            cols.append(np.where(m, cov, 0.0) if a.empilhada else cov)
            nomes.append(f"log_controle[{gl}]" if a.empilhada else "log_controle")
            if not a.empilhada:
                break
    X = np.column_stack(cols)
    i_T = nomes.index("T")
    cov_ok = np.isfinite(X).all(axis=1)
    usa = (kern > 0) & np.isfinite(yv) & np.isfinite(off) & cov_ok
    janela = kern > 0
    res = {"tau": float("nan"), "ep": float("nan"), "ic95_inf": float("nan"), "ic95_sup": float("nan"),
           "p_valor": float("nan"), "n_abaixo": int(np.unique(a.cl[usa & (x_mil <= 0)]).size),
           "n_acima": int(np.unique(a.cl[usa & (x_mil > 0)]).size), "n_obs": int(usa.sum()), "n_clusters": None,
           "efeito_relativo": float("nan"), "efeito_relativo_ic95_inf": float("nan"),
           "efeito_relativo_ic95_sup": float("nan"), "convergiu": False, "iteracoes": 0,
           "n_descartadas_y_ausente": int((janela & ~np.isfinite(yv)).sum()),
           "n_descartadas_offset_ausente": int((janela & np.isfinite(yv) & ~np.isfinite(off)).sum()),
           "n_descartadas_covariavel_ausente": int((janela & np.isfinite(yv) & np.isfinite(off) & ~cov_ok).sum()),
           "nota": ""}
    if (yv[usa] < 0).any():
        raise ValueError("Poisson local exige y >= 0")
    notas = [f"{res[k]} linhas na janela descartadas por {k.removeprefix('n_descartadas_').replace('_', ' ')}"
             for k in ("n_descartadas_y_ausente", "n_descartadas_offset_ausente", "n_descartadas_covariavel_ausente")
             if res[k]]

    def falha(motivo: str) -> dict:
        res["nota"] = _juntar(*notas, motivo)
        return res

    w = kern
    for gl in grupos:
        em = usa & (a.g == gl)
        for lado, m in (("abaixo", em & (x_mil <= 0)), ("acima", em & (x_mil > 0))):
            if np.unique(s[m]).size < 2:
                return falha(f"suporte insuficiente no grupo {gl}: menos de 2 mass points com peso positivo ({lado})")
            if np.sum(w[m] * yv[m]) <= 0:
                return falha(f"lado sem eventos ({lado}, grupo {gl}): salto em log nao identificado")
            if np.unique(s[m & (w * np.where(np.isfinite(yv), yv, 0.0) > 0)]).size < 2:
                return falha(f"separacao ({lado}, grupo {gl}): eventos em um unico mass point")
    k = X.shape[1]
    if int(usa.sum()) <= k:
        return falha("graus de liberdade insuficientes")
    Xu, yy, ww, oo = X[usa], yv[usa], w[usa], off[usa]
    escala = max(1.0, float(np.sum(ww * yy)))

    def pseudo_ll(b):
        with np.errstate(over="ignore", invalid="ignore"):
            eta = oo + Xu @ b
            return float(np.sum(ww * (yy * eta - np.exp(eta))))

    beta = np.zeros(k)
    for j, mg in interceptos:
        mu_g = mg[usa]
        beta[j] = math.log(np.sum(ww[mu_g] * yy[mu_g]) / np.sum(ww[mu_g] * np.exp(oo[mu_g])))
    ll = pseudo_ll(beta)
    convergiu, motivo, it = False, "IRLS nao convergiu em max_iter iteracoes", 0
    for it in range(1, max_iter + 1):
        mu = np.exp(oo + Xu @ beta)
        grad = Xu.T @ (ww * (yy - mu))
        Hm = Xu.T @ (Xu * (ww * mu)[:, None])
        try:
            passo = np.linalg.solve(Hm, grad)
        except np.linalg.LinAlgError:
            motivo = "hessiana singular no IRLS (possivel separacao ou covariavel colinear)"
            break
        fator, melhorou = 1.0, False
        while fator >= 1e-8:
            novo = beta + fator * passo
            ll_novo = pseudo_ll(novo)
            if math.isfinite(ll_novo) and ll_novo >= ll - 1e-12 * abs(ll):
                melhorou = True
                break
            fator /= 2.0
        if not melhorou:
            motivo = "busca em linha parou sem melhorar a pseudo-verossimilhanca"
            break
        beta, ll = novo, ll_novo
        mu = np.exp(oo + Xu @ beta)
        grad = Xu.T @ (ww * (yy - mu))
        if np.max(np.abs(fator * passo)) < tol and np.max(np.abs(grad)) / escala < 1e-8:
            convergiu = True
            break
    res["iteracoes"], res["convergiu"] = it, convergiu
    if not convergiu or not np.isfinite(beta).all():
        return falha(motivo)
    mu = np.exp(oo + Xu @ beta)
    try:
        bread = np.linalg.inv(Xu.T @ (Xu * (ww * mu)[:, None]))
    except np.linalg.LinAlgError:
        return falha("hessiana singular na solucao")
    score = Xu * (ww * (yy - mu))[:, None]
    m_obs = len(yy)
    if a.empilhada:
        _, idx = np.unique(a.cl[usa], return_inverse=True)
        G = int(idx.max()) + 1
        S = np.zeros((G, k))
        np.add.at(S, idx, score)
        meat = S.T @ S
        fator = (G / (G - 1)) * ((m_obs - 1) / (m_obs - k))
        res["n_clusters"] = G
    else:
        meat = score.T @ score
        fator = m_obs / (m_obs - k)
    V = bread @ meat @ bread * fator
    tau, ep = float(beta[i_T]), float(math.sqrt(max(V[i_T, i_T], 0.0)))
    res.update({"tau": tau, "ep": ep, "ic95_inf": tau - L.Z_975 * ep, "ic95_sup": tau + L.Z_975 * ep,
                "p_valor": L.p_normal(tau / ep) if ep > 0 else float("nan"),
                "efeito_relativo": math.expm1(tau), "efeito_relativo_ic95_inf": math.expm1(tau - L.Z_975 * ep),
                "efeito_relativo_ic95_sup": math.expm1(tau + L.Z_975 * ep)})
    if cov is not None:
        res["gamma_log_controle"] = {nm: float(beta[nomes.index(nm)]) for nm in nomes if nm.startswith("log_controle")}
    res["nota"] = _juntar(*notas)
    return res


def conferir_poisson_lib(a: Amostra, y: np.ndarray, off: np.ndarray, meu: dict, tol: float = 1e-8) -> None:
    """Com um corte e offset, sem covariável, o Poisson daqui tem de reproduzir `L.rd_poisson_local`."""
    ref = L.rd_poisson_local(a.s, y, a.corte_unico, H, offset=off)
    for k in ("tau", "ep"):
        a_, b_ = meu[k], ref[k]
        if not (np.isnan(a_) and np.isnan(b_)) and not abs(a_ - b_) <= tol * max(1.0, abs(b_)):
            raise FalhaValidacao(f"Poisson local diverge da rdd_lib em {k}: {a_} vs {b_}")


# ---------------------------------------------------------------------------
# Linhas de saída
# ---------------------------------------------------------------------------

COLUNAS = [
    "natureza_dos_dados", "estatuto", "familia", "outcome_id", "outcome", "descricao_outcome", "populacao", "ciclo",
    "corte", "especificacao", "variante", "controle", "forma_controle", "estimador", "no_protocolo", "rotulo",
    "status", "h", "w_lr", "corte_placebo", "n_abaixo", "n_acima", "n_obs", "n_clusters",
    "n_descartadas_y_ausente", "n_descartadas_controle_ausente", "tau", "ep", "ic95_inf", "ic95_sup", "p_valor",
    "ic_honesto_inf", "ic_honesto_sup", "M", "fator_M", "vies_max", "coef_controle", "ep_coef_controle",
    "media_abaixo", "efeito_relativo_media_abaixo", "mde", "mde_relativo_media_abaixo", "efeito_relativo",
    "efeito_relativo_ic95_inf", "efeito_relativo_ic95_sup", "pesos_grupos", "entra_holm", "p_holm", "unidade", "nota",
]


def nova_linha(meta: dict, esp: str, variante: str, estimador: str, *, h_mil, unidade: str, controle: str = "",
               forma: str = "", no_protocolo: bool = True, rot: str = "") -> dict:
    linha = {c: np.nan for c in COLUNAS}
    linha.update({"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "familia": "N", **meta,
                  "especificacao": esp, "variante": variante, "controle": controle, "forma_controle": forma,
                  "estimador": estimador, "no_protocolo": bool(no_protocolo), "rotulo": rot, "status": "EXECUTADO",
                  "h": (h_mil / 1000.0) if h_mil is not None and np.isfinite(h_mil) else np.nan,
                  "unidade": unidade, "nota": "", "entra_holm": False})
    return linha


def preencher(linha: dict, res: dict | None, *, media: float | None = None) -> dict:
    if res is None:
        return linha
    for k in ("tau", "ep", "ic95_inf", "ic95_sup", "p_valor", "n_abaixo", "n_acima", "n_obs", "n_clusters",
              "efeito_relativo", "efeito_relativo_ic95_inf", "efeito_relativo_ic95_sup", "n_descartadas_y_ausente"):
        if k in res and res[k] is not None:
            linha[k] = res[k]
    if linha.get("controle"):
        # Controle ausente: como covariável (S-a, S-d), offset (S-d) ou peso (S-e); a rdd_lib conta cada motivo.
        linha["n_descartadas_controle_ausente"] = sum(int(res.get(f"n_descartadas_{m}", 0) or 0)
                                                      for m in ("covariavel_ausente", "offset_ausente", "peso_ausente"))
    if res.get("pesos_grupos"):
        linha["pesos_grupos"] = json.dumps({k: round(v, 12) for k, v in res["pesos_grupos"].items()})
    if res.get("gamma"):
        gm = res["gamma"]
        if len(gm) == 1:
            (gl, gv), = gm.items()
            linha["coef_controle"], linha["ep_coef_controle"] = gv, res["ep_gamma"][gl]
        else:
            linha["coef_controle"] = np.nan
            linha["nota"] = _juntar(linha["nota"], "coeficiente do controle por grupo: " + json.dumps(
                {g: round(v, 6) for g, v in gm.items()}))
    notas = [linha.get("nota", ""), res.get("nota", "")]
    if res.get("covariaveis_descartadas"):
        notas.append(f"colunas descartadas: {res['covariaveis_descartadas']}")
    linha["nota"] = _juntar(*notas)
    if media is None:
        media = res.get("media_abaixo", np.nan)
    linha["media_abaixo"] = media
    tau, ep = float(linha["tau"]), float(linha["ep"])
    if np.isfinite(ep):
        linha["mde"] = FATOR_MDE * ep
    if media is not None and np.isfinite(media) and media != 0:
        linha["efeito_relativo_media_abaixo"] = tau / media if np.isfinite(tau) else np.nan
        linha["mde_relativo_media_abaixo"] = linha["mde"] / media if np.isfinite(linha["mde"]) else np.nan
    if not np.isfinite(tau):
        linha["status"] = "SEM_ESTIMATIVA"
        if not linha["nota"]:
            linha["nota"] = "biblioteca devolveu NaN sem motivo"
    return linha


def nao_executado(meta: dict, esp: str, variante: str, motivo: str, *, unidade: str, controle: str = "",
                  forma: str = "") -> dict:
    linha = nova_linha(meta, esp, variante, "-", h_mil=H, unidade=unidade, controle=controle, forma=forma)
    linha["status"] = "NAO_EXECUTADO"
    linha["nota"] = motivo
    return linha


def _est(a: Amostra, base: str) -> str:
    if a.empilhada:
        return f"empilhado: {base}; intercepto e inclinacoes por grupo x lado, tau comum, CR1 por municipio"
    return f"local linear sharp, kernel triangular; {base}; EP HC1"


def linha_honesta(meta, hon: dict, *, fator, pos: bool, unidade, controle, forma, esp, media, residualizado) -> dict:
    variante = "ic_honesto_pos_resultado" if pos else f"ic_honesto_M_x{fator:g}"
    rot = E6.ROTULO_POS if pos else ""
    est = ("IC honesto Armstrong-Kolesar (classe de Taylor; " + ("CR1" if hon.get("variancia") == "cluster" else
           "variancia por vizinhos, J=3") + ")" + ("; outcome residualizado na janela, y - gamma (v - v_barra), "
                                                   "gamma de S-a tratado como fixo" if residualizado else ""))
    linha = nova_linha(meta, esp, variante, est, h_mil=H, unidade=unidade, controle=controle, forma=forma,
                       no_protocolo=not pos, rot=rot)
    for k in ("tau", "ep", "ic95_inf", "ic95_sup", "p_valor", "n_abaixo", "n_acima", "M", "vies_max", "n_clusters"):
        v = hon.get(k)
        if v is not None:
            linha[k] = v
    linha["ic_honesto_inf"], linha["ic_honesto_sup"] = linha["ic95_inf"], linha["ic95_sup"]
    linha["fator_M"] = fator
    linha["media_abaixo"] = media
    if np.isfinite(float(linha["ep"])):
        linha["mde"] = FATOR_MDE * float(linha["ep"])
    linha["nota"] = _juntar("ep = EP usado no IC honesto; M = " + (
        "regra de bolso com suporte POS_RESULTADO (lado interno ate o outro corte), como no E6" if pos else
        f"{fator:g} x regra de bolso (suporte ate o ponto medio entre cortes), regra do E6"), hon.get("nota", ""))
    if not np.isfinite(float(linha["ic95_inf"])):
        linha["status"] = "SEM_ESTIMATIVA"
    return linha


# ---------------------------------------------------------------------------
# Especificações de um outcome N numa amostra
# ---------------------------------------------------------------------------

def especificacoes_n(spec: dict, meta: dict, a: Amostra, ctrl: dict, *, w_lr: dict | None = None, extras: dict | None = None, holm: bool = False) -> list[dict]:
    """S-a, S-b, h, controle alternativo, decomposição, S-d, S-e, S-f, S-g, S-j (e S-h por ciclo x corte).

    `holm=True` marca a linha S-a principal para o Holm (só a amostra com ciclos e cortes empilhados).
    """
    linhas: list[dict] = []
    y = a.col(spec["col"])
    un = spec["unidade"]
    cp = ctrl["principal"][spec["controle"]]          # {"id": "VIC", "col": ...}
    v = a.col(cp["col"])
    ctl, forma = cp["col"], cp["id"]

    # S-a principal (+ honesto) e S-b principal.
    ra = ajustar(a, y, H, v=v)
    la = preencher(nova_linha(meta, "S-a", "principal", _est(a, "controle linear comum aos dois lados (CCFT 2019)"),
                              h_mil=H, unidade=un, controle=ctl, forma=forma), ra)
    la["entra_holm"] = bool(holm and la["status"] == "EXECUTADO")
    linhas.append(la)
    rb = ajustar(a, y, H)
    lb = preencher(nova_linha(meta, "S-b", "principal", _est(a, "sem controle (efeito total da faixa)"), h_mil=H,
                              unidade=un), rb)
    linhas.append(lb)
    # Conferência FWL: o salto de y~ (sem controle) é o de S-a.
    ytil = residualizar(y, ra) if "_detalhes" in ra else None
    if ytil is not None and np.isfinite(ra["tau"]):
        rt = ajustar(a, ytil, H)
        if not abs(rt["tau"] - ra["tau"]) <= 1e-8 * max(1.0, abs(ra["tau"])):
            raise FalhaValidacao(f"residualizacao nao reproduz S-a em {meta}: {rt['tau']} vs {ra['tau']}")
    # Sensibilidade de h.
    for h in H_SENS:
        linhas.append(preencher(nova_linha(meta, "S-a", f"h={h / 1000:.3f}", _est(a, "controle linear comum"), h_mil=h,
                                           unidade=un, controle=ctl, forma=forma), ajustar(a, y, h, v=v)))
        linhas.append(preencher(nova_linha(meta, "S-b", f"h={h / 1000:.3f}", _est(a, "sem controle"), h_mil=h,
                                           unidade=un), ajustar(a, y, h)))
    # Controle na forma alternativa (só onde o controle é vagas oferecidas).
    if spec["controle"] == "vagas_oferecidas":
        alt = ctrl["sensibilidade"]["vagas_oferecidas"]
        linhas.append(preencher(nova_linha(meta, "S-a", "controle_forma_alternativa",
                                           _est(a, f"controle linear comum: {alt['col']}"), h_mil=H, unidade=un,
                                           controle=alt["col"], forma=alt["id"]), ajustar(a, y, H, v=a.col(alt["col"]))))
    # Sensibilidade da auditoria 20 (fora do protocolo): no empilhado, um só coeficiente do controle para todos os
    # grupos, com teste de Wald da igualdade dos coeficientes por grupo da S-a principal.
    if a.empilhada:
        lu = preencher(nova_linha(meta, "S-a", "controle_coeficiente_unico",
                                  _est(a, "controle linear comum aos dois lados e a todos os grupos (um so coeficiente)"),
                                  h_mil=H, unidade=un, controle=ctl, forma=forma, no_protocolo=False, rot=ROTULO_AUD20),
                       ajustar(a, y, H, v=v, unico=True))
        wd = wald_igualdade_gamma(ra)
        lu["nota"] = _juntar(lu["nota"], _nota_wald(wd))
        linhas.append(lu)
        if holm and extras is not None:
            extras.setdefault("wald_gamma", {})[spec["id"]] = wd
    # Decomposição exata: total (S-b na amostra de S-a) = via oferta (sum gamma_g x salto do controle) + S-a.
    if "_detalhes" in ra and np.isfinite(ra["tau"]):
        okv = np.isfinite(v)
        sub = a.subconjunto(okv) if not okv.all() else a
        rb_mesma = ajustar(sub, y[okv], H) if not okv.all() else rb
        via = 0.0
        for gl, vc in ra["vc_g"].items():
            dg = ajustar(sub, vc[okv], H)
            via += ra["gamma"][gl] * dg["tau"]
        resid = rb_mesma["tau"] - ra["tau"] - via
        if not abs(resid) <= 1e-8 * max(1.0, abs(rb_mesma["tau"])):
            raise FalhaValidacao(f"decomposicao nao fecha em {meta}: residuo {resid}")
        if extras is not None:
            extras.setdefault("decomposicao_residuos", []).append(float(resid))
        for var, tau, ep, res_ in (("total (= S-b na amostra de S-a)", rb_mesma["tau"], rb_mesma["ep"], rb_mesma),
                                   ("via oferta (soma gamma x salto do controle)", via, np.nan, None),
                                   ("preenchimento dado as vagas (= S-a)", ra["tau"], ra["ep"], ra)):
            ln = nova_linha(meta, "decomposicao", var, "identidade de Frisch-Waugh-Lovell com a mesma amostra e pesos",
                            h_mil=H, unidade=un, controle=ctl, forma=forma)
            if res_ is not None:
                preencher(ln, res_)
                ln["coef_controle"] = np.nan
                ln["entra_holm"] = False
            else:
                ln.update({"tau": tau, "media_abaixo": ra["media_abaixo"], "n_abaixo": ra["n_abaixo"],
                           "n_acima": ra["n_acima"], "n_obs": ra["n_obs"]})
                if np.isfinite(ra["media_abaixo"]) and ra["media_abaixo"] != 0:
                    ln["efeito_relativo_media_abaixo"] = tau / ra["media_abaixo"]
                ln["nota"] = ("soma algebrica: total - S-a; sem EP proprio (a incerteza esta nas linhas S-b e S-c); "
                              f"residuo da identidade = {resid:.3g}")
            linhas.append(ln)
    # S-d: Poisson local com log(controle) como covariável e como offset.
    with np.errstate(divide="ignore", invalid="ignore"):
        logv = np.where(v > 0, np.log(np.where(v > 0, v, 1.0)), np.nan)
    logv = np.where(np.isfinite(v), logv, np.nan)
    rp_cov = poisson(a, y, H, covariavel=logv)
    lpc = preencher(nova_linha(meta, "S-d", "log_controle_covariavel",
                               "Poisson local (IRLS), kernel triangular, log(controle) como covariavel (elasticidade "
                               "livre)" + ("; CR1 por municipio" if a.empilhada else "; EP HC1"), h_mil=H,
                               unidade=E6.UNIDADE_LOG, controle=ctl, forma=forma), rp_cov)
    if rp_cov.get("gamma_log_controle") and len(rp_cov["gamma_log_controle"]) == 1:
        lpc["coef_controle"] = next(iter(rp_cov["gamma_log_controle"].values()))
    elif rp_cov.get("gamma_log_controle"):
        lpc["nota"] = _juntar(lpc["nota"], "elasticidade por grupo: " + json.dumps(
            {g: round(x, 6) for g, x in rp_cov["gamma_log_controle"].items()}))
    linhas.append(lpc)
    rp_off = poisson(a, y, H, offset=logv)
    if not a.empilhada:
        conferir_poisson_lib(a, y, logv, rp_off)
    linhas.append(preencher(nova_linha(meta, "S-d", "log_controle_offset",
                                       "Poisson local (IRLS), kernel triangular, offset log(controle) (taxa por vaga)"
                                       + ("; CR1 por municipio" if a.empilhada else "; EP HC1"), h_mil=H,
                                       unidade=E6.UNIDADE_LOG, controle=ctl, forma=forma), rp_off))
    # S-e: fração ponderada pelo controle.
    with np.errstate(divide="ignore", invalid="ignore"):
        frac = np.where(np.isfinite(v) & (v > 0), y / np.where(v > 0, v, 1.0), np.nan)
    re_ = ajustar(a, frac, H, peso=np.where(np.isfinite(v), v, np.nan))
    linhas.append(preencher(nova_linha(meta, "S-e", "fracao_ponderada_pelo_controle",
                                       _est(a, f"y / {ctl}, peso = kernel x {ctl}"), h_mil=H,
                                       unidade="fracao (x100 = p.p.)", controle=ctl, forma=forma), re_))
    # S-f: inclinação do controle diferente de cada lado.
    rf = ajustar(a, y, H, v=v, lados=True)
    linhas.append(preencher(nova_linha(meta, "S-f", "controle_com_inclinacao_por_lado",
                                       _est(a, "controle com inclinacao diferente de cada lado, centrado na media da "
                                               "janela (salto no municipio com a media de vagas)"), h_mil=H,
                                       unidade=un, controle=ctl, forma=forma), rf))
    # S-g: IC honesto de S-a (y residualizado) e de S-b.
    for nome_esp, yy, residualizado, media in (("S-a", ytil, True, ra["media_abaixo"]), ("S-b", y, False, rb["media_abaixo"])):
        if yy is None:
            linhas.append(nao_executado(meta, "S-g", f"ic_honesto_{nome_esp}", "S-a sem estimativa: nada a residualizar",
                                        unidade=un, controle=ctl if residualizado else "", forma=forma if residualizado else ""))
            continue
        try:
            base = honesto(a, yy)
            M0 = base["M"]
            for f in FATORES_M:
                hon = base if f == 1.0 else honesto(a, yy, M=f * M0)
                ln = linha_honesta(meta, hon, fator=f, pos=False, unidade=un, controle=ctl if residualizado else "",
                                   forma=forma if residualizado else "", esp="S-g", media=media,
                                   residualizado=residualizado)
                ln["variante"] = f"{nome_esp}: {ln['variante']}"
                linhas.append(ln)
                if f == 1.0:
                    alvo = la if residualizado else lb
                    alvo["ic_honesto_inf"], alvo["ic_honesto_sup"] = ln["ic95_inf"], ln["ic95_sup"]
                    alvo["M"], alvo["fator_M"] = ln["M"], 1.0
            hp = honesto(a, yy, pos_resultado=True)
            ln = linha_honesta(meta, hp, fator=1.0, pos=True, unidade=un, controle=ctl if residualizado else "",
                               forma=forma if residualizado else "", esp="S-g", media=media, residualizado=residualizado)
            ln["variante"] = f"{nome_esp}: {ln['variante']}"
            linhas.append(ln)
        except ValueError as erro:
            linhas.append(nao_executado(meta, "S-g", f"{nome_esp}: ic_honesto", f"IC honesto nao calculado: {erro}",
                                        unidade=un))
    # S-j: donut.
    xm = L.normalizar_s_mil(a.s) - a.c
    fora = np.abs(xm) < DONUT_MIL
    sub = a.subconjunto(~fora)
    for nome_esp, vv in (("S-a", sub.col(cp["col"])), ("S-b", None)):
        ln = preencher(nova_linha(meta, "S-j", f"donut ({nome_esp})",
                                  _est(a, ("controle linear comum; " if vv is not None else "")
                                       + "exclui |IVS - corte| < 0,002"), h_mil=H, unidade=un,
                                  controle=ctl if vv is not None else "", forma=forma if vv is not None else ""),
                       ajustar(sub, sub.col(spec["col"]), H, v=vv))
        ln["nota"] = _juntar(f"{int(fora.sum())} linhas excluidas (|IVS - corte| < 0,002)", ln["nota"])
        linhas.append(ln)
    # S-h: local randomization (só um corte). No empilhado, linha NAO_EXECUTADO com o motivo (auditoria 20).
    if not a.empilhada and w_lr is not None:
        linhas.extend(local_randomization(meta, a, y, v, w_lr, un, ctl, forma))
    elif a.empilhada:
        linhas.append(nao_executado(meta, "S-h", "empilhado", MOTIVO_SH_EMPILHADO, unidade=un))
    return linhas


MOTIVO_SH_EMPILHADO = ("local randomization empilhada nao executada: a janela do E5 e o p de Fisher sao por "
                       "populacao x corte e a rdd_lib nao tem versao empilhada; ver as linhas S-h por ciclo x corte")
MOTIVO_SI_EMPILHADO = ("cortes placebo com ciclos empilhados nao executados: o protocolo os pede como no E9, por "
                       "ciclo; ver as linhas S-i de cada ciclo")


def local_randomization(meta: dict, a: Amostra, y: np.ndarray, v: np.ndarray, lr: dict, un: str, ctl: str,
                        forma: str) -> list[dict]:
    """S-h: Fisher na janela do E5 (E6_lr_selecao_janela.csv); sem controle e com o ajuste de Rosenbaum (2002)."""
    corte = a.corte_unico
    w = lr.get("w")
    est = "local randomization: diferenca de medias na janela (c-w, c+w], p de Fisher (10.000 permutacoes)"
    if w is None:
        return [nao_executado(meta, "S-h", var, lr.get("motivo", "nenhuma janela passou no balanco (regra do E5)"),
                              unidade=un, controle=c_, forma=f_)
                for var, c_, f_ in (("sem_controle", "", ""), ("residuo_rosenbaum", ctl, forma))]
    semente = (L.SEMENTE, lr["id_pop"], int(corte), int(w))
    x = L.normalizar_s_mil(a.s) - corte
    dentro = (x > -w) & (x <= w)
    linhas = []
    # Ajuste de Rosenbaum: resíduo de MQO de y em (1, v) na janela, sem o tratamento (válido sob o nulo exato).
    ok = dentro & np.isfinite(y) & np.isfinite(v)
    e = np.full(len(y), np.nan)
    nota_r = ""
    if ok.sum() >= 3 and np.unique(v[ok]).size >= 2:
        X = np.column_stack([np.ones(int(ok.sum())), v[ok]])
        b = np.linalg.lstsq(X, y[ok], rcond=None)[0]
        e[ok] = y[ok] - X @ b
        nota_r = f"residuo de MQO de y em (1, {ctl}) na janela, sem o tratamento; coef = {b[1]:.6g}"
    else:
        nota_r = "controle sem variacao na janela: residuo indefinido"
    for var, yy, c_, f_, nota in (("sem_controle", y, "", "", ""), ("residuo_rosenbaum", e, ctl, forma, nota_r)):
        r = L.rl_janela(a.s, yy, corte, int(w), semente=semente)
        ln = nova_linha(meta, "S-h", var, est + ("; ajuste de covariavel de Rosenbaum (2002)" if c_ else ""),
                        h_mil=w, unidade=un, controle=c_, forma=f_)
        ln["w_lr"] = w / 1000.0
        ln.update({"tau": r["tau"], "p_valor": r["p_valor"], "ep": r["ep_permutacao"], "n_abaixo": r["n_abaixo"],
                   "n_acima": r["n_acima"], "n_obs": (r["n_abaixo"] or 0) + (r["n_acima"] or 0)})
        sem_y = int((dentro & ~np.isfinite(yy)).sum())
        ln["n_descartadas_y_ausente"] = sem_y
        ab = dentro & np.isfinite(y) & (x <= 0)
        ln["media_abaixo"] = float(np.mean(y[ab])) if ab.any() else np.nan
        if np.isfinite(ln["ep"]):
            ln["mde"] = FATOR_MDE * ln["ep"]
        if np.isfinite(ln["media_abaixo"]) and ln["media_abaixo"] != 0 and np.isfinite(ln["tau"]):
            ln["efeito_relativo_media_abaixo"] = ln["tau"] / ln["media_abaixo"]
        ln["nota"] = _juntar("ep = DP da distribuicao de permutacao sob o nulo exato; IC por inversao nao calculado "
                             "(outcome fora de [0, 1])", f"semente {list(semente)}", f"janela {lr.get('origem', '')}",
                             f"{sem_y} municipios da janela sem outcome (fora)" if sem_y else "", nota, r.get("nota", ""))
        if not np.isfinite(ln["tau"]):
            ln["status"] = "SEM_ESTIMATIVA"
        linhas.append(ln)
    return linhas


def especificacoes_oferta(oid: str, meta: dict, a: Amostra, *, completo: bool, w_lr: dict | None = None) -> list[dict]:
    """S-c: a variável de oferta como outcome (primeiro passo da decomposição)."""
    o = OFERTA[oid]
    y = a.col(o["col"])
    un = o["unidade"]
    linhas = [preencher(nova_linha(meta, "S-c", "principal", _est(a, "oferta como outcome"), h_mil=H, unidade=un),
                        ajustar(a, y, H))]
    principal = linhas[0]
    for h in H_SENS:
        linhas.append(preencher(nova_linha(meta, "S-c", f"h={h / 1000:.3f}", _est(a, "oferta como outcome"), h_mil=h,
                                           unidade=un), ajustar(a, y, h)))
    if not completo:
        return linhas
    try:
        base = honesto(a, y)
        for f in FATORES_M:
            hon = base if f == 1.0 else honesto(a, y, M=f * base["M"])
            ln = linha_honesta(meta, hon, fator=f, pos=False, unidade=un, controle="", forma="", esp="S-c",
                               media=principal["media_abaixo"], residualizado=False)
            linhas.append(ln)
            if f == 1.0:
                principal["ic_honesto_inf"], principal["ic_honesto_sup"] = ln["ic95_inf"], ln["ic95_sup"]
                principal["M"], principal["fator_M"] = ln["M"], 1.0
        linhas.append(linha_honesta(meta, honesto(a, y, pos_resultado=True), fator=1.0, pos=True, unidade=un,
                                    controle="", forma="", esp="S-c", media=principal["media_abaixo"],
                                    residualizado=False))
    except ValueError as erro:
        linhas.append(nao_executado(meta, "S-c", "ic_honesto", f"IC honesto nao calculado: {erro}", unidade=un))
    xm = L.normalizar_s_mil(a.s) - a.c
    fora = np.abs(xm) < DONUT_MIL
    sub = a.subconjunto(~fora)
    ln = preencher(nova_linha(meta, "S-c", "donut", _est(a, "oferta como outcome; exclui |IVS - corte| < 0,002"),
                              h_mil=H, unidade=un), ajustar(sub, sub.col(o["col"]), H))
    ln["nota"] = _juntar(f"{int(fora.sum())} linhas excluidas", ln["nota"])
    linhas.append(ln)
    if not a.empilhada and w_lr is not None:
        lr = local_randomization(meta, a, y, np.full(len(y), np.nan), w_lr, un, "", "")
        lr = [l for l in lr if l["variante"] == "sem_controle"]
        for l in lr:
            l["especificacao"], l["variante"] = "S-c", "local_randomization"
        linhas.extend(lr)
    return linhas


# ---------------------------------------------------------------------------
# S-i: cortes placebo (um ciclo)
# ---------------------------------------------------------------------------

SEGMENTOS = {"abaixo_de_0,300": (-math.inf, 300), "entre_0,300_e_0,400": (300, 400), "acima_de_0,400": (400, math.inf)}


def _segmento(c: float) -> str:
    for nome, (lo, hi) in SEGMENTOS.items():
        if lo < c <= hi if math.isfinite(lo) else c <= hi:
            return nome
    raise ValueError(c)


def placebos(spec: dict, meta_base: dict, d: pd.DataFrame, ctrl: dict) -> tuple[list[dict], list[dict]]:
    """Cortes falsos nas médias de IVS de cada segmento de bolsa e na grade do E9; S-a e S-b; só o segmento do corte."""
    cp = ctrl["principal"][spec["controle"]]
    un = spec["unidade"]
    s = L.normalizar_s_mil(d["s_mil"].to_numpy(dtype=float))
    alvos = []
    for nome, (lo, hi) in SEGMENTOS.items():
        m = (s > lo) & (s <= hi)
        if m.any():
            alvos.append((f"media_do_segmento_{nome}", int(round(float(np.mean(s[m])))), nome))
    for c in PLACEBOS_MIL:
        alvos.append(("grade_E9", c, _segmento(c)))
    linhas, ts = [], []
    for variante, cpl, seg in alvos:
        lo, hi = SEGMENTOS[seg]
        m = (s > lo) & (s <= hi)
        dd = d[m].copy()
        dd["corte_mil"] = cpl
        dd["grupo"] = str(cpl)
        a = Amostra(dd, empilhada=False)
        meta = {**meta_base, "corte": "placebo"}
        for nome_esp, vv in (("S-a", a.col(cp["col"])), ("S-b", None)):
            r = ajustar(a, a.col(spec["col"]), H, v=vv)
            ln = preencher(nova_linha(meta, "S-i", f"{variante} ({nome_esp})",
                                      _est(a, ("controle linear comum; " if vv is not None else "")
                                           + f"corte falso; so municipios do segmento {seg}"), h_mil=H, unidade=un,
                                      controle=cp["col"] if vv is not None else "",
                                      forma=cp["id"] if vv is not None else ""), r)
            ln["corte_placebo"] = cpl / 1000.0
            linhas.append(ln)
            if variante == "grade_E9":
                ts.append({"spec": nome_esp, "corte_placebo": cpl,
                           "t": ln["tau"] / ln["ep"] if np.isfinite(ln["ep"]) and ln["ep"] > 0 else np.nan})
    return linhas, ts


# ---------------------------------------------------------------------------
# Pipeline (puro: recebe dados, devolve linhas)
# ---------------------------------------------------------------------------

def _fmt_ciclo(ks) -> str:
    return "+".join(str(k) for k in ks) if isinstance(ks, (list, tuple)) else str(ks)


def preparar_controles(controle_principal: str) -> dict:
    alt = "VI" if controle_principal == "VIC" else "VIC"
    return {"principal": {"vagas_oferecidas": {"id": controle_principal, "col": OFERTA[controle_principal]["col"]},
                          "n_celulas": {"id": "NC", "col": "n_celulas"}},
            "sensibilidade": {"vagas_oferecidas": {"id": alt, "col": OFERTA[alt]["col"]}}}


def _motivo_ausente(d: pd.DataFrame, col: str) -> str:
    motivos = set()
    for txt in d.get("motivos_ausencia", pd.Series(dtype=object)).dropna():
        try:
            m = json.loads(txt)
        except (TypeError, ValueError):
            continue
        if col in m:
            motivos.add(m[col])
    return "; ".join(sorted(motivos)) or "outcome ausente no ciclo"


def estimar_tudo(V: dict[int, pd.DataFrame], U: pd.DataFrame | None, *, controle_principal: str,
                 lr: dict, log=print) -> tuple[pd.DataFrame, dict]:
    """Todas as linhas da família N. `V[k]`: co_ibge, s_mil e colunas da tarefa B (+ vagas_imediatas_mais_cr).

    `lr[(pop, corte)]` = {"w": milésimos ou None, "id_pop", "origem", "motivo"}. `U`: população secundária.
    """
    ctrl = preparar_controles(controle_principal)
    linhas: list[dict] = []
    extras: dict = {"placebo_t": {}, "decomposicao_residuos": []}
    for spec in CATALOGO_N:
        meta_o = {"outcome_id": spec["id"], "outcome": spec["col"], "descricao_outcome": spec["desc"]}
        ks = [k for k in spec["ciclos"] if k in V]
        for k in sorted(V):
            if k not in spec["ciclos"] or V[k][spec["col"]].isna().all():
                motivo = _motivo_ausente(V[k], spec["col"]) if spec["col"] in V[k] else "coluna ausente"
                for c in [ROTULO_CORTE[x] for x in CORTES] + [EMPILHADO]:
                    linhas.append(nao_executado({**meta_o, "populacao": f"V{k}", "ciclo": str(k), "corte": c}, "S-a",
                                                "principal", f"outcome nao definido no ciclo {k}: {motivo}",
                                                unidade=spec["unidade"]))
                ks = [x for x in ks if x != k]
        for k in ks:
            d = V[k]
            meta = {**meta_o, "populacao": f"V{k}", "ciclo": str(k)}
            for c in CORTES:
                a = montar_amostra([(d, c, str(c))], empilhada=False)
                linhas.extend(especificacoes_n(spec, {**meta, "corte": ROTULO_CORTE[c]}, a, ctrl,
                                               w_lr=lr.get((f"V{k}", c)), extras=extras))
            a = montar_amostra([(d, c, str(c)) for c in CORTES], empilhada=True)
            linhas.extend(especificacoes_n(spec, {**meta, "corte": EMPILHADO}, a, ctrl, extras=extras))
            pl, ts = placebos(spec, meta, d, ctrl)
            linhas.extend(pl)
            extras["placebo_t"][(spec["id"], k)] = ts
        if len(ks) >= 2:
            meta = {**meta_o, "populacao": "+".join(f"V{k}" for k in ks), "ciclo": _fmt_ciclo(ks),
                    "descricao_outcome": spec["desc"] + " (ciclos empilhados; interceptos por ciclo = EF de ciclo)"}
            for c in CORTES:
                a = montar_amostra([(V[k], c, f"c{k}") for k in ks], empilhada=True)
                linhas.extend(especificacoes_n(spec, {**meta, "corte": ROTULO_CORTE[c]}, a, ctrl, extras=extras))
            a = montar_amostra([(V[k], c, f"c{k}_{c}") for k in ks for c in CORTES], empilhada=True)
            linhas.extend(especificacoes_n(spec, {**meta, "corte": EMPILHADO}, a, ctrl, extras=extras, holm=True))
            linhas.append(nao_executado({**meta, "corte": "placebo"}, "S-i", "ciclos_empilhados", MOTIVO_SI_EMPILHADO,
                                        unidade=spec["unidade"]))
        log(f"  {spec['id']}: {len(linhas)} linhas acumuladas")
    # S-c em V: as variáveis de oferta.
    for oid in OFERTA:
        meta_o = {"outcome_id": oid, "outcome": OFERTA[oid]["col"], "descricao_outcome": OFERTA[oid]["desc"]}
        ks = sorted(V)
        for k in ks:
            meta = {**meta_o, "populacao": f"V{k}", "ciclo": str(k)}
            for c in CORTES:
                a = montar_amostra([(V[k], c, str(c))], empilhada=False)
                linhas.extend(especificacoes_oferta(oid, {**meta, "corte": ROTULO_CORTE[c]}, a, completo=True,
                                                    w_lr=lr.get((f"V{k}", c))))
            a = montar_amostra([(V[k], c, str(c)) for c in CORTES], empilhada=True)
            linhas.extend(especificacoes_oferta(oid, {**meta, "corte": EMPILHADO}, a, completo=True))
        meta = {**meta_o, "populacao": "+".join(f"V{k}" for k in ks), "ciclo": _fmt_ciclo(ks)}
        for c in CORTES:
            a = montar_amostra([(V[k], c, f"c{k}") for k in ks], empilhada=True)
            linhas.extend(especificacoes_oferta(oid, {**meta, "corte": ROTULO_CORTE[c]}, a, completo=True))
        a = montar_amostra([(V[k], c, f"c{k}_{c}") for k in ks for c in CORTES], empilhada=True)
        linhas.extend(especificacoes_oferta(oid, {**meta, "corte": EMPILHADO}, a, completo=True))
    log(f"  S-c em V: {len(linhas)} linhas acumuladas")
    # População secundária U: N sem controle (efeito total) e S-c, zero fora do quadro.
    if U is not None:
        linhas.extend(estimar_u(U, V))
        log(f"  U: {len(linhas)} linhas acumuladas")
    est = pd.DataFrame(linhas)[COLUNAS]
    est = aplicar_holm(est)
    return est, extras


def colunas_u(U: pd.DataFrame, V: dict[int, pd.DataFrame]) -> pd.DataFrame:
    """N1–N4 e oferta em U: valor de V_k no município do quadro; zero estrutural fora do quadro; ausente fica ausente."""
    u = U.copy()
    for k, d in V.items():
        idx = d.set_index("co_ibge")
        no_quadro = u["co_ibge"].isin(idx.index)
        for spec in CATALOGO_N:
            col = spec["col"]
            if spec["id"] == "N4":
                fonte = f"n_ativos_pmme_c{k}"
                u[f"{col}_c{k}"] = u[fonte].astype(float) if fonte in u.columns else np.nan
                continue
            vals = u["co_ibge"].map(idx[col]).astype(float)
            u[f"{col}_c{k}"] = np.where(no_quadro, vals, 0.0)
        for oid, o in OFERTA.items():
            fonte = {"VIC": None, "VI": f"vagas_imediatas_c{k}", "NC": f"n_celulas_c{k}"}[oid]
            if oid == "VIC":
                u[f"{o['col']}_c{k}"] = u[f"vagas_imediatas_c{k}"].astype(float) + u[f"vagas_cr_c{k}"].astype(float)
            else:
                u[f"{o['col']}_c{k}"] = u[fonte].astype(float)
    return u


def estimar_u(U: pd.DataFrame, V: dict[int, pd.DataFrame]) -> list[dict]:
    u = colunas_u(U, V)
    linhas = []
    itens = [(s["id"], s["col"], s["desc"], s["unidade"], s["ciclos"], "S-b") for s in CATALOGO_N] + [
        (oid, o["col"], o["desc"], o["unidade"], tuple(sorted(V)), "S-c") for oid, o in OFERTA.items()]
    for oid, col, desc, un, ciclos, esp in itens:
        ks = [k for k in ciclos if k in V and u[f"{col}_c{k}"].notna().any()]
        partes = {}
        for k in ks:
            d = u[["co_ibge", "s_mil"]].copy()
            d["y"] = u[f"{col}_c{k}"].to_numpy(dtype=float)
            partes[k] = d
            meta = {"outcome_id": oid, "outcome": f"{col}_c{k}", "populacao": "U", "ciclo": str(k),
                    "descricao_outcome": desc + " (U: zero fora do quadro; efeito total)"}
            for c in CORTES:
                linhas.extend(_linhas_u(meta | {"corte": ROTULO_CORTE[c]},
                                        montar_amostra([(d, c, str(c))], empilhada=False), esp, un))
            linhas.extend(_linhas_u(meta | {"corte": EMPILHADO},
                                    montar_amostra([(d, c, str(c)) for c in CORTES], empilhada=True), esp, un))
        if len(ks) >= 2:
            meta = {"outcome_id": oid, "outcome": col, "populacao": "U", "ciclo": _fmt_ciclo(ks),
                    "descricao_outcome": desc + " (U, ciclos empilhados: interceptos por ciclo, CR1 por municipio)"}
            for c in CORTES:
                linhas.extend(_linhas_u(meta | {"corte": ROTULO_CORTE[c]},
                                        montar_amostra([(partes[k], c, f"c{k}") for k in ks], empilhada=True), esp, un))
            linhas.extend(_linhas_u(meta | {"corte": EMPILHADO},
                                    montar_amostra([(partes[k], c, f"c{k}_{c}") for k in ks for c in CORTES],
                                                   empilhada=True), esp, un))
    return linhas


def _linhas_u(meta: dict, a: Amostra, esp: str, un: str) -> list[dict]:
    y = a.col("y")
    out = [preencher(nova_linha(meta, esp, "principal", _est(a, "sem controle; U (zero fora do quadro)"), h_mil=H,
                                unidade=un), ajustar(a, y, H))]
    for h in H_SENS:
        out.append(preencher(nova_linha(meta, esp, f"h={h / 1000:.3f}", _est(a, "sem controle; U"), h_mil=h,
                                        unidade=un), ajustar(a, y, h)))
    return out


def aplicar_holm(est: pd.DataFrame) -> pd.DataFrame:
    est = est.copy()
    est["entra_holm"] = est["entra_holm"].astype(bool)
    est["p_holm"] = np.nan
    m = est["entra_holm"]
    if m.any():
        est.loc[m, "p_holm"] = L.holm(est.loc[m, "p_valor"].to_numpy(dtype=float))
    return est


def resumo_placebos(est: pd.DataFrame, placebo_t: dict) -> list[dict]:
    """Por outcome x ciclo x especificação: fração de |t| > 1,96 na grade e p por posto contra cada corte real (E9)."""
    out = []
    for (oid, k), ts in placebo_t.items():
        df = pd.DataFrame(ts)
        for esp in ("S-a", "S-b"):
            tt = df.loc[df["spec"] == esp, "t"].to_numpy(dtype=float)
            tt = tt[np.isfinite(tt)]
            for c in CORTES:
                r = est[(est["outcome_id"] == oid) & (est["populacao"] == f"V{k}") & (est["corte"] == ROTULO_CORTE[c])
                        & (est["especificacao"] == esp) & (est["variante"] == "principal")]
                t_real = float(r["tau"].iloc[0] / r["ep"].iloc[0]) if len(r) and r["ep"].iloc[0] > 0 else np.nan
                out.append({"outcome_id": oid, "ciclo": str(k), "especificacao": esp, "corte": ROTULO_CORTE[c],
                            "n_placebos": int(tt.size), "fracao_abs_t_maior_1_96": float(np.mean(np.abs(tt) > L.Z_975))
                            if tt.size else np.nan, "abs_t_placebo_max": float(np.abs(tt).max()) if tt.size else np.nan,
                            "t_real": t_real,
                            "n_abs_t_placebo_maior_ou_igual_ao_real": int(np.sum(np.abs(tt) >= abs(t_real)))
                            if np.isfinite(t_real) else None,
                            "p_posto": float((1 + np.sum(np.abs(tt) >= abs(t_real))) / (1 + tt.size))
                            if np.isfinite(t_real) else np.nan})
    return out


# ---------------------------------------------------------------------------
# Conferência contra o E6 (S-e de N2 e N3 = F1.3 e F1.4 ponderados por células)
# ---------------------------------------------------------------------------

def conferir_e6(est: pd.DataFrame, e6: pd.DataFrame, tol: float = 1e-10) -> dict:
    mapa = {"N2": "F1.3", "N3": "F1.4"}
    maior, n = 0.0, 0
    for oid, fid in mapa.items():
        ref = e6[(e6["outcome_id"] == fid) & (e6["especificacao"] == "ponderado_celulas")]
        for r in ref.to_dict("records"):
            x = est[(est["outcome_id"] == oid) & (est["especificacao"] == "S-e") & (est["populacao"] == r["populacao"])
                    & (est["corte"] == str(r["corte"]))]
            if len(x) != 1:
                raise FalhaValidacao(f"S-e de {oid} sem linha unica para {r['populacao']} {r['corte']}")
            x = x.iloc[0]
            for c in ("tau", "ep", "p_valor"):
                maior = max(maior, abs(float(x[c]) - float(r[c])))
            n += 1
    if maior > tol:
        raise FalhaValidacao(f"S-e de N2/N3 nao reproduz o ponderado do E6: max |dif| = {maior}")
    return {"linhas_conferidas": n, "max_abs_dif": maior, "tolerancia": tol, "reproduz": True,
            "o_que": "S-e de N2 (N3) = F1.3 (F1.4) ponderado por celulas do E6, em cada ciclo, corte e empilhamento"}


# ---------------------------------------------------------------------------
# Leitura
# ---------------------------------------------------------------------------

def ler_lr(pops: dict) -> dict:
    """Janela de local randomization do E6 (regra do E5, só covariáveis) para V1–V3."""
    tab = pd.read_csv(E6_LR, dtype={"corte": str})
    lr = {}
    for k in (1, 2, 3):
        pop = f"V{k}"
        for c in CORTES:
            sel = tab[(tab["populacao"] == pop) & (tab["corte"] == ROTULO_CORTE[c]) & tab["selecionada"].astype(bool)]
            if len(sel) > 1:
                raise FalhaValidacao(f"{pop} {c}: mais de uma janela LR selecionada")
            w = int(round(float(sel.iloc[0]["w"]) * 1000)) if len(sel) else None
            lr[(pop, c)] = {"w": w, "id_pop": ID_SEMENTE_POP[pop], "origem": f"{rotulo(E6_LR)} ({pop})",
                            "motivo": "nenhuma janela candidata passou no balanco (regra do E5, E6_lr_selecao_janela.csv)"}
    return lr


def carregar(rv: pd.DataFrame, pops: dict) -> tuple[dict, pd.DataFrame, dict]:
    vm = pd.read_parquet(ARQ_VM)
    vm["vagas_imediatas_mais_cr"] = vm["vagas_imediatas"].astype(float) + vm["vagas_cr"].astype(float)
    V, info = {}, {}
    for k in sorted(vm["ciclo"].unique()):
        nome = f"V{int(k)}"
        d = vm[vm["ciclo"] == k]
        V[int(k)] = d.merge(pops[nome], on="co_ibge", how="inner", validate="one_to_one").reset_index(drop=True)
        info[nome] = {"municipios_no_quadro": int(len(d)), "municipios_com_ivs_oficial": int(len(V[int(k)])),
                      "municipios_sem_ivs_fora": int(len(d) - len(V[int(k)])),
                      "municipios_com_vagas_oferecidas_ausentes": {
                          c: int(V[int(k)][c].isna().sum()) for c in ("vagas_imediatas_mais_cr", "vagas_imediatas",
                                                                       "n_celulas")},
                      "municipios_com_outcome_ausente": {s["col"]: int(V[int(k)][s["col"]].isna().sum())
                                                         for s in CATALOGO_N}}
    u = pd.read_parquet(ARQ_U).merge(pops["U"], on="co_ibge", how="inner", validate="one_to_one")
    for k, d in V.items():
        idx = d.set_index("co_ibge")
        uu = u.set_index("co_ibge").reindex(idx.index)
        dif = {c: int((uu[f"{c}_c{k}"] != idx[c]).sum()) for c in ("n_celulas", "vagas_imediatas", "vagas_cr")}
        if f"n_ativos_pmme_c{k}" in uu:
            dif["n_ativos"] = int((uu[f"n_ativos_pmme_c{k}"] != idx["n_ativos_ciclo"]).sum())
        if any(dif.values()):
            raise FalhaValidacao(f"V{k} e U divergem nas colunas de oferta/ativos: {dif}")
        info[f"V{k}"]["U_igual_a_V_nas_colunas_de_oferta_e_ativos"] = True
    return V, u, info


# ---------------------------------------------------------------------------
# Figuras
# ---------------------------------------------------------------------------

COR_DENTRO = "#2a78d6"
COR_FORA = "#a3a29c"
COR_RETA = "#1d4f91"
COR_BANDA = "#2a78d6"
COR_SALTO = "#eb6834"
TINTA = "#0b0b0b"
TINTA_2 = "#52514e"
SUPERFICIE = "#fcfcfb"


def _faixas(x_mil: np.ndarray) -> np.ndarray:
    """Índice de faixa de largura 0,010 em x = IVS - corte: abaixo, x em (-10(k+1), -10k]; acima, [10k, 10(k+1)).

    Cada faixa fica inteira dentro ou inteira fora da janela |x| < 0,050 (os pontos x = -0,050 e +0,050, de peso
    zero, caem na primeira faixa de fora).
    """
    return np.where(x_mil <= 0, -(np.floor(-x_mil / LARGURA_FAIXA_FIG) + 1), np.floor(x_mil / LARGURA_FAIXA_FIG))


def _linha_prevista(fit: dict, nomes_coef: list[tuple[str, float]], V: np.ndarray) -> tuple[float, float]:
    """Valor e EP de sum_j c_j beta_j (nomes ausentes do ajuste contam zero)."""
    idx = [fit["nomes"].index(n) for n, _ in nomes_coef if n in fit["nomes"]]
    cvec = np.array([c for n, c in nomes_coef if n in fit["nomes"]])
    b = fit["beta"][idx]
    return float(cvec @ b), float(math.sqrt(max(cvec @ V[np.ix_(idx, idx)] @ cvec, 0.0)))


def curva_um_corte(r: dict, corte: int) -> dict:
    fit = r["_detalhes"]["fit"]
    out = {}
    for lado, grade in (("abaixo", np.linspace(-H + 1, 0, 50)), ("acima", np.linspace(1e-9, H - 1, 50))):
        t = 1.0 if lado == "acima" else 0.0
        pr, lo, hi = [], [], []
        for g in grade:
            x = g / 1000.0
            val, ep = _linha_prevista(fit, [("const", 1.0), ("x", x), ("T", t), ("T_x", t * x)], fit["V"])
            pr.append(val)
            lo.append(val - L.Z_975 * ep)
            hi.append(val + L.Z_975 * ep)
        out[lado] = (corte + grade, np.array(pr), np.array(lo), np.array(hi))
    return out


def curva_empilhada(r: dict, a: Amostra) -> tuple[dict, np.ndarray, dict]:
    """Reta média entre os grupos (pesos = participação do grupo no peso de kernel); salto no corte = tau.

    Pontos da janela = reta média em r_i + resíduo da regressão empilhada (gráfico de resíduos parciais).
    """
    d = r["_detalhes"]
    fit, usa, w = d["fit"], d["usa"], d["w"]
    grupos = sorted(np.unique(a.g).tolist())
    peso = {gl: float(np.sum(w[usa & (a.g == gl)])) for gl in grupos}
    tot = sum(peso.values())
    peso = {g: v / tot for g, v in peso.items()}

    def coef(x, t):
        cs = [("T", t)]
        for gl in grupos:
            cs += [(f"const[{gl}]", peso[gl]), (f"x[{gl}]", peso[gl] * x), (f"T_x[{gl}]", peso[gl] * t * x)]
        return cs

    out = {}
    for lado, grade in (("abaixo", np.linspace(-H + 1, 0, 50)), ("acima", np.linspace(1e-9, H - 1, 50))):
        t = 1.0 if lado == "acima" else 0.0
        pr, lo, hi = [], [], []
        for g in grade:
            val, ep = _linha_prevista(fit, coef(g / 1000.0, t), fit["V"])
            pr.append(val)
            lo.append(val - L.Z_975 * ep)
            hi.append(val + L.Z_975 * ep)
        out[lado] = (grade, np.array(pr), np.array(lo), np.array(hi))
    xu = d["x"][usa]
    tu = d["t"][usa]
    media_linha = np.array([_linha_prevista(fit, coef(xx, tt), fit["V"])[0] for xx, tt in zip(xu, tu)])
    y_ponto = np.full(len(a.s), np.nan)
    y_ponto[usa] = media_linha + fit["residuos"]
    return out, y_ponto, peso


def _fmt(v, casas=2, sinal=True) -> str:
    if v is None or not np.isfinite(v):
        return "—"
    return (f"{v:+.{casas}f}" if sinal else f"{v:.{casas}f}").replace("-", "−").replace(".", ",")


def _titulo_painel(r: dict) -> str:
    return (f"salto = {_fmt(r['tau'])} vagas  [IC 95%: {_fmt(r['ic95_inf'])}; {_fmt(r['ic95_sup'])}],"
            f"  p = {_fmt(r['p_valor'], 3, False)}")


def _area(n: int) -> float:
    """Área do ponto (pt²) crescente no número de municípios da faixa (a legenda mostra a escala)."""
    return 12.0 + 40.0 * math.sqrt(n)


def _fmt_eixo_x(v, _=None) -> str:
    txt = f"{v:.3f}"
    return (txt[:-1] if txt.endswith("0") else txt).replace(".", ",").replace("-", "−")


def desenhar(paineis: list[dict], titulo: str, ylabel: str, xlabel: str, legenda: str, caminho: Path, *,
             unidade_n: tuple[str, str] = ("município", "municípios"), rotulo_salto: bool = True) -> None:
    """Cada painel: x (IVS ou IVS - corte, em milésimos), y_ponto, dentro (bool), curva, corte, rótulo, título.

    `unidade_n` = (singular, plural) do que o tamanho do ponto conta (no empilhado, linhas município x ciclo).
    `rotulo_salto=False` omite o texto "salto" ao lado da seta (a legenda já explica a seta; auditoria 21: o
    texto cobria pontos perto do corte nas figuras da família K). O padrão mantém as figuras da família N.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch

    larg_painel = 6.0 if len(paineis) > 1 else 8.0
    esq, dir_, meio = 0.95, 0.25, 0.75
    ncol = 5 if len(paineis) > 1 else 4
    n_linhas_leg = math.ceil(9 / ncol)
    largura = esq + dir_ + larg_painel * len(paineis) + meio * (len(paineis) - 1)
    linhas_leg = []
    for par in legenda.split("\n"):
        linhas_leg.extend(textwrap.wrap(par, int(largura * 15.5)) or [""])
    # 0,30 pol. por linha da legenda: o marcador de 50 unidades é mais alto que o texto (auditoria 20: com 0,26 e a
    # altura do texto subestimada, a terceira linha da legenda do painel único encostava no texto "COMO LER").
    h_tit, h_plot, h_xlab, h_leg = 0.75, 3.9, 0.5, 0.30 * n_linhas_leg + 0.25
    # 7,4 pt com espaçamento 1,25 ocupa ~0,155 pol. por linha (0,125 subestimava a altura do texto: auditoria 20).
    h_txt = 0.155 * len(linhas_leg) + 0.2
    altura = h_tit + h_plot + h_xlab + h_leg + h_txt
    fig = plt.figure(figsize=(largura, altura), facecolor=SUPERFICIE)
    base = (h_txt + h_leg + h_xlab) / altura
    eixos = []
    for i, p in enumerate(paineis):
        ax = fig.add_axes([(esq + i * (larg_painel + meio)) / largura, base, larg_painel / largura, h_plot / altura])
        ax.set_facecolor(SUPERFICIE)
        eixos.append(ax)
        x, y, dentro, corte = p["x"], p["y"], p["dentro"], p["corte"]
        ok = np.isfinite(x) & np.isfinite(y)
        fx = _faixas(x[ok] - corte)
        for f in np.unique(fx):
            m = fx == f
            n = int(m.sum())
            dent = bool(dentro[ok][m].all())
            ax.scatter(np.mean(x[ok][m]) / 1000, np.mean(y[ok][m]), s=_area(n), color=COR_DENTRO if dent else COR_FORA,
                       edgecolor=SUPERFICIE, linewidth=1.2, zorder=3, alpha=0.95)
        cur = p["curva"]
        for lado in ("abaixo", "acima"):
            gx, pr, lo, hi = cur[lado]
            ax.fill_between(gx / 1000, lo, hi, color=COR_BANDA, alpha=0.16, linewidth=0, zorder=1)
            ax.plot(gx / 1000, pr, color=COR_RETA, linewidth=2, zorder=2)
        y0, y1 = cur["abaixo"][1][-1], cur["acima"][1][0]
        ax.axvline(corte / 1000, color=TINTA_2, linewidth=1, linestyle="--", zorder=0)
        ax.annotate("", xy=(corte / 1000, y1), xytext=(corte / 1000, y0),
                    arrowprops=dict(arrowstyle="-|>", color=COR_SALTO, linewidth=2.2, mutation_scale=12), zorder=4)
        if rotulo_salto:
            ax.text(corte / 1000, (y0 + y1) / 2, "  salto", color=COR_SALTO, fontsize=9, va="center", ha="left",
                    fontweight="bold", zorder=5,
                    bbox=dict(facecolor=SUPERFICIE, edgecolor="none", alpha=0.85, pad=0.6))
        ax.set_title(f"{p['rotulo']}\n{p['titulo']}", fontsize=9.5, color=TINTA)
        ax.set_xlabel(xlabel, fontsize=9, color=TINTA_2)
        ax.grid(alpha=0.25, linewidth=0.6)
        ax.tick_params(colors=TINTA_2, labelsize=8)
        ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(_fmt_eixo_x))
        ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",")))
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)
    eixos[0].set_ylabel(ylabel, fontsize=9, color=TINTA_2)
    handles = [
        Line2D([], [], marker="o", linestyle="", color=COR_DENTRO, markersize=8, label="média da faixa, dentro da janela"),
        Line2D([], [], marker="o", linestyle="", color=COR_FORA, markersize=8, label="média da faixa, fora da janela"),
        Line2D([], [], color=COR_RETA, linewidth=2, label="reta ajustada (separada de cada lado)"),
        Patch(color=COR_BANDA, alpha=0.16, label="IC 95% da reta"),
        Line2D([], [], color=COR_SALTO, linewidth=2.2, label="salto no corte = efeito estimado"),
        Line2D([], [], color=TINTA_2, linewidth=1, linestyle="--", label="corte"),
    ]
    tamanhos = [Line2D([], [], marker="o", linestyle="", color=COR_FORA, markersize=math.sqrt(_area(n)),
                       label=f"{n} {unidade_n[1] if n > 1 else unidade_n[0]}") for n in (1, 10, 50)]
    fig.legend(handles=handles + tamanhos, loc="center", ncol=ncol, fontsize=7.6,
               frameon=False, bbox_to_anchor=(0.5, (h_txt + h_leg / 2) / altura))
    fig.suptitle(titulo, fontsize=11, color=TINTA, y=1 - 0.18 / altura)
    fig.text(0.12 / largura, 0.1 / altura, "\n".join(linhas_leg), fontsize=7.4, color=TINTA_2, va="bottom", ha="left",
             linespacing=1.25, parse_math=False)
    fig.savefig(caminho, dpi=130, facecolor=SUPERFICIE)
    plt.close(fig)


def _limites_segmento(corte: int) -> tuple[float, float]:
    outros = [c for c in CORTES if c != corte]
    lo = max([c for c in outros if c < corte], default=-math.inf)
    hi = min([c for c in outros if c > corte], default=math.inf)
    return max(lo, corte - ALCANCE_FIG), min(hi, corte + ALCANCE_FIG)


LEGENDA_BASE = (
    "COMO LER. Cada ponto é a média do outcome entre os municípios de uma faixa de IVS de largura 0,010 (a posição "
    "horizontal é a média do IVS deles); o tamanho do ponto é o número de municípios da faixa. Azul: faixa dentro da "
    "janela usada na estimativa (IVS a menos de 0,050 do corte); cinza: fora da janela, só para contexto (não entra "
    "na conta). A reta é ajustada separadamente de cada lado do corte (local linear, kernel triangular, h = 0,050: "
    "municípios mais perto do corte pesam mais), e a faixa clara em volta é o IC 95% da reta. A linha tracejada é o "
    "corte; a seta laranja é o salto entre as duas retas no corte, que é o efeito estimado (lado com bolsa maior, à "
    "direita, menos lado com bolsa menor, à esquerda), com o valor e o IC 95% no título do painel. Em 0,300 a bolsa "
    "passa de R$ 10 mil para R$ 15 mil por mês; em 0,400, de R$ 15 mil para R$ 20 mil; outras regras federais mudam "
    "nos mesmos cortes, por isso o salto é o do pacote do corte. EMPIRICO.")
LEGENDA_CONTROLE = (
    "\nCOM CONTROLE: o eixo vertical é o número de vagas preenchidas ajustado às vagas oferecidas: de cada município "
    "tira-se gamma × (vagas oferecidas − média das vagas oferecidas na janela), com gamma estimado na janela pela "
    "mesma regressão (mesmo coeficiente dos dois lados). Lê-se como as vagas preenchidas de um município com o número "
    "médio de vagas oferecidas da janela. Se as próprias vagas oferecidas saltam no corte, este salto é condicional "
    "a uma variável possivelmente afetada pela faixa (ver S-c no doc 49).")
LEGENDA_EMPILHADO = (
    "\nEMPILHADO: o eixo horizontal é a distância ao corte (IVS − corte), juntando os ciclos 1 a 3 e os dois cortes. "
    "A reta é a média ponderada das retas de cada ciclo × corte da regressão empilhada (interceptos e inclinações "
    "próprios, salto comum, EP CR1 por município), e cada ponto é essa reta mais o resíduo médio dos municípios da "
    "faixa; só aparecem municípios dentro da janela. Aqui o tamanho do ponto conta linhas município × ciclo: o "
    "mesmo município entra uma vez em cada ciclo em que tem célula no quadro.")


def gerar_figuras(V: dict[int, pd.DataFrame], est: pd.DataFrame, ctrl_principal: str, dir_fig: Path) -> list[dict]:
    dir_fig.mkdir(parents=True, exist_ok=True)
    for antigo in dir_fig.glob("*.png"):
        antigo.unlink()
    spec = CATALOGO_N[0]
    ctl = OFERTA[ctrl_principal]["col"]
    feitas = []
    ylab = {False: "Vagas preenchidas na 1ª chamada (nº por município)",
            True: "Vagas preenchidas na 1ª chamada, ajustadas às\nvagas oferecidas (nº por município)"}
    for com in (False, True):
        sufixo = "com_controle" if com else "sem_controle"
        esp = "S-a" if com else "S-b"
        for k in (1, 2):
            d = V[k]
            paineis, meta_fig = [], []
            for c in CORTES:
                lo, hi = _limites_segmento(c)
                s = L.normalizar_s_mil(d["s_mil"].to_numpy(dtype=float))
                a = montar_amostra([(d, c, str(c))], empilhada=False)
                y = a.col(spec["col"])
                r = ajustar(a, y, H, v=a.col(ctl) if com else None)
                # Pontos com controle: y~ = y - gamma (v - v_barra). A reta é a da própria regressão S-a sem a parte
                # do controle (o controle centrado vale zero em v = v_barra), com o IC 95% da matriz HC1 de S-a.
                y_p = residualizar(y, r) if com else y
                mostra = (s > lo) & (s <= hi)
                paineis.append({"x": np.where(mostra, s, np.nan), "y": y_p, "dentro": np.abs(s - c) < H, "corte": c,
                                "curva": curva_um_corte(r, c), "rotulo": f"Ciclo {k}, corte {ROTULO_CORTE[c].replace('.', ',')}",
                                "titulo": _titulo_painel(r)})
                meta_fig.append({"ciclo": str(k), "corte": ROTULO_CORTE[c], "especificacao": esp, "tau": r["tau"],
                                 "ic95_inf": r["ic95_inf"], "ic95_sup": r["ic95_sup"], "p_valor": r["p_valor"]})
            nome = f"N1_{sufixo}_ciclo{k}.png"
            desenhar(paineis, f"N1 — vagas preenchidas na 1ª chamada, {'com' if com else 'sem'} controle pelas vagas "
                              f"oferecidas (V{k}, ciclo {k})", ylab[com], "IVS 2010 oficial do município",
                     LEGENDA_BASE + (LEGENDA_CONTROLE if com else ""), dir_fig / nome)
            feitas.append({"arquivo": rotulo(dir_fig / nome), "outcome_id": "N1", "populacao": f"V{k}", "paineis": meta_fig})
        # Empilhado: ciclos 1–3 e cortes.
        ks = sorted(V)
        a = montar_amostra([(V[k], c, f"c{k}_{c}") for k in ks for c in CORTES], empilhada=True)
        y = a.col(spec["col"])
        r = ajustar(a, y, H, v=a.col(ctl) if com else None)
        cur, y_p, pesos = curva_empilhada(r, a)
        x = L.normalizar_s_mil(a.s) - a.c
        dentro = np.isfinite(y_p)
        paineis = [{"x": np.where(dentro, x, np.nan), "y": y_p, "dentro": dentro, "corte": 0, "curva": cur,
                    "rotulo": f"Ciclos {_fmt_ciclo(ks).replace('+', ', ')} e cortes 0,300 e 0,400 empilhados",
                    "titulo": _titulo_painel(r)}]
        nome = f"N1_{sufixo}_empilhado.png"
        desenhar(paineis, f"N1 — vagas preenchidas na 1ª chamada, {'com' if com else 'sem'} controle, ciclos e cortes "
                          f"empilhados", ylab[com], "distância ao corte (IVS 2010 oficial − corte)",
                 LEGENDA_BASE + (LEGENDA_CONTROLE if com else "") + LEGENDA_EMPILHADO, dir_fig / nome,
                 unidade_n=("linha município × ciclo", "linhas município × ciclo"))
        feitas.append({"arquivo": rotulo(dir_fig / nome), "outcome_id": "N1", "populacao": "+".join(f"V{k}" for k in ks),
                       "paineis": [{"ciclo": _fmt_ciclo(ks), "corte": EMPILHADO, "especificacao": esp, "tau": r["tau"],
                                    "ic95_inf": r["ic95_inf"], "ic95_sup": r["ic95_sup"], "p_valor": r["p_valor"],
                                    "pesos_da_reta_media": pesos}]})
    return feitas


# ---------------------------------------------------------------------------
# Tabelas do doc 49 (geradas das saídas; nenhum número digitado)
# ---------------------------------------------------------------------------

_n, _p, _ic = E6._n, E6._p, E6._ic


def _fi(v) -> str:
    return "—" if v is None or (isinstance(v, float) and not math.isfinite(v)) or pd.isna(v) else str(int(v))


def _casas(un: str) -> tuple[int, bool, str]:
    if str(un).startswith("fracao"):
        return 1, True, " p.p."
    if str(un).startswith("log"):
        return 3, False, " (log)"
    return 2, False, ""


def _tab(sub: pd.DataFrame, cab: list[str], cols) -> str:
    out = ["| " + " | ".join(cab) + " |", "|" + "|".join("---" for _ in cab) + "|"]
    for r in sub.to_dict("records"):
        out.append("| " + " | ".join(f(r) for f in cols) + " |")
    return "\n".join(out)


def _tau(r):
    c, pp, u = _casas(r["unidade"])
    return f"{_n(r['tau'], c, pp)}{u}"


def _icr(r, a="ic95_inf", b="ic95_sup"):
    c, pp, _ = _casas(r["unidade"])
    return _ic(r[a], r[b], c, pp)


def _rel(r, col="efeito_relativo_media_abaixo"):
    v = r.get(col)
    return "—" if v is None or pd.isna(v) else _n(v, 1, pp=True) + " %"


def _corte(r):
    return str(r["corte"]).replace(".", ",")


def _nab(r):
    return f"{_fi(r['n_abaixo'])} / {_fi(r['n_acima'])}"


def gerar_tabelas_doc(est: pd.DataFrame, resumo: dict) -> dict[str, str]:
    t: dict[str, str] = {}
    vc = resumo.get("verificacao_cadastro_reserva", {})
    cont = vc.get("contagens_por_ciclo", {})
    linhas = ["| Ciclo | Células no quadro | Células só de cadastro reserva | Alocados na 1ª chamada | Alocados em células "
              "só de CR | Células com mais alocados que vagas imediatas | Células com mais alocados que imediatas + CR | "
              "Municípios com N1 > vagas imediatas |", "|---|---|---|---|---|---|---|---|"]
    for k, v in cont.items():
        linhas.append(f"| {k} | {v['celulas']} | {v['celulas_so_cadastro_reserva']} | {_n(v['alocados_ch1'], 0, sinal=False)} | "
                      f"{_n(v['alocados_em_celulas_so_cadastro_reserva'], 0, sinal=False)} | "
                      f"{v['celulas_com_alocados_acima_das_imediatas']} | {v['celulas_com_alocados_acima_de_imediatas_mais_cr']} | "
                      f"{v['municipios_com_N1_acima_das_imediatas']} |")
    t["verificacao_cr"] = "\n".join(linhas)
    linhas = ["| Edital | Item | Trecho |", "|---|---|---|"]
    for e in vc.get("editais", []):
        linhas.append(f"| {e['edital']} | {e['item']} | “{e['trecho']}” |")
    t["editais_cr"] = "\n".join(linhas)
    cp = resumo.get("controle", {})
    t["decisao_controle"] = (f"Resposta: **{vc.get('resposta', '—')}**. Controle principal das vagas oferecidas: "
                             f"**`{cp.get('principal_coluna', '—')}`**; sensibilidade: `{cp.get('sensibilidade_coluna', '—')}`.")
    # Principal e Holm.
    f = (est["especificacao"] == "S-a") & (est["variante"] == "principal") & est["entra_holm"].astype(bool)
    t["principal_holm"] = _tab(est[f], ["Outcome", "População", "n abaixo / acima", "Média abaixo", "Salto (S-a)",
                                        "IC 95% (CR1)", "IC honesto", "p", "p Holm", "Salto / média abaixo", "MDE"],
                               [lambda r: r["outcome_id"], lambda r: r["populacao"], _nab,
                                lambda r: _n(r["media_abaixo"], 2, sinal=False), _tau, _icr,
                                lambda r: _icr(r, "ic_honesto_inf", "ic_honesto_sup"), lambda r: _p(r["p_valor"]),
                                lambda r: _p(r["p_holm"]), _rel, lambda r: _n(r["mde"], 2, sinal=False)])
    t["leitura_principal"] = leitura_principal(est)
    su = resumo.get("sensibilidade_coeficiente_unico_auditoria_20", {}).get("linhas", [])
    linhas = ["| Outcome | População | Salto (S-a, coef. por grupo) | p Holm (protocolo) | Salto (coef. único) | "
              "IC 95% (CR1) | p | p Holm (só nesta variante) | Wald: coeficientes iguais entre grupos, p |",
              "|---|---|---|---|---|---|---|---|---|"]
    for x in su:
        linhas.append(f"| {x['outcome_id']} | {x['populacao']} | {_n(x['tau_principal'], 2)} | {_p(x['p_holm_principal'])} | "
                      f"{_n(x['tau_coef_unico'], 2)} | {_ic(x['ic95_inf_coef_unico'], x['ic95_sup_coef_unico'], 2)} | "
                      f"{_p(x['p_coef_unico'])} | {_p(x['p_holm_coef_unico'])} | {_p(x['wald_igualdade_p'])} |")
    t["coef_unico"] = "\n".join(linhas)
    rej_p = [x["outcome_id"] for x in su if x["p_holm_principal"] < 0.05]
    rej_u = [x["outcome_id"] for x in su if x["p_holm_coef_unico"] < 0.05]
    wald_rej = [x["outcome_id"] for x in su if x["wald_igualdade_p"] is not None and x["wald_igualdade_p"] < 0.05]
    t["leitura_coef_unico"] = (
        f"Linhas que rejeitam zero depois do Holm: no protocolo (coeficiente por grupo), "
        f"**{', '.join(rej_p) if rej_p else 'nenhuma'}**; com coeficiente único, "
        f"**{', '.join(rej_u) if rej_u else 'nenhuma'}**. O Wald rejeita a igualdade dos coeficientes entre os "
        f"grupos (p < 0,05) em **{', '.join(wald_rej) if wald_rej else 'nenhuma'}** das quatro linhas.")
    # Sem controle, mesma amostra empilhada.
    chave = est[f][["outcome_id", "populacao"]]
    g = est.merge(chave, on=["outcome_id", "populacao"])
    g = g[(g["especificacao"] == "S-b") & (g["variante"] == "principal") & (g["corte"] == EMPILHADO)]
    t["principal_sem_controle"] = _tab(g, ["Outcome", "População", "Média abaixo", "Salto (S-b)", "IC 95% (CR1)",
                                           "IC honesto", "p", "Salto / média abaixo", "MDE"],
                                       [lambda r: r["outcome_id"], lambda r: r["populacao"],
                                        lambda r: _n(r["media_abaixo"], 2, sinal=False), _tau, _icr,
                                        lambda r: _icr(r, "ic_honesto_inf", "ic_honesto_sup"), lambda r: _p(r["p_valor"]),
                                        _rel, lambda r: _n(r["mde"], 2, sinal=False)])
    # S-c: oferta como outcome, principal (V e U).
    f = (est["especificacao"] == "S-c") & (est["variante"] == "principal")
    t["sc_oferta"] = _tab(est[f & (est["populacao"] != "U")],
                          ["Oferta", "População", "Corte", "n abaixo / acima", "Média abaixo", "Salto", "IC 95%",
                           "IC honesto", "p", "Salto / média abaixo"],
                          [lambda r: f"{r['outcome_id']} `{r['outcome']}`", lambda r: r["populacao"], _corte, _nab,
                           lambda r: _n(r["media_abaixo"], 2, sinal=False), _tau, _icr,
                           lambda r: _icr(r, "ic_honesto_inf", "ic_honesto_sup"), lambda r: _p(r["p_valor"]), _rel])
    t["sc_oferta_U"] = _tab(est[f & (est["populacao"] == "U")],
                            ["Oferta", "Ciclo", "Corte", "n abaixo / acima", "Média abaixo", "Salto", "IC 95%", "p"],
                            [lambda r: f"{r['outcome_id']} `{r['outcome']}`", lambda r: r["ciclo"], _corte, _nab,
                             lambda r: _n(r["media_abaixo"], 3, sinal=False), _tau, _icr, lambda r: _p(r["p_valor"])])
    vered = resumo.get("veredito_S_c", {})
    t["veredito_sc"] = (f"Vagas oferecidas na forma principal (`{vered.get('oferta')}`) em V, linhas principais por "
                        f"ciclo × corte e empilhadas: **{vered.get('n_p_menor_005')} de {vered.get('n_linhas')}** com "
                        f"p < 0,05 no IC convencional"
                        + (f" ({vered.get('quais')})" if vered.get("quais") else "")
                        + f"; linha empilhada principal (ciclos e cortes): p = {_p(vered.get('p_empilhado'))}. "
                        + f"Regra fixada no código: o controle é tratado como possivelmente afetado se alguma dessas "
                        + f"linhas tiver p < 0,05 → **{'sim' if vered.get('possivelmente_afetado') else 'não'}**.")
    # Decomposição de N1.
    f = (est["outcome_id"] == "N1") & (est["especificacao"] == "decomposicao")
    sub = est[f].copy()
    piv = []
    for (pop, cic, cor), gg in sub.groupby(["populacao", "ciclo", "corte"], sort=False):
        d = {r["variante"]: r for r in gg.to_dict("records")}
        tot = d.get("total (= S-b na amostra de S-a)")
        via = d.get("via oferta (soma gamma x salto do controle)")
        pre = d.get("preenchimento dado as vagas (= S-a)")
        piv.append({"populacao": pop, "ciclo": cic, "corte": cor, "tot": tot, "via": via, "pre": pre})
    linhas = ["| População | Corte | Total (S-b) | = via oferta | + preenchimento dado as vagas (S-a) | IC 95% do total | "
              "IC 95% de S-a |", "|---|---|---|---|---|---|---|"]
    for x in piv:
        linhas.append(f"| {x['populacao']} | {str(x['corte']).replace('.', ',')} | {_n(x['tot']['tau'], 2)} | "
                      f"{_n(x['via']['tau'], 2)} | {_n(x['pre']['tau'], 2)} | "
                      f"{_ic(x['tot']['ic95_inf'], x['tot']['ic95_sup'], 2)} | {_ic(x['pre']['ic95_inf'], x['pre']['ic95_sup'], 2)} |")
    t["decomposicao_N1"] = "\n".join(linhas)
    # Por ciclo, S-a e S-b, N1–N4.
    f = (est["especificacao"].isin(["S-a", "S-b"])) & (est["variante"] == "principal") & (est["populacao"] != "U")
    t["por_ciclo"] = _tab(est[f], ["Outcome", "Esp.", "População", "Corte", "n abaixo / acima", "Média abaixo",
                                   "Salto", "IC 95%", "IC honesto", "p", "Salto / média", "MDE"],
                          [lambda r: r["outcome_id"], lambda r: r["especificacao"], lambda r: r["populacao"], _corte,
                           _nab, lambda r: _n(r["media_abaixo"], 2, sinal=False), _tau, _icr,
                           lambda r: _icr(r, "ic_honesto_inf", "ic_honesto_sup"), lambda r: _p(r["p_valor"]), _rel,
                           lambda r: _n(r["mde"], 2, sinal=False)])
    nao = est[(est["status"] == "NAO_EXECUTADO") & (est["especificacao"] == "S-a") & (est["variante"] == "principal")]
    t["nao_definidos"] = _tab(nao.drop_duplicates(["outcome_id", "populacao"]), ["Outcome", "População", "Motivo"],
                              [lambda r: r["outcome_id"], lambda r: r["populacao"], lambda r: r["nota"]])
    # Robustez de N1, empilhado (ciclos e cortes) e por ciclo empilhando cortes.
    f = (est["outcome_id"] == "N1") & (est["corte"] == EMPILHADO) & (est["populacao"] != "U") & \
        ~est["especificacao"].isin(["decomposicao"])
    t["robustez_N1"] = _tab(est[f], ["População", "Esp.", "Variante", "h", "Salto", "IC 95%", "p", "Salto / média",
                                     "nota curta"],
                            [lambda r: r["populacao"], lambda r: r["especificacao"], lambda r: r["variante"],
                             lambda r: _n(r["h"], 3, sinal=False), _tau, _icr, lambda r: _p(r["p_valor"]), _rel,
                             lambda r: ("M = " + _n(r["M"], 1, sinal=False)) if pd.notna(r["M"]) else
                             (r["status"] if r["status"] != "EXECUTADO" else "")])
    # S-d e S-e de N1 por ciclo x corte.
    f = (est["outcome_id"] == "N1") & est["especificacao"].isin(["S-d", "S-e"]) & (est["corte"] != EMPILHADO)
    t["sd_se_N1"] = _tab(est[f], ["População", "Corte", "Esp.", "Variante", "Salto", "IC 95%", "Efeito relativo (Poisson)",
                                  "p"],
                         [lambda r: r["populacao"], _corte, lambda r: r["especificacao"], lambda r: r["variante"], _tau,
                          _icr, lambda r: _rel(r, "efeito_relativo") if pd.notna(r["efeito_relativo"]) else "—",
                          lambda r: _p(r["p_valor"])])
    # S-h.
    f = est["especificacao"].eq("S-h") & est["outcome_id"].eq("N1")
    t["sh_N1"] = _tab(est[f], ["População", "Corte", "Variante", "Janela (±)", "n abaixo / acima", "Diferença de médias",
                               "p de Fisher", "status"],
                      [lambda r: r["populacao"], _corte, lambda r: r["variante"], lambda r: _n(r["w_lr"], 3, sinal=False),
                       _nab, _tau, lambda r: _p(r["p_valor"]), lambda r: r["status"]])
    # S-i: médias de segmento e resumo da grade.
    f = est["especificacao"].eq("S-i") & est["outcome_id"].eq("N1") & est["variante"].str.startswith("media_do_segmento")
    t["si_medias_N1"] = _tab(est[f], ["População", "Corte falso", "Variante", "n abaixo / acima", "Salto", "IC 95%", "p"],
                             [lambda r: r["populacao"], lambda r: _n(r["corte_placebo"], 3, sinal=False),
                              lambda r: r["variante"], _nab, _tau, _icr, lambda r: _p(r["p_valor"])])
    pr = pd.DataFrame(resumo.get("placebos_grade", []))
    if len(pr):
        pr = pr[pr["outcome_id"] == "N1"]
    t["si_grade_N1"] = _tab(pr, ["Ciclo", "Esp.", "Corte real", "Cortes falsos", "Fração com abs(t) > 1,96", "máx abs(t) falso",
                                 "t real", "p por posto"],
                            [lambda r: r["ciclo"], lambda r: r["especificacao"], _corte, lambda r: _fi(r["n_placebos"]),
                             lambda r: _n(r["fracao_abs_t_maior_1_96"], 3, sinal=False),
                             lambda r: _n(r["abs_t_placebo_max"], 2, sinal=False), lambda r: _n(r["t_real"], 2),
                             lambda r: _p(r["p_posto"])]) if len(pr) else "—"
    # U: efeito total.
    f = (est["populacao"] == "U") & (est["especificacao"] == "S-b") & (est["variante"] == "principal")
    t["u_total"] = _tab(est[f], ["Outcome", "Ciclo", "Corte", "n abaixo / acima", "Média abaixo", "Salto", "IC 95%", "p"],
                        [lambda r: r["outcome_id"], lambda r: r["ciclo"], _corte, _nab,
                         lambda r: _n(r["media_abaixo"], 3, sinal=False), _tau, _icr, lambda r: _p(r["p_valor"])])
    # Contagens e validações.
    q = resumo.get("contagens", {})
    v = resumo.get("validacoes", {})
    e6v = v.get("E6_ponderado", {})
    t["validacoes"] = "\n".join([
        "| Conferência | Resultado |", "|---|---|",
        f"| S-e de N2 e N3 reproduz o F1.3 e o F1.4 ponderados por células do E6 | {e6v.get('linhas_conferidas')} linhas; max abs dif = {e6v.get('max_abs_dif')} |",
        f"| salto de y residualizado = salto de S-a (FWL), em todas as amostras | {v.get('fwl_residualizacao')} |",
        f"| decomposição total = oferta + preenchimento fecha | {v.get('decomposicao', {}).get('linhas')} amostras; max abs resíduo = {v.get('decomposicao', {}).get('max_abs_residuo')} |",
        f"| Poisson local daqui = rdd_lib (um corte, offset) | {v.get('poisson_igual_rdd_lib')} |",
        f"| linhas em N_estimativas.csv | {q.get('linhas')} |",
        f"| linhas EXECUTADO / SEM_ESTIMATIVA / NAO_EXECUTADO | {q.get('executado')} / {q.get('sem_estimativa')} / {q.get('nao_executado')} |",
        f"| municípios com vagas oferecidas ausentes (saem da linha, nunca viram zero) | {q.get('municipios_com_controle_ausente')} |",
        f"| municípios do quadro sem IVS 2010 oficial (fora da RDD) | {q.get('municipios_sem_ivs_fora')} |",
    ])
    figs = resumo.get("saidas", {}).get("figuras", [])
    linhas = ["| Figura | População | Painel | Salto no título | IC 95% |", "|---|---|---|---|---|"]
    for fg in figs:
        for p in fg["paineis"]:
            linhas.append(f"| `{Path(fg['arquivo']).name}` | {fg['populacao']} | {p['especificacao']}, corte "
                          f"{str(p['corte']).replace('.', ',')} | {_n(p['tau'], 2)} | {_ic(p['ic95_inf'], p['ic95_sup'], 2)} |")
    t["figuras"] = "\n".join(linhas)
    return t


def leitura_principal(est: pd.DataFrame) -> str:
    """Frases de leitura das linhas principais empilhadas, por regra fixa (nenhum número digitado no doc)."""
    out = []
    princ = est[(est["variante"] == "principal") & (est["corte"] == EMPILHADO) & est["populacao"].str.contains(r"\+")]
    for oid in [s["id"] for s in CATALOGO_N]:
        ra = princ[(princ["outcome_id"] == oid) & (princ["especificacao"] == "S-a")]
        rb = princ[(princ["outcome_id"] == oid) & (princ["especificacao"] == "S-b")]
        if not len(ra) or not len(rb):
            continue
        ra, rb = ra.iloc[0], rb.iloc[0]
        pos = est[(est["outcome_id"] == oid) & (est["populacao"] == ra["populacao"]) & (est["corte"] == EMPILHADO)
                  & (est["variante"] == "S-a: ic_honesto_pos_resultado")]

        def exclui(lo, hi):
            return bool(np.isfinite(lo) and np.isfinite(hi) and (lo > 0 or hi < 0))

        def sinal(v):
            return "negativo (menos no lado de bolsa maior)" if v < 0 else "positivo (mais no lado de bolsa maior)"

        txt = (f"- **{oid}** ({ra['populacao']}): com controle (S-a), salto {sinal(ra['tau'])}; o IC 95% convencional "
               f"{'exclui' if exclui(ra['ic95_inf'], ra['ic95_sup']) else 'contém'} zero; depois do Holm, "
               f"{'rejeita' if ra['p_holm'] < 0.05 else 'não rejeita'} zero; o IC honesto da regra do E6 "
               f"{'exclui' if exclui(ra['ic_honesto_inf'], ra['ic_honesto_sup']) else 'contém'} zero")
        if len(pos):
            txt += (f", e o POS_RESULTADO também {'exclui' if exclui(pos.iloc[0]['ic95_inf'], pos.iloc[0]['ic95_sup']) else 'contém'}"
                    " zero")
        txt += (f". Sem controle (S-b), salto {sinal(rb['tau'])}, IC 95% convencional que "
                f"{'exclui' if exclui(rb['ic95_inf'], rb['ic95_sup']) else 'contém'} zero.")
        out.append(txt)
    return "\n".join(out)


MARCA = re.compile(r"(<!-- N:(?P<nome>[A-Za-z0-9_]+):inicio -->\n)(?P<corpo>.*?)(\n<!-- N:(?P=nome):fim -->)", re.S)


def aplicar_tabelas_doc(texto: str, tabelas: dict[str, str]) -> str:
    def sub(m):
        nome = m.group("nome")
        if nome not in tabelas:
            raise KeyError(f"tabela {nome} nao gerada")
        return m.group(1) + tabelas[nome] + m.group(4)
    return MARCA.sub(sub, texto)


def tabelas_no_doc(texto: str) -> dict[str, str]:
    return {m.group("nome"): m.group("corpo") for m in MARCA.finditer(texto)}


def ler_saidas() -> tuple[pd.DataFrame, dict]:
    est = pd.read_csv(OUT / NOME_EST, dtype={"corte": str, "ciclo": str})
    resumo = json.loads((OUT / NOME_RESUMO).read_text(encoding="utf-8"))
    return est, resumo


def atualizar_doc() -> None:
    if not DOC49.exists():
        print(f"{rotulo(DOC49)} nao existe: tabelas nao gravadas")
        return
    est, resumo = ler_saidas()
    DOC49.write_text(aplicar_tabelas_doc(DOC49.read_text(encoding="utf-8"), gerar_tabelas_doc(est, resumo)),
                     encoding="utf-8")
    print(f"tabelas do doc 49 regravadas: {rotulo(DOC49)}")


# ---------------------------------------------------------------------------
# Execução
# ---------------------------------------------------------------------------

def sensibilidade_coef_unico(est: pd.DataFrame, wald: dict) -> dict:
    """Auditoria 20 (fora do protocolo): as quatro linhas do Holm com um só coeficiente do controle, Holm entre elas
    e o Wald da igualdade dos coeficientes por grupo da S-a principal. Não substitui o Holm do protocolo."""
    princ = est[est["entra_holm"].astype(bool)]
    linhas = []
    for r in princ.to_dict("records"):
        u = est[(est["outcome_id"] == r["outcome_id"]) & (est["populacao"] == r["populacao"])
                & (est["corte"] == EMPILHADO) & (est["especificacao"] == "S-a")
                & (est["variante"] == "controle_coeficiente_unico")]
        if len(u) != 1:
            raise FalhaValidacao(f"sensibilidade de coeficiente unico sem linha unica para {r['outcome_id']}")
        u = u.iloc[0]
        wd = wald.get(r["outcome_id"]) or {}
        linhas.append({"outcome_id": r["outcome_id"], "populacao": r["populacao"],
                       "tau_principal": r["tau"], "p_principal": r["p_valor"], "p_holm_principal": r["p_holm"],
                       "tau_coef_unico": float(u["tau"]), "ep_coef_unico": float(u["ep"]),
                       "ic95_inf_coef_unico": float(u["ic95_inf"]), "ic95_sup_coef_unico": float(u["ic95_sup"]),
                       "p_coef_unico": float(u["p_valor"]), "coef_controle_unico": float(u["coef_controle"]),
                       "wald_igualdade_chi2": wd.get("chi2"), "wald_igualdade_gl": wd.get("gl"),
                       "wald_igualdade_p": wd.get("p_valor")})
    ph = L.holm(np.array([x["p_coef_unico"] for x in linhas], dtype=float)) if linhas else []
    for x, p in zip(linhas, ph):
        x["p_holm_coef_unico"] = float(p)
    return {"rotulo": ROTULO_AUD20, "no_protocolo": False, "linhas": linhas,
            "descricao": "S-a empilhada com um so coeficiente do controle para todos os grupos ciclo x corte (o "
                         "protocolo nao diz se o coeficiente e por grupo ou unico; a linha principal usa um por "
                         "grupo, decisao registrada em 'decisoes'); Holm entre as quatro linhas "
                         "nessa variante, so como sensibilidade; Wald (CR1) da igualdade dos coeficientes por grupo "
                         "na S-a principal"}


def veredito_sc(est: pd.DataFrame, oferta: str) -> dict:
    """Regra fixada no código: as vagas oferecidas são tratadas como possivelmente afetadas pela faixa se alguma
    linha principal de S-c (forma principal, V, por ciclo x corte, cortes empilhados ou ciclos empilhados) tiver p < 0,05."""
    f = (est["especificacao"] == "S-c") & (est["variante"] == "principal") & (est["outcome_id"] == oferta) & \
        (est["populacao"] != "U") & (est["status"] == "EXECUTADO")
    sub = est[f]
    sig = sub[sub["p_valor"] < 0.05]
    emp = sub[(sub["corte"] == EMPILHADO) & sub["populacao"].str.contains(r"\+")]
    return {"oferta": OFERTA[oferta]["col"], "n_linhas": int(len(sub)), "n_p_menor_005": int(len(sig)),
            "quais": "; ".join(f"{r['populacao']} {str(r['corte']).replace('.', ',')}" for r in sig.to_dict("records")),
            "p_empilhado": float(emp["p_valor"].iloc[0]) if len(emp) else None,
            "tau_empilhado": float(emp["tau"].iloc[0]) if len(emp) else None,
            "possivelmente_afetado": bool(len(sig) > 0),
            "regra": "possivelmente afetado se alguma linha principal de S-c em V (forma principal) tiver p < 0,05"}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--atualizar-doc", action="store_true", help="so regrava as tabelas do doc 49 a partir das saidas")
    args = ap.parse_args(argv)
    if args.atualizar_doc:
        atualizar_doc()
        return 0

    # (1) Running variable e populações (só chaves; IVS da tarefa B igual ao a08; primeiro estágio sharp).
    rv = E6.ler_running_variable()
    pops, conf_pop = E6.chaves_populacoes(rv)
    # (2) Verificação do cadastro reserva ANTES de estimar (contagens globais por ciclo, sem corte).
    cel = pd.read_parquet(ARQ_VC)
    vm = pd.read_parquet(ARQ_VM)
    dicionario = json.loads(DICIONARIO.read_text(encoding="utf-8"))
    verif = verificar_cadastro_reserva(cel, vm, dicionario)
    controle_principal = verif["controle_principal"]
    print("cadastro reserva:", verif["resposta"], "-> controle principal", OFERTA[controle_principal]["col"])
    # (3) Dados e janelas LR.
    V, U, info = carregar(rv, pops)
    lr = ler_lr(pops)
    # (4) Estimação.
    est, extras = estimar_tudo(V, U, controle_principal=controle_principal, lr=lr)
    # (5) Conferências (falha fechada antes de gravar).
    e6 = pd.read_csv(E6_EST, dtype={"corte": str, "ciclo": str})
    val_e6 = conferir_e6(est, e6)
    nucleo = ["tau", "ep", "ic95_inf", "ic95_sup", "p_valor"]
    sem_nota = est[est[nucleo].isna().any(axis=1) & (est["nota"].fillna("") == "")]
    if len(sem_nota):
        raise FalhaValidacao(f"{len(sem_nota)} linhas com NaN sem nota")
    if int(est["entra_holm"].sum()) != 4:
        raise FalhaValidacao(f"Holm com {int(est['entra_holm'].sum())} linhas; o protocolo pede 4 (N1-N4 S-a empilhado)")
    OUT.mkdir(parents=True, exist_ok=True)
    est.to_csv(OUT / NOME_EST, index=False)
    figs = gerar_figuras(V, est, controle_principal, OUT / DIR_FIG)
    # (6) Resumo.
    ver = veredito_sc(est, controle_principal)
    plac = resumo_placebos(est, extras["placebo_t"])
    holm = est[est["entra_holm"]][["outcome_id", "populacao", "ciclo", "corte", "tau", "ep", "ic95_inf", "ic95_sup",
                                    "p_valor", "p_holm", "ic_honesto_inf", "ic_honesto_sup", "media_abaixo",
                                    "efeito_relativo_media_abaixo", "mde"]].to_dict("records")
    sens_unico = sensibilidade_coef_unico(est, extras.get("wald_gamma", {}))
    entradas = [
        E6.bloco_entrada(PROTOCOLO_MD, "protocolo 48 congelado (somente lido)", "pipeline do repositorio", "2026-10-19",
                         "§§1-6", "documento", "-", "-"),
        E6.bloco_entrada(A08, "running variable (IVS 2010 oficial)", "Ipea, Atlas da Vulnerabilidade Social (a08)",
                         "Censo 2010", f"{len(rv)} municipios", "municipio", "co_ibge", "ivs"),
        E6.bloco_entrada(ARQ_VM, "N1-N4, vagas oferecidas e celulas (V1-V3)", "tarefa B (12_construir_outcomes_funil.py)",
                         "ver dicionario", ", ".join(f"V{k}: {len(d)}" for k, d in V.items()), "municipio x ciclo",
                         "ciclo, co_ibge", "municipios sem IVS oficial fora"),
        E6.bloco_entrada(ARQ_VC, "verificacao do cadastro reserva (contagens globais por celula, sem corte)",
                         "tarefa B", "ver dicionario", f"{len(cel)} celulas", "celula CNES x curso x ciclo",
                         "ciclo, co_cnes_7d, cod_curso", "colunas n_alocados_ch1, vagas_imediatas, vagas_cr"),
        E6.bloco_entrada(ARQ_U, "populacao secundaria U (zero fora do quadro)", "tarefa B", "ver dicionario",
                         f"{len(U)} municipios", "municipio", "co_ibge", "nenhum"),
        E6.bloco_entrada(DICIONARIO, "conferencia da verificacao (linhas alocadas em celula so CR)", "tarefa B",
                         "2026-10-18", "-", "documento", "-", "-"),
        E6.bloco_entrada(E6_LR, "janela de local randomization de V1-V3 (regra do E5)", "13_estimar_E6_funil.py",
                         "2026-10-18", "V1, V2, V3", "janela", "populacao, corte, w", "selecionada"),
        E6.bloco_entrada(E6_EST, "alvo de conferencia (S-e de N2/N3 = ponderado do E6)", "13_estimar_E6_funil.py",
                         "2026-10-18", f"{len(e6)} linhas", "linha de estimativa", "outcome_id, populacao, corte",
                         "especificacao == ponderado_celulas"),
    ] + [E6.bloco_entrada(p, "texto do edital (verificacao do cadastro reserva; somente lido)",
                          "Ministerio da Saude, SGTES", "edital do ciclo", "-", "documento", "-", "-")
         for p in sorted({t["arquivo"] for t in TRECHOS_EDITAL} | {EDITAL_C2})]
    contagens = {
        "linhas": int(len(est)), "executado": int((est["status"] == "EXECUTADO").sum()),
        "sem_estimativa": int((est["status"] == "SEM_ESTIMATIVA").sum()),
        "nao_executado": int((est["status"] == "NAO_EXECUTADO").sum()),
        "por_especificacao": est["especificacao"].value_counts().sort_index().to_dict(),
        "municipios_com_controle_ausente": sum(sum(v["municipios_com_vagas_oferecidas_ausentes"].values())
                                               for v in info.values()),
        "municipios_sem_ivs_fora": sum(v["municipios_sem_ivs_fora"] for v in info.values()),
    }
    residuos = extras["decomposicao_residuos"]
    resumo = {
        "etapa": "N_contagem_vagas_preenchidas",
        "natureza_dos_dados": NATUREZA,
        "estatuto": ESTATUTO,
        "data_execucao": DATA_EXECUCAO,
        "script": rotulo(Path(__file__)),
        "protocolo": {"arquivo": rotulo(PROTOCOLO_MD), "sha256": sha256(PROTOCOLO_MD)},
        "contraste": CONTRASTE,
        "salto": "tau = lado com bolsa maior (s > c) menos lado com bolsa menor; o corte pertence ao lado inferior",
        "entradas": entradas,
        "verificacao_cadastro_reserva": verif,
        "controle": {"principal": controle_principal, "principal_coluna": OFERTA[controle_principal]["col"],
                     "sensibilidade": verif["controle_sensibilidade"],
                     "sensibilidade_coluna": OFERTA[verif["controle_sensibilidade"]]["col"],
                     "N2_N3": "n_celulas",
                     "forma": "linear, coeficiente comum aos dois lados (CCFT 2019), dentro da regressao local "
                              "ponderada; centrado na media ponderada pelo kernel na janela; no empilhado, um "
                              "coeficiente por grupo (ciclo x corte)"},
        "populacoes": {k: v for k, v in info.items()},
        "municipios_sem_ivs_oficial_fora_da_rdd": conf_pop["municipios_sem_ivs_oficial_fora_da_rdd"],
        "janelas_lr": {f"{k[0]}|{ROTULO_CORTE[k[1]]}": (v["w"] / 1000 if v["w"] else None) for k, v in lr.items()},
        "holm": {"linhas": holm, "descricao": "Holm entre as quatro linhas S-a com ciclos e cortes empilhados "
                                              "(N1, N2, N3, N4), protocolo 48 §3"},
        "sensibilidade_coeficiente_unico_auditoria_20": sens_unico,
        "veredito_S_c": ver,
        "placebos_grade": plac,
        "validacoes": {"populacoes": conf_pop, "E6_ponderado": val_e6, "fwl_residualizacao": True,
                       "decomposicao": {"linhas": len(residuos), "max_abs_residuo": float(np.max(np.abs(residuos)))
                                        if residuos else None},
                       "poisson_igual_rdd_lib": True, "linhas_com_nan_sem_nota": 0},
        "contagens": contagens,
        "decisoes": [
            "Controle principal escolhido pela verificacao registrada em verificacao_cadastro_reserva antes de estimar; "
            "a outra forma e a variante 'controle_forma_alternativa' de S-a.",
            "Controle linear com coeficiente comum aos dois lados (CCFT 2019), centrado na media ponderada pelo kernel "
            "na janela (o centro so muda o intercepto). No empilhado (cortes e/ou ciclos), um coeficiente por grupo, "
            "comum aos dois lados do grupo.",
            "S-f: controle e T x controle, ambos centrados na media da janela; o salto e o do municipio com a media de "
            "vagas oferecidas da janela.",
            "S-g: IC honesto com a regra do E6 (M pela regra de bolso, quartica por lado com suporte ate o ponto medio "
            "entre cortes; M x 0,5, 1 e 2) e a variante POS_RESULTADO do E6 (lado interno ate o outro corte). Com "
            "controle, o IC honesto e aplicado a y~ = y - gamma (v - v_barra), com gamma de S-a na janela tratado como "
            "fixo (a incerteza de gamma nao entra no IC honesto). Sem h otimo (o protocolo fixa h = 0,050).",
            "S-d: Poisson local com o mesmo algoritmo da rdd_lib (reproduz rd_poisson_local com um corte e offset, "
            "conferido); com covariavel e no empilhado, colunas extras e CR1 por municipio. Ciclos empilhados com "
            "intercepto e inclinacoes por grupo.",
            "S-e: y / controle com peso = kernel x controle; para N2 e N3 e o F1.3 e o F1.4 ponderados do E6 "
            "(reproduzidos).",
            "S-h: janela da regra do E5 gravada pelo E6 (E6_lr_selecao_janela.csv, 'janela minima do E5' = a janela "
            "selecionada pela regra de balanco); com controle, ajuste de covariavel de Rosenbaum (2002): residuo de "
            "MQO de y em (1, controle) na janela, sem o tratamento. So por ciclo x corte.",
            "S-i: 'cortes placebo nas medias de cada lado, como no E9' lido como (a) corte falso na media do IVS de "
            "cada segmento de bolsa (abaixo de 0,300, entre 0,300 e 0,400, acima de 0,400) e (b) a grade do E9 "
            "(0,190 a 0,510 de 0,010 em 0,010, a mais de 0,010 dos cortes), com p por posto; cada corte falso usa so "
            "os municipios do seu segmento. So por ciclo.",
            "S-j: donut sem os municipios com |IVS - corte| < 0,002 (IVS em milesimos: x em -1, 0, +1).",
            "Media abaixo do corte = media simples do outcome bruto nas linhas usadas do lado de baixo da janela; "
            "efeito relativo = salto / essa media; MDE = 2,8 x EP (convencional; na linha honesta, o EP do IC honesto).",
            "Populacao secundaria U: N1-N3 = valor de V_k no municipio do quadro e zero estrutural fora do quadro (sem "
            "celula, sem alocado); N4 = ativos do ciclo na relacao nominal (n_ativos_pmme_c{k}, igual a V_k no quadro); "
            "so S-b (efeito total) e S-c, com h = 0,050, 0,030 e 0,080.",
            "Holm entre as quatro linhas S-a principais com ciclos e cortes empilhados: N1 e N2 em V1+V2+V3; N3 e N4 "
            "em V1+V2 (nao definidos no ciclo 3).",
        ],
        "desvios": [
            {"data": DATA_EXECUCAO, "item": "N3 e N4 no ciclo 3",
             "situacao": "o protocolo 48 lista ciclos 1 a 3; N3 (ate a 2a chamada) e N4 (ativos) nao existem no ciclo 3 "
                         "(tarefa B; ciclo 3 congelado para presenca)",
             "resolucao": "linhas NAO_EXECUTADO com o motivo gravado pela tarefa B; empilhamento so com os ciclos 1 e 2"},
            {"data": DATA_EXECUCAO, "item": "S-d, S-h e S-i empilhados",
             "situacao": "a rdd_lib nao tem Poisson empilhado nem local randomization empilhada",
             "resolucao": "Poisson empilhado implementado aqui com o algoritmo da rdd_lib (CR1); S-h e S-i so por ciclo "
                          "x corte"},
            {"data": DATA_EXECUCAO, "item": "auditoria 20 (docs/auditorias/20_auditoria_contagem_vagas_N.md)",
             "situacao": "o protocolo nao diz se, no empilhado, o coeficiente do controle e por grupo ou unico; S-h "
                         "e S-i empilhados nao tinham linha propria",
             "resolucao": "acrescentada a variante S-a 'controle_coeficiente_unico' (fora do protocolo, rotulo "
                          "SENSIBILIDADE_AUDITORIA_20) com Holm proprio e Wald da igualdade dos coeficientes; S-h "
                          "empilhado e S-i com ciclos empilhados saem NAO_EXECUTADO com o motivo; a linha principal "
                          "e o Holm do protocolo nao mudam"},
            {"data": DATA_EXECUCAO, "item": "edital do ciclo 2",
             "situacao": "a copia do Edital SGTES/MS 1/2026 no repositorio e so a pagina do chamamento",
             "resolucao": "a verificacao do ciclo 2 usa so os quadros e resultados (nenhum alocado da 1a chamada em "
                          "celula so de CR); os editais dos ciclos 1 e 3 sao citados"},
        ],
        "saidas": {NOME_EST: {"arquivo": rotulo(OUT / NOME_EST), "sha256": sha256(OUT / NOME_EST)}, "figuras": figs},
        "linguagem": "RDD em nivel = pacote do corte; com controle, o salto e condicional as vagas oferecidas, que "
                     "podem responder a faixa; resultado nulo e falta de evidencia com a precisao relatada, nao "
                     "ausencia de efeito",
    }
    _gravar_json(OUT / NOME_RESUMO, resumo)
    atualizar_doc()
    print(json.dumps(_nan_none({"holm": holm, "veredito_S_c": ver}), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except FalhaValidacao as erro:
        print(f"FALHA DE VALIDACAO: {erro}", file=sys.stderr)
        sys.exit(2)
