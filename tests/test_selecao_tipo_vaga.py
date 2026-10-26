"""Testes do adendo 48f (script 46): seleção pelo tipo de vaga na H1 (SV-1 a SV-5).

- Esquema, `natureza_dos_dados = EMPIRICO` e estatuto `ADENDO_48F_POS_RESULTADO` em todas as saídas `SV_*`.
- Running variable só o IVS oficial (a08); o arquivo local de IVS não é lido; nada escrito em `data/`.
- Portão: HI-1/HI-2 do 48b e D-b do 57l reproduzidos (<= 1e-8); SV-2 entre S = 1 igual ao CL-0 do 48d.
- Limites de Lee: ordem, combinação dos ciclos, IC de Imbens–Manski recalculado, 1.999 reamostras; o ponto do SV-3
  refeito com uma aparagem escrita no teste a partir das bases.
- Leitura do §4 refeita das saídas; doc 57t: blocos iguais aos gerados, decisões antes dos resultados.
- Casos SINTÉTICOS em memória (rotulados "sintético"; nada é gravado): direção da aparagem de Lee com o lado de cima
  e com o lado de baixo aparado, q = 0 e versão com a reta.
"""

from __future__ import annotations

import importlib.util
import re
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "rdd_bolsa"
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "46_selecao_tipo_vaga.py"
DOC = ROOT / "docs" / "06_execucao" / "57t_resultados_selecao_tipo_vaga.md"
ADENDO = ROOT / "docs" / "06_execucao" / "48f_adendo_selecao_tipo_de_vaga.md"


def _mod(nome: str, caminho: Path):
    if nome in sys.modules:
        return sys.modules[nome]
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    return mod


SV = _mod("sv46_teste", SCRIPT)
EST, BAL, RES = SV.ler_saidas()
LEE = EST[EST["tipo_linha"] == "limites_lee"]


class TestEsquemaENatureza(unittest.TestCase):
    def test_colunas(self):
        self.assertEqual(list(EST.columns), SV.COLUNAS)
        self.assertEqual(list(BAL.columns), SV.COLUNAS_BAL)

    def test_natureza_e_estatuto(self):
        for df in (EST, BAL):
            self.assertEqual(set(df["natureza_dos_dados"]), {"EMPIRICO"})
            self.assertEqual(set(df["estatuto"]), {"ADENDO_48F_POS_RESULTADO"})
        self.assertEqual(RES["natureza_dos_dados"], "EMPIRICO")
        self.assertEqual(RES["estatuto"], "ADENDO_48F_POS_RESULTADO")

    def test_linhas_do_adendo(self):
        self.assertFalse(EST["id_linha"].duplicated().any())
        self.assertEqual(set(EST["status"]), {"EXECUTADO"})
        # SV-1: S e célula por corte; SV-3/4/5: Y1 e Y2 por corte, combinado e 3 ciclos.
        self.assertEqual(len(EST[(EST["linha"] == "SV-1") & (EST["tipo_linha"] == "salto")]), 4)
        for lid in ("SV-3", "SV-4", "SV-5"):
            self.assertEqual(len(LEE[LEE["linha"] == lid]), 4, lid)
            self.assertEqual(len(EST[(EST["linha"] == lid) & (EST["tipo_linha"] == "limites_lee_ciclo")]), 12, lid)
        self.assertEqual(len(BAL), 2 * 2 * len(SV.VARS_BAL))

    def test_figuras_com_como_ler(self):
        self.assertEqual(len(RES["figuras"]), 2)
        for f in RES["figuras"]:
            self.assertTrue((ROOT / f["arquivo"]).exists(), f["arquivo"])
            self.assertTrue(f["como_ler"].startswith("Como ler"))


class TestIntegridade(unittest.TestCase):
    def setUp(self):
        self.src = SCRIPT.read_text(encoding="utf-8")

    def test_ivs_oficial_e_dados(self):
        self.assertNotIn("ivs_ipea_2010_municipios", self.src)
        self.assertNotIn("malha_municipios_regioes_saude", self.src)
        for x in RES["entradas"]:
            self.assertNotIn("ivs_ipea_2010_municipios", x["arquivo"])
        self.assertIn("output/aquisicao/a08_ivs_2010_oficial_municipio.csv", [x["arquivo"] for x in RES["entradas"]])
        for v in RES["saidas"].values():
            self.assertTrue(v.startswith("output/") or v.startswith("docs/"), v)
        self.assertNotRegex(self.src, r"\"data\"[^\n]*(write|to_csv|to_parquet)")

    def test_sem_competencia_202609(self):
        self.assertEqual(SV.T44.LIMITE_CNES, "202609")
        self.assertTrue(all(c < "202609" for c in SV.T44.COMP_PRE))

    def test_nao_regrava_hi_cl_dq(self):
        for pref in ("HI_", "CL_", "DQ_"):
            self.assertNotRegex(self.src, rf"OUT / \"{pref}[^\"]*\"\)?\.write|to_csv\([^)]*{pref}")
        self.assertEqual(RES["integridade"]["saidas_nao_regravadas"], ["HI_*", "CL_*", "DQ_*"])

    def test_adendo_congelado(self):
        self.assertEqual(SV.sha256(ADENDO), SV.SHA_ADENDO)
        self.assertEqual(RES["adendo"]["sha256"], SV.SHA_ADENDO)

    def test_parametros(self):
        p = RES["parametros"]
        self.assertEqual((p["n_bootstrap"], p["semente"], p["h"], p["janela_sv4"]), (1999, 20261026, 0.05, 0.02))


class TestPortao(unittest.TestCase):
    def test_hi(self):
        p = RES["portao"]["hi"]
        self.assertTrue(p["aprovado"])
        self.assertLessEqual(p["max_abs_dif"], 1e-8)
        hi = pd.read_csv(OUT / "HI_estimativas.csv", dtype={"corte": str})
        for x in p["linhas"]:
            ref = hi[(hi["linha"] == x["linha"]) & (hi["outcome"] == x["linha"]) & (hi["variante"] == "principal")
                     & (hi["corte"] == x["corte"])]
            self.assertAlmostEqual(float(ref["tau"].iloc[0]), x["tau_44"], delta=1e-8)

    def test_db(self):
        p = RES["portao"]["db"]
        self.assertTrue(p["aprovado"])
        self.assertEqual(len(p["linhas"]), 16)
        dq = pd.read_csv(OUT / "DQ_estimativas.csv", dtype={"corte": str, "ciclo": str}, low_memory=False)
        for x in p["linhas"]:
            ref = dq[(dq["explicacao"] == "D-b") & (dq["bloco"] == "composicao") & (dq["quantidade"] == x["quantidade"])
                     & (dq["ciclo"] == x["ciclo"]) & (dq["corte"] == x["corte"])].iloc[0]
            self.assertAlmostEqual(float(ref["tau"]), x["c2_19mar"]["tau"], delta=1e-8)
            self.assertAlmostEqual(float(ref["media_abaixo"]), x["c2_19mar"]["media_abaixo"], delta=1e-8)
            # Ciclos 1 e 3 não dependem do quadro do ciclo 2.
            if x["ciclo"] in ("1", "3"):
                self.assertAlmostEqual(x["c2_19mar"]["tau"], x["c2_13fev"]["tau"], delta=1e-12)

    def test_sv2_entre_s1_e_o_cl0(self):
        s1 = BAL[BAL["amostra"].str.startswith("S=1")]
        self.assertEqual(set(s1["confere_cl0"]), {"sim"})
        cl = pd.read_csv(OUT / "CL_balanco.csv", dtype={"corte": str})
        cl0 = cl[(cl["bloco"] == "CL-0") & (cl["populacao"] == "H1 (municipio x ciclo, amostra da HI-2)")]
        for _, r in s1.iterrows():
            ref = cl0[(cl0["corte"] == r["corte"]) & (cl0["variavel"] == r["variavel"])].iloc[0]
            self.assertAlmostEqual(float(ref["tau"]), float(r["tau"]), delta=1e-8)


class TestLimitesGravados(unittest.TestCase):
    def test_ordem_e_ic(self):
        for _, r in LEE.iterrows():
            self.assertLessEqual(r["limite_inf"], r["dif_sem_aparo"] + 1e-12)
            self.assertLessEqual(r["dif_sem_aparo"], r["limite_sup"] + 1e-12)
            self.assertLessEqual(r["ic_im_inf"], r["limite_inf"])
            self.assertGreaterEqual(r["ic_im_sup"], r["limite_sup"])
            lo, hi = SV.T24.ic_imbens_manski(r["limite_inf"], r["limite_sup"], r["ep_limite_inf"], r["ep_limite_sup"])
            self.assertAlmostEqual(lo, r["ic_im_inf"], delta=1e-10)
            self.assertAlmostEqual(hi, r["ic_im_sup"], delta=1e-10)
            self.assertEqual(int(r["n_reamostras"]), 1999)
            self.assertGreater(int(r["n_reamostras_validas"]), 1900)

    def test_combinacao_dos_ciclos(self):
        cic = EST[EST["tipo_linha"] == "limites_lee_ciclo"]
        for _, r in LEE.iterrows():
            sub = cic[(cic["linha"] == r["linha"]) & (cic["outcome"] == r["outcome"]) & (cic["corte"] == r["corte"])]
            self.assertAlmostEqual(sub["peso_ciclo"].sum(), 1.0, delta=1e-12)
            for col, tot in (("limite_inf", "limite_inf"), ("limite_sup", "limite_sup"),
                             ("dif_sem_aparo", "dif_sem_aparo")):
                self.assertAlmostEqual(float((sub["peso_ciclo"] * sub[col]).sum()), float(r[tot]), delta=1e-12)
            for _, c in sub.iterrows():
                pmax, pmin = max(c["p_acima"], c["p_abaixo"]), min(c["p_acima"], c["p_abaixo"])
                self.assertAlmostEqual(c["q"], (pmax - pmin) / pmax, delta=1e-12)
                self.assertEqual(c["lado_aparado"], "acima" if c["p_acima"] > c["p_abaixo"] else "abaixo")

    def test_leitura_refeita(self):
        le = SV.leituras(EST, BAL)
        self.assertEqual(le, RES["leitura"])
        for ct, x in le["sv1"].items():
            s = EST[(EST["linha"] == "SV-1") & (EST["outcome"] == "S") & (EST["corte"] == ct)].iloc[0]
            t = EST[(EST["linha"] == "SV-1") & (EST["tipo_linha"] == "taxa_selecao") & (EST["ciclo"] == "1+2+3")
                    & (EST["corte"] == ct)].iloc[0]
            if not (s["ic95_inf"] <= 0 <= s["ic95_sup"]):
                self.assertEqual(x["codigo"], "TIPO_RESPONDE_AO_CORTE")
            else:
                self.assertEqual(x["codigo"], "SELECAO_PEQUENA" if t["q"] < 0.05 else "IC_CONTEM_ZERO_MAS_TAXAS_DIFEREM")


class TestRecalculoDoPonto(unittest.TestCase):
    """SV-3 (sem bootstrap) refeito das bases com uma aparagem escrita aqui (ordem por y, empates proporcionais)."""

    @classmethod
    def setUpClass(cls):
        cls.dados = SV.carregar()

    @staticmethod
    def _media_aparada(y, w, q, de_cima):
        alvo, mult = q * w.sum(), np.ones(len(y))
        acum = 0.0
        for v in (sorted(set(y), reverse=True) if de_cima else sorted(set(y))):
            if acum >= alvo:
                break
            m = y == v
            wv = w[m].sum()
            mult[m] = 1 - min(alvo - acum, wv) / wv
            acum += wv
        return float(np.sum(w * mult * y) / np.sum(w * mult))

    def test_sv3(self):
        for c in SV.CORTES:
            for oid, spec in SV.OUTCOMES.items():
                infs, sups, ns = [], [], []
                for k in SV.CICLOS:
                    d = self.dados["MK"][k]
                    x = d["s_mil"].to_numpy(float) - c
                    w = np.where(np.abs(x) < 50, 1 - np.abs(x) / 50, 0.0)
                    s = (d["n_cel_imed"] > 0).to_numpy(float)
                    y = d[spec["col"]].to_numpy(float)
                    ac = x > 0
                    pa = np.sum(w[ac] * s[ac]) / np.sum(w[ac])
                    pb = np.sum(w[~ac] * s[~ac]) / np.sum(w[~ac])
                    sa, sb = ac & (s == 1) & (w > 0), ~ac & (s == 1) & (w > 0)
                    ma = np.sum(w[sa] * y[sa]) / np.sum(w[sa])
                    mb = np.sum(w[sb] * y[sb]) / np.sum(w[sb])
                    if pa > pb:
                        q = (pa - pb) / pa
                        lo = self._media_aparada(y[sa], w[sa], q, True) - mb
                        hi = self._media_aparada(y[sa], w[sa], q, False) - mb
                    else:
                        q = (pb - pa) / pb
                        lo = ma - self._media_aparada(y[sb], w[sb], q, False)
                        hi = ma - self._media_aparada(y[sb], w[sb], q, True)
                    infs.append(lo)
                    sups.append(hi)
                    ns.append(int((sa | sb).sum()))
                p = np.array(ns) / sum(ns)
                r = LEE[(LEE["linha"] == "SV-3") & (LEE["outcome"] == oid) & (LEE["corte"] == SV.ROT_CORTE[c])].iloc[0]
                self.assertAlmostEqual(float(p @ np.array(infs)), r["limite_inf"], delta=1e-10)
                self.assertAlmostEqual(float(p @ np.array(sups)), r["limite_sup"], delta=1e-10)

    def test_y_ausente_quando_s0(self):
        for k, d in self.dados["MK"].items():
            s0 = d["S"] == 0
            for spec in SV.OUTCOMES.values():
                self.assertTrue(d.loc[s0, spec["col"]].isna().all(), k)
                self.assertTrue(d.loc[~s0, spec["col"]].notna().all(), k)


class TestSinteticoDirecaoDaAparagem(unittest.TestCase):
    """SINTÉTICO, só em memória (nada é gravado): direção da aparagem de Lee nos dois casos do §3, passo 2."""

    def test_sintetico_lado_de_cima_aparado(self):
        # Acima: 4 unidades, todas selecionadas (p = 1), y = 1, 2, 3, 4. Abaixo: 4 unidades, 2 selecionadas (p = 0,5),
        # y = 0. q = 0,5 no lado de cima: inferior tira as de MAIOR y (fica 1, 2), superior as de MENOR y (fica 3, 4).
        x = np.array([1, 2, 3, 4, -1, -2, -3, -4], float)
        acima = x > 0
        w = np.ones(8)
        s = np.array([1, 1, 1, 1, 1, 1, 0, 0], float)
        y = np.array([1, 2, 3, 4, 0, 0, np.nan, np.nan])
        r = SV.limites_lee_ciclo(x, acima, w, s, y)
        self.assertEqual(r["lado"], "acima")
        self.assertAlmostEqual(r["q"], 0.5)
        self.assertAlmostEqual(r["inf"], 1.5)
        self.assertAlmostEqual(r["sup"], 3.5)
        self.assertAlmostEqual(r["sem_aparo"], 2.5)

    def test_sintetico_lado_de_baixo_aparado(self):
        # Abaixo: todas selecionadas, y = 1, 2, 3, 4; acima: metade selecionada, y = 10. Salto = acima − abaixo.
        # Inferior tira as de MENOR y de baixo (fica 3, 4: média 3,5 -> 10 − 3,5); superior as de MAIOR y (fica 1, 2).
        x = np.array([1, 2, 3, 4, -1, -2, -3, -4], float)
        acima = x > 0
        w = np.ones(8)
        s = np.array([1, 1, 0, 0, 1, 1, 1, 1], float)
        y = np.array([10, 10, np.nan, np.nan, 1, 2, 3, 4])
        r = SV.limites_lee_ciclo(x, acima, w, s, y)
        self.assertEqual(r["lado"], "abaixo")
        self.assertAlmostEqual(r["q"], 0.5)
        self.assertAlmostEqual(r["inf"], 10 - 3.5)
        self.assertAlmostEqual(r["sup"], 10 - 1.5)
        self.assertLess(r["inf"], r["sup"])

    def test_sintetico_aparo_fracionario_e_pesos(self):
        # q = 0,25 de 4 unidades de peso igual: sai uma unidade inteira; com pesos, sai massa, não contagem.
        x = np.array([1, 2, 3, 4, -1, -2, -3, -4], float)
        acima = x > 0
        s = np.array([1, 1, 1, 1, 1, 1, 1, 0], float)
        y = np.array([1, 2, 3, 4, 0, 0, 0, np.nan])
        r = SV.limites_lee_ciclo(x, acima, np.ones(8), s, y)
        self.assertAlmostEqual(r["q"], 0.25)
        self.assertAlmostEqual(r["inf"], 2.0)
        self.assertAlmostEqual(r["sup"], 3.0)

    def test_sintetico_q_zero_sem_aparo(self):
        x = np.array([1, 2, -1, -2], float)
        r = SV.limites_lee_ciclo(x, x > 0, np.ones(4), np.ones(4), np.array([5.0, 7.0, 1.0, 3.0]))
        self.assertEqual(r["lado"], "nenhum")
        self.assertEqual(r["q"], 0.0)
        self.assertEqual(r["inf"], r["sup"])
        self.assertAlmostEqual(r["sem_aparo"], 4.0)

    def test_sintetico_com_a_reta(self):
        # y = 2 + 0,001 x acima e y = 0 + 0,001 x abaixo, sem ruído: o salto da reta é 2 e os resíduos são zero,
        # então os dois limites são 2 qualquer que seja q.
        x = np.array([5, 10, 20, 30, -5, -10, -20, -30], float)
        acima = x > 0
        y = np.where(acima, 2.0, 0.0) + x / 1000.0
        s = np.array([1, 1, 1, 1, 1, 1, 0, 1], float)
        y = np.where(s == 1, y, np.nan)
        r = SV.limites_lee_ciclo(x, acima, np.ones(8), s, y, reta=True)
        self.assertAlmostEqual(r["inf"], 2.0, places=10)
        self.assertAlmostEqual(r["sup"], 2.0, places=10)
        # Sem a reta, a diferença de médias mistura a inclinação.
        r0 = SV.limites_lee_ciclo(x, acima, np.ones(8), s, y, reta=False)
        self.assertNotAlmostEqual(r0["sem_aparo"], 2.0, places=3)

    def test_sintetico_ciclo_sem_selecionado_fica_fora(self):
        x = np.array([1, 2, -1, -2], float)
        self.assertIsNone(SV.limites_lee_ciclo(x, x > 0, np.ones(4), np.array([1, 1, 0, 0.0]),
                                               np.array([1, 2, np.nan, np.nan])))


class TestDoc(unittest.TestCase):
    def setUp(self):
        self.txt = DOC.read_text(encoding="utf-8")

    def test_blocos_iguais_aos_gerados(self):
        blocos = SV.gerar_blocos(EST, BAL, RES)
        achados = {m.group("nome"): m.group("corpo") for m in SV.MARCA.finditer(self.txt)}
        self.assertEqual(set(achados), set(blocos))
        for nome, corpo in blocos.items():
            self.assertEqual(achados[nome].rstrip(), corpo.rstrip(), nome)

    def test_cabecalho_e_decisoes_antes(self):
        self.assertIn("ADENDO_48F_POS_RESULTADO", self.txt)
        self.assertIn("**Auditoria:** pendente", self.txt)
        i_dec = self.txt.index("## 0. Decisões de implementação")
        i_res = self.txt.index("<!-- SV:resposta_curta:inicio -->")
        self.assertLess(i_dec, i_res)
        self.assertIn("monotonicidade", self.txt)

    def test_sem_numero_de_resultado_fora_dos_blocos(self):
        fora = SV.MARCA.sub("", self.txt)
        permitidos = {"0,050", "0,020", "0,300", "0,400", "0,05", "0,95", "0,25", "1,96", "1e−8"}
        for n in re.findall(r"[−+-]?\d+,\d+|\d+e[−-]\d+", fora):
            self.assertIn(n.lstrip("+"), permitidos, n)

    def test_linguagem(self):
        for proibida in ("a bolsa reduz", "a bolsa aumenta", "causa"):
            self.assertNotIn(proibida, self.txt.lower())
        self.assertIn("pacote do corte", self.txt)


if __name__ == "__main__":
    unittest.main()
