"""a12_adquirir_sia_tabnet.py — SIA/SUS no TabNet: município × mês de processamento × subgrupo × conjunto de CBO.

Aquisição SIA do protocolo de produção especializada
(``docs/06_execucao/47_protocolo_producao_especializada.md``, §2–§4 e §6).
Só adquire, valida e documenta: não lê IVS, não calcula nada por faixa, lado
de corte, bolsa ou tratamento e não estima nada.

Fonte: TabNet do DATASUS, "Produção Ambulatorial do SUS - Brasil - por local de
atendimento" (``sia/cnv/qabr.def``), por HTTP (o HTTPS do TabNet falha neste
ambiente). O formulário (``deftohtm.exe``) é baixado primeiro; os valores das
opções (dimensões, arquivos mensais, índices das CBO e das UF) são lidos dele, e
não digitados. Cada consulta é um POST em ``tabcgi.exe`` (latin-1), formato
``prn`` (texto separado por ponto e vírgula), com ``zeradas=exibirlz``.

Consultas por mês de processamento (202201 a 202607; nenhum mês >= 202609):
- Linha = Município, Coluna = Subgrupo, Incremento = Qtd.aprovada, uma vez para
  cada conjunto de CBO do profissional executante (``alvo_pmme``,
  ``especialistas_nao_alvo``, ``generalistas``, ``mfc_225130``) e uma vez sem
  filtro de CBO (``todos_profissionais``);
- Linha = UF, sem filtro de CBO: validação do total nacional e por UF;
- Linha = Profissional - CBO, sem filtro: validação de cada conjunto contra a soma
  das suas CBO e completude do CBO (produção sem CBO na tabela do TabNet).
Mais uma conferência célula a célula de duas UF pequenas (RR e AC) num mês
fixado antes de ver os dados (202506), por consultas filtradas por UF.

Conjuntos de CBO: a regra é a do painel CNES nacional. A lista ``alvo_pmme`` vem
da ponte (``a09.carregar_ponte``) e os grupos saem da própria função
``a09.agregar_mes`` aplicada à lista de CBO do formulário, sem redigitar a regra.

Zeros e ausências: ``-`` no TabNet é zero não resultante de arredondamento
(legenda do próprio TabNet) e vira ``qtd_aprovada = 0`` com
``status = zero_tabnet``. Município da lista do formulário que não aparece na
resposta fica com ``qtd_aprovada`` nula e ``status = municipio_ausente_da_resposta``.
Consulta que falha não gera linhas: a consolidação para (fail closed). Subgrupo
que não é coluna da resposta não gera linhas; a presença de cada subgrupo em
cada consulta está em ``sia_subgrupos_por_consulta.csv``. "Município ignorado"
fica em arquivo próprio e nunca é atribuído a município.

Modos (``--etapa``): ``verificar`` (padrão, usado pelo ``run_all.py``) confere as
saídas versionadas contra o manifesto, sem rede e sem gravar; ``baixar`` só
grava respostas brutas no cache (fora do Git); ``consolidar`` lê o cache, valida e
só então grava as saídas; ``tudo`` faz as duas coisas.

Saídas (``output/aquisicao/sia/``):
- ``painel_sia_municipio_mes_subgrupo_cbo.parquet``;
- ``sia_municipio_ignorado_mes_subgrupo_cbo.parquet``;
- ``sia_uf_mes_subgrupo_todos.parquet``;
- ``sia_nacional_cbo_mes_subgrupo.parquet``;
- ``sia_subgrupos_por_consulta.csv``, ``sia_cobertura_mes.csv``,
  ``sia_conjuntos_cbo.csv``, ``sia_municipios_tabnet.csv``;
- ``manifesto_sia.json`` e ``a12_resumo.md``;
- ``brutos/`` (cache das respostas, gzip, ignorado pelo Git).
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import gzip
import hashlib
import html
import importlib.util
import io
import json
import re
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[2]

A09_FILE = Path(__file__).resolve().parent / "a09_adquirir_cnes_nacional.py"
_SPEC_A09 = importlib.util.spec_from_file_location("a09_adquirir_cnes_nacional", A09_FILE)
a09 = importlib.util.module_from_spec(_SPEC_A09)
_SPEC_A09.loader.exec_module(a09)

OUT_AQ = ROOT / "output" / "aquisicao"
OUT_DIR = OUT_AQ / "sia"
CACHE_DIR = OUT_DIR / "brutos"
PAINEL_FILE = OUT_DIR / "painel_sia_municipio_mes_subgrupo_cbo.parquet"
IGNORADOS_FILE = OUT_DIR / "sia_municipio_ignorado_mes_subgrupo_cbo.parquet"
UF_FILE = OUT_DIR / "sia_uf_mes_subgrupo_todos.parquet"
CBO_FILE = OUT_DIR / "sia_nacional_cbo_mes_subgrupo.parquet"
SUBGRUPOS_FILE = OUT_DIR / "sia_subgrupos_por_consulta.csv"
COBERTURA_FILE = OUT_DIR / "sia_cobertura_mes.csv"
CONJUNTOS_FILE = OUT_DIR / "sia_conjuntos_cbo.csv"
MUNICIPIOS_FILE = OUT_DIR / "sia_municipios_tabnet.csv"
MANIFESTO_FILE = OUT_DIR / "manifesto_sia.json"
RESUMO_FILE = OUT_DIR / "a12_resumo.md"
PONTE_FILE = a09.PONTE_FILE

URL_FORMULARIO = "http://tabnet.datasus.gov.br/cgi/deftohtm.exe?sia/cnv/qabr.def"
URL_CONSULTA = "http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sia/cnv/qabr.def"
CABECALHOS_HTTP = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/x-www-form-urlencoded"}

# Meses de processamento (protocolo 47, §2 e §6): SIA lido até 202607; nada do ciclo 3.
PRIMEIRA_COMPETENCIA = "202201"
ULTIMA_COMPETENCIA = "202607"
LIMITE_EXCLUSIVO = a09.LIMITE_EXCLUSIVO  # "202609"
COMPETENCIAS = [
    f"{ano}{mes:02d}" for ano in range(2022, 2027) for mes in range(1, 13)
    if PRIMEIRA_COMPETENCIA <= f"{ano}{mes:02d}" <= ULTIMA_COMPETENCIA
]
assert all(c < LIMITE_EXCLUSIVO for c in COMPETENCIAS)

CONJUNTOS_CBO = ("alvo_pmme", "especialistas_nao_alvo", "generalistas", a09.GRUPO_MFC)
TODOS = "todos_profissionais"
CONJUNTOS = CONJUNTOS_CBO + (TODOS,)
# Conjuntos disjuntos (regra do a09: mfc_225130 está contido em especialistas_nao_alvo).
CONJUNTOS_DISJUNTOS = ("alvo_pmme", "especialistas_nao_alvo", "generalistas")

# Conferência célula a célula fixada antes de ver os dados: duas UF pequenas, um mês do pré.
MES_CONFERENCIA_UF = "202506"
UFS_CONFERENCIA = {"RR": "Roraima", "AC": "Acre"}

# Nomes de dimensões e opções exigidos no formulário (conferidos contra o HTML baixado).
LINHA_MUNICIPIO = "Município"
LINHA_UF = "UF"
LINHA_CBO = "Profissional_-_CBO"
COLUNA = "Subgrupo_proced."
INCREMENTO = "Qtd.aprovada"
FILTRO_CBO = "SProfissional_-_CBO"
FILTRO_UF = "SUF"
FILTRO_MUNICIPIO = "SMunicípio"
ROTULO_LINHA = {LINHA_MUNICIPIO: "Município", LINHA_UF: "UF", LINHA_CBO: "Profissional - CBO"}
ROTULO_FILTRO_CBO = "Profissional - CBO"
ROTULO_FILTRO_UF = "UF"
MESES_PT = ("Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez")

TENTATIVAS = 5
PAUSA_ENTRE_CONSULTAS = 1.5  # segundos
TIMEOUT = 300
# Sinalização de cobertura (só relato, nada é corrigido), fixada antes de ver os dados.
LIMIAR_QUEDA_MUNICIPIOS = 0.90  # municípios com produção < 90% da mediana do conjunto
LIMIAR_QUEDA_TOTAL = 0.80       # total nacional < 80% da mediana do conjunto

STATUS_VALOR = "valor_tabnet"
STATUS_ZERO = "zero_tabnet"
STATUS_AUSENTE = "municipio_ausente_da_resposta"
STATUS_VALIDOS = (STATUS_VALOR, STATUS_ZERO, STATUS_AUSENTE)
NATUREZA = "EMPIRICO"

COLUNAS_PAINEL = ["co_ibge", "competencia_processamento", "subgrupo", "conjunto_cbo",
                  "qtd_aprovada", "status", "natureza_dos_dados"]
ESQUEMA_PAINEL = pa.schema([
    ("co_ibge", pa.dictionary(pa.int32(), pa.string())),
    ("competencia_processamento", pa.dictionary(pa.int8(), pa.string())),
    ("subgrupo", pa.dictionary(pa.int8(), pa.string())),
    ("conjunto_cbo", pa.dictionary(pa.int8(), pa.string())),
    ("qtd_aprovada", pa.int64()),
    ("status", pa.dictionary(pa.int8(), pa.string())),
    ("natureza_dos_dados", pa.dictionary(pa.int8(), pa.string())),
])

RE_MUNICIPIO = re.compile(r"^(\d{6}) (.+)$")
RE_IGNORADO_UF = re.compile(r"^MUNICIPIO IGNORADO - ([A-Z]{2})$")
RE_IGNORADO_EXTERIOR = re.compile(r"^000000 (.+)$")
RE_SUBGRUPO = re.compile(r"^(\d{4}) (.*)$")
RE_UF = re.compile(r"^(\d{2}) (.+)$")
RE_CBO = re.compile(r"^([0-9A-Z]{6}) (.+)$")


class ErroResposta(RuntimeError):
    """A resposta do TabNet não tem a forma esperada (fail closed)."""


def log(msg: str) -> None:
    print(f"[{dt.datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def _rel(p: Path) -> str:
    """Caminho relativo à raiz (POSIX) quando está no repositório; absoluto caso contrário."""
    try:
        return Path(p).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return Path(p).as_posix()


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_arquivo(path: Path) -> str:
    return a09.sha256_arquivo(path)


def checar_limite(comp: str) -> None:
    if comp >= LIMITE_EXCLUSIVO:
        raise RuntimeError(f"Competência {comp} >= {LIMITE_EXCLUSIVO} é vedada (ciclo 3).")
    if comp > ULTIMA_COMPETENCIA or comp < PRIMEIRA_COMPETENCIA:
        raise RuntimeError(f"Competência {comp} fora do plano do protocolo 47 ({PRIMEIRA_COMPETENCIA}–{ULTIMA_COMPETENCIA}).")


def arquivo_do_mes(comp: str) -> str:
    return f"qabr{comp[2:4]}{comp[4:6]}.dbf"


def rotulo_do_mes(comp: str) -> str:
    return f"{MESES_PT[int(comp[4:6]) - 1]}/{comp[:4]}"


# ---------------------------------------------------------------- formulário

def ler_formulario(txt: str) -> dict[str, Any]:
    """Opções de cada SELECT e as entradas do formulário (texto latin-1 já decodificado)."""
    selects: dict[str, list[tuple[str, str]]] = {}
    for m in re.finditer(r'<SELECT[^>]*NAME="([^"]+)"[^>]*>(.*?)</SELECT>', txt, re.S | re.I):
        opcoes = re.findall(r'<OPTION[^>]*VALUE="([^"]*)"[^>]*>([^<\r\n]*)', m.group(2), re.I)
        selects[m.group(1)] = [(v, html.unescape(t).strip()) for v, t in opcoes]
    acao = re.search(r'<FORM ACTION="([^"]+)"', txt, re.I)
    entradas = re.findall(r'<input[^>]*name="([^"]+)"[^>]*VALUE="?([^"\s>]+)', txt, re.I)
    return {"selects": selects, "acao": acao.group(1) if acao else None, "entradas": sorted(set(entradas))}


def _valores(form: dict[str, Any], nome: str) -> list[str]:
    return [v for v, _ in form["selects"].get(nome, [])]


def conferir_formulario(form: dict[str, Any]) -> None:
    """Fail closed se o formulário não oferecer o que o protocolo usa."""
    erros = []
    if form["acao"] != "/cgi/tabcgi.exe?sia/cnv/qabr.def":
        erros.append(f"ação do formulário inesperada: {form['acao']}")
    for nome, exigidos in (("Linha", [LINHA_MUNICIPIO, LINHA_UF, LINHA_CBO]), ("Coluna", [COLUNA]),
                           ("Incremento", [INCREMENTO]),
                           ("Arquivos", [arquivo_do_mes(c) for c in COMPETENCIAS])):
        faltam = [x for x in exigidos if x not in _valores(form, nome)]
        if faltam:
            erros.append(f"{nome} sem {faltam}")
    for nome in (FILTRO_CBO, FILTRO_UF, FILTRO_MUNICIPIO):
        if nome not in form["selects"]:
            erros.append(f"filtro {nome} ausente")
    for par in (("formato", "prn"), ("zeradas", "exibirlz"), ("mostre", "Mostra")):
        if par not in form["entradas"]:
            erros.append(f"entrada {par} ausente")
    rotulos = dict(form["selects"].get("Arquivos", []))
    for c in COMPETENCIAS:
        if rotulos.get(arquivo_do_mes(c)) != rotulo_do_mes(c):
            erros.append(f"rótulo do arquivo de {c}: {rotulos.get(arquivo_do_mes(c))!r}")
    if erros:
        raise ErroResposta("formulário: " + "; ".join(erros))


def opcoes_cbo(form: dict[str, Any]) -> list[dict[str, str]]:
    saida = []
    for v, t in form["selects"][FILTRO_CBO]:
        if v == "TODAS_AS_CATEGORIAS__":
            continue
        m = RE_CBO.match(t)
        if not m:
            raise ErroResposta(f"opção de CBO fora do padrão: {v} {t!r}")
        saida.append({"indice": v, "co_cbo": m.group(1), "rotulo": t})
    if len({o["co_cbo"] for o in saida}) != len(saida):
        raise ErroResposta("CBO repetida no formulário")
    return saida


def classificar_cbos(codigos: list[str], alvo: list[str]) -> dict[str, list[str]]:
    """Aplica a regra de grupos do a09 (``a09.agregar_mes``) a uma lista de CBO.

    Cada CBO vira uma linha num quadro de classificação (não é dado: horas e IDs
    são marcadores) com chave própria; o grupo em que a linha cai em
    ``agregar_mes`` é o conjunto da CBO. Assim a regra não é redigitada.
    """
    faltam = [c for c in alvo if c not in codigos]
    if faltam:
        raise ErroResposta(f"CBO-alvo ausentes do formulário do TabNet: {faltam}")
    n = len(codigos)
    quadro = pd.DataFrame({
        "co_municipio": pd.Series(codigos, dtype="string"),
        "co_profissional_sus": pd.Series(codigos, dtype="string"),
        "co_cbo": pd.Series(codigos, dtype="string"),
        "qt_ch_ambulatorial": pd.array([0] * n, dtype="Int32"),
        "qt_ch_hosp_sus": pd.array([0] * n, dtype="Int32"),
        "qt_ch_outros": pd.array([0] * n, dtype="Int32"),
        "tp_sus_nao_sus": pd.Series(["S"] * n, dtype="string"),
    })
    agg = a09.agregar_mes(quadro, alvo)
    return {g: sorted(agg.loc[agg["grupo"] == g, "co_municipio"].astype(str)) for g in CONJUNTOS_CBO}


def conjuntos_do_formulario(form: dict[str, Any]) -> dict[str, list[dict[str, str]]]:
    alvo, _, _ = a09.carregar_ponte()
    opcoes = opcoes_cbo(form)
    por_codigo = {o["co_cbo"]: o for o in opcoes}
    grupos = classificar_cbos(sorted(por_codigo), alvo)
    saida = {}
    for g in CONJUNTOS_CBO:
        if not grupos[g]:
            raise ErroResposta(f"conjunto {g} vazio")
        saida[g] = sorted((por_codigo[c] for c in grupos[g]), key=lambda o: int(o["indice"]))
    if [o["co_cbo"] for o in saida["alvo_pmme"]] != sorted(alvo, key=lambda c: int(por_codigo[c]["indice"])):
        raise ErroResposta("alvo_pmme do a09 não coincide com a ponte")
    return saida


def municipios_do_formulario(form: dict[str, Any]) -> tuple[list[dict[str, str]], dict[str, str]]:
    """Lista de municípios (6 dígitos) e mapa sigla da UF -> código, na ordem do formulário.

    A UF do município é o prefixo de 2 dígitos do código. A sigla vem da opção
    "MUNICIPIO IGNORADO - XX" que abre o bloco da UF (o DF não tem essa opção e
    fica sem sigla). Os blocos têm de ser contíguos.
    """
    municipios = []
    sigla_para_codigo: dict[str, str] = {}
    sigla_pendente = None
    uf_atual = None
    vistos_uf: set[str] = set()
    for v, t in form["selects"][FILTRO_MUNICIPIO]:
        if v == "TODAS_AS_CATEGORIAS__":
            continue
        m_ign = RE_IGNORADO_UF.match(t)
        if m_ign:
            sigla_pendente = m_ign.group(1)
            continue
        if RE_IGNORADO_EXTERIOR.match(t):
            continue
        m = RE_MUNICIPIO.match(t)
        if not m:
            raise ErroResposta(f"opção de município fora do padrão: {t!r}")
        cod = m.group(1)
        if cod[:2] != uf_atual:
            if cod[:2] in vistos_uf:
                raise ErroResposta(f"bloco da UF {cod[:2]} não contíguo no formulário")
            uf_atual = cod[:2]
            vistos_uf.add(uf_atual)
            if sigla_pendente is not None:
                if sigla_pendente in sigla_para_codigo:
                    raise ErroResposta(f"sigla {sigla_pendente} repetida")
                sigla_para_codigo[sigla_pendente] = uf_atual
            sigla_pendente = None
        elif sigla_pendente is not None:
            raise ErroResposta(f"'MUNICIPIO IGNORADO - {sigla_pendente}' no meio do bloco da UF {uf_atual}")
        sigla = next((s for s, c in sigla_para_codigo.items() if c == uf_atual), None)
        municipios.append({"co_ibge": cod, "nome_tabnet": m.group(2), "co_uf": cod[:2], "sigla_uf": sigla})
    if len({m["co_ibge"] for m in municipios}) != len(municipios):
        raise ErroResposta("município repetido no formulário")
    if len(vistos_uf) != 27:
        raise ErroResposta(f"{len(vistos_uf)} UF no formulário")
    return municipios, sigla_para_codigo


def indice_uf(form: dict[str, Any], nome: str) -> str:
    achados = [v for v, t in form["selects"][FILTRO_UF] if t == nome]
    if len(achados) != 1:
        raise ErroResposta(f"UF {nome!r} não encontrada uma única vez no filtro")
    return achados[0]


# ---------------------------------------------------------------- consultas

def _base(linha: str, comp: str) -> list[tuple[str, str]]:
    return [("Linha", linha), ("Coluna", COLUNA), ("Incremento", INCREMENTO), ("Arquivos", arquivo_do_mes(comp))]


def _fim(zeradas: bool) -> list[tuple[str, str]]:
    return [("formato", "prn")] + ([("zeradas", "exibirlz")] if zeradas else []) + [("mostre", "Mostra")]


def planejar_consultas(form: dict[str, Any], competencias: list[str]) -> list[dict[str, Any]]:
    """Todas as consultas, na ordem de execução (as de um mês ficam juntas no tempo)."""
    conj = conjuntos_do_formulario(form)
    consultas = []
    for comp in competencias:
        checar_limite(comp)
        for c in CONJUNTOS:
            filtros = [(FILTRO_CBO, o["indice"]) for o in conj[c]] if c != TODOS else []
            eco = {ROTULO_FILTRO_CBO: ", ".join(o["rotulo"] for o in conj[c])} if c != TODOS else {}
            consultas.append({"id": f"municipio_{c}_{comp}", "tipo": "municipio", "competencia": comp,
                              "conjunto_cbo": c, "uf": None, "linha": LINHA_MUNICIPIO,
                              "campos": _base(LINHA_MUNICIPIO, comp) + filtros + _fim(True), "eco_filtros": eco})
        consultas.append({"id": f"uf_{TODOS}_{comp}", "tipo": "uf", "competencia": comp, "conjunto_cbo": TODOS,
                          "uf": None, "linha": LINHA_UF, "campos": _base(LINHA_UF, comp) + _fim(True), "eco_filtros": {}})
        consultas.append({"id": f"cbo_{TODOS}_{comp}", "tipo": "cbo", "competencia": comp, "conjunto_cbo": TODOS,
                          "uf": None, "linha": LINHA_CBO, "campos": _base(LINHA_CBO, comp) + _fim(False),
                          "eco_filtros": {}})
        if comp == MES_CONFERENCIA_UF:
            for sigla, nome in UFS_CONFERENCIA.items():
                filtro_uf = [(FILTRO_UF, indice_uf(form, nome))]
                for c in CONJUNTOS:
                    filtros = [(FILTRO_CBO, o["indice"]) for o in conj[c]] if c != TODOS else []
                    eco = {ROTULO_FILTRO_UF: nome}
                    if c != TODOS:
                        eco[ROTULO_FILTRO_CBO] = ", ".join(o["rotulo"] for o in conj[c])
                    consultas.append({"id": f"conferencia_{sigla}_{c}_{comp}", "tipo": "conferencia_uf",
                                      "competencia": comp, "conjunto_cbo": c, "uf": sigla, "linha": LINHA_MUNICIPIO,
                                      "campos": _base(LINHA_MUNICIPIO, comp) + filtro_uf + filtros + _fim(True),
                                      "eco_filtros": eco})
    return consultas


def corpo_post(campos: list[tuple[str, str]]) -> str:
    return urllib.parse.urlencode(campos, encoding="latin-1")


# ---------------------------------------------------------------- leitura da resposta

def ler_resposta(raw: bytes) -> dict[str, Any]:
    """Interpreta a resposta ``prn`` do TabNet. Levanta ErroResposta se a forma não for a esperada."""
    txt = raw.decode("latin-1")
    if txt.count("<PRE>") != 1 or txt.count("</PRE>") != 1:
        msg = re.findall(r"<H2>(.*?)</H2>", txt, re.S | re.I)
        raise ErroResposta(f"resposta sem bloco PRE único; mensagem: {[html.unescape(m).strip() for m in msg]}")
    ini, fim = txt.find("<PRE>"), txt.find("</PRE>")
    cab = html.unescape(txt[:ini + 5])
    h1 = cab.find("</H1>")
    filtros = {k.strip(): v.strip() for k, v in
               re.findall(r"<b>([^<]+?):</b>\s*(.*?)(?=<BR>|<PRE>)", cab[h1:], re.S | re.I)}
    titulo = re.findall(r"<b>([^<:]+)</b><br>", cab[h1:], re.I)
    linhas_txt = [ln for ln in txt[ini + 5:fim].strip("\r\n").splitlines() if ln.strip() not in ("", "&")]
    leitor = csv.reader(io.StringIO("\n".join(linhas_txt)), delimiter=";", quotechar='"')
    tabela = [[html.unescape(c) for c in r] for r in leitor]
    if len(tabela) < 2:
        raise ErroResposta("tabela vazia")
    cabecalho = tabela[0]
    if cabecalho[-1] != "Total":
        raise ErroResposta(f"última coluna não é Total: {cabecalho[-1]!r}")
    subgrupos = []
    for c in cabecalho[1:-1]:
        m = RE_SUBGRUPO.match(c)
        if not m:
            raise ErroResposta(f"coluna fora do padrão de subgrupo: {c!r}")
        subgrupos.append((m.group(1), m.group(2).strip()))
    if len({s for s, _ in subgrupos}) != len(subgrupos):
        raise ErroResposta("subgrupo repetido nas colunas")
    n = len(cabecalho) - 1
    linhas = []
    for r in tabela[1:]:
        if len(r) != n + 1:
            raise ErroResposta(f"linha com {len(r)} campos (esperado {n + 1}): {r[:2]}")
        valores, zeros = [], []
        for x in r[1:]:
            x = x.strip()
            if x == "-":
                valores.append(0)
                zeros.append(True)
            elif re.fullmatch(r"[1-9]\d*", x):
                valores.append(int(x))
                zeros.append(False)
            else:
                # "0" seria zero por arredondamento (legenda do TabNet), impossível numa contagem
                raise ErroResposta(f"valor não reconhecido {x!r} na linha {r[0]!r}")
        linhas.append((r[0].strip(), valores, zeros))
    if linhas[-1][0] != "Total":
        raise ErroResposta(f"última linha não é Total: {linhas[-1][0]!r}")
    if sum(1 for rotulo, _, _ in linhas if rotulo == "Total") != 1:
        raise ErroResposta("mais de uma linha Total")
    return {
        "rotulo_linha": cabecalho[0].strip(),
        "subgrupos": subgrupos,
        "linhas": linhas[:-1],
        "total": linhas[-1][1],
        "filtros_eco": {k: v for k, v in filtros.items() if not k.startswith("Per")},
        "periodo_eco": next((v for k, v in filtros.items() if k.startswith("Per")), None),
        "titulo": titulo[0].strip() if titulo else None,
    }


def conferir_eco(resp: dict[str, Any], consulta: dict[str, Any]) -> None:
    """O TabNet repete no cabeçalho o período e os filtros aplicados: têm de ser os pedidos."""
    erros = []
    if resp["periodo_eco"] != rotulo_do_mes(consulta["competencia"]):
        erros.append(f"período {resp['periodo_eco']!r} != {rotulo_do_mes(consulta['competencia'])!r}")
    if resp["filtros_eco"] != consulta["eco_filtros"]:
        erros.append(f"filtros {sorted(resp['filtros_eco'])} diferentes dos pedidos {sorted(consulta['eco_filtros'])}"
                     if set(resp["filtros_eco"]) != set(consulta["eco_filtros"]) else "lista de filtros diferente da pedida")
    if resp["rotulo_linha"] != ROTULO_LINHA[consulta["linha"]]:
        erros.append(f"linha {resp['rotulo_linha']!r}")
    if erros:
        raise ErroResposta("eco: " + "; ".join(erros))


def somas_conferem(resp: dict[str, Any]) -> dict[str, Any]:
    """Total = soma das linhas (por coluna) e coluna Total = soma das células (por linha)."""
    m = np.array([v for _, v, _ in resp["linhas"]], dtype=np.int64).reshape(len(resp["linhas"]), -1)
    tot = np.array(resp["total"], dtype=np.int64)
    col_ok = bool((m.sum(axis=0) == tot).all())
    lin_ok = bool((m[:, :-1].sum(axis=1) == m[:, -1]).all()) if len(m) else True
    tot_ok = bool(tot[:-1].sum() == tot[-1])
    return {"colunas": col_ok, "linhas": lin_ok, "total_geral": tot_ok, "ok": col_ok and lin_ok and tot_ok}


# ---------------------------------------------------------------- cache

def caminho_bruto(cid: str) -> Path:
    return CACHE_DIR / f"{cid}.html.gz"


def caminho_meta(cid: str) -> Path:
    return CACHE_DIR / f"{cid}.json"


FORMULARIO_ID = "formulario_qabr"


def ler_bruto(cid: str) -> bytes:
    raw = gzip.decompress(caminho_bruto(cid).read_bytes())
    meta = json.loads(caminho_meta(cid).read_text(encoding="utf-8"))
    if sha256_bytes(raw) != meta["sha256_resposta"]:
        raise ErroResposta(f"{cid}: SHA-256 do bruto em cache diferente do metadado")
    return raw


def _gravar_cache(cid: str, raw: bytes, meta: dict[str, Any]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = caminho_bruto(cid).with_suffix(".gz.tmp")
    # mtime=0: o .gz é determinístico para os mesmos bytes
    tmp.write_bytes(gzip.compress(raw, compresslevel=9, mtime=0))
    tmp.replace(caminho_bruto(cid))
    caminho_meta(cid).write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _http(url: str, corpo: bytes | None) -> tuple[bytes, int, str | None]:
    req = urllib.request.Request(url, data=corpo, headers=CABECALHOS_HTTP if corpo else {"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.read(), resp.status, resp.headers.get("Content-Type")


def baixar_formulario(refazer: bool = False) -> dict[str, Any]:
    if not refazer and caminho_meta(FORMULARIO_ID).exists() and caminho_bruto(FORMULARIO_ID).exists():
        raw = ler_bruto(FORMULARIO_ID)
        form = ler_formulario(raw.decode("latin-1"))
        conferir_formulario(form)
        return form
    t0 = time.time()
    raw, status, ctype = _http(URL_FORMULARIO, None)
    form = ler_formulario(raw.decode("latin-1"))
    conferir_formulario(form)
    _gravar_cache(FORMULARIO_ID, raw, {
        "id": FORMULARIO_ID, "url": URL_FORMULARIO, "metodo": "GET",
        "data_hora_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "sha256_resposta": sha256_bytes(raw), "bytes_resposta": len(raw), "http_status": status,
        "content_type": ctype, "segundos": round(time.time() - t0, 1), "status": "ok",
    })
    log(f"formulário baixado: {len(raw):,} bytes")
    return form


def carregar_formulario() -> dict[str, Any]:
    if not caminho_meta(FORMULARIO_ID).exists():
        raise SystemExit("formulário ausente do cache; rode --etapa baixar")
    form = ler_formulario(ler_bruto(FORMULARIO_ID).decode("latin-1"))
    conferir_formulario(form)
    return form


def baixar_consulta(consulta: dict[str, Any], refazer: bool = False) -> dict[str, Any]:
    cid = consulta["id"]
    checar_limite(consulta["competencia"])
    corpo = corpo_post(consulta["campos"])
    if not refazer and caminho_meta(cid).exists() and caminho_bruto(cid).exists():
        meta = json.loads(caminho_meta(cid).read_text(encoding="utf-8"))
        if meta.get("status") == "ok" and meta.get("corpo_post") == corpo:
            return meta
    falhas = []
    for tentativa in range(1, TENTATIVAS + 1):
        quando = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        t0 = time.time()
        try:
            raw, status, ctype = _http(URL_CONSULTA, corpo.encode("ascii"))
            seg = round(time.time() - t0, 1)
            resp = ler_resposta(raw)
            conferir_eco(resp, consulta)
            meta = {
                "id": cid, "tipo": consulta["tipo"], "competencia": consulta["competencia"],
                "conjunto_cbo": consulta["conjunto_cbo"], "uf": consulta["uf"],
                "url": URL_CONSULTA, "metodo": "POST", "codificacao_corpo": "latin-1 (application/x-www-form-urlencoded)",
                "corpo_post": corpo, "data_hora_utc": quando, "sha256_resposta": sha256_bytes(raw),
                "bytes_resposta": len(raw), "http_status": status, "content_type": ctype, "segundos": seg,
                "tentativas": tentativa, "falhas_anteriores": falhas, "status": "ok",
                "periodo_eco": resp["periodo_eco"], "titulo_eco": resp["titulo"],
            }
            _gravar_cache(cid, raw, meta)
            return meta
        except (urllib.error.URLError, TimeoutError, ConnectionError, ErroResposta, OSError) as exc:
            falhas.append({"tentativa": tentativa, "data_hora_utc": quando, "segundos": round(time.time() - t0, 1),
                           "erro": f"{type(exc).__name__}: {exc}"[:500]})
            log(f"  {cid}: falha na tentativa {tentativa}: {falhas[-1]['erro'][:160]}")
            time.sleep(min(15 * 2 ** (tentativa - 1), 240))
    meta = {"id": cid, "tipo": consulta["tipo"], "competencia": consulta["competencia"],
            "conjunto_cbo": consulta["conjunto_cbo"], "uf": consulta["uf"], "url": URL_CONSULTA, "metodo": "POST",
            "corpo_post": corpo, "status": "falha", "tentativas": TENTATIVAS, "falhas_anteriores": falhas}
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    caminho_meta(cid).write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if caminho_bruto(cid).exists():
        caminho_bruto(cid).unlink()
    return meta


def etapa_baixar(competencias: list[str], refazer: bool) -> int:
    form = baixar_formulario(refazer=refazer)
    consultas = planejar_consultas(form, competencias)
    log(f"{len(consultas)} consultas planejadas para {len(competencias)} meses")
    falhas = 0
    t0 = time.time()
    for i, q in enumerate(consultas, 1):
        em_cache = (not refazer and caminho_meta(q["id"]).exists() and caminho_bruto(q["id"]).exists()
                    and json.loads(caminho_meta(q["id"]).read_text(encoding="utf-8")).get("status") == "ok")
        meta = baixar_consulta(q, refazer=refazer)
        if meta["status"] != "ok":
            falhas += 1
        if i % 7 == 0 or meta["status"] != "ok":
            log(f"{i}/{len(consultas)} {q['id']}: {meta['status']} ({time.time() - t0:.0f}s decorridos)")
        if not em_cache:
            time.sleep(PAUSA_ENTRE_CONSULTAS)
    log(f"download terminado: {len(consultas) - falhas} ok, {falhas} com falha; rode --etapa consolidar")
    return 0 if falhas == 0 else 3


# ---------------------------------------------------------------- consolidação

def _classificar_linha_municipio(rotulo: str) -> tuple[str, str | None]:
    """('municipio', co_ibge) | ('ignorado_uf', sigla) | ('ignorado_exterior', None)."""
    m = RE_MUNICIPIO.match(rotulo)
    if m and m.group(1) != "000000":
        return "municipio", m.group(1)
    m = RE_IGNORADO_UF.match(rotulo)
    if m:
        return "ignorado_uf", m.group(1)
    if RE_IGNORADO_EXTERIOR.match(rotulo):
        return "ignorado_exterior", None
    raise ErroResposta(f"linha de município fora do padrão: {rotulo!r}")


def matriz_municipios(resp: dict[str, Any], referencia: list[str]) -> dict[str, Any]:
    """Separa municípios e ignorados; alinha os municípios à lista de referência do formulário."""
    pos = {c: i for i, c in enumerate(referencia)}
    nsub = len(resp["subgrupos"])
    valores = np.zeros((len(referencia), nsub), dtype=np.int64)
    zero = np.zeros((len(referencia), nsub), dtype=bool)
    presente = np.zeros(len(referencia), dtype=bool)
    fora_da_referencia, ignorados = [], []
    for rotulo, vals, zs in resp["linhas"]:
        tipo, chave = _classificar_linha_municipio(rotulo)
        if tipo != "municipio":
            ignorados.append({"rotulo_tabnet": rotulo, "tipo": tipo, "sigla_uf": chave,
                              "valores": vals[:-1], "zeros": zs[:-1]})
            continue
        if chave not in pos:
            fora_da_referencia.append({"co_ibge": chave, "rotulo_tabnet": rotulo, "valores": vals[:-1], "zeros": zs[:-1]})
            continue
        i = pos[chave]
        if presente[i]:
            raise ErroResposta(f"município {chave} repetido na resposta")
        presente[i] = True
        valores[i] = vals[:-1]
        zero[i] = zs[:-1]
    return {"valores": valores, "zero": zero, "presente": presente, "ignorados": ignorados,
            "fora_da_referencia": fora_da_referencia, "subgrupos": [s for s, _ in resp["subgrupos"]]}


def _tabela_painel(comp: str, conjunto: str, codigos: list[str], mm: dict[str, Any]) -> pa.Table:
    nmun, nsub = mm["valores"].shape
    co = np.repeat(np.array(codigos + [x["co_ibge"] for x in mm["fora_da_referencia"]], dtype=object), nsub)
    vals = mm["valores"]
    zero = mm["zero"]
    pres = mm["presente"]
    if mm["fora_da_referencia"]:
        vals = np.vstack([vals, np.array([x["valores"] for x in mm["fora_da_referencia"]], dtype=np.int64)])
        zero = np.vstack([zero, np.array([x["zeros"] for x in mm["fora_da_referencia"]], dtype=bool)])
        pres = np.concatenate([pres, np.ones(len(mm["fora_da_referencia"]), dtype=bool)])
    n = vals.shape[0]
    presente = np.repeat(pres, nsub)
    q = vals.reshape(-1)
    z = zero.reshape(-1)
    status = np.where(~presente, STATUS_AUSENTE, np.where(z, STATUS_ZERO, STATUS_VALOR))
    if ((q > 0) != (status == STATUS_VALOR)).any() or ((status == STATUS_ZERO) & (q != 0)).any():
        raise ErroResposta(f"{conjunto} {comp}: status incoerente com a quantidade")
    qtd = pa.array(q, type=pa.int64(), mask=~presente)
    sub = np.tile(np.array(mm["subgrupos"], dtype=object), n)
    tabela = pa.table({
        "co_ibge": pa.array(co, pa.string()).dictionary_encode(),
        "competencia_processamento": pa.array([comp] * len(q), pa.string()).dictionary_encode(),
        "subgrupo": pa.array(sub, pa.string()).dictionary_encode(),
        "conjunto_cbo": pa.array([conjunto] * len(q), pa.string()).dictionary_encode(),
        "qtd_aprovada": qtd,
        "status": pa.array(status.astype(object), pa.string()).dictionary_encode(),
        "natureza_dos_dados": pa.array([NATUREZA] * len(q), pa.string()).dictionary_encode(),
    })
    # ordem determinística: municípios na ordem do formulário × subgrupos na ordem das colunas da resposta
    return tabela.cast(ESQUEMA_PAINEL)


def _linhas_longas(resp: dict[str, Any], comp: str, chave_nome: str, conv) -> list[dict[str, Any]]:
    subs = [s for s, _ in resp["subgrupos"]]
    saida = []
    for rotulo, vals, zs in resp["linhas"]:
        chave = conv(rotulo)
        for s, v, z in zip(subs, vals[:-1], zs[:-1]):
            saida.append({chave_nome: chave, "rotulo_tabnet": rotulo, "competencia_processamento": comp,
                          "subgrupo": s, "qtd_aprovada": v, "status": STATUS_ZERO if z else STATUS_VALOR})
    return saida


def _uf_da_linha(rotulo: str) -> str | None:
    m = RE_UF.match(rotulo)
    return m.group(1) if m else None


def _cbo_da_linha(rotulo: str) -> str:
    m = RE_CBO.match(rotulo)
    if not m:
        raise ErroResposta(f"linha de CBO fora do padrão: {rotulo!r}")
    return m.group(1)


def consolidar(competencias: list[str]) -> int:
    t_ini = time.time()
    form = carregar_formulario()
    meta_form = json.loads(caminho_meta(FORMULARIO_ID).read_text(encoding="utf-8"))
    conj = conjuntos_do_formulario(form)
    municipios, sigla_para_codigo = municipios_do_formulario(form)
    referencia = [m["co_ibge"] for m in municipios]
    consultas = planejar_consultas(form, competencias)

    # 1. todas as consultas precisam estar em cache, íntegras e com eco conferido
    metas, faltam = {}, []
    for q in consultas:
        p = caminho_meta(q["id"])
        meta = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"status": "nao_baixada"}
        metas[q["id"]] = meta
        if meta.get("status") != "ok" or not caminho_bruto(q["id"]).exists() or meta.get("corpo_post") != corpo_post(q["campos"]):
            faltam.append({"id": q["id"], "status": meta.get("status"), "falhas": meta.get("falhas_anteriores")})
    if faltam:
        log(f"FAIL CLOSED: {len(faltam)} consultas sem resposta válida em cache; nada gravado em output/")
        for f in faltam[:20]:
            log(f"  {f['id']}: {f['status']}")
        return 2

    validacoes: dict[str, Any] = {}
    erros: list[str] = []
    tmp_painel = CACHE_DIR / "painel.parquet.tmp"
    escritor = pq.ParquetWriter(tmp_painel, ESQUEMA_PAINEL, compression="zstd", compression_level=9,
                                use_dictionary=True)
    linhas_painel = 0
    ignorados_reg, uf_reg, cbo_reg, subgrupos_reg, cobertura_reg = [], [], [], [], []
    rotulos_subgrupo: dict[str, set[str]] = {}
    fora_ref_reg: dict[str, list[str]] = {}
    ausentes_reg: dict[str, int] = {}
    val_somas, val_conj_todos, val_uf, val_cbo, val_ausentes_cbo, val_conf = [], [], [], [], [], []
    try:
        for comp in competencias:
            resp = {}
            for q in consultas:
                if q["competencia"] != comp:
                    continue
                r = ler_resposta(ler_bruto(q["id"]))
                conferir_eco(r, q)
                s = somas_conferem(r)
                val_somas.append({"id": q["id"], **s})
                if not s["ok"]:
                    erros.append(f"{q['id']}: total da resposta não é a soma das linhas")
                for cod, rot in r["subgrupos"]:
                    rotulos_subgrupo.setdefault(cod, set()).add(rot)
                resp[q["id"]] = r

            mats = {}
            for c in CONJUNTOS:
                r = resp[f"municipio_{c}_{comp}"]
                mm = matriz_municipios(r, referencia)
                mats[c] = mm
                if mm["fora_da_referencia"]:
                    fora_ref_reg[f"{c}_{comp}"] = [x["co_ibge"] for x in mm["fora_da_referencia"]]
                n_aus = int((~mm["presente"]).sum())
                if n_aus:
                    ausentes_reg[f"{c}_{comp}"] = n_aus
                tabela = _tabela_painel(comp, c, referencia, mm)
                escritor.write_table(tabela)
                linhas_painel += tabela.num_rows
                for ig in mm["ignorados"]:
                    for s_, v, z in zip(mm["subgrupos"], ig["valores"], ig["zeros"]):
                        ignorados_reg.append({"rotulo_tabnet": ig["rotulo_tabnet"], "tipo_ignorado": ig["tipo"],
                                              "sigla_uf": ig["sigla_uf"], "competencia_processamento": comp,
                                              "subgrupo": s_, "conjunto_cbo": c, "qtd_aprovada": v,
                                              "status": STATUS_ZERO if z else STATUS_VALOR})
                # cobertura (relato)
                mun_prod = int((mm["valores"].sum(axis=1) > 0).sum())
                cobertura_reg.append({
                    "competencia_processamento": comp, "conjunto_cbo": c,
                    "municipios_na_resposta": int(mm["presente"].sum()) + len(mm["fora_da_referencia"]),
                    "municipios_ausentes_da_resposta": n_aus,
                    "municipios_com_producao": mun_prod + sum(1 for x in mm["fora_da_referencia"] if sum(x["valores"])),
                    "qtd_municipios": int(mm["valores"].sum()) + sum(sum(x["valores"]) for x in mm["fora_da_referencia"]),
                    "qtd_ignorados": int(sum(sum(ig["valores"]) for ig in mm["ignorados"])),
                    "qtd_total_tabnet": int(r["total"][-1]),
                    "subgrupos_na_resposta": len(mm["subgrupos"]),
                })

            # 2. conjuntos <= todos, célula a célula (município × subgrupo); mfc <= especialistas_nao_alvo
            subs_todos = mats[TODOS]["subgrupos"]

            def alinhar(c: str) -> np.ndarray:
                m = np.zeros((len(referencia), len(subs_todos)), dtype=np.int64)
                for j, s_ in enumerate(mats[c]["subgrupos"]):
                    if s_ not in subs_todos:
                        raise ErroResposta(f"{c} {comp}: subgrupo {s_} ausente da consulta sem filtro")
                    m[:, subs_todos.index(s_)] = mats[c]["valores"][:, j]
                return m
            al = {c: alinhar(c) for c in CONJUNTOS}
            soma_disj = sum(al[c] for c in CONJUNTOS_DISJUNTOS)
            ok_todos = bool((soma_disj <= al[TODOS]).all())
            ok_mfc = bool((al[a09.GRUPO_MFC] <= al["especialistas_nao_alvo"]).all())
            val_conj_todos.append({
                "competencia": comp, "soma_disjuntos_le_todos_celula_a_celula": ok_todos,
                "mfc_le_especialistas_nao_alvo_celula_a_celula": ok_mfc,
                "qtd_soma_disjuntos": int(soma_disj.sum()), "qtd_todos": int(al[TODOS].sum()),
            })
            if not (ok_todos and ok_mfc):
                erros.append(f"{comp}: conjunto maior que o total sem filtro em alguma célula")

            # 3. todos: total nacional e por UF contra a consulta por UF
            r_uf = resp[f"uf_{TODOS}_{comp}"]
            r_mt = resp[f"municipio_{TODOS}_{comp}"]
            subs_uf = [s_ for s_, _ in r_uf["subgrupos"]]
            ok_nac = subs_uf == subs_todos and r_uf["total"] == r_mt["total"]
            difs_uf = []
            por_uf_mun: dict[str, np.ndarray] = {}
            for i, cod in enumerate(referencia):
                por_uf_mun.setdefault(cod[:2], np.zeros(len(subs_todos), dtype=np.int64))
                por_uf_mun[cod[:2]] += mats[TODOS]["valores"][i]
            for x in mats[TODOS]["fora_da_referencia"]:
                por_uf_mun.setdefault(x["co_ibge"][:2], np.zeros(len(subs_todos), dtype=np.int64))
                por_uf_mun[x["co_ibge"][:2]] += np.array(x["valores"], dtype=np.int64)
            for ig in mats[TODOS]["ignorados"]:
                chave = sigla_para_codigo.get(ig["sigla_uf"]) if ig["tipo"] == "ignorado_uf" else "ignorado_exterior"
                por_uf_mun.setdefault(chave, np.zeros(len(subs_todos), dtype=np.int64))
                por_uf_mun[chave] += np.array(ig["valores"], dtype=np.int64)
            linhas_uf = {}
            for rotulo, vals, zs in r_uf["linhas"]:
                cod_uf = _uf_da_linha(rotulo)
                linhas_uf[cod_uf or "ignorado_exterior"] = np.array(vals[:-1], dtype=np.int64)
                for s_, v, z in zip(subs_uf, vals[:-1], zs[:-1]):
                    uf_reg.append({"co_uf": cod_uf, "rotulo_tabnet": rotulo, "competencia_processamento": comp,
                                   "subgrupo": s_, "qtd_aprovada": v, "status": STATUS_ZERO if z else STATUS_VALOR})
            if subs_uf == subs_todos:
                for chave in sorted(set(linhas_uf) | set(por_uf_mun)):
                    a = linhas_uf.get(chave, np.zeros(len(subs_todos), dtype=np.int64))
                    b = por_uf_mun.get(chave, np.zeros(len(subs_todos), dtype=np.int64))
                    if not (a == b).all():
                        difs_uf.append({"uf": chave, "qtd_consulta_uf": int(a.sum()), "qtd_soma_municipios": int(b.sum())})
            val_uf.append({"competencia": comp, "total_nacional_igual": bool(ok_nac),
                           "ufs_com_diferenca": difs_uf, "qtd_total": int(r_mt["total"][-1])})
            if not ok_nac or difs_uf:
                erros.append(f"{comp}: consulta por município (sem filtro) não reproduz a consulta por UF")

            # 4. cada conjunto contra a soma das suas CBO na consulta por CBO; completude do CBO
            r_cbo = resp[f"cbo_{TODOS}_{comp}"]
            subs_cbo = [s_ for s_, _ in r_cbo["subgrupos"]]
            por_cbo = {}
            for rotulo, vals, zs in r_cbo["linhas"]:
                cod = _cbo_da_linha(rotulo)
                por_cbo[cod] = vals[:-1]
                for s_, v, z in zip(subs_cbo, vals[:-1], zs[:-1]):
                    cbo_reg.append({"co_cbo": cod, "rotulo_tabnet": rotulo, "competencia_processamento": comp,
                                    "subgrupo": s_, "qtd_aprovada": v, "status": STATUS_ZERO if z else STATUS_VALOR})
            tot_mt = dict(zip(subs_todos, r_mt["total"][:-1]))
            tot_cbo_total = dict(zip(subs_cbo, r_cbo["total"][:-1]))
            for c in CONJUNTOS:
                r_c = resp[f"municipio_{c}_{comp}"]
                tot_c = dict(zip([s_ for s_, _ in r_c["subgrupos"]], r_c["total"][:-1]))
                codigos = {o["co_cbo"] for o in conj[c]} if c != TODOS else None
                for s_ in subs_todos:
                    if c == TODOS:
                        por_cbo_s = tot_cbo_total.get(s_, 0) if s_ in subs_cbo else 0
                    else:
                        j = subs_cbo.index(s_) if s_ in subs_cbo else None
                        por_cbo_s = sum(v[j] for k, v in por_cbo.items() if k in codigos) if j is not None else 0
                    presente = s_ in tot_c
                    reg = {
                        "competencia_processamento": comp, "conjunto_cbo": c, "subgrupo": s_,
                        "presente_na_resposta": presente,
                        "total_tabnet_municipio": int(tot_c[s_]) if presente else None,
                        "total_tabnet_uf": int(dict(zip(subs_uf, r_uf["total"][:-1])).get(s_, 0)) if c == TODOS else None,
                        "total_soma_cbo": int(por_cbo_s),
                    }
                    if c == TODOS:
                        reg["producao_sem_cbo_na_tabela"] = int(tot_mt[s_] - por_cbo_s)
                        if tot_mt[s_] < por_cbo_s:
                            erros.append(f"{comp} {s_}: soma por CBO maior que o total sem filtro")
                    else:
                        reg["producao_sem_cbo_na_tabela"] = None
                        ok = (tot_c.get(s_, 0) == por_cbo_s)
                        val_cbo.append({"competencia": comp, "conjunto_cbo": c, "subgrupo": s_, "ok": bool(ok),
                                        "presente_na_resposta": presente})
                        if not ok:
                            erros.append(f"{comp} {c} {s_}: total do conjunto {tot_c.get(s_)} != soma das CBO {por_cbo_s}")
                        if not presente:
                            val_ausentes_cbo.append({"competencia": comp, "conjunto_cbo": c, "subgrupo": s_,
                                                     "soma_cbo": int(por_cbo_s)})
                    subgrupos_reg.append(reg)
                faltando = set(tot_c) - set(subs_todos)
                if faltando:
                    erros.append(f"{comp} {c}: subgrupos fora da consulta sem filtro: {sorted(faltando)}")

            # 5. conferência célula a célula das UF pequenas
            if comp == MES_CONFERENCIA_UF:
                for sigla in UFS_CONFERENCIA:
                    cod_uf = sigla_para_codigo[sigla]
                    for c in CONJUNTOS:
                        r_f = resp[f"conferencia_{sigla}_{c}_{comp}"]
                        nac = mats[c]
                        subs_f = [s_ for s_, _ in r_f["subgrupos"]]
                        problemas = []
                        vistos = set()
                        for rotulo, vals, zs in r_f["linhas"]:
                            tipo, chave = _classificar_linha_municipio(rotulo)
                            if tipo == "municipio":
                                if chave[:2] != cod_uf:
                                    # com exibirlz o TabNet lista todos os municípios; os de outra UF têm de vir zerados
                                    if sum(vals) != 0:
                                        problemas.append(f"município de outra UF com produção: {chave}")
                                    continue
                                i = referencia.index(chave)
                                vistos.add(chave)
                                for s_, v in zip(subs_f, vals[:-1]):
                                    if s_ not in nac["subgrupos"]:
                                        problemas.append(f"{chave} {s_}: subgrupo ausente da consulta nacional")
                                    elif nac["valores"][i, nac["subgrupos"].index(s_)] != v:
                                        problemas.append(f"{chave} {s_}: {v} != nacional")
                            elif tipo == "ignorado_uf" and chave == sigla:
                                ig = next(x for x in nac["ignorados"] if x["sigla_uf"] == sigla)
                                for s_, v in zip(subs_f, vals[:-1]):
                                    if ig["valores"][nac["subgrupos"].index(s_)] != v:
                                        problemas.append(f"ignorado {sigla} {s_}: {v} != nacional")
                            elif sum(vals) != 0:
                                problemas.append(f"linha inesperada com produção: {rotulo}")
                        esperados = {m for m in referencia if m[:2] == cod_uf}
                        if vistos != esperados:
                            problemas.append(f"municípios da UF: {len(vistos)} na consulta filtrada, {len(esperados)} esperados")
                        # subgrupos ausentes da consulta filtrada: zero nos municípios da UF na nacional
                        idx_uf = [referencia.index(m) for m in sorted(esperados)]
                        for j, s_ in enumerate(nac["subgrupos"]):
                            if s_ not in subs_f and nac["valores"][idx_uf, j].sum() != 0:
                                problemas.append(f"subgrupo {s_} ausente na consulta filtrada mas com produção na nacional")
                        n_celulas = len(vistos) * len(subs_f)
                        val_conf.append({"uf": sigla, "conjunto_cbo": c, "competencia": comp,
                                         "municipios": len(vistos), "celulas_comparadas": n_celulas,
                                         "qtd_total": int(r_f["total"][-1]), "problemas": problemas[:20],
                                         "ok": not problemas})
                        if problemas:
                            erros.append(f"conferência {sigla} {c}: {problemas[:3]}")
            log(f"{comp}: consolidado ({linhas_painel:,} linhas de painel até aqui)")
    except ErroResposta as exc:
        escritor.close()
        tmp_painel.unlink(missing_ok=True)
        log(f"FAIL CLOSED: resposta em cache fora da forma esperada ({exc}); nada gravado em output/")
        return 2
    finally:
        if escritor.is_open:
            escritor.close()

    # subgrupo ausente da resposta de um conjunto: a soma das CBO do conjunto tem de ser zero
    ausentes_com_producao = [x for x in val_ausentes_cbo if x["soma_cbo"] != 0]
    # 6. cobertura: sinalização (relato, não correção)
    cob = pd.DataFrame(cobertura_reg)
    cob["sinal_queda"] = sinalizar_quedas(cob)
    cob["natureza_dos_dados"] = NATUREZA

    validacoes = {
        "V1_total_igual_soma_das_linhas": {
            "descricao": "em cada resposta, linha Total = soma das linhas (municípios + ignorados) por coluna, e coluna Total = soma das células por linha",
            "respostas": len(val_somas), "respostas_com_falha": [v["id"] for v in val_somas if not v["ok"]],
            "status": "APROVADO" if all(v["ok"] for v in val_somas) else "REPROVADO"},
        "V2_conjuntos_le_todos": {
            "descricao": "alvo_pmme + especialistas_nao_alvo + generalistas <= todos_profissionais e mfc_225130 <= especialistas_nao_alvo, em cada célula município × subgrupo × mês",
            "por_competencia": val_conj_todos,
            "status": "APROVADO" if all(v["soma_disjuntos_le_todos_celula_a_celula"] and
                                        v["mfc_le_especialistas_nao_alvo_celula_a_celula"] for v in val_conj_todos) else "REPROVADO"},
        "V3_todos_contra_consulta_uf": {
            "descricao": "consulta por município sem filtro de CBO: total nacional por subgrupo igual ao da consulta Linha=UF, e soma dos municípios + ignorado da UF igual à linha da UF",
            "por_competencia": val_uf,
            "status": "APROVADO" if all(v["total_nacional_igual"] and not v["ufs_com_diferenca"] for v in val_uf) else "REPROVADO"},
        "V4_conjunto_contra_soma_das_cbo": {
            "descricao": "total nacional de cada conjunto por subgrupo (linha Total da consulta por município filtrada) igual à soma das linhas das suas CBO na consulta Linha=Profissional - CBO sem filtro",
            "celulas_comparadas": len(val_cbo), "celulas_com_diferenca": [v for v in val_cbo if not v["ok"]][:50],
            "subgrupos_ausentes_da_resposta_do_conjunto": len(val_ausentes_cbo),
            "subgrupos_ausentes_com_producao_nas_cbo_do_conjunto": ausentes_com_producao[:50],
            "status": "APROVADO" if all(v["ok"] for v in val_cbo) and not ausentes_com_producao else "REPROVADO"},
        "V5_conferencia_uf_celula_a_celula": {
            "descricao": f"consultas filtradas por UF ({', '.join(UFS_CONFERENCIA)}) em {MES_CONFERENCIA_UF}, cada conjunto: cada célula igual à da consulta nacional; mesmos municípios; subgrupo ausente na filtrada é zero na nacional",
            "resultados": val_conf,
            "status": "APROVADO" if val_conf and all(v["ok"] for v in val_conf) else
                      ("NAO_EXECUTADA" if not val_conf else "REPROVADO")},
        "V6_cobertura": {
            "descricao": f"relato: meses com municípios com produção < {LIMIAR_QUEDA_MUNICIPIOS:.0%} da mediana do conjunto ou quantidade < {LIMIAR_QUEDA_TOTAL:.0%} da mediana; nada é corrigido",
            "meses_sinalizados": cob.loc[cob["sinal_queda"] != "", ["competencia_processamento", "conjunto_cbo", "sinal_queda"]].to_dict(orient="records"),
            "municipios_ausentes_da_resposta": ausentes_reg,
            "municipios_fora_da_lista_do_formulario": fora_ref_reg,
            "status": "RELATO"},
        "V7_eco_e_limites": {
            "descricao": "período e filtros repetidos pelo TabNet iguais aos pedidos em todas as respostas; nenhum mês >= 202609 nem > 202607",
            "status": "APROVADO" if all(c < LIMITE_EXCLUSIVO and c <= ULTIMA_COMPETENCIA for c in competencias) else "REPROVADO"},
    }
    obrigatorias = [k for k, v in validacoes.items() if v["status"] not in ("APROVADO", "RELATO")]
    if erros or obrigatorias:
        log(f"FAIL CLOSED: validação reprovada ({obrigatorias}); nada gravado em output/")
        for e in erros[:30]:
            log(f"  {e}")
        diag = CACHE_DIR / "diagnostico_validacao_reprovada.json"
        diag.write_text(json.dumps({"erros": erros, "validacoes": validacoes}, ensure_ascii=False, indent=2, default=str),
                        encoding="utf-8")
        log(f"diagnóstico (fora do Git): {_rel(diag)}")
        tmp_painel.unlink(missing_ok=True)
        return 2

    # 7. gravação (só depois de todas as validações)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.move(str(tmp_painel), PAINEL_FILE)
    _gravar_parquet(pd.DataFrame(ignorados_reg), IGNORADOS_FILE,
                    ["rotulo_tabnet", "tipo_ignorado", "sigla_uf", "competencia_processamento", "subgrupo",
                     "conjunto_cbo", "qtd_aprovada", "status"])
    _gravar_parquet(pd.DataFrame(uf_reg), UF_FILE,
                    ["co_uf", "rotulo_tabnet", "competencia_processamento", "subgrupo", "qtd_aprovada", "status"])
    cbo_df = pd.DataFrame(cbo_reg)
    membro = {o["co_cbo"]: c for c in CONJUNTOS_DISJUNTOS for o in conj[c]}
    cbo_df["conjunto_cbo"] = cbo_df["co_cbo"].map(membro).fillna(
        cbo_df["co_cbo"].str[:4].isin(a09.PREFIXOS_MEDICOS).map({True: "outro_medico", False: "nao_medico"}))
    cbo_df["em_mfc_225130"] = cbo_df["co_cbo"] == a09.MFC
    _gravar_parquet(cbo_df, CBO_FILE, ["co_cbo", "rotulo_tabnet", "conjunto_cbo", "em_mfc_225130",
                                        "competencia_processamento", "subgrupo", "qtd_aprovada", "status"])
    sub_df = pd.DataFrame(subgrupos_reg)
    sub_df["rotulo_subgrupo"] = sub_df["subgrupo"].map(lambda s_: " | ".join(sorted(rotulos_subgrupo[s_])))
    sub_df["natureza_dos_dados"] = NATUREZA
    for col in ("total_tabnet_municipio", "total_tabnet_uf", "producao_sem_cbo_na_tabela"):
        sub_df[col] = sub_df[col].astype("Int64")
    sub_df.to_csv(SUBGRUPOS_FILE, index=False, lineterminator="\n")
    cob.to_csv(COBERTURA_FILE, index=False, lineterminator="\n")
    conj_df = pd.DataFrame([{"conjunto_cbo": c, "co_cbo": o["co_cbo"], "rotulo_tabnet": o["rotulo"],
                             "indice_formulario": o["indice"]} for c in CONJUNTOS_CBO for o in conj[c]])
    medicos = [o for o in opcoes_cbo(form) if o["co_cbo"][:4] in a09.PREFIXOS_MEDICOS]
    conj_df = pd.concat([conj_df, pd.DataFrame([{"conjunto_cbo": "_opcao_medica_do_formulario", "co_cbo": o["co_cbo"],
                                                 "rotulo_tabnet": o["rotulo"], "indice_formulario": o["indice"]}
                                                for o in medicos])], ignore_index=True)
    conj_df["natureza_dos_dados"] = NATUREZA
    conj_df.to_csv(CONJUNTOS_FILE, index=False, lineterminator="\n")
    mun_df = pd.DataFrame(municipios)
    mun_df["natureza_dos_dados"] = NATUREZA
    mun_df.to_csv(MUNICIPIOS_FILE, index=False, lineterminator="\n")

    gravar_manifesto(competencias, consultas, metas, meta_form, conj, validacoes, linhas_painel,
                     len(referencia), round(time.time() - t_ini, 1))
    gravar_resumo()
    log(f"Painel: {linhas_painel:,} linhas, {PAINEL_FILE.stat().st_size / 1024**2:.1f} MB; manifesto e resumo gravados")
    return 0


def sinalizar_quedas(cob: pd.DataFrame) -> pd.Series:
    """Sinal de queda por linha (mês × conjunto), contra a mediana do próprio conjunto. Só relato."""
    med_m = cob.groupby("conjunto_cbo")["municipios_com_producao"].transform("median")
    med_q = cob.groupby("conjunto_cbo")["qtd_municipios"].transform("median")
    sinais = []
    for n_m, q, mm, mq in zip(cob["municipios_com_producao"], cob["qtd_municipios"], med_m, med_q):
        motivos = []
        if n_m < LIMIAR_QUEDA_MUNICIPIOS * mm:
            motivos.append(f"municípios com produção < {LIMIAR_QUEDA_MUNICIPIOS:.0%} da mediana do conjunto ({mm:.0f})")
        if q < LIMIAR_QUEDA_TOTAL * mq:
            motivos.append(f"quantidade < {LIMIAR_QUEDA_TOTAL:.0%} da mediana do conjunto ({mq:.0f})")
        sinais.append("; ".join(motivos))
    return pd.Series(sinais, index=cob.index, dtype=object)


def _gravar_parquet(df: pd.DataFrame, path: Path, colunas: list[str]) -> None:
    df = df[colunas].copy()
    df["qtd_aprovada"] = df["qtd_aprovada"].astype("int64")
    df["natureza_dos_dados"] = NATUREZA
    df.to_parquet(path, index=False, compression="zstd")


# ---------------------------------------------------------------- manifesto e resumo

def saidas() -> tuple[Path, ...]:
    """Saídas tabulares registradas no manifesto (lidas na hora: os testes as redirecionam)."""
    return (PAINEL_FILE, IGNORADOS_FILE, UF_FILE, CBO_FILE, SUBGRUPOS_FILE, COBERTURA_FILE, CONJUNTOS_FILE,
            MUNICIPIOS_FILE)


def _info_saida(p: Path) -> dict[str, Any]:
    if p.suffix == ".parquet":
        linhas = pq.read_metadata(p).num_rows
    else:
        with p.open(encoding="utf-8") as f:
            linhas = sum(1 for _ in f) - 1
    return {"sha256": sha256_arquivo(p), "bytes": p.stat().st_size, "linhas": linhas}


def gravar_manifesto(competencias, consultas, metas, meta_form, conj, validacoes, linhas_painel, n_ref, segundos) -> None:
    alvo, _, versao = a09.carregar_ponte()
    reg_consultas = []
    for q in consultas:
        m = metas[q["id"]]
        reg_consultas.append({k: m.get(k) for k in (
            "id", "tipo", "competencia", "conjunto_cbo", "uf", "url", "metodo", "corpo_post", "data_hora_utc",
            "sha256_resposta", "bytes_resposta", "http_status", "segundos", "tentativas", "falhas_anteriores",
            "status", "periodo_eco")})
    datas = sorted(m["data_hora_utc"] for m in metas.values() if m.get("data_hora_utc"))
    tempo_download = round(sum(m.get("segundos") or 0 for m in metas.values()), 1)
    manifesto = {
        "gerador": "scripts/aquisicao/a12_adquirir_sia_tabnet.py",
        "protocolo": "docs/06_execucao/47_protocolo_producao_especializada.md (§2–§4, §6; aquisição SIA)",
        "estatuto": "PROTOCOLO_47_POS_SINTESE",
        "natureza_dos_dados": NATUREZA,
        "data_execucao": dt.date.today().isoformat(),
        "fonte": {
            "nome": "SIA/SUS — Produção Ambulatorial do SUS - Brasil - por local de atendimento (TabNet, DATASUS/MS)",
            "url_formulario": URL_FORMULARIO,
            "url_consulta": URL_CONSULTA,
            "formulario": {k: meta_form.get(k) for k in ("data_hora_utc", "sha256_resposta", "bytes_resposta")},
            "nota_https": "o TabNet só respondeu por HTTP neste ambiente; HTTPS falha",
            "nota_tabnet": "rodapé do TabNet: dados dos últimos seis meses sujeitos a atualização",
        },
        "unidade": "quantidade aprovada (Qtd.aprovada) de procedimentos ambulatoriais",
        "chaves": {
            "co_ibge": "município do local de atendimento (estabelecimento), 6 dígitos do TabNet",
            "competencia_processamento": "mês de processamento (arquivo qabrAAMM.dbf), não o mês de atendimento",
            "subgrupo": "subgrupo SIGTAP do procedimento (4 dígitos)",
            "conjunto_cbo": "conjunto de CBO do profissional executante, regra do a09",
        },
        "filtros_e_opcoes": {
            "Linha": [LINHA_MUNICIPIO, LINHA_UF, LINHA_CBO], "Coluna": COLUNA, "Incremento": INCREMENTO,
            "formato": "prn", "zeradas": "exibirlz (municípios zerados aparecem; colunas sem registro não)",
            "filtro_cbo": FILTRO_CBO, "filtro_uf": f"{FILTRO_UF} (só na conferência {', '.join(UFS_CONFERENCIA)})",
            "nenhum_outro_filtro": "sem filtro de financiamento, documento (BPA-C/BPA-I/APAC/RAAS), complexidade, gestão ou prestador",
            "qtd_apresentada": "não adquirida: o TabNet recusa mais de um Incremento com Coluna ativa ('Múltiplos conteúdos exigem coluna não ativa'), o que dobraria as consultas",
        },
        "competencias_planejadas": COMPETENCIAS,
        "competencias_obtidas": competencias,
        "limite_ciclo3": f"nenhum mês >= {LIMITE_EXCLUSIVO} é pedido ou lido; o SIA vai até {ULTIMA_COMPETENCIA} (protocolo 47, §6)",
        "conjuntos_cbo": {
            "regra": "importada de scripts/aquisicao/a09_adquirir_cnes_nacional.py: alvo_pmme = CBO-alvo da ponte; generalistas = a09.GENERALISTAS; mfc_225130 = a09.MFC; especialistas_nao_alvo = CBO 2251/2252/2253 fora do alvo e dos generalistas (contém 225130); a classificação é a própria a09.agregar_mes aplicada à lista de CBO do formulário",
            "ponte": {"arquivo": _rel(PONTE_FILE), "versao": versao, "cbos_alvo": alvo},
            "generalistas_a09": list(a09.GENERALISTAS),
            "mfc_a09": a09.MFC,
            "todos_profissionais": "sem filtro de CBO (inclui produção sem CBO na tabela do TabNet)",
            "listas": {c: [{"co_cbo": o["co_cbo"], "rotulo_tabnet": o["rotulo"], "indice_formulario": o["indice"]}
                           for o in conj[c]] for c in CONJUNTOS_CBO},
            "fora_dos_conjuntos": "família 2231 (inclui 2231F9, médico residente): médica, mas fora dos quatro conjuntos, como no a09",
        },
        "regras_de_status": {
            STATUS_VALOR: "valor positivo devolvido pelo TabNet",
            STATUS_ZERO: "'-' no TabNet: dado numérico igual a 0 não resultante de arredondamento (legenda do TabNet); qtd_aprovada = 0",
            STATUS_AUSENTE: "município da lista do formulário que não veio na resposta; qtd_aprovada nula",
            "subgrupo_sem_linha": "subgrupo que não é coluna da resposta não tem linha no painel (o TabNet omite colunas sem registro sob o filtro, mesmo com exibirlz); a presença por consulta está em sia_subgrupos_por_consulta.csv e a V4 confere que a soma das CBO do conjunto é zero nesses subgrupos",
            "consulta_com_falha": "não gera linhas: a consolidação para (fail closed) e nada é gravado",
            "municipio_ignorado": "linhas 'MUNICIPIO IGNORADO - UF' e '000000 Ignorado ou exterior' ficam só em sia_municipio_ignorado_mes_subgrupo_cbo.parquet, nunca atribuídas a município",
            "valor_0": "'0' (zero por arredondamento) é impossível numa contagem; se aparecer, a leitura falha",
        },
        "municipios_do_formulario": n_ref,
        "conferencia_uf": {"mes": MES_CONFERENCIA_UF, "ufs": UFS_CONFERENCIA},
        "limiares_cobertura": {"municipios": LIMIAR_QUEDA_MUNICIPIOS, "quantidade": LIMIAR_QUEDA_TOTAL},
        "validacoes": validacoes,
        "consultas": {
            "n": len(reg_consultas), "primeira_utc": datas[0] if datas else None, "ultima_utc": datas[-1] if datas else None,
            "segundos_de_resposta_somados": tempo_download,
            "com_mais_de_uma_tentativa": [q["id"] for q in reg_consultas if (q.get("tentativas") or 1) > 1],
            "divididas_por_uf": [],
            "lista": reg_consultas,
        },
        "segundos_consolidacao": segundos,
        "entradas_locais": {
            _rel(PONTE_FILE): {"sha256": sha256_arquivo(PONTE_FILE), "uso": "CBO-alvo (a09.carregar_ponte)"},
            "scripts/aquisicao/a09_adquirir_cnes_nacional.py": {
                "sha256": sha256_arquivo(A09_FILE),
                "uso": "regra dos conjuntos de CBO (importada)"},
        },
        "saidas": {_rel(p): _info_saida(p) for p in saidas()},
        "painel": {"arquivo": _rel(PAINEL_FILE), "linhas": linhas_painel,
                   "colunas": COLUNAS_PAINEL, "conjuntos": list(CONJUNTOS)},
        "cache_bruto": {"diretorio": _rel(CACHE_DIR), "git": "ignorado (.gitignore)",
                        "formato": "<id>.html.gz (resposta bruta, gzip) e <id>.json (metadado); SHA-256 da resposta sem compressão"},
        "cegamento": "nenhum IVS lido; nada por faixa, lado de corte, bolsa ou tratamento",
    }
    MANIFESTO_FILE.write_text(json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def gravar_resumo() -> None:
    """Resumo legível, gerado das saídas (só totais nacionais e contagens; nada por IVS)."""
    man = json.loads(MANIFESTO_FILE.read_text(encoding="utf-8"))
    cob = pd.read_csv(COBERTURA_FILE, dtype={"competencia_processamento": str})
    sub = pd.read_csv(SUBGRUPOS_FILE, dtype={"competencia_processamento": str, "subgrupo": str})
    v = man["validacoes"]
    linhas = [
        "# A12 — resumo gerado do SIA/SUS (TabNet)",
        "",
        f"Gerado por `scripts/aquisicao/a12_adquirir_sia_tabnet.py` em {man['data_execucao']}. Não editar à mão. "
        "Natureza dos dados: EMPIRICO. Só totais nacionais e contagens; nada por faixa, lado de corte ou IVS.",
        "",
        "## Aquisição",
        "",
        f"- Meses de processamento: {len(man['competencias_obtidas'])} "
        f"({man['competencias_obtidas'][0]} a {man['competencias_obtidas'][-1]}).",
        f"- Consultas: {man['consultas']['n']}, entre {man['consultas']['primeira_utc']} e "
        f"{man['consultas']['ultima_utc']} (UTC); com mais de uma tentativa: "
        f"{len(man['consultas']['com_mais_de_uma_tentativa'])}.",
        f"- Municípios na lista do formulário: {man['municipios_do_formulario']}.",
        f"- Linhas do painel: {man['painel']['linhas']}.",
        "",
        "## Validações",
        "",
        "| Validação | Status |",
        "|---|---|",
    ]
    for k, x in v.items():
        linhas.append(f"| {k} | {x['status']} |")
    linhas += ["", "## Conjuntos de CBO", "", "| Conjunto | CBO |", "|---|---|"]
    for c, lst in man["conjuntos_cbo"]["listas"].items():
        linhas.append(f"| {c} | {', '.join(o['co_cbo'] for o in lst)} |")
    linhas += ["", "## Cobertura por mês e conjunto", "",
               "Municípios com produção = municípios com quantidade aprovada > 0 em algum subgrupo.", ""]
    for c in CONJUNTOS:
        parte = cob.loc[cob["conjunto_cbo"] == c]
        linhas += [f"### {c}", "", "| Mês | Municípios com produção | Qtd. municípios | Qtd. ignorados | Total TabNet | Subgrupos | Sinal |",
                   "|---|---:|---:|---:|---:|---:|---|"]
        for r in parte.itertuples(index=False):
            sinal = r.sinal_queda if isinstance(r.sinal_queda, str) else ""
            linhas.append(f"| {r.competencia_processamento} | {r.municipios_com_producao} | {r.qtd_municipios} | "
                          f"{r.qtd_ignorados} | {r.qtd_total_tabnet} | {r.subgrupos_na_resposta} | {sinal} |")
        linhas.append("")
    t = sub.loc[sub["conjunto_cbo"] == TODOS].groupby("competencia_processamento")[
        ["total_tabnet_municipio", "total_soma_cbo", "producao_sem_cbo_na_tabela"]].sum()
    linhas += ["## Completude do CBO (todos os profissionais)", "",
               "Produção sem CBO na tabela = total sem filtro − soma das linhas da consulta por CBO.", "",
               "| Mês | Total | Soma por CBO | Sem CBO na tabela | Fração sem CBO |", "|---|---:|---:|---:|---:|"]
    for comp, r in t.iterrows():
        frac = r["producao_sem_cbo_na_tabela"] / r["total_tabnet_municipio"] if r["total_tabnet_municipio"] else float("nan")
        linhas.append(f"| {comp} | {int(r['total_tabnet_municipio'])} | {int(r['total_soma_cbo'])} | "
                      f"{int(r['producao_sem_cbo_na_tabela'])} | {frac:.6f} |")
    linhas.append("")
    linhas += ["## Subgrupos ao longo do tempo", "",
               "Meses em que o subgrupo é coluna da resposta (o TabNet omite coluna sem registro sob o filtro). "
               "O grupo 09 (Ofertas de Cuidados Integrados, OCI) fica fora de consultas (0301), exames (02) e "
               "cirurgias (04) na definição do protocolo 47.", "",
               "| Subgrupo | Rótulo | Primeiro mês (todos) | Último mês (todos) | Meses (todos) | Meses (alvo_pmme) | "
               "Qtd. total (todos) | Qtd. total (alvo_pmme) |",
               "|---|---|---|---|---:|---:|---:|---:|"]
    pres = sub[sub["presente_na_resposta"]]
    for s_, parte in pres.groupby("subgrupo", sort=True):
        t_ = parte[parte["conjunto_cbo"] == TODOS]
        a_ = parte[parte["conjunto_cbo"] == "alvo_pmme"]
        linhas.append(
            f"| {s_} | {parte['rotulo_subgrupo'].iloc[0]} | {t_['competencia_processamento'].min() if len(t_) else ''} | "
            f"{t_['competencia_processamento'].max() if len(t_) else ''} | {len(t_)} | {len(a_)} | "
            f"{int(t_['total_tabnet_municipio'].sum())} | {int(a_['total_tabnet_municipio'].sum())} |")
    linhas.append("")
    RESUMO_FILE.write_text("\n".join(linhas), encoding="utf-8")


# ---------------------------------------------------------------- verificação sem rede

def verificar() -> int:
    """Confere as saídas versionadas contra o manifesto, sem rede e sem gravar."""
    erros: list[str] = []
    if not MANIFESTO_FILE.exists():
        raise SystemExit(f"verificar: {_rel(MANIFESTO_FILE)} ausente; rode --etapa tudo")
    man = json.loads(MANIFESTO_FILE.read_text(encoding="utf-8"))
    for rel, info in (man.get("saidas") or {}).items():
        p = ROOT / rel
        if not p.exists():
            erros.append(f"saída ausente: {rel}")
        elif sha256_arquivo(p) != info.get("sha256"):
            erros.append(f"SHA-256 diferente do manifesto: {rel}")
    if PAINEL_FILE.exists():
        meta = pq.read_metadata(PAINEL_FILE)
        if meta.schema.to_arrow_schema().names != COLUNAS_PAINEL:
            erros.append("colunas do painel diferentes de COLUNAS_PAINEL")
        if meta.num_rows != (man.get("painel") or {}).get("linhas"):
            erros.append("linhas do painel diferentes do manifesto")
    if man.get("competencias_planejadas") != COMPETENCIAS:
        erros.append("plano de meses do script mudou desde a consolidação")
    obtidas = man.get("competencias_obtidas") or []
    if obtidas != COMPETENCIAS or any(c >= LIMITE_EXCLUSIVO for c in obtidas):
        erros.append("meses obtidos incoerentes com o plano ou >= limite do ciclo 3")
    for k, v in (man.get("validacoes") or {}).items():
        if v.get("status") not in ("APROVADO", "RELATO"):
            erros.append(f"validação {k} não aprovada: {v.get('status')}")
    for rel, reg in (man.get("entradas_locais") or {}).items():
        p = ROOT / rel
        if not p.exists() or sha256_arquivo(p) != reg.get("sha256"):
            erros.append(f"entrada mudou desde a consolidação: {rel}")
    # regra dos conjuntos: reaplicada às opções médicas do formulário guardadas na saída
    if CONJUNTOS_FILE.exists():
        cj = pd.read_csv(CONJUNTOS_FILE, dtype=str)
        medicos = sorted(cj.loc[cj["conjunto_cbo"] == "_opcao_medica_do_formulario", "co_cbo"])
        alvo, _, _ = a09.carregar_ponte()
        try:
            grupos = classificar_cbos(medicos, alvo)
            for c in CONJUNTOS_CBO:
                if grupos[c] != sorted(cj.loc[cj["conjunto_cbo"] == c, "co_cbo"]):
                    erros.append(f"conjunto {c} não reproduz a regra atual do a09")
        except ErroResposta as exc:
            erros.append(str(exc))
    if erros:
        for e in erros:
            log(f"VERIFICAÇÃO REPROVADA: {e}")
        raise SystemExit("verificar: saídas do a12 não conferem; refaça com --etapa consolidar ou --etapa tudo")
    log(f"SIA conferido sem rede: {(man.get('painel') or {}).get('linhas'):,} linhas de painel, "
        f"{len(obtidas)} meses, {len(man.get('saidas') or {})} saídas com SHA-256 do manifesto; nada gravado")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--etapa", choices=["verificar", "baixar", "consolidar", "tudo"], default="verificar",
                    help="verificar (padrão): confere as saídas versionadas sem rede e sem gravar; baixar: grava as "
                         "respostas brutas no cache (fora do Git); consolidar: valida o cache e grava as saídas; "
                         "tudo: baixar + consolidar")
    ap.add_argument("--competencias", nargs="*", help="subconjunto de meses para --etapa baixar (depuração ou refazer)")
    ap.add_argument("--refazer", action="store_true", help="com --etapa baixar: baixa de novo mesmo com cache válido")
    args = ap.parse_args()
    if args.etapa == "verificar":
        if args.competencias or args.refazer:
            raise SystemExit("--competencias e --refazer não se aplicam a --etapa verificar")
        return verificar()
    comps = sorted(args.competencias) if args.competencias else list(COMPETENCIAS)
    for c in comps:
        checar_limite(c)
        if c not in COMPETENCIAS:
            raise SystemExit(f"mês fora do plano: {c}")
    if args.etapa in ("baixar", "tudo"):
        codigo = etapa_baixar(comps, args.refazer)
        if args.etapa == "baixar" or codigo != 0:
            return codigo
    if args.competencias:
        raise SystemExit("a consolidação usa sempre o plano completo de meses (painel nunca parcial)")
    return consolidar(list(COMPETENCIAS))


if __name__ == "__main__":
    sys.exit(main())
