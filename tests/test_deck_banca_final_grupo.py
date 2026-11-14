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
PROIBIDAS = ("buito", "renumeração", "11.1.4", "Vulnerabilidade: Alta", "Vulnerabilidade: Muito alta",
             "piso da bolsa", "preenchimento das vagas", "altruísmo", "vaga é preenchida", "Hips de", "medicos",
             "Esse tá ruim", "Estética ruim", "Evidenciarqal", "Escolha das palavras", "Cautela", "cardápio",
             # nada de arquivo interno na tela (pedido do autor de 14/11): fontes só públicas
             ".json", ".csv", ".py", "output/", "scripts/", "adendo 5", "auditoria",
             # rodada 7 (14/11): sem o plano original na tela, sem "A seguir", "forte" e não "firme"
             "Plano original", "PLANO ORIGINAL", "pré-registrado", "A seguir", "firme", "Só as duas")


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

    def pos(self, inicio: str) -> int:
        """Posição (base 0) do slide cujo título começa com `inicio` (a ordem muda entre rodadas)."""
        tits = [x["titulo"] for x in self.man["slides"]]
        achados = [i for i, t in enumerate(tits) if t.startswith(inicio)]
        self.assertEqual(len(achados), 1, inicio)
        return achados[0]

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
                  "Modelo: logit condicional da 1ª opção", "Candidatos escolhem perto de onde trabalham",
                  "Limitações"):
            self.assertIn(t, tits)
        self.assertEqual(tits.count("Cadeia causal: da bolsa aos desfechos na saúde"), 2)

    def test_logit_condicional_na_tela(self):
        t = self.txt[self.pos("Modelo: logit condicional")]
        self.assertIn("P(i escolhe v) =", t)
        self.assertIn("exp(β·x", t)
        self.assertIn("todas as vagas k de i", t)

    def test_estimacao_explica_como_foi_feito(self):
        """Slide 23 (14/11): variação que identifica o β, o que fica fixo e a inferência, com números de output/."""
        d = pd.read_csv(ROOT / "output/rdd_bolsa/VL_estimativas.csv")
        c = d[(d.chave_modelo == "VL1_emp") & (d.tipo_linha == "coeficiente") & (d.termo == "bolsa_mil")].iloc[0]
        r = d[(d.chave_modelo == "VL1_emp") & (d.tipo_linha == "razao_chances_por_5mil")].iloc[0]
        i = self.pos("Anexo 4: estimação")
        t = self.txt[i]
        notas = self.prs.slides[i].notes_slide.notes_text_frame.text
        self.assertIn("Anexo 4: estimação, de onde vem o β", t)
        # a incerteza saiu da tela (pedido de 14/11) e fica nas notas, para as perguntas
        self.assertIn(f"({int(c.n_conjuntos)} grupos", notas)
        self.assertIn(f"p = {r.p_score_rademacher:.3f}".replace(".", ","), notas)
        self.assertIn(f"p = {r.p_holm:.3f}".replace(".", ","), notas)
        for termo in ("Vagas do mesmo candidato", "Vagas da mesma UF", "Não dentro do município"):
            self.assertIn(termo, t)
        # a ressalva "exploratório" fica em Limitações, não no corpo do método (pedido do autor de 14/11)
        self.assertNotIn("exploratório", t)

    def test_aninhado_no_modelo_base(self):
        i = self.pos("Identificação:")
        self.assertIn("testado no modelo base", self.txt[i])
        self.assertIn("rodado no modelo base sem o par de UFs", self.prs.slides[i].notes_slide.notes_text_frame.text)

    def test_funil_das_alternativas(self):
        self.assertIn("932.577 → 578.998 linhas", self.prs.slides[self.pos("Cada candidato vira")].notes_slide.notes_text_frame.text)

    def test_equacao_com_erro_e_chance_sobre_parte_observada(self):
        """Rodada 7 (14/11): U com o erro no fim; a chance usa só a parte observada (β·x), nunca U inteiro."""
        t = self.txt[self.pos("Modelo: logit condicional")]
        self.assertIn("ε", t)
        self.assertIn("exp(β·x", t)
        self.assertNotIn("exp(U", t)
        for x in ("Viv", "Vik", "U = V"):
            self.assertNotIn(x, t)
        self.assertIn("254 efeitos fixos", t)

    def test_descritiva_em_numeros_sem_modelo(self):
        t = self.txt[self.pos("Candidatos escolhem perto")]
        # rodada 7 (14/11): os cartões repetidos saíram; no lugar, como a análise foi montada
        for x in ("COMO MONTAMOS ESTA ANÁLISE", "5.425 candidatos", "I. A que distância fica a 1ª opção",
                  "II. Onde fica a 1ª opção"):
            self.assertIn(x, t)
        self.assertNotIn("modelo", t)

    def test_exploratorio_so_em_limitacoes(self):
        """Pedido do autor de 14/11: a ressalva sai do corpo do método e vai para Limitações."""
        tits = [x["titulo"] for x in self.man["slides"]]
        lim = tits.index("Limitações")
        self.assertIn("exploratório", self.txt[lim])
        self.assertIn("confirmar exige dados novos", self.txt[lim])
        notas = self.prs.slides[lim].notes_slide.notes_text_frame.text
        self.assertIn("não quer dizer 'não causal'", notas)
        for i, t in enumerate(self.txt[:lim]):
            self.assertNotIn("exploratório", t, f"slide {i + 1}")

    @unittest.skip("ideias do colega desligadas (COM_IDEIAS_COLEGA = False)")
    def test_intuicao_e_anexos_do_logit(self):
        """Ideias do deck v4.1 de um colega (14/11): vagas A, B e C antes do modelo; anexos com y e U e com as
        alternativas. As chances saem dos pesos do VL-1."""
        d = pd.read_csv(ROOT / "output/rdd_bolsa/VL_estimativas.csv")
        c = d[(d.chave_modelo == "VL1_emp") & (d.tipo_linha == "coeficiente")].set_index("termo")
        b, g = float(c.loc["bolsa_mil", "estimativa"]), float(c.loc["distancia_100km", "estimativa"])
        km_c = 50 + round(5 * b / -g * 100)
        ev = [1.0, math.exp(5 * b), math.exp(5 * b + g * (km_c - 50) / 100)]
        pb = ev[1] / sum(ev)
        tits = [x["titulo"] for x in self.man["slides"]]
        i = tits.index("Cada médico escolhe a vaga que mais vale a pena")
        self.assertEqual(tits[i + 1], "Modelo: logit condicional da 1ª opção")
        self.assertIn(f"{100 * pb:.0f}%", self.txt[i])
        j = tits.index("Anexo 5: o modelo formal, do valor à escolha")
        self.assertIn(f"{100 * pb:.1f}%".replace(".", ","), self.txt[j])
        self.assertIn("y é o resultado.", self.txt[j])
        self.assertIn("U é o mecanismo.", self.txt[j])
        k = tits.index("Anexo 6: por que este modelo e não outro")
        for x in ("RDD por vaga", "Poisson", "Guimarães, Figueiredo e Woodward", "logit condicional"):
            self.assertIn(x, self.txt[k])
        self.assertEqual(tits[-2:], ["Anexo 5: o modelo formal, do valor à escolha",
                                     "Anexo 6: por que este modelo e não outro"])

    def test_literatura_e_estimacao_no_anexo(self):
        """Rodada 10 (14/11): para encurtar a fala, Literatura e Estimação vão para depois do Q&A."""
        qa = self.pos("Q&A") if any(x["titulo"].startswith("Q&A") for x in self.man["slides"]) else None
        lit, est = self.pos("Anexo 1: modelo combina"), self.pos("Anexo 4: estimação")
        self.assertEqual(self.pos("Conclusão:"), lit - 2)  # conclusão, Q&A, anexos
        self.assertLess(lit, est)
        self.assertLess(self.pos("Limitações"), self.pos("Conclusão:"))
        for t in ("Anexo 2: literatura teórica, a equação", "Anexo 3: bolsa segue exatamente o IVS do município"):
            self.assertTrue(any(x["titulo"] == t for x in self.man["slides"]), t)

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
