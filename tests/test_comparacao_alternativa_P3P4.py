"""Testes do protocolo 59, parte B (script 35) e das saídas H_/CA_ (scripts 34 e 35).

Os testes de função usam dados SINTÉTICOS construídos em memória (rotulados aqui; nada vai para `output/`). Os
testes de saída conferem esquema, rótulos, privacidade, Holm e coerência com o protocolo, e são pulados se as saídas
ainda não existirem.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "rdd_bolsa"


def _mod(nome: str, arquivo: str):
    if nome in sys.modules:
        return sys.modules[nome]
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location(nome, ROOT / "scripts" / "rdd_bolsa" / arquivo)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    return mod


CA = _mod("ca35_teste", "35_comparacao_alternativa_P3P4.py")


class TestEstimadorP4CA(unittest.TestCase):
    def test_efeito_constante_exato(self):
        # SINTÉTICO: ΔY = 2 D + efeito de célula, sem ruído -> θ = 2 em todo e, EP 0
        cel = np.array(["a"] * 4 + ["b"] * 4)
        D = np.array([1, 0, 0, 1, 1, 0, 0, 0])
        dY = np.column_stack([2.0 * D + np.where(cel == "a", 5.0, -3.0)] * 3)
        r = CA.did_celula(dY, D, cel)
        np.testing.assert_allclose(r["theta"], 2.0, atol=1e-12)
        np.testing.assert_allclose(CA.cov_cluster(r["IFg"]), 0.0, atol=1e-20)

    def test_igual_ao_r1_do_p6(self):
        # SINTÉTICO: uma coluna de ΔY; mesma estimativa e mesmo EP CR1 do R1 (script 31)
        R1 = _mod("r31_teste", "31_rd_mecanismo.py")
        rng = np.random.default_rng(5)
        cel = np.repeat([f"c{i}" for i in range(12)], 6)
        D = np.tile([1, 1, 0, 0, 0, 0], 12)
        y = 1.5 * D + rng.normal(size=cel.size) + np.repeat(rng.normal(size=12), 6)
        r = CA.did_celula(y[:, None], D, cel)
        ref = R1.r1(y, D.astype(float), cel, permutar=False)
        self.assertAlmostEqual(float(r["theta"][0]), ref["estimativa"], places=10)
        self.assertAlmostEqual(float(np.sqrt(CA.cov_cluster(r["IFg"])[0, 0])), ref["ep"], places=10)

    def test_celula_de_um_lado_nao_muda(self):
        # SINTÉTICO: acrescentar célula só com não alocados não muda θ
        rng = np.random.default_rng(2)
        cel = np.repeat(["a", "b", "c"], 5)
        D = np.tile([1, 0, 0, 1, 0], 3)
        y = rng.normal(size=15)
        r1 = CA.did_celula(y[:, None], D, cel)
        cel2 = np.concatenate([cel, ["z"] * 4])
        D2 = np.concatenate([D, [0] * 4])
        y2 = np.concatenate([y, rng.normal(size=4) + 10])
        r2 = CA.did_celula(y2[:, None], D2, cel2)
        self.assertAlmostEqual(float(r1["theta"][0]), float(r2["theta"][0]), places=12)

    def test_permutacao_e_wald(self):
        # SINTÉTICO: sem efeito e pré plano -> p da média e do pré não pequenos; com efeito forte -> p mínimo
        rng = np.random.default_rng(11)
        es = np.arange(-4, 3)
        cel = np.repeat([f"c{i}" for i in range(15)], 6)
        D = np.tile([1, 1, 0, 0, 0, 0], 15)
        dY = rng.normal(size=(cel.size, es.size))
        dY[:, es == -1] = np.nan
        r0 = CA.estimar_p4ca(dY, D, cel, es, b_perm=199)
        self.assertGreater(r0["p_perm_media"], 0.05)
        dY2 = dY + np.where(es >= 0, 3.0, 0.0)[None, :] * D[:, None]
        r1 = CA.estimar_p4ca(dY2, D, cel, es, b_perm=199)
        self.assertLess(r1["p_perm_media"], 0.01)
        self.assertAlmostEqual(r1["p_perm_pre"], r0["p_perm_pre"], places=12)   # pré idêntico

    def test_holm(self):
        p = np.array([0.01, 0.04, 0.03, 0.5])
        np.testing.assert_allclose(CA.holm(p), [0.04, 0.09, 0.09, 0.5])


class TestPainelCandidatos(unittest.TestCase):
    def test_horas_por_local_ausente_e_zero(self):
        # SINTÉTICO: dois candidatos, três meses; hora vazia deixa o mês ausente; mês sem vínculo vale zero
        v = pd.DataFrame({
            "competencia": ["202401", "202401", "202402", "202401"],
            "co_profissional_sus": ["p1", "p1", "p1", "p2"],
            "co_cnes": ["1", "2", "1", "3"], "co_municipio": ["111111", "222222", "111111", "333333"],
            "co_cbo": ["225125"] * 4, "tp_sus_nao_sus": ["S", "N", "S", "S"],
            "qt_ch_ambulatorial": [10, 5, None, 20], "qt_ch_hosp_sus": [0, 0, 4, 0], "qt_ch_outros": [0, 1, 0, 0]})
        cmap = pd.DataFrame({"chave": ["k1", "k2"], "co_profissional_sus": ["p1", "p2"],
                             "co_ibge_1a_opcao": ["111111", "999999"]})
        p = CA.painel_candidatos(v, cmap, ["202401", "202402", "202403"]).set_index(["chave", "competencia"])
        self.assertEqual(p.loc[("k1", "202401"), "horas_totais"], 16)
        self.assertEqual(p.loc[("k1", "202401"), "horas_mun_1a"], 10)
        self.assertEqual(p.loc[("k1", "202401"), "horas_fora_1a"], 6)
        self.assertEqual(p.loc[("k1", "202401"), "horas_sus"], 10)
        self.assertEqual(p.loc[("k1", "202401"), "n_municipios"], 2)
        self.assertTrue(np.isnan(p.loc[("k1", "202402"), "horas_totais"]))
        self.assertEqual(p.loc[("k1", "202402"), "vinculo_mun_1a"], 1)
        self.assertEqual(p.loc[("k1", "202403"), "horas_totais"], 0)
        self.assertEqual(p.loc[("k1", "202403"), "n_vinculos"], 0)
        self.assertEqual(p.loc[("k2", "202401"), "horas_fora_1a"], 20)
        self.assertEqual(p.loc[("k2", "202401"), "vinculo_mun_1a"], 0)

    def test_matriz_evento_por_ciclo(self):
        # SINTÉTICO: o valor do mês t₀ do ciclo cai em e = 0
        comps = list(pd.period_range("2024-06", "2026-08", freq="M").strftime("%Y%m"))
        base = pd.DataFrame({"chave": ["a", "b"], "ciclo": [1, 2]})
        p = pd.DataFrame([{"chave": k, "competencia": c, "horas_totais": float(i)} for k in ("a", "b")
                          for i, c in enumerate(comps)])
        Y = CA.matriz_evento(p, base, "horas_totais", comps)
        j0 = -CA.E4_MIN
        self.assertEqual(Y[0, j0], comps.index(CA.T0[1]))
        self.assertEqual(Y[1, j0], comps.index(CA.T0[2]))
        self.assertEqual(Y[1, -1], comps.index(CA.T0[2]) + CA.E4_MAX)


def _existe(*nomes):
    return all((OUT / n).exists() for n in nomes)


@unittest.skipUnless(_existe("CA_estimativas.csv", "CA_resumo.json"), "saídas do CA ainda não geradas")
class TestSaidasCA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.est = pd.read_csv(OUT / "CA_estimativas.csv")
        cls.ev = pd.read_csv(OUT / "CA_estudo_evento.csv")
        cls.res = json.loads((OUT / "CA_resumo.json").read_text(encoding="utf-8"))

    def test_rotulos_e_privacidade(self):
        for df in (self.est, self.ev):
            self.assertEqual(set(df["natureza_dos_dados"]), {"EMPIRICO"})
            self.assertFalse(any(c.lower() in CA.COLUNAS_PROIBIDAS for c in df.columns))
        txt = (OUT / "CA_estimativas.csv").read_text(encoding="utf-8") + (OUT / "CA_estudo_evento.csv").read_text(
            encoding="utf-8")
        # números longos fora de casas decimais e de notação científica (CPF, CNS, código do profissional)
        self.assertIsNone(re.search(r"g5p_|x1m_|(?<![\d.])\d{11}(?:\d{4})?(?![\d.eE])", txt))

    def test_hashes_do_resumo(self):
        self.assertEqual(CA.verificar(), 0)

    def test_holm_da_familia(self):
        f = self.est[self.est["familia"] == "holm_CA"]
        exec_ = f[f["status"] == "EXECUTADO"]
        self.assertIn(len(exec_), (1, 4))
        np.testing.assert_allclose(exec_["p_holm"].to_numpy(float), CA.holm(exec_["p_valor"].to_numpy(float)))

    def test_p3ca_cursos_sem_controle_fora(self):
        sp = self.res["amostras"]["P3"]["por_especificacao"]["P3-CA"]
        self.assertEqual(sorted(sp["cursos"]), [10, 11, 12, 13, 14])
        self.assertEqual(sorted(int(c) for c in sp["cursos_fora"]), [7, 15, 16])

    def test_p4ca_amostra_do_r1(self):
        am = self.res["amostras"]["P4"]
        if am.get("status") == "NAO_EXECUTADO":
            self.skipTest("P4-CA não executado")
        sp = am["por_especificacao"]["P4-CA"]
        self.assertEqual((sp["alocados"], sp["nao_alocados"], sp["celulas"]), (30, 68, 27))
        self.assertFalse(any(am["conferencia_P6_amostra"].values()))

    def test_janela_e_referencia(self):
        r = self.ev[self.ev["referencia"]]
        self.assertTrue((r["theta"] == 0).all())
        p4 = self.ev[self.ev["pergunta"] == "P4"]
        if len(p4):
            self.assertEqual((int(p4["e"].min()), int(p4["e"].max())), (CA.E4_MIN, CA.E4_MAX))


@unittest.skipUnless(_existe("H_estimativas.csv", "H_resumo.json"), "saídas do H ainda não geradas")
class TestSaidasH(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.H34 = _mod("h34_teste", "34_sensibilidade_honestdid.py")
        cls.tab = pd.read_csv(OUT / "H_estimativas.csv")

    def test_rotulos(self):
        self.assertEqual(set(self.tab["natureza_dos_dados"]), {"EMPIRICO"})
        self.assertEqual(set(self.tab["rotulo"]), {"SENSIBILIDADE"})

    def test_lista_fechada(self):
        ids = set(self.tab["id_linha"])
        for i in ("H-P3-K_esp", "H-P3-K2r", "H-P3-K2r_tot", "H-P3-K1_reg", "H-P3-K2_reg"):
            self.assertIn(i, ids)
        self.assertEqual(sum(i.startswith("H-P4-") for i in ids), 14)

    def test_ic_robusto_contem_conjunto_identificado(self):
        for restr in ("RM", "RM_hibrido", "SD"):
            s = self.tab[(self.tab["restricao"] == restr) & self.tab["id_inf"].notna()]
            self.assertTrue((s["ic_inf"] <= s["id_inf"] + 1e-6).all(), restr)
            self.assertTrue((s["ic_sup"] >= s["id_sup"] - 1e-6).all(), restr)

    def test_conjunto_identificado_cresce_com_mbar(self):
        for (idl, alvo), s in self.tab[self.tab["restricao"] == "RM"].groupby(["id_linha", "alvo"]):
            s = s.sort_values("parametro")
            larg = (s["id_sup"] - s["id_inf"]).to_numpy(float)
            self.assertTrue(np.all(np.diff(larg) >= -1e-8), (idl, alvo))

    def test_ruptura_sd_coerente_com_grade(self):
        # o FLCI é monotônico em M; o condicional de Δ^RM não precisa ser (ver doc 57h, limitações)
        for (idl, alvo), s in self.tab.groupby(["id_linha", "alvo"]):
            br = s[s["restricao"] == "SD_ruptura"]["parametro"].iloc[0]
            g = s[s["restricao"] == "SD"]
            for r in g.itertuples(index=False):
                if r.parametro < br - 0.02:
                    self.assertTrue(r.exclui_zero, (idl, alvo, r.parametro, br))
                if r.parametro > br + 0.02:
                    self.assertFalse(r.exclui_zero, (idl, alvo, r.parametro, br))

    def test_doc_igual_ao_gerado(self):
        self.assertEqual(self.H34.verificar(), 0)


if __name__ == "__main__":
    unittest.main()
