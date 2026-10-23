"""Testes do P1 (protocolo 52): `scripts/rdd_bolsa/25_escolha_dap.py`.

Três partes:

1. `TestSintetico`: DADOS SINTÉTICOS gerados em memória (semente fixa), rotulados "sintético" e nunca gravados em
   `output/` nem em `data/`. Recuperam um beta conhecido num logit condicional simulado; conferem a compressão
   por tipo, os gradientes analíticos do logit misto e do aninhado contra diferenças finitas, o aninhado com
   lambda = 1 igual ao condicional, o gradiente da DAP e o salto previsto do P1g contra o recálculo direto.
2. `TestSaidasReais`: esquema e rótulos de `output/rdd_bolsa/P1_*`, todas as especificações relatadas (M3 como
   NAO_EXECUTADO com motivo), NaN sempre com nota, Holm só em P1a, BKY recalculado, reprodução do E9, DAP
   recalculada dos coeficientes, Wald entre ciclos recalculado, RDD por célula igual ao A3, contagens da amostra,
   hashes das saídas e figuras com "Como ler", sem nome nem CPF; conferência independente do M5 (ciclo 1) com o
   `ConditionalLogit` do statsmodels.
3. `TestDoc57a`: o doc 57a é igual ao gerado das saídas e traz a linguagem e as ameaças do protocolo.
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
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "25_escolha_dap.py"
_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location("escolha_dap_25", SCRIPT)
P1 = importlib.util.module_from_spec(_spec)
sys.modules["escolha_dap_25"] = P1
_spec.loader.exec_module(P1)
sys.dont_write_bytecode = _bytecode
L = P1.L

OUT = ROOT / "output" / "rdd_bolsa"
EST = OUT / "P1_estimativas.csv"
DAP = OUT / "P1_dap.csv"
RESUMO = OUT / "P1_resumo.json"
DOC = ROOT / "docs" / "06_execucao" / "57a_resultados_P1_escolha.md"

NATUREZA_SINTETICA = "SINTETICO_TESTE"   # rótulo dos dados gerados aqui ("sintético"); nunca gravados


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Sintético (só em memória)
# ---------------------------------------------------------------------------

def desenho_sintetico(semente: int = 7, n_conj: int = 30, cand_por_conj: int = 60, m: int = 12,
                      beta=(0.25, -0.8, 0.5), tipos_por_conj: int | None = None) -> dict:
    """SINTÉTICO: logit condicional com bolsa (3 níveis), distância (varia por candidato) e um atributo binário.

    Com `tipos_por_conj`, candidatos do mesmo tipo têm linhas idênticas (para testar a compressão)."""
    rng = np.random.default_rng(semente)
    beta = np.asarray(beta, dtype=float)
    blocos, grupos, esc, starts, cel = [], [], [], [], []
    pos = 0
    for s in range(n_conj):
        bolsa = rng.choice([10.0, 15.0, 20.0], m)
        attr = (rng.random(m) < 0.4).astype(float)
        origens = rng.normal(0, 1, (tipos_por_conj or cand_por_conj, m))
        for i in range(cand_por_conj):
            dist = np.abs(origens[i % len(origens)]) * 3.0
            X = np.column_stack([bolsa, dist, attr])
            u = X @ beta + rng.gumbel(size=m)
            j = int(np.argmax(u))
            blocos.append(X)
            starts.append(pos)
            esc.append(pos + j)
            cel.append(np.arange(m) + s * m)
            grupos.append({"cluster_conjunto": f"s{s:02d}", "cluster_candidato": f"s{s:02d}_c{i:03d}",
                           "co_ibge_origem": f"o{i % len(origens):03d}", "idx_excluida": -1, "posto": 1,
                           "id_candidato": f"s{s:02d}_c{i:03d}"})
            pos += m
    A = np.vstack(blocos)
    starts = np.array(starts)
    tam = np.diff(np.append(starts, len(A)))
    D = {"starts": starts, "grp": np.repeat(np.arange(len(starts)), tam), "esc": np.array(esc), "tam": tam,
         "cel": np.concatenate(cel), "grupos": pd.DataFrame(grupos)}
    return {"A": A, "D": D, "beta": beta, "natureza_dos_dados": NATUREZA_SINTETICA}


class TestSintetico(unittest.TestCase):
    """Estimadores em dados sintéticos (nada é gravado)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.s = desenho_sintetico()

    def test_dados_rotulados_como_sinteticos(self) -> None:
        self.assertEqual(self.s["natureza_dos_dados"], NATUREZA_SINTETICA)

    def test_logit_condicional_recupera_beta_conhecido(self) -> None:
        fit = P1.ajustar_cl(self.s["A"], self.s["D"])
        self.assertTrue(fit["convergiu"])
        ep = np.sqrt(np.diag(np.linalg.inv(fit["info"])))
        z = (fit["theta"] - self.s["beta"]) / ep
        self.assertTrue(np.all(np.abs(z) < 4), f"sintético: theta {fit['theta']} beta {self.s['beta']} z {z}")
        # DAP da distância (−β_dist/β_bolsa) perto da verdadeira.
        dap = -fit["theta"][1] / fit["theta"][0]
        self.assertLess(abs(dap - 0.8 / 0.25), 1.0)

    def test_compressao_por_tipo_tem_a_mesma_verossimilhanca(self) -> None:
        s = desenho_sintetico(semente=3, tipos_por_conj=8)
        cheio = P1.ajustar_cl(s["A"], s["D"])
        At, Dt = P1.comprimir(s["A"], s["D"])
        self.assertLess(len(At), len(s["A"]))
        comp = P1.ajustar_cl(At, Dt, estat=P1._estat_tipos)
        np.testing.assert_allclose(comp["theta"], cheio["theta"], rtol=1e-9, atol=1e-11)
        self.assertAlmostEqual(comp["ll"], cheio["ll"], places=8)

    def test_gradiente_do_logit_misto_igual_ao_numerico(self) -> None:
        s = desenho_sintetico(semente=5, n_conj=4, cand_por_conj=15, m=6)
        A, D = s["A"], s["D"]
        eb, ed = P1.sorteios_halton(len(D["starts"]), 40, 11)
        Xf = A[:, [2]]
        p = np.array([0.4, 0.2, 0.15, -0.7, 0.3])
        ll, g, sc = P1.misto_ll_grad(p, Xf, A[:, 0], A[:, 1], D, eb, ed)
        np.testing.assert_allclose(sc.sum(axis=0), g)
        for k in range(len(p)):
            h = 1e-6
            pp, pm = p.copy(), p.copy()
            pp[k] += h
            pm[k] -= h
            num = (P1.misto_ll_grad(pp, Xf, A[:, 0], A[:, 1], D, eb, ed)[0] -
                   P1.misto_ll_grad(pm, Xf, A[:, 0], A[:, 1], D, eb, ed)[0]) / (2 * h)
            self.assertAlmostEqual(g[k], num, delta=1e-5 * max(1.0, abs(num)), msg=f"parâmetro {k}")
        # Desvios zero: o misto vira o condicional.
        p0 = np.array([0.4, 0.2, 0.0, -0.7, 0.0])
        ll0 = P1.misto_ll_grad(p0, Xf, A[:, 0], A[:, 1], D, eb, ed)[0]
        cl = P1._estat(np.array([0.2, -0.7, 0.4]), A, D)["ll"]
        self.assertAlmostEqual(ll0, cl, places=8)

    def test_gradiente_do_aninhado_e_lambda_um(self) -> None:
        s = desenho_sintetico(semente=9, n_conj=5, cand_por_conj=20, m=8)
        A, D = s["A"], s["D"]
        ninho_cel = np.arange(len(D["cel"])) % 3            # 3 "regiões" por conjunto (sintético)
        D2, ordem, nin = P1.preparar_ninhos(D, D["cel"] % 3)
        args = (A[ordem], D2, nin["ninho"], nin["ninho_grp"], nin["ninho_st"], nin["grp_ninho_st"])
        b = np.array([0.2, -0.6, 0.4])
        ll1 = P1.aninhado_ll_grad(np.r_[b, 1.0], *args)[0]
        self.assertAlmostEqual(ll1, P1._estat(b, A, D)["ll"], places=8)
        p = np.r_[b, 0.7]
        ll, g, sc = P1.aninhado_ll_grad(p, *args)
        for k in range(len(p)):
            h = 1e-6
            pp, pm = p.copy(), p.copy()
            pp[k] += h
            pm[k] -= h
            num = (P1.aninhado_ll_grad(pp, *args)[0] - P1.aninhado_ll_grad(pm, *args)[0]) / (2 * h)
            self.assertAlmostEqual(g[k], num, delta=1e-5 * max(1.0, abs(num)))
        del ninho_cel

    def test_gradiente_da_dap(self) -> None:
        termos = [P1.TERMO_BOLSA, P1.TERMO_DIST, "mesma_uf", "capital", "tem_vaga_imediata",
                  "log_vagas_imediatas_mais_1"]
        th = np.array([0.05, -0.2, 2.0, -0.3, 0.4, 0.3])
        for a in P1.DAP_DEF:
            v, g = P1.dap_vetor(termos, th, a)
            num = np.array([(P1.dap_vetor(termos, th + 1e-7 * np.eye(6)[k], a)[0] -
                             P1.dap_vetor(termos, th - 1e-7 * np.eye(6)[k], a)[0]) / 2e-7 for k in range(6)])
            np.testing.assert_allclose(g, num, rtol=1e-5, atol=1e-6)
        self.assertAlmostEqual(P1.dap_vetor(termos, th, "distancia_100km_a_menos")[0], 0.2 / 0.05)
        self.assertAlmostEqual(P1.dap_vetor(termos, th, "vaga_imediata")[0], (0.4 + math.log(2) * 0.3) / 0.05)

    def test_salto_previsto_igual_ao_recalculo_direto(self) -> None:
        s = desenho_sintetico(semente=13, n_conj=3, cand_por_conj=10, m=5)
        A, D = s["A"], s["D"]
        th = np.array([0.1, -0.5, 0.3])
        r = {"_A": A, "_D": D, "termos": [P1.TERMO_BOLSA, P1.TERMO_DIST, "x"]}
        alvo = np.array([1, 7])                                  # células sintéticas da "janela"
        linhas = np.flatnonzero(np.isin(D["cel"], alvo))
        jan = {"linhas": linhas, "pos_celula": np.searchsorted(alvo, D["cel"][linhas]), "peso": np.array([1.0, 0.5]),
               "bolsa_alta": np.full(len(linhas), 20.0), "bolsa_baixa": np.full(len(linhas), 15.0)}
        prev = P1.saltos_previstos(th, r, [jan])[0]

        def esperado(bolsa_nova: float) -> np.ndarray:
            EN = np.zeros(len(alvo))
            for i, c in enumerate(alvo):
                B = A.copy()
                B[D["cel"] == c, 0] = bolsa_nova
                p = P1._estat(th, B, D)["p"]
                EN[i] = p[D["cel"] == c].sum()
            return EN
        dif = esperado(20.0) - esperado(15.0)
        self.assertAlmostEqual(prev, float((jan["peso"] * dif).sum() / jan["peso"].sum()), places=10)


# ---------------------------------------------------------------------------
# Saídas reais
# ---------------------------------------------------------------------------

class TestSaidasReais(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.est = pd.read_csv(EST, dtype={"ciclo": str})
        cls.dap = pd.read_csv(DAP, dtype={"ciclo": str})
        cls.res = json.loads(RESUMO.read_text(encoding="utf-8"))

    def test_esquema_e_rotulos(self) -> None:
        self.assertEqual(list(self.est.columns), P1.COLUNAS_EST)
        for df in (self.est, self.dap):
            self.assertTrue((df["natureza_dos_dados"] == "EMPIRICO").all())
            self.assertTrue((df["estatuto"] == "PROTOCOLO_52_POS_RESULTADO").all())
        self.assertEqual(self.res["natureza_dos_dados"], "EMPIRICO")
        self.assertTrue(set(self.est["status"]) <= {"EXECUTADO", "NAO_EXECUTADO", "NAO_CONVERGIU"})
        self.assertTrue(set(self.est["estimando"]) <= {"P1a", "P1d", "P1e", "P1f", "P1g", "sensibilidade"})

    def test_todas_as_especificacoes_relatadas(self) -> None:
        modelos = set(self.est["modelo"])
        for m in ("E9_amostra_completa", "M0", "M1", "M2", "M3", "M4", "M5", "M6_nota", "M6_municipio", "M6_curso",
                  "M7", "M8", "M9", "M1_previsto", "RDD_celula"):
            self.assertIn(m, modelos)
        m3 = self.est[self.est["modelo"] == "M3"]
        self.assertTrue((m3["status"] == "NAO_EXECUTADO").all())
        self.assertTrue(m3["nota"].str.contains("origem mais próxima").all())
        self.assertEqual(sorted(self.est.loc[self.est["modelo"] == "M5", "ciclo"].unique()), ["1", "1,2,3", "2", "3"])
        for m in ("M8", "M9"):
            s = self.est[self.est["modelo"] == m]
            if (s["status"] != "EXECUTADO").any():
                self.assertTrue((s["nota"].fillna("") != "").all(), m)

    def test_nan_sempre_com_nota(self) -> None:
        sem = self.est[self.est["coef"].isna() & ~self.est["tipo_linha"].str.startswith("wald") &
                       (self.est["nota"].fillna("") == "")]
        self.assertEqual(len(sem), 0)
        d = self.dap[self.dap["dap"].isna() & (self.dap["nota"].fillna("") == "")]
        self.assertEqual(len(d), 0)

    def test_holm_so_em_P1a(self) -> None:
        h = self.est[self.est["entra_holm"].astype(bool)]
        self.assertEqual(len(h), 1)
        r = h.iloc[0]
        self.assertEqual((r["modelo"], r["termo"], r["ciclo"], r["estimando"]), ("M1", "bolsa_mil", "empilhado", "P1a"))
        self.assertAlmostEqual(r["p_holm"], L.holm([r["p"]])[0])
        self.assertTrue(self.est.loc[~self.est["entra_holm"].astype(bool), "p_holm"].isna().all())

    def test_bky_recalculado_e_so_secundarias(self) -> None:
        b = self.est[self.est["entra_bky"].astype(bool) & self.est["p"].notna()]
        self.assertTrue(set(b["estimando"]) <= {"P1d", "P1e", "P1f"})
        self.assertFalse((b["inferencia_cluster_degenerada"].astype(bool)).any())
        np.testing.assert_allclose(b["q_bky"].to_numpy(), L.qvalores_bky(b["p"].to_numpy()), rtol=1e-9)
        self.assertTrue(self.est.loc[~self.est.index.isin(b.index), "q_bky"].isna().all())

    def test_reproduz_o_E9(self) -> None:
        e9 = pd.read_csv(OUT / "E9_estimativas.csv", dtype={"ciclo": str})
        alvo = e9[(e9.ciclo == "empilhado") & (e9.modelo == "logit_condicional_1a_opcao") & (e9.conjunto == "principal")
                  & (e9.especificacao == "spline_linear__bolsa_linear") & (e9.termo == "bolsa_mil")].iloc[0]
        r = self.est[(self.est["modelo"] == "E9_amostra_completa") & (self.est["termo"] == "bolsa_mil")].iloc[0]
        self.assertAlmostEqual(r["coef"], alvo["coef"], places=8)
        self.assertAlmostEqual(r["ep_cluster_conjunto"], alvo["ep_cluster_conjunto"], places=8)
        self.assertTrue(self.res["amostra"]["reproducao_E9"]["igual"])

    def test_dap_recalculada_dos_coeficientes(self) -> None:
        for m, ciclo in (("M1", "empilhado"), ("M4", "empilhado"), ("M7", "empilhado")):
            c = self.est[(self.est["modelo"] == m) & (self.est["ciclo"] == ciclo) &
                         (self.est["tipo_linha"] == "coeficiente")].set_index("termo")["coef"]
            d = self.dap[self.dap["modelo"] == m].set_index("atributo")["dap"]
            b = c["bolsa_mil"]
            self.assertAlmostEqual(d["distancia_100km_a_menos"], -c["distancia_100km"] / b, delta=1e-6 * abs(d["distancia_100km_a_menos"]) + 1e-9)
            self.assertAlmostEqual(d["mesma_uf"], c["mesma_uf"] / b, delta=1e-6 * abs(d["mesma_uf"]) + 1e-9)
            self.assertAlmostEqual(d["capital"], c["capital"] / b, delta=1e-6 * abs(d["capital"]) + 1e-9)
            vi = (c["tem_vaga_imediata"] + math.log(2) * c["log_vagas_imediatas_mais_1"]) / b
            self.assertAlmostEqual(d["vaga_imediata"], vi, delta=1e-6 * abs(vi) + 1e-9)
        m1 = self.dap[self.dap["modelo"] == "M1"]
        self.assertTrue((m1["n_boot"] == 999).all())
        self.assertTrue(m1["ic95_boot_inf"].notna().all())
        ic = m1["ic95_delta_sup"] - m1["ic95_delta_inf"]
        np.testing.assert_allclose(ic, 2 * stats.norm.ppf(0.975) * m1["ep_delta"], rtol=1e-8)

    def test_wald_entre_ciclos_recalculado(self) -> None:
        s = self.est[(self.est["modelo"] == "M5") & (self.est["termo"] == "bolsa_mil")].set_index("ciclo")
        b = s.loc[["1", "2", "3"], "coef"].to_numpy()
        v = s.loc[["1", "2", "3"], "ep_cluster_conjunto"].to_numpy() ** 2
        R = np.array([[1.0, -1, 0], [0, 1, -1]])
        d = R @ b
        W = float(d @ np.linalg.solve(R @ np.diag(v) @ R.T, d))
        w = self.est[self.est["tipo_linha"] == "wald_igualdade_ciclos"].iloc[0]
        self.assertAlmostEqual(w["estatistica_wald"], W, delta=1e-6 * W)
        self.assertAlmostEqual(w["p"], float(stats.chi2.sf(W, 2)), delta=1e-7)

    def test_rdd_por_celula_igual_ao_A3(self) -> None:
        conf = self.res["p1g"]["conferencia_A3"]
        self.assertGreaterEqual(len(conf), 4)
        self.assertTrue(all(v["igual"] for v in conf.values()))
        na = pd.read_csv(OUT / "NA_estimativas.csv", dtype={"ciclo": str, "corte": str})
        a3 = na[(na.outcome_id == "A3_CAND_1A_OPCAO") & (na.variante == "so_curso_x_ciclo") & (na.ciclo == "1+2+3") &
                (na.corte == "empilhado")].iloc[0]
        r = self.est[(self.est["modelo"] == "RDD_celula") & (self.est["ciclo"] == "1+2+3") &
                     (self.est["termo"] == "corte_empilhado") &
                     (self.est["amostra"] == "todos os candidatos (outcomes_V_celula)")].iloc[0]
        self.assertAlmostEqual(r["coef"], a3["tau"], places=8)

    def test_contagens_da_amostra(self) -> None:
        a = self.res["amostra"]
        for k in ("1", "2", "3"):
            fora = sum(v.get(k, 0) for v in a["exclusoes"].values())
            self.assertEqual(a["r1_por_ciclo"][k], a["p1_por_ciclo"][k] + fora)
        m1 = self.est[(self.est["modelo"] == "M1") & (self.est["termo"] == "bolsa_mil")].iloc[0]
        self.assertEqual(int(m1["n_candidatos"]), sum(a["p1_por_ciclo"].values()))
        self.assertEqual(a["conferencia_distancia"]["diferenca_maxima_km"], 0.0)
        for k in ("1", "2", "3"):
            m5 = self.est[(self.est["modelo"] == "M5") & (self.est["ciclo"] == k) & (self.est["termo"] == "bolsa_mil")]
            self.assertEqual(int(m5.iloc[0]["n_candidatos"]), a["p1_por_ciclo"][k])

    def test_hashes_e_figuras(self) -> None:
        for rel_, h in self.res["saidas"].items():
            self.assertEqual(sha256(ROOT / rel_), h, rel_)
        nomes = set()
        for f in self.res["figuras"]:
            self.assertTrue((ROOT / f["arquivo"]).exists())
            self.assertEqual(sha256(ROOT / f["arquivo"]), f["sha256"])
            self.assertGreater(len(f["como_ler"]), 40)
            nomes.add(Path(f["arquivo"]).name)
        self.assertEqual(nomes, set(self.res["como_ler"]))
        self.assertEqual(nomes, {"P1_dap.png", "P1_beta_por_ciclo.png", "P1_ponte_P1g.png"})

    def test_sem_nome_nem_cpf_nem_pseudonimo(self) -> None:
        for df in (self.est, self.dap):
            for c in df.columns:
                self.assertNotRegex(c.lower(), r"nome|cpf|id_candidato|crm")
            texto = df.astype(str).to_csv()
            self.assertNotRegex(texto, r"c[123]_\d{5}")       # pseudônimo do candidato
            self.assertNotRegex(texto, r"\d{3}\.\d{3}\.\d{3}-\d{2}")
        self.assertNotRegex(RESUMO.read_text(encoding="utf-8"), r"c[123]_\d{5}")

    def test_integridade_do_script(self) -> None:
        src = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("ivs_ipea_2010_municipios", src)
        self.assertNotIn("painel_municipio_cbo_mes", src)          # nenhum mês do CNES é lido
        self.assertNotIn("random.normal", src)
        self.assertNotIn("to_parquet", src)

    def test_recalculo_independente_M5_ciclo1_statsmodels(self) -> None:
        """Conferência independente do M5 no ciclo 1 com o ConditionalLogit do statsmodels: a log-verossimilhança
        dele no ponto gravado é a gravada, e o score dele nesse ponto é zero (o ponto é o máximo). O otimizador do
        statsmodels não é usado porque estoura numericamente em conjuntos com centenas de células."""
        from statsmodels.discrete.conditional_models import ConditionalLogit
        dados = P1.carregar()
        conj = dados["conj_p1"]
        D = P1.montar_desenho(conj[conj["ciclo"] == 1].reset_index(drop=True),
                              dados["r1_p1"][dados["r1_p1"]["ciclo"] == 1], None, dados)
        X = P1.matriz_modelo(D, dados, "M1")
        X = X.drop(columns=P1.colunas_sem_variacao(X, D))
        y = np.zeros(len(X))
        y[D["esc"]] = 1.0
        mod = ConditionalLogit(y, X.to_numpy(), groups=D["grp"])
        csv = self.est[(self.est["modelo"] == "M5") & (self.est["ciclo"] == "1") &
                       (self.est["tipo_linha"] == "coeficiente")].set_index("termo")
        th = csv.loc[list(X.columns), "coef"].to_numpy(dtype=float)
        self.assertAlmostEqual(mod.loglike(th), float(csv["log_verossimilhanca"].iloc[0]), delta=1e-4)
        self.assertLess(float(np.max(np.abs(mod.score(th)))), 1e-2)


# ---------------------------------------------------------------------------
# Documento
# ---------------------------------------------------------------------------

class TestDoc57a(unittest.TestCase):

    def test_doc_igual_ao_gerado(self) -> None:
        est = pd.read_csv(EST, dtype={"ciclo": str})
        dap = pd.read_csv(DAP, dtype={"ciclo": str})
        res = json.loads(RESUMO.read_text(encoding="utf-8"))
        self.assertEqual(DOC.read_text(encoding="utf-8"), P1.gerar_doc(est, dap, res))

    def test_linguagem_e_ameacas(self) -> None:
        t = " ".join(DOC.read_text(encoding="utf-8").split())
        for frase in ("dentro do conjunto de vagas abertas", "Nada sobre quem não se candidatou",
                      "não mede a participação no PMM-E", "seleção pela ligação",
                      "não a residência", "viu todas as células do curso", "pacote", "Como ler"):
            self.assertIn(frase.lower(), t.lower(), frase)
        self.assertNotIn("Toda figura traz um bloco \"Como ler\" dentro da imagem", t)

    def test_como_ler_do_resumo_no_doc(self) -> None:
        res = json.loads(RESUMO.read_text(encoding="utf-8"))
        t = DOC.read_text(encoding="utf-8")
        for v in res["como_ler"].values():
            self.assertIn(v, t)


if __name__ == "__main__":
    unittest.main()
