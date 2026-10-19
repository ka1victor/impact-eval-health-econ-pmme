"""Testes do adendo §7 do protocolo 48: `scripts/rdd_bolsa/24_abertura_vagas_selecao.py`.

Duas partes:

1. `TestSintetico`: DADOS SINTÉTICOS gerados em memória (semente fixa), rotulados como sintéticos e nunca
   gravados em `output/` nem em `data/`. Conferem a fórmula dos limites de Lee do §7 (A2), que os limites
   contêm a estimativa pontual (e coincidem com ela quando p = 0), o IC de Imbens–Manski, que o MQP rápido
   do bootstrap reproduz a rdd_lib e que o Lee extensivo daqui reproduz `rdd_lib.limites_lee_rd`.
2. `TestSaidasReais` e `TestDoc49Adendo`: esquema e rótulos de `output/rdd_bolsa/NA_*`, figuras, e os blocos
   NA do doc 49 iguais aos gerados das saídas (nenhum número digitado na prosa do adendo).
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
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "24_abertura_vagas_selecao.py"
_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location("abertura_vagas_24", SCRIPT)
NA = importlib.util.module_from_spec(_spec)
sys.modules["abertura_vagas_24"] = NA
_spec.loader.exec_module(NA)
sys.dont_write_bytecode = _bytecode
L, T23 = NA.L, NA.T23

OUT = ROOT / "output" / "rdd_bolsa"
EST = OUT / "NA_estimativas.csv"
RESUMO = OUT / "NA_resumo.json"
DOC = ROOT / "docs" / "06_execucao" / "49_resultados_contagem_vagas_preenchidas.md"

NATUREZA_SINTETICA = "SINTETICO_TESTE"   # rótulo dos dados gerados aqui; nunca gravados


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def municipios_sinteticos(semente: int = 7, n: int = 1500, n_ciclos: int = 1) -> pd.DataFrame:
    """SINTÉTICO: abertura com salto no corte e fração preenchida com salto conhecido; zero fora do quadro."""
    rng = np.random.default_rng(semente)
    s = rng.integers(220, 481, n).astype(float)
    t = ((s > 300) & (s <= 350)) | (s > 400)
    linhas = []
    for k in range(1, n_ciclos + 1):
        abre = rng.random(n) < (0.3 + 0.15 * t)
        vagas = np.where(abre, rng.integers(1, 6, n), 0).astype(float)
        frac = np.clip(0.5 + 0.1 * t + rng.normal(0, 0.2, n), 0, 1)
        preench = np.where(abre, np.round(frac * vagas), 0.0)
        pop = rng.integers(3000, 60000, n).astype(float)
        linhas.append(pd.DataFrame({
            "co_ibge": [f"9{i:05d}" for i in range(n)], "s_mil": s, "ciclo": k, "natureza_dos_dados": NATUREZA_SINTETICA,
            "ofert": vagas, "preench_lim": preench, "tem_celula": abre.astype(float), "pop": pop,
            "frac_lim": np.where(abre, preench / np.where(abre, vagas, 1.0), np.nan),
            "ofert_10k": vagas / pop * 1e4}))
    return pd.concat(linhas, ignore_index=True)


class TestSintetico(unittest.TestCase):
    """Fórmulas e estimadores em dados sintéticos (nada é gravado)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.d = municipios_sinteticos()
        cls.mapa = {c: i for i, c in enumerate(sorted(cls.d["co_ibge"].unique()))}

    def test_dados_rotulados_como_sinteticos(self) -> None:
        self.assertEqual(set(self.d["natureza_dos_dados"]), {NATUREZA_SINTETICA})

    def test_formula_dos_limites_binarios(self) -> None:
        # Sintético: f = 0,6 e p = 0,2 -> [0,5; 0,75]; truncamento em 0 e em 1.
        lo, hi = NA.limites_binario(0.6, 0.2)
        self.assertAlmostEqual(lo, 0.5)
        self.assertAlmostEqual(hi, 0.75)
        self.assertEqual(NA.limites_binario(0.1, 0.5), (0.0, 0.2))
        self.assertEqual(NA.limites_binario(0.9, 0.5)[1], 1.0)
        self.assertTrue(all(np.isnan(NA.limites_binario(0.5, 1.0))))

    def test_lee_intensivo_lado_aparado_e_sinal(self) -> None:
        # Sintético: mais vagas acima -> apara acima; salto = acima - abaixo.
        r = NA.lee_intensivo(s0=4.0, s1=5.0, f0=0.5, f1=0.6)
        self.assertEqual(r["lado"], "acima")
        self.assertAlmostEqual(r["p"], 0.2)
        self.assertAlmostEqual(r["inf"], 0.5 - 0.5)
        self.assertAlmostEqual(r["sup"], 0.75 - 0.5)
        # Mais vagas abaixo -> apara abaixo; limites = f1 - [sup, inf] do lado de baixo.
        r = NA.lee_intensivo(s0=5.0, s1=4.0, f0=0.6, f1=0.5)
        self.assertEqual(r["lado"], "abaixo")
        self.assertAlmostEqual(r["inf"], 0.5 - 0.75)
        self.assertAlmostEqual(r["sup"], 0.5 - 0.5)
        self.assertTrue(np.isnan(NA.lee_intensivo(0.0, 1.0, 0.5, 0.5)["inf"]))

    def test_limites_contem_a_estimativa_e_coincidem_com_p_zero(self) -> None:
        rng = np.random.default_rng(3)
        for _ in range(500):
            s0, s1 = rng.uniform(0.5, 5, 2)
            f0, f1 = rng.uniform(0, 1, 2)
            r = NA.lee_intensivo(s0, s1, f0, f1)
            self.assertLessEqual(r["inf"], f1 - f0 + 1e-12)
            self.assertGreaterEqual(r["sup"], f1 - f0 - 1e-12)
        r = NA.lee_intensivo(3.0, 3.0, 0.4, 0.55)
        self.assertEqual(r["p"], 0.0)
        self.assertAlmostEqual(r["inf"], 0.15)
        self.assertAlmostEqual(r["sup"], 0.15)

    def test_imbens_manski(self) -> None:
        # Intervalo degenerado: c = 1,96; intervalo largo: c -> 1,645.
        lo, hi = NA.ic_imbens_manski(0.0, 0.0, 1.0, 1.0)
        self.assertAlmostEqual(hi, L.Z_975, places=6)
        lo, hi = NA.ic_imbens_manski(0.0, 100.0, 1.0, 1.0)
        self.assertAlmostEqual(-lo, 1.6448536, places=5)
        self.assertTrue(np.isnan(NA.ic_imbens_manski(0.0, 1.0, np.nan, 1.0)[0]))

    def _amostras(self):
        a1 = T23.montar_amostra([(self.d, 300, "300")], empilhada=False)
        a2 = T23.montar_amostra([(self.d, c, str(c)) for c in (300, 400)], empilhada=True)
        return a1, a2

    def test_desenho_rapido_reproduz_rdd_lib(self) -> None:
        for a in self._amostras():
            D = NA.Desenho(a, self.mapa)
            for y, peso in (("ofert_10k", None), ("frac_lim", "ofert")):
                pv = a.col(peso) if peso else None
                ref = T23.ajustar(a, a.col(y), NA.H, peso=pv)
                NA.conferir_desenho(D, a, a.col(y), pv, ref)   # levanta FalhaValidacao se divergir

    def test_multiplicidade_igual_a_duplicar_linhas(self) -> None:
        a = self._amostras()[1]
        D = NA.Desenho(a, self.mapa)
        m = np.zeros(len(self.mapa))
        m[: len(m) // 2] = 2.0
        r = D.ajustar(a.col("ofert_10k"), None, m)
        dup = pd.concat([self.d[self.d["co_ibge"].map(self.mapa) < len(self.mapa) // 2]] * 2, ignore_index=True)
        b = T23.montar_amostra([(dup, c, str(c)) for c in (300, 400)], empilhada=True)
        ref = T23.ajustar(b, b.col("ofert_10k"), NA.H)
        self.assertAlmostEqual(r["tau"], ref["tau"], places=9)

    def test_lee_extensivo_igual_rdd_lib(self) -> None:
        a = self._amostras()[0]
        D = NA.Desenho(a, self.mapa)
        meu = NA.lee_extensivo_desenho(D, D.janela(a.col("tem_celula")), D.janela(a.col("frac_lim")), None)
        ref = L.limites_lee_rd(a.s, a.col("frac_lim"), a.col("tem_celula"), 300, NA.H, empates=NA.EMPATES_LEE)
        for x, z in ((meu["inf"], ref["tau_inf"]), (meu["sup"], ref["tau_sup"]), (meu["q"], ref["q_aparo"]),
                     (meu["ingenuo"], ref["tau_selecionados"])):
            self.assertAlmostEqual(x, z, places=9)
        self.assertLessEqual(meu["inf"], meu["ingenuo"])
        self.assertGreaterEqual(meu["sup"], meu["ingenuo"])

    def test_lee_extensivo_nao_depende_da_ordem_das_linhas(self) -> None:
        # Sintético (auditoria 22): a fração tem muitos empates (0 e 1); embaralhar as linhas não muda os limites.
        self.assertEqual(NA.EMPATES_LEE, "proporcional")
        a = self._amostras()[0]
        perm = np.random.default_rng(11).permutation(len(self.d))
        b = T23.montar_amostra([(self.d.iloc[perm].reset_index(drop=True), 300, "300")], empilhada=False)
        r = []
        for x in (a, b):
            D = NA.Desenho(x, self.mapa)
            r.append(NA.lee_extensivo_desenho(D, D.janela(x.col("tem_celula")), D.janela(x.col("frac_lim")), None))
        self.assertAlmostEqual(r[0]["inf"], r[1]["inf"], places=9)
        self.assertAlmostEqual(r[0]["sup"], r[1]["sup"], places=9)

    def test_bootstrap_deterministico(self) -> None:
        a1 = self._amostras()[0]
        D = NA.Desenho(a1, self.mapa)
        e = {"DU": D, "DV": D, "args": {"int": (D.janela(a1.col("ofert_10k")), None, D.janela(a1.col("frac_lim")),
                                                D.janela(a1.col("ofert"))),
                                        "int_pop": (D.janela(a1.col("ofert_10k")), D.janela(a1.col("pop")),
                                                    D.janela(a1.col("frac_lim")), D.janela(a1.col("ofert"))),
                                        "ext": (D.janela(a1.col("tem_celula")), D.janela(a1.col("frac_lim")))}}
        e2 = {k: v for k, v in e.items()}
        NA.bootstrap_a2([e], len(self.mapa), n_boot=5, log=lambda *_: None)
        NA.bootstrap_a2([e2], len(self.mapa), n_boot=5, log=lambda *_: None)
        self.assertEqual(e["boot"]["int"]["inf"], e2["boot"]["int"]["inf"])

    def test_fonte_sem_ivs_errado_e_sem_fillna_zero(self) -> None:
        fonte = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("ivs_ipea_2010_municipios", fonte)
        self.assertNotIn("fillna(0", fonte)
        self.assertIn('("competencia", "<=", COMP_PRE[1])', fonte)


@unittest.skipUnless(EST.exists() and RESUMO.exists(), "saidas do adendo §7 ausentes")
class TestSaidasReais(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.est = pd.read_csv(EST, dtype={"corte": str, "ciclo": str})
        cls.resumo = json.loads(RESUMO.read_text(encoding="utf-8"))

    def test_esquema_e_rotulos(self) -> None:
        self.assertEqual(list(self.est.columns), NA.COLUNAS)
        self.assertTrue((self.est["natureza_dos_dados"] == "EMPIRICO").all())
        self.assertTrue((self.est["estatuto"] == "PROTOCOLO_48_ADENDO_7_POS_RESULTADO").all())
        self.assertTrue((self.est["familia"] == "N_ADENDO_7").all())
        self.assertEqual(self.resumo["natureza_dos_dados"], "EMPIRICO")
        self.assertEqual(self.resumo["estatuto"], "PROTOCOLO_48_ADENDO_7_POS_RESULTADO")
        self.assertTrue(set(self.est["status"]) <= {"EXECUTADO", "SEM_ESTIMATIVA", "NAO_EXECUTADO"})
        self.assertFalse(self.est["entra_holm"].astype(bool).any())

    def test_nan_sempre_com_nota(self) -> None:
        nucleo = ["tau", "ep", "ic95_inf", "ic95_sup", "p_valor"]
        ruins = self.est[self.est[nucleo].isna().any(axis=1) & (self.est["nota"].fillna("") == "")]
        self.assertEqual(len(ruins), 0)

    def test_quatro_analises_e_grade_completa(self) -> None:
        self.assertEqual(set(self.est["especificacao"]), {"A1", "A2", "A3", "A4"})
        a2 = self.est[self.est["especificacao"] == "A2"]
        self.assertEqual(len(a2), 12 * 3)
        a1 = self.est[(self.est["especificacao"] == "A1") & (self.est["variante"] == "principal")]
        self.assertTrue((a1["populacao"] == "U").all())
        self.assertEqual(len(a1), 12 * 3)

    def test_lee_contem_salto_ingenuo_e_formula_nas_saidas(self) -> None:
        a2 = self.est[(self.est["especificacao"] == "A2") & self.est["lee_limite_inf"].notna()]
        self.assertTrue(len(a2) > 0)
        it = a2[a2["outcome_id"] == "A2_INTENSIVA"]
        # Margem intensiva: pela fórmula do §7, os limites sempre contêm o salto ingênuo.
        self.assertTrue((it["lee_limite_inf"] <= it["tau"] + 1e-9).all())
        self.assertTrue((it["lee_limite_sup"] >= it["tau"] - 1e-9).all())
        # Margem extensiva: com reta local isso não é garantido; quando falha, a linha diz.
        ex = a2[a2["outcome_id"] == "A2_EXTENSIVA"]
        fora = ex[(ex["lee_limite_inf"] > ex["tau"] + 1e-12) | (ex["lee_limite_sup"] < ex["tau"] - 1e-12)]
        self.assertTrue(fora["nota"].str.contains("salto ingenuo fora dos limites").all())
        self.assertTrue((a2["ic_im_inf"] <= a2["lee_limite_inf"]).all() and (a2["ic_im_sup"] >= a2["lee_limite_sup"]).all())
        for r in it.to_dict("records"):
            x = NA.lee_intensivo(r["taxa_selecao_abaixo"], r["taxa_selecao_acima"], r["taxa_preench_abaixo"],
                                 r["taxa_preench_acima"])
            self.assertAlmostEqual(x["inf"], r["lee_limite_inf"], places=10)
            self.assertAlmostEqual(x["sup"], r["lee_limite_sup"], places=10)
            self.assertAlmostEqual(x["p"], r["lee_p_aparo"], places=10)
        self.assertTrue((a2["n_boot"] >= 999).all())

    def test_lacunas_documentadas_como_nao_executado(self) -> None:
        ne = self.est[self.est["status"] == "NAO_EXECUTADO"]
        self.assertIn("efeito_fixo_tipo_pratica", set(ne["variante"]))
        self.assertIn("covariavel_estabelecimentos_hospitalares", set(ne["variante"]))
        self.assertTrue((ne["nota"].str.len() > 0).all())
        self.assertIn("tipo_de_pratica", self.resumo["atributos_celula"]["ausentes"])

    def test_hashes_das_entradas_conferem(self) -> None:
        for e in self.resumo["entradas"]:
            self.assertEqual(sha256(ROOT / e["caminho"]), e["sha256"], e["caminho"])
        self.assertEqual(sha256(EST), self.resumo["saidas"]["NA_estimativas.csv"]["sha256"])
        self.assertEqual(self.resumo["protocolo"]["sha256"], sha256(ROOT / self.resumo["protocolo"]["arquivo"]))

    def test_cnes_so_pre_programa(self) -> None:
        comps = self.resumo["cnes_pre"]["competencias"]
        self.assertEqual((comps[0], comps[-1]), ("202406", "202506"))

    def test_figuras_existem_e_titulos_batem_com_o_csv(self) -> None:
        figs = self.resumo["saidas"]["figuras"]
        nomes = {Path(f["arquivo"]).name for f in figs}
        self.assertEqual(nomes, {"NA_A1_por_10k_empilhado.png", "NA_A3_celula_preenchida_empilhado.png"})
        for f in figs:
            caminho = ROOT / f["arquivo"]
            self.assertTrue(caminho.exists() and caminho.stat().st_size > 10_000, f["arquivo"])
            self.assertEqual(caminho.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
            for p in f["paineis"]:
                m = np.ones(len(self.est), dtype=bool)
                for k in ("outcome_id", "populacao", "ciclo", "corte", "especificacao", "variante"):
                    m &= self.est[k].astype(str) == str(p[k])
                self.assertEqual(int(m.sum()), 1, p)
                r = self.est[m].iloc[0]
                for c in ("tau", "ic95_inf", "ic95_sup", "p_valor"):
                    self.assertAlmostEqual(float(r[c]), p[c], places=12)

    def test_saidas_da_familia_n_nao_lidas_como_escrita(self) -> None:
        # O script 24 só lê N_estimativas.csv; o hash registrado confere com o arquivo atual.
        lidos = {e["caminho"]: e["sha256"] for e in self.resumo["entradas"]}
        self.assertIn("output/rdd_bolsa/N_estimativas.csv", lidos)


OUTC = OUT / "outcomes"


def _rdd_independente(s, c, g, cl, y, *, empilhada: bool, cluster: bool, colunas_extra=(), fe=None, peso=None):
    """Auditoria 22: MQP local linear escrito do zero (não usa rdd_lib nem o script 24). Devolve salto, EP,
    interceptos do lado de baixo por grupo e pesos omega_g."""
    x_mil = s - c
    w = np.where((x_mil > -NA.H) & (x_mil < NA.H), 1 - np.abs(x_mil) / NA.H, 0.0)
    if peso is not None:
        w = w * peso
    t = (x_mil > 0).astype(float)
    x = x_mil / 1000
    grupos = sorted(np.unique(g))
    cols = []
    for gl in grupos:
        ind = (g == gl).astype(float)
        cols += [ind, ind * x, ind * t * x]
    cols.append(t)
    n_estr = len(cols)
    if fe is not None:
        for nivel in sorted(np.unique(fe))[1:]:
            cols.append((fe == nivel).astype(float))
    cols += list(colunas_extra)
    X = np.column_stack(cols)
    ok = (w > 0) & np.isfinite(y) & np.isfinite(X).all(axis=1)
    X, yy, ww = X[ok], y[ok], w[ok]
    # Colunas de efeito fixo sem variação ou colineares com as estruturais saem, na ordem dada.
    manter = list(range(n_estr))
    sw = np.sqrt(ww)
    for j in range(n_estr, X.shape[1]):
        M = X[:, manter + [j]] * sw[:, None]
        M = M / np.where(np.linalg.norm(M, axis=0) > 0, np.linalg.norm(M, axis=0), 1.0)
        if np.linalg.matrix_rank(M, tol=1e-9) == len(manter) + 1:
            manter.append(j)
    X = X[:, manter]
    B = np.linalg.inv(X.T @ (X * ww[:, None]))
    b = B @ (X.T @ (ww * yy))
    e = yy - X @ b
    sc = X * (ww * e)[:, None]
    n, k = X.shape
    iT = n_estr - 1
    if cluster:
        _, ids = np.unique(cl[ok], return_inverse=True)
        G = ids.max() + 1
        S = np.zeros((G, k))
        np.add.at(S, ids, sc)
        V = B @ S.T @ S @ B * (G / (G - 1)) * ((n - 1) / (n - k))
    else:
        V = B @ sc.T @ sc @ B * n / (n - k)
    a = (B[iT] @ X.T) * ww
    gg, tt = g[ok], t[ok]
    return {"tau": b[iT], "ep": float(np.sqrt(V[iT, iT])), "const": {gl: b[3 * i] for i, gl in enumerate(grupos)},
            "omega": {gl: float(np.sum(a[gg == gl] * tt[gg == gl])) for gl in grupos}}


@unittest.skipUnless(EST.exists() and (OUTC / "outcomes_U_municipio.parquet").exists(), "saidas ou outcomes ausentes")
class TestRecalculoIndependenteAuditoria22(unittest.TestCase):
    """Auditoria 22: linhas principais recalculadas dos parquets da tarefa B, com o IVS oficial dos outcomes."""

    @classmethod
    def setUpClass(cls) -> None:
        import pyarrow.parquet as pq
        cls.est = pd.read_csv(EST, dtype={"corte": str, "ciclo": str})
        U = pd.read_parquet(OUTC / "outcomes_U_municipio.parquet")
        U = U[U["ivs_2010_oficial"].notna()].reset_index(drop=True)
        VM = pd.read_parquet(OUTC / "outcomes_V_municipio.parquet")
        C = pd.read_parquet(OUTC / "outcomes_V_celula.parquet")
        C["vic"] = C["vagas_imediatas"].astype(float) + C["vagas_cr"].astype(float)
        C["lim"] = np.minimum(C["n_alocados_ch1"].astype(float), C["vic"])
        t = pq.read_table(ROOT / "output/aquisicao/cnes_nacional/painel_municipio_cbo_mes.parquet",
                          columns=["co_ibge", "competencia", "grupo", "n_profissionais_distintos"],
                          filters=[("competencia", ">=", "202406"), ("competencia", "<=", "202506"),
                                   ("grupo", "in", ["alvo_pmme", "generalistas"])]).to_pandas()
        est_cnes = t.groupby(["co_ibge", "grupo"])["n_profissionais_distintos"].mean().unstack()
        smap = U.set_index("co_ibge")["ivs_2010_oficial"].mul(1000).round()
        pop = U.set_index("co_ibge")["populacao_2022"].astype(float)
        cls.U, cls.V, cls.C = {}, {}, {}
        for k in (1, 2, 3):
            v = VM[(VM["ciclo"] == k) & VM["ivs_2010_oficial"].notna()].copy()
            v["s"] = (v["ivs_2010_oficial"] * 1000).round()
            v["ofert"] = v["vagas_imediatas"].astype(float) + v["vagas_cr"].astype(float)
            v["lim"] = v["co_ibge"].map(C[C["ciclo"] == k].groupby("co_ibge")["lim"].sum())
            v["frac"] = v["lim"] / v["ofert"]
            v["preench"] = v["n_alocados_ch1"].astype(float)
            v["log_pop"] = np.log(v["co_ibge"].map(pop))
            v["alvo"] = v["co_ibge"].map(est_cnes["alvo_pmme"])
            v["gen"] = v["co_ibge"].map(est_cnes["generalistas"])
            cls.V[k] = v
            u = pd.DataFrame({"co_ibge": U["co_ibge"], "s": (U["ivs_2010_oficial"] * 1000).round(),
                              "pop": U["populacao_2022"].astype(float)})
            vi = v.set_index("co_ibge")
            no_q = u["co_ibge"].isin(vi.index)
            u["ofert"] = U[f"vagas_imediatas_c{k}"].astype(float) + U[f"vagas_cr_c{k}"].astype(float)
            u["preench"] = np.where(no_q, u["co_ibge"].map(vi["preench"]), 0.0)   # zero verdadeiro fora do quadro
            u["sel"] = no_q.astype(float)
            u["frac"] = np.where(no_q, u["co_ibge"].map(vi["frac"]), np.nan)
            u["ofert_10k"] = u["ofert"] / u["pop"] * 1e4
            u["preench_10k"] = u["preench"] / u["pop"] * 1e4
            cls.U[k] = u
            c_ = C[C["ciclo"] == k].copy()
            c_["s"] = c_["co_ibge"].map(smap)
            c_ = c_[c_["s"].notna()].copy()
            c_["fe"] = f"c{k}_" + c_["cod_curso"].astype(int).astype(str).str.zfill(2)
            cls.C[k] = c_

    @staticmethod
    def _emp(frames):
        partes = [f.assign(c=float(c), g=f"c{k}_{c}") for k, f in frames.items() for c in (300, 400)]
        d = pd.concat(partes, ignore_index=True)
        return d, d["s"].to_numpy(float), d["c"].to_numpy(float), d["g"].to_numpy(str), d["co_ibge"].to_numpy(str)

    def _ref(self, **f):
        m = np.ones(len(self.est), dtype=bool)
        for k, v in f.items():
            m &= self.est[k].astype(str) == str(v)
        self.assertEqual(int(m.sum()), 1, f)
        return self.est[m].iloc[0]

    def test_a1_a3_a4_principais(self) -> None:
        d, s, c, g, cl = self._emp(self.U)
        for oid, col in (("A1_PREENCH_10K", "preench_10k"), ("A1_OFERT_10K", "ofert_10k")):
            r = _rdd_independente(s, c, g, cl, d[col].to_numpy(float), empilhada=True, cluster=True)
            ref = self._ref(especificacao="A1", outcome_id=oid, variante="principal", ciclo="1+2+3", corte="empilhado")
            self.assertAlmostEqual(r["tau"], ref["tau"], places=10)
            self.assertAlmostEqual(r["ep"], ref["ep"], places=10)
        d, s, c, g, cl = self._emp(self.C)
        r = _rdd_independente(s, c, g, cl, (d["n_alocados_ch1"] >= 1).astype(float).to_numpy(), empilhada=True,
                              cluster=True, fe=d["fe"].to_numpy(str),
                              colunas_extra=[d["com_vagas_imediatas"].to_numpy(float)])
        ref = self._ref(especificacao="A3", outcome_id="A3_PREENCHIDA", variante="principal",
                        populacao="V1+V2+V3 (celulas)", corte="empilhado")
        self.assertAlmostEqual(r["tau"], ref["tau"], places=10)
        self.assertAlmostEqual(r["ep"], ref["ep"], places=10)
        d, s, c, g, cl = self._emp(self.V)
        extra = [np.where(g == gl, d[cv].to_numpy(float), 0.0) for cv in ("log_pop", "alvo", "gen")
                 for gl in sorted(np.unique(g))]
        r = _rdd_independente(s, c, g, cl, d["preench"].to_numpy(float), empilhada=True, cluster=True,
                              colunas_extra=extra)
        ref = self._ref(especificacao="A4", outcome_id="N1", variante="com_covariaveis", populacao="V1+V2+V3",
                        corte="empilhado")
        self.assertAlmostEqual(r["tau"], ref["tau"], places=8)
        self.assertAlmostEqual(r["ep"], ref["ep"], places=8)

    def test_a2_limites_empilhados(self) -> None:
        du, s, c, g, cl = self._emp(self.U)
        dv, sv, cv, gv, clv = self._emp(self.V)
        rs = _rdd_independente(s, c, g, cl, du["ofert_10k"].to_numpy(float), empilhada=True, cluster=True)
        rf = _rdd_independente(sv, cv, gv, clv, dv["frac"].to_numpy(float), empilhada=True, cluster=True,
                               peso=dv["ofert"].to_numpy(float))
        s0 = sum(rs["omega"][k] * rs["const"][k] for k in rs["omega"])
        s1 = s0 + rs["tau"]
        f0 = sum(rs["omega"][k] * rf["const"][k] for k in rs["omega"])
        f1 = f0 + rf["tau"]
        self.assertGreater(s0, s1)                      # mais vagas por habitante abaixo: apara abaixo
        p = (s0 - s1) / s0
        lo, hi = max(0.0, (f0 - p) / (1 - p)), min(1.0, f0 / (1 - p))
        ref = self._ref(especificacao="A2", variante="margem_intensiva_vaga", ciclo="1+2+3", corte="empilhado")
        self.assertEqual(ref["lee_lado_aparado"], "abaixo")
        self.assertAlmostEqual(f1 - hi, ref["lee_limite_inf"], places=10)
        self.assertAlmostEqual(f1 - lo, ref["lee_limite_sup"], places=10)
        # Extensiva, com empates repartidos proporcionalmente dentro de cada grupo do lado de maior abertura.
        rsel = _rdd_independente(s, c, g, cl, du["sel"].to_numpy(float), empilhada=True, cluster=True)
        p0 = sum(rsel["omega"][k] * rsel["const"][k] for k in rsel["omega"])
        p1 = p0 + rsel["tau"]
        q = (p0 - p1) / p0 if p0 > p1 else (p1 - p0) / p1
        x = s - c
        w = np.where((x > -NA.H) & (x < NA.H), 1 - np.abs(x) / NA.H, 0.0)
        y = du["frac"].to_numpy(float)
        lado_t = (x > 0) if p1 >= p0 else (x <= 0)
        taus = []
        for de_cima in (True, False):
            mult = np.ones(len(y))
            for gl in np.unique(g):
                m = (du["sel"].to_numpy() == 1) & (w > 0) & (g == gl) & lado_t
                yv, wv = y[m], w[m]
                alvo, acum, mm = q * wv.sum(), 0.0, np.ones(m.sum())
                for v in (np.unique(yv)[::-1] if de_cima else np.unique(yv)):
                    e = yv == v
                    if acum >= alvo:
                        break
                    mm[e] = 1 - min(alvo - acum, wv[e].sum()) / wv[e].sum()
                    acum += wv[e].sum()
                mult[m] = mm
            taus.append(_rdd_independente(s, c, g, cl, y, empilhada=True, cluster=True, peso=mult)["tau"])
        ref = self._ref(especificacao="A2", variante="margem_extensiva_abertura", ciclo="1+2+3", corte="empilhado")
        self.assertAlmostEqual(min(taus), ref["lee_limite_inf"], places=10)
        self.assertAlmostEqual(max(taus), ref["lee_limite_sup"], places=10)


@unittest.skipUnless(DOC.exists() and EST.exists(), "doc 49 ou saidas do adendo ausentes")
class TestDoc49Adendo(unittest.TestCase):
    def test_blocos_iguais_aos_gerados(self) -> None:
        est, resumo = NA.ler_saidas()
        n_est, e9 = NA.ler_auxiliares()
        geradas = NA.gerar_tabelas_doc(est, resumo, n_est, e9)
        no_doc = NA.tabelas_no_doc(DOC.read_text(encoding="utf-8"))
        self.assertEqual(set(no_doc), set(geradas))
        for nome, corpo in no_doc.items():
            self.assertEqual(corpo, geradas[nome], nome)

    def test_prosa_do_adendo_sem_numero_de_resultado(self) -> None:
        texto = DOC.read_text(encoding="utf-8")
        texto = texto[texto.index("## 15. Adendo §7"):]
        texto = NA.MARCA.sub("", texto)
        texto = re.sub(r"`[^`]*`", "", texto)
        texto = re.sub(r"\]\([^)]*\)", "]", texto)
        texto = re.sub(r"(?m)^#+ .*$", "", texto)
        texto = re.sub(r"§+\s?\d+", "", texto)
        texto = re.sub(r"\b(?:docs?|protocolo|seção)\s+\d+", "", texto)
        texto = re.sub(r"\b[A-Za-z_]+\d+[a-z]?\b", "", texto)
        texto = re.sub(r"\d+ª", "", texto)
        decimais = set(re.findall(r"(?<![\w.,])[−+-]?\d+[,.]\d+", texto))
        self.assertEqual(decimais - {"0,050", "0,300", "0,400", "0,010"}, set())
        sem_dec = re.sub(r"(?<![\w.,])[−+-]?\d+[,.]\d+", "", texto)
        inteiros = set(re.findall(r"(?<![\w.,])[−+-]?\d+(?![\w.,]\d)", sem_dec))
        self.assertEqual(inteiros - {"1", "5", "10", "2022"}, set())

    def test_leitura_conjunta_relata_ciclo_1(self) -> None:
        corpo = NA.tabelas_no_doc(DOC.read_text(encoding="utf-8"))["leitura_conjunta"]
        self.assertIn("**Ciclo 1**", corpo)
        self.assertIn("**Todos os ciclos empilhados**", corpo)

    def test_leitura_conjunta_sem_afirmar_efeito_nulo(self) -> None:
        # Auditoria 22: IC que contém zero é falta de evidência; a regra não afirma "não é efeito" nem "o único".
        corpo = NA.tabelas_no_doc(DOC.read_text(encoding="utf-8"))["leitura_conjunta"]
        for frase in ("não com efeito sobre o preenchimento", "o único salto que exclui zero é",
                      "não o preenchimento das vagas abertas"):
            self.assertNotIn(frase, corpo)
        self.assertIn("pacote do corte", corpo)
        self.assertIn("não efeito da participação no PMM-E", corpo)


if __name__ == "__main__":
    unittest.main()
