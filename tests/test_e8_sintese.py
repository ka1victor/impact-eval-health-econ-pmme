"""Testes do E8 (`scripts/rdd_bolsa/15_sintese_E8.py`): Holm das primárias, síntese e doc 44.

Três partes:

1. `TestHolmSintetico`: o ajuste de Holm com p-valores SINTÉTICOS fixados em
   memória, contra a fórmula escrita à mão e contra o `multipletests` do
   statsmodels. Nada é gravado em `output/` nem em `data/`.
2. `TestE8SaidasReais`: as saídas versionadas `output/rdd_bolsa/E8_*` batem com
   os CSV do E3, E5, E6, E7 e E9. Os alvos são lidos desses arquivos ou
   recalculados aqui, de forma independente do script; nenhum número é digitado.
3. `TestDoc44`: os blocos gerados do doc 44 são idênticos aos produzidos a partir
   das saídas do E8, e a prosa fora deles só tem parâmetros do protocolo.
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

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "15_sintese_E8.py"
_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location("e8_sintese_15", SCRIPT)
E8 = importlib.util.module_from_spec(_spec)
sys.modules["e8_sintese_15"] = E8
_spec.loader.exec_module(E8)
sys.dont_write_bytecode = _bytecode

OUT = ROOT / "output" / "rdd_bolsa"
RESUMO = OUT / "E8_resumo.json"
TABELA = OUT / "E8_tabela_sintese.csv"
DOC = ROOT / "docs" / "06_execucao" / "44_sintese_rdd_bolsa_multioutcome.md"
TEM_SAIDAS = RESUMO.exists() and TABELA.exists()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def holm_manual_dois(p_a: float, p_b: float) -> tuple[float, float]:
    """Holm com m = 2, escrito à mão: o menor p vezes 2; o maior, sem fator, nunca abaixo do anterior."""
    menor, maior = sorted((p_a, p_b))
    adj_menor = min(1.0, 2.0 * menor)
    adj_maior = max(adj_menor, min(1.0, maior))
    return (adj_menor, adj_maior) if p_a <= p_b else (adj_maior, adj_menor)


# --------------------------------------------------------------------------
# 1. Holm com p-valores sintéticos
# --------------------------------------------------------------------------

class TestHolmSintetico(unittest.TestCase):
    """Holm (1979) com p-valores sintéticos fixados aqui (não são resultados)."""

    CASOS_SINTETICOS = [(0.01, 0.04), (0.04, 0.01), (0.03, 0.03), (0.2, 0.9), (0.6, 0.7), (0.0001, 0.5)]

    def test_igual_a_formula_manual(self) -> None:
        for a, b in self.CASOS_SINTETICOS:
            adj = E8.L.holm([a, b])
            esp = holm_manual_dois(a, b)
            self.assertAlmostEqual(adj[0], esp[0], places=15)
            self.assertAlmostEqual(adj[1], esp[1], places=15)

    def test_igual_ao_statsmodels(self) -> None:
        try:
            from statsmodels.stats.multitest import multipletests
        except ImportError:  # pragma: no cover
            self.skipTest("statsmodels ausente")
        rng = np.random.default_rng(20261019)
        for _ in range(200):
            m = int(rng.integers(2, 8))
            p = rng.uniform(0, 1, m) ** 2
            np.testing.assert_allclose(E8.L.holm(p), multipletests(p, method="holm")[1], rtol=0, atol=1e-14)

    def test_propriedades(self) -> None:
        for a, b in self.CASOS_SINTETICOS:
            adj = E8.L.holm([a, b])
            self.assertTrue(np.all(adj >= np.array([a, b]) - 1e-15))  # ajuste nunca reduz o p
            self.assertTrue(np.all(adj <= 1.0))
            # Invariante à ordem.
            np.testing.assert_allclose(E8.L.holm([b, a])[::-1], adj)


# --------------------------------------------------------------------------
# 2. Saídas reais
# --------------------------------------------------------------------------

@unittest.skipUnless(TEM_SAIDAS, "saidas do E8 ausentes")
class TestE8SaidasReais(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.resumo = json.loads(RESUMO.read_text(encoding="utf-8"))
        cls.tabela = pd.read_csv(TABELA, dtype={"ciclo": str, "corte": str})
        cls.e6 = pd.read_csv(OUT / "E6_estimativas.csv", dtype={"corte": str, "ciclo": str})
        cls.e7 = pd.read_csv(OUT / "E7_estimativas.csv", dtype={"corte": str})
        cls.ev = pd.read_csv(OUT / "E7_estudo_evento.csv", dtype={"corte": str, "competencia": str})
        cls.e9 = pd.read_csv(OUT / "E9_estimativas.csv", dtype={"ciclo": str})
        cls.efm = pd.read_csv(OUT / "E9_efeitos_marginais.csv", dtype={"ciclo": str})
        cls.r6 = json.loads((OUT / "E6_resumo.json").read_text(encoding="utf-8"))
        cls.r7 = json.loads((OUT / "E7_resumo.json").read_text(encoding="utf-8"))

    def test_natureza_empirica(self) -> None:
        self.assertEqual(self.resumo["natureza_dos_dados"], "EMPIRICO")
        self.assertEqual(set(self.tabela["natureza_dos_dados"]), {"EMPIRICO"})

    def test_entradas_com_hash_atual_e_sem_arquivo_errado(self) -> None:
        for e in self.resumo["entradas"]:
            self.assertEqual(sha256(ROOT / e["caminho"]), e["sha256"], e["caminho"])
            for chave in ("fonte", "data_referencia", "cobertura", "unidade", "chaves", "filtros"):
                self.assertTrue(e[chave], f"{e['caminho']}: {chave} vazio")
            self.assertNotIn("ivs_" + "ipea", e["caminho"])  # auditoria 16
        self.assertEqual(sha256(TABELA), self.resumo["saidas"]["E8_tabela_sintese.csv"]["sha256"])

    def test_holm_com_os_p_das_linhas_do_csv(self) -> None:
        p1 = self.e6[(self.e6["outcome_id"] == "P1") & (self.e6["populacao"] == "V1+V2+V3")
                     & (self.e6["corte"] == "empilhado") & (self.e6["especificacao"] == "principal")]
        p2 = self.e7[(self.e7["outcome_id"] == "F3.1") & (self.e7["populacao"] == "U")
                     & (self.e7["corte"] == "empilhado") & (self.e7["especificacao"] == "principal")]
        self.assertEqual((len(p1), len(p2)), (1, 1))
        pa, pb = float(p1["p_valor"].iloc[0]), float(p2["p_valor"].iloc[0])
        self.assertEqual(pa, self.r6["p1_para_holm"]["p_valor"])
        self.assertEqual(pb, self.r7["p2_para_holm"]["p_valor"])
        h = self.resumo["holm"]
        self.assertEqual(h["P1"]["p_valor"], pa)
        self.assertEqual(h["P2"]["p_valor"], pb)
        esp = holm_manual_dois(pa, pb)
        self.assertAlmostEqual(h["P1"]["p_holm"], esp[0], places=15)
        self.assertAlmostEqual(h["P2"]["p_holm"], esp[1], places=15)
        self.assertEqual(h["P1"]["rejeita_holm_5pct"], esp[0] < 0.05)
        self.assertEqual(h["P2"]["rejeita_holm_5pct"], esp[1] < 0.05)
        # Na tabela-síntese, o p Holm só aparece nas duas primárias.
        com_holm = self.tabela[self.tabela["p_holm"].notna()]
        self.assertEqual(sorted(com_holm["outcome_id"]), ["F3.1", "P1"])

    def test_resumo_e_tabela_reproduzem(self) -> None:
        """O script, rodado de novo em memória, dá as mesmas saídas (salvo a data de execução)."""
        novo, tab = E8.construir()
        novo = json.loads(json.dumps(E8._sem_nan(novo), ensure_ascii=False))
        velho = {k: v for k, v in self.resumo.items() if k not in ("data_execucao", "saidas")}
        novo.pop("data_execucao")
        self.assertEqual(novo, velho)
        self.assertEqual(tab.to_csv(index=False, lineterminator="\n"), TABELA.read_text(encoding="utf-8"))

    def test_tabela_bate_com_os_csv_de_origem(self) -> None:
        """Conferência independente do script: cada linha F0–F4 da tabela = linha principal empilhada da origem."""
        for _, r in self.tabela.iterrows():
            if r["familia"] in ("F0", "F1", "F2", "F4"):
                src = self.e6[(self.e6["outcome_id"] == r["outcome_id"]) & (self.e6["populacao"] == r["populacao"])
                              & (self.e6["ciclo"] == r["ciclo"]) & (self.e6["corte"] == "empilhado")
                              & (self.e6["especificacao"] == "principal")]
                if len(src) > 1:  # outcomes por ciclo (F0.1, F0.2, F2.2): o nome do outcome está na fonte
                    nome = re.search(r"outcome == (\S+),", r["fonte"]).group(1)
                    src = src[src["outcome"] == nome]
            elif r["familia"] == "F3":
                src = self.e7[(self.e7["outcome_id"] == r["outcome_id"]) & (self.e7["populacao"] == r["populacao"])
                              & (self.e7["corte"] == "empilhado") & (self.e7["especificacao"] == "principal")]
            else:
                continue
            self.assertEqual(len(src), 1, r["outcome"])
            s = src.iloc[0]
            for a, b in (("estimativa", "tau"), ("ic95_inf", "ic95_inf"), ("ic95_sup", "ic95_sup"),
                         ("p_valor", "p_valor")):
                # Ida e volta pelo CSV pode mudar o último bit do float.
                self.assertTrue(math.isclose(float(r[a]), float(s[b]), rel_tol=1e-13, abs_tol=1e-15),
                                f"{r['outcome']}: {a}")
            if r["outcome_id"] not in ("P1",):
                self.assertTrue(math.isclose(float(r["q_bky"]), float(s["q_bky"])), r["outcome"])

    def test_e9_bate_com_os_csv(self) -> None:
        for _, r in self.tabela[self.tabela["familia"] == "E9"].iterrows():
            cic = "empilhado" if r["ciclo"] == "1+2+3" else r["ciclo"]
            q = self.efm[(self.efm["ciclo"] == cic) & (self.efm["modelo"] == "logit_condicional_1a_opcao")
                         & (self.efm["conjunto"] == "principal") & (self.efm["especificacao"] == "spline_linear__bolsa_linear")
                         & (self.efm["termo"] == "bolsa_mil") & (self.efm["quantidade"] == "razao_chances_por_5mil")]
            self.assertEqual(len(q), 1)
            self.assertTrue(math.isclose(float(r["estimativa"]), float(q["estimativa"].iloc[0]), rel_tol=1e-13))
            self.assertTrue(math.isclose(float(r["ic95_inf"]), float(q["ic95_inf"].iloc[0]), rel_tol=1e-13))
            # A razão de chances é exp(5 x coef.).
            c = self.e9[(self.e9["ciclo"] == cic) & (self.e9["modelo"] == "logit_condicional_1a_opcao")
                        & (self.e9["conjunto"] == "principal") & (self.e9["especificacao"] == "spline_linear__bolsa_linear")
                        & (self.e9["termo"] == "bolsa_mil")]
            self.assertAlmostEqual(float(r["estimativa"]), math.exp(5 * float(c["coef"].iloc[0])), places=7)

    def test_descarte_recalculado(self) -> None:
        ref = self.resumo["descarte"]["referencias"]["preenchimento_pp"]
        for x in self.resumo["descarte"]["preenchimento"]:
            src = self.e6[(self.e6["outcome_id"] == x["outcome_id"]) & (self.e6["populacao"] == x["populacao"])
                          & (self.e6["ciclo"] == x["ciclo"]) & (self.e6["corte"] == "empilhado")
                          & (self.e6["especificacao"] == "principal")]
            sup = float(src["ic95_sup"].iloc[0])
            self.assertTrue(math.isclose(x["ic95_sup"], sup, rel_tol=1e-13))
            self.assertEqual(x["exclui_referencia"], sup < ref)

    def test_sequencia_do_estudo_de_evento_recalculada(self) -> None:
        s = self.ev[(self.ev["outcome_id"] == "F3.1") & (self.ev["populacao"] == "U") & (self.ev["corte"] == "0.300")
                    & self.ev["tau"].notna()].sort_values("competencia")
        sig = (s["p_valor"] < 0.05).tolist()
        melhor, atual, fim = 0, 0, None
        for i, v in enumerate(sig):
            atual = atual + 1 if v else 0
            if atual > melhor:
                melhor, fim = atual, i
        seq = s.iloc[fim - melhor + 1:fim + 1]
        o = self.resumo["e7"]["f31_U_0300"]["maior_sequencia_p_menor_005"]
        self.assertEqual(o["n_meses"], melhor)
        self.assertEqual(o["inicio"], f"{seq['competencia'].iloc[0][:4]}-{seq['competencia'].iloc[0][4:]}")
        self.assertEqual(o["fim"], f"{seq['competencia'].iloc[-1][:4]}-{seq['competencia'].iloc[-1][4:]}")

    def test_afirmacoes_conferidas(self) -> None:
        af = self.resumo["afirmacoes_conferidas"]
        self.assertTrue(af)
        self.assertEqual([k for k, v in af.items() if not v], [])

    def test_literatura_copiada_da_fonte(self) -> None:
        for x in self.resumo["literatura"]["estudos"]:
            self.assertIn(x["linha_fonte"], (ROOT / x["fonte"]).read_text(encoding="utf-8"))
        for t in self.resumo["literatura"]["trechos"]:
            self.assertIn(t["trecho"], (ROOT / t["fonte"]).read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# 3. Doc 44
# --------------------------------------------------------------------------

@unittest.skipUnless(TEM_SAIDAS and DOC.exists(), "saidas do E8 ou doc 44 ausentes")
class TestDoc44(unittest.TestCase):
    def test_blocos_iguais_aos_gerados_das_saidas(self) -> None:
        resumo, tabela = E8.ler_saidas()
        gerados = E8.blocos_doc(resumo, tabela)
        no_doc = E8.blocos_no_doc(DOC.read_text(encoding="utf-8"))
        self.assertEqual(set(no_doc), set(gerados))
        for k, v in gerados.items():
            self.assertEqual(no_doc[k], v, f"bloco {k} do doc 44 difere das saidas do E8")

    @staticmethod
    def _prosa() -> str:
        texto = E8.MARCA.sub("", DOC.read_text(encoding="utf-8"))
        texto = re.sub(r"```.*?```", "", texto, flags=re.S)                    # bloco de comandos
        texto = re.sub(r"`[^`]*`", "", texto)                                  # nomes de arquivo e coluna
        texto = re.sub(r"\]\([^)]*\)", "]", texto)                             # links
        texto = re.sub(r"(?m)^#+ .*$", "", texto)                              # títulos numerados
        texto = re.sub(r"§+\s?\d+(?:[.,–-]\d+)*", "", texto)                   # seções
        texto = re.sub(r"\b\d{2}/\d{2}/\d{4}\b", "", texto)                    # datas
        texto = re.sub(r"\b\d{4}-\d{2}\b", "", texto)                          # competências
        texto = re.sub(r"\b(?:docs?|seção|auditorias?|pedido|protocolo|tarefa)\s+\d+[a-z]?\b", "", texto)
        texto = re.sub(r"\[\d+[a-z]?\]", "", texto)                            # [37], [41a]
        texto = re.sub(r"\b[A-Za-z_]+\d+[a-z]?(?:\.\d+)*\b", "", texto)        # F1.3, V1, E9, H1
        texto = re.sub(r"\d+ª", "", texto)                                     # 1ª chamada
        texto = re.sub(r"(?m)^\s*\d+\. ", "", texto)                           # listas numeradas
        texto = re.sub(r"\b\d+(?:\.\d+)?/\d{4}\b", "", texto)                  # atos normativos
        for fixo in ("SHA-256", "IC 95%"):
            texto = texto.replace(fixo, "")
        return texto

    def test_prosa_sem_numero_de_resultado(self) -> None:
        texto = self._prosa()
        decimais = set(re.findall(r"(?<![\w.,])[−+-]?\d+[,.]\d+", texto))
        permitidos = {"0,300", "0,400", "0,050", "0,05", "0,3", "0,4", "1,96"}  # cortes, h, alfa, valor crítico
        self.assertEqual(decimais - permitidos, set())

    def test_prosa_sem_inteiro_de_resultado(self) -> None:
        texto = re.sub(r"(?<![\w.,])[−+-]?\d+[,.]\d+", "", self._prosa())
        inteiros = set(re.findall(r"(?<![\w.,])[−+-]?\d+(?![\w.,]\d)", texto))
        permitidos = {"1", "2", "3", "5", "+10", "+25", "+26"}  # ciclos, R$ 5 mil, 5%, referências do protocolo e
        # a citação de Dal Bó et al. (+26% de candidaturas), que o teste de literatura confere na fonte
        anos = {x for x in inteiros if x.isdigit() and 2000 <= int(x) <= 2030}
        self.assertEqual(inteiros - permitidos - anos, set())

    def test_secoes_obrigatorias(self) -> None:
        texto = DOC.read_text(encoding="utf-8")
        for titulo in ("## 1. Resposta curta", "## 3. Tabela-síntese por elo da cadeia", "## 4. Testes primários com Holm",
                       "## 5. O que podemos afirmar e o que não podemos",
                       "## 6. Comparação com a literatura de magnitude",
                       "## 7. Revisão da pergunta e da hipótese econômica (PROPOSTA ao autor, não decisão)",
                       "### 7.3 Proposta A", "### 7.4 Proposta B", "### 7.5 Proposta C", "## 8. Limitações",
                       "## 9. Próximos passos"):
            self.assertIn(titulo, texto)
        corrido = " ".join(texto.split())
        # CLAUDE.md: incentivo marginal ≠ participação no PMM-E ≠ Agora Tem Especialistas.
        self.assertIn("nenhum é efeito da participação no PMM-E nem do Agora Tem Especialistas", corrido)
        self.assertIn("Não é participação no PMM-E nem Agora Tem Especialistas", corrido)
        self.assertIn("Tudo aqui é **proposta** para o autor decidir", corrido)


if __name__ == "__main__":
    unittest.main()
