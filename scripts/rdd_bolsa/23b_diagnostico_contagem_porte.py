"""Diagnóstico ND (fora do protocolo 48): porte, oferta e taxa na RDD do número de vagas preenchidas (N1).

Por que existe
--------------
Na figura de N1 do doc 49 (com controle, ciclos e cortes empilhados) o autor viu dois padrões estranhos:
(a) dentro da janela, a contagem de vagas preenchidas sobe com o IVS, sobretudo à esquerda do corte;
(b) no corte, a contagem cai do lado de bolsa maior.
Este script examina de onde vêm os dois padrões. É **diagnóstico**, fora do protocolo 48: não substitui a
especificação principal (S-a empilhada), não muda o Holm do protocolo 48 e nenhuma variante daqui vira
especificação principal. Toda linha sai com `estatuto = DIAGNOSTICO_FORA_PROTOCOLO_48` e
`natureza_dos_dados = EMPIRICO`.

Conjunto fixo de diagnósticos (listado em `ND_resumo.json`, chave `diagnosticos`, e no doc 49b antes dos
resultados; todos relatados, qualquer que seja o resultado)
--------------------------------------------------------------------------------------------------------
- D1, decomposição contagem = oferta × taxa: saltos local linear (h = 0,050, triangular, CR1 por município,
  como no script 23) em log(população 2022), vagas imediatas, vagas oferecidas (imediatas + cadastro reserva,
  controle principal do protocolo 48), nº de células, N1 sem controle e taxa ponderada (alocados / vagas, peso
  = vagas; com as vagas oferecidas e com as imediatas). Decomposição log-aditiva log(N1) = log(oferta) +
  log(taxa) nos municípios com N1 > 0, com a contagem dos que ficam de fora.
- D2, de onde vem a inclinação: médias por faixa de 0,010 da distância ao corte (população, vagas, N1, taxa);
  inclinação de cada lado com e sem log(pop) como covariável; influência por município (leave-one-out do
  salto) no N1 com controle e no Poisson com offset; os 10 municípios mais influentes por corte;
  sensibilidade retirando os k = 1, 3, 5 municípios mais populosos da janela de cada lado.
- D3, forma da estimativa da taxa: Poisson com offset log(vagas oferecidas) com h em {0,020; 0,030; 0,050;
  0,080}; local linear da taxa ponderada nas mesmas janelas; diferença de médias (local constante) em ±0,010,
  ±0,020 e ±0,030, ponderada por vagas e sem peso; local quadrático com h = 0,080; banda ótima com viés
  corrigido (estilo rdrobust) se a rdd_lib a tiver.
- D4, porte como covariável: N1 sem controle, com log(pop) e com log(pop) + vagas imediatas; N1 com o controle
  do protocolo (referência); contagem por vaga oferecida (N1 / vagas, sem peso) como outcome.
- D5, empilhamento: peso efetivo (omega) e contribuição de cada ciclo × corte no salto empilhado; empilhado
  comparado com os cortes isolados.

Amostras
--------
- POR_CORTE (principal deste diagnóstico): um corte de cada vez (0,300 e 0,400), ciclos 1–3 juntos com
  intercepto e inclinações por ciclo (o efeito fixo de ciclo do protocolo), salto comum, EP CR1 por município;
- APENDICE_POR_CICLO: ciclo × corte, local linear com EP HC1 (D1 e D4);
- EMPILHADO_COMPARACAO: ciclos e cortes empilhados (a amostra da figura que o autor viu), só como comparação.

Integridade
-----------
Nada imputado nem simulado. A running variable é o IVS 2010 oficial do Ipea (a08), conferida contra as saídas
da tarefa B pelas funções do E6; o arquivo local de IVS da auditoria 16 não é lido. Taxa com denominador zero
(vagas imediatas = 0) e log de zero (N1 = 0) ficam ausentes, contados por lado, nunca viram zero. O doc 49b é
gerado inteiro por este script a partir das saídas; nenhum número é digitado.

Uso
---
    python3 scripts/rdd_bolsa/23b_diagnostico_contagem_porte.py
    python3 scripts/rdd_bolsa/23b_diagnostico_contagem_porte.py --atualizar-doc
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import re
import sys
import textwrap
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


_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
T23 = _importar(DIR_RDD / "23_estimar_contagem_vagas.py", "contagem_vagas_para_nd")
sys.dont_write_bytecode = _bytecode
L, E6 = T23.L, T23.E6

# ---------------------------------------------------------------------------
# Caminhos e parâmetros (constantes permitidas: cortes, janelas, k, largura da faixa)
# ---------------------------------------------------------------------------

OUT = ROOT / "output" / "rdd_bolsa"
NOME_EST = "ND_estimativas.csv"
NOME_RESUMO = "ND_resumo.json"
DIR_FIG = "ND_figuras"
DOC = ROOT / "docs" / "06_execucao" / "49b_diagnostico_contagem_porte.md"
A08 = T23.A08
ARQ_VM = T23.ARQ_VM
N_EST = OUT / "N_estimativas.csv"

DATA_EXECUCAO = "2026-10-21"
# Correção de 26/10/2026 (auditoria 36; adendo 48b, §7): o zero de alocados nas células só de reserva do ciclo 2
# vale para o quadro de 19/03/2026, refeito depois do resultado preliminar; não é a regra do ciclo. Texto, sem número
# de resultado.
NOTA_A36_C2 = ("no quadro de 19/03/2026, usado aqui, que foi refeito depois do resultado preliminar e converteu em "
               "imediatas vagas de reserva onde houve alocado; pelo quadro de 13/02/2026, vigente na inscrição, havia "
               "alocados do ciclo 2 em células só de reserva (correção de 26/10/2026: "
               "[auditoria 36](../auditorias/36_auditoria_dados_H1.md); "
               "[adendo 48b, §7](48b_adendo_H1_vagas_imediatas.md))")
ESTATUTO = "DIAGNOSTICO_FORA_PROTOCOLO_48"
NATUREZA = "EMPIRICO"
CORTES = L.CORTES_MIL                 # (300, 400)
CICLOS = (1, 2, 3)
H = L.H_PRINCIPAL_MIL                 # 50
H_D3 = (20, 30, 50, 80)
JANELAS_LC = (10, 20, 30)             # local constante: |x| <= w (milésimos), kernel uniforme
JANELA_LC_ADENDO = 50                 # adendo 1: a janela inteira (|x| < 0,050), como nas pistas brutas
H_QUAD = 80
KS = (1, 3, 5)
N_TOP = 10
LARGURA_FAIXA = 10
ROTULO_CORTE = T23.ROTULO_CORTE       # {300: "0,300", 400: "0,400"}
POR_CORTE = "POR_CORTE"
APENDICE = "APENDICE_POR_CICLO"
EMP = "EMPILHADO_COMPARACAO"
EMPILHADO = "empilhado"
CONTRASTE = E6.CONTRASTE

VARIAVEIS = {
    "log_pop": {"col": "log_pop", "desc": "log da populacao do Censo 2022", "un": "log(habitantes)"},
    "VI": {"col": "vagas_imediatas", "desc": "vagas imediatas no quadro da 1a chamada", "un": "vagas por municipio"},
    "VIC": {"col": "vagas_imediatas_mais_cr", "desc": "vagas oferecidas: imediatas + cadastro reserva (controle "
            "principal do protocolo 48)", "un": "vagas por municipio"},
    "NC": {"col": "n_celulas", "desc": "celulas (estabelecimento x curso) no quadro", "un": "celulas por municipio"},
    "N1": {"col": "n_alocados_ch1", "desc": "vagas preenchidas na 1a chamada (N1)", "un": "vagas preenchidas por municipio"},
    "TAXA_VIC": {"col": "taxa_vic", "desc": "N1 / vagas oferecidas, peso = vagas oferecidas (taxa no nivel da vaga)",
                 "un": "fracao (x100 = p.p.)", "peso": "vagas_imediatas_mais_cr"},
    "TAXA_VI": {"col": "taxa_vi", "desc": "N1 / vagas imediatas, peso = vagas imediatas (so municipios com vaga "
                "imediata)", "un": "fracao (x100 = p.p.)", "peso": "vagas_imediatas"},
    "N1_POR_VAGA": {"col": "taxa_vic", "desc": "N1 / vagas oferecidas, sem peso (media simples entre municipios)",
                    "un": "fracao (x100 = p.p.)"},
    "LOG_N1": {"col": "log_n1", "desc": "log(N1), so N1 > 0", "un": "log"},
    "LOG_VIC": {"col": "log_vic", "desc": "log(vagas oferecidas), so N1 > 0", "un": "log"},
    "LOG_TAXA": {"col": "log_taxa_vic", "desc": "log(N1 / vagas oferecidas), so N1 > 0", "un": "log"},
}
MOTIVO_TAXA_VI = "vagas imediatas = 0: taxa com denominador zero fica ausente (nunca zero)"
MOTIVO_LOG = "N1 = 0: log(0) indefinido; o municipio sai da decomposicao log-aditiva (nunca vira zero)"
MOTIVO_RDROBUST = ("banda otima com vies corrigido (estilo rdrobust, Calonico, Cattaneo e Titiunik 2014) nao "
                   "executada: a rdd_lib nao tem esse estimador (so o h que minimiza o IC honesto, rd_honesto_h_otimo, "
                   "que e outro conceito); nao se acrescenta dependencia nova num diagnostico")

DIAGNOSTICOS = [
    {"id": "D1", "nome": "decomposicao contagem = oferta x taxa",
     "itens": ["saltos local linear (h = 0,050, triangular, CR1 por municipio) em log(pop 2022), vagas imediatas, "
               "vagas oferecidas (imediatas + CR), n de celulas, N1 sem controle, N1 com o controle do protocolo, "
               "taxa ponderada com as vagas oferecidas e taxa ponderada com as vagas imediatas",
               "decomposicao log-aditiva log(N1) = log(vagas oferecidas) + log(taxa) nos municipios com N1 > 0, com "
               "o numero de linhas fora por lado e a identidade conferida",
               "por corte (ciclos juntos); apendice por ciclo; empilhado so como comparacao"]},
    {"id": "D2", "nome": "de onde vem a inclinacao",
     "itens": ["medias por faixa de 0,010 da distancia ao corte (populacao media e mediana, vagas, N1, taxa "
               "ponderada e media simples), por corte e no empilhado de comparacao",
               "inclinacao de cada lado (por 0,010 de IVS) de N1 sem e com o controle do protocolo, cada uma sem e "
               "com log(pop) como covariavel",
               "influencia por municipio: leave-one-out do salto de N1 com controle (S-a) e do Poisson com offset "
               "(S-d), todos os municipios da janela; os 10 mais influentes por corte (co_ibge, nome, populacao, "
               "vagas, lado, distancia)",
               "sensibilidade retirando os k = 1, 3, 5 municipios mais populosos da janela, abaixo, acima e dos dois "
               "lados, em N1 com e sem controle, no Poisson com offset e na taxa ponderada"]},
    {"id": "D3", "nome": "forma da estimativa da taxa",
     "itens": ["Poisson local com offset log(vagas oferecidas), h em 0,020; 0,030; 0,050; 0,080",
               "local linear da taxa ponderada (vagas oferecidas e vagas imediatas), mesmas janelas",
               "diferenca de medias (local constante, kernel uniforme, intercepto por ciclo) em +-0,010, +-0,020 e "
               "+-0,030, ponderada por vagas e sem peso, com as vagas oferecidas e com as imediatas",
               "local quadratico (curvatura propria de cada lado) com h = 0,080 da taxa ponderada e de N1 com e sem "
               "controle",
               "banda otima com vies corrigido estilo rdrobust, se a rdd_lib tiver"]},
    {"id": "D4", "nome": "porte como covariavel",
     "itens": ["N1 sem controle; com log(pop); com log(pop) + vagas imediatas; com o controle do protocolo 48 "
               "(vagas oferecidas, referencia)", "contagem por vaga oferecida (N1 / vagas, sem peso) como outcome",
               "por corte; apendice por ciclo; empilhado so como comparacao"]},
    {"id": "D5", "nome": "empilhamento",
     "itens": ["peso efetivo omega (Cattaneo, Keele, Titiunik e Vazquez-Bare 2016) e contribuicao omega x salto de "
               "cada ciclo x corte no salto empilhado, para N1 sem e com controle, com a identidade "
               "salto empilhado = soma das contribuicoes conferida",
               "o mesmo dentro de cada corte (pesos dos ciclos)",
               "empilhado comparado com os cortes isolados (N1 sem e com controle, Poisson com offset, taxa)"]},
]

EXPOSICAO_PREVIA = [
    "Pistas do pedido (conta descritiva no chat, fora de output/): populacao media e vagas imediatas nas faixas "
    "-0,015, -0,005 e +0,005; taxa bruta alocados/vagas maior acima do corte em media simples; N1 por corte com e "
    "sem controle (doc 49); Poisson com offset empilhado negativo; atracao (f1_1) e fracao preenchida (f1_3) sem "
    "salto no E6.",
    "Ja publicados no doc 49 antes deste diagnostico: S-a, S-b, S-c, S-d e S-e por corte e empilhados; decomposicao "
    "total = oferta + preenchimento; A4 (log pop e estoques CNES).",
    "Exploracao feita ao preparar este script, antes de fixar a lista (registrada aqui por transparencia): medias "
    "por faixa de populacao, vagas, N1 e taxa ponderada por corte; saltos por corte em log(pop), vagas e taxa "
    "ponderada; Poisson com offset por corte com h de 0,020 a 0,080; leave-one-out de S-a e do Poisson por corte; "
    "taxas medias simples e ponderadas com vagas oferecidas e imediatas nas janelas +-0,010 a +-0,050.",
]

ADENDOS = [
    {"data": "2026-10-21", "id": "AD1",
     "o_que": "D3 ganha a diferenca de medias na janela inteira (|x| < 0,050), ponderada e sem peso, com as vagas "
              "oferecidas e com as imediatas",
     "por_que": "a taxa bruta das pistas (maior acima do corte em media simples) e uma media da janela inteira com "
                "as vagas imediatas no denominador; sem esta linha, o conflito com o Poisson com offset nao pode ser "
                "reconciliado com os numeros gravados",
     "ja_visto": "a exploracao registrada em exposicao_previa (medias simples e ponderadas com os dois "
                 "denominadores nas janelas +-0,010 a +-0,050) ja tinha mostrado que a media simples com as vagas "
                 "imediatas, na janela inteira, e maior acima do corte"},
]

COLUNAS = [
    "natureza_dos_dados", "estatuto", "id_linha", "diagnostico", "tipo_linha", "amostra", "populacao", "ciclo",
    "corte", "outcome", "descricao_outcome", "especificacao", "variante", "estimador", "h", "peso", "unidade",
    "status", "n_abaixo", "n_acima", "n_obs", "n_clusters", "n_fora_abaixo", "n_fora_acima", "motivo_fora",
    "tau", "ep", "ic95_inf", "ic95_sup", "p_valor", "media_abaixo", "media_acima",
    "inclinacao_abaixo", "ep_inclinacao_abaixo", "inclinacao_acima", "ep_inclinacao_acima",
    "grupo", "peso_omega", "tau_grupo", "contribuicao", "residuo_identidade",
    "faixa", "faixa_inf", "faixa_sup", "lado", "n_linhas", "n_municipios", "pop_media", "pop_mediana",
    "vi_media", "vic_media", "nc_media", "n1_media", "taxa_vic_ponderada", "taxa_vic_media_simples",
    "taxa_vi_ponderada", "maior_municipio",
    "co_ibge", "nome_municipio", "populacao_2022", "vagas_oferecidas_ciclos", "n_alocados_ciclos", "distancia",
    "delta_tau", "delta_tau_sobre_ep", "posto", "k_retirados", "retirados", "nota",
    "adendo", "vagas_imediatas_ciclos", "vagas_cr_ciclos", "fracao_cr",
]


class FalhaValidacao(RuntimeError):
    """Conferência que falhou: o script para sem gravar."""


sha256 = E6.sha256
rotulo = E6.rotulo


def _juntar(*notas) -> str:
    return "; ".join(str(n) for n in notas if n)


# ---------------------------------------------------------------------------
# Dados
# ---------------------------------------------------------------------------

def preparar(V: dict[int, pd.DataFrame], nomes: pd.Series) -> dict[int, pd.DataFrame]:
    """Colunas derivadas por município × ciclo; ausência (taxa com denominador zero, log de zero) fica NaN."""
    out = {}
    for k, d in V.items():
        d = d.copy()
        pop = d["populacao_2022"].astype(float)
        if (pop.isna() | (pop <= 0)).any():
            raise FalhaValidacao(f"V{k}: populacao 2022 ausente ou nao positiva")
        vic = d["vagas_imediatas_mais_cr"].astype(float)
        vi = d["vagas_imediatas"].astype(float)
        n1 = d["n_alocados_ch1"].astype(float)
        if (vic <= 0).any():
            raise FalhaValidacao(f"V{k}: municipio do quadro sem vaga oferecida")
        d["log_pop"] = np.log(pop)
        d["taxa_vic"] = n1 / vic
        d["taxa_vi"] = np.where(vi > 0, n1 / np.where(vi > 0, vi, 1.0), np.nan)
        pos = n1 > 0
        d["log_n1"] = np.where(pos, np.log(np.where(pos, n1, 1.0)), np.nan)
        d["log_vic"] = np.where(pos, np.log(vic), np.nan)
        d["log_taxa_vic"] = d["log_n1"] - d["log_vic"]
        d["nome_municipio"] = d["co_ibge"].map(nomes)
        out[k] = d
    return out


def amostra_corte(V: dict, c: int):
    return T23.montar_amostra([(V[k], c, f"c{k}") for k in CICLOS], empilhada=True)


def amostra_ciclo(V: dict, k: int, c: int):
    return T23.montar_amostra([(V[k], c, str(c))], empilhada=False)


def amostra_empilhada(V: dict):
    return T23.montar_amostra([(V[k], c, f"c{k}_{c}") for k in CICLOS for c in CORTES], empilhada=True)


def _x(a) -> np.ndarray:
    return L.normalizar_s_mil(a.s) - a.c


# ---------------------------------------------------------------------------
# Estimadores (rdd_lib e script 23)
# ---------------------------------------------------------------------------

def ajustar(a, y: np.ndarray, h=H, covs: tuple = (), *, peso: np.ndarray | None = None, quad: bool = False) -> dict:
    """Local linear (um corte, HC1) ou empilhado (CR1 por município), com covariáveis CCFT por grupo.

    Cada covariável entra centrada na média ponderada pelo kernel do grupo, com um coeficiente por grupo, comum
    aos dois lados (a mesma forma do controle do script 23). `quad=True` acrescenta x² e T·x² por grupo (local
    quadrático com curvatura própria de cada lado).
    """
    Zs, nomes = [], []
    for nome, v in covs:
        Z, nm, _, _ = T23.colunas_controle(a, y, v, h, peso=peso)
        Zs.append(Z)
        nomes += [n.replace("controle", nome) for n in nm]
    if quad:
        x = _x(a) / 1000.0
        grupos = sorted(np.unique(a.g).tolist()) if a.empilhada else [None]
        for gl in grupos:
            m = (a.g == gl).astype(float) if gl is not None else np.ones(len(x))
            suf = f"[{gl}]" if gl is not None else ""
            Zs.append(np.column_stack([m * x ** 2, m * a.t * x ** 2]))
            nomes += [f"x2{suf}", f"T_x2{suf}"]
    Z = np.column_stack(Zs) if Zs else None
    if a.empilhada:
        return L.rd_empilhado(a.s, y, a.c, grupo=a.g, h_mil=h, cluster=a.cl, ids_unidade=a.cl, Z=Z, nomes_z=nomes or None,
                              peso=peso, detalhes=True)
    return L.rd_local_linear(a.s, y, a.corte_unico, h, Z=Z, nomes_z=nomes or None, peso=peso, detalhes=True)


def local_constante(a, y: np.ndarray, w_mil: int, *, peso: np.ndarray | None = None) -> dict:
    """Diferença de médias em |x| <= w (kernel uniforme), intercepto por grupo (dummies comuns aos dois lados)."""
    x = _x(a)
    grupos = sorted(np.unique(a.g).tolist())
    Z = np.column_stack([(a.g == gl).astype(float) for gl in grupos[1:]]) if len(grupos) > 1 else None
    nomes = [f"grupo[{gl}]" for gl in grupos[1:]] if Z is not None else None
    kw = {"cluster": a.cl, "ids_unidade": a.cl} if a.empilhada else {}
    return L.rd_local_linear(x, y, 0.0, w_mil + 0.5, kernel="uniforme", grau=0, peso=peso, Z=Z, nomes_z=nomes,
                             detalhes=True, **kw)


def poisson_offset(a, h=H) -> dict:
    y = a.col("n_alocados_ch1")
    return T23.poisson(a, y, h, offset=np.log(a.col("vagas_imediatas_mais_cr")))


def medias_lados(r: dict, y: np.ndarray, peso: np.ndarray | None = None) -> tuple[float, float]:
    """Média (ponderada por `peso`, se houver) do outcome nas linhas usadas de cada lado da janela."""
    if "_detalhes" not in r:
        return float("nan"), float("nan")
    d = r["_detalhes"]
    out = []
    for m in (d["usa"] & (d["x_mil"] <= 0), d["usa"] & (d["x_mil"] > 0)):
        if not m.any():
            out.append(float("nan"))
        elif peso is None:
            out.append(float(np.mean(y[m])))
        else:
            out.append(float(np.sum(peso[m] * y[m]) / np.sum(peso[m])))
    return out[0], out[1]


def inclinacoes(r: dict, a) -> dict:
    """Inclinação de cada lado, por 0,010 de IVS; no empilhado, média das retas dos grupos (peso = kernel do grupo)."""
    if "_detalhes" not in r:
        return {}
    d = r["_detalhes"]
    fit = d["fit"]
    if a.empilhada:
        grupos = sorted(np.unique(a.g).tolist())
        pw = {gl: float(np.sum(d["w"][d["usa"] & (a.g == gl)])) for gl in grupos}
        tot = sum(pw.values())
        ab = [(f"x[{gl}]", pw[gl] / tot) for gl in grupos]
        ac = ab + [(f"T_x[{gl}]", pw[gl] / tot) for gl in grupos]
    else:
        ab = [("x", 1.0)]
        ac = ab + [("T_x", 1.0)]
    res = {}
    for lado, cs in (("abaixo", ab), ("acima", ac)):
        val, ep = T23._linha_prevista(fit, cs, fit["V"])
        res[lado] = (val * LARGURA_FAIXA / 1000.0, ep * LARGURA_FAIXA / 1000.0)
    return res


# ---------------------------------------------------------------------------
# Linhas
# ---------------------------------------------------------------------------

def nova(diag: str, tipo: str, amostra: str, pop: str, ciclo: str, corte: str, outcome: str, esp: str,
         variante: str, **kw) -> dict:
    ln = {c: np.nan for c in COLUNAS}
    ln.update({"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "diagnostico": diag, "tipo_linha": tipo,
               "amostra": amostra, "populacao": pop, "ciclo": ciclo, "corte": corte, "outcome": outcome,
               "especificacao": esp, "variante": variante, "status": "EXECUTADO", "nota": "", "peso": "",
               "estimador": "", "unidade": "", "motivo_fora": "", "grupo": "", "faixa": "", "lado": "",
               "maior_municipio": "", "co_ibge": "", "nome_municipio": "", "retirados": "", "adendo": "",
               "descricao_outcome": VARIAVEIS.get(outcome, {}).get("desc", "")})
    ln["id_linha"] = "|".join(str(x) for x in (diag, tipo, amostra, pop, corte, outcome, esp, variante))
    ln.update(kw)
    return ln


def preencher(ln: dict, r: dict, *, medias: tuple | None = None) -> dict:
    for k in ("tau", "ep", "ic95_inf", "ic95_sup", "p_valor", "n_abaixo", "n_acima", "n_obs", "n_clusters"):
        if r.get(k) is not None:
            ln[k] = r[k]
    ln["nota"] = _juntar(ln.get("nota", ""), r.get("nota", ""),
                         f"colunas descartadas: {r['covariaveis_descartadas']}" if r.get("covariaveis_descartadas") else "")
    if medias is not None:
        ln["media_abaixo"], ln["media_acima"] = medias
    if not np.isfinite(float(ln["tau"])):
        ln["status"] = "SEM_ESTIMATIVA"
        if not ln["nota"]:
            ln["nota"] = "biblioteca devolveu NaN sem motivo"
    return ln


def _est_txt(a, base: str) -> str:
    if a.empilhada:
        return f"{base}; intercepto e inclinacoes por grupo x lado, salto comum, CR1 por municipio"
    return f"{base}; EP HC1"


def _ctx(amostra: str, a, k=None, c=None) -> dict:
    if amostra == POR_CORTE:
        return {"pop": "V1+V2+V3", "ciclo": "1+2+3", "corte": ROTULO_CORTE[c]}
    if amostra == APENDICE:
        return {"pop": f"V{k}", "ciclo": str(k), "corte": ROTULO_CORTE[c]}
    return {"pop": "V1+V2+V3", "ciclo": "1+2+3", "corte": EMPILHADO}


def fora_por_lado(a, col: str, h=H) -> tuple[int, int]:
    x = _x(a)
    jan = L.pesos_kernel(x, h) > 0
    nan = ~np.isfinite(a.col(col))
    return int((jan & nan & (x <= 0)).sum()), int((jan & nan & (x > 0)).sum())


def linha_ll(diag, amostra, a, ctx, outcome, esp, variante, *, h=H, covs=(), peso_col=None, quad=False,
             y_col=None, estimador=None, nota="") -> tuple[dict, dict]:
    spec = VARIAVEIS[outcome]
    col = y_col or spec["col"]
    y = a.col(col)
    peso = a.col(peso_col) if peso_col else None
    if peso is not None:
        peso = np.where(np.isfinite(y), peso, np.nan)   # a linha sem taxa definida sai pelo y, não pelo peso
    r = ajustar(a, y, h, tuple((n, a.col(cc)) for n, cc in covs), peso=peso, quad=quad)
    est = estimador or _est_txt(a, ("local quadratico" if quad else "local linear") + ", kernel triangular"
                                + (f", covariaveis CCFT por grupo: {', '.join(cc for _, cc in covs)}" if covs else "")
                                + (f", peso = kernel x {peso_col}" if peso_col else ""))
    ln = nova(diag, "estimativa", amostra, ctx["pop"], ctx["ciclo"], ctx["corte"], outcome, esp, variante,
              estimador=est, h=h / 1000.0, peso=peso_col or "", unidade=spec["un"], nota=nota)
    fa, fc = fora_por_lado(a, col, h)
    if fa or fc:
        ln["n_fora_abaixo"], ln["n_fora_acima"] = fa, fc
        ln["motivo_fora"] = MOTIVO_TAXA_VI if col == "taxa_vi" else MOTIVO_LOG if col.startswith("log_") and col != "log_pop" else "ausente"
    preencher(ln, r, medias=medias_lados(r, y, peso))
    return ln, r


def linha_poisson(diag, amostra, a, ctx, variante, *, h=H) -> tuple[dict, dict]:
    r = poisson_offset(a, h)
    ln = nova(diag, "estimativa", amostra, ctx["pop"], ctx["ciclo"], ctx["corte"], "N1", "poisson_offset", variante,
              estimador=_est_txt(a, "Poisson local (IRLS do script 23), kernel triangular, offset log(vagas "
                                    "oferecidas): salto em log da taxa por vaga"),
              h=h / 1000.0, peso="", unidade="log (exp(tau) - 1 = variacao relativa da taxa)")
    preencher(ln, r)
    return ln, r


def linha_lc(diag, amostra, a, ctx, outcome, w_mil, *, peso_col=None, variante=None, nota="") -> dict:
    spec = VARIAVEIS[outcome]
    y = a.col(spec["col"])
    peso = a.col(peso_col) if peso_col else None
    if peso is not None:
        peso = np.where(np.isfinite(y), peso, np.nan)
    r = local_constante(a, y, w_mil, peso=peso)
    var = variante or (f"janela_{w_mil / 1000:.3f}_" + ("ponderada" if peso_col else "sem_peso"))
    ln = nova(diag, "estimativa", amostra, ctx["pop"], ctx["ciclo"], ctx["corte"], outcome, "local_constante", var,
              estimador=("diferenca de medias, kernel uniforme em |x| <= janela, intercepto por grupo"
                         + (" (dummies comuns aos dois lados), CR1 por municipio" if a.empilhada else ", EP HC1")
                         + (f", peso = {peso_col}" if peso_col else ", sem peso")),
              h=w_mil / 1000.0, peso=peso_col or "", unidade=spec["un"], nota=nota)
    fa, fc = fora_por_lado(a, spec["col"], w_mil + 0.5)
    if fa or fc:
        ln["n_fora_abaixo"], ln["n_fora_acima"] = fa, fc
        ln["motivo_fora"] = MOTIVO_TAXA_VI
    preencher(ln, r, medias=medias_lados(r, y, peso))
    return ln


# ---------------------------------------------------------------------------
# D1–D5
# ---------------------------------------------------------------------------

D1_OUTCOMES = [("log_pop", None), ("VI", None), ("VIC", None), ("NC", None), ("N1", None),
               ("TAXA_VIC", "vagas_imediatas_mais_cr"), ("TAXA_VI", "vagas_imediatas")]


def d1(amostra, a, ctx, extras) -> list[dict]:
    linhas = []
    for oid, peso in D1_OUTCOMES:
        esp = "taxa_ponderada" if peso else "sem_controle"
        ln, _ = linha_ll("D1", amostra, a, ctx, oid, esp, "principal", peso_col=peso)
        linhas.append(ln)
    ln, _ = linha_ll("D1", amostra, a, ctx, "N1", "controle_protocolo_48", "principal",
                     covs=(("vagas_oferecidas", "vagas_imediatas_mais_cr"),))
    linhas.append(ln)
    # Decomposição log-aditiva: mesma amostra (N1 > 0) e mesmos pesos -> identidade linear exata.
    taus = {}
    for oid in ("LOG_N1", "LOG_VIC", "LOG_TAXA"):
        ln, r = linha_ll("D1", amostra, a, ctx, oid, "log_aditiva", "N1_maior_que_zero")
        taus[oid] = r["tau"]
        linhas.append(ln)
    resid = taus["LOG_N1"] - taus["LOG_VIC"] - taus["LOG_TAXA"]
    if not abs(resid) <= 1e-9:
        raise FalhaValidacao(f"decomposicao log-aditiva nao fecha em {ctx}: {resid}")
    extras["residuos_log"].append(float(resid))
    linhas.append(nova("D1", "identidade", amostra, ctx["pop"], ctx["ciclo"], ctx["corte"], "LOG_N1", "log_aditiva",
                       "identidade", tau=taus["LOG_N1"], contribuicao=taus["LOG_VIC"], tau_grupo=taus["LOG_TAXA"],
                       residuo_identidade=resid, unidade="log",
                       nota="tau = salto em log(N1); contribuicao = salto em log(vagas oferecidas); tau_grupo = salto "
                            "em log(taxa); identidade exata na mesma amostra (N1 > 0) e pesos"))
    return linhas


def faixas(amostra, a, ctx) -> list[dict]:
    x = _x(a)
    dentro = np.abs(x) < H
    d = a.d.assign(x=x)[dentro].copy()
    d["faixa"] = T23._faixas(d["x"].to_numpy())
    linhas = []
    for f, g in d.groupby("faixa", sort=True):
        f = int(f)
        lo, hi = (10 * f, 10 * (f + 1)) if f < 0 else (10 * f, 10 * (f + 1))
        if f < 0:
            lo, hi = 10 * f, 10 * (f + 1)          # (lo, hi] abaixo
        lado = "abaixo" if f < 0 else "acima"
        big = g.sort_values(["populacao_2022", "co_ibge"], ascending=[False, True]).iloc[0]
        linhas.append(nova("D2", "faixa", amostra, ctx["pop"], ctx["ciclo"], ctx["corte"], "faixas", "medias_por_faixa",
                           f"faixa_{f:+d}", faixa=f"{f:+d}", faixa_inf=lo / 1000.0, faixa_sup=hi / 1000.0, lado=lado,
                           n_linhas=len(g), n_municipios=g["co_ibge"].nunique(),
                           pop_media=g["populacao_2022"].mean(), pop_mediana=g["populacao_2022"].median(),
                           vi_media=g["vagas_imediatas"].mean(), vic_media=g["vagas_imediatas_mais_cr"].mean(),
                           nc_media=g["n_celulas"].mean(), n1_media=g["n_alocados_ch1"].mean(),
                           taxa_vic_ponderada=g["n_alocados_ch1"].sum() / g["vagas_imediatas_mais_cr"].sum(),
                           taxa_vic_media_simples=g["taxa_vic"].mean(),
                           taxa_vi_ponderada=(g["n_alocados_ch1"].sum() / g["vagas_imediatas"].sum()
                                              if g["vagas_imediatas"].sum() > 0 else np.nan),
                           maior_municipio=f"{big['co_ibge']} {big['nome_municipio']}",
                           populacao_2022=float(big["populacao_2022"]),
                           unidade="medias simples por linha municipio x ciclo; taxa ponderada = soma N1 / soma vagas",
                           nota=("faixa abaixo: distancia em (faixa_inf, faixa_sup]; acima: [faixa_inf, faixa_sup); "
                                 "distancia = IVS - corte")))
    return linhas


def d2_inclinacoes(amostra, a, ctx) -> list[dict]:
    linhas = []
    y = a.col("n_alocados_ch1")
    for esp, base in (("sem_controle", ()), ("controle_protocolo_48", (("vagas_oferecidas", "vagas_imediatas_mais_cr"),))):
        for var, extra in (("sem_log_pop", ()), ("com_log_pop", (("log_pop", "log_pop"),))):
            covs = base + extra
            r = ajustar(a, y, H, tuple((n, a.col(cc)) for n, cc in covs))
            inc = inclinacoes(r, a)
            ln = nova("D2", "inclinacao", amostra, ctx["pop"], ctx["ciclo"], ctx["corte"], "N1", esp, var,
                      estimador=_est_txt(a, "local linear, kernel triangular" + (
                          f", covariaveis CCFT por grupo: {', '.join(cc for _, cc in covs)}" if covs else "")),
                      h=H / 1000.0, unidade="vagas preenchidas por 0,010 de IVS (inclinacao); tau em vagas",
                      nota="inclinacao do empilhado = media das retas dos ciclos com peso = participacao do ciclo no "
                           "peso de kernel" if a.empilhada else "")
            preencher(ln, r, medias=medias_lados(r, y))
            if inc:
                ln["inclinacao_abaixo"], ln["ep_inclinacao_abaixo"] = inc["abaixo"]
                ln["inclinacao_acima"], ln["ep_inclinacao_acima"] = inc["acima"]
            linhas.append(ln)
    return linhas


def d2_influencia(a, ctx, c) -> tuple[list[dict], dict]:
    """Leave-one-out por município (todas as linhas de ciclo do município saem juntas)."""
    y = a.col("n_alocados_ch1")
    v = a.col("vagas_imediatas_mais_cr")
    x = _x(a)
    dentro = np.abs(x) < H
    base_sa = T23.ajustar(a, y, H, v=v)
    base_p = poisson_offset(a)
    munis = sorted(np.unique(a.cl[dentro]).tolist())
    reg = []
    for m in munis:
        k = a.cl != m
        sub = a.subconjunto(k)
        rs = T23.ajustar(sub, y[k], H, v=v[k])
        rp = poisson_offset(sub)
        linhas_m = a.d[(a.cl == m) & dentro]
        reg.append({"co_ibge": m, "nome": linhas_m["nome_municipio"].iloc[0],
                    "pop": float(linhas_m["populacao_2022"].iloc[0]), "dist": float(x[(a.cl == m)][0] / 1000.0),
                    "vagas": float(linhas_m["vagas_imediatas_mais_cr"].sum()),
                    "n1": float(linhas_m["n_alocados_ch1"].sum()), "ciclos": ",".join(str(int(z)) for z in sorted(linhas_m["ciclo"])),
                    "d_sa": base_sa["tau"] - rs["tau"], "d_p": base_p["tau"] - rp["tau"]})
    df = pd.DataFrame(reg)
    linhas = []
    for esp, col, base in (("S-a", "d_sa", base_sa), ("poisson_offset", "d_p", base_p)):
        ordem = df.assign(ab=df[col].abs()).sort_values(["ab", "co_ibge"], ascending=[False, True]).reset_index(drop=True)
        for i, rr in ordem.iterrows():
            linhas.append(nova("D2", "influencia", POR_CORTE, ctx["pop"], ctx["ciclo"], ctx["corte"], "N1", esp,
                               f"loo_{rr['co_ibge']}", co_ibge=rr["co_ibge"], nome_municipio=rr["nome"],
                               populacao_2022=rr["pop"], vagas_oferecidas_ciclos=rr["vagas"],
                               n_alocados_ciclos=rr["n1"], distancia=rr["dist"],
                               lado="abaixo" if rr["dist"] <= 0 else "acima", delta_tau=rr[col],
                               delta_tau_sobre_ep=rr[col] / base["ep"], posto=i + 1, tau=base["tau"], ep=base["ep"],
                               h=H / 1000.0,
                               unidade="vagas" if esp == "S-a" else "log",
                               nota=f"delta_tau = salto com todos - salto sem o municipio; ciclos do municipio na "
                                    f"janela: {rr['ciclos']}"))
    return linhas, {"n_municipios": len(munis)}


def d2_sem_maiores(a, ctx) -> list[dict]:
    x = _x(a)
    dentro = np.abs(x) < H
    mun = a.d.assign(x=x)[dentro].drop_duplicates("co_ibge")
    linhas = []
    for kk in KS:
        for qual in ("abaixo", "acima", "dois_lados"):
            tirar = []
            for lado in (("abaixo", "acima") if qual == "dois_lados" else (qual,)):
                m = mun[(mun["x"] <= 0) if lado == "abaixo" else (mun["x"] > 0)]
                tirar += m.sort_values(["populacao_2022", "co_ibge"], ascending=[False, True])["co_ibge"].head(kk).tolist()
            sub = a.subconjunto(~np.isin(a.cl, tirar))
            nomes = ", ".join(f"{c} {mun.set_index('co_ibge').loc[c, 'nome_municipio']}" for c in tirar)
            var = f"sem_{kk}_maiores_{qual}"
            for oid, esp, covs, peso in (("N1", "controle_protocolo_48", (("vagas_oferecidas", "vagas_imediatas_mais_cr"),), None),
                                         ("N1", "sem_controle", (), None),
                                         ("TAXA_VIC", "taxa_ponderada", (), "vagas_imediatas_mais_cr")):
                ln, _ = linha_ll("D2", POR_CORTE, sub, ctx, oid, esp, var, covs=covs, peso_col=peso)
                ln.update({"tipo_linha": "sem_maiores", "k_retirados": kk, "retirados": nomes,
                           "id_linha": ln["id_linha"].replace("|estimativa|", "|sem_maiores|")})
                linhas.append(ln)
            ln, _ = linha_poisson("D2", POR_CORTE, sub, ctx, var)
            ln.update({"tipo_linha": "sem_maiores", "k_retirados": kk, "retirados": nomes,
                       "id_linha": ln["id_linha"].replace("|estimativa|", "|sem_maiores|")})
            linhas.append(ln)
    return linhas


def d3(amostra, a, ctx) -> list[dict]:
    linhas = []
    for h in H_D3:
        linhas.append(linha_poisson("D3", amostra, a, ctx, f"h={h / 1000:.3f}", h=h)[0])
        for oid, peso in (("TAXA_VIC", "vagas_imediatas_mais_cr"), ("TAXA_VI", "vagas_imediatas")):
            linhas.append(linha_ll("D3", amostra, a, ctx, oid, "taxa_ponderada_local_linear", f"h={h / 1000:.3f}", h=h,
                                   peso_col=peso)[0])
    for w in JANELAS_LC + (JANELA_LC_ADENDO,):
        nota = "ADENDO AD1 (2026-10-21): janela inteira |x| < 0,050" if w == JANELA_LC_ADENDO else ""
        for oid, peso in (("TAXA_VIC", "vagas_imediatas_mais_cr"), ("TAXA_VI", "vagas_imediatas")):
            for p in (peso, None):
                ln = linha_lc("D3", amostra, a, ctx, oid, w, peso_col=p, nota=nota)
                if w == JANELA_LC_ADENDO:
                    ln["adendo"] = "AD1"
                    ln["especificacao"] = "local_constante_adendo_AD1"
                    ln["id_linha"] = ln["id_linha"].replace("|local_constante|", "|local_constante_adendo_AD1|")
                linhas.append(ln)
    for oid, esp, covs, peso in (("TAXA_VIC", "taxa_ponderada", (), "vagas_imediatas_mais_cr"),
                                 ("TAXA_VI", "taxa_ponderada", (), "vagas_imediatas"),
                                 ("N1", "sem_controle", (), None),
                                 ("N1", "controle_protocolo_48", (("vagas_oferecidas", "vagas_imediatas_mais_cr"),), None)):
        ln, _ = linha_ll("D3", amostra, a, ctx, oid, f"local_quadratico_{esp}", f"h={H_QUAD / 1000:.3f}", h=H_QUAD,
                         covs=covs, peso_col=peso, quad=True)
        linhas.append(ln)
    ln = nova("D3", "estimativa", amostra, ctx["pop"], ctx["ciclo"], ctx["corte"], "TAXA_VIC", "rdrobust_h_otimo",
              "nao_executado", status="NAO_EXECUTADO", nota=MOTIVO_RDROBUST)
    linhas.append(ln)
    return linhas


def d4(amostra, a, ctx) -> list[dict]:
    linhas = []
    for esp, covs in (("sem_controle", ()), ("log_pop", (("log_pop", "log_pop"),)),
                      ("log_pop_mais_vagas_imediatas", (("log_pop", "log_pop"), ("vagas_imediatas", "vagas_imediatas"))),
                      ("controle_protocolo_48", (("vagas_oferecidas", "vagas_imediatas_mais_cr"),))):
        linhas.append(linha_ll("D4", amostra, a, ctx, "N1", esp, "principal", covs=covs)[0])
    linhas.append(linha_ll("D4", amostra, a, ctx, "N1_POR_VAGA", "sem_peso", "principal")[0])
    return linhas


def d5(V: dict, extras: dict) -> list[dict]:
    linhas = []
    ae = amostra_empilhada(V)
    for esp, covs in (("sem_controle", ()), ("controle_protocolo_48", (("vagas_oferecidas", "vagas_imediatas_mais_cr"),))):
        # (i) ciclos e cortes empilhados; (ii) dentro de cada corte (ciclos juntos).
        for nome_am, a, grupos in [(EMP, ae, [(k, c) for k in CICLOS for c in CORTES])] + \
                [(POR_CORTE, amostra_corte(V, c), [(k, c) for k in CICLOS]) for c in CORTES]:
            r = ajustar(a, a.col("n_alocados_ch1"), H, tuple((n, a.col(cc)) for n, cc in covs))
            ctx = {"pop": "V1+V2+V3", "ciclo": "1+2+3",
                   "corte": EMPILHADO if nome_am == EMP else ROTULO_CORTE[grupos[0][1]]}
            soma = 0.0
            for k, c in grupos:
                gl = f"c{k}_{c}" if nome_am == EMP else f"c{k}"
                om = r["pesos_grupos"][gl]
                rg = ajustar(amostra_ciclo(V, k, c), V[k]["n_alocados_ch1"].to_numpy(dtype=float), H,
                             tuple((n, V[k][cc].to_numpy(dtype=float)) for n, cc in covs))
                soma += om * rg["tau"]
                linhas.append(nova("D5", "contribuicao", nome_am, ctx["pop"], ctx["ciclo"], ctx["corte"], "N1", esp,
                                   f"grupo_c{k}_{c}", grupo=f"ciclo {k}, corte {ROTULO_CORTE[c]}", peso_omega=om,
                                   tau_grupo=rg["tau"], contribuicao=om * rg["tau"], tau=r["tau"], ep=r["ep"],
                                   ic95_inf=rg["ic95_inf"], ic95_sup=rg["ic95_sup"], p_valor=rg["p_valor"],
                                   n_abaixo=rg["n_abaixo"], n_acima=rg["n_acima"], h=H / 1000.0, unidade="vagas",
                                   nota="tau/ep = salto empilhado; tau_grupo e IC/p = local linear so do ciclo x corte "
                                        "(HC1); contribuicao = omega x tau_grupo"))
            resid = r["tau"] - soma
            if not abs(resid) <= 1e-8 * max(1.0, abs(r["tau"])):
                raise FalhaValidacao(f"identidade omega nao fecha em {nome_am} {ctx} {esp}: {resid}")
            extras["residuos_omega"].append(float(resid))
            linhas.append(nova("D5", "identidade", nome_am, ctx["pop"], ctx["ciclo"], ctx["corte"], "N1", esp,
                               "soma_das_contribuicoes", tau=r["tau"], ep=r["ep"], ic95_inf=r["ic95_inf"],
                               ic95_sup=r["ic95_sup"], p_valor=r["p_valor"], contribuicao=soma,
                               residuo_identidade=resid, h=H / 1000.0, unidade="vagas",
                               nota="salto empilhado = soma omega_g x salto do grupo (Frisch-Waugh-Lovell; grupos com "
                                    "parametros proprios exceto o salto)"))
    return linhas


# ---------------------------------------------------------------------------
# Adendo AD2 (21/10/2026): por que a taxa por vaga oferecida cai em 0,300
# ---------------------------------------------------------------------------

ADENDO2 = "AD2"
ADENDO2_DATA = "2026-10-21"
ADENDO2_DESC = {
    "id": ADENDO2, "data": ADENDO2_DATA,
    "pergunta": "por que a taxa de preenchimento por vaga oferecida cai no corte 0,300, onde o porte nao explica a "
                "queda",
    "ja_visto": "antes deste adendo ja estavam gravados e lidos: o salto de -16 p.p. da taxa ponderada pelas vagas "
                "oferecidas no local linear (D1, corte 0,300) e a dependencia da medida (com as vagas imediatas no "
                "denominador, e com cada municipio pesando igual em +-0,010, o IC contem zero; D3)",
    "conjunto_fixo": [
        {"id": "A1", "nome": "cadastro reserva",
         "itens": ["saltos na fracao de vagas de cadastro reserva sobre as vagas oferecidas (peso = vagas oferecidas), "
                   "no n de vagas de CR e no n de vagas imediatas",
                   "taxa de preenchimento separada: alocados em vaga imediata / vagas imediatas e alocados em CR / "
                   "vagas de CR, se a base distinguir; se nao distinguir, a ausencia e o motivo"]},
        {"id": "A2", "nome": "decomposicao da diferenca entre as taxas",
         "itens": ["no corte 0,300, quanto do salto vem de trocar o denominador (imediatas -> imediatas + CR) e quanto "
                   "de trocar o peso (municipio -> vaga), mesma janela e especificacao, um elemento por vez, nas duas "
                   "ordens; a restricao a municipios com vaga imediata (exigida pelo denominador de imediatas) e "
                   "relatada como passo proprio"]},
        {"id": "A3", "nome": "por ciclo",
         "itens": ["taxa ponderada pelas vagas oferecidas, taxa so com vagas imediatas e fracao de CR, ciclo x corte, "
                   "EP HC1", "peso efetivo omega e contribuicao de cada ciclo no salto da taxa com os ciclos juntos"]},
        {"id": "A4", "nome": "influencia no nivel da vaga",
         "itens": ["os 5 municipios com mais vagas oferecidas (soma dos ciclos) na janela de 0,300, com vagas "
                   "imediatas, CR, alocados, lado e nome, e o salto da taxa ponderada sem cada um deles"]},
    ],
    "especificacao": "a do ND: local linear, h = 0,050, kernel triangular, CR1 por municipio, ciclos juntos com "
                     "intercepto e inclinacao por ciclo; por corte (0,300 e 0,400, este como contraste)",
}
MOTIVO_SEPARADA = ("a base nao registra em que tipo de vaga (imediata ou cadastro reserva) cada alocado entrou; so e "
                   "possivel separar nas celulas puras: celula so com vagas imediatas (todo alocado ocupa vaga "
                   "imediata ou entrou acima delas) e celula so de cadastro reserva (todo alocado ocupa vaga de CR). "
                   "As celulas mistas (imediatas e CR na mesma celula) ficam fora das duas taxas separadas, contadas, "
                   "nunca divididas por suposicao")
N_TOP_VAGA = 5


def agregar_celulas(cel: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Por município × ciclo: vagas e alocados nas células só de imediatas, só de CR e mistas (contagens observadas)."""
    c = cel.copy()
    vi, vcr = c["vagas_imediatas"].astype(float), c["vagas_cr"].astype(float)
    c["tipo"] = np.where((vi > 0) & (vcr > 0), "mista", np.where(vi > 0, "so_imed", "so_cr"))
    out = c.pivot_table(index=["ciclo", "co_ibge"], columns="tipo",
                        values=["vagas_imediatas", "vagas_cr", "n_alocados_ch1"], aggfunc="sum", fill_value=0)
    out.columns = [f"{a}_{b}" for a, b in out.columns]
    for col in [f"{a}_{b}" for a in ("vagas_imediatas", "vagas_cr", "n_alocados_ch1") for b in ("so_imed", "so_cr", "mista")]:
        if col not in out:
            out[col] = 0.0
    out = out.reset_index()
    tot = c.groupby(["ciclo", "tipo"]).agg(celulas=("tipo", "size"), vagas_imediatas=("vagas_imediatas", "sum"),
                                           vagas_cr=("vagas_cr", "sum"), alocados=("n_alocados_ch1", "sum"))
    info = {f"ciclo {k} / {t}": {kk: float(v) for kk, v in r.items()} for (k, t), r in tot.iterrows()}
    return out, info


def preparar_adendo2(V: dict[int, pd.DataFrame], agg: pd.DataFrame) -> dict[int, pd.DataFrame]:
    out = {}
    for k, d in V.items():
        a = agg[agg["ciclo"] == k].drop(columns="ciclo")
        d = d.merge(a, on="co_ibge", how="left", validate="one_to_one")
        cols = [c for c in a.columns if c != "co_ibge"]
        if d[cols].isna().any().any():
            raise FalhaValidacao(f"V{k}: municipio do quadro sem celula no arquivo de celulas")
        soma_vi = d[["vagas_imediatas_so_imed", "vagas_imediatas_mista"]].sum(axis=1)
        soma_cr = d[["vagas_cr_so_cr", "vagas_cr_mista"]].sum(axis=1)
        soma_al = d[["n_alocados_ch1_so_imed", "n_alocados_ch1_so_cr", "n_alocados_ch1_mista"]].sum(axis=1)
        if (np.abs(soma_vi - d["vagas_imediatas"]) > 1e-9).any() or (np.abs(soma_cr - d["vagas_cr"]) > 1e-9).any() \
                or (np.abs(soma_al - d["n_alocados_ch1"]) > 1e-9).any():
            raise FalhaValidacao(f"V{k}: soma das celulas difere do municipio")
        d["vagas_cr_f"] = d["vagas_cr"].astype(float)
        d["frac_cr"] = d["vagas_cr_f"] / d["vagas_imediatas_mais_cr"]
        vsi, vsc = d["vagas_imediatas_so_imed"].astype(float), d["vagas_cr_so_cr"].astype(float)
        d["vagas_so_imed"], d["vagas_so_cr"] = vsi, vsc
        d["taxa_so_imed"] = np.where(vsi > 0, d["n_alocados_ch1_so_imed"] / np.where(vsi > 0, vsi, 1.0), np.nan)
        d["taxa_so_cr"] = np.where(vsc > 0, d["n_alocados_ch1_so_cr"] / np.where(vsc > 0, vsc, 1.0), np.nan)
        d["tem_vi"] = (d["vagas_imediatas"] > 0).astype(float)
        out[k] = d
    return out


VARIAVEIS.update({
    "FRAC_CR": {"col": "frac_cr", "desc": "vagas de cadastro reserva / vagas oferecidas, peso = vagas oferecidas",
                "un": "fracao (x100 = p.p.)", "peso": "vagas_imediatas_mais_cr"},
    "CR": {"col": "vagas_cr_f", "desc": "vagas de cadastro reserva no quadro da 1a chamada", "un": "vagas por municipio"},
    "TAXA_SO_IMED": {"col": "taxa_so_imed", "desc": "alocados / vagas nas celulas so de vagas imediatas, peso = essas "
                     "vagas", "un": "fracao (x100 = p.p.)", "peso": "vagas_so_imed"},
    "TAXA_SO_CR": {"col": "taxa_so_cr", "desc": "alocados / vagas nas celulas so de cadastro reserva, peso = essas "
                   "vagas", "un": "fracao (x100 = p.p.)", "peso": "vagas_so_cr"},
})


def _ad2(ln: dict, diag: str, tipo: str | None = None) -> dict:
    ln["adendo"] = ADENDO2
    partes = ln["id_linha"].split("|")
    partes[0] = diag
    if tipo:
        partes[1] = tipo
        ln["tipo_linha"] = tipo
    ln["diagnostico"] = diag
    ln["id_linha"] = "|".join(partes)
    return ln


def ad2_a1(amostra, a, ctx) -> list[dict]:
    linhas = []
    for oid, peso in (("FRAC_CR", "vagas_imediatas_mais_cr"), ("CR", None), ("VI", None),
                      ("TAXA_SO_IMED", "vagas_so_imed"), ("TAXA_SO_CR", "vagas_so_cr")):
        esp = "taxa_ponderada" if peso else "sem_controle"
        ln, _ = linha_ll("AD2_A1", amostra, a, ctx, oid, esp, "principal", peso_col=peso)
        if oid.startswith("TAXA_SO"):
            ln["nota"] = _juntar(ln["nota"], "separacao parcial: " + MOTIVO_SEPARADA)
            if ln["motivo_fora"] == "ausente":
                ln["motivo_fora"] = "municipio sem celula pura desse tipo: taxa indefinida (nunca zero)"
        linhas.append(_ad2(ln, "AD2_A1"))
    return linhas


A2_CELULAS = [  # (nome, outcome, peso, so municipios com vaga imediata)
    ("vic_vaga_todos", "TAXA_VIC", "vagas_imediatas_mais_cr", False),
    ("vic_vaga_com_vi", "TAXA_VIC", "vagas_imediatas_mais_cr", True),
    ("vi_vaga_com_vi", "TAXA_VI", "vagas_imediatas", True),
    ("vic_municipio_todos", "TAXA_VIC", None, False),
    ("vic_municipio_com_vi", "TAXA_VIC", None, True),
    ("vi_municipio_com_vi", "TAXA_VI", None, True),
]


def ad2_a2(a, ctx) -> list[dict]:
    linhas, tau = [], {}
    for nome, oid, peso, so_vi in A2_CELULAS:
        sub = a.subconjunto(a.col("vagas_imediatas") > 0) if so_vi else a
        ln, r = linha_ll("AD2_A2", POR_CORTE, sub, ctx, oid, "taxa_2x2", nome, peso_col=peso)
        ln["nota"] = _juntar(ln["nota"], ("amostra: so municipios x ciclo com vaga imediata" if so_vi else
                                          "amostra: todos os municipios x ciclo do quadro"),
                             "peso = vagas" if peso else "peso = municipio (sem peso)")
        tau[nome] = r["tau"]
        linhas.append(_ad2(ln, "AD2_A2"))
    # Caminhos de um elemento por vez, do salto principal (VIC, vaga, todos) até a taxa so com imediatas por município.
    caminhos = {
        "ordem_denominador_primeiro": [("amostra (so com vaga imediata)", "vic_vaga_todos", "vic_vaga_com_vi"),
                                       ("denominador (imediatas + CR -> imediatas)", "vic_vaga_com_vi", "vi_vaga_com_vi"),
                                       ("peso (vaga -> municipio)", "vi_vaga_com_vi", "vi_municipio_com_vi")],
        "ordem_peso_primeiro": [("peso (vaga -> municipio)", "vic_vaga_todos", "vic_municipio_todos"),
                                ("amostra (so com vaga imediata)", "vic_municipio_todos", "vic_municipio_com_vi"),
                                ("denominador (imediatas + CR -> imediatas)", "vic_municipio_com_vi", "vi_municipio_com_vi")],
    }
    for ordem, passos in caminhos.items():
        for i, (rot, de, para) in enumerate(passos, 1):
            ln = nova("AD2_A2", "decomposicao", POR_CORTE, ctx["pop"], ctx["ciclo"], ctx["corte"], "TAXA", ordem,
                      f"passo_{i}", grupo=rot, tau_grupo=tau[de], tau=tau[para], contribuicao=tau[para] - tau[de],
                      posto=i, unidade="fracao (x100 = p.p.)", h=H / 1000.0, adendo=ADENDO2,
                      nota=f"de {de} para {para}; contribuicao = salto depois - salto antes")
            linhas.append(ln)
    return linhas


def ad2_a3(V, extras) -> list[dict]:
    linhas = []
    for k in CICLOS:
        for c in CORTES:
            a = amostra_ciclo(V, k, c)
            ctx = _ctx(APENDICE, a, k=k, c=c)
            for oid, peso in (("TAXA_VIC", "vagas_imediatas_mais_cr"), ("TAXA_VI", "vagas_imediatas"),
                              ("FRAC_CR", "vagas_imediatas_mais_cr")):
                ln, _ = linha_ll("AD2_A3", APENDICE, a, ctx, oid, "taxa_ponderada", "principal", peso_col=peso)
                linhas.append(_ad2(ln, "AD2_A3"))
    for c in CORTES:
        a = amostra_corte(V, c)
        ctx = _ctx(POR_CORTE, a, c=c)
        for oid, peso in (("TAXA_VIC", "vagas_imediatas_mais_cr"), ("TAXA_VI", "vagas_imediatas")):
            col = VARIAVEIS[oid]["col"]
            y = a.col(col)
            pw = np.where(np.isfinite(y), a.col(peso), np.nan)
            r = ajustar(a, y, H, peso=pw)
            soma = 0.0
            for k in CICLOS:
                om = r["pesos_grupos"][f"c{k}"]
                ak = amostra_ciclo(V, k, c)
                yk = ak.col(col)
                rg = ajustar(ak, yk, H, peso=np.where(np.isfinite(yk), ak.col(peso), np.nan))
                soma += om * rg["tau"]
                linhas.append(nova("AD2_A3", "contribuicao", POR_CORTE, ctx["pop"], ctx["ciclo"], ctx["corte"], oid,
                                   "taxa_ponderada", f"grupo_c{k}", grupo=f"ciclo {k}", peso_omega=om,
                                   tau_grupo=rg["tau"], contribuicao=om * rg["tau"], tau=r["tau"], ep=r["ep"],
                                   ic95_inf=rg["ic95_inf"], ic95_sup=rg["ic95_sup"], p_valor=rg["p_valor"],
                                   n_abaixo=rg["n_abaixo"], n_acima=rg["n_acima"], h=H / 1000.0, adendo=ADENDO2,
                                   peso=peso, unidade="fracao (x100 = p.p.)",
                                   nota="tau/ep = salto com os ciclos juntos; tau_grupo e IC/p = so o ciclo (HC1); "
                                        "contribuicao = omega x tau_grupo"))
            resid = r["tau"] - soma
            if not abs(resid) <= 1e-8 * max(1.0, abs(r["tau"])):
                raise FalhaValidacao(f"identidade omega da taxa nao fecha em {c} {oid}: {resid}")
            extras["residuos_omega_ad2"].append(float(resid))
            linhas.append(nova("AD2_A3", "identidade", POR_CORTE, ctx["pop"], ctx["ciclo"], ctx["corte"], oid,
                               "taxa_ponderada", "soma_das_contribuicoes", tau=r["tau"], ep=r["ep"],
                               ic95_inf=r["ic95_inf"], ic95_sup=r["ic95_sup"], p_valor=r["p_valor"], contribuicao=soma,
                               residuo_identidade=resid, h=H / 1000.0, adendo=ADENDO2, peso=peso,
                               unidade="fracao (x100 = p.p.)"))
    return linhas


def ad2_a4(a, ctx) -> list[dict]:
    x = _x(a)
    dentro = np.abs(x) < H
    d = a.d.assign(x=x)[dentro]
    por_mun = d.groupby("co_ibge").agg(vic=("vagas_imediatas_mais_cr", "sum"), vi=("vagas_imediatas", "sum"),
                                       cr=("vagas_cr_f", "sum"), n1=("n_alocados_ch1", "sum"), x=("x", "first"),
                                       nome=("nome_municipio", "first"), pop=("populacao_2022", "first"),
                                       ciclos=("ciclo", lambda s: ",".join(str(int(z)) for z in sorted(s))))
    top = por_mun.reset_index().sort_values(["vic", "co_ibge"], ascending=[False, True]).head(N_TOP_VAGA)
    y = a.col("taxa_vic")
    base = ajustar(a, y, H, peso=a.col("vagas_imediatas_mais_cr"))
    linhas = []
    for i, rr in enumerate(top.itertuples(), 1):
        k = a.cl != rr.co_ibge
        sub = a.subconjunto(k)
        r = ajustar(sub, y[k], H, peso=sub.col("vagas_imediatas_mais_cr"))
        ln = nova("AD2_A4", "influencia_vaga", POR_CORTE, ctx["pop"], ctx["ciclo"], ctx["corte"], "TAXA_VIC",
                  "taxa_ponderada", f"sem_{rr.co_ibge}", co_ibge=rr.co_ibge, nome_municipio=rr.nome,
                  populacao_2022=rr.pop, vagas_oferecidas_ciclos=rr.vic, n_alocados_ciclos=rr.n1,
                  vagas_imediatas_ciclos=rr.vi, vagas_cr_ciclos=rr.cr, distancia=rr.x / 1000.0, lado="abaixo" if rr.x <= 0 else "acima",
                  posto=i, tau=r["tau"], ep=r["ep"], ic95_inf=r["ic95_inf"], ic95_sup=r["ic95_sup"], p_valor=r["p_valor"],
                  n_abaixo=r["n_abaixo"], n_acima=r["n_acima"], delta_tau=base["tau"] - r["tau"],
                  delta_tau_sobre_ep=(base["tau"] - r["tau"]) / base["ep"], h=H / 1000.0, adendo=ADENDO2,
                  peso="vagas_imediatas_mais_cr", unidade="fracao (x100 = p.p.)",
                  nota=f"ciclos na janela: {rr.ciclos}; tau = salto da taxa ponderada sem o municipio; delta_tau = "
                       f"salto com todos - salto sem ele")
        linhas.append(ln)
    return linhas


def faixas_adendo2(a, ctx) -> list[dict]:
    """Por faixa de 0,010: fração de CR (soma CR / soma vagas) e as duas taxas ponderadas (para a figura do adendo)."""
    x = _x(a)
    d = a.d.assign(x=x)[np.abs(x) < H].copy()
    d["faixa"] = T23._faixas(d["x"].to_numpy())
    linhas = []
    for f, g in d.groupby("faixa", sort=True):
        f = int(f)
        lo, hi = 10 * f, 10 * (f + 1)
        vi = g["vagas_imediatas"].sum()
        linhas.append(nova("AD2_A1", "faixa_cr", POR_CORTE, ctx["pop"], ctx["ciclo"], ctx["corte"], "faixas_cr",
                           "medias_por_faixa", f"faixa_{f:+d}", faixa=f"{f:+d}", faixa_inf=lo / 1000.0,
                           faixa_sup=hi / 1000.0, lado="abaixo" if f < 0 else "acima", n_linhas=len(g),
                           n_municipios=g["co_ibge"].nunique(), vi_media=g["vagas_imediatas"].mean(),
                           vic_media=g["vagas_imediatas_mais_cr"].mean(), n1_media=g["n_alocados_ch1"].mean(),
                           taxa_vic_ponderada=g["n_alocados_ch1"].sum() / g["vagas_imediatas_mais_cr"].sum(),
                           taxa_vi_ponderada=g["n_alocados_ch1"].sum() / vi if vi > 0 else np.nan,
                           fracao_cr=g["vagas_cr_f"].sum() / g["vagas_imediatas_mais_cr"].sum(),
                           adendo=ADENDO2, unidade="taxas ponderadas = soma N1 / soma vagas; fracao_cr = soma CR / "
                                                   "soma vagas oferecidas",
                           nota="faixa abaixo: (faixa_inf, faixa_sup]; acima: [faixa_inf, faixa_sup)"))
    return linhas


def estimar_adendo2(V: dict, extras: dict) -> list[dict]:
    linhas = []
    for c in CORTES:
        a = amostra_corte(V, c)
        ctx = _ctx(POR_CORTE, a, c=c)
        linhas += ad2_a1(POR_CORTE, a, ctx)
        linhas += faixas_adendo2(a, ctx)
        linhas += ad2_a2(a, ctx)
        if c == 300:
            linhas += ad2_a4(a, ctx)
    linhas += ad2_a3(V, extras)
    return linhas


# ---------------------------------------------------------------------------
# Orquestração
# ---------------------------------------------------------------------------

def estimar_tudo(V: dict, log=print) -> tuple[pd.DataFrame, dict]:
    extras = {"residuos_log": [], "residuos_omega": [], "influencia": {}, "residuos_omega_ad2": []}
    linhas: list[dict] = []
    for c in CORTES:
        a = amostra_corte(V, c)
        ctx = _ctx(POR_CORTE, a, c=c)
        linhas += d1(POR_CORTE, a, ctx, extras)
        linhas += faixas(POR_CORTE, a, ctx)
        linhas += d2_inclinacoes(POR_CORTE, a, ctx)
        li, info = d2_influencia(a, ctx, c)
        linhas += li
        extras["influencia"][ROTULO_CORTE[c]] = info
        linhas += d2_sem_maiores(a, ctx)
        linhas += d3(POR_CORTE, a, ctx)
        linhas += d4(POR_CORTE, a, ctx)
        log(f"  corte {ROTULO_CORTE[c]}: {len(linhas)} linhas")
    for k in CICLOS:
        for c in CORTES:
            a = amostra_ciclo(V, k, c)
            ctx = _ctx(APENDICE, a, k=k, c=c)
            linhas += d1(APENDICE, a, ctx, extras)
            linhas += d4(APENDICE, a, ctx)
    log(f"  apendice por ciclo: {len(linhas)} linhas")
    ae = amostra_empilhada(V)
    ctx = _ctx(EMP, ae)
    linhas += d1(EMP, ae, ctx, extras)
    linhas += faixas(EMP, ae, ctx)
    linhas += d2_inclinacoes(EMP, ae, ctx)
    linhas += d3(EMP, ae, ctx)
    linhas += d4(EMP, ae, ctx)
    linhas += d5(V, extras)
    log(f"  empilhado e D5: {len(linhas)} linhas")
    linhas += estimar_adendo2(V, extras)
    log(f"  adendo AD2: {len(linhas)} linhas")
    est = pd.DataFrame(linhas)[COLUNAS]
    if est["id_linha"].duplicated().any():
        raise FalhaValidacao(f"id_linha duplicado: {est.loc[est['id_linha'].duplicated(), 'id_linha'].tolist()[:5]}")
    return est, extras


def conferir_doc49(est: pd.DataFrame) -> dict:
    """As linhas por corte e empilhadas que existem no N_estimativas.csv têm de ser reproduzidas aqui."""
    n = pd.read_csv(N_EST, dtype={"corte": str, "ciclo": str})
    pares = [("D4", "N1", "sem_controle", "S-b", "principal"), ("D4", "N1", "controle_protocolo_48", "S-a", "principal"),
             ("D3", "N1", "poisson_offset", "S-d", "log_controle_offset"),
             ("D1", "TAXA_VIC", "taxa_ponderada", "S-e", "fracao_ponderada_pelo_controle")]
    conf, maxdif = [], 0.0
    for diag, oid, esp, esp_n, var_n in pares:
        for corte in [ROTULO_CORTE[c] for c in CORTES] + [EMPILHADO]:
            am = EMP if corte == EMPILHADO else POR_CORTE
            var = "h=0.050" if esp == "poisson_offset" else "principal"
            sel = est[(est["diagnostico"] == diag) & (est["amostra"] == am) & (est["corte"] == corte)
                      & (est["outcome"] == oid) & (est["especificacao"] == esp) & (est["variante"] == var)
                      & (est["tipo_linha"] == "estimativa")]
            alvo = n[(n["outcome_id"] == "N1") & (n["populacao"] == "V1+V2+V3") & (n["corte"] == corte)
                     & (n["especificacao"] == esp_n) & (n["variante"] == var_n)]
            if len(sel) != 1 or len(alvo) != 1:
                raise FalhaValidacao(f"conferencia com o doc 49: {diag} {esp} {corte}: {len(sel)} / {len(alvo)} linhas")
            for k in ("tau", "ep"):
                dif = abs(float(sel[k].iloc[0]) - float(alvo[k].iloc[0]))
                maxdif = max(maxdif, dif)
                if dif > 1e-9:
                    raise FalhaValidacao(f"{diag} {esp} {corte} {k} diverge do N_estimativas.csv: {dif}")
            conf.append(f"{esp_n} {var_n} {corte}")
    return {"linhas_conferidas": conf, "max_abs_dif": maxdif}


# ---------------------------------------------------------------------------
# Figuras
# ---------------------------------------------------------------------------

COR_AB = "#2a78d6"
COR_AC = "#eb6834"
TINTA = T23.TINTA
TINTA_2 = "#52514e"
SUPERF = T23.SUPERFICIE


def _fx(v, _=None) -> str:
    return f"{v:+.3f}".replace(".", ",").replace("-", "−") if abs(v) > 1e-12 else "0"


def _num(v, casas=2, sinal=True) -> str:
    if v is None or (isinstance(v, float) and not math.isfinite(v)):
        return "—"
    if round(v, casas) == 0:
        v = 0.0                      # sem "−0,0"
    return (f"{v:+.{casas}f}" if sinal else f"{v:.{casas}f}").replace("-", "−").replace(".", ",")


TAMANHO_FIG = (12.8, 7.2)      # 16:9, dois painéis lado a lado (um por corte)

# "Como ler" de cada figura: 1 a 2 frases curtas, sem jargão (regra do autor). Vai no ND_resumo.json e no doc 49b,
# abaixo da imagem; nunca dentro da imagem. O detalhe técnico fica em DETALHE_FIG, só no doc.
COMO_LER = {
    "ND_faixas_populacao.png": "Cada ponto é o tamanho típico dos municípios num trecho de distância ao corte. Perto "
                               "do corte, do lado de bolsa menor, a média fica muito acima da mediana: ali há poucas "
                               "cidades muito grandes.",
    "ND_faixas_vagas.png": "Cada ponto é o número médio de vagas oferecidas por município num trecho de distância ao "
                           "corte. Mostra se um lado do corte simplesmente abriu mais vagas.",
    "ND_faixas_N1.png": "Cada ponto é o número médio de vagas preenchidas por município num trecho de distância ao "
                        "corte. Ele sobe e desce junto com o tamanho das cidades e com as vagas abertas, por isso não "
                        "mede atração.",
    "ND_faixas_taxa.png": "Cada ponto é a parte das vagas oferecidas que foi preenchida num trecho de distância ao "
                          "corte. Círculos contam cada vaga igual; quadrados contam cada município igual.",
    "ND_influencia_Sa.png": "Cada ponto é um município: a altura mostra quanto o salto no corte muda se ele for "
                            "retirado. Pontos perto de zero, sem nenhum isolado, querem dizer que o salto não depende "
                            "de uma cidade só.",
    "ND_influencia_poisson.png": "O mesmo que a figura anterior, para a taxa de preenchimento por vaga. Pontos perto "
                                 "de zero querem dizer que nenhuma cidade sozinha decide o resultado.",
    "ND_taxa_janelas.png": "Cada linha é uma forma diferente de medir o salto na taxa de preenchimento no corte, com "
                           "seu intervalo de confiança. Se as linhas mudam de lado do zero conforme a forma, o salto "
                           "não é nítido.",
    "ND_poisson_janelas.png": "Cada linha mede o salto na taxa de preenchimento por vaga usando um trecho mais "
                              "estreito ou mais largo em volta do corte. Resultados que mudam muito com o trecho pedem "
                              "cautela.",
}
DETALHE_FIG = {
    "ND_faixas_populacao.png": "Média e mediana da população do Censo 2022 por faixa de 0,010 da distância ao corte, "
                               "linhas município × ciclo da janela (|distância| < 0,050), ciclos 1–3 juntos; eixo "
                               "vertical em escala log. A anotação traz o salto local linear em log(pop) (POR_CORTE).",
    "ND_faixas_vagas.png": "Média das vagas oferecidas (imediatas + cadastro reserva, forma do controle do protocolo 48) "
                           "e das vagas imediatas por faixa; anotação = salto local linear nas vagas oferecidas.",
    "ND_faixas_N1.png": "Média de N1 por faixa (linhas município × ciclo); anotação = salto local linear de N1 sem "
                        "controle (POR_CORTE, h = 0,050, kernel triangular, CR1 por município).",
    "ND_faixas_taxa.png": "Taxa ponderada = soma de N1 / soma das vagas oferecidas na faixa; média simples = média das "
                          "razões municipais. Anotação = salto local linear da taxa ponderada (peso = kernel × vagas).",
    "ND_influencia_Sa.png": "Leave-one-out por município (todas as linhas de ciclo saem juntas) do salto de N1 com o "
                            "controle do protocolo 48, POR_CORTE; nome dos três mais influentes.",
    "ND_influencia_poisson.png": "Leave-one-out do Poisson local com offset log(vagas oferecidas), POR_CORTE; salto em "
                                 "log.",
    "ND_taxa_janelas.png": "Saltos da taxa N1 / vagas oferecidas em p.p.: local linear ponderado com h de 0,020 a "
                           "0,080, local constante em ±0,010, ±0,020, ±0,030 e ±0,050 (adendo AD1), ponderado e sem "
                           "peso, e local quadrático com h = 0,080; IC 95% CR1 por município.",
    "ND_poisson_janelas.png": "Poisson local com offset log(vagas oferecidas), h = 0,020; 0,030; 0,050; 0,080; salto em "
                              "log com IC 95% CR1 por município.",
}


def gerar_figuras(est: pd.DataFrame, dir_fig: Path) -> list[dict]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter
    dir_fig.mkdir(parents=True, exist_ok=True)
    for antigo in dir_fig.glob("*.png"):
        antigo.unlink()
    feitas = []
    fx = est[(est["tipo_linha"] == "faixa") & (est["amostra"] == POR_CORTE)].copy()
    fx["meio"] = (fx["faixa_inf"].astype(float) + fx["faixa_sup"].astype(float)) / 2

    def salvar(fig, nome, fonte):
        fig.savefig(dir_fig / nome, dpi=110, facecolor=fig.get_facecolor())
        plt.close(fig)
        feitas.append({"arquivo": rotulo(dir_fig / nome), "fonte": fonte, "como_ler": COMO_LER[nome]})

    def anotar(ax, txt):
        ax.text(0.02, 0.97, txt, transform=ax.transAxes, fontsize=8.5, va="top", ha="left", color=TINTA,
                bbox={"boxstyle": "round,pad=0.25", "fc": "white", "ec": "#d0cfca", "lw": 0.6})

    def salto_d1(c, oid, esp, pct=False, casas=2):
        r = _sel(est, diagnostico="D1", tipo_linha="estimativa", amostra=POR_CORTE, corte=ROTULO_CORTE[c], outcome=oid,
                 especificacao=esp, variante="principal").iloc[0]
        k = 100 if pct else 1
        un = " p.p." if pct else ""
        return (f"salto no corte: {_num(k * float(r['tau']), casas)}{un} "
                f"[{_num(k * float(r['ic95_inf']), casas)}; {_num(k * float(r['ic95_sup']), casas)}]")

    def painel_faixas(nome, titulo, cols, ylabel, salto, log=False):
        fig, axs = plt.subplots(1, 2, figsize=TAMANHO_FIG, facecolor=SUPERF, sharey=True)
        for ax, c in zip(axs, CORTES):
            sub = fx[fx["corte"] == ROTULO_CORTE[c]].sort_values("meio")
            for col, mk, rot in cols:
                for lado, cor in (("abaixo", COR_AB), ("acima", COR_AC)):
                    s = sub[sub["lado"] == lado]
                    ax.plot(s["meio"], s[col].astype(float), marker=mk, color=cor, lw=1.4,
                            mfc=cor if mk == "o" else "white", ms=8,
                            label=f"{rot}, {'bolsa menor' if lado == 'abaixo' else 'bolsa maior'}")
            ax.axvline(0, color=TINTA, ls="--", lw=0.9)
            if log:
                ax.set_yscale("log")
            else:
                ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _=None: f"{v:g}".replace(".", ",").replace("-", "−")))
            ax.set_title(f"corte {ROTULO_CORTE[c].replace('.', ',')}", fontsize=12, color=TINTA)
            ax.set_xlabel("distância ao corte (IVS − corte)", fontsize=10)
            ax.xaxis.set_major_formatter(FuncFormatter(_fx))
            ax.set_facecolor(SUPERF)
            ax.grid(alpha=0.25)
            anotar(ax, salto(c))
        axs[0].set_ylabel(ylabel, fontsize=10)
        axs[1].legend(fontsize=8.5, loc="lower right", frameon=False)
        fig.suptitle(titulo, fontsize=13, color=TINTA)
        fig.tight_layout(rect=(0, 0, 1, 0.95))
        salvar(fig, nome, "ND_estimativas.csv, tipo_linha = faixa, amostra = POR_CORTE; salto da linha D1")

    painel_faixas("ND_faixas_populacao.png", "População dos municípios perto do corte",
                  [("pop_media", "o", "média"), ("pop_mediana", "s", "mediana")], "habitantes (escala log)",
                  lambda c: salto_d1(c, "log_pop", "sem_controle") + " em log(pop)", log=True)
    painel_faixas("ND_faixas_vagas.png", "Vagas oferecidas perto do corte",
                  [("vic_media", "o", "vagas oferecidas")], "vagas por município (média)",
                  lambda c: salto_d1(c, "VIC", "sem_controle"))
    painel_faixas("ND_faixas_N1.png", "Vagas preenchidas (N1) perto do corte",
                  [("n1_media", "o", "N1 médio")], "vagas preenchidas por município (média)",
                  lambda c: salto_d1(c, "N1", "sem_controle"))
    painel_faixas("ND_faixas_taxa.png", "Taxa de preenchimento perto do corte",
                  [("taxa_vic_ponderada", "o", "por vaga"), ("taxa_vic_media_simples", "s", "por município")],
                  "vagas preenchidas / vagas oferecidas",
                  lambda c: salto_d1(c, "TAXA_VIC", "taxa_ponderada", pct=True, casas=1) + " (por vaga)")

    inf = est[est["tipo_linha"] == "influencia"].copy()
    for esp, nome, un, tit in (("S-a", "ND_influencia_Sa.png", "vagas", "Influência de cada município: N1 com controle"),
                               ("poisson_offset", "ND_influencia_poisson.png", "log",
                                "Influência de cada município: taxa por vaga (Poisson)")):
        fig, axs = plt.subplots(1, 2, figsize=TAMANHO_FIG, facecolor=SUPERF, sharey=True)
        for ax, c in zip(axs, CORTES):
            sub = inf[(inf["especificacao"] == esp) & (inf["corte"] == ROTULO_CORTE[c])]
            for lado, cor, rot in (("abaixo", COR_AB, "bolsa menor"), ("acima", COR_AC, "bolsa maior")):
                s = sub[sub["lado"] == lado]
                ax.scatter(s["distancia"].astype(float), s["delta_tau"].astype(float), s=36, c=cor, alpha=0.75,
                           edgecolor="white", lw=0.4, label=f"município, {rot}")
            for _, rr in sub[sub["posto"].astype(float) <= 3].iterrows():
                ax.annotate(str(rr["nome_municipio"]), (float(rr["distancia"]), float(rr["delta_tau"])), fontsize=8,
                            xytext=(4, 4), textcoords="offset points", color=TINTA)
            r0 = sub.iloc[0]
            ax.axhline(0, color=TINTA_2, lw=0.8)
            ax.axvline(0, color=TINTA, ls="--", lw=0.9)
            ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _=None: f"{v:g}".replace(".", ",").replace("-", "−")))
            ax.set_title(f"corte {ROTULO_CORTE[c].replace('.', ',')}", fontsize=12, color=TINTA)
            anotar(ax, f"salto com todos: {_num(float(r0['tau']), 2 if un == 'vagas' else 3)} ({un})")
            ax.set_xlabel("distância ao corte (IVS − corte)", fontsize=10)
            ax.xaxis.set_major_formatter(FuncFormatter(_fx))
            ax.set_facecolor(SUPERF)
            ax.grid(alpha=0.25)
        axs[0].set_ylabel(f"mudança no salto ao retirar o município ({un})", fontsize=10)
        axs[1].legend(fontsize=8.5, loc="lower right", frameon=False)
        fig.suptitle(tit, fontsize=13, color=TINTA)
        fig.tight_layout(rect=(0, 0, 1, 0.95))
        salvar(fig, nome, f"ND_estimativas.csv, tipo_linha = influencia, especificacao = {esp}")

    def rot_curto(rr) -> str:
        e, v = rr["especificacao"], rr["variante"]
        num = v.split("_")[1].replace(".", ",") if v.startswith("janela") else v.split("=")[-1].replace(".", ",")
        if e == "taxa_ponderada_local_linear":
            return f"reta local, h {num}"
        if e.startswith("local_constante"):
            return f"médias ±{num}, {'por vaga' if v.endswith('ponderada') else 'por município'}"
        if e.startswith("local_quadratico"):
            return f"curva local, h {num}"
        if e == "poisson_offset":
            return f"h {num}"
        return e

    for nome, filtro, k, xl, tit, cor in (
            ("ND_taxa_janelas.png", lambda s: s[(s["outcome"] == "TAXA_VIC") & (s["especificacao"] != "rdrobust_h_otimo")],
             100, "salto na taxa (pontos percentuais)", "Salto na taxa de preenchimento: várias formas de medir", COR_AB),
            ("ND_poisson_janelas.png", lambda s: s[s["especificacao"] == "poisson_offset"], 1,
             "salto em log da taxa por vaga", "Salto na taxa por vaga (Poisson) em janelas diferentes", COR_AC)):
        fig, axs = plt.subplots(1, 2, figsize=TAMANHO_FIG, facecolor=SUPERF, sharey=True)
        for j, c in enumerate(CORTES):
            sub = est[(est["amostra"] == POR_CORTE) & (est["corte"] == ROTULO_CORTE[c]) & (est["diagnostico"] == "D3")
                      & (est["status"] == "EXECUTADO")]
            sub = filtro(sub)
            val = k * sub["tau"].astype(float).to_numpy()
            lo = k * sub["ic95_inf"].astype(float).to_numpy()
            hi = k * sub["ic95_sup"].astype(float).to_numpy()
            yy = np.arange(len(sub))[::-1]
            ax = axs[j]
            ax.errorbar(val, yy, xerr=[val - lo, hi - val], fmt="o", color=cor, ecolor=cor, capsize=2, ms=5)
            ax.axvline(0, color=TINTA, lw=0.8)
            ax.set_yticks(yy)
            ax.set_yticklabels([rot_curto(rr) for _, rr in sub.iterrows()], fontsize=8.5)
            ax.set_title(f"corte {ROTULO_CORTE[c].replace('.', ',')}", fontsize=12, color=TINTA)
            ax.set_xlabel(xl, fontsize=10)
            ax.set_facecolor(SUPERF)
            ax.grid(alpha=0.25, axis="x")
        fig.suptitle(tit, fontsize=13, color=TINTA)
        fig.tight_layout(rect=(0, 0, 1, 0.95))
        salvar(fig, nome, "ND_estimativas.csv, diagnostico = D3, amostra = POR_CORTE")
    return feitas


# ---------------------------------------------------------------------------
# Doc 49b (gerado inteiro a partir das saídas)
# ---------------------------------------------------------------------------

def _sel(est: pd.DataFrame, **f) -> pd.DataFrame:
    m = np.ones(len(est), dtype=bool)
    for k, v in f.items():
        m &= (est[k].astype(str) == str(v)).to_numpy()
    return est[m]


def _um(est: pd.DataFrame, **f) -> pd.Series:
    s = _sel(est, **f)
    if len(s) != 1:
        raise FalhaValidacao(f"esperada 1 linha para {f}, achadas {len(s)}")
    return s.iloc[0]


def _f(v, casas=2, sinal=True, pct=False) -> str:
    try:
        v = float(v)
    except (TypeError, ValueError):
        return "—"
    if not math.isfinite(v):
        return "—"
    if pct:
        v = 100 * v
    return _num(v, casas, sinal)


def _ic(r, casas=2, pct=False) -> str:
    return f"[{_f(r['ic95_inf'], casas, pct=pct)}; {_f(r['ic95_sup'], casas, pct=pct)}]"


def _p(r) -> str:
    return _f(r["p_valor"], 3, False)


def _int(v) -> str:
    try:
        return str(int(float(v)))
    except (TypeError, ValueError):
        return "—"


def _mil(v) -> str:
    """População em milhares de habitantes, sem casa decimal."""
    try:
        return f"{float(v) / 1000:.0f}"
    except (TypeError, ValueError):
        return "—"


def _excl(r) -> bool:
    return float(r["ic95_inf"]) > 0 or float(r["ic95_sup"]) < 0


def _sentido(r, unidade="") -> str:
    t = float(r["tau"])
    s = "negativo" if t < 0 else "positivo"
    return f"{s} ({_f(t)}{unidade}; IC 95% {_ic(r)}, {'exclui' if _excl(r) else 'contém'} zero)"


def _tab(cab: list[str], linhas: list[list[str]]) -> str:
    out = ["| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)]
    out += ["| " + " | ".join(x) + " |" for x in linhas]
    return "\n".join(out)


ROT_OUT = {"log_pop": "log(pop 2022)", "VI": "vagas imediatas", "VIC": "vagas oferecidas (imediatas + CR)",
           "NC": "nº de células", "N1": "N1", "TAXA_VIC": "taxa N1 / vagas oferecidas (ponderada)",
           "TAXA_VI": "taxa N1 / vagas imediatas (ponderada)", "N1_POR_VAGA": "N1 / vagas oferecidas, sem peso",
           "LOG_N1": "log(N1)", "LOG_VIC": "log(vagas oferecidas)", "LOG_TAXA": "log(taxa)"}
PCT = {"TAXA_VIC", "TAXA_VI", "N1_POR_VAGA"}


def _rot_esp(r) -> str:
    return {"sem_controle": "sem controle", "controle_protocolo_48": "com o controle do protocolo 48",
            "taxa_ponderada": "peso = vagas", "log_aditiva": "N1 > 0", "log_pop": "com log(pop)",
            "log_pop_mais_vagas_imediatas": "com log(pop) + vagas imediatas", "sem_peso": "sem peso"}.get(
        r["especificacao"], r["especificacao"])


def tabela_d1(est, amostra) -> str:
    linhas = []
    cortes = [ROTULO_CORTE[c] for c in CORTES] if amostra == POR_CORTE else [EMPILHADO]
    for oid in ["log_pop", "VI", "VIC", "NC", "N1", "TAXA_VIC", "TAXA_VI"]:
        for esp in (["sem_controle", "controle_protocolo_48"] if oid == "N1" else
                    ["taxa_ponderada"] if oid.startswith("TAXA") else ["sem_controle"]):
            cel = [ROT_OUT[oid] + (f" ({_rot_esp({'especificacao': esp})})" if oid == "N1" else "")]
            for corte in cortes:
                r = _um(est, diagnostico="D1", tipo_linha="estimativa", amostra=amostra, corte=corte, outcome=oid,
                        especificacao=esp, variante="principal")
                pct = oid in PCT
                cel += [f"{_f(r['media_abaixo'], 2, False, pct)} → {_f(r['media_acima'], 2, False, pct)}",
                        f"{_f(r['tau'], 2, pct=pct)} {_ic(r, 2, pct)}", _p(r)]
            linhas.append(cel)
    cab = ["Variável"]
    for corte in cortes:
        cab += [f"{corte}: média abaixo → acima", f"{corte}: salto [IC 95%]", f"{corte}: p"]
    return _tab(cab, linhas)


def tabela_log(est, amostra) -> str:
    linhas = []
    cortes = [ROTULO_CORTE[c] for c in CORTES] if amostra == POR_CORTE else [EMPILHADO]
    for corte in cortes:
        rs = {o: _um(est, diagnostico="D1", tipo_linha="estimativa", amostra=amostra, corte=corte, outcome=o,
                     especificacao="log_aditiva") for o in ("LOG_N1", "LOG_VIC", "LOG_TAXA")}
        idt = _um(est, diagnostico="D1", tipo_linha="identidade", amostra=amostra, corte=corte)
        r0 = rs["LOG_N1"]
        linhas.append([corte, f"{_int(r0['n_abaixo'])} / {_int(r0['n_acima'])}",
                       f"{_int(r0['n_fora_abaixo'])} / {_int(r0['n_fora_acima'])}",
                       f"{_f(r0['tau'], 3)} {_ic(r0, 3)}", f"{_f(rs['LOG_VIC']['tau'], 3)} {_ic(rs['LOG_VIC'], 3)}",
                       f"{_f(rs['LOG_TAXA']['tau'], 3)} {_ic(rs['LOG_TAXA'], 3)}",
                       f"{float(idt['residuo_identidade']):.1e}"])
    return _tab(["Corte", "municípios usados abaixo / acima", "linhas fora (N1 = 0) abaixo / acima",
                 "salto em log(N1)", "= salto em log(vagas oferecidas)", "+ salto em log(taxa)", "resíduo"], linhas)


def tabela_faixas(est, corte, amostra=POR_CORTE) -> str:
    sub = _sel(est, tipo_linha="faixa", amostra=amostra, corte=corte).copy()
    sub["fi"] = sub["faixa_inf"].astype(float)
    linhas = []
    for _, r in sub.sort_values("fi").iterrows():
        lo, hi = float(r["faixa_inf"]), float(r["faixa_sup"])
        intervalo = f"({_fx(lo)}; {_fx(hi)}]" if r["lado"] == "abaixo" else f"[{_fx(lo)}; {_fx(hi)})"
        linhas.append([intervalo, r["lado"], _int(r["n_linhas"]), _mil(r["pop_media"]), _mil(r["pop_mediana"]),
                       _f(r["vi_media"], 1, False), _f(r["vic_media"], 1, False), _f(r["n1_media"], 2, False),
                       _f(r["taxa_vic_ponderada"], 1, False, True), _f(r["taxa_vic_media_simples"], 1, False, True),
                       f"{r['maior_municipio']} ({_mil(r['populacao_2022'])} mil)"])
    return _tab(["Distância ao corte", "lado", "linhas", "pop. média (mil)", "pop. mediana (mil)", "vagas imediatas",
                 "vagas oferecidas", "N1", "taxa ponderada (%)", "taxa média simples (%)", "maior município"], linhas)


def tabela_inclinacoes(est, amostra) -> str:
    linhas = []
    cortes = [ROTULO_CORTE[c] for c in CORTES] if amostra == POR_CORTE else [EMPILHADO]
    for corte in cortes:
        for esp in ("sem_controle", "controle_protocolo_48"):
            for var in ("sem_log_pop", "com_log_pop"):
                r = _um(est, tipo_linha="inclinacao", amostra=amostra, corte=corte, especificacao=esp, variante=var)
                linhas.append([corte, _rot_esp(r), "sim" if var == "com_log_pop" else "não",
                               f"{_f(r['inclinacao_abaixo'])} (EP {_f(r['ep_inclinacao_abaixo'], 2, False)})",
                               f"{_f(r['inclinacao_acima'])} (EP {_f(r['ep_inclinacao_acima'], 2, False)})",
                               f"{_f(r['tau'])} {_ic(r)}"])
    return _tab(["Corte", "N1", "log(pop) como covariável", "inclinação abaixo (vagas por 0,010)",
                 "inclinação acima (vagas por 0,010)", "salto [IC 95%]"], linhas)


def tabela_top(est, corte, esp) -> str:
    sub = _sel(est, tipo_linha="influencia", corte=corte, especificacao=esp).copy()
    sub["po"] = sub["posto"].astype(int)
    sub = sub.sort_values("po").head(N_TOP)
    casas = 2 if esp == "S-a" else 3
    linhas = [[_int(r["posto"]), r["co_ibge"], str(r["nome_municipio"]), _mil(r["populacao_2022"]),
               _f(r["vagas_oferecidas_ciclos"], 0, False), _f(r["n_alocados_ciclos"], 0, False), r["lado"],
               _fx(float(r["distancia"])), _f(r["delta_tau"], casas), _f(r["delta_tau_sobre_ep"], 2)]
              for _, r in sub.iterrows()]
    return _tab(["Posto", "co_ibge", "Município", "pop. (mil)", "vagas oferecidas (soma dos ciclos)",
                 "N1 (soma dos ciclos)", "lado", "distância", "Δ salto", "Δ salto / EP"], linhas)


def tabela_sem_maiores(est, corte) -> str:
    linhas = []
    for oid, esp, casas, pct in (("N1", "controle_protocolo_48", 2, False), ("N1", "sem_controle", 2, False),
                                 ("N1", "poisson_offset", 3, False), ("TAXA_VIC", "taxa_ponderada", 1, True)):
        base = (_um(est, diagnostico="D3", amostra=POR_CORTE, corte=corte, especificacao="poisson_offset", variante="h=0.050")
                if esp == "poisson_offset" else
                _um(est, diagnostico="D1" if esp != "controle_protocolo_48" else "D4", tipo_linha="estimativa",
                    amostra=POR_CORTE, corte=corte, outcome=oid, especificacao=esp, variante="principal"))
        cel = [("N1 Poisson com offset" if esp == "poisson_offset" else ROT_OUT[oid] if oid in PCT
                else f"{ROT_OUT[oid]} ({_rot_esp(base)})"),
               f"{_f(base['tau'], casas, pct=pct)}"]
        for kk in KS:
            for qual in ("abaixo", "acima", "dois_lados"):
                r = _um(est, tipo_linha="sem_maiores", corte=corte, outcome=oid, especificacao=esp,
                        variante=f"sem_{kk}_maiores_{qual}")
                cel.append(f"{_f(r['tau'], casas, pct=pct)}{'*' if _excl(r) else ''}")
        linhas.append(cel)
    cab = ["Outcome", "todos"] + [f"k={kk} {q.replace('dois_lados', 'ambos')}" for kk in KS
                                  for q in ("abaixo", "acima", "dois_lados")]
    return _tab(cab, linhas)


def lista_retirados(est, corte) -> str:
    out = []
    for kk in (max(KS),):
        for qual in ("abaixo", "acima"):
            r = _sel(est, tipo_linha="sem_maiores", corte=corte, variante=f"sem_{kk}_maiores_{qual}").iloc[0]
            out.append(f"- {qual} do corte {corte}, os {kk} mais populosos: {r['retirados']}.")
    return "\n".join(out)


def tabela_d3(est, corte, amostra=POR_CORTE) -> str:
    linhas = []
    sub = _sel(est, diagnostico="D3", amostra=amostra, corte=corte)
    for _, r in sub.iterrows():
        if r["status"] != "EXECUTADO":
            linhas.append([r["especificacao"], r["variante"], "—", "—", "—", "—", "NAO_EXECUTADO"])
            continue
        pct = r["outcome"] in PCT
        casas = 1 if pct else 3 if r["especificacao"] == "poisson_offset" else 2
        alvo = ("N1 (log da taxa)" if r["especificacao"] == "poisson_offset" else
                {"TAXA_VIC": "N1 / vagas oferecidas", "TAXA_VI": "N1 / vagas imediatas"}.get(r["outcome"],
                                                                                         ROT_OUT[r["outcome"]]))
        medias = ("—" if r["especificacao"] == "poisson_offset" else
                  f"{_f(r['media_abaixo'], casas, False, pct)} → {_f(r['media_acima'], casas, False, pct)}")
        linhas.append([r["especificacao"].replace("_", " "), r["variante"].replace("_", " "), alvo,
                       f"{_int(r['n_abaixo'])} / {_int(r['n_acima'])}", medias,
                       f"{_f(r['tau'], casas, pct=pct)} {_ic(r, casas, pct)}", _p(r)])
    return _tab(["Estimador", "Janela / variante", "Outcome", "municípios abaixo / acima", "média abaixo → acima",
                 "salto [IC 95%]", "p"], linhas)


def tabela_d4(est, amostra) -> str:
    linhas = []
    cortes = [ROTULO_CORTE[c] for c in CORTES] if amostra in (POR_CORTE,) else [EMPILHADO]
    for esp, oid in (("sem_controle", "N1"), ("log_pop", "N1"), ("log_pop_mais_vagas_imediatas", "N1"),
                     ("controle_protocolo_48", "N1"), ("sem_peso", "N1_POR_VAGA")):
        cel = [ROT_OUT[oid] if oid == "N1_POR_VAGA" else f"{ROT_OUT[oid]}, {_rot_esp({'especificacao': esp})}"]
        for corte in cortes:
            r = _um(est, diagnostico="D4", amostra=amostra, corte=corte, outcome=oid, especificacao=esp)
            pct = oid in PCT
            cel += [f"{_f(r['tau'], 2 if not pct else 1, pct=pct)} {_ic(r, 2 if not pct else 1, pct)}", _p(r)]
        linhas.append(cel)
    cab = ["Especificação"] + [x for corte in cortes for x in (f"{corte}: salto [IC 95%]", f"{corte}: p")]
    return _tab(cab, linhas)


def tabela_d5(est, esp) -> str:
    linhas = []
    sub = _sel(est, diagnostico="D5", tipo_linha="contribuicao", amostra=EMP, especificacao=esp)
    for _, r in sub.iterrows():
        linhas.append([r["grupo"], _f(r["peso_omega"], 3, False), f"{_f(r['tau_grupo'])} {_ic(r)}",
                       _f(r["contribuicao"])])
    idt = _um(est, diagnostico="D5", tipo_linha="identidade", amostra=EMP, especificacao=esp)
    linhas.append(["**soma = salto empilhado**", _f(1.0, 3, False), f"{_f(idt['tau'])} {_ic(idt)}",
                   f"{_f(idt['contribuicao'])}"])
    return _tab(["Ciclo × corte", "peso omega", "salto só do grupo [IC 95%]", "contribuição (omega × salto)"], linhas)


def tabela_d5_cortes(est) -> str:
    linhas = []
    for esp in ("sem_controle", "controle_protocolo_48"):
        sub = _sel(est, diagnostico="D5", tipo_linha="contribuicao", amostra=EMP, especificacao=esp).copy()
        sub["c"] = sub["variante"].str[-3:]
        emp = _um(est, diagnostico="D5", tipo_linha="identidade", amostra=EMP, especificacao=esp)
        cel = [f"N1 {_rot_esp({'especificacao': esp})}", f"{_f(emp['tau'])} {_ic(emp)}"]
        for c in CORTES:
            s = sub[sub["c"] == str(c)]
            iso = _um(est, diagnostico="D5", tipo_linha="identidade", amostra=POR_CORTE, corte=ROTULO_CORTE[c],
                      especificacao=esp)
            cel += [_f(s["peso_omega"].astype(float).sum(), 3, False), _f(s["contribuicao"].astype(float).sum()),
                    f"{_f(iso['tau'])} {_ic(iso)}"]
        linhas.append(cel)
    for oid, esp, var, casas, pct in (("N1", "poisson_offset", "h=0.050", 3, False),
                                      ("TAXA_VIC", "taxa_ponderada", "principal", 1, True)):
        diag = "D3" if esp == "poisson_offset" else "D1"
        emp = _um(est, diagnostico=diag, tipo_linha="estimativa", amostra=EMP, corte=EMPILHADO, outcome=oid,
                  especificacao=esp, variante=var)
        cel = ["N1 Poisson com offset (log)" if esp == "poisson_offset" else ROT_OUT[oid],
               f"{_f(emp['tau'], casas, pct=pct)} {_ic(emp, casas, pct)}"]
        for c in CORTES:
            iso = _um(est, diagnostico=diag, tipo_linha="estimativa", amostra=POR_CORTE, corte=ROTULO_CORTE[c],
                      outcome=oid, especificacao=esp, variante=var)
            cel += ["—", "—", f"{_f(iso['tau'], casas, pct=pct)} {_ic(iso, casas, pct)}"]
        linhas.append(cel)
    cab = ["Outcome", "empilhado [IC 95%]"] + [x for c in CORTES for x in (
        f"{ROTULO_CORTE[c]}: soma dos pesos", f"{ROTULO_CORTE[c]}: contribuição", f"{ROTULO_CORTE[c]} isolado [IC 95%]")]
    return _tab(cab, linhas)


def tabela_apendice(est) -> str:
    linhas = []
    for k in CICLOS:
        for c in CORTES:
            corte = ROTULO_CORTE[c]
            cel = [str(k), corte]
            for diag, oid, esp in (("D1", "log_pop", "sem_controle"), ("D1", "VIC", "sem_controle"),
                                   ("D1", "N1", "sem_controle"), ("D1", "N1", "controle_protocolo_48"),
                                   ("D1", "TAXA_VIC", "taxa_ponderada"), ("D4", "N1", "log_pop_mais_vagas_imediatas")):
                r = _um(est, diagnostico=diag, tipo_linha="estimativa", amostra=APENDICE, populacao=f"V{k}", corte=corte,
                        outcome=oid, especificacao=esp)
                pct = oid in PCT
                cel.append(f"{_f(r['tau'], 1 if pct else 2, pct=pct)}{'*' if _excl(r) else ''}")
            r = _um(est, diagnostico="D1", tipo_linha="estimativa", amostra=APENDICE, populacao=f"V{k}", corte=corte,
                    outcome="N1", especificacao="sem_controle")
            cel.insert(2, f"{_int(r['n_abaixo'])} / {_int(r['n_acima'])}")
            linhas.append(cel)
    return _tab(["Ciclo", "Corte", "n abaixo / acima", "log(pop)", "vagas oferecidas", "N1 sem controle",
                 "N1 com controle", "taxa ponderada (p.p.)", "N1 com log(pop) + vagas imediatas"], linhas)


def _r(est, **f):
    return _um(est, **f)


def leitura(est: pd.DataFrame, resumo: dict) -> dict[str, str]:
    """Frases de leitura geradas por regra fixa a partir das linhas gravadas."""
    t = {}
    g = {}
    for c in CORTES:
        cl = ROTULO_CORTE[c]
        g[cl] = {
            "pop": _r(est, diagnostico="D1", tipo_linha="estimativa", amostra=POR_CORTE, corte=cl, outcome="log_pop",
                      especificacao="sem_controle"),
            "vic": _r(est, diagnostico="D1", tipo_linha="estimativa", amostra=POR_CORTE, corte=cl, outcome="VIC",
                      especificacao="sem_controle"),
            "vi": _r(est, diagnostico="D1", tipo_linha="estimativa", amostra=POR_CORTE, corte=cl, outcome="VI",
                     especificacao="sem_controle"),
            "n1": _r(est, diagnostico="D1", tipo_linha="estimativa", amostra=POR_CORTE, corte=cl, outcome="N1",
                     especificacao="sem_controle"),
            "sa": _r(est, diagnostico="D1", tipo_linha="estimativa", amostra=POR_CORTE, corte=cl, outcome="N1",
                     especificacao="controle_protocolo_48"),
            "tx": _r(est, diagnostico="D1", tipo_linha="estimativa", amostra=POR_CORTE, corte=cl, outcome="TAXA_VIC",
                     especificacao="taxa_ponderada"),
            "txi": _r(est, diagnostico="D1", tipo_linha="estimativa", amostra=POR_CORTE, corte=cl, outcome="TAXA_VI",
                      especificacao="taxa_ponderada"),
            "lvic": _r(est, diagnostico="D1", tipo_linha="estimativa", amostra=POR_CORTE, corte=cl, outcome="LOG_VIC"),
            "ltx": _r(est, diagnostico="D1", tipo_linha="estimativa", amostra=POR_CORTE, corte=cl, outcome="LOG_TAXA"),
            "po": _r(est, diagnostico="D3", amostra=POR_CORTE, corte=cl, especificacao="poisson_offset", variante="h=0.050"),
            "lp": _r(est, diagnostico="D4", amostra=POR_CORTE, corte=cl, outcome="N1", especificacao="log_pop"),
            "lpv": _r(est, diagnostico="D4", amostra=POR_CORTE, corte=cl, outcome="N1",
                      especificacao="log_pop_mais_vagas_imediatas"),
            "inc0": _r(est, tipo_linha="inclinacao", amostra=POR_CORTE, corte=cl, especificacao="controle_protocolo_48",
                       variante="sem_log_pop"),
            "inc1": _r(est, tipo_linha="inclinacao", amostra=POR_CORTE, corte=cl, especificacao="controle_protocolo_48",
                       variante="com_log_pop"),
            "incb0": _r(est, tipo_linha="inclinacao", amostra=POR_CORTE, corte=cl, especificacao="sem_controle",
                        variante="sem_log_pop"),
            "incb1": _r(est, tipo_linha="inclinacao", amostra=POR_CORTE, corte=cl, especificacao="sem_controle",
                        variante="com_log_pop"),
        }
        inf = _sel(est, tipo_linha="influencia", corte=cl, especificacao="S-a").copy()
        inf["po"] = inf["posto"].astype(int)
        g[cl]["top"] = inf.sort_values("po").iloc[0]
        g[cl]["maxep"] = float(inf["delta_tau_sobre_ep"].astype(float).abs().max())
        infp = _sel(est, tipo_linha="influencia", corte=cl, especificacao="poisson_offset").copy()
        infp["po"] = infp["posto"].astype(int)
        g[cl]["topp"] = infp.sort_values("po").iloc[0]
        sm = {}
        for esp, oid in (("controle_protocolo_48", "N1"), ("poisson_offset", "N1"), ("taxa_ponderada", "TAXA_VIC"),
                         ("sem_controle", "N1")):
            vals = _sel(est, tipo_linha="sem_maiores", corte=cl, especificacao=esp, outcome=oid)
            sm[esp] = (float(vals["tau"].astype(float).min()), float(vals["tau"].astype(float).max()),
                       int(sum(_excl(r) for _, r in vals.iterrows())), len(vals))
        g[cl]["sm"] = sm
        d3 = _sel(est, diagnostico="D3", amostra=POR_CORTE, corte=cl, status="EXECUTADO")
        d3t = d3[d3["outcome"] == "TAXA_VIC"]
        g[cl]["d3_sinais"] = (int((d3t["tau"].astype(float) < 0).sum()), int((d3t["tau"].astype(float) > 0).sum()),
                              int(sum(_excl(r) for _, r in d3t.iterrows())), len(d3t))
        d3p = d3[d3["especificacao"] == "poisson_offset"]
        g[cl]["d3_pois"] = (float(d3p["tau"].astype(float).min()), float(d3p["tau"].astype(float).max()),
                            int(sum(_excl(r) for _, r in d3p.iterrows())), len(d3p))
        fx = _sel(est, tipo_linha="faixa", amostra=POR_CORTE, corte=cl).copy()
        fx["f"] = fx["faixa"].astype(int)
        g[cl]["fx"] = fx.set_index("f")

    a_txt = []
    for cl in g:
        G = g[cl]
        fx = G["fx"]
        a_txt.append(
            f"- **Corte {cl}.** Na faixa mais distante à esquerda (distância de −0,050 a −0,040), N1 médio = "
            f"{_f(fx.loc[-5, 'n1_media'], 2, False)}, população média = {_mil(fx.loc[-5, 'pop_media'])} mil e vagas "
            f"oferecidas = {_f(fx.loc[-5, 'vic_media'], 1, False)}; na faixa colada ao corte (−0,010 a 0), N1 médio = "
            f"{_f(fx.loc[-1, 'n1_media'], 2, False)}, população média = {_mil(fx.loc[-1, 'pop_media'])} mil "
            f"(mediana {_mil(fx.loc[-1, 'pop_mediana'])} mil; maior município: {fx.loc[-1, 'maior_municipio']}) e "
            f"vagas oferecidas = {_f(fx.loc[-1, 'vic_media'], 1, False)}. A inclinação de N1 com controle à esquerda "
            f"é {_f(G['inc0']['inclinacao_abaixo'])} vaga por 0,010 de IVS sem log(pop) e "
            f"{_f(G['inc1']['inclinacao_abaixo'])} com log(pop); sem controle, {_f(G['incb0']['inclinacao_abaixo'])} e "
            f"{_f(G['incb1']['inclinacao_abaixo'])}.")
    t["a"] = "\n".join(a_txt)

    b_txt = []
    for cl in g:
        G = g[cl]
        b_txt.append(
            f"- **Corte {cl}.** N1 sem controle: salto {_sentido(G['n1'])}. Vagas oferecidas: {_sentido(G['vic'])}; "
            f"vagas imediatas: {_sentido(G['vi'])}; log(pop): {_sentido(G['pop'])}. Taxa ponderada por vagas "
            f"oferecidas: {_f(G['tx']['tau'], 1, pct=True)} p.p. (IC 95% {_ic(G['tx'], 1, True)}, "
            f"{'exclui' if _excl(G['tx']) else 'contém'} zero); com as vagas imediatas: "
            f"{_f(G['txi']['tau'], 1, pct=True)} p.p. (IC 95% {_ic(G['txi'], 1, True)}, "
            f"{'exclui' if _excl(G['txi']) else 'contém'} zero). Na decomposição em log (municípios com N1 > 0), o "
            f"salto de log(vagas oferecidas) é {_f(G['lvic']['tau'], 3)} e o de log(taxa) é {_f(G['ltx']['tau'], 3)}. "
            f"N1 com log(pop): {_sentido(G['lp'])}; com log(pop) + vagas imediatas: {_sentido(G['lpv'])}.")
    t["b"] = "\n".join(b_txt)

    inf_txt = []
    for cl in g:
        G = g[cl]
        sm = G["sm"]
        inf_txt.append(
            f"- **Corte {cl}.** O município mais influente no salto com controle é {G['top']['nome_municipio']} "
            f"(Δ = {_f(G['top']['delta_tau'])} vaga, {_f(G['top']['delta_tau_sobre_ep'])} EP); nenhum muda o salto em "
            f"mais de {_f(G['maxep'], 2, False)} EP. No Poisson com offset, o mais influente é "
            f"{G['topp']['nome_municipio']} (Δ = {_f(G['topp']['delta_tau'], 3)} em log). Retirando os k = 1, 3, 5 "
            f"municípios mais populosos (abaixo, acima, dos dois lados), o salto com controle fica entre "
            f"{_f(sm['controle_protocolo_48'][0])} e {_f(sm['controle_protocolo_48'][1])} "
            f"({sm['controle_protocolo_48'][2]} de {sm['controle_protocolo_48'][3]} com IC que exclui zero); o Poisson "
            f"com offset, entre {_f(sm['poisson_offset'][0], 3)} e {_f(sm['poisson_offset'][1], 3)} "
            f"({sm['poisson_offset'][2]} de {sm['poisson_offset'][3]}); a taxa ponderada, entre "
            f"{_f(sm['taxa_ponderada'][0], 1, pct=True)} e {_f(sm['taxa_ponderada'][1], 1, pct=True)} p.p. "
            f"({sm['taxa_ponderada'][2]} de {sm['taxa_ponderada'][3]}).")
    t["influencia"] = "\n".join(inf_txt)

    d3_txt = []
    for cl in g:
        G = g[cl]
        neg, pos, exc, tot = G["d3_sinais"]
        pmin, pmax, pexc, ptot = G["d3_pois"]
        d3_txt.append(
            f"- **Corte {cl}.** Das {tot} estimativas da taxa (local linear ponderado, local constante ponderado e "
            f"sem peso, local quadrático, com as vagas oferecidas no denominador), {neg} são negativas e {pos} "
            f"positivas; com IC que exclui zero: {exc}. O Poisson com offset vai de {_f(pmin, 3)} a {_f(pmax, 3)} entre "
            f"h = 0,020 e h = 0,080 ({pexc} de {ptot} com IC que exclui zero).")
    t["d3"] = "\n".join(d3_txt)

    # Conciliação com a taxa bruta das pistas (adendo AD1: janela inteira, sem peso, vagas imediatas).
    conc = []
    for cl in g:
        ad_si = _r(est, diagnostico="D3", amostra=POR_CORTE, corte=cl, outcome="TAXA_VI",
                   especificacao="local_constante_adendo_AD1", variante="janela_0.050_sem_peso")
        ad_wc = _r(est, diagnostico="D3", amostra=POR_CORTE, corte=cl, outcome="TAXA_VIC",
                   especificacao="local_constante_adendo_AD1", variante="janela_0.050_ponderada")
        lc10 = _r(est, diagnostico="D3", amostra=POR_CORTE, corte=cl, outcome="TAXA_VIC", especificacao="local_constante",
                  variante="janela_0.010_ponderada")
        conc.append(
            f"- **Corte {cl}.** Média simples de N1 / vagas imediatas na janela inteira: "
            f"{_f(ad_si['media_abaixo'], 1, False, True)} % abaixo e {_f(ad_si['media_acima'], 1, False, True)} % acima "
            f"(diferença com intercepto por ciclo: {_f(ad_si['tau'], 1, pct=True)} p.p., IC 95% {_ic(ad_si, 1, True)}). "
            f"Trocando para a taxa no nível da vaga com as vagas oferecidas (imediatas + CR), na mesma janela: "
            f"{_f(ad_wc['media_abaixo'], 1, False, True)} % e {_f(ad_wc['media_acima'], 1, False, True)} % "
            f"({_f(ad_wc['tau'], 1, pct=True)} p.p.). Só em ±0,010: {_f(lc10['media_abaixo'], 1, False, True)} % e "
            f"{_f(lc10['media_acima'], 1, False, True)} % ({_f(lc10['tau'], 1, pct=True)} p.p., IC 95% "
            f"{_ic(lc10, 1, True)}). O Poisson com offset (reta local, h = 0,050): {_f(g[cl]['po']['tau'], 3)} em log "
            f"(IC 95% {_ic(g[cl]['po'], 3)}).")
    t["conciliacao"] = "\n".join(conc)

    # D5
    d5 = []
    for esp in ("sem_controle", "controle_protocolo_48"):
        sub = _sel(est, diagnostico="D5", tipo_linha="contribuicao", amostra=EMP, especificacao=esp).copy()
        sub["c"] = sub["variante"].str[-3:]
        emp = _um(est, diagnostico="D5", tipo_linha="identidade", amostra=EMP, especificacao=esp)
        partes = []
        for c in CORTES:
            s = sub[sub["c"] == str(c)]
            partes.append(f"o corte {ROTULO_CORTE[c]} tem peso {_f(s['peso_omega'].astype(float).sum(), 2, False)} e "
                          f"contribui {_f(s['contribuicao'].astype(float).sum())}")
        maior = sub.assign(ab=sub["contribuicao"].astype(float).abs()).sort_values("ab", ascending=False).iloc[0]
        d5.append(f"- **N1 {_rot_esp({'especificacao': esp})}**: salto empilhado {_f(emp['tau'])}; "
                  + "; ".join(partes) + f". A maior contribuição isolada é a do grupo {maior['grupo']} "
                  f"({_f(maior['contribuicao'])}, salto só do grupo {_f(maior['tau_grupo'])}).")
    t["d5"] = "\n".join(d5)
    return t


def gerar_doc(est: pd.DataFrame, resumo: dict) -> str:
    lt = leitura(est, resumo)
    diags = "\n".join(f"- **{d['id']}, {d['nome']}:**\n" + "\n".join(f"  - {i}" for i in d["itens"])
                      for d in resumo["diagnosticos"])
    expo = "\n".join(f"- {x}" for x in resumo["exposicao_previa"])
    ad = "\n".join(f"- **{x['id']} ({x['data'][8:10]}/{x['data'][5:7]}/{x['data'][:4]}).** {x['o_que']}. Por quê: "
                   f"{x['por_que']}. O que já tinha sido visto: {x['ja_visto']}." for x in resumo["adendos"])
    val = resumo["validacoes"]
    figs = "\n\n".join(f"![{Path(f['arquivo']).stem}](../../{f['arquivo']})\n\n**Como ler:** {f['como_ler']}\n\n"
                         f"*Detalhe técnico:* {DETALHE_FIG[Path(f['arquivo']).name]}"
                         for f in resumo["saidas"]["figuras"] if not f.get("adendo"))
    figs_ad2 = "\n\n".join(f"![{Path(f['arquivo']).stem}](../../{f['arquivo']})\n\n**Como ler:** {f['como_ler']}\n\n"
                             f"*Detalhe técnico:* {DETALHE_FIG[Path(f['arquivo']).name]}"
                             for f in resumo["saidas"]["figuras"] if f.get("adendo") == ADENDO2)
    cont = resumo["contagens"]
    G = {ROTULO_CORTE[c]: {
        "sa": _um(est, diagnostico="D1", tipo_linha="estimativa", amostra=POR_CORTE, corte=ROTULO_CORTE[c], outcome="N1",
                  especificacao="controle_protocolo_48"),
        "n1": _um(est, diagnostico="D1", tipo_linha="estimativa", amostra=POR_CORTE, corte=ROTULO_CORTE[c], outcome="N1",
                  especificacao="sem_controle"),
        "tx": _um(est, diagnostico="D1", tipo_linha="estimativa", amostra=POR_CORTE, corte=ROTULO_CORTE[c],
                  outcome="TAXA_VIC", especificacao="taxa_ponderada"),
        "vic": _um(est, diagnostico="D1", tipo_linha="estimativa", amostra=POR_CORTE, corte=ROTULO_CORTE[c],
                   outcome="VIC", especificacao="sem_controle"),
        "pop": _um(est, diagnostico="D1", tipo_linha="estimativa", amostra=POR_CORTE, corte=ROTULO_CORTE[c],
                   outcome="log_pop", especificacao="sem_controle"),
        "po": _um(est, diagnostico="D3", amostra=POR_CORTE, corte=ROTULO_CORTE[c], especificacao="poisson_offset",
                  variante="h=0.050")} for c in CORTES}
    c3, c4 = ROTULO_CORTE[300], ROTULO_CORTE[400]
    emp_sa = _um(est, diagnostico="D5", tipo_linha="identidade", amostra=EMP, especificacao="controle_protocolo_48")
    emp_po = _um(est, diagnostico="D3", amostra=EMP, corte=EMPILHADO, especificacao="poisson_offset", variante="h=0.050")

    def forca(r) -> str:
        p = float(r["p_valor"])
        return "forte" if p < 0.01 else "moderada" if p < 0.05 else "fraca" if p < 0.10 else "ausente"

    def R(**f):
        return _um(est, **f)

    def fx_(corte):
        s = _sel(est, tipo_linha="faixa", amostra=POR_CORTE, corte=corte).copy()
        s["f"] = s["faixa"].astype(int)
        return s.set_index("f")

    fx3, fx4 = fx_(c3), fx_(c4)
    inc = {(cl, v): R(tipo_linha="inclinacao", amostra=POR_CORTE, corte=cl, especificacao="controle_protocolo_48",
                      variante=v) for cl in (c3, c4) for v in ("sem_log_pop", "com_log_pop")}
    tvi3 = R(diagnostico="D1", tipo_linha="estimativa", amostra=POR_CORTE, corte=c3, outcome="TAXA_VI",
             especificacao="taxa_ponderada")
    lcw3 = R(diagnostico="D3", amostra=POR_CORTE, corte=c3, outcome="TAXA_VIC", especificacao="local_constante",
             variante="janela_0.010_ponderada")
    lcs3 = R(diagnostico="D3", amostra=POR_CORTE, corte=c3, outcome="TAXA_VIC", especificacao="local_constante",
             variante="janela_0.010_sem_peso")
    q3 = R(diagnostico="D3", amostra=POR_CORTE, corte=c3, outcome="TAXA_VIC",
           especificacao="local_quadratico_taxa_ponderada")
    hs3 = [R(diagnostico="D3", amostra=POR_CORTE, corte=c3, outcome="TAXA_VIC", especificacao="taxa_ponderada_local_linear",
             variante=f"h={h / 1000:.3f}") for h in H_D3]
    sm3 = _sel(est, tipo_linha="sem_maiores", corte=c3, especificacao="controle_protocolo_48", outcome="N1")
    smt3 = _sel(est, tipo_linha="sem_maiores", corte=c3, especificacao="taxa_ponderada", outcome="TAXA_VIC")
    s4 = R(tipo_linha="sem_maiores", corte=c4, outcome="N1", especificacao="sem_controle", variante="sem_3_maiores_abaixo")
    inf3 = _sel(est, tipo_linha="influencia", corte=c3, especificacao="S-a")
    maxep3 = float(inf3["delta_tau_sobre_ep"].astype(float).abs().max())
    hs_exc = [f"{_f(r['h'], 3, False)}" for r in hs3 if _excl(r)]

    resposta_a = (
        f"A contagem acompanha quantas vagas o município abre e o tamanho dele, e perto do corte, do lado de bolsa "
        f"menor, há municípios maiores ou com mais vagas. No corte {c3}, a faixa colada ao corte (distância de −0,010 a 0) tem população "
        f"média de {_mil(fx3.loc[-1, 'pop_media'])} mil, contra mediana de {_mil(fx3.loc[-1, 'pop_mediana'])} mil "
        f"(maior município: {fx3.loc[-1, 'maior_municipio']}); na faixa mais distante (−0,050 a −0,040), média de "
        f"{_mil(fx3.loc[-5, 'pop_media'])} mil. Nesse lado a taxa por vaga também sobe, de "
        f"{_f(fx3.loc[-5, 'taxa_vic_ponderada'], 1, False, True)} % para {_f(fx3.loc[-1, 'taxa_vic_ponderada'], 1, False, True)} %. "
        f"No corte {c4}, o que sobe à esquerda são as vagas imediatas (de {_f(fx4.loc[-5, 'vi_media'], 1, False)} para "
        f"{_f(fx4.loc[-1, 'vi_media'], 1, False)} por município) e as oferecidas (de {_f(fx4.loc[-5, 'vic_media'], 1, False)} "
        f"para {_f(fx4.loc[-1, 'vic_media'], 1, False)}), com a taxa por vaga entre "
        f"{_f(fx4.loc[-5, 'taxa_vic_ponderada'], 1, False, True)} % e {_f(fx4.loc[-1, 'taxa_vic_ponderada'], 1, False, True)} %. "
        f"Pôr log(pop) como covariável quase não muda a inclinação à esquerda de N1 com controle "
        f"({_f(inc[(c3, 'sem_log_pop')]['inclinacao_abaixo'])} → {_f(inc[(c3, 'com_log_pop')]['inclinacao_abaixo'])} vaga "
        f"por 0,010 em {c3}; {_f(inc[(c4, 'sem_log_pop')]['inclinacao_abaixo'])} → "
        f"{_f(inc[(c4, 'com_log_pop')]['inclinacao_abaixo'])} em {c4}): o que pesa são poucas cidades grandes e as "
        f"vagas que elas abrem e preenchem, não o porte medido em log. A reta local de cada lado projeta essa "
        f"subida até o corte.")

    resposta_b = (
        f"No corte {c3}, o desbalanceamento de porte **não** explica o salto: log(pop) "
        f"({_f(G[c3]['pop']['tau'])}, IC 95% {_ic(G[c3]['pop'])}) e as vagas oferecidas ({_f(G[c3]['vic']['tau'])}, "
        f"IC 95% {_ic(G[c3]['vic'])}) não saltam, e tirar os 1, 3 ou 5 municípios mais populosos de um lado ou dos "
        f"dois deixa o salto com controle entre {_f(sm3['tau'].astype(float).min())} e {_f(sm3['tau'].astype(float).max())} "
        f"(com todos, {_f(G[c3]['sa']['tau'])}). O que cai é a taxa de preenchimento por vaga oferecida "
        f"({_f(G[c3]['tx']['tau'], 1, pct=True)} p.p., IC 95% {_ic(G[c3]['tx'], 1, True)}; Poisson com offset "
        f"{_f(G[c3]['po']['tau'], 3)}), estável a retirar qualquer município (a maior mudança é de {_f(maxep3, 2, False)} "
        f"EP), a retirar os maiores (entre {_f(smt3['tau'].astype(float).min(), 1, pct=True)} e "
        f"{_f(smt3['tau'].astype(float).max(), 1, pct=True)} p.p.), com IC que exclui zero nas janelas h = "
        f"{', '.join(hs_exc) if hs_exc else 'nenhuma'} e no local quadrático ({_f(q3['tau'], 1, pct=True)} p.p.). Mas o "
        f"salto depende de como a taxa é medida: com as vagas imediatas no denominador o IC contém zero "
        f"({_f(tvi3['tau'], 1, pct=True)} p.p., IC 95% {_ic(tvi3, 1, True)}); comparando só os municípios a até 0,010 "
        f"do corte, ele é {_f(lcw3['tau'], 1, pct=True)} p.p. contando cada vaga igual (IC 95% {_ic(lcw3, 1, True)}) e "
        f"{_f(lcs3['tau'], 1, pct=True)} p.p. contando cada município igual (IC 95% {_ic(lcs3, 1, True)}). Parte do "
        f"salto local linear vem da subida da taxa à esquerda, que a reta projeta até o corte. No corte {c4}, o porte e a "
        f"oferta **explicam a maior parte** da queda: sem controle ela é {_f(G[c4]['n1']['tau'])} (IC 95% {_ic(G[c4]['n1'])}), acompanha menos "
        f"vagas oferecidas acima do corte ({_f(G[c4]['vic']['tau'])}, IC 95% {_ic(G[c4]['vic'])}), passa a "
        f"{_f(s4['tau'])} sem os três municípios mais populosos logo abaixo do corte, quase some com controle "
        f"({_f(G[c4]['sa']['tau'])}, IC 95% {_ic(G[c4]['sa'])}), e a taxa não salta "
        f"({_f(G[c4]['tx']['tau'], 1, pct=True)} p.p., IC 95% {_ic(G[c4]['tx'], 1, True)}).")

    doc = f"""# 49b. Diagnóstico: porte, oferta e taxa na contagem de vagas preenchidas (família N)

> **Data:** {resumo['data_execucao'][8:10]}/{resumo['data_execucao'][5:7]}/{resumo['data_execucao'][:4]}.<br>
> **Estatuto:** `{ESTATUTO}`. Diagnóstico **fora do protocolo 48**: não substitui a especificação principal (S-a,
> ciclos e cortes empilhados), não muda o Holm do protocolo 48 nem as conclusões do
> [doc 49](49_resultados_contagem_vagas_preenchidas.md). Nenhuma variante daqui vira especificação principal.<br>
> **Script:** `scripts/rdd_bolsa/23b_diagnostico_contagem_porte.py` (estimadores de `rdd_lib.py` e do script 23).<br>
> **Saídas:** `output/rdd_bolsa/ND_estimativas.csv` (toda linha com `estatuto = {ESTATUTO}` e
> `natureza_dos_dados = {NATUREZA}`), `ND_resumo.json` (entradas com SHA-256, lista fixa de diagnósticos, adendos,
> validações) e `ND_figuras/`.<br>
> **Testes:** `tests/test_diagnostico_contagem_porte.py`.<br>
> **Números:** este documento é gerado inteiro pelo script a partir das saídas; o teste confere que ele é idêntico
> ao gerado e que cada número tem origem em `output/`.

## 1. A pergunta

Na figura de N1 do doc 49 (vagas preenchidas na 1ª chamada, com controle pelas vagas oferecidas, ciclos e cortes
empilhados) aparecem dois padrões:

- **(a)** dentro da janela, a contagem **sobe** com o IVS, sobretudo à esquerda do corte, quando a intuição diria
  que municípios mais vulneráveis atraem menos;
- **(b)** no corte, a contagem **cai** do lado de bolsa maior.

O contraste é o **pacote do corte**: em 0,300 e 0,400 sobe a bolsa anunciada, mas outras regras federais mudam
nos mesmos cortes ([auditoria 18](../auditorias/18_politicas_nos_mesmos_cortes_ivs.md)). Nada aqui é efeito da
participação no PMM-E, do Agora Tem Especialistas ou do degrau de R$ 5 mil isolado. O IVS é o de 2010, fixo
antes do programa: um desequilíbrio de porte entre os lados não é manipulação, é composição de uma amostra finita
perto do corte.

## 2. Conjunto fixo de diagnósticos (listado antes de rodar)

Gravado em `diagnosticos` de `ND_resumo.json`. Todos são relatados abaixo, qualquer que seja o resultado.

{diags}

**Amostras.** POR_CORTE (principal deste diagnóstico): um corte por vez, ciclos 1–3 juntos com intercepto e
inclinações por ciclo e salto comum, EP CR1 por município, h = 0,050, kernel triangular (a mesma especificação do
script 23). APENDICE_POR_CICLO: ciclo × corte, EP HC1. EMPILHADO_COMPARACAO: ciclos e cortes empilhados, a amostra
da figura do doc 49, **só como comparação**.

**O que já tinha sido visto antes de fixar a lista** (`exposicao_previa`):

{expo}

**Adendos datados** (diagnósticos acrescentados depois de rodar):

{ad}

## 3. Resposta curta

**(a) A subida dentro da janela.** {resposta_a} Força da evidência: **descritiva** (seção 5), não um teste.

**(b) A queda no corte.** Tem causas diferentes em cada corte, e o empilhado mistura as duas. {resposta_b}
Força da evidência sobre a queda da taxa em {c3}: **{forca(G[c3]['tx'])}** no local linear ponderado
(p = {_p(G[c3]['tx'])}), sem correção por comparações múltiplas e dependente da medida da taxa (seção 6); a hipótese de
porte em {c4} tem apoio **descritivo**, e lá nem a queda sem controle (p = {_p(G[c4]['n1'])}) nem a taxa
(p = {_p(G[c4]['tx'])}) se distinguem de zero.

**O conflito entre o Poisson com offset e a taxa bruta** (seção 7) se desfaz quando se separam quatro coisas que a
taxa bruta das pistas junta: o denominador (vagas imediatas, nas pistas; imediatas + cadastro reserva, no Poisson),
o peso (cada município pesa igual na média simples; cada vaga pesa igual no Poisson), a janela (média da janela
inteira, nas pistas; reta local avaliada no corte, no Poisson) e o empilhamento dos cortes (o sinal negativo do
Poisson empilhado, {_f(emp_po['tau'], 3)}, vem de {c3}).

**Empilhar os cortes** (seção 8) junta um corte em que a taxa por vaga cai e outro em que a oferta cai: o salto
com controle empilhado ({_f(emp_sa['tau'])}) é uma média ponderada dos dois e não descreve bem nenhum deles. Não é
manipulação: o IVS é o de 2010, fixo antes do programa.

## 4. D1 — contagem = oferta × taxa

Saltos local linear por corte (POR_CORTE). "Média abaixo → acima" é a média simples do outcome nas linhas usadas
de cada lado (nas taxas, a média ponderada pelas vagas, isto é, soma de N1 / soma de vagas). Taxas em %.

{tabela_d1(est, POR_CORTE)}

Empilhado (só comparação):

{tabela_d1(est, EMP)}

**Decomposição log-aditiva** nos municípios com N1 > 0. Na mesma amostra e com os mesmos pesos, o salto em
log(N1) é exatamente a soma dos saltos em log(vagas oferecidas) e em log(taxa). Os municípios com N1 = 0 ficam
de fora (contados por lado, nunca viram zero).

{tabela_log(est, POR_CORTE)}

Leitura por corte:

{lt['b']}

## 5. D2 — de onde vem a inclinação

### Médias por faixa de 0,010 da distância ao corte

Corte {c3} (ciclos juntos; uma linha por município × ciclo):

{tabela_faixas(est, c3)}

Corte {c4}:

{tabela_faixas(est, c4)}

Empilhado (só comparação; faixas da distância ao corte, os dois cortes misturados):

{tabela_faixas(est, EMPILHADO, EMP)}

{lt['a']}

### Inclinação de cada lado, com e sem log(pop)

Inclinação em vagas preenchidas por 0,010 de IVS; com ciclos juntos, é a média das retas dos ciclos ponderada pela
participação de cada ciclo no peso de kernel.

{tabela_inclinacoes(est, POR_CORTE)}

Empilhado (só comparação):

{tabela_inclinacoes(est, EMP)}

### Influência por município (leave-one-out)

Cada município da janela sai com todas as suas linhas de ciclo; Δ salto = salto com todos − salto sem ele.
Municípios na janela: {resumo['contagens']['influencia'][c3]['n_municipios']} no corte {c3} e
{resumo['contagens']['influencia'][c4]['n_municipios']} no corte {c4}. Todos estão em `ND_estimativas.csv`
(`tipo_linha = influencia`); abaixo, os {N_TOP} mais influentes.

N1 com controle (S-a), corte {c3}:

{tabela_top(est, c3, 'S-a')}

N1 com controle (S-a), corte {c4}:

{tabela_top(est, c4, 'S-a')}

Poisson com offset, corte {c3}:

{tabela_top(est, c3, 'poisson_offset')}

Poisson com offset, corte {c4}:

{tabela_top(est, c4, 'poisson_offset')}

### Sem os municípios mais populosos da janela

Salto retirando os k mais populosos da janela abaixo do corte, acima, ou dos dois lados. Taxa em p.p.; Poisson em
log; `*` = IC 95% que exclui zero.

Corte {c3}:

{tabela_sem_maiores(est, c3)}

{lista_retirados(est, c3)}

Corte {c4}:

{tabela_sem_maiores(est, c4)}

{lista_retirados(est, c4)}

Leitura:

{lt['influencia']}

## 6. D3 — forma da estimativa da taxa

Corte {c3}:

{tabela_d3(est, c3)}

Corte {c4}:

{tabela_d3(est, c4)}

Empilhado (só comparação):

{tabela_d3(est, EMPILHADO, EMP)}

{lt['d3']}

## 7. Por que o Poisson com offset é negativo se a taxa bruta é maior acima do corte

{lt['conciliacao']}

O Poisson com offset log(vagas oferecidas) estima a taxa **no nível da vaga** (cada vaga pesa igual, então os
municípios com muitas vagas, e muitas delas de cadastro reserva, dominam) e a avalia **no corte**, pela reta local
de cada lado. A taxa bruta das pistas é outra quantidade: média simples entre municípios (o município com uma vaga
imediata preenchida pesa o mesmo que uma capital), com as vagas imediatas no denominador (sem o cadastro reserva,
que quase não é preenchido na 1ª chamada) e na janela inteira, nas pistas com os dois cortes juntos. Por corte, a
média simples é maior acima nos dois cortes (tabela acima); o que muda o sinal em 0,300 é passar a contar cada vaga
igual, com o cadastro reserva no denominador, e olhar só perto do corte. As duas medidas não precisam ter o mesmo
sinal, e não têm.

## 8. D5 — o que o empilhamento faz

Peso efetivo omega de cada ciclo × corte no salto empilhado e contribuição omega × salto do grupo; a soma das
contribuições é exatamente o salto empilhado (resíduo máximo em `validacoes`).

N1 sem controle:

{tabela_d5(est, 'sem_controle')}

N1 com o controle do protocolo 48:

{tabela_d5(est, 'controle_protocolo_48')}

Empilhado contra cortes isolados:

{tabela_d5_cortes(est)}

{lt['d5']}

## 9. D4 — porte como covariável

Por corte:

{tabela_d4(est, POR_CORTE)}

Empilhado (só comparação):

{tabela_d4(est, EMP)}

## 10. Como evitar confusão

**Gráficos.**

- Mostrar **os cortes separados**, um painel por corte. Empilhar 0,300 e 0,400 junta um corte em que a taxa cai e
  outro em que a oferta cai, e a figura empilhada sugere um padrão único que nenhum dos dois tem.
- Mostrar **a taxa junto da contagem** (e, de preferência, as vagas oferecidas e a população por faixa), como em
  `ND_faixas_*.png`. Uma contagem sozinha mistura porte, oferta e preenchimento.
- Escrever no eixo horizontal que ele é **a distância ao corte (IVS − corte), não o IVS**. No empilhado, o mesmo
  ponto do eixo reúne municípios logo abaixo de 0,300 e logo abaixo de 0,400.
- Dar o número de municípios por faixa no texto ou numa tabela (não numa escala de tamanho dentro da figura) e
  assinalar quando uma faixa tem um município muito grande (média longe da mediana).
- Na figura com controle, dizer que o eixo vertical é N1 ajustado às vagas oferecidas, com um coeficiente por
  ciclo × corte, e não N1 observado.

**Interpretação.**

- Não ler a contagem de vagas preenchidas como **atração**. A atração dos candidatos (candidatos de 1ª opção por
  célula, F1.1 do E6) e a fração de células preenchidas (F1.3) não saltam em nenhum corte; a contagem sobe e desce
  com o porte e com as vagas abertas.
- A subida dentro da janela não diz que municípios mais vulneráveis atraem mais: diz que, perto destes cortes, os
  municípios com IVS logo abaixo incluem grandes capitais.
- O salto é do **pacote do corte**, não da bolsa sozinha; com controle, é condicional a vagas oferecidas que podem
  ter respondido ao pacote (doc 49, seção 4).
- Nada aqui muda o Holm do protocolo 48: lá nenhuma das quatro linhas rejeita zero, e este diagnóstico não
  escolhe outra especificação.
- Resultado com IC que contém zero é falta de evidência com a precisão relatada, não ausência de efeito; resultado
  que exclui zero numa linha diagnóstica, sem correção por comparações múltiplas, não é descoberta.

## 11. Apêndice — por ciclo (ciclo × corte, EP HC1)

Saltos; taxa em p.p.; `*` = IC 95% que exclui zero.

{tabela_apendice(est)}

## 12. Figuras

Todas em 16:9, com um painel por corte (0,300 à esquerda, 0,400 à direita). A imagem traz só o gráfico; o "Como ler" fica abaixo de cada uma e também em `como_ler` de cada figura em `ND_resumo.json`. As figuras do adendo AD2 ficam na seção 14.

{figs}

## 13. Validações e integridade

| Conferência | Resultado |
|---|---|
| saltos por corte e empilhados de S-a, S-b, S-d (offset) e S-e reproduzem `N_estimativas.csv` | {len(val['doc49']['linhas_conferidas'])} linhas; max abs dif = {val['doc49']['max_abs_dif']:.1e} |
| decomposição log-aditiva fecha | {val['log_aditiva']['linhas']} amostras; max abs resíduo = {val['log_aditiva']['max_abs_residuo']:.1e} |
| salto empilhado = soma omega × salto do grupo | {val['omega']['linhas']} identidades; max abs resíduo = {val['omega']['max_abs_residuo']:.1e} |
| adendo AD2: salto da taxa com ciclos juntos = soma omega × salto do ciclo | {val['omega_adendo2']['linhas']} identidades; max abs resíduo = {val['omega_adendo2']['max_abs_residuo']:.1e} |
| linhas em `ND_estimativas.csv` | {cont['linhas']} |
| EXECUTADO / SEM_ESTIMATIVA / NAO_EXECUTADO | {cont['executado']} / {cont['sem_estimativa']} / {cont['nao_executado']} |
| linhas município × ciclo sem vaga imediata (taxa com vagas imediatas ausente, nunca zero) | {cont['linhas_sem_vaga_imediata']} |
| linhas município × ciclo com N1 = 0 (fora da decomposição em log, nunca zero) | {cont['linhas_n1_zero']} |
| municípios do quadro sem IVS 2010 oficial (fora da RDD) | {cont['municipios_sem_ivs_fora']} |

Nada imputado ou simulado; a running variable é o IVS 2010 oficial do Ipea (a08), conferido contra as saídas da
tarefa B; o arquivo local de IVS da auditoria 16 não é lido; `data/` é só lido.

"""
    doc = doc + secao_adendo2(est, resumo) + figs_ad2 + "\n"
    return re.sub(r"(?<![\w.])0\.(\d{3})\b", r"0,\1", doc)


COMO_LER.update({
    "ND_adendo_cr_taxas.png": "Cada linha acompanha, trecho a trecho, a parte das vagas que é cadastro reserva e as duas "
                              "formas de medir o preenchimento. Mostra se a taxa cai no corte junto com mais vagas de "
                              "cadastro reserva.",
    "ND_adendo_ciclos.png": "Cada ponto é o salto no corte em um ciclo, com seu intervalo de confiança. Mostra de que "
                            "ciclo vem a queda da taxa.",
})
DETALHE_FIG.update({
    "ND_adendo_cr_taxas.png": "Adendo AD2. Por faixa de 0,010 da distância ao corte, ciclos juntos: fração de cadastro "
                              "reserva (soma de CR / soma das vagas oferecidas), taxa por vaga oferecida (soma de N1 / "
                              "soma das vagas oferecidas) e taxa só com vagas imediatas (soma de N1 / soma das vagas "
                              "imediatas). Anotação = salto local linear da fração de CR (peso = vagas oferecidas, CR1).",
    "ND_adendo_ciclos.png": "Adendo AD2. Saltos local linear por ciclo × corte (EP HC1) da taxa ponderada pelas vagas "
                            "oferecidas e da fração de CR, em p.p.; a última linha é o salto com os ciclos juntos (CR1).",
})


def gerar_figuras_adendo2(est: pd.DataFrame, dir_fig: Path) -> list[dict]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter
    feitas = []
    fmt_y = FuncFormatter(lambda v, _=None: f"{v:g}".replace(".", ",").replace("-", "−"))
    fx = est[(est["adendo"] == ADENDO2) & (est["tipo_linha"] == "faixa_cr")].copy()
    fx["meio"] = (fx["faixa_inf"].astype(float) + fx["faixa_sup"].astype(float)) / 2
    series = (("fracao_cr", "#7a5195", "s", "parte das vagas que é cadastro reserva"),
              ("taxa_vic_ponderada", COR_AB, "o", "preenchidas / vagas oferecidas"),
              ("taxa_vi_ponderada", COR_AC, "^", "preenchidas / vagas imediatas"))
    fig, axs = plt.subplots(1, 2, figsize=TAMANHO_FIG, facecolor=SUPERF, sharey=True)
    for ax, c in zip(axs, CORTES):
        sub = fx[fx["corte"] == ROTULO_CORTE[c]].sort_values("meio")
        for col, cor, mk, rot in series:
            for j, lado in enumerate(("abaixo", "acima")):
                s = sub[sub["lado"] == lado]
                ax.plot(s["meio"], s[col].astype(float), marker=mk, color=cor, lw=1.4, ms=7,
                        label=rot if j == 0 else None)
        ax.axvline(0, color=TINTA, ls="--", lw=0.9)
        r = _sel(est, adendo=ADENDO2, diagnostico="AD2_A1", tipo_linha="estimativa", corte=ROTULO_CORTE[c],
                 outcome="FRAC_CR").iloc[0]
        ax.text(0.02, 0.97, f"salto na parte de cadastro reserva: {_num(100 * float(r['tau']), 1)} p.p. "
                f"[{_num(100 * float(r['ic95_inf']), 1)}; {_num(100 * float(r['ic95_sup']), 1)}]",
                transform=ax.transAxes, fontsize=8.5, va="top", ha="left", color=TINTA,
                bbox={"boxstyle": "round,pad=0.25", "fc": "white", "ec": "#d0cfca", "lw": 0.6})
        ax.set_title(f"corte {ROTULO_CORTE[c].replace('.', ',')}", fontsize=12, color=TINTA)
        ax.set_xlabel("distância ao corte (IVS − corte)", fontsize=10)
        ax.xaxis.set_major_formatter(FuncFormatter(_fx))
        ax.yaxis.set_major_formatter(fmt_y)
        ax.set_facecolor(SUPERF)
        ax.grid(alpha=0.25)
    axs[0].set_ylabel("fração", fontsize=10)
    axs[1].legend(fontsize=8.5, loc="lower right", frameon=False)
    fig.suptitle("Cadastro reserva e taxa de preenchimento perto do corte", fontsize=13, color=TINTA)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    nome = "ND_adendo_cr_taxas.png"
    fig.savefig(dir_fig / nome, dpi=110, facecolor=fig.get_facecolor())
    plt.close(fig)
    feitas.append({"arquivo": rotulo(dir_fig / nome), "fonte": "ND_estimativas.csv, adendo = AD2, tipo_linha = faixa_cr",
                   "como_ler": COMO_LER[nome], "adendo": ADENDO2})

    fig, axs = plt.subplots(1, 2, figsize=TAMANHO_FIG, facecolor=SUPERF, sharey=True)
    for ax, c in zip(axs, CORTES):
        rotulos = [f"ciclo {k}" for k in CICLOS] + ["ciclos juntos"]
        yy = np.arange(len(rotulos))[::-1]
        for desl, (oid, cor, mk, leg) in zip((0.12, -0.12), (("TAXA_VIC", COR_AB, "o", "taxa por vaga oferecida"),
                                                              ("FRAC_CR", "#7a5195", "s", "parte de cadastro reserva"))):
            rs = [_um(est, adendo=ADENDO2, diagnostico="AD2_A3", tipo_linha="estimativa", populacao=f"V{k}",
                      corte=ROTULO_CORTE[c], outcome=oid) for k in CICLOS]
            rs.append(_um(est, adendo=ADENDO2, diagnostico="AD2_A1" if oid == "FRAC_CR" else "AD2_A2",
                          tipo_linha="estimativa", corte=ROTULO_CORTE[c], outcome=oid,
                          **({} if oid == "FRAC_CR" else {"variante": "vic_vaga_todos"})))
            v = np.array([100 * float(r["tau"]) for r in rs])
            lo = np.array([100 * float(r["ic95_inf"]) for r in rs])
            hi = np.array([100 * float(r["ic95_sup"]) for r in rs])
            ax.errorbar(v, yy + desl, xerr=[v - lo, hi - v], fmt=mk, color=cor, ecolor=cor, capsize=2, ms=6, label=leg)
        ax.axvline(0, color=TINTA, lw=0.8)
        ax.set_yticks(yy)
        ax.set_yticklabels(rotulos, fontsize=10)
        ax.set_title(f"corte {ROTULO_CORTE[c].replace('.', ',')}", fontsize=12, color=TINTA)
        ax.set_xlabel("salto no corte (pontos percentuais)", fontsize=10)
        ax.set_facecolor(SUPERF)
        ax.grid(alpha=0.25, axis="x")
    axs[1].legend(fontsize=8.5, loc="lower right", frameon=False)
    fig.suptitle("Salto na taxa e na parte de cadastro reserva, por ciclo", fontsize=13, color=TINTA)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    nome = "ND_adendo_ciclos.png"
    fig.savefig(dir_fig / nome, dpi=110, facecolor=fig.get_facecolor())
    plt.close(fig)
    feitas.append({"arquivo": rotulo(dir_fig / nome), "fonte": "ND_estimativas.csv, adendo = AD2, AD2_A1/A2/A3",
                   "como_ler": COMO_LER[nome], "adendo": ADENDO2})
    return feitas


def secao_adendo2(est: pd.DataFrame, resumo: dict) -> str:
    ad = resumo["adendo_2026_10_21"]
    c3, c4 = ROTULO_CORTE[300], ROTULO_CORTE[400]

    def R(**f):
        return _um(est, adendo=ADENDO2, **f)

    def lin(r, pct=True, casas=1):
        return f"{_f(r['tau'], casas, pct=pct)} {_ic(r, casas, pct)}"

    conj = "\n".join(f"- **{d['id']}, {d['nome']}:** " + "; ".join(d["itens"]) + "." for d in ad["conjunto_fixo"])
    # A1
    a1 = []
    for oid in ("FRAC_CR", "CR", "VI", "TAXA_SO_IMED", "TAXA_SO_CR"):
        cel = [{"FRAC_CR": "parte das vagas que é cadastro reserva (%)", "CR": "vagas de cadastro reserva",
                "VI": "vagas imediatas", "TAXA_SO_IMED": "taxa nas células só de vagas imediatas (%)",
                "TAXA_SO_CR": "taxa nas células só de cadastro reserva (%)"}[oid]]
        for corte in (c3, c4):
            r = R(diagnostico="AD2_A1", tipo_linha="estimativa", corte=corte, outcome=oid)
            pct = oid in ("FRAC_CR", "TAXA_SO_IMED", "TAXA_SO_CR")
            fora = (f" ({_int(r['n_fora_abaixo'])} / {_int(r['n_fora_acima'])} fora)"
                    if str(r["n_fora_abaixo"]) not in ("nan", "") else "")
            cel += [f"{_f(r['media_abaixo'], 1, False, pct)} → {_f(r['media_acima'], 1, False, pct)}",
                    f"{lin(r, pct, 1 if pct else 2)}{fora}", _p(r)]
        a1.append(cel)
    tab_a1 = _tab(["Variável", f"{c3}: média abaixo → acima", f"{c3}: salto [IC 95%]", f"{c3}: p",
                   f"{c4}: média abaixo → acima", f"{c4}: salto [IC 95%]", f"{c4}: p"], a1)
    tipos = ad["taxa_separada_por_tipo_de_vaga"]["celulas_por_tipo"]
    tab_tipos = _tab(["Ciclo / tipo de célula", "células", "vagas imediatas", "vagas de CR", "alocados na 1ª chamada"],
                     [[k.replace("so_imed", "só imediatas").replace("so_cr", "só CR"), _f(v["celulas"], 0, False),
                       _f(v["vagas_imediatas"], 0, False), _f(v["vagas_cr"], 0, False), _f(v["alocados"], 0, False)]
                      for k, v in tipos.items()])
    # A2
    rot2 = {"vic_vaga_todos": ("imediatas + CR", "vaga", "todos"),
            "vic_vaga_com_vi": ("imediatas + CR", "vaga", "só com vaga imediata"),
            "vi_vaga_com_vi": ("imediatas", "vaga", "só com vaga imediata"),
            "vic_municipio_todos": ("imediatas + CR", "município", "todos"),
            "vic_municipio_com_vi": ("imediatas + CR", "município", "só com vaga imediata"),
            "vi_municipio_com_vi": ("imediatas", "município", "só com vaga imediata")}
    a2 = []
    for nome, (den, peso, am) in rot2.items():
        r3 = R(diagnostico="AD2_A2", tipo_linha="estimativa", corte=c3, variante=nome)
        r4 = R(diagnostico="AD2_A2", tipo_linha="estimativa", corte=c4, variante=nome)
        a2.append([den, peso, am, f"{_int(r3['n_abaixo'])} / {_int(r3['n_acima'])}", lin(r3), _p(r3), lin(r4)])
    tab_a2 = _tab(["Denominador", "cada um pesa igual", "municípios", f"{c3}: n abaixo / acima",
                   f"{c3}: salto [IC 95%] (p.p.)", f"{c3}: p", f"{c4}: salto [IC 95%] (p.p.)"], a2)
    passos = []
    for ordem, rot in (("ordem_denominador_primeiro", "denominador antes do peso"), ("ordem_peso_primeiro",
                                                                                   "peso antes do denominador")):
        for i in (1, 2, 3):
            r = R(diagnostico="AD2_A2", tipo_linha="decomposicao", corte=c3, especificacao=ordem, variante=f"passo_{i}")
            passos.append([rot, str(i), r["grupo"], _f(r["tau_grupo"], 1, pct=True), _f(r["tau"], 1, pct=True),
                           _f(r["contribuicao"], 1, pct=True)])
    tab_passos = _tab(["Ordem", "passo", "o que muda", "salto antes (p.p.)", "salto depois (p.p.)",
                       "mudança (p.p.)"], passos)
    # A3
    a3 = []
    for k in CICLOS:
        for corte in (c3, c4):
            cel = [str(k), corte]
            for oid in ("TAXA_VIC", "TAXA_VI", "FRAC_CR"):
                r = R(diagnostico="AD2_A3", tipo_linha="estimativa", populacao=f"V{k}", corte=corte, outcome=oid)
                cel.append(f"{_f(r['tau'], 1, pct=True)}{'*' if _excl(r) else ''}")
            co = R(diagnostico="AD2_A3", tipo_linha="contribuicao", corte=corte, outcome="TAXA_VIC",
                   variante=f"grupo_c{k}")
            cel += [_f(co["peso_omega"], 3, False), _f(co["contribuicao"], 1, pct=True)]
            a3.append(cel)
    tab_a3 = _tab(["Ciclo", "Corte", "taxa por vaga oferecida (p.p.)", "taxa só imediatas (p.p.)",
                   "parte de CR (p.p.)", "peso omega no salto com ciclos juntos", "contribuição (p.p.)"], a3)
    # A4
    a4 = []
    base = R(diagnostico="AD2_A2", tipo_linha="estimativa", corte=c3, variante="vic_vaga_todos")
    sub = _sel(est, adendo=ADENDO2, tipo_linha="influencia_vaga").copy()
    sub["po"] = sub["posto"].astype(int)
    for _, r in sub.sort_values("po").iterrows():
        a4.append([_int(r["posto"]), r["co_ibge"], str(r["nome_municipio"]), _f(r["vagas_oferecidas_ciclos"], 0, False),
                   _f(r["vagas_imediatas_ciclos"], 0, False), _f(r["vagas_cr_ciclos"], 0, False),
                   _f(r["n_alocados_ciclos"], 0, False), r["lado"], _fx(float(r["distancia"])),
                   f"{_f(r['tau'], 1, pct=True)} {_ic(r, 1, True)}", _f(r["delta_tau"], 1, pct=True)])
    tab_a4 = _tab(["Posto", "co_ibge", "Município", "vagas oferecidas", "imediatas", "CR", "alocados", "lado",
                   "distância", "salto sem ele (p.p.)", "Δ (p.p.)"], a4)

    # Resposta curta, por regra a partir das linhas gravadas.
    fcr3 = R(diagnostico="AD2_A1", tipo_linha="estimativa", corte=c3, outcome="FRAC_CR")
    fcr4 = R(diagnostico="AD2_A1", tipo_linha="estimativa", corte=c4, outcome="FRAC_CR")
    vi_vaga = R(diagnostico="AD2_A2", tipo_linha="estimativa", corte=c3, variante="vi_vaga_com_vi")
    vic_mun = R(diagnostico="AD2_A2", tipo_linha="estimativa", corte=c3, variante="vic_municipio_todos")
    vi_mun = R(diagnostico="AD2_A2", tipo_linha="estimativa", corte=c3, variante="vi_municipio_com_vi")
    so_imed = R(diagnostico="AD2_A1", tipo_linha="estimativa", corte=c3, outcome="TAXA_SO_IMED")
    so_cr = R(diagnostico="AD2_A1", tipo_linha="estimativa", corte=c3, outcome="TAXA_SO_CR")
    contr = {k: R(diagnostico="AD2_A3", tipo_linha="contribuicao", corte=c3, outcome="TAXA_VIC", variante=f"grupo_c{k}")
             for k in CICLOS}
    c2 = R(diagnostico="AD2_A3", tipo_linha="estimativa", populacao="V2", corte=c3, outcome="TAXA_VIC")
    maxd = float(sub["delta_tau"].astype(float).abs().max())
    frac_c2 = float(contr[2]["contribuicao"]) / float(base["tau"])
    cr_sustenta = _excl(fcr3) and not _excl(fcr4) and abs(float(vi_vaga["tau"])) < abs(float(base["tau"])) / 2
    cr_coincide = _excl(fcr3) and not _excl(fcr4)
    c2_sustenta = frac_c2 > 0.5
    grandes = maxd > abs(float(base["tau"])) / 4
    veredito = ("cadastro reserva" if cr_sustenta else
                "ciclo 2, que responde por cerca de metade do salto; nenhum suspeito explica a queda inteira"
                if c2_sustenta else "peso das cidades grandes" if grandes else "nenhum dos três sozinho")
    fcr_c2 = R(diagnostico="AD2_A3", tipo_linha="estimativa", populacao="V2", corte=c3, outcome="FRAC_CR")
    vi_c2 = R(diagnostico="AD2_A3", tipo_linha="estimativa", populacao="V2", corte=c3, outcome="TAXA_VI")
    vi_c3 = R(diagnostico="AD2_A3", tipo_linha="estimativa", populacao="V3", corte=c3, outcome="TAXA_VI")
    al_cr_c2 = resumo["adendo_2026_10_21"]["taxa_separada_por_tipo_de_vaga"]["celulas_por_tipo"]["ciclo 2 / so_cr"]["alocados"]
    resposta = (
        f"**Qual suspeito se sustenta: {veredito}.** "
        f"(1) **Cadastro reserva:** a parte das vagas que é cadastro reserva sobe no corte {c3} "
        f"({lin(fcr3)} p.p., {'exclui' if _excl(fcr3) else 'contém'} zero) e não em {c4} ({lin(fcr4)} p.p.). Mas, se a "
        f"queda fosse só efeito de mais vagas de reserva no denominador, ela sumiria ao contar só as vagas imediatas, e "
        f"não some: {lin(vi_vaga)} p.p. Nas células puras, a taxa das células só de vagas imediatas também é menor "
        f"acima ({lin(so_imed)} p.p.) e a das células só de reserva quase não muda ({lin(so_cr)} p.p.); os dois IC "
        f"contêm zero. O cadastro reserva {'coincide com a queda, mas não a explica sozinho' if cr_coincide and not cr_sustenta else 'explica a queda' if cr_sustenta else 'não acompanha a queda'}. "
        f"(2) **Ciclo 2:** é o ciclo com a maior queda ({lin(c2)} p.p.) e responde por "
        f"{_f(100 * frac_c2, 0, False)} % do salto com os ciclos juntos ({_f(contr[2]['contribuicao'], 1, pct=True)} de "
        f"{_f(base['tau'], 1, pct=True)} p.p.); o ciclo 3 contribui {_f(contr[3]['contribuicao'], 1, pct=True)} e o "
        f"ciclo 1, {_f(contr[1]['contribuicao'], 1, pct=True)}. "
        f"No ciclo 2, a parte de cadastro reserva sobe no corte ({lin(fcr_c2)} p.p.), e as células só de reserva têm "
        f"{_f(al_cr_c2, 0, False)} alocados na 1ª chamada {NOTA_A36_C2}: com esse quadro, mais reserva no "
        f"denominador baixa a taxa por vaga oferecida, e contando só as vagas imediatas a queda do ciclo 2 fica em "
        f"{lin(vi_c2)} p.p. Nos ciclos juntos isso não basta, porque no ciclo 3 a taxa só com vagas imediatas também "
        f"cai ({lin(vi_c3)} p.p., IC largo). "
        f"(3) **Peso das cidades grandes:** tirar qualquer um dos {N_TOP_VAGA} municípios com mais vagas oferecidas "
        f"muda o salto em no máximo {_f(100 * maxd, 1, False)} p.p. Trocar o peso de vaga para município leva o salto a "
        f"{lin(vic_mun)} p.p.; só a combinação das duas trocas (vagas imediatas no denominador e cada município "
        f"pesando igual) o leva a {lin(vi_mun)} p.p. A decomposição não é aditiva: a ordem das trocas muda quanto cabe "
        f"a cada uma (tabela de passos). **Força da evidência:** a queda da taxa por vaga oferecida em {c3} é "
        f"estatisticamente nítida na medida principal (p = {_p(base)}), mas não há um único suspeito que a explique; "
        f"é uma linha diagnóstica, sem correção por comparações múltiplas, e descreve o pacote do corte, não a bolsa "
        f"sozinha.")

    return f"""## 14. Adendo: a queda da taxa em 0,300

> **Adendo de {ad['data'][8:10]}/{ad['data'][5:7]}/{ad['data'][:4]}** (`adendo = {ADENDO2}` em `ND_estimativas.csv`;
> `adendo_2026_10_21` em `ND_resumo.json`). Fora do protocolo 48; nada aqui vira especificação principal.<br>
> **Pergunta:** {ad['pergunta']}.<br>
> **O que já tinha sido visto:** {ad['ja_visto']}.<br>
> **Especificação:** {ad['especificacao']}.

**Conjunto fixo, listado antes de rodar** (todos relatados):

{conj}

### Resposta curta

{resposta}

### A1 — cadastro reserva

{tab_a1}

A taxa separada por tipo de vaga só existe em parte: {ad['taxa_separada_por_tipo_de_vaga']['motivo']}.
Células por tipo (todos os municípios do quadro):

{tab_tipos}

### A2 — denominador, peso e amostra, um elemento por vez

{tab_a2}

Passos, no corte {c3}, do salto principal (imediatas + CR, peso por vaga, todos os municípios) até a taxa só com vagas
imediatas e cada município pesando igual:

{tab_passos}

### A3 — por ciclo

Saltos ciclo × corte (EP HC1); `*` = IC 95% que exclui zero. O peso omega e a contribuição referem-se ao salto da
taxa por vaga oferecida com os ciclos juntos (a soma das contribuições é o salto com os ciclos juntos).

{tab_a3}

### A4 — os {N_TOP_VAGA} municípios com mais vagas oferecidas na janela de {c3}

Salto da taxa ponderada com todos: {lin(base)} p.p.

{tab_a4}

### Figuras do adendo

"""


def ler_saidas() -> tuple[pd.DataFrame, dict]:
    est = pd.read_csv(OUT / NOME_EST, dtype={"corte": str, "ciclo": str, "co_ibge": str, "faixa": str})
    for c in ("nota", "motivo_fora", "grupo", "lado", "maior_municipio", "nome_municipio", "retirados", "peso",
              "estimador", "co_ibge", "faixa", "unidade"):
        est[c] = est[c].fillna("")
    resumo = json.loads((OUT / NOME_RESUMO).read_text(encoding="utf-8"))
    return est, resumo


def atualizar_doc() -> None:
    est, resumo = ler_saidas()
    DOC.write_text(gerar_doc(est, resumo), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--atualizar-doc", action="store_true", help="so regrava o doc 49b a partir das saidas")
    args = ap.parse_args(argv)
    if args.atualizar_doc:
        atualizar_doc()
        return 0
    rv = E6.ler_running_variable()
    pops, conf_pop = E6.chaves_populacoes(rv)
    V0, _U, info = T23.carregar(rv, pops)
    a08 = pd.read_csv(A08, dtype={"co_ibge": str}, usecols=["co_ibge", "nome_municipio_uf"])
    a08["co_ibge"] = a08["co_ibge"].str.zfill(6)
    V = preparar(V0, a08.set_index("co_ibge")["nome_municipio_uf"])
    cel = pd.read_parquet(T23.ARQ_VC, columns=["ciclo", "co_ibge", "vagas_imediatas", "vagas_cr", "n_alocados_ch1"])
    agg, info_cel = agregar_celulas(cel)
    V = preparar_adendo2(V, agg)
    est, extras = estimar_tudo(V)
    nucleo = ["tau", "ep", "ic95_inf", "ic95_sup", "p_valor"]
    est_ = est[est["tipo_linha"] == "estimativa"]
    sem_nota = est_[est_[nucleo].isna().any(axis=1) & (est_["nota"].fillna("") == "")]
    if len(sem_nota):
        raise FalhaValidacao(f"{len(sem_nota)} linhas com NaN sem nota")
    conf49 = conferir_doc49(est)
    OUT.mkdir(parents=True, exist_ok=True)
    est.to_csv(OUT / NOME_EST, index=False)
    figs = gerar_figuras(est, OUT / DIR_FIG)
    figs += gerar_figuras_adendo2(est, OUT / DIR_FIG)
    todas = pd.concat(V.values(), ignore_index=True)
    contagens = {
        "linhas": int(len(est)), "executado": int((est["status"] == "EXECUTADO").sum()),
        "sem_estimativa": int((est["status"] == "SEM_ESTIMATIVA").sum()),
        "nao_executado": int((est["status"] == "NAO_EXECUTADO").sum()),
        "por_diagnostico": est["diagnostico"].value_counts().sort_index().to_dict(),
        "por_tipo_linha": est["tipo_linha"].value_counts().sort_index().to_dict(),
        "linhas_sem_vaga_imediata": int((todas["vagas_imediatas"] == 0).sum()),
        "linhas_n1_zero": int((todas["n_alocados_ch1"] == 0).sum()),
        "municipios_sem_ivs_fora": int(sum(v["municipios_sem_ivs_fora"] for v in info.values())),
        "influencia": extras["influencia"],
    }
    entradas = [
        E6.bloco_entrada(A08, "running variable (IVS 2010 oficial) e nome do municipio", "Ipea, Atlas da "
                         "Vulnerabilidade Social (a08)", "Censo 2010", f"{len(rv)} municipios", "municipio", "co_ibge",
                         "ivs, nome_municipio_uf"),
        E6.bloco_entrada(ARQ_VM, "N1, vagas oferecidas, celulas e populacao 2022 (V1-V3)", "tarefa B "
                         "(12_construir_outcomes_funil.py)", "ver dicionario",
                         ", ".join(f"V{k}: {len(d)}" for k, d in V.items()), "municipio x ciclo", "ciclo, co_ibge",
                         "municipios sem IVS oficial fora"),
        E6.bloco_entrada(T23.ARQ_U, "conferencia do IVS e das colunas de oferta (funcoes do script 23)", "tarefa B",
                         "ver dicionario", "-", "municipio", "co_ibge", "nenhum"),
        E6.bloco_entrada(E6.ARQ_G3, "conferencia do IVS da tarefa B (funcao do E6)", "tarefa B", "ver dicionario", "-",
                         "municipio", "co_ibge", "so co_ibge e ivs_2010_oficial"),
        E6.bloco_entrada(T23.ARQ_VC, "adendo AD2: vagas e alocados por tipo de celula (so imediatas, so CR, mista)",
                         "tarefa B", "ver dicionario", f"{len(cel)} celulas", "celula CNES x curso x ciclo",
                         "ciclo, co_ibge", "colunas vagas_imediatas, vagas_cr, n_alocados_ch1"),
        E6.bloco_entrada(N_EST, "alvo de conferencia (S-a, S-b, S-d, S-e por corte e empilhados)",
                         "23_estimar_contagem_vagas.py", "2026-10-19", "-", "linha de estimativa",
                         "outcome_id, populacao, corte, especificacao, variante", "N1, V1+V2+V3"),
    ]
    resumo = {
        "etapa": "ND_diagnostico_contagem_porte",
        "natureza_dos_dados": NATUREZA,
        "estatuto": ESTATUTO,
        "data_execucao": DATA_EXECUCAO,
        "script": rotulo(Path(__file__)),
        "contraste": CONTRASTE,
        "salto": "tau = lado com bolsa maior (s > c) menos lado com bolsa menor; o corte pertence ao lado inferior",
        "nao_muda": "nao substitui a S-a empilhada do protocolo 48, nao muda o Holm do protocolo 48 nem as conclusoes "
                    "do doc 49; nenhuma variante daqui vira especificacao principal",
        "diagnosticos": DIAGNOSTICOS,
        "amostras": {POR_CORTE: "um corte por vez; ciclos 1-3 juntos com intercepto e inclinacoes por ciclo, salto "
                                "comum, CR1 por municipio; h = 0,050, kernel triangular",
                     APENDICE: "ciclo x corte, local linear, EP HC1",
                     EMP: "ciclos e cortes empilhados (amostra da figura do doc 49), so comparacao"},
        "parametros": {"h_mil": H, "h_D3_mil": list(H_D3), "janelas_local_constante_mil": list(JANELAS_LC),
                       "janela_adendo_AD1_mil": JANELA_LC_ADENDO, "h_local_quadratico_mil": H_QUAD, "k_maiores": list(KS),
                       "n_top_influencia": N_TOP, "largura_faixa_mil": LARGURA_FAIXA},
        "exposicao_previa": EXPOSICAO_PREVIA,
        "adendos": ADENDOS,
        "adendo_2026_10_21": {**ADENDO2_DESC, "taxa_separada_por_tipo_de_vaga": {
            "situacao": "PARCIAL", "motivo": MOTIVO_SEPARADA, "celulas_por_tipo": info_cel}},
        "entradas": entradas,
        "validacoes": {
            "populacoes": conf_pop,
            "doc49": conf49,
            "log_aditiva": {"linhas": len(extras["residuos_log"]),
                            "max_abs_residuo": float(np.max(np.abs(extras["residuos_log"])))},
            "omega": {"linhas": len(extras["residuos_omega"]),
                      "max_abs_residuo": float(np.max(np.abs(extras["residuos_omega"])))},
            "omega_adendo2": {"linhas": len(extras["residuos_omega_ad2"]),
                              "max_abs_residuo": float(np.max(np.abs(extras["residuos_omega_ad2"])))},
        },
        "contagens": contagens,
        "decisoes": [
            "Taxa ponderada = N1 / vagas com peso = kernel x vagas (a S-e do script 23); com as vagas oferecidas "
            "(imediatas + CR, forma principal do protocolo 48) e com as imediatas (forma de sensibilidade).",
            "Covariaveis (log pop, vagas) entram como no script 23: centradas na media ponderada pelo kernel do grupo, "
            "um coeficiente por grupo (ciclo), comum aos dois lados.",
            "Local constante: kernel uniforme em |x| <= w (IVS em milesimos inteiros; h = w + 0,5 milesimo), "
            "intercepto por ciclo como dummies comuns aos dois lados, CR1 por municipio.",
            "Local quadratico: x^2 e T x^2 por grupo como colunas extras (curvatura propria de cada lado).",
            "Influencia: leave-one-out por municipio (todas as linhas de ciclo saem juntas); o salto base e o da "
            "amostra POR_CORTE.",
            "Sem os maiores: os k municipios de maior populacao 2022 na janela do lado indicado (empate pelo co_ibge).",
            "D5: omega = pesos_grupos da rdd_lib; salto do grupo = local linear so do ciclo x corte; a identidade "
            "salto empilhado = soma omega x salto do grupo e exata (Frisch-Waugh-Lovell) e conferida.",
        ],
        "saidas": {NOME_EST: {"arquivo": rotulo(OUT / NOME_EST), "sha256": sha256(OUT / NOME_EST)},
                   "figuras": [dict(f, sha256=sha256(ROOT / f["arquivo"])) for f in figs]},
        "linguagem": "diagnostico descritivo do pacote do corte; nada aqui e efeito da participacao no PMM-E nem do "
                     "degrau de R$ 5 mil isolado",
    }
    T23._gravar_json(OUT / NOME_RESUMO, resumo)
    atualizar_doc()
    print(f"ND: {len(est)} linhas; doc {rotulo(DOC)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except FalhaValidacao as erro:
        print(f"FALHA DE VALIDACAO: {erro}", file=sys.stderr)
        sys.exit(2)
