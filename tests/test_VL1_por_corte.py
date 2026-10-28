"""Testes do adendo 52h: `scripts/rdd_bolsa/54_VL1_por_corte.py`.

Partes:

1. `TestSintetico`: DADOS SINTÉTICOS gerados em memória, rotulados `SINTETICO_TESTE` e nunca gravados. Conferem as
   regras de leitura do §4 (por degrau e por modelo, com a ordem da decisão 8), a concordância com o score bootstrap,
   a reparametrização do teste de igualdade e a contagem de quem identifica cada degrau.
2. `TestPortaoReal`: o resumo registra o portão VK-R aprovado, e as linhas reproduzidas batem com `VL_estimativas.csv`.
3. `TestNumeros`: rótulos e hashes; `VL_*` e `VG_*` não regravados; degraus conferidos contra a regra do IVS;
   especificação igual à do VL-1 com a bolsa trocada pelos degraus; razão de chances, IC, p, Wald e Holm recalculados
   da covariância gravada; contagens coerentes; leitura refeita; integridade.
4. `TestDoc57za`: o doc 57za é igual ao gerado, tem os marcadores e nenhum número de resultado fora dos blocos, e as
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
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "54_VL1_por_corte.py"
_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location("VL1_por_corte_54", SCRIPT)
M = importlib.util.module_from_spec(_spec)
sys.modules["VL1_por_corte_54"] = M
_spec.loader.exec_module(M)
sys.dont_write_bytecode = _bytecode

OUT = ROOT / "output" / "rdd_bolsa"
CSV = OUT / "VK_estimativas.csv"
RESUMO = OUT / "VK_resumo.json"
VL_CSV = OUT / "VL_estimativas.csv"
DOC = ROOT / "docs" / "06_execucao" / "57za_VL1_por_corte.md"
ADENDO = ROOT / "docs" / "06_execucao" / "52h_adendo_VL1_por_corte.md"
NATUREZA_SINTETICA = "SINTETICO_TESTE"
TOL = 1e-8
B, D300, D400, DIF = M.B, M.D300, M.D400, M.DIF
Z95 = float(stats.norm.ppf(0.975))
BLOCOS = ("resposta", "portao", "identificacao", "principais", "igualdade", "controles", "leitura", "decisoes")


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

    REF = linha_sint(1.5, 1.1, 1.9)

    def _m(self, d3: tuple, d4: tuple, rz: tuple) -> dict:
        return M.regra_modelo(linha_sint(*d3), linha_sint(*d4), linha_sint(*rz), self.REF)

    def test_regra_degrau(self) -> None:
        self.assertEqual(M.regra_degrau(linha_sint(1.3, 0.8, 2.0), self.REF), "CONTEM_1")
        self.assertEqual(M.regra_degrau(linha_sint(1.5, 1.1, 2.0), self.REF), "EXCLUI_1_MESMO_LADO")
        self.assertEqual(M.regra_degrau(linha_sint(0.6, 0.4, 0.9), self.REF), "EXCLUI_1_LADO_OPOSTO")
        self.assertEqual(M.regra_degrau(linha_sint(np.nan, np.nan, np.nan), self.REF), "SEM_ESTIMATIVA")

    def test_regra_modelo_linhas_do_adendo(self) -> None:
        # 1ª linha: os dois > 1, razão contém 1 (os dois excluem 1, ou nenhum).
        m = self._m((1.4, 1.1, 1.8), (1.5, 1.1, 2.0), (0.9, 0.6, 1.4))
        self.assertEqual(m["regra"], "VALE_NOS_DOIS_CORTES")
        self.assertFalse(m["nenhum_degrau_exclui_1"])
        m = self._m((1.2, 0.9, 1.6), (1.3, 0.9, 1.8), (0.9, 0.6, 1.4))
        self.assertEqual(m["regra"], "VALE_NOS_DOIS_CORTES")
        self.assertTrue(m["nenhum_degrau_exclui_1"])
        # 2ª linha vem antes da 1ª: um exclui 1, o outro contém, razão contém 1.
        m = self._m((1.6, 1.2, 2.1), (1.2, 0.9, 1.6), (1.3, 0.9, 1.9))
        self.assertEqual((m["regra"], m["corte"]), ("APARECE_NUM_CORTE", "0,300"))
        m = self._m((0.95, 0.7, 1.3), (1.6, 1.2, 2.1), (0.6, 0.35, 1.05))
        self.assertEqual((m["regra"], m["corte"]), ("APARECE_NUM_CORTE", "0,400"))
        # 3ª linha: razão exclui 1.
        m = self._m((2.0, 1.5, 2.6), (1.1, 0.9, 1.3), (1.8, 1.2, 2.7))
        self.assertEqual((m["regra"], m["corte"]), ("DIFERE_ENTRE_CORTES", "0,300"))
        # 4ª linha tem precedência.
        m = self._m((2.0, 1.5, 2.6), (0.6, 0.4, 0.9), (3.3, 2.0, 5.0))
        self.assertEqual((m["regra"], m["corte"]), ("SINAL_OPOSTO", ["0,400"]))
        # Fora da tabela: um abaixo de 1 sem excluir, outro contém.
        self.assertEqual(self._m((0.9, 0.6, 1.3), (1.1, 0.8, 1.5), (0.8, 0.5, 1.3))["regra"], "FORA_DA_TABELA")
        self.assertEqual(self._m((np.nan,) * 3, (1.1, 0.8, 1.5), (np.nan,) * 3)["regra"], "SEM_ESTIMATIVA")

    def test_score_concorda(self) -> None:
        self.assertTrue(M.score_concorda(linha_sint(1.5, 1.1, 2.0, 0.01)))
        self.assertFalse(M.score_concorda(linha_sint(1.5, 1.1, 2.0, 0.2)))
        self.assertFalse(M.score_concorda(linha_sint(1.3, 0.8, 2.0, 0.01)))
        self.assertIsNone(M.score_concorda(linha_sint(1.3, 0.8, 2.0)))

    def test_reparametrizacao_da_igualdade(self) -> None:
        """A utilidade não muda; o coeficiente da coluna D300 vira δ300 − δ400."""
        rng = np.random.default_rng(7)
        A = np.column_stack([rng.integers(0, 2, 50), rng.integers(0, 2, 50), rng.normal(size=50)]).astype(float)
        th = np.array([0.4, 0.1, -0.3])
        Ar = A.copy()
        Ar[:, 1] = A[:, 0] + A[:, 1]
        thr = th.copy()
        thr[0], thr[1] = th[0] - th[1], th[1]
        np.testing.assert_allclose(A @ th, Ar @ thr)
        self.assertAlmostEqual(thr[0], 0.3)

    def test_contagens_degraus_sinteticas(self) -> None:
        """Dois candidatos, dois pares: o 1º vê faixas 3 e 2 no par a; o 2º vê 3 e 1 no par b (mesmo conjunto)."""
        conj = pd.DataFrame({"faixa_anunciada": ["FAIXA 3", "FAIXA 2", "FAIXA 3", "FAIXA 1", "FAIXA 2"]})
        D = {"conj": conj, "cel": np.array([0, 1, 2, 3, 4]), "grp": np.array([0, 0, 1, 1, 1]),
             "starts": np.array([0, 2]), "esc": np.array([1, 3]),
             "grupos": pd.DataFrame({"cluster_conjunto": ["c1", "c1"]})}
        ef = {"par_lin": np.array(["SP|SP", "SP|SP", "RJ|RJ", "RJ|RJ", "RJ|MG"], dtype=object)}
        c = M.contagens_degraus(D, ef)
        self.assertEqual(c["dois_lados_0300"]["candidatos"], 2)
        self.assertEqual(c["vizinhas_0300"]["candidatos"], 1)
        self.assertEqual(c["dois_lados_0400"]["candidatos"], 1)
        self.assertEqual(c["vizinhas_0400"]["candidatos"], 0)
        self.assertEqual(c["dois_lados_0400"]["candidatos_com_1a_opcao_no_par"], 1)
        self.assertEqual(c["dois_lados_0300"]["pares"], 2)
        self.assertEqual(c["dois_lados_0300"]["conjuntos"], 1)
        self.assertEqual(c["pares_no_modelo"], 3)

    def test_holm_do_teste_igual_ao_da_lib(self) -> None:
        p = np.array([0.04, 0.01, 0.3, 0.02])
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
            self.assertTrue(linha["identificacao_igual"], linha)
            for k, v in linha.items():
                if k.startswith("dif_max_"):
                    self.assertLessEqual(v, TOL, (linha["linha"], k))

    def test_reproduzidas_iguais_ao_vl(self) -> None:
        for chave in ("VL1_c2", "VL1_emp"):
            a = self.est[(self.est["chave_modelo"] == chave) & (self.est["tipo_linha"] == "razao_chances_por_5mil")]
            g = self.vl[(self.vl["chave_modelo"] == chave) & (self.vl["tipo_linha"] == "razao_chances_por_5mil")]
            self.assertEqual(len(a), 1)
            for c in ("estimativa", "ic95_inf", "ic95_sup", "p", "p_score_rademacher", "g_conjuntos"):
                self.assertLessEqual(dif_rel(a[c], g[c]), TOL, (chave, c))

    def test_desenho_igual_ao_do_vl1(self) -> None:
        self.assertTrue(self.resumo["conferencias"]["desenho_igual_ao_VL1"])
        vl = json.loads((OUT / "VL_resumo.json").read_text(encoding="utf-8"))
        for chave, ref in (("VK1", "VL1_emp"), ("VK2", "VL1_c2")):
            self.assertEqual(self.resumo["identificacao"][chave]["identificacao"], vl["identificacao"][ref]["identificacao"])


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
        self.assertTrue((self.est["estatuto"] == "ADENDO_52H_POS_RESULTADO").all())
        self.assertEqual(self.resumo["natureza_dos_dados"], "EMPIRICO")
        self.assertEqual(self.resumo["estatuto"], "ADENDO_52H_POS_RESULTADO")
        self.assertEqual(set(self.est["chave_modelo"]), {"VK1", "VK2", "VK3", "VL1_c2", "VL1_emp"})
        self.assertEqual(set(self.est.loc[self.est["chave_modelo"] == "VK2", "ciclo"]), {"2"})

    def test_hashes(self) -> None:
        self.assertEqual(self.resumo["adendo"]["sha256"], sha256(ADENDO))
        self.assertEqual(self.resumo["adendo"]["commit_de_congelamento"], "2c8b964")
        for caminho, h in self.resumo["saidas"].items():
            self.assertEqual(sha256(ROOT / caminho), h, caminho)
        for e in self.resumo["entradas"]:
            self.assertEqual(sha256(ROOT / e["caminho"]), e["sha256"], e["caminho"])

    def test_vl_e_vg_nao_regravados(self) -> None:
        self.assertEqual(set(self.resumo["protegidos_nao_regravados"]),
                         {f"output/rdd_bolsa/{x}" for x in ("VL_estimativas.csv", "VL_resumo.json",
                                                             "VG_estimativas.csv", "VG_resumo.json")})
        for caminho, h in self.resumo["protegidos_nao_regravados"].items():
            self.assertEqual(sha256(ROOT / caminho), h, caminho)

    def test_degraus_conferidos(self) -> None:
        c = self.resumo["conferencias"]["degraus"]
        for k, v in c.items():
            if k.startswith("discordantes"):
                self.assertEqual(v, 0, k)
        f = c["celulas_por_faixa"]
        self.assertEqual(f["degrau_0400_sem_0300"], 0)
        self.assertEqual(f["ate_0300"] + f["0300_a_0400"] + f["acima_0400"], c["celulas"])
        self.assertTrue(all(f[k] > 0 for k in ("ate_0300", "0300_a_0400", "acima_0400")))

    def test_especificacao_e_a_do_VL1_com_degraus(self) -> None:
        for chave, base in (("VK1", "VL1_emp"), ("VK2", "VL1_c2"), ("VK3", "VL3_VL1_emp")):
            e = M.ESPECS[chave]
            for k in ("ciclo", "ef", "janela", "dist"):
                self.assertEqual(e[k], M.VL.ESPECS[base][k], (chave, k))
            termos = self.resumo["convergencia"][chave]["termos_sem_efeito_fixo"]
            ref = self.resumo["convergencia"].get(base, {}).get("termos_sem_efeito_fixo")
            self.assertNotIn(B, termos)
            self.assertIn(D300, termos)
            self.assertIn(D400, termos)
            self.assertNotIn("mesma_uf", termos)
            self.assertFalse(any(t.startswith("macro_") for t in termos))
            self.assertIn(M.DIST, termos)
            self.assertGreater(self.resumo["convergencia"][chave]["n_efeitos_fixos"], 0)
            if ref is not None:  # mesma ordem, com a bolsa trocada pelos dois degraus na mesma posição
                k = ref.index(B)
                self.assertEqual(termos, ref[:k] + [D300, D400] + ref[k + 1:])

    def test_razao_de_chances_e_igualdade_da_covariancia(self) -> None:
        for chave in M.NOVAS:
            c = self.resumo["covariancias"][chave]
            th = np.array(c["theta"])
            V = np.array(c["V_cluster_conjunto"])
            G = c["g_conjuntos"]
            for i, t in enumerate(c["termos"]):
                r = self._sel(chave, "razao_chances_degrau", t)
                e = math.sqrt(V[i, i])
                self.assertAlmostEqual(r["estimativa"], math.exp(th[i]), delta=1e-8 * r["estimativa"])
                self.assertAlmostEqual(r["ic95_inf"], math.exp(th[i] - Z95 * e), delta=1e-8)
                self.assertAlmostEqual(r["ic95_sup"], math.exp(th[i] + Z95 * e), delta=1e-8)
                self.assertAlmostEqual(r["p"], 2 * stats.norm.sf(abs(th[i] / e)), delta=1e-9)
                self.assertAlmostEqual(r["p_t_g_menos_1"], 2 * stats.t.sf(abs(th[i] / e), G - 1), delta=1e-9)
                b = self._sel(chave, "coeficiente", t)
                self.assertLessEqual(dif_rel([b["estimativa"]], [th[i]]), TOL)
            a = np.array([1.0, -1.0])
            d, ep = float(a @ th), math.sqrt(float(a @ V @ a))
            rz = self._sel(chave, "razao_razoes_chances", DIF)
            self.assertAlmostEqual(rz["estimativa"], math.exp(d), delta=1e-8 * rz["estimativa"])
            self.assertAlmostEqual(rz["ic95_inf"], math.exp(d - Z95 * ep), delta=1e-8)
            self.assertAlmostEqual(rz["ic95_sup"], math.exp(d + Z95 * ep), delta=1e-8)
            self.assertAlmostEqual(rz["p"], stats.chi2.sf((d / ep) ** 2, 1), delta=1e-9)

    def test_score_bootstrap(self) -> None:
        for chave in M.COM_SCORE:
            for t in (D300, D400, DIF):
                sb = self.resumo["score_bootstrap"][chave][t]
                self.assertEqual(sb["status"], "EXECUTADO", (chave, t))
                tipo = "razao_razoes_chances" if t == DIF else "razao_chances_degrau"
                r = self._sel(chave, tipo, t)
                self.assertEqual(sb["g"], r["g_conjuntos"])
                self.assertLessEqual(dif_rel([sb["p_rademacher"]], [r["p_score_rademacher"]]), TOL)
                if sb["g"] <= 24:
                    self.assertEqual(sb["n_rademacher"], 2 ** sb["g"])
        self.assertEqual(self.resumo["score_bootstrap"]["VK3"], {})

    def test_holm(self) -> None:
        h = self.est[self.est["entra_holm"]]
        self.assertEqual(len(h), 4)
        self.assertEqual(set(h["chave_modelo"]), {"VK1", "VK2"})
        self.assertEqual(set(h["termo"]), {D300, D400})
        self.assertTrue((h["tipo_linha"] == "razao_chances_degrau").all())
        np.testing.assert_allclose(h["p_holm"], holm(h["p"].to_numpy()), rtol=1e-8)
        np.testing.assert_allclose(h["p_holm_score_rademacher"], holm(h["p_score_rademacher"].to_numpy()), rtol=1e-8)

    def test_contagens_de_identificacao(self) -> None:
        for chave in M.NOVAS:
            d = self.resumo["identificacao"][chave]["degraus"]
            i = self.resumo["identificacao"][chave]["identificacao"]
            r = self._sel(chave, "razao_chances_degrau", D300)
            self.assertEqual(d["candidatos_no_modelo"], r["n_candidatos"])
            self.assertEqual(d["candidatos_no_modelo"], i["candidatos_no_modelo"])
            self.assertEqual(d["pares_no_modelo"], i["pares_no_modelo"])
            self.assertEqual(d["conjuntos_no_modelo"], r["g_conjuntos"])
            for corte in ("0300", "0400"):
                dois, viz = d[f"dois_lados_{corte}"], d[f"vizinhas_{corte}"]
                self.assertLessEqual(viz["candidatos"], dois["candidatos"])
                self.assertLessEqual(dois["candidatos_com_1a_opcao_no_par"], dois["candidatos"])
                self.assertLessEqual(dois["conjuntos"], d["conjuntos_no_modelo"])
                # Variação num degrau implica variação de bolsa no par (contagem do 50).
                self.assertLessEqual(dois["candidatos"], i["candidatos_com_variacao_de_bolsa_em_algum_par"])
            self.assertLessEqual(d["tres_faixas"]["candidatos"], d["vizinhas_0300"]["candidatos"])

    def test_leitura_refeita(self) -> None:
        self.assertEqual(json.loads(json.dumps(M.leitura(self.est))), self.resumo["leitura"])

    def test_integridade(self) -> None:
        texto = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("ivs_ipea_2010_municipios", texto)
        self.assertNotIn("to_csv(ROOT / \"data", texto)
        for c in ("nome", "cpf", "crm", "pseudonimo", "id_candidato"):
            self.assertNotIn(c, [x.lower() for x in self.est.columns])


# ---------------------------------------------------------------------------
# 4. Doc 57za
# ---------------------------------------------------------------------------

class TestDoc57za(unittest.TestCase):
    def test_doc_igual_ao_gerado(self) -> None:
        self.assertEqual(DOC.read_text(encoding="utf-8"), M.gerar_doc(M.ler_est(), M.ler_resumo()))

    def test_marcadores_e_secoes(self) -> None:
        t = DOC.read_text(encoding="utf-8")
        for nome in BLOCOS:
            self.assertEqual(t.count(f"<!-- VK:{nome}:inicio -->"), 1, nome)
            self.assertEqual(t.count(f"<!-- VK:{nome}:fim -->"), 1, nome)
        for s in ("## 1. Resposta curta", "## 2. Portão", "## 3. Quem identifica", "## 6. Decisões de "
                  "implementação", "## 7. Limites", "ADENDO_52H_POS_RESULTADO", "**Auditoria:** pendente"):
            self.assertIn(s, t)

    def test_nenhum_numero_de_resultado_fora_dos_blocos(self) -> None:
        t = DOC.read_text(encoding="utf-8")
        fora = re.sub(r"<!-- VK:(\w+):inicio -->.*?<!-- VK:\1:fim -->", "", t, flags=re.S)
        fora = "\n".join(x for x in fora.splitlines() if not x.startswith("#"))
        # Fora dos blocos, só os cortes do adendo (parâmetros, não resultado).
        self.assertEqual(sorted(set(re.findall(r"\d+,\d+", fora))), ["0,300", "0,400"])
        self.assertEqual(re.findall(r"\d+\.\d+", fora), [])

    def test_leitura_no_texto(self) -> None:
        t = DOC.read_text(encoding="utf-8")
        for g in M.ler_resumo()["leitura"]["geral"].values():
            self.assertIn(f"`{g}`", t)

    def test_linguagem(self) -> None:
        t = " ".join(DOC.read_text(encoding="utf-8").split())
        self.assertIn("preferência revelada, não efeito causal", t)
        self.assertIn("pacote do corte", t)
        self.assertIn("Não é efeito da participação no PMM-E", t)
        self.assertIn("não a ida ao município", t)
        self.assertIn("pós-resultado", t)
        self.assertIn("Em linguagem simples", t)
        self.assertNotIn("a bolsa funciona", t.lower())

    def test_decisoes_iguais_as_do_pre_registro(self) -> None:
        t = DOC.read_text(encoding="utf-8")
        ini = t.index("<!-- VK:decisoes:inicio -->") + len("<!-- VK:decisoes:inicio -->\n")
        fim = t.index("\n<!-- VK:decisoes:fim -->")
        self.assertEqual(t[ini:fim], M.texto_decisoes())
        self.assertEqual(len(M.DECISOES), 11)
        self.assertTrue(all(d["data"] == "2026-10-28" for d in M.DECISOES))
        try:
            h = subprocess.run(["git", "log", "--diff-filter=A", "--format=%H", "--", str(DOC.relative_to(ROOT))],
                               cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
        except (OSError, subprocess.CalledProcessError):
            self.skipTest("sem git")
        if not h:
            self.skipTest("57za ainda sem commit")
        antigo = subprocess.run(["git", "show", f"{h[-1]}:{DOC.relative_to(ROOT)}"], cwd=ROOT, capture_output=True,
                                text=True, check=True).stdout
        a_ini = antigo.index("<!-- VK:decisoes:inicio -->")
        a_fim = antigo.index("<!-- VK:decisoes:fim -->")
        self.assertEqual(antigo[a_ini:a_fim],
                         t[t.index("<!-- VK:decisoes:inicio -->"):t.index("<!-- VK:decisoes:fim -->")])
        self.assertNotIn("<!-- VK:principais:inicio -->", antigo)


if __name__ == "__main__":
    unittest.main()
