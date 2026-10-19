"""Testes do portão G5: painel CNES médico × mês com registro do conselho (a16).

Três partes:

1. `TestPlano` e `TestAgregacaoSintetica`: plano de competências (nenhuma >= 202609) e a agregação
   médico × mês sobre um mini-cadastro SINTÉTICO, inventado e montado só em memória (nunca gravado):
   hora vazia não vira zero, vínculo SUS e não SUS separados, zero só para quem não tem vínculo
   numa competência lida, pseudônimo pela ordem do SHA-256.
2. `TestSaidas`: invariantes das saídas EMPÍRICAS versionadas (painéis, chaves, cobertura,
   manifesto, G5_resumo): esquema, nenhum dado pessoal, natureza, coerência entre painéis,
   cobertura recalculada do painel, proveniência por competência e veredito recalculado pelos
   critérios do script. Os alvos vêm das saídas, nunca digitados.
3. `TestSemContrasteNemRede`: o script não lê IVS nem quebra nada por faixa, corte ou ciclo, e o
   modo `verificar` (o do run_all) não usa a rede nem grava.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "aquisicao" / "a16_cnes_profissional_mensal.py"
_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location("a16_cnes_profissional_teste", SCRIPT)
A16 = importlib.util.module_from_spec(_spec)
sys.modules["a16_cnes_profissional_teste"] = A16
_spec.loader.exec_module(A16)
sys.dont_write_bytecode = _bytecode

SAIDAS = (A16.PAINEL_VINCULO, A16.PAINEL_MEDICO, A16.CHAVES, A16.COBERTURA, A16.MANIFESTO, A16.G5_RESUMO)
TEM_SAIDAS = all(p.exists() for p in SAIDAS)


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


class TestPlano(unittest.TestCase):
    def test_competencias_mensais_sem_ciclo3(self) -> None:
        self.assertEqual(A16.COMPETENCIAS[0], "202406")
        self.assertEqual(A16.COMPETENCIAS[-1], "202608")
        self.assertEqual(len(A16.COMPETENCIAS), 27)
        self.assertEqual(len(set(A16.COMPETENCIAS)), 27)
        self.assertTrue(all(c < "202609" for c in A16.COMPETENCIAS))
        with self.assertRaises(RuntimeError):
            A16.checar_limite("202609")

    def test_competencias_da_x1_contidas(self) -> None:
        self.assertTrue(set(A16.competencias_x1()) <= set(A16.COMPETENCIAS))

    def test_cache_privado_ignorado_pelo_git(self) -> None:
        texto = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("output/aquisicao/cnes_profissional/cache_privado/", texto)
        self.assertTrue(A16.ZIP_DIR.is_relative_to(A16.PRIV))
        # nada é gravado em data/
        self.assertFalse(A16.PRIV.is_relative_to(ROOT / "data"))
        self.assertNotIn("data/raw/cnes", SCRIPT.read_text(encoding="utf-8"))


def _vinc_sintetico() -> pd.DataFrame:
    """Mini-cadastro SINTÉTICO (inventado): dois profissionais, duas competências."""
    linhas = [
        # id, comp, cnes, mun, cbo, tp, amb, hosp, outros
        ("g5p_00001", "202406", "0000001", "000001", "225125", "S", 20, 0, 0),
        ("g5p_00001", "202406", "0000002", "000002", "225125", "N", 10, 0, 4),
        ("g5p_00001", "202407", "0000001", "000001", "225125", "S", 20, None, 0),  # hospitalar vazio
        ("g5p_00002", "202406", "0000003", "000001", "225250", "S", 0, 24, 0),
    ]
    df = pd.DataFrame(linhas, columns=["id_prof", "competencia", "co_cnes", "co_municipio", "co_cbo",
                                       "tp_sus_nao_sus", "qt_ch_ambulatorial", "qt_ch_hosp_sus", "qt_ch_outros"])
    for c in A16.HORAS:
        df[c] = df[c].astype("Int32")
    for c in ("id_prof", "competencia", "co_cnes", "co_municipio", "co_cbo", "tp_sus_nao_sus"):
        df[c] = df[c].astype("string")
    return df


class TestAgregacaoSintetica(unittest.TestCase):
    """Dados SINTÉTICOS, só em memória."""

    def setUp(self) -> None:
        self.p = A16.agregar_medico_mes(_vinc_sintetico(), ["g5p_00001", "g5p_00002"], ["202406", "202407"])
        self.p = self.p.set_index(["id_prof", "competencia"])

    def test_balanceado_e_zero_so_sem_vinculo(self) -> None:
        self.assertEqual(len(self.p), 4)
        sem = self.p.loc[("g5p_00002", "202407")]
        self.assertEqual(sem["tem_vinculo_medico"], 0)
        self.assertEqual(sem["n_vinculos"], 0)
        self.assertEqual(sem["horas_totais"], 0)

    def test_sus_e_nao_sus_separados(self) -> None:
        r = self.p.loc[("g5p_00001", "202406")]
        self.assertEqual((r["n_vinculos"], r["n_vinculos_sus"], r["n_vinculos_nao_sus"]), (2, 1, 1))
        self.assertEqual(r["horas_amb_vinc_sus"], 20)
        self.assertEqual(r["horas_amb_vinc_nao_sus"], 10)
        self.assertEqual(r["horas_outros_vinc_nao_sus"], 4)
        self.assertEqual(r["horas_totais"], 34)
        self.assertEqual((r["n_estabelecimentos"], r["n_municipios"], r["n_cbo"]), (2, 2, 1))

    def test_hora_vazia_nao_vira_zero(self) -> None:
        r = self.p.loc[("g5p_00001", "202407")]
        self.assertTrue(pd.isna(r["horas_hosp_vinc_sus"]))
        self.assertTrue(pd.isna(r["horas_totais"]))
        self.assertEqual(r["horas_amb_vinc_sus"], 20)
        self.assertEqual(r["n_vinculos_horas_ausentes"], 1)
        # o vazio de um vínculo SUS não anula a soma não SUS
        self.assertEqual(r["horas_hosp_vinc_nao_sus"], 0)

    def test_pseudonimo_ordem_do_sha256(self) -> None:
        ch = pd.DataFrame({"co_profissional_sus": ["B", "A", "B"]}, dtype="string")  # sintético
        ids = A16.atribuir_ids(ch)
        ordem = sorted({"A", "B"}, key=lambda s: hashlib.sha256(s.encode()).hexdigest())
        self.assertEqual(ids, {ordem[0]: "g5p_00001", ordem[1]: "g5p_00002"})


@unittest.skipUnless(TEM_SAIDAS, "saídas do a16 ausentes")
class TestSaidas(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.v = pd.read_parquet(A16.PAINEL_VINCULO)
        cls.m = pd.read_parquet(A16.PAINEL_MEDICO)
        cls.ch = pd.read_parquet(A16.CHAVES)
        cls.cob = pd.read_csv(A16.COBERTURA, dtype={"competencia": str, "regra_ligacao": str},
                              keep_default_na=False, na_values=[""])
        cls.man = json.loads(A16.MANIFESTO.read_text(encoding="utf-8"))
        cls.g5 = json.loads(A16.G5_RESUMO.read_text(encoding="utf-8"))

    def test_esquemas(self) -> None:
        self.assertEqual(list(self.v.columns), A16.COLS_VINCULO)
        self.assertEqual(list(self.m.columns), A16.COLS_MEDICO)
        self.assertEqual(list(self.ch.columns), A16.COLS_CHAVES)

    def test_nenhum_dado_pessoal(self) -> None:
        for df in (self.v, self.m, self.ch, self.cob):
            for c in df.columns:
                self.assertNotIn(c.lower(), A16.COLUNAS_PROIBIDAS, c)
        for df in (self.v, self.m, self.ch):
            self.assertTrue(df["id_prof"].str.fullmatch(r"g5p_\d{5}").all())
        # nenhum valor de id_externo parece CRM ou código de profissional: só pseudônimos da X1
        x1 = self.ch[self.ch["origem"] == "X1"]
        self.assertTrue(x1["id_externo"].str.fullmatch(r"x1m_\d{5}").all())

    def test_natureza_empirica(self) -> None:
        for df in (self.v, self.m, self.ch, self.cob):
            self.assertEqual(set(df["natureza_dos_dados"]), {"EMPIRICO"})
        self.assertEqual(self.man["natureza_dos_dados"], "EMPIRICO")
        self.assertEqual(self.g5["natureza_dos_dados"], "EMPIRICO")

    def test_competencias(self) -> None:
        obtidas = self.man["competencias_obtidas"]
        self.assertTrue(all(c < "202609" for c in obtidas))
        self.assertEqual(sorted(set(self.m["competencia"])), sorted(obtidas))
        self.assertTrue(set(self.v["competencia"]) <= set(obtidas))
        self.assertEqual(sorted(obtidas + list(self.man["competencias_nao_obtidas"])), A16.COMPETENCIAS)
        for c, r in self.man["competencias_nao_obtidas"].items():
            self.assertTrue(r.get("status"), c)  # ausente tem motivo

    def test_painel_medico_balanceado_e_coerente_com_vinculos(self) -> None:
        ids = set(self.ch["id_prof"])
        self.assertEqual(set(self.m["id_prof"]), ids)
        self.assertEqual(len(self.m), len(ids) * len(self.man["competencias_obtidas"]))
        self.assertFalse(self.m.duplicated(["id_prof", "competencia"]).any())
        n = self.v.groupby(["id_prof", "competencia"]).size()
        mm = self.m.set_index(["id_prof", "competencia"])
        self.assertTrue((mm.loc[n.index, "n_vinculos"].to_numpy() == n.to_numpy()).all())
        self.assertEqual(int(mm["n_vinculos"].sum()), len(self.v))
        self.assertTrue(((mm["tem_vinculo_medico"] == 1) == (mm["n_vinculos"] > 0)).all())
        sem = mm[mm["tem_vinculo_medico"] == 0]
        horas = [c for c in A16.COLS_MEDICO if c.startswith("horas_")]
        self.assertTrue((sem[horas].fillna(-1) == 0).all().all())

    def test_horas_recalculadas_do_painel_de_vinculos(self) -> None:
        rec = A16.agregar_medico_mes(self.v, sorted(set(self.ch["id_prof"])), self.man["competencias_obtidas"])
        a = rec.set_index(["id_prof", "competencia"]).sort_index()
        b = self.m.set_index(["id_prof", "competencia"]).sort_index()
        for c in A16.COLS_MEDICO[2:-1]:
            x, y = a[c].astype("Float64"), b[c].astype("Float64")
            self.assertTrue(((x == y) | (x.isna() & y.isna())).fillna(False).all(), c)

    def test_cbo_medica(self) -> None:
        self.assertTrue(self.v["co_cbo"].str.startswith(("2251", "2252", "2253", "2231")).all())

    def test_cobertura_recalculada(self) -> None:
        pres = self.m[self.m["tem_vinculo_medico"] == 1]
        for (origem, regra), g in self.ch.groupby(["origem", "regra_ligacao"], dropna=False):
            ids = set(g["id_prof"])
            regra = regra if pd.notna(regra) else ""
            cg = self.cob[(self.cob["origem"] == origem) & (self.cob["regra_ligacao"].fillna("") == regra)]
            for r in cg.itertuples(index=False):
                n = int(pres[(pres["competencia"] == r.competencia) & pres["id_prof"].isin(ids)].shape[0])
                self.assertEqual(r.profissionais_com_vinculo_medico, n)
                self.assertEqual(r.profissionais, len(ids))
                self.assertEqual(r.registros_ligados, len(g))

    def test_cobertura_sem_quebra_proibida(self) -> None:
        proibidas = {"ivs", "faixa", "corte", "ciclo", "tratado", "lado", "mes_inicio", "evento", "pre", "pos"}
        for df in (self.v, self.m, self.ch, self.cob):
            self.assertFalse(proibidas & {c.lower() for c in df.columns}, list(df.columns))

    def test_proveniencia_por_competencia(self) -> None:
        for c in self.man["competencias_obtidas"]:
            r = self.man["por_competencia"][c]
            self.assertTrue(r["url"].endswith(f"BASE_DE_DADOS_CNES_{c}.ZIP"))
            self.assertRegex(r["sha256_zip"], r"^[0-9a-f]{64}$")
            self.assertGreater(r["bytes_zip"], 100 * 1024**2)
            self.assertTrue(r["data_download"])
            self.assertEqual(r["status"], "extraido_zip_apagado")
            self.assertIn("validacao_contra_a09", r)
            if r["validacao_contra_a09"]["sha256_igual_ao_a09"]:
                self.assertTrue(r["validacao_contra_a09"]["linhas_iguais_ao_a09"], c)

    def test_saidas_conferem_com_manifesto(self) -> None:
        for nome, p in (("painel_vinculo_mes", A16.PAINEL_VINCULO), ("painel_medico_mes", A16.PAINEL_MEDICO),
                        ("chaves_origem", A16.CHAVES), ("cobertura", A16.COBERTURA)):
            self.assertEqual(sha256(p), self.man["saidas"][nome]["sha256"], nome)
        for r, reg in self.man["entradas_locais"].items():
            self.assertEqual(sha256(ROOT / r), reg["sha256"], r)

    def test_veredito_recalculado(self) -> None:
        obtidas = self.man["competencias_obtidas"]
        regs = self.man["por_competencia"]
        e = self.cob[(self.cob["origem"] == "X1") & (self.cob["regra_ligacao"] == "d1_pos_hoc")]
        ver = A16.veredito(regs, obtidas, self.man["reproducao_x1"], e if len(e) else None)
        self.assertEqual(ver["veredito"], self.g5["veredito"])
        self.assertEqual(ver["veredito"], self.man["veredito"]["veredito"])
        self.assertIn(self.g5["veredito"], {"VIAVEL", "VIAVEL_PARCIAL", "INVIAVEL"})

    def test_reproducao_x1_coerente_com_chaves(self) -> None:
        rep = self.man["reproducao_x1"]
        if rep is None:
            self.skipTest("ligação da X1 não refeita")
        ref = pd.read_parquet(A16.X1_MEDICOS, columns=["id_medico", "regra_ligacao", "ligado"])
        for regra, r in rep["por_regra"].items():
            self.assertEqual(r["registros_x1"], int((ref["regra_ligacao"] == regra).sum()))
            n = int(((self.ch["origem"] == "X1") & (self.ch["regra_ligacao"] == regra)).sum())
            self.assertEqual(n, r["ligados_a16"])
            if rep["reproduz_100pct"]:
                self.assertEqual(n, int(ref.loc[ref["regra_ligacao"] == regra, "ligado"].sum()))


DOC = ROOT / "docs" / "auditorias" / "aquisicao" / "A16_cnes_profissional.md"


@unittest.skipUnless(TEM_SAIDAS and DOC.exists(), "saídas ou doc A16 ausentes")
class TestDocA16(unittest.TestCase):
    """As afirmações qualitativas do doc A16 (seções 0 e 6) conferidas contra as saídas."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = DOC.read_text(encoding="utf-8")
        cls.man = json.loads(A16.MANIFESTO.read_text(encoding="utf-8"))
        cls.g5 = json.loads(A16.G5_RESUMO.read_text(encoding="utf-8"))
        cls.cob = pd.read_csv(A16.COBERTURA, dtype={"competencia": str})

    def test_veredito_do_doc(self) -> None:
        self.assertIn(f"**Veredito do portão: `{self.g5['veredito']}`**", self.doc)
        for k, v in self.g5["status_por_criterio"].items():
            if k.startswith("C") and isinstance(v, str) and k.count("_") >= 1 and v in ("ok", "parcial", "falha"):
                self.assertIn(f"{k.split('_')[0]}, ", self.doc)
                self.assertRegex(self.doc, rf"\*\*{k.split('_')[0]}, [^*]*: {v}\.\*\*")

    def test_afirmacoes_da_secao_6(self) -> None:
        regs = self.man["por_competencia"]
        # "Em todas, o ZIP é o mesmo do a09 e a contagem de vínculos médicos é idêntica."
        self.assertTrue(all(regs[c]["validacao_contra_a09"]["sha256_igual_ao_a09"]
                            and regs[c]["validacao_contra_a09"]["linhas_iguais_ao_a09"]
                            for c in self.man["competencias_obtidas"]))
        # "Todas as 27 competências mensais foram obtidas."
        self.assertEqual(self.man["competencias_obtidas"], A16.COMPETENCIAS)
        # teste de viabilidade: 202406 e 202608 sem tempo de download
        for c in ("202406", "202608"):
            self.assertIsNone(regs[c]["segundos_download"])
        # "nenhum deles [vínculos com hora vazia] é de médico do painel"
        self.assertEqual(int(pd.read_parquet(A16.PAINEL_MEDICO)["n_vinculos_horas_ausentes"].sum()), 0)
        # C4: reprodução idêntica
        self.assertTrue(self.man["reproducao_x1"]["reproduz_100pct"])
        x1 = self.cob[self.cob["origem"] == "X1"]
        # "O registro CRM+UF da lista nunca aparece em outro código de profissional."
        self.assertEqual(int(x1["registros_crm_uf_em_outro_codigo"].sum()), 0)
        # "Nenhum deles está sem registro."
        self.assertEqual(int(x1["com_vinculo_sem_registro_crm"].sum()), 0)
        # "a fração com o CRM da lista só alcança o limiar de 0,95 no segundo semestre de 2025"
        d1 = x1[x1["regra_ligacao"] == "d1_pos_hoc"].set_index("competencia")
        ok = d1.index[d1["fracao_com_crm_da_lista_entre_presentes"] >= A16.LIMIARES["registro_igual_min"]]
        self.assertTrue(min(ok) >= "202507" and min(ok) <= "202512", min(ok))
        # "a fração [com vínculo médico] sobe ao longo do período"
        self.assertLess(d1["fracao_com_vinculo_medico"].iloc[0], d1["fracao_com_vinculo_medico"].iloc[-1])


class TestSemContrasteNemRede(unittest.TestCase):
    def test_script_nao_le_ivs_nem_quebra_por_corte(self) -> None:
        texto = SCRIPT.read_text(encoding="utf-8")
        for proibido in ("a08_ivs", "IVS_OFICIAL", "faixa_atracao", "CORTES_MIL", "rd_local_linear", "mes_inicio",
                         "dt_inicio"):
            self.assertNotIn(proibido, texto, proibido)

    def test_padrao_e_verificar(self) -> None:
        with mock.patch.object(sys, "argv", ["a16", "--help"]), self.assertRaises(SystemExit), \
                mock.patch("sys.stdout"):
            A16.main()
        self.assertIn('default="verificar"', SCRIPT.read_text(encoding="utf-8"))

    @unittest.skipUnless(TEM_SAIDAS, "saídas do a16 ausentes")
    def test_verificar_sem_rede_e_sem_gravar(self) -> None:
        antes = {p: p.stat().st_mtime_ns for p in SAIDAS}

        def sem_rede(*_a, **_k):
            raise AssertionError("a16 em --etapa verificar tentou acessar a rede ou gravar")

        with mock.patch("urllib.request.urlopen", sem_rede), \
                mock.patch.object(A16, "etapa_baixar", sem_rede), \
                mock.patch.object(A16, "etapa_consolidar", sem_rede), \
                mock.patch.object(sys, "argv", ["a16", "--etapa", "verificar"]):
            self.assertEqual(A16.main(), 0)
        self.assertEqual({p: p.stat().st_mtime_ns for p in SAIDAS}, antes)


if __name__ == "__main__":
    unittest.main()
