"""Testes do P4 (protocolo 54): `scripts/rdd_bolsa/28_trajetoria_medicos.py`.

Três partes:

1. `TestSintetico`: DADOS SINTÉTICOS gerados em memória (semente fixa), rotulados "sintético" e nunca gravados em
   `output/` nem em `data/`. Conferem o Callaway–Sant'Anna (efeito conhecido, controles ainda não iniciados, base
   g − 1, mínimo de controles), o painel médico × mês (zero só para quem não aparece numa competência lida, hora
   vazia = ausente, posto × fora, natureza jurídica), a deduplicação por médico, o IC de Wilson e a razão.
2. `TestSaidasReais`: esquema e rótulos de `output/rdd_bolsa/P4_*`, ausência de identificadores, BKY só onde o
   protocolo manda, hashes das entradas e das figuras, "Como ler" e números recalculados de `output/`.
3. `TestDoc57d`: o doc 57d é igual ao que o script gera das saídas.
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
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "28_trajetoria_medicos.py"
_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location("trajetoria_medicos_28", SCRIPT)
P4 = importlib.util.module_from_spec(_spec)
sys.modules["trajetoria_medicos_28"] = P4
_spec.loader.exec_module(P4)
sys.dont_write_bytecode = _bytecode

OUT = ROOT / "output" / "rdd_bolsa"
EST = OUT / "P4_estimativas.csv"
RESUMO = OUT / "P4_resumo.json"
DOC = ROOT / "docs" / "06_execucao" / "57d_resultados_P4_trajetoria.md"

NATUREZA_SINTETICA = "SINTETICO_TESTE"   # rótulo dos dados gerados aqui (sintético); nunca gravados


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def painel_sintetico(semente: int = 3, ruido: float = 0.0, tau: float = 5.0):
    """SINTÉTICO: médicos com efeito fixo, tendência comum e efeito tau a partir do início (coortes escalonadas)."""
    rng = np.random.default_rng(semente)
    T = 20
    G = np.repeat([6, 9, 12, 15, -1], 60)          # −1: início depois do horizonte (nunca tratado)
    N = G.size
    alfa = rng.normal(40, 10, N)
    tempo = np.linspace(0, 3, T)
    Y = alfa[:, None] + tempo[None, :] + ruido * rng.normal(size=(N, T))
    for i in range(N):
        if G[i] >= 0:
            Y[i, G[i]:] += tau
    return Y, G, {"natureza": NATUREZA_SINTETICA}


class TestSintetico(unittest.TestCase):
    """Verificação sintética (dados sintéticos em memória, rotulados SINTETICO_TESTE)."""

    def test_rotulo_sintetico(self):
        _, _, meta = painel_sintetico()
        self.assertEqual(meta["natureza"], "SINTETICO_TESTE")

    def test_cs_recupera_efeito_constante_sem_ruido(self):
        Y, G, _ = painel_sintetico(ruido=0.0, tau=5.0)
        trat = G >= 0
        xi = P4.pesos_mammen(199, G.size, 1)
        res = P4.estimar_cs(Y, G, trat, xi, e_min=-4, e_max=3, min_controles=10)
        ev = res["evento"].set_index("e")
        for e in range(0, 4):
            self.assertAlmostEqual(ev.loc[e, "theta"], 5.0, places=10)
        for e in (-4, -3, -2):
            self.assertAlmostEqual(ev.loc[e, "theta"], 0.0, places=10)
        self.assertEqual(ev.loc[-1, "theta"], 0.0)
        self.assertAlmostEqual(res["pos"]["att"], 5.0, places=10)

    def test_cs_com_ruido_cobre_o_efeito(self):
        Y, G, _ = painel_sintetico(semente=8, ruido=2.0, tau=3.0)
        xi = P4.pesos_mammen(999, G.size, 2)
        res = P4.estimar_cs(Y, G, G >= 0, xi, e_min=-3, e_max=3, min_controles=10)
        self.assertLess(res["pos"]["ic95_inf"], 3.0)
        self.assertGreater(res["pos"]["ic95_sup"], 3.0)
        self.assertGreater(res["pre"]["p_wald"], 0.001)

    def test_controles_ainda_nao_iniciados_e_minimo(self):
        Y, G, _ = painel_sintetico()
        tab, _ = P4.att_gt(Y, G, G >= 0, [6], e_min=-2, e_max=13, min_controles=61)
        # Em t = 14 só restam como controles a coorte 15 (60) e os nunca tratados (60): 120 >= 61.
        # Em t = 15 só os 60 nunca tratados: abaixo do mínimo, sem estimativa.
        r14 = tab[tab["t"] == 14].iloc[0]
        r15 = tab[tab["t"] == 15].iloc[0]
        self.assertEqual(r14["n_controles"], 120)
        self.assertTrue(np.isfinite(r14["att"]))
        self.assertEqual(r15["n_controles"], 60)
        self.assertTrue(np.isnan(r15["att"]))
        # Pré (t < b): a própria coorte nunca é controle.
        r4 = tab[tab["t"] == 4].iloc[0]
        self.assertEqual(r4["n_controles"], 240)   # coortes 9, 12, 15 e nunca tratados

    def test_mascara_de_tratados_nao_tira_controles(self):
        Y, G, _ = painel_sintetico()
        grupo = np.arange(G.size) % 2 == 0
        tab_a, _ = P4.att_gt(Y, G, G >= 0, [9], e_min=0, e_max=0, min_controles=1)
        tab_b, _ = P4.att_gt(Y, G, (G >= 0) & grupo, [9], e_min=0, e_max=0, min_controles=1)
        self.assertEqual(tab_a.iloc[0]["n_controles"], tab_b.iloc[0]["n_controles"])
        self.assertEqual(tab_b.iloc[0]["n_tratados"], 30)

    def test_painel_medico_sintetico(self):
        comps = ["202406", "202407", "202408"]
        m = pd.DataFrame({"id_prof": ["s1", "s2"], "co_cnes": ["0000001", "0000009"], "co_ibge": ["100001", "200002"]})
        v = pd.DataFrame({
            "id_prof": ["s1", "s1", "s1", "s2"],
            "competencia": ["202406", "202406", "202408", "202407"],
            "co_cnes": ["0000001", "0000002", "0000003", "0000009"],
            "co_municipio": ["100001", "100001", "300003", "200002"],
            "co_cbo": ["225151"] * 4,
            "tp_sus_nao_sus": ["S", "N", "S", "S"],
            "qt_ch_ambulatorial": pd.array([10, 5, 4, None], dtype="Int32"),
            "qt_ch_hosp_sus": pd.array([20, 0, 0, 1], dtype="Int32"),
            "qt_ch_outros": pd.array([0, 0, 0, 0], dtype="Int32"),
            "co_natureza_jur": ["1023", "2062", "3999", "1023"],
        })
        for c in ("id_prof", "co_cnes", "co_municipio", "co_cbo", "tp_sus_nao_sus", "co_natureza_jur"):
            v[c] = v[c].astype("string")
        p = P4.painel_medico(m, v, comps).set_index(["id_prof", "competencia"])
        a = p.loc[("s1", "202406")]
        self.assertEqual(a["horas_totais"], 35)
        self.assertEqual(a["horas_estab_posto"], 30)
        self.assertEqual(a["horas_resto_mun_posto"], 5)
        self.assertEqual(a["horas_mun_posto"], 35)
        self.assertEqual(a["horas_fora_mun_posto"], 0)
        self.assertEqual(a["horas_sus"], 30)
        self.assertEqual(a["horas_nao_sus"], 5)
        self.assertEqual(a["horas_publico"], 30)
        self.assertEqual(a["horas_privado_com_fins"], 5)
        self.assertEqual(a["n_vinculos"], 2)
        # Mês lido sem o médico: zero vínculos e zero horas, com o rótulo.
        b = p.loc[("s1", "202407")]
        self.assertEqual(b["com_vinculo_medico"], 0)
        self.assertEqual(b["n_vinculos"], 0)
        self.assertEqual(b["horas_totais"], 0)
        c = p.loc[("s1", "202408")]
        self.assertEqual(c["horas_fora_mun_posto"], 4)
        self.assertEqual(c["horas_privado_sem_fins"], 4)
        # Hora vazia: horas ausentes, nunca zero; o vínculo conta.
        d = p.loc[("s2", "202407")]
        self.assertTrue(np.isnan(d["horas_totais"]))
        self.assertTrue(np.isnan(d["horas_mun_posto"]))
        self.assertEqual(d["n_vinculos"], 1)

    def test_deduplicacao_por_medico(self):
        comps = ["202406", "202407", "202408"]
        li = pd.DataFrame({"id_medico": ["m1", "m2", "m3"], "ciclo": [1, 1, 3], "co_cnes": ["a", "b", "c"],
                           "co_ibge": ["1", "1", "2"], "cod_curso": [1, 1, 2],
                           "mes_inicio": ["202407", "202407", "202409"],
                           "fonte_lista": ["nominal_2026-08-12", "ativos_2026-09-11", "ativos_2026-09-11"],
                           "faixa_atracao": ["FAIXA 1"] * 3})
        x1 = pd.DataFrame({"id_medico": ["m1", "m2", "m3"], "regra_ligacao": ["d1_pos_hoc"] * 3, "ligado": [1, 1, 1],
                           "faixa": ["FAIXA 1"] * 3, "b_mesmo_mun_ultimo_pre": [1.0, 0.0, np.nan]})
        ch = pd.DataFrame({"id_prof": ["p1", "p1", "p2"], "origem": ["X1"] * 3, "id_externo": ["m1", "m2", "m3"],
                           "regra_ligacao": ["d1_pos_hoc"] * 3})
        m, diag = P4.medicos_da_regra("d1_pos_hoc", li, x1, ch, comps)
        self.assertEqual(list(m["id_prof"]), ["p1", "p2"])
        self.assertEqual(m.loc[0, "id_medico"], "m2")          # a lista de ativos vem primeiro
        self.assertEqual(m.loc[0, "origem"], "novo_no_municipio")
        self.assertEqual(int(m.loc[1, "G"]), -1)                 # início depois do horizonte
        self.assertFalse(bool(m.loc[1, "tratavel"]))             # ciclo 3 nunca é coorte tratada
        self.assertEqual(diag["registros_descartados_na_deduplicacao"], 1)

    def test_wilson_e_razao(self):
        p, lo, hi = P4.wilson(50, 100)
        self.assertAlmostEqual(p, 0.5)
        self.assertLess(lo, 0.5)
        self.assertGreater(hi, 0.5)
        a = np.array([-1.0, -1.0, -2.0, 0.0])
        b = np.array([4.0, 4.0, 4.0, 4.0])
        r, lo, hi = P4.razao_ic(a, b, 1)
        self.assertAlmostEqual(r, 0.25)
        self.assertLessEqual(lo, r)
        self.assertGreaterEqual(hi, r)
        self.assertTrue(np.isnan(P4.razao_ic(a, -b, 1)[0]))


class TestSaidasReais(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.est = pd.read_csv(EST, dtype={"grupo": str})
        cls.est["nota"] = cls.est["nota"].fillna("")
        cls.resumo = json.loads(RESUMO.read_text(encoding="utf-8"))

    def test_esquema_e_rotulos(self):
        self.assertEqual(list(self.est.columns), P4.COLUNAS)
        self.assertTrue((self.est["natureza_dos_dados"] == "EMPIRICO").all())
        self.assertTrue((self.est["estatuto"] == "EXPLORATORIO_P4").all())
        self.assertEqual(self.resumo["natureza_dos_dados"], "EMPIRICO")
        self.assertEqual(self.resumo["estatuto"], "EXPLORATORIO_P4")
        self.assertTrue(set(self.est["status"]) <= {"EXECUTADO", "SEM_ESTIMATIVA", "REFERENCIA"})
        self.assertEqual(set(self.est["especificacao"]), {"T4.1a", "T4.1b", "T4.1c", "T4.2", "T4.3", "origem"})
        self.assertEqual(set(self.est["regra_ligacao"]), {"d1_pos_hoc", "literal_doc45"})
        self.assertTrue(self.est["leitura"].fillna("").str.len().gt(0).all())

    def test_ausencia_tem_nota(self):
        sem = self.est[self.est["estimativa"].isna()]
        self.assertTrue((sem["nota"] != "").all())
        self.assertTrue((sem["status"] == "SEM_ESTIMATIVA").all())

    def test_sem_identificadores(self):
        proibidos = ("nome", "cpf", "cns", "crm", "co_profissional", "id_prof", "id_medico", "nu_registro")
        for c in self.est.columns:
            self.assertFalse(any(p in c.lower() for p in proibidos), c)
        texto = EST.read_text(encoding="utf-8") + RESUMO.read_text(encoding="utf-8")
        self.assertIsNone(re.search(r"\bg5p_\d+|\bx1m_\d+", texto))
        self.assertIsNone(re.search(r"(?<![\d.])\d{11}(?![\d.])|(?<![\d.])\d{15}(?![\d.])", EST.read_text(encoding="utf-8")))
        for chave in ("_nome", "crm", "cpf", "cns"):
            self.assertNotIn(f'"{chave}"', RESUMO.read_text(encoding="utf-8").lower())

    def test_bky_so_no_protocolo(self):
        b = self.est[self.est["entra_bky"]]
        self.assertTrue(set(b["especificacao"]) == {"T4.1b", "T4.1c"})
        self.assertTrue((b["janela"] == "[-6,6]").all())
        self.assertTrue((b["e"] >= 0).all())
        self.assertTrue(set(b["outcome"]) <= set(P4.OUT_PROTOCOLO))
        self.assertTrue((b["medida"] == "att_e").all())
        self.assertTrue(self.est.loc[~self.est["entra_bky"], "q_bky"].isna().all())
        for (esp, regra), d in b.groupby(["especificacao", "regra_ligacao"]):
            q = P4.L.qvalores_bky(d["p_valor"].to_numpy(float))
            np.testing.assert_allclose(q, d["q_bky"].to_numpy(float), rtol=0, atol=1e-9)
            n_out = 14 * 7 * (2 if esp == "T4.1c" else 1)
            self.assertEqual(len(d), n_out)

    def test_hashes_entradas_e_figuras(self):
        for ent in self.resumo["entradas"]:
            self.assertEqual(sha256(ROOT / ent["caminho"]), ent["sha256"], ent["caminho"])
        self.assertEqual(sha256(EST), self.resumo["saidas"]["P4_estimativas.csv"]["sha256"])
        figs = self.resumo["saidas"]["figuras"]
        self.assertEqual(len(figs), 5)
        for f in figs:
            self.assertEqual(sha256(ROOT / f["arquivo"]), f["sha256"])
            self.assertTrue(f["como_ler"])
            self.assertEqual(self.resumo["como_ler"][Path(f["arquivo"]).name], f["como_ler"])
            n_frases = len([s for s in re.split(r"(?<=[.;])\s", f["como_ler"]) if s.strip()])
            self.assertLessEqual(n_frases, 3)

    def test_nao_le_ivs_errado_nem_mes_proibido(self):
        fonte = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("ivs_ipea_2010_municipios", fonte)
        self.assertEqual(self.resumo["parametros"]["competencias"], ["202406", "202608"])
        self.assertEqual(self.resumo["parametros"]["limite_exclusivo"], "202609")

    def test_principais_batem_com_csv(self):
        pr = self.resumo["principais"]
        r = self.est[(self.est["especificacao"] == "T4.1b") & (self.est["regra_ligacao"] == "d1_pos_hoc")
                     & (self.est["janela"] == "[-6,6]") & (self.est["outcome"] == "horas_totais")
                     & (self.est["medida"] == "att_pos_medio")].iloc[0]
        self.assertAlmostEqual(pr["att_pos_medio_horas_totais"]["estimativa"], r["estimativa"], places=8)
        # Horas totais = município do posto + fora: vale para θ(e) por linearidade do estimador.
        for med in ("att_pos_medio",):
            v = {o: self.est[(self.est["especificacao"] == "T4.1b") & (self.est["regra_ligacao"] == "d1_pos_hoc")
                             & (self.est["janela"] == "[-6,6]") & (self.est["outcome"] == o)
                             & (self.est["medida"] == med)].iloc[0]["estimativa"]
                 for o in ("horas_totais", "horas_mun_posto", "horas_fora_mun_posto")}
            self.assertAlmostEqual(v["horas_totais"], v["horas_mun_posto"] + v["horas_fora_mun_posto"], places=6)

    def test_t43_saldo_e_soma(self):
        t = self.est[(self.est["especificacao"] == "T4.3") & (self.est["medida"] == "soma")]
        for (regra, am, gt, g), d in t.groupby(["regra_ligacao", "amostra", "grupo_tipo", "grupo"]):
            s = d.set_index("outcome")["estimativa"]
            self.assertAlmostEqual(s["delta_horas_totais"],
                                   s["delta_horas_mun_posto"] + s["delta_horas_fora_mun_posto"], places=4)
            self.assertAlmostEqual(s["delta_horas_mun_posto"],
                                   s["delta_horas_estab_posto"] + s["delta_horas_resto_mun_posto"], places=4)

    def test_origem_recalculada_da_x1(self):
        """Fração já no município (regra D1) recalculada da X1 e das chaves do a16, com a deduplicação."""
        x1 = pd.read_parquet(P4.ARQ_X1)
        ch = pd.read_parquet(P4.ARQ_CHAVES)
        li, _ = P4.ler_listas()
        m, _ = P4.medicos_da_regra("d1_pos_hoc", li, x1, ch, P4.competencias())
        t = m[m["tratavel"]]
        esperado = float((t["b_mesmo_mun_ultimo_pre"] == 1).mean())
        r = self.est[(self.est["especificacao"] == "origem") & (self.est["regra_ligacao"] == "d1_pos_hoc")
                     & (self.est["grupo_tipo"] == "todos") & (self.est["outcome"] == "fracao_ja_no_municipio_x1b")]
        self.assertAlmostEqual(float(r.iloc[0]["estimativa"]), esperado, places=10)
        self.assertEqual(int(r.iloc[0]["n_obs"]), len(t))

    def test_t41a_recalculada_do_painel_a16(self):
        """Média das horas totais por e, ciclo 1, regra D1, refeita do painel médico × mês do a16."""
        x1 = pd.read_parquet(P4.ARQ_X1)
        ch = pd.read_parquet(P4.ARQ_CHAVES)
        li, _ = P4.ler_listas()
        comps = P4.competencias()
        m, _ = P4.medicos_da_regra("d1_pos_hoc", li, x1, ch, comps)
        a = pd.read_parquet(P4.ARQ_MED, columns=["id_prof", "competencia", "horas_totais"])
        a["t"] = a["competencia"].astype(str).map({c: i for i, c in enumerate(comps)})
        d = a.merge(m[m["tratavel"] & (m["ciclo"] == 1)][["id_prof", "G"]], on="id_prof")
        d["e"] = d["t"] - d["G"]
        for e in (-6, -1, 0, 5):
            esperado = d.loc[d["e"] == e, "horas_totais"].astype(float).mean()
            r = self.est[(self.est["especificacao"] == "T4.1a") & (self.est["regra_ligacao"] == "d1_pos_hoc")
                         & (self.est["amostra"] == "completa") & (self.est["grupo"] == "1")
                         & (self.est["outcome"] == "horas_totais") & (self.est["e"] == e)]
            self.assertAlmostEqual(float(r.iloc[0]["estimativa"]), esperado, places=6)


class TestDoc57d(unittest.TestCase):
    def test_doc_igual_ao_gerado(self):
        est, resumo = P4.ler_saidas()
        self.assertEqual(DOC.read_text(encoding="utf-8"), P4.gerar_doc(est, resumo))

    def test_linguagem(self):
        texto = DOC.read_text(encoding="utf-8").lower()
        for termo in ("efeito causal", "causou", "comprova"):
            self.assertNotIn(termo, texto)
        self.assertIn("vínculo não é presença", texto)
        self.assertIn("como ler", texto)


if __name__ == "__main__":
    unittest.main()
