"""Testes do adendo 52f: `scripts/rdd_bolsa/52_robustez_E9_ciclo2_quadro_1302.py`.

Partes:

1. `TestSintetico`: DADOS SINTÉTICOS gerados em memória, rotulados `SINTETICO_TESTE` e nunca gravados. Conferem o
   portão (passa com números iguais, falha com 2e−8, linha sem par), a regra do §3 (MANTEM, REBAIXAR,
   PLACEBO_NAO_CONFIRMA), a classificação das linhas em peças, a família BKY, os critérios de leitura e a razão de
   chances.
2. `TestPortaoReal`: a versão antiga gravada em `RB_estimativas.csv` bate, linha a linha, com `E9_estimativas.csv`,
   `E9_efeitos_marginais.csv` e `E9_robustez_pos_auditoria.csv`, e o resumo registra o portão aprovado.
3. `TestNumeros`: rótulos e hashes; IC, p, razão de chances, CV3, placebos e BKY recalculados das linhas; mesma
   amostra no conjunto principal e conjunto só com vaga imediata refeito; correção conferida contra a auditoria 36;
   leitura e mudanças refeitas; integridade.
4. `TestDoc57y`: o doc 57y é igual ao gerado, tem os marcadores, nenhum número de resultado fora dos blocos, a
   linguagem pedida, e o bloco de decisões é igual ao do commit de pré-registro.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import re
import subprocess
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "52_robustez_E9_ciclo2_quadro_1302.py"
_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location("robustez_E9_ciclo2_quadro_1302_52", SCRIPT)
M = importlib.util.module_from_spec(_spec)
sys.modules["robustez_E9_ciclo2_quadro_1302_52"] = M
_spec.loader.exec_module(M)
sys.dont_write_bytecode = _bytecode

OUT = ROOT / "output" / "rdd_bolsa"
CSV = OUT / "RB_estimativas.csv"
RESUMO = OUT / "RB_resumo.json"
FIG = OUT / "RB_figuras" / "RB_antigo_corrigido.png"
DOC = ROOT / "docs" / "06_execucao" / "57y_robustez_E9_ciclo2_quadro_1302.md"
A36 = ROOT / "output" / "auditoria_H1" / "a36_celulas.csv"
COMMIT_PRE_REGISTRO = "2f7deba"
NATUREZA_SINTETICA = "SINTETICO_TESTE"
TOL = 1e-8
B = M.B


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def ler_csv(p: Path) -> pd.DataFrame:
    return pd.read_csv(p, dtype={"ciclo": str})


def dif_rel(a, b) -> float:
    """Escrita no teste, sem a função do script: absoluta até 1, relativa acima; NaN só com NaN."""
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    assert (np.isnan(a) == np.isnan(b)).all(), "NaN em só um dos lados"
    ok = ~np.isnan(a)
    return float(np.max(np.abs(a[ok] - b[ok]) / np.maximum(1.0, np.abs(b[ok])))) if ok.any() else 0.0


# ---------------------------------------------------------------------------
# 1. Sintético (só em memória)
# ---------------------------------------------------------------------------

def _est_sintetico(rng) -> pd.DataFrame:
    linhas = []
    for ciclo in ("2", "empilhado"):
        for espec in (M.ESPEC, f"{M.TAG}:spline_cubico__bolsa_linear", f"{M.TAG}:placebo_0250__spline_linear__bolsa_linear"):
            for termo in ("bolsa_mil", "ivs_inclinacao"):
                linhas.append({c: np.nan for c in M.ORDEM_EST} |
                              {"natureza_dos_dados": NATUREZA_SINTETICA, "ciclo": ciclo, "conjunto": "principal",
                               "modelo": M.COND, "especificacao": espec, "termo": termo, "coef": rng.normal(0, 0.3),
                               "ep_cluster_conjunto": rng.uniform(0.01, 0.1), "log_verossimilhanca": -812.3456789})
    return pd.DataFrame(linhas)[M.ORDEM_EST]


class TestSintetico(unittest.TestCase):
    """Tudo aqui é sintético, gerado em memória e rotulado SINTETICO_TESTE."""

    def setUp(self) -> None:
        rng = np.random.default_rng(52)
        self.est = _est_sintetico(rng)
        self.efe = pd.DataFrame({"natureza_dos_dados": NATUREZA_SINTETICA, "ciclo": ["2"], "conjunto": ["principal"],
                                 "modelo": [M.COND], "papel_no_protocolo": [""], "n_candidatos": [10],
                                 "n_conjuntos": [2], "n_alternativas": [5], "especificacao": [M.ESPEC],
                                 "termo": [B], "quantidade": ["razao_chances_por_5mil"], "estimativa": [1.5],
                                 "ep_cluster_conjunto": [0.1], "ep_mle": [0.05], "ic95_inf": [1.1], "ic95_sup": [2.0],
                                 "metodo_ic": [""], "nota": [""]})
        self.rob = pd.DataFrame([M.E9._linha_rob("placebo_cortes", "2", "p_posto", 0.036, p=0.036),
                                 M.E9._linha_rob("score_bootstrap_rademacher_cluster_conjunto", "2", "p_H0_beta_igual_0",
                                                 0.001, p=0.001, g=16, n_reamostras=65536)])
        self.v = {"est": self.est, "efe": self.efe, "rob": self.rob}

    def test_portao_passa_com_numeros_iguais(self) -> None:
        p = M.portao(self.v, self.est.copy(), self.efe.copy(), self.rob.copy())
        self.assertEqual(p["status"], "PASSOU")
        self.assertTrue(all(x["passou"] for x in p["linhas"]))
        grupos = {x["linha"] for x in p["linhas"]}
        self.assertIn("est:placebos", grupos)
        self.assertIn("est:forma_funcional_e_janelas", grupos)

    def test_portao_falha_com_2e_8(self) -> None:
        g = self.est.copy()
        g.loc[0, "coef"] += 2e-8
        self.assertTrue(M.portao(self.v, g, self.efe, self.rob)["status"].startswith("FALHA_REPRODUCAO_"))
        r = self.rob.copy()
        r.loc[1, "p"] += 2e-8
        self.assertTrue(M.portao(self.v, self.est, self.efe, r)["status"].startswith("FALHA_REPRODUCAO_rob"))

    def test_portao_relativo_acima_de_1(self) -> None:
        g = self.est.copy()
        g.loc[0, "log_verossimilhanca"] += 5e-7      # relativa ≈ 6e−10: passa
        self.assertEqual(M.portao(self.v, g, self.efe, self.rob)["status"], "PASSOU")

    def test_portao_falha_com_linha_sem_par(self) -> None:
        g = self.est.copy()
        g.loc[0, "termo"] = "outro"
        self.assertNotEqual(M.portao(self.v, g, self.efe, self.rob)["status"], "PASSOU")
        self.assertNotEqual(M.portao(self.v, self.est.iloc[1:], self.efe, self.rob)["status"], "PASSOU")

    def test_regra_do_par3(self) -> None:
        self.assertEqual(M.regra_rb(0.001, 0.002, 0.001, 0), ("MANTEM", []))
        self.assertEqual(M.regra_rb(0.001, 0.002, 0.001, 1), ("PLACEBO_NAO_CONFIRMA", []))
        regra, caiu = M.regra_rb(0.001, 0.06, 0.001, 0)
        self.assertEqual(regra, "REBAIXAR")
        self.assertEqual(caiu, ["score bootstrap Webb"])
        regra, caiu = M.regra_rb(0.05, 0.002, float("nan"), 0)
        self.assertEqual(caiu, ["score bootstrap Rademacher", "CV3"])

    def test_classificacao(self) -> None:
        self.assertEqual(M.classificar_est(M.COND, "principal", M.ESPEC)[0], "ref-52c")
        self.assertEqual(M.classificar_est(M.COND, "sensibilidade", M.ESPEC)[0], "ref-52d")
        self.assertEqual(M.classificar_est(M.COND, "sensibilidade", "spline_quadratico__bolsa_linear")[0], "RB-4")
        self.assertEqual(M.classificar_est(M.EXPL, "principal", M.ESPEC)[0], "RB-5")
        self.assertEqual(M.classificar_est(M.COND, "principal", "spline_linear__degraus_por_corte")[0], "RB-5")
        self.assertEqual(M.classificar_est(M.COND, "principal", f"{M.TAG}:placebo_0250__x")[0], "RB-2")
        self.assertEqual(M.classificar_est(M.COND, "principal", f"{M.TAG}:janela_0050__spline_cubico__bolsa_linear")[0],
                         "RB-3")
        self.assertEqual(M.classificar_rob("cv3_cluster_conjunto", M.COND, "principal", M.ESPEC)[0], "RB-1")
        self.assertEqual(M.classificar_rob("cluster_curso", M.COND, "principal", M.ESPEC)[0], "RB-1")
        self.assertEqual(M.classificar_rob("cluster_curso", M.EXPL, "principal", M.ESPEC)[0], "RB-5")
        self.assertEqual(M.classificar_rob("cluster_curso", M.COND, "sensibilidade", M.ESPEC)[0], "RB-4")
        self.assertEqual(M.classificar_rob("heterogeneidade_ciclos", M.COND, "principal", M.ESPEC)[0], "apoio")
        self.assertEqual(M.papel("RB-1", "2"), "principal")
        self.assertEqual(M.papel("RB-1", "empilhado"), "secundaria")
        self.assertEqual(M.papel("ref-52c", "2"), "apoio")

    def test_familia_bky(self) -> None:
        base = {"papel": "secundaria", "p": 0.01, "fonte": "E9_estimativas", "id_rb": "RB-3", "termo": B,
                "analise": "", "estatistica": "coeficiente"}
        self.assertTrue(M.entra_bky(pd.Series(base)))
        self.assertFalse(M.entra_bky(pd.Series({**base, "termo": M.TESTE_DEGRAUS})))
        self.assertFalse(M.entra_bky(pd.Series({**base, "id_rb": "RB-2"})))       # coeficiente dentro do placebo
        self.assertFalse(M.entra_bky(pd.Series({**base, "papel": "principal"})))
        self.assertFalse(M.entra_bky(pd.Series({**base, "p": np.nan})))
        rob = {**base, "fonte": "E9_robustez_pos_auditoria", "id_rb": "RB-2", "analise": "placebo_cortes"}
        self.assertTrue(M.entra_bky(pd.Series({**rob, "estatistica": "p_posto"})))
        self.assertFalse(M.entra_bky(pd.Series({**rob, "estatistica": "t_real"})))
        self.assertFalse(M.entra_bky(pd.Series({**rob, "analise": "ic_inversao_score_rademacher_cluster_curso"})))
        self.assertTrue(M.entra_bky(pd.Series({**rob, "analise": "cv3_cluster_curso"})))

    def test_criterios_e_rc(self) -> None:
        r = pd.Series({"fonte": "E9_estimativas", "estatistica": "coeficiente", "ic95_inf": 0.01, "ic95_sup": 0.2,
                       "p": 0.01, "analise": ""})
        self.assertEqual(M.criterio(r), ("IC 95% exclui 0 (cluster por conjunto)", True, True))
        r = pd.Series({"fonte": "E9_robustez_pos_auditoria", "analise": "placebo_cortes", "p": 0.107,
                       "ic95_inf": np.nan, "ic95_sup": np.nan})
        self.assertEqual(M.criterio(r), ("p por posto < 0,05", False, False))
        rc = M._rc("bolsa_mil", 0.1, 0.05, 0.15)
        self.assertAlmostEqual(rc["rc_por_5mil"], math.exp(0.5))
        self.assertAlmostEqual(M._rc("degrau_0300", 0.6, 0.3, 0.9)["rc_ic95_inf"], math.exp(0.3))
        self.assertEqual(M._rc("ivs_inclinacao", 0.1, 0.0, 0.2), {})


# ---------------------------------------------------------------------------
# 2. Portão real
# ---------------------------------------------------------------------------

class TestPortaoReal(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.est = M.ler_est()
        cls.resumo = json.loads(RESUMO.read_text(encoding="utf-8"))
        cls.ant = cls.est[cls.est["versao"] == M.ANTIGA]

    def test_resumo_registra_portao_aprovado(self) -> None:
        p = self.resumo["portao"]
        self.assertEqual(p["status"], "PASSOU")
        self.assertEqual(p["tolerancia"], TOL)
        fontes = {x["fonte"] for x in p["linhas"]}
        self.assertEqual(fontes, {"E9_estimativas", "E9_efeitos_marginais", "E9_robustez_pos_auditoria"})
        n = {f: 0 for f in fontes}
        for linha in p["linhas"]:
            self.assertTrue(linha["passou"], linha)
            self.assertTrue(linha["todas_casadas"], linha)
            n[linha["fonte"]] += linha["linhas_gravadas"]
            for k, v in linha.items():
                if k.startswith("dif_max_"):
                    self.assertLessEqual(v, TOL, (linha["linha"], k))
        self.assertEqual(n["E9_estimativas"], len(ler_csv(OUT / "E9_estimativas.csv")))
        self.assertEqual(n["E9_efeitos_marginais"], len(ler_csv(OUT / "E9_efeitos_marginais.csv")))
        self.assertEqual(n["E9_robustez_pos_auditoria"], len(ler_csv(OUT / "E9_robustez_pos_auditoria.csv")))

    def test_estimativas_antigas_iguais_as_gravadas(self) -> None:
        g = ler_csv(OUT / "E9_estimativas.csv")
        g = g[g["ciclo"].isin(M.CICLOS_QUE_MUDAM)].copy()
        g["especificacao"] = g["especificacao"].str.replace(f"{M.TAG}:", "", regex=False)
        a = self.ant[self.ant["fonte"] == "E9_estimativas"]
        self.assertEqual(len(a), len(g))
        m = a.merge(g, on=["ciclo", "conjunto", "modelo", "especificacao", "termo"], suffixes=("", "_g"),
                    validate="one_to_one")
        self.assertEqual(len(m), len(g))
        for ca, cg in (("estimativa", "coef"), ("ep", "ep_cluster_conjunto"), ("ic95_inf", "ic95_inf_g"),
                       ("ic95_sup", "ic95_sup_g"), ("p", "p_g"), ("n_candidatos", "n_candidatos_g")):
            self.assertLessEqual(dif_rel(m[ca], m[cg]), TOL, ca)

    def test_robustez_antiga_igual_a_gravada(self) -> None:
        g = ler_csv(OUT / "E9_robustez_pos_auditoria.csv")
        g = g[g["ciclo"].isin(M.CICLOS_QUE_MUDAM + ("1,2,3", "2 vs 3"))]
        a = self.ant[self.ant["fonte"] == "E9_robustez_pos_auditoria"]
        self.assertEqual(len(a), len(g))
        m = a.merge(g.rename(columns={"especificacao": "esp_rot"}), left_on=["analise", "ciclo", "modelo", "conjunto",
                                                                             "especificacao", "termo", "estatistica"],
                    right_on=["analise", "ciclo", "modelo", "conjunto", "especificacao_base", "termo", "estatistica"],
                    suffixes=("", "_g"), validate="one_to_one")
        self.assertEqual(len(m), len(g))
        for ca, cg in (("estimativa", "valor"), ("ep", "ep_g"), ("ic95_inf", "ic95_inf_g"), ("ic95_sup", "ic95_sup_g"),
                       ("p", "p_g"), ("n_reamostras", "n_reamostras_g")):
            self.assertLessEqual(dif_rel(m[ca], m[cg]), TOL, ca)


# ---------------------------------------------------------------------------
# 3. Números contra output/
# ---------------------------------------------------------------------------

class TestNumeros(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.est = M.ler_est()
        cls.resumo = json.loads(RESUMO.read_text(encoding="utf-8"))

    def test_rotulos_e_hashes(self) -> None:
        self.assertTrue((self.est["natureza_dos_dados"] == "EMPIRICO").all())
        self.assertTrue((self.est["estatuto"] == "ADENDO_52F_POS_RESULTADO").all())
        self.assertEqual(self.resumo["natureza_dos_dados"], "EMPIRICO")
        self.assertEqual(self.resumo["estatuto"], "ADENDO_52F_POS_RESULTADO")
        self.assertEqual(set(self.est["versao"]), set(M.VERSOES))
        self.assertEqual(self.resumo["adendo"]["sha256"], sha256(M.ADENDO_MD))
        for caminho, h in self.resumo["saidas"].items():
            self.assertEqual(sha256(ROOT / caminho), h, caminho)
        for e in self.resumo["entradas"]:
            self.assertEqual(sha256(ROOT / e["caminho"]), e["sha256"], e["caminho"])
        caminhos = {e["caminho"] for e in self.resumo["entradas"]}
        for s in ("12_construir_outcomes_funil.py", "16_estimar_E9_escolha.py", "17_ponte_pmme_cnes.py",
                  "19_escolha_heterogeneidade.py", "42_escolha_vaga_imediata_c2.py",
                  "48_sensibilidades_ciclo2_quadro_1302.py", "rdd_lib.py"):
            self.assertIn(f"scripts/rdd_bolsa/{s}", caminhos)
        self.assertTrue({"RB-1", "RB-2", "RB-3", "RB-4", "RB-5"} <= set(self.est["id_rb"]))
        self.assertEqual(set(self.est["ciclo"]), {"2", "empilhado", "1,2,3", "2 vs 3"})

    def test_saidas_antigas_nao_regravadas(self) -> None:
        texto = SCRIPT.read_text(encoding="utf-8")
        for alvo in ("to_csv(E9_", "to_csv(VC_", "to_csv(VD_", "E9_EST.write", "E9_ROB.write", "E9_EFE.write",
                     "VC_CSV.write", "VD_CSV.write", "to_csv(E9.", "VL_estimativas", "VL_resumo"):
            self.assertNotIn(alvo, texto)
        self.assertNotIn("E9.main(", texto)

    def test_principal_unica(self) -> None:
        p = self.est[self.est["papel"] == "principal"]
        self.assertTrue((p["id_rb"] == "RB-1").all())
        self.assertTrue((p["ciclo"] == "2").all())
        self.assertEqual(set(p["analise"]), {"score_bootstrap_rademacher_cluster_conjunto",
                                             "score_bootstrap_webb_cluster_conjunto", "cv3_cluster_conjunto",
                                             "ic_inversao_score_rademacher_cluster_conjunto"})
        self.assertFalse(p["entra_bky"].any())

    def test_coeficientes_ic_p_e_rc(self) -> None:
        z = stats.norm.ppf(0.975)
        c = self.est[(self.est["fonte"] == "E9_estimativas") & (self.est["estatistica"] == "coeficiente") &
                     self.est["estimativa"].notna()]
        np.testing.assert_allclose(c["ic95_inf"], c["estimativa"] - z * c["ep"], atol=1e-8)
        np.testing.assert_allclose(c["p"], 2 * stats.norm.sf(np.abs(c["estimativa"] / c["ep"])), atol=1e-8)
        for termo, f in (("bolsa_mil", 5.0), ("degrau_0300", 1.0), ("degrau_0400", 1.0)):
            s = self.est[(self.est["termo"] == termo) & self.est["rc_por_5mil"].notna()]
            self.assertGreater(len(s), 0)
            np.testing.assert_allclose(s["rc_por_5mil"], np.exp(f * s["estimativa"]), rtol=1e-8)
            np.testing.assert_allclose(s["rc_ic95_inf"], np.exp(f * s["ic95_inf"]), rtol=1e-8)

    def test_cv3_ic_pela_t(self) -> None:
        s = self.est[self.est["analise"].str.startswith("cv3_")]
        for r in s.itertuples(index=False):
            tq = stats.t.ppf(0.975, r.g - 1)
            self.assertAlmostEqual(r.ic95_inf, r.estimativa - tq * r.ep, delta=1e-8)
            self.assertAlmostEqual(r.p, 2 * stats.t.sf(abs(r.estimativa / r.ep), r.g - 1), delta=1e-8)

    def test_placebos_recalculados(self) -> None:
        for v in M.VERSOES:
            for ciclo in M.CICLOS_QUE_MUDAM:
                pl = self.est[(self.est["versao"] == v) & (self.est["ciclo"] == ciclo) & (self.est["id_rb"] == "RB-2") &
                              (self.est["fonte"] == "E9_estimativas") & (self.est["termo"] == "degrau_placebo")]
                t = (pl["estimativa"] / pl["ep"]).to_numpy()
                t = t[np.isfinite(t)]
                g = lambda s: M._rob(self.est, v, "placebo_cortes", ciclo, s)["estimativa"]  # noqa: E731
                principal = M._coef(self.est, v, ciclo, M.COND, "principal", M.ESPEC)
                t_real = principal["estimativa"] / principal["ep"]
                self.assertAlmostEqual(g("t_real"), t_real, delta=1e-6)
                n = int((np.abs(t) >= abs(g("t_real"))).sum())
                self.assertEqual(int(g("n_abs_t_placebo_maior_ou_igual_ao_real")), n)
                self.assertEqual(int(g("n_placebos")), len(t))
                self.assertAlmostEqual(g("p_posto"), (1 + n) / (1 + len(t)), delta=1e-9)

    def test_bky_refeito(self) -> None:
        for v in M.VERSOES:
            f = self.est[(self.est["versao"] == v) & self.est["entra_bky"]]
            self.assertGreater(len(f), 20)
            np.testing.assert_allclose(f["q_bky"].to_numpy(), M.L.qvalores_bky(f["p"].to_numpy()), atol=1e-12)
            self.assertTrue(f["papel"].eq("secundaria").all())
            self.assertTrue(self.est[(self.est["versao"] == v) & ~self.est["entra_bky"]]["q_bky"].isna().all())
        a = self.est[(self.est["versao"] == M.ANTIGA) & self.est["entra_bky"]][M.CHAVE_RB].astype(str)
        c = self.est[(self.est["versao"] == M.CORRIGIDA) & self.est["entra_bky"]][M.CHAVE_RB].astype(str)
        self.assertEqual(sorted(map(tuple, a.to_numpy())), sorted(map(tuple, c.to_numpy())))

    def test_amostras_e_ciclos_sem_mudanca(self) -> None:
        am = self.resumo["amostras"]
        for chave in ("2|principal|" + M.COND, "empilhado|principal|" + M.COND, "2|principal|" + M.EXPL):
            self.assertEqual(am[M.ANTIGA][chave], am[M.CORRIGIDA][chave], chave)
        self.assertEqual(am[M.ANTIGA]["2|principal|" + M.COND], 2140)
        cc = self.resumo["conferencias"]["marca_dos_candidatos"]
        self.assertEqual(am[M.CORRIGIDA]["2|sensibilidade|" + M.COND], cc["primeiras_opcoes_com_vaga_imediata_13fev"])
        self.assertEqual(am[M.ANTIGA]["2|sensibilidade|" + M.COND], cc["primeiras_opcoes_com_vaga_imediata_19mar"])
        sm = self.resumo["ciclos_sem_mudanca"]
        for fonte in ("est", "efe", "rob"):
            self.assertGreater(sm[fonte]["linhas"], 0)
            self.assertLessEqual(sm[fonte]["dif_max"], TOL)
        for v in M.VERSOES:
            for chave, d in self.resumo["conferencia_vc_vd"][v].items():
                self.assertLessEqual(d, TOL, (v, chave))

    def test_correcao_contra_auditoria_36(self) -> None:
        a = pd.read_csv(A36)
        a = a[a["ciclo"] == 2]
        s = self.resumo["correcao"]["sensibilidade_ciclo2"]
        self.assertEqual(s["celulas_13fev"], int((a["vagas_imediatas_13fev"] > 0).sum()))
        self.assertEqual(s["celulas_19mar"], int((a["vagas_imediatas_pipe_versao"] > 0).sum()))
        self.assertEqual(s["vagas_imediatas_13fev"], float(a["vagas_imediatas_13fev"].sum()))
        cv = self.resumo["correcao"]["conjunto_principal_ciclo2"]
        self.assertEqual(cv["imputadas"], 0)
        self.assertEqual(cv["celulas_sem_linha_no_quadro_1302"], 0)
        self.assertEqual(self.resumo["conferencias"]["quadro_1302_contra_a36"]["celulas_com_vagas_imediatas_diferentes"],
                         0)

    def test_leitura_e_mudancas_refeitas(self) -> None:
        self.assertEqual(M.P1._nan_none(M.mudancas(self.est)), self.resumo["mudancas"])
        self.assertEqual(M.P1._nan_none(M.leitura(self.est)), self.resumo["leitura"])
        lei = self.resumo["leitura"]
        for v in M.VERSOES:
            ps = [lei[v]["p_score_rademacher"], lei[v]["p_score_webb"], lei[v]["p_cv3"]]
            n = lei[v]["RB2_n_placebos_com_abs_t_maior_ou_igual"]
            esperado = ("REBAIXAR" if any(p >= 0.05 for p in ps) else "MANTEM" if n == 0 else "PLACEBO_NAO_CONFIRMA")
            self.assertEqual(lei[v]["regra"], esperado, v)
        self.assertEqual(lei[M.ANTIGA]["regra"], "MANTEM")  # o original: "como no original"
        self.assertEqual(lei["frase_doc44"], {"MANTEM": "CONTINUA_VALENDO", "REBAIXAR": "REBAIXAR",
                                              "PLACEBO_NAO_CONFIRMA": "VALE_SO_POUCOS_CLUSTERS"}[lei[M.CORRIGIDA]["regra"]])

    def test_integridade(self) -> None:
        texto = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("ivs_ipea_2010_municipios", texto)
        self.assertNotIn("data/ivs", texto)
        for col in self.est.columns:
            self.assertNotRegex(col.lower(), r"cpf|nome|crm|id_candidato")
        corpo = CSV.read_text(encoding="utf-8").lower()
        for padrao in ("cpf", "c1_0", "c2_0", "c3_0"):
            self.assertNotIn(padrao, corpo)
        self.assertNotIn("id_candidato\":", RESUMO.read_text(encoding="utf-8"))

    def test_figura_com_como_ler(self) -> None:
        self.assertTrue(FIG.exists())
        self.assertEqual(self.resumo["figura"]["sha256"], sha256(FIG))
        self.assertTrue(self.resumo["figura"]["como_ler"])
        self.assertIn("**Como ler.**", DOC.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# 4. Doc 57y
# ---------------------------------------------------------------------------

BLOCOS = ("resposta", "portao", "decisoes", "correcao", "rb1", "rb2", "rb3", "rb4", "rb5", "bky", "mudancas", "figura")


def _bloco(t: str, nome: str) -> str:
    ini = t.index(f"<!-- RB:{nome}:inicio -->") + len(f"<!-- RB:{nome}:inicio -->\n")
    return t[ini:t.index(f"\n<!-- RB:{nome}:fim -->")]


class TestDoc57y(unittest.TestCase):
    def test_doc_igual_ao_gerado(self) -> None:
        self.assertEqual(DOC.read_text(encoding="utf-8"), M.gerar_doc(M.ler_est(), M.ler_resumo()))

    def test_marcadores_e_cabecalho(self) -> None:
        t = DOC.read_text(encoding="utf-8")
        for nome in BLOCOS:
            self.assertEqual(t.count(f"<!-- RB:{nome}:inicio -->"), 1, nome)
            self.assertEqual(t.count(f"<!-- RB:{nome}:fim -->"), 1, nome)
        for s in ("## 1. Resposta curta", "## 2. Portão", "## 3. Decisões de implementação", "## 7. Limites",
                  "`ADENDO_52F_POS_RESULTADO`",
                  "> **Auditoria:** [auditoria 54](../auditorias/54_auditoria_robustez_E9_ciclo2.md)", "> **Gerado por**",
                  "52f_adendo_robustez_E9_ciclo2_quadro_1302.md"):
            self.assertIn(s, t)
        self.assertLess(t.index("<!-- RB:decisoes:fim -->"), t.index("## 4. A correção"))

    def test_nenhum_numero_de_resultado_fora_dos_blocos(self) -> None:
        t = DOC.read_text(encoding="utf-8")
        fora = re.sub(r"<!-- RB:(\w+):inicio -->.*?<!-- RB:\1:fim -->", "", t, flags=re.S)
        fora = "\n".join(x for x in fora.splitlines() if not x.startswith("#"))
        self.assertEqual(re.findall(r"\d+,\d+", fora), [])
        self.assertEqual(re.findall(r"\d+\.\d+", fora), [])

    def test_frase_do_doc44_e_linguagem(self) -> None:
        t = " ".join(DOC.read_text(encoding="utf-8").split())
        r = " ".join(_bloco(DOC.read_text(encoding="utf-8"), "resposta").split())
        frase = {"CONTINUA_VALENDO": "continua valendo com o tipo de vaga anterior à alocação",
                 "REBAIXAR": "deve ser rebaixada para o ciclo 2",
                 "VALE_SO_POUCOS_CLUSTERS": "vale só pela metade"}[M.ler_resumo()["leitura"]["frase_doc44"]]
        self.assertIn(frase, r)
        self.assertIn("robusto a poucos *clusters* e a placebos", r)
        self.assertIn("Em linguagem simples", r)
        self.assertIn("preferência revelada, não efeito causal", t)
        self.assertIn("pacote do corte", t)
        self.assertIn("Não é efeito da participação no PMM-E", t)
        self.assertNotIn("a bolsa funciona", t.lower())
        # Auditoria 54: folga dos placebos, spline cúbico com as janelas e leitura do q do BKY.
        self.assertIn("O p por posto não mede a folga", r)
        self.assertIn("especificações com spline cúbico no ciclo 2", r)
        bky = " ".join(_bloco(DOC.read_text(encoding="utf-8"), "bky").split())
        self.assertIn("Como ler o q (auditoria 54)", bky)
        self.assertIn("A leitura do §3 não usa o q", bky)

    def test_decisoes_iguais_as_do_pre_registro(self) -> None:
        t = DOC.read_text(encoding="utf-8")
        self.assertEqual(_bloco(t, "decisoes"), M.texto_decisoes())
        self.assertTrue(all(d["data"] == "2026-10-27" for d in M.DECISOES))
        try:
            pre = subprocess.run(["git", "show", f"{COMMIT_PRE_REGISTRO}:docs/06_execucao/{DOC.name}"], cwd=ROOT,
                                 capture_output=True, text=True, check=True).stdout
        except (OSError, subprocess.CalledProcessError):
            self.skipTest("histórico do Git sem o commit de pré-registro")
        self.assertEqual(_bloco(pre, "decisoes"), _bloco(t, "decisoes"))
        self.assertNotIn("RB:resposta", pre)  # o pré-registro não tinha resultado


if __name__ == "__main__":
    unittest.main()
