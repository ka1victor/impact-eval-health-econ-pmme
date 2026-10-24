"""Testes do T1.6 (adendo §7 do protocolo 52): `scripts/rdd_bolsa/25b_cenarios_bolsa.py`.

Três partes:

1. `TestSintetico`: DADOS SINTÉTICOS gerados em memória (semente fixa), rotulados "sintético" e nunca gravados.
   O sorteio condicional do erro reproduz a ordem observada e tem a distribuição certa (marginal de valor
   extremo); um mercado pequeno de resultado conhecido passa pelo mecanismo do G2 e pelos outcomes; conservação
   em mercados aleatórios; determinismo do núcleo.
2. `TestSaidas`: rótulo `CENARIO_CONTRAFACTUAL` só em `output/cenarios/`; validação de base dentro da tolerância
   do adendo; conservação registrada; identidades entre outcomes; tabela recalculada das réplicas; fluxos
   coerentes; hashes; nenhum identificador de candidato; bolsas dentro de R$ 10–20 mil; IVS errado não lido.
3. `TestDoc57b`: o doc 57b é igual ao gerado e diz no topo que é simulação.
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
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "25b_cenarios_bolsa.py"
_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location("cenarios_bolsa_25b", SCRIPT)
T16 = importlib.util.module_from_spec(_spec)
sys.modules["cenarios_bolsa_25b"] = T16
_spec.loader.exec_module(T16)
sys.dont_write_bytecode = _bytecode
G2M = T16.G2M

NATUREZA_SINTETICA = "SINTETICO_TESTE"   # rótulo dos dados gerados aqui ("sintético"); nunca gravados
GAMMA = 0.5772156649015329


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def unidades_sinteticas(rng, n_unid: int, tam_min: int = 1, tam_max: int = 8):
    """SINTÉTICO: blocos de tamanho variado, V aleatório e ordem observada sorteada pelo próprio logit."""
    tam = rng.integers(tam_min, tam_max + 1, n_unid)
    starts = np.concatenate([[0], np.cumsum(tam)[:-1]]).astype(np.int64)
    V = rng.normal(0, 2, int(tam.sum()))
    U0 = V + rng.gumbel(size=len(V))
    a1, a2 = T16.melhores(U0, starts)
    top2 = np.where(rng.random(n_unid) < 0.6, a2, -1)
    return {"V": V, "starts": starts, "top1": a1, "top2": top2, "tam": tam,
            "natureza_dos_dados": NATUREZA_SINTETICA}


class TestSintetico(unittest.TestCase):
    def test_rotulo_sintetico(self) -> None:
        u = unidades_sinteticas(np.random.default_rng(1), 5)
        self.assertEqual(u["natureza_dos_dados"], NATUREZA_SINTETICA)

    def test_sorteio_condicional_reproduz_a_ordem_observada(self) -> None:
        rng = np.random.default_rng(2)
        u = unidades_sinteticas(rng, 3000)
        for _ in range(20):
            n_u, n = len(u["starts"]), len(u["V"])
            U = T16.sortear_condicional(u["V"], u["starts"], u["top1"], u["top2"], rng.exponential(size=n_u),
                                        rng.exponential(size=n_u), rng.exponential(size=n))
            a1, a2 = T16.melhores(U, u["starts"])
            np.testing.assert_array_equal(a1, u["top1"])
            tem2 = u["top2"] >= 0
            np.testing.assert_array_equal(a2[tem2], u["top2"][tem2])

    def test_sorteio_condicional_tem_marginal_de_valor_extremo(self) -> None:
        """Se a ordem observada vem do logit e o erro é sorteado condicional a ela, U − V é Gumbel(0, 1) na
        marginal: média γ e variância π²/6, em toda posição (1ª, 2ª e demais)."""
        rng = np.random.default_rng(3)
        n_u, m = 60000, 4
        V = np.tile(np.array([0.8, 0.0, -0.5, 1.5]), n_u)
        starts = np.arange(n_u, dtype=np.int64) * m
        U0 = V + rng.gumbel(size=len(V))
        a1, a2 = T16.melhores(U0, starts)
        U = T16.sortear_condicional(V, starts, a1, a2, rng.exponential(size=n_u), rng.exponential(size=n_u),
                                    rng.exponential(size=len(V)))
        e = (U - V).reshape(n_u, m)
        for j in range(m):
            self.assertAlmostEqual(float(e[:, j].mean()), GAMMA, delta=0.03)
            self.assertAlmostEqual(float(e[:, j].var()), np.pi ** 2 / 6, delta=0.06)

    def test_estabilidade_numerica_com_1a_opcao_dominante(self) -> None:
        """Quando a 1ª opção domina (λ das demais ~ 1e-20 do total), a 2ª observada continua em 2º."""
        V = np.array([50.0, 0.0, -1.0, 2.0, 50.0, 1.0])
        starts = np.array([0, 4], dtype=np.int64)
        top1, top2 = np.array([0, 4]), np.array([3, 5])
        for s in range(50):
            r = np.random.default_rng(s)
            U = T16.sortear_condicional(V, starts, top1, top2, r.exponential(size=2), r.exponential(size=2),
                                        r.exponential(size=6))
            a1, a2 = T16.melhores(U, starts)
            np.testing.assert_array_equal(a1, top1)
            np.testing.assert_array_equal(a2, top2)

    def _mercado_pequeno(self):
        """SINTÉTICO: célula A (Faixa 3, 1 vaga AC) vazia e célula B (Faixa 1, 1 vaga AC) disputada por dois
        candidatos que só listaram B. c1 tem nota maior."""
        A, B = ("A", 1), ("B", 1)
        cap = {A: (1, 0, 0), B: (1, 0, 0)}
        faixa = {A: "FAIXA 3", B: "FAIXA 1"}
        fixos = pd.DataFrame(columns=["id_candidato", "celula", "opcao_rank", "pontuacao", "tipo_inscricao",
                                      "classificacao_publicada"])
        resp = pd.DataFrame({"ciclo": [1, 1], "id_candidato": ["c1", "c2"], "pontuacao": [10.0, 8.0],
                             "tipo_inscricao": ["AC", "AC"], "L": [1, 1], "obs1": [B, B], "obs2": [None, None]})
        return A, B, cap, faixa, fixos, resp

    def test_mercado_de_resultado_conhecido(self) -> None:
        A, B, cap, faixa, fixos, resp = self._mercado_pequeno()
        cel_chave = [A, B]
        u = {"c1": 0.5, "c2": 0.4}
        ent0 = T16.montar_entrada_mecanismo(fixos, resp, {}, cel_chave)
        b0 = G2M.alocar(ent0, cap, G2M.AC_PRIMEIRO, desempate="sorteio", sorteio=u)
        self.assertEqual({p: c for p, (c, _t) in b0.items()}, {"c1": B})
        # Só c2 passa a preferir A: o total sobe de 1 para 2.
        ent1 = T16.montar_entrada_mecanismo(fixos, resp, {(1, "c2"): {1: 0}}, cel_chave)
        s1 = G2M.alocar(ent1, cap, G2M.AC_PRIMEIRO, desempate="sorteio", sorteio=u)
        o, fl = T16.medir(b0, s1, faixa, T16.BOLSA_OBS, {"FAIXA 3": 15.0, "FAIXA 2": 15.0, "FAIXA 1": 20.0})
        self.assertEqual(o["delta_preenchidas_total"], 1)
        self.assertEqual(o["medicos_mudam_de_vaga"], 1)
        self.assertEqual((o["vagas_passam_a_ser_preenchidas"], o["vagas_deixam_de_ser_preenchidas"]), (1, 0))
        self.assertEqual(o["delta_preenchidas_FAIXA 3"], 1)
        self.assertEqual(o["delta_custo_mensal_bolsas_mil"], 15.0)
        self.assertEqual(fl, {(T16.NAO_ALOCADO, "FAIXA 3"): 1})
        # Os dois passam a preferir A: o total não muda, c1 troca B por A, B fica vazia.
        ent2 = T16.montar_entrada_mecanismo(fixos, resp, {(1, "c1"): {1: 0}, (1, "c2"): {1: 0}}, cel_chave)
        s2 = G2M.alocar(ent2, cap, G2M.AC_PRIMEIRO, desempate="sorteio", sorteio=u)
        o, fl = T16.medir(b0, s2, faixa, T16.BOLSA_OBS, T16.BOLSA_OBS)
        self.assertEqual(o["delta_preenchidas_total"], 0)
        self.assertEqual(o["medicos_mudam_de_vaga"], 1)
        self.assertEqual((o["vagas_passam_a_ser_preenchidas"], o["vagas_deixam_de_ser_preenchidas"]), (1, 1))
        self.assertEqual((o["delta_preenchidas_FAIXA 3"], o["delta_preenchidas_FAIXA 1"]), (1, -1))
        self.assertEqual(fl, {("FAIXA 1", "FAIXA 3"): 1})

    def test_ponta_a_ponta_com_utilidades(self) -> None:
        """SINTÉTICO: unidades sobre [A, B] com B observada; sem mudança a lista se repete; com bolsa de A muito
        maior (β grande), todo candidato passa a listar A."""
        A, B, cap, faixa, fixos, resp = self._mercado_pequeno()
        U = {"cel": np.array([0, 1, 0, 1]), "starts": np.array([0, 2], dtype=np.int64), "top1": np.array([1, 3]),
             "top2": np.array([-1, -1]), "chave": [(1, "c1"), (1, "c2")], "posicoes": [(1,), (1,)]}
        V = np.array([0.0, 0.3, 0.0, 0.3])
        r = np.random.default_rng(5)
        Ub = T16.sortear_condicional(V, U["starts"], U["top1"], U["top2"], r.exponential(size=2),
                                     r.exponential(size=2), r.exponential(size=4))
        a1, a2 = T16.melhores(Ub, U["starts"])
        self.assertEqual(T16.listas_das_unidades(U, a1, a2), {(1, "c1"): {1: 1}, (1, "c2"): {1: 1}})
        delta = np.array([5.0, 0.0, 5.0, 0.0])
        a1, a2 = T16.melhores(Ub + 100.0 * delta, U["starts"])
        listas = T16.listas_das_unidades(U, a1, a2)
        self.assertEqual(listas, {(1, "c1"): {1: 0}, (1, "c2"): {1: 0}})
        ent = T16.montar_entrada_mecanismo(fixos, resp, listas, [A, B])
        sim = G2M.alocar(ent, cap, G2M.AC_PRIMEIRO, desempate="sorteio", sorteio={"c1": 0.1, "c2": 0.2})
        self.assertEqual({p: c for p, (c, _t) in sim.items()}, {"c1": A})

    def test_conservacao_em_mercados_aleatorios(self) -> None:
        rng = np.random.default_rng(11)
        for _ in range(40):
            n_c, n_p = int(rng.integers(3, 9)), int(rng.integers(5, 30))
            cels = [(f"x{i}", 1) for i in range(n_c)]
            cap = {c: (int(rng.integers(0, 3)), int(rng.integers(0, 2)), 0) for c in cels}
            linhas = []
            for p in range(n_p):
                esc = rng.choice(n_c, size=int(rng.integers(1, 3)), replace=False)
                tipo = "ER" if rng.random() < 0.2 else "AC"
                for o, j in enumerate(esc, start=1):
                    linhas.append({"id_candidato": f"p{p:02d}", "celula": cels[j], "opcao_rank": o,
                                   "pontuacao": float(rng.integers(0, 6)), "tipo_inscricao": tipo,
                                   "classificacao_publicada": np.nan})
            ent = pd.DataFrame(linhas)
            u = {f"p{p:02d}": float(rng.random()) for p in range(n_p)}
            sim = G2M.alocar(ent, cap, G2M.AC_PRIMEIRO, desempate="sorteio", sorteio=u)
            c = T16.conferir_conservacao(sim, ent, cap)
            self.assertEqual(c["celulas_acima_da_capacidade"], 0)
            self.assertEqual(c["alocados_fora_da_lista"], 0)
            self.assertEqual(len(sim), len(set(sim)))   # um médico, no máximo uma vaga

    def test_determinismo_do_nucleo(self) -> None:
        def uma_vez():
            r = np.random.default_rng(99)
            u = unidades_sinteticas(r, 500)
            n_u, n = len(u["starts"]), len(u["V"])
            U = T16.sortear_condicional(u["V"], u["starts"], u["top1"], u["top2"], r.exponential(size=n_u),
                                        r.exponential(size=n_u), r.exponential(size=n))
            return T16.melhores(U + 0.3 * r.normal(size=n), u["starts"])
        x, y = uma_vez(), uma_vez()
        np.testing.assert_array_equal(x[0], y[0])
        np.testing.assert_array_equal(x[1], y[1])

    def test_cenarios_dentro_da_faixa_observada(self) -> None:
        T16.checar_faixa_de_bolsa()
        for m in T16.CENARIOS.values():
            self.assertTrue(all(10.0 <= v <= 20.0 for v in m.values()))
        self.assertEqual(T16.CENARIOS["C1"], {"FAIXA 3": 15.0, "FAIXA 2": 15.0, "FAIXA 1": 20.0})
        self.assertEqual(T16.CENARIOS["C3"], {"FAIXA 3": 10.0, "FAIXA 2": 20.0, "FAIXA 1": 20.0})


class TestSaidas(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.resumo = json.loads(T16.OUT_RESUMO.read_text(encoding="utf-8"))
        cls.val = pd.read_csv(T16.OUT_VALIDACAO, dtype={"ciclo": str})
        cls.passou = cls.resumo["validacao_base"]["passou"]
        if cls.passou:
            cls.tab = pd.read_csv(T16.OUT_TABELA, dtype={"ciclo": str})
            cls.rep = pd.read_parquet(T16.OUT_REPLICAS)
            cls.fl = pd.read_csv(T16.OUT_FLUXOS, dtype={"ciclo": str})

    def test_rotulo_cenario_so_em_output_cenarios(self) -> None:
        self.assertEqual(self.resumo["natureza_dos_dados"], "CENARIO_CONTRAFACTUAL")
        for p in sorted(T16.OUT.rglob("*")):
            if p.suffix == ".csv":
                self.assertEqual(set(pd.read_csv(p)["natureza_dos_dados"]), {"CENARIO_CONTRAFACTUAL"}, p.name)
            elif p.suffix == ".parquet":
                self.assertEqual(set(pd.read_parquet(p, columns=["natureza_dos_dados"])["natureza_dos_dados"]),
                                 {"CENARIO_CONTRAFACTUAL"}, p.name)
        # Nada de cenário em output/rdd_bolsa/ (nem arquivo da etapa, nem o rótulo).
        rdd = ROOT / "output" / "rdd_bolsa"
        self.assertEqual(sorted(rdd.rglob("P1_cenario*")), [])
        for p in sorted(rdd.glob("*.json")) + sorted(rdd.glob("*.csv")):
            if p.stat().st_size < 50_000_000:
                self.assertNotIn("CENARIO_CONTRAFACTUAL", p.read_text(encoding="utf-8", errors="replace"), p.name)

    def test_validacao_de_base_segue_a_regra_do_adendo(self) -> None:
        """O cenário base reproduz o observado dentro da tolerância? O veredito gravado tem de ser o da regra
        fixada antes (|B0 − observado| ≤ max(3; 2%) em todas as réplicas), recalculado aqui; se falhou, nenhum
        cenário foi calculado (nada de réplicas, tabela, fluxos ou figuras) e o status é FALHA_VALIDACAO_BASE."""
        for r in self.val.itertuples(index=False):
            tol = max(3, 0.02 * r.observado)
            self.assertAlmostEqual(r.tolerancia, tol)
            self.assertEqual(r.desvio_maximo, max(abs(r.b0_minimo - r.observado), abs(r.b0_maximo - r.observado)))
            self.assertEqual(bool(r.passa), r.desvio_maximo <= tol)
            self.assertLessEqual(r.b0_minimo, r.b0_media)
            self.assertLessEqual(r.b0_media, r.b0_maximo)
        self.assertEqual(self.passou, bool(self.val["passa"].all()))
        cenario = [T16.OUT_TABELA, T16.OUT_REPLICAS, T16.OUT_FLUXOS, T16.FIG_TOTAL, T16.FIG_FAIXAS]
        if self.passou:
            self.assertTrue(all(p.exists() for p in cenario))
        else:
            self.assertEqual(self.resumo["status"], "FALHA_VALIDACAO_BASE")
            self.assertEqual([p.name for p in cenario if p.exists()], [])
            self.assertEqual(self.resumo["figuras"], [])
            self.assertNotIn("principal", self.resumo)
        # Com a classificação publicada (G2 principal), a reconstrução fica perto do observado (≥ 99% no G2).
        self.assertLessEqual(int((self.val["g2_principal_classificacao_publicada"] - self.val["observado"]).abs().max()), 3)
        tot = self.val[self.val["faixa"] == "total"].set_index("ciclo")["observado"]
        for k, c in self.resumo["contagens"].items():
            self.assertEqual(int(tot[k]), c["preenchidas_publicadas"])
            fx = self.val[(self.val["ciclo"] == k) & (self.val["faixa"] != "total")]["observado"].sum()
            self.assertEqual(int(fx), c["preenchidas_publicadas"])   # nenhuma vaga publicada sem faixa

    def test_conservacao_registrada(self) -> None:
        self.assertEqual(self.resumo["validacao_base"]["conservacao_b0"],
                         {"celulas_acima_da_capacidade": 0, "alocados_fora_da_lista": 0})
        if not self.passou:
            return
        c = self.resumo["conservacao"]
        self.assertEqual(c["celulas_acima_da_capacidade"], 0)
        self.assertEqual(c["alocados_fora_da_lista"], 0)
        R = self.resumo["parametros"]["R"]
        self.assertEqual(c["listas_base_iguais_as_observadas"], R * len(T16.VARIANTES))

    def test_parametros_do_adendo(self) -> None:
        p = self.resumo["parametros"]
        self.assertEqual((p["R"], p["semente"], p["K_M8"]), (200, 20261024, 100))
        self.assertEqual((p["tolerancia_abs"], p["tolerancia_rel"]), (3, 0.02))
        self.assertEqual(p["cenarios"], T16.CENARIOS)
        self.assertLess(self.resumo["modelo"]["diferenca_theta_gravado"], 1e-6)
        est = pd.read_csv(ROOT / "output" / "rdd_bolsa" / "P1_estimativas.csv", dtype={"ciclo": str})
        b = est[(est["modelo"] == "M1") & (est["ciclo"] == "empilhado") & (est["termo"] == "bolsa_mil")].iloc[0]
        self.assertAlmostEqual(self.resumo["modelo"]["beta_bolsa"], b["coef"], places=8)
        self.assertEqual(self.resumo["modelo"]["ic95_beta"], [b["ic95_inf"], b["ic95_sup"]])

    def test_identidades_entre_outcomes(self) -> None:
        if not self.passou:
            self.skipTest("validação falhou: sem cenários")
        R = self.resumo["parametros"]["R"]
        w = self.rep.pivot_table(index=["variante", "cenario", "replica", "ciclo"], columns="outcome",
                                 values="valor").reset_index()
        self.assertEqual(len(w), len(T16.VARIANTES) * len(T16.CENARIOS) * R * 4)
        soma_fx = sum(w[f"delta_preenchidas_{f}"] for f in T16.FAIXAS)
        np.testing.assert_allclose(w["delta_preenchidas_total"], soma_fx)
        np.testing.assert_allclose(w["delta_preenchidas_total"],
                                   w["vagas_passam_a_ser_preenchidas"] - w["vagas_deixam_de_ser_preenchidas"])
        self.assertTrue((w["medicos_mudam_de_vaga"] >= w["delta_preenchidas_total"].abs()).all())
        ciclos = w[w["ciclo"] != T16.TOTAL].groupby(["variante", "cenario", "replica"])[list(T16.OUTCOMES)].sum()
        total = w[w["ciclo"] == T16.TOTAL].set_index(["variante", "cenario", "replica"])[list(T16.OUTCOMES)]
        pd.testing.assert_frame_equal(ciclos.sort_index(), total.sort_index(), check_names=False)

    def test_tabela_recalculada_das_replicas(self) -> None:
        if not self.passou:
            self.skipTest("validação falhou: sem cenários")
        t = T16.tabela(self.rep.drop(columns=["natureza_dos_dados"]))
        cols = ["media", "p2_5", "p97_5", "minimo", "maximo"]
        np.testing.assert_allclose(t[cols].to_numpy(), self.tab[cols].to_numpy(), rtol=0, atol=1e-9)
        self.assertTrue((self.tab["replicas"] == self.resumo["parametros"]["R"]).all())

    def test_fluxos_coerentes_com_mudancas(self) -> None:
        if not self.passou:
            self.skipTest("validação falhou: sem cenários")
        R = self.resumo["parametros"]["R"]
        soma = self.fl.groupby(["variante", "cenario", "ciclo"])["soma"].sum()
        mud = self.rep[self.rep["outcome"] == "medicos_mudam_de_vaga"].groupby(["variante", "cenario", "ciclo"])["valor"].sum()
        pd.testing.assert_series_equal(soma.sort_index().astype(float), mud.reindex(soma.index).sort_index(),
                                       check_names=False)
        np.testing.assert_allclose(self.fl["media_por_replica"], self.fl["soma"] / R)

    def test_c2_e_c4_iguais_salvo_custo(self) -> None:
        """No logit, somar a mesma constante à bolsa de todas as células não muda a escolha; C4 = C2 − 5."""
        if not self.passou:
            self.skipTest("validação falhou: sem cenários")
        r = self.rep[self.rep["outcome"] != "delta_custo_mensal_bolsas_mil"]
        a = r[r["cenario"] == "C2"].drop(columns="cenario").reset_index(drop=True)
        b = r[r["cenario"] == "C4"].drop(columns="cenario").reset_index(drop=True)
        pd.testing.assert_frame_equal(a, b)

    def test_hashes_e_figuras(self) -> None:
        for s in self.resumo["saidas"]:
            self.assertEqual(sha256(ROOT / s["caminho"]), s["sha256"], s["caminho"])
        for f in self.resumo["figuras"]:
            self.assertTrue((ROOT / f["arquivo"]).exists())
            self.assertGreater(len(f["como_ler"]), 40)
            self.assertEqual(self.resumo["como_ler"][Path(f["arquivo"]).name], f["como_ler"])

    def test_sem_identificador_de_candidato(self) -> None:
        padrao = re.compile(r"\bc[123](ch2)?_\d{5}\b")
        for p in sorted(T16.OUT.rglob("*")):
            if p.suffix in (".csv", ".json"):
                txt = p.read_text(encoding="utf-8")
                self.assertIsNone(padrao.search(txt), p.name)
                self.assertNotIn("id_candidato", txt, p.name)
                self.assertIsNone(re.search(r"[\d*]{3}\.\d{3}\.\d{3}-[\d*]{2}", txt), p.name)   # CPF, mascarado ou não
            elif p.suffix == ".parquet":
                cols = pd.read_parquet(p).columns
                self.assertNotIn("id_candidato", cols)
                self.assertFalse(pd.read_parquet(p).astype(str).apply(lambda s: s.str.contains(padrao)).any().any())

    def test_integridade_do_script(self) -> None:
        txt = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("ivs_ipea_2010_municipios", txt)
        self.assertNotIn('"output" / "rdd_bolsa" / "P1_c', txt)
        self.assertIn('OUT = ROOT / "output" / "cenarios"', txt)
        self.assertIn('NATUREZA = "CENARIO_CONTRAFACTUAL"', txt)
        self.assertNotIn("to_parquet(P1.", txt)
        self.assertNotIn("run_all", txt)


class TestDoc57b(unittest.TestCase):
    def test_doc_igual_ao_gerado(self) -> None:
        self.assertEqual(T16.DOC.read_text(encoding="utf-8"), T16.gerar_doc(*T16.ler_saidas()))

    def test_topo_diz_que_e_simulacao(self) -> None:
        topo = "\n".join(T16.DOC.read_text(encoding="utf-8").splitlines()[:5])
        self.assertIn("SIMULAÇÃO, NÃO OBSERVAÇÃO", topo)
        self.assertIn("CENARIO_CONTRAFACTUAL", topo)
        self.assertIn("não use estes números como resultado empírico".lower(), topo.lower())

    def test_validacao_e_leitura_no_doc(self) -> None:
        doc = T16.DOC.read_text(encoding="utf-8")
        resumo = json.loads(T16.OUT_RESUMO.read_text(encoding="utf-8"))
        self.assertIn("## 3. Validação de base", doc)
        self.assertIn(resumo["nota_processo"], doc)
        if resumo["validacao_base"]["passou"]:
            self.assertIn("Subir a bolsa redistribui médicos entre vagas ou aumenta o total preenchido?", doc)
            self.assertIn("aritmética simples", doc)
        else:
            self.assertIn("`FALHA_VALIDACAO_BASE`", doc)
            self.assertIn("os cenários não foram calculados", doc)
            self.assertIn("Decisões em aberto, do autor (nenhuma foi executada)", doc)
        for como in resumo["como_ler"].values():
            self.assertIn(como, doc)


if __name__ == "__main__":
    unittest.main()
