"""Testes da aquisição SIH/SUS por local de residência pelo TabNet (a15, portão G3 do plano 51).

Os testes de artefato leem só saídas versionadas (painéis, manifesto e
validações do a15 e as validações do a13); o cache de respostas brutas fica fora
do controle de versão. Os testes do leitor usam respostas e formulários
SINTÉTICOS, escritos em memória, que não representam nenhum município nem mês
real. Nenhum teste lê IVS.
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
SCRIPT = ROOT / "scripts" / "aquisicao" / "a15_adquirir_sih_residencia.py"
SPEC = importlib.util.spec_from_file_location("sih_residencia_a15", SCRIPT)
A15 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(A15)

DOC = ROOT / "docs" / "auditorias" / "aquisicao" / "A15_sih_residencia.md"
STATUS_COM_VALOR = {"observado", "zero_tabnet", "zero_coluna_omitida"}


# ---------------------------------------------------------------- sintéticos (em memória)

def _resposta_sintetica(linhas: list[str], periodo: str = "Jul/2026", eco: str = "",
                        titulo: str = "Procedimentos hospitalares do SUS - por local de resid&ecirc;ncia - Brasil") -> str:
    """Resposta 'prn' SINTÉTICA no formato do TabNet; números inventados."""
    return (
        f"<html><HEAD><TITLE>TabNet Win32 3.3:  {titulo}</TITLE></HEAD>"
        "<b>AIH aprovadas por Grupo procedimento segundo Munic&iacute;pio</b><br>\n"
        f"{eco}<b>Per&iacute;odo:</b> {periodo}<PRE>\n" + "\n".join(linhas) + "\n&\n</PRE></html>"
    )


CAB_MUN = '"Munic&iacute;pio";"03 Procedimentos clinicos";"04 Procedimentos cirurgicos";"Total"'
CAB_UF = '"UF";"03 Procedimentos clinicos";"04 Procedimentos cirurgicos";"Total"'


class TestPlano(unittest.TestCase):
    def test_competencias_202201_a_202607_sem_ciclo3(self) -> None:
        self.assertEqual(A15.COMPETENCIAS[0], "202201")
        self.assertEqual(A15.COMPETENCIAS[-1], "202607")
        self.assertEqual(len(A15.COMPETENCIAS), 55)
        self.assertTrue(all(c < "202609" for c in A15.COMPETENCIAS))
        for proibida in ("202609", "202612", "202608"):
            with self.assertRaises(RuntimeError):
                A15.checar_limite(proibida)

    def test_fontes_so_http_e_formularios_certos(self) -> None:
        self.assertIn("sih/cnv/qrbr.def", A15.URL_FORM)
        self.assertTrue(all(f["url_form"].startswith("http://") for f in A15.FONTES.values()))
        self.assertEqual({s["fonte"] for s in A15.CONSULTAS.values()}, {"qrbr", "qibr"})
        self.assertEqual([c for c, s in A15.CONSULTAS.items() if s["fonte"] == "qibr"], ["int_uf_grupo_aih"])

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
        tab = A15.ler_tabela(txt, "mun_grupo_aih", "202607")
        rot, valores, zeros = tab["linhas"][1]
        self.assertEqual((rot, valores, zeros), ("120001 SINTETICO A", [5, 0, 5], [False, True, False]))

    def test_titulo_distingue_residencia_de_internacao(self) -> None:
        linhas = [CAB_UF, '"12 Acre";5;1;6', '"Total";5;1;6']
        interna = "Procedimentos hospitalares do SUS - por local de interna&ccedil;&atilde;o - Brasil"
        # resposta do formulário de internação não serve como residência, e vice-versa
        with self.assertRaises(RuntimeError):
            A15.ler_tabela(_resposta_sintetica(linhas, titulo=interna), "uf_grupo_aih", "202607")
        with self.assertRaises(RuntimeError):
            A15.ler_tabela(_resposta_sintetica(linhas), "int_uf_grupo_aih", "202607")
        self.assertEqual(A15.ler_tabela(_resposta_sintetica(linhas, titulo=interna), "int_uf_grupo_aih",
                                        "202607")["total"], [5, 1, 6])

    def test_total_incoerente_falha(self) -> None:
        txt = _resposta_sintetica([CAB_MUN, '"120001 SINTETICO A";5;1;7', '"Total";5;1;7'])
        with self.assertRaises(RuntimeError):
            A15.ler_tabela(txt, "mun_grupo_aih", "202607")

    def test_periodo_errado_falha(self) -> None:
        txt = _resposta_sintetica([CAB_MUN, '"120001 SINTETICO A";5;1;6', '"Total";5;1;6'], periodo="Jun/2026")
        with self.assertRaises(RuntimeError):
            A15.ler_tabela(txt, "mun_grupo_aih", "202607")

    def test_filtro_tem_de_ser_ecoado(self) -> None:
        linhas = ['"Munic&iacute;pio";"Eletivo";"Total"', '"120001 SINTETICO A";2;2', '"Total";2;2']
        with self.assertRaises(RuntimeError):
            A15.ler_tabela(_resposta_sintetica(linhas), "mun_carater_g04_aih", "202607")
        com_eco = _resposta_sintetica(linhas, eco="<b>Grupo procedimento:</b> 04 Procedimentos cirurgicos<BR>\n")
        self.assertEqual(A15.ler_tabela(com_eco, "mun_carater_g04_aih", "202607")["total"], [2, 2])


class TestCorpoDoPost(unittest.TestCase):
    """Formulários SINTÉTICOS mínimos: o corpo sai dos VALUEs do formulário da fonte da consulta."""

    @staticmethod
    def _form(fonte: str) -> str:
        return (
            f'<FORM ACTION="/cgi/tabcgi.exe?sih/cnv/{fonte}.def" METHOD=POST>'
            '<SELECT NAME="Linha"><OPTION VALUE="Município">Munic&iacute;pio<OPTION VALUE="UF" SELECTED>UF</SELECT>'
            '<SELECT NAME="Coluna"><OPTION VALUE="Grupo_procedimento">Grupo procedimento</SELECT>'
            '<SELECT NAME="Incremento"><OPTION VALUE="AIH_aprovadas" SELECTED>AIH aprovadas</SELECT>'
            f'<SELECT NAME="Arquivos"><OPTION VALUE="{fonte}2607.dbf" SELECTED>Jul/2026</SELECT>'
            '<SELECT NAME="SUF"><OPTION VALUE="TODAS_AS_CATEGORIAS__" SELECTED>Todas as categorias'
            '<OPTION VALUE="2">12 Acre</SELECT>'
        )

    def test_corpo_usa_o_formulario_da_fonte(self) -> None:
        selects = {f: A15.ler_formulario(self._form(f), f) for f in ("qrbr", "qibr")}
        res = dict(p.split("=", 1) for p in A15.montar_corpo(selects, "uf_grupo_aih", "202607").split("&"))
        inte = dict(p.split("=", 1) for p in A15.montar_corpo(selects, "int_uf_grupo_aih", "202607").split("&"))
        self.assertEqual(res["Arquivos"], "qrbr2607.dbf")
        self.assertEqual(inte["Arquivos"], "qibr2607.dbf")
        self.assertEqual(res["SUF"], "TODAS_AS_CATEGORIAS__")
        filtrado = dict(p.split("=", 1) for p in A15.montar_corpo(selects, "mun_grupo_aih_uf_AC", "202607").split("&"))
        self.assertEqual((filtrado["Linha"], filtrado["SUF"]), ("Munic%EDpio", "2"))

    def test_formulario_de_outra_fonte_falha(self) -> None:
        with self.assertRaises(RuntimeError):
            A15.ler_formulario(self._form("qibr"), "qrbr")


# ---------------------------------------------------------------- artefatos versionados

class TestArtefatos(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.man = json.loads(A15.MANIFESTO_FILE.read_text(encoding="utf-8"))
        cls.val = json.loads(A15.VALIDACOES_FILE.read_text(encoding="utf-8"))
        cls.val13 = json.loads(A15.A13_VALIDACOES.read_text(encoding="utf-8"))
        cls.painel = pd.read_parquet(A15.PAINEL_FILE)
        cls.carater = pd.read_parquet(A15.CARATER_FILE)
        cls.ign = pd.read_parquet(A15.IGNORADOS_FILE)
        cls.ausentes = ({(r["competencia"], r["uf"]) for r in cls.val["uf_meses_sem_dado"]}
                        | {(r["competencia"], r["uf"]) for r in cls.val["uf_meses_sem_arquivo_internacao"]})

    def test_esquemas(self) -> None:
        self.assertEqual(list(self.painel.columns), A15.COLUNAS_PAINEL)
        self.assertEqual(list(self.carater.columns), A15.COLUNAS_CARATER)
        self.assertEqual(list(self.ign.columns), A15.COLUNAS_IGNORADOS)
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
            self.assertEqual(sorted(df["competencia"].unique()), A15.COMPETENCIAS)
        self.assertEqual(self.man["competencias_planejadas"], A15.COMPETENCIAS)

    def test_painel_balanceado_no_universo_do_formulario(self) -> None:
        n_mun = self.man["universo_municipios"]["n"]
        grupos = self.val["grupos_painel"]
        self.assertIn("04", grupos)
        self.assertEqual(self.painel["co_ibge"].nunique(), n_mun)
        self.assertEqual(len(self.painel), n_mun * len(A15.COMPETENCIAS) * len(grupos))

    def test_validacoes_aprovadas(self) -> None:
        self.assertEqual(self.val["status"], "APROVADO")
        self.assertEqual(self.val["erros"], [])
        self.assertEqual(self.man["validacoes"]["status"], "APROVADO")
        for comp, v in self.val["por_competencia"].items():
            for chave in ("v1_soma_linhas_igual_total", "v2_total_mun_uf_procmes", "v3_soma_municipal_por_uf",
                          "v4_mes_processamento", "v5_carater_soma_g04", "v7_universo_municipios",
                          "v8_total_residencia_igual_internacao"):
                self.assertTrue(v[chave], (comp, chave))
            for uf, r in v["v6_uf_pequena_celula_a_celula"].items():
                self.assertTrue(r["identicas"] and r["celulas_comparadas"] > 0, (comp, uf))
            self.assertIn(v["v9_situacao_frente_ao_a13"], {"igual_a13", "revisado_na_fonte_depois_do_a13"})
            self.assertIn(v["v9_internacoes_valor_iguais_a13"], {True, None})

    def test_totais_nacionais_iguais_ao_a13_nos_meses_nao_revistos(self) -> None:
        """Recalcula a v9 a partir das validações do a13, sem usar o que o a15 gravou sobre o a13."""
        comp_a13 = self.val["comparacao_a13"]
        self.assertEqual(sorted(comp_a13["meses_iguais"] + comp_a13["meses_revisados_na_fonte"]), A15.COMPETENCIAS)
        for comp, v in self.val["por_competencia"].items():
            t13 = self.val13["por_competencia"][comp]["total_aih_por_grupo"]
            res = v["total_aih_por_grupo"]
            iguais = all(res.get(k, 0) == t13.get(k, 0) for k in set(res) | set(t13))
            self.assertEqual(iguais, comp in comp_a13["meses_iguais"], comp)
            if not iguais:
                # mês revisto: a fonte por internação, consultada na mesma execução, dá o mesmo total da residência
                self.assertEqual(res, v["total_aih_internacao_contemporaneo"], comp)
        # revisão da fonte só no fim da série: os meses revistos formam um sufixo contíguo do plano
        n = len(comp_a13["meses_revisados_na_fonte"])
        self.assertEqual(comp_a13["meses_revisados_na_fonte"], A15.COMPETENCIAS[len(A15.COMPETENCIAS) - n:])
        self.assertIn("202508", comp_a13["meses_iguais"])

    def test_ausente_fica_nan_nunca_zero(self) -> None:
        for df, cols in ((self.painel, ["aih_aprovadas", "internacoes", "valor_total"]),
                         (self.carater, ["aih_aprovadas"])):
            chave = pd.Series(list(zip(df["competencia"], df["uf"])), index=df.index)
            em_ausente = chave.isin(self.ausentes)
            self.assertTrue(df.loc[em_ausente, "status"].isin(A15.STATUS_AUSENTES).all())
            for c in cols:
                self.assertTrue(df.loc[em_ausente, c].isna().all(), c)
                self.assertFalse(df.loc[~em_ausente, c].isna().any(), c)
            self.assertTrue(set(df.loc[~em_ausente, "status"]) <= STATUS_COM_VALOR)
        ign_chave = pd.Series(list(zip(self.ign["competencia"], self.ign["uf"])), index=self.ign.index)
        self.assertTrue(self.ign.loc[ign_chave.isin(self.ausentes), "aih_aprovadas"].isna().all())

    def test_ausencia_coincide_com_totais_da_fonte(self) -> None:
        res = self.val["totais_uf_mes_aih_residencia"]
        inte = self.val["totais_uf_mes_aih_internacao"]
        self.assertEqual({(c, s) for c, d in res.items() for s, x in d.items() if x == 0},
                         {(c, r["sigla"]) for r in self.val["uf_meses_sem_dado"] for c in [r["competencia"]]})
        self.assertEqual({(c, s) for c, d in inte.items() for s, x in d.items() if x == 0},
                         {(r["competencia"], r["sigla"]) for r in self.val["uf_meses_sem_arquivo_internacao"]})
        self.assertEqual(self.man["uf_meses_sem_arquivo_internacao"], self.val["uf_meses_sem_arquivo_internacao"])

    def test_alerta_de_falta_em_outra_uf(self) -> None:
        falta = self.val["meses_com_falta_ou_atipico_em_alguma_uf_de_internacao"]
        sigla = A15.UF_CODIGO_SIGLA
        p = self.painel.drop_duplicates(["competencia", "uf"])
        for r in p.itertuples():
            esperado = bool(set(falta.get(r.competencia, [])) - {sigla[r.uf]})
            self.assertEqual(bool(r.mes_com_falta_em_outra_uf), esperado, (r.competencia, r.uf))

    def test_status_coerente_com_valor(self) -> None:
        p = self.painel
        self.assertTrue((p.loc[p["status"] == "observado", "aih_aprovadas"] > 0).all())
        self.assertTrue((p.loc[p["status"].isin(["zero_tabnet", "zero_coluna_omitida"]), "aih_aprovadas"] == 0).all())

    def test_soma_municipal_mais_ignorados_reproduz_total_do_tabnet(self) -> None:
        soma = self.painel.groupby(["competencia", "grupo"])["aih_aprovadas"].sum()
        soma_ign = self.ign.groupby(["competencia", "grupo"])["aih_aprovadas"].sum()
        meses_com_ausencia = {c for c, _ in self.ausentes}
        for comp, v in self.val["por_competencia"].items():
            for g in self.val["grupos_painel"]:
                total = v["total_aih_por_grupo"].get(g, 0)
                s = int(soma[(comp, g)]) + int(soma_ign[(comp, g)])
                if comp in meses_com_ausencia:
                    self.assertLessEqual(s, total, (comp, g))  # o parcial da UF ausente ficou fora
                else:
                    self.assertEqual(s, total, (comp, g))

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
        self.assertEqual(feitas, {(c, m) for c in A15.CONSULTAS for m in A15.COMPETENCIAS})
        for q in self.man["consultas_realizadas"]:
            fonte = A15.CONSULTAS[q["consulta"]]["fonte"]
            self.assertEqual(q["url"], A15.FONTES[fonte]["url_tab"])
            self.assertRegex(q["sha256"], r"^[0-9a-f]{64}$")
            self.assertIn("formato=prn", q["corpo_post"])
            self.assertIn(f"{fonte}{q['competencia'][2:]}.dbf", q["corpo_post"])
            self.assertTrue(q["data_hora_utc"])
        self.assertRegex(self.man["fonte"]["formulario"]["sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(self.man["fonte_conferencia"]["formulario"]["sha256"], r"^[0-9a-f]{64}$")

    def test_saidas_conferem_com_manifesto(self) -> None:
        for nome, path in (("painel", A15.PAINEL_FILE), ("carater", A15.CARATER_FILE),
                           ("ignorados", A15.IGNORADOS_FILE)):
            self.assertEqual(A15.sha256_arquivo(path), self.man["saidas"][nome]["sha256"], nome)
        self.assertEqual(A15.sha256_arquivo(A15.VALIDACOES_FILE), self.man["validacoes"]["sha256"])

    def test_doc_lista_ausencias_e_revisoes_do_manifesto(self) -> None:
        texto = DOC.read_text(encoding="utf-8")

        def bloco(nome: str) -> set[tuple[str, str]]:
            b = texto.split(f"<!-- {nome} -->")[1].split(f"<!-- /{nome} -->")[0]
            return set(re.findall(r"(\d{6}) — ([A-Z]{2})", b))

        self.assertEqual(bloco("uf_meses_sem_arquivo_internacao"),
                         {(r["competencia"], r["sigla"]) for r in self.man["uf_meses_sem_arquivo_internacao"]})
        self.assertEqual(bloco("uf_meses_sem_dado"), {(r["competencia"], r["sigla"]) for r in self.man["uf_meses_sem_dado"]})
        self.assertEqual(bloco("uf_meses_atipicos"), {(r["competencia"], r["sigla"]) for r in self.man["uf_meses_atipicos"]})
        b = texto.split("<!-- meses_revisados -->")[1].split("<!-- /meses_revisados -->")[0]
        self.assertEqual(set(re.findall(r"\b(20\d{4})\b", b)), set(self.man["comparacao_a13"]["meses_revisados_na_fonte"]))


class TestVerificarSemRede(unittest.TestCase):
    def test_verificar_nao_usa_rede_nem_grava(self) -> None:
        saidas = [A15.PAINEL_FILE, A15.CARATER_FILE, A15.IGNORADOS_FILE, A15.MANIFESTO_FILE,
                  A15.VALIDACOES_FILE, A15.RESUMO_FILE]
        antes = {p: p.stat().st_mtime_ns for p in saidas}

        def sem_rede(*_a, **_k):
            raise AssertionError("a15 em --etapa verificar tentou acessar a rede ou gravar")

        with mock.patch("urllib.request.urlopen", sem_rede), \
                mock.patch.object(A15, "gravar_parquet", sem_rede), \
                mock.patch.object(A15, "etapa_baixar", sem_rede), \
                mock.patch.object(sys, "argv", ["a15", "--etapa", "verificar"]):
            self.assertEqual(A15.main(), 0)
        self.assertEqual({p: p.stat().st_mtime_ns for p in saidas}, antes)


if __name__ == "__main__":
    unittest.main()
