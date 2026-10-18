"""E6 do protocolo multi-outcome da bolsa: estimação das famílias F0, F1, F2 e F4.

Protocolo congelado: `docs/06_execucao/40_protocolo_multioutcome_rdd_bolsa.md`
(§§3–9 e adendos §§12–15) e `output/rdd_bolsa/protocolo_E6_multioutcome.json`.
Outcomes: `output/rdd_bolsa/outcomes/` (tarefa B, doc 41a). Estimadores:
`scripts/rdd_bolsa/rdd_lib.py` (tarefa A); este script não reimplementa
estimador, só monta as amostras e chama a biblioteca.

Contraste
---------
Salto = lado com bolsa maior (s > c) menos lado com bolsa menor, no IVS 2010
oficial do Ipea (a08) em milésimos; cortes 300 e 400; T = 1[s > c]. Em nível,
a RDD mede o **pacote do corte**: bolsa anunciada de +R$ 5 mil por mês e as
outras regras federais que mudam nos mesmos cortes (protocolo §13; auditoria
18). Não é efeito da participação no PMM-E nem do Agora Tem Especialistas.

Ordem de execução (falha fechada)
---------------------------------
1. Running variable e populações só pelas colunas de chave (co_ibge, IVS,
   ciclo, faixa): IVS das saídas da tarefa B igual ao a08; primeiro estágio
   sharp em V1–V3.
2. Diagnósticos sem outcome, gravados antes de ler qualquer outcome:
   suporte, densidade (Poisson em mass points, E3) e balanço de covariáveis
   oficiais (§8) por população; seleção da janela de local randomization
   (regra do E5, só covariáveis) para U, G3 e V3; V1 e V2 leem a janela de
   `E5_lr_selecao_janela.csv`, e a mesma regra recalculada tem de reproduzi-la.
3. Outcomes e todas as especificações do protocolo (lista em `especificacoes`
   do resumo). Nada é escolhido depois de ver resultado.
4. Conferências: as linhas de F1.3 (ciclo 1) e F2.3 (ciclos 1 e 2) reproduzem
   `E3_estimativas.csv`; local randomization, ponderado, nível célula e ciclos
   empilhados reproduzem as linhas correspondentes de `E5_especificacoes.csv`.
   Divergência interrompe antes de gravar as estimativas.
5. q-valores BKY por família; p de P1 registrado para o Holm com P2 (E7).

Saídas em output/rdd_bolsa/
---------------------------
E6_diagnosticos.csv, E6_lr_selecao_janela.csv (antes dos outcomes),
E6_estimativas.csv, E6_resumo.json, E6_figuras/*.png.

Uso
---
    python3 scripts/rdd_bolsa/13_estimar_E6_funil.py
    python3 scripts/rdd_bolsa/13_estimar_E6_funil.py --atualizar-doc

`--atualizar-doc` regrava, a partir das saídas, as tabelas entre marcadores de
`docs/06_execucao/41_resultados_E6_funil.md` (nenhum número é digitado no doc).
As funções puras são importáveis pelo teste sintético (`tests/test_e6_funil.py`).
"""

from __future__ import annotations

import argparse
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
L = _importar(DIR_RDD / "rdd_lib.py", "rdd_lib_e6")
E3 = _importar(DIR_RDD / "07_estimar_E3_rdd_completa.py", "e3_para_e6")
E5 = _importar(DIR_RDD / "11_inferencia_alternativa.py", "e5_para_e6")
sys.dont_write_bytecode = _bytecode

# ---------------------------------------------------------------------------
# Caminhos e parâmetros do protocolo (constantes permitidas: cortes, h, sementes)
# ---------------------------------------------------------------------------

OUT = ROOT / "output" / "rdd_bolsa"
OUTC = OUT / "outcomes"
A08 = ROOT / "output" / "aquisicao" / "a08_ivs_2010_oficial_municipio.csv"
POP22 = ROOT / "output" / "aquisicao" / "populacao_censo2022_municipios.csv"
TIPOLOGIA = ROOT / "output" / "tema_trabalho" / "matriz_tipologia_territorial.parquet"
PROTOCOLO_JSON = OUT / "protocolo_E6_multioutcome.json"
PROTOCOLO_MD = ROOT / "docs" / "06_execucao" / "40_protocolo_multioutcome_rdd_bolsa.md"
DICIONARIO = OUTC / "dicionario_outcomes_funil.json"
ARQ_U = OUTC / "outcomes_U_municipio.parquet"
ARQ_G3 = OUTC / "outcomes_G3_municipio.parquet"
ARQ_VM = OUTC / "outcomes_V_municipio.parquet"
ARQ_VC = OUTC / "outcomes_V_celula.parquet"
E3_EST = OUT / "E3_estimativas.csv"
E5_SEL = OUT / "E5_lr_selecao_janela.csv"
E5_ESP = OUT / "E5_especificacoes.csv"
E4_MUN = OUT / "E4_proporcao_municipio.csv"
PPF_ZIP = ROOT / "data" / "raw" / "aquisicao" / "ivs_administrativo" / "ppf_mais_medicos_csv.zip"
A10_IED = ROOT / "output" / "aquisicao" / "a10_ied_aps_2024_municipio.csv"
A10_DIAG = ROOT / "output" / "aquisicao" / "a10_diagnostico_cortes_normas.json"
DOC41 = ROOT / "docs" / "06_execucao" / "41_resultados_E6_funil.md"

NOME_EST = "E6_estimativas.csv"
NOME_DIAG = "E6_diagnosticos.csv"
NOME_LR = "E6_lr_selecao_janela.csv"
NOME_RESUMO = "E6_resumo.json"
DIR_FIG = "E6_figuras"

DATA_EXECUCAO = "2026-10-18"
CORTES = L.CORTES_MIL                     # (300, 400)
H = L.H_PRINCIPAL_MIL                     # 50
H_SENS = L.H_SENSIBILIDADE_MIL            # (30, 80)
FATORES_M = (0.5, 1.0, 2.0)
ROTULO_CORTE = {300: "0.300", 400: "0.400"}
EMPILHADO = "empilhado"
# Identificador de população na semente da local randomization: V1 e V2 usam
# os do E5 (P1 = 1, P2 = 2) para reproduzi-lo; os demais são novos.
ID_SEMENTE_POP = {"V1": 1, "V2": 2, "V3": 3, "U": 4, "G3": 5}
# Classes de porte onde o estrato IED da APS muda no corte (protocolo §13);
# o script recalcula a partir do a10 e para se divergir.
PORTES_MUDA_PROTOCOLO = {300: {2, 3}, 400: {1, 2, 4}}
ESTRATO_IED_CODIGO = {300: (4, 3), 400: (3, 2)}   # código IVS da Portaria abaixo e acima do corte
COMPONENTES_INDICE = ["F1.1", "F1.2", "F1.3", "F2.1"]
# Referências de magnitude do protocolo §7 (parâmetros, não resultados).
REFERENCIA_PREENCHIMENTO = 0.10      # +10 p.p.
REFERENCIA_CANDIDATURAS = 0.25       # +25%
FAMILIAS_BKY = ("F0", "F1", "F2", "F4")
ADICIONAL = "ESPECIFICACAO_ADICIONAL_AO_PROTOCOLO"

CONTRASTE = (
    "pacote do corte: anúncio de +R$ 5 mil por mês na bolsa (0,300: R$ 10 mil -> 15 mil; 0,400: R$ 15 mil -> "
    "20 mil) mais as outras regras federais que mudam nos mesmos cortes (protocolo §13, auditoria 18); "
    "não é efeito da participação no PMM-E nem do Agora Tem Especialistas"
)

UNIDADES = {
    "binario": "fracao (x100 = p.p.)",
    "proporcao": "fracao (x100 = p.p.)",
    "contagem_celula": "contagem por celula oferecida",
    "taxa_hab": "contagem por 10 mil habitantes",
    "contagem": "contagem por municipio",
    "continuo": "pontos da pontuacao do ciclo",
    "indice": "desvios-padrao (indice)",
}
UNIDADE_LOG = "log (salto no log da taxa; exp(tau)-1 = efeito relativo)"

# ---------------------------------------------------------------------------
# Catálogo de outcomes (protocolo §5) — fixado antes de ler outcomes
# ---------------------------------------------------------------------------

CATALOGO: list[dict] = [
    # F0: diagnósticos de seleção e co-intervenção
    {"id": "F0.1", "familia": "F0", "col": "f0_1_tem_celula_c{k}", "pop": "U", "ciclos": (1, 2, 3), "tipo": "binario",
     "desc": "município tem >= 1 célula no quadro do ciclo k"},
    {"id": "F0.2", "familia": "F0", "col": "f0_2_celulas_por_10k_c{k}", "pop": "U", "ciclos": (1, 2, 3),
     "tipo": "taxa_hab", "poisson": ("n_celulas_c{k}", "populacao_2022", 1e4),
     "desc": "células do quadro do ciclo k por 10 mil hab."},
    {"id": "F0.2", "familia": "F0", "col": "f0_2_vagas_imediatas_por_10k_c{k}", "pop": "U", "ciclos": (1, 2, 3),
     "tipo": "taxa_hab", "poisson": ("vagas_imediatas_c{k}", "populacao_2022", 1e4),
     "desc": "vagas imediatas do quadro do ciclo k por 10 mil hab."},
    {"id": "F0.3", "familia": "F0", "col": "f0_3a_consta_do_resultado_final_adesao", "pop": "G3", "ciclos": (3,),
     "tipo": "binario", "desc": "consta do resultado final da adesão do ciclo 3"},
    {"id": "F0.3", "familia": "F0", "col": "f0_3_vagas_pedidas", "pop": "G3", "ciclos": (3,), "tipo": "contagem",
     "poisson": ("f0_3_vagas_pedidas", "populacao_2022", 1e4), "condicional": "consta do resultado final da adesão",
     "desc": "vagas pedidas na adesão do ciclo 3 (só quem consta)"},
    {"id": "F0.3", "familia": "F0", "col": "f0_3_fracao_priorizada", "pop": "G3", "ciclos": (3,), "tipo": "proporcao",
     "peso": "f0_3_vagas_pedidas", "condicional": "consta do resultado final da adesão",
     "desc": "fração das vagas pedidas que foi priorizada (só quem consta)"},
    {"id": "F0.3", "familia": "F0", "col": "f0_3_vagas_imediatas_priorizadas", "pop": "G3", "ciclos": (3,),
     "tipo": "contagem", "poisson": ("f0_3_vagas_imediatas_priorizadas", "populacao_2022", 1e4),
     "condicional": "consta do resultado final da adesão",
     "desc": "vagas imediatas priorizadas na adesão do ciclo 3 (só quem consta)"},
    {"id": "F0.4", "familia": "F0", "col": "f0_4_pmmb_vagas_por_10k", "pop": "U", "ciclos": (None,),
     "tipo": "taxa_hab", "poisson": ("pmmb_vagas_ativas", "populacao_2022", 1e4),
     "desc": "PMMB: vagas ativas por 10 mil hab. (retrato de 09/10/2026)"},
    {"id": "F0.4", "familia": "F0", "col": "f0_4_pmmb_medicos_por_10k", "pop": "U", "ciclos": (None,),
     "tipo": "taxa_hab", "poisson": ("pmmb_medicos_ativos", "populacao_2022", 1e4),
     "desc": "PMMB: médicos ativos por 10 mil hab. (retrato de 09/10/2026)"},
    # F1: atração
    {"id": "F1.1", "familia": "F1", "col": "f1_1_cand_1a_opcao_por_celula", "pop": "V", "ciclos": (1, 2, 3),
     "tipo": "contagem_celula", "poisson": ("n_cand_1a_opcao", "n_celulas", 1.0),
     "desc": "candidatos de 1a opção por célula oferecida"},
    {"id": "F1.2", "familia": "F1", "col": "f1_2_fracao_celulas_com_candidato", "pop": "V", "ciclos": (1, 2, 3),
     "tipo": "proporcao", "peso": "n_celulas", "celula": "f1_2_tem_candidato",
     "desc": "fração de células com >= 1 candidato (qualquer opção)"},
    {"id": "F1.3", "familia": "F1", "col": "f1_3_fracao_celulas_preenchidas_ch1", "pop": "V", "ciclos": (1, 2, 3),
     "tipo": "proporcao", "peso": "n_celulas", "celula": "f1_3_preenchida_ch1",
     "desc": "fração de células preenchidas na 1a chamada"},
    {"id": "F1.4", "familia": "F1", "col": "f1_4_fracao_celulas_preenchidas_ate_ch2", "pop": "V", "ciclos": (1, 2),
     "tipo": "proporcao", "peso": "n_celulas", "celula": "f1_4_preenchida_ate_ch2",
     "desc": "fração de células preenchidas até a 2a chamada"},
    # F2: presença
    {"id": "F2.1", "familia": "F2", "col": "f2_1_ativos_por_celula", "pop": "V", "ciclos": (1, 2),
     "tipo": "contagem_celula", "poisson": ("n_ativos_ciclo", "n_celulas", 1.0),
     "desc": "especialistas ativos do ciclo em 09/10/2026 por célula oferecida"},
    {"id": "F2.2", "familia": "F2", "col": "f2_2_ativos_pmme_por_10k_c{k}", "pop": "U", "ciclos": (1, 2),
     "tipo": "taxa_hab", "poisson": ("n_ativos_pmme_c{k}", "populacao_2022", 1e4),
     "desc": "especialistas ativos do ciclo k por 10 mil hab. (zeros fora do quadro)"},
    {"id": "F2.3", "familia": "F2", "col": "f2_3_d_k_algum_ativo_do_ciclo", "pop": "V", "ciclos": (1, 2),
     "tipo": "binario", "desc": "D_k: >= 1 especialista ativo do ciclo (âncora do E3)"},
    # F4: seleção de quem chega
    {"id": "F4.1", "familia": "F4", "col": "f4_1_pontuacao_media_alocados", "pop": "V", "ciclos": (1, 2, 3),
     "tipo": "continuo", "lee": "n_celulas_preenchidas_ch1", "condicional": "município com >= 1 célula preenchida",
     "desc": "pontuação média dos alocados na 1a chamada (condicional a preencher)"},
    {"id": "F4.2", "familia": "F4", "col": "f4_2_pontuacao_media_cand_1a_opcao", "pop": "V", "ciclos": (1, 2, 3),
     "tipo": "continuo", "condicional": "município com >= 1 candidato de 1a opção pontuado",
     "desc": "pontuação média dos candidatos de 1a opção"},
    # S1: primeiro estágio do confundidor (adendo §13; auditoria 18 §5.2)
    {"id": "S1", "familia": "S1", "col": "s1_pmmb_coparticipacao_por_10k", "pop": "U", "ciclos": (None,),
     "tipo": "taxa_hab", "poisson": ("pmmb_ativas_coparticipacao", "populacao_2022", 1e4),
     "desc": "PMMB: vagas ativas em coparticipação por 10 mil hab. (retrato de 09/10/2026)"},
]

# Sensibilidades de construção definidas pela tarefa B (só especificação principal).
SENS_CONSTRUCAO: list[dict] = [
    {"id": "F0.1", "familia": "F0", "col": "f0_1s_tem_celula_c1_ch1_ou_ch2", "pop": "U", "ciclos": (1,),
     "tipo": "binario", "desc": "sensibilidade B: célula na 1a ou 2a chamada do ciclo 1"},
    {"id": "F1.1", "familia": "F1", "col": "f1_1s_cand_1a_opcao_com_pre_requisito_por_celula", "pop": "V",
     "ciclos": (1, 2, 3), "tipo": "contagem_celula", "desc": "sensibilidade B: sem 'SEM PRÉ-REQUISITO'"},
    {"id": "F1.3", "familia": "F1", "col": "f1_3s_fracao_celulas_imediatas_preenchidas_ch1", "pop": "V",
     "ciclos": (1, 2, 3), "tipo": "proporcao", "desc": "sensibilidade B: só células com vaga imediata"},
    {"id": "F1.3", "familia": "F1", "col": "f1_3s_fracao_celulas_preenchidas_ch1_com_remanescentes", "pop": "V",
     "ciclos": (2,), "tipo": "proporcao", "desc": "sensibilidade B: com remanescentes (ciclo 2)"},
    {"id": "F1.3", "familia": "F1", "col": "f1_3s_fracao_celulas_preenchidas_ch1_com_sub_judice", "pop": "V",
     "ciclos": (3,), "tipo": "proporcao", "desc": "sensibilidade B: com 'SUB JUDICE' (ciclo 3)"},
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


def _nan_none(obj):
    if isinstance(obj, dict):
        return {str(k): _nan_none(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_nan_none(v) for v in obj]
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


def _col(spec: dict, k) -> str:
    return spec["col"].format(k=k) if k is not None else spec["col"]


def _fmt_ciclo(k) -> str:
    if k is None:
        return "-"
    if isinstance(k, (list, tuple)):
        return "+".join(str(x) for x in k)
    return str(k)


# ---------------------------------------------------------------------------
# Linhas de saída
# ---------------------------------------------------------------------------

COLUNAS_SAIDA = [
    "natureza_dos_dados", "familia", "outcome_id", "outcome", "descricao_outcome", "populacao", "ciclo", "corte",
    "especificacao", "estimador", "no_protocolo", "rotulo", "status", "h", "n_abaixo", "n_acima", "n_obs",
    "n_clusters", "tau", "ep", "ic95_inf", "ic95_sup", "p_valor", "ic_honesto_inf", "ic_honesto_sup", "M",
    "fator_M", "vies_max", "efeito_relativo", "efeito_relativo_ic95_inf", "efeito_relativo_ic95_sup",
    "lee_tau_inf", "lee_tau_sup", "lee_q_aparo", "w_lr", "media_bruta_abaixo", "media_bruta_acima",
    "pesos_grupos", "entra_bky", "q_bky", "unidade", "nota",
]


def nova_linha(meta: dict, especificacao: str, estimador: str, *, no_protocolo: bool, h_mil, unidade: str,
               rotulo_esp: str = "") -> dict:
    linha = {c: np.nan for c in COLUNAS_SAIDA}
    linha.update({"natureza_dos_dados": "EMPIRICO", **meta, "especificacao": especificacao, "estimador": estimador,
                  "no_protocolo": bool(no_protocolo), "rotulo": rotulo_esp,
                  "h": (h_mil / 1000.0) if h_mil is not None and np.isfinite(h_mil) else np.nan,
                  "unidade": unidade, "nota": "", "entra_bky": False, "status": "EXECUTADO"})
    return linha


def preencher(linha: dict, res: dict | None) -> dict:
    if res is None:
        return linha
    for k in ("tau", "ep", "ic95_inf", "ic95_sup", "p_valor", "n_abaixo", "n_acima", "n_obs", "n_clusters",
              "media_bruta_abaixo", "media_bruta_acima", "efeito_relativo", "efeito_relativo_ic95_inf",
              "efeito_relativo_ic95_sup"):
        if k in res and res[k] is not None:
            linha[k] = res[k]
    if res.get("pesos_grupos"):
        linha["pesos_grupos"] = json.dumps({k: round(v, 12) for k, v in res["pesos_grupos"].items()})
    notas = [n for n in (linha.get("nota", ""), res.get("nota", "")) if n]
    if res.get("covariaveis_descartadas"):
        notas.append(f"colunas descartadas: {res['covariaveis_descartadas']}")
    linha["nota"] = "; ".join(notas)
    if not np.isfinite(float(linha["tau"]) if linha["tau"] is not None else np.nan):
        linha["status"] = "SEM_ESTIMATIVA"
        if not linha["nota"]:
            linha["nota"] = "biblioteca devolveu NaN sem motivo"
    return linha


def nao_executado(meta: dict, especificacao: str, estimador: str, motivo: str, *, no_protocolo: bool, unidade: str,
                  h_mil=H) -> dict:
    linha = nova_linha(meta, especificacao, estimador, no_protocolo=no_protocolo, h_mil=h_mil, unidade=unidade)
    linha["status"] = "NAO_EXECUTADO"
    linha["nota"] = motivo
    return linha


def anexar_honesto(linha: dict, hon: dict) -> None:
    linha["ic_honesto_inf"] = hon.get("ic95_inf", np.nan)
    linha["ic_honesto_sup"] = hon.get("ic95_sup", np.nan)
    linha["M"] = hon.get("M", np.nan)
    linha["fator_M"] = 1.0
    if not np.isfinite(linha["ic_honesto_inf"]):
        linha["nota"] = "; ".join(x for x in (linha["nota"], f"IC honesto indefinido: {hon.get('nota', '')}") if x)


def linha_honesta(meta: dict, hon: dict, *, fator: float, h_otimo: bool, unidade: str, estimador: str) -> dict:
    esp = "ic_honesto_h_otimo" if h_otimo else "ic_honesto"
    linha = nova_linha(meta, esp, estimador, no_protocolo=not h_otimo, h_mil=hon.get("h_mil", H), unidade=unidade,
                       rotulo_esp=L.ROTULO_H_OTIMO if h_otimo else "")
    for k in ("tau", "ep", "ic95_inf", "ic95_sup", "p_valor", "n_abaixo", "n_acima", "M", "vies_max"):
        v = hon.get(k)
        if v is not None:
            linha[k] = v
    linha["ic_honesto_inf"], linha["ic_honesto_sup"] = linha["ic95_inf"], linha["ic95_sup"]
    linha["fator_M"] = fator
    linha["nota"] = "; ".join(x for x in (
        "IC com viés limitado (Armstrong-Kolesar, classe de Taylor); ep = EP usado no IC honesto; "
        f"M = {fator:g} x regra de bolso (suporte ate o ponto medio entre cortes)", hon.get("nota", "")) if x)
    if not np.isfinite(float(linha["ic95_inf"])):
        linha["status"] = "SEM_ESTIMATIVA"
    return linha


# ---------------------------------------------------------------------------
# Estimação por corte (uma população, um ciclo)
# ---------------------------------------------------------------------------

def _amostra(d: pd.DataFrame, col: str) -> tuple[np.ndarray, np.ndarray]:
    return d["s_mil"].to_numpy(dtype=float), d[col].to_numpy(dtype=float)


def _em_01(y: np.ndarray) -> bool:
    v = y[np.isfinite(y)]
    return bool(v.size and v.min() >= 0 and v.max() <= 1)


def local_randomization(meta: dict, d: pd.DataFrame, col: str, corte: int, w_mil, id_pop: int, unidade: str,
                        motivo_sem_janela: str = "") -> dict:
    est = "local randomization: diferenca de medias na janela (c-w, c+w], p de Fisher (10.000 permutacoes)"
    if w_mil is None or not np.isfinite(w_mil):
        return nao_executado(meta, "local_randomization", est,
                             motivo_sem_janela or "nenhuma janela candidata passou no balanco (regra do E5)",
                             no_protocolo=True, unidade=unidade, h_mil=np.nan)
    w = int(w_mil)
    s, y = _amostra(d, col)
    semente = (L.SEMENTE, id_pop, int(corte), w)
    r = L.rl_janela(s, y, corte, w, semente=semente)
    linha = nova_linha(meta, "local_randomization", est, no_protocolo=True, h_mil=w, unidade=unidade)
    linha["w_lr"] = w / 1000.0
    linha.update({"tau": r["tau"], "p_valor": r["p_valor"], "ep": r["ep_permutacao"], "n_abaixo": r["n_abaixo"],
                  "n_acima": r["n_acima"], "n_obs": (r["n_abaixo"] or 0) + (r["n_acima"] or 0)})
    notas = ["ep = DP da distribuicao de permutacao sob o nulo exato", f"semente {list(semente)}"]
    x = s - corte
    dentro = (x > -w) & (x <= w)
    sem_y = int((dentro & ~np.isfinite(y)).sum())
    if sem_y:
        notas.append(f"{sem_y} municipios da janela sem outcome (fora da amostra)")
    ok = dentro & np.isfinite(y)
    if _em_01(y) and ok.sum() >= 2 and (x[ok] > 0).any() and (x[ok] <= 0).any():
        t = x[ok] > 0
        P = E5.matriz_permutacao(int(ok.sum()), int(t.sum()), L.N_PERMUTACOES, semente)
        inf = E5.inferencia_lr(y[ok], t, P)
        if abs(inf["p_valor"] - r["p_valor"]) > 1e-12 or abs(inf["tau"] - r["tau"]) > 1e-12:
            raise FalhaValidacao("local randomization: rdd_lib e E5 divergem com a mesma semente")
        linha["ic95_inf"], linha["ic95_sup"] = inf["ic95_inf"], inf["ic95_sup"]
        notas.append("IC 95% por inversao do teste de Fisher sob efeito aditivo constante (grade do E5, passo 0,001)")
        if not inf["ic_contiguo"]:
            notas.append("regiao de aceitacao nao contigua: IC = envoltoria")
    else:
        notas.append("IC por inversao nao calculado: a grade do E5 so cobre outcomes em [0, 1]")
    if r.get("nota"):
        notas.append(r["nota"])
    linha["nota"] = "; ".join(notas)
    if not np.isfinite(linha["tau"]):
        linha["status"] = "SEM_ESTIMATIVA"
    return linha


def estimar_por_corte(spec: dict, meta_base: dict, d: pd.DataFrame, corte: int, *, cel: pd.DataFrame | None = None,
                      w_lr=None, motivo_sem_janela: str = "", id_pop: int = 0, protocolo: bool = True,
                      bky: bool = True, suplementares: dict | None = None) -> list[dict]:
    """Todas as especificações de um outcome x população x ciclo em um corte."""
    col = spec["_col"]
    unidade = UNIDADES[spec["tipo"]]
    meta = {**meta_base, "corte": ROTULO_CORTE[corte]}
    s, y = _amostra(d, col)
    linhas = []
    est_ll = "local linear sharp, kernel triangular, EP HC1 por municipio"
    # Principal (+ IC honesto anexado).
    r = L.rd_local_linear(s, y, corte, H)
    esp_p = "principal" if protocolo else "sensibilidade_construcao"
    lp = preencher(nova_linha(meta, esp_p, est_ll, no_protocolo=protocolo, h_mil=H, unidade=unidade,
                              rotulo_esp="" if protocolo else ADICIONAL), r)
    lp["entra_bky"] = bool(bky and lp["status"] == "EXECUTADO")
    linhas.append(lp)
    if not protocolo:
        return linhas
    # Sensibilidade de h.
    for h in H_SENS:
        r = L.rd_local_linear(s, y, corte, h)
        linhas.append(preencher(nova_linha(meta, "sensibilidade_h", est_ll, no_protocolo=True, h_mil=h,
                                           unidade=unidade), r))
    # IC honesto: h fixo (protocolo) e h ótimo (adicional), M x {0,5; 1; 2}.
    est_hon = "local linear triangular; IC honesto Armstrong-Kolesar (variancia por vizinhos, J=3)"
    try:
        tab = L.rd_honesto_relato(s, y, corte, fatores_M=FATORES_M, cortes_vizinhos=CORTES)
    except ValueError as erro:
        tab = None
        lp["nota"] = "; ".join(x for x in (lp["nota"], f"IC honesto nao calculado: {erro}") if x)
    if tab is not None:
        for rec in tab.to_dict("records"):
            otimo = rec["especificacao"] == "h_otimo"
            linhas.append(linha_honesta(meta, rec, fator=rec["fator_M"], h_otimo=otimo, unidade=unidade,
                                        estimador=est_hon))
            if not otimo and rec["fator_M"] == 1.0:
                anexar_honesto(lp, rec)
    # Local randomization na janela do E5 (regra de balanço).
    linhas.append(local_randomization(meta, d, col, corte, w_lr, id_pop, unidade, motivo_sem_janela))
    # Estimadores por tipo.
    if "poisson" in spec:
        cnt, expo, escala = spec["_poisson"]
        off = np.log(d[expo].to_numpy(dtype=float) / escala)
        rp = L.rd_poisson_local(s, d[cnt].to_numpy(dtype=float), corte, H, offset=off)
        lpo = preencher(nova_linha(meta, "poisson_local",
                                   f"Poisson local (IRLS), kernel triangular, offset log({expo}"
                                   f"{'/1e4' if escala != 1 else ''}), EP HC1", no_protocolo=True, h_mil=H,
                                   unidade=UNIDADE_LOG), rp)
        linhas.append(lpo)
    if "peso" in spec:
        rw = L.rd_local_linear(s, y, corte, H, peso=d[spec["peso"]].to_numpy(dtype=float))
        linhas.append(preencher(nova_linha(meta, "ponderado_celulas",
                                           f"local linear triangular x peso {spec['peso']}, EP HC1", no_protocolo=True,
                                           h_mil=H, unidade=unidade), rw))
    if "celula" in spec:
        if cel is None:
            linhas.append(nao_executado(meta, "nivel_celula", "celula CNES-curso, CR1 por municipio",
                                        "sem tabela de celulas para esta populacao", no_protocolo=True,
                                        unidade=unidade))
        else:
            rc = L.rd_local_linear(cel["s_mil"].to_numpy(dtype=float), cel[spec["celula"]].to_numpy(dtype=float),
                                   corte, H, cluster=cel["co_ibge"].to_numpy(), ids_unidade=cel["co_ibge"].to_numpy())
            linhas.append(preencher(nova_linha(meta, "nivel_celula",
                                               f"celula CNES-curso ({spec['celula']}), peso = kernel do municipio, "
                                               "EP CR1 por municipio", no_protocolo=True, h_mil=H, unidade=unidade),
                                    rc))
    if "lee" in spec:
        sel = (d[spec["lee"]].to_numpy(dtype=float) > 0).astype(float)
        rl = L.limites_lee_rd(s, y, sel, corte, H)
        ll = nova_linha(meta, "limites_lee", f"limites de Lee locais (selecionado = {spec['lee']} > 0)",
                        no_protocolo=True, h_mil=H, unidade=unidade)
        ll.update({"ic95_inf": rl["ic95_inf"], "ic95_sup": rl["ic95_sup"], "lee_tau_inf": rl["tau_inf"],
                   "lee_tau_sup": rl["tau_sup"], "lee_q_aparo": rl["q_aparo"], "n_abaixo": rl["n_abaixo"],
                   "n_acima": rl["n_acima"]})
        ll["nota"] = "; ".join(x for x in (
            "tau e ep nao se aplicam: o efeito so e limitado (lee_tau_inf, lee_tau_sup); IC 95% conservador de Lee",
            f"salto na selecao = {rl['salto_selecao']:.6g}; lado aparado = {rl['lado_aparado']}",
            rl.get("nota", "")) if x)
        if not np.isfinite(rl["tau_inf"]):
            ll["status"] = "SEM_ESTIMATIVA"
        linhas.append(ll)
    # Suplementares S2–S4.
    linhas.extend(suplementares_por_corte(meta, d, col, corte, unidade, suplementares or {}))
    return linhas


def _rd_dif(a: dict, b: dict) -> dict:
    """Diferença de saltos entre subamostras disjuntas de municípios (EPs independentes)."""
    tau = a["tau"] - b["tau"]
    ep = math.sqrt(a["ep"] ** 2 + b["ep"] ** 2) if np.isfinite(a["ep"]) and np.isfinite(b["ep"]) else np.nan
    res = {"tau": tau, "ep": ep, "ic95_inf": tau - L.Z_975 * ep, "ic95_sup": tau + L.Z_975 * ep,
           "p_valor": L.p_normal(tau / ep) if ep and np.isfinite(ep) and ep > 0 else np.nan,
           "n_abaixo": (a["n_abaixo"] or 0) + (b["n_abaixo"] or 0), "n_acima": (a["n_acima"] or 0) + (b["n_acima"] or 0),
           "nota": "diferenca entre subamostras disjuntas de municipios; EP = raiz da soma das variancias"}
    if not np.isfinite(tau):
        res["nota"] += "; algum dos saltos indefinido: " + "; ".join(x for x in (a.get("nota"), b.get("nota")) if x)
    return res


def suplementares_por_corte(meta: dict, d: pd.DataFrame, col: str, corte: int, unidade: str, sup: dict,
                            *, estimar=None) -> list[dict]:
    """S2 (donut), S3 (porte IED muda x não muda) e S4 (Amazônia Legal/fronteira, só 0,400).

    `estimar(dsub) -> dict` é o estimador principal na subamostra (padrão:
    local linear do corte); é trocado pelo empilhado nas amostras empilhadas.
    """
    if estimar is None:
        def estimar(dsub):
            return L.rd_local_linear(dsub["s_mil"].to_numpy(dtype=float), dsub[col].to_numpy(dtype=float), corte, H)
    linhas = []
    est = "estimador principal na subamostra"
    # S2: donut.
    donut = d[~d["s_mil"].isin(list(CORTES))]
    linha = preencher(nova_linha(meta, "S2_donut", f"{est}: exclui IVS == 0,300 e == 0,400", no_protocolo=True,
                                 h_mil=H, unidade=unidade), estimar(donut))
    linha["nota"] = "; ".join(x for x in (f"{len(d) - len(donut)} linhas excluidas (IVS exatamente no corte)",
                                          linha["nota"]) if x)
    linhas.append(linha)
    # S3: classe de porte da Portaria 3.493/2024.
    s3 = sup.get("S3")
    nomes3 = ("S3_porte_muda", "S3_porte_nao_muda", "S3_diferenca")
    if s3 is None or s3.get("tabela") is None:
        motivo = (s3 or {}).get("motivo", "insumo do S3 indisponivel")
        linhas.extend(nao_executado(meta, n, est, motivo, no_protocolo=True, unidade=unidade) for n in nomes3)
    else:
        porte = d["co_ibge"].map(s3["tabela"])
        muda = porte.isin(s3["portes_muda"][corte])
        sem = int(porte.isna().sum())
        ra, rb = estimar(d[muda & porte.notna()]), estimar(d[~muda & porte.notna()])
        txt = f"portes onde o estrato IED muda em {ROTULO_CORTE[corte]}: {sorted(s3['portes_muda'][corte])}"
        for nome, rr in zip(nomes3, (ra, rb, _rd_dif(ra, rb))):
            ln = preencher(nova_linha(meta, nome, f"{est}; {txt}", no_protocolo=True, h_mil=H, unidade=unidade), rr)
            if sem:
                ln["nota"] = "; ".join(x for x in (ln["nota"], f"{sem} municipios sem porte no a10 (fora)") if x)
            linhas.append(ln)
    # S4: só em 0,400.
    if corte == 400:
        s4 = sup.get("S4")
        nomes4 = ("S4_dentro", "S4_fora", "S4_diferenca")
        if s4 is None or s4.get("tabela") is None:
            motivo = (s4 or {}).get("motivo", "insumo do S4 indisponivel")
            linhas.extend(nao_executado(meta, n, est, motivo, no_protocolo=True, unidade=unidade) for n in nomes4)
        else:
            flag = d["co_ibge"].map(s4["tabela"])
            sem = int(flag.isna().sum())
            dentro = flag == 1
            ra, rb = estimar(d[dentro & flag.notna()]), estimar(d[~dentro & flag.notna()])
            for nome, rr in zip(nomes4, (ra, rb, _rd_dif(ra, rb))):
                ln = preencher(nova_linha(meta, nome, f"{est}; {s4['definicao']}", no_protocolo=True, h_mil=H,
                                          unidade=unidade), rr)
                if sem:
                    ln["nota"] = "; ".join(x for x in (ln["nota"], f"{sem} municipios sem atributo (fora)") if x)
                linhas.append(ln)
    return linhas


# ---------------------------------------------------------------------------
# Estimação empilhada (cortes e/ou ciclos)
# ---------------------------------------------------------------------------

def empilhar(partes: list[tuple[pd.DataFrame, int, str]], cols: list[str]) -> pd.DataFrame:
    """Concatena (dados, corte, grupo) com corte_mil e grupo."""
    blocos = []
    for d, corte, grupo in partes:
        b = d[["co_ibge", "s_mil"] + [c for c in cols if c in d.columns]].copy()
        b["corte_mil"] = corte
        b["grupo"] = grupo
        blocos.append(b)
    return pd.concat(blocos, ignore_index=True)


def estimar_empilhado(spec: dict, meta: dict, emp: pd.DataFrame, *, emp_cel: pd.DataFrame | None = None,
                      protocolo: bool = True, bky: bool = True, suplementares: dict | None = None,
                      corte_unico: int | None = None) -> list[dict]:
    """Especificações de uma amostra empilhada (r = s - c; intercepto e inclinações por grupo x lado; CR1)."""
    col = spec["_col"]
    unidade = UNIDADES[spec["tipo"]]
    linhas = []
    est = "empilhado: local linear triangular, intercepto e inclinacoes por grupo x lado, tau comum, CR1 por municipio"

    def rodar(e: pd.DataFrame, h=H, coluna=col, **kw):
        return L.rd_empilhado(e["s_mil"].to_numpy(dtype=float), e[coluna].to_numpy(dtype=float),
                              e["corte_mil"].to_numpy(dtype=float), grupo=e["grupo"].to_numpy(), h_mil=h,
                              cluster=e["co_ibge"].to_numpy(), ids_unidade=e["co_ibge"].to_numpy(), **kw)

    esp_p = "principal" if protocolo else "sensibilidade_construcao"
    lp = preencher(nova_linha(meta, esp_p, est, no_protocolo=protocolo, h_mil=H, unidade=unidade,
                              rotulo_esp="" if protocolo else ADICIONAL), rodar(emp))
    lp["entra_bky"] = bool(bky and lp["status"] == "EXECUTADO")
    linhas.append(lp)
    if not protocolo:
        return linhas
    for h in H_SENS:
        linhas.append(preencher(nova_linha(meta, "sensibilidade_h", est, no_protocolo=True, h_mil=h, unidade=unidade),
                                rodar(emp, h)))
    # IC honesto empilhado: M = máximo da regra de bolso por grupo; fatores 0,5; 1; 2 (h fixo).
    s, y = emp["s_mil"].to_numpy(dtype=float), emp[col].to_numpy(dtype=float)
    c, g, cl = emp["corte_mil"].to_numpy(dtype=float), emp["grupo"].to_numpy(), emp["co_ibge"].to_numpy()
    est_hon = "empilhado; IC honesto Armstrong-Kolesar (variancia CR1)"
    try:
        base = L.rd_empilhado_honesto(s, y, c, grupo=g, h_mil=H, cluster=cl, ids_unidade=cl, cortes_vizinhos=CORTES)
        M0 = base["M"]
        for f in FATORES_M:
            hon = base if f == 1.0 else L.rd_empilhado_honesto(s, y, c, grupo=g, h_mil=H, M=f * M0, cluster=cl,
                                                                 ids_unidade=cl)
            hon = {**hon, "h_mil": H}
            linhas.append(linha_honesta(meta, hon, fator=f, h_otimo=False, unidade=unidade, estimador=est_hon))
            if f == 1.0:
                anexar_honesto(lp, hon)
    except ValueError as erro:
        lp["nota"] = "; ".join(x for x in (lp["nota"], f"IC honesto nao calculado: {erro}") if x)
    if "peso" in spec:
        linhas.append(preencher(nova_linha(meta, "ponderado_celulas", f"{est}; peso {spec['peso']}", no_protocolo=True,
                                           h_mil=H, unidade=unidade), rodar(emp, peso=emp[spec["peso"]].to_numpy(dtype=float))))
    if "celula" in spec:
        if emp_cel is None:
            linhas.append(nao_executado(meta, "nivel_celula", est, "sem tabela de celulas para esta populacao",
                                        no_protocolo=True, unidade=unidade))
        else:
            linhas.append(preencher(nova_linha(meta, "nivel_celula", f"{est}; celula CNES-curso ({spec['celula']})",
                                               no_protocolo=True, h_mil=H, unidade=unidade),
                                    rodar(emp_cel, coluna=spec["celula"])))
    # Suplementares na amostra empilhada.
    sup = suplementares or {}

    def estimar(sub):
        return rodar(sub)

    if corte_unico is None:
        linhas.extend(l for l in suplementares_por_corte(meta, emp, col, 0, unidade, {}, estimar=estimar)
                      if l["especificacao"] == "S2_donut")
    else:
        linhas.extend(suplementares_por_corte(meta, emp, col, corte_unico, unidade, sup, estimar=estimar))
    return linhas


# ---------------------------------------------------------------------------
# Índice de atração-presença (P1)
# ---------------------------------------------------------------------------

def montar_indice(V: dict[int, pd.DataFrame], cols: dict[str, str], metodo: str = "klk") -> tuple[pd.DataFrame, pd.DataFrame]:
    """Linhas ciclo x corte x município de V_k, componentes padronizados pelo lado abaixo na janela h = 50."""
    partes = []
    for k, d in sorted(V.items()):
        for corte in CORTES:
            b = d[["co_ibge", "s_mil"]].copy()
            for comp, c in cols.items():
                b[comp] = d[c].to_numpy(dtype=float) if c in d.columns else np.nan
            b["ciclo"] = k
            b["corte_mil"] = corte
            b["grupo"] = f"c{k}_{corte}"
            partes.append(b)
    dados = pd.concat(partes, ignore_index=True)
    ref = L.mascara_referencia(dados["s_mil"].to_numpy(dtype=float), dados["corte_mil"].to_numpy(dtype=float), H)
    saida, params = L.indice_klk(dados, list(cols), referencia=ref, grupo=dados["grupo"].to_numpy(), metodo=metodo)
    dados["indice"] = saida["indice"].to_numpy()
    dados["n_componentes"] = saida["n_componentes"].to_numpy()
    return dados, params


# ---------------------------------------------------------------------------
# Pipeline de estimação (puro: recebe dados, devolve linhas)
# ---------------------------------------------------------------------------

def _preparar_spec(spec: dict, k) -> dict:
    s = dict(spec)
    s["_col"] = _col(spec, k)
    if "poisson" in spec:
        cnt, expo, esc = spec["poisson"]
        s["_poisson"] = (cnt.format(k=k) if k is not None else cnt, expo, esc)
    return s


def estimar_tudo(dados: dict, *, sup: dict, lr: dict, motivos_lr: dict | None = None,
                 log=print) -> tuple[pd.DataFrame, dict]:
    """Roda todas as especificações. `dados`: U, G3 (DataFrames), V e C (dict ciclo -> DataFrame).

    `lr[(pop, corte)]` = w em milésimos ou None. Devolve (estimativas, extras).
    """
    motivos_lr = motivos_lr or {}
    linhas: list[dict] = []
    extras: dict = {}
    V, C = dados["V"], dados["C"]
    for catalogo, protocolo in ((CATALOGO, True), (SENS_CONSTRUCAO, False)):
        for spec in catalogo:
            for k in spec["ciclos"]:
                sp = _preparar_spec(spec, k)
                meta_o = {"familia": spec["familia"], "outcome_id": spec["id"], "outcome": sp["_col"],
                          "descricao_outcome": spec["desc"] + ("" if protocolo else f" [{ADICIONAL}]")}
                bky = protocolo and spec["familia"] in FAMILIAS_BKY
                if spec["pop"] in ("U", "G3"):
                    pop = spec["pop"]
                    d = dados[pop]
                    if sp["_col"] not in d.columns:
                        continue
                    meta = {**meta_o, "populacao": pop, "ciclo": _fmt_ciclo(k)}
                    for corte in CORTES:
                        linhas.extend(estimar_por_corte(sp, meta, d, corte, w_lr=lr.get((pop, corte)),
                                                        motivo_sem_janela=motivos_lr.get((pop, corte), ""),
                                                        id_pop=ID_SEMENTE_POP[pop], protocolo=protocolo, bky=bky,
                                                        suplementares=sup))
                    emp = empilhar([(d, c, str(c)) for c in CORTES], _cols_spec(sp))
                    linhas.extend(estimar_empilhado(sp, {**meta, "corte": EMPILHADO}, emp, protocolo=protocolo, bky=bky,
                                                    suplementares=sup))
                    continue
                if k not in V or sp["_col"] not in V[k].columns:
                    continue
                pop = f"V{k}"
                d, cel = V[k], C.get(k)
                meta = {**meta_o, "populacao": pop, "ciclo": _fmt_ciclo(k)}
                for corte in CORTES:
                    linhas.extend(estimar_por_corte(sp, meta, d, corte, cel=cel, w_lr=lr.get((pop, corte)),
                                                    motivo_sem_janela=motivos_lr.get((pop, corte), ""),
                                                    id_pop=ID_SEMENTE_POP[pop], protocolo=protocolo, bky=bky,
                                                    suplementares=sup))
                emp = empilhar([(d, c, str(c)) for c in CORTES], _cols_spec(sp))
                emp_cel = empilhar([(cel, c, str(c)) for c in CORTES], _cols_spec(sp)) if (
                    cel is not None and "celula" in sp) else None
                linhas.extend(estimar_empilhado(sp, {**meta, "corte": EMPILHADO}, emp, emp_cel=emp_cel,
                                                protocolo=protocolo, bky=bky, suplementares=sup))
                if protocolo and "lee" in spec:
                    linhas.append(nao_executado({**meta, "corte": EMPILHADO}, "limites_lee",
                                                "limites de Lee empilhados",
                                                "rdd_lib so tem limites de Lee em um corte; relatados por ciclo e corte",
                                                no_protocolo=True, unidade=UNIDADES[spec["tipo"]]))
            # Ciclos empilhados (só V, só protocolo).
            if spec["pop"] == "V" and protocolo:
                ks = [k for k in spec["ciclos"] if k in V and _col(spec, k) in V[k].columns]
                if len(ks) >= 2:
                    linhas.extend(_ciclos_empilhados(spec, ks, V, C, sup))
            log(f"  {spec['id']} {spec['col']}: {len(linhas)} linhas acumuladas")
    # Índice P1.
    lin_ind, extras["indice"] = _estimar_indice(V, C, sup, lr, motivos_lr)
    linhas.extend(lin_ind)
    est = pd.DataFrame(linhas)[COLUNAS_SAIDA]
    est = aplicar_bky(est)
    return est, extras


def _cols_spec(sp: dict) -> list[str]:
    cols = [sp["_col"]]
    if "_poisson" in sp:
        cols += [sp["_poisson"][0], sp["_poisson"][1]]
    for chave in ("peso", "celula", "lee"):
        if chave in sp:
            cols.append(sp[chave])
    return list(dict.fromkeys(cols))


def _ciclos_empilhados(spec: dict, ks: list[int], V: dict, C: dict, sup: dict) -> list[dict]:
    linhas = []
    sp = _preparar_spec(spec, ks[0])
    sp["_col"] = spec["col"]
    pop = "+".join(f"V{k}" for k in ks)
    meta = {"familia": spec["familia"], "outcome_id": spec["id"], "outcome": spec["col"],
            "descricao_outcome": spec["desc"] + " (ciclos empilhados; interceptos por ciclo = EF de ciclo)",
            "populacao": pop, "ciclo": _fmt_ciclo(ks)}
    cols = _cols_spec(sp)
    for corte in CORTES:
        emp = empilhar([(V[k], corte, f"c{k}") for k in ks], cols)
        emp_cel = empilhar([(C[k], corte, f"c{k}") for k in ks], cols) if (
            "celula" in spec and all(k in C for k in ks)) else None
        linhas.extend(estimar_empilhado(sp, {**meta, "corte": ROTULO_CORTE[corte]}, emp, emp_cel=emp_cel,
                                        suplementares=sup, corte_unico=corte))
    emp = empilhar([(V[k], c, f"c{k}_{c}") for k in ks for c in CORTES], cols)
    emp_cel = empilhar([(C[k], c, f"c{k}_{c}") for k in ks for c in CORTES], cols) if (
        "celula" in spec and all(k in C for k in ks)) else None
    linhas.extend(estimar_empilhado(sp, {**meta, "corte": EMPILHADO}, emp, emp_cel=emp_cel, suplementares=sup))
    if "lee" in spec:
        for c in [ROTULO_CORTE[x] for x in CORTES] + [EMPILHADO]:
            linhas.append(nao_executado({**meta, "corte": c}, "limites_lee", "limites de Lee com ciclos empilhados",
                                        "rdd_lib so tem limites de Lee em um corte e um ciclo; relatados por ciclo e "
                                        "corte", no_protocolo=True, unidade=UNIDADES[spec["tipo"]]))
    return linhas


def _estimar_indice(V: dict, C: dict, sup: dict, lr: dict, motivos_lr: dict) -> tuple[list[dict], dict]:
    cols = {}
    for spec in CATALOGO:
        if spec["id"] in COMPONENTES_INDICE and spec["pop"] == "V":
            cols[spec["id"]] = spec["col"]
    linhas = []
    extras = {}
    for metodo in ("klk", "anderson"):
        dados, params = montar_indice(V, cols, metodo)
        extras[metodo] = {"parametros": params.to_dict("records"),
                          "linhas_sem_indice": int(dados["indice"].isna().sum())}
        if metodo == "klk":
            extras["dados_klk"] = dados
        spec = {"id": "P1" if metodo == "klk" else "P1.anderson", "familia": "P1", "col": "indice", "_col": "indice",
                "tipo": "indice"}
        protocolo = metodo == "klk"
        rot = "" if protocolo else "sensibilidade prevista (variante de Anderson, 2008)"
        desc = ("indice de atracao-presenca (KLK): z de F1.1, F1.2, F1.3 e F2.1, padronizados pelo lado abaixo "
                "do corte na janela h = 0,050, por ciclo x corte; + = mais provimento")
        if not protocolo:
            desc = desc.replace("(KLK)", "(Anderson)")
        ks = sorted(V)
        base = {"familia": "P1", "outcome_id": spec["id"], "outcome": f"indice_{metodo}", "descricao_outcome": desc}
        # P1 principal: ciclos e cortes empilhados.
        meta = {**base, "populacao": "+".join(f"V{k}" for k in ks), "ciclo": _fmt_ciclo(ks), "corte": EMPILHADO}
        lin = estimar_empilhado(spec, meta, dados, protocolo=protocolo, bky=False, suplementares=sup)
        if not protocolo:
            lin[0]["especificacao"] = "indice_anderson"
            lin[0]["no_protocolo"] = True
            lin[0]["rotulo"] = rot
        linhas.extend(lin)
        # Por corte, ciclos empilhados.
        for corte in CORTES:
            sub = dados[dados["corte_mil"] == corte]
            m2 = {**meta, "corte": ROTULO_CORTE[corte]}
            lin = estimar_empilhado(spec, m2, sub, protocolo=protocolo, bky=False, suplementares=sup,
                                    corte_unico=corte)
            if not protocolo:
                lin[0]["especificacao"] = "indice_anderson"
                lin[0]["no_protocolo"] = True
                lin[0]["rotulo"] = rot
            linhas.extend(lin)
        # Por ciclo: cortes empilhados e cada corte.
        for k in ks:
            dk = dados[dados["ciclo"] == k]
            mk = {**base, "populacao": f"V{k}", "ciclo": str(k)}
            lin = estimar_empilhado(spec, {**mk, "corte": EMPILHADO}, dk, protocolo=protocolo, bky=False,
                                    suplementares=sup)
            if not protocolo:
                lin[0]["especificacao"] = "indice_anderson"
                lin[0]["no_protocolo"] = True
                lin[0]["rotulo"] = rot
            linhas.extend(lin)
            for corte in CORTES:
                dkc = dk[dk["corte_mil"] == corte].reset_index(drop=True)
                lin = estimar_por_corte(spec, mk, dkc, corte, w_lr=lr.get((f"V{k}", corte)),
                                        motivo_sem_janela=motivos_lr.get((f"V{k}", corte), ""),
                                        id_pop=ID_SEMENTE_POP[f"V{k}"], protocolo=protocolo, bky=False,
                                        suplementares=sup)
                if not protocolo:
                    lin[0]["especificacao"] = "indice_anderson"
                    lin[0]["no_protocolo"] = True
                    lin[0]["rotulo"] = rot
                linhas.extend(lin)
    for l in linhas:
        if l["especificacao"] == "principal" and l["outcome_id"] == "P1":
            l["unidade"] = UNIDADES["indice"]
    return linhas, extras


def aplicar_bky(est: pd.DataFrame) -> pd.DataFrame:
    est = est.copy()
    est["q_bky"] = np.nan
    for fam in FAMILIAS_BKY:
        m = (est["familia"] == fam) & est["entra_bky"].astype(bool)
        if m.any():
            est.loc[m, "q_bky"] = L.qvalores_bky(est.loc[m, "p_valor"].to_numpy(dtype=float))
    return est


# ---------------------------------------------------------------------------
# Leitura (chaves primeiro; outcomes depois dos diagnósticos)
# ---------------------------------------------------------------------------

def ler_running_variable() -> pd.DataFrame:
    a08 = pd.read_csv(A08, dtype={"co_ibge": str})
    a08["co_ibge"] = E3.normalizar_ibge(a08["co_ibge"]).str.zfill(6)
    if a08["co_ibge"].duplicated().any():
        raise FalhaValidacao("a08 com municipio duplicado")
    a08["s_mil"] = s_mil_de_ivs(a08["ivs"])
    if a08["s_mil"].isna().any():
        raise FalhaValidacao("a08 com IVS ausente")
    return a08[["co_ibge", "s_mil"]]


def chaves_populacoes(rv: pd.DataFrame) -> tuple[dict[str, pd.DataFrame], dict]:
    """Populações só com colunas de chave; confere IVS contra a08 e o primeiro estágio."""
    conf: dict = {}
    pops: dict[str, pd.DataFrame] = {}
    mapa = rv.set_index("co_ibge")["s_mil"]
    u = pd.read_parquet(ARQ_U, columns=["co_ibge", "ivs_2010_oficial"])
    g3 = pd.read_parquet(ARQ_G3, columns=["co_ibge", "ivs_2010_oficial"])
    vm = pd.read_parquet(ARQ_VM, columns=["ciclo", "co_ibge", "faixa_anunciada", "ivs_2010_oficial"])
    fora = {}
    for nome, df in (("U", u), ("G3", g3)):
        s_b = s_mil_de_ivs(df["ivs_2010_oficial"])
        sem = df.loc[s_b.isna(), "co_ibge"].tolist()
        s_a = df["co_ibge"].map(mapa)
        dif = int(((s_a - s_b).abs() > 0)[s_b.notna()].sum()) + int(s_a[s_b.notna()].isna().sum())
        if dif:
            raise FalhaValidacao(f"{nome}: IVS da tarefa B difere do a08 em {dif} municipios")
        conf[f"{nome}_ivs_igual_a08"] = True
        fora[nome] = sem
        pops[nome] = df.loc[s_b.notna(), ["co_ibge"]].assign(s_mil=s_b[s_b.notna()].to_numpy()).reset_index(drop=True)
    pe = {}
    for k, df in vm.groupby("ciclo"):
        nome = f"V{k}"
        s_b = s_mil_de_ivs(df["ivs_2010_oficial"])
        s_a = df["co_ibge"].map(mapa)
        if int(((s_a - s_b).abs() > 0)[s_b.notna()].sum()) or s_a[s_b.notna()].isna().any():
            raise FalhaValidacao(f"{nome}: IVS da tarefa B difere do a08")
        fora[nome] = df.loc[s_b.isna(), "co_ibge"].tolist()
        p = df.loc[s_b.notna(), ["co_ibge", "faixa_anunciada"]].assign(s_mil=s_b[s_b.notna()].to_numpy().astype(int))
        esc = p[["co_ibge", "s_mil"]].copy()
        pe[nome] = E3.primeiro_estagio(p[["co_ibge", "faixa_anunciada"]], esc)
        if not pe[nome]["sharp"]:
            raise FalhaValidacao(f"{nome}: primeiro estagio nao sharp ({pe[nome]})")
        conf[f"{nome}_ivs_igual_a08"] = True
        pops[nome] = p[["co_ibge", "s_mil"]].astype({"s_mil": float}).reset_index(drop=True)
    conf["primeiro_estagio"] = pe
    conf["municipios_sem_ivs_oficial_fora_da_rdd"] = fora
    return pops, conf


def carregar_covariaveis_balanco() -> tuple[pd.DataFrame, dict]:
    """Covariáveis oficiais pré (§8): a08 (subíndices, IDHM, população e renda 2010), Censo 2022, estrato A2, região."""
    a08 = pd.read_csv(A08, dtype={"co_ibge": str})
    a08["co_ibge"] = E3.normalizar_ibge(a08["co_ibge"]).str.zfill(6)
    pop10 = pd.to_numeric(a08["populacao"], errors="raise")
    cov = pd.DataFrame({
        "co_ibge": a08["co_ibge"],
        "ivs_infra_2010": pd.to_numeric(a08["ivs_infraestrutura_urbana"], errors="raise"),
        "ivs_ch_2010": pd.to_numeric(a08["ivs_capital_humano"], errors="raise"),
        "ivs_rt_2010": pd.to_numeric(a08["ivs_renda_e_trabalho"], errors="raise"),
        "idhm_2010": pd.to_numeric(a08["idhm"], errors="raise"),
        "log_populacao_2010": np.where(pop10 > 0, np.log(pop10.where(pop10 > 0)), np.nan),
        "rdpc_2010": pd.to_numeric(a08["renda_per_capita"], errors="raise"),
    })
    p22 = pd.read_csv(POP22, dtype={"co_ibge_6d": str})
    p22["co_ibge"] = p22["co_ibge_6d"].str.zfill(6)
    cov = cov.merge(p22[["co_ibge", "populacao_2022"]], on="co_ibge", how="left", validate="one_to_one")
    cov["log_populacao_2022"] = np.log(cov.pop("populacao_2022").astype(float))
    tip = pd.read_parquet(TIPOLOGIA, columns=["co_ibge_6d", "estrato"])
    tip["co_ibge"] = tip["co_ibge_6d"].astype(str).str.replace(r"\D", "", regex=True).str.zfill(6)
    cov = cov.merge(tip[["co_ibge", "estrato"]], on="co_ibge", how="left", validate="one_to_one")
    for e in E5.ESTRATOS_DUMMIES:
        cov[e] = np.where(cov["estrato"].isna(), np.nan, (cov["estrato"].astype(str) == e.removeprefix("estrato_")).astype(float))
    reg = cov["co_ibge"].str[0].map(E5.REGIOES)
    for r_ in E5.REGIOES_DUMMIES:
        cov[r_] = (reg == r_.removeprefix("regiao_")).astype(float)
    cov = cov.drop(columns=["estrato"])
    notas = {"colunas": [c for c in cov.columns if c != "co_ibge"],
             "fora": "IVS 2010 (running variable) e colunas da tipologia que vem do arquivo local errado (auditoria 16)"}
    return cov, notas


def diagnosticos(pops: dict[str, pd.DataFrame], cov: pd.DataFrame) -> pd.DataFrame:
    partes = []
    for nome in ("U", "G3", "V1", "V2", "V3"):
        p = pops[nome][["co_ibge"]].assign(s_mil=pops[nome]["s_mil"].astype(int))
        d = E3.diagnosticos_sem_outcome(p, cov, nome)
        partes.append(d)
    diag = pd.concat(partes, ignore_index=True)
    diag["corte"] = diag["corte"].map(lambda c: f"{c:.3f}")
    diag.insert(0, "natureza_dos_dados", "EMPIRICO")
    return diag


def selecao_janelas_lr(pops: dict[str, pd.DataFrame], n_perm: int = L.N_PERMUTACOES) -> tuple[pd.DataFrame, dict, dict, dict]:
    """Regra do E5 (só covariáveis). V1/V2: lê E5 e confere a recomputação. Devolve (tabela, lr, motivos, conf)."""
    cov_lr, _ = E5.carregar_covariaveis_e5(ROOT)
    e5 = pd.read_csv(E5_SEL)
    tabelas, lr, motivos, conf = [], {}, {}, {}
    for nome in ("U", "G3", "V1", "V2", "V3"):
        pc = pops[nome][["co_ibge"]].assign(s_mil=pops[nome]["s_mil"].astype(int)).merge(
            cov_lr, on="co_ibge", how="left", validate="one_to_one")
        if pc[[c for c, _ in E5.COV_LR]].isna().any().any():
            raise FalhaValidacao(f"{nome}: covariavel da selecao LR ausente")
        sel = E5.selecionar_janela(pc, f"P{ID_SEMENTE_POP[nome]}", n_perm)
        sel["populacao"] = nome
        sel["origem"] = "regra do E5 aplicada pelo E6 (so covariaveis, antes dos outcomes)"
        if nome in ("V1", "V2"):
            ref = e5[e5["populacao"] == f"P{ID_SEMENTE_POP[nome]}"].reset_index(drop=True)
            a = sel[["corte", "w", "n_abaixo", "n_acima", "p_min", "selecionada"]].reset_index(drop=True)
            b = ref[["corte", "w", "n_abaixo", "n_acima", "p_min", "selecionada"]]
            iguais = (len(a) == len(b) and np.allclose(a[["corte", "w", "n_abaixo", "n_acima"]], b[["corte", "w", "n_abaixo", "n_acima"]])
                      and np.allclose(a["p_min"].fillna(-1), b["p_min"].fillna(-1), atol=1e-12)
                      and (a["selecionada"].astype(bool) == b["selecionada"].astype(bool)).all())
            if not iguais:
                raise FalhaValidacao(f"{nome}: recomputacao da selecao LR nao reproduz E5_lr_selecao_janela.csv")
            conf[f"{nome}_selecao_lr_reproduz_E5"] = True
            sel["origem"] = f"E5_lr_selecao_janela.csv (P{ID_SEMENTE_POP[nome]}); recomputacao identica"
        for corte in CORTES:
            esc = sel[(sel["corte"] == corte / 1000) & sel["selecionada"]]
            if len(esc):
                lr[(nome, corte)] = int(round(float(esc.iloc[0]["w"]) * 1000))
            else:
                lr[(nome, corte)] = None
                motivos[(nome, corte)] = "nenhuma janela candidata passou no balanco (regra do E5)"
        tabelas.append(sel)
    tab = pd.concat(tabelas, ignore_index=True)
    tab["corte"] = tab["corte"].map(lambda c: f"{c:.3f}")
    tab.insert(0, "natureza_dos_dados", "EMPIRICO")
    return tab, lr, motivos, conf


def ler_pmmb_coparticipacao() -> tuple[pd.DataFrame, dict]:
    with zipfile.ZipFile(PPF_ZIP) as z:
        nomes = z.namelist()
        bruto = z.read(nomes[0])
    df = pd.read_csv(io.BytesIO(bruto), sep=";", dtype=str, encoding="latin1")
    df = df[df["nivel"] == "MUNICIPAL"].copy()
    df["co_ibge"] = E3.normalizar_ibge(df["co_ibge"]).str.zfill(6)
    if df["co_ibge"].duplicated().any():
        raise FalhaValidacao("PMMB: municipio duplicado no nivel MUNICIPAL")
    for c in ("ativas_ff", "ativas_coparticipacao", "total_vagas_ativas"):
        df[c] = pd.to_numeric(df[c], errors="raise")
    ident = float((df["total_vagas_ativas"] == df["ativas_ff"] + df["ativas_coparticipacao"]).mean())
    info = {"identidade_total_igual_ff_mais_coparticipacao": ident,
            "dt_referencia": sorted(df["dt_referencia"].dropna().unique().tolist())}
    return df, info


def carregar_s3() -> dict:
    """Porte da Portaria 3.493/2024 (a10) e portes em que o estrato IED muda em cada corte, lidos do a10."""
    if not A10_IED.exists():
        return {"tabela": None, "motivo": f"{rotulo(A10_IED)} ausente"}
    a10 = pd.read_csv(A10_IED, dtype={"co_ibge": str})
    falta = {"co_ibge", "porte_codigo", "estrato_ied", "ivs_codigo_portaria"} - set(a10.columns)
    if falta:
        return {"tabela": None, "motivo": f"a10 sem colunas {sorted(falta)}"}
    a10["co_ibge"] = a10["co_ibge"].str.zfill(6)
    mapa = a10.groupby(["ivs_codigo_portaria", "porte_codigo"])["estrato_ied"].agg(lambda v: sorted(set(v)))
    if (mapa.map(len) != 1).any():
        raise FalhaValidacao("a10: estrato IED nao e funcao de (codigo IVS, porte)")
    mapa = mapa.map(lambda v: v[0])
    portes_muda = {}
    for corte, (cod_ab, cod_ac) in ESTRATO_IED_CODIGO.items():
        portes_muda[corte] = {int(p) for p in sorted(a10["porte_codigo"].unique())
                              if mapa.get((cod_ab, p)) != mapa.get((cod_ac, p))}
        if portes_muda[corte] != PORTES_MUDA_PROTOCOLO[corte]:
            raise FalhaValidacao(f"a10: portes onde o estrato muda em {corte} = {portes_muda[corte]}, protocolo §13 diz "
                                 f"{PORTES_MUDA_PROTOCOLO[corte]}")
    return {"tabela": a10.set_index("co_ibge")["porte_codigo"].astype(int), "portes_muda": portes_muda,
            "definicao": "classe de porte do Anexo VI da Portaria 3.493/2024 (a10); muda = estrato IED diferente "
                         "dos dois lados do corte para aquele porte",
            "mapa_estrato": {f"{c}|{p}": int(e) for (c, p), e in mapa.items()}}


def carregar_s4(pmmb: pd.DataFrame) -> dict:
    """Atributo municipal Amazônia Legal / faixa de fronteira do PMMB consolidado (MS, retrato de 09/10/2026)."""
    falta = {"amazonia_legal", "faixa_fronteira"} - set(pmmb.columns)
    if falta:
        return {"tabela": None, "motivo": f"PMMB consolidado sem colunas {sorted(falta)}"}
    am = pmmb["amazonia_legal"].map({"Amazonia Legal": 1.0, "Fora da Amazonia Legal": 0.0})
    ff = pmmb["faixa_fronteira"].map({"Faixa de Fronteira": 1.0, "Fora da Faixa de Fronteira": 0.0})
    nao_mapeados = int((pmmb["amazonia_legal"].notna() & am.isna()).sum() + (pmmb["faixa_fronteira"].notna() & ff.isna()).sum())
    if nao_mapeados:
        raise FalhaValidacao(f"PMMB: {nao_mapeados} valores de amazonia_legal/faixa_fronteira fora do dicionario")
    flag = np.where(am.isna() | ff.isna(), np.nan, np.maximum(am.fillna(0), ff.fillna(0)))
    tab = pd.Series(flag, index=pmmb["co_ibge"].to_numpy()).dropna()
    return {"tabela": tab, "tabela_amazonia": pd.Series(am.to_numpy(), index=pmmb["co_ibge"].to_numpy()).dropna(),
            "definicao": "dentro = Amazonia Legal OU faixa de fronteira (atributo municipal do PMMB consolidado, MS); "
                         "a ajuda de custo da PI 604/2023 e Faixa 1 ali em qualquer IVS",
            "linhas_sem_atributo": int(np.isnan(flag).sum())}


def carregar_outcomes(pops: dict[str, pd.DataFrame], pmmb: pd.DataFrame) -> tuple[dict, dict]:
    """Lê os outcomes completos; tira os municípios sem IVS oficial (registrados)."""
    info: dict = {}
    u = pd.read_parquet(ARQ_U)
    pm = pmmb.set_index("co_ibge")
    u["pmmb_ativas_coparticipacao"] = u["co_ibge"].map(pm["ativas_coparticipacao"]).astype(float)
    if u["pmmb_ativas_coparticipacao"].isna().any():
        raise FalhaValidacao("municipio de U sem linha no PMMB consolidado")
    u["s1_pmmb_coparticipacao_por_10k"] = u["pmmb_ativas_coparticipacao"] / u["populacao_2022"] * 1e4
    u = u.merge(pops["U"], on="co_ibge", how="inner", validate="one_to_one")
    g3 = pd.read_parquet(ARQ_G3).merge(pops["G3"], on="co_ibge", how="inner", validate="one_to_one")
    vm = pd.read_parquet(ARQ_VM)
    vc = pd.read_parquet(ARQ_VC)
    V, C = {}, {}
    for k in sorted(vm["ciclo"].unique()):
        nome = f"V{k}"
        V[int(k)] = vm[vm["ciclo"] == k].merge(pops[nome], on="co_ibge", how="inner", validate="one_to_one").reset_index(drop=True)
        ck = vc[vc["ciclo"] == k].merge(pops[nome], on="co_ibge", how="inner", validate="many_to_one")
        info[f"celulas_{nome}"] = {"celulas": int(len(ck)),
                                   "celulas_fora_sem_ivs": int((vc["ciclo"] == k).sum() - len(ck))}
        C[int(k)] = ck.reset_index(drop=True)
    return {"U": u, "G3": g3, "V": V, "C": C}, info


def diagnostico_m(dados: dict, indice: pd.DataFrame) -> list[dict]:
    """M da regra de bolso por lado (quártica no suporte até o ponto médio entre cortes), por outcome V e corte.

    Só descreve o insumo do IC honesto já estimado; não muda nenhuma estimativa.
    """
    linhas = []

    def um(oid, pop, ciclo, s, y, corte):
        r = L.m_regra_de_bolso(s, y, corte, cortes_vizinhos=CORTES)
        sup = [None if not np.isfinite(v) else int(v) for v in r["suporte_mil"]]
        ok = np.isfinite(y)
        lo = -np.inf if sup[0] is None else sup[0]
        hi = np.inf if sup[1] is None else sup[1]
        dentro = ok & (s >= lo) & (s <= hi)
        linhas.append({"outcome_id": oid, "populacao": pop, "ciclo": ciclo, "corte": ROTULO_CORTE[corte],
                       "suporte_mil": sup, "M": r["M"], "M_abaixo": r["M_abaixo"], "M_acima": r["M_acima"],
                       "mass_points_abaixo": int(np.unique(s[dentro & (s <= corte)]).size),
                       "mass_points_acima": int(np.unique(s[dentro & (s > corte)]).size)})

    for spec in CATALOGO:
        if spec["pop"] != "V":
            continue
        for k in spec["ciclos"]:
            if k not in dados["V"]:
                continue
            d = dados["V"][k]
            for corte in CORTES:
                um(spec["id"], f"V{k}", str(k), d["s_mil"].to_numpy(float), d[spec["col"]].to_numpy(float), corte)
    for (k, corte), g in indice.groupby(["ciclo", "corte_mil"]):
        um("P1", f"V{k}", str(k), g["s_mil"].to_numpy(float), g["indice"].to_numpy(float), int(corte))
    return linhas


# ---------------------------------------------------------------------------
# Conferências contra E3 e E5 (falha fechada)
# ---------------------------------------------------------------------------

def _uma(est: pd.DataFrame, **f) -> pd.Series:
    m = np.ones(len(est), dtype=bool)
    for k, v in f.items():
        if k == "h":
            m &= np.isclose(est["h"].astype(float), v)
        else:
            m &= est[k].astype(str) == str(v)
    sub = est[m]
    if len(sub) != 1:
        raise FalhaValidacao(f"esperada 1 linha para {f}, achadas {len(sub)}")
    return sub.iloc[0]


def conferir_e3(est: pd.DataFrame, e3: pd.DataFrame, tol: float = 1e-12) -> dict:
    mapa = {("P1", E3.OUTCOME_PREENCHIMENTO): ("F1.3", "V1", "1"),
            ("P1", E3.OUTCOME_D): ("F2.3", "V1", "1"), ("P2", E3.OUTCOME_D): ("F2.3", "V2", "2")}
    maior, n = 0.0, 0
    for r in e3.to_dict("records"):
        oid, pop, ciclo = mapa[(r["populacao"], r["outcome"])]
        esp = "principal" if r["especificacao"] == "principal" else "sensibilidade_h"
        x = _uma(est, outcome_id=oid, populacao=pop, ciclo=ciclo, corte=f"{r['corte']:.3f}", especificacao=esp,
                 h=r["h"])
        for c in ("tau", "ep", "ic95_inf", "ic95_sup", "p_valor"):
            maior = max(maior, abs(float(x[c]) - float(r[c])))
        if int(x["n_abaixo"]) != int(r["n_abaixo"]) or int(x["n_acima"]) != int(r["n_acima"]):
            raise FalhaValidacao(f"E3 nao reproduzido (n) em {r['populacao']} {r['outcome']} {r['corte']} {r['h']}")
        n += 1
    if maior > tol:
        raise FalhaValidacao(f"E3 nao reproduzido: max |dif| = {maior}")
    return {"linhas_E3_conferidas": n, "max_abs_dif": maior, "tolerancia": tol, "reproduz": True}


def conferir_e5(est: pd.DataFrame, e5: pd.DataFrame, tol: float = 1e-10, *, v1: pd.DataFrame | None = None,
                e4: pd.DataFrame | None = None) -> dict:
    """Linhas do E5 reproduzidas pelo E6.

    O Y1 que o E5 leu de `E4_proporcao_municipio.csv` está gravado com menos
    dígitos que o F1.3 da tarefa B (diferença de ordem 1e-11 por município). Para a
    linha E0 (ponderada por células), que amplifica essa diferença, a conferência
    é feita em duas partes: (i) a mesma estimação da rdd_lib com o Y1 do E4
    reproduz o E5 dentro de `tol`; (ii) a diferença entre o F1.3 e o Y1 do E4 é
    registrada. As demais linhas são comparadas diretamente com `tol`.
    """
    extra = {}
    if v1 is not None and e4 is not None:
        m = v1[["co_ibge", "s_mil", "f1_3_fracao_celulas_preenchidas_ch1", "n_celulas"]].merge(
            e4[["co_ibge", "y1", "n_celulas"]], on="co_ibge", how="left", suffixes=("", "_e4"), validate="one_to_one")
        if m["y1"].isna().any() or (m["n_celulas"] != m["n_celulas_e4"]).any():
            raise FalhaValidacao("V1 e E4 nao casam (municipios ou numero de celulas)")
        extra["max_abs_dif_entrada_F13_vs_y1_E4"] = float((m["f1_3_fracao_celulas_preenchidas_ch1"] - m["y1"]).abs().max())
        extra["_e0_com_y1_e4"] = {c: L.rd_local_linear(m["s_mil"].to_numpy(float), m["y1"].to_numpy(float), c, H,
                                                       peso=m["n_celulas"].to_numpy(float)) for c in CORTES}
    return _conferir_e5(est, e5, tol, extra)


def _conferir_e5(est: pd.DataFrame, e5: pd.DataFrame, tol: float, extra: dict) -> dict:
    alvo = {
        ("D", "Y1"): dict(outcome_id="F1.3", populacao="V1", ciclo="1", especificacao="local_randomization"),
        ("D", "D1"): dict(outcome_id="F2.3", populacao="V1", ciclo="1", especificacao="local_randomization"),
        ("D", "D2"): dict(outcome_id="F2.3", populacao="V2", ciclo="2", especificacao="local_randomization"),
        ("E0", "Y1"): dict(outcome_id="F1.3", populacao="V1", ciclo="1", especificacao="ponderado_celulas"),
        ("E1", "Y1"): dict(outcome_id="F1.3", populacao="V1", ciclo="1", especificacao="nivel_celula"),
        ("F1", "D1+D2"): dict(outcome_id="F2.3", populacao="V1+V2", ciclo="1+2", especificacao="principal"),
        ("F2", "D1+D2"): dict(outcome_id="F2.3", populacao="V1+V2", ciclo="1+2", especificacao="principal"),
    }
    maior, n, sem_janela = 0.0, 0, 0
    for r in e5.to_dict("records"):
        f = alvo.get((r["especificacao"], r["outcome"]))
        if f is None:
            continue
        corte = EMPILHADO if r["especificacao"] == "F2" else f"{float(r['corte']):.3f}"
        filtro = dict(f, corte=corte)
        if f["especificacao"] in ("principal", "ponderado_celulas", "nivel_celula"):
            filtro["h"] = 0.05
        x = _uma(est, **filtro)
        if not np.isfinite(r["tau"]):
            if x["status"] != "NAO_EXECUTADO":
                raise FalhaValidacao(f"E5 sem janela em {r} mas E6 estimou")
            sem_janela += 1
            continue
        cols = ("tau", "ep", "ic95_inf", "ic95_sup", "p_valor")
        if r["especificacao"] == "E0" and "_e0_com_y1_e4" in extra:
            ref = extra["_e0_com_y1_e4"][int(round(float(r["corte"]) * 1000))]
            dif_e0 = max(abs(float(ref[c]) - float(r[c])) for c in cols)
            maior = max(maior, dif_e0)
            dif_e6 = max(abs(float(x[c]) - float(r[c])) for c in cols)
            extra["max_abs_dif_E0_linha_E6_vs_E5_por_arredondamento_do_y1"] = max(
                extra.get("max_abs_dif_E0_linha_E6_vs_E5_por_arredondamento_do_y1", 0.0), dif_e6)
            n += 1
            continue
        for c in cols:
            maior = max(maior, abs(float(x[c]) - float(r[c])))
        n += 1
    if maior > tol:
        raise FalhaValidacao(f"E5 nao reproduzido: max |dif| = {maior}")
    return {"linhas_E5_conferidas": n, "linhas_E5_sem_janela_confirmadas": sem_janela, "max_abs_dif": maior,
            "tolerancia": tol, "reproduz": True,
            **{k: v for k, v in extra.items() if not k.startswith("_")},
            "nota": "E0 (ponderado) conferido com o Y1 do E4 como entrada; a linha do E6 usa o F1.3 da tarefa B, "
                    "que difere do Y1 gravado no CSV do E4 so por arredondamento"}


# ---------------------------------------------------------------------------
# Figuras
# ---------------------------------------------------------------------------

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
              rodape: str, xlabel: str = "IVS 2010 oficial", rotulo_salto: str = "salto") -> None:
    import textwrap
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, len(painel), figsize=(5.2 * len(painel), 4.0), squeeze=False)
    for ax, (sub, s, y, corte) in zip(axs[0], painel):
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
            txt = (f"{rotulo_salto} = {r['tau']:.3g} [{r['ic95_inf']:.3g}; {r['ic95_sup']:.3g}]"
                   .replace(".", ",").replace("-", "−"))
        else:
            txt = f"sem estimativa: {r.get('nota', '')[:60]}"
        ax.axvline(corte / 1000, color="#9ca3af", linewidth=1, linestyle="--")
        ax.set_title(f"{sub}\n{txt}", fontsize=9)
        ax.set_xlabel(xlabel)
        ax.grid(alpha=0.25, linewidth=0.6)
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)
    axs[0][0].set_ylabel(ylabel)
    fig.suptitle(titulo, fontsize=11)
    largura = 95 if len(painel) > 1 else 70
    linhas_rod = textwrap.wrap(rodape, largura)
    fig.text(0.01, 0.005, "\n".join(linhas_rod), fontsize=7, color="#4b5563", va="bottom")
    fig.tight_layout(rect=(0, 0.035 * len(linhas_rod), 1, 0.95))
    fig.savefig(caminho, dpi=130)
    plt.close(fig)


def gerar_figuras(dados: dict, indice: pd.DataFrame, dir_fig: Path) -> list[str]:
    dir_fig.mkdir(parents=True, exist_ok=True)
    for antigo in dir_fig.glob("*.png"):
        antigo.unlink()
    rod = ("EMPIRICO. Médias em faixas de 0,005 (área ~ n); reta local linear triangular h = 0,050 e IC 95% "
           "pontual HC1. Salto = lado de bolsa maior - lado de bolsa menor.")
    feitos = []
    V = dados["V"]
    figs = [(c["id"], c["col"], c["desc"], c["ciclos"]) for c in CATALOGO
            if c["id"] in COMPONENTES_INDICE + ["F2.3"] and c["pop"] == "V"]
    for oid, col, desc, ciclos in figs:
        for k in ciclos:
            if k not in V:
                continue
            d = V[k]
            painel = [(f"corte {ROTULO_CORTE[c].replace('.', ',')}", d["s_mil"].to_numpy(float),
                       d[col].to_numpy(float), c) for c in CORTES]
            nome = f"E6_{oid.replace('.', '_')}_V{k}.png"
            figura_rd(painel, f"{oid} — {desc} (V{k}, ciclo {k})", oid, dir_fig / nome, rod)
            feitos.append(nome)
    u = dados["U"]
    for k in (1, 2, 3):
        col = f"f0_1_tem_celula_c{k}"
        painel = [(f"corte {ROTULO_CORTE[c].replace('.', ',')}", u["s_mil"].to_numpy(float), u[col].to_numpy(float), c)
                  for c in CORTES]
        nome = f"E6_F0_1_U_c{k}.png"
        figura_rd(painel, f"F0.1 — município tem célula no quadro do ciclo {k} (U, diagnóstico de seleção)", "F0.1",
                  dir_fig / nome, rod)
        feitos.append(nome)
    for k in sorted(indice["ciclo"].unique()):
        dk = indice[indice["ciclo"] == k]
        painel = [(f"corte {ROTULO_CORTE[c].replace('.', ',')}", dk.loc[dk["corte_mil"] == c, "s_mil"].to_numpy(float),
                   dk.loc[dk["corte_mil"] == c, "indice"].to_numpy(float), c) for c in CORTES]
        nome = f"E6_indice_P1_V{k}.png"
        figura_rd(painel, f"Índice de atração-presença (KLK), V{k}", "índice (DP)", dir_fig / nome, rod)
        feitos.append(nome)
    # Índice agrupado em r = s - c (visual; a estimativa P1 tem interceptos por ciclo x corte).
    r = (indice["s_mil"] - indice["corte_mil"]).to_numpy(float)
    figura_rd([("todos os ciclos e cortes, r = s - c", r, indice["indice"].to_numpy(float), 0)],
              "Índice P1 com ciclos e cortes agrupados (visual)", "índice (DP)", dir_fig / "E6_indice_P1_agrupado.png",
              rod + " Visual: reta comum em r; a estimativa P1 (E6_estimativas.csv) usa interceptos e inclinações "
                    "por ciclo x corte e CR1.", xlabel="r = IVS 2010 oficial − corte", rotulo_salto="salto da reta comum")
    feitos.append("E6_indice_P1_agrupado.png")
    return feitos


# ---------------------------------------------------------------------------
# Tabelas do doc 41 (geradas das saídas; nenhum número digitado)
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


def _escala(unidade: str) -> tuple[int, bool, str]:
    if unidade.startswith("fracao"):
        return 1, True, "p.p."
    if unidade.startswith("desvios"):
        return 2, False, "DP"
    if unidade.startswith("log"):
        return 3, False, "log"
    return 3, False, ""


def _tab_linhas(est: pd.DataFrame, filtro, cab: list[str], cols) -> str:
    sub = est[filtro]
    out = ["| " + " | ".join(cab) + " |", "|" + "|".join("---" for _ in cab) + "|"]
    for r in sub.to_dict("records"):
        out.append("| " + " | ".join(f(r) for f in cols) + " |")
    return "\n".join(out)


def gerar_tabelas_doc(est: pd.DataFrame, diag: pd.DataFrame, resumo: dict) -> dict[str, str]:
    t: dict[str, str] = {}

    def tau(r):
        c, pp, u = _escala(r["unidade"])
        return f"{_n(r['tau'], 1 if pp else c, pp)} {u}".strip()

    def ic(r):
        c, pp, _ = _escala(r["unidade"])
        return _ic(r["ic95_inf"], r["ic95_sup"], 1 if pp else c, pp)

    def ich(r):
        c, pp, _ = _escala(r["unidade"])
        return _ic(r["ic_honesto_inf"], r["ic_honesto_sup"], 1 if pp else c, pp)

    nab = lambda r: f"{_fmt_int(r['n_abaixo'])} / {_fmt_int(r['n_acima'])}"
    corte = lambda r: r["corte"].replace(".", ",")
    princ = est["especificacao"] == "principal"
    # 1. Seleção F0 em U.
    f = princ & est["outcome_id"].isin(["F0.1", "F0.2"]) & (est["populacao"] == "U") & est["no_protocolo"]
    t["selecao_F0"] = _tab_linhas(est, f, ["Outcome", "Ciclo", "Corte", "n abaixo / acima", "Salto", "IC 95%", "p", "q BKY"],
                                  [lambda r: f"{r['outcome_id']} `{r['outcome']}`", lambda r: r["ciclo"], corte, nab,
                                   tau, ic, lambda r: _p(r["p_valor"]), lambda r: _p(r["q_bky"])])
    # 2. P1.
    f = est["outcome_id"].isin(["P1"]) & princ
    t["indice_P1"] = _tab_linhas(est, f, ["População", "Corte", "n abaixo / acima", "Salto", "IC 95% (CR1/HC1)",
                                          "IC honesto", "p"],
                                 [lambda r: r["populacao"], corte, nab, tau, ic, ich, lambda r: _p(r["p_valor"])])
    f = est["outcome_id"].eq("P1") & est["especificacao"].isin(["sensibilidade_h", "ic_honesto", "local_randomization",
                                                                "S2_donut"]) & (est["populacao"] == "V1+V2+V3") \
        & est["corte"].eq(EMPILHADO)
    f2 = est["outcome_id"].eq("P1.anderson") & est["especificacao"].eq("indice_anderson") & \
        est["populacao"].eq("V1+V2+V3") & est["corte"].eq(EMPILHADO)
    t["indice_P1_sensibilidade"] = _tab_linhas(
        est, f | f2, ["Especificação", "h", "M", "Salto", "IC 95%", "p"],
        [lambda r: r["especificacao"] + (" (Anderson)" if r["outcome_id"] == "P1.anderson" else ""),
         lambda r: _n(r["h"], 3, sinal=False), lambda r: _n(r["fator_M"], 1, sinal=False) + " × M" if pd.notna(r["fator_M"]) else "—",
         tau, ic, lambda r: _p(r["p_valor"])])
    # 3. Componentes F1/F2 (principal), por ciclo e empilhados.
    for fam in ("F1", "F2", "F4"):
        f = princ & (est["familia"] == fam) & est["no_protocolo"]
        t[f"componentes_{fam}"] = _tab_linhas(
            est, f, ["Outcome", "População", "Ciclo", "Corte", "n abaixo / acima", "Salto", "IC 95%", "IC honesto", "p",
                     "q BKY"],
            [lambda r: f"{r['outcome_id']}", lambda r: r["populacao"], lambda r: r["ciclo"], corte, nab, tau, ic, ich,
             lambda r: _p(r["p_valor"]), lambda r: _p(r["q_bky"])])
    # 4. Poisson das contagens (efeito relativo).
    f = (est["especificacao"] == "poisson_local") & est["familia"].isin(["F1", "F2"])
    t["poisson"] = _tab_linhas(est, f, ["Outcome", "População", "Ciclo", "Corte", "Salto em log", "Efeito relativo",
                                        "IC 95% (relativo)", "p"],
                               [lambda r: r["outcome_id"], lambda r: r["populacao"], lambda r: r["ciclo"], corte,
                                lambda r: _n(r["tau"], 3), lambda r: _n(r["efeito_relativo"], 1, pp=True) + " %",
                                lambda r: _ic(r["efeito_relativo_ic95_inf"], r["efeito_relativo_ic95_sup"], 1, True),
                                lambda r: _p(r["p_valor"])])
    # 5. Lee.
    f = (est["especificacao"] == "limites_lee") & (est["status"] != "NAO_EXECUTADO")
    t["lee"] = _tab_linhas(est, f, ["População", "Corte", "Limite inferior", "Limite superior", "IC 95% conservador"],
                           [lambda r: r["populacao"], corte, lambda r: _n(r["lee_tau_inf"], 3),
                            lambda r: _n(r["lee_tau_sup"], 3), lambda r: _ic(r["ic95_inf"], r["ic95_sup"], 3)])
    # 6. F0.3, F0.4 e S1.
    f = princ & (est["outcome_id"].isin(["F0.3", "F0.4", "S1"])) & est["no_protocolo"]
    t["copolitica"] = _tab_linhas(est, f, ["Outcome", "População", "Corte", "n abaixo / acima", "Salto", "IC 95%", "p"],
                                  [lambda r: f"{r['outcome_id']} `{r['outcome']}`", lambda r: r["populacao"], corte, nab,
                                   tau, ic, lambda r: _p(r["p_valor"])])
    # 7. Suplementares S3/S4 do índice.
    f = est["outcome_id"].eq("P1") & est["especificacao"].str.startswith(("S3", "S4"))
    t["s3_s4_indice"] = _tab_linhas(est, f, ["População", "Especificação", "Corte", "n abaixo / acima", "Salto", "IC 95%",
                                             "p"],
                                    [lambda r: r["populacao"], lambda r: r["especificacao"], corte, nab, tau, ic,
                                     lambda r: _p(r["p_valor"])])
    dm = pd.DataFrame(resumo.get("diagnostico_M_regra_de_bolso", []))
    if len(dm):
        dm = dm[dm["outcome_id"].isin(COMPONENTES_INDICE + ["P1"])]
    t["diagnostico_M"] = _tab_linhas(
        dm, np.ones(len(dm), dtype=bool),
        ["Outcome", "População", "Corte", "Suporte (milésimos)", "mass points abaixo / acima", "M abaixo", "M acima"],
        [lambda r: r["outcome_id"], lambda r: r["populacao"], lambda r: r["corte"].replace(".", ","),
         lambda r: "[" + ("−∞" if r["suporte_mil"][0] is None else str(r["suporte_mil"][0])) + "; "
                   + ("+∞" if r["suporte_mil"][1] is None else str(r["suporte_mil"][1])) + "]", lambda r: f"{_fmt_int(r['mass_points_abaixo'])} / {_fmt_int(r['mass_points_acima'])}",
         lambda r: _n(r["M_abaixo"], 1, sinal=False), lambda r: _n(r["M_acima"], 1, sinal=False)]) if len(dm) else "—"
    # 8. Diagnósticos: densidade e balanço (h = 0,050).
    dd = diag[(diag["diagnostico"] == "densidade_poisson_mass_points") & (diag["especificacao"] == "principal")]
    t["densidade"] = _tab_linhas(dd, np.ones(len(dd), dtype=bool), ["População", "Corte", "n abaixo / acima", "Razão de densidades", "IC 95%", "p"],
                                 [lambda r: r["populacao"], lambda r: r["corte"].replace(".", ","), nab,
                                  lambda r: _n(r["rho"], 2, sinal=False), lambda r: f"[{_n(r['rho_ic95_inf'], 2, sinal=False)}; {_n(r['rho_ic95_sup'], 2, sinal=False)}]",
                                  lambda r: _p(r["p_valor"])])
    bal = diag[(diag["diagnostico"] == "balanco_covariavel_pre") & (diag["especificacao"] == "principal")]
    linhas = ["| População | Corte | Covariáveis testadas | p < 0,05 | Quais |", "|---|---|---|---|---|"]
    for (pop, c), g in bal.groupby(["populacao", "corte"], sort=False):
        ok = g[g["p_valor"].notna()]
        sig = ok[ok["p_valor"] < 0.05]
        quais = ", ".join(f"{v} ({_n(tv, 3)}; p = {_p(pv)})" for v, tv, pv in zip(sig["variavel"], sig["tau"], sig["p_valor"]))
        linhas.append(f"| {pop} | {c.replace('.', ',')} | {len(ok)} | {len(sig)} | {quais or '—'} |")
    t["balanco"] = "\n".join(linhas)
    # 8b. Resumo dos testes por família (linhas principais do protocolo que entram no BKY).
    linhas = ["| Família | Linhas principais no BKY | p < 0,05 | q BKY < 0,05 | menor p | menor q |",
              "|---|---|---|---|---|---|"]
    for fam in FAMILIAS_BKY:
        g = est[(est["familia"] == fam) & est["entra_bky"].astype(bool)]
        linhas.append(f"| {fam} | {len(g)} | {int((g['p_valor'] < 0.05).sum())} | {int((g['q_bky'] < 0.05).sum())} | "
                      f"{_p(g['p_valor'].min())} | {_p(g['q_bky'].min())} |")
    sup = est[est["especificacao"].str.startswith(("S2", "S3", "S4")) & (est["status"] == "EXECUTADO")]
    linhas.append(f"| S2–S4, todos os outcomes (fora do BKY) | {len(sup)} | {int((sup['p_valor'] < 0.05).sum())} | — | "
                  f"{_p(sup['p_valor'].min())} | — |")
    t["resumo_testes"] = "\n".join(linhas)
    sig = est[est["entra_bky"].astype(bool) & (est["p_valor"] < 0.05)]
    t["principais_p_menor_005"] = _tab_linhas(
        sig, np.ones(len(sig), dtype=bool),
        ["Família", "Outcome", "População", "Ciclo", "Corte", "Salto", "IC 95%", "IC honesto", "p", "q BKY"],
        [lambda r: r["familia"], lambda r: f"{r['outcome_id']} `{r['outcome']}`", lambda r: r["populacao"],
         lambda r: r["ciclo"], corte, tau, ic, ich, lambda r: _p(r["p_valor"]), lambda r: _p(r["q_bky"])])
    # 8c. Referências de magnitude do protocolo (§7): +10 p.p. de preenchimento e +25% de candidaturas.
    linhas = ["| Outcome | População | Ciclo | Corte | Referência | Limite superior do IC 95% | IC 95% exclui a referência? |",
              "|---|---|---|---|---|---|---|"]
    ref_pp = REFERENCIA_PREENCHIMENTO
    for r in est[princ & est["outcome_id"].isin(["F1.2", "F1.3", "F1.4"]) & est["no_protocolo"]].to_dict("records"):
        linhas.append(f"| {r['outcome_id']} | {r['populacao']} | {r['ciclo']} | {corte(r)} | {_n(ref_pp, 0, pp=True)} p.p. | "
                      f"{_n(r['ic95_sup'], 1, pp=True)} p.p. | {'sim' if r['ic95_sup'] < ref_pp else 'não'} |")
    for r in est[(est["especificacao"] == "poisson_local") & (est["outcome_id"] == "F1.1")].to_dict("records"):
        linhas.append(f"| F1.1 (Poisson) | {r['populacao']} | {r['ciclo']} | {corte(r)} | "
                      f"{_n(REFERENCIA_CANDIDATURAS, 0, pp=True)} % | {_n(r['efeito_relativo_ic95_sup'], 1, pp=True)} % | "
                      f"{'sim' if r['efeito_relativo_ic95_sup'] < REFERENCIA_CANDIDATURAS else 'não'} |")
    t["referencias_magnitude"] = "\n".join(linhas)
    jan = resumo.get("janelas_lr", {})
    linhas = ["| População | Corte | Janela (± IVS) |", "|---|---|---|"]
    for chave, w in jan.items():
        pop, c = chave.split("|")
        linhas.append(f"| {pop} | {c.replace('.', ',')} | {_n(w, 3, sinal=False) if w else 'nenhuma passou no balanço'} |")
    t["janelas_lr"] = "\n".join(linhas)
    # 9. Contagens e validações.
    v = resumo.get("validacoes", {})
    e3v, e5v = v.get("E3", {}), v.get("E5", {})
    q = resumo.get("contagens", {})
    t["validacoes"] = "\n".join([
        "| Conferência | Resultado |", "|---|---|",
        f"| linhas do E3 reproduzidas (F1.3 ciclo 1, F2.3 ciclos 1 e 2) | {e3v.get('linhas_E3_conferidas')}; max abs dif = {e3v.get('max_abs_dif')} |",
        f"| linhas do E5 reproduzidas (LR, ponderado, célula, ciclos empilhados) | {e5v.get('linhas_E5_conferidas')} (+ {e5v.get('linhas_E5_sem_janela_confirmadas')} sem janela); max abs dif = {e5v.get('max_abs_dif')} |",
        f"| linhas em E6_estimativas.csv | {q.get('linhas')} |",
        f"| linhas do protocolo (no_protocolo = True) | {q.get('linhas_no_protocolo')} |",
        f"| linhas NAO_EXECUTADO | {q.get('nao_executado')} |",
        f"| linhas SEM_ESTIMATIVA (biblioteca devolveu NaN com motivo) | {q.get('sem_estimativa')} |",
    ])
    p1 = resumo.get("p1_para_holm", {})
    t["p1_holm"] = f"p de P1 (para o Holm com P2 do E7): **{_p(p1.get('p_valor'))}**; salto {_n(p1.get('tau'), 2)} DP, IC 95% {_ic(p1.get('ic95_inf'), p1.get('ic95_sup'), 2)}."
    return t


def _fmt_int(v) -> str:
    return "—" if v is None or pd.isna(v) else str(int(v))


MARCA = re.compile(r"(<!-- E6:(?P<nome>[A-Za-z0-9_]+):inicio -->\n)(?P<corpo>.*?)(\n<!-- E6:(?P=nome):fim -->)", re.S)


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
    est = pd.read_csv(OUT / NOME_EST, dtype={"corte": str, "ciclo": str})
    diag = pd.read_csv(OUT / NOME_DIAG, dtype={"corte": str})
    resumo = json.loads((OUT / NOME_RESUMO).read_text(encoding="utf-8"))
    return est, diag, resumo


def atualizar_doc() -> None:
    """Regrava as tabelas entre marcadores do doc 41 a partir das saídas gravadas."""
    if not DOC41.exists():
        print(f"{rotulo(DOC41)} nao existe: tabelas nao gravadas")
        return
    est, diag, resumo = ler_saidas()
    DOC41.write_text(aplicar_tabelas_doc(DOC41.read_text(encoding="utf-8"), gerar_tabelas_doc(est, diag, resumo)),
                     encoding="utf-8")
    print(f"tabelas do doc 41 regravadas: {rotulo(DOC41)}")


# ---------------------------------------------------------------------------
# Execução
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--atualizar-doc", action="store_true", help="so regrava as tabelas do doc 41 a partir das saidas")
    ap.add_argument("--n-perm", type=int, default=L.N_PERMUTACOES)
    args = ap.parse_args(argv)

    if args.atualizar_doc:
        atualizar_doc()
        return 0

    protocolo = json.loads(PROTOCOLO_JSON.read_text(encoding="utf-8"))
    if [round(c * 1000) for c in protocolo["running_variable"]["cortes"]] != list(CORTES):
        raise SystemExit("cortes do script divergem do protocolo congelado")
    sha_md = sha256(PROTOCOLO_MD)
    desvios: list[dict] = []
    decisoes: list[str] = []

    # (1) Running variable e populações (só chaves).
    rv = ler_running_variable()
    pops, conf_pop = chaves_populacoes(rv)
    print("populacoes:", {k: len(v) for k, v in pops.items()})

    # (2) Diagnósticos sem outcome e seleção LR, gravados antes dos outcomes.
    cov, notas_cov = carregar_covariaveis_balanco()
    diag = diagnosticos(pops, cov)
    OUT.mkdir(parents=True, exist_ok=True)
    diag.to_csv(OUT / NOME_DIAG, index=False)
    sel, lr, motivos_lr, conf_lr = selecao_janelas_lr(pops, args.n_perm)
    sel.to_csv(OUT / NOME_LR, index=False)
    print("janelas LR:", {f"{k[0]}|{k[1]}": v for k, v in lr.items()})

    # (3) Outcomes.
    pmmb, info_pmmb = ler_pmmb_coparticipacao()
    dados, info_out = carregar_outcomes(pops, pmmb)
    s3 = carregar_s3()
    s4 = carregar_s4(pmmb)
    sup = {"S3": s3, "S4": s4}
    est, extras = estimar_tudo(dados, sup=sup, lr=lr, motivos_lr=motivos_lr)

    # (4) Conferências (falha fechada antes de gravar).
    e3 = pd.read_csv(E3_EST)
    e5 = pd.read_csv(E5_ESP)
    val_e3 = conferir_e3(est, e3)
    e4 = pd.read_csv(E4_MUN, dtype={"co_ibge": str})
    e4["co_ibge"] = E3.normalizar_ibge(e4["co_ibge"]).str.zfill(6)
    val_e5 = conferir_e5(est, e5, v1=dados["V"][1], e4=e4)
    nucleo = ["tau", "ep", "ic95_inf", "ic95_sup", "p_valor"]
    sem_nota = est[est[nucleo].isna().any(axis=1) & (est["nota"].fillna("") == "")]
    if len(sem_nota):
        raise FalhaValidacao(f"{len(sem_nota)} linhas com NaN sem nota")

    est.to_csv(OUT / NOME_EST, index=False)
    figs = gerar_figuras(dados, extras["indice"]["dados_klk"], OUT / DIR_FIG)

    # (5) Resumo.
    p1 = est[(est["outcome_id"] == "P1") & (est["especificacao"] == "principal") & (est["corte"] == EMPILHADO)
             & (est["populacao"] == "V1+V2+V3")].iloc[0]
    entradas = [
        bloco_entrada(PROTOCOLO_JSON, "protocolo congelado (somente lido)", "pipeline do repositorio", "2026-10-18",
                      "-", "documento", "-", "-"),
        bloco_entrada(PROTOCOLO_MD, "texto canonico do protocolo (somente lido)", "pipeline do repositorio",
                      "2026-10-18", "§§1-15", "documento", "-", "-"),
        bloco_entrada(A08, "running variable (IVS 2010 oficial) e covariaveis pre", "Ipea, Atlas da Vulnerabilidade Social (a08)",
                      "Censo 2010", f"{len(rv)} municipios", "municipio", "co_ibge",
                      "ivs; subindices, idhm, populacao e renda per capita para balanco"),
        bloco_entrada(POP22, "covariavel log populacao 2022 (balanco)", "IBGE, Censo 2022", "Censo 2022",
                      "5570 municipios", "municipio", "co_ibge_6d", "nenhum"),
        bloco_entrada(TIPOLOGIA, "estrato territorial (so a coluna estrato)", "tipologia A2 (REGIC 2018, RM/RIDE 2022)",
                      "REGIC 2018; RM/RIDE 2022", "5570 municipios", "municipio", "co_ibge_6d", "colunas co_ibge_6d e estrato"),
        bloco_entrada(ARQ_U, "outcomes F0.1, F0.2, F0.4, F2.2 (U)", "tarefa B (12_construir_outcomes_funil.py)",
                      "ver dicionario", f"{len(dados['U'])} municipios", "municipio", "co_ibge", "nenhum"),
        bloco_entrada(ARQ_G3, "outcomes F0.3 (G3)", "tarefa B", "ver dicionario", f"{len(dados['G3'])} municipios com IVS",
                      "municipio", "co_ibge", "municipios sem IVS oficial fora"),
        bloco_entrada(ARQ_VM, "outcomes F1, F2.1, F2.3, F4 (V1-V3)", "tarefa B", "ver dicionario",
                      ", ".join(f"V{k}: {len(v)}" for k, v in dados["V"].items()), "municipio x ciclo", "ciclo, co_ibge",
                      "municipios sem IVS oficial fora"),
        bloco_entrada(ARQ_VC, "proporcoes no nivel celula", "tarefa B", "ver dicionario",
                      ", ".join(f"V{k}: {len(v)}" for k, v in dados["C"].items()), "celula CNES x curso x ciclo",
                      "ciclo, co_cnes_7d, cod_curso", "celulas de municipios sem IVS oficial fora"),
        bloco_entrada(DICIONARIO, "dicionario dos outcomes (somente lido)", "tarefa B", "2026-10-18", "-", "documento",
                      "-", "-"),
        bloco_entrada(PPF_ZIP, "S1 (ativas_coparticipacao) e atributo Amazonia Legal/fronteira do S4",
                      "Ministerio da Saude, PMMB consolidado (dados abertos)",
                      ", ".join(info_pmmb["dt_referencia"]), "nivel MUNICIPAL", "municipio", "co_ibge",
                      "nivel == MUNICIPAL; colunas co_ibge, ativas_ff, ativas_coparticipacao, total_vagas_ativas, "
                      "amazonia_legal, faixa_fronteira"),
        bloco_entrada(E3_EST, "alvo de conferencia (E3)", "07_estimar_E3_rdd_completa.py", "2026-10-14", "18 linhas",
                      "linha de estimativa", "populacao, outcome, corte, h", "nenhum"),
        bloco_entrada(E4_MUN, "Y1 do E4 (entrada do E5), so para conferir a linha E0 do E5", "08_estimar_E4_proporcao.py",
                      "2026-10-14", "368 municipios", "municipio", "co_ibge", "colunas co_ibge, y1, n_celulas"),
        bloco_entrada(E5_SEL, "janela LR de V1 e V2 (regra do E5)", "11_inferencia_alternativa.py", "2026-10-18",
                      "P1, P2", "janela", "populacao, corte, w", "selecionada"),
        bloco_entrada(E5_ESP, "alvo de conferencia (E5)", "11_inferencia_alternativa.py", "2026-10-18",
                      "42 linhas", "linha de estimativa", "especificacao, outcome, corte", "D, E0, E1, F1, F2"),
    ]
    if A10_IED.exists():
        entradas.append(bloco_entrada(A10_IED, "S3: porte e estrato IED da Portaria 3.493/2024", "tarefa D (a10), Anexo VI",
                                      "Portaria GM/MS 3.493/2024", "5570 municipios", "municipio", "co_ibge",
                                      "colunas co_ibge, ivs_codigo_portaria, porte_codigo, estrato_ied"))
    if A10_DIAG.exists():
        entradas.append(bloco_entrada(A10_DIAG, "conferencia do mapa estrato x porte (somente lido)", "tarefa D (a10)",
                                      "2026-10-18", "-", "documento", "-", "-"))

    # Desvios e decisões (fixados no código antes de rodar).
    desvios += [
        {"data": DATA_EXECUCAO, "item": "local randomization em U, G3 e V3",
         "situacao": "o E5 so selecionou janela para P1 (= V1) e P2 (= V2)",
         "resolucao": "a mesma regra do E5 (so covariaveis, antes dos outcomes) foi aplicada a U, G3 e V3, com "
                      "semente (20261018, id da populacao, corte, w); ids: " + json.dumps(ID_SEMENTE_POP)
                      + f"; tabela em {NOME_LR}. V1 e V2 leem o E5 e a recomputacao o reproduz"},
        {"data": DATA_EXECUCAO, "item": "S4 (Amazonia Legal / faixa de fronteira em 0,400)",
         "situacao": "nao ha no repositorio lista municipal do IBGE da faixa de fronteira nem da Amazonia Legal",
         "resolucao": "usado o atributo municipal amazonia_legal e faixa_fronteira do PMMB consolidado (Ministerio da "
                      "Saude, dados abertos, retrato de 09/10/2026, SHA-256 registrado), que a auditoria 18 (§4) "
                      "indica para essa estratificacao; nada e aproximado. A faixa de fronteira e a classificacao "
                      "atribuida pelo MS ao municipio, nao uma lista do IBGE conferida aqui"
                      if s4.get("tabela") is not None else s4.get("motivo", "")},
        {"data": DATA_EXECUCAO, "item": "conferencia da linha E0 do E5 (Y1 ponderado por celulas)",
         "situacao": "na primeira execucao, a comparacao direta E6 x E5 com tolerancia 1e-10 falhou nessa linha "
                     "(diferenca da ordem de 1e-10 no p); a causa e a entrada: o E5 le o Y1 do CSV do E4, gravado com "
                     "menos digitos que o F1.3 da tarefa B (diferenca por municipio registrada em validacoes.E5)",
         "resolucao": "a linha E0 passa a ser conferida rodando a mesma estimacao da rdd_lib com o Y1 do E4 como "
                      "entrada (tolerancia 1e-10 mantida); a diferenca da linha do E6 para o E5 e a diferenca de "
                      "entrada ficam registradas; nenhuma estimativa do E6 foi alterada"},
        {"data": DATA_EXECUCAO, "item": "Poisson local e limites de Lee empilhados",
         "situacao": "a rdd_lib (tarefa A) so tem Poisson local e limites de Lee em um corte",
         "resolucao": "relatados por ciclo e corte; as linhas empilhadas de Lee saem NAO_EXECUTADO com o motivo"},
        {"data": DATA_EXECUCAO, "item": "IVS dos municipios criados depois de 2010",
         "situacao": "sem IVS 2010 oficial: " + json.dumps(conf_pop["municipios_sem_ivs_oficial_fora_da_rdd"]),
         "resolucao": "fora da RDD (sem imputacao)"},
    ]
    decisoes += [
        "Ciclos empilhados: grupo = ciclo (ou ciclo x corte), com intercepto e inclinacoes por grupo x lado; o "
        "intercepto por ciclo contem o efeito fixo de ciclo do protocolo (§6). CR1 por municipio.",
        "Cortes empilhados: sempre CR1 por municipio (o mesmo municipio pode estar nas duas janelas com h = 0,080).",
        "q BKY: dentro de cada familia F0, F1, F2, F4, sobre todas as linhas 'principal' do protocolo (cada outcome x "
        "populacao x ciclo x corte, incluindo cortes empilhados e ciclos empilhados). Sensibilidades de construcao da "
        "tarefa B, S1 e o indice P1 ficam fora.",
        "Indice P1: z-scores pelo lado abaixo do corte dentro da janela h = 0,050 (-50 < x <= 0) em cada ciclo x corte; "
        "a mesma padronizacao e usada nas sensibilidades h = 0,030 e 0,080. F2.1 nao existe no ciclo 3: o indice de "
        "V3 tem tres componentes. Componente ausente nao e imputado.",
        "IC honesto: M pela regra de bolso com suporte ate o ponto medio entre os cortes (cortes_vizinhos = (300, 400)); "
        "h fixo = protocolo; h otimo = especificacao adicional rotulada. No empilhado, M = maximo da regra por grupo; "
        "nao ha h otimo empilhado.",
        "F4.1: principal = local linear nos municipios com >= 1 celula preenchida (condicional); limites de Lee com "
        "selecionado = n_celulas_preenchidas_ch1 > 0 (identico a ter pontuacao de alocado, conferido na tarefa B).",
        "F0.3 condicionais (vagas pedidas, fracao priorizada): so municipios que constam do resultado final; o "
        "ponderado da fracao priorizada usa as vagas pedidas como peso; nao ha tabela no nivel da celula para G3.",
        "Local randomization: IC por inversao (grade do E5) so para outcomes em [0, 1]; para os demais so p de Fisher.",
        "S2–S4 aplicados a especificacao principal de cada outcome por ciclo e corte, as amostras de ciclos "
        "empilhados por corte e ao indice; S2 tambem aos cortes empilhados. S4 so em 0,400.",
        "S1 (ativas_coparticipacao por 10 mil hab.) recebe as mesmas especificacoes de uma outcome de U (familia S1, "
        "fora do BKY).",
    ]
    contagens = {
        "linhas": int(len(est)), "linhas_no_protocolo": int(est["no_protocolo"].sum()),
        "nao_executado": int((est["status"] == "NAO_EXECUTADO").sum()),
        "sem_estimativa": int((est["status"] == "SEM_ESTIMATIVA").sum()),
        "por_especificacao": est["especificacao"].value_counts().sort_index().to_dict(),
        "por_familia": est["familia"].value_counts().sort_index().to_dict(),
        "bky_por_familia": est[est["entra_bky"]].groupby("familia").size().to_dict(),
    }
    resumo = {
        "etapa": "E6_funil",
        "natureza_dos_dados": "EMPIRICO",
        "data_execucao": DATA_EXECUCAO,
        "script": rotulo(Path(__file__)),
        "protocolo": {"arquivo": rotulo(PROTOCOLO_JSON), "sha256": sha256(PROTOCOLO_JSON),
                      "texto_canonico": rotulo(PROTOCOLO_MD), "sha256_texto_canonico": sha_md,
                      "sha256_texto_canonico_declarado_no_json": protocolo.get("sha256_texto_canonico"),
                      "texto_igual_ao_declarado": sha_md == protocolo.get("sha256_texto_canonico")},
        "contraste": CONTRASTE,
        "salto": "tau = lado com bolsa maior (s > c) menos lado com bolsa menor; o corte pertence ao lado inferior",
        "entradas": entradas,
        "populacoes": {k: int(len(v)) for k, v in pops.items()},
        "celulas": info_out,
        "pmmb": info_pmmb,
        "covariaveis_balanco": notas_cov,
        "janelas_lr": {f"{k[0]}|{ROTULO_CORTE[k[1]]}": (v / 1000 if v else None) for k, v in lr.items()},
        "S3": {"status": "EXECUTADO" if s3.get("tabela") is not None else "NAO_EXECUTADO",
               "motivo": s3.get("motivo"), "definicao": s3.get("definicao"),
               "portes_muda": {ROTULO_CORTE[c]: sorted(v) for c, v in (s3.get("portes_muda") or {}).items()},
               "mapa_estrato_codigo_porte": s3.get("mapa_estrato")},
        "S4": {"status": "EXECUTADO" if s4.get("tabela") is not None else "NAO_EXECUTADO",
               "motivo": s4.get("motivo"), "definicao": s4.get("definicao"),
               "municipios_PMMB_sem_atributo": s4.get("linhas_sem_atributo")},
        "diagnostico_M_regra_de_bolso": diagnostico_m(dados, extras["indice"]["dados_klk"]),
        "indice": {m: {"linhas_sem_indice": extras["indice"][m]["linhas_sem_indice"],
                       "parametros": extras["indice"][m]["parametros"]} for m in ("klk", "anderson")},
        "validacoes": {"populacoes": conf_pop, "selecao_lr": conf_lr, "E3": val_e3, "E5": val_e5,
                       "linhas_com_nan_sem_nota": 0},
        "p1_para_holm": {k: (None if pd.isna(p1[k]) else float(p1[k])) for k in
                         ("tau", "ep", "ic95_inf", "ic95_sup", "p_valor", "ic_honesto_inf", "ic_honesto_sup")}
        | {"descricao": "P1: indice KLK, ciclos e cortes empilhados, h = 0,050, CR1 por municipio; o Holm com P2 e "
                        "feito pelo coordenador (E8)"},
        "contagens": contagens,
        "decisoes": decisoes,
        "desvios": desvios,
        "saidas": {n: {"arquivo": rotulo(OUT / n), "sha256": sha256(OUT / n)} for n in (NOME_EST, NOME_DIAG, NOME_LR)}
        | {"figuras": [rotulo(OUT / DIR_FIG / f) for f in figs]},
        "linguagem": "RDD em nivel = pacote do corte; resultado nulo e falta de evidencia com a precisao relatada, "
                     "nao ausencia de efeito",
    }
    _gravar_json(OUT / NOME_RESUMO, resumo)
    atualizar_doc()
    print(json.dumps(_nan_none({"P1": resumo["p1_para_holm"], "contagens": {k: v for k, v in contagens.items()
                                                                              if not isinstance(v, dict)}}),
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except FalhaValidacao as erro:
        print(f"FALHA DE VALIDACAO: {erro}", file=sys.stderr)
        sys.exit(2)
