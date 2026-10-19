"""a15_adquirir_sih_residencia.py — SIH/SUS no TabNet: AIH por município de RESIDÊNCIA × mês × grupo.

Portão G3 do plano das perguntas reformuladas
(``docs/06_execucao/51_plano_perguntas_reformuladas.md``, P3, T3.4): adquirir a
SIH por local de residência do paciente, com as mesmas regras do a13
(``scripts/aquisicao/a13_adquirir_sih_tabnet.py``). É só aquisição e
verificação de viabilidade; nenhum contraste é calculado.

Fonte: TabNet/DATASUS, "Procedimentos hospitalares do SUS - por local de
residência - Brasil" (``sih/cnv/qrbr.def``), só por HTTP. O formulário
(``deftohtm.exe``) é baixado e lido; os nomes dos campos e os valores das
opções (Linha, Coluna, Incremento, Arquivos e filtros S*) saem dele, e não são
digitados. As consultas são POSTs a ``tabcgi.exe`` em latin-1, com
``formato=prn``, ``zeradas=exibirlz`` e ``mostre=Mostra``.

Unidade de tempo: o arquivo mensal ``qrbrAAMM.dbf`` do campo "Arquivos", que é o
**mês de processamento** da AIH (o mesmo conceito do a13). Cada arquivo é
conferido contra a linha "Ano/mês processamento" da própria fonte.

Lugar: município de **residência** do paciente (Linha = "Município" deste
formulário). As AIH são as mesmas do a13; muda só a linha. Por isso o total
nacional de cada mês e grupo tem de ser igual ao do SIH por local de internação
(``sih/cnv/qibr.def``, o formulário do a13) consultado na mesma execução
(validação v8), e igual ao total versionado do a13 nos meses que a fonte não
revisou depois da extração do a13 (comparação v9).

Consultas, uma por arquivo mensal (202201 a 202607; nada >= 202609 é pedido),
as mesmas do a13 mais uma de conferência:
- ``mun_grupo_aih``, ``mun_grupo_internacoes``, ``mun_grupo_valor``: município de
  residência × grupo do procedimento principal, com os incrementos AIH
  aprovadas, Internações e Valor total;
- ``uf_grupo_aih``: UF de residência × grupo (conferência);
- ``procmes_grupo_aih``: ano/mês de processamento × grupo (conceito de tempo e
  total nacional);
- ``mun_carater_g04_aih``: município de residência × caráter do atendimento, só
  grupo 04;
- ``mun_grupo_aih_uf_AC`` e ``mun_grupo_aih_uf_RR``: a mesma tabela municipal
  filtrada pela UF de residência, para a conferência célula a célula;
- ``int_uf_grupo_aih``: UF **de internação** × grupo, no formulário ``qibr.def``
  (o do a13), na mesma execução: total nacional contemporâneo (v8) e detecção
  de UF-mês sem arquivo de internação.

Regras de integridade (fail closed): ``-`` do TabNet é zero (legenda da própria
página). Ausência por UF-mês tem duas origens, ambas NaN com motivo, nunca zero:
(a) UF de residência com total zero no mês (a regra do a13);
(b) UF cujo arquivo de **internação** falta no mês: total zero da UF na consulta
``int_uf_grupo_aih``. Os residentes dessa UF internados em outra UF ainda
aparecem, mas o grosso das internações (as da própria UF) falta; o número
observado seria parcial e fica fora do painel (o total parcial da UF vai só para
as validações). Nas demais UFs do mesmo mês, os residentes internados na UF sem
arquivo (ou com arquivo atípico) faltam: a coluna ``mes_com_falta_em_outra_uf``
marca esse alerta, sem mudar o valor. "Município ignorado" de cada UF e
"Ignorado ou exterior" ficam numa tabela própria. Qualquer consulta ausente,
resposta fora do formato ou conferência obrigatória reprovada impede a gravação
das saídas canônicas.

Cegamento: este script não lê IVS, faixa da bolsa, lado de corte ou tratamento.
O universo de municípios é a lista do próprio formulário do TabNet. Do a13 lê
só as validações e os painéis versionados (comparação v9).

Modos (``--etapa``): ``verificar`` (padrão, usado pelo ``run_all.py``) só confere
os painéis versionados contra o manifesto, sem rede e sem gravar; ``baixar``
busca os formulários e as respostas para o cache (fora do controle de versão);
``consolidar`` monta, valida e grava as saídas a partir do cache, sem rede;
``tudo`` faz os dois.

Saídas (``output/aquisicao/sih_residencia/``):
- ``painel_sih_residencia_municipio_mes_grupo.parquet``;
- ``painel_sih_residencia_municipio_mes_carater_g04.parquet``;
- ``ignorados_sih_residencia_uf_mes_grupo.parquet``;
- ``a15_validacoes.json``, ``a15_resumo.md``, ``manifesto_sih_residencia.json``;
- ``cache_tabnet/`` (respostas brutas e metadados; fora do controle de versão).
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import html
import json
import re
import sys
import time
import unicodedata
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
OUT_DIR = ROOT / "output" / "aquisicao" / "sih_residencia"
CACHE_DIR = OUT_DIR / "cache_tabnet"
PAINEL_FILE = OUT_DIR / "painel_sih_residencia_municipio_mes_grupo.parquet"
CARATER_FILE = OUT_DIR / "painel_sih_residencia_municipio_mes_carater_g04.parquet"
IGNORADOS_FILE = OUT_DIR / "ignorados_sih_residencia_uf_mes_grupo.parquet"
VALIDACOES_FILE = OUT_DIR / "a15_validacoes.json"
RESUMO_FILE = OUT_DIR / "a15_resumo.md"
MANIFESTO_FILE = OUT_DIR / "manifesto_sih_residencia.json"

# Saídas versionadas do a13 (SIH por local de internação): a mesma base de AIH.
A13_DIR = ROOT / "output" / "aquisicao" / "sih"
A13_VALIDACOES = A13_DIR / "a13_validacoes.json"
A13_PAINEL = A13_DIR / "painel_sih_municipio_mes_grupo.parquet"
A13_IGNORADOS = A13_DIR / "ignorados_sih_uf_mes_grupo.parquet"

TABNET = "http://tabnet.datasus.gov.br/cgi"
FONTES: dict[str, dict[str, Any]] = {
    # formulário principal: local de residência
    "qrbr": {"url_form": f"{TABNET}/deftohtm.exe?sih/cnv/qrbr.def", "url_tab": f"{TABNET}/tabcgi.exe?sih/cnv/qrbr.def",
             "form_file": CACHE_DIR / "formulario_qrbr.html", "form_meta": CACHE_DIR / "formulario_qrbr.json",
             "nome": "Procedimentos hospitalares do SUS - por local de residência - Brasil"},
    # formulário do a13 (local de internação): só a consulta de conferência int_uf_grupo_aih
    "qibr": {"url_form": f"{TABNET}/deftohtm.exe?sih/cnv/qibr.def", "url_tab": f"{TABNET}/tabcgi.exe?sih/cnv/qibr.def",
             "form_file": CACHE_DIR / "formulario_qibr.html", "form_meta": CACHE_DIR / "formulario_qibr.json",
             "nome": "Procedimentos hospitalares do SUS - por local de internação - Brasil"},
}
URL_FORM = FONTES["qrbr"]["url_form"]
URL_TAB = FONTES["qrbr"]["url_tab"]
FORM_FILE = FONTES["qrbr"]["form_file"]
FORM_META = FONTES["qrbr"]["form_meta"]
ENCODING = "latin-1"

# Protocolo 47, §6, e plano 51, §2: SIA e SIH lidos até 202607; ciclo 3: nada >= 202609.
LIMITE_EXCLUSIVO = "202609"
COMPETENCIA_INICIAL = "202201"
COMPETENCIA_FINAL = "202607"


def _meses(ini: str, fim: str) -> list[str]:
    a, m = int(ini[:4]), int(ini[4:])
    saida = []
    while f"{a}{m:02d}" <= fim:
        saida.append(f"{a}{m:02d}")
        a, m = (a + 1, 1) if m == 12 else (a, m + 1)
    return saida


COMPETENCIAS = _meses(COMPETENCIA_INICIAL, COMPETENCIA_FINAL)
assert all(c < LIMITE_EXCLUSIVO for c in COMPETENCIAS)

MESES_PT = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
MESES_LONGOS = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro",
                "Outubro", "Novembro", "Dezembro"]

# IBGE: código numérico de cada UF (tabela oficial de UFs; constante, não dado observado).
# Conferida contra as próprias respostas: o "MUNICIPIO IGNORADO - XX" de cada UF
# precede os municípios com o prefixo correspondente.
UF_SIGLA_CODIGO = {
    "RO": "11", "AC": "12", "AM": "13", "RR": "14", "PA": "15", "AP": "16", "TO": "17",
    "MA": "21", "PI": "22", "CE": "23", "RN": "24", "PB": "25", "PE": "26", "AL": "27",
    "SE": "28", "BA": "29", "MG": "31", "ES": "32", "RJ": "33", "SP": "35", "PR": "41",
    "SC": "42", "RS": "43", "MS": "50", "MT": "51", "GO": "52", "DF": "53",
}
UF_CODIGO_SIGLA = {v: k for k, v in UF_SIGLA_CODIGO.items()}

# Rótulos do formulário (a resolução para os VALUEs é feita no formulário baixado).
# Em qrbr.def a linha "Município" é o município de residência (título da página).
LINHA = {"municipio": "Município", "uf": "UF", "procmes": "Ano/mês processamento"}
COLUNA = {"grupo": "Grupo procedimento", "carater": "Caráter atendimento"}
INCREMENTO = {"aih": "AIH aprovadas", "internacoes": "Internações", "valor": "Valor total"}
GRUPO_CIRURGICO_ROTULO = "04 Procedimentos cirurgicos"

# Consulta -> (fonte, linha, coluna, incremento, filtros {select: rótulo da opção}).
CONSULTAS: dict[str, dict[str, Any]] = {
    "mun_grupo_aih": {"fonte": "qrbr", "linha": "municipio", "coluna": "grupo", "incremento": "aih", "filtros": {}},
    "mun_grupo_internacoes": {"fonte": "qrbr", "linha": "municipio", "coluna": "grupo", "incremento": "internacoes",
                              "filtros": {}},
    "mun_grupo_valor": {"fonte": "qrbr", "linha": "municipio", "coluna": "grupo", "incremento": "valor", "filtros": {}},
    "uf_grupo_aih": {"fonte": "qrbr", "linha": "uf", "coluna": "grupo", "incremento": "aih", "filtros": {}},
    "procmes_grupo_aih": {"fonte": "qrbr", "linha": "procmes", "coluna": "grupo", "incremento": "aih", "filtros": {}},
    "mun_carater_g04_aih": {"fonte": "qrbr", "linha": "municipio", "coluna": "carater", "incremento": "aih",
                            "filtros": {"SGrupo_procedimento": GRUPO_CIRURGICO_ROTULO}},
    "mun_grupo_aih_uf_AC": {"fonte": "qrbr", "linha": "municipio", "coluna": "grupo", "incremento": "aih",
                            "filtros": {"SUF": "12 Acre"}},
    "mun_grupo_aih_uf_RR": {"fonte": "qrbr", "linha": "municipio", "coluna": "grupo", "incremento": "aih",
                            "filtros": {"SUF": "14 Roraima"}},
    "int_uf_grupo_aih": {"fonte": "qibr", "linha": "uf", "coluna": "grupo", "incremento": "aih", "filtros": {}},
}
UFS_CONFERENCIA_CELULA = {"mun_grupo_aih_uf_AC": "12", "mun_grupo_aih_uf_RR": "14"}

# Regra de UF-mês atípico (alerta, não altera valor), a mesma do a13: total de AIH
# da UF **de internação** no mês abaixo desta fração da mediana mensal da UF no
# período. Lida da consulta contemporânea por local de internação, porque o que
# falha é o arquivo do processamento da UF onde a internação ocorreu.
FRACAO_ATIPICO = 0.5
PAUSA_ENTRE_CONSULTAS = 0.5  # segundos, por cortesia com o servidor

STATUS = {
    "observado": "valor positivo devolvido pelo TabNet",
    "zero_tabnet": "o TabNet devolveu '-' (zero não resultante de arredondamento, pela legenda da página)",
    "zero_coluna_omitida": (
        "o grupo não aparece como coluna no mês (o TabNet omite coluna com total nacional zero); "
        "zero só porque o Total de cada linha confere com a soma das colunas devolvidas"
    ),
    "ausente_uf_mes_sem_dado": (
        "a UF de residência tem total zero no mês; valor ausente (NaN), nunca zero"
    ),
    "ausente_uf_internacao_sem_dado": (
        "o arquivo de internação da própria UF falta no processamento publicado do mês (total zero da UF na "
        "consulta contemporânea por local de internação); só aparecem residentes internados em outra UF, "
        "o número seria parcial: valor ausente (NaN), nunca zero nem parcial"
    ),
}
STATUS_AUSENTES = ("ausente_uf_mes_sem_dado", "ausente_uf_internacao_sem_dado")
COLUNAS_PAINEL = [
    "co_ibge", "uf", "competencia", "grupo", "aih_aprovadas", "internacoes", "valor_total",
    "status", "uf_mes_atipico", "mes_com_falta_em_outra_uf", "natureza_dos_dados",
]
COLUNAS_CARATER = [
    "co_ibge", "uf", "competencia", "grupo", "carater", "aih_aprovadas", "status",
    "uf_mes_atipico", "mes_com_falta_em_outra_uf", "natureza_dos_dados",
]
COLUNAS_IGNORADOS = [
    "linha_tabnet", "uf", "competencia", "grupo", "aih_aprovadas", "internacoes", "valor_total",
    "status", "natureza_dos_dados",
]


def log(msg: str) -> None:
    print(f"[{dt.datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_arquivo(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def checar_limite(comp: str) -> None:
    if comp >= LIMITE_EXCLUSIVO:
        raise RuntimeError(f"Competência {comp} >= {LIMITE_EXCLUSIVO} é vedada (ciclo 3).")
    if comp > COMPETENCIA_FINAL:
        raise RuntimeError(f"Competência {comp} > {COMPETENCIA_FINAL}: o plano lê SIH até {COMPETENCIA_FINAL}.")


def rotulo_mes(comp: str) -> str:
    """'202607' -> 'Jul/2026' (rótulo do campo Arquivos e do 'Período')."""
    return f"{MESES_PT[int(comp[4:]) - 1]}/{comp[:4]}"


def rotulo_procmes(comp: str) -> str:
    """'202607' -> 'Julho/2026' (rótulo da linha mensal de 'Ano/mês processamento', sem o recuo)."""
    return f"{MESES_LONGOS[int(comp[4:]) - 1]}/{comp[:4]}"


def slug(texto: str) -> str:
    s = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")


# ---------------------------------------------------------------- formulário

def ler_formulario(texto: str, fonte: str = "qrbr") -> dict[str, list[dict[str, Any]]]:
    """Devolve, para cada SELECT do formulário, as opções (valor, rótulo, selecionada)."""
    selects: dict[str, list[dict[str, Any]]] = {}
    for m in re.finditer(r"<SELECT([^>]*)>(.*?)</SELECT>", texto, re.S | re.I):
        nome = re.search(r'NAME="([^"]*)"', m.group(1), re.I)
        if not nome:
            continue
        opcoes = []
        for o in re.finditer(r"<OPTION([^>]*)>([^<\r\n]*)", m.group(2), re.I):
            valor = re.search(r'VALUE="([^"]*)"', o.group(1), re.I)
            if not valor:
                continue
            opcoes.append({
                "valor": valor.group(1),
                "rotulo": html.unescape(o.group(2)).strip(),
                "selecionada": bool(re.search(r"\bSELECTED\b", o.group(1), re.I)),
            })
        selects[nome.group(1)] = opcoes
    if not selects:
        raise RuntimeError("formulário sem SELECT: resposta inesperada do TabNet")
    if not re.search(rf'ACTION="/cgi/tabcgi\.exe\?sih/cnv/{fonte}\.def"', texto, re.I):
        raise RuntimeError(f"formulário não aponta para tabcgi.exe?sih/cnv/{fonte}.def")
    return selects


def valor_da_opcao(selects: dict[str, list[dict[str, Any]]], campo: str, rotulo: str) -> str:
    achados = [o["valor"] for o in selects.get(campo, []) if o["rotulo"] == rotulo]
    if len(achados) != 1:
        raise RuntimeError(f"opção '{rotulo}' não encontrada (ou ambígua) no campo {campo} do formulário")
    return achados[0]


def arquivo_do_mes(selects: dict[str, list[dict[str, Any]]], comp: str, fonte: str = "qrbr") -> str:
    valor = valor_da_opcao(selects, "Arquivos", rotulo_mes(comp))
    if valor.lower() != f"{fonte}{comp[2:]}.dbf":
        raise RuntimeError(f"Arquivos: '{rotulo_mes(comp)}' aponta para {valor}, não para {fonte}{comp[2:]}.dbf")
    return valor


def montar_corpo(selects_por_fonte: dict[str, dict[str, list[dict[str, Any]]]], consulta: str, comp: str) -> str:
    """Corpo do POST: campos e valores lidos do formulário da fonte da consulta, codificados em latin-1."""
    checar_limite(comp)
    spec = CONSULTAS[consulta]
    fonte = spec["fonte"]
    selects = selects_por_fonte[fonte]
    pares: list[tuple[str, str]] = [
        ("Linha", valor_da_opcao(selects, "Linha", LINHA[spec["linha"]])),
        ("Coluna", valor_da_opcao(selects, "Coluna", COLUNA[spec["coluna"]])),
        ("Incremento", valor_da_opcao(selects, "Incremento", INCREMENTO[spec["incremento"]])),
        ("Arquivos", arquivo_do_mes(selects, comp, fonte)),
    ]
    for campo, opcoes in selects.items():
        if not campo.startswith("S"):
            continue
        if campo in spec["filtros"]:
            pares.append((campo, valor_da_opcao(selects, campo, spec["filtros"][campo])))
        else:
            padrao = [o["valor"] for o in opcoes if o["selecionada"]]
            if padrao != ["TODAS_AS_CATEGORIAS__"]:
                raise RuntimeError(f"filtro {campo} sem 'Todas as categorias' como padrão: {padrao}")
            pares.append((campo, padrao[0]))
    faltam = set(spec["filtros"]) - set(selects)
    if faltam:
        raise RuntimeError(f"filtros ausentes do formulário: {sorted(faltam)}")
    pares += [("zeradas", "exibirlz"), ("formato", "prn"), ("mostre", "Mostra")]
    return urllib.parse.urlencode(pares, encoding=ENCODING)


# ---------------------------------------------------------------- download

def _http(url: str, corpo: str | None, timeout: int) -> tuple[bytes, int]:
    dados = corpo.encode("ascii") if corpo is not None else None
    req = urllib.request.Request(url, data=dados, headers={
        "User-Agent": "Mozilla/5.0",
        **({"Content-Type": "application/x-www-form-urlencoded"} if dados is not None else {}),
    })
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read(), resp.status


def baixar_formulario(fonte: str) -> dict[str, Any]:
    f = FONTES[fonte]
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    corpo, status = _http(f["url_form"], None, 120)
    ler_formulario(corpo.decode(ENCODING), fonte)  # falha se não for o formulário
    f["form_file"].write_bytes(corpo)
    meta = {
        "fonte": fonte, "url": f["url_form"], "metodo": "GET", "http_status": status,
        "data_hora_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "sha256": sha256_bytes(corpo), "bytes": len(corpo),
    }
    f["form_meta"].write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    log(f"formulário {fonte}: {len(corpo):,} bytes, SHA-256 {meta['sha256'][:12]}")
    return meta


def carregar_formulario(fonte: str) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    f = FONTES[fonte]
    if not f["form_file"].exists() or not f["form_meta"].exists():
        raise RuntimeError(f"formulário {fonte} ausente do cache; rode --etapa baixar")
    meta = json.loads(f["form_meta"].read_text(encoding="utf-8"))
    if sha256_arquivo(f["form_file"]) != meta["sha256"]:
        raise RuntimeError(f"SHA-256 do formulário {fonte} em cache difere do metadado")
    return ler_formulario(f["form_file"].read_bytes().decode(ENCODING), fonte), meta


def caminho_resposta(consulta: str, comp: str) -> Path:
    return CACHE_DIR / consulta / f"{comp}.html"


def caminho_meta(consulta: str, comp: str) -> Path:
    return CACHE_DIR / consulta / f"{comp}.json"


def cache_valido(consulta: str, comp: str, corpo: str) -> bool:
    r, m = caminho_resposta(consulta, comp), caminho_meta(consulta, comp)
    if not (r.exists() and m.exists()):
        return False
    meta = json.loads(m.read_text(encoding="utf-8"))
    return meta.get("corpo_post") == corpo and meta.get("sha256") == sha256_arquivo(r)


def baixar_consulta(selects_por_fonte: dict[str, dict[str, list[dict[str, Any]]]], consulta: str, comp: str,
                    tentativas: int = 4, timeout: int = 300) -> str:
    corpo = montar_corpo(selects_por_fonte, consulta, comp)
    if cache_valido(consulta, comp, corpo):
        return "cache"
    url = FONTES[CONSULTAS[consulta]["fonte"]]["url_tab"]
    destino = caminho_resposta(consulta, comp)
    destino.parent.mkdir(parents=True, exist_ok=True)
    erro = ""
    for t in range(1, tentativas + 1):
        t0 = time.time()
        try:
            bruto, status = _http(url, corpo, timeout)
            texto = bruto.decode(ENCODING)
            ler_tabela(texto, consulta, comp)  # resposta fora do formato não entra no cache
        except Exception as exc:  # noqa: BLE001
            erro = f"{type(exc).__name__}: {exc}"
            log(f"  {consulta} {comp}: falha na tentativa {t}/{tentativas} ({erro})")
            time.sleep(min(10 * 2 ** (t - 1), 120))
            continue
        destino.write_bytes(bruto)
        meta = {
            "consulta": consulta, "competencia": comp, "url": url, "metodo": "POST",
            "corpo_post": corpo, "codificacao_corpo": ENCODING, "http_status": status,
            "data_hora_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "sha256": sha256_bytes(bruto), "bytes": len(bruto), "segundos": round(time.time() - t0, 1),
            "tentativa": t,
        }
        caminho_meta(consulta, comp).write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
                                                encoding="utf-8")
        time.sleep(PAUSA_ENTRE_CONSULTAS)
        return "baixada"
    raise RuntimeError(f"{consulta} {comp}: consulta falhou após {tentativas} tentativas: {erro}")


def etapa_baixar(competencias: list[str], consultas: list[str]) -> dict[str, Any]:
    selects = {}
    for fonte in FONTES:
        baixar_formulario(fonte)
        selects[fonte] = ler_formulario(FONTES[fonte]["form_file"].read_bytes().decode(ENCODING), fonte)
    falhas: dict[str, str] = {}
    contagem = {"cache": 0, "baixada": 0}
    for comp in competencias:
        for consulta in consultas:
            try:
                contagem[baixar_consulta(selects, consulta, comp)] += 1
            except Exception as exc:  # noqa: BLE001
                falhas[f"{consulta}/{comp}"] = str(exc)
        log(f"{comp}: ok ({contagem['baixada']} baixadas, {contagem['cache']} do cache, {len(falhas)} falhas)")
    return {"contagem": contagem, "falhas": falhas}


# ---------------------------------------------------------------- leitura das respostas

def _numero(celula: str, decimal: bool) -> float | int:
    c = celula.strip()
    if c == "-":
        return 0
    if decimal:
        if not re.fullmatch(r"-?\d+(,\d+)?", c):
            raise ValueError(f"célula não numérica: {celula!r}")
        return float(c.replace(",", "."))
    if not re.fullmatch(r"\d+", c):
        raise ValueError(f"célula não inteira: {celula!r}")
    return int(c)


def ler_tabela(texto: str, consulta: str, comp: str) -> dict[str, Any]:
    """Lê a tabela 'prn' (entre <PRE> e </PRE>) e confere título, cabeçalho, período, filtro e totais.

    Devolve as colunas (rótulos), as linhas (rótulo, valores, eh_zero) e a linha Total.
    """
    spec = CONSULTAS[consulta]
    if "<PRE>" not in texto or "</PRE>" not in texto:
        raise RuntimeError("resposta sem tabela <PRE>")
    cabeca, resto = texto.split("<PRE>", 1)
    bloco = resto.split("</PRE>", 1)[0]
    # o título da página distingue local de residência (qrbr) de local de internação (qibr)
    titulo = re.search(r"<TITLE>([^<]*)</TITLE>", cabeca, re.I)
    if titulo:
        esperado = "resid" if spec["fonte"] == "qrbr" else "interna"
        if esperado not in html.unescape(titulo.group(1)).lower():
            raise RuntimeError(f"título da resposta não é o da fonte {spec['fonte']}: {titulo.group(1)!r}")
    periodo = re.search(r"<b>Per&iacute;odo:</b>\s*([^<]*)", cabeca)
    if not periodo or html.unescape(periodo.group(1)).strip() != rotulo_mes(comp):
        raise RuntimeError(f"período da resposta difere de {rotulo_mes(comp)}")
    cabeca_txt = html.unescape(cabeca)
    for campo, rotulo in spec["filtros"].items():
        # o TabNet ecoa cada filtro ativo: SGrupo_procedimento -> "<b>Grupo procedimento:</b> 04 ..."
        nome_campo = campo[1:].replace("_", " ")
        eco = re.search(rf"<b>{re.escape(nome_campo)}:</b>\s*([^<]*)", cabeca_txt)
        eco_txt = eco.group(1).strip() if eco else None
        if eco_txt != rotulo:
            raise RuntimeError(f"filtro {campo} não ecoado como '{rotulo}' (eco: {eco_txt!r})")
    linhas = [ln for ln in bloco.strip().splitlines() if ln.strip() and ln.strip() != "&"]
    rows = list(csv.reader(linhas, delimiter=";", quotechar='"'))
    if len(rows) < 3:
        raise RuntimeError("tabela vazia")
    cab = [html.unescape(c).strip() for c in rows[0]]
    if cab[0] != LINHA[spec["linha"]] or cab[-1] != "Total":
        raise RuntimeError(f"cabeçalho inesperado: {cab[:1]} ... {cab[-1:]}")
    decimal = spec["incremento"] == "valor"
    hierarquica = spec["linha"] == "procmes"  # linhas de ano (subtotal) seguidas dos 12 meses recuados
    corpo = []
    subtotais_ano: dict[str, list] = {}
    total = None
    for r in rows[1:]:
        if len(r) != len(cab):
            raise RuntimeError(f"linha com {len(r)} campos; cabeçalho tem {len(cab)}: {r[:2]}")
        rotulo = html.unescape(r[0]).strip()
        if hierarquica:
            rotulo = rotulo.lstrip(". ")
        valores = [_numero(c, decimal) for c in r[1:]]
        eh_zero = [c.strip() == "-" for c in r[1:]]
        soma = sum(valores[:-1])
        if (abs(soma - valores[-1]) > 0.011 * len(valores)) if decimal else (soma != valores[-1]):
            raise RuntimeError(f"linha '{rotulo}': soma das colunas {soma} difere do Total {valores[-1]}")
        if rotulo == "Total":
            total = valores
        elif hierarquica and re.fullmatch(r"\d{4}", rotulo):
            subtotais_ano[rotulo] = valores
        else:
            corpo.append((rotulo, valores, eh_zero))
    if total is None:
        raise RuntimeError("linha Total ausente")
    for ano, sub in subtotais_ano.items():
        meses = [v for rot, v, _ in corpo if rot.endswith(f"/{ano}")]
        if len(meses) != 12 or [sum(x) for x in zip(*meses)] != sub:
            raise RuntimeError(f"subtotal do ano {ano} não confere com os 12 meses")
    for j in range(len(cab) - 1):
        soma = sum(v[j] for _, v, _ in corpo)
        if (abs(soma - total[j]) > 0.011 * len(corpo)) if decimal else (soma != total[j]):
            raise RuntimeError(f"coluna '{cab[j + 1]}': soma das linhas {soma} difere do Total {total[j]}")
    nota = re.search(r"<li>(Dados referentes[^<]*)", texto)
    return {"colunas": cab[1:-1], "linhas": corpo, "total": total,
            "nota_atualizacao": html.unescape(nota.group(1)).strip() if nota else None}


def carregar(consulta: str, comp: str) -> dict[str, Any]:
    r, m = caminho_resposta(consulta, comp), caminho_meta(consulta, comp)
    if not (r.exists() and m.exists()):
        raise RuntimeError(f"resposta ausente no cache: {consulta}/{comp} (rode --etapa baixar)")
    meta = json.loads(m.read_text(encoding="utf-8"))
    bruto = r.read_bytes()
    if sha256_bytes(bruto) != meta["sha256"]:
        raise RuntimeError(f"SHA-256 do cache difere do metadado: {consulta}/{comp}")
    tab = ler_tabela(bruto.decode(ENCODING), consulta, comp)
    tab["meta"] = meta
    return tab


def classificar_linha_municipal(rotulo: str) -> tuple[str, str, str]:
    """Devolve (tipo, chave, uf): ('municipio', co_ibge, uf), ('ignorado_uf', 'IGNORADO_XX', uf)
    ou ('ignorado_exterior', '000000', '00')."""
    m = re.fullmatch(r"MUNICIPIO IGNORADO - ([A-Z]{2})", rotulo)
    if m:
        sigla = m.group(1)
        if sigla not in UF_SIGLA_CODIGO:
            raise RuntimeError(f"UF desconhecida em '{rotulo}'")
        return "ignorado_uf", f"IGNORADO_{sigla}", UF_SIGLA_CODIGO[sigla]
    m = re.fullmatch(r"(\d{6}) (.+)", rotulo)
    if not m:
        raise RuntimeError(f"linha municipal fora do padrão: '{rotulo}'")
    if m.group(1) == "000000":
        return "ignorado_exterior", "000000", "00"
    if m.group(1)[:2] not in UF_CODIGO_SIGLA:
        raise RuntimeError(f"código municipal com UF desconhecida: '{rotulo}'")
    return "municipio", m.group(1), m.group(1)[:2]


def universo_do_formulario(selects: dict[str, list[dict[str, Any]]]) -> list[str]:
    cods = []
    for o in selects["SMunicípio"]:
        if o["valor"] == "TODAS_AS_CATEGORIAS__":
            continue
        tipo, chave, _ = classificar_linha_municipal(o["rotulo"])
        if tipo == "municipio":
            cods.append(chave)
    if len(cods) != len(set(cods)) or len(cods) < 5_500:
        raise RuntimeError("lista de municípios do formulário inválida")
    return sorted(cods)


def grupo_do_rotulo(rotulo: str) -> str:
    m = re.fullmatch(r"(\d{2}) .+", rotulo)
    if not m:
        raise RuntimeError(f"rótulo de grupo fora do padrão: '{rotulo}'")
    return m.group(1)


def tabela_longa(tab: dict[str, Any], dimensao: str) -> pd.DataFrame:
    """Linhas municipais em formato longo: tipo, chave, uf, categoria, valor, eh_zero."""
    reg = []
    ordem_uf = []
    for rotulo, valores, zeros in tab["linhas"]:
        tipo, chave, uf = classificar_linha_municipal(rotulo)
        ordem_uf.append((tipo, uf))
        for j, col in enumerate(tab["colunas"]):
            cat = grupo_do_rotulo(col) if dimensao == "grupo" else slug(col)
            reg.append((tipo, chave, uf, cat, valores[j], zeros[j]))
    # o ignorado de cada UF vem logo antes do primeiro município da UF (confere UF_SIGLA_CODIGO);
    # o DF não tem linha de ignorado no TabNet
    for i, (tipo, uf) in enumerate(ordem_uf):
        if tipo == "ignorado_uf":
            seguinte = ordem_uf[i + 1] if i + 1 < len(ordem_uf) else (None, None)
            if seguinte != ("municipio", uf):
                raise RuntimeError(f"'MUNICIPIO IGNORADO' da UF {uf} não precede município da UF {uf}")
    df = pd.DataFrame(reg, columns=["tipo", "chave", "uf", "categoria", "valor", "eh_zero"])
    if df.duplicated(["chave", "categoria"]).any():
        raise RuntimeError("linha municipal duplicada na resposta")
    return df


def totais_por_uf(tab: dict[str, Any], grupos: list[str]) -> dict[str, dict[str, Any]]:
    """Consulta Linha = UF: {código da UF: {grupo: AIH, 'total': AIH}}."""
    saida = {}
    for rotulo, valores, _ in tab["linhas"]:
        saida[rotulo[:2]] = dict(zip(grupos + ["total"], valores))
    return saida


# ---------------------------------------------------------------- comparação com o a13 (v9)

def totais_a13() -> dict[str, Any]:
    """Totais nacionais versionados do a13 por mês × grupo: AIH (validações) e internações e valor
    (painel + ignorados, com UF-mês ausente somando zero, que é o que o Total do TabNet somou)."""
    if not A13_VALIDACOES.exists():
        raise RuntimeError(f"{A13_VALIDACOES.relative_to(ROOT)} ausente: o a13 tem de vir antes do a15")
    val = json.loads(A13_VALIDACOES.read_text(encoding="utf-8"))
    cols = ["competencia", "grupo", "aih_aprovadas", "internacoes", "valor_total"]
    partes = [pd.read_parquet(p, columns=cols) for p in (A13_PAINEL, A13_IGNORADOS)]
    soma = pd.concat(partes, ignore_index=True)
    soma[["aih_aprovadas", "internacoes"]] = soma[["aih_aprovadas", "internacoes"]].astype("float64")
    agg = soma.groupby(["competencia", "grupo"]).agg(
        aih=("aih_aprovadas", "sum"), internacoes=("internacoes", "sum"), valor=("valor_total", "sum"),
        celulas=("valor_total", "size"))
    return {
        "aih": {c: v["total_aih_por_grupo"] for c, v in val["por_competencia"].items()},
        "agregado": agg,
        "uf_meses_sem_dado": [(r["competencia"], r["uf"]) for r in val["uf_meses_sem_dado"]],
        "uf_meses_atipicos": [(r["competencia"], r["uf"]) for r in val["uf_meses_atipicos"]],
        "sha256_validacoes": sha256_arquivo(A13_VALIDACOES),
    }


# ---------------------------------------------------------------- consolidação

def consolidar(competencias: list[str]) -> dict[str, Any]:
    selects, form_meta = carregar_formulario("qrbr")
    selects_int, form_meta_int = carregar_formulario("qibr")
    universo = universo_do_formulario(selects)
    for comp in competencias:
        arquivo_do_mes(selects, comp, "qrbr")  # o mês existe no formulário
        arquivo_do_mes(selects_int, comp, "qibr")
    a13 = totais_a13()

    erros: list[str] = []
    val: dict[str, Any] = {"por_competencia": {}}
    partes_mun, partes_car = [], []
    totais_uf: dict[str, dict[str, int]] = {}
    totais_uf_int: dict[str, dict[str, int]] = {}
    grupos_por_mes: dict[str, list[str]] = {}
    carater_rotulos: dict[str, str] = {}
    consultas_meta: list[dict[str, Any]] = []
    notas: set[str] = set()
    comparacao_a13: dict[str, Any] = {}

    for comp in competencias:
        checar_limite(comp)
        tabs = {c: carregar(c, comp) for c in CONSULTAS}
        for c in CONSULTAS:
            consultas_meta.append({k: tabs[c]["meta"][k] for k in (
                "consulta", "competencia", "url", "metodo", "corpo_post", "codificacao_corpo", "http_status",
                "data_hora_utc", "sha256", "bytes")})
            if tabs[c]["nota_atualizacao"]:
                notas.add(tabs[c]["nota_atualizacao"])
        v: dict[str, Any] = {}

        # V4: conceito de tempo — o arquivo do mês tem uma só linha de processamento, a do próprio mês
        pm = tabs["procmes_grupo_aih"]
        rot_pm = [r for r, valores, _ in pm["linhas"] if valores[-1] != 0]
        v["v4_mes_processamento"] = rot_pm == [rotulo_procmes(comp)]
        if not v["v4_mes_processamento"]:
            erros.append(f"{comp}: linhas de processamento {rot_pm}, esperado [{rotulo_procmes(comp)}]")

        grupos = [grupo_do_rotulo(c) for c in tabs["mun_grupo_aih"]["colunas"]]
        grupos_por_mes[comp] = grupos
        for c in ("uf_grupo_aih", "procmes_grupo_aih"):
            g_c = [grupo_do_rotulo(x) for x in tabs[c]["colunas"]]
            if g_c != grupos:
                erros.append(f"{comp}: grupos de {c} {g_c} diferem de mun_grupo_aih {grupos}")

        # V2: Total nacional do município = UF = processamento (AIH)
        t_mun, t_uf, t_pm = tabs["mun_grupo_aih"]["total"], tabs["uf_grupo_aih"]["total"], pm["total"]
        linha_pm = [valores for r, valores, _ in pm["linhas"] if r == rotulo_procmes(comp)]
        v["v2_total_mun_uf_procmes"] = t_mun == t_uf == t_pm and linha_pm == [t_pm]
        if not v["v2_total_mun_uf_procmes"]:
            erros.append(f"{comp}: Total municipal {t_mun}, UF {t_uf}, processamento {t_pm} diferem")
        tot_res = dict(zip(grupos + ["total"], t_mun))
        v["total_aih_por_grupo"] = tot_res

        # V8: mesmas AIH — total nacional por residência = total por local de internação, na mesma execução
        g_int = [grupo_do_rotulo(x) for x in tabs["int_uf_grupo_aih"]["colunas"]]
        tot_int = dict(zip(g_int + ["total"], tabs["int_uf_grupo_aih"]["total"]))
        chaves = sorted(set(tot_res) | set(tot_int))
        v["v8_total_residencia_igual_internacao"] = all(tot_res.get(k, 0) == tot_int.get(k, 0) for k in chaves)
        v["total_aih_internacao_contemporaneo"] = tot_int
        if not v["v8_total_residencia_igual_internacao"]:
            erros.append(f"{comp}: total nacional por residência {tot_res} ≠ por local de internação {tot_int}")

        # V9: comparação com o total versionado do a13 (a fonte pode ter revisto meses recentes)
        tot_a13 = a13["aih"].get(comp)
        if tot_a13 is None:
            erros.append(f"{comp}: mês ausente das validações do a13")
            situacao = "sem_a13"
        else:
            ks = sorted(set(tot_res) | set(tot_a13))
            igual = all(tot_res.get(k, 0) == tot_a13.get(k, 0) for k in ks)
            if igual:
                situacao = "igual_a13"
            elif v["v8_total_residencia_igual_internacao"]:
                situacao = "revisado_na_fonte_depois_do_a13"
            else:
                situacao = "divergente_nao_explicado"
                erros.append(f"{comp}: total por residência difere do a13 sem revisão da fonte que explique")
        comparacao_a13[comp] = {
            "situacao": situacao, "total_a13": tot_a13, "total_residencia": tot_res,
            "total_internacao_contemporaneo": tot_int,
            "diferenca_total_residencia_menos_a13": (tot_res["total"] - tot_a13["total"]) if tot_a13 else None,
        }
        v["v9_situacao_frente_ao_a13"] = situacao

        # Tabelas longas
        longas = {
            "aih": tabela_longa(tabs["mun_grupo_aih"], "grupo"),
            "internacoes": tabela_longa(tabs["mun_grupo_internacoes"], "grupo"),
            "valor": tabela_longa(tabs["mun_grupo_valor"], "grupo"),
        }
        # V7: universo do formulário = municípios de cada resposta
        car = tabela_longa(tabs["mun_carater_g04_aih"], "carater")
        ok7 = True
        for k, df in list(longas.items()) + [("carater", car)]:
            cods = sorted(df.loc[df["tipo"] == "municipio", "chave"].unique())
            if cods != universo:
                ok7 = False
                faltam = sorted(set(universo) - set(cods))[:10]
                sobram = sorted(set(cods) - set(universo))[:10]
                erros.append(f"{comp} {k}: municípios da resposta diferem do formulário (faltam {faltam}, sobram {sobram})")
        v["v7_universo_municipios"] = ok7

        # V3: soma municipal (municípios + ignorado da UF) por UF × grupo = linha da UF de residência
        aih = longas["aih"]
        uf_tab = totais_por_uf(tabs["uf_grupo_aih"], grupos)
        por_uf = aih.groupby(["uf", "categoria"])["valor"].sum()
        ok3 = True
        for cod, d in uf_tab.items():
            for g in grupos:
                s = int(por_uf.get((cod, g), 0))
                if s != d[g]:
                    ok3 = False
                    erros.append(f"{comp}: UF {cod} grupo {g}: soma municipal {s} ≠ linha UF {d[g]}")
        v["v3_soma_municipal_por_uf"] = ok3
        # V1: soma de todas as linhas (municípios + ignorados) = Total, por incremento
        ok1 = True
        totais_incremento = {}
        for k, c in (("aih", "mun_grupo_aih"), ("internacoes", "mun_grupo_internacoes"), ("valor", "mun_grupo_valor")):
            cols = [grupo_do_rotulo(x) for x in tabs[c]["colunas"]]
            totais_incremento[k] = dict(zip(cols + ["total"], tabs[c]["total"]))
            s = longas[k].groupby("categoria")["valor"].sum()
            for j, g in enumerate(cols):
                tol = 0.011 * len(universo) if k == "valor" else 0
                if abs(float(s.get(g, 0)) - tabs[c]["total"][j]) > tol:
                    ok1 = False
                    erros.append(f"{comp} {k}: soma das linhas do grupo {g} ≠ Total")
        v["v1_soma_linhas_igual_total"] = ok1

        # V9 (internações e valor): nos meses iguais ao a13 em AIH, os outros dois incrementos também
        if situacao == "igual_a13":
            ok9 = True
            for k in ("internacoes", "valor"):
                for g, total_res in totais_incremento[k].items():
                    if g == "total":
                        continue
                    if (comp, g) not in a13["agregado"].index:
                        ok9 = ok9 and total_res == 0
                        continue
                    linha = a13["agregado"].loc[(comp, g)]
                    if k == "internacoes":
                        ok9 = ok9 and int(linha["internacoes"]) == int(total_res)
                    else:
                        # o a13 soma células arredondadas a centavos; o Total do TabNet não: tolerância de meio
                        # centavo por célula somada
                        ok9 = ok9 and abs(float(linha["valor"]) - float(total_res)) <= 0.005 * float(linha["celulas"]) + 0.01
            v["v9_internacoes_valor_iguais_a13"] = ok9
            if not ok9:
                erros.append(f"{comp}: internações ou valor nacionais diferem do a13 num mês em que a AIH é igual")
        else:
            v["v9_internacoes_valor_iguais_a13"] = None
        v["totais_nacionais_residencia"] = totais_incremento

        totais_uf[comp] = {cod: d["total"] for cod, d in uf_tab.items() if cod != "00"}
        faltam_ufs = sorted(set(UF_CODIGO_SIGLA) - set(totais_uf[comp]))
        if faltam_ufs:
            erros.append(f"{comp}: UFs sem linha na consulta por UF de residência: {faltam_ufs}")
        uf_int = totais_por_uf(tabs["int_uf_grupo_aih"], g_int)
        totais_uf_int[comp] = {cod: d["total"] for cod, d in uf_int.items() if cod != "00"}
        faltam_ufs = sorted(set(UF_CODIGO_SIGLA) - set(totais_uf_int[comp]))
        if faltam_ufs:
            erros.append(f"{comp}: UFs sem linha na consulta por UF de internação: {faltam_ufs}")

        # V5: caráter do grupo 04 soma o grupo 04 municipal
        for col in tabs["mun_carater_g04_aih"]["colunas"]:
            carater_rotulos[slug(col)] = col
        soma_car = car.groupby("chave")["valor"].sum()
        g04 = aih.loc[aih["categoria"] == "04"].set_index("chave")["valor"] if "04" in grupos else pd.Series(dtype=int)
        comp_car = pd.concat([soma_car.rename("car"), g04.rename("g04")], axis=1).fillna(0)
        v["v5_carater_soma_g04"] = bool((comp_car["car"] == comp_car["g04"]).all())
        if not v["v5_carater_soma_g04"]:
            erros.append(f"{comp}: soma por caráter difere do grupo 04 em {int((comp_car['car'] != comp_car['g04']).sum())} linhas")

        # V6: conferência célula a célula de UF pequena (consulta filtrada pela UF de residência × nacional)
        v6 = {}
        nac_linhas = {}
        for rotulo, valores, _ in tabs["mun_grupo_aih"]["linhas"]:
            _, chave, _ = classificar_linha_municipal(rotulo)
            nac_linhas[chave] = dict(zip(grupos + ["total"], valores))
        for c, cod in UFS_CONFERENCIA_CELULA.items():
            g_f = [grupo_do_rotulo(x) for x in tabs[c]["colunas"]]
            n_cel, ok = 0, True
            for rotulo, valores, _ in tabs[c]["linhas"]:
                tipo, chave, uf = classificar_linha_municipal(rotulo)
                f = dict(zip(g_f + ["total"], valores))
                if tipo != "ignorado_exterior" and uf == cod:
                    nac_l = nac_linhas.get(chave, {})
                    for g in grupos + ["total"]:
                        n_cel += 1
                        if f.get(g, 0) != nac_l.get(g):
                            ok = False
                elif f["total"] != 0:
                    ok = False
            v6[UF_CODIGO_SIGLA[cod]] = {"celulas_comparadas": n_cel, "identicas": ok}
            if not ok or n_cel == 0:
                erros.append(f"{comp}: conferência célula a célula da UF {UF_CODIGO_SIGLA[cod]} reprovada")
        v["v6_uf_pequena_celula_a_celula"] = v6

        # Partes do painel
        base = longas["aih"].rename(columns={"valor": "aih_aprovadas", "eh_zero": "aih_zero"})
        for k in ("internacoes", "valor"):
            base = base.merge(longas[k][["chave", "categoria", "valor"]].rename(columns={"valor": k}),
                              on=["chave", "categoria"], how="left", validate="one_to_one")
        base["competencia"] = comp
        partes_mun.append(base)
        car["competencia"] = comp
        partes_car.append(car)
        v["municipios_com_aih"] = int(base.loc[(base["tipo"] == "municipio") & (base["aih_aprovadas"] > 0), "chave"].nunique())
        v["municipios_com_aih_g04"] = int(base.loc[(base["tipo"] == "municipio") & (base["categoria"] == "04")
                                                   & (base["aih_aprovadas"] > 0), "chave"].nunique())
        val["por_competencia"][comp] = v

    # UF-mês sem dado: (a) residência com total zero; (b) arquivo de internação da UF ausente
    tot = pd.DataFrame(totais_uf).T.sort_index()  # competência × UF (residência)
    tot_int = pd.DataFrame(totais_uf_int).T.sort_index()  # competência × UF (internação)
    aus_res = sorted((c, uf) for c in tot.index for uf in tot.columns if tot.loc[c, uf] == 0)
    aus_int = sorted((c, uf) for c in tot_int.index for uf in tot_int.columns if tot_int.loc[c, uf] == 0)
    medianas = tot_int.where(tot_int > 0).median()
    atipicos = sorted(
        (c, uf) for c in tot_int.index for uf in tot_int.columns
        if tot_int.loc[c, uf] > 0 and tot_int.loc[c, uf] < FRACAO_ATIPICO * medianas[uf]
    )
    set_res, set_int, set_atip = set(aus_res), set(aus_int), set(atipicos)
    # mês com falta em outra UF: alguma outra UF de internação sem arquivo ou atípica no mês
    falta_mes: dict[str, set[str]] = {}
    for c, uf in aus_int + atipicos:
        falta_mes.setdefault(c, set()).add(uf)

    def status_ausencia(comp: str, uf: str) -> str | None:
        if (comp, uf) in set_int:
            return "ausente_uf_internacao_sem_dado"
        if (comp, uf) in set_res:
            return "ausente_uf_mes_sem_dado"
        return None

    def falta_outra(comp: str, uf: str) -> bool:
        return bool(falta_mes.get(comp, set()) - {uf})

    # Grupos do painel: união das colunas devolvidas em algum mês
    grupos_painel = sorted({g for gs in grupos_por_mes.values() for g in gs})

    mun = pd.concat(partes_mun, ignore_index=True)
    obs = mun.loc[mun["tipo"] == "municipio"]
    esqueleto = pd.MultiIndex.from_product([universo, competencias, grupos_painel],
                                           names=["chave", "competencia", "categoria"]).to_frame(index=False)
    painel = esqueleto.merge(obs[["chave", "competencia", "categoria", "aih_aprovadas", "aih_zero",
                                  "internacoes", "valor"]],
                             on=["chave", "competencia", "categoria"], how="left", validate="one_to_one")
    omitida = painel["aih_aprovadas"].isna()  # grupo sem coluna no mês: zero (V1 confere o Total)
    painel["status"] = np.where(omitida, "zero_coluna_omitida",
                                np.where(painel["aih_zero"].fillna(False).astype(bool), "zero_tabnet", "observado"))
    for col in ("aih_aprovadas", "internacoes"):
        painel[col] = painel[col].fillna(0).astype("Int64")
    painel["valor"] = painel["valor"].fillna(0.0).astype(float)
    painel = painel.rename(columns={"chave": "co_ibge", "categoria": "grupo", "valor": "valor_total"})
    painel["uf"] = painel["co_ibge"].str[:2]

    def aplicar_ausencia(df: pd.DataFrame, cols_int: list[str], cols_float: list[str]) -> pd.DataFrame:
        chave = list(zip(df["competencia"], df["uf"]))
        st = np.array([status_ausencia(c, u) for c, u in chave], dtype=object)
        mask = np.array([s is not None for s in st])
        for col in cols_int:
            df.loc[mask, col] = pd.NA
        for col in cols_float:
            df.loc[mask, col] = np.nan
        df.loc[mask, "status"] = st[mask]
        return df

    painel = aplicar_ausencia(painel, ["aih_aprovadas", "internacoes"], ["valor_total"])
    chave_uf = list(zip(painel["competencia"], painel["uf"]))
    painel["uf_mes_atipico"] = np.array([k in set_atip for k in chave_uf])
    painel["mes_com_falta_em_outra_uf"] = np.array([falta_outra(c, u) for c, u in chave_uf])
    painel["natureza_dos_dados"] = "EMPIRICO"
    painel = painel[COLUNAS_PAINEL].sort_values(["co_ibge", "competencia", "grupo"], kind="mergesort").reset_index(drop=True)

    # Ignorados (município ignorado de cada UF e ignorado/exterior)
    ign = mun.loc[mun["tipo"] != "municipio"].copy()
    esq_i = pd.MultiIndex.from_product(
        [sorted(ign["chave"].unique()), competencias, grupos_painel], names=["chave", "competencia", "categoria"]
    ).to_frame(index=False)
    ign = esq_i.merge(ign[["chave", "competencia", "categoria", "aih_aprovadas", "aih_zero", "internacoes", "valor"]],
                      on=["chave", "competencia", "categoria"], how="left", validate="one_to_one")
    ign["uf"] = ign["chave"].map(lambda k: "00" if k == "000000" else UF_SIGLA_CODIGO[k.split("_")[1]])
    omit_i = ign["aih_aprovadas"].isna()
    ign["status"] = np.where(omit_i, "zero_coluna_omitida",
                             np.where(ign["aih_zero"].fillna(False).astype(bool), "zero_tabnet", "observado"))
    for col in ("aih_aprovadas", "internacoes"):
        ign[col] = ign[col].fillna(0).astype("Int64")
    ign["valor"] = ign["valor"].fillna(0.0).astype(float)
    ign = ign.rename(columns={"chave": "linha_tabnet", "categoria": "grupo", "valor": "valor_total"})
    ign = aplicar_ausencia(ign, ["aih_aprovadas", "internacoes"], ["valor_total"])
    ign["natureza_dos_dados"] = "EMPIRICO"
    ign = ign[COLUNAS_IGNORADOS].sort_values(["linha_tabnet", "competencia", "grupo"], kind="mergesort").reset_index(drop=True)

    # Painel de caráter (grupo 04)
    carl = pd.concat(partes_car, ignore_index=True)
    carl = carl.loc[carl["tipo"] == "municipio"]
    categorias = sorted(carater_rotulos)
    esq_c = pd.MultiIndex.from_product([universo, competencias, categorias],
                                       names=["chave", "competencia", "categoria"]).to_frame(index=False)
    carp = esq_c.merge(carl[["chave", "competencia", "categoria", "valor", "eh_zero"]],
                       on=["chave", "competencia", "categoria"], how="left", validate="one_to_one")
    omit_c = carp["valor"].isna()
    carp["status"] = np.where(omit_c, "zero_coluna_omitida",
                              np.where(carp["eh_zero"].fillna(False).astype(bool), "zero_tabnet", "observado"))
    carp["valor"] = carp["valor"].fillna(0).astype("Int64")
    carp = carp.rename(columns={"chave": "co_ibge", "categoria": "carater", "valor": "aih_aprovadas"})
    carp["uf"] = carp["co_ibge"].str[:2]
    carp = aplicar_ausencia(carp, ["aih_aprovadas"], [])
    chave_c = list(zip(carp["competencia"], carp["uf"]))
    carp["uf_mes_atipico"] = np.array([k in set_atip for k in chave_c])
    carp["mes_com_falta_em_outra_uf"] = np.array([falta_outra(c, u) for c, u in chave_c])
    carp["grupo"] = "04"
    carp["natureza_dos_dados"] = "EMPIRICO"
    carp = carp[COLUNAS_CARATER].sort_values(["co_ibge", "competencia", "carater"], kind="mergesort").reset_index(drop=True)

    # Consistência de UF-mês de residência zerado: todos os incrementos da UF zerados no mês
    for c, uf in aus_res:
        sub = mun.loc[(mun["competencia"] == c) & (mun["uf"] == uf)]
        if (sub[["aih_aprovadas", "internacoes", "valor"]].abs().sum() != 0).any():
            erros.append(f"{c}: UF {uf} com AIH total zero mas outro incremento positivo")

    val["uf_meses_sem_dado"] = [{"competencia": c, "uf": uf, "sigla": UF_CODIGO_SIGLA[uf]} for c, uf in aus_res]
    val["uf_meses_sem_arquivo_internacao"] = [
        {"competencia": c, "uf": uf, "sigla": UF_CODIGO_SIGLA[uf],
         "aih_residentes_internados_em_outra_uf_parcial": int(tot.loc[c, uf])}
        for c, uf in aus_int
    ]
    val["uf_meses_atipicos"] = [
        {"competencia": c, "uf": uf, "sigla": UF_CODIGO_SIGLA[uf], "aih_total_uf_internacao": int(tot_int.loc[c, uf]),
         "aih_total_uf_residencia": int(tot.loc[c, uf]),
         "mediana_mensal_uf_internacao": float(medianas[uf]),
         "fracao_da_mediana": round(float(tot_int.loc[c, uf] / medianas[uf]), 4)}
        for c, uf in atipicos
    ]
    val["meses_com_falta_ou_atipico_em_alguma_uf_de_internacao"] = {c: sorted(UF_CODIGO_SIGLA[u] for u in s)
                                                                    for c, s in sorted(falta_mes.items())}
    val["regra_uf_mes_sem_dado"] = "total de AIH aprovadas da UF de residência no mês igual a zero na consulta UF × grupo"
    val["regra_uf_mes_sem_arquivo_internacao"] = (
        "total de AIH aprovadas da UF no mês igual a zero na consulta contemporânea por local de internação "
        "(int_uf_grupo_aih, formulário qibr.def)"
    )
    val["regra_uf_mes_atipico"] = (
        f"total da UF de internação no mês > 0 e < {FRACAO_ATIPICO} × mediana mensal da UF em "
        f"{competencias[0]}–{competencias[-1]} (consulta contemporânea por local de internação); alerta "
        "(coluna uf_mes_atipico), o valor não é alterado"
    )
    val["regra_mes_com_falta_em_outra_uf"] = (
        "no mês, outra UF de internação está sem arquivo ou atípica: residentes desta UF internados lá podem "
        "faltar; alerta, o valor não é alterado"
    )
    val["comparacao_a13"] = {
        "a13_validacoes_sha256": a13["sha256_validacoes"],
        "por_competencia": comparacao_a13,
        "meses_iguais": sorted(c for c, d in comparacao_a13.items() if d["situacao"] == "igual_a13"),
        "meses_revisados_na_fonte": sorted(c for c, d in comparacao_a13.items()
                                           if d["situacao"] == "revisado_na_fonte_depois_do_a13"),
        "uf_meses_sem_dado_no_a13": [{"competencia": c, "uf": u, "sigla": UF_CODIGO_SIGLA[u]}
                                     for c, u in a13["uf_meses_sem_dado"]],
        "uf_meses_atipicos_no_a13": [{"competencia": c, "uf": u, "sigla": UF_CODIGO_SIGLA[u]}
                                     for c, u in a13["uf_meses_atipicos"]],
    }
    val["grupos_por_competencia"] = grupos_por_mes
    val["grupos_painel"] = grupos_painel
    val["carater_rotulos"] = carater_rotulos
    val["universo_municipios_formulario"] = len(universo)
    val["totais_uf_mes_aih_residencia"] = {c: {UF_CODIGO_SIGLA[u]: int(x) for u, x in sorted(d.items())}
                                           for c, d in sorted(totais_uf.items())}
    val["totais_uf_mes_aih_internacao"] = {c: {UF_CODIGO_SIGLA[u]: int(x) for u, x in sorted(d.items())}
                                           for c, d in sorted(totais_uf_int.items())}
    val["erros"] = erros
    val["status"] = "APROVADO" if not erros else "REPROVADO"
    val["natureza_dos_dados"] = "EMPIRICO"
    return {
        "painel": painel, "ignorados": ign, "carater": carp, "validacoes": val, "universo": universo,
        "form_meta": form_meta, "form_meta_int": form_meta_int, "consultas_meta": consultas_meta,
        "selects": selects, "selects_int": selects_int, "notas": sorted(notas),
    }


# ---------------------------------------------------------------- gravação

def gravar_parquet(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tabela = pa.Table.from_pandas(df, preserve_index=False)
    pq.write_table(tabela, path, compression="zstd", compression_level=9, use_dictionary=True)


def _opcoes_usadas(selects: dict[str, list[dict[str, Any]]], fonte: str) -> dict[str, Any]:
    usado: dict[str, Any] = {}
    specs = [s for s in CONSULTAS.values() if s["fonte"] == fonte]
    for campo, chave, rotulos in (("Linha", "linha", LINHA), ("Coluna", "coluna", COLUNA),
                                  ("Incremento", "incremento", INCREMENTO)):
        usados = sorted({rotulos[s[chave]] for s in specs})
        usado[campo] = {r: valor_da_opcao(selects, campo, r) for r in usados}
    usado["filtros"] = {
        f"{c}={r}": valor_da_opcao(selects, c, r)
        for spec in specs for c, r in spec["filtros"].items()
    }
    usado["dimensoes_disponiveis"] = {
        "Linha": [o["rotulo"] for o in selects["Linha"]],
        "Coluna": [o["rotulo"] for o in selects["Coluna"]],
        "Incremento": [o["rotulo"] for o in selects["Incremento"]],
        "filtros_S": [c for c in selects if c.startswith("S")],
    }
    usado["arquivos_no_formulario"] = {
        "primeiro": min(o["valor"] for o in selects["Arquivos"]),
        "ultimo_rotulo": next(o["rotulo"] for o in selects["Arquivos"] if o["selecionada"]),
        "n": len(selects["Arquivos"]),
    }
    return usado


def gravar_manifesto(res: dict[str, Any]) -> dict[str, Any]:
    val = res["validacoes"]
    manifesto = {
        "gerador": "scripts/aquisicao/a15_adquirir_sih_residencia.py",
        "plano": "docs/06_execucao/51_plano_perguntas_reformuladas.md (P3, T3.4, portão G3)",
        "natureza_dos_dados": "EMPIRICO",
        "data_execucao": dt.date.today().isoformat(),
        "fonte": {
            "nome": "SIH/SUS — Procedimentos hospitalares do SUS por local de residência, Brasil (TabNet/DATASUS)",
            "url_formulario": URL_FORM,
            "url_consulta": URL_TAB,
            "metodo": "POST application/x-www-form-urlencoded, latin-1; formato=prn, zeradas=exibirlz, mostre=Mostra",
            "formulario": {**res["form_meta"], "cache": FORM_FILE.relative_to(ROOT).as_posix()},
            "notas_da_fonte": res["notas"],
        },
        "fonte_conferencia": {
            "nome": "SIH/SUS — Procedimentos hospitalares do SUS por local de internação, Brasil (formulário do a13)",
            "url_formulario": FONTES["qibr"]["url_form"],
            "url_consulta": FONTES["qibr"]["url_tab"],
            "formulario": {**res["form_meta_int"], "cache": FONTES["qibr"]["form_file"].relative_to(ROOT).as_posix()},
            "uso": "só a consulta int_uf_grupo_aih: total nacional contemporâneo (v8), UF-mês sem arquivo de "
                   "internação e UF-mês atípico",
        },
        "conceito_de_tempo": (
            "mês de processamento da AIH: arquivo qrbrAAMM.dbf do campo Arquivos; cada arquivo conferido "
            "contra a linha 'Ano/mês processamento' (validação v4). Não é o mês da internação nem da alta."
        ),
        "conceito_de_lugar": (
            "município de residência do paciente (Linha 'Município' do formulário qrbr.def), não o do "
            "estabelecimento de internação; mede uso de internação pelos residentes, não oferta local"
        ),
        "unidade": ("município de residência (co_ibge, 6 dígitos) × competência de processamento (AAAAMM) × "
                    "grupo do procedimento principal (SIGTAP, 2 dígitos)"),
        "chaves": {"painel": ["co_ibge", "competencia", "grupo"], "carater": ["co_ibge", "competencia", "carater"],
                   "ignorados": ["linha_tabnet", "competencia", "grupo"]},
        "medidas": {
            "aih_aprovadas": "Incremento 'AIH aprovadas' (todas as AIH aprovadas no processamento, inclusive de continuidade)",
            "internacoes": "Incremento 'Internações' (exclui AIH de continuação/longa permanência)",
            "valor_total": "Incremento 'Valor total' em R$ correntes",
        },
        "filtros": {
            "painel_principal": "nenhum filtro (todas as categorias em todos os S*)",
            "painel_carater": f"SGrupo_procedimento = '{GRUPO_CIRURGICO_ROTULO}'",
            "sem_filtro_de_cbo": "o TabNet do SIH não oferece CBO do profissional; a AIH não é restrita a especialista",
        },
        "consultas": CONSULTAS,
        "opcoes_do_formulario_usadas": {"qrbr": _opcoes_usadas(res["selects"], "qrbr"),
                                        "qibr": _opcoes_usadas(res["selects_int"], "qibr")},
        "competencias_planejadas": COMPETENCIAS,
        "arquivos_planejados": {c: f"qrbr{c[2:]}.dbf" for c in COMPETENCIAS},
        "limite_ciclo3": f"nenhuma competência >= {LIMITE_EXCLUSIVO} é pedida; o plano lê SIH até {COMPETENCIA_FINAL}",
        "universo_municipios": {
            "origem": "opções do filtro SMunicípio do formulário qrbr.def baixado (sem leitura de IVS)",
            "n": len(res["universo"]),
            "sha256_lista": sha256_bytes("\n".join(res["universo"]).encode()),
        },
        "status_vocabulario": STATUS,
        "regras": {
            "zero": "'-' do TabNet é zero (legenda da página); nada é preenchido com zero fora disso e da coluna omitida conferida",
            "uf_mes_sem_dado": val["regra_uf_mes_sem_dado"] + "; status ausente_uf_mes_sem_dado (NaN)",
            "uf_mes_sem_arquivo_internacao": val["regra_uf_mes_sem_arquivo_internacao"]
            + "; municípios e ignorado da UF ficam NaN com status ausente_uf_internacao_sem_dado",
            "uf_mes_atipico": val["regra_uf_mes_atipico"],
            "mes_com_falta_em_outra_uf": val["regra_mes_com_falta_em_outra_uf"],
            "ignorados": "MUNICIPIO IGNORADO - UF e 000000 Ignorado ou exterior ficam em ignorados_sih_residencia_uf_mes_grupo.parquet",
            "fail_closed": "qualquer resposta ausente, fora do formato ou conferência obrigatória reprovada impede a gravação",
            "comparacao_a13": (
                "v8 (obrigatória): total nacional por residência = total por local de internação consultado na mesma "
                "execução. v9: igual ao total versionado do a13 nos meses não revistos pela fonte; mês diferente do a13 "
                "só passa se a consulta contemporânea por local de internação também mudou (revisão da fonte)"
            ),
        },
        "uf_meses_sem_dado": val["uf_meses_sem_dado"],
        "uf_meses_sem_arquivo_internacao": val["uf_meses_sem_arquivo_internacao"],
        "uf_meses_atipicos": val["uf_meses_atipicos"],
        "comparacao_a13": {k: val["comparacao_a13"][k] for k in (
            "a13_validacoes_sha256", "meses_iguais", "meses_revisados_na_fonte")},
        "saidas": {},
        "validacoes": {"arquivo": VALIDACOES_FILE.relative_to(ROOT).as_posix(), "status": val["status"],
                       "sha256": sha256_arquivo(VALIDACOES_FILE)},
        "consultas_realizadas": res["consultas_meta"],
        "cache_bruto": f"{CACHE_DIR.relative_to(ROOT).as_posix()}/ (fora do controle de versão; um .html e um .json por consulta × mês)",
        "cegamento": "nada foi calculado por IVS, faixa da bolsa, lado de corte ou tratamento; o IVS não é lido",
    }
    for nome, path, df in (("painel", PAINEL_FILE, res["painel"]), ("carater", CARATER_FILE, res["carater"]),
                           ("ignorados", IGNORADOS_FILE, res["ignorados"])):
        manifesto["saidas"][nome] = {
            "arquivo": path.relative_to(ROOT).as_posix(), "sha256": sha256_arquivo(path), "linhas": int(len(df)),
            "colunas": list(df.columns),
            "contagem_status": {k: int(v) for k, v in df["status"].value_counts().sort_index().items()},
        }
    manifesto["saidas"]["resumo"] = {"arquivo": RESUMO_FILE.relative_to(ROOT).as_posix()}
    MANIFESTO_FILE.write_text(json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifesto


def gravar_resumo(res: dict[str, Any]) -> None:
    val = res["validacoes"]
    painel = res["painel"]
    ok = lambda b: "—" if b is None else ("ok" if b else "FALHA")  # noqa: E731
    linhas = [
        "# A15 — resumo gerado do SIH/SUS por local de residência (TabNet)",
        "",
        f"Gerado por `scripts/aquisicao/a15_adquirir_sih_residencia.py` em {dt.date.today().isoformat()}. "
        "Não editar à mão. Natureza dos dados: EMPIRICO. Totais nacionais e por UF apenas; nada por IVS, "
        "faixa ou lado de corte.",
        "",
        f"Status das validações: **{val['status']}**. Universo: {val['universo_municipios_formulario']} municípios "
        "(lista do formulário do TabNet).",
        "",
        "## UF-mês sem arquivo de internação (NaN no painel, nunca zero nem parcial)",
        "",
        val["regra_uf_mes_sem_arquivo_internacao"] + ".",
        "",
    ]
    if val["uf_meses_sem_arquivo_internacao"]:
        linhas += ["| Competência | UF | AIH parciais (residentes internados em outra UF), fora do painel |",
                   "|---|---|---:|"]
        linhas += [f"| {r['competencia']} | {r['sigla']} ({r['uf']}) | {r['aih_residentes_internados_em_outra_uf_parcial']} |"
                   for r in val["uf_meses_sem_arquivo_internacao"]]
    else:
        linhas.append("Nenhum.")
    linhas += ["", "## UF-mês de residência com total zero (NaN no painel)", ""]
    if val["uf_meses_sem_dado"]:
        linhas += ["| Competência | UF |", "|---|---|"]
        linhas += [f"| {r['competencia']} | {r['sigla']} ({r['uf']}) |" for r in val["uf_meses_sem_dado"]]
    else:
        linhas.append("Nenhum.")
    linhas += ["", f"## UF-mês atípico (alerta; valor mantido): {val['regra_uf_mes_atipico']}", ""]
    if val["uf_meses_atipicos"]:
        linhas += ["| Competência | UF | AIH da UF (internação) | AIH da UF (residência) | Mediana mensal (internação) | Fração |",
                   "|---|---|---:|---:|---:|---:|"]
        linhas += [f"| {r['competencia']} | {r['sigla']} | {r['aih_total_uf_internacao']} | {r['aih_total_uf_residencia']} | "
                   f"{r['mediana_mensal_uf_internacao']:.0f} | {r['fracao_da_mediana']:.3f} |" for r in val["uf_meses_atipicos"]]
    else:
        linhas.append("Nenhum.")
    comp_a13 = val["comparacao_a13"]
    linhas += [
        "",
        "## Comparação com o a13 (total nacional de AIH aprovadas)",
        "",
        f"Validações do a13 lidas: SHA-256 `{comp_a13['a13_validacoes_sha256'][:16]}…`. "
        f"Meses iguais ao a13: {len(comp_a13['meses_iguais'])}. "
        f"Meses revistos pela fonte depois da extração do a13: {', '.join(comp_a13['meses_revisados_na_fonte']) or 'nenhum'}.",
        "",
    ]
    if comp_a13["meses_revisados_na_fonte"]:
        linhas += ["| Competência | Total a13 (versionado) | Total por residência | Total por internação (mesma execução) | Diferença |",
                   "|---|---:|---:|---:|---:|"]
        for c in comp_a13["meses_revisados_na_fonte"]:
            d = comp_a13["por_competencia"][c]
            linhas.append(f"| {c} | {d['total_a13']['total']} | {d['total_residencia']['total']} | "
                          f"{d['total_internacao_contemporaneo']['total']} | {d['diferenca_total_residencia_menos_a13']:+d} |")
    grupos = val["grupos_painel"]
    linhas += [
        "",
        "## Totais nacionais de AIH aprovadas por mês de processamento e grupo",
        "",
        "Total do próprio TabNet (inclui município ignorado e exterior). Validações v1–v9 em `a15_validacoes.json`.",
        "",
        "| Competência | " + " | ".join(f"Grupo {g}" for g in grupos) + " | Total | Municípios com AIH | "
        "Municípios com AIH do grupo 04 | v1 | v2 | v3 | v4 | v5 | v6 | v7 | v8 | v9 |",
        "|---|" + "---:|" * (len(grupos) + 3) + "---|" * 9,
    ]
    for c, v in val["por_competencia"].items():
        t = v["total_aih_por_grupo"]
        v6 = all(x["identicas"] for x in v["v6_uf_pequena_celula_a_celula"].values())
        v9 = {"igual_a13": "igual", "revisado_na_fonte_depois_do_a13": "revisado"}.get(v["v9_situacao_frente_ao_a13"], "FALHA")
        if v["v9_internacoes_valor_iguais_a13"] is False:
            v9 = "FALHA"
        linhas.append(
            f"| {c} | " + " | ".join(str(t.get(g, 0)) for g in grupos) + f" | {t['total']} | {v['municipios_com_aih']} | "
            f"{v['municipios_com_aih_g04']} | {ok(v['v1_soma_linhas_igual_total'])} | {ok(v['v2_total_mun_uf_procmes'])} | "
            f"{ok(v['v3_soma_municipal_por_uf'])} | {ok(v['v4_mes_processamento'])} | {ok(v['v5_carater_soma_g04'])} | "
            f"{ok(v6)} | {ok(v['v7_universo_municipios'])} | {ok(v['v8_total_residencia_igual_internacao'])} | {v9} |"
        )
    contagem = painel["status"].value_counts().sort_index()
    linhas += ["", "## Status no painel principal", "", "| Status | Linhas |", "|---|---:|"]
    linhas += [f"| {k} | {int(n)} |" for k, n in contagem.items()]
    linhas += ["", "## Caráter do atendimento (grupo 04)", "", "| Código | Rótulo do TabNet |", "|---|---|"]
    linhas += [f"| {k} | {r} |" for k, r in sorted(val["carater_rotulos"].items())]
    if val["erros"]:
        linhas += ["", "## Erros", ""] + [f"- {e}" for e in val["erros"]]
    RESUMO_FILE.write_text("\n".join(linhas) + "\n", encoding="utf-8")


def etapa_consolidar() -> int:
    log(f"Consolidando {len(COMPETENCIAS)} competências × {len(CONSULTAS)} consultas do cache")
    res = consolidar(COMPETENCIAS)
    val = res["validacoes"]
    if val["status"] != "APROVADO":
        for e in val["erros"][:50]:
            log(f"VALIDAÇÃO REPROVADA: {e}")
        log("PORTÃO REPROVADO: nada gravado em output/")
        return 2
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    gravar_parquet(res["painel"], PAINEL_FILE)
    gravar_parquet(res["carater"], CARATER_FILE)
    gravar_parquet(res["ignorados"], IGNORADOS_FILE)
    VALIDACOES_FILE.write_text(json.dumps(val, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    gravar_resumo(res)
    gravar_manifesto(res)
    log(f"Painel: {len(res['painel']):,} linhas; caráter: {len(res['carater']):,}; ignorados: {len(res['ignorados']):,}")
    log(f"UF-mês sem arquivo de internação: {[(r['competencia'], r['sigla']) for r in val['uf_meses_sem_arquivo_internacao']]}")
    log(f"UF-mês de residência zerado: {[(r['competencia'], r['sigla']) for r in val['uf_meses_sem_dado']]}")
    log(f"UF-mês atípicos: {[(r['competencia'], r['sigla']) for r in val['uf_meses_atipicos']]}")
    log(f"Meses revistos pela fonte depois do a13: {val['comparacao_a13']['meses_revisados_na_fonte']}")
    return 0


# ---------------------------------------------------------------- verificação sem rede

def verificar_versionado() -> int:
    """Confere as saídas versionadas contra o manifesto, sem rede e sem gravar."""
    erros: list[str] = []
    if not MANIFESTO_FILE.exists():
        raise SystemExit(f"verificar: {MANIFESTO_FILE.relative_to(ROOT)} ausente; rode --etapa tudo")
    man = json.loads(MANIFESTO_FILE.read_text(encoding="utf-8"))
    colunas = {"painel": COLUNAS_PAINEL, "carater": COLUNAS_CARATER, "ignorados": COLUNAS_IGNORADOS}
    for nome, path in (("painel", PAINEL_FILE), ("carater", CARATER_FILE), ("ignorados", IGNORADOS_FILE)):
        reg = man.get("saidas", {}).get(nome, {})
        if not path.exists():
            erros.append(f"{path.relative_to(ROOT)} ausente")
            continue
        if sha256_arquivo(path) != reg.get("sha256"):
            erros.append(f"SHA-256 de {path.name} difere do manifesto")
        meta = pq.read_metadata(path)
        if meta.schema.to_arrow_schema().names != colunas[nome]:
            erros.append(f"colunas de {path.name} diferem do esperado")
        if meta.num_rows != reg.get("linhas"):
            erros.append(f"{path.name}: {meta.num_rows} linhas; manifesto registra {reg.get('linhas')}")
    if man.get("competencias_planejadas") != COMPETENCIAS:
        erros.append("plano de competências do script mudou desde a consolidação")
    if any(c >= LIMITE_EXCLUSIVO for c in man.get("competencias_planejadas", [])):
        erros.append("competência >= limite do ciclo 3 no manifesto")
    if not VALIDACOES_FILE.exists():
        erros.append(f"{VALIDACOES_FILE.relative_to(ROOT)} ausente")
    else:
        if sha256_arquivo(VALIDACOES_FILE) != man.get("validacoes", {}).get("sha256"):
            erros.append("SHA-256 das validações difere do manifesto")
        if json.loads(VALIDACOES_FILE.read_text(encoding="utf-8")).get("status") != "APROVADO":
            erros.append("validações não aprovadas")
    if erros:
        for e in erros:
            log(f"VERIFICAÇÃO REPROVADA: {e}")
        raise SystemExit("verificar: saídas versionadas do a15 não conferem; refaça com --etapa consolidar ou tudo")
    if A13_VALIDACOES.exists() and sha256_arquivo(A13_VALIDACOES) != man.get("comparacao_a13", {}).get("a13_validacoes_sha256"):
        # o a13 foi refeito depois do a15: a comparação v9 ficou velha (não invalida o painel por residência)
        log("AVISO: as validações do a13 mudaram desde a consolidação do a15; refaça o a15 para atualizar a v9")
    log(f"SIH por residência versionado conferido sem rede: {man['saidas']['painel']['linhas']:,} linhas no painel, "
        f"{len(COMPETENCIAS)} competências; nada gravado")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--etapa", choices=["verificar", "baixar", "consolidar", "tudo"], default="verificar",
                    help="verificar (padrão): confere as saídas versionadas sem rede; baixar: formulários e "
                         "respostas para o cache; consolidar: valida e grava a partir do cache; tudo: os dois")
    ap.add_argument("--competencias", nargs="*", help="subconjunto para --etapa baixar (depuração)")
    ap.add_argument("--consultas", nargs="*", choices=sorted(CONSULTAS), help="subconjunto para --etapa baixar")
    args = ap.parse_args()
    if args.etapa == "verificar":
        if args.competencias or args.consultas:
            raise SystemExit("--competencias/--consultas não se aplicam a --etapa verificar")
        return verificar_versionado()
    if args.etapa in ("baixar", "tudo"):
        comps = sorted(args.competencias) if args.competencias else COMPETENCIAS
        for c in comps:
            checar_limite(c)
            if c not in COMPETENCIAS:
                raise SystemExit(f"competência fora do plano: {c}")
        t0 = time.time()
        r = etapa_baixar(comps, args.consultas or list(CONSULTAS))
        log(f"Download: {r['contagem']}, {len(r['falhas'])} falhas, {time.time() - t0:.0f}s")
        if r["falhas"]:
            for k, e in r["falhas"].items():
                log(f"FALHA {k}: {e}")
            return 3
        if args.etapa == "baixar":
            return 0
    if args.competencias or args.consultas:
        raise SystemExit("consolidar usa sempre o plano completo; não passe subconjuntos")
    return etapa_consolidar()


if __name__ == "__main__":
    sys.exit(main())
