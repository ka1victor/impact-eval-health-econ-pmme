"""Testes do adendo 48c (script 41): capitais e UF no corte 0,300, robustez pós-resultado da H1.

- Esquema de `HC_estimativas.csv` (72 linhas, blocos do adendo), `natureza_dos_dados = EMPIRICO` e estatuto
  `ADENDO_48C_POS_RESULTADO` em toda linha, no resumo e na referência do IBGE.
- Running variable só o IVS 2010 oficial (a08); o arquivo local de IVS da auditoria 16 não é lido; nenhuma competência
  do CNES >= 202609 (o 48c não usa CNES).
- Referência de capitais e regiões: SHA-256 igual ao manifesto; manifesto com fonte, data, cobertura e hashes; região de
  cada UF igual à da REGIC 2018 do IBGE arquivada em `data/raw/` (conferência sem rede).
- Portão contra o 48b: HI-1 e HI-2 sem ajuste iguais às primárias de `HI_estimativas.csv` (<= 1e-8).
- IC, p, BKY (só C-2 a C-4) e a leitura pré-registrada recalculados das linhas gravadas.
- Doc 57o idêntico ao gerado de `output/`; nenhum número com decimais fora dos blocos `<!-- HC:... -->` além dos
  parâmetros do adendo; linguagem de robustez pós-resultado.
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
OUT = ROOT / "output" / "rdd_bolsa"
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "41_h1_capitais_uf.py"
DOC = ROOT / "docs" / "06_execucao" / "57o_h1_capitais_uf.md"
ADENDO = ROOT / "docs" / "06_execucao" / "48c_adendo_capitais_e_UF.md"
REGIC = ROOT / "data" / "raw" / "aquisicao" / "territorio" / "REGIC2018_Municipios_Hierarquia_e_regiao.xlsx"
IVS_ERRADO = "ivs_ipea_2010_municipios"


def _mod(nome: str, caminho: Path):
    if nome in sys.modules:
        return sys.modules[nome]
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    return mod


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


HC = _mod("hc41_teste", SCRIPT)
EST, RES = HC.ler_saidas()
COLUNAS = ["natureza_dos_dados", "estatuto", "id_linha", "bloco", "medida", "papel", "unidade_analise", "amostra",
           "corte", "ajuste", "rotulo_ajuste", "especificacao", "efeitos_fixos", "controle", "estimador", "h", "status",
           "tau", "ep", "ic95_inf", "ic95_sup", "p_valor", "ic_contem_zero", "n_abaixo", "n_acima", "n_obs",
           "n_clusters", "capitais_abaixo", "capitais_acima", "ufs_na_janela", "coef_capital", "entra_bky", "q_bky",
           "unidade", "covariaveis_descartadas", "nota"]


def _um(**f) -> pd.Series:
    m = np.ones(len(EST), dtype=bool)
    for k, v in f.items():
        m &= (EST[k].astype(str) == str(v)).to_numpy()
    assert m.sum() == 1, f
    return EST[m].iloc[0]


class TestEsquemaENatureza(unittest.TestCase):
    def test_colunas_e_linhas(self):
        self.assertEqual(list(EST.columns), COLUNAS)
        self.assertEqual(len(EST), 72)
        self.assertFalse(EST["id_linha"].duplicated().any())
        self.assertEqual(set(EST["status"]), {"EXECUTADO"})
        self.assertTrue(np.isfinite(EST[["tau", "ep", "ic95_inf", "ic95_sup", "p_valor"]].to_numpy(float)).all())

    def test_blocos_do_adendo(self):
        # C-1: 3 variáveis x 2 unidades x 2 amostras x 2 cortes; base e C-2 a C-4: HI-1/HI-2 x 2 cortes;
        # C-5: A3, A3 com o tipo de 13/02, N1 S-a e taxa S-e x 4 ajustes x 2 cortes.
        self.assertEqual(EST["bloco"].value_counts().to_dict(),
                         {"C-5": 32, "C-1": 24, "base": 4, "C-2": 4, "C-3": 4, "C-4": 4})
        self.assertEqual(set(EST["corte"]), {"0.300", "0.400"})
        self.assertTrue((EST["h"].astype(float) == 0.05).all())
        h1 = EST[EST["bloco"].isin(["base", "C-2", "C-3", "C-4"])]
        self.assertEqual(set(h1["medida"]), {"HI-1", "HI-2"})
        self.assertEqual(set(h1["amostra"]), {"H1"})
        self.assertEqual(set(EST.loc[EST["bloco"] == "C-5", "medida"]), {"A3", "A3-pre", "N1", "taxa"})
        self.assertEqual(set(EST.loc[EST["bloco"] == "C-1", "medida"]), {"capital", "nordeste", "norte"})

    def test_natureza_e_estatuto(self):
        self.assertEqual(set(EST["natureza_dos_dados"]), {"EMPIRICO"})
        self.assertEqual(set(EST["estatuto"]), {"ADENDO_48C_POS_RESULTADO"})
        self.assertEqual(RES["natureza_dos_dados"], "EMPIRICO")
        self.assertEqual(RES["estatuto"], "ADENDO_48C_POS_RESULTADO")
        ref = pd.read_csv(HC.REF_CSV, dtype=str)
        self.assertEqual(set(ref["natureza_dos_dados"]), {"EMPIRICO"})
        man = json.loads(HC.REF_MANIFESTO.read_text(encoding="utf-8"))
        self.assertEqual(man["natureza_dos_dados"], "EMPIRICO")

    def test_sem_identificador_pessoal(self):
        cols = {c.lower() for c in EST.columns}
        self.assertFalse({"cpf", "nome", "id_candidato", "co_profissional_sus", "crm", "cns"} & cols)

    def test_figuras_com_como_ler(self):
        figs = RES["saidas"]["figuras"]
        self.assertEqual(len(figs), 4)
        for f in figs:
            p = ROOT / f["arquivo"]
            self.assertTrue(p.exists(), f["arquivo"])
            self.assertEqual(sha(p), f["sha256"], f["arquivo"])
            self.assertTrue(f["como_ler"])
        self.assertEqual(sha(OUT / "HC_estimativas.csv"), RES["saidas"]["HC_estimativas.csv"]["sha256"])


class TestIntegridade(unittest.TestCase):
    def setUp(self):
        self.src = SCRIPT.read_text(encoding="utf-8")

    def test_ivs_oficial(self):
        self.assertNotIn(IVS_ERRADO, self.src)
        self.assertEqual(HC.IVS_OFICIAL.name, "a08_ivs_2010_oficial_municipio.csv")
        # A base vem da auditoria 36, cujo leitor de IVS usa o a08.
        self.assertEqual(Path(HC.A36.IVS_OFICIAL).name, "a08_ivs_2010_oficial_municipio.csv")
        caminhos = [x["caminho"] for x in RES["entradas"]]
        self.assertIn("output/aquisicao/a08_ivs_2010_oficial_municipio.csv", caminhos)
        self.assertFalse(any(IVS_ERRADO in c for c in caminhos))
        # No a36_reconstruir_H1 o caminho do arquivo errado só aparece na conferência de texto, nunca numa leitura.
        a36 = (ROOT / "scripts" / "auditoria_H1" / "a36_reconstruir_H1.py").read_text(encoding="utf-8")
        self.assertNotRegex(a36, r"read_(csv|excel|parquet)\(\s*IVS_ERRADO")

    def test_sem_cnes_202609_ou_depois(self):
        # O 48c não usa CNES: nenhuma entrada é painel CNES e nenhum texto cita competência >= 202609.
        competencia = re.compile(r"\b(2026(09|1[0-2])|20(2[7-9]|[3-9]\d)(0[1-9]|1[0-2]))\b")
        for x in RES["entradas"]:
            self.assertNotRegex(x["caminho"].lower(), r"cnes_(nacional|profissional)|painel_cnes")
            self.assertIsNone(competencia.search(x["caminho"]), x["caminho"])
        self.assertIsNone(competencia.search(self.src))
        self.assertIsNone(competencia.search(json.dumps(RES["parametros"])))

    def test_entradas_com_hash_em_dia(self):
        for x in RES["entradas"]:
            p = ROOT / x["caminho"]
            self.assertTrue(p.exists(), x["caminho"])
            self.assertEqual(sha(p), x["sha256"], x["caminho"])
            for campo in ("papel", "fonte", "data_referencia", "cobertura", "unidade", "chaves", "filtros"):
                self.assertIn(campo, x)

    def test_nao_escreve_em_data(self):
        self.assertNotRegex(self.src, r"ROOT\s*/\s*\"data\"")
        for f in RES["saidas"]["figuras"]:
            self.assertTrue(f["arquivo"].startswith("output/"))

    def test_adendo_congelado(self):
        self.assertEqual(RES["adendo"]["sha256"], sha(ADENDO))
        texto = ADENDO.read_text(encoding="utf-8")
        self.assertIn("ADENDO_48C_POS_RESULTADO", texto)
        self.assertIn("robustez pós-resultado", texto)


class TestReferenciaIBGE(unittest.TestCase):
    def setUp(self):
        self.ref = pd.read_csv(HC.REF_CSV, dtype=str)
        self.man = json.loads(HC.REF_MANIFESTO.read_text(encoding="utf-8"))

    def test_hash_e_manifesto(self):
        self.assertEqual(sha(HC.REF_CSV), self.man["saida"]["sha256"])
        self.assertEqual(RES["referencia_ibge"]["sha256"], self.man["saida"]["sha256"])
        for chave in ("capitais", "regioes"):
            f = self.man["fontes"][chave]
            for campo in ("fonte", "data_referencia", "cobertura", "unidade", "chaves"):
                self.assertTrue(f.get(campo), f"{chave}.{campo}")
        self.assertTrue(self.man["fontes"]["capitais"]["url"].startswith("https://geoftp.ibge.gov.br/"))
        self.assertRegex(self.man["fontes"]["capitais"]["sha256_zip"], r"^[0-9a-f]{64}$")
        self.assertRegex(self.man["data_acesso_utc"], r"^\d{4}-\d{2}-\d{2}T")

    def test_27_capitais_uma_por_uf(self):
        self.assertEqual(len(self.ref), 27)
        self.assertEqual(self.ref["cd_uf"].nunique(), 27)
        self.assertEqual(self.ref["capital_co_ibge_6d"].nunique(), 27)
        self.assertTrue((self.ref["capital_co_ibge_6d"].str[:2] == self.ref["cd_uf"]).all())
        self.assertTrue((self.ref["capital_co_ibge_7d"].str[:6] == self.ref["capital_co_ibge_6d"]).all())
        self.assertEqual(int((self.ref["categoria_ibge"] == "Capital Federal").sum()), 1)

    def test_regiao_igual_a_regic_2018_arquivada(self):
        regic = pd.read_excel(REGIC, sheet_name=0, dtype={"coduf": str})
        por_uf = regic.groupby("coduf")["Grande Região"].agg(lambda s: sorted(set(s)))
        self.assertTrue(all(len(v) == 1 for v in por_uf))
        for r in self.ref.itertuples():
            self.assertEqual(por_uf[r.cd_uf][0], r.nome_regiao, r.sigla_uf)


class TestPortaoContraHI(unittest.TestCase):
    def test_base_igual_ao_48b(self):
        hi = pd.read_csv(OUT / "HI_estimativas.csv", dtype={"corte": str, "ciclo": str})
        g = hi[(hi["ciclo"] == "1+2+3") & (hi["variante"] == "principal") & (hi["versao_quadro_c2"] == "13fev")
               & (hi["linha"].isin(["HI-1", "HI-2"])) & (hi["linha"] == hi["outcome"])
               & (pd.to_numeric(hi["h"]) == 0.05)]
        self.assertEqual(len(g), 4)
        for r in g.itertuples():
            meu = _um(bloco="base", medida=r.linha, corte=r.corte)
            self.assertLessEqual(abs(float(meu["tau"]) - r.tau), 1e-8, (r.linha, r.corte))
            self.assertLessEqual(abs(float(meu["ep"]) - r.ep), 1e-8, (r.linha, r.corte))
            self.assertEqual(int(meu["n_abaixo"]), int(r.n_abaixo))
            self.assertEqual(int(meu["n_acima"]), int(r.n_acima))
        conf = RES["conferencias"]["HI"]
        self.assertEqual(conf["status"], "CONFERIDO")
        self.assertEqual(conf["sha256"], sha(OUT / "HI_estimativas.csv"))

    def test_conferencias_a36_e_pipeline(self):
        c = RES["conferencias"]
        self.assertGreaterEqual(len(c["auditoria_36"]), 20)
        self.assertEqual(len(c["pipeline"]), 6)
        for x in c["auditoria_36"] + c["pipeline"]:
            self.assertLessEqual(max(x["dif_tau"], x["dif_ep"]), 1e-8)


class TestInferenciaELeitura(unittest.TestCase):
    def test_ic_e_p(self):
        z = 1.959963984540054
        for r in EST.itertuples():
            self.assertAlmostEqual(r.ic95_inf, r.tau - z * r.ep, places=10)
            self.assertAlmostEqual(r.ic95_sup, r.tau + z * r.ep, places=10)
            self.assertAlmostEqual(r.p_valor, math.erfc(abs(r.tau / r.ep) / math.sqrt(2)), places=10)
            self.assertEqual(str(r.ic_contem_zero) == "True", bool(r.ic95_inf <= 0 <= r.ic95_sup))

    def test_bky_so_c2_a_c4(self):
        bky = EST["entra_bky"].astype(str) == "True"
        self.assertEqual(set(EST.loc[bky, "bloco"]), {"C-2", "C-3", "C-4"})
        self.assertEqual(int(bky.sum()), 12)
        self.assertTrue(EST.loc[~bky, "q_bky"].isna().all())
        q = HC.L.qvalores_bky(EST.loc[bky, "p_valor"].to_numpy(float))
        np.testing.assert_allclose(EST.loc[bky, "q_bky"].to_numpy(float), q, atol=1e-12)

    def test_leitura_refeita(self):
        est = EST.copy()
        est["ic_contem_zero"] = est["ic_contem_zero"].astype(str) == "True"
        refeita = HC.leitura_preregistrada(est)
        for cs, l in RES["leitura"].items():
            for k in ("c1_salto_em_capital_ou_regiao", "c1_linhas_com_salto", "linhas_H1_com_queda_a_levar",
                      "c2_ajustes_levam_a_ic_com_zero", "leitura", "motivo", "texto"):
                self.assertEqual(refeita[cs][k], l[k], (cs, k))
            for m, v in l["por_medida"].items():
                self.assertAlmostEqual(refeita[cs]["por_medida"][m]["tau_sem_ajuste"], v["tau_sem_ajuste"], places=12)
                for k in ("ic_sem_ajuste_exclui_zero", "ic_contem_zero_por_ajuste", "levam_nos_tres"):
                    self.assertEqual(refeita[cs]["por_medida"][m][k], v[k], (cs, m, k))
        self.assertEqual(RES["leitura"]["0.300"]["leitura"], "ANDA_JUNTO_COM_CAPITAIS_OU_REGIAO")
        self.assertEqual(RES["leitura"]["0.400"]["leitura"], "RELATAR_COMO_ESTA")

    def test_sem_capitais_exclui_capitais(self):
        for r in EST[EST["ajuste"] == "sem_capitais"].itertuples():
            self.assertEqual((int(r.capitais_abaixo), int(r.capitais_acima)), (0, 0))


class TestDoc57o(unittest.TestCase):
    def setUp(self):
        self.doc = DOC.read_text(encoding="utf-8")

    def test_doc_igual_ao_gerado(self):
        self.assertEqual(self.doc, HC.gerar_doc(EST, RES))

    def test_numeros_so_nos_blocos(self):
        fora = re.sub(r"<!-- HC:(\w+):inicio -->.*?<!-- HC:\1:fim -->", "", self.doc, flags=re.S)
        decimais = set(re.findall(r"\d+,\d+", fora))
        self.assertTrue(decimais <= {"0,300", "0,400", "0,050", "0,010"}, decimais)
        blocos = re.findall(r"<!-- HC:(\w+):inicio -->", self.doc)
        self.assertEqual(len(blocos), len(set(blocos)))
        for b in ("resposta_curta", "capitais", "balanco", "composicao", "composicao_estreita", "h1", "antigas",
                  "leitura", "conferencias", "figuras", "limites", "decisoes"):
            self.assertIn(b, blocos)

    def test_linguagem(self):
        baixo = self.doc.lower()
        self.assertIn("pós-resultado", baixo)
        self.assertIn("limite da rdd em 0,300", baixo)
        self.assertIn("não quer dizer que a bolsa não tenha efeito", baixo)
        self.assertIn("pacote do corte", baixo)
        for proibida in ("a bolsa reduz", "a bolsa causa", "efeito causal da bolsa", "a bolsa não tem efeito"):
            self.assertNotIn(proibida, baixo)
        self.assertNotIn("pendente", baixo.split("## 7. conferências")[1].split("## 8.")[0])


if __name__ == "__main__":
    unittest.main()
