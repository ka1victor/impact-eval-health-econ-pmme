"""Testes do painel CNES nacional município × grupo de CBO × mês (a09).

Os testes de artefato leem só saídas versionadas (painel, manifesto e
validação); o cache mensal e os ZIPs ficam fora do Git. O teste da agregação
usa um mini-cadastro SINTÉTICO, inventado, que não representa nenhum município.
Nenhum teste lê IVS além da lista de municípios do universo.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "aquisicao" / "a09_adquirir_cnes_nacional.py"
SPEC = importlib.util.spec_from_file_location("cnes_nacional_a09", SCRIPT)
A09 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(A09)

PAINEL = ROOT / "output" / "aquisicao" / "cnes_nacional" / "painel_municipio_cbo_mes.parquet"
MANIFESTO = ROOT / "output" / "aquisicao" / "a09_manifesto_cnes_nacional.json"
VALIDACAO = ROOT / "output" / "aquisicao" / "cnes_nacional" / "a09_validacao_painel_ciclo1.json"
COLUNAS = [
    "co_ibge", "competencia", "grupo", "n_vinculos", "n_vinculos_sus", "n_profissionais_distintos",
    "horas_sus_semanais", "horas_sus_semanais_parcial",
    "horas_totais_amb_hosp", "horas_totais", "horas_totais_parcial",
    "n_vinculos_horas_ausentes", "tem_profissional", "natureza_dos_dados",
]
METRICAS = COLUNAS[3:13]
HORAS_PRINCIPAIS = {  # coluna principal -> coluna parcial (sensibilidade, protocolo 40 §16)
    "horas_sus_semanais": "horas_sus_semanais_parcial",
    "horas_totais": "horas_totais_parcial",
}


class TestPlanoDeCompetencias(unittest.TestCase):
    def test_nenhuma_competencia_do_ciclo3(self) -> None:
        self.assertTrue(all(c < "202609" for c in A09.COMPETENCIAS))
        with self.assertRaises(RuntimeError):
            A09.checar_limite("202609")

    def test_grade_planejada(self) -> None:
        self.assertEqual(A09.COMPETENCIAS_MENSAIS[0], "202406")
        self.assertEqual(A09.COMPETENCIAS_MENSAIS[-1], "202608")
        self.assertEqual(len(A09.COMPETENCIAS_MENSAIS), 27)
        self.assertEqual(
            A09.COMPETENCIAS_TRIMESTRAIS,
            ["202201", "202204", "202207", "202210", "202301", "202304", "202307", "202310", "202401", "202404"],
        )
        # adendo §13 (S5): meses extras antes de todas as políticas nos mesmos cortes
        self.assertEqual(A09.COMPETENCIAS_PRE_ADICIONAIS, ["202302", "202303"])
        self.assertEqual(len(A09.COMPETENCIAS), len(set(A09.COMPETENCIAS)))


class TestAgregacaoSintetica(unittest.TestCase):
    """Mini-cadastro SINTÉTICO: dois municípios fictícios e códigos de profissional inventados."""

    def setUp(self) -> None:
        self.alvo = ["225120", "225151", "225225"]
        self.df = pd.DataFrame({
            "co_municipio": ["999991", "999991", "999991", "999991", "999992", "999992", None, "999992", "999993", "999993"],
            "co_profissional_sus": ["P1", "P1", "P2", "P3", "P4", "", "P9", "P5", "P6", "P7"],
            "co_cbo": ["225151", "225225", "225125", "225133", "225142", "225151", "225151", "225130", "225120", "225120"],
            "qt_ch_ambulatorial": pd.array([10, 5, 20, 4, 40, 8, 1, 30, 20, 10], dtype="Int32"),
            "qt_ch_hosp_sus": pd.array([2, 0, 0, 0, 0, 0, 1, 0, 0, 0], dtype="Int32"),
            # 999993: um vínculo com 'outros' ausente (SUS observado) e, em cbo_225120, nada mais
            "qt_ch_outros": pd.array([1, 0, 0, 6, 0, 0, 1, 0, None, 0], dtype="Int32"),
            "tp_sus_nao_sus": ["S", "N", "S", "S", "S", "S", "S", "S", "S", "S"],
        })
        self.df_sus_ausente = self.df.copy()
        self.df_sus_ausente["qt_ch_hosp_sus"] = pd.array([2, 0, 0, 0, 0, 0, 1, 0, 0, None], dtype="Int32")
        self.agg = A09.agregar_mes(self.df, self.alvo).set_index(["co_municipio", "grupo"])

    def test_uniao_conta_pessoa_uma_vez(self) -> None:
        r = self.agg.loc[("999991", "alvo_pmme")]
        self.assertEqual(r["n_vinculos"], 2)
        self.assertEqual(r["n_profissionais_distintos"], 1)
        self.assertEqual(r["horas_totais_amb_hosp"], 17)
        self.assertEqual(r["horas_totais"], 18)

    def test_horas_sus_so_vinculos_sus(self) -> None:
        # o vínculo 225225 do P1 é não SUS ('N'): fica fora das horas SUS (§16)
        r = self.agg.loc[("999991", "alvo_pmme")]
        self.assertEqual(r["n_vinculos_sus"], 1)
        self.assertEqual(r["horas_sus_semanais"], 12)
        self.assertEqual(r["horas_sus_semanais_parcial"], 12)
        self.assertEqual(self.agg.loc[("999991", "cbo_225225"), "horas_sus_semanais"], 0)
        self.assertEqual(self.agg.loc[("999991", "cbo_225225"), "horas_totais_amb_hosp"], 5)

    def test_sem_residentes(self) -> None:
        df = self.df.copy()
        df.loc[3, "co_cbo"] = "2231F9"
        agg = A09.agregar_mes(df, self.alvo).set_index(["co_municipio", "grupo"])
        self.assertEqual(agg.loc[("999991", "todos_medicos"), "n_vinculos"], 4)
        self.assertEqual(agg.loc[("999991", "todos_medicos_sem_residentes"), "n_vinculos"], 3)
        self.assertEqual(agg.loc[("999991", "todos_medicos_sem_residentes"), "n_profissionais_distintos"], 2)

    def test_grupos_disjuntos(self) -> None:
        self.assertEqual(self.agg.loc[("999991", "generalistas"), "n_profissionais_distintos"], 1)
        self.assertEqual(self.agg.loc[("999991", "especialistas_nao_alvo"), "n_profissionais_distintos"], 1)
        self.assertEqual(self.agg.loc[("999991", "todos_medicos"), "n_profissionais_distintos"], 3)
        self.assertEqual(self.agg.loc[("999991", "todos_medicos"), "n_vinculos"], 4)

    def test_mfc_em_grupo_proprio_e_no_nao_alvo(self) -> None:
        self.assertEqual(self.agg.loc[("999992", "mfc_225130"), "n_profissionais_distintos"], 1)
        self.assertEqual(self.agg.loc[("999992", "especialistas_nao_alvo"), "n_profissionais_distintos"], 1)
        self.assertNotIn(("999992", "mfc_225130"), [(m, g) for m, g in self.agg.index if g == "generalistas"])
        self.assertEqual(self.agg.loc[("999992", "generalistas"), "n_profissionais_distintos"], 1)

    def test_hora_ausente_nao_vira_zero(self) -> None:
        r = self.agg.loc[("999993", "cbo_225120")]
        self.assertEqual(r["n_vinculos_horas_ausentes"], 1)
        self.assertEqual(r["horas_sus_semanais"], 30)  # só 'outros' ausente: soma SUS observada
        self.assertTrue(pd.isna(r["horas_totais"]))
        self.assertEqual(r["horas_totais_parcial"], 30)
        agg2 = A09.agregar_mes(self.df_sus_ausente, self.alvo).set_index(["co_municipio", "grupo"])
        r2 = agg2.loc[("999993", "cbo_225120")]
        self.assertEqual(r2["n_vinculos_horas_ausentes"], 2)
        self.assertTrue(pd.isna(r2["horas_sus_semanais"]))
        self.assertTrue(pd.isna(r2["horas_totais_amb_hosp"]))
        self.assertTrue(pd.isna(r2["horas_totais"]))
        self.assertEqual(r2["horas_sus_semanais_parcial"], 30)  # 20 + 10 observadas; o branco não vira número
        self.assertEqual(r2["horas_totais_parcial"], 30)
        self.assertEqual(self.agg.loc[("999991", "alvo_pmme"), "n_vinculos_horas_ausentes"], 0)

    def test_hora_em_branco_de_vinculo_nao_sus_nao_anula_horas_sus(self) -> None:
        df = self.df_sus_ausente.copy()
        df.loc[9, "tp_sus_nao_sus"] = "N"
        r = A09.agregar_mes(df, self.alvo).set_index(["co_municipio", "grupo"]).loc[("999993", "cbo_225120")]
        self.assertEqual(r["horas_sus_semanais"], 20)
        self.assertTrue(pd.isna(r["horas_totais_amb_hosp"]))

    def test_id_vazio_e_sem_municipio(self) -> None:
        r = self.agg.loc[("999992", "cbo_225151")]
        self.assertEqual(r["n_vinculos"], 1)
        self.assertEqual(r["n_profissionais_distintos"], 0)
        self.assertNotIn(None, set(self.agg.index.get_level_values(0)))


@unittest.skipUnless(PAINEL.exists() and MANIFESTO.exists(), "painel a09 ausente")
class TestPainelNacional(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.painel = pd.read_parquet(PAINEL)
        cls.man = json.loads(MANIFESTO.read_text(encoding="utf-8"))
        cls.universo = A09.carregar_universo()
        cls.alvo, _, _ = A09.carregar_ponte()

    def test_esquema(self) -> None:
        self.assertEqual(list(self.painel.columns), COLUNAS)
        self.assertTrue(self.painel["co_ibge"].str.fullmatch(r"\d{6}").all())
        self.assertTrue(self.painel["competencia"].str.fullmatch(r"20\d{4}").all())

    def test_unicidade(self) -> None:
        self.assertFalse(self.painel.duplicated(["co_ibge", "competencia", "grupo"]).any())

    def test_balanceado(self) -> None:
        comps = sorted(self.painel["competencia"].unique())
        grupos = A09.grupos_do_cbo(self.alvo)
        self.assertEqual(sorted(self.painel["grupo"].unique()), sorted(grupos))
        self.assertEqual(sorted(self.painel["co_ibge"].unique()), self.universo)
        self.assertEqual(len(self.painel), len(self.universo) * len(comps) * len(grupos))
        self.assertEqual(comps, self.man["competencias_obtidas"])

    def test_competencias(self) -> None:
        comps = set(self.painel["competencia"].unique())
        self.assertTrue(all(c < "202609" for c in comps))
        self.assertTrue(comps <= set(A09.COMPETENCIAS))
        self.assertIn("202406", comps)
        self.assertIn("202506", comps)

    def test_nao_negativo_e_coerente(self) -> None:
        p = self.painel
        for col in METRICAS:
            self.assertTrue((p[col].dropna() >= 0).all(), col)
        self.assertTrue((p["tem_profissional"] == (p["n_profissionais_distintos"] >= 1).astype(int)).all())
        for maior, menor in (("horas_totais", "horas_totais_amb_hosp"), ("horas_totais_amb_hosp", "horas_sus_semanais"),
                             ("horas_totais_parcial", "horas_sus_semanais_parcial")):
            ambos = p[maior].notna() & p[menor].notna()
            self.assertTrue((p.loc[ambos, maior] >= p.loc[ambos, menor]).all(), (maior, menor))
        self.assertTrue((p["n_vinculos_sus"] <= p["n_vinculos"]).all())
        self.assertTrue((p["n_vinculos"] >= p["n_profissionais_distintos"]).all())

    def test_regra_de_horas_ausentes(self) -> None:
        p = self.painel
        self.assertTrue((p["n_vinculos_horas_ausentes"] <= p["n_vinculos"]).all())
        # horas_totais ausente exatamente quando algum vínculo tem hora ausente
        self.assertTrue((p["horas_totais"].isna() == (p["n_vinculos_horas_ausentes"] > 0)).all())
        # horas SUS ausente só onde há vínculo com hora ausente
        self.assertFalse((p["horas_sus_semanais"].isna() & (p["n_vinculos_horas_ausentes"] == 0)).any())
        self.assertFalse((p["horas_totais_amb_hosp"].isna() & (p["n_vinculos_horas_ausentes"] == 0)).any())
        # parciais nunca são ausentes e coincidem com a principal quando ela existe
        for principal, parcial in HORAS_PRINCIPAIS.items():
            self.assertFalse(p[parcial].isna().any(), parcial)
            ok = p[principal].notna()
            self.assertTrue((p.loc[ok, principal] == p.loc[ok, parcial]).all(), principal)
        # célula sem vínculo: zeros observados, nunca ausente
        vazias = p["n_vinculos"] == 0
        self.assertTrue((p.loc[vazias, ["horas_sus_semanais", "horas_totais"]] == 0).all().all())

    def test_contagem_de_horas_ausentes_bate_com_manifesto(self) -> None:
        tm = self.painel.loc[self.painel["grupo"] == "todos_medicos"]
        por_mes = tm.groupby("competencia")["n_vinculos_horas_ausentes"].sum()
        for comp, n in por_mes.items():
            reg = self.man["horas_ausentes_por_competencia"][comp]
            self.assertEqual(reg["por_campo"].keys(), {"QT_CARGA_HORARIA_AMBULATORIAL", "QT_CARGA_HOR_HOSP_SUS",
                                                       "QT_CARGA_HORARIA_OUTROS"})
            # o painel só cobre o universo do a08: no máximo o total nacional do mês
            self.assertLessEqual(n, reg["vinculos_medicos_com_alguma_hora_ausente"], comp)
            self.assertEqual(self.man["por_competencia"][comp]["versao_extracao"], A09.VERSAO_EXTRACAO)

    def test_agregados(self) -> None:
        w = self.painel.pivot_table(index=["co_ibge", "competencia"], columns="grupo",
                                    values=["n_vinculos", "n_profissionais_distintos"], aggfunc="sum")
        cbo_cols = [f"cbo_{c}" for c in self.alvo]
        v = w["n_vinculos"]
        self.assertTrue((v[cbo_cols].sum(axis=1) == v["alvo_pmme"]).all())
        soma = v["alvo_pmme"] + v["generalistas"] + v["especialistas_nao_alvo"]
        self.assertTrue((v["todos_medicos"] >= soma).all())
        n = w["n_profissionais_distintos"]
        self.assertTrue((n["alvo_pmme"] <= n[cbo_cols].sum(axis=1)).all())
        self.assertTrue((n["alvo_pmme"] >= n[cbo_cols].max(axis=1)).all())
        self.assertTrue((n["todos_medicos"] >= n["alvo_pmme"]).all())
        self.assertTrue((n["especialistas_nao_alvo"] >= n["mfc_225130"]).all())
        self.assertTrue((v["todos_medicos"] >= v["todos_medicos_sem_residentes"]).all())
        self.assertTrue((n["todos_medicos"] >= n["todos_medicos_sem_residentes"]).all())
        self.assertTrue((v["especialistas_nao_alvo"] >= v["mfc_225130"]).all())

    def test_natureza_empirica(self) -> None:
        self.assertEqual(set(self.painel["natureza_dos_dados"].unique()), {"EMPIRICO"})
        self.assertEqual(self.man["natureza_dos_dados"], "EMPIRICO")

    def test_coerencia_com_manifesto(self) -> None:
        tm = self.painel.loc[self.painel["grupo"] == "todos_medicos"]
        por_mes = tm.groupby("competencia")["tem_profissional"].sum()
        for comp, n in por_mes.items():
            reg = self.man["por_competencia"][comp]
            self.assertLessEqual(n, reg["municipios_distintos"], comp)

    def test_manifesto(self) -> None:
        self.assertEqual(self.man["gerador"], "scripts/aquisicao/a09_adquirir_cnes_nacional.py")
        for comp in self.man["competencias_obtidas"]:
            reg = self.man["por_competencia"][comp]
            self.assertTrue(re.fullmatch(r"[0-9a-f]{64}", reg["sha256_zip"]), comp)
            self.assertGreater(reg["bytes_zip"], 0)
            self.assertGreaterEqual(reg["linhas_vinculos_medicos"], A09.MIN_VINCULOS_MEDICOS_MES)
            self.assertIn("tbCargaHorariaSus", reg["membros_lidos"]["carga"])
        self.assertTrue(all(c < "202609" for c in self.man["por_competencia"]))
        self.assertEqual(self.man["painel"]["sha256"], A09.sha256_arquivo(PAINEL))

    def test_df_so_530010(self) -> None:
        self.assertFalse(self.painel["co_ibge"].str.match(r"53").pipe(
            lambda m: m & (self.painel["co_ibge"] != A09.DF_MUNICIPIO)).any())
        self.assertIn("portao_df", self.man["painel"])

    def test_rotulos_empiricos(self) -> None:
        rot = pd.read_csv(ROOT / "output" / "aquisicao" / "cnes_nacional" / "a09_rotulos_cbo_medicos.csv", dtype=str)
        self.assertEqual(set(rot["natureza_dos_dados"]), {"EMPIRICO"})
        self.assertIn("2231F9", set(rot["co_cbo"]))

    def test_tamanho_versionado(self) -> None:
        self.assertLess(PAINEL.stat().st_size, 50 * 1024**2)


class TestPortaoFailClosedSintetico(unittest.TestCase):
    """Portão reprovado (validação SINTÉTICA forçada): nada é gravado nos caminhos de saída."""

    def test_reprovado_nao_grava(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            t = Path(tmp)
            alvos = {nome: t / f"{nome}.out" for nome in
                     ("PAINEL_FILE", "VALIDACAO_FILE", "ROTULOS_FILE", "MANIFESTO_FILE", "RESUMO_FILE")}
            painel = pd.DataFrame({"co_ibge": ["999991"], "natureza_dos_dados": ["EMPIRICO"]})
            reprovado = {"status": "REPROVADO", "fracao_celulas_identicas": 0.5, "por_competencia": []}
            with mock.patch.multiple(A09, **alvos), \
                    mock.patch.object(A09, "ler_registros", return_value={"202406": {"status": "adquirido_extraido_zip_apagado"}}), \
                    mock.patch.object(A09, "consolidar_rotulos", return_value=pd.DataFrame(columns=["co_cbo", "ds_cbo"])), \
                    mock.patch.object(A09, "construir_painel", return_value=(painel, {})), \
                    mock.patch.object(A09, "validar_contra_ciclo1", return_value=reprovado), \
                    mock.patch.object(sys, "argv", ["a09", "--etapa", "painel"]):
                codigo = A09.main()
            self.assertEqual(codigo, 2)
            self.assertEqual(list(t.iterdir()), [])

    def test_portao_df(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp)
            df = pd.DataFrame({
                "competencia": ["202406"], "co_municipio": ["530020"], "co_profissional_sus": ["P1"],
                "co_cbo": ["225125"], "qt_ch_ambulatorial": pd.array([1], dtype="Int32"),
                "qt_ch_hosp_sus": pd.array([0], dtype="Int32"), "qt_ch_outros": pd.array([0], dtype="Int32"),
                "tp_sus_nao_sus": ["S"],
            })
            df.to_parquet(cache / "c.parquet")
            (cache / "m.json").write_text(json.dumps({"versao_extracao": A09.VERSAO_EXTRACAO}))
            with mock.patch.object(A09, "caminho_cache", return_value=cache / "c.parquet"), \
                    mock.patch.object(A09, "caminho_meta", return_value=cache / "m.json"):
                with self.assertRaisesRegex(RuntimeError, "DF"):
                    A09.construir_painel(["202406"])


@unittest.skipUnless(VALIDACAO.exists(), "validação a09 ausente")
class TestValidacaoCiclo1(unittest.TestCase):
    def test_painel_ciclo1_reproduzido(self) -> None:
        v = json.loads(VALIDACAO.read_text(encoding="utf-8"))
        self.assertEqual(v["status"], "APROVADO")
        self.assertEqual(v["tolerancia_teste"], A09.TOLERANCIA_VALIDACAO)
        self.assertTrue(v["competencias_comparadas"])
        self.assertGreaterEqual(v["fracao_celulas_identicas"], v["tolerancia_teste"]["fracao_celulas_identicas_min"])
        self.assertLessEqual(abs(v["dif_relativa_soma"]), v["tolerancia_teste"]["dif_relativa_soma_max"])


if __name__ == "__main__":
    unittest.main()
