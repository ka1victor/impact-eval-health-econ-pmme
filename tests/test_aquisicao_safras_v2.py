"""Testes das safras v2 do SIH (a13b) e do SIA (a12b), adendo §12.1 do protocolo 47.

Os testes de lógica usam painéis SINTÉTICOS montados em memória ou em diretório
temporário (municípios 99000x, UF "99", quantidades inventadas que não representam
nenhum dado real). Os testes de artefato leem só as saídas versionadas em
``output/aquisicao/sih_v2/`` e ``output/aquisicao/sia_v2/`` e as da v1. Nenhum
teste lê IVS nem usa a rede.
"""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
AQ = ROOT / "scripts" / "aquisicao"


def _carregar(nome: str, arquivo: Path):
    spec = importlib.util.spec_from_file_location(nome, arquivo)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


A13B = _carregar("safra_v2_sih_a13b", AQ / "a13b_safra_v2_sih.py")
A12B = _carregar("safra_v2_sia_a12b", AQ / "a12b_safra_v2_sia.py")
SIH_V2 = ROOT / "output" / "aquisicao" / "sih_v2"
SIA_V2 = ROOT / "output" / "aquisicao" / "sia_v2"
DOC = ROOT / "docs" / "auditorias" / "aquisicao" / "A12b_A13b_safras_v2.md"


class TestEmbrulhoNaoMudaOsOriginais(unittest.TestCase):
    def test_a13_sozinho_continua_gravando_na_v1(self) -> None:
        a13 = _carregar("a13_limpo", AQ / "a13_adquirir_sih_tabnet.py")
        self.assertEqual(a13.OUT_DIR, ROOT / "output" / "aquisicao" / "sih")
        self.assertEqual(a13.PAINEL_FILE.parent, a13.OUT_DIR)
        A13B.redirecionar()
        self.assertEqual(A13B.a13.OUT_DIR, SIH_V2)
        for nome in ("CACHE_DIR", "FORM_FILE", "FORM_META", "PAINEL_FILE", "CARATER_FILE", "IGNORADOS_FILE",
                     "VALIDACOES_FILE", "RESUMO_FILE", "MANIFESTO_FILE"):
            self.assertTrue(str(getattr(A13B.a13, nome)).startswith(str(SIH_V2)), nome)
            self.assertEqual(getattr(A13B.a13, nome).name, getattr(a13, nome).name, nome)
        self.assertEqual(A13B.a13.COMPETENCIAS, a13.COMPETENCIAS)
        self.assertTrue(all(c < "202609" for c in A13B.a13.COMPETENCIAS))

    def test_a12_sozinho_continua_com_55_meses(self) -> None:
        a12 = _carregar("a12_limpo", AQ / "a12_adquirir_sia_tabnet.py")
        self.assertEqual((len(a12.COMPETENCIAS), a12.MES_CONFERENCIA_UF), (55, "202506"))
        self.assertEqual(a12.OUT_DIR, ROOT / "output" / "aquisicao" / "sia")
        A12B.redirecionar()
        self.assertEqual(A12B.a12.COMPETENCIAS, [f"2025{m:02d}" for m in range(9, 13)] + [f"2026{m:02d}" for m in range(1, 8)])
        self.assertEqual(A12B.a12.MES_CONFERENCIA_UF, "202509")
        self.assertTrue(all(c < "202609" for c in A12B.a12.COMPETENCIAS))
        for nome in ("CACHE_DIR", "PAINEL_FILE", "MANIFESTO_FILE", "CBO_FILE", "RESUMO_FILE"):
            self.assertTrue(str(getattr(A12B.a12, nome)).startswith(str(SIA_V2)), nome)


class TestComparacaoSintetica(unittest.TestCase):
    def test_sih_por_uf_ausente_nunca_zero_e_exterior_fora(self) -> None:
        # SINTÉTICO: UF 99 com dois municípios e o ignorado da UF; exterior ("00") não entra na UF
        painel = pd.DataFrame({
            "co_ibge": ["990001", "990002", "980001"], "uf": ["99", "99", "98"], "competencia": ["202201"] * 3,
            "grupo": ["04"] * 3, "aih_aprovadas": pd.array([3, 4, pd.NA], dtype="Int64"),
            "internacoes": pd.array([3, 4, pd.NA], dtype="Int64"), "valor_total": [10.0, 20.0, np.nan],
            "status": ["observado", "observado", "ausente_uf_mes_sem_dado"]})
        ign = pd.DataFrame({"linha_tabnet": ["IGNORADO_ZZ", "000000"], "uf": ["99", "00"], "competencia": ["202201"] * 2,
                            "grupo": ["04"] * 2, "aih_aprovadas": pd.array([1, 50], dtype="Int64"),
                            "internacoes": pd.array([1, 50], dtype="Int64"), "valor_total": [5.0, 500.0],
                            "status": ["observado", "observado"]})
        u = A13B._por_uf(painel, ign).set_index("uf")
        self.assertEqual(u.loc["99", "aih"], 8)
        self.assertAlmostEqual(u.loc["99", "valor"], 35.0)
        self.assertTrue(pd.isna(u.loc["98", "aih"]))
        self.assertTrue(bool(u.loc["98", "ausente"]))
        self.assertNotIn("00", u.index)

    def test_sia_celula_a_celula(self) -> None:
        # SINTÉTICO: v1 e v2 com uma célula igual, uma revista, um subgrupo só na v2 e um município ausente na v1
        chave = ["co_ibge", "competencia_processamento", "subgrupo", "conjunto_cbo"]
        v1 = pd.DataFrame([["990001", "202509", "0301", "todos_profissionais", 5, "valor_tabnet"],
                           ["990002", "202509", "0301", "todos_profissionais", 2, "valor_tabnet"],
                           ["990003", "202509", "0301", "todos_profissionais", None, "municipio_ausente_da_resposta"]],
                          columns=chave + ["qtd_aprovada", "status"])
        v2 = pd.DataFrame([["990001", "202509", "0301", "todos_profissionais", 5, "valor_tabnet"],
                           ["990002", "202509", "0301", "todos_profissionais", 3, "valor_tabnet"],
                           ["990003", "202509", "0301", "todos_profissionais", 1, "valor_tabnet"],
                           ["990001", "202509", "0201", "todos_profissionais", 4, "valor_tabnet"],
                           ["990002", "202509", "0201", "todos_profissionais", 0, "zero_tabnet"],
                           ["990003", "202509", "0201", "todos_profissionais", 0, "zero_tabnet"]],
                          columns=chave + ["qtd_aprovada", "status"])
        with tempfile.TemporaryDirectory() as d:
            p1, p2 = Path(d) / "v1.parquet", Path(d) / "v2.parquet"
            for df, p in ((v1, p1), (v2, p2)):
                df = df.copy()
                df["qtd_aprovada"] = df["qtd_aprovada"].astype("Int64")
                df.to_parquet(p, index=False)
            with mock.patch.object(A12B, "V1_PAINEL", p1), mock.patch.object(A12B.a12, "PAINEL_FILE", p2):
                m, dif = A12B.comparar_mes("202509")
        sit = m.set_index(["co_ibge", "subgrupo"])["situacao"]
        self.assertEqual(sit[("990001", "0301")], "igual")
        self.assertEqual(sit[("990002", "0301")], "diferente")
        self.assertEqual(sit[("990003", "0301")], "ausente_so_na_v1")
        self.assertEqual(sit[("990001", "0201")], "subgrupo_so_na_v2")
        # subgrupo só numa safra com quantidade zero não é diferença
        self.assertEqual(sorted(zip(dif["co_ibge"], dif["subgrupo"])),
                         [("990001", "0201"), ("990002", "0301"), ("990003", "0301")])
        aus = dif.set_index(["co_ibge", "subgrupo"]).loc[("990003", "0301")]
        self.assertTrue(pd.isna(aus["qtd_aprovada_v1"]))  # ausente continua nulo, nunca zero


@unittest.skipUnless((SIH_V2 / "manifesto_sih.json").exists(), "safra v2 do SIH ausente")
class TestSafraV2SIH(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.man = json.loads((SIH_V2 / "manifesto_sih.json").read_text(encoding="utf-8"))
        cls.res = json.loads((SIH_V2 / "comparacao_v2_v1_resumo.json").read_text(encoding="utf-8"))
        cls.mes = pd.read_csv(SIH_V2 / "comparacao_v2_v1_mes.csv", dtype={"competencia": str})
        cls.uf = pd.read_csv(SIH_V2 / "comparacao_v2_v1_uf_mes_grupo.csv",
                             dtype={"competencia": str, "uf": str, "grupo": str})

    def test_mesmo_esquema_da_v1_e_empirico(self) -> None:
        for nome in ("painel_sih_municipio_mes_grupo.parquet", "painel_sih_municipio_mes_carater_g04.parquet",
                     "ignorados_sih_uf_mes_grupo.parquet"):
            e1 = pq.read_schema(ROOT / "output" / "aquisicao" / "sih" / nome).names
            e2 = pq.read_schema(SIH_V2 / nome).names
            self.assertEqual(e1, e2, nome)
        p = pd.read_parquet(SIH_V2 / "painel_sih_municipio_mes_grupo.parquet", columns=["competencia", "natureza_dos_dados"])
        self.assertEqual(set(p["natureza_dos_dados"]), {"EMPIRICO"})
        self.assertEqual(sorted(p["competencia"].unique()), A13B.a13.COMPETENCIAS)
        self.assertTrue((p["competencia"] < "202609").all())

    def test_manifesto_da_safra_com_horarios_de_extracao(self) -> None:
        s = self.man["safra"]
        self.assertEqual(s["versao"], "v2")
        self.assertLess(s["extracao_primeira_utc"], s["extracao_ultima_utc"])
        horas = sorted(q["data_hora_utc"] for q in self.man["consultas_realizadas"])
        self.assertEqual((horas[0], horas[-1]), (s["extracao_primeira_utc"], s["extracao_ultima_utc"]))
        self.assertEqual(len(self.man["consultas_realizadas"]), 55 * 8)
        self.assertGreater(s["extracao_primeira_utc"], self.res["safra_v1"]["consultas_ultima_utc"])

    def test_meses_revisados_coerentes(self) -> None:
        rev = self.mes.loc[self.mes["mes_revisado"], "competencia"].tolist()
        self.assertEqual(rev, self.res["meses_revisados"])
        self.assertEqual(rev, self.man["safra"]["meses_revisados_frente_a_v1"])
        nao = self.uf[~self.uf["competencia"].isin(rev)]
        self.assertTrue((nao["situacao"] == "igual").all())
        self.assertTrue((self.uf.loc[self.uf["competencia"].isin(rev)].groupby("competencia")["situacao"]
                         .apply(lambda s: (s != "igual").any())).all())

    def test_tabela_uf_recalculada_dos_paineis(self) -> None:
        # soma independente: municípios + ignorado da UF, por UF × mês × grupo, nas duas safras
        for safra, d in (("v1", ROOT / "output" / "aquisicao" / "sih"), ("v2", SIH_V2)):
            p = pd.read_parquet(d / "painel_sih_municipio_mes_grupo.parquet", columns=["uf", "competencia", "grupo", "aih_aprovadas"])
            i = pd.read_parquet(d / "ignorados_sih_uf_mes_grupo.parquet", columns=["uf", "competencia", "grupo", "aih_aprovadas"])
            x = pd.concat([p, i[i["uf"] != "00"]])
            g = x.groupby(["uf", "competencia", "grupo"])["aih_aprovadas"].sum(min_count=1)
            t = self.uf.set_index(["uf", "competencia", "grupo"])[f"aih_{safra}"]
            ok = t.dropna()
            self.assertTrue((g.reindex(ok.index).astype(float) == ok.astype(float)).all(), safra)

    def test_total_mensal_igual_as_validacoes_e_ao_a15(self) -> None:
        v2 = json.loads((SIH_V2 / "a13_validacoes.json").read_text(encoding="utf-8"))
        for r in self.mes.itertuples(index=False):
            self.assertEqual(r.aih_total_v2, v2["por_competencia"][r.competencia]["total_aih_por_grupo"]["total"])
        self.assertEqual(self.res["conferencia_com_a15"]["meses_diferentes"], [])

    def test_verificar_sem_rede(self) -> None:
        A13B.redirecionar()
        with mock.patch("urllib.request.urlopen", side_effect=AssertionError("rede proibida")):
            self.assertEqual(A13B.verificar(), 0)


@unittest.skipUnless((SIA_V2 / "manifesto_sia.json").exists(), "safra v2 do SIA ausente")
class TestSafraV2SIA(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.man = json.loads((SIA_V2 / "manifesto_sia.json").read_text(encoding="utf-8"))
        cls.res = json.loads((SIA_V2 / "comparacao_v2_v1_resumo.json").read_text(encoding="utf-8"))
        cls.mes = pd.read_csv(SIA_V2 / "comparacao_v2_v1_mes_conjunto.csv", dtype={"competencia_processamento": str})

    def test_meses_esquema_e_empirico(self) -> None:
        self.assertEqual(self.man["competencias_obtidas"], A12B.COMPETENCIAS_V2)
        self.assertEqual(self.man["safra"]["meses"], A12B.COMPETENCIAS_V2)
        self.assertEqual(pq.read_schema(SIA_V2 / "painel_sia_municipio_mes_subgrupo_cbo.parquet").names,
                         pq.read_schema(ROOT / "output" / "aquisicao" / "sia" / "painel_sia_municipio_mes_subgrupo_cbo.parquet").names)
        for q in self.man["consultas"]["lista"]:
            self.assertLess(q["competencia"], "202609")
            self.assertGreaterEqual(q["competencia"], "202509")
            self.assertEqual(q["status"], "ok")
        for k, v in self.man["validacoes"].items():
            self.assertIn(v["status"], ("APROVADO", "RELATO"), k)

    def test_comparacao_coerente(self) -> None:
        cel = pd.read_parquet(SIA_V2 / "comparacao_v2_v1_celulas_diferentes.parquet")
        self.assertEqual(len(cel), int(self.mes["celulas_diferentes"].sum()))
        self.assertEqual(self.res["celulas_diferentes"], len(cel))
        self.assertEqual(set(cel["natureza_dos_dados"]) | {"EMPIRICO"}, {"EMPIRICO"})
        rev = sorted(self.mes.loc[self.mes["celulas_diferentes"] > 0, "competencia_processamento"].unique())
        self.assertEqual(rev, self.res["meses_com_revisao"])

    def test_quantidade_v1_recalculada_do_painel_v1(self) -> None:
        painel_v1 = ROOT / "output" / "aquisicao" / "sia" / "painel_sia_municipio_mes_subgrupo_cbo.parquet"
        alvo = self.mes.set_index(["competencia_processamento", "conjunto_cbo"])["qtd_v1"]
        for comp in A12B.COMPETENCIAS_V2[:2] + A12B.COMPETENCIAS_V2[-1:]:
            t = pq.read_table(painel_v1, columns=["conjunto_cbo", "qtd_aprovada"],
                              filters=[("competencia_processamento", "=", comp)])
            g = t.to_pandas().assign(conjunto_cbo=lambda d: d["conjunto_cbo"].astype(str)).groupby("conjunto_cbo")["qtd_aprovada"].sum()
            for conj, q in g.items():
                self.assertEqual(int(q), int(alvo[(comp, conj)]), (comp, conj))

    def test_verificar_sem_rede(self) -> None:
        A12B.redirecionar()
        with mock.patch("urllib.request.urlopen", side_effect=AssertionError("rede proibida")):
            self.assertEqual(A12B.verificar(), 0)


class TestDocumento(unittest.TestCase):
    def test_documento_de_auditoria(self) -> None:
        self.assertTrue(DOC.exists())
        texto = DOC.read_text(encoding="utf-8")
        for k in ("a13b_safra_v2_sih.py", "a12b_safra_v2_sia.py", "EMPIRICO", "§12.1"):
            self.assertIn(k, texto)

    def _bloco(self, texto: str, nome: str) -> str:
        ini, fim = f"<!-- {nome} -->", f"<!-- /{nome} -->"
        return texto.split(ini, 1)[1].split(fim, 1)[0].strip()

    @unittest.skipUnless((SIH_V2 / "comparacao_v2_v1_resumo.json").exists()
                         and (SIA_V2 / "comparacao_v2_v1_resumo.json").exists(), "safras v2 ausentes")
    def test_listas_do_documento_conferem_com_as_saidas(self) -> None:
        texto = DOC.read_text(encoding="utf-8")
        sih = json.loads((SIH_V2 / "comparacao_v2_v1_resumo.json").read_text(encoding="utf-8"))["meses_revisados"]
        sia = json.loads((SIA_V2 / "comparacao_v2_v1_resumo.json").read_text(encoding="utf-8"))["meses_com_revisao"]
        self.assertEqual(self._bloco(texto, "sih_meses_revisados"), ", ".join(sih) or "Nenhum.")
        self.assertEqual(self._bloco(texto, "sia_meses_revisados"), ", ".join(sia) or "Nenhum.")


if __name__ == "__main__":
    unittest.main()
