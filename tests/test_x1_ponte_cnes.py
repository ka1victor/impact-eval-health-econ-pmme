"""Testes do X1 (ponte PMM-E–CNES, `scripts/rdd_bolsa/17_ponte_pmme_cnes.py`), protocolo do doc 45.

Três partes:

1. `TestX1LigacaoSintetico` e `TestX1OutcomesSintetico`: dados SINTÉTICOS,
   montados em memória (registros, vínculos, nomes e coordenadas fictícios),
   nunca gravados. Conferem a regra de ligação (CRM+UF; CRM+nome; ambíguos fora),
   a compatibilidade de nomes, as categorias de origem, a distância e a contagem
   de vínculos depois do início.
2. `TestX1SaidasReais`: invariantes das saídas EMPÍRICAS `output/rdd_bolsa/X1_*`:
   natureza e estatuto, hashes das entradas, nenhuma competência >= 202609,
   taxas de ligação e descritivos recalculados do parquet, q de BKY recalculado,
   e nenhum dado pessoal (nome, CRM, CPF) nas saídas. Os alvos vêm das saídas
   ou das listas de entrada, nunca digitados.
3. `TestDoc46X1`: os blocos `<!-- X1:... -->` do doc 46 são idênticos aos gerados
   das saídas, e a prosa da seção X1 fora deles só tem parâmetros do protocolo.
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
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "17_ponte_pmme_cnes.py"
_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location("x1_ponte_17", SCRIPT)
X1 = importlib.util.module_from_spec(_spec)
sys.modules["x1_ponte_17"] = X1
_spec.loader.exec_module(X1)
sys.dont_write_bytecode = _bytecode

TEM_SAIDAS = all(p.exists() for p in (X1.OUT_RESUMO, X1.OUT_MEDICOS, X1.OUT_ESTIMATIVAS, X1.OUT_DESCRITIVO))


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


# --------------------------------------------------------------------------
# 1. Sintético (só em memória)
# --------------------------------------------------------------------------

def _vinc_sintetico(linhas: list[tuple]) -> pd.DataFrame:
    cols = ["competencia", "co_unidade", "co_cnes", "co_municipio", "co_profissional_sus", "nu_registro", "sg_uf_crm"]
    df = pd.DataFrame(linhas, columns=cols)
    df["co_regiao_saude"] = pd.NA
    df["co_cbo"] = "225125"
    return df


class TestX1LigacaoSintetico(unittest.TestCase):
    """Regra de ligação com registros SINTÉTICOS."""

    def setUp(self) -> None:
        self.listas = pd.DataFrame({
            "id_medico": ["m1", "m2", "m3", "m4", "m5", "m6", "m7", "m8"],
            "crm": ["100", "200", "300", "400", "500", pd.NA, "700", "800"],
            "uf": ["SP", "RJ", "MG", "BA", "PE", "SP", "AM", "SP"],
            "_nome": ["ANA SOUZA", "BRUNO LIMA", "CARLA DIAS", "DANIEL REIS", "EVA ROCHA", "FABIO", "GIL COSTA",
                      "HELENA PRADO"],
        })
        self.vinc = _vinc_sintetico([
            ("202406", "u1", "0000001", "355030", "P1", "100", "SP"),     # m1: etapa 1
            ("202406", "u2", "0000002", "330455", "P2", "200", "RJ"),     # m2: etapa 1 ambígua (dois profissionais)
            ("202406", "u3", "0000003", "330455", "P3", "200", "RJ"),
            ("202406", "u4", "0000004", "310620", "P4", "300", "SP"),     # m3: CRM em outra UF, nome compatível
            ("202406", "u5", "0000005", "292740", "P5", "400", "SE"),     # m4: CRM em outra UF, nome incompatível
            ("202406", "u6", "0000006", "261160", "P6", "500", "PB"),     # m5: duas pessoas compatíveis -> ambíguo
            ("202406", "u7", "0000007", "261160", "P7", "500", "AL"),
            ("202406", "u8", "0000008", "355030", "P8", "800", "SP"),     # m8: colisão de CRM na UF do posto ...
            ("202406", "u9", "0000009", "330455", "P9", "800", "RJ"),     # ... e a pessoa certa em outra UF
        ])
        self.nomes = pd.DataFrame({
            "competencia": "202406",
            "co_profissional_sus": ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9"],
            "nome_norm": ["ANA MARIA SOUZA", "BRUNO LIMA", "BRUNO LIMA", "CARLA MARIA DIAS", "JOAO REIS",
                          "EVA ROCHA", "EVA MARIA ROCHA", "OTAVIO NUNES", "HELENA M PRADO"],
        })

    def test_regra(self) -> None:
        lig, diag = X1.ligar(self.listas, self.vinc, self.nomes)
        r = lig.set_index("id_medico")
        self.assertEqual(r.at["m1", "co_profissional_sus"], "P1")
        self.assertEqual(r.at["m1", "etapa_ligacao"], "1_crm_uf")
        self.assertTrue(pd.isna(r.at["m2", "co_profissional_sus"]))
        self.assertEqual(r.at["m2", "motivo"], "ambiguo_crm_uf_com_mais_de_um_profissional")
        self.assertEqual(r.at["m3", "co_profissional_sus"], "P4")
        self.assertEqual(r.at["m3", "etapa_ligacao"], "2_crm_nome")
        self.assertEqual(r.at["m4", "motivo"], "crm_sem_nome_compativel")
        self.assertEqual(r.at["m5", "motivo"], "ambiguo_crm_nome_com_mais_de_um_profissional")
        self.assertEqual(r.at["m6", "motivo"], "crm_ausente_na_lista")
        self.assertEqual(r.at["m7", "motivo"], "crm_sem_vinculo_medico_no_cnes")
        # Desvio D1: colisão na UF do posto não liga; a pessoa certa liga pela etapa 2.
        self.assertEqual(r.at["m8", "co_profissional_sus"], "P9")
        self.assertEqual(r.at["m8", "etapa_ligacao"], "2_crm_nome")
        self.assertEqual(r.at["m8", "etapa1_rejeitada_por_nome"], 1)
        self.assertEqual(diag["etapa1_candidato_unico"], 2)
        self.assertEqual(diag["etapa1_nome_compativel"], 1)
        self.assertEqual(diag["etapa1_rejeitadas_ligadas_na_etapa2"], 1)

    def test_regra_literal(self) -> None:
        lig, _ = X1.ligar(self.listas, self.vinc, self.nomes, exigir_nome_etapa1=False)
        r = lig.set_index("id_medico")
        self.assertEqual(r.at["m8", "co_profissional_sus"], "P8")
        self.assertEqual(r.at["m8", "etapa_ligacao"], "1_crm_uf")
        self.assertEqual(r.at["m1", "co_profissional_sus"], "P1")

    def test_nomes_compativeis(self) -> None:
        self.assertTrue(X1.nomes_compativeis("José da Silva", "JOSE SILVA"))
        self.assertTrue(X1.nomes_compativeis("MARIA DE FATIMA COSTA", "MARIA FATIMA COSTA PEREIRA"))
        self.assertFalse(X1.nomes_compativeis("MARIA COSTA", "ANA COSTA"))
        self.assertFalse(X1.nomes_compativeis("PEDRO ALVES", "PEDRO SANTOS"))
        self.assertFalse(X1.nomes_compativeis("", "PEDRO"))

    def test_registro_norm(self) -> None:
        s = X1.registro_norm(pd.Series(["0012345", "CRM 99", "", None]))
        self.assertEqual(s.iloc[0], "12345")
        self.assertEqual(s.iloc[1], "99")
        self.assertTrue(pd.isna(s.iloc[2]) and pd.isna(s.iloc[3]))


class TestX1OutcomesSintetico(unittest.TestCase):
    """Origem, distância e vínculos depois do início com dados SINTÉTICOS."""

    def test_categorias_e_distancia(self) -> None:
        med = pd.DataFrame({
            "id_medico": ["a", "b", "c", "d", "e", "f"],
            "co_profissional_sus": ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6"],
            "co_cnes": ["9000001"] * 6, "co_ibge": ["100001"] * 6,
            "mes_inicio": ["202511", "202511", "202511", "202511", "202511", "202604"],
        })
        vinc = _vinc_sintetico([
            ("202510", "u1", "9000001", "100001", "Q1", "1", "XX"),   # a: mesmo estab. e município
            ("202608", "u1", "9000001", "100001", "Q1", "1", "XX"),
            ("202608", "u9", "9000009", "100003", "Q1", "1", "XX"),
            ("202510", "u2", "9000002", "100002", "Q2", "2", "XX"),   # b: mesma região, outro município
            ("202510", "u3", "9000003", "100003", "Q3", "3", "XX"),   # c: mesma UF, outra região
            ("202510", "u4", "9000004", "200001", "Q4", "4", "XX"),   # d: outra UF
            ("202406", "u5", "9000005", "100001", "Q5", "5", "XX"),   # e: só antes da última pré -> sem vínculo
            ("202602", "u6", "9000006", "200001", "Q6", "6", "XX"),   # f: última pré = 202602; outra UF ...
            ("202602", "u7", "9000007", "100002", "Q6", "6", "XX"),   # ... e mesma região: vence a mais próxima
        ])
        regiao = pd.Series({"100001": "10|R1", "100002": "10|R1", "100003": "10|R2", "200001": "20|R9"})
        coord = pd.DataFrame({"co_ibge": ["100001", "100002", "100003", "200001"],
                              "lon": [0.0, 0.0, 1.0, 0.0], "lat": [0.0, 1.0, 0.0, 10.0]})
        o = X1.outcomes_medico(med, vinc, regiao, coord).set_index("id_medico")
        esperado = {"a": "mesmo_municipio", "b": "mesma_regiao_saude", "c": "mesma_uf", "d": "outra_uf",
                    "e": "sem_vinculo_medico_anterior", "f": "mesma_regiao_saude"}
        for k, v in esperado.items():
            self.assertEqual(o.at[k, "c_origem"], v, k)
        self.assertEqual(o.at["a", "a_mesmo_estab_ultimo_pre"], 1)
        self.assertEqual(o.at["b", "b_mesmo_mun_ultimo_pre"], 0)
        self.assertEqual(o.at["e", "b_mesmo_mun_algum_pre"], 1)
        self.assertEqual(o.at["e", "b_mesmo_mun_ultimo_pre"], 0)
        self.assertEqual(o.at["a", "ultima_competencia_pre"], "202510")
        self.assertEqual(o.at["f", "ultima_competencia_pre"], "202602")
        self.assertAlmostEqual(o.at["a", "d_distancia_km"], 0.0)
        um_grau = 2 * math.pi * X1.RAIO_TERRA_KM / 360.0
        self.assertAlmostEqual(o.at["b", "d_distancia_km"], um_grau, places=6)
        self.assertAlmostEqual(o.at["f", "d_distancia_km"], um_grau, places=6)  # origem mais próxima
        self.assertTrue(pd.isna(o.at["e", "d_distancia_km"]))
        self.assertEqual(o.at["a", "e_vinculos_202608"], 2)
        self.assertEqual(o.at["a", "e_estabelecimentos_202608"], 2)
        self.assertEqual(o.at["a", "vinculo_no_estab_do_posto_202608"], 1)
        self.assertEqual(o.at["b", "e_vinculos_202608"], 0)

    def test_limite_ciclo3(self) -> None:
        self.assertTrue(all(c < X1.LIMITE_EXCLUSIVO for c in X1.COMPETENCIAS))
        with self.assertRaises(RuntimeError):
            X1.checar_limite("202609")


# --------------------------------------------------------------------------
# 2. Saídas reais
# --------------------------------------------------------------------------

@unittest.skipUnless(TEM_SAIDAS, "saídas do X1 ausentes")
class TestX1SaidasReais(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.resumo, cls.est, cls.desc = X1.ler_saidas()
        cls.med = pd.read_parquet(X1.OUT_MEDICOS)

    def test_natureza_e_estatuto(self) -> None:
        self.assertEqual(self.resumo["natureza_dos_dados"], "EMPIRICO")
        self.assertEqual(self.resumo["estatuto"], "EXPLORATORIO_POS_SINTESE")
        for df in (self.med, self.est, self.desc):
            self.assertTrue((df["natureza_dos_dados"] == "EMPIRICO").all())
            self.assertTrue((df["estatuto"] == "EXPLORATORIO_POS_SINTESE").all())

    def test_entradas_com_hash_atual_e_sem_arquivo_errado(self) -> None:
        for e in self.resumo["entradas"]:
            self.assertNotIn("ivs_ipea_2010_municipios", e["caminho"])
            p = ROOT / e["caminho"]
            self.assertTrue(p.exists(), e["caminho"])
            self.assertEqual(sha256(p), e["sha256"], e["caminho"])
        for c, m in self.resumo["competencias_cnes"].items():
            self.assertLess(c, "202609")
            self.assertEqual(len(m["sha256_zip"]), 64)
            self.assertTrue(m["url"].endswith(f"BASE_DE_DADOS_CNES_{c}.ZIP"))
        self.assertEqual(sorted(self.resumo["competencias_cnes"]), list(X1.COMPETENCIAS))
        for p, h in self.resumo["saidas"].items():
            self.assertEqual(sha256(ROOT / p), h, p)

    def test_taxas_de_ligacao_recalculadas(self) -> None:
        for ciclo, r in self.resumo["taxas_ligacao"]["por_ciclo"].items():
            d = self.med[self.med["ciclo"] == int(ciclo)]
            self.assertEqual(r["registros"], len(d))
            self.assertEqual(r["ligados"], int(d["ligado"].sum()))
            self.assertAlmostEqual(r["taxa"], float(d["ligado"].mean()))
            self.assertEqual(r["etapa_1_crm_uf"] + r["etapa_2_crm_nome"], r["ligados"])
            self.assertEqual(r["ligados"] + r["ambiguos"] + r["nao_ligados_sem_ambiguidade"], r["registros"])
        self.assertTrue(((self.med["ligado"] == 1) == (self.med["motivo_ligacao"] == "ligado")).all())

    def test_outcomes_coerentes(self) -> None:
        m = self.med[(self.med["ligado"] == 1) & self.med["ciclo"].isin([1, 2])]
        com_pre = m[m["competencias_pre_inicio"] > 0]
        self.assertTrue(com_pre["b_mesmo_mun_ultimo_pre"].notna().all())
        self.assertTrue((com_pre["a_mesmo_estab_ultimo_pre"] <= com_pre["b_mesmo_mun_ultimo_pre"]).all())
        self.assertTrue((com_pre["b_mesmo_mun_ultimo_pre"] <= com_pre["b_mesmo_mun_algum_pre"]).all())
        self.assertTrue(((com_pre["c_origem"] == "mesmo_municipio") == (com_pre["b_mesmo_mun_ultimo_pre"] == 1)).all())
        sem = com_pre["c_origem"] == "sem_vinculo_medico_anterior"
        self.assertTrue(com_pre.loc[sem, "d_distancia_km"].isna().all())
        self.assertTrue((com_pre.loc[com_pre["c_origem"] == "mesmo_municipio", "d_distancia_km"] == 0).all())
        self.assertTrue((com_pre["d_distancia_km"].dropna() >= 0).all())
        self.assertTrue(set(com_pre["c_origem"].dropna()) <= set(X1.ORIGENS))
        self.assertTrue(self.med.loc[self.med["ciclo"] == 3, "c_origem"].isna().all())

    def test_descritivo_recalculado(self) -> None:
        for ciclo, cs in (("1", [1]), ("2", [2]), ("1+2", [1, 2])):
            m = self.med[self.med["ciclo"].isin(cs) & (self.med["ligado"] == 1)]
            novo = (1 - m["b_mesmo_mun_ultimo_pre"]).dropna()
            d = self.desc[self.desc["regra_ligacao"] == "principal_d1"]
            r = d[(d["ciclo"] == ciclo) & (d["faixa"] == "todas") & (d["fonte_lista"] == "todas")
                  & (d["indicador"] == "novo_no_municipio")].iloc[0]
            self.assertEqual(r["n_base"], len(novo))
            self.assertAlmostEqual(r["valor"], float(novo.mean()))
            for o in X1.ORIGENS:
                x = (m["c_origem"] == o).astype(float).where(m["c_origem"].notna()).dropna()
                r = d[(d["ciclo"] == ciclo) & (d["faixa"] == "todas") & (d["fonte_lista"] == "todas")
                      & (d["indicador"] == f"origem_{o}")].iloc[0]
                self.assertAlmostEqual(r["valor"], float(x.mean()))

    def test_bky_recalculado(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts" / "rdd_bolsa"))
        import rdd_lib
        q = rdd_lib.qvalores_bky(self.est["p_valor"].to_numpy(dtype=float))
        np.testing.assert_allclose(q, self.est["q_bky_x1"].to_numpy(dtype=float), equal_nan=True)

    def test_especificacoes_presentes(self) -> None:
        e = self.est
        for y in X1.OUTCOMES_RDD:
            for ciclo in ("1", "2"):
                for corte in ("0.300", "0.400", "empilhado"):
                    self.assertEqual(len(e[(e["analise"] == "rdd_condicional") & (e["outcome"] == y)
                                           & (e["ciclo"] == ciclo) & (e["corte"] == corte)]), 1)
                for corte in ("0.300", "0.400"):
                    self.assertEqual(len(e[(e["analise"] == "limites_lee") & (e["outcome"] == y)
                                           & (e["ciclo"] == ciclo) & (e["corte"] == corte)]), 1)
            self.assertEqual(len(e[(e["analise"] == "rdd_condicional") & (e["outcome"] == y) & (e["ciclo"] == "1+2")]), 1)
        sem_valor = e[e["analise"].isin(["rdd_condicional", "rdd_selecao"]) & e["tau"].isna()]
        self.assertTrue((sem_valor["nota"].fillna("") != "").all())

    def test_sem_dados_pessoais(self) -> None:
        proibidas = {"nome", "_nome", "crm", "cpf", "cns", "co_profissional_sus", "nu_registro", "inscricao"}
        self.assertEqual(proibidas & set(self.med.columns), set())
        self.assertEqual(proibidas & set(self.est.columns), set())
        self.assertEqual(proibidas & set(self.desc.columns), set())
        listas, _ = X1.ler_listas_pmme()
        nomes = {n for n in listas["_nome"] if len(n.split()) >= 2}
        crms = set(listas["crm"].dropna())
        textos = [X1.OUT_RESUMO.read_text(encoding="utf-8"), X1.OUT_ESTIMATIVAS.read_text(encoding="utf-8"),
                  X1.OUT_DESCRITIVO.read_text(encoding="utf-8")]
        for col in self.med.columns:
            if self.med[col].dtype == object or str(self.med[col].dtype).startswith(("string", "str")):
                valores = set(self.med[col].dropna().astype(str))
                self.assertEqual(valores & crms - {"1", "2", "3"} if col == "ciclo" else valores & crms, set(), col)
                self.assertEqual(valores & nomes, set(), col)
                textos.append("\n".join(sorted(valores)))
        corpo = X1.texto_norm("\n".join(textos))
        achados = [n for n in nomes if f" {n} " in f" {corpo} "]
        self.assertEqual(achados, [])


# --------------------------------------------------------------------------
# 3. Doc 46, seção X1
# --------------------------------------------------------------------------

@unittest.skipUnless(TEM_SAIDAS and X1.DOC_46.exists(), "saídas do X1 ou doc 46 ausentes")
class TestDoc46X1(unittest.TestCase):
    def _secao(self) -> str:
        texto = X1.DOC_46.read_text(encoding="utf-8")
        m = re.search(r"(?ms)^## X1\b.*?(?=^## (?!X1)|\Z)", texto)
        self.assertIsNotNone(m)
        return m.group(0)

    def test_blocos_iguais_aos_gerados(self) -> None:
        gerados = X1.blocos_doc(*X1.ler_saidas())
        no_doc = X1.blocos_no_doc(self._secao())
        self.assertEqual(set(no_doc), set(gerados))
        for k, v in gerados.items():
            self.assertEqual(no_doc[k], v, f"bloco X1:{k} difere das saídas")

    def test_prosa_sem_numero_de_resultado(self) -> None:
        t = X1.MARCA.sub("", self._secao())
        t = re.sub(r"`[^`]*`", "", t)
        t = re.sub(r"\]\([^)]*\)", "]", t)
        t = re.sub(r"(?m)^#+ .*$", "", t)
        t = re.sub(r"§+\s?\d+(?:[.,–-]\d+)*", "", t)
        t = re.sub(r"\b\d{2}/\d{2}/\d{4}\b", "", t)
        t = re.sub(r"\b\d{6}\b", "", t)                                  # competências AAAAMM
        t = re.sub(r"\b(?:docs?|doc\.|protocolo|auditoria)\s+\d+[a-z]?\b", "", t)
        t = re.sub(r"\b[A-Za-z_]+\d+[a-z]?(?:\.\d+)*\b", "", t)          # X1, E9, V1, F2.1
        t = re.sub(r"\d+ª", "", t)
        t = re.sub(r"(?m)^\s*\d+\. ", "", t)
        t = t.replace("SHA-256", "").replace("IC 95%", "")
        decimais = set(re.findall(r"(?<![\w.,])[−+-]?\d+[,.]\d+", t))
        self.assertEqual(decimais - {"0,300", "0,400", "0,050", "0,05"}, set())
        t = re.sub(r"(?<![\w.,])[−+-]?\d+[,.]\d+", "", t)
        inteiros = set(re.findall(r"(?<![\w.,])[−+-]?\d+(?![\w.,]\d)", t))
        anos = {x for x in inteiros if x.isdigit() and 2000 <= int(x) <= 2030}
        self.assertEqual(inteiros - anos - {"1", "2", "3", "5", "100"}, set())


if __name__ == "__main__":
    unittest.main()
