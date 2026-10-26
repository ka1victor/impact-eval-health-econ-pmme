"""Testes do P1h (protocolo 52b): `scripts/rdd_bolsa/25c_magnitudes_P1h.py`.

Três partes:

1. `TestSintetico`: DADOS SINTÉTICOS gerados em memória (semente fixa), rotulados "sintético"
   (`SINTETICO_TESTE`) e nunca gravados em `output/` nem em `data/`. Conferem a combinação linear (EP pela fórmula
   explícita), o método delta (gradiente contra diferenças finitas e EP explícito), o conjunto de Fieller (pontas
   na igualdade, caso de denominador exato igual ao delta, caso ilimitado, cobertura por Monte Carlo), o portão de
   reprodução (passa com os números iguais e falha com 2e−8 de diferença) e as linhas montadas (Holm, BKY, marcas).
2. `TestSaidasReais`: rótulos de `output/rdd_bolsa/P1h_*`, portão aprovado, estimativas recalculadas dos
   coeficientes publicados no P1, EP, IC, limite unilateral, p, delta e Fieller recalculados da covariância
   gravada no resumo (cujas diagonais batem com os EP do P1), Holm e BKY, hashes, P1 não regravado, sem
   identificador pessoal, sem o arquivo de IVS errado e sem mês CNES ≥ 202609.
3. `TestDoc57i`: o doc 57i é igual ao gerado das saídas e traz a linguagem do protocolo.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import re
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "25c_magnitudes_P1h.py"
_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location("magnitudes_p1h_25c", SCRIPT)
M = importlib.util.module_from_spec(_spec)
sys.modules["magnitudes_p1h_25c"] = M
_spec.loader.exec_module(M)
sys.dont_write_bytecode = _bytecode
L = M.L

OUT = ROOT / "output" / "rdd_bolsa"
CSV = OUT / "P1h_magnitudes.csv"
RESUMO = OUT / "P1h_resumo.json"
FIG = OUT / "P1h_figuras" / "P1h_magnitudes.png"
P1_EST = OUT / "P1_estimativas.csv"
P1_RESUMO = OUT / "P1_resumo.json"
DOC = ROOT / "docs" / "06_execucao" / "57i_resultados_P1h_magnitudes.md"
PROTOCOLO = ROOT / "docs" / "06_execucao" / "52b_protocolo_P1h_magnitudes.md"

NATUREZA_SINTETICA = "SINTETICO_TESTE"   # rótulo dos dados gerados aqui ("sintético"); nunca gravados
Z95 = float(stats.norm.ppf(0.975))
Z90 = float(stats.norm.ppf(0.95))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def fieller_independente(num, den, v_nn, v_dd, v_nd, z):
    """Raízes de (den² − z²v_dd)ρ² − 2(num·den − z²v_nd)ρ + (num² − z²v_nn) = 0 por numpy.roots (sintético e real)."""
    raizes = np.roots([den ** 2 - z ** 2 * v_dd, -2 * (num * den - z ** 2 * v_nd), num ** 2 - z ** 2 * v_nn])
    return float(np.min(raizes.real)), float(np.max(raizes.real))


# ---------------------------------------------------------------------------
# Sintético (só em memória)
# ---------------------------------------------------------------------------

def caso_sintetico(semente: int = 11) -> dict:
    """SINTÉTICO: θ e covariâncias definidas positivas para os cinco termos do P1h e um termo de controle."""
    rng = np.random.default_rng(semente)
    termos = [M.B, "controle_sintetico", M.G, M.UF, M.REG, M.MUN]
    theta = np.array([0.04, 0.3, -0.19, 2.4, 1.6, 0.8])
    out = {"natureza_dos_dados": NATUREZA_SINTETICA, "termos": termos, "theta": theta}
    for nome, escala in (("V_conj", 1.0), ("V_mle", 0.5), ("V_cand", 0.6)):
        A = rng.normal(0, 0.02 * escala, (6, 6))
        out[nome] = A @ A.T + np.diag(np.full(6, 1e-4 * escala))
    return out


def res_sintetico(semente: int = 11) -> dict:
    """SINTÉTICO: um 'resultado de estimação' por especificação do P1h, no formato de P1.estimar."""
    res = {}
    for i, (chave, _, _) in enumerate(M.ESPECS):
        c = caso_sintetico(semente + i)
        res[chave] = {"ok": True, "termos": c["termos"], "theta": c["theta"] + 0.01 * i, "V_conj": c["V_conj"],
                      "V_mle": c["V_mle"], "V_cand": c["V_cand"], "G_conj": 56, "G_cand": 5000, "n_candidatos": 5000,
                      "n_grupos": 5000, "n_linhas": 100000, "n_conjuntos": 56, "natureza_dos_dados": NATUREZA_SINTETICA}
    return res


def csv_p1_sintetico(res: dict) -> pd.DataFrame:
    """SINTÉTICO: o que o P1 teria gravado para `res` (coeficiente e EPs por termo)."""
    linhas = []
    for chave, modelo, ciclo in M.ESPECS:
        r = res[chave]
        for k, t in enumerate(r["termos"]):
            linhas.append({"natureza_dos_dados": NATUREZA_SINTETICA, "modelo": modelo, "ciclo": ciclo,
                           "tipo_linha": "coeficiente", "termo": t, "coef": r["theta"][k],
                           "ep_cluster_conjunto": math.sqrt(r["V_conj"][k, k]), "ep_mle": math.sqrt(r["V_mle"][k, k]),
                           "ep_cluster_candidato": math.sqrt(r["V_cand"][k, k])})
    return pd.DataFrame(linhas)


class TestSintetico(unittest.TestCase):
    """Tudo aqui é sintético, gerado em memória e rotulado SINTETICO_TESTE."""

    def setUp(self) -> None:
        self.c = caso_sintetico()
        self.assertEqual(self.c["natureza_dos_dados"], NATUREZA_SINTETICA)
        self.Vs = {"conj": self.c["V_conj"], "mle": self.c["V_mle"], "cand": self.c["V_cand"]}

    def test_combinacao_linear_d_uf(self) -> None:
        t, th, V = self.c["termos"], self.c["theta"], self.c["V_conj"]
        a = M.vetor(t, {M.UF: 1.0, M.B: -10.0})
        out = M.combinacao_linear(th, self.Vs, a, 56)
        iu, ib = t.index(M.UF), t.index(M.B)
        self.assertAlmostEqual(out["estimativa"], th[iu] - 10 * th[ib], places=14)
        var = V[iu, iu] + 100 * V[ib, ib] - 20 * V[iu, ib]
        self.assertAlmostEqual(out["ep_cluster_conjunto"], math.sqrt(var), places=14)
        ep = out["ep_cluster_conjunto"]
        self.assertAlmostEqual(out["ic95_inf"], out["estimativa"] - Z95 * ep, places=14)
        self.assertAlmostEqual(out["li95_unilateral"], out["estimativa"] - Z90 * ep, places=14)
        self.assertAlmostEqual(out["p_unilateral"], stats.norm.sf(out["estimativa"] / ep), places=14)
        self.assertAlmostEqual(out["p_unilateral_t_g_menos_1"], stats.t.sf(out["estimativa"] / ep, 55), places=14)
        for k, col in (("mle", "ep_mle"), ("cand", "ep_cluster_candidato")):
            Vk = self.Vs[k]
            self.assertAlmostEqual(out[col], math.sqrt(Vk[iu, iu] + 100 * Vk[ib, ib] - 20 * Vk[iu, ib]), places=14)

    def test_p_unilateral_no_limite(self) -> None:
        out = M._inferencia(Z90 * 0.5, {"conj": 0.5, "mle": 0.5, "cand": 0.5}, None)
        self.assertAlmostEqual(out["p_unilateral"], 0.05, places=12)
        self.assertAlmostEqual(out["li95_unilateral"], 0.0, places=12)

    def test_delta_gradiente_e_ep(self) -> None:
        t, th, V = self.c["termos"], self.c["theta"], self.c["V_conj"]
        a = M.vetor(t, {M.B: 500.0})
        b = M.vetor(t, {M.G: -1.0})
        g = M.gradiente_razao(th, a, b)
        f = lambda x: float(a @ x) / float(b @ x)  # noqa: E731
        num = np.array([(f(th + h) - f(th - h)) / 2e-7 for h in np.eye(len(th)) * 1e-7])
        np.testing.assert_allclose(g, num, rtol=1e-6, atol=1e-6)
        out = M.razao_delta(th, self.Vs, a, b, 56)
        ib, ig = t.index(M.B), t.index(M.G)
        beta, gama = th[ib], th[ig]
        self.assertAlmostEqual(out["estimativa"], -500 * beta / gama, places=12)
        gb, gg = -500 / gama, 500 * beta / gama ** 2
        var = gb ** 2 * V[ib, ib] + gg ** 2 * V[ig, ig] + 2 * gb * gg * V[ib, ig]
        self.assertAlmostEqual(out["ep_cluster_conjunto"], math.sqrt(var), places=10)

    def test_fieller_pontas_e_metodo_independente(self) -> None:
        num, den, v_nn, v_dd, v_nd = 2.0, 0.19, 1.3, 0.0002, 0.003
        lo, hi, forma = M.fieller(num, den, v_nn, v_dd, v_nd, Z95)
        self.assertEqual(forma, "limitado")
        self.assertLess(lo, num / den)
        self.assertGreater(hi, num / den)
        for r in (lo, hi):
            self.assertAlmostEqual((num - r * den) ** 2, Z95 ** 2 * (v_nn - 2 * r * v_nd + r ** 2 * v_dd), places=8)
        lo2, hi2 = fieller_independente(num, den, v_nn, v_dd, v_nd, Z95)
        self.assertAlmostEqual(lo, lo2, places=8)
        self.assertAlmostEqual(hi, hi2, places=8)

    def test_fieller_denominador_exato_igual_ao_delta(self) -> None:
        lo, hi, forma = M.fieller(3.0, 2.0, 0.25, 0.0, 0.0, Z95)
        self.assertEqual(forma, "limitado")
        self.assertAlmostEqual(lo, (3.0 - Z95 * 0.5) / 2.0, places=12)
        self.assertAlmostEqual(hi, (3.0 + Z95 * 0.5) / 2.0, places=12)

    def test_fieller_contem_zero_sse_numerador_nao_significante(self) -> None:
        for num in (0.5, 1.0, 1.9, 2.1, 3.0):
            lo, hi, forma = M.fieller(num, 1.0, 1.0, 0.001, 0.0, Z95)
            self.assertEqual(forma, "limitado")
            self.assertEqual(lo <= 0 <= hi, abs(num) <= Z95, num)

    def test_fieller_ilimitado(self) -> None:
        _, _, forma = M.fieller(1.0, 0.1, 0.01, 1.0, 0.0, Z95)       # denominador não significante
        self.assertIn(forma, ("complemento", "reta"))
        lo, hi, forma = M.fieller(0.0, 0.1, 1.0, 1.0, 0.0, Z95)
        self.assertEqual(forma, "reta")
        self.assertTrue(math.isinf(lo) and math.isinf(hi))

    def test_fieller_cobertura_monte_carlo(self) -> None:
        """SINTÉTICO: 4000 pares (num, den) normais com razão verdadeira 1,5; cobertura perto de 95%."""
        rng = np.random.default_rng(20261026)
        Vnn, Vdd, Vnd = 0.09, 0.01, 0.005
        C = np.array([[Vnn, Vnd], [Vnd, Vdd]])
        dados = rng.multivariate_normal([0.6, 0.4], C, 4000)
        cobre = []
        for n_, d_ in dados:
            lo, hi, forma = M.fieller(n_, d_, Vnn, Vdd, Vnd, Z95)
            if forma == "limitado":
                cobre.append(lo <= 1.5 <= hi)
            elif forma == "complemento":
                cobre.append(1.5 <= lo or 1.5 >= hi)
            else:
                cobre.append(True)
        self.assertAlmostEqual(float(np.mean(cobre)), 0.95, delta=0.012)

    def test_portao_passa_e_falha(self) -> None:
        res = res_sintetico()
        csv = csv_p1_sintetico(res)
        self.assertTrue((csv["natureza_dos_dados"] == NATUREZA_SINTETICA).all())
        p = M.portao(res, csv)
        self.assertEqual(p["status"], "PASSOU")
        ruim = csv.copy()
        ruim.loc[(ruim["modelo"] == "M1") & (ruim["termo"] == M.B), "coef"] += 2e-8
        self.assertEqual(M.portao(res, ruim)["status"], "FALHA_REPRODUCAO_M1")
        ruim = csv.copy()
        ruim.loc[(ruim["modelo"] == "M4") & (ruim["termo"] == M.UF), "ep_cluster_conjunto"] += 2e-8
        self.assertEqual(M.portao(res, ruim)["status"], "FALHA_REPRODUCAO_M4")
        ruim = csv[~((csv["modelo"] == "M5") & (csv["ciclo"] == "2") & (csv["termo"] == M.MUN))]
        self.assertEqual(M.portao(res, ruim)["status"], "FALHA_REPRODUCAO_M5_2")
        # Abaixo da tolerância passa.
        ok = csv.copy()
        ok["coef"] += 5e-9
        self.assertEqual(M.portao(res, ok)["status"], "PASSOU")

    def test_linhas_montadas(self) -> None:
        res = res_sintetico()
        est = M.montar_linhas(res)
        est["natureza_dos_dados"] = NATUREZA_SINTETICA          # rótulo do caso sintético; nunca gravado
        self.assertEqual(sorted(est["id_linha"].unique()), ["FIG", "P1h-1", "P1h-2a", "P1h-2b", "P1h-3"])
        self.assertEqual(int((est["id_linha"] == "P1h-3").sum()), len(M.SENSIBILIDADES))
        p1 = est[est["id_linha"] == "P1h-1"].iloc[0]
        self.assertTrue(p1["entra_holm"])
        self.assertAlmostEqual(p1["p_holm"], p1["p_unilateral"], places=15)
        self.assertEqual(bool(p1["rejeita_h0_5pct"]), p1["p_unilateral"] < 0.05)
        s = est[est["id_linha"] == "P1h-3"]
        np.testing.assert_allclose(s["q_bky"].to_numpy(dtype=float),
                                   L.qvalores_bky(s["p_unilateral"].to_numpy(dtype=float)))
        self.assertFalse(est.loc[est["id_linha"] != "P1h-1", "entra_holm"].any())
        self.assertFalse(est.loc[est["id_linha"] != "P1h-3", "entra_bky"].any())
        r1 = res["M1"]
        k5 = est[est["id_linha"] == "P1h-2a"].iloc[0]
        k10 = est[est["id_linha"] == "P1h-2b"].iloc[0]
        beta, gama = r1["theta"][0], r1["theta"][2]
        self.assertAlmostEqual(k5["estimativa"], -500 * beta / gama, places=10)
        self.assertAlmostEqual(k10["estimativa"], 2 * k5["estimativa"], places=10)
        fig = est[est["id_linha"] == "FIG"].set_index("componente")["estimativa"]
        th = dict(zip(r1["termos"], r1["theta"]))
        self.assertAlmostEqual(fig["θ_UF + θ_reg + θ_mun"], th[M.UF] + th[M.REG] + th[M.MUN], places=12)
        self.assertAlmostEqual(fig["−γ"], -th[M.G], places=12)


# ---------------------------------------------------------------------------
# Saídas reais
# ---------------------------------------------------------------------------

def _ler():
    est = pd.read_csv(CSV, dtype={"ciclo": str})
    res = json.loads(RESUMO.read_text(encoding="utf-8"))
    p1 = pd.read_csv(P1_EST, dtype={"ciclo": str})
    return est, res, p1


def _coef_p1(p1: pd.DataFrame, modelo: str, ciclo: str) -> pd.Series:
    g = p1[(p1["modelo"] == modelo) & (p1["ciclo"] == ciclo) & (p1["tipo_linha"] == "coeficiente")]
    return g.set_index("termo")


def _verdadeiro(v) -> bool:
    return str(v).strip().lower() in ("true", "1")


class TestSaidasReais(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.est, cls.res, cls.p1 = _ler()

    def test_rotulos_em_toda_saida(self) -> None:
        self.assertTrue((self.est["natureza_dos_dados"] == "EMPIRICO").all())
        self.assertTrue((self.est["estatuto"] == "PROTOCOLO_52B_POS_RESULTADO").all())
        self.assertEqual(self.res["natureza_dos_dados"], "EMPIRICO")
        self.assertEqual(self.res["estatuto"], "PROTOCOLO_52B_POS_RESULTADO")
        self.assertEqual(list(self.est.columns), M.COLUNAS)
        self.assertFalse(self.est[["estimativa", "ep_cluster_conjunto", "ic95_inf", "ic95_sup", "li95_unilateral",
                                   "p_unilateral"]].isna().any().any())

    def test_portao_aprovado(self) -> None:
        p = self.res["portao"]
        self.assertEqual(p["status"], "PASSOU")
        self.assertEqual(p["tolerancia"], 1e-8)
        self.assertEqual([e["especificacao"] for e in p["especificacoes"]], [k for k, _, _ in M.ESPECS])
        for e in p["especificacoes"]:
            self.assertTrue(e["passou"] and e["mesmos_termos_na_mesma_ordem"], e)
            self.assertLessEqual(e["dif_max_coef"], 1e-8)
            self.assertLessEqual(e["dif_max_ep_cluster_conjunto"], 1e-8)
            self.assertEqual(e["termos_reestimados"], e["termos_gravados"])

    def test_linhas_esperadas(self) -> None:
        cont = self.est["id_linha"].value_counts().to_dict()
        self.assertEqual(cont, {"P1h-1": 1, "P1h-2a": 1, "P1h-2b": 1, "P1h-3": 6, "FIG": 6})
        s = self.est[self.est["id_linha"] == "P1h-3"]
        self.assertEqual(sorted(zip(s["modelo"], s["ciclo"])),
                         sorted((m, c) for k, m, c in M.ESPECS if k != "M1"))

    def test_estimativas_dos_coeficientes_publicados(self) -> None:
        for chave, modelo, ciclo in M.ESPECS:
            g = _coef_p1(self.p1, modelo, ciclo)["coef"]
            idl = "P1h-1" if chave == "M1" else "P1h-3"
            r = self.est[(self.est["id_linha"] == idl) & (self.est["modelo"] == modelo) & (self.est["ciclo"] == ciclo)]
            self.assertEqual(len(r), 1)
            self.assertAlmostEqual(r.iloc[0]["estimativa"], g[M.UF] - 10 * g[M.B], delta=1e-8)
        g = _coef_p1(self.p1, "M1", M.EMPILHADO)["coef"]
        k5 = self.est[self.est["id_linha"] == "P1h-2a"].iloc[0]
        k10 = self.est[self.est["id_linha"] == "P1h-2b"].iloc[0]
        self.assertAlmostEqual(k5["estimativa"], 500 * g[M.B] / -g[M.G], delta=1e-6)
        self.assertAlmostEqual(k10["estimativa"], 1000 * g[M.B] / -g[M.G], delta=1e-6)
        fig = self.est[self.est["id_linha"] == "FIG"].set_index("componente")["estimativa"]
        esperado = {"5β": 5 * g[M.B], "10β": 10 * g[M.B], "−γ": -g[M.G], "θ_UF": g[M.UF],
                    "θ_UF + θ_reg": g[M.UF] + g[M.REG], "θ_UF + θ_reg + θ_mun": g[M.UF] + g[M.REG] + g[M.MUN]}
        for k, v in esperado.items():
            self.assertAlmostEqual(fig[k], v, delta=1e-8, msg=k)

    def test_covariancia_gravada_bate_com_os_ep_do_P1(self) -> None:
        for chave, modelo, ciclo in M.ESPECS:
            c = self.res["covariancias"][chave]
            g = _coef_p1(self.p1, modelo, ciclo)
            for nome, col in (("V_cluster_conjunto", "ep_cluster_conjunto"), ("V_mle", "ep_mle"),
                              ("V_cluster_candidato", "ep_cluster_candidato")):
                V = np.array(c[nome])
                np.testing.assert_allclose(np.sqrt(np.diag(V)), g.loc[c["termos"], col].to_numpy(), atol=1e-8)
                self.assertTrue(np.all(np.linalg.eigvalsh(V) > 0), (chave, nome))
            np.testing.assert_allclose(c["theta"], g.loc[c["termos"], "coef"].to_numpy(), atol=1e-8)

    def test_inferencia_recalculada(self) -> None:
        for _, r in self.est.iterrows():
            ep = r["ep_cluster_conjunto"]
            self.assertAlmostEqual(r["ic95_inf"], r["estimativa"] - Z95 * ep, delta=1e-7 * max(1, abs(r["estimativa"])))
            self.assertAlmostEqual(r["ic95_sup"], r["estimativa"] + Z95 * ep, delta=1e-7 * max(1, abs(r["estimativa"])))
            self.assertAlmostEqual(r["li95_unilateral"], r["estimativa"] - Z90 * ep,
                                   delta=1e-7 * max(1, abs(r["estimativa"])))
            self.assertAlmostEqual(r["p_unilateral"], stats.norm.sf(r["estimativa"] / ep), delta=1e-9)
            self.assertAlmostEqual(r["p_unilateral_t_g_menos_1"], stats.t.sf(r["estimativa"] / ep, r["g_conjuntos"] - 1),
                                   delta=1e-9)
        # D_UF: EP pela covariância gravada (três covariâncias).
        for chave, modelo, ciclo in M.ESPECS:
            c = self.res["covariancias"][chave]
            a = np.zeros(len(c["termos"]))
            a[c["termos"].index(M.UF)], a[c["termos"].index(M.B)] = 1.0, -10.0
            idl = "P1h-1" if chave == "M1" else "P1h-3"
            r = self.est[(self.est["id_linha"] == idl) & (self.est["modelo"] == modelo) &
                         (self.est["ciclo"] == ciclo)].iloc[0]
            for nome, col in (("V_cluster_conjunto", "ep_cluster_conjunto"), ("V_mle", "ep_mle"),
                              ("V_cluster_candidato", "ep_cluster_candidato")):
                self.assertAlmostEqual(r[col], math.sqrt(a @ np.array(c[nome]) @ a), delta=1e-8)

    def test_km_delta_e_fieller_recalculados(self) -> None:
        c = self.res["covariancias"]["M1"]
        t = c["termos"]
        th = np.array(c["theta"])
        V = np.array(c["V_cluster_conjunto"])
        ib, ig = t.index(M.B), t.index(M.G)
        for idl, passo in (("P1h-2a", 5.0), ("P1h-2b", 10.0)):
            r = self.est[self.est["id_linha"] == idl].iloc[0]
            num, den = 100 * passo * th[ib], -th[ig]
            v_nn, v_dd, v_nd = (100 * passo) ** 2 * V[ib, ib], V[ig, ig], -(100 * passo) * V[ib, ig]
            gb, gg = 100 * passo / den, num / den ** 2   # d/dβ e d/dγ de num/den (den = −γ)
            ep = math.sqrt(gb ** 2 * V[ib, ib] + gg ** 2 * V[ig, ig] + 2 * gb * gg * V[ib, ig])
            self.assertAlmostEqual(r["ep_cluster_conjunto"], ep, delta=1e-6)
            lo, hi = fieller_independente(num, den, v_nn, v_dd, v_nd, Z95)
            self.assertAlmostEqual(r["ic95_fieller_inf"], lo, delta=1e-6)
            self.assertAlmostEqual(r["ic95_fieller_sup"], hi, delta=1e-6)
            lo90, _ = fieller_independente(num, den, v_nn, v_dd, v_nd, Z90)
            self.assertAlmostEqual(r["li95_unilateral_fieller"], lo90, delta=1e-6)
            self.assertEqual(r["fieller_forma"], "limitado")
        # §4: se o IC de β contém zero, o de K5 e K10 também (Fieller: equivalência exata).
        b = self.res["beta_M1"]
        if b["ic95_inf"] <= 0 <= b["ic95_sup"]:
            for idl in ("P1h-2a", "P1h-2b"):
                r = self.est[self.est["id_linha"] == idl].iloc[0]
                self.assertTrue(r["ic95_fieller_inf"] <= 0 <= r["ic95_fieller_sup"])
                self.assertTrue(r["ic95_inf"] <= 0 <= r["ic95_sup"])

    def test_holm_e_bky(self) -> None:
        p1 = self.est[self.est["id_linha"] == "P1h-1"]
        self.assertEqual(int(self.est["entra_holm"].sum()), 1)
        self.assertTrue(bool(p1["entra_holm"].iloc[0]))
        self.assertAlmostEqual(p1["p_holm"].iloc[0], p1["p_unilateral"].iloc[0], delta=1e-15)
        self.assertEqual(_verdadeiro(p1["rejeita_h0_5pct"].iloc[0]), p1["p_holm"].iloc[0] < 0.05)
        s = self.est[self.est["id_linha"] == "P1h-3"]
        self.assertTrue(s["entra_bky"].all())
        self.assertEqual(int(self.est["entra_bky"].sum()), len(s))
        np.testing.assert_allclose(s["q_bky"].to_numpy(dtype=float),
                                   L.qvalores_bky(s["p_unilateral"].to_numpy(dtype=float)), atol=1e-12)
        self.assertEqual([_verdadeiro(v) for v in s["rejeita_h0_5pct"]], list(s["q_bky"] < 0.05))
        self.assertTrue(self.est.loc[~self.est["id_linha"].isin(["P1h-1", "P1h-3"]), "rejeita_h0_5pct"].isna().all())
        rp = self.res["resultado_principal"]
        self.assertAlmostEqual(rp["estimativa"], p1["estimativa"].iloc[0], delta=1e-8)
        self.assertEqual(rp["rejeita_h0_5pct"], _verdadeiro(p1["rejeita_h0_5pct"].iloc[0]))

    def test_beta_do_resumo_igual_ao_P1(self) -> None:
        g = _coef_p1(self.p1, "M1", M.EMPILHADO).loc[M.B]
        b = self.res["beta_M1"]
        self.assertAlmostEqual(b["coef"], g["coef"], delta=1e-8)
        self.assertAlmostEqual(b["ic95_inf"], g["ic95_inf"], delta=1e-8)
        self.assertAlmostEqual(b["ic95_sup"], g["ic95_sup"], delta=1e-8)
        self.assertAlmostEqual(b["p_bilateral"], g["p"], delta=1e-8)

    def test_hashes_e_proveniencia(self) -> None:
        self.assertEqual(self.res["protocolo"]["sha256"], sha256(PROTOCOLO))
        for e in self.res["entradas"]:
            self.assertEqual(e["sha256"], sha256(ROOT / e["caminho"]), e["caminho"])
        caminhos = {e["caminho"] for e in self.res["entradas"]}
        for p in ("output/rdd_bolsa/P1_estimativas.csv", "docs/06_execucao/52b_protocolo_P1h_magnitudes.md",
                  "output/aquisicao/a08_ivs_2010_oficial_municipio.csv"):
            self.assertIn(p, caminhos)
        for caminho, h in self.res["saidas"].items():
            self.assertEqual(h, sha256(ROOT / caminho), caminho)
        self.assertEqual(set(self.res["saidas"]), {"output/rdd_bolsa/P1h_magnitudes.csv",
                                                    "output/rdd_bolsa/P1h_figuras/P1h_magnitudes.png"})
        self.assertTrue(FIG.read_bytes().startswith(b"\x89PNG"))
        self.assertEqual(self.res["figura"]["como_ler"], self.res["como_ler"][FIG.name])

    def test_saidas_do_P1_nao_regravadas(self) -> None:
        p1r = json.loads(P1_RESUMO.read_text(encoding="utf-8"))
        for caminho, h in p1r["saidas"].items():
            self.assertEqual(h, sha256(ROOT / caminho), caminho)

    def test_sem_identificador_pessoal(self) -> None:
        proibidos = re.compile(r"cpf|crm|nome|id_candidato|cns_", re.I)
        self.assertFalse([c for c in self.est.columns if proibidos.search(c)])
        texto = RESUMO.read_text(encoding="utf-8") + CSV.read_text(encoding="utf-8")
        self.assertNotRegex(texto, r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b")   # CPF formatado
        # 'id_candidato' só pode aparecer como nome de chave das entradas (proveniência), nunca no CSV.
        self.assertNotIn("id_candidato", CSV.read_text(encoding="utf-8"))
        chaves = set()

        def coletar(o):
            if isinstance(o, dict):
                for k, v in o.items():
                    chaves.add(k)
                    coletar(v)
            elif isinstance(o, list):
                for v in o:
                    coletar(v)
        coletar(self.res)
        self.assertFalse([k for k in chaves if proibidos.search(k)])

    def test_script_sem_ivs_errado_nem_cnes_futuro(self) -> None:
        texto = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("ivs_ipea_2010_municipios", texto)
        self.assertNotRegex(texto, r"(?<!\d)(2026(09|1[0-2])|20(2[7-9]|[3-9]\d)(0[1-9]|1[0-2]))(?!\d)")
        self.assertNotIn("P1_estimativas.csv\").write", texto)
        self.assertNotRegex(texto, r"OUT_EST|OUT_DAP|P1\.OUT_RESUMO|P1\.figuras\(|P1\.main\(")


# ---------------------------------------------------------------------------
# Doc 57i
# ---------------------------------------------------------------------------

class TestDoc57i(unittest.TestCase):

    def test_doc_igual_ao_gerado(self) -> None:
        est, res, _ = _ler()
        self.assertEqual(DOC.read_text(encoding="utf-8"), M.gerar_doc(est, res))

    def test_marcadores(self) -> None:
        t = DOC.read_text(encoding="utf-8")
        for nome in ("portao", "leitura", "tabela", "figura", "desvios"):
            self.assertEqual(t.count(f"<!-- P1h:{nome}:inicio -->"), 1, nome)
            self.assertEqual(t.count(f"<!-- P1h:{nome}:fim -->"), 1, nome)

    def test_secoes_e_linguagem(self) -> None:
        t = DOC.read_text(encoding="utf-8")
        for sec in ("## 1. O que se mede e o que não se pode dizer", "## 2. Amostra e portão de reprodução",
                    "## 3. Leitura em linguagem simples", "## 4. Tabela", "## 5. Figura", "## 7. Limites"):
            self.assertIn(sec, t)
        u = " ".join(t.split()).lower()
        for frase in ("preferência revelada condicional ao modelo", "não é efeito causal da geografia",
                      "pacote do corte", "nada aqui diz se a bolsa \"funciona\" ou \"não funciona\"",
                      "condicional a se candidatar e dentro das vagas abertas", "como ler",
                      "protocolo_52b_pos_resultado", "não é teste confirmatório novo"):
            self.assertIn(frase.lower(), u, frase)
        self.assertNotRegex(u, r"a bolsa (não )?funciona(?!\")")
        self.assertNotIn("efeito causal da origem", u)

    def test_leitura_segue_o_pre_registro(self) -> None:
        est, res, _ = _ler()
        t = " ".join(DOC.read_text(encoding="utf-8").split())
        if res["resultado_principal"]["rejeita_h0_5pct"]:
            self.assertIn("No modelo de escolha, a amplitude inteira da bolsa pesa menos que a vaga ficar na UF de "
                          "origem.", t)
            self.assertIn("Não diz que a bolsa não tem efeito nem que a geografia causa a escolha", t)
        else:
            self.assertIn("inconclusivo", t)
        b = res["beta_M1"]
        if b["ic95_inf"] <= 0 <= b["ic95_sup"]:
            self.assertIn("o IC de K5 e o de K10 também contêm zero", t)
        self.assertIn("não o substitui", t)

    def test_como_ler_e_figura_no_doc(self) -> None:
        _, res, _ = _ler()
        t = DOC.read_text(encoding="utf-8")
        self.assertIn(res["como_ler"][FIG.name], t)
        self.assertIn("../../output/rdd_bolsa/P1h_figuras/P1h_magnitudes.png", t)


if __name__ == "__main__":
    unittest.main()
