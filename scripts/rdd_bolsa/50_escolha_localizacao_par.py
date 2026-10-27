"""Adendo 52e: H2 com a localização do médico e da vaga fixada (efeito fixo do par de UFs e comparação local no corte).

Adendo congelado: `docs/06_execucao/52e_adendo_escolha_localizacao_par.md` (27/10/2026, antes de rodar), com estatuto
`ADENDO_52E_POS_RESULTADO`. Toda saída leva `natureza_dos_dados = EMPIRICO`.

Pedido do autor (27/10/2026)
----------------------------
"Rodar de novo a H1 fazendo pareamento pela localização da unidade e do médico, como se fosse um controle. O mesmo
vale para a H2." Na H2 (logit condicional da 1ª opção, P1), cada candidato já é comparado consigo mesmo; o que falta é
fixar o par de localizações: comparar só vagas que estão na mesma relação geográfica com o médico.

O que o script faz
------------------
1. **Portão (VL-5).** Reestima, com as funções dos scripts 25 e 25c importadas sem alteração (pelo 42), o M1 e o
   P1h-1 com o tipo de vaga antigo (contra `P1_estimativas.csv` e `P1h_magnitudes.csv`) e o M1 dos ciclos 1–3 e do
   ciclo 2, o D_UF, o M4 e os km do M1 com o tipo de vaga do ciclo 2 do quadro de 13/02/2026 (contra
   `VC_estimativas.csv` e `VD_estimativas.csv`). Diferença ≤ 1e−8 (relativa quando o valor gravado passa de 1 em
   módulo). Se falhar, a execução para (`FALHA_REPRODUCAO_<linha>`) e nada novo é estimado.
2. **VL-1 a VL-4.** Logit condicional da 1ª opção (nas referências, a função `estimar` do 25, sem alteração; nas
   linhas com par, `estimar_ef`, que repete o `estimar` e só muda o ponto de partida do Newton, nota de execução 1 do
   doc 57x) com efeito fixo de UF de origem × UF da vaga (VL-1), restrito às vagas a até 0,050 de um corte de IVS (VL-2), com efeito fixo de região de
   saúde de origem × UF da vaga (VL-3) e os km equivalentes de +R$ 5 mil (VL-4). Holm nas principais (VL-1 ciclos
   1–3, VL-1 ciclo 2, VL-2) e BKY nas secundárias. Score bootstrap de Kline–Santos (funções do 16) nas principais.
3. **Leitura do §3** por regra fixada no código (`regra_linha`, `leitura`), sem escolha depois de ver os números.

Contraste: pacote do corte e incentivo marginal da bolsa na escolha condicional a candidatar-se, dentro das vagas
abertas. Não é efeito da participação no PMM-E nem do Agora Tem Especialistas. A origem é preferência revelada, não
efeito causal.

Integridade
-----------
Só lê `data/` (o quadro do ciclo 2 de 13/02 e, pelas funções do 25, a CIR e os centroides) e `output/`; não escreve
em `data/`. O IVS 2010 oficial vem do a08; o arquivo local de IVS da auditoria 16 não é lido. Nada simulado nem
imputado. Sem nome, CPF, CRM ou pseudônimo de candidato em `output/`. As saídas `E9_*`, `P1_*`, `P1h_*`, `VC_*` e
`VD_*` não são regravadas.

Uso
---
    python3 scripts/rdd_bolsa/50_escolha_localizacao_par.py
    python3 scripts/rdd_bolsa/50_escolha_localizacao_par.py --atualizar-doc   # só regrava o doc 57x
    python3 scripts/rdd_bolsa/50_escolha_localizacao_par.py --pre-registro    # doc 57x só com as decisões
"""

from __future__ import annotations

import argparse
import gc
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
VC = _importar(DIR_RDD / "42_escolha_vaga_imediata_c2.py", "vaga_imediata_c2_para_vl")
P1H = VC.P1H
P1 = VC.P1
E9 = VC.E9
L = P1.L

# ---------------------------------------------------------------------------
# Caminhos
# ---------------------------------------------------------------------------

SCRIPT_42 = DIR_RDD / "42_escolha_vaga_imediata_c2.py"
SCRIPT_25 = DIR_RDD / "25_escolha_dap.py"
SCRIPT_25C = DIR_RDD / "25c_magnitudes_P1h.py"
SCRIPT_16 = DIR_RDD / "16_estimar_E9_escolha.py"
ADENDO_MD = ROOT / "docs" / "06_execucao" / "52e_adendo_escolha_localizacao_par.md"
ADENDO_52C = VC.ADENDO_MD
ADENDO_52D = ROOT / "docs" / "06_execucao" / "52d_adendo_sensibilidades_ciclo2_quadro_1302.md"
PROTOCOLO_52 = VC.PROTOCOLO_52
PROTOCOLO_52B = VC.PROTOCOLO_52B
DOC = ROOT / "docs" / "06_execucao" / "57x_resultados_escolha_localizacao_par.md"
OUT = ROOT / "output" / "rdd_bolsa"
P1_EST = P1.OUT_EST
P1H_CSV = P1H.OUT_CSV
VC_CSV = VC.OUT_CSV
VD_CSV = OUT / "VD_estimativas.csv"
OUT_CSV = OUT / "VL_estimativas.csv"
OUT_RESUMO = OUT / "VL_resumo.json"
DIR_FIG = OUT / "VL_figuras"
FIG = DIR_FIG / "VL_razao_chances_e_km.png"

# ---------------------------------------------------------------------------
# Parâmetros (adendo 52e e protocolos de origem; nenhum é dado)
# ---------------------------------------------------------------------------

DATA_EXECUCAO = "2026-10-27"
NATUREZA = "EMPIRICO"
ESTATUTO = "ADENDO_52E_POS_RESULTADO"
COMMIT_ADENDO = "243160d"
TOL_REPRODUCAO = 1e-8
ALFA = 0.05
Z95 = float(stats.norm.ppf(0.975))
PASSO_BOLSA = 5.0
H_JANELA_MIL = P1.H_RDD                 # 50 = 0,050 (§2, VL-2; convenção do A3)
CORTES_MIL = tuple(P1.CORTES)           # (300, 400)
LIMITE_JANELAS_MIL = 350                # célula com IVS até 0,350 fica na janela do corte 0,300
EMPILHADO = P1.EMPILHADO
B = P1.TERMO_BOLSA
DIST = P1.TERMO_DIST
LOGDIST = P1.TERMO_LOGDIST
ANTIGA, CORRIGIDA = VC.ANTIGA, VC.CORRIGIDA
TERMO_INTERCEPTO = "intercepto_corte_0400"
PREFIXO_EF = "ef_par_"
ABSORVIDOS = ("mesma_uf",)              # função do par; as macrorregiões da vaga também saem (prefixo macro_)
FRACAO_PERTO_DE_1 = 0.5                 # §3, regra fixada: |log RC| ≤ metade do |log RC| do M1
FATOR_IC_LARGO = 2.0                    # §3, regra fixada: IC (em log) pelo menos 2 vezes mais largo que o do M1
AMOSTRA = "P1 (G1 com origem)"
FAMILIA_HOLM = "VL principais (adendo 52e, §2): VL-1 ciclos 1–3, VL-1 ciclo 2, VL-2 ciclos 1–3"
FAMILIA_BKY = "VL secundárias (adendo 52e, §2): VL-2 ciclo 2, VL-3, VL-1 com log da distância"

# Linhas estimadas. ef: "nenhum" (M1), "uf_vaga" (M4), "uf_origem" (UF de origem × UF da vaga), "cir_origem" (região
# de saúde de origem × UF da vaga).
ESPECS: dict[str, dict] = {
    "M1_emp": {"id_vl": "VL-5", "papel": "referencia", "ciclo": EMPILHADO, "ef": "nenhum", "janela": False,
               "dist": "linear", "referencia": None},
    "M1_c2": {"id_vl": "VL-5", "papel": "referencia", "ciclo": "2", "ef": "nenhum", "janela": False, "dist": "linear",
              "referencia": None},
    "M4_emp": {"id_vl": "apoio", "papel": "referencia_figura", "ciclo": EMPILHADO, "ef": "uf_vaga", "janela": False,
               "dist": "linear", "referencia": None},
    "M4_c2": {"id_vl": "apoio", "papel": "referencia_figura", "ciclo": "2", "ef": "uf_vaga", "janela": False,
              "dist": "linear", "referencia": None},
    "VL1_emp": {"id_vl": "VL-1", "papel": "principal", "ciclo": EMPILHADO, "ef": "uf_origem", "janela": False,
                "dist": "linear", "referencia": "M1_emp"},
    "VL1_c2": {"id_vl": "VL-1", "papel": "principal", "ciclo": "2", "ef": "uf_origem", "janela": False,
               "dist": "linear", "referencia": "M1_c2"},
    "VL2_emp": {"id_vl": "VL-2", "papel": "principal", "ciclo": EMPILHADO, "ef": "uf_origem", "janela": True,
                "dist": "linear", "referencia": "M1_emp"},
    "VL2_c2": {"id_vl": "VL-2", "papel": "secundaria", "ciclo": "2", "ef": "uf_origem", "janela": True,
               "dist": "linear", "referencia": "M1_c2"},
    "VL3_VL1_emp": {"id_vl": "VL-3", "papel": "secundaria", "ciclo": EMPILHADO, "ef": "cir_origem", "janela": False,
                    "dist": "linear", "referencia": "M1_emp"},
    "VL3_VL1_c2": {"id_vl": "VL-3", "papel": "secundaria", "ciclo": "2", "ef": "cir_origem", "janela": False,
                   "dist": "linear", "referencia": "M1_c2"},
    "VL3_VL2_emp": {"id_vl": "VL-3", "papel": "secundaria", "ciclo": EMPILHADO, "ef": "cir_origem", "janela": True,
                    "dist": "linear", "referencia": "M1_emp"},
    "VL3_VL2_c2": {"id_vl": "VL-3", "papel": "secundaria", "ciclo": "2", "ef": "cir_origem", "janela": True,
                   "dist": "linear", "referencia": "M1_c2"},
    "VL1log_emp": {"id_vl": "VL-1 (log da distância)", "papel": "secundaria", "ciclo": EMPILHADO, "ef": "uf_origem",
                   "janela": False, "dist": "log", "referencia": "M1_emp"},
    "VL1log_c2": {"id_vl": "VL-1 (log da distância)", "papel": "secundaria", "ciclo": "2", "ef": "uf_origem",
                  "janela": False, "dist": "log", "referencia": "M1_c2"},
}
PRINCIPAIS = ("VL1_emp", "VL1_c2", "VL2_emp")
SECUNDARIAS = ("VL2_c2", "VL3_VL1_emp", "VL3_VL1_c2", "VL3_VL2_emp", "VL3_VL2_c2", "VL1log_emp", "VL1log_c2")
COM_SCORE = PRINCIPAIS + ("M1_emp", "M1_c2")
COM_KM = ("M1_emp", "M1_c2", "VL1_emp", "VL1_c2")
ROTULO = {
    "M1_emp": "M1 (base), ciclos 1–3", "M1_c2": "M1 (base), ciclo 2",
    "M4_emp": "M4 (efeito fixo de UF da vaga), ciclos 1–3", "M4_c2": "M4 (efeito fixo de UF da vaga), ciclo 2",
    "VL1_emp": "VL-1 (par de UFs), ciclos 1–3", "VL1_c2": "VL-1 (par de UFs), ciclo 2",
    "VL2_emp": "VL-2 (local no corte, par de UFs), ciclos 1–3", "VL2_c2": "VL-2 (local no corte, par de UFs), ciclo 2",
    "VL3_VL1_emp": "VL-3: VL-1 com região de saúde de origem, ciclos 1–3",
    "VL3_VL1_c2": "VL-3: VL-1 com região de saúde de origem, ciclo 2",
    "VL3_VL2_emp": "VL-3: VL-2 com região de saúde de origem, ciclos 1–3",
    "VL3_VL2_c2": "VL-3: VL-2 com região de saúde de origem, ciclo 2",
    "VL1log_emp": "VL-1 com log da distância, ciclos 1–3", "VL1log_c2": "VL-1 com log da distância, ciclo 2",
}
ROTULO_EF = {"nenhum": "nenhum (macrorregião da vaga e mesma UF como no M1)", "uf_vaga": "UF da vaga (M4)",
             "uf_origem": "UF de origem × UF da vaga", "cir_origem": "região de saúde de origem × UF da vaga"}

COLUNAS = ["natureza_dos_dados", "estatuto", "id_vl", "papel", "chave_modelo", "modelo", "ciclo", "efeito_fixo",
           "janela_corte", "distancia", "tipo_linha", "termo", "estimativa", "ep_cluster_conjunto", "ep_mle",
           "ep_cluster_candidato", "ic95_inf", "ic95_sup", "p", "p_t_g_menos_1", "p_mle", "p_score_rademacher",
           "p_score_webb", "li95_unilateral", "p_unilateral", "ic95_fieller_inf", "ic95_fieller_sup", "entra_holm",
           "familia_holm", "p_holm", "p_holm_score_rademacher", "entra_bky", "familia_bky", "q_bky", "referencia",
           "g_conjuntos", "g_candidatos", "n_candidatos", "n_linhas_candidato_celula", "n_conjuntos",
           "n_efeitos_fixos", "status", "nota"]

COMO_LER = ("Cada linha é um modelo da escolha da 1ª opção; o ponto é a estimativa e a barra, o IC 95% com cluster por "
            "conjunto de escolha (curso × ciclo). À esquerda, a razão de chances por +R$ 5 mil de bolsa anunciada, em "
            "escala log: acima de 1, a vaga com bolsa maior é mais escolhida; a linha vertical marca 1 (nenhum peso). "
            "Em cada bloco (ciclos 1–3 e ciclo 2): M1 é o modelo base (distância, mesma UF, mesma região e mesmo "
            "município de origem, macrorregião da vaga); M4 troca a macrorregião por efeito fixo de UF da vaga; VL-1 "
            "compara só vagas da mesma UF vistas por médicos da mesma UF de origem (efeito fixo do par de UFs); VL-2 faz "
            "o mesmo só com vagas a até 0,050 de um corte de IVS. À direita, quantos km a menos de distância pesam "
            "como +R$ 5 mil de bolsa, no M1 e no VL-1 (IC pelo método delta). Tudo é escolha condicional a se "
            "candidatar, dentro das vagas abertas; a bolsa mede o pacote do corte, e a origem é preferência revelada, "
            "não efeito causal.")


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
    {"data": "2026-10-27", "item": "Como o efeito fixo do par de UFs entra no logit condicional",
     "situacao": "O §2 pede efeito fixo de UF de origem × UF da vaga; no logit condicional só entra o que varia entre "
                 "as alternativas do mesmo candidato.",
     "resolucao": "A UF de origem é constante dentro do conjunto de cada candidato. Por isso o efeito fixo do par vira, "
                  "para cada UF de origem, um indicador de UF da vaga próprio daquela origem: uma coluna por par (UF de "
                  "origem, UF da vaga) presente no desenho, menos uma base por componente de pares de cada origem "
                  "(pares ligados por candidatos que veem os dois; em geral, uma componente por origem; depois da "
                  "retirada da decisão 2 pode haver mais), porque dentro de cada candidato os indicadores da sua "
                  "componente somam 1. A base é o par da própria UF (origem = vaga) quando ele está na componente e tem "
                  "escolha; senão, o par mais escolhido da componente (empate: menor código). Saem os termos "
                  "do M1 que o par absorve: `mesma_uf` (função do par) e as quatro macrorregiões da vaga (função da "
                  "UF da vaga). Ficam todos os outros termos do M1: bolsa linear, spline do IVS, vaga imediata e log das "
                  "vagas imediatas, log da população, capital, estratos, distância por 100 km, mesma região de saúde e "
                  "mesmo município. Estima-se com a função `estimar` do script 25, sem alteração (Newton, sanduíche por "
                  "conjunto e por candidato), com os indicadores como colunas; coluna sem variação dentro de nenhum "
                  "candidato é omitida, como no 25, e, se a matriz não tiver posto completo, a linha fica "
                  "NAO_CONVERGIU, sem forçar nada. Os coeficientes dos pares não são relatados um a um (só a contagem). "
                  "O D_UF do P1h não é identificado e fica relatado da especificação base (VL-5), como diz o §2."},
    {"data": "2026-10-27", "item": "Pares de UF sem nenhuma escolha e efeitos fixos separados",
     "situacao": "Num par (origem, UF da vaga) que nenhum candidato daquela origem escolheu, a máxima verossimilhança "
                 "do efeito fixo vai a menos infinito e o Newton não converge. O mesmo acontece, para mais infinito, "
                 "com um conjunto S de pares de uma origem em que todo candidato que vê algum par de S escolheu em S "
                 "e algum deles também vê pares fora de S (conferido antes de estimar: acontece em algumas linhas, "
                 "sobretudo no VL-3).",
     "resolucao": "No limite, a verossimilhança dos demais parâmetros é a do conjunto sem as alternativas que ficam com "
                  "probabilidade zero (é a mesma retirada de efeitos fixos separados que fixest e ppmlhdfe fazem). "
                  "Então: (a) saem as alternativas dos pares sem escolha; (b) para cada par p, S é o fecho de p "
                  "(junta-se o par escolhido por cada candidato que vê S até não mudar); se algum candidato que vê S "
                  "também vê pares fora de S, esses candidatos perdem as alternativas fora de S e continuam escolhendo "
                  "dentro de S; (c) candidato que fica com uma só alternativa sai (não contribui para nada). Repete-se "
                  "até não mudar. A escolha observada nunca sai do conjunto. Alternativas e candidatos retirados são "
                  "contados por linha no resumo e no doc; nenhuma escolha é imputada."},
    {"data": "2026-10-27", "item": "Pares de UF sem variação de bolsa",
     "situacao": "Num par em que todas as vagas que um candidato vê têm a mesma bolsa, o par não informa o peso da "
                 "bolsa.",
     "resolucao": "Esses pares ficam no modelo: identificam os controles (distância, mesma região, mesmo município, "
                  "spline, porte, tipo de vaga) e o próprio efeito fixo, e não enviesam o peso da bolsa. Mas não "
                  "contribuem para ele. O doc relata, por linha: pares no desenho; pares com escolha (os que ficam); "
                  "pares com variação de bolsa (há um candidato daquela origem que vê, dentro do par, vagas com bolsas "
                  "diferentes); candidatos com variação de bolsa dentro de algum par do seu conjunto (são os que "
                  "identificam o peso da bolsa); e candidatos cuja 1ª opção está num par com variação no seu "
                  "conjunto."},
    {"data": "2026-10-27", "item": "Distância no VL-1",
     "situacao": "O parêntese do VL-1 no §2 diz \"log da distância\", mas o M1 do doc 57a (script 25) usa a distância "
                 "linear por 100 km, e o VL-4 pede os km equivalentes \"como no P1h\", que só existem com o termo linear.",
     "resolucao": "Leitura mais próxima dos scripts 25 e 42: o VL-1 é o M1, com a distância linear por 100 km. Como "
                  "sensibilidade (secundária, no BKY), o VL-1 com log(1 + km) no lugar da distância, como no M2 do "
                  "P1, nos ciclos 1–3 e no ciclo 2."},
    {"data": "2026-10-27", "item": "Ciclo 2 e referência de comparação",
     "situacao": "O §1 manda usar o tipo de vaga do ciclo 2 do quadro de 13/02/2026 (52c); o §3 compara com o M1.",
     "resolucao": "Todas as linhas novas usam o conjunto do P1 com a correção do ciclo 2 (função `corrigir` do 42). O "
                  "VL-1 do ciclo 2 é o M1 da amostra do ciclo 2 (como o M5 do P1) com o efeito fixo do par. A "
                  "referência do VL-1 e do VL-2 dos ciclos 1–3 é o M1 corrigido dos ciclos 1–3; a do ciclo 2 é o M5 "
                  "do ciclo 2 corrigido (o \"M1 do ciclo 2\"), ambos do `VC_estimativas.csv`."},
    {"data": "2026-10-27", "item": "Janela e spline do IVS no VL-2",
     "situacao": "O §2 diz: vagas com |IVS − corte| ≤ 0,050, os dois cortes juntos, com intercepto por corte, mesmo "
                 "efeito fixo.",
     "resolucao": "Como na robustez de janelas do E9 (doc 42, script 16): ficam as células com |s − 300| ≤ 50 ou "
                  "|s − 400| ≤ 50, em milésimos de IVS (s = IVS oficial × 1000 arredondado, como no E9), e os "
                  "candidatos cuja 1ª opção está nessas células. O spline do IVS é o mesmo do M1 (inclinação, mudança "
                  "de inclinação em 0,300 e em 0,400, contínuo), restrito à janela. O intercepto por corte é "
                  "`intercepto_corte_0400` = 1 se s > 350 (a célula com IVS exatamente 0,350 fica na janela do corte "
                  "0,300); no logit condicional um intercepto comum não existe, então um indicador basta. A bolsa "
                  "continua linear. Mesmo efeito fixo do par e mesma retirada de pares sem escolha (decisão 2). O VL-2 "
                  "dos ciclos 1–3 é a principal; o do ciclo 2 é secundário (entra no BKY e na figura)."},
    {"data": "2026-10-27", "item": "VL-3",
     "situacao": "O §2 pede VL-1 e VL-2 com efeito fixo de região de saúde de origem × UF da vaga.",
     "resolucao": "Região de saúde (CIR do TabNet, o mesmo mapa do script 25) do município de origem do candidato × "
                  "UF da vaga, com a mesma construção da decisão 1 (base por região: o par da UF da própria região, "
                  "se tiver escolha). `mesma_uf` e as macrorregiões saem; `mesma_regiao_saude` fica (varia dentro do "
                  "par da UF da própria região). Quatro linhas: VL-1 e VL-2, ciclos 1–3 e ciclo 2."},
    {"data": "2026-10-27", "item": "Inferência e score bootstrap",
     "situacao": "O §2 pede cluster por conjunto de escolha como no 52c e, com poucos clusters, score bootstrap de "
                 "Rademacher como no doc 42.",
     "resolucao": "Principal: sanduíche CR1 por conjunto de escolha (curso × ciclo), fator G/(G − 1), p bilateral de "
                  "H0: β = 0 pela normal, como no 52c; Holm nas três principais com esse p (como no script 42). Score "
                  "bootstrap de Kline–Santos como no doc 42 (funções do script 16): ajuste restrito sob H0: β = 0 (a "
                  "coluna da bolsa sai; com β0 = 0 não há offset), scores e informação no ponto restrito com todos os "
                  "efeitos fixos, score da bolsa projetado fora dos demais parâmetros, somado por conjunto; Rademacher "
                  "por enumeração completa se G ≤ 24, senão 199.999 sorteios com a semente do script 16; Webb também. "
                  "Calculado nas três principais e nas referências (M1 dos ciclos 1–3 e do ciclo 2). Holm também nos p "
                  "do Rademacher, como coluna de robustez; se as duas leituras divergirem, o doc diz. O IC por inversão "
                  "do score não é calculado (cada ponto exige reajustar centenas de efeitos fixos); o IC relatado é o "
                  "CR1."},
    {"data": "2026-10-27", "item": "Famílias de testes",
     "situacao": "O §2 pede Holm entre as principais e BKY nas secundárias.",
     "resolucao": "Holm: VL-1 ciclos 1–3, VL-1 ciclo 2 e VL-2 ciclos 1–3 (p bilateral do β). BKY: VL-2 ciclo 2, as "
                  "quatro linhas do VL-3 e as duas do VL-1 com log da distância (p bilateral do β). O VL-4 (km "
                  "equivalentes) é descritivo, com IC pelo método delta e por Fieller e sem teste, como o P1h-2. As "
                  "referências (VL-5) e o M4 não entram em família."},
    {"data": "2026-10-27", "item": "Comparação com o M1",
     "situacao": "O §3 lê se a razão de chances do VL é \"parecida\" com a do M1; os dois modelos são estimados nos "
                  "mesmos dados (o VL num subconjunto dos candidatos e das alternativas do M1), e os dois β são "
                  "correlacionados.",
     "resolucao": "Para cada principal, a diferença do log da razão de chances (VL − referência) tem IC pelo sanduíche "
                  "conjunto: as funções de influência do β de cada modelo, somadas por conjunto de escolha (zero no "
                  "conjunto que só um dos modelos tem), com o mesmo fator G/(G − 1). É descritiva, fora do Holm, e "
                  "ajuda a ler o §3."},
    {"data": "2026-10-27", "item": "Leitura do §3 por regra",
     "situacao": "O §3 não fixa o que é \"parecida\", \"perto de 1\" nem \"IC muito largo\".",
     "resolucao": "Para cada principal, contra a sua referência: (1) se o IC 95% da razão de chances do VL contém 1 e "
                  "|log RC do VL| ≤ metade do |log RC da referência|: CAI_PARA_PERTO_DE_1 (2ª linha do §3); (2) senão, "
                  "se a RC do VL está dentro do IC da referência e a da referência dentro do IC do VL: PARECIDA_COM_M1 "
                  "(1ª linha); (3) senão, fora do §3 e só relatado: MAIOR_QUE_M1, SINAL_OPOSTO (IC que exclui 1 do "
                  "outro lado) ou MENOR_QUE_M1_SEM_CHEGAR_A_1. Para o VL-2, IC_MUITO_LARGO quando a largura do IC em "
                  "log é pelo menos 2 vezes a da referência (3ª linha). VL-4: a frase \"+R$ 5 mil pesa como X km a "
                  "menos de distância, comparando vagas da mesma UF\", e, se o IC do β contém 0, o doc diz que o IC dos "
                  "km também contém. Leitura geral: todas as principais PARECIDA_COM_M1 → a localização não explica o "
                  "peso da bolsa; algum VL-1 CAI_PARA_PERTO_DE_1 → explica em parte; outro caso → misto, linha a "
                  "linha."},
    {"data": "2026-10-27", "item": "Portão (VL-5) e tolerância",
     "situacao": "O §4 pede reproduzir VL-5 contra `VC_*`/`P1_*` (≤ 1e−8) antes de qualquer conta nova.",
     "resolucao": "Antes de qualquer linha nova: M1 e P1h-1 com o tipo de vaga antigo contra `P1_estimativas.csv` e "
                  "`P1h_magnitudes.csv`; M1 dos ciclos 1–3, M1 do ciclo 2 (M5) e D_UF corrigidos contra "
                  "`VC_estimativas.csv`; M4 dos ciclos 1–3 e km do M1 corrigidos contra `VD_estimativas.csv` (são as "
                  "referências da figura). Diferença absoluta ≤ 1e−8 se o valor gravado tem módulo até 1, relativa "
                  "se maior (os CSV têm 10 algarismos significativos), como na decisão 6 do 52d. Falhou, para. O M4 do "
                  "ciclo 2 não existe gravado: é estimado como apoio da figura, sem teste."},
    {"data": "2026-10-27", "item": "Números do doc 57x",
     "situacao": "O pedido do autor exige números só em blocos gerados.",
     "resolucao": "Todo número de resultado do 57x vem de `VL_*` por `--atualizar-doc`, entre marcadores "
                  "`<!-- VL:... -->`; o teste confere o doc contra o gerado e que não há número de resultado fora dos "
                  "blocos."},
]


# ---------------------------------------------------------------------------
# Desenho: amostra, janela, pares e retirada de pares sem escolha
# ---------------------------------------------------------------------------

def subconjunto(conj: pd.DataFrame, r1: pd.DataFrame, ciclo: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Conjunto e 1ªs opções de um ciclo, como o M5 do script 25 (ciclos 1–3: tudo)."""
    if ciclo == EMPILHADO:
        return conj, r1
    k = int(ciclo)
    return conj[conj["ciclo"] == k].reset_index(drop=True), r1[r1["ciclo"] == k]


def na_janela(s_mil) -> np.ndarray:
    s = np.asarray(s_mil, dtype=float)
    dentro = np.zeros(len(s), dtype=bool)
    for c in CORTES_MIL:
        dentro |= np.abs(s - c) <= H_JANELA_MIL
    return dentro


def restringir_janela(conj: pd.DataFrame, r1: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Células a até 0,050 de um corte e candidatos com a 1ª opção nelas (regra das janelas do E9, script 16)."""
    dentro = na_janela(conj["s_mil"])
    cj = conj[dentro].reset_index(drop=True)
    chaves = pd.MultiIndex.from_frame(cj[["ciclo", "co_cnes_7d", "cod_curso"]])
    no_jan = pd.MultiIndex.from_frame(r1[["ciclo", "co_cnes_7d", "cod_curso"]]).isin(chaves)
    diag = {"celulas_no_conjunto": int(len(conj)), "celulas_na_janela": int(dentro.sum()),
            "candidatos": int(len(r1)), "candidatos_com_1a_opcao_na_janela": int(no_jan.sum())}
    return cj, r1[no_jan], diag


def rotulos_par(D: dict, dados: dict, ef: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Rótulo da origem (por linha), UF da vaga (por linha) e UF de origem (por linha)."""
    org = D["grupos"]["co_ibge_origem"].astype(str).to_numpy()
    uf_o = np.array([x[:2] for x in org], dtype=object)
    if ef == "uf_origem":
        o = uf_o
    elif ef == "cir_origem":
        cir = dados["mapa_cir"].reindex(org)
        if cir.isna().any():
            raise FalhaValidacao("origem sem região de saúde na amostra do P1")
        o = np.array([f"cir{c}" for c in cir.astype(str)], dtype=object)
    else:
        raise ValueError(ef)
    v = D["conj"]["co_ibge"].astype(str).str[:2].to_numpy(dtype=object)[D["cel"]]
    return o[D["grp"]], v, uf_o[D["grp"]]


def conjuntos_separados(grp_l: np.ndarray, par_l: np.ndarray, orig_g: np.ndarray, par_esc: np.ndarray,
                        grupos: np.ndarray) -> dict[int, set]:
    """Separação em que o efeito fixo de um conjunto S de pares de uma origem vai a +infinito (decisão 2): todo
    candidato daquela origem que vê algum par de S escolheu em S, e algum deles vê pares fora de S. Para cada par p, S
    é o fecho de p (junta-se o par escolhido de cada candidato que toca S até não mudar). Devolve, por grupo afetado,
    os pares que ele mantém (interseção dos S com vazamento que ele toca)."""
    gp = pd.DataFrame({"g": grp_l, "p": par_l}).drop_duplicates()
    pares_do_grupo = gp.groupby("g")["p"].agg(lambda s: frozenset(s.tolist())).to_dict()
    grupos_do_par: dict[int, list[int]] = gp.groupby("p")["g"].agg(list).to_dict()
    escolhido = dict(zip(grupos.tolist(), par_esc.tolist()))
    origem = dict(zip(grupos.tolist(), orig_g.tolist()))
    pares_por_origem: dict = {}
    for p, gs in grupos_do_par.items():
        pares_por_origem.setdefault(origem[gs[0]], []).append(p)
    manter: dict[int, set] = {}
    for _, pares in sorted(pares_por_origem.items(), key=lambda x: str(x[0])):
        for p in sorted(pares):
            S = {p}
            while True:
                T = {g for q in S for g in grupos_do_par[q]}
                C = {escolhido[g] for g in T}
                if C <= S:
                    break
                S |= C
            vaza = [g for g in T if not pares_do_grupo[g] <= S]
            for g in vaza:
                manter[g] = (manter[g] & S) if g in manter else set(S)
    return manter


def filtrar_pares(D: dict, par: np.ndarray, orig: np.ndarray) -> tuple[np.ndarray, np.ndarray, dict]:
    """Decisão 2, até não mudar: (a) saem as alternativas de pares sem escolha; (b) nos conjuntos de pares cujo
    efeito fixo vai a +infinito (`conjuntos_separados`), saem as alternativas fora do conjunto dos candidatos que o
    tocam; (c) sai o candidato com uma só alternativa. `par` e `orig` são códigos inteiros por linha (origem do
    candidato). Devolve (linhas mantidas, grupos mantidos, contagens)."""
    n_g = len(D["starts"])
    grp, esc = D["grp"], D["esc"]
    manter = np.ones(len(par), dtype=bool)
    grupo_ok = np.ones(n_g, dtype=bool)
    cont = {"iteracoes": 0, "alternativas_retiradas_par_sem_escolha": 0, "alternativas_retiradas_por_separacao": 0,
            "candidatos_com_alternativas_retiradas_por_separacao": 0}
    afetados: set = set()
    while True:
        cont["iteracoes"] += 1
        antes = manter.copy()
        com_escolha = np.zeros(int(par.max()) + 1, dtype=bool)
        com_escolha[par[esc[grupo_ok]]] = True
        novo = manter & com_escolha[par] & grupo_ok[grp]
        cont["alternativas_retiradas_par_sem_escolha"] += int((manter & grupo_ok[grp] & ~com_escolha[par]).sum())
        idx = np.flatnonzero(novo)
        gs = np.flatnonzero(grupo_ok)
        sep = conjuntos_separados(grp[idx], par[idx], orig[esc[gs]], par[esc[gs]], gs)
        if sep:
            fora = np.zeros(len(par), dtype=bool)
            for g, S in sep.items():
                a, m = D["starts"][g], D["tam"][g]
                linhas = np.arange(a, a + m)
                fora[linhas] = novo[linhas] & ~np.isin(par[linhas], list(S))
            cont["alternativas_retiradas_por_separacao"] += int(fora.sum())
            afetados |= {int(g) for g in sep}
            novo &= ~fora
        tam = np.bincount(grp[novo], minlength=n_g)
        novo_g = grupo_ok & (tam >= 2)
        novo &= novo_g[grp]
        if np.array_equal(novo, antes) and np.array_equal(novo_g, grupo_ok):
            break
        manter, grupo_ok = novo, novo_g
    if not manter[esc[grupo_ok]].all():
        raise FalhaValidacao("escolha retirada do conjunto")
    cont["candidatos_com_alternativas_retiradas_por_separacao"] = len(afetados & set(np.flatnonzero(grupo_ok).tolist()))
    return manter, grupo_ok, cont


def recortar_desenho(D: dict, manter: np.ndarray, grupo_ok: np.ndarray) -> dict:
    """Desenho do script 25 só com as linhas e os grupos mantidos (linhas contíguas por grupo preservadas)."""
    idx = np.flatnonzero(manter)
    nova_pos = np.full(len(manter), -1, dtype=np.int64)
    nova_pos[idx] = np.arange(len(idx))
    gmap = np.full(len(grupo_ok), -1, dtype=np.int64)
    gmap[grupo_ok] = np.arange(int(grupo_ok.sum()))
    grp = gmap[D["grp"][idx]]
    if (grp < 0).any() or (np.diff(grp) < 0).any():
        raise FalhaValidacao("recorte do desenho quebrou a contiguidade dos grupos")
    tam = np.bincount(grp, minlength=int(grupo_ok.sum()))
    starts = np.concatenate([[0], np.cumsum(tam)[:-1]]).astype(np.int64)
    esc = nova_pos[D["esc"][grupo_ok]]
    if (esc < 0).any() or not ((esc >= starts) & (esc < starts + tam)).all():
        raise FalhaValidacao("escolha fora do próprio grupo depois do recorte")
    Dn = {"cel": D["cel"][idx], "grp": grp, "starts": starts, "esc": esc.astype(np.int64),
          "grupos": D["grupos"][grupo_ok].reset_index(drop=True), "tam": tam, "conj": D["conj"]}
    for k in ("dist_km", "mesmo_municipio", "mesma_uf", "mesma_regiao_saude"):
        if k in D:
            Dn[k] = D[k][idx]
    return Dn


def componentes_de_pares(grp_l: np.ndarray, par_l) -> dict:
    """Componentes conexas dos pares ligados por candidatos que veem os dois (union-find). Cada componente precisa da
    sua base: dentro de cada candidato os indicadores da componente somam 1."""
    pai: dict = {}

    def raiz(x):
        while pai[x] != x:
            pai[x] = pai[pai[x]]
            x = pai[x]
        return x

    for p in set(par_l):
        pai[p] = p
    gp = pd.DataFrame({"g": grp_l, "p": list(par_l)}).drop_duplicates()
    for _, ps in gp.groupby("g")["p"]:
        ps = ps.tolist()
        r0 = raiz(ps[0])
        for q in ps[1:]:
            rq = raiz(q)
            if rq != r0:
                pai[rq] = r0
    return {p: raiz(p) for p in pai}


def colunas_ef(o_lin: np.ndarray, v_lin: np.ndarray, uf_o_lin: np.ndarray, esc: np.ndarray,
               grp_l: np.ndarray) -> tuple[np.ndarray, list[str], dict]:
    """Indicadores de par (origem, UF da vaga) menos uma base por componente de pares de cada origem (decisão 1).
    Devolve a coluna de cada linha (−1 = base), os nomes e, por componente, (par base, se é o par da própria UF)."""
    par = pd.Series(o_lin, dtype=object) + "|" + pd.Series(v_lin, dtype=object)
    cont = par.iloc[esc].value_counts()
    pares = sorted(set(par))
    comp = componentes_de_pares(grp_l, par.to_numpy())
    por_comp: dict[str, list[str]] = {}
    for p in pares:
        por_comp.setdefault(comp[p], []).append(p)
    uf_da_origem = pd.Series(uf_o_lin, index=o_lin).groupby(level=0).first()
    if (pd.Series(uf_o_lin, index=o_lin).groupby(level=0).nunique() > 1).any():
        raise FalhaValidacao("origem com mais de uma UF")
    bases: dict[str, tuple[str, bool]] = {}
    for c, lst in sorted(por_comp.items()):
        o = lst[0].split("|")[0]
        if any(p.split("|")[0] != o for p in lst):
            raise FalhaValidacao("componente com pares de origens diferentes")
        propria = f"{o}|{uf_da_origem[o]}"
        if propria in lst and cont.get(propria, 0) > 0:
            bases[c] = (propria, True)
        else:
            bases[c] = (sorted(lst, key=lambda p: (-int(cont.get(p, 0)), p))[0], False)
    eh_base = {b for b, _ in bases.values()}
    nomes = [p for p in pares if p not in eh_base]
    pos = {p: i for i, p in enumerate(nomes)}
    col = np.array([pos.get(p, -1) for p in par], dtype=np.int64)
    rotulos = [PREFIXO_EF + p.replace("|", "_") for p in nomes]
    return col, rotulos, bases


def contagens(D: dict, par: np.ndarray, rotulos_par_lin: np.ndarray) -> dict:
    """Quem identifica o peso da bolsa (decisão 3), no desenho final."""
    bolsa = D["conj"]["bolsa_mil"].to_numpy(dtype=float)[D["cel"]]
    df = pd.DataFrame({"grp": D["grp"], "par": par, "bolsa": bolsa})
    var = df.groupby(["grp", "par"])["bolsa"].nunique() > 1
    var = var[var]
    gr_var = np.unique(var.index.get_level_values(0))
    pares_var = np.unique(var.index.get_level_values(1))
    par_esc = par[D["esc"]]
    chave_esc = pd.MultiIndex.from_arrays([np.arange(len(D["starts"])), par_esc])
    esc_em_var = int(chave_esc.isin(var.index).sum())
    rot = pd.Series(rotulos_par_lin)
    origens = rot.str.split("|").str[0]
    return {"pares_no_modelo": int(len(np.unique(par))), "pares_com_variacao_de_bolsa": int(len(pares_var)),
            "pares_sem_variacao_de_bolsa": int(len(np.unique(par)) - len(pares_var)),
            "origens_no_modelo": int(origens.nunique()),
            "origens_com_algum_par_com_variacao": int(origens[np.isin(par, pares_var)].nunique()),
            "candidatos_no_modelo": int(len(D["starts"])),
            "candidatos_com_variacao_de_bolsa_em_algum_par": int(len(gr_var)),
            "candidatos_com_1a_opcao_em_par_com_variacao": esc_em_var,
            "alternativas_no_modelo": int(len(D["cel"]))}


def desenho_ef(D0: dict, dados: dict, ef: str) -> tuple[dict, dict, dict]:
    """Aplica a decisão 2 a um desenho do script 25 e devolve (desenho recortado, efeitos fixos, diagnóstico)."""
    o, v, uf_o = rotulos_par(D0, dados, ef)
    rot = pd.Series(o, dtype=object) + "|" + pd.Series(v, dtype=object)
    cod, uniq = pd.factorize(rot)
    cod_o, _ = pd.factorize(pd.Series(o, dtype=object))
    pares_desenho = int(len(uniq))
    manter, grupo_ok, cont = filtrar_pares(D0, cod, cod_o)
    D = recortar_desenho(D0, manter, grupo_ok)
    idx = np.flatnonzero(manter)
    o, v, uf_o, cod_m = o[idx], v[idx], uf_o[idx], cod[idx]
    col, nomes, bases = colunas_ef(o, v, uf_o, D["esc"], D["grp"])
    diag = {"pares_no_desenho": pares_desenho, "pares_com_escolha": int(len(np.unique(cod_m))),
            "pares_retirados": pares_desenho - int(len(np.unique(cod_m))),
            "alternativas_no_desenho": int(len(D0["cel"])), "alternativas_retiradas": int((~manter).sum()),
            "alternativas_retiradas_par_sem_escolha": cont["alternativas_retiradas_par_sem_escolha"],
            "alternativas_retiradas_por_separacao": cont["alternativas_retiradas_por_separacao"],
            "candidatos_com_alternativas_retiradas_por_separacao":
                cont["candidatos_com_alternativas_retiradas_por_separacao"],
            "candidatos_no_desenho": int(len(D0["starts"])), "candidatos_retirados_uma_so_alternativa":
                int((~grupo_ok).sum()), "iteracoes_da_retirada": cont["iteracoes"],
            "colunas_de_efeito_fixo": len(nomes),
            "componentes_com_base": len(bases), "bases_no_par_da_propria_uf": int(sum(propria for _, propria in
                                                                                  bases.values()))}
    diag.update(contagens(D, cod_m, rot.to_numpy()[idx]))
    par_lin = rot.to_numpy()[idx]
    comp = componentes_de_pares(D["grp"], par_lin)
    base_de = {p: bases[comp[p]][0] for p in comp}
    nome_par = {PREFIXO_EF + p.replace("|", "_"): p for p in comp}
    return D, {"col": col, "nomes": nomes, "bases": bases, "par_lin": par_lin, "base_de": base_de,
               "nome_par": nome_par}, diag


def matriz_vl(D: dict, dv: dict, espec: dict, ef: dict | None) -> pd.DataFrame:
    """Matriz do M1 (ou M2, com log da distância; ou M4) com os ajustes do adendo."""
    if espec["ef"] == "uf_vaga":
        return P1.matriz_modelo(D, dv, "M4")
    X = P1.matriz_modelo(D, dv, "M2" if espec["dist"] == "log" else "M1")
    if espec["ef"] == "nenhum":
        return X
    X = X.drop(columns=[c for c in X.columns if c in ABSORVIDOS or c.startswith("macro_")])
    if espec["janela"]:
        X[TERMO_INTERCEPTO] = (D["conj"]["s_mil"].to_numpy(dtype=float)[D["cel"]] > LIMITE_JANELAS_MIL).astype(float)
    Z = np.zeros((len(X), len(ef["nomes"])))
    m = ef["col"] >= 0
    Z[np.flatnonzero(m), ef["col"][m]] = 1.0
    return pd.concat([X, pd.DataFrame(Z, columns=ef["nomes"], index=X.index)], axis=1)


# ---------------------------------------------------------------------------
# Estimação (função `estimar` do 25, sem alteração) e score bootstrap (funções do 16)
# ---------------------------------------------------------------------------

def score_bootstrap(r: dict, termo: str = B) -> dict:
    """Score bootstrap de Kline e Santos (2012) para H0: β = 0, como no `score_efetivo_por_cluster` do script 16, com
    a verossimilhança do 25 (com β0 = 0 o ajuste restrito é o modelo sem a coluna da bolsa).

    O Newton restrito parte da estimativa irrestrita sem a bolsa: partindo de zero, o 1º passo leva os efeitos fixos
    de pares com pouquíssimas escolhas a valores muito negativos e a informação fica numericamente singular. O ponto de
    partida não muda o máximo (a log-verossimilhança é côncava)."""
    A, D = r["_A"], r["_D"]
    k = r["termos"].index(termo)
    outros = [j for j in range(A.shape[1]) if j != k]
    fit = P1.ajustar_cl(np.ascontiguousarray(A[:, outros]), D, theta0=np.asarray(r["theta"])[outros])
    if not fit["convergiu"]:
        return {"status": "NAO_CONVERGIU", "nota": "ajuste restrito sob H0 não convergiu"}
    theta = np.zeros(A.shape[1])
    theta[outros] = fit["theta"]
    est = P1._estat(theta, A, D)
    info, S = est["info"], est["scores"]
    a = np.linalg.solve(info[np.ix_(outros, outros)], info[outros, k])
    st = S[:, k] - S[:, outros] @ a
    _, idx = np.unique(D["grupos"]["cluster_conjunto"].to_numpy(), return_inverse=True)
    sc = np.bincount(idx, weights=st)
    p_r, met_r, n_r = E9.p_score_bootstrap(sc, "rademacher")
    p_w, met_w, n_w = E9.p_score_bootstrap(sc, "webb")
    return {"status": "EXECUTADO", "g": int(len(sc)), "t_score": float(sc.sum() / math.sqrt((sc ** 2).sum())),
            "p_rademacher": p_r, "metodo_rademacher": met_r, "n_rademacher": n_r, "p_webb": p_w,
            "metodo_webb": met_w, "n_webb": n_w, "iteracoes_ajuste_restrito": fit["iteracoes"],
            "partida_ajuste_restrito": "estimativa irrestrita sem a bolsa"}


def contracao_ef(v0: np.ndarray, D: dict, par_lin: np.ndarray, max_it: int = 5000, tol: float = 1e-10) -> tuple[
        dict, int]:
    """Constantes de par que igualam escolhas previstas e observadas em cada par, com a utilidade `v0` fixa
    (contração de escala iterativa: α_p += log O_p − log E_p(α)). Só serve de ponto de partida do Newton."""
    cod, uniq = pd.factorize(pd.Series(par_lin, dtype=object))
    n_p = len(uniq)
    O = np.bincount(cod[D["esc"]], minlength=n_p).astype(float)
    if (O <= 0).any():
        raise FalhaValidacao("par sem escolha no desenho final")
    alfa = np.zeros(n_p)
    st, grp = D["starts"], D["grp"]
    it = 0
    for it in range(1, max_it + 1):
        v = v0 + alfa[cod]
        vmax = np.maximum.reduceat(v, st)
        ex = np.exp(v - vmax[grp])
        p = ex / np.add.reduceat(ex, st)[grp]
        E = np.bincount(cod, weights=p, minlength=n_p)
        delta = np.log(O) - np.log(E)
        alfa += delta
        if np.max(np.abs(delta)) < tol:
            break
    return dict(zip(uniq, alfa)), it


def estimar_ef(X: pd.DataFrame, D: dict, ef: dict, *, modelo: str, ciclo: str, amostra: str) -> dict:
    """A função `estimar` do script 25 com ponto de partida para o Newton (nota de execução 1 do doc 57x).

    Mesmas etapas do 25: colunas sem variação omitidas, posto da matriz centrada no grupo, `ajustar_cl` (Newton com
    meio-passo e o mesmo critério de parada), covariâncias de MV e sanduíche por conjunto e por candidato. A única
    diferença é o `theta0`: partindo de zero, o Newton com centenas de indicadores de par levava pares com
    pouquíssimas escolhas a valores muito negativos e a informação ficava numericamente singular. A partida é (i) os
    termos que não são de par, ajustados sem os indicadores, e (ii) as constantes de par da `contracao_ef` com essa
    utilidade fixa, normalizadas pela base de cada componente. A log-verossimilhança é côncava e a matriz tem posto
    completo: o máximo é único e não depende da partida."""
    omit = P1.colunas_sem_variacao(X, D)
    X = X.drop(columns=omit)
    A = X.to_numpy(dtype=float)
    G = D["grupos"]
    termos = list(X.columns)
    base = {"modelo": modelo, "ciclo": ciclo, "amostra": amostra, "termos": termos, "omitidas": omit,
            "n_candidatos": int(G.loc[G["posto"] == 1, "id_candidato"].nunique()), "n_grupos": int(len(G)),
            "n_linhas": int(len(A)), "n_conjuntos": int(G["cluster_conjunto"].nunique())}
    media = np.add.reduceat(A, D["starts"], axis=0) / D["tam"][:, None]
    posto = int(np.linalg.matrix_rank(A - media[D["grp"]]))
    del media
    if posto < A.shape[1]:
        return {**base, "ok": False, "status": "NAO_CONVERGIU", "nota": f"X sem posto completo ({posto} < {A.shape[1]})"}
    k_n = [j for j, t in enumerate(termos) if not t.startswith(PREFIXO_EF)]
    theta0 = np.zeros(A.shape[1])
    try:
        f0 = P1.ajustar_cl(np.ascontiguousarray(A[:, k_n]), D)
        if f0["convergiu"]:
            theta0[k_n] = f0["theta"]
        alfa, it_c = contracao_ef(A[:, k_n] @ theta0[k_n], D, ef["par_lin"])
        for j, t in enumerate(termos):
            if t.startswith(PREFIXO_EF):
                p = ef["nome_par"][t]
                theta0[j] = alfa[p] - alfa[ef["base_de"][p]]
        fit = P1.ajustar_cl(A, D, theta0=theta0)
    except (np.linalg.LinAlgError, FloatingPointError) as erro:
        return {**base, "ok": False, "status": "NAO_CONVERGIU", "nota": f"estimação falhou ({type(erro).__name__})"}
    if not fit["convergiu"]:
        return {**base, "ok": False, "status": "NAO_CONVERGIU", "nota": "Newton–Raphson não convergiu",
                "iteracoes": fit["iteracoes"]}
    info_inv = np.linalg.inv(fit["info"])
    Vc, Gc = E9.covariancia_cluster(info_inv, fit["scores"], G["cluster_conjunto"].to_numpy())
    Vk, Gk = E9.covariancia_cluster(info_inv, fit["scores"], G["cluster_candidato"].to_numpy())
    nota = P1._juntar("omitidas por não variarem dentro de nenhum grupo: " + ", ".join(omit) if omit else "")
    return {**base, "ok": True, "status": "EXECUTADO", "nota": nota, "theta": fit["theta"], "ll": fit["ll"],
            "iteracoes": fit["iteracoes"], "V_mle": info_inv, "V_conj": Vc, "V_cand": Vk, "G_conj": Gc, "G_cand": Gk,
            "grad_max": float(np.max(np.abs(fit["grad"]))), "decremento_final": fit["decremento_final"],
            "iteracoes_contracao": it_c, "partida": "termos sem par ajustados sem os indicadores + contração",
            "_A": A, "_D": D, "_scores": fit["scores"], "_info": fit["info"]}


def ajustar(chave: str, X: pd.DataFrame, D: dict, log=print, com_score: bool = True, ef: dict | None = None) -> dict:
    e = ESPECS[chave]
    if ef is None:
        r = P1.estimar(X, D, modelo=chave, ciclo=e["ciclo"], amostra=AMOSTRA)
    else:
        r = estimar_ef(X, D, ef, modelo=chave, ciclo=e["ciclo"], amostra=AMOSTRA)
    r["n_efeitos_fixos"] = int(sum(1 for t in r["termos"] if t.startswith(PREFIXO_EF)))
    if r["ok"]:
        kb = r["termos"].index(B)
        infl = r["_scores"] @ r["V_mle"][:, kb]
        cl = D["grupos"]["cluster_conjunto"].astype(str).to_numpy()
        r["infl_bolsa"] = {str(k): float(v) for k, v in pd.Series(infl).groupby(cl).sum().items()}
        if com_score and chave in COM_SCORE:
            r["score_bootstrap"] = score_bootstrap(r)
    for k in ("_A", "_D", "_scores", "_info"):
        r.pop(k, None)
    log(f"{chave}: ok={r['ok']} it={r.get('iteracoes')} termos={len(r['termos'])} candidatos={r['n_candidatos']} "
        f"grad_max={r.get('grad_max')}")
    return r


def estimar_linha(chave: str, dados: dict, conj_p1: pd.DataFrame, log=print) -> tuple[dict, dict]:
    e = ESPECS[chave]
    dv = {**dados, "conj_p1": conj_p1}
    conj, r1 = subconjunto(conj_p1, dados["r1_p1"], e["ciclo"])
    diag: dict = {}
    if e["janela"]:
        conj, r1, diag["janela"] = restringir_janela(conj, r1)
    D0 = P1.montar_desenho(conj, r1, None, dv)
    if e["ef"] in ("uf_origem", "cir_origem"):
        D, ef, diag["identificacao"] = desenho_ef(D0, dados, e["ef"])
        del D0
    else:
        D, ef = D0, None
    X = matriz_vl(D, dv, e, ef)
    r = ajustar(chave, X, D, log, ef=ef)
    del X, D
    gc.collect()
    return r, diag


# ---------------------------------------------------------------------------
# Portão de reprodução (VL-5)
# ---------------------------------------------------------------------------

def _dif_rel(a, b) -> float:
    """Diferença absoluta (|b| ≤ 1) ou relativa (|b| > 1); NaN só casa com NaN (decisão 12)."""
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


def _ep(V: np.ndarray) -> np.ndarray:
    return np.sqrt(np.diag(V))


def comparar_coef(r: dict, g: pd.DataFrame, col_coef: str) -> tuple[bool, dict]:
    """Coeficientes e os três EP de todos os termos, na mesma ordem."""
    if not r["ok"] or list(g["termo"]) != list(r["termos"]):
        return False, {}
    return True, {"coef": _dif_rel(r["theta"], g[col_coef]),
                  "ep_cluster_conjunto": _dif_rel(_ep(r["V_conj"]), g["ep_cluster_conjunto"]),
                  "ep_mle": _dif_rel(_ep(r["V_mle"]), g["ep_mle"]),
                  "ep_cluster_candidato": _dif_rel(_ep(r["V_cand"]), g["ep_cluster_candidato"])}


def comparar_linha(nova: dict, g: pd.Series, colunas: list[str]) -> dict:
    return {c: _dif_rel([nova[c]], [g[c]]) for c in colunas}


def portao(res: dict, p1_est: pd.DataFrame, p1h: pd.DataFrame, vc: pd.DataFrame, vd: pd.DataFrame,
           tol: float = TOL_REPRODUCAO) -> dict:
    linhas, falha = [], None

    def registrar(nome: str, ok: bool, difs: dict, contra: str) -> None:
        nonlocal falha
        passou = bool(ok and difs and all(x <= tol for x in difs.values()))
        linhas.append({"linha": nome, "contra": contra, "casou": bool(ok), **{f"dif_max_{k}": x for k, x in difs.items()},
                       "passou": passou})
        if not passou and falha is None:
            falha = f"FALHA_REPRODUCAO_{nome}"

    r = res["M1_antiga"]
    g = p1_est[(p1_est["modelo"] == "M1") & (p1_est["ciclo"] == EMPILHADO) & (p1_est["tipo_linha"] == "coeficiente")]
    ok, d = comparar_coef(r, g, "coef")
    registrar("M1_antiga", ok, d, "P1_estimativas.csv (M1, ciclos 1–3, coeficientes)")
    h = p1h[p1h["id_linha"] == "P1h-1"]
    ok = r["ok"] and len(h) == 1
    d = comparar_linha(P1H.linha_dif_uf("M1", r, "P1h-1", "primaria"), h.iloc[0],
                       ["estimativa", "ep_cluster_conjunto", "ep_mle", "ep_cluster_candidato", "ic95_inf", "ic95_sup",
                        "li95_unilateral", "p_unilateral"]) if ok else {}
    registrar("P1h-1_antiga", ok, d, "P1h_magnitudes.csv (P1h-1)")
    vcc = vc[vc["versao"] == CORRIGIDA]
    for chave, chave_vc in (("M1_emp", "M1"), ("M1_c2", "M5_2")):
        r = res[chave]
        g = vcc[(vcc["chave_modelo"] == chave_vc) & (vcc["tipo_linha"] == "coeficiente")]
        ok, d = comparar_coef(r, g, "estimativa")
        if ok:
            orr = linha_rc(chave, r)
            go = vcc[(vcc["chave_modelo"] == chave_vc) & (vcc["tipo_linha"] == "razao_chances_por_5mil")].iloc[0]
            d.update({f"rc_{k}": v for k, v in comparar_linha(orr, go, ["estimativa", "ic95_inf", "ic95_sup", "p"]).items()})
            du = P1H.linha_dif_uf("M1", r, "P1h-1", "primaria")
            gd = vcc[(vcc["chave_modelo"] == chave_vc) & (vcc["tipo_linha"] == "D_UF")].iloc[0]
            d.update({f"duf_{k}": v for k, v in comparar_linha(du, gd, ["estimativa", "ep_cluster_conjunto", "ic95_inf",
                                                                         "ic95_sup", "p_unilateral"]).items()})
        registrar(f"{chave}_corrigida", ok, d, f"VC_estimativas.csv (corrigida, {chave_vc}: coeficientes, razão de "
                                               "chances e D_UF)")
    vdc = vd[vd["versao"] == CORRIGIDA]
    r = res["M4_emp"]
    g = vdc[(vdc["chave_modelo"] == "M4") & (vdc["tipo_linha"] == "coeficiente")]
    ok, d = comparar_coef(r, g, "estimativa")
    if ok:
        go = vdc[(vdc["chave_modelo"] == "M4") & (vdc["tipo_linha"] == "razao_chances_por_5mil")].iloc[0]
        d.update({f"rc_{k}": v for k, v in comparar_linha(linha_rc("M4_emp", r), go,
                                                          ["estimativa", "ic95_inf", "ic95_sup"]).items()})
    registrar("M4_emp_corrigida", ok, d, "VD_estimativas.csv (corrigida, M4: coeficientes e razão de chances)")
    r = res["M1_emp"]
    for comp, passo in (("K5", 5.0), ("K10", 10.0)):
        k = P1H.linha_km(r, passo, "P1h-2", comp)
        gk = vdc[(vdc["chave_modelo"] == "M1") & (vdc["tipo_linha"] == "km_equivalentes") & (vdc["termo"] == comp)]
        ok = len(gk) == 1
        d = comparar_linha(k, gk.iloc[0], ["estimativa", "ep_cluster_conjunto", "ic95_inf", "ic95_sup",
                                           "ic95_fieller_inf", "ic95_fieller_sup"]) if ok else {}
        registrar(f"{comp}_M1_emp_corrigida", ok, d, "VD_estimativas.csv (corrigida, km equivalentes do M1)")
    return {"status": "PASSOU" if falha is None else falha, "tolerancia": tol,
            "regra": ("M1 e P1h-1 com o tipo de vaga antigo contra P1_estimativas.csv e P1h_magnitudes.csv; M1 dos "
                      "ciclos 1–3, M1 do ciclo 2 (M5) e D_UF corrigidos contra VC_estimativas.csv; M4 dos ciclos 1–3 "
                      "e K5, K10 do M1 corrigidos contra VD_estimativas.csv; diferença absoluta ≤ 1e−8 se o valor "
                      "gravado tem módulo ≤ 1, relativa ≤ 1e−8 se maior; NaN só casa com NaN"),
            "linhas": linhas}


# ---------------------------------------------------------------------------
# Linhas de saída
# ---------------------------------------------------------------------------

def _base(chave: str, r: dict, **kw) -> dict:
    e = ESPECS.get(chave, ESPECS["M1_emp"])
    b = {c: np.nan for c in COLUNAS}
    b.update({"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "id_vl": e["id_vl"], "papel": e["papel"],
              "chave_modelo": chave, "modelo": ROTULO.get(chave, chave), "ciclo": e["ciclo"],
              "efeito_fixo": e["ef"], "janela_corte": bool(e["janela"]), "distancia": e["dist"],
              "entra_holm": False, "familia_holm": "", "entra_bky": False, "familia_bky": "",
              "referencia": e["referencia"] or "", "g_conjuntos": r.get("G_conj"), "g_candidatos": r.get("G_cand"),
              "n_candidatos": r.get("n_candidatos"), "n_linhas_candidato_celula": r.get("n_linhas"),
              "n_conjuntos": r.get("n_conjuntos"), "n_efeitos_fixos": r.get("n_efeitos_fixos", 0),
              "status": r.get("status", "EXECUTADO"), "nota": ""})
    b.update(kw)
    return b


def linha_rc(chave: str, r: dict) -> dict:
    """Razão de chances por +R$ 5 mil: exp(5β), IC = exp do IC do log, EP pelo delta (como no script 42)."""
    k = r["termos"].index(B)
    b = float(r["theta"][k])
    e, em, ek = (math.sqrt(r[V][k, k]) for V in ("V_conj", "V_mle", "V_cand"))
    orr = math.exp(PASSO_BOLSA * b)
    z = b / e
    return {"estimativa": orr, "ep_cluster_conjunto": orr * PASSO_BOLSA * e, "ep_mle": orr * PASSO_BOLSA * em,
            "ep_cluster_candidato": orr * PASSO_BOLSA * ek, "ic95_inf": math.exp(PASSO_BOLSA * (b - Z95 * e)),
            "ic95_sup": math.exp(PASSO_BOLSA * (b + Z95 * e)), "p": float(2 * stats.norm.sf(abs(z))),
            "p_t_g_menos_1": float(2 * stats.t.sf(abs(z), r["G_conj"] - 1)),
            "p_mle": float(2 * stats.norm.sf(abs(b / em)))}


def diferenca(r: dict, ref: dict) -> dict:
    """5·(β_VL − β_ref) com EP pelo sanduíche conjunto das funções de influência somadas por conjunto (decisão 10)."""
    a, b = r["infl_bolsa"], ref["infl_bolsa"]
    cls = sorted(set(a) | set(b))
    ia = np.array([a.get(c, 0.0) for c in cls])
    ib = np.array([b.get(c, 0.0) for c in cls])
    G = len(cls)
    f = G / (G - 1.0)
    kb, kr = r["termos"].index(B), ref["termos"].index(B)
    d = PASSO_BOLSA * (float(r["theta"][kb]) - float(ref["theta"][kr]))
    ep = PASSO_BOLSA * math.sqrt(f * float(((ia - ib) ** 2).sum()))
    cov = f * float((ia * ib).sum())
    return {"estimativa": d, "ep_cluster_conjunto": ep, "ic95_inf": d - Z95 * ep, "ic95_sup": d + Z95 * ep,
            "p": float(2 * stats.norm.sf(abs(d / ep))) if ep > 0 else float("nan"), "g_conjuntos": G,
            "correlacao_beta": cov / math.sqrt(f * float((ia ** 2).sum()) * f * float((ib ** 2).sum()))}


def linhas_modelo(chave: str, r: dict, res: dict) -> list[dict]:
    out = []
    if not r["ok"]:
        out.append(_base(chave, r, tipo_linha="razao_chances_por_5mil", termo=B, status="NAO_CONVERGIU",
                         nota=r.get("nota", "")))
        return out
    nota_ef = (f"{r['n_efeitos_fixos']} indicadores de par (decisão 1), não relatados um a um" if r["n_efeitos_fixos"]
               else "")
    for t in r["termos"]:
        if t.startswith(PREFIXO_EF) or (ESPECS[chave]["ef"] == "uf_vaga" and t.startswith("uf_")):
            continue
        c = P1.combinacao(r, P1.vetor(r, t))
        out.append(_base(chave, r, tipo_linha="coeficiente", termo=t, estimativa=c["coef"],
                         **{k: c[k] for k in ("ep_cluster_conjunto", "ep_mle", "ep_cluster_candidato", "ic95_inf",
                                              "ic95_sup", "p", "p_t_g_menos_1", "p_mle")},
                         nota=P1._juntar("coeficiente da utilidade" + (" por R$ 1 mil/mês" if t == B else ""),
                                         r.get("nota", ""), nota_ef)))
    sb = r.get("score_bootstrap", {})
    out.append(_base(chave, r, tipo_linha="razao_chances_por_5mil", termo=B, **linha_rc(chave, r),
                     p_score_rademacher=sb.get("p_rademacher", np.nan), p_score_webb=sb.get("p_webb", np.nan),
                     nota=P1._juntar("exp(5·β), IC = exp do IC do log, EP pelo delta; p = o do β (cluster por conjunto)",
                                     (f"score bootstrap: {sb.get('metodo_rademacher')} (Rademacher)"
                                      if sb.get("status") == "EXECUTADO" else ""), nota_ef)))
    ref = ESPECS[chave]["referencia"]
    if chave in PRINCIPAIS and ref in res and res[ref]["ok"]:
        d = diferenca(r, res[ref])
        out.append(_base(chave, r, tipo_linha="diferenca_log_rc_contra_referencia", termo=B,
                         **{k: d[k] for k in ("estimativa", "ep_cluster_conjunto", "ic95_inf", "ic95_sup", "p")},
                         g_conjuntos=d["g_conjuntos"],
                         nota=(f"5·(β − β de {ref}); sanduíche conjunto por conjunto de escolha (decisão 10); "
                               f"correlação entre os dois β = {d['correlacao_beta']:.4f}; descritiva, fora do Holm")))
    if chave in ("M1_emp", "M1_c2"):
        du = P1H.linha_dif_uf("M1", r, "P1h-1", "primaria")
        out.append(_base(chave, r, tipo_linha="D_UF", termo="D_UF",
                         **{k: du[k] for k in ("estimativa", "ep_cluster_conjunto", "ep_mle", "ep_cluster_candidato",
                                               "ic95_inf", "ic95_sup", "li95_unilateral", "p_unilateral")},
                         nota="D_UF = θ_UF − 10·β da especificação base (não identificado com o par de UFs; §2)"))
    if chave in COM_KM:
        for comp, passo in (("K5", 5.0), ("K10", 10.0)):
            k = P1H.linha_km(r, passo, "VL-4", comp)
            out.append(_base(chave, r, id_vl="VL-4" if chave.startswith("VL") else "VL-5",
                             papel="secundaria_descritiva" if chave.startswith("VL") else "referencia",
                             tipo_linha="km_equivalentes", termo=comp,
                             **{c: k[c] for c in ("estimativa", "ep_cluster_conjunto", "ep_mle", "ep_cluster_candidato",
                                                  "ic95_inf", "ic95_sup", "ic95_fieller_inf", "ic95_fieller_sup")},
                             nota=f"{comp} = 100 · {passo:g}β / (−γ), km; delta e Fieller (forma: {k['fieller_forma']}); "
                                  "descritiva, sem teste"))
    return out


def montar(res: dict) -> pd.DataFrame:
    linhas = []
    for chave in ESPECS:
        linhas += linhas_modelo(chave, res[chave], res)
    est = pd.DataFrame(linhas)[COLUNAS]
    rc = est["tipo_linha"] == "razao_chances_por_5mil"
    mh = rc & est["chave_modelo"].isin(PRINCIPAIS)
    est.loc[mh, "entra_holm"] = True
    est.loc[mh, "familia_holm"] = FAMILIA_HOLM
    est.loc[mh, "p_holm"] = L.holm(est.loc[mh, "p"].to_numpy(dtype=float))
    est.loc[mh, "p_holm_score_rademacher"] = L.holm(est.loc[mh, "p_score_rademacher"].to_numpy(dtype=float))
    mb = rc & est["chave_modelo"].isin(SECUNDARIAS)
    est.loc[mb, "entra_bky"] = True
    est.loc[mb, "familia_bky"] = FAMILIA_BKY
    est.loc[mb, "q_bky"] = L.qvalores_bky(est.loc[mb, "p"].to_numpy(dtype=float))
    for c in ("entra_holm", "entra_bky", "janela_corte"):
        est[c] = est[c].astype(bool)
    return est


# ---------------------------------------------------------------------------
# Leitura (regras fixadas antes de rodar; decisão 11)
# ---------------------------------------------------------------------------

def _sel(est: pd.DataFrame, chave: str, tipo: str, termo: str | None = None) -> pd.Series:
    s = est[(est["chave_modelo"] == chave) & (est["tipo_linha"] == tipo)]
    if termo is not None:
        s = s[s["termo"] == termo]
    if len(s) != 1:
        raise FalhaValidacao(f"esperava 1 linha {chave} {tipo} {termo}, achei {len(s)}")
    return s.iloc[0]


def regra_linha(l: pd.Series, ref: pd.Series) -> str:
    """§3: razão de chances de uma linha VL contra a da referência (M1)."""
    if pd.isna(l["estimativa"]) or pd.isna(ref["estimativa"]):
        return "SEM_ESTIMATIVA"
    contem_1 = bool(l["ic95_inf"] <= 1.0 <= l["ic95_sup"])
    llog, rlog = math.log(l["estimativa"]), math.log(ref["estimativa"])
    if contem_1 and abs(llog) <= FRACAO_PERTO_DE_1 * abs(rlog):
        return "CAI_PARA_PERTO_DE_1"
    if ref["ic95_inf"] <= l["estimativa"] <= ref["ic95_sup"] and l["ic95_inf"] <= ref["estimativa"] <= l["ic95_sup"]:
        return "PARECIDA_COM_M1"
    if not contem_1 and np.sign(llog) != np.sign(rlog):
        return "SINAL_OPOSTO"
    if llog > rlog:
        return "MAIOR_QUE_M1"
    return "MENOR_QUE_M1_SEM_CHEGAR_A_1"


def ic_muito_largo(l: pd.Series, ref: pd.Series) -> bool | None:
    if pd.isna(l["ic95_inf"]) or pd.isna(ref["ic95_inf"]):
        return None
    lw = math.log(l["ic95_sup"]) - math.log(l["ic95_inf"])
    rw = math.log(ref["ic95_sup"]) - math.log(ref["ic95_inf"])
    return bool(lw >= FATOR_IC_LARGO * rw)


def leitura(est: pd.DataFrame) -> dict:
    out = {}
    for chave in PRINCIPAIS:
        l = _sel(est, chave, "razao_chances_por_5mil")
        ref = _sel(est, ESPECS[chave]["referencia"], "razao_chances_por_5mil")
        out[chave] = {"regra": regra_linha(l, ref), "referencia": ESPECS[chave]["referencia"],
                      "ic_contem_1": None if pd.isna(l["ic95_inf"]) else bool(l["ic95_inf"] <= 1.0 <= l["ic95_sup"]),
                      "ic_referencia_contem_1": bool(ref["ic95_inf"] <= 1.0 <= ref["ic95_sup"]),
                      "rejeita_holm_5pct": None if pd.isna(l["p_holm"]) else bool(l["p_holm"] < ALFA),
                      "rejeita_holm_score_5pct": (None if pd.isna(l["p_holm_score_rademacher"]) else
                                                  bool(l["p_holm_score_rademacher"] < ALFA))}
        if chave.startswith("VL2"):
            out[chave]["ic_muito_largo"] = ic_muito_largo(l, ref)
    regras = [out[k]["regra"] for k in PRINCIPAIS]
    if all(r == "PARECIDA_COM_M1" for r in regras):
        geral = "LOCALIZACAO_NAO_EXPLICA"
    elif any(out[k]["regra"] == "CAI_PARA_PERTO_DE_1" for k in ("VL1_emp", "VL1_c2")):
        geral = "LOCALIZACAO_EXPLICA_EM_PARTE"
    else:
        geral = "MISTA"
    holm = [out[k]["rejeita_holm_5pct"] for k in PRINCIPAIS]
    holm_s = [out[k]["rejeita_holm_score_5pct"] for k in PRINCIPAIS]
    km = {}
    for chave in ("VL1_emp", "VL1_c2"):
        k5 = _sel(est, chave, "km_equivalentes", "K5")
        b = _sel(est, chave, "coeficiente", B)
        km[chave] = {"km": float(k5["estimativa"]), "ic_beta_contem_0": bool(b["ic95_inf"] <= 0 <= b["ic95_sup"])}
    return {"linhas": out, "geral": geral, "holm_e_score_concordam": holm == holm_s, "VL4": km}


# ---------------------------------------------------------------------------
# Figura
# ---------------------------------------------------------------------------

def _plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 12})
    return plt


COR = {"M1": "#8a8984", "M4": "#b07a2a", "VL1": "#2a78d6", "VL2": "#1d4f8f"}
ROT_FIG = {"M1": "M1 base", "M4": "M4: UF da vaga", "VL1": "VL-1: par de UFs", "VL2": "VL-2: par de UFs, perto do corte"}


def titulo_figura(lei: dict, est: pd.DataFrame) -> str:
    nao_cai = all(_sel(est, k, "razao_chances_por_5mil")["estimativa"] >=
                  _sel(est, ESPECS[k]["referencia"], "razao_chances_por_5mil")["estimativa"] for k in PRINCIPAIS)
    return {"LOCALIZACAO_NAO_EXPLICA": ("Comparando vagas da mesma UF, o peso da bolsa na escolha não diminui" if nao_cai
                                        else "Comparando vagas da mesma UF, o peso da bolsa na escolha fica parecido "
                                             "com o do modelo base"),
            "LOCALIZACAO_EXPLICA_EM_PARTE": "Comparando vagas da mesma UF, o peso da bolsa na escolha cai para perto "
                                            "de nenhum",
            "MISTA": "Comparando vagas da mesma UF, o peso da bolsa na escolha muda conforme o recorte"}[lei["geral"]]


def figura(est: pd.DataFrame, lei: dict) -> dict:
    plt = _plt()
    DIR_FIG.mkdir(parents=True, exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14.0, 7.6), gridspec_kw={"width_ratios": [1.45, 1.0]})
    blocos = [("ciclos 1–3", "emp"), ("ciclo 2", "c2")]
    y, rotulos, ys = 0.0, [], []
    for nome_bloco, suf in blocos:
        for m in ("M1", "M4", "VL1", "VL2"):
            r = _sel(est, f"{m}_{suf}", "razao_chances_por_5mil")
            ys.append(y)
            rotulos.append(f"{ROT_FIG[m]} — {nome_bloco}")
            if pd.notna(r["estimativa"]):
                ax1.plot([r["ic95_inf"], r["ic95_sup"]], [y, y], color=COR[m], lw=2.6, solid_capstyle="round")
                ax1.plot([r["estimativa"]], [y], "o", ms=9, color=COR[m], zorder=3)
                ax1.text(r["ic95_sup"] * 1.04, y, _n(r["estimativa"], 2), va="center", ha="left", fontsize=10.5,
                         color="#2b2b29")
            y -= 1.0
        y -= 0.7
    ax1.axvline(1.0, color="#52514e", lw=1.0)
    ax1.set_xscale("log")
    sub = est[(est["tipo_linha"] == "razao_chances_por_5mil") & est["chave_modelo"].isin(
        [f"{m}_{s}" for m in ("M1", "M4", "VL1", "VL2") for _, s in blocos])]
    lo = min(0.5, float(sub["ic95_inf"].min()) * 0.9)
    hi = max(3.0, float(sub["ic95_sup"].max()) * 1.4)
    ax1.set_xlim(lo, hi)
    ticks = [t for t in (0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0) if lo <= t <= hi]
    ax1.set_xticks(ticks)
    ax1.set_xticklabels([_n(t, 2 if t == 0.75 else 1) for t in ticks])
    ax1.minorticks_off()
    ax1.set_yticks(ys)
    ax1.set_yticklabels(rotulos, fontsize=10.5)
    ax1.set_xlabel("razão de chances por +R$ 5 mil (escala log), IC 95%", fontsize=11.5)
    y, rot2, ys2 = 0.0, [], []
    for nome_bloco, suf in blocos:
        for m in ("M1", "VL1"):
            r = _sel(est, f"{m}_{suf}", "km_equivalentes", "K5")
            ys2.append(y)
            rot2.append(f"{'M1 base' if m == 'M1' else 'VL-1 (mesma UF)'} — {nome_bloco}")
            if pd.notna(r["estimativa"]):
                ax2.plot([r["ic95_inf"], r["ic95_sup"]], [y, y], color=COR[m], lw=2.6, solid_capstyle="round")
                ax2.plot([r["estimativa"]], [y], "o", ms=9, color=COR[m], zorder=3)
                ax2.text(r["ic95_sup"] + 8, y, f"{_n(r['estimativa'], 0)} km", va="center", ha="left", fontsize=10.5,
                         color="#2b2b29")
            y -= 1.0
        y -= 0.7
    k = est[(est["tipo_linha"] == "km_equivalentes") & (est["termo"] == "K5")]
    ax2.axvline(0.0, color="#52514e", lw=1.0)
    ax2.set_xlim(min(-20.0, float(k["ic95_inf"].min()) - 20), float(k["ic95_sup"].max()) + 90)
    ax2.set_yticks(ys2)
    ax2.set_yticklabels(rot2, fontsize=10.5)
    ax2.set_xlabel("km a menos com o peso de +R$ 5 mil\n(IC 95%, método delta)", fontsize=11.5)
    for ax in (ax1, ax2):
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
        ax.tick_params(axis="y", length=0)
        ax.grid(axis="x", color="#e6e5e0", lw=0.6)
        ax.set_axisbelow(True)
    fig.text(0.012, 0.975, titulo_figura(lei, est), fontsize=15, ha="left", va="top", color="#1f1f1d")
    fig.text(0.012, 0.02, "Escolha da 1ª opção, condicional a se candidatar; IC 95% com cluster por conjunto de escolha "
             "(curso × ciclo); tipo de vaga do ciclo 2 pelo quadro de 13/02/2026.\nBolsa: pacote do corte; origem: "
             "preferência revelada, não efeito causal.", fontsize=9.5, color="#52514e", ha="left", va="bottom")
    fig.subplots_adjust(left=0.25, right=0.965, top=0.9, bottom=0.16, wspace=0.7)
    fig.savefig(FIG, dpi=150, metadata={"Software": None})
    plt.close(fig)
    return {"arquivo": rel(FIG), "sha256": sha256(FIG), "titulo": titulo_figura(lei, est), "como_ler": COMO_LER}


# ---------------------------------------------------------------------------
# Documento 57x
# ---------------------------------------------------------------------------

def bloco(nome: str, corpo: str) -> list[str]:
    return [f"<!-- VL:{nome}:inicio -->", corpo, f"<!-- VL:{nome}:fim -->"]


def _sci(v) -> str:
    return "—" if v is None else f"{v:.1e}".replace(".", ",").replace("-", "−")


def _data_br(iso: str) -> str:
    a, m, d = iso.split("-")
    return f"{d}/{m}/{a}"


def _rc(r: pd.Series, casas: int = 2) -> str:
    if pd.isna(r["estimativa"]):
        return f"— ({r['status']})"
    return f"{_n(r['estimativa'], casas)} {_ic(r['ic95_inf'], r['ic95_sup'], casas)}"


def texto_decisoes() -> str:
    t = ["Decisões de implementação onde o adendo não fixava o detalhe. Foram registradas e commitadas antes de "
         "qualquer estimativa deste adendo (o histórico do Git mostra o commit deste bloco antes do commit dos "
         "números). Em qualquer ambiguidade, vale a leitura mais próxima dos scripts 25 e 42.", ""]
    for i, d in enumerate(DECISOES, 1):
        t.append(f"{i}. **{d['item']}** ({_data_br(d['data'])}). {d['situacao']} *Resolução:* {d['resolucao']}")
    return "\n".join(t)


NOTAS_EXECUCAO = [
    {"data": "2026-10-27", "item": "Ponto de partida do Newton nas linhas com efeito fixo de par",
     "o_que": "A decisão 1 dizia que as linhas com par seriam estimadas com a função `estimar` do script 25 sem "
              "alteração. Na 1ª execução, o Newton dela, que parte de zero, levou os indicadores de pares com "
              "pouquíssimas escolhas a valores muito negativos já no 1º passo; a informação ficou numericamente "
              "singular, e uma linha parou como NAO_CONVERGIU. Nenhuma estimativa da bolsa dessa execução foi lida ou "
              "gravada (o script parou antes de gravar qualquer saída).",
     "mudanca": "As linhas com par usam `estimar_ef`, que repete as etapas do `estimar` do 25 (colunas sem variação, "
                "posto, `ajustar_cl` com o mesmo critério de parada, covariâncias de MV e sanduíches) e só acrescenta "
                "o ponto de partida: os termos que não são de par, ajustados sem os indicadores, e as constantes de "
                "par que igualam escolhas previstas e observadas em cada par (contração de escala). A "
                "log-verossimilhança é côncava e a matriz tem posto completo, então o máximo é o mesmo; o resumo "
                "registra o gradiente máximo e o decremento de Newton finais de cada linha. As referências (M1, M4) "
                "continuam com o `estimar` do 25, sem mudança (portão)."},
    {"data": "2026-10-27", "item": "Ponto de partida do ajuste restrito do score bootstrap",
     "o_que": "Pelo mesmo motivo, o Newton do ajuste restrito (sem a bolsa) partindo de zero chegava a uma informação "
              "singular.",
     "mudanca": "O ajuste restrito parte da estimativa irrestrita sem a bolsa. O máximo restrito não muda."},
]


def texto_notas() -> str:
    t = ["Mudanças de execução feitas depois do commit das decisões e antes de ler qualquer estimativa da bolsa. Não "
         "mudam amostra, especificação, inferência nem leitura.", ""]
    for i, n in enumerate(NOTAS_EXECUCAO, 1):
        t.append(f"{i}. **{n['item']}** ({_data_br(n['data'])}). {n['o_que']} *O que mudou:* {n['mudanca']}")
    return "\n".join(t)


def texto_portao(resumo: dict) -> str:
    p = resumo["portao"]
    linhas = []
    for e in p["linhas"]:
        difs = [v for k, v in e.items() if k.startswith("dif_max_")]
        linhas.append([e["linha"], e["contra"], _sci(max(difs)) if difs else "—",
                       "passou" if e["passou"] else "**falhou**"])
    t = [f"**Portão de reprodução (VL-5): {p['status']}.** Antes de qualquer conta nova, as funções dos scripts 25 e "
         "25c (importadas sem alteração pelo 42) reproduzem as linhas já gravadas. A diferença é absoluta quando o "
         "valor gravado tem módulo até 1 e relativa acima disso (decisão 12); a coluna mostra a maior diferença entre "
         "todas as quantidades comparadas da linha (a lista completa está em `portao` de `VL_resumo.json`).", "",
         _tab(["Linha", "Contra", "Dif. máx.", "Portão"], linhas)]
    if p["status"] != "PASSOU":
        t += ["", f"A execução parou em `{p['status']}`: nada novo foi estimado (adendo 52e, §4)."]
    return "\n".join(t)


def texto_identificacao(resumo: dict) -> str:
    idt = resumo["identificacao"]
    linhas = []
    for chave in [k for k in ESPECS if ESPECS[k]["ef"] in ("uf_origem", "cir_origem")]:
        d = idt[chave]["identificacao"]
        jan = idt[chave].get("janela")
        linhas.append([ROTULO[chave],
                       (f"{jan['candidatos_com_1a_opcao_na_janela']} de {jan['candidatos']}" if jan else "—"),
                       f"{d['pares_no_desenho']} → {d['pares_no_modelo']}",
                       f"{d['pares_com_variacao_de_bolsa']}",
                       f"{d['alternativas_retiradas_par_sem_escolha']} + {d['alternativas_retiradas_por_separacao']} "
                       f"de {d['alternativas_no_desenho']}",
                       f"{d['candidatos_retirados_uma_so_alternativa']}",
                       f"{d['candidatos_no_modelo']}",
                       f"{d['candidatos_com_variacao_de_bolsa_em_algum_par']}",
                       f"{d['candidatos_com_1a_opcao_em_par_com_variacao']}",
                       f"{d['colunas_de_efeito_fixo']}"])
    v1 = idt["VL1_emp"]["identificacao"]
    v2 = idt["VL1_c2"]["identificacao"]
    return "\n".join([
        f"**Quem identifica o peso da bolsa com o par de UFs.** Nos ciclos 1–3, o VL-1 fica com "
        f"{v1['pares_no_modelo']} pares (UF de origem, UF da vaga) com alguma escolha, de {v1['pares_no_desenho']} "
        f"no desenho; {v1['pares_com_variacao_de_bolsa']} deles têm vagas com bolsas diferentes para algum candidato "
        f"e, por isso, informam o peso da bolsa, vindos de {v1['origens_com_algum_par_com_variacao']} das "
        f"{v1['origens_no_modelo']} UFs de origem. São {v1['candidatos_com_variacao_de_bolsa_em_algum_par']} dos "
        f"{v1['candidatos_no_modelo']} candidatos do modelo que veem, dentro de alguma UF, vagas com bolsas "
        f"diferentes; {v1['candidatos_com_1a_opcao_em_par_com_variacao']} escolheram a 1ª opção numa UF assim. No "
        f"ciclo 2: {v2['pares_com_variacao_de_bolsa']} pares com variação, "
        f"{v2['candidatos_com_variacao_de_bolsa_em_algum_par']} de {v2['candidatos_no_modelo']} candidatos com "
        "variação.", "",
        "Colunas: candidatos com a 1ª opção na janela (só no VL-2); pares no desenho → pares que ficam no modelo (os "
        "sem escolha saem, decisão 2); pares com variação de bolsa; alternativas (candidato × vaga) retiradas por "
        "estarem em par sem escolha + por separação do efeito fixo (decisão 2); candidatos retirados por ficarem com "
        "uma só alternativa; candidatos no modelo; candidatos com variação de bolsa dentro de algum par (são os que "
        "identificam o peso); candidatos com a 1ª opção num par com variação; colunas de efeito fixo (pares menos uma "
        "base por componente). Os pares sem variação de bolsa ficam no modelo (decisão 3).",
        "",
        _tab(["Linha", "1ª opção na janela", "Pares (desenho → modelo)", "Pares com variação de bolsa",
              "Alternativas retiradas (sem escolha + separação)", "Candidatos retirados", "Candidatos no modelo",
              "Candidatos com variação", "1ª opção em par com variação", "Colunas de efeito fixo"], linhas)])


def tabela_principais(est: pd.DataFrame, resumo: dict) -> str:
    linhas = []
    for chave in PRINCIPAIS:
        r = _sel(est, chave, "razao_chances_por_5mil")
        ref = _sel(est, ESPECS[chave]["referencia"], "razao_chances_por_5mil")
        d = _sel(est, chave, "diferenca_log_rc_contra_referencia")
        linhas.append([ROTULO[chave], _int(r["n_candidatos"]), _int(r["g_conjuntos"]), _rc(r), _p(r["p"]),
                       _p(r["p_holm"]), _p(r["p_score_rademacher"]), _p(r["p_holm_score_rademacher"]),
                       f"{ROTULO[ESPECS[chave]['referencia']]}: {_rc(ref)}",
                       f"{_n(d['estimativa'], 3)} {_ic(d['ic95_inf'], d['ic95_sup'], 3)}"])
    sb = resumo["score_bootstrap"]
    ref = []
    for chave in ("M1_emp", "M1_c2"):
        r = _sel(est, chave, "razao_chances_por_5mil")
        ref.append([ROTULO[chave], _int(r["n_candidatos"]), _int(r["g_conjuntos"]), _rc(r), _p(r["p"]),
                    _p(r["p_score_rademacher"]), _p(r["p_score_webb"])])
    return "\n".join([
        "Razão de chances da 1ª opção por +R$ 5 mil de bolsa, IC 95% e p (H0: β = 0) com cluster por conjunto de "
        "escolha (curso × ciclo); p de Holm na família das três principais; p do score bootstrap (Kline–Santos, "
        "Rademacher) e o seu Holm, como robustez para poucos clusters; diferença do log da razão de chances contra a "
        "referência (M1), com IC pelo sanduíche conjunto (decisão 10). Tipo de vaga do ciclo 2 pelo quadro de "
        "13/02/2026. O ponto de partida do Newton está na seção 7.1 (notas de execução).", "",
        _tab(["Linha", "Candidatos", "Conjuntos (G)", "RC [IC 95%]", "p", "p Holm", "p score", "p Holm (score)",
              "Referência: RC [IC 95%]", "Diferença de log RC [IC 95%]"], linhas), "",
        "Referências (VL-5, sem teste novo; os mesmos números do `VC_estimativas.csv`), com o score bootstrap "
        f"calculado aqui ({sb['M1_emp'].get('metodo_rademacher', '—')} nos ciclos 1–3; "
        f"{sb['M1_c2'].get('metodo_rademacher', '—')} no ciclo 2):", "",
        _tab(["Referência", "Candidatos", "Conjuntos (G)", "RC [IC 95%]", "p", "p score (Rademacher)",
              "p score (Webb)"], ref)])


def tabela_secundarias(est: pd.DataFrame) -> str:
    linhas = []
    for chave in SECUNDARIAS + ("M4_emp", "M4_c2"):
        r = _sel(est, chave, "razao_chances_por_5mil")
        linhas.append([ROTULO[chave], r["id_vl"], ROTULO_EF[ESPECS[chave]["ef"]], _int(r["n_candidatos"]),
                       _int(r["g_conjuntos"]), _rc(r), _p(r["p"]), _p(r["q_bky"]) if r["entra_bky"] else "—"])
    return "\n".join([
        "Mesma leitura da tabela anterior. q BKY na família das sete secundárias (decisão 9); o M4 é só referência da "
        "figura, sem teste.", "",
        _tab(["Linha", "Id", "Efeito fixo", "Candidatos", "Conjuntos (G)", "RC [IC 95%]", "p", "q BKY"], linhas)])


def tabela_km(est: pd.DataFrame) -> str:
    linhas = []
    for chave in COM_KM:
        for comp in ("K5", "K10"):
            r = _sel(est, chave, "km_equivalentes", comp)
            linhas.append([ROTULO[chave], comp, f"{_n(r['estimativa'], 0)} km",
                           _ic(r["ic95_inf"], r["ic95_sup"], 0), _ic(r["ic95_fieller_inf"], r["ic95_fieller_sup"], 0)])
    return "\n".join([
        "VL-4: quantos km a menos de distância origem–vaga pesam na escolha como +R$ 5 mil (K5) ou +R$ 10 mil (K10) "
        "de bolsa: 100 · passo · β / (−γ), com γ o peso da distância por 100 km. No VL-1, comparando vagas da mesma "
        "UF vistas por médicos da mesma UF de origem. IC pelo método delta e por Fieller; descritivo, sem teste (como "
        "o P1h-2). Fieller com limite infinito quer dizer que o IC do β contém zero.", "",
        _tab(["Modelo", "Passo", "km equivalentes", "IC 95% (delta)", "IC 95% (Fieller)"], linhas)])


def tabela_controles(est: pd.DataFrame) -> str:
    termos = [t for t in est[(est["chave_modelo"] == "VL1_emp") & (est["tipo_linha"] == "coeficiente")]["termo"]]
    linhas = []
    for t in termos:
        cel = []
        for chave in ("M1_emp", "VL1_emp", "VL2_emp"):
            s = est[(est["chave_modelo"] == chave) & (est["tipo_linha"] == "coeficiente") & (est["termo"] == t)]
            cel.append("—" if s.empty else f"{_n(s.iloc[0]['estimativa'], 3)} "
                                           f"{_ic(s.iloc[0]['ic95_inf'], s.iloc[0]['ic95_sup'], 3)}")
        linhas.append([f"`{t}`"] + cel)
    s = _sel(est, "VL2_emp", "coeficiente", TERMO_INTERCEPTO)
    linhas.append([f"`{TERMO_INTERCEPTO}`", "—", "—", f"{_n(s['estimativa'], 3)} {_ic(s['ic95_inf'], s['ic95_sup'], 3)}"])
    return "\n".join([
        "Todos os coeficientes que não são indicadores de par, nos ciclos 1–3 (log-chance; IC 95% com cluster por "
        "conjunto). `mesma_uf` e as macrorregiões não aparecem no VL-1 e no VL-2 porque o par de UFs os absorve "
        "(decisão 1). Todas as linhas estão em `VL_estimativas.csv`.", "",
        _tab(["Termo", "M1 (base)", "VL-1", "VL-2"], linhas)])


ROTULO_REGRA = {
    "PARECIDA_COM_M1": "parecida com a do M1",
    "CAI_PARA_PERTO_DE_1": "cai para perto de 1, com IC que contém 1",
    "MAIOR_QUE_M1": "maior que a do M1 (fora das leituras do §3)",
    "SINAL_OPOSTO": "do outro lado de 1 (fora das leituras do §3)",
    "MENOR_QUE_M1_SEM_CHEGAR_A_1": "menor que a do M1, sem chegar perto de 1 (fora das leituras do §3)",
    "SEM_ESTIMATIVA": "sem estimativa",
}


def _correlacao(resumo: dict, chave: str, ref: str) -> float:
    """Correlação entre os β de duas linhas, das influências por conjunto gravadas (a mesma da nota da decisão 10)."""
    a, b = resumo["influencia_bolsa_por_conjunto"][chave], resumo["influencia_bolsa_por_conjunto"][ref]
    cls = sorted(set(a) | set(b))
    ia = np.array([a.get(c, 0.0) for c in cls])
    ib = np.array([b.get(c, 0.0) for c in cls])
    return float((ia * ib).sum() / math.sqrt((ia ** 2).sum() * (ib ** 2).sum()))


def _perto(l: pd.Series, m: pd.Series, limite: float = 0.1) -> bool:
    """Auditoria 48: duas razões de chances a menos de 0,1 em log uma da outra (só para a frase descritiva do M4)."""
    return bool(abs(math.log(l["estimativa"]) - math.log(m["estimativa"])) < limite)


def texto_resposta(est: pd.DataFrame, resumo: dict) -> str:
    lei = resumo["leitura"]
    t = []
    geral = {
        "LOCALIZACAO_NAO_EXPLICA": "**O peso da bolsa na escolha não vem da localização.** Comparando só vagas da mesma "
                                   "UF, vistas por médicos da mesma UF de origem, a razão de chances da bolsa fica "
                                   "parecida com a do modelo base nas três principais, pela regra fixada (1ª linha do "
                                   "§3): entre vagas na mesma relação geográfica com o médico, a bolsa maior continua "
                                   "pesando.",
        "LOCALIZACAO_EXPLICA_EM_PARTE": "**Parte do peso da bolsa no modelo base vinha de onde ficam as vagas de bolsa "
                                        "maior em relação à origem dos médicos** (2ª linha do §3).",
        "MISTA": "**A leitura muda conforme o recorte; vale linha a linha.**",
    }[lei["geral"]]
    # Auditoria 48 (A1): quando a diferença pareada contra o M1 exclui zero para cima, a resposta curta o diz já aqui.
    acima = [c for c in PRINCIPAIS if _sel(est, c, "diferenca_log_rc_contra_referencia")["ic95_inf"] > 0]
    if lei["geral"] == "LOCALIZACAO_NAO_EXPLICA" and acima:
        geral += (" Mais que isso: em " + " e ".join(ROTULO[c] for c in acima) + ", a comparação pareada com o M1 mostra "
                  "a bolsa pesando mais que no modelo base, não o mesmo; \"parecida\" é o rótulo da regra fixada, que "
                  "compara os IC lado a lado.")
    t.append(geral)
    for chave in PRINCIPAIS:
        r = _sel(est, chave, "razao_chances_por_5mil")
        ref = _sel(est, ESPECS[chave]["referencia"], "razao_chances_por_5mil")
        d = _sel(est, chave, "diferenca_log_rc_contra_referencia")
        li = lei["linhas"][chave]
        exclui_zero = bool(d["ic95_inf"] > 0 or d["ic95_sup"] < 0)
        # Auditoria 48 (A1): a regra fixada (decisão 11) compara os IC lado a lado e ignora que os dois β andam juntos;
        # quando a diferença pareada (decisão 10) exclui zero, o rótulo da regra fica, mas o texto diz o que ela mostra.
        rotulo_regra = (f"pela regra fixada, {ROTULO_REGRA[li['regra']]} (cada estimativa cai no IC da outra)"
                        if exclui_zero and li["regra"] == "PARECIDA_COM_M1" else ROTULO_REGRA[li["regra"]])
        frase = (f"- **{ROTULO[chave]}:** razão de chances {_rc(r)} contra {_rc(ref)} no "
                 f"{ROTULO[ESPECS[chave]['referencia']]}; {rotulo_regra}. p de Holm {_p(r['p_holm'])} "
                 f"(score bootstrap: {_p(r['p_holm_score_rademacher'])}). Diferença de log da razão de chances "
                 f"{_n(d['estimativa'], 2)} {_ic(d['ic95_inf'], d['ic95_sup'], 2)}.")
        if exclui_zero:
            mais = "mais" if d["estimativa"] > 0 else "menos"
            frase += (f" Essa diferença é medida nos mesmos candidatos, e os dois β andam juntos (correlação "
                      f"{_n(_correlacao(resumo, chave, ESPECS[chave]['referencia']), 2)}); por isso ela exclui zero mesmo com os IC lado a lado se "
                      f"sobrepondo. A leitura mais exata é que, comparando dentro da mesma UF, a bolsa pesa {mais} que no "
                      "M1, não o mesmo (descritivo, fora do Holm).")
        else:
            frase += " A diferença contra o M1 contém zero."
        if li.get("ic_muito_largo"):
            frase += " O IC é pelo menos duas vezes mais largo que o da referência: a comparação local tem pouca " \
                     "informação (3ª linha do §3)."
        t.append(frase)
    # Auditoria 48 (A1): de onde vem a subida contra o M1 (M4 já está na figura e na tabela 4.2; descritivo).
    m4 = {s: _sel(est, f"M4_{s}", "razao_chances_por_5mil") for s in ("emp", "c2")}
    vl1 = {s: _sel(est, f"VL1_{s}", "razao_chances_por_5mil") for s in ("emp", "c2")}
    frase_m4 = (f"**De onde vem a diferença contra o M1.** O M4, que só troca a macrorregião por efeito fixo de UF da "
                f"vaga, dá {_rc(m4['emp'])} nos ciclos 1–3 e {_rc(m4['c2'])} no ciclo 2")
    if all(_perto(vl1[s], m4[s]) for s in ("emp", "c2")):
        frase_m4 += (": perto do VL-1. O que muda o peso da bolsa é comparar vagas dentro da mesma UF; fixar também a "
                     "UF de origem do médico muda pouco (descritivo, sem teste).")
    else:
        frase_m4 += f" (VL-1: {_rc(vl1['emp'])} e {_rc(vl1['c2'])}; descritivo, sem teste)."
    t.append(frase_m4)
    # Auditoria 48 (A4): o parêntese do §2 fala em log da distância; a decisão 4 manteve a distância linear do M1.
    lg = {s: _sel(est, f"VL1log_{s}", "razao_chances_por_5mil") for s in ("emp", "c2")}
    mesma = all(regra_linha(lg[s], _sel(est, ESPECS[f"VL1log_{s}"]["referencia"], "razao_chances_por_5mil")) ==
                lei["linhas"][f"VL1_{s}"]["regra"] for s in ("emp", "c2"))
    t.append(f"**Com o log da distância.** O parêntese do VL-1 no §2 do adendo fala em log da distância; a decisão 4 "
             f"manteve a distância linear do M1 e pôs o log como secundária. Com o log, o VL-1 dá {_rc(lg['emp'])} nos "
             f"ciclos 1–3 e {_rc(lg['c2'])} no ciclo 2 (q BKY {_p(lg['emp']['q_bky'])} e {_p(lg['c2']['q_bky'])})"
             + ("; pela mesma regra do §3, a leitura não muda." if mesma else
                "; pela mesma regra do §3, a leitura muda (ver a seção 4.2)."))
    if not lei["holm_e_score_concordam"]:
        t.append("Holm com o p por cluster e Holm com o p do score bootstrap **não** dão a mesma decisão em todas as "
                 "principais; ver a seção 4.1.")
    km = lei["VL4"]
    k1, k2 = _sel(est, "VL1_emp", "km_equivalentes", "K5"), _sel(est, "VL1_c2", "km_equivalentes", "K5")
    m1, m2 = _sel(est, "M1_emp", "km_equivalentes", "K5"), _sel(est, "M1_c2", "km_equivalentes", "K5")
    frase_km = (f"**VL-4.** Comparando vagas da mesma UF, +R$ 5 mil pesam como {_n(k1['estimativa'], 0)} km a menos "
                f"de distância nos ciclos 1–3 (IC delta {_ic(k1['ic95_inf'], k1['ic95_sup'], 0)}; no M1, "
                f"{_n(m1['estimativa'], 0)} km) e {_n(k2['estimativa'], 0)} km no ciclo 2 (IC "
                f"{_ic(k2['ic95_inf'], k2['ic95_sup'], 0)}; no M1, {_n(m2['estimativa'], 0)} km).")
    contem = [c for c in ("VL1_emp", "VL1_c2") if km[c]["ic_beta_contem_0"]]
    if contem:
        frase_km += (" O IC do β contém zero em " + " e ".join(ROTULO[c] for c in contem) +
                     "; o IC dos km também contém zero ali.")
    for vl, m1 in (("VL1_emp", "M1_emp"), ("VL1_c2", "M1_c2")):
        gv, gm = _sel(est, vl, "coeficiente", DIST), _sel(est, m1, "coeficiente", DIST)
        bv, bm = _sel(est, vl, "coeficiente", B), _sel(est, m1, "coeficiente", B)
        kv, km_ = _sel(est, vl, "km_equivalentes", "K5"), _sel(est, m1, "km_equivalentes", "K5")
        if kv["estimativa"] < km_["estimativa"] and abs(gv["estimativa"]) > abs(gm["estimativa"]) and \
                bv["estimativa"] >= bm["estimativa"]:
            frase_km += (f" Em {ROTULO[vl]}, os km caem em relação ao M1 porque, dentro da mesma UF, a distância pesa "
                         f"mais ({_n(gv['estimativa'], 2)} por 100 km, contra {_n(gm['estimativa'], 2)} no M1), e não "
                         "porque a bolsa pese menos.")
        else:
            frase_km += (f" Em {ROTULO[vl]}, o peso da distância é {_n(gv['estimativa'], 2)} por 100 km (no M1, "
                         f"{_n(gm['estimativa'], 2)}).")
    t.append(frase_km)
    v1 = resumo["identificacao"]["VL1_emp"]["identificacao"]
    t.append(f"**Quem identifica.** Nos ciclos 1–3, {v1['pares_com_variacao_de_bolsa']} pares de UF (origem, vaga) "
             f"têm vagas com bolsas diferentes, e {v1['candidatos_com_variacao_de_bolsa_em_algum_par']} candidatos "
             "veem essa variação dentro de alguma UF (seção 3).")
    t.append("**Em linguagem simples.** A pergunta era: a bolsa maior atrai porque paga mais, ou porque as vagas de "
             "bolsa maior ficam em lugares que os médicos já preferem (perto de casa, na própria UF)? Para separar, "
             "a conta compara só vagas da mesma UF, vistas por médicos que vêm da mesma UF, e depois só vagas "
             "parecidas, perto de um corte de IVS. A bolsa aqui é o pacote do corte de IVS (bolsa e outras regras "
             "federais que mudam nos mesmos cortes), não a participação no PMM-E; a origem do candidato é preferência "
             "revelada, não efeito causal; e tudo vale para quem se candidatou, dentro das vagas abertas.")
    return "\n\n".join(t)


def texto_leitura(resumo: dict) -> str:
    lei = resumo["leitura"]
    linhas = []
    for chave in PRINCIPAIS:
        li = lei["linhas"][chave]
        linhas.append([ROTULO[chave], ROTULO[li["referencia"]], f"`{li['regra']}`",
                       "sim" if li["ic_contem_1"] else "não", "sim" if li["ic_referencia_contem_1"] else "não",
                       "—" if "ic_muito_largo" not in li else ("sim" if li["ic_muito_largo"] else "não")])
    return "\n".join([
        f"Regra fixada no código antes de rodar (decisão 11). Leitura geral: `{lei['geral']}`.", "",
        _tab(["Linha", "Referência", "Regra", "IC contém 1", "IC da referência contém 1", "IC muito largo (VL-2)"],
             linhas)])


def texto_figura(resumo: dict) -> str:
    f = resumo["figura"]
    return "\n".join([f"![{f['titulo']}](../../{f['arquivo']})", "",
                      f"Arquivo: `{f['arquivo']}`. Título: \"{f['titulo']}\".", "",
                      f"**Como ler.** {f['como_ler']}"])


PENDENTE = "*Pendente: preenchido pelo script depois do portão de reprodução.*"


def gerar_doc(est: pd.DataFrame | None, resumo: dict | None) -> str:
    """Doc 57x. Sem resumo (pré-registro), só cabeçalho, decisões e limites."""
    tem_portao = resumo is not None and "portao" in resumo
    ok = tem_portao and resumo["portao"]["status"] == "PASSOU" and est is not None
    Lh = [
        "# 57x. H2 com a localização do médico e da vaga fixada: efeito fixo do par de UFs e comparação local no corte "
        "(adendo 52e)",
        "",
        "> **Gerado por** `scripts/rdd_bolsa/50_escolha_localizacao_par.py` a partir de `output/rdd_bolsa/VL_*`; não "
        "editar à mão (o teste `tests/test_escolha_localizacao_par.py` confere que este arquivo é igual ao gerado; "
        "`--atualizar-doc` o regrava das saídas).<br>",
        f"> **Adendo:** [`52e_adendo_escolha_localizacao_par.md`](52e_adendo_escolha_localizacao_par.md), congelado em "
        f"27/10/2026 antes de rodar (commit `{COMMIT_ADENDO}`); SHA-256 em `adendo` de `VL_resumo.json`, conferido pelo "
        "teste. Protocolos de origem: [52](52_protocolo_P1_escolha_dap.md) (P1) e [52b](52b_protocolo_P1h_magnitudes.md) "
        "(P1h); adendos [52c](52c_adendo_vaga_imediata_ciclo2.md) (tipo de vaga do ciclo 2, doc "
        "[57p](57p_escolha_vaga_imediata_c2.md)) e [52d](52d_adendo_sensibilidades_ciclo2_quadro_1302.md) (doc "
        "[57v](57v_sensibilidades_ciclo2_quadro_1302.md)).<br>",
        "> **Estatuto:** `ADENDO_52E_POS_RESULTADO`. O P1 (doc 57a), o P1h (57i), o 52c (57p) e o 52d (57v) já tinham "
        "sido vistos; isto não é teste confirmatório novo. Toda linha de `VL_estimativas.csv` e o resumo têm "
        "`natureza_dos_dados = EMPIRICO`.<br>",
        "> **Pedido do autor (27/10/2026):** \"rodar de novo a H1 fazendo pareamento pela localização da unidade e do "
        "médico, como se fosse um controle. O mesmo vale para a H2.\" Este doc é a parte da H2.<br>",
        "> **Saídas:** `output/rdd_bolsa/VL_estimativas.csv`, `VL_resumo.json` e "
        "`VL_figuras/VL_razao_chances_e_km.png`. As saídas `E9_*`, `P1_*`, `P1h_*`, `VC_*` e `VD_*` não são regravadas, "
        "e os docs 57a, 57i, 57p e 57v não são editados.<br>",
        "> **Auditoria:** [48](../auditorias/48_auditoria_escolha_localizacao_par.md), aprovada com correções de texto: o "
        "recálculo independente reproduz todas as linhas, e nenhuma estimativa mudou. A auditoria acrescentou à resposta "
        "curta a leitura da comparação pareada com o M1, a frase do M4 e a da distância em log. A redação da resposta "
        "curta e o título da figura foram escritos depois de ver as estimativas; as regras do §3 (`regra_linha`, "
        "`leitura`) são as do commit das decisões.",
        "",
        "## 1. Resposta curta",
        "",
    ]
    if ok:
        Lh += [*bloco("resposta", texto_resposta(est, resumo)), ""]
    elif tem_portao:
        Lh += [*bloco("resposta", f"Nada novo estimado: `{resumo['portao']['status']}`."), ""]
    else:
        Lh += [PENDENTE, ""]
    Lh += ["## 2. Portão de reprodução (VL-5)", ""]
    Lh += [*bloco("portao", texto_portao(resumo)), ""] if tem_portao else [PENDENTE, ""]
    if ok:
        Lh += [
            "## 3. Quantos pares de UF e quantas escolhas identificam o peso da bolsa",
            "",
            *bloco("identificacao", texto_identificacao(resumo)),
            "",
            "## 4. Resultados",
            "",
            "### 4.1 Principais (VL-1 e VL-2), com Holm",
            "",
            *bloco("principais", tabela_principais(est, resumo)),
            "",
            "### 4.2 Secundárias (VL-2 do ciclo 2, VL-3, distância em log) e M4",
            "",
            *bloco("secundarias", tabela_secundarias(est)),
            "",
            "### 4.3 km equivalentes (VL-4)",
            "",
            *bloco("km", tabela_km(est)),
            "",
            "### 4.4 Os outros pesos do modelo",
            "",
            *bloco("controles", tabela_controles(est)),
            "",
            "## 5. Leitura do §3 por regra",
            "",
            *bloco("leitura", texto_leitura(resumo)),
            "",
            "## 6. Figura",
            "",
            *bloco("figura", texto_figura(resumo)),
            "",
        ]
    else:
        Lh += ["## 3. Resultados", "", PENDENTE, ""]
    Lh += [
        "## 7. Decisões de implementação",
        "",
        *bloco("decisoes", texto_decisoes()),
        "",
    ]
    if tem_portao:
        Lh += ["### 7.1 Notas de execução", "", *bloco("notas", texto_notas()), ""]
    Lh += [
        "## 8. Limites",
        "",
        "- **Pós-resultado.** O M1, o P1h, o 52c e o 52d já eram conhecidos. O adendo foi congelado antes de rodar, mas "
        "isto é robustez, não teste confirmatório novo.",
        "- **O que o par de UFs controla.** Tudo o que é igual para vagas da mesma UF vistas por médicos da mesma UF "
        "de origem: distância média entre as UFs, registro no conselho regional, rede e família na UF, salário de "
        "mercado da UF, regras estaduais. Não controla diferenças dentro da UF que andem junto com a bolsa (capital "
        "contra interior além do que capital, estrato e porte já captam; acesso; serviço de saúde da vaga).",
        "- **A identificação fica mais estreita.** Com o par de UFs, o peso da bolsa vem só de UFs que têm vagas de "
        "faixas diferentes; os pares sem variação de bolsa não informam o peso (seção 3). O resultado vale para essas "
        "UFs e para os candidatos que veem essa variação.",
        "- **Pares sem escolha saem.** As vagas de pares que ninguém daquela origem escolheu saem do conjunto (decisão "
        "2). Isso não muda o peso dos outros atributos no limite da verossimilhança, mas o conjunto de escolha do "
        "modelo fica menor que o do M1.",
        "- **Comparação local.** O VL-2 usa só vagas perto de um corte de IVS; é a versão \"RDD dentro da escolha\", "
        "com menos vagas e menos candidatos, e o IC é mais largo.",
        "- **Escolha condicional.** Tudo vale para quem se candidatou, dentro das vagas abertas do seu curso e ciclo; o "
        "conjunto de escolha supõe que o candidato viu todas as vagas do curso; IIA do logit condicional.",
        "- **Pacote do corte.** O peso da bolsa é identificado pelos saltos nos cortes de IVS, com o IVS em spline "
        "contínua; nos mesmos cortes mudam outras regras federais (auditoria 18). Não é efeito da participação no "
        "PMM-E nem do Agora Tem Especialistas.",
        "- **Origem não é causal.** A origem é o município do vínculo médico no CNES (G1), não a residência; o peso da "
        "origem é preferência revelada, não efeito causal.",
        "- **Poucos conjuntos.** O cluster é o conjunto de escolha (curso × ciclo), e são poucos, sobretudo no ciclo 2; "
        "por isso o score bootstrap vai ao lado do p por cluster, e o número de cada linha está na coluna "
        "`g_conjuntos` de `VL_estimativas.csv`.",
        "- **km são razões.** Com o peso da bolsa perto de zero, os km equivalentes ficam instáveis e não são preço.",
    ]
    return "\n".join(Lh) + "\n"


# ---------------------------------------------------------------------------
# Execução
# ---------------------------------------------------------------------------

def entradas(dados: dict) -> list[dict]:
    be = P1.bloco_entrada
    return [
        be(ADENDO_MD, "adendo 52e (especificação, somente lido)", "repositório", "2026-10-27", "§1–§5", "documento",
           "-", "-"),
        be(ADENDO_52C, "adendo 52c (somente lido)", "repositório", "2026-10-26", "§1–§3", "documento", "-", "-"),
        be(ADENDO_52D, "adendo 52d (somente lido)", "repositório", "2026-10-26", "§1–§5", "documento", "-", "-"),
        be(PROTOCOLO_52, "protocolo 52 (P1; somente lido)", "repositório", "2026-10-19", "§1–§6", "documento", "-", "-"),
        be(PROTOCOLO_52B, "protocolo 52b (P1h; somente lido)", "repositório", "2026-10-26", "§1–§6", "documento", "-",
           "-"),
        be(VC.QUADRO_1302, "quadro do ciclo 2, retificado de 13/02/2026 (vigente na inscrição)",
           "Chamamento SGTES/MS nº 1/2026 (página oficial)", "2026-02-13", "1547 células CNES × curso", "célula",
           "CNES (7 dígitos) × código do curso", "coluna TOTAL de vagas imediatas"),
        be(VC.QUADRO_1903, "quadro do ciclo 2, retificado de 19/03/2026 (lido pelo 42; versão antiga)", "idem",
           "2026-03-19", "1547 células", "célula", "CNES × curso", "coluna TOTAL de vagas imediatas"),
        be(VC.A36_CELULAS, "leitura independente da auditoria 36 (conferência do quadro de 13/02 pelo 42)",
           "auditoria 36", "2026-10-26", "células dos ciclos 1–3", "célula", "cnes, cod_curso", "ciclo = 2"),
        be(P1_EST, "alvo do portão (M1 antigo)", "script 25", "2026-10-23", "M1, coeficientes", "especificação × termo",
           "modelo, ciclo, tipo_linha, termo", "-"),
        be(P1H_CSV, "alvo do portão (P1h-1 antigo)", "script 25c", "2026-10-26", "P1h-1", "linha",
           "id_linha, modelo, ciclo, componente", "-"),
        be(VC_CSV, "alvo do portão (M1, M5 do ciclo 2 e D_UF corrigidos)", "script 42", "2026-10-26",
           "M1 e M5_2, corrigida", "especificação × termo", "versao, chave_modelo, tipo_linha, termo", "-"),
        be(VD_CSV, "alvo do portão (M4 e km do M1 corrigidos)", "script 48", "2026-10-26", "M4 e M1, corrigida",
           "especificação × termo", "versao, chave_modelo, tipo_linha, termo", "-"),
        be(SCRIPT_42, "funções do adendo 52c (importadas sem alteração)", "repositório", "-", "-", "código", "-", "-"),
        be(SCRIPT_16, "funções do E9 (score bootstrap; importadas sem alteração, pelo 42)", "repositório", "-", "-",
           "código", "-", "-"),
        be(SCRIPT_25, "funções do P1 (importadas sem alteração, pelo 42)", "repositório", "-", "-", "código", "-", "-"),
        be(SCRIPT_25C, "funções do P1h (importadas sem alteração, pelo 42)", "repositório", "-", "-", "código", "-",
           "-"),
        be(E9.ESCOLHAS, "escolhas dos candidatos (1ª opção)", "tarefa B (script 12)", "resultados da 1ª chamada",
           f"{len(dados['cand'])} linhas", "candidato × opção", "ciclo, id_candidato, opcao_rank", "posto 1"),
        be(E9.CONJ_PRINCIPAL, "conjunto de escolha principal; ciclo 2 corrigido em memória (52c)",
           "tarefa B (script 12)", "quadros da 1ª chamada", f"{len(dados['conj'])} células com IVS",
           "célula CNES × curso × ciclo", "ciclo, co_cnes_7d, cod_curso", "como no P1"),
        be(E9.IVS_OFICIAL, "IVS 2010 oficial (a08)", "Ipea (a08)", "Censo 2010", f"{len(dados['ivs'])} municípios",
           "município", "co_ibge", "co_ibge, ivs"),
        be(P1.G1_ORIGEM, "município de origem (G1)", "portão G1", "referências 202506, 202510, 202602",
           f"{len(dados['org'])} candidatos", "candidato", "ciclo, id_candidato", f"regra_ligacao = {P1.REGRA_G1}"),
        be(P1.G1_DIST, "conferência das distâncias", "portão G1", "idem", "candidato × opção", "candidato × opção",
           "ciclo, id_candidato, opcao_rank", f"regra_ligacao = {P1.REGRA_G1}"),
        be(P1.X45.CIR_BRUTO, "região de saúde (CIR), só lido", "DATASUS/TabNet",
           dados["manifesto_cir"]["data_download_utc"], f"{dados['diag_cir']['municipios']} municípios", "município",
           "co_ibge → co_cir", "-"),
        be(P1.X1.COORD_JSON, "centroides municipais do IBGE, só lido", "IBGE, API de malhas v3",
           str(dados["diag_coord"].get("data_download", "")), f"{dados['diag_coord'].get('municipios')} municípios",
           "município", "id", "centroide"),
    ]


def covariancias(res: dict) -> dict:
    """θ e blocos da covariância de bolsa, distância (e mesma UF nas referências), para recálculo nos testes."""
    out = {}
    for chave, r in res.items():
        if not r.get("ok") or chave not in ESPECS:
            continue
        termos = [t for t in (B, DIST, LOGDIST, "mesma_uf") if t in r["termos"]]
        k = [r["termos"].index(t) for t in termos]
        out[chave] = {"termos": termos, "theta": np.asarray(r["theta"])[k].tolist(),
                      "V_cluster_conjunto": np.asarray(r["V_conj"])[np.ix_(k, k)].tolist(),
                      "g_conjuntos": r["G_conj"]}
    return out


def remover_saidas_calculadas() -> None:
    for p in (OUT_CSV, FIG):
        if p.exists():
            p.unlink()
    if DIR_FIG.exists() and not any(DIR_FIG.iterdir()):
        DIR_FIG.rmdir()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--atualizar-doc", action="store_true", help="só regrava o doc 57x a partir das saídas")
    ap.add_argument("--pre-registro", action="store_true",
                    help="grava o doc 57x só com as decisões (antes de qualquer estimativa)")
    args = ap.parse_args(argv)
    if args.pre_registro:
        if OUT_RESUMO.exists():
            raise FalhaValidacao("VL_resumo.json já existe: o pré-registro só vale antes das estimativas")
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
    q1302, q1903 = VC.ler_quadros_c2()
    conf_antiga = VC.conferir_versao_antiga(dados["conj"], q1903)
    conf_a36 = VC.conferir_contra_a36(q1302)
    conj_p1_c, corr = VC.corrigir(dados["conj_p1"], q1302)
    log("quadro de 13/02 conferido e conjunto do P1 corrigido")
    resumo = {
        "etapa": "VL_escolha_localizacao_par",
        "natureza_dos_dados": NATUREZA,
        "estatuto": ESTATUTO,
        "data_execucao": DATA_EXECUCAO,
        "script": rel(Path(__file__)),
        "adendo": {"arquivo": rel(ADENDO_MD), "sha256": sha256(ADENDO_MD), "commit_de_congelamento": COMMIT_ADENDO},
        "protocolos": {rel(p): sha256(p) for p in (PROTOCOLO_52, PROTOCOLO_52B, ADENDO_52C, ADENDO_52D)},
        "conferencias": {"versao_antiga_do_conjunto": conf_antiga, "quadro_1302_contra_a36": conf_a36,
                         "correcao_ciclo2": {k: corr[k] for k in ("celulas_ciclo2_no_conjunto",
                                                                  "celulas_sem_linha_no_quadro_1302",
                                                                  "celulas_com_vagas_imediatas_diferentes",
                                                                  "imputadas")}},
        "decisoes": DECISOES,
        "notas_de_execucao": NOTAS_EXECUCAO,
        "especificacoes": ESPECS,
        "entradas": entradas(dados),
        "integridade": ("nada simulado nem imputado; data/ só lido; IVS do a08 (o arquivo local de IVS da auditoria 16 "
                        "não é lido); só agregados em output/ (sem nome, CPF, CRM nem pseudônimo de candidato); saídas "
                        "E9_*, P1_*, P1h_*, VC_* e VD_* não regravadas"),
        "linguagem": ("escolha condicional a se candidatar, dentro das vagas abertas; a bolsa mede o pacote do corte e o "
                      "incentivo marginal; a origem é preferência revelada, não efeito causal; não é efeito da "
                      "participação no PMM-E"),
        "tempo_execucao_nao_registrado": "fora do resumo para que duas execuções deem o mesmo hash",
    }

    # Portão (VL-5): nada novo antes dele.
    res: dict[str, dict] = {}
    D = P1.montar_desenho(dados["conj_p1"], dados["r1_p1"], None, dados)
    res["M1_antiga"] = ajustar("M1_emp", P1.matriz_modelo(D, dados, "M1"), D, log, com_score=False)
    del D
    gc.collect()
    idt: dict[str, dict] = {}
    for chave in ("M1_emp", "M1_c2", "M4_emp"):
        res[chave], idt[chave] = estimar_linha(chave, dados, conj_p1_c, log)
    port = portao(res, pd.read_csv(P1_EST, dtype={"ciclo": str}), pd.read_csv(P1H_CSV, dtype={"ciclo": str}),
                  pd.read_csv(VC_CSV, dtype={"ciclo": str}), pd.read_csv(VD_CSV, dtype={"ciclo": str}))
    resumo["portao"] = port
    log(f"portão: {port['status']}")
    if port["status"] != "PASSOU":
        remover_saidas_calculadas()
        resumo["saidas"] = {}
        gravar_json(OUT_RESUMO, resumo)
        atualizar_doc()
        print(f"{port['status']}: nada novo estimado (adendo 52e)", file=sys.stderr)
        return 3

    for chave in ESPECS:
        if chave not in res:
            res[chave], idt[chave] = estimar_linha(chave, dados, conj_p1_c, log)
    est = montar(res)
    sem = est[est["estimativa"].isna() & (est["status"] == "EXECUTADO")]
    if len(sem):
        raise FalhaValidacao(f"{len(sem)} linhas executadas sem estimativa")
    est.to_csv(OUT_CSV, index=False, float_format="%.10g")
    est = ler_est()
    resumo["identificacao"] = {k: v for k, v in idt.items() if v}
    resumo["score_bootstrap"] = {k: res[k].get("score_bootstrap", {}) for k in COM_SCORE}
    resumo["convergencia"] = {k: {"ok": bool(r["ok"]), "status": r.get("status"), "iteracoes": r.get("iteracoes"),
                                  "omitidas": r.get("omitidas", []), "n_efeitos_fixos": r.get("n_efeitos_fixos", 0),
                                  "grad_max": r.get("grad_max"), "decremento_final": r.get("decremento_final"),
                                  "partida": r.get("partida", "zero (estimar do script 25)"),
                                  "termos_sem_efeito_fixo": [t for t in r["termos"] if not t.startswith(PREFIXO_EF)],
                                  "nota": r.get("nota", "")} for k, r in res.items()}
    resumo["covariancias"] = covariancias(res)
    resumo["influencia_bolsa_por_conjunto"] = {k: res[k]["infl_bolsa"] for k in ESPECS if res[k].get("ok")}
    resumo["leitura"] = leitura(est)
    resumo["inferencia"] = {"principal": "sanduíche com cluster por conjunto de escolha (curso × ciclo), fator G/(G−1)",
                            "holm": FAMILIA_HOLM, "bky": FAMILIA_BKY,
                            "score_bootstrap": "Kline–Santos, H0: β = 0, Rademacher e Webb (funções do script 16)",
                            "z_bilateral_95": Z95}
    resumo["figura"] = figura(est, resumo["leitura"])
    resumo["como_ler"] = {FIG.name: COMO_LER}
    resumo["saidas"] = {rel(OUT_CSV): sha256(OUT_CSV), rel(FIG): resumo["figura"]["sha256"]}
    gravar_json(OUT_RESUMO, resumo)
    atualizar_doc()
    log(f"gravado: {rel(OUT_CSV)}, {rel(OUT_RESUMO)}, {rel(FIG)}, {rel(DOC)}")
    return 0


def ler_est() -> pd.DataFrame:
    return pd.read_csv(OUT_CSV, dtype={"ciclo": str, "referencia": str}, keep_default_na=True)


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
