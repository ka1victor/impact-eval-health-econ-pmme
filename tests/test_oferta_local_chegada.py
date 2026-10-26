"""Testes do protocolo 60, parte B (H4): `scripts/rdd_bolsa/37_oferta_local_chegada.py`.

1. `TestSintetico`: DADOS SINTÉTICOS gerados em memória (rotulados SINTETICO_TESTE, nunca gravados): índices de
   coorte com controles que saem no início do ciclo 3, Callaway–Sant'Anna recuperando efeito conhecido com esses
   controles, Holm e BKY nas famílias certas e as regras da leitura pré-registrada.
2. `TestPortoes`: os dois portões, refeitos aqui: coortes do D2 (datas e contagens) a partir de `K_D2_resumo.json`
   e de `OL_ligacao_municipio.csv`; B1 e B2 iguais ao F3.1 e F3.3 do E7 em 202506, lidos do painel a09.
3. `TestSaidasReais`: esquema, rótulos, números recalculados de `output/`, hashes, figuras e nenhum identificador
   pessoal.
4. `TestDoc57k`: o doc é igual ao que o script gera das saídas.
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
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "37_oferta_local_chegada.py"
_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location("oferta_local_37", SCRIPT)
OL = importlib.util.module_from_spec(_spec)
sys.modules["oferta_local_37"] = OL
_spec.loader.exec_module(OL)
sys.dont_write_bytecode = _bytecode

OUT = ROOT / "output" / "rdd_bolsa"
EST = OUT / "OL_estimativas.csv"
LIG = OUT / "OL_ligacao_municipio.csv"
RESUMO = OUT / "OL_resumo.json"
DIR_FIG = OUT / "OL_figuras"
DOC = ROOT / "docs" / "06_execucao" / "57k_resultados_oferta_local.md"
NATUREZA_SINTETICA = "SINTETICO_TESTE"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def ler():
    est = pd.read_csv(EST, dtype={"outcome_id": str})
    lig = pd.read_csv(LIG, dtype={"co_ibge": str, "mes_chegada": str})
    resumo = json.loads(RESUMO.read_text(encoding="utf-8"))
    return est, lig, resumo


# ---------------------------------------------------------------------------
# 1. Sintético
# ---------------------------------------------------------------------------

class TestSintetico(unittest.TestCase):
    """Dados sintéticos em memória (SINTETICO_TESTE)."""

    def test_indices_coorte_e_controles_que_saem(self):
        meses = list(OL.MESES)
        am = pd.Index(["s01", "s02", "s03", "s04", "s05", "s06"], name="co_ibge")
        chegadas = pd.DataFrame({"chegada": ["202509", np.nan, np.nan, "202609", np.nan, np.nan]}, index=am)
        ativos = pd.Series({"s02": "202608", "s03": "202609", "s01": "202501", "s06": "202509"})
        G, coortes, info, saida = OL.indices(chegadas, ativos, am)
        self.assertEqual(G[0], meses.index("202509"))          # tratado: mês da chegada (não o da lista de ativos)
        self.assertEqual(list(G[1:]), [-1] * 5)                # ninguém mais é coorte
        self.assertEqual(saida[1], meses.index("202608"))      # ciclo 3: sai dos controles em 202608
        self.assertEqual(saida[5], meses.index("202509"))      # início no mesmo mês de uma coorte: não vira coorte
        self.assertEqual(list(saida[[0, 2, 3, 4]]), [-1] * 4)
        self.assertEqual(coortes, [meses.index("202509")])
        self.assertEqual(info["n_tratados"], 1)
        self.assertEqual(info["coortes_mensais"], {"202509": 1})
        self.assertEqual(info["n_controles_censurados"], 2)
        self.assertEqual(info["n_nunca_tratados_no_horizonte"], 3)
        Y = OL.censurar(np.ones((6, len(meses))), saida)
        self.assertTrue(np.isnan(Y[1, meses.index("202608"):]).all())
        self.assertTrue(np.isfinite(Y[1, :meses.index("202608")]).all())
        self.assertTrue(np.isfinite(Y[[0, 2, 3, 4]]).all())

    def test_cs_com_controle_que_sai_recupera_efeito(self):
        rng = np.random.default_rng(5)
        T = len(OL.MESES)
        g1, g2, gc = OL.MESES.index("202509"), OL.MESES.index("202603"), OL.MESES.index("202608")
        G = np.repeat([g1, g2, -1, -1, -1], 50)
        saida = np.repeat([-1, -1, gc, g1, -1], 50)
        N = G.size
        Y = rng.normal(10, 2, N)[:, None] + np.linspace(0, 2, T)[None, :]
        for i in range(N):
            if G[i] >= 0:
                Y[i, G[i]:] += 3.0
            elif saida[i] >= 0:
                Y[i, saida[i]:] += 50.0   # o início fora das coortes mexeria muito: não pode contaminar a comparação
        xi = OL.D2M.pesos_mammen(199, N, 1)
        r = OL.D2M.estimar_cs(OL.censurar(Y, saida), G, [g1, g2], xi, e_min=OL.E_MIN, e_max=OL.E_MAX)
        ev = r["evento"].set_index("e")
        for e in range(0, OL.E_MAX + 1):
            self.assertAlmostEqual(ev.loc[e, "theta"], 3.0, places=10)
        for e in range(OL.E_MIN, -1):
            self.assertAlmostEqual(ev.loc[e, "theta"], 0.0, places=10)
        tab, _ = OL.D2M.att_gt(OL.censurar(Y, saida), G, [g1, g2], e_min=OL.E_MIN, e_max=OL.E_MAX)
        self.assertTrue((tab.loc[tab["g"] == g1, "n_tratados"] == 50).all())

    def test_holm_e_bky_nas_familias(self):
        linhas = []
        for oid, p in zip(OL.IDS, (0.01, 0.04, 0.03, 0.5, 0.2)):
            linhas.append({"outcome_id": oid, "medida": "att_pos_medio", "p_valor": p})
            linhas.append({"outcome_id": oid, "medida": "att_e", "p_valor": 0.001})
        est = OL.aplicar_multiplos(pd.DataFrame(linhas))
        pos = est[est["medida"] == "att_pos_medio"].set_index("outcome_id")
        self.assertAlmostEqual(pos.loc["B1", "p_holm"], 0.02)
        self.assertAlmostEqual(pos.loc["B2", "p_holm"], 0.04)
        self.assertTrue(pos.loc[["B3", "B4", "B5"], "p_holm"].isna().all())
        self.assertTrue(pos.loc[["B1", "B2"], "q_bky"].isna().all())
        self.assertTrue(pos.loc[["B3", "B4", "B5"], "q_bky"].notna().all())
        self.assertTrue(est.loc[est["medida"] == "att_e", ["p_holm", "q_bky"]].isna().all().all())

    def _est(self, att, padj, pre_p, rup):
        linhas = []
        for oid in OL.IDS:
            fam = OL.SPEC[oid]["familia"]
            linhas += [{"outcome_id": oid, "medida": "att_pos_medio", "valor": att[oid],
                        "p_holm": padj[oid] if fam == "holm" else np.nan,
                        "q_bky": padj[oid] if fam == "bky" else np.nan},
                       {"outcome_id": oid, "medida": "pretendencia_wald", "p_valor": pre_p[oid]},
                       {"outcome_id": oid, "medida": "RM_condicional_ruptura", "valor": rup[oid]},
                       {"outcome_id": oid, "medida": "RM_hibrido_ruptura", "valor": rup[oid]}]
        # Auditoria 34: o esquema completo (colunas e e Mbar vazias), como nas saídas reais.
        return pd.DataFrame(linhas).reindex(columns=OL.COLUNAS_EST)

    def test_leitura_preregistrada(self):
        um = {o: 1.0 for o in OL.IDS}
        # B2 sobe com tudo; B3 não se distingue: ganho dos médicos do programa.
        est = self._est({**um, "B3": 0.1}, {"B1": 0.3, "B2": 0.01, "B3": 0.4, "B4": 0.5, "B5": 0.6},
                        {o: 0.5 for o in OL.IDS}, {**um, "B2": 1.5})
        c = OL.classificar(est)
        self.assertTrue(c["B2"]["sobe_com_diagnosticos"])
        self.assertIn("o ganho vem dos médicos do programa", OL.gerar_leitura(est))
        # B2 sobe, mas ruptura < 1: não chama de aumento.
        est = self._est(um, {"B1": 0.3, "B2": 0.01, "B3": 0.4, "B4": 0.5, "B5": 0.6},
                        {o: 0.5 for o in OL.IDS}, {**um, "B2": 0.4})
        txt = OL.gerar_leitura(est)
        self.assertFalse(OL.classificar(est)["B2"]["sobe_com_diagnosticos"])
        self.assertIn("não dá para falar em aumento", txt)
        self.assertIn("a ruptura M̄ fica abaixo de 1", txt)
        # Pré que não passa.
        est = self._est(um, {"B1": 0.3, "B2": 0.01, "B3": 0.4, "B4": 0.5, "B5": 0.6},
                        {**{o: 0.5 for o in OL.IDS}, "B2": 0.01}, {**um, "B2": 2.0})
        self.assertIn("o pré não passa", OL.gerar_leitura(est))
        # B3 cai: deslocamento.
        est = self._est({**um, "B3": -1.0}, {"B1": 0.3, "B2": 0.3, "B3": 0.01, "B4": 0.5, "B5": 0.6},
                        {o: 0.5 for o in OL.IDS}, um)
        self.assertIn("sinal de deslocamento", OL.gerar_leitura(est))


# ---------------------------------------------------------------------------
# 2. Portões
# ---------------------------------------------------------------------------

class TestPortoes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.est, cls.lig, cls.resumo = ler()

    def test_portoes_aprovados_no_resumo(self):
        p = self.resumo["portoes"]
        self.assertTrue(p["coortes"]["aprovado"])
        self.assertTrue(all(p["coortes"]["conferencias"].values()))
        self.assertTrue(p["definicoes"]["aprovado"])

    def test_coortes_reproduzem_o_d2(self):
        d2 = json.loads((OUT / "K_D2_resumo.json").read_text(encoding="utf-8"))["coortes"]
        tri = self.lig["mes_chegada"].map(lambda c: f"{c[:4]}{3 * ((int(c[4:]) - 1) // 3) + 1:02d}")
        contagem = tri.value_counts().sort_index()
        self.assertEqual({k: int(v) for k, v in contagem.items()}, {k: v["municipios"] for k, v in d2.items()})
        self.assertEqual(self.resumo["portoes"]["coortes"]["coortes_deste_bloco"], d2)
        mensais = self.lig["mes_chegada"].value_counts().sort_index()
        self.assertEqual(sum(v["municipios"] for v in d2.values()), int(len(self.lig)))
        self.assertEqual({k: int(v) for k, v in mensais.items()}, self.resumo["coortes"]["coortes_mensais"])
        self.assertEqual(int(len(self.lig)), self.resumo["coortes"]["n_tratados"])

    def test_definicoes_reproduzem_f3_do_e7(self):
        mes = OL.MES_PORTAO_DEFINICOES
        self.assertLess(mes, min(self.lig["mes_chegada"]))     # mês do pré de todas as coortes
        p = pd.read_parquet(OL.PAINEL, columns=["co_ibge", "competencia", "grupo", "n_vinculos", "horas_sus_semanais"],
                            filters=[("competencia", "==", mes), ("grupo", "==", "alvo_pmme")])
        p["co_ibge"] = p["co_ibge"].astype(str)
        pop = pd.read_csv(OL.POP22, dtype={"co_ibge_6d": str}).set_index("co_ibge_6d")["populacao_2022"].astype(float)
        p = p.set_index("co_ibge")
        base, _ = OL.K1M.ler_universo()
        alvo = p.index.intersection(base.index)
        bpop = base.loc[alvo].rename_axis("co_ibge").reset_index()[["co_ibge", "s_mil", "populacao_2022"]]
        for col, fid in (("n_vinculos", "F3.1"), ("horas_sus_semanais", "F3.3")):
            spec = next(c for c in OL.E7.CATALOGO if c["id"] == fid)
            ref = OL.E7.serie_outcome(p.reset_index(), spec, bpop).set_index("co_ibge")["y"].reindex(alvo)
            meu = pd.to_numeric(p.loc[alvo, col], errors="coerce").astype(float) / pop.reindex(alvo) * 1e4
            self.assertTrue((ref.isna() == meu.isna()).all(), fid)
            self.assertLess(float(np.nanmax(np.abs(ref - meu))), 1e-9, fid)


# ---------------------------------------------------------------------------
# 3. Saídas reais
# ---------------------------------------------------------------------------

class TestSaidasReais(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.est, cls.lig, cls.resumo = ler()

    def test_esquema_e_rotulos(self):
        self.assertEqual(list(self.est.columns), OL.COLUNAS_EST)
        for df in (self.est, self.lig):
            self.assertEqual(set(df["natureza_dos_dados"]), {"EMPIRICO"})
            self.assertEqual(set(df["estatuto"]), {"PROTOCOLO_60_POS_RESULTADO"})
        self.assertEqual(self.resumo["natureza_dos_dados"], "EMPIRICO")
        self.assertEqual(self.resumo["estatuto"], "PROTOCOLO_60_POS_RESULTADO")
        self.assertEqual(sorted(self.est["outcome_id"].unique()), OL.IDS)
        for oid in OL.IDS:
            g = self.est[self.est["outcome_id"] == oid]
            self.assertEqual(sorted(g.loc[g["medida"] == "att_e", "e"].astype(int)), list(range(-6, 7)))
            for m in ("att_pos_medio", "pretendencia_wald", "pretendencia_supt", "RM_condicional_ruptura",
                      "RM_hibrido_ruptura", "RM_descritivo_pre"):
                self.assertEqual(int((g["medida"] == m).sum()), 1, (oid, m))
            for met in OL.METODOS_RM:
                self.assertEqual(sorted(g.loc[g["medida"] == f"RM_{met}", "Mbar"]), list(OL.GRADE_RM))

    def test_att_pos_e_inferencia(self):
        z = stats.norm.ppf(0.975)
        for oid in OL.IDS:
            g = self.est[self.est["outcome_id"] == oid]
            ev = g[(g["medida"] == "att_e") & (g["e"] >= 0)]["valor"]
            pos = g[g["medida"] == "att_pos_medio"].iloc[0]
            self.assertAlmostEqual(pos["valor"], ev.mean(), places=10)
            self.assertAlmostEqual(pos["ic95_inf"], pos["valor"] - z * pos["ep"], places=8)
            self.assertAlmostEqual(pos["ic95_sup"], pos["valor"] + z * pos["ep"], places=8)
            self.assertAlmostEqual(pos["p_valor"], 2 * stats.norm.sf(abs(pos["valor"] / pos["ep"])), places=8)
            base = g[(g["medida"] == "att_e") & (g["e"] == -1)].iloc[0]
            self.assertEqual(base["valor"], 0.0)
            for _, r in g[g["medida"] == "att_e"].iterrows():
                self.assertTrue(np.isfinite(r["valor"]), (oid, r["e"]))
                if r["e"] != -1:
                    self.assertTrue(np.isfinite(r["ep"]))

    def test_holm_e_bky_recalculados(self):
        pos = self.est[self.est["medida"] == "att_pos_medio"].set_index("outcome_id")
        p = pos.loc[["B1", "B2"], "p_valor"].to_numpy()
        o = np.argsort(p)
        h = np.empty(2)
        h[o[0]] = min(1, 2 * p[o[0]])
        h[o[1]] = max(h[o[0]], min(1, p[o[1]]))
        np.testing.assert_allclose(pos.loc[["B1", "B2"], "p_holm"].to_numpy(), h, rtol=0, atol=1e-12)
        q = OL.L.qvalores_bky(pos.loc[["B3", "B4", "B5"], "p_valor"].to_numpy())
        np.testing.assert_allclose(pos.loc[["B3", "B4", "B5"], "q_bky"].to_numpy(), q, rtol=0, atol=1e-12)
        self.assertTrue(self.est.loc[self.est["medida"] != "att_pos_medio", ["p_holm", "q_bky"]].isna().all().all())

    def test_ruptura_coerente_com_a_grade(self):
        """Ruptura pela regra da honestdid_lib (protocolo 59): 0 se o IC em M̄ = 0 inclui zero; senão, todo M̄ da
        grade abaixo dela exclui zero."""
        for oid in OL.IDS:
            g = self.est[self.est["outcome_id"] == oid]
            for met in OL.METODOS_RM:
                rup = float(g[g["medida"] == f"RM_{met}_ruptura"]["valor"].iloc[0])
                s = g[g["medida"] == f"RM_{met}"].set_index("Mbar")
                exclui = (s["ic95_inf"] > 0) | (s["ic95_sup"] < 0)
                self.assertEqual(rup == 0.0, not bool(exclui.loc[0.0]), (oid, met))
                for mb in s.index[s.index < rup - 1e-9]:
                    self.assertTrue(exclui.loc[mb], (oid, met, mb, rup))
                self.assertTrue((s["ic95_inf"] <= s["valor"] + 1e-9).all())
                self.assertTrue((s["ic95_sup"] >= s["valor"] - 1e-9).all())

    def test_ligacao_recalculada(self):
        t = self.lig
        com = t[t["n_registros_x1_ciclos_1_2"] > 0]
        np.testing.assert_allclose(com["fracao_nao_ligados"],
                                   com["n_nao_ligados"] / com["n_registros_x1_ciclos_1_2"], atol=1e-12)
        self.assertTrue((t["n_nao_ligados"] == t["n_registros_x1_ciclos_1_2"] - t["n_ligados"]).all())
        for k in ("pre", "pos"):
            ok = t[f"horas_b2_{k}"] > 0
            np.testing.assert_allclose(t.loc[ok, f"parcela_subtraida_{k}"],
                                       t.loc[ok, f"horas_subtraidas_{k}"] / t.loc[ok, f"horas_b2_{k}"], atol=1e-12)
            self.assertTrue((t[f"horas_subtraidas_{k}"].dropna() <= t[f"horas_b2_{k}"].dropna() + 1e-9).all())
            lg = self.resumo["ligacao"]
            self.assertAlmostEqual(lg[f"parcela_subtraida_agregada_{k}"],
                                   t[f"horas_subtraidas_{k}"].sum() / t[f"horas_b2_{k}"].sum(), places=12)
        lg = self.resumo["ligacao"]
        self.assertEqual(lg["nao_ligados_nos_tratados"], int(com["n_nao_ligados"].sum()))
        # Auditoria 34: nota toda vazia é lida como float; fillna antes do .str.
        notas = t.loc[t["n_registros_x1_ciclos_1_2"] == 0, "nota"].fillna("").astype(str)
        self.assertTrue(notas.str.len().gt(0).all())

    def test_hashes(self):
        r = self.resumo
        self.assertEqual(r["protocolo"]["sha256_texto"], sha256(OL.PROTOCOLO_MD))
        for e in r["entradas"]:
            self.assertEqual(e["sha256"], sha256(ROOT / e["caminho"]), e["caminho"])
        for s in r["saidas"]:
            self.assertEqual(s["sha256"], sha256(ROOT / s["arquivo"]), s["arquivo"])
        for f in r["figuras"]:
            self.assertEqual(f["sha256"], sha256(ROOT / f["arquivo"]), f["arquivo"])

    def test_figuras_com_como_ler(self):
        figs = {f["outcome_id"]: f for f in self.resumo["figuras"]}
        self.assertEqual(set(figs), {"B1", "B2", "B3"})
        self.assertEqual(sorted(p.name for p in DIR_FIG.glob("*.png")),
                         sorted(Path(f["arquivo"]).name for f in figs.values()))
        for oid, f in figs.items():
            self.assertTrue(f["como_ler"].startswith("COMO LER."))
            self.assertIn("não efeito da bolsa", f["como_ler"])
            self.assertEqual(f["como_ler"], OL.como_ler(oid))

    def test_sem_identificador_pessoal(self):
        proibidas = {"nome", "cpf", "crm", "cns", "id_prof", "id_medico", "co_profissional_sus", "nu_registro"}
        padrao = re.compile(r"g5p_\d|x1m_\d|\b\d{3}\.\d{3}\.\d{3}-\d{2}\b", re.I)
        for df in (self.est, self.lig):
            self.assertFalse(proibidas & {c.lower() for c in df.columns})
        for arq in [EST, LIG, RESUMO, DOC]:
            self.assertIsNone(padrao.search(arq.read_text(encoding="utf-8")), arq.name)
        texto = RESUMO.read_text(encoding="utf-8").lower()
        for chave in ('"nome"', '"crm"', '"cpf"', '"id_prof"'):
            self.assertNotIn(chave, texto)

    def test_horizonte_e_fontes(self):
        self.assertEqual(self.resumo["parametros"]["meses"], ["202406", "202608"])
        self.assertTrue((self.lig["mes_chegada"] < "202609").all())
        fonte = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("ivs_ipea_2010_municipios", fonte)
        self.assertIn('"202609"', fonte)
        self.assertEqual(self.resumo["parametros"]["bootstrap"]["semente"], 20261026)


# ---------------------------------------------------------------------------
# 4. Doc
# ---------------------------------------------------------------------------

class TestDoc57k(unittest.TestCase):
    def test_doc_igual_ao_gerado(self):
        est, lig, resumo = ler()
        gerado = OL.gerar_tabelas_doc(est, lig, resumo)
        no_doc = OL.tabelas_no_doc(DOC.read_text(encoding="utf-8"))
        self.assertEqual(set(no_doc), set(gerado))
        for k, v in gerado.items():
            self.assertEqual(no_doc[k], v, k)

    def test_doc_tem_secoes_e_limites(self):
        texto = DOC.read_text(encoding="utf-8")
        for s in ("## 1. O que se mede", "## 2. Amostra e coortes", "## 4. Leitura simples", "## 5. Tabelas",
                  "## 6. Figuras", "## 7. Limites", "Vínculo cadastrado não é presença",
                  "ATT sob tendências paralelas da chegada, não efeito da bolsa", "Seleção da chegada"):
            self.assertIn(s, texto)

    def test_linguagem(self):
        est, lig, resumo = ler()
        c = OL.classificar(est)
        leitura = OL.gerar_tabelas_doc(est, lig, resumo)["leitura"]
        if not any(c[o]["sobe_com_diagnosticos"] for o in ("B1", "B2")):
            self.assertIn("não dá para falar em aumento", leitura)
        self.assertNotIn("efeito da chegada", leitura)
        self.assertIn("não efeito da bolsa", leitura)


class TestCorrecoesAuditoria34(unittest.TestCase):
    """Correções de texto e figura da auditoria 34 (docs/auditorias/34_auditoria_oferta_local.md)."""

    @classmethod
    def setUpClass(cls):
        cls.est, cls.lig, cls.resumo = ler()
        cls.leitura = OL.gerar_tabelas_doc(cls.est, cls.lig, cls.resumo)["leitura"]

    def test_leitura_descreve_mudanca_e_nao_nivel(self):
        self.assertNotIn("ficaram maiores", self.leitura)
        self.assertNotIn("ficaram menores", self.leitura)
        self.assertIn("a mudança nas horas SUS desses especialistas (B2)", self.leitura)

    def test_ruptura_zero_por_potencia_explicada(self):
        c = OL.classificar(self.est)
        for oid in ("B1", "B2"):
            g = self.est[self.est["outcome_id"] == oid]
            pos = g[g["medida"] == "att_pos_medio"].iloc[0]
            s0 = g[(g["medida"] == "RM_condicional") & (g["Mbar"] == 0.0)].iloc[0]
            if (pos["ic95_inf"] > 0 or pos["ic95_sup"] < 0) and s0["ic95_inf"] <= 0 <= s0["ic95_sup"]:
                self.assertIn("pouca potência do teste de Andrews, Roth e Pakes", self.leitura)
                self.assertEqual(c[oid]["ruptura_min"], 0.0)

    def test_b3_positivo_nao_vira_atracao(self):
        c = OL.classificar(self.est)["B3"]
        if c["sobe"] and c["ruptura_min"] < 1:
            self.assertIn("não é lido como atração de outros especialistas", self.leitura)

    def test_como_ler_cabe_na_figura(self):
        import textwrap
        self.assertLessEqual(OL.LARGURA_COMO_LER, 155)
        for oid in OL.FIGURAS:
            txt = OL.como_ler(oid)
            self.assertIn("vinha crescendo antes da chegada", txt)
            self.assertTrue(all(len(x) <= OL.LARGURA_COMO_LER for x in textwrap.wrap(txt, OL.LARGURA_COMO_LER)))

    def test_portao_com_virgula_decimal(self):
        texto = DOC.read_text(encoding="utf-8")
        self.assertNotIn("0.0e+00", texto)
        self.assertNotIn("coortes d2 refeitas", texto)


if __name__ == "__main__":
    unittest.main()
