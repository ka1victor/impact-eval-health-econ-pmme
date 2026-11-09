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

# Texto da banca 1 que não pode voltar (erratas E8 e E10, hipótese antiga, slides de exemplo e P12)
PROIBIDAS = ("piso", "renumeração", "trasnporte", "buito", "PMEE", "EXEMPLO", "indícios de efetividade",
             "Viabilidade Empírica", "BOLSA → PREENCHIMENTO", "maior probabilidade de preenchimento de vagas",
             "Municípios com maior remuneração", "REGIC")


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def norm(t: str) -> str:
    return " ".join(t.split())


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

    def test_sem_texto_proibido(self):
        tudo = " ".join(" ".join(t) for t in self.textos)
        for f in PROIBIDAS:
            self.assertNotIn(f, tudo, f)

    def test_textos_novos_na_tela_e_no_doc(self):
        doc = norm(DOC.read_text(encoding="utf-8"))
        tudo = " ".join(" ".join(t) for t in self.textos)
        novos = [G.PERGUNTA, G.HIPOTESE, G.ROTULO_HIPOTESE, G.TITULO_IVS, G.SUB_IVS, G.SUB2_IVS, G.NOTA_IVS,
                 G.FONTES_IVS, G.SUB_VAGAS, G.SUB2_VAGAS, G.SUB2_UF, G.FONTES_ESCASSEZ, G.CTEXT_UTILIDADE,
                 G.ROTULO_CADEIA, *G.FAIXAS_IVS.values()]
        for t in novos:
            self.assertIn(norm(t), tudo, t)
            self.assertIn(norm(t).replace("|", "\\|"), doc, f"não está no doc 02: {t}")

    def test_slides_da_banca2_sem_mudanca_de_texto(self):
        from pptx import Presentation
        b2 = Presentation(str(G.ENT_B2))
        for pos, (o, n, _) in enumerate(G.ORDEM):
            if o != "B2":
                continue
            antes = [norm(sh.text_frame.text) for sh in G.formas(b2.slides[n - 1].shapes)
                     if sh.has_text_frame and not sh.text_frame.text.startswith("Hipótese  |")]
            depois = [t for t in self.textos[pos] if not t.startswith("Motivação |")]
            self.assertEqual(antes, depois, f"banca 2, slide {n}")
            self.assertEqual(norm(b2.slides[n - 1].notes_slide.notes_text_frame.text),
                             norm(self.prs.slides[pos].notes_slide.notes_text_frame.text))

    def test_rodape_marca_a_secao(self):
        for pos, (o, n, secao) in enumerate(G.ORDEM):
            rod = [sh for sh in G.formas(self.prs.slides[pos].shapes)
                   if sh.has_text_frame and sh.text_frame.text.startswith("Motivação") and "|" in sh.text_frame.text]
            if not rod:
                continue
            self.assertEqual(norm(rod[0].text_frame.text), norm("  |  ".join(G.SECOES)))
            negrito = [r.text for r in rod[0].text_frame.paragraphs[0].runs if r.font.bold]
            self.assertEqual(negrito, [secao] if secao else [], f"slide {pos + 1}")

    def test_ordem_e_fora_cobrem_o_deck_do_grupo(self):
        usados = [n for o, n, _ in G.ORDEM if o == "G"]
        self.assertEqual(len(usados), len(set(usados)))
        self.assertEqual(set(usados) | set(G.FORA), set(range(1, 39)))
        self.assertEqual(sorted(n for o, n, _ in G.ORDEM if o == "B2"), list(range(1, 12)))


if __name__ == "__main__":
    unittest.main()
