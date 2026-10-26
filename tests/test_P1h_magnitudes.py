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
4. `TestRecalculoIndependenteAuditoria31`: monta a amostra do P1 das entradas do protocolo 52 §2 e reestima o
   logit condicional com código próprio (sem importar os scripts 16, 17, 19, 25 nem 25c, nem a rdd_lib), com EP
   sanduíche CR1 (G/(G−1)) por conjunto; compara com `P1_estimativas.csv` e refaz D_UF, K5, K10 (delta e Fieller)
   e os pesos da figura contra `P1h_magnitudes.csv`. Por padrão, M1 e M5 ciclo 1; com `AUDITORIA31_TODAS=1`, as
   sete especificações (M1, M2, M4, M5 por ciclo, M7) e o BKY do P1h-3.
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


# ---------------------------------------------------------------------------
# Auditoria 31: recálculo independente (código próprio, sem os scripts 16, 17, 19, 25, 25c nem a rdd_lib)
# ---------------------------------------------------------------------------

def _a31_insumos() -> dict:
    """Entradas do protocolo 52 §2, lidas com leitores próprios. Só leitura; nada é gravado."""
    O = ROOT / "output"
    conj = pd.read_parquet(O / "rdd_bolsa" / "outcomes" / "escolhas_conjunto_principal.parquet")
    cand = pd.read_parquet(O / "rdd_bolsa" / "outcomes" / "escolhas_candidatos.parquet")
    org = pd.read_parquet(O / "rdd_bolsa" / "G1_candidatos_origem.parquet")
    ivs = pd.read_csv(O / "aquisicao" / "a08_ivs_2010_oficial_municipio.csv", dtype={"co_ibge": str},
                      usecols=["co_ibge", "ivs"])
    ivs = ivs.assign(co_ibge=ivs["co_ibge"].str.zfill(6)).set_index("co_ibge")["ivs"]
    cir = {}
    bruto = (ROOT / "data" / "raw" / "aquisicao" / "territorio" / "datasus_tabnet_br_regsaud.cnv").read_bytes()
    for ln in bruto.decode("latin1").splitlines()[1:]:
        m = re.match(r"^\s*\d+\s+(\d{5})\s+.*?\s+(\d{6})\s*$", ln)
        if m:
            cir[m.group(2)] = m.group(1)
    cir = pd.Series(cir)
    js = json.loads((ROOT / "data" / "raw" / "aquisicao" / "territorio" /
                     "ibge_api_v3_malhas_metadados_municipios.json").read_text(encoding="utf-8"))
    xy = pd.DataFrame({"co": [str(d["id"])[:6] for d in js], "lon": [d["centroide"]["longitude"] for d in js],
                       "lat": [d["centroide"]["latitude"] for d in js]}).set_index("co")
    c = conj.copy()
    c["ivs"] = c["co_ibge"].map(ivs)
    c = c[c["ivs"].notna()].copy()
    c["s"] = np.round(c["ivs"] * 1000)
    c["bolsa_mil"] = c["faixa_anunciada"].map({"FAIXA 3": 10.0, "FAIXA 2": 15.0, "FAIXA 1": 20.0})
    regra = np.where(c["s"] > 400, "FAIXA 1", np.where(c["s"] > 300, "FAIXA 2", "FAIXA 3"))
    assert (regra == c["faixa_anunciada"]).all()
    c["cir"] = c["co_ibge"].map(cir)
    sem_cir = set(zip(c.loc[c["cir"].isna(), "ciclo"], c.loc[c["cir"].isna(), "co_cnes_7d"],
                      c.loc[c["cir"].isna(), "cod_curso"]))
    c = c[c["cir"].notna()].reset_index(drop=True)
    c["cel_id"] = np.arange(len(c))
    A = pd.DataFrame({"bolsa_mil": c["bolsa_mil"], "ivs_inclinacao": (c["s"] - 300) / 100.0,
                      "ivs_mudanca_inclinacao_0300": np.maximum(c["s"] - 300, 0) / 100.0,
                      "ivs_mudanca_inclinacao_0400": np.maximum(c["s"] - 400, 0) / 100.0,
                      "tem_vaga_imediata": c["tem_vaga_imediata"].astype(float),
                      "log_vagas_imediatas_mais_1": c["log_vagas_imediatas_mais_1"].astype(float),
                      "log_populacao_2022": np.log(c["populacao_2022"].astype(float))})
    for nome in sorted(c["macrorregiao"].unique()):
        if nome != "SUDESTE":
            A["macro_" + nome.lower().replace(" ", "_")] = (c["macrorregiao"] == nome).astype(float)
    for e in sorted(c["estrato_territorial"].unique()):
        if e != "interior_proximo_polo":
            A["capital" if e == "capital" else "estrato_" + e] = (c["estrato_territorial"] == e).astype(float)
    o = org[org["regra_ligacao"] == "g1_cpf_nome"][["ciclo", "id_candidato", "co_ibge_origem"]]
    r1 = cand[cand["opcao_rank"] == 1].merge(o, on=["ciclo", "id_candidato"], how="left", validate="one_to_one")
    r1 = r1[r1["co_ibge_origem"].notna()].copy()
    r1["co_ibge_origem"] = r1["co_ibge_origem"].astype(str)
    r1 = r1[r1["co_ibge_origem"].isin(cir.index)]
    r1 = r1[[k not in sem_cir for k in zip(r1["ciclo"], r1["co_cnes_7d"], r1["cod_curso"])]].copy()
    chave = c.set_index(["ciclo", "co_cnes_7d", "cod_curso"])["cel_id"]
    r1["cel_esc"] = chave.reindex(pd.MultiIndex.from_frame(r1[["ciclo", "co_cnes_7d", "cod_curso"]])).to_numpy()
    r2 = cand[(cand["opcao_rank"] == 2) & cand["id_candidato"].isin(set(r1["id_candidato"]))]
    r2 = r2[[k not in sem_cir for k in zip(r2["ciclo"], r2["co_cnes_7d"], r2["cod_curso"])]].copy()
    r2["cel_esc"] = chave.reindex(pd.MultiIndex.from_frame(r2[["ciclo", "co_cnes_7d", "cod_curso"]])).to_numpy()
    assert r1["cel_esc"].notna().all() and r2["cel_esc"].notna().all()
    return {"c": c, "A": A, "cir": cir, "xy": xy, "r1": r1, "r2": r2,
            "uf_base": c["co_ibge"].str[:2].value_counts().sort_index().idxmax()}


def _a31_estimar(I: dict, ciclos: tuple, modelo: str, com_r2: bool) -> dict:
    c, r1, r2 = I["c"], I["r1"], I["r2"]
    g1 = r1[r1["ciclo"].isin(ciclos)][["id_candidato", "id_conjunto_escolha", "co_ibge_origem", "cel_esc"]].copy()
    g1["excl"], g1["posto"] = -1, 1
    gs = [g1]
    if com_r2:
        g2 = r2[r2["ciclo"].isin(ciclos)][["id_candidato", "id_conjunto_escolha", "cel_esc"]].copy()
        i1 = g1.set_index("id_candidato")
        g2["co_ibge_origem"] = g2["id_candidato"].map(i1["co_ibge_origem"])
        mesmo = g2["id_conjunto_escolha"].to_numpy() == g2["id_candidato"].map(i1["id_conjunto_escolha"]).to_numpy()
        g2["excl"] = np.where(mesmo, g2["id_candidato"].map(i1["cel_esc"]).to_numpy(), -1)
        g2["posto"] = 2
        gs.append(g2)
    g = pd.concat(gs, ignore_index=True)
    g["gid"] = np.arange(len(g))
    lg = g.merge(c[["id_conjunto_escolha", "cel_id"]], on="id_conjunto_escolha")
    lg = lg[lg["cel_id"] != lg["excl"]].sort_values(["gid", "cel_id"]).reset_index(drop=True)
    y = (lg["cel_id"] == lg["cel_esc"]).to_numpy(float)
    cel = lg["cel_id"].to_numpy()
    X = I["A"].iloc[cel].reset_index(drop=True).copy()
    uf_c = c["co_ibge"].str[:2].to_numpy()
    if modelo == "M4":
        X = X.drop(columns=[k for k in X.columns if k.startswith("macro_")])
        for u in sorted(set(uf_c)):
            if u != I["uf_base"]:
                X["uf_" + u] = (uf_c[cel] == u).astype(float)
    oc, cc = lg["co_ibge_origem"].to_numpy(), c["co_ibge"].to_numpy()[cel]
    rad = lambda s, k: np.radians(I["xy"].loc[s, k].to_numpy())  # noqa: E731
    h = (np.sin((rad(cc, "lat") - rad(oc, "lat")) / 2) ** 2 + np.cos(rad(oc, "lat")) * np.cos(rad(cc, "lat")) *
         np.sin((rad(cc, "lon") - rad(oc, "lon")) / 2) ** 2)
    dist = 2 * 6371.0088 * np.arcsin(np.sqrt(np.clip(h, 0, 1)))
    if modelo == "M2":
        X["log1p_distancia_km"] = np.log1p(dist)
    else:
        X["distancia_100km"] = dist / 100.0
    X["mesma_uf"] = (np.array([s[:2] for s in oc]) == np.array([s[:2] for s in cc])).astype(float)
    X["mesma_regiao_saude"] = (I["cir"].reindex(oc).to_numpy() == I["cir"].reindex(cc).to_numpy()).astype(float)
    X["mesmo_municipio"] = (oc == cc).astype(float)
    gid = lg["gid"].to_numpy()
    nG = len(g)
    Xm = X.to_numpy(float)
    amp = np.zeros(Xm.shape[1])
    for j in range(Xm.shape[1]):
        mx, mn = np.full(nG, -np.inf), np.full(nG, np.inf)
        np.maximum.at(mx, gid, Xm[:, j])
        np.minimum.at(mn, gid, Xm[:, j])
        amp[j] = np.max(mx - mn)
    termos = [t for t, a in zip(X.columns, amp) if a > 0]
    Xm = X[termos].to_numpy(float)
    k = Xm.shape[1]

    def aval(b):
        v = Xm @ b
        vm = np.full(nG, -np.inf)
        np.maximum.at(vm, gid, v)
        ev = np.exp(v - vm[gid])
        den = np.bincount(gid, ev, nG)
        p = ev / den[gid]
        xbar = np.column_stack([np.bincount(gid, p * Xm[:, j], nG) for j in range(k)])
        xesc = np.column_stack([np.bincount(gid, y * Xm[:, j], nG) for j in range(k)])
        H = (Xm * p[:, None]).T @ Xm - xbar.T @ xbar
        return float(y @ v - np.sum(vm + np.log(den))), xesc - xbar, H

    b = np.zeros(k)
    for _ in range(100):
        ll, sc, H = aval(b)
        passo = np.linalg.solve(H, sc.sum(0))
        if sc.sum(0) @ passo < 1e-20:
            break
        t = 1.0
        while aval(b + t * passo)[0] < ll - 1e-10 and t > 1e-8:
            t /= 2
        b = b + t * passo
    ll, sc, H = aval(b)
    Hi = np.linalg.inv(H)

    def cr1(cl):
        cod, idx = np.unique(cl, return_inverse=True)
        S = np.zeros((len(cod), k))
        np.add.at(S, idx, sc)
        return len(cod) / (len(cod) - 1) * Hi @ (S.T @ S) @ Hi, len(cod)

    Vc, Gc = cr1(g["id_conjunto_escolha"].to_numpy())
    Vk, _ = cr1(g["id_candidato"].to_numpy())
    return {"termos": termos, "theta": b, "V_conj": Vc, "V_mle": Hi, "V_cand": Vk, "G": Gc, "n_linhas": len(lg)}


class TestRecalculoIndependenteAuditoria31(unittest.TestCase):
    """Recálculo da auditoria 31 com código próprio; compara com P1_estimativas.csv e P1h_magnitudes.csv."""

    ESPECS = {"M1": ((1, 2, 3), "M1", False, "M1", "empilhado"), "M2": ((1, 2, 3), "M2", False, "M2", "empilhado"),
              "M4": ((1, 2, 3), "M4", False, "M4", "empilhado"), "M5_1": ((1,), "M1", False, "M5", "1"),
              "M5_2": ((2,), "M1", False, "M5", "2"), "M5_3": ((3,), "M1", False, "M5", "3"),
              "M7": ((1, 2, 3), "M1", True, "M7", "empilhado")}

    @classmethod
    def setUpClass(cls) -> None:
        import os
        cls.todas = os.environ.get("AUDITORIA31_TODAS") == "1"
        chaves = list(cls.ESPECS) if cls.todas else ["M1", "M5_1"]
        I = _a31_insumos()
        cls.res = {kk: _a31_estimar(I, *cls.ESPECS[kk][:3]) for kk in chaves}
        cls.p1 = pd.read_csv(P1_EST, dtype={"ciclo": str})
        cls.p1h = pd.read_csv(CSV, dtype={"ciclo": str})

    def _comb(self, r: dict, pesos: dict, V: str = "V_conj") -> tuple[float, float]:
        a = np.zeros(len(r["termos"]))
        for t, w in pesos.items():
            a[r["termos"].index(t)] = w
        return float(a @ r["theta"]), math.sqrt(float(a @ r[V] @ a))

    def test_coeficientes_e_ep_contra_P1(self) -> None:
        for kk, r in self.res.items():
            m, ci = self.ESPECS[kk][3:]
            g = self.p1[(self.p1["modelo"] == m) & (self.p1["ciclo"] == ci) &
                        (self.p1["tipo_linha"] == "coeficiente")].set_index("termo")
            self.assertEqual(list(g.index), r["termos"], kk)
            self.assertEqual(int(g["n_linhas_candidato_celula"].iloc[0]), r["n_linhas"], kk)
            np.testing.assert_allclose(r["theta"], g["coef"].to_numpy(), rtol=0, atol=1e-7, err_msg=kk)
            for V, col in (("V_conj", "ep_cluster_conjunto"), ("V_mle", "ep_mle"), ("V_cand", "ep_cluster_candidato")):
                np.testing.assert_allclose(np.sqrt(np.diag(r[V])), g[col].to_numpy(), rtol=1e-6, err_msg=f"{kk} {V}")

    def _linha(self, id_linha: str, m: str, ci: str, comp: str | None = None) -> pd.Series:
        s = self.p1h[(self.p1h["id_linha"] == id_linha) & (self.p1h["modelo"] == m) & (self.p1h["ciclo"] == ci)]
        if comp is not None:
            s = s[s["componente"] == comp]
        self.assertEqual(len(s), 1)
        return s.iloc[0]

    def test_d_uf_e_pesos_da_figura(self) -> None:
        z, zu = stats.norm.ppf(0.975), stats.norm.ppf(0.95)
        alvos = [("P1h-1", kk, None, {"mesma_uf": 1, "bolsa_mil": -10}) for kk in ["M1"]]
        alvos += [("P1h-3", kk, None, {"mesma_uf": 1, "bolsa_mil": -10}) for kk in self.res if kk != "M1"]
        alvos += [("FIG", "M1", comp, p) for comp, p in (
            ("5β", {"bolsa_mil": 5}), ("10β", {"bolsa_mil": 10}), ("−γ", {"distancia_100km": -1}),
            ("θ_UF", {"mesma_uf": 1}), ("θ_UF + θ_reg", {"mesma_uf": 1, "mesma_regiao_saude": 1}),
            ("θ_UF + θ_reg + θ_mun", {"mesma_uf": 1, "mesma_regiao_saude": 1, "mesmo_municipio": 1}))]
        ps = {}
        for id_linha, kk, comp, pesos in alvos:
            r = self.res[kk]
            e, s = self._comb(r, pesos)
            g = self._linha(id_linha, *self.ESPECS[kk][3:], comp)
            got = [e, s, self._comb(r, pesos, "V_mle")[1], self._comb(r, pesos, "V_cand")[1], e - z * s, e + z * s,
                   e - zu * s, stats.norm.sf(e / s), stats.t.sf(e / s, r["G"] - 1)]
            ref = g[["estimativa", "ep_cluster_conjunto", "ep_mle", "ep_cluster_candidato", "ic95_inf", "ic95_sup",
                     "li95_unilateral", "p_unilateral", "p_unilateral_t_g_menos_1"]].to_numpy(float)
            np.testing.assert_allclose(got, ref, rtol=1e-6, atol=1e-12, err_msg=f"{id_linha} {kk} {comp}")
            if id_linha == "P1h-3":
                ps[kk] = stats.norm.sf(e / s)
        if self.todas:  # BKY (Anderson, 2008) refeito à mão sobre as seis linhas
            ordem = ["M2", "M4", "M5_1", "M5_2", "M5_3", "M7"]
            p = np.array([ps[kk] for kk in ordem])
            m = len(p)
            q = np.ones(m)
            rk = np.arange(1, m + 1)
            o = np.argsort(p)
            for i in range(1000, 0, -1):
                qq = i / 1000
                q1 = qq / (1 + qq)
                ok1 = p[o] <= q1 * rk / m
                R1 = rk[ok1].max() if ok1.any() else 0
                q2 = q1 * m / (m - R1) if R1 < m else np.inf
                ok2 = p[o] <= q2 * rk / m
                R2 = rk[ok2].max() if ok2.any() else 0
                q[o[:R2]] = qq
            for kk, qv in zip(ordem, q):
                self.assertAlmostEqual(qv, float(self._linha("P1h-3", *self.ESPECS[kk][3:])["q_bky"]), places=9)

    def test_km_delta_e_fieller(self) -> None:
        r = self.res["M1"]
        ib, ig = r["termos"].index("bolsa_mil"), r["termos"].index("distancia_100km")
        b, gm, V = r["theta"][ib], r["theta"][ig], r["V_conj"]
        for id_linha, passo in (("P1h-2a", 5.0), ("P1h-2b", 10.0)):
            g = self._linha(id_linha, "M1", "empilhado")
            K = 100 * passo * b / (-gm)
            grad = np.zeros(len(r["theta"]))
            grad[ib], grad[ig] = 100 * passo / (-gm), 100 * passo * b / gm ** 2
            s = math.sqrt(grad @ V @ grad)
            # Fieller: (a + K·γ)² ≤ z²·Var(a + K·γ), a = 100·passo·β
            a, vaa, vgg, vag = 100 * passo * b, (100 * passo) ** 2 * V[ib, ib], V[ig, ig], 100 * passo * V[ib, ig]
            pontas = {}
            for nome, z in (("95", stats.norm.ppf(0.975)), ("90", stats.norm.ppf(0.95))):
                qa, qb, qc = gm ** 2 - z ** 2 * vgg, 2 * (a * gm - z ** 2 * vag), a ** 2 - z ** 2 * vaa
                self.assertGreater(qa, 0)  # conjunto limitado
                d = math.sqrt(qb ** 2 - 4 * qa * qc)
                pontas[nome] = sorted([(-qb - d) / (2 * qa), (-qb + d) / (2 * qa)])
            got = [K, s, K - stats.norm.ppf(0.975) * s, K + stats.norm.ppf(0.975) * s, K - stats.norm.ppf(0.95) * s,
                   stats.norm.sf(K / s), pontas["95"][0], pontas["95"][1], pontas["90"][0]]
            ref = g[["estimativa", "ep_cluster_conjunto", "ic95_inf", "ic95_sup", "li95_unilateral", "p_unilateral",
                     "ic95_fieller_inf", "ic95_fieller_sup", "li95_unilateral_fieller"]].to_numpy(float)
            np.testing.assert_allclose(got, ref, rtol=1e-6, err_msg=id_linha)
            # IC de β contém zero, e o de K também (§4); o LI unilateral > 0 não muda o P1a bilateral (p > 0,05)
            sb = math.sqrt(V[ib, ib])
            self.assertTrue(b - stats.norm.ppf(0.975) * sb < 0 < b + stats.norm.ppf(0.975) * sb)
            self.assertTrue(pontas["95"][0] < 0 < pontas["95"][1])
            self.assertGreater(2 * stats.norm.sf(abs(b / sb)), 0.05)


if __name__ == "__main__":
    unittest.main()
