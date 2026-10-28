"""Testes do adendo 52g: `scripts/rdd_bolsa/53_VL1_por_ciclo.py`.

Partes:

1. `TestSintetico`: DADOS SINTÉTICOS gerados em memória, rotulados `SINTETICO_TESTE` e nunca gravados. Conferem as
   regras de leitura do §2 (por linha e geral), a concordância com o score bootstrap e o portão (iguais e fora da
   tolerância).
2. `TestPortaoReal`: o resumo registra o portão VG-R aprovado, e as linhas reproduzidas em `VG_estimativas.csv` batem
   com as de `VL_estimativas.csv`.
3. `TestNumeros`: rótulos e hashes; `VL_*` não regravados; razão de chances, IC, p, Holm e km recalculados das linhas e
   da covariância gravada; especificação igual à do VL-1 do 50, só com o ciclo trocado; contagens coerentes; leitura
   refeita; integridade.
4. `TestDoc57z`: o doc 57z é igual ao gerado, tem os marcadores e nenhum número de resultado fora dos blocos, e as
   decisões são as do pré-registro.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import re
import subprocess
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "53_VL1_por_ciclo.py"
_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location("VL1_por_ciclo_53", SCRIPT)
M = importlib.util.module_from_spec(_spec)
sys.modules["VL1_por_ciclo_53"] = M
_spec.loader.exec_module(M)
sys.dont_write_bytecode = _bytecode

OUT = ROOT / "output" / "rdd_bolsa"
CSV = OUT / "VG_estimativas.csv"
RESUMO = OUT / "VG_resumo.json"
VL_CSV = OUT / "VL_estimativas.csv"
DOC = ROOT / "docs" / "06_execucao" / "57z_VL1_por_ciclo.md"
ADENDO = ROOT / "docs" / "06_execucao" / "52g_adendo_VL1_por_ciclo.md"
NATUREZA_SINTETICA = "SINTETICO_TESTE"
TOL = 1e-8
B = M.B
Z95 = float(stats.norm.ppf(0.975))
BLOCOS = ("resposta", "portao", "identificacao", "principais", "km", "controles", "leitura", "decisoes")


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


def holm(p: np.ndarray) -> np.ndarray:
    """Holm escrito no teste."""
    p = np.asarray(p, dtype=float)
    o = np.argsort(p)
    m = len(p)
    adj = np.maximum.accumulate([(m - i) * p[j] for i, j in enumerate(o)])
    out = np.empty(m)
    out[o] = np.minimum(adj, 1.0)
    return out


def linha_sint(est: float, lo: float, hi: float, p_score: float = np.nan) -> pd.Series:
    return pd.Series({"natureza_dos_dados": NATUREZA_SINTETICA, "estimativa": est, "ic95_inf": lo, "ic95_sup": hi,
                      "p_score_rademacher": p_score, "status": "EXECUTADO"})


# ---------------------------------------------------------------------------
# 1. Sintético (só em memória)
# ---------------------------------------------------------------------------

class TestSintetico(unittest.TestCase):
    """Tudo aqui é sintético, gerado em memória e rotulado SINTETICO_TESTE."""

    def test_regra_linha(self) -> None:
        ref = linha_sint(1.6, 1.2, 2.1)
        self.assertEqual(M.regra_linha(linha_sint(1.3, 0.8, 2.0), ref), "IC_CONTEM_1")
        self.assertEqual(M.regra_linha(linha_sint(1.0, 1.0, 1.4), ref), "IC_CONTEM_1")
        self.assertEqual(M.regra_linha(linha_sint(1.5, 1.1, 2.0), ref), "EXCLUI_1_MESMO_SINAL")
        self.assertEqual(M.regra_linha(linha_sint(0.6, 0.4, 0.9), ref), "EXCLUI_1_SINAL_OPOSTO")
        self.assertEqual(M.regra_linha(linha_sint(np.nan, np.nan, np.nan), ref), "SEM_ESTIMATIVA")

    def test_score_concorda(self) -> None:
        self.assertTrue(M.score_concorda(linha_sint(1.5, 1.1, 2.0, 0.01)))
        self.assertFalse(M.score_concorda(linha_sint(1.5, 1.1, 2.0, 0.2)))
        self.assertFalse(M.score_concorda(linha_sint(1.3, 0.8, 2.0, 0.01)))
        self.assertTrue(M.score_concorda(linha_sint(1.3, 0.8, 2.0, 0.3)))
        self.assertIsNone(M.score_concorda(linha_sint(1.3, 0.8, 2.0)))

    def _est(self, vg1: tuple, vg3: tuple) -> pd.DataFrame:
        linhas = []
        for chave, (e, lo, hi) in (("VL1_c2", (1.6, 1.2, 2.1)), ("VG1", vg1), ("VG3", vg3)):
            linhas.append({"natureza_dos_dados": NATUREZA_SINTETICA, "chave_modelo": chave,
                           "tipo_linha": "razao_chances_por_5mil", "termo": B, "estimativa": e, "ic95_inf": lo,
                           "ic95_sup": hi, "p_score_rademacher": 0.5, "g_conjuntos": 10, "status": "EXECUTADO"})
            b = math.log(e) / 5
            linhas.append({"natureza_dos_dados": NATUREZA_SINTETICA, "chave_modelo": chave, "tipo_linha": "coeficiente",
                           "termo": B, "estimativa": b, "ic95_inf": math.log(lo) / 5, "ic95_sup": math.log(hi) / 5})
            linhas.append({"natureza_dos_dados": NATUREZA_SINTETICA, "chave_modelo": chave,
                           "tipo_linha": "km_equivalentes", "termo": "K5", "estimativa": 100.0})
        return pd.DataFrame(linhas)

    def test_leitura_geral(self) -> None:
        self.assertEqual(M.leitura(self._est((1.2, 0.8, 1.8), (1.1, 0.7, 1.7)))["geral"], "FORTE_SO_NO_CICLO_2")
        lei = M.leitura(self._est((1.5, 1.1, 2.0), (1.1, 0.7, 1.7)))
        self.assertEqual(lei["geral"], "APARECE_TAMBEM_EM_OUTRO_CICLO")
        self.assertEqual(lei["ciclos_que_excluem_1_mesmo_sinal"], ["1"])
        self.assertEqual(M.leitura(self._est((1.5, 1.1, 2.0), (0.6, 0.4, 0.9)))["geral"], "DEPENDE_DA_COMPOSICAO")
        self.assertTrue(M.leitura(self._est((1.2, 0.8, 1.8), (1.1, 0.7, 1.7)))["VG4"]["VG1"]["ic_beta_contem_0"])

    def test_portao_sintetico(self) -> None:
        """Portão com linhas sintéticas: iguais passam; 2e−8 fora falha."""
        def linhas(delta: float) -> pd.DataFrame:
            out = []
            for chave in M.REPRODUZIDAS:
                out.append({"natureza_dos_dados": NATUREZA_SINTETICA, "chave_modelo": chave,
                            "tipo_linha": "coeficiente", "termo": B, "estimativa": 0.1 + delta,
                            **{c: 0.05 for c in M.COLS_COEF[1:]}})
                out.append({"natureza_dos_dados": NATUREZA_SINTETICA, "chave_modelo": chave,
                            "tipo_linha": "razao_chances_por_5mil", "termo": B,
                            **{c: 0.3 for c in M.COLS_RC}, "g_conjuntos": 10, "g_candidatos": 50,
                            "n_candidatos": 50})
                for k in ("K5", "K10"):
                    out.append({"natureza_dos_dados": NATUREZA_SINTETICA, "chave_modelo": chave,
                                "tipo_linha": "km_equivalentes", "termo": k, **{c: 120.0 for c in M.COLS_KM}})
            return pd.DataFrame(out)

        sb = {"g": 10, "t_score": 1.0, "p_rademacher": 0.3, "p_webb": 0.3, "n_rademacher": 1024, "n_webb": 9,
              "metodo_rademacher": "x", "metodo_webb": "y"}
        res = {k: {"ok": True, "score_bootstrap": sb} for k in M.REPRODUZIDAS}
        idt = {k: {"identificacao": {"pares_no_modelo": 3}} for k in M.REPRODUZIDAS}
        vl_resumo = {"identificacao": idt, "score_bootstrap": {k: sb for k in M.REPRODUZIDAS}}
        self.assertEqual(M.portao(linhas(0.0), linhas(0.0), res, idt, vl_resumo)["status"], "PASSOU")
        self.assertEqual(M.portao(linhas(2e-8), linhas(0.0), res, idt, vl_resumo)["status"],
                         "FALHA_REPRODUCAO_VL1_c2")
        idt2 = {k: {"identificacao": {"pares_no_modelo": 4}} for k in M.REPRODUZIDAS}
        self.assertEqual(M.portao(linhas(0.0), linhas(0.0), res, idt2, vl_resumo)["status"],
                         "FALHA_REPRODUCAO_VL1_c2")

    def test_holm_do_teste_igual_ao_da_lib(self) -> None:
        p = np.array([0.04, 0.01])
        np.testing.assert_allclose(M.L.holm(p), holm(p))


# ---------------------------------------------------------------------------
# 2. Portão real
# ---------------------------------------------------------------------------

class TestPortaoReal(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.est = ler_csv(CSV)
        cls.vl = ler_csv(VL_CSV)
        cls.resumo = json.loads(RESUMO.read_text(encoding="utf-8"))

    def test_resumo_registra_portao_aprovado(self) -> None:
        p = self.resumo["portao"]
        self.assertEqual(p["status"], "PASSOU")
        self.assertEqual(p["tolerancia"], TOL)
        self.assertEqual([x["linha"] for x in p["linhas"]], ["VL1_c2", "VL1_emp"])
        for linha in p["linhas"]:
            self.assertTrue(linha["passou"], linha)
            self.assertTrue(linha["casou"], linha)
            self.assertTrue(linha["identificacao_igual"], linha)
            self.assertTrue(linha["metodo_score_igual"], linha)
            for k, v in linha.items():
                if k.startswith("dif_max_"):
                    self.assertLessEqual(v, TOL, (linha["linha"], k))

    def test_reproduzidas_iguais_ao_vl(self) -> None:
        for chave in ("VL1_c2", "VL1_emp"):
            for tipo, cols in (("coeficiente", ["estimativa", "ep_cluster_conjunto", "ic95_inf", "ic95_sup", "p"]),
                               ("razao_chances_por_5mil", ["estimativa", "ic95_inf", "ic95_sup", "p",
                                                           "p_score_rademacher", "p_score_webb", "g_conjuntos"]),
                               ("km_equivalentes", ["estimativa", "ic95_inf", "ic95_sup"])):
                a = self.est[(self.est["chave_modelo"] == chave) & (self.est["tipo_linha"] == tipo)]
                g = self.vl[(self.vl["chave_modelo"] == chave) & (self.vl["tipo_linha"] == tipo)]
                self.assertEqual(list(a["termo"]), list(g["termo"]), (chave, tipo))
                for c in cols:
                    self.assertLessEqual(dif_rel(a[c], g[c]), TOL, (chave, tipo, c))

    def test_identificacao_reproduzida_igual_ao_vl(self) -> None:
        vl = json.loads((OUT / "VL_resumo.json").read_text(encoding="utf-8"))
        for chave in ("VL1_c2", "VL1_emp"):
            self.assertEqual(self.resumo["identificacao"][chave]["identificacao"],
                             vl["identificacao"][chave]["identificacao"])


# ---------------------------------------------------------------------------
# 3. Números
# ---------------------------------------------------------------------------

class TestNumeros(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.est = ler_csv(CSV)
        cls.resumo = json.loads(RESUMO.read_text(encoding="utf-8"))

    def _sel(self, chave: str, tipo: str, termo: str | None = None) -> pd.Series:
        s = self.est[(self.est["chave_modelo"] == chave) & (self.est["tipo_linha"] == tipo)]
        if termo is not None:
            s = s[s["termo"] == termo]
        self.assertEqual(len(s), 1, (chave, tipo, termo))
        return s.iloc[0]

    def test_rotulos(self) -> None:
        self.assertTrue((self.est["natureza_dos_dados"] == "EMPIRICO").all())
        self.assertTrue((self.est["estatuto"] == "ADENDO_52G_POS_RESULTADO").all())
        self.assertEqual(self.resumo["natureza_dos_dados"], "EMPIRICO")
        self.assertEqual(self.resumo["estatuto"], "ADENDO_52G_POS_RESULTADO")
        self.assertEqual(set(self.est["chave_modelo"]), {"VG1", "VG3", "VL1_c2", "VL1_emp"})
        self.assertEqual(set(self.est.loc[self.est["chave_modelo"] == "VG1", "ciclo"]), {"1"})
        self.assertEqual(set(self.est.loc[self.est["chave_modelo"] == "VG3", "ciclo"]), {"3"})

    def test_hashes(self) -> None:
        self.assertEqual(self.resumo["adendo"]["sha256"], sha256(ADENDO))
        self.assertEqual(self.resumo["adendo"]["commit_de_congelamento"], "e9740a5")
        for caminho, h in self.resumo["saidas"].items():
            self.assertEqual(sha256(ROOT / caminho), h, caminho)
        for e in self.resumo["entradas"]:
            self.assertEqual(sha256(ROOT / e["caminho"]), e["sha256"], e["caminho"])

    def test_vl_nao_regravado(self) -> None:
        for caminho, h in self.resumo["vl_nao_regravado"].items():
            self.assertEqual(sha256(ROOT / caminho), h, caminho)
        vl = json.loads((OUT / "VL_resumo.json").read_text(encoding="utf-8"))
        self.assertEqual(vl["saidas"]["output/rdd_bolsa/VL_estimativas.csv"], sha256(VL_CSV))

    def test_especificacao_e_a_do_VL1_com_outro_ciclo(self) -> None:
        for chave, ciclo in (("VG1", "1"), ("VG3", "3")):
            e = M.ESPECS[chave]
            self.assertEqual(e["ciclo"], ciclo)
            for k in ("ef", "janela", "dist"):
                self.assertEqual(e[k], M.VL.ESPECS["VL1_c2"][k], k)
            termos = self.resumo["convergencia"][chave]["termos_sem_efeito_fixo"]
            self.assertNotIn("mesma_uf", termos)
            self.assertFalse(any(t.startswith("macro_") for t in termos))
            self.assertIn(B, termos)
            self.assertIn(M.DIST, termos)
            self.assertGreater(self.resumo["convergencia"][chave]["n_efeitos_fixos"], 0)

    def test_razao_de_chances_e_ic(self) -> None:
        for chave in M.ORDEM:
            b = self._sel(chave, "coeficiente", B)
            r = self._sel(chave, "razao_chances_por_5mil")
            self.assertAlmostEqual(r["estimativa"], math.exp(5 * b["estimativa"]), delta=1e-8 * r["estimativa"])
            e = b["ep_cluster_conjunto"]
            self.assertAlmostEqual(r["ic95_inf"], math.exp(5 * (b["estimativa"] - Z95 * e)), delta=1e-8)
            self.assertAlmostEqual(r["ic95_sup"], math.exp(5 * (b["estimativa"] + Z95 * e)), delta=1e-8)
            self.assertAlmostEqual(r["p"], 2 * stats.norm.sf(abs(b["estimativa"] / e)), delta=1e-9)
            self.assertAlmostEqual(r["p_t_g_menos_1"], 2 * stats.t.sf(abs(b["estimativa"] / e), r["g_conjuntos"] - 1),
                                   delta=1e-9)
            self.assertGreater(r["g_conjuntos"], 1)
            self.assertTrue(pd.notna(r["p_score_rademacher"]), chave)

    def test_score_bootstrap(self) -> None:
        for chave in M.ORDEM:
            sb = self.resumo["score_bootstrap"][chave]
            self.assertEqual(sb["status"], "EXECUTADO")
            r = self._sel(chave, "razao_chances_por_5mil")
            self.assertEqual(sb["g"], r["g_conjuntos"])
            self.assertLessEqual(dif_rel([sb["p_rademacher"]], [r["p_score_rademacher"]]), TOL)
            if sb["g"] <= 24:
                self.assertEqual(sb["n_rademacher"], 2 ** sb["g"])
                self.assertIn("enumeração completa", sb["metodo_rademacher"])

    def test_holm(self) -> None:
        h = self.est[self.est["entra_holm"]]
        self.assertEqual(set(h["chave_modelo"]), {"VG1", "VG3"})
        self.assertTrue((h["tipo_linha"] == "razao_chances_por_5mil").all())
        np.testing.assert_allclose(h["p_holm"], holm(h["p"].to_numpy()), rtol=1e-8)
        np.testing.assert_allclose(h["p_holm_score_rademacher"], holm(h["p_score_rademacher"].to_numpy()), rtol=1e-8)

    def test_km_da_covariancia(self) -> None:
        for chave in M.NOVAS:
            c = self.resumo["covariancias"][chave]
            i, j = c["termos"].index(B), c["termos"].index(M.DIST)
            b, g = c["theta"][i], c["theta"][j]
            for comp, passo in (("K5", 5.0), ("K10", 10.0)):
                k = self._sel(chave, "km_equivalentes", comp)
                self.assertAlmostEqual(k["estimativa"], 100 * passo * b / (-g), delta=1e-8 * max(1, abs(k["estimativa"])))
                V = np.array(c["V_cluster_conjunto"])
                grad = np.zeros(len(c["termos"]))
                grad[i] = 100 * passo / (-g)
                grad[j] = 100 * passo * b / g ** 2
                ep = math.sqrt(grad @ V @ grad)
                self.assertAlmostEqual(k["ep_cluster_conjunto"], ep, delta=1e-6 * max(1, ep))

    def test_contagens_de_identificacao(self) -> None:
        for chave in M.ORDEM:
            d = self.resumo["identificacao"][chave]["identificacao"]
            r = self._sel(chave, "razao_chances_por_5mil")
            self.assertEqual(d["candidatos_no_modelo"], r["n_candidatos"])
            self.assertEqual(d["alternativas_no_modelo"], r["n_linhas_candidato_celula"])
            self.assertEqual(d["pares_no_modelo"], d["pares_com_variacao_de_bolsa"] + d["pares_sem_variacao_de_bolsa"])
            self.assertLessEqual(d["candidatos_com_1a_opcao_em_par_com_variacao"],
                                 d["candidatos_com_variacao_de_bolsa_em_algum_par"])
            self.assertEqual(d["candidatos_no_desenho"] - d["candidatos_retirados_uma_so_alternativa"],
                             d["candidatos_no_modelo"])
        soma = sum(self.resumo["identificacao"][k]["identificacao"]["candidatos_no_desenho"] for k in
                   ("VG1", "VL1_c2", "VG3"))
        self.assertEqual(soma, self.resumo["identificacao"]["VL1_emp"]["identificacao"]["candidatos_no_desenho"])

    def test_leitura_refeita(self) -> None:
        self.assertEqual(json.loads(json.dumps(M.leitura(self.est))), self.resumo["leitura"])

    def test_integridade(self) -> None:
        texto = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("ivs_ipea_2010_municipios", texto)
        self.assertNotIn("to_csv(ROOT / \"data", texto)
        for c in ("nome", "cpf", "crm", "pseudonimo", "id_candidato"):
            self.assertNotIn(c, [x.lower() for x in self.est.columns])


# ---------------------------------------------------------------------------
# 4. Doc 57z
# ---------------------------------------------------------------------------

class TestDoc57z(unittest.TestCase):
    def test_doc_igual_ao_gerado(self) -> None:
        self.assertEqual(DOC.read_text(encoding="utf-8"), M.gerar_doc(M.ler_est(), M.ler_resumo()))

    def test_marcadores_e_secoes(self) -> None:
        t = DOC.read_text(encoding="utf-8")
        for nome in BLOCOS:
            self.assertEqual(t.count(f"<!-- VG:{nome}:inicio -->"), 1, nome)
            self.assertEqual(t.count(f"<!-- VG:{nome}:fim -->"), 1, nome)
        for s in ("## 1. Resposta curta", "## 2. Portão", "## 3. Quem identifica", "## 6. Decisões de "
                  "implementação", "## 7. Limites", "ADENDO_52G_POS_RESULTADO", "**Auditoria:** pendente"):
            self.assertIn(s, t)

    def test_nenhum_numero_de_resultado_fora_dos_blocos(self) -> None:
        t = DOC.read_text(encoding="utf-8")
        fora = re.sub(r"<!-- VG:(\w+):inicio -->.*?<!-- VG:\1:fim -->", "", t, flags=re.S)
        fora = "\n".join(x for x in fora.splitlines() if not x.startswith("#"))
        self.assertEqual(re.findall(r"\d+,\d+", fora), [])
        self.assertEqual(re.findall(r"\d+\.\d+", fora), [])

    def test_leitura_no_texto(self) -> None:
        t = DOC.read_text(encoding="utf-8")
        self.assertIn(f"`{M.ler_resumo()['leitura']['geral']}`", t)

    def test_linguagem(self) -> None:
        t = " ".join(DOC.read_text(encoding="utf-8").split())
        self.assertIn("preferência revelada, não efeito causal", t)
        self.assertIn("pacote do corte", t)
        self.assertIn("Não é efeito da participação no PMM-E", t)
        self.assertIn("Em linguagem simples", t)
        self.assertNotIn("a bolsa funciona", t.lower())

    def test_decisoes_iguais_as_do_pre_registro(self) -> None:
        t = DOC.read_text(encoding="utf-8")
        ini = t.index("<!-- VG:decisoes:inicio -->") + len("<!-- VG:decisoes:inicio -->\n")
        fim = t.index("\n<!-- VG:decisoes:fim -->")
        self.assertEqual(t[ini:fim], M.texto_decisoes())
        self.assertEqual(len(M.DECISOES), 10)
        self.assertTrue(all(d["data"] == "2026-10-28" for d in M.DECISOES))
        # O bloco do commit de pré-registro (primeiro commit que criou o 57z) é igual ao atual.
        try:
            h = subprocess.run(["git", "log", "--diff-filter=A", "--format=%H", "--", str(DOC.relative_to(ROOT))],
                               cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
        except (OSError, subprocess.CalledProcessError):
            self.skipTest("sem git")
        if not h:
            self.skipTest("57z ainda sem commit")
        antigo = subprocess.run(["git", "show", f"{h[-1]}:{DOC.relative_to(ROOT)}"], cwd=ROOT, capture_output=True,
                                text=True, check=True).stdout
        a_ini = antigo.index("<!-- VG:decisoes:inicio -->")
        a_fim = antigo.index("<!-- VG:decisoes:fim -->")
        self.assertEqual(antigo[a_ini:a_fim], t[t.index("<!-- VG:decisoes:inicio -->"):t.index("<!-- VG:decisoes:fim -->")])
        self.assertNotIn("<!-- VG:principais:inicio -->", antigo)


if __name__ == "__main__":
    unittest.main()
