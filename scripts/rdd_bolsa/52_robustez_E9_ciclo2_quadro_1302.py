"""Adendo 52f: robustezes do E9 no ciclo 2 com o tipo de vaga do quadro de 13/02/2026.

Adendo congelado: `docs/06_execucao/52f_adendo_robustez_E9_ciclo2_quadro_1302.md` (27/10/2026, antes de rodar,
commit 9540a8a), com estatuto `ADENDO_52F_POS_RESULTADO`. Toda saída leva `natureza_dos_dados = EMPIRICO`.

Motivo (auditoria 46, achados A1, A2 e A10)
-------------------------------------------
O adendo 52c (script 42, doc 57p) corrigiu com o quadro de 13/02/2026 o E9 principal do ciclo 2, e o 52d (script 48,
doc 57v) a especificação principal do conjunto "só células com vaga imediata". Continuavam com o quadro retificado de
19/03/2026, refeito depois do resultado preliminar: as robustezes pós-auditoria do conjunto principal (score
bootstrap, CV3, inversão do score, placebos de corte, spline cúbico, nós a cada 0,05, janelas, cluster por curso), as
variantes quadrática e de degraus e o cluster por curso do conjunto só com vaga imediata, e o logit explodido e as
versões quadrática e de degraus do conjunto principal.

O que o script faz
------------------
1. **Portão RB-6.** Com o tipo de vaga antigo (19/03), reestima com as funções do script 16 importadas sem alteração
   (pelo 48 e pelo 42) as 48 especificações do protocolo do E9 (laço do `main` do 16) e chama
   `robustez_pos_auditoria` do 16 como está. Compara todas as linhas com `E9_estimativas.csv`,
   `E9_efeitos_marginais.csv` e `E9_robustez_pos_auditoria.csv` (diferença absoluta ≤ 1e−8 se o valor gravado tem
   módulo ≤ 1, relativa acima; NaN só com NaN; bootstraps com a mesma semente). Se falhar, a execução para
   (`FALHA_REPRODUCAO_<linha>`), as saídas calculadas são apagadas e nada é corrigido.
2. **Correção.** Só no ciclo 2: `vagas_imediatas`, `tem_vaga_imediata` e `log_vagas_imediatas_mais_1` do conjunto
   principal vêm do quadro de 13/02 (função `corrigir` do 42); o conjunto "só células com vaga imediata" e a marca da
   1ª opção dos candidatos são refeitos pela regra do script 12 (funções `sensibilidade_pela_regra` e
   `corrigir_candidatos` do 48). Nada é imputado.
3. **RB-1 a RB-5** com a versão corrigida, lado a lado com a antiga; BKY entre as secundárias (decisão 9).
4. **Leitura do §3** por regra fixada no código (`leitura`), sem escolha depois de ver os números.

Contraste: pacote do corte e incentivo marginal da bolsa na escolha condicional a candidatar-se, dentro das vagas
abertas. Não é efeito da participação no PMM-E nem do Agora Tem Especialistas. O E9 não usa a origem do candidato;
onde a origem aparece (P1), é preferência revelada, não efeito causal.

Integridade
-----------
Só lê `data/` (os dois quadros do ciclo 2, pelo leitor do script 12) e `output/`; não escreve em `data/`. O IVS 2010
oficial vem do a08; o arquivo local de IVS da auditoria 16 não é lido. Nada simulado nem imputado. Sem nome, CPF, CRM
ou pseudônimo de candidato em `output/`. As saídas `E9_*`, `VC_*`, `VD_*` e `VL_*` não são regravadas.

Uso
---
    python3 scripts/rdd_bolsa/52_robustez_E9_ciclo2_quadro_1302.py
    python3 scripts/rdd_bolsa/52_robustez_E9_ciclo2_quadro_1302.py --atualizar-doc   # só regrava o doc 57y
    python3 scripts/rdd_bolsa/52_robustez_E9_ciclo2_quadro_1302.py --pre-registro    # doc 57y sem resultados
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


# O 48 importa o 42, que importa o 25c, o 25, o 16 e o 12: usam-se os mesmos objetos, sem reescrever nenhum deles.
VD = _importar(DIR_RDD / "48_sensibilidades_ciclo2_quadro_1302.py", "sensibilidades_ciclo2_para_rb")
VC = VD.VC
E9 = VD.E9
P1 = VD.P1
L = VD.L

# ---------------------------------------------------------------------------
# Caminhos
# ---------------------------------------------------------------------------

SCRIPT_16 = DIR_RDD / "16_estimar_E9_escolha.py"
SCRIPT_42 = DIR_RDD / "42_escolha_vaga_imediata_c2.py"
SCRIPT_48 = DIR_RDD / "48_sensibilidades_ciclo2_quadro_1302.py"
SCRIPTS_CADEIA = [DIR_RDD / "12_construir_outcomes_funil.py", DIR_RDD / "25_escolha_dap.py",
                  DIR_RDD / "25c_magnitudes_P1h.py", DIR_RDD / "17_ponte_pmme_cnes.py",
                  DIR_RDD / "19_escolha_heterogeneidade.py", DIR_RDD / "rdd_lib.py"]
ADENDO_MD = ROOT / "docs" / "06_execucao" / "52f_adendo_robustez_E9_ciclo2_quadro_1302.md"
ADENDO_52C = VC.ADENDO_MD
ADENDO_52D = VD.ADENDO_MD
PROTOCOLO_40 = E9.PROTOCOLO_MD
DOC = ROOT / "docs" / "06_execucao" / "57y_robustez_E9_ciclo2_quadro_1302.md"
OUT = ROOT / "output" / "rdd_bolsa"
E9_EST = E9.OUT_ESTIMATIVAS
E9_EFE = E9.OUT_EFEITOS
E9_ROB = E9.OUT_ROBUSTEZ
VC_CSV = VC.OUT_CSV
VD_CSV = VD.OUT_CSV
OUT_CSV = OUT / "RB_estimativas.csv"
OUT_RESUMO = OUT / "RB_resumo.json"
DIR_FIG = OUT / "RB_figuras"
FIG = DIR_FIG / "RB_antigo_corrigido.png"

# ---------------------------------------------------------------------------
# Parâmetros (adendo 52f e script 16; nenhum é dado)
# ---------------------------------------------------------------------------

DATA_EXECUCAO = "2026-10-27"
NATUREZA = "EMPIRICO"
ESTATUTO = "ADENDO_52F_POS_RESULTADO"
COMMIT_ADENDO = "9540a8a"
TOL_REPRODUCAO = 1e-8
ALFA = 0.05
CICLO_CORRIGIDO = VC.CICLO_CORRIGIDO
ANTIGA, CORRIGIDA = VC.ANTIGA, VC.CORRIGIDA
VERSOES = (ANTIGA, CORRIGIDA)
QUADRO_DA_VERSAO = {ANTIGA: "19/03/2026", CORRIGIDA: "13/02/2026"}
CICLOS_QUE_MUDAM = ("2", "empilhado")
CICLOS_SEM_MUDANCA = ("1", "3", "1+3")
TAG = E9.TAG_ROB
ESPEC = E9.ESPEC_PRINCIPAL
COND, EXPL = E9.MODELO_COND, E9.MODELO_EXPL
B = "bolsa_mil"
TERMOS_BOLSA = ("bolsa_mil", "degrau_0300", "degrau_0400")
TESTE_DEGRAUS = "teste_igualdade_degraus_0300_menos_0400"
FATOR_RC = {"bolsa_mil": E9.PASSO_BOLSA_MIL, "degrau_0300": 1.0, "degrau_0400": 1.0, "degrau_placebo": 1.0}
# Ordem das colunas de E9_estimativas.csv (local `ordem_est` do main do script 16).
ORDEM_EST = ["natureza_dos_dados", "ciclo", "conjunto", "modelo", "especificacao", "no_protocolo",
             "papel_no_protocolo", "termo", "coef", "ep_cluster_conjunto", "ep_mle", "ep_cluster_candidato",
             "ic95", "ic95_inf", "ic95_sup", "p", "p_t_g_menos_1", "g_conjuntos", "g_candidatos", "n_candidatos",
             "n_grupos_escolha", "n_conjuntos", "n_alternativas", "log_verossimilhanca", "iteracoes", "convergiu",
             "nota"]
CHAVE_EST = ["ciclo", "conjunto", "modelo", "especificacao", "termo"]
CHAVE_EFE = ["ciclo", "conjunto", "modelo", "especificacao", "termo", "quantidade"]
CHAVE_ROB = ["analise", "ciclo", "modelo", "conjunto", "especificacao_base", "termo", "estatistica"]
COLS_EST = ["coef", "ep_cluster_conjunto", "ep_mle", "ep_cluster_candidato", "ic95_inf", "ic95_sup", "p",
            "p_t_g_menos_1", "g_conjuntos", "g_candidatos", "n_candidatos", "n_grupos_escolha", "n_conjuntos",
            "n_alternativas", "log_verossimilhanca"]
COLS_EFE = ["estimativa", "ep_cluster_conjunto", "ep_mle", "ic95_inf", "ic95_sup", "n_candidatos", "n_conjuntos",
            "n_alternativas"]
COLS_ROB = ["valor", "ep", "ic95_inf", "ic95_sup", "p", "g", "n_reamostras"]

COLUNAS = ["natureza_dos_dados", "estatuto", "id_rb", "papel", "peca", "versao", "versao_quadro_ciclo2", "fonte",
           "ciclo", "modelo", "conjunto", "especificacao", "analise", "termo", "estatistica", "estimativa", "ep",
           "ep_mle", "ep_cluster_candidato", "ic95_inf", "ic95_sup", "p", "p_t_g_menos_1", "g", "n_candidatos",
           "n_alternativas", "n_conjuntos", "n_reamostras", "rc_por_5mil", "rc_ic95_inf", "rc_ic95_sup", "convergiu",
           "entra_bky", "q_bky", "metodo", "nota"]

COMO_LER = ("À esquerda, cada linha é uma peça do E9 no ciclo 2, e o eixo é a razão de chances por +R$ 5 mil de bolsa "
            "anunciada, em escala log (nos degraus, um degrau vale +R$ 5 mil). O círculo vazado cinza é a versão antiga "
            "(tipo de vaga do ciclo 2 pelo quadro de 19/03/2026, refeito depois do resultado preliminar) e o ponto azul é "
            "a corrigida (quadro de 13/02/2026, vigente na inscrição). A faixa sombreada no alto marca a peça principal "
            "(RB-1): a barra é o IC 95% com cluster por conjunto (CR1, referência do adendo 52c), pelo CV3 e pela "
            "inversão do score bootstrap. Nas demais linhas, a barra é o IC 95% com cluster por conjunto de escolha. A "
            "linha vertical marca 1: acima de 1, a célula com bolsa maior é mais escolhida como 1ª opção. À direita, "
            "os cortes placebo do ciclo 2 (RB-2): cada ponto pequeno é o |t| de um corte falso; o losango é o |t| da "
            "bolsa no corte verdadeiro. Se o losango fica à direita de todos os pontos, o corte verdadeiro está fora da "
            "distribuição dos placebos. Tudo é escolha condicional a se candidatar, dentro das vagas abertas; a bolsa "
            "mede o pacote do corte, não a participação no PMM-E.")


class FalhaValidacao(RuntimeError):
    pass


rel = P1.rel
sha256 = P1.sha256
gravar_json = P1.gravar_json
_n, _p, _peq, _ic, _tab = P1._n, P1._p, P1._peq, P1._ic, P1._tab
comparar = VD.comparar
_dif_rel = VD._dif_rel


def _int(v) -> str:
    return "—" if v is None or pd.isna(v) else f"{int(v)}"


def _sim(v) -> str:
    return "—" if v is None else ("sim" if v else "não")


def _data_br(iso: str) -> str:
    a, m, d = iso.split("-")
    return f"{d}/{m}/{a}"


# ---------------------------------------------------------------------------
# Decisões de implementação (registradas e commitadas antes de qualquer estimativa)
# ---------------------------------------------------------------------------

# Inventário: (id, peça, função original no script 16, ciclos refeitos, como o quadro de 13/02 entra).
INVENTARIO = [
    ("RB-1", "Inferência com poucos clusters da especificação principal (logit condicional da 1ª opção, conjunto "
             "principal, spline linear, bolsa linear): score bootstrap de Kline–Santos com pesos Rademacher e Webb, "
             "CV3 e IC por inversão do score, com cluster por conjunto de escolha",
     "`robustez_pos_auditoria`, item 2: `score_efetivo_por_cluster`, `p_score_bootstrap` (com `p_rademacher_exato` "
     "e `matriz_pesos`), `ep_cv3`, `ic_inversao_score`; o ajuste é `estimar` do laço do `main`",
     "ciclo 2 (principal) e empilhado (secundária)",
     "as colunas `tem_vaga_imediata` e `log_vagas_imediatas_mais_1` do conjunto principal entram na matriz de "
     "atributos do modelo irrestrito e do restrito (β = 0) e de cada ajuste sem um cluster"),
    ("RB-1", "Mesma inferência com cluster por curso (score bootstrap, CV3, inversão) e CR1 por curso",
     "`robustez_pos_auditoria`, itens 1 e 2 (`covariancia_cluster` com `cluster_curso`)",
     "empilhado (secundária; o cluster por curso só existe no empilhado)", "idem"),
    ("RB-2", "Cortes placebo: degrau falso e nó no corte falso, com a bolsa verdadeira no modelo; 27 cortes; t real "
             "= t da bolsa na especificação principal; p por posto",
     "`robustez_pos_auditoria`, item 4: `estimar(..., placebo_mil=c)` e `linhas_estimativas`",
     "ciclo 2 e empilhado", "idem, em cada um dos 27 modelos e no t real"),
    ("RB-3", "Forma funcional: spline cúbico; spline linear com nós a cada 0,05; janelas de ±0,10, ±0,05 e ±0,025 em "
             "torno dos cortes, com spline linear e cúbico",
     "`robustez_pos_auditoria`, item 3: `estimar(..., grau=3)`, `estimar(..., nos_extras_mil=NOS_EXTRAS_MIL)` e "
     "conjuntos restritos às janelas",
     "ciclo 2 e empilhado", "idem; as janelas recortam células e candidatos pelo IVS, que não muda"),
    ("RB-4", "Conjunto \"só células com vaga imediata\": spline quadrático com bolsa linear; degraus por corte com "
             "spline linear e quadrático (e o Wald da igualdade dos degraus); CR1 por curso no empilhado",
     "laço do `main` (`estimar` com conjunto `sensibilidade`, `linhas_estimativas`, `linhas_efeitos`) e "
     "`robustez_pos_auditoria`, item 1",
     "ciclo 2 e empilhado",
     "define o conjunto (células com vaga imediata > 0 no quadro de 13/02, `sensibilidade_pela_regra` do 48) e os "
     "candidatos (1ª opção em célula com vaga imediata, `corrigir_candidatos` do 48; `montar_grupos` do 16 filtra "
     "por essa marca); `log_vagas_imediatas_mais_1` é covariável e `tem_vaga_imediata` é constante e sai"),
    ("RB-5", "Conjunto principal: logit explodido (1ª e 2ª opções) nas quatro especificações; logit condicional com "
             "spline quadrático e com degraus por corte; CR1 por curso no empilhado",
     "laço do `main` (`estimar`, `montar_grupos` com o posto 2) e `robustez_pos_auditoria`, item 1",
     "ciclo 2 e empilhado", "as duas colunas do tipo de vaga do conjunto principal, nos postos 1 e 2"),
    ("RB-6", "Todas as linhas acima, e as do protocolo e dos ciclos sem mudança, com o quadro de 19/03",
     "as mesmas funções", "ciclos 1, 2, 3, empilhado e 1+3", "não entra: é a versão antiga, contra os CSV gravados"),
    ("apoio", "Especificação principal (CR1) no conjunto principal e no só com vaga imediata; heterogeneidade entre "
              "ciclos (Q de Cochran, z do ciclo 2 contra o 3)",
     "laço do `main`; `robustez_pos_auditoria`, item 5",
     "ciclo 2 e empilhado; Q e z", "como em RB-1 e RB-4; o Q e o z usam o coeficiente do ciclo 2"),
]
FORA_DO_ADENDO = ("Não mudam e não são refeitos como resultado (só reproduzidos no portão e conferidos iguais nas "
                  "duas versões): os ciclos 1 e 3 e os ciclos 1 e 3 empilhados, porque o quadro só muda no ciclo 2. O "
                  "P1, a DAP e o P1h não entram: estão nos adendos 52c e 52d.")
SEMENTES = ("Sementes e grades são as do script 16, sem número aleatório novo: `SEMENTE_BOOT` = 20261018 e "
            "`N_REAMOSTRAS` = 199999; os pesos de cada sorteio vêm de `numpy.random.default_rng([20261018, G, k])`, "
            "com k = 1 (Rademacher) ou 6 (Webb), e são os mesmos em todo β₀ da inversão. Com G ≤ 24 o Rademacher é "
            "enumerado por inteiro (2^G vetores de sinais; no ciclo 2, G = 16) e não sorteia nada; o Webb é sempre "
            "sorteado. Grade de placebos `PLACEBOS_MIL` (27 cortes), janelas `JANELAS_MIL` e nós `NOS_EXTRAS_MIL`, "
            "todos do script 16.")

DECISOES = [
    {"data": "2026-10-27", "item": "Unidade de execução",
     "situacao": "O §2 pede \"as mesmas especificações do doc 42 e do 52d\"; no script 16 o cluster por curso percorre "
                 "todos os modelos empilhados do laço do `main`, e as robustezes saem de uma única função.",
     "resolucao": "Cada versão refaz o laço do `main` do 16 inteiro (ciclos 1, 2, 3 e empilhado × condicional no "
                  "conjunto principal, condicional no só com vaga imediata e explodido no principal × quatro "
                  "especificações) e chama `robustez_pos_auditoria` sem alteração. Assim o portão RB-6 cobre todas as "
                  "linhas de `E9_estimativas.csv`, `E9_efeitos_marginais.csv` e `E9_robustez_pos_auditoria.csv`, e "
                  "a versão corrigida usa exatamente o mesmo código. O laço é copiado do `main` (lá não é função), "
                  "como o 48 fez com o M6."},
    {"data": "2026-10-27", "item": "Como o quadro de 13/02 entra",
     "situacao": "O §2 manda tirar do quadro de 13/02 \"toda variável ou definição que depende do tipo de vaga\".",
     "resolucao": "Três trocas, todas só no ciclo 2 e com funções já auditadas: (a) `vagas_imediatas`, "
                  "`tem_vaga_imediata` e `log_vagas_imediatas_mais_1` do conjunto principal, por `corrigir` do 42 "
                  "(mesmo leitor `ler_quadro` do 12, conferido contra a auditoria 36); (b) o conjunto \"só células com "
                  "vaga imediata\" refeito por `sensibilidade_pela_regra` do 48 sobre o principal corrigido; (c) a "
                  "marca `celula_com_vaga_imediata` da 1ª opção, por `corrigir_candidatos` do 48. IVS, faixa, bolsa, "
                  "população, macrorregião, estrato, conjuntos de escolha e código do curso não mudam. Antes, o script "
                  "confere que o conjunto antigo é o do quadro de 19/03 e que a regra reproduz o conjunto gravado. "
                  "Célula sem linha ou sem número no quadro de 13/02 faz parar: nada é imputado."},
    {"data": "2026-10-27", "item": "Ciclos e empilhado",
     "situacao": "A tabela do §2 nomeia o ciclo 2; o doc 42 relata cada robustez também no empilhado, e os scripts 42 "
                 "e 48 refizeram o ciclo 2 e o empilhado.",
     "resolucao": "Cada peça é refeita no ciclo 2 e no empilhado, com o mesmo id. Só as linhas do ciclo 2 de RB-1 "
                  "(score bootstrap Rademacher e Webb, CV3 e inversão, cluster por conjunto) são a principal; as do "
                  "empilhado são secundárias. Ciclos 1, 3 e 1+3 são reestimados nas duas versões e têm de sair iguais "
                  "(diferença ≤ 1e−8; no conjunto só com vaga imediata a ordem das linhas pode mudar o último "
                  "algarismo). O Q de Cochran e o z do ciclo 2 contra o 3 dependem do ciclo 2: são relatados como "
                  "apoio, sem leitura e sem BKY, porque não estão na lista do §1."},
    {"data": "2026-10-27", "item": "Cluster por curso",
     "situacao": "O cluster por curso aparece no §1 só no conjunto \"só vaga imediata\"; no 16 ele existe também no "
                 "conjunto principal (auditoria 46, A1).",
     "resolucao": "Refeito onde o 16 o calcula (empilhado): na especificação principal do conjunto principal, com o "
                  "score bootstrap, o CV3 e a inversão, vai para RB-1; nas outras especificações do conjunto "
                  "principal e no explodido, para RB-5; no conjunto só com vaga imediata, para RB-4."},
    {"data": "2026-10-27", "item": "Sementes e grades",
     "situacao": "O §2 pede \"mesmos tamanhos de bootstrap, mesmas sementes e mesmas grades de placebo\".",
     "resolucao": "As constantes e as funções do 16, importadas; nenhuma semente nova (ver o parágrafo das sementes "
                  "acima). O portão exige que a versão antiga reproduza os p do bootstrap gravados."},
    {"data": "2026-10-27", "item": "Tolerância do portão RB-6",
     "situacao": "O §4 pede diferença ≤ 1e−8; os CSV gravam 10 algarismos significativos.",
     "resolucao": "Como na decisão 6 do 52d: diferença absoluta ≤ 1e−8 quando o valor gravado tem módulo ≤ 1, "
                  "relativa ≤ 1e−8 quando maior; NaN só casa com NaN; cada linha nova tem de casar com uma gravada "
                  "pelas chaves, e o número de linhas tem de ser igual. Também confere: o E9 principal (ciclo 2 e "
                  "empilhado) igual ao `VC_estimativas.csv` e a especificação principal do conjunto só com vaga "
                  "imediata igual ao `VD_estimativas.csv`, nas duas versões. Qualquer falha para a execução antes da "
                  "versão corrigida, e as saídas calculadas são apagadas."},
    {"data": "2026-10-27", "item": "Leitura do §3 por regra",
     "situacao": "O §3 fala em \"p < 0,05 (score bootstrap e CV3)\" e em \"corte verdadeiro fora da distribuição dos "
                 "placebos, como no original\", sem fixar o detalhe; e não prevê RB-1 mantido com RB-2 caído.",
     "resolucao": "Ciclo 2, versão corrigida. Score bootstrap: p < 0,05 nos dois pesos, Rademacher e Webb (o doc 44 "
                  "cita os dois). CV3: p pela t com G − 1 gl < 0,05 (como no 16). RB-2: nenhum |t| placebo maior ou "
                  "igual ao |t| real (p por posto no mínimo, 1/(N + 1)), como no original. Regra: se algum dos três p "
                  "de RB-1 for ≥ 0,05, REBAIXAR (e relatar qual caiu); senão, se RB-2 valer, MANTEM; senão, "
                  "PLACEBO_NAO_CONFIRMA, caso fora do §3: a parte \"poucos clusters\" da frase do doc 44 vale e a "
                  "parte \"a placebos\" não, e isso é só relatado. A mesma regra é aplicada à versão antiga, para "
                  "mostrar o \"como no original\"."},
    {"data": "2026-10-27", "item": "Mudança de sinal e de IC em RB-3 a RB-5",
     "situacao": "O §3 diz \"muda de sinal ou perde o IC que exclui 1\".",
     "resolucao": "Linhas lidas: cada peso da bolsa (coeficiente da bolsa linear ou de um degrau) de RB-3, RB-4 e "
                  "RB-5, no ciclo 2 e no empilhado, inclusive as do CR1 por curso. Muda de sinal: a estimativa "
                  "pontual troca de sinal. Perde o IC: o IC 95% da razão de chances excluía 1 na antiga e contém 1 na "
                  "corrigida (IC com cluster por conjunto; nas linhas por curso, o IC por curso). Ganhos de IC também "
                  "são listados. Uma linha que não converge numa versão é listada como sem estimativa."},
    {"data": "2026-10-27", "item": "BKY entre as secundárias",
     "situacao": "O §2 pede \"BKY entre as secundárias\"; o E9 é exploratório e não tinha família BKY.",
     "resolucao": "Família nova, uma por versão: toda linha secundária (RB-1 do empilhado, RB-2 a RB-5) que testa "
                  "H0: peso da bolsa = 0, com o p da própria linha: p normal com cluster por conjunto no coeficiente "
                  "da bolsa ou de um degrau (RB-3 a RB-5); p normal com cluster por curso nas linhas por curso; p do "
                  "score bootstrap; p do CV3 (t, G − 1); p por posto dos placebos. Ficam fora: a principal (RB-1 do "
                  "ciclo 2), os Wald de igualdade dos degraus (outra hipótese), os coeficientes dentro de cada modelo "
                  "placebo, as inversões (sem p) e o apoio. q pela função `qvalores_bky` da `rdd_lib` (Anderson, "
                  "2008)."},
    {"data": "2026-10-27", "item": "Razão de chances e figura",
     "situacao": "O 16 só grava razão de chances nas especificações do protocolo.",
     "resolucao": "Em toda linha de peso da bolsa: exp(5·β) na bolsa linear e exp(δ) num degrau (um degrau = +R$ 5 "
                  "mil), com o IC transformado do IC da linha, como em `linhas_efeitos` do 16 e no 42. A figura mostra "
                  "o ciclo 2, antiga e corrigida, com a principal destacada."},
    {"data": "2026-10-27", "item": "Números do doc 57y e entradas",
     "situacao": "O pedido do autor exige números só em blocos gerados; a auditoria 46 (A7) pediu hashes dos scripts "
                 "da cadeia.",
     "resolucao": "Todo número de resultado do 57y vem de `RB_*` por `--atualizar-doc`, entre marcadores "
                  "`<!-- RB:... -->`, e o teste confere. `entradas` traz o SHA-256 dos scripts 12, 16, 17, 19, 25, "
                  "25c, 42 e 48 e da `rdd_lib`."},
]

# ---------------------------------------------------------------------------
# Insumos e correção
# ---------------------------------------------------------------------------


def carregar() -> dict:
    """Insumos do E9 como no `main` do script 16."""
    dic = json.loads(E9.DICIONARIO.read_text(encoding="utf-8"))
    conferencias = E9.conferir_insumos(dic)
    mapa, _ = E9.mapa_bolsa_por_faixa()
    ivs = E9.carregar_ivs()
    cand = pd.read_parquet(E9.ESCOLHAS)
    if not (cand["natureza_dos_dados"] == NATUREZA).all():
        raise FalhaValidacao("escolhas com natureza diferente de EMPIRICO")
    conj_p, diag_p = E9.preparar_conjunto(pd.read_parquet(E9.CONJ_PRINCIPAL), ivs, mapa)
    conj_s, _ = E9.preparar_conjunto(pd.read_parquet(E9.CONJ_SENSIBILIDADE), ivs, mapa)
    if (conj_s["tem_vaga_imediata"] != 1).any():
        raise FalhaValidacao("conjunto de sensibilidade com célula sem vaga imediata")
    for d in diag_p["alternativas_retiradas_sem_ivs"]:
        hit = cand[(cand.ciclo == d["ciclo"]) & (cand.co_cnes_7d == d["co_cnes_7d"]) & (cand.cod_curso == d["cod_curso"])]
        if len(hit):
            raise FalhaValidacao(f"célula sem IVS escolhida por candidato: {d}")
    return {"conferencias": conferencias, "mapa": mapa, "ivs": ivs, "cand": cand, "conj_p": conj_p, "conj_s": conj_s,
            "macros": sorted(conj_p["macrorregiao"].unique()),
            "estratos": sorted(conj_p["estrato_territorial"].unique())}


def preparar(d: dict) -> dict:
    """Quadros do ciclo 2 conferidos; conjunto principal, conjunto só com vaga imediata e marca da 1ª opção corrigidos."""
    q1302, q1903 = VC.ler_quadros_c2()
    conf_antiga = VC.conferir_versao_antiga(d["conj_p"], q1903)
    conf_a36 = VC.conferir_contra_a36(q1302)
    conj_p_c, corr = VC.corrigir(d["conj_p"], q1302)
    conf_sens = VD.conferir_sensibilidade_gravada(d["conj_s"], VD.sensibilidade_pela_regra(d["conj_p"]))
    conj_s_c = VD.sensibilidade_pela_regra(conj_p_c)
    cand_c, conf_cand = VD.corrigir_candidatos(d["cand"], q1302, q1903)
    s2a = d["conj_s"][d["conj_s"]["ciclo"] == CICLO_CORRIGIDO]
    s2c = conj_s_c[conj_s_c["ciclo"] == CICLO_CORRIGIDO]
    return {"conj_p_c": conj_p_c, "conj_s_c": conj_s_c, "cand_c": cand_c,
            "conferencias": {"versao_antiga_do_conjunto": conf_antiga, "quadro_1302_contra_a36": conf_a36,
                             "sensibilidade_gravada_igual_a_regra": conf_sens, "marca_dos_candidatos": conf_cand},
            "correcao": {"conjunto_principal_ciclo2": corr,
                         "sensibilidade_ciclo2": {"celulas_19mar": int(len(s2a)), "celulas_13fev": int(len(s2c)),
                                                  "vagas_imediatas_19mar": float(s2a["vagas_imediatas"].sum()),
                                                  "vagas_imediatas_13fev": float(s2c["vagas_imediatas"].sum())},
                         "quadro_antigo": rel(VC.QUADRO_1903), "quadro_corrigido": rel(VC.QUADRO_1302)}}


# ---------------------------------------------------------------------------
# Estimação (funções do script 16, sem alteração)
# ---------------------------------------------------------------------------

def estimar_versao(conj_p: pd.DataFrame, conj_s: pd.DataFrame, cand: pd.DataFrame, macros: list[str],
                   estratos: list[str], log=print) -> dict:
    """Laço do `main` do script 16 e `robustez_pos_auditoria`, num par de conjuntos de escolha."""
    conjuntos = {"principal": conj_p, "sensibilidade": conj_s}
    resultados: dict[tuple, dict] = {}
    est_linhas: list[dict] = []
    efe_linhas: list[dict] = []
    for ciclo in E9.CICLOS:
        ciclos_int = [1, 2, 3] if ciclo == "empilhado" else [int(ciclo)]
        for modelo, conjunto in E9.COMBINACOES:
            conj = conjuntos[conjunto]
            conj_c = conj[conj["ciclo"].isin(ciclos_int)].reset_index(drop=True)
            cand_c = cand[cand["ciclo"].isin(ciclos_int)]
            for espec in E9.ESPECIFICACOES:
                r = E9.estimar(conj_c, cand_c, modelo, conjunto, espec, macros, estratos)
                resultados[(ciclo, modelo, conjunto, espec)] = r
                est_linhas += E9.linhas_estimativas(ciclo, r)
                efe_linhas += E9.linhas_efeitos(ciclo, r)
    log(f"laço do protocolo: {len(resultados)} modelos, {sum(r['ok'] for r in resultados.values())} ok")
    est_rob, rob_linhas, resumo_rob = E9.robustez_pos_auditoria(conj_p, cand, macros, estratos, resultados)
    log(f"robustez pós-auditoria: {len(est_rob)} linhas de modelos, {len(rob_linhas)} de inferência")
    est = pd.DataFrame(est_linhas + est_rob)
    efe = pd.DataFrame(efe_linhas)
    rob = pd.DataFrame(rob_linhas)
    for nome, df, cols in (("estimativas", est, ["coef", "ep_cluster_conjunto", "ep_mle", "ep_cluster_candidato", "p"]),
                           ("efeitos", efe, ["estimativa"]), ("robustez", rob, ["valor"])):
        sem = df[df[cols].isna().any(axis=1) & (df["nota"].fillna("") == "")]
        if len(sem):
            raise FalhaValidacao(f"{nome}: {len(sem)} linhas com NaN sem nota")
    convergencia = {f"{c}|{m}|{cj}|{e}": {"ok": bool(r["ok"]), "iteracoes": r.get("iteracoes"),
                                          "omitidas": r["omitidas"], "nota": r.get("nota", "")}
                    for (c, m, cj, e), r in resultados.items()}
    diag = {f"{c}|{cj}|{m}": r["diag_grupos"] for (c, m, cj, e), r in resultados.items() if e == ESPEC}
    del resultados
    return {"est": est[ORDEM_EST], "efe": efe, "rob": rob, "resumo_rob": resumo_rob, "convergencia": convergencia,
            "diag_grupos": diag}


# ---------------------------------------------------------------------------
# Classificação das linhas em peças
# ---------------------------------------------------------------------------

def _espec_curta(espec: str) -> str:
    return espec[len(TAG) + 1:] if str(espec).startswith(TAG) else str(espec)


def classificar_est(modelo: str, conjunto: str, espec: str) -> tuple[str, str]:
    """(id, peça) de uma linha de E9_estimativas ou E9_efeitos_marginais."""
    e = _espec_curta(espec)
    if str(espec).startswith(TAG):
        if e.startswith("placebo_"):
            return "RB-2", "cortes placebo (modelos)"
        if e.startswith("ciclos_1_e_3"):
            return "sem_mudanca", "ciclos 1 e 3 empilhados"
        return "RB-3", "forma funcional e janelas"
    if conjunto == "sensibilidade":
        return ("ref-52d", "especificação principal, só vaga imediata (adendo 52d)") if espec == ESPEC else \
            ("RB-4", "só vaga imediata: quadrática e degraus")
    if modelo == EXPL:
        return "RB-5", "logit explodido"
    return ("ref-52c", "especificação principal (adendo 52c)") if espec == ESPEC else \
        ("RB-5", "conjunto principal: quadrática e degraus")


def classificar_rob(analise: str, modelo: str, conjunto: str, espec_base: str) -> tuple[str, str]:
    if analise.startswith(("score_bootstrap", "cv3_", "ic_inversao")):
        return "RB-1", "poucos clusters"
    if analise == "cluster_curso":
        if conjunto == "sensibilidade":
            return "RB-4", "só vaga imediata: CR1 por curso"
        if modelo == COND and espec_base == ESPEC:
            return "RB-1", "poucos clusters: CR1 por curso"
        return "RB-5", "conjunto principal e explodido: CR1 por curso"
    if analise == "placebo_cortes":
        return "RB-2", "cortes placebo (resumo)"
    if analise == "heterogeneidade_ciclos":
        return "apoio", "heterogeneidade entre ciclos"
    raise FalhaValidacao(f"análise de robustez sem peça: {analise}")


def papel(id_rb: str, ciclo: str) -> str:
    if id_rb == "RB-1" and ciclo == "2":
        return "principal"
    if id_rb.startswith("RB-"):
        return "secundaria"
    return "apoio"


def grupo_portao(fonte: str, r: pd.Series) -> str:
    if fonte == "E9_estimativas":
        e = str(r["especificacao"])
        if e.startswith(TAG):
            c = _espec_curta(e)
            return ("est:placebos" if c.startswith("placebo_") else
                    "est:ciclos_1_e_3" if c.startswith("ciclos_1_e_3") else "est:forma_funcional_e_janelas")
        return f"est:{r['modelo']}:{r['conjunto']}"
    if fonte == "E9_efeitos_marginais":
        return f"efe:{r['modelo']}:{r['conjunto']}"
    a = str(r["analise"])
    return "rob:" + ("poucos_clusters" if a.startswith(("score_bootstrap", "cv3_", "ic_inversao")) else a)


# ---------------------------------------------------------------------------
# Portão RB-6
# ---------------------------------------------------------------------------

def portao(v: dict, e9_est: pd.DataFrame, e9_efe: pd.DataFrame, e9_rob: pd.DataFrame,
           tol: float = TOL_REPRODUCAO) -> dict:
    """Versão antiga contra os três CSV do 16; uma linha do portão por grupo de linhas."""
    linhas, falha = [], None
    for fonte, novo, grav, chave, cols in (("E9_estimativas", v["est"], e9_est, CHAVE_EST, COLS_EST),
                                           ("E9_efeitos_marginais", v["efe"], e9_efe, CHAVE_EFE, COLS_EFE),
                                           ("E9_robustez_pos_auditoria", v["rob"], e9_rob, CHAVE_ROB, COLS_ROB)):
        if list(novo.columns) != list(grav.columns):
            linhas.append({"linha": f"{fonte}:colunas", "linhas_reestimadas": 0, "linhas_gravadas": 0,
                           "todas_casadas": False, "passou": False})
            falha = falha or f"FALHA_REPRODUCAO_{fonte}_colunas"
            continue
        gn = novo.apply(lambda r: grupo_portao(fonte, r), axis=1)
        gg = grav.apply(lambda r: grupo_portao(fonte, r), axis=1)
        for g in sorted(set(gn) | set(gg)):
            n, gr = novo[gn == g], grav[gg == g]
            casou, difs, k = comparar(n, gr, chave, cols)
            passou = bool(casou and k == len(gr) and k > 0 and all(x <= tol for x in difs.values()))
            linhas.append({"linha": g, "fonte": fonte, "linhas_reestimadas": int(len(n)),
                           "linhas_gravadas": int(len(gr)), "todas_casadas": bool(casou and k == len(gr)),
                           **{f"dif_max_{c}": x for c, x in difs.items()}, "passou": passou})
            if not passou and falha is None:
                falha = f"FALHA_REPRODUCAO_{g}"
    return {"status": "PASSOU" if falha is None else falha, "tolerancia": tol,
            "regra": ("versão antiga (tipo de vaga do ciclo 2 pelo quadro de 19/03) reestimada com as funções do script "
                      "16 (laço do main e robustez_pos_auditoria) contra todas as linhas de E9_estimativas.csv, "
                      "E9_efeitos_marginais.csv e E9_robustez_pos_auditoria.csv, casadas pelas chaves; diferença "
                      "absoluta ≤ 1e−8 se o valor gravado tem módulo ≤ 1, relativa ≤ 1e−8 se maior; NaN só casa com "
                      "NaN; bootstraps com a mesma semente"),
            "linhas": linhas}


def conferir_contra_vc_vd(v: dict, versao: str) -> dict:
    """E9 principal igual ao VC_ (52c) e principal do conjunto só com vaga imediata igual ao VD_ (52d)."""
    vc = pd.read_csv(VC_CSV, dtype={"ciclo": str})
    vd = pd.read_csv(VD_CSV, dtype={"ciclo": str})
    out = {}
    est = v["est"]
    for ref, chave, ciclo, conjunto in ((vc, "E9_2", "2", "principal"), (vc, "E9_emp", "empilhado", "principal"),
                                        (vd, "E9s_2", "2", "sensibilidade"), (vd, "E9s_emp", "empilhado", "sensibilidade")):
        a = est[(est["ciclo"] == ciclo) & (est["modelo"] == COND) & (est["conjunto"] == conjunto) &
                (est["especificacao"] == ESPEC)]
        g = ref[(ref["versao"] == versao) & (ref["chave_modelo"] == chave) & (ref["tipo_linha"] == "coeficiente")]
        if list(a["termo"]) != list(g["termo"]):
            raise FalhaValidacao(f"{chave} ({versao}): termos diferentes da referência")
        d = max(_dif_rel(a[c].to_numpy(dtype=float), g[cg].to_numpy(dtype=float))
                for c, cg in (("coef", "estimativa"), ("ep_cluster_conjunto", "ep_cluster_conjunto"),
                              ("ep_mle", "ep_mle"), ("ep_cluster_candidato", "ep_cluster_candidato")))
        if d > TOL_REPRODUCAO:
            raise FalhaValidacao(f"{chave} ({versao}) difere de {'VC' if ref is vc else 'VD'}_estimativas.csv ({d})")
        out[chave] = d
    return out


def conferir_sem_mudanca(va: dict, vc: dict) -> dict:
    """Ciclos 1, 3 e 1+3 iguais nas duas versões (o quadro só muda no ciclo 2)."""
    out = {}
    for fonte, chave, cols, col_ciclo in (("est", CHAVE_EST, COLS_EST, "ciclo"), ("efe", CHAVE_EFE, COLS_EFE, "ciclo"),
                                          ("rob", CHAVE_ROB, COLS_ROB, "ciclo")):
        a = va[fonte][va[fonte][col_ciclo].isin(CICLOS_SEM_MUDANCA)]
        c = vc[fonte][vc[fonte][col_ciclo].isin(CICLOS_SEM_MUDANCA)]
        casou, difs, k = comparar(c, a, chave, cols)
        dmax = max(difs.values()) if difs else 0.0
        if not casou or k != len(a) or dmax > TOL_REPRODUCAO:
            raise FalhaValidacao(f"{fonte}: ciclos 1, 3 ou 1+3 mudaram com a correção do ciclo 2 ({dmax})")
        out[fonte] = {"linhas": int(k), "dif_max": dmax}
    return out


# ---------------------------------------------------------------------------
# Linhas de saída (esquema RB)
# ---------------------------------------------------------------------------

def _base(**kw) -> dict:
    b = {c: np.nan for c in COLUNAS}
    b.update({"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "entra_bky": False, "metodo": "", "nota": ""})
    b.update(kw)
    return b


def _rc(termo: str, est: float, lo: float, hi: float) -> dict:
    f = FATOR_RC.get(termo)
    if f is None or pd.isna(est):
        return {}
    ex = lambda x: math.exp(f * x) if pd.notna(x) else np.nan  # noqa: E731
    return {"rc_por_5mil": ex(est), "rc_ic95_inf": ex(lo), "rc_ic95_sup": ex(hi)}


def linhas_rb(versao: str, v: dict) -> list[dict]:
    out = []
    comum = {"versao": versao, "versao_quadro_ciclo2": QUADRO_DA_VERSAO[versao]}
    est = v["est"][v["est"]["ciclo"].isin(CICLOS_QUE_MUDAM)]
    for r in est.itertuples(index=False):
        idr, peca = classificar_est(r.modelo, r.conjunto, r.especificacao)
        estat = "wald_igualdade_degraus" if r.termo == TESTE_DEGRAUS else "coeficiente"
        out.append(_base(**comum, id_rb=idr, papel=papel(idr, r.ciclo), peca=peca, fonte="E9_estimativas",
                         ciclo=r.ciclo, modelo=r.modelo, conjunto=r.conjunto, especificacao=_espec_curta(r.especificacao),
                         analise="", termo=r.termo, estatistica=estat, estimativa=r.coef, ep=r.ep_cluster_conjunto,
                         ep_mle=r.ep_mle, ep_cluster_candidato=r.ep_cluster_candidato, ic95_inf=r.ic95_inf,
                         ic95_sup=r.ic95_sup, p=r.p, p_t_g_menos_1=r.p_t_g_menos_1, g=r.g_conjuntos,
                         n_candidatos=r.n_candidatos, n_alternativas=r.n_alternativas, n_conjuntos=r.n_conjuntos,
                         convergiu=bool(r.convergiu), metodo="CR1 por conjunto de escolha (script 16)",
                         nota=r.nota if isinstance(r.nota, str) else "",
                         **(_rc(r.termo, r.coef, r.ic95_inf, r.ic95_sup) if estat == "coeficiente" else {})))
    efe = v["efe"][v["efe"]["ciclo"].isin(CICLOS_QUE_MUDAM) &
                   v["efe"]["quantidade"].isin(["razao_chances_por_5mil", "variacao_prob_media_pp"])]
    for r in efe.itertuples(index=False):
        idr, peca = classificar_est(r.modelo, r.conjunto, r.especificacao)
        out.append(_base(**comum, id_rb=idr, papel=papel(idr, r.ciclo), peca=peca, fonte="E9_efeitos_marginais",
                         ciclo=r.ciclo, modelo=r.modelo, conjunto=r.conjunto, especificacao=r.especificacao, analise="",
                         termo=r.termo, estatistica=r.quantidade, estimativa=r.estimativa, ep=r.ep_cluster_conjunto,
                         ep_mle=r.ep_mle, ic95_inf=r.ic95_inf, ic95_sup=r.ic95_sup, n_candidatos=r.n_candidatos,
                         n_alternativas=r.n_alternativas, n_conjuntos=r.n_conjuntos, metodo=r.metodo_ic,
                         nota=r.nota if isinstance(r.nota, str) else ""))
    rob = v["rob"][v["rob"]["ciclo"].isin(CICLOS_QUE_MUDAM + ("1,2,3", "2 vs 3"))]
    for r in rob.itertuples(index=False):
        idr, peca = classificar_rob(r.analise, r.modelo, r.conjunto, r.especificacao_base)
        ciclo = str(r.ciclo)
        com_rc = r.analise == "cluster_curso" or r.analise.startswith(("cv3_", "ic_inversao"))
        out.append(_base(**comum, id_rb=idr, papel=papel(idr, ciclo), peca=peca, fonte="E9_robustez_pos_auditoria",
                         ciclo=ciclo, modelo=r.modelo, conjunto=r.conjunto, especificacao=r.especificacao_base,
                         analise=r.analise, termo=r.termo, estatistica=r.estatistica, estimativa=r.valor, ep=r.ep,
                         ic95_inf=r.ic95_inf, ic95_sup=r.ic95_sup, p=r.p, g=r.g, n_reamostras=r.n_reamostras,
                         metodo=r.metodo if isinstance(r.metodo, str) else "",
                         nota=r.nota if isinstance(r.nota, str) else "",
                         **(_rc(r.termo, r.valor, r.ic95_inf, r.ic95_sup) if com_rc else {})))
    return out


def entra_bky(r: pd.Series) -> bool:
    """Decisão 9: linha secundária que testa H0: peso da bolsa = 0, com p."""
    if r["papel"] != "secundaria" or pd.isna(r["p"]):
        return False
    if r["fonte"] == "E9_estimativas":
        return r["id_rb"] in ("RB-3", "RB-4", "RB-5") and r["termo"] in TERMOS_BOLSA
    if r["fonte"] == "E9_robustez_pos_auditoria":
        a = r["analise"]
        if a.startswith("score_bootstrap") or a.startswith("cv3_"):
            return True
        if a == "cluster_curso":
            return r["termo"] in TERMOS_BOLSA
        if a == "placebo_cortes":
            return r["estatistica"] == "p_posto"
    return False


def montar(va: dict, vc: dict) -> pd.DataFrame:
    est = pd.DataFrame(linhas_rb(ANTIGA, va) + linhas_rb(CORRIGIDA, vc))[COLUNAS]
    est["entra_bky"] = est.apply(entra_bky, axis=1).astype(bool)
    est["q_bky"] = np.nan
    for versao in VERSOES:
        m = (est["versao"] == versao) & est["entra_bky"]
        est.loc[m, "q_bky"] = L.qvalores_bky(est.loc[m, "p"].to_numpy(dtype=float))
    return est


CHAVE_RB = ["fonte", "ciclo", "modelo", "conjunto", "especificacao", "analise", "termo", "estatistica"]


# ---------------------------------------------------------------------------
# Leitura (regras fixadas antes de rodar; ver DECISOES 7 e 8)
# ---------------------------------------------------------------------------

def _sel(est: pd.DataFrame, versao: str, **f) -> pd.Series:
    m = (est["versao"] == versao).to_numpy().copy()
    for k, v in f.items():
        m &= (est[k].fillna("").astype(str) == str(v)).to_numpy()
    s = est[m]
    if len(s) != 1:
        raise FalhaValidacao(f"esperava 1 linha {versao} {f}, achei {len(s)}")
    return s.iloc[0]


def _rob(est: pd.DataFrame, versao: str, analise: str, ciclo: str, estatistica: str | None = None,
         **f) -> pd.Series:
    kw = {"fonte": "E9_robustez_pos_auditoria", "analise": analise, "ciclo": ciclo, **f}
    if estatistica is not None:
        kw["estatistica"] = estatistica
    return _sel(est, versao, **kw)


def _coef(est: pd.DataFrame, versao: str, ciclo: str, modelo: str, conjunto: str, espec: str,
          termo: str = B) -> pd.Series:
    return _sel(est, versao, fonte="E9_estimativas", ciclo=ciclo, modelo=modelo, conjunto=conjunto,
                especificacao=espec, termo=termo)


def _exclui(lo, hi, nulo: float = 0.0) -> bool | None:
    if pd.isna(lo) or pd.isna(hi):
        return None
    return bool(lo > nulo or hi < nulo)


def _sinal(x) -> int:
    return 0 if pd.isna(x) else int(np.sign(float(x)))


def criterio(r: pd.Series) -> tuple[str, bool | None, bool]:
    """(critério, significativa?, tem sinal?) de uma linha lida."""
    if r["fonte"] == "E9_estimativas":
        if r["estatistica"] == "wald_igualdade_degraus":
            return "p < 0,05", (None if pd.isna(r["p"]) else bool(r["p"] < ALFA)), False
        return "IC 95% exclui 0 (cluster por conjunto)", _exclui(r["ic95_inf"], r["ic95_sup"]), True
    a = r["analise"]
    if a.startswith("score_bootstrap") or a == "placebo_cortes":
        return ("p < 0,05" if a != "placebo_cortes" else "p por posto < 0,05"), \
            (None if pd.isna(r["p"]) else bool(r["p"] < ALFA)), False
    if a.startswith("cv3_"):
        return "p < 0,05 (t, G − 1)", (None if pd.isna(r["p"]) else bool(r["p"] < ALFA)), True
    if a == "cluster_curso":
        return "IC 95% exclui 0 (cluster por curso)", _exclui(r["ic95_inf"], r["ic95_sup"]), True
    if a.startswith("ic_inversao"):
        return "IC por inversão exclui 0", _exclui(r["ic95_inf"], r["ic95_sup"]), True
    raise FalhaValidacao(f"linha sem critério: {a}")


def linhas_de_leitura(est: pd.DataFrame) -> pd.DataFrame:
    """Linhas antigas lidas: principal (RB-1 do ciclo 2), membros do BKY, Wald dos degraus e inversões."""
    a = est[est["versao"] == ANTIGA]
    m = (a["entra_bky"] | (a["papel"] == "principal") |
         ((a["estatistica"] == "wald_igualdade_degraus") & a["id_rb"].isin(["RB-4", "RB-5"])) |
         a["analise"].fillna("").str.startswith("ic_inversao"))
    return a[m]


def mudancas(est: pd.DataFrame) -> list[dict]:
    out = []
    corr = est[est["versao"] == CORRIGIDA]
    chaves = [tuple(str(x) for x in t) for t in corr[CHAVE_RB].itertuples(index=False, name=None)]
    if len(set(chaves)) != len(chaves):
        raise FalhaValidacao("chave repetida na versão corrigida")
    c_idx = dict(zip(chaves, (r for _, r in corr.iterrows())))
    for _, a in linhas_de_leitura(est).iterrows():
        k = tuple(str(a[x]) for x in CHAVE_RB)
        if k not in c_idx:
            raise FalhaValidacao(f"linha sem par na versão corrigida: {k}")
        c = c_idx[k]
        crit, sa, tem_sinal = criterio(a)
        _, sc, _ = criterio(c)
        ga, gc = (_sinal(a["estimativa"]), _sinal(c["estimativa"])) if tem_sinal else (0, 0)
        sem_est = bool(pd.isna(a["estimativa"]) or pd.isna(c["estimativa"]))
        out.append({"id_rb": a["id_rb"], "papel": a["papel"], "peca": a["peca"], "fonte": a["fonte"],
                    "ciclo": a["ciclo"], "modelo": a["modelo"], "conjunto": a["conjunto"],
                    "especificacao": a["especificacao"], "analise": a["analise"] if pd.notna(a["analise"]) else "",
                    "termo": a["termo"], "estatistica": a["estatistica"],
                    "estimativa_antiga": float(a["estimativa"]) if pd.notna(a["estimativa"]) else None,
                    "estimativa_corrigida": float(c["estimativa"]) if pd.notna(c["estimativa"]) else None,
                    "criterio": crit, "significativa_antiga": sa, "significativa_corrigida": sc,
                    "sem_estimativa": sem_est,
                    "muda_sinal": bool(ga != gc and ga != 0 and gc != 0),
                    "perde_significancia": bool(sa is True and sc is False),
                    "ganha_significancia": bool(sa is False and sc is True)})
    return out


def _nome(m: dict) -> str:
    return f"{m['ciclo']}|{m['conjunto']}|{m['modelo']}|{m['especificacao']}|{m['analise']}|{m['termo']}"


def regra_rb(p_rad: float, p_webb: float, p_cv3: float, n_maior: float) -> tuple[str, list[str]]:
    """§3 do adendo (decisão 7). Devolve a regra e a lista das inferências de RB-1 com p ≥ 0,05."""
    caiu = [nome for nome, p in (("score bootstrap Rademacher", p_rad), ("score bootstrap Webb", p_webb),
                                 ("CV3", p_cv3)) if pd.isna(p) or p >= ALFA]
    if caiu:
        return "REBAIXAR", caiu
    if pd.notna(n_maior) and int(n_maior) == 0:
        return "MANTEM", []
    return "PLACEBO_NAO_CONFIRMA", []


def leitura(est: pd.DataFrame) -> dict:
    out = {}
    for v in VERSOES:
        rad = _rob(est, v, "score_bootstrap_rademacher_cluster_conjunto", "2")
        web = _rob(est, v, "score_bootstrap_webb_cluster_conjunto", "2")
        cv3 = _rob(est, v, "cv3_cluster_conjunto", "2")
        inv = _rob(est, v, "ic_inversao_score_rademacher_cluster_conjunto", "2")
        nm = _rob(est, v, "placebo_cortes", "2", "n_abs_t_placebo_maior_ou_igual_ao_real")
        pp = _rob(est, v, "placebo_cortes", "2", "p_posto")
        regra, caiu = regra_rb(rad["p"], web["p"], cv3["p"], nm["estimativa"])
        out[v] = {"regra": regra, "inferencias_RB1_com_p_maior_ou_igual_0_05": caiu,
                  "p_score_rademacher": rad["p"], "p_score_webb": web["p"], "p_cv3": cv3["p"],
                  "ic_cv3": [cv3["ic95_inf"], cv3["ic95_sup"]], "ic_inversao": [inv["ic95_inf"], inv["ic95_sup"]],
                  "RB2_n_placebos_com_abs_t_maior_ou_igual": nm["estimativa"], "RB2_p_posto": pp["estimativa"],
                  "RB2_corte_fora_da_distribuicao": bool(pd.notna(nm["estimativa"]) and int(nm["estimativa"]) == 0)}
    mud = mudancas(est)
    rb35 = [m for m in mud if m["id_rb"] in ("RB-3", "RB-4", "RB-5") and m["estatistica"] != "wald_igualdade_degraus"
            and m["criterio"].startswith("IC")]
    regra = out[CORRIGIDA]["regra"]
    out["frase_doc44"] = {"MANTEM": "CONTINUA_VALENDO", "REBAIXAR": "REBAIXAR",
                          "PLACEBO_NAO_CONFIRMA": "VALE_SO_POUCOS_CLUSTERS"}[regra]
    out["RB3_a_RB5"] = {"mudam_sinal": [_nome(m) for m in rb35 if m["muda_sinal"]],
                        "perdem_ic_que_exclui_1": [_nome(m) for m in rb35 if m["perde_significancia"]],
                        "ganham_ic_que_exclui_1": [_nome(m) for m in rb35 if m["ganha_significancia"]],
                        "sem_estimativa": [_nome(m) for m in rb35 if m["sem_estimativa"]],
                        "linhas_lidas": len(rb35),
                        "nao_mudam": len([m for m in rb35 if not (m["muda_sinal"] or m["perde_significancia"]
                                                                   or m["sem_estimativa"])])}
    out["linhas_que_mudam_sinal"] = [f"{m['id_rb']}:{_nome(m)}" for m in mud if m["muda_sinal"]]
    out["linhas_que_mudam_significancia"] = [f"{m['id_rb']}:{_nome(m)}" for m in mud
                                             if m["perde_significancia"] or m["ganha_significancia"]]
    return out


# ---------------------------------------------------------------------------
# Rótulos
# ---------------------------------------------------------------------------

ROT_ESPEC = {"spline_linear__bolsa_linear": "spline linear, bolsa linear",
             "spline_quadratico__bolsa_linear": "spline quadrático, bolsa linear",
             "spline_linear__degraus_por_corte": "spline linear, degraus",
             "spline_quadratico__degraus_por_corte": "spline quadrático, degraus",
             "spline_cubico__bolsa_linear": "spline cúbico",
             "nos_cada_0050__spline_linear__bolsa_linear": "spline linear, nós a cada 0,05"}
for _h in E9.JANELAS_MIL:
    ROT_ESPEC[f"janela_{_h:04d}__spline_linear__bolsa_linear"] = f"janela ±{_h / 1000:.3f}, spline linear".replace(".", ",")
    ROT_ESPEC[f"janela_{_h:04d}__spline_cubico__bolsa_linear"] = f"janela ±{_h / 1000:.3f}, spline cúbico".replace(".", ",")
ROT_TERMO = {"bolsa_mil": "bolsa", "degrau_0300": "degrau 0,300", "degrau_0400": "degrau 0,400",
             TESTE_DEGRAUS: "Wald: degrau 0,300 = degrau 0,400"}
ROT_MODELO = {COND: "condicional", EXPL: "explodido"}
ROT_ANALISE = {"score_bootstrap_rademacher_cluster_conjunto": "p do score bootstrap, Rademacher",
               "score_bootstrap_webb_cluster_conjunto": "p do score bootstrap, Webb",
               "cv3_cluster_conjunto": "CV3: coef. [IC t]; p",
               "ic_inversao_score_rademacher_cluster_conjunto": "IC por inversão do score",
               "score_bootstrap_rademacher_cluster_curso": "p do score bootstrap, Rademacher",
               "score_bootstrap_webb_cluster_curso": "p do score bootstrap, Webb",
               "cv3_cluster_curso": "CV3: coef. [IC t]; p",
               "ic_inversao_score_rademacher_cluster_curso": "IC por inversão do score"}


ROT_CONJUNTO = {"principal": "conjunto principal", "sensibilidade": "só vaga imediata"}


def rot_linha(m: dict | pd.Series) -> str:
    espec = ROT_ESPEC.get(m["especificacao"], m["especificacao"])
    m = {**dict(m), "conjunto": ROT_CONJUNTO.get(m["conjunto"], m["conjunto"])}
    if m["analise"] == "cluster_curso":
        return f"{ROT_MODELO.get(m['modelo'], m['modelo'])}, {m['conjunto']}, {espec}, {ROT_TERMO.get(m['termo'], m['termo'])} (CR1 por curso)"
    if m["analise"]:
        if m["analise"] == "placebo_cortes":
            return "cortes placebo: p por posto"
        return ROT_ANALISE.get(m["analise"], m["analise"])
    return f"{ROT_MODELO.get(m['modelo'], m['modelo'])}, {m['conjunto']}, {espec}, {ROT_TERMO.get(m['termo'], m['termo'])}"


# ---------------------------------------------------------------------------
# Figura
# ---------------------------------------------------------------------------

def _plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 11})
    return plt


COR = {ANTIGA: "#8a8984", CORRIGIDA: "#2a78d6"}


def linhas_figura(est: pd.DataFrame) -> list[tuple[str, str, dict]]:
    """(rótulo, id, seletor) das linhas do painel da esquerda, ciclo 2."""
    sel = [("RB-1: CR1 por conjunto (adendo 52c)", "RB-1",
            dict(fonte="E9_estimativas", modelo=COND, conjunto="principal", especificacao=ESPEC, termo=B)),
           ("RB-1: CV3, IC pela t", "RB-1", dict(fonte="E9_robustez_pos_auditoria", analise="cv3_cluster_conjunto")),
           ("RB-1: inversão do score bootstrap", "RB-1",
            dict(fonte="E9_robustez_pos_auditoria", analise="ic_inversao_score_rademacher_cluster_conjunto"))]
    for e in ["spline_cubico__bolsa_linear", "nos_cada_0050__spline_linear__bolsa_linear"] + \
             [f"janela_{h:04d}__spline_{s}__bolsa_linear" for h in E9.JANELAS_MIL for s in ("linear", "cubico")]:
        sel.append((f"RB-3: {ROT_ESPEC[e]}", "RB-3",
                    dict(fonte="E9_estimativas", modelo=COND, conjunto="principal", especificacao=e, termo=B)))
    for conjunto, idr, modelos, rotc in (("sensibilidade", "RB-4", (COND,), "só vaga imediata"),
                                         ("principal", "RB-5", (COND, EXPL), "principal")):
        for modelo in modelos:
            for e, termos in (("spline_linear__bolsa_linear", (B,)), ("spline_quadratico__bolsa_linear", (B,)),
                              ("spline_linear__degraus_por_corte", ("degrau_0300", "degrau_0400")),
                              ("spline_quadratico__degraus_por_corte", ("degrau_0300", "degrau_0400"))):
                if e == ESPEC and modelo == COND:
                    continue
                for t in termos:
                    pre = f"{idr}: só vaga imediata" if conjunto == "sensibilidade" else f"{idr}: {ROT_MODELO[modelo]}"
                    rot = (f"{pre}, {ROT_ESPEC[e]}" if t == B else
                           f"{pre}, {ROT_ESPEC[e].replace(', degraus', '')}, {ROT_TERMO[t]}")
                    sel.append((rot, idr, dict(fonte="E9_estimativas", modelo=modelo, conjunto=conjunto,
                                               especificacao=e, termo=t)))
    return sel


def titulo_figura(lei: dict) -> str:
    return {"MANTEM": "Com o tipo de vaga da inscrição, o ciclo 2 continua robusto a poucos clusters e a placebos",
            "REBAIXAR": "Com o tipo de vaga da inscrição, a inferência robusta do ciclo 2 perde a precisão",
            "PLACEBO_NAO_CONFIRMA": "Com o tipo de vaga da inscrição, o ciclo 2 resiste a poucos clusters, mas não "
                                    "se destaca dos placebos"}[lei[CORRIGIDA]["regra"]]


def figura(est: pd.DataFrame, lei: dict) -> dict:
    plt = _plt()
    DIR_FIG.mkdir(parents=True, exist_ok=True)
    sel = linhas_figura(est)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15.0, 12.5), gridspec_kw={"width_ratios": [1.9, 1.0]})
    y0 = np.arange(len(sel))[::-1].astype(float)
    n_rb1 = sum(1 for _, i, _ in sel if i == "RB-1")
    ax1.axhspan(y0[n_rb1 - 1] - 0.5, y0[0] + 0.5, color="#e8f0fb", zorder=0)
    vals = []
    for yi, (rot, idr, f) in zip(y0, sel):
        for v, dy in ((ANTIGA, 0.17), (CORRIGIDA, -0.17)):
            r = _sel(est, v, ciclo="2", **f)
            if pd.isna(r["rc_por_5mil"]) or pd.isna(r["rc_ic95_inf"]):
                continue
            vals += [r["rc_ic95_inf"], r["rc_ic95_sup"]]
            ax1.plot([r["rc_ic95_inf"], r["rc_ic95_sup"]], [yi + dy] * 2, color=COR[v], lw=2.2,
                     solid_capstyle="round", zorder=2)
            ax1.plot([r["rc_por_5mil"]], [yi + dy], "o", ms=7.5, zorder=3, mfc="white" if v == ANTIGA else COR[v],
                     mec=COR[v], mew=1.8)
    ax1.axvline(1.0, color="#52514e", lw=1.0)
    ax1.set_yticks(y0)
    ax1.set_yticklabels([s[0] for s in sel], fontsize=9.5)
    for lab, (_, idr, _) in zip(ax1.get_yticklabels(), sel):
        if idr == "RB-1":
            lab.set_fontweight("bold")
    ax1.set_xscale("log")
    ticks = [0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0]
    lo, hi = max(0.3, min(vals) * 0.9), max(vals) * 1.1
    ax1.set_xlim(lo, hi)
    ax1.set_xticks([t for t in ticks if lo <= t <= hi])
    ax1.set_xticklabels([_n(t, 2 if t == 0.75 else 1) for t in ticks if lo <= t <= hi])
    ax1.minorticks_off()
    ax1.set_ylim(-0.7, len(sel) - 0.3)
    ax1.set_xlabel("razão de chances da 1ª opção por +R$ 5 mil (escala log), IC 95%", fontsize=10.5)
    ax1.set_title("ciclo 2: peças RB-1, RB-3, RB-4 e RB-5", fontsize=11, loc="left")
    # Placebos (RB-2)
    tmax = 0.0
    for k, v in enumerate(VERSOES):
        pl = est[(est["versao"] == v) & (est["ciclo"] == "2") & (est["id_rb"] == "RB-2") &
                 (est["fonte"] == "E9_estimativas") & (est["termo"] == "degrau_placebo")]
        t = np.abs(pl["estimativa"].to_numpy(dtype=float) / pl["ep"].to_numpy(dtype=float))
        t = t[np.isfinite(t)]
        yk = 1 - k
        jit = (np.arange(len(t)) % 3 - 1) * 0.08
        ax2.plot(t, yk + jit, "o", ms=5, color=COR[v], alpha=0.55, mfc=COR[v] if v == CORRIGIDA else "white",
                 mec=COR[v])
        tr = abs(_rob(est, v, "placebo_cortes", "2", "t_real")["estimativa"])
        ax2.plot([tr], [yk], "D", ms=11, color=COR[v], mec="#1f1f1d", mew=1.2, zorder=4)
        tmax = max(tmax, tr, float(t.max()) if len(t) else 0.0)
        ax2.text(tr, yk + 0.2, f"|t| real {_n(tr, 2)}", ha="right", fontsize=9.5, color="#2b2b29")
    ax2.axvline(1.96, color="#52514e", lw=0.8, ls=":")
    ax2.set_yticks([1, 0])
    ax2.set_yticklabels(["antiga (19/03)", "corrigida (13/02)"], fontsize=10)
    ax2.set_ylim(-0.6, 1.6)
    ax2.set_xlim(0, tmax * 1.1)
    ax2.set_xlabel("|t|: cortes falsos (pontos) e corte verdadeiro (losango)", fontsize=10)
    ax2.set_title("ciclo 2: cortes placebo (RB-2)", fontsize=11, loc="left")
    for ax in (ax1, ax2):
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
        ax.tick_params(axis="y", length=0)
        ax.grid(axis="x", color="#e6e5e0", lw=0.6)
        ax.set_axisbelow(True)
    from matplotlib.lines import Line2D
    leg = [Line2D([0], [0], marker="o", color=COR[ANTIGA], mfc="white", mec=COR[ANTIGA], mew=2, lw=2.2,
                  label="antiga: tipo de vaga do ciclo 2 pelo quadro de 19/03/2026 (pós-resultado)"),
           Line2D([0], [0], marker="o", color=COR[CORRIGIDA], mfc=COR[CORRIGIDA], mec=COR[CORRIGIDA], lw=2.2,
                  label="corrigida: quadro de 13/02/2026 (vigente na inscrição)")]
    fig.legend(handles=leg, loc="upper left", bbox_to_anchor=(0.01, 0.945), ncol=2, frameon=False, fontsize=10)
    fig.text(0.01, 0.985, titulo_figura(lei), fontsize=14.5, ha="left", va="top", color="#1f1f1d")
    fig.text(0.01, 0.012, "Escolha da 1ª opção, condicional a se candidatar. Faixa azul: peça principal (RB-1). Bolsa: "
             "pacote do corte, não participação no PMM-E.", fontsize=9.5, color="#52514e", ha="left", va="bottom")
    fig.subplots_adjust(left=0.27, right=0.975, top=0.90, bottom=0.07, wspace=0.22)
    fig.savefig(FIG, dpi=130, metadata={"Software": None})
    plt.close(fig)
    return {"arquivo": rel(FIG), "sha256": sha256(FIG), "titulo": titulo_figura(lei), "como_ler": COMO_LER}


# ---------------------------------------------------------------------------
# Documento 57y
# ---------------------------------------------------------------------------

def bloco(nome: str, corpo: str) -> list[str]:
    return [f"<!-- RB:{nome}:inicio -->", corpo, f"<!-- RB:{nome}:fim -->"]


def _sci(v) -> str:
    return "—" if v is None else f"{v:.1e}".replace(".", ",").replace("-", "−")


def texto_decisoes() -> str:
    linhas = [list(x) for x in INVENTARIO]
    t = ["Registradas e commitadas antes de qualquer estimativa deste adendo (o histórico do Git mostra o commit deste "
         "bloco antes do commit dos números). Nenhuma muda a amostra, o conjunto de escolha principal ou a "
         "especificação dos modelos do doc 42. Onde o adendo era ambíguo, vale a leitura mais próxima dos scripts 16, "
         "42 e 48.", "",
         "**Inventário das peças.** Lido do código do script 16, sem estimar nada.", "",
         _tab(["Id", "Peça", "Função original (script 16)", "Ciclos refeitos", "Como o quadro de 13/02 entra"], linhas),
         "", FORA_DO_ADENDO, "", f"**Sementes.** {SEMENTES}", "", "**Decisões.**", ""]
    for i, d in enumerate(DECISOES, 1):
        t.append(f"{i}. **{d['item']}** ({_data_br(d['data'])}). {d['situacao']} *Resolução:* {d['resolucao']}")
    return "\n".join(t)


def texto_portao(resumo: dict) -> str:
    p = resumo["portao"]
    linhas = []
    for e in p["linhas"]:
        difs = [v for k, v in e.items() if k.startswith("dif_max_")]
        linhas.append([f"`{e['linha']}`", f"{e['linhas_reestimadas']} / {e['linhas_gravadas']}",
                       _sci(max(difs)) if difs else "—", "passou" if e["passou"] else "**falhou**"])
    t = [f"**Portão de reprodução (RB-6): {p['status']}.** Com o tipo de vaga antigo, as funções do script 16 "
         "(importadas sem alteração pelo 48 e pelo 42) reproduzem todas as linhas de `E9_estimativas.csv`, "
         "`E9_efeitos_marginais.csv` e `E9_robustez_pos_auditoria.csv`, inclusive os p do score bootstrap com a mesma "
         "semente. A diferença é absoluta quando o valor gravado tem módulo até 1 e relativa acima disso (decisão 6); "
         "a coluna mostra a maior diferença entre as quantidades comparadas do grupo (a lista completa está em "
         "`portao` de `RB_resumo.json`).", "",
         _tab(["Grupo de linhas", "Linhas (reestimadas / gravadas)", "Dif. máx.", "Portão"], linhas)]
    if p["status"] != "PASSOU":
        t += ["", f"A execução parou em `{p['status']}`: nada foi corrigido (adendo 52f, §4)."]
    else:
        cv = resumo["conferencia_vc_vd"]
        dmax = max(max(x.values()) for x in cv.values())
        sm = resumo["ciclos_sem_mudanca"]
        t += ["", f"Também conferido: o E9 principal (ciclo 2 e empilhado) sai igual ao `VC_estimativas.csv` do 52c e a "
                  f"especificação principal do conjunto só com vaga imediata sai igual ao `VD_estimativas.csv` do 52d, "
                  f"nas duas versões (dif. máx. {_sci(dmax)}); os ciclos 1, 3 e 1+3 saem iguais nas duas versões "
                  f"({sm['est']['linhas'] + sm['efe']['linhas'] + sm['rob']['linhas']} linhas; dif. máx. "
                  f"{_sci(max(x['dif_max'] for x in sm.values()))})."]
    return "\n".join(t)


def texto_correcao(resumo: dict) -> str:
    cv = resumo["correcao"]["conjunto_principal_ciclo2"]
    s = resumo["correcao"]["sensibilidade_ciclo2"]
    cc = resumo["conferencias"]["marca_dos_candidatos"]
    am = resumo["amostras"]
    linhas = [
        ["células do ciclo 2 no conjunto principal", _int(cv["celulas_ciclo2_no_conjunto"]),
         _int(cv["celulas_ciclo2_no_conjunto"])],
        ["células com vaga imediata (conjunto principal)", _int(cv["celulas_com_vaga_imediata_19mar"]),
         _int(cv["celulas_com_vaga_imediata_13fev"])],
        ["vagas imediatas somadas", _n(cv["vagas_imediatas_total_19mar"], 0), _n(cv["vagas_imediatas_total_13fev"], 0)],
        ["células do conjunto só com vaga imediata", _int(s["celulas_19mar"]), _int(s["celulas_13fev"])],
        ["1ªs opções do ciclo 2 em célula com vaga imediata",
         f"{cc['primeiras_opcoes_com_vaga_imediata_19mar']} de {cc['primeiras_opcoes_ciclo2']}",
         f"{cc['primeiras_opcoes_com_vaga_imediata_13fev']} de {cc['primeiras_opcoes_ciclo2']}"],
    ]
    for chave, rot in (("2|principal|" + COND, "candidatos no conjunto principal, ciclo 2 (condicional)"),
                       ("2|principal|" + EXPL, "grupos de escolha do explodido, ciclo 2 (postos 1 e 2)"),
                       ("2|sensibilidade|" + COND, "candidatos no conjunto só com vaga imediata, ciclo 2"),
                       ("empilhado|sensibilidade|" + COND, "candidatos no conjunto só com vaga imediata, ciclos 1–3")):
        linhas.append([rot, _int(am[ANTIGA][chave]), _int(am[CORRIGIDA][chave])])
    ca = resumo["conferencias"]["quadro_1302_contra_a36"]
    cs = resumo["conferencias"]["sensibilidade_gravada_igual_a_regra"]
    return "\n".join([
        _tab(["Item", "Antiga (19/03/2026)", "Corrigida (13/02/2026)"], linhas), "",
        "- No conjunto principal, só mudam as duas covariáveis do tipo de vaga do ciclo 2; células, candidatos e "
        "conjuntos são os mesmos nas duas versões. No conjunto só com vaga imediata mudam as células e os candidatos "
        "(as células de reserva que viraram imediatas depois do resultado saem, com quem as escolheu).",
        f"- Conferências: a regra do script 12 aplicada ao quadro de 19/03 reproduz o conjunto só com vaga imediata "
        f"gravado em {cs['celulas']} células e a marca de {cc['marca_gravada_igual_ao_quadro_19mar']} de "
        f"{cc['linhas_ciclo2']} linhas de escolha do ciclo 2; o quadro de 13/02 bate com a leitura independente da "
        f"auditoria 36 em {ca['celulas_comparadas']} células ({ca['celulas_com_vagas_imediatas_diferentes']} "
        f"diferenças). Nada imputado."])


def _fc(r: pd.Series, casas: int = 4) -> str:
    """coef. [IC]; p"""
    if pd.isna(r["estimativa"]):
        return "— (não convergiu)"
    return f"{_n(r['estimativa'], casas)} {_ic(r['ic95_inf'], r['ic95_sup'], casas)}; {_peq(r['p'])}"


def _frc(r: pd.Series) -> str:
    if pd.isna(r["rc_por_5mil"]):
        return "—"
    return f"{_n(r['rc_por_5mil'], 2)} {_ic(r['rc_ic95_inf'], r['rc_ic95_sup'], 2)}"


def _q(a: pd.Series, c: pd.Series) -> str:
    if pd.isna(a["q_bky"]) and pd.isna(c["q_bky"]):
        return "—"
    return f"{_p(a['q_bky'])} → {_p(c['q_bky'])}"


def tabela_rb1(est: pd.DataFrame) -> str:
    linhas = []
    for ciclo, clusters in (("2", ("conjunto",)), ("empilhado", ("conjunto", "curso"))):
        for cl in clusters:
            if cl == "conjunto":
                a = _coef(est, ANTIGA, ciclo, COND, "principal", ESPEC)
                c = _coef(est, CORRIGIDA, ciclo, COND, "principal", ESPEC)
            else:
                a = _rob(est, ANTIGA, "cluster_curso", ciclo, modelo=COND, conjunto="principal", especificacao=ESPEC,
                         termo=B)
                c = _rob(est, CORRIGIDA, "cluster_curso", ciclo, modelo=COND, conjunto="principal",
                         especificacao=ESPEC, termo=B)
            pap = "principal" if ciclo == "2" else "secundária"
            linhas.append([ciclo, cl, f"CR1: coef. [IC]; p (G = {_int(c['g'])})", _fc(a), _fc(c), "—"])
            for an in (f"score_bootstrap_rademacher_cluster_{cl}", f"score_bootstrap_webb_cluster_{cl}"):
                a, c = _rob(est, ANTIGA, an, ciclo), _rob(est, CORRIGIDA, an, ciclo)
                linhas.append([ciclo, cl, f"{ROT_ANALISE[an]} ({pap})", _p(a["p"]), _p(c["p"]), _q(a, c)])
            an = f"cv3_cluster_{cl}"
            a, c = _rob(est, ANTIGA, an, ciclo), _rob(est, CORRIGIDA, an, ciclo)
            linhas.append([ciclo, cl, f"{ROT_ANALISE[an]} ({pap})", _fc(a), _fc(c), _q(a, c)])
            an = f"ic_inversao_score_rademacher_cluster_{cl}"
            a, c = _rob(est, ANTIGA, an, ciclo), _rob(est, CORRIGIDA, an, ciclo)
            linhas.append([ciclo, cl, ROT_ANALISE[an], _ic(a["ic95_inf"], a["ic95_sup"], 4),
                           _ic(c["ic95_inf"], c["ic95_sup"], 4), "—"])
    return "\n".join([
        "Especificação principal do E9 (logit condicional da 1ª opção, conjunto principal, spline linear, bolsa linear). "
        "Coeficiente por R$ 1 mil/mês. CR1 é o sanduíche com cluster (fator G/(G − 1)), a referência dos adendos 52c e "
        "52d. p do score bootstrap de Kline–Santos sob H0: coef. = 0 (Rademacher enumerado quando G ≤ 24; Webb "
        "sorteado). CV3 com IC e p pela t com G − 1 gl. IC por inversão do score bootstrap Rademacher. Só o ciclo 2 com "
        "cluster por conjunto é a principal; o empilhado é secundário e entra no BKY (última coluna).", "",
        _tab(["Ciclo", "Cluster", "Quantidade", "Antiga (19/03)", "Corrigida (13/02)", "q BKY (antiga → corrigida)"],
             linhas)])


def tabela_rb2(est: pd.DataFrame) -> str:
    linhas = []
    for ciclo in CICLOS_QUE_MUDAM:
        for v in VERSOES:
            g = lambda s: _rob(est, v, "placebo_cortes", ciclo, s)  # noqa: E731
            pp = g("p_posto")
            linhas.append([ciclo, QUADRO_DA_VERSAO[v], _int(g("n_placebos")["estimativa"]),
                           _n(g("t_real")["estimativa"], 2), _n(g("t_placebo_media")["estimativa"], 2),
                           _n(g("t_placebo_dp")["estimativa"], 2),
                           _n(g("fracao_abs_t_placebo_maior_que_1_96")["estimativa"], 3),
                           _n(g("abs_t_placebo_max")["estimativa"], 2),
                           _int(g("n_abs_t_placebo_maior_ou_igual_ao_real")["estimativa"]), _n(pp["estimativa"], 3),
                           _p(pp["q_bky"])])
    return "\n".join([
        "Degrau falso e nó no corte falso, com a bolsa verdadeira no modelo; cortes de 0,190 a 0,510 a cada 0,010, sem "
        "0,290–0,310 e 0,390–0,410 (grade do doc 42). t com EP cluster por conjunto; t real = t da bolsa na "
        "especificação principal. p por posto = (1 + nº de |t placebo| ≥ |t real|)/(1 + N); o menor possível com N "
        "placebos é 1/(1 + N). Os t de cada corte estão nas linhas `RB-2` de `RB_estimativas.csv`.", "",
        _tab(["Ciclo", "Quadro do ciclo 2", "N", "t real", "média do t placebo", "dp", "fração |t| > 1,96",
              "máx. |t| placebo", "nº |t placebo| ≥ |t real|", "p por posto", "q BKY"], linhas)])


def _tabela_modelos(est: pd.DataFrame, linhas_sel: list[tuple[str, dict]], com_ciclo: bool = True) -> str:
    linhas = []
    for ciclo in CICLOS_QUE_MUDAM:
        for rot, f in linhas_sel:
            try:
                a, c = _sel(est, ANTIGA, ciclo=ciclo, **f), _sel(est, CORRIGIDA, ciclo=ciclo, **f)
            except FalhaValidacao:
                continue
            if f.get("termo") == TESTE_DEGRAUS:
                linhas.append([ciclo, rot, f"dif. {_n(a['estimativa'], 3)}; {_peq(a['p'])}",
                               f"dif. {_n(c['estimativa'], 3)}; {_peq(c['p'])}", "—", "—"])
                continue
            linhas.append([ciclo, rot, _fc(a), _fc(c), _frc(c), _q(a, c)])
    return _tab(["Ciclo", "Especificação", "Antiga: coef. [IC]; p", "Corrigida: coef. [IC]; p",
                 "Razão de chances corrigida por +R$ 5 mil [IC]", "q BKY (antiga → corrigida)"], linhas)


def tabela_rb3(est: pd.DataFrame) -> str:
    sel = []
    for e in ["spline_cubico__bolsa_linear", "nos_cada_0050__spline_linear__bolsa_linear"] + \
             [f"janela_{h:04d}__spline_{s}__bolsa_linear" for h in E9.JANELAS_MIL for s in ("linear", "cubico")]:
        sel.append((ROT_ESPEC[e], dict(fonte="E9_estimativas", modelo=COND, conjunto="principal", especificacao=e,
                                       termo=B)))
    return "\n".join([
        "Logit condicional da 1ª opção, conjunto principal, bolsa linear. Janela: só células com |IVS − corte| ≤ h e "
        "candidatos com a 1ª opção nelas. Coeficiente por R$ 1 mil/mês; IC 95% e p com cluster por conjunto.", "",
        _tabela_modelos(est, sel)])


def _sel_variantes(conjunto: str, modelos: tuple[str, ...], incluir_principal: bool) -> list[tuple[str, dict]]:
    sel = []
    for modelo in modelos:
        for e, termos in (("spline_linear__bolsa_linear", (B,)), ("spline_quadratico__bolsa_linear", (B,)),
                          ("spline_linear__degraus_por_corte", ("degrau_0300", "degrau_0400", TESTE_DEGRAUS)),
                          ("spline_quadratico__degraus_por_corte", ("degrau_0300", "degrau_0400", TESTE_DEGRAUS))):
            if e == ESPEC and modelo == COND and not incluir_principal:
                continue
            for t in termos:
                rot = f"{ROT_MODELO[modelo]}, {ROT_ESPEC[e]}: {ROT_TERMO[t]}"
                sel.append((rot, dict(fonte="E9_estimativas", modelo=modelo, conjunto=conjunto, especificacao=e,
                                      termo=t)))
    return sel


def _tabela_curso(est: pd.DataFrame, conjuntos: tuple[str, ...], excluir_principal: bool) -> str:
    linhas = []
    sub = est[(est["versao"] == ANTIGA) & (est["analise"] == "cluster_curso") & est["conjunto"].isin(conjuntos)]
    for r in sub.itertuples(index=False):
        if excluir_principal and r.modelo == COND and r.conjunto == "principal" and r.especificacao == ESPEC:
            continue
        f = dict(fonte="E9_robustez_pos_auditoria", analise="cluster_curso", modelo=r.modelo, conjunto=r.conjunto,
                 especificacao=r.especificacao, termo=r.termo)
        a, c = _sel(est, ANTIGA, ciclo="empilhado", **f), _sel(est, CORRIGIDA, ciclo="empilhado", **f)
        linhas.append([f"{ROT_MODELO[r.modelo]}, {ROT_ESPEC[r.especificacao]}: {ROT_TERMO[r.termo]}", _int(c["g"]),
                       _fc(a), _fc(c), _frc(c), _q(a, c)])
    return _tab(["Especificação (empilhado)", "G (cursos)", "Antiga: coef. [IC]; p", "Corrigida: coef. [IC]; p",
                 "Razão de chances corrigida [IC]", "q BKY (antiga → corrigida)"], linhas)


def tabela_rb4(est: pd.DataFrame) -> str:
    n = []
    for ciclo in CICLOS_QUE_MUDAM:
        a = _coef(est, ANTIGA, ciclo, COND, "sensibilidade", "spline_quadratico__bolsa_linear")
        c = _coef(est, CORRIGIDA, ciclo, COND, "sensibilidade", "spline_quadratico__bolsa_linear")
        n.append(f"{'ciclo 2' if ciclo == '2' else 'ciclos 1–3'}: {_int(a['n_candidatos'])} → {_int(c['n_candidatos'])}")
    return "\n".join([
        "Logit condicional da 1ª opção no conjunto só com células de vaga imediata (o tipo de vaga define o conjunto e "
        f"os candidatos; candidatos, antiga → corrigida: {'; '.join(n)}). A especificação principal desse conjunto "
        "(VD-1 e VD-2) está no doc 57v e só é reproduzida aqui. Cada degrau vale +R$ 5 mil, e a razão de chances do "
        "degrau é exp(coef.). O Wald compara os dois degraus.", "",
        _tabela_modelos(est, _sel_variantes("sensibilidade", (COND,), False)), "",
        "CR1 com cluster por curso (empilhado; mesmo código do curso nos três ciclos):", "",
        _tabela_curso(est, ("sensibilidade",), False)])


def tabela_rb5(est: pd.DataFrame) -> str:
    return "\n".join([
        "Conjunto principal: logit condicional com spline quadrático e com degraus, e logit explodido (1ª > 2ª opção; o "
        "conjunto do posto 2 é o do curso da 2ª opção, sem a célula da 1ª quando os cursos coincidem) nas quatro "
        "especificações.", "",
        _tabela_modelos(est, _sel_variantes("principal", (COND, EXPL), False)), "",
        "CR1 com cluster por curso (empilhado; a especificação principal está em RB-1):", "",
        _tabela_curso(est, ("principal",), True)])


def texto_bky(est: pd.DataFrame, resumo: dict) -> str:
    linhas = []
    for v in VERSOES:
        f = est[(est["versao"] == v) & est["entra_bky"]]
        por = f.groupby("id_rb").agg(n=("q_bky", "size"), rej=("q_bky", lambda s: int((s < ALFA).sum())))
        linhas.append([QUADRO_DA_VERSAO[v], _int(len(f)), _int(int((f["q_bky"] < ALFA).sum()))] +
                      [f"{_int(por.loc[i, 'rej'])} de {_int(por.loc[i, 'n'])}" if i in por.index else "—"
                       for i in ("RB-1", "RB-2", "RB-3", "RB-4", "RB-5")])
    # Auditoria 54 (A1): q abaixo de p numa família em que quase todos os membros rejeitam.
    avisos = []
    for v in VERSOES:
        f = est[(est["versao"] == v) & est["entra_bky"]]
        sub = f[(f["p"] >= ALFA) & (f["q_bky"] < ALFA)]
        rots = [f"{r['id_rb']}, {'ciclo 2' if r['ciclo'] == '2' else 'empilhado'}, {rot_linha(r)} (p = {_n(r['p'], 3)}; q = {_p(r['q_bky'])})"
                for _, r in sub.iterrows()]
        avisos.append(f"com o quadro de {QUADRO_DA_VERSAO[v]}, {_int(int((f['q_bky'] < f['p']).sum()))} dos "
                      f"{_int(len(f))} membros têm q menor que o p, e {_int(len(sub))} têm p ≥ 0,05 e q < 0,05"
                      + (f": {_lista(rots)}" if rots else ""))
    return "\n".join([
        "Família BKY nova, uma por versão (decisão 9): toda linha secundária que testa H0: peso da bolsa = 0, com o p "
        "da própria linha. O q de cada linha está nas tabelas acima e em `q_bky` de `RB_estimativas.csv`; q = 0,001 é o "
        "piso da grade do algoritmo (Anderson, 2008). O q depende dos p de toda a família, e não só do p da linha.", "",
        _tab(["Quadro do ciclo 2", "Membros", "q < 0,05", "RB-1 (empilhado)", "RB-2", "RB-3", "RB-4", "RB-5"], linhas),
        "",
        "**Como ler o q (auditoria 54).** O BKY estima quantas hipóteses nulas são verdadeiras a partir da própria "
        "família. Quando quase todos os membros rejeitam, ele estima poucas nulas verdadeiras e afrouxa o limiar, e o q "
        "pode ficar abaixo do p. É o que acontece aqui: " + "; ".join(avisos) + ". A família junta várias inferências "
        "sobre o mesmo coeficiente (score bootstrap, CV3, cluster por curso), que rejeitam juntas e empurram o limiar "
        "para cima. Por isso a contagem de q < 0,05 não é uma contagem de achados independentes, e uma linha com p ≥ "
        "0,05 não passa a contar como significativa por causa do q. A leitura do §3 não usa o q."])


def tabela_mudancas(resumo: dict) -> str:
    linhas = []
    for m in resumo["mudancas"]:
        if not (m["muda_sinal"] or m["perde_significancia"] or m["ganha_significancia"] or m["sem_estimativa"]):
            continue
        o = []
        if m["muda_sinal"]:
            o.append("sinal")
        if m["perde_significancia"] or m["ganha_significancia"]:
            o.append(f"{m['criterio']}: {_sim(m['significativa_antiga'])} → {_sim(m['significativa_corrigida'])}")
        if m["sem_estimativa"]:
            o.append("sem estimativa numa versão")
        linhas.append([m["id_rb"], m["ciclo"], rot_linha(m),
                       f"{_n(m['estimativa_antiga'], 4)} → {_n(m['estimativa_corrigida'], 4)}", "; ".join(o)])
    n = len(resumo["mudancas"])
    if not linhas:
        return (f"Das {n} quantidades lidas (principal, membros do BKY, Wald dos degraus e inversões), nenhuma muda de "
                "sinal nem de significância pelo critério de cada linha. A lista completa, com o critério, está em "
                "`mudancas` de `RB_resumo.json`.")
    return "\n".join([
        f"Das {n} quantidades lidas (principal, membros do BKY, Wald dos degraus e inversões), só as abaixo mudam de "
        "sinal ou de significância pelo critério de cada linha (decisões 7 e 8); a lista completa, com o critério, está "
        "em `mudancas` de `RB_resumo.json`. A estimativa é o coeficiente (ou o p, nas linhas de p).", "",
        _tab(["Id", "Ciclo", "Linha", "Estimativa (antiga → corrigida)", "O que muda"], linhas), "",
        "Como ler: a regra conta qualquer troca de sinal, mesmo de uma estimativa perto de zero, e qualquer passagem "
        "do IC por zero, mesmo na borda; o IC de cada linha está nas seções 5.1 a 5.5. O IC do coeficiente exclui 0 "
        "exatamente quando o IC da razão de chances exclui 1, que é como o §3 do adendo e a resposta curta falam."])


def _lista(xs: list[str]) -> str:
    return "; ".join(xs)


def texto_resposta(est: pd.DataFrame, resumo: dict) -> str:
    lei = resumo["leitura"]
    a, c = lei[ANTIGA], lei[CORRIGIDA]
    t = []
    cr_a = _coef(est, ANTIGA, "2", COND, "principal", ESPEC)
    cr_c = _coef(est, CORRIGIDA, "2", COND, "principal", ESPEC)
    nums = (f"No ciclo 2, com o quadro de 13/02, o score bootstrap dá {_peq(c['p_score_rademacher'])} (Rademacher) e "
            f"{_peq(c['p_score_webb'])} (Webb), contra {_peq(a['p_score_rademacher'])} e {_peq(a['p_score_webb'])} com "
            f"o quadro de 19/03; o CV3 dá {_peq(c['p_cv3'])} e IC {_ic(*c['ic_cv3'], 4)} (antes, {_peq(a['p_cv3'])}, "
            f"IC {_ic(*a['ic_cv3'], 4)}); o IC por inversão do score vai de {_ic(*a['ic_inversao'], 4)} para "
            f"{_ic(*c['ic_inversao'], 4)}. O coeficiente da bolsa (CR1, adendo 52c) vai de {_n(cr_a['estimativa'], 4)} "
            f"para {_n(cr_c['estimativa'], 4)} por R$ 1 mil/mês.")
    def _quantos(n) -> str:
        n = int(n)
        return "nenhum corte falso tem" if n == 0 else ("1 corte falso tem" if n == 1 else f"{n} cortes falsos têm")

    na = int(a["RB2_n_placebos_com_abs_t_maior_ou_igual"])
    plac = (f"Nos cortes placebo (RB-2), {_quantos(c['RB2_n_placebos_com_abs_t_maior_ou_igual'])} |t| maior ou igual "
            f"ao do corte verdadeiro, e o p por posto é {_n(c['RB2_p_posto'], 3)}"
            f"{', o menor possível com essa grade' if c['RB2_corte_fora_da_distribuicao'] else ''} (com o quadro de "
            f"19/03: {'nenhum' if na == 0 else na}; p por posto {_n(a['RB2_p_posto'], 3)}).")
    # Auditoria 54 (A2): o p por posto não mostra a folga entre o corte verdadeiro e o maior corte falso.
    pg = {v: {s: _rob(est, v, "placebo_cortes", "2", s)["estimativa"]
              for s in ("t_real", "abs_t_placebo_max", "fracao_abs_t_placebo_maior_que_1_96", "n_placebos")}
          for v in VERSOES}
    folga = {v: abs(pg[v]["t_real"]) / pg[v]["abs_t_placebo_max"] for v in VERSOES}
    n196 = {v: int(round(pg[v]["fracao_abs_t_placebo_maior_que_1_96"] * pg[v]["n_placebos"])) for v in VERSOES}
    plac += (f" O p por posto não mede a folga: o maior |t| entre os cortes falsos vai de "
             f"{_n(pg[ANTIGA]['abs_t_placebo_max'], 2)} para {_n(pg[CORRIGIDA]['abs_t_placebo_max'], 2)}, contra |t| "
             f"real de {_n(abs(pg[ANTIGA]['t_real']), 2)} e {_n(abs(pg[CORRIGIDA]['t_real']), 2)}, e os cortes falsos com "
             f"|t| > 1,96 vão de {_int(n196[ANTIGA])} para {_int(n196[CORRIGIDA])} de {_int(pg[CORRIGIDA]['n_placebos'])}."
             + (" Com o quadro da inscrição, o corte verdadeiro ainda fica à frente de todos os falsos, mas por pouco."
                if folga[CORRIGIDA] < folga[ANTIGA] else ""))

    frase = "\"o ciclo 2 é robusto a poucos *clusters* e a placebos\""
    if c["regra"] == "MANTEM":
        t.append(f"**RB-1 e RB-2: a frase do doc 44 {frase} continua valendo com o tipo de vaga anterior à "
                 f"alocação.** {nums} {plac} Pela leitura pré-registrada (§3), os três p abaixo de 0,05 e o corte "
                 "verdadeiro fora da distribuição dos placebos, como no original, mantêm a frase.")
    elif c["regra"] == "REBAIXAR":
        t.append(f"**RB-1: a frase do doc 44 {frase} deve ser rebaixada para o ciclo 2.** {nums} Caiu (p ≥ 0,05): "
                 f"{_lista(c['inferencias_RB1_com_p_maior_ou_igual_0_05'])}. {plac} Pela leitura pré-registrada (§3), "
                 "a frase do doc 44 é rebaixada para o ciclo 2; editar o doc 44 é decisão do autor.")
    else:
        t.append(f"**RB-1 se mantém, RB-2 não: a frase do doc 44 {frase} vale só pela metade.** {nums} {plac} O §3 não "
                 "prevê este caso. A parte \"robusto a poucos clusters\" continua valendo; a parte \"a placebos\" não, "
                 "porque o corte verdadeiro já não fica fora da distribuição dos placebos. Isto é só relatado; mudar o "
                 "doc 44 é decisão do autor.")
    t.append(f"**Como no original?** Com o quadro de 19/03 a mesma regra dá `{a['regra']}`; com o de 13/02, "
             f"`{c['regra']}`.")
    r = lei["RB3_a_RB5"]
    cub_a = _coef(est, ANTIGA, "2", COND, "principal", "spline_cubico__bolsa_linear")
    cub_c = _coef(est, CORRIGIDA, "2", COND, "principal", "spline_cubico__bolsa_linear")
    mud = [m for m in resumo["mudancas"] if m["id_rb"] in ("RB-3", "RB-4", "RB-5") and m["criterio"].startswith("IC")]
    sinal = [f"{m['id_rb']}, ciclo {m['ciclo']}, {rot_linha(m)}" for m in mud if m["muda_sinal"]]
    perde = [f"{m['id_rb']}, ciclo {m['ciclo']}, {rot_linha(m)}" for m in mud if m["perde_significancia"]]
    ganha = [f"{m['id_rb']}, ciclo {m['ciclo']}, {rot_linha(m)}" for m in mud if m["ganha_significancia"]]
    s = (f"**RB-3 a RB-5 (forma funcional, janelas, só vaga imediata, explodido, quadrática e degraus).** Das "
         f"{r['linhas_lidas']} linhas de peso da bolsa lidas (ciclo 2 e empilhado), {r['nao_mudam']} não mudam de sinal "
         "nem perdem o IC que exclui 1. ")
    s += (f"Mudam de sinal: {_lista(sinal)}. " if sinal else "Nenhuma muda de sinal. ")
    s += (f"Perdem o IC que exclui 1: {_lista(perde)}. " if perde else "Nenhuma perde o IC que exclui 1. ")
    if ganha:
        s += f"Passam a ter IC que exclui 1: {_lista(ganha)}. "
    if r["sem_estimativa"]:
        s += f"Sem estimativa numa das versões: {_lista(r['sem_estimativa'])}. "
    s += ("Pela leitura pré-registrada, a leitura se apoia nas que não mudam. " if (sinal or perde) else "")
    def _fc_par(r: pd.Series) -> str:
        return f"{_n(r['estimativa'], 4)} {_ic(r['ic95_inf'], r['ic95_sup'], 4)} ({_peq(r['p'])})"

    s += (f"A ressalva do doc 44 sobre o spline cúbico no ciclo 2 continua de pé: o coeficiente vai de "
          f"{_fc_par(cub_a)} para {_fc_par(cub_c)}, e o IC "
          f"{'exclui' if _exclui(cub_c['ic95_inf'], cub_c['ic95_sup']) else 'contém'} zero na corrigida.")
    # Auditoria 54 (A3): todas as variantes cúbicas do ciclo 2 (sem janela e nas três janelas).
    cubs = ["spline_cubico__bolsa_linear"] + [f"janela_{h:04d}__spline_cubico__bolsa_linear" for h in E9.JANELAS_MIL]
    n_exc = {v: sum(bool(_exclui(r["ic95_inf"], r["ic95_sup"])) for r in
                    (_coef(est, v, "2", COND, "principal", e) for e in cubs)) for v in VERSOES}
    s += (f" Somando as janelas, há {_int(len(cubs))} especificações com spline cúbico no ciclo 2; o IC exclui zero em "
          f"{_int(n_exc[ANTIGA])} delas com o quadro de 19/03 e em {_int(n_exc[CORRIGIDA])} com o de 13/02. A regra do "
          "§3 confere a robustez a poucos clusters e a placebos, com o spline linear; não confere a robustez a uma forma "
          "mais flexível do IVS, que o doc 44 já tratava como ressalva.")
    t.append(s)
    emp = [(_rob(est, v, "score_bootstrap_rademacher_cluster_conjunto", "empilhado"),
            _rob(est, v, "placebo_cortes", "empilhado", "p_posto")) for v in VERSOES]
    t.append(f"**Empilhado (secundário).** p do score bootstrap Rademacher com cluster por conjunto: "
             f"{_p(emp[0][0]['p'])} → {_p(emp[1][0]['p'])}; p por posto contra os placebos: "
             f"{_n(emp[0][1]['estimativa'], 3)} → {_n(emp[1][1]['estimativa'], 3)}. O empilhado continua sendo uma "
             "média de ciclos heterogêneos (doc 42).")
    ressalvas = []
    if folga[CORRIGIDA] < folga[ANTIGA]:
        ressalvas.append("a folga contra os cortes falsos ficou menor")
    if not _exclui(cub_c["ic95_inf"], cub_c["ic95_sup"]):
        ressalvas.append("com uma curva mais flexível do IVS (spline cúbico) o efeito continua sem se separar do zero, "
                         "como o doc 44 já dizia")
    veredito = {"MANTEM": "Pela regra fixada antes das contas, a conclusão continua de pé: com o quadro da inscrição, "
                          "os testes para poucos grupos e o de cortes falsos dão o mesmo recado."
                          + (f" Mas {', e '.join(ressalvas)}." if ressalvas else ""),
                "REBAIXAR": "A conclusão precisa ser rebaixada: com o quadro da inscrição, parte dos testes para poucos "
                            "grupos deixa de excluir o zero.",
                "PLACEBO_NAO_CONFIRMA": "A conclusão fica pela metade: os testes para poucos grupos se mantêm, mas o "
                                        "corte verdadeiro deixa de se destacar dos cortes falsos."}[c["regra"]]
    t.append("**Em linguagem simples.** O doc 44 diz que o efeito da bolsa sobre a 1ª opção no ciclo 2 aguenta testes "
             "feitos para poucos grupos e para cortes falsos. Esses testes usavam um quadro de vagas arrumado depois do "
             "resultado. Aqui eles foram refeitos com o quadro que o candidato via na inscrição. " + veredito + " A bolsa aqui é o pacote do corte de IVS (bolsa e "
             "outras regras federais que mudam nos mesmos cortes), não a participação no PMM-E; o E9 não usa a origem "
             "do candidato, e onde ela aparece (P1) é preferência revelada, não efeito causal; tudo vale para quem se "
             "candidatou, dentro das vagas abertas.")
    return "\n\n".join(t)


def texto_figura(resumo: dict) -> str:
    f = resumo["figura"]
    return "\n".join([f"![{f['titulo']}](../../{f['arquivo']})", "",
                      f"Arquivo: `{f['arquivo']}`. Título: \"{f['titulo']}\".", "",
                      f"**Como ler.** {f['como_ler']}"])


PENDENTE = "*Pendente: preenchido pelo script depois do portão de reprodução.*"


def gerar_doc(est: pd.DataFrame | None, resumo: dict | None) -> str:
    """Doc 57y. Sem resumo (pré-registro), só cabeçalho, decisões (com inventário e sementes) e limites."""
    tem_portao = resumo is not None and "portao" in resumo
    ok = tem_portao and resumo["portao"]["status"] == "PASSOU" and est is not None
    Lh = [
        "# 57y. Robustez do E9 no ciclo 2 com o tipo de vaga do quadro de 13/02/2026 (adendo 52f)",
        "",
        "> **Gerado por** `scripts/rdd_bolsa/52_robustez_E9_ciclo2_quadro_1302.py` a partir de `output/rdd_bolsa/RB_*`; "
        "não editar à mão (o teste `tests/test_robustez_E9_ciclo2_quadro_1302.py` confere que este arquivo é igual ao "
        "gerado; `--atualizar-doc` o regrava das saídas).<br>",
        f"> **Adendo:** [`52f_adendo_robustez_E9_ciclo2_quadro_1302.md`](52f_adendo_robustez_E9_ciclo2_quadro_1302.md), "
        f"congelado em 27/10/2026 antes de rodar (commit `{COMMIT_ADENDO}`); SHA-256 em `adendo` de `RB_resumo.json`, "
        "conferido pelo teste. Origem: [doc 42](42_resultados_E9_escolha.md) (E9 e robustez pós-auditoria, protocolo "
        "[40](40_protocolo_multioutcome_rdd_bolsa.md), §12); adendos [52c](52c_adendo_vaga_imediata_ciclo2.md) (doc "
        "[57p](57p_escolha_vaga_imediata_c2.md)) e [52d](52d_adendo_sensibilidades_ciclo2_quadro_1302.md) (doc "
        "[57v](57v_sensibilidades_ciclo2_quadro_1302.md)).<br>",
        "> **Estatuto:** `ADENDO_52F_POS_RESULTADO`. As versões com o quadro de 19/03 (doc 42) e os adendos 52c, 52d e "
        "52e já tinham sido vistos; isto não é teste confirmatório novo. Toda linha de `RB_estimativas.csv` e o resumo "
        "têm `natureza_dos_dados = EMPIRICO`.<br>",
        "> **Motivo:** [auditoria 46](../auditorias/46_auditoria_sensibilidades_ciclo2.md), achados A1, A2 e A10: a "
        "frase do [doc 44](44_sintese_rdd_bolsa_multioutcome.md) de que o ciclo 2 é robusto a poucos clusters e a "
        "placebos se apoiava em robustezes ainda feitas com o quadro retificado de 19/03/2026, refeito depois do "
        "resultado preliminar ([auditoria 36](../auditorias/36_auditoria_dados_H1.md)).<br>",
        "> **Saídas:** `output/rdd_bolsa/RB_estimativas.csv`, `RB_resumo.json` e `RB_figuras/RB_antigo_corrigido.png`. "
        "As saídas `E9_*`, `VC_*`, `VD_*` e `VL_*` não são regravadas, e os docs 42, 44, 57, 57p e 57v não são "
        "editados.<br>",
        "> **Auditoria:** [auditoria 54](../auditorias/54_auditoria_robustez_E9_ciclo2.md), aprovada com correções de "
        "texto (folga dos placebos, spline cúbico e leitura do q do BKY); nenhum número mudou.",
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
    Lh += ["## 2. Portão de reprodução (RB-6)", ""]
    Lh += [*bloco("portao", texto_portao(resumo)), ""] if tem_portao else [PENDENTE, ""]
    Lh += ["## 3. Decisões de implementação", "", *bloco("decisoes", texto_decisoes()), ""]
    if ok:
        Lh += [
            "## 4. A correção do tipo de vaga no ciclo 2",
            "",
            *bloco("correcao", texto_correcao(resumo)),
            "",
            "## 5. Tabelas: antigo e corrigido lado a lado",
            "",
            "### 5.1 RB-1: inferência com poucos clusters (principal)",
            "",
            *bloco("rb1", tabela_rb1(est)),
            "",
            "### 5.2 RB-2: cortes placebo",
            "",
            *bloco("rb2", tabela_rb2(est)),
            "",
            "### 5.3 RB-3: forma funcional e janelas",
            "",
            *bloco("rb3", tabela_rb3(est)),
            "",
            "### 5.4 RB-4: conjunto só com vaga imediata",
            "",
            *bloco("rb4", tabela_rb4(est)),
            "",
            "### 5.5 RB-5: explodido, quadrática e degraus no conjunto principal",
            "",
            *bloco("rb5", tabela_rb5(est)),
            "",
            "### 5.6 BKY entre as secundárias",
            "",
            *bloco("bky", texto_bky(est, resumo)),
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
        "## 7. Limites",
        "",
        "- **Pós-resultado.** As versões com o quadro de 19/03 e as principais corrigidas dos adendos 52c e 52d já eram "
        "conhecidas. O adendo foi congelado antes de rodar, mas as robustezes corrigidas não são teste confirmatório "
        "novo.",
        "- **O quadro de 13/02 também é anúncio.** Ele mede o que estava publicado na inscrição, não a vaga que de fato "
        "seria preenchida; o remanejamento posterior fica fora do atributo, como deve ficar num controle "
        "pré-tratamento.",
        "- **O conjunto só com vaga imediata muda de tamanho.** Com o quadro de 13/02 ele perde as células de reserva "
        "que viraram imediatas depois do resultado e os candidatos que as escolheram; em RB-4 a comparação antiga × "
        "corrigida mistura a troca do atributo com a troca da amostra.",
        "- **Placebos têm piso.** Com a grade do doc 42, o menor p por posto possível é o de nenhum corte falso com |t| "
        "maior que o real; o teste não distingue efeitos maiores que isso. A fração de placebos com |t| alto mostra que "
        "o t com cluster por conjunto, com spline linear, superestima a precisão (doc 42).",
        "- **BKY novo.** O E9 é exploratório e não tinha família de correção múltipla; a família BKY deste adendo foi "
        "fixada na decisão 9, antes das estimativas, e junta inferências diferentes sobre o mesmo peso da bolsa.",
        "- **Escolha condicional.** Tudo vale para quem se candidatou, dentro das vagas abertas do seu curso e ciclo; o "
        "conjunto de escolha supõe que o candidato viu todas as células do curso; IIA do logit condicional; o "
        "explodido supõe ainda que a 2ª opção é a melhor do que sobra.",
        "- **Pacote do corte.** O peso da bolsa é identificado pelos saltos nos cortes de IVS, com o IVS em spline "
        "contínua; nos mesmos cortes mudam outras regras federais (auditoria 18). Não é efeito da participação no "
        "PMM-E nem do Agora Tem Especialistas.",
        "- **Origem não entra.** O E9 não usa a origem do candidato. Onde ela aparece (P1, adendos 52c e 52d), é "
        "preferência revelada, não efeito causal.",
        "- **Poucos conjuntos.** O cluster é o conjunto de escolha (curso × ciclo), e são poucos por ciclo; o número de "
        "cada linha está na coluna `g` de `RB_estimativas.csv`.",
    ]
    return "\n".join(Lh) + "\n"


# ---------------------------------------------------------------------------
# Execução
# ---------------------------------------------------------------------------

def entradas(d: dict) -> list[dict]:
    be = P1.bloco_entrada
    out = [
        be(ADENDO_MD, "adendo 52f (especificação, somente lido)", "repositório", "2026-10-27", "§1–§5", "documento",
           "-", "-"),
        be(ADENDO_52C, "adendo 52c (somente lido)", "repositório", "2026-10-26", "§1–§3", "documento", "-", "-"),
        be(ADENDO_52D, "adendo 52d (somente lido)", "repositório", "2026-10-26", "§1–§5", "documento", "-", "-"),
        be(PROTOCOLO_40, "protocolo 40 (E9, §12, §14, §15; somente lido)", "repositório", "2026-10-18",
           "§12, §14, §15", "documento", "-", "-"),
        be(VC.QUADRO_1302, "quadro do ciclo 2, retificado de 13/02/2026 (vigente na inscrição): versão corrigida",
           "Chamamento SGTES/MS nº 1/2026 (página oficial)", "2026-02-13", "1547 células CNES × curso", "célula",
           "CNES (7 dígitos) × código do curso", "coluna TOTAL de vagas imediatas"),
        be(VC.QUADRO_1903, "quadro do ciclo 2, retificado de 19/03/2026: conferência da versão antiga", "idem",
           "2026-03-19", "1547 células", "célula", "CNES × curso", "coluna TOTAL de vagas imediatas"),
        be(VC.A36_CELULAS, "leitura independente da auditoria 36: conferência do quadro de 13/02", "auditoria 36",
           "2026-10-26", "células dos ciclos 1–3", "célula", "cnes, cod_curso", "ciclo = 2"),
        be(E9_EST, "alvo do portão RB-6 (todas as linhas)", "script 16", "2026-10-18", "todas as linhas",
           "especificação × termo", ", ".join(CHAVE_EST), "-"),
        be(E9_EFE, "alvo do portão RB-6 (todas as linhas)", "script 16", "2026-10-18", "todas as linhas",
           "especificação × quantidade", ", ".join(CHAVE_EFE), "-"),
        be(E9_ROB, "alvo do portão RB-6 (todas as linhas)", "script 16", "2026-10-19", "todas as linhas",
           "análise × estatística", ", ".join(CHAVE_ROB), "-"),
        be(VC_CSV, "conferência do E9 principal (adendo 52c)", "script 42", "2026-10-26", "E9_2, E9_emp",
           "especificação × termo", "versao, chave_modelo, tipo_linha, termo", "coeficientes"),
        be(VD_CSV, "conferência do E9 só com vaga imediata (adendo 52d)", "script 48", "2026-10-26", "E9s_2, E9s_emp",
           "especificação × termo", "versao, chave_modelo, tipo_linha, termo", "coeficientes"),
        be(E9.DICIONARIO, "dicionário da tarefa B (SHA-256 das tabelas de escolha conferido)", "script 12",
           "2026-10-18", "-", "documento", "-", "-"),
        be(E9.ESCOLHAS, "escolhas dos candidatos (1ª e 2ª opção, marca de vaga imediata)", "tarefa B (script 12)",
           "resultados da 1ª chamada", f"{len(d['cand'])} linhas", "candidato × opção",
           "ciclo, id_candidato, opcao_rank", "postos 1 e 2"),
        be(E9.CONJ_PRINCIPAL, "conjunto de escolha principal; ciclo 2 com a covariável de 19/03", "tarefa B (script 12)",
           "quadros da 1ª chamada", f"{len(d['conj_p'])} células com IVS", "célula CNES × curso × ciclo",
           "ciclo, co_cnes_7d, cod_curso", "como no E9"),
        be(E9.CONJ_SENSIBILIDADE, "conjunto só com vaga imediata (versão antiga, conferida contra a regra)",
           "tarefa B (script 12)", "quadros da 1ª chamada", f"{len(d['conj_s'])} células com IVS",
           "célula CNES × curso × ciclo", "ciclo, co_cnes_7d, cod_curso", "tem_vaga_imediata == 1"),
        be(E9.IVS_OFICIAL, "IVS 2010 oficial (a08)", "Ipea (a08)", "Censo 2010", f"{len(d['ivs'])} municípios",
           "município", "co_ibge", "co_ibge, ivs"),
        be(E9.GRADES_EDITAIS, "grades faixa → bolsa dos editais (só mapeamento_regras_por_edital)", "a03",
           "editais 3/2025, 1/2026 e 28/2026", "3 faixas × 2 grades", "faixa", "faixa_1..3", "-"),
        be(E9.GRADE_2025, "grade 2025 da FAQ (conferência do mapa faixa → bolsa)", "a04", "FAQ do edital 3/2025",
           "3 faixas", "faixa", "faixa_atracao", "valor_anunciado_mensal_brl"),
        be(E9.PROTOCOLO_JSON, "protocolo congelado (E9)", "repositório", "2026-10-18", "-", "documento", "-", "-"),
    ]
    for s, papel_ in ((SCRIPT_16, "funções do E9 (importadas sem alteração, pelo 48 e pelo 42)"),
                      (SCRIPT_42, "funções do adendo 52c (importadas sem alteração, pelo 48)"),
                      (SCRIPT_48, "funções do adendo 52d (importadas sem alteração)")):
        out.append(be(s, papel_, "repositório", "-", "-", "código", "-", "-"))
    for s in SCRIPTS_CADEIA:
        out.append(be(s, "código importado pela cadeia (48 → 42 → 25c → 25 → 16, 17, 19, rdd_lib; 42 → 12)",
                      "repositório", "-", "-", "código", "-", "-"))
    return out


def remover_saidas_calculadas() -> None:
    for p in (OUT_CSV, FIG):
        if p.exists():
            p.unlink()
    if DIR_FIG.exists() and not any(DIR_FIG.iterdir()):
        DIR_FIG.rmdir()


def amostras(v: dict) -> dict:
    """Candidatos (posto 1) ou grupos de escolha por ciclo × conjunto × modelo, da especificação principal."""
    e = v["est"]
    e = e[(e["especificacao"] == ESPEC) & (e["termo"] == B)]
    out = {}
    for r in e.itertuples(index=False):
        out[f"{r.ciclo}|{r.conjunto}|{r.modelo}"] = int(r.n_grupos_escolha if r.modelo == EXPL else r.n_candidatos)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--atualizar-doc", action="store_true", help="só regrava o doc 57y a partir das saídas")
    ap.add_argument("--pre-registro", action="store_true",
                    help="grava o doc 57y só com as decisões e o inventário (antes de qualquer estimativa)")
    args = ap.parse_args(argv)
    if args.pre_registro:
        if OUT_RESUMO.exists():
            raise FalhaValidacao("RB_resumo.json já existe: o pré-registro só vale antes das estimativas")
        DOC.write_text(gerar_doc(None, None), encoding="utf-8")
        return 0
    if args.atualizar_doc:
        atualizar_doc()
        return 0
    t0 = time.time()

    def log(m: str) -> None:
        print(f"[{time.time() - t0:7.0f}s] {m}", flush=True)

    d = carregar()
    log("insumos do E9 carregados")
    prep = preparar(d)
    log("quadros conferidos; conjuntos e marcas corrigidos montados")
    resumo = {
        "etapa": "RB_robustez_E9_ciclo2_quadro_1302",
        "natureza_dos_dados": NATUREZA,
        "estatuto": ESTATUTO,
        "data_execucao": DATA_EXECUCAO,
        "script": rel(Path(__file__)),
        "adendo": {"arquivo": rel(ADENDO_MD), "sha256": sha256(ADENDO_MD), "commit_de_congelamento": COMMIT_ADENDO},
        "protocolos": {rel(p): sha256(p) for p in (PROTOCOLO_40, ADENDO_52C, ADENDO_52D)},
        "conferencias": {**prep["conferencias"], "insumos_do_E9": d["conferencias"]},
        "correcao": prep["correcao"],
        "inventario": [dict(zip(("id", "peca", "funcao_original", "ciclos", "como_o_quadro_entra"), x))
                       for x in INVENTARIO],
        "sementes": {"texto": SEMENTES, "semente_boot": E9.SEMENTE_BOOT, "n_reamostras": E9.N_REAMOSTRAS,
                     "g_max_enumeracao": E9.G_MAX_ENUMERACAO, "placebos_mil": list(E9.PLACEBOS_MIL),
                     "janelas_mil": list(E9.JANELAS_MIL), "nos_extras_mil": list(E9.NOS_EXTRAS_MIL)},
        "decisoes": DECISOES,
        "entradas": entradas(d),
        "integridade": ("nada simulado nem imputado; data/ só lido; IVS do a08 (o arquivo local de IVS da auditoria 16 "
                        "não é lido); só agregados em output/ (sem nome, CPF, CRM nem pseudônimo de candidato); saídas "
                        "E9_*, VC_*, VD_* e VL_* não regravadas"),
        "linguagem": ("escolha condicional a se candidatar, dentro das vagas abertas; a bolsa mede o pacote do corte e o "
                      "incentivo marginal; não é efeito da participação no PMM-E; a origem, onde aparece (P1), é "
                      "preferência revelada"),
        "tempo_execucao_nao_registrado": "fora do resumo para que duas execuções deem o mesmo hash",
    }
    va = estimar_versao(d["conj_p"], d["conj_s"], d["cand"], d["macros"], d["estratos"], log)
    port = portao(va, pd.read_csv(E9_EST, dtype={"ciclo": str}), pd.read_csv(E9_EFE, dtype={"ciclo": str}),
                  pd.read_csv(E9_ROB, dtype={"ciclo": str}))
    resumo["portao"] = port
    log(f"portão: {port['status']}")
    if port["status"] != "PASSOU":
        remover_saidas_calculadas()
        resumo["saidas"] = {}
        gravar_json(OUT_RESUMO, resumo)
        atualizar_doc()
        print(f"{port['status']}: nada corrigido (adendo 52f)", file=sys.stderr)
        return 3
    conf_a = conferir_contra_vc_vd(va, ANTIGA)

    vc = estimar_versao(prep["conj_p_c"], prep["conj_s_c"], prep["cand_c"], d["macros"], d["estratos"], log)
    conf_c = conferir_contra_vc_vd(vc, CORRIGIDA)
    resumo["conferencia_vc_vd"] = {ANTIGA: conf_a, CORRIGIDA: conf_c}
    resumo["ciclos_sem_mudanca"] = conferir_sem_mudanca(va, vc)
    resumo["amostras"] = {ANTIGA: amostras(va), CORRIGIDA: amostras(vc)}
    resumo["convergencia"] = {ANTIGA: va["convergencia"], CORRIGIDA: vc["convergencia"]}
    resumo["resumo_robustez_16"] = {ANTIGA: va["resumo_rob"], CORRIGIDA: vc["resumo_rob"]}
    est = montar(va, vc)
    est.to_csv(OUT_CSV, index=False, float_format="%.10g")
    est = ler_est()
    resumo["mudancas"] = mudancas(est)
    resumo["leitura"] = leitura(est)
    resumo["bky"] = {"familia": "decisão 9", "membros_por_versao": {v: int(est[(est["versao"] == v) &
                                                                               est["entra_bky"]].shape[0])
                                                                    for v in VERSOES}}
    resumo["figura"] = figura(est, resumo["leitura"])
    resumo["como_ler"] = {FIG.name: COMO_LER}
    resumo["saidas"] = {rel(OUT_CSV): sha256(OUT_CSV), rel(FIG): resumo["figura"]["sha256"]}
    gravar_json(OUT_RESUMO, resumo)
    atualizar_doc()
    log(f"gravado: {rel(OUT_CSV)}, {rel(OUT_RESUMO)}, {rel(FIG)}, {rel(DOC)}")
    return 0


def ler_est() -> pd.DataFrame:
    e = pd.read_csv(OUT_CSV, dtype={"ciclo": str, "analise": str, "especificacao": str})
    for c in ("analise", "modelo", "conjunto", "especificacao", "termo", "estatistica"):
        e[c] = e[c].fillna("")
    return e


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
