"""Testes do deck da banca 2 revisto depois da banca de 04/11/2026 (doc 12 da banca 2).

O deck `output/apresentacao_banca2/deck_banca2_pos_banca.pptx` é derivado do deck que o grupo apresentou, por
`scripts/apresentacao/gerar_deck_banca2_pos_banca.py`. Confere:

1. o pacote: deck, PDF e manifesto existem; os hashes do manifesto batem com os arquivos e com as entradas atuais;
2. os títulos do deck estão no conteúdo canônico (doc 12, §2): divergência entre deck e doc é erro do deck;
3. nada proibido na tela: resultado da origem (×11, D_UF), "incentivo limitado", números do modelo base nos ciclos 1
   e 3 (+7%, 0%), o nome "origem", typos do deck apresentado;
4. a regra dos números: todo número na tela é valor de um código do registro usado pelo gerador, um coeficiente do
   VL-1, uma conta de leitura refeita, um parâmetro do edital ou um valor ilustrativo rotulado como tal;
5. as contas de leitura do slide de resultados: 5β, e^5β e os km batem com `VL_estimativas.csv`;
6. a navbar: as nove seções, na ordem, com a seção certa em destaque em cada slide do corpo e nenhuma no apêndice;
7. o roteiro: um por slide do corpo e soma de 6:30 a 7:30 (doc 06, §4).
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import unittest
from pathlib import Path

import pandas as pd
from pptx import Presentation

ROOT = Path(__file__).resolve().parents[1]
SAIDA = ROOT / "output" / "apresentacao_banca2"
DECK, PDF = SAIDA / "deck_banca2_pos_banca.pptx", SAIDA / "deck_banca2_pos_banca.pdf"
MANIF = SAIDA / "manifesto_deck_banca2_pos_banca.json"
DOC12 = ROOT / "docs" / "07_apresentacoes" / "banca2" / "12_revisao_pos_banca_0411.md"
NUMEROS = SAIDA / "numeros_banca2.json"
VL_EST = ROOT / "output" / "rdd_bolsa" / "VL_estimativas.csv"

SECOES = ["Motivação", "Hipótese", "Dados", "Análise Descritiva", "Metodologia", "Identificação", "Resultados",
          "Robustez", "Discussão"]
SECAO_POR_SLIDE = {2: "Motivação", 3: "Hipótese", 4: "Dados", 5: "Análise Descritiva", 6: "Metodologia",
                   7: "Metodologia", 8: "Identificação", 9: "Resultados", 10: "Robustez", 11: "Discussão",
                   12: "Discussão"}
PROIBIDOS = ["×11", "11,0", "D_UF", "incentivo limitado", "+7%", "(0%)", "origem", "Origem", "escolgas",
             "inconclusive", "medicos", "Click to edit", "Literatura", "mesmo estado", "regras do programa",
             "VL-1", "adendo 52e"]
# Parâmetros do edital e da apresentação (não são resultado) e valores ilustrativos rotulados como tais na tela.
PARAMETROS = {"0,300", "0,400", "0,05", "10", "15", "20", "5", "1", "2", "3", "100", "1974", "2010", "2026", "2025",
              "2024", "2003", "2022", "2027", "29068", "1.480", "320", "2,5", "72", "86", "40", "70", "28", "6",
              "27/08/2026", "10/09/2025", "04/11/2026", "13", "0", "4", "52g", "52h", "52c", "57x", "57a", "44",
              "48", "16", "18", "50", "07", "11", "20", "4.1", "3.1", "95"}  # 95: "IC 95%"
ILUSTRATIVOS = {"120", "340", "510", "980", "1.100"}  # slide 4, "linhas ilustrativas, não dados reais"


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _texto_tela(slide) -> str:
    partes = []

    def walk(shapes):
        for sh in shapes:
            if sh.shape_type == 6:
                walk(sh.shapes)
            elif sh.has_text_frame:
                partes.append(sh.text_frame.text)
            elif getattr(sh, "has_table", False) and sh.has_table:
                for row in sh.table.rows:
                    for c in row.cells:
                        partes.append(c.text)
    walk(slide.shapes)
    return "\n".join(partes)


def _sem_rodape(txt: str) -> str:
    return "\n".join(l for l in txt.split("\n") if not l.startswith("Fontes:") and not l.startswith("Motivação"))


class DeckPosBanca(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not DECK.exists():
            raise unittest.SkipTest("deck pós-banca não gerado")
        cls.prs = Presentation(str(DECK))
        cls.slides = list(cls.prs.slides)
        cls.man = json.loads(MANIF.read_text(encoding="utf-8"))
        cls.reg = json.loads(NUMEROS.read_text(encoding="utf-8"))["numeros"]
        cls.vl1 = pd.read_csv(VL_EST).query("chave_modelo == 'VL1_emp'")

    def test_pacote_e_hashes(self):
        self.assertTrue(PDF.exists())
        self.assertEqual(self.man["deck"]["sha256"], _sha(DECK))
        for ent in self.man["entradas"]:
            self.assertEqual(ent["sha256"], _sha(ROOT / ent["caminho"]), ent["caminho"])

    def test_titulos_no_doc12(self):
        doc = DOC12.read_text(encoding="utf-8")
        for s in self.man["slides"]:
            if s["titulo"]:
                self.assertIn(s["titulo"], doc, f"título do slide {s['n']} fora do doc 12")

    def test_nada_proibido_na_tela(self):
        for k, sl in enumerate(self.slides, 1):
            tela = _sem_rodape(_texto_tela(sl))
            for p in PROIBIDOS:
                self.assertNotIn(p, tela, f"slide {k}: '{p}' na tela")

    def test_regra_dos_numeros(self):
        permitidos = set(PARAMETROS) | ILUSTRATIVOS
        for cod in self.man["codigos_usados"]:
            permitidos.add(self.reg[cod]["valor"])
        for _, r in self.vl1[self.vl1["tipo_linha"] == "coeficiente"].iterrows():
            for v in (r["estimativa"], r["ic95_inf"], r["ic95_sup"]):
                permitidos.add(f"{abs(v):.3f}".replace(".", ","))
        c = self.man["contas_de_leitura"]
        permitidos |= {f"{c['cinco_beta']:.3f}".replace(".", ","), f"{abs(c['dist']):.3f}".replace(".", ","),
                       f"{c['n_cand']:,}".replace(",", "."), f"{c['n_lin']:,}".replace(",", "."), str(c["n_ef"]),
                       str(c["n_conj"]), str(c["pares_var"]), f"{c['cand_var']:,}".replace(",", "."),
                       str(round(c["n_lin"] / c["n_cand"]))}
        for k, sl in enumerate(self.slides, 1):
            tela = _sem_rodape(_texto_tela(sl))
            toks = []
            for tok in re.findall(r"\d[\d.,/]*\d|\d", tela):
                tok = tok.rstrip(".,")
                toks += [tok] if re.fullmatch(r"\d{2}/\d{2}/\d{4}", tok) else tok.split("/")
            for tok in toks:
                self.assertIn(tok, permitidos | {str(k)}, f"slide {k}: número '{tok}' sem origem registrada")

    def test_contas_de_leitura(self):
        b = float(self.vl1.query("tipo_linha == 'coeficiente' and termo == 'bolsa_mil'")["estimativa"].iloc[0])
        d = float(self.vl1.query("tipo_linha == 'coeficiente' and termo == 'distancia_100km'")["estimativa"].iloc[0])
        rc = float(self.vl1.query("tipo_linha == 'razao_chances_por_5mil'")["estimativa"].iloc[0])
        k5 = float(self.vl1.query("tipo_linha == 'km_equivalentes' and termo == 'K5'")["estimativa"].iloc[0])
        self.assertAlmostEqual(math.exp(5 * b), rc, places=6)
        self.assertAlmostEqual(5 * b / -d * 100, k5, places=3)
        tela = _texto_tela(self.slides[8])
        self.assertIn(f"{5 * b:.3f}".replace(".", ","), tela)
        self.assertIn(f"{-d:.3f}".replace(".", ","), tela)
        self.assertIn(self.reg["VL1_EMP_RC"]["valor"], tela)
        self.assertIn(f"{k5:.0f} km", tela)

    def test_navbar(self):
        for k, sl in enumerate(self.slides, 1):
            nav = [sh for sh in sl.shapes if sh.has_text_frame and sh.text_frame.text.startswith("Motivação")]
            if k in (1, 13):
                continue
            self.assertEqual(len(nav), 1, f"slide {k}: navbar")
            texto = nav[0].text_frame.text
            self.assertEqual([s.strip() for s in texto.split("|")], SECOES, f"slide {k}: seções da navbar")
            negrito = [r.text.strip() for r in nav[0].text_frame.paragraphs[0].runs if r.font.bold and r.text.strip()]
            esperado = [SECAO_POR_SLIDE[k]] if k in SECAO_POR_SLIDE else []
            self.assertEqual(negrito, esperado, f"slide {k}: seção em destaque")

    def test_roteiro(self):
        rot = self.man["roteiro_segundos"]
        self.assertTrue(390 <= rot["total"] <= 450, rot)
        for k in SECAO_POR_SLIDE:
            notas = self.slides[k - 1].notes_slide.notes_text_frame.text
            self.assertTrue(notas.startswith("Roteiro ("), f"slide {k} sem roteiro")


if __name__ == "__main__":
    unittest.main()
