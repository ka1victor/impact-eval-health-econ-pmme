"""E7 do protocolo multi-outcome da bolsa: diferença em descontinuidades (DiRD) no CNES, família F3.

Protocolo congelado: `docs/06_execucao/40_protocolo_multioutcome_rdd_bolsa.md`
(§3, §4, §5 F3, §6 linha "painel CNES", §7 P2, §13 S1–S6, §16 horas SUS) e
`output/rdd_bolsa/protocolo_E6_multioutcome.json`. Painel: tarefa C
(`output/aquisicao/cnes_nacional/painel_municipio_cbo_mes.parquet`, auditoria
A09). Políticas nos mesmos cortes e suas datas: auditoria 18. Estimadores:
`scripts/rdd_bolsa/rdd_lib.py` (tarefa A). Este script não reimplementa
estimador: monta as amostras e chama a biblioteca.

Contraste
---------
Running variable: IVS 2010 oficial do Ipea (a08), em milésimos; cortes 300 e
400; T = 1[s > c]; salto = lado de bolsa maior menos lado de bolsa menor.
- **DiRD** (ΔY = média(pós) − média(pré)): anúncio de +R$ 5 mil na bolsa do
  PMM-E **mais a variação, entre pré e pós, das descontinuidades das outras
  políticas nos mesmos cortes** (auditoria 18, §3.1). Remove só a parte
  constante no tempo dessas políticas.
- **RDD em nível** (Y_pré, Y_pós separados): o **pacote do corte**.
Nenhum dos dois é efeito da participação no PMM-E nem do Agora Tem
Especialistas. Vínculo no CNES não é médico do PMM-E nem retenção individual.

Janelas (protocolo §6)
----------------------
pré 202406–202506; pós 202510–202608; referência do estudo de evento 202506;
placebo dentro do pré: média(202412–202505) − média(202406–202411); S5: pré
extra 202201–202303 (competências disponíveis). Nenhuma competência >= 202609
é lida.

Ordem de execução (falha fechada)
---------------------------------
1. Validação de esquema do painel, sem nada por lado de corte: SHA-256 igual ao
   manifesto a09, definição de `horas_sus_semanais` com o filtro
   TP_SUS_NAO_SUS (§16) e colunas de horas da sensibilidade presentes, chaves únicas, painel balanceado no universo a08, todas as
   competências do protocolo presentes e nenhuma >= 202609, coerência de
   contagens e da regra de horas ausentes. `--somente-validar` para aqui.
2. Populações (U = a08; V1 = quadro do ciclo 1, IVS conferido contra a08) e
   insumos de S3 (a10) e S4 (PMMB consolidado, só colunas de atribuição).
3. Seleção da janela de local randomization só com covariáveis (regra do E5;
   V1 tem de reproduzir `E5_lr_selecao_janela.csv`).
4. Outcomes e todas as especificações (lista em `especificacoes` do resumo);
   conferência de identidade DiRD-delta = DiRD-painel. Nada é escolhido depois
   de ver resultado.
5. q-valores BKY na família F3; p de P2 registrado para o Holm com P1 (E6).

Saídas em output/rdd_bolsa/
---------------------------
E7_estimativas.csv, E7_estudo_evento.csv, E7_resumo.json, E7_figuras/*.png.

Uso
---
    python3 scripts/rdd_bolsa/14_estimar_E7_dird_cnes.py --somente-validar
    python3 scripts/rdd_bolsa/14_estimar_E7_dird_cnes.py
    python3 scripts/rdd_bolsa/14_estimar_E7_dird_cnes.py --atualizar-doc

`--atualizar-doc` regrava, a partir das saídas, as tabelas entre marcadores de
`docs/06_execucao/43_resultados_E7_dird_cnes.md` (nenhum número é digitado no
doc). As funções puras são importáveis pelo teste sintético
(`tests/test_e7_dird.py`).
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import io
import json
import math
import re
import sys
import zipfile
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
L = _importar(DIR_RDD / "rdd_lib.py", "rdd_lib_e7")
sys.dont_write_bytecode = _bytecode

# ---------------------------------------------------------------------------
# Caminhos e parâmetros do protocolo (constantes permitidas: cortes, h, meses, datas de atos)
# ---------------------------------------------------------------------------

OUT = ROOT / "output" / "rdd_bolsa"
PAINEL = ROOT / "output" / "aquisicao" / "cnes_nacional" / "painel_municipio_cbo_mes.parquet"
MANIFESTO_A09 = ROOT / "output" / "aquisicao" / "a09_manifesto_cnes_nacional.json"
A08 = ROOT / "output" / "aquisicao" / "a08_ivs_2010_oficial_municipio.csv"
POP22 = ROOT / "output" / "aquisicao" / "populacao_censo2022_municipios.csv"
ARQ_VM = OUT / "outcomes" / "outcomes_V_municipio.parquet"
A10_IED = ROOT / "output" / "aquisicao" / "a10_ied_aps_2024_municipio.csv"
PPF_ZIP = ROOT / "data" / "raw" / "aquisicao" / "ivs_administrativo" / "ppf_mais_medicos_csv.zip"
TIPOLOGIA = ROOT / "output" / "tema_trabalho" / "matriz_tipologia_territorial.parquet"
E5_SEL = OUT / "E5_lr_selecao_janela.csv"
E6_SEL = OUT / "E6_lr_selecao_janela.csv"   # conferência opcional da janela LR de U (saída do E6, se existir)
PROTOCOLO_JSON = OUT / "protocolo_E6_multioutcome.json"
PROTOCOLO_MD = ROOT / "docs" / "06_execucao" / "40_protocolo_multioutcome_rdd_bolsa.md"
AUD18 = ROOT / "docs" / "auditorias" / "18_politicas_nos_mesmos_cortes_ivs.md"
AUD01 = ROOT / "docs" / "auditorias" / "01_regra_institucional.md"
DOC43 = ROOT / "docs" / "06_execucao" / "43_resultados_E7_dird_cnes.md"
ARQUIVO_PROIBIDO = "data/ivs_ipea_2010_municipios.csv"   # auditoria 16: nunca lido

NOME_EST = "E7_estimativas.csv"
NOME_EVENTO = "E7_estudo_evento.csv"
NOME_RESUMO = "E7_resumo.json"
DIR_FIG = "E7_figuras"

DATA_EXECUCAO = "2026-10-19"
CORTES = L.CORTES_MIL                     # (300, 400)
H = L.H_PRINCIPAL_MIL                     # 50
H_SENS = L.H_SENSIBILIDADE_MIL            # (30, 80)
FATORES_M = (0.5, 1.0, 2.0)
EMPILHADO = "empilhado"
ROTULO_CORTE = {300: "0.300", 400: "0.400", EMPILHADO: EMPILHADO}
ID_SEMENTE_POP = {"V1": 1, "U": 4}        # iguais aos do E5/E6 (seleção da janela LR)
ADICIONAL = "ESPECIFICACAO_ADICIONAL_AO_PROTOCOLO"
ESCALA_HAB = 1e4                          # por 10 mil habitantes (protocolo §5)


def _meses(ini: str, fim: str) -> tuple[str, ...]:
    a, m = int(ini[:4]), int(ini[4:])
    out = []
    while f"{a}{m:02d}" <= fim:
        out.append(f"{a}{m:02d}")
        a, m = (a + 1, 1) if m == 12 else (a, m + 1)
    return tuple(out)


COMP_PRE = _meses("202406", "202506")
COMP_POS = _meses("202510", "202608")
COMP_REF = "202506"
COMP_PLACEBO_A = _meses("202406", "202411")
COMP_PLACEBO_B = _meses("202412", "202505")
# Pré extra do S5: competências disponíveis de 2022-01 a 2023-03 (trimestrais + 202302 e 202303, a09).
COMP_PRE_EXTRA = ("202201", "202204", "202207", "202210", "202301", "202302", "202303")
COMP_ENTRE = ("202304", "202307", "202310", "202401", "202404")
COMP_TRANSICAO = _meses("202507", "202509")
COMP_EVENTO = tuple(sorted(COMP_PRE_EXTRA + COMP_ENTRE + COMP_PRE + COMP_TRANSICAO + COMP_POS))
LIMITE_CICLO3 = "202609"

# Datas de atos (auditoria 18 e auditoria 01 §7): marcas verticais do estudo de evento.
DATAS_POLITICAS = [
    # (data, rótulo, fonte, principal)
    ("2023-06-19", "Portaria 752/2023 (teto PMMB)", "auditoria 18 §2.1 (DOU 19/06/2023)", True),
    ("2024-05-01", "Portaria 3.493/2024 (IED, parcela 05/2024)", "auditoria 18 §2.5 (art. 8º)", True),
    ("2025-07-24", "PMM-E ciclo 1: quadro de vagas", "auditoria 18 §1; auditoria 01 §7 (Edital 3/2025)", True),
    ("2025-09-11", "PMM-E ciclo 1: início", "auditoria 01 §7 (homologação/início 11–18/09/2025)", True),
    ("2026-02-03", "PMM-E ciclo 2: edital e vagas", "auditoria 01 §7 (Edital 3/2026)", True),
    ("2026-03-25", "PMM-E ciclo 2: início", "auditoria 01 §7 (25/03–08/04/2026)", True),
    ("2023-04-18", "Portaria 485/2023", "auditoria 18 §2.2", False),
    ("2023-05-18", "PI 604/2023 (ajuda de custo)", "auditoria 18 §2.3", False),
    ("2023-05-22", "Portaria 635/2023 (eMulti)", "auditoria 18 §2.7", False),
    ("2024-03-08", "Portaria 3.283/2024 (emendas +20% IVS > 0,3)", "auditoria 18 §2.6", False),
    ("2024-11-18", "Portaria 5.721/2024 (nutrição)", "auditoria 18 §2.7", False),
    ("2025-04-16", "Portaria 6.870/2025 (emendas 2025)", "auditoria 18 §2.6", False),
    ("2025-12-09", "Portaria 9.177/2025 (Eixo Vínculo)", "auditoria 18 §2.7", False),
    ("2026-01-20", "Portaria 10.169/2026 (parcelas ATE)", "auditoria 18 §2.6", False),
]

# Classes de porte onde o estrato IED da APS muda no corte (protocolo §13, auditoria 18 §2.5);
# o script recalcula a partir do a10 e para se divergir.
PORTES_MUDA_PROTOCOLO = {300: {2, 3}, 400: {1, 2, 4}}
ESTRATO_IED_CODIGO = {300: (4, 3), 400: (3, 2)}   # código IVS da Portaria abaixo e acima do corte

CONTRASTE_DIRD = (
    "DiRD: anúncio de +R$ 5 mil por mês na bolsa (0,300: R$ 10 mil -> 15 mil; 0,400: R$ 15 mil -> 20 mil) mais a "
    "variação, entre pré (202406-202506) e pós (202510-202608), das descontinuidades das outras políticas nos mesmos "
    "cortes (auditoria 18, §3.1); remove só a parte constante no tempo delas; não é efeito da participação no PMM-E "
    "nem do Agora Tem Especialistas")
CONTRASTE_NIVEL = ("RDD em nível: pacote do corte (bolsa anunciada + todas as outras regras federais nos mesmos "
                   "cortes, auditoria 18)")

# Horas no CNES (protocolo §16, 19/10/2026). Principal: `horas_sus_semanais` = horas ambulatoriais +
# hospitalares dos vínculos com TP_SUS_NAO_SUS == 'S'; célula com hora em branco fica ausente. Sensibilidades
# rotuladas: a soma sem o filtro TP_SUS_NAO_SUS e a soma parcial das horas observadas (com a contagem de
# vínculos em branco ao lado). Nomes das colunas do painel auditado da tarefa C (definições no manifesto a09);
# coluna ausente faz a validação falhar (nada é substituído). O §16 diz que a soma sem filtro "continua como
# horas_totais", mas no painel `horas_totais` é o total dos três campos; a soma ambulatorial + hospitalar sem
# filtro é `horas_totais_amb_hosp` (nota de nomenclatura em DESVIOS).
COL_HORAS_SUS = "horas_sus_semanais"
COL_HORAS_SEM_FILTRO = "horas_totais_amb_hosp"
COL_HORAS_PARCIAL = "horas_sus_semanais_parcial"
COLS_HORAS_SENSIBILIDADE = (COL_HORAS_SEM_FILTRO, COL_HORAS_PARCIAL)
TERMO_FILTRO_SUS = "TP_SUS_NAO_SUS"
ROTULO_SENS_HORAS = "SENSIBILIDADE_PROTOCOLO_§16"

UNIDADES = {
    "taxa": "vinculos por 10 mil hab. (Censo 2022)",
    "horas": "horas SUS semanais por 10 mil hab. (Censo 2022)",
    "binario": "fracao (x100 = p.p.)",
}

# ---------------------------------------------------------------------------
# Catálogo de outcomes (protocolo §5 F3 e §13 S6) — fixado antes de ler outcomes
# ---------------------------------------------------------------------------

CATALOGO: list[dict] = [
    {"id": "F3.1", "grupo": "alvo_pmme", "col": "n_vinculos", "tipo": "taxa", "pops": ("U", "V1"), "bky": True,
     "papel": "efeito (P2 = U, cortes empilhados)",
     "desc": "vínculos nas CBO-alvo do PMM-E por 10 mil hab."},
    {"id": "F3.2", "grupo": "alvo_pmme", "col": "tem_profissional", "tipo": "binario", "pops": ("U",), "bky": True,
     "papel": "efeito (cobertura)", "desc": "município com >= 1 profissional nas CBO-alvo"},
    {"id": "F3.3", "grupo": "alvo_pmme", "col": COL_HORAS_SUS, "tipo": "horas", "pops": ("U",), "bky": True,
     "papel": "efeito (horas)",
     "desc": "horas SUS semanais (vínculos TP_SUS_NAO_SUS = 'S') nas CBO-alvo por 10 mil hab."},
    {"id": "F3.3.sem_filtro_sus", "grupo": "alvo_pmme", "col": COL_HORAS_SEM_FILTRO, "tipo": "horas", "pops": ("U",),
     "bky": False, "figura": False, "rotulo": f"{ROTULO_SENS_HORAS} (horas sem o filtro TP_SUS_NAO_SUS)",
     "papel": "sensibilidade rotulada do F3.3 (§16; fora do BKY)",
     "desc": "horas ambulatoriais + hospitalares SUS sem o filtro TP_SUS_NAO_SUS, nas CBO-alvo, por 10 mil hab."},
    {"id": "F3.3.soma_parcial", "grupo": "alvo_pmme", "col": COL_HORAS_PARCIAL, "tipo": "horas", "pops": ("U",),
     "bky": False, "figura": False, "horas_parcial": True,
     "rotulo": f"{ROTULO_SENS_HORAS} (soma parcial das horas observadas; vinculos em branco contados)",
     "papel": "sensibilidade rotulada do F3.3 (§16; fora do BKY)",
     "desc": "horas SUS (TP_SUS_NAO_SUS = 'S') com soma parcial das horas observadas, nas CBO-alvo, por 10 mil hab."},
    {"id": "F3.P1", "grupo": "generalistas", "col": "n_vinculos", "tipo": "taxa", "pops": ("U",), "bky": True,
     "papel": "placebo/confundidor (Portaria 752, IED)",
     "desc": "vínculos de generalistas (225125, 225142, 225170) por 10 mil hab."},
    {"id": "F3.P2", "grupo": "especialistas_nao_alvo", "col": "n_vinculos", "tipo": "taxa", "pops": ("U",),
     "bky": True, "papel": "placebo", "desc": "vínculos de especialistas fora das CBO-alvo por 10 mil hab."},
    {"id": "S6", "grupo": "mfc_225130", "col": "n_vinculos", "tipo": "taxa", "pops": ("U",), "bky": False,
     "papel": "placebo suplementar (§13 S6; fora do BKY)",
     "desc": "vínculos de médico de família e comunidade (225130) por 10 mil hab."},
]
GRUPOS_USADOS = sorted({c["grupo"] for c in CATALOGO})
COLUNAS_PAINEL = ["co_ibge", "competencia", "grupo", "n_vinculos", "n_profissionais_distintos",
                  COL_HORAS_SUS, *COLS_HORAS_SENSIBILIDADE, "n_vinculos_horas_ausentes", "tem_profissional",
                  "natureza_dos_dados"]

# Especificações (protocolo §6 e §13; adições rotuladas).
ESPECIFICACOES = {
    "principal": "DiRD: RDD local linear triangular h = 0,050 sobre delta = media(pos) - media(pre); HC1 por corte, "
                 "CR1 por municipio no empilhado",
    "sensibilidade_h": "idem com h = 0,030 e 0,080",
    "ic_honesto": "IC com viés limitado (Armstrong-Kolesar, classe de Taylor), M da regra de bolso com suporte ate o "
                  "ponto medio entre cortes, fatores 0,5; 1; 2; h = 0,050",
    "ic_honesto_h_otimo": f"{ADICIONAL}: h que minimiza o IC honesto (rdd_lib.ROTULO_H_OTIMO)",
    "pos_com_pre_covariavel": "alternativa do protocolo §6: RDD de media(pos) com media(pre) como covariavel",
    "local_randomization": "protocolo §6: diferenca de medias de delta na janela do E5 (so covariaveis), Fisher",
    "dird_painel": f"{ADICIONAL} (conferencia): rd_dird_painel em linhas municipio x mes, CR1; ponto identico ao "
                   "principal",
    "placebo_pre": "protocolo §6: delta = media(202412-202505) - media(202406-202411)",
    "nivel_pre": f"{ADICIONAL} (pedido do coordenador antes de estimar): RDD em nivel de media(pre) = pacote",
    "nivel_pos": f"{ADICIONAL} (pedido do coordenador antes de estimar): RDD em nivel de media(pos) = pacote",
    "nivel_pre_extra": f"{ADICIONAL} (pedido do coordenador antes de estimar): RDD em nivel de media(pre extra)",
    "S5_pre_menos_pre_extra": "§13 S5: delta = media(pre) - media(pre extra 202201-202303); a descontinuidade "
                              "mudou antes do PMM-E?",
    "S5_dird_pre_extra": "§13 S5 / auditoria 18 §5.7: DiRD com pre = pre extra (delta = media(pos) - media(pre "
                         "extra))",
    "S2_donut": "§13 S2: principal sem IVS == 0,300 e == 0,400",
    "S3_porte_muda": "§13 S3: principal nos portes em que o estrato IED muda no corte",
    "S3_porte_nao_muda": "§13 S3: principal nos portes em que o estrato IED nao muda",
    "S3_diferenca": "§13 S3: diferenca dos dois saltos (subamostras disjuntas)",
    "S4_dentro": "§13 S4 (0,400): principal dentro da Amazonia Legal ou faixa de fronteira",
    "S4_fora": "§13 S4 (0,400): principal fora",
    "S4_diferenca": "§13 S4: diferenca dos dois saltos (subamostras disjuntas)",
    "estudo_evento": "§6/§13 S5: RDD de (Y_t - Y_202506) em cada competencia (E7_estudo_evento.csv)",
}
NO_PROTOCOLO = {k: not v.startswith(ADICIONAL) for k, v in ESPECIFICACOES.items()}

DESVIOS = [
    {"data": DATA_EXECUCAO, "tipo": "desvio",
     "item": "Poisson local (protocolo §6, contagens por habitante)",
     "descricao": "nao estimado na F3. O estimando da DiRD e uma diferenca de medias de taxas por municipio; um "
                  "analogo em log exigiria um modelo de painel (Poisson com efeito de periodo e interacao) que o "
                  "protocolo nao especifica, e o coordenador o deixou opcional. Nada foi estimado e descartado."},
    {"data": DATA_EXECUCAO, "tipo": "regra_de_dado",
     "item": "F3.3 horas (protocolo §16)",
     "descricao": "principal: horas_sus_semanais = horas ambulatoriais + hospitalares dos vinculos com "
                  "TP_SUS_NAO_SUS = 'S'; celula com hora em branco fica ausente, nunca zero; o municipio sem todos "
                  "os meses de uma janela sai daquele outcome naquela especificacao (diferenca_pos_pre com "
                  "exigir_completo=True); no estudo de evento sai so dos meses afetados. Sensibilidades rotuladas "
                  "(fora do BKY): F3.3.sem_filtro_sus (sem o filtro TP_SUS_NAO_SUS) e F3.3.soma_parcial (soma das "
                  "horas observadas, com a contagem de vinculos em branco na nota e em validacoes.horas_ausentes). "
                  "O grupo todos_medicos_sem_residentes do painel nao e outcome do E7 (§16: nao primario; F3 nao "
                  "o lista)."},
    {"data": DATA_EXECUCAO, "tipo": "nota_de_nomenclatura",
     "item": "coluna da sensibilidade 'horas sem filtro SUS' (§16)",
     "descricao": "o texto do §16 diz que a soma sem o filtro TP_SUS_NAO_SUS 'continua no painel como "
                  "horas_totais'; no painel auditado da tarefa C, horas_totais e a soma dos tres campos "
                  "(ambulatorial + hospitalar + outros) e a soma ambulatorial + hospitalar sem filtro chama-se "
                  "horas_totais_amb_hosp (definicao no manifesto a09). O E7 usa horas_totais_amb_hosp em "
                  "F3.3.sem_filtro_sus. Mapeamento de nome, sem mudanca de substancia."},
    {"data": DATA_EXECUCAO, "tipo": "esclarecimento",
     "item": "populacoes",
     "descricao": "protocolo §5: F3.1 em U e V1; F3.2, F3.3, F3.P1, F3.P2 e S6 em U. V1 = municipios do quadro "
                  "do ciclo 1 (outcomes_V_municipio, ciclo 1). Nenhuma outra populacao foi estimada."},
    {"data": DATA_EXECUCAO, "tipo": "esclarecimento",
     "item": "S5",
     "descricao": "duas formas, ambas fixadas antes de estimar: (a) media(pre) - media(pre extra), teste de que a "
                  "descontinuidade se moveu antes do PMM-E; (b) DiRD com pre extra (auditoria 18, recomendacao 7). "
                  "O pre extra contem as Portarias 377/2022 e 1.054/2022 (IVS em indice composto; auditoria 18 §3.2)."},
    {"data": DATA_EXECUCAO, "tipo": "adicao",
     "item": "RDD em nivel e conferencia painel",
     "descricao": "nivel_pre, nivel_pos e nivel_pre_extra (pacote do corte) e dird_painel (identidade com o "
                  "principal) sao adicoes rotuladas ESPECIFICACAO_ADICIONAL_AO_PROTOCOLO, pedidas antes de estimar."},
    {"data": DATA_EXECUCAO, "tipo": "esclarecimento",
     "item": "datas do estudo de evento",
     "descricao": "datas do ciclo 2 do PMM-E vem da auditoria 01 §7 (cronologia auditada), nao da auditoria 18. "
                  "Estudo de evento empilhado: rd_empilhado em cada competencia (CR1 por municipio)."},
    {"data": DATA_EXECUCAO, "tipo": "esclarecimento",
     "item": "S3 e S4",
     "descricao": "porte = classe do Anexo VI da Portaria 3.493/2024 (a10), portes em que o estrato muda "
                  "recalculados do a10 e conferidos com o protocolo §13; S4 = Amazonia Legal OU faixa de fronteira "
                  "do PMMB consolidado (mesmo atributo e mesma regra do E6; areas indigenas sem atributo municipal "
                  "no repositorio). So corte a corte (S3) e so 0,400 (S4)."},
]


class FalhaValidacao(RuntimeError):
    """Validação obrigatória falhou: o script para sem gravar estimativas."""


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


def s_mil_de_ivs(ivs: pd.Series) -> pd.Series:
    """IVS em [0, 1] com três casas -> milésimos inteiros; ausente fica NaN (não vira zero)."""
    v = pd.to_numeric(ivs, errors="raise").astype(float)
    mil = v * 1000.0
    ok = v.notna()
    if (np.abs(mil[ok] - np.round(mil[ok])) > 1e-6).any():
        raise FalhaValidacao("IVS com mais de três casas decimais")
    return pd.Series(np.where(ok, np.round(mil), np.nan), index=ivs.index)


def _ibge6(serie: pd.Series) -> pd.Series:
    out = serie.astype(str).str.split(".").str[0].str.replace(r"\D", "", regex=True).str[:6].str.zfill(6)
    if (out.str.len() != 6).any():
        raise FalhaValidacao("codigo IBGE fora do formato de 6 digitos")
    return out


def _nan_none(obj):
    if isinstance(obj, dict):
        return {str(k): _nan_none(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [_nan_none(v) for v in (sorted(obj) if isinstance(obj, set) else obj)]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating, float)):
        return None if not math.isfinite(float(obj)) else float(obj)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    return obj


def _gravar_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(_nan_none(obj), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def bloco_entrada(path: Path, papel: str, fonte: str, data_ref: str, cobertura: str, unidade: str,
                  chaves: str, filtros: str) -> dict:
    return {"caminho": rotulo(path), "sha256": sha256(path), "bytes": Path(path).stat().st_size, "papel": papel,
            "fonte": fonte, "data_referencia": data_ref, "cobertura": cobertura, "unidade": unidade,
            "chaves": chaves, "filtros": filtros}


def _juntar(*notas) -> str:
    return "; ".join(str(n) for n in notas if n)


# ---------------------------------------------------------------------------
# 1. Validação de esquema do painel (nada por lado de corte)
# ---------------------------------------------------------------------------

def validar_painel(painel: pd.DataFrame, universo: set[str], *, competencias_esperadas=COMP_EVENTO,
                   grupos=GRUPOS_USADOS) -> dict:
    """Validações de esquema e coerência do painel a09. Levanta FalhaValidacao; devolve contagens agregadas.

    Nada aqui separa municípios por IVS, faixa ou lado de corte.
    """
    falta = set(COLUNAS_PAINEL) - set(painel.columns)
    if falta:
        raise FalhaValidacao(f"painel sem colunas {sorted(falta)}")
    rot = set(painel["natureza_dos_dados"].astype(str).str.upper().unique())
    if rot != {"EMPIRICO"}:
        raise FalhaValidacao(f"painel com natureza_dos_dados {sorted(rot)}")
    if painel.duplicated(["co_ibge", "competencia", "grupo"]).any():
        raise FalhaValidacao("painel com chave (co_ibge, competencia, grupo) repetida")
    comps = set(painel["competencia"].astype(str).unique())
    proibidas = sorted(c for c in comps if c >= LIMITE_CICLO3)
    if proibidas:
        raise FalhaValidacao(f"painel com competencias >= {LIMITE_CICLO3}: {proibidas}")
    faltam = sorted(set(competencias_esperadas) - comps)
    if faltam:
        raise FalhaValidacao(f"competencias do protocolo ausentes do painel: {faltam}")
    extras = sorted(comps - set(competencias_esperadas))
    faltam_g = sorted(set(grupos) - set(painel["grupo"].unique()))
    if faltam_g:
        raise FalhaValidacao(f"grupos ausentes do painel: {faltam_g}")
    sub = painel[painel["grupo"].isin(grupos)]
    munis = set(sub["co_ibge"].unique())
    if munis != set(universo):
        raise FalhaValidacao(f"municipios do painel != universo a08 ({len(munis - set(universo))} a mais, "
                             f"{len(set(universo) - munis)} a menos)")
    cont = sub.groupby(["competencia", "grupo"]).size()
    if (cont != len(universo)).any():
        raise FalhaValidacao("painel desbalanceado: (competencia, grupo) sem todos os municipios do universo")
    for c in ("n_vinculos", "n_profissionais_distintos", "tem_profissional", "n_vinculos_horas_ausentes"):
        if sub[c].isna().any():
            raise FalhaValidacao(f"{c} com valores ausentes")
    if (sub["n_vinculos"] < 0).any() or (sub["n_profissionais_distintos"] < 0).any():
        raise FalhaValidacao("contagens negativas no painel")
    if not sub["tem_profissional"].isin([0, 1]).all():
        raise FalhaValidacao("tem_profissional fora de {0, 1}")
    if ((sub["tem_profissional"] == 1) != (sub["n_profissionais_distintos"] > 0)).any():
        raise FalhaValidacao("tem_profissional incoerente com n_profissionais_distintos")
    # Horas (a09 e protocolo §16): principal e "sem filtro" ficam ausentes se algum vínculo da célula tem hora
    # em branco (n_vinculos_horas_ausentes > 0 é condição necessária); a soma parcial nunca é ausente e coincide
    # com o principal onde ele existe; célula sem vínculo tem horas 0 (observado).
    for c in (COL_HORAS_SUS, COL_HORAS_SEM_FILTRO):
        if (sub[c].isna() & (sub["n_vinculos_horas_ausentes"] == 0)).any():
            raise FalhaValidacao(f"{c} ausente sem vinculo com horas em branco (regra a09)")
    if sub[COL_HORAS_PARCIAL].isna().any():
        raise FalhaValidacao(f"{COL_HORAS_PARCIAL} com valores ausentes (a soma parcial deveria existir sempre)")
    ok_sus = sub[COL_HORAS_SUS].notna()
    if (sub.loc[ok_sus, COL_HORAS_PARCIAL].astype(float) != sub.loc[ok_sus, COL_HORAS_SUS].astype(float)).any():
        raise FalhaValidacao(f"{COL_HORAS_PARCIAL} difere de {COL_HORAS_SUS} em celula sem hora em branco")
    sem_vinc = sub["n_vinculos"] == 0
    for c in (COL_HORAS_SUS, *COLS_HORAS_SENSIBILIDADE):
        if (sub.loc[sem_vinc, c].astype(float).fillna(-1) != 0).any():
            raise FalhaValidacao(f"celula sem vinculo com {c} diferente de 0 (regra a09)")
        if (sub[c].dropna().astype(float) < 0).any():
            raise FalhaValidacao(f"{c} negativa")
    horas_nulas = sub[COL_HORAS_SUS].isna()
    nulas = (sub[horas_nulas].groupby(["grupo", "competencia"]).size().unstack(fill_value=0)
             if horas_nulas.any() else pd.DataFrame())
    branco = sub[sub["n_vinculos_horas_ausentes"] > 0].groupby(["grupo", "competencia"])[
        "n_vinculos_horas_ausentes"].sum().unstack(fill_value=0) if (sub["n_vinculos_horas_ausentes"] > 0).any() \
        else pd.DataFrame()
    return {
        "linhas_grupos_usados": int(len(sub)),
        "municipios": len(munis),
        "competencias": sorted(comps),
        "competencias_fora_do_protocolo": extras,
        "grupos": list(grupos),
        "chave_unica": True,
        "balanceado": True,
        "celulas_horas_sus_ausentes_por_grupo_e_competencia": {g: {c: int(v) for c, v in r.items() if v}
                                                              for g, r in nulas.iterrows()} if len(nulas) else {},
        "vinculos_horas_em_branco_por_grupo_e_competencia": {g: {c: int(v) for c, v in r.items() if v}
                                                            for g, r in branco.iterrows()} if len(branco) else {},
        "colunas_horas": {"principal": COL_HORAS_SUS, "sensibilidades": list(COLS_HORAS_SENSIBILIDADE)},
    }


def validar_manifesto(manifesto: dict, sha_painel: str) -> dict:
    p = manifesto.get("painel", {})
    if p.get("sha256") != sha_painel:
        raise FalhaValidacao("SHA-256 do painel difere do manifesto a09")
    if manifesto.get("competencias_nao_obtidas"):
        raise FalhaValidacao(f"manifesto a09 com competencias nao obtidas: {manifesto['competencias_nao_obtidas']}")
    if str(manifesto.get("natureza_dos_dados", "")).upper() != "EMPIRICO":
        raise FalhaValidacao("manifesto a09 sem natureza EMPIRICO")
    definicao = str((manifesto.get("definicoes") or {}).get(COL_HORAS_SUS, ""))
    if TERMO_FILTRO_SUS not in definicao or "sem filtro de TP_SUS_NAO_SUS" in definicao:
        raise FalhaValidacao(f"manifesto a09: {COL_HORAS_SUS} nao e definido com o filtro {TERMO_FILTRO_SUS} "
                             f"(protocolo §16); definicao lida: {definicao[:200]!r}")
    return {"sha256_painel_igual_manifesto": True, "competencias_nao_obtidas": [],
            "data_execucao_a09": manifesto.get("data_execucao"),
            "definicao_horas_sus_no_manifesto": definicao}


# ---------------------------------------------------------------------------
# 2. Populações e atributos (só chaves e atribuição)
# ---------------------------------------------------------------------------

def ler_running_variable() -> pd.DataFrame:
    a08 = pd.read_csv(A08, dtype={"co_ibge": str})
    a08["co_ibge"] = _ibge6(a08["co_ibge"])
    if a08["co_ibge"].duplicated().any():
        raise FalhaValidacao("a08 com municipio duplicado")
    a08["s_mil"] = s_mil_de_ivs(a08["ivs"])
    if a08["s_mil"].isna().any():
        raise FalhaValidacao("a08 com IVS ausente")
    return a08[["co_ibge", "s_mil"]].reset_index(drop=True)


def ler_populacao() -> pd.DataFrame:
    p = pd.read_csv(POP22, dtype={"co_ibge_6d": str})
    p["co_ibge"] = _ibge6(p["co_ibge_6d"])
    if p["co_ibge"].duplicated().any():
        raise FalhaValidacao("Censo 2022 com municipio duplicado")
    p["populacao_2022"] = pd.to_numeric(p["populacao_2022"], errors="raise").astype(float)
    return p[["co_ibge", "populacao_2022"]]


def populacoes(rv: pd.DataFrame, pop: pd.DataFrame) -> tuple[dict[str, pd.DataFrame], dict]:
    """U = universo a08; V1 = municípios do quadro do ciclo 1 (IVS conferido contra a08)."""
    base = rv.merge(pop, on="co_ibge", how="left", validate="one_to_one")
    sem_pop = base.loc[~(base["populacao_2022"] > 0), "co_ibge"].tolist()
    conf = {"U_municipios": int(len(base)), "U_sem_populacao_2022": sem_pop,
            "nota_sem_populacao": "municipio sem populacao 2022 > 0 fica com taxa ausente (fora dos outcomes por "
                                  "10 mil hab.), nunca zero"}
    vm = pd.read_parquet(ARQ_VM, columns=["ciclo", "co_ibge", "ivs_2010_oficial"])
    v1 = vm[vm["ciclo"] == 1].copy()
    v1["co_ibge"] = _ibge6(v1["co_ibge"])
    if v1["co_ibge"].duplicated().any():
        raise FalhaValidacao("V1 com municipio duplicado")
    s_b = s_mil_de_ivs(v1["ivs_2010_oficial"])
    s_a = v1["co_ibge"].map(rv.set_index("co_ibge")["s_mil"])
    sem_ivs = v1.loc[s_b.isna(), "co_ibge"].tolist()
    if int(((s_a - s_b).abs() > 0)[s_b.notna()].sum()) or s_a[s_b.notna()].isna().any():
        raise FalhaValidacao("V1: IVS da tarefa B difere do a08")
    v1 = v1[s_b.notna()]
    conf.update({"V1_municipios": int(len(v1)), "V1_sem_ivs_oficial_fora": sem_ivs, "V1_ivs_igual_a08": True})
    pops = {"U": base.reset_index(drop=True),
            "V1": base[base["co_ibge"].isin(set(v1["co_ibge"]))].reset_index(drop=True)}
    return pops, conf


def carregar_s3() -> dict:
    """Porte da Portaria 3.493/2024 (a10) e portes em que o estrato IED muda em cada corte, lidos do a10."""
    if not A10_IED.exists():
        return {"tabela": None, "motivo": f"{rotulo(A10_IED)} ausente"}
    a10 = pd.read_csv(A10_IED, dtype={"co_ibge": str})
    return s3_de_tabela(a10)


def s3_de_tabela(a10: pd.DataFrame) -> dict:
    falta = {"co_ibge", "porte_codigo", "estrato_ied", "ivs_codigo_portaria"} - set(a10.columns)
    if falta:
        return {"tabela": None, "motivo": f"a10 sem colunas {sorted(falta)}"}
    a10 = a10.copy()
    a10["co_ibge"] = _ibge6(a10["co_ibge"])
    if a10["co_ibge"].duplicated().any():
        raise FalhaValidacao("a10 com municipio duplicado")
    mapa = a10.groupby(["ivs_codigo_portaria", "porte_codigo"])["estrato_ied"].agg(lambda v: sorted(set(v)))
    if (mapa.map(len) != 1).any():
        raise FalhaValidacao("a10: estrato IED nao e funcao de (codigo IVS, porte)")
    mapa = mapa.map(lambda v: v[0])
    portes_muda = {}
    for corte, (cod_ab, cod_ac) in ESTRATO_IED_CODIGO.items():
        portes_muda[corte] = {int(p) for p in sorted(a10["porte_codigo"].unique())
                              if mapa.get((cod_ab, p)) != mapa.get((cod_ac, p))}
        if portes_muda[corte] != PORTES_MUDA_PROTOCOLO[corte]:
            raise FalhaValidacao(f"a10: portes onde o estrato muda em {corte} = {portes_muda[corte]}, protocolo §13 "
                                 f"diz {PORTES_MUDA_PROTOCOLO[corte]}")
    return {"tabela": a10.set_index("co_ibge")["porte_codigo"].astype(int), "portes_muda": portes_muda,
            "definicao": "classe de porte do Anexo VI da Portaria 3.493/2024 (a10); muda = estrato IED diferente "
                         "dos dois lados do corte para aquele porte"}


def carregar_s4() -> tuple[dict, dict]:
    """Amazônia Legal / faixa de fronteira do PMMB consolidado (MS, 09/10/2026): só colunas de atribuição."""
    with zipfile.ZipFile(PPF_ZIP) as z:
        nomes = z.namelist()
        if len(nomes) != 1:
            raise FalhaValidacao(f"zip do PMMB com {len(nomes)} membros")
        bruto = z.read(nomes[0])
    df = pd.read_csv(io.BytesIO(bruto), sep=";", dtype=str, encoding="latin1",
                     usecols=["nivel", "co_ibge", "amazonia_legal", "faixa_fronteira", "dt_referencia"])
    df = df[df["nivel"] == "MUNICIPAL"].copy()
    df["co_ibge"] = _ibge6(df["co_ibge"])
    if df["co_ibge"].duplicated().any():
        raise FalhaValidacao("PMMB: municipio duplicado no nivel MUNICIPAL")
    info = {"membro_zip": nomes[0], "dt_referencia": sorted(df["dt_referencia"].dropna().unique().tolist()),
            "colunas_lidas": ["nivel", "co_ibge", "amazonia_legal", "faixa_fronteira", "dt_referencia"]}
    return s4_de_tabela(df), info


def s4_de_tabela(pmmb: pd.DataFrame) -> dict:
    falta = {"amazonia_legal", "faixa_fronteira", "co_ibge"} - set(pmmb.columns)
    if falta:
        return {"tabela": None, "motivo": f"PMMB consolidado sem colunas {sorted(falta)}"}
    am = pmmb["amazonia_legal"].map({"Amazonia Legal": 1.0, "Fora da Amazonia Legal": 0.0})
    ff = pmmb["faixa_fronteira"].map({"Faixa de Fronteira": 1.0, "Fora da Faixa de Fronteira": 0.0})
    nao_mapeados = int((pmmb["amazonia_legal"].notna() & am.isna()).sum()
                       + (pmmb["faixa_fronteira"].notna() & ff.isna()).sum())
    if nao_mapeados:
        raise FalhaValidacao(f"PMMB: {nao_mapeados} valores de amazonia_legal/faixa_fronteira fora do dicionario")
    flag = np.where(am.isna() | ff.isna(), np.nan, np.maximum(am.fillna(0), ff.fillna(0)))
    return {"tabela": pd.Series(flag, index=pmmb["co_ibge"].to_numpy()).dropna(),
            "definicao": "dentro = Amazonia Legal OU faixa de fronteira (atributo municipal do PMMB consolidado, MS); "
                         "areas indigenas, que a PI 604 tambem poe na Faixa 1, nao entram (sem atributo municipal)"}


# ---------------------------------------------------------------------------
# 3. Outcomes e janelas
# ---------------------------------------------------------------------------

def serie_outcome(painel: pd.DataFrame, spec: dict, pop: pd.DataFrame) -> pd.DataFrame:
    """Linhas município x competência com y do outcome; ausência continua ausente (nunca vira zero).

    `pop` tem co_ibge, s_mil e populacao_2022. Taxas: valor / população 2022 x 10 mil; sem população > 0, NaN.
    """
    sub = painel.loc[painel["grupo"] == spec["grupo"], ["co_ibge", "competencia", spec["col"]]]
    sub = sub[sub["co_ibge"].isin(set(pop["co_ibge"]))]
    v = pd.to_numeric(sub[spec["col"]], errors="coerce").astype(float)   # Int32 <NA> -> NaN
    out = sub[["co_ibge", "competencia"]].copy()
    if spec["tipo"] in ("taxa", "horas"):
        p = sub["co_ibge"].map(pop.set_index("co_ibge")["populacao_2022"]).astype(float)
        out["y"] = np.where(p > 0, v / p * ESCALA_HAB, np.nan)
    else:
        out["y"] = v
    out["s_mil"] = out["co_ibge"].map(pop.set_index("co_ibge")["s_mil"]).astype(float)
    return out.reset_index(drop=True)


def janelas(serie: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Por município: médias das janelas do protocolo e deltas; ausência num mês da janela -> média ausente."""
    kw = {"col_unidade": "co_ibge", "col_periodo": "competencia", "col_y": "y", "exigir_completo": True}
    a = L.diferenca_pos_pre(serie, periodos_pre=COMP_PRE, periodos_pos=COMP_POS, **kw)
    b = L.diferenca_pos_pre(serie, periodos_pre=COMP_PLACEBO_A, periodos_pos=COMP_PLACEBO_B, **kw)
    c = L.diferenca_pos_pre(serie, periodos_pre=COMP_PRE_EXTRA, periodos_pos=COMP_PRE, **kw)
    d = L.diferenca_pos_pre(serie, periodos_pre=COMP_PRE_EXTRA, periodos_pos=COMP_POS, **kw)
    base = a.rename(columns={"delta": "delta_principal"})[["co_ibge", "y_pre", "y_pos", "delta_principal"]]
    base = base.merge(b.rename(columns={"y_pre": "y_placebo_a", "y_pos": "y_placebo_b", "delta": "delta_placebo"})
                      [["co_ibge", "y_placebo_a", "y_placebo_b", "delta_placebo"]], on="co_ibge", validate="one_to_one")
    base = base.merge(c.rename(columns={"y_pre": "y_pre_extra", "delta": "delta_s5_pre"})
                      [["co_ibge", "y_pre_extra", "delta_s5_pre"]], on="co_ibge", validate="one_to_one")
    base = base.merge(d.rename(columns={"delta": "delta_s5_dird"})[["co_ibge", "delta_s5_dird"]], on="co_ibge",
                      validate="one_to_one")
    s = serie.drop_duplicates("co_ibge").set_index("co_ibge")["s_mil"]
    base["s_mil"] = base["co_ibge"].map(s).astype(float)
    notas = {"principal": a.attrs.get("nota", ""), "placebo_pre": b.attrs.get("nota", ""),
             "S5_pre_menos_pre_extra": c.attrs.get("nota", ""), "S5_dird_pre_extra": d.attrs.get("nota", ""),
             "municipios_y_ausente_em_algum_mes_do_evento": int(
                 serie[serie["competencia"].isin(COMP_EVENTO)].groupby("co_ibge")["y"]
                 .apply(lambda v: bool(v.isna().any())).sum())}
    return base, notas


# ---------------------------------------------------------------------------
# 4. Estimação (chamadas à rdd_lib)
# ---------------------------------------------------------------------------

COLUNAS_SAIDA = [
    "natureza_dos_dados", "familia", "outcome_id", "outcome", "descricao_outcome", "papel", "populacao", "corte",
    "especificacao", "estimador", "no_protocolo", "rotulo", "status", "contraste", "h", "n_abaixo", "n_acima",
    "n_obs", "n_clusters", "tau", "ep", "ic95_inf", "ic95_sup", "p_valor", "ic_honesto_inf", "ic_honesto_sup", "M",
    "fator_M", "vies_max", "w_lr", "media_bruta_abaixo", "media_bruta_acima", "pesos_grupos", "entra_bky", "q_bky",
    "unidade", "nota",
]

COLUNAS_EVENTO = ["natureza_dos_dados", "familia", "outcome_id", "outcome", "populacao", "corte", "competencia",
                  "data", "janela", "referencia", "h", "n_abaixo", "n_acima", "tau", "ep", "ic95_inf", "ic95_sup",
                  "p_valor", "unidade", "nota"]


def janela_de(comp: str) -> str:
    if comp in COMP_PRE_EXTRA:
        return "pre_extra"
    if comp in COMP_ENTRE:
        return "entre_pre_extra_e_pre"
    if comp in COMP_PRE:
        return "pre"
    if comp in COMP_TRANSICAO:
        return "transicao"
    if comp in COMP_POS:
        return "pos"
    raise FalhaValidacao(f"competencia fora das janelas: {comp}")


def nova_linha(meta: dict, esp: str, estimador: str, *, h_mil, unidade: str, contraste: str = CONTRASTE_DIRD,
               rotulo_esp: str = "") -> dict:
    linha = {c: np.nan for c in COLUNAS_SAIDA}
    linha.update({"natureza_dos_dados": "EMPIRICO", **meta, "especificacao": esp, "estimador": estimador,
                  "no_protocolo": bool(NO_PROTOCOLO.get(esp.split("|")[0], False)),
                  "rotulo": rotulo_esp or ("" if NO_PROTOCOLO.get(esp, True) else ADICIONAL),
                  "contraste": contraste,
                  "h": (h_mil / 1000.0) if h_mil is not None and np.isfinite(h_mil) else np.nan,
                  "unidade": unidade, "nota": "", "entra_bky": False, "status": "EXECUTADO"})
    return linha


def preencher(linha: dict, res: dict | None) -> dict:
    if res is None:
        return linha
    for k in ("tau", "ep", "ic95_inf", "ic95_sup", "p_valor", "n_abaixo", "n_acima", "n_obs", "n_clusters",
              "media_bruta_abaixo", "media_bruta_acima"):
        if k in res and res[k] is not None:
            linha[k] = res[k]
    if res.get("pesos_grupos"):
        linha["pesos_grupos"] = json.dumps({k: round(v, 12) for k, v in res["pesos_grupos"].items()})
    notas = [linha.get("nota", ""), res.get("nota", "")]
    if res.get("covariaveis_descartadas"):
        notas.append(f"colunas descartadas: {res['covariaveis_descartadas']}")
    linha["nota"] = _juntar(*notas)
    tau = linha["tau"]
    if tau is None or not np.isfinite(float(tau)):
        linha["status"] = "SEM_ESTIMATIVA"
        if not linha["nota"]:
            linha["nota"] = "biblioteca devolveu NaN sem motivo"
    return linha


def nao_executado(meta: dict, esp: str, estimador: str, motivo: str, *, unidade: str, h_mil=H) -> dict:
    linha = nova_linha(meta, esp, estimador, h_mil=h_mil, unidade=unidade)
    linha["status"] = "NAO_EXECUTADO"
    linha["nota"] = motivo
    return linha


def empilhar(d: pd.DataFrame) -> pd.DataFrame:
    """Cada município entra uma vez por corte (grupo = corte); o kernel zera quem está fora da janela."""
    partes = []
    for c in CORTES:
        b = d.copy()
        b["corte_mil"] = float(c)
        b["grupo"] = str(c)
        partes.append(b)
    return pd.concat(partes, ignore_index=True)


def rd(d: pd.DataFrame, coluna: str, corte, h_mil=H, *, covariavel: str | None = None) -> dict:
    """RDD local linear (por corte, HC1) ou empilhada (CR1 por município) de `coluna`."""
    if corte == EMPILHADO:
        e = empilhar(d)
        Z = e[[covariavel]].to_numpy(dtype=float) if covariavel else None
        return L.rd_empilhado(e["s_mil"].to_numpy(dtype=float), e[coluna].to_numpy(dtype=float),
                              e["corte_mil"].to_numpy(dtype=float), grupo=e["grupo"].to_numpy(), h_mil=h_mil,
                              cluster=e["co_ibge"].to_numpy(), ids_unidade=e["co_ibge"].to_numpy(), Z=Z,
                              nomes_z=[covariavel] if covariavel else None)
    Z = d[[covariavel]].to_numpy(dtype=float) if covariavel else None
    return L.rd_local_linear(d["s_mil"].to_numpy(dtype=float), d[coluna].to_numpy(dtype=float), corte, h_mil, Z=Z,
                             nomes_z=[covariavel] if covariavel else None)


def rd_delta(d: pd.DataFrame, col_pos: str, col_pre: str, corte, h_mil=H) -> dict:
    """DiRD sobre delta = col_pos - col_pre: rd_dird_delta por corte, rd_empilhado no empilhado."""
    if corte == EMPILHADO:
        dd = d.assign(_delta=d[col_pos].to_numpy(dtype=float) - d[col_pre].to_numpy(dtype=float))
        r = rd(dd, "_delta", EMPILHADO, h_mil)
        r["estimador"] = "DiRD empilhado: rd_empilhado sobre delta, CR1 por municipio"
        return r
    return L.rd_dird_delta(d["s_mil"].to_numpy(dtype=float), d[col_pos].to_numpy(dtype=float),
                           d[col_pre].to_numpy(dtype=float), corte, h_mil)


def _rd_dif(a: dict, b: dict) -> dict:
    """Diferença de saltos entre subamostras disjuntas de municípios (EPs independentes)."""
    tau = a["tau"] - b["tau"]
    ep = math.sqrt(a["ep"] ** 2 + b["ep"] ** 2) if np.isfinite(a["ep"]) and np.isfinite(b["ep"]) else np.nan
    res = {"tau": tau, "ep": ep, "ic95_inf": tau - L.Z_975 * ep, "ic95_sup": tau + L.Z_975 * ep,
           "p_valor": L.p_normal(tau / ep) if np.isfinite(ep) and ep > 0 else np.nan,
           "n_abaixo": (a["n_abaixo"] or 0) + (b["n_abaixo"] or 0), "n_acima": (a["n_acima"] or 0) + (b["n_acima"] or 0),
           "nota": "diferenca entre subamostras disjuntas de municipios; EP = raiz da soma das variancias"}
    if not np.isfinite(tau):
        res["nota"] += "; algum dos saltos indefinido: " + _juntar(a.get("nota"), b.get("nota"))
    return res


def linhas_honesto(meta: dict, d: pd.DataFrame, corte, unidade: str, principal: dict) -> list[dict]:
    """IC honesto (h fixo, M x {0,5; 1; 2}) e h ótimo rotulado, por corte; empilhado com CR1."""
    linhas = []
    y = d["delta_principal"].to_numpy(dtype=float)
    s = d["s_mil"].to_numpy(dtype=float)
    est_c = "DiRD local linear triangular; IC honesto Armstrong-Kolesar (variancia por vizinhos, J=3)"
    est_e = "DiRD empilhado; IC honesto Armstrong-Kolesar (variancia CR1)"
    nota_m = "M = {f:g} x regra de bolso (quartica por lado, suporte ate o ponto medio entre cortes)"

    def linha_de(rec: dict, fator: float, otimo: bool, estimador: str) -> dict:
        esp = "ic_honesto_h_otimo" if otimo else "ic_honesto"
        ln = nova_linha(meta, esp, estimador, h_mil=rec.get("h_mil", H), unidade=unidade,
                        rotulo_esp=L.ROTULO_H_OTIMO if otimo else "")
        for k in ("tau", "ep", "ic95_inf", "ic95_sup", "p_valor", "n_abaixo", "n_acima", "M", "vies_max"):
            v = rec.get(k)
            if v is not None:
                ln[k] = v
        ln["ic_honesto_inf"], ln["ic_honesto_sup"] = ln["ic95_inf"], ln["ic95_sup"]
        ln["fator_M"] = fator
        ln["nota"] = _juntar("ep = EP usado no IC honesto", nota_m.format(f=fator), rec.get("nota", ""))
        if not np.isfinite(float(ln["ic95_inf"])):
            ln["status"] = "SEM_ESTIMATIVA"
        if fator == 1.0 and not otimo:
            principal["ic_honesto_inf"], principal["ic_honesto_sup"] = ln["ic95_inf"], ln["ic95_sup"]
            principal["M"], principal["fator_M"] = ln["M"], 1.0
        return ln

    try:
        if corte == EMPILHADO:
            e = empilhar(d)
            args = (e["s_mil"].to_numpy(dtype=float), e["delta_principal"].to_numpy(dtype=float),
                    e["corte_mil"].to_numpy(dtype=float))
            kw = {"grupo": e["grupo"].to_numpy(), "h_mil": H, "cluster": e["co_ibge"].to_numpy(),
                  "ids_unidade": e["co_ibge"].to_numpy()}
            base = L.rd_empilhado_honesto(*args, cortes_vizinhos=CORTES, **kw)
            M0 = base["M"]
            for f in FATORES_M:
                if f == 1.0:
                    hon = base
                elif M0 is not None and np.isfinite(M0):
                    hon = L.rd_empilhado_honesto(*args, M=f * M0, **kw)
                else:
                    hon = {**base, "ic95_inf": np.nan, "ic95_sup": np.nan, "M": np.nan,
                           "nota": _juntar(base.get("nota"), "M base indefinido")}
                linhas.append(linha_de({**hon, "h_mil": H}, f, False, est_e))
        else:
            tab = L.rd_honesto_relato(s, y, corte, fatores_M=FATORES_M, cortes_vizinhos=CORTES)
            for rec in tab.to_dict("records"):
                linhas.append(linha_de(rec, rec["fator_M"], rec["especificacao"] == "h_otimo", est_c))
    except ValueError as erro:
        principal["nota"] = _juntar(principal["nota"], f"IC honesto nao calculado: {erro}")
    return linhas


def local_randomization(meta: dict, d: pd.DataFrame, corte: int, w_mil, id_pop: int, unidade: str,
                        motivo_sem_janela: str = "") -> dict:
    est = "local randomization: diferenca de medias de delta na janela (c-w, c+w], p de Fisher (10.000 permutacoes)"
    if w_mil is None or not np.isfinite(w_mil):
        return nao_executado(meta, "local_randomization", est,
                             motivo_sem_janela or "nenhuma janela candidata passou no balanco (regra do E5)",
                             unidade=unidade, h_mil=np.nan)
    w = int(w_mil)
    semente = (L.SEMENTE, id_pop, int(corte), w)
    r = L.rl_janela(d["s_mil"].to_numpy(dtype=float), d["delta_principal"].to_numpy(dtype=float), corte, w,
                    semente=semente)
    linha = nova_linha(meta, "local_randomization", est, h_mil=w, unidade=unidade)
    linha["w_lr"] = w / 1000.0
    linha.update({"tau": r["tau"], "p_valor": r["p_valor"], "ep": r["ep_permutacao"], "n_abaixo": r["n_abaixo"],
                  "n_acima": r["n_acima"], "n_obs": (r["n_abaixo"] or 0) + (r["n_acima"] or 0)})
    x = d["s_mil"].to_numpy(dtype=float) - corte
    sem_y = int((((x > -w) & (x <= w)) & ~np.isfinite(d["delta_principal"].to_numpy(dtype=float))).sum())
    linha["nota"] = _juntar("ep = DP da distribuicao de permutacao sob o nulo exato; sem IC por inversao "
                            "(grade do E5 so cobre outcomes em [0, 1])", f"semente {list(semente)}",
                            f"{sem_y} municipios da janela sem delta (fora)" if sem_y else "", r.get("nota", ""))
    if not np.isfinite(linha["tau"]):
        linha["status"] = "SEM_ESTIMATIVA"
    return linha


def conferir_painel(meta: dict, d: pd.DataFrame, serie: pd.DataFrame, corte: int, principal: dict,
                    unidade: str) -> dict:
    """rd_dird_painel em linhas município x mês (municípios com delta completo): ponto idêntico ao principal."""
    ok = set(d.loc[np.isfinite(d["delta_principal"].to_numpy(dtype=float)), "co_ibge"])
    p = serie[serie["competencia"].isin(COMP_PRE + COMP_POS) & serie["co_ibge"].isin(ok)].copy()
    p["pos"] = p["competencia"].isin(COMP_POS).astype(float)
    r = L.rd_dird_painel(p["s_mil"].to_numpy(dtype=float), p["y"].to_numpy(dtype=float), p["pos"].to_numpy(),
                         corte, p["co_ibge"].to_numpy(), H)
    t0, t1 = principal.get("tau"), r.get("tau")
    if np.isfinite(t0) or np.isfinite(t1):
        if not (np.isfinite(t0) and np.isfinite(t1) and abs(t0 - t1) <= 1e-8 * max(1.0, abs(t0))):
            raise FalhaValidacao(f"{meta['outcome_id']} {meta['populacao']} {corte}: rd_dird_painel ({t1}) != "
                                 f"rd_dird_delta ({t0})")
    linha = preencher(nova_linha(meta, "dird_painel", r.get("estimador", "rd_dird_painel"), h_mil=H,
                                 unidade=unidade, rotulo_esp=f"{ADICIONAL} (conferencia de identidade)"), r)
    linha["nota"] = _juntar("ponto identico ao principal (conferido, tol 1e-8); EP CR1 por municipio sobre linhas "
                            "mensais", linha["nota"])
    return linha


def suplementares(meta: dict, d: pd.DataFrame, corte, unidade: str, sup: dict) -> list[dict]:
    """S2 (donut), S3 (porte IED muda x não muda, por corte) e S4 (Amazônia Legal/fronteira, só 0,400)."""
    linhas = []
    est = "DiRD principal na subamostra"

    def estimar(sub):
        return rd_delta(sub, "y_pos", "y_pre", corte)

    donut = d[~d["s_mil"].isin([float(c) for c in CORTES])]
    ln = preencher(nova_linha(meta, "S2_donut", f"{est}: exclui IVS == 0,300 e == 0,400", h_mil=H, unidade=unidade),
                   estimar(donut))
    ln["nota"] = _juntar(f"{len(d) - len(donut)} municipios excluidos (IVS exatamente num corte)", ln["nota"])
    linhas.append(ln)
    if corte == EMPILHADO:
        return linhas
    s3 = sup.get("S3")
    nomes3 = ("S3_porte_muda", "S3_porte_nao_muda", "S3_diferenca")
    if s3 is None or s3.get("tabela") is None:
        motivo = (s3 or {}).get("motivo", "insumo do S3 indisponivel")
        linhas.extend(nao_executado(meta, n, est, motivo, unidade=unidade) for n in nomes3)
    else:
        porte = d["co_ibge"].map(s3["tabela"])
        muda = porte.isin(s3["portes_muda"][corte])
        sem = int(porte.isna().sum())
        ra, rb = estimar(d[muda & porte.notna()]), estimar(d[~muda & porte.notna()])
        txt = f"portes onde o estrato IED muda em {ROTULO_CORTE[corte]}: {sorted(s3['portes_muda'][corte])}"
        for nome, rr in zip(nomes3, (ra, rb, _rd_dif(ra, rb))):
            ln = preencher(nova_linha(meta, nome, f"{est}; {txt}", h_mil=H, unidade=unidade), rr)
            if sem:
                ln["nota"] = _juntar(ln["nota"], f"{sem} municipios sem porte no a10 (fora)")
            linhas.append(ln)
    if corte == 400:
        s4 = sup.get("S4")
        nomes4 = ("S4_dentro", "S4_fora", "S4_diferenca")
        if s4 is None or s4.get("tabela") is None:
            motivo = (s4 or {}).get("motivo", "insumo do S4 indisponivel")
            linhas.extend(nao_executado(meta, n, est, motivo, unidade=unidade) for n in nomes4)
        else:
            flag = d["co_ibge"].map(s4["tabela"])
            sem = int(flag.isna().sum())
            dentro = flag == 1
            ra, rb = estimar(d[dentro & flag.notna()]), estimar(d[~dentro & flag.notna()])
            for nome, rr in zip(nomes4, (ra, rb, _rd_dif(ra, rb))):
                ln = preencher(nova_linha(meta, nome, f"{est}; {s4['definicao']}", h_mil=H, unidade=unidade), rr)
                if sem:
                    ln["nota"] = _juntar(ln["nota"], f"{sem} municipios sem atributo (fora)")
                linhas.append(ln)
    return linhas


def estimar_outcome(spec: dict, pop_nome: str, serie: pd.DataFrame, *, sup: dict, lr: dict,
                    motivos_lr: dict | None = None, conferir: bool = True,
                    nota_extra: str = "") -> tuple[list[dict], dict, pd.DataFrame]:
    """Todas as especificações de um outcome x população, nos dois cortes e empilhado.

    Devolve (linhas, informações de amostra, base por município com médias e deltas).
    """
    d, notas_jan = janelas(serie)
    unidade = UNIDADES[spec["tipo"]]
    familia = "F3"
    meta0 = {"familia": familia, "outcome_id": spec["id"], "outcome": f"{spec['grupo']}:{spec['col']}",
             "descricao_outcome": spec["desc"], "papel": spec["papel"], "populacao": pop_nome}
    linhas = []
    nota_hor = ""
    if spec.get("horas_parcial"):
        nota_hor = _juntar("soma parcial das horas observadas (vinculos com hora em branco entram com as horas que "
                           "tem; protocolo §16)", nota_extra)
    elif spec["tipo"] == "horas":
        nota_hor = _juntar("horas em branco ficam ausentes (nunca zero): municipio sem todos os meses da janela fica "
                           f"fora; {notas_jan['principal'] or 'nenhum municipio incompleto nas janelas principais'}",
                           nota_extra)
    for corte in (*CORTES, EMPILHADO):
        meta = {**meta0, "corte": ROTULO_CORTE[corte]}
        est_p = ("DiRD local linear triangular sobre delta, EP HC1" if corte != EMPILHADO else
                 "DiRD empilhado (r = s - c, intercepto e inclinacoes por corte x lado, tau comum), CR1 por municipio")
        rp = rd_delta(d, "y_pos", "y_pre", corte)
        lp = preencher(nova_linha(meta, "principal", est_p, h_mil=H, unidade=unidade), rp)
        lp["nota"] = _juntar(nota_hor, lp["nota"])
        lp["entra_bky"] = bool(spec["bky"] and lp["status"] == "EXECUTADO")
        linhas.append(lp)
        for h in H_SENS:
            linhas.append(preencher(nova_linha(meta, "sensibilidade_h", est_p, h_mil=h, unidade=unidade),
                                    rd_delta(d, "y_pos", "y_pre", corte, h)))
        linhas.extend(linhas_honesto(meta, d, corte, unidade, lp))
        linhas.append(preencher(nova_linha(meta, "pos_com_pre_covariavel",
                                           f"RDD de media(pos) com media(pre) como covariavel ({est_p.split(',')[0]})",
                                           h_mil=H, unidade=unidade), rd(d, "y_pos", corte, covariavel="y_pre")))
        if corte != EMPILHADO:
            id_pop = ID_SEMENTE_POP[pop_nome]
            linhas.append(local_randomization(meta, d, corte, lr.get((pop_nome, corte)), id_pop, unidade,
                                              (motivos_lr or {}).get((pop_nome, corte), "")))
            if conferir:
                linhas.append(conferir_painel(meta, d, serie, corte, rp, unidade))
        lpl = preencher(nova_linha(meta, "placebo_pre", f"{est_p}; delta = media(202412-202505) - media(202406-202411)",
                                   h_mil=H, unidade=unidade), rd_delta(d, "y_placebo_b", "y_placebo_a", corte))
        lpl["nota"] = _juntar("placebo nao e nulo limpo: IED desde 05/2024, nutricao 11/2024, emendas 04-05/2025 "
                              "(auditoria 18 §3.1)", notas_jan["placebo_pre"], lpl["nota"])
        linhas.append(lpl)
        for esp, col in (("nivel_pre", "y_pre"), ("nivel_pos", "y_pos"), ("nivel_pre_extra", "y_pre_extra")):
            ln = preencher(nova_linha(meta, esp, f"RDD em nivel de {col} ({est_p.split(',')[0].replace('DiRD ', '')})",
                                      h_mil=H, unidade=unidade, contraste=CONTRASTE_NIVEL), rd(d, col, corte))
            linhas.append(ln)
        l5a = preencher(nova_linha(meta, "S5_pre_menos_pre_extra", f"{est_p}; delta = media(pre) - media(pre extra)",
                                   h_mil=H, unidade=unidade), rd_delta(d, "y_pre", "y_pre_extra", corte))
        l5a["contraste"] = ("mudança da descontinuidade entre 2022-01..2023-03 e o pré principal, antes do PMM-E "
                            "(Portarias 752, 3.493, emendas e outras; auditoria 18)")
        l5a["nota"] = _juntar(notas_jan["S5_pre_menos_pre_extra"], l5a["nota"])
        linhas.append(l5a)
        l5b = preencher(nova_linha(meta, "S5_dird_pre_extra", f"{est_p}; delta = media(pos) - media(pre extra)",
                                   h_mil=H, unidade=unidade), rd_delta(d, "y_pos", "y_pre_extra", corte))
        l5b["contraste"] = ("bolsa + variação, entre 2022-01..2023-03 e o pós, das descontinuidades de todas as "
                            "políticas com corte em 0,3/0,4 (todas posteriores a 2023-03)")
        l5b["nota"] = _juntar(notas_jan["S5_dird_pre_extra"], l5b["nota"])
        linhas.append(l5b)
        linhas.extend(suplementares(meta, d, corte, unidade, sup))
    if spec.get("rotulo"):
        for ln in linhas:
            ln["rotulo"] = _juntar(spec["rotulo"], ln["rotulo"])
    info = {"notas_janelas": notas_jan, "n_municipios": int(len(d)),
            "n_delta_principal_completo": int(np.isfinite(d["delta_principal"].to_numpy(dtype=float)).sum())}
    return linhas, info, d


def contar_horas_em_branco(painel: pd.DataFrame, grupo: str, municipios) -> dict:
    """Contagem agregada (sem quebra por corte) de células e vínculos com hora em branco no grupo, nos meses do E7."""
    sub = painel[(painel["grupo"] == grupo) & painel["co_ibge"].isin(set(municipios))
                 & painel["competencia"].isin(COMP_EVENTO)]
    b = sub[sub["n_vinculos_horas_ausentes"] > 0]
    return {"celulas_municipio_mes": int(len(b)), "vinculos_em_branco_soma_nos_meses": int(b["n_vinculos_horas_ausentes"].sum()),
            "municipios": int(b["co_ibge"].nunique())}


def estudo_evento(spec: dict, pop_nome: str, serie: pd.DataFrame) -> list[dict]:
    """RDD de (Y_t - Y_202506) em cada competência, por corte (rd_estudo_evento) e empilhado (rd_empilhado)."""
    unidade = UNIDADES[spec["tipo"]]
    meta = {"natureza_dos_dados": "EMPIRICO", "familia": "F3", "outcome_id": spec["id"],
            "outcome": f"{spec['grupo']}:{spec['col']}", "populacao": pop_nome, "unidade": unidade}
    linhas = []
    for corte in CORTES:
        ev = L.rd_estudo_evento(serie, col_unidade="co_ibge", col_periodo="competencia", col_y="y", col_s="s_mil",
                                corte_mil=corte, periodo_ref=COMP_REF, h_mil=H, periodos=list(COMP_EVENTO))
        for r in ev.to_dict("records"):
            linhas.append({**meta, "corte": ROTULO_CORTE[corte], "competencia": r["periodo"],
                           "referencia": bool(r["referencia"]), **{k: r[k] for k in (
                               "h", "n_abaixo", "n_acima", "tau", "ep", "ic95_inf", "ic95_sup", "p_valor", "nota")}})
    larga = serie.pivot(index="co_ibge", columns="competencia", values="y")
    s = serie.drop_duplicates("co_ibge").set_index("co_ibge")["s_mil"].reindex(larga.index)
    ref = larga[COMP_REF]
    for per in COMP_EVENTO:
        base = {**meta, "corte": EMPILHADO, "competencia": per, "h": H / 1000.0}
        if per == COMP_REF:
            linhas.append({**base, "referencia": True, "tau": np.nan, "ep": np.nan, "ic95_inf": np.nan,
                           "ic95_sup": np.nan, "p_valor": np.nan, "n_abaixo": None, "n_acima": None,
                           "nota": "periodo de referencia: normalizado (y_ref - y_ref), nao estimado"})
            continue
        dd = pd.DataFrame({"co_ibge": larga.index, "s_mil": s.to_numpy(dtype=float),
                           "dy": (larga[per] - ref).to_numpy(dtype=float)})
        r = rd(dd, "dy", EMPILHADO)
        linhas.append({**base, "referencia": False, **{k: r.get(k) for k in (
            "n_abaixo", "n_acima", "tau", "ep", "ic95_inf", "ic95_sup", "p_valor", "nota")}})
    for ln in linhas:
        ln["janela"] = janela_de(ln["competencia"])
        ln["data"] = f"{ln['competencia'][:4]}-{ln['competencia'][4:]}"
    return linhas


def aplicar_bky(est: pd.DataFrame) -> pd.DataFrame:
    """q BKY dentro da família F3: linhas principais dos outcomes do §5 (S6 fora)."""
    est = est.copy()
    est["q_bky"] = np.nan
    m = (est["familia"] == "F3") & est["entra_bky"].astype(bool)
    if m.any():
        est.loc[m, "q_bky"] = L.qvalores_bky(est.loc[m, "p_valor"].to_numpy(dtype=float))
    return est


def p2_de(est: pd.DataFrame) -> dict:
    r = est[(est["outcome_id"] == "F3.1") & (est["populacao"] == "U") & (est["corte"] == EMPILHADO)
            & (est["especificacao"] == "principal")]
    if len(r) != 1:
        raise FalhaValidacao(f"P2: {len(r)} linhas encontradas (esperada 1)")
    r = r.iloc[0]
    return {"hipotese": "P2: F3.1 por DiRD em U, cortes empilhados (protocolo §7)",
            **{k: r[k] for k in ("tau", "ep", "ic95_inf", "ic95_sup", "p_valor", "q_bky", "ic_honesto_inf",
                                 "ic_honesto_sup", "M", "n_abaixo", "n_acima", "n_clusters", "unidade", "status")},
            "holm": "o coordenador junta este p com o de P1 (E6_resumo.json) no Holm; nao calculado aqui"}


# ---------------------------------------------------------------------------
# Seleção da janela de local randomization (só covariáveis; regra do E5)
# ---------------------------------------------------------------------------

def selecao_janelas_lr(pops: dict[str, pd.DataFrame], n_perm: int = L.N_PERMUTACOES) -> tuple[dict, dict, dict]:
    sys.dont_write_bytecode = True
    E5 = _importar(DIR_RDD / "11_inferencia_alternativa.py", "e5_para_e7")
    sys.dont_write_bytecode = _bytecode
    cov_lr, _ = E5.carregar_covariaveis_e5(ROOT)
    e5 = pd.read_csv(E5_SEL)
    lr, motivos, conf = {}, {}, {}
    for nome in ("U", "V1"):
        pc = pops[nome][["co_ibge"]].assign(s_mil=pops[nome]["s_mil"].astype(int)).merge(
            cov_lr, on="co_ibge", how="left", validate="one_to_one")
        if pc[[c for c, _ in E5.COV_LR]].isna().any().any():
            raise FalhaValidacao(f"{nome}: covariavel da selecao LR ausente")
        sel = E5.selecionar_janela(pc, f"P{ID_SEMENTE_POP[nome]}", n_perm)
        if nome == "V1":
            ref = e5[e5["populacao"] == "P1"].reset_index(drop=True)
            a = sel[["corte", "w", "n_abaixo", "n_acima", "p_min", "selecionada"]].reset_index(drop=True)
            b = ref[["corte", "w", "n_abaixo", "n_acima", "p_min", "selecionada"]]
            iguais = (len(a) == len(b)
                      and np.allclose(a[["corte", "w", "n_abaixo", "n_acima"]], b[["corte", "w", "n_abaixo", "n_acima"]])
                      and np.allclose(a["p_min"].fillna(-1), b["p_min"].fillna(-1), atol=1e-12)
                      and (a["selecionada"].astype(bool) == b["selecionada"].astype(bool)).all())
            if not iguais:
                raise FalhaValidacao("V1: recomputacao da selecao LR nao reproduz E5_lr_selecao_janela.csv")
            conf["V1_selecao_lr_reproduz_E5"] = True
        if nome == "U" and E6_SEL.exists():
            e6 = pd.read_csv(E6_SEL, dtype={"corte": str})
            ref = e6[e6["populacao"] == "U"].assign(corte=lambda x: x["corte"].astype(float)).reset_index(drop=True)
            a = sel[["corte", "w", "n_abaixo", "n_acima", "p_min", "selecionada"]].reset_index(drop=True)
            b = ref[["corte", "w", "n_abaixo", "n_acima", "p_min", "selecionada"]]
            iguais = (len(a) == len(b)
                      and np.allclose(a[["corte", "w", "n_abaixo", "n_acima"]].astype(float),
                                      b[["corte", "w", "n_abaixo", "n_acima"]].astype(float))
                      and np.allclose(a["p_min"].astype(float).fillna(-1), b["p_min"].astype(float).fillna(-1),
                                      atol=1e-12)
                      and (a["selecionada"].astype(bool) == b["selecionada"].astype(bool)).all())
            if not iguais:
                raise FalhaValidacao("U: selecao LR do E7 nao reproduz E6_lr_selecao_janela.csv")
            conf["U_selecao_lr_reproduz_E6"] = True
        elif nome == "U":
            conf["U_selecao_lr_reproduz_E6"] = "E6_lr_selecao_janela.csv ausente: conferencia nao feita"
        for corte in CORTES:
            esc = sel[(sel["corte"] == corte / 1000) & sel["selecionada"]]
            if len(esc):
                lr[(nome, corte)] = int(round(float(esc.iloc[0]["w"]) * 1000))
            else:
                lr[(nome, corte)] = None
                motivos[(nome, corte)] = "nenhuma janela candidata passou no balanco (regra do E5)"
    conf["janelas"] = {f"{k[0]}|{ROTULO_CORTE[k[1]]}": (v / 1000 if v else None) for k, v in lr.items()}
    return lr, motivos, conf


# ---------------------------------------------------------------------------
# Figuras
# ---------------------------------------------------------------------------

def _plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    return plt


def _data(comp_ou_iso: str) -> dt.date:
    if "-" in comp_ou_iso and len(comp_ou_iso) == 10:
        return dt.date.fromisoformat(comp_ou_iso)
    c = comp_ou_iso.replace("-", "")
    return dt.date(int(c[:4]), int(c[4:6]), 15)


def figura_evento(ev: pd.DataFrame, titulo: str, ylabel: str, caminho: Path) -> None:
    import textwrap
    plt = _plt()
    cortes = [ROTULO_CORTE[c] for c in (*CORTES, EMPILHADO)]
    fig, axs = plt.subplots(len(cortes), 1, figsize=(10.5, 3.0 * len(cortes)), sharex=True, squeeze=False)
    for ax, c in zip(axs[:, 0], cortes):
        e = ev[ev["corte"] == c].sort_values("competencia")
        x = [_data(v) for v in e["competencia"]]
        tau = e["tau"].to_numpy(dtype=float)
        tau = np.where(e["referencia"].astype(bool).to_numpy(), 0.0, tau)
        lo = e["ic95_inf"].to_numpy(dtype=float)
        hi = e["ic95_sup"].to_numpy(dtype=float)
        ax.axvspan(_data("202406") - dt.timedelta(days=14), _data("202506") + dt.timedelta(days=15),
                   color="#e5e7eb", alpha=0.7, linewidth=0, label="pré principal")
        ax.axvspan(_data("202510") - dt.timedelta(days=14), _data("202608") + dt.timedelta(days=15),
                   color="#dbeafe", alpha=0.7, linewidth=0, label="pós")
        ax.axhline(0, color="#6b7280", linewidth=0.8)
        for data, rot, _, principal in DATAS_POLITICAS:
            if principal:
                ax.axvline(_data(data), color="#b91c1c", linewidth=1.0, linestyle="--", alpha=0.8)
            else:
                ax.axvline(_data(data), color="#9ca3af", linewidth=0.7, linestyle=":", alpha=0.9)
        ok = np.isfinite(lo) & np.isfinite(hi)
        ax.errorbar(np.array(x, dtype=object)[ok], tau[ok], yerr=[tau[ok] - lo[ok], hi[ok] - tau[ok]], fmt="none",
                    ecolor="#93c5fd", elinewidth=1.4, capsize=0)
        ax.plot(x, tau, "o", color="#1d4ed8", markersize=3.5)
        ref = e["referencia"].astype(bool).to_numpy()
        ax.plot(np.array(x, dtype=object)[ref], tau[ref], "s", color="#111827", markersize=5)
        ax.set_title(f"corte {c.replace('.', ',')}", fontsize=9, loc="left")
        ax.set_ylabel(ylabel, fontsize=8)
        ax.grid(alpha=0.25, linewidth=0.6)
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)
    ax0 = axs[0, 0]
    ylim = ax0.get_ylim()
    for data, rot, _, principal in DATAS_POLITICAS:
        if principal:
            ax0.text(_data(data), ylim[1], " " + rot, rotation=90, va="top", ha="right", fontsize=6, color="#b91c1c")
    fig.suptitle(titulo, fontsize=10)
    secund = "; ".join(f"{d[:7]} {r}" for d, r, _, p in DATAS_POLITICAS if not p)
    rod = ("EMPIRICO. Salto da RDD (h = 0,050, triangular; HC1 por corte, CR1 empilhado) de Y_t − Y_202506; "
           "quadrado = referência; barras = IC 95% pontual. Tracejado vermelho: atos principais (rótulo no topo). "
           f"Pontilhado cinza: {secund}. Fontes: auditorias 18 e 01.")
    linhas = textwrap.wrap(rod, 150)
    fig.text(0.01, 0.005, "\n".join(linhas), fontsize=6.5, color="#4b5563", va="bottom")
    fig.tight_layout(rect=(0, 0.012 * len(linhas) + 0.01, 1, 0.97))
    fig.savefig(caminho, dpi=120)
    plt.close(fig)


def _curva(s, y, corte):
    r = L.rd_local_linear(s, y, corte, H, detalhes=True)
    if "_detalhes" not in r:
        return None, r
    fit = r["_detalhes"]["fit"]
    out = {}
    for lado, grade in (("abaixo", np.linspace(-H + 1, 0, 40)), ("acima", np.linspace(0.5, H - 1, 40))):
        x = grade / 1000.0
        t = 1.0 if lado == "acima" else 0.0
        X = np.column_stack([np.ones_like(x), x, np.full_like(x, t), t * x])
        idx = [fit["nomes"].index(n) for n in ("const", "x", "T", "T_x")]
        b = fit["beta"][idx]
        V = fit["V"][np.ix_(idx, idx)]
        pred = X @ b
        ep = np.sqrt(np.einsum("ij,jk,ik->i", X, V, X))
        out[lado] = (corte + grade, pred, pred - L.Z_975 * ep, pred + L.Z_975 * ep)
    return out, r


def figura_rd(painel: list[tuple[str, np.ndarray, np.ndarray, int]], titulo: str, ylabel: str, caminho: Path,
              rodape: str) -> None:
    import textwrap
    plt = _plt()
    ncol = 2
    nlin = math.ceil(len(painel) / ncol)
    fig, axs = plt.subplots(nlin, ncol, figsize=(10.4, 3.9 * nlin), squeeze=False)
    for ax, (sub, s, y, corte) in zip(axs.flat, painel):
        ok = np.isfinite(y) & np.isfinite(s)
        s, y = s[ok], y[ok]
        jan = (s > corte - H) & (s < corte + H)
        bins = np.arange(corte - H, corte + H + 1, 5)
        idx = np.digitize(s[jan], bins, right=True)
        for b in np.unique(idx):
            m = idx == b
            if m.sum():
                xc = (bins[b - 1] + bins[b]) / 2 if 0 < b < len(bins) else s[jan][m].mean()
                ax.scatter(xc / 1000, y[jan][m].mean(), s=10 + 4 * m.sum() ** 0.5, color="#4b5563", zorder=3,
                           edgecolor="white", linewidth=0.8)
        cur, r = _curva(s, y, corte)
        if cur is not None:
            for lado in ("abaixo", "acima"):
                gx, pr, lo, hi = cur[lado]
                ax.fill_between(gx / 1000, lo, hi, color="#93c5fd", alpha=0.45, linewidth=0)
                ax.plot(gx / 1000, pr, color="#1d4ed8", linewidth=2)
            txt = (f"salto = {r['tau']:.3g} [{r['ic95_inf']:.3g}; {r['ic95_sup']:.3g}]"
                   .replace(".", ",").replace("-", "−"))
        else:
            txt = f"sem estimativa: {r.get('nota', '')[:60]}"
        ax.axvline(corte / 1000, color="#9ca3af", linewidth=1, linestyle="--")
        ax.set_title(f"{sub}\n{txt}", fontsize=9)
        ax.set_xlabel("IVS 2010 oficial")
        ax.set_ylabel(ylabel, fontsize=8)
        ax.grid(alpha=0.25, linewidth=0.6)
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)
    for ax in list(axs.flat)[len(painel):]:
        ax.axis("off")
    fig.suptitle(titulo, fontsize=10)
    linhas = textwrap.wrap(rodape, 130)
    fig.text(0.01, 0.005, "\n".join(linhas), fontsize=7, color="#4b5563", va="bottom")
    fig.tight_layout(rect=(0, 0.03 * len(linhas) / nlin, 1, 0.95))
    fig.savefig(caminho, dpi=120)
    plt.close(fig)


def gerar_figuras(bases: dict, eventos: pd.DataFrame, dir_fig: Path) -> list[str]:
    dir_fig.mkdir(parents=True, exist_ok=True)
    for antigo in dir_fig.glob("*.png"):
        antigo.unlink()
    feitos = []
    rod = ("EMPIRICO. Médias em faixas de 0,005 (área ~ n); reta local linear triangular h = 0,050 e IC 95% pontual "
           "HC1, por corte. Salto = lado de bolsa maior − lado de bolsa menor.")
    for (oid, pop), (spec, d) in bases.items():
        if not spec.get("figura", True):
            continue
        tag = f"{oid.replace('.', '_')}_{pop}"
        un = UNIDADES[spec["tipo"]]
        s = d["s_mil"].to_numpy(float)
        dl = d["delta_principal"].to_numpy(float)
        painel = [(f"corte {ROTULO_CORTE[c].replace('.', ',')}", s, dl, c) for c in CORTES]
        nome = f"E7_dird_{tag}.png"
        figura_rd(painel, f"{oid} — DiRD: Δ = média(pós) − média(pré), {pop}", f"Δ {un}", dir_fig / nome,
                  rod + " Contraste: bolsa + variação das outras descontinuidades (auditoria 18).")
        feitos.append(nome)
        painel = []
        for c in CORTES:
            for col, rot in (("y_pre_extra", "pré extra 2022-01..2023-03"), ("y_pre", "pré 2024-06..2025-06"),
                             ("y_pos", "pós 2025-10..2026-08")):
                painel.append((f"{rot}, corte {ROTULO_CORTE[c].replace('.', ',')}", s, d[col].to_numpy(float), c))
        nome = f"E7_nivel_{tag}.png"
        figura_rd(painel, f"{oid} — RDD em nível (pacote do corte), {pop}", un, dir_fig / nome,
                  rod + " Em nível o contraste é o pacote do corte (bolsa + outras regras nos mesmos cortes).")
        feitos.append(nome)
        ev = eventos[(eventos["outcome_id"] == oid) & (eventos["populacao"] == pop)]
        nome = f"E7_evento_{tag}.png"
        figura_evento(ev, f"{oid} — estudo de evento da DiRD ({spec['desc']}), {pop}", f"salto em Y_t − Y_ref",
                      dir_fig / nome)
        feitos.append(nome)
    return feitos


# ---------------------------------------------------------------------------
# Tabelas do doc 43 (geradas das saídas; nenhum número digitado)
# ---------------------------------------------------------------------------

def _n(v, casas=3, pp=False, sinal=True) -> str:
    if v is None or (isinstance(v, float) and not math.isfinite(v)) or pd.isna(v):
        return "—"
    v = float(v) * (100 if pp else 1)
    txt = f"{v:+.{casas}f}" if sinal else f"{v:.{casas}f}"
    return txt.replace("-", "−").replace(".", ",")


def _p(v) -> str:
    if v is None or pd.isna(v):
        return "—"
    return f"{float(v):.3f}".replace(".", ",")


def _ic(a, b, casas=3, pp=False) -> str:
    return f"[{_n(a, casas, pp)}; {_n(b, casas, pp)}]"


def _fmt_int(v) -> str:
    return "—" if v is None or pd.isna(v) else str(int(v))


def _escala(unidade: str) -> tuple[int, bool, str]:
    if unidade.startswith("fracao"):
        return 1, True, "p.p."
    if unidade.startswith("horas"):
        return 1, False, ""
    return 3, False, ""


def _tab(sub: pd.DataFrame, cab: list[str], cols) -> str:
    out = ["| " + " | ".join(cab) + " |", "|" + "|".join("---" for _ in cab) + "|"]
    for r in sub.to_dict("records"):
        out.append("| " + " | ".join(f(r) for f in cols) + " |")
    return "\n".join(out)


def gerar_tabelas_doc(est: pd.DataFrame, ev: pd.DataFrame, resumo: dict) -> dict[str, str]:
    t: dict[str, str] = {}

    def tau(r):
        c, pp, u = _escala(r["unidade"])
        return f"{_n(r['tau'], c, pp)} {u}".strip()

    def ic(r):
        c, pp, _ = _escala(r["unidade"])
        return _ic(r["ic95_inf"], r["ic95_sup"], c, pp)

    def ich(r):
        c, pp, _ = _escala(r["unidade"])
        return _ic(r["ic_honesto_inf"], r["ic_honesto_sup"], c, pp)

    nab = lambda r: f"{_fmt_int(r['n_abaixo'])} / {_fmt_int(r['n_acima'])}"
    corte = lambda r: str(r["corte"]).replace(".", ",")
    oid = lambda r: r["outcome_id"]
    pop = lambda r: r["populacao"]
    esp = est["especificacao"]
    ordem = {c["id"]: i for i, c in enumerate(CATALOGO)}

    def ordenar(sub):
        return sub.assign(_o=sub["outcome_id"].map(ordem)).sort_values(["_o", "populacao"], kind="stable")

    # P2.
    p2 = resumo.get("p2_para_holm", {})
    c, pp, u = _escala(p2.get("unidade", ""))
    t["p2"] = "\n".join([
        "| Hipótese | n abaixo / acima | Salto | IC 95% (CR1) | IC honesto (M) | p | q BKY (F3) |",
        "|---|---|---|---|---|---|---|",
        f"| P2: F3.1, U, cortes empilhados | {_fmt_int(p2.get('n_abaixo'))} / {_fmt_int(p2.get('n_acima'))} | "
        f"{_n(p2.get('tau'), c, pp)} | {_ic(p2.get('ic95_inf'), p2.get('ic95_sup'), c, pp)} | "
        f"{_ic(p2.get('ic_honesto_inf'), p2.get('ic_honesto_sup'), c, pp)} | **{_p(p2.get('p_valor'))}** | "
        f"{_p(p2.get('q_bky'))} |"])
    # Principal.
    sub = ordenar(est[esp == "principal"])
    t["principal"] = _tab(sub, ["Outcome", "População", "Corte", "n abaixo / acima", "Salto", "IC 95%",
                                "IC honesto (M)", "p", "q BKY"],
                          [oid, pop, corte, nab, tau, ic, ich, lambda r: _p(r["p_valor"]), lambda r: _p(r["q_bky"])])
    # Sensibilidades.
    linhas = ["| Outcome | População | Corte | h = 0,030 | h = 0,080 | Y_pós com Y_pré covariável | donut (S2) | "
              "LR: janela, salto, p Fisher | painel (conferência) |", "|---|---|---|---|---|---|---|---|---|"]
    for r in ordenar(est[esp == "principal"]).to_dict("records"):
        chave = (est["outcome_id"] == r["outcome_id"]) & (est["populacao"] == r["populacao"]) & \
                (est["corte"] == r["corte"])

        def pega(e, h=None):
            m = chave & (esp == e)
            if h is not None:
                m &= np.isclose(est["h"].astype(float), h)
            g = est[m]
            return g.iloc[0].to_dict() if len(g) else None

        def cel(x):
            return "—" if x is None else f"{tau(x)} (p = {_p(x['p_valor'])})"

        lr = pega("local_randomization")
        lr_txt = "—" if lr is None else ("sem janela" if lr["status"] == "NAO_EXECUTADO" else
                                        f"±{_n(lr['w_lr'], 3, sinal=False)}: {tau(lr)} (p = {_p(lr['p_valor'])})")
        pn = pega("dird_painel")
        linhas.append(f"| {r['outcome_id']} | {r['populacao']} | {corte(r)} | {cel(pega('sensibilidade_h', 0.030))} | "
                      f"{cel(pega('sensibilidade_h', 0.080))} | {cel(pega('pos_com_pre_covariavel'))} | "
                      f"{cel(pega('S2_donut'))} | {lr_txt} | "
                      f"{'—' if pn is None else 'ponto idêntico; p CR1 = ' + _p(pn['p_valor'])} |")
    t["sensibilidades"] = "\n".join(linhas)
    # Honesto.
    sub = ordenar(est[(esp == "ic_honesto")])
    t["honesto"] = _tab(sub, ["Outcome", "População", "Corte", "fator de M", "M", "IC honesto", "p honesto"],
                        [oid, pop, corte, lambda r: _n(r["fator_M"], 1, sinal=False), lambda r: _n(r["M"], 1, sinal=False),
                         ich, lambda r: _p(r["p_valor"])])
    # Placebos de janela e S5.
    for nome, filtro in (("placebo_pre", esp == "placebo_pre"),
                         ("s5", esp.isin(["S5_pre_menos_pre_extra", "S5_dird_pre_extra"]))):
        sub = ordenar(est[filtro])
        t[nome] = _tab(sub, ["Outcome", "População", "Corte", "Especificação", "n abaixo / acima", "Salto", "IC 95%",
                             "p"], [oid, pop, corte, lambda r: r["especificacao"], nab, tau, ic,
                                    lambda r: _p(r["p_valor"])])
    # Níveis.
    linhas = ["| Outcome | População | Corte | nível pré extra | nível pré | nível pós | DiRD (principal) |",
              "|---|---|---|---|---|---|---|"]
    for r in ordenar(est[esp == "principal"]).to_dict("records"):
        chave = (est["outcome_id"] == r["outcome_id"]) & (est["populacao"] == r["populacao"]) & \
                (est["corte"] == r["corte"])
        cel = []
        for e in ("nivel_pre_extra", "nivel_pre", "nivel_pos"):
            g = est[chave & (esp == e)]
            cel.append("—" if not len(g) else f"{tau(g.iloc[0])} {ic(g.iloc[0])}")
        linhas.append(f"| {r['outcome_id']} | {r['populacao']} | {corte(r)} | " + " | ".join(cel) +
                      f" | {tau(r)} {ic(r)} |")
    t["niveis"] = "\n".join(linhas)
    # S3/S4.
    sub = ordenar(est[esp.str.startswith(("S3", "S4"))])
    t["s3_s4"] = _tab(sub, ["Outcome", "População", "Corte", "Especificação", "n abaixo / acima", "Salto", "IC 95%",
                            "p"], [oid, pop, corte, lambda r: r["especificacao"], nab, tau, ic,
                                   lambda r: _p(r["p_valor"])])
    # Estudo de evento: resumo por janela.
    e = ev[~ev["referencia"].astype(bool)].copy()
    linhas = ["| Outcome | População | Corte | Janela | Competências estimadas | p < 0,05 | maior abs(salto) | "
              "salto médio |", "|---|---|---|---|---|---|---|---|"]
    for (o, p_, c_, j), g in e.assign(_o=e["outcome_id"].map(ordem)).sort_values(
            ["_o", "populacao", "corte", "competencia"], kind="stable").groupby(
            ["outcome_id", "populacao", "corte", "janela"], sort=False):
        un = g["unidade"].iloc[0]
        cc, pp, _ = _escala(un)
        ok = g[np.isfinite(g["tau"].astype(float))]
        linhas.append(f"| {o} | {p_} | {str(c_).replace('.', ',')} | {j} | {len(ok)} | "
                      f"{int((ok['p_valor'] < 0.05).sum())} | {_n(ok['tau'].abs().max() if len(ok) else np.nan, cc, pp, sinal=False)} | "
                      f"{_n(ok['tau'].mean() if len(ok) else np.nan, cc, pp)} |")
    t["evento"] = "\n".join(linhas)
    # Entradas, validações e desvios.
    linhas = ["| Entrada | SHA-256 | Papel |", "|---|---|---|"]
    for b in resumo.get("entradas", []):
        linhas.append(f"| `{b['caminho']}` | `{b['sha256'][:16]}…` | {b['papel']} |")
    t["entradas"] = "\n".join(linhas)
    v = resumo.get("validacoes", {})
    q = resumo.get("contagens", {})
    lr = v.get("local_randomization", {}).get("janelas", {})
    t["validacoes"] = "\n".join([
        "| Conferência | Resultado |", "|---|---|",
        f"| SHA-256 do painel = manifesto a09 | {v.get('manifesto', {}).get('sha256_painel_igual_manifesto')} |",
        f"| painel: chave única e balanceado no universo a08 | {v.get('painel', {}).get('chave_unica')} / "
        f"{v.get('painel', {}).get('balanceado')} |",
        f"| municípios no universo U / V1 | {v.get('populacoes', {}).get('U_municipios')} / "
        f"{v.get('populacoes', {}).get('V1_municipios')} |",
        f"| U sem população 2022 | {len(v.get('populacoes', {}).get('U_sem_populacao_2022', []))} |",
        f"| DiRD painel = DiRD delta (todas as combinações por corte) | {v.get('identidade_painel_delta')} |",
        f"| seleção LR de V1 reproduz o E5 | {v.get('local_randomization', {}).get('V1_selecao_lr_reproduz_E5')} |",
        f"| seleção LR de U reproduz o E6 | {v.get('local_randomization', {}).get('U_selecao_lr_reproduz_E6')} |",
        f"| definição de horas SUS no manifesto a09 contém {TERMO_FILTRO_SUS} (§16) | "
        f"{TERMO_FILTRO_SUS in str(v.get('manifesto', {}).get('definicao_horas_sus_no_manifesto', ''))} |",
        "| janelas LR (± IVS) | " + "; ".join(f"{k}: {_n(w, 3, sinal=False) if w else 'nenhuma'}"
                                          for k, w in lr.items()) + " |",
        f"| linhas em E7_estimativas.csv / no protocolo | {q.get('linhas')} / {q.get('linhas_no_protocolo')} |",
        f"| linhas SEM_ESTIMATIVA / NAO_EXECUTADO | {q.get('sem_estimativa')} / {q.get('nao_executado')} |",
        f"| linhas em E7_estudo_evento.csv | {q.get('linhas_evento')} |",
    ])
    linhas = ["| Data | Tipo | Item | Descrição |", "|---|---|---|---|"]
    for dv in resumo.get("desvios", []):
        linhas.append(f"| {dv['data']} | {dv['tipo']} | {dv['item']} | {dv['descricao']} |")
    t["desvios"] = "\n".join(linhas)
    return t


MARCA = re.compile(r"(<!-- E7:(?P<nome>[A-Za-z0-9_]+):inicio -->\n)(?P<corpo>.*?)(\n<!-- E7:(?P=nome):fim -->)", re.S)


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
    est = pd.read_csv(OUT / NOME_EST, dtype={"corte": str})
    ev = pd.read_csv(OUT / NOME_EVENTO, dtype={"corte": str, "competencia": str})
    resumo = json.loads((OUT / NOME_RESUMO).read_text(encoding="utf-8"))
    return est, ev, resumo


def atualizar_doc() -> None:
    if not DOC43.exists():
        print(f"{rotulo(DOC43)} nao existe: tabelas nao gravadas")
        return
    est, ev, resumo = ler_saidas()
    DOC43.write_text(aplicar_tabelas_doc(DOC43.read_text(encoding="utf-8"), gerar_tabelas_doc(est, ev, resumo)),
                     encoding="utf-8")
    print(f"tabelas do doc 43 regravadas: {rotulo(DOC43)}")


# ---------------------------------------------------------------------------
# Execução
# ---------------------------------------------------------------------------

def ler_painel() -> pd.DataFrame:
    p = pd.read_parquet(PAINEL, columns=COLUNAS_PAINEL)
    p["co_ibge"] = p["co_ibge"].astype(str)
    p["competencia"] = p["competencia"].astype(str)
    p["grupo"] = p["grupo"].astype(str)
    return p


def entradas(info_s4: dict | None) -> list[dict]:
    blocos = [
        bloco_entrada(PAINEL, "painel CNES municipio x grupo de CBO x mes (F3)",
                      "CNES/DATASUS, base completa mensal (tarefa C, a09)", "competencias 202201-202608 (lista no a09)",
                      "universo a08", "municipio x competencia x grupo", "co_ibge, competencia, grupo",
                      f"grupos lidos: {', '.join(GRUPOS_USADOS)}; nenhuma competencia >= {LIMITE_CICLO3}"),
        bloco_entrada(MANIFESTO_A09, "manifesto do painel (SHA-256, competencias)", "a09", "2026-10-19 (execucao)",
                      "painel inteiro", "-", "-", "lidos: painel.sha256, competencias_nao_obtidas, natureza"),
        bloco_entrada(A08, "running variable (IVS 2010 oficial) e universo U", "Ipea, Plataforma IVS (a08)",
                      "Censo 2010", "municipios da malha 2010", "municipio", "co_ibge", "colunas co_ibge, ivs"),
        bloco_entrada(POP22, "denominador das taxas por 10 mil hab.", "IBGE, Censo 2022", "2022",
                      "municipios", "municipio", "co_ibge_6d", "coluna populacao_2022"),
        bloco_entrada(ARQ_VM, "lista de municipios de V1 (quadro do ciclo 1)", "tarefa B (12_construir_outcomes)",
                      "ciclo 1 (Edital 3/2025)", "V1-V3", "municipio x ciclo", "ciclo, co_ibge",
                      "ciclo == 1; colunas ciclo, co_ibge, ivs_2010_oficial (conferencia); nenhum outcome"),
        bloco_entrada(A10_IED, "S3: porte e estrato IED", "Portaria GM/MS 3.493/2024, Anexo VI (a10)",
                      "2024", "municipios do Anexo VI", "municipio", "co_ibge",
                      "colunas co_ibge, ivs_codigo_portaria, porte_codigo, estrato_ied"),
        bloco_entrada(PPF_ZIP, "S4: Amazonia Legal / faixa de fronteira", "MS, PMMB consolidado",
                      ", ".join((info_s4 or {}).get("dt_referencia", [])) or "2026-10-09", "linhas MUNICIPAL",
                      "municipio", "co_ibge", "nivel == MUNICIPAL; colunas co_ibge, amazonia_legal, faixa_fronteira, "
                      "dt_referencia (nenhuma vaga ou medico lido)"),
        bloco_entrada(TIPOLOGIA, "covariavel estrato da selecao da janela LR (regra do E5)", "tipologia A2",
                      "REGIC 2018; RM/RIDE 2022", "municipios", "municipio", "co_ibge_6d", "so a coluna estrato"),
        bloco_entrada(E5_SEL, "janela LR de V1 (E5, P1) para conferencia", "E5 (11_inferencia_alternativa)",
                      "2026-10-18", "P1/P2", "corte x janela", "populacao, corte, w", "populacao == P1"),
        *([bloco_entrada(E6_SEL, "janela LR de U (E6) para conferencia", "E6 (13_estimar_E6_funil)", "2026-10-18",
                         "U, G3, V1-V3", "corte x janela", "populacao, corte, w", "populacao == U")]
          if E6_SEL.exists() else []),
        bloco_entrada(PROTOCOLO_MD, "protocolo congelado (texto canonico)", "doc 40", "2026-10-18", "-", "-", "-",
                      "-"),
        bloco_entrada(PROTOCOLO_JSON, "protocolo congelado (maquina)", "protocolo_E6_multioutcome.json",
                      "2026-10-18", "-", "-", "-", "-"),
        bloco_entrada(AUD18, "datas das politicas nos mesmos cortes (marcas do estudo de evento)", "auditoria 18",
                      "2026-10-18", "-", "-", "-", "datas transcritas em DATAS_POLITICAS"),
        bloco_entrada(AUD01, "datas dos ciclos 1 e 2 do PMM-E", "auditoria 01 §7", "-", "-", "-", "-",
                      "datas transcritas em DATAS_POLITICAS"),
    ]
    return blocos


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--somente-validar", action="store_true",
                    help="so valida o esquema do painel e as populacoes (nada por lado de corte); nao grava nada")
    ap.add_argument("--atualizar-doc", action="store_true", help="so regrava as tabelas do doc 43 a partir das saidas")
    ap.add_argument("--n-perm", type=int, default=L.N_PERMUTACOES)
    args = ap.parse_args(argv)
    if args.atualizar_doc:
        atualizar_doc()
        return 0
    try:
        rv = ler_running_variable()
        pop = ler_populacao()
        pops, conf_pop = populacoes(rv, pop)
        manifesto = json.loads(MANIFESTO_A09.read_text(encoding="utf-8"))
        sha_painel = sha256(PAINEL)
        val_man = validar_manifesto(manifesto, sha_painel)
        painel = ler_painel()
        val_painel = validar_painel(painel, set(rv["co_ibge"]))
        if args.somente_validar:
            print(json.dumps(_nan_none({"manifesto": val_man, "painel": val_painel, "populacoes": conf_pop}),
                             ensure_ascii=False, indent=2))
            print("validacao de esquema concluida; nenhuma estimativa calculada")
            return 0
        sup = {"S3": carregar_s3()}
        s4, info_s4 = carregar_s4()
        sup["S4"] = s4
        lr, motivos_lr, conf_lr = selecao_janelas_lr(pops, args.n_perm)
        linhas, linhas_ev, info, bases, horas_branco = [], [], {}, {}, {}
        for spec in CATALOGO:
            for pop_nome in spec["pops"]:
                serie = serie_outcome(painel, spec, pops[pop_nome])
                nota_extra = ""
                if spec["tipo"] == "horas":
                    br = contar_horas_em_branco(painel, spec["grupo"], pops[pop_nome]["co_ibge"])
                    horas_branco[f"{spec['id']}|{pop_nome}"] = br
                    nota_extra = (f"vinculos com hora em branco nos meses do E7: {br['vinculos_em_branco_soma_nos_meses']} "
                                  f"(soma mes a mes), em {br['celulas_municipio_mes']} celulas municipio-mes de "
                                  f"{br['municipios']} municipios")
                ls, inf, base = estimar_outcome(spec, pop_nome, serie, sup=sup, lr=lr, motivos_lr=motivos_lr,
                                                nota_extra=nota_extra)
                linhas.extend(ls)
                info[f"{spec['id']}|{pop_nome}"] = inf
                linhas_ev.extend(estudo_evento(spec, pop_nome, serie))
                bases[(spec["id"], pop_nome)] = (spec, base)
    except FalhaValidacao as erro:
        print(f"FALHA DE VALIDACAO (nada gravado): {erro}", file=sys.stderr)
        return 2
    est = aplicar_bky(pd.DataFrame(linhas)[COLUNAS_SAIDA])
    ev = pd.DataFrame(linhas_ev)[COLUNAS_EVENTO]
    p2 = p2_de(est)
    OUT.mkdir(parents=True, exist_ok=True)
    est.to_csv(OUT / NOME_EST, index=False)
    ev.to_csv(OUT / NOME_EVENTO, index=False)
    figuras = gerar_figuras(bases, ev.astype({"corte": str}), OUT / DIR_FIG)
    horas = {k: {"janelas": v["notas_janelas"], "em_branco": horas_branco.get(k)} for k, v in info.items()
             if k.startswith("F3.3")}
    resumo = {
        "natureza_dos_dados": "EMPIRICO",
        "gerador": rotulo(Path(__file__)),
        "data_execucao": DATA_EXECUCAO,
        "protocolo": {"texto": rotulo(PROTOCOLO_MD), "sha256_texto": sha256(PROTOCOLO_MD),
                      "maquina": rotulo(PROTOCOLO_JSON), "sha256_maquina": sha256(PROTOCOLO_JSON),
                      "secoes": "§3, §4, §5 F3, §6 (painel CNES), §7 (P2), §13 (S2-S6), §16 (horas SUS)"},
        "contraste": {"dird": CONTRASTE_DIRD, "nivel": CONTRASTE_NIVEL},
        "parametros": {"cortes_mil": list(CORTES), "h_mil": H, "h_sensibilidade_mil": list(H_SENS),
                       "fatores_M": list(FATORES_M), "pre": list(COMP_PRE), "pos": list(COMP_POS), "ref": COMP_REF,
                       "placebo_a": list(COMP_PLACEBO_A), "placebo_b": list(COMP_PLACEBO_B),
                       "pre_extra": list(COMP_PRE_EXTRA), "evento": list(COMP_EVENTO),
                       "escala_taxa": "por 10 mil habitantes (Censo 2022)"},
        "datas_politicas": [{"data": d, "ato": r, "fonte": f, "marca_principal": p} for d, r, f, p in DATAS_POLITICAS],
        "outcomes": [{k: v for k, v in c.items()} for c in CATALOGO],
        "especificacoes": ESPECIFICACOES,
        "entradas": entradas(info_s4),
        "arquivo_proibido_nao_lido": ARQUIVO_PROIBIDO,
        "validacoes": {"manifesto": val_man, "painel": val_painel, "populacoes": conf_pop,
                       "identidade_painel_delta": True, "local_randomization": conf_lr,
                       "s3_portes_muda": {str(k): sorted(v) for k, v in sup["S3"].get("portes_muda", {}).items()},
                       "s4_definicao": s4.get("definicao"), "s4_info": info_s4,
                       "horas_ausentes": horas},
        "amostras": {k: {kk: vv for kk, vv in v.items() if kk != "notas_janelas"} | {"notas": v["notas_janelas"]}
                     for k, v in info.items()},
        "p2_para_holm": p2,
        "desvios": DESVIOS,
        "contagens": {"linhas": int(len(est)), "linhas_no_protocolo": int(est["no_protocolo"].sum()),
                      "sem_estimativa": int((est["status"] == "SEM_ESTIMATIVA").sum()),
                      "nao_executado": int((est["status"] == "NAO_EXECUTADO").sum()),
                      "linhas_bky": int(est["entra_bky"].sum()), "linhas_evento": int(len(ev))},
        "figuras": [f"{rotulo(OUT / DIR_FIG)}/{f}" for f in figuras],
        "saidas": [rotulo(OUT / NOME_EST), rotulo(OUT / NOME_EVENTO), rotulo(OUT / NOME_RESUMO)],
    }
    _gravar_json(OUT / NOME_RESUMO, resumo)
    atualizar_doc()
    print(f"E7: {len(est)} linhas de estimativas, {len(ev)} de estudo de evento; P2 p = {p2['p_valor']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
