"""Testes do deck curto da banca 2 (`docs/07_apresentacoes/banca2/04_conteudo_deck_curto.md`).

O deck curto é o único usado na versão final (decisão do autor de 26/10/2026; doc 06) e é derivado do doc 04 por
`scripts/apresentacao/gerar_deck_banca2.py` (modo padrão). Desde 28/10/2026 (doc 07 da banca 2) o corpo tem uma
hipótese só, o efeito da bolsa na 1ª opção comparando vagas da mesma UF ("a hipótese é simplesmente sobre o efeito
bolsa → 1ª opção", "só comparação entre municípios da mesma UF"; "UF, origem etc. é tudo controle/pareamento"). O
resultado principal é o VL-1 (adendo 52e); nada da origem é resultado; o apêndice tem um slide, o fato da antiga H1
pareando municípios da mesma UF. Confere:

1. a estrutura obrigatória (doc 06): Hipótese, Dados, Análise descritiva, Metodologia, Identificação, Resultados,
   Robustez, Discussão, nesta ordem; no máximo 14 slides no corpo e 2 no apêndice, depois da Discussão; a sequência;
2. a regra do autor "texto demais": no máximo 30 palavras visíveis por slide, fora o título, a figura e a linha de
   fontes, no doc 04 e no próprio deck;
3. a hipótese única, sobre a bolsa na 1ª opção dentro da mesma UF, dita como formulada depois dos dados;
4. o conteúdo de cada seção: dados e fontes, regra *sharp* com "Como ler", os 79% como motivação do desenho, a
   descritiva F2 do doc 66, o logit com o efeito fixo do par de UFs e o teste β > 0, o que fica fixo, o VL-1 como
   principal, a robustez só dentro da mesma UF (com os ciclos 1 e 3 do adendo 52g) e a Discussão; cada número
   relido do registro;
5. nenhum resultado da origem na tela: sem "origem pesa", "×11" nem "D_UF" no corpo nem no apêndice;
6. o apêndice: o fato só com municípios pareados na mesma UF;
7. a redação das auditorias 49 e 50: nada de "não detectado" lido como "não muda", nem de números vencidos;
8. a regra dos números: todo número do doc 04 e do deck é o valor de um código listado ou um parâmetro;
9. o pacote gerado: títulos e texto iguais ao doc 04, rodapé com as oito seções, figuras do pipeline, manifesto com
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
T_HIP = "Pergunta e hipótese: a bolsa maior muda a 1ª opção?"
T_ONDE = "Onde escolhem: a maioria fica na própria UF"
T_F2 = "Descritivo: perto do corte, a bolsa maior é mais escolhida"
T_RES = "Dentro da mesma UF, a vaga de bolsa maior é preferida"
T_ROB = "Robustez: sempre comparando vagas da mesma UF"
T_CONC = "Conclusão: a bolsa maior aumenta a 1ª opção? Sim"
T_FATO = "Apêndice · O fato: pareando municípios da mesma UF"
SEQUENCIA = [  # (seção, título, layout); versão de 28/10/2026 (decisão do autor; doc 10, §6)
    ("Hipótese", T_HIP, "curto_hipotese"),
    ("Dados", "Dados e amostra: de onde vêm e quem entra no modelo", "curto_figura"),
    ("Análise descritiva", "A bolsa é função exata do IVS: a regra é sharp", "curto_figura"),
    ("Análise descritiva", T_ONDE, "curto_figura"),
    ("Análise descritiva", T_F2, "curto_figura"),
    ("Metodologia", "Modelo: logit condicional da 1ª opção", "curto_espec"),
    ("Identificação", "Identificação: as premissas e o nosso caso", "curto_tabela"),
    ("Resultados", T_RES, "curto_figura"),
    ("Robustez", T_ROB, "curto_figura"),
    ("Discussão", T_CONC, "curto_texto"),
    ("Discussão", "Limitações e o que cada uma implica", "curto_tabela"),
]  # sem apêndice (decisão do autor de 28/10/2026: nada de preenchimento)
FIGURAS = {  # título → figura de output/ (caminho a partir de output/)
    "Dados e amostra: de onde vêm e quem entra no modelo": "apresentacao_banca2/curto_dados_amostra.png",
    "A bolsa é função exata do IVS: a regra é sharp": "apresentacao_banca2/regra_bolsa_ivs_oficial.png",
    T_ONDE: "apresentacao_banca2/exp_escolha_origem.png",
    T_F2: "rdd_bolsa/H2_figuras/H2_F2_mesma_uf_perto_do_corte.png",  # F2 do doc 66 (script 51), sem redesenho
    T_RES: "apresentacao_banca2/curto_bolsa_mesma_uf.png",
    T_ROB: "apresentacao_banca2/curto_robustez_escolha.png",
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
             "p de Holm 0,072",
             # decisão do autor de 28/10/2026: a hipótese não fala da origem
             "pesa menos que a origem", "a origem pesa mais")
# Decisão do autor de 28/10/2026 ("UF, origem etc. é tudo controle/pareamento"): nenhum slide, nem do apêndice,
# interpreta o coeficiente da origem ou da UF
PROIBIDAS_TELA = ("origem pesa", "×11", "× 11", "D_UF", "θ", "Teste central", "toda a bolsa")
# Guardas antigas que a reescrita de 27/10/2026 tinha deixado de fora (auditoria 36 e 33; auditoria 53)
DOC09 = ROOT / "docs" / "07_apresentacoes" / "banca2" / "09_roteiro_fala_7min.md"
DOC10 = ROOT / "docs" / "07_apresentacoes" / "banca2" / "10_mapa_deck_anterior_para_rubrica.md"
VERSAO_ANTERIOR = SAIDA / "versoes" / "deck_banca2_curto_8901dea.pdf"
TEMPO_MIN, TEMPO_MAX = 390, 450  # roteiro de fala: de 6:30 a 7:30 (rubrica da banca; cerca de 7 minutos)
MARCA_ROTEIRO = re.compile(r"\*\*Roteiro \(\d+ s\)\.\*\*")  # o tempo-alvo é parâmetro de fala, não resultado
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
    return " ".join(txt.replace(" ", " ").split())


def rotulos(sl: dict) -> list[str]:
    return [re.match(r"\*\*(.+?)\*\*", m).group(1) for m in sl["marcadores"] if m.startswith("**")]


def numeros_listados(bloco: str) -> list[str]:
    m = re.search(r"(?m)^\*\*Números:\*\*(.*?)(?=\n\n|\Z)", bloco, flags=re.S)
    return re.findall(r"`([A-Z0-9_]+)`", m.group(1)) if m else []


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

    def rc(self, base: str) -> str:
        return self.ic(base, "RC", "RCI", "RCS")

    # ---- estrutura e forma -------------------------------------------------------------------------------------

    def test_estrutura_obrigatoria(self) -> None:
        self.assertEqual(D.SECOES_CURTO, SECOES)
        D.conferir_estrutura(self.slides)
        self.assertEqual([(s["secao"], s["titulo"], s["layout"]) for s in self.slides], SEQUENCIA)
        self.assertEqual([s["apendice"] for s in self.slides], [s == "Apêndice" for s, _, _ in SEQUENCIA])
        self.assertLessEqual(len([s for s in self.slides if not s["apendice"]]), 11)  # pedido do autor: até 11
        regra = " ".join(DOC06.read_text(encoding="utf-8").split())
        self.assertIn("30 palavras", regra)  # a regra do autor está registrada no doc 06, §2
        self.assertIn("no máximo 14 slides", regra)
        self.assertIn("apêndice", regra.lower())

    def test_no_maximo_14_slides_e_apendice_curto(self) -> None:
        """Decisões do autor de 26 e 27/10/2026: no máximo 14 slides no corpo e 2 no apêndice, que vem no fim."""
        self.assertEqual((D.MAX_SLIDES_CURTO, D.MAX_APENDICE_CURTO), (MAX_SLIDES, MAX_APENDICE))
        corpo = [s for s in self.slides if not s["apendice"]]
        self.assertEqual([s for s in self.slides if s["apendice"]], [])  # sem apêndice desde 28/10/2026
        apend = [dict(corpo[-1], apendice=True, roteiro=None, tempo_s=None)]  # apêndice fictício, só para a regra
        self.assertLessEqual(len(corpo), MAX_SLIDES)
        with self.assertRaises(SystemExit):  # corpo com 15 slides
            D.conferir_estrutura(corpo + [corpo[-1]] * (MAX_SLIDES + 1 - len(corpo)) + apend)
        with self.assertRaises(SystemExit):  # apêndice com 3 slides
            D.conferir_estrutura(corpo + apend * 3)
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
        """Cada slide de figura usa a figura prevista, lida de output/; as figuras novas trazem "Como ler"; a da
        regra sharp, que vem da galeria, leva o "Como ler" na tela (auditoria 49, A8); a F2 traz o seu."""
        for tit, rel in FIGURAS.items():
            sl = self.por_titulo[tit]
            self.assertTrue(sl["imagem"].as_posix().endswith(f"output/{rel}"), tit)
        novas = self.man_fig["figuras_novas"]
        for nome in ("curto_bolsa_mesma_uf.png", "curto_robustez_escolha.png",
                     "exp_escolha_origem.png", "curto_dados_amostra.png"):
            self.assertTrue(any(t.startswith("Como ler") for t in novas[nome]["textos"]), nome)
        regra = self.por_titulo["A bolsa é função exata do IVS: a regra é sharp"]
        self.assertTrue(D.texto_puro(regra["marcadores"][0]).startswith("Como ler:"))
        self.assertIn("Como ler", corrido(regra["notas"]))

    # ---- hipótese única ----------------------------------------------------------------------------------------

    def test_hipotese_unica_pos_resultado(self) -> None:
        """O corpo tem uma hipótese só, sobre a bolsa na 1ª opção comparando vagas da mesma UF, dita como formulada
        depois dos dados (decisão do autor de 28/10/2026); a motivação (o fato) é uma linha, sem gráfico."""
        hip = self.por_titulo[T_HIP]
        self.assertEqual(rotulos(hip), ["Hipótese", "Motivação"])
        self.assertTrue(D.rotulo_central("Hipótese") and not D.rotulo_central("Motivação"))
        self.assertIsNone(hip["imagem"])
        self.assertIn("após ver os dados", hip["cautela"])
        frase = D.texto_puro(hip["marcadores"][0]).replace("**", "")
        self.assertIn("mesma UF", frase)
        self.assertIn("bolsa maior", frase)
        self.assertIn("1ª opção", frase)
        self.assertNotIn("origem", frase)
        self.assertIn("a bolsa sobe com o IVS", tela(hip))
        notas = corrido(hip["notas"])
        for k in ("pós-resultado", "interpretação, não teste", "pacote do corte", "condicional a se candidatar",
                  "controle e pareamento", "28/10/2026"):
            self.assertIn(k, notas, k)
        for s in self.slides:
            if s["apendice"]:
                self.assertTrue(s["titulo"].startswith("Apêndice · "), s["titulo"])
                continue
            self.assertIsNone(re.match(r"H\d", s["titulo"]), s["titulo"])
            self.assertIsNone(re.search(r"\bH[13]\b", tela(s)), s["titulo"])
            self.assertNotIn("plano B", s["titulo"])

    # ---- dados e análise descritiva ----------------------------------------------------------------------------

    def test_dados_unidade_e_funil(self) -> None:
        """Rubrica (base de dados): origem dos dados, variáveis, unidade de observação e construção da amostra."""
        s = self.por_titulo[SEQUENCIA[1][1]]
        self.assertEqual(rotulos(s), ["Unidade:", "No modelo:"])
        txt = tela(s)
        self.assertIn("candidato × vaga do seu curso e ciclo; y = 1 na 1ª opção", txt)
        # pedido do autor (28/10/2026): deixar claro que é a opção marcada, não a ida ao município
        self.assertIn("opção marcada, não ida ao município", s["cautela"])
        self.assertIn("não medimos se ele foi alocado nem se entrou no município", corrido(s["roteiro"]))
        self.assertIn(f"{self.v('M1_N')} candidatos e {self.v('AM_PARES')} pares candidato × vaga", txt)
        # o funil encaixa: R1 − não ligados = ligados; − sem vínculo = com origem; − sem região = modelo
        for c in "123":
            r1, nlig, svin, sreg = (self.b(f"AM_C{c}_{k}") for k in ("R1", "NLIG", "SVIN", "SREG"))
            self.assertEqual(r1, self.b(f"D_C{c}_CAND1"), c)  # o mesmo R1 do quadro de células
            self.assertEqual(r1 - nlig, self.b(f"AM_C{c}_LIG"), c)
            self.assertEqual(r1 - nlig - svin, self.b(f"AM_C{c}_ORI"), c)
            self.assertEqual(self.b(f"AM_C{c}_ORI") - sreg, self.b(f"D_C{c}_P1"), c)
            self.assertGreaterEqual(sreg, 0.0, c)
        self.assertEqual(self.b("AM_TOT_ORI"), self.b("ESC_N"))  # a descritiva da origem é a mesma amostra
        self.assertEqual(sum(self.b(f"D_C{c}_P1") for c in "123"), self.b("M1_N"))
        for k in ("R1", "LIG", "ORI"):
            self.assertEqual(self.b(f"AM_TOT_{k}"), sum(self.b(f"AM_C{c}_{k}") for c in "123"), k)
        for c in ("AM_PARES", "AM_CONJ", "AM_VAGAS", "AM_C1_NLIG"):
            self.assertIn("P1_resumo.json", json.dumps(self.todos[c]["seletor"]), c)
        reg = self.man_fig["figuras_novas"]["curto_dados_amostra.png"]
        self.assertEqual([ln["codigos"][-1] for ln in reg["funil"] if not ln["etapa"].startswith("−")],
                         ["AM_TOT_R1", "AM_TOT_LIG", "AM_TOT_ORI", "M1_N"])
        for ln in reg["funil"]:
            self.assertEqual(ln["valores"], [self.v(c) for c in ln["codigos"]], ln["etapa"])
        textos = " ".join(reg["textos"])
        for k in ("De onde vêm os dados", "Construção da amostra", "1ª opção (y)", "CNES, vínculo antes da inscrição",
                  "Ipea", "IBGE", "SGTES/MS", "não a residência",
                  f"{self.v('AM_PARES')} pares candidato × vaga, em {self.v('AM_CONJ')} conjuntos"):
            self.assertIn(k, textos, k)
        notas = corrido(s["notas"])
        for k in ("13/02/2026", "vínculo médico no CNES", "não é a residência", "Unidade do modelo"):
            self.assertIn(k, notas, k)
        cron = (SAIDA / "cronologia_ciclos.csv").read_text(encoding="utf-8")
        for data in ("24/07/2025", "03/02/2026", "13/02/2026", "19/03/2026", "16/07/2026"):
            self.assertIn(data, cron)  # a cronologia cita a retificação de 13/02 (auditoria 49, A10)
            self.assertIn(data, notas)
        self.assertEqual(self.v("CR_C2_RETIF1302"), "13/02/2026")

    def test_regra_sharp(self) -> None:
        s = self.por_titulo["A bolsa é função exata do IVS: a regra é sharp"]
        txt = tela(s)
        self.assertIn(f"{self.v('R_C1_REPR')}/{self.v('R_C1_MUN')}", txt)
        self.assertIn(f"{self.v('R_C2_REPR')}/{self.v('R_C2_MUN')}", txt)
        self.assertEqual(self.v("R_C1_REPR"), self.v("R_C1_MUN"))
        self.assertEqual(self.v("R_C2_REPR"), self.v("R_C2_MUN"))

    def test_onde_escolhem_motivacao_do_desenho(self) -> None:
        """Os 79% na própria UF são a motivação para comparar dentro da UF, não resultado (28/10/2026)."""
        s = self.por_titulo[T_ONDE]
        self.assertIn(f"{self.v('ESC_UF')}% põem a 1ª opção na UF de origem", tela(s))
        self.assertIn(f"{self.v('ESC_DIST_P50')} km", tela(s))
        self.assertIn("descritivo", tela(s))
        self.assertIn("Por isso: comparamos só vagas da mesma UF", tela(s))
        self.assertGreater(self.b("ESC_UF"), 0.5)  # "a maioria"
        notas = corrido(s["notas"])
        self.assertIn("preferência revelada", notas)
        self.assertIn("não é resultado", notas)
        self.assertIn("não é o nosso resultado", corrido(s["roteiro"]))

    def test_descritiva_F2_mesma_uf(self) -> None:
        """A F2 do doc 66 (script 51, auditoria 52) é a descritiva da hipótese: perto do corte, na UF de origem, o lado
        de bolsa maior recebe mais 1ªs opções do que tem de vagas. Números relidos do H2_sintese.csv pelo registro."""
        s = self.por_titulo[T_F2]
        txt = tela(s)
        self.assertIn(f"{self.v('H2D_DISP')}% das vagas, {self.v('H2D_ESC')}% das 1ªs opções", txt)
        self.assertIn(f"{self.v('H2D_N')} candidatos", txt)
        self.assertIn("na UF de origem", txt)
        self.assertIn("Descritivo: sem teste e sem controlar a distância", s["cautela"])
        self.assertGreater(self.b("H2D_ESC"), self.b("H2D_DISP"))
        for c in ("H2D_DISP", "H2D_ESC", "H2D_N"):
            self.assertIn("H2_sintese.csv", self.todos[c]["arquivo"], c)
            self.assertIn("auditoria 52", self.todos[c]["auditoria"], c)
        self.assertIn("VL-2", corrido(s["notas"]))  # a versão com inferência é inconclusiva
        self.assertIn("inconclusiva", corrido(s["notas"]))

    # ---- metodologia e identificação ---------------------------------------------------------------------------

    def test_metodologia_em_palavras(self) -> None:
        espec = [s for s in self.slides if s["layout"] == "curto_espec"]
        self.assertEqual(len(espec), 1)
        m = espec[0]
        self.assertLessEqual(len(m["marcadores"]), 4)
        eq = m["marcadores"][0]
        self.assertFalse(eq.startswith("**"))
        for k in ("U = β·bolsa", "γ·distância", "EF(UF origem × UF vaga)", "P(j) = e^Uj/Σe^U"):
            self.assertIn(k, eq)
        self.assertNotIn("θ", eq)  # a origem não tem coeficiente interpretado (28/10/2026)
        self.assertEqual(rotulos(m), ["Por quê", "Bolsa", "Teste"])
        for k in ("consigo mesmo", "vagas da mesma UF", "regra do IVS", "β > zero", "cluster por conjunto"):
            self.assertIn(k, tela(m), k)
        self.assertIn("erro-padrão agrupado por conjunto de escolha", corrido(m["roteiro"]))
        notas = corrido(m["notas"])
        for k in ("Logit condicional", "comparado consigo mesmo", "Só o salto da bolsa nos cortes de IVS",
                  "efeito fixo do par", "não são interpretados", "13/02/2026", "pós-resultado", "score bootstrap"):
            self.assertIn(k, notas, k)

    def test_identificacao(self) -> None:
        s = self.por_titulo["Identificação: as premissas e o nosso caso"]
        linhas = {D.texto_puro(r[0]): D.texto_puro(r[1]) for r in s["tabela"][1:]}
        self.assertEqual(linhas["Bolsa por regra"],
                         f"sharp: {self.v('R_C1_REPR')}/{self.v('R_C1_MUN')}, {self.v('R_C2_REPR')}/{self.v('R_C2_MUN')}")
        self.assertEqual(linhas["Mantido fixo"], "candidato, par de UFs, distância")
        self.assertEqual(linhas["Só a bolsa?"], "não: pacote do corte")
        self.assertEqual(linhas["Especificação"], "pós-resultado (adendo 52e)")
        self.assertEqual(linhas["Conjunto"], "suposto: todas vistas")  # premissa não testável (auditoria 55)
        self.assertEqual(len(linhas), 5)
        notas = corrido(s["notas"])
        for k in ("auditoria 18", "auditoria 48", "vínculo anterior no CNES", "condicional a se candidatar",
                  "nenhum deles é resultado", self.rc("VLB_EMP"),
                  f"p {self.v('VC_B_HOLM')}; família de um teste, Holm = p"):
            self.assertIn(k, notas, k)
        self.assertIn("contém 1", corrido(s["roteiro"]))
        self.assertTrue(self.b("VLB_EMP_RCI") < 1.0 < self.b("VLB_EMP_RCS"))  # pré-registrado: IC contém 1
        self.assertGreaterEqual(self.b("VC_B_HOLM"), 0.05)

    # ---- resultados ---------------------------------------------------------------------------------------------

    def test_sem_resultado_da_origem(self) -> None:
        """Decisão do autor de 28/10/2026: nenhum slide, nem do apêndice, interpreta o coeficiente da origem ou da UF;
        o D_UF fica só numa linha das notas do slide de Limitações, para pergunta da banca."""
        for s in self.slides:
            for frase in PROIBIDAS_TELA:
                self.assertNotIn(frase, tela(s), f"{s['titulo']}: {frase}")
                self.assertNotIn(frase, s["titulo"], f"{s['titulo']}: {frase}")
            self.assertFalse(s["imagem"] is not None and s["imagem"].name == "curto_origem_bolsa.png", s["titulo"])
        for b in self.blocos:
            tit = b.splitlines()[0][3:]
            cods = numeros_listados(b)
            for c in cods:
                self.assertFalse(c.startswith(("VC_THETA", "VC_B10")), f"{tit}: {c}")
                if c.startswith("VC_DUF"):
                    self.assertEqual(tit, "Limitações e o que cada uma implica", c)
        lim = corrido(self.por_titulo["Limitações e o que cada uma implica"]["notas"])
        self.assertIn("não é interpretado aqui", lim)

    def test_resultado_principal_VL1(self) -> None:
        """O resultado principal é o VL-1 (adendo 52e, auditoria 48): vagas da mesma UF, ciclos 1–3 e ciclo 2, com os
        km; a figura não tem a linha do modelo base; a especificação pré-registrada fica na cautela e nas notas."""
        s = self.por_titulo[T_RES]
        txt = tela(s)
        self.assertIn(f"chance ×{self.rc('VL1_EMP')}.", txt)
        # leitura simples na tela (pedido do autor, 28/10); o ciclo 2 fica na figura e nas notas
        self.assertIn(f"o médico aceita vaga {self.v('VL1_EMP_K5')} km mais longe", txt)
        self.assertIn(self.v("VL1_C2_RC"), corrido(s["notas"]))
        self.assertNotIn(self.v("VLB_EMP_K5"), txt)  # 75 km na tela, não os 119 do M1 (auditoria 53)
        self.assertIn("pós-resultado", s["cautela"])
        self.assertIn("sem fixar a UF: IC contém 1", s["cautela"])
        self.assertEqual((self.v("VL1_EMP_RC"), self.v("VL1_EMP_RCI"), self.v("VL1_EMP_RCS")), ("1,47", "1,15", "1,89"))
        self.assertEqual((self.v("VL1_C2_RC"), self.v("VL1_C2_RCI"), self.v("VL1_C2_RCS")), ("1,90", "1,30", "2,78"))
        self.assertEqual(self.v("VL1_EMP_K5"), "75")
        for k in ("EMP", "C2"):
            self.assertGreater(self.b(f"VL1_{k}_RCI"), 1.0, k)
            self.assertLess(self.b(f"VL1_{k}_HOLM"), 0.05, k)
            self.assertIn("VL_estimativas.csv", self.todos[f"VL1_{k}_RC"]["arquivo"], k)
        reg = self.man_fig["figuras_novas"]["curto_bolsa_mesma_uf.png"]
        self.assertEqual([ln["codigos"][0] for ln in reg["linhas"]], ["VL1_EMP_RC", "VL1_C2_RC"])  # sem o base
        self.assertFalse(any("VLB" in c for ln in reg["linhas"] for c in ln["codigos"]))
        notas = corrido(s["notas"])
        for k in (self.rc("VL1_EMP"), self.rc("VL1_C2"), self.rc("VLB_EMP"), self.rc("VLB_C2"),
                  f"{self.v('VL1_EMP_K5')} km [{self.v('VL1_EMP_K5I')}; {self.v('VL1_EMP_K5S')}]",
                  "Escolha não é expansão", "auditoria 48", "Pacote do corte"):
            self.assertIn(k, notas, k)

    def test_robustez_so_dentro_da_mesma_UF(self) -> None:
        """Só variantes que comparam vagas da mesma UF: distância em log, região de saúde × UF da vaga, só vagas perto
        do corte (inconclusiva) e o VL-1 por ciclo, com os ciclos 1 e 3 do adendo 52g (VG_estimativas.csv)."""
        s = self.por_titulo[T_ROB]
        self.assertEqual(rotulos(s), ["Mantém:", "Por ciclo:", "Perto do corte:"])
        txt = tela(s)
        self.assertIn("forte só no ciclo 2; nos ciclos 1 e 3 o IC contém 1", txt)
        self.assertIn("inconclusivo", txt)
        for c in ("VG1", "VG3"):
            self.assertTrue(self.b(f"{c}_RCI") < 1.0 < self.b(f"{c}_RCS"), c)
            self.assertIn("VG_estimativas.csv", self.todos[f"{c}_RC"]["arquivo"], c)
        self.assertEqual(self.rc("VG1"), "1,15 [0,66; 2,01]")
        self.assertEqual(self.rc("VG3"), "1,25 [0,90; 1,73]")
        self.assertGreater(self.b("VL1_C2_RCI"), 1.0)
        self.assertTrue(self.b("VL2_EMP_RCI") < 1.0 < self.b("VL2_EMP_RCS"))
        self.assertGreaterEqual(self.b("VL2_EMP_HOLM"), 0.05)
        for k in ("VLLOG_EMP", "VLLOG_C2", "VL3_EMP", "VL3_C2"):
            self.assertGreater(self.b(f"{k}_RCI"), 1.0, k)
        reg = self.man_fig["figuras_novas"]["curto_robustez_escolha.png"]
        self.assertEqual([ln["codigos"][0] for ln in reg["linhas"]],
                         ["VL1_EMP_RC", "VLLOG_EMP_RC", "VL3_EMP_RC", "VL2_EMP_RC", "VL3P_EMP_RC", "VK1_300_RC",
                          "VK1_400_RC", "VG1_RC", "VL1_C2_RC", "VG3_RC"])
        self.assertFalse(any(c.startswith("VC_") for ln in reg["linhas"] for c in ln["codigos"]))
        self.assertNotIn(" km", txt)  # os km dos ciclos 1 e 3 têm IC com zero: fora da tela
        notas = corrido(s["notas"])
        for k in (self.rc("VG1"), self.rc("VG3"), self.rc("VL2_EMP"), self.rc("VLLOG_EMP"), self.rc("VL3_EMP"),
                  "inconclusivo", "não sabemos", "auditoria pendente", "52g"):
            self.assertIn(k, notas, k)

    def test_quadro_corrigido_do_ciclo2(self) -> None:
        """Auditoria 49, A2: a escolha usa o quadro do ciclo 2 de 13/02/2026 (VC_*, versão corrigida); os números do
        quadro de 19/03 (H3_* do P1h e o M5 antigo) não aparecem como resultado."""
        texto = deck_doc04()
        self.assertNotIn("`H3_", texto)
        self.assertNotIn("VC_M5C2A", texto)
        self.assertNotIn(self.v("H3_DUF"), texto)
        self.assertNotIn(self.v("H3_S_M5C2"), texto)
        for c, e in self.todos.items():
            if c.startswith("VC_") and not c.startswith("VC_M5C2A"):
                self.assertIn("corrigida_13fev", json.dumps(e["seletor"]), c)

    def test_discussao_conclusao_e_limitacoes(self) -> None:
        """Rubrica (conclusões e limitações): a Conclusão retoma a pergunta do slide 1 ("a bolsa maior aumenta a
        chance de a vaga ser a 1ª opção, comparando vagas da mesma UF? Sim, forte no ciclo 2"); as Limitações vêm
        cada uma com a sua implicação (tabela)."""
        disc = [s for s in self.slides if s["secao"] == "Discussão"]
        self.assertEqual([s["layout"] for s in disc], ["curto_texto", "curto_tabela"])
        conc, lim = disc
        self.assertIn("a bolsa maior muda a 1ª opção?", self.slides[0]["titulo"])  # a pergunta, no slide 1
        self.assertIn("a bolsa maior aumenta a 1ª opção? Sim", conc["titulo"])  # retomada na Conclusão
        self.assertEqual(rotulos(conc), ["Resposta", "Força", "Teoria"])
        txt = tela(conc)
        for k in (f"sim, comparando vagas da mesma UF: chance ×{self.v('VL1_EMP_RC')}",
                  f"forte só no ciclo 2 (×{self.v('VL1_C2_RC')})", "os dados sugerem"):
            self.assertIn(k, txt, k)
        self.assertIn("Voltando à pergunta", conc["roteiro"])
        self.assertIn("comparando vagas da mesma UF? Sim", corrido(conc["roteiro"]))
        notas = corrido(conc["notas"])
        for k in ("modelo da banca 1", "interpretação, não teste", "Não dá para afirmar", "pacote do corte"):
            self.assertIn(k, notas, k)
        self.assertEqual([D.texto_puro(c) for c in lim["tabela"][0]], ["Limitação", "Implicação"])
        par = {D.texto_puro(r[0]): D.texto_puro(r[1]) for r in lim["tabela"][1:]}
        self.assertEqual(par, {"Pós-resultado": "exploratório", "Sem fixar UF": "IC contém 1",
                               "Só inscrição": "≠ ida ao município", "Pacote do corte": "bolsa não isolada",
                               "Só ciclo 2": "não generalizar", "Origem = CNES": "≠ residência"})
        rot = corrido(lim["roteiro"])
        for k in ("pós-resultado", "Sem fixar a UF", "se candidatou", "não quem entrou no município",
                  "pacote do corte", "ciclo 2", "não a residência"):
            self.assertIn(k, rot, k)
        notas = corrido(lim["notas"])
        self.assertIn("Perguntas prováveis da banca", notas)
        self.assertEqual(len(re.findall(r"\bP[1234], \"", notas)), 4)
        self.assertIn(f"{self.rc('VL1_EMP')}, p de Holm {self.v('VL1_EMP_HOLM')}", notas)
        self.assertIn(self.rc("VLB_EMP"), notas)
        self.assertIn(self.rc("VG1"), notas)
        self.assertIn(self.rc("VG3"), notas)

    def test_roteiro_de_fala(self) -> None:
        """Rubrica (apresentador): cada slide do corpo tem roteiro de fala com tempo-alvo; a soma fica entre 6:30 e
        7:30, a cerca de 140 palavras por minuto; o apêndice não é apresentado; o doc 09 traz o mesmo roteiro."""
        corpo = [s for s in self.slides if not s["apendice"]]
        self.assertTrue(all(s["roteiro"] and s["tempo_s"] for s in corpo))
        self.assertTrue(all(not s["roteiro"] for s in self.slides if s["apendice"]))
        total = sum(s["tempo_s"] for s in corpo)
        self.assertTrue(TEMPO_MIN <= total <= TEMPO_MAX, total)
        self.assertEqual((D.TEMPO_MIN_S, D.TEMPO_MAX_S), (TEMPO_MIN, TEMPO_MAX))
        falas = sum(D.palavras(s["roteiro"]) for s in corpo)
        self.assertTrue(120 <= falas / total * 60 <= 160, falas)
        for s in corpo:  # nenhum slide fala rápido demais (até 175 palavras por minuto)
            self.assertLessEqual(D.palavras(s["roteiro"]) / s["tempo_s"] * 60, 175, s["titulo"])
            for frase in PROIBIDAS_TELA:  # nem a fala interpreta a origem
                self.assertNotIn(frase, s["roteiro"], f"{s['titulo']}: {frase}")
        with self.assertRaises(SystemExit):  # o gerador para se o roteiro passar de 7:30
            D.conferir_roteiro([dict(s, tempo_s=s["tempo_s"] * 2) if not s["apendice"] else s for s in self.slides])
        with self.assertRaises(SystemExit):  # ou se faltar roteiro num slide do corpo
            D.conferir_roteiro([dict(corpo[0], roteiro="")] + self.slides[1:])
        # o doc 09 traz o mesmo roteiro, slide a slide, com o mesmo tempo e o total
        t9 = DOC09.read_text(encoding="utf-8")
        for k, s in enumerate(corpo, 1):
            m = re.search(rf"(?ms)^## {k}\. (.+?) \((\d+) s\)\n\n(.*?)(?=\n\n|\Z)", t9)
            self.assertIsNotNone(m, k)
            self.assertEqual(m.group(1), s["titulo"], k)
            self.assertEqual(int(m.group(2)), s["tempo_s"], k)
            self.assertEqual(corrido(m.group(3)), corrido(s["roteiro"]), k)
        self.assertIn(f"Total: {D.mmss(total)}", t9)
        self.assertIn("Perguntas prováveis", t9)
        falado = t9[t9.index("\n## 1. "):]  # a tabela de tempos (metas de fala) fica de fora
        achados = {x for x in T.tokens(T.limpar(falado)) if not T.ano(x)}
        validos = T.PERMITIDOS | T.todos_valores(self.registro)
        tempos = {str(s["tempo_s"]) for s in corpo} | {str(k) for k in range(1, len(corpo) + 1)}
        self.assertEqual(achados - validos - tempos, set())

    def test_doc10_mapa_e_versao_anterior(self) -> None:
        """Mapa do deck de 27/10/2026 (33d15d9) para o de 28/10/2026 (doc 10, §6): cada título novo aparece no doc 10,
        com o texto da tela dos slides do corpo; os títulos que saíram também; a cópia rotulada do PDF de 8901dea
        existe e o hash confere."""
        t10 = corrido(DOC10.read_text(encoding="utf-8"))
        self.assertIn("Mudança de 28/10", t10)
        for s in self.slides:
            self.assertIn(s["titulo"], t10, s["titulo"])
        for tit in ("Teste central: a origem pesa mais que toda a bolsa",
                    "Conclusão: a origem pesa mais que toda a bolsa? Sim",
                    "Pergunta e hipótese: origem ou bolsa na escolha?", "Apêndice · H3: oferta, numa frase"):
            self.assertIn(tit, t10, tit)  # os títulos do deck de 27/10/2026
        for s in self.slides:
            if s["apendice"]:
                continue
            for item in [t for t, _ in D.linhas_curtas(s)]:
                self.assertIn(corrido(D.texto_puro(item).replace("**", "")), t10, s["titulo"])
            for linha in s["tabela"][1:]:
                self.assertIn(f"{D.texto_puro(linha[0])} | {D.texto_puro(linha[1])}", t10, s["titulo"])
        self.assertTrue(VERSAO_ANTERIOR.exists())
        self.assertIn(sha256(VERSAO_ANTERIOR), t10)
        # o tempo de fala de cada slide é meta de fala, não resultado
        sem_tempo = re.sub(r"Tempo de fala: \d+ s", "", DOC10.read_text(encoding="utf-8"))
        achados = {x for x in T.tokens(T.limpar(sem_tempo)) if not T.ano(x)}
        validos = T.PERMITIDOS | T.todos_valores(self.registro)
        livres = {x for x in achados if x.lstrip("+").isdigit() and int(x.lstrip("+")) <= 15}  # nº de slide
        self.assertEqual(achados - validos - livres, set())

    # ---- apêndice ------------------------------------------------------------------------------------------------

    def test_sem_preenchimento_e_sem_apendice(self) -> None:
        """Decisão do autor de 28/10/2026 ("não é pra ter nada de preenchimento, só escolha na primeira opção"): o
        deck não tem apêndice, e nem a tela, nem o roteiro, nem as notas falam de preenchimento."""
        self.assertFalse(any(s["apendice"] for s in self.slides))
        self.assertNotIn("preench", deck_doc04().lower())
        with zipfile.ZipFile(CURTO) as z:
            for n in z.namelist():
                if n.startswith(("ppt/slides/slide", "ppt/notesSlides/")) and n.endswith(".xml"):
                    self.assertNotIn("preench", unescape(z.read(n).decode("utf-8")).lower(), n)

    # ---- redação e números --------------------------------------------------------------------------------------

    def test_redacao_das_auditorias_49_e_50(self) -> None:
        texto = corrido(re.sub(r"(?m)^>\s?", "", deck_doc04()))
        for frase in PROIBIDAS:
            self.assertNotIn(frase, texto, frase)
        self.assertIsNone(re.search(r"\bsome\b", texto))
        self.assertIn("inconclusivo", texto)  # sem preenchimento desde 28/10/2026: "não detectamos aumento" saiu
        # guardas restauradas (auditoria 53): redação da auditoria 36, SOCR, "em auditoria", termos técnicos na tela
        for frase in PROIBIDAS_A36:
            self.assertNotIn(frase, texto, frase)
        self.assertNotIn("SOCR", texto)
        self.assertNotIn("em auditoria", texto.lower())
        for s in self.slides:
            for frase in ("escolhidas em 1º lugar", "candidato de 1ª opção", "52c", "fuzzy"):
                self.assertNotIn(frase, tela(s), f"{s['titulo']}: {frase}")
        for c, e in self.todos.items():
            if c.startswith(("HI", "PL_", "VL", "VC_", "VG")):
                self.assertNotIn("EM AUDITORIA", e["descricao"], c)

    def test_todo_numero_registrado_ou_parametro(self) -> None:
        sobra = {}
        permitidos_base = set(T.PERMITIDOS)
        for b in self.blocos:
            m = re.search(r"(?m)^\*\*Números:\*\*(.*?)(?=\n\n|\Z)", b, flags=re.S)
            self.assertIsNotNone(m, b.splitlines()[0])
            codigos = re.findall(r"`([A-Z0-9_]+)`", m.group(1))
            sem_linha = re.sub(r"(?m)^\*\*Números:\*\*.*?(?=\n\n|\Z)", "", b, flags=re.S)
            b = MARCA_ROTEIRO.sub("", b)
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
        for frase in ("pacote do corte", "Formulada após ver os dados", "pós-resultado", "preferência revelada",
                      "vínculo anterior no CNES", "condicional a se candidatar", "participação no PMM-E",
                      "interpretação, não teste", "escolha não é expansão", "comparando vagas da mesma UF",
                      "IC contém 1", "sem fixar a UF"):
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

    def test_tela_sem_resultado_da_origem(self) -> None:
        """Decisão do autor de 28/10/2026: no deck gerado, nenhum slide (nem do apêndice) diz "origem pesa", "×11" ou
        "D_UF"; o slide de hipótese fala de vagas da mesma UF; o VL-1 é o resultado principal na tela."""
        for _, titulo, texto in self.deck:
            corr = " ".join(texto.replace(" ", " ").split())
            for frase in PROIBIDAS_TELA:
                self.assertNotIn(frase, corr, f"{titulo}: {frase}")
        hip = next(t for _, tit, t in self.deck if tit.startswith("Pergunta e hipótese:"))
        self.assertIn("mesma UF", hip)
        res = next(" ".join(t.split()) for _, tit, t in self.deck if tit == T_RES)
        self.assertIn("×1,47 [1,15; 1,89]", res)

    def test_hipotese_em_destaque(self) -> None:
        parte = next(p for p, t, _ in self.deck if t.startswith("Pergunta e hipótese:"))
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
                                 1 if titulo.startswith("Pergunta e hipótese:") else 0, titulo)

    def test_notas_com_roteiro(self) -> None:
        """As notas de cada slide do corpo abrem pelo roteiro de fala, com o tempo-alvo, em parágrafo próprio; o
        apêndice não tem roteiro. O manifesto registra o tempo total e a versão anterior."""
        with zipfile.ZipFile(CURTO) as z:
            for (parte, titulo, _), sl in zip(self.deck, self.slides):
                r = z.read(parte.replace("slides/", "slides/_rels/") + ".rels").decode("utf-8")
                nota = "ppt/notesSlides/" + re.search(r'Target="\.\./notesSlides/([^"]+)"', r).group(1)
                paras = [unescape("".join(re.findall(r"<a:t>([^<]*)</a:t>", p)))
                         for p in re.findall(r"<a:p>(.*?)</a:p>", z.read(nota).decode("utf-8"), flags=re.S)]
                if sl["apendice"]:
                    self.assertFalse(any(p.startswith("FALA") for p in paras), titulo)
                else:
                    self.assertEqual(paras[0], f"FALA ({D.mmss(sl['tempo_s'])}): " + D.texto_puro(sl["roteiro"]),
                                     titulo)
                    self.assertTrue(paras[1].startswith("DETALHE PARA PERGUNTAS: "), titulo)
        rot = self.man["roteiro"]
        self.assertEqual(rot["tempo_total_s"], sum(s["tempo_s"] or 0 for s in self.slides))
        self.assertTrue(TEMPO_MIN <= rot["tempo_total_s"] <= TEMPO_MAX)
        self.assertEqual(self.man["versao_anterior"]["sha256"], sha256(VERSAO_ANTERIOR))

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
