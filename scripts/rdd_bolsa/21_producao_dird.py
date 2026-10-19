"""D1 do protocolo 47: diferença em descontinuidades (DiRD) da produção especializada nos cortes da bolsa (família K).

Protocolo congelado: `docs/06_execucao/47_protocolo_producao_especializada.md`
(§3, §4, §5 D1, §6, §7 e os adendos §10 e §11, todos anteriores a qualquer
contraste), com o desenho do E7 (protocolo 40, §5–§6 e §13). Estatuto: posterior
à síntese E8. Toda linha sai com `estatuto = PROTOCOLO_47_POS_SINTESE` e
`natureza_dos_dados = EMPIRICO`. A família K tem Holm próprio (K1–K3) e não
mexe no Holm de P1 e P2 do protocolo 40 nem em saída anterior.

Contraste
---------
Running variable: IVS 2010 oficial do Ipea (a08), em milésimos; cortes 300 e
400; T = 1[s > c]; salto = lado de bolsa maior menos lado de bolsa menor.
DiRD (ΔY = média(pós) − média(pré)): anúncio de +R$ 5 mil por mês na bolsa do
PMM-E **mais a variação, entre pré e pós, das descontinuidades das outras
políticas nos mesmos cortes** (auditoria 18). Identifica, no máximo, o incentivo
marginal; não é efeito da participação no PMM-E nem do Agora Tem Especialistas.
RDD em nível (linhas `nivel_*`) é o pacote do corte.

Insumos (todos conferidos pelo SHA-256 do manifesto da aquisição)
-----------------------------------------------------------------
- SIA/SUS (a12): quantidade aprovada por município de atendimento × mês de
  processamento × subgrupo × conjunto de CBO. `-` do TabNet é zero
  (`zero_tabnet`); subgrupo que não veio como coluna é zero daquela consulta
  (validação V4 do a12); município ausente da resposta fica ausente.
- SIH/SUS (a13): AIH aprovadas do grupo 04 por município de internação × mês de
  processamento; `ausente_uf_mes_sem_dado` fica ausente; `uf_mes_atipico` só
  entra na sensibilidade.
- TISS/ANS (a14): quantidade informada (`qt_itens`) por município do prestador
  × mês de realização × tipo × grupo de CBO; `ausente_*` fica ausente;
  `arquivo_presente_municipio_sem_evento` é zero de eventos reportados. UF-mês
  sinalizado em `alertas_queda` só sai na sensibilidade (§11.4).
- CNES nacional (a09): vínculos e horas não SUS das CBO-alvo (total − SUS);
  nenhuma competência >= 202609 é lida.
- Censo 2022 (o mesmo arquivo do E7) como denominador; município sem população
  ou sem IVS oficial fica fora e é contado (por exemplo, 510183).

Janelas (§4, §10, §11)
----------------------
pré 202406–202506 em todos; pós de K1, K2 e das secundárias SIA/SIH/CNES
202510–202605 (§10.1; até 202607 é sensibilidade; K4 também até 202608, a
janela do E7); pós de K3, K3a, K3b, K3c e K5 202510–202512 (§2; 202510–202511
é sensibilidade, §11.4). Placebo dentro do pré (KP3): média(202412–202505) −
média(202406–202411). Pré extra (S5): 202201–202303. Estudo de evento: mês a
mês contra 202506, desde 202201.

Saídas
------
output/rdd_bolsa/K_D1_estimativas.csv, K_D1_estudo_evento.csv, K_D1_resumo.json
e K_D1_figuras/*.png; tabelas entre marcadores `<!-- K:...:inicio/fim -->` de
`docs/06_execucao/50_resultados_producao_especializada.md`.

Uso
---
    python3 scripts/rdd_bolsa/21_producao_dird.py
    python3 scripts/rdd_bolsa/21_producao_dird.py --atualizar-doc
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

ROOT = Path(__file__).resolve().parents[2]
DIR_RDD = ROOT / "scripts" / "rdd_bolsa"


def _importar(caminho: Path, nome: str):
    if nome in sys.modules:
        return sys.modules[nome]
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    return mod


_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
L = _importar(DIR_RDD / "rdd_lib.py", "rdd_lib_k")
E7 = _importar(DIR_RDD / "14_estimar_E7_dird_cnes.py", "e7_para_k")
sys.dont_write_bytecode = _bytecode

# ---------------------------------------------------------------------------
# Caminhos e parâmetros do protocolo (constantes permitidas: cortes, h, meses, datas de atos)
# ---------------------------------------------------------------------------

OUT = ROOT / "output" / "rdd_bolsa"
AQ = ROOT / "output" / "aquisicao"
SIA = AQ / "sia" / "painel_sia_municipio_mes_subgrupo_cbo.parquet"
SIA_SUBG = AQ / "sia" / "sia_subgrupos_por_consulta.csv"
SIA_MUN = AQ / "sia" / "sia_municipios_tabnet.csv"
MANIF_SIA = AQ / "sia" / "manifesto_sia.json"
SIH = AQ / "sih" / "painel_sih_municipio_mes_grupo.parquet"
MANIF_SIH = AQ / "sih" / "manifesto_sih.json"
TISS = AQ / "tiss" / "painel_tiss_municipio_mes_tipo_cbo.parquet"
TISS_H = AQ / "tiss" / "painel_tiss_hospitalar_municipio_mes_tipo.parquet"
VAL_TISS = AQ / "tiss" / "validacao_tiss.json"
MANIF_TISS = AQ / "tiss" / "manifesto_tiss.json"
CNES = E7.PAINEL
MANIF_A09 = E7.MANIFESTO_A09
A08 = E7.A08
POP22 = E7.POP22
ARQ_VM = E7.ARQ_VM
PROTOCOLO_MD = ROOT / "docs" / "06_execucao" / "47_protocolo_producao_especializada.md"
DOC50 = ROOT / "docs" / "06_execucao" / "50_resultados_producao_especializada.md"
ARQUIVO_PROIBIDO = E7.ARQUIVO_PROIBIDO

NOME_EST = "K_D1_estimativas.csv"
NOME_EVENTO = "K_D1_estudo_evento.csv"
NOME_RESUMO = "K_D1_resumo.json"
DIR_FIG = "K_D1_figuras"

DATA_EXECUCAO = "2026-10-19"
ESTATUTO = "PROTOCOLO_47_POS_SINTESE"
NATUREZA = "EMPIRICO"
CORTES = L.CORTES_MIL                 # (300, 400)
H = L.H_PRINCIPAL_MIL                 # 50
H_SENS = (35, 75)                     # protocolo 47, §5 D1
FATORES_M = (0.5, 1.0, 2.0)
FATOR_MDE = 2.8                       # protocolo 47, §7: MDE = 2,8 x EP
EMPILHADO = E7.EMPILHADO
ROTULO_CORTE = E7.ROTULO_CORTE
ESCALA_HAB = 1e4
ADICIONAL = "ESPECIFICACAO_ADICIONAL_AO_PROTOCOLO"
LIMITE_CNES = "202609"                # nenhum mês CNES >= 202609 (ciclo 3)
LIMITE_SIA_SIH = "202607"
LIMITE_TISS = "202512"

_meses = E7._meses
MESES_SIA = _meses("202201", LIMITE_SIA_SIH)
MESES_TISS = _meses("202201", LIMITE_TISS)
MESES_CNES = tuple(c for c in E7.COMP_EVENTO if c < LIMITE_CNES)
COMP_PRE = _meses("202406", "202506")
POS_K1 = _meses("202510", "202605")           # §10.1
POS_ATE_202607 = _meses("202510", "202607")    # §10.1, sensibilidade
POS_TISS = _meses("202510", "202512")          # §2 e §4
POS_TISS_CURTO = _meses("202510", "202511")    # §11.4, sensibilidade
POS_CNES_E7 = _meses("202510", "202608")       # janela do E7 (sensibilidade de K4)
PLACEBO_A = _meses("202406", "202411")
PLACEBO_B = _meses("202412", "202505")
PRE_EXTRA = _meses("202201", "202303")
PRE_EXTRA_CNES = E7.COMP_PRE_EXTRA
COMP_REF = "202506"
DATAS_POLITICAS = E7.DATAS_POLITICAS

CONJUNTOS_SIA = ("alvo_pmme", "especialistas_nao_alvo", "generalistas", "mfc_225130")
TIPOS_SIA = ("consultas", "exames", "cirurgias", "oci")
TIPOS_K1 = TIPOS_SIA                           # §10.2: K1 principal inclui o grupo 09 (OCI)
TIPOS_K1_SEM_09 = ("consultas", "exames", "cirurgias")
TIPOS_TISS = ("consultas", "exames", "cirurgicos", "agrupados_tuss63")
STATUS_SIA_AUSENTE = "municipio_ausente_da_resposta"
STATUS_SIH_AUSENTE = "ausente_uf_mes_sem_dado"

CONTRASTE_DIRD = (
    "DiRD: anuncio de +R$ 5 mil por mes na bolsa do PMM-E (0,300: R$ 10 mil -> 15 mil; 0,400: R$ 15 mil -> 20 mil) "
    "mais a variacao, entre pre e pos, das descontinuidades das outras politicas nos mesmos cortes (auditoria 18); "
    "identifica no maximo o incentivo marginal; nao e participacao no PMM-E nem Agora Tem Especialistas")
CONTRASTE_NIVEL = "RDD em nivel: pacote do corte (bolsa anunciada + outras regras federais nos mesmos cortes)"

UNIDADES = {
    "taxa": "por 10 mil hab. por mes (Censo 2022)",
    "fracao": "fracao (x100 = p.p.)",
}


def tipo_sia(subgrupo: str) -> str | None:
    """§3.2 e §10.2: 0301 consultas; grupo 02 exames; grupo 04 cirurgias; grupo 09 OCI."""
    if subgrupo == "0301":
        return "consultas"
    return {"02": "exames", "04": "cirurgias", "09": "oci"}.get(subgrupo[:2])


# ---------------------------------------------------------------------------
# Catálogo (protocolo §4, §10, §11) — fixado antes de ler outcomes
# ---------------------------------------------------------------------------
# fonte: SIA (conj, tipos), SIH, TISS (tipos alvo), TISSH (medida), CNES (medida), K3, K5.

def _v(nome, **kw):
    return {"nome": nome, **kw}


V_POS_ATE = _v("pos_ate_202607", pos=POS_ATE_202607, motivo="§10.1: pós até 202607 (meses imaturos incluídos)")
V_SEM_09 = _v("sem_grupo_09", tipos=TIPOS_K1_SEM_09, motivo="§10.2: definição original, sem o grupo 09 (OCI)")
V_TISS_CURTO = _v("pos_202510_202511", pos=POS_TISS_CURTO, motivo="§11.4: pós só 202510-202511")
V_TISS_ATIP = _v("sem_uf_mes_atipico", mascara="tiss_amb", motivo="§11.4: sem as UF-meses sinalizadas pela A14")

CATALOGO: list[dict] = [
    {"id": "K1", "papel": "primaria", "fonte": "SIA", "conj": ("alvo_pmme",), "tipos": TIPOS_K1, "pos": POS_K1,
     "desc": "produção SUS ambulatorial executada pelas CBO-alvo (consultas 0301 + exames 02 + cirurgias 04 + OCI 09)",
     "variantes": [V_POS_ATE, V_SEM_09]},
    {"id": "K2", "papel": "primaria", "fonte": "SIH", "pos": POS_K1,
     "desc": "cirurgias SUS hospitalares: AIH aprovadas do grupo 04 (sem filtro de CBO)",
     "variantes": [_v("pos_ate_202607", pos=POS_ATE_202607,
                      motivo="§10.1: pós até 202607 (AC e RR sem dado em 202607 ficam ausentes)"),
                   _v("sem_uf_mes_atipico", mascara="sih", motivo="§10.3: sem as UF-meses atípicas da A13")]},
    {"id": "K3", "papel": "primaria", "fonte": "K3", "pos": POS_TISS,
     "desc": "consultas especializadas SUS + planos pelas CBO-alvo (SIA 0301 + TISS consultas)",
     "variantes": [V_TISS_CURTO, V_TISS_ATIP]},
    {"id": "K1a", "papel": "secundaria", "fonte": "SIA", "conj": ("alvo_pmme",), "tipos": ("consultas",),
     "pos": POS_K1, "desc": "K1, só consultas (0301)", "variantes": [V_POS_ATE]},
    {"id": "K1b", "papel": "secundaria", "fonte": "SIA", "conj": ("alvo_pmme",), "tipos": ("exames",),
     "pos": POS_K1, "desc": "K1, só exames (grupo 02)", "variantes": [V_POS_ATE]},
    {"id": "K1c", "papel": "secundaria", "fonte": "SIA", "conj": ("alvo_pmme",), "tipos": ("cirurgias",),
     "pos": POS_K1, "desc": "K1, só cirurgias ambulatoriais (grupo 04)", "variantes": [V_POS_ATE]},
    {"id": "K1d", "papel": "secundaria", "fonte": "SIA", "conj": ("alvo_pmme", "especialistas_nao_alvo"),
     "tipos": TIPOS_K1, "pos": POS_K1, "desc": "K1 com todos os especialistas (alvo + não alvo)",
     "variantes": [V_POS_ATE, V_SEM_09]},
    {"id": "K1f", "papel": "secundaria", "fonte": "SIA", "conj": ("alvo_pmme",), "tipos": ("oci",),
     "pos": POS_K1, "desc": "K1, só OCI (grupo 09, Ofertas de Cuidados Integrados)", "variantes": [V_POS_ATE]},
    {"id": "K3a.consultas", "papel": "secundaria", "fonte": "TISS", "tipos": ("consultas",), "pos": POS_TISS,
     "desc": "planos (TISS): consultas pelas CBO-alvo", "variantes": [V_TISS_CURTO, V_TISS_ATIP]},
    {"id": "K3a.exames", "papel": "secundaria", "fonte": "TISS", "tipos": ("exames",), "pos": POS_TISS,
     "desc": "planos (TISS): exames (família 4) pelas CBO-alvo; piso (CBO ausente em parte dos eventos)",
     "variantes": [_v("com_tuss63", tipos=("exames", "agrupados_tuss63"),
                      motivo="§11.1: inclui os itens agrupados da tabela TUSS 63"), V_TISS_CURTO, V_TISS_ATIP]},
    {"id": "K3a.cirurgias", "papel": "secundaria", "fonte": "TISS", "tipos": ("cirurgicos",), "pos": POS_TISS,
     "desc": "planos (TISS): procedimentos cirúrgicos (família 3) pelas CBO-alvo; piso",
     "variantes": [V_TISS_CURTO, V_TISS_ATIP]},
    {"id": "K3b", "papel": "secundaria", "fonte": "SIA", "conj": ("alvo_pmme",), "tipos": ("consultas",),
     "pos": POS_TISS, "desc": "parte SIA de K3 (consultas 0301 pelas CBO-alvo) no mesmo pós 202510-202512",
     "variantes": [V_TISS_CURTO]},
    {"id": "K3c", "papel": "secundaria", "fonte": "TISSH", "medida": "qt_itens", "pos": POS_TISS,
     "desc": "planos (TISS hospitalar): procedimentos cirúrgicos, total municipal sem filtro de CBO",
     "variantes": [_v("n_eventos", medida="n_eventos", motivo="internações com item cirúrgico, em vez de itens"),
                   V_TISS_CURTO, _v("sem_uf_mes_atipico", mascara="tiss_hosp",
                                    motivo="§11.4: sem as UF-meses sinalizadas pela A14 (hospitalar)")]},
    {"id": "K4.vinculos", "papel": "secundaria", "fonte": "CNES", "medida": "vinculos_nao_sus", "pos": POS_K1,
     "desc": "capacidade privada: vínculos não SUS das CBO-alvo (CNES; total − SUS)",
     "variantes": [_v("pos_ate_202608", pos=POS_CNES_E7, motivo="pós do E7 (202510-202608)")]},
    {"id": "K4.horas", "papel": "secundaria", "fonte": "CNES", "medida": "horas_nao_sus", "pos": POS_K1,
     "desc": "capacidade privada: horas semanais não SUS das CBO-alvo (CNES; amb. + hosp. total − SUS)",
     "variantes": [_v("pos_ate_202608", pos=POS_CNES_E7, motivo="pós do E7 (202510-202608)")]},
    {"id": "K5", "papel": "secundaria", "fonte": "K5", "pos": POS_TISS, "unidade": "fracao",
     "desc": "composição: participação do SUS nas consultas de K3 (SIA / (SIA + TISS)), razão das somas da janela",
     "variantes": [V_TISS_CURTO, V_TISS_ATIP]},
    {"id": "KP1", "papel": "placebo", "fonte": "SIA", "conj": ("generalistas",), "tipos": TIPOS_K1, "pos": POS_K1,
     "desc": "placebo: produção SIA dos generalistas (225125, 225142, 225170)", "variantes": [V_POS_ATE, V_SEM_09]},
    {"id": "KP2", "papel": "placebo", "fonte": "SIA", "conj": ("especialistas_nao_alvo",), "tipos": TIPOS_K1,
     "pos": POS_K1, "desc": "placebo: produção SIA dos especialistas fora das CBO-alvo",
     "variantes": [V_POS_ATE, V_SEM_09]},
    {"id": "KP1.mfc", "papel": "suplementar", "fonte": "SIA", "conj": ("mfc_225130",), "tipos": TIPOS_K1,
     "pos": POS_K1, "desc": "S6: produção SIA de medicina de família e comunidade (225130), à parte (§3.1)",
     "variantes": [V_POS_ATE]},
]
for _c in CATALOGO:
    _c.setdefault("unidade", "taxa")
    _c["poisson"] = _c["unidade"] == "taxa"
    _c["honesto"] = _c["papel"] == "primaria"
    _c["bky"] = _c["papel"] == "secundaria"
PRIMARIAS = [c["id"] for c in CATALOGO if c["papel"] == "primaria"]
SECUNDARIAS = [c["id"] for c in CATALOGO if c["papel"] == "secundaria"]
FIGURAS_OUTCOMES = ("K1", "K2", "K3", "K1d", "KP1", "KP2", "K4.vinculos")
POPULACOES = ("U", "V1")

ESPECIFICACOES = {
    "principal": "DiRD: RDD local linear triangular h = 0,050 sobre delta = media(pos) - media(pre), medias dos "
                 "meses com dado; HC1 por corte, CR1 por municipio no empilhado",
    "media_completa": "§5 D1 robustez: so municipios com todos os meses de pre e de pos (media do pos inteiro)",
    "sensibilidade_h": "§5 D1 robustez: h = 0,035 e 0,075",
    "ic_honesto": "§5 D1 robustez (primarias): IC Armstrong-Kolesar, M da regra de bolso (suporte ate o ponto "
                  "medio entre cortes), fatores 0,5; 1; 2; h = 0,050",
    "ic_honesto_h_otimo": f"{ADICIONAL}: h que minimiza o IC honesto (rdd_lib.ROTULO_H_OTIMO)",
    "poisson_dird": "§5 D1 robustez: Poisson local nas contagens da janela com exposicao populacional; tau = salto "
                    "em log da razao pos/pre (painel municipio x janela, CR1 por municipio)",
    "placebo_pre": "KP3 (§4): delta = media(202412-202505) - media(202406-202411)",
    "nivel_pre": f"{ADICIONAL}: RDD em nivel de media(pre) = pacote do corte",
    "nivel_pos": f"{ADICIONAL}: RDD em nivel de media(pos) = pacote do corte",
    "S5_pre_menos_pre_extra": "protocolo 40 §13 S5: delta = media(pre) - media(pre extra 202201-202303)",
    "S2_donut": "protocolo 40 §13 S2: principal sem IVS == 0,300 e == 0,400",
    "S3_porte_muda": "protocolo 40 §13 S3: principal nos portes em que o estrato IED muda no corte",
    "S3_porte_nao_muda": "protocolo 40 §13 S3: principal nos portes em que o estrato IED nao muda",
    "S3_diferenca": "protocolo 40 §13 S3: diferenca dos dois saltos",
    "S4_dentro": "protocolo 40 §13 S4 (0,400): Amazonia Legal ou faixa de fronteira",
    "S4_fora": "protocolo 40 §13 S4 (0,400): fora",
    "S4_diferenca": "protocolo 40 §13 S4: diferenca dos dois saltos",
    "sens": "§10-§11: variante do outcome ou da janela (nome depois de '|'), estimador principal",
    "estudo_evento": "§5 D1: RDD de (Y_t - Y_202506) em cada mes desde 202201 (K_D1_estudo_evento.csv)",
}
NO_PROTOCOLO = {k: not v.startswith(ADICIONAL) for k, v in ESPECIFICACOES.items()}

DESVIOS = [
    {"data": DATA_EXECUCAO, "tipo": "esclarecimento", "item": "K1e",
     "descricao": "o protocolo 47 (§4, §10, §11) define K1a, K1b, K1c, K1d e K1f; nao existe K1e. Nada foi estimado "
                  "com esse nome."},
    {"data": DATA_EXECUCAO, "tipo": "esclarecimento", "item": "K3b",
     "descricao": "'K3 com SIA no mesmo pos 202510-202512, para separar janela de fonte' foi lido como a parte SIA "
                  "de K3 (consultas 0301 das CBO-alvo) com pre 202406-202506 e pos 202510-202512: K3 = K3b + "
                  "K3a.consultas, e K3b contra K1a separa a janela; K3 contra K3b separa a fonte."},
    {"data": DATA_EXECUCAO, "tipo": "esclarecimento", "item": "janela de K4",
     "descricao": "o protocolo nao da o pos de K4 (CNES). Fixado antes de estimar: o mesmo pos de K1 (202510-202605), "
                  "para que a leitura de substituicao SUS x privado (§5) compare a mesma janela; o pos do E7 "
                  "(202510-202608) e sensibilidade. Nenhum mes CNES >= 202609 e lido."},
    {"data": DATA_EXECUCAO, "tipo": "esclarecimento", "item": "medida de K3c e K4.horas",
     "descricao": "K3c usa a quantidade informada (qt_itens, §3.2) dos itens cirurgicos do TISS hospitalar; o numero "
                  "de internacoes com item cirurgico (n_eventos) e variante. K4.horas = horas_totais_amb_hosp - "
                  "horas_sus_semanais (ambulatorial + hospitalar, total menos SUS, regra do §16 do protocolo 40); hora "
                  "em branco fica ausente."},
    {"data": DATA_EXECUCAO, "tipo": "esclarecimento", "item": "K5",
     "descricao": "participacao do SUS = soma(SIA) / soma(SIA + TISS) das consultas das CBO-alvo nos meses da janela "
                  "com os dois dados; municipio sem nenhuma consulta na janela tem a razao indefinida e sai (contado). "
                  "Sem Poisson (nao e contagem)."},
    {"data": DATA_EXECUCAO, "tipo": "esclarecimento", "item": "principal com meses de dado",
     "descricao": "a robustez 'media do pos em vez da media de meses com dado' (§5 D1) fixa o principal como a media "
                  "dos meses com dado e a robustez (media_completa) como so os municipios com todos os meses. Ausencia "
                  "nunca vira zero."},
    {"data": DATA_EXECUCAO, "tipo": "esclarecimento", "item": "testes multiplos",
     "descricao": "Holm entre K1, K2 e K3 (linha principal, U, cortes empilhados); BKY nas secundarias (mesma linha, "
                  "uma por outcome). Placebos e KP1.mfc ficam fora dos dois."},
    {"data": DATA_EXECUCAO, "tipo": "esclarecimento", "item": "S1 a S6",
     "descricao": "S2, S3 e S4 por outcome como no E7; S5 = linhas S5_pre_menos_pre_extra e o pre extra do estudo de "
                  "evento; S6 = KP1.mfc; S1 (RDD no PMMB) nao depende do outcome e esta no E6. Local randomization "
                  "nao esta no protocolo 47 e nao foi estimada."},
    {"data": DATA_EXECUCAO, "tipo": "esclarecimento", "item": "efeito relativo",
     "descricao": "efeito relativo = salto / media simples de Y_pre dos municipios abaixo do corte na janela "
                  "(-h < x <= 0) com delta definido; no empilhado, as linhas dos dois cortes juntas. MDE = 2,8 x EP."},
    {"data": DATA_EXECUCAO, "tipo": "esclarecimento", "item": "variantes por fonte",
     "descricao": "'ate 202607' vale para todo outcome SIA/SIH; 'sem grupo 09' para todo outcome SIA que inclui OCI; "
                  "'sem UF-mes atipico' e 'pos 202510-202511' para os outcomes TISS; 'com TUSS 63' so para exames."},
]


class FalhaValidacao(RuntimeError):
    """Validação obrigatória falhou: o script para sem gravar estimativas."""


sha256 = E7.sha256
rotulo = E7.rotulo
_nan_none = E7._nan_none
_juntar = E7._juntar
_ibge6 = E7._ibge6


def _gravar_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(_nan_none(obj), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# 1. Universo, população e V1
# ---------------------------------------------------------------------------

def ler_universo() -> tuple[pd.DataFrame, dict]:
    """U = municípios do a08 com população 2022 > 0; V1 = quadro do ciclo 1 (IVS conferido)."""
    rv = E7.ler_running_variable()
    pop = E7.ler_populacao()
    pops, conf = E7.populacoes(rv, pop)
    base = pops["U"].copy()
    sem_pop = base.loc[~(base["populacao_2022"] > 0), "co_ibge"].tolist()
    base = base[base["populacao_2022"] > 0]
    base["V1"] = base["co_ibge"].isin(set(pops["V1"]["co_ibge"]))
    so_pop = sorted(set(pop["co_ibge"]) - set(rv["co_ibge"]))
    conf.update({"U_com_populacao": int(len(base)), "U_excluidos_sem_populacao": sem_pop,
                 "censo2022_sem_ivs_oficial_fora": so_pop})
    return base.set_index("co_ibge").sort_index(), conf


# ---------------------------------------------------------------------------
# 2. Leitura das fontes (filtros cedo, com pyarrow) e validação
# ---------------------------------------------------------------------------

def conferir_sha(caminho: Path, esperado: str | None, nome: str) -> str:
    atual = sha256(caminho)
    if esperado != atual:
        raise FalhaValidacao(f"{nome}: SHA-256 {atual[:12]} difere do manifesto ({str(esperado)[:12]})")
    return atual


def _fora_do_universo(codigos: set[str], universo: pd.Index) -> list[str]:
    return sorted(set(codigos) - set(universo))


def ler_sia(universo: pd.Index) -> tuple[dict, dict]:
    """{(conjunto, tipo): DataFrame largo município x mês} com a quantidade aprovada; ausente fica NaN."""
    import pyarrow.parquet as pq
    man = json.loads(MANIF_SIA.read_text(encoding="utf-8"))
    conferir_sha(SIA, man["saidas"][rotulo(SIA)]["sha256"], "painel SIA")
    sub = pd.read_csv(SIA_SUBG, dtype={"competencia_processamento": str, "subgrupo": str})
    sub["tipo"] = sub["subgrupo"].map(tipo_sia)
    sub = sub[sub["tipo"].notna() & sub["conjunto_cbo"].isin(CONJUNTOS_SIA)]
    comps = set(sub["competencia_processamento"])
    if max(comps) > LIMITE_SIA_SIH or set(MESES_SIA) - comps:
        raise FalhaValidacao("SIA: meses fora do limite ou ausentes do plano de consultas")
    subgrupos = sorted(sub["subgrupo"].unique())
    tab = pq.read_table(SIA, columns=["co_ibge", "competencia_processamento", "subgrupo", "conjunto_cbo",
                                      "qtd_aprovada", "status", "natureza_dos_dados"],
                        filters=[("conjunto_cbo", "in", list(CONJUNTOS_SIA)), ("subgrupo", "in", subgrupos)])
    df = tab.to_pandas()
    del tab
    if set(df["natureza_dos_dados"].astype(str).unique()) != {NATUREZA}:
        raise FalhaValidacao("SIA com natureza_dos_dados diferente de EMPIRICO")
    df = df.drop(columns="natureza_dos_dados")
    for c in ("competencia_processamento", "subgrupo", "conjunto_cbo", "co_ibge", "status"):
        if not isinstance(df[c].dtype, pd.CategoricalDtype):
            df[c] = df[c].astype("category")
    if str(df["competencia_processamento"].cat.categories.max()) > LIMITE_SIA_SIH:
        raise FalhaValidacao("SIA com mes > 202607")
    mapa_tipo = {s: tipo_sia(s) for s in df["subgrupo"].cat.categories}
    df["tipo"] = df["subgrupo"].map(mapa_tipo).astype("category")
    df["ausente"] = (df["status"] == STATUS_SIA_AUSENTE).astype(np.int8)
    if (df["qtd_aprovada"].isna() != (df["ausente"] == 1)).any():
        raise FalhaValidacao("SIA: qtd_aprovada nula sem status de ausencia (ou o contrario)")
    df["qtd"] = df["qtd_aprovada"].astype("float64")
    g = df.groupby(["conjunto_cbo", "tipo", "competencia_processamento", "co_ibge"], observed=True)
    agg = g.agg(q=("qtd", "sum"), n=("qtd", "size"), aus=("ausente", "sum")).reset_index()
    del df, g
    for c in ("conjunto_cbo", "tipo", "competencia_processamento", "co_ibge"):
        agg[c] = agg[c].astype(str)
    # Número de subgrupos de cada tipo presentes como coluna em cada consulta (mês x conjunto).
    pres = (sub[sub["presente_na_resposta"].astype(str).str.lower() == "true"]
            .groupby(["conjunto_cbo", "tipo", "competencia_processamento"]).size().rename("n_presentes").reset_index())
    agg = agg.merge(pres, on=["conjunto_cbo", "tipo", "competencia_processamento"], how="left", validate="many_to_one")
    if agg["n_presentes"].isna().any() or (agg["n"] != agg["n_presentes"]).any():
        raise FalhaValidacao("SIA: municipio com numero de linhas diferente dos subgrupos presentes na consulta "
                             "(exibirlz do a12 violado)")
    munis_tab = pd.read_csv(SIA_MUN, dtype={"co_ibge": str})["co_ibge"].map(lambda v: str(v).zfill(6))
    agg.loc[agg["aus"] > 0, "q"] = np.nan
    pres_idx = pres.set_index(["conjunto_cbo", "tipo", "competencia_processamento"])["n_presentes"]
    saida = {}
    for conj in CONJUNTOS_SIA:
        for tipo in TIPOS_SIA:
            a = agg[(agg["conjunto_cbo"] == conj) & (agg["tipo"] == tipo)]
            larga = a.pivot(index="co_ibge", columns="competencia_processamento", values="q")
            larga = larga.reindex(index=munis_tab, columns=list(MESES_SIA))
            for mes in MESES_SIA:
                n_p = pres_idx.get((conj, tipo, mes), 0)
                if n_p == 0:
                    # nenhum subgrupo do tipo veio como coluna: zero daquela consulta (V4 do a12)
                    larga[mes] = 0.0
                elif larga[mes].isna().any():
                    sem = larga.index[larga[mes].isna()]
                    aus = set(a[(a["competencia_processamento"] == mes) & (a["aus"] > 0)]["co_ibge"])
                    if not set(sem) <= aus:
                        raise FalhaValidacao(f"SIA {conj} {tipo} {mes}: municipio sem linha na consulta")
            saida[(conj, tipo)] = larga.reindex(universo)
    info = {"municipios_tabnet": int(len(munis_tab)),
            "municipios_tabnet_fora_de_U": _fora_do_universo(set(munis_tab), universo),
            "municipios_de_U_fora_do_tabnet": _fora_do_universo(set(universo), pd.Index(munis_tab)),
            "celulas_ausentes_municipio_mes_conjunto_tipo": int(sum(int(v.isna().sum().sum()) for v in saida.values())),
            "subgrupos_lidos": subgrupos, "meses": [MESES_SIA[0], MESES_SIA[-1]],
            "regra_subgrupo_ausente": "subgrupo que nao veio como coluna da consulta = zero daquela consulta (V4 do a12)"}
    return saida, info


def ler_sih(universo: pd.Index) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    import pyarrow.parquet as pq
    man = json.loads(MANIF_SIH.read_text(encoding="utf-8"))
    conferir_sha(SIH, man["saidas"]["painel"]["sha256"], "painel SIH")
    df = pq.read_table(SIH, columns=["co_ibge", "uf", "competencia", "grupo", "aih_aprovadas", "status",
                                     "uf_mes_atipico", "natureza_dos_dados"],
                       filters=[("grupo", "=", "04")]).to_pandas()
    if set(df["natureza_dos_dados"].astype(str)) != {NATUREZA}:
        raise FalhaValidacao("SIH com natureza diferente de EMPIRICO")
    if df["competencia"].max() > LIMITE_SIA_SIH or set(MESES_SIA) - set(df["competencia"]):
        raise FalhaValidacao("SIH: meses fora do limite ou ausentes")
    if df.duplicated(["co_ibge", "competencia"]).any():
        raise FalhaValidacao("SIH com chave repetida")
    aus = df["status"] == STATUS_SIH_AUSENTE
    if (df["aih_aprovadas"].isna() != aus).any():
        raise FalhaValidacao("SIH: aih_aprovadas nula sem status de ausencia (ou o contrario)")
    df["q"] = pd.to_numeric(df["aih_aprovadas"], errors="coerce").astype(float)
    larga = df.pivot(index="co_ibge", columns="competencia", values="q").reindex(columns=list(MESES_SIA))
    atip = df.pivot(index="co_ibge", columns="competencia", values="uf_mes_atipico").reindex(columns=list(MESES_SIA))
    info = {"municipios_painel": int(larga.shape[0]),
            "municipios_painel_fora_de_U": _fora_do_universo(set(larga.index), universo),
            "municipios_de_U_fora_do_painel": _fora_do_universo(set(universo), larga.index),
            "uf_meses_sem_dado": sorted({f"{u}|{c}" for u, c in df.loc[aus, ["uf", "competencia"]].itertuples(index=False)}),
            "uf_meses_atipicos": sorted({f"{u}|{c}" for u, c in df.loc[df["uf_mes_atipico"], ["uf", "competencia"]]
                                        .itertuples(index=False)}),
            "celulas_ausentes": int(aus.sum())}
    return larga.reindex(universo), atip.reindex(universo).fillna(False).astype(bool), info


def _alertas_tiss(base: str) -> set[tuple[str, str]]:
    v = json.loads(VAL_TISS.read_text(encoding="utf-8"))
    return {(a["uf"], a["competencia_realizacao"]) for a in v.get("alertas_queda", []) if a["base"] == base}


def ler_tiss(universo: pd.Index) -> tuple[dict, dict, dict]:
    """TISS ambulatorial, CBO-alvo: {tipo: largo de qt_itens} e máscara das UF-meses sinalizadas (AMB)."""
    import pyarrow.parquet as pq
    man = json.loads(MANIF_TISS.read_text(encoding="utf-8"))
    conferir_sha(TISS, man["saidas"]["AMB"]["sha256"], "painel TISS ambulatorial")
    df = pq.read_table(TISS, columns=["co_ibge", "uf", "competencia_realizacao", "tipo_procedimento", "grupo_cbo",
                                      "qt_itens", "status_cobertura", "natureza_dos_dados"],
                       filters=[("grupo_cbo", "=", "alvo_pmme"),
                                ("tipo_procedimento", "in", list(TIPOS_TISS))]).to_pandas()
    return _tiss_largo(df, universo, "AMB", "qt_itens", TIPOS_TISS)


def ler_tiss_hosp(universo: pd.Index) -> tuple[dict, dict, dict]:
    import pyarrow.parquet as pq
    man = json.loads(MANIF_TISS.read_text(encoding="utf-8"))
    conferir_sha(TISS_H, man["saidas"]["HOSP"]["sha256"], "painel TISS hospitalar")
    df = pq.read_table(TISS_H, columns=["co_ibge", "uf", "competencia_realizacao", "tipo_procedimento", "grupo_cbo",
                                        "qt_itens", "n_eventos", "status_cobertura", "natureza_dos_dados"],
                       filters=[("grupo_cbo", "=", "todos_cbo"), ("tipo_procedimento", "=", "cirurgicos")]).to_pandas()
    out_q, atip, info = _tiss_largo(df, universo, "HOSP", "qt_itens", ("cirurgicos",))
    out_e, _, _ = _tiss_largo(df, universo, "HOSP", "n_eventos", ("cirurgicos",))
    return {"qt_itens": out_q["cirurgicos"], "n_eventos": out_e["cirurgicos"]}, atip, info


def _tiss_largo(df: pd.DataFrame, universo: pd.Index, base: str, medida: str, tipos) -> tuple[dict, pd.DataFrame, dict]:
    if set(df["natureza_dos_dados"].astype(str)) != {NATUREZA}:
        raise FalhaValidacao("TISS com natureza diferente de EMPIRICO")
    if df["competencia_realizacao"].max() > LIMITE_TISS or set(MESES_TISS) - set(df["competencia_realizacao"]):
        raise FalhaValidacao("TISS: meses fora do limite ou ausentes")
    if df.duplicated(["co_ibge", "competencia_realizacao", "tipo_procedimento"]).any():
        raise FalhaValidacao("TISS com chave repetida")
    aus = df["status_cobertura"].astype(str).str.startswith("ausente")
    v = df[medida].astype(float)
    df = df.assign(q=np.where(aus, np.nan, v))
    if (df.loc[~aus, "q"].isna()).any():
        raise FalhaValidacao(f"TISS: {medida} nulo em pacote aprovado")
    out = {}
    for t in tipos:
        sub = df[df["tipo_procedimento"] == t]
        out[t] = sub.pivot(index="co_ibge", columns="competencia_realizacao", values="q").reindex(
            columns=list(MESES_TISS)).reindex(universo)
    uf = df.drop_duplicates("co_ibge").set_index("co_ibge")["uf"].reindex(universo)
    alertas = _alertas_tiss(base)
    atip = pd.DataFrame({m: uf.map(lambda u, m=m: (u, m) in alertas).astype(bool) for m in MESES_TISS})
    info = {"municipios_painel": int(df["co_ibge"].nunique()),
            "municipios_painel_fora_de_U": _fora_do_universo(set(df["co_ibge"]), universo),
            "municipios_de_U_fora_do_painel": _fora_do_universo(set(universo), pd.Index(df["co_ibge"].unique())),
            "celulas_ausentes": int(aus.sum()),
            "uf_meses_sinalizados_alertas_queda": sorted(f"{u}|{m}" for u, m in alertas)}
    return out, atip, info


def ler_cnes(universo: pd.Index) -> tuple[dict, dict]:
    import pyarrow.parquet as pq
    man = json.loads(MANIF_A09.read_text(encoding="utf-8"))
    conferir_sha(CNES, man["painel"]["sha256"], "painel CNES a09")
    df = pq.read_table(CNES, columns=["co_ibge", "competencia", "grupo", "n_vinculos", "n_vinculos_sus",
                                      "horas_sus_semanais", "horas_totais_amb_hosp", "natureza_dos_dados"],
                       filters=[("grupo", "=", "alvo_pmme"), ("competencia", "<", LIMITE_CNES)]).to_pandas()
    if df["competencia"].max() >= LIMITE_CNES:
        raise FalhaValidacao("CNES com competencia >= 202609")
    if set(MESES_CNES) - set(df["competencia"]):
        raise FalhaValidacao("CNES: competencias do E7 ausentes")
    df = df[df["competencia"].isin(MESES_CNES)]
    if df.duplicated(["co_ibge", "competencia"]).any():
        raise FalhaValidacao("CNES com chave repetida")
    v = df["n_vinculos"].astype(float) - df["n_vinculos_sus"].astype(float)
    h = pd.to_numeric(df["horas_totais_amb_hosp"], errors="coerce").astype(float) - \
        pd.to_numeric(df["horas_sus_semanais"], errors="coerce").astype(float)
    if (v < 0).any() or (h.dropna() < 0).any():
        raise FalhaValidacao("CNES: total menor que SUS")
    df = df.assign(vinculos_nao_sus=v, horas_nao_sus=h)
    out = {m: df.pivot(index="co_ibge", columns="competencia", values=m).reindex(columns=list(MESES_CNES))
           .reindex(universo) for m in ("vinculos_nao_sus", "horas_nao_sus")}
    info = {"municipios_painel_fora_de_U": _fora_do_universo(set(df["co_ibge"]), universo),
            "celulas_horas_ausentes": int(h.isna().sum()), "competencias": list(MESES_CNES)}
    return out, info


class Dados:
    """Matrizes largas (município de U x mês) das contagens, por fonte."""

    def __init__(self, base: pd.DataFrame, sia, sih, sih_atip, tiss, tiss_atip, tissh, tissh_atip, cnes, info):
        self.base = base
        self.pop = base["populacao_2022"].astype(float)
        self.sia, self.sih, self.sih_atip = sia, sih, sih_atip
        self.tiss, self.tiss_atip, self.tissh, self.tissh_atip = tiss, tiss_atip, tissh, tissh_atip
        self.cnes = cnes
        self.info = info

    def sia_soma(self, conjs, tipos) -> pd.DataFrame:
        partes = [self.sia[(c, t)] for c in conjs for t in tipos]
        tot = partes[0].copy()
        for p in partes[1:]:
            tot = tot + p          # NaN propaga: componente ausente deixa o total ausente
        return tot

    def tiss_soma(self, tipos) -> pd.DataFrame:
        tot = self.tiss[tipos[0]].copy()
        for t in tipos[1:]:
            tot = tot + self.tiss[t]
        return tot


def contagens(D: Dados, spec: dict, var: dict | None = None) -> tuple[pd.DataFrame, pd.DataFrame | None, tuple]:
    """(numerador, denominador ou None, meses do estudo de evento) do outcome, com a variante aplicada."""
    var = var or {}
    tipos = var.get("tipos", spec.get("tipos"))
    fonte = spec["fonte"]
    den = None
    if fonte == "SIA":
        num, meses = D.sia_soma(spec["conj"], tipos), MESES_SIA
    elif fonte == "SIH":
        num, meses = D.sih.copy(), MESES_SIA
    elif fonte == "TISS":
        num, meses = D.tiss_soma(tipos), MESES_TISS
    elif fonte == "TISSH":
        num, meses = D.tissh[var.get("medida", spec["medida"])].copy(), MESES_TISS
    elif fonte == "CNES":
        num, meses = D.cnes[spec["medida"]].copy(), MESES_CNES
    elif fonte in ("K3", "K5"):
        sia = D.sia[("alvo_pmme", "consultas")].reindex(columns=list(MESES_TISS))
        tis = D.tiss["consultas"].copy()
        if var.get("mascara") == "tiss_amb":
            tis = tis.mask(D.tiss_atip.to_numpy())
        tot = sia + tis
        meses = MESES_TISS
        if fonte == "K3":
            num = tot
        else:
            num, den = sia.where(tot.notna()), tot
        return num, den, meses
    else:
        raise ValueError(fonte)
    masc = var.get("mascara")
    if masc == "sih":
        num = num.mask(D.sih_atip.to_numpy())
    elif masc == "tiss_amb":
        num = num.mask(D.tiss_atip.to_numpy())
    elif masc == "tiss_hosp":
        num = num.mask(D.tissh_atip.to_numpy())
    return num, den, meses


# ---------------------------------------------------------------------------
# 3. Janelas por município
# ---------------------------------------------------------------------------

def _media_janela(R: pd.DataFrame, meses, completo: bool) -> pd.Series:
    sub = R.reindex(columns=list(meses))
    m = sub.mean(axis=1, skipna=True)
    if completo:
        m = m.where(sub.notna().all(axis=1))
    return m


def janela_valores(num: pd.DataFrame, den: pd.DataFrame | None, pop: pd.Series, meses, *, completo: bool = False
                   ) -> tuple[pd.Series, pd.Series, pd.Series]:
    """(y, contagem somada, exposição) da janela. Taxa: média dos meses com dado (ou só completos); razão: somas."""
    sub = num.reindex(columns=list(meses))
    if den is None:
        R = sub.div(pop, axis=0) * ESCALA_HAB
        y = _media_janela(R, meses, completo)
        n = sub.notna().sum(axis=1)
        cont = sub.sum(axis=1, min_count=1)
        if completo:
            cont = cont.where(sub.notna().all(axis=1))
        expo = pop * n
        return y, cont.where(n > 0), expo.where(n > 0)
    d = den.reindex(columns=list(meses))
    ok = sub.notna() & d.notna()
    sn = sub.where(ok).sum(axis=1, min_count=1)
    sd = d.where(ok).sum(axis=1, min_count=1)
    y = (sn / sd).where(sd > 0)
    if completo:
        y = y.where(ok.all(axis=1))
    return y, sn, sd


def base_janelas(num, den, pop: pd.Series, s_mil: pd.Series, pos, *, completo: bool = False,
                 pre_extra=PRE_EXTRA) -> pd.DataFrame:
    y_pre, c_pre, e_pre = janela_valores(num, den, pop, COMP_PRE, completo=completo)
    y_pos, c_pos, e_pos = janela_valores(num, den, pop, pos, completo=completo)
    y_pa, _, _ = janela_valores(num, den, pop, PLACEBO_A, completo=completo)
    y_pb, _, _ = janela_valores(num, den, pop, PLACEBO_B, completo=completo)
    y_px, _, _ = janela_valores(num, den, pop, pre_extra, completo=completo)
    d = pd.DataFrame({"co_ibge": num.index, "s_mil": s_mil.reindex(num.index).to_numpy(dtype=float),
                      "y_pre": y_pre.to_numpy(), "y_pos": y_pos.to_numpy(), "y_placebo_a": y_pa.to_numpy(),
                      "y_placebo_b": y_pb.to_numpy(), "y_pre_extra": y_px.to_numpy(),
                      "c_pre": c_pre.to_numpy(), "c_pos": c_pos.to_numpy(), "e_pre": e_pre.to_numpy(),
                      "e_pos": e_pos.to_numpy()})
    d["delta_principal"] = d["y_pos"] - d["y_pre"]
    return d.reset_index(drop=True)


# ---------------------------------------------------------------------------
# 4. Poisson DiRD (painel município x janela, IRLS, CR1 por município)
# ---------------------------------------------------------------------------

def poisson_irls(X: np.ndarray, y: np.ndarray, w: np.ndarray, off: np.ndarray, cluster: np.ndarray, i_tau: int,
                 *, max_iter: int = 200, tol: float = 1e-10) -> dict:
    """Pseudo-verossimilhança de Poisson ponderada (mesma rotina da rdd_lib.rd_poisson_local, com X genérico)."""
    k = X.shape[1]
    out = {"tau": np.nan, "ep": np.nan, "convergiu": False, "nota": ""}
    escala = max(1.0, float(np.sum(w * y)))

    def pll(b):
        with np.errstate(over="ignore", invalid="ignore"):
            eta = off + X @ b
            return float(np.sum(w * (y * eta - np.exp(eta))))

    beta = np.zeros(k)
    beta[0] = math.log(np.sum(w * y) / np.sum(w * np.exp(off)))
    ll = pll(beta)
    for _ in range(max_iter):
        mu = np.exp(off + X @ beta)
        grad = X.T @ (w * (y - mu))
        Hm = X.T @ (X * (w * mu)[:, None])
        try:
            passo = np.linalg.solve(Hm, grad)
        except np.linalg.LinAlgError:
            out["nota"] = "hessiana singular no IRLS"
            return out
        f = 1.0
        while f >= 1e-8:
            novo = beta + f * passo
            ll_n = pll(novo)
            if math.isfinite(ll_n) and ll_n >= ll - 1e-12 * abs(ll):
                break
            f /= 2.0
        else:
            out["nota"] = "busca em linha parou sem melhorar a pseudo-verossimilhanca"
            return out
        beta, ll = novo, ll_n
        mu = np.exp(off + X @ beta)
        grad = X.T @ (w * (y - mu))
        if np.max(np.abs(f * passo)) < tol and np.max(np.abs(grad)) / escala < 1e-8:
            out["convergiu"] = True
            break
    if not out["convergiu"]:
        out["nota"] = "IRLS nao convergiu"
        return out
    mu = np.exp(off + X @ beta)
    try:
        bread = np.linalg.inv(X.T @ (X * (w * mu)[:, None]))
    except np.linalg.LinAlgError:
        out["nota"] = "hessiana singular na solucao"
        return out
    score = X * (w * (y - mu))[:, None]
    _, idx = np.unique(cluster, return_inverse=True)
    G = int(idx.max()) + 1
    S = np.zeros((G, k))
    np.add.at(S, idx, score)
    m_obs = len(y)
    V = bread @ (S.T @ S) @ bread * (G / (G - 1)) * ((m_obs - 1) / (m_obs - k))
    out.update({"tau": float(beta[i_tau]), "ep": float(math.sqrt(max(V[i_tau, i_tau], 0.0))), "n_clusters": G,
                "beta": beta})
    return out


def poisson_dird(d: pd.DataFrame, corte, h_mil: float = H) -> dict:
    """log E[C] = log(exposição) + [por grupo: 1, x, T, Tx] + P [por grupo: 1, x, Tx] + tau T P.

    Duas linhas por município (pré, pós), contagem somada na janela e exposição = população x meses com dado;
    grupo = corte (no empilhado, cada município entra uma vez por corte). tau = salto em log da razão pós/pré.
    """
    cortes = list(CORTES) if corte == EMPILHADO else [corte]
    partes = []
    for c in cortes:
        for per, cc, ee in ((0.0, "c_pre", "e_pre"), (1.0, "c_pos", "e_pos")):
            partes.append(pd.DataFrame({"u": d["co_ibge"].to_numpy(), "s": d["s_mil"].to_numpy(dtype=float),
                                        "c": float(c), "P": per, "y": d[cc].to_numpy(dtype=float),
                                        "e": d[ee].to_numpy(dtype=float)}))
    p = pd.concat(partes, ignore_index=True)
    p["s"] = L.normalizar_s_mil(p["s"].to_numpy())
    xm = p["s"].to_numpy() - p["c"].to_numpy()
    w = L.pesos_kernel(xm, h_mil)
    # Município só entra se tem pré e pós válidos (contagem e exposição > 0): painel balanceado na janela.
    ok_lin = np.isfinite(p["y"].to_numpy()) & (p["e"].to_numpy() > 0)
    ok_u = pd.Series(ok_lin).groupby([p["u"].to_numpy(), p["c"].to_numpy()]).transform("all").to_numpy()
    usa = (w > 0) & ok_u
    res = {"tau": np.nan, "ep": np.nan, "ic95_inf": np.nan, "ic95_sup": np.nan, "p_valor": np.nan,
           "n_abaixo": None, "n_acima": None, "n_obs": int(usa.sum()), "n_clusters": None, "nota": "",
           "estimador": "Poisson DiRD: pseudo-verossimilhanca ponderada (kernel triangular), exposicao = populacao x "
                        "meses com dado, CR1 por municipio"}
    q = p[usa].copy()
    q["w"] = w[usa]
    q["x"] = (q["s"] - q["c"]) / 1000.0
    q["T"] = (q["s"] > q["c"]).astype(float)
    res["n_abaixo"] = int(q.loc[q["T"] == 0, "u"].nunique())
    res["n_acima"] = int(q.loc[q["T"] == 1, "u"].nunique())
    for c in cortes:
        for per in (0.0, 1.0):
            for t in (0.0, 1.0):
                m = (q["c"] == c) & (q["P"] == per) & (q["T"] == t)
                if np.unique(q.loc[m & (q["y"] > 0), "s"]).size < 2:
                    res["nota"] = (f"suporte insuficiente ou separacao no corte {c:g}, periodo {int(per)}, lado "
                                   f"{int(t)}: eventos em menos de 2 mass points")
                    return res
    cols, nomes = [], []
    for c in cortes:
        g = (q["c"] == c).astype(float).to_numpy()
        x, T, P = q["x"].to_numpy(), q["T"].to_numpy(), q["P"].to_numpy()
        for nome, v in (("const", g), ("x", g * x), ("T", g * T), ("Tx", g * T * x), ("P", g * P),
                        ("Px", g * P * x), ("PTx", g * P * T * x)):
            cols.append(v)
            nomes.append(f"{nome}[{c:g}]")
    cols.append(q["T"].to_numpy() * q["P"].to_numpy())
    nomes.append("TP")
    X = np.column_stack(cols)
    r = poisson_irls(X, q["y"].to_numpy(dtype=float), q["w"].to_numpy(dtype=float),
                     np.log(q["e"].to_numpy(dtype=float)), q["u"].to_numpy(), len(nomes) - 1)
    if not np.isfinite(r["tau"]):
        res["nota"] = r["nota"]
        return res
    res.update({"tau": r["tau"], "ep": r["ep"], "n_clusters": r["n_clusters"],
                "ic95_inf": r["tau"] - L.Z_975 * r["ep"], "ic95_sup": r["tau"] + L.Z_975 * r["ep"],
                "p_valor": L.p_normal(r["tau"] / r["ep"]) if r["ep"] > 0 else np.nan})
    return res


# ---------------------------------------------------------------------------
# 5. Linhas de estimativas
# ---------------------------------------------------------------------------

COLUNAS_SAIDA = [
    "natureza_dos_dados", "estatuto", "familia", "desenho", "outcome_id", "descricao_outcome", "papel", "fonte",
    "populacao", "corte", "especificacao", "variante", "estimador", "no_protocolo", "rotulo", "status", "contraste",
    "janela_pre", "janela_pos", "h", "n_abaixo", "n_acima", "n_obs", "n_clusters", "tau", "ep", "ic95_inf",
    "ic95_sup", "p_valor", "ic_honesto_inf", "ic_honesto_sup", "M", "fator_M", "vies_max", "media_pre_abaixo",
    "efeito_relativo", "efeito_relativo_ic95_inf", "efeito_relativo_ic95_sup", "mde", "mde_relativo",
    "entra_holm", "p_holm", "entra_bky", "q_bky", "unidade", "nota",
]

COLUNAS_EVENTO = ["natureza_dos_dados", "estatuto", "familia", "outcome_id", "populacao", "corte", "competencia",
                  "data", "janela", "referencia", "h", "n_abaixo", "n_acima", "tau", "ep", "ic95_inf", "ic95_sup",
                  "p_valor", "unidade", "nota"]


def _rot(meses) -> str:
    return f"{meses[0]}-{meses[-1]}"


def nova_linha(meta: dict, esp: str, estimador: str, *, h_mil=H, variante: str = "", rotulo_esp: str = "",
               contraste: str = CONTRASTE_DIRD, janelas=None) -> dict:
    linha = {c: np.nan for c in COLUNAS_SAIDA}
    base_esp = esp.split("|")[0]
    linha.update({"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "familia": "K", "desenho": "D1", **meta,
                  "especificacao": esp, "variante": variante, "estimador": estimador,
                  "no_protocolo": bool(NO_PROTOCOLO.get(base_esp, False)),
                  "rotulo": rotulo_esp or ("" if NO_PROTOCOLO.get(base_esp, True) else ADICIONAL),
                  "status": "EXECUTADO", "contraste": contraste,
                  "h": (h_mil / 1000.0) if h_mil is not None and np.isfinite(h_mil) else np.nan,
                  "entra_holm": False, "entra_bky": False, "nota": ""})
    if janelas:
        linha["janela_pre"], linha["janela_pos"] = _rot(janelas[0]), _rot(janelas[1])
    return linha


def preencher(linha: dict, res: dict | None) -> dict:
    if res is None:
        linha["status"] = "SEM_ESTIMATIVA"
        return linha
    for k in ("tau", "ep", "ic95_inf", "ic95_sup", "p_valor", "n_abaixo", "n_acima", "n_obs", "n_clusters"):
        if k in res and res[k] is not None:
            linha[k] = res[k]
    linha["nota"] = _juntar(linha.get("nota", ""), res.get("nota", ""))
    if not np.isfinite(float(linha["tau"])):
        linha["status"] = "SEM_ESTIMATIVA"
        if not linha["nota"]:
            linha["nota"] = "biblioteca devolveu NaN sem motivo"
    return linha


def media_abaixo(d: pd.DataFrame, corte, h_mil=H) -> float:
    """Média simples de y_pre dos municípios abaixo do corte na janela (-h < x <= 0) com delta definido."""
    s = L.normalizar_s_mil(d["s_mil"].to_numpy(dtype=float))
    ok = np.isfinite(d["delta_principal"].to_numpy(dtype=float)) & np.isfinite(d["y_pre"].to_numpy(dtype=float))
    vals = []
    for c in (CORTES if corte == EMPILHADO else [corte]):
        x = s - c
        vals.append(d["y_pre"].to_numpy(dtype=float)[ok & (x > -h_mil) & (x <= 0)])
    v = np.concatenate(vals)
    return float(v.mean()) if v.size else float("nan")


def linhas_honesto(meta: dict, d: pd.DataFrame, corte, janelas, principal: dict) -> list[dict]:
    linhas = []
    y = d["delta_principal"].to_numpy(dtype=float)
    s = d["s_mil"].to_numpy(dtype=float)

    def linha_de(rec, fator, otimo, estimador):
        esp = "ic_honesto_h_otimo" if otimo else "ic_honesto"
        ln = nova_linha(meta, esp, estimador, h_mil=rec.get("h_mil", H), rotulo_esp=L.ROTULO_H_OTIMO if otimo else "",
                        janelas=janelas)
        for k in ("tau", "ep", "ic95_inf", "ic95_sup", "p_valor", "n_abaixo", "n_acima", "M", "vies_max"):
            if rec.get(k) is not None:
                ln[k] = rec[k]
        ln["ic_honesto_inf"], ln["ic_honesto_sup"], ln["fator_M"] = ln["ic95_inf"], ln["ic95_sup"], fator
        ln["nota"] = _juntar("ep = EP usado no IC honesto", f"M = {fator:g} x regra de bolso", rec.get("nota", ""))
        if not np.isfinite(float(ln["ic95_inf"])):
            ln["status"] = "SEM_ESTIMATIVA"
        if fator == 1.0 and not otimo:
            principal["ic_honesto_inf"], principal["ic_honesto_sup"] = ln["ic95_inf"], ln["ic95_sup"]
            principal["M"], principal["fator_M"] = ln["M"], 1.0
        return ln

    try:
        if corte == EMPILHADO:
            e = E7.empilhar(d)
            args = (e["s_mil"].to_numpy(dtype=float), e["delta_principal"].to_numpy(dtype=float),
                    e["corte_mil"].to_numpy(dtype=float))
            kw = {"grupo": e["grupo"].to_numpy(), "h_mil": H, "cluster": e["co_ibge"].to_numpy(),
                  "ids_unidade": e["co_ibge"].to_numpy()}
            base = L.rd_empilhado_honesto(*args, cortes_vizinhos=CORTES, **kw)
            for f in FATORES_M:
                hon = base if f == 1.0 else (L.rd_empilhado_honesto(*args, M=f * base["M"], **kw)
                                             if base.get("M") is not None and np.isfinite(base["M"])
                                             else {**base, "ic95_inf": np.nan, "ic95_sup": np.nan, "M": np.nan})
                linhas.append(linha_de({**hon, "h_mil": H}, f, False,
                                       "DiRD empilhado; IC honesto Armstrong-Kolesar (variancia CR1)"))
        else:
            tab = L.rd_honesto_relato(s, y, corte, fatores_M=FATORES_M, cortes_vizinhos=CORTES)
            for rec in tab.to_dict("records"):
                linhas.append(linha_de(rec, rec["fator_M"], rec["especificacao"] == "h_otimo",
                                       "DiRD local linear triangular; IC honesto Armstrong-Kolesar (vizinhos, J=3)"))
    except ValueError as erro:
        principal["nota"] = _juntar(principal["nota"], f"IC honesto nao calculado: {erro}")
    return linhas


def suplementares(meta: dict, d: pd.DataFrame, corte, janelas, sup: dict) -> list[dict]:
    """S2 (donut), S3 (porte IED, por corte) e S4 (Amazônia Legal/fronteira, só 0,400), como no E7."""
    linhas = []
    est = "DiRD principal na subamostra"

    def estimar(sub):
        return E7.rd_delta(sub, "y_pos", "y_pre", corte)

    donut = d[~d["s_mil"].isin([float(c) for c in CORTES])]
    ln = preencher(nova_linha(meta, "S2_donut", f"{est}: exclui IVS == 0,300 e == 0,400", janelas=janelas),
                   estimar(donut))
    ln["nota"] = _juntar(f"{len(d) - len(donut)} municipios excluidos (IVS exatamente num corte)", ln["nota"])
    linhas.append(ln)
    if corte == EMPILHADO:
        return linhas
    s3 = sup.get("S3") or {}
    nomes3 = ("S3_porte_muda", "S3_porte_nao_muda", "S3_diferenca")
    if s3.get("tabela") is None:
        for n in nomes3:
            ln = nova_linha(meta, n, est, janelas=janelas)
            ln["status"], ln["nota"] = "NAO_EXECUTADO", s3.get("motivo", "insumo do S3 indisponivel")
            linhas.append(ln)
    else:
        porte = d["co_ibge"].map(s3["tabela"])
        muda = porte.isin(s3["portes_muda"][corte])
        ra, rb = estimar(d[muda & porte.notna()]), estimar(d[~muda & porte.notna()])
        for nome, rr in zip(nomes3, (ra, rb, E7._rd_dif(ra, rb))):
            ln = preencher(nova_linha(meta, nome, f"{est}; portes onde o estrato muda: {sorted(s3['portes_muda'][corte])}",
                                      janelas=janelas), rr)
            if int(porte.isna().sum()):
                ln["nota"] = _juntar(ln["nota"], f"{int(porte.isna().sum())} municipios sem porte no a10 (fora)")
            linhas.append(ln)
    if corte == 400:
        s4 = sup.get("S4") or {}
        nomes4 = ("S4_dentro", "S4_fora", "S4_diferenca")
        if s4.get("tabela") is None:
            for n in nomes4:
                ln = nova_linha(meta, n, est, janelas=janelas)
                ln["status"], ln["nota"] = "NAO_EXECUTADO", s4.get("motivo", "insumo do S4 indisponivel")
                linhas.append(ln)
        else:
            flag = d["co_ibge"].map(s4["tabela"])
            ra, rb = estimar(d[(flag == 1) & flag.notna()]), estimar(d[(flag != 1) & flag.notna()])
            for nome, rr in zip(nomes4, (ra, rb, E7._rd_dif(ra, rb))):
                ln = preencher(nova_linha(meta, nome, f"{est}; {s4['definicao']}", janelas=janelas), rr)
                if int(flag.isna().sum()):
                    ln["nota"] = _juntar(ln["nota"], f"{int(flag.isna().sum())} municipios sem atributo (fora)")
                linhas.append(ln)
    return linhas


def _completar_relativos(linhas: list[dict], media: float) -> None:
    for ln in linhas:
        ln["media_pre_abaixo"] = media
        tau, ep = float(ln["tau"]), float(ln["ep"]) if np.isfinite(float(ln["ep"])) else np.nan
        if np.isfinite(ep):
            ln["mde"] = FATOR_MDE * ep
        if ln["especificacao"] == "poisson_dird":
            if np.isfinite(tau):
                ln["efeito_relativo"] = math.expm1(tau)
                ln["efeito_relativo_ic95_inf"] = math.expm1(float(ln["ic95_inf"]))
                ln["efeito_relativo_ic95_sup"] = math.expm1(float(ln["ic95_sup"]))
            ln["mde_relativo"] = math.expm1(ln["mde"]) if np.isfinite(float(ln["mde"])) else np.nan
            continue
        if np.isfinite(media) and media != 0 and np.isfinite(tau):
            ln["efeito_relativo"] = tau / media
            ln["efeito_relativo_ic95_inf"] = float(ln["ic95_inf"]) / media
            ln["efeito_relativo_ic95_sup"] = float(ln["ic95_sup"]) / media
            ln["mde_relativo"] = ln["mde"] / media if np.isfinite(float(ln["mde"])) else np.nan


def estimar_outcome(spec: dict, pop_nome: str, D: Dados, sup: dict) -> tuple[list[dict], dict, pd.DataFrame]:
    base_u = D.base if pop_nome == "U" else D.base[D.base["V1"]]
    num, den, _ = contagens(D, spec)
    num = num.reindex(base_u.index)
    den = den.reindex(base_u.index) if den is not None else None
    pop, s_mil = base_u["populacao_2022"].astype(float), base_u["s_mil"].astype(float)
    pre_extra = PRE_EXTRA_CNES if spec["fonte"] == "CNES" else PRE_EXTRA
    d = base_janelas(num, den, pop, s_mil, spec["pos"], pre_extra=pre_extra)
    dc = base_janelas(num, den, pop, s_mil, spec["pos"], completo=True, pre_extra=pre_extra)
    unidade = UNIDADES[spec["unidade"]]
    jan = (COMP_PRE, spec["pos"])
    meta0 = {"outcome_id": spec["id"], "descricao_outcome": spec["desc"], "papel": spec["papel"],
             "fonte": spec["fonte"], "populacao": pop_nome, "unidade": unidade}
    linhas = []
    for corte in (*CORTES, EMPILHADO):
        meta = {**meta0, "corte": ROTULO_CORTE[corte]}
        bloco = []
        est_p = ("DiRD local linear triangular sobre delta, EP HC1" if corte != EMPILHADO else
                 "DiRD empilhado (r = s - c, intercepto e inclinacoes por corte x lado, tau comum), CR1 por municipio")
        lp = preencher(nova_linha(meta, "principal", est_p, janelas=jan), E7.rd_delta(d, "y_pos", "y_pre", corte))
        sem = int((~np.isfinite(d["delta_principal"].to_numpy(dtype=float))).sum())
        if sem:
            lp["nota"] = _juntar(f"{sem} municipios sem delta (fora)", lp["nota"])
        bloco.append(lp)
        bloco.append(preencher(nova_linha(meta, "media_completa", est_p, janelas=jan),
                               E7.rd_delta(dc, "y_pos", "y_pre", corte)))
        for h in H_SENS:
            bloco.append(preencher(nova_linha(meta, "sensibilidade_h", est_p, h_mil=h, janelas=jan),
                                   E7.rd_delta(d, "y_pos", "y_pre", corte, h)))
        if spec["honesto"]:
            bloco.extend(linhas_honesto(meta, d, corte, jan, lp))
        if spec["poisson"]:
            rp = poisson_dird(d, corte)
            bloco.append(preencher(nova_linha(meta, "poisson_dird", rp["estimador"], janelas=jan), rp))
        lpl = preencher(nova_linha(meta, "placebo_pre", f"{est_p}; delta = media(202412-202505) - media(202406-202411)",
                                   janelas=(PLACEBO_A, PLACEBO_B)),
                        E7.rd_delta(d, "y_placebo_b", "y_placebo_a", corte))
        lpl["nota"] = _juntar("KP3; placebo nao e nulo limpo: IED desde 05/2024, nutricao 11/2024, emendas 04-05/2025 "
                              "(auditoria 18 §3.1)", lpl["nota"])
        bloco.append(lpl)
        for esp, col in (("nivel_pre", "y_pre"), ("nivel_pos", "y_pos")):
            bloco.append(preencher(nova_linha(meta, esp, f"RDD em nivel de {col}", contraste=CONTRASTE_NIVEL,
                                              janelas=jan), E7.rd(d, col, corte)))
        l5 = preencher(nova_linha(meta, "S5_pre_menos_pre_extra", f"{est_p}; delta = media(pre) - media(pre extra)",
                                  janelas=(pre_extra, COMP_PRE)), E7.rd_delta(d, "y_pre", "y_pre_extra", corte))
        l5["contraste"] = "mudanca da descontinuidade entre 2022-01..2023-03 e o pre principal, antes do PMM-E"
        bloco.append(l5)
        bloco.extend(suplementares(meta, d, corte, jan, sup))
        for var in spec.get("variantes", []):
            nv, dv, _ = contagens(D, spec, var)
            nv = nv.reindex(base_u.index)
            dv = dv.reindex(base_u.index) if dv is not None else None
            pos_v = var.get("pos", spec["pos"])
            bv = base_janelas(nv, dv, pop, s_mil, pos_v, pre_extra=pre_extra)
            ln = preencher(nova_linha(meta, f"sens|{var['nome']}", est_p, variante=var["nome"],
                                      janelas=(COMP_PRE, pos_v)), E7.rd_delta(bv, "y_pos", "y_pre", corte))
            ln["nota"] = _juntar(var["motivo"], ln["nota"])
            bloco.append(ln)
        _completar_relativos(bloco, media_abaixo(d, corte))
        linhas.extend(bloco)
    info = {"n_municipios": int(len(d)), "n_delta_principal": int(np.isfinite(d["delta_principal"]).sum()),
            "n_delta_media_completa": int(np.isfinite(dc["delta_principal"]).sum())}
    return linhas, info, d


# ---------------------------------------------------------------------------
# 6. Estudo de evento
# ---------------------------------------------------------------------------

def janela_de(comp: str, spec: dict) -> str:
    if comp in PRE_EXTRA or comp in PRE_EXTRA_CNES:
        return "pre_extra"
    if comp < COMP_PRE[0]:
        return "entre_pre_extra_e_pre"
    if comp in COMP_PRE:
        return "pre"
    if comp < spec["pos"][0]:
        return "transicao"
    if comp <= spec["pos"][-1]:
        return "pos"
    return "pos_sensibilidade"


def serie_mensal(num: pd.DataFrame, den: pd.DataFrame | None, pop: pd.Series) -> pd.DataFrame:
    if den is None:
        return num.div(pop, axis=0) * ESCALA_HAB
    return (num / den).where(den > 0)


def estudo_evento(spec: dict, pop_nome: str, D: Dados) -> list[dict]:
    base_u = D.base if pop_nome == "U" else D.base[D.base["V1"]]
    num, den, meses = contagens(D, spec)
    R = serie_mensal(num.reindex(base_u.index), den.reindex(base_u.index) if den is not None else None,
                     base_u["populacao_2022"].astype(float))
    s = base_u["s_mil"].to_numpy(dtype=float)
    ref = R[COMP_REF].to_numpy(dtype=float)
    meta = {"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "familia": "K", "outcome_id": spec["id"],
            "populacao": pop_nome, "unidade": UNIDADES[spec["unidade"]]}
    linhas = []
    for per in meses:
        for corte in (*CORTES, EMPILHADO):
            base = {**meta, "corte": ROTULO_CORTE[corte], "competencia": per, "h": H / 1000.0,
                    "janela": janela_de(per, spec), "data": f"{per[:4]}-{per[4:]}"}
            if per == COMP_REF:
                linhas.append({**base, "referencia": True, "tau": np.nan, "ep": np.nan, "ic95_inf": np.nan,
                               "ic95_sup": np.nan, "p_valor": np.nan, "n_abaixo": None, "n_acima": None,
                               "nota": "mes de referencia: normalizado a zero, nao estimado"})
                continue
            dy = R[per].to_numpy(dtype=float) - ref
            if corte == EMPILHADO:
                r = E7.rd(pd.DataFrame({"co_ibge": base_u.index, "s_mil": s, "dy": dy}), "dy", EMPILHADO)
            else:
                r = L.rd_local_linear(s, dy, corte, H)
            linhas.append({**base, "referencia": False, **{k: r.get(k) for k in (
                "n_abaixo", "n_acima", "tau", "ep", "ic95_inf", "ic95_sup", "p_valor", "nota")}})
    return linhas


# ---------------------------------------------------------------------------
# 7. Holm e BKY
# ---------------------------------------------------------------------------

def _mascara_teste(est: pd.DataFrame, ids) -> pd.Series:
    return (est["outcome_id"].isin(ids) & (est["populacao"] == "U") & (est["corte"] == EMPILHADO)
            & (est["especificacao"] == "principal") & (est["status"] == "EXECUTADO"))


def aplicar_testes(est: pd.DataFrame) -> pd.DataFrame:
    est = est.copy()
    est["p_holm"], est["q_bky"] = np.nan, np.nan
    mh = _mascara_teste(est, PRIMARIAS)
    if int(mh.sum()) != len(PRIMARIAS):
        raise FalhaValidacao(f"Holm: {int(mh.sum())} linhas primarias executadas (esperadas {len(PRIMARIAS)})")
    est.loc[mh, "entra_holm"] = True
    est.loc[mh, "p_holm"] = L.holm(est.loc[mh, "p_valor"].to_numpy(dtype=float))
    mb = _mascara_teste(est, SECUNDARIAS)
    est.loc[mb, "entra_bky"] = True
    est.loc[mb, "q_bky"] = L.qvalores_bky(est.loc[mb, "p_valor"].to_numpy(dtype=float))
    return est


# ---------------------------------------------------------------------------
# 8. Figuras (estilo aceito em N_figuras: bloco "COMO LER" dentro da imagem)
# ---------------------------------------------------------------------------

SUPERFICIE, TINTA, TINTA_2 = "#fcfcfb", "#0b0b0b", "#52514e"
COR_PONTO, COR_IC, COR_PRE, COR_POS, COR_POS_SENS, COR_ATO = "#1d4f91", "#2a78d6", "#e7e6e2", "#dbe8f8", "#eef3fb", "#b91c1c"
NOMES_MES = ("jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez")


def _mes_txt(c: str) -> str:
    return f"{NOMES_MES[int(c[4:]) - 1]}/{c[:4]}"


def _fmt(v, casas=2, sinal=True) -> str:
    if v is None or not np.isfinite(float(v)):
        return "—"
    return (f"{float(v):+.{casas}f}" if sinal else f"{float(v):.{casas}f}").replace("-", "−").replace(".", ",")


def _rotulo_unidade(spec: dict) -> str:
    if spec["unidade"] == "fracao":
        return "participação do SUS (fração)"
    if spec["fonte"] == "CNES":
        return ("vínculos" if spec["medida"] == "vinculos_nao_sus" else "horas semanais") + " por 10 mil habitantes"
    if spec["fonte"] == "SIH":
        return "AIH por 10 mil habitantes por mês"
    return "procedimentos por 10 mil habitantes por mês"


def _o_que(spec: dict) -> str:
    """Substantivo do outcome para os guias de leitura (auditoria 21: K4 é capacidade, não produção)."""
    if spec["unidade"] == "fracao":
        return "da participação do SUS nas consultas"
    if spec["fonte"] == "CNES":
        return "dos vínculos não SUS" if spec["medida"] == "vinculos_nao_sus" else "das horas semanais não SUS"
    if spec["fonte"] == "SIH":
        return "das cirurgias com internação (AIH)"
    return "da produção"


def legenda_dird(spec: dict) -> str:
    por_hab = "" if spec["unidade"] == "fracao" else ", por 10 mil habitantes"
    return (
        f"COMO LER. Para cada município calcula-se a mudança {_o_que(spec)}: a média mensal no pós "
        f"({_mes_txt(spec['pos'][0])} a {_mes_txt(spec['pos'][-1])}) menos a média mensal no pré "
        f"({_mes_txt(COMP_PRE[0])} a {_mes_txt(COMP_PRE[-1])}){por_hab}. Cada ponto é a média dessa mudança "
        "entre os municípios de uma faixa de IVS de largura 0,010 (o tamanho do ponto é o número de municípios); azul: "
        "faixa dentro da janela usada na estimativa (IVS a menos de 0,050 do corte); cinza: fora da janela, só para "
        "contexto. A média de uma faixa pode ficar longe das outras por causa de um único município com mudança muito "
        "grande (por 10 mil habitantes, isso acontece sobretudo em municípios pequenos). As "
        "retas são ajustadas separadamente de cada lado do corte (municípios mais perto do corte pesam mais), com a "
        "faixa clara do IC 95%. A seta laranja no corte é o salto: quanto essa mudança foi maior (ou menor) do lado de "
        "bolsa maior, à direita, do que do lado de bolsa menor, à esquerda; o valor e o IC 95% estão no título de cada "
        "painel (a seta pode ser curta demais para ver). Salto com IC 95% que cruza zero quer dizer que não se vê "
        "diferença, não que a diferença seja zero. Em 0,300 a bolsa passa de R$ 10 mil para R$ 15 mil por mês; em "
        "0,400, de R$ 15 mil para R$ 20 mil. Por usar a mudança, o que já era diferente no corte antes do PMM-E sai da "
        "conta; o que outras políticas com o mesmo corte mudaram no mesmo período, não. EMPIRICO.")


def figura_dird(spec: dict, d: pd.DataFrame, est: pd.DataFrame, caminho: Path) -> dict:
    N23 = _importar(DIR_RDD / "23_estimar_contagem_vagas.py", "n23_para_k")
    paineis, meta = [], []
    for c in CORTES:
        lo, hi = N23._limites_segmento(c)
        s = L.normalizar_s_mil(d["s_mil"].to_numpy(dtype=float))
        y = d["delta_principal"].to_numpy(dtype=float)
        r = L.rd_local_linear(s, y, c, H, detalhes=True)
        g = est[(est["outcome_id"] == spec["id"]) & (est["populacao"] == "U") & (est["corte"] == ROTULO_CORTE[c])
                & (est["especificacao"] == "principal")].iloc[0]
        if abs(float(g["tau"]) - r["tau"]) > 1e-9 * max(1.0, abs(r["tau"])):
            raise FalhaValidacao(f"figura {spec['id']} {c}: salto difere do CSV")
        mostra = (s > lo) & (s <= hi)
        un = "p.p." if spec["unidade"] == "fracao" else ""
        tau_txt = (_fmt(100 * r["tau"]), _fmt(100 * r["ic95_inf"]), _fmt(100 * r["ic95_sup"])) if un else \
            (_fmt(r["tau"]), _fmt(r["ic95_inf"]), _fmt(r["ic95_sup"]))
        paineis.append({"x": np.where(mostra, s, np.nan), "y": y, "dentro": np.abs(s - c) < H, "corte": c,
                        "curva": N23.curva_um_corte(r, c), "rotulo": f"corte {ROTULO_CORTE[c].replace('.', ',')}",
                        "titulo": f"salto = {tau_txt[0]} {un} [IC 95%: {tau_txt[1]}; {tau_txt[2]}],  "
                                  f"p = {_fmt(r['p_valor'], 3, False)}".replace("  [", " ["),
                        })
        meta.append({"corte": ROTULO_CORTE[c], "tau": r["tau"], "ic95_inf": r["ic95_inf"], "ic95_sup": r["ic95_sup"],
                     "p_valor": r["p_valor"]})
    ylab = ("Mudança da participação do SUS (pós − pré)" if spec["unidade"] == "fracao" else
            f"Mudança entre pré e pós (média mensal),\n{_rotulo_unidade(spec)}")
    N23.desenhar(paineis, f"{spec['id']} — {spec['desc']}: mudança entre pré e pós nos cortes (U)", ylab,
                 "IVS 2010 oficial do município", legenda_dird(spec), caminho, rotulo_salto=False)
    return {"arquivo": rotulo(caminho), "outcome_id": spec["id"], "populacao": "U", "tipo": "dird", "paineis": meta}


def _atos_principais() -> list[tuple[str, str]]:
    return [(d, r) for d, r, _, principal in DATAS_POLITICAS if principal]


def legenda_evento(spec: dict, *, com_sensibilidade: bool = True) -> str:
    atos = "; ".join(f"{k} = {r}" for k, (_, r) in enumerate(_atos_principais(), 1))
    o_que = _o_que(spec)
    por_hab = "" if spec["unidade"] == "fracao" else ", por 10 mil habitantes"
    sens = "; azul mais claro: meses fora do pós principal, só da sensibilidade" if com_sensibilidade else ""
    cnes = (" O CNES só tem competências trimestrais antes de jun/2024, por isso há menos pontos nesse trecho."
            if spec["fonte"] == "CNES" else "")
    return (
        "COMO LER. Cada ponto azul compara, num mês, os municípios logo acima do corte (bolsa maior) com os logo abaixo "
        f"(bolsa menor): é o salto no corte {o_que} daquele mês menos o de junho de 2025 (quadrado preto, fixado em "
        f"zero){por_hab}. A barra vertical é o IC 95% de cada mês. Antes do PMM-E (faixa cinza, pré; à "
        "esquerda dela, 2022 a 2024) os pontos deveriam ficar em torno de zero: se já se afastam de zero antes, a "
        "diferença entre os lados não vem da bolsa. Os meses em branco entre o pré e o pós (jul a set/2025) são de "
        f"transição e não entram nas médias. Depois do início do ciclo 1 (faixa azul, pós{sens}) um efeito da bolsa "
        "apareceria como pontos acima de zero (valor maior do lado de bolsa maior) ou abaixo (menor)." + cnes +
        " Linhas vermelhas tracejadas, numeradas no alto do primeiro painel: " + atos + ". Pontilhadas cinza: outros "
        "atos com o mesmo corte (auditoria 18). Painéis: corte 0,300 (R$ 10 mil -> 15 mil), corte 0,400 (R$ 15 mil -> "
        "20 mil) e os dois juntos. EMPIRICO.")


def figura_evento(spec: dict, ev: pd.DataFrame, caminho: Path) -> dict:
    import datetime as dt
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch

    def data(c):
        return dt.date(int(c[:4]), int(c[4:6]), 15)

    cortes = [ROTULO_CORTE[c] for c in (*CORTES, EMPILHADO)]
    titulos = {"0.300": "corte 0,300", "0.400": "corte 0,400", EMPILHADO: "cortes 0,300 e 0,400 juntos"}
    meses = sorted(ev["competencia"].astype(str).unique())
    pos = spec["pos"]
    com_sens = meses[-1] > pos[-1]
    texto = textwrap.wrap(legenda_evento(spec, com_sensibilidade=com_sens), 175)
    h_txt = 0.16 * len(texto) + 0.3
    fig = plt.figure(figsize=(12.5, 3.0 * len(cortes) + 1.4 + h_txt), facecolor=SUPERFICIE)
    altura = 3.0 * len(cortes) + 1.4 + h_txt
    eixos = []
    for i, c in enumerate(cortes):
        ax = fig.add_axes([0.08, (h_txt + 0.9 + 3.0 * (len(cortes) - 1 - i) + 0.35) / altura, 0.9, 2.45 / altura])
        ax.set_facecolor(SUPERFICIE)
        e = ev[ev["corte"] == c].sort_values("competencia")
        x = [data(v) for v in e["competencia"]]
        tau = np.where(e["referencia"].astype(bool), 0.0, e["tau"].astype(float))
        lo, hi = e["ic95_inf"].astype(float).to_numpy(), e["ic95_sup"].astype(float).to_numpy()
        ax.axvspan(data(COMP_PRE[0]) - dt.timedelta(days=15), data(COMP_PRE[-1]) + dt.timedelta(days=15),
                   color=COR_PRE, linewidth=0, zorder=0)
        ax.axvspan(data(pos[0]) - dt.timedelta(days=15), data(pos[-1]) + dt.timedelta(days=15), color=COR_POS,
                   linewidth=0, zorder=0)
        if com_sens:
            ax.axvspan(data(pos[-1]) + dt.timedelta(days=15), data(meses[-1]) + dt.timedelta(days=15),
                       color=COR_POS_SENS, linewidth=0, zorder=0)
        ax.axhline(0, color=TINTA_2, linewidth=0.9)
        for dd, _, _, principal in DATAS_POLITICAS:
            ax.axvline(dt.date.fromisoformat(dd), color=COR_ATO if principal else "#9ca3af",
                       linestyle="--" if principal else ":", linewidth=1.0 if principal else 0.8, alpha=0.85)
        ok = np.isfinite(lo) & np.isfinite(hi)
        xa = np.array(x, dtype=object)
        ax.errorbar(xa[ok], tau[ok], yerr=[tau[ok] - lo[ok], hi[ok] - tau[ok]], fmt="none", ecolor=COR_IC,
                    elinewidth=1.2, alpha=0.6)
        ax.plot(xa[~e["referencia"].astype(bool).to_numpy()], tau[~e["referencia"].astype(bool).to_numpy()], "o",
                color=COR_PONTO, markersize=3.8)
        ref = e["referencia"].astype(bool).to_numpy()
        ax.plot(xa[ref], tau[ref], "s", color=TINTA, markersize=6)
        ax.set_title(titulos[c], fontsize=10, loc="left", color=TINTA)
        ax.set_ylabel("salto no corte, relativo\na jun/2025", fontsize=8.5, color=TINTA_2)
        ax.grid(alpha=0.25, linewidth=0.6)
        ax.tick_params(colors=TINTA_2, labelsize=8)
        ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",")))
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)
        eixos.append(ax)
    for ax in eixos[:-1]:
        ax.tick_params(labelbottom=False)
    eixos[-1].set_xlabel("mês (SIA e SIH: mês de processamento; TISS: mês de realização; CNES: competência)",
                         fontsize=9, color=TINTA_2)
    # Números dos atos principais acima do primeiro painel, fora da área dos dados (auditoria 21: o rótulo vertical
    # dentro do painel cobria pontos e barras); a chave dos números está no "COMO LER".
    for k, (dd, _) in enumerate(_atos_principais(), 1):
        eixos[0].annotate(str(k), xy=(dt.date.fromisoformat(dd), 1.0), xycoords=("data", "axes fraction"),
                          xytext=(0, 2), textcoords="offset points", ha="center", va="bottom", fontsize=7.5,
                          fontweight="bold", color=COR_ATO, annotation_clip=False)
    handles = [Line2D([], [], marker="o", linestyle="", color=COR_PONTO, label="salto no mês (lado de bolsa maior − menor)"),
               Line2D([], [], color=COR_IC, linewidth=1.2, label="IC 95% do mês"),
               Line2D([], [], marker="s", linestyle="", color=TINTA, label="jun/2025 = referência (zero)"),
               Patch(color=COR_PRE, label="pré"), Patch(color=COR_POS, label="pós principal")]
    if com_sens:
        handles.append(Patch(color=COR_POS_SENS, label="meses só da sensibilidade"))
    handles += [Line2D([], [], color=COR_ATO, linestyle="--", label="PMM-E e portarias principais (números no alto)"),
                Line2D([], [], color="#9ca3af", linestyle=":", label="outros atos com o mesmo corte")]
    fig.legend(handles=handles, loc="center", ncol=4, fontsize=8, frameon=False,
               bbox_to_anchor=(0.5, (h_txt + 0.45) / altura))
    fig.suptitle(f"{spec['id']} — {spec['desc']}\nestudo de evento: {_rotulo_unidade(spec)} (U)", fontsize=10.5,
                 color=TINTA, y=1 - 0.1 / altura)
    fig.text(0.015, 0.1 / altura, "\n".join(texto), fontsize=7.6, color=TINTA_2, va="bottom", ha="left",
             linespacing=1.25, parse_math=False)
    fig.savefig(caminho, dpi=120, facecolor=SUPERFICIE)
    plt.close(fig)
    return {"arquivo": rotulo(caminho), "outcome_id": spec["id"], "populacao": "U", "tipo": "evento"}


def gerar_figuras(bases: dict, est: pd.DataFrame, ev: pd.DataFrame, dir_fig: Path) -> list[dict]:
    dir_fig.mkdir(parents=True, exist_ok=True)
    for antigo in dir_fig.glob("*.png"):
        antigo.unlink()
    feitas = []
    for oid in FIGURAS_OUTCOMES:
        spec = next(c for c in CATALOGO if c["id"] == oid)
        tag = oid.replace(".", "_")
        feitas.append(figura_dird(spec, bases[(oid, "U")], est, dir_fig / f"K_D1_dird_{tag}_U.png"))
        e = ev[(ev["outcome_id"] == oid) & (ev["populacao"] == "U")]
        feitas.append(figura_evento(spec, e, dir_fig / f"K_D1_evento_{tag}_U.png"))
    return feitas


# ---------------------------------------------------------------------------
# 9. Tabelas e leitura do doc 50 (geradas das saídas; nenhum número digitado)
# ---------------------------------------------------------------------------

def _n(v, casas=3, pp=False, sinal=True) -> str:
    return E7._n(v, casas, pp, sinal)


def _p(v) -> str:
    return E7._p(v)


def _escala(unidade: str) -> tuple[int, bool, str]:
    return (1, True, "p.p.") if str(unidade).startswith("fracao") else (2, False, "")


def _tab(sub: pd.DataFrame, cab: list[str], cols) -> str:
    return E7._tab(sub, cab, [lambda r, f=f: _esc(f(r)) for f in cols])


def _esc(txt) -> str:
    """Barra vertical dentro de célula de tabela Markdown (por exemplo, 'sens|pos_ate_202607')."""
    return str(txt).replace("|", "\\|")


def _tau(r):
    c, pp, u = _escala(r["unidade"])
    return f"{_n(r['tau'], c, pp)} {u}".strip()


def _ic(r, a="ic95_inf", b="ic95_sup"):
    c, pp, _ = _escala(r["unidade"])
    return f"[{_n(r[a], c, pp)}; {_n(r[b], c, pp)}]"


def _rel(r):
    if pd.isna(r.get("efeito_relativo")):
        return "—"
    return (f"{_n(r['efeito_relativo'], 1, pp=True)} % [{_n(r['efeito_relativo_ic95_inf'], 1, pp=True)}; "
            f"{_n(r['efeito_relativo_ic95_sup'], 1, pp=True)}]")


def _corte(r):
    return str(r["corte"]).replace(".", ",")


def _nab(r):
    return f"{E7._fmt_int(r['n_abaixo'])} / {E7._fmt_int(r['n_acima'])}"


ORDEM = {c["id"]: i for i, c in enumerate(CATALOGO)}
ORDEM_CORTE = {"0.300": 0, "0.400": 1, EMPILHADO: 2}


def _ordenar(sub: pd.DataFrame) -> pd.DataFrame:
    return sub.assign(_o=sub["outcome_id"].map(ORDEM), _c=sub["corte"].map(ORDEM_CORTE),
                      _p=sub["populacao"].map({"U": 0, "V1": 1})).sort_values(["_o", "_p", "_c"], kind="stable")


def _linha(est, oid, pop="U", corte=EMPILHADO, esp="principal"):
    g = est[(est["outcome_id"] == oid) & (est["populacao"] == pop) & (est["corte"].astype(str) == corte)
            & (est["especificacao"] == esp)]
    return g.iloc[0].to_dict() if len(g) == 1 else None


def classificar(r: dict | None) -> str:
    """'sobe' se o IC 95% fica acima de zero, 'cai' se fica abaixo, 'indeterminado' se inclui zero."""
    if r is None or not np.isfinite(float(r["ic95_inf"])):
        return "sem estimativa"
    if float(r["ic95_inf"]) > 0:
        return "sobe"
    if float(r["ic95_sup"]) < 0:
        return "cai"
    return "indeterminado"


def leitura_substituicao(pares: dict[str, dict | None], *, desenho: str) -> str:
    """Padrões do §5 do protocolo 47 a partir dos sinais (IC 95%) de SUS alvo, privado alvo, total e não alvo."""
    c = {k: classificar(v) for k, v in pares.items()}
    nomes = {"sus": "SUS nas CBO-alvo (K1)", "privado_vinculos": "vínculos não SUS das CBO-alvo (K4.vinculos)",
             "privado_horas": "horas não SUS das CBO-alvo (K4.horas)", "planos": "consultas dos planos nas CBO-alvo "
             "(K3a.consultas)", "total": "consultas SUS + planos nas CBO-alvo (K3)",
             "nao_alvo": "SUS dos especialistas fora das CBO-alvo (KP2)"}
    partes = [f"{nomes[k]}: {c[k]}" for k in nomes if k in c]
    privado_cai = any(c.get(k) == "cai" for k in ("privado_vinculos", "privado_horas", "planos"))
    padroes = []
    if c.get("sus") == "sobe" and privado_cai:
        padroes.append("SUS sobe e o privado cai na mesma especialidade: migração de horas do privado para o SUS, "
                       "sem ganho líquido")
    if c.get("total") == "sobe":
        padroes.append("o total sobe: ganho líquido")
    if c.get("sus") == "sobe" and c.get("nao_alvo") == "cai":
        padroes.append("alvo sobe e não alvo cai: remanejamento entre especialidades")
    txt = (f"{desenho}. Sinal de cada margem pelo IC 95% ('sobe' = IC acima de zero; 'cai' = abaixo; "
           f"'indeterminado' = inclui zero): " + "; ".join(partes) + ". ")
    if padroes:
        txt += "Padrão do §5 que aparece: " + "; ".join(padroes) + "."
    else:
        txt += ("Nenhum dos três padrões do §5 (migração, ganho líquido, remanejamento) aparece, porque nenhuma das "
                "margens necessárias tem IC que exclua zero no sentido exigido. Isso não mostra ausência de "
                "substituição: mostra que os dados não a distinguem de zero.")
    return txt


def gerar_tabelas_doc(est: pd.DataFrame, ev: pd.DataFrame, resumo: dict) -> dict[str, str]:
    t: dict[str, str] = {}
    esp = est["especificacao"]
    # Primárias (U, empilhado) com Holm, honesto, MDE e relativo.
    sub = _ordenar(est[est["entra_holm"].astype(bool)])
    t["primarias"] = _tab(sub, ["Outcome", "n abaixo / acima", "Salto (por 10 mil hab./mês)", "IC 95% (CR1)",
                                "p", "p Holm", "IC honesto (M)", "MDE (2,8 × EP)", "Efeito relativo [IC 95%]",
                                "Média do pré abaixo do corte"],
                          [lambda r: r["outcome_id"], _nab, _tau, _ic, lambda r: _p(r["p_valor"]),
                           lambda r: f"**{_p(r['p_holm'])}**", lambda r: _ic(r, "ic_honesto_inf", "ic_honesto_sup"),
                           lambda r: _n(r["mde"], 2, sinal=False), _rel,
                           lambda r: _n(r["media_pre_abaixo"], 2, sinal=False)])
    sub = _ordenar(est[est["outcome_id"].isin(PRIMARIAS) & (esp == "principal")])
    t["primarias_cortes"] = _tab(sub, ["Outcome", "População", "Corte", "n abaixo / acima", "Salto", "IC 95%", "p",
                                       "IC honesto (M)", "MDE", "Efeito relativo [IC 95%]"],
                                 [lambda r: r["outcome_id"], lambda r: r["populacao"], _corte, _nab, _tau, _ic,
                                  lambda r: _p(r["p_valor"]), lambda r: _ic(r, "ic_honesto_inf", "ic_honesto_sup"),
                                  lambda r: _n(r["mde"], 2, sinal=False), _rel])
    sub = _ordenar(est[est["outcome_id"].isin(SECUNDARIAS) & (esp == "principal") & (est["populacao"] == "U")])
    t["secundarias"] = _tab(sub, ["Outcome", "Descrição", "Corte", "n abaixo / acima", "Salto", "IC 95%", "p",
                                  "q BKY", "Efeito relativo [IC 95%]"],
                            [lambda r: r["outcome_id"], lambda r: r["descricao_outcome"], _corte, _nab, _tau, _ic,
                             lambda r: _p(r["p_valor"]), lambda r: _p(r["q_bky"]), _rel])
    sub = _ordenar(est[est["papel"].isin(["placebo", "suplementar"]) & (esp == "principal") & (est["populacao"] == "U")])
    t["placebos"] = _tab(sub, ["Placebo", "Descrição", "Corte", "n abaixo / acima", "Salto", "IC 95%", "p",
                               "Efeito relativo [IC 95%]"],
                         [lambda r: r["outcome_id"], lambda r: r["descricao_outcome"], _corte, _nab, _tau, _ic,
                          lambda r: _p(r["p_valor"]), _rel])
    sub = _ordenar(est[(esp == "placebo_pre") & (est["populacao"] == "U")])
    t["kp3"] = _tab(sub, ["Outcome", "Corte", "n abaixo / acima", "Salto (dentro do pré)", "IC 95%", "p"],
                    [lambda r: r["outcome_id"], _corte, _nab, _tau, _ic, lambda r: _p(r["p_valor"])])
    # Robustez das primárias.
    linhas = ["| Outcome | População | Corte | Especificação | n abaixo / acima | Salto | IC 95% | p | Efeito relativo |",
              "|---|---|---|---|---|---|---|---|---|"]
    rob = _ordenar(est[est["outcome_id"].isin(PRIMARIAS) & ~esp.isin(["principal", "ic_honesto",
                                                                        "ic_honesto_h_otimo", "nivel_pre",
                                                                        "nivel_pos", "placebo_pre",
                                                                        "S5_pre_menos_pre_extra"])
                       & ~esp.str.startswith(("S3", "S4"))])
    for r in rob.to_dict("records"):
        nome = r["especificacao"] + (f" h = {_n(r['h'], 3, sinal=False)}" if r["especificacao"] == "sensibilidade_h" else "")
        tau_txt = (f"{_n(r['tau'], 4)} (log)" if r["especificacao"] == "poisson_dird" else _tau(r))
        ic_txt = (f"[{_n(r['ic95_inf'], 4)}; {_n(r['ic95_sup'], 4)}]" if r["especificacao"] == "poisson_dird"
                  else _ic(r))
        linhas.append(f"| {r['outcome_id']} | {r['populacao']} | {_corte(r)} | {_esc(nome)} | {_nab(r)} | {tau_txt} | "
                      f"{ic_txt} | {_p(r['p_valor'])} | {_rel(r)} |")
    t["robustez"] = "\n".join(linhas)
    sub = _ordenar(est[est["outcome_id"].isin(PRIMARIAS) & esp.isin(["ic_honesto", "ic_honesto_h_otimo"])])
    t["honesto"] = _tab(sub, ["Outcome", "População", "Corte", "Especificação", "fator de M", "M", "h", "IC honesto",
                              "p honesto"],
                        [lambda r: r["outcome_id"], lambda r: r["populacao"], _corte, lambda r: r["especificacao"],
                         lambda r: _n(r["fator_M"], 1, sinal=False), lambda r: _n(r["M"], 1, sinal=False),
                         lambda r: _n(r["h"], 3, sinal=False), lambda r: _ic(r, "ic_honesto_inf", "ic_honesto_sup"),
                         lambda r: _p(r["p_valor"])])
    sub = _ordenar(est[esp.isin(["nivel_pre", "nivel_pos", "S5_pre_menos_pre_extra"]) & (est["populacao"] == "U")
                       & est["outcome_id"].isin(PRIMARIAS + ["KP1", "KP2"])])
    t["niveis_s5"] = _tab(sub, ["Outcome", "Corte", "Especificação", "Salto", "IC 95%", "p"],
                          [lambda r: r["outcome_id"], _corte, lambda r: r["especificacao"], _tau, _ic,
                           lambda r: _p(r["p_valor"])])
    sub = _ordenar(est[esp.str.startswith(("S3", "S4")) & (est["populacao"] == "U")
                       & est["outcome_id"].isin(PRIMARIAS)])
    t["s3_s4"] = _tab(sub, ["Outcome", "Corte", "Especificação", "n abaixo / acima", "Salto", "IC 95%", "p"],
                      [lambda r: r["outcome_id"], _corte, lambda r: r["especificacao"], _nab, _tau, _ic,
                       lambda r: _p(r["p_valor"])])
    # Estudo de evento: resumo por janela (U).
    e = ev[~ev["referencia"].astype(bool) & (ev["populacao"] == "U")].copy()
    linhas = ["| Outcome | Corte | Janela | Meses estimados | p < 0,05 | maior abs(salto) | salto médio |",
              "|---|---|---|---|---|---|---|"]
    ordem_j = {"pre_extra": 0, "entre_pre_extra_e_pre": 1, "pre": 2, "transicao": 3, "pos": 4, "pos_sensibilidade": 5}
    e = e.assign(_o=e["outcome_id"].map(ORDEM), _c=e["corte"].map(ORDEM_CORTE), _j=e["janela"].map(ordem_j))
    for (o, c_, j), g in e.sort_values(["_o", "_c", "_j"], kind="stable").groupby(["outcome_id", "corte", "janela"],
                                                                                  sort=False):
        cc, pp, _ = _escala(g["unidade"].iloc[0])
        ok = g[np.isfinite(g["tau"].astype(float))]
        linhas.append(f"| {o} | {str(c_).replace('.', ',')} | {j} | {len(ok)} | {int((ok['p_valor'] < 0.05).sum())} | "
                      f"{_n(ok['tau'].abs().max() if len(ok) else np.nan, cc, pp, sinal=False)} | "
                      f"{_n(ok['tau'].mean() if len(ok) else np.nan, cc, pp)} |")
    t["evento"] = "\n".join(linhas)
    # Entradas, validações e desvios.
    linhas = ["| Entrada | SHA-256 | Papel |", "|---|---|---|"]
    for b in resumo.get("entradas", []):
        linhas.append(f"| `{b['caminho']}` | `{b['sha256'][:16]}…` | {b['papel']} |")
    t["entradas"] = "\n".join(linhas)
    v = resumo.get("validacoes", {})
    q = resumo.get("contagens", {})
    pv = v.get("populacoes", {})
    t["validacoes"] = "\n".join([
        "| Conferência | Resultado |", "|---|---|",
        f"| SHA-256 dos painéis SIA, SIH, TISS (amb. e hosp.) e CNES = manifestos | {v.get('sha256_iguais_manifestos')} |",
        f"| municípios em U (IVS oficial e população 2022) / em V1 | {pv.get('U_com_populacao')} / {pv.get('V1_municipios')} |",
        f"| U sem população 2022 (fora) | {len(pv.get('U_excluidos_sem_populacao', []))} |",
        f"| municípios do Censo 2022 sem IVS oficial (fora) | {', '.join(pv.get('censo2022_sem_ivs_oficial_fora', [])) or '—'} |",
        f"| municípios do SIA fora de U (fora, sem IVS ou população) | {', '.join(v.get('sia', {}).get('municipios_tabnet_fora_de_U', [])) or '—'} |",
        f"| municípios do SIH fora de U | {', '.join(v.get('sih', {}).get('municipios_painel_fora_de_U', [])) or '—'} |",
        f"| células SIA ausentes (município × mês × conjunto × tipo) | {v.get('sia', {}).get('celulas_ausentes_municipio_mes_conjunto_tipo')} |",
        f"| UF-meses SIH sem dado (ausentes) | {_esc(', '.join(v.get('sih', {}).get('uf_meses_sem_dado', [])) or '—')} |",
        f"| UF-meses SIH atípicos (só na sensibilidade) | {_esc(', '.join(v.get('sih', {}).get('uf_meses_atipicos', [])) or '—')} |",
        f"| células TISS ausentes (amb. / hosp.) | {v.get('tiss', {}).get('celulas_ausentes')} / "
        f"{v.get('tiss_hosp', {}).get('celulas_ausentes')} |",
        f"| UF-meses TISS sinalizados (amb.; só na sensibilidade) | {len(v.get('tiss', {}).get('uf_meses_sinalizados_alertas_queda', []))} |",
        f"| maior mês lido: SIA e SIH / TISS / CNES | {v.get('meses_maximos', {}).get('sia_sih')} / "
        f"{v.get('meses_maximos', {}).get('tiss')} / {v.get('meses_maximos', {}).get('cnes')} |",
        f"| linhas em {NOME_EST} / SEM_ESTIMATIVA / NAO_EXECUTADO | {q.get('linhas')} / {q.get('sem_estimativa')} / "
        f"{q.get('nao_executado')} |",
        f"| linhas em {NOME_EVENTO} | {q.get('linhas_evento')} |",
    ])
    linhas = ["| Data | Tipo | Item | Descrição |", "|---|---|---|---|"]
    for dv in resumo.get("desvios", []):
        linhas.append(f"| {dv['data']} | {dv['tipo']} | {dv['item']} | {_esc(dv['descricao'])} |")
    t["desvios"] = "\n".join(linhas)
    t.update(gerar_leitura(est, ev))
    return t


def _frase_primaria(r: dict, nome: str) -> str:
    return (f"{nome}: salto {_n(r['tau'], 2)} por 10 mil hab. por mês (IC 95% {_ic(r)}, p = {_p(r['p_valor'])}, "
            f"p de Holm = {_p(r['p_holm'])}); a média mensal do pré abaixo do corte é "
            f"{_n(r['media_pre_abaixo'], 2, sinal=False)}, então o salto equivale a {_rel(r)} dela; o menor efeito que "
            f"o desenho detectaria com 80% de poder é {_n(r['mde'], 2, sinal=False)} "
            f"({_n(r['mde_relativo'], 1, pp=True, sinal=False)} % da média).")


def gerar_leitura(est: pd.DataFrame, ev: pd.DataFrame) -> dict[str, str]:
    t = {}
    nomes = {"K1": "Produção SUS ambulatorial das CBO-alvo (K1)", "K2": "Cirurgias SUS hospitalares (K2)",
             "K3": "Consultas especializadas SUS + planos (K3)"}
    frases = []
    rej = 0
    for oid in PRIMARIAS:
        r = _linha(est, oid)
        if r is None:
            frases.append(f"{nomes[oid]}: linha ausente.")
            continue
        rej += int(float(r["p_holm"]) < 0.05)
        frases.append(_frase_primaria(r, nomes[oid]))
    t["leitura_primarias"] = (
        " ".join(frases) + " " +
        (f"{rej} das {len(PRIMARIAS)} primárias rejeita(m) zero a 5% depois do Holm." if rej else
         f"Nenhuma das {len(PRIMARIAS)} primárias rejeita zero a 5% depois do Holm."))
    # Pré-tendências do estudo de evento (U, empilhado): meses do pré e do pré extra com p < 0,05.
    partes, muitos = [], []
    for oid in PRIMARIAS + ["KP1", "KP2"]:
        e = ev[(ev["outcome_id"] == oid) & (ev["populacao"] == "U") & (ev["corte"] == EMPILHADO)
               & ~ev["referencia"].astype(bool)]
        pre = e[e["janela"].isin(["pre_extra", "entre_pre_extra_e_pre", "pre"])]
        pos = e[e["janela"] == "pos"]
        n_rej, n_pre = int((pre["p_valor"] < 0.05).sum()), int(pre["tau"].notna().sum())
        if n_pre and n_rej >= 0.15 * n_pre:      # 3x os 5% esperados por acaso (auditoria 21)
            tau_todos = e["tau"].astype(float).dropna()       # todos os meses (antes e depois de jun/2025)
            mesmo_sinal = max((tau_todos > 0).mean(), (tau_todos < 0).mean())
            muitos.append((oid, float(mesmo_sinal)))
        partes.append(f"{oid}: {n_rej} de {n_pre} meses antes de "
                      f"jun/2025 com p < 0,05; no pós principal, {int((pos['p_valor'] < 0.05).sum())} de "
                      f"{int(pos['tau'].notna().sum())}")
    nota = ""
    for oid, ms in muitos:
        nota += (f" Em {oid}, a fração de meses antes de jun/2025 com p < 0,05 passa de três vezes os 5% esperados por "
                 "acaso: a descontinuidade no corte de jun/2025 difere da dos outros meses.")
        if ms >= 0.8:
            nota += (f" Como {_n(100 * ms, 0, sinal=False)} % dos saltos mensais, antes e depois de jun/2025, têm o "
                     "mesmo sinal, o padrão é o de um mês de referência atípico, e não necessariamente de uma "
                     "tendência; a DiRD, que compara médias de janelas, não depende desse mês.")
        else:
            nota += " A descontinuidade varia no tempo antes do PMM-E, e a DiRD só remove a parte fixa no tempo."
    t["leitura_evento"] = ("Estudo de evento, cortes empilhados, U (mês a mês contra jun/2025): " + "; ".join(partes) +
                           ". Com 5% de nível, cerca de 1 mês em 20 dá p < 0,05 por acaso, sem correção para muitos "
                           "meses." + nota)
    # Placebos.
    partes = []
    for oid in ("KP1", "KP2", "KP1.mfc"):
        r = _linha(est, oid)
        if r is not None:
            partes.append(f"{oid} {_tau(r)} {_ic(r)} (p = {_p(r['p_valor'])})")
    kp3 = [f"{oid} {_tau(r)} (p = {_p(r['p_valor'])})" for oid in PRIMARIAS
           if (r := _linha(est, oid, esp="placebo_pre")) is not None]
    t["leitura_placebos"] = ("Placebos de profissional (U, empilhado): " + "; ".join(partes) +
                             ". Placebo dentro do pré (KP3, U, empilhado): " + "; ".join(kp3) + ".")
    # Substituição (§5).
    pares = {"sus": _linha(est, "K1"), "privado_vinculos": _linha(est, "K4.vinculos"),
             "privado_horas": _linha(est, "K4.horas"), "planos": _linha(est, "K3a.consultas"),
             "total": _linha(est, "K3"), "nao_alvo": _linha(est, "KP2")}
    t["leitura_substituicao"] = leitura_substituicao(pares, desenho="D1 (DiRD nos cortes, U, empilhado)")
    t["leitura_simples"] = leitura_simples(est)
    return t


VERBO = {"sobe": "cresceu mais do lado de bolsa maior", "cai": "cresceu menos do lado de bolsa maior",
         "indeterminado": "não se vê diferença entre os dois lados", "sem estimativa": "não há estimativa"}


def leitura_simples(est: pd.DataFrame) -> str:
    """Parágrafo em linguagem simples das três primárias, montado das saídas (sinal pelo IC 95%)."""
    nomes = {"K1": "consultas, exames, cirurgias e OCI feitos no SUS pelos especialistas-alvo",
             "K2": "cirurgias com internação no SUS",
             "K3": "consultas dos especialistas-alvo no SUS e nos planos de saúde, somadas"}
    partes = []
    for oid in PRIMARIAS:
        r = _linha(est, oid)
        if r is None:
            continue
        partes.append(f"{nomes[oid]} ({oid}): {VERBO[classificar(r)]}; o IC 95% vai de "
                      f"{_n(r['efeito_relativo_ic95_inf'], 1, pp=True)} % a {_n(r['efeito_relativo_ic95_sup'], 1, pp=True)} % "
                      f"da produção média do pré abaixo do corte, e uma diferença menor que cerca de "
                      f"{_n(r['mde_relativo'], 1, pp=True, sinal=False)} % dela não seria detectada")
    corpo = "; ".join(partes)
    corpo = corpo[:1].upper() + corpo[1:]
    return ("Em linguagem simples: a pergunta é se, nos municípios logo acima de 0,300 ou de 0,400, onde a bolsa "
            "anunciada é R$ 5 mil maior, a produção que exige especialista cresceu mais entre antes e depois do início do "
            "PMM-E do que nos municípios logo abaixo. " + corpo + ". Um intervalo que inclui zero não prova "
            "que a bolsa não tem efeito: diz que, com estes municípios e estes meses, um efeito do tamanho que o "
            "intervalo admite não se distingue de zero. E mesmo um salto nítido mediria o incentivo marginal de R$ 5 mil "
            "somado ao que outras políticas com o mesmo corte mudaram no período, não o efeito de ter um especialista do "
            "PMM-E.")


MARCA = re.compile(r"(<!-- K:(?P<nome>[A-Za-z0-9_]+):inicio -->\n)(?P<corpo>.*?)(\n<!-- K:(?P=nome):fim -->)", re.S)


def aplicar_tabelas_doc(texto: str, tabelas: dict[str, str]) -> str:
    def sub(m):
        nome = m.group("nome")
        if nome not in tabelas:
            raise KeyError(f"tabela {nome} nao gerada")
        return m.group(1) + tabelas[nome] + m.group(4)
    return MARCA.sub(sub, texto)


def tabelas_no_doc(texto: str) -> dict[str, str]:
    return {m.group("nome"): m.group("corpo") for m in MARCA.finditer(texto)}


def ler_saidas() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    est = pd.read_csv(OUT / NOME_EST, dtype={"corte": str, "variante": str}, keep_default_na=True)
    est["variante"] = est["variante"].fillna("")
    ev = pd.read_csv(OUT / NOME_EVENTO, dtype={"corte": str, "competencia": str})
    resumo = json.loads((OUT / NOME_RESUMO).read_text(encoding="utf-8"))
    return est, ev, resumo


def atualizar_doc() -> None:
    if not DOC50.exists():
        print(f"{rotulo(DOC50)} nao existe: tabelas nao gravadas")
        return
    est, ev, resumo = ler_saidas()
    DOC50.write_text(aplicar_tabelas_doc(DOC50.read_text(encoding="utf-8"), gerar_tabelas_doc(est, ev, resumo)),
                     encoding="utf-8")
    print(f"tabelas K do doc 50 regravadas: {rotulo(DOC50)}")


# ---------------------------------------------------------------------------
# 10. Execução
# ---------------------------------------------------------------------------

def carregar_dados() -> Dados:
    base, conf_pop = ler_universo()
    universo = base.index
    sia, info_sia = ler_sia(universo)
    sih, sih_atip, info_sih = ler_sih(universo)
    tiss, tiss_atip, info_tiss = ler_tiss(universo)
    tissh, tissh_atip, info_tissh = ler_tiss_hosp(universo)
    cnes, info_cnes = ler_cnes(universo)
    info = {"populacoes": conf_pop, "sia": info_sia, "sih": info_sih, "tiss": info_tiss, "tiss_hosp": info_tissh,
            "cnes": info_cnes, "sha256_iguais_manifestos": True,
            "meses_maximos": {"sia_sih": MESES_SIA[-1], "tiss": MESES_TISS[-1], "cnes": MESES_CNES[-1]}}
    return Dados(base, sia, sih, sih_atip, tiss, tiss_atip, tissh, tissh_atip, cnes, info)


def entradas() -> list[dict]:
    b = E7.bloco_entrada
    return [
        b(SIA, "SIA/SUS: K1, K1a-K1f, K3, K3b, K5, KP1, KP2", "DATASUS TabNet qabr.def (a12)", "processamento 202201-202607",
          "municipios do formulario", "municipio x mes x subgrupo x conjunto CBO",
          "co_ibge, competencia_processamento, subgrupo, conjunto_cbo",
          "conjuntos alvo_pmme, especialistas_nao_alvo, generalistas, mfc_225130; subgrupos 0301, 02xx, 04xx, 09xx"),
        b(SIA_SUBG, "SIA: subgrupos presentes em cada consulta (zero de subgrupo omitido)", "a12", "202201-202607",
          "mes x conjunto x subgrupo", "consulta", "competencia_processamento, conjunto_cbo, subgrupo",
          "presente_na_resposta"),
        b(SIA_MUN, "SIA: lista de municipios do formulario", "a12", "2026-10-19", "TabNet", "municipio", "co_ibge", "-"),
        b(MANIF_SIA, "manifesto SIA (SHA-256 do painel)", "a12", "2026-10-19", "-", "-", "-", "saidas"),
        b(SIH, "SIH/SUS: K2", "DATASUS TabNet qibr.def (a13)", "processamento 202201-202607", "municipios do formulario",
          "municipio x mes x grupo", "co_ibge, competencia, grupo", "grupo == 04; aih_aprovadas, status, uf_mes_atipico"),
        b(MANIF_SIH, "manifesto SIH (SHA-256 do painel)", "a13", "2026-10-19", "-", "-", "-", "saidas.painel"),
        b(TISS, "TISS ambulatorial: K3, K3a, K5", "ANS dados abertos TISS (a14)", "realizacao 202201-202512",
          "municipios do IBGE", "municipio x mes x tipo x grupo CBO", "co_ibge, competencia_realizacao, tipo, grupo_cbo",
          "grupo_cbo == alvo_pmme; tipos consultas, exames, cirurgicos, agrupados_tuss63; qt_itens"),
        b(TISS_H, "TISS hospitalar: K3c", "ANS dados abertos TISS (a14)", "realizacao 202201-202512",
          "municipios do IBGE", "municipio x mes x tipo", "co_ibge, competencia_realizacao, tipo",
          "todos_cbo, cirurgicos; qt_itens e n_eventos"),
        b(VAL_TISS, "TISS: UF-meses sinalizados (alertas_queda)", "a14", "2026-10-19", "-", "UF x mes", "base, uf, mes",
          "alertas_queda"),
        b(MANIF_TISS, "manifesto TISS (SHA-256 dos paineis)", "a14", "2026-10-19", "-", "-", "-", "saidas"),
        b(CNES, "CNES: K4 (vinculos e horas nao SUS das CBO-alvo)", "CNES/DATASUS (a09)", "competencias < 202609",
          "universo a08", "municipio x mes x grupo", "co_ibge, competencia, grupo",
          "grupo == alvo_pmme; n_vinculos - n_vinculos_sus; horas_totais_amb_hosp - horas_sus_semanais"),
        b(MANIF_A09, "manifesto CNES (SHA-256 do painel)", "a09", "2026-10-19", "-", "-", "-", "painel.sha256"),
        b(A08, "running variable (IVS 2010 oficial) e universo U", "Ipea (a08)", "Censo 2010", "municipios", "municipio",
          "co_ibge", "co_ibge, ivs"),
        b(POP22, "denominador por 10 mil hab.", "IBGE Censo 2022", "2022", "municipios", "municipio", "co_ibge_6d",
          "populacao_2022"),
        b(ARQ_VM, "lista de V1 (quadro do ciclo 1)", "tarefa B (12)", "ciclo 1", "V1-V3", "municipio x ciclo",
          "ciclo, co_ibge", "ciclo == 1; nenhum outcome"),
        b(E7.A10_IED, "S3: porte e estrato IED", "Portaria 3.493/2024 (a10)", "2024", "municipios", "municipio", "co_ibge",
          "porte_codigo, estrato_ied, ivs_codigo_portaria"),
        b(E7.PPF_ZIP, "S4: Amazonia Legal / faixa de fronteira", "MS, PMMB consolidado", "2026-10-09", "MUNICIPAL",
          "municipio", "co_ibge", "amazonia_legal, faixa_fronteira (nenhuma vaga ou medico lido)"),
        b(PROTOCOLO_MD, "protocolo congelado (com adendos §10 e §11)", "doc 47", "2026-10-19", "-", "-", "-", "-"),
        b(E7.AUD18, "datas das politicas nos mesmos cortes", "auditoria 18", "2026-10-18", "-", "-", "-",
          "datas em E7.DATAS_POLITICAS"),
    ]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--atualizar-doc", action="store_true", help="so regrava as tabelas K do doc 50 a partir das saidas")
    args = ap.parse_args(argv)
    if args.atualizar_doc:
        atualizar_doc()
        return 0
    try:
        D = carregar_dados()
        sup = {"S3": E7.carregar_s3()}
        sup["S4"], info_s4 = E7.carregar_s4()
        linhas, linhas_ev, info, bases = [], [], {}, {}
        for spec in CATALOGO:
            for pop_nome in POPULACOES:
                ls, inf, d = estimar_outcome(spec, pop_nome, D, sup)
                linhas.extend(ls)
                info[f"{spec['id']}|{pop_nome}"] = inf
                bases[(spec["id"], pop_nome)] = d
                if pop_nome == "U" or spec["papel"] == "primaria":
                    linhas_ev.extend(estudo_evento(spec, pop_nome, D))
        est = aplicar_testes(pd.DataFrame(linhas)[COLUNAS_SAIDA])
        ev = pd.DataFrame(linhas_ev)[COLUNAS_EVENTO]
        if (ev["competencia"].astype(str) >= LIMITE_CNES).any():
            raise FalhaValidacao("estudo de evento com mes >= 202609")
    except FalhaValidacao as erro:
        print(f"FALHA DE VALIDACAO (nada gravado): {erro}", file=sys.stderr)
        return 2
    OUT.mkdir(parents=True, exist_ok=True)
    est.to_csv(OUT / NOME_EST, index=False)
    ev.to_csv(OUT / NOME_EVENTO, index=False)
    figuras = gerar_figuras(bases, est, ev, OUT / DIR_FIG)
    holm = est[est["entra_holm"].astype(bool)][["outcome_id", "tau", "ep", "ic95_inf", "ic95_sup", "p_valor", "p_holm",
                                                "ic_honesto_inf", "ic_honesto_sup", "mde", "efeito_relativo",
                                                "media_pre_abaixo", "n_abaixo", "n_acima", "unidade"]]
    resumo = {
        "natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "gerador": rotulo(Path(__file__)),
        "data_execucao": DATA_EXECUCAO,
        "protocolo": {"texto": rotulo(PROTOCOLO_MD), "sha256_texto": sha256(PROTOCOLO_MD),
                      "secoes": "§3, §4, §5 D1, §6, §7, adendos §10 e §11; protocolo 40 §5-§6 e §13"},
        "contraste": {"dird": CONTRASTE_DIRD, "nivel": CONTRASTE_NIVEL},
        "parametros": {"cortes_mil": list(CORTES), "h_mil": H, "h_sensibilidade_mil": list(H_SENS),
                       "fatores_M": list(FATORES_M), "fator_mde": FATOR_MDE, "pre": _rot(COMP_PRE),
                       "pos_K1_K2_SIA_SIH_CNES": _rot(POS_K1), "pos_sensibilidade_ate_202607": _rot(POS_ATE_202607),
                       "pos_TISS": _rot(POS_TISS), "pos_TISS_curto": _rot(POS_TISS_CURTO),
                       "pos_K4_sensibilidade": _rot(POS_CNES_E7), "placebo_a": _rot(PLACEBO_A),
                       "placebo_b": _rot(PLACEBO_B), "pre_extra": _rot(PRE_EXTRA),
                       "pre_extra_cnes": list(PRE_EXTRA_CNES), "referencia_evento": COMP_REF,
                       "escala": "por 10 mil habitantes (Censo 2022) por mes"},
        "datas_politicas": [{"data": d, "ato": r, "fonte": f, "marca_principal": p} for d, r, f, p in DATAS_POLITICAS],
        "outcomes": [{k: (list(v) if isinstance(v, tuple) else v) for k, v in c.items()} for c in CATALOGO],
        "primarias_holm": PRIMARIAS, "secundarias_bky": SECUNDARIAS,
        "especificacoes": ESPECIFICACOES,
        "entradas": entradas(),
        "arquivo_proibido_nao_lido": ARQUIVO_PROIBIDO,
        "validacoes": {**D.info, "s3_portes_muda": {str(k): sorted(v) for k, v in
                                                    (sup["S3"].get("portes_muda") or {}).items()},
                       "s4_info": info_s4},
        "amostras": info,
        "holm_K": holm.to_dict("records"),
        "desvios": DESVIOS,
        "contagens": {"linhas": int(len(est)), "linhas_no_protocolo": int(est["no_protocolo"].sum()),
                      "sem_estimativa": int((est["status"] == "SEM_ESTIMATIVA").sum()),
                      "nao_executado": int((est["status"] == "NAO_EXECUTADO").sum()),
                      "linhas_evento": int(len(ev))},
        "figuras": figuras,
        "saidas": [rotulo(OUT / NOME_EST), rotulo(OUT / NOME_EVENTO), rotulo(OUT / NOME_RESUMO)],
    }
    _gravar_json(OUT / NOME_RESUMO, resumo)
    atualizar_doc()
    print(f"K D1: {len(est)} linhas, {len(ev)} de estudo de evento; Holm: "
          + "; ".join(f"{r['outcome_id']} p={r['p_valor']:.3f} holm={r['p_holm']:.3f}" for r in holm.to_dict("records")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
