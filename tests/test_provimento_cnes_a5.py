"""Invariantes A5 — dinâmica associativa da oferta cadastrada no CNES."""

from __future__ import annotations

import json
import hashlib
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "tema_trabalho"

# Entradas declaradas por A5 que o pipeline regera e o repositorio nao versiona.
REGERAVEIS_NAO_VERSIONADOS = {"output/painel_municipio_curso_mensal.parquet"}


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class ProvimentoCnesA5Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.panel = pd.read_parquet(OUT / "A5_painel_T0.parquet")
        cls.cross = pd.read_csv(OUT / "A5_cross_section_6m.csv", dtype={"co_ibge_6d": str})
        cls.manifest = json.loads((OUT / "A5_manifesto_maturidade_censura.json").read_text(encoding="utf-8"))
        cls.est = json.loads((OUT / "A5_estimativas_provimento.json").read_text(encoding="utf-8"))
        cls.report = (OUT / "A5_relatorio_diagnostico.md").read_text(encoding="utf-8")

    def test_hashes_entradas_conferem(self) -> None:
        # Proveniencia de A5, ausente ate entao: A3, A4 e A6 ja checavam seus
        # hashes de entrada, mas A5 nao, e por isso registros obsoletos de A5
        # passavam despercebidos. Os sha256 sao sempre da forma canonica LF
        # imposta pelo .gitattributes; um tree com CRLF produz outro digest.
        #
        # Uma unica entrada declarada nao e versionada: o painel mensal
        # municipio-curso e regeravel pelo pipeline e esta no .gitignore. Num
        # clone limpo ele nao existe, entao a existencia so e exigida dos
        # arquivos versionados; se o painel estiver presente, o hash e cobrado
        # como qualquer outro.
        for artefato, hashes in [
            ("A5_estimativas_provimento.json", self.est["hashes_entradas"]),
            ("A5_manifesto_maturidade_censura.json", self.manifest["hashes_entradas"]),
        ]:
            self.assertGreater(len(hashes), 3, f"bloco de hashes incompleto em {artefato}")
            conferidos = 0
            for rel, meta in hashes.items():
                caminho = ROOT / rel
                if not caminho.exists():
                    self.assertIn(
                        rel,
                        REGERAVEIS_NAO_VERSIONADOS,
                        f"missing {artefato}: {rel}",
                    )
                    continue
                self.assertEqual(sha(caminho), meta["sha256"], f"hash diverge {artefato}: {rel}")
                conferidos += 1
            self.assertGreater(conferidos, 3, f"poucas entradas conferidas em {artefato}")

    def test_painel_balanceado(self) -> None:
        self.assertEqual(len(self.panel), 1184 * 26)
        self.assertEqual(self.panel["co_ibge_6d"].nunique(), 368)
        self.assertFalse(self.panel.duplicated(["co_ibge_6d", "cod_curso", "competencia"]).any())

    def test_referencia_limpa_e_timing(self) -> None:
        timing = self.est["t0_e_horizonte"]
        self.assertEqual(timing["referencia_pre_oferta"], "202506")
        self.assertEqual(timing["follow_comum"], "202603")
        self.assertNotIn("baseline", timing)
        self.assertIn("Setembro/2025 não é usado como baseline", self.report)
        self.assertIn("tempo de exposição física heterogêneo", self.report)

    def test_amostra_principal_confirmatoria(self) -> None:
        self.assertEqual(self.cross["amostra_confirmatoria"].sum(), 587)
        primary = self.est["modelos"]["principal_dinamico_confirmatorio"]
        self.assertEqual(primary["n_celulas"], 587)
        self.assertEqual(primary["n_clusters"], 295)
        level = pd.read_csv(OUT / "A5_tabela_03_modelo_estoque_6m.csv")
        row = level[(level["termo"] == "atracao_muni") & level["espec"].str.contains("minimal")].iloc[0]
        self.assertEqual(int(row["n"]), 587)
        self.assertEqual(int(row["n_clusters"]), 295)

    def test_estudo_evento(self) -> None:
        event = pd.read_csv(OUT / "A5_tabela_07_estudo_evento_atracao.csv", dtype={"competencia": str})
        self.assertEqual(set(event["amostra"]), {"confirmatoria_587", "ampliada_1184"})
        self.assertEqual(len(event), 52)
        ref = event[(event["amostra"] == "confirmatoria_587") & (event["competencia"] == "202506")].iloc[0]
        self.assertTrue(ref["referencia"])
        self.assertEqual(ref["beta"], 0)
        summary = self.est["modelos"]["principal_dinamico_confirmatorio"]
        self.assertIn("pre_p", summary)
        self.assertIn("mar2026_beta", summary)

    def test_delta_distribuicao_transparente(self) -> None:
        self.assertIn("delta_estoque_jun25_mar26", self.cross.columns)
        distribution = self.est["modelos"]["distribuicao_delta_confirmatoria"]
        self.assertEqual(distribution["0"]["mediana"], 0)
        self.assertEqual(distribution["1"]["mediana"], 1)
        self.assertGreater(distribution["1"]["max"], 100)
        self.assertIn("mediana", self.report.lower())
        self.assertIn("máximo", self.report.lower())

    def test_fluxo_mensal_nao_e_acumulado(self) -> None:
        definition = self.est["outcomes_permitidos"]["n_entradas_6m"].lower()
        self.assertIn("washout", definition)
        self.assertIn("nao fluxo acumulado", definition)
        self.assertIn("não entradas acumuladas", self.report.lower())

    def test_censura(self) -> None:
        self.assertTrue(self.panel.loc[self.panel["competencia"] < "202412", "n_entradas_6m"].isna().all())
        self.assertTrue(self.panel.loc[self.panel["competencia"] > "202604", "n_saidas_confirmadas_3m"].isna().all())
        checks = self.manifest["checks"]
        self.assertTrue(checks["painel_balanceado_1184x26"])
        self.assertTrue(checks["referencia_202506_madura_para_6m"])

    def test_figuras(self) -> None:
        for name in [
            "A5_figura_01_trajetoria_estoque_estrato.png",
            "A5_figura_02_trajetoria_estoque_atracao.png",
            "A5_figura_03_delta_estoque_atracao.png",
            "A5_figura_04_estudo_evento_atracao.png",
        ]:
            path = OUT / name
            self.assertTrue(path.exists())
            self.assertGreater(path.stat().st_size, 5000)

    def test_linguagem(self) -> None:
        low = self.report.lower()
        self.assertIn("associativo", low)
        self.assertIn("proibido", low)
        self.assertIn("evolução do estoque cadastral", low)
        self.assertNotIn("persistencia da oferta medica local no cnes", low)
        self.assertIn("retenção individual", low)


if __name__ == "__main__":
    unittest.main()
