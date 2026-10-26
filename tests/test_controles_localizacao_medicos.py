"""Testes do adendo 48d (script 44): H1 e oferta local com controles L e M, e pareamento (PSM principal, §3.2).

- Esquema, `natureza_dos_dados = EMPIRICO` e estatuto em todas as saídas `CL_*`.
- Running variable só o IVS 2010 oficial (a08); o arquivo local de IVS e a malha de regiões (que traz IVS, IDHM e
  renda) não são lidos; nenhuma competência do CNES >= 202609.
- Portões: HI-1 e HI-2 do 48b (contra `HI_estimativas.csv`) e OC-A1 em 0,300 (contra `OC_estimativas.csv`), <= 1e-8.
- Holm (PS-1 e PS-2) e BKY (CL-1, CL-2, CL-3, CL-5 a CL-8) recalculados.
- Doc 57r: cada bloco gerado é idêntico ao que o script gera a partir de `output/`.
- Casos SINTÉTICOS em memória (rotulados "sintético"; nada vai para `output/`): pareamento guloso, inferência
  pareada, resto da região de saúde.
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
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "44_controles_localizacao_medicos.py"
DOC = ROOT / "docs" / "06_execucao" / "57r_resultados_controles_localizacao_medicos.md"
ADENDO = ROOT / "docs" / "06_execucao" / "48d_adendo_controles_localizacao_e_medicos.md"


def _mod(nome: str, caminho: Path):
    if nome in sys.modules:
        return sys.modules[nome]
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    return mod


CL = _mod("cl44_teste", SCRIPT)
L = CL.L
EST, BAL, RES = CL.ler_saidas()


class TestEsquemaENatureza(unittest.TestCase):
    def test_colunas(self):
        self.assertEqual(list(EST.columns), CL.COLUNAS)
        self.assertEqual(list(BAL.columns), CL.COLUNAS_BAL)

    def test_natureza_e_estatuto(self):
        for df in (EST, BAL):
            self.assertEqual(set(df["natureza_dos_dados"]), {"EMPIRICO"})
            self.assertEqual(set(df["estatuto"]), {"ADENDO_48D_POS_RESULTADO"})
        self.assertEqual(RES["natureza_dos_dados"], "EMPIRICO")
        self.assertEqual(RES["estatuto"], "ADENDO_48D_POS_RESULTADO")

    def test_ids_unicos_e_status(self):
        self.assertFalse(EST["id_linha"].duplicated().any())
        self.assertTrue(set(EST["status"]) <= {"EXECUTADO", "SEM_ESTIMATIVA", "PENDENTE_OC"})
        n_pend = int((EST["status"] == "PENDENTE_OC").sum())
        self.assertEqual(n_pend, RES["contagens"]["pendentes_oc"])
        if (OUT / "OC_estimativas.csv").exists():
            self.assertEqual(n_pend, 0, "com OC_* presentes não pode sobrar PENDENTE_OC")

    def test_blocos_do_adendo(self):
        esperados = {"CL-1": 4, "CL-2": 12, "CL-3": 24, "CL-4": 4, "CL-5": 4, "CL-6": 20, "CL-7": 4, "CL-8": 10,
                     "CL-9": 14, "PS-1": 4, "PS-2": 4, "PS-3": 8, "PS-4": 8}
        self.assertEqual(EST["bloco"].value_counts().to_dict(), esperados)
        self.assertEqual(set(BAL.loc[BAL["tipo"] == "salto_no_corte", "bloco"]), {"CL-0"})

    def test_figuras_com_como_ler(self):
        self.assertGreaterEqual(len(RES["figuras"]), 4)
        for f in RES["figuras"]:
            self.assertTrue((ROOT / f["arquivo"]).exists(), f["arquivo"])
            self.assertTrue(f["como_ler"].startswith("Como ler"))


class TestIntegridade(unittest.TestCase):
    def setUp(self):
        self.src = SCRIPT.read_text(encoding="utf-8")

    def test_ivs_oficial(self):
        self.assertNotIn("ivs_ipea_2010_municipios", self.src)
        self.assertNotIn("malha_municipios_regioes_saude", self.src)
        self.assertEqual(CL.A08.name, "a08_ivs_2010_oficial_municipio.csv")
        for x in RES["entradas"]:
            self.assertNotIn("ivs_ipea_2010_municipios", x["arquivo"])
            self.assertNotIn("malha_municipios", x["arquivo"])

    def test_sem_pib_idhm_renda(self):
        for termo in ("idhm_2010", "rdpc", "pib_per_capita"):
            self.assertNotIn(termo, self.src.lower(), termo)
        cols = set(CL.CONJUNTOS["L+M"]) | set(CL.CONJUNTOS["LUF+M"])
        self.assertEqual(cols, {"capital", "regiao", "uf", "log_pop", "med", "esp", "esp_resto"})

    def test_sem_competencia_202609(self):
        comp = RES["parametros"]["competencias_pre"] + RES["parametros"]["competencias_pos_oferta_local"]
        self.assertTrue(all(c < "202609" for c in comp))
        self.assertEqual(CL.LIMITE_CNES, "202609")
        self.assertEqual(RES["parametros"]["competencias_pre"][0], "202406")
        self.assertEqual(RES["parametros"]["competencias_pre"][-1], "202506")

    def test_nao_escreve_em_data(self):
        self.assertNotRegex(self.src, r"ROOT\s*/\s*\"data\"[^\n]*write")
        for k, v in RES["saidas"].items():
            self.assertTrue(v.startswith("output/") or v.startswith("docs/"), v)

    def test_adendo_congelado(self):
        self.assertEqual(CL.sha256(ADENDO), CL.SHA_ADENDO)
        self.assertEqual(RES["adendo"]["sha256"], CL.SHA_ADENDO)


class TestPortoes(unittest.TestCase):
    def test_portao_hi(self):
        p = RES["portao_hi"]
        self.assertTrue(p["aprovado"])
        self.assertLessEqual(p["max_abs_dif"], 1e-8)
        hi = pd.read_csv(OUT / "HI_estimativas.csv", dtype={"corte": str})
        for x in p["linhas"]:
            r = hi[(hi["linha"] == x["linha"]) & (hi["outcome"] == x["linha"]) & (hi["variante"] == "principal")
                   & (hi["corte"] == x["corte"])]
            self.assertEqual(len(r), 1)
            self.assertAlmostEqual(float(r["tau"].iloc[0]), x["tau_csv"], places=12)
            self.assertLessEqual(abs(x["tau_44"] - x["tau_csv"]), 1e-8)
        self.assertEqual(len(p["linhas"]), 4)

    def test_portao_oc(self):
        if not (OUT / "OC_estimativas.csv").exists():
            self.assertIsNone(RES["portao_oc"])
            return
        p = RES["portao_oc"]
        self.assertTrue(p["aprovado"])
        self.assertLessEqual(max(p["difs"].values()), 1e-8)
        oc = pd.read_csv(OUT / "OC_estimativas.csv", dtype={"corte": str})
        r = oc[(oc["id_oc"] == "OC-A1") & (oc["populacao"] == "V") & (oc["corte"] == "0.300")
               & (oc["especificacao"] == "principal")]
        self.assertEqual(len(r), 1)
        self.assertAlmostEqual(float(r["tau"].iloc[0]), p["tau_oc"], places=12)


class TestMultiplicidade(unittest.TestCase):
    def test_holm(self):
        m = EST["entra_holm"]
        self.assertEqual(set(EST.loc[m, "bloco"]), {"PS-1", "PS-2"})
        exe = m & (EST["status"] == "EXECUTADO")
        p = EST.loc[exe, "p_valor"].astype(float).to_numpy()
        if not (EST.loc[m, "status"] == "PENDENTE_OC").any():
            np.testing.assert_allclose(L.holm(p), EST.loc[exe, "p_holm"].astype(float).to_numpy(), atol=1e-12)

    def test_bky(self):
        m = EST["entra_bky"]
        self.assertEqual(set(EST.loc[m, "bloco"]) - {"CL-1", "CL-2", "CL-3", "CL-5", "CL-6", "CL-7", "CL-8"}, set())
        self.assertFalse((EST["bloco"].isin(["CL-4", "CL-9", "PS-3", "PS-4"]) & (m | EST["entra_holm"])).any())
        exe = m & (EST["status"] == "EXECUTADO")
        if not (EST.loc[m, "status"] == "PENDENTE_OC").any():
            q = L.qvalores_bky(EST.loc[exe, "p_valor"].astype(float).to_numpy())
            np.testing.assert_allclose(q, EST.loc[exe, "q_bky"].astype(float).to_numpy(), atol=1e-12)


class TestCoerencia(unittest.TestCase):
    def test_pares_e_ic(self):
        par = EST[EST["metodo"].isin(["pareamento_psm", "pareamento_mahalanobis"])
                  & (EST["status"] == "EXECUTADO")]
        for _, r in par.iterrows():
            self.assertGreaterEqual(int(r["n_pares"]), 2)
            self.assertLessEqual(float(r["ic95_inf"]), float(r["tau"]))
            self.assertGreaterEqual(float(r["ic95_sup"]), float(r["tau"]))
            limpa = "SIM" if float(r["max_abs_dp_depois"]) <= CL.LIMIAR_DP_LIMPA else "NAO"
            self.assertEqual(r["comparacao_limpa"], limpa)

    def test_pares_no_resumo(self):
        for reg in RES["amostra"]["pareamento"]:
            for met in ("PSM", "MAH"):
                info = reg.get(met)
                if not info or "pares" not in info:
                    continue
                pares = info["pares"]
                self.assertEqual(len({p["acima"] for p in pares}), len(pares))
                self.assertEqual(len({p["abaixo"] for p in pares}), len(pares))

    def test_variacao(self):
        r = EST[EST["bloco"].isin(["CL-1", "CL-2", "CL-3"]) & (EST["status"] == "EXECUTADO")]
        np.testing.assert_allclose(r["tau"] - r["tau_sem_controle"], r["variacao_abs"], atol=1e-12)

    def test_cl4_igual_ao_sem_controle_da_cl1(self):
        for _, r in EST[EST["bloco"] == "CL-1"].iterrows():
            r4 = EST[(EST["bloco"] == "CL-4") & (EST["outcome"] == r["outcome"]) & (EST["corte"] == r["corte"])]
            self.assertAlmostEqual(float(r4["tau"].iloc[0]), float(r["tau_sem_controle"]), places=12)


class TestDoc(unittest.TestCase):
    def test_blocos_iguais_ao_gerado(self):
        txt = DOC.read_text(encoding="utf-8")
        achados = {m.group("nome"): m.group("corpo") for m in CL.MARCA.finditer(txt)}
        gerados = CL.gerar_blocos(EST, BAL, RES)
        self.assertEqual(set(gerados), set(achados))
        for nome, corpo in gerados.items():
            self.assertEqual(achados[nome].rstrip(), corpo.rstrip(), nome)

    def test_decisoes_antes_e_linguagem(self):
        txt = DOC.read_text(encoding="utf-8")
        self.assertIn("## 0. Decisões de implementação", txt)
        self.assertLess(txt.index("## 0. Decisões"), txt.index("## 1. Resposta curta"))
        self.assertIn("ADENDO_48D_POS_RESULTADO", txt)
        self.assertIn("Auditoria:** pendente", txt)
        for proibido in ("a bolsa reduz", "a bolsa aumenta", "a bolsa causa", "efeito da bolsa sobre"):
            self.assertNotIn(proibido, txt.lower())

    def test_sem_numeros_fora_dos_blocos_nas_secoes_de_resultado(self):
        txt = DOC.read_text(encoding="utf-8")
        resto = CL.MARCA.sub("", txt[txt.index("## 1. Resposta curta"):])
        parametros = {"0,300", "0,400", "0,050", "0,020", "0,10", "0,25", "0,05", "0,95"}   # do adendo, não resultado
        achados = set(re.findall(r"\d+,\d{2,}", resto))
        self.assertEqual(achados - parametros, set(), "número com decimais fora dos blocos gerados")


class TestSintetico(unittest.TestCase):
    """sintético: dados construídos aqui, só em memória."""

    def test_guloso_global(self):
        cand = [(0.5, "a1", "b1"), (0.1, "a1", "b2"), (0.2, "a2", "b2"), (0.3, "a2", "b1")]
        self.assertEqual(CL.guloso_global(cand), [("a1", "b2", 0.1), ("a2", "b1", 0.3)])

    def test_inferencia_pareada_recupera_deslocamento(self):
        rng = np.random.default_rng(7)
        dif = 1.0 + rng.normal(0, 0.5, 60)                 # sintético
        r = CL.inferencia_pareada(dif)
        self.assertLess(r["ic95_inf"], 1.0 + 0.3)
        self.assertGreater(r["ic95_sup"], 1.0 - 0.3)
        self.assertLess(r["p_valor"], 0.01)
        r0 = CL.inferencia_pareada(dif - dif.mean())
        self.assertGreater(r0["p_valor"], 0.5)

    def test_poucos_pares_ic_nao_limitado(self):
        r = CL.inferencia_pareada(np.array([1.0, 2.0, 3.0]))   # sintético: 3 pares, 8 padrões de sinal
        self.assertTrue(np.isinf(r["ic95_inf"]) and np.isinf(r["ic95_sup"]))

    def test_resto_da_regiao(self):
        idx = pd.Index(["1", "2", "3", "4"])
        cnt = pd.Series([10.0, 20.0, 30.0, 5.0], index=idx)       # sintético
        pop = pd.Series([1e4, 1e4, 2e4, 1e4], index=idx)
        reg = pd.Series(["A", "A", "A", "B"], index=idx)
        r, info = CL._resto_regiao(cnt, pop, reg)
        self.assertAlmostEqual(r["1"], 50.0 / 3e4 * 1e4)
        self.assertTrue(np.isnan(r["4"]))                       # região de um município só
        self.assertEqual(info["municipios_em_regiao_de_um_so"], 1)
        cnt2 = cnt.copy()
        cnt2["2"] = np.nan
        r2, _ = CL._resto_regiao(cnt2, pop, reg)
        self.assertTrue(np.isnan(r2["1"]))                      # outro da região ausente: ausente
        self.assertFalse(np.isnan(r2["2"]))                     # o próprio ausente não impede o resto


if __name__ == "__main__":
    unittest.main()
