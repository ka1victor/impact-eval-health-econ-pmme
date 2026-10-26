"""Testes do protocolo 61 (script 38): por que o preenchimento cai no corte 0,300 (diagnóstico D-a a D-g).

- O doc 57l tem de ser idêntico ao que o script gera a partir de `output/`.
- Os números de `output/rdd_bolsa/DQ_*` são conferidos contra as saídas dos blocos (`N_`, `NA_`, `ND_estimativas`) e
  recalculados onde a conta é simples (p por posto, razões, regra da metade, BKY, identidades).
- Placebo e randomização local são conferidos em casos SINTÉTICOS construídos em memória (rotulados "sintético";
  nada vai para `output/`).
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "rdd_bolsa"
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "38_diagnostico_queda_0300.py"
DOC = ROOT / "docs" / "06_execucao" / "57l_diagnostico_queda_0300.md"
PROTOCOLO = ROOT / "docs" / "06_execucao" / "61_protocolo_diagnostico_queda_0300.md"


def _mod(nome: str, caminho: Path):
    if nome in sys.modules:
        return sys.modules[nome]
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    return mod


DQ = _mod("dq38_teste", SCRIPT)
EST, RESUMO = DQ.ler_saidas()


def _sha(p: Path) -> str:
    return DQ.sha256(p)


class TestSaidas(unittest.TestCase):
    def test_rotulos_e_estatuto(self):
        self.assertEqual(set(EST["natureza_dos_dados"]), {"EMPIRICO"})
        self.assertEqual(set(EST["estatuto"]), {"DIAGNOSTICO_61_POS_RESULTADO"})
        self.assertEqual(RESUMO["natureza_dos_dados"], "EMPIRICO")
        self.assertEqual(RESUMO["estatuto"], "DIAGNOSTICO_61_POS_RESULTADO")
        self.assertEqual(set(EST["rotulo"]), {"PROTOCOLO_61", "COMPLEMENTAR_FORA_DO_PROTOCOLO_61"})
        self.assertFalse(EST["id_linha"].duplicated().any())

    def test_hashes_do_protocolo_das_entradas_e_saidas(self):
        self.assertEqual(RESUMO["protocolo"]["sha256"], _sha(PROTOCOLO))
        for e in RESUMO["entradas"]:
            self.assertEqual(e["sha256"], _sha(ROOT / e["caminho"]), e["caminho"])
        self.assertEqual(RESUMO["saidas"]["DQ_estimativas.csv"]["sha256"], _sha(OUT / "DQ_estimativas.csv"))
        nomes = set()
        for f in RESUMO["saidas"]["figuras"]:
            self.assertEqual(f["sha256"], _sha(ROOT / f["arquivo"]))
            self.assertTrue(f["como_ler"])
            nomes.add(Path(f["arquivo"]).name)
        self.assertEqual(nomes, {"DQ_placebos.png", "DQ_quanto_da_queda.png", "DQ_funil.png"})
        self.assertEqual(set(p.name for p in (OUT / "DQ_figuras").glob("*.png")), nomes)

    def test_sem_identificador_pessoal(self):
        cols = {c.lower() for c in EST.columns}
        self.assertFalse(cols & {"id_candidato", "cpf", "cpf_masc", "nome", "co_profissional_sus"})
        texto = (OUT / "DQ_estimativas.csv").read_text(encoding="utf-8")
        self.assertNotRegex(texto, r"c[123]_\d{5}")   # formato do id_candidato das tabelas de escolha
        self.assertNotIn("CPF_MASC", json.dumps(RESUMO["regra_ciclo2"]["nota_do_quadro_original"]))

    def test_lista_fechada_relatada(self):
        self.assertEqual([e["id"] for e in RESUMO["explicacoes"]], ["D-a", "D-b", "D-c", "D-d", "D-e", "D-f", "D-g"])
        for e in ("D-a", "D-b", "D-c", "D-d", "D-e", "D-f", "D-g"):
            for c in ("0.300", "0.400"):
                self.assertTrue(((EST["explicacao"] == e) & (EST["corte"].str.contains(c, regex=False))).any(), (e, c))

    def test_script_integridade(self):
        src = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("ivs_ipea_2010_municipios", src)
        self.assertNotIn("to_csv(ROOT / \"data", src)
        self.assertEqual(RESUMO["parametros"]["cnes_pre"], ["202406", "202506"])
        info = RESUMO["info_dados"]
        self.assertLess(info["cnes_sus"]["competencias"][-1], "202609")


class TestReproducao(unittest.TestCase):
    def test_q1_q3_batem_com_os_blocos(self):
        n = pd.read_csv(OUT / "N_estimativas.csv", dtype={"corte": str})
        na = pd.read_csv(OUT / "NA_estimativas.csv", dtype={"corte": str})
        nd = pd.read_csv(OUT / "ND_estimativas.csv", dtype={"corte": str})
        rep = EST[EST["tipo_linha"] == "reproducao"]
        self.assertEqual(len(rep), 6)
        for c in ("0.300", "0.400"):
            alvo = {
                "Q1": [n[(n.outcome_id == "N1") & (n.populacao == "V1+V2+V3") & (n.corte == c) & (n.especificacao == "S-a")
                         & (n.variante == "principal")],
                       nd[(nd.diagnostico == "D4") & (nd.amostra == "POR_CORTE") & (nd.corte == c) & (nd.outcome == "N1")
                          & (nd.especificacao == "controle_protocolo_48") & (nd.variante == "principal")]],
                "Q2": [n[(n.outcome_id == "N1") & (n.populacao == "V1+V2+V3") & (n.corte == c) & (n.especificacao == "S-e")],
                       nd[(nd.diagnostico == "D1") & (nd.amostra == "POR_CORTE") & (nd.corte == c)
                          & (nd.outcome == "TAXA_VIC") & (nd.variante == "principal")
                          & (nd.tipo_linha == "estimativa")]],
                "Q3": [na[(na.outcome_id == "A3_PREENCHIDA") & (na.populacao == "V1+V2+V3 (celulas)") & (na.corte == c)
                          & (na.variante == "principal")]],
            }
            for q, dfs in alvo.items():
                r = rep[(rep["quantidade"] == q) & (rep["corte"] == c)].iloc[0]
                for df in dfs:
                    self.assertEqual(len(df), 1, (q, c))
                    for k in ("tau", "ep"):
                        self.assertAlmostEqual(float(r[k]), float(df[k].iloc[0]), delta=1e-9, msg=(q, c, k))
        self.assertLessEqual(RESUMO["validacoes"]["reproducao"]["max_abs_dif"], 1e-9)

    def test_q_original_nas_linhas_fixadas(self):
        rep = EST[EST["tipo_linha"] == "reproducao"].set_index(["quantidade", "corte"])["tau"]
        fx = EST[(EST["tipo_linha"] == "fixado") & (EST["status"] == "EXECUTADO")]
        for _, r in fx.iterrows():
            self.assertAlmostEqual(float(r["tau_original"]), float(rep[(r["quantidade"], r["corte"])]), places=12)


class TestNumerosContraOutput(unittest.TestCase):
    def test_grade_placebo_do_protocolo(self):
        self.assertEqual(DQ.PLACEBOS, (250, 350, 450))
        self.assertEqual(RESUMO["parametros"]["placebos_protocolo_mil"], [250, 350, 450])
        comp = RESUMO["parametros"]["placebos_complementares_mil"]
        self.assertTrue(all(abs(c - k) > 10 for c in comp for k in (300, 400)))

    def test_p_por_posto_recalculado(self):
        for rot in ("PROTOCOLO_61", "COMPLEMENTAR_FORA_DO_PROTOCOLO_61"):
            for q in ("Q1", "Q2", "Q3"):
                ts = EST[(EST["tipo_linha"] == "placebo") & (EST["rotulo"] == rot) & (EST["quantidade"] == q)]["t"]
                ts = ts.astype(float).to_numpy()
                for c in ("0.300", "0.400"):
                    r = EST[(EST["tipo_linha"] == "resumo_placebo") & (EST["rotulo"] == rot) & (EST["quantidade"] == q)
                            & (EST["corte"] == c)].iloc[0]
                    p = (1 + np.sum(np.abs(ts) >= abs(float(r["t"])))) / (1 + len(ts))
                    self.assertAlmostEqual(float(r["p_posto"]), p, places=12)
                    self.assertAlmostEqual(float(r["valor"]), 1 / (1 + len(ts)), places=12)
                    self.assertAlmostEqual(float(r["frac_t_maior_196"]), float(np.mean(np.abs(ts) > 1.96)), places=12)

    def test_razao_e_regra_da_metade(self):
        fx = EST[(EST["tipo_linha"] == "fixado") & (EST["status"] == "EXECUTADO")]
        self.assertGreater(len(fx), 0)
        for _, r in fx.iterrows():
            base = r["tau_original_mesma_amostra"] if pd.notna(r["tau_original_mesma_amostra"]) else r["tau_original"]
            self.assertAlmostEqual(float(r["razao_fixado_original"]), float(r["tau"]) / float(base), places=10)
            esperado = "sim" if abs(float(r["tau"])) <= 0.5 * abs(float(base)) else "nao"
            self.assertEqual(r["reduz_metade"], esperado)

    def test_bky_por_explicacao(self):
        L = DQ.L
        for e in EST["explicacao"].unique():
            m = (EST["explicacao"] == e) & (EST["tipo_linha"] == "salto") & EST["p_valor"].notna() \
                & (EST["rotulo"] == "PROTOCOLO_61")
            if m.sum():
                q = L.qvalores_bky(EST.loc[m, "p_valor"].to_numpy(dtype=float))
                np.testing.assert_allclose(EST.loc[m, "q_bky"].to_numpy(dtype=float), q, atol=1e-12)

    def test_ic_e_p_pela_normal(self):
        from scipy import stats
        s = EST[(EST["tipo_linha"].isin(["salto", "fixado", "reproducao"])) & EST["ep"].notna()
                & (EST["ep"].astype(float) > 0) & (EST["bloco"] != "fisher")]
        z = stats.norm.ppf(0.975)
        np.testing.assert_allclose(s["ic95_inf"], s["tau"] - z * s["ep"], atol=1e-9)
        np.testing.assert_allclose(s["ic95_sup"], s["tau"] + z * s["ep"], atol=1e-9)
        np.testing.assert_allclose(s["p_valor"], 2 * stats.norm.sf(np.abs(s["tau"] / s["ep"])), atol=1e-9)

    def test_identidade_dos_motivos(self):
        for c in ("0.300", "0.400"):
            mot = EST[(EST["bloco"] == "motivos") & (EST["tipo_linha"] == "salto") & (EST["corte"] == c)]
            pfc = EST[(EST["bloco"] == "funil") & (EST["quantidade"] == "P_F_dado_C") & (EST["corte"] == c)
                      & (EST["variante"] == "especificacao_Q3")].iloc[0]
            self.assertAlmostEqual(float(pfc["tau"]), -float(mot["tau"].sum()), delta=1e-9)

    def test_leitura_preregistrada_refeita(self):
        lt = RESUMO["leitura"]
        da = lt["D-a"]
        apoia = all(v > 0.10 for v in da["p_posto_por_q"].values())
        self.assertEqual(da["apoia"], apoia)
        self.assertAlmostEqual(da["p_minimo_possivel"], 1 / (1 + da["n_placebos"]))
        fx = EST[(EST["tipo_linha"] == "fixado") & (EST["corte"] == "0.300") & (EST["reduz_metade"] == "sim")]
        reduz = sorted(set(fx["explicacao"]) | ({"D-f"} if lt["D-f"]["apoia"] else set()))
        self.assertEqual(lt["descritivas_que_reduzem_metade"], reduz)
        df = EST[(EST["explicacao"] == "D-f") & (EST["quantidade"] == "Q2_ciclo2") & (EST["corte"] == "0.300")]
        com = float(df[df["variante"] == "todas_as_celulas"]["tau"].iloc[0])
        sem = float(df[df["variante"] == "sem_celulas_so_cr"]["tau"].iloc[0])
        self.assertEqual(lt["D-f"]["apoia"], abs(sem) <= 0.5 * abs(com))
        esperado = ("ACASO_MAIS_POUCOS_MUNICIPIOS" if apoia else "EXPLICACOES_CANDIDATAS_DESCRITIVAS" if reduz
                    else "SEM_EXPLICACAO_NOS_DADOS")
        self.assertEqual(lt["leitura_principal"], esperado)

    def test_regra_ciclo2_citada_ou_ausencia_registrada(self):
        rc = RESUMO["regra_ciclo2"]
        self.assertEqual(rc["pagina_do_chamamento"]["ocorrencias_de_cadastro_reserva_ou_remanejamento"], 0)
        self.assertEqual(rc["texto_do_edital_3_2026_arquivado"], [])
        self.assertIn("cadastro reserva corresponde", rc["nota_do_quadro_original"]["texto"])

    def test_regras_auditoria_18_tem_ancora(self):
        aud = (ROOT / "docs" / "auditorias" / "18_politicas_nos_mesmos_cortes_ivs.md").read_text(encoding="utf-8")
        for r in DQ.REGRAS_AUDITORIA_18:
            self.assertIn(r["ancora"], aud)


class TestDoc(unittest.TestCase):
    def test_doc_igual_ao_gerado(self):
        self.assertEqual(DOC.read_text(encoding="utf-8"), DQ.gerar_doc(EST, RESUMO))

    def test_secoes_e_linguagem(self):
        t = DOC.read_text(encoding="utf-8")
        for s in ("## 1. Resposta curta", "## 3. D-a", "## 4. D-b", "## 5. D-c", "## 6. D-d", "## 7. D-e", "## 8. D-f",
                  "## 9. D-g", "## 10. Quanto da queda", "## 11. Leitura pré-registrada", "## 12. Figuras",
                  "## 13. Limites", "**Como ler:**", "pacote do corte", "pós-resultado"):
            self.assertIn(s, t)
        baixo = t.lower()
        for proibida in ("a bolsa causa", "a bolsa reduziu", "efeito da bolsa sobre", "a bolsa provoca"):
            self.assertNotIn(proibida, baixo)
        self.assertIn("Nada disso mostra que a bolsa reduz o preenchimento", t)
        self.assertEqual(t.count(":inicio -->"), t.count(":fim -->"))
        self.assertGreaterEqual(t.count(":inicio -->"), 20)
        for f in RESUMO["saidas"]["figuras"]:
            self.assertIn(f["como_ler"], t)


class TestSintetico(unittest.TestCase):
    """Casos sintéticos em memória (rotulados "sintético"); nada vai para output/."""

    @staticmethod
    def _sintetico_municipios(salto: float, semente: int = 1) -> dict:
        # sintético: 3 ciclos, municípios com IVS de 0,200 a 0,500; N1 = 0,3 x vagas + salto em 0,300 + ruído
        rng = np.random.default_rng(semente)
        V = {}
        s = np.arange(200, 501)
        for k in (1, 2, 3):
            vic = rng.integers(1, 10, size=s.size).astype(float)
            n1 = 0.3 * vic + salto * (s > 300) + rng.normal(0, 0.05, size=s.size)
            V[k] = pd.DataFrame({"co_ibge": [f"{900000 + i}" for i in range(s.size)], "s_mil": s.astype(float),
                                 "vagas_imediatas_mais_cr": vic, "n_alocados_ch1": n1, "taxa_vic": n1 / vic})
        return V

    def test_sintetico_placebo_nao_ve_salto_e_corte_real_ve(self):
        V = self._sintetico_municipios(salto=2.0)
        real = DQ.fit_q1(DQ.am_mun(V, 300))
        self.assertAlmostEqual(real["tau"], 2.0, delta=0.1)
        for cp in DQ.PLACEBOS:
            r = DQ.placebo_q("Q1", V, None, cp, segmento=False)
            self.assertLess(abs(r["tau"]), 0.1, cp)
        ts = np.array([DQ.placebo_q("Q1", V, None, cp, segmento=True)["tau"]
                       / DQ.placebo_q("Q1", V, None, cp, segmento=True)["ep"] for cp in DQ.PLACEBOS_COMPLEMENTARES])
        p = DQ.p_posto(real["tau"] / real["ep"], ts)
        self.assertAlmostEqual(p, 1 / (1 + len(ts)))

    def test_sintetico_segmento_nao_atravessa_o_corte(self):
        s = np.arange(200, 501).astype(float)
        m = DQ._segmento(s, 330)
        self.assertTrue(((s[m] > 300) & (s[m] <= 400)).all())
        self.assertTrue((s[DQ._segmento(s, 280)] <= 300).all())
        self.assertTrue((s[DQ._segmento(s, 430)] > 400).all())

    def test_sintetico_p_por_posto(self):
        self.assertAlmostEqual(DQ.p_posto(-2.5, np.array([0.1, -1.0, 3.0])), 2 / 4)
        self.assertAlmostEqual(DQ.p_posto(5.0, np.array([0.1, -1.0, 3.0, np.nan])), 1 / 4)

    def test_sintetico_fisher_estatistica_e_coeficiente_da_mqp(self):
        # sintético: 40 municípios x 2 linhas; estatística = coeficiente de T na MQP com os controles
        rng = np.random.default_rng(7)
        mun = np.repeat(np.arange(40), 2).astype(str)
        t = np.repeat((np.arange(40) >= 20).astype(float), 2)
        g = np.tile([0.0, 1.0], 40)
        X0 = np.column_stack([1 - g, g])
        w = rng.uniform(1, 3, size=80)
        y = 0.5 * t + g + rng.normal(0, 1, size=80)
        r = DQ.fisher_fwl(y, w, X0, mun, t, n_perm=199, semente=(1,))
        X = np.column_stack([X0, t])
        sw = np.sqrt(w)
        beta = np.linalg.lstsq(X * sw[:, None], y * sw, rcond=None)[0]
        self.assertAlmostEqual(r["tau"], beta[-1], places=10)
        self.assertEqual((r["n_abaixo"], r["n_acima"]), (20, 20))

    def test_sintetico_fisher_rejeita_efeito_grande_e_nao_rejeita_nulo(self):
        rng = np.random.default_rng(11)
        mun = np.arange(60).astype(str)
        t = (np.arange(60) >= 30).astype(float)
        X0 = np.ones((60, 1))
        forte = DQ.fisher_fwl(5 * t + rng.normal(0, 1, 60), np.ones(60), X0, mun, t, n_perm=999, semente=(3,))
        self.assertAlmostEqual(forte["p_valor"], 1 / 1000)
        ps = [DQ.fisher_fwl(rng.normal(0, 1, 60), np.ones(60), X0, mun, t, n_perm=199, semente=(i,))["p_valor"]
              for i in range(60)]
        self.assertGreater(np.mean(np.array(ps) > 0.05), 0.8)

    def test_sintetico_fisher_tratamento_tem_de_ser_do_municipio(self):
        mun = np.array(["a", "a", "b", "b"])
        with self.assertRaises(DQ.FalhaValidacao):
            DQ.fisher_fwl(np.arange(4.0), np.ones(4), np.ones((4, 1)), mun, np.array([0, 1, 0, 1.0]), n_perm=9)


if __name__ == "__main__":
    unittest.main()
