"""Testes da aquisição SIA/SUS pelo TabNet (a12).

Os testes de leitura, de conjuntos e do portão usam respostas do TabNet
SINTÉTICAS, montadas em memória ou em diretório temporário: municípios 99000x,
UF "ZZ" e quantidades inventadas, que não representam nenhum dado real. Os testes
de artefato leem só as saídas versionadas em ``output/aquisicao/sia/``; o cache
de respostas brutas fica fora do Git. Nenhum teste lê IVS.
"""

from __future__ import annotations

import gzip
import hashlib
import importlib.util
import json
import re
import sys
import tempfile
import unittest
import urllib.request
from pathlib import Path
from unittest import mock

import numpy as np
import pandas as pd
import pyarrow.compute as pc
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "aquisicao" / "a12_adquirir_sia_tabnet.py"
SPEC = importlib.util.spec_from_file_location("sia_tabnet_a12", SCRIPT)
A12 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(A12)

OUT = ROOT / "output" / "aquisicao" / "sia"
PAINEL = OUT / "painel_sia_municipio_mes_subgrupo_cbo.parquet"
MANIFESTO = OUT / "manifesto_sia.json"
DOC = ROOT / "docs" / "auditorias" / "aquisicao" / "A12_sia_tabnet.md"


# ------------------------------------------------------------------ gerador SINTÉTICO

def _resposta_sintetica(rotulo_linha_html: str, subgrupos: list[str], linhas: list[tuple[str, list[int]]],
                        filtros: dict[str, str], periodo: str) -> bytes:
    """Resposta prn no formato do TabNet, SINTÉTICA. Zero vira '-' (legenda do TabNet)."""
    cab = ['"' + rotulo_linha_html + '"'] + [f'"{s} Subgrupo sintetico {s}"' for s in subgrupos] + ['"Total"']
    corpo = [";".join(cab)]
    totais = np.zeros(len(subgrupos) + 1, dtype=np.int64)
    for rotulo, vals in linhas:
        cel = list(vals) + [sum(vals)]
        totais += np.array(cel, dtype=np.int64)
        corpo.append(";".join([f'"{rotulo}"'] + [("-" if v == 0 else str(v)) for v in cel]))
    corpo.append(";".join(['"Total"'] + [("-" if v == 0 else str(int(v))) for v in totais]))
    filt = "".join(f"<b>{k}:</b> {v}<BR>\n" for k, v in filtros.items())
    txt = (
        "<HTML><BODY><H1 CLASS=\"Nivel0\"> Producao sintetica</H1>\n"
        "<b>Qtd.aprovada por Subgrupo proced. segundo X</b><br>\n"
        f"{filt}<b>Per&iacute;odo:</b> {periodo}<PRE>\n" + "\n".join(corpo) + "\n&\n</PRE></BODY></HTML>"
    )
    return txt.encode("latin-1")


class TestPlanoDeMeses(unittest.TestCase):
    def test_meses_do_protocolo_e_nada_do_ciclo3(self) -> None:
        self.assertEqual(A12.COMPETENCIAS[0], "202201")
        self.assertEqual(A12.COMPETENCIAS[-1], "202607")
        self.assertEqual(len(A12.COMPETENCIAS), 55)
        self.assertEqual(len(set(A12.COMPETENCIAS)), 55)
        self.assertTrue(all(c < "202609" for c in A12.COMPETENCIAS))
        for proibido in ("202609", "202608", "202112"):
            with self.assertRaises(RuntimeError):
                A12.checar_limite(proibido)

    def test_arquivo_e_rotulo_do_mes(self) -> None:
        self.assertEqual(A12.arquivo_do_mes("202607"), "qabr2607.dbf")
        self.assertEqual(A12.rotulo_do_mes("202602"), "Fev/2026")


class TestLeituraSintetica(unittest.TestCase):
    """Respostas SINTÉTICAS do TabNet."""

    def setUp(self) -> None:
        self.raw = _resposta_sintetica(
            "Munic&iacute;pio", ["0201", "0301"],
            [(" MUNICIPIO IGNORADO - ZZ", [0, 0]), ("990001 SINTETICO A", [3, 0]), ("990002 SINTETICO B", [0, 4]),
             ("000000 Ignorado ou exterior", [0, 0])],
            {"Profissional - CBO": "225120 Medico cardiologista"}, "Jan/2022")

    def test_traco_e_zero_e_entidade_com_ponto_e_virgula(self) -> None:
        r = A12.ler_resposta(self.raw)
        self.assertEqual(r["rotulo_linha"], "Município")  # &iacute; tem ';' dentro das aspas
        self.assertEqual([s for s, _ in r["subgrupos"]], ["0201", "0301"])
        linhas = {rot: (v, z) for rot, v, z in r["linhas"]}
        self.assertEqual(linhas["990001 SINTETICO A"], ([3, 0, 3], [False, True, False]))
        self.assertEqual(r["total"], [3, 4, 7])
        self.assertEqual(r["periodo_eco"], "Jan/2022")
        self.assertEqual(r["filtros_eco"], {"Profissional - CBO": "225120 Medico cardiologista"})
        self.assertTrue(A12.somas_conferem(r)["ok"])

    def test_zero_por_arredondamento_falha(self) -> None:
        raw = self.raw.replace(b'"990001 SINTETICO A";3', b'"990001 SINTETICO A";0')
        with self.assertRaises(A12.ErroResposta):
            A12.ler_resposta(raw)

    def test_total_incoerente_e_detectado(self) -> None:
        raw = self.raw.replace(b'"Total";3;4;7', b'"Total";3;5;8')
        self.assertFalse(A12.somas_conferem(A12.ler_resposta(raw))["ok"])

    def test_resposta_de_erro_falha(self) -> None:
        with self.assertRaisesRegex(A12.ErroResposta, "coluna n"):
            A12.ler_resposta("<H2>Múltiplos conteúdos exigem coluna não ativa.</H2>".encode("latin-1"))

    def test_eco_diferente_do_pedido_falha(self) -> None:
        r = A12.ler_resposta(self.raw)
        consulta = {"competencia": "202201", "linha": A12.LINHA_MUNICIPIO,
                    "eco_filtros": {"Profissional - CBO": "225121 Medico oncologista clinico"}}
        with self.assertRaisesRegex(A12.ErroResposta, "eco"):
            A12.conferir_eco(r, consulta)
        consulta = {"competencia": "202202", "linha": A12.LINHA_MUNICIPIO,
                    "eco_filtros": {"Profissional - CBO": "225120 Medico cardiologista"}}
        with self.assertRaisesRegex(A12.ErroResposta, "período"):
            A12.conferir_eco(r, consulta)

    def test_ausente_nunca_vira_zero_e_ignorado_fica_separado(self) -> None:
        r = A12.ler_resposta(self.raw)
        referencia = ["990001", "990002", "990003"]  # 990003 SINTÉTICO, ausente da resposta
        mm = A12.matriz_municipios(r, referencia)
        self.assertEqual(mm["presente"].tolist(), [True, True, False])
        self.assertEqual(sorted(x["rotulo_tabnet"] for x in mm["ignorados"]),
                         ["000000 Ignorado ou exterior", "MUNICIPIO IGNORADO - ZZ"])
        t = A12._tabela_painel("202201", "alvo_pmme", referencia, mm).to_pandas()
        aus = t[t["co_ibge"] == "990003"]
        self.assertEqual(set(aus["status"]), {A12.STATUS_AUSENTE})
        self.assertTrue(aus["qtd_aprovada"].isna().all())
        zer = t[(t["co_ibge"] == "990001") & (t["subgrupo"] == "0301")]
        self.assertEqual(zer["status"].tolist(), [A12.STATUS_ZERO])
        self.assertEqual(zer["qtd_aprovada"].tolist(), [0])
        self.assertNotIn("000000", set(t["co_ibge"]))
        self.assertEqual(set(t["natureza_dos_dados"]), {"EMPIRICO"})

    def test_linha_de_municipio_desconhecida_falha(self) -> None:
        with self.assertRaises(A12.ErroResposta):
            A12._classificar_linha_municipio("SEM CODIGO")


class TestSinalDeQuedaSintetico(unittest.TestCase):
    def test_sinal_na_linha_certa_com_conjuntos_intercalados(self) -> None:
        # SINTÉTICO, na ordem mês-a-mês da consolidação (conjuntos intercalados)
        cob = pd.DataFrame({
            "competencia_processamento": ["202201", "202201", "202202", "202202", "202203", "202203"],
            "conjunto_cbo": ["a", "b", "a", "b", "a", "b"],
            "municipios_com_producao": [100, 10, 100, 10, 50, 10],
            "qtd_municipios": [1000, 5, 1000, 5, 1000, 1],
        })
        s = A12.sinalizar_quedas(cob).tolist()
        self.assertEqual([bool(x) for x in s], [False, False, False, False, True, True])
        self.assertIn("municípios", s[4])
        self.assertNotIn("quantidade", s[4])
        self.assertIn("quantidade", s[5])
        self.assertNotIn("municípios", s[5])


class TestConjuntosPelaRegraDoA09(unittest.TestCase):
    def test_regra_do_a09(self) -> None:
        alvo, _, _ = A12.a09.carregar_ponte()
        codigos = sorted(set(alvo) | {"225125", "225142", "225170", "225130", "225133", "2231F9", "223106", "515105"})
        g = A12.classificar_cbos(codigos, alvo)
        self.assertEqual(g["alvo_pmme"], sorted(alvo))
        self.assertEqual(g["generalistas"], ["225125", "225142", "225170"])
        self.assertEqual(g["mfc_225130"], ["225130"])
        self.assertEqual(g["especialistas_nao_alvo"], ["225130", "225133"])
        todos = set().union(*g.values())
        for fora in ("2231F9", "223106", "515105"):
            self.assertNotIn(fora, todos)

    def test_alvo_ausente_do_formulario_falha(self) -> None:
        alvo, _, _ = A12.a09.carregar_ponte()
        with self.assertRaises(A12.ErroResposta):
            A12.classificar_cbos(["225125"], alvo)


class TestPortaoFailClosedSintetico(unittest.TestCase):
    """Consolidação de um mês SINTÉTICO com todas as consultas em cache temporário.

    Controle positivo: respostas coerentes passam e gravam (no diretório temporário).
    Negativos: uma consulta faltando ou um total de conjunto que não bate com a soma
    das CBO param a consolidação sem gravar nada.
    """

    COMP = "202201"
    CONJ = {
        "alvo_pmme": [{"indice": "1", "co_cbo": "225120", "rotulo": "225120 Medico cardiologista"}],
        "especialistas_nao_alvo": [{"indice": "2", "co_cbo": "225130", "rotulo": "225130 Medico de familia e comunidade"}],
        "generalistas": [{"indice": "3", "co_cbo": "225125", "rotulo": "225125 Medico clinico"}],
        "mfc_225130": [{"indice": "2", "co_cbo": "225130", "rotulo": "225130 Medico de familia e comunidade"}],
    }
    MUNIS = [{"co_ibge": "990001", "nome_tabnet": "SINTETICO A", "co_uf": "99", "sigla_uf": "ZZ"},
             {"co_ibge": "990002", "nome_tabnet": "SINTETICO B", "co_uf": "99", "sigla_uf": "ZZ"}]
    # (CBO, município, subgrupo) -> quantidade, tudo SINTÉTICO; 515105 não é médico
    DADOS = {("225120", "990001", "0301"): 5, ("225130", "990002", "0301"): 2,
             ("225125", "990001", "0201"): 7, ("515105", "990002", "0301"): 10}

    def _resposta(self, consulta: dict, dados: dict) -> bytes:
        c = consulta["conjunto_cbo"]
        cbos = None if c == A12.TODOS else {o["co_cbo"] for o in self.CONJ[c]}
        sel = {k: v for k, v in dados.items() if cbos is None or k[0] in cbos}
        subs = sorted({k[2] for k, v in sel.items() if v})
        periodo = A12.rotulo_do_mes(self.COMP)
        if consulta["tipo"] in ("municipio", "conferencia_uf"):
            linhas = [(" MUNICIPIO IGNORADO - ZZ", [0] * len(subs))]
            for m in self.MUNIS:
                linhas.append((f"{m['co_ibge']} {m['nome_tabnet']}",
                               [sum(v for k, v in sel.items() if k[1] == m["co_ibge"] and k[2] == s) for s in subs]))
            linhas.append(("000000 Ignorado ou exterior", [0] * len(subs)))
            return _resposta_sintetica("Munic&iacute;pio", subs, linhas, consulta["eco_filtros"], periodo)
        if consulta["tipo"] == "uf":
            return _resposta_sintetica("UF", subs, [("99 Zeta", [sum(v for k, v in sel.items() if k[2] == s) for s in subs])],
                                       {}, periodo)
        cbos_com = sorted({k[0] for k, v in sel.items() if v})
        linhas = [(f"{cb} CBO sintetica", [sum(v for k, v in sel.items() if k[0] == cb and k[2] == s) for s in subs])
                  for cb in cbos_com]
        return _resposta_sintetica("Profissional - CBO", subs, linhas, {}, periodo)

    def _rodar(self, alterar=None, omitir=None) -> tuple[int, Path]:
        tmp = Path(self.tmp.name)
        saida, cache = tmp / "saida", tmp / "brutos"
        saida.mkdir()
        cache.mkdir()
        alvos = {n: saida / getattr(A12, n).name for n in
                 ("PAINEL_FILE", "IGNORADOS_FILE", "UF_FILE", "CBO_FILE", "SUBGRUPOS_FILE", "COBERTURA_FILE",
                  "CONJUNTOS_FILE", "MUNICIPIOS_FILE", "MANIFESTO_FILE", "RESUMO_FILE")}
        opcoes = [o for lst in self.CONJ.values() for o in lst]
        with mock.patch.multiple(A12, OUT_DIR=saida, CACHE_DIR=cache, MES_CONFERENCIA_UF=self.COMP,
                                 UFS_CONFERENCIA={"ZZ": "Zeta"}, **alvos), \
                mock.patch.object(A12, "carregar_formulario", return_value={"selects": {}}), \
                mock.patch.object(A12, "conjuntos_do_formulario", return_value=self.CONJ), \
                mock.patch.object(A12, "municipios_do_formulario", return_value=(self.MUNIS, {"ZZ": "99"})), \
                mock.patch.object(A12, "indice_uf", return_value="1"), \
                mock.patch.object(A12, "opcoes_cbo", return_value=opcoes):
            (cache / f"{A12.FORMULARIO_ID}.json").write_text(json.dumps(
                {"data_hora_utc": "sintetico", "sha256_resposta": "0" * 64, "bytes_resposta": 0}))
            for q in A12.planejar_consultas({}, [self.COMP]):
                if q["id"] == omitir:
                    continue
                raw = self._resposta(q, self.DADOS)
                if alterar and q["id"] == alterar[0]:
                    for velho, novo in alterar[1]:
                        self.assertIn(velho, raw)
                        raw = raw.replace(velho, novo)
                A12._gravar_cache(q["id"], raw, {"id": q["id"], "status": "ok", "corpo_post": A12.corpo_post(q["campos"]),
                                                 "sha256_resposta": hashlib.sha256(raw).hexdigest()})
            codigo = A12.consolidar([self.COMP])
        return codigo, saida

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_controle_positivo(self) -> None:
        codigo, saida = self._rodar()
        self.assertEqual(codigo, 0)
        p = pd.read_parquet(saida / A12.PAINEL_FILE.name)
        self.assertEqual(set(p["natureza_dos_dados"]), {"EMPIRICO"})
        todos = p[p["conjunto_cbo"] == A12.TODOS].set_index(["co_ibge", "subgrupo"])["qtd_aprovada"]
        self.assertEqual(todos[("990002", "0301")], 12)
        self.assertEqual(todos[("990002", "0201")], 0)
        man = json.loads((saida / A12.MANIFESTO_FILE.name).read_text(encoding="utf-8"))
        self.assertTrue(all(v["status"] in ("APROVADO", "RELATO") for v in man["validacoes"].values()))

    def test_consulta_faltando_nao_grava(self) -> None:
        codigo, saida = self._rodar(omitir=f"cbo_{A12.TODOS}_{self.COMP}")
        self.assertEqual(codigo, 2)
        self.assertEqual(list(saida.iterdir()), [])

    def test_total_do_conjunto_diferente_da_soma_das_cbo_nao_grava(self) -> None:
        # alvo: 990001/0301 passa de 5 para 6 e o Total junto (V1 continua coerente); a consulta
        # por CBO não muda, então só a V4 (conjunto = soma das suas CBO) pode reprovar
        trocas = [(b'"990001 SINTETICO A";5;5', b'"990001 SINTETICO A";6;6'), (b'"Total";5;5', b'"Total";6;6')]
        with mock.patch.object(A12, "log") as log:
            codigo, saida = self._rodar(alterar=(f"municipio_alvo_pmme_{self.COMP}", trocas))
        self.assertEqual(codigo, 2)
        self.assertEqual(list(saida.iterdir()), [])
        mensagens = " ".join(str(c.args[0]) for c in log.call_args_list)
        self.assertIn("V4_conjunto_contra_soma_das_cbo", mensagens)
        self.assertNotIn("V1_total_igual_soma_das_linhas", mensagens)


@unittest.skipUnless(PAINEL.exists() and MANIFESTO.exists(), "saídas do a12 ausentes")
class TestSaidasVersionadas(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.man = json.loads(MANIFESTO.read_text(encoding="utf-8"))
        cls.sub = pd.read_csv(OUT / "sia_subgrupos_por_consulta.csv",
                              dtype={"competencia_processamento": str, "subgrupo": str})
        pf = pq.ParquetFile(PAINEL)
        cls.esquema = pf.schema_arrow
        # agregação por grupo de linhas (um por mês × conjunto), sem carregar o painel inteiro
        totais, status_qtd, naturezas = [], set(), set()
        for i in range(pf.num_row_groups):
            t = pf.read_row_group(i)
            naturezas |= set(pc.unique(t.column("natureza_dos_dados").cast("string")).to_pylist())
            df = pd.DataFrame({c: t.column(c).cast("string").to_numpy(zero_copy_only=False)
                               for c in ("competencia_processamento", "conjunto_cbo", "subgrupo", "status")})
            df["qtd"] = t.column("qtd_aprovada").to_pandas()
            for s, parte in df.groupby("status"):
                q = parte["qtd"]
                status_qtd.add((s, bool(q.isna().all()), bool(q.notna().all()),
                                bool((q.dropna() > 0).all()), bool((q.dropna() == 0).all())))
            totais.append(df.groupby(["competencia_processamento", "conjunto_cbo", "subgrupo"])["qtd"]
                          .agg(qtd_painel=lambda q: q.sum(min_count=1), linhas="size").reset_index())
        tot = pd.concat(totais, ignore_index=True)
        cls.totais = tot.groupby(["competencia_processamento", "conjunto_cbo", "subgrupo"], as_index=False).agg(
            qtd_painel=("qtd_painel", lambda q: q.sum(min_count=1)), linhas=("linhas", "sum"))
        cls.status_qtd = status_qtd
        cls.naturezas = naturezas
        cls.linhas_por = cls.totais.groupby(["competencia_processamento", "conjunto_cbo"])["linhas"].sum().to_dict()
        cls.comps = set(cls.totais["competencia_processamento"])
        cls.conjs = set(cls.totais["conjunto_cbo"])

    def test_natureza_empirica(self) -> None:
        self.assertEqual(self.naturezas, {"EMPIRICO"})
        self.assertEqual(self.man["natureza_dos_dados"], "EMPIRICO")

    def test_esquema(self) -> None:
        self.assertEqual(self.esquema.names, A12.COLUNAS_PAINEL)
        self.assertEqual(str(self.esquema.field("qtd_aprovada").type), "int64")

    def test_meses_e_conjuntos(self) -> None:
        self.assertEqual(sorted(self.comps), A12.COMPETENCIAS)
        self.assertTrue(all(c < "202609" for c in self.comps))
        self.assertEqual(self.conjs, set(A12.CONJUNTOS))
        self.assertEqual(self.man["competencias_obtidas"], A12.COMPETENCIAS)

    def test_status_coerente_e_ausente_nunca_zero(self) -> None:
        for s, so_nulos, sem_nulos, positivos, zeros in self.status_qtd:
            self.assertIn(s, A12.STATUS_VALIDOS)
            if s == A12.STATUS_AUSENTE:
                self.assertTrue(so_nulos, s)
            else:
                self.assertTrue(sem_nulos, s)
            if s == A12.STATUS_VALOR:
                self.assertTrue(positivos)
            if s == A12.STATUS_ZERO:
                self.assertTrue(zeros)

    def test_painel_denso_nas_colunas_da_resposta(self) -> None:
        # linhas por mês × conjunto = municípios (lista do formulário) × subgrupos presentes na resposta
        pres = self.sub[self.sub["presente_na_resposta"]].groupby(["competencia_processamento", "conjunto_cbo"]).size()
        n_mun = self.man["municipios_do_formulario"]
        fora = self.man["validacoes"]["V6_cobertura"]["municipios_fora_da_lista_do_formulario"]
        for (comp, conj), n in pres.items():
            extra = len(fora.get(f"{conj}_{comp}", []))
            self.assertEqual(self.linhas_por[(comp, conj)], (n_mun + extra) * n, (comp, conj))

    def test_soma_dos_municipios_mais_ignorados_igual_total_tabnet(self) -> None:
        ign = pd.read_parquet(OUT / "sia_municipio_ignorado_mes_subgrupo_cbo.parquet")
        self.assertEqual(set(ign["natureza_dos_dados"]), {"EMPIRICO"})
        gi = ign.groupby(["competencia_processamento", "conjunto_cbo", "subgrupo"])["qtd_aprovada"].sum()
        t = self.totais.set_index(["competencia_processamento", "conjunto_cbo", "subgrupo"])["qtd_painel"]
        s = self.sub[self.sub["presente_na_resposta"]].set_index(
            ["competencia_processamento", "conjunto_cbo", "subgrupo"])["total_tabnet_municipio"]
        self.assertEqual(len(s), len(t))
        for k, total in s.items():
            self.assertEqual(int(t[k]) + int(gi.get(k, 0)), int(total), k)

    def test_conjuntos_nao_excedem_todos_e_batem_com_cbo(self) -> None:
        s = self.sub
        piv = s.pivot_table(index=["competencia_processamento", "subgrupo"], columns="conjunto_cbo",
                            values="total_soma_cbo", aggfunc="sum")
        tot = s[s["conjunto_cbo"] == A12.TODOS].set_index(["competencia_processamento", "subgrupo"])["total_tabnet_municipio"]
        disj = piv[list(A12.CONJUNTOS_DISJUNTOS)].sum(axis=1)
        self.assertTrue((disj <= tot.reindex(disj.index)).all())
        conj = s[s["conjunto_cbo"] != A12.TODOS]
        pres = conj[conj["presente_na_resposta"]]
        self.assertTrue((pres["total_tabnet_municipio"] == pres["total_soma_cbo"]).all())
        # subgrupo ausente da resposta de um conjunto: nenhuma produção nas CBO do conjunto
        self.assertTrue((conj.loc[~conj["presente_na_resposta"], "total_soma_cbo"] == 0).all())
        self.assertTrue(conj.loc[~conj["presente_na_resposta"], "total_tabnet_municipio"].isna().all())

    def test_todos_igual_consulta_por_uf(self) -> None:
        uf = pd.read_parquet(OUT / "sia_uf_mes_subgrupo_todos.parquet")
        self.assertEqual(set(uf["natureza_dos_dados"]), {"EMPIRICO"})
        g = uf.groupby(["competencia_processamento", "subgrupo"])["qtd_aprovada"].sum()
        t = self.sub[self.sub["conjunto_cbo"] == A12.TODOS].set_index(["competencia_processamento", "subgrupo"])
        self.assertTrue((t["total_tabnet_municipio"] == g.reindex(t.index)).all())
        self.assertTrue((t["total_tabnet_municipio"] == t["total_tabnet_uf"]).all())

    def test_validacoes_aprovadas(self) -> None:
        for k, v in self.man["validacoes"].items():
            self.assertIn(v["status"], ("APROVADO", "RELATO"), k)
        conf = self.man["validacoes"]["V5_conferencia_uf_celula_a_celula"]["resultados"]
        self.assertEqual({(r["uf"], r["conjunto_cbo"]) for r in conf},
                         {(u, c) for u in A12.UFS_CONFERENCIA for c in A12.CONJUNTOS})
        self.assertGreater(sum(r["celulas_comparadas"] for r in conf), 0)

    def test_proveniencia_de_cada_consulta(self) -> None:
        lista = self.man["consultas"]["lista"]
        self.assertEqual(len(lista), self.man["consultas"]["n"])
        self.assertEqual(len({q["id"] for q in lista}), len(lista))
        for q in lista:
            self.assertEqual(q["status"], "ok", q["id"])
            self.assertRegex(q["sha256_resposta"], r"^[0-9a-f]{64}$")
            self.assertEqual(q["url"], A12.URL_CONSULTA)
            self.assertIn("Arquivos=qabr", q["corpo_post"])
            self.assertTrue(q["data_hora_utc"])
            self.assertLess(q["competencia"], "202609")
            self.assertLessEqual(q["competencia"], "202607")
        self.assertRegex(self.man["fonte"]["formulario"]["sha256_resposta"], r"^[0-9a-f]{64}$")

    def test_sinal_de_queda_recalculado_da_cobertura(self) -> None:
        cob = pd.read_csv(OUT / "sia_cobertura_mes.csv", dtype={"competencia_processamento": str}, keep_default_na=False)
        for c, parte in cob.groupby("conjunto_cbo"):
            mm = parte["municipios_com_producao"].median()
            mq = parte["qtd_municipios"].median()
            for r in parte.itertuples(index=False):
                self.assertEqual("municípios" in r.sinal_queda, r.municipios_com_producao < A12.LIMIAR_QUEDA_MUNICIPIOS * mm)
                self.assertEqual("quantidade" in r.sinal_queda, r.qtd_municipios < A12.LIMIAR_QUEDA_TOTAL * mq)
        self.assertEqual(len(self.man["validacoes"]["V6_cobertura"]["meses_sinalizados"]), int((cob["sinal_queda"] != "").sum()))

    def test_hashes_das_saidas(self) -> None:
        for rel, info in self.man["saidas"].items():
            self.assertEqual(A12.sha256_arquivo(ROOT / rel), info["sha256"], rel)

    def test_csvs_empiricos(self) -> None:
        for nome in ("sia_subgrupos_por_consulta.csv", "sia_cobertura_mes.csv", "sia_conjuntos_cbo.csv",
                     "sia_municipios_tabnet.csv"):
            df = pd.read_csv(OUT / nome, dtype=str)
            self.assertEqual(set(df["natureza_dos_dados"]), {"EMPIRICO"}, nome)
        cbo = pd.read_parquet(OUT / "sia_nacional_cbo_mes_subgrupo.parquet")
        self.assertEqual(set(cbo["natureza_dos_dados"]), {"EMPIRICO"})

    def test_conjuntos_reproduzem_o_a09(self) -> None:
        cj = pd.read_csv(OUT / "sia_conjuntos_cbo.csv", dtype=str)
        alvo, _, _ = A12.a09.carregar_ponte()
        self.assertEqual(sorted(cj.loc[cj["conjunto_cbo"] == "alvo_pmme", "co_cbo"]), sorted(alvo))
        self.assertEqual(sorted(cj.loc[cj["conjunto_cbo"] == "generalistas", "co_cbo"]), sorted(A12.a09.GENERALISTAS))
        for c, lst in self.man["conjuntos_cbo"]["listas"].items():
            self.assertEqual(sorted(o["co_cbo"] for o in lst), sorted(cj.loc[cj["conjunto_cbo"] == c, "co_cbo"]), c)

    def test_numeros_do_documento_saem_do_manifesto(self) -> None:
        texto = " ".join(DOC.read_text(encoding="utf-8").split())
        cob = pd.read_csv(OUT / "sia_cobertura_mes.csv", dtype={"competencia_processamento": str})
        esperados = {
            "meses": len(self.man["competencias_obtidas"]),
            "consultas": self.man["consultas"]["n"],
            "municipios": self.man["municipios_do_formulario"],
            "alvo_cbo": len(self.man["conjuntos_cbo"]["listas"]["alvo_pmme"]),
            "nao_alvo_cbo": len(self.man["conjuntos_cbo"]["listas"]["especialistas_nao_alvo"]),
            "meses_sinalizados": len(self.man["validacoes"]["V6_cobertura"]["meses_sinalizados"]),
        }
        for chave, valor in esperados.items():
            m = re.search(r"<!--n:" + chave + r"-->(\d+)", texto)
            self.assertIsNotNone(m, chave)
            self.assertEqual(int(m.group(1)), valor, chave)
        self.assertGreater(len(cob), 0)

    def test_afirmacoes_do_documento(self) -> None:
        """Cada afirmação factual da seção 6 do doc A12, conferida contra as saídas."""
        self.assertEqual(self.man["consultas"]["com_mais_de_uma_tentativa"], [])
        v6 = self.man["validacoes"]["V6_cobertura"]
        self.assertEqual(v6["municipios_ausentes_da_resposta"], {})
        self.assertEqual(v6["municipios_fora_da_lista_do_formulario"], {})
        self.assertNotIn(A12.STATUS_AUSENTE, {s for s, *_ in self.status_qtd})
        ign = pd.read_parquet(OUT / "sia_municipio_ignorado_mes_subgrupo_cbo.parquet")
        self.assertEqual(int(ign["qtd_aprovada"].sum()), 0)
        sinal = {(x["competencia_processamento"], x["conjunto_cbo"]) for x in v6["meses_sinalizados"]
                 if "municípios" in x["sinal_queda"]}
        for chave in (("202606", A12.TODOS), ("202607", A12.TODOS), ("202607", "alvo_pmme"),
                      ("202607", "especialistas_nao_alvo"), ("202607", "generalistas")):
            self.assertIn(chave, sinal)
        oci = self.sub[self.sub["subgrupo"].str.startswith("09") & self.sub["presente_na_resposta"]
                       & (self.sub["conjunto_cbo"] == A12.TODOS)]
        self.assertGreater(oci["competencia_processamento"].min(), "202406")
        t = self.sub[self.sub["conjunto_cbo"] == A12.TODOS].groupby("competencia_processamento")[
            ["total_tabnet_municipio", "producao_sem_cbo_na_tabela"]].sum()
        self.assertTrue(((t["producao_sem_cbo_na_tabela"] / t["total_tabnet_municipio"]) < 0.05).all())

    def test_tamanho_versionado(self) -> None:
        self.assertLess(PAINEL.stat().st_size, 60 * 1024**2)


class TestPipelineSemRede(unittest.TestCase):
    def test_run_all_so_verifica(self) -> None:
        spec = importlib.util.spec_from_file_location("run_all_a12", ROOT / "run_all.py")
        ra = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ra)
        self.assertIn(SCRIPT, ra.STEPS)
        self.assertEqual(ra.ARGUMENTOS[SCRIPT], ["--etapa", "verificar"])
        self.assertLess(ra.STEPS.index(ROOT / "scripts" / "aquisicao" / "01_congelar_ponte_cbo.py"), ra.STEPS.index(SCRIPT))

    @unittest.skipUnless(MANIFESTO.exists(), "saídas do a12 ausentes")
    def test_verificar_nao_usa_rede_nem_grava(self) -> None:
        antes = {p: A12.sha256_arquivo(p) for p in OUT.iterdir() if p.is_file()}

        def sem_rede(*_a, **_k):
            raise AssertionError("a12 em --etapa verificar tentou acessar a rede")
        with mock.patch.object(urllib.request, "urlopen", sem_rede), \
                mock.patch.object(A12, "consolidar", sem_rede), \
                mock.patch.object(sys, "argv", ["a12", "--etapa", "verificar"]):
            self.assertEqual(A12.main(), 0)
        depois = {p: A12.sha256_arquivo(p) for p in OUT.iterdir() if p.is_file()}
        self.assertEqual(antes, depois)


if __name__ == "__main__":
    unittest.main()
