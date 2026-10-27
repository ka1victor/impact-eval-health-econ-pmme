"""Testes da síntese da H2: `scripts/rdd_bolsa/51_sintese_H2.py` e `docs/06_execucao/66_analise_completa_H2.md`.

Partes:

1. `TestEsquema`: colunas, `EMPIRICO`, estatuto, ids únicos, hashes das saídas e das entradas, figuras com "Como ler"
   de no máximo duas linhas e fonte.
2. `TestReproducao`: cada número copiado de uma saída auditada (`VL_`, `VC_`, `VD_`, `E9_`, `P1h_`, `G1_`, `P1_`,
   `numeros_banca2.json`) é relido da origem pelo filtro gravado e bate a ≤ 1e−8; cada descritivo novo é recalculado
   das bases de escolha e bate a ≤ 1e−8; os `ESC_*` da banca 2 batem com a base desta análise.
3. `TestIntegridade`: nenhum arquivo de IVS errado é aberto ou citado; o script só grava nos seus alvos; as saídas de
   origem não foram regravadas.
4. `TestDoc66`: o doc é igual ao regerado das saídas; nenhum número de resultado fora dos blocos; estrutura,
   linguagem e as frases qualitativas do texto conferidas contra o CSV.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import re
import sys
import textwrap
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "51_sintese_H2.py"
_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location("sintese_H2_51", SCRIPT)
M = importlib.util.module_from_spec(_spec)
sys.modules["sintese_H2_51"] = M
_spec.loader.exec_module(M)
sys.dont_write_bytecode = _bytecode

CSV = M.OUT_CSV
RESUMO = M.OUT_RESUMO
DOC = M.DOC
TOL = 1e-8
IVS_ERRADO = "ivs_ipea_2010_municipios"

_ABERTOS: list[str] = []
_GRAVAR = [False]


def _hook(evento, args):
    if _GRAVAR[0] and evento == "open" and args and isinstance(args[0], (str, Path)):
        _ABERTOS.append(str(args[0]))


sys.addaudithook(_hook)


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def dif(a: float, b: float) -> float:
    """Absoluta até 1, relativa acima (o CSV grava 10 algarismos significativos); NaN só com NaN."""
    if math.isnan(a) or math.isnan(b):
        assert math.isnan(a) and math.isnan(b), f"NaN em só um lado: {a} × {b}"
        return 0.0
    return abs(a - b) / max(1.0, abs(b))


def ler() -> pd.DataFrame:
    return M.ler_sintese()


# ---------------------------------------------------------------------------
# 1. Esquema
# ---------------------------------------------------------------------------

class TestEsquema(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.df = ler()
        cls.resumo = json.loads(RESUMO.read_text(encoding="utf-8"))

    def test_colunas_natureza_estatuto(self) -> None:
        self.assertEqual(list(self.df.columns), M.COLUNAS)
        self.assertTrue((self.df["natureza_dos_dados"] == "EMPIRICO").all())
        self.assertTrue((self.df["estatuto"] == "SINTESE_H2_POS_RESULTADO").all())
        self.assertFalse(self.df["id"].duplicated().any())
        self.assertEqual(set(self.df["origem_numero"]), {"SAIDA_AUDITADA", "DESCRITIVO_NOVO"})
        self.assertEqual(self.resumo["natureza_dos_dados"], "EMPIRICO")
        self.assertEqual(self.resumo["estatuto"], "SINTESE_H2_POS_RESULTADO")
        self.assertTrue(self.resumo["nao_reestima"])
        self.assertEqual(self.resumo["n_linhas"], len(self.df))
        corpo = CSV.read_text(encoding="utf-8").upper()
        for proibido in ("SINTETICO", "CENARIO_CONTRAFACTUAL", "SIMULA", "IMPUT"):
            self.assertNotIn(proibido, corpo)

    def test_estimativa_preenchida_e_ic_ordenado(self) -> None:
        self.assertFalse(self.df["estimativa"].isna().any())
        com_ic = self.df.dropna(subset=["ic95_inf", "ic95_sup"])
        self.assertTrue((com_ic["ic95_inf"] <= com_ic["estimativa"] + 1e-12).all())
        self.assertTrue((com_ic["estimativa"] <= com_ic["ic95_sup"] + 1e-12).all())

    def test_saidas_com_hash_do_resumo(self) -> None:
        for caminho, h in self.resumo["saidas"].items():
            self.assertEqual(sha256(ROOT / caminho), h, caminho)
        self.assertIn(M.rel(CSV), self.resumo["saidas"])

    def test_entradas_registradas(self) -> None:
        for e in self.resumo["entradas"]:
            for campo in ("caminho", "papel", "data_referencia", "cobertura", "unidade", "chaves", "filtros", "sha256"):
                self.assertTrue(e[campo], (e["caminho"], campo))
            if e["conferencia"] == "sha256":
                self.assertEqual(sha256(ROOT / e["caminho"]), e["sha256"], e["caminho"])
            else:  # numeros_banca2.json: outro script o reconstrói; os valores são conferidos em TestReproducao
                self.assertEqual(e["caminho"], "output/apresentacao_banca2/numeros_banca2.json")

    def test_figuras_f1_a_f6_com_como_ler_e_fonte(self) -> None:
        fig = self.resumo["figuras"]
        self.assertEqual(sorted(fig), [f"F{i}" for i in range(1, 7)])
        for k, f in fig.items():
            self.assertTrue((ROOT / f["arquivo"]).exists(), k)
            self.assertTrue(f["arquivo"].startswith("output/rdd_bolsa/H2_figuras/H2_"), k)
            self.assertLessEqual(len(textwrap.wrap("Como ler: " + f["como_ler"], 135)), 2, k)
            self.assertTrue(f["fonte"].startswith("Fonte:"), k)
            self.assertTrue(f["titulo"], k)


# ---------------------------------------------------------------------------
# 2. Reprodução a partir das saídas de origem
# ---------------------------------------------------------------------------

class TestReproducao(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.df = ler()

    def test_numeros_copiados_batem_com_a_origem(self) -> None:
        cache: dict[str, pd.DataFrame] = {}
        aud = self.df[self.df["origem_numero"] == "SAIDA_AUDITADA"]
        self.assertGreater(len(aud), 50)
        prefixos = set()
        for _, r in aud.iterrows():
            arq = ROOT / r["fonte_arquivo"]
            prefixos.add(arq.name.split("_")[0])
            filtro = json.loads(r["fonte_filtro"])
            if arq.suffix == ".json":
                obj = json.loads(arq.read_text(encoding="utf-8"))
                for k in filtro["caminho"]:
                    obj = obj[k]
                self.assertLessEqual(dif(r["estimativa"], float(obj)), TOL, r["id"])
                continue
            if r["fonte_arquivo"] not in cache:
                cache[r["fonte_arquivo"]] = pd.read_csv(arq, dtype={"ciclo": str})
            src = cache[r["fonte_arquivo"]]
            m = pd.Series(True, index=src.index)
            for k, v in filtro.items():
                m &= src[k].astype(str) == str(v)
            self.assertEqual(int(m.sum()), 1, r["id"])
            linha = src[m].iloc[0]
            self.assertEqual(linha["natureza_dos_dados"], "EMPIRICO", r["id"])
            cols = json.loads(r["fonte_colunas"])

            def t(col, aplica=True):
                if not col:
                    return float("nan")
                x = float(linha[col])
                if not aplica or math.isnan(x):
                    return x
                return {"identidade": x, "exp5": math.exp(5 * x) if abs(x) < 50 else float("inf"),
                        "vezes10": 10 * x}[r["transformacao"]]

            self.assertLessEqual(dif(r["estimativa"], t(cols["est"])), TOL, r["id"])
            self.assertLessEqual(dif(r["ic95_inf"], t(cols["inf"])), TOL, r["id"])
            self.assertLessEqual(dif(r["ic95_sup"], t(cols["sup"])), TOL, r["id"])
            self.assertLessEqual(dif(r["p"], t(cols["p"], False)), TOL, r["id"])
            self.assertLessEqual(dif(r["p_ajustado"], t(cols["padj"], False)), TOL, r["id"])
            self.assertLessEqual(dif(r["p_score_rademacher"], t(cols["pscore"], False)), TOL, r["id"])
        # todas as famílias de saída pedidas
        for pre in ("G1", "E9", "P1", "P1h", "VC", "VD", "VL", "numeros"):
            self.assertIn(pre, prefixos)

    def test_descritivos_recalculados(self) -> None:
        linhas, _diag, _base = M.descritivas()
        novo = {l["id"]: l for l in linhas}
        desc = self.df[self.df["origem_numero"] == "DESCRITIVO_NOVO"]
        self.assertEqual(set(desc["id"]), set(novo))
        for _, r in desc.iterrows():
            self.assertLessEqual(dif(r["estimativa"], novo[r["id"]]["estimativa"]), TOL, r["id"])
            self.assertLessEqual(dif(r["n_candidatos"], novo[r["id"]]["n_candidatos"]), TOL, r["id"])
            self.assertEqual(r["doc_origem"], "66 §3")

    def test_esc_da_banca2_igual_a_base_desta_analise(self) -> None:
        N = {r["id"]: r for _, r in self.df.iterrows()}
        num = json.loads((ROOT / "output/apresentacao_banca2/numeros_banca2.json").read_text(encoding="utf-8"))
        for esc, d in (("ESC_N", "D_N_EMP"), ("ESC_UF", "D_UF_EMP"), ("ESC_REG", "D_REG_EMP"),
                       ("ESC_MUN", "D_MUN_EMP"), ("ESC_DIST_P50", "D_P50_EMP"), ("ESC_DIST_P75", "D_P75_EMP")):
            self.assertEqual(num["numeros"][esc]["natureza"], "EMPIRICO")
            self.assertLessEqual(dif(num["numeros"][esc]["valor_bruto"], N[esc]["estimativa"]), TOL, esc)
            self.assertLessEqual(dif(N[esc]["estimativa"], N[d]["estimativa"]), TOL, esc)

    def test_contas_por_ciclo_coerentes(self) -> None:
        N = {r["id"]: r["estimativa"] for _, r in self.df.iterrows()}
        self.assertEqual(N["D_N_C1"] + N["D_N_C2"] + N["D_N_C3"], N["D_N_EMP"])
        self.assertEqual(N["G1_CAND_C1"] + N["G1_CAND_C2"] + N["G1_CAND_C3"], N["G1_CAND_EMP"])
        for k in ("UF", "REG", "MUN", "LADO_DISP", "LADO_ESC"):
            for s in ("EMP", "C1", "C2", "C3"):
                self.assertTrue(0 <= N[f"D_{k}_{s}"] <= 1, (k, s))


# ---------------------------------------------------------------------------
# 3. Integridade
# ---------------------------------------------------------------------------

class TestIntegridade(unittest.TestCase):
    def test_nenhum_arquivo_de_ivs_errado(self) -> None:
        texto = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn(IVS_ERRADO, texto)
        self.assertNotIn("data/ivs", texto)
        resumo = json.loads(RESUMO.read_text(encoding="utf-8"))
        self.assertFalse(any(IVS_ERRADO in e["caminho"] for e in resumo["entradas"]))
        self.assertIn("output/aquisicao/a08_ivs_2010_oficial_municipio.csv", [e["caminho"] for e in resumo["entradas"]])
        _ABERTOS.clear()
        _GRAVAR[0] = True
        try:
            M.linhas_auditadas()
            M.descritivas()
        finally:
            _GRAVAR[0] = False
        self.assertTrue(_ABERTOS)
        self.assertFalse([a for a in _ABERTOS if IVS_ERRADO in a])
        self.assertTrue(any("a08_ivs_2010_oficial_municipio.csv" in a for a in _ABERTOS))
        self.assertFalse([a for a in _ABERTOS if "/data/" in a.replace("\\", "/")])

    def test_so_grava_nos_alvos(self) -> None:
        texto = SCRIPT.read_text(encoding="utf-8")
        self.assertEqual(texto.count(".write_text("), 1)
        self.assertEqual(texto.count(".savefig("), 1)
        for proibido in (".to_csv(OUT", ".to_csv(ROOT", ".to_parquet(", "open(", "json.dump("):
            self.assertNotIn(proibido, texto.replace("pd.read_parquet(", "").replace("with open(p, \"rb\")", ""))
        for alvo in ("VL_estimativas.csv", "VC_estimativas.csv", "P1h_magnitudes.csv", "G1_resumo.json",
                     "numeros_banca2.json"):
            with self.assertRaises(AssertionError):
                M.gravar_texto(M.OUT / alvo, "")
        with self.assertRaises(AssertionError):
            M.gravar_texto(ROOT / "output" / "apresentacao_banca2" / "numeros_banca2.json", "")

    def test_saidas_de_origem_nao_regravadas(self) -> None:
        resumo = json.loads(RESUMO.read_text(encoding="utf-8"))
        saidas = set(resumo["saidas"])
        for e in resumo["entradas"]:
            self.assertNotIn(e["caminho"], saidas)
            if e["conferencia"] == "sha256":
                self.assertEqual(sha256(ROOT / e["caminho"]), e["sha256"], e["caminho"])
        for s in saidas:
            self.assertTrue(Path(s).name.startswith("H2_"), s)

    def test_sem_identificadores_pessoais(self) -> None:
        corpo = CSV.read_text(encoding="utf-8").lower()
        for padrao in ("cpf\"", "c1_0", "c2_0", "c3_0", "id_candidato,"):
            self.assertNotIn(padrao, corpo)
        self.assertNotIn("\"id_candidato\":", RESUMO.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# 4. Doc 66
# ---------------------------------------------------------------------------

CORTES_PERMITIDOS = {"0,300", "0,400", "0,050"}
SECOES = ["## 0. Resposta curta", "## 1. A hipótese e por que ela importa para a política", "## 2. Dados e amostra",
          "## 3. Descritiva", "## 4. Método em palavras", "## 5. Identificação", "## 6. Resultados principais",
          "## 7. Robustez", "## 8. Ameaças e respostas", "## 9. O que dá e o que não dá para afirmar",
          "## 10. Leitura pela teoria"]


class TestDoc66(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.texto = DOC.read_text(encoding="utf-8")
        cls.df = ler()
        cls.N = {r["id"]: r for _, r in cls.df.iterrows()}

    def test_doc_igual_ao_regerado_das_saidas(self) -> None:
        resumo = json.loads(RESUMO.read_text(encoding="utf-8"))
        self.assertEqual(self.texto, M.atualizar_texto(self.texto, M.blocos(self.df, resumo)))

    def test_marcadores_e_secoes(self) -> None:
        for nome in M.NOMES_BLOCOS:
            self.assertEqual(self.texto.count(f"<!-- H2:{nome}:inicio -->"), 1, nome)
            self.assertEqual(self.texto.count(f"<!-- H2:{nome}:fim -->"), 1, nome)
        pos = [self.texto.index(s) for s in SECOES]
        self.assertEqual(pos, sorted(pos))
        for k in ("F1", "F2", "F3", "F4", "F5", "F6"):
            self.assertIn(f"H2_{k}_", self.texto)
        self.assertGreaterEqual(self.texto.count("**Como ler.**"), 6)

    def test_nenhum_numero_de_resultado_fora_dos_blocos(self) -> None:
        fora = re.sub(r"<!-- H2:(\w+):inicio -->.*?<!-- H2:\1:fim -->", "", self.texto, flags=re.S)
        fora = "\n".join(x for x in fora.splitlines() if not x.startswith("#"))
        fora = re.sub(r"§\s?\d+(\.\d+)*", "", fora)
        self.assertEqual([d for d in re.findall(r"\d+,\d+", fora) if d not in CORTES_PERMITIDOS], [])
        self.assertEqual(re.findall(r"\d+\.\d+", fora), [])
        self.assertEqual(re.findall(r"\d+\s?%", fora), [])
        self.assertEqual(re.findall(r"\d+\s?km", fora), [])

    def test_numeros_dos_blocos_vem_do_csv(self) -> None:
        """Cada decimal dos blocos de resultado é a formatação de algum número do CSV (ou de 10·β, D_UF etc. já nele)."""
        fmt = set()
        for _, r in self.df.iterrows():
            for c in ("estimativa", "ic95_inf", "ic95_sup", "p", "p_ajustado", "p_score_rademacher"):
                v = r[c]
                if isinstance(v, float) and not math.isnan(v):
                    for f in (M.f2, M.f3, M.f0, lambda x: M._br(x, 4), M.fp):
                        fmt.add(f(v))
                    if r["quantidade"] == "fracao":
                        fmt.add(M.pct(v)[:-1])
                        fmt.add(M.pct1(v)[:-1])
                    if c == "estimativa" and r["quantidade"] == "bolsa_mil":
                        fmt.add(M.f2(v))
        for nome in ("resposta", "resultados", "robustez", "descritiva"):
            bloco = re.search(rf"<!-- H2:{nome}:inicio -->(.*?)<!-- H2:{nome}:fim -->", self.texto, re.S).group(1)
            bloco = re.sub(r"\(\.\./\.\./[^)]*\)", "", bloco)  # caminhos das figuras
            bloco = re.sub(r"!\[[^\]]*\]", "", bloco)
            bloco = re.sub(r"§\s?\d+(\.\d+)*", "", bloco)
            for d in re.findall(r"−?\d+,\d+", bloco):
                if d in CORTES_PERMITIDOS:
                    continue
                self.assertIn(d, fmt, (nome, d))

    def test_linguagem(self) -> None:
        t = " ".join(self.texto.split())
        for exigido in ("pacote do corte", "preferência revelada", "pós-resultado", "não detectamos aumento",
                        "interpretação", "condicional a se candidatar", "vínculo anterior no CNES",
                        "não passa no Holm", "inconclusivo", "teste central"):
            self.assertIn(exigido.lower(), t.lower(), exigido)
        for proibido in ("não encheu", "não aumenta quantas", "a bolsa funciona", "a bolsa não funciona",
                         "efeito causal da origem", "não traz médico de longe", "não quantas"):
            self.assertNotIn(proibido, t.lower(), proibido)
        self.assertIn("**cenário contrafactual, não observação**", t)

    def test_correcoes_da_auditoria_52(self) -> None:
        """Cabeçalho aponta para a auditoria 52; o VL-1 não é descrito como 'só vagas da UF de origem'; a linha
        principal da bolsa é a pré-registrada (M1), não o adendo pós-resultado; títulos cabem numa linha."""
        cab = self.texto.split("## 0.")[0]
        self.assertIn("../auditorias/52_auditoria_analise_H2.md", cab)
        self.assertNotIn("auditoria 52 em curso", cab)
        self.assertTrue((ROOT / "docs/auditorias/52_auditoria_analise_H2.md").exists())
        t = " ".join(self.texto.split()).lower()
        for proibido in ("só vagas da uf de origem", "dentro da uf de origem, a bolsa maior", "a bolsa aparece"):
            self.assertNotIn(proibido, t, proibido)
        principais = set(self.df.loc[self.df["principal"].astype(str) == "True", "id"])
        self.assertEqual(principais, {"OR_M1_EMP", "DUF_M1"})
        fig = json.loads(RESUMO.read_text(encoding="utf-8"))["figuras"]
        self.assertIn("Descritivo", fig["F2"]["titulo"])
        self.assertIn("pré-registrada", fig["F6"]["como_ler"])

    def test_frases_qualitativas_conferem_com_o_csv(self) -> None:
        N = self.N
        e = lambda k: N[k]["estimativa"]  # noqa: E731
        # §3: perto do corte, o lado de bolsa maior é mais escolhido do que oferecido, nos dois cortes e nos três ciclos
        for s in ("EMP", "C1", "C2", "C3", "K300", "K400"):
            self.assertGreater(e(f"D_LADO_ESC_{s}"), e(f"D_LADO_DISP_{s}"), s)
        dif_c = {s: e(f"D_LADO_ESC_{s}") - e(f"D_LADO_DISP_{s}") for s in ("C1", "C2", "C3")}
        self.assertEqual(max(dif_c, key=dif_c.get), "C2")
        # §3: o ciclo 1 é o mais disperso
        self.assertEqual(min(("C1", "C2", "C3"), key=lambda s: e(f"D_UF_{s}")), "C1")
        # §6.1 e §7: D_UF > 0 em todas as variantes; 10·β sup < θ_UF inf
        for k in M.ROBUSTEZ_DUF:
            self.assertGreater(N[k]["ic95_inf"], 0, k)
        self.assertLess(N["BOLSA10_M1"]["ic95_sup"], N["THETA_UF_M1"]["ic95_inf"])
        self.assertLess(N["BOLSA10_VL1_EMP"]["ic95_sup"], N["THETA_UF_M1"]["ic95_inf"])
        # §6.2: o β pré-registrado não passa no Holm
        self.assertGreater(N["BETA_M1_EMP"]["p_ajustado"], 0.05)
        # §6.3: VL-1 passa no Holm e a diferença pareada dos ciclos 1–3 exclui zero (maior que no M1)
        for k in ("OR_VL1_EMP", "OR_VL1_C2"):
            self.assertLess(N[k]["p_ajustado"], 0.05, k)
        self.assertGreater(N["DIF_VL1_EMP"]["ic95_inf"], 0)
        # §6.4: VL-2 inconclusivo
        self.assertLess(N["OR_VL2_EMP"]["ic95_inf"], 1)
        # §6.5: K5 do M1 ≈ duas vezes a mediana da distância, IC com zero; VL-1 menor e IC acima de zero
        self.assertTrue(1.8 < e("K5_M1_EMP") / e("ESC_DIST_P50") < 2.7)
        self.assertLess(N["K5_M1_EMP"]["ic95_inf"], 0)
        self.assertGreater(N["K5_VL1_EMP"]["ic95_inf"], 0)
        self.assertLess(e("K5_VL1_EMP"), e("K5_M1_EMP"))
        # §7: quem cruza 1
        cruza = {k for k in M.ROBUSTEZ_OR if N[k]["ic95_inf"] <= 1}
        self.assertEqual(cruza, {"OR_M1_EMP", "OR_M5_C1", "OR_M5_C3", "OR_M7_EMP", "OR_VL2_EMP", "OR_VL3_VL2_EMP",
                                 "OR_E9CUB_EMP", "OR_E9CUB_C2"})
        # números citados pelo coordenador (auditoria 50): β com p de Holm 0,072; km 119 [−12; 250]; 75 km
        self.assertEqual(M.fp(N["BETA_M1_EMP"]["p_ajustado"]), "0,072")
        self.assertEqual((M.f0(e("K5_M1_EMP")), M.f0(N["K5_M1_EMP"]["ic95_inf"]), M.f0(N["K5_M1_EMP"]["ic95_sup"])),
                         ("119", "−12", "250"))
        self.assertEqual(M.f0(e("K5_VL1_EMP")), "75")
        self.assertEqual(M.pct(e("ESC_UF")), "79%")


if __name__ == "__main__":
    unittest.main()
