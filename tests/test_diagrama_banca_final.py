"""Testes do diagrama causal da banca final (`docs/07_apresentacoes/banca_final/`).

O diagrama é teoria: não pode trazer número de resultado. Os testes conferem

1. os arquivos de conteúdo e de saída;
2. o texto exibido nas formas do diagrama: só números da regra da bolsa, anos de
   citação e numeração dos passos; nenhum termo proibido pelo `CLAUDE.md`;
3. o doc 01 contra as constantes do script (bloco gerado) e cada texto exibido
   contra o doc 01 (o deck é derivado do conteúdo canônico);
4. o pptx: formas nativas (sem imagem), 38 slides no deck proposto, slides de
   equações depois do divisor "Apêndice", sem perda de slide;
5. o manifesto: hashes atuais; determinismo, se o deck do grupo estiver acessível
   (variável de ambiente `PMME_DECK_GRUPO`).

Nada aqui lê `data/` nem estima nada.
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
SCRIPT = ROOT / "scripts" / "apresentacao" / "gerar_diagrama_banca_final.py"
DOCS = ROOT / "docs" / "07_apresentacoes" / "banca_final"
DOC01, README = DOCS / "01_diagrama_teoria_mudanca.md", DOCS / "README.md"
SAIDA = ROOT / "output" / "apresentacao_banca_final"
SLIDES, DECK, MANIFESTO = (SAIDA / "slides_diagrama_teoria_mudanca.pptx", SAIDA / "deck_proposta_reorganizada.pptx",
                           SAIDA / "manifesto_diagrama.json")
TEM_SAIDAS = SLIDES.exists() and DECK.exists() and MANIFESTO.exists()

_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location("gerar_diagrama_banca_final", SCRIPT)
G = importlib.util.module_from_spec(_spec)
sys.modules["gerar_diagrama_banca_final"] = G
_spec.loader.exec_module(G)
sys.dont_write_bytecode = _bytecode

PROIBIDOS = ["funciona", "não funciona", "nao funciona", "SGETS", "especialidade", "177", "é o piso", "0,500", "%",
             "p <", "p =", "intervalo de confiança", "efeito de ", "ivs_ipea_2010_municipios"]
# o que pode aparecer como número: cortes e valores da regra aplicada, o incentivo marginal e os anos das citações
PERMITIDOS = [r"0,300", r"0,301", r"0,400", r"R\$ (?:5|10|15|20) mil", r"\b(?:2001|2010|2011|2017|2020)\b"]


def texto_das_formas(xml: str) -> list[str]:
    """Texto de cada `a:t` do corpo do diagrama (sem o título do template, o número da página e o rodapé de navegação)."""
    corpo = re.sub(r'<p:sp><p:nvSpPr><p:cNvPr id="[234]" name="(?:Título|Número da página|Navegação do rodapé)".*?</p:sp>',
                   "", xml, flags=re.S)
    achados = [t.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">") for t in re.findall(r"<a:t>([^<]*)</a:t>", corpo)]
    return [t.strip(" ·") for t in achados if t.strip(" ·")]


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


class TestArquivos(unittest.TestCase):
    def test_conteudo_canonico_existe(self) -> None:
        for p in (DOC01, README, SCRIPT):
            self.assertTrue(p.exists(), p)
        self.assertIn("01_diagrama_teoria_mudanca.md", README.read_text(encoding="utf-8"))

    def test_saidas_existem(self) -> None:
        for p in (SLIDES, DECK, MANIFESTO):
            self.assertTrue(p.exists(), f"{p.relative_to(ROOT)} ausente: rode o gerador com --deck")

    def test_registro_de_mudancas_e_indice(self) -> None:
        reg = (ROOT / "docs" / "00_registro_mudancas.md").read_text(encoding="utf-8")
        self.assertIn("07_apresentacoes/banca_final/", reg)
        self.assertIn("gerar_diagrama_banca_final.py", reg)
        indice = (ROOT / "docs" / "07_apresentacoes" / "README.md").read_text(encoding="utf-8")
        self.assertIn("banca_final/", indice)

    def test_nao_toca_arquivo_errado_de_ivs(self) -> None:
        for p in (SCRIPT, DOC01, README):
            self.assertNotIn("ivs_ipea_2010_municipios", p.read_text(encoding="utf-8"), p.name)

    def test_nao_grava_em_data(self) -> None:
        self.assertTrue(str(G.SAIDA).startswith(str(ROOT / "output")))
        self.assertFalse(re.search(r"ROOT\s*/\s*[\"']data[\"']", SCRIPT.read_text(encoding="utf-8")))


class TestTextoDoDiagrama(unittest.TestCase):
    def setUp(self) -> None:
        self.xmls = {"A": G.montar_slide_a(), "B": G.montar_slide_b()}

    def test_so_numero_da_regra_citacao_e_passo(self) -> None:
        for k, xml in self.xmls.items():
            for t in texto_das_formas(xml):
                if re.fullmatch(r"\d", t):  # numeração dos passos
                    continue
                resto = t
                for padrao in PERMITIDOS:
                    resto = re.sub(padrao, "", resto)
                self.assertFalse(re.search(r"\d", resto), f"slide {k}: número fora da regra em {t!r}")

    def test_sem_termo_proibido(self) -> None:
        for k, xml in self.xmls.items():
            todo = " ".join(texto_das_formas(xml)) + " " + G.TITULO_A + " " + G.TITULO_B
            for termo in PROIBIDOS:
                self.assertNotIn(termo, todo, f"slide {k}: {termo!r}")

    def test_regra_da_bolsa_aplicada(self) -> None:
        self.assertEqual(G.FAIXAS_A, [("até 0,300", "R$ 10 mil"), ("0,301 a 0,400", "R$ 15 mil"), ("acima de 0,400", "R$ 20 mil")])

    def test_formas_nativas_sem_imagem(self) -> None:
        for k, xml in self.xmls.items():
            self.assertNotIn("<p:pic>", xml, k)
            self.assertNotIn("r:embed", xml, k)
            self.assertGreater(xml.count("<p:cxnSp>"), 5, k)
            self.assertGreater(xml.count("<p:sp>"), 15, k)

    def test_ids_unicos_e_sem_sobreposicao_de_id(self) -> None:
        for k, xml in self.xmls.items():
            ids = re.findall(r'<p:cNvPr id="(\d+)"', xml)
            self.assertEqual(len(ids), len(set(ids)), k)

    def test_elementos_obrigatorios_do_pedido(self) -> None:
        a = " ".join(texto_das_formas(self.xmls["A"]))
        for trecho in ["IVS 2010 oficial", "Faixa da bolsa", "E(w | B)", "MOEHLING et al. (2020)", "REDDING & ROSSI-HANSBERG (2017)",
                       "CHONÉ & MA (2011)", "BURDETT, SHI & WRIGHT (2001)", "π", "Vaga preenchida", "Capacidade", "Produção e acesso",
                       "Saúde", "Custo de viver ali", "Custo de trabalhar ali", "moradia".capitalize(), "Equipe"]:
            self.assertIn(trecho, a)
        b = " ".join(texto_das_formas(self.xmls["B"]))
        for trecho in ["Abertura de vagas", "SGTES", "Outras políticas nos mesmos cortes", "Substituição", "já estava no município",
                       "A BOLSA AGE AQUI", "pacote"]:
            self.assertIn(trecho, b)


class TestDoc01(unittest.TestCase):
    def test_bloco_gerado_atualizado(self) -> None:
        txt = DOC01.read_text(encoding="utf-8")
        i, j = txt.index(G.MARCA_INI), txt.index(G.MARCA_FIM) + len(G.MARCA_FIM)
        self.assertEqual(txt[i:j], G.bloco_doc(), "bloco desatualizado: rode --atualizar-doc")

    def test_todo_texto_exibido_esta_no_doc(self) -> None:
        doc = DOC01.read_text(encoding="utf-8").replace("\\|", "|")
        for xml in (G.montar_slide_a(), G.montar_slide_b()):
            for t in texto_das_formas(xml):
                self.assertIn(t, doc, f"texto do slide ausente do doc 01: {t!r}")

    def test_secoes_pedidas(self) -> None:
        txt = DOC01.read_text(encoding="utf-8")
        for t in ["## 3. Literatura de cada elo", "## 4. Onde cada equação do apêndice", "## 6. Nova ordem dos slides de teoria"]:
            self.assertIn(t, txt)
        for titulo in G.TITULOS_ESPERADOS.values():
            self.assertIn(titulo, txt)

    def test_links_locais_existem(self) -> None:
        for p in (DOC01, README):
            for alvo in re.findall(r"\]\(([^)#]+)(?:#[^)]*)?\)", p.read_text(encoding="utf-8")):
                if alvo.startswith(("http", "mailto")):
                    continue
                self.assertTrue((p.parent / alvo).resolve().exists(), f"{p.name}: {alvo}")


@unittest.skipUnless(TEM_SAIDAS, "saídas do diagrama ausentes")
class TestPptx(unittest.TestCase):
    @staticmethod
    def _slides_em_ordem(caminho: Path) -> list[tuple[str, str]]:
        with zipfile.ZipFile(caminho) as z:
            pres = z.read("ppt/presentation.xml").decode()
            rels = z.read("ppt/_rels/presentation.xml.rels").decode()
            alvo = {m.group(1): m.group(2) for m in re.finditer(r'<Relationship Id="(rId\d+)"[^>]*Target="([^"]*)"', rels)}
            saida = []
            for rid in re.findall(r'<p:sldId id="\d+" r:id="(rId\d+)"/>', pres):
                xml = z.read("ppt/" + alvo[rid]).decode()
                saida.append((G.titulo_do_slide(xml), xml))
            return saida

    def test_arquivo_dos_slides_novos(self) -> None:
        s = self._slides_em_ordem(SLIDES)
        self.assertEqual([t for t, _ in s], [G.TITULO_A, G.TITULO_B])
        self.assertEqual(texto_das_formas(s[0][1]), texto_das_formas(G.montar_slide_a()))
        self.assertEqual(texto_das_formas(s[1][1]), texto_das_formas(G.montar_slide_b()))
        with zipfile.ZipFile(SLIDES) as z:
            self.assertIsNone(z.testzip())
            self.assertFalse([n for n in z.namelist() if n.startswith("ppt/slides/slide") and n.endswith(".xml")][2:])

    def test_deck_reorganizado(self) -> None:
        s = self._slides_em_ordem(DECK)
        titulos = [t for t, _ in s]
        self.assertEqual(len(s), 38)
        ia, ib = titulos.index(G.TITULO_A), titulos.index(G.TITULO_B)
        self.assertLess(ia, ib)
        self.assertEqual(titulos[ia - 1], "Sumário")  # A fecha a seção Literatura: logo depois do sumário dela
        self.assertEqual(titulos[ia + 1], "Sumário")
        self.assertEqual(titulos[ib - 1], "Sumário")
        div = titulos.index("Apêndice")
        self.assertGreater(div, ib)
        depois = titulos[div + 1: div + 8]
        self.assertEqual(depois, [G.TITULOS_ESPERADOS[p] for p in G.POS_EQUACOES])
        antes = titulos[:div]
        for p in G.POS_EQUACOES:
            self.assertEqual(antes.count(G.TITULOS_ESPERADOS[p]) if G.TITULOS_ESPERADOS[p] != "Da escolha individual ao preenchimento agregado" else 0, 0)
        self.assertEqual(titulos.count("Da escolha individual ao preenchimento agregado"), 2)  # as duas versões, sem perda

    def test_slides_de_equacao_nao_foram_editados(self) -> None:
        """Os 7 slides movidos mantêm o texto: nenhuma perda; só 19 e 20 deixaram de estar ocultos."""
        with zipfile.ZipFile(DECK) as z:
            ocultos = [n for n in z.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", n) and ' show="0"' in z.read(n).decode()[:600]]
        self.assertNotIn("ppt/slides/slide19.xml", ocultos)
        self.assertNotIn("ppt/slides/slide20.xml", ocultos)
        self.assertIn("ppt/slides/slide21.xml", ocultos)


@unittest.skipUnless(TEM_SAIDAS, "saídas do diagrama ausentes")
class TestManifesto(unittest.TestCase):
    def setUp(self) -> None:
        self.m = json.loads(MANIFESTO.read_text(encoding="utf-8"))

    def test_hashes_atuais(self) -> None:
        for s in self.m["saidas"]:
            p = ROOT / s["caminho"]
            self.assertEqual(sha256(p), s["sha256"], s["caminho"])
            self.assertEqual(p.stat().st_size, s["bytes"])

    def test_registra_entrada_sem_alterar_o_original(self) -> None:
        e = self.m["entradas"][0]
        self.assertRegex(e["sha256"], r"^[0-9a-f]{64}$")
        self.assertIn("fora do repositório", e["caminho"])
        self.assertNotIn("natureza_dos_dados", self.m)  # não é saída de dados: o teste de integridade não se aplica

    def test_ordem_registrada(self) -> None:
        self.assertEqual(len(self.m["ordem_do_deck_proposto"]), 38)
        self.assertEqual(sum(1 for o in self.m["ordem_do_deck_proposto"] if o["origem"] == "novo"), 2)

    def test_tamanho_do_deck_dentro_do_limite_do_repositorio(self) -> None:
        self.assertLess(DECK.stat().st_size, 15 * 1024 * 1024)

    @unittest.skipUnless(os.environ.get("PMME_DECK_GRUPO"), "deck do grupo não informado (PMME_DECK_GRUPO)")
    def test_determinismo(self) -> None:
        deck = Path(os.environ["PMME_DECK_GRUPO"])
        self.assertEqual(sha256(deck), self.m["entradas"][0]["sha256"])
        with tempfile.TemporaryDirectory() as tmp:
            G.construir(deck, Path(tmp))
            for s in self.m["saidas"]:
                self.assertEqual(sha256(Path(tmp) / Path(s["caminho"]).name), s["sha256"], s["caminho"])


if __name__ == "__main__":
    unittest.main()
