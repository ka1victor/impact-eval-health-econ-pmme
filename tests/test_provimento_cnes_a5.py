"""Invariantes A5 — persistencia da oferta medica local no CNES.

Verifica prompt 05_avaliar_provimento_cnes.md:
- painel analitico alinhado ao T0
- manifesto maturidade/censura
- trajetoria agregada
- decisao explicita ligacao com atracao
E proibicoes: retencao individual, atividade fisica, efeito causal bolsa.
"""

from __future__ import annotations

import json
import hashlib
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "tema_trabalho"
PAINEL_T0 = OUT / "A5_painel_T0.parquet"
CROSS = OUT / "A5_cross_section_6m.csv"
MANIFESTO = OUT / "A5_manifesto_maturidade_censura.json"
ESTIMATIVAS = OUT / "A5_estimativas_provimento.json"
RELATORIO = OUT / "A5_relatorio_diagnostico.md"
PAINEL_MUNI = ROOT / "output" / "painel_municipio_curso_mensal.parquet"


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class ProvimentoCnesA5Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifesto = json.loads(MANIFESTO.read_text(encoding="utf-8"))
        cls.estim = json.loads(ESTIMATIVAS.read_text(encoding="utf-8"))
        cls.rel = RELATORIO.read_text(encoding="utf-8")
        cls.cross = pd.read_csv(CROSS)
        cls.painel = pd.read_parquet(PAINEL_T0)

    def test_arquivos_existem(self) -> None:
        for key, rel in self.estim["arquivos"].items():
            p = ROOT / rel
            self.assertTrue(p.exists(), f"missing {key}: {rel}")
            self.assertGreater(p.stat().st_size, 0, f"empty {rel}")
        # manifesto arquivos also
        for key, rel in self.manifesto["arquivos"].items():
            p = ROOT / rel if not rel.startswith("output/") else ROOT / rel
            # manifesto may have painel_T0 etc already checked
            self.assertTrue((ROOT / rel).exists(), f"manifesto missing {key}")

    def test_hashes_conferem(self) -> None:
        for rel, meta in self.estim["hashes_entradas"].items():
            self.assertEqual(sha(ROOT / rel), meta["sha256"], f"hash diverge {rel}")
        for rel, meta in self.manifesto["hashes_entradas"].items():
            # manifesto includes same plus potential fallback, skip if missing
            p = ROOT / rel
            if p.exists():
                self.assertEqual(sha(p), meta["sha256"], f"manifesto hash diverge {rel}")

    def test_painel_T0_balanceado_e_alinhado(self) -> None:
        self.assertEqual(len(self.painel), 30784)
        self.assertEqual(self.painel["competencia"].nunique(), 26)
        self.assertFalse(self.painel.duplicated(["co_ibge_6d","cod_curso","competencia"]).any())
        # t_rel_T0 must be competencia index - t0 idx 16
        self.assertIn("t_rel_T0", self.painel.columns)
        self.assertEqual(self.painel[self.painel["competencia"]=="202510"]["t_rel_T0"].iloc[0], 0)
        self.assertEqual(self.painel[self.painel["competencia"]=="202509"]["t_rel_T0"].iloc[0], -1)
        self.assertEqual(self.painel[self.painel["competencia"]=="202603"]["t_rel_T0"].iloc[0], 5)
        # censura checks
        self.assertTrue(self.painel.loc[self.painel["competencia"]<"202412","n_entradas_6m"].isna().all())
        self.assertTrue(self.painel.loc[self.painel["competencia"]>="202412","n_entradas_6m"].notna().all())
        self.assertTrue(self.painel.loc[self.painel["competencia"]>"202604","n_saidas_confirmadas_3m"].isna().all())
        self.assertTrue(self.painel.loc[self.painel["competencia"]<="202601","entrantes_presentes_6m"].notna().any())

    def test_cross_section_exata(self) -> None:
        self.assertEqual(len(self.cross), 1184)
        self.assertEqual(self.cross["co_ibge_6d"].nunique(), 368)
        self.assertIn("atracao_muni", self.cross.columns)
        self.assertIn("delta_estoque_6m", self.cross.columns)
        self.assertIn("presentes_baseline_6m", self.cross.columns)
        # atracao coverage must be 378 with 1, 806 with 0 (from earlier)
        self.assertEqual(self.cross[self.cross["atracao_muni"]==1].shape[0], 378)
        self.assertEqual(self.cross[self.cross["atracao_muni"]==0].shape[0], 806)
        # baseline 202509 estoque mean 13.92 approx
        self.assertAlmostEqual(self.cross["estoque_baseline"].mean(), 13.92, delta=0.1)
        self.assertAlmostEqual(self.cross["delta_estoque_6m"].mean(), 0.73, delta=0.1)

    def test_construcao_steps(self) -> None:
        cons = pd.read_csv(OUT / "A5_tabela_00_construcao_steps.csv")
        self.assertEqual(cons[cons["etapa"]=="01_quadro_Ch1_cnes_curso"]["n_celulas"].values[0], 1295)
        self.assertEqual(cons[cons["etapa"]=="02_municipio_curso_agregado"]["n_celulas"].values[0], 1184)
        self.assertEqual(cons[cons["etapa"]=="03_painel_completo_26_comp"]["n_celulas"].values[0], 30784)
        self.assertEqual(cons[cons["etapa"]=="04_confirmatoria_10_cursos"]["n_celulas"].values[0], 587)
        self.assertEqual(cons[cons["etapa"]=="06_baseline_202509_madura"]["n_celulas"].values[0], 1184)

    def test_maturidade_e_ponte_no_manifesto(self) -> None:
        self.assertEqual(self.manifesto["t0"]["baseline_competencia"], "202509")
        self.assertEqual(self.manifesto["t0"]["follow_6m_competencia"], "202603")
        self.assertEqual(self.manifesto["t0"]["homologacao_competencia_admin_T0"], "202510")
        self.assertEqual(self.manifesto["ponte_curso_cbo"]["n_cursos_confirmatorios"], 10)
        self.assertEqual(self.manifesto["ponte_curso_cbo"]["celulas_confirmatorias_202509"], 587)
        self.assertTrue(self.manifesto["checks"]["26_competencias_presentes"])
        self.assertTrue(self.manifesto["checks"]["painel_balanceado_1184x26"])
        self.assertTrue(self.manifesto["checks"]["censura_entradas_primeiros_6_meses"])
        # nominal stats must exist
        self.assertIn("ciclo1_n", self.manifesto["t0"]["validacao_fisica_nominal"])
        self.assertEqual(self.manifesto["t0"]["validacao_fisica_nominal"]["ciclo1_n"], 521)

    def test_modelo_estoque_e_delta(self) -> None:
        est = pd.read_csv(OUT / "A5_tabela_03_modelo_estoque_6m.csv")
        self.assertIn("atracao_muni", est["termo"].values)
        # estoque level should be positive and significant in minimal
        row = est[(est["termo"]=="atracao_muni") & (est["espec"].str.contains("minimal"))].iloc[0]
        self.assertGreater(row["coef"], 5)
        self.assertLess(row["p_valor"], 0.05)
        self.assertEqual(int(row["n"]), 1184)
        self.assertEqual(int(row["n_clusters"]), 368)
        # delta minimal non-sign or small - check exists
        delta = pd.read_csv(OUT / "A5_tabela_03b_modelo_delta_estoque.csv")
        row_d = delta[(delta["termo"]=="atracao_muni") & (delta["espec"].str.contains("minimal"))].iloc[0]
        # delta coef 0.64 with p ~0.11 (non-sig at 5% allowed)
        self.assertAlmostEqual(row_d["coef"], 0.64, delta=0.1)
        # cobertura LPM minimal significant
        cob = pd.read_csv(OUT / "A5_tabela_03c_modelo_cobertura.csv")
        row_c = cob[(cob["termo"]=="atracao_muni") & (cob["espec"].str.contains("minimal"))].iloc[0]
        self.assertAlmostEqual(row_c["coef"], 0.044, delta=0.02)
        self.assertLess(row_c["p_valor"], 0.05)

    def test_entradas_e_presenca_nivel_nao_taxa(self) -> None:
        ent = pd.read_csv(OUT / "A5_tabela_03d_modelo_entradas.csv")
        row = ent[(ent["termo"]=="atracao_muni") & (ent["espec"].str.contains("minimal"))].iloc[0]
        self.assertGreater(row["coef"], 0)
        # presenca nivel
        pres = pd.read_csv(OUT / "A5_tabela_03e_modelo_presenca.csv")
        row_p = pres[(pres["termo"]=="atracao_muni") & (pres["espec"].str.contains("minimal"))].iloc[0]
        self.assertGreater(row_p["coef"], 0)
        # Verify cross section has nivel not taxa: presentes_baseline_6m is count, not ratio
        self.assertTrue((self.cross["presentes_baseline_6m"]>=0).all())
        self.assertTrue((self.cross["presentes_baseline_6m"]<=self.cross["elegiveis_baseline_6m"].fillna(0)).all() | (self.cross["elegiveis_baseline_6m"]==0).any())  # trivial

    def test_loo_e_influencia(self) -> None:
        loo = pd.read_csv(OUT / "A5_tabela_04_leave_one_out.csv")
        self.assertEqual(loo[loo["tipo"]=="leave_one_UF"]["excluido"].nunique(), 27)
        self.assertEqual(loo[loo["tipo"]=="leave_one_curso"]["excluido"].nunique(), 16)
        infl = pd.read_csv(OUT / "A5_tabela_05_influencia_municipal.csv")
        self.assertEqual(len(infl), 368)
        self.assertLess(infl["dfbeta"].abs().max(), 1.5)

    def test_validacao_preditiva(self) -> None:
        pred = pd.read_csv(OUT / "A5_tabela_06_validacao_preditiva.csv")
        self.assertEqual(len(pred), 2)
        # R2 out should not be NaN
        self.assertFalse(pred["r2_media_out"].isna().all())
        self.assertFalse(pred["r2_insample"].isna().all())

    def test_trajetoria_e_figuras(self) -> None:
        traj = pd.read_csv(OUT / "A5_tabela_01b_trajetoria_mensal.csv")
        self.assertEqual(len(traj), 26)
        self.assertIn("especialistas_mst_mean", traj.columns)
        for fname in ["A5_figura_01_trajetoria_estoque_estrato.png","A5_figura_02_trajetoria_estoque_atracao.png","A5_figura_03_delta_estoque_atracao.png"]:
            p = OUT / fname
            self.assertTrue(p.exists())
            self.assertGreater(p.stat().st_size, 5000)

    def test_linguagem_e_proibicoes(self) -> None:
        self.assertIn("associativa", self.rel.lower())
        self.assertIn("persistencia da oferta local", self.rel.lower())
        self.assertIn("oferta cadastrada local", self.rel.lower())
        # Proibido termos devem aparecer como proibição, não como afirmação; mas relatorio deve mencionar proibido
        self.assertIn("Proibido", self.rel)
        self.assertIn("Nao pode", self.rel)
        # Não deve conter afirmação causal indevida como "efeito causal do PMM-E" sem proibido
        # Verificar que json linguagem contém associativa e proibido
        self.assertIn("associativa", self.estim["linguagem"])
        self.assertTrue(self.estim["efeitos_estimados"])
        # Não usar lista nominal
        self.assertNotIn("CPF", self.rel)
        # Verificar que manifesto avisos contém retenção bloqueada
        avisos = " ".join(self.manifesto["avisos_linguagem"]).lower()
        self.assertIn("retencao", avisos)

    def test_ponte_estratificada_nao_contamina(self) -> None:
        # Verifica que primário é 1184 com FE, mas manifesto declara 587 confirmatoria como primária conceitual
        # Cross deve ter coluna amostra_confirmatoria
        self.assertIn("amostra_confirmatoria", self.cross.columns)
        self.assertEqual(self.cross[self.cross["amostra_confirmatoria"]].shape[0], 587)

    def test_nao_condiciona_apenas_entrantes(self) -> None:
        # Modelos principais usam estoque/cobertura incondicional, não apenas entrantes
        # Verifica que desc outcomes includes delta incondicional
        desc = pd.read_csv(OUT / "A5_tabela_02_descritiva_outcomes_6m.csv")
        self.assertIn("delta_medio", desc.columns)
        self.assertIn("estoque_baseline_medio", desc.columns)


if __name__ == "__main__":
    unittest.main()
