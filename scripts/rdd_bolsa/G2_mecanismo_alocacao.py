"""Portão G2 (doc 51, T6.0): o mecanismo de alocação do PMM-E é replicável?

Pergunta do portão: a partir das escolhas (ordem de prioridade), das notas
(pontuação), da elegibilidade e das vagas de cada célula CNES × curso, dá para
reconstruir a alocação publicada da chamada com concordância ≥ 99% por ciclo?

O que o script faz, de forma determinística e só com arquivos do repositório:

1. lê os resultados publicados de cada chamada (candidato × opção) e os quadros
   de vagas com a divisão AC/ER/PCD das vagas imediatas;
2. implementa o mecanismo dos editais (aceitação adiada com prioridade da
   célula dada por ordem da opção, pontuação e desempate; vagas reservadas a
   ações afirmativas processadas na ordem do edital de cada ciclo; ver
   `MECANISMO` abaixo e o doc da auditoria);
3. compara a alocação reconstruída com a publicada, por ciclo e chamada, em
   uma grade fixa de especificações (capacidade ex ante ou efetiva; desempate
   pela classificação publicada ou por sorteio; com ou sem prioridade da 1ª
   opção; ordem das cotas);
4. tipifica as divergências;
5. deriva, como variáveis de mecanismo, a nota de corte de cada célula e a
   margem de cada candidato em relação ao corte da sua 1ª opção.

Regra do portão (doc 51, §2.3): nenhum contraste de outcome. O script não lê
CNES, produção, IVS, faixa da bolsa nem qualquer outcome; a faixa impressa no
quadro não é lida. Nenhum nome ou CPF é gravado: nome e CPF mascarado entram só
em memória, num hash que gera o mesmo pseudônimo `id_candidato` de
`escolhas_candidatos.parquet` (script 12). O tipo de inscrição em ação
afirmativa é gravado só como indicador (reserva sim/não), sem separar ER de PCD.

Saídas (`output/rdd_bolsa/`):
- `G2_alocacao_reconstruida.parquet`: uma linha por candidato × chamada;
- `G2_cortes_celula.csv`: uma linha por célula × chamada;
- `G2_resumo.json`: concordância, divergências, contagens e veredito;
e o relatório `docs/auditorias/G2_viabilidade_mecanismo.md`, gerado aqui.

Os arquivos em `data/` são somente lidos. Fora do `run_all.py` (portão).
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from collections import deque
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_EXECUCAO = "2026-10-19"
NATUREZA = "EMPIRICO"
SEMENTE = 20261019
N_SORTEIOS = 100
META = 0.99

_spec = importlib.util.spec_from_file_location("funil12", ROOT / "scripts" / "rdd_bolsa" / "12_construir_outcomes_funil.py")
f12 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(f12)

RAW_VAGAS = ROOT / "data" / "raw" / "aquisicao" / "vagas"
RAW_PMME = ROOT / "data" / "raw" / "pmm_e"
ESCOLHAS = ROOT / "output" / "rdd_bolsa" / "outcomes" / "escolhas_candidatos.parquet"
V_CELULA = ROOT / "output" / "rdd_bolsa" / "outcomes" / "outcomes_V_celula.parquet"

EDITAIS = {
    "ciclo_1": ROOT / "data" / "raw" / "aquisicao" / "normas_ivs" / "edital_sgtes_03_2025_ciclo1_dou.html",
    "ciclo_1_pdf": ROOT / "data" / "raw" / "aquisicao" / "ivs_regra" / "edital_sgtes_03_2025_dou.pdf",
    "ciclo_1_retificacao": ROOT / "data" / "raw" / "aquisicao" / "normas_ivs" / "edital_sgtes_03_2025_retificacao_dou.html",
    "ciclo_2_pagina": ROOT / "data" / "raw" / "aquisicao" / "ivs_regra" / "edital_sgtes_01_2026_ciclo2.html",
    "ciclo_3": ROOT / "data" / "raw" / "aquisicao" / "ivs_regra" / "edital_sgtes_06_2026_edital_28_2026_ciclo3.html",
}

OUT_DIR = ROOT / "output" / "rdd_bolsa"
OUT_ALOC = OUT_DIR / "G2_alocacao_reconstruida.parquet"
OUT_CORTES = OUT_DIR / "G2_cortes_celula.csv"
OUT_RESUMO = OUT_DIR / "G2_resumo.json"
OUT_DOC = ROOT / "docs" / "auditorias" / "G2_viabilidade_mecanismo.md"

CHAVE = ["co_cnes_7d", "cod_curso"]
RESERVA = ("ER", "PCD")

# Ordem de processamento das vagas reservadas (item 5.6 de cada edital).
AC_PRIMEIRO = "AC_PRIMEIRO"            # ciclo 3: AC, depois ações afirmativas, depois remanescentes
RESERVA_PRIMEIRO = "RESERVA_PRIMEIRO"  # ciclo 1: ações afirmativas, depois AC, depois remanescentes

# --------------------------------------------------------------------------
# Chamadas analisadas
# --------------------------------------------------------------------------
# `alvo`: regra que define a alocação publicada que o mecanismo deve reproduzir.
# `tipo_vaga`: como ler o tipo de vaga (AC, ER, PCD) da alocação publicada.
CHAMADAS: list[dict[str, Any]] = [
    {
        "id": "c1_ch1", "ciclo": 1, "chamada": 1, "principal": True,
        "arquivo": RAW_VAGAS / "2025_ciclo1_chamada1_alocacao_retificada_subjudice.xlsx", "aba": 0,
        "col_pontuacao": ("PONTUACAO NO BAREMA GERAL",), "col_classificacao": ("CLASSIFICACAO AMPLA CONCORRENCIA",),
        "col_status": ("RESULTADO",), "col_status2": ("ALOCACAO",),
        "alvo": "RESULTADO começa com 'CLASSIFICAÇÃO' (resultado do processamento eletrônico; inclui os 59 locais "
                "depois desconsiderados pela gestão)",
        "quadro": RAW_VAGAS / "2025_ciclo1_chamada1_vagas.xlsx", "quadro_aba": 0,
        "ordem_edital": RESERVA_PRIMEIRO, "ordem_documentada": True,
        "fonte_ordem": "Edital SGTES/MS nº 3/2025, item 5.6 (1. ações afirmativas; 2. ampla concorrência; 3. remanescentes)",
    },
    {
        "id": "c2_ch1", "ciclo": 2, "chamada": 1, "principal": True,
        "arquivo": RAW_PMME / "resultado-final-pmme-2o-ciclo-25-05.xlsx", "aba": "Classificados",
        "col_pontuacao": ("PONTUACAO FINAL",), "col_classificacao": ("CLASSIFICACAO",),
        "col_status": ("SITUACAO",), "col_status2": None,
        "alvo": "SITUAÇÃO começa com 'ALOCADO' (AC, ER, PCD)",
        "quadro": RAW_PMME / "2026_ciclo2_chamada1_vagas_retificadas.xlsx", "quadro_aba": 0,
        "ordem_edital": AC_PRIMEIRO, "ordem_documentada": False,
        "fonte_ordem": "texto do Edital nº 3/2026 (ciclo 2) ausente do repositório (só a página de anexos); "
                       "adotada a ordem do edital mais recente (ciclo 3) e relatada a alternativa",
    },
    {
        "id": "c3_ch1", "ciclo": 3, "chamada": 1, "principal": True,
        "arquivo": RAW_PMME / "2026_ciclo3_chamada1_resultado_final_sub_judice.xlsx", "aba": "Classificados",
        "col_pontuacao": ("PONTUACAO NO BAREMA GERAL",), "col_classificacao": ("CLASSIFICACAO",),
        "col_status": ("SITUACAO",), "col_status2": None,
        "alvo": "SITUAÇÃO começa com 'ALOCADO' (AC, ER, PCD); 'SUB JUDICE' fica fora do alvo e é tipificado",
        "quadro": RAW_PMME / "2026_ciclo3_chamada1_vagas_retificadas.xlsx", "quadro_aba": 0,
        "ordem_edital": AC_PRIMEIRO, "ordem_documentada": True,
        "fonte_ordem": "Edital nº 28/2026, item 5.6 (I ampla concorrência; II ações afirmativas; III remanescentes)",
    },
    {
        "id": "c1_ch2", "ciclo": 1, "chamada": 2, "principal": False,
        "arquivo": RAW_PMME / "2025_ciclo1_chamada2_classificacao_final.xlsx", "aba": "ALOCADOS",
        "col_pontuacao": ("PONTUACAO NO BAREMA GERAL",), "col_classificacao": ("CLASSIFICACAO AMPLA CONCORRENCIA",),
        "col_status": ("SITUACAO",), "col_status2": None,
        "alvo": "SITUAÇÃO começa com 'ALOCADO(A) EM' (AC, ER, PCD); o título da planilha diz 'ALOCAÇÃO "
                "PRELIMINAR DOS CANDIDATOS - 2ª CHAMADA', apesar do nome do arquivo",
        "quadro": None, "quadro_aba": None,
        "ordem_edital": RESERVA_PRIMEIRO, "ordem_documentada": True,
        "fonte_ordem": "Edital SGTES/MS nº 3/2025, item 5.6",
    },
    {
        "id": "c2_ch2", "ciclo": 2, "chamada": 2, "principal": False,
        "arquivo": RAW_PMME / "2026_ciclo2_chamada2_resultado_final.xlsx", "aba": "Classificados",
        "col_pontuacao": ("PONTUACAO FINAL",), "col_classificacao": ("CLASSIFICACAO",),
        "col_status": ("SITUACAO",), "col_status2": None,
        "alvo": "SITUAÇÃO começa com 'ALOCADO' (o arquivo não diz o tipo de vaga)",
        "quadro": RAW_PMME / "2026_ciclo2_chamada2_vagas.xlsx", "quadro_aba": 0,
        "ordem_edital": AC_PRIMEIRO, "ordem_documentada": False,
        "fonte_ordem": "como no ciclo 2, 1ª chamada",
    },
]

# Trechos dos editais que definem o mecanismo (conferidos por teste contra os arquivos).
TRECHOS_EDITAL = {
    "ciclo_1": [
        ("4.1.3", "facultado ao candidato a indicação de até 2 (dois) locais de atuação"),
        ("4.1.3.4", "poderá recebê-la por remanejamento"),
        ("4.1.7", "observado a ordem de classificação e as vagas disponíveis"),
        ("5.2.5", "Em caso de empate serão considerados os seguintes critérios"),
        ("5.2.5 II", "candidatos que possuírem maior idade"),
        ("5.4", "identificada como vaga remanescente de cota"),
        ("5.5", "concorrerão, concomitantemente, às vagas destinadas à ampla concorrência"),
        ("5.6", "Vagas destinadas às ações afirmativas"),
        ("5.7", "as vagas remanescentes poderão ser redistribuídas para municípios com cadastro de reserva"),
    ],
    "ciclo_3": [
        ("4.1.3", "devendo a segunda indicação ser"),
        ("4.1.6", "respeitada a ordem de classificação e observada a disponibilidade de vagas"),
        ("5.2.5", "Em caso de empate, serão considerados os seguintes critérios"),
        ("5.2.5 III", "candidatos que possuírem maior idade"),
        ("5.6 I", "Serão processadas, inicialmente, as vagas destinadas à ampla"),
        ("5.7", "remanescentes poderão ser redistribuídas para municípios com cadastro de reserva"),
    ],
}

MECANISMO = (
    "Aceitação adiada (deferred acceptance) com até 2 opções por candidato, na ordem de prioridade escolhida. "
    "Cada célula CNES × curso ordena quem a escolheu por (i) ordem da opção — quem a pôs em 1º lugar vem antes de "
    "quem a pôs em 2º —, (ii) pontuação, decrescente, e (iii) desempate. Com 2 opções, essa prioridade e sem "
    "vagas reservadas, o resultado é idêntico ao do mecanismo de Boston em duas rodadas (1ª opções primeiro, depois "
    "2ª opções nas vagas que sobraram); com vagas reservadas os dois podem diferir, e Boston é relatado como "
    "variante. As vagas reservadas (ER, PCD) são processadas na ordem do item 5.6 de cada edital; quem se "
    "inscreve em reserva concorre também às vagas de ampla concorrência (item 5.5); vaga reservada sem candidato "
    "vai à ampla concorrência como remanescente de cota (item 5.4). Desempate do edital (item 5.2.5: mesma UF de "
    "residência ou de nascimento; maior idade) não é observável; a especificação principal usa a classificação "
    "publicada da célula, que embute esse desempate, e a sensibilidade usa sorteio."
)


# --------------------------------------------------------------------------
# Leitura
# --------------------------------------------------------------------------

def _coluna_opcional(cab: list[str], nomes: tuple[str, ...] | None) -> int | None:
    if not nomes:
        return None
    try:
        return f12.coluna(cab, *nomes)
    except KeyError:
        return None


def _tipo_inscricao(valor: object) -> str:
    t = f12.texto_norm(valor)
    return t if t in ("AC", "ER", "PCD") else "NA"


def _tipo_vaga_publicada(texto: str) -> str | None:
    """Tipo de vaga lido do status publicado: AC, ER, PCD ou None (sem tipo)."""
    if "COTA ETNICO" in texto or texto.endswith(" ER"):
        return "ER"
    if "COTA PCD" in texto or texto.endswith(" PCD"):
        return "PCD"
    if "AMPLA" in texto or texto.endswith(" AC"):
        return "AC"
    return None


def ler_resultado(ch: dict[str, Any]) -> pd.DataFrame:
    """Linhas candidato × opção da chamada, com a pessoa só em hash (como no script 12)."""
    cab, _, linhas = f12.ler_aba(ch["arquivo"], ch["aba"])
    i_cnes, i_curso = f12.coluna(cab, "CNES"), f12.coluna(cab, "CURSO")
    i_ordem = f12.coluna(cab, "ORDEM DE PRIORIDADE ESCOLHIDA")
    i_pont = f12.coluna(cab, *ch["col_pontuacao"])
    i_class = f12.coluna(cab, *ch["col_classificacao"], prefixo=True)
    i_status = f12.coluna(cab, *ch["col_status"])
    i_status2 = _coluna_opcional(cab, ch["col_status2"])
    i_tipo = f12.coluna(cab, "TIPO DE INSCRICAO")
    i_nome = f12.coluna(cab, "NOME CANDIDATO A", "NOME")
    i_cpf = f12.coluna(cab, "CPF", "CPF MASC", prefixo=True)
    registros, sem_chave = [], 0
    for r in linhas:
        cnes, curso = f12.chave_cnes(f12.valor(r, i_cnes)), f12.chave_curso(f12.valor(r, i_curso))
        if cnes is None or curso is None:
            sem_chave += 1
            continue
        bruto_pont = f12.valor(r, i_pont)
        pont = f12.numero(bruto_pont)
        status = f12.texto_norm(f12.valor(r, i_status))
        status2 = f12.texto_norm(f12.valor(r, i_status2)) if i_status2 is not None else ""
        pessoa = hashlib.sha256(
            (f12.texto_norm(f12.valor(r, i_nome)) + "|" + str(f12.valor(r, i_cpf) or "").strip()).encode("utf-8")
        ).hexdigest()
        if ch["id"] == "c1_ch1":
            alvo = status.startswith("CLASSIFICACAO")
            tipo_pub = _tipo_vaga_publicada(status) if alvo else None
        elif ch["id"] == "c1_ch2":
            alvo = status.startswith("ALOCADO A EM")
            tipo_pub = _tipo_vaga_publicada(status) if alvo else None
        else:
            alvo = status.startswith("ALOCADO")
            tipo_pub = _tipo_vaga_publicada(status) if alvo else None
        registros.append({
            "_pessoa": pessoa,
            "co_cnes_7d": cnes,
            "cod_curso": curso,
            "opcao_rank": f12.opcao(f12.valor(r, i_ordem)),
            "pontuacao": pont,
            "sem_pre_requisito": bool(np.isnan(pont) and "PRE REQUISITO" in f12.texto_norm(bruto_pont)),
            "classificacao_publicada": f12.numero(f12.valor(r, i_class)),
            "tipo_inscricao": _tipo_inscricao(f12.valor(r, i_tipo)),
            "status": status,
            "status2": status2,
            "alvo": bool(alvo),
            "tipo_vaga_publicada": tipo_pub,
            "sub_judice": status == "SUB JUDICE",
            "confirmado": status2.startswith("LOCAL DE ATUACAO CONFIRMADO"),
            "desconsiderado": status2.startswith("LOCAL DE ATUACAO DESCONSIDERADO"),
        })
    df = pd.DataFrame(registros)
    df.attrs["linhas_sem_chave"] = sem_chave
    return df


def ler_quadro_tipos(caminho: Path, aba: str | int) -> pd.DataFrame:
    """Vagas imediatas por tipo (TOTAL, AC, ER, PCD) e total de cadastro reserva por célula.

    Os blocos são localizados pela linha acima do cabeçalho ('VAGAS IMEDIATAS',
    'CADASTRO RESERVA'); dentro de cada bloco, as colunas AC, ER e PCD são as
    três que seguem a coluna TOTAL, conferidas pelo nome.
    """
    cab, acima, linhas = f12.ler_aba(caminho, aba)
    i_cnes, i_curso = f12.coluna(cab, "CNES"), f12.coluna(cab, "CURSO")
    totais = [i for i, c in enumerate(cab) if c == "TOTAL"]
    blocos: dict[str, int] = {}
    for i in totais:
        rotulo = acima[i] if i < len(acima) else ""
        if "IMEDIATA" in rotulo:
            blocos["imed"] = i
        elif "RESERVA" in rotulo:
            blocos["cr"] = i
    if "imed" not in blocos or "cr" not in blocos:
        raise KeyError(f"blocos de vagas não localizados em {f12.rel(caminho)}")
    for b, i in blocos.items():
        if cab[i + 1:i + 4] != ["AC", "ER", "PCD"]:
            raise KeyError(f"colunas AC/ER/PCD fora do lugar no bloco {b} de {f12.rel(caminho)}")
    reg = []
    for r in linhas:
        cnes, curso = f12.chave_cnes(f12.valor(r, i_cnes)), f12.chave_curso(f12.valor(r, i_curso))
        if cnes is None or curso is None:
            continue
        i, j = blocos["imed"], blocos["cr"]
        reg.append({
            "co_cnes_7d": cnes, "cod_curso": curso,
            "vagas_imediatas": f12.numero(f12.valor(r, i)),
            "vagas_imediatas_ac": f12.numero(f12.valor(r, i + 1)),
            "vagas_imediatas_er": f12.numero(f12.valor(r, i + 2)),
            "vagas_imediatas_pcd": f12.numero(f12.valor(r, i + 3)),
            "vagas_cr": f12.numero(f12.valor(r, j)),
            "vagas_cr_ac": f12.numero(f12.valor(r, j + 1)),
            "vagas_cr_er": f12.numero(f12.valor(r, j + 2)),
            "vagas_cr_pcd": f12.numero(f12.valor(r, j + 3)),
        })
    q = pd.DataFrame(reg)
    if q.duplicated(CHAVE).any():
        raise AssertionError(f"quadro {f12.rel(caminho)} com chave duplicada")
    for b in ("imediatas", "cr"):
        soma = q[[f"vagas_{b}_ac", f"vagas_{b}_er", f"vagas_{b}_pcd"]].sum(axis=1)
        if not np.allclose(soma, q[f"vagas_{b}"]):
            raise AssertionError(f"quadro {f12.rel(caminho)}: AC + ER + PCD ≠ TOTAL ({b})")
    return q.sort_values(CHAVE).reset_index(drop=True)


def pseudonimos(res: pd.DataFrame, ciclo: int, mapa_ch1: dict[str, str] | None) -> dict[str, str]:
    """Mesmo pseudônimo do script 12 na 1ª chamada; na 2ª, o da 1ª quando a pessoa já estava lá."""
    pessoas = sorted(res["_pessoa"].unique())
    if mapa_ch1 is None:
        return {h: f"c{ciclo}_{i + 1:05d}" for i, h in enumerate(pessoas)}
    novos = [h for h in pessoas if h not in mapa_ch1]
    mapa = {h: mapa_ch1[h] for h in pessoas if h in mapa_ch1}
    mapa.update({h: f"c{ciclo}ch2_{i + 1:05d}" for i, h in enumerate(novos)})
    return mapa


# --------------------------------------------------------------------------
# Mecanismo
# --------------------------------------------------------------------------

def escolher(proponentes: list[str], vagas: tuple[int, int, int], chave: dict[str, tuple], tipo: dict[str, str],
             ordem: str) -> dict[str, str]:
    """Função de escolha da célula: quem fica e em que tipo de vaga.

    `vagas` = (AC, ER, PCD). Tipos devolvidos: 'AC', 'ER', 'PCD' e 'AC_REM'
    (vaga reservada sem candidato da reserva, passada à ampla concorrência).
    """
    n_ac, n_er, n_pcd = vagas
    ordenados = sorted(proponentes, key=lambda p: chave[p])
    escolhidos: dict[str, str] = {}

    def reserva(lista: list[str]) -> None:
        for t, n in (("ER", n_er), ("PCD", n_pcd)):
            for p in [q for q in lista if tipo[q] == t and q not in escolhidos][:n]:
                escolhidos[p] = t

    if ordem == AC_PRIMEIRO:
        for p in ordenados[:n_ac]:
            escolhidos[p] = "AC"
        reserva(ordenados)
    elif ordem == RESERVA_PRIMEIRO:
        reserva(ordenados)
        for p in [q for q in ordenados if q not in escolhidos][:n_ac]:
            escolhidos[p] = "AC"
    else:
        raise ValueError(ordem)
    usadas = sum(1 for t in escolhidos.values() if t in RESERVA)
    sobra = n_er + n_pcd - usadas
    for p in [q for q in ordenados if q not in escolhidos][:max(sobra, 0)]:
        escolhidos[p] = "AC_REM"
    return escolhidos


def alocar(cand: pd.DataFrame, vagas: dict[tuple[str, int], tuple[int, int, int]], ordem: str,
           desempate: str = "classificacao_publicada", prioridade_1a_opcao: bool = True,
           sorteio: dict[str, float] | None = None) -> dict[str, tuple[tuple[str, int], str]]:
    """Aceitação adiada (proposta pelos candidatos) com a função de escolha `escolher`.

    `cand`: linhas candidato × opção elegíveis, com id_candidato, celula (tupla),
    opcao_rank, pontuacao, tipo_inscricao, classificacao_publicada.
    Devolve {id_candidato: (célula, tipo de vaga)} para os alocados.
    """
    prefs: dict[str, list[tuple[str, int]]] = {}
    chave: dict[tuple[str, int], dict[str, tuple]] = {}
    tipo: dict[str, str] = {}
    for r in cand.sort_values(["id_candidato", "opcao_rank"]).itertuples(index=False):
        prefs.setdefault(r.id_candidato, []).append(r.celula)
        tipo[r.id_candidato] = r.tipo_inscricao
        if desempate == "classificacao_publicada":
            d = r.classificacao_publicada if not np.isnan(r.classificacao_publicada) else np.inf
        elif desempate == "sorteio":
            d = sorteio[r.id_candidato]
        else:
            raise ValueError(desempate)
        chave.setdefault(r.celula, {})[r.id_candidato] = (
            r.opcao_rank if prioridade_1a_opcao else 0, -r.pontuacao, d, r.id_candidato)
    proximo = {p: 0 for p in prefs}
    retidos: dict[tuple[str, int], dict[str, str]] = {}
    livres = deque(sorted(prefs))
    while livres:
        p = livres.popleft()
        if proximo[p] >= len(prefs[p]):
            continue
        c = prefs[p][proximo[p]]
        proximo[p] += 1
        v = vagas.get(c, (0, 0, 0))
        if sum(v) <= 0:
            livres.append(p)
            continue
        atuais = list(retidos.get(c, {})) + [p]
        escolhidos = escolher(atuais, v, chave[c], tipo, ordem)
        retidos[c] = escolhidos
        for q in atuais:
            if q not in escolhidos:
                livres.append(q)
    return {p: (c, t) for c, d in retidos.items() for p, t in d.items()}


def boston(cand: pd.DataFrame, vagas: dict[tuple[str, int], tuple[int, int, int]], ordem: str) -> dict:
    """Mecanismo de Boston em duas rodadas (1ª opções, depois 2ª opções nas vagas restantes).

    Só para a verificação de equivalência com `alocar` (com prioridade da 1ª opção).
    """
    out: dict[str, tuple[tuple[str, int], str]] = {}
    restantes = dict(vagas)
    tipo = dict(zip(cand["id_candidato"], cand["tipo_inscricao"]))
    for o in (1, 2):
        sub = cand[(cand["opcao_rank"] == o) & ~cand["id_candidato"].isin(out)]
        for c, g in sub.groupby("celula", sort=True):
            v = restantes.get(c, (0, 0, 0))
            if sum(v) <= 0:
                continue
            ch = {r.id_candidato: (0, -r.pontuacao,
                                   r.classificacao_publicada if not np.isnan(r.classificacao_publicada) else np.inf,
                                   r.id_candidato) for r in g.itertuples(index=False)}
            esc = escolher(list(ch), v, ch, tipo, ordem)
            for p, t in esc.items():
                out[p] = (c, t)
            usados = {"AC": 0, "ER": 0, "PCD": 0}
            for t in esc.values():
                usados["AC" if t == "AC_REM" else t] += 1
            n_ac, n_er, n_pcd = v
            # vagas reservadas usadas como remanescente saem da reserva
            rem = sum(1 for t in esc.values() if t == "AC_REM")
            usados["AC"] -= rem
            sobra_er = n_er - usados["ER"]
            sobra_pcd = n_pcd - usados["PCD"]
            tira = rem
            tira_er = min(tira, sobra_er)
            sobra_er -= tira_er
            sobra_pcd -= tira - tira_er
            restantes[c] = (n_ac - usados["AC"], sobra_er, sobra_pcd)
    return out


# --------------------------------------------------------------------------
# Capacidades
# --------------------------------------------------------------------------

def capacidade_ex_ante(quadro: pd.DataFrame) -> dict[tuple[str, int], tuple[int, int, int]]:
    return {(r.co_cnes_7d, r.cod_curso): (int(r.vagas_imediatas_ac), int(r.vagas_imediatas_er),
                                          int(r.vagas_imediatas_pcd))
            for r in quadro.fillna(0).itertuples(index=False)}


def tipar_acrescimo(extra: int, cr: tuple[int, int, int], regra: str) -> tuple[int, int, int]:
    """Tipos (AC, ER, PCD) das vagas acrescidas a uma célula além das imediatas.

    `divisao_cr`: segue a divisão AC/ER/PCD do cadastro reserva do quadro — se o
    acréscimo cobre todo o cadastro reserva, a divisão inteira (o que passar dela
    é AC); se cobre só parte, preenche AC, depois ER, depois PCD. `tudo_ac`: todas
    as vagas acrescidas são de ampla concorrência.
    """
    if regra == "tudo_ac":
        return (extra, 0, 0)
    cr_ac, cr_er, cr_pcd = cr
    if extra >= cr_ac + cr_er + cr_pcd:
        return (cr_ac + extra - (cr_ac + cr_er + cr_pcd), cr_er, cr_pcd)
    ac = min(extra, cr_ac)
    er = min(extra - ac, cr_er)
    pcd = min(extra - ac - er, cr_pcd)
    return (ac + (extra - ac - er - pcd), er, pcd)


def capacidade_efetiva(quadro: pd.DataFrame | None, publicado: pd.DataFrame,
                       regra: str = "divisao_cr") -> dict[tuple[str, int], tuple[int, int, int]]:
    """Capacidade efetiva ex post: imediatas do quadro, acrescidas do que a publicação alocou acima delas.

    `publicado`: uma linha por alocação no alvo (celula, tipo_vaga_publicada).
    As vagas acrescidas são tipadas por `tipar_acrescimo`. Sem quadro (ciclo 1,
    2ª chamada), a capacidade é a própria contagem publicada por tipo.
    """
    n_pub = publicado.groupby("celula").size()
    if quadro is None:
        cap = {}
        for c, g in publicado.groupby("celula"):
            t = g["tipo_vaga_publicada"].fillna("AC").value_counts()
            cap[c] = (int(t.get("AC", 0)), int(t.get("ER", 0)), int(t.get("PCD", 0)))
        return cap
    cap = capacidade_ex_ante(quadro)
    cr = {(r.co_cnes_7d, r.cod_curso): (int(r.vagas_cr_ac), int(r.vagas_cr_er), int(r.vagas_cr_pcd))
          for r in quadro.fillna(0).itertuples(index=False)}
    for c, n in n_pub.items():
        ac, er, pcd = cap.get(c, (0, 0, 0))
        extra = int(n) - (ac + er + pcd)
        if extra > 0:
            a, e, p = tipar_acrescimo(extra, cr.get(c, (0, 0, 0)), regra)
            cap[c] = (ac + a, er + e, pcd + p)
    return cap


# --------------------------------------------------------------------------
# Comparação, tipos de divergência, cortes e margens
# --------------------------------------------------------------------------

def concordancia(cand_todos: pd.DataFrame, sim: dict, ids: list[str]) -> pd.Series:
    pub = cand_todos[cand_todos["alvo"]].groupby("id_candidato")["celula"].first().to_dict()
    return pd.Series({p: sim.get(p, (None, None))[0] == pub.get(p) for p in ids})


def tipificar(cand_todos: pd.DataFrame, sim: dict, ids: list[str], quadro: pd.DataFrame | None,
              considerar_5_7: bool) -> dict[str, str]:
    """Tipo de cada divergência, na ordem: publicação com o candidato alocado em mais de uma célula;
    sub judice; redistribuição do item 5.7 (só ex ante); ação afirmativa; efeito em cadeia de outra
    divergência; não explicada."""
    pub = cand_todos[cand_todos["alvo"]].groupby("id_candidato")["celula"].first().to_dict()
    n_pub = cand_todos[cand_todos["alvo"]].groupby("id_candidato").size()
    duplicados = set(n_pub[n_pub > 1].index)
    celulas = cand_todos.groupby("id_candidato")["celula"].apply(set).to_dict()
    sj = set(cand_todos.loc[cand_todos["sub_judice"], "id_candidato"])
    reserva_ids = set(cand_todos.loc[cand_todos["tipo_inscricao"].isin(RESERVA), "id_candidato"])
    acima = set()
    if quadro is not None:
        imed = {(r.co_cnes_7d, r.cod_curso): r.vagas_imediatas for r in quadro.fillna(0).itertuples(index=False)}
        n_pub = cand_todos[cand_todos["alvo"]].groupby("celula").size()
        acima = {c for c, n in n_pub.items() if n > imed.get(c, 0)}
    diverg = [p for p in ids if sim.get(p, (None, None))[0] != pub.get(p)]
    tipos: dict[str, str] = {}
    for p in diverg:
        cs = set(celulas.get(p, set())) | {pub.get(p), sim.get(p, (None, None))[0]}
        cs.discard(None)
        if p in duplicados:
            tipos[p] = "publicacao_alocado_em_duas_celulas"
        elif p in sj:
            tipos[p] = "sub_judice"
        elif considerar_5_7 and cs & acima:
            tipos[p] = "redistribuicao_cadastro_reserva_item_5_7"
        elif p in reserva_ids or any(q in reserva_ids and (cs & (celulas.get(q, set()))) for q in diverg if q != p):
            tipos[p] = "acao_afirmativa"
    pendentes = [p for p in diverg if p not in tipos]
    mudou = True
    while mudou:
        mudou = False
        for p in list(pendentes):
            cs = set(celulas.get(p, set())) | {pub.get(p), sim.get(p, (None, None))[0]}
            if any(cs & set(celulas.get(q, set())) for q in tipos):
                tipos[p] = "efeito_em_cadeia"
                pendentes.remove(p)
                mudou = True
    for p in pendentes:
        tipos[p] = "nao_explicada"
    return tipos


def cortes_e_margens(cand: pd.DataFrame, sim: dict, vagas: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Nota de corte por célula (vagas de ampla concorrência) e margem da 1ª opção de cada candidato.

    Proponentes de uma célula: quem a listou e não ficou numa opção que prefere.
    Corte ativo: algum proponente foi recusado. O corte é a prioridade do último
    admitido em vaga de ampla concorrência (AC ou remanescente de cota): par
    (ordem da opção, pontuação). Margem da 1ª opção = pontuação − pontuação de
    corte, definida só quando o corte está entre candidatos de 1ª opção.
    """
    rank_aloc = {}
    for r in cand.itertuples(index=False):
        if sim.get(r.id_candidato, (None, None))[0] == r.celula:
            rank_aloc[r.id_candidato] = r.opcao_rank
    linhas = []
    for c, g in cand.groupby("celula", sort=True):
        v = vagas.get(c, (0, 0, 0))
        prop = g.loc[(g["id_candidato"].map(lambda p: rank_aloc.get(p, 99)) >= g["opcao_rank"]).astype(bool)]
        adm = prop.loc[prop["id_candidato"].map(lambda p: sim.get(p, (None, None))[0] == c).astype(bool)]
        adm_geral = adm.loc[adm["id_candidato"].map(lambda p: sim[p][1] in ("AC", "AC_REM")).astype(bool)]
        recusados = len(prop) - len(adm)
        linha = {
            "co_cnes_7d": c[0], "cod_curso": c[1],
            "vagas_ac": v[0], "vagas_reserva": v[1] + v[2], "vagas_total": sum(v),
            "n_cand_1a_opcao": int((g["opcao_rank"] == 1).sum()), "n_cand_2a_opcao": int((g["opcao_rank"] == 2).sum()),
            "n_proponentes": len(prop), "n_admitidos": len(adm), "n_admitidos_vaga_geral": len(adm_geral),
            "n_admitidos_reserva": len(adm) - len(adm_geral), "n_recusados": recusados,
            "corte_ativo": int(recusados > 0),
        }
        if sum(v) == 0:
            linha.update(corte_opcao=np.nan, corte_pontuacao=np.nan, n_empatados_no_corte=np.nan,
                         n_admitidos_no_corte=np.nan, motivo_corte="célula sem vaga efetiva: ninguém é admitido")
        elif recusados == 0:
            linha.update(corte_opcao=np.nan, corte_pontuacao=np.nan, n_empatados_no_corte=np.nan,
                         n_admitidos_no_corte=np.nan, motivo_corte="sem corte ativo: nenhum proponente recusado")
        elif adm_geral.empty:
            linha.update(corte_opcao=np.nan, corte_pontuacao=np.nan, n_empatados_no_corte=np.nan,
                         n_admitidos_no_corte=np.nan,
                         motivo_corte="corte ativo sem admitido em vaga geral (só reserva): corte geral indefinido")
        else:
            ult = adm_geral.sort_values(["opcao_rank", "pontuacao"], ascending=[False, True]).iloc[0]
            emp = prop[(prop["opcao_rank"] == ult["opcao_rank"]) & (prop["pontuacao"] == ult["pontuacao"])]
            linha.update(corte_opcao=int(ult["opcao_rank"]), corte_pontuacao=float(ult["pontuacao"]),
                         n_empatados_no_corte=len(emp),
                         n_admitidos_no_corte=int(emp["id_candidato"].map(lambda p: sim.get(p, (None,))[0] == c).sum()),
                         motivo_corte="")
        linhas.append(linha)
    cortes = pd.DataFrame(linhas)
    idx = cortes.set_index(CHAVE)
    marg = []
    for r in cand[cand["opcao_rank"] == 1].itertuples(index=False):
        k = idx.loc[r.celula]
        m, motivo = np.nan, ""
        if k["vagas_total"] == 0:
            motivo = "1a opção sem vaga efetiva"
        elif k["corte_ativo"] == 0:
            motivo = "1a opção sem corte ativo (nenhum proponente recusado)"
        elif np.isnan(k["corte_opcao"]):
            motivo = "1a opção com corte geral indefinido (só reserva admitida)"
        elif k["corte_opcao"] == 2:
            motivo = "corte da 1a opção entre candidatos de 2a opção: todo candidato de 1a opção é admitido"
        else:
            m = float(r.pontuacao - k["corte_pontuacao"])
        marg.append({"id_candidato": r.id_candidato, "margem_1a_opcao": m, "motivo_margem": motivo,
                     "admitido_1a_opcao": int(sim.get(r.id_candidato, (None, None))[0] == r.celula)})
    return cortes, pd.DataFrame(marg)


# --------------------------------------------------------------------------
# Execução
# --------------------------------------------------------------------------

def preparar(ch: dict[str, Any], mapa_ch1: dict[int, dict[str, str]]) -> tuple[pd.DataFrame, pd.DataFrame | None, dict]:
    res = ler_resultado(ch)
    mapa = pseudonimos(res, ch["ciclo"], mapa_ch1.get(ch["ciclo"]) if ch["chamada"] == 2 else None)
    if ch["chamada"] == 1:
        mapa_ch1[ch["ciclo"]] = mapa
    res["id_candidato"] = res["_pessoa"].map(mapa)
    res["celula"] = list(zip(res["co_cnes_7d"], res["cod_curso"]))
    res["elegivel"] = res["pontuacao"].notna() & res["opcao_rank"].notna()
    quadro = ler_quadro_tipos(ch["quadro"], ch["quadro_aba"]) if ch["quadro"] is not None else None
    diag = {
        "linhas": int(len(res)), "linhas_sem_chave": int(res.attrs["linhas_sem_chave"]),
        "candidatos": int(res["id_candidato"].nunique()),
        "candidatos_inelegiveis_sem_pontuacao": int(res.loc[~res["elegivel"], "id_candidato"].nunique()),
        "linhas_no_alvo": int(res["alvo"].sum()), "candidatos_no_alvo": int(res.loc[res["alvo"], "id_candidato"].nunique()),
        "candidatos_com_mais_de_uma_alocacao_publicada": int((res[res["alvo"]].groupby("id_candidato").size() > 1).sum()),
        "pontuacao_varia_entre_opcoes_do_candidato": int((res.groupby("id_candidato")["pontuacao"].nunique() > 1).sum()),
        "inscritos_em_reserva": int(res.loc[res["tipo_inscricao"].isin(RESERVA), "id_candidato"].nunique()),
        "sub_judice": int(res["sub_judice"].sum()),
    }
    if ch["chamada"] == 2:
        diag["candidatos_ja_presentes_na_1a_chamada"] = int(sum(h in mapa_ch1.get(ch["ciclo"], {})
                                                               for h in res["_pessoa"].unique()))
    if quadro is not None:
        diag["celulas_no_quadro"] = int(len(quadro))
        diag["vagas_imediatas_quadro"] = int(quadro["vagas_imediatas"].sum())
        diag["vagas_cr_quadro"] = int(quadro["vagas_cr"].sum())
        fora = ~res["celula"].isin(set(zip(quadro["co_cnes_7d"], quadro["cod_curso"])))
        diag["linhas_com_celula_fora_do_quadro"] = int(fora.sum())
    if ch["id"] == "c1_ch1":
        diag["no_alvo_confirmados"] = int((res["alvo"] & res["confirmado"]).sum())
        diag["no_alvo_desconsiderados_pela_gestao"] = int((res["alvo"] & res["desconsiderado"]).sum())
    return res.drop(columns=["_pessoa"]), quadro, diag


def conferir_com_escolhas(res: pd.DataFrame, ciclo: int) -> dict[str, Any]:
    """A 1ª chamada lida aqui é a mesma de `escolhas_candidatos.parquet` (pseudônimo, célula, opção, nota)."""
    esc = pd.read_parquet(ESCOLHAS, columns=["ciclo", "id_candidato", "co_cnes_7d", "cod_curso", "opcao_rank",
                                             "pontuacao", "alocado", "classificado"])
    esc = esc[esc["ciclo"] == ciclo]
    k = ["id_candidato", "co_cnes_7d", "cod_curso", "opcao_rank"]
    m = res.merge(esc, on=k, how="outer", indicator=True, suffixes=("", "_e9"))
    ambos = m[m["_merge"] == "both"]
    alocado_e9 = ambos["classificado"] if ciclo == 1 else ambos["alocado"]
    return {
        "linhas_g2": int(len(res)), "linhas_escolhas": int(len(esc)),
        "linhas_casadas": int(len(ambos)), "so_g2": int((m["_merge"] == "left_only").sum()),
        "so_escolhas": int((m["_merge"] == "right_only").sum()),
        "pontuacao_igual": int(((ambos["pontuacao"] == ambos["pontuacao_e9"])
                                | (ambos["pontuacao"].isna() & ambos["pontuacao_e9"].isna())).sum()),
        "alvo_igual": int((ambos["alvo"].astype(int) == alocado_e9.astype(int)).sum()),
        "regra_alvo_no_e9": "classificado (ciclo 1) ou alocado (ciclos 2-3)",
    }


def conferir_vagas_v_celula(quadro: pd.DataFrame, ciclo: int) -> dict[str, Any]:
    """Vagas lidas aqui = vagas de `outcomes_V_celula.parquet` (só as colunas de vagas são lidas)."""
    v = pd.read_parquet(V_CELULA, columns=["ciclo", "co_cnes_7d", "cod_curso", "vagas_imediatas", "vagas_cr"])
    v = v[v["ciclo"] == ciclo]
    m = quadro.merge(v, on=CHAVE, how="outer", indicator=True, suffixes=("", "_v"))
    ambos = m[m["_merge"] == "both"]
    return {
        "celulas_g2": int(len(quadro)), "celulas_v": int(len(v)), "casadas": int(len(ambos)),
        "imediatas_iguais": int((ambos["vagas_imediatas"] == ambos["vagas_imediatas_v"]).sum()),
        "cr_iguais": int((ambos["vagas_cr"] == ambos["vagas_cr_v"]).sum()),
    }


def taxa(s: pd.Series) -> float:
    return float(s.mean()) if len(s) else float("nan")


def rodar_chamada(ch: dict[str, Any], res: pd.DataFrame, quadro: pd.DataFrame | None) -> dict[str, Any]:
    ids = sorted(res["id_candidato"].unique())
    eleg = res[res["elegivel"]].copy()
    publicado = res[res["alvo"]][["id_candidato", "celula", "tipo_vaga_publicada"]]
    cap_ef = capacidade_efetiva(quadro, publicado)
    # Ex ante só existe quando o quadro da chamada tem vagas imediatas (o da 2ª chamada do ciclo 2 só tem
    # cadastro reserva; o da 2ª chamada do ciclo 1 não está no repositório).
    cap_ea = (capacidade_ex_ante(quadro) if quadro is not None and quadro["vagas_imediatas"].sum() > 0 else None)
    ordem = ch["ordem_edital"]
    alt = RESERVA_PRIMEIRO if ordem == AC_PRIMEIRO else AC_PRIMEIRO

    especs: dict[str, dict] = {}

    def registrar(nome: str, sim: dict, desc: dict) -> None:
        conc = concordancia(res, sim, ids)
        especs[nome] = {**desc, "sim": sim, "conc": conc, "n": int(len(conc)), "concordantes": int(conc.sum()),
                        "taxa": taxa(conc)}

    registrar("P_efetiva_publicada", alocar(eleg, cap_ef, ordem),
              {"capacidade": "efetiva_ex_post", "desempate": "classificacao_publicada", "prioridade": "1a_opcao_primeiro",
               "ordem_cotas": ordem, "principal": True})
    registrar("S_efetiva_publicada_cotas_alternativa", alocar(eleg, cap_ef, alt),
              {"capacidade": "efetiva_ex_post", "desempate": "classificacao_publicada", "prioridade": "1a_opcao_primeiro",
               "ordem_cotas": alt, "principal": False})
    registrar("S_efetiva_publicada_so_nota", alocar(eleg, cap_ef, ordem, prioridade_1a_opcao=False),
              {"capacidade": "efetiva_ex_post", "desempate": "classificacao_publicada", "prioridade": "so_pontuacao",
               "ordem_cotas": ordem, "principal": False})
    registrar("S_efetiva_publicada_boston", boston(eleg, cap_ef, ordem),
              {"capacidade": "efetiva_ex_post", "desempate": "classificacao_publicada",
               "prioridade": "rodadas_boston_1a_depois_2a", "ordem_cotas": ordem, "principal": False})
    if quadro is not None:
        registrar("S_efetiva_acrescimo_tudo_ac", alocar(eleg, capacidade_efetiva(quadro, publicado, "tudo_ac"), ordem),
                  {"capacidade": "efetiva_ex_post_acrescimo_tudo_ac", "desempate": "classificacao_publicada",
                   "prioridade": "1a_opcao_primeiro", "ordem_cotas": ordem, "principal": False})
    if cap_ea is not None:
        registrar("A_ex_ante_publicada", alocar(eleg, cap_ea, ordem),
                  {"capacidade": "ex_ante_vagas_imediatas", "desempate": "classificacao_publicada",
                   "prioridade": "1a_opcao_primeiro", "ordem_cotas": ordem, "principal": False})
    # Sorteios: desempate do edital não observável substituído por ordem aleatória global (como a idade).
    rng = np.random.default_rng(SEMENTE + 100 * ch["ciclo"] + ch["chamada"])
    acertos = pd.Series(0, index=ids, dtype=int)
    taxas_ef, taxas_ea = [], []
    for _ in range(N_SORTEIOS):
        u = dict(zip(ids, rng.random(len(ids))))
        conc = concordancia(res, alocar(eleg, cap_ef, ordem, desempate="sorteio", sorteio=u), ids)
        acertos += conc.astype(int)
        taxas_ef.append(taxa(conc))
        if cap_ea is not None:
            taxas_ea.append(taxa(concordancia(res, alocar(eleg, cap_ea, ordem, desempate="sorteio", sorteio=u), ids)))
    sorteios = {
        "n_sorteios": N_SORTEIOS, "semente": int(SEMENTE + 100 * ch["ciclo"] + ch["chamada"]),
        "efetiva_ex_post": {"media": float(np.mean(taxas_ef)), "minimo": float(np.min(taxas_ef)),
                            "maximo": float(np.max(taxas_ef))},
        "ex_ante": ({"media": float(np.mean(taxas_ea)), "minimo": float(np.min(taxas_ea)),
                     "maximo": float(np.max(taxas_ea))} if taxas_ea else None),
    }
    # Boston em duas rodadas × aceitação adiada: iguais sem vagas reservadas; com elas, a vaga reservada pode
    # virar remanescente já na rodada das 1ª opções (Boston) ou esperar o cotista de 2ª opção (aceitação adiada).
    bos = especs["S_efetiva_publicada_boston"]["sim"]
    equiv_boston = int(sum(bos.get(p, (None, None))[0] != especs["P_efetiva_publicada"]["sim"].get(p, (None, None))[0]
                           for p in ids))
    sem_reserva = {c: (sum(v), 0, 0) for c, v in cap_ef.items()}
    eleg_ac = eleg.assign(tipo_inscricao="AC")
    bos0, da0 = boston(eleg_ac, sem_reserva, ordem), alocar(eleg_ac, sem_reserva, ordem)
    equiv_boston_sem_reserva = int(sum(bos0.get(p, (None, None))[0] != da0.get(p, (None, None))[0] for p in ids))

    tipos_p = tipificar(res, especs["P_efetiva_publicada"]["sim"], ids, quadro, considerar_5_7=False)
    tipos_a = (tipificar(res, especs["A_ex_ante_publicada"]["sim"], ids, quadro, considerar_5_7=True)
               if "A_ex_ante_publicada" in especs else {})

    # Concordância do tipo de vaga (AC × reserva) entre os alocados nas duas versões.
    sim_p = especs["P_efetiva_publicada"]["sim"]
    pub_t = res[res["alvo"]].groupby("id_candidato")["tipo_vaga_publicada"].first()
    mesmo = [p for p in pub_t.index if sim_p.get(p, (None, None))[0] is not None and pub_t[p] is not None
             and sim_p[p][0] == res[res["alvo"] & (res["id_candidato"] == p)]["celula"].iloc[0]]
    tipo_ok = sum((sim_p[p][1] in RESERVA) == (pub_t[p] in RESERVA) for p in mesmo)

    cortes, margens = cortes_e_margens(eleg, sim_p, cap_ef)
    cortes_ea = None
    if cap_ea is not None:
        cortes_ea, margens_ea = cortes_e_margens(eleg, especs["A_ex_ante_publicada"]["sim"], cap_ea)
    else:
        margens_ea = None
    return {"especs": especs, "sorteios": sorteios, "acertos_sorteio": acertos, "tipos_p": tipos_p,
            "tipos_a": tipos_a, "equiv_boston_divergencias": equiv_boston,
            "equiv_boston_sem_reserva": equiv_boston_sem_reserva,
            "tipo_vaga": {"alocados_mesma_celula_com_tipo_publicado": len(mesmo), "tipo_concorda": int(tipo_ok)},
            "cortes": cortes, "cortes_ea": cortes_ea, "margens": margens, "margens_ea": margens_ea,
            "cap_ef": cap_ef, "cap_ea": cap_ea}


def contagens_margem(mg: pd.DataFrame) -> dict[str, int]:
    """Contagens da margem da 1ª opção (só para planejamento de poder)."""
    d = mg[mg["margem_1a_opcao"].notna()]
    m, adm = d["margem_1a_opcao"], d["admitido_1a_opcao"] == 1
    return {"definida": int(len(d)), "igual_0_empate_no_corte": int((m == 0).sum()),
            "igual_0_admitidos": int(((m == 0) & adm).sum()), "igual_0_recusados": int(((m == 0) & ~adm).sum()),
            "abs_ate_1": int((m.abs() <= 1).sum()), "abs_ate_2": int((m.abs() <= 2).sum()),
            "positiva": int((m > 0).sum()), "negativa": int((m < 0).sum()),
            "negativa_admitidos_por_reserva": int(((m < 0) & adm).sum())}


def contagens_cortes(c: pd.DataFrame) -> dict[str, int]:
    return {
        "celulas": int(len(c)), "celulas_com_vaga": int((c["vagas_total"] > 0).sum()),
        "celulas_com_corte_ativo": int(((c["corte_ativo"] == 1) & (c["vagas_total"] > 0)).sum()),
        "com_corte_entre_1a_opcao": int((c["corte_opcao"] == 1).sum()),
        "com_corte_entre_2a_opcao": int((c["corte_opcao"] == 2).sum()),
        "com_empate_no_corte_decidido_por_desempate": int(((c["n_empatados_no_corte"] > c["n_admitidos_no_corte"])
                                                           & (c["n_admitidos_no_corte"] > 0)).sum()),
    }


def veredito_ciclo(r: dict) -> str:
    ea = r.get("A_ex_ante_publicada")
    if ea is not None and ea >= META:
        return "VIAVEL"
    if r["P_efetiva_publicada"] >= META:
        return "VIAVEL_PARCIAL"
    return "INVIAVEL"


def main() -> int:
    mapa_ch1: dict[int, dict[str, str]] = {}
    resumo_ch: dict[str, Any] = {}
    linhas_aloc, linhas_cortes = [], []
    entradas = []
    for ch in CHAMADAS:
        res, quadro, diag = preparar(ch, mapa_ch1)
        r = rodar_chamada(ch, res, quadro)
        conf = conferir_com_escolhas(res, ch["ciclo"]) if ch["chamada"] == 1 else None
        conf_v = conferir_vagas_v_celula(quadro, ch["ciclo"]) if ch["chamada"] == 1 else None
        for caminho, papel in ((ch["arquivo"], "resultado publicado (candidato × opção)"),
                               (ch["quadro"], "quadro de vagas da chamada")):
            if caminho is not None:
                entradas.append({"chamada": ch["id"], "papel": papel, "caminho": f12.rel(caminho),
                                 "sha256": f12.sha256_arquivo(caminho)})
        esp = r["especs"]
        ids = sorted(res["id_candidato"].unique())
        pub_cel = res[res["alvo"]].groupby("id_candidato")["celula"].first()
        pub_tipo = res[res["alvo"]].groupby("id_candidato")["tipo_vaga_publicada"].first()
        op = res.sort_values("opcao_rank").groupby("id_candidato")
        primeira = res[res["opcao_rank"] == 1].groupby("id_candidato")["celula"].first()
        segunda = res[res["opcao_rank"] == 2].groupby("id_candidato")["celula"].first()
        pont = op["pontuacao"].first()
        n_op = op.size()
        eleg = res.groupby("id_candidato")["elegivel"].any()
        reserva = res.groupby("id_candidato")["tipo_inscricao"].first().isin(RESERVA)
        sj = res.groupby("id_candidato")["sub_judice"].any()
        marg = r["margens"].set_index("id_candidato")
        marg_ea = r["margens_ea"].set_index("id_candidato") if r["margens_ea"] is not None else None
        sim_p = esp["P_efetiva_publicada"]["sim"]
        sim_a = esp["A_ex_ante_publicada"]["sim"] if "A_ex_ante_publicada" in esp else None
        for p in ids:
            c1, c2 = primeira.get(p), segunda.get(p)
            cp, cs = pub_cel.get(p), sim_p.get(p, (None, None))
            tp = pub_tipo.get(p)
            motivos = []
            linha = {
                "ciclo": ch["ciclo"], "chamada": ch["chamada"], "id_candidato": p,
                "n_opcoes": int(n_op[p]),
                "co_cnes_7d_1a_opcao": c1[0] if c1 else None, "cod_curso_1a_opcao": float(c1[1]) if c1 else np.nan,
                "co_cnes_7d_2a_opcao": c2[0] if c2 else None, "cod_curso_2a_opcao": float(c2[1]) if c2 else np.nan,
                "pontuacao": float(pont[p]), "elegivel": int(eleg[p]), "inscricao_em_reserva": int(reserva[p]),
                "sub_judice": int(sj[p]),
                "alocado_publicado": int(cp is not None),
                "co_cnes_7d_publicado": cp[0] if cp else None, "cod_curso_publicado": float(cp[1]) if cp else np.nan,
                "vaga_publicada_reserva": (float(tp in RESERVA) if tp is not None else np.nan),
                "opcao_publicada": np.nan,
                "alocado_reconstruido": int(cs[0] is not None),
                "co_cnes_7d_reconstruido": cs[0][0] if cs[0] else None,
                "cod_curso_reconstruido": float(cs[0][1]) if cs[0] else np.nan,
                "vaga_reconstruida_reserva": (float(cs[1] in RESERVA) if cs[0] else np.nan),
                "concorda_principal": int(esp["P_efetiva_publicada"]["conc"][p]),
                "tipo_divergencia_principal": r["tipos_p"].get(p, ""),
                "concorda_ex_ante": (int(esp["A_ex_ante_publicada"]["conc"][p]) if sim_a is not None else np.nan),
                "tipo_divergencia_ex_ante": (r["tipos_a"].get(p, "") if sim_a is not None else None),
                "concorda_so_nota": int(esp["S_efetiva_publicada_so_nota"]["conc"][p]),
                "concorda_cotas_ordem_alternativa": int(esp["S_efetiva_publicada_cotas_alternativa"]["conc"][p]),
                "taxa_concordancia_sorteios": float(r["acertos_sorteio"][p] / N_SORTEIOS),
                "margem_1a_opcao": float(marg["margem_1a_opcao"].get(p, np.nan)) if p in marg.index else np.nan,
                "margem_1a_opcao_ex_ante": (float(marg_ea["margem_1a_opcao"].get(p, np.nan))
                                            if marg_ea is not None and p in marg_ea.index else np.nan),
            }
            if cp is not None:
                linha["opcao_publicada"] = float(1 if cp == c1 else 2 if cp == c2 else np.nan)
            if cp is None:
                motivos.append("co_cnes_7d_publicado,cod_curso_publicado,vaga_publicada_reserva,opcao_publicada: "
                               "não alocado na publicação")
            elif tp is None:
                motivos.append("vaga_publicada_reserva: arquivo publicado não informa o tipo de vaga")
            if cs[0] is None:
                motivos.append("co_cnes_7d_reconstruido,cod_curso_reconstruido,vaga_reconstruida_reserva: "
                               "não alocado na reconstrução")
            if c2 is None:
                motivos.append("co_cnes_7d_2a_opcao,cod_curso_2a_opcao: candidato com uma só opção")
            if not eleg[p]:
                motivos.append("pontuacao: sem pontuação numérica (SEM PRÉ-REQUISITO), fora do processamento")
            if np.isnan(linha["margem_1a_opcao"]):
                motivos.append("margem_1a_opcao: " + (marg["motivo_margem"].get(p, "") if p in marg.index
                                                      else "candidato inelegível ou sem 1a opção"))
            if sim_a is None:
                motivos.append("concorda_ex_ante,tipo_divergencia_ex_ante,margem_1a_opcao_ex_ante: "
                               "sem vagas imediatas de quadro da chamada (2ª chamada: quadro ausente do repositório ou só com cadastro reserva)")
            elif np.isnan(linha["margem_1a_opcao_ex_ante"]):
                motivos.append("margem_1a_opcao_ex_ante: " + (marg_ea["motivo_margem"].get(p, "")
                                                              if p in marg_ea.index
                                                              else "candidato inelegível ou sem 1a opção"))
            linha["motivos_ausencia"] = "; ".join(motivos)
            linhas_aloc.append(linha)
        cortes = r["cortes"].copy()
        if r["cortes_ea"] is not None:
            ea = r["cortes_ea"][CHAVE + ["vagas_total", "corte_ativo", "corte_opcao", "corte_pontuacao",
                                         "motivo_corte"]].rename(
                columns={"vagas_total": "vagas_total_ex_ante", "corte_ativo": "corte_ativo_ex_ante",
                         "corte_opcao": "corte_opcao_ex_ante", "corte_pontuacao": "corte_pontuacao_ex_ante",
                         "motivo_corte": "motivo_corte_ex_ante"})
            cortes = cortes.merge(ea, on=CHAVE, how="left", validate="one_to_one")
        else:
            for col in ("vagas_total_ex_ante", "corte_ativo_ex_ante", "corte_opcao_ex_ante", "corte_pontuacao_ex_ante"):
                cortes[col] = np.nan
            cortes["motivo_corte_ex_ante"] = ("sem vagas imediatas de quadro da chamada (quadro ausente do "
                                              "repositório ou só com cadastro reserva)")
        n_pub_cel = res[res["alvo"]].groupby("celula").size()
        cortes["n_alocados_publicado"] = [int(n_pub_cel.get((a, b), 0)) for a, b in zip(cortes["co_cnes_7d"],
                                                                                      cortes["cod_curso"])]
        if quadro is not None:
            q = quadro.set_index(CHAVE)
            cortes["vagas_imediatas_quadro"] = [q["vagas_imediatas"].get((a, b), np.nan)
                                                for a, b in zip(cortes["co_cnes_7d"], cortes["cod_curso"])]
            cortes["vagas_cr_quadro"] = [q["vagas_cr"].get((a, b), np.nan)
                                         for a, b in zip(cortes["co_cnes_7d"], cortes["cod_curso"])]
        else:
            cortes["vagas_imediatas_quadro"] = np.nan
            cortes["vagas_cr_quadro"] = np.nan
            cortes["motivo_corte_ex_ante"] = ("sem quadro de vagas da chamada no repositório; vagas_imediatas_quadro "
                                              "e vagas_cr_quadro também ausentes")
        cortes.insert(0, "chamada", ch["chamada"])
        cortes.insert(0, "ciclo", ch["ciclo"])
        linhas_cortes.append(cortes)

        tabela_esp = {k: {kk: vv for kk, vv in v.items() if kk not in ("sim", "conc")} for k, v in esp.items()}
        tp_cont = pd.Series(r["tipos_p"], dtype=object).value_counts().to_dict()
        ta_cont = pd.Series(r["tipos_a"], dtype=object).value_counts().to_dict()
        resumo_ch[ch["id"]] = {
            "ciclo": ch["ciclo"], "chamada": ch["chamada"], "chamada_principal_do_portao": ch["principal"],
            "arquivo_resultado": f12.rel(ch["arquivo"]),
            "arquivo_quadro": f12.rel(ch["quadro"]) if ch["quadro"] is not None else None,
            "regra_do_alvo": ch["alvo"], "ordem_das_cotas": ch["ordem_edital"],
            "ordem_das_cotas_documentada_no_repositorio": ch["ordem_documentada"], "fonte_da_ordem": ch["fonte_ordem"],
            "diagnostico_entrada": diag,
            "conferencia_com_escolhas_candidatos": conf,
            "conferencia_vagas_com_V_celula": conf_v,
            "especificacoes": tabela_esp,
            "sorteios_desempate": r["sorteios"],
            "divergencias_boston_vs_aceitacao_adiada": r["equiv_boston_divergencias"],
            "divergencias_boston_vs_aceitacao_adiada_sem_vagas_reservadas": r["equiv_boston_sem_reserva"],
            "tipo_de_vaga_reserva_vs_geral": r["tipo_vaga"],
            "intervalo_variantes_capacidade_efetiva_desempate_publicado": {
                "variantes": [n for n in tabela_esp if tabela_esp[n]["capacidade"].startswith("efetiva")
                              and tabela_esp[n]["prioridade"] != "so_pontuacao"],
                "minimo": float(min(x["taxa"] for x in tabela_esp.values() if x["capacidade"].startswith("efetiva")
                                    and x["prioridade"] != "so_pontuacao")),
                "maximo": float(max(x["taxa"] for x in tabela_esp.values() if x["capacidade"].startswith("efetiva")
                                    and x["prioridade"] != "so_pontuacao")),
            },
            "divergencias_principal_por_tipo": {str(k): int(v) for k, v in tp_cont.items()},
            "divergencias_ex_ante_por_tipo": {str(k): int(v) for k, v in ta_cont.items()},
            "celulas_alocacao_publicada_acima_das_imediatas": (
                int(sum(1 for c, n in res[res["alvo"]].groupby("celula").size().items()
                        if n > sum(capacidade_ex_ante(quadro).get(c, (0, 0, 0))))) if quadro is not None else None),
            "vagas_acrescidas_na_capacidade_efetiva": (
                int(sum(sum(v) for v in r["cap_ef"].values()) - quadro["vagas_imediatas"].sum())
                if quadro is not None else None),
            "cortes_principal": contagens_cortes(r["cortes"]),
            "cortes_ex_ante": contagens_cortes(r["cortes_ea"]) if r["cortes_ea"] is not None else None,
            "margem_1a_opcao_principal": contagens_margem(r["margens"]),
            "margem_1a_opcao_ex_ante": (contagens_margem(r["margens_ea"])
                                        if r["margens_ea"] is not None else None),
        }
        if ch["id"] == "c1_ch1":
            # Alvo alternativo: só os locais confirmados (os 59 desconsiderados pela gestão viram divergência).
            conf_alvo = res[res["confirmado"]].groupby("id_candidato")["celula"].first().to_dict()
            sim = esp["P_efetiva_publicada"]["sim"]
            ok = [sim.get(p, (None, None))[0] == conf_alvo.get(p) for p in ids]
            resumo_ch[ch["id"]]["alvo_alternativo_confirmados"] = {
                "descricao": "alvo = ALOCAÇÃO 'LOCAL DE ATUAÇÃO CONFIRMADO' (468); mesma reconstrução principal",
                "n": len(ok), "concordantes": int(sum(ok)), "taxa": float(np.mean(ok)),
                "divergencias_locais_desconsiderados_pela_gestao": int(res.loc[res["desconsiderado"], "id_candidato"].nunique()),
            }
        if ch["id"] == "c3_ch1":
            sim = esp["P_efetiva_publicada"]["sim"]
            alvo_sj = res[res["alvo"] | res["sub_judice"]].groupby("id_candidato")["celula"].first().to_dict()
            ok = [sim.get(p, (None, None))[0] == alvo_sj.get(p) for p in ids]
            resumo_ch[ch["id"]]["alvo_alternativo_com_sub_judice"] = {
                "descricao": "alvo = ALOCADO ou SUB JUDICE; mesma reconstrução principal",
                "n": len(ok), "concordantes": int(sum(ok)), "taxa": float(np.mean(ok)),
            }

    aloc = pd.DataFrame(linhas_aloc)
    aloc["natureza_dos_dados"] = NATUREZA
    aloc = aloc.sort_values(["ciclo", "chamada", "id_candidato"]).reset_index(drop=True)
    cortes = pd.concat(linhas_cortes, ignore_index=True)
    cortes["natureza_dos_dados"] = NATUREZA
    cortes = cortes.sort_values(["ciclo", "chamada"] + CHAVE).reset_index(drop=True)

    taxas = {k: {e: v["especificacoes"][e]["taxa"] for e in v["especificacoes"]} for k, v in resumo_ch.items()}
    vered_ciclo = {k: veredito_ciclo(taxas[k]) for k in resumo_ch if resumo_ch[k]["chamada_principal_do_portao"]}
    if all(v == "VIAVEL" for v in vered_ciclo.values()):
        veredito = "VIAVEL"
    elif all(v in ("VIAVEL", "VIAVEL_PARCIAL") for v in vered_ciclo.values()):
        veredito = "VIAVEL_PARCIAL"
    else:
        veredito = "INVIAVEL"
    sorteio_min = {k: resumo_ch[k]["sorteios_desempate"]["efetiva_ex_post"]["media"] for k in vered_ciclo}
    robusto = {k: bool(resumo_ch[k]["intervalo_variantes_capacidade_efetiva_desempate_publicado"]["minimo"] >= META)
               for k in vered_ciclo}
    resumo = {
        "natureza_dos_dados": NATUREZA,
        "portao": "G2 (doc 51, T6.0): replicação do mecanismo de alocação",
        "data_execucao": DATA_EXECUCAO,
        "script": "scripts/rdd_bolsa/G2_mecanismo_alocacao.py",
        "meta_concordancia": META,
        "mecanismo": MECANISMO,
        "regra_do_veredito": (
            "Por ciclo, na 1ª chamada: VIAVEL se a especificação ex ante (vagas imediatas do quadro, classificação "
            "publicada como desempate, ordem das cotas do edital) concorda em ≥ 99% dos candidatos; VIAVEL_PARCIAL "
            "se só a especificação com capacidade efetiva ex post concorda em ≥ 99%; INVIAVEL caso contrário. "
            "Global: VIAVEL se todos os ciclos são VIAVEL; VIAVEL_PARCIAL se todos são ao menos VIAVEL_PARCIAL; "
            "INVIAVEL caso contrário."),
        "veredito_por_ciclo": vered_ciclo,
        "veredito": veredito,
        "veredito_robusto_as_variantes_do_mecanismo": robusto,
        "ressalvas_do_veredito": [
            "≥ 99% só é atingido com a classificação publicada da célula como desempate; o desempate do edital "
            "(mesma UF de residência ou nascimento; idade) não é observável. Com sorteio no lugar dele, a "
            "concordância média na capacidade efetiva é " + ", ".join(f"{k}: {v:.4f}" for k, v in sorteio_min.items())
            + ".",
            "Nos ciclos 1 e 3 a publicação da 1ª chamada já incorpora a redistribuição do item 5.7 para células de "
            "cadastro reserva, feita por priorização da SGTES não publicada; a capacidade efetiva é observada ex post.",
            "A prioridade da 1ª opção sobre a 2ª não está escrita nos editais; é revelada pela classificação publicada "
            "e pela concordância (a especificação só por nota concorda menos).",
            "Ciclo 2: o texto do edital (Edital nº 3/2026) não está no repositório; a ordem das cotas é a do ciclo 3.",
            "A grade de especificações, a regra de tipagem das vagas acrescidas e a regra do veredito foram fixadas "
            "nesta execução depois de rodadas exploratórias sobre os mesmos arquivos; não há outcome envolvido, mas "
            "as taxas não são pré-registradas.",
        ],
        "chamadas": resumo_ch,
        "editais": {k: {"caminho": f12.rel(v), "sha256": f12.sha256_arquivo(v)} for k, v in EDITAIS.items()},
        "trechos_edital_conferidos": {k: [{"item": i, "trecho": t} for i, t in v] for k, v in TRECHOS_EDITAL.items()},
        "entradas": entradas + [
            {"chamada": "todas", "papel": "conferência de pseudônimos, células, opções e notas",
             "caminho": f12.rel(ESCOLHAS), "sha256": f12.sha256_arquivo(ESCOLHAS)},
            {"chamada": "1as chamadas", "papel": "conferência das vagas (só colunas de vagas)",
             "caminho": f12.rel(V_CELULA), "sha256": f12.sha256_arquivo(V_CELULA)},
        ],
        "nao_lido": ["arquivo local de IVS da auditoria 16", "IVS (qualquer fonte)", "faixa da bolsa", "CNES",
                     "SIA/SIH/TISS", "qualquer outcome"],
        "saidas": {
            "alocacao": {"caminho": f12.rel(OUT_ALOC), "linhas": int(len(aloc)),
                         "chave": ["ciclo", "chamada", "id_candidato"]},
            "cortes": {"caminho": f12.rel(OUT_CORTES), "linhas": int(len(cortes)),
                       "chave": ["ciclo", "chamada"] + CHAVE},
        },
        "parametros": {"n_sorteios": N_SORTEIOS, "semente_base": SEMENTE},
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    aloc.to_parquet(OUT_ALOC, index=False)
    cortes.to_csv(OUT_CORTES, index=False, float_format="%.6g")
    OUT_RESUMO.write_text(json.dumps(resumo, ensure_ascii=False, indent=2, default=_json) + "\n", encoding="utf-8")
    OUT_DOC.write_text(gerar_doc(resumo), encoding="utf-8")
    for k, v in resumo_ch.items():
        e = v["especificacoes"]
        print(k, {n: round(x["taxa"], 4) for n, x in e.items()}, "sorteio", v["sorteios_desempate"]["efetiva_ex_post"])
    print("veredito", veredito, vered_ciclo)
    return 0


def _json(o: Any) -> Any:
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, tuple):
        return list(o)
    raise TypeError(type(o))


# --------------------------------------------------------------------------
# Relatório (todo número vem do resumo)
# --------------------------------------------------------------------------

def _pct(x: float | None) -> str:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "—"
    return f"{100 * x:.2f}%".replace(".", ",")


def _n(x: Any) -> str:
    if x is None:
        return "—"
    return f"{int(x):,}".replace(",", ".")


ROTULO_CHAMADA = {"c1_ch1": "Ciclo 1, 1ª chamada", "c2_ch1": "Ciclo 2, 1ª chamada", "c3_ch1": "Ciclo 3, 1ª chamada",
                  "c1_ch2": "Ciclo 1, 2ª chamada", "c2_ch2": "Ciclo 2, 2ª chamada"}
ROTULO_TIPO = {
    "publicacao_alocado_em_duas_celulas": "publicação aloca o mesmo candidato em duas células",
    "sub_judice": "*sub judice* (fora do alvo, alocado pela reconstrução)",
    "redistribuicao_cadastro_reserva_item_5_7": "redistribuição para cadastro reserva (item 5.7)",
    "acao_afirmativa": "vagas reservadas (ER/PCD)",
    "efeito_em_cadeia": "efeito em cadeia de outra divergência na mesma célula",
    "nao_explicada": "não explicada",
}


def gerar_doc(r: dict[str, Any]) -> str:
    ch = r["chamadas"]
    L: list[str] = []
    L += [
        "# G2. Viabilidade do desenho do mecanismo de alocação (P6)",
        "",
        f"> **Data:** {DATA_EXECUCAO[8:10]}/{DATA_EXECUCAO[5:7]}/{DATA_EXECUCAO[:4]}.<br>",
        "> **Pedido:** portão G2 do doc 51 (T6.0): reconstruir a alocação publicada a partir das escolhas, notas,",
        "> elegibilidade e vagas, com meta de ≥ 99% de concordância por ciclo e chamada.<br>",
        "> **Estatuto:** portão de viabilidade. Não calcula contraste de outcome: nada de CNES, produção, IVS ou faixa",
        "> da bolsa foi lido. Cortes e margens são variáveis do mecanismo.<br>",
        "> **Gerado por:** `scripts/rdd_bolsa/G2_mecanismo_alocacao.py`. Todo número deste documento vem de",
        "> `output/rdd_bolsa/G2_resumo.json` e é conferido por `tests/test_G2.py`.",
        "",
        f"**Veredito: `{r['veredito']}`** (por ciclo: "
        + ", ".join(f"ciclo {k[1]} `{v}`" for k, v in r["veredito_por_ciclo"].items()) + ").",
        "",
        "Robustez: com capacidade efetiva e desempate publicado, a concordância fica entre "
        + "; ".join(f"ciclo {k[1]} {_pct(ch[k]['intervalo_variantes_capacidade_efetiva_desempate_publicado']['minimo'])}–"
                    f"{_pct(ch[k]['intervalo_variantes_capacidade_efetiva_desempate_publicado']['maximo'])}"
                    for k in r["veredito_por_ciclo"])
        + " nas variantes do mecanismo (aceitação adiada ou Boston, ordem das cotas, tipagem das vagas acrescidas).",
        "",
        "Nota de processo: a grade de especificações, a regra de tipagem das vagas acrescidas e a regra do veredito",
        "foram fixadas nesta execução depois de rodadas exploratórias sobre os mesmos arquivos. Não há outcome no",
        "portão, mas as taxas de concordância não são pré-registradas.",
        "",
        "## 1. O mecanismo dos editais",
        "",
        "Trechos conferidos nos editais do repositório (ciclo 1: Edital SGTES/MS nº 3/2025; ciclo 3: Edital nº",
        "28/2026; o texto do edital do ciclo 2 não está no repositório, só a página de anexos):",
        "",
        "| Item | O que diz |",
        "|---|---|",
        "| 4.1.3 | até 2 locais de atuação, em ordem de preferência; no ciclo 3, a 2ª no mesmo aprimoramento da 1ª |",
        "| 4.1.3.4 | célula de cadastro reserva não tem vaga imediata; pode recebê-la por remanejamento |",
        "| 4.1.7 (c1) / 4.1.6 (c3) | alocação no estabelecimento indicado, observadas a ordem de classificação e as vagas |",
        "| 5.2 | classificação pela pontuação do barema (inteira, 0 a 15) |",
        "| 5.2.5 | desempate: mesma UF da residência (c1: ou do nascimento; c3: depois nascimento) e maior idade |",
        "| 5.4–5.5 | cotista concorre também na ampla concorrência; vaga reservada vazia vai à ampla (remanescente de cota) |",
        "| 5.6 | ordem: c1 = ações afirmativas, ampla, remanescentes; c3 = ampla, ações afirmativas, remanescentes |",
        "| 5.7 | vaga imediata não preenchida pode ser redistribuída a célula de cadastro reserva com lista de espera, por priorização da SGTES (regiões com mais dificuldade de acesso e escassez) |",
        "",
        "Mecanismo implementado: " + r["mecanismo"],
        "",
        "O que o edital não escreve e os dados revelam: a classificação publicada de cada célula põe quem escolheu a",
        "célula como 1ª opção antes de quem a escolheu como 2ª, e só depois ordena por nota. A especificação \"só",
        "nota\" abaixo testa a alternativa (ditadura serial pela nota) e concorda menos.",
        "",
        "## 2. Concordância com a alocação publicada",
        "",
        "Concordância = proporção de candidatos cuja célula reconstruída (ou nenhuma) é igual à publicada.",
        "",
        "| Chamada | Candidatos | Principal: capacidade efetiva, desempate publicado | Ex ante: vagas imediatas do quadro | Boston em duas rodadas | Só nota | Cotas na ordem alternativa | Vagas acrescidas todas AC | Sorteio no desempate (média; mín.–máx.) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]

    def _t(e: dict, nome: str, ausente: str) -> str:
        return _pct(e[nome]["taxa"]) if nome in e else ausente

    for k, v in ch.items():
        e = v["especificacoes"]
        s = v["sorteios_desempate"]["efetiva_ex_post"]
        L.append(
            f"| {ROTULO_CHAMADA[k]} | {_n(e['P_efetiva_publicada']['n'])} | {_pct(e['P_efetiva_publicada']['taxa'])} "
            f"({_n(e['P_efetiva_publicada']['concordantes'])}) | "
            f"{_t(e, 'A_ex_ante_publicada', '— (quadro ausente)' if v['arquivo_quadro'] is None else '— (quadro só com cadastro reserva)')} | "
            f"{_t(e, 'S_efetiva_publicada_boston', '—')} | "
            f"{_t(e, 'S_efetiva_publicada_so_nota', '—')} | "
            f"{_t(e, 'S_efetiva_publicada_cotas_alternativa', '—')} | "
            f"{_t(e, 'S_efetiva_acrescimo_tudo_ac', '— (sem quadro)')} | "
            f"{_pct(s['media'])}; {_pct(s['minimo'])}–{_pct(s['maximo'])} |")
    L += [
        "",
        "Como ler: a coluna principal usa a capacidade efetiva de cada célula (as vagas imediatas do quadro,",
        "acrescidas do que a publicação alocou acima delas) e a classificação publicada da célula como desempate. As",
        "vagas acrescidas seguem a divisão AC/ER/PCD do cadastro reserva do quadro; a coluna \"vagas acrescidas todas",
        "AC\" é a alternativa. Essa regra de tipagem foi escolhida depois de ver as divergências da 2ª chamada do ciclo",
        "2, onde cotistas ocupam vagas de cadastro reserva; por isso a alternativa é relatada ao lado. A coluna ex ante",
        "usa só as vagas imediatas do quadro, sem a redistribuição do item 5.7. \"Boston em duas rodadas\" processa",
        "todas as 1ª opções antes das 2ª opções. A última coluna troca o desempate do edital, que não é observável, por",
        "um sorteio (" + _n(r["parametros"]["n_sorteios"]) + " sorteios).",
        "",
        "Conferências de entrada (1ª chamada): as linhas lidas aqui são as de `escolhas_candidatos.parquet`",
        "(mesmo pseudônimo, célula, opção e nota) e as vagas são as de `outcomes_V_celula.parquet`:",
        "",
        "| Chamada | Linhas casadas / lidas | Nota igual | Alvo igual ao E9 | Células com vagas iguais |",
        "|---|---:|---:|---:|---:|",
    ]
    for k, v in ch.items():
        c, cv = v["conferencia_com_escolhas_candidatos"], v["conferencia_vagas_com_V_celula"]
        if c is None:
            continue
        L.append(f"| {ROTULO_CHAMADA[k]} | {_n(c['linhas_casadas'])} / {_n(c['linhas_g2'])} | {_n(c['pontuacao_igual'])} | "
                 f"{_n(c['alvo_igual'])} | {_n(cv['imediatas_iguais'])} / {_n(cv['celulas_g2'])} |")
    L += ["", "## 3. Divergências", "",
          "Tipos, na ordem de atribuição: *sub judice*; redistribuição do item 5.7 (só na especificação ex ante);",
          "vagas reservadas; efeito em cadeia de outra divergência na mesma célula; não explicada.", "",
          "| Chamada | Especificação | Tipo | Candidatos |", "|---|---|---|---:|"]
    for k, v in ch.items():
        for nome, d in (("principal", v["divergencias_principal_por_tipo"]), ("ex ante", v["divergencias_ex_ante_por_tipo"])):
            for t, n in sorted(d.items(), key=lambda x: -x[1]):
                L.append(f"| {ROTULO_CHAMADA[k]} | {nome} | {ROTULO_TIPO.get(t, t)} | {_n(n)} |")
    c1 = ch["c1_ch1"]
    c3 = ch["c3_ch1"]
    L += [
        "",
        "Outras fontes de diferença, fora da comparação principal:",
        "",
        f"- Ciclo 1: o alvo é o resultado do processamento ({_n(c1['diagnostico_entrada']['candidatos_no_alvo'])} "
        f"classificados). Destes, {_n(c1['diagnostico_entrada']['no_alvo_desconsiderados_pela_gestao'])} tiveram o "
        "local depois desconsiderado a pedido da gestão (Quadro 2, realocação). Contra só os confirmados, a mesma "
        f"reconstrução concorda em {_pct(c1['alvo_alternativo_confirmados']['taxa'])}.",
        f"- Ciclo 1: {_n(c1['diagnostico_entrada']['candidatos_inelegiveis_sem_pontuacao'])} candidatos com \"SEM "
        "PRÉ-REQUISITO\" ficam fora do processamento (não classificados na publicação e na reconstrução).",
        f"- Ciclo 3: {_n(c3['diagnostico_entrada']['sub_judice'])} linhas *sub judice*. Contando-as como alocadas, a "
        f"concordância é {_pct(c3['alvo_alternativo_com_sub_judice']['taxa'])}.",
        f"- Ciclo 2, 2ª chamada: a publicação aloca {_n(ch['c2_ch2']['diagnostico_entrada']['candidatos_com_mais_de_uma_alocacao_publicada'])} "
        "candidato em duas células; a comparação usa a primeira linha publicada. O arquivo da 2ª chamada do ciclo 1 é",
        "  a alocação preliminar (título da planilha), não a final.",
        "- Ciclo 2: as vagas remanescentes (resultados de 05/05/2026 e o anterior) e a 2ª chamada são etapas",
        "  posteriores à 1ª chamada; só a 2ª chamada é reconstruída aqui, com o próprio quadro e o próprio resultado.",
        "- Ciclos 1 e 3: a publicação da 1ª chamada já inclui a redistribuição do item 5.7 (células acima das",
        f"  imediatas: ciclo 1 = {_n(c1['celulas_alocacao_publicada_acima_das_imediatas'])}, ciclo 3 = "
        f"{_n(c3['celulas_alocacao_publicada_acima_das_imediatas'])}; vagas acrescidas na capacidade efetiva: "
        f"{_n(c1['vagas_acrescidas_na_capacidade_efetiva'])} e {_n(c3['vagas_acrescidas_na_capacidade_efetiva'])}). "
        "A priorização da SGTES que decide para onde vão essas vagas não é publicada; por isso a especificação",
        "  ex ante não as reproduz.",
        "- Aceitação adiada com prioridade da 1ª opção × Boston em duas rodadas: sem vagas reservadas, as duas dão o",
        "  mesmo resultado em todas as chamadas (candidatos com resultado diferente: "
        + ", ".join(f"{ROTULO_CHAMADA[k]} {_n(v['divergencias_boston_vs_aceitacao_adiada_sem_vagas_reservadas'])}"
                    for k, v in ch.items())
        + "). Com as vagas reservadas, diferem em "
        + ", ".join(f"{ROTULO_CHAMADA[k]} {_n(v['divergencias_boston_vs_aceitacao_adiada'])}" for k, v in ch.items())
        + " candidatos: em Boston, a vaga reservada sem cotista de 1ª opção vira remanescente já na rodada das 1ª",
        "  opções; na aceitação adiada, ela espera o cotista de 2ª opção. A tabela 2 mostra qual reproduz melhor cada",
        "  chamada.",
        "",
        "## 4. Cortes por célula e margens (variáveis do mecanismo)",
        "",
        "Corte da célula: prioridade do último admitido em vaga de ampla concorrência — o par (ordem da opção,",
        "pontuação). Corte ativo: algum candidato que propôs à célula foi recusado. Margem da 1ª opção: pontuação",
        "menos a pontuação de corte da célula da 1ª opção, definida só quando o corte cai entre candidatos de 1ª",
        "opção. Margem 0 = empatado no corte, onde decide o desempate não observável. Contagens apenas, para",
        "planejamento de poder; nenhuma comparação de outcome.",
        "",
        "| Chamada | Células com vaga | Com corte ativo | Corte entre 1ª opções | Corte entre 2ª opções | Empate no corte decidido por desempate | Margem definida | Margem = 0 (admitidos / recusados) | \\|margem\\| ≤ 1 | \\|margem\\| ≤ 2 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for k, v in ch.items():
        c, m = v["cortes_principal"], v["margem_1a_opcao_principal"]
        L.append(f"| {ROTULO_CHAMADA[k]} | {_n(c['celulas_com_vaga'])} | {_n(c['celulas_com_corte_ativo'])} | "
                 f"{_n(c['com_corte_entre_1a_opcao'])} | {_n(c['com_corte_entre_2a_opcao'])} | "
                 f"{_n(c['com_empate_no_corte_decidido_por_desempate'])} | {_n(m['definida'])} | "
                 f"{_n(m['igual_0_empate_no_corte'])} ({_n(m['igual_0_admitidos'])} / {_n(m['igual_0_recusados'])}) | "
                 f"{_n(m['abs_ate_1'])} | {_n(m['abs_ate_2'])} |")
    L += [
        "",
        "Como ler: valores da especificação principal (capacidade efetiva). A mesma tabela na capacidade ex ante está",
        "em `G2_resumo.json` (`cortes_ex_ante`, `margem_1a_opcao_ex_ante`).",
        "",
        "## 5. O que isso implica para o P6",
        "",
        "1. A regra de alocação é replicável quando a classificação publicada da célula entra como desempate e a",
        "   capacidade efetiva é tomada da publicação. Sem a classificação publicada, a nota (inteira, 0–15) e a",
        "   ordem da opção não bastam: os empates no corte são decididos por UF de residência ou nascimento e idade,",
        "   que não são públicos.",
        "2. A variável de corte é discreta (pontuação inteira) e a vizinhança do corte é dominada por empates. Um",
        "   desenho de RD na nota terá poucos pontos de suporte; o contraste perto do corte compara candidatos",
        "   empatados separados por um desempate determinístico (idade, UF), não por sorteio.",
        "3. Nos ciclos 1 e 3, a capacidade de parte das células resulta de uma redistribuição discricionária (item",
        "   5.7) feita depois de ver as listas de espera; essas células precisam de tratamento separado no protocolo",
        "   56 (por exemplo, restringir o contraste às células cuja capacidade efetiva é igual às imediatas do",
        "   quadro).",
        "4. Ciclo 2: o texto do edital não está no repositório; a ordem das cotas foi assumida (a do ciclo 3) e a",
        "   ordem alternativa é relatada na tabela 2.",
        "",
        "## 6. Saídas",
        "",
        f"- `{r['saidas']['alocacao']['caminho']}`: uma linha por candidato × chamada "
        f"({_n(r['saidas']['alocacao']['linhas'])} linhas).",
        f"- `{r['saidas']['cortes']['caminho']}`: uma linha por célula × chamada "
        f"({_n(r['saidas']['cortes']['linhas'])} linhas).",
        "- `output/rdd_bolsa/G2_resumo.json`: concordâncias, divergências, contagens, entradas com SHA-256 e veredito.",
        "",
        "Nenhum nome ou CPF é gravado; o candidato é o pseudônimo `id_candidato` do script 12. A inscrição em ação",
        "afirmativa é gravada só como indicador (reserva sim/não). O arquivo local de IVS não é lido.",
        "",
    ]
    return "\n".join(L)


if __name__ == "__main__":
    sys.exit(main())
