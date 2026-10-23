"""P3, extensões do adendo §12 do protocolo 47 (script 27): esquema, rótulos, doc 57c, números e sintético.

As classes `TestSintetico*` usam dados SINTETICOS gerados só em memória (nunca gravados) para conferir o
Callaway–Sant'Anna generalizado (grupos, elegíveis, controles nunca tratados, cluster), o DiD sintético e o outcome
regional. As demais leem as saídas versionadas `output/rdd_bolsa/K_X_*` e o doc 57c.
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
X = _importar(RDD / "27_producao_extensoes.py", "k27_teste")
sys.dont_write_bytecode = _bytecode
D2, K, L = X.D2M, X.K1M, X.L

OUT = ROOT / "output" / "rdd_bolsa"
EST, EV, ATT, RES = OUT / X.NOME_EST, OUT / X.NOME_EVENTO, OUT / X.NOME_ATT, OUT / X.NOME_RESUMO
ROTULO_SINTETICO = "sintético"    # rótulo dos dados gerados nesta suíte (só em memória, nunca gravados)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


# --------------------------------------------------------------------------
# Sintético (só em memória)
# --------------------------------------------------------------------------

def painel_sintetico(rng, N=600, T=40, efeito=1.0):
    """sintético: coortes 20, 26 e 32, nunca tratados, efeito 1 + 0,1 e depois da chegada."""
    coortes = np.array([20, 26, 32])
    G = rng.choice(np.r_[coortes, -1], size=N, p=[0.2, 0.2, 0.2, 0.4])
    a = rng.normal(0, 5, N)
    lam = np.cumsum(rng.normal(0, 1, T))
    Y = a[:, None] + lam[None, :] + rng.normal(0, 1, (N, T))
    tt = np.arange(T)
    for i in range(N):
        if G[i] >= 0:
            e = tt - G[i]
            Y[i] += np.where(e >= 0, efeito + 0.1 * e, 0.0)
    return Y, G, sorted(set(coortes.tolist()))


class TestSinteticoCSGeral(unittest.TestCase):
    """sintético: o CS generalizado reduz-se ao do D2 e respeita grupos, elegíveis, controles e cluster."""

    def test_rotulo(self) -> None:
        self.assertEqual(ROTULO_SINTETICO, "sintético")

    def test_igual_ao_d2_sem_grupo(self) -> None:
        rng = np.random.default_rng(1)
        Y, G, coortes = painel_sintetico(rng)
        tab0, IF0 = D2.att_gt(Y, G, coortes, e_min=-6, e_max=4)
        tab1, IF1, _ = X.att_gt_geral(Y, G, [(None, g) for g in coortes], e_min=-6, e_max=4)
        self.assertTrue(np.allclose(tab0["att"].to_numpy(dtype=float), tab1["att"].to_numpy(dtype=float),
                                    equal_nan=True))
        self.assertTrue(np.allclose(IF0, IF1))
        xi = D2.pesos_mammen(999, Y.shape[0], 7)
        r0 = D2.estimar_cs(Y, G, coortes, xi, e_min=-6, e_max=4)
        r1 = X.estimar_cs_cluster(Y, G, [(None, g) for g in coortes], np.arange(Y.shape[0]), semente=7, B=999,
                                  e_min=-6, e_max=4)
        self.assertTrue(np.allclose(r0["evento"]["theta"], r1["evento"]["theta"], equal_nan=True))
        self.assertTrue(np.allclose(r0["evento"]["ep"], r1["evento"]["ep"], equal_nan=True))
        self.assertAlmostEqual(r0["pos"]["att"], r1["pos"]["att"], places=12)
        self.assertAlmostEqual(r0["pos"]["ep"], r1["pos"]["ep"], places=12)
        self.assertAlmostEqual(r1["pos"]["att"], np.mean([1 + 0.1 * e for e in range(5)]), delta=0.3)

    def test_controles_do_mesmo_grupo(self) -> None:
        G = np.array([5, 5, -1, -1, 5, -1, -1, -1])
        grupo = np.array([1, 1, 1, 1, 2, 2, 2, 2])
        Y = np.arange(8 * 10, dtype=float).reshape(8, 10)
        tab, _, _ = X.att_gt_geral(Y, G, [(1, 5), (2, 5)], grupo=grupo, e_min=0, e_max=1, min_controles=1)
        r1 = tab[(tab["grupo"] == 1) & (tab["e"] == 0)].iloc[0]
        r2 = tab[(tab["grupo"] == 2) & (tab["e"] == 0)].iloc[0]
        self.assertEqual((int(r1["n_tratados"]), int(r1["n_controles"])), (2, 2))
        self.assertEqual((int(r2["n_tratados"]), int(r2["n_controles"])), (1, 3))

    def test_elegiveis_e_nunca_tratados(self) -> None:
        G = np.array([5, 5, 8, 8, -1, -1])
        Y = np.arange(6 * 12, dtype=float).reshape(6, 12)
        eleg = np.array([True, True, False, False, False, False])
        tab, _, _ = X.att_gt_geral(Y, G, [(None, 5)], elegivel=eleg, e_min=0, e_max=4, min_controles=1)
        self.assertEqual(int(tab[tab["t"] == 7].iloc[0]["n_controles"]), 4)    # coorte 8 ainda é controle
        self.assertEqual(int(tab[tab["t"] == 8].iloc[0]["n_controles"]), 2)
        tab, _, _ = X.att_gt_geral(Y, G, [(None, 5)], elegivel=eleg, controles="nunca", e_min=0, e_max=4,
                                   min_controles=1)
        self.assertTrue((tab["n_controles"] == 2).all())

    def test_cluster_de_pares_duplicados(self) -> None:
        """sintético: duplicar cada unidade dentro do mesmo cluster não muda θ nem o EP."""
        rng = np.random.default_rng(2)
        Y, G, coortes = painel_sintetico(rng, N=300)
        cs = [(None, g) for g in coortes]
        r1 = X.estimar_cs_cluster(Y, G, cs, np.arange(300), semente=3, B=499, e_min=-4, e_max=3)
        r2 = X.estimar_cs_cluster(np.vstack([Y, Y]), np.r_[G, G], cs, np.r_[np.arange(300), np.arange(300)],
                                  semente=3, B=499, e_min=-4, e_max=3)
        self.assertAlmostEqual(r1["pos"]["att"], r2["pos"]["att"], places=10)
        self.assertAlmostEqual(r1["pos"]["ep"], r2["pos"]["ep"], places=10)

    def test_diferenca_de_si_mesmo_e_zero(self) -> None:
        rng = np.random.default_rng(4)
        Y, G, coortes = painel_sintetico(rng, N=300)
        r = X.estimar_cs_cluster(Y, G, [(None, g) for g in coortes], np.arange(300), B=199, e_min=-3, e_max=2)
        d = X.diferenca_pos(r, r)
        self.assertEqual(d["att"], 0.0)
        self.assertEqual(d["ep"], 0.0)


class TestSinteticoSDID(unittest.TestCase):
    """sintético: o DiD sintético recupera um efeito constante num modelo de fatores."""

    def test_recupera_efeito(self) -> None:
        rng = np.random.default_rng(5)
        N0, N1, T0, T = 120, 30, 30, 38
        f = np.cumsum(rng.normal(0, 1, (T, 2)), axis=0)
        load = rng.normal(0, 1, (N0 + N1, 2))
        load[N0:] += 0.5                                       # tratados com cargas diferentes
        Y = 10 + load @ f.T + rng.normal(0, 0.3, (N0 + N1, T))
        Y[N0:, T0:] += 2.0
        r = X.sdid(Y, N0, T0)
        self.assertAlmostEqual(r["tau"], 2.0, delta=0.3)
        for w in (r["omega"], r["lambda"]):
            self.assertAlmostEqual(float(w.sum()), 1.0, places=10)
            self.assertTrue((w >= 0).all())

    def test_fw_no_simplex(self) -> None:
        rng = np.random.default_rng(6)
        A = rng.normal(size=(40, 12))
        lam = X.fw_pesos(A, 0.1)
        self.assertAlmostEqual(float(lam.sum()), 1.0, places=10)
        self.assertTrue((lam >= 0).all())


class TestSinteticoRegiao(unittest.TestCase):
    """sintético: outcome regional = outros municípios da região; ausente não vira zero; sozinho sem outcome."""

    def test_regional(self) -> None:
        meses = list(X.MESES)
        idx = pd.Index(["A", "B", "C", "D"])
        num = pd.DataFrame(1.0, index=idx, columns=meses)
        num.loc["B"] = 2.0
        num.loc["C"] = 3.0
        num.loc["C", meses[1]] = np.nan
        pop = pd.Series([1e4, 2e4, 3e4, 5e4], index=idx)
        cir = pd.Series(["r1", "r1", "r1", "r2"], index=idx)
        Y, info = X.serie_regional(num, pop, cir, pd.Index(["A", "D"]))
        self.assertAlmostEqual(Y[0, 0], (2 + 3) / 5e4 * 1e4)
        self.assertTrue(np.isnan(Y[0, 1]))                         # C sem dado no mês: regional ausente
        self.assertTrue(np.isnan(Y[1]).all())                      # D sozinho na região
        self.assertEqual(info["municipios_da_amostra_sozinhos_na_regiao"], ["D"])
        Yb, _ = X.serie_regional(num, pop, cir, pd.Index(["C"]))
        self.assertAlmostEqual(Yb[0, 1], (1 + 2) / 3e4 * 1e4)      # o próprio ausente não contamina os outros


class TestSinteticoRegras(unittest.TestCase):
    def test_codigo_nao_le_arquivo_errado_nem_nomes(self) -> None:
        texto = (RDD / "27_producao_extensoes.py").read_text(encoding="utf-8")
        self.assertNotIn("ivs_ipea_2010_municipios", texto)
        self.assertNotIn("cnes_nacional", texto)
        for c in ("nome", "crm", "sexo", "raca_cor"):
            self.assertNotIn(c, X.COLUNAS_NOMINAL)
        self.assertEqual(X.FIM, "202605")
        self.assertEqual(X.LIMITE_SIA_SIH, "202607")


# --------------------------------------------------------------------------
# Saídas reais
# --------------------------------------------------------------------------

class TestSaidas(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.est, cls.ev, cls.resumo = X.ler_saidas()
        cls.att = pd.read_csv(ATT, dtype={"coorte": str, "competencia": str})

    def test_esquema_e_rotulos(self) -> None:
        self.assertEqual(list(self.est.columns), X.COLUNAS_EST)
        self.assertEqual(list(self.ev.columns), X.COLUNAS_EVENTO)
        self.assertEqual(list(self.att.columns), X.COLUNAS_ATT)
        for df in (self.est, self.ev, self.att):
            self.assertEqual(set(df["natureza_dos_dados"]), {"EMPIRICO"})
            self.assertEqual(set(df["estatuto"]), {"PROTOCOLO_47_ADENDO_12_POS_RESULTADO"})
        self.assertEqual(self.resumo["natureza_dos_dados"], "EMPIRICO")
        self.assertEqual(self.resumo["estatuto"], "PROTOCOLO_47_ADENDO_12_POS_RESULTADO")
        self.assertTrue(set(self.est["status"]) <= {"EXECUTADO", "SEM_ESTIMATIVA", "NAO_EXECUTADO"})
        self.assertEqual(set(self.est["item"]), {"12.1", "12.2", "12.3", "12.4", "12.5"})

    def test_sem_estimativa_tem_nota(self) -> None:
        s = self.est[self.est["valor"].isna() & (self.est["estatistica"] != "pretendencia_supt")]
        self.assertTrue((s["nota"].fillna("").str.len() > 0).all())
        self.assertTrue((s["status"] != "EXECUTADO").all())

    def test_limites_de_meses(self) -> None:
        self.assertLessEqual(self.att["competencia"].max(), "202605")
        self.assertGreaterEqual(self.att["coorte"].min(), "202201")

    def test_bky_recalculado(self) -> None:
        b = self.est[self.est["entra_bky"].astype(bool)]
        self.assertEqual(len(b), 8)
        q = L.qvalores_bky(b["p_valor"].to_numpy(dtype=float))
        self.assertTrue(np.allclose(q, b["q_bky"].to_numpy(dtype=float)))
        self.assertTrue(self.est.loc[~self.est["entra_bky"].astype(bool), "q_bky"].isna().all())

    def test_att_medio_igual_media_do_evento(self) -> None:
        a = self.est[self.est["estatistica"] == "att_pos_medio"]
        n = 0
        for r in a.to_dict("records"):
            if r["status"] != "EXECUTADO":
                continue
            m = ((self.ev["item"] == r["item"]) & (self.ev["outcome_id"] == r["outcome_id"])
                 & (self.ev["versao_fonte"].fillna("") == r["versao_fonte"])
                 & (self.ev["recorte"].fillna("") == r["recorte"]) & (self.ev["variante"] == r["variante"])
                 & (self.ev["desenho"] == r["desenho"]) & (self.ev["e"] >= 0) & self.ev["theta"].notna())
            self.assertGreater(int(m.sum()), 0)
            self.assertAlmostEqual(float(self.ev.loc[m, "theta"].mean()), r["valor"], places=9)
            n += 1
        self.assertGreater(n, 15)

    def test_v1_e_d2_reproduzem_doc50(self) -> None:
        kd1 = pd.read_csv(X.K_D1_EST, dtype={"corte": str})
        kd2 = pd.read_csv(X.K_D2_EST)
        for corte in ("0.300", "0.400", "empilhado"):
            a = kd1[(kd1["outcome_id"] == "K2") & (kd1["populacao"] == "U") & (kd1["corte"] == corte)
                    & (kd1["especificacao"] == "principal")]["tau"].iloc[0]
            b = X._um(self.est, item="12.1", outcome_id="K2", versao_fonte="a13_v1", desenho="D1",
                      variante="principal", corte=corte)["valor"]
            self.assertAlmostEqual(a, b, places=9)
        for oid, f in (("K2", dict(item="12.1", outcome_id="K2", versao_fonte="a13_v1", desenho="D2")),
                       ("K1", dict(item="12.3", recorte="D2_doc50"))):
            a = kd2[(kd2["outcome_id"] == oid) & (kd2["variante"] == "principal")
                    & (kd2["estatistica"] == "att_pos_medio")]
            b = X._um(self.est, **f, estatistica="att_pos_medio")
            self.assertAlmostEqual(float(a["valor"].iloc[0]), b["valor"], places=9)
            self.assertAlmostEqual(float(a["ep"].iloc[0]), b["ep"], places=9)

    def test_k1_v2_nao_executado_com_motivo(self) -> None:
        comp = json.loads(X.SIA_V2_COMP.read_text(encoding="utf-8"))
        self.assertEqual(int(comp["celulas_diferentes"]), 0)
        r = X._um(self.est, item="12.1", outcome_id="K1")
        self.assertEqual(r["status"], "NAO_EXECUTADO")
        self.assertIn("sem revisao", r["nota"])

    def test_entradas_com_hash_atual(self) -> None:
        for e in self.resumo["entradas"]:
            self.assertEqual(sha256(ROOT / e["caminho"]), e["sha256"], e["caminho"])
        for s in self.resumo["saidas"].values():
            self.assertEqual(sha256(ROOT / s["arquivo"]), s["sha256"], s["arquivo"])

    def test_figuras_com_como_ler(self) -> None:
        figs = self.resumo["figuras"]
        self.assertEqual(len(figs), 6)
        for f in figs:
            self.assertEqual(sha256(ROOT / f["arquivo"]), f["sha256"])
            frases = [s for s in re.split(r"(?<=[.;])\s+", f["como_ler"].strip()) if s]
            self.assertTrue(1 <= len([s for s in frases if s.endswith(".")]) <= 2, f["arquivo"])
            self.assertNotRegex(f["como_ler"], r"\d+,\d+")          # sem número de resultado

    def test_doc_igual_ao_gerado(self) -> None:
        texto = X.DOC.read_text(encoding="utf-8")
        self.assertEqual(texto, X.gerar_doc(self.est, self.ev, self.resumo))

    def test_numeros_do_doc_contra_output(self) -> None:
        texto = X.DOC.read_text(encoding="utf-8")
        r = X._um(self.est, item="12.2", recorte=X.TODOS, variante="principal", estatistica="att_pos_medio")
        self.assertIn(f"| {X._n(r['valor'], 2)} | [{X._n(r['ic95_inf'], 2)}; {X._n(r['ic95_sup'], 2)}] |", texto)
        for b in self.est[self.est["entra_bky"].astype(bool)].to_dict("records"):
            self.assertIn(X._p(b["q_bky"]), texto)
        for f in self.resumo["figuras"]:
            self.assertIn(f["como_ler"], texto)
            self.assertIn(f["arquivo"], texto)

    def test_linguagem(self) -> None:
        texto = X.DOC.read_text(encoding="utf-8").lower()
        self.assertIn("tendências paralelas", texto)
        self.assertIn("deslocamento", texto)
        self.assertIn("expansão líquida", texto)
        self.assertNotIn("efeito causal", texto)
        self.assertIn("57c", texto)


class TestRecalculoIndependente(unittest.TestCase):
    """Refaz duas linhas com leitura própria dos painéis (pandas) e o CS do D2."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.est, _, cls.resumo = X.ler_saidas()
        base, _ = K.ler_universo()
        cls.base = base
        cls.amostra, _ = D2.ler_amostra(base)
        cls.chegadas, _ = D2.ler_chegadas(cls.amostra)

    def _att(self, Y, G, coortes):
        tab, IF = D2.att_gt(Y, G, coortes)
        ev, _ = D2.agregar_evento(tab, IF, G)
        th = ev.loc[ev["e"] >= 0, "theta"].astype(float)
        return float(th[np.isfinite(th)].mean())

    def test_k2r_d2(self) -> None:
        df = pd.read_parquet(X.A15_PAINEL, columns=["co_ibge", "competencia", "grupo", "aih_aprovadas"])
        df = df[(df["grupo"] == "04") & df["competencia"].isin(X.MESES)]
        larga = df.pivot(index="co_ibge", columns="competencia", values="aih_aprovadas").astype(float)
        pop = self.base["populacao_2022"].astype(float)
        Y = (larga.reindex(self.amostra).div(pop.reindex(self.amostra), axis=0) * 1e4)[list(X.MESES)].to_numpy()
        G, coortes = D2.indices_coorte(self.chegadas, list(X.MESES))
        r = X._um(self.est, item="12.4", outcome_id="K2r", desenho="D2", variante="principal",
                  estatistica="att_pos_medio")
        self.assertAlmostEqual(self._att(Y, G, coortes), r["valor"], places=9)

    def test_curso_15(self) -> None:
        formas = self.resumo["amostras"]["cursos_especificos"]["formas_tipicas"]["15"]
        df = pd.read_parquet(X.A17_PAINEL, columns=["co_ibge", "competencia_processamento", "cod_curso", "forma",
                                                    "qtd_aprovada"],
                             filters=[("cod_curso", "=", 15), ("forma", "in", formas)])
        df["comp"] = df["competencia_processamento"].astype(str)
        df = df[df["comp"].isin(X.MESES)]
        larga = df.groupby([df["co_ibge"].astype(str), "comp"])["qtd_aprovada"].sum().unstack().astype(float)
        cel = pd.read_parquet(X.V_CELULA, columns=["ciclo", "co_ibge", "cod_curso"])
        cel = cel[cel["ciclo"].isin([1, 2]) & (cel["cod_curso"] == 15)]
        mun = sorted(set(cel["co_ibge"].astype(str).str.zfill(6)) & set(self.base.index))
        nom = pd.read_csv(X.NOMINAL, usecols=["co_ibge", "curso", "dt_inicio_atividade"], dtype=str)
        nom = nom[nom["curso"].str[:2] == "15"]
        nom["co_ibge"] = nom["co_ibge"].str[:6]
        nom["comp"] = nom["dt_inicio_atividade"].str[:7].str.replace("-", "")
        ch = nom.groupby("co_ibge")["comp"].min().reindex(mun)
        chegadas = pd.DataFrame({"chegada": ch, "coorte": ch.map(lambda c: D2.trimestre_inicio(c) if isinstance(c, str)
                                                                 else np.nan)})
        pop = self.base["populacao_2022"].astype(float)
        Y = (larga.reindex(mun).div(pop.reindex(mun), axis=0) * 1e4)[list(X.MESES)].to_numpy()
        G, coortes = D2.indices_coorte(chegadas, list(X.MESES))
        r = X._um(self.est, item="12.2", recorte="curso_15", variante="principal", estatistica="att_pos_medio")
        self.assertAlmostEqual(self._att(Y, G, coortes), r["valor"], places=9)


if __name__ == "__main__":
    unittest.main()
