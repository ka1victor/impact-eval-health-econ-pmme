"""Teste do pipeline E3 (RDD sharp completa) com DADOS SINTETICOS.

Todos os municipios, escores, covariaveis e outcomes deste modulo sao
SINTETICOS: gerados em memoria com semente fixa, com codigos IBGE ficticios
(prefixo 9, inexistente no IBGE) e saltos conhecidos por construcao. Nada aqui
e observacao empirica. O que e gravado vai para diretorios temporarios; o
proprio `executar` recusa gravar dados nao empiricos em `output/` ou `data/`.

O teste verifica: (1) o estimador local linear com HC1 recupera um salto
conhecido e o EP esta calibrado; (2) o corte pertence ao lado inferior;
(3) a densidade Poisson em mass points detecta manipulacao sintetica e nao
acusa densidade continua; (4) o modo falha-fechado nao le outcome nem
covariavel quando falta escore; (5) com escore completo, os diagnosticos sao
gravados antes de qualquer outcome e o salto sintetico e recuperado.
"""

from __future__ import annotations

import importlib.util
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "07_estimar_E3_rdd_completa.py"
SPEC = importlib.util.spec_from_file_location("e3_rdd_completa", SCRIPT)
E3 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(E3)

SEMENTE = 20261014
NATUREZA = "SINTETICO_TESTE"


def municipios_sinteticos(n: int, inicio: int, rng: np.random.Generator) -> pd.DataFrame:
    """Municipios SINTETICOS: codigo ficticio 9xxxxx e escore uniforme em milesimos."""
    s_mil = rng.integers(150, 651, size=n)
    return pd.DataFrame({
        "co_ibge": [f"{900000 + inicio + i:06d}" for i in range(n)],
        "s_mil": s_mil,
        "ivs_admin": s_mil / 1000,
    })


def populacao_de(mun: pd.DataFrame) -> pd.DataFrame:
    """Faixa anunciada SINTETICA coerente com a regra do protocolo."""
    return pd.DataFrame({
        "co_ibge": mun["co_ibge"],
        "faixa_anunciada": mun["s_mil"].map(E3.faixa_por_mil),
    })


def outcome_binario_sintetico(s_mil: np.ndarray, rng: np.random.Generator,
                              salto_300: float, salto_400: float) -> np.ndarray:
    s = s_mil / 1000
    p = 0.20 + 0.40 * (s - 0.150) + salto_300 * (s_mil > 300) + salto_400 * (s_mil > 400)
    return (rng.random(len(s)) < np.clip(p, 0, 1)).astype(float)


class TestEstimadorLocalLinearSintetico(unittest.TestCase):
    def test_recupera_salto_exato_sem_ruido(self) -> None:
        s = np.arange(200, 501).repeat(3)
        x = (s - 300) / 1000
        t = (s > 300).astype(float)
        y = 0.2 + 1.5 * x + 0.3 * t + 0.8 * t * x
        r = E3.rdd_local_linear(s, y, 300, 50)
        self.assertAlmostEqual(r["tau"], 0.3, places=10)
        self.assertLess(r["ep"], 1e-8)

    def test_corte_pertence_ao_lado_inferior(self) -> None:
        s = np.arange(200, 501)
        r = E3.rdd_local_linear(s, (s > 300).astype(float), 300, 50)
        self.assertAlmostEqual(r["tau"], 1.0, places=10)
        # O ponto s = c entra do lado inferior, com peso maximo.
        self.assertEqual(r["mass_points_abaixo"], 50)
        self.assertEqual(r["mass_points_acima"], 49)  # s = c + h tem peso triangular zero

    def test_recupera_salto_em_outcome_binario(self) -> None:
        rng = np.random.default_rng(SEMENTE)
        mun = municipios_sinteticos(30_000, 0, rng)
        y = outcome_binario_sintetico(mun["s_mil"].to_numpy(), rng, salto_300=0.20, salto_400=0.0)
        r300 = E3.rdd_local_linear(mun["s_mil"], y, 300, 50)
        r400 = E3.rdd_local_linear(mun["s_mil"], y, 400, 50)
        self.assertLess(abs(r300["tau"] - 0.20), 4 * r300["ep"])
        self.assertLess(r300["p_valor"], 0.001)
        self.assertLess(abs(r400["tau"]), 4 * r400["ep"])
        self.assertLessEqual(r300["ic95_inf"], 0.20)
        self.assertGreaterEqual(r300["ic95_sup"], 0.20)

    def test_ep_hc1_calibrado_em_monte_carlo(self) -> None:
        rng = np.random.default_rng(SEMENTE + 1)
        taus, eps = [], []
        for _ in range(300):
            s = rng.integers(200, 501, size=3_000)
            x = (s - 300) / 1000
            ruido = rng.normal(0, 0.5 + 2 * np.abs(x), size=len(s))  # heterocedastico
            y = 1.0 + 2.0 * x + 0.15 * (s > 300) + ruido
            r = E3.rdd_local_linear(s, y, 300, 50)
            taus.append(r["tau"])
            eps.append(r["ep"])
        taus, eps = np.array(taus), np.array(eps)
        self.assertLess(abs(taus.mean() - 0.15), 3 * taus.std() / np.sqrt(len(taus)))
        razao = eps.mean() / taus.std(ddof=1)
        self.assertGreater(razao, 0.85)
        self.assertLess(razao, 1.15)

    def test_suporte_insuficiente_nao_estima(self) -> None:
        s = np.array([300, 300, 301, 302])
        r = E3.rdd_local_linear(s, np.array([0.0, 1.0, 1.0, 0.0]), 300, 50)
        self.assertTrue(np.isnan(r["tau"]))
        self.assertIn("suporte insuficiente", r["nota"])

    def test_covariavel_igual_a_running_variable_nao_e_testada(self) -> None:
        # Com ivs_2010 = escore, o "salto" e zero por construcao e o EP e ruido
        # numerico; o p-valor desse ruido nao pode aparecer como desequilibrio.
        rng = np.random.default_rng(SEMENTE + 2)
        s_mil = rng.integers(200, 501, size=600)
        pop_s = pd.DataFrame({"co_ibge": [f"{i:06d}" for i in range(600)], "s_mil": s_mil})
        cov = pd.DataFrame({"co_ibge": pop_s["co_ibge"], "ivs_2010": s_mil / 1000,
                            "outra": rng.normal(size=600)})
        d = E3.diagnosticos_sem_outcome(pop_s, cov, "SINTETICO")
        bal = d[d["diagnostico"].eq("balanco_covariavel_pre")]
        mec = bal[bal["variavel"].eq("ivs_2010")]
        self.assertEqual(len(mec), len(E3.CORTES_MIL) * len(E3.JANELAS_MIL))
        self.assertTrue(mec["p_valor"].isna().all())
        self.assertTrue(mec["nota"].str.contains("running variable").all())
        self.assertTrue(bal.loc[bal["variavel"].eq("outra"), "p_valor"].notna().all())


class TestDensidadeSintetica(unittest.TestCase):
    def test_densidade_continua_nao_acusa_salto(self) -> None:
        rng = np.random.default_rng(SEMENTE + 2)
        s = rng.integers(150, 651, size=20_000)
        d = E3.densidade_poisson(s, 300, 50)
        self.assertLessEqual(d["rho_ic95_inf"], 1.0)
        self.assertGreaterEqual(d["rho_ic95_sup"], 1.0)

    def test_densidade_manipulada_e_detectada(self) -> None:
        rng = np.random.default_rng(SEMENTE + 3)
        base = rng.integers(150, 651, size=20_000)
        extra = rng.integers(301, 351, size=2_000)  # massa SINTETICA logo acima do corte
        d = E3.densidade_poisson(np.concatenate([base, extra]), 300, 50)
        self.assertGreater(d["rho"], 1.3)
        self.assertLess(d["p_valor"], 0.001)

    def test_mass_points_vazios_entram_na_grade(self) -> None:
        s = np.array([280, 290, 300, 310, 320, 330])
        d = E3.densidade_poisson(s, 300, 50)
        self.assertEqual(d["n_abaixo"], 3)
        self.assertEqual(d["n_acima"], 3)


class TestValidacaoEscoreSintetico(unittest.TestCase):
    def test_tres_casas_decimais_e_milesimos(self) -> None:
        e = E3.validar_escore(pd.DataFrame({"co_ibge": ["9000001", "900002"], "ivs_admin": ["0.300", "0,401"]}))
        self.assertEqual(e["co_ibge"].tolist(), ["900000", "900002"])
        self.assertEqual(e["s_mil"].tolist(), [300, 401])

    def test_quatro_casas_falham(self) -> None:
        with self.assertRaises(E3.EscoreInvalido):
            E3.validar_escore(pd.DataFrame({"co_ibge": ["900001"], "ivs_admin": ["0.3004"]}))

    def test_escore_conflitante_falha(self) -> None:
        with self.assertRaises(E3.EscoreInvalido):
            E3.validar_escore(pd.DataFrame({"co_ibge": ["900001", "900001"], "ivs_admin": ["0.300", "0.301"]}))

    def test_valor_vazio_e_ausencia_nao_zero(self) -> None:
        e = E3.validar_escore(pd.DataFrame({"co_ibge": ["900001", "900002"], "ivs_admin": ["0.300", ""]}))
        self.assertEqual(e["co_ibge"].tolist(), ["900001"])


def leitor_proibido(*_args, **_kwargs):
    raise AssertionError("outcome ou covariavel lido no modo falha-fechado")


class TestFalhaFechadaSintetica(unittest.TestCase):
    def setUp(self) -> None:
        rng = np.random.default_rng(SEMENTE + 4)
        self.m1 = municipios_sinteticos(400, 0, rng)
        self.m2 = municipios_sinteticos(300, 10_000, rng)
        self.pops = {"P1": populacao_de(self.m1), "P2": populacao_de(self.m2)}
        self.escore = pd.concat([self.m1, self.m2], ignore_index=True)[["co_ibge", "ivs_admin", "s_mil"]]

    def test_escore_incompleto_nao_le_outcome(self) -> None:
        parcial = self.escore.iloc[1:]  # falta um municipio de P1
        with tempfile.TemporaryDirectory() as tmp:
            saida = Path(tmp)
            (saida / E3.NOME_ESTIMATIVAS).write_text("estimativa_antiga_sintetica\n", encoding="utf-8")
            st = E3.executar(parcial, self.pops, saida_dir=saida, natureza=NATUREZA,
                             carregar_covariaveis_fn=leitor_proibido, carregar_outcomes_fn=leitor_proibido)
            gravado = json.loads((saida / E3.NOME_STATUS).read_text(encoding="utf-8"))
            self.assertFalse((saida / E3.NOME_ESTIMATIVAS).exists())
            self.assertFalse((saida / E3.NOME_DIAGNOSTICOS).exists())
        self.assertEqual(st["status"], "AGUARDANDO_ESCORE_COMPLETO")
        self.assertEqual(gravado["status"], "AGUARDANDO_ESCORE_COMPLETO")
        self.assertEqual(gravado["natureza_dos_dados"], NATUREZA)
        self.assertFalse(gravado["outcomes_abertos"])
        self.assertEqual(gravado["outcomes_lidos"], [])
        self.assertEqual(gravado["saidas_anteriores_removidas"], [E3.NOME_ESTIMATIVAS])
        self.assertEqual(gravado["cobertura_do_escore"]["P1"]["sem_escore"], 1)
        self.assertFalse(gravado["cobertura_do_escore"]["P1"]["completa"])
        self.assertTrue(gravado["cobertura_do_escore"]["P2"]["completa"])

    def test_falta_so_em_p2_tambem_bloqueia(self) -> None:
        parcial = self.escore[self.escore["co_ibge"] != self.m2["co_ibge"].iloc[0]]
        with tempfile.TemporaryDirectory() as tmp:
            st = E3.executar(parcial, self.pops, saida_dir=Path(tmp), natureza=NATUREZA,
                             carregar_covariaveis_fn=leitor_proibido, carregar_outcomes_fn=leitor_proibido)
        self.assertEqual(st["status"], "AGUARDANDO_ESCORE_COMPLETO")

    def test_regra_nao_reproduzida_nao_le_outcome(self) -> None:
        pops = {k: v.copy() for k, v in self.pops.items()}
        pops["P1"].loc[0, "faixa_anunciada"] = "FAIXA 1" if pops["P1"].loc[0, "faixa_anunciada"] != "FAIXA 1" else "FAIXA 3"
        with tempfile.TemporaryDirectory() as tmp:
            st = E3.executar(self.escore, pops, saida_dir=Path(tmp), natureza=NATUREZA,
                             carregar_covariaveis_fn=leitor_proibido, carregar_outcomes_fn=leitor_proibido)
        self.assertEqual(st["status"], "PRIMEIRO_ESTAGIO_NAO_SHARP")
        self.assertEqual(st["primeiro_estagio"]["P1"]["reproduzidos"], 399)

    def test_sintetico_nao_grava_em_output_nem_data(self) -> None:
        for destino in (ROOT / "output" / "rdd_bolsa", ROOT / "data"):
            with self.assertRaises(ValueError):
                E3.executar(self.escore, self.pops, saida_dir=destino, natureza=NATUREZA,
                            carregar_covariaveis_fn=leitor_proibido, carregar_outcomes_fn=leitor_proibido)


class TestPipelineCompletoSintetico(unittest.TestCase):
    """Escore SINTETICO completo; salto conhecido de +0,25 em 0,300 e nenhum em 0,400."""

    @classmethod
    def setUpClass(cls) -> None:
        rng = np.random.default_rng(SEMENTE + 5)
        m1 = municipios_sinteticos(20_000, 0, rng)
        m2 = municipios_sinteticos(20_000, 50_000, rng)
        escore = pd.concat([m1, m2], ignore_index=True)[["co_ibge", "ivs_admin", "s_mil"]]
        pops = {"P1": populacao_de(m1), "P2": populacao_de(m2)}
        todos = pd.concat([m1, m2], ignore_index=True)
        covariaveis = pd.DataFrame({
            "co_ibge": todos["co_ibge"],
            "covariavel_sintetica_suave": 0.5 * todos["ivs_admin"] + rng.normal(0, 0.05, len(todos)),
        })
        d = {
            "P1": pd.Series(outcome_binario_sintetico(m1["s_mil"].to_numpy(), rng, 0.25, 0.0), index=m1["co_ibge"]),
            "P2": pd.Series(outcome_binario_sintetico(m2["s_mil"].to_numpy(), rng, 0.25, 0.0), index=m2["co_ibge"]),
        }
        cls.diag_existia_ao_ler_outcome = []
        cls.tmp = tempfile.TemporaryDirectory()
        saida = Path(cls.tmp.name)

        def outcomes(nome, municipios):
            cls.diag_existia_ao_ler_outcome.append((saida / E3.NOME_DIAGNOSTICOS).exists())
            itens = [{"outcome": E3.OUTCOME_D, "ciclo": int(nome[1]), "serie": d[nome].loc[list(municipios)],
                      "fonte": "SINTETICO"}]
            if nome == "P1":
                itens.append({"outcome": E3.OUTCOME_PREENCHIMENTO, "ciclo": 1, "serie": None,
                              "motivo": "SINTETICO: outcome pendente de proposito"})
            return itens

        cls.status = E3.executar(
            escore, pops, saida_dir=saida, natureza=NATUREZA,
            carregar_covariaveis_fn=lambda: (covariaveis, {"covariaveis": "SINTETICAS"}),
            carregar_outcomes_fn=outcomes,
        )
        cls.diag = pd.read_csv(saida / E3.NOME_DIAGNOSTICOS)
        cls.est = pd.read_csv(saida / E3.NOME_ESTIMATIVAS)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def test_diagnosticos_gravados_antes_dos_outcomes(self) -> None:
        self.assertEqual(self.diag_existia_ao_ler_outcome, [True, True])

    def test_status_registra_pendencia_sem_esconder(self) -> None:
        self.assertEqual(self.status["status"], "CONCLUIDO_COM_OUTCOME_PENDENTE")
        pend = [s for s in self.status["outcomes_lidos"] if not s["estimado"]]
        self.assertEqual([p["outcome"] for p in pend], [E3.OUTCOME_PREENCHIMENTO])
        self.assertTrue(all(self.status["primeiro_estagio"][k]["sharp"] for k in ("P1", "P2")))

    def test_saidas_rotuladas_como_sinteticas(self) -> None:
        self.assertEqual(set(self.diag["natureza_dos_dados"]), {NATUREZA})
        self.assertEqual(set(self.est["natureza_dos_dados"]), {NATUREZA})

    def test_todas_as_especificacoes_relatadas(self) -> None:
        # 2 populacoes x 1 outcome estimado x 2 cortes x 3 janelas
        self.assertEqual(len(self.est), 12)
        self.assertEqual(sorted(self.est["h"].unique()), [0.03, 0.05, 0.08])

    def test_recupera_salto_sintetico_em_0300(self) -> None:
        for pop in ("P1", "P2"):
            r = self.est[(self.est["populacao"] == pop) & (self.est["corte"] == 0.3) & (self.est["h"] == 0.05)].iloc[0]
            self.assertLess(abs(r["tau"] - 0.25), 4 * r["ep"], pop)
            self.assertLess(r["p_valor"], 0.001, pop)

    def test_sem_salto_sintetico_em_0400(self) -> None:
        for pop in ("P1", "P2"):
            r = self.est[(self.est["populacao"] == pop) & (self.est["corte"] == 0.4) & (self.est["h"] == 0.05)].iloc[0]
            self.assertLess(abs(r["tau"]), 4 * r["ep"], pop)

    def test_diagnosticos_sem_outcome(self) -> None:
        tipos = set(self.diag["diagnostico"])
        self.assertEqual(tipos, {"suporte", "densidade_poisson_mass_points", "balanco_covariavel_pre"})
        dens = self.diag[(self.diag["diagnostico"] == "densidade_poisson_mass_points") & (self.diag["h"] == 0.05)]
        self.assertEqual(len(dens), 4)
        bal = self.diag[(self.diag["diagnostico"] == "balanco_covariavel_pre") & (self.diag["h"] == 0.05)]
        self.assertTrue((bal["tau"].abs() < 4 * bal["ep"]).all())


class TestLeituraOutcomesSintetica(unittest.TestCase):
    def _zip(self, pasta: Path, linhas: list[str]) -> Path:
        cab = 'co_ibge;co_cnes;"nome";crm;ciclo;"municipio"'
        conteudo = "\n".join([cab] + linhas).encode("latin1")
        caminho = pasta / "ativos_sinteticos.zip"
        with zipfile.ZipFile(caminho, "w") as z:
            z.writestr("ativos_sinteticos.csv", conteudo)
        return caminho

    def test_le_so_co_ibge_e_ciclo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            zp = self._zip(Path(tmp), [
                '9000017;1;"PESSOA FICTICIA A";1;1;"X"',
                '900002;2;"PESSOA FICTICIA B";2;Ciclo 2;"Y"',
                '900003;3;"PESSOA FICTICIA C";3;2.0;"Z"',
            ])
            a = E3.ler_ativos(zp)
        self.assertEqual(list(a.columns), ["co_ibge", "ciclo_k"])
        self.assertEqual(sorted(a.itertuples(index=False, name=None)), [("900001", 1), ("900002", 2), ("900003", 2)])
        d1 = E3.construir_d_k(pd.Series(["900001", "900002", "900009"]), a, 1)
        self.assertEqual(d1.to_dict(), {"900001": 1.0, "900002": 0.0, "900009": 0.0})

    def test_ciclo_nao_reconhecido_falha(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            zp = self._zip(Path(tmp), ['900001;1;"PESSOA FICTICIA";1;2025;"X"'])
            with self.assertRaises(ValueError):
                E3.ler_ativos(zp)

    def test_preenchimento_por_municipio_definicao_a4(self) -> None:
        funil = pd.DataFrame({
            "chamada": [1, 1, 1, 1, 1, 2],
            "in_quadro_ch1_original": [True, True, True, False, True, None],
            "co_ibge_6d": ["900001", "900001", "900002", "900002", "900003", "900003"],
            "co_cnes_7d": ["0000001", "0000002", "0000003", "0000004", "0000005", "0000005"],
            "cod_curso": [1, 1, 2, 2, 3, 3],
            "outcome_alguma_confirmacao_ou_homologacao": [1, 0, 0, 1, 1, 0],
        })
        frac = E3.preenchimento_ch1_por_municipio(funil, pd.Series(["900001", "900002", "900003"]))
        self.assertEqual(frac.to_dict(), {"900001": 0.5, "900002": 0.0, "900003": 1.0})
        with self.assertRaises(ValueError):
            E3.preenchimento_ch1_por_municipio(funil, pd.Series(["900001", "900002", "900003", "900004"]))


if __name__ == "__main__":
    unittest.main()
