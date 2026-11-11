"""Testes do deck da banca final sobre a versão do grupo de 11/11/2026 (doc 03 da banca final)."""
from __future__ import annotations

import hashlib
import json
import math
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/apresentacao_banca_final"
DECK = OUT / "deck_banca_final_grupo.pptx"
MANIF = OUT / "manifesto_deck_banca_final_grupo.json"
EXEMPLO = OUT / "exemplo_logit_real.json"
DOC = ROOT / "docs/07_apresentacoes/banca_final/03_deck_banca_final_grupo.md"

# Não pode aparecer na tela: erros de digitação e faixas do FAQ do grupo, a equação antiga da utilidade, anotações
PROIBIDAS = ("buito", "renumeração", "11.1.4", "Vulnerabilidade: Alta", "Vulnerabilidade: Muito alta", "+ ε",
             "U_iv", "piso da bolsa", "preenchimento das vagas", "Esse tá ruim", "Estética ruim", "Evidenciarqal", "Escolha das palavras", "Cautela")


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def textos(slide) -> str:
    out = []

    def walk(shs):
        for sh in shs:
            if sh.shape_type == 6:
                walk(sh.shapes)
            elif sh.has_text_frame:
                out.append(sh.text_frame.text)
            elif getattr(sh, "has_table", False) and sh.has_table:
                out.extend(c.text for r in sh.table.rows for c in r.cells)
    walk(slide.shapes)
    return " ".join(" ".join(out).split())


@unittest.skipUnless(DECK.exists(), "deck não gerado")
class TestDeck(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from pptx import Presentation
        cls.prs = Presentation(str(DECK))
        cls.txt = [textos(s) for s in cls.prs.slides]
        cls.man = json.loads(MANIF.read_text(encoding="utf-8"))

    def test_tamanho_e_ocultos(self):
        self.assertEqual(len(self.prs.slides), 32)
        self.assertFalse(any(s._element.get("show") == "0" for s in self.prs.slides))

    def test_manifesto_bate(self):
        self.assertEqual(self.man["saidas"][str(DECK.relative_to(ROOT))], sha256(DECK))
        for arq, h in self.man["entradas"].items():
            self.assertEqual(sha256(ROOT / arq), h, arq)

    def test_proibidas(self):
        for i, t in enumerate(self.txt, 1):
            for p in PROIBIDAS:
                self.assertNotIn(p, t, f"slide {i}: {p!r}")

    def test_numeros_lidos_de_output(self):
        d = pd.read_csv(ROOT / "output/rdd_bolsa/VL_estimativas.csv")
        b = float(d[(d.chave_modelo == "VL1_emp") & (d.tipo_linha == "coeficiente") & (d.termo == "bolsa_mil")]
                  .estimativa.iloc[0])
        g = float(d[(d.chave_modelo == "VL1_emp") & (d.tipo_linha == "coeficiente") & (d.termo == "distancia_100km")]
                  .estimativa.iloc[0])
        rc = f"{math.exp(5 * b):.2f}".replace(".", ",")
        km = f"{round(5 * b / -g * 100)} km"
        tudo = " ".join(self.txt)
        self.assertIn(f"×{rc}", tudo)
        self.assertIn(km, tudo)

    def test_slides_novos_e_titulos(self):
        tits = [s["titulo"] for s in self.man["slides"]]
        for t in ("Cadeia causal: da bolsa aos desfechos na saúde", "Maior remuneração, maior chance de ser escolhida",
                  "Modelo: logit condicional da 1ª opção", "3 em 4 escolhem uma vaga a até 189 km", "Limitações"):
            self.assertIn(t, tits)
        self.assertEqual(tits.count("Cadeia causal: da bolsa aos desfechos na saúde"), 2)

    def test_logit_condicional_na_tela(self):
        t = self.txt[20]
        self.assertIn("P(i escolhe v) =", t)
        self.assertIn("exp(V", t)
        self.assertIn("cardápio de i", t)

    def test_pergunta_nova(self):
        self.assertIn("Uma bolsa maior aumenta a chance de uma vaga ser a 1ª opção do médico?", self.txt[8])

    def test_doc_cita_o_deck(self):
        doc = DOC.read_text(encoding="utf-8")
        self.assertIn("deck_banca_final_grupo.pptx", doc)
        self.assertIn("32 slides", doc)


@unittest.skipUnless(EXEMPLO.exists(), "exemplo não gerado")
class TestExemplo(unittest.TestCase):
    def test_sem_identificador_e_conta_fecha(self):
        ex = json.loads(EXEMPLO.read_text(encoding="utf-8"))
        bruto = json.dumps(ex, ensure_ascii=False)
        self.assertNotIn("id_candidato", bruto)
        self.assertNotIn("co_ibge_origem", bruto)
        c = ex["conta"]
        self.assertAlmostEqual(math.prod(c["razao_por_termo"].values()), c["razao_total"], places=10)
        self.assertAlmostEqual(ex["vaga_b"]["chance_modelo"] / ex["vaga_a"]["chance_modelo"], c["razao_total"],
                               places=8)
        self.assertEqual(ex["vaga_b"]["bolsa_mil"] - ex["vaga_a"]["bolsa_mil"], 5.0)


if __name__ == "__main__":
    unittest.main()
