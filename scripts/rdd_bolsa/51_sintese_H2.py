"""Síntese da H2 (banca 2): o médico escolhe perto da origem; a bolsa muda qual vaga ele escolhe, mas pesa menos que a origem.

Não reestima nada. Lê as saídas já auditadas da escolha (`G1_*`, `E9_*`, `P1_*`, `P1h_*`, `VC_*`, `VD_*`, `VL_*`) e o
`numeros_banca2.json` (só os descritivos `ESC_*`), copia os números que a análise usa para `H2_sintese.csv`, com a
fonte e o filtro de cada um, e calcula alguns números **descritivos novos** a partir das bases de escolha versionadas
(`output/rdd_bolsa/outcomes/escolhas_*` do script 12, `G1_*`, a malha de regiões de saúde e o IVS 2010 oficial do a08):

- onde fica a 1ª opção em relação à origem (mesma UF, mesma região de saúde, mesmo município; distância), por ciclo;
- a fração de 1ªs opções na UF de origem por faixa de bolsa da vaga escolhida;
- dentro da UF de origem, a bolsa média das vagas disponíveis contra a da vaga escolhida;
- dentro da UF de origem, perto de um corte de IVS (|IVS − corte| ≤ 0,050), a parte do lado de bolsa maior nas vagas
  disponíveis contra a parte nas 1ªs opções.

Tudo é `natureza_dos_dados = EMPIRICO`: nada sintético, nada imputado, nenhum cenário. O IVS vem só de
`output/aquisicao/a08_ivs_2010_oficial_municipio.csv`; o arquivo local de IVS errado nunca é lido (auditoria 16).

Saídas: `output/rdd_bolsa/H2_sintese.csv`, `H2_resumo.json` e `H2_figuras/` (F1 a F6). Com `--atualizar-doc`, regrava
os blocos `<!-- H2:... -->` de `docs/06_execucao/66_analise_completa_H2.md` a partir dessas saídas (o texto fora dos
blocos não é tocado). As saídas de origem não são regravadas.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import textwrap
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "rdd_bolsa"
FIG_DIR = OUT / "H2_figuras"
OUT_CSV = OUT / "H2_sintese.csv"
OUT_RESUMO = OUT / "H2_resumo.json"
DOC = ROOT / "docs" / "06_execucao" / "66_analise_completa_H2.md"

NATUREZA = "EMPIRICO"
ESTATUTO = "SINTESE_H2_POS_RESULTADO"
DATA = "2026-10-27"
SCRIPT_REL = "scripts/rdd_bolsa/51_sintese_H2.py"
TOL = 1e-8

# Saídas auditadas (só leitura).
G1_RESUMO = OUT / "G1_resumo.json"
G1_ORIGEM = OUT / "G1_candidatos_origem.parquet"
G1_DIST = OUT / "G1_distancias_opcoes.parquet"
E9_EST = OUT / "E9_estimativas.csv"
E9_RESUMO = OUT / "E9_resumo.json"
P1_RESUMO = OUT / "P1_resumo.json"
P1H_CSV = OUT / "P1h_magnitudes.csv"
VC_CSV = OUT / "VC_estimativas.csv"
VD_CSV = OUT / "VD_estimativas.csv"
VL_CSV = OUT / "VL_estimativas.csv"
VL_RESUMO = OUT / "VL_resumo.json"
NUM_BANCA2 = ROOT / "output" / "apresentacao_banca2" / "numeros_banca2.json"
# Bases de escolha versionadas (script 12) e auxiliares.
ESCOLHAS = OUT / "outcomes" / "escolhas_candidatos.parquet"
CONJUNTO = OUT / "outcomes" / "escolhas_conjunto_principal.parquet"
MALHA = ROOT / "output" / "aquisicao" / "malha_municipios_regioes_saude.parquet"
IVS_OFICIAL = ROOT / "output" / "aquisicao" / "a08_ivs_2010_oficial_municipio.csv"

CORTES_MIL = (300, 400)
JANELA_MIL = 50
REGRA_LIGACAO = "g1_cpf_nome"

ENTRADAS = [
    # (caminho, papel, data de referência, cobertura, unidade, chaves, filtros)
    (G1_RESUMO, "portão G1: candidatos, ligados e com município de origem", "2026-10-19", "ciclos 1–3",
     "ciclo", "taxas_ligacao.g1_cpf_nome.<ciclo>", "regra g1_cpf_nome"),
    (G1_ORIGEM, "município de origem do candidato no CNES (vínculo médico na competência anterior à inscrição)",
     "2026-10-19", "ciclos 1–3", "candidato", "ciclo, id_candidato", "regra g1_cpf_nome; co_ibge_origem preenchido"),
    (G1_DIST, "distância (km) da origem principal a cada opção ranqueada", "2026-10-19", "ciclos 1–3",
     "candidato × opção", "ciclo, id_candidato, opcao_rank", "opcao_rank = 1; distância preenchida"),
    (ESCOLHAS, "opções publicadas de cada candidato (script 12)", "2026-10-18", "1ª chamada dos ciclos 1–3",
     "candidato × opção", "ciclo, id_candidato, opcao_rank", "opcao_rank = 1"),
    (CONJUNTO, "conjunto de escolha principal: vagas (CNES × curso) abertas por curso e ciclo (script 12)",
     "2026-10-18", "1ª chamada dos ciclos 1–3", "célula CNES × curso × ciclo", "id_conjunto_escolha, co_cnes_7d",
     "células com IVS 2010 oficial"),
    (MALHA, "UF e região de saúde do município (só as colunas co_ibge_6d, sg_uf, no_regiao_saude)", "2026-09",
     "5.565 municípios", "município", "co_ibge_6d", "nenhum; a coluna de IVS da malha não é usada"),
    (IVS_OFICIAL, "IVS 2010 oficial do IPEA (running variable canônica)", "2010", "municípios com IVS 2010",
     "município", "co_ibge", "só a coluna ivs"),
    (E9_EST, "E9: logit condicional sem distância; robustez com spline cúbico (quadro do ciclo 2 de 19/03)",
     "2026-10-18", "ciclos 1–3", "termo × especificação", "especificacao, ciclo, conjunto, modelo, termo", "termo bolsa_mil"),
    (E9_RESUMO, "E9: mapa faixa → bolsa (R$ mil/mês)", "2026-10-18", "editais 2025 e 2026", "faixa",
     "mapa_faixa_bolsa", "nenhum"),
    (P1_RESUMO, "P1: amostra do modelo de escolha com origem (M1)", "2026-10-19", "ciclos 1–3", "ciclo",
     "amostra", "nenhum"),
    (P1H_CSV, "P1h: D_UF com o quadro do ciclo 2 de 19/03 (versão antiga, referência)", "2026-10-26",
     "ciclos 1–3", "linha × modelo", "id_linha, modelo", "P1h-1, M1"),
    (VC_CSV, "adendo 52c: M1 e M5 com o tipo de vaga do ciclo 2 de 13/02 (versão de referência)", "2026-10-26",
     "ciclos 1–3", "termo × modelo × versão", "versao, chave_modelo, tipo_linha, termo", "versao corrigida_13fev"),
    (VD_CSV, "adendo 52d: M2, M4, M7, M8, M9 e D_UF com o quadro de 13/02", "2026-10-26", "ciclos 1–3",
     "termo × modelo × versão", "id_vd, versao, chave_modelo, tipo_linha, termo", "versao corrigida_13fev"),
    (VL_CSV, "adendo 52e: efeito fixo do par de UFs (VL-1), comparação local (VL-2), VL-3, km (VL-4), M1 e M4",
     "2026-10-27", "ciclos 1–3 e ciclo 2", "termo × modelo", "chave_modelo, tipo_linha, termo", "nenhum"),
    (VL_RESUMO, "adendo 52e: contagens de identificação do VL-1", "2026-10-27", "ciclos 1–3 e ciclo 2",
     "modelo", "identificacao.<chave>", "nenhum"),
    (NUM_BANCA2, "descritivos ESC_* da banca 2 (fonte dos 79%; gerado fora do run_all por "
     "scripts/apresentacao/gerar_figuras_banca2.py)", "2026-10-27", "ciclos 1–3", "número", "numeros.<id>",
     "só ESC_*"),
]
# numeros_banca2.json é reconstruído por outro script (deck da banca 2): o teste confere os valores ESC_*, não o hash.
ENTRADA_SO_VALORES = {NUM_BANCA2}

DOCS = {"57x": "docs/06_execucao/57x_resultados_escolha_localizacao_par.md",
        "57p": "docs/06_execucao/57p_escolha_vaga_imediata_c2.md",
        "57v": "docs/06_execucao/57v_sensibilidades_ciclo2_quadro_1302.md",
        "57i": "docs/06_execucao/57i_resultados_P1h_magnitudes.md",
        "57a": "docs/06_execucao/57a_resultados_P1_escolha.md",
        "42": "docs/06_execucao/42_resultados_E9_escolha.md",
        "G1": "docs/auditorias/G1_viabilidade_candidatos.md",
        "banca2": "docs/07_apresentacoes/banca2/02_conteudo_slides.md",
        "66": "docs/06_execucao/66_analise_completa_H2.md"}


def rel(p: Path) -> str:
    return p.resolve().relative_to(ROOT).as_posix()


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Escrita: só nos alvos deste script
# ---------------------------------------------------------------------------

def _alvo_permitido(caminho: Path) -> bool:
    c = caminho.resolve()
    return (c in {OUT_CSV.resolve(), OUT_RESUMO.resolve(), DOC.resolve()}
            or (c.parent == FIG_DIR.resolve() and c.name.startswith("H2_") and c.suffix == ".png"))


def gravar_texto(caminho: Path, texto: str) -> None:
    if not _alvo_permitido(caminho):
        raise AssertionError(f"escrita fora dos alvos do script 51: {caminho}")
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8")


def gravar_figura(fig, caminho: Path) -> None:
    if not _alvo_permitido(caminho):
        raise AssertionError(f"escrita fora dos alvos do script 51: {caminho}")
    caminho.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(caminho, dpi=150, metadata={"Software": None})


# ---------------------------------------------------------------------------
# Números copiados das saídas auditadas
# ---------------------------------------------------------------------------

def _t(arquivo, filtro, rotulo, quantidade, ciclo, grupo, doc, auditoria, *, est="estimativa", inf="ic95_inf",
       sup="ic95_sup", p="p", padj=None, tipo_ajuste="", pscore=None, transf="identidade", principal=False,
       versao_quadro_c2="13/02/2026") -> dict:
    return dict(arquivo=arquivo, filtro=filtro, rotulo=rotulo, quantidade=quantidade, ciclo=ciclo, grupo=grupo,
                doc=doc, auditoria=auditoria, est=est, inf=inf, sup=sup, p=p, padj=padj, tipo_ajuste=tipo_ajuste,
                pscore=pscore, transf=transf, principal=principal, versao_quadro_c2=versao_quadro_c2)


def _vl(chave, tipo="razao_chances_por_5mil", termo="bolsa_mil"):
    return {"chave_modelo": chave, "tipo_linha": tipo, "termo": termo}


def _vc(chave, tipo, termo, versao="corrigida_13fev"):
    return {"versao": versao, "chave_modelo": chave, "tipo_linha": tipo, "termo": termo}


def _vd(chave, tipo, termo):
    return {"versao": "corrigida_13fev", "chave_modelo": chave, "tipo_linha": tipo, "termo": termo}


def _e9cub(ciclo):
    return {"especificacao": "ROBUSTEZ_POS_AUDITORIA:spline_cubico__bolsa_linear", "ciclo": ciclo,
            "conjunto": "principal", "modelo": "logit_condicional_1a_opcao", "termo": "bolsa_mil"}


RC, DU = "razao_chances_por_5mil", "D_UF"
VL, VC, VD = "output/rdd_bolsa/VL_estimativas.csv", "output/rdd_bolsa/VC_estimativas.csv", "output/rdd_bolsa/VD_estimativas.csv"
DUF_T = "D_UF = θ_UF − 10·β"

TABELAS = {
    # Razão de chances da 1ª opção por +R$ 5 mil
    "OR_M1_EMP": _t(VL, _vl("M1_emp"), "M1 (base), ciclos 1–3", RC, "1–3", "bolsa", "57x §4.1", "48"),
    "OR_M1_C2": _t(VL, _vl("M1_c2"), "M1 (base), ciclo 2", RC, "2", "bolsa", "57x §4.1", "48"),
    "OR_M5_C1": _t(VC, _vc("M5_1", RC, "bolsa_mil"), "M1 (base), ciclo 1", RC, "1", "bolsa", "57p §4.1", "41"),
    "OR_M5_C3": _t(VC, _vc("M5_3", RC, "bolsa_mil"), "M1 (base), ciclo 3", RC, "3", "bolsa", "57p §4.1", "41"),
    "OR_VL1_EMP": _t(VL, _vl("VL1_emp"), "VL-1: mesma UF (par de UFs), ciclos 1–3", RC, "1–3", "bolsa", "57x §4.1",
                     "48", padj="p_holm", tipo_ajuste="Holm (3 principais do 52e)", pscore="p_score_rademacher",
                     principal=True),
    "OR_VL1_C2": _t(VL, _vl("VL1_c2"), "VL-1: mesma UF (par de UFs), ciclo 2", RC, "2", "bolsa", "57x §4.1", "48",
                    padj="p_holm", tipo_ajuste="Holm (3 principais do 52e)", pscore="p_score_rademacher"),
    "OR_VL2_EMP": _t(VL, _vl("VL2_emp"), "VL-2: mesma UF, só vagas perto do corte, ciclos 1–3", RC, "1–3", "bolsa",
                     "57x §4.1", "48", padj="p_holm", tipo_ajuste="Holm (3 principais do 52e)",
                     pscore="p_score_rademacher"),
    "OR_VL2_C2": _t(VL, _vl("VL2_c2"), "VL-2: mesma UF, só vagas perto do corte, ciclo 2", RC, "2", "bolsa",
                    "57x §4.2", "48", padj="q_bky", tipo_ajuste="BKY (7 secundárias do 52e)"),
    "OR_VL3_VL1_EMP": _t(VL, _vl("VL3_VL1_emp"), "VL-3: região de saúde de origem × UF da vaga, ciclos 1–3", RC,
                         "1–3", "bolsa", "57x §4.2", "48", padj="q_bky", tipo_ajuste="BKY (7 secundárias do 52e)"),
    "OR_VL3_VL1_C2": _t(VL, _vl("VL3_VL1_c2"), "VL-3: região de saúde de origem × UF da vaga, ciclo 2", RC, "2",
                        "bolsa", "57x §4.2", "48", padj="q_bky", tipo_ajuste="BKY (7 secundárias do 52e)"),
    "OR_VL3_VL2_EMP": _t(VL, _vl("VL3_VL2_emp"), "VL-3 perto do corte, ciclos 1–3", RC, "1–3", "bolsa", "57x §4.2",
                         "48", padj="q_bky", tipo_ajuste="BKY (7 secundárias do 52e)"),
    "OR_VL3_VL2_C2": _t(VL, _vl("VL3_VL2_c2"), "VL-3 perto do corte, ciclo 2", RC, "2", "bolsa", "57x §4.2", "48",
                        padj="q_bky", tipo_ajuste="BKY (7 secundárias do 52e)"),
    "OR_VL1LOG_EMP": _t(VL, _vl("VL1log_emp"), "VL-1 com log da distância, ciclos 1–3", RC, "1–3", "bolsa",
                        "57x §4.2", "48", padj="q_bky", tipo_ajuste="BKY (7 secundárias do 52e)"),
    "OR_VL1LOG_C2": _t(VL, _vl("VL1log_c2"), "VL-1 com log da distância, ciclo 2", RC, "2", "bolsa", "57x §4.2",
                       "48", padj="q_bky", tipo_ajuste="BKY (7 secundárias do 52e)"),
    "OR_M4_EMP": _t(VL, _vl("M4_emp"), "M4: efeito fixo de UF da vaga, ciclos 1–3", RC, "1–3", "bolsa", "57x §4.2",
                    "48"),
    "OR_M4_C2": _t(VL, _vl("M4_c2"), "M4: efeito fixo de UF da vaga, ciclo 2", RC, "2", "bolsa", "57x §4.2", "48"),
    "OR_M2_EMP": _t(VD, _vd("M2", RC, "bolsa_mil"), "M2: log da distância, ciclos 1–3", RC, "1–3", "bolsa",
                    "57v §5", "46"),
    "OR_M7_EMP": _t(VD, _vd("M7", RC, "bolsa_mil"), "M7: logit explodido (1ª e 2ª opção), ciclos 1–3", RC, "1–3",
                    "bolsa", "57v §5", "46"),
    "OR_M8_EMP": _t(VD, _vd("M8", RC, "media_bolsa_mil"), "M8: logit misto (média), ciclos 1–3", RC, "1–3", "bolsa",
                    "57v §5", "46"),
    "OR_M9_EMP": _t(VD, _vd("M9", RC, "bolsa_mil"), "M9: logit aninhado por região de saúde, ciclos 1–3", RC, "1–3",
                    "bolsa", "57v §5", "46"),
    "OR_E9_EMP": _t(VC, _vc("E9_emp", RC, "bolsa_mil"), "E9: sem origem nem distância, ciclos 1–3", RC, "1–3",
                    "bolsa", "57p §4.1", "41"),
    "OR_E9_C2": _t(VC, _vc("E9_2", RC, "bolsa_mil"), "E9: sem origem nem distância, ciclo 2", RC, "2", "bolsa",
                   "57p §4.1", "41"),
    "OR_E9CUB_EMP": _t("output/rdd_bolsa/E9_estimativas.csv", _e9cub("empilhado"),
                       "E9 com spline cúbico do IVS, ciclos 1–3", RC, "1–3", "bolsa", "42 §5.2", "E9 (doc 42 §5)",
                       est="coef", transf="exp5", versao_quadro_c2="19/03/2026"),
    "OR_E9CUB_C2": _t("output/rdd_bolsa/E9_estimativas.csv", _e9cub("2"), "E9 com spline cúbico do IVS, ciclo 2", RC,
                      "2", "bolsa", "42 §5.2", "E9 (doc 42 §5)", est="coef", transf="exp5",
                      versao_quadro_c2="19/03/2026"),
    # Diferença de log da razão de chances contra o M1 (sanduíche conjunto, 52e decisão 10)
    "DIF_VL1_EMP": _t(VL, _vl("VL1_emp", "diferenca_log_rc_contra_referencia"), "VL-1 − M1, ciclos 1–3",
                      "diferenca_log_rc", "1–3", "bolsa", "57x §4.1", "48"),
    "DIF_VL1_C2": _t(VL, _vl("VL1_c2", "diferenca_log_rc_contra_referencia"), "VL-1 − M1, ciclo 2",
                     "diferenca_log_rc", "2", "bolsa", "57x §4.1", "48"),
    "DIF_VL2_EMP": _t(VL, _vl("VL2_emp", "diferenca_log_rc_contra_referencia"), "VL-2 − M1, ciclos 1–3",
                      "diferenca_log_rc", "1–3", "bolsa", "57x §4.1", "48"),
    # β (por R$ 1 mil) na especificação pré-registrada
    "BETA_M1_EMP": _t(VC, _vc("M1", "coeficiente", "bolsa_mil"), "β do M1 (pré-registrado, P1a), ciclos 1–3",
                      "coeficiente", "1–3", "bolsa", "57p §4.1", "41", padj="p_holm",
                      tipo_ajuste="Holm (família de um teste, P1a)"),
    "BETA_VL1_EMP": _t(VL, _vl("VL1_emp", "coeficiente"), "β do VL-1, ciclos 1–3", "coeficiente", "1–3", "bolsa",
                       "57x §4.4", "48"),
    # D_UF = θ_UF − 10·β e os dois pesos
    "DUF_M1": _t(VC, _vc("M1", DU, DUF_T), "D_UF no M1 (P1h-1), ciclos 1–3", "D_UF", "1–3", "origem", "57p §4.2",
                 "41", p="p_unilateral", padj="p_holm", tipo_ajuste="Holm (família de um teste, P1h-1)",
                 principal=True),
    "DUF_M5_C1": _t(VC, _vc("M5_1", DU, DUF_T), "D_UF no M1 só do ciclo 1", "D_UF", "1", "origem", "57p §4.2",
                    "41", p="p_unilateral"),
    "DUF_M5_C2": _t(VC, _vc("M5_2", DU, DUF_T), "D_UF no M1 só do ciclo 2", "D_UF", "2", "origem", "57p §4.2",
                    "41", p="p_unilateral"),
    "DUF_M5_C3": _t(VC, _vc("M5_3", DU, DUF_T), "D_UF no M1 só do ciclo 3", "D_UF", "3", "origem", "57p §4.2",
                    "41", p="p_unilateral"),
    "DUF_M2": _t(VD, _vd("M2", DU, "D_UF"), "D_UF no M2 (log da distância)", "D_UF", "1–3", "origem", "57v §5.6",
                 "46", p=None, padj="q_bky", tipo_ajuste="BKY (6 sensibilidades P1h-3)"),
    "DUF_M4": _t(VD, _vd("M4", DU, "D_UF"), "D_UF no M4 (efeito fixo de UF da vaga)", "D_UF", "1–3", "origem",
                 "57v §5.6", "46", p=None, padj="q_bky", tipo_ajuste="BKY (6 sensibilidades P1h-3)"),
    "DUF_M7": _t(VD, _vd("M7", DU, "D_UF"), "D_UF no M7 (logit explodido)", "D_UF", "1–3", "origem", "57v §5.6",
                 "46", p=None, padj="q_bky", tipo_ajuste="BKY (6 sensibilidades P1h-3)"),
    "DUF_M1_ANTIGA": _t("output/rdd_bolsa/P1h_magnitudes.csv", {"id_linha": "P1h-1", "modelo": "M1"},
                        "D_UF no M1, quadro de 19/03 (antiga)", "D_UF", "1–3", "origem",
                        "57i §4", "31", p="p_unilateral", padj="p_holm", tipo_ajuste="Holm (família de um teste)",
                        versao_quadro_c2="19/03/2026"),
    "THETA_UF_M1": _t(VC, _vc("M1", "coeficiente", "mesma_uf"), "θ_UF: vaga na UF de origem, ciclos 1–3",
                      "coeficiente", "1–3", "origem", "57p §4.3", "41"),
    "BOLSA10_M1": _t(VC, _vc("M1", "coeficiente", "bolsa_mil"), "10·β: toda a bolsa (R$ 10 → 20 mil), ciclos 1–3",
                     "coeficiente_x10", "1–3", "origem", "57p §4.1", "41", p=None, transf="vezes10"),
    "THETA_UF_C2": _t(VC, _vc("M5_2", "coeficiente", "mesma_uf"), "θ_UF: vaga na UF de origem, ciclo 2",
                      "coeficiente", "2", "origem", "57p §4.3", "41"),
    "BOLSA10_C2": _t(VC, _vc("M5_2", "coeficiente", "bolsa_mil"), "10·β: toda a bolsa (R$ 10 → 20 mil), ciclo 2",
                     "coeficiente_x10", "2", "origem", "57p §4.1", "41", p=None, transf="vezes10"),
    "BOLSA10_VL1_EMP": _t(VL, _vl("VL1_emp", "coeficiente"), "10·β do VL-1 (mesma UF), ciclos 1–3",
                          "coeficiente_x10", "1–3", "origem", "57x §4.4", "48", p=None, transf="vezes10"),
    # Distância e km equivalentes
    "GAMA_M1_EMP": _t(VC, _vc("M1", "coeficiente", "distancia_100km"), "peso de 100 km a mais no M1, ciclos 1–3",
                      "coeficiente", "1–3", "km", "57x §4.4", "48"),
    "GAMA_VL1_EMP": _t(VL, _vl("VL1_emp", "coeficiente", "distancia_100km"),
                       "peso de 100 km a mais no VL-1, ciclos 1–3", "coeficiente", "1–3", "km", "57x §4.4", "48"),
    "K5_M1_EMP": _t(VL, _vl("M1_emp", "km_equivalentes", "K5"), "+R$ 5 mil em km, M1, ciclos 1–3", "km", "1–3",
                    "km", "57x §4.3; 57v §5.6", "48", p=None),
    "K5_M1_C2": _t(VL, _vl("M1_c2", "km_equivalentes", "K5"), "+R$ 5 mil em km, M1, ciclo 2", "km", "2", "km",
                   "57x §4.3", "48", p=None),
    "K5_VL1_EMP": _t(VL, _vl("VL1_emp", "km_equivalentes", "K5"), "+R$ 5 mil em km, mesma UF (VL-1), ciclos 1–3",
                     "km", "1–3", "km", "57x §4.3", "48", p=None),
    "K5_VL1_C2": _t(VL, _vl("VL1_c2", "km_equivalentes", "K5"), "+R$ 5 mil em km, mesma UF (VL-1), ciclo 2", "km",
                    "2", "km", "57x §4.3", "48", p=None),
}

# Números lidos de JSON: (arquivo, caminho, rótulo, ciclo, grupo, doc, auditoria)
JSONS = {
    **{(f"G1_CAND_EMP" if c == "EMP" else f"G1_CAND_C{c}"): ("output/rdd_bolsa/G1_resumo.json", ["taxas_ligacao", REGRA_LIGACAO, k, "candidatos"],
                         f"candidatos no portão G1, {r}", "1–3" if c == "EMP" else c, "amostra", "G1 §4", "G1")
       for c, k, r in (("1", "1", "ciclo 1"), ("2", "2", "ciclo 2"), ("3", "3", "ciclo 3"), ("EMP", "total", "total"))},
    **{(f"G1_LIG_EMP" if c == "EMP" else f"G1_LIG_C{c}"): ("output/rdd_bolsa/G1_resumo.json", ["taxas_ligacao", REGRA_LIGACAO, k, "ligados"],
                        f"ligados ao CNES, {r}", "1–3" if c == "EMP" else c, "amostra", "G1 §4", "G1")
       for c, k, r in (("1", "1", "ciclo 1"), ("2", "2", "ciclo 2"), ("3", "3", "ciclo 3"), ("EMP", "total", "total"))},
    **{(f"G1_ORIG_EMP" if c == "EMP" else f"G1_ORIG_C{c}"): ("output/rdd_bolsa/G1_resumo.json",
                         ["taxas_ligacao", REGRA_LIGACAO, k, "ligados_com_municipio_de_origem"],
                         f"ligados com município de origem, {r}", "1–3" if c == "EMP" else c, "amostra", "G1 §4", "G1")
       for c, k, r in (("1", "1", "ciclo 1"), ("2", "2", "ciclo 2"), ("3", "3", "ciclo 3"), ("EMP", "total", "total"))},
    **{f"P1_R1_C{c}": ("output/rdd_bolsa/P1_resumo.json", ["amostra", "r1_por_ciclo", c],
                       f"candidatos com linha de 1ª opção, ciclo {c}", c, "amostra", "57a §2", "26")
       for c in ("1", "2", "3")},
    **{f"P1_N_C{c}": ("output/rdd_bolsa/P1_resumo.json", ["amostra", "p1_por_ciclo", c],
                      f"amostra do modelo de escolha (P1), ciclo {c}", c, "amostra", "57a §2", "26")
       for c in ("1", "2", "3")},
    "P1_LINHAS": ("output/rdd_bolsa/P1_resumo.json", ["amostra", "linhas_m1"], "linhas candidato × vaga no M1",
                  "1–3", "amostra", "57a §2", "26"),
    "P1_CONJ": ("output/rdd_bolsa/P1_resumo.json", ["amostra", "conjuntos_m1"], "conjuntos de escolha (curso × ciclo)",
                "1–3", "amostra", "57a §2", "26"),
    "P1_CELULAS": ("output/rdd_bolsa/P1_resumo.json", ["amostra", "celulas_p1"], "vagas (células) no conjunto do P1",
                   "1–3", "amostra", "57a §2", "26"),
    **{f"VL1_{k.upper()}": ("output/rdd_bolsa/VL_resumo.json", ["identificacao", "VL1_emp", "identificacao", k], r,
                            "1–3", "identificacao", "57x §3", "48")
       for k, r in (("candidatos_no_modelo", "candidatos no VL-1"),
                    ("pares_com_escolha", "pares (UF de origem, UF da vaga) com alguma escolha"),
                    ("pares_com_variacao_de_bolsa", "pares com vagas de bolsas diferentes"),
                    ("origens_com_algum_par_com_variacao", "UFs de origem com algum par com variação de bolsa"),
                    ("candidatos_com_variacao_de_bolsa_em_algum_par", "candidatos que veem bolsas diferentes dentro de uma UF"),
                    ("candidatos_com_1a_opcao_em_par_com_variacao", "candidatos com a 1ª opção num par com variação"))},
    **{f"ESC_{k}": ("output/apresentacao_banca2/numeros_banca2.json", ["numeros", f"ESC_{k}", "valor_bruto"], r,
                    "1–3", "descritiva", "doc 02 da banca 2; auditoria 50 (A8)", "50")
       for k, r in (("N", "candidatos com 1ª opção e origem no G1"), ("UF", "1ª opção na UF de origem (fração)"),
                    ("REG", "1ª opção na região de saúde de origem (fração)"),
                    ("MUN", "1ª opção no município de origem (fração)"),
                    ("DIST_P50", "distância origem → 1ª opção: mediana (km)"),
                    ("DIST_P75", "distância origem → 1ª opção: 3º quartil (km)"))},
}

COLUNAS = ["natureza_dos_dados", "estatuto", "id", "origem_numero", "grupo", "rotulo", "quantidade", "ciclo",
           "estimativa", "ic95_inf", "ic95_sup", "p", "p_ajustado", "tipo_ajuste", "p_score_rademacher",
           "n_candidatos", "principal", "versao_quadro_ciclo2", "transformacao", "fonte_arquivo", "fonte_filtro",
           "fonte_colunas", "doc_origem", "auditoria"]


def _transf(x, t: str) -> float:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return float("nan")
    x = float(x)
    if t == "identidade":
        return x
    if t == "exp5":
        return math.exp(5.0 * x)
    if t == "vezes10":
        return 10.0 * x
    raise AssertionError(f"transformação desconhecida: {t}")


def selecionar(df: pd.DataFrame, filtro: dict) -> pd.Series:
    m = pd.Series(True, index=df.index)
    for k, v in filtro.items():
        m &= df[k].astype(str) == str(v)
    sel = df[m]
    if len(sel) != 1:
        raise AssertionError(f"filtro {filtro} seleciona {len(sel)} linhas")
    return sel.iloc[0]


def _json_caminho(obj, caminho):
    for k in caminho:
        obj = obj[k]
    return obj


def linhas_auditadas() -> list[dict]:
    cache: dict[str, pd.DataFrame] = {}
    out = []
    for id_, s in TABELAS.items():
        if s["arquivo"] not in cache:
            df = pd.read_csv(ROOT / s["arquivo"], dtype={"ciclo": str})
            if set(df["natureza_dos_dados"]) != {NATUREZA}:
                raise AssertionError(f"{s['arquivo']} com linha não EMPIRICO")
            cache[s["arquivo"]] = df
        r = selecionar(cache[s["arquivo"]], s["filtro"])
        g = lambda col: float(r[col]) if col else float("nan")  # noqa: E731
        n = r.get("n_candidatos", float("nan"))
        out.append({
            "natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "id": id_, "origem_numero": "SAIDA_AUDITADA",
            "grupo": s["grupo"], "rotulo": s["rotulo"], "quantidade": s["quantidade"], "ciclo": s["ciclo"],
            "estimativa": _transf(g(s["est"]), s["transf"]), "ic95_inf": _transf(g(s["inf"]), s["transf"]),
            "ic95_sup": _transf(g(s["sup"]), s["transf"]), "p": g(s["p"]), "p_ajustado": g(s["padj"]),
            "tipo_ajuste": s["tipo_ajuste"], "p_score_rademacher": g(s["pscore"]),
            "n_candidatos": float(n) if pd.notna(n) else float("nan"), "principal": bool(s["principal"]),
            "versao_quadro_ciclo2": s["versao_quadro_c2"], "transformacao": s["transf"],
            "fonte_arquivo": s["arquivo"], "fonte_filtro": json.dumps(s["filtro"], ensure_ascii=False, sort_keys=True),
            "fonte_colunas": json.dumps({k: s[k] for k in ("est", "inf", "sup", "p", "padj", "pscore")},
                                        ensure_ascii=False, sort_keys=True),
            "doc_origem": s["doc"], "auditoria": s["auditoria"]})
    for id_, (arq, caminho, rotulo, ciclo, grupo, doc, aud) in JSONS.items():
        obj = json.loads((ROOT / arq).read_text(encoding="utf-8"))
        if arq.endswith("numeros_banca2.json"):
            item = obj["numeros"][caminho[1]]
            if item.get("natureza") != NATUREZA:
                raise AssertionError(f"{caminho[1]} não EMPIRICO")
        v = float(_json_caminho(obj, caminho))
        out.append({
            "natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "id": id_, "origem_numero": "SAIDA_AUDITADA",
            "grupo": grupo, "rotulo": rotulo, "quantidade": "contagem" if "fração" not in rotulo and "km" not in rotulo
            else ("fracao" if "fração" in rotulo else "km"), "ciclo": ciclo, "estimativa": v,
            "ic95_inf": float("nan"), "ic95_sup": float("nan"), "p": float("nan"), "p_ajustado": float("nan"),
            "tipo_ajuste": "", "p_score_rademacher": float("nan"), "n_candidatos": float("nan"), "principal": False,
            "versao_quadro_ciclo2": "", "transformacao": "identidade", "fonte_arquivo": arq,
            "fonte_filtro": json.dumps({"caminho": caminho}, ensure_ascii=False), "fonte_colunas": "",
            "doc_origem": doc, "auditoria": aud})
    return out


# ---------------------------------------------------------------------------
# Descritivos novos (bases de escolha versionadas)
# ---------------------------------------------------------------------------

def base_descritiva() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """1ª opção de cada candidato com origem no G1 e distância; e o conjunto de vagas com UF, IVS e bolsa."""
    esc = pd.read_parquet(ESCOLHAS)
    conj = pd.read_parquet(CONJUNTO)
    org = pd.read_parquet(G1_ORIGEM)
    dist = pd.read_parquet(G1_DIST)
    for nome, d in (("escolhas", esc), ("conjunto", conj), ("G1 origem", org), ("G1 distância", dist)):
        if set(d["natureza_dos_dados"]) != {NATUREZA}:
            raise AssertionError(f"{nome} com linha não EMPIRICO")
    mapa = json.loads(E9_RESUMO.read_text(encoding="utf-8"))["mapa_faixa_bolsa"]["mapa_faixa_para_bolsa_mil"]
    ivs = pd.read_csv(IVS_OFICIAL, dtype={"co_ibge": str}, usecols=["co_ibge", "ivs"]).set_index("co_ibge")["ivs"]
    mal = pd.read_parquet(MALHA, columns=["co_ibge_6d", "sg_uf", "no_regiao_saude"])
    regiao = (mal["sg_uf"] + "|" + mal["no_regiao_saude"]).set_axis(mal["co_ibge_6d"].astype(str))

    o = org[(org["regra_ligacao"] == REGRA_LIGACAO) & org["co_ibge_origem"].notna()]
    o = o[["ciclo", "id_candidato", "co_ibge_origem"]].astype({"co_ibge_origem": str})
    d1 = dist[(dist["regra_ligacao"] == REGRA_LIGACAO) & (dist["opcao_rank"] == 1)
              & dist["dist_km_origem_principal"].notna()][["ciclo", "id_candidato", "co_ibge_opcao",
                                                           "dist_km_origem_principal"]]
    e1 = esc[esc["opcao_rank"] == 1][["ciclo", "id_candidato", "id_conjunto_escolha", "co_cnes_7d", "co_ibge",
                                      "faixa_anunciada"]]
    b = e1.merge(o, on=["ciclo", "id_candidato"], how="inner", validate="one_to_one")
    b = b.merge(d1, on=["ciclo", "id_candidato"], how="inner", validate="one_to_one")
    if (b["co_ibge_opcao"].astype(str) != b["co_ibge"].astype(str)).any():
        raise AssertionError("município da 1ª opção difere entre escolhas e G1_distancias")
    b["reg_origem"] = b["co_ibge_origem"].map(regiao)
    b["reg_vaga"] = b["co_ibge"].astype(str).map(regiao)
    if b[["reg_origem", "reg_vaga"]].isna().any().any():
        raise AssertionError("município sem região de saúde na malha")
    b["uf_origem"] = b["co_ibge_origem"].str[:2]
    b["uf_vaga"] = b["co_ibge"].astype(str).str[:2]
    b["mesma_uf"] = b["uf_origem"] == b["uf_vaga"]
    b["mesma_regiao"] = b["reg_origem"] == b["reg_vaga"]
    b["mesmo_municipio"] = b["co_ibge_origem"] == b["co_ibge"].astype(str)
    b["bolsa_mil"] = b["faixa_anunciada"].map(mapa).astype(float)
    b["s_mil"] = np.round(b["co_ibge"].astype(str).map(ivs).to_numpy() * 1000.0)

    c = conj[["ciclo", "id_conjunto_escolha", "co_cnes_7d", "co_ibge", "faixa_anunciada"]].copy()
    c["uf_vaga"] = c["co_ibge"].astype(str).str[:2]
    c["s_mil"] = np.round(c["co_ibge"].astype(str).map(ivs).to_numpy() * 1000.0)
    sem_ivs = int(c["s_mil"].isna().sum())
    c = c[c["s_mil"].notna()].copy()
    c["bolsa_mil"] = c["faixa_anunciada"].map(mapa).astype(float)
    regra = np.where(c["s_mil"] > CORTES_MIL[1], "FAIXA 1", np.where(c["s_mil"] > CORTES_MIL[0], "FAIXA 2", "FAIXA 3"))
    if (regra != c["faixa_anunciada"].to_numpy()).any():
        raise AssertionError("faixa impressa difere da regra do IVS oficial no conjunto")
    diag = {"candidatos_1a_opcao": int(len(e1)), "com_origem_e_distancia": int(len(b)),
            "celulas_conjunto": int(len(conj)), "celulas_sem_ivs_retiradas": sem_ivs, "mapa_faixa_bolsa_mil": mapa}
    return b, c, diag


def _por_ciclo(b: pd.DataFrame):
    yield "1–3", b
    for k in (1, 2, 3):
        yield str(k), b[b["ciclo"] == k]


def descritivas() -> tuple[list[dict], dict, pd.DataFrame]:
    b, c, diag = base_descritiva()
    linhas: list[dict] = []
    fontes = [rel(p) for p in (ESCOLHAS, G1_ORIGEM, G1_DIST, MALHA)]

    def add(id_, rotulo, quantidade, ciclo, v, n, fontes_=fontes, grupo="descritiva"):
        linhas.append({"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "id": id_,
                       "origem_numero": "DESCRITIVO_NOVO", "grupo": grupo, "rotulo": rotulo, "quantidade": quantidade,
                       "ciclo": ciclo, "estimativa": float(v), "ic95_inf": float("nan"), "ic95_sup": float("nan"),
                       "p": float("nan"), "p_ajustado": float("nan"), "tipo_ajuste": "",
                       "p_score_rademacher": float("nan"), "n_candidatos": float(n), "principal": False,
                       "versao_quadro_ciclo2": "", "transformacao": "identidade",
                       "fonte_arquivo": "; ".join(fontes_), "fonte_filtro": "", "fonte_colunas": "",
                       "doc_origem": "66 §3", "auditoria": ""})

    for cc, d in _por_ciclo(b):
        sfx = "EMP" if cc == "1–3" else f"C{cc}"
        add(f"D_N_{sfx}", "candidatos com 1ª opção, origem e distância", "contagem", cc, len(d), len(d))
        add(f"D_UF_{sfx}", "1ª opção na UF de origem (fração)", "fracao", cc, d["mesma_uf"].mean(), len(d))
        add(f"D_REG_{sfx}", "1ª opção na região de saúde de origem (fração)", "fracao", cc, d["mesma_regiao"].mean(),
            len(d))
        add(f"D_MUN_{sfx}", "1ª opção no município de origem (fração)", "fracao", cc, d["mesmo_municipio"].mean(),
            len(d))
        add(f"D_P50_{sfx}", "distância origem → 1ª opção: mediana (km)", "km", cc,
            d["dist_km_origem_principal"].median(), len(d))
        add(f"D_P75_{sfx}", "distância origem → 1ª opção: 3º quartil (km)", "km", cc,
            d["dist_km_origem_principal"].quantile(0.75), len(d))
        for bolsa in (10.0, 15.0, 20.0):
            dd = d[d["bolsa_mil"] == bolsa]
            add(f"D_UF_B{int(bolsa)}_{sfx}", f"1ª opção na UF de origem, vaga escolhida de R$ {int(bolsa)} mil (fração)",
                "fracao", cc, dd["mesma_uf"].mean(), len(dd))

    # Dentro da UF de origem: vagas disponíveis × vaga escolhida
    fontes_uf = fontes + [rel(CONJUNTO), rel(IVS_OFICIAL), rel(E9_RESUMO)]
    m = b[b["mesma_uf"] & b["s_mil"].notna()].copy()
    disp = c.groupby(["id_conjunto_escolha", "uf_vaga"])
    media_disp = disp["bolsa_mil"].mean().rename("bolsa_disp")
    m = m.merge(media_disp, left_on=["id_conjunto_escolha", "uf_origem"], right_index=True, how="left",
                validate="many_to_one")
    if m["bolsa_disp"].isna().any():
        raise AssertionError("1ª opção na UF de origem sem vagas da UF no conjunto")
    for cc, d in _por_ciclo(m):
        sfx = "EMP" if cc == "1–3" else f"C{cc}"
        add(f"D_BOLSA_DISP_{sfx}", "na UF de origem: bolsa média das vagas disponíveis (R$ mil)", "bolsa_mil", cc,
            d["bolsa_disp"].mean(), len(d), fontes_uf)
        add(f"D_BOLSA_ESC_{sfx}", "na UF de origem: bolsa média da vaga escolhida (R$ mil)", "bolsa_mil", cc,
            d["bolsa_mil"].mean(), len(d), fontes_uf)

    # Perto do corte: lado de bolsa maior nas disponíveis × nas escolhidas (mesma UF)
    m["corte"] = np.where(m["s_mil"] <= 350, CORTES_MIL[0], CORTES_MIL[1])
    m = m[(m["s_mil"] - m["corte"]).abs() <= JANELA_MIL].copy()
    c2 = c.copy()
    c2["corte"] = np.where(c2["s_mil"] <= 350, CORTES_MIL[0], CORTES_MIL[1])
    c2 = c2[(c2["s_mil"] - c2["corte"]).abs() <= JANELA_MIL].copy()
    c2["lado_maior"] = (c2["s_mil"] > c2["corte"]).astype(float)
    g = c2.groupby(["id_conjunto_escolha", "uf_vaga", "corte"])["lado_maior"].agg(["mean", "size"])
    m = m.merge(g, left_on=["id_conjunto_escolha", "uf_origem", "corte"], right_index=True, how="left",
                validate="many_to_one")
    m["lado_maior_escolhido"] = (m["s_mil"] > m["corte"]).astype(float)
    m = m[(m["mean"] > 0) & (m["mean"] < 1)].copy()  # só quem vê os dois lados do corte na sua UF
    for cc, d in list(_por_ciclo(m)) + [("corte 0,300", m[m["corte"] == 300]), ("corte 0,400", m[m["corte"] == 400])]:
        sfx = {"1–3": "EMP", "corte 0,300": "K300", "corte 0,400": "K400"}.get(cc, f"C{cc}")
        add(f"D_LADO_DISP_{sfx}", "perto do corte, na UF de origem: parte do lado de bolsa maior nas vagas disponíveis",
            "fracao", cc, d["mean"].mean(), len(d), fontes_uf)
        add(f"D_LADO_ESC_{sfx}", "perto do corte, na UF de origem: parte do lado de bolsa maior nas 1ªs opções",
            "fracao", cc, d["lado_maior_escolhido"].mean(), len(d), fontes_uf)
    diag["perto_do_corte"] = {"janela_mil": JANELA_MIL, "regra_corte": "s ≤ 350 → 0,300; s > 350 → 0,400",
                              "candidatos": int(len(m)),
                              "pares_conjunto_uf": int(m.groupby(["id_conjunto_escolha", "uf_origem"]).ngroups)}
    return linhas, diag, b


# ---------------------------------------------------------------------------
# Formatação
# ---------------------------------------------------------------------------

def _br(x: float, nd: int) -> str:
    s = f"{x:,.{nd}f}".replace(",", "§").replace(".", ",").replace("§", ".")
    return s.replace("-", "−")


def f2(x):
    return _br(x, 2)


def f3(x):
    return _br(x, 3)


def f0(x):
    return _br(x, 0)


def pct(x):
    return _br(100 * x, 0) + "%"


def pct1(x):
    return _br(100 * x, 1) + "%"


def fp(p):
    if p is None or (isinstance(p, float) and math.isnan(p)):
        return "—"
    return "< 0,001" if p < 0.001 else _br(p, 3)


def ic(r, f=f2):
    return f"[{f(r['ic95_inf'])}; {f(r['ic95_sup'])}]"


TEXTO = ["natureza_dos_dados", "estatuto", "id", "origem_numero", "grupo", "rotulo", "quantidade", "ciclo", "tipo_ajuste",
         "versao_quadro_ciclo2", "transformacao", "fonte_arquivo", "fonte_filtro", "fonte_colunas", "doc_origem",
         "auditoria"]


def ler_sintese() -> pd.DataFrame:
    df = pd.read_csv(OUT_CSV, dtype={c: str for c in TEXTO})
    df[TEXTO] = df[TEXTO].fillna("")
    return df


def _ix(df: pd.DataFrame) -> dict:
    return {r["id"]: r for _, r in df.iterrows()}


# ---------------------------------------------------------------------------
# Figuras
# ---------------------------------------------------------------------------

AZUL, CINZA, CINZA_C, TINTA = "#1f4e79", "#7f7f7f", "#c8c8c8", "#222222"
FONTE_PADRAO = "Fonte: output/rdd_bolsa (saídas auditadas); script 51."


def _plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 12, "axes.spines.top": False, "axes.spines.right": False,
                         "svg.hashsalt": "h2", "font.family": "DejaVu Sans"})
    return plt


def _rodape(fig, como_ler: str, fonte: str) -> None:
    linhas = textwrap.wrap("Como ler: " + como_ler, 135)
    if len(linhas) > 2:
        raise AssertionError(f"'Como ler' com mais de 2 linhas: {como_ler}")
    h = fig.get_figheight()
    fig.text(0.01, 0.34 / h, "\n".join(linhas), fontsize=10, color=TINTA, va="bottom")
    fig.text(0.01, 0.08 / h, fonte, fontsize=8.5, color=CINZA, va="bottom")


def _virgula(ax, eixo="x", nd=1):
    from matplotlib.ticker import FuncFormatter, NullFormatter
    a = ax.xaxis if eixo == "x" else ax.yaxis
    a.set_major_formatter(FuncFormatter(lambda v, _p: _br(v, nd) if abs(v - round(v)) > 1e-9 else _br(v, 0)))
    a.set_minor_formatter(NullFormatter())


def figuras(df: pd.DataFrame, base: pd.DataFrame) -> dict:
    plt = _plt()
    N = _ix(df)
    info = {}

    def salvar(fig, nome, titulo, como_ler, fonte):
        fig.suptitle(titulo, x=0.01, ha="left", fontsize=14, fontweight="bold")
        _rodape(fig, como_ler, fonte)
        caminho = FIG_DIR / nome
        gravar_figura(fig, caminho)
        plt.close(fig)
        info[nome.split("_")[1]] = {"arquivo": rel(caminho), "titulo": titulo, "como_ler": como_ler, "fonte": fonte}

    # F1: onde os médicos escolhem
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 5.6), gridspec_kw={"width_ratios": [1.1, 1]})
    fig.subplots_adjust(left=0.15, right=0.97, top=0.84, bottom=0.3, wspace=0.3)
    cats = [("UF", "mesma UF"), ("REG", "mesma região\nde saúde"), ("MUN", "mesmo município")]
    y = np.arange(len(cats))[::-1]
    a1.barh(y, [100 * N[f"ESC_{k}"]["estimativa"] for k, _ in cats], color=AZUL, height=0.55)
    for yy, (k, _) in zip(y, cats):
        a1.text(100 * N[f"ESC_{k}"]["estimativa"] + 1.5, yy, pct(N[f"ESC_{k}"]["estimativa"]), va="center",
                fontsize=12, fontweight="bold")
        for j, cc in enumerate(("1", "2", "3")):
            a1.plot(100 * N[f"D_{k}_C{cc}"]["estimativa"], yy + 0.36, "|", color=CINZA, ms=10)
    a1.set_yticks(y, [r for _, r in cats])
    a1.set_xlim(0, 100)
    a1.set_xlabel("% das 1ªs opções (traços: ciclos 1, 2 e 3)")
    a1.set_title("A 1ª opção fica perto da origem", fontsize=12, loc="left")
    dist = base["dist_km_origem_principal"].clip(upper=1500)
    a2.hist(dist, bins=np.arange(0, 1550, 50), color=CINZA_C, edgecolor="white")
    p50 = N["ESC_DIST_P50"]["estimativa"]
    a2.axvline(p50, color=AZUL, lw=2)
    a2.text(p50 + 30, a2.get_ylim()[1] * 0.9, f"mediana: {f0(p50)} km", color=AZUL, fontsize=12, fontweight="bold")
    a2.set_xlabel("km da origem à 1ª opção (última barra: 1.500+)")
    _virgula(a2, "x", 0)
    a2.set_ylabel("candidatos")
    a2.set_title("Distância origem → 1ª opção", fontsize=12, loc="left")
    salvar(fig, "H2_F1_onde_escolhem.png",
           f"O médico escolhe perto de onde já trabalha: {pct(N['ESC_UF']['estimativa'])} põem a 1ª opção na UF de origem",
           "cada barra é a parte das 1ªs opções no mesmo lugar do vínculo médico anterior no CNES (origem); "
           "descritivo, entre quem se candidatou.",
           "Fonte: numeros_banca2.json (ESC_*); G1_candidatos_origem, G1_distancias_opcoes, escolhas_candidatos "
           "(script 12), malha de regiões de saúde; script 51.")

    # F2: dentro da UF, perto do corte
    grupos = [("EMP", "ciclos 1–3"), ("C1", "ciclo 1"), ("C2", "ciclo 2"), ("C3", "ciclo 3")]
    fig, ax = plt.subplots(figsize=(11, 5.6))
    fig.subplots_adjust(left=0.08, right=0.97, top=0.84, bottom=0.3)
    x = np.arange(len(grupos))
    vd = [100 * N[f"D_LADO_DISP_{g}"]["estimativa"] for g, _ in grupos]
    ve = [100 * N[f"D_LADO_ESC_{g}"]["estimativa"] for g, _ in grupos]
    ax.bar(x - 0.19, vd, 0.36, color=CINZA_C, label="nas vagas disponíveis")
    ax.bar(x + 0.19, ve, 0.36, color=AZUL, label="nas 1ªs opções")
    for xx, a, e in zip(x, vd, ve):
        ax.text(xx - 0.19, a + 1, f"{_br(a, 0)}%", ha="center", fontsize=11)
        ax.text(xx + 0.19, e + 1, f"{_br(e, 0)}%", ha="center", fontsize=11, fontweight="bold", color=AZUL)
    ax.axhline(50, color=CINZA, lw=0.8, ls=":")
    ax.set_xticks(x, [f"{r}\n(n = {f0(N[f'D_LADO_ESC_{g}']['n_candidatos'])})" for g, r in grupos])
    ax.set_ylim(0, 100)
    ax.set_ylabel("% do lado de bolsa maior")
    ax.legend(frameon=False, loc="upper right")
    maior = N["D_LADO_ESC_EMP"]["estimativa"] > N["D_LADO_DISP_EMP"]["estimativa"]
    titulo_f2 = ("Na UF de origem, perto do corte, o lado de bolsa maior é mais escolhido do que oferecido"
                 if maior else "Na UF de origem, perto do corte, o lado de bolsa maior não é mais escolhido do que oferecido")
    salvar(fig, "H2_F2_mesma_uf_perto_do_corte.png", titulo_f2,
           "só 1ªs opções na UF de origem e a até 0,050 de um corte de IVS; cinza: parte das vagas do mesmo curso e UF "
           "no lado de bolsa maior; azul: parte das escolhas. Descritivo, sem teste.",
           "Fonte: escolhas_candidatos e escolhas_conjunto_principal (script 12), G1, IVS 2010 oficial (a08); script 51.")

    # F3: razão de chances por +R$ 5 mil
    fig, ax = plt.subplots(figsize=(11, 5.8))
    fig.subplots_adjust(left=0.12, right=0.97, top=0.84, bottom=0.3)
    blocos = [("ciclos 1–3", "OR_M1_EMP", "OR_VL1_EMP"), ("ciclo 1", "OR_M5_C1", None),
              ("ciclo 2", "OR_M1_C2", "OR_VL1_C2"), ("ciclo 3", "OR_M5_C3", None)]
    for i, (rot, base_id, vl_id) in enumerate(blocos):
        yy = len(blocos) - 1 - i
        r = N[base_id]
        ax.errorbar(r["estimativa"], yy + 0.15, xerr=[[r["estimativa"] - r["ic95_inf"]], [r["ic95_sup"] - r["estimativa"]]],
                    fmt="o", mfc="white", color=CINZA, ms=8, capsize=3, label="M1: todas as vagas" if i == 0 else None)
        if vl_id:
            r = N[vl_id]
            ax.errorbar(r["estimativa"], yy - 0.15,
                        xerr=[[r["estimativa"] - r["ic95_inf"]], [r["ic95_sup"] - r["estimativa"]]], fmt="o",
                        color=AZUL, ms=9, capsize=3, label="VL-1: só vagas da UF de origem" if i == 0 else None)
            ax.text(r["ic95_sup"] * 1.04, yy - 0.15, f2(r["estimativa"]), va="center", color=AZUL, fontweight="bold")
        else:
            ax.text(1.75, yy - 0.15, "VL-1: não estimado neste ciclo (adendo 52e)", fontsize=9, color=CINZA,
                    ha="left", va="center")
    ax.axvline(1, color=TINTA, lw=0.8)
    ax.set_xscale("log")
    ax.set_xticks([0.5, 0.75, 1, 1.5, 2, 3], ["0,5", "0,75", "1", "1,5", "2", "3"])
    from matplotlib.ticker import NullFormatter
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.set_yticks(range(len(blocos)), [b[0] for b in blocos][::-1])
    ax.set_ylim(-0.55, len(blocos) - 0.5)
    ax.set_xlabel("razão de chances de a vaga ser a 1ª opção, por +R$ 5 mil (escala log)")
    ax.legend(frameon=False, loc="upper left", fontsize=10)
    salvar(fig, "H2_F3_razao_chances_bolsa.png",
           "Comparando vagas da mesma UF, a de bolsa maior é mais escolhida (ciclos 1–3 e ciclo 2)",
           "acima de 1, a vaga com bolsa R$ 5 mil maior é mais escolhida, com distância, origem e IVS contínuo fixos; "
           "barra: IC 95%. Bolsa = pacote do corte; VL-1 é adendo pós-resultado.",
           "Fonte: VL_estimativas.csv (52e), VC_estimativas.csv (52c); script 51.")

    # F4: origem × toda a bolsa
    fig, ax = plt.subplots(figsize=(11, 5.6))
    fig.subplots_adjust(left=0.36, right=0.97, top=0.84, bottom=0.3)
    linhas = [("ciclos 1–3: toda a bolsa (10·β)", "BOLSA10_M1", CINZA), ("ciclos 1–3: vaga na UF de origem (θ_UF)",
              "THETA_UF_M1", AZUL), ("ciclo 2: toda a bolsa (10·β)", "BOLSA10_C2", CINZA),
              ("ciclo 2: vaga na UF de origem (θ_UF)", "THETA_UF_C2", AZUL)]
    for i, (rot, k, cor) in enumerate(linhas):
        yy = len(linhas) - 1 - i - (0.4 if i >= 2 else 0)
        r = N[k]
        ax.barh(yy, r["estimativa"], color=cor, height=0.5, alpha=0.9)
        ax.errorbar(r["estimativa"], yy, xerr=[[r["estimativa"] - r["ic95_inf"]], [r["ic95_sup"] - r["estimativa"]]],
                    fmt="none", color=TINTA, capsize=4)
        ax.text(max(r["ic95_sup"], r["estimativa"]) + 0.06, yy, f2(r["estimativa"]), va="center", fontsize=11)
    ax.set_yticks([3, 2, 0.6, -0.4], [l[0] for l in linhas])
    ax.axvline(0, color=TINTA, lw=0.8)
    ax.set_xlabel("peso na escolha da 1ª opção (log-chance; barra: IC 95%)")
    _virgula(ax)
    d1, d2 = N["DUF_M1"], N["DUF_M5_C2"]
    ax.text(0.98, 0.95, f"D_UF = θ_UF − 10·β\nciclos 1–3: {f2(d1['estimativa'])} {ic(d1)}\n"
            f"ciclo 2: {f2(d2['estimativa'])} {ic(d2)}", transform=ax.transAxes, ha="right", va="top", fontsize=11,
            bbox={"facecolor": "white", "edgecolor": CINZA_C})
    salvar(fig, "H2_F4_origem_contra_bolsa.png",
           "Ter a vaga na UF de origem pesa mais que toda a diferença de bolsa (R$ 10 → 20 mil)",
           "barras na mesma escala da utilidade do modelo M1 (quadro do ciclo 2 de 13/02); D_UF > 0: a origem pesa mais. "
           "A origem é preferência revelada; a bolsa, o pacote do corte.",
           "Fonte: VC_estimativas.csv (adendo 52c; P1h-1 corrigido); script 51.")

    # F5: km
    fig, ax = plt.subplots(figsize=(11, 5.4))
    fig.subplots_adjust(left=0.3, right=0.97, top=0.84, bottom=0.3)
    kms = [("M1, ciclos 1–3 (referência)", "K5_M1_EMP", CINZA), ("M1, ciclo 2", "K5_M1_C2", CINZA),
           ("mesma UF (VL-1), ciclos 1–3", "K5_VL1_EMP", AZUL), ("mesma UF (VL-1), ciclo 2", "K5_VL1_C2", AZUL)]
    for i, (rot, k, cor) in enumerate(kms):
        yy = len(kms) - 1 - i
        r = N[k]
        ax.errorbar(r["estimativa"], yy, xerr=[[r["estimativa"] - r["ic95_inf"]], [r["ic95_sup"] - r["estimativa"]]],
                    fmt="o", color=cor, ms=9, capsize=4)
        ax.text(r["estimativa"], yy + 0.22, f"{f0(r['estimativa'])} km", ha="center", color=cor, fontweight="bold")
    ax.axvline(0, color=TINTA, lw=0.8)
    ax.axvline(p50, color=AZUL, lw=1, ls="--")
    ax.text(p50 + 8, -0.6, f"mediana da distância à 1ª opção: {f0(p50)} km", color=AZUL, fontsize=10)
    ax.set_ylim(-0.8, len(kms) - 0.4)
    ax.set_yticks(range(len(kms)), [k[0] for k in kms][::-1])
    ax.set_xlabel("km a menos de distância que pesam como +R$ 5 mil de bolsa (IC 95%, método delta)")
    salvar(fig, "H2_F5_bolsa_em_km.png",
           f"+R$ 5 mil pesam como {f0(N['K5_M1_EMP']['estimativa'])} km a menos; dentro da mesma UF, "
           f"{f0(N['K5_VL1_EMP']['estimativa'])} km",
           "cada ponto converte o peso de um degrau de bolsa em km de distância origem → vaga. Os km do VL-1 são "
           "km dentro da UF, onde a distância pesa mais: não se comparam um a um com os do M1.",
           "Fonte: VL_estimativas.csv (VL-4 e VL-5); numeros_banca2.json (ESC_DIST_P50); script 51.")

    # F6: robustez
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(16, 8.6), gridspec_kw={"width_ratios": [1.3, 0.8]})
    fig.subplots_adjust(left=0.25, right=0.98, top=0.88, bottom=0.2, wspace=0.95)
    for ax, ids, escala, ref, xlab in ((a1, ROBUSTEZ_OR, "log", 1.0, "razão de chances por +R$ 5 mil (log)"),
                                       (a2, ROBUSTEZ_DUF, "linear", 0.0, "D_UF = θ_UF − 10·β")):
        for i, k in enumerate(ids):
            r = N[k]
            yy = len(ids) - 1 - i
            cor = AZUL if r["principal"] else CINZA
            ax.errorbar(r["estimativa"], yy, xerr=[[r["estimativa"] - r["ic95_inf"]], [r["ic95_sup"] - r["estimativa"]]],
                        fmt="D" if r["principal"] else "o", color=cor, ms=8 if r["principal"] else 5, capsize=2,
                        mfc=cor if r["versao_quadro_ciclo2"] == "13/02/2026" else "white")
        ax.axvline(ref, color=TINTA, lw=0.8)
        ax.set_xscale(escala)
        if escala == "log":
            ax.set_xticks([0.7, 1, 1.5, 2, 3], ["0,7", "1", "1,5", "2", "3"])
            from matplotlib.ticker import NullFormatter
            ax.xaxis.set_minor_formatter(NullFormatter())
        else:
            _virgula(ax)
        ax.set_yticks(range(len(ids)), [N[k]["rotulo"] for k in ids][::-1], fontsize=9)
        ax.set_xlabel(xlab)
    a1.set_title("A bolsa pesa na escolha?", loc="left", fontsize=12)
    a2.set_title("A origem pesa mais que toda a bolsa?", loc="left", fontsize=12)
    salvar(fig, "H2_F6_robustez.png",
           "Em todas as variantes a origem pesa mais que a bolsa; o peso da bolsa sozinho muda com a especificação",
           "losango azul: linha principal; ponto vazado: tipo de vaga do ciclo 2 do quadro de 19/03 (versão antiga). "
           "IC 95%. À esquerda, IC que cruza 1 não distingue a bolsa de zero.",
           "Fonte: VL_, VC_, VD_, E9_estimativas.csv e P1h_magnitudes.csv; script 51.")
    return info


ROBUSTEZ_OR = ["OR_VL1_EMP", "OR_VL1_C2", "OR_VL1LOG_EMP", "OR_VL1LOG_C2", "OR_VL3_VL1_EMP", "OR_VL3_VL1_C2",
               "OR_VL2_EMP", "OR_VL2_C2", "OR_VL3_VL2_EMP", "OR_VL3_VL2_C2", "OR_M4_EMP", "OR_M4_C2", "OR_M1_EMP",
               "OR_M5_C1", "OR_M1_C2", "OR_M5_C3", "OR_M2_EMP", "OR_M7_EMP", "OR_M8_EMP", "OR_M9_EMP", "OR_E9_EMP",
               "OR_E9_C2", "OR_E9CUB_EMP", "OR_E9CUB_C2"]
ROBUSTEZ_DUF = ["DUF_M1", "DUF_M2", "DUF_M4", "DUF_M7", "DUF_M5_C1", "DUF_M5_C2", "DUF_M5_C3", "DUF_M1_ANTIGA"]


# ---------------------------------------------------------------------------
# Blocos do doc 66
# ---------------------------------------------------------------------------

def _linha_or(r) -> str:
    padj = fp(r["p_ajustado"]) if not math.isnan(r["p_ajustado"]) else "—"
    return (f"| {r['rotulo']} | {f0(r['n_candidatos'])} | {f2(r['estimativa'])} {ic(r)} | {fp(r['p'])} | {padj} | "
            f"{r['tipo_ajuste'] or '—'} | {r['doc_origem']} |")


def blocos(df: pd.DataFrame, resumo: dict) -> dict[str, str]:
    N = _ix(df)
    B = {}
    g = lambda k: N[k]["estimativa"]  # noqa: E731
    fig = resumo["figuras"]

    def img(k):
        f = fig[k]
        return (f"![{f['titulo']}](../../{f['arquivo']})\n\n**Como ler.** {f['como_ler'][0].upper() + f['como_ler'][1:]}"
                f" *{f['fonte']}*")

    B["resposta"] = "\n".join([
        f"- **Perto de casa (descritivo).** Entre os {f0(g('ESC_N'))} candidatos com origem conhecida, "
        f"{pct(g('ESC_UF'))} põem a 1ª opção na UF onde já tinham vínculo médico, {pct(g('ESC_REG'))} na mesma região "
        f"de saúde e {pct(g('ESC_MUN'))} no mesmo município; a distância mediana é {f0(g('ESC_DIST_P50'))} km "
        "(`ESC_*` de `numeros_banca2.json`, reproduzidos pelo script 51).",
        f"- **Teste central: a origem pesa mais que toda a bolsa.** No modelo de escolha pré-registrado (M1, quadro do "
        f"ciclo 2 de 13/02), D_UF = θ_UF − 10·β = {f2(g('DUF_M1'))} {ic(N['DUF_M1'])}, p unilateral "
        f"{fp(N['DUF_M1']['p'])} (Holm = p). Ter a vaga na UF de origem pesa {f2(g('THETA_UF_M1'))}; toda a "
        f"amplitude da bolsa, {f2(g('BOLSA10_M1'))} {ic(N['BOLSA10_M1'])}.",
        f"- **O peso da bolsa sozinho, na especificação pré-registrada, não passa no Holm:** β = "
        f"{_br(g('BETA_M1_EMP'), 4)} por R$ 1 mil {ic(N['BETA_M1_EMP'], lambda x: _br(x, 4))}, p de Holm "
        f"{fp(N['BETA_M1_EMP']['p_ajustado'])}.",
        f"- **Dentro da UF de origem, a bolsa maior é mais escolhida (adendo pós-resultado 52e).** Comparando só vagas "
        f"da mesma UF, vistas por médicos da mesma UF de origem, a razão de chances por +R$ 5 mil é "
        f"{f2(g('OR_VL1_EMP'))} {ic(N['OR_VL1_EMP'])} nos ciclos 1–3 (p de Holm {fp(N['OR_VL1_EMP']['p_ajustado'])}) e "
        f"{f2(g('OR_VL1_C2'))} {ic(N['OR_VL1_C2'])} no ciclo 2 (p de Holm {fp(N['OR_VL1_C2']['p_ajustado'])}). Só com "
        f"vagas perto do corte: {f2(g('OR_VL2_EMP'))} {ic(N['OR_VL2_EMP'])}, inconclusivo.",
        f"- **Dentro da UF, perto do corte (descritivo, sem teste).** O lado de bolsa maior é "
        f"{pct1(g('D_LADO_DISP_EMP'))} das vagas disponíveis e {pct1(g('D_LADO_ESC_EMP'))} das 1ªs opções "
        f"({f0(N['D_LADO_ESC_EMP']['n_candidatos'])} candidatos que veem os dois lados do corte na sua UF).",
        f"- **Em km.** Um degrau de R$ 5 mil pesa como {f0(g('K5_M1_EMP'))} km "
        f"{ic(N['K5_M1_EMP'], f0)} a menos de distância no M1 e {f0(g('K5_VL1_EMP'))} km {ic(N['K5_VL1_EMP'], f0)} "
        f"comparando dentro da mesma UF.",
    ])

    B["amostra"] = "\n".join([
        "| Etapa | Ciclo 1 | Ciclo 2 | Ciclo 3 | Total | Fonte |",
        "|---|---|---|---|---|---|",
        f"| candidatos classificados com opção na 1ª chamada (portão G1) | {f0(g('G1_CAND_C1'))} | {f0(g('G1_CAND_C2'))} | "
        f"{f0(g('G1_CAND_C3'))} | {f0(g('G1_CAND_EMP'))} | G1 §4 |",
        f"| ligados ao CNES (CPF mascarado + nome) | {f0(g('G1_LIG_C1'))} | {f0(g('G1_LIG_C2'))} | {f0(g('G1_LIG_C3'))} | "
        f"{f0(g('G1_LIG_EMP'))} | G1 §4 |",
        f"| com município de origem (vínculo médico na competência anterior à inscrição) | {f0(g('G1_ORIG_C1'))} | "
        f"{f0(g('G1_ORIG_C2'))} | {f0(g('G1_ORIG_C3'))} | {f0(g('G1_ORIG_EMP'))} | G1 §4 |",
        f"| com linha de 1ª opção publicada | {f0(g('P1_R1_C1'))} | {f0(g('P1_R1_C2'))} | {f0(g('P1_R1_C3'))} | "
        f"{f0(g('P1_R1_C1') + g('P1_R1_C2') + g('P1_R1_C3'))} | 57a §2 |",
        f"| descritiva desta análise (1ª opção com origem e distância) | {f0(g('D_N_C1'))} | {f0(g('D_N_C2'))} | "
        f"{f0(g('D_N_C3'))} | {f0(g('D_N_EMP'))} | script 51 |",
        f"| **modelo de escolha (M1)** | {f0(g('P1_N_C1'))} | {f0(g('P1_N_C2'))} | {f0(g('P1_N_C3'))} | "
        f"{f0(g('P1_N_C1') + g('P1_N_C2') + g('P1_N_C3'))} | 57a §2 |",
        "",
        f"O M1 compara cada candidato consigo mesmo: são {f0(g('P1_CONJ'))} conjuntos de escolha (curso × ciclo), "
        f"{f0(g('P1_CELULAS'))} vagas (CNES × curso) e {f0(g('P1_LINHAS'))} pares candidato × vaga. A descritiva tem "
        f"{f0(g('D_N_EMP') - (g('P1_N_C1') + g('P1_N_C2') + g('P1_N_C3')))} candidatos a mais que o M1, que retira "
        "quem tem a origem ou a 1ª opção num município sem região de saúde na tabela do TabNet (57a §2).",
    ])

    lin = ["| | Ciclos 1–3 | Ciclo 1 | Ciclo 2 | Ciclo 3 |", "|---|---|---|---|---|"]
    for k, r in (("UF", "1ª opção na UF de origem"), ("REG", "1ª opção na região de saúde de origem"),
                 ("MUN", "1ª opção no município de origem")):
        lin.append(f"| {r} | {pct(g('D_' + k + '_EMP'))} | {pct(g('D_' + k + '_C1'))} | {pct(g('D_' + k + '_C2'))} | "
                   f"{pct(g('D_' + k + '_C3'))} |")
    for k, r in (("P50", "distância origem → 1ª opção: mediana (km)"), ("P75", "distância: 3º quartil (km)")):
        lin.append(f"| {r} | {f0(g('D_' + k + '_EMP'))} | {f0(g('D_' + k + '_C1'))} | {f0(g('D_' + k + '_C2'))} | "
                   f"{f0(g('D_' + k + '_C3'))} |")
    lin.append(f"| candidatos | {f0(g('D_N_EMP'))} | {f0(g('D_N_C1'))} | {f0(g('D_N_C2'))} | {f0(g('D_N_C3'))} |")
    lin += ["", "Por bolsa da vaga escolhida (ciclos 1–3): parte das 1ªs opções que fica na UF de origem.", "",
            "| Vaga escolhida | Na UF de origem | Candidatos |", "|---|---|---|"]
    for bb in (10, 15, 20):
        lin.append(f"| R$ {bb} mil | {pct(g(f'D_UF_B{bb}_EMP'))} | {f0(N[f'D_UF_B{bb}_EMP']['n_candidatos'])} |")
    lin += ["", "Dentro da UF de origem: o que estava disponível e o que foi escolhido.", "",
            "| | Ciclos 1–3 | Ciclo 1 | Ciclo 2 | Ciclo 3 |", "|---|---|---|---|---|"]
    lin.append("| todas as vagas da UF: bolsa média disponível (R$ mil) | " +
               " | ".join(f2(g(f"D_BOLSA_DISP_{s}")) for s in ("EMP", "C1", "C2", "C3")) + " |")
    lin.append("| todas as vagas da UF: bolsa média escolhida (R$ mil) | " +
               " | ".join(f2(g(f"D_BOLSA_ESC_{s}")) for s in ("EMP", "C1", "C2", "C3")) + " |")
    lin.append("| candidatos | " + " | ".join(f0(N[f"D_BOLSA_ESC_{s}"]["n_candidatos"]) for s in ("EMP", "C1", "C2", "C3"))
               + " |")
    lin.append("| perto do corte: lado de bolsa maior nas vagas disponíveis | " +
               " | ".join(pct1(g(f"D_LADO_DISP_{s}")) for s in ("EMP", "C1", "C2", "C3")) + " |")
    lin.append("| perto do corte: lado de bolsa maior nas 1ªs opções | " +
               " | ".join(pct1(g(f"D_LADO_ESC_{s}")) for s in ("EMP", "C1", "C2", "C3")) + " |")
    lin.append("| candidatos perto do corte que veem os dois lados na sua UF | " +
               " | ".join(f0(N[f"D_LADO_ESC_{s}"]["n_candidatos"]) for s in ("EMP", "C1", "C2", "C3")) + " |")
    lin += ["", f"Por corte (ciclos 1–3): em 0,300, {pct1(g('D_LADO_DISP_K300'))} das vagas disponíveis e "
            f"{pct1(g('D_LADO_ESC_K300'))} das escolhas ficam do lado de bolsa maior "
            f"({f0(N['D_LADO_ESC_K300']['n_candidatos'])} candidatos); em 0,400, {pct1(g('D_LADO_DISP_K400'))} e "
            f"{pct1(g('D_LADO_ESC_K400'))} ({f0(N['D_LADO_ESC_K400']['n_candidatos'])}).",
            "", img("F1"), "", img("F2")]
    B["descritiva"] = "\n".join(lin)

    B["identificacao"] = (
        f"No VL-1 (ciclos 1–3), {f0(g('VL1_PARES_COM_VARIACAO_DE_BOLSA'))} dos {f0(g('VL1_PARES_COM_ESCOLHA'))} pares "
        f"(UF de origem, UF da vaga) com alguma escolha têm vagas de bolsas diferentes, vindos de "
        f"{f0(g('VL1_ORIGENS_COM_ALGUM_PAR_COM_VARIACAO'))} UFs de origem. São "
        f"{f0(g('VL1_CANDIDATOS_COM_VARIACAO_DE_BOLSA_EM_ALGUM_PAR'))} dos {f0(g('VL1_CANDIDATOS_NO_MODELO'))} "
        f"candidatos que veem, dentro de uma UF, vagas de bolsas diferentes; "
        f"{f0(g('VL1_CANDIDATOS_COM_1A_OPCAO_EM_PAR_COM_VARIACAO'))} escolheram a 1ª opção numa UF assim (57x §3).")

    t = ["| Linha | Candidatos | Razão de chances [IC 95%] | p | p ajustado | Ajuste | Fonte |",
         "|---|---|---|---|---|---|---|"]
    for k in ("OR_VL1_EMP", "OR_VL1_C2", "OR_VL2_EMP", "OR_M1_EMP", "OR_M1_C2", "OR_M5_C1", "OR_M5_C3"):
        t.append(_linha_or(N[k]))
    t += ["", f"Diferença pareada contra o M1, em log da razão de chances (52e, decisão 10): VL-1 ciclos 1–3 "
          f"{f3(g('DIF_VL1_EMP'))} {ic(N['DIF_VL1_EMP'], f3)}; VL-1 ciclo 2 {f3(g('DIF_VL1_C2'))} "
          f"{ic(N['DIF_VL1_C2'], f3)}; VL-2 {f3(g('DIF_VL2_EMP'))} {ic(N['DIF_VL2_EMP'], f3)}. p do score bootstrap "
          f"(poucos *clusters*): VL-1 ciclos 1–3 {fp(N['OR_VL1_EMP']['p_score_rademacher'])}, ciclo 2 "
          f"{fp(N['OR_VL1_C2']['p_score_rademacher'])}, VL-2 {fp(N['OR_VL2_EMP']['p_score_rademacher'])}.",
          "", "| Peso no M1 (log-chance) | Ciclos 1–3 | Ciclo 2 | Fonte |", "|---|---|---|---|",
          f"| vaga na UF de origem (θ_UF) | {f2(g('THETA_UF_M1'))} {ic(N['THETA_UF_M1'])} | {f2(g('THETA_UF_C2'))} "
          f"{ic(N['THETA_UF_C2'])} | 57p §4.3 |",
          f"| toda a bolsa, R$ 10 → 20 mil (10·β) | {f2(g('BOLSA10_M1'))} {ic(N['BOLSA10_M1'])} | {f2(g('BOLSA10_C2'))} "
          f"{ic(N['BOLSA10_C2'])} | 57p §4.1 |",
          f"| **D_UF = θ_UF − 10·β** | **{f2(g('DUF_M1'))} {ic(N['DUF_M1'])}**, p unilateral {fp(N['DUF_M1']['p'])} | "
          f"{f2(g('DUF_M5_C2'))} {ic(N['DUF_M5_C2'])}, p unilateral {fp(N['DUF_M5_C2']['p'])} | 57p §4.2 |",
          "", f"| Um degrau de +R$ 5 mil, em km a menos (IC 95% delta) | Ciclos 1–3 | Ciclo 2 | Fonte |",
          "|---|---|---|---|",
          f"| M1: todas as vagas (quadro corrigido) | {f0(g('K5_M1_EMP'))} {ic(N['K5_M1_EMP'], f0)} | "
          f"{f0(g('K5_M1_C2'))} {ic(N['K5_M1_C2'], f0)} | 57x §4.3; 57v §5.6 |",
          f"| VL-1: só vagas da UF de origem | {f0(g('K5_VL1_EMP'))} {ic(N['K5_VL1_EMP'], f0)} | {f0(g('K5_VL1_C2'))} "
          f"{ic(N['K5_VL1_C2'], f0)} | 57x §4.3 |",
          "", f"Dentro da UF, a distância pesa mais ({f2(g('GAMA_VL1_EMP'))} por 100 km, contra "
          f"{f2(g('GAMA_M1_EMP'))} no M1) e a bolsa também (β de {f3(g('BETA_VL1_EMP'))} contra "
          f"{f3(g('BETA_M1_EMP'))} por R$ 1 mil). Por isso os km do VL-1 caem: são km dentro da UF.",
          "", img("F3"), "", img("F4"), "", img("F5")]
    B["resultados"] = "\n".join(t)

    r = ["Bolsa: razão de chances da 1ª opção por +R$ 5 mil. Linha principal em negrito.", "",
         "| Variante | Candidatos | Razão de chances [IC 95%] | p | p ajustado | Ajuste | Quadro do ciclo 2 | Fonte |",
         "|---|---|---|---|---|---|---|---|"]
    for k in ROBUSTEZ_OR:
        x = N[k]
        rot = f"**{x['rotulo']}**" if x["principal"] else x["rotulo"]
        padj = fp(x["p_ajustado"]) if not math.isnan(x["p_ajustado"]) else "—"
        r.append(f"| {rot} | {f0(x['n_candidatos'])} | {f2(x['estimativa'])} {ic(x)} | {fp(x['p'])} | {padj} | "
                 f"{x['tipo_ajuste'] or '—'} | {x['versao_quadro_ciclo2']} | {x['doc_origem']} |")
    r += ["", "Origem contra toda a bolsa: D_UF = θ_UF − 10·β (log-chance). Linha principal em negrito.", "",
          "| Variante | D_UF [IC 95%] | p unilateral | p ajustado | Quadro do ciclo 2 | Fonte |", "|---|---|---|---|---|---|"]
    for k in ROBUSTEZ_DUF:
        x = N[k]
        rot = f"**{x['rotulo']}**" if x["principal"] else x["rotulo"]
        padj = fp(x["p_ajustado"]) if not math.isnan(x["p_ajustado"]) else "—"
        r.append(f"| {rot} | {f2(x['estimativa'])} {ic(x)} | {fp(x['p'])} | {padj} | {x['versao_quadro_ciclo2']} | "
                 f"{x['doc_origem']} |")
    n_duf_pos = sum(N[k]["ic95_inf"] > 0 for k in ROBUSTEZ_DUF)
    n_or_sem1 = sum(N[k]["ic95_inf"] > 1 for k in ROBUSTEZ_OR)
    r += ["", f"Contagem: D_UF tem IC acima de zero em {n_duf_pos} de {len(ROBUSTEZ_DUF)} variantes; a razão de "
          f"chances da bolsa tem IC acima de 1 em {n_or_sem1} de {len(ROBUSTEZ_OR)}. O 10·β do VL-1, que é o maior "
          f"peso da bolsa entre as principais, é {f2(g('BOLSA10_VL1_EMP'))} {ic(N['BOLSA10_VL1_EMP'])}: o limite de "
          f"cima fica abaixo do limite de baixo do θ_UF do M1 ({f2(N['THETA_UF_M1']['ic95_inf'])}). É comparação entre "
          "modelos, sem teste: no VL-1 o efeito fixo do par absorve a mesma UF, e o D_UF não é identificado.",
          "", img("F6")]
    B["robustez"] = "\n".join(r)

    f = ["| Entrada | Papel | Referência | Unidade | SHA-256 (12) |", "|---|---|---|---|---|"]
    for e in resumo["entradas"]:
        f.append(f"| `{e['caminho']}` | {e['papel']} | {e['data_referencia']} | {e['unidade']} | `{e['sha256'][:12]}` |")
    f += ["", f"Saídas: `{rel(OUT_CSV)}` ({len(df)} linhas: {int((df['origem_numero'] == 'SAIDA_AUDITADA').sum())} "
          f"copiadas de saídas auditadas e {int((df['origem_numero'] == 'DESCRITIVO_NOVO').sum())} descritivas novas), "
          f"`{rel(OUT_RESUMO)}` e {len(resumo['figuras'])} figuras em `{rel(FIG_DIR)}/`. Todas com "
          f"`natureza_dos_dados = {NATUREZA}`."]
    B["fontes"] = "\n".join(f)
    return B


MARCADOR = re.compile(r"(<!-- H2:(\w+):inicio -->\n)(?:(.*?)\n)?(<!-- H2:\2:fim -->)", re.S)
NOMES_BLOCOS = ("resposta", "amostra", "descritiva", "identificacao", "resultados", "robustez", "fontes")


def atualizar_texto(texto: str, B: dict[str, str]) -> str:
    vistos = []

    def troca(m):
        vistos.append(m.group(2))
        return m.group(1) + B[m.group(2)] + "\n" + m.group(4)

    novo = MARCADOR.sub(troca, texto)
    if sorted(vistos) != sorted(NOMES_BLOCOS):
        raise AssertionError(f"marcadores do doc 66: {sorted(vistos)}")
    return novo


def atualizar_doc() -> None:
    df = ler_sintese()
    resumo = json.loads(OUT_RESUMO.read_text(encoding="utf-8"))
    gravar_texto(DOC, atualizar_texto(DOC.read_text(encoding="utf-8"), blocos(df, resumo)))


# ---------------------------------------------------------------------------
# Execução
# ---------------------------------------------------------------------------

def construir() -> tuple[pd.DataFrame, dict, pd.DataFrame]:
    for p, *_ in ENTRADAS:  # o único IVS lido é o oficial do a08 (auditoria 16)
        if "ivs" in p.name.lower() and p != IVS_OFICIAL:
            raise AssertionError(f"arquivo de IVS fora do a08 entre as entradas: {p}")
    aud = linhas_auditadas()
    desc, diag, base = descritivas()
    df = pd.DataFrame(aud + desc, columns=COLUNAS)
    if df["id"].duplicated().any():
        raise AssertionError("id duplicado na síntese")
    # Conferência: os descritivos ESC_* da banca 2 são os mesmos que a base desta análise reproduz.
    N = _ix(df)
    for k, d in (("ESC_N", "D_N_EMP"), ("ESC_UF", "D_UF_EMP"), ("ESC_REG", "D_REG_EMP"), ("ESC_MUN", "D_MUN_EMP"),
                 ("ESC_DIST_P50", "D_P50_EMP"), ("ESC_DIST_P75", "D_P75_EMP")):
        if abs(N[k]["estimativa"] - N[d]["estimativa"]) > TOL:
            raise AssertionError(f"{k} da banca 2 difere da base desta análise ({d})")
    return df, diag, base


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--atualizar-doc", action="store_true", help="só regrava os blocos do doc 66 a partir das saídas")
    a = ap.parse_args(argv)
    if a.atualizar_doc:
        atualizar_doc()
        print(f"doc atualizado: {rel(DOC)}")
        return 0
    df, diag, base = construir()
    csv = df.to_csv(index=False, float_format="%.10g", lineterminator="\n")
    gravar_texto(OUT_CSV, csv)
    info = figuras(df, base)
    resumo = {
        "natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "data_execucao": DATA, "script": SCRIPT_REL,
        "hipotese": ("O médico especialista escolhe vagas perto de onde já trabalha. A bolsa maior muda qual vaga ele "
                     "escolhe dentro da sua região, mas pesa menos que a própria origem."),
        "teste_central": "D_UF = θ_UF − 10·β > 0 no M1 (P1h-1, quadro do ciclo 2 de 13/02/2026; 57p §4.2)",
        "contraste": ("bolsa = pacote do corte (bolsa e outras regras federais nos mesmos cortes de IVS, auditoria 18); "
                      "origem = preferência revelada (município do vínculo médico no CNES antes da inscrição); tudo "
                      "condicional a se candidatar, dentro das vagas abertas; não é participação no PMM-E"),
        "pos_resultado": "a hipótese foi formulada depois de ver os resultados; nada aqui é teste confirmatório novo",
        "nao_reestima": True,
        "entradas": [{"caminho": rel(p), "papel": papel, "data_referencia": dref, "cobertura": cob, "unidade": un,
                      "chaves": ch, "filtros": fil, "sha256": sha256(p),
                      "conferencia": "valores" if p in ENTRADA_SO_VALORES else "sha256"}
                     for p, papel, dref, cob, un, ch, fil in ENTRADAS],
        "descritivas": {**diag, "definicoes": {
            "base": "1ª opção publicada (escolhas_candidatos, opcao_rank = 1) com município de origem (G1, regra "
                    "g1_cpf_nome) e distância à origem principal (G1_distancias_opcoes)",
            "mesma_regiao": "região de saúde da malha (sg_uf + no_regiao_saude), como em numeros_banca2.json",
            "dentro_da_uf": "vagas do mesmo conjunto de escolha (curso × ciclo) na UF de origem, com IVS 2010 oficial; "
                            "média por candidato e depois entre candidatos",
            "perto_do_corte": "1ª opção na UF de origem com |IVS − corte| ≤ 0,050 (s ≤ 350 → corte 0,300; s > 350 → "
                              "0,400); vagas disponíveis = mesmo conjunto, mesma UF, mesma janela; só candidatos que "
                              "veem os dois lados do corte; lado de bolsa maior = IVS acima do corte",
            "inferencia": "nenhuma: são descritivos, sem teste"}},
        "figuras": info,
        "saidas": {rel(OUT_CSV): sha256(OUT_CSV),
                   **{v["arquivo"]: sha256(ROOT / v["arquivo"]) for v in info.values()}},
        "n_linhas": int(len(df)),
        "linguagem": "pacote do corte; preferência revelada; pós-resultado; não detectamos aumento do preenchimento",
    }
    gravar_texto(OUT_RESUMO, json.dumps(resumo, ensure_ascii=False, indent=2, sort_keys=False) + "\n")
    if DOC.exists():
        atualizar_doc()
    print(f"H2: {len(df)} linhas; figuras {sorted(info)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
