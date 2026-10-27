"""Testes do deck curto da banca 2 (`docs/07_apresentacoes/banca2/04_conteudo_deck_curto.md`).

O deck curto é o único usado na versão final (decisão do autor de 26/10/2026; doc 06) e é derivado do doc 04 por
`scripts/apresentacao/gerar_deck_banca2.py` (modo padrão). Desde 27/10/2026 (doc 07 da banca 2) o corpo tem uma
hipótese só, a antiga H2 (bolsa × origem), e a antiga H1 (o fato) e a antiga H3 ficam num apêndice curto. Confere:

1. a estrutura obrigatória (doc 06): Hipótese, Dados, Análise descritiva, Metodologia, Identificação, Resultados,
   Robustez, Discussão, nesta ordem; no máximo 14 slides no corpo e 2 no apêndice, depois da Discussão; a sequência;
2. a regra do autor "texto demais": no máximo 30 palavras visíveis por slide, fora o título, a figura e a linha de
   fontes, no doc 04 e no próprio deck;
3. a hipótese única, dita como formulada depois dos dados, sem as outras hipóteses no corpo;
4. o conteúdo de cada seção: dados e fontes, ciclos, regra *sharp* com "Como ler", onde escolhem, o logit em
   palavras, as premissas, o teste central (origem × toda a bolsa, quadro do ciclo 2 de 13/02/2026), o peso da bolsa
   dentro da mesma UF (adendo pós-resultado), a robustez e a Discussão; cada número da leitura relido do registro;
5. o apêndice: o fato (G-A) com a redação das auditorias 49 e 50 e a H3 numa frase;
6. a redação das auditorias 49 e 50: nada de "não detectado" lido como "não muda", nem de números vencidos;
7. a regra dos números: todo número do doc 04 e do deck é o valor de um código listado ou um parâmetro;
8. o pacote gerado: títulos e texto iguais ao doc 04, rodapé com as oito seções, figuras do pipeline, manifesto com
   hashes atuais e, se `PMME_DECK_GRUPO` apontar para o deck do grupo, o determinismo do `.pptx`.
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
MAX_SLIDES = 14   # corpo; decisão do autor de 26/10/2026: "idealmente <15 slides" (doc 06, §2)
MAX_APENDICE = 2  # decisão do autor de 27/10/2026: apêndice "bem rápido", no máximo 2 slides
SEQUENCIA = [  # (seção, título, layout)
    ("Hipótese", "Hipótese: a origem pesa mais que a bolsa na escolha", "curto_hipotese"),
    ("Dados", "Dados: as variáveis e de onde vêm", "curto_tabela"),
    ("Análise descritiva", "Os três ciclos em números", "curto_tabela"),
    ("Análise descritiva", "A bolsa é função exata do IVS: a regra é sharp", "curto_figura"),
    ("Análise descritiva", "Onde escolhem: perto de onde já trabalham", "curto_figura"),
    ("Metodologia", "Metodologia: logit condicional da 1ª opção", "curto_espec"),
    ("Identificação", "Identificação: as premissas e o nosso caso", "curto_tabela"),
    ("Resultados", "Teste central: a origem pesa mais que toda a bolsa", "curto_figura"),
    ("Resultados", "Dentro da mesma UF, a vaga de bolsa maior é preferida", "curto_figura"),
    ("Robustez", "Robustez: a origem pesa mais em todos os ciclos", "curto_figura"),
    ("Discussão", "Discussão: um incentivo limitado", "curto_texto"),
    ("Apêndice", "Apêndice · O fato: sem aumento detectado no corte", "curto_figura"),
    ("Apêndice", "Apêndice · H3: oferta, numa frase", "curto_capa"),
]
FIGURAS = {  # título → figura de output/ (G-A a G-D do doc 07 e a robustez)
    "A bolsa é função exata do IVS: a regra é sharp": "regra_bolsa_ivs_oficial.png",
    "Onde escolhem: perto de onde já trabalham": "exp_escolha_origem.png",
    "Teste central: a origem pesa mais que toda a bolsa": "curto_origem_bolsa.png",
    "Dentro da mesma UF, a vaga de bolsa maior é preferida": "curto_bolsa_mesma_uf.png",
    "Robustez: a origem pesa mais em todos os ciclos": "curto_robustez_escolha.png",
    "Apêndice · O fato: sem aumento detectado no corte": "curto_fato.png",
}
# Redação das auditorias 49 e 50: "não detectado" não é "não muda"; o sinal negativo "anda junto com a UF", não
# "some"; nada de números vencidos (quadro de 19/03 do ciclo 2, km de 112) nem da nota de reestimação já feita
PROIBIDAS = ("não encheu", "não enche", "não aumenta quantas", "era localização", "vinha da localização",
             "não traz médico de longe", "oferta igual", "outros ficam", "por que não sobe", "não sobe", "não muda",
             "vem do ciclo 2", "Reestimação em curso", "mais reserva", "a oferta local muda igual", "1,31", "1,98",
             "112 km",
             # auditoria 53: título causal ("atrai"), interpretação dita como dado, número fora de output/ ("cai à
             # metade" = −0,55, só na auditoria 47), "vagas próximas" (o VL-1 compara vagas da mesma UF), rótulo
             # trocado do quadro do ciclo 2
             "bolsa maior atrai", "o custo que domina é sair", "cai à metade", "vagas próximas",
             "Quadro da inscrição, log",
             # auditoria 52: o VL-1 compara vagas da mesma UF (a de origem ou outra); Holm de família de um teste
             "dentro da sua região", "dentro da região", "só vagas da UF de origem", "Holm 0,072",
             "p de Holm 0,072")
# Guardas antigas que a reescrita de 27/10/2026 tinha deixado de fora (auditoria 36 e 33; auditoria 53)
PROIBIDAS_A36 = ("não podia ser preenchida", "só de reserva", "só de cadastro reserva", "vagas de reserva",
                 "células só de CR", "reserva não")


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def deck_doc04() -> str:
    t = DOC04.read_text(encoding="utf-8")
    return t[t.index("<!-- deck:inicio -->"):t.index("<!-- deck:fim -->")]


def blocos_doc04() -> list[str]:
    return [p for p in re.split(r"(?m)^(?=#{1,2} )", deck_doc04()) if p.startswith("## ")]


def tela(sl: dict) -> str:
    """O que vai à tela: linhas, cautela, selo e células da tabela (sem as notas)."""
    partes = [t for t, _ in D.linhas_curtas(sl)] + ([sl["selo"]] if sl["selo"] else [])
    partes += [c for linha in sl["tabela"] for c in linha]
    return " ".join(D.texto_puro(p).replace("**", "") for p in partes)


def corrido(txt: str) -> str:
    return " ".join(txt.replace(" ", " ").split())


def rotulos(sl: dict) -> list[str]:
    return [re.match(r"\*\*(.+?)\*\*", m).group(1) for m in sl["marcadores"] if m.startswith("**")]


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
        cls.man_fig = json.loads(MANIF_FIG.read_text(encoding="utf-8"))

    def v(self, cod: str) -> str:
        return self.todos[cod]["valor"]

    def b(self, cod: str) -> float:
        return float(self.todos[cod]["valor_bruto"])

    def ic(self, base: str, est: str = "EST", inf: str = "INF", sup: str = "SUP") -> str:
        return f"{self.v(f'{base}_{est}')} [{self.v(f'{base}_{inf}')}; {self.v(f'{base}_{sup}')}]"

    # ---- estrutura e forma -------------------------------------------------------------------------------------

    def test_estrutura_obrigatoria(self) -> None:
        self.assertEqual(D.SECOES_CURTO, SECOES)
        D.conferir_estrutura(self.slides)
        self.assertEqual([(s["secao"], s["titulo"], s["layout"]) for s in self.slides], SEQUENCIA)
        self.assertEqual([s["apendice"] for s in self.slides], [s == "Apêndice" for s, _, _ in SEQUENCIA])
        regra = " ".join(DOC06.read_text(encoding="utf-8").split())
        self.assertIn("30 palavras", regra)  # a regra do autor está registrada no doc 06, §2
        self.assertIn("no máximo 14 slides", regra)
        self.assertIn("apêndice", regra.lower())

    def test_no_maximo_14_slides_e_apendice_curto(self) -> None:
        """Decisões do autor de 26 e 27/10/2026: no máximo 14 slides no corpo e 2 no apêndice, que vem no fim."""
        self.assertEqual((D.MAX_SLIDES_CURTO, D.MAX_APENDICE_CURTO), (MAX_SLIDES, MAX_APENDICE))
        corpo = [s for s in self.slides if not s["apendice"]]
        apend = [s for s in self.slides if s["apendice"]]
        self.assertLessEqual(len(corpo), MAX_SLIDES)
        self.assertLessEqual(len(apend), MAX_APENDICE)
        with self.assertRaises(SystemExit):  # corpo com 15 slides
            D.conferir_estrutura(corpo + [corpo[-1]] * (MAX_SLIDES + 1 - len(corpo)) + apend)
        with self.assertRaises(SystemExit):  # apêndice com 3 slides
            D.conferir_estrutura(corpo + apend + apend[-1:])
        with self.assertRaises(SystemExit):  # apêndice antes da Discussão
            D.conferir_estrutura(apend[:1] + corpo)
        self.assertIn(f"slides: {len(self.slides)}", DOC04.read_text(encoding="utf-8"))

    def test_no_maximo_30_palavras(self) -> None:
        for s in self.slides:
            D.conferir_curto(s)  # para (SystemExit) se fugir do formato
            self.assertLessEqual(D.palavras_visiveis(s), 30, s["titulo"])
            self.assertLessEqual(len(s["titulo"]), D.MAX_TITULO_CURTO, s["titulo"])

    def test_contagem_de_palavras_sintetica(self) -> None:
        self.assertEqual(D.palavras("**H2 · central** a bolsa → mais 1,98 [1,56; 2,40]"), 8)
        self.assertEqual(D.palavras("preenchida = salto + reta"), 3)
        self.assertEqual(D.palavras("salto × lado ÷ reta"), 3)  # "×" e "÷" soltos não são palavra

    def test_figuras_grandes_com_como_ler(self) -> None:
        """Cada slide de figura usa a figura prevista (G-A a G-D do doc 07 e a robustez), lida de output/; as figuras
        novas trazem "Como ler"; a da regra sharp, que vem da galeria, leva o "Como ler" na tela (auditoria 49, A8)."""
        for tit, nome in FIGURAS.items():
            sl = self.por_titulo[tit]
            self.assertEqual(sl["imagem"].name, nome, tit)
            self.assertTrue(sl["imagem"].as_posix().endswith(f"output/apresentacao_banca2/{nome}"), tit)
        novas = self.man_fig["figuras_novas"]
        for nome in ("curto_fato.png", "curto_bolsa_mesma_uf.png", "curto_origem_bolsa.png",
                     "curto_robustez_escolha.png", "exp_escolha_origem.png"):
            self.assertTrue(any(t.startswith("Como ler") for t in novas[nome]["textos"]), nome)
        regra = self.por_titulo["A bolsa é função exata do IVS: a regra é sharp"]
        self.assertTrue(D.texto_puro(regra["marcadores"][0]).startswith("Como ler:"))
        self.assertIn("Como ler", corrido(regra["notas"]))

    # ---- hipótese única ----------------------------------------------------------------------------------------

    def test_hipotese_unica_pos_resultado(self) -> None:
        """O corpo tem uma hipótese só, dita como formulada depois dos dados; a motivação (o fato) é uma linha, sem
        gráfico; as outras hipóteses só aparecem no apêndice."""
        hip = self.por_titulo[SEQUENCIA[0][1]]
        self.assertEqual(rotulos(hip), ["Hipótese", "Motivação"])
        self.assertTrue(D.rotulo_central("Hipótese") and not D.rotulo_central("Motivação"))
        self.assertIsNone(hip["imagem"])
        self.assertIn("após ver os dados", hip["cautela"])
        self.assertIn("pesa menos que a origem", tela(hip))
        self.assertIn("sem aumento detectado", tela(hip))
        notas = corrido(hip["notas"])
        for k in ("pós-resultado", "interpretação, não teste", "pacote do corte", "condicional a se candidatar"):
            self.assertIn(k, notas, k)
        for s in self.slides:
            if s["apendice"]:
                self.assertTrue(s["titulo"].startswith("Apêndice · "), s["titulo"])
                continue
            self.assertIsNone(re.match(r"H\d", s["titulo"]), s["titulo"])
            self.assertIsNone(re.search(r"\bH[13]\b", tela(s)), s["titulo"])
            self.assertNotIn("plano B", s["titulo"])

    # ---- dados e análise descritiva ----------------------------------------------------------------------------

    def test_dados_principais_e_secundarias(self) -> None:
        s = self.por_titulo["Dados: as variáveis e de onde vêm"]
        self.assertEqual(len(s["tabela"][0]), 2)
        self.assertEqual(D.texto_puro(s["tabela"][0][1]), "Fonte")
        sec = [D.texto_puro(r[0]) for r in s["tabela"][1:] if D._linha_italica(r)]
        pri = [D.texto_puro(r[0]) for r in s["tabela"][1:] if not D._linha_italica(r)]
        self.assertEqual(sec, ["Porte, capital"])
        for k in ("1ª opção", "Origem do médico", "IVS 2010", "Distância, UF"):
            self.assertIn(k, pri)
        self.assertTrue(all(r[1].strip() for r in s["tabela"][1:]))  # toda variável tem fonte
        notas = corrido(s["notas"])
        self.assertIn("13/02/2026", notas)
        self.assertIn("vínculo médico no CNES", notas)
        self.assertIn("não é a residência", notas)

    def test_ciclos_em_numeros(self) -> None:
        s = self.por_titulo["Os três ciclos em números"]
        self.assertEqual([D.texto_puro(c) for c in s["tabela"][0][1:]], ["Ciclo 1", "Ciclo 2", "Ciclo 3"])
        linhas = {D.texto_puro(r[0]): [D.texto_puro(c) for c in r[1:]] for r in s["tabela"][1:]}
        self.assertEqual(linhas["Células"], [self.v(f"D_C{c}_CEL") for c in "123"])
        self.assertEqual(linhas["Candidatos, 1ª opção"], [self.v(f"D_C{c}_CAND1") for c in "123"])
        self.assertEqual(linhas["Com origem"], [self.v(f"D_C{c}_P1") for c in "123"])
        self.assertEqual(sum(self.b(f"D_C{c}_P1") for c in "123"), self.b("M1_N"))
        self.assertIn("Ciclo = edital", D.texto_puro(s["marcadores"][0]))
        cron = (SAIDA / "cronologia_ciclos.csv").read_text(encoding="utf-8")
        for data in ("24/07/2025", "03/02/2026", "13/02/2026", "19/03/2026", "16/07/2026"):
            self.assertIn(data, cron)  # a cronologia cita a retificação de 13/02 (auditoria 49, A10)
            self.assertIn(data, corrido(s["notas"]))
        self.assertEqual(self.v("CR_C2_RETIF1302"), "13/02/2026")

    def test_regra_sharp(self) -> None:
        s = self.por_titulo["A bolsa é função exata do IVS: a regra é sharp"]
        txt = tela(s)
        self.assertIn(f"{self.v('R_C1_REPR')}/{self.v('R_C1_MUN')}", txt)
        self.assertIn(f"{self.v('R_C2_REPR')}/{self.v('R_C2_MUN')}", txt)
        self.assertEqual(self.v("R_C1_REPR"), self.v("R_C1_MUN"))
        self.assertEqual(self.v("R_C2_REPR"), self.v("R_C2_MUN"))

    def test_onde_escolhem(self) -> None:
        s = self.por_titulo["Onde escolhem: perto de onde já trabalham"]
        self.assertIn(f"{self.v('ESC_UF')}% põem a 1ª opção na UF de origem", tela(s))
        self.assertIn(f"{self.v('ESC_DIST_P50')} km", tela(s))
        self.assertIn("descritivo", tela(s))
        self.assertGreater(self.b("ESC_UF"), 0.5)  # "a maioria" (doc 07, §2)
        self.assertIn("preferência revelada", corrido(s["notas"]))

    # ---- metodologia e identificação ---------------------------------------------------------------------------

    def test_metodologia_em_palavras(self) -> None:
        espec = [s for s in self.slides if s["layout"] == "curto_espec"]
        self.assertEqual(len(espec), 1)
        m = espec[0]
        self.assertLessEqual(len(m["marcadores"]), 4)
        eq = m["marcadores"][0]
        self.assertFalse(eq.startswith("**"))
        for k in ("=", "bolsa", "distância", "origem"):
            self.assertIn(k, eq)
        self.assertEqual(rotulos(m), ["Comparação", "Teste"])
        self.assertIn("consigo mesmo", tela(m))
        notas = corrido(m["notas"])
        for k in ("Logit condicional", "comparado consigo mesmo", "Só o salto da bolsa nos cortes de IVS",
                  "D_UF", "Erro-padrão agrupado por conjunto de escolha", "efeito fixo do par", "13/02/2026",
                  "pós-resultado"):
            self.assertIn(k, notas, k)

    def test_identificacao(self) -> None:
        s = self.por_titulo["Identificação: as premissas e o nosso caso"]
        linhas = {D.texto_puro(r[0]): D.texto_puro(r[1]) for r in s["tabela"][1:]}
        self.assertEqual(linhas["Bolsa por regra"],
                         f"sharp: {self.v('R_C1_REPR')}/{self.v('R_C1_MUN')}, {self.v('R_C2_REPR')}/{self.v('R_C2_MUN')}")
        self.assertEqual(linhas["Só a bolsa?"], "não: pacote")
        self.assertEqual(linhas["Origem"], "preferência revelada")
        self.assertEqual(linhas["Hipótese"], "pós-resultado")
        self.assertIn("par de UFs", linhas["Localização"])
        self.assertIn("em parte", linhas["IIA"])
        notas = corrido(s["notas"])
        for k in ("auditoria 18", "auditoria 48", "vínculo anterior no CNES", "inconclusiva",
                  "condicional a se candidatar", f"p {self.v('VC_B_HOLM')}; família de um teste, Holm = p"):
            self.assertIn(k, notas, k)
        self.assertGreaterEqual(self.b("VC_B_HOLM"), 0.05)  # a especificação pré-registrada não passa no Holm

    # ---- resultados ---------------------------------------------------------------------------------------------

    def test_teste_central_origem_x_bolsa(self) -> None:
        """G-D: o teste central é origem × toda a bolsa (D_UF), com o quadro do ciclo 2 de 13/02/2026 (adendo 52c,
        auditoria 41); relido do registro: D_UF > 0 com IC longe de zero, a origem multiplica a chance muito mais que
        toda a bolsa, e o IC de toda a bolsa contém 1."""
        s = self.por_titulo["Teste central: a origem pesa mais que toda a bolsa"]
        self.assertIn(f"{self.ic('VC_DUF')} em log-chance; p {self.v('VC_DUF_P')}", tela(s))
        self.assertGreater(self.b("VC_DUF_INF"), 0.0)
        self.assertLess(self.b("VC_DUF_P"), 0.05)
        self.assertGreater(self.b("VC_THETAX_INF"), self.b("VC_B10X_SUP"))
        self.assertTrue(self.b("VC_B10X_INF") < 1.0 < self.b("VC_B10X_SUP"))
        self.assertAlmostEqual(self.b("VC_THETA_EST") - self.b("VC_B10_EST"), self.b("VC_DUF_EST"), places=6)
        self.assertIn("preferência revelada", s["cautela"])
        for c in ("VC_DUF_EST", "VC_THETA_EST", "VC_B10_EST"):
            self.assertIn("auditoria 41", self.todos[c]["auditoria"], c)
            self.assertIn("corrigida_13fev", json.dumps(self.todos[c]["seletor"]), c)
        notas = corrido(s["notas"])
        for k in ("Teste central", self.ic("VC_THETAX"), self.ic("VC_B10X"), self.ic("VC_THETA"), self.ic("VC_B10"),
                  "intervalo que contém 1", "pacote do corte", "vínculo anterior no CNES",
                  "condicional a se candidatar"):
            self.assertIn(k, notas, k)
        reg = self.man_fig["figuras_novas"]["curto_origem_bolsa.png"]
        self.assertEqual([ln["codigos"][0] for ln in reg["linhas"]], ["VC_THETAX_EST", "VC_B10X_EST"])
        self.assertTrue(any(self.ic("VC_DUF") in t for t in reg["textos"]))

    def test_bolsa_dentro_da_mesma_uf(self) -> None:
        """G-C: comparando vagas da mesma UF (adendo 52e, auditoria 48), por +R$ 5 mil, ciclos 1–3 e ciclo 2, com a
        versão base em cinza; dito como adendo pós-resultado, com o Holm da especificação pré-registrada na tela."""
        s = self.por_titulo["Dentro da mesma UF, a vaga de bolsa maior é preferida"]
        self.assertIn(f"{self.v('VL1_EMP_K5')} km a menos", tela(s))
        self.assertIn("pós-resultado", s["cautela"])
        self.assertIn(f"p {self.v('VC_B_HOLM')}", s["cautela"])  # família de um teste: Holm = p (auditoria 52)
        for k in ("EMP", "C2"):
            self.assertGreater(self.b(f"VL1_{k}_RCI"), 1.0, k)
            self.assertLess(self.b(f"VL1_{k}_HOLM"), 0.05, k)
        self.assertTrue(self.b("VLB_EMP_RCI") < 1.0 < self.b("VLB_EMP_RCS"))
        self.assertEqual(self.v("VLB_EMP_RC"), self.v("VLB_EMP_RC"))
        reg = self.man_fig["figuras_novas"]["curto_bolsa_mesma_uf.png"]
        self.assertEqual([ln["codigos"][0] for ln in reg["linhas"]],
                         ["VL1_EMP_RC", "VLB_EMP_RC", "VL1_C2_RC", "VLB_C2_RC"])
        notas = corrido(s["notas"])
        for k in (self.ic("VL1_EMP", "RC", "RCI", "RCS"), self.ic("VL1_C2", "RC", "RCI", "RCS"),
                  self.ic("VLB_EMP", "RC", "RCI", "RCS"), self.ic("VLB_C2", "RC", "RCI", "RCS"),
                  f"{self.v('VLB_EMP_K5')} km [{self.v('VLB_EMP_K5I')}; {self.v('VLB_EMP_K5S')}]",
                  "não testa a comparação com a origem", "Escolha não é expansão", "auditoria 48"):
            self.assertIn(k, notas, k)
        for c in ("VL1_EMP_RC", "VLB_EMP_K5"):
            self.assertIn("auditoria 48", self.todos[c]["auditoria"], c)

    def test_robustez(self) -> None:
        """Por ciclo (só o ciclo 2 com força), quadro do ciclo 2 de 13/02 contra o refeito, distância em log, região de
        saúde e comparação local (inconclusiva); à direita, origem − bolsa positiva nos três ciclos."""
        s = self.por_titulo["Robustez: a origem pesa mais em todos os ciclos"]
        self.assertIn("forte só no ciclo 2", tela(s))
        self.assertIn("perto do corte, inconclusivo", tela(s))
        for c in ("C1", "C3"):
            self.assertTrue(self.b(f"VC_M5{c}_RCI") < 1.0 < self.b(f"VC_M5{c}_RCS"), c)
        self.assertGreater(self.b("VC_M5C2_RCI"), 1.0)
        self.assertTrue(self.b("VL2_EMP_RCI") < 1.0 < self.b("VL2_EMP_RCS"))
        self.assertGreaterEqual(self.b("VL2_EMP_HOLM"), 0.05)
        for k in ("VLLOG_EMP", "VLLOG_C2", "VL3_EMP", "VL3_C2"):
            self.assertGreater(self.b(f"{k}_RCI"), 1.0, k)
        for c in ("C1", "C2", "C3"):
            self.assertGreater(self.b(f"VC_DUF_{c}_INF"), 0.0, c)
        reg = self.man_fig["figuras_novas"]["curto_robustez_escolha.png"]
        self.assertEqual([ln["codigos"][0] for ln in reg["linhas"]],
                         ["VLB_EMP_RC", "VC_M5C1_RC", "VC_M5C2_RC", "VC_M5C3_RC", "VC_M5C2A_RC", "VLLOG_EMP_RC", "VL3_EMP_RC",
                          "VL2_EMP_RC", "VC_DUF_C1_EST", "VC_DUF_C2_EST", "VC_DUF_C3_EST"])
        notas = corrido(s["notas"])
        for k in ("13/02/2026", "19/03/2026", self.ic("VC_DUF_C2"), self.ic("VL2_EMP", "RC", "RCI", "RCS"),
                  "inconclusivo", "não sabemos por quê", "spline cúbico", "logit explodido"):
            self.assertIn(k, notas, k)
        # auditorias 52 e 53: o pré-registrado (M1) abre a figura e a cautela; o VL-1 é adendo, não a principal
        self.assertIn("Pré-registrado: IC contém 1", s["cautela"])
        self.assertIn(self.ic("VLB_EMP", "RC", "RCI", "RCS"), notas)

    def test_quadro_corrigido_do_ciclo2(self) -> None:
        """Auditoria 49, A2: a H2 usa o quadro do ciclo 2 de 13/02/2026 (VC_*, versão corrigida); os números do quadro
        de 19/03 (H3_* do P1h e o M5 antigo) não aparecem como resultado."""
        texto = deck_doc04()
        self.assertNotIn("`H3_", texto)
        self.assertEqual((self.v("VC_DUF_EST"), self.v("VC_DUF_C2_EST")), ("1,94", "1,19"))
        self.assertNotIn(self.v("H3_DUF"), texto)
        self.assertNotIn(self.v("H3_S_M5C2"), texto)
        for c, e in self.todos.items():
            if c.startswith("VC_") and c != "VC_M5C2A_RC" and not c.startswith("VC_M5C2A"):
                self.assertIn("corrigida_13fev", json.dumps(e["seletor"]), c)

    def test_discussao(self) -> None:
        disc = [s for s in self.slides if s["secao"] == "Discussão"]
        self.assertEqual(len(disc), 1)
        s = disc[0]
        self.assertEqual(rotulos(s), ["Teoria", "Dados", "Leitura"])
        self.assertIn("incentivo limitado", tela(s))
        self.assertIn("sugerem", tela(s))
        self.assertIn("pacote do corte", tela(s))
        # auditoria 53: o que é dado (origem pesa mais que toda a bolsa) e o que é leitura (o custo de sair) separados
        self.assertIn("a origem pesa mais que toda a bolsa", tela(s))
        self.assertNotIn("custo que domina", tela(s))
        notas = corrido(s["notas"])
        for k in ("modelo da banca 1", "interpretação, não teste", "Não dá para afirmar", "que a bolsa reduz o "
                  "preenchimento", "pacote do corte"):
            self.assertIn(k, notas, k)

    # ---- apêndice ------------------------------------------------------------------------------------------------

    def test_apendice_o_fato(self) -> None:
        """G-A no apêndice, por corte: sem controle, com efeito fixo de UF e pareando na mesma UF; o negativo nunca
        passou no Holm e anda junto com a UF; a HI-2 cai em tamanho parecido nos três ciclos; o balanço falha em
        capital, Nordeste e especialistas na região; médico de outra UF em 0,400 é inconclusivo (auditorias 47, 49
        e 50)."""
        s = self.por_titulo["Apêndice · O fato: sem aumento detectado no corte"]
        self.assertIn("nunca passou no Holm", tela(s))
        self.assertIn("anda junto com a UF", tela(s))
        self.assertIn("Pacote do corte", s["cautela"])
        reg = self.man_fig["figuras_novas"]["curto_fato.png"]
        self.assertEqual([ln["codigos"][0] for ln in reg["linhas"]],
                         [f"{p}_{c}_TAU" for c in ("300", "400") for p in ("HI1", "PL_H41", "PL_FRAC")])
        for ln in reg["linhas"]:  # nenhuma linha do fato exclui zero
            self.assertFalse(ln["exclui_nulo"], ln["linha"])
        self.assertGreaterEqual(self.b("HI2_300_HOLM"), 0.05)
        self.assertLess(self.b("HI2_300_SUP"), 0.0)  # IC convencional sem zero, mas fora do Holm
        self.assertTrue(self.b("PL_H42_300_INF") < 0.0 < self.b("PL_H42_300_SUP"))
        self.assertGreater(self.b("PL_H42_300_TAU"), self.b("HI2_300_TAU"))  # encolhe com a UF
        for c in "123":
            self.assertLess(self.b(f"HI2_C{c}_300_TAU"), 0.0, c)
        self.assertTrue(self.b("PL_OUT_400_INF") <= 0.0 < self.b("PL_OUT_400_SUP"))
        notas = corrido(s["notas"])
        for k in ("nunca passou no Holm", "encolhe e deixa de se distinguir de zero", "três ciclos",
                  "o balanço falha", self.v("CL_BAL_CAP_300"), self.v("CL_BAL_NE_300"), self.v("CL_BAL_ESP_300"),
                  "inconclusivo", "não mostra que a bolsa reduz o preenchimento", "só detectaria saltos",
                  self.v("HI1_300_MDE")):
            self.assertIn(k, notas, k)
        for c in ("PL_H41_300_TAU", "PL_FRAC_300_TAU", "PL_OUT_400_TAU"):
            self.assertIn("auditoria 47", self.todos[c]["auditoria"], c)

    def test_apendice_h3(self) -> None:
        s = self.por_titulo["Apêndice · H3: oferta, numa frase"]
        self.assertIn(self.v("P4_HT_ATT") + " h/sem", tela(s))
        self.assertIn("vínculo cadastrado não é presença", s["cautela"])
        self.assertIn("Associação", s["cautela"])
        notas = corrido(s["notas"])
        self.assertIn("não se detecta diferença na oferta", notas)
        self.assertIn("não quer dizer que ela seja igual", notas)

    # ---- redação e números --------------------------------------------------------------------------------------

    def test_redacao_das_auditorias_49_e_50(self) -> None:
        texto = corrido(re.sub(r"(?m)^>\s?", "", deck_doc04()))
        for frase in PROIBIDAS:
            self.assertNotIn(frase, texto, frase)
        self.assertIsNone(re.search(r"\bsome\b", texto))
        for frase in ("não detectamos aumento", "sem aumento detectado", "Teste central",
                      "anda junto com a UF", "inconclusivo"):
            self.assertIn(frase, texto, frase)
        # guardas restauradas (auditoria 53): redação da auditoria 36, SOCR, "em auditoria", termos técnicos na tela
        for frase in PROIBIDAS_A36:
            self.assertNotIn(frase, texto, frase)
        self.assertNotIn("SOCR", texto)
        self.assertNotIn("em auditoria", texto.lower())
        for s in self.slides:
            for frase in ("escolhidas em 1º lugar", "candidato de 1ª opção", "52c", "fuzzy"):
                self.assertNotIn(frase, tela(s), f"{s['titulo']}: {frase}")
        for c, e in self.todos.items():
            if c.startswith(("HI", "PL_", "VL", "VC_")):
                self.assertNotIn("EM AUDITORIA", e["descricao"], c)

    def test_fato_mesma_amostra(self) -> None:
        """Auditoria 53: a linha com UF e raio do G-A usa uma amostra menor; o ponto sem controle nessa amostra vai
        na figura e nas notas, e a HI-2 sem controle na mesma amostra vem do registro, não da auditoria 47."""
        s = self.por_titulo["Apêndice · O fato: sem aumento detectado no corte"]
        notas = corrido(s["notas"])
        for c in ("PL_H41_300_SC", "PL_H41_400_SC", "PL_H42_300_SC"):
            self.assertIn(self.v(c), notas, c)
        self.assertNotIn("−0,55", notas)
        reg = self.man_fig["figuras_novas"]["curto_fato.png"]
        for c in ("300", "400"):
            self.assertTrue(any(f"sem controle nela: {self.v(f'PL_H41_{c}_SC')}" in t for t in reg["textos"]), c)

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
        texto = corrido(re.sub(r"(?m)^>\s?", "", deck_doc04())).lower()
        for frase in ("pacote do corte", "Formulada após ver os dados", "pós-resultado",
                      "origem é preferência revelada, não causa", "vínculo anterior no CNES",
                      "condicional a se candidatar", "participação no PMM-E", "interpretação, não teste",
                      "escolha não é expansão", "Associação", "vínculo cadastrado não é presença",
                      "não mostra que a bolsa reduz o preenchimento", "não quer dizer que ela seja igual"):
            self.assertIn(frase.lower(), texto, frase)
        self.assertNotIn("bolsa não funciona", texto)
        self.assertEqual(texto.count("a bolsa reduz"), texto.count("que a bolsa reduz"))


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
                n = sum(1 for w in texto.split() if re.search(r"[0-9A-Za-zÀ-ÖØ-öø-ÿ]", w))  # "×" não é letra
                self.assertLessEqual(n, D.MAX_PALAVRAS, f"{titulo}: {n} palavras")
        self.assertEqual(D.MAX_PALAVRAS, 30)
        self.assertTrue(all(o["palavras"] <= 30 for o in self.man["ordem"]))

    def test_rodape_com_as_oito_secoes(self) -> None:
        """O rodapé lista as oito seções e marca em negrito a do slide; no apêndice, nenhuma fica marcada."""
        with zipfile.ZipFile(CURTO) as z:
            for (parte, titulo, _), sl in zip(self.deck, self.slides):
                x = z.read(parte).decode("utf-8")
                nav = re.search(r'name="Navegação do rodapé".*?</p:sp>', x, flags=re.S).group(0)
                self.assertEqual("".join(re.findall(r"<a:t[^>]*>([^<]*)</a:t>", nav)), "  |  ".join(SECOES), titulo)
                negrito = re.findall(r'<a:rPr[^>]* b="1"[^>]*>.*?<a:t[^>]*>([^<]*)</a:t>', nav, flags=re.S)
                self.assertEqual(negrito, [] if sl["apendice"] else [sl["secao"]], titulo)

    def test_hipotese_em_destaque(self) -> None:
        parte = next(p for p, t, _ in self.deck if t.startswith("Hipótese:"))
        with zipfile.ZipFile(CURTO) as z:
            x = z.read(parte).decode("utf-8")
        central = re.search(r'name="Rótulo central".*?</p:sp>', x, flags=re.S).group(0)
        self.assertIn(D.VERDE_ESCURO, central)
        self.assertIn(">Hipótese<", central)
        cinzas = re.findall(r'name="Hipótese plano B".*?</p:sp>', x, flags=re.S)
        self.assertEqual(len(cinzas), 1)  # só a motivação, em cinza
        self.assertIn(D.CINZA_TEXTO, cinzas[0])

    def test_sem_planos_b_no_corpo(self) -> None:
        with zipfile.ZipFile(CURTO) as z:
            for parte, titulo, _ in self.deck:
                x = z.read(parte).decode("utf-8")
                tit = re.search(r'name="Título".*?</p:sp>', x, flags=re.S).group(0)
                self.assertNotIn(D.COR_TITULO_PLANO_B, tit, titulo)
                # só a motivação, no slide de Hipótese, sai em cinza; nenhum item de plano B no resto
                self.assertEqual(len(re.findall(r'name="(?:Item|Rótulo) plano B"', x)),
                                 1 if titulo.startswith("Hipótese:") else 0, titulo)
                if titulo.startswith("Dados"):  # variáveis secundárias em cinza
                    self.assertIn(D.CINZA_TEXTO, x, titulo)

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
