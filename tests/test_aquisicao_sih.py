"""Testes da aquisição SIH/SUS pelo TabNet (a13): AIH por município × mês × grupo.

Os testes de artefato leem só saídas versionadas (painéis, manifesto e
validações); o cache de respostas brutas fica fora do Git. Os testes do leitor
usam respostas e formulários SINTÉTICOS, escritos em memória, que não
representam nenhum município nem mês real. Nenhum teste lê IVS.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path
from unittest import mock

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "aquisicao" / "a13_adquirir_sih_tabnet.py"
SPEC = importlib.util.spec_from_file_location("sih_tabnet_a13", SCRIPT)
A13 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(A13)

DOC = ROOT / "docs" / "auditorias" / "aquisicao" / "A13_sih_tabnet.md"
STATUS_COM_VALOR = {"observado", "zero_tabnet", "zero_coluna_omitida"}
STATUS_AUSENTE = "ausente_uf_mes_sem_dado"


def _ler(path: Path) -> pd.DataFrame:
    return pd.read_parquet(path)


# ---------------------------------------------------------------- sintéticos (em memória)

def _resposta_sintetica(linhas: list[str], periodo: str = "Jul/2026", eco: str = "") -> str:
    """Resposta 'prn' SINTÉTICA no formato do TabNet; números inventados."""
    return (
        "<html><b>AIH aprovadas por Grupo procedimento segundo Munic&iacute;pio</b><br>\n"
        f"{eco}<b>Per&iacute;odo:</b> {periodo}<PRE>\n" + "\n".join(linhas) + "\n&\n</PRE></html>"
    )


CAB_MUN = '"Munic&iacute;pio";"03 Procedimentos clinicos";"04 Procedimentos cirurgicos";"Total"'


class TestPlano(unittest.TestCase):
    def test_competencias_202201_a_202607_sem_ciclo3(self) -> None:
        self.assertEqual(A13.COMPETENCIAS[0], "202201")
        self.assertEqual(A13.COMPETENCIAS[-1], "202607")
        self.assertEqual(len(A13.COMPETENCIAS), 55)
        self.assertTrue(all(c < "202609" for c in A13.COMPETENCIAS))
        for proibida in ("202609", "202612", "202608"):
            with self.assertRaises(RuntimeError):
                A13.checar_limite(proibida)

    def test_rotulos_de_mes(self) -> None:
        self.assertEqual(A13.rotulo_mes("202603"), "Mar/2026")
        self.assertEqual(A13.rotulo_procmes("202603"), "Março/2026")

    def test_script_nao_le_ivs(self) -> None:
        texto = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("ivs_ipea_2010_municipios", texto)
        self.assertNotIn("a08_", texto)

    def test_padrao_e_verificar(self) -> None:
        self.assertIn('default="verificar"', SCRIPT.read_text(encoding="utf-8"))


class TestLeitorSintetico(unittest.TestCase):
    """Respostas SINTÉTICAS: testam o leitor, não a fonte."""

    def test_traco_e_zero_marcado(self) -> None:
        txt = _resposta_sintetica([CAB_MUN, '" MUNICIPIO IGNORADO - AC";-;-;-', '"120001 SINTETICO A";5;-;5',
                                   '"Total";5;-;5'])
        tab = A13.ler_tabela(txt, "mun_grupo_aih", "202607")
        self.assertEqual(tab["colunas"], ["03 Procedimentos clinicos", "04 Procedimentos cirurgicos"])
        rot, valores, zeros = tab["linhas"][1]
        self.assertEqual((rot, valores, zeros), ("120001 SINTETICO A", [5, 0, 5], [False, True, False]))

    def test_total_incoerente_falha(self) -> None:
        txt = _resposta_sintetica([CAB_MUN, '"120001 SINTETICO A";5;1;7', '"Total";5;1;7'])
        with self.assertRaises(RuntimeError):
            A13.ler_tabela(txt, "mun_grupo_aih", "202607")
        txt = _resposta_sintetica([CAB_MUN, '"120001 SINTETICO A";5;1;6', '"Total";5;2;7'])
        with self.assertRaises(RuntimeError):
            A13.ler_tabela(txt, "mun_grupo_aih", "202607")

    def test_periodo_errado_falha(self) -> None:
        txt = _resposta_sintetica([CAB_MUN, '"120001 SINTETICO A";5;1;6', '"Total";5;1;6'], periodo="Jun/2026")
        with self.assertRaises(RuntimeError):
            A13.ler_tabela(txt, "mun_grupo_aih", "202607")

    def test_resposta_sem_tabela_falha(self) -> None:
        with self.assertRaises(RuntimeError):
            A13.ler_tabela("<html>Erro no servidor</html>", "mun_grupo_aih", "202607")

    def test_celula_nao_numerica_falha(self) -> None:
        txt = _resposta_sintetica([CAB_MUN, '"120001 SINTETICO A";x;1;1', '"Total";0;1;1'])
        with self.assertRaises(ValueError):
            A13.ler_tabela(txt, "mun_grupo_aih", "202607")

    def test_filtro_tem_de_ser_ecoado(self) -> None:
        linhas = ['"Munic&iacute;pio";"Eletivo";"Total"', '"120001 SINTETICO A";2;2', '"Total";2;2']
        sem_eco = _resposta_sintetica(linhas)
        with self.assertRaises(RuntimeError):
            A13.ler_tabela(sem_eco, "mun_carater_g04_aih", "202607")
        com_eco = _resposta_sintetica(linhas, eco="<b>Grupo procedimento:</b> 04 Procedimentos cirurgicos<BR>\n")
        self.assertEqual(A13.ler_tabela(com_eco, "mun_carater_g04_aih", "202607")["total"], [2, 2])

    def test_processamento_hierarquico(self) -> None:
        meses = [f'"..{m}/2026";-;-' for m in A13.MESES_LONGOS]
        meses[6] = '"..Julho/2026";4;4'
        linhas = ['"Ano/m&ecirc;s processamento";"04 Procedimentos cirurgicos";"Total"', '"2026";4;4', *meses,
                  '"Total";4;4']
        tab = A13.ler_tabela(_resposta_sintetica(linhas), "procmes_grupo_aih", "202607")
        self.assertEqual([r for r, v, _ in tab["linhas"] if v[-1]], ["Julho/2026"])

    def test_classificacao_das_linhas(self) -> None:
        self.assertEqual(A13.classificar_linha_municipal("MUNICIPIO IGNORADO - RR"), ("ignorado_uf", "IGNORADO_RR", "14"))
        self.assertEqual(A13.classificar_linha_municipal("000000 Ignorado ou exterior"),
                         ("ignorado_exterior", "000000", "00"))
        self.assertEqual(A13.classificar_linha_municipal("530010 BRASILIA"), ("municipio", "530010", "53"))
        with self.assertRaises(RuntimeError):
            A13.classificar_linha_municipal("Linha estranha")


class TestCorpoDoPost(unittest.TestCase):
    """Formulário SINTÉTICO mínimo: o corpo sai dos VALUEs do formulário, não de texto digitado."""

    FORM = (
        '<FORM ACTION="/cgi/tabcgi.exe?sih/cnv/qibr.def" METHOD=POST>'
        '<SELECT NAME="Linha"><OPTION VALUE="Município">Munic&iacute;pio<OPTION VALUE="UF" SELECTED>UF</SELECT>'
        '<SELECT NAME="Coluna"><OPTION VALUE="Grupo_procedimento">Grupo procedimento'
        '<OPTION VALUE="Caráter_atendimento">Car&aacute;ter atendimento</SELECT>'
        '<SELECT NAME="Incremento"><OPTION VALUE="AIH_aprovadas" SELECTED>AIH aprovadas</SELECT>'
        '<SELECT NAME="Arquivos"><OPTION VALUE="qibr2607.dbf" SELECTED>Jul/2026</SELECT>'
        '<SELECT NAME="SGrupo_procedimento"><OPTION VALUE="TODAS_AS_CATEGORIAS__" SELECTED>Todas as categorias'
        '<OPTION VALUE="4">04 Procedimentos cirurgicos</SELECT>'
        '<SELECT NAME="SUF"><OPTION VALUE="TODAS_AS_CATEGORIAS__" SELECTED>Todas as categorias'
        '<OPTION VALUE="2">12 Acre</SELECT>'
    )

    def test_corpo_usa_valores_do_formulario(self) -> None:
        selects = A13.ler_formulario(self.FORM)
        corpo = A13.montar_corpo(selects, "mun_carater_g04_aih", "202607")
        pares = dict(p.split("=", 1) for p in corpo.split("&"))
        self.assertEqual(pares["Linha"], "Munic%EDpio")  # latin-1
        self.assertEqual(pares["Coluna"], "Car%E1ter_atendimento")
        self.assertEqual(pares["Arquivos"], "qibr2607.dbf")
        self.assertEqual(pares["SGrupo_procedimento"], "4")
        self.assertEqual(pares["SUF"], "TODAS_AS_CATEGORIAS__")
        self.assertEqual((pares["formato"], pares["zeradas"], pares["mostre"]), ("prn", "exibirlz", "Mostra"))

    def test_mes_fora_do_formulario_falha(self) -> None:
        selects = A13.ler_formulario(self.FORM)
        with self.assertRaises(RuntimeError):
            A13.montar_corpo(selects, "mun_grupo_aih", "202606")
        with self.assertRaises(RuntimeError):
            A13.montar_corpo(selects, "mun_grupo_aih", "202609")


# ---------------------------------------------------------------- artefatos versionados

class TestArtefatos(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.man = json.loads(A13.MANIFESTO_FILE.read_text(encoding="utf-8"))
        cls.val = json.loads(A13.VALIDACOES_FILE.read_text(encoding="utf-8"))
        cls.painel = _ler(A13.PAINEL_FILE)
        cls.carater = _ler(A13.CARATER_FILE)
        cls.ign = _ler(A13.IGNORADOS_FILE)

    def test_esquemas(self) -> None:
        self.assertEqual(list(self.painel.columns), A13.COLUNAS_PAINEL)
        self.assertEqual(list(self.carater.columns), A13.COLUNAS_CARATER)
        self.assertEqual(list(self.ign.columns), A13.COLUNAS_IGNORADOS)
        self.assertFalse(self.painel.duplicated(["co_ibge", "competencia", "grupo"]).any())
        self.assertFalse(self.carater.duplicated(["co_ibge", "competencia", "carater"]).any())
        self.assertTrue(self.painel["co_ibge"].str.fullmatch(r"\d{6}").all())
        self.assertTrue((self.painel["uf"] == self.painel["co_ibge"].str[:2]).all())

    def test_natureza_empirica(self) -> None:
        for df in (self.painel, self.carater, self.ign):
            self.assertEqual(set(df["natureza_dos_dados"]), {"EMPIRICO"})
        self.assertEqual(self.man["natureza_dos_dados"], "EMPIRICO")
        self.assertEqual(self.val["natureza_dos_dados"], "EMPIRICO")

    def test_nenhum_mes_do_ciclo3(self) -> None:
        for df in (self.painel, self.carater, self.ign):
            self.assertTrue((df["competencia"] < "202609").all())
            self.assertEqual(sorted(df["competencia"].unique()), A13.COMPETENCIAS)
        self.assertEqual(self.man["competencias_planejadas"], A13.COMPETENCIAS)

    def test_painel_balanceado_no_universo_do_formulario(self) -> None:
        n_mun = self.man["universo_municipios"]["n"]
        grupos = self.val["grupos_painel"]
        self.assertIn("04", grupos)
        self.assertEqual(self.painel["co_ibge"].nunique(), n_mun)
        # doc A13, §4: o formulário inclui 510183 (Boa Esperança do Norte, MT), posterior ao Censo 2022
        self.assertIn("510183", set(self.painel["co_ibge"]))
        self.assertEqual(len(self.painel), n_mun * len(A13.COMPETENCIAS) * len(grupos))

    def test_validacoes_aprovadas(self) -> None:
        self.assertEqual(self.val["status"], "APROVADO")
        self.assertEqual(self.val["erros"], [])
        self.assertEqual(self.man["validacoes"]["status"], "APROVADO")
        for comp, v in self.val["por_competencia"].items():
            for chave in ("v1_soma_linhas_igual_total", "v2_total_mun_uf_procmes", "v3_soma_municipal_por_uf",
                          "v4_mes_processamento", "v5_carater_soma_g04", "v7_universo_municipios"):
                self.assertTrue(v[chave], (comp, chave))
            for uf, r in v["v6_uf_pequena_celula_a_celula"].items():
                self.assertTrue(r["identicas"] and r["celulas_comparadas"] > 0, (comp, uf))

    def test_uf_mes_sem_dado_fica_ausente_nunca_zero(self) -> None:
        ausentes = {(r["competencia"], r["uf"]) for r in self.val["uf_meses_sem_dado"]}
        for df, cols in ((self.painel, ["aih_aprovadas", "internacoes", "valor_total"]),
                         (self.carater, ["aih_aprovadas"])):
            chave = pd.Series(list(zip(df["competencia"], df["uf"])), index=df.index)
            em_ausente = chave.isin(ausentes)
            self.assertTrue((df.loc[em_ausente, "status"] == STATUS_AUSENTE).all())
            for c in cols:
                self.assertTrue(df.loc[em_ausente, c].isna().all(), c)
                # fora de UF-mês sem dado não há ausente: zero só vem do '-' ou da coluna omitida conferida
                self.assertFalse(df.loc[~em_ausente, c].isna().any(), c)
            self.assertTrue(set(df.loc[~em_ausente, "status"]) <= STATUS_COM_VALOR)
        ign_chave = pd.Series(list(zip(self.ign["competencia"], self.ign["uf"])), index=self.ign.index)
        self.assertTrue(self.ign.loc[ign_chave.isin(ausentes), "aih_aprovadas"].isna().all())

    def test_ausencia_coincide_com_total_zero_da_uf(self) -> None:
        tot = self.val["totais_uf_mes_aih"]
        detectados = {(c, s) for c, d in tot.items() for s, x in d.items() if x == 0}
        registrados = {(r["competencia"], r["sigla"]) for r in self.val["uf_meses_sem_dado"]}
        self.assertEqual(detectados, registrados)
        self.assertEqual(self.man["uf_meses_sem_dado"], self.val["uf_meses_sem_dado"])

    def test_status_coerente_com_valor(self) -> None:
        p = self.painel
        self.assertTrue((p.loc[p["status"] == "observado", "aih_aprovadas"] > 0).all())
        self.assertTrue((p.loc[p["status"].isin(["zero_tabnet", "zero_coluna_omitida"]), "aih_aprovadas"] == 0).all())

    def test_soma_municipal_mais_ignorados_reproduz_total_do_tabnet(self) -> None:
        soma = self.painel.groupby(["competencia", "grupo"])["aih_aprovadas"].sum()
        soma_ign = self.ign.groupby(["competencia", "grupo"])["aih_aprovadas"].sum()
        for comp, v in self.val["por_competencia"].items():
            for g in self.val["grupos_painel"]:
                total = v["total_aih_por_grupo"].get(g, 0)
                self.assertEqual(int(soma[(comp, g)]) + int(soma_ign[(comp, g)]), total, (comp, g))

    def test_carater_soma_o_grupo_04(self) -> None:
        g04 = self.painel.loc[self.painel["grupo"] == "04"].set_index(["co_ibge", "competencia"])["aih_aprovadas"]
        car = self.carater.groupby(["co_ibge", "competencia"])["aih_aprovadas"].sum(min_count=1)
        comparado = pd.concat([g04.rename("g04"), car.rename("car")], axis=1)
        ambos_ausentes = comparado["g04"].isna() & comparado["car"].isna()
        iguais = (comparado["g04"] == comparado["car"]).fillna(False).astype(bool)
        self.assertTrue((ambos_ausentes | iguais).all())
        self.assertTrue({"eletivo", "urgencia"} <= set(self.carater["carater"]))

    def test_proveniencia_de_cada_consulta(self) -> None:
        feitas = {(q["consulta"], q["competencia"]) for q in self.man["consultas_realizadas"]}
        esperadas = {(c, m) for c in A13.CONSULTAS for m in A13.COMPETENCIAS}
        self.assertEqual(feitas, esperadas)
        for q in self.man["consultas_realizadas"]:
            self.assertEqual(q["url"], A13.URL_TAB)
            self.assertRegex(q["sha256"], r"^[0-9a-f]{64}$")
            self.assertIn("formato=prn", q["corpo_post"])
            self.assertIn(f"qibr{q['competencia'][2:]}.dbf", q["corpo_post"])
            self.assertTrue(q["data_hora_utc"])
        self.assertRegex(self.man["fonte"]["formulario"]["sha256"], r"^[0-9a-f]{64}$")

    def test_saidas_conferem_com_manifesto(self) -> None:
        for nome, path in (("painel", A13.PAINEL_FILE), ("carater", A13.CARATER_FILE),
                           ("ignorados", A13.IGNORADOS_FILE)):
            self.assertEqual(A13.sha256_arquivo(path), self.man["saidas"][nome]["sha256"], nome)

    def test_doc_lista_os_uf_meses_sem_dado_do_manifesto(self) -> None:
        texto = DOC.read_text(encoding="utf-8")
        bloco = texto.split("<!-- uf_meses_sem_dado -->")[1].split("<!-- /uf_meses_sem_dado -->")[0]
        no_doc = set(re.findall(r"(\d{6}) — ([A-Z]{2})", bloco))
        no_man = {(r["competencia"], r["sigla"]) for r in self.man["uf_meses_sem_dado"]}
        self.assertEqual(no_doc, no_man)
        bloco = texto.split("<!-- uf_meses_atipicos -->")[1].split("<!-- /uf_meses_atipicos -->")[0]
        no_doc = set(re.findall(r"(\d{6}) — ([A-Z]{2})", bloco))
        no_man = {(r["competencia"], r["sigla"]) for r in self.man["uf_meses_atipicos"]}
        self.assertEqual(no_doc, no_man)


    def test_afirmacoes_da_secao_5_3_do_doc(self) -> None:
        """§5.3: AC e RR têm dado em 202606 no TabNet; RR 202606 é atípico; a falta está em 202607."""
        sem_dado = {(r["competencia"], r["sigla"]) for r in self.val["uf_meses_sem_dado"]}
        atipicos = {(r["competencia"], r["sigla"]) for r in self.val["uf_meses_atipicos"]}
        self.assertNotIn(("202606", "AC"), sem_dado)
        self.assertNotIn(("202606", "RR"), sem_dado)
        self.assertIn(("202606", "RR"), atipicos)
        self.assertTrue({("202607", "AC"), ("202607", "RR")} <= sem_dado)
        self.assertGreater(self.val["totais_uf_mes_aih"]["202606"]["AC"], 0)


class TestVerificarSemRede(unittest.TestCase):
    def test_verificar_nao_usa_rede_nem_grava(self) -> None:
        saidas = [A13.PAINEL_FILE, A13.CARATER_FILE, A13.IGNORADOS_FILE, A13.MANIFESTO_FILE,
                  A13.VALIDACOES_FILE, A13.RESUMO_FILE]
        antes = {p: p.stat().st_mtime_ns for p in saidas}

        def sem_rede(*_a, **_k):
            raise AssertionError("a13 em --etapa verificar tentou acessar a rede ou gravar")

        with mock.patch("urllib.request.urlopen", sem_rede), \
                mock.patch.object(A13, "gravar_parquet", sem_rede), \
                mock.patch.object(A13, "etapa_baixar", sem_rede), \
                mock.patch.object(sys, "argv", ["a13", "--etapa", "verificar"]):
            self.assertEqual(A13.main(), 0)
        self.assertEqual({p: p.stat().st_mtime_ns for p in saidas}, antes)


if __name__ == "__main__":
    unittest.main()
