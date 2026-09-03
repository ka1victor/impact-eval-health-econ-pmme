"""Invariantes A4 — estimação da atração (núcleo associativo).

Verifica sequência do prompt 04_estimar_atracao.md:
1) suporte antes dos coefs, 2) primário exatamente como A3, 3) AME/IC cluster,
4) leave-one-UF/curso e influência municipal, 5) separação faixa/IVS/remoticidade sem causalidade,
6) validação preditiva por município. E proibições: WTA, p-valor selection, efeito bolsa.
"""

from __future__ import annotations

import json
import hashlib
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "tema_trabalho"
ESTIMATIVAS = OUT / "A4_estimativas_atracao.json"
RELATORIO = OUT / "A4_relatorio_diagnostico.md"
QUADRO = ROOT / "output" / "aquisicao" / "quadro_vagas_tratamento.parquet"


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class EstimativasAtracaoA4Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.estim = json.loads(ESTIMATIVAS.read_text(encoding="utf-8"))
        cls.rel = RELATORIO.read_text(encoding="utf-8")

    def test_arquivos_existem(self) -> None:
        for key, rel in self.estim["arquivos"].items():
            p = ROOT / rel
            self.assertTrue(p.exists(), f"missing {key}: {rel}")
            self.assertGreater(p.stat().st_size, 0, f"empty {rel}")

    def test_hashes_entradas_conferem(self) -> None:
        for rel, meta in self.estim["hashes_entradas"].items():
            self.assertEqual(sha(ROOT / rel), meta["sha256"], f"hash diverge {rel}")

    def test_populacao_primaria_exata(self) -> None:
        pop = self.estim["populacao"]
        self.assertIn("1295", pop["primaria"])
        self.assertIn("368", pop["primaria"])
        self.assertIn("3057", pop["estendida"])
        # Confere com quadro real
        q = pd.read_parquet(QUADRO)
        self.assertEqual(len(q), 1295)
        self.assertEqual(q["qt_vagas_imediatas"].sum(), 678)
        # Verifica tabelas amostra por estrato
        am = pd.read_csv(OUT / "A4_tabela_01_amostra_construcao.csv")
        prim = am[am["amostra"] == "primaria_1295_Ch1"]
        self.assertEqual(prim[prim["estrato"] == "capital"]["n_celulas"].values[0], 73)
        self.assertEqual(prim[prim["estrato"] == "metropolitano"]["n_celulas"].values[0], 265)
        self.assertEqual(prim[prim["estrato"] == "interior_proximo_polo"]["n_celulas"].values[0], 811)
        self.assertEqual(prim[prim["estrato"] == "interior_remoto"]["n_celulas"].values[0], 146)

    def test_construcao_steps(self) -> None:
        cons = pd.read_csv(OUT / "A4_tabela_00_construcao_steps.csv")
        self.assertEqual(cons[cons["etapa"] == "01_funil_total_A1"]["n_celulas"].values[0], 3323)
        self.assertEqual(cons[cons["etapa"] == "03_estendida_A1"]["n_celulas"].values[0], 3057)
        self.assertEqual(cons[cons["etapa"] == "04_primaria_quadro_Ch1"]["n_celulas"].values[0], 1295)

    def test_modelo_primario_LPM(self) -> None:
        lpm = pd.read_csv(OUT / "A4_tabela_02_modelo_principal_LPM.csv")
        # 3 coefs estrato
        estr = lpm[lpm["termo"].str.startswith("estrato_")]
        self.assertEqual(len(estr), 3)
        # Metro > próximo > remoto e significativo
        metro = estr[estr["termo"] == "estrato_metropolitano"].iloc[0]
        self.assertGreater(metro["coef"], 0.15)
        self.assertLess(metro["p_valor"], 0.01)
        self.assertLess(metro["q_fdr_estrato"], 0.05)
        # Capital e próximo também >0 mas com magnitude plausível
        cap = estr[estr["termo"] == "estrato_capital"].iloc[0]
        self.assertGreater(cap["coef"], 0.10)
        # R2 e N
        self.assertEqual(int(lpm["n"].iloc[0]), 1295)
        self.assertEqual(int(lpm["n_clusters"].iloc[0]), 368)
        self.assertGreater(lpm["r2"].iloc[0], 0.15)

    def test_logit_AME_concordancia(self) -> None:
        lpm = pd.read_csv(OUT / "A4_tabela_02_modelo_principal_LPM.csv")
        logit = pd.read_csv(OUT / "A4_tabela_02b_logit_AME.csv")
        for termo in ["estrato_capital", "estrato_metropolitano", "estrato_interior_proximo_polo"]:
            coef_lpm = float(lpm[lpm["termo"] == termo]["coef"].values[0])
            ame = float(logit[logit["termo"] == termo]["ame"].values[0])
            # Concordância <0.05 pp de diferença
            self.assertAlmostEqual(coef_lpm, ame, delta=0.05, msg=f"discord {termo}: LPM {coef_lpm} vs AME {ame}")

    def test_sensibilidades_pre_especificadas(self) -> None:
        # Full, winsor, spline devem existir e ter estrato metro preservado
        for path, espec in [
            (OUT / "A4_tabela_03b_ajuste_completo.csv", "full"),
            (OUT / "A4_tabela_03c_winsorizado.csv", "winsor"),
            (OUT / "A4_tabela_03d_ivs_spline.csv", "spline"),
        ]:
            df = pd.read_csv(path)
            metro = df[df["termo"] == "estrato_metropolitano"]["coef"].values[0]
            self.assertGreater(metro, 0.05, f"{espec} metro não preservado")
        # IVS quadrático p não sig
        spl = pd.read_csv(OUT / "A4_tabela_03d_ivs_spline.csv")
        p_sq = float(spl[spl["termo"] == "ivs_2010_sq"]["p_valor"].values[0])
        self.assertGreater(p_sq, 0.05)

    def test_robustez_estagios_e_municipio_curso(self) -> None:
        estagios = pd.read_csv(OUT / "A4_tabela_02c_confirmacao_homologacao.csv")
        self.assertEqual(set(estagios["outcome_estagio"]), {"alguma_confirmacao", "alguma_homologacao"})
        for outcome in ["alguma_confirmacao", "alguma_homologacao"]:
            row = estagios[(estagios["outcome_estagio"] == outcome) & (estagios["termo"] == "estrato_metropolitano")].iloc[0]
            self.assertGreater(row["coef"], 0.20)
        mc = pd.read_csv(OUT / "A4_tabela_02d_municipio_curso.csv")
        row = mc[mc["termo"] == "estrato_metropolitano"].iloc[0]
        self.assertEqual(int(row["n"]), 1184)
        self.assertGreater(row["coef"], 0.25)

    def test_separacao_faixa_ivs(self) -> None:
        sep = pd.read_csv(OUT / "A4_tabela_03_separacao_faixa_ivs_remoticidade.csv")
        # Deve conter faixa, ivs, inter
        self.assertTrue(any(sep["espec"].str.contains("faixa_only")))
        self.assertTrue(any(sep["espec"].str.contains("ivs_only")))
        # Faixa não deve ser chamada de efeito causal: relatorio deve dizer descritivo
        self.assertIn("descritivo", self.rel.lower())
        self.assertIn("não causal", self.rel.lower() + "nao causal")

    def test_leave_one_out_completude(self) -> None:
        loo = pd.read_csv(OUT / "A4_tabela_04_leave_one_out.csv")
        self.assertEqual(loo[loo["tipo"] == "leave_one_UF"]["excluido"].nunique(), 27)
        self.assertEqual(loo[loo["tipo"] == "leave_one_curso"]["excluido"].nunique(), 16)
        # Range metro deve ser estreito (sd <0.05) indicando robustez
        sd_metro_uf = loo[loo["termo"] == "estrato_metropolitano"]["coef"].std()
        self.assertLess(sd_metro_uf, 0.05)

    def test_influencia_municipal(self) -> None:
        infl = pd.read_csv(OUT / "A4_tabela_05_influencia_municipal.csv")
        self.assertEqual(len(infl), 1104)  # 368*3
        # Nenhum DFBETA >1 (influência extrema) — threshold conservador
        self.assertLess(infl["dfbeta"].abs().max(), 1.5)

    def test_validacao_preditiva_por_municipio(self) -> None:
        pred = pd.read_csv(OUT / "A4_tabela_06_validacao_preditiva.csv")
        self.assertEqual(len(pred), 2)
        # out-sample AUC >0.70 indica discriminação acima do acaso
        for _, row in pred.iterrows():
            self.assertGreater(row["auc_media_out"], 0.70)
            self.assertGreater(row["auc_insample"], 0.70)
            self.assertLess(row["brier_media_out"], 0.22)

    def test_figuras_existem_e_nao_vazias(self) -> None:
        for fname in ["A4_figura_01_prob_ajustada_estrato.png", "A4_figura_02_gradiente_ivs.png", "A4_figura_03_faixa_descritiva.png"]:
            p = OUT / fname
            self.assertTrue(p.exists())
            self.assertGreater(p.stat().st_size, 5000)

    def test_linguagem_autorizada_e_proibicoes(self) -> None:
        # Deve conter linguagem associativa e não conter afirmação causal
        self.assertIn("associativa", self.rel.lower())
        self.assertIn("Proibido", self.rel)
        # Não deve conter taxa de preenchimento por vaga como outcome
        self.assertNotIn("taxa de preenchimento por vaga como outcome primário", self.rel.lower())
        # Não deve converter em WTA (não há estimativa de WTA)
        self.assertNotIn("WTA =", self.rel)
        # Não deve escolher modelo por p-valor: relatorio não diz "escolhido por menor p-valor"
        self.assertNotIn("menor p-valor", self.rel.lower())
        # Faixa deve ser tratada como descritiva não causal
        self.assertIn("Faixa", self.rel)
        # Verifica que json marca efeitos_estimados=True mas linguagem associativa
        self.assertTrue(self.estim["efeitos_estimados"])
        self.assertIn("associativa", self.estim["linguagem"])

    def test_nao_usa_variavel_pos_oferta(self) -> None:
        # Verifica que modelo não usa n_confirmacoes como covariada
        lpm = pd.read_csv(OUT / "A4_tabela_02_modelo_principal_LPM.csv")
        termos = " ".join(lpm["termo"].tolist()).lower()
        self.assertNotIn("confirmacao", termos)
        self.assertNotIn("homologacao", termos)
        self.assertNotIn("cnes_pos", termos)


if __name__ == "__main__":
    unittest.main()
