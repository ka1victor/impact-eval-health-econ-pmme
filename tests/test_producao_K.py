"""Testes da família K (protocolo 47): D1 (`21_producao_dird.py`) e D2 (`22_chegada_pmme_evento.py`).

Duas partes:

1. `TestSintetico*`: DADOS SINTÉTICOS gerados em memória (semente fixa), rotulados como sintéticos e nunca
   gravados em `output/` nem em `data/`. Servem só para conferir que a DiRD (linear e Poisson), as janelas com
   ausência e o estimador de Callaway–Sant'Anna recuperam efeitos conhecidos e que ausência nunca vira zero.
2. `TestSaidasReais*`: invariantes das saídas versionadas `output/rdd_bolsa/K_D1_*` e `K_D2_*` (pulados se
   não existirem): esquema, rótulos, limites de meses, Holm e BKY recalculados, MDE e efeito relativo, todas as
   especificações presentes, uma linha principal refeita de forma independente a partir do painel do SIH, doc 50
   igual ao gerado das saídas e figuras existentes. Nenhum número esperado é digitado.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RDD = ROOT / "scripts" / "rdd_bolsa"


def _importar(caminho: Path, nome: str):
    if nome in sys.modules:
        return sys.modules[nome]
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    return mod


_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
K = _importar(RDD / "21_producao_dird.py", "k21_teste")
D2 = _importar(RDD / "22_chegada_pmme_evento.py", "k22_teste")
sys.dont_write_bytecode = _bytecode
L = K.L

OUT = ROOT / "output" / "rdd_bolsa"
EST1, EV1, RES1 = OUT / K.NOME_EST, OUT / K.NOME_EVENTO, OUT / K.NOME_RESUMO
EST2, EV2, ATT2, RES2 = OUT / D2.NOME_EST, OUT / D2.NOME_EVENTO, OUT / D2.NOME_ATT, OUT / D2.NOME_RESUMO
DOC = K.DOC50
ROTULO_SINTETICO = "SINTETICO"   # rótulo dos dados gerados nesta suíte (nunca gravados)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


# --------------------------------------------------------------------------
# Dados sintéticos (só em memória)
# --------------------------------------------------------------------------

def municipios_sinteticos(rng, n=4000):
    """SINTETICO: running variable em milésimos entre 200 e 500, com mass points inteiros."""
    s = rng.integers(200, 501, size=n).astype(float)
    return pd.Index([f"S{i:05d}" for i in range(n)], name="co_ibge"), s


class TestSinteticoDiRD(unittest.TestCase):
    """SINTETICO: a DiRD recupera o salto do pós e ignora o salto fixo; ausência não vira zero."""

    @classmethod
    def setUpClass(cls) -> None:
        rng = np.random.default_rng(20261019)
        idx, s = municipios_sinteticos(rng)
        T = (s > 300).astype(float) + (s > 400).astype(float)  # degrau: 0, 1, 2 (um passo em cada corte)
        meses = list(K.MESES_SIA)
        pop = pd.Series(50_000.0, index=idx)
        base = 100 + 50 * (s / 1000)
        salto_fixo, salto_pos = 7.0, 3.0
        cols = {}
        for m in meses:
            pos = 1.0 if m >= "202510" else 0.0
            taxa = base + salto_fixo * T + pos * salto_pos * T + rng.normal(0, 0.5, size=len(s))
            cols[m] = taxa * pop.to_numpy() / K.ESCALA_HAB
        num = pd.DataFrame(cols, index=idx)
        # ausência: um município perde dois meses do pós
        num.iloc[0, num.columns.get_loc("202511")] = np.nan
        num.iloc[0, num.columns.get_loc("202512")] = np.nan
        cls.num, cls.pop, cls.s = num, pop, pd.Series(s, index=idx)
        cls.salto_pos = salto_pos
        cls.d = K.base_janelas(num, None, pop, cls.s, K.POS_K1)
        cls.dc = K.base_janelas(num, None, pop, cls.s, K.POS_K1, completo=True)

    def test_rotulo(self) -> None:
        self.assertEqual(ROTULO_SINTETICO, "SINTETICO")

    def test_dird_recupera_salto_do_pos(self) -> None:
        for corte in (300, 400, K.EMPILHADO):
            r = K.E7.rd_delta(self.d, "y_pos", "y_pre", corte)
            self.assertAlmostEqual(r["tau"], self.salto_pos, delta=0.15, msg=str(corte))

    def test_nivel_mostra_pacote(self) -> None:
        r = K.E7.rd(self.d, "y_pre", 300)
        self.assertAlmostEqual(r["tau"], 7.0, delta=0.3)

    def test_placebo_pre_em_zero(self) -> None:
        r = K.E7.rd_delta(self.d, "y_placebo_b", "y_placebo_a", K.EMPILHADO)
        self.assertLess(abs(r["tau"]), 0.15)

    def test_ausencia_nao_vira_zero(self) -> None:
        """Média do principal usa os meses com dado; media_completa deixa o município sem delta."""
        i0 = self.num.index[0]
        y_pos = self.d.set_index("co_ibge").loc[i0, "y_pos"]
        esperado = (self.num.loc[i0, list(K.POS_K1)].dropna() / self.pop[i0] * K.ESCALA_HAB).mean()
        self.assertAlmostEqual(y_pos, esperado, places=9)
        self.assertTrue(np.isnan(self.dc.set_index("co_ibge").loc[i0, "delta_principal"]))
        # a exposição do Poisson conta só os meses com dado
        e = self.d.set_index("co_ibge").loc[i0, "e_pos"]
        self.assertEqual(e, self.pop[i0] * (len(K.POS_K1) - 2))

    def test_razao_k5_usa_somas(self) -> None:
        num = self.num.iloc[:3, :].copy()
        den = num * 2
        y, sn, sd = K.janela_valores(num, den, self.pop.iloc[:3], K.COMP_PRE)
        self.assertTrue(np.allclose(y.to_numpy(), 0.5))
        den.iloc[1, :] = 0.0
        y, _, _ = K.janela_valores(num.where(den > 0, 0.0), den, self.pop.iloc[:3], K.COMP_PRE)
        self.assertTrue(np.isnan(y.iloc[1]), "razao indefinida (denominador zero) fica ausente")


class TestSinteticoPoisson(unittest.TestCase):
    """SINTETICO: a DiRD de Poisson recupera o salto em log da razão pós/pré."""

    def test_recupera_salto_log(self) -> None:
        rng = np.random.default_rng(7)
        n = 5000
        s = rng.integers(200, 501, size=n).astype(float)
        T = (s > 300).astype(float)
        expo_pre, expo_pos = np.full(n, 2e5), np.full(n, 1.5e5)
        lam = 1e-3 * np.exp(0.5 * (s - 300) / 1000)
        tau = 0.2
        c_pre = rng.poisson(expo_pre * lam * np.exp(0.3 * T))
        c_pos = rng.poisson(expo_pos * lam * np.exp(0.3 * T + 0.1 + tau * T))
        d = pd.DataFrame({"co_ibge": [f"P{i}" for i in range(n)], "s_mil": s, "c_pre": c_pre.astype(float),
                          "c_pos": c_pos.astype(float), "e_pre": expo_pre, "e_pos": expo_pos})
        r = K.poisson_dird(d, 300)
        self.assertAlmostEqual(r["tau"], tau, delta=0.06)
        self.assertGreater(r["ep"], 0)
        r2 = K.poisson_dird(d.assign(s_mil=s), K.EMPILHADO)
        self.assertTrue(np.isfinite(r2["tau"]))

    def test_lado_sem_evento_fica_sem_estimativa(self) -> None:
        n = 200
        s = np.linspace(250, 350, n).round()
        d = pd.DataFrame({"co_ibge": [f"Z{i}" for i in range(n)], "s_mil": s, "c_pre": np.zeros(n),
                          "c_pos": np.zeros(n), "e_pre": np.ones(n), "e_pos": np.ones(n)})
        r = K.poisson_dird(d, 300)
        self.assertTrue(np.isnan(r["tau"]))
        self.assertIn("suporte insuficiente", r["nota"])


class TestSinteticoCallawaySantAnna(unittest.TestCase):
    """SINTETICO: ATT(g, t) com ainda-não-tratados recupera a trajetória conhecida e o teste do pré funciona."""

    @staticmethod
    def painel(rng, violacao: float = 0.0, N: int = 900, T: int = 40):
        coortes = np.array([20, 26, 32])
        G = rng.choice(np.r_[coortes, -1], size=N, p=[0.2, 0.2, 0.2, 0.4])
        a = rng.normal(0, 5, N)
        lam = np.cumsum(rng.normal(0, 1, T))
        Y = a[:, None] + lam[None, :] + rng.normal(0, 1, (N, T))
        tt = np.arange(T)
        for i in range(N):
            if G[i] >= 0:
                e = tt - G[i]
                Y[i] += np.where(e >= 0, 1.0 + 0.1 * e, 0.0)
                Y[i] += violacao * tt * (G[i] == 26)       # tendência própria da coorte 26
        return Y, G, sorted(set(coortes.tolist()))

    def test_recupera_efeito_e_pre_plano(self) -> None:
        rng = np.random.default_rng(11)
        Y, G, coortes = self.painel(rng)
        xi = D2.pesos_mammen(1999, Y.shape[0], 5)
        r = D2.estimar_cs(Y, G, coortes, xi, e_min=-12, e_max=6)
        ev = r["evento"].set_index("e")
        for e in range(0, 7):
            self.assertAlmostEqual(ev.loc[e, "theta"], 1.0 + 0.1 * e, delta=0.35, msg=f"e={e}")
        for e in range(-12, -1):
            self.assertLess(abs(ev.loc[e, "theta"]), 0.35, msg=f"e={e}")
        self.assertEqual(ev.loc[-1, "theta"], 0.0)
        self.assertGreater(r["pre"]["p_wald"], 0.001)
        self.assertAlmostEqual(r["pos"]["att"], np.mean([1.0 + 0.1 * e for e in range(7)]), delta=0.3)
        # EP do bootstrap perto do analítico
        ok = ev["ep"].notna()
        self.assertTrue(np.allclose(ev.loc[ok, "ep"], ev.loc[ok, "ep_analitico"], rtol=0.25))

    def test_violacao_rejeita_pre(self) -> None:
        rng = np.random.default_rng(12)
        Y, G, coortes = self.painel(rng, violacao=0.3)
        xi = D2.pesos_mammen(999, Y.shape[0], 5)
        r = D2.estimar_cs(Y, G, coortes, xi, e_min=-12, e_max=6)
        self.assertLess(r["pre"]["p_wald"], 0.01)

    def test_ausencia_tira_da_celula(self) -> None:
        rng = np.random.default_rng(13)
        Y, G, coortes = self.painel(rng)
        Y2 = Y.copy()
        alvo = np.flatnonzero(G == 20)[:5]
        Y2[alvo, 22] = np.nan
        tab, _ = D2.att_gt(Y2, G, coortes, e_min=-3, e_max=3)
        tab0, _ = D2.att_gt(Y, G, coortes, e_min=-3, e_max=3)
        a = tab[(tab["g"] == 20) & (tab["t"] == 22)].iloc[0]
        b = tab0[(tab0["g"] == 20) & (tab0["t"] == 22)].iloc[0]
        self.assertEqual(int(a["n_tratados"]), int(b["n_tratados"]) - 5)

    def test_controles_ainda_nao_tratados(self) -> None:
        """Para t >= g, coorte posterior só é controle enquanto g' > t."""
        G = np.array([5, 5, 8, 8, -1, -1])
        Y = np.arange(6 * 12, dtype=float).reshape(6, 12)
        tab, _ = D2.att_gt(Y, G, [5, 8], e_min=0, e_max=4, min_controles=1)
        r = tab[(tab["g"] == 5) & (tab["t"] == 7)].iloc[0]
        self.assertEqual(int(r["n_controles"]), 4)
        r = tab[(tab["g"] == 5) & (tab["t"] == 8)].iloc[0]
        self.assertEqual(int(r["n_controles"]), 2)

    def test_bootstrap_deterministico(self) -> None:
        a = D2.pesos_mammen(500, 300, 20261019)
        b = D2.pesos_mammen(500, 300, 20261019)
        self.assertTrue(np.array_equal(a, b))
        self.assertAlmostEqual(float(a.mean()), 0.0, delta=0.02)
        self.assertAlmostEqual(float(a.var()), 1.0, delta=0.03)


class TestSinteticoRegras(unittest.TestCase):
    def test_tipos_sigtap(self) -> None:
        self.assertEqual(K.tipo_sia("0301"), "consultas")
        self.assertIsNone(K.tipo_sia("0302"))
        self.assertEqual(K.tipo_sia("0205"), "exames")
        self.assertEqual(K.tipo_sia("0415"), "cirurgias")
        self.assertEqual(K.tipo_sia("0903"), "oci")
        self.assertIsNone(K.tipo_sia("0101"))

    def test_trimestre(self) -> None:
        self.assertEqual(D2.trimestre_inicio("202509"), "202507")
        self.assertEqual(D2.trimestre_inicio("202604"), "202604")
        self.assertEqual(D2.trimestre_inicio("202612"), "202610")

    def test_substituicao(self) -> None:
        sobe, cai, zero = ({"ic95_inf": 1, "ic95_sup": 2}, {"ic95_inf": -2, "ic95_sup": -1},
                           {"ic95_inf": -1, "ic95_sup": 1})
        t = K.leitura_substituicao({"sus": sobe, "privado_vinculos": cai, "total": zero, "nao_alvo": zero}, desenho="x")
        self.assertIn("migração", t)
        t = K.leitura_substituicao({"sus": zero, "total": sobe, "nao_alvo": zero}, desenho="x")
        self.assertIn("ganho líquido", t)
        t = K.leitura_substituicao({"sus": sobe, "total": zero, "nao_alvo": cai}, desenho="x")
        self.assertIn("remanejamento entre especialidades", t)
        t = K.leitura_substituicao({"sus": zero, "total": zero}, desenho="x")
        self.assertIn("Nenhum dos três padrões", t)

    def test_codigo_nao_le_arquivo_errado_nem_nomes(self) -> None:
        for script in ("21_producao_dird.py", "22_chegada_pmme_evento.py"):
            texto = (RDD / script).read_text(encoding="utf-8")
            self.assertNotIn("ivs_ipea_2010_municipios", texto)
        self.assertNotIn("nome", D2.COLUNAS_NOMINAL)
        self.assertNotIn("crm", D2.COLUNAS_NOMINAL)


# --------------------------------------------------------------------------
# Saídas reais
# --------------------------------------------------------------------------

@unittest.skipUnless(EST1.exists() and RES1.exists(), "saidas do D1 ausentes")
class TestSaidasReaisD1(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.est, cls.ev, cls.resumo = K.ler_saidas()

    def test_esquema_e_rotulos(self) -> None:
        self.assertEqual(list(self.est.columns), K.COLUNAS_SAIDA)
        self.assertEqual(list(self.ev.columns), K.COLUNAS_EVENTO)
        for df in (self.est, self.ev):
            self.assertEqual(set(df["natureza_dos_dados"]), {"EMPIRICO"})
            self.assertEqual(set(df["estatuto"]), {"PROTOCOLO_47_POS_SINTESE"})
        self.assertEqual(set(self.est["desenho"]), {"D1"})
        self.assertEqual(self.resumo["estatuto"], "PROTOCOLO_47_POS_SINTESE")
        self.assertTrue(set(self.est["status"]) <= {"EXECUTADO", "SEM_ESTIMATIVA", "NAO_EXECUTADO"})
        sem = self.est[self.est["status"] != "EXECUTADO"]
        self.assertTrue((sem["nota"].fillna("") != "").all(), "linha sem estimativa precisa de motivo")

    def test_limites_de_meses(self) -> None:
        comp = self.ev["competencia"].astype(str)
        self.assertTrue((comp >= "202201").all())
        fonte = self.ev["outcome_id"].map({c["id"]: c["fonte"] for c in K.CATALOGO})
        self.assertTrue((comp[fonte.isin(["SIA", "SIH"])] <= K.LIMITE_SIA_SIH).all())
        self.assertTrue((comp[fonte.isin(["TISS", "TISSH", "K3", "K5"])] <= K.LIMITE_TISS).all())
        self.assertTrue((comp[fonte == "CNES"] < K.LIMITE_CNES).all())
        p = self.resumo["parametros"]
        self.assertEqual(p["pos_K1_K2_SIA_SIH_CNES"], "202510-202605")
        self.assertEqual(p["pos_TISS"], "202510-202512")
        self.assertEqual(p["pre"], "202406-202506")
        self.assertTrue((self.est["janela_pos"].dropna().str[-6:] < K.LIMITE_CNES).all())

    def test_holm_recalculado(self) -> None:
        h = self.est[self.est["entra_holm"].astype(bool)]
        self.assertEqual(sorted(h["outcome_id"]), sorted(K.PRIMARIAS))
        self.assertTrue((h["populacao"] == "U").all() and (h["corte"] == K.EMPILHADO).all()
                        and (h["especificacao"] == "principal").all())
        p = h["p_valor"].to_numpy(dtype=float)
        ordem = np.argsort(p)
        m = len(p)
        adj = np.empty(m)
        acum = 0.0
        for k, i in enumerate(ordem):
            acum = max(acum, min(1.0, (m - k) * p[i]))
            adj[i] = acum
        self.assertTrue(np.allclose(adj, h["p_holm"].to_numpy(dtype=float)))
        self.assertTrue(self.est.loc[~self.est["entra_holm"].astype(bool), "p_holm"].isna().all())

    def test_bky_recalculado(self) -> None:
        b = self.est[self.est["entra_bky"].astype(bool)]
        self.assertEqual(sorted(b["outcome_id"]), sorted(K.SECUNDARIAS))
        q = L.qvalores_bky(b["p_valor"].to_numpy(dtype=float))
        self.assertTrue(np.allclose(q, b["q_bky"].to_numpy(dtype=float), equal_nan=True))

    def test_mde_e_relativo(self) -> None:
        e = self.est[np.isfinite(self.est["ep"].astype(float))]
        self.assertTrue(np.allclose(e["mde"], K.FATOR_MDE * e["ep"]))
        lin = e[(e["especificacao"] != "poisson_dird") & np.isfinite(e["efeito_relativo"].astype(float))]
        self.assertTrue(np.allclose(lin["efeito_relativo"], lin["tau"] / lin["media_pre_abaixo"]))
        po = e[(e["especificacao"] == "poisson_dird") & np.isfinite(e["tau"].astype(float))]
        self.assertTrue(np.allclose(po["efeito_relativo"], np.expm1(po["tau"])))

    def test_todas_as_especificacoes(self) -> None:
        for spec in K.CATALOGO:
            for pop in K.POPULACOES:
                for corte in ("0.300", "0.400", K.EMPILHADO):
                    g = self.est[(self.est["outcome_id"] == spec["id"]) & (self.est["populacao"] == pop)
                                 & (self.est["corte"] == corte)]
                    esp = set(g["especificacao"])
                    exig = {"principal", "media_completa", "sensibilidade_h", "placebo_pre", "nivel_pre", "nivel_pos",
                            "S5_pre_menos_pre_extra", "S2_donut"}
                    exig |= {f"sens|{v['nome']}" for v in spec["variantes"]}
                    if spec["poisson"]:
                        exig.add("poisson_dird")
                    if spec["honesto"]:
                        exig.add("ic_honesto")
                    if corte != K.EMPILHADO:
                        exig |= {"S3_porte_muda", "S3_porte_nao_muda", "S3_diferenca"}
                    if corte == "0.400":
                        exig |= {"S4_dentro", "S4_fora", "S4_diferenca"}
                    self.assertTrue(exig <= esp, f"{spec['id']} {pop} {corte}: faltam {exig - esp}")
                    hs = sorted(g.loc[g["especificacao"] == "sensibilidade_h", "h"].round(3))
                    self.assertEqual(hs, [0.035, 0.075])
        self.assertNotIn("K1e", set(self.est["outcome_id"]))

    def test_k2_principal_refeito_do_painel(self) -> None:
        """Linha principal de K2 em 0,300 (U) refeita com MQP à mão a partir dos insumos versionados."""
        sih = pd.read_parquet(K.SIH, columns=["co_ibge", "competencia", "grupo", "aih_aprovadas"],
                              filters=[("grupo", "=", "04")])
        a08 = pd.read_csv(K.A08, dtype={"co_ibge": str})
        a08["co_ibge"] = a08["co_ibge"].str[:6]
        pop = pd.read_csv(K.POP22, dtype={"co_ibge_6d": str}).rename(columns={"co_ibge_6d": "co_ibge"})
        u = a08.merge(pop[["co_ibge", "populacao_2022"]], on="co_ibge")
        sih = sih[sih["co_ibge"].isin(set(u["co_ibge"]))].merge(u[["co_ibge", "populacao_2022"]], on="co_ibge")
        sih["taxa"] = sih["aih_aprovadas"].astype(float) / sih["populacao_2022"] * 1e4
        pre = sih[sih["competencia"].between("202406", "202506")].groupby("co_ibge")["taxa"].mean()
        pos = sih[sih["competencia"].between("202510", "202605")].groupby("co_ibge")["taxa"].mean()
        d = u.set_index("co_ibge").assign(delta=pos - pre)
        x = (np.round(d["ivs"].astype(float) * 1000) - 300) / 1000
        w = np.maximum(0, 1 - np.abs(x) / 0.05)
        ok = (w > 0) & d["delta"].notna()
        X = np.column_stack([np.ones(ok.sum()), x[ok], (x[ok] > 0), (x[ok] > 0) * x[ok]]).astype(float)
        W = w[ok].to_numpy()
        beta = np.linalg.solve(X.T @ (X * W[:, None]), X.T @ (W * d.loc[ok, "delta"].to_numpy()))
        r = self.est[(self.est["outcome_id"] == "K2") & (self.est["populacao"] == "U") & (self.est["corte"] == "0.300")
                     & (self.est["especificacao"] == "principal")].iloc[0]
        self.assertAlmostEqual(beta[2], r["tau"], places=8)

    def test_entradas_com_hash_atual(self) -> None:
        for b in self.resumo["entradas"]:
            self.assertEqual(sha256(ROOT / b["caminho"]), b["sha256"], b["caminho"])
        self.assertNotIn("ivs_ipea_2010_municipios", json.dumps(self.resumo))

    def test_figuras_existem(self) -> None:
        self.assertEqual(len(self.resumo["figuras"]), 2 * len(K.FIGURAS_OUTCOMES))
        for f in self.resumo["figuras"]:
            self.assertTrue((ROOT / f["arquivo"]).exists(), f["arquivo"])

    @unittest.skipUnless(DOC.exists(), "doc 50 ausente")
    def test_doc_bate_com_as_saidas(self) -> None:
        texto = DOC.read_text(encoding="utf-8")
        no_doc = K.tabelas_no_doc(texto)
        geradas = K.gerar_tabelas_doc(self.est, self.ev, self.resumo)
        self.assertEqual(set(no_doc), set(geradas))
        for k, v in geradas.items():
            self.assertEqual(no_doc[k], v, f"bloco K:{k} do doc 50 difere das saidas")


@unittest.skipUnless(EST2.exists() and RES2.exists(), "saidas do D2 ausentes")
class TestSaidasReaisD2(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.est, cls.ev, cls.resumo = D2.ler_saidas()
        cls.att = pd.read_csv(ATT2, dtype={"coorte": str, "competencia": str})

    def test_esquema_e_rotulos(self) -> None:
        self.assertEqual(list(self.est.columns), D2.COLUNAS_EST)
        self.assertEqual(list(self.ev.columns), D2.COLUNAS_EVENTO)
        self.assertEqual(list(self.att.columns), D2.COLUNAS_ATT)
        for df in (self.est, self.ev, self.att):
            self.assertEqual(set(df["natureza_dos_dados"]), {"EMPIRICO"})
            self.assertEqual(set(df["estatuto"]), {"EXPLORATORIO_PARTICIPACAO"})
            self.assertEqual(set(df["desenho"]), {"D2"})
        self.assertEqual(set(self.est["outcome_id"]), set(D2.OUTCOMES_D2))
        self.assertEqual(set(self.est["variante"]), set(D2.VARIANTES))

    def test_sem_dado_pessoal(self) -> None:
        for p in (EST2, EV2, ATT2, RES2):
            texto = p.read_text(encoding="utf-8").lower()
            self.assertNotIn("crm", texto)
        for df in (self.est, self.ev, self.att):
            self.assertFalse({"nome", "crm", "sexo", "raca_cor"} & set(df.columns))

    def test_limites_de_meses(self) -> None:
        comp = self.att["competencia"]
        k3 = self.att["outcome_id"] == "K3"
        self.assertTrue((comp[k3] <= "202512").all())
        self.assertTrue((comp[~k3] <= "202605").all())
        self.assertTrue((self.att.loc[k3, "coorte"] <= D2.COORTE_MAX_K3).all())
        self.assertTrue(self.ev["e"].between(D2.E_MIN, D2.E_MAX).all())

    def test_base_e_att_medio(self) -> None:
        for (oid, var), g in self.ev.groupby(["outcome_id", "variante"]):
            base = g[g["e"] == -1].iloc[0]
            self.assertTrue(bool(base["referencia"]))
            self.assertEqual(float(base["theta"]), 0.0)
            pos = g[(g["e"] >= 0) & g["theta"].notna()]
            r = self.est[(self.est["outcome_id"] == oid) & (self.est["variante"] == var)
                         & (self.est["estatistica"] == "att_pos_medio")].iloc[0]
            self.assertAlmostEqual(r["valor"], pos["theta"].mean(), places=10)

    def test_theta_reproduz_att_gt(self) -> None:
        """θ(e) = média das ATT(g, g+e) ponderada pelo tamanho da coorte (CSV de ATT(g,t))."""
        for (oid, var), g in self.att.groupby(["outcome_id", "variante"]):
            ev = self.ev[(self.ev["outcome_id"] == oid) & (self.ev["variante"] == var)].set_index("e")
            for e, c in g[g["att"].notna()].groupby("e"):
                th = np.average(c["att"], weights=c["n_coorte"])
                self.assertAlmostEqual(ev.loc[e, "theta"], th, places=10)

    def test_figuras_existem(self) -> None:
        self.assertEqual(len(self.resumo["figuras"]), len(D2.OUTCOMES_D2))
        for f in self.resumo["figuras"]:
            self.assertTrue((ROOT / f["arquivo"]).exists(), f["arquivo"])

    def test_entradas_com_hash_atual(self) -> None:
        for b in self.resumo["entradas"]:
            self.assertEqual(sha256(ROOT / b["caminho"]), b["sha256"], b["caminho"])

    @unittest.skipUnless(DOC.exists(), "doc 50 ausente")
    def test_doc_bate_com_as_saidas(self) -> None:
        texto = DOC.read_text(encoding="utf-8")
        no_doc = D2.tabelas_no_doc(texto)
        geradas = D2.gerar_tabelas_doc(self.est, self.ev, self.resumo)
        self.assertEqual(set(no_doc), set(geradas))
        for k, v in geradas.items():
            self.assertEqual(no_doc[k], v, f"bloco KD2:{k} do doc 50 difere das saidas")


@unittest.skipUnless(DOC.exists(), "doc 50 ausente")
class TestDoc50(unittest.TestCase):
    def test_sem_numero_digitado_fora_dos_blocos(self) -> None:
        texto = D2.MARCA.sub("", K.MARCA.sub("", DOC.read_text(encoding="utf-8")))
        permitidos = {"0,300", "0,400", "0,050", "0,035", "0,075", "2,8", "0,010", "0,5M"}
        decimais = set(re.findall(r"(?<![\w/.-])\d+,\d+(?![\w/])", texto))
        self.assertEqual(decimais - permitidos, set(), "numero decimal fora dos blocos gerados")

    def test_figuras_citadas_existem(self) -> None:
        texto = DOC.read_text(encoding="utf-8")
        for rel in re.findall(r"\]\((\.\./\.\./output/[^)]+\.png)\)", texto):
            self.assertTrue((DOC.parent / rel).resolve().exists(), rel)


if __name__ == "__main__":
    unittest.main()
