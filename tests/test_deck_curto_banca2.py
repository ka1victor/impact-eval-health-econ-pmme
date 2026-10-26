"""Testes do deck curto da banca 2 (`docs/07_apresentacoes/banca2/04_conteudo_deck_curto.md`).

O deck curto é derivado do doc 04 por `scripts/apresentacao/gerar_deck_banca2.py --curto`. Confere:

1. a sequência pedida pelo autor (26/10/2026): capa curta; identificação (antes → regra); H1 (ficha → antes e
   depois do controle → queda em 0,300, PRELIMINAR); H3 (ficha → resultado → o que quer dizer, com a H2 numa
   frase); H4 (ficha → resultado → o que quer dizer); conclusão. Sem slides do grupo, sem divisórias, sem
   apêndice, sem a H2 como slide próprio, sem a tabela "Um estimador por hipótese";
2. o formato: limites de linhas e de título, fichas só com tabela e letra de 14 pt ou mais;
3. as fichas do curto são recortes das fichas do deck completo (doc 02), com o mesmo texto linha a linha;
4. a regra dos números: todo número do doc 04 e do deck é o valor de um código listado ou um parâmetro;
5. as cautelas obrigatórias, o slide da queda em 0,300 em duas ideias (auditoria 33, sem selo) e a tradução do
   0,21 da H3;
6. o pacote gerado: títulos e texto iguais ao doc 04, manifesto com hashes atuais e, se `PMME_DECK_GRUPO`
   apontar para o deck do grupo, o determinismo do `.pptx`.
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
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAIDA = ROOT / "output" / "apresentacao_banca2"
DOC04 = ROOT / "docs" / "07_apresentacoes" / "banca2" / "04_conteudo_deck_curto.md"
DOC02 = ROOT / "docs" / "07_apresentacoes" / "banca2" / "02_conteudo_slides.md"
NUMEROS = SAIDA / "numeros_banca2.json"
CURTO, MANIF = SAIDA / "deck_banca2_curto.pptx", SAIDA / "manifesto_deck_banca2_curto.json"
PDF = SAIDA / "deck_banca2_curto.pdf"


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

SEQUENCIA = [  # (título, layout, papel no bloco)
    ("O que a bolsa de R$ 5 mil faz", "curto_capa", "capa"),
    ("A bolsa sai do IVS de 2010: dá para comparar no corte", "curto_texto", "antes"),
    ("A bolsa é função exata do IVS: a regra é sharp", "curto_figura", "resultado"),
    ("H1: bolsa maior → mais vagas preenchidas?", "curto_ficha", "antes"),
    ("Antes e depois do controle: em 0,400, passa pelas vagas", "curto_figura", "resultado"),
    ("Por que o preenchimento cai em 0,300", "curto_figura", "depois"),
    ("H3: a bolsa pesa pouco perto da origem do médico?", "curto_ficha", "antes"),
    ("H3: a UF de origem pesa mais que toda a bolsa", "curto_figura", "resultado"),
    ("O que isso quer dizer: incentivo limitado", "curto_texto", "depois"),
    ("H4: a chegada aumenta a oferta ou só remaneja?", "curto_ficha", "antes"),
    ("H4: o médico soma horas, mas metade já estava lá", "curto_figura", "resultado"),
    ("O que isso quer dizer: soma horas, mas em parte remaneja", "curto_texto", "depois"),
    ("A bolsa muda a escolha, não o preenchimento", "curto_texto", "conclusão"),
]
FICHA_COMPLETA = {"H1:": "## Especificação da H1", "H3:": "## Especificação da H2 e da H3", "H4:": "## Especificação da H4"}


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def blocos_doc04() -> list[str]:
    t = DOC04.read_text(encoding="utf-8")
    corpo = t[t.index("<!-- deck:inicio -->"):t.index("<!-- deck:fim -->")]
    return [p for p in re.split(r"(?m)^(?=#{1,2} )", corpo) if p.startswith("## ")]


def tabela_md(texto: str) -> list[tuple[str, str]]:
    linhas = []
    for ln in texto.splitlines():
        if ln.startswith("| ") and not re.fullmatch(r"[|\-: ]+", ln):
            cel = [c.strip() for c in ln.strip().split("|")[1:-1]]
            linhas.append((cel[0], cel[1]))
    return linhas[1:]


@unittest.skipUnless(DOC04.exists() and NUMEROS.exists(), "doc 04 ou registro de números ausente")
class TestConteudoCurto(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.slides = D.ler_slides(D.DOC_CURTO)
        cls.blocos = blocos_doc04()
        num = json.loads(NUMEROS.read_text(encoding="utf-8"))
        cls.todos = {c: e for b in ("numeros", "failure_mode", "texto_citado") for c, e in num[b].items()}

    def test_sequencia_antes_resultado_depois(self) -> None:
        self.assertEqual([(s["titulo"], s["layout"]) for s in self.slides], [(t, l) for t, l, _ in SEQUENCIA])
        self.assertFalse(any(s["apendice"] for s in self.slides))
        titulos = " ".join(s["titulo"] for s in self.slides)
        for fora in ("Um estimador por hipótese", "Quatro hipóteses", "H2:", "Nos dados crus"):
            self.assertNotIn(fora, titulos, fora)

    def test_formato_curto(self) -> None:
        for s in self.slides:
            D.conferir_curto(s)  # para (SystemExit) se fugir do formato
            self.assertLessEqual(len(s["titulo"]), D.MAX_TITULO_CURTO, s["titulo"])
            if s["layout"] == "curto_ficha":
                self.assertTrue(s["titulo"].startswith(("H1:", "H3:", "H4:")), s["titulo"])

    def test_fichas_sao_recortes_das_do_completo(self) -> None:
        t02 = DOC02.read_text(encoding="utf-8")
        for s, bloco in zip(self.slides, self.blocos):
            if s["layout"] != "curto_ficha":
                continue
            ini = t02.index(FICHA_COMPLETA[s["titulo"][:3]])
            completa = dict(tabela_md(t02[ini:t02.index("\n---", ini)]))
            curta = tabela_md(bloco)
            self.assertGreaterEqual(len(curta), 6, s["titulo"])
            for campo, texto in curta:
                self.assertEqual(texto, completa.get(campo), (s["titulo"], campo))
            campos = [c for c, _ in curta]
            for c in ("Outcome", "Amostra", "Equação em palavras", "Comum e por ciclo", "Erro-padrão", "Cuidado"):
                self.assertIn(c, campos, (s["titulo"], c))
        h1 = dict(tabela_md(next(b for b in self.blocos if b.startswith("## H1:"))))
        self.assertIn("vagas preenchidas = intercepto do ciclo + salto × (lado de bolsa maior) + reta de cada lado do "
                      "corte, por ciclo + coeficiente do ciclo × vagas oferecidas", h1["Equação em palavras"])
        self.assertIn("sem controle", h1["Equação em palavras"])
        self.assertIn("É causal?", dict(tabela_md(next(b for b in self.blocos if b.startswith("## H3:")))))

    def test_todo_numero_registrado_ou_parametro(self) -> None:
        sobra = {}
        for b in self.blocos:
            m = re.search(r"(?m)^\*\*Números:\*\*(.*?)(?=\n\n|\Z)", b, flags=re.S)
            self.assertIsNotNone(m, b.splitlines()[0])
            codigos = re.findall(r"`([A-Z0-9_]+)`", m.group(1))
            sem_linha = re.sub(r"(?m)^\*\*Números:\*\*.*?(?=\n\n|\Z)", "", b, flags=re.S)
            permitidos = set(T.PERMITIDOS)
            for c in codigos:
                self.assertIn(c, self.todos, c)
                self.assertIn(self.todos[c]["valor"], sem_linha, f"{c} listado e ausente")
                permitidos |= T.tokens(self.todos[c]["valor"])
            achados = {x for x in T.tokens(T.limpar(b)) if not T.ano(x)}
            if achados - permitidos:
                sobra[b.splitlines()[0]] = sorted(achados - permitidos)
        self.assertEqual(sobra, {})

    def test_queda_em_0300_em_duas_ideias(self) -> None:
        """Auditoria 33: sem selo, duas ideias e o fecho; "menos células com candidato" só como estimativa imprecisa."""
        dq = next(s for s in self.slides if s["titulo"].startswith("Por que o preenchimento"))
        self.assertEqual(dq["selo"], "")
        self.assertTrue(dq["imagem"].as_posix().endswith("output/rdd_bolsa/DQ_figuras/DQ_quanto_da_queda.png"))
        self.assertEqual([re.match(r"\*\*(.+?)\*\*", m).group(1) for m in dq["marcadores"]],
                         ["É a estimativa no corte, não os dados:", "As vagas do lado de cima eram diferentes:"])
        self.assertEqual(dq["cautela"], "**Nada disso mostra que a bolsa reduz o preenchimento: o corte junta a bolsa "
                                        "com outras regras.**")
        tela = " ".join(dq["marcadores"])
        self.assertNotIn("escolhidas em 1º lugar", tela)
        self.assertNotIn("candidato de 1ª opção", tela)
        self.assertIn("estimativa imprecisa", dq["notas"])
        bloco = next(b for b in self.blocos if b.startswith("## Por que o preenchimento"))
        codigos = re.findall(r"`(DQ_[A-Z0-9_]+)`", bloco)
        self.assertTrue(codigos)
        for c in codigos:
            self.assertIn("auditoria 33", self.todos[c].get("auditoria", ""), c)
        self.assertFalse(any(s["selo"] for s in self.slides))

    def test_h3_traduz_o_peso_e_absorve_a_h2(self) -> None:
        v = {c: e["valor"] for c, e in self.todos.items()}
        h3 = next(b for b in self.blocos if b.startswith("## H3: a UF"))
        self.assertIn(f"{v['H3_5B']} ≈ chance cerca de {v['M1_RC_PCT']}% maior de a vaga ser a 1ª opção, sem "
                      "distinção de zero; não é efeito no preenchimento", h3)
        depois = next(b for b in self.blocos if b.startswith("## O que isso quer dizer: incentivo"))
        self.assertIn(f"só o ciclo 2 mostra efeito, {v['M5_C2_RC']} [{v['M5_C2_RCI']}; {v['M5_C2_RCS']}]", depois)
        self.assertIn(f"{v['P1G_300_PREV']} e {v['P1G_400_PREV']}", depois)
        self.assertIn("leitura de", " ".join(depois.split()))

    def test_cautelas_obrigatorias(self) -> None:
        corrido = " ".join(re.sub(r"(?m)^>\s?", "", DOC04.read_text(encoding="utf-8")).split())
        for frase in ("pacote do corte", "Pacote do corte", "Pós-resultado", "preferência revelada, não efeito causal",
                      "horas cadastradas não são presença", "vínculo não é presença", "Associação",
                      "não é a participação no PMM-E", "Nada disso mostra que a bolsa reduz o preenchimento",
                      "inconclusivo não é efeito zero", "Escolha não é expansão"):
            self.assertIn(frase, corrido, frase)
        self.assertNotIn("bolsa não funciona", corrido)
        self.assertEqual(corrido.count("a bolsa reduz"), corrido.count("mostra que a bolsa reduz"))
        h4 = next(b for b in self.blocos if b.startswith("## O que isso quer dizer: soma horas"))
        self.assertIn("ainda está em análise", h4)  # protocolo 60, parte B, sem resultado no deck
        self.assertNotIn("OL_", h4)


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
            corrido = " ".join(texto.replace(" ", " ").replace(".", "").split())
            for item in sl["marcadores"] + ([sl["cautela"]] if sl["cautela"] else []) + ([sl["selo"]] if sl["selo"] else []):
                self.assertIn(" ".join(D.texto_puro(item).replace("**", "").replace(".", "").split()), corrido, titulo)
            for linha in sl["tabela"]:
                for cel in linha:
                    self.assertIn(" ".join(D.texto_puro(cel).replace(".", "").split()), corrido, titulo)

    def test_numeros_do_deck_registrados(self) -> None:
        for _, titulo, texto in self.deck:
            achados = {x for x in T.tokens(T.limpar(texto.replace(" ", " "))) if not T.ano(x)}
            self.assertEqual(achados - self.validos, set(), titulo)

    def test_letra_minima(self) -> None:
        with zipfile.ZipFile(CURTO) as z:
            for parte, titulo, _ in self.deck:
                x = z.read(parte).decode("utf-8")
                sem_fontes = re.sub(r'<p:sp><p:nvSpPr><p:cNvPr id="\d+" name="(?:Fontes|Navegação do rodapé)".*?</p:sp>',
                                    "", x, flags=re.S)
                tam = [int(v) for v in re.findall(r'<a:rPr[^>]* sz="(\d+)"', sem_fontes)]
                self.assertGreaterEqual(min(tam), 1400, titulo)
                self.assertNotIn('show="0"', x[:800], titulo)

    def test_sem_slides_do_grupo_e_manifesto(self) -> None:
        self.assertEqual(len(self.deck), len(SEQUENCIA))
        self.assertEqual([o["titulo"] for o in self.man["ordem"]], [t for t, _, _ in SEQUENCIA])
        for e in self.man["saidas"]:
            if e["caminho"].endswith(".pptx"):
                self.assertEqual(sha256(ROOT / e["caminho"]), e["sha256"], e["caminho"])
        for e in self.man["entradas"]:
            if e["caminho"].startswith(("docs/", "output/")):
                self.assertEqual(sha256(ROOT / e["caminho"]), e["sha256"], e["caminho"])
        self.assertTrue(PDF.exists())
        with zipfile.ZipFile(CURTO) as z:
            nomes = z.namelist()
        self.assertEqual(len([n for n in nomes if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)]), len(SEQUENCIA))

    @unittest.skipUnless(os.environ.get("PMME_DECK_GRUPO") and Path(os.environ.get("PMME_DECK_GRUPO", "")).exists(),
                         "PMME_DECK_GRUPO não aponta para o deck do grupo")
    def test_deterministico(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            D.construir_curto(Path(os.environ["PMME_DECK_GRUPO"]), Path(tmp))
            self.assertEqual(sha256(Path(tmp) / D.ARQ_CURTO), sha256(CURTO))


if __name__ == "__main__":
    unittest.main()
