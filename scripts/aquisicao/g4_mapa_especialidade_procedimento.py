"""g4_mapa_especialidade_procedimento.py — portão G4: mapa curso do PMM-E → procedimentos SIGTAP típicos.

Portão G4 do plano das perguntas reformuladas
(``docs/06_execucao/51_plano_perguntas_reformuladas.md``, P3, T3.2). Só verifica
viabilidade e monta o mapa; não abre nenhum outcome e não calcula nada por IVS,
faixa da bolsa, lado de corte, tratamento ou chegada.

Duas fontes, nesta ordem:

1. **SIGTAP, compatibilidade procedimento × ocupação** (``rl_procedimento_ocupacao``
   do ZIP ``TabelaUnificada_AAAAMM_v*.zip``). O script sonda a página de download
   (``http://sigtap.datasus.gov.br/tabela-unificada/app/download.jsp``), o RSS de
   competências (que dá o nome do ZIP) e o FTP oficial
   (``ftp2.datasus.gov.br/pub/sistemas/tup/downloads``). Tudo o que responde
   (ou não) fica registrado, com data, status e SHA-256. Se o ZIP for obtido, a
   tabela é lida pelo layout que vem no próprio ZIP e marca, para cada forma de
   organização, se há procedimento compatível com a CBO do curso.
2. **Produção ambulatorial observada no TabNet do SIA** (``sia/cnv/qabr.def``, o
   mesmo formulário do a12): quantidade aprovada nacional por CBO médica × forma
   de organização, somada nos 12 meses de processamento de 2024 (antes das
   chegadas do PMM-E), e o total de todos os profissionais por forma. É o mapa
   "revelado": o que cada CBO de fato registra no SUS, não o que a regra permite.

Mapa: curso → CBO (ponte curso–CBO, ``output/aquisicao/ponte_curso_cbo_oficial.json``)
→ formas de organização com produção dessas CBO. Para cada curso e forma:
participação na produção das CBO do curso, participação acumulada (forma
"típica" = entre as que somam os primeiros ``LIMIAR_TIPICA`` da produção do
curso) e especificidade (participação das CBO do curso na produção médica e na
produção total da forma).

Teste de viabilidade do filtro (um mês, só totais nacionais): Linha = Município,
Coluna = Forma de organização, filtro Profissional - CBO = CBO-alvo do PMM-E, mês
de processamento ``MES_TESTE``. Confere que a consulta municipal responde, traz
todos os municípios do formulário e soma, por forma, o total nacional da mesma
consulta por CBO; e que a soma das formas por subgrupo reproduz o a12. As
respostas municipais ficam só no cache (fora do controle de versão); as saídas
guardam só totais nacionais e contagens estruturais.

Modos (``--etapa``): ``verificar`` (padrão) confere as saídas versionadas contra o
manifesto, sem rede e sem gravar; ``baixar`` sonda o SIGTAP e busca o formulário e
as respostas do TabNet para o cache; ``consolidar`` monta, valida e grava a partir
do cache, sem rede; ``tudo`` faz os dois.

Saídas:
- ``output/aquisicao/sigtap/sigtap_sondagem.json`` (tentativas de obter o SIGTAP);
- ``output/aquisicao/sigtap/g4_sia_nacional_cbo_forma_2024.csv`` (CBO médica × forma, nacional);
- ``output/aquisicao/sigtap/g4_sia_nacional_forma_2024.csv`` (forma: médicos e todos, nacional);
- ``output/aquisicao/sigtap/g4_teste_filtro_totais_nacionais.csv`` (teste de um mês, nacional);
- ``output/aquisicao/sigtap/manifesto_g4.json``;
- ``output/rdd_bolsa/G4_mapa_especialidade_procedimento.csv`` (curso × forma);
- ``output/rdd_bolsa/G4_mapa_especialidade_subgrupo.csv`` (curso × subgrupo);
- ``output/rdd_bolsa/G4_resumo.json`` (cobertura, especificidade, viabilidade e veredito);
- ``output/aquisicao/sigtap/cache/`` (respostas brutas; fora do controle de versão).
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import ftplib
import gzip
import hashlib
import html
import io
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT_AQ = ROOT / "output" / "aquisicao" / "sigtap"
CACHE_DIR = OUT_AQ / "cache"
OUT_RDD = ROOT / "output" / "rdd_bolsa"
SONDAGEM_FILE = OUT_AQ / "sigtap_sondagem.json"
CBO_FORMA_FILE = OUT_AQ / "g4_sia_nacional_cbo_forma_2024.csv"
FORMA_FILE = OUT_AQ / "g4_sia_nacional_forma_2024.csv"
TESTE_FILE = OUT_AQ / "g4_teste_filtro_totais_nacionais.csv"
MANIFESTO_FILE = OUT_AQ / "manifesto_g4.json"
MAPA_FILE = OUT_RDD / "G4_mapa_especialidade_procedimento.csv"
MAPA_SUBGRUPO_FILE = OUT_RDD / "G4_mapa_especialidade_subgrupo.csv"
RESUMO_FILE = OUT_RDD / "G4_resumo.json"

PONTE_FILE = ROOT / "output" / "aquisicao" / "ponte_curso_cbo_oficial.json"
A12_SUBGRUPOS_FILE = ROOT / "output" / "aquisicao" / "sia" / "sia_subgrupos_por_consulta.csv"

URL_SIGTAP_DOWNLOAD = "http://sigtap.datasus.gov.br/tabela-unificada/app/download.jsp"
URL_SIGTAP_RSS = "http://sigtap.datasus.gov.br/tabela-unificada/competencias.rss"
FTP_SIGTAP_HOST = "ftp2.datasus.gov.br"
FTP_SIGTAP_DIR = "/pub/sistemas/tup/downloads"
# Competência do SIGTAP alinhada ao fim da janela do mapa (procedimentos vigentes em dez/2024).
COMPETENCIA_SIGTAP = "202412"

URL_FORM = "http://tabnet.datasus.gov.br/cgi/deftohtm.exe?sia/cnv/qabr.def"
URL_TAB = "http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sia/cnv/qabr.def"
ENCODING = "latin-1"
TIMEOUT = 600
TENTATIVAS = 4
PAUSA = 1.5

# Janela do mapa: os 12 meses de processamento de 2024, antes das chegadas do PMM-E
# (ciclo 1 em 2025). Mês do teste de viabilidade: 202406 (maduro, já no a12).
MESES_MAPA = [f"2024{m:02d}" for m in range(1, 13)]
MES_TESTE = "202406"
LIMITE_EXCLUSIVO = "202609"

# Regras do mapa, fixadas antes de ler as respostas (nenhuma depende de IVS ou de outcome).
LIMIAR_TIPICA = 0.80          # formas que somam os primeiros 80% da produção das CBO do curso
LIMIAR_ESPEC_ALTA = 0.50      # CBO do curso fazem >= 50% da produção médica da forma
LIMIAR_ESPEC_MEDIA = 0.20     # entre 20% e 50%: média; abaixo: baixa
PREFIXOS_CBO_MEDICO = ("2251", "2252", "2253", "2231")
# Classificação do curso (descritiva; fixada depois de ver só o mapa nacional de 2024, sem IVS nem
# outcome): participação da produção das CBO do curso em formas de especificidade alta (e média).
LIMIAR_CURSO_ESPECIFICO = 0.20   # >= 20% da produção em formas de especificidade alta
LIMIAR_PARTICIPACAO_RELEVANTE = 0.01  # forma específica relevante: >= 1% da produção do curso

MESES_PT = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
NATUREZA = "EMPIRICO"
RE_FORMA = re.compile(r"^(\d{6}) (.+)$")
RE_CBO = re.compile(r"^([0-9A-Z]{6}) (.+)$")
RE_MUNICIPIO = re.compile(r"^(\d{6}) (.+)$")
RE_IGNORADO = re.compile(r"^(MUNICIPIO IGNORADO - [A-Z]{2}|000000 .+)$")

COLUNAS_MAPA = [
    "cod_curso", "no_curso", "cbos_curso", "grau_univocidade_ponte", "co_grupo", "co_subgrupo", "co_forma",
    "no_forma", "qtd_aprovada_cbo_curso", "participacao_na_producao_do_curso", "participacao_acumulada",
    "ordem_no_curso", "tipica", "qtd_aprovada_medicos", "qtd_aprovada_todos", "especificidade_medicos",
    "especificidade_todos", "classe_especificidade", "compatibilidade_sigtap", "janela_producao", "fonte_mapa",
    "natureza_dos_dados",
]
COLUNAS_SUBGRUPO = [
    "cod_curso", "no_curso", "cbos_curso", "co_grupo", "co_subgrupo", "qtd_aprovada_cbo_curso",
    "participacao_na_producao_do_curso", "n_formas_com_producao", "n_formas_tipicas", "qtd_aprovada_medicos",
    "qtd_aprovada_todos", "especificidade_medicos", "especificidade_todos", "classe_especificidade",
    "janela_producao", "fonte_mapa", "natureza_dos_dados",
]


class ErroResposta(RuntimeError):
    pass


def log(msg: str) -> None:
    print(f"[{dt.datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def agora() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_arquivo(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def checar_limite(comp: str) -> None:
    if comp >= LIMITE_EXCLUSIVO:
        raise RuntimeError(f"Competência {comp} >= {LIMITE_EXCLUSIVO} é vedada (ciclo 3).")


def rotulo_mes(comp: str) -> str:
    return f"{MESES_PT[int(comp[4:]) - 1]}/{comp[:4]}"


def classe_especificidade(x: float | None) -> str:
    if x is None or pd.isna(x):
        return "sem_producao_medica"
    if x >= LIMIAR_ESPEC_ALTA:
        return "alta"
    if x >= LIMIAR_ESPEC_MEDIA:
        return "media"
    return "baixa"


# ---------------------------------------------------------------- ponte curso–CBO

def carregar_ponte() -> tuple[list[dict[str, Any]], str]:
    raw = json.loads(PONTE_FILE.read_text(encoding="utf-8"))
    cursos = []
    for c in raw["catalogo_cursos"]:
        cursos.append({
            "cod_curso": int(c["cod_curso"]), "no_curso": c["no_curso_padronizado"],
            "cbos": sorted(str(x).zfill(6) for x in c["cbos_elegiveis"]),
            "grau_univocidade": c.get("grau_univocidade", ""),
        })
    if len(cursos) != raw["total_cursos_pmme"]:
        raise RuntimeError("ponte: número de cursos difere do declarado")
    return sorted(cursos, key=lambda c: c["cod_curso"]), sha256_arquivo(PONTE_FILE)


# ---------------------------------------------------------------- SIGTAP (fonte normativa)

def _http_get(url: str, timeout: int = 60) -> tuple[bytes, int, str | None]:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read(), resp.status, resp.headers.get("Content-Type")


def ler_rss_competencias(texto: str) -> list[dict[str, str]]:
    """Itens do RSS de competências do SIGTAP: título, link do ZIP e data."""
    itens = []
    for m in re.finditer(r"<item>(.*?)</item>", texto, re.S):
        titulo = re.search(r"<title>(.*?)</title>", m.group(1), re.S)
        link = re.search(r"<link>(.*?)</link>", m.group(1), re.S)
        data = re.search(r"<pubDate>(.*?)</pubDate>", m.group(1), re.S)
        itens.append({"titulo": titulo.group(1).strip() if titulo else "",
                      "link": link.group(1).strip() if link else "",
                      "pub_date": data.group(1).strip() if data else ""})
    return itens


def ler_layout_sigtap(raw: bytes) -> dict[str, tuple[int, int]]:
    """Layout do SIGTAP (CSV 'Coluna,Tamanho,Inicio,Fim,Tipo'): nome -> (início 0-based, fim exclusivo)."""
    texto = raw.decode("latin-1")
    saida = {}
    for linha in csv.DictReader(io.StringIO(texto)):
        nome = (linha.get("Coluna") or "").strip().upper()
        if nome:
            saida[nome] = (int(linha["Inicio"]) - 1, int(linha["Fim"]))
    return saida


def ler_rl_procedimento_ocupacao(zbytes: bytes) -> pd.DataFrame:
    """Lê ``rl_procedimento_ocupacao`` de um ZIP da Tabela Unificada, pelo layout do próprio ZIP."""
    with zipfile.ZipFile(io.BytesIO(zbytes)) as z:
        nomes = {n.lower(): n for n in z.namelist()}
        tab = nomes.get("rl_procedimento_ocupacao.txt")
        lay = nomes.get("rl_procedimento_ocupacao_layout.txt")
        if not tab or not lay:
            raise ErroResposta("ZIP do SIGTAP sem rl_procedimento_ocupacao(.txt/_layout.txt)")
        layout = ler_layout_sigtap(z.read(lay))
        for exigida in ("CO_PROCEDIMENTO", "CO_OCUPACAO", "DT_COMPETENCIA"):
            if exigida not in layout:
                raise ErroResposta(f"layout sem {exigida}")
        linhas = []
        for ln in z.read(tab).decode("latin-1").splitlines():
            if not ln.strip():
                continue
            reg = {k.lower(): ln[a:b].strip() for k, (a, b) in layout.items()}
            linhas.append(reg)
    df = pd.DataFrame(linhas)
    if df.empty or not df["co_procedimento"].str.fullmatch(r"\d{10}").all():
        raise ErroResposta("rl_procedimento_ocupacao vazia ou com código de procedimento fora do padrão")
    df["co_forma"] = df["co_procedimento"].str[:6]
    return df


def sondar_sigtap() -> dict[str, Any]:
    """Tenta obter o ZIP oficial do SIGTAP; registra cada tentativa. Nunca inventa a tabela."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    sond: dict[str, Any] = {"data_hora_utc": agora(), "competencia_alvo": COMPETENCIA_SIGTAP, "tentativas": []}
    # 1. página de download
    try:
        raw, status, ctype = _http_get(URL_SIGTAP_DOWNLOAD)
        (CACHE_DIR / "sigtap_download.html").write_bytes(raw)
        txt = re.sub(r"\s+", " ", re.sub(r"<[^>]*>", " ", html.unescape(raw.decode("latin-1"))))
        m = re.search(r"(Caro usu[aá]rio[^.]*servi[çc]o de downloads[^.]*indispon[^.]*\.)", txt, re.I)
        sond["tentativas"].append({
            "via": "pagina_download", "url": URL_SIGTAP_DOWNLOAD, "data_hora_utc": agora(), "http_status": status,
            "content_type": ctype, "bytes": len(raw), "sha256": sha256_bytes(raw),
            "mensagem_indisponivel": bool(m), "trecho": m.group(1).strip() if m else None,
            "resultado": "servico_de_download_indisponivel" if m else "pagina_respondeu",
        })
    except Exception as exc:  # noqa: BLE001
        sond["tentativas"].append({"via": "pagina_download", "url": URL_SIGTAP_DOWNLOAD, "data_hora_utc": agora(),
                                   "resultado": "falha", "erro": f"{type(exc).__name__}: {exc}"[:300]})
    # 2. RSS de competências (nome oficial do ZIP)
    zip_nome = None
    try:
        raw, status, ctype = _http_get(URL_SIGTAP_RSS)
        (CACHE_DIR / "sigtap_competencias.rss").write_bytes(raw)
        # o servidor manda o RSS comprimido em gzip mesmo sem Accept-Encoding
        texto_rss = (gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw).decode("utf-8", errors="replace")
        itens = ler_rss_competencias(texto_rss)
        alvo = f"Competência {COMPETENCIA_SIGTAP[4:]}/{COMPETENCIA_SIGTAP[:4]}"
        escolhido = next((i for i in itens if i["titulo"] == alvo), None)
        zip_nome = escolhido["link"].rsplit("/", 1)[-1] if escolhido else None
        sond["tentativas"].append({
            "via": "rss_competencias", "url": URL_SIGTAP_RSS, "data_hora_utc": agora(), "http_status": status,
            "bytes": len(raw), "sha256": sha256_bytes(raw), "itens": len(itens),
            "itens_recentes": itens[:3], "item_competencia_alvo": escolhido,
            "resultado": "ok" if itens else "sem_itens",
        })
    except Exception as exc:  # noqa: BLE001
        sond["tentativas"].append({"via": "rss_competencias", "url": URL_SIGTAP_RSS, "data_hora_utc": agora(),
                                   "resultado": "falha", "erro": f"{type(exc).__name__}: {exc}"[:300]})
    # 3. FTP oficial (onde o ZIP está)
    zbytes = None
    try:
        ftp = ftplib.FTP(FTP_SIGTAP_HOST, timeout=45)
        ftp.login()
        ftp.cwd(FTP_SIGTAP_DIR)
        lista = ftp.nlst()
        candidatos = sorted(n for n in lista if n.startswith(f"TabelaUnificada_{COMPETENCIA_SIGTAP}_"))
        nome = zip_nome if zip_nome in lista else (candidatos[-1] if candidatos else None)
        if nome:
            buf = io.BytesIO()
            ftp.retrbinary(f"RETR {nome}", buf.write)
            zbytes = buf.getvalue()
            (CACHE_DIR / nome).write_bytes(zbytes)
        ftp.quit()
        sond["tentativas"].append({
            "via": "ftp", "url": f"ftp://{FTP_SIGTAP_HOST}{FTP_SIGTAP_DIR}/{nome or ''}", "data_hora_utc": agora(),
            "resultado": "ok" if zbytes else "zip_da_competencia_nao_listado",
            "bytes": len(zbytes) if zbytes else None, "sha256": sha256_bytes(zbytes) if zbytes else None,
        })
    except Exception as exc:  # noqa: BLE001
        sond["tentativas"].append({"via": "ftp", "url": f"ftp://{FTP_SIGTAP_HOST}{FTP_SIGTAP_DIR}/{zip_nome or ''}",
                                   "data_hora_utc": agora(), "resultado": "falha",
                                   "erro": f"{type(exc).__name__}: {exc}"[:300]})
    sond["zip_oficial_nome"] = zip_nome
    sond["obtido"] = zbytes is not None
    sond["status"] = "OBTIDO" if zbytes else "INDISPONIVEL_NESTA_EXECUCAO"
    (CACHE_DIR / "sigtap_sondagem.json").write_text(json.dumps(sond, ensure_ascii=False, indent=2) + "\n",
                                                   encoding="utf-8")
    log(f"SIGTAP: {sond['status']} ({[t['via'] + ':' + t['resultado'] for t in sond['tentativas']]})")
    return sond


# ---------------------------------------------------------------- TabNet SIA (fonte revelada)

def ler_formulario(txt: str) -> dict[str, list[tuple[str, str]]]:
    selects: dict[str, list[tuple[str, str]]] = {}
    for m in re.finditer(r'<SELECT[^>]*NAME="([^"]+)"[^>]*>(.*?)</SELECT>', txt, re.S | re.I):
        opcoes = re.findall(r'<OPTION[^>]*VALUE="([^"]*)"[^>]*>([^<\r\n]*)', m.group(2), re.I)
        selects[m.group(1)] = [(v, html.unescape(t).strip()) for v, t in opcoes]
    if not re.search(r'ACTION="/cgi/tabcgi\.exe\?sia/cnv/qabr\.def"', txt, re.I):
        raise ErroResposta("formulário não aponta para tabcgi.exe?sia/cnv/qabr.def")
    return selects


def valor(selects: dict[str, list[tuple[str, str]]], campo: str, rotulo: str) -> str:
    achados = [v for v, t in selects.get(campo, []) if t == rotulo]
    if len(achados) != 1:
        raise ErroResposta(f"opção {rotulo!r} não encontrada uma única vez em {campo}")
    return achados[0]


def opcoes_cbo_medicas(selects: dict[str, list[tuple[str, str]]]) -> list[dict[str, str]]:
    saida = []
    for v, t in selects["SProfissional_-_CBO"]:
        m = RE_CBO.match(t)
        if v != "TODAS_AS_CATEGORIAS__" and m and m.group(1).startswith(PREFIXOS_CBO_MEDICO):
            saida.append({"indice": v, "co_cbo": m.group(1), "rotulo": t})
    if not saida:
        raise ErroResposta("nenhuma CBO médica no formulário")
    return saida


def municipios_do_formulario(selects: dict[str, list[tuple[str, str]]]) -> list[str]:
    cods = [RE_MUNICIPIO.match(t).group(1) for v, t in selects["SMunicípio"]
            if v != "TODAS_AS_CATEGORIAS__" and RE_MUNICIPIO.match(t) and not t.startswith("000000")]
    if len(cods) != len(set(cods)) or len(cods) < 5_500:
        raise ErroResposta("lista de municípios do formulário inválida")
    return sorted(cods)


def planejar(selects: dict[str, list[tuple[str, str]]], alvo: list[str]) -> list[dict[str, Any]]:
    """As quatro consultas do G4, com campos lidos do formulário."""
    for c in MESES_MAPA + [MES_TESTE]:
        checar_limite(c)
    arq = {c: valor(selects, "Arquivos", rotulo_mes(c)) for c in MESES_MAPA + [MES_TESTE]}
    for c, a in arq.items():
        if a.lower() != f"qabr{c[2:]}.dbf":
            raise ErroResposta(f"Arquivos de {c} aponta para {a}")
    linha_cbo = valor(selects, "Linha", "Profissional - CBO")
    linha_mun = valor(selects, "Linha", "Município")
    linha_forma = valor(selects, "Linha", "Forma organização")
    col_forma = valor(selects, "Coluna", "Forma organização")
    col_nao = valor(selects, "Coluna", "Não ativa")
    inc = valor(selects, "Incremento", "Qtd.aprovada")
    medicas = opcoes_cbo_medicas(selects)
    por_cbo = {o["co_cbo"]: o for o in opcoes_cbo_medicas(selects)}
    faltam = [c for c in alvo if c not in por_cbo]
    if faltam:
        raise ErroResposta(f"CBO dos cursos ausentes do formulário: {faltam}")
    alvo_op = sorted((por_cbo[c] for c in alvo), key=lambda o: int(o["indice"]))
    fim = [("zeradas", "exibirlz"), ("formato", "prn"), ("mostre", "Mostra")]
    meses_mapa = [("Arquivos", arq[c]) for c in MESES_MAPA]
    return [
        {"id": "nac_cbo_medica_forma_2024", "linha": "Profissional - CBO", "coluna": "forma", "meses": MESES_MAPA,
         "campos": [("Linha", linha_cbo), ("Coluna", col_forma), ("Incremento", inc)] + meses_mapa
         + [("SProfissional_-_CBO", o["indice"]) for o in medicas] + fim,
         "eco_cbo": ", ".join(o["rotulo"] for o in medicas)},
        {"id": "nac_forma_todos_2024", "linha": "Forma organização", "coluna": "nao_ativa", "meses": MESES_MAPA,
         "campos": [("Linha", linha_forma), ("Coluna", col_nao), ("Incremento", inc)] + meses_mapa
         + [("formato", "prn"), ("mostre", "Mostra")], "eco_cbo": None},
        {"id": f"teste_mun_forma_alvo_{MES_TESTE}", "linha": "Município", "coluna": "forma", "meses": [MES_TESTE],
         "campos": [("Linha", linha_mun), ("Coluna", col_forma), ("Incremento", inc), ("Arquivos", arq[MES_TESTE])]
         + [("SProfissional_-_CBO", o["indice"]) for o in alvo_op] + fim,
         "eco_cbo": ", ".join(o["rotulo"] for o in alvo_op)},
        {"id": f"teste_cbo_forma_alvo_{MES_TESTE}", "linha": "Profissional - CBO", "coluna": "forma",
         "meses": [MES_TESTE],
         "campos": [("Linha", linha_cbo), ("Coluna", col_forma), ("Incremento", inc), ("Arquivos", arq[MES_TESTE])]
         + [("SProfissional_-_CBO", o["indice"]) for o in alvo_op] + fim,
         "eco_cbo": ", ".join(o["rotulo"] for o in alvo_op)},
    ]


def ler_resposta(raw: bytes, consulta: dict[str, Any]) -> dict[str, Any]:
    """Lê a tabela 'prn' e confere eco do período e do filtro, cabeçalho e somas (fail closed)."""
    txt = raw.decode(ENCODING)
    if txt.count("<PRE>") != 1 or txt.count("</PRE>") != 1:
        raise ErroResposta("resposta sem bloco PRE único")
    ini, fim = txt.find("<PRE>"), txt.find("</PRE>")
    cab = html.unescape(txt[:ini])
    periodo = re.search(r"<b>Período:</b>\s*([^<]*)", cab)
    esperado = ", ".join(rotulo_mes(c) for c in sorted(consulta["meses"], reverse=True))
    if not periodo or periodo.group(1).strip() != esperado:
        raise ErroResposta(f"período ecoado {periodo.group(1).strip() if periodo else None!r} != {esperado!r}")
    eco = re.search(r"<b>Profissional - CBO:</b>\s*([^<]*)", cab)
    eco_txt = eco.group(1).strip() if eco else None
    if eco_txt != consulta["eco_cbo"]:
        raise ErroResposta("filtro de CBO ecoado difere do pedido")
    linhas_txt = [ln for ln in txt[ini + 5:fim].strip("\r\n").splitlines() if ln.strip() not in ("", "&")]
    tabela = [[html.unescape(c).strip() for c in r] for r in csv.reader(io.StringIO("\n".join(linhas_txt)),
                                                                          delimiter=";", quotechar='"')]
    cabecalho = tabela[0]
    if cabecalho[0] != consulta["linha"]:
        raise ErroResposta(f"rótulo da linha {cabecalho[0]!r}")
    if consulta["coluna"] == "nao_ativa":
        if cabecalho[1:] != ["Qtd.aprovada"]:
            raise ErroResposta(f"cabeçalho inesperado {cabecalho}")
        colunas = []
    else:
        if cabecalho[-1] != "Total":
            raise ErroResposta("última coluna não é Total")
        colunas = []
        for c in cabecalho[1:-1]:
            m = RE_FORMA.match(c)
            if not m:
                raise ErroResposta(f"coluna fora do padrão de forma: {c!r}")
            colunas.append((m.group(1), m.group(2).strip()))
    linhas = []
    for r in tabela[1:]:
        if len(r) != len(cabecalho):
            raise ErroResposta(f"linha com {len(r)} campos: {r[:2]}")
        vals = []
        for x in r[1:]:
            if x == "-":
                vals.append(0)
            elif re.fullmatch(r"[1-9]\d*", x):
                vals.append(int(x))
            else:
                raise ErroResposta(f"valor não reconhecido {x!r}")
        linhas.append((r[0], vals))
    if not linhas or linhas[-1][0] != "Total":
        raise ErroResposta("última linha não é Total")
    corpo, total = linhas[:-1], linhas[-1][1]
    n = len(total)
    for j in range(n):
        if sum(v[j] for _, v in corpo) != total[j]:
            raise ErroResposta(f"coluna {j}: soma das linhas difere do Total")
    if colunas:
        for rot, v in corpo + [("Total", total)]:
            if sum(v[:-1]) != v[-1]:
                raise ErroResposta(f"linha {rot!r}: soma das colunas difere do Total")
    return {"colunas": colunas, "linhas": corpo, "total": total, "periodo_eco": periodo.group(1).strip()}


def caminho(cid: str, ext: str) -> Path:
    return CACHE_DIR / f"{cid}.{ext}"


def baixar_formulario() -> dict[str, Any]:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    raw, status, ctype = _http_get(URL_FORM, timeout=180)
    ler_formulario(raw.decode(ENCODING))
    caminho("formulario_qabr", "html.gz").write_bytes(gzip.compress(raw, mtime=0))
    meta = {"url": URL_FORM, "metodo": "GET", "data_hora_utc": agora(), "http_status": status,
            "sha256": sha256_bytes(raw), "bytes": len(raw)}
    caminho("formulario_qabr", "json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
                                                  encoding="utf-8")
    return meta


def carregar_formulario() -> tuple[dict[str, list[tuple[str, str]]], dict[str, Any]]:
    meta_p, raw_p = caminho("formulario_qabr", "json"), caminho("formulario_qabr", "html.gz")
    if not meta_p.exists() or not raw_p.exists():
        raise SystemExit("formulário do qabr ausente do cache; rode --etapa baixar")
    meta = json.loads(meta_p.read_text(encoding="utf-8"))
    raw = gzip.decompress(raw_p.read_bytes())
    if sha256_bytes(raw) != meta["sha256"]:
        raise ErroResposta("SHA-256 do formulário em cache difere do metadado")
    return ler_formulario(raw.decode(ENCODING)), meta


def baixar_consulta(q: dict[str, Any]) -> dict[str, Any]:
    corpo = urllib.parse.urlencode(q["campos"], encoding=ENCODING)
    mp, rp = caminho(q["id"], "json"), caminho(q["id"], "html.gz")
    if mp.exists() and rp.exists():
        meta = json.loads(mp.read_text(encoding="utf-8"))
        if meta.get("corpo_post") == corpo and meta.get("status") == "ok":
            return meta
    falhas = []
    for t in range(1, TENTATIVAS + 1):
        quando, t0 = agora(), time.time()
        try:
            req = urllib.request.Request(URL_TAB, data=corpo.encode("ascii"), headers={
                "User-Agent": "Mozilla/5.0", "Content-Type": "application/x-www-form-urlencoded"})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                raw, status = resp.read(), resp.status
            ler_resposta(raw, q)
        except Exception as exc:  # noqa: BLE001
            falhas.append({"tentativa": t, "data_hora_utc": quando, "erro": f"{type(exc).__name__}: {exc}"[:300]})
            log(f"  {q['id']}: falha {t}/{TENTATIVAS}: {falhas[-1]['erro'][:150]}")
            time.sleep(min(15 * 2 ** (t - 1), 240))
            continue
        rp.write_bytes(gzip.compress(raw, mtime=0))
        meta = {"id": q["id"], "url": URL_TAB, "metodo": "POST", "codificacao_corpo": ENCODING, "corpo_post": corpo,
                "data_hora_utc": quando, "http_status": status, "sha256": sha256_bytes(raw), "bytes": len(raw),
                "segundos": round(time.time() - t0, 1), "tentativas": t, "falhas_anteriores": falhas, "status": "ok"}
        mp.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        time.sleep(PAUSA)
        return meta
    raise RuntimeError(f"{q['id']}: falhou após {TENTATIVAS} tentativas")


def carregar_consulta(q: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    mp, rp = caminho(q["id"], "json"), caminho(q["id"], "html.gz")
    if not mp.exists() or not rp.exists():
        raise SystemExit(f"consulta {q['id']} ausente do cache; rode --etapa baixar")
    meta = json.loads(mp.read_text(encoding="utf-8"))
    raw = gzip.decompress(rp.read_bytes())
    if sha256_bytes(raw) != meta["sha256"]:
        raise ErroResposta(f"{q['id']}: SHA-256 do cache difere do metadado")
    if meta["corpo_post"] != urllib.parse.urlencode(q["campos"], encoding=ENCODING):
        raise ErroResposta(f"{q['id']}: corpo do POST em cache difere do plano atual")
    return ler_resposta(raw, q), meta


def etapa_baixar() -> int:
    sondar_sigtap()
    baixar_formulario()
    selects, _ = carregar_formulario()
    cursos, _ = carregar_ponte()
    alvo = sorted({c for k in cursos for c in k["cbos"]})
    for q in planejar(selects, alvo):
        meta = baixar_consulta(q)
        log(f"{q['id']}: {meta['bytes']:,} bytes em {meta.get('segundos')} s")
    return 0


# ---------------------------------------------------------------- consolidação

def montar_tabelas(r_cbo: dict[str, Any], r_forma: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """CBO médica × forma (longo) e forma × (médicos, todos), nacionais, 2024."""
    reg = []
    for rot, vals in r_cbo["linhas"]:
        m = RE_CBO.match(rot)
        if not m:
            raise ErroResposta(f"linha de CBO fora do padrão: {rot!r}")
        for (cof, nof), q in zip(r_cbo["colunas"], vals[:-1]):
            if q > 0:
                reg.append({"co_cbo": m.group(1), "no_cbo": m.group(2), "co_forma": cof, "no_forma": nof,
                            "qtd_aprovada": q})
    cbo_forma = pd.DataFrame(reg).sort_values(["co_cbo", "co_forma"]).reset_index(drop=True)
    cbo_forma["janela_producao"] = f"{MESES_MAPA[0]}-{MESES_MAPA[-1]}"
    cbo_forma["natureza_dos_dados"] = NATUREZA
    medicos = dict(zip([c for c, _ in r_cbo["colunas"]], r_cbo["total"][:-1]))
    formas = []
    for rot, vals in r_forma["linhas"]:
        m = RE_FORMA.match(rot)
        if not m:
            raise ErroResposta(f"linha de forma fora do padrão: {rot!r}")
        formas.append({"co_forma": m.group(1), "no_forma": m.group(2), "qtd_aprovada_todos": vals[0],
                       "qtd_aprovada_medicos": medicos.get(m.group(1), 0)})
    forma = pd.DataFrame(formas)
    sem_linha = sorted(set(medicos) - set(forma["co_forma"]))
    if sem_linha:
        raise ErroResposta(f"formas com produção médica sem linha no total: {sem_linha}")
    if (forma["qtd_aprovada_medicos"] > forma["qtd_aprovada_todos"]).any():
        raise ErroResposta("produção médica maior que a de todos os profissionais numa forma")
    forma["co_subgrupo"] = forma["co_forma"].str[:4]
    forma["co_grupo"] = forma["co_forma"].str[:2]
    forma["janela_producao"] = f"{MESES_MAPA[0]}-{MESES_MAPA[-1]}"
    forma["natureza_dos_dados"] = NATUREZA
    forma = forma[["co_grupo", "co_subgrupo", "co_forma", "no_forma", "qtd_aprovada_medicos", "qtd_aprovada_todos",
                   "janela_producao", "natureza_dos_dados"]].sort_values("co_forma").reset_index(drop=True)
    return cbo_forma, forma


def montar_mapa(cursos: list[dict[str, Any]], cbo_forma: pd.DataFrame, forma: pd.DataFrame,
                compat: dict[tuple[int, str], bool] | None) -> tuple[pd.DataFrame, pd.DataFrame]:
    tot = forma.set_index("co_forma")
    linhas, linhas_sg = [], []
    for c in cursos:
        sub = cbo_forma.loc[cbo_forma["co_cbo"].isin(c["cbos"])]
        por_forma = sub.groupby(["co_forma", "no_forma"], as_index=False)["qtd_aprovada"].sum()
        total_curso = int(por_forma["qtd_aprovada"].sum())
        por_forma = por_forma.sort_values(["qtd_aprovada", "co_forma"], ascending=[False, True]).reset_index(drop=True)
        if total_curso == 0:
            continue
        por_forma["participacao"] = por_forma["qtd_aprovada"] / total_curso
        por_forma["acumulada"] = por_forma["participacao"].cumsum()
        # típica: a forma entra enquanto a acumulada ANTES dela for < limiar (a que cruza o limiar entra)
        antes = por_forma["acumulada"] - por_forma["participacao"]
        por_forma["tipica"] = antes < LIMIAR_TIPICA - 1e-12
        for i, r in por_forma.iterrows():
            med = int(tot.loc[r["co_forma"], "qtd_aprovada_medicos"])
            todos = int(tot.loc[r["co_forma"], "qtd_aprovada_todos"])
            esp_m = r["qtd_aprovada"] / med if med else None
            linhas.append({
                "cod_curso": c["cod_curso"], "no_curso": c["no_curso"], "cbos_curso": "|".join(c["cbos"]),
                "grau_univocidade_ponte": c["grau_univocidade"], "co_grupo": r["co_forma"][:2],
                "co_subgrupo": r["co_forma"][:4], "co_forma": r["co_forma"], "no_forma": r["no_forma"],
                "qtd_aprovada_cbo_curso": int(r["qtd_aprovada"]),
                "participacao_na_producao_do_curso": round(float(r["participacao"]), 6),
                "participacao_acumulada": round(float(r["acumulada"]), 6), "ordem_no_curso": i + 1,
                "tipica": bool(r["tipica"]), "qtd_aprovada_medicos": med, "qtd_aprovada_todos": todos,
                "especificidade_medicos": round(esp_m, 6) if esp_m is not None else None,
                "especificidade_todos": round(r["qtd_aprovada"] / todos, 6) if todos else None,
                "classe_especificidade": classe_especificidade(esp_m),
                "compatibilidade_sigtap": ("NAO_OBTIDA" if compat is None else
                                           ("COMPATIVEL" if compat.get((c["cod_curso"], r["co_forma"])) else
                                            "SEM_PROCEDIMENTO_COMPATIVEL")),
                "janela_producao": f"{MESES_MAPA[0]}-{MESES_MAPA[-1]}",
                "fonte_mapa": "TABNET_SIA_QABR_PRODUCAO_APROVADA_NACIONAL",
                "natureza_dos_dados": NATUREZA,
            })
        df = pd.DataFrame([x for x in linhas if x["cod_curso"] == c["cod_curso"]])
        for sg, g in df.groupby("co_subgrupo"):
            med = int(forma.loc[forma["co_subgrupo"] == sg, "qtd_aprovada_medicos"].sum())
            todos = int(forma.loc[forma["co_subgrupo"] == sg, "qtd_aprovada_todos"].sum())
            q = int(g["qtd_aprovada_cbo_curso"].sum())
            esp = q / med if med else None
            linhas_sg.append({
                "cod_curso": c["cod_curso"], "no_curso": c["no_curso"], "cbos_curso": "|".join(c["cbos"]),
                "co_grupo": sg[:2], "co_subgrupo": sg, "qtd_aprovada_cbo_curso": q,
                "participacao_na_producao_do_curso": round(q / total_curso, 6),
                "n_formas_com_producao": int(len(g)), "n_formas_tipicas": int(g["tipica"].sum()),
                "qtd_aprovada_medicos": med, "qtd_aprovada_todos": todos,
                "especificidade_medicos": round(esp, 6) if esp is not None else None,
                "especificidade_todos": round(q / todos, 6) if todos else None,
                "classe_especificidade": classe_especificidade(esp),
                "janela_producao": f"{MESES_MAPA[0]}-{MESES_MAPA[-1]}",
                "fonte_mapa": "TABNET_SIA_QABR_PRODUCAO_APROVADA_NACIONAL", "natureza_dos_dados": NATUREZA,
            })
    mapa = pd.DataFrame(linhas, columns=COLUNAS_MAPA)
    mapa_sg = pd.DataFrame(linhas_sg, columns=COLUNAS_SUBGRUPO).sort_values(
        ["cod_curso", "qtd_aprovada_cbo_curso", "co_subgrupo"], ascending=[True, False, True]).reset_index(drop=True)
    return mapa, mapa_sg


def resumo_por_curso(cursos: list[dict[str, Any]], mapa: pd.DataFrame, cbo_forma: pd.DataFrame) -> list[dict[str, Any]]:
    conjuntos = {c["cod_curso"]: frozenset(c["cbos"]) for c in cursos}
    saida = []
    for c in cursos:
        m = mapa.loc[mapa["cod_curso"] == c["cod_curso"]]
        tip = m.loc[m["tipica"]]
        por_cbo = cbo_forma.loc[cbo_forma["co_cbo"].isin(c["cbos"])].groupby("co_cbo")["qtd_aprovada"].sum()
        mesmo_conjunto = sorted(k for k, s in conjuntos.items() if s == conjuntos[c["cod_curso"]] and k != c["cod_curso"])
        compartilha = sorted(k for k, s in conjuntos.items() if s & conjuntos[c["cod_curso"]] and k != c["cod_curso"])
        total = int(m["qtd_aprovada_cbo_curso"].sum())
        p_alta = float(m.loc[m["classe_especificidade"] == "alta", "participacao_na_producao_do_curso"].sum())
        p_media_alta = float(m.loc[m["classe_especificidade"].isin(["alta", "media"]),
                                   "participacao_na_producao_do_curso"].sum())
        if p_alta >= LIMIAR_CURSO_ESPECIFICO:
            classe_curso = "ESPECIFICO"
        elif p_media_alta >= LIMIAR_CURSO_ESPECIFICO:
            classe_curso = "PARCIAL"
        else:
            classe_curso = "GENERICO"
        relevantes = m.loc[(m["classe_especificidade"] == "alta")
                           & (m["participacao_na_producao_do_curso"] >= LIMIAR_PARTICIPACAO_RELEVANTE)]
        saida.append({
            "classe_mapa_curso": classe_curso,
            "formas_especificas_relevantes": [
                {"co_forma": r.co_forma, "no_forma": r.no_forma, "participacao": r.participacao_na_producao_do_curso,
                 "especificidade_medicos": r.especificidade_medicos} for r in relevantes.itertuples()],
            "cod_curso": c["cod_curso"], "no_curso": c["no_curso"], "cbos": c["cbos"],
            "qtd_aprovada_cbo_curso_2024": total,
            "qtd_por_cbo_2024": {k: int(por_cbo.get(k, 0)) for k in c["cbos"]},
            "cbos_sem_producao_sia_2024": [k for k in c["cbos"] if int(por_cbo.get(k, 0)) == 0],
            "n_formas_com_producao": int(len(m)), "n_formas_tipicas": int(len(tip)),
            "participacao_formas_tipicas": round(float(tip["participacao_na_producao_do_curso"].sum()), 4) if total else None,
            "participacao_da_producao_em_formas_de_especificidade_alta": round(float(
                m.loc[m["classe_especificidade"] == "alta", "participacao_na_producao_do_curso"].sum()), 4) if total else None,
            "participacao_da_producao_em_formas_de_especificidade_media_ou_alta": round(float(
                m.loc[m["classe_especificidade"].isin(["alta", "media"]), "participacao_na_producao_do_curso"].sum()), 4)
            if total else None,
            "formas_tipicas": [
                {"co_forma": r.co_forma, "no_forma": r.no_forma,
                 "participacao": r.participacao_na_producao_do_curso,
                 "especificidade_medicos": r.especificidade_medicos, "classe": r.classe_especificidade}
                for r in tip.itertuples()],
            "cursos_com_o_mesmo_conjunto_de_cbo": mesmo_conjunto,
            "cursos_que_compartilham_alguma_cbo": compartilha,
            "distinguivel_de_outros_cursos_pela_cbo": not compartilha,
        })
    return saida


def teste_viabilidade(r_mun: dict[str, Any], r_nac: dict[str, Any], universo: list[str],
                      meta_mun: dict[str, Any]) -> tuple[dict[str, Any], pd.DataFrame]:
    """Teste de um mês: município × forma com filtro de CBO. Só agregados nacionais saem daqui."""
    cods = []
    ignorados = 0
    for rot, _ in r_mun["linhas"]:
        if RE_IGNORADO.match(rot):
            ignorados += 1
            continue
        m = RE_MUNICIPIO.match(rot)
        if not m:
            raise ErroResposta(f"linha municipal fora do padrão: {rot!r}")
        cods.append(m.group(1))
    tot_mun = dict(zip([c for c, _ in r_mun["colunas"]], r_mun["total"][:-1]))
    tot_nac = dict(zip([c for c, _ in r_nac["colunas"]], r_nac["total"][:-1]))
    nomes = dict(r_mun["colunas"]) | dict(r_nac["colunas"])
    formas = sorted(set(tot_mun) | set(tot_nac))
    tab = pd.DataFrame({
        "co_forma": formas, "no_forma": [nomes[f] for f in formas],
        "qtd_total_consulta_municipal": [tot_mun.get(f, 0) for f in formas],
        "qtd_total_consulta_por_cbo": [tot_nac.get(f, 0) for f in formas],
    })
    tab["co_subgrupo"] = tab["co_forma"].str[:4]
    # conferência com o a12 (mesmo mês, conjunto alvo_pmme, por subgrupo)
    a12 = pd.read_csv(A12_SUBGRUPOS_FILE, dtype={"competencia_processamento": str, "subgrupo": str})
    a12 = a12.loc[(a12["competencia_processamento"] == MES_TESTE) & (a12["conjunto_cbo"] == "alvo_pmme")]
    a12_sg = a12.set_index("subgrupo")["total_tabnet_municipio"].fillna(0).astype(int)
    sg = tab.groupby("co_subgrupo")["qtd_total_consulta_municipal"].sum()
    subgrupos = sorted(set(sg.index) | set(a12_sg[a12_sg > 0].index))
    difs = {s: (int(sg.get(s, 0)), int(a12_sg.get(s, 0))) for s in subgrupos if int(sg.get(s, 0)) != int(a12_sg.get(s, 0))}
    tab["mes_processamento"] = MES_TESTE
    tab["filtro_cbo"] = "alvo_pmme (17 CBO da ponte)"
    tab["natureza_dos_dados"] = NATUREZA
    res = {
        "consulta": "Linha = Município, Coluna = Forma organização, Incremento = Qtd.aprovada, filtro "
                    "Profissional - CBO = 17 CBO-alvo da ponte, Arquivos = qabr" + MES_TESTE[2:] + ".dbf, exibirlz",
        "mes_processamento": MES_TESTE,
        "respondeu_no_formato": True,
        "bytes_resposta": meta_mun["bytes"], "segundos": meta_mun.get("segundos"),
        "linhas_municipio": len(cods), "linhas_ignorado": ignorados,
        "municipios_do_formulario": len(universo),
        "todos_os_municipios_do_formulario_presentes": sorted(cods) == universo,
        "formas_como_coluna": len(r_mun["colunas"]),
        "total_municipal_igual_ao_nacional_por_cbo_em_cada_forma": bool(
            (tab["qtd_total_consulta_municipal"] == tab["qtd_total_consulta_por_cbo"]).all()),
        "soma_por_subgrupo_igual_ao_a12": not difs,
        "diferencas_por_subgrupo_frente_ao_a12": difs,
        "qtd_total_nacional": int(r_mun["total"][-1]),
        "procedimento_como_coluna": False,
        "nota_procedimento": ("no formulário qabr.def 'Procedimento' só existe como Linha e como filtro; o nível mais "
                              "fino que cruza com Município numa mesma consulta é a Forma de organização (coluna). "
                              "Profissional - CBO só existe como Linha e como filtro, por isso cada consulta "
                              "municipal cobre um conjunto de CBO."),
    }
    res["viavel"] = bool(res["todos_os_municipios_do_formulario_presentes"]
                         and res["total_municipal_igual_ao_nacional_por_cbo_em_cada_forma"]
                         and res["soma_por_subgrupo_igual_ao_a12"])
    return res, tab[["mes_processamento", "filtro_cbo", "co_subgrupo", "co_forma", "no_forma",
                     "qtd_total_consulta_municipal", "qtd_total_consulta_por_cbo", "natureza_dos_dados"]]


def ler_sigtap_cache(sond: dict[str, Any], cursos: list[dict[str, Any]]) -> dict[tuple[int, str], bool] | None:
    if not sond.get("obtido") or not sond.get("zip_oficial_nome"):
        return None
    p = CACHE_DIR / sond["zip_oficial_nome"]
    if not p.exists():
        return None
    rl = ler_rl_procedimento_ocupacao(p.read_bytes())
    saida = {}
    for c in cursos:
        formas = set(rl.loc[rl["co_ocupacao"].isin(c["cbos"]), "co_forma"])
        for f in formas:
            saida[(c["cod_curso"], f)] = True
    return saida


def gravar_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, lineterminator="\n")


def etapa_consolidar() -> int:
    sond_p = CACHE_DIR / "sigtap_sondagem.json"
    if not sond_p.exists():
        raise SystemExit("sondagem do SIGTAP ausente do cache; rode --etapa baixar")
    sond = json.loads(sond_p.read_text(encoding="utf-8"))
    selects, form_meta = carregar_formulario()
    cursos, sha_ponte = carregar_ponte()
    alvo = sorted({c for k in cursos for c in k["cbos"]})
    plano = planejar(selects, alvo)
    resp, metas = {}, []
    for q in plano:
        resp[q["id"]], meta = carregar_consulta(q)
        metas.append({k: meta[k] for k in ("id", "url", "metodo", "codificacao_corpo", "corpo_post", "data_hora_utc",
                                           "http_status", "sha256", "bytes", "segundos", "tentativas")})
    cbo_forma, forma = montar_tabelas(resp["nac_cbo_medica_forma_2024"], resp["nac_forma_todos_2024"])
    faltam = [c for c in alvo if c not in set(cbo_forma["co_cbo"])]
    compat = ler_sigtap_cache(sond, cursos)
    mapa, mapa_sg = montar_mapa(cursos, cbo_forma, forma, compat)
    universo = municipios_do_formulario(selects)
    teste, tab_teste = teste_viabilidade(resp[f"teste_mun_forma_alvo_{MES_TESTE}"],
                                         resp[f"teste_cbo_forma_alvo_{MES_TESTE}"], universo,
                                         next(m for m in metas if m["id"] == f"teste_mun_forma_alvo_{MES_TESTE}"))
    erros = []
    if not teste["viavel"]:
        erros.append("teste de viabilidade do filtro reprovado")
    if mapa.duplicated(["cod_curso", "co_forma"]).any():
        erros.append("mapa com curso × forma duplicado")
    for k, g in mapa.groupby("cod_curso"):
        if abs(g["participacao_na_producao_do_curso"].sum() - 1) > 1e-4:
            erros.append(f"curso {k}: participações não somam 1")
    por_curso = resumo_por_curso(cursos, mapa, cbo_forma)
    cursos_sem_mapa = [c["cod_curso"] for c in cursos if c["cod_curso"] not in set(mapa["cod_curso"])]

    if compat is None:
        veredito = "VIAVEL_PARCIAL"
        motivo = (
            "O filtro de CBO cruza com a forma de organização por município e mês no TabNet do SIA (teste de um mês "
            "aprovado), e o mapa curso → formas foi montado com a produção nacional aprovada de 2024. Falta a fonte "
            "normativa pedida: a compatibilidade procedimento × CBO do SIGTAP (rl_procedimento_ocupacao) não pôde ser "
            "obtida nesta execução (sondagem registrada). O mapa é revelado (o que as CBO registram), não normativo. "
            "Do lado hospitalar, o TabNet do SIH não tem CBO: cirurgias por AIH não se atribuem à especialidade.")
    else:
        veredito = "VIAVEL" if teste["viavel"] else "INVIAVEL"
        motivo = "SIGTAP obtido e teste do filtro aprovado."
    if erros:
        veredito = "INVIAVEL"
        motivo = "; ".join(erros)

    OUT_AQ.mkdir(parents=True, exist_ok=True)
    SONDAGEM_FILE.write_text(json.dumps(sond, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    gravar_csv(cbo_forma[["co_cbo", "no_cbo", "co_forma", "no_forma", "qtd_aprovada", "janela_producao",
                          "natureza_dos_dados"]], CBO_FORMA_FILE)
    gravar_csv(forma, FORMA_FILE)
    gravar_csv(tab_teste, TESTE_FILE)
    gravar_csv(mapa, MAPA_FILE)
    gravar_csv(mapa_sg, MAPA_SUBGRUPO_FILE)
    resumo = {
        "gerador": "scripts/aquisicao/g4_mapa_especialidade_procedimento.py",
        "plano": "docs/06_execucao/51_plano_perguntas_reformuladas.md (P3, T3.2, portão G4)",
        "data_execucao": dt.date.today().isoformat(),
        "natureza_dos_dados": NATUREZA,
        "veredito": veredito, "motivo": motivo,
        "sigtap": {"status": sond["status"], "competencia_alvo": COMPETENCIA_SIGTAP,
                   "zip_oficial_nome": sond.get("zip_oficial_nome"),
                   "tentativas": [{k: t.get(k) for k in ("via", "url", "resultado", "http_status", "erro", "trecho")}
                                  for t in sond["tentativas"]]},
        "regras": {
            "janela_producao": f"{MESES_MAPA[0]}–{MESES_MAPA[-1]} (meses de processamento, antes das chegadas do PMM-E)",
            "tipica": f"formas que, em ordem decrescente de produção das CBO do curso, somam os primeiros "
                      f"{LIMIAR_TIPICA:.0%} da produção (a forma que cruza o limiar entra)",
            "especificidade": f"qtd das CBO do curso / qtd de todas as CBO médicas ({', '.join(PREFIXOS_CBO_MEDICO)}) "
                              f"na forma; alta >= {LIMIAR_ESPEC_ALTA}, média >= {LIMIAR_ESPEC_MEDIA}, baixa abaixo",
            "classe_mapa_curso": f"ESPECIFICO se >= {LIMIAR_CURSO_ESPECIFICO:.0%} da produção das CBO do curso está em "
                                 f"formas de especificidade alta; PARCIAL se só somando média e alta; GENERICO senão. "
                                 "Limiar fixado depois de ver só o mapa nacional de 2024 (sem IVS nem outcome); a "
                                 "escolha de outcomes fica para o adendo §12 do protocolo 47",
            "forma_especifica_relevante": f"especificidade alta e >= {LIMIAR_PARTICIPACAO_RELEVANTE:.0%} da produção do curso",
        },
        "classes_dos_cursos": {k: sorted(c["cod_curso"] for c in por_curso if c["classe_mapa_curso"] == k)
                               for k in ("ESPECIFICO", "PARCIAL", "GENERICO")},
        "cobertura": {
            "cursos": len(cursos), "cursos_com_mapa": len(cursos) - len(cursos_sem_mapa),
            "cursos_sem_producao_sia_2024": cursos_sem_mapa,
            "cbos_da_ponte": len(alvo), "cbos_sem_producao_sia_2024": faltam,
            "formas_com_producao_medica_2024": int((forma["qtd_aprovada_medicos"] > 0).sum()),
            "formas_no_total_2024": int(len(forma)),
            "linhas_do_mapa": int(len(mapa)), "linhas_tipicas": int(mapa["tipica"].sum()),
        },
        "por_curso": por_curso,
        "teste_filtro_tabnet": teste,
        "custo_estimado_aquisicao": {
            "consultas_por_mes": "uma por conjunto de CBO (Linha = Município, Coluna = Forma, filtro de CBO)",
            "conjuntos_de_cbo_distintos_nos_cursos": len({frozenset(c["cbos"]) for c in cursos}),
            "cbos_distintas": len(alvo),
            "meses_202201_202607": 55,
            "consultas_se_por_cbo": len(alvo) * 55,
            "bytes_por_consulta_no_teste": teste["bytes_resposta"],
        },
        "limites": [
            "mapa revelado pela produção, não pela regra de compatibilidade do SIGTAP (não obtida nesta execução)",
            "produção ambulatorial (SIA) apenas; a AIH (SIH) no TabNet não tem CBO, então cirurgias hospitalares e "
            "anestesias em internação não entram no mapa por especialidade",
            "cursos que compartilham CBO (6 e 8; 10 e 11; 7 com 4, 10 e 11) não se distinguem pela CBO",
            "CBO informada pelo prestador; produção sem CBO na tabela do TabNet fica fora de 'médicos' e entra só em 'todos'",
            "grupo 09 (OCI) não existe em 2024; formas de OCI ficam fora do mapa",
        ],
        "cegamento": "nada foi calculado por IVS, faixa da bolsa, lado de corte, tratamento ou chegada; o IVS não é lido",
        "erros": erros,
    }
    RESUMO_FILE.write_text(json.dumps(resumo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifesto = {
        "gerador": "scripts/aquisicao/g4_mapa_especialidade_procedimento.py",
        "natureza_dos_dados": NATUREZA, "data_execucao": dt.date.today().isoformat(),
        "entradas": {
            "ponte_curso_cbo": {"arquivo": rel(PONTE_FILE), "sha256": sha_ponte},
            "a12_subgrupos": {"arquivo": rel(A12_SUBGRUPOS_FILE), "sha256": sha256_arquivo(A12_SUBGRUPOS_FILE)},
        },
        "fonte_sigtap": {"url_download": URL_SIGTAP_DOWNLOAD, "url_rss": URL_SIGTAP_RSS,
                         "ftp": f"ftp://{FTP_SIGTAP_HOST}{FTP_SIGTAP_DIR}", "sondagem": rel(SONDAGEM_FILE),
                         "status": sond["status"]},
        "fonte_tabnet": {"nome": "SIA/SUS — Produção Ambulatorial do SUS, Brasil, por local de atendimento (TabNet)",
                         "url_formulario": URL_FORM, "url_consulta": URL_TAB,
                         "formulario": form_meta, "consultas": metas},
        "saidas": {},
        "cache_bruto": f"{rel(CACHE_DIR)}/ (fora do controle de versão; respostas municipais do teste só aqui)",
        "cegamento": resumo["cegamento"],
    }
    for nome, p in (("sondagem", SONDAGEM_FILE), ("cbo_forma", CBO_FORMA_FILE), ("forma", FORMA_FILE),
                    ("teste", TESTE_FILE), ("mapa", MAPA_FILE), ("mapa_subgrupo", MAPA_SUBGRUPO_FILE),
                    ("resumo", RESUMO_FILE)):
        manifesto["saidas"][nome] = {"arquivo": rel(p), "sha256": sha256_arquivo(p)}
    MANIFESTO_FILE.write_text(json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    log(f"G4: {veredito}; mapa com {len(mapa)} linhas ({int(mapa['tipica'].sum())} típicas); teste {teste['viavel']}")
    return 0 if not erros else 2


def verificar() -> int:
    if not MANIFESTO_FILE.exists():
        raise SystemExit("manifesto do G4 ausente; rode --etapa tudo")
    man = json.loads(MANIFESTO_FILE.read_text(encoding="utf-8"))
    erros = [n for n, s in man["saidas"].items()
             if not (ROOT / s["arquivo"]).exists() or sha256_arquivo(ROOT / s["arquivo"]) != s["sha256"]]
    if erros:
        raise SystemExit(f"verificar: saídas do G4 não conferem com o manifesto: {erros}")
    log("G4 conferido sem rede; nada gravado")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--etapa", choices=["verificar", "baixar", "consolidar", "tudo"], default="verificar")
    a = ap.parse_args()
    if a.etapa == "verificar":
        return verificar()
    if a.etapa in ("baixar", "tudo"):
        etapa_baixar()
        if a.etapa == "baixar":
            return 0
    return etapa_consolidar()


if __name__ == "__main__":
    sys.exit(main())
