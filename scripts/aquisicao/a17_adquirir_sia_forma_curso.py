"""a17_adquirir_sia_forma_curso.py — SIA/SUS no TabNet: município × mês de processamento × forma de organização × curso.

Aquisição do adendo §12.2 do protocolo 47
(``docs/06_execucao/47_protocolo_producao_especializada.md``; T3.2 do plano 51):
produção ambulatorial aprovada por forma de organização, filtrada pelo conjunto de
CBO de cada curso da classe "específico" do portão G4. Só adquire, valida e
documenta: não lê IVS, não calcula nada por faixa, lado de corte, bolsa,
tratamento ou chegada e não estima nada. O outcome (formas típicas por 10 mil
habitantes) é montado depois, pela etapa de estimação.

Fonte: o mesmo formulário do a12, "Produção Ambulatorial do SUS - Brasil - por
local de atendimento" (``sia/cnv/qabr.def``), por HTTP. O que o a12 já faz não é
redigitado: este script carrega uma instância própria do módulo do a12 e usa dele
o formulário, a lista de municípios, as opções de CBO, o POST, o cache com
SHA-256, as tentativas com espera crescente, o leitor ``prn`` (com o padrão de
coluna trocado de subgrupo, 4 dígitos, para forma de organização, 6 dígitos), o
eco de período e filtros e a separação de "município ignorado".

Cursos e CBO: os cursos são os da classe ``ESPECIFICO`` de
``output/rdd_bolsa/G4_resumo.json``; as CBO de cada curso vêm da ponte curso–CBO
(``output/aquisicao/ponte_curso_cbo_oficial.json``) pela função
``carregar_ponte`` do script do G4, e têm de coincidir com as do G4. Cursos com o
mesmo conjunto de CBO (10 e 11) compartilham a consulta; o painel repete as linhas
para cada curso e diz isso no manifesto.

Consultas por mês de processamento (202201 a 202607; nenhum mês >= 202609):
- Linha = Município, Coluna = Forma organização, Incremento = Qtd.aprovada, filtro
  Profissional - CBO = CBO do conjunto, ``exibirlz``: uma por conjunto distinto;
- Linha = Profissional - CBO, Coluna = Forma organização, filtro = união das CBO dos
  cursos: total nacional por forma de cada conjunto, independente da municipal;
- no mês de conferência do a12 (202506): a consulta municipal filtrada também por
  UF (AC e RR), para a conferência célula a célula;
- diagnóstico (V8, acrescentado depois de ver a V5): Linha = Procedimento, filtro =
  união das CBO dos cursos, sem coluna e com Coluna = Forma organização.

Validações (fail closed nas obrigatórias):
- V1: em cada resposta, linha Total = soma das linhas e coluna Total = soma das células;
- V2: conjunto contido noutro (CBO dos cursos 10/11 dentro das do 7) tem produção
  menor ou igual em cada célula município × forma;
- V3: total nacional de cada conjunto por forma (linha Total da municipal) = soma das
  suas CBO na consulta por CBO; forma que não é coluna da municipal tem soma zero;
- V4: AC e RR célula a célula contra a consulta nacional;
- V5 (relato): soma das formas por subgrupo, nacional, contra a soma das CBO do
  conjunto na tabela nacional CBO × subgrupo do a12 (safra v1; nos meses
  202509–202607 também a safra v2 do a12b);
- V6 (relato): cobertura por mês e conjunto e presença das formas típicas do G4;
- V8 (relato, com coerência interna obrigatória): procedimentos que o TabNet deixa
  fora de toda tabela com Coluna = Forma (forma ausente da tabela de formas);
- V7: eco do período e dos filtros; nenhum mês >= 202609.

Zeros e ausências (regras do a12): ``-`` vira ``qtd_aprovada = 0`` com
``status = zero_tabnet``; município do formulário que não vem na resposta fica com
``qtd_aprovada`` nula e ``status = municipio_ausente_da_resposta``; forma que não é
coluna da resposta não gera linha (presença em ``sia_forma_curso_formas_por_consulta.csv``);
consulta que falha não gera linha e a consolidação para; "município ignorado" fica
em arquivo próprio.

Modos (``--etapa``): ``verificar`` (padrão, usado pelo ``run_all.py``) confere as
saídas versionadas contra o manifesto, sem rede e sem gravar; ``baixar`` só grava
respostas brutas no cache (fora do Git); ``consolidar`` lê o cache, valida e só
então grava; ``tudo`` faz as duas coisas.

Saídas (``output/aquisicao/sia_forma_curso/``):
- ``painel_sia_municipio_mes_forma_curso.parquet`` (co_ibge, competencia_processamento,
  cod_curso, forma, qtd_aprovada, status, natureza_dos_dados);
- ``sia_forma_curso_ignorados.parquet``, ``sia_forma_curso_nacional_cbo_forma.parquet``;
- ``sia_forma_curso_formas_por_consulta.csv``, ``sia_forma_curso_cobertura_mes.csv``,
  ``sia_forma_curso_cruzamento_a12.csv``, ``sia_forma_curso_cursos.csv``,
  ``sia_forma_curso_formas_tipicas.csv``, ``sia_forma_curso_procedimentos_fora_da_coluna_forma.csv``;
- ``manifesto_sia_forma_curso.json`` e ``a17_resumo.md``;
- ``brutos/`` (respostas brutas em gzip e metadados; fora do Git).
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import html
import importlib.util
import io
import json
import re
import shutil
import sys
import time
import urllib.error
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[2]
AQ_DIR = Path(__file__).resolve().parent
A12_FILE = AQ_DIR / "a12_adquirir_sia_tabnet.py"
G4_FILE = AQ_DIR / "g4_mapa_especialidade_procedimento.py"


def _carregar(nome: str, arquivo: Path):
    spec = importlib.util.spec_from_file_location(nome, arquivo)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Instância própria do a12 (não é a do run_all nem a dos testes do a12): só o cache e o padrão
# de coluna mudam. Tudo o mais (formulário, POST, cache, tentativas, leitor, eco) é o código do a12.
a12 = _carregar("a12_para_a17", A12_FILE)
g4 = _carregar("g4_para_a17", G4_FILE)

OUT_DIR = ROOT / "output" / "aquisicao" / "sia_forma_curso"
CACHE_DIR = OUT_DIR / "brutos"
a12.CACHE_DIR = CACHE_DIR
RE_FORMA = re.compile(r"^(\d{6}) (.*)$")
a12.RE_SUBGRUPO = RE_FORMA  # o leitor do a12 passa a exigir colunas de forma de organização (6 dígitos)

PAINEL_FILE = OUT_DIR / "painel_sia_municipio_mes_forma_curso.parquet"
IGNORADOS_FILE = OUT_DIR / "sia_forma_curso_ignorados.parquet"
CBO_FILE = OUT_DIR / "sia_forma_curso_nacional_cbo_forma.parquet"
FORMAS_FILE = OUT_DIR / "sia_forma_curso_formas_por_consulta.csv"
COBERTURA_FILE = OUT_DIR / "sia_forma_curso_cobertura_mes.csv"
CRUZAMENTO_FILE = OUT_DIR / "sia_forma_curso_cruzamento_a12.csv"
CURSOS_FILE = OUT_DIR / "sia_forma_curso_cursos.csv"
TIPICAS_FILE = OUT_DIR / "sia_forma_curso_formas_tipicas.csv"
PROC_FILE = OUT_DIR / "sia_forma_curso_procedimentos_fora_da_coluna_forma.csv"
MANIFESTO_FILE = OUT_DIR / "manifesto_sia_forma_curso.json"
RESUMO_FILE = OUT_DIR / "a17_resumo.md"

G4_RESUMO = ROOT / "output" / "rdd_bolsa" / "G4_resumo.json"
G4_MAPA = ROOT / "output" / "rdd_bolsa" / "G4_mapa_especialidade_procedimento.csv"
PONTE_FILE = g4.PONTE_FILE
A12_CBO_V1 = ROOT / "output" / "aquisicao" / "sia" / "sia_nacional_cbo_mes_subgrupo.parquet"
A12_CBO_V2 = ROOT / "output" / "aquisicao" / "sia_v2" / "sia_nacional_cbo_mes_subgrupo.parquet"

COMPETENCIAS = list(a12.COMPETENCIAS)  # 202201–202607, o plano do a12
LIMITE_EXCLUSIVO = a12.LIMITE_EXCLUSIVO  # "202609"
assert COMPETENCIAS[0] == "202201" and COMPETENCIAS[-1] == "202607" and len(COMPETENCIAS) == 55
assert all(c < LIMITE_EXCLUSIVO for c in COMPETENCIAS)
CLASSE = "ESPECIFICO"
COLUNA_FORMA = "Forma_organização"
MES_CONFERENCIA_UF = a12.MES_CONFERENCIA_UF  # 202506, fixado no a12
UFS_CONFERENCIA = dict(a12.UFS_CONFERENCIA)
PAUSA_ENTRE_CONSULTAS = a12.PAUSA_ENTRE_CONSULTAS
NATUREZA = "EMPIRICO"
STATUS_VALOR, STATUS_ZERO, STATUS_AUSENTE = a12.STATUS_VALOR, a12.STATUS_ZERO, a12.STATUS_AUSENTE
LIMIAR_QUEDA_MUNICIPIOS = a12.LIMIAR_QUEDA_MUNICIPIOS
LIMIAR_QUEDA_TOTAL = a12.LIMIAR_QUEDA_TOTAL

COLUNAS_PAINEL = ["co_ibge", "competencia_processamento", "cod_curso", "forma", "qtd_aprovada", "status",
                  "natureza_dos_dados"]
ESQUEMA_PAINEL = pa.schema([
    ("co_ibge", pa.dictionary(pa.int32(), pa.string())),
    ("competencia_processamento", pa.dictionary(pa.int8(), pa.string())),
    ("cod_curso", pa.int8()),
    ("forma", pa.dictionary(pa.int16(), pa.string())),
    ("qtd_aprovada", pa.int64()),
    ("status", pa.dictionary(pa.int8(), pa.string())),
    ("natureza_dos_dados", pa.dictionary(pa.int8(), pa.string())),
])

log = a12.log
ErroResposta = a12.ErroResposta


def _rel(p: Path) -> str:
    return a12._rel(p)


def checar_limite(comp: str) -> None:
    a12.checar_limite(comp)


# ---------------------------------------------------------------- cursos e conjuntos de CBO

def cursos_especificos() -> list[dict[str, Any]]:
    """Cursos da classe ESPECIFICO do G4, com as CBO da ponte (lidas pela função do G4)."""
    resumo = json.loads(G4_RESUMO.read_text(encoding="utf-8"))
    codigos = sorted(int(c) for c in resumo["classes_dos_cursos"][CLASSE])
    g4_por_curso = {int(c["cod_curso"]): c for c in resumo["por_curso"]}
    ponte, _ = g4.carregar_ponte()
    por_cod = {c["cod_curso"]: c for c in ponte}
    saida = []
    for k in codigos:
        if k not in por_cod:
            raise ErroResposta(f"curso {k} do G4 ausente da ponte")
        cbos = sorted(por_cod[k]["cbos"])
        if cbos != sorted(g4_por_curso[k]["cbos"]) or g4_por_curso[k]["classe_mapa_curso"] != CLASSE:
            raise ErroResposta(f"curso {k}: CBO ou classe da ponte diferente do G4")
        saida.append({"cod_curso": k, "no_curso": por_cod[k]["no_curso"], "cbos": cbos})
    if not saida:
        raise ErroResposta("nenhum curso ESPECIFICO no G4")
    return saida


def id_conjunto(cursos: list[int]) -> str:
    return "_".join(f"c{k:02d}" for k in sorted(cursos))


def conjuntos_dos_cursos(cursos: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Conjuntos distintos de CBO -> {'cbos': [...], 'cursos': [...]} (ordem pelo menor curso)."""
    por_cbos: dict[tuple[str, ...], list[int]] = {}
    for c in cursos:
        por_cbos.setdefault(tuple(c["cbos"]), []).append(c["cod_curso"])
    saida = {}
    for cbos, ks in sorted(por_cbos.items(), key=lambda x: min(x[1])):
        saida[id_conjunto(ks)] = {"cbos": list(cbos), "cursos": sorted(ks)}
    return saida


def opcoes_dos_conjuntos(form: dict[str, Any], conjuntos: dict[str, dict[str, Any]]) -> dict[str, list[dict[str, str]]]:
    por_codigo = {o["co_cbo"]: o for o in a12.opcoes_cbo(form)}
    saida = {}
    for s, info in conjuntos.items():
        faltam = [c for c in info["cbos"] if c not in por_codigo]
        if faltam:
            raise ErroResposta(f"CBO do conjunto {s} ausentes do formulário: {faltam}")
        saida[s] = sorted((por_codigo[c] for c in info["cbos"]), key=lambda o: int(o["indice"]))
    return saida


def contencoes(conjuntos: dict[str, dict[str, Any]]) -> list[tuple[str, str]]:
    """Pares (menor, maior) em que as CBO do primeiro conjunto estão contidas nas do segundo."""
    pares = []
    for a, ia in conjuntos.items():
        for b, ib in conjuntos.items():
            if a != b and set(ia["cbos"]) < set(ib["cbos"]):
                pares.append((a, b))
    return sorted(pares)


# ---------------------------------------------------------------- formulário e plano

def conferir_formulario_forma(form: dict[str, Any]) -> None:
    """Além do que o a12 confere: a forma de organização tem de ser oferecida como coluna."""
    erros = []
    if COLUNA_FORMA not in a12._valores(form, "Coluna"):
        erros.append(f"Coluna sem {COLUNA_FORMA}")
    if a12.LINHA_CBO not in a12._valores(form, "Linha"):
        erros.append(f"Linha sem {a12.LINHA_CBO}")
    if erros:
        raise ErroResposta("formulário: " + "; ".join(erros))


def _base(linha: str, comp: str) -> list[tuple[str, str]]:
    return [("Linha", linha), ("Coluna", COLUNA_FORMA), ("Incremento", a12.INCREMENTO),
            ("Arquivos", a12.arquivo_do_mes(comp))]


def planejar_consultas(form: dict[str, Any], competencias: list[str]) -> list[dict[str, Any]]:
    cursos = cursos_especificos()
    conjuntos = conjuntos_dos_cursos(cursos)
    op = opcoes_dos_conjuntos(form, conjuntos)
    uniao = sorted({o["co_cbo"]: o for s in op for o in op[s]}.values(), key=lambda o: int(o["indice"]))
    consultas = []
    for comp in competencias:
        checar_limite(comp)
        for s in conjuntos:
            filtros = [(a12.FILTRO_CBO, o["indice"]) for o in op[s]]
            consultas.append({"id": f"municipio_forma_{s}_{comp}", "tipo": "municipio", "competencia": comp,
                              "conjunto_cbo": s, "uf": None, "linha": a12.LINHA_MUNICIPIO,
                              "campos": _base(a12.LINHA_MUNICIPIO, comp) + filtros + a12._fim(True),
                              "eco_filtros": {a12.ROTULO_FILTRO_CBO: ", ".join(o["rotulo"] for o in op[s])}})
        consultas.append({"id": f"cbo_forma_uniao_{comp}", "tipo": "cbo", "competencia": comp,
                          "conjunto_cbo": "uniao_dos_cursos", "uf": None, "linha": a12.LINHA_CBO,
                          "campos": _base(a12.LINHA_CBO, comp) + [(a12.FILTRO_CBO, o["indice"]) for o in uniao]
                          + a12._fim(False),
                          "eco_filtros": {a12.ROTULO_FILTRO_CBO: ", ".join(o["rotulo"] for o in uniao)}})
        if comp == MES_CONFERENCIA_UF:
            for sigla, nome in UFS_CONFERENCIA.items():
                filtro_uf = [(a12.FILTRO_UF, a12.indice_uf(form, nome))]
                for s in conjuntos:
                    filtros = [(a12.FILTRO_CBO, o["indice"]) for o in op[s]]
                    consultas.append({"id": f"conferencia_forma_{sigla}_{s}_{comp}", "tipo": "conferencia_uf",
                                      "competencia": comp, "conjunto_cbo": s, "uf": sigla, "linha": a12.LINHA_MUNICIPIO,
                                      "campos": _base(a12.LINHA_MUNICIPIO, comp) + filtro_uf + filtros + a12._fim(True),
                                      "eco_filtros": {a12.ROTULO_FILTRO_UF: nome,
                                                      a12.ROTULO_FILTRO_CBO: ", ".join(o["rotulo"] for o in op[s])}})
    return consultas


def ler_resposta(raw: bytes) -> dict[str, Any]:
    """Leitor do a12 com colunas de forma; devolve também 'formas' (sinônimo de 'subgrupos')."""
    r = a12.ler_resposta(raw)
    r["formas"] = r["subgrupos"]
    return r


# ---------------------------------------------------------------- diagnóstico por procedimento (V8)
# Acrescentado depois de ver a V5 (diferença pequena e só no subgrupo 0301, a partir de 202501, frente ao a12):
# o TabNet deixa fora da tabela com Coluna = Forma os registros cuja forma não está na tabela de formas
# do formulário. Duas consultas por mês, Linha = Procedimento, filtradas pela união das CBO dos cursos,
# sem coluna e com Coluna = Forma, dizem quais procedimentos somem e quanto. É relato, não correção.

LINHA_PROCEDIMENTO = "Procedimento"
COLUNA_NAO_ATIVA = "--Não-Ativa--"
RE_PROCEDIMENTO = re.compile(r"^(\d{10}) (.*)$")


def _opcoes_uniao(form: dict[str, Any]) -> list[dict[str, str]]:
    op = opcoes_dos_conjuntos(form, conjuntos_dos_cursos(cursos_especificos()))
    return sorted({o["co_cbo"]: o for s in op for o in op[s]}.values(), key=lambda o: int(o["indice"]))


def planejar_diagnostico(form: dict[str, Any], competencias: list[str]) -> list[dict[str, Any]]:
    uniao = _opcoes_uniao(form)
    filtros = [(a12.FILTRO_CBO, o["indice"]) for o in uniao]
    eco = {a12.ROTULO_FILTRO_CBO: ", ".join(o["rotulo"] for o in uniao)}
    consultas = []
    for comp in competencias:
        checar_limite(comp)
        for sufixo, coluna in (("sem_coluna", COLUNA_NAO_ATIVA), ("forma", COLUNA_FORMA)):
            consultas.append({
                "id": f"diag_procedimento_{sufixo}_{comp}", "tipo": f"diag_procedimento_{sufixo}", "competencia": comp,
                "conjunto_cbo": "uniao_dos_cursos", "uf": None, "linha": LINHA_PROCEDIMENTO,
                "campos": [("Linha", LINHA_PROCEDIMENTO), ("Coluna", coluna), ("Incremento", a12.INCREMENTO),
                           ("Arquivos", a12.arquivo_do_mes(comp))] + filtros + a12._fim(False),
                "eco_filtros": eco})
    return consultas


def ler_resposta_procedimento(raw: bytes, consulta: dict[str, Any]) -> dict[str, Any]:
    """Tabela Linha = Procedimento (sem coluna ou com colunas de forma); confere período, filtro e somas."""
    txt = raw.decode("latin-1")
    if txt.count("<PRE>") != 1 or txt.count("</PRE>") != 1:
        raise ErroResposta("resposta sem bloco PRE único")
    ini, fim = txt.find("<PRE>"), txt.find("</PRE>")
    cab = html_unescape(txt[:ini + 5])
    h1 = cab.find("</H1>")
    filtros = {k.strip(): v.strip() for k, v in
               re.findall(r"<b>([^<]+?):</b>\s*(.*?)(?=<BR>|<PRE>)", cab[h1:], re.S | re.I)}
    periodo = next((v for k, v in filtros.items() if k.startswith("Per")), None)
    if periodo != a12.rotulo_do_mes(consulta["competencia"]):
        raise ErroResposta(f"eco: período {periodo!r}")
    if {k: v for k, v in filtros.items() if not k.startswith("Per")} != consulta["eco_filtros"]:
        raise ErroResposta("eco: filtros diferentes dos pedidos")
    linhas_txt = [ln for ln in txt[ini + 5:fim].strip("\r\n").splitlines() if ln.strip() not in ("", "&")]
    tabela = [[html_unescape(c).strip() for c in r] for r in csv.reader(io.StringIO("\n".join(linhas_txt)),
                                                                                delimiter=";", quotechar='"')]
    if len(tabela) < 2 or tabela[0][0] != LINHA_PROCEDIMENTO:
        raise ErroResposta("cabeçalho da consulta por procedimento inesperado")
    sem_coluna = consulta["tipo"].endswith("sem_coluna")
    if sem_coluna and tabela[0][1:] != [a12.INCREMENTO]:
        raise ErroResposta(f"cabeçalho {tabela[0]}")
    if not sem_coluna:
        if tabela[0][-1] != "Total" or not all(RE_FORMA.match(c) for c in tabela[0][1:-1]):
            raise ErroResposta("colunas de forma fora do padrão")
    linhas = []
    for r in tabela[1:]:
        if len(r) != len(tabela[0]):
            raise ErroResposta(f"linha com {len(r)} campos")
        vals = []
        for x in r[1:]:
            if x == "-":
                vals.append(0)
            elif re.fullmatch(r"[1-9]\d*", x):
                vals.append(int(x))
            else:
                raise ErroResposta(f"valor não reconhecido {x!r}")
        if not sem_coluna and sum(vals[:-1]) != vals[-1]:
            raise ErroResposta(f"linha {r[0]!r}: soma das colunas difere do Total")
        linhas.append((r[0], vals))
    if linhas[-1][0] != "Total":
        raise ErroResposta("última linha não é Total")
    corpo, total = linhas[:-1], linhas[-1][1]
    for j in range(len(total)):
        if sum(v[j] for _, v in corpo) != total[j]:
            raise ErroResposta("soma das linhas difere do Total")
    procs = {}
    for rot, v in corpo:
        m = RE_PROCEDIMENTO.match(rot)
        if not m:
            raise ErroResposta(f"procedimento fora do padrão: {rot!r}")
        procs[m.group(1)] = {"rotulo": m.group(2).strip(), "qtd": v[-1]}
    return {"procedimentos": procs, "total": total[-1],
            "total_por_forma": {} if sem_coluna else dict(zip([RE_FORMA.match(c).group(1) for c in tabela[0][1:-1]],
                                                             total[:-1]))}


def html_unescape(s: str) -> str:
    return html.unescape(s)


def baixar_diagnostico(q: dict[str, Any], refazer: bool = False) -> dict[str, Any]:
    """Como ``a12.baixar_consulta`` (cache, SHA-256, tentativas com espera crescente), com o leitor por procedimento."""
    cid = q["id"]
    checar_limite(q["competencia"])
    corpo = a12.corpo_post(q["campos"])
    if not refazer and a12.caminho_meta(cid).exists() and a12.caminho_bruto(cid).exists():
        meta = json.loads(a12.caminho_meta(cid).read_text(encoding="utf-8"))
        if meta.get("status") == "ok" and meta.get("corpo_post") == corpo:
            return meta
    falhas = []
    for tentativa in range(1, a12.TENTATIVAS + 1):
        quando = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        t0 = time.time()
        try:
            raw, status, ctype = a12._http(a12.URL_CONSULTA, corpo.encode("ascii"))
            ler_resposta_procedimento(raw, q)
            meta = {"id": cid, "tipo": q["tipo"], "competencia": q["competencia"], "conjunto_cbo": q["conjunto_cbo"],
                    "uf": None, "url": a12.URL_CONSULTA, "metodo": "POST",
                    "codificacao_corpo": "latin-1 (application/x-www-form-urlencoded)", "corpo_post": corpo,
                    "data_hora_utc": quando, "sha256_resposta": a12.sha256_bytes(raw), "bytes_resposta": len(raw),
                    "http_status": status, "content_type": ctype, "segundos": round(time.time() - t0, 1),
                    "tentativas": tentativa, "falhas_anteriores": falhas, "status": "ok",
                    "periodo_eco": a12.rotulo_do_mes(q["competencia"])}
            a12._gravar_cache(cid, raw, meta)
            return meta
        except (urllib.error.URLError, TimeoutError, ConnectionError, ErroResposta, OSError) as exc:
            falhas.append({"tentativa": tentativa, "data_hora_utc": quando, "segundos": round(time.time() - t0, 1),
                           "erro": f"{type(exc).__name__}: {exc}"[:500]})
            log(f"  {cid}: falha na tentativa {tentativa}: {falhas[-1]['erro'][:160]}")
            time.sleep(min(15 * 2 ** (tentativa - 1), 240))
    meta = {"id": cid, "tipo": q["tipo"], "competencia": q["competencia"], "conjunto_cbo": q["conjunto_cbo"],
            "uf": None, "url": a12.URL_CONSULTA, "metodo": "POST", "corpo_post": corpo, "status": "falha",
            "tentativas": a12.TENTATIVAS, "falhas_anteriores": falhas}
    a12.caminho_meta(cid).write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return meta


# ---------------------------------------------------------------- download

def etapa_baixar(competencias: list[str], refazer: bool) -> int:
    form = a12.baixar_formulario(refazer=refazer)
    conferir_formulario_forma(form)
    consultas = planejar_consultas(form, competencias) + planejar_diagnostico(form, competencias)
    log(f"{len(consultas)} consultas planejadas para {len(competencias)} meses")
    falhas = []
    t0 = time.time()
    for i, q in enumerate(consultas, 1):
        checar_limite(q["competencia"])
        em_cache = (not refazer and a12.caminho_meta(q["id"]).exists() and a12.caminho_bruto(q["id"]).exists()
                    and json.loads(a12.caminho_meta(q["id"]).read_text(encoding="utf-8")).get("status") == "ok"
                    and json.loads(a12.caminho_meta(q["id"]).read_text(encoding="utf-8")).get("corpo_post")
                    == a12.corpo_post(q["campos"]))
        if q["tipo"].startswith("diag_procedimento"):
            meta = baixar_diagnostico(q, refazer=refazer)
        else:
            meta = a12.baixar_consulta(q, refazer=refazer)
        if meta["status"] != "ok":
            falhas.append(q["id"])
        if i % 8 == 0 or meta["status"] != "ok":
            log(f"{i}/{len(consultas)} {q['id']}: {meta['status']} ({time.time() - t0:.0f}s decorridos)")
        if not em_cache:
            time.sleep(PAUSA_ENTRE_CONSULTAS)
    log(f"download terminado: {len(consultas) - len(falhas)} ok, {len(falhas)} com falha; rode --etapa consolidar")
    for f in falhas:
        log(f"  FALHA {f}")
    return 0 if not falhas else 3


# ---------------------------------------------------------------- consolidação

def _tabela_painel(comp: str, cod_curso: int, codigos: list[str], mm: dict[str, Any]) -> pa.Table:
    nmun, nf = mm["valores"].shape
    if mm["fora_da_referencia"]:
        raise ErroResposta(f"{comp}: município fora da lista do formulário {mm['fora_da_referencia'][:3]}")
    co = np.repeat(np.array(codigos, dtype=object), nf)
    presente = np.repeat(mm["presente"], nf)
    q = mm["valores"].reshape(-1)
    z = mm["zero"].reshape(-1)
    status = np.where(~presente, STATUS_AUSENTE, np.where(z, STATUS_ZERO, STATUS_VALOR))
    if ((q > 0) != (status == STATUS_VALOR)).any() or ((status == STATUS_ZERO) & (q != 0)).any():
        raise ErroResposta(f"curso {cod_curso} {comp}: status incoerente com a quantidade")
    formas = np.tile(np.array(mm["subgrupos"], dtype=object), nmun)
    n = len(q)
    tabela = pa.table({
        "co_ibge": pa.array(co, pa.string()).dictionary_encode(),
        "competencia_processamento": pa.array([comp] * n, pa.string()).dictionary_encode(),
        "cod_curso": pa.array(np.full(n, cod_curso, dtype=np.int8)),
        "forma": pa.array(formas, pa.string()).dictionary_encode(),
        "qtd_aprovada": pa.array(q, type=pa.int64(), mask=~presente),
        "status": pa.array(status.astype(object), pa.string()).dictionary_encode(),
        "natureza_dos_dados": pa.array([NATUREZA] * n, pa.string()).dictionary_encode(),
    })
    return tabela.cast(ESQUEMA_PAINEL)


def _cbo_nacional_a12(path: Path, comp: str, cbos: list[str]) -> dict[str, int] | None:
    """Soma das CBO do conjunto por subgrupo na tabela nacional CBO × subgrupo do a12 (None se o mês não está lá)."""
    if not path.exists():
        return None
    t = pd.read_parquet(path, columns=["co_cbo", "competencia_processamento", "subgrupo", "qtd_aprovada"],
                        filters=[("competencia_processamento", "=", comp)])
    if t.empty:
        return None
    t = t.loc[t["co_cbo"].astype(str).isin(cbos)]
    return {str(k): int(v) for k, v in t.groupby("subgrupo")["qtd_aprovada"].sum().items()}


def consolidar(competencias: list[str]) -> int:
    t_ini = time.time()
    form = a12.carregar_formulario()
    conferir_formulario_forma(form)
    meta_form = json.loads(a12.caminho_meta(a12.FORMULARIO_ID).read_text(encoding="utf-8"))
    cursos = cursos_especificos()
    conjuntos = conjuntos_dos_cursos(cursos)
    op = opcoes_dos_conjuntos(form, conjuntos)
    pares_contidos = contencoes(conjuntos)
    municipios, sigla_para_codigo = a12.municipios_do_formulario(form)
    referencia = [m["co_ibge"] for m in municipios]
    consultas = planejar_consultas(form, competencias)
    diag = {q["id"]: q for q in planejar_diagnostico(form, competencias)}
    formas_do_formulario = {m.group(1) for _, t in form["selects"].get("SForma_organização", [])
                            if (m := RE_FORMA.match(t))}
    tipicas = pd.read_csv(G4_MAPA, dtype={"co_forma": str, "co_subgrupo": str})
    tipicas = tipicas.loc[tipicas["tipica"].astype(bool) & tipicas["cod_curso"].isin([c["cod_curso"] for c in cursos]),
                          ["cod_curso", "co_forma", "no_forma", "participacao_na_producao_do_curso",
                           "classe_especificidade"]]

    metas, faltam = {}, []
    for q in consultas + list(diag.values()):
        p = a12.caminho_meta(q["id"])
        meta = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"status": "nao_baixada"}
        metas[q["id"]] = meta
        if (meta.get("status") != "ok" or not a12.caminho_bruto(q["id"]).exists()
                or meta.get("corpo_post") != a12.corpo_post(q["campos"])):
            faltam.append({"id": q["id"], "status": meta.get("status")})
    if faltam:
        log(f"FAIL CLOSED: {len(faltam)} consultas sem resposta válida em cache; nada gravado em output/")
        for f in faltam[:20]:
            log(f"  {f['id']}: {f['status']}")
        return 2

    erros: list[str] = []
    tmp_painel = CACHE_DIR / "painel_forma_curso.parquet.tmp"
    escritor = pq.ParquetWriter(tmp_painel, ESQUEMA_PAINEL, compression="zstd", compression_level=9,
                                use_dictionary=True)
    linhas_painel = 0
    ign_reg, cbo_reg, formas_reg, cob_reg, cruz_reg, proc_reg, diag_mes = [], [], [], [], [], [], []
    rotulos_forma: dict[str, set[str]] = {}
    ausentes_reg: dict[str, int] = {}
    val_somas, val_cont, val_cbo, val_aus_cbo, val_conf = [], [], [], [], []
    try:
        for comp in competencias:
            resp = {}
            for q in consultas:
                if q["competencia"] != comp:
                    continue
                r = ler_resposta(a12.ler_bruto(q["id"]))
                a12.conferir_eco(r, q)
                s_ = a12.somas_conferem(r)
                val_somas.append({"id": q["id"], **s_})
                if not s_["ok"]:
                    erros.append(f"{q['id']}: total da resposta não é a soma das linhas")
                for cod, rot in r["formas"]:
                    rotulos_forma.setdefault(cod, set()).add(rot)
                resp[q["id"]] = r

            mats = {}
            for s in conjuntos:
                r = resp[f"municipio_forma_{s}_{comp}"]
                mm = a12.matriz_municipios(r, referencia)
                mats[s] = mm
                n_aus = int((~mm["presente"]).sum())
                if n_aus:
                    ausentes_reg[f"{s}_{comp}"] = n_aus
                for k in conjuntos[s]["cursos"]:
                    tabela = _tabela_painel(comp, k, referencia, mm)
                    escritor.write_table(tabela)
                    linhas_painel += tabela.num_rows
                for ig in mm["ignorados"]:
                    for f_, v, z in zip(mm["subgrupos"], ig["valores"], ig["zeros"]):
                        ign_reg.append({"rotulo_tabnet": ig["rotulo_tabnet"], "tipo_ignorado": ig["tipo"],
                                        "sigla_uf": ig["sigla_uf"], "competencia_processamento": comp,
                                        "conjunto_cbo": s, "forma": f_, "qtd_aprovada": v,
                                        "status": STATUS_ZERO if z else STATUS_VALOR})
                cob_reg.append({
                    "competencia_processamento": comp, "conjunto_cbo": s,
                    "cursos": "|".join(str(k) for k in conjuntos[s]["cursos"]),
                    "municipios_na_resposta": int(mm["presente"].sum()),
                    "municipios_ausentes_da_resposta": n_aus,
                    "municipios_com_producao": int((mm["valores"].sum(axis=1) > 0).sum()),
                    "qtd_municipios": int(mm["valores"].sum()),
                    "qtd_ignorados": int(sum(sum(ig["valores"]) for ig in mm["ignorados"])),
                    "qtd_total_tabnet": int(r["total"][-1]),
                    "formas_na_resposta": len(mm["subgrupos"]),
                })

            # V2: conjunto contido noutro tem produção <= célula a célula (município × forma)
            for a, b in pares_contidos:
                fa, fb = mats[a]["subgrupos"], mats[b]["subgrupos"]
                ok = True
                for j, f_ in enumerate(fa):
                    col_a = mats[a]["valores"][:, j]
                    col_b = mats[b]["valores"][:, fb.index(f_)] if f_ in fb else np.zeros_like(col_a)
                    if (col_a > col_b).any():
                        ok = False
                        break
                val_cont.append({"competencia": comp, "contido": a, "contem": b, "ok": ok})
                if not ok:
                    erros.append(f"{comp}: {a} maior que {b} em alguma célula")

            # V3: total nacional de cada conjunto por forma = soma das suas CBO na consulta por CBO
            r_cbo = resp[f"cbo_forma_uniao_{comp}"]
            formas_cbo = [f_ for f_, _ in r_cbo["formas"]]
            por_cbo = {}
            uniao = {c for s in conjuntos for c in conjuntos[s]["cbos"]}
            for rotulo, vals, zs in r_cbo["linhas"]:
                cod = a12._cbo_da_linha(rotulo)
                if cod not in uniao:
                    erros.append(f"{comp}: CBO {cod} fora do filtro na consulta por CBO")
                    continue
                por_cbo[cod] = vals[:-1]
                for f_, v, z in zip(formas_cbo, vals[:-1], zs[:-1]):
                    cbo_reg.append({"co_cbo": cod, "rotulo_tabnet": rotulo, "competencia_processamento": comp,
                                    "forma": f_, "qtd_aprovada": v, "status": STATUS_ZERO if z else STATUS_VALOR})
            for s in conjuntos:
                r_m = resp[f"municipio_forma_{s}_{comp}"]
                tot_m = dict(zip([f_ for f_, _ in r_m["formas"]], r_m["total"][:-1]))
                cbos = set(conjuntos[s]["cbos"])
                soma = {f_: sum(v[j] for k, v in por_cbo.items() if k in cbos) for j, f_ in enumerate(formas_cbo)}
                for f_ in sorted(set(tot_m) | {x for x, v in soma.items() if v}):
                    presente = f_ in tot_m
                    ok = tot_m.get(f_, 0) == soma.get(f_, 0)
                    val_cbo.append({"competencia": comp, "conjunto_cbo": s, "forma": f_, "ok": bool(ok)})
                    if not ok:
                        erros.append(f"{comp} {s} {f_}: total municipal {tot_m.get(f_)} != soma das CBO {soma.get(f_, 0)}")
                    if not presente:
                        val_aus_cbo.append({"competencia": comp, "conjunto_cbo": s, "forma": f_, "soma_cbo": soma.get(f_, 0)})
                    formas_reg.append({
                        "competencia_processamento": comp, "conjunto_cbo": s,
                        "cursos": "|".join(str(k) for k in conjuntos[s]["cursos"]), "forma": f_,
                        "presente_na_resposta": presente,
                        "total_tabnet_municipio": int(tot_m[f_]) if presente else None,
                        "total_soma_cbo": int(soma.get(f_, 0)),
                    })

                # V5 (relato): formas somadas por subgrupo contra a tabela nacional CBO × subgrupo do a12
                sub_a17: dict[str, int] = {}
                for f_, v in tot_m.items():
                    sub_a17[f_[:4]] = sub_a17.get(f_[:4], 0) + int(v)
                ref = {"v1": _cbo_nacional_a12(A12_CBO_V1, comp, sorted(cbos)),
                       "v2": _cbo_nacional_a12(A12_CBO_V2, comp, sorted(cbos))}
                for sg in sorted(set(sub_a17) | set((ref["v1"] or {})) | set((ref["v2"] or {}))):
                    a = sub_a17.get(sg, 0)
                    v1 = (ref["v1"] or {}).get(sg, 0) if ref["v1"] is not None else None
                    v2 = (ref["v2"] or {}).get(sg, 0) if ref["v2"] is not None else None
                    if a == 0 and not v1 and not v2:
                        continue
                    cruz_reg.append({"competencia_processamento": comp, "conjunto_cbo": s, "subgrupo": sg,
                                     "qtd_a17": a, "qtd_a12_v1": v1, "qtd_a12_v2": v2,
                                     "igual_a12_v1": (a == v1) if v1 is not None else None,
                                     "igual_a12_v2": (a == v2) if v2 is not None else None})

            # V8 (relato; coerência interna obrigatória): procedimentos que somem com Coluna = Forma
            q0, q1 = diag[f"diag_procedimento_sem_coluna_{comp}"], diag[f"diag_procedimento_forma_{comp}"]
            d0 = ler_resposta_procedimento(a12.ler_bruto(q0["id"]), q0)
            d1 = ler_resposta_procedimento(a12.ler_bruto(q1["id"]), q1)
            tot_uniao = {f_: int(v) for f_, v in zip(formas_cbo, r_cbo["total"][:-1]) if v}
            if {f_: v for f_, v in d1["total_por_forma"].items() if v} != tot_uniao:
                erros.append(f"{comp}: consulta por procedimento com Coluna = Forma difere da consulta por CBO")
            if set(d1["procedimentos"]) - set(d0["procedimentos"]):
                erros.append(f"{comp}: procedimento com forma ausente da consulta sem coluna")
            soma_fora = 0
            for cod, info in sorted(d0["procedimentos"].items()):
                q_forma = d1["procedimentos"].get(cod, {}).get("qtd", 0)
                if q_forma == info["qtd"]:
                    continue
                if q_forma > info["qtd"]:
                    erros.append(f"{comp}: procedimento {cod} maior com Coluna = Forma")
                soma_fora += info["qtd"] - q_forma
                proc_reg.append({"competencia_processamento": comp, "co_procedimento": cod,
                                 "rotulo_procedimento": info["rotulo"], "subgrupo": cod[:4], "forma_do_codigo": cod[:6],
                                 "forma_do_codigo_no_formulario": cod[:6] in formas_do_formulario,
                                 "qtd_sem_coluna": info["qtd"], "qtd_com_coluna_forma": q_forma})
            if d0["total"] - d1["total"] != soma_fora:
                erros.append(f"{comp}: diferença dos Totais por procedimento não é a soma dos procedimentos que somem")
            diag_mes.append({"competencia_processamento": comp, "qtd_uniao_sem_coluna": d0["total"],
                             "qtd_uniao_com_coluna_forma": d1["total"], "qtd_fora_da_coluna_forma": soma_fora})

            # V4: conferência célula a célula das UF pequenas
            if comp == MES_CONFERENCIA_UF:
                for sigla in UFS_CONFERENCIA:
                    cod_uf = sigla_para_codigo[sigla]
                    for s in conjuntos:
                        r_f = resp[f"conferencia_forma_{sigla}_{s}_{comp}"]
                        nac = mats[s]
                        formas_f = [f_ for f_, _ in r_f["formas"]]
                        problemas, vistos = [], set()
                        for rotulo, vals, zs in r_f["linhas"]:
                            tipo, chave = a12._classificar_linha_municipio(rotulo)
                            if tipo == "municipio":
                                if chave[:2] != cod_uf:
                                    if sum(vals) != 0:
                                        problemas.append(f"município de outra UF com produção: {chave}")
                                    continue
                                i = referencia.index(chave)
                                vistos.add(chave)
                                for f_, v in zip(formas_f, vals[:-1]):
                                    if f_ not in nac["subgrupos"]:
                                        problemas.append(f"{chave} {f_}: forma ausente da consulta nacional")
                                    elif nac["valores"][i, nac["subgrupos"].index(f_)] != v:
                                        problemas.append(f"{chave} {f_}: {v} != nacional")
                            elif tipo == "ignorado_uf" and chave == sigla:
                                ig = next((x for x in nac["ignorados"] if x["sigla_uf"] == sigla), None)
                                for f_, v in zip(formas_f, vals[:-1]):
                                    nv = ig["valores"][nac["subgrupos"].index(f_)] if ig and f_ in nac["subgrupos"] else 0
                                    if nv != v:
                                        problemas.append(f"ignorado {sigla} {f_}: {v} != nacional")
                            elif sum(vals) != 0:
                                problemas.append(f"linha inesperada com produção: {rotulo}")
                        esperados = {m for m in referencia if m[:2] == cod_uf}
                        if vistos != esperados:
                            problemas.append(f"municípios da UF: {len(vistos)} na filtrada, {len(esperados)} esperados")
                        idx_uf = [referencia.index(m) for m in sorted(esperados)]
                        for j, f_ in enumerate(nac["subgrupos"]):
                            if f_ not in formas_f and nac["valores"][idx_uf, j].sum() != 0:
                                problemas.append(f"forma {f_} ausente na filtrada mas com produção na nacional")
                        val_conf.append({"uf": sigla, "conjunto_cbo": s, "competencia": comp,
                                         "municipios": len(vistos), "celulas_comparadas": len(vistos) * len(formas_f),
                                         "qtd_total": int(r_f["total"][-1]), "problemas": problemas[:20],
                                         "ok": not problemas})
                        if problemas:
                            erros.append(f"conferência {sigla} {s}: {problemas[:3]}")
            log(f"{comp}: consolidado ({linhas_painel:,} linhas de painel até aqui)")
    except ErroResposta as exc:
        escritor.close()
        tmp_painel.unlink(missing_ok=True)
        log(f"FAIL CLOSED: resposta em cache fora da forma esperada ({exc}); nada gravado em output/")
        return 2
    finally:
        if escritor.is_open:
            escritor.close()

    aus_com_prod = [x for x in val_aus_cbo if x["soma_cbo"] != 0]
    cob = pd.DataFrame(cob_reg)
    cob["sinal_queda"] = sinalizar_quedas(cob)
    cob["natureza_dos_dados"] = NATUREZA
    cruz = pd.DataFrame(cruz_reg)
    cruz["natureza_dos_dados"] = NATUREZA
    cruz_mes = (cruz.assign(dif_v1=cruz["igual_a12_v1"].eq(False), dif_v2=cruz["igual_a12_v2"].eq(False),
                            tem_v2=cruz["qtd_a12_v2"].notna())
                .groupby(["competencia_processamento", "conjunto_cbo"])
                .agg(dif_v1=("dif_v1", "any"), dif_v2=("dif_v2", "any"), tem_v2=("tem_v2", "any")).reset_index())
    cruz_mes["situacao"] = np.where(~cruz_mes["dif_v1"], "igual_a12_v1",
                                    np.where(cruz_mes["tem_v2"] & ~cruz_mes["dif_v2"], "igual_a12_v2_revisado_na_v1",
                                             "diferente_das_safras_do_a12"))
    tip_reg = presenca_tipicas(tipicas, pd.DataFrame(formas_reg), conjuntos)
    proc = pd.DataFrame(proc_reg, columns=["competencia_processamento", "co_procedimento", "rotulo_procedimento",
                                           "subgrupo", "forma_do_codigo", "forma_do_codigo_no_formulario",
                                           "qtd_sem_coluna", "qtd_com_coluna_forma"])
    proc["natureza_dos_dados"] = NATUREZA
    # Diferença frente ao a12 (V5) cabe no que some com Coluna = Forma (V8)? Só onde a v2 não confirma revisão.
    fora = proc.assign(q=proc["qtd_sem_coluna"] - proc["qtd_com_coluna_forma"]).groupby(
        ["competencia_processamento", "subgrupo"])["q"].sum().to_dict()
    nao_explicadas = []
    for r in cruz.itertuples(index=False):
        if r.igual_a12_v1 == False and not (r.igual_a12_v2 == True):  # noqa: E712 (bool do numpy ou None)
            falta = int(r.qtd_a12_v1) - int(r.qtd_a17)
            if not (0 < falta <= fora.get((r.competencia_processamento, r.subgrupo), 0)):
                nao_explicadas.append({"competencia_processamento": r.competencia_processamento,
                                       "conjunto_cbo": r.conjunto_cbo, "subgrupo": r.subgrupo,
                                       "qtd_a17": int(r.qtd_a17), "qtd_a12_v1": int(r.qtd_a12_v1)})

    validacoes = {
        "V1_total_igual_soma_das_linhas": {
            "descricao": "em cada resposta, linha Total = soma das linhas (municípios + ignorados) por coluna, e coluna Total = soma das células por linha",
            "respostas": len(val_somas), "respostas_com_falha": [v["id"] for v in val_somas if not v["ok"]],
            "status": "APROVADO" if all(v["ok"] for v in val_somas) else "REPROVADO"},
        "V2_conjunto_contido_le_conjunto_maior": {
            "descricao": "conjunto de CBO contido noutro tem quantidade menor ou igual em cada célula município × forma × mês",
            "pares": [list(p) for p in pares_contidos], "comparacoes": len(val_cont),
            "falhas": [v for v in val_cont if not v["ok"]],
            "status": "APROVADO" if all(v["ok"] for v in val_cont) else ("NAO_APLICAVEL" if not val_cont else "REPROVADO")},
        "V3_nacional_por_forma_contra_consulta_por_cbo": {
            "descricao": "total nacional de cada conjunto por forma (linha Total da consulta municipal) igual à soma das suas CBO na consulta Linha = Profissional - CBO, Coluna = Forma organização, filtrada pela união das CBO dos cursos; forma ausente da municipal tem soma zero",
            "celulas_comparadas": len(val_cbo), "celulas_com_diferenca": [v for v in val_cbo if not v["ok"]][:50],
            "formas_ausentes_da_resposta_do_conjunto": len(val_aus_cbo),
            "formas_ausentes_com_producao_nas_cbo_do_conjunto": aus_com_prod[:50],
            "status": "APROVADO" if all(v["ok"] for v in val_cbo) and not aus_com_prod else "REPROVADO"},
        "V4_conferencia_uf_celula_a_celula": {
            "descricao": f"consultas filtradas por UF ({', '.join(UFS_CONFERENCIA)}) em {MES_CONFERENCIA_UF}, cada conjunto: cada célula igual à da consulta nacional; mesmos municípios; forma ausente na filtrada é zero na nacional",
            "resultados": val_conf,
            "status": "APROVADO" if val_conf and all(v["ok"] for v in val_conf) else
                      ("NAO_EXECUTADA" if not val_conf else "REPROVADO")},
        "V5_cruzamento_com_a12_por_subgrupo": {
            "descricao": "relato: soma nacional das formas por subgrupo (prefixo de 4 dígitos) contra a soma das CBO do conjunto na tabela nacional CBO × subgrupo do a12 (safra v1, 55 meses; safra v2 do a12b em 202509–202607). Diferença em mês que a safra v2 confirma é revisão da fonte, não erro de aquisição",
            "por_situacao": {k: int(v) for k, v in cruz_mes["situacao"].value_counts().sort_index().items()},
            "meses_conjunto_diferentes_das_safras_do_a12": cruz_mes.loc[cruz_mes["situacao"] == "diferente_das_safras_do_a12",
                                                                    ["competencia_processamento", "conjunto_cbo"]].to_dict(orient="records"),
            "meses_iguais_a_v2_e_diferentes_da_v1": sorted(cruz_mes.loc[cruz_mes["situacao"] == "igual_a12_v2_revisado_na_v1",
                                                                        "competencia_processamento"].unique().tolist()),
            "safra_v2_do_a12_disponivel": A12_CBO_V2.exists(),
            "diferencas_nao_explicadas_pela_V8": nao_explicadas[:50],
            "n_diferencas_nao_explicadas_pela_V8": len(nao_explicadas),
            "nota": "diferença explicada = o a17 tem menos que o a12 no subgrupo, e a falta cabe na produção da união das CBO dos cursos que some com Coluna = Forma no mesmo mês e subgrupo (V8)",
            "status": "RELATO"},
        "V6_cobertura_e_formas_tipicas": {
            "descricao": f"relato: meses com municípios com produção < {LIMIAR_QUEDA_MUNICIPIOS:.0%} da mediana do conjunto ou quantidade < {LIMIAR_QUEDA_TOTAL:.0%} da mediana (limiares do a12); presença das formas típicas do G4 como coluna; nada é corrigido",
            "meses_sinalizados": cob.loc[cob["sinal_queda"] != "", ["competencia_processamento", "conjunto_cbo", "sinal_queda"]].to_dict(orient="records"),
            "municipios_ausentes_da_resposta": ausentes_reg,
            "formas_tipicas_sem_coluna_em_algum_mes": tip_reg.loc[tip_reg["meses_presente"] < len(competencias),
                                                                  ["cod_curso", "co_forma", "meses_presente"]].to_dict(orient="records"),
            "status": "RELATO"},
        "V7_eco_e_limites": {
            "descricao": "período e filtros repetidos pelo TabNet iguais aos pedidos em todas as respostas; nenhum mês >= 202609 nem > 202607",
            "status": "APROVADO" if all(c < LIMITE_EXCLUSIVO and c <= a12.ULTIMA_COMPETENCIA for c in competencias) else "REPROVADO"},
        "V8_procedimentos_fora_da_coluna_forma": {
            "descricao": "relato (diagnóstico acrescentado depois de ver a V5): por mês, consulta Linha = Procedimento filtrada pela união das CBO dos cursos, sem coluna e com Coluna = Forma organização; procedimentos cuja quantidade diminui com a coluna de forma ficam fora de toda tabela por forma. Coerência interna obrigatória: totais por forma iguais aos da consulta por CBO, nenhum procedimento só na tabela com forma, diferença dos Totais = soma dos que somem",
            "por_mes": diag_mes,
            "meses_com_producao_fora": [d["competencia_processamento"] for d in diag_mes if d["qtd_fora_da_coluna_forma"]],
            "procedimentos_fora": sorted(proc["co_procedimento"].unique().tolist()),
            "formas_dos_procedimentos_fora_ausentes_do_formulario": sorted(
                proc.loc[~proc["forma_do_codigo_no_formulario"].astype(bool), "forma_do_codigo"].unique().tolist()),
            "qtd_total_fora": int(sum(d["qtd_fora_da_coluna_forma"] for d in diag_mes)),
            "qtd_total_uniao_sem_coluna": int(sum(d["qtd_uniao_sem_coluna"] for d in diag_mes)),
            "status": "RELATO"},
    }
    obrigatorias = [k for k, v in validacoes.items() if v["status"] not in ("APROVADO", "RELATO", "NAO_APLICAVEL")]
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

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.move(str(tmp_painel), PAINEL_FILE)
    _gravar_parquet(pd.DataFrame(ign_reg), IGNORADOS_FILE,
                    ["rotulo_tabnet", "tipo_ignorado", "sigla_uf", "competencia_processamento", "conjunto_cbo",
                     "forma", "qtd_aprovada", "status"])
    _gravar_parquet(pd.DataFrame(cbo_reg), CBO_FILE,
                    ["co_cbo", "rotulo_tabnet", "competencia_processamento", "forma", "qtd_aprovada", "status"])
    fdf = pd.DataFrame(formas_reg)
    fdf["rotulo_forma"] = fdf["forma"].map(lambda f_: " | ".join(sorted(rotulos_forma.get(f_, {""}))))
    for col in ("total_tabnet_municipio", "total_soma_cbo"):
        fdf[col] = fdf[col].astype("Int64")
    fdf["natureza_dos_dados"] = NATUREZA
    fdf.to_csv(FORMAS_FILE, index=False, lineterminator="\n")
    cob.to_csv(COBERTURA_FILE, index=False, lineterminator="\n")
    for col in ("qtd_a12_v1", "qtd_a12_v2"):
        cruz[col] = cruz[col].astype("Int64")
    for col in ("igual_a12_v1", "igual_a12_v2"):
        cruz[col] = cruz[col].astype("boolean")
    cruz.to_csv(CRUZAMENTO_FILE, index=False, lineterminator="\n")
    cdf = pd.DataFrame([{"cod_curso": c["cod_curso"], "no_curso": c["no_curso"], "cbos": "|".join(c["cbos"]),
                         "conjunto_cbo": next(s for s, i in conjuntos.items() if c["cod_curso"] in i["cursos"]),
                         "classe_g4": CLASSE,
                         "rotulos_tabnet_cbo": " | ".join(o["rotulo"] for o in op[next(
                             s for s, i in conjuntos.items() if c["cod_curso"] in i["cursos"])]),
                         "natureza_dos_dados": NATUREZA} for c in cursos])
    cdf.to_csv(CURSOS_FILE, index=False, lineterminator="\n")
    tip_reg.to_csv(TIPICAS_FILE, index=False, lineterminator="\n")
    proc.to_csv(PROC_FILE, index=False, lineterminator="\n")
    gravar_manifesto(competencias, consultas + list(diag.values()), metas, meta_form, cursos, conjuntos, op, validacoes, linhas_painel,
                     len(referencia), round(time.time() - t_ini, 1))
    gravar_resumo()
    log(f"Painel: {linhas_painel:,} linhas, {PAINEL_FILE.stat().st_size / 1024**2:.1f} MB; manifesto e resumo gravados")
    return 0


def presenca_tipicas(tipicas: pd.DataFrame, formas: pd.DataFrame, conjuntos: dict[str, dict[str, Any]]) -> pd.DataFrame:
    """Para cada curso e forma típica do G4: meses em que a forma é coluna da resposta e quantidade nacional."""
    reg = []
    for r in tipicas.itertuples(index=False):
        s = next(k for k, i in conjuntos.items() if r.cod_curso in i["cursos"])
        f = formas.loc[(formas["conjunto_cbo"] == s) & (formas["forma"] == r.co_forma)]
        pres = f.loc[f["presente_na_resposta"]]
        reg.append({"cod_curso": int(r.cod_curso), "conjunto_cbo": s, "co_forma": r.co_forma, "no_forma": r.no_forma,
                    "participacao_g4_2024": r.participacao_na_producao_do_curso,
                    "classe_especificidade_g4": r.classe_especificidade,
                    "meses_presente": int(pres["competencia_processamento"].nunique()),
                    "primeiro_mes_presente": pres["competencia_processamento"].min() if len(pres) else None,
                    "ultimo_mes_presente": pres["competencia_processamento"].max() if len(pres) else None,
                    "qtd_nacional_202201_202607": int(pres["total_tabnet_municipio"].sum()) if len(pres) else 0,
                    "natureza_dos_dados": NATUREZA})
    return pd.DataFrame(reg)


def sinalizar_quedas(cob: pd.DataFrame) -> pd.Series:
    """Regra do a12 (só relato), contra a mediana do próprio conjunto."""
    return a12.sinalizar_quedas(cob)


def _gravar_parquet(df: pd.DataFrame, path: Path, colunas: list[str]) -> None:
    df = df[colunas].copy()
    df["qtd_aprovada"] = df["qtd_aprovada"].astype("int64")
    df["natureza_dos_dados"] = NATUREZA
    df.to_parquet(path, index=False, compression="zstd")


# ---------------------------------------------------------------- manifesto e resumo

def saidas() -> tuple[Path, ...]:
    return (PAINEL_FILE, IGNORADOS_FILE, CBO_FILE, FORMAS_FILE, COBERTURA_FILE, CRUZAMENTO_FILE, CURSOS_FILE,
            TIPICAS_FILE, PROC_FILE)


def entradas_locais() -> dict[str, dict[str, Any]]:
    ent = {
        _rel(G4_RESUMO): {"uso": "cursos da classe ESPECIFICO e suas CBO (conferidas contra a ponte)"},
        _rel(G4_MAPA): {"uso": "formas típicas de cada curso (só relato de presença, V6)"},
        _rel(PONTE_FILE): {"uso": "CBO de cada curso (g4.carregar_ponte)"},
        _rel(A12_CBO_V1): {"uso": "cruzamento por subgrupo com o a12, safra v1 (V5, relato)"},
        _rel(A12_FILE): {"uso": "código importado: formulário, POST, cache, leitor, eco e regras de status"},
        _rel(G4_FILE): {"uso": "código importado: carregar_ponte"},
    }
    if A12_CBO_V2.exists():
        ent[_rel(A12_CBO_V2)] = {"uso": "cruzamento por subgrupo com o a12, safra v2 do a12b (V5, relato)"}
    for rel in ent:
        ent[rel]["sha256"] = a12.sha256_arquivo(ROOT / rel)
    return ent


def _info_saida(p: Path) -> dict[str, Any]:
    return a12._info_saida(p)


def gravar_manifesto(competencias, consultas, metas, meta_form, cursos, conjuntos, op, validacoes, linhas_painel,
                     n_ref, segundos) -> None:
    reg = []
    for q in consultas:
        m = metas[q["id"]]
        reg.append({**{k: m.get(k) for k in (
            "id", "tipo", "competencia", "conjunto_cbo", "uf", "url", "metodo", "corpo_post", "data_hora_utc",
            "sha256_resposta", "bytes_resposta", "http_status", "segundos", "tentativas", "falhas_anteriores",
            "status", "periodo_eco")}, **{k: q[k] for k in ("id", "tipo", "competencia", "conjunto_cbo", "uf")}})
    datas = sorted(m["data_hora_utc"] for m in metas.values() if m.get("data_hora_utc"))
    manifesto = {
        "gerador": "scripts/aquisicao/a17_adquirir_sia_forma_curso.py",
        "protocolo": "docs/06_execucao/47_protocolo_producao_especializada.md (adendo §12.2; T3.2 do plano 51)",
        "estatuto": "PROTOCOLO_47_ADENDO_12_POS_RESULTADO",
        "natureza_dos_dados": NATUREZA,
        "data_execucao": dt.date.today().isoformat(),
        "fonte": {
            "nome": "SIA/SUS — Produção Ambulatorial do SUS - Brasil - por local de atendimento (TabNet, DATASUS/MS)",
            "url_formulario": a12.URL_FORMULARIO, "url_consulta": a12.URL_CONSULTA,
            "formulario": {k: meta_form.get(k) for k in ("data_hora_utc", "sha256_resposta", "bytes_resposta")},
            "nota_https": "o TabNet só respondeu por HTTP neste ambiente; HTTPS falha",
            "nota_tabnet": "rodapé do TabNet: dados dos últimos seis meses sujeitos a atualização; a revisão observada no SIH alcançou 11 meses (A15 §5)",
        },
        "unidade": "quantidade aprovada (Qtd.aprovada) de procedimentos ambulatoriais",
        "chaves": {
            "co_ibge": "município do local de atendimento (estabelecimento), 6 dígitos do TabNet",
            "competencia_processamento": "mês de processamento (arquivo qabrAAMM.dbf), não o mês de atendimento",
            "cod_curso": "curso do PMM-E (código da ponte), classe ESPECIFICO do G4",
            "forma": "forma de organização SIGTAP do procedimento (6 dígitos)",
        },
        "filtros_e_opcoes": {
            "Linha": [a12.LINHA_MUNICIPIO, a12.LINHA_CBO, LINHA_PROCEDIMENTO + " (só no diagnóstico V8)"],
            "Coluna": [COLUNA_FORMA, COLUNA_NAO_ATIVA + " (só no diagnóstico V8)"], "Incremento": a12.INCREMENTO,
            "formato": "prn", "zeradas": "exibirlz na consulta municipal (municípios zerados aparecem; colunas sem registro não); a consulta por CBO vai sem exibirlz",
            "filtro_cbo": a12.FILTRO_CBO, "filtro_uf": f"{a12.FILTRO_UF} (só na conferência {', '.join(UFS_CONFERENCIA)})",
            "nenhum_outro_filtro": "sem filtro de financiamento, documento, complexidade, gestão ou prestador",
        },
        "competencias_planejadas": COMPETENCIAS,
        "competencias_obtidas": competencias,
        "limite_ciclo3": f"nenhum mês >= {LIMITE_EXCLUSIVO} é pedido ou lido; o SIA vai até {a12.ULTIMA_COMPETENCIA} (protocolo 47, §6)",
        "cursos": {
            "regra": "classe ESPECIFICO de output/rdd_bolsa/G4_resumo.json; CBO da ponte curso–CBO lidas por g4.carregar_ponte e conferidas contra o G4",
            "lista": cursos,
            "conjuntos_de_cbo": {s: {**i, "rotulos_tabnet": [o["rotulo"] for o in op[s]],
                                     "indices_formulario": [o["indice"] for o in op[s]]} for s, i in conjuntos.items()},
            "cursos_com_o_mesmo_conjunto": {s: i["cursos"] for s, i in conjuntos.items() if len(i["cursos"]) > 1},
            "nota": "cursos com o mesmo conjunto de CBO compartilham a consulta; o painel repete as linhas para cada um. A CBO é mais larga que o curso (G4 §3): o painel mede a produção da CBO, não o conteúdo do curso",
        },
        "regras_de_status": {
            STATUS_VALOR: "valor positivo devolvido pelo TabNet",
            STATUS_ZERO: "'-' no TabNet: dado numérico igual a 0 não resultante de arredondamento (legenda do TabNet); qtd_aprovada = 0",
            STATUS_AUSENTE: "município da lista do formulário que não veio na resposta; qtd_aprovada nula",
            "forma_sem_linha": "forma que não é coluna da resposta não tem linha no painel (o TabNet omite colunas sem registro sob o filtro); a presença por consulta está em sia_forma_curso_formas_por_consulta.csv e a V3 confere que a soma das CBO do conjunto é zero nessas formas",
            "consulta_com_falha": "não gera linhas: a consolidação para (fail closed) e nada é gravado",
            "municipio_ignorado": "linhas 'MUNICIPIO IGNORADO - UF' e '000000 Ignorado ou exterior' ficam só em sia_forma_curso_ignorados.parquet",
            "procedimento_fora_da_coluna_forma": "com Coluna = Forma, o TabNet descarta os registros cuja forma não está na sua tabela de formas (V8); essa produção não está no painel nem em nenhum Total por forma. Ela não é zero nem ausente: fica fora da dimensão. A quantidade, pela união das CBO dos cursos, está em sia_forma_curso_procedimentos_fora_da_coluna_forma.csv",
        },
        "municipios_do_formulario": n_ref,
        "conferencia_uf": {"mes": MES_CONFERENCIA_UF, "ufs": UFS_CONFERENCIA},
        "validacoes": validacoes,
        "consultas": {
            "n": len(reg), "primeira_utc": datas[0] if datas else None, "ultima_utc": datas[-1] if datas else None,
            "segundos_de_resposta_somados": round(sum(m.get("segundos") or 0 for m in metas.values()), 1),
            "com_mais_de_uma_tentativa": [q["id"] for q in reg if (q.get("tentativas") or 1) > 1],
            "lista": reg,
        },
        "segundos_consolidacao": segundos,
        "entradas_locais": entradas_locais(),
        "saidas": {_rel(p): _info_saida(p) for p in saidas()},
        "painel": {"arquivo": _rel(PAINEL_FILE), "linhas": linhas_painel, "colunas": COLUNAS_PAINEL,
                   "cursos": [c["cod_curso"] for c in cursos]},
        "cache_bruto": {"diretorio": _rel(CACHE_DIR), "git": "ignorado (.gitignore)",
                        "formato": "<id>.html.gz (resposta bruta, gzip) e <id>.json (metadado); SHA-256 da resposta sem compressão"},
        "cegamento": "nenhum IVS lido; nada por faixa, lado de corte, bolsa, tratamento ou chegada",
    }
    MANIFESTO_FILE.write_text(json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def gravar_resumo() -> None:
    man = json.loads(MANIFESTO_FILE.read_text(encoding="utf-8"))
    cob = pd.read_csv(COBERTURA_FILE, dtype={"competencia_processamento": str})
    tip = pd.read_csv(TIPICAS_FILE, dtype={"co_forma": str})
    cruz = pd.read_csv(CRUZAMENTO_FILE, dtype={"competencia_processamento": str, "subgrupo": str})
    v = man["validacoes"]
    linhas = [
        "# A17 — resumo gerado do SIA/SUS por forma de organização × curso (TabNet)", "",
        f"Gerado por `scripts/aquisicao/a17_adquirir_sia_forma_curso.py` em {man['data_execucao']}. Não editar à mão. "
        "Natureza dos dados: EMPIRICO. Só totais nacionais e contagens; nada por faixa, lado de corte, IVS ou chegada.", "",
        "## Aquisição", "",
        f"- Meses de processamento: {len(man['competencias_obtidas'])} "
        f"({man['competencias_obtidas'][0]} a {man['competencias_obtidas'][-1]}).",
        f"- Consultas: {man['consultas']['n']}, entre {man['consultas']['primeira_utc']} e {man['consultas']['ultima_utc']} "
        f"(UTC); com mais de uma tentativa: {len(man['consultas']['com_mais_de_uma_tentativa'])}.",
        f"- Municípios na lista do formulário: {man['municipios_do_formulario']}.",
        f"- Linhas do painel: {man['painel']['linhas']}.", "",
        "## Cursos e conjuntos de CBO", "", "| Conjunto | Cursos | CBO |", "|---|---|---|",
    ]
    for s, i in man["cursos"]["conjuntos_de_cbo"].items():
        linhas.append(f"| {s} | {', '.join(str(k) for k in i['cursos'])} | {', '.join(i['rotulos_tabnet'])} |")
    linhas += ["", "## Validações", "", "| Validação | Status |", "|---|---|"]
    for k, x in v.items():
        linhas.append(f"| {k} | {x['status']} |")
    linhas += ["", "## Cruzamento com o a12 por subgrupo (V5, relato)", "",
               "Situação de cada mês × conjunto: igual à safra v1 do a12; igual à safra v2 (a12b) e diferente da v1 "
               "(revisão da fonte); ou diferente das duas.", "",
               "| Situação | Meses × conjuntos |", "|---|---:|"]
    for k, n in v["V5_cruzamento_com_a12_por_subgrupo"]["por_situacao"].items():
        linhas.append(f"| {k} | {n} |")
    linhas += ["", "Diferenças frente ao a12 sem explicação pelos procedimentos fora da coluna de forma (V8): "
               f"{v['V5_cruzamento_com_a12_por_subgrupo']['n_diferencas_nao_explicadas_pela_V8']}."]
    dif = cruz.loc[cruz["igual_a12_v1"].astype(str) == "False"]
    if len(dif):
        g = dif.groupby("competencia_processamento").agg(conjuntos=("conjunto_cbo", "nunique"),
                                                        subgrupos=("subgrupo", "nunique"),
                                                        qtd_a17=("qtd_a17", "sum"), qtd_a12_v1=("qtd_a12_v1", "sum"))
        linhas += ["", "Meses com diferença frente à safra v1 do a12 (soma das células diferentes):", "",
                   "| Mês | Conjuntos | Subgrupos | Qtd a17 | Qtd a12 v1 |", "|---|---:|---:|---:|---:|"]
        for comp, r in g.iterrows():
            linhas.append(f"| {comp} | {r['conjuntos']} | {r['subgrupos']} | {int(r['qtd_a17'])} | {int(r['qtd_a12_v1'])} |")
    v8 = v["V8_procedimentos_fora_da_coluna_forma"]
    linhas += ["", "## Procedimentos fora da coluna de forma (V8, relato)", "",
               "União das CBO dos cursos. Produção que o TabNet descarta com Coluna = Forma organização.", "",
               f"- Procedimentos: {', '.join(v8['procedimentos_fora']) or 'nenhum'}.",
               f"- Formas desses procedimentos ausentes da lista de formas do formulário: "
               f"{', '.join(v8['formas_dos_procedimentos_fora_ausentes_do_formulario']) or 'nenhuma'}.",
               f"- Quantidade fora: {v8['qtd_total_fora']} de {v8['qtd_total_uniao_sem_coluna']} "
               "(202201–202607).", "",
               "| Mês | Qtd. união sem coluna | Qtd. união com coluna de forma | Fora |", "|---|---:|---:|---:|"]
    for d in v8["por_mes"]:
        if d["qtd_fora_da_coluna_forma"]:
            linhas.append(f"| {d['competencia_processamento']} | {d['qtd_uniao_sem_coluna']} | "
                          f"{d['qtd_uniao_com_coluna_forma']} | {d['qtd_fora_da_coluna_forma']} |")
    linhas += ["", "## Formas típicas do G4 (presença como coluna)", "",
               "| Curso | Forma | Participação no curso (G4, 2024) | Especificidade (G4) | Meses presente | Qtd. nacional 202201–202607 |",
               "|---|---|---:|---|---:|---:|"]
    for r in tip.itertuples(index=False):
        linhas.append(f"| {r.cod_curso} | {r.co_forma} {r.no_forma} | {r.participacao_g4_2024:.3f} | "
                      f"{r.classe_especificidade_g4} | {r.meses_presente} | {r.qtd_nacional_202201_202607} |")
    linhas += ["", "## Cobertura por mês e conjunto", "",
               "Municípios com produção = municípios com quantidade aprovada > 0 em alguma forma.", ""]
    for s, parte in cob.groupby("conjunto_cbo", sort=False):
        linhas += [f"### {s}", "", "| Mês | Municípios com produção | Qtd. municípios | Qtd. ignorados | Total TabNet | Formas | Sinal |",
                   "|---|---:|---:|---:|---:|---:|---|"]
        for r in parte.itertuples(index=False):
            sinal = r.sinal_queda if isinstance(r.sinal_queda, str) else ""
            linhas.append(f"| {r.competencia_processamento} | {r.municipios_com_producao} | {r.qtd_municipios} | "
                          f"{r.qtd_ignorados} | {r.qtd_total_tabnet} | {r.formas_na_resposta} | {sinal} |")
        linhas.append("")
    RESUMO_FILE.write_text("\n".join(linhas), encoding="utf-8")


# ---------------------------------------------------------------- verificação sem rede

def verificar() -> int:
    erros: list[str] = []
    if not MANIFESTO_FILE.exists():
        raise SystemExit(f"verificar: {_rel(MANIFESTO_FILE)} ausente; rode --etapa tudo")
    man = json.loads(MANIFESTO_FILE.read_text(encoding="utf-8"))
    for rel, info in (man.get("saidas") or {}).items():
        p = ROOT / rel
        if not p.exists():
            erros.append(f"saída ausente: {rel}")
        elif a12.sha256_arquivo(p) != info.get("sha256"):
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
        if v.get("status") not in ("APROVADO", "RELATO", "NAO_APLICAVEL"):
            erros.append(f"validação {k} não aprovada: {v.get('status')}")
    for rel, reg in (man.get("entradas_locais") or {}).items():
        p = ROOT / rel
        if not p.exists() or a12.sha256_arquivo(p) != reg.get("sha256"):
            erros.append(f"entrada mudou desde a consolidação: {rel}")
    try:
        cursos = cursos_especificos()
        if [c["cod_curso"] for c in cursos] != (man.get("painel") or {}).get("cursos"):
            erros.append("cursos ESPECIFICO do G4 diferentes dos do painel")
    except ErroResposta as exc:
        erros.append(str(exc))
    if erros:
        for e in erros:
            log(f"VERIFICAÇÃO REPROVADA: {e}")
        raise SystemExit("verificar: saídas do a17 não conferem; refaça com --etapa consolidar ou --etapa tudo")
    log(f"SIA por forma × curso conferido sem rede: {(man.get('painel') or {}).get('linhas'):,} linhas de painel, "
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
