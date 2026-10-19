"""Relatório da RDD da bolsa (`scripts/rdd_bolsa/09_gerar_relatorio_pdf.py`): parte II, rodada multi-outcome.

Lê o HTML gravado em `output/rdd_bolsa/relatorio_resultados_rdd_bolsa.html` e as saídas que ele cita. Confere:
- as seções da parte II e da parte I estão presentes, com as hipóteses primárias antes das secundárias;
- toda tabela da parte II tem uma caixa "Como ler" antes;
- todo número das seções da parte II vem de um arquivo de `output/` (ou de um documento canônico que a seção
  copia), e os números-chave (P1, P2, E9) batem com as saídas;
- toda figura incorporada é um PNG gravado pelo pipeline em `output/rdd_bolsa/E*_figuras/`, byte a byte;
- o HTML está em dia com as saídas (SHA-256 de cada fonte no apêndice B);
- a seção "Síntese (E8)" mostra "pendente" sem `E8_resumo.json` e nunca inventa conteúdo.

O único dado sintético é o JSON da classe `TestSinteseE8Sintetico`, gravado numa pasta temporária (nunca em
`output/`) só para conferir que a seção renderiza o que lê.
"""

from __future__ import annotations

import base64
import hashlib
import html
import importlib.util
import json
import math
import re
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "output" / "rdd_bolsa" / "relatorio_resultados_rdd_bolsa.html"
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "09_gerar_relatorio_pdf.py"
SCRIPT_E7 = ROOT / "scripts" / "rdd_bolsa" / "14_estimar_E7_dird_cnes.py"


def _importar(nome: str, caminho: Path):
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    antes = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        sys.modules[nome] = mod
        spec.loader.exec_module(mod)
    finally:
        sys.dont_write_bytecode = antes
    return mod


R = _importar("relatorio_rdd_bolsa_teste", SCRIPT)


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def secoes_mo(texto: str) -> list[str]:
    return re.findall(r'(<section[^>]*data-rodada="multioutcome"[^>]*>.*?</section>)', texto, re.S)


# ---------------------------------------------------------------------------
# Números: tokens do HTML e valores das fontes
# ---------------------------------------------------------------------------

# Constantes de exibição e de método que não são resultado: nível do IC (95%), valor crítico normal (1,96) e o
# limiar de exibição de p (< 0,001).
PERMITIDOS = {"95", "1.96", "0.001"}
PT = re.compile(r"(?<![\w.,/])(\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+(?:,\d+)?)(?![\w/]|[.,]\d)")
EN = re.compile(r"(?<![\w])(\d+\.\d+(?:[eE][-+]?\d+)?)")


def _canon_pt(tok: str) -> str:
    t = tok.replace(".", "").replace(",", ".")
    return t


def _formatos(x: float, out: set[str]) -> None:
    if not math.isfinite(x):
        return
    for v in (abs(x), abs(100 * x)):
        for nd in range(5):
            out.add(f"{v:.{nd}f}")
    out.add(repr(abs(x)))


def _tokens_texto(s: str, out: set[str]) -> None:
    for m in EN.finditer(s):
        try:
            _formatos(float(m.group(1)), out)
        except ValueError:
            pass
    for m in PT.finditer(s):
        c = _canon_pt(m.group(1))
        out.add(c)
        try:
            _formatos(float(c), out)
        except ValueError:
            pass


def _walk(obj, out: set[str]) -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            _tokens_texto(str(k), out)
            _walk(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _walk(v, out)
    elif isinstance(obj, bool) or obj is None:
        return
    elif isinstance(obj, (int, float)):
        _formatos(float(obj), out)
    else:
        _tokens_texto(str(obj), out)


def valores_das_fontes(arquivos: list[Path]) -> set[str]:
    out: set[str] = set()
    for p in arquivos:
        if not p.exists():
            continue
        if p.suffix == ".csv":
            d = pd.read_csv(p, dtype=str, keep_default_na=False)
            for col in d.columns:
                for v in d[col].unique():
                    try:
                        _formatos(float(v), out)
                    except ValueError:
                        _tokens_texto(v, out)
        elif p.suffix == ".json":
            _walk(json.loads(p.read_text(encoding="utf-8")), out)
        else:
            _tokens_texto(p.read_text(encoding="utf-8"), out)
    return out


def texto_numerico(secao: str) -> str:
    """Texto visível da seção, sem código, imagens, frases geradas pelo E7 e referências estruturais."""
    s = re.sub(r"<img[^>]*>", " ", secao)
    s = re.sub(r'<p class="gerado".*?</p>', " ", s, flags=re.S)
    s = re.sub(r"<code>.*?</code>", " ", s, flags=re.S)
    s = html.unescape(re.sub(r"<[^>]+>", " ", s))
    padroes = [
        r"(?<!\d)20\d{2}(?:0[1-9]|1[0-2])(?!\d)",  # competência AAAAMM
        r"\d{2}/\d{2}/\d{4}", r"\d{4}-\d{2}-\d{2}", r"\d{4}-\d{2}(?:\.\.\d{4}-\d{2})?", r"\d{2}/\d{4}",
        r"(?:Tabela|Figura|seção|seções|Seção|doc|docs|auditoria|auditorias|protocolo|Protocolo|Parte)\s+\d+"
        r"(?:\s*(?:e|a|–)\s*\d+)*", r"§§?\s*\d+(?:\s*[–-]\s*§?\d+)*", r"^\s*\d+\.\s", r"\s\d+\.\s(?=[A-Z])",
    ]
    for pad in padroes:
        s = re.sub(pad, " ", s, flags=re.M)
    return s


def tokens_html(s: str) -> list[str]:
    return [_canon_pt(m.group(1)) for m in PT.finditer(s)]


# ---------------------------------------------------------------------------


class TestRelatorioParteII(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not HTML.exists():
            raise unittest.SkipTest("relatório ainda não gerado")
        cls.html = HTML.read_text(encoding="utf-8")
        cls.secoes = secoes_mo(cls.html)

    def test_secoes_presentes_e_em_ordem(self) -> None:
        titulos = [
            "Resumo em 1 página", "Resumo da rodada multi-outcome", "1. A regra", "2. RDD sharp com o escore completo",
            "3. Inferência alternativa", "4. Antes do escore completo", "5. Leitura e limites",
            "Parte II — rodada multi-outcome", "6. Protocolo 40", "7. Políticas nos mesmos cortes", "8. E6 — funil",
            "9. E9 — escolha revelada", "10. E7 — diferença em descontinuidades", "11. A4 reestimado",
            "12. Síntese (E8)", "Apêndice A", "Apêndice B",
        ]
        pos = []
        for t in titulos:
            i = self.html.find(t, (pos[-1] + 1) if pos else 0)
            self.assertGreaterEqual(i, 0, f"seção ausente ou fora de ordem: {t}")
            pos.append(i)
        self.assertEqual(len(self.secoes), 8, "seções da parte II (resumo + 6 a 12)")

    def test_hipoteses_primarias_primeiro(self) -> None:
        resumo = next(s for s in self.secoes if "Resumo da rodada multi-outcome" in s)
        i1, i2, isec = resumo.find("<strong>P1</strong>"), resumo.find("<strong>P2</strong>"), resumo.find("Secundária")
        self.assertTrue(0 <= i1 < i2 < isec, "ordem P1 → P2 → secundária no resumo da rodada")
        e6 = next(s for s in self.secoes if "8. E6" in s)
        self.assertLess(e6.find("Hipótese primária P1"), e6.find("Seleção e diagnósticos"))
        self.assertLess(e6.find("Seleção e diagnósticos"), e6.find("<h3>Componentes</h3>"))
        e7 = next(s for s in self.secoes if "10. E7" in s)
        self.assertLess(e7.find("Hipótese primária P2"), e7.find("<h3>Família F3</h3>"))

    def test_como_ler_antes_de_cada_tabela(self) -> None:
        n = 0
        for s in self.secoes:
            if 'id="sintese-e8"' in s:
                continue  # tabelas da síntese vêm do JSON do E8; a caixa "Como ler" fica no topo da seção
            for bloco in re.findall(r'<div class="bloco-tab[^"]*">(.*?)</table>', s, re.S):
                n += 1
                i_leg, i_tab = bloco.find('class="legenda-salto"><strong>Como ler.</strong>'), bloco.find("<table")
                self.assertTrue(0 <= i_leg < i_tab, "tabela sem caixa “Como ler” antes: " + bloco[:120])
        self.assertGreaterEqual(n, 20)

    def test_como_ler_define_o_salto_e_o_contraste(self) -> None:
        tudo = "".join(self.secoes)
        self.assertIn("lado com bolsa maior (IVS acima do corte) − lado com bolsa menor", tudo)
        self.assertIn("RDD em nível = pacote do corte", tudo)
        self.assertIn("Salto da DiRD = salto de ΔY", tudo)

    def test_numeros_rastreaveis_as_saidas(self) -> None:
        fontes = valores_das_fontes(list(R.FONTES_RODADA_MO))
        sem_fonte = {}
        for s in self.secoes:
            for t in tokens_html(texto_numerico(s)):
                if t not in fontes and t not in PERMITIDOS:
                    sem_fonte[t] = sem_fonte.get(t, 0) + 1
        self.assertEqual(sem_fonte, {}, "números da parte II sem origem nas saídas lidas")

    def test_numeros_chave_batem_com_as_saidas(self) -> None:
        tudo = "".join(self.secoes)
        p1 = json.loads(R.E6_RES.read_text(encoding="utf-8"))["p1_para_holm"]
        p2 = json.loads(R.E7_RES.read_text(encoding="utf-8"))["p2_para_holm"]
        self.assertIn(R.sinal(p1["tau"], 2) + " DP", tudo)
        self.assertIn(f"[{R.sinal(p1['ic95_inf'], 2)}; {R.sinal(p1['ic95_sup'], 2)}]", tudo)
        self.assertIn(R.br_p(p1["p_valor"]), tudo)
        self.assertIn(R.sinal(p2["tau"], 3), tudo)
        self.assertIn(f"[{R.sinal(p2['ic95_inf'], 3)}; {R.sinal(p2['ic95_sup'], 3)}]", tudo)
        e9 = pd.read_csv(R.E9_EST, dtype={"ciclo": str})
        for c in ("1", "2", "3", "empilhado"):
            r = e9[(e9["ciclo"] == c) & (e9["especificacao"] == "spline_linear__bolsa_linear")
                   & (e9["termo"] == "bolsa_mil") & (e9["modelo"] == "logit_condicional_1a_opcao")
                   & (e9["conjunto"] == "principal")].iloc[0]
            self.assertIn(f"<strong>{R.br(r['coef'], 4)}</strong>", tudo, c)

    def test_figuras_sao_pngs_do_pipeline(self) -> None:
        do_pipeline = {_sha(p) for p in (ROOT / "output" / "rdd_bolsa").glob("E*_figuras/*.png")}
        imgs = re.findall(r'<img[^>]*src="data:image/png;base64,([^"]+)"', self.html)
        self.assertGreaterEqual(len(imgs), 10)
        for b in imgs:
            self.assertIn(hashlib.sha256(base64.b64decode(b)).hexdigest(), do_pipeline,
                          "imagem incorporada que não é PNG gravado pelo pipeline")
        self.assertEqual(len(re.findall(r"<img", self.html)), len(imgs), "imagem fora de data URI PNG")

    def test_html_em_dia_com_as_saidas(self) -> None:
        for p in list(R.FONTES_RODADA_MO) + [f for figs in R.FIGURAS_MO.values() for f in figs]:
            if p.exists():
                self.assertIn(_sha(p)[:12], self.html, f"{p.relative_to(ROOT)} mudou depois do relatório")

    def test_failure_mode_rotulado(self) -> None:
        a4 = next(s for s in self.secoes if "11. A4" in s)
        self.assertIn("FAILURE_MODE", a4)
        self.assertIn("não citável", a4)
        d = pd.read_csv(R.FM_CSV)
        n_a4 = int(d["bloco"].astype(str).str.startswith("A4").sum())
        self.assertEqual(a4.count('<span class="failure">'), n_a4, "todo valor antigo marcado como failure mode")

    def test_leitura_do_e7_igual_ao_gerador(self) -> None:
        e7 = _importar("e7_teste_relatorio", SCRIPT_E7)
        est, ev, _ = e7.ler_saidas()
        t = e7.gerar_leitura(est, ev)
        blocos = re.findall(r'<p class="gerado" data-gerador="[^"]+" data-chave="(\w+)">(.*?)</p>', self.html, re.S)
        self.assertGreaterEqual(len(blocos), 3)
        for k, v in blocos:
            self.assertEqual(html.unescape(v), t[k], k)

    def test_sintese_e8_coerente_com_o_arquivo(self) -> None:
        e8 = next(s for s in self.secoes if 'id="sintese-e8"' in s)
        if R.E8_RES.exists():
            self.assertNotIn(">pendente<", e8)
            self.assertIn(_sha(R.E8_RES)[:12], e8)
        else:
            self.assertIn(">pendente<", e8)
            self.assertNotIn("<table", e8)

    def test_dependencia_da_conferencia_do_sinal_mantida(self) -> None:
        fonte = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('conf.get("status") != "CONFERIDO"', fonte)
        self.assertIn("09b_conferir_sinal.py antes do relatorio", fonte)


class TestSinteseE8Sintetico(unittest.TestCase):
    """Dado SINTÉTICO: um E8_resumo.json inventado em pasta temporária, só para a renderização."""

    CTX = {"valor_faixa": {"baixa": 10000.0, "media": 15000.0, "alta": 20000.0}, "faixas": ["baixa", "media", "alta"],
           "cortes": [0.3, 0.4]}

    def test_sem_arquivo_fica_pendente(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            h = R.secao_sintese_e8(self.CTX, Path(d) / "E8_resumo.json")
        self.assertIn(">pendente<", h)
        self.assertNotIn("<table", h)
        self.assertNotIn("Holm =", h)

    def test_com_arquivo_renderiza_o_que_le(self) -> None:
        sintetico = {"natureza_dos_dados": "SINTETICO_DE_TESTE", "holm": [{"hipotese": "P1", "p_ajustado": 0.123456}],
                     "nota": "texto sintético"}
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "E8_resumo.json"
            p.write_text(json.dumps(sintetico), encoding="utf-8")
            h = R.secao_sintese_e8(self.CTX, p)
        self.assertNotIn(">pendente<", h)
        self.assertIn("0,123456", h)
        self.assertIn("texto sintético", h)
        self.assertIn("SINTETICO_DE_TESTE", h)


if __name__ == "__main__":
    unittest.main()
