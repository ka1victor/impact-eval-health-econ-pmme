"""Invariantes A5 — dinâmica associativa da oferta cadastrada no CNES."""

from __future__ import annotations

import json
import hashlib
import unittest
from pathlib import Path

import numpy as np
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

    def test_escala_proporcional_e_primaria(self) -> None:
        # C2 do plano congelado: a escala proporcional passa a ser a forma
        # primaria de reportar A5, com os coeficientes registrados na auditoria
        # antes da implementacao.
        prop = pd.read_csv(OUT / "A5_tabela_08_estudo_evento_proporcional.csv", dtype={"competencia": str})
        linha = prop[(prop["amostra"] == "confirmatoria_587") & (prop["competencia"] == "202603")].iloc[0]
        self.assertEqual(round(float(linha["beta"]), 4), 0.0684)
        self.assertEqual(round(float(linha["p_valor"]), 4), 0.0002)
        escala = self.est["escala_de_reporte"]
        self.assertIn("proporcional", escala["primaria"])
        self.assertIn("nivel", escala["sensibilidade"])
        self.assertIn("fragil", escala["sensibilidade"])

    def test_leave_one_curso_do_coeficiente_de_evento(self) -> None:
        loo = pd.read_csv(OUT / "A5_tabela_09_leave_one_curso_evento.csv")
        self.assertEqual(set(loo["escala"]), {"nivel", "proporcional"})
        # 10 cursos deixados de fora, mais a amostra cheia e os 8 estritos.
        self.assertEqual(len(loo), 24)
        alvos = {
            ("nivel", "sem_curso_14", 3): 0.200,
            ("nivel", "somente_8_cbo_1_para_1", 3): 0.121,
            ("proporcional", "sem_curso_14", 4): 0.0592,
            ("proporcional", "somente_8_cbo_1_para_1", 4): 0.0570,
        }
        for (escala, subamostra, casas), alvo in alvos.items():
            linha = loo[(loo["escala"] == escala) & (loo["subamostra"] == subamostra)].iloc[0]
            self.assertEqual(round(float(linha["beta"]), casas), alvo, f"{escala}/{subamostra}")
        estritos = loo[loo["subamostra"] == "somente_8_cbo_1_para_1"]["n_cursos"].unique().tolist()
        self.assertEqual(estritos, [8])

    def test_sensibilidade_mes_de_referencia(self) -> None:
        ref = pd.read_csv(OUT / "A5_tabela_10_sensibilidade_referencia.csv")
        linha = ref[(ref["escala"] == "nivel") & (ref["referencia"] == "media_12_meses_pre")].iloc[0]
        self.assertEqual(round(float(linha["beta"]), 3), 0.405)
        self.assertEqual(round(float(linha["p_valor"]), 3), 0.174)
        # A referencia publicada continua sendo 202506 e continua na tabela.
        self.assertIn("202506", set(ref["referencia"].astype(str)))

    def test_graus_de_liberdade_contam_os_fe_absorvidos(self) -> None:
        correcao = self.est["correcao_graus_liberdade"]
        self.assertEqual(correcao["k_regressores_visiveis"], 25)
        self.assertEqual(correcao["n_parametros_fe_absorvidos"], 1547)
        self.assertEqual(round(correcao["nivel_202603_se_k_visivel"], 4), 0.2340)
        self.assertEqual(round(correcao["nivel_202603_p_k_visivel"], 4), 0.0334)
        self.assertEqual(round(correcao["nivel_202603_se_gl_fe"], 4), 0.2469)
        self.assertEqual(round(correcao["nivel_202603_p_gl_fe"], 4), 0.0437)
        evento = pd.read_csv(OUT / "A5_tabela_07_estudo_evento_atracao.csv", dtype={"competencia": str})
        for coluna in ["se_cluster_gl_fe", "p_valor_gl_fe", "ci_low_gl_fe", "ci_high_gl_fe"]:
            self.assertIn(coluna, evento.columns)

    def test_fit_absorbed_ols_sem_n_absorbed_nao_muda(self) -> None:
        # O parametro e opt-in: os scripts da versao agregada do ciclo 1 usam a
        # funcao sem ele e nao podem mudar de comportamento.
        import sys

        sys.path.insert(0, str(ROOT / "scripts" / "avaliacao_impacto"))
        from model_utils import fit_absorbed_ols

        rng = np.random.default_rng(20260909)
        n = 400
        frame = pd.DataFrame({
            "g": rng.integers(0, 20, n),
            "h": rng.integers(0, 10, n),
            "cluster": rng.integers(0, 25, n),
            "x": rng.normal(size=n),
        })
        frame["y"] = 1.5 * frame["x"] + frame["g"] * 0.1 + rng.normal(size=n)
        base, _ = fit_absorbed_ols(frame, "y", ["x"], ["g", "h"], "cluster")
        repetido, _ = fit_absorbed_ols(frame, "y", ["x"], ["g", "h"], "cluster", n_absorbed=None)
        self.assertEqual(float(base.bse["x"]), float(repetido.bse["x"]))
        n_fe = frame["g"].nunique() + frame["h"].nunique() - 1
        corrigido, diag = fit_absorbed_ols(frame, "y", ["x"], ["g", "h"], "cluster", n_absorbed=n_fe)
        fator = (n - 1) / (n - 1 - n_fe)
        self.assertEqual(float(corrigido.params["x"]), float(base.params["x"]))
        self.assertAlmostEqual(
            float(corrigido.bse["x"]) / float(base.bse["x"]), float(np.sqrt(fator)), places=12
        )
        self.assertEqual(diag["n_parametros_fe_absorvidos"], n_fe)

    def test_nomenclatura_cbo_nao_compartilhado(self) -> None:
        ponte = self.manifest["ponte_curso_cbo"]
        self.assertEqual(len(ponte["cursos_cbo_nao_compartilhado_confirmatorios"]), 10)
        self.assertEqual(ponte["n_cursos_cbo_estritamente_1_para_1"], 8)
        self.assertEqual(
            sorted(int(c) for c in ponte["cursos_nao_compartilhados_com_multiplos_cbo"]), [14, 16]
        )
        low = self.report.lower()
        self.assertIn("cbo não compartilhado entre cursos", low)
        # "Unívoco" só pode aparecer na frase que corrige o rótulo, nunca como
        # descritor da amostra confirmatória.
        for descritor in ["cursos com cbo unívoco", "ponte cbo unívoca", "dez cursos com cbo unívoco"]:
            self.assertNotIn(descritor, low)
        self.assertIn('e não "cbo unívoco"', low)

    def test_linguagem(self) -> None:
        low = self.report.lower()
        self.assertIn("associativo", low)
        self.assertIn("proibido", low)
        self.assertIn("evolução do estoque cadastral", low)
        self.assertNotIn("persistencia da oferta medica local no cnes", low)
        self.assertIn("retenção individual", low)


if __name__ == "__main__":
    unittest.main()
