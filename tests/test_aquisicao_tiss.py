"""Testes da aquisição TISS/ANS (a14): produção paga por planos por município do prestador.

Dois blocos:
- funções puras em dados SINTÉTICOS, inventados em memória (eventos, itens e
  municípios fictícios), que não representam nenhum prestador nem operadora;
- artefatos versionados em ``output/aquisicao/tiss/`` (painéis, manifesto,
  cobertura, validação e resumo), conferidos contra o manifesto e entre si.

Nenhum teste lê IVS nem quebra nada por faixa, lado de corte ou tratamento.
"""

from __future__ import annotations

import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "aquisicao" / "a14_adquirir_tiss_ans.py"
SPEC = importlib.util.spec_from_file_location("tiss_a14", SCRIPT)
A14 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(A14)

OUT = ROOT / "output" / "aquisicao" / "tiss"
DOC = ROOT / "docs" / "auditorias" / "aquisicao" / "A14_tiss_ans.md"
STATUS_AUSENTES = {"ausente_nao_processado", "ausente_arquivo_nao_publicado", "ausente_falha_download",
                   "ausente_falha_leitura_ou_validacao"}

# ---------------------------------------------------------------- dados sintéticos

ALVO_SINT = A14.A09.carregar_ponte()[0]
CBO_ALVO = ALVO_SINT[0]
UF_SINT = "AC"
MUN_A, MUN_B, MUN_OUTRA_UF = "120001", "120002", "130001"  # códigos fictícios
VALIDOS_SINT = {MUN_A, MUN_B, MUN_OUTRA_UF}
PREFIXOS_SINT = {"AC": "12", "AM": "13"}


def _cons_sintetico(base: str = "AMB") -> pa.Table:
    """Eventos SINTÉTICOS: 1–3 válidos em MUN_A, 4 em MUN_B, 5 sem município, 6 inválido,
    7 de outra UF, 8 com mês divergente, 9 de operadora odontológica, 10 sem item DET."""
    mes = "DT_REALIZACAO" if base == "AMB" else "ANO_MES_EVENTO"
    d = {
        "ID_EVENTO_ATENCAO_SAUDE": [str(i) for i in range(1, 11)],
        "CD_MODALIDADE": ["22"] * 8 + ["26", "22"],
        "CD_MUNICIPIO_PRESTADOR": [MUN_A, MUN_A, MUN_A, MUN_B, "", "999999", MUN_OUTRA_UF, MUN_A, MUN_A, MUN_B],
        "UF_PRESTADOR": [UF_SINT] * 10,
        mes: ["2025-10"] * 7 + ["2025-09", "2025-10", "2025-10"],
    }
    if base == "AMB":
        d["CBO"] = [CBO_ALVO, "225125", "", "225130", CBO_ALVO, CBO_ALVO, CBO_ALVO, CBO_ALVO, "223208", "2231F9"]
    return pa.table({k: pa.array(v, pa.string()) for k, v in d.items()})


def _det_sintetico(base: str = "AMB") -> pa.RecordBatch:
    mes = "DT_REALIZACAO" if base == "AMB" else "ANO_MES_EVENTO"
    linhas = [  # (id, tabela, código, quantidade, pacote, própria)
        ("1", "22", "10101012", "1", "0", "0"),     # consulta
        ("1", "22", "10101012", "1", "0", "0"),     # 2ª consulta no mesmo evento: evento conta 1 vez
        ("1", "22", "40301010", "2", "0", "0"),     # exame
        ("2", "22", "30101018", "1,5", "0", "0"),   # cirúrgico, vírgula decimal
        ("2", "63", "009", "3", "0", "0"),          # agrupado TUSS 63
        ("3", "22", "40301010", "", "1", "0"),      # exame com quantidade vazia (item de pacote)
        ("4", "98", "PCT1", "1", "0", "0"),         # pacote
        ("4", "22", "81000030", "1", "0", "0"),     # odontologia TUSS 22: fora das contagens médicas
        ("5", "22", "10101012", "1", "0", "0"),
        ("6", "22", "10101012", "1", "0", "0"),
        ("7", "22", "10101012", "1", "0", "0"),
        ("8", "22", "10101012", "1", "0", "0"),
        ("9", "22", "81000030", "1", "0", "0"),
        ("99", "22", "10101012", "1", "0", "0"),    # ID sem evento no CONS
    ]
    cols = ["ID_EVENTO_ATENCAO_SAUDE", "CD_TABELA_REFERENCIA", "CD_PROCEDIMENTO", "QT_ITEM_EVENTO_INFORMADO",
            "IND_PACOTE", "IND_TABELA_PROPRIA"]
    d = {c: [r[i] for r in linhas] for i, c in enumerate(cols)}
    d[mes] = ["2025-10"] * len(linhas)
    return pa.RecordBatch.from_pydict({k: pa.array(v, pa.string()) for k, v in d.items()})


def _agregar(base: str = "AMB", det: list | None = None):
    lotes = det if det is not None else [_det_sintetico(base)]
    return A14.agregar_pacote(base, UF_SINT, "202510", _cons_sintetico(base), lotes, ALVO_SINT, VALIDOS_SINT,
                              PREFIXOS_SINT)


def _celula(agg: pd.DataFrame, **filtro) -> pd.DataFrame:
    m = pd.Series(True, index=agg.index)
    for k, v in filtro.items():
        m &= agg[k] == v
    return agg.loc[m]


class TestPlano(unittest.TestCase):
    def test_competencias_e_limite(self) -> None:
        self.assertEqual(A14.COMPETENCIAS[0], "202201")
        self.assertEqual(A14.COMPETENCIAS[-1], "202512")
        self.assertEqual(len(A14.COMPETENCIAS), 48)
        self.assertTrue(all(c < "202601" for c in A14.COMPETENCIAS))
        for c in ("202601", "202609", "202112"):
            with self.assertRaises(RuntimeError):
                A14.checar_limite(c)
        A14.checar_limite("202512")

    def test_prioridade_do_protocolo_primeiro(self) -> None:
        esperado = [f"2024{m:02d}" for m in range(6, 13)] + [f"2025{m:02d}" for m in range(1, 7)] + ["202510", "202511", "202512"]
        self.assertEqual(A14.PRIORIDADE_1, esperado)
        ordem = A14.plano_pacotes(["AMB"], ["AC"], A14.COMPETENCIAS)
        self.assertEqual([c for _, _, c in ordem[:16]], esperado)
        self.assertEqual(sorted(A14.PRIORIDADE_1 + A14.PRIORIDADE_2), A14.COMPETENCIAS)

    def test_nao_le_ivs(self) -> None:
        fonte = SCRIPT.read_text(encoding="utf-8")
        for proibido in ("a08_", "ivs_ipea", "ivs_2010", "escore", "faixa_bolsa", "lado_corte"):
            self.assertNotIn(proibido, fonte.lower())


class TestClassificacaoCBO(unittest.TestCase):
    def test_grupos_vem_do_a09(self) -> None:
        fonte = SCRIPT.read_text(encoding="utf-8")
        # nenhuma lista de CBO redigitada: generalistas, MFC e prefixos vêm do a09
        for cod in ("225125", "225142", "225170", "\"225130\"", "\"2251\"", "\"2231\""):
            self.assertNotIn(cod, fonte)
        self.assertIn("A09.agregar_mes", fonte)

    def test_particao_sintetica(self) -> None:
        cods = [CBO_ALVO, "225130", "225125", "225142", "225170", "225112", "2231F9", "223208", "", "2232",
                "251510", " 225-125 "]
        esperado = ["alvo_pmme", "mfc_225130", "generalistas", "generalistas", "generalistas",
                    "especialistas_nao_alvo_exceto_mfc", "outros_medicos", "nao_medicos", "cbo_ausente",
                    "nao_medicos", "nao_medicos", "generalistas"]
        self.assertEqual(list(A14.classificar_cbo(cods, ALVO_SINT)), esperado)

    def test_igual_ao_a09_em_todos_os_cbo_medicos_da_ponte(self) -> None:
        """Para cada CBO, a partição do a14 reproduz os grupos do a09 (agregar_mes)."""
        cods = list(ALVO_SINT) + list(A14.A09.GENERALISTAS) + [A14.A09.MFC, "225112", "225285", "2231F9"]
        part = dict(zip(cods, A14.classificar_cbo(cods, ALVO_SINT)))
        grupos = A14.grupos_a09_por_cbo(cods, ALVO_SINT)
        for c in cods:
            saida = {g for g, ps in A14.GRUPOS_SAIDA_AMB.items() if part[c] in ps} - {"todos_cbo", "outros_medicos",
                                                                                         "nao_medicos", "cbo_ausente"}
            a09 = {g for g in grupos[c] if g in A14.GRUPOS_SAIDA_AMB}
            self.assertEqual(saida, a09, c)

    def test_grupos_de_saida(self) -> None:
        g = A14.GRUPOS_SAIDA_AMB
        self.assertIn("mfc_225130", g["especialistas_nao_alvo"])  # regra do a09: MFC contida no não alvo
        particao = set(A14.PARTICOES_CBO) - {"sem_cbo_na_fonte"}
        self.assertEqual(set(g["todos_cbo"]), particao)


class TestClassificacaoItens(unittest.TestCase):
    def test_categorias(self) -> None:
        tab = pa.array(["22", "22", "22", "22", "22", "22", "63", "0", "98", "19", "22", "22", "90", "22", "00"])
        proc = pa.array(["10101012", "40301010", "30101018", "20101015", "81000030", "1010101", "009", "X", "P1",
                         "123", "50000012", "10102019", "P2", "10101039", "Y"])
        prop = pa.array(["0"] * 7 + ["1"] + ["0"] * 6 + ["0"])
        cat = [A14.CATEGORIAS[i] for i in A14.classificar_itens(tab, proc, prop)]
        self.assertEqual(cat, [
            "consultas", "exames", "cirurgicos", "outros_tuss22", "odontologia_tuss22", "outra_tabela_ou_invalido",
            "agrupados_tuss63", "pacote_ou_tabela_propria", "pacote_ou_tabela_propria", "materiais_medicamentos_taxas",
            "outros_tuss22", "consultas", "pacote_ou_tabela_propria", "consultas", "outra_tabela_ou_invalido"])

    def test_tabela_propria_vence_tabela_22(self) -> None:
        cat = A14.classificar_itens(pa.array(["22"]), pa.array(["10101012"]), pa.array(["1"]))
        self.assertEqual(A14.CATEGORIAS[cat[0]], "pacote_ou_tabela_propria")

    def test_normalizacao_de_codigo(self) -> None:
        self.assertEqual(A14.normalizar_codigo(pa.array(["0", "00", "22", " 63 ", "", "1", "001"]), 3).to_pylist(),
                         ["000", "000", "022", "063", "", "001", "001"])

    def test_odontologia_fora_dos_tipos_medicos(self) -> None:
        for tipo, cats in A14.TIPOS_PAINEL.items():
            self.assertNotIn("odontologia_tuss22", cats, tipo)
        self.assertEqual(set(A14.TIPOS_PAINEL["todos_nao_odonto"]), set(A14.CATEGORIAS) - {"odontologia_tuss22"})
        self.assertTrue(set(A14.TIPOS_PAINEL["agrupados_tuss63"]) <= set(A14.TIPOS_PAINEL["outros"]))

    def test_quantidade_vazia_nao_vira_zero(self) -> None:
        val, vazio, nao_num = A14.converter_quantidade(pa.array(["1", "2,5", "", "abc", "-1", None]))
        self.assertEqual(list(vazio), [False, False, True, False, False, True])
        self.assertEqual(list(nao_num), [False, False, False, True, False, False])
        self.assertTrue(np.isnan(val[[2, 3, 5]]).all())
        self.assertEqual(list(val[[0, 1, 4]]), [1.0, 2.5, -1.0])


class TestAgregacaoSintetica(unittest.TestCase):
    """Par CONS/DET SINTÉTICO de uma UF × mês fictícia."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.agg, cls.diag = _agregar("AMB")

    def test_evento_conta_uma_vez_por_tipo(self) -> None:
        c = _celula(self.agg, status_municipio="ok", co_ibge=MUN_A, particao_cbo="alvo_pmme", nivel="painel",
                    tipo="consultas", operadora_odontologica=False)
        self.assertEqual(int(c["n_eventos"].sum()), 1)   # evento 1 tem duas linhas de consulta
        self.assertEqual(float(c["qt_itens"].sum()), 2.0)
        self.assertEqual(int(c["n_linhas_det"].sum()), 2)

    def test_tipos_e_quantidades(self) -> None:
        g = _celula(self.agg, status_municipio="ok", co_ibge=MUN_A, particao_cbo="generalistas", nivel="painel",
                    operadora_odontologica=False).set_index("tipo")
        self.assertEqual(float(g.loc["cirurgicos", "qt_itens"]), 1.5)
        self.assertEqual(int(g.loc["outros", "n_eventos"]), 1)
        self.assertEqual(int(g.loc["agrupados_tuss63", "n_eventos"]), 1)
        self.assertEqual(int(g.loc["todos_nao_odonto", "n_eventos"]), 1)
        self.assertEqual(float(g.loc["todos_nao_odonto", "qt_itens"]), 4.5)

    def test_quantidade_vazia_contada_e_fora_da_soma(self) -> None:
        c = _celula(self.agg, co_ibge=MUN_A, particao_cbo="cbo_ausente", nivel="painel", tipo="exames")
        self.assertEqual(int(c["n_eventos"].sum()), 1)
        self.assertEqual(float(c["qt_itens"].sum()), 0.0)
        self.assertEqual(int(c["n_linhas_qt_vazia"].sum()), 1)
        self.assertEqual(self.diag["quantidades"]["qt_vazia_item_de_pacote"], 1)

    def test_odontologia_excluida(self) -> None:
        mfc = _celula(self.agg, co_ibge=MUN_B, particao_cbo="mfc_225130", nivel="painel",
                      operadora_odontologica=False).set_index("tipo")
        self.assertEqual(int(mfc.loc["todos_nao_odonto", "n_eventos"]), 1)  # pacote conta, item odontológico não
        self.assertNotIn("consultas", mfc.index)
        self.assertEqual(self.diag["eventos_operadora_odontologica"], 1)
        odo = _celula(self.agg, operadora_odontologica=True, nivel="fino", tipo="odontologia_tuss22")
        self.assertEqual(int(odo["n_eventos"].sum()), 1)

    def test_municipio_invalido_nunca_atribuido(self) -> None:
        st = self.diag["eventos_por_status_municipio"]
        self.assertEqual(st, {"ok": 6, "mes_divergente": 1, "municipio_ausente": 1, "municipio_invalido": 1,
                              "municipio_de_outra_uf": 1})
        nao_ok = self.agg.loc[self.agg["status_municipio"] != "ok"]
        self.assertTrue((nao_ok["co_ibge"] == "").all())
        self.assertEqual(set(self.agg.loc[self.agg["status_municipio"] == "ok", "co_ibge"]), {MUN_A, MUN_B})

    def test_juncao_e_evento_sem_item(self) -> None:
        self.assertEqual(self.diag["linhas_det"], 14)
        self.assertEqual(self.diag["linhas_det_nao_juntadas"], 1)
        self.assertAlmostEqual(self.diag["taxa_juncao_det"], 13 / 14)
        self.assertEqual(self.diag["eventos_cons_sem_item_det"], 1)
        self.assertEqual(A14.avaliar_portoes(self.diag), ["juncao_det_cons_abaixo_do_portao",
                                                          "mes_divergente_acima_do_portao"])

    def test_lotes_partidos_dao_o_mesmo_resultado(self) -> None:
        det = _det_sintetico("AMB")
        agg2, _ = _agregar("AMB", [det.slice(0, 1), det.slice(1, 6), det.slice(7)])
        pd.testing.assert_frame_equal(agg2, self.agg)
        agg1, _ = _agregar("AMB", [det.slice(0, 7), det.slice(7)])
        pd.testing.assert_frame_equal(agg1, self.agg)

    def test_hospitalar_sem_cbo_e_municipio_omitido(self) -> None:
        agg, diag = _agregar("HOSP")
        self.assertEqual(set(agg["particao_cbo"]), {"sem_cbo_na_fonte"})
        self.assertIn("municipio_omitido_pela_ans", diag["eventos_por_status_municipio"])
        self.assertNotIn("eventos_por_cbo", diag)

    def test_id_duplicado_falha(self) -> None:
        cons = _cons_sintetico()
        ids = cons.column("ID_EVENTO_ATENCAO_SAUDE").to_pylist()
        ids[1] = ids[0]
        cons = cons.set_column(0, "ID_EVENTO_ATENCAO_SAUDE", pa.array(ids, pa.string()))
        with self.assertRaises(ValueError):
            A14.agregar_pacote("AMB", UF_SINT, "202510", cons, [_det_sintetico()], ALVO_SINT, VALIDOS_SINT, PREFIXOS_SINT)

    def test_portoes_aprovam_par_limpo(self) -> None:
        self.assertEqual(A14.avaliar_portoes({"linhas_cons": 10, "linhas_det": 20, "taxa_juncao_det": 1.0,
                                              "fracao_mes_divergente_cons": 0.0}), [])
        self.assertIn("arquivo_vazio", A14.avaliar_portoes({"linhas_cons": 0, "linhas_det": 0}))


class TestPainelSintetico(unittest.TestCase):
    """Montagem do painel com cache SINTÉTICO: zero só em UF × mês aprovado; ausente é NA."""

    def test_zero_versus_ausente(self) -> None:
        agg, diag = A14.agregar_pacote("AMB", UF_SINT, "202510", _cons_sintetico(), [_det_sintetico()], ALVO_SINT,
                                       VALIDOS_SINT, PREFIXOS_SINT)
        municipios = pd.DataFrame({"co_ibge": [MUN_A, MUN_B, "120003", MUN_OUTRA_UF], "uf": ["AC", "AC", "AC", "AM"]})
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(A14, "CACHE_PACOTE", Path(tmp)):
            agg.to_parquet(A14.caminho_cache("AMB", "AC", "202510"), index=False)
            metas = {
                ("AMB", "AC", "202510"): {"status": "aprovado",
                                          "sha256_cache": A14.sha256_arquivo(A14.caminho_cache("AMB", "AC", "202510"))},
                ("AMB", "AC", "202511"): {"status": "falha_download"},
                ("AMB", "AM", "202510"): {"status": "ausente_arquivo_nao_publicado"},
            }
            s = A14.montar_paineis(municipios, metas)
        painel = s["AMB"][0]
        self.assertEqual(list(painel.columns), A14.COLUNAS_PAINEL)
        self.assertTrue((painel["natureza_dos_dados"] == "EMPIRICO").all())
        out = painel.set_index(["co_ibge", "competencia_realizacao", "tipo_procedimento", "grupo_cbo"])
        self.assertEqual(out.loc[(MUN_A, "202510", "consultas", "alvo_pmme"), "n_eventos"], 1)
        self.assertEqual(out.loc[(MUN_A, "202510", "consultas", "alvo_pmme"), "status_cobertura"], A14.STATUS_OBSERVADO)
        z = out.loc[("120003", "202510", "consultas", "todos_cbo")]
        self.assertEqual((z["n_eventos"], z["status_cobertura"]), (0, A14.STATUS_ZERO))
        na = out.loc[(MUN_A, "202511", "consultas", "todos_cbo")]
        self.assertTrue(pd.isna(na["n_eventos"]) and pd.isna(na["qt_itens"]))
        self.assertEqual(na["status_cobertura"], "ausente_falha_download")
        self.assertEqual(out.loc[(MUN_OUTRA_UF, "202510", "consultas", "todos_cbo"), "status_cobertura"],
                         "ausente_arquivo_nao_publicado")
        self.assertEqual(out.loc[(MUN_A, "202512", "consultas", "todos_cbo"), "status_cobertura"], "ausente_nao_processado")
        aus = painel["status_cobertura"].str.startswith("ausente_")
        self.assertTrue(painel.loc[aus, "n_eventos"].isna().all())
        self.assertTrue(painel.loc[~aus, "n_eventos"].notna().all())
        # eventos sem município válido ficam na tabela de não atribuídos
        nao = s["nao_atribuido"]
        self.assertEqual(set(nao["motivo_nao_atribuido"]),
                         {"mes_divergente", "municipio_ausente", "municipio_invalido", "municipio_de_outra_uf"})
        # todos_cbo = soma da partição; especialistas_nao_alvo contém a MFC
        o = painel.loc[painel["competencia_realizacao"] == "202510"].set_index(
            ["co_ibge", "tipo_procedimento", "grupo_cbo"])["n_eventos"]
        self.assertEqual(o[(MUN_B, "todos_nao_odonto", "especialistas_nao_alvo")],
                         o[(MUN_B, "todos_nao_odonto", "mfc_225130")])


# ---------------------------------------------------------------- artefatos versionados

class TestArtefatos(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.man = json.loads((OUT / "manifesto_tiss.json").read_text(encoding="utf-8"))
        cls.amb = pd.read_parquet(OUT / "painel_tiss_municipio_mes_tipo_cbo.parquet")
        cls.hosp = pd.read_parquet(OUT / "painel_tiss_hospitalar_municipio_mes_tipo.parquet")
        cls.nao = pd.read_parquet(OUT / "painel_tiss_nao_atribuido_uf_mes.parquet")
        cls.itens = pd.read_parquet(OUT / "tiss_itens_por_categoria_uf_mes.parquet")
        cls.cob = pd.read_csv(OUT / "cobertura_tiss_uf_mes.csv", dtype={"competencia_realizacao": str})
        cls.val = json.loads((OUT / "validacao_tiss.json").read_text(encoding="utf-8"))
        cls.mun = A14.carregar_municipios()

    def test_saidas_conferem_com_manifesto(self) -> None:
        for nome, reg in self.man["saidas"].items():
            p = ROOT / reg["arquivo"]
            self.assertEqual(A14.sha256_arquivo(p), reg["sha256"], nome)
            if p.suffix == ".parquet":
                self.assertEqual(pq.read_metadata(p).num_rows, reg["linhas"], nome)
        self.assertEqual(A14.verificar(), 0)

    def test_esquema_e_natureza(self) -> None:
        for df in (self.amb, self.hosp):
            self.assertEqual(list(df.columns), A14.COLUNAS_PAINEL)
        for df in (self.amb, self.hosp, self.nao, self.itens, self.cob):
            self.assertTrue((df["natureza_dos_dados"] == "EMPIRICO").all())
        self.assertEqual(self.man["natureza_dos_dados"], "EMPIRICO")

    def test_balanceado_e_municipios_do_ibge(self) -> None:
        n_mun = len(self.mun)
        self.assertEqual(len(self.amb), n_mun * 48 * len(A14.TIPOS_PAINEL) * len(A14.GRUPOS_SAIDA_AMB))
        self.assertEqual(len(self.hosp), n_mun * 48 * len(A14.TIPOS_PAINEL))
        self.assertEqual(set(self.amb["co_ibge"]), set(self.mun["co_ibge"]))
        self.assertTrue(self.amb["competencia_realizacao"].max() < "202601")
        self.assertFalse(self.amb.duplicated(["co_ibge", "competencia_realizacao", "tipo_procedimento", "grupo_cbo"]).any())

    def test_ausente_e_na_e_zero_tem_status(self) -> None:
        validos = {A14.STATUS_OBSERVADO, A14.STATUS_ZERO} | STATUS_AUSENTES
        for df in (self.amb, self.hosp):
            st = df["status_cobertura"]
            self.assertTrue((st.isin(validos) | st.str.startswith("ausente_reprovado_")).all())
            aus = st.str.startswith("ausente_")
            for c in ("n_eventos", "qt_itens", "n_linhas_det", "n_linhas_qt_vazia"):
                self.assertTrue(df.loc[aus, c].isna().all(), c)
                self.assertTrue(df.loc[~aus, c].notna().all(), c)
            zero = st == A14.STATUS_ZERO
            self.assertTrue((df.loc[zero, "n_eventos"] == 0).all())
            self.assertTrue((df.loc[~aus, "n_eventos"] >= 0).all())

    def test_status_do_painel_igual_a_cobertura(self) -> None:
        for base, df in (("AMB", self.amb), ("HOSP", self.hosp)):
            c = self.cob.loc[self.cob["base"] == base].set_index(["uf", "competencia_realizacao"])["status"]
            u = df.drop_duplicates(["uf", "competencia_realizacao"]).set_index(["uf", "competencia_realizacao"])["status_cobertura"]
            u = u.where(u.str.startswith("ausente_"), "aprovado")
            pd.testing.assert_series_equal(u.sort_index(), c.reindex(u.index).sort_index(), check_names=False)

    def test_relacoes_de_subconjunto(self) -> None:
        o = self.amb.loc[~self.amb["status_cobertura"].str.startswith("ausente_")]
        pv = o.pivot_table(index=["co_ibge", "competencia_realizacao", "tipo_procedimento"], columns="grupo_cbo",
                           values="n_eventos", aggfunc="sum")
        self.assertTrue((pv["especialistas_nao_alvo"] >= pv["mfc_225130"]).all())
        part = ["alvo_pmme", "especialistas_nao_alvo", "generalistas", "outros_medicos", "nao_medicos", "cbo_ausente"]
        self.assertTrue((pv[part].sum(axis=1) == pv["todos_cbo"]).all())
        pt = o.pivot_table(index=["co_ibge", "competencia_realizacao", "grupo_cbo"], columns="tipo_procedimento",
                           values="n_eventos", aggfunc="sum")
        self.assertTrue((pt["outros"] >= pt["agrupados_tuss63"]).all())
        for t in ("consultas", "exames", "cirurgicos", "outros"):
            self.assertTrue((pt["todos_nao_odonto"] >= pt[t]).all(), t)

    def test_portao_de_juncao_nos_aprovados(self) -> None:
        ap = self.cob.loc[self.cob["status"] == "aprovado"]
        self.assertGreater(len(ap), 0)
        self.assertTrue((ap["taxa_juncao_det"] >= A14.PORTOES["taxa_juncao_det_min"]).all())
        self.assertTrue((ap["fracao_mes_divergente_cons"] <= A14.PORTOES["fracao_mes_divergente_cons_max"]).all())

    def test_manifesto_de_arquivos(self) -> None:
        arqs = [a for a in self.man["arquivos"] if a.get("sha256")]
        self.assertGreater(len(arqs), 0)
        for a in arqs:
            self.assertRegex(a["sha256"], r"^[0-9a-f]{64}$")
            self.assertTrue(a["url"].startswith(A14.URL_BASE))
            self.assertGreater(a["bytes"], 0)
            self.assertTrue(a["data_download_utc"])
            self.assertTrue(a["last_modified_http"])
            m = re.search(r"_(\d{6})_", a["nome"])
            self.assertLess(m.group(1), "202601")
        self.assertEqual(self.man["bytes_baixados_total"], sum(a["bytes"] for a in arqs))
        n_ap = int((self.cob["status"] == "aprovado").sum())
        self.assertEqual(self.man["pacotes_aprovados"], n_ap)
        self.assertEqual(len([a for a in arqs if a["pacote"] in set(
            self.cob.loc[self.cob["status"] == "aprovado"].apply(
                lambda r: f"{r['base']}_{r['uf']}_{r['competencia_realizacao']}", axis=1))]), 2 * n_ap)

    def test_resumo_gerado_confere_com_paineis(self) -> None:
        """Os totais mensais do resumo são a soma do painel com os não atribuídos."""
        txt = (OUT / "a14_resumo.md").read_text(encoding="utf-8")
        for base, df in (("AMB", self.amb), ("HOSP", self.hosp)):
            bloco = txt.split(f"## Eventos por mês, Brasil, {base}")[1].split("\n## ")[0]
            cab = next(l for l in bloco.splitlines() if l.startswith("| Mês |"))
            i_tod = [c.strip() for c in cab.split("|")].index("todos_nao_odonto")
            p = df.loc[(df["grupo_cbo"] == "todos_cbo") & (df["tipo_procedimento"] == "todos_nao_odonto")]
            n = self.nao.loc[(self.nao["base"] == base) & (self.nao["grupo_cbo"] == "todos_cbo")
                             & (self.nao["tipo_procedimento"] == "todos_nao_odonto")]
            soma = p.groupby("competencia_realizacao")["n_eventos"].sum().add(
                n.groupby("competencia_realizacao")["n_eventos"].sum(), fill_value=0)
            linhas = [l for l in bloco.splitlines() if re.match(r"\| 20\d{4} \|", l)]
            self.assertGreater(len(linhas), 0)
            for l in linhas:
                cel = [c.strip() for c in l.split("|")]
                self.assertEqual(int(cel[i_tod].replace(".", "")), int(soma[cel[1]]), (base, cel[1]))

    def test_doc_sem_contagens_digitadas(self) -> None:
        txt = DOC.read_text(encoding="utf-8")
        self.assertIsNone(re.search(r"\b\d{1,3}(?:\.\d{3})+\b", txt), "contagem digitada no doc A14")
        self.assertIn("a14_resumo.md", txt)
        self.assertIn("manifesto_tiss.json", txt)

    def test_run_all_so_verifica(self) -> None:
        txt = (ROOT / "run_all.py").read_text(encoding="utf-8")
        self.assertIn('ROOT / "scripts" / "aquisicao" / "a14_adquirir_tiss_ans.py": ["--etapa", "verificar"]', txt)


class TestAfirmacoesDoDoc(unittest.TestCase):
    """Cada afirmação qualitativa da §8 do doc A14 conferida contra as saídas."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.cob = pd.read_csv(OUT / "cobertura_tiss_uf_mes.csv", dtype={"competencia_realizacao": str})
        cls.val = json.loads((OUT / "validacao_tiss.json").read_text(encoding="utf-8"))
        cls.amb = pd.read_parquet(OUT / "painel_tiss_municipio_mes_tipo_cbo.parquet",
                                  columns=["tipo_procedimento", "grupo_cbo", "n_eventos", "status_cobertura"])
        cls.hosp = pd.read_parquet(OUT / "painel_tiss_hospitalar_municipio_mes_tipo.parquet",
                                   columns=["status_cobertura"])

    def test_cobertura_completa(self) -> None:
        self.assertEqual(len(self.cob), 27 * 48 * 2)
        self.assertTrue((self.cob["status"] == "aprovado").all())
        self.assertFalse(self.amb["status_cobertura"].str.startswith("ausente_").any())

    def test_juncao_completa_e_sem_divergencia(self) -> None:
        j = self.val["juncao_det_cons"]
        self.assertEqual((j["minima"], j["linhas_det_nao_juntadas"]), (1.0, 0))
        self.assertEqual(self.val["eventos_cons_sem_item_det"], 0)
        self.assertEqual(self.val["quantidades"]["det_mes_divergente"], 0)
        self.assertTrue((self.cob["fracao_mes_divergente_cons"] == 0).all())

    def test_quantidades(self) -> None:
        q = self.val["quantidades"]
        self.assertEqual((q["qt_vazia_fora_de_pacote"], q["qt_nao_numerica"], q["qt_negativa"]), (0, 0, 0))
        self.assertGreater(q["qt_vazia_item_de_pacote"], 0)
        self.assertGreater(q["qt_nao_inteira"], 0)

    def test_municipios_nao_atribuidos_sao_fracao_minima(self) -> None:
        st = self.val["eventos_por_status_municipio"]
        self.assertNotIn("municipio_ausente", st)
        self.assertLess(sum(v for k, v in st.items() if k != "ok") / sum(st.values()), 1e-4)

    def test_cbo_ausente_por_tipo(self) -> None:
        pv = self.amb.groupby(["tipo_procedimento", "grupo_cbo"])["n_eventos"].sum().unstack()
        f = pv["cbo_ausente"] / pv["todos_cbo"]
        for t in ("exames", "cirurgicos", "outros"):
            self.assertGreater(f[t], 0.5, t)
        self.assertLess(f["consultas"], 0.15)
        self.assertLess((pv["outros_medicos"] / pv["todos_cbo"]).max(), 0.001)

    def test_hospitalar_maioria_sem_evento(self) -> None:
        self.assertGreater((self.hosp["status_cobertura"] == A14.STATUS_ZERO).mean(), 0.5)

    def test_sip_sem_alerta_tiss_abaixo_e_ultimo_trimestre_menor(self) -> None:
        linhas = self.val["comparacao_sip"]["linhas"]
        self.assertTrue(all(r["tiss_trimestre_completo"] for r in linhas))
        self.assertFalse(any(r["alerta"] for r in linhas))
        self.assertTrue(all(r["razao_tiss_sip"] < 1 for r in linhas))
        for item, medida in (("E", "n_eventos"), ("A", "qt_itens")):
            rs = {r["trimestre"]: r["razao_tiss_sip"] for r in linhas
                  if r["item_sip"] == item and r["tiss_medida"] == medida}
            self.assertEqual(min(rs, key=rs.get), "202510", item)

    def test_tuss63_e_grupo_009_o_maior(self) -> None:
        g = self.val["linhas_det_tuss63_por_grupo"]
        self.assertEqual(max(g, key=g.get), "009")
        self.assertGreater(self.val["linhas_det_por_tabela"]["63"], 0)

    def test_alertas_citados(self) -> None:
        a = {(x["base"], x["uf"], x["competencia_realizacao"]) for x in self.val["alertas_queda"]}
        for k in (("AMB", "AC", "202509"), ("HOSP", "AC", "202509"), ("AMB", "RR", "202512"), ("AMB", "PI", "202211")):
            self.assertIn(k, a)

    def test_datas_de_publicacao(self) -> None:
        c = self.cob.assign(ano=self.cob["competencia_realizacao"].str[:4],
                            dc=self.cob["data_publicacao_cons"].str[5:16], dd=self.cob["data_publicacao_det"].str[5:16])
        self.assertEqual(set(c.loc[c["ano"] == "2022", "dc"]) | set(c.loc[c["ano"] == "2022", "dd"]), {"30 Jul 2025"})
        rec = c.loc[c["ano"] > "2022"]
        self.assertEqual(set(rec["dc"]), {"20 Aug 2026"})
        self.assertEqual(set(rec["dd"]), {"18 Jun 2026", "19 Jun 2026"})


if __name__ == "__main__":
    unittest.main()
