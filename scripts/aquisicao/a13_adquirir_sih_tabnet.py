"""a13_adquirir_sih_tabnet.py — SIH/SUS no TabNet: AIH por município de internação × mês × grupo.

Tarefa de aquisição SIH do protocolo de produção especializada
(``docs/06_execucao/47_protocolo_producao_especializada.md``, §2, §6 e §9),
insumo da primária K2 (cirurgias SUS hospitalares, AIH do grupo 04).

Fonte: TabNet/DATASUS, "Procedimentos hospitalares do SUS - por local de
internação - Brasil" (``sih/cnv/qibr.def``), só por HTTP. O formulário
(``deftohtm.exe``) é baixado e lido; os nomes dos campos e os valores das
opções (Linha, Coluna, Incremento, Arquivos e filtros S*) saem dele, e não são
digitados. As consultas são POSTs a ``tabcgi.exe`` em latin-1, com
``formato=prn``, ``zeradas=exibirlz`` e ``mostre=Mostra``.

Unidade de tempo: o arquivo mensal ``qibrAAMM.dbf`` do campo "Arquivos", que é o
**mês de processamento** da AIH (o mesmo conceito do SIA no TabNet). Cada arquivo
é conferido contra a linha "Ano/mês processamento" da própria fonte.

Consultas, uma por arquivo mensal (202201 a 202607; nada >= 202609 é pedido):
- ``mun_grupo_aih``, ``mun_grupo_internacoes``, ``mun_grupo_valor``: município ×
  grupo do procedimento principal, com os incrementos AIH aprovadas, Internações
  e Valor total;
- ``uf_grupo_aih``: UF × grupo (conferência e detecção de UF-mês sem dado);
- ``procmes_grupo_aih``: ano/mês de processamento × grupo (conceito de tempo e
  total nacional);
- ``mun_carater_g04_aih``: município × caráter do atendimento, só grupo 04
  (painel opcional eletivo × urgência);
- ``mun_grupo_aih_uf_AC`` e ``mun_grupo_aih_uf_RR``: a mesma tabela municipal
  filtrada por UF, para a conferência célula a célula de UF pequena.

Regras de integridade (fail closed): ``-`` do TabNet é zero (legenda da própria
página); UF com total zero num mês é UF-mês sem dado na fonte (arquivo da UF
ausente no processamento), e seus municípios ficam ausentes (NaN) com motivo,
nunca zero; "município ignorado" de cada UF e "Ignorado ou exterior" ficam numa
tabela própria; qualquer consulta ausente, resposta fora do formato ou conferência
reprovada impede a gravação das saídas canônicas.

Cegamento: este script não lê IVS, faixa da bolsa, lado de corte ou tratamento.
O universo de municípios é a lista do próprio formulário do TabNet.

Modos (``--etapa``): ``verificar`` (padrão, usado pelo ``run_all.py``) só confere
os painéis versionados contra o manifesto, sem rede e sem gravar; ``baixar``
busca o formulário e as respostas para o cache (fora do Git); ``consolidar``
monta, valida e grava as saídas a partir do cache, sem rede; ``tudo`` faz os dois.

Saídas (``output/aquisicao/sih/``):
- ``painel_sih_municipio_mes_grupo.parquet``;
- ``painel_sih_municipio_mes_carater_g04.parquet``;
- ``ignorados_sih_uf_mes_grupo.parquet``;
- ``a13_validacoes.json``, ``a13_resumo.md``, ``manifesto_sih.json``;
- ``cache_tabnet/`` (respostas brutas e metadados; ignorado pelo Git).
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
OUT_DIR = ROOT / "output" / "aquisicao" / "sih"
CACHE_DIR = OUT_DIR / "cache_tabnet"
FORM_FILE = CACHE_DIR / "formulario_qibr.html"
FORM_META = CACHE_DIR / "formulario_qibr.json"
PAINEL_FILE = OUT_DIR / "painel_sih_municipio_mes_grupo.parquet"
CARATER_FILE = OUT_DIR / "painel_sih_municipio_mes_carater_g04.parquet"
IGNORADOS_FILE = OUT_DIR / "ignorados_sih_uf_mes_grupo.parquet"
VALIDACOES_FILE = OUT_DIR / "a13_validacoes.json"
RESUMO_FILE = OUT_DIR / "a13_resumo.md"
MANIFESTO_FILE = OUT_DIR / "manifesto_sih.json"

URL_FORM = "http://tabnet.datasus.gov.br/cgi/deftohtm.exe?sih/cnv/qibr.def"
URL_TAB = "http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sih/cnv/qibr.def"
ENCODING = "latin-1"

# Protocolo 47, §6: SIA e SIH lidos até 202607; ciclo 3: nada >= 202609.
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
LINHA = {"municipio": "Município", "uf": "UF", "procmes": "Ano/mês processamento"}
COLUNA = {"grupo": "Grupo procedimento", "carater": "Caráter atendimento"}
INCREMENTO = {"aih": "AIH aprovadas", "internacoes": "Internações", "valor": "Valor total"}
GRUPO_CIRURGICO_ROTULO = "04 Procedimentos cirurgicos"

# Consulta -> (linha, coluna, incremento, filtros {select: rótulo da opção}).
CONSULTAS: dict[str, dict[str, Any]] = {
    "mun_grupo_aih": {"linha": "municipio", "coluna": "grupo", "incremento": "aih", "filtros": {}},
    "mun_grupo_internacoes": {"linha": "municipio", "coluna": "grupo", "incremento": "internacoes", "filtros": {}},
    "mun_grupo_valor": {"linha": "municipio", "coluna": "grupo", "incremento": "valor", "filtros": {}},
    "uf_grupo_aih": {"linha": "uf", "coluna": "grupo", "incremento": "aih", "filtros": {}},
    "procmes_grupo_aih": {"linha": "procmes", "coluna": "grupo", "incremento": "aih", "filtros": {}},
    "mun_carater_g04_aih": {"linha": "municipio", "coluna": "carater", "incremento": "aih",
                            "filtros": {"SGrupo_procedimento": GRUPO_CIRURGICO_ROTULO}},
    "mun_grupo_aih_uf_AC": {"linha": "municipio", "coluna": "grupo", "incremento": "aih",
                            "filtros": {"SUF": "12 Acre"}},
    "mun_grupo_aih_uf_RR": {"linha": "municipio", "coluna": "grupo", "incremento": "aih",
                            "filtros": {"SUF": "14 Roraima"}},
}
UFS_CONFERENCIA_CELULA = {"mun_grupo_aih_uf_AC": "12", "mun_grupo_aih_uf_RR": "14"}

# Regra de UF-mês atípico (alerta, não altera valor): total de AIH da UF no mês
# abaixo desta fração da mediana mensal da UF no período. Fixada depois de ver a
# tabela nacional UF × mês da própria fonte, sem nenhum dado por IVS ou corte.
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
        "a UF tem total zero no mês: arquivo da UF ausente do processamento publicado; "
        "valor ausente (NaN), nunca zero"
    ),
}
COLUNAS_PAINEL = [
    "co_ibge", "uf", "competencia", "grupo", "aih_aprovadas", "internacoes", "valor_total",
    "status", "uf_mes_atipico", "natureza_dos_dados",
]
COLUNAS_CARATER = [
    "co_ibge", "uf", "competencia", "grupo", "carater", "aih_aprovadas", "status",
    "uf_mes_atipico", "natureza_dos_dados",
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
    return sha256_bytes(path.read_bytes())


def checar_limite(comp: str) -> None:
    if comp >= LIMITE_EXCLUSIVO:
        raise RuntimeError(f"Competência {comp} >= {LIMITE_EXCLUSIVO} é vedada (ciclo 3).")
    if comp > COMPETENCIA_FINAL:
        raise RuntimeError(f"Competência {comp} > {COMPETENCIA_FINAL}: protocolo 47 lê SIH até {COMPETENCIA_FINAL}.")


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

def ler_formulario(texto: str) -> dict[str, list[dict[str, Any]]]:
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
    if not re.search(r'ACTION="/cgi/tabcgi\.exe\?sih/cnv/qibr\.def"', texto, re.I):
        raise RuntimeError("formulário não aponta para tabcgi.exe?sih/cnv/qibr.def")
    return selects


def valor_da_opcao(selects: dict[str, list[dict[str, Any]]], campo: str, rotulo: str) -> str:
    achados = [o["valor"] for o in selects.get(campo, []) if o["rotulo"] == rotulo]
    if len(achados) != 1:
        raise RuntimeError(f"opção '{rotulo}' não encontrada (ou ambígua) no campo {campo} do formulário")
    return achados[0]


def arquivo_do_mes(selects: dict[str, list[dict[str, Any]]], comp: str) -> str:
    valor = valor_da_opcao(selects, "Arquivos", rotulo_mes(comp))
    if valor.lower() != f"qibr{comp[2:]}.dbf":
        raise RuntimeError(f"Arquivos: '{rotulo_mes(comp)}' aponta para {valor}, não para qibr{comp[2:]}.dbf")
    return valor


def montar_corpo(selects: dict[str, list[dict[str, Any]]], consulta: str, comp: str) -> str:
    """Corpo do POST: campos e valores lidos do formulário, codificados em latin-1."""
    checar_limite(comp)
    spec = CONSULTAS[consulta]
    pares: list[tuple[str, str]] = [
        ("Linha", valor_da_opcao(selects, "Linha", LINHA[spec["linha"]])),
        ("Coluna", valor_da_opcao(selects, "Coluna", COLUNA[spec["coluna"]])),
        ("Incremento", valor_da_opcao(selects, "Incremento", INCREMENTO[spec["incremento"]])),
        ("Arquivos", arquivo_do_mes(selects, comp)),
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


def baixar_formulario() -> dict[str, Any]:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    corpo, status = _http(URL_FORM, None, 120)
    ler_formulario(corpo.decode(ENCODING))  # falha se não for o formulário
    FORM_FILE.write_bytes(corpo)
    meta = {
        "url": URL_FORM, "metodo": "GET", "http_status": status,
        "data_hora_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "sha256": sha256_bytes(corpo), "bytes": len(corpo),
    }
    FORM_META.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    log(f"formulário: {len(corpo):,} bytes, SHA-256 {meta['sha256'][:12]}")
    return meta


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


def baixar_consulta(selects: dict[str, list[dict[str, Any]]], consulta: str, comp: str,
                    tentativas: int = 4, timeout: int = 300) -> str:
    corpo = montar_corpo(selects, consulta, comp)
    if cache_valido(consulta, comp, corpo):
        return "cache"
    destino = caminho_resposta(consulta, comp)
    destino.parent.mkdir(parents=True, exist_ok=True)
    erro = ""
    for t in range(1, tentativas + 1):
        t0 = time.time()
        try:
            bruto, status = _http(URL_TAB, corpo, timeout)
            texto = bruto.decode(ENCODING)
            ler_tabela(texto, consulta, comp)  # resposta fora do formato não entra no cache
        except Exception as exc:  # noqa: BLE001
            erro = f"{type(exc).__name__}: {exc}"
            log(f"  {consulta} {comp}: falha na tentativa {t}/{tentativas} ({erro})")
            time.sleep(min(10 * 2 ** (t - 1), 120))
            continue
        destino.write_bytes(bruto)
        meta = {
            "consulta": consulta, "competencia": comp, "url": URL_TAB, "metodo": "POST",
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
    baixar_formulario()
    selects = ler_formulario(FORM_FILE.read_bytes().decode(ENCODING))
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
    """Lê a tabela 'prn' (entre <PRE> e </PRE>) e confere cabeçalho, período, filtro e totais.

    Devolve as colunas (rótulos), as linhas (rótulo, valores, eh_zero) e a linha Total.
    """
    spec = CONSULTAS[consulta]
    if "<PRE>" not in texto or "</PRE>" not in texto:
        raise RuntimeError("resposta sem tabela <PRE>")
    cabeca, resto = texto.split("<PRE>", 1)
    bloco = resto.split("</PRE>", 1)[0]
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


# ---------------------------------------------------------------- consolidação

def consolidar(competencias: list[str]) -> dict[str, Any]:
    if not FORM_FILE.exists() or not FORM_META.exists():
        raise RuntimeError("formulário ausente do cache; rode --etapa baixar")
    form_meta = json.loads(FORM_META.read_text(encoding="utf-8"))
    if sha256_arquivo(FORM_FILE) != form_meta["sha256"]:
        raise RuntimeError("SHA-256 do formulário em cache difere do metadado")
    selects = ler_formulario(FORM_FILE.read_bytes().decode(ENCODING))
    universo = universo_do_formulario(selects)
    for comp in competencias:
        arquivo_do_mes(selects, comp)  # o mês existe no formulário

    erros: list[str] = []
    val: dict[str, Any] = {"por_competencia": {}}
    partes_mun, partes_ign, partes_car = [], [], []
    totais_uf: dict[str, dict[str, int]] = {}
    grupos_por_mes: dict[str, list[str]] = {}
    carater_rotulos: dict[str, str] = {}
    consultas_meta: list[dict[str, Any]] = []
    notas: set[str] = set()

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
        for c in ("mun_grupo_internacoes", "mun_grupo_valor", "uf_grupo_aih", "procmes_grupo_aih"):
            g_c = [grupo_do_rotulo(x) for x in tabs[c]["colunas"]]
            if c != "mun_grupo_internacoes" and c != "mun_grupo_valor" and g_c != grupos:
                erros.append(f"{comp}: grupos de {c} {g_c} diferem de mun_grupo_aih {grupos}")

        # V2: Total nacional do município = UF = processamento (AIH)
        t_mun, t_uf, t_pm = tabs["mun_grupo_aih"]["total"], tabs["uf_grupo_aih"]["total"], pm["total"]
        linha_pm = [valores for r, valores, _ in pm["linhas"] if r == rotulo_procmes(comp)]
        v["v2_total_mun_uf_procmes"] = t_mun == t_uf == t_pm and linha_pm == [t_pm]
        if not v["v2_total_mun_uf_procmes"]:
            erros.append(f"{comp}: Total municipal {t_mun}, UF {t_uf}, processamento {t_pm} diferem")
        v["total_aih_por_grupo"] = dict(zip(grupos + ["total"], t_mun))

        # Tabelas longas
        longas = {
            "aih": tabela_longa(tabs["mun_grupo_aih"], "grupo"),
            "internacoes": tabela_longa(tabs["mun_grupo_internacoes"], "grupo"),
            "valor": tabela_longa(tabs["mun_grupo_valor"], "grupo"),
        }
        # V7: universo do formulário = municípios de cada resposta
        for k, df in list(longas.items()) + [("carater", tabela_longa(tabs["mun_carater_g04_aih"], "carater"))]:
            cods = sorted(df.loc[df["tipo"] == "municipio", "chave"].unique())
            if cods != universo:
                faltam = sorted(set(universo) - set(cods))[:10]
                sobram = sorted(set(cods) - set(universo))[:10]
                erros.append(f"{comp} {k}: municípios da resposta diferem do formulário (faltam {faltam}, sobram {sobram})")
        v["v7_universo_municipios"] = not any(e.startswith(f"{comp} ") and "municípios da resposta" in e for e in erros)

        # V3: soma municipal (municípios + ignorado da UF) por UF × grupo = linha da UF
        aih = longas["aih"]
        uf_tab = {}
        for rotulo, valores, _ in tabs["uf_grupo_aih"]["linhas"]:
            cod = rotulo[:2]
            uf_tab[cod] = dict(zip(grupos + ["total"], valores))
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
        for k, c in (("aih", "mun_grupo_aih"), ("internacoes", "mun_grupo_internacoes"), ("valor", "mun_grupo_valor")):
            cols = [grupo_do_rotulo(x) for x in tabs[c]["colunas"]]
            s = longas[k].groupby("categoria")["valor"].sum()
            for j, g in enumerate(cols):
                tol = 0.011 * len(universo) if k == "valor" else 0
                if abs(float(s.get(g, 0)) - tabs[c]["total"][j]) > tol:
                    ok1 = False
                    erros.append(f"{comp} {k}: soma das linhas do grupo {g} ≠ Total")
        v["v1_soma_linhas_igual_total"] = ok1

        totais_uf[comp] = {cod: d["total"] for cod, d in uf_tab.items() if cod != "00"}
        faltam_ufs = sorted(set(UF_CODIGO_SIGLA) - set(totais_uf[comp]))
        if faltam_ufs:
            erros.append(f"{comp}: UFs sem linha na consulta por UF: {faltam_ufs}")

        # V5: caráter do grupo 04 soma o grupo 04 municipal
        car = tabela_longa(tabs["mun_carater_g04_aih"], "carater")
        for col in tabs["mun_carater_g04_aih"]["colunas"]:
            carater_rotulos[slug(col)] = col
        soma_car = car.groupby("chave")["valor"].sum()
        g04 = aih.loc[aih["categoria"] == "04"].set_index("chave")["valor"] if "04" in grupos else pd.Series(dtype=int)
        comp_car = pd.concat([soma_car.rename("car"), g04.rename("g04")], axis=1).fillna(0)
        v["v5_carater_soma_g04"] = bool((comp_car["car"] == comp_car["g04"]).all())
        if not v["v5_carater_soma_g04"]:
            erros.append(f"{comp}: soma por caráter difere do grupo 04 em {int((comp_car['car'] != comp_car['g04']).sum())} linhas")

        # V6: conferência célula a célula de UF pequena (consulta filtrada × nacional)
        v6 = {}
        nac_linhas = {}
        for rotulo, valores, _ in tabs["mun_grupo_aih"]["linhas"]:
            _, chave, _ = classificar_linha_municipal(rotulo)
            nac_linhas[chave] = dict(zip(grupos + ["total"], valores))
        for c, cod in UFS_CONFERENCIA_CELULA.items():
            # a consulta filtrada lista todas as linhas do país (exibirlz), com dado só na UF, e
            # só traz as colunas de grupo com dado na UF; grupo sem coluna tem de ser zero no nacional
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

    # UF-mês sem dado e UF-mês atípico
    tot = pd.DataFrame(totais_uf).T.sort_index()  # competência × UF
    ausentes = sorted((c, uf) for c in tot.index for uf in tot.columns if tot.loc[c, uf] == 0)
    medianas = tot.where(tot > 0).median()
    atipicos = sorted(
        (c, uf) for c in tot.index for uf in tot.columns
        if tot.loc[c, uf] > 0 and tot.loc[c, uf] < FRACAO_ATIPICO * medianas[uf]
    )
    set_aus, set_atip = set(ausentes), set(atipicos)

    # Grupos do painel: união das colunas devolvidas em algum mês
    grupos_painel = sorted({g for gs in grupos_por_mes.values() for g in gs})

    mun = pd.concat(partes_mun, ignore_index=True)
    obs = mun.loc[mun["tipo"] == "municipio"]
    esqueleto = pd.MultiIndex.from_product([universo, competencias, grupos_painel],
                                           names=["chave", "competencia", "categoria"]).to_frame(index=False)
    painel = esqueleto.merge(obs[["chave", "competencia", "categoria", "aih_aprovadas", "aih_zero",
                                  "internacoes", "valor"]],
                             on=["chave", "competencia", "categoria"], how="left", validate="one_to_one")
    omitida = painel["aih_aprovadas"].isna()  # grupo sem coluna no mês: zero (V1/V9 conferem o Total)
    painel["status"] = np.where(omitida, "zero_coluna_omitida",
                                np.where(painel["aih_zero"].fillna(False).astype(bool), "zero_tabnet", "observado"))
    for col in ("aih_aprovadas", "internacoes"):
        painel[col] = painel[col].fillna(0).astype("Int64")
    painel["valor"] = painel["valor"].fillna(0.0).astype(float)
    painel = painel.rename(columns={"chave": "co_ibge", "categoria": "grupo", "valor": "valor_total"})
    painel["uf"] = painel["co_ibge"].str[:2]
    chave_uf = list(zip(painel["competencia"], painel["uf"]))
    aus_mask = np.array([k in set_aus for k in chave_uf])
    painel.loc[aus_mask, ["aih_aprovadas", "internacoes"]] = pd.NA
    painel.loc[aus_mask, "valor_total"] = np.nan
    painel.loc[aus_mask, "status"] = "ausente_uf_mes_sem_dado"
    painel["uf_mes_atipico"] = np.array([k in set_atip for k in chave_uf])
    painel["natureza_dos_dados"] = "EMPIRICO"
    painel = painel[COLUNAS_PAINEL].sort_values(["co_ibge", "competencia", "grupo"], kind="mergesort").reset_index(drop=True)

    # Ignorados (município ignorado de cada UF e ignorado/exterior)
    ign = mun.loc[mun["tipo"] != "municipio"].copy()
    esq_i = pd.MultiIndex.from_product(
        [sorted(ign["chave"].unique()), competencias, grupos_painel], names=["chave", "competencia", "categoria"]
    ).to_frame(index=False)
    ign = esq_i.merge(ign[["chave", "uf", "competencia", "categoria", "aih_aprovadas", "aih_zero", "internacoes", "valor"]],
                      on=["chave", "competencia", "categoria"], how="left", validate="one_to_one")
    ign["uf"] = ign["chave"].map(lambda k: "00" if k == "000000" else UF_SIGLA_CODIGO[k.split("_")[1]])
    omit_i = ign["aih_aprovadas"].isna()
    ign["status"] = np.where(omit_i, "zero_coluna_omitida",
                             np.where(ign["aih_zero"].fillna(False).astype(bool), "zero_tabnet", "observado"))
    for col in ("aih_aprovadas", "internacoes"):
        ign[col] = ign[col].fillna(0).astype("Int64")
    ign["valor"] = ign["valor"].fillna(0.0).astype(float)
    aus_i = np.array([k in set_aus for k in zip(ign["competencia"], ign["uf"])])
    ign.loc[aus_i, ["aih_aprovadas", "internacoes"]] = pd.NA
    ign.loc[aus_i, "valor"] = np.nan
    ign.loc[aus_i, "status"] = "ausente_uf_mes_sem_dado"
    ign = ign.rename(columns={"chave": "linha_tabnet", "categoria": "grupo", "valor": "valor_total"})
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
    chave_c = list(zip(carp["competencia"], carp["uf"]))
    aus_c = np.array([k in set_aus for k in chave_c])
    carp.loc[aus_c, "aih_aprovadas"] = pd.NA
    carp.loc[aus_c, "status"] = "ausente_uf_mes_sem_dado"
    carp["uf_mes_atipico"] = np.array([k in set_atip for k in chave_c])
    carp["grupo"] = "04"
    carp["natureza_dos_dados"] = "EMPIRICO"
    carp = carp[COLUNAS_CARATER].sort_values(["co_ibge", "competencia", "carater"], kind="mergesort").reset_index(drop=True)

    # Consistência de UF-mês ausente: todos os incrementos da UF zerados no mês
    for c, uf in ausentes:
        sub = mun.loc[(mun["competencia"] == c) & (mun["uf"] == uf)]
        if (sub[["aih_aprovadas", "internacoes", "valor"]].abs().sum() != 0).any():
            erros.append(f"{c}: UF {uf} com AIH total zero mas outro incremento positivo")

    val["uf_meses_sem_dado"] = [{"competencia": c, "uf": uf, "sigla": UF_CODIGO_SIGLA[uf]} for c, uf in ausentes]
    val["uf_meses_atipicos"] = [
        {"competencia": c, "uf": uf, "sigla": UF_CODIGO_SIGLA[uf], "aih_total_uf": int(tot.loc[c, uf]),
         "mediana_mensal_uf": float(medianas[uf]), "fracao_da_mediana": round(float(tot.loc[c, uf] / medianas[uf]), 4)}
        for c, uf in atipicos
    ]
    val["regra_uf_mes_sem_dado"] = "total de AIH aprovadas da UF no mês igual a zero na consulta UF × grupo"
    val["regra_uf_mes_atipico"] = (
        f"total da UF no mês > 0 e < {FRACAO_ATIPICO} × mediana mensal da UF em {competencias[0]}–{competencias[-1]}; "
        "alerta (coluna uf_mes_atipico), o valor não é alterado"
    )
    val["grupos_por_competencia"] = grupos_por_mes
    val["grupos_painel"] = grupos_painel
    val["carater_rotulos"] = carater_rotulos
    val["universo_municipios_formulario"] = len(universo)
    val["totais_uf_mes_aih"] = {c: {UF_CODIGO_SIGLA[u]: int(x) for u, x in sorted(d.items())} for c, d in sorted(totais_uf.items())}
    val["erros"] = erros
    val["status"] = "APROVADO" if not erros else "REPROVADO"
    val["natureza_dos_dados"] = "EMPIRICO"
    return {
        "painel": painel, "ignorados": ign, "carater": carp, "validacoes": val, "universo": universo,
        "form_meta": form_meta, "consultas_meta": consultas_meta, "selects": selects, "notas": sorted(notas),
    }


# ---------------------------------------------------------------- gravação

def gravar_parquet(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tabela = pa.Table.from_pandas(df, preserve_index=False)
    pq.write_table(tabela, path, compression="zstd", compression_level=9, use_dictionary=True)


def _opcoes_usadas(selects: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    usado = {}
    for campo, rotulos in (("Linha", LINHA), ("Coluna", COLUNA), ("Incremento", INCREMENTO)):
        usado[campo] = {r: valor_da_opcao(selects, campo, r) for r in rotulos.values()}
    usado["filtros"] = {
        f"{c}={r}": valor_da_opcao(selects, c, r)
        for spec in CONSULTAS.values() for c, r in spec["filtros"].items()
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
    selects = res["selects"]
    sufixo = {c: f"qibr{c[2:]}.dbf" for c in COMPETENCIAS}
    manifesto = {
        "gerador": "scripts/aquisicao/a13_adquirir_sih_tabnet.py",
        "protocolo": "docs/06_execucao/47_protocolo_producao_especializada.md (§2, §6, §9; insumo de K2)",
        "natureza_dos_dados": "EMPIRICO",
        "data_execucao": dt.date.today().isoformat(),
        "fonte": {
            "nome": "SIH/SUS — Procedimentos hospitalares do SUS por local de internação, Brasil (TabNet/DATASUS)",
            "url_formulario": URL_FORM,
            "url_consulta": URL_TAB,
            "metodo": "POST application/x-www-form-urlencoded, latin-1; formato=prn, zeradas=exibirlz, mostre=Mostra",
            "formulario": {**res["form_meta"], "cache": FORM_FILE.relative_to(ROOT).as_posix()},
            "notas_da_fonte": res["notas"],
        },
        "conceito_de_tempo": (
            "mês de processamento da AIH: arquivo qibrAAMM.dbf do campo Arquivos; cada arquivo conferido "
            "contra a linha 'Ano/mês processamento' (validação v4). Não é o mês da internação nem da alta."
        ),
        "conceito_de_lugar": "município do estabelecimento de internação (local de internação), não de residência",
        "unidade": "município (co_ibge, 6 dígitos) × competência de processamento (AAAAMM) × grupo do procedimento principal (SIGTAP, 2 dígitos)",
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
        "opcoes_do_formulario_usadas": _opcoes_usadas(selects),
        "competencias_planejadas": COMPETENCIAS,
        "arquivos_planejados": sufixo,
        "limite_ciclo3": f"nenhuma competência >= {LIMITE_EXCLUSIVO} é pedida; protocolo 47 lê SIH até {COMPETENCIA_FINAL}",
        "universo_municipios": {
            "origem": "opções do filtro SMunicípio do formulário baixado (sem leitura de IVS)",
            "n": len(res["universo"]),
            "sha256_lista": sha256_bytes("\n".join(res["universo"]).encode()),
        },
        "status_vocabulario": STATUS,
        "regras": {
            "zero": "'-' do TabNet é zero (legenda da página); nada é preenchido com zero fora disso e da coluna omitida conferida",
            "uf_mes_sem_dado": val["regra_uf_mes_sem_dado"] + "; municípios e ignorado da UF ficam NaN com status ausente_uf_mes_sem_dado",
            "uf_mes_atipico": val["regra_uf_mes_atipico"],
            "ignorados": "MUNICIPIO IGNORADO - UF e 000000 Ignorado ou exterior ficam em ignorados_sih_uf_mes_grupo.parquet",
            "fail_closed": "qualquer resposta ausente, fora do formato ou conferência reprovada impede a gravação",
        },
        "uf_meses_sem_dado": val["uf_meses_sem_dado"],
        "uf_meses_atipicos": val["uf_meses_atipicos"],
        "saidas": {},
        "validacoes": {"arquivo": VALIDACOES_FILE.relative_to(ROOT).as_posix(), "status": val["status"],
                       "sha256": sha256_arquivo(VALIDACOES_FILE)},
        "consultas_realizadas": res["consultas_meta"],
        "cache_bruto": f"{CACHE_DIR.relative_to(ROOT).as_posix()}/ (ignorado pelo Git; um .html e um .json por consulta × mês)",
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
    linhas = [
        "# A13 — resumo gerado do SIH/SUS (TabNet)",
        "",
        f"Gerado por `scripts/aquisicao/a13_adquirir_sih_tabnet.py` em {dt.date.today().isoformat()}. "
        "Não editar à mão. Natureza dos dados: EMPIRICO. Totais nacionais e por UF apenas; nada por IVS, "
        "faixa ou lado de corte.",
        "",
        f"Status das validações: **{val['status']}**. Universo: {val['universo_municipios_formulario']} municípios "
        "(lista do formulário do TabNet).",
        "",
        "## UF-mês sem dado na fonte (NaN no painel, nunca zero)",
        "",
    ]
    if val["uf_meses_sem_dado"]:
        linhas += ["| Competência | UF |", "|---|---|"]
        linhas += [f"| {r['competencia']} | {r['sigla']} ({r['uf']}) |" for r in val["uf_meses_sem_dado"]]
    else:
        linhas.append("Nenhum.")
    linhas += ["", f"## UF-mês atípico (alerta; valor mantido): {val['regra_uf_mes_atipico']}", ""]
    if val["uf_meses_atipicos"]:
        linhas += ["| Competência | UF | AIH da UF | Mediana mensal da UF | Fração |", "|---|---|---:|---:|---:|"]
        linhas += [f"| {r['competencia']} | {r['sigla']} | {r['aih_total_uf']} | {r['mediana_mensal_uf']:.0f} | "
                   f"{r['fracao_da_mediana']:.3f} |" for r in val["uf_meses_atipicos"]]
    else:
        linhas.append("Nenhum.")
    grupos = val["grupos_painel"]
    linhas += [
        "",
        "## Totais nacionais de AIH aprovadas por mês de processamento e grupo",
        "",
        "Total do próprio TabNet (inclui município ignorado e exterior). Validações v1–v7 em `a13_validacoes.json`.",
        "",
        "| Competência | " + " | ".join(f"Grupo {g}" for g in grupos) + " | Total | Municípios com AIH | "
        "Municípios com AIH do grupo 04 | v1 | v2 | v3 | v4 | v5 | v6 | v7 |",
        "|---|" + "---:|" * (len(grupos) + 3) + "---|" * 7,
    ]
    for c, v in val["por_competencia"].items():
        t = v["total_aih_por_grupo"]
        ok = lambda b: "ok" if b else "FALHA"  # noqa: E731
        v6 = all(x["identicas"] for x in v["v6_uf_pequena_celula_a_celula"].values())
        linhas.append(
            f"| {c} | " + " | ".join(str(t.get(g, 0)) for g in grupos) + f" | {t['total']} | {v['municipios_com_aih']} | "
            f"{v['municipios_com_aih_g04']} | {ok(v['v1_soma_linhas_igual_total'])} | {ok(v['v2_total_mun_uf_procmes'])} | "
            f"{ok(v['v3_soma_municipal_por_uf'])} | {ok(v['v4_mes_processamento'])} | {ok(v['v5_carater_soma_g04'])} | "
            f"{ok(v6)} | {ok(v['v7_universo_municipios'])} |"
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
    log(f"UF-mês sem dado: {[(r['competencia'], r['sigla']) for r in val['uf_meses_sem_dado']]}")
    log(f"UF-mês atípicos: {[(r['competencia'], r['sigla']) for r in val['uf_meses_atipicos']]}")
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
        raise SystemExit("verificar: saídas versionadas do a13 não conferem; refaça com --etapa consolidar ou tudo")
    log(f"SIH versionado conferido sem rede: {man['saidas']['painel']['linhas']:,} linhas no painel, "
        f"{len(COMPETENCIAS)} competências; nada gravado")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--etapa", choices=["verificar", "baixar", "consolidar", "tudo"], default="verificar",
                    help="verificar (padrão): confere as saídas versionadas sem rede; baixar: formulário e "
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
