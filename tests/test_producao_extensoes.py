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

    def test_leitura_com_pre_e_sem_separar_deslocamento(self) -> None:
        """Auditoria 25: pré destacado onde o IC exclui zero e 12.5 sem leitura de deslocamento como achado."""
        texto = X.DOC.read_text(encoding="utf-8")
        baixo = texto.lower()
        self.assertIn("não ficam separados", baixo)
        self.assertNotIn("compatível com atendimento de referência, não com deslocamento", baixo)
        self.assertNotIn("separa expansão líquida de deslocamento: produção", baixo)
        self.assertIn("pré não plano (wald p < 0,05)", baixo)
        for rot in ("12.2, todos os cursos (ATT agregado)", "12.2, curso 14", "12.5, K1_reg (D2)"):
            self.assertIn(rot, texto)
        # toda linha D2 principal com IC fora de zero e Wald do pré < 0,05 aparece na seção de alertas
        a = self.est[(self.est["estatistica"] == "att_pos_medio") & (self.est["variante"] == "principal")
                     & (self.est["status"] == "EXECUTADO")]
        for r in a.to_dict("records"):
            if X.classificar(r) == "inclui zero":
                continue
            self.assertIn(X._rotulo_linha(r), texto, X._rotulo_linha(r))
        self.assertIn("θ médio do pré", texto)

    def test_classe_pre_regra_do_doc50(self) -> None:
        self.assertEqual(X.classe_pre(2.0, 1.1, np.nan), "parecido")
        self.assertEqual(X.classe_pre(2.0, 0.5, 1.0), "parecido")        # vale o pré dos 12 meses antes do mês-base
        self.assertEqual(X.classe_pre(2.0, -1.0, -0.1), "oposto")
        self.assertEqual(X.classe_pre(2.0, 0.9, 0.2), "neutro")
        self.assertEqual(X.classe_pre(0.0, 1.0, 1.0), "neutro")

    def test_figuras_sem_titulo_nem_legenda_e_corte_declarado(self) -> None:
        for f in self.resumo["figuras"]:
            if f["eixo_cortado"]:
                self.assertIn("limitado", f["como_ler"])
            self.assertNotIn("deslocamento", f["como_ler"].replace("não separa expansão líquida de deslocamento", ""))


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


# --------------------------------------------------------------------------
# Auditoria 25: recálculo com código próprio (pandas/numpy), sem importar funções dos scripts 21, 22 e 27
# --------------------------------------------------------------------------

AUD_MESES = [f"{a}{m:02d}" for a in range(2022, 2027) for m in range(1, 13) if f"{a}{m:02d}" <= "202605"]
AUD_TIPO = {"0301": "consultas"}
AQ = ROOT / "output" / "aquisicao"


def _aud_ib6(s: pd.Series) -> pd.Series:
    return s.astype(str).str.split(".").str[0].str.replace(r"\D", "", regex=True).str[:6].str.zfill(6)


def _aud_tipo(sub: str):
    if sub == "0301":
        return "consultas"
    return {"02": "exames", "04": "cirurgias", "09": "oci"}.get(sub[:2])


def aud_cs(Y, G, grupo=None, eleg=None, nunca=False, emin=-24, emax=9):
    """Callaway–Sant'Anna próprio: base g-1; controles ainda não tratados (G<0 ou G>max(t,b)) ou só nunca tratados;
    theta(e) com peso = fração das unidades de cada (grupo, coorte) entre as células com ATT definido; ATT do pós
    = média de theta(e), e >= 0. Devolve (att_pos, psi_pos, theta por e)."""
    N, T = Y.shape
    grupo = np.zeros(N, dtype=int) if grupo is None else np.asarray(grupo)
    eleg = np.ones(N, dtype=bool) if eleg is None else np.asarray(eleg, dtype=bool)
    chaves = sorted({(int(a), int(g)) for a, g, e in zip(grupo, G, eleg) if g >= 1 and e})
    por_e: dict[int, list] = {}
    for a, g in chaves:
        tr0 = (grupo == a) & (G == g) & eleg
        b = g - 1
        for t in range(max(0, g + emin), min(T, g + emax + 1)):
            if t == b:
                continue
            ok = np.isfinite(Y[:, t]) & np.isfinite(Y[:, b])
            dy = Y[:, t] - Y[:, b]
            ct0 = (G < 0) & (grupo == a) if nunca else (((G < 0) | (G > max(t, b))) & (G != g) & (grupo == a))
            tr, ct = tr0 & ok, ct0 & ok
            if tr.sum() < 1 or ct.sum() < 2:
                continue
            m1, m0 = dy[tr].mean(), dy[ct].mean()
            psi = np.zeros(N)
            psi[tr] = N * (dy[tr] - m1) / tr.sum()
            psi[ct] = -N * (dy[ct] - m0) / ct.sum()
            por_e.setdefault(t - g, []).append(((a, g), m1 - m0, psi, ((grupo == a) & (G == g) & eleg)))
    theta, psis = {}, {}
    for e, lst in por_e.items():
        pi = np.array([c[3].mean() for c in lst])
        S = pi.sum()
        w = pi / S
        att = np.array([c[1] for c in lst])
        psi = sum(wk * c[2] for wk, c in zip(w, lst))
        D = np.column_stack([c[3].astype(float) - p for c, p in zip(lst, pi)])
        psi = psi + (D / S - np.outer(D.sum(axis=1), pi) / S ** 2) @ att
        theta[e], psis[e] = float(w @ att), psi
    pos = [e for e in theta if e >= 0]
    return (float(np.mean([theta[e] for e in pos])), np.mean([psis[e] for e in pos], axis=0), theta)


def aud_ep_cluster(psi, cluster) -> float:
    N = len(psi)
    s = pd.Series(psi).groupby(np.asarray(cluster)).sum()
    return float(np.sqrt((s ** 2).sum()) / N)


def aud_bky(p):
    """BKY (2006) no algoritmo de Anderson (2008), escrito do zero."""
    p = np.asarray(p, float)
    m = len(p)
    ordem = np.argsort(p, kind="stable")
    ps = p[ordem]
    r = np.arange(1, m + 1)
    qs = np.ones(m)
    for k in range(1000, 0, -1):
        q = k / 1000
        q1 = q / (1 + q)
        R1 = (r[ps <= q1 * r / m].max() if (ps <= q1 * r / m).any() else 0)
        q2 = q1 * m / (m - R1) if R1 < m else np.inf
        R2 = (r[ps <= q2 * r / m].max() if (ps <= q2 * r / m).any() else 0)
        qs[r <= R2] = q
    out = np.empty(m)
    out[ordem] = qs
    return out


class TestRecalculoIndependenteAuditoria25(unittest.TestCase):
    """Recálculo da auditoria 25 (docs/auditorias/25_auditoria_P3_extensoes.md), com leitura e estimador próprios:
    12.2 (agregado e um curso), 12.4 (K2r_tot D2), 12.5 (K1_reg), 12.3a (só nunca tratados) e 12.1 (v1 contra v2)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.est = pd.read_csv(EST, dtype={"item": str, "corte": str, "recorte": str, "versao_fonte": str},
                              keep_default_na=True)
        for c in ("corte", "recorte", "versao_fonte"):
            cls.est[c] = cls.est[c].fillna("")
        cls.ev = pd.read_csv(EV, dtype={"item": str, "recorte": str, "versao_fonte": str})
        a08 = pd.read_csv(AQ / "a08_ivs_2010_oficial_municipio.csv", usecols=["co_ibge", "ivs"], dtype={"co_ibge": str})
        pop = pd.read_csv(AQ / "populacao_censo2022_municipios.csv", usecols=["co_ibge_6d", "populacao_2022"],
                          dtype={"co_ibge_6d": str})
        pop["co_ibge"] = _aud_ib6(pop["co_ibge_6d"])
        pop = pop.set_index("co_ibge")["populacao_2022"].astype(float)
        u = sorted(c for c in _aud_ib6(a08["co_ibge"]) if pop.get(c, 0) > 0)
        cls.U = pd.Index(u)
        cls.pop = pop.reindex(cls.U)
        vm = pd.read_parquet(OUT / "outcomes" / "outcomes_V_municipio.parquet", columns=["ciclo", "co_ibge"])
        vm = vm[vm["ciclo"].isin([1, 2])]
        cls.amostra = pd.Index(sorted(set(_aud_ib6(vm["co_ibge"])) & set(u)))
        nom = pd.read_csv(ROOT / "data" / "pmm_especialistas_nominal.csv",
                          usecols=["co_ibge", "curso", "dt_inicio_atividade"], dtype=str)
        nom["co_ibge"] = _aud_ib6(nom["co_ibge"])
        nom["comp"] = pd.to_datetime(nom["dt_inicio_atividade"], format="%Y-%m-%d", errors="coerce").dt.strftime("%Y%m")
        cls.nom = nom[nom["comp"].notna()].copy()
        cls.nom["curso_n"] = cls.nom["curso"].str[:2].astype(int)

    # ---- utilitários ----
    @staticmethod
    def _coorte(comp):
        if not isinstance(comp, str) or comp > "202605":
            return -1
        a, m = int(comp[:4]), int(comp[4:])
        return AUD_MESES.index(f"{a}{3 * ((m - 1) // 3) + 1:02d}")

    def _G_mun(self, idx):
        ch = self.nom.groupby("co_ibge")["comp"].min().reindex(idx)
        return np.array([self._coorte(c) for c in ch])

    def _taxa(self, larga, idx):
        r = larga.reindex(idx).reindex(columns=AUD_MESES)
        return (r.div(self.pop.reindex(idx), axis=0) * 1e4).to_numpy(dtype=float)

    def _linha(self, **f):
        s = self.est
        for k, v in f.items():
            s = s[s[k].astype(str) == str(v)]
        self.assertEqual(len(s), 1, f)
        return s.iloc[0]

    def _comparar(self, nome, att, ep, linha, tol=1e-8):
        self.assertLess(abs(att - float(linha["valor"])), tol, f"{nome}: {att} contra {linha['valor']}")
        razao = ep / float(linha["ep"])
        self.assertTrue(0.6 < razao < 1.6, f"{nome}: EP analítico {ep:.4f} contra bootstrap {linha['ep']:.4f}")

    # ---- SIH ----
    def _sih(self, caminho, grupos):
        df = pd.read_parquet(caminho, columns=["co_ibge", "competencia", "grupo", "aih_aprovadas"],
                             filters=[("competencia", "<=", "202605"), ("grupo", "in", list(grupos))])
        df["q"] = df["aih_aprovadas"].astype("float64")
        larg = [df[df["grupo"] == g].pivot(index="co_ibge", columns="competencia", values="q") for g in grupos]
        tot = larg[0]
        for l in larg[1:]:
            tot = tot.add(l, fill_value=np.nan) if False else tot + l          # ausente propaga (nunca zero)
        return tot

    def test_12_4_k2r_tot_d2(self) -> None:
        tot = self._sih(AQ / "sih_residencia" / "painel_sih_residencia_municipio_mes_grupo.parquet",
                        ["02", "03", "04", "05"])
        Y = self._taxa(tot, self.amostra)
        G = self._G_mun(self.amostra)
        att, psi, _ = aud_cs(Y, G)
        self._comparar("K2r_tot", att, aud_ep_cluster(psi, self.amostra.to_numpy()),
                       self._linha(item="12.4", outcome_id="K2r_tot", desenho="D2", estatistica="att_pos_medio"))

    def test_12_1_k2_v1_contra_v2(self) -> None:
        res = {}
        for v, p in (("a13_v1", AQ / "sih" / "painel_sih_municipio_mes_grupo.parquet"),
                     ("a13b_v2", AQ / "sih_v2" / "painel_sih_municipio_mes_grupo.parquet")):
            Y = self._taxa(self._sih(p, ["04"]), self.amostra)
            att, psi, _ = aud_cs(Y, self._G_mun(self.amostra))
            res[v] = att
            self._comparar(f"K2 {v}", att, aud_ep_cluster(psi, self.amostra.to_numpy()),
                           self._linha(item="12.1", outcome_id="K2", desenho="D2", versao_fonte=v,
                                       estatistica="att_pos_medio"))
        self.assertLess(abs(res["a13b_v2"] - res["a13_v1"]), 0.05)      # a revisão quase não mexe no ponto

    # ---- SIA K1 ----
    @classmethod
    def _k1(cls):
        if hasattr(cls, "_k1_cache"):
            return cls._k1_cache
        sub = pd.read_csv(AQ / "sia" / "sia_subgrupos_por_consulta.csv",
                          dtype={"competencia_processamento": str, "subgrupo": str})
        sub = sub[(sub["conjunto_cbo"] == "alvo_pmme") & (sub["competencia_processamento"] <= "202605")]
        sub["tipo"] = sub["subgrupo"].map(_aud_tipo)
        sub = sub[sub["tipo"].notna()]
        pres = set(sub.loc[sub["presente_na_resposta"].astype(str).str.lower() == "true",
                           ["tipo", "competencia_processamento"]].itertuples(index=False, name=None))
        df = pd.read_parquet(AQ / "sia" / "painel_sia_municipio_mes_subgrupo_cbo.parquet",
                             columns=["co_ibge", "competencia_processamento", "subgrupo", "qtd_aprovada", "status"],
                             filters=[("conjunto_cbo", "=", "alvo_pmme"),
                                      ("competencia_processamento", "<=", "202605")])
        for c in ("co_ibge", "competencia_processamento", "subgrupo", "status"):
            df[c] = df[c].astype(str)
        df["tipo"] = df["subgrupo"].map(_aud_tipo)
        df = df[df["tipo"].notna()]
        df["aus"] = (df["status"] == "municipio_ausente_da_resposta").astype(int)
        df["q"] = df["qtd_aprovada"].astype(float)
        agg = df.groupby(["tipo", "competencia_processamento", "co_ibge"]).agg(q=("q", "sum"), aus=("aus", "sum")
                                                                             ).reset_index()
        agg.loc[agg["aus"] > 0, "q"] = np.nan
        munis = pd.read_csv(AQ / "sia" / "sia_municipios_tabnet.csv", usecols=["co_ibge"], dtype=str)["co_ibge"]
        munis = _aud_ib6(munis)
        tot = None
        for tipo in ("consultas", "exames", "cirurgias", "oci"):
            a = agg[agg["tipo"] == tipo].pivot(index="co_ibge", columns="competencia_processamento", values="q")
            a = a.reindex(index=munis, columns=AUD_MESES)
            for m in AUD_MESES:
                if (tipo, m) not in pres:
                    a[m] = 0.0                 # nenhum subgrupo do tipo veio como coluna: zero da consulta (regra do a12)
            tot = a if tot is None else tot + a
        cls._k1_cache = tot.reindex(cls.U)
        return cls._k1_cache

    def test_12_3a_so_nunca_tratados_e_d2_doc50(self) -> None:
        k1 = self._k1()
        G = self._G_mun(self.amostra)
        att, psi, _ = aud_cs(self._taxa(k1, self.amostra), G)
        self._comparar("K1 D2 doc 50", att, aud_ep_cluster(psi, self.amostra.to_numpy()),
                       self._linha(item="12.3", recorte="D2_doc50", estatistica="att_pos_medio"))
        # (a): saem os municípios cuja 1ª chegada é depois de 202605 (célula não ficou vazia)
        ch = self.nom.groupby("co_ibge")["comp"].min().reindex(self.amostra)
        tarde = ch.notna() & (ch > "202605")
        am_a = self.amostra[~tarde.to_numpy()]
        self.assertEqual(int(tarde.sum()), 20)
        Ga = self._G_mun(am_a)
        att_a, psi_a, _ = aud_cs(self._taxa(k1, am_a), Ga, nunca=True)
        self._comparar("K1 (a)", att_a, aud_ep_cluster(psi_a, am_a.to_numpy()),
                       self._linha(item="12.3", recorte="a_nunca_tratados", estatistica="att_pos_medio"))
        self.assertEqual(int((Ga < 0).sum()), 283)

    # ---- 12.5 ----
    def test_12_5_k1_reg(self) -> None:
        k1 = self._k1()
        linhas = (AQ.parent.parent / "data" / "raw" / "aquisicao" / "territorio" / "datasus_tabnet_br_regsaud.cnv"
                  ).read_bytes().decode("latin1").splitlines()
        cir = {}
        for ln in linhas[1:]:
            m = re.match(r"^\s*\d+\s+(\d{5})\s+.*?\s+(\d{6})\s*$", ln)
            if m:
                cir[m.group(2)] = m.group(1)
        reg = pd.Series(cir).reindex(self.U)
        membros = {r: list(idx) for r, idx in reg.dropna().groupby(reg.dropna()).groups.items()}
        Y = np.full((len(self.amostra), len(AUD_MESES)), np.nan)
        for i, m in enumerate(self.amostra):
            r = reg.get(m)
            if not isinstance(r, str):
                continue
            outros = [o for o in membros[r] if o != m]
            if not outros:
                continue
            soma = k1.loc[outros].sum(axis=0, skipna=False).to_numpy()       # um ausente deixa o mês ausente
            Y[i] = soma / self.pop.loc[outros].sum() * 1e4
        att, psi, _ = aud_cs(Y, self._G_mun(self.amostra))
        self._comparar("K1_reg", att, aud_ep_cluster(psi, self.amostra.to_numpy()),
                       self._linha(item="12.5", outcome_id="K1_reg", estatistica="att_pos_medio"))

    # ---- 12.2 ----
    def _a17(self):
        g4 = json.loads((OUT / "G4_resumo.json").read_text(encoding="utf-8"))
        cursos = sorted(int(c) for c in g4["classes_dos_cursos"]["ESPECIFICO"])
        mapa = pd.read_csv(OUT / "G4_mapa_especialidade_procedimento.csv", dtype={"co_forma": str})
        mapa = mapa[mapa["tipica"].astype(str).str.lower() == "true"]
        tip = {c: set(mapa.loc[mapa["cod_curso"] == c, "co_forma"].str.zfill(6)) for c in cursos}
        cur = pd.read_csv(AQ / "sia_forma_curso" / "sia_forma_curso_cursos.csv")
        conj = {int(r.cod_curso): str(r.conjunto_cbo) for r in cur.itertuples()}
        pres = pd.read_csv(AQ / "sia_forma_curso" / "sia_forma_curso_formas_por_consulta.csv",
                           dtype={"competencia_processamento": str, "forma": str, "conjunto_cbo": str})
        pres["forma"] = pres["forma"].str.zfill(6)
        pres = set(pres.loc[pres["presente_na_resposta"].astype(str).str.lower() == "true",
                            ["competencia_processamento", "conjunto_cbo", "forma"]].itertuples(index=False, name=None))
        df = pd.read_parquet(AQ / "sia_forma_curso" / "painel_sia_municipio_mes_forma_curso.parquet",
                             columns=["co_ibge", "competencia_processamento", "cod_curso", "forma", "qtd_aprovada",
                                      "status"],
                             filters=[("competencia_processamento", "<=", "202605"), ("cod_curso", "in", cursos),
                                      ("forma", "in", sorted(set().union(*tip.values())))])
        for c in ("co_ibge", "competencia_processamento", "forma", "status"):
            df[c] = df[c].astype(str)
        df["cod_curso"] = df["cod_curso"].astype(int)
        df = df[[f in tip[c] for c, f in zip(df["cod_curso"], df["forma"])]]
        df["aus"] = (df["status"] == "municipio_ausente_da_resposta").astype(int)
        agg = df.groupby(["cod_curso", "competencia_processamento", "co_ibge"]).agg(
            q=("qtd_aprovada", "sum"), aus=("aus", "sum")).reset_index()
        agg["q"] = agg["q"].astype(float)
        agg.loc[agg["aus"] > 0, "q"] = np.nan
        out = {}
        for c in cursos:
            a = agg[agg["cod_curso"] == c].pivot(index="co_ibge", columns="competencia_processamento", values="q")
            a = a.reindex(columns=AUD_MESES)
            for m in AUD_MESES:
                if not any((m, conj[c], f) in pres for f in tip[c]):
                    a[m] = 0.0
            out[c] = a.reindex(self.U)
        return cursos, out

    def test_12_2_agregado_e_curso(self) -> None:
        cursos, a17 = self._a17()
        vc = pd.read_parquet(OUT / "outcomes" / "outcomes_V_celula.parquet", columns=["ciclo", "co_ibge", "cod_curso"])
        vc = vc[vc["ciclo"].isin([1, 2]) & vc["cod_curso"].isin(cursos)]
        vc["co_ibge"] = _aud_ib6(vc["co_ibge"])
        pares = vc.drop_duplicates(["co_ibge", "cod_curso"])
        pares = pares[pares["co_ibge"].isin(set(self.U))].sort_values(["cod_curso", "co_ibge"]).reset_index(drop=True)
        ch = self.nom[self.nom["curso_n"].isin(cursos)].groupby(["co_ibge", "curso_n"])["comp"].min()
        chp = [ch.get((m, c), np.nan) for m, c in zip(pares["co_ibge"], pares["cod_curso"])]
        G = np.array([self._coorte(c) for c in chp])
        grupo = pares["cod_curso"].to_numpy()
        clus = pares["co_ibge"].to_numpy()
        Y = np.vstack([self._taxa(a17[c], pd.Index([m]))[0] for m, c in zip(pares["co_ibge"], pares["cod_curso"])])
        self.assertEqual((len(pares), int((G >= 0).sum()), int((G < 0).sum())), (1017, 298, 719))
        att, psi, theta = aud_cs(Y, G, grupo=grupo)
        self._comparar("12.2 agregado", att, aud_ep_cluster(psi, clus),
                       self._linha(item="12.2", recorte="todos_os_cursos", estatistica="att_pos_medio"))
        # os theta(e) do estudo de evento (pré incluído) também batem
        ev = self.ev[(self.ev["item"] == "12.2") & (self.ev["recorte"] == "todos_os_cursos")
                     & (self.ev["variante"] == "principal")].set_index("e")["theta"]
        dif = max(abs(ev[e] - v) for e, v in theta.items())
        self.assertLess(dif, 1e-8)
        # um curso (14: o de maior ATT e pré que rejeita)
        for c in (14, 15):
            m = grupo == c
            a, p, _ = aud_cs(Y[m], G[m], grupo=grupo[m])
            self._comparar(f"12.2 curso {c}", a, aud_ep_cluster(p, clus[m]),
                           self._linha(item="12.2", recorte=f"curso_{c}", estatistica="att_pos_medio"))

    # ---- BKY e SDID ----
    def test_bky_proprio(self) -> None:
        b = self.est[self.est["entra_bky"].astype(bool)]
        self.assertEqual(len(b), 8)
        q = aud_bky(b["p_valor"].to_numpy(dtype=float))
        self.assertLess(float(np.abs(q - b["q_bky"].to_numpy(dtype=float)).max()), 1e-12)

    def test_sdid_pesos_plausiveis(self) -> None:
        """Plausibilidade (não é recálculo): pesos de unidade e de tempo somam 1 e não são negativos, e o ponto bate
        com a fórmula tau = (tratados pós - sum lambda pré) - sum omega (controles pós - sum lambda pré)."""
        k1 = self._k1()
        ch = self.nom.groupby("co_ibge")["comp"].min().reindex(self.amostra)
        am_a = self.amostra[~(ch.notna() & (ch > "202605")).to_numpy()]
        Y = self._taxa(k1, am_a)
        G = self._G_mun(am_a)
        g = AUD_MESES.index("202604")
        ok = np.isfinite(Y).all(axis=1)
        ctrl, trat = np.flatnonzero((G < 0) & ok), np.flatnonzero((G == g) & ok)
        r = X.sdid(np.vstack([Y[ctrl], Y[trat]]), len(ctrl), g)
        om, lam = r["omega"], r["lambda"]
        for w in (om, lam):
            self.assertAlmostEqual(float(w.sum()), 1.0, places=9)
            self.assertGreaterEqual(float(w.min()), 0.0)
        Yc, Yt = Y[ctrl], Y[trat]
        dt = Yt[:, g:].mean() - Yt[:, :g].mean(axis=0) @ lam
        dc = (Yc[:, g:].mean(axis=1) - Yc[:, :g] @ lam) @ om
        self.assertAlmostEqual(float(dt - dc), r["tau"], places=8)
        lin = self._linha(item="12.3", recorte="b_sdid_coorte_202604", estatistica="att_sdid")
        self.assertAlmostEqual(r["tau"], float(lin["valor"]), places=6)


if __name__ == "__main__":
    unittest.main()
