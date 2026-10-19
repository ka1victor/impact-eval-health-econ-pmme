"""Testes da aquisição a17: SIA/SUS no TabNet por município × mês × forma de organização × curso.

Os testes de leitura, de plano e do portão usam respostas do TabNet SINTÉTICAS,
montadas em memória ou em diretório temporário: municípios 99000x, UF "ZZ", CBO
2259xx e cursos 91–93, com quantidades inventadas que não representam nenhum dado
real. Os testes de artefato leem só as saídas versionadas em
``output/aquisicao/sia_forma_curso/``; o cache de respostas brutas fica fora do
Git. Nenhum teste lê IVS.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np
import pandas as pd
import pyarrow.compute as pc
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "aquisicao" / "a17_adquirir_sia_forma_curso.py"
SPEC = importlib.util.spec_from_file_location("sia_forma_curso_a17", SCRIPT)
A17 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(A17)

OUT = ROOT / "output" / "aquisicao" / "sia_forma_curso"
PAINEL = OUT / "painel_sia_municipio_mes_forma_curso.parquet"
MANIFESTO = OUT / "manifesto_sia_forma_curso.json"
DOC = ROOT / "docs" / "auditorias" / "aquisicao" / "A17_sia_forma_curso.md"


def _resposta_sintetica(rotulo_linha_html: str, formas: list[str], linhas: list[tuple[str, list[int]]],
                        filtros: dict[str, str], periodo: str) -> bytes:
    """Resposta prn no formato do TabNet, SINTÉTICA, com colunas de forma de organização."""
    cab = ['"' + rotulo_linha_html + '"'] + [f'"{f} Forma sintetica {f}"' for f in formas] + ['"Total"']
    corpo = [";".join(cab)]
    totais = np.zeros(len(formas) + 1, dtype=np.int64)
    for rotulo, vals in linhas:
        cel = list(vals) + [sum(vals)]
        totais += np.array(cel, dtype=np.int64)
        corpo.append(";".join([f'"{rotulo}"'] + [("-" if v == 0 else str(v)) for v in cel]))
    corpo.append(";".join(['"Total"'] + [("-" if v == 0 else str(int(v))) for v in totais]))
    filt = "".join(f"<b>{k}:</b> {v}<BR>\n" for k, v in filtros.items())
    txt = ("<HTML><BODY><H1 CLASS=\"Nivel0\"> Producao sintetica</H1>\n"
           "<b>Qtd.aprovada por Forma organiza&ccedil;&atilde;o segundo X</b><br>\n"
           f"{filt}<b>Per&iacute;odo:</b> {periodo}<PRE>\n" + "\n".join(corpo) + "\n&\n</PRE></BODY></HTML>")
    return txt.encode("latin-1")


def _resposta_procedimento(procs: dict[str, dict[str, int]], formas: list[str] | None, filtros: dict[str, str],
                           periodo: str) -> bytes:
    """Resposta SINTÉTICA Linha = Procedimento: sem coluna (formas=None) ou com colunas de forma."""
    if formas is None:
        cab = '"Procedimento";"Qtd.aprovada"'
        corpo = [cab] + [f'"{c} PROCEDIMENTO SINTETICO";{sum(v.values())}' for c, v in sorted(procs.items())]
        corpo.append(f'"Total";{sum(sum(v.values()) for v in procs.values())}')
    else:
        cab = ";".join(['"Procedimento"'] + [f'"{f} Forma sintetica"' for f in formas] + ['"Total"'])
        corpo = [cab]
        for c, v in sorted(procs.items()):
            cel = [v.get(f, 0) for f in formas]
            corpo.append(";".join([f'"{c} PROCEDIMENTO SINTETICO"'] + [("-" if x == 0 else str(x)) for x in cel + [sum(cel)]]))
        tot = [sum(v.get(f, 0) for v in procs.values()) for f in formas]
        corpo.append(";".join(['"Total"'] + [("-" if x == 0 else str(x)) for x in tot + [sum(tot)]]))
    filt = "".join(f"<b>{k}:</b> {v}<BR>\n" for k, v in filtros.items())
    txt = ("<HTML><BODY><H1 CLASS=\"Nivel0\"> Producao sintetica</H1>\n<b>Qtd.aprovada segundo Procedimento</b><br>\n"
           f"{filt}<b>Per&iacute;odo:</b> {periodo}<PRE>\n" + "\n".join(corpo) + "\n&\n</PRE></BODY></HTML>")
    return txt.encode("latin-1")


class TestPlanoECursos(unittest.TestCase):
    def test_meses_do_a12_e_nada_do_ciclo3(self) -> None:
        self.assertEqual(A17.COMPETENCIAS, A17.a12.COMPETENCIAS)
        self.assertEqual((A17.COMPETENCIAS[0], A17.COMPETENCIAS[-1], len(A17.COMPETENCIAS)), ("202201", "202607", 55))
        self.assertTrue(all(c < "202609" for c in A17.COMPETENCIAS))
        for proibido in ("202609", "202608", "202112"):
            with self.assertRaises(RuntimeError):
                A17.checar_limite(proibido)

    def test_instancia_propria_do_a12(self) -> None:
        # o a17 troca o cache e o padrão de coluna só na própria instância do a12
        spec = importlib.util.spec_from_file_location("a12_limpo", ROOT / "scripts" / "aquisicao" / "a12_adquirir_sia_tabnet.py")
        limpo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(limpo)
        self.assertEqual(limpo.CACHE_DIR, ROOT / "output" / "aquisicao" / "sia" / "brutos")
        self.assertEqual(limpo.RE_SUBGRUPO.pattern, r"^(\d{4}) (.*)$")
        self.assertEqual(A17.a12.CACHE_DIR, A17.CACHE_DIR)
        self.assertEqual(A17.a12.RE_SUBGRUPO.pattern, r"^(\d{6}) (.*)$")

    def test_cursos_especificos_do_g4_e_cbo_da_ponte(self) -> None:
        g4 = json.loads((ROOT / "output" / "rdd_bolsa" / "G4_resumo.json").read_text(encoding="utf-8"))
        cursos = A17.cursos_especificos()
        self.assertEqual([c["cod_curso"] for c in cursos], sorted(g4["classes_dos_cursos"]["ESPECIFICO"]))
        por = {int(c["cod_curso"]): sorted(c["cbos"]) for c in g4["por_curso"]}
        for c in cursos:
            self.assertEqual(c["cbos"], por[c["cod_curso"]])

    def test_conjuntos_distintos_e_contencao(self) -> None:
        cursos = [{"cod_curso": 93, "cbos": ["225901"]}, {"cod_curso": 91, "cbos": ["225901", "225902"]},
                  {"cod_curso": 92, "cbos": ["225901"]}]
        conj = A17.conjuntos_dos_cursos(cursos)
        self.assertEqual(list(conj), ["c91", "c92_c93"])
        self.assertEqual(conj["c92_c93"]["cursos"], [92, 93])
        self.assertEqual(A17.contencoes(conj), [("c92_c93", "c91")])


class TestLeituraSintetica(unittest.TestCase):
    def setUp(self) -> None:
        self.raw = _resposta_sintetica(
            "Munic&iacute;pio", ["020901", "030101"],
            [(" MUNICIPIO IGNORADO - ZZ", [0, 1]), ("990001 SINTETICO A", [3, 0]), ("990002 SINTETICO B", [0, 4]),
             ("000000 Ignorado ou exterior", [0, 0])],
            {"Profissional - CBO": "225901 Medico sintetico"}, "Jan/2022")

    def test_colunas_de_forma(self) -> None:
        r = A17.ler_resposta(self.raw)
        self.assertEqual([f for f, _ in r["formas"]], ["020901", "030101"])
        self.assertEqual(r["total"], [3, 5, 8])
        self.assertTrue(A17.a12.somas_conferem(r)["ok"])

    def test_coluna_de_subgrupo_falha(self) -> None:
        raw = _resposta_sintetica("Munic&iacute;pio", ["0209"], [("990001 SINTETICO A", [3])], {}, "Jan/2022")
        with self.assertRaises(A17.ErroResposta):
            A17.ler_resposta(raw)

    def test_ausente_nunca_vira_zero(self) -> None:
        r = A17.ler_resposta(self.raw)
        referencia = ["990001", "990002", "990003"]  # 990003 SINTÉTICO, ausente da resposta
        mm = A17.a12.matriz_municipios(r, referencia)
        t = A17._tabela_painel("202201", 91, referencia, mm).to_pandas()
        self.assertEqual(list(t.columns), A17.COLUNAS_PAINEL)
        aus = t[t["co_ibge"] == "990003"]
        self.assertEqual(set(aus["status"]), {A17.STATUS_AUSENTE})
        self.assertTrue(aus["qtd_aprovada"].isna().all())
        zer = t[(t["co_ibge"] == "990001") & (t["forma"] == "030101")]
        self.assertEqual((zer["status"].tolist(), zer["qtd_aprovada"].tolist()), ([A17.STATUS_ZERO], [0]))
        self.assertNotIn("000000", set(t["co_ibge"]))
        self.assertEqual(set(t["cod_curso"]), {91})
        self.assertEqual(set(t["natureza_dos_dados"]), {"EMPIRICO"})


class TestPortaoFailClosedSintetico(unittest.TestCase):
    """Consolidação de um mês SINTÉTICO com todas as consultas em cache temporário."""

    COMP = "202201"
    CURSOS = [{"cod_curso": 91, "no_curso": "CURSO SINTETICO 91", "cbos": ["225901", "225902"]},
              {"cod_curso": 92, "no_curso": "CURSO SINTETICO 92", "cbos": ["225901"]},
              {"cod_curso": 93, "no_curso": "CURSO SINTETICO 93", "cbos": ["225901"]}]
    OPCOES = {"c91": [{"indice": "1", "co_cbo": "225901", "rotulo": "225901 Medico sintetico um"},
                      {"indice": "2", "co_cbo": "225902", "rotulo": "225902 Medico sintetico dois"}],
              "c92_c93": [{"indice": "1", "co_cbo": "225901", "rotulo": "225901 Medico sintetico um"}]}
    MUNIS = [{"co_ibge": "990001", "nome_tabnet": "SINTETICO A", "co_uf": "99", "sigla_uf": "ZZ"},
             {"co_ibge": "990002", "nome_tabnet": "SINTETICO B", "co_uf": "99", "sigla_uf": "ZZ"}]
    # (CBO, município, forma) -> quantidade, tudo SINTÉTICO
    DADOS = {("225901", "990001", "020901"): 5, ("225902", "990002", "020901"): 2,
             ("225901", "990002", "030101"): 7}

    # procedimento SINTÉTICO cuja forma (039999) não está na tabela de formas: some com Coluna = Forma
    FORA = {"0399990001": 3}

    def _resposta(self, q: dict) -> bytes:
        if q["tipo"].startswith("diag_procedimento"):
            procs: dict[str, dict[str, int]] = {}
            for (cb, _, f), v in self.DADOS.items():
                procs.setdefault(f + "0001", {}).setdefault(f, 0)
                procs[f + "0001"][f] += v
            if q["tipo"].endswith("sem_coluna"):
                for c, v in self.FORA.items():
                    procs[c] = {"fora": v}
                return _resposta_procedimento(procs, None, q["eco_filtros"], A17.a12.rotulo_do_mes(self.COMP))
            formas = sorted({f for (_, _, f), v in self.DADOS.items() if v})
            return _resposta_procedimento(procs, formas, q["eco_filtros"], A17.a12.rotulo_do_mes(self.COMP))
        cbos = {"225901", "225902"} if q["tipo"] == "cbo" else {o["co_cbo"] for o in self.OPCOES[q["conjunto_cbo"]]}
        sel = {k: v for k, v in self.DADOS.items() if k[0] in cbos}
        formas = sorted({k[2] for k, v in sel.items() if v})
        periodo = A17.a12.rotulo_do_mes(self.COMP)
        if q["tipo"] in ("municipio", "conferencia_uf"):
            linhas = [(" MUNICIPIO IGNORADO - ZZ", [0] * len(formas))]
            for m in self.MUNIS:
                linhas.append((f"{m['co_ibge']} {m['nome_tabnet']}",
                               [sum(v for k, v in sel.items() if k[1] == m["co_ibge"] and k[2] == f) for f in formas]))
            linhas.append(("000000 Ignorado ou exterior", [0] * len(formas)))
            return _resposta_sintetica("Munic&iacute;pio", formas, linhas, q["eco_filtros"], periodo)
        linhas = [(f"{cb} CBO sintetica", [sum(v for k, v in sel.items() if k[0] == cb and k[2] == f) for f in formas])
                  for cb in sorted({k[0] for k, v in sel.items() if v})]
        return _resposta_sintetica("Profissional - CBO", formas, linhas, q["eco_filtros"], periodo)

    def _rodar(self, alterar=None, omitir=None) -> tuple[int, Path, list[str]]:
        tmp = Path(self.tmp.name)
        saida, cache = tmp / "saida", tmp / "brutos"
        saida.mkdir()
        cache.mkdir()
        tip = tmp / "tipicas.csv"
        pd.DataFrame({"cod_curso": [91, 92], "co_forma": ["020901", "030101"], "no_forma": ["F1", "F2"],
                      "co_subgrupo": ["0209", "0301"], "participacao_na_producao_do_curso": [0.6, 0.9],
                      "classe_especificidade": ["alta", "baixa"], "tipica": [True, True]}).to_csv(tip, index=False)
        alvos = {n: saida / getattr(A17, n).name for n in
                 ("PAINEL_FILE", "IGNORADOS_FILE", "CBO_FILE", "FORMAS_FILE", "COBERTURA_FILE", "CRUZAMENTO_FILE",
                  "CURSOS_FILE", "TIPICAS_FILE", "PROC_FILE", "MANIFESTO_FILE", "RESUMO_FILE")}
        mensagens: list[str] = []
        with mock.patch.multiple(A17, OUT_DIR=saida, CACHE_DIR=cache, MES_CONFERENCIA_UF=self.COMP,
                                 UFS_CONFERENCIA={"ZZ": "Zeta"}, G4_MAPA=tip, A12_CBO_V1=tmp / "nao_existe_v1.parquet",
                                 A12_CBO_V2=tmp / "nao_existe_v2.parquet", **alvos), \
                mock.patch.object(A17.a12, "CACHE_DIR", cache), \
                mock.patch.object(A17.a12, "carregar_formulario", return_value={"selects": {}}), \
                mock.patch.object(A17.a12, "municipios_do_formulario", return_value=(self.MUNIS, {"ZZ": "99"})), \
                mock.patch.object(A17.a12, "indice_uf", return_value="1"), \
                mock.patch.object(A17, "conferir_formulario_forma", return_value=None), \
                mock.patch.object(A17, "cursos_especificos", return_value=self.CURSOS), \
                mock.patch.object(A17, "opcoes_dos_conjuntos", return_value=self.OPCOES), \
                mock.patch.object(A17, "entradas_locais", return_value={}), \
                mock.patch.object(A17, "log", side_effect=lambda m: mensagens.append(str(m))):
            (cache / f"{A17.a12.FORMULARIO_ID}.json").write_text(json.dumps(
                {"data_hora_utc": "sintetico", "sha256_resposta": "0" * 64, "bytes_resposta": 0}))
            for q in A17.planejar_consultas({}, [self.COMP]) + A17.planejar_diagnostico({}, [self.COMP]):
                if q["id"] == omitir:
                    continue
                raw = self._resposta(q)
                if alterar and q["id"] == alterar[0]:
                    for velho, novo in alterar[1]:
                        self.assertIn(velho, raw)
                        raw = raw.replace(velho, novo)
                A17.a12._gravar_cache(q["id"], raw, {"id": q["id"], "status": "ok",
                                                     "corpo_post": A17.a12.corpo_post(q["campos"]),
                                                     "sha256_resposta": hashlib.sha256(raw).hexdigest()})
            codigo = A17.consolidar([self.COMP])
        return codigo, saida, mensagens

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_plano_de_consultas(self) -> None:
        with mock.patch.object(A17, "cursos_especificos", return_value=self.CURSOS), \
                mock.patch.object(A17, "opcoes_dos_conjuntos", return_value=self.OPCOES), \
                mock.patch.object(A17.a12, "indice_uf", return_value="1"), \
                mock.patch.multiple(A17, MES_CONFERENCIA_UF=self.COMP, UFS_CONFERENCIA={"ZZ": "Zeta"}):
            plano = A17.planejar_consultas({}, [self.COMP, "202202"])
        tipos = pd.Series([q["tipo"] for q in plano]).value_counts().to_dict()
        # 2 conjuntos × 2 meses + 1 por CBO por mês + 2 conjuntos × 1 UF no mês de conferência
        self.assertEqual(tipos, {"municipio": 4, "cbo": 2, "conferencia_uf": 2})
        q = next(x for x in plano if x["id"] == f"municipio_forma_c91_{self.COMP}")
        self.assertIn(("Coluna", "Forma_organização"), q["campos"])
        self.assertIn(("zeradas", "exibirlz"), q["campos"])
        self.assertEqual([v for k, v in q["campos"] if k == "SProfissional_-_CBO"], ["1", "2"])
        with self.assertRaises(RuntimeError):
            with mock.patch.object(A17, "cursos_especificos", return_value=self.CURSOS), \
                    mock.patch.object(A17, "opcoes_dos_conjuntos", return_value=self.OPCOES):
                A17.planejar_consultas({}, ["202609"])

    def test_controle_positivo(self) -> None:
        codigo, saida, _ = self._rodar()
        self.assertEqual(codigo, 0)
        p = pd.read_parquet(saida / A17.PAINEL_FILE.name)
        self.assertEqual(list(p.columns), A17.COLUNAS_PAINEL)
        self.assertEqual(set(p["natureza_dos_dados"]), {"EMPIRICO"})
        self.assertEqual(sorted(p["cod_curso"].unique()), [91, 92, 93])
        i = p.set_index(["cod_curso", "co_ibge", "forma"])["qtd_aprovada"]
        self.assertEqual(i[(91, "990002", "020901")], 2)
        self.assertEqual(i[(92, "990001", "020901")], 5)
        self.assertEqual(i[(92, "990002", "020901")], 0)
        # cursos com o mesmo conjunto de CBO têm as mesmas linhas
        c92 = p[p["cod_curso"] == 92].drop(columns="cod_curso").reset_index(drop=True)
        c93 = p[p["cod_curso"] == 93].drop(columns="cod_curso").reset_index(drop=True)
        pd.testing.assert_frame_equal(c92, c93)
        man = json.loads((saida / A17.MANIFESTO_FILE.name).read_text(encoding="utf-8"))
        self.assertTrue(all(v["status"] in ("APROVADO", "RELATO", "NAO_APLICAVEL") for v in man["validacoes"].values()))
        self.assertEqual(man["validacoes"]["V2_conjunto_contido_le_conjunto_maior"]["pares"], [["c92_c93", "c91"]])
        # V8: o procedimento cuja forma não está na tabela some com Coluna = Forma e fica registrado
        v8 = man["validacoes"]["V8_procedimentos_fora_da_coluna_forma"]
        self.assertEqual((v8["procedimentos_fora"], v8["qtd_total_fora"]), (["0399990001"], 3))
        proc = pd.read_csv(saida / A17.PROC_FILE.name, dtype={"co_procedimento": str})
        self.assertEqual(proc[["co_procedimento", "qtd_sem_coluna", "qtd_com_coluna_forma"]].values.tolist(),
                         [["0399990001", 3, 0]])
        self.assertTrue(any(q["tipo"] == "diag_procedimento_forma" for q in man["consultas"]["lista"]))

    def test_consulta_faltando_nao_grava(self) -> None:
        codigo, saida, _ = self._rodar(omitir=f"cbo_forma_uniao_{self.COMP}")
        self.assertEqual(codigo, 2)
        self.assertEqual(list(saida.iterdir()), [])

    def test_total_do_conjunto_diferente_da_soma_das_cbo_nao_grava(self) -> None:
        # c91: 990002/020901 passa de 2 para 3 com o Total junto (V1 coerente); só a V3 pode reprovar
        trocas = [(b'"990002 SINTETICO B";2;7;9', b'"990002 SINTETICO B";3;7;10'), (b'"Total";7;7;14', b'"Total";8;7;15')]
        codigo, saida, msgs = self._rodar(alterar=(f"municipio_forma_c91_{self.COMP}", trocas))
        self.assertEqual(codigo, 2)
        self.assertEqual(list(saida.iterdir()), [])
        texto = " ".join(msgs)
        self.assertIn("V3_nacional_por_forma_contra_consulta_por_cbo", texto)
        self.assertNotIn("V1_total_igual_soma_das_linhas", texto)

    def test_diagnostico_incoerente_com_a_consulta_por_cbo_nao_grava(self) -> None:
        # a consulta por procedimento com Coluna = Forma passa a ter 1 a mais em 020901 (Total junto): V8 reprova
        trocas = [(b'"0209010001 PROCEDIMENTO SINTETICO";7;-;7', b'"0209010001 PROCEDIMENTO SINTETICO";8;-;8'),
                  (b'"Total";7;7;14', b'"Total";8;7;15')]
        codigo, saida, msgs = self._rodar(alterar=(f"diag_procedimento_forma_{self.COMP}", trocas))
        self.assertEqual(codigo, 2)
        self.assertEqual(list(saida.iterdir()), [])
        self.assertIn("Coluna = Forma difere da consulta por CBO", " ".join(msgs))

    def test_conjunto_contido_maior_que_o_maior_nao_grava(self) -> None:
        # c92_c93 (CBO 225901) com mais produção que c91 (225901 + 225902) numa célula: V2 reprova
        trocas = [(b'"990001 SINTETICO A";5;-;5', b'"990001 SINTETICO A";5;9;14'), (b'"Total";5;7;12', b'"Total";5;16;21')]
        codigo, saida, msgs = self._rodar(alterar=(f"municipio_forma_c92_c93_{self.COMP}", trocas))
        self.assertEqual(codigo, 2)
        self.assertEqual(list(saida.iterdir()), [])
        self.assertIn("V2_conjunto_contido_le_conjunto_maior", " ".join(msgs))


@unittest.skipUnless(PAINEL.exists() and MANIFESTO.exists(), "saídas do a17 ausentes")
class TestSaidasVersionadas(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.man = json.loads(MANIFESTO.read_text(encoding="utf-8"))
        cls.formas = pd.read_csv(OUT / "sia_forma_curso_formas_por_consulta.csv",
                                 dtype={"competencia_processamento": str, "forma": str, "cursos": str})
        pf = pq.ParquetFile(PAINEL)
        cls.esquema = pf.schema_arrow
        totais, status_qtd, naturezas = [], set(), set()
        for i in range(pf.num_row_groups):
            t = pf.read_row_group(i)
            naturezas |= set(pc.unique(t.column("natureza_dos_dados").cast("string")).to_pylist())
            df = pd.DataFrame({c: t.column(c).cast("string").to_numpy(zero_copy_only=False)
                               for c in ("competencia_processamento", "forma", "status")})
            df["cod_curso"] = t.column("cod_curso").to_numpy()
            df["qtd"] = t.column("qtd_aprovada").to_pandas()
            for s, parte in df.groupby("status"):
                q = parte["qtd"]
                status_qtd.add((s, bool(q.isna().all()), bool(q.notna().all()),
                                bool((q.dropna() > 0).all()), bool((q.dropna() == 0).all())))
            totais.append(df.groupby(["competencia_processamento", "cod_curso", "forma"])["qtd"]
                          .agg(qtd_painel=lambda q: q.sum(min_count=1), linhas="size").reset_index())
        tot = pd.concat(totais, ignore_index=True)
        cls.totais = tot.groupby(["competencia_processamento", "cod_curso", "forma"], as_index=False).agg(
            qtd_painel=("qtd_painel", lambda q: q.sum(min_count=1)), linhas=("linhas", "sum"))
        cls.status_qtd = status_qtd
        cls.naturezas = naturezas

    def test_natureza_esquema_e_meses(self) -> None:
        self.assertEqual(self.naturezas, {"EMPIRICO"})
        self.assertEqual(self.esquema.names, A17.COLUNAS_PAINEL)
        self.assertEqual(str(self.esquema.field("qtd_aprovada").type), "int64")
        comps = sorted(self.totais["competencia_processamento"].unique())
        self.assertEqual(comps, A17.COMPETENCIAS)
        self.assertTrue(all(c < "202609" for c in comps))
        self.assertEqual(self.man["competencias_obtidas"], A17.COMPETENCIAS)

    def test_cursos_sao_os_especificos_do_g4(self) -> None:
        g4 = json.loads((ROOT / "output" / "rdd_bolsa" / "G4_resumo.json").read_text(encoding="utf-8"))
        self.assertEqual(sorted(self.totais["cod_curso"].unique().tolist()), sorted(g4["classes_dos_cursos"]["ESPECIFICO"]))

    def test_status_coerente_e_ausente_nunca_zero(self) -> None:
        for s, so_nulos, sem_nulos, positivos, zeros in self.status_qtd:
            self.assertIn(s, A17.a12.STATUS_VALIDOS)
            self.assertTrue(so_nulos if s == A17.STATUS_AUSENTE else sem_nulos, s)
            if s == A17.STATUS_VALOR:
                self.assertTrue(positivos)
            if s == A17.STATUS_ZERO:
                self.assertTrue(zeros)

    def test_painel_denso_e_soma_igual_total_tabnet(self) -> None:
        ign = pd.read_parquet(OUT / "sia_forma_curso_ignorados.parquet")
        self.assertEqual(set(ign["natureza_dos_dados"]), {"EMPIRICO"})
        gi = ign.groupby(["competencia_processamento", "conjunto_cbo", "forma"])["qtd_aprovada"].sum()
        n_mun = self.man["municipios_do_formulario"]
        pres = self.formas[self.formas["presente_na_resposta"]]
        conj_de = {int(k): s for s, i in self.man["cursos"]["conjuntos_de_cbo"].items() for k in i["cursos"]}
        t = self.totais.set_index(["competencia_processamento", "cod_curso", "forma"])
        n_pres = pres.groupby(["competencia_processamento", "conjunto_cbo"]).size()
        lin = self.totais.groupby(["competencia_processamento", "cod_curso"])["linhas"].sum()
        for (comp, k), n in lin.items():
            self.assertEqual(n, n_mun * n_pres[(comp, conj_de[int(k)])], (comp, k))
        for r in pres.itertuples(index=False):
            for k in r.cursos.split("|"):
                q = t.loc[(r.competencia_processamento, int(k), r.forma), "qtd_painel"]
                self.assertEqual(int(q) + int(gi.get((r.competencia_processamento, r.conjunto_cbo, r.forma), 0)),
                                 int(r.total_tabnet_municipio))

    def test_total_por_forma_igual_soma_das_cbo(self) -> None:
        f = self.formas
        pres = f[f["presente_na_resposta"]]
        self.assertTrue((pres["total_tabnet_municipio"] == pres["total_soma_cbo"]).all())
        self.assertTrue((f.loc[~f["presente_na_resposta"], "total_soma_cbo"] == 0).all())

    def test_validacoes_e_proveniencia(self) -> None:
        for k, v in self.man["validacoes"].items():
            self.assertIn(v["status"], ("APROVADO", "RELATO", "NAO_APLICAVEL"), k)
        conf = self.man["validacoes"]["V4_conferencia_uf_celula_a_celula"]["resultados"]
        self.assertEqual({(r["uf"], r["conjunto_cbo"]) for r in conf},
                         {(u, s) for u in A17.UFS_CONFERENCIA for s in self.man["cursos"]["conjuntos_de_cbo"]})
        lista = self.man["consultas"]["lista"]
        self.assertEqual(len(lista), self.man["consultas"]["n"])
        for q in lista:
            self.assertEqual(q["status"], "ok")
            self.assertTrue(q["url"].startswith("http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sia/cnv/qabr.def"))
            self.assertRegex(q["sha256_resposta"], r"^[0-9a-f]{64}$")
            self.assertTrue(q["corpo_post"] and q["data_hora_utc"])
            self.assertLess(q["competencia"], "202609")
            if q["tipo"] == "diag_procedimento_sem_coluna":
                self.assertIn("Coluna=--N%E3o-Ativa--", q["corpo_post"])
            else:
                self.assertIn("Coluna=Forma_organiza%E7%E3o", q["corpo_post"])
        tipos = pd.Series([q["tipo"] for q in lista]).value_counts().to_dict()
        n_conj = len(self.man["cursos"]["conjuntos_de_cbo"])
        self.assertEqual(tipos, {"municipio": 55 * n_conj, "cbo": 55, "conferencia_uf": 2 * n_conj,
                                 "diag_procedimento_sem_coluna": 55, "diag_procedimento_forma": 55})

    def test_diferencas_frente_ao_a12_explicadas_pela_v8(self) -> None:
        v5 = self.man["validacoes"]["V5_cruzamento_com_a12_por_subgrupo"]
        self.assertEqual(v5["n_diferencas_nao_explicadas_pela_V8"], 0)
        proc = pd.read_csv(OUT / "sia_forma_curso_procedimentos_fora_da_coluna_forma.csv",
                           dtype={"competencia_processamento": str, "co_procedimento": str, "forma_do_codigo": str,
                                  "subgrupo": str})
        self.assertEqual(set(proc["natureza_dos_dados"]), {"EMPIRICO"})
        v8 = self.man["validacoes"]["V8_procedimentos_fora_da_coluna_forma"]
        self.assertEqual(int((proc["qtd_sem_coluna"] - proc["qtd_com_coluna_forma"]).sum()), v8["qtd_total_fora"])
        self.assertEqual(sorted(proc["co_procedimento"].unique()), v8["procedimentos_fora"])

    def test_verificar_sem_rede(self) -> None:
        with mock.patch("urllib.request.urlopen", side_effect=AssertionError("rede proibida")):
            self.assertEqual(A17.verificar(), 0)

    def test_documento_de_auditoria(self) -> None:
        self.assertTrue(DOC.exists())
        texto = DOC.read_text(encoding="utf-8")
        self.assertIn("a17_adquirir_sia_forma_curso.py", texto)
        self.assertIn("EMPIRICO", texto)

        def bloco(nome: str) -> str:
            return texto.split(f"<!-- {nome} -->", 1)[1].split(f"<!-- /{nome} -->", 1)[0].strip()

        esperado = []
        for s, i in self.man["cursos"]["conjuntos_de_cbo"].items():
            cursos = i["cursos"]
            nome = f"curso {cursos[0]}" if len(cursos) == 1 else "cursos " + " e ".join(str(k) for k in cursos)
            esperado.append(f"- {s}: {nome} (CBO {', '.join(sorted(i['cbos']))})")
        self.assertEqual(bloco("a17_conjuntos"), "\n".join(esperado))
        v8 = self.man["validacoes"]["V8_procedimentos_fora_da_coluna_forma"]
        self.assertEqual(bloco("a17_procedimentos_fora"), ", ".join(v8["procedimentos_fora"]) or "Nenhum.")


if __name__ == "__main__":
    unittest.main()
