"""Testes do protocolo 64: `scripts/rdd_bolsa/43_oferta_local_corte.py` (doc 57q).

1. `TestSintetico`: DADOS SINTÉTICOS gerados em memória (rotulados SINTETICO_TESTE, nunca gravados): IC de
   Anderson–Rubin da grade igual à solução analítica da quadrática, Wald conjunto do pré e regras da leitura
   pré-registrada (§4 do protocolo; decisões D14 e D15).
2. `TestPortao`: o salto do F3.1 do E7 em U, 0,300, refeito aqui com a mesma função a partir do B1 do script 37
   (diferença ≤ 1e−8), e o registro do portão no resumo.
3. `TestSaidasReais`: esquema, `natureza_dos_dados`, nenhuma competência ≥ 202609, IVS oficial, famílias de Holm e
   BKY recalculadas, coerência entre partes, hashes, figuras e saídas de outros blocos intactas.
4. `TestDoc57q`: o doc é igual ao que o script gera das saídas, com cabeçalho, decisões e limites.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "43_oferta_local_corte.py"
_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location("oferta_local_corte_43", SCRIPT)
OC = importlib.util.module_from_spec(_spec)
sys.modules["oferta_local_corte_43"] = OC
_spec.loader.exec_module(OC)
sys.dont_write_bytecode = _bytecode
L = OC.L

OUT = ROOT / "output" / "rdd_bolsa"
EST = OUT / "OC_estimativas.csv"
EVENTO = OUT / "OC_estudo_evento.csv"
RESUMO = OUT / "OC_resumo.json"
DIR_FIG = OUT / "OC_figuras"
DOC = ROOT / "docs" / "06_execucao" / "57q_resultados_oferta_local_corte.md"
NATUREZA_SINTETICA = "SINTETICO_TESTE"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def ler():
    return OC.ler_saidas()


# ---------------------------------------------------------------------------
# 1. Sintético
# ---------------------------------------------------------------------------

class TestSintetico(unittest.TestCase):
    """Dados sintéticos em memória (SINTETICO_TESTE)."""

    def test_anderson_rubin_igual_a_quadratica(self):
        rng = np.random.default_rng(64)
        n = 600
        s = rng.integers(240, 361, n).astype(float)
        d = (rng.random(n) < np.where(s > 300, 0.7, 0.2)).astype(float)
        dy = 2.0 * d + 0.01 * (s - 300) + rng.normal(0, 1.0, n)
        ar = OC.anderson_rubin(s, dy, d, 300)
        ry = L.rd_local_linear(s, dy, 300, OC.H, detalhes=True)
        rd = L.rd_local_linear(s, d, 300, OC.H, detalhes=True)
        fy, fd = ry["_detalhes"]["fit"], rd["_detalhes"]["fit"]
        a = L._pesos_lineares(fy)
        np.testing.assert_allclose(a, L._pesos_lineares(fd), atol=1e-12)
        ey, ed = fy["residuos"], fd["residuos"]
        z2, f = L.Z_975 ** 2, fy["fator"]
        A = rd["tau"] ** 2 - z2 * f * np.sum(a ** 2 * ed ** 2)
        B = -2 * ry["tau"] * rd["tau"] + 2 * z2 * f * np.sum(a ** 2 * ey * ed)
        C = ry["tau"] ** 2 - z2 * f * np.sum(a ** 2 * ey ** 2)
        self.assertGreater(A, 0)                          # primeiro estágio forte: intervalo limitado
        raizes = np.sort(np.roots([A, B, C]).real)
        self.assertAlmostEqual(ar["ar_ic_inf"], raizes[0], places=6)
        self.assertAlmostEqual(ar["ar_ic_sup"], raizes[1], places=6)
        self.assertFalse(ar["ar_aberto_inf"] or ar["ar_aberto_sup"])
        self.assertEqual(ar["ar_n_intervalos"], 1)
        self.assertAlmostEqual(ar["p_beta0"], ry["p_valor"], places=12)
        self.assertTrue(ar["ar_ic_inf"] < ry["tau"] / rd["tau"] < ar["ar_ic_sup"])

    def test_anderson_rubin_instrumento_fraco_fica_aberto(self):
        rng = np.random.default_rng(7)
        n = 600
        s = rng.integers(240, 361, n).astype(float)
        d = (rng.random(n) < 0.3).astype(float)           # sem salto no corte
        dy = rng.normal(0, 1.0, n)
        ar = OC.anderson_rubin(s, dy, d, 300)
        self.assertTrue(ar["ar_aberto_inf"] or ar["ar_aberto_sup"] or not np.isfinite(ar["ar_ic_inf"]))

    def _painel(self, inclinacao_pre: float, semente: int) -> tuple[np.ndarray, pd.DataFrame]:
        rng = np.random.default_rng(semente)
        n = 800
        s = rng.integers(240, 361, n).astype(float)
        cima = (s > 300).astype(float)
        meses = list(OC.MESES)
        k = np.arange(len(meses)) - meses.index(OC.COMP_REF)
        Y = rng.normal(0, 1, (n, 1)) + rng.normal(0, 0.3, (n, len(meses))) + inclinacao_pre * cima[:, None] * k[None, :]
        return s, pd.DataFrame(Y, columns=meses)

    def test_wald_do_pre(self):
        s, larga = self._painel(0.0, 3)
        w = OC.wald_pre_corte(s, larga, 300)
        self.assertEqual(w["gl"], len(OC.MESES_PRE_PLANO))
        self.assertGreater(w["p_valor"], 0.01)
        s, larga = self._painel(0.2, 3)
        self.assertLess(OC.wald_pre_corte(s, larga, 300)["p_valor"], 1e-6)
        larga.iloc[0, 0] = np.nan                          # mês ausente: o município sai do teste e é contado
        self.assertEqual(OC.wald_pre_corte(s, larga, 300)["n_municipios_fora"], 1)

    def _est(self, *, prim=(0.1, 0.1, 0.1, 0.1), lo=(-1, -1, -1, -1), hi=(1, 1, 1, 1), holm=(0.5,) * 4,
             q5=(0.5, 0.5), pre=(0.5,) * 6, f=(50.0, 50.0), a3=((0.1, -1, 1), (0.1, -1, 1)),
             d_ic=((-1, 1),) * 6, e_p=(0.5, 0.5)):
        linhas = []
        i = 0
        for oid in OC.PRIMARIAS:
            for corte in OC.CORTES:
                linhas.append(OC.linha("A", OC.ID_OC[oid], oid, "V", corte, "principal", tau=prim[i],
                                       ic95_inf=lo[i], ic95_sup=hi[i], p_holm=holm[i]))
                i += 1
        for j, corte in enumerate(OC.CORTES):
            linhas.append(OC.linha("A", "OC-A5", "B5", "V", corte, "principal", tau=0.0, ic95_inf=-1, ic95_sup=1,
                                   q_bky=q5[j]))
            linhas.append(OC.linha("A", "OC-A3", "B3", "V", corte, "principal", tau=a3[j][0], ic95_inf=a3[j][1],
                                   ic95_sup=a3[j][2]))
            linhas.append(OC.linha("B", "OC-B0", "D1", "V", corte, "primeiro_estagio", f_robusto=f[j]))
            linhas.append(OC.linha("E", "OC-E", "celula_algum_ciclo", "U", corte, "principal", p_valor=e_p[j]))
        k = 0
        for corte in OC.CORTES:
            for oid in OC.OUTCOMES_EVENTO:
                linhas.append(OC.linha("C", "OC-C", oid, "V", corte, "pre_wald", p_valor=pre[k]))
                linhas.append(OC.linha("D", "OC-D", oid, "V", corte, "chegada_diferenca", ic95_inf=d_ic[k][0],
                                       ic95_sup=d_ic[k][1]))
                k += 1
        est = pd.DataFrame(linhas).reindex(columns=OC.COLUNAS_EST)
        est["natureza_dos_dados"] = NATUREZA_SINTETICA
        return est

    def test_leitura_preregistrada(self):
        c = OC.classificar(self._est())
        self.assertEqual(c["caso_primarias"], "nulo")
        self.assertFalse(c["fraco"]["0.300"])
        # B1 em 0,300 rejeita depois do Holm, placebo não rejeita e pré plano: pacote do corte.
        est = self._est(prim=(0.5, 0.1, 0.1, 0.1), lo=(0.2, -1, -1, -1), holm=(0.01, 0.5, 0.5, 0.5))
        c = OC.classificar(est)
        self.assertEqual(c["caso_primarias"], "pacote")
        self.assertEqual(c["rejeitam_limpos"], ["B1|0.300"])
        # Placebo rejeita no mesmo corte: não ler.
        est = self._est(prim=(0.5, 0.1, 0.1, 0.1), lo=(0.2, -1, -1, -1), holm=(0.01, 0.5, 0.5, 0.5), q5=(0.01, 0.5))
        self.assertEqual(OC.classificar(est)["caso_primarias"], "nao_ler")
        # Pré do B1 em 0,300 não é plano: não ler.
        est = self._est(prim=(0.5, 0.1, 0.1, 0.1), lo=(0.2, -1, -1, -1), holm=(0.01, 0.5, 0.5, 0.5),
                        pre=(0.01, 0.5, 0.5, 0.5, 0.5, 0.5))
        self.assertEqual(OC.classificar(est)["caso_primarias"], "nao_ler")
        # IC exclui zero, Holm não rejeita: descritivo (D15).
        est = self._est(prim=(0.5, 0.1, 0.1, 0.1), lo=(0.01, -1, -1, -1), holm=(0.12, 0.5, 0.5, 0.5))
        self.assertEqual(OC.classificar(est)["caso_primarias"], "descritivo")
        # Instrumento fraco, deslocamento em B3, OC-D e OC-E.
        est = self._est(f=(4.0, 50.0), a3=((-0.5, -0.9, -0.1), (0.1, -1, 1)), d_ic=((0.1, 1),) + ((-1, 1),) * 5,
                        e_p=(0.01, 0.5))
        c = OC.classificar(est)
        self.assertTrue(c["fraco"]["0.300"])
        self.assertFalse(c["fraco"]["0.400"])
        self.assertEqual(c["a3_deslocamento_cortes"], ["0.300"])
        self.assertFalse(c["d"]["B1|0.300"]["contem_zero"])
        self.assertTrue(c["v_selecionada"])

    def test_aplicar_multiplos_nas_familias(self):
        linhas = [OC.linha("A", "x", f"o{i}", "V", 300, "principal", p_valor=p, familia_multipla=fam)
                  for i, (p, fam) in enumerate([(0.01, "holm"), (0.04, "holm"), (0.03, "bky"), (0.2, "bky"),
                                                (0.001, "")])]
        est = pd.DataFrame(linhas).reindex(columns=OC.COLUNAS_EST).assign(natureza_dos_dados=NATUREZA_SINTETICA)
        est = OC.aplicar_multiplos(est)
        self.assertAlmostEqual(est.loc[0, "p_holm"], 0.02)
        self.assertAlmostEqual(est.loc[1, "p_holm"], 0.04)
        self.assertTrue(est.loc[[2, 3, 4], "p_holm"].isna().all())
        self.assertTrue(est.loc[[0, 1, 4], "q_bky"].isna().all())
        np.testing.assert_allclose(est.loc[[2, 3], "q_bky"], L.qvalores_bky([0.03, 0.2]))


# ---------------------------------------------------------------------------
# 2. Portão de reprodução
# ---------------------------------------------------------------------------

class TestPortao(unittest.TestCase):
    def test_portao_registrado(self):
        p = json.loads(RESUMO.read_text(encoding="utf-8"))["portao"]
        self.assertTrue(p["aprovado"])
        self.assertLessEqual(p["dif_tau"], 1e-8)
        self.assertLessEqual(p["dif_ep"], 1e-8)
        self.assertEqual(p["n_e7"], p["n_reproduzido"])

    def test_reproduz_f31_do_e7_em_U_0300(self):
        """Refaz o portão: B1 do script 37 em U → ΔB1 → rd_dird_delta(0,300) = F3.1 do E7 (≤ 1e−8)."""
        base, _ = OC.K1M.ler_universo()
        U = pd.Index(base.index, name="co_ibge")
        p = OC.OL.ler_painel(U)
        self.assertLess(p["competencia"].max(), "202609")
        b1 = OC.OL.contagem(p, "alvo_pmme", "n_vinculos", U)
        dados = {"base": base, "U": U, "niveis": {"B1": b1}, "pop": base["populacao_2022"].astype(float)}
        r = OC.portao_reproducao(dados)
        e7 = pd.read_csv(OUT / "E7_estimativas.csv", dtype={"corte": str})
        ref = e7[(e7["outcome_id"] == "F3.1") & (e7["populacao"] == "U") & (e7["corte"] == "0.300")
                 & (e7["especificacao"] == "principal")].iloc[0]
        self.assertLessEqual(abs(r["tau_reproduzido"] - float(ref["tau"])), 1e-8)
        self.assertLessEqual(abs(r["ep_reproduzido"] - float(ref["ep"])), 1e-8)


# ---------------------------------------------------------------------------
# 3. Saídas reais
# ---------------------------------------------------------------------------

class TestSaidasReais(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.est, cls.ev, cls.resumo = ler()

    def test_esquema_e_rotulos(self):
        self.assertEqual(list(self.est.columns), OC.COLUNAS_EST)
        self.assertEqual(list(self.ev.columns), OC.COLUNAS_EVENTO)
        for df in (self.est, self.ev):
            self.assertEqual(set(df["natureza_dos_dados"]), {"EMPIRICO"})
            self.assertEqual(set(df["estatuto"]), {"PROTOCOLO_64_POS_RESULTADO"})
        self.assertEqual(self.resumo["natureza_dos_dados"], "EMPIRICO")
        self.assertEqual(self.resumo["estatuto"], "PROTOCOLO_64_POS_RESULTADO")
        self.assertEqual(set(self.est["parte"]), {"A", "B", "C", "D", "E"})
        prin = self.est[(self.est["parte"] == "A") & (self.est["especificacao"] == "principal")]
        self.assertEqual(len(prin), 2 * len(OC.IDS) * len(OC.CORTES))
        for esp, n in (("sensibilidade_h", 2), ("ic_honesto", 1), ("pos_com_pre_covariavel", 1)):
            self.assertEqual(int((self.est["especificacao"] == esp).sum()), n * 2 * len(OC.IDS) * len(OC.CORTES), esp)
        self.assertEqual(int((self.est["especificacao"] == "primeiro_estagio").sum()), 6)
        for dn in ("D1", "D2"):
            n = 2 if dn == "D1" else 1
            self.assertEqual(int((self.est["especificacao"] == f"fuzzy_{dn}").sum()), n * len(OC.IDS) * len(OC.CORTES))

    def test_amostra(self):
        a = self.resumo["amostra"]
        ol = json.loads((OUT / "OL_resumo.json").read_text(encoding="utf-8"))
        self.assertEqual(a["V"], ol["amostra"]["n_municipios"])
        self.assertEqual(a["V_tratados"], ol["coortes"]["n_tratados"])
        self.assertEqual(a["U_com_celula"] - a["excluidos_tratados_fora_d2"], a["V"])
        for pn in ("V", "U"):
            for oid in OC.IDS:
                self.assertGreaterEqual(a["fora_por_falta_de_mes"][pn][oid]["sem_delta"], 0)

    def test_nenhuma_competencia_proibida(self):
        self.assertLess(self.ev["competencia"].max(), "202609")
        self.assertEqual(sorted(self.ev["competencia"].unique()), list(OC.MESES))
        self.assertEqual(self.resumo["parametros"]["meses_lidos"], ["202406", "202608"])
        self.assertIn('"202609"', SCRIPT.read_text(encoding="utf-8"))

    def test_ivs_oficial(self):
        fonte = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("ivs_ipea_2010_municipios", fonte)
        caminhos = [e["caminho"] for e in self.resumo["entradas"]]
        self.assertIn("output/aquisicao/a08_ivs_2010_oficial_municipio.csv", caminhos)
        self.assertFalse(any("ivs_ipea" in c for c in caminhos))

    def test_inferencia_da_parte_a(self):
        z = stats.norm.ppf(0.975)
        for _, r in self.est[(self.est["parte"] == "A") & (self.est["especificacao"] != "ic_honesto")].iterrows():
            self.assertAlmostEqual(r["ic95_inf"], r["tau"] - z * r["ep"], places=8)
            self.assertAlmostEqual(r["ic95_sup"], r["tau"] + z * r["ep"], places=8)
            self.assertAlmostEqual(r["p_valor"], 2 * stats.norm.sf(abs(r["tau"] / r["ep"])), places=8)

    def test_holm_e_bky_recalculados(self):
        e = self.est
        holm = e[e["familia_multipla"] == "holm"]
        bky = e[e["familia_multipla"] == "bky"]
        self.assertEqual(len(holm), 4)
        self.assertEqual(set(holm["id_oc"]), {"OC-A1", "OC-A2"})
        self.assertEqual(set(holm["populacao"]), {"V"})
        self.assertEqual(len(bky), 24)
        self.assertEqual(sorted(bky["id_oc"].value_counts().items()),
                         sorted({"OC-A3": 2, "OC-A4": 2, "OC-A5": 2, "OC-B0": 2, "OC-B1": 2, "OC-B2": 2, "OC-B3": 2,
                                 "OC-B4": 2, "OC-B5": 2, "OC-D": 6}.items()))
        np.testing.assert_allclose(holm["p_holm"], L.holm(holm["p_valor"].to_numpy()), atol=1e-12)
        np.testing.assert_allclose(bky["q_bky"], L.qvalores_bky(OC.p_familia(bky).to_numpy()), atol=1e-12)
        self.assertTrue(np.isfinite(OC.p_familia(bky).to_numpy()).all())
        self.assertTrue(e.loc[e["familia_multipla"] != "holm", "p_holm"].isna().all())
        self.assertTrue(e.loc[e["familia_multipla"] != "bky", "q_bky"].isna().all())

    def test_fuzzy_coerente_com_a_forma_reduzida(self):
        e = self.est
        for _, r in e[e["especificacao"].str.startswith("fuzzy")].iterrows():
            if r["f_robusto"] >= OC.F_FRACO:
                self.assertAlmostEqual(r["tau"], r["tau_forma_reduzida"] / r["tau_primeiro_estagio"], places=10)
                self.assertAlmostEqual(r["p_valor"], r["ar_p_beta0"], places=12)
            if np.isfinite(r["ar_ic_inf"]) and np.isfinite(r["ar_ic_sup"]):
                self.assertLessEqual(r["ar_ic_inf"], r["ar_ic_sup"])
            if r["populacao"] == "V" and r["especificacao"] == "fuzzy_D1":
                a = e[(e["parte"] == "A") & (e["populacao"] == "V") & (e["outcome_id"] == r["outcome_id"])
                      & (e["corte"] == r["corte"]) & (e["especificacao"] == "principal")].iloc[0]
                self.assertAlmostEqual(r["tau_forma_reduzida"], a["tau"], places=10)
                self.assertAlmostEqual(r["ar_p_beta0"], a["p_valor"], places=10)

    def test_fuzzy_vazio_quando_instrumento_fraco(self):
        """Auditoria 39, achado B1 (correção de formato pedida pelo autor em 26/10/2026): com F robusto < 10, a
        linha fuzzy não grava razão, EP, IC convencional nem p; leva a nota `instrumento_fraco_F<10`; o IC de AR
        ilimitado sai como `ar_ilimitado = True`, sem a borda da grade nos limites."""
        f = self.est[self.est["especificacao"].str.startswith("fuzzy")]
        fracos = f[~(f["f_robusto"] >= OC.F_FRACO)]
        self.assertGreater(len(fracos), 0)
        for _, r in fracos.iterrows():
            chave = (r["outcome_id"], r["populacao"], r["corte"], r["especificacao"])
            for c in ("tau", "ep", "ic95_inf", "ic95_sup", "p_valor"):
                self.assertTrue(pd.isna(r[c]), (c, chave))
            self.assertTrue(r["nota"].startswith(OC.NOTA_FRACO), chave)
            self.assertTrue(np.isfinite(r["ar_p_beta0"]), chave)
            self.assertTrue(np.isfinite(r["tau_forma_reduzida"]) and np.isfinite(r["tau_primeiro_estagio"]), chave)
        for _, r in f.iterrows():
            chave = (r["outcome_id"], r["populacao"], r["corte"], r["especificacao"])
            if str(r["ar_ilimitado"]) == "True":
                self.assertTrue(pd.isna(r["ar_ic_inf"]) and pd.isna(r["ar_ic_sup"]), chave)
            if str(r["ar_aberto_inf"]) == "True":
                self.assertTrue(pd.isna(r["ar_ic_inf"]), chave)
            if str(r["ar_aberto_sup"]) == "True":
                self.assertTrue(pd.isna(r["ar_ic_sup"]), chave)
        nao_fuzzy = self.est[~self.est["especificacao"].str.startswith("fuzzy")]
        self.assertTrue(nao_fuzzy[["ar_ilimitado", "ar_p_beta0"]].isna().all().all())

    def test_ar_para_csv(self):
        base = {"ar_ic_inf": -5.0, "ar_ic_sup": 5.0, "ar_n_intervalos": 1, "nota_ar": "x"}
        r = OC.ar_para_csv({**base, "ar_aberto_inf": True, "ar_aberto_sup": True})
        self.assertTrue(r["ar_ilimitado"])
        self.assertTrue(np.isnan(r["ar_ic_inf"]) and np.isnan(r["ar_ic_sup"]))
        r = OC.ar_para_csv({**base, "ar_aberto_inf": False, "ar_aberto_sup": True})
        self.assertFalse(r["ar_ilimitado"])
        self.assertEqual(r["ar_ic_inf"], -5.0)
        self.assertTrue(np.isnan(r["ar_ic_sup"]))
        r = OC.ar_para_csv({**base, "ar_aberto_inf": False, "ar_aberto_sup": False})
        self.assertFalse(r["ar_ilimitado"])
        self.assertEqual((r["ar_ic_inf"], r["ar_ic_sup"]), (-5.0, 5.0))

    def test_ar_ilimitado_quando_f_abaixo_do_critico(self):
        """Auditoria 39: com F robusto (t² do primeiro estágio na mesma amostra) abaixo de z², o coeficiente de β²
        da desigualdade de Anderson–Rubin é negativo e o conjunto é ilimitado dos dois lados."""
        z2 = L.Z_975 ** 2
        f = self.est[self.est["especificacao"].str.startswith("fuzzy")]
        for _, r in f[f["f_robusto"] < z2].iterrows():
            self.assertEqual(str(r["ar_aberto_inf"]), "True", (r["outcome_id"], r["populacao"], r["corte"]))
            self.assertEqual(str(r["ar_aberto_sup"]), "True", (r["outcome_id"], r["populacao"], r["corte"]))

    def test_primeiro_estagio_f_robusto(self):
        for _, r in self.est[self.est["especificacao"] == "primeiro_estagio"].iterrows():
            self.assertAlmostEqual(r["f_robusto"], (r["tau"] / r["ep"]) ** 2, places=8)

    def test_estudo_de_evento(self):
        ev = self.ev
        self.assertEqual(len(ev), len(OC.OUTCOMES_EVENTO) * len(OC.CORTES) * len(OC.MESES))
        ref = ev[ev["referencia"].astype(str) == "True"]
        self.assertEqual(set(ref["competencia"]), {OC.COMP_REF})
        self.assertTrue(ref["tau"].isna().all())
        nref = ev[ev["referencia"].astype(str) != "True"]
        self.assertTrue(np.isfinite(nref["tau"]).all())
        pre = self.est[self.est["especificacao"] == "pre_wald"]
        self.assertEqual(len(pre), len(OC.OUTCOMES_EVENTO) * len(OC.CORTES))
        self.assertTrue((pre["gl"] == len(OC.MESES_PRE_PLANO)).all())
        np.testing.assert_allclose(pre["p_valor"], stats.chi2.sf(pre["tau"], pre["gl"]), atol=1e-12)

    def test_parte_d(self):
        d = self.est[self.est["parte"] == "D"]
        for (oid, corte), g in d.groupby(["outcome_id", "corte"]):
            g = g.set_index("especificacao")
            self.assertAlmostEqual(g.loc["chegada_diferenca", "tau"],
                                   g.loc["chegada_acima", "tau"] - g.loc["chegada_abaixo", "tau"], places=10)
            self.assertEqual(int(g.loc["chegada_diferenca", "n_tratados"]),
                             int(g.loc["chegada_acima", "n_tratados"] + g.loc["chegada_abaixo", "n_tratados"]))
        lados = self.resumo["chegada_por_lado_tratados"]
        for corte, v in lados.items():
            g = d[(d["corte"] == corte) & (d["outcome_id"] == "B1")].set_index("especificacao")
            self.assertEqual(int(g.loc["chegada_abaixo", "n_tratados"]), v["abaixo"])
            self.assertEqual(int(g.loc["chegada_acima", "n_tratados"]), v["acima"])
        self.assertEqual(self.resumo["parametros"]["bootstrap_parte_d"]["semente"], 20261026)
        self.assertEqual(self.resumo["parametros"]["bootstrap_parte_d"]["B"], 9999)

    def test_hashes(self):
        r = self.resumo
        self.assertEqual(r["protocolo"]["sha256_texto"], sha256(OC.PROTOCOLO_MD))
        for e in r["entradas"]:
            self.assertEqual(e["sha256"], sha256(ROOT / e["caminho"]), e["caminho"])
        for s in r["saidas"]:
            self.assertEqual(s["sha256"], sha256(ROOT / s["arquivo"]), s["arquivo"])
        for f in r["figuras"]:
            self.assertEqual(f["sha256"], sha256(ROOT / f["arquivo"]), f["arquivo"])

    def test_figuras(self):
        figs = self.resumo["figuras"]
        self.assertEqual({f["chave"] for f in figs}, {"salto", "evento", "primeiro_estagio"})
        self.assertEqual(sorted(p.name for p in DIR_FIG.glob("*.png")), sorted(Path(f["arquivo"]).name for f in figs))
        for f in figs:
            self.assertTrue(f["como_ler"].startswith("COMO LER."))
            self.assertTrue(f["fonte"].startswith("Fonte:"))

    def test_saidas_de_outros_blocos_intactas(self):
        for nome in (OC.NOME_EST, OC.NOME_EVENTO, OC.NOME_RESUMO, OC.DIR_FIG):
            self.assertTrue(nome.startswith("OC_"))
        self.assertTrue(all(Path(s["arquivo"]).name.startswith("OC_") for s in self.resumo["saidas"]))
        try:
            st = subprocess.run(["git", "status", "--porcelain", "--", "output/rdd_bolsa"], cwd=ROOT,
                                capture_output=True, text=True, check=True).stdout
        except (OSError, subprocess.CalledProcessError):
            self.skipTest("git indisponível")
        alterados = [ln[3:] for ln in st.splitlines() if ln[:2].strip() in ("M", "D")]
        self.assertFalse([a for a in alterados if re.search(r"/(E7_|OL_|EQ_)", a)], alterados)

    def test_sem_identificador_pessoal(self):
        padrao = re.compile(r"g5p_\d|x1m_\d|\b\d{3}\.\d{3}\.\d{3}-\d{2}\b", re.I)
        for arq in (EST, EVENTO, RESUMO, DOC):
            self.assertIsNone(padrao.search(arq.read_text(encoding="utf-8")), arq.name)


# ---------------------------------------------------------------------------
# 4. Doc 57q
# ---------------------------------------------------------------------------

class TestDoc57q(unittest.TestCase):
    def test_doc_igual_ao_gerado(self):
        est, ev, resumo = ler()
        gerado = OC.gerar_tabelas_doc(est, ev, resumo)
        no_doc = OC.tabelas_no_doc(DOC.read_text(encoding="utf-8"))
        self.assertEqual(set(no_doc), set(gerado))
        for k, v in gerado.items():
            self.assertEqual(no_doc[k], v, k)

    def test_cabecalho_decisoes_e_limites(self):
        texto = DOC.read_text(encoding="utf-8")
        for s in ("PROTOCOLO_64_POS_RESULTADO", "**Auditoria:** [auditoria 39]", "conjunto é a **reta inteira**",
                  "Esclarecimento da auditoria 39","64_protocolo_oferta_local_no_corte.md",
                  "43_oferta_local_corte.py", "test_oferta_local_corte.py", "## 9. Decisões de implementação",
                  "2026-10-26, antes de olhar qualquer estimativa", "## 7. Limites", "Pacote do corte", "Exclusão",
                  "Seleção de V", "Pouca potência da parte D"):
            self.assertIn(s, texto)
        for d in range(1, 17):
            self.assertIn(f"| D{d} |", texto)

    def test_linguagem(self):
        est, ev, resumo = ler()
        leitura = OC.gerar_tabelas_doc(est, ev, resumo)["leitura"]
        c = OC.classificar(est)
        if c["caso_primarias"] == "nulo":
            self.assertIn("o corte não detecta efeito do pacote sobre a oferta local", leitura)
        self.assertIn("nada é efeito da participação no PMM-E como política", leitura)
        self.assertNotIn("efeito da bolsa sobre", leitura)
        for k, fraco in c["fraco"].items():
            if fraco:
                self.assertIn(f"Em {k.replace('.', ',')} o instrumento é fraco", leitura)


if __name__ == "__main__":
    unittest.main()
