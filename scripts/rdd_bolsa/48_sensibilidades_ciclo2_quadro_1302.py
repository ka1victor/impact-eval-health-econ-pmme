"""Adendo 52d: sensibilidades da escolha no ciclo 2 com o tipo de vaga do quadro de 13/02/2026.

Adendo congelado: `docs/06_execucao/52d_adendo_sensibilidades_ciclo2_quadro_1302.md` (26/10/2026, antes de rodar),
com estatuto `ADENDO_52D_POS_RESULTADO`. Toda saída leva `natureza_dos_dados = EMPIRICO`.

Motivo (auditoria 41, achado A1)
--------------------------------
O adendo 52c (script 42, doc 57p) refez com o quadro de 13/02/2026 só as principais da escolha (E9 principal, P1 M1 e
M5, P1h-1). As sensibilidades que sustentam a robustez do ciclo 2 (doc 44) ainda usavam o quadro retificado de
19/03/2026, refeito depois do resultado preliminar: o conjunto "só células com vaga imediata" do E9, as variantes M2,
M4 e M6 a M9 do P1 e a DAP e os km equivalentes do P1 e do P1h.

O que o script faz
------------------
1. **Portão (VD-5).** Reestima, com o tipo de vaga antigo (19/03) e com as funções dos scripts 16, 25 e 25c
   importadas sem alteração (pelo 42), todas as linhas que este adendo refaz, e as compara com `E9_estimativas.csv`,
   `E9_efeitos_marginais.csv`, `P1_estimativas.csv`, `P1_dap.csv` e `P1h_magnitudes.csv` (diferença ≤ 1e−8; relativa
   quando o valor gravado passa de 1 em módulo, porque os CSV têm 10 algarismos significativos). Se falhar, a
   execução para (`FALHA_REPRODUCAO_<linha>`), as saídas calculadas são apagadas e nada é corrigido.
2. **Correção.** Só no ciclo 2, `vagas_imediatas`, `tem_vaga_imediata` e `log_vagas_imediatas_mais_1` vêm do quadro de
   13/02 (função `corrigir` do 42, mesmo leitor e mesma conferência contra a auditoria 36), e o conjunto "só células
   com vaga imediata" e a marca da 1ª opção dos candidatos são refeitos pela regra do script 12 com esse quadro.
3. **VD-1 a VD-4** com a versão corrigida, lado a lado com a antiga; BKY refeito nas famílias secundárias dos
   protocolos de origem (P1, protocolo 52; P1h-3, protocolo 52b).
4. **Leitura do §3** por regra fixada no código (`leitura`), sem escolha depois de ver os números.

Contraste: pacote do corte e incentivo marginal da bolsa na escolha condicional a candidatar-se, dentro das vagas
abertas. Não é efeito da participação no PMM-E nem do Agora Tem Especialistas. A origem é preferência revelada, não
efeito causal.

Integridade
-----------
Só lê `data/` (os quadros do ciclo 2 e, pelas funções do 25, a CIR e os centroides) e `output/`; não escreve em
`data/`. O IVS 2010 oficial vem do a08; o arquivo local de IVS da auditoria 16 não é lido. Nada simulado nem imputado.
Sem nome, CPF, CRM ou pseudônimo de candidato em `output/`. As saídas `E9_*`, `P1_*`, `P1h_*` e `VC_*` não são
regravadas.

Uso
---
    python3 scripts/rdd_bolsa/48_sensibilidades_ciclo2_quadro_1302.py
    python3 scripts/rdd_bolsa/48_sensibilidades_ciclo2_quadro_1302.py --atualizar-doc   # só regrava o doc 57v
    python3 scripts/rdd_bolsa/48_sensibilidades_ciclo2_quadro_1302.py --pre-registro    # doc 57v sem resultados
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
DIR_RDD = ROOT / "scripts" / "rdd_bolsa"


def _importar(caminho: Path, nome: str):
    bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    sys.dont_write_bytecode = bytecode
    return mod


# O 42 importa o 25c, que importa o 25, que importa o 16: usam-se os mesmos objetos (sem reescrever nenhum deles).
VC = _importar(DIR_RDD / "42_escolha_vaga_imediata_c2.py", "vaga_imediata_c2_para_vd")
P1H = VC.P1H
P1 = VC.P1
E9 = VC.E9
L = P1.L
X45 = P1.X45

# ---------------------------------------------------------------------------
# Caminhos
# ---------------------------------------------------------------------------

SCRIPT_42 = DIR_RDD / "42_escolha_vaga_imediata_c2.py"
SCRIPT_25 = DIR_RDD / "25_escolha_dap.py"
SCRIPT_25C = DIR_RDD / "25c_magnitudes_P1h.py"
SCRIPT_16 = DIR_RDD / "16_estimar_E9_escolha.py"
ADENDO_MD = ROOT / "docs" / "06_execucao" / "52d_adendo_sensibilidades_ciclo2_quadro_1302.md"
ADENDO_52C = VC.ADENDO_MD
PROTOCOLO_40 = E9.PROTOCOLO_MD
PROTOCOLO_52 = VC.PROTOCOLO_52
PROTOCOLO_52B = VC.PROTOCOLO_52B
DOC = ROOT / "docs" / "06_execucao" / "57v_sensibilidades_ciclo2_quadro_1302.md"
OUT = ROOT / "output" / "rdd_bolsa"
E9_EST = E9.OUT_ESTIMATIVAS
E9_EFE = E9.OUT_EFEITOS
P1_EST = P1.OUT_EST
P1_DAP = P1.OUT_DAP
P1H_CSV = P1H.OUT_CSV
VC_CSV = VC.OUT_CSV
OUT_CSV = OUT / "VD_estimativas.csv"
OUT_RESUMO = OUT / "VD_resumo.json"
DIR_FIG = OUT / "VD_figuras"
FIG = DIR_FIG / "VD_antigo_corrigido.png"

# ---------------------------------------------------------------------------
# Parâmetros (adendo 52d e protocolos de origem; nenhum é dado)
# ---------------------------------------------------------------------------

DATA_EXECUCAO = "2026-10-26"
NATUREZA = "EMPIRICO"
ESTATUTO = "ADENDO_52D_POS_RESULTADO"
COMMIT_ADENDO = "c87ed75"
TOL_REPRODUCAO = 1e-8
ALFA = 0.05
Z95 = float(stats.norm.ppf(0.975))
PASSO_BOLSA = 5.0
CICLO_CORRIGIDO = VC.CICLO_CORRIGIDO
ANTIGA, CORRIGIDA = VC.ANTIGA, VC.CORRIGIDA
VERSOES = (ANTIGA, CORRIGIDA)
QUADRO_DA_VERSAO = {ANTIGA: "19/03/2026", CORRIGIDA: "13/02/2026"}
EMPILHADO = P1.EMPILHADO
B = P1.TERMO_BOLSA
MOD_E9 = E9.MODELO_COND
ESPEC_E9 = E9.ESPEC_PRINCIPAL
AMOSTRA = "P1 (G1 com origem)"
VD3 = ("M2", "M4", "M6_nota", "M6_municipio", "M6_curso", "M7", "M8", "M9")
VD3_BETA = ("M2", "M4", "M7", "M8", "M9")           # variantes com um único peso da bolsa (média no M8)
DAP_VD4 = ("M1", "M4", "M7", "M5_2")                  # DAP que usam o tipo de vaga do ciclo 2
DUF_VD4 = ("M2", "M4", "M7")                          # D_UF do P1h-3 que dependem do VD-3
FAMILIA_P1 = "P1 secundária (protocolo 52, §4)"
FAMILIA_P1H3 = "P1h-3 (protocolo 52b, §3)"
TERMO_RC = {"M8": f"media_{B}"}                       # peso da bolsa usado na razão de chances

ROTULO = {
    "E9s_2": "E9, só vaga imediata, ciclo 2",
    "E9s_emp": "E9, só vaga imediata, ciclos 1–3",
    "M1": "P1 M1 (principal)",
    "M2": "P1 M2 (log da distância)",
    "M4": "P1 M4 (efeito fixo de UF)",
    "M5_1": "P1 M5, ciclo 1",
    "M5_2": "P1 M5, ciclo 2",
    "M5_3": "P1 M5, ciclo 3",
    "M6_nota": "P1 M6, nota",
    "M6_municipio": "P1 M6, município de origem",
    "M6_curso": "P1 M6, curso",
    "M7": "P1 M7 (logit explodido)",
    "M8": "P1 M8 (logit misto, média)",
    "M9": "P1 M9 (logit aninhado)",
    "P1d": "P1d, Wald entre ciclos",
}

COLUNAS = ["natureza_dos_dados", "estatuto", "id_vd", "versao", "versao_quadro_ciclo2", "bloco", "chave_modelo",
           "modelo", "ciclo", "tipo_linha", "termo", "estimativa", "ep_cluster_conjunto", "ep_mle",
           "ep_cluster_candidato", "ic95_inf", "ic95_sup", "p", "p_t_g_menos_1", "p_mle", "li95_unilateral",
           "p_unilateral", "estatistica_wald", "gl", "ic95_boot_inf", "ic95_boot_sup", "ic95_fieller_inf",
           "ic95_fieller_sup", "li95_unilateral_fieller", "inferencia_cluster_degenerada", "entra_bky",
           "familia_bky", "q_bky", "g_conjuntos", "g_candidatos", "n_candidatos", "n_alternativas_ou_linhas",
           "n_conjuntos", "status", "nota"]

COMO_LER = ("Cada linha é uma especificação; o círculo vazado cinza é a versão antiga (tipo de vaga do ciclo 2 pelo "
            "quadro de 19/03/2026, refeito depois do resultado preliminar) e o ponto azul é a versão corrigida (quadro "
            "de 13/02/2026, vigente na inscrição). As barras são o IC 95% com cluster por conjunto de escolha (curso × "
            "ciclo). À esquerda, a razão de chances por +R$ 5 mil de bolsa anunciada, em escala log: acima de 1, a "
            "célula com bolsa maior é mais escolhida como 1ª opção; a linha vertical marca 1 (nenhum efeito). As duas "
            "primeiras linhas são o E9 no conjunto só com vaga imediata (VD-1 e VD-2); as demais, as variantes do P1 "
            "(VD-3; no M8, a média da bolsa; no M9, o peso na escala do logit aninhado). À direita, D_UF = θ_UF − 10·β, "
            "o peso de a vaga ficar na UF de origem menos o de toda a amplitude da bolsa (R$ 10 → 20 mil), em "
            "log-chance; acima de 0, a origem pesa mais. Tudo é escolha condicional a se candidatar, dentro das vagas "
            "abertas; a bolsa mede o pacote do corte, e a origem é preferência revelada, não efeito causal.")


class FalhaValidacao(RuntimeError):
    pass


rel = P1.rel
sha256 = P1.sha256
gravar_json = P1.gravar_json
_n, _p, _peq, _ic, _tab = P1._n, P1._p, P1._peq, P1._ic, P1._tab


def _int(v) -> str:
    return "—" if v is None or pd.isna(v) else f"{int(v)}"


def _verdadeiro(v) -> bool:
    return str(v).strip().lower() in ("true", "1", "1.0")


# ---------------------------------------------------------------------------
# Decisões de implementação (registradas e commitadas antes de qualquer estimativa)
# ---------------------------------------------------------------------------

DECISOES = [
    {"data": "2026-10-26", "item": "Conjunto \"só células com vaga imediata\" com o quadro de 13/02",
     "situacao": "O §2 manda tirar do quadro de 13/02 a definição do conjunto de escolha \"só células com vaga "
                 "imediata\", sem dizer como.",
     "resolucao": "Mesma regra do script 12 (`conjunto_escolha` e `tabela_escolhas`): o conjunto é o subconjunto "
                  "`tem_vaga_imediata == 1` do conjunto principal, e entram os candidatos com `celula_com_vaga_imediata "
                  "== 1` (1ª opção em célula com vagas imediatas > 0). No ciclo 2, a regra é aplicada ao conjunto "
                  "principal corrigido pela função `corrigir` do script 42 e à marca da 1ª opção refeita com as vagas "
                  "imediatas de 13/02. Antes, o script confere que a mesma regra, aplicada ao quadro de 19/03, "
                  "reproduz célula a célula o conjunto gravado pelo script 12 e a marca gravada de cada candidato; se "
                  "não reproduzir, para. Célula escolhida sem linha ou sem número no quadro de 13/02 faz parar: nada "
                  "é imputado."},
    {"data": "2026-10-26", "item": "Especificação do E9 no VD-1 e no VD-2",
     "situacao": "No conjunto de sensibilidade, o doc 42 estimou quatro especificações por ciclo; a linha VD-1 é a "
                 "razão de chances por +R$ 5 mil.",
     "resolucao": "Só a especificação principal do E9 (logit condicional da 1ª opção, spline linear, bolsa linear), "
                  "no ciclo 2 (VD-1) e nos ciclos empilhados (VD-2), como o script 42 fez no conjunto principal. O "
                  "spline quadrático e os degraus por corte no conjunto de sensibilidade não são refeitos; os ciclos "
                  "1 e 3 não mudam por construção. Inferência como no doc 42 (cluster por conjunto de escolha). O "
                  "score bootstrap e os placebos de corte do doc 42 foram usados só no conjunto principal (robustez "
                  "pós-auditoria), nunca no de sensibilidade, e por isso não entram aqui."},
    {"data": "2026-10-26", "item": "Alcance do VD-3",
     "situacao": "O §2 pede M2, M4, M6, M7, M8 e M9 \"nos ciclos e no empilhado em que usam o tipo de vaga\".",
     "resolucao": "No P1 essas variantes só existem empilhadas, e todas usam o tipo de vaga do ciclo 2 (seção 3): "
                  "M2, M4, M6 da nota, do município e do curso, M7, M8 e M9. O M3 não foi estimado no P1 e continua "
                  "fora. O M1 e o M5 do ciclo 2 já foram corrigidos pelo adendo 52c; aqui são reestimados só como base "
                  "da DAP, dos km, do M8 e do M9 e como membros das famílias BKY, e o script confere que saem iguais "
                  "ao `VC_estimativas.csv` nas duas versões. O M5 dos ciclos 1 e 3 entra só no Wald e no BKY e tem de "
                  "sair idêntico nas duas versões."},
    {"data": "2026-10-26", "item": "Alcance do VD-4",
     "situacao": "O §2 diz \"DAP e km equivalentes que dependem de VD-3\", mas os km equivalentes (P1h-2) só existem "
                 "no M1, e a DAP do M1 e a do M5 também usam o tipo de vaga e não foram refeitas pelo 52c (doc 57p, "
                 "§7).",
     "resolucao": "VD-4 = toda linha de DAP e de km que usa o tipo de vaga do ciclo 2 e ainda não tinha versão "
                  "corrigida: DAP do M1 (delta e bootstrap de pares por conjunto, 999 réplicas, mesma semente do "
                  "script 25), do M4, do M7 e do M5 do ciclo 2; K5 e K10 (M1); D_UF do P1h-3 no M2, no M4 e no M7. "
                  "As DAP do M5 nos ciclos 1 e 3 não usam o ciclo 2 e não são refeitas. M8 e M9 não têm DAP nem D_UF "
                  "nos originais e continuam sem."},
    {"data": "2026-10-26", "item": "BKY nas secundárias",
     "situacao": "O §2 pede \"BKY entre as secundárias\" sem listar a família; o script 42 deixou pendentes as "
                 "famílias BKY dos protocolos de origem, porque parte delas não estava no 52c.",
     "resolucao": "Refazer as duas famílias exatamente como nos originais, com as linhas corrigidas no lugar das "
                  "antigas: (a) família secundária do P1 (protocolo 52): β da bolsa no M5 por ciclo, Wald do P1d, "
                  "interações e Wald do M6 da nota, interação do M6 do município, média da bolsa e desvios no M8; (b) "
                  "família P1h-3 (protocolo 52b): D_UF, p unilateral, no M2, no M4, no M5 por ciclo e no M7. As "
                  "linhas do E9 (VD-1, VD-2) ficam sem correção múltipla, como no protocolo 40 (§12) e no script 42. "
                  "DAP e km continuam descritivos, sem teste, como nos originais. Não se cria família nova."},
    {"data": "2026-10-26", "item": "Tolerância do portão",
     "situacao": "O §4 pede diferença ≤ 1e−8; os CSV de origem gravam 10 algarismos significativos, e para valores "
                 "com módulo acima de 1 (DAP, km, Wald, log-verossimilhança) a diferença absoluta de 1e−8 fica abaixo "
                 "da precisão gravada.",
     "resolucao": "Diferença absoluta ≤ 1e−8 quando o valor gravado tem módulo ≤ 1, e relativa ≤ 1e−8 quando tem "
                  "módulo maior; NaN só casa com NaN. Entram todas as linhas VD-5 (coeficientes, os três EP, IC, p, "
                  "Wald, q BKY, DAP com IC delta e bootstrap, km com Fieller, D_UF). Qualquer falha para a execução "
                  "antes da versão corrigida, e as saídas calculadas são apagadas."},
    {"data": "2026-10-26", "item": "M8 e M9",
     "situacao": "O logit misto e o aninhado têm tetos de avaliações e polimento por Newton no script 25.",
     "resolucao": "Mesmas funções (`estimar_misto`, `estimar_aninhado`), mesmos tetos, sementes e polimento, partindo "
                  "do M1 da mesma versão. Se a versão corrigida não convergir, a linha fica NAO_CONVERGIU com o motivo; "
                  "nada é forçado."},
    {"data": "2026-10-26", "item": "Leitura do §3 por regra",
     "situacao": "O §3 fixa a leitura do VD-1 e do VD-3, mas não o critério de \"sinal\" e de \"significância\".",
     "resolucao": "VD-1 'mantém' quando o IC 95% da razão de chances corrigida exclui 1 e o log da razão tem o mesmo "
                  "sinal do antigo; 'dependia do quadro pós-resultado' quando o IC corrigido contém 1; IC que exclui 1 "
                  "com sinal oposto não está no §3 e é relatado como 'sinal oposto', sem leitura. VD-3: uma variante "
                  "muda de sinal quando a estimativa pontual de algum peso da bolsa dela muda de sinal (β da bolsa; "
                  "média no M8; inclinações e interações no M6); a leitura da H2 lista as que não mudam. Mudança de "
                  "significância compara, nas duas versões, o mesmo critério: q BKY < 0,05 nas linhas das famílias "
                  "BKY; IC 95% com cluster por conjunto que exclui 0 (ou 1, na razão de chances) nas demais; p de "
                  "máxima verossimilhança < 0,05 no M6 do curso (cluster degenerado, como no P1); IC delta (e, no M1, "
                  "também o do bootstrap) na DAP e nos km."},
    {"data": "2026-10-26", "item": "Razão de chances das variantes",
     "situacao": "O P1 não gravou razão de chances.",
     "resolucao": "exp(5·β) com o IC transformado do IC do coeficiente, como no script 42; no M8, com a média da "
                  "bolsa; no M9, com o β da utilidade do logit aninhado (descritiva)."},
    {"data": "2026-10-26", "item": "Números do doc 57v",
     "situacao": "O pedido do autor exige números só em blocos gerados.",
     "resolucao": "Todo número de resultado do 57v vem de `VD_*` por `--atualizar-doc`, entre marcadores "
                  "`<!-- VD:... -->`; o teste confere o doc contra o gerado e que não há número de resultado fora "
                  "dos blocos."},
]

# Inventário: o que usa o tipo de vaga do ciclo 2 (lido do código dos scripts 16, 25 e 25c; sem estimar nada).
INVENTARIO = [
    ("E9, conjunto \"só células com vaga imediata\", ciclo 2 e empilhado (doc 42)", "sim",
     "define o conjunto e os candidatos; `log_vagas_imediatas_mais_1` é covariável (`tem_vaga_imediata` é constante "
     "e sai)", "refeita (VD-1, VD-2)"),
    ("E9, mesmo conjunto, ciclos 1 e 3", "não", "o tipo de vaga só muda no ciclo 2", "não refeita"),
    ("P1 M2 (log da distância)", "sim", "`tem_vaga_imediata` e `log_vagas_imediatas_mais_1` do M1, ciclos 1–3 "
     "empilhados", "refeita (VD-3)"),
    ("P1 M4 (efeito fixo de UF da vaga)", "sim", "idem", "refeita (VD-3)"),
    ("P1 M6 da nota, do município e do curso", "sim", "idem, mais as interações da bolsa", "refeitas (VD-3)"),
    ("P1 M7 (logit explodido)", "sim", "idem, nos postos 1 e 2", "refeita (VD-3)"),
    ("P1 M8 (logit misto)", "sim", "matriz do M1 e partida no M1", "refeita (VD-3)"),
    ("P1 M9 (logit aninhado)", "sim", "matriz do M1 e partida no M1", "refeita (VD-3)"),
    ("P1 M3 (origem mais próxima)", "—", "não foi estimado no P1 (`NAO_EXECUTADO`)", "nada a refazer"),
    ("DAP do M1, quatro atributos, delta e bootstrap (doc 57a)", "sim",
     "β e atributos do M1; \"1 vaga imediata\" é a própria covariável", "refeita (VD-4)"),
    ("DAP do M4 e do M7", "sim", "coeficientes do M4 e do M7", "refeitas (VD-4)"),
    ("DAP do M5, ciclo 2", "sim", "coeficientes do M5 do ciclo 2", "refeita (VD-4)"),
    ("DAP do M5, ciclos 1 e 3", "não", "ciclos sem mudança", "não refeitas"),
    ("km equivalentes K5 e K10 (P1h-2, M1; doc 57i)", "sim", "β e distância do M1", "refeitas (VD-4)"),
    ("D_UF do P1h-3 no M2, no M4 e no M7", "sim", "coeficientes dessas variantes", "refeitas (VD-4)"),
    ("D_UF do P1h-3 no M5", "ciclo 2 sim; ciclos 1 e 3 não", "coeficientes do M5 de cada ciclo",
     "recalculadas só para o BKY da família (o ciclo 2 já estava no 52c)"),
]
FORA_DO_ADENDO = ("Fora do §1 do adendo também usam o tipo de vaga do ciclo 2, e não são refeitas aqui: o logit "
                  "explodido e as variantes quadrática e de degraus do E9 no conjunto principal; o M0 do P1; a ponte "
                  "P1g (salto previsto pelo M1); os pesos descritivos da figura do P1h. Fica registrado para o autor.")


# ---------------------------------------------------------------------------
# Insumos e correção
# ---------------------------------------------------------------------------

def sensibilidade_pela_regra(conj: pd.DataFrame) -> pd.DataFrame:
    """Conjunto "só células com vaga imediata": subconjunto `tem_vaga_imediata == 1` (script 12, conjunto_escolha)."""
    return conj[conj["tem_vaga_imediata"] == 1].reset_index(drop=True)


CHAVE = ["ciclo", "co_cnes_7d", "cod_curso"]


def conferir_sensibilidade_gravada(sens_gravada: pd.DataFrame, sens_regra: pd.DataFrame) -> dict:
    """O conjunto de sensibilidade gravado pelo script 12 é a regra aplicada ao conjunto principal (versão antiga)."""
    a = sens_gravada.sort_values(CHAVE).reset_index(drop=True)
    b = sens_regra.sort_values(CHAVE).reset_index(drop=True)
    if len(a) != len(b) or not (a[CHAVE].to_numpy() == b[CHAVE].to_numpy()).all():
        raise FalhaValidacao(f"conjunto de sensibilidade gravado ({len(a)} células) difere da regra ({len(b)})")
    cols = ["vagas_imediatas", "log_vagas_imediatas_mais_1", "tem_vaga_imediata", "bolsa_mil", "s_mil",
            "populacao_2022"]
    dif = {c: float(np.max(np.abs(a[c].to_numpy(dtype=float) - b[c].to_numpy(dtype=float)))) for c in cols}
    for c in ("id_conjunto_escolha", "macrorregiao", "estrato_territorial", "faixa_anunciada", "co_ibge"):
        if not (a[c].to_numpy() == b[c].to_numpy()).all():
            raise FalhaValidacao(f"conjunto de sensibilidade gravado difere da regra na coluna {c}")
    if any(v > 0 for v in dif.values()):
        raise FalhaValidacao(f"conjunto de sensibilidade gravado difere da regra: {dif}")
    return {"celulas": int(len(a)), "por_ciclo": {str(k): int(v) for k, v in a.groupby("ciclo").size().items()},
            "dif_max_por_coluna": dif, "regra": "subconjunto tem_vaga_imediata == 1 do conjunto principal (script 12)"}


def marca_vaga_imediata(cand: pd.DataFrame, quadro: pd.DataFrame) -> np.ndarray:
    """`celula_com_vaga_imediata` do ciclo 2 refeita com um quadro (fórmula do script 12, tabela_escolhas). Célula no
    quadro da 1ª chamada sem linha ou sem número no quadro dado faz parar (nada é imputado)."""
    m = (cand["ciclo"] == CICLO_CORRIGIDO).to_numpy()
    sub = cand.loc[m]
    q = quadro.set_index(["co_cnes_7d", "cod_curso"])["vagas_imediatas"]
    idx = pd.MultiIndex.from_frame(sub[["co_cnes_7d", "cod_curso"]])
    vi = q.reindex(idx).to_numpy(dtype=float)
    no_quadro = (sub["celula_no_quadro"] == 1).to_numpy()
    sem = int((no_quadro & np.isnan(vi)).sum())
    if sem:
        raise FalhaValidacao(f"FALHA_CELULA_AUSENTE_1302: {sem} escolhas do ciclo 2 em célula sem número de vagas "
                             "imediatas no quadro (nada é imputado)")
    return np.where(no_quadro, (np.nan_to_num(vi) > 0).astype(float), np.nan)


def corrigir_candidatos(cand: pd.DataFrame, q1302: pd.DataFrame, q1903: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Confere a marca gravada contra o quadro de 19/03 e a refaz, só no ciclo 2, com o de 13/02."""
    m = (cand["ciclo"] == CICLO_CORRIGIDO).to_numpy()
    antiga = marca_vaga_imediata(cand, q1903)
    gravada = cand.loc[m, "celula_com_vaga_imediata"].to_numpy(dtype=float)
    iguais = (antiga == gravada) | (np.isnan(antiga) & np.isnan(gravada))
    if not iguais.all():
        raise FalhaValidacao(f"marca gravada de vaga imediata difere do quadro de 19/03 em {int((~iguais).sum())} linhas")
    nova = marca_vaga_imediata(cand, q1302)
    c = cand.copy()
    c.loc[m, "celula_com_vaga_imediata"] = nova
    r1 = (c.loc[m, "opcao_rank"] == 1).to_numpy()
    return c, {"linhas_ciclo2": int(m.sum()), "marca_gravada_igual_ao_quadro_19mar": int(iguais.sum()),
               "primeiras_opcoes_ciclo2": int(r1.sum()),
               "primeiras_opcoes_com_vaga_imediata_19mar": int(np.nansum(antiga[r1])),
               "primeiras_opcoes_com_vaga_imediata_13fev": int(np.nansum(nova[r1])),
               "imputadas": 0}


def preparar(dados: dict) -> dict:
    q1302, q1903 = VC.ler_quadros_c2()
    conf_antiga = VC.conferir_versao_antiga(dados["conj"], q1903)
    conf_a36 = VC.conferir_contra_a36(q1302)
    conj_c, corr = VC.corrigir(dados["conj"], q1302)
    conj_p1_c, corr_p1 = VC.corrigir(dados["conj_p1"], q1302)
    sens_grav, diag_s = E9.preparar_conjunto(pd.read_parquet(E9.CONJ_SENSIBILIDADE), dados["ivs"], dados["mapa"])
    conf_sens = conferir_sensibilidade_gravada(sens_grav, sensibilidade_pela_regra(dados["conj"]))
    sens_c = sensibilidade_pela_regra(conj_c)
    cand_c, conf_cand = corrigir_candidatos(dados["cand"], q1302, q1903)
    s2a = sens_grav[sens_grav["ciclo"] == CICLO_CORRIGIDO]
    s2c = sens_c[sens_c["ciclo"] == CICLO_CORRIGIDO]
    return {"q1302": q1302, "q1903": q1903, "conj_c": conj_c, "conj_p1_c": conj_p1_c, "sens_a": sens_grav,
            "sens_c": sens_c, "cand_c": cand_c,
            "conferencias": {"versao_antiga_do_conjunto": conf_antiga, "quadro_1302_contra_a36": conf_a36,
                             "sensibilidade_gravada_igual_a_regra": conf_sens, "marca_dos_candidatos": conf_cand},
            "correcao": {"conjunto_principal_ciclo2": corr,
                         "conjunto_P1": {k: corr_p1[k] for k in ("celulas_ciclo2_no_conjunto",
                                                                 "celulas_sem_linha_no_quadro_1302",
                                                                 "celulas_com_vagas_imediatas_diferentes")},
                         "sensibilidade_ciclo2": {"celulas_19mar": int(len(s2a)), "celulas_13fev": int(len(s2c)),
                                                  "celulas_em_ambas": int(len(s2a.merge(s2c[CHAVE], on=CHAVE))),
                                                  "vagas_imediatas_19mar": float(s2a["vagas_imediatas"].sum()),
                                                  "vagas_imediatas_13fev": float(s2c["vagas_imediatas"].sum())},
                         "quadro_antigo": rel(VC.QUADRO_1903), "quadro_corrigido": rel(VC.QUADRO_1302)}}


# ---------------------------------------------------------------------------
# Estimação (funções dos scripts 16, 25 e 25c, sem alteração)
# ---------------------------------------------------------------------------

def _slim(r: dict) -> dict:
    for k in ("_A", "_D", "_scores", "_info", "_X", "_conj", "_esc_r1", "_esc", "_exc", "_grupos", "_info_inv"):
        r.pop(k, None)
    return r


def estimar_e9s(conj_s: pd.DataFrame, cand: pd.DataFrame, dados: dict, log=print) -> tuple[pd.DataFrame,
                                                                                            pd.DataFrame, dict]:
    """E9 principal (logit condicional, spline linear, bolsa linear) no conjunto só com vaga imediata."""
    est, efe, res = [], [], {}
    for chave, ciclo in (("E9s_2", "2"), ("E9s_emp", EMPILHADO)):
        ci = [1, 2, 3] if ciclo == EMPILHADO else [int(ciclo)]
        cj = conj_s[conj_s["ciclo"].isin(ci)].reset_index(drop=True)
        r = E9.estimar(cj, cand[cand["ciclo"].isin(ci)], MOD_E9, "sensibilidade", ESPEC_E9, dados["macros"],
                       dados["estratos"])
        if not r["ok"]:
            raise FalhaValidacao(f"{chave} não convergiu")
        est += E9.linhas_estimativas(ciclo, r)
        efe += E9.linhas_efeitos(ciclo, r)
        res[chave] = _slim(r)
        log(f"{chave}: ok, it={r['iteracoes']}, candidatos={r['n_candidatos']}")
    return pd.DataFrame(est), pd.DataFrame(efe), res


def linhas_m6(D: dict, dados: dict, res: dict, log=print) -> list[dict]:
    """M6 da nota, do município e do curso: o mesmo bloco do `main` do script 25 (lá ele não é função)."""
    est = []
    TB = P1.TERMO_BOLSA
    G1g = D["grupos"]
    rot = pd.Series("sem_pontuacao", index=G1g.index, dtype=object)
    for k in P1.CICLOS:
        m = (G1g["ciclo"] == k) & G1g["pontuacao"].notna()
        t, _ = X45.tercis(G1g.loc[m, "pontuacao"])
        rot.loc[m] = [f"tercil{int(v)}" for v in t]
    rot_linha_nota = rot.to_numpy()[D["grp"]]
    ncurso = G1g.groupby("cod_curso").size()
    grandes = sorted(int(c) for c, n in ncurso.items() if n >= P1.MIN_CAND_CURSO)
    rot_curso = np.array([f"curso{int(c):02d}" if int(c) in grandes else "demais_cursos" for c in G1g["cod_curso"]],
                         dtype=object)
    cont_curso = pd.Series(rot_curso).value_counts()
    base_curso = sorted(cont_curso.index, key=lambda g: (-int(cont_curso[g]), g))[0]
    dims = {
        "M6_nota": ("tercil1", rot_linha_nota, ["tercil1", "tercil2", "tercil3", "sem_pontuacao"], False),
        "M6_municipio": ("fora_do_municipio", np.where(D["mesmo_municipio"] == 1, "mesmo_municipio", "fora_do_municipio"),
                         ["fora_do_municipio", "mesmo_municipio"], False),
        "M6_curso": (base_curso, rot_curso[D["grp"]], [f"curso{k:02d}" for k in grandes] + ["demais_cursos"], True),
    }
    for nome, (base, rot_l, ordem, degenerada) in dims.items():
        X = P1.matriz_modelo(D, dados, "M1")
        bolsa = X[TB].to_numpy()
        presentes = [g for g in ordem if g in set(rot_l)]
        outros = [g for g in presentes if g != base]
        for g in outros:
            X[f"bolsa_x_{g}"] = bolsa * (rot_l == g)
        r = P1.estimar(X, D, modelo=nome, ciclo=EMPILHADO, amostra=AMOSTRA)
        if not r["ok"]:
            raise FalhaValidacao(f"{nome} não convergiu")
        c = P1._comuns(r, "P1e")
        cont_g = pd.Series(rot_l[D["esc"]]).value_counts()
        nota_deg = ("dimensão curso: o termo de cada curso só varia nos conjuntos do curso; EP e p por cluster não "
                    "são confiáveis; usar o EP de máxima verossimilhança; fora do BKY" if degenerada else "")
        for g in presentes:
            a = P1.vetor(r, TB)
            if g != base:
                a = a + P1.vetor(r, f"bolsa_x_{g}")
            est.append(P1._linha(**c, tipo_linha="inclinacao_do_grupo", termo=f"bolsa_mil|{g}", **P1.combinacao(r, a),
                                 log_verossimilhanca=r["ll"], iteracoes=r["iteracoes"],
                                 inferencia_cluster_degenerada=degenerada, unidade="coeficiente por R$ 1 mil/mês",
                                 nota=P1._juntar(f"inclinação da bolsa no grupo {g} ({int(cont_g.get(g, 0))} escolhas)",
                                                 nota_deg)))
        R = []
        for g in outros:
            a = P1.vetor(r, f"bolsa_x_{g}")
            R.append(a)
            est.append(P1._linha(**c, tipo_linha="interacao", termo=f"bolsa_x_{g}", **P1.combinacao(r, a),
                                 log_verossimilhanca=r["ll"], iteracoes=r["iteracoes"],
                                 inferencia_cluster_degenerada=degenerada, entra_bky=not degenerada,
                                 unidade="diferença de inclinação por R$ 1 mil/mês",
                                 nota=P1._juntar(f"diferença da inclinação do grupo {g} para a do grupo {base}",
                                                 nota_deg)))
        if len(R) > 1:
            W, gl, pw = P1.wald(r, np.array(R))
            Wm_, _, pm_ = P1.wald(r, np.array(R), "V_mle")
            est.append(P1._linha(**c, tipo_linha="wald_igualdade", termo="wald_inclinacoes_iguais", estatistica_wald=W,
                                 gl=gl, p=pw, p_mle=pm_, inferencia_cluster_degenerada=degenerada,
                                 entra_bky=not degenerada,
                                 nota=P1._juntar(f"Wald de H0: inclinações iguais nos {len(presentes)} grupos; χ² com "
                                                 f"cluster por conjunto (MV: {Wm_:.4g})", nota_deg)))
        for t in r["termos"]:
            if t == TB or t.startswith("bolsa_x_"):
                continue
            est.append(P1._linha(**c, tipo_linha="coeficiente_controle", termo=t, **P1.combinacao(r, P1.vetor(r, t)),
                                 log_verossimilhanca=r["ll"], iteracoes=r["iteracoes"], nota="controle do modelo"))
        res[nome] = _slim(r)
        log(f"{nome}: ok grupos={presentes}")
    return est


def linhas_m9(r9: dict, r1: dict) -> list[dict]:
    """Linhas do M9 como no `main` do script 25."""
    est = []
    r9.update({"ciclo": EMPILHADO, "amostra": AMOSTRA, "n_candidatos": r1["n_candidatos"], "n_grupos": r1["n_grupos"],
               "n_linhas": r1["n_linhas"], "n_conjuntos": r1["n_conjuntos"]})
    c9 = P1._comuns(r9, "sensibilidade")
    for t in r9["termos"]:
        if r9["ok"]:
            cb = P1.combinacao(r9, P1.vetor(r9, t))
            if t == "lambda":
                cb.update({"p": np.nan, "p_t_g_menos_1": np.nan, "p_mle": np.nan})
            est.append(P1._linha(**c9, tipo_linha="coeficiente", termo=t, **cb, log_verossimilhanca=r9["ll"],
                                 iteracoes=r9["iteracoes"], nota=P1._juntar(r9["nota"], "p de H0: lambda = 0 não relatado"
                                                                            if t == "lambda" else "")))
        else:
            est.append(P1._linha(**c9, tipo_linha="coeficiente", termo=t, coef=float(r9["theta"][r9["termos"].index(t)]),
                                 log_verossimilhanca=r9["ll"], nota=r9["nota"]))
    if r9["ok"]:
        k = r9["termos"].index("lambda")
        lam = float(r9["theta"][k])
        ep = math.sqrt(r9["V_conj"][k, k])
        est.append(P1._linha(**c9, tipo_linha="teste_lambda_igual_1", termo="lambda_menos_1", coef=lam - 1,
                             ep_cluster_conjunto=ep, ep_mle=math.sqrt(r9["V_mle"][k, k]),
                             ep_cluster_candidato=math.sqrt(r9["V_cand"][k, k]), ic95_inf=lam - 1 - Z95 * ep,
                             ic95_sup=lam - 1 + Z95 * ep, p=float(2 * stats.norm.sf(abs((lam - 1) / ep))),
                             estatistica_wald=r9["lr_contra_M1"], gl=1, g_conjuntos=r9["G_conj"],
                             g_candidatos=r9["G_cand"],
                             nota=f"Wald de H0: lambda = 1 (cluster por conjunto); estatistica_wald guarda a razão de "
                                  f"verossimilhança contra M1 (p LR = {stats.chi2.sf(max(r9['lr_contra_M1'], 0), 1):.4g})"))
    return est


def linhas_m8(r8: dict, r1: dict) -> list[dict]:
    """Linhas do M8 como no `main` do script 25."""
    est = []
    r8.update({"ciclo": EMPILHADO, "amostra": AMOSTRA, "n_candidatos": r1["n_candidatos"], "n_grupos": r1["n_grupos"],
               "n_linhas": r1["n_linhas"], "n_conjuntos": r1["n_conjuntos"]})
    c8 = P1._comuns(r8, "P1f")
    for t in r8["termos"]:
        if r8["ok"]:
            cb = P1.combinacao(r8, P1.vetor(r8, t))
            alvo = t in (f"media_{B}", f"desvio_{B}", f"desvio_{P1.TERMO_DIST}")
            if t.startswith("desvio_"):
                cb["coef"] = abs(cb["coef"])
                cb["ic95_inf"], cb["ic95_sup"] = np.nan, np.nan
            est.append(P1._linha(**c8, tipo_linha="coeficiente", termo=t, **cb, log_verossimilhanca=r8["ll"],
                                 iteracoes=r8.get("iteracoes"), entra_bky=alvo, nota=r8["nota"]))
        else:
            est.append(P1._linha(**c8, tipo_linha="coeficiente", termo=t, nota=r8["nota"]))
    return est


def estimar_p1(dados: dict, conj_p1: pd.DataFrame, log=print) -> dict:
    """M1, M2, M4, M5 por ciclo, M6, M7, M8, M9, Wald do P1d, DAP (M1 com bootstrap, M4, M7, M5 ciclo 2) e P1h,
    com as funções do script 25 e do 25c, no conjunto `conj_p1`. Devolve as linhas nos esquemas dos CSV de origem."""
    dv = {**dados, "conj_p1": conj_p1}
    D = P1.montar_desenho(conj_p1, dados["r1_p1"], None, dv)
    conf_dist = P1.conferir_distancias(D)
    est: list[dict] = []
    res: dict[str, dict] = {}
    for m in ("M1", "M2", "M4"):
        r = P1.estimar(P1.matriz_modelo(D, dv, m), D, modelo=m, ciclo=EMPILHADO, amostra=AMOSTRA)
        if not r["ok"]:
            raise FalhaValidacao(f"{m} não convergiu")
        est += P1.linhas_modelo(r, {"M1": "P1a", "M2": "sensibilidade", "M4": "sensibilidade"}[m])
        res[m] = r if m == "M1" else _slim(r)
        log(f"{m}: ok it={r.get('iteracoes')}")
    r1 = res["M1"]
    bs, vs = [], []
    for k in P1.CICLOS:
        Dk = P1.montar_desenho(conj_p1[conj_p1["ciclo"] == k].reset_index(drop=True),
                               dados["r1_p1"][dados["r1_p1"]["ciclo"] == k], None, dv)
        rk = P1.estimar(P1.matriz_modelo(Dk, dv, "M1"), Dk, modelo="M5", ciclo=str(k), amostra=AMOSTRA)
        if not rk["ok"]:
            raise FalhaValidacao(f"M5 ciclo {k} não convergiu")
        est += P1.linhas_modelo(rk, "P1d")
        kb = rk["termos"].index(B)
        bs.append(rk["theta"][kb])
        vs.append(rk["V_conj"][kb, kb])
        res[f"M5_{k}"] = _slim(rk)
        log(f"M5 ciclo {k}: ok")
    for ln in est:
        if ln["modelo"] == "M5" and ln["termo"] == B:
            ln["entra_bky"] = True
    Rw = np.array([[1.0, -1.0, 0.0], [0.0, 1.0, -1.0]])
    d = Rw @ np.array(bs)
    Wm = float(d @ np.linalg.solve(Rw @ np.diag(vs) @ Rw.T, d))
    est.append(P1._linha(estimando="P1d", modelo="M5", descricao_modelo="Wald: β da bolsa igual nos ciclos 1, 2 e 3",
                         ciclo="1,2,3", amostra=AMOSTRA, tipo_linha="wald_igualdade_ciclos",
                         termo="wald_bolsa_igual_entre_ciclos", estatistica_wald=Wm, gl=2,
                         p=float(stats.chi2.sf(Wm, 2)), entra_bky=True,
                         nota="EP cluster por conjunto de cada ciclo; ciclos tratados como amostras independentes "
                              "(candidatos distintos; a mesma célula pode se repetir)"))
    est += linhas_m6(D, dv, res, log)
    De = P1.montar_desenho(conj_p1, dados["r1_p1"], dados["r2_p1"], dv)
    P1.conferir_distancias(De)
    r7 = P1.estimar(P1.matriz_modelo(De, dv, "M1"), De, modelo="M7", ciclo=EMPILHADO,
                    amostra="P1 (G1 com origem), 1ª e 2ª opção")
    if not r7["ok"]:
        raise FalhaValidacao("M7 não convergiu")
    est += P1.linhas_modelo(r7, "sensibilidade", nota_extra="logit explodido: conjunto do posto 2 = curso da 2ª opção, "
                                                             "sem a célula da 1ª quando os cursos coincidem")
    res["M7"] = _slim(r7)
    del De
    log("M7: ok")
    for ln in est:
        if ln["modelo"] == "M1" and ln["termo"] == B and ln["ciclo"] == EMPILHADO:
            ln["entra_holm"] = True
    atributos = list(P1.DAP_DEF)
    estim_dap = {"distancia_100km_a_menos": "P1b", "mesma_uf": "P1c", "capital": "P1c", "vaga_imediata": "P1c"}
    boot = P1.bootstrap_dap(r1, atributos, log=log)
    dap = P1.linhas_dap(r1, atributos, boot, estim_dap)
    for m in ("M4", "M7"):
        dap += P1.linhas_dap(res[m], atributos, None, estim_dap)
    dap += P1.linhas_dap(res["M5_2"], atributos, None, estim_dap)
    log("DAP e bootstrap prontos")
    cir = dados["mapa_cir"]
    cir_linha = pd.factorize(cir.reindex(D["conj"]["co_ibge"].to_numpy()[D["cel"]]).to_numpy())[0]
    r9 = P1.estimar_aninhado(r1, cir_linha)
    est += linhas_m9(r9, r1)
    log(f"M9: ok={r9['ok']} ({r9.get('segundos')} s)")
    r8 = P1.estimar_misto(r1, r1["termos"])
    est += linhas_m8(r8, r1)
    log(f"M8: ok={r8['ok']} ({r8.get('segundos')} s, {r8.get('avaliacoes')} avaliações)")
    res["M8"] = {k: v for k, v in r8.items() if not k.startswith("_")}
    res["M9"] = {k: v for k, v in r9.items() if not k.startswith("_")}
    res["M1"] = _slim(r1)
    del D
    est = pd.DataFrame(est)[P1.COLUNAS_EST]
    est["p_holm"] = np.nan
    mh = est["entra_holm"].astype(bool)
    est.loc[mh, "p_holm"] = L.holm(est.loc[mh, "p"].to_numpy())
    mb = est["entra_bky"].astype(bool) & est["p"].notna()
    est["q_bky"] = np.nan
    est.loc[mb, "q_bky"] = L.qvalores_bky(est.loc[mb, "p"].to_numpy())
    p1h = P1H.montar_linhas({k: res[k] for k, _, _ in P1H.ESPECS})
    p1h = p1h[p1h["id_linha"] != "FIG"].reset_index(drop=True)
    diag = {"conferencia_distancia": conf_dist, "bootstrap": boot,
            "m8": {k: v for k, v in res["M8"].items() if not k.startswith("V_") and k not in ("theta", "segundos")},
            "m9": {k: v for k, v in res["M9"].items() if not k.startswith("V_") and k not in ("theta", "segundos")},
            "convergencia": {m: {"ok": bool(r["ok"]), "status": r.get("status"), "iteracoes": r.get("iteracoes"),
                                 "omitidas": r.get("omitidas", [])} for m, r in res.items()}}
    return {"p1": est, "dap": pd.DataFrame(dap), "p1h": p1h, "res": res, "diag": diag}


def estimar_versao(dados: dict, conj_s: pd.DataFrame, cand: pd.DataFrame, conj_p1: pd.DataFrame, log=print) -> dict:
    e9_est, e9_efe, res_e9 = estimar_e9s(conj_s, cand, dados, log)
    p1 = estimar_p1(dados, conj_p1, log)
    return {"e9_est": e9_est, "e9_efe": e9_efe, "res_e9": res_e9, **p1}


# ---------------------------------------------------------------------------
# Portão de reprodução (VD-5)
# ---------------------------------------------------------------------------

def _dif_rel(a, b) -> float:
    """Diferença absoluta (|b| ≤ 1) ou relativa (|b| > 1); NaN só casa com NaN."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if a.shape != b.shape:
        return float("inf")
    na, nb = np.isnan(a), np.isnan(b)
    if (na != nb).any():
        return float("inf")
    ok = ~na
    if not ok.any():
        return 0.0
    return float(np.max(np.abs(a[ok] - b[ok]) / np.maximum(1.0, np.abs(b[ok]))))


def comparar(novo: pd.DataFrame, gravado: pd.DataFrame, chaves: list[str], colunas: list[str]) -> tuple[bool, dict, int]:
    """Casa as linhas por `chaves` (uma linha gravada para cada nova) e devolve a maior diferença por coluna."""
    g = gravado.copy()
    n = novo.copy()
    for c in chaves:
        g[c] = g[c].astype(str)
        n[c] = n[c].astype(str)
    if n.duplicated(chaves).any() or g.duplicated(chaves).any():
        return False, {"chaves_repetidas": float("inf")}, 0
    m = n.merge(g, on=chaves, how="left", suffixes=("", "_gravado"), indicator=True)
    if (m["_merge"] != "both").any():
        return False, {"linhas_sem_par_no_gravado": float((m["_merge"] != "both").sum())}, int(len(m))
    difs = {c: _dif_rel(m[c].to_numpy(dtype=float), m[f"{c}_gravado"].to_numpy(dtype=float))
            for c in colunas if c in n.columns and c in g.columns}
    return True, difs, int(len(m))


COLS_E9 = ["coef", "ep_cluster_conjunto", "ep_mle", "ep_cluster_candidato", "ic95_inf", "ic95_sup", "p",
           "p_t_g_menos_1", "g_conjuntos", "g_candidatos", "n_candidatos", "n_alternativas", "log_verossimilhanca"]
COLS_E9_EFE = ["estimativa", "ep_cluster_conjunto", "ep_mle", "ic95_inf", "ic95_sup"]
COLS_P1 = ["coef", "ep_cluster_conjunto", "ep_mle", "ep_cluster_candidato", "ic95_inf", "ic95_sup", "p",
           "p_t_g_menos_1", "p_mle", "estatistica_wald", "gl", "g_conjuntos", "g_candidatos", "n_candidatos",
           "n_linhas_candidato_celula", "n_conjuntos", "log_verossimilhanca", "p_holm", "q_bky"]
COLS_DAP = ["dap", "ep_delta", "ic95_delta_inf", "ic95_delta_sup", "ic95_boot_inf", "ic95_boot_sup", "n_boot",
            "n_boot_validos", "fracao_boot_beta_bolsa_nao_positivo", "n_candidatos", "g_conjuntos"]
COLS_P1H = ["estimativa", "ep_cluster_conjunto", "ep_mle", "ep_cluster_candidato", "ic95_inf", "ic95_sup",
            "li95_unilateral", "p_unilateral", "p_unilateral_t_g_menos_1", "p_unilateral_mle",
            "p_unilateral_cluster_candidato", "ic95_fieller_inf", "ic95_fieller_sup", "li95_unilateral_fieller",
            "p_holm", "q_bky", "n_candidatos", "g_conjuntos"]


def portao(v: dict, e9_est: pd.DataFrame, e9_efe: pd.DataFrame, p1_est: pd.DataFrame, p1_dap: pd.DataFrame,
           p1h: pd.DataFrame, tol: float = TOL_REPRODUCAO) -> dict:
    """Versão antiga contra os CSV gravados; uma linha do portão por especificação."""
    linhas, falha = [], None

    def registrar(nome: str, casou: bool, difs: dict, n: int, n_gravado: int) -> None:
        nonlocal falha
        passou = bool(casou and n == n_gravado and n > 0 and all(x <= tol for x in difs.values()))
        linhas.append({"linha": nome, "linhas_reestimadas": n, "linhas_gravadas": n_gravado,
                       "todas_casadas": bool(casou and n == n_gravado),
                       **{f"dif_max_{k}": x for k, x in difs.items()}, "passou": passou})
        if not passou and falha is None:
            falha = f"FALHA_REPRODUCAO_{nome}"

    for chave, ciclo in (("E9s_2", "2"), ("E9s_emp", EMPILHADO)):
        sel_g = (e9_est["ciclo"] == ciclo) & (e9_est["modelo"] == MOD_E9) & (e9_est["conjunto"] == "sensibilidade") & \
                (e9_est["especificacao"] == ESPEC_E9)
        n = v["e9_est"][v["e9_est"]["ciclo"] == ciclo]
        casou, difs, k = comparar(n, e9_est[sel_g], ["ciclo", "conjunto", "modelo", "especificacao", "termo"], COLS_E9)
        sel_f = (e9_efe["ciclo"] == ciclo) & (e9_efe["modelo"] == MOD_E9) & (e9_efe["conjunto"] == "sensibilidade") & \
                (e9_efe["especificacao"] == ESPEC_E9)
        nf = v["e9_efe"][v["e9_efe"]["ciclo"] == ciclo]
        casou_f, difs_f, kf = comparar(nf, e9_efe[sel_f], ["ciclo", "conjunto", "modelo", "especificacao", "termo",
                                                           "quantidade"], COLS_E9_EFE)
        difs.update({f"efeitos_{c}": x for c, x in difs_f.items()})
        registrar(chave, casou and casou_f and kf == int(sel_f.sum()), difs, k, int(sel_g.sum()))
    p1 = v["p1"]
    for chave, modelo, ciclo in (("M1", "M1", EMPILHADO), ("M2", "M2", EMPILHADO), ("M4", "M4", EMPILHADO),
                                 ("M5_1", "M5", "1"), ("M5_2", "M5", "2"), ("M5_3", "M5", "3"),
                                 ("P1d", "M5", "1,2,3"), ("M6_nota", "M6_nota", EMPILHADO),
                                 ("M6_municipio", "M6_municipio", EMPILHADO), ("M6_curso", "M6_curso", EMPILHADO),
                                 ("M7", "M7", EMPILHADO), ("M8", "M8", EMPILHADO), ("M9", "M9", EMPILHADO)):
        n = p1[(p1["modelo"] == modelo) & (p1["ciclo"].astype(str) == ciclo)]
        g = p1_est[(p1_est["modelo"] == modelo) & (p1_est["ciclo"] == ciclo)]
        casou, difs, k = comparar(n, g, ["modelo", "ciclo", "tipo_linha", "termo"], COLS_P1)
        registrar(f"P1_{chave}", casou, difs, k, int(len(g)))
    for chave, modelo, ciclo in (("M1", "M1", EMPILHADO), ("M4", "M4", EMPILHADO), ("M7", "M7", EMPILHADO),
                                 ("M5_2", "M5", "2")):
        n = v["dap"][(v["dap"]["modelo"] == modelo) & (v["dap"]["ciclo"].astype(str) == ciclo)]
        g = p1_dap[(p1_dap["modelo"] == modelo) & (p1_dap["ciclo"] == ciclo)]
        casou, difs, k = comparar(n, g, ["modelo", "ciclo", "atributo"], COLS_DAP)
        registrar(f"DAP_{chave}", casou, difs, k, int(len(g)))
    h = v["p1h"]
    for id_linha, modelo, ciclo, comp in (("P1h-1", "M1", EMPILHADO, "D_UF"), ("P1h-2a", "M1", EMPILHADO, "K5"),
                                          ("P1h-2b", "M1", EMPILHADO, "K10"), ("P1h-3", "M2", EMPILHADO, "D_UF"),
                                          ("P1h-3", "M4", EMPILHADO, "D_UF"), ("P1h-3", "M5", "1", "D_UF"),
                                          ("P1h-3", "M5", "2", "D_UF"), ("P1h-3", "M5", "3", "D_UF"),
                                          ("P1h-3", "M7", EMPILHADO, "D_UF")):
        n = h[(h["id_linha"] == id_linha) & (h["modelo"] == modelo) & (h["ciclo"].astype(str) == ciclo)]
        g = p1h[(p1h["id_linha"] == id_linha) & (p1h["modelo"] == modelo) & (p1h["ciclo"] == ciclo) &
                (p1h["componente"] == comp)]
        casou, difs, k = comparar(n, g, ["id_linha", "modelo", "ciclo", "componente"], COLS_P1H)
        nome = f"P1h_{id_linha}_{modelo}" + ("" if ciclo == EMPILHADO else f"_{ciclo}")
        registrar(nome, casou, difs, k, int(len(g)))
    return {"status": "PASSOU" if falha is None else falha, "tolerancia": tol,
            "regra": ("versão antiga (tipo de vaga do ciclo 2 pelo quadro de 19/03) reestimada com as funções dos scripts "
                      "16, 25 e 25c contra E9_estimativas.csv e E9_efeitos_marginais.csv (E9 no conjunto só com vaga "
                      "imediata, especificação principal, ciclo 2 e empilhado), P1_estimativas.csv (todas as linhas do "
                      "M1, M2, M4, M5 por ciclo, Wald do P1d, M6 da nota, do município e do curso, M7, M8 e M9, com "
                      "p de Holm e q BKY), P1_dap.csv (M1 com bootstrap, M4, M7, M5 do ciclo 2) e P1h_magnitudes.csv "
                      "(P1h-1, K5, K10 e as seis linhas P1h-3, com q BKY); diferença absoluta ≤ 1e−8 se o valor "
                      "gravado tem módulo ≤ 1, relativa ≤ 1e−8 se maior (os CSV têm 10 algarismos significativos); "
                      "NaN só casa com NaN"),
            "linhas": linhas}


# ---------------------------------------------------------------------------
# Linhas de saída (esquema VD)
# ---------------------------------------------------------------------------

def _base(**kw) -> dict:
    b = {c: np.nan for c in COLUNAS}
    b.update({"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "inferencia_cluster_degenerada": False,
              "entra_bky": False, "familia_bky": "", "status": "EXECUTADO", "nota": ""})
    b.update(kw)
    return b


def id_vd(bloco: str, chave: str, tipo: str) -> str:
    if bloco == "E9":
        return "VD-1" if chave == "E9s_2" else "VD-2"
    if bloco == "P1":
        return "VD-3" if chave in VD3 else "apoio"
    if bloco == "DAP":
        return "VD-4"
    if tipo == "km_equivalentes" or chave in DUF_VD4:
        return "VD-4"
    return "apoio"


def _chave_p1(modelo: str, ciclo: str) -> str:
    if modelo == "M5":
        return "P1d" if ciclo == "1,2,3" else f"M5_{ciclo}"
    return modelo


def linhas_vd(versao: str, v: dict) -> list[dict]:
    out = []
    comum = {"versao": versao, "versao_quadro_ciclo2": QUADRO_DA_VERSAO[versao]}
    # E9 (VD-1, VD-2)
    for r in v["e9_est"].itertuples(index=False):
        chave = "E9s_2" if str(r.ciclo) == "2" else "E9s_emp"
        out.append(_base(**comum, id_vd=id_vd("E9", chave, "coeficiente"), bloco="E9", chave_modelo=chave,
                         modelo="E9 só vaga imediata", ciclo=str(r.ciclo), tipo_linha="coeficiente", termo=r.termo,
                         estimativa=r.coef, ep_cluster_conjunto=r.ep_cluster_conjunto, ep_mle=r.ep_mle,
                         ep_cluster_candidato=r.ep_cluster_candidato, ic95_inf=r.ic95_inf, ic95_sup=r.ic95_sup, p=r.p,
                         p_t_g_menos_1=r.p_t_g_menos_1, g_conjuntos=r.g_conjuntos, g_candidatos=r.g_candidatos,
                         n_candidatos=r.n_candidatos, n_alternativas_ou_linhas=r.n_alternativas,
                         n_conjuntos=r.n_conjuntos,
                         nota=P1._juntar(r.nota, "E9 secundário e exploratório (protocolo 40, §12): sem correção "
                                                 "múltipla" if r.termo == B else "")))
    for r in v["e9_efe"].itertuples(index=False):
        if r.termo != B or r.quantidade not in ("razao_chances_por_5mil", "variacao_prob_media_pp"):
            continue
        chave = "E9s_2" if str(r.ciclo) == "2" else "E9s_emp"
        c = v["e9_est"][(v["e9_est"]["ciclo"].astype(str) == str(r.ciclo)) & (v["e9_est"]["termo"] == B)].iloc[0]
        out.append(_base(**comum, id_vd=id_vd("E9", chave, r.quantidade), bloco="E9", chave_modelo=chave,
                         modelo="E9 só vaga imediata", ciclo=str(r.ciclo), tipo_linha=r.quantidade, termo=B,
                         estimativa=r.estimativa, ep_cluster_conjunto=r.ep_cluster_conjunto, ep_mle=r.ep_mle,
                         ic95_inf=r.ic95_inf, ic95_sup=r.ic95_sup,
                         p=c["p"] if r.quantidade == "razao_chances_por_5mil" else np.nan,
                         g_conjuntos=c["g_conjuntos"], n_candidatos=c["n_candidatos"],
                         n_alternativas_ou_linhas=c["n_alternativas"], n_conjuntos=c["n_conjuntos"],
                         nota=("exp(5·coef.), IC = exp do IC do log (função linhas_efeitos do script 16); p = o do "
                               "coeficiente da bolsa" if r.quantidade == "razao_chances_por_5mil" else
                               "variação média da probabilidade de escolha (p.p.) por +R$ 5 mil, delta (script 16)")))
    # P1 (VD-3 e apoio)
    for r in v["p1"].itertuples(index=False):
        ciclo = str(r.ciclo)
        chave = _chave_p1(r.modelo, ciclo)
        fam = FAMILIA_P1 if _verdadeiro(r.entra_bky) else ""
        out.append(_base(**comum, id_vd=id_vd("P1", chave, r.tipo_linha), bloco="P1", chave_modelo=chave,
                         modelo=r.modelo, ciclo=ciclo, tipo_linha=r.tipo_linha, termo=r.termo, estimativa=r.coef,
                         ep_cluster_conjunto=r.ep_cluster_conjunto, ep_mle=r.ep_mle,
                         ep_cluster_candidato=r.ep_cluster_candidato, ic95_inf=r.ic95_inf, ic95_sup=r.ic95_sup, p=r.p,
                         p_t_g_menos_1=r.p_t_g_menos_1, p_mle=r.p_mle, estatistica_wald=r.estatistica_wald, gl=r.gl,
                         inferencia_cluster_degenerada=bool(_verdadeiro(r.inferencia_cluster_degenerada)),
                         entra_bky=bool(_verdadeiro(r.entra_bky)), familia_bky=fam, q_bky=r.q_bky,
                         g_conjuntos=r.g_conjuntos, g_candidatos=r.g_candidatos, n_candidatos=r.n_candidatos,
                         n_alternativas_ou_linhas=r.n_linhas_candidato_celula, n_conjuntos=r.n_conjuntos,
                         status=r.status, nota=r.nota if isinstance(r.nota, str) else ""))
        termo_rc = TERMO_RC.get(chave, B)
        if chave in VD3_BETA and r.tipo_linha == "coeficiente" and r.termo == termo_rc:
            nota_rc = ("exp(5·coef.), IC = exp do IC do log, EP pelo delta (como no script 42); p = o do coeficiente"
                       + ("; média da bolsa no logit misto" if chave == "M8" else "")
                       + ("; peso na escala do logit aninhado" if chave == "M9" else ""))
            rc = {}
            if pd.notna(r.coef) and pd.notna(r.ep_cluster_conjunto):
                b, e = float(r.coef), float(r.ep_cluster_conjunto)
                orr = math.exp(PASSO_BOLSA * b)
                rc = {"estimativa": orr, "ep_cluster_conjunto": orr * PASSO_BOLSA * e,
                      "ep_mle": orr * PASSO_BOLSA * float(r.ep_mle),
                      "ep_cluster_candidato": orr * PASSO_BOLSA * float(r.ep_cluster_candidato),
                      "ic95_inf": math.exp(PASSO_BOLSA * (b - Z95 * e)),
                      "ic95_sup": math.exp(PASSO_BOLSA * (b + Z95 * e)), "p": r.p}
            else:
                nota_rc = P1._juntar(nota_rc, r.nota if isinstance(r.nota, str) else "")
            out.append(_base(**comum, id_vd="VD-3", bloco="P1", chave_modelo=chave, modelo=r.modelo, ciclo=ciclo,
                             tipo_linha="razao_chances_por_5mil", termo=r.termo, **rc, g_conjuntos=r.g_conjuntos,
                             n_candidatos=r.n_candidatos, n_alternativas_ou_linhas=r.n_linhas_candidato_celula,
                             n_conjuntos=r.n_conjuntos, status=r.status, nota=nota_rc))
    # DAP (VD-4)
    for r in v["dap"].itertuples(index=False):
        chave = _chave_p1(r.modelo, str(r.ciclo))
        out.append(_base(**comum, id_vd="VD-4", bloco="DAP", chave_modelo=chave, modelo=r.modelo, ciclo=str(r.ciclo),
                         tipo_linha="dap", termo=r.atributo, estimativa=r.dap, ep_cluster_conjunto=r.ep_delta,
                         ic95_inf=r.ic95_delta_inf, ic95_sup=r.ic95_delta_sup, ic95_boot_inf=r.ic95_boot_inf,
                         ic95_boot_sup=r.ic95_boot_sup, g_conjuntos=r.g_conjuntos, n_candidatos=r.n_candidatos,
                         status=r.status, nota=P1._juntar(f"R$ mil por mês; {r.formula}", r.nota)))
    # P1h (VD-4 e apoio)
    for r in v["p1h"].itertuples(index=False):
        chave = _chave_p1(r.modelo, str(r.ciclo))
        tipo = "D_UF" if r.componente == "D_UF" else "km_equivalentes"
        fam = FAMILIA_P1H3 if r.id_linha == "P1h-3" else ""
        out.append(_base(**comum, id_vd=id_vd("P1h", chave, tipo), bloco="P1h", chave_modelo=chave, modelo=r.modelo,
                         ciclo=str(r.ciclo), tipo_linha=tipo, termo=r.componente, estimativa=r.estimativa,
                         ep_cluster_conjunto=r.ep_cluster_conjunto, ep_mle=r.ep_mle,
                         ep_cluster_candidato=r.ep_cluster_candidato, ic95_inf=r.ic95_inf, ic95_sup=r.ic95_sup,
                         li95_unilateral=r.li95_unilateral, p_unilateral=r.p_unilateral,
                         p_t_g_menos_1=r.p_unilateral_t_g_menos_1, ic95_fieller_inf=r.ic95_fieller_inf,
                         ic95_fieller_sup=r.ic95_fieller_sup, li95_unilateral_fieller=r.li95_unilateral_fieller,
                         entra_bky=fam != "", familia_bky=fam, q_bky=r.q_bky, g_conjuntos=r.g_conjuntos,
                         g_candidatos=r.g_candidatos, n_candidatos=r.n_candidatos,
                         n_alternativas_ou_linhas=r.n_linhas_candidato_celula, n_conjuntos=r.n_conjuntos,
                         nota=P1._juntar(f"{r.id_linha}", r.nota, "p_t_g_menos_1 aqui é o unilateral pela t")))
    return out


def montar(va: dict, vc: dict) -> pd.DataFrame:
    est = pd.DataFrame(linhas_vd(ANTIGA, va) + linhas_vd(CORRIGIDA, vc))[COLUNAS]
    for c in ("entra_bky", "inferencia_cluster_degenerada"):
        est[c] = est[c].astype(bool)
    return est


def conferir_mesma_amostra(va: dict, vc: dict) -> dict:
    """Mesmas linhas nas duas versões no P1; M5 dos ciclos 1 e 3 idêntico; amostra do E9 muda só no ciclo 2."""
    out = {}
    a, c = va["p1"], vc["p1"]
    for col in ("modelo", "ciclo", "tipo_linha", "termo", "n_candidatos", "n_linhas_candidato_celula", "n_conjuntos"):
        if not (a[col].fillna(-1).astype(str).to_numpy() == c[col].fillna(-1).astype(str).to_numpy()).all():
            raise FalhaValidacao(f"P1: coluna {col} difere entre as versões")
    for k in ("1", "3"):
        m = (a["modelo"] == "M5") & (a["ciclo"].astype(str) == k)
        d = float(np.max(np.abs(a.loc[m, "coef"].to_numpy() - c.loc[m, "coef"].to_numpy())))
        if d > 0:
            raise FalhaValidacao(f"M5 ciclo {k} mudou com a correção do ciclo 2 (dif. {d})")
        out[f"M5_{k}_dif_max_coef"] = d
    out["P1_linhas"] = int(len(a))
    e = {}
    for ver, v in ((ANTIGA, va), (CORRIGIDA, vc)):
        r = v["res_e9"]
        e[ver] = {k: {"n_candidatos": r[k]["n_candidatos"], "n_alternativas": r[k]["n_alternativas"],
                      "n_conjuntos": r[k]["n_conjuntos"], "omitidas": r[k]["omitidas"]} for k in r}
    out["E9_sensibilidade"] = e
    return out


def conferir_contra_vc(est: pd.DataFrame) -> dict:
    """M1 e M5 por ciclo saem iguais aos do VC_estimativas.csv (adendo 52c) nas duas versões."""
    vc = pd.read_csv(VC_CSV, dtype={"ciclo": str})
    out = {}
    for versao in VERSOES:
        for chave in ("M1", "M5_1", "M5_2", "M5_3"):
            a = est[(est["versao"] == versao) & (est["chave_modelo"] == chave) & (est["tipo_linha"] == "coeficiente")]
            g = vc[(vc["versao"] == versao) & (vc["chave_modelo"] == chave) & (vc["tipo_linha"] == "coeficiente")]
            if list(a["termo"]) != list(g["termo"]):
                raise FalhaValidacao(f"{chave} ({versao}): termos diferentes do VC")
            d = max(_dif_rel(a[c].to_numpy(dtype=float), g[c].to_numpy(dtype=float))
                    for c in ("estimativa", "ep_cluster_conjunto", "ep_mle", "ep_cluster_candidato"))
            if d > TOL_REPRODUCAO:
                raise FalhaValidacao(f"{chave} ({versao}) difere do VC_estimativas.csv ({d})")
            out[f"{versao}:{chave}"] = d
    return out


# ---------------------------------------------------------------------------
# Leitura (regras fixadas antes de rodar a versão corrigida; ver DECISOES)
# ---------------------------------------------------------------------------

def _sel(est: pd.DataFrame, versao: str, chave: str, tipo: str, termo: str | None = None) -> pd.Series:
    s = est[(est["versao"] == versao) & (est["chave_modelo"] == chave) & (est["tipo_linha"] == tipo)]
    if termo is not None:
        s = s[s["termo"] == termo]
    if len(s) != 1:
        raise FalhaValidacao(f"esperava 1 linha {versao} {chave} {tipo} {termo}, achei {len(s)}")
    return s.iloc[0]


def _exclui(r: pd.Series, nulo: float) -> bool | None:
    if pd.isna(r["ic95_inf"]) or pd.isna(r["ic95_sup"]):
        return None
    return bool(r["ic95_inf"] > nulo or r["ic95_sup"] < nulo)


def _sinal(x: float, nulo: float = 0.0) -> int:
    if pd.isna(x):
        return 0
    return int(np.sign(math.log(x) if nulo == 1.0 else x))


def criterio(r: pd.Series) -> tuple[str, bool | None]:
    """Critério de significância de cada linha (DECISOES, item 'Leitura do §3 por regra')."""
    if _verdadeiro(r["entra_bky"]):
        return "q BKY < 0,05", (None if pd.isna(r["q_bky"]) else bool(r["q_bky"] < ALFA))
    if r["chave_modelo"] == "M6_curso" and r["tipo_linha"] != "coeficiente_controle":
        return "p MV < 0,05", (None if pd.isna(r["p_mle"]) else bool(r["p_mle"] < ALFA))
    if r["tipo_linha"] == "wald_igualdade":
        return "p < 0,05", (None if pd.isna(r["p"]) else bool(r["p"] < ALFA))
    if r["tipo_linha"] == "razao_chances_por_5mil":
        return "IC 95% exclui 1", _exclui(r, 1.0)
    if r["tipo_linha"] in ("dap", "km_equivalentes"):
        return "IC 95% delta exclui 0", _exclui(r, 0.0)
    return "IC 95% exclui 0", _exclui(r, 0.0)


def linhas_de_leitura(est: pd.DataFrame) -> list[tuple[str, str, str, str]]:
    """(id_vd, chave, tipo_linha, termo) das quantidades lidas no §3 e na tabela de mudanças."""
    a = est[est["versao"] == ANTIGA]
    out = [("VD-1", "E9s_2", "razao_chances_por_5mil", B), ("VD-2", "E9s_emp", "razao_chances_por_5mil", B)]
    for chave in VD3_BETA:
        out.append(("VD-3", chave, "razao_chances_por_5mil", TERMO_RC.get(chave, B)))
    for chave in ("M6_nota", "M6_municipio", "M6_curso"):
        s = a[(a["chave_modelo"] == chave) & a["tipo_linha"].isin(["inclinacao_do_grupo", "interacao", "wald_igualdade"])]
        out += [("VD-3", chave, t, termo) for t, termo in zip(s["tipo_linha"], s["termo"])]
    out += [("VD-3", "M8", "coeficiente", f"desvio_{B}"), ("VD-3", "M8", "coeficiente", f"desvio_{P1.TERMO_DIST}"),
            ("VD-3", "M9", "teste_lambda_igual_1", "lambda_menos_1")]
    out += [("apoio", f"M5_{k}", "coeficiente", B) for k in P1.CICLOS]
    out += [("apoio", "P1d", "wald_igualdade_ciclos", "wald_bolsa_igual_entre_ciclos")]
    for chave in DAP_VD4:
        out += [("VD-4", chave, "dap", at) for at in P1.DAP_DEF]
    out += [("VD-4", "M1", "km_equivalentes", "K5"), ("VD-4", "M1", "km_equivalentes", "K10")]
    out += [("VD-4", chave, "D_UF", "D_UF") for chave in DUF_VD4]
    out += [("apoio", f"M5_{k}", "D_UF", "D_UF") for k in P1.CICLOS]
    return out


def mudancas(est: pd.DataFrame) -> list[dict]:
    out = []
    for vd, chave, tipo, termo in linhas_de_leitura(est):
        a, c = _sel(est, ANTIGA, chave, tipo, termo), _sel(est, CORRIGIDA, chave, tipo, termo)
        crit, sa = criterio(a)
        _, sc = criterio(c)
        nulo = 1.0 if tipo == "razao_chances_por_5mil" else 0.0
        sem_sinal = termo.startswith("desvio_") or tipo.startswith("wald")
        ga, gc = (0, 0) if sem_sinal else (_sinal(a["estimativa"], nulo), _sinal(c["estimativa"], nulo))
        boot = {}
        if tipo == "dap" and chave == "M1":
            ea = _exclui(pd.Series({"ic95_inf": a["ic95_boot_inf"], "ic95_sup": a["ic95_boot_sup"]}), 0.0)
            ec = _exclui(pd.Series({"ic95_inf": c["ic95_boot_inf"], "ic95_sup": c["ic95_boot_sup"]}), 0.0)
            boot = {"bootstrap_exclui_0_antiga": ea, "bootstrap_exclui_0_corrigida": ec,
                    "muda_significancia_bootstrap": bool(ea != ec)}
        out.append({"id_vd": vd, "chave_modelo": chave, "tipo_linha": tipo, "termo": termo,
                    "estimativa_antiga": float(a["estimativa"]), "estimativa_corrigida": float(c["estimativa"]),
                    "criterio": crit, "significativa_antiga": sa, "significativa_corrigida": sc,
                    "muda_sinal": bool(ga != gc and ga != 0 and gc != 0),
                    "muda_significancia": bool(sa is not None and sc is not None and sa != sc), **boot})
    return out


def regra_vd1(a: pd.Series, c: pd.Series) -> str:
    """§3 do adendo: mesmo sinal e IC corrigido que exclui 1 → mantém; IC corrigido que contém 1 → dependia do quadro
    pós-resultado; IC que exclui 1 do outro lado não está no §3 (só relatado)."""
    if not _exclui(c, 1.0):
        return "DEPENDIA_DO_QUADRO_POS_RESULTADO"
    if _sinal(a["estimativa"], 1.0) == _sinal(c["estimativa"], 1.0):
        return "MANTEM"
    return "SINAL_OPOSTO"


def leitura(est: pd.DataFrame) -> dict:
    a = _sel(est, ANTIGA, "E9s_2", "razao_chances_por_5mil")
    c = _sel(est, CORRIGIDA, "E9s_2", "razao_chances_por_5mil")
    exc_c = _exclui(c, 1.0)
    mesmo_sinal = _sinal(a["estimativa"], 1.0) == _sinal(c["estimativa"], 1.0)
    vd1 = regra_vd1(a, c)
    mud = mudancas(est)
    var_sinal = {}
    for chave in VD3:
        linhas = [m for m in mud if m["chave_modelo"] == chave and m["id_vd"] == "VD-3" and
                  (m["tipo_linha"] in ("razao_chances_por_5mil", "inclinacao_do_grupo", "interacao"))]
        var_sinal[chave] = any(m["muda_sinal"] for m in linhas)
    return {"VD1": {"regra": vd1, "ic_antigo_exclui_1": _exclui(a, 1.0), "ic_corrigido_exclui_1": exc_c,
                    "mesmo_sinal": bool(mesmo_sinal)},
            "VD2": {"ic_antigo_exclui_1": _exclui(_sel(est, ANTIGA, "E9s_emp", "razao_chances_por_5mil"), 1.0),
                    "ic_corrigido_exclui_1": _exclui(_sel(est, CORRIGIDA, "E9s_emp", "razao_chances_por_5mil"), 1.0)},
            "VD3": {"variante_muda_sinal": var_sinal,
                    "mudam_sinal": [k for k in VD3 if var_sinal[k]],
                    "nao_mudam_sinal_base_da_H2": [k for k in VD3 if not var_sinal[k]]},
            "linhas_que_mudam_sinal": [f"{m['chave_modelo']}:{m['tipo_linha']}:{m['termo']}" for m in mud
                                       if m["muda_sinal"]],
            "linhas_que_mudam_significancia": [f"{m['chave_modelo']}:{m['tipo_linha']}:{m['termo']}" for m in mud
                                               if m["muda_significancia"] or m.get("muda_significancia_bootstrap")]}


# ---------------------------------------------------------------------------
# Figura
# ---------------------------------------------------------------------------

def _plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 12})
    return plt


COR = {ANTIGA: "#8a8984", CORRIGIDA: "#2a78d6"}


def titulo_figura(lei: dict) -> str:
    return {"MANTEM": "Com o tipo de vaga da inscrição, a bolsa continua deslocando a 1ª opção no ciclo 2",
            "DEPENDIA_DO_QUADRO_POS_RESULTADO": "Com o tipo de vaga da inscrição, o sinal do ciclo 2 no conjunto só "
                                                "com vaga imediata perde a precisão",
            "SINAL_OPOSTO": "Com o tipo de vaga da inscrição, o sinal do ciclo 2 se inverte"}[lei["VD1"]["regra"]]


def figura(est: pd.DataFrame, lei: dict) -> dict:
    plt = _plt()
    DIR_FIG.mkdir(parents=True, exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14.0, 7.0), gridspec_kw={"width_ratios": [1.35, 1.0]})
    paineis = [(ax1, ["E9s_2", "E9s_emp", "M2", "M4", "M7", "M8", "M9"], "razao_chances_por_5mil",
                "razão de chances por +R$ 5 mil (escala log), IC 95%", 1.0, True),
               (ax2, list(DUF_VD4), "D_UF", "D_UF = θ_UF − 10·β (log-chance), IC 95%", 0.0, False)]
    for ax, chaves, tipo, xlab, ref, logx in paineis:
        y0 = np.arange(len(chaves))[::-1].astype(float)
        sub = est[(est["tipo_linha"] == tipo) & est["chave_modelo"].isin(chaves)]
        for yi, chave in zip(y0, chaves):
            for v, dy in ((ANTIGA, 0.17), (CORRIGIDA, -0.17)):
                r = _sel(est, v, chave, tipo)
                if pd.isna(r["estimativa"]):
                    continue
                ax.plot([r["ic95_inf"], r["ic95_sup"]], [yi + dy] * 2, color=COR[v], lw=2.4, solid_capstyle="round")
                ax.plot([r["estimativa"]], [yi + dy], "o", ms=9, zorder=3,
                        mfc="white" if v == ANTIGA else COR[v], mec=COR[v], mew=2.0)
                ax.text(r["ic95_sup"] * (1.04 if logx else 1.0) + (0 if logx else 0.06), yi + dy,
                        _n(r["estimativa"], 2), va="center", ha="left", fontsize=10.5, color="#2b2b29")
        ax.axvline(ref, color="#52514e", lw=1.0)
        ax.set_yticks(y0)
        ax.set_yticklabels([ROTULO[k] for k in chaves], fontsize=11.5)
        ax.set_xlabel(xlab, fontsize=11.5)
        if logx:
            ax.set_xscale("log")
            ticks = [0.6, 0.8, 1.0, 1.5, 2.0, 3.0]
            ax.set_xticks(ticks)
            ax.set_xticklabels([_n(t, 1) for t in ticks])
            ax.minorticks_off()
            lo = min(0.55, float(sub["ic95_inf"].min()) * 0.95)
            hi = max(3.2, float(sub["ic95_sup"].max()) * 1.35)
            ax.set_xlim(lo, hi)
        else:
            ax.set_xlim(min(-0.2, float(sub["ic95_inf"].min()) - 0.2), float(sub["ic95_sup"].max()) + 0.7)
            from matplotlib.ticker import FuncFormatter
            ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: _n(x, 1)))
            ax.set_ylim(-0.6, len(chaves) - 0.4)
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
        ax.tick_params(axis="y", length=0)
        ax.grid(axis="x", color="#e6e5e0", lw=0.6)
        ax.set_axisbelow(True)
    from matplotlib.lines import Line2D
    leg = [Line2D([0], [0], marker="o", color=COR[ANTIGA], mfc="white", mec=COR[ANTIGA], mew=2, lw=2.4,
                  label="antiga: tipo de vaga do ciclo 2 pelo quadro de 19/03/2026 (pós-resultado)"),
           Line2D([0], [0], marker="o", color=COR[CORRIGIDA], mfc=COR[CORRIGIDA], mec=COR[CORRIGIDA], lw=2.4,
                  label="corrigida: quadro de 13/02/2026 (vigente na inscrição)")]
    fig.legend(handles=leg, loc="upper left", bbox_to_anchor=(0.012, 0.915), ncol=2, frameon=False, fontsize=10.5)
    fig.text(0.012, 0.975, titulo_figura(lei), fontsize=15, ha="left", va="top", color="#1f1f1d")
    fig.text(0.012, 0.02, "Escolha da 1ª opção, condicional a se candidatar; IC 95% com cluster por conjunto de escolha "
             "(curso × ciclo). Bolsa: pacote do corte; origem: preferência revelada, não efeito causal.",
             fontsize=9.5, color="#52514e", ha="left", va="bottom")
    fig.subplots_adjust(left=0.20, right=0.985, top=0.82, bottom=0.15, wspace=0.62)
    fig.savefig(FIG, dpi=150, metadata={"Software": None})
    plt.close(fig)
    return {"arquivo": rel(FIG), "sha256": sha256(FIG), "titulo": titulo_figura(lei), "como_ler": COMO_LER}


# ---------------------------------------------------------------------------
# Documento 57v
# ---------------------------------------------------------------------------

def bloco(nome: str, corpo: str) -> list[str]:
    return [f"<!-- VD:{nome}:inicio -->", corpo, f"<!-- VD:{nome}:fim -->"]


def _sci(v) -> str:
    return "—" if v is None else f"{v:.1e}".replace(".", ",").replace("-", "−")


def _data_br(iso: str) -> str:
    a, m, d = iso.split("-")
    return f"{d}/{m}/{a}"


def _sim(v) -> str:
    return "—" if v is None else ("sim" if v else "não")


def texto_decisoes() -> str:
    t = ["Decisões de implementação onde o adendo não fixava o detalhe. Foram registradas e commitadas antes de "
         "qualquer estimativa deste adendo (o histórico do Git mostra o commit do bloco antes do commit dos números). "
         "Nenhuma muda a amostra, o conjunto de escolha principal ou a especificação dos modelos de origem.", ""]
    for i, d in enumerate(DECISOES, 1):
        t.append(f"{i}. **{d['item']}** ({_data_br(d['data'])}). {d['situacao']} *Resolução:* {d['resolucao']}")
    return "\n".join(t)


def texto_inventario() -> str:
    linhas = [list(x) for x in INVENTARIO]
    return "\n".join([
        "Lido do código dos scripts 16, 25 e 25c, antes de qualquer estimativa. \"Usa\" quer dizer que a linha depende "
        "de `tem_vaga_imediata`, `log_vagas_imediatas_mais_1` ou da definição do conjunto \"só células com vaga "
        "imediata\" no ciclo 2. As linhas que não usam não precisam ser refeitas e não são.", "",
        _tab(["Linha (origem)", "Usa o tipo de vaga do ciclo 2?", "Por onde", "Neste adendo"], linhas), "",
        FORA_DO_ADENDO])


def texto_portao(resumo: dict) -> str:
    p = resumo["portao"]
    linhas = []
    for e in p["linhas"]:
        difs = {k[len("dif_max_"):]: v for k, v in e.items() if k.startswith("dif_max_")}
        linhas.append([e["linha"], f"{e['linhas_reestimadas']} / {e['linhas_gravadas']}",
                       _sci(max(difs.values())) if difs else "—", "passou" if e["passou"] else "**falhou**"])
    t = [f"**Portão de reprodução (VD-5): {p['status']}.** Com o tipo de vaga antigo, as funções originais (scripts 16, "
         "25 e 25c, importadas sem alteração pelo 42) reproduzem as linhas gravadas em `E9_estimativas.csv`, "
         "`E9_efeitos_marginais.csv`, `P1_estimativas.csv`, `P1_dap.csv` e `P1h_magnitudes.csv`. A diferença é "
         "absoluta quando o valor gravado tem módulo até 1 e relativa acima disso (decisão 6); a coluna mostra a maior "
         "diferença entre todas as quantidades comparadas da linha (a lista completa está em `portao` de "
         "`VD_resumo.json`).", "",
         _tab(["Linha", "Linhas (reestimadas / gravadas)", "Dif. máx.", "Portão"], linhas)]
    if p["status"] != "PASSOU":
        t += ["", f"A execução parou em `{p['status']}`: nada foi corrigido (adendo 52d, §4)."]
    return "\n".join(t)


def texto_correcao(resumo: dict) -> str:
    cv = resumo["correcao"]
    s = cv["sensibilidade_ciclo2"]
    cc = resumo["conferencias"]["marca_dos_candidatos"]
    am = resumo["mesma_amostra"]["E9_sensibilidade"]
    linhas = [
        ["células do ciclo 2 no conjunto só com vaga imediata", _int(s["celulas_19mar"]), _int(s["celulas_13fev"])],
        ["vagas imediatas somadas nessas células", _n(s["vagas_imediatas_19mar"], 0), _n(s["vagas_imediatas_13fev"], 0)],
        ["1ªs opções do ciclo 2 em célula com vaga imediata",
         f"{cc['primeiras_opcoes_com_vaga_imediata_19mar']} de {cc['primeiras_opcoes_ciclo2']}",
         f"{cc['primeiras_opcoes_com_vaga_imediata_13fev']} de {cc['primeiras_opcoes_ciclo2']}"],
        ["candidatos no E9 só com vaga imediata, ciclo 2", _int(am[ANTIGA]["E9s_2"]["n_candidatos"]),
         _int(am[CORRIGIDA]["E9s_2"]["n_candidatos"])],
        ["células usadas no E9 só com vaga imediata, ciclo 2", _int(am[ANTIGA]["E9s_2"]["n_alternativas"]),
         _int(am[CORRIGIDA]["E9s_2"]["n_alternativas"])],
        ["candidatos no E9 só com vaga imediata, ciclos 1–3", _int(am[ANTIGA]["E9s_emp"]["n_candidatos"]),
         _int(am[CORRIGIDA]["E9s_emp"]["n_candidatos"])],
    ]
    cs = resumo["conferencias"]["sensibilidade_gravada_igual_a_regra"]
    ca = resumo["conferencias"]["quadro_1302_contra_a36"]
    return "\n".join([
        _tab(["Item", "Antiga (19/03/2026)", "Corrigida (13/02/2026)"], linhas), "",
        f"- Células do conjunto antigo que continuam no corrigido: {s['celulas_em_ambas']}; nenhuma célula entra no "
        "conjunto corrigido sem estar no antigo, porque nenhuma célula perdeu vaga imediata entre 13/02 e 19/03 "
        f"(adendo 52c: {resumo['correcao']['conjunto_principal_ciclo2']['celulas_com_imediata_em_13fev_e_reserva_em_19mar']} "
        "células nesse sentido).",
        f"- Conferências: a regra do script 12 aplicada ao quadro de 19/03 reproduz o conjunto gravado em "
        f"{cs['celulas']} células (diferença máxima 0 em todas as colunas) e a marca de vaga imediata de "
        f"{cc['marca_gravada_igual_ao_quadro_19mar']} de {cc['linhas_ciclo2']} linhas de escolha do ciclo 2; o quadro "
        f"de 13/02 bate com a leitura independente da auditoria 36 em {ca['celulas_comparadas']} células "
        f"({ca['celulas_com_vagas_imediatas_diferentes']} diferenças). Nada imputado.",
        "- No P1, a correção é a mesma do adendo 52c (conjunto principal, só as covariáveis do ciclo 2); a amostra, os "
        "conjuntos e os termos são iguais nas duas versões (conferido), e o M1 e o M5 batem com o `VC_estimativas.csv`."])


def _coef(r: pd.Series, casas: int = 4) -> str:
    if pd.isna(r["estimativa"]):
        return f"— ({r['status']})"
    return f"{_n(r['estimativa'], casas)} {_ic(r['ic95_inf'], r['ic95_sup'], casas)}; {_peq(r['p'])}"


def tabela_e9(est: pd.DataFrame) -> str:
    linhas = []
    for chave in ("E9s_2", "E9s_emp"):
        ca, cc = _sel(est, ANTIGA, chave, "coeficiente", B), _sel(est, CORRIGIDA, chave, "coeficiente", B)
        oa, oc = _sel(est, ANTIGA, chave, "razao_chances_por_5mil"), _sel(est, CORRIGIDA, chave, "razao_chances_por_5mil")
        pa, pc = _sel(est, ANTIGA, chave, "variacao_prob_media_pp"), _sel(est, CORRIGIDA, chave, "variacao_prob_media_pp")
        linhas.append([("VD-1: " if chave == "E9s_2" else "VD-2: ") + ROTULO[chave],
                       f"{_int(ca['n_candidatos'])} → {_int(cc['n_candidatos'])}",
                       _coef(ca), _coef(cc),
                       f"{_n(oa['estimativa'], 2)} {_ic(oa['ic95_inf'], oa['ic95_sup'], 2)}",
                       f"{_n(oc['estimativa'], 2)} {_ic(oc['ic95_inf'], oc['ic95_sup'], 2)}",
                       f"{_n(pa['estimativa'], 3)} → {_n(pc['estimativa'], 3)}"])
    lv = []
    for chave in ("E9s_2", "E9s_emp"):
        a = _sel(est, ANTIGA, chave, "coeficiente", "log_vagas_imediatas_mais_1")
        c = _sel(est, CORRIGIDA, chave, "coeficiente", "log_vagas_imediatas_mais_1")
        lv.append([ROTULO[chave], f"{_n(a['estimativa'], 3)} {_ic(a['ic95_inf'], a['ic95_sup'], 3)}",
                   f"{_n(c['estimativa'], 3)} {_ic(c['ic95_inf'], c['ic95_sup'], 3)}"])
    return "\n".join([
        "Logit condicional da 1ª opção, spline linear do IVS, bolsa linear (especificação principal do E9), no conjunto "
        "só com células de vaga imediata. Coeficiente por R$ 1 mil/mês, IC 95% e p com cluster por conjunto de "
        "escolha; razão de chances por +R$ 5 mil; variação média da probabilidade de escolha da célula (p.p.). Sem "
        "correção múltipla (E9 exploratório, protocolo 40, §12). Todos os termos estão em `VD_estimativas.csv`.", "",
        _tab(["Linha", "Candidatos (antiga → corrigida)", "Coef. antigo [IC]; p", "Coef. corrigido [IC]; p",
              "Razão de chances antiga [IC]", "Razão de chances corrigida [IC]", "Δ prob., p.p. (antiga → corrigida)"],
             linhas), "",
        "Peso de `log(vagas imediatas + 1)` no mesmo modelo (a outra covariável do tipo de vaga é constante neste "
        "conjunto e sai):", "",
        _tab(["Linha", "Antigo [IC]", "Corrigido [IC]"], lv)])


def tabela_p1(est: pd.DataFrame) -> str:
    linhas = []
    for chave in VD3_BETA:
        t = TERMO_RC.get(chave, B)
        ca, cc = _sel(est, ANTIGA, chave, "coeficiente", t), _sel(est, CORRIGIDA, chave, "coeficiente", t)
        oa, oc = _sel(est, ANTIGA, chave, "razao_chances_por_5mil"), _sel(est, CORRIGIDA, chave, "razao_chances_por_5mil")
        linhas.append([ROTULO[chave], _coef(ca), _coef(cc),
                       f"{_n(oa['estimativa'], 2)} {_ic(oa['ic95_inf'], oa['ic95_sup'], 2)}",
                       f"{_n(oc['estimativa'], 2)} {_ic(oc['ic95_inf'], oc['ic95_sup'], 2)}"])
    extra = []
    for chave, tipo, termo, rot in (("M8", "coeficiente", f"desvio_{B}", "M8: desvio da bolsa entre candidatos"),
                                    ("M8", "coeficiente", f"desvio_{P1.TERMO_DIST}", "M8: desvio da distância"),
                                    ("M9", "coeficiente", "lambda", "M9: lambda (1 = logit condicional)"),
                                    ("M9", "teste_lambda_igual_1", "lambda_menos_1", "M9: lambda − 1")):
        a, c = _sel(est, ANTIGA, chave, tipo, termo), _sel(est, CORRIGIDA, chave, tipo, termo)
        fmt = (lambda r: f"{_n(r['estimativa'], 3)}; EP {_n(r['ep_cluster_conjunto'], 3)}; {_peq(r['p'])}"
               + (f"; q BKY {_p(r['q_bky'])}" if pd.notna(r["q_bky"]) else "")) if termo.startswith("desvio") else \
              (lambda r: f"{_n(r['estimativa'], 3)} {_ic(r['ic95_inf'], r['ic95_sup'], 3)}")
        extra.append([rot, fmt(a) if pd.notna(a["estimativa"]) else "—", fmt(c) if pd.notna(c["estimativa"]) else
                      f"— ({c['status']})"])
    return "\n".join([
        "Coeficiente da bolsa por R$ 1 mil/mês (no M8, a média da bolsa entre candidatos), IC 95% e p com cluster por "
        "conjunto de escolha, e razão de chances por +R$ 5 mil (exp de 5 × coef.; no M9, na escala do logit "
        "aninhado). Todas as variantes são dos ciclos 1–3 empilhados, na amostra do P1. Sem Holm (só o M1 é a "
        "principal do P1a, já no adendo 52c); os β das variantes não entram no BKY, como no protocolo 52.", "",
        _tab(["Variante", "Coef. antigo [IC]; p", "Coef. corrigido [IC]; p", "Razão de chances antiga [IC]",
              "Razão de chances corrigida [IC]"], linhas), "",
        _tab(["Parâmetro", "Antigo", "Corrigido"], extra)])


def tabela_m6(est: pd.DataFrame) -> str:
    linhas = []
    a_all = est[(est["versao"] == ANTIGA) & est["chave_modelo"].isin(["M6_nota", "M6_municipio", "M6_curso"]) &
                est["tipo_linha"].isin(["inclinacao_do_grupo", "interacao", "wald_igualdade"])]
    for r in a_all.itertuples(index=False):
        a = _sel(est, ANTIGA, r.chave_modelo, r.tipo_linha, r.termo)
        c = _sel(est, CORRIGIDA, r.chave_modelo, r.tipo_linha, r.termo)
        crit, _ = criterio(a)

        def fmt(x: pd.Series) -> str:
            if x["tipo_linha"] == "wald_igualdade":
                s = f"χ² {_n(x['estatistica_wald'], 2)}; {_peq(x['p'])}"
                if x["chave_modelo"] == "M6_curso":
                    s += f"; p MV {_p(x['p_mle'])}"
            else:
                s = f"{_n(x['estimativa'], 4)} {_ic(x['ic95_inf'], x['ic95_sup'], 4)}; {_peq(x['p'])}"
                if x["chave_modelo"] == "M6_curso":
                    s += f"; p MV {_p(x['p_mle'])}"
            if pd.notna(x["q_bky"]):
                s += f"; q BKY {_p(x['q_bky'])}"
            return s
        linhas.append([ROTULO[r.chave_modelo], f"`{r.termo}`", fmt(a), fmt(c), crit])
    return "\n".join([
        "`bolsa_mil|grupo` é a inclinação da bolsa no grupo; `bolsa_x_grupo` é a diferença para o grupo de base. "
        "No M6 do curso o EP por cluster é degenerado (o termo de cada curso só varia nos conjuntos do curso), e vale o "
        "p de máxima verossimilhança (MV), como no P1; essas linhas ficam fora do BKY. A última coluna diz o critério "
        "de significância usado na seção 5.7.", "",
        _tab(["Modelo", "Termo", "Antigo", "Corrigido", "Critério"], linhas)])


def tabela_bky(est: pd.DataFrame) -> str:
    linhas = []
    fam = est[(est["versao"] == ANTIGA) & est["familia_bky"].isin([FAMILIA_P1, FAMILIA_P1H3])]
    for r in fam.itertuples(index=False):
        a = _sel(est, ANTIGA, r.chave_modelo, r.tipo_linha, r.termo)
        c = _sel(est, CORRIGIDA, r.chave_modelo, r.tipo_linha, r.termo)
        pa = a["p"] if r.bloco == "P1" else a["p_unilateral"]
        pc = c["p"] if r.bloco == "P1" else c["p_unilateral"]
        linhas.append([r.familia_bky, ROTULO.get(r.chave_modelo, r.chave_modelo), f"`{r.termo}`",
                       f"{_p(pa)} / {_p(a['q_bky'])}", f"{_p(pc)} / {_p(c['q_bky'])}",
                       f"{_sim(bool(a['q_bky'] < ALFA))} → {_sim(bool(c['q_bky'] < ALFA))}"])
    return "\n".join([
        "As duas famílias BKY dos protocolos de origem, refeitas com as linhas corrigidas (decisão 5). Na família do "
        "P1, p bilateral com cluster por conjunto; na P1h-3, p unilateral de H0: D_UF ≤ 0. q BKY = 0,001 é o piso da "
        "grade do algoritmo (Anderson, 2008).", "",
        _tab(["Família", "Linha", "Termo", "Antigo: p / q BKY", "Corrigido: p / q BKY", "q < 0,05 (antigo → corrigido)"],
             linhas)])


def tabela_dap(est: pd.DataFrame) -> str:
    linhas = []
    for chave in DAP_VD4:
        for at in P1.DAP_DEF:
            a, c = _sel(est, ANTIGA, chave, "dap", at), _sel(est, CORRIGIDA, chave, "dap", at)

            def fmt(x: pd.Series) -> str:
                s = f"{_n(x['estimativa'], 2)} {_ic(x['ic95_inf'], x['ic95_sup'], 2)}"
                if pd.notna(x["ic95_boot_inf"]):
                    s += f"; bootstrap {_ic(x['ic95_boot_inf'], x['ic95_boot_sup'], 2)}"
                return s
            linhas.append([ROTULO[chave], P1.ROTULO_DAP[at], fmt(a), fmt(c)])
    return "\n".join([
        "DAP em R$ mil por mês de bolsa equivalentes a um atributo da vaga (razão de coeficientes), IC 95% pelo método "
        "delta com cluster por conjunto; no M1, também o IC percentil do bootstrap de pares por conjunto (999 "
        "réplicas, mesma semente do P1). Descritiva, sem teste de zero, como no P1b e no P1c. Quando o coeficiente "
        "da bolsa é pequeno perto do seu erro, a razão fica instável e não é um preço.", "",
        _tab(["Modelo", "Atributo", "Antiga: DAP [IC delta]", "Corrigida: DAP [IC delta]"], linhas)])


def tabela_p1h(est: pd.DataFrame) -> str:
    linhas = []
    for termo in ("K5", "K10"):
        a, c = _sel(est, ANTIGA, "M1", "km_equivalentes", termo), _sel(est, CORRIGIDA, "M1", "km_equivalentes", termo)

        def fmt(x: pd.Series) -> str:
            return (f"{_n(x['estimativa'], 0)} km, delta {_ic(x['ic95_inf'], x['ic95_sup'], 0)}; Fieller "
                    f"{_ic(x['ic95_fieller_inf'], x['ic95_fieller_sup'], 0)}")
        linhas.append([f"P1h-2 ({termo})", "M1", fmt(a), fmt(c)])
    for chave in DUF_VD4 + ("M5_1", "M5_2", "M5_3"):
        a, c = _sel(est, ANTIGA, chave, "D_UF"), _sel(est, CORRIGIDA, chave, "D_UF")

        def fmt(x: pd.Series) -> str:
            return (f"{_n(x['estimativa'], 3)} {_ic(x['ic95_inf'], x['ic95_sup'], 3)}; LI "
                    f"{_n(x['li95_unilateral'], 3)}; q BKY {_p(x['q_bky'])}")
        linhas.append(["P1h-3 (D_UF)" + (" — apoio" if chave.startswith("M5") else ""), ROTULO[chave], fmt(a), fmt(c)])
    return "\n".join([
        "K5 e K10: km a menos de distância com o mesmo peso de um degrau (R$ 5 mil) e de toda a amplitude (R$ 10 mil) "
        "da bolsa no M1, IC pelo método delta e por Fieller (descritivos, como no P1h-2). D_UF = θ_UF − 10·β, IC 95% "
        "bilateral, limite inferior (LI) unilateral de 95% e q BKY da família P1h-3 refeita. As linhas do M5 são "
        "apoio (o ciclo 2 já estava no 52c; ciclos 1 e 3 não mudam) e entram só para refazer o BKY.", "",
        _tab(["Linha", "Modelo", "Antiga", "Corrigida"], linhas)])


def tabela_mudancas(resumo: dict) -> str:
    linhas = []
    for m in resumo["mudancas"]:
        if not (m["muda_sinal"] or m["muda_significancia"] or m.get("muda_significancia_bootstrap")):
            continue
        o_que = []
        if m["muda_sinal"]:
            o_que.append("sinal")
        if m["muda_significancia"]:
            o_que.append(f"significância ({m['criterio']}: {_sim(m['significativa_antiga'])} → "
                         f"{_sim(m['significativa_corrigida'])})")
        if m.get("muda_significancia_bootstrap"):
            o_que.append(f"IC do bootstrap exclui 0: {_sim(m['bootstrap_exclui_0_antiga'])} → "
                         f"{_sim(m['bootstrap_exclui_0_corrigida'])}")
        rot = P1.ROTULO_DAP.get(m["termo"], m["termo"]) if m["tipo_linha"] == "dap" else m["termo"]
        linhas.append([m["id_vd"], ROTULO.get(m["chave_modelo"], m["chave_modelo"]), m["tipo_linha"], f"`{rot}`",
                       f"{_n(m['estimativa_antiga'], 3)} → {_n(m['estimativa_corrigida'], 3)}", "; ".join(o_que)])
    n = len(resumo["mudancas"])
    if not linhas:
        return (f"Das {n} quantidades lidas (seções 5.1 a 5.6), nenhuma muda de sinal nem de significância pelo critério "
                "da decisão 8. A lista completa, com o critério de cada linha, está em `mudancas` de `VD_resumo.json`.")
    return "\n".join([
        f"Das {n} quantidades lidas (seções 5.1 a 5.6), só as abaixo mudam de sinal ou de significância pelo critério "
        "da decisão 8; a lista completa, com o critério de cada uma, está em `mudancas` de `VD_resumo.json`.", "",
        _tab(["Id", "Linha", "Tipo", "Termo", "Estimativa (antiga → corrigida)", "O que muda"], linhas)])


def texto_resposta(est: pd.DataFrame, resumo: dict) -> str:
    lei = resumo["leitura"]
    a1, c1 = _sel(est, ANTIGA, "E9s_2", "razao_chances_por_5mil"), _sel(est, CORRIGIDA, "E9s_2", "razao_chances_por_5mil")
    a2, c2 = _sel(est, ANTIGA, "E9s_emp", "razao_chances_por_5mil"), _sel(est, CORRIGIDA, "E9s_emp", "razao_chances_por_5mil")
    exc = {True: "exclui 1", False: "contém 1"}
    t = []
    frase1 = (f"No E9 do ciclo 2, no conjunto só com células de vaga imediata, a razão de chances da 1ª opção por "
              f"+R$ 5 mil de bolsa passa de {_n(a1['estimativa'], 2)} (IC 95% {_ic(a1['ic95_inf'], a1['ic95_sup'], 2)}) "
              f"para {_n(c1['estimativa'], 2)} (IC {_ic(c1['ic95_inf'], c1['ic95_sup'], 2)}); o IC corrigido "
              f"{exc[bool(lei['VD1']['ic_corrigido_exclui_1'])]}. Com o quadro de 13/02 o conjunto tem "
              f"{_int(c1['n_alternativas_ou_linhas'])} células usadas e {_int(c1['n_candidatos'])} candidatos, contra "
              f"{_int(a1['n_alternativas_ou_linhas'])} e {_int(a1['n_candidatos'])} na versão antiga.")
    regra = lei["VD1"]["regra"]
    if regra == "MANTEM":
        t.append("**VD-1 (principal deste adendo): a robustez do ciclo 2 (doc 44) se mantém com o tipo de vaga anterior "
                 f"à alocação.** {frase1} Pela leitura pré-registrada (§3), o mesmo sinal e o IC que exclui 1 mantêm a "
                 "frase do doc 44 nesta peça. Os placebos de corte, o score bootstrap e o spline cúbico do doc 42 não "
                 "foram refeitos no conjunto de sensibilidade (decisão 2).")
    elif regra == "DEPENDIA_DO_QUADRO_POS_RESULTADO":
        t.append("**VD-1 (principal deste adendo): a robustez do ciclo 2 dependia do quadro pós-resultado.** "
                 f"{frase1} Pela leitura pré-registrada (§3), o IC que contém 1 obriga a relatar e a rebaixar a frase do "
                 "doc 44 sobre a robustez do ciclo 2 nesta peça; a mudança no doc 44 é decisão do autor.")
    else:
        t.append(f"**VD-1 (principal deste adendo): sinal oposto.** {frase1} O IC corrigido exclui 1 do outro lado; "
                 "esse caso não está no §3 e é só relatado.")
    t.append(f"**VD-2 (E9 empilhado, mesmo conjunto).** A razão de chances vai de {_n(a2['estimativa'], 2)} "
             f"{_ic(a2['ic95_inf'], a2['ic95_sup'], 2)} para {_n(c2['estimativa'], 2)} "
             f"{_ic(c2['ic95_inf'], c2['ic95_sup'], 2)}; o IC {exc[bool(lei['VD2']['ic_antigo_exclui_1'])]} na antiga e "
             f"{exc[bool(lei['VD2']['ic_corrigido_exclui_1'])]} na corrigida. O empilhado continua sendo uma média de "
             "ciclos heterogêneos (doc 42).")
    rc = {k: (_sel(est, ANTIGA, k, "razao_chances_por_5mil"), _sel(est, CORRIGIDA, k, "razao_chances_por_5mil"))
          for k in VD3_BETA}
    lista = "; ".join(f"{ROTULO[k].replace('P1 ', '')}: {_n(a['estimativa'], 2)} → {_n(c['estimativa'], 2)}"
                      for k, (a, c) in rc.items())
    v3 = lei["VD3"]
    rot = lambda ks: ", ".join(ROTULO[k].replace("P1 ", "") for k in ks)  # noqa: E731
    if v3["mudam_sinal"]:
        frase3 = (f"Mudam de sinal em algum peso da bolsa: {rot(v3['mudam_sinal'])}. Pela leitura pré-registrada, a "
                  f"leitura da H2 se apoia nas que não mudam: {rot(v3['nao_mudam_sinal_base_da_H2'])}.")
    else:
        frase3 = ("Nenhuma variante muda o sinal de um peso da bolsa (β, média do M8, inclinações e interações do M6); "
                  "a leitura da H2 continua apoiada em todas elas.")
    mud_sig3 = [m for m in resumo["mudancas"] if m["id_vd"] == "VD-3" and m["muda_significancia"]]
    sig3 = ("Mudam de significância: " + "; ".join(f"{ROTULO.get(m['chave_modelo'])}, `{m['termo']}` "
                                                   f"({_sim(m['significativa_antiga'])} → "
                                                   f"{_sim(m['significativa_corrigida'])})" for m in mud_sig3) + "."
            if mud_sig3 else "Nenhuma linha do VD-3 muda de significância pelo critério da decisão 8.")
    t.append(f"**VD-3 (variantes do P1).** Razão de chances por +R$ 5 mil, antiga → corrigida: {lista}. {frase3} "
             f"{sig3}")
    mud4 = [m for m in resumo["mudancas"] if m["id_vd"] == "VD-4" and
            (m["muda_sinal"] or m["muda_significancia"] or m.get("muda_significancia_bootstrap"))]
    duf = {k: (_sel(est, ANTIGA, k, "D_UF"), _sel(est, CORRIGIDA, k, "D_UF")) for k in DUF_VD4}
    k5a, k5c = _sel(est, ANTIGA, "M1", "km_equivalentes", "K5"), _sel(est, CORRIGIDA, "M1", "km_equivalentes", "K5")
    t.append("**VD-4 (DAP, km e D_UF).** D_UF no P1h-3, antiga → corrigida: "
             + "; ".join(f"{ROTULO[k].replace('P1 ', '')}: {_n(a['estimativa'], 2)} → {_n(c['estimativa'], 2)} "
                         f"(q BKY {_p(a['q_bky'])} → {_p(c['q_bky'])})" for k, (a, c) in duf.items())
             + f". Um degrau da bolsa equivale a {_n(k5a['estimativa'], 0)} km na antiga e {_n(k5c['estimativa'], 0)} km "
               f"na corrigida (IC delta {_ic(k5c['ic95_inf'], k5c['ic95_sup'], 0)}). "
             + ((f"Mudam de sinal ou de significância {len(mud4)} linhas de DAP, km ou D_UF (seção 5.7)."
                 if len(mud4) > 1 else "Muda de sinal ou de significância uma linha de DAP, km ou D_UF (seção 5.7).")
                if mud4 else "Nenhuma linha de DAP, km ou D_UF muda de sinal ou de significância (seção 5.7)."))
    t.append("**Em linguagem simples.** A conta foi refeita usando o tipo de vaga que o candidato via na inscrição, e "
             "não o quadro arrumado depois do resultado. A tabela da seção 5.7 lista tudo o que mudou de lado do zero "
             "ou de significância. A bolsa aqui é o pacote do corte de IVS (bolsa e outras regras federais que mudam "
             "nos mesmos cortes), não a participação no PMM-E; a origem do candidato é preferência revelada, não efeito "
             "causal; e tudo vale para quem se candidatou, dentro das vagas abertas.")
    return "\n\n".join(t)


def texto_figura(resumo: dict) -> str:
    f = resumo["figura"]
    return "\n".join([f"![{f['titulo']}](../../{f['arquivo']})", "",
                      f"Arquivo: `{f['arquivo']}`. Título: \"{f['titulo']}\".", "",
                      f"**Como ler.** {f['como_ler']}"])


PENDENTE = "*Pendente: preenchido pelo script depois do portão de reprodução.*"


def gerar_doc(est: pd.DataFrame | None, resumo: dict | None) -> str:
    """Doc 57v. Sem resumo (pré-registro), só cabeçalho, inventário, decisões e limites."""
    tem_portao = resumo is not None and "portao" in resumo
    ok = tem_portao and resumo["portao"]["status"] == "PASSOU" and est is not None
    Lh = [
        "# 57v. Sensibilidades da escolha no ciclo 2 com o tipo de vaga do quadro de 13/02/2026 (adendo 52d)",
        "",
        "> **Gerado por** `scripts/rdd_bolsa/48_sensibilidades_ciclo2_quadro_1302.py` a partir de `output/rdd_bolsa/VD_*`; "
        "não editar à mão (o teste `tests/test_sensibilidades_ciclo2_quadro_1302.py` confere que este arquivo é igual "
        "ao gerado; `--atualizar-doc` o regrava das saídas).<br>",
        f"> **Adendo:** [`52d_adendo_sensibilidades_ciclo2_quadro_1302.md`](52d_adendo_sensibilidades_ciclo2_quadro_1302.md), "
        f"congelado em 26/10/2026 antes de rodar (commit `{COMMIT_ADENDO}`); SHA-256 em `adendo` de `VD_resumo.json`, "
        "conferido pelo teste. Protocolos de origem: [40](40_protocolo_multioutcome_rdd_bolsa.md) (E9, §12), "
        "[52](52_protocolo_P1_escolha_dap.md) (P1) e [52b](52b_protocolo_P1h_magnitudes.md) (P1h); adendo "
        "[52c](52c_adendo_vaga_imediata_ciclo2.md) (principais corrigidas, doc [57p](57p_escolha_vaga_imediata_c2.md)).<br>",
        "> **Estatuto:** `ADENDO_52D_POS_RESULTADO`. As versões com o quadro de 19/03 (docs 42, 57a e 57i) e as "
        "principais corrigidas do adendo 52c (doc 57p) já tinham sido vistas; isto não é teste confirmatório novo. "
        "Toda linha de `VD_estimativas.csv` e o resumo têm `natureza_dos_dados = EMPIRICO`.<br>",
        "> **Motivo:** [auditoria 41](../auditorias/41_auditoria_escolha_vaga_imediata_c2.md), achado A1: as "
        "sensibilidades que sustentam a robustez do ciclo 2 ([doc 44](44_sintese_rdd_bolsa_multioutcome.md)) ainda "
        "usavam o tipo de vaga do quadro retificado de 19/03/2026, refeito depois do resultado preliminar "
        "([auditoria 36](../auditorias/36_auditoria_dados_H1.md)).<br>",
        "> **Saídas:** `output/rdd_bolsa/VD_estimativas.csv`, `VD_resumo.json` e `VD_figuras/VD_antigo_corrigido.png`. "
        "As saídas `E9_*`, `P1_*`, `P1h_*` e `VC_*` não são regravadas, e os docs 42, 44, 57, 57a, 57i e 57p não são "
        "editados.<br>",
        "> **Auditoria:** pendente.",
        "",
        "## 1. Resposta curta",
        "",
    ]
    if ok:
        Lh += [*bloco("resposta", texto_resposta(est, resumo)), ""]
    elif tem_portao:
        Lh += [*bloco("resposta", f"Nada corrigido: `{resumo['portao']['status']}`."), ""]
    else:
        Lh += [PENDENTE, ""]
    Lh += ["## 2. Portão de reprodução (VD-5)", ""]
    Lh += [*bloco("portao", texto_portao(resumo)), ""] if tem_portao else [PENDENTE, ""]
    Lh += ["## 3. O que usa o tipo de vaga do ciclo 2", "", *bloco("inventario", texto_inventario()), ""]
    if ok:
        Lh += [
            "## 4. O conjunto só com vaga imediata com o quadro de 13/02",
            "",
            *bloco("correcao", texto_correcao(resumo)),
            "",
            "## 5. Tabelas: antigo e corrigido lado a lado",
            "",
            "### 5.1 E9 no conjunto só com vaga imediata (VD-1, VD-2)",
            "",
            *bloco("e9", tabela_e9(est)),
            "",
            "### 5.2 Variantes do P1: peso da bolsa (VD-3)",
            "",
            *bloco("p1", tabela_p1(est)),
            "",
            "### 5.3 M6: a bolsa por grupo (VD-3)",
            "",
            *bloco("m6", tabela_m6(est)),
            "",
            "### 5.4 Famílias BKY refeitas",
            "",
            *bloco("bky", tabela_bky(est)),
            "",
            "### 5.5 Disposição a pagar (VD-4)",
            "",
            *bloco("dap", tabela_dap(est)),
            "",
            "### 5.6 km equivalentes e D_UF (VD-4)",
            "",
            *bloco("p1h", tabela_p1h(est)),
            "",
            "### 5.7 O que mudou de sinal ou de significância",
            "",
            *bloco("mudancas", tabela_mudancas(resumo)),
            "",
            "## 6. Figura",
            "",
            *bloco("figura", texto_figura(resumo)),
            "",
        ]
    else:
        Lh += ["## 4. Resultados", "", PENDENTE, ""]
    Lh += [
        "## 7. Decisões de implementação",
        "",
        *bloco("decisoes", texto_decisoes()),
        "",
        "## 8. Limites",
        "",
        "- **Pós-resultado.** As versões antigas e as principais corrigidas já eram conhecidas. O adendo foi congelado "
        "antes de rodar, mas as sensibilidades corrigidas não são teste confirmatório novo.",
        "- **Só o tipo de vaga do ciclo 2 muda.** As linhas fora do §1 do adendo (seção 3) continuam com o quadro de "
        "19/03; os placebos de corte, o score bootstrap e o spline cúbico do doc 42 não foram refeitos no conjunto só "
        "com vaga imediata.",
        "- **O quadro de 13/02 também é anúncio.** Ele mede o que estava publicado na inscrição, não a vaga que de fato "
        "seria preenchida; o remanejamento posterior fica fora do atributo, como deve ficar num controle "
        "pré-tratamento.",
        "- **O conjunto só com vaga imediata muda de tamanho.** Com o quadro de 13/02 ele perde as células de reserva "
        "que viraram imediatas depois do resultado e os candidatos que as escolheram; a comparação antiga × corrigida "
        "mistura a troca da covariável com a troca da amostra.",
        "- **Escolha condicional.** Tudo vale para quem se candidatou, dentro das vagas abertas do seu curso e ciclo; o "
        "conjunto de escolha supõe que o candidato viu todas as células do curso; IIA do logit condicional (relaxada em "
        "parte no M8 e no M9).",
        "- **Pacote do corte.** O peso da bolsa é identificado pelos saltos nos cortes de IVS, com o IVS em spline "
        "contínua; nos mesmos cortes mudam outras regras federais (auditoria 18). Não é efeito da participação no "
        "PMM-E nem do Agora Tem Especialistas.",
        "- **Origem não é causal.** θ_UF é preferência revelada condicional ao modelo; a origem é o município do vínculo "
        "médico no CNES, não a residência.",
        "- **DAP e km são razões.** Com o coeficiente da bolsa perto de zero, a razão fica instável e não é preço.",
        "- **Poucos conjuntos.** O cluster é o conjunto de escolha (curso × ciclo), e são poucos; o número de cada linha "
        "está na coluna `g_conjuntos` de `VD_estimativas.csv`, e o p pela t com G − 1 gl está ao lado.",
    ]
    return "\n".join(Lh) + "\n"


# ---------------------------------------------------------------------------
# Execução
# ---------------------------------------------------------------------------

def entradas(dados: dict) -> list[dict]:
    be = P1.bloco_entrada
    return [
        be(ADENDO_MD, "adendo 52d (especificação, somente lido)", "repositório", "2026-10-26", "§1–§5", "documento",
           "-", "-"),
        be(ADENDO_52C, "adendo 52c (somente lido)", "repositório", "2026-10-26", "§1–§3", "documento", "-", "-"),
        be(PROTOCOLO_40, "protocolo 40 (E9, §12; somente lido)", "repositório", "2026-10-18", "§12, §14, §15",
           "documento", "-", "-"),
        be(PROTOCOLO_52, "protocolo 52 (P1; somente lido)", "repositório", "2026-10-19", "§1–§6", "documento", "-", "-"),
        be(PROTOCOLO_52B, "protocolo 52b (P1h; somente lido)", "repositório", "2026-10-26", "§1–§6", "documento", "-",
           "-"),
        be(VC.QUADRO_1302, "quadro do ciclo 2, retificado de 13/02/2026 (vigente na inscrição): versão corrigida",
           "Chamamento SGTES/MS nº 1/2026 (página oficial)", "2026-02-13", "1547 células CNES × curso", "célula",
           "CNES (7 dígitos) × código do curso", "coluna TOTAL de vagas imediatas"),
        be(VC.QUADRO_1903, "quadro do ciclo 2, retificado de 19/03/2026: conferência da versão antiga", "idem",
           "2026-03-19", "1547 células", "célula", "CNES × curso", "coluna TOTAL de vagas imediatas"),
        be(VC.A36_CELULAS, "leitura independente da auditoria 36: conferência do quadro de 13/02", "auditoria 36",
           "2026-10-26", "células dos ciclos 1–3", "célula", "cnes, cod_curso", "ciclo = 2"),
        be(E9_EST, "alvo do portão (E9 no conjunto só com vaga imediata)", "script 16", "2026-10-18", "todos os termos",
           "especificação × termo", "ciclo, modelo, conjunto, especificacao, termo",
           "condicional, sensibilidade, spline linear, bolsa linear"),
        be(E9_EFE, "alvo do portão (razão de chances e Δ prob. do E9)", "script 16", "2026-10-18", "bolsa_mil",
           "especificação × quantidade", "ciclo, modelo, conjunto, especificacao, termo, quantidade", "idem"),
        be(P1_EST, "alvo do portão (M1, M2, M4, M5, P1d, M6, M7, M8, M9, Holm e BKY)", "script 25", "2026-10-23",
           "todas as linhas desses modelos", "especificação × termo", "modelo, ciclo, tipo_linha, termo", "-"),
        be(P1_DAP, "alvo do portão (DAP do M1, M4, M7 e M5 ciclo 2)", "script 25", "2026-10-23", "4 atributos",
           "modelo × atributo", "modelo, ciclo, atributo", "-"),
        be(P1H_CSV, "alvo do portão (P1h-1, P1h-2, P1h-3)", "script 25c", "2026-10-26", "9 linhas", "linha",
           "id_linha, modelo, ciclo, componente", "sem as linhas FIG"),
        be(VC_CSV, "conferência do M1 e do M5 (adendo 52c)", "script 42", "2026-10-26", "M1 e M5, duas versões",
           "especificação × termo", "versao, chave_modelo, tipo_linha, termo", "coeficientes"),
        be(SCRIPT_42, "funções do adendo 52c (importadas sem alteração)", "repositório", "-", "-", "código", "-", "-"),
        be(SCRIPT_16, "funções do E9 (importadas sem alteração, pelo 42)", "repositório", "-", "-", "código", "-", "-"),
        be(SCRIPT_25, "funções do P1 (importadas sem alteração, pelo 42)", "repositório", "-", "-", "código", "-", "-"),
        be(SCRIPT_25C, "funções do P1h (importadas sem alteração, pelo 42)", "repositório", "-", "-", "código", "-",
           "-"),
        be(E9.ESCOLHAS, "escolhas dos candidatos (1ª e 2ª opção, marca de vaga imediata)", "tarefa B (script 12)",
           "resultados da 1ª chamada", f"{len(dados['cand'])} linhas", "candidato × opção",
           "ciclo, id_candidato, opcao_rank", "postos 1 e 2"),
        be(E9.CONJ_PRINCIPAL, "conjunto de escolha principal; ciclo 2 com a covariável de 19/03", "tarefa B (script 12)",
           "quadros da 1ª chamada", f"{len(dados['conj'])} células com IVS", "célula CNES × curso × ciclo",
           "ciclo, co_cnes_7d, cod_curso", "como no E9 e no P1"),
        be(E9.CONJ_SENSIBILIDADE, "conjunto só com vaga imediata (versão antiga, conferida contra a regra)",
           "tarefa B (script 12)", "quadros da 1ª chamada", "células com vaga imediata", "célula CNES × curso × ciclo",
           "ciclo, co_cnes_7d, cod_curso", "tem_vaga_imediata == 1"),
        be(E9.IVS_OFICIAL, "IVS 2010 oficial (a08)", "Ipea (a08)", "Censo 2010", f"{len(dados['ivs'])} municípios",
           "município", "co_ibge", "co_ibge, ivs"),
        be(P1.G1_ORIGEM, "município de origem (G1)", "portão G1", "referências 202506, 202510, 202602",
           f"{len(dados['org'])} candidatos", "candidato", "ciclo, id_candidato", f"regra_ligacao = {P1.REGRA_G1}"),
        be(P1.G1_DIST, "conferência das distâncias", "portão G1", "idem", "candidato × opção", "candidato × opção",
           "ciclo, id_candidato, opcao_rank", f"regra_ligacao = {P1.REGRA_G1}"),
        be(P1.X45.CIR_BRUTO, "região de saúde (CIR), só lido", "DATASUS/TabNet", dados["manifesto_cir"]["data_download_utc"],
           f"{dados['diag_cir']['municipios']} municípios", "município", "co_ibge → co_cir", "-"),
        be(P1.X1.COORD_JSON, "centroides municipais do IBGE, só lido", "IBGE, API de malhas v3",
           str(dados["diag_coord"].get("data_download", "")), f"{dados['diag_coord'].get('municipios')} municípios",
           "município", "id", "centroide"),
    ]


def remover_saidas_calculadas() -> None:
    for p in (OUT_CSV, FIG):
        if p.exists():
            p.unlink()
    if DIR_FIG.exists() and not any(DIR_FIG.iterdir()):
        DIR_FIG.rmdir()


def covariancias(v: dict) -> dict:
    """θ e blocos da covariância de bolsa, distância e mesma UF, para recálculo nos testes."""
    out = {}
    for chave, r in {**v["res_e9"], **{k: v["res"][k] for k in ("M1", "M2", "M4", "M5_2", "M7")}}.items():
        termos = [t for t in (B, P1.TERMO_DIST, "mesma_uf") if t in r["termos"]]
        k = [r["termos"].index(t) for t in termos]
        out[chave] = {"termos": termos, "theta": np.asarray(r["theta"])[k].tolist(),
                      "V_cluster_conjunto": np.asarray(r["V_conj"])[np.ix_(k, k)].tolist(), "g_conjuntos": r["G_conj"]}
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--atualizar-doc", action="store_true", help="só regrava o doc 57v a partir das saídas")
    ap.add_argument("--pre-registro", action="store_true",
                    help="grava o doc 57v só com o inventário e as decisões (antes de qualquer estimativa)")
    args = ap.parse_args(argv)
    if args.pre_registro:
        if OUT_RESUMO.exists():
            raise FalhaValidacao("VD_resumo.json já existe: o pré-registro só vale antes das estimativas")
        DOC.write_text(gerar_doc(None, None), encoding="utf-8")
        return 0
    if args.atualizar_doc:
        atualizar_doc()
        return 0
    t0 = time.time()

    def log(m: str) -> None:
        print(f"[{time.time() - t0:7.0f}s] {m}", flush=True)

    dados = P1.carregar()
    log("insumos do P1 carregados")
    prep = preparar(dados)
    log("quadros conferidos; conjunto e marcas corrigidos montados")
    resumo = {
        "etapa": "VD_sensibilidades_ciclo2_quadro_1302",
        "natureza_dos_dados": NATUREZA,
        "estatuto": ESTATUTO,
        "data_execucao": DATA_EXECUCAO,
        "script": rel(Path(__file__)),
        "adendo": {"arquivo": rel(ADENDO_MD), "sha256": sha256(ADENDO_MD), "commit_de_congelamento": COMMIT_ADENDO},
        "protocolos": {rel(p): sha256(p) for p in (PROTOCOLO_40, PROTOCOLO_52, PROTOCOLO_52B, ADENDO_52C)},
        "conferencias": prep["conferencias"],
        "correcao": prep["correcao"],
        "inventario": [dict(zip(("linha", "usa_tipo_de_vaga_ciclo2", "por_onde", "neste_adendo"), x))
                       for x in INVENTARIO],
        "decisoes": DECISOES,
        "entradas": entradas(dados),
        "integridade": ("nada simulado nem imputado; data/ só lido; IVS do a08 (o arquivo local de IVS da auditoria 16 "
                        "não é lido); só agregados em output/ (sem nome, CPF, CRM nem pseudônimo de candidato); saídas "
                        "E9_*, P1_*, P1h_* e VC_* não regravadas"),
        "linguagem": ("escolha condicional a se candidatar, dentro das vagas abertas; a bolsa mede o pacote do corte e o "
                      "incentivo marginal; θ_UF é preferência revelada, não efeito causal; não é efeito da participação "
                      "no PMM-E"),
        "tempo_execucao_nao_registrado": "fora do resumo para que duas execuções deem o mesmo hash",
    }
    va = estimar_versao(dados, prep["sens_a"], dados["cand"], dados["conj_p1"], log)
    port = portao(va, pd.read_csv(E9_EST, dtype={"ciclo": str}), pd.read_csv(E9_EFE, dtype={"ciclo": str}),
                  pd.read_csv(P1_EST, dtype={"ciclo": str}), pd.read_csv(P1_DAP, dtype={"ciclo": str}),
                  pd.read_csv(P1H_CSV, dtype={"ciclo": str}))
    resumo["portao"] = port
    log(f"portão: {port['status']}")
    if port["status"] != "PASSOU":
        remover_saidas_calculadas()
        resumo["saidas"] = {}
        gravar_json(OUT_RESUMO, resumo)
        atualizar_doc()
        print(f"{port['status']}: nada corrigido (adendo 52d)", file=sys.stderr)
        return 3

    vc = estimar_versao(dados, prep["sens_c"], prep["cand_c"], prep["conj_p1_c"], log)
    resumo["mesma_amostra"] = conferir_mesma_amostra(va, vc)
    est = montar(va, vc)
    sem = est[est["estimativa"].isna() & ~est["tipo_linha"].str.startswith("wald") & (est["status"] == "EXECUTADO")]
    if len(sem):
        raise FalhaValidacao(f"{len(sem)} linhas executadas sem estimativa")
    est.to_csv(OUT_CSV, index=False, float_format="%.10g")
    est = ler_est()
    resumo["conferencia_vc"] = conferir_contra_vc(est)
    for chave in VD3:
        for versao in VERSOES:
            termos = set(est[(est["versao"] == versao) & (est["chave_modelo"] == chave)]["termo"])
            if not {"tem_vaga_imediata", "log_vagas_imediatas_mais_1"} <= termos:
                raise FalhaValidacao(f"{chave}: o inventário diz que usa o tipo de vaga, mas os termos não estão lá")
    resumo["mudancas"] = mudancas(est)
    resumo["leitura"] = leitura(est)
    resumo["diagnosticos"] = {ANTIGA: va["diag"], CORRIGIDA: vc["diag"]}
    resumo["covariancias"] = {ANTIGA: covariancias(va), CORRIGIDA: covariancias(vc)}
    resumo["inferencia"] = {"principal": "sanduíche com cluster por conjunto de escolha (curso × ciclo), fator G/(G−1)",
                            "bky": {"P1": FAMILIA_P1, "P1h-3": FAMILIA_P1H3},
                            "sem_correcao_multipla": "VD-1 e VD-2 (E9 exploratório, protocolo 40 §12); DAP e km "
                                                     "(descritivos)",
                            "z_bilateral_95": Z95}
    resumo["figura"] = figura(est, resumo["leitura"])
    resumo["como_ler"] = {FIG.name: COMO_LER}
    resumo["saidas"] = {rel(OUT_CSV): sha256(OUT_CSV), rel(FIG): resumo["figura"]["sha256"]}
    gravar_json(OUT_RESUMO, resumo)
    atualizar_doc()
    log(f"gravado: {rel(OUT_CSV)}, {rel(OUT_RESUMO)}, {rel(FIG)}, {rel(DOC)}")
    return 0


def ler_est() -> pd.DataFrame:
    return pd.read_csv(OUT_CSV, dtype={"ciclo": str})


def ler_resumo() -> dict:
    return json.loads(OUT_RESUMO.read_text(encoding="utf-8"))


def atualizar_doc() -> None:
    resumo = ler_resumo()
    ok = resumo.get("portao", {}).get("status") == "PASSOU" and OUT_CSV.exists()
    DOC.write_text(gerar_doc(ler_est() if ok else None, resumo), encoding="utf-8")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except FalhaValidacao as erro:
        print(f"FALHA DE VALIDACAO: {erro}", file=sys.stderr)
        sys.exit(2)
