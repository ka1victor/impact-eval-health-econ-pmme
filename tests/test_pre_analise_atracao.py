"""Invariantes da pré-análise A3 — núcleo associativo."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
REGISTRO = ROOT / "output" / "tema_trabalho" / "registro_pre_analise_atracao.json"
POTENCIA = ROOT / "output" / "tema_trabalho" / "potencia_atracao.json"
QUADRO = ROOT / "output" / "aquisicao" / "quadro_vagas_tratamento.parquet"


class PreAnaliseAtracaoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registro = json.loads(REGISTRO.read_text(encoding="utf-8"))
        cls.potencia = json.loads(POTENCIA.read_text(encoding="utf-8"))

    def test_outcome_conforme_A1(self) -> None:
        out = self.registro["outcome_primario"]
        self.assertEqual(out["nome"], "alguma_confirmacao_ou_homologacao_na_celula")
        self.assertIn("taxa de preenchimento por vaga", out["outcomes_bloqueados"])
        self.assertEqual(out["tipo"], "binário por célula")
        self.assertFalse(self.registro["efeitos_estimados"])

    def test_unidade_e_cluster(self) -> None:
        self.assertIn("célula CNES", self.registro["populacao"]["unidade_analitica"])
        self.assertEqual(self.registro["populacao"]["primaria"][:4], "1295")
        self.assertIn("município", self.registro["inferencia"]["unidade_cluster"])
        self.assertIn("cluster", self.registro["inferencia"]["metodo"].lower())

    def test_covariadas_pre_oferta_e_ivs_canonico(self) -> None:
        cov = self.registro["covariadas_exclusivamente_pre_oferta"]
        permitidas = " ".join(cov["permitidas"])
        self.assertIn("ivs_2010", permitidas)
        proibidas = " ".join(cov["proibidas"])
        self.assertIn("CNES pós", proibidas)
        # IVS canônico — não substituir por IDHM sem justificativa está no texto
        self.assertTrue(any("IVS" in p for p in cov["proibidas"]) or "IDHM" in proibidas)

    def test_modelos_e_efeitos_fixos(self) -> None:
        esp = self.registro["especificacao"]
        self.assertTrue(any("LPM" in m for m in esp["modelos_candidatos_primarios"]))
        self.assertTrue(any("Logit" in m for m in esp["modelos_candidatos_primarios"]))
        self.assertIn("curso", esp["efeitos_fixos"])
        self.assertIn("UF", esp["efeitos_fixos"])

    def test_potencia_global_e_por_estrato(self) -> None:
        self.assertAlmostEqual(self.potencia["alfa_bilateral"], 0.05)
        self.assertAlmostEqual(self.potencia["poder_alvo"], 0.80)
        # O global é apenas benchmark de uma proporção, não potência do contraste.
        self.assertLess(self.potencia["mde_global"]["mde_80_pp_p30"], 0.05)
        self.assertIn("não é o MDE", self.potencia["mde_global"]["rotulo"])
        # Próximo é o estrato mais potenciado (maior n)
        self.assertLess(
            self.potencia["por_estrato"]["interior_proximo_polo"]["mde_80_pp_p30"],
            self.potencia["por_estrato"]["capital"]["mde_80_pp_p30"],
        )
        # DEFF nunca <1 (floor)
        for estr, vals in self.potencia["por_estrato"].items():
            self.assertGreaterEqual(vals["deff_assumido"], 1.0, f"DEFF<1 em {estr}")
            self.assertGreater(vals["m_medio_celulas_por_municipio"], 1.0, f"m<1 em {estr} — usa populacao A1 em vez de quadro")
        # n_municipios deve ser do quadro Ch1 (368), não populacao A1 (540)
        self.assertEqual(self.potencia["por_estrato"]["capital"]["n_municipios"], 18)
        self.assertEqual(self.potencia["por_estrato"]["metropolitano"]["n_municipios"], 72)
        self.assertEqual(self.potencia["por_estrato"]["interior_proximo_polo"]["n_municipios"], 203)
        self.assertEqual(self.potencia["por_estrato"]["interior_remoto"]["n_municipios"], 75)
        self.assertEqual(self.potencia["por_estrato"]["capital"]["n_celulas"], 73)
        self.assertEqual(self.potencia["por_estrato"]["metropolitano"]["n_celulas"], 265)
        self.assertEqual(self.potencia["por_estrato"]["interior_proximo_polo"]["n_celulas"], 811)
        self.assertEqual(self.potencia["por_estrato"]["interior_remoto"]["n_celulas"], 146)
        self.assertEqual(self.potencia["amostra_primaria"]["n_municipios_clusters"], 368)
        self.assertEqual(self.potencia["amostra_primaria"]["n_celulas"], 1295)

    def test_potencia_mde_numerico(self) -> None:
        # Valida MDE 80% p=0.30 contra DEFF correto (ICC=0.05) com tolerância 0.001
        # Valores congelados após correção strict (18/72/203/75)
        esperado = {
            "capital": 0.1613,
            "metropolitano": 0.0840,
            "interior_proximo_polo": 0.0483,
            "interior_remoto": 0.1087,
        }
        for estr, exp in esperado.items():
            obt = self.potencia["por_estrato"][estr]["mde_80_pp_p30"]
            self.assertAlmostEqual(obt, exp, places=3, msg=f"MDE {estr} esperado {exp} obtido {obt}")

    def test_potencia_contrastes_vs_remoto(self) -> None:
        contrastes = self.potencia["contrastes_vs_interior_remoto"]
        self.assertEqual(set(contrastes), {"capital", "metropolitano", "interior_proximo_polo"})
        for vals in contrastes.values():
            self.assertEqual(vals["referencia"], "interior_remoto")
            self.assertGreater(vals["mde_80_pp_p30"], 0.10)
            self.assertGreater(vals["mde_80_pp_p50"], vals["mde_80_pp_p30"])

    def test_potencia_clusters_quadro_coerencia(self) -> None:
        # Garante que potência por estrato usa join quadro↔tipologia (clusters do quadro), não populacao A1
        import pandas as pd

        quadro = pd.read_parquet(QUADRO)
        tip = pd.read_parquet(ROOT / "output" / "tema_trabalho" / "matriz_tipologia_territorial.parquet")
        qj = quadro.merge(tip[["co_ibge_6d", "estrato"]], on="co_ibge_6d", how="left")
        por_mun = qj.groupby("estrato")["co_ibge_6d"].nunique().to_dict()
        for estr, g in por_mun.items():
            self.assertEqual(self.potencia["por_estrato"][estr]["n_municipios"], int(g))

    def test_linguagem_maxima(self) -> None:
        ling = self.registro["linguagem_maxima"]
        texto = ling["proibido"]
        self.assertIn("preenchimento por vaga", texto)
        self.assertIn("individual", texto)

    def test_hashes_presentes(self) -> None:
        self.assertIn("output/aquisicao/quadro_vagas_tratamento.parquet", self.registro["hashes_entradas"])
        self.assertGreater(len(self.registro["hashes_entradas"]), 3)
        # Território versionado deve estar nos hashes (REGIC + RM/RIDE)
        self.assertIn("data/raw/aquisicao/territorio/REGIC2018_Municipios_Hierarquia_e_regiao.xlsx", self.registro["hashes_entradas"])
        self.assertIn("data/raw/aquisicao/territorio/Composicao_RMs_RIDEs_AglomUrbanas_2022_v2.xlsx", self.registro["hashes_entradas"])
        self.assertIn("output/tema_trabalho/manifesto_tipologia_territorial.json", self.registro["hashes_entradas"])
        self.assertIn("output/tema_trabalho/portao_denominador.json", self.registro["hashes_entradas"])
        # Hashes conferem com arquivos
        import hashlib

        def sha(p: Path) -> str:
            h = hashlib.sha256()
            with (ROOT / p).open("rb") as f:
                for chunk in iter(lambda: f.read(1 << 20), b""):
                    h.update(chunk)
            return h.hexdigest()

        for rel, meta in self.registro["hashes_entradas"].items():
            self.assertEqual(sha(rel), meta["sha256"], f"hash diverge {rel}")
        for rel, meta in self.registro["hashes_artefatos_A1_A2"].items():
            self.assertEqual(sha(rel), meta["sha256"], f"hash artefato diverge {rel}")

    def test_tipologia_congelada_strict(self) -> None:
        tip = self.registro["tipologia_congelada"]
        self.assertIn("strict", tip["fonte"].lower())
        self.assertIn("540/540", tip["cobertura_A1"])
        self.assertIn("25", tip["cobertura_A1"])
        self.assertIn("101", tip["cobertura_A1"])
        self.assertIn("368", tip["cobertura_A1"])

    def test_secao_econometrica_completa(self) -> None:
        secao = (ROOT / "docs" / "06_execucao" / "31_secao_econometrica_A3.md").read_text(encoding="utf-8")
        for termo in ["capital", "metropolitano", "interior_proximo", "interior_remoto", "DEFF", "MDE"]:
            self.assertIn(termo, secao)

    def test_quadro_consistencia(self) -> None:
        q = pd.read_parquet(QUADRO)
        self.assertEqual(len(q), 1295)
        self.assertEqual(q["qt_vagas_imediatas"].sum(), 678)


if __name__ == "__main__":
    unittest.main()
