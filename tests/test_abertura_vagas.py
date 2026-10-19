"""Testes do adendo §7 do protocolo 48: `scripts/rdd_bolsa/24_abertura_vagas_selecao.py`.

Duas partes:

1. `TestSintetico`: DADOS SINTÉTICOS gerados em memória (semente fixa), rotulados como sintéticos e nunca
   gravados em `output/` nem em `data/`. Conferem a fórmula dos limites de Lee do §7 (A2), que os limites
   contêm a estimativa pontual (e coincidem com ela quando p = 0), o IC de Imbens–Manski, que o MQP rápido
   do bootstrap reproduz a rdd_lib e que o Lee extensivo daqui reproduz `rdd_lib.limites_lee_rd`.
2. `TestSaidasReais` e `TestDoc49Adendo`: esquema e rótulos de `output/rdd_bolsa/NA_*`, figuras, e os blocos
   NA do doc 49 iguais aos gerados das saídas (nenhum número digitado na prosa do adendo).
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "24_abertura_vagas_selecao.py"
_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location("abertura_vagas_24", SCRIPT)
NA = importlib.util.module_from_spec(_spec)
sys.modules["abertura_vagas_24"] = NA
_spec.loader.exec_module(NA)
sys.dont_write_bytecode = _bytecode
L, T23 = NA.L, NA.T23

OUT = ROOT / "output" / "rdd_bolsa"
EST = OUT / "NA_estimativas.csv"
RESUMO = OUT / "NA_resumo.json"
DOC = ROOT / "docs" / "06_execucao" / "49_resultados_contagem_vagas_preenchidas.md"

NATUREZA_SINTETICA = "SINTETICO_TESTE"   # rótulo dos dados gerados aqui; nunca gravados


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def municipios_sinteticos(semente: int = 7, n: int = 1500, n_ciclos: int = 1) -> pd.DataFrame:
    """SINTÉTICO: abertura com salto no corte e fração preenchida com salto conhecido; zero fora do quadro."""
    rng = np.random.default_rng(semente)
    s = rng.integers(220, 481, n).astype(float)
    t = ((s > 300) & (s <= 350)) | (s > 400)
    linhas = []
    for k in range(1, n_ciclos + 1):
        abre = rng.random(n) < (0.3 + 0.15 * t)
        vagas = np.where(abre, rng.integers(1, 6, n), 0).astype(float)
        frac = np.clip(0.5 + 0.1 * t + rng.normal(0, 0.2, n), 0, 1)
        preench = np.where(abre, np.round(frac * vagas), 0.0)
        pop = rng.integers(3000, 60000, n).astype(float)
        linhas.append(pd.DataFrame({
            "co_ibge": [f"9{i:05d}" for i in range(n)], "s_mil": s, "ciclo": k, "natureza_dos_dados": NATUREZA_SINTETICA,
            "ofert": vagas, "preench_lim": preench, "tem_celula": abre.astype(float), "pop": pop,
            "frac_lim": np.where(abre, preench / np.where(abre, vagas, 1.0), np.nan),
            "ofert_10k": vagas / pop * 1e4}))
    return pd.concat(linhas, ignore_index=True)


class TestSintetico(unittest.TestCase):
    """Fórmulas e estimadores em dados sintéticos (nada é gravado)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.d = municipios_sinteticos()
        cls.mapa = {c: i for i, c in enumerate(sorted(cls.d["co_ibge"].unique()))}

    def test_dados_rotulados_como_sinteticos(self) -> None:
        self.assertEqual(set(self.d["natureza_dos_dados"]), {NATUREZA_SINTETICA})

    def test_formula_dos_limites_binarios(self) -> None:
        # Sintético: f = 0,6 e p = 0,2 -> [0,5; 0,75]; truncamento em 0 e em 1.
        lo, hi = NA.limites_binario(0.6, 0.2)
        self.assertAlmostEqual(lo, 0.5)
        self.assertAlmostEqual(hi, 0.75)
        self.assertEqual(NA.limites_binario(0.1, 0.5), (0.0, 0.2))
        self.assertEqual(NA.limites_binario(0.9, 0.5)[1], 1.0)
        self.assertTrue(all(np.isnan(NA.limites_binario(0.5, 1.0))))

    def test_lee_intensivo_lado_aparado_e_sinal(self) -> None:
        # Sintético: mais vagas acima -> apara acima; salto = acima - abaixo.
        r = NA.lee_intensivo(s0=4.0, s1=5.0, f0=0.5, f1=0.6)
        self.assertEqual(r["lado"], "acima")
        self.assertAlmostEqual(r["p"], 0.2)
        self.assertAlmostEqual(r["inf"], 0.5 - 0.5)
        self.assertAlmostEqual(r["sup"], 0.75 - 0.5)
        # Mais vagas abaixo -> apara abaixo; limites = f1 - [sup, inf] do lado de baixo.
        r = NA.lee_intensivo(s0=5.0, s1=4.0, f0=0.6, f1=0.5)
        self.assertEqual(r["lado"], "abaixo")
        self.assertAlmostEqual(r["inf"], 0.5 - 0.75)
        self.assertAlmostEqual(r["sup"], 0.5 - 0.5)
        self.assertTrue(np.isnan(NA.lee_intensivo(0.0, 1.0, 0.5, 0.5)["inf"]))

    def test_limites_contem_a_estimativa_e_coincidem_com_p_zero(self) -> None:
        rng = np.random.default_rng(3)
        for _ in range(500):
            s0, s1 = rng.uniform(0.5, 5, 2)
            f0, f1 = rng.uniform(0, 1, 2)
            r = NA.lee_intensivo(s0, s1, f0, f1)
            self.assertLessEqual(r["inf"], f1 - f0 + 1e-12)
            self.assertGreaterEqual(r["sup"], f1 - f0 - 1e-12)
        r = NA.lee_intensivo(3.0, 3.0, 0.4, 0.55)
        self.assertEqual(r["p"], 0.0)
        self.assertAlmostEqual(r["inf"], 0.15)
        self.assertAlmostEqual(r["sup"], 0.15)

    def test_imbens_manski(self) -> None:
        # Intervalo degenerado: c = 1,96; intervalo largo: c -> 1,645.
        lo, hi = NA.ic_imbens_manski(0.0, 0.0, 1.0, 1.0)
        self.assertAlmostEqual(hi, L.Z_975, places=6)
        lo, hi = NA.ic_imbens_manski(0.0, 100.0, 1.0, 1.0)
        self.assertAlmostEqual(-lo, 1.6448536, places=5)
        self.assertTrue(np.isnan(NA.ic_imbens_manski(0.0, 1.0, np.nan, 1.0)[0]))

    def _amostras(self):
        a1 = T23.montar_amostra([(self.d, 300, "300")], empilhada=False)
        a2 = T23.montar_amostra([(self.d, c, str(c)) for c in (300, 400)], empilhada=True)
        return a1, a2

    def test_desenho_rapido_reproduz_rdd_lib(self) -> None:
        for a in self._amostras():
            D = NA.Desenho(a, self.mapa)
            for y, peso in (("ofert_10k", None), ("frac_lim", "ofert")):
                pv = a.col(peso) if peso else None
                ref = T23.ajustar(a, a.col(y), NA.H, peso=pv)
                NA.conferir_desenho(D, a, a.col(y), pv, ref)   # levanta FalhaValidacao se divergir

    def test_multiplicidade_igual_a_duplicar_linhas(self) -> None:
        a = self._amostras()[1]
        D = NA.Desenho(a, self.mapa)
        m = np.zeros(len(self.mapa))
        m[: len(m) // 2] = 2.0
        r = D.ajustar(a.col("ofert_10k"), None, m)
        dup = pd.concat([self.d[self.d["co_ibge"].map(self.mapa) < len(self.mapa) // 2]] * 2, ignore_index=True)
        b = T23.montar_amostra([(dup, c, str(c)) for c in (300, 400)], empilhada=True)
        ref = T23.ajustar(b, b.col("ofert_10k"), NA.H)
        self.assertAlmostEqual(r["tau"], ref["tau"], places=9)

    def test_lee_extensivo_igual_rdd_lib(self) -> None:
        a = self._amostras()[0]
        D = NA.Desenho(a, self.mapa)
        meu = NA.lee_extensivo_desenho(D, D.janela(a.col("tem_celula")), D.janela(a.col("frac_lim")), None)
        ref = L.limites_lee_rd(a.s, a.col("frac_lim"), a.col("tem_celula"), 300, NA.H)
        for x, z in ((meu["inf"], ref["tau_inf"]), (meu["sup"], ref["tau_sup"]), (meu["q"], ref["q_aparo"]),
                     (meu["ingenuo"], ref["tau_selecionados"])):
            self.assertAlmostEqual(x, z, places=9)
        self.assertLessEqual(meu["inf"], meu["ingenuo"])
        self.assertGreaterEqual(meu["sup"], meu["ingenuo"])

    def test_bootstrap_deterministico(self) -> None:
        a1 = self._amostras()[0]
        D = NA.Desenho(a1, self.mapa)
        e = {"DU": D, "DV": D, "args": {"int": (D.janela(a1.col("ofert_10k")), None, D.janela(a1.col("frac_lim")),
                                                D.janela(a1.col("ofert"))),
                                        "int_pop": (D.janela(a1.col("ofert_10k")), D.janela(a1.col("pop")),
                                                    D.janela(a1.col("frac_lim")), D.janela(a1.col("ofert"))),
                                        "ext": (D.janela(a1.col("tem_celula")), D.janela(a1.col("frac_lim")))}}
        e2 = {k: v for k, v in e.items()}
        NA.bootstrap_a2([e], len(self.mapa), n_boot=5, log=lambda *_: None)
        NA.bootstrap_a2([e2], len(self.mapa), n_boot=5, log=lambda *_: None)
        self.assertEqual(e["boot"]["int"]["inf"], e2["boot"]["int"]["inf"])

    def test_fonte_sem_ivs_errado_e_sem_fillna_zero(self) -> None:
        fonte = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("ivs_ipea_2010_municipios", fonte)
        self.assertNotIn("fillna(0", fonte)
        self.assertIn('("competencia", "<=", COMP_PRE[1])', fonte)


@unittest.skipUnless(EST.exists() and RESUMO.exists(), "saidas do adendo §7 ausentes")
class TestSaidasReais(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.est = pd.read_csv(EST, dtype={"corte": str, "ciclo": str})
        cls.resumo = json.loads(RESUMO.read_text(encoding="utf-8"))

    def test_esquema_e_rotulos(self) -> None:
        self.assertEqual(list(self.est.columns), NA.COLUNAS)
        self.assertTrue((self.est["natureza_dos_dados"] == "EMPIRICO").all())
        self.assertTrue((self.est["estatuto"] == "PROTOCOLO_48_ADENDO_7_POS_RESULTADO").all())
        self.assertTrue((self.est["familia"] == "N_ADENDO_7").all())
        self.assertEqual(self.resumo["natureza_dos_dados"], "EMPIRICO")
        self.assertEqual(self.resumo["estatuto"], "PROTOCOLO_48_ADENDO_7_POS_RESULTADO")
        self.assertTrue(set(self.est["status"]) <= {"EXECUTADO", "SEM_ESTIMATIVA", "NAO_EXECUTADO"})
        self.assertFalse(self.est["entra_holm"].astype(bool).any())

    def test_nan_sempre_com_nota(self) -> None:
        nucleo = ["tau", "ep", "ic95_inf", "ic95_sup", "p_valor"]
        ruins = self.est[self.est[nucleo].isna().any(axis=1) & (self.est["nota"].fillna("") == "")]
        self.assertEqual(len(ruins), 0)

    def test_quatro_analises_e_grade_completa(self) -> None:
        self.assertEqual(set(self.est["especificacao"]), {"A1", "A2", "A3", "A4"})
        a2 = self.est[self.est["especificacao"] == "A2"]
        self.assertEqual(len(a2), 12 * 3)
        a1 = self.est[(self.est["especificacao"] == "A1") & (self.est["variante"] == "principal")]
        self.assertTrue((a1["populacao"] == "U").all())
        self.assertEqual(len(a1), 12 * 3)

    def test_lee_contem_salto_ingenuo_e_formula_nas_saidas(self) -> None:
        a2 = self.est[(self.est["especificacao"] == "A2") & self.est["lee_limite_inf"].notna()]
        self.assertTrue(len(a2) > 0)
        it = a2[a2["outcome_id"] == "A2_INTENSIVA"]
        # Margem intensiva: pela fórmula do §7, os limites sempre contêm o salto ingênuo.
        self.assertTrue((it["lee_limite_inf"] <= it["tau"] + 1e-9).all())
        self.assertTrue((it["lee_limite_sup"] >= it["tau"] - 1e-9).all())
        # Margem extensiva: com reta local isso não é garantido; quando falha, a linha diz.
        ex = a2[a2["outcome_id"] == "A2_EXTENSIVA"]
        fora = ex[(ex["lee_limite_inf"] > ex["tau"] + 1e-12) | (ex["lee_limite_sup"] < ex["tau"] - 1e-12)]
        self.assertTrue(fora["nota"].str.contains("salto ingenuo fora dos limites").all())
        self.assertTrue((a2["ic_im_inf"] <= a2["lee_limite_inf"]).all() and (a2["ic_im_sup"] >= a2["lee_limite_sup"]).all())
        for r in it.to_dict("records"):
            x = NA.lee_intensivo(r["taxa_selecao_abaixo"], r["taxa_selecao_acima"], r["taxa_preench_abaixo"],
                                 r["taxa_preench_acima"])
            self.assertAlmostEqual(x["inf"], r["lee_limite_inf"], places=10)
            self.assertAlmostEqual(x["sup"], r["lee_limite_sup"], places=10)
            self.assertAlmostEqual(x["p"], r["lee_p_aparo"], places=10)
        self.assertTrue((a2["n_boot"] >= 999).all())

    def test_lacunas_documentadas_como_nao_executado(self) -> None:
        ne = self.est[self.est["status"] == "NAO_EXECUTADO"]
        self.assertIn("efeito_fixo_tipo_pratica", set(ne["variante"]))
        self.assertIn("covariavel_estabelecimentos_hospitalares", set(ne["variante"]))
        self.assertTrue((ne["nota"].str.len() > 0).all())
        self.assertIn("tipo_de_pratica", self.resumo["atributos_celula"]["ausentes"])

    def test_hashes_das_entradas_conferem(self) -> None:
        for e in self.resumo["entradas"]:
            self.assertEqual(sha256(ROOT / e["caminho"]), e["sha256"], e["caminho"])
        self.assertEqual(sha256(EST), self.resumo["saidas"]["NA_estimativas.csv"]["sha256"])
        self.assertEqual(self.resumo["protocolo"]["sha256"], sha256(ROOT / self.resumo["protocolo"]["arquivo"]))

    def test_cnes_so_pre_programa(self) -> None:
        comps = self.resumo["cnes_pre"]["competencias"]
        self.assertEqual((comps[0], comps[-1]), ("202406", "202506"))

    def test_figuras_existem_e_titulos_batem_com_o_csv(self) -> None:
        figs = self.resumo["saidas"]["figuras"]
        nomes = {Path(f["arquivo"]).name for f in figs}
        self.assertEqual(nomes, {"NA_A1_por_10k_empilhado.png", "NA_A3_celula_preenchida_empilhado.png"})
        for f in figs:
            caminho = ROOT / f["arquivo"]
            self.assertTrue(caminho.exists() and caminho.stat().st_size > 10_000, f["arquivo"])
            self.assertEqual(caminho.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
            for p in f["paineis"]:
                m = np.ones(len(self.est), dtype=bool)
                for k in ("outcome_id", "populacao", "ciclo", "corte", "especificacao", "variante"):
                    m &= self.est[k].astype(str) == str(p[k])
                self.assertEqual(int(m.sum()), 1, p)
                r = self.est[m].iloc[0]
                for c in ("tau", "ic95_inf", "ic95_sup", "p_valor"):
                    self.assertAlmostEqual(float(r[c]), p[c], places=12)

    def test_saidas_da_familia_n_nao_lidas_como_escrita(self) -> None:
        # O script 24 só lê N_estimativas.csv; o hash registrado confere com o arquivo atual.
        lidos = {e["caminho"]: e["sha256"] for e in self.resumo["entradas"]}
        self.assertIn("output/rdd_bolsa/N_estimativas.csv", lidos)


@unittest.skipUnless(DOC.exists() and EST.exists(), "doc 49 ou saidas do adendo ausentes")
class TestDoc49Adendo(unittest.TestCase):
    def test_blocos_iguais_aos_gerados(self) -> None:
        est, resumo = NA.ler_saidas()
        n_est, e9 = NA.ler_auxiliares()
        geradas = NA.gerar_tabelas_doc(est, resumo, n_est, e9)
        no_doc = NA.tabelas_no_doc(DOC.read_text(encoding="utf-8"))
        self.assertEqual(set(no_doc), set(geradas))
        for nome, corpo in no_doc.items():
            self.assertEqual(corpo, geradas[nome], nome)

    def test_prosa_do_adendo_sem_numero_de_resultado(self) -> None:
        texto = DOC.read_text(encoding="utf-8")
        texto = texto[texto.index("## 15. Adendo §7"):]
        texto = NA.MARCA.sub("", texto)
        texto = re.sub(r"`[^`]*`", "", texto)
        texto = re.sub(r"\]\([^)]*\)", "]", texto)
        texto = re.sub(r"(?m)^#+ .*$", "", texto)
        texto = re.sub(r"§+\s?\d+", "", texto)
        texto = re.sub(r"\b(?:docs?|protocolo|seção)\s+\d+", "", texto)
        texto = re.sub(r"\b[A-Za-z_]+\d+[a-z]?\b", "", texto)
        texto = re.sub(r"\d+ª", "", texto)
        decimais = set(re.findall(r"(?<![\w.,])[−+-]?\d+[,.]\d+", texto))
        self.assertEqual(decimais - {"0,050", "0,300", "0,400", "0,010"}, set())
        sem_dec = re.sub(r"(?<![\w.,])[−+-]?\d+[,.]\d+", "", texto)
        inteiros = set(re.findall(r"(?<![\w.,])[−+-]?\d+(?![\w.,]\d)", sem_dec))
        self.assertEqual(inteiros - {"1", "5", "10", "2022"}, set())

    def test_leitura_conjunta_relata_ciclo_1(self) -> None:
        corpo = NA.tabelas_no_doc(DOC.read_text(encoding="utf-8"))["leitura_conjunta"]
        self.assertIn("**Ciclo 1**", corpo)
        self.assertIn("**Todos os ciclos empilhados**", corpo)


if __name__ == "__main__":
    unittest.main()
