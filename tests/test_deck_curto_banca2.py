"""Testes do deck curto da banca 2 (`docs/07_apresentacoes/banca2/04_conteudo_deck_curto.md`).

O deck curto é o único usado na versão final (decisão do autor de 26/10/2026; doc 06) e é derivado do doc 04 por
`scripts/apresentacao/gerar_deck_banca2.py` (modo padrão). Confere:

1. a estrutura obrigatória (doc 06): Hipótese, Dados, Análise descritiva, Metodologia, Identificação, Resultados,
   Robustez, Discussão, nesta ordem; no máximo 14 slides (decisão do autor de 26/10/2026); a sequência pedida;
2. a regra do autor "texto demais": no máximo 30 palavras visíveis por slide, fora o título, a figura e a linha de
   fontes, no doc 04 e no próprio deck; especificação em até 4 linhas curtas, com a equação em palavras no centro;
3. a numeração da apresentação a partir de 26/10/2026 (H1 preenchimento; H2 bolsa × origem, antes H3; H3 oferta,
   antes H4), a H1 central em destaque e H2 e H3 em cinza, como plano B (na hipótese, na especificação e no
   slide de planos B); cada seção começa pela H1;
4. Dados numa tabela só, com as secundárias em cinza; os ciclos explicados; a Identificação com o tipo de vaga
   (doc 05, §2.12) como premissa não testada;
5. a H1 principal do adendo 48b (saídas HI_*, em auditoria: a cautela e a linha de fontes dizem isso), o scatter
   só com vagas imediatas e o TOST HI-s7 numa linha, e a medida antiga como especificação secundária, em
   Robustez;
6. a queda em 0,300 (auditoria 36: as capitais; sem a explicação errada pelo cadastro reserva do ciclo 2;
   auditoria 33: sem "escolhidas em 1º lugar" como fato), o doc 57m auditado (auditoria 37) nas notas, a H1 por
   ciclo, a nota 52c da H2 só nas notas, a H3 nos dois níveis (doc 05, §2.13) e a Discussão;
7. a regra dos números: todo número do doc 04 e do deck é o valor de um código listado ou um parâmetro;
8. o pacote gerado: títulos e texto iguais ao doc 04, rodapé com as oito seções, manifesto com hashes atuais e, se
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
MAX_SLIDES = 14  # decisão do autor de 26/10/2026: "idealmente <15 slides" (doc 06, §2)
SEQUENCIA = [  # (seção, título, layout)
    ("Hipótese", "Hipóteses: a H1 é a candidata central", "curto_hipotese"),
    ("Dados", "Dados: as variáveis e de onde vêm", "curto_tabela"),
    ("Análise descritiva", "Os três ciclos em números", "curto_tabela"),
    ("Análise descritiva", "A bolsa é função exata do IVS: a regra é sharp", "curto_figura"),
    ("Análise descritiva", "H1 · Dados crus, só vagas imediatas", "curto_figura"),
    ("Metodologia", "H1 · O salto no corte, só com vagas imediatas", "curto_espec"),
    ("Identificação", "H1 · RDD: as premissas e o nosso caso", "curto_tabela"),
    ("Resultados", "H1 · Só vagas imediatas: nada passa no Holm", "curto_figura"),
    ("Robustez", "H1 · Antes e depois do controle das vagas", "curto_figura"),
    ("Robustez", "H1 · Por ciclo: a queda em 0,300 vem do ciclo 2", "curto_figura"),
    ("Robustez", "H1 · Controlando a capital, a queda encolhe", "curto_figura"),
    ("Discussão", "H1 · Por que o sinal sai negativo", "curto_texto"),
    ("Discussão", "H2 e H3 · plano B: origem pesa; oferta incerta", "curto_texto"),
    ("Discussão", "Discussão: por que não sobe? Um incentivo limitado", "curto_texto"),
]
LINHA_POR_CICLO = "A queda em 0,300 vem sobretudo do ciclo 2; por ciclo, os intervalos são largos."
# auditoria 36: a ideia "no ciclo 2, a vaga de reserva não podia ser preenchida" está errada e não pode voltar
PROIBIDAS_A36 = ("não podia ser preenchida", "só de reserva", "só de cadastro reserva", "vagas de reserva",
                 "células só de CR", "reserva não")
A36_MUN = ROOT / "output" / "auditoria_H1" / "a36_municipios.csv"
HIP = re.compile(r"^(H\d)(?: e (H\d))? ·")


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
    return " ".join(txt.replace(" ", " ").split())


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

    def test_estrutura_obrigatoria(self) -> None:
        self.assertEqual(D.SECOES_CURTO, SECOES)
        D.conferir_estrutura(self.slides)
        self.assertEqual([(s["secao"], s["titulo"], s["layout"]) for s in self.slides], SEQUENCIA)
        self.assertFalse(any(s["apendice"] for s in self.slides))
        regra = " ".join(DOC06.read_text(encoding="utf-8").split())
        self.assertIn("30 palavras", regra)  # a regra do autor está registrada no doc 06, §2
        self.assertIn("no máximo 14 slides", regra)

    def test_no_maximo_14_slides(self) -> None:
        """Decisão do autor de 26/10/2026: o deck curto tem no máximo 14 slides; o gerador para se passar."""
        self.assertEqual(D.MAX_SLIDES_CURTO, MAX_SLIDES)
        self.assertLessEqual(len(self.slides), MAX_SLIDES)
        with self.assertRaises(SystemExit):
            D.conferir_estrutura(self.slides + self.slides[-1:])
        self.assertIn(f"slides: {len(self.slides)}", DOC04.read_text(encoding="utf-8"))

    def test_no_maximo_30_palavras(self) -> None:
        for s in self.slides:
            D.conferir_curto(s)  # para (SystemExit) se fugir do formato
            self.assertLessEqual(D.palavras_visiveis(s), 30, s["titulo"])
            self.assertLessEqual(len(s["titulo"]), D.MAX_TITULO_CURTO, s["titulo"])
            self.assertEqual(s["layout"] == "curto_ficha", False, s["titulo"])  # fichas longas saíram

    def test_contagem_de_palavras_sintetica(self) -> None:
        self.assertEqual(D.palavras("**H2 · central** a bolsa → mais 1,98 [1,56; 2,40]"), 8)
        self.assertEqual(D.palavras("preenchida = salto + reta"), 3)
        self.assertEqual(D.palavras("salto × lado ÷ reta"), 3)  # "×" e "÷" soltos não são palavra

    def test_numeracao_das_hipoteses(self) -> None:
        """H1 preenchimento; H2 bolsa × origem (antes H3); H3 oferta (antes H4). Nada de H4 no deck curto."""
        corpo = DOC04.read_text(encoding="utf-8")
        deck = corpo[corpo.index("<!-- deck:inicio -->"):]
        self.assertNotIn("H4", re.sub(r"\(antes H4\)", "", deck))
        for s in self.slides:
            m = HIP.match(s["titulo"])
            if not m:
                continue
            self.assertIn(m.group(1), ("H1", "H2", "H3"), s["titulo"])
            # H2 e H3 são plano B (decisão do autor de 26/10/2026): o título diz isso
            self.assertEqual("plano B" in s["titulo"], m.group(1) != "H1", s["titulo"])
        hip = self.por_titulo["Hipóteses: a H1 é a candidata central"]
        self.assertEqual(rotulos(hip), ["H1 · central", "H2 · plano B", "H3 · plano B"])
        self.assertIn("H2 bolsa × origem (antes H3); H3 oferta (antes", corrido(hip["notas"]))
        reg = self.registro["numeracao_das_hipoteses"]
        self.assertIn("H2 bolsa × origem (antes H3); H3 oferta (antes H4)", reg)
        self.assertEqual(self.todos["H3_DUF"]["hipotese_apresentacao"], "H2")
        self.assertEqual(self.todos["P4_HT_ATT"]["hipotese_apresentacao"], "H3")
        self.assertEqual(self.todos["N1_300_TAU"]["hipotese_apresentacao"], "H1")
        # a H2 antiga (escolha por ciclo) não tem slide
        self.assertFalse(any("só o ciclo 2" in s["titulo"] for s in self.slides))

    def test_dados_principais_e_secundarias(self) -> None:
        """Uma tabela só, com a fonte de cada variável; as secundárias em itálico, que o gerador pinta de cinza."""
        s = self.por_titulo["Dados: as variáveis e de onde vêm"]
        self.assertEqual(len(s["tabela"][0]), 2)
        self.assertEqual(D.texto_puro(s["tabela"][0][1]), "Fonte")
        sec = [D.texto_puro(r[0]) for r in s["tabela"][1:] if D._linha_italica(r)]
        pri = [D.texto_puro(r[0]) for r in s["tabela"][1:] if not D._linha_italica(r)]
        self.assertEqual(sec, ["Capital, porte", "Regras no corte"])
        self.assertIn("Bolsa", pri)
        self.assertIn("IVS 2010", pri)
        self.assertTrue(all(r[1].strip() for r in s["tabela"][1:]))  # toda variável tem fonte
        self.assertIn("13/02/2026", corrido(s["notas"]))

    def test_ciclos_explicados(self) -> None:
        s = self.por_titulo["Os três ciclos em números"]
        self.assertEqual([D.texto_puro(c) for c in s["tabela"][0][1:]], ["Ciclo 1", "Ciclo 2", "Ciclo 3"])
        self.assertEqual(len(s["marcadores"]), 1)
        self.assertIn("Ciclo = edital de vagas", D.texto_puro(s["marcadores"][0]))
        cron = (SAIDA / "cronologia_ciclos.csv").read_text(encoding="utf-8")
        for data in ("24/07/2025", "03/02/2026", "16/07/2026"):  # as datas das notas são as da cronologia
            self.assertIn(data, cron)
            self.assertIn(data, corrido(s["notas"]))

    def test_especificacoes_curtas(self) -> None:
        espec = [s for s in self.slides if s["layout"] == "curto_espec"]
        self.assertEqual([s["titulo"][:4] for s in espec], ["H1 ·"])
        h1 = espec[0]
        self.assertLessEqual(len(h1["marcadores"]), 4)
        self.assertFalse(h1["marcadores"][0].startswith("**"))
        self.assertIn("=", h1["marcadores"][0])
        self.assertIn("salto", h1["marcadores"][0])
        self.assertIn("vagas imediatas", h1["marcadores"][0])
        self.assertIn("rro-padrão", " ".join(h1["marcadores"]))  # h, kernel e erro-padrão na tela
        self.assertIn("triangular", " ".join(h1["marcadores"]))
        self.assertIn("0,050", " ".join(h1["marcadores"]))
        # H2 e H3 numa linha cada, com rótulo que o gerador pinta de cinza (plano B)
        rot = rotulos(h1)
        self.assertEqual([r for r in rot if D.eh_plano_b(r)], ["H2", "H3"])
        self.assertFalse(D.eh_plano_b(rot[0]))
        notas = corrido(h1["notas"])
        for k in ("HI-1", "HI-2", "Holm", "h = 0,050", "cada corte separado", "13/02/2026",
                  "erro-padrão agrupado por município", "erro-padrão agrupado por conjunto de escolha",
                  "bootstrap multiplicador", "Rambachan–Roth"):
            self.assertIn(k, notas, k)

    def test_identificacao(self) -> None:
        """Premissas e aderência numa tabela, com o tipo de vaga (doc 05, §2.12) como premissa não testada."""
        s = self.por_titulo["H1 · RDD: as premissas e o nosso caso"]
        linhas = {D.texto_puro(r[0]): D.texto_puro(r[1]) for r in s["tabela"][1:]}
        self.assertEqual(linhas["Regra sharp"], "368/368, 454/454")
        self.assertEqual(linhas["Só a bolsa"], "não: pacote")
        self.assertEqual(linhas["Outro incentivo individual em 0,300"], "nenhum")
        self.assertEqual(linhas["Tipo de vaga (MS) exógeno"], "não testado")
        self.assertIn("capitais", linhas["Sem manipulação, balanço"])
        notas = corrido(s["notas"])
        for k in ("auditoria 35", "auditoria 18", "§2.12", "pode responder ao corte", "limites de Lee"):
            self.assertIn(k, notas, k)
        self.assertEqual(self.todos["R_C1_REPR"]["valor"] + "/" + self.todos["R_C1_MUN"]["valor"], "368/368")

    def test_h1_central_e_hipoteses_contiguas(self) -> None:
        """Cada seção de Metodologia a Discussão começa pela H1; dentro da seção, H1, depois H2, depois H3."""
        for sec in ("Metodologia", "Identificação", "Resultados", "Robustez", "Discussão"):
            hs = [int(HIP.match(s["titulo"]).group(1)[1]) for s in self.slides
                  if s["secao"] == sec and HIP.match(s["titulo"])]
            self.assertTrue(hs and hs[0] == 1, sec)
            self.assertEqual(hs, sorted(hs), sec)
        n = {h: sum(1 for s in self.slides if HIP.match(s["titulo"]) and HIP.match(s["titulo"]).group(1) == h)
             for h in ("H1", "H2", "H3")}
        self.assertGreater(n["H1"], 2 * (n["H2"] + n["H3"]))  # a H1 tem o maior espaço

    def test_h1_principal_do_48b(self) -> None:
        """A H1 principal é a do adendo 48b (HI_*), em auditoria, com o TOST numa linha; a medida antiga fica em
        Robustez."""
        self.assertTrue(HI_RESUMO.exists())
        res = [s for s in self.slides if s["secao"] == "Resultados"]
        self.assertEqual(len(res), 1)
        h1 = res[0]
        self.assertTrue(h1["titulo"].startswith("H1 ·"))
        self.assertNotIn("aguardando", h1["titulo"])
        self.assertTrue(h1["imagem"].as_posix().endswith("output/rdd_bolsa/HI_figuras/HI_principal.png"))
        self.assertEqual(D.texto_puro(h1["marcadores"][0]), "Nada passa no Holm; HI-1: IC contém zero nos dois cortes.")
        self.assertEqual(D.texto_puro(h1["marcadores"][1]),
                         "TOST: HI-2 em 0,300 descarta aumento ≥ 25% da média, não descarta queda.")
        self.assertIn("Em auditoria", h1["cautela"])  # rótulo "em auditoria" na tela
        v = {c: float(e["valor_bruto"]) for c, e in self.todos.items() if c.startswith("HI") and "LEIT" not in c}
        self.assertTrue(all(v[f"HI{h}_{c}_HOLM"] >= 0.05 for h in "12" for c in ("300", "400")))
        self.assertTrue(v["HI1_300_INF"] < 0 < v["HI1_300_SUP"] and v["HI1_400_INF"] < 0 < v["HI1_400_SUP"])
        self.assertLess(v["HI2_300_SUP"], 0.0)
        leit = {c: self.todos[f"HI_EQ{c}_LEIT"]["valor"] for c in ("1_300", "1_400", "2_300", "2_400")}
        self.assertEqual(leit, {"1_300": "INCONCLUSIVO", "1_400": "INCONCLUSIVO", "2_300": "SO_AUMENTO",
                                "2_400": "INCONCLUSIVO"})
        self.assertIn("Não dá para dizer que nada mudou", corrido(h1["notas"]))
        for s in self.slides:  # saídas do 48b ainda em auditoria: a linha de fontes diz isso
            if s["imagem"] is not None and "HI_figuras" in s["imagem"].as_posix() or "HI_estimativas" in s["fontes"]:
                self.assertIn("em auditoria", s["fontes"], s["titulo"])
        for c, e in self.todos.items():
            if c.startswith("HI"):
                self.assertIn("EM AUDITORIA", e["auditoria"], c)
        rob = [s["imagem"].name for s in self.slides if s["secao"] == "Robustez"]
        self.assertEqual(rob, ["h1_controle.png", "curto_h1_por_ciclo.png", "curto_queda_capital.png"])
        nomes = [s["imagem"].name for s in self.slides if s["imagem"] is not None]
        self.assertNotIn("HI_por_ciclo.png", nomes)  # uma figura por ciclo só: a do curto, mais legível no slide
        self.assertFalse(any("TOST" in s["titulo"] or "afirmar" in s["titulo"] for s in self.slides))

    def test_descritiva_dados_crus(self) -> None:
        crus = self.por_titulo["H1 · Dados crus, só vagas imediatas"]
        self.assertTrue(crus["imagem"].as_posix().endswith("output/rdd_bolsa/HI_figuras/HI_scatter_imediatas.png"))
        notas = corrido(crus["notas"])
        self.assertIn("A distância crua entre as retas não é a estimativa", notas)
        # a subida dentro da faixa (doc 57m) ficou nas notas, na versão auditada (auditoria 37)
        self.assertIn("auditoria 37", notas)
        self.assertIn(self.todos["GF_10_ORIG"]["valor"], notas)
        for c, e in self.todos.items():
            if c.startswith("GF_"):
                self.assertIn("auditoria 37", e["auditoria"], c)
        self.assertEqual(self.todos["DQ_FUN_PRE_ABX0"]["valor"], "33")
        self.assertEqual(self.todos["DQ_FUN_PRE_ACI0"]["valor"], "33")

    def test_queda_e_capitais(self) -> None:
        """Auditoria 36: controlando a capital, a queda encolhe; a explicação pelo cadastro reserva do ciclo 2 saiu."""
        c = self.por_titulo["H1 · Controlando a capital, a queda encolhe"]
        self.assertEqual(c["imagem"].name, "curto_queda_capital.png")
        self.assertIn("Controlando a capital, a queda encolhe e o IC contém zero; só com vagas imediatas, encolhe",
                      tela(c))
        self.assertIn("13 capitais abaixo de 0,300 e 6 acima", tela(c))
        self.assertIn("Auditoria 36", c["cautela"])
        self.assertEqual((self.todos["A36_CAP_ABX"]["valor"], self.todos["A36_CAP_ACI"]["valor"]), ("13", "6"))
        for k in ("A3", "TX", "N1"):
            self.assertGreater(float(self.todos[f"A36_{k}_CAP_SUP"]["valor_bruto"]), 0.0, k)  # IC com dummy contém zero
            self.assertLess(abs(float(self.todos[f"A36_{k}_CAP_TAU"]["valor_bruto"])),
                            abs(float(self.todos[f"A36_{k}_PIPE_TAU"]["valor_bruto"])), k)  # a queda encolhe
        for k in ("A3", "TX"):
            self.assertGreater(float(self.todos[f"A36_{k}_VI_SUP"]["valor_bruto"]), 0.0, k)
            self.assertIn("auditoria 36", self.todos[f"A36_{k}_VI_TAU"]["auditoria"])
        # as quatro capitais a menos de 0,010 abaixo do corte, e nenhuma acima, relidas da saída da auditoria 36
        import pandas as pd
        m = pd.read_csv(A36_MUN, dtype=str, keep_default_na=False)
        m = m[m["capital"] == "1"].drop_duplicates("co_ibge")
        ivs = m["ivs"].astype(float)
        abaixo = sorted(m.loc[(ivs > 0.290) & (ivs <= 0.300), "nome_municipio_uf"].str.split(" (", regex=False).str[0])
        self.assertEqual(abaixo, ["Brasília", "Goiânia", "Natal", "São Paulo"])
        self.assertEqual(int(((ivs > 0.300) & (ivs < 0.310)).sum()), 0)
        self.assertIn("São Paulo, Goiânia, Natal e Brasília", corrido(c["notas"]))
        # a ideia errada (auditoria 36) não volta, nem na tela nem nas notas
        texto = DOC04.read_text(encoding="utf-8")
        deck = corrido(re.sub(r"(?m)^>\s?", "", texto[texto.index("<!-- deck:inicio -->"):]))
        for proibida in PROIBIDAS_A36:
            self.assertNotIn(proibida, deck, proibida)
        self.assertNotIn("SOCR", texto[texto.index("<!-- deck:inicio -->"):])
        # correção M1 da auditoria 33: "menos células escolhidas em 1º lugar" não vai à tela como fato
        for s in self.slides:
            self.assertNotIn("escolhidas em 1º lugar", tela(s), s["titulo"])
            self.assertNotIn("candidato de 1ª opção", tela(s), s["titulo"])
        self.assertFalse(any(s["selo"] for s in self.slides))

    def test_h2_reestimacao_52c_so_nas_notas(self) -> None:
        for s in self.slides:
            if s["titulo"].startswith("H2"):
                self.assertIn("Reestimação em curso (52c)", corrido(s["notas"]), s["titulo"])
            self.assertNotIn("52c", tela(s), s["titulo"])

    def test_h1_por_ciclo(self) -> None:
        s = self.por_titulo["H1 · Por ciclo: a queda em 0,300 vem do ciclo 2"]
        self.assertEqual(s["imagem"].name, "curto_h1_por_ciclo.png")
        self.assertEqual(D.texto_puro(s["marcadores"][0]), LINHA_POR_CICLO)
        self.assertIn("quadro refeito depois do resultado (auditoria 36)", s["cautela"])
        man = json.loads(MANIF_FIG.read_text(encoding="utf-8"))
        reg = man["figuras_novas"]["curto_h1_por_ciclo.png"]
        esperado = {f"PC_{m}_{c}_{k}_TAU" for m in ("A3", "TX") for c in ("1", "2", "3", "J") for k in ("300", "400")}
        self.assertEqual({ln["codigos"][0] for ln in reg["linhas"]}, esperado)
        self.assertFalse(any("auditoria 36 em curso" in x for x in reg["textos"]))
        # os ciclos juntos repetem os números já publicados (A3 e taxa por vaga, doc 49b)
        self.assertEqual(self.todos["PC_A3_J_300_TAU"]["valor"], self.todos["A3_300_TAU"]["valor"])
        self.assertEqual(self.todos["PC_TX_J_300_TAU"]["valor"], self.todos["ND_TX300"]["valor"])

    def test_discussao(self) -> None:
        disc = [s for s in self.slides if s["secao"] == "Discussão"]
        sinal = disc[0]
        self.assertEqual(rotulos(sinal), ["Reta", "Vagas", "Porte", "Incentivo"])
        self.assertIn("capitais e Nordeste logo abaixo de 0,300", tela(sinal))
        self.assertIn("nenhum individual muda em 0,300", tela(sinal))
        notas = corrido(sinal["notas"])
        self.assertIn("auditoria 35", notas)
        self.assertIn("Nada disso mostra que a bolsa reduz o preenchimento", notas)
        self.assertIn(self.todos["DQ_FUN_PRE_ABX"]["valor"], notas)
        teoria = disc[-1]
        self.assertEqual(rotulos(teoria), ["Incentivo limitado", "Pacote do corte", "Oferta"])
        self.assertIn("vínculo cadastrado não é presença", tela(teoria))
        self.assertIn("A história parte da H1", corrido(teoria["notas"]))

    def test_planos_b(self) -> None:
        """H2 com um número por ciclo; H3 nos dois níveis (doc 05, §2.13): o +6,6 h é do próprio médico."""
        s = self.por_titulo["H2 e H3 · plano B: origem pesa; oferta incerta"]
        self.assertEqual(rotulos(s), ["H2", "H3", "H3 · município"])
        self.assertTrue(all(D.eh_plano_b(r) for r in rotulos(s)))
        h2, h3, mun = (D.texto_puro(m) for m in s["marcadores"])
        por_ciclo = [self.todos[f"H3_S_M5C{c}"]["valor"] for c in "123"]
        self.assertIn(" · ".join(por_ciclo), h2)
        self.assertIn("ciclos 1–3", h2)
        self.assertIn(self.todos["P4_HT_ATT"]["valor"] + " h/sem do próprio médico", h3)
        self.assertIn("aumento não afirmável; outros especialistas não saem", mun)
        notas = corrido(s["notas"])
        for k in ("não diz nada sobre os outros médicos do município", "Rambachan–Roth", "parte B",
                  self.todos["P4_ORIGEM"]["valor"] + "%"):
            self.assertIn(k, notas, k)

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
        for frase in ("pacote do corte", "Pacote do corte", "H2 é pós-resultado",
                      "origem é preferência revelada, não efeito causal", "horas cadastradas não são presença",
                      "vínculo não é presença", "vínculo cadastrado não é presença", "Associação",
                      "não é a participação no PMM-E", "Nada disso mostra que a bolsa reduz o preenchimento",
                      "não é efeito zero", "escolha não é expansão", "Em auditoria"):
            self.assertIn(frase.lower(), deck.lower(), frase)
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
                n = sum(1 for w in texto.split() if re.search(r"[0-9A-Za-zÀ-ÖØ-öø-ÿ]", w))  # "×" não é letra
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
        self.assertIn("H1 · central", next(tx for _, t, tx in self.deck if t.startswith("Hipóteses")))
        with zipfile.ZipFile(CURTO) as z:
            x = z.read(parte).decode("utf-8")
        central = re.search(r'name="Rótulo central".*?</p:sp>', x, flags=re.S).group(0)
        self.assertIn(D.VERDE_ESCURO, central)
        planos = re.findall(r'name="Hipótese plano B".*?</p:sp>', x, flags=re.S)
        self.assertEqual(len(planos), 2)
        for p in planos:
            self.assertIn(D.CINZA_TEXTO, p)
            self.assertIn(D.CINZA_FUNDO, p)

    def test_plano_b_em_cinza(self) -> None:
        with zipfile.ZipFile(CURTO) as z:
            for parte, titulo, _ in self.deck:
                x = z.read(parte).decode("utf-8")
                tit = re.search(r'name="Título".*?</p:sp>', x, flags=re.S).group(0)
                self.assertEqual(D.COR_TITULO_PLANO_B in tit, "plano B" in titulo, titulo)
                n_b = len(re.findall(r'name="Item plano B"', x))
                if titulo.startswith("H2 e H3 · plano B"):
                    self.assertEqual(n_b, 3, titulo)  # H2, H3 no médico e H3 no município, todos em cinza
                    self.assertEqual(len(re.findall(r'name="Item"', x)), 0, titulo)
                elif titulo.startswith("H1 · O salto no corte"):
                    self.assertEqual(n_b, 2, titulo)  # as linhas de H2 e H3 sob a especificação da H1
                elif not titulo.startswith("Hipóteses"):
                    self.assertEqual(n_b, 0, titulo)
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
