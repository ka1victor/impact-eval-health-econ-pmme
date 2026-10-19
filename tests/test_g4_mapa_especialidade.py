"""Testes do portão G4 (plano 51, P3, T3.2): mapa curso → formas de organização e viabilidade do filtro.

Os testes de artefato leem só saídas versionadas (mapa, tabelas nacionais,
resumo, sondagem e manifesto) e a ponte curso–CBO. Os testes do leitor usam
respostas do TabNet e um ZIP do SIGTAP SINTÉTICOS, escritos em memória, que não
representam nenhum dado real. Nenhum teste lê IVS.
"""

from __future__ import annotations

import importlib.util
import io
import json
import re
import unittest
import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "aquisicao" / "g4_mapa_especialidade_procedimento.py"
SPEC = importlib.util.spec_from_file_location("g4_mapa", SCRIPT)
G4 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(G4)
DOC = ROOT / "docs" / "auditorias" / "G4_viabilidade_especialidade.md"


def _resposta(linhas: list[str], periodo: str, eco: str = "") -> bytes:
    """Resposta 'prn' SINTÉTICA; números inventados."""
    return (f"<html><H1>x</H1>{eco}<b>Per&iacute;odo:</b> {periodo}<PRE>\n" + "\n".join(linhas)
            + "\n&\n</PRE></html>").encode("latin-1")


class TestPlano(unittest.TestCase):
    def test_janela_antes_do_programa_e_sem_ciclo3(self) -> None:
        self.assertEqual(G4.MESES_MAPA, [f"2024{m:02d}" for m in range(1, 13)])
        self.assertTrue(all(c < "202609" for c in G4.MESES_MAPA + [G4.MES_TESTE]))
        with self.assertRaises(RuntimeError):
            G4.checar_limite("202609")

    def test_script_nao_le_ivs(self) -> None:
        texto = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("ivs_ipea_2010_municipios", texto)
        self.assertNotIn("a08_", texto)
        self.assertIn('default="verificar"', texto)

    def test_classes_de_especificidade(self) -> None:
        self.assertEqual(G4.classe_especificidade(0.5), "alta")
        self.assertEqual(G4.classe_especificidade(0.2), "media")
        self.assertEqual(G4.classe_especificidade(0.19), "baixa")
        self.assertEqual(G4.classe_especificidade(None), "sem_producao_medica")


class TestLeitorSintetico(unittest.TestCase):
    Q = {"id": "x", "linha": "Profissional - CBO", "coluna": "forma", "meses": ["202402", "202401"],
         "eco_cbo": "225151 Medico anestesiologista"}

    def test_le_varios_meses_e_confere_somas(self) -> None:
        eco = "<b>Profissional - CBO:</b> 225151 Medico anestesiologista<BR>"
        raw = _resposta(['"Profissional - CBO";"041701 Anestesias";"030101 Consultas";"Total"',
                         '"225151 Medico anestesiologista";3;-;3', '"Total";3;-;3'], "Fev/2024, Jan/2024", eco)
        r = G4.ler_resposta(raw, self.Q)
        self.assertEqual(r["colunas"], [("041701", "Anestesias"), ("030101", "Consultas")])
        self.assertEqual(r["total"], [3, 0, 3])
        with self.assertRaises(G4.ErroResposta):  # período que não é o pedido
            G4.ler_resposta(_resposta(['"Profissional - CBO";"041701 Anestesias";"Total"',
                                       '"225151 Medico anestesiologista";3;3', '"Total";3;3'], "Jan/2024", eco), self.Q)
        with self.assertRaises(G4.ErroResposta):  # filtro de CBO não ecoado
            G4.ler_resposta(_resposta(['"Profissional - CBO";"041701 Anestesias";"Total"',
                                       '"225151 Medico anestesiologista";3;3', '"Total";3;3'], "Fev/2024, Jan/2024"),
                            self.Q)
        with self.assertRaises(G4.ErroResposta):  # Total incoerente
            G4.ler_resposta(_resposta(['"Profissional - CBO";"041701 Anestesias";"Total"',
                                       '"225151 Medico anestesiologista";3;4', '"Total";3;4'], "Fev/2024, Jan/2024",
                                      eco), self.Q)

    def test_sigtap_zip_sintetico(self) -> None:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("rl_procedimento_ocupacao_layout.txt",
                       "Coluna,Tamanho,Inicio,Fim,Tipo\nCO_PROCEDIMENTO,10,1,10,VARCHAR2\n"
                       "CO_OCUPACAO,6,11,16,CHAR\nDT_COMPETENCIA,6,17,22,CHAR\n")
            z.writestr("rl_procedimento_ocupacao.txt", "0417010010225151202412\n0405010010225265202412\n")
        df = G4.ler_rl_procedimento_ocupacao(buf.getvalue())
        self.assertEqual(list(df["co_ocupacao"]), ["225151", "225265"])
        self.assertEqual(list(df["co_forma"]), ["041701", "040501"])

    def test_tipica_inclui_a_forma_que_cruza_o_limiar(self) -> None:
        cursos = [{"cod_curso": 99, "no_curso": "SINTETICO", "cbos": ["999999"], "grau_univocidade": "X"}]
        cbo_forma = pd.DataFrame({"co_cbo": ["999999"] * 3, "no_cbo": ["s"] * 3,
                                  "co_forma": ["010101", "020202", "030303"], "no_forma": ["a", "b", "c"],
                                  "qtd_aprovada": [70, 20, 10]})
        forma = pd.DataFrame({"co_forma": ["010101", "020202", "030303"], "qtd_aprovada_medicos": [100, 20, 50],
                              "qtd_aprovada_todos": [200, 40, 50], "co_subgrupo": ["0101", "0202", "0303"]})
        mapa, sg = G4.montar_mapa(cursos, cbo_forma, forma, None)
        self.assertEqual(list(mapa["tipica"]), [True, True, False])
        self.assertEqual(list(mapa["classe_especificidade"]), ["alta", "alta", "media"])
        self.assertEqual(set(mapa["compatibilidade_sigtap"]), {"NAO_OBTIDA"})
        self.assertAlmostEqual(sg["participacao_na_producao_do_curso"].sum(), 1.0)


class TestArtefatos(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mapa = pd.read_csv(G4.MAPA_FILE, dtype={"co_forma": str, "co_subgrupo": str, "co_grupo": str,
                                                    "cbos_curso": str})
        cls.sg = pd.read_csv(G4.MAPA_SUBGRUPO_FILE, dtype={"co_subgrupo": str, "co_grupo": str, "cbos_curso": str})
        cls.cbo_forma = pd.read_csv(G4.CBO_FORMA_FILE, dtype={"co_cbo": str, "co_forma": str})
        cls.forma = pd.read_csv(G4.FORMA_FILE, dtype={"co_forma": str, "co_subgrupo": str, "co_grupo": str})
        cls.teste = pd.read_csv(G4.TESTE_FILE, dtype={"co_forma": str, "co_subgrupo": str, "mes_processamento": str})
        cls.res = json.loads(G4.RESUMO_FILE.read_text(encoding="utf-8"))
        cls.sond = json.loads(G4.SONDAGEM_FILE.read_text(encoding="utf-8"))
        cls.man = json.loads(G4.MANIFESTO_FILE.read_text(encoding="utf-8"))
        cls.ponte = json.loads(G4.PONTE_FILE.read_text(encoding="utf-8"))

    def test_esquema_e_natureza(self) -> None:
        self.assertEqual(list(self.mapa.columns), G4.COLUNAS_MAPA)
        self.assertEqual(list(self.sg.columns), G4.COLUNAS_SUBGRUPO)
        for df in (self.mapa, self.sg, self.cbo_forma, self.forma, self.teste):
            self.assertEqual(set(df["natureza_dos_dados"]), {"EMPIRICO"})
        self.assertEqual(self.res["natureza_dos_dados"], "EMPIRICO")
        self.assertFalse(self.mapa.duplicated(["cod_curso", "co_forma"]).any())

    def test_cursos_e_cbos_vem_da_ponte(self) -> None:
        ponte = {c["cod_curso"]: "|".join(sorted(c["cbos_elegiveis"])) for c in self.ponte["catalogo_cursos"]}
        self.assertEqual(set(self.mapa["cod_curso"]), set(ponte))
        for k, g in self.mapa.groupby("cod_curso"):
            self.assertEqual(set(g["cbos_curso"]), {ponte[k]})

    def test_mapa_recalculado_das_tabelas_nacionais(self) -> None:
        tot = self.forma.set_index("co_forma")
        for k, g in self.mapa.groupby("cod_curso"):
            cbos = g["cbos_curso"].iloc[0].split("|")
            esperado = self.cbo_forma.loc[self.cbo_forma["co_cbo"].isin(cbos)].groupby("co_forma")["qtd_aprovada"].sum()
            self.assertEqual(g.set_index("co_forma")["qtd_aprovada_cbo_curso"].sort_index().to_dict(),
                             esperado.sort_index().to_dict(), k)
            self.assertAlmostEqual(g["participacao_na_producao_do_curso"].sum(), 1.0, places=4)
            g = g.sort_values("ordem_no_curso")
            antes = g["participacao_acumulada"] - g["participacao_na_producao_do_curso"]
            self.assertEqual(list(g["tipica"]), list(antes < G4.LIMIAR_TIPICA - 1e-6), k)
            for r in g.itertuples():
                med = tot.loc[r.co_forma, "qtd_aprovada_medicos"]
                self.assertEqual(r.qtd_aprovada_medicos, med)
                self.assertAlmostEqual(r.especificidade_medicos, r.qtd_aprovada_cbo_curso / med, places=5)
                self.assertEqual(r.classe_especificidade, G4.classe_especificidade(r.especificidade_medicos))

    def test_medicos_nao_excedem_todos(self) -> None:
        self.assertTrue((self.forma["qtd_aprovada_medicos"] <= self.forma["qtd_aprovada_todos"]).all())
        soma = self.cbo_forma.groupby("co_forma")["qtd_aprovada"].sum()
        self.assertEqual(soma.to_dict(), self.forma.set_index("co_forma")["qtd_aprovada_medicos"][
            lambda s: s > 0].to_dict())

    def test_sigtap_registrado_sem_inventar(self) -> None:
        self.assertIn(self.sond["status"], {"OBTIDO", "INDISPONIVEL_NESTA_EXECUCAO"})
        self.assertTrue(self.sond["tentativas"])
        for t in self.sond["tentativas"]:
            self.assertTrue(t["data_hora_utc"] and t["url"] and t["resultado"])
        if self.sond["status"] != "OBTIDO":
            self.assertEqual(set(self.mapa["compatibilidade_sigtap"]), {"NAO_OBTIDA"})
            self.assertEqual(self.res["veredito"], "VIAVEL_PARCIAL")

    def test_teste_do_filtro(self) -> None:
        t = self.res["teste_filtro_tabnet"]
        self.assertTrue(t["viavel"])
        self.assertTrue(t["todos_os_municipios_do_formulario_presentes"])
        self.assertEqual(t["mes_processamento"], G4.MES_TESTE)
        self.assertTrue((self.teste["qtd_total_consulta_municipal"] == self.teste["qtd_total_consulta_por_cbo"]).all())
        self.assertEqual(int(self.teste["qtd_total_consulta_municipal"].sum()), t["qtd_total_nacional"])
        # só totais nacionais no arquivo versionado: nenhuma coluna de município
        self.assertFalse({"co_ibge", "municipio"} & set(self.teste.columns))
        # soma por subgrupo reproduz o a12 (recalculado aqui a partir do CSV versionado do a12)
        a12 = pd.read_csv(G4.A12_SUBGRUPOS_FILE, dtype={"competencia_processamento": str, "subgrupo": str})
        a12 = a12.loc[(a12["competencia_processamento"] == G4.MES_TESTE) & (a12["conjunto_cbo"] == "alvo_pmme")]
        a12 = a12.set_index("subgrupo")["total_tabnet_municipio"].fillna(0).astype(int)
        sg = self.teste.groupby("co_subgrupo")["qtd_total_consulta_municipal"].sum()
        self.assertEqual(sg.to_dict(), a12[a12 > 0].to_dict())

    def test_resumo_coerente_com_o_mapa(self) -> None:
        cob = self.res["cobertura"]
        self.assertEqual(cob["linhas_do_mapa"], len(self.mapa))
        self.assertEqual(cob["linhas_tipicas"], int(self.mapa["tipica"].sum()))
        classes = self.res["classes_dos_cursos"]
        self.assertEqual(sorted(sum(classes.values(), [])), sorted(set(self.mapa["cod_curso"])))
        for c in self.res["por_curso"]:
            g = self.mapa.loc[self.mapa["cod_curso"] == c["cod_curso"]]
            p_alta = g.loc[g["classe_especificidade"] == "alta", "participacao_na_producao_do_curso"].sum()
            self.assertAlmostEqual(c["participacao_da_producao_em_formas_de_especificidade_alta"], p_alta, places=3)

    def test_manifesto_confere_saidas(self) -> None:
        for nome, s in self.man["saidas"].items():
            self.assertEqual(G4.sha256_arquivo(ROOT / s["arquivo"]), s["sha256"], nome)
        for q in self.man["fonte_tabnet"]["consultas"]:
            self.assertEqual(q["url"], G4.URL_TAB)
            self.assertRegex(q["sha256"], r"^[0-9a-f]{64}$")
            self.assertIn("formato=prn", q["corpo_post"])

    def test_doc_traz_o_veredito_e_as_classes_do_resumo(self) -> None:
        texto = DOC.read_text(encoding="utf-8")
        b = texto.split("<!-- G4:veredito -->")[1].split("<!-- /G4:veredito -->")[0]
        self.assertIn(self.res["veredito"], b)
        b = texto.split("<!-- G4:classes -->")[1].split("<!-- /G4:classes -->")[0]
        for classe, cursos in self.res["classes_dos_cursos"].items():
            linha = next(ln for ln in b.splitlines() if ln.startswith(f"| {classe} "))
            self.assertEqual(sorted(int(x) for x in re.findall(r"\b\d+\b", linha.split("|")[2])), cursos, classe)


if __name__ == "__main__":
    unittest.main()
