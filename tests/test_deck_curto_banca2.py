"""Testes do deck curto da banca 2 (`docs/07_apresentacoes/banca2/04_conteudo_deck_curto.md`).

O deck curto é o único usado na versão final (decisão do autor de 26/10/2026; doc 06) e é derivado do doc 04 por
`scripts/apresentacao/gerar_deck_banca2.py` (modo padrão). Confere:

1. a estrutura obrigatória (doc 06): Hipótese, Dados, Análise descritiva, Metodologia, Identificação, Resultados,
   Robustez, Discussão, nesta ordem, e a sequência de slides pedida;
2. a regra do autor "texto demais": no máximo 30 palavras visíveis por slide, fora o título, a figura e a linha de
   fontes, no doc 04 e no próprio deck; especificações em até 4 linhas curtas, com a equação em palavras no centro;
3. a numeração da apresentação a partir de 26/10/2026 (H1 preenchimento; H2 bolsa × origem, antes H3; H3 oferta,
   antes H4), a H2 central em destaque e H1 e H3 em cinza;
4. a H1 principal do adendo 48b (marcada "aguardando 48b" enquanto as saídas HI_* não existem) e as medidas antigas
   como especificações secundárias, em Robustez;
5. a explicação da queda em 0,300 passo a passo (auditoria 33: a correção M1, sem "escolhidas em 1º lugar" como
   fato), as linhas do doc 57m marcadas "(em auditoria)", a H1 por ciclo e a linha simples da Discussão;
6. a regra dos números: todo número do doc 04 e do deck é o valor de um código listado ou um parâmetro;
7. o pacote gerado: títulos e texto iguais ao doc 04, rodapé com as oito seções, manifesto com hashes atuais e, se
   `PMME_DECK_GRUPO` apontar para o deck do grupo, o determinismo do `.pptx`.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import sys
import tempfile
import unittest
import zipfile
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAIDA = ROOT / "output" / "apresentacao_banca2"
DOC04 = ROOT / "docs" / "07_apresentacoes" / "banca2" / "04_conteudo_deck_curto.md"
DOC06 = ROOT / "docs" / "07_apresentacoes" / "banca2" / "06_estrutura_obrigatoria_versao_final.md"
NUMEROS = SAIDA / "numeros_banca2.json"
MANIF_FIG = SAIDA / "manifesto_figuras.json"
CURTO, MANIF = SAIDA / "deck_banca2_curto.pptx", SAIDA / "manifesto_deck_banca2_curto.json"
PDF = SAIDA / "deck_banca2_curto.pdf"
HI_RESUMO = ROOT / "output" / "rdd_bolsa" / "HI_resumo.json"


def _carregar(nome: str, caminho: Path):
    b = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    sys.dont_write_bytecode = b
    return mod


T = sys.modules.get("test_conteudo_banca2") or _carregar("test_conteudo_banca2", ROOT / "tests" / "test_conteudo_banca2.py")
D = sys.modules.get("gerar_deck_banca2") or _carregar("gerar_deck_banca2", ROOT / "scripts" / "apresentacao" / "gerar_deck_banca2.py")

SECOES = ("Hipótese", "Dados", "Análise descritiva", "Metodologia", "Identificação", "Resultados", "Robustez",
          "Discussão")
SEQUENCIA = [  # (seção, título, layout)
    ("Hipótese", "O que a bolsa de R$ 5 mil faz", "curto_capa"),
    ("Hipótese", "Hipóteses: a H2 é a candidata central", "curto_hipotese"),
    ("Dados", "Dados: as variáveis principais e de onde vêm", "curto_tabela"),
    ("Dados", "Dados: as variáveis secundárias", "curto_tabela"),
    ("Análise descritiva", "Os três ciclos em números", "curto_tabela"),
    ("Análise descritiva", "A bolsa é função exata do IVS: a regra é sharp", "curto_figura"),
    ("Análise descritiva", "A 1ª opção fica perto de onde o médico já trabalhava", "curto_figura"),
    ("Análise descritiva", "Nos dados crus, os dois lados preenchem igual", "curto_figura"),
    ("Análise descritiva", "Dentro da faixa de R$ 10 mil, o preenchimento sobe", "curto_figura"),
    ("Análise descritiva", "Perto de 0,300 sobra uma subida forte, sem explicação", "curto_figura"),
    ("Metodologia", "H1: o salto no corte, só com vagas imediatas", "curto_espec"),
    ("Metodologia", "H2: o logit condicional da 1ª opção", "curto_espec"),
    ("Metodologia", "H3: horas antes e depois de entrar", "curto_espec"),
    ("Identificação", "RDD: as premissas do desenho valem", "curto_tabela"),
    ("Identificação", "O corte é um pacote; a H3 pede tendências paralelas", "curto_tabela"),
    ("Resultados", "H1: vagas imediatas, por corte (aguardando 48b)", "curto_capa"),
    ("Resultados", "H2: a UF de origem pesa mais que toda a bolsa", "curto_figura"),
    ("Resultados", "H3: o médico soma horas, mas metade já estava lá", "curto_figura"),
    ("Robustez", "H1, medidas antigas: nenhum corte mostra aumento", "curto_figura"),
    ("Robustez", "Antes e depois do controle: em 0,400, passa pelas vagas", "curto_figura"),
    ("Robustez", "H1 por ciclo: a queda em 0,300 vem do ciclo 2", "curto_figura"),
    ("Robustez", "Em 0,300 é a estimativa no corte", "curto_figura"),
    ("Robustez", "As vagas do lado de cima eram diferentes", "curto_figura"),
    ("Robustez", "O que dá para afirmar sobre a queda", "curto_figura"),
    ("Robustez", "H2: por ciclo, a bolsa pesa só no ciclo 2", "curto_figura"),
    ("Robustez", "H3: na nota de corte, a mesma direção", "curto_figura"),
    ("Discussão", "Discussão: o sinal negativo da H1", "curto_capa"),
    ("Discussão", "Discussão: um incentivo limitado", "curto_texto"),
]
LINHA_DISCUSSAO = ("O sinal negativo não é a bolsa afastando médicos: é a estimativa no corte, com poucos municípios e "
                   "vagas diferentes.")
LINHA_POR_CICLO = ("A queda em 0,300 vem sobretudo do ciclo 2 (vagas de reserva); por ciclo, os intervalos são "
                   "largos.")
RAZAO_48B = "comparamos vagas do mesmo tipo: a de reserva não estava em jogo na 1ª chamada"


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def blocos_doc04() -> list[str]:
    t = DOC04.read_text(encoding="utf-8")
    corpo = t[t.index("<!-- deck:inicio -->"):t.index("<!-- deck:fim -->")]
    return [p for p in re.split(r"(?m)^(?=#{1,2} )", corpo) if p.startswith("## ")]


def tela(sl: dict) -> str:
    """O que vai à tela: linhas, cautela, selo e células da tabela (sem as notas)."""
    partes = [t for t, _ in D.linhas_curtas(sl)] + ([sl["selo"]] if sl["selo"] else [])
    partes += [c for linha in sl["tabela"] for c in linha]
    return " ".join(D.texto_puro(p).replace("**", "") for p in partes)


def corrido(txt: str) -> str:
    return " ".join(txt.replace(" ", " ").split())


@unittest.skipUnless(DOC04.exists() and NUMEROS.exists(), "doc 04 ou registro de números ausente")
class TestConteudoCurto(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.slides = D.ler_slides(D.DOC_CURTO)
        cls.blocos = blocos_doc04()
        num = json.loads(NUMEROS.read_text(encoding="utf-8"))
        cls.registro = num
        cls.todos = {c: e for b in ("numeros", "failure_mode", "texto_citado") for c, e in num[b].items()}
        cls.por_titulo = {s["titulo"]: s for s in cls.slides}

    def test_estrutura_obrigatoria(self) -> None:
        self.assertEqual(D.SECOES_CURTO, SECOES)
        D.conferir_estrutura(self.slides)
        self.assertEqual([(s["secao"], s["titulo"], s["layout"]) for s in self.slides], SEQUENCIA)
        self.assertFalse(any(s["apendice"] for s in self.slides))
        regra = " ".join(DOC06.read_text(encoding="utf-8").split())
        self.assertIn("30 palavras", regra)  # a regra do autor está registrada no doc 06, §2

    def test_no_maximo_30_palavras(self) -> None:
        for s in self.slides:
            D.conferir_curto(s)  # para (SystemExit) se fugir do formato
            self.assertLessEqual(D.palavras_visiveis(s), 30, s["titulo"])
            self.assertLessEqual(len(s["titulo"]), D.MAX_TITULO_CURTO, s["titulo"])
            self.assertEqual(s["layout"] == "curto_ficha", False, s["titulo"])  # fichas longas saíram

    def test_contagem_de_palavras_sintetica(self) -> None:
        self.assertEqual(D.palavras("**H2 · central** a bolsa → mais 1,98 [1,56; 2,40]"), 8)
        self.assertEqual(D.palavras("preenchida = salto + reta"), 3)

    def test_numeracao_das_hipoteses(self) -> None:
        """H1 preenchimento; H2 bolsa × origem (antes H3); H3 oferta (antes H4). Nada de H4 no deck curto."""
        corpo = DOC04.read_text(encoding="utf-8")
        deck = corpo[corpo.index("<!-- deck:inicio -->"):]
        self.assertNotIn("H4", re.sub(r"\(antes H4\)", "", deck))
        for s in self.slides:
            m = re.match(r"(H\d)\b", s["titulo"])
            if not m:
                continue
            self.assertIn(m.group(1), ("H1", "H2", "H3"), s["titulo"])
            if m.group(1) == "H2":
                self.assertTrue(any(k in s["titulo"] for k in ("origem", "logit", "bolsa pesa")), s["titulo"])
            if m.group(1) == "H3":
                self.assertTrue(any(k in s["titulo"] for k in ("horas", "nota de corte")), s["titulo"])
        hip = self.por_titulo["Hipóteses: a H2 é a candidata central"]
        rotulos = [re.match(r"\*\*(.+?)\*\*", m).group(1) for m in hip["marcadores"]]
        self.assertEqual(rotulos, ["H2 · central", "H1 · plano B", "H3 · plano B"])
        self.assertIn("H2 bolsa × origem (antes H3); H3 oferta (antes", corrido(hip["notas"]))
        reg = self.registro["numeracao_das_hipoteses"]
        self.assertIn("H2 bolsa × origem (antes H3); H3 oferta (antes H4)", reg)
        self.assertEqual(self.todos["H3_DUF"]["hipotese_apresentacao"], "H2")
        self.assertEqual(self.todos["P4_HT_ATT"]["hipotese_apresentacao"], "H3")
        self.assertEqual(self.todos["N1_300_TAU"]["hipotese_apresentacao"], "H1")

    def test_especificacoes_curtas(self) -> None:
        espec = [s for s in self.slides if s["layout"] == "curto_espec"]
        self.assertEqual([s["titulo"][:3] for s in espec], ["H1:", "H2:", "H3:"])
        for s in espec:
            self.assertLessEqual(len(s["marcadores"]), 4, s["titulo"])
            self.assertFalse(s["marcadores"][0].startswith("**"), s["titulo"])
            self.assertIn("=", s["marcadores"][0], s["titulo"])
            self.assertIn("rro-padrão", s["notas"], s["titulo"])  # o detalhe foi para as notas, não se perdeu
        h1 = espec[0]
        self.assertIn(RAZAO_48B, " ".join(h1["marcadores"]))
        self.assertIn("vaga imediata", " ".join(h1["marcadores"]))
        for k in ("HI-1", "HI-2", "Holm", "h = 0,050", "cada corte separado"):
            self.assertIn(k, corrido(h1["notas"]), k)

    def test_h1_principal_do_48b(self) -> None:
        res = [s for s in self.slides if s["secao"] == "Resultados"]
        self.assertTrue(res[0]["titulo"].startswith("H1:"))
        if HI_RESUMO.exists():
            self.assertNotIn("aguardando 48b", res[0]["titulo"])
            self.assertIn("HI_figuras", res[0]["imagem"].as_posix())
        else:
            self.assertIn("aguardando 48b", res[0]["titulo"])
            self.assertIn("Aguardando 48b", res[0]["marcadores"][0])
        # as medidas antigas (A3, N1, taxa por vaga) estão só em Robustez, como especificações secundárias
        for s in self.slides:
            if s["imagem"] is not None and s["imagem"].name in ("h1_preenchimento.png", "h1_controle.png",
                                                                "curto_h1_por_ciclo.png", "DQ_quanto_da_queda.png"):
                self.assertEqual(s["secao"], "Robustez", s["titulo"])

    def test_descritiva_dados_crus_e_subida(self) -> None:
        crus = self.por_titulo["Nos dados crus, os dois lados preenchem igual"]
        self.assertEqual(crus["imagem"].name, "curto_dispersao_a3.png")
        self.assertIn("nos dados crus os dois lados preenchem igual (33% e 33%)", " ".join(crus["marcadores"]))
        self.assertEqual(self.todos["DQ_FUN_PRE_ABX0"]["valor"], "33")
        self.assertEqual(self.todos["DQ_FUN_PRE_ACI0"]["valor"], "33")
        gf = [s for s in self.slides if s["imagem"] is not None and "GF_figuras" in s["imagem"].as_posix()]
        self.assertEqual(len(gf), 2)
        for s in gf:
            self.assertEqual(s["secao"], "Análise descritiva")
            self.assertIn("(em auditoria)", s["marcadores"][0], s["titulo"])
            self.assertIn("Em auditoria", s["notas"], s["titulo"])
        for c, e in self.todos.items():
            if c.startswith("GF_"):
                self.assertIn("EM AUDITORIA", e["auditoria"], c)
                self.assertIn("EM AUDITORIA", e["descricao"], c)
        self.assertIn("anda junto com a região (Nordeste)", gf[0]["marcadores"][0])
        self.assertIn("quase some", gf[0]["marcadores"][0])
        self.assertIn("sem fator que a acompanhe", gf[1]["marcadores"][0])

    def test_queda_passo_a_passo(self) -> None:
        rob = [s["titulo"] for s in self.slides if s["secao"] == "Robustez"]
        passos = ["Antes e depois do controle: em 0,400, passa pelas vagas", "Em 0,300 é a estimativa no corte",
                  "As vagas do lado de cima eram diferentes", "O que dá para afirmar sobre a queda"]
        self.assertEqual([t for t in rob if t in passos], passos)
        b = self.por_titulo["Em 0,300 é a estimativa no corte"]
        self.assertEqual(b["imagem"].name, "curto_reta_0300.png")
        tb = tela(b)
        for k in ("reta de baixo leva até o corte a subida dos últimos 0,050", "a ponta fica alta", "Médias iguais",
                  "salto negativo", "poucos municípios", "O acaso não está descartado"):
            self.assertIn(k, tb, k)
        c = self.por_titulo["As vagas do lado de cima eram diferentes"]
        self.assertTrue(c["imagem"].as_posix().endswith("output/rdd_bolsa/DQ_figuras/DQ_quanto_da_queda.png"))
        self.assertEqual(c["marcadores"], ["Cursos que preenchem pouco", "Mais células do curso na UF",
                                           "Ciclo 2: mais células só de reserva"])
        self.assertIn("nenhum fator nas três", c["cautela"])
        self.assertIn("pela metade ou mais", c["cautela"])
        # correção M1 da auditoria 33: "menos células escolhidas em 1º lugar" não vai à tela como fato
        for s in self.slides:
            self.assertNotIn("escolhidas em 1º lugar", tela(s), s["titulo"])
            self.assertNotIn("candidato de 1ª opção", tela(s), s["titulo"])
            self.assertNotIn("vagas de cursos", tela(s), s["titulo"])
        self.assertIn("estimativa imprecisa", c["notas"])
        for cod in re.findall(r"`(DQ_[A-Z0-9_]+)`", next(x for x in self.blocos if x.startswith("## As vagas"))):
            self.assertIn("auditoria 33", self.todos[cod].get("auditoria", ""), cod)
        d = self.por_titulo["O que dá para afirmar sobre a queda"]
        td = tela(d)
        for k in ("TOST", "sem aumento de 10 p.p. ou mais", '"nada mudou" não se sustenta',
                  "nenhum incentivo individual muda", "teto de emendas"):
            self.assertIn(k, td, k)
        self.assertIn("auditoria 35", d["notas"])
        self.assertIn("Nada disso mostra que a bolsa reduz o preenchimento", corrido(d["notas"]))
        self.assertFalse(any(s["selo"] for s in self.slides))

    def test_h1_por_ciclo(self) -> None:
        s = self.por_titulo["H1 por ciclo: a queda em 0,300 vem do ciclo 2"]
        self.assertEqual(s["imagem"].name, "curto_h1_por_ciclo.png")
        self.assertEqual(D.texto_puro(s["marcadores"][0]), LINHA_POR_CICLO)
        self.assertIn("confirmada no ciclo 1; alocada nos ciclos 2 e 3", s["cautela"])
        self.assertIn("auditoria 36", corrido(s["notas"]))
        man = json.loads(MANIF_FIG.read_text(encoding="utf-8"))
        linhas = man["figuras_novas"]["curto_h1_por_ciclo.png"]["linhas"]
        esperado = {f"HC_{m}_{c}_{k}_TAU" for m in ("A3", "TX") for c in ("1", "2", "3", "J") for k in ("300", "400")}
        self.assertEqual({ln["codigos"][0] for ln in linhas}, esperado)
        # os ciclos juntos repetem os números já publicados (A3 e taxa por vaga, doc 49b)
        self.assertEqual(self.todos["HC_A3_J_300_TAU"]["valor"], self.todos["A3_300_TAU"]["valor"])
        self.assertEqual(self.todos["HC_TX_J_300_TAU"]["valor"], self.todos["ND_TX300"]["valor"])

    def test_discussao(self) -> None:
        disc = [s for s in self.slides if s["secao"] == "Discussão"]
        self.assertEqual(D.texto_puro(disc[0]["marcadores"][0]), LINHA_DISCUSSAO)
        rot = [re.match(r"\*\*(.+?)\*\*", m).group(1) for m in disc[1]["marcadores"]]
        self.assertEqual(rot, ["Limitado", "Escolha", "Substituição"])

    def test_todo_numero_registrado_ou_parametro(self) -> None:
        sobra = {}
        permitidos_base = set(T.PERMITIDOS)
        for b in self.blocos:
            m = re.search(r"(?m)^\*\*Números:\*\*(.*?)(?=\n\n|\Z)", b, flags=re.S)
            self.assertIsNotNone(m, b.splitlines()[0])
            codigos = re.findall(r"`([A-Z0-9_]+)`", m.group(1))
            sem_linha = re.sub(r"(?m)^\*\*Números:\*\*.*?(?=\n\n|\Z)", "", b, flags=re.S)
            permitidos = set(permitidos_base)
            for c in codigos:
                self.assertIn(c, self.todos, c)
                self.assertIn(self.todos[c]["valor"], sem_linha, f"{c} listado e ausente")
                permitidos |= T.tokens(self.todos[c]["valor"])
            achados = {x for x in T.tokens(T.limpar(b)) if not T.ano(x)}
            if achados - permitidos:
                sobra[b.splitlines()[0]] = sorted(achados - permitidos)
        self.assertEqual(sobra, {})

    def test_cautelas_obrigatorias(self) -> None:
        texto = DOC04.read_text(encoding="utf-8")
        deck = " ".join(re.sub(r"(?m)^>\s?", "", texto[texto.index("<!-- deck:inicio -->"):]).split())
        for frase in ("pacote do corte", "Pacote do corte", "Pós-resultado", "H2 é pós-resultado",
                      "origem é preferência revelada, não efeito causal", "horas cadastradas não são presença",
                      "vínculo não é presença", "Associação", "não é a participação no PMM-E",
                      "Nada disso mostra que a bolsa reduz o preenchimento", "não é efeito zero",
                      "Escolha não é expansão", "escolha não é expansão"):
            self.assertIn(frase, deck, frase)
        self.assertNotIn("bolsa não funciona", deck)
        self.assertEqual(deck.count("a bolsa reduz"), deck.count("mostra que a bolsa reduz"))


def _sem_moldura(xml: str) -> str:
    """O XML do slide sem o título, o número da página, a navegação do rodapé e a linha de fontes."""
    return re.sub(r'<p:sp><p:nvSpPr><p:cNvPr id="\d+" name="(?:Título|Número da página|Navegação do rodapé|Fontes)"'
                  r'.*?</p:sp>', "", xml, flags=re.S)


@unittest.skipUnless(CURTO.exists() and MANIF.exists() and NUMEROS.exists(), "deck curto ausente")
class TestDeckCurto(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.deck = T._texto_slides(CURTO)
        cls.slides = D.ler_slides(D.DOC_CURTO)
        cls.man = json.loads(MANIF.read_text(encoding="utf-8"))
        num = json.loads(NUMEROS.read_text(encoding="utf-8"))
        cls.validos = T.PERMITIDOS | T.todos_valores(num)

    def test_titulos_e_texto_do_doc04(self) -> None:
        self.assertEqual([t for _, t, _ in self.deck], [s["titulo"] for s in self.slides])
        for sl, (_, titulo, texto) in zip(self.slides, self.deck):
            corr = " ".join(texto.replace(" ", " ").replace(".", "").split())
            for item in sl["marcadores"] + ([sl["cautela"]] if sl["cautela"] else []):
                self.assertIn(" ".join(D.texto_puro(item).replace("**", "").replace(".", "").split()), corr, titulo)
            for linha in sl["tabela"]:
                for cel in linha:
                    self.assertIn(" ".join(D.texto_puro(cel).replace(".", "").split()), corr, titulo)

    def test_numeros_do_deck_registrados(self) -> None:
        for _, titulo, texto in self.deck:
            achados = {x for x in T.tokens(T.limpar(texto.replace(" ", " "))) if not T.ano(x)}
            self.assertEqual(achados - self.validos, set(), titulo)

    def test_palavras_na_tela(self) -> None:
        """Regra do autor: no máximo 30 palavras visíveis por slide, fora o título, a figura e a linha de fontes."""
        with zipfile.ZipFile(CURTO) as z:
            for parte, titulo, _ in self.deck:
                x = _sem_moldura(z.read(parte).decode("utf-8"))
                texto = unescape(" ".join(re.findall(r"<a:t[^>]*>([^<]*)</a:t>", x)))
                n = sum(1 for w in texto.split() if re.search(r"[0-9A-Za-zÀ-ÿ]", w))
                self.assertLessEqual(n, D.MAX_PALAVRAS, f"{titulo}: {n} palavras")
        self.assertEqual(D.MAX_PALAVRAS, 30)
        self.assertTrue(all(o["palavras"] <= 30 for o in self.man["ordem"]))

    def test_rodape_com_as_oito_secoes(self) -> None:
        with zipfile.ZipFile(CURTO) as z:
            for (parte, titulo, _), sl in zip(self.deck, self.slides):
                x = z.read(parte).decode("utf-8")
                nav = re.search(r'name="Navegação do rodapé".*?</p:sp>', x, flags=re.S).group(0)
                self.assertEqual("".join(re.findall(r"<a:t[^>]*>([^<]*)</a:t>", nav)), "  |  ".join(SECOES), titulo)
                negrito = re.findall(r'<a:rPr[^>]* b="1"[^>]*>.*?<a:t[^>]*>([^<]*)</a:t>', nav, flags=re.S)
                self.assertEqual(negrito, [sl["secao"]], titulo)

    def test_hipotese_central_em_destaque(self) -> None:
        parte = next(p for p, t, _ in self.deck if t.startswith("Hipóteses"))
        with zipfile.ZipFile(CURTO) as z:
            x = z.read(parte).decode("utf-8")
        central = re.search(r'name="Rótulo central".*?</p:sp>', x, flags=re.S).group(0)
        self.assertIn(D.VERDE_ESCURO, central)
        planos = re.findall(r'name="Hipótese plano B".*?</p:sp>', x, flags=re.S)
        self.assertEqual(len(planos), 2)
        for p in planos:
            self.assertIn(D.CINZA_TEXTO, p)
            self.assertIn(D.CINZA_FUNDO, p)

    def test_letra_minima(self) -> None:
        with zipfile.ZipFile(CURTO) as z:
            for parte, titulo, _ in self.deck:
                x = z.read(parte).decode("utf-8")
                tam = [int(v) for v in re.findall(r'<a:rPr[^>]* sz="(\d+)"', _sem_moldura(x))]
                self.assertGreaterEqual(min(tam), 1400, titulo)
                self.assertNotIn('show="0"', x[:800], titulo)

    def test_sem_slides_do_grupo_e_manifesto(self) -> None:
        self.assertEqual(len(self.deck), len(SEQUENCIA))
        self.assertEqual([o["titulo"] for o in self.man["ordem"]], [t for _, t, _ in SEQUENCIA])
        self.assertEqual([o["secao"] for o in self.man["ordem"]], [s for s, _, _ in SEQUENCIA])
        for e in self.man["saidas"]:
            if e["caminho"].endswith(".pptx"):
                self.assertEqual(sha256(ROOT / e["caminho"]), e["sha256"], e["caminho"])
        for e in self.man["entradas"]:
            if e["caminho"].startswith(("docs/", "output/")):
                self.assertEqual(sha256(ROOT / e["caminho"]), e["sha256"], e["caminho"])
        self.assertTrue(PDF.exists())
        self.assertGreaterEqual(PDF.stat().st_mtime, CURTO.stat().st_mtime - 5)
        with zipfile.ZipFile(CURTO) as z:
            nomes = z.namelist()
        self.assertEqual(len([n for n in nomes if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)]), len(SEQUENCIA))

    def test_figuras_do_pipeline(self) -> None:
        """Toda figura do curto vem de output/: as de apresentacao_banca2 com o hash do manifesto de figuras; as de
        rdd_bolsa listadas no resumo da etapa que as gravou."""
        man = {f["arquivo"]: f["sha256"] for f in json.loads(MANIF_FIG.read_text(encoding="utf-8"))["figuras"]}
        for sl in self.slides:
            if sl["imagem"] is None:
                continue
            rel = sl["imagem"].relative_to(ROOT).as_posix()
            if rel.startswith("output/apresentacao_banca2/"):
                self.assertEqual(sha256(sl["imagem"]), man[rel], rel)
            else:
                etapa = Path(rel).parent.name
                resumo = json.loads((ROOT / T.RESUMO_DA_ETAPA[etapa]).read_text(encoding="utf-8"))
                self.assertIn(rel, json.dumps(resumo, ensure_ascii=False), rel)

    @unittest.skipUnless(os.environ.get("PMME_DECK_GRUPO") and Path(os.environ.get("PMME_DECK_GRUPO", "")).exists(),
                         "PMME_DECK_GRUPO não aponta para o deck do grupo")
    def test_deterministico(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            D.construir_curto(Path(os.environ["PMME_DECK_GRUPO"]), Path(tmp))
            self.assertEqual(sha256(Path(tmp) / D.ARQ_CURTO), sha256(CURTO))


if __name__ == "__main__":
    unittest.main()
