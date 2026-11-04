"""Slides de apoio da banca 2: como ler e como foi feito o logit condicional com o par de UFs (VL-1, adendo 52e).

Entrada (só leitura): o conteúdo canônico `docs/07_apresentacoes/banca2/11_explicacoes_metodo_logit.md`; o template
`output/apresentacao_banca2/deck_banca2_curto.pptx` (mestre, layout, rodapé e logotipo do deck curto); os números de
`output/rdd_bolsa/VL_estimativas.csv` e `VL_resumo.json`; os scripts citados no slide de código.

Saídas, em `output/apresentacao_banca2/`:

* `slides_explicacoes_logit.pptx`: um slide por `##` do doc 11, no estilo do deck curto;
* `slides_explicacoes_logit.pdf`: o PDF, pelo LibreOffice, se houver;
* `manifesto_slides_explicacoes_logit.json`: entradas e saídas com SHA-256 e a ordem dos slides.

Proveniência: nada é estimado aqui e nada é lido de `data/`. O script recalcula cada número citado no doc a partir de
`output/rdd_bolsa/VL_*` e para se o doc não trouxer exatamente o valor recalculado; no slide de código, para se alguma
linha mostrada não existir, igual, na linha indicada do arquivo. Determinístico: reaproveita as funções do gerador do
deck curto (`gerar_deck_banca2.py`) e o zip com data fixa.

Uso:

    python3 scripts/apresentacao/gerar_slides_explicacoes_logit.py
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs" / "07_apresentacoes" / "banca2" / "11_explicacoes_metodo_logit.md"
SAIDA = ROOT / "output" / "apresentacao_banca2"
TEMPLATE = SAIDA / "deck_banca2_curto.pptx"
VL_EST = ROOT / "output" / "rdd_bolsa" / "VL_estimativas.csv"
VL_RES = ROOT / "output" / "rdd_bolsa" / "VL_resumo.json"
ARQ = "slides_explicacoes_logit.pptx"
ARQ_PDF = "slides_explicacoes_logit.pdf"
ARQ_MANIF = "manifesto_slides_explicacoes_logit.json"


def _carregar(nome: str, caminho: Path):
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    antes = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.dont_write_bytecode = antes
    return mod


G = _carregar("gerar_deck_banca2", ROOT / "scripts" / "apresentacao" / "gerar_deck_banca2.py")
BF = G.BF
Slide, para, run, runs_md = G.Slide, G.para, G.run, G.runs_md
X0, X1, Y0, Y_FONTES = G.X0, G.X1, G.Y0, G.Y_FONTES
VERDE_ESCURO, VERDE, TEXTO, BRANCO, MUDO = G.VERDE_ESCURO, G.VERDE, G.TEXTO, G.BRANCO, G.MUDO
FONTE_CODIGO = "Courier New"
LAYOUTS = ("espec", "ficha", "tabela_cartoes", "codigo")
CAMPOS = ("secao", "layout", "equacao", "cartao", "cautela", "fontes", "notas")


class Falha(SystemExit):
    pass


# --------------------------------------------------------------------------------------------------
# Leitura do doc 11
# --------------------------------------------------------------------------------------------------

def ler_slides(doc: Path = DOC) -> list[dict]:
    t = doc.read_text(encoding="utf-8")
    corpo = t[t.index("<!-- slides:inicio -->"):t.index("<!-- slides:fim -->")]
    slides: list[dict] = []
    sl: dict | None = None
    passo: dict | None = None
    em_codigo = False
    for ln in corpo.splitlines():
        if em_codigo:
            if ln.startswith("```"):
                em_codigo = False
            else:
                passo["codigo"].append(ln)
            continue
        if ln.startswith("## "):
            sl = {"titulo": ln[3:].strip(), "cartao": [], "tabela": [], "passos": []}
            for c in CAMPOS:
                sl.setdefault(c, None)
            sl["cartao"] = []
            slides.append(sl)
            passo = None
            continue
        if sl is None:
            continue
        if ln.startswith("### Passo:"):
            rot, _, onde = ln[len("### Passo:"):].partition("|")
            arq, _, linhas = onde.strip().rpartition(":")
            passo = {"rotulo": rot.strip(), "arquivo": arq.strip(),
                     "linhas": [int(x) for x in linhas.split(",")], "codigo": []}
            sl["passos"].append(passo)
            continue
        if ln.startswith("```"):
            if passo is None:
                raise Falha(f"ERRO: bloco de código fora de um passo em {sl['titulo']!r}")
            em_codigo = True
            continue
        m = re.match(r"- (\w+): (.*)", ln)
        if m and m.group(1) in CAMPOS:
            if m.group(1) == "cartao":
                sl["cartao"].append(m.group(2).strip())
            else:
                sl[m.group(1)] = m.group(2).strip()
            continue
        if ln.startswith("|"):
            cel = G._celulas(ln)
            if not all(re.fullmatch(r":?-+:?", c) for c in cel):
                sl["tabela"].append(cel)
    for sl in slides:
        if sl["layout"] not in LAYOUTS:
            raise Falha(f"ERRO: layout {sl['layout']!r} desconhecido em {sl['titulo']!r}")
        if sl["secao"] not in G.SECOES_CURTO:
            raise Falha(f"ERRO: seção {sl['secao']!r} fora da estrutura do deck curto em {sl['titulo']!r}")
        if len(sl["titulo"]) > G.MAX_TITULO_CURTO:
            raise Falha(f"ERRO: título longo demais (encosta no logotipo): {sl['titulo']!r}")
        if not sl["fontes"] or not sl["notas"]:
            raise Falha(f"ERRO: slide sem fontes ou sem notas: {sl['titulo']!r}")
    return slides


# --------------------------------------------------------------------------------------------------
# Proveniência: cada número do doc é recalculado de output/
# --------------------------------------------------------------------------------------------------

def _n(x: float, casas: int = 2) -> str:
    s = f"{abs(x):,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return ("−" if x < 0 and round(abs(x), casas) != 0 else "") + s


def _int(x: float) -> str:
    return f"{int(x):,}".replace(",", ".")


def _ic(r: pd.Series) -> str:
    return f"{_n(r.estimativa)} [{_n(r.ic95_inf)}; {_n(r.ic95_sup)}]"


def numeros_esperados() -> dict[str, str]:
    est = pd.read_csv(VL_EST)
    if not (est["natureza_dos_dados"] == "EMPIRICO").all():
        raise Falha("ERRO: VL_estimativas.csv com linha não empírica")
    res = json.loads(VL_RES.read_text(encoding="utf-8"))

    def linha(chave: str, tipo: str, termo: str) -> pd.Series:
        s = est[(est.chave_modelo == chave) & (est.tipo_linha == tipo) & (est.termo == termo)]
        if len(s) != 1:
            raise Falha(f"ERRO: esperava uma linha {chave}/{tipo}/{termo}, achei {len(s)}")
        if s.iloc[0]["status"] != "EXECUTADO":
            raise Falha(f"ERRO: linha {chave}/{tipo}/{termo} não executada")
        return s.iloc[0]

    rc1 = linha("VL1_emp", "razao_chances_por_5mil", "bolsa_mil")
    b1 = linha("VL1_emp", "coeficiente", "bolsa_mil")
    d1 = linha("VL1_emp", "coeficiente", "distancia_100km")
    k5 = linha("VL1_emp", "km_equivalentes", "K5")
    rcl = linha("VL1log_emp", "razao_chances_por_5mil", "bolsa_mil")
    rc2 = linha("VL2_emp", "razao_chances_por_5mil", "bolsa_mil")
    q1 = [linha(c, "coeficiente", f"ivs_mudanca_inclinacao_{k}") for c in ("VL1_emp", "VL2_emp")
          for k in ("0300", "0400")]
    ident = res["identificacao"]["VL1_emp"]["identificacao"]
    meia = (math.log(rc1.ic95_sup) - math.log(rc1.ic95_inf)) / 2
    if abs(5 * b1.estimativa - math.log(rc1.estimativa)) > 1e-9:
        raise Falha("ERRO: razão de chances do VL-1 diferente de exp(5β)")
    if ident["alternativas_no_modelo"] != int(b1.n_linhas_candidato_celula):
        raise Falha("ERRO: linhas do VL-1 diferem entre o CSV e o resumo")
    return {
        "razão de chances do VL-1": _ic(rc1),
        "5β": _n(5 * b1.estimativa, 3),
        "meia largura do IC em log": f"± {_n(meia)}",
        "aumento ≈ %": f"≈ {round((rc1.estimativa - 1) * 100)}%",
        "peso da distância": f"{_n(d1.estimativa, 3)} por 100 km",
        "km equivalentes": f"{round(k5.estimativa)} km",
        "km na razão": f"{_n(5 * b1.estimativa, 3)} ÷ {_n(-d1.estimativa, 3)} × 100 km",
        "log da distância": _ic(rcl),
        "VL-2": _ic(rc2),
        "dobras": " | ".join(f"| {_n(q.estimativa)} |" for q in q1),
        "candidatos VL-1": _int(b1.n_candidatos),
        "linhas VL-1": _int(b1.n_linhas_candidato_celula),
        "conjuntos VL-1": f"{int(b1.n_conjuntos)}",
        "vagas por candidato": f"≈ {round(b1.n_linhas_candidato_celula / b1.n_candidatos)} vagas",
        "candidatos VL-2": _int(rc2.n_candidatos),
        "pares": f"{ident['pares_no_desenho']} → {ident['pares_com_escolha']} pares",
        "pares com variação": f"{ident['pares_com_variacao_de_bolsa']} pares",
        "dummies": f"{ident['colunas_de_efeito_fixo']} dummies",
        "candidatos com variação": f"{_int(ident['candidatos_com_variacao_de_bolsa_em_algum_par'])} candidatos",
    }


def conferir_numeros(slides: list[dict]) -> dict[str, str]:
    """Cada número esperado tem de aparecer, igual, no texto dos slides do doc (tela, tabela ou notas)."""
    texto = DOC.read_text(encoding="utf-8")
    corpo = texto[texto.index("<!-- slides:inicio -->"):texto.index("<!-- slides:fim -->")]
    esp = numeros_esperados()
    faltam = []
    for nome, valor in esp.items():
        if nome == "dobras":
            for v in valor.split(" | "):
                if v.strip("| ").strip() not in corpo:
                    faltam.append(f"{nome}: {v}")
            continue
        if valor not in corpo:
            faltam.append(f"{nome}: {valor}")
    if faltam:
        raise Falha("ERRO: números do doc 11 divergem de output/rdd_bolsa/VL_*: " + "; ".join(faltam))
    return esp


def conferir_codigo(slides: list[dict]) -> list[dict]:
    """Cada linha de código mostrada existe, igual, na linha indicada do arquivo."""
    out = []
    for sl in slides:
        for p in sl["passos"]:
            arq = ROOT / p["arquivo"]
            linhas = arq.read_text(encoding="utf-8").splitlines()
            if len(p["linhas"]) != len(p["codigo"]):
                raise Falha(f"ERRO: {p['rotulo']!r}: {len(p['codigo'])} linhas de código para {len(p['linhas'])} números")
            for k, cod in zip(p["linhas"], p["codigo"]):
                if linhas[k - 1].strip() != cod.strip():
                    raise Falha(f"ERRO: {p['arquivo']}:{k} não é {cod.strip()!r}")
            out.append({"arquivo": p["arquivo"], "linhas": p["linhas"], "sha256": sha256_arq(arq)})
    return out


# --------------------------------------------------------------------------------------------------
# Montagem
# --------------------------------------------------------------------------------------------------

def _partes_cartao(txt: str) -> tuple[str, str]:
    m = re.match(r"\*\*(.+?)\*\*\s*(.*)", txt)
    if not m:
        raise Falha(f"ERRO: cartão sem rótulo em negrito: {txt!r}")
    return m.group(1), m.group(2)


def cartoes(s: Slide, itens: list[str], x: float, y: float, w: float, y_fim: float, w_rot: float = 2.4,
            sz: float = 20.0, gap: float = 0.2) -> None:
    h_i = (y_fim - y - gap * (len(itens) - 1)) / len(itens)
    for it in itens:
        rot, corpo = _partes_cartao(it)
        s.forma("Rótulo", x, y, w_rot, h_i, adj=10000, fill=VERDE_ESCURO, anchor="ctr",
                paras=[para([run(rot, sz, BRANCO, b=True)], "ctr")])
        s.forma("Item", x + w_rot + 0.15, y, w - w_rot - 0.15, h_i, adj=6000, fill="F4F8F5", line=VERDE,
                line_w=1.0, anchor="ctr", ins=(0.25, 0.04, 0.25, 0.04),
                paras=[para(runs_md(corpo, sz, TEXTO, cor_neg=VERDE_ESCURO), "l", linha=102)])
        y += h_i + gap


def equacao(s: Slide, eq: str, y: float, h: float) -> None:
    partes = eq.replace(";  ", ";\n").split("\n") if len(eq) > 60 else [eq]
    sz = 28 if len(eq) <= 60 else 24
    s.forma("Equação", X0, y, X1 - X0, h, adj=8000, fill=VERDE_ESCURO, anchor="ctr", ins=(0.4, 0.08, 0.4, 0.08),
            paras=[para(G.runs_equacao(p, sz, BRANCO), "ctr") for p in partes])


def montar(sl: dict) -> str:
    s = Slide()
    W = X1 - X0
    y_fim = Y_FONTES - 0.1
    if sl["cautela"]:
        y_c = y_fim - G.H_LINHA_CURTA
        G._linha_curta(s, sl["cautela"], True, y_c)
        y_fim = y_c - 0.18
    lay = sl["layout"]
    if lay == "espec":
        h_eq = 1.75
        equacao(s, sl["equacao"], Y0 + 0.05, h_eq)
        cartoes(s, sl["cartao"], X0, Y0 + 0.05 + h_eq + 0.3, W, y_fim)
    elif lay == "ficha":
        G.tabela(s, sl["tabela"], X0, Y0 + 0.05, W, y_fim - Y0 - 0.05, sz_max=22, sz_min=G.SZ_TAB_CORPO,
                 onde=sl["titulo"])
    elif lay == "tabela_cartoes":
        w_t = 5.2
        G.tabela(s, sl["tabela"], X0, Y0 + 0.05, w_t, y_fim - Y0 - 0.05, sz_max=22, sz_min=G.SZ_TAB_CORPO,
                 onde=sl["titulo"])
        cartoes(s, sl["cartao"], X0 + w_t + 0.3, Y0 + 0.05, W - w_t - 0.3, y_fim, w_rot=1.9, sz=18)
    elif lay == "codigo":
        n = len(sl["passos"])
        gap = 0.16
        h_rot = 0.42
        disp = y_fim - Y0 - 0.05 - gap * (n - 1)
        pesos = [h_rot + 0.2 + len(p["codigo"]) * 0.33 for p in sl["passos"]]
        y = Y0 + 0.05
        for p, peso in zip(sl["passos"], pesos):
            h = disp * peso / sum(pesos)
            s.forma("Passo", X0, y, W, h_rot, adj=10000, fill=VERDE_ESCURO, anchor="ctr", ins=(0.2, 0.02, 0.2, 0.02),
                    paras=[para([run(p["rotulo"], 16, BRANCO, b=True),
                                 run("   " + p["arquivo"].split("/")[-1] + ":" + ",".join(map(str, p["linhas"])),
                                     12, "DDEFE0")], "l")])
            cod = []
            for c in p["codigo"]:
                r = (f'<a:r><a:rPr lang="en-US" sz="1500" b="0" dirty="0"><a:solidFill><a:srgbClr val="{TEXTO}"/>'
                     f'</a:solidFill><a:latin typeface="{FONTE_CODIGO}"/><a:cs typeface="{FONTE_CODIGO}"/></a:rPr>'
                     f'<a:t xml:space="preserve">{G.escape(c.strip())}</a:t></a:r>')
                cod.append(para([r], "l", linha=100))
            s.forma("Código", X0, y + h_rot, W, h - h_rot, geom="rect", fill="F4F8F5", line=VERDE, line_w=1.0,
                    anchor="ctr", ins=(0.25, 0.04, 0.25, 0.04), paras=cod)
            y += h + gap
    G.linha_fontes(s, sl["fontes"])
    return G.xml_slide_curto(sl["titulo"], sl["secao"], s.partes)


def sha256_arq(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def construir(slides: list[dict], saida: Path) -> list[dict]:
    """Os slides do template saem; entram os do doc 11, no layout `1_Title Slide` do deck curto."""
    pk = BF.Pacote(TEMPLATE)
    pres = pk.texto("ppt/presentation.xml")
    rels = pk.texto("ppt/_rels/presentation.xml.rels")
    ct = pk.texto("[Content_Types].xml")
    layout = "slideLayout14.xml"
    if 'name="1_Title Slide"' not in pk.texto("ppt/slideLayouts/" + layout):
        raise Falha("ERRO: layout 1_Title Slide não está em slideLayout14.xml do template")
    ids = [int(i) for i in re.findall(r'<p:sldId id="(\d+)"', pres)]
    rids = [int(r[3:]) for r in re.findall(r'Id="(rId\d+)"', rels)]
    n_slide = max(int(re.search(r"slide(\d+)\.xml", n).group(1)) for n in pk.partes
                  if re.fullmatch(r"ppt/slides/slide\d+\.xml", n))
    n_notas = max(int(re.search(r"notesSlide(\d+)\.xml", n).group(1)) for n in pk.partes
                  if re.fullmatch(r"ppt/notesSlides/notesSlide\d+\.xml", n))
    rels = re.sub(r'<Relationship Id="rId\d+" Type="[^"]*/relationships/slide" Target="slides/[^"]*"/>', "", rels)
    itens, ordem = [], []
    for k, sl in enumerate(slides):
        ns, nn, rid = n_slide + 1 + k, n_notas + 1 + k, f"rId{max(rids) + 1 + k}"
        pk.gravar(f"ppt/slides/slide{ns}.xml", montar(sl))
        pk.gravar(f"ppt/slides/_rels/slide{ns}.xml.rels",
                  '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                  '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                  f'<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/{layout}"/>'
                  f'<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide" Target="../notesSlides/notesSlide{nn}.xml"/>'
                  '</Relationships>')
        notas = [sl["notas"]] + ([f"Cautela na tela: {sl['cautela']}"] if sl["cautela"] else [])
        pk.gravar(f"ppt/notesSlides/notesSlide{nn}.xml", G.xml_notas_paragrafos([G.texto_puro(n) for n in notas]))
        pk.gravar(f"ppt/notesSlides/_rels/notesSlide{nn}.xml.rels",
                  '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                  '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                  '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesMaster" Target="../notesMasters/notesMaster1.xml"/>'
                  f'<Relationship Id="rId2" Type="{G.REL_SLIDE}" Target="../slides/slide{ns}.xml"/>'
                  '</Relationships>')
        rels = rels.replace("</Relationships>",
                            f'<Relationship Id="{rid}" Type="{G.REL_SLIDE}" Target="slides/slide{ns}.xml"/></Relationships>')
        ct = ct.replace("</Types>",
                        f'<Override PartName="/ppt/slides/slide{ns}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
                        f'<Override PartName="/ppt/notesSlides/notesSlide{nn}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml"/></Types>')
        itens.append((str(max(ids) + 1 + k), rid))
        ordem.append({"posicao": k + 1, "titulo": sl["titulo"], "secao": sl["secao"], "layout": sl["layout"]})
    nova = "<p:sldIdLst>" + "".join(f'<p:sldId id="{i}" r:id="{r}"/>' for i, r in itens) + "</p:sldIdLst>"
    pres = re.sub(r"<p:sldIdLst>.*?</p:sldIdLst>", lambda _m: nova, pres, count=1, flags=re.S)
    pk.gravar("ppt/presentation.xml", pres)
    pk.gravar("ppt/_rels/presentation.xml.rels", rels)
    pk.gravar("[Content_Types].xml", ct)
    manter = BF.alcancaveis(pk)
    ct_p = re.sub(r'<Override PartName="/([^"]+)"[^>]*/>',
                  lambda m: m.group(0) if m.group(1) in manter or m.group(1) not in pk.partes else "", ct)
    pk.gravar("[Content_Types].xml", ct_p)
    pk.salvar(saida / ARQ, manter=manter | {"[Content_Types].xml"})
    return ordem


def main() -> int:
    slides = ler_slides()
    numeros = conferir_numeros(slides)
    codigo = conferir_codigo(slides)
    SAIDA.mkdir(parents=True, exist_ok=True)
    ordem = construir(slides, SAIDA)
    com_pdf = G.converter_pdf(SAIDA / ARQ, SAIDA / ARQ_PDF)
    entradas = [{"arquivo": p.relative_to(ROOT).as_posix(), "sha256": sha256_arq(p)}
                for p in (DOC, TEMPLATE, VL_EST, VL_RES)]
    saidas = [{"arquivo": (SAIDA / a).relative_to(ROOT).as_posix(), "sha256": sha256_arq(SAIDA / a)}
              for a in ([ARQ] + ([ARQ_PDF] if com_pdf else []))]
    man = {"natureza_dos_dados": "EMPIRICO",
           "estatuto": "material de apoio da banca 2; nenhuma estimativa nova (adendo 52e, doc 57x, auditoria 48)",
           "script": "scripts/apresentacao/gerar_slides_explicacoes_logit.py",
           "entradas": entradas, "codigo_conferido": codigo, "numeros_conferidos": numeros,
           "slides": ordem, "saidas": saidas,
           "nota_pdf": None if com_pdf else "LibreOffice ausente: PDF não gerado"}
    (SAIDA / ARQ_MANIF).write_text(json.dumps(man, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(slides)} slides em {(SAIDA / ARQ).relative_to(ROOT)}" + (" (+ PDF)" if com_pdf else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
