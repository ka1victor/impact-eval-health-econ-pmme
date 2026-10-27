"""Testes do adendo 52e: `scripts/rdd_bolsa/50_escolha_localizacao_par.py`.

Partes:

1. `TestSintetico`: DADOS SINTÉTICOS gerados em memória, rotulados `SINTETICO_TESTE` e nunca gravados. Conferem a
   comparação do portão, a janela do VL-2, a retirada de pares sem escolha e de efeitos fixos separados, as
   componentes e as bases dos indicadores de par, a recuperação do peso da bolsa num logit condicional com efeito fixo
   do par (com a função `estimar` do script 25), a diferença pelo sanduíche conjunto e as regras de leitura do §3.
2. `TestPortaoReal`: o resumo registra o portão VL-5 aprovado, e as referências gravadas em `VL_estimativas.csv` batem
   com `VC_estimativas.csv`, `VD_estimativas.csv` e `P1h_magnitudes.csv`.
3. `TestNumeros`: rótulos e hashes; razão de chances, IC, p, Holm, BKY, km e diferença recalculados das linhas, da
   covariância e das funções de influência gravadas; termos absorvidos fora; contagens de identificação coerentes;
   leitura refeita; integridade.
4. `TestDoc57x`: o doc 57x é igual ao gerado, tem os marcadores e nenhum número de resultado fora dos blocos, e as
   decisões são as do pré-registro.
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
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "50_escolha_localizacao_par.py"
_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location("escolha_localizacao_par_50", SCRIPT)
M = importlib.util.module_from_spec(_spec)
sys.modules["escolha_localizacao_par_50"] = M
_spec.loader.exec_module(M)
sys.dont_write_bytecode = _bytecode

OUT = ROOT / "output" / "rdd_bolsa"
CSV = OUT / "VL_estimativas.csv"
RESUMO = OUT / "VL_resumo.json"
FIG = OUT / "VL_figuras" / "VL_razao_chances_e_km.png"
DOC = ROOT / "docs" / "06_execucao" / "57x_resultados_escolha_localizacao_par.md"
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
    """Escrita no teste: absoluta até 1, relativa acima; NaN só com NaN."""
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    assert (np.isnan(a) == np.isnan(b)).all(), "NaN em só um dos lados"
    ok = ~np.isnan(a)
    return float(np.max(np.abs(a[ok] - b[ok]) / np.maximum(1.0, np.abs(b[ok])))) if ok.any() else 0.0


def desenho_sintetico(blocos: list[list[str]], escolhas: list[int], conjunto: list[str] | None = None) -> dict:
    """Desenho no formato do script 25: cada grupo é a lista de rótulos de par das suas linhas; `escolhas` é a posição
    escolhida dentro do grupo. SINTÉTICO."""
    tam = np.array([len(b) for b in blocos], dtype=np.int64)
    starts = np.concatenate([[0], np.cumsum(tam)[:-1]]).astype(np.int64)
    grp = np.repeat(np.arange(len(blocos)), tam)
    esc = starts + np.array(escolhas, dtype=np.int64)
    G = pd.DataFrame({"natureza_dos_dados": NATUREZA_SINTETICA, "posto": 1, "id_candidato": np.arange(len(blocos)),
                      "cluster_conjunto": conjunto or ["c"] * len(blocos),
                      "cluster_candidato": np.arange(len(blocos))})
    par = np.concatenate([np.array(b, dtype=object) for b in blocos])
    return {"cel": np.arange(len(par)), "grp": grp, "starts": starts, "esc": esc, "tam": tam, "grupos": G,
            "conj": pd.DataFrame({"x": np.arange(len(par))}), "dist_km": np.zeros(len(par)),
            "mesmo_municipio": np.zeros(len(par)), "mesma_uf": np.zeros(len(par)),
            "mesma_regiao_saude": np.zeros(len(par)), "_par": par}


# ---------------------------------------------------------------------------
# 1. Sintético (só em memória)
# ---------------------------------------------------------------------------

class TestSintetico(unittest.TestCase):
    """Tudo aqui é sintético, gerado em memória e rotulado SINTETICO_TESTE."""

    def test_dif_rel(self) -> None:
        self.assertEqual(M._dif_rel([0.3], [0.3]), 0.0)
        self.assertGreater(M._dif_rel([0.3 + 2e-8], [0.3]), TOL)
        self.assertLessEqual(M._dif_rel([812.3456789 + 5e-7], [812.3456789]), TOL)
        self.assertEqual(M._dif_rel([np.nan], [0.1]), float("inf"))
        self.assertEqual(M._dif_rel([np.nan], [np.nan]), 0.0)

    def test_janela_fechada_nos_dois_cortes(self) -> None:
        s = np.array([249, 250, 300, 350, 351, 400, 450, 451, 600])
        np.testing.assert_array_equal(M.na_janela(s), [False, True, True, True, True, True, True, False, False])
        self.assertEqual(M.LIMITE_JANELAS_MIL, 350)

    def test_retira_par_sem_escolha_e_grupo_de_uma_alternativa(self) -> None:
        # Origem única "o"; par "o|C" nunca é escolhido: sai; o 3º grupo fica só com uma linha e sai.
        D = desenho_sintetico([["o|A", "o|A", "o|B", "o|C"], ["o|A", "o|B", "o|C"], ["o|B", "o|C"]], [0, 1, 0])
        cod, _ = pd.factorize(pd.Series(D["_par"]))
        manter, grupo_ok, cont = M.filtrar_pares(D, cod, np.zeros(len(cod), dtype=np.int64))
        self.assertEqual(manter.tolist(), [True, True, True, False, True, True, False, False, False])
        self.assertEqual(grupo_ok.tolist(), [True, True, False])
        self.assertEqual(cont["alternativas_retiradas_par_sem_escolha"], 3)
        self.assertTrue(manter[D["esc"][grupo_ok]].all())
        Dn = M.recortar_desenho(D, manter, grupo_ok)
        self.assertEqual(Dn["starts"].tolist(), [0, 3])
        self.assertEqual(Dn["esc"].tolist(), [0, 4])
        self.assertEqual(len(Dn["grupos"]), 2)

    def test_separacao_mais_infinito(self) -> None:
        # Todo candidato que vê "o|B" escolheu em "o|B" e o 1º também vê "o|A": o 1º perde "o|A".
        D = desenho_sintetico([["o|A", "o|B", "o|B"], ["o|A", "o|A"], ["o|B", "o|B"]], [1, 0, 0])
        cod, _ = pd.factorize(pd.Series(D["_par"]))
        sep = M.conjuntos_separados(D["grp"], cod, np.zeros(3, dtype=np.int64), cod[D["esc"]], np.arange(3))
        self.assertEqual(sep, {0: {int(cod[1])}})
        manter, grupo_ok, cont = M.filtrar_pares(D, cod, np.zeros(len(cod), dtype=np.int64))
        self.assertEqual(manter.tolist(), [False, True, True, True, True, True, True])
        self.assertEqual(cont["alternativas_retiradas_por_separacao"], 1)
        self.assertEqual(cont["candidatos_com_alternativas_retiradas_por_separacao"], 1)
        # Sem separação: o fecho de cada par cobre tudo o que os candidatos veem.
        D2 = desenho_sintetico([["o|A", "o|B"], ["o|A", "o|B"]], [0, 1])
        cod2, _ = pd.factorize(pd.Series(D2["_par"]))
        self.assertEqual(M.conjuntos_separados(D2["grp"], cod2, np.zeros(2, dtype=np.int64), cod2[D2["esc"]],
                                               np.arange(2)), {})

    def test_componentes_e_bases(self) -> None:
        o = np.array(["11"] * 6 + ["22"] * 2, dtype=object)
        v = np.array(["11", "12", "13", "14", "13", "14", "22", "11"], dtype=object)
        grp = np.array([0, 0, 1, 1, 2, 2, 3, 3])
        esc = np.array([0, 3, 5, 7])
        comp = M.componentes_de_pares(grp, pd.Series(o) + "|" + pd.Series(v))
        self.assertEqual(comp["11|11"], comp["11|12"])
        self.assertEqual(comp["11|13"], comp["11|14"])
        self.assertNotEqual(comp["11|11"], comp["11|13"])
        col, nomes, bases = M.colunas_ef(o, v, o, esc, grp)
        self.assertEqual(len(bases), 3)                      # duas componentes na origem 11, uma na 22
        base_set = {b for b, _ in bases.values()}
        self.assertIn("11|11", base_set)                     # par da própria UF
        self.assertIn("11|14", base_set)                     # componente sem a própria UF: o mais escolhido
        self.assertIn("22|11", base_set)                     # própria UF sem escolha: o mais escolhido
        self.assertEqual(sorted(nomes), ["ef_par_11_12", "ef_par_11_13", "ef_par_22_22"])
        self.assertEqual((col >= 0).sum(), 4)

    def test_efeito_fixo_do_par_recupera_a_bolsa(self) -> None:
        """Logit condicional sintético: a utilidade tem efeito do par correlacionado com a bolsa; o modelo com os
        indicadores de par (função estimar do 25) recupera β; sem eles, β fica viesado."""
        rng = np.random.default_rng(52)
        n_cand, n_cel = 3000, 24
        uf_cel = np.repeat(np.array(["31", "32", "33"]), 8)
        bolsa = np.concatenate([[10.0, 10.0, 10.0, 10.0, 15.0, 15.0, 15.0, 20.0],      # UF 31: bolsas menores
                                [10.0, 10.0, 15.0, 15.0, 15.0, 20.0, 20.0, 20.0],
                                [15.0, 15.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0]])     # UF 33: bolsas maiores
        alfa = {("31", "31"): 0.0, ("31", "32"): -1.0, ("31", "33"): 0.8, ("32", "32"): 0.0, ("32", "31"): 0.5,
                ("32", "33"): 1.2, ("33", "33"): 0.0, ("33", "31"): -0.4, ("33", "32"): 0.9}
        uf_bolsa = {"31": -0.6, "32": 0.0, "33": 0.7}       # UFs de bolsa média maior também são mais preferidas
        beta, gama = 0.08, 0.5
        x = rng.normal(size=n_cel)
        origem = rng.choice(["31", "32", "33"], size=n_cand)
        escolhas = []
        for i in range(n_cand):
            u = (beta * bolsa + gama * x + np.array([alfa[(origem[i], u_)] + uf_bolsa[u_] for u_ in uf_cel]) +
                 rng.gumbel(size=n_cel))
            escolhas.append(int(np.argmax(u)))
        blocos = [[f"{origem[i]}|{u_}" for u_ in uf_cel] for i in range(n_cand)]
        conjunto = [f"s{i % 20}" for i in range(n_cand)]
        D = desenho_sintetico(blocos, escolhas, conjunto)
        o_lin = np.repeat(origem, n_cel).astype(object)
        v_lin = np.tile(uf_cel, n_cand).astype(object)
        col, nomes, _ = M.colunas_ef(o_lin, v_lin, o_lin, D["esc"], D["grp"])
        X = pd.DataFrame({B: np.tile(bolsa, n_cand), "x": np.tile(x, n_cand)})
        Z = np.zeros((len(X), len(nomes)))
        Z[np.flatnonzero(col >= 0), col[col >= 0]] = 1.0
        Xf = pd.concat([X, pd.DataFrame(Z, columns=nomes)], axis=1)
        r = M.P1.estimar(Xf, D, modelo="SINTETICO_TESTE", ciclo="s", amostra="SINTETICO_TESTE")
        self.assertTrue(r["ok"])
        kb = r["termos"].index(B)
        self.assertLess(abs(r["theta"][kb] - beta), 3 * math.sqrt(r["V_mle"][kb, kb]))
        r0 = M.P1.estimar(X, D, modelo="SINTETICO_TESTE", ciclo="s", amostra="SINTETICO_TESTE")
        self.assertGreater(r0["theta"][r0["termos"].index(B)] - beta, 3 * math.sqrt(r0["V_mle"][0, 0]))

    def test_diferenca_pelo_sanduiche_conjunto(self) -> None:
        r = {"termos": [B], "theta": np.array([0.10]), "infl_bolsa": {"a": 0.01, "b": -0.02, "c": 0.005}}
        ref = {"termos": [B], "theta": np.array([0.04]), "infl_bolsa": {"a": 0.008, "b": -0.01}}
        d = M.diferenca(r, ref)
        f = 3 / 2
        ep = 5 * math.sqrt(f * ((0.01 - 0.008) ** 2 + (-0.02 + 0.01) ** 2 + 0.005 ** 2))
        self.assertAlmostEqual(d["estimativa"], 5 * 0.06, places=12)
        self.assertAlmostEqual(d["ep_cluster_conjunto"], ep, places=12)
        self.assertEqual(d["g_conjuntos"], 3)

    def test_regras_do_par3(self) -> None:
        ref = pd.Series({"estimativa": 1.25, "ic95_inf": 0.98, "ic95_sup": 1.6})
        s = lambda e, lo, hi: pd.Series({"estimativa": e, "ic95_inf": lo, "ic95_sup": hi})  # noqa: E731
        self.assertEqual(M.regra_linha(s(1.05, 0.8, 1.4), ref), "CAI_PARA_PERTO_DE_1")
        self.assertEqual(M.regra_linha(s(1.3, 1.02, 1.7), ref), "PARECIDA_COM_M1")
        self.assertEqual(M.regra_linha(s(2.5, 1.8, 3.4), ref), "MAIOR_QUE_M1")
        self.assertEqual(M.regra_linha(s(0.6, 0.45, 0.8), ref), "SINAL_OPOSTO")
        self.assertEqual(M.regra_linha(s(1.15, 1.10, 1.20), ref), "MENOR_QUE_M1_SEM_CHEGAR_A_1")
        self.assertTrue(M.ic_muito_largo(s(1.2, 0.5, 2.9), ref))
        self.assertFalse(M.ic_muito_largo(s(1.2, 0.9, 1.6), ref))


# ---------------------------------------------------------------------------
# 2. Portão real
# ---------------------------------------------------------------------------

class TestPortaoReal(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.est = ler_csv(CSV)
        cls.resumo = json.loads(RESUMO.read_text(encoding="utf-8"))

    def test_resumo_registra_portao_aprovado(self) -> None:
        p = self.resumo["portao"]
        self.assertEqual(p["status"], "PASSOU")
        self.assertEqual(p["tolerancia"], TOL)
        self.assertEqual([x["linha"] for x in p["linhas"]],
                         ["M1_antiga", "P1h-1_antiga", "M1_emp_corrigida", "M1_c2_corrigida", "M4_emp_corrigida",
                          "K5_M1_emp_corrigida", "K10_M1_emp_corrigida"])
        for linha in p["linhas"]:
            self.assertTrue(linha["passou"], linha)
            self.assertTrue(linha["casou"], linha)
            for k, v in linha.items():
                if k.startswith("dif_max_"):
                    self.assertLessEqual(v, TOL, (linha["linha"], k))

    def test_referencias_iguais_ao_vc_e_ao_vd(self) -> None:
        vc = ler_csv(OUT / "VC_estimativas.csv")
        vd = ler_csv(OUT / "VD_estimativas.csv")
        for chave, fonte, chave_g in (("M1_emp", vc, "M1"), ("M1_c2", vc, "M5_2"), ("M4_emp", vd, "M4")):
            g = fonte[(fonte["versao"] == M.CORRIGIDA) & (fonte["chave_modelo"] == chave_g)]
            for tipo in ("coeficiente", "razao_chances_por_5mil"):
                a = self.est[(self.est["chave_modelo"] == chave) & (self.est["tipo_linha"] == tipo)].set_index("termo")
                gg = g[g["tipo_linha"] == tipo].set_index("termo").loc[a.index]
                for c in ("estimativa", "ep_cluster_conjunto", "ic95_inf", "ic95_sup", "p"):
                    self.assertLessEqual(dif_rel(a[c], gg[c]), TOL, (chave, tipo, c))
        h = ler_csv(OUT / "P1h_magnitudes.csv")
        g = vc[(vc["versao"] == M.CORRIGIDA) & (vc["chave_modelo"] == "M1") & (vc["tipo_linha"] == "D_UF")].iloc[0]
        a = M._sel(self.est, "M1_emp", "D_UF")
        for c in ("estimativa", "ep_cluster_conjunto", "ic95_inf", "ic95_sup", "p_unilateral"):
            self.assertLessEqual(dif_rel([a[c]], [g[c]]), TOL, c)
        self.assertEqual(len(h[h["id_linha"] == "P1h-1"]), 1)
        gk = vd[(vd["versao"] == M.CORRIGIDA) & (vd["chave_modelo"] == "M1") & (vd["tipo_linha"] == "km_equivalentes")]
        for comp in ("K5", "K10"):
            a = M._sel(self.est, "M1_emp", "km_equivalentes", comp)
            g = gk[gk["termo"] == comp].iloc[0]
            for c in ("estimativa", "ic95_inf", "ic95_sup", "ic95_fieller_inf", "ic95_fieller_sup"):
                self.assertLessEqual(dif_rel([a[c]], [g[c]]), TOL, (comp, c))


# ---------------------------------------------------------------------------
# 3. Números contra output/
# ---------------------------------------------------------------------------

class TestNumeros(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.est = ler_csv(CSV)
        cls.resumo = json.loads(RESUMO.read_text(encoding="utf-8"))

    def test_rotulos_e_hashes(self) -> None:
        self.assertTrue((self.est["natureza_dos_dados"] == "EMPIRICO").all())
        self.assertTrue((self.est["estatuto"] == "ADENDO_52E_POS_RESULTADO").all())
        self.assertEqual(self.resumo["natureza_dos_dados"], "EMPIRICO")
        self.assertEqual(self.resumo["estatuto"], "ADENDO_52E_POS_RESULTADO")
        self.assertEqual(self.resumo["adendo"]["sha256"], sha256(M.ADENDO_MD))
        self.assertEqual(self.resumo["adendo"]["commit_de_congelamento"], "243160d")
        for caminho, h in self.resumo["saidas"].items():
            self.assertEqual(sha256(ROOT / caminho), h, caminho)
        for e in self.resumo["entradas"]:
            self.assertEqual(sha256(ROOT / e["caminho"]), e["sha256"], e["caminho"])
        self.assertEqual(set(self.est["chave_modelo"]), set(M.ESPECS))
        self.assertEqual(set(self.est["id_vl"]),
                         {"VL-1", "VL-2", "VL-3", "VL-4", "VL-5", "VL-1 (log da distância)", "apoio"})

    def test_saidas_antigas_nao_regravadas(self) -> None:
        ent = {e["caminho"] for e in self.resumo["entradas"]}
        for nome in ("P1_estimativas.csv", "P1h_magnitudes.csv", "VC_estimativas.csv", "VD_estimativas.csv"):
            self.assertIn(f"output/rdd_bolsa/{nome}", ent)
        texto = SCRIPT.read_text(encoding="utf-8")
        for alvo in ("to_csv(P1_", "to_csv(P1H_", "to_csv(VC_", "to_csv(VD_", "P1_EST.write", "P1H_CSV.write",
                     "VC_CSV.write", "VD_CSV.write", "VC.OUT_RESUMO", "E9.OUT_"):
            self.assertNotIn(alvo, texto)

    def test_razao_de_chances_ic_e_p(self) -> None:
        z = stats.norm.ppf(0.975)
        for chave in M.ESPECS:
            c = M._sel(self.est, chave, "coeficiente", B)
            o = M._sel(self.est, chave, "razao_chances_por_5mil")
            self.assertAlmostEqual(o["estimativa"], math.exp(5 * c["estimativa"]), delta=1e-8)
            self.assertAlmostEqual(o["ic95_inf"], math.exp(5 * c["ic95_inf"]), delta=1e-8)
            self.assertAlmostEqual(o["ic95_sup"], math.exp(5 * c["ic95_sup"]), delta=1e-8)
            self.assertAlmostEqual(o["p"], c["p"], delta=1e-12)
            self.assertAlmostEqual(c["ic95_inf"], c["estimativa"] - z * c["ep_cluster_conjunto"], delta=1e-8)
            self.assertAlmostEqual(c["p"], 2 * stats.norm.sf(abs(c["estimativa"] / c["ep_cluster_conjunto"])),
                                   delta=1e-10)

    def test_holm_e_bky(self) -> None:
        rc = self.est[self.est["tipo_linha"] == "razao_chances_por_5mil"]
        h = rc[rc["entra_holm"]].set_index("chave_modelo").loc[list(M.PRINCIPAIS)]
        np.testing.assert_allclose(h["p_holm"], M.L.holm(h["p"].to_numpy()), atol=1e-12)
        np.testing.assert_allclose(h["p_holm_score_rademacher"], M.L.holm(h["p_score_rademacher"].to_numpy()),
                                   atol=1e-12)
        # Holm escrito no teste: p ordenado × (m − posto), máximo acumulado, teto 1.
        p = h["p"].to_numpy()
        ordem = np.argsort(p)
        adj = np.minimum(1, np.maximum.accumulate((3 - np.arange(3)) * p[ordem]))
        np.testing.assert_allclose(h["p_holm"].to_numpy()[ordem], adj, atol=1e-12)
        b = rc[rc["entra_bky"]].set_index("chave_modelo").loc[list(M.SECUNDARIAS)]
        np.testing.assert_allclose(b["q_bky"], M.L.qvalores_bky(b["p"].to_numpy()), atol=1e-12)
        self.assertEqual(set(rc[rc["entra_holm"]]["chave_modelo"]), set(M.PRINCIPAIS))
        self.assertEqual(set(rc[rc["entra_bky"]]["chave_modelo"]), set(M.SECUNDARIAS))
        self.assertFalse(self.est[self.est["tipo_linha"] != "razao_chances_por_5mil"]["entra_holm"].any())

    def test_score_bootstrap_nas_principais_e_referencias(self) -> None:
        for chave in M.COM_SCORE:
            sb = self.resumo["score_bootstrap"][chave]
            self.assertEqual(sb["status"], "EXECUTADO", chave)
            self.assertTrue(0 < sb["p_rademacher"] <= 1)
            o = M._sel(self.est, chave, "razao_chances_por_5mil")
            self.assertLessEqual(dif_rel([o["p_score_rademacher"]], [sb["p_rademacher"]]), 1e-9)
            g = int(o["g_conjuntos"])
            self.assertEqual(sb["g"], g)
            self.assertIn("enumeração completa" if g <= 24 else "199999 sorteios", sb["metodo_rademacher"])

    def test_km_da_covariancia_gravada(self) -> None:
        z = stats.norm.ppf(0.975)
        for chave in M.COM_KM:
            cv = self.resumo["covariancias"][chave]
            ib, ig = cv["termos"].index(B), cv["termos"].index("distancia_100km")
            th, V = np.array(cv["theta"]), np.array(cv["V_cluster_conjunto"])
            for termo, passo in (("K5", 5.0), ("K10", 10.0)):
                k = 100 * passo * th[ib] / (-th[ig])
                g = np.zeros(len(th))
                g[ib], g[ig] = 100 * passo / (-th[ig]), 100 * passo * th[ib] / th[ig] ** 2
                ep = math.sqrt(g @ V @ g)
                r = M._sel(self.est, chave, "km_equivalentes", termo)
                self.assertLessEqual(dif_rel([r["estimativa"]], [k]), 1e-8)
                self.assertLessEqual(dif_rel([r["ic95_inf"]], [k - z * ep]), 1e-8)

    def test_diferenca_das_influencias_gravadas(self) -> None:
        infl = self.resumo["influencia_bolsa_por_conjunto"]
        for chave in M.PRINCIPAIS:
            ref = M.ESPECS[chave]["referencia"]
            a, b = infl[chave], infl[ref]
            cls = sorted(set(a) | set(b))
            ia = np.array([a.get(c, 0.0) for c in cls])
            ib = np.array([b.get(c, 0.0) for c in cls])
            G = len(cls)
            ep = 5 * math.sqrt(G / (G - 1) * ((ia - ib) ** 2).sum())
            d = M._sel(self.est, chave, "diferenca_log_rc_contra_referencia")
            bl = M._sel(self.est, chave, "coeficiente", B)["estimativa"]
            br = M._sel(self.est, ref, "coeficiente", B)["estimativa"]
            self.assertAlmostEqual(d["estimativa"], 5 * (bl - br), delta=1e-8)
            self.assertLessEqual(dif_rel([d["ep_cluster_conjunto"]], [ep]), 1e-8)
            # A variância de cada β pelas influências é a do sanduíche gravado (mesmo G).
            ga = len(a)
            v = ga / (ga - 1) * (np.array(list(a.values())) ** 2).sum()
            ep_l = M._sel(self.est, chave, "coeficiente", B)["ep_cluster_conjunto"]
            self.assertLessEqual(dif_rel([math.sqrt(v)], [ep_l]), 1e-6)

    def test_termos_absorvidos_e_intercepto(self) -> None:
        for chave, e in M.ESPECS.items():
            termos = set(self.resumo["convergencia"][chave]["termos_sem_efeito_fixo"])
            if e["ef"] in ("uf_origem", "cir_origem"):
                self.assertNotIn("mesma_uf", termos, chave)
                self.assertFalse(any(t.startswith("macro_") for t in termos), chave)
                self.assertGreater(self.resumo["convergencia"][chave]["n_efeitos_fixos"], 0)
                self.assertIn("mesma_regiao_saude", termos)
            else:
                self.assertEqual(self.resumo["convergencia"][chave]["n_efeitos_fixos"], 0)
            self.assertEqual(M.TERMO_INTERCEPTO in termos, e["janela"], chave)
            self.assertEqual("log1p_distancia_km" in termos, e["dist"] == "log", chave)
            self.assertTrue(self.resumo["convergencia"][chave]["ok"], chave)

    def test_contagens_de_identificacao(self) -> None:
        for chave, e in M.ESPECS.items():
            if e["ef"] not in ("uf_origem", "cir_origem"):
                continue
            d = self.resumo["identificacao"][chave]["identificacao"]
            o = M._sel(self.est, chave, "razao_chances_por_5mil")
            self.assertEqual(d["candidatos_no_modelo"], int(o["n_candidatos"]), chave)
            self.assertEqual(d["alternativas_no_modelo"], int(o["n_linhas_candidato_celula"]), chave)
            self.assertEqual(d["alternativas_no_desenho"] - d["alternativas_retiradas"], d["alternativas_no_modelo"])
            self.assertLessEqual(d["pares_com_variacao_de_bolsa"], d["pares_no_modelo"])
            self.assertLessEqual(d["candidatos_com_1a_opcao_em_par_com_variacao"],
                                 d["candidatos_com_variacao_de_bolsa_em_algum_par"])
            self.assertLessEqual(d["candidatos_com_variacao_de_bolsa_em_algum_par"], d["candidatos_no_modelo"])
            self.assertEqual(d["candidatos_no_desenho"] - d["candidatos_retirados_uma_so_alternativa"],
                             d["candidatos_no_modelo"])
            self.assertEqual(d["colunas_de_efeito_fixo"], int(o["n_efeitos_fixos"]), chave)
            if e["janela"]:
                j = self.resumo["identificacao"][chave]["janela"]
                self.assertEqual(j["candidatos_com_1a_opcao_na_janela"], d["candidatos_no_desenho"])

    def test_leitura_refeita(self) -> None:
        self.assertEqual(M.P1._nan_none(M.leitura(self.est)), self.resumo["leitura"])
        for chave in M.PRINCIPAIS:
            l = M._sel(self.est, chave, "razao_chances_por_5mil")
            ref = M._sel(self.est, M.ESPECS[chave]["referencia"], "razao_chances_por_5mil")
            self.assertEqual(self.resumo["leitura"]["linhas"][chave]["regra"], M.regra_linha(l, ref))

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
# 4. Doc 57x
# ---------------------------------------------------------------------------

BLOCOS = ("resposta", "portao", "identificacao", "principais", "secundarias", "km", "controles", "leitura", "figura",
          "decisoes")


class TestDoc57x(unittest.TestCase):
    def test_doc_igual_ao_gerado(self) -> None:
        self.assertEqual(DOC.read_text(encoding="utf-8"), M.gerar_doc(M.ler_est(), M.ler_resumo()))

    def test_marcadores_e_secoes(self) -> None:
        t = DOC.read_text(encoding="utf-8")
        for nome in BLOCOS:
            self.assertEqual(t.count(f"<!-- VL:{nome}:inicio -->"), 1, nome)
            self.assertEqual(t.count(f"<!-- VL:{nome}:fim -->"), 1, nome)
        for s in ("## 1. Resposta curta", "## 2. Portão", "## 3. Quantos pares de UF", "## 7. Decisões de "
                  "implementação", "## 8. Limites", "ADENDO_52E_POS_RESULTADO",
                  "**Auditoria:** [48](../auditorias/48_auditoria_escolha_localizacao_par.md)"):
            self.assertIn(s, t)

    def test_nenhum_numero_de_resultado_fora_dos_blocos(self) -> None:
        t = DOC.read_text(encoding="utf-8")
        fora = re.sub(r"<!-- VL:(\w+):inicio -->.*?<!-- VL:\1:fim -->", "", t, flags=re.S)
        fora = "\n".join(x for x in fora.splitlines() if not x.startswith("#"))
        self.assertEqual(re.findall(r"\d+,\d+", fora), [])
        self.assertEqual(re.findall(r"\d+\.\d+", fora), [])

    def test_parecida_com_diferenca_pareada_que_exclui_zero(self) -> None:
        """Auditoria 48 (A1): se a diferença pareada contra o M1 exclui zero, o texto não fica só no "parecida"."""
        t = " ".join(DOC.read_text(encoding="utf-8").split())
        est = M.ler_est()
        dif = est[est["tipo_linha"] == "diferenca_log_rc_contra_referencia"]
        exclui = ((dif["ic95_inf"] > 0) | (dif["ic95_sup"] < 0)).any()
        self.assertEqual("A leitura mais exata" in t, bool(exclui))
        self.assertIn("De onde vem a diferença contra o M1", t)
        self.assertIn("Com o log da distância", t)

    def test_linguagem(self) -> None:
        t = " ".join(DOC.read_text(encoding="utf-8").split())
        self.assertIn("preferência revelada, não efeito causal", t)
        self.assertIn("pacote do corte", t)
        self.assertIn("Não é efeito da participação no PMM-E", t)
        self.assertIn("Em linguagem simples", t)
        self.assertNotIn("a bolsa funciona", t.lower())
        self.assertNotIn("efeito causal da origem", t.lower())

    def test_decisoes_iguais_as_do_pre_registro(self) -> None:
        t = DOC.read_text(encoding="utf-8")
        ini = t.index("<!-- VL:decisoes:inicio -->") + len("<!-- VL:decisoes:inicio -->\n")
        fim = t.index("\n<!-- VL:decisoes:fim -->")
        self.assertEqual(t[ini:fim], M.texto_decisoes())
        self.assertEqual(len(M.DECISOES), 13)
        self.assertTrue(all(d["data"] == "2026-10-27" for d in M.DECISOES))


if __name__ == "__main__":
    unittest.main()
