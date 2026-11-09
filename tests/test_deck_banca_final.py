"""Testes do deck da banca final (scripts/apresentacao/gerar_deck_banca_final.py; doc 02 da banca final)."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAIDA = ROOT / "output/apresentacao_banca_final"
DECK = SAIDA / "deck_banca_final.pptx"
MANIF = SAIDA / "manifesto_deck_banca_final.json"
DOC = ROOT / "docs/07_apresentacoes/banca_final/02_deck_banca_final.md"

_spec = importlib.util.spec_from_file_location("gerar_deck_banca_final",
                                               ROOT / "scripts/apresentacao/gerar_deck_banca_final.py")
G = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(G)

# Na tela, não pode voltar: erratas E8 e E10 da banca 1, hipótese antiga, slides de exemplo, P12, título antigo,
# "origem" (doc 12 da banca 2, §1.2) e referência à numeração da banca 1
PROIBIDAS = ("piso", "renumeração", "trasnporte", "buito", "PMEE", "EXEMPLO", "indícios de efetividade",
             "Viabilidade Empírica", "BOLSA → PREENCHIMENTO", "maior probabilidade de preenchimento de vagas",
             "Municípios com maior remuneração", "REGIC", "incentivo limitado", "origem", "slide 11", "Sumário")


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def norm(t: str) -> str:
    return " ".join(t.split())


def eh_rodape(t: str) -> bool:
    return "|" in t and t.startswith(("Motivação", "Hipótese"))


@unittest.skipUnless(DECK.exists() and MANIF.exists(), "deck da banca final ausente")
class TestDeckBancaFinal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from pptx import Presentation
        cls.prs = Presentation(str(DECK))
        cls.man = json.loads(MANIF.read_text(encoding="utf-8"))
        cls.textos = [[norm(sh.text_frame.text) for sh in G.formas(s.shapes) if sh.has_text_frame]
                      for s in cls.prs.slides]

    def test_ordem_e_tamanho(self):
        self.assertEqual(len(self.prs.slides), len(G.ORDEM))
        self.assertEqual(len(self.man["ordem"]), len(G.ORDEM))
        self.assertTrue(all(s._element.get("show") != "0" for s in self.prs.slides), "nenhum slide oculto")

    def test_manifesto_confere_hashes(self):
        for e in self.man["entradas"] + self.man["saidas"]:
            if e["caminho"].endswith(".pdf"):
                continue  # o PDF do LibreOffice não é determinístico
            self.assertEqual(sha256(ROOT / e["caminho"]), e["sha256"], e["caminho"])

    def test_sem_texto_proibido_na_tela(self):
        for pos, ts in enumerate(self.textos, start=1):
            tudo = " ".join(ts)
            for f in PROIBIDAS:
                self.assertNotIn(f, tudo, f"slide {pos}: {f}")

    def test_textos_novos_na_tela_e_no_doc(self):
        doc = norm(DOC.read_text(encoding="utf-8"))
        tudo = " ".join(" ".join(t) for t in self.textos)
        novos = [*G.TITULO_CAPA, G.SUB2_UF, G.SUB_VAGAS, G.SUB2_VAGAS, G.FONTES_ESCASSEZ, G.A4_DIAGRAMA,
                 G.CTEXT_UTILIDADE, G.ROTULO_CADEIA, G.ADICOES]
        for t in novos:
            self.assertIn(norm(t), tudo, t)
            self.assertIn(norm(t).replace("|", "\\|"), doc, f"não está no doc 02: {t}")

    def test_slides_do_pos_banca_sem_mudanca_de_texto(self):
        from pptx import Presentation
        pb = Presentation(str(G.ENT_PB))
        for pos, (o, n, _) in enumerate(G.ORDEM):
            if o != "PB":
                continue
            def filtrar(ts):
                return [t for t in ts if not eh_rodape(t) and not t.isdigit()]
            antes = filtrar([norm(sh.text_frame.text) for sh in G.formas(pb.slides[n - 1].shapes)
                             if sh.has_text_frame])
            self.assertEqual(antes, filtrar(self.textos[pos]), f"pós-banca, slide {n}")
            if pb.slides[n - 1].has_notes_slide:
                self.assertEqual(norm(pb.slides[n - 1].notes_slide.notes_text_frame.text),
                                 norm(self.prs.slides[pos].notes_slide.notes_text_frame.text))

    def test_rodape_igual_em_todos_e_marca_a_secao(self):
        for pos, (o, n, secao) in enumerate(G.ORDEM):
            rod = [sh for sh in G.formas(self.prs.slides[pos].shapes)
                   if sh.has_text_frame and eh_rodape(sh.text_frame.text)]
            if o == "G" and n in (1, 25, 26):
                continue  # capa, Q&A e divisor não têm rodapé
            self.assertEqual(len(rod), 1, f"slide {pos + 1}")
            self.assertEqual(norm(rod[0].text_frame.text), norm("  |  ".join(G.SECOES)))
            negrito = [r.text for r in rod[0].text_frame.paragraphs[0].runs if r.font.bold]
            self.assertEqual(negrito, [secao] if secao else [], f"slide {pos + 1}")

    def test_numero_da_pagina(self):
        for pos, s in enumerate(self.prs.slides, start=1):
            for sh in G.formas(s.shapes):
                t = sh.text_frame.text.strip() if sh.has_text_frame else ""
                if t.isdigit() and sh.left is not None and sh.left > 12 * 914400 and sh.top > 6.8 * 914400:
                    self.assertEqual(int(t), pos, f"slide {pos}")

    def test_ordem_e_fora_cobrem_as_entradas(self):
        g = [n for o, n, _ in G.ORDEM if o == "G"]
        pb = [n for o, n, _ in G.ORDEM if o == "PB"]
        self.assertEqual(len(g), len(set(g)))
        self.assertEqual(len(pb), len(set(pb)))
        self.assertEqual(set(g) | set(G.FORA_G), set(range(1, 39)))
        self.assertEqual(set(pb) | set(G.FORA_PB), set(range(1, 15)))


if __name__ == "__main__":
    unittest.main()
