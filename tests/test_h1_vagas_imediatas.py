"""Testes do adendo 48b (script 40): H1 só com vagas imediatas (HI-1, HI-2, HI-s1 a HI-s8).

- O doc 57n tem de ser idêntico ao que o script gera a partir de `output/`.
- Os números das primárias são refeitos com código próprio (rdd_lib direto, agregação própria) e comparados com
  `output/rdd_bolsa/HI_estimativas.csv`; Holm e BKY são recalculados.
- A reprodução (A3, N1 S-a, 49b §14) é conferida contra `NA_`, `N_` e `ND_estimativas.csv`.
- Um caso SINTÉTICO em memória (rotulado "sintético" aqui; nada vai para `output/`) confere o estimador por célula,
  a agregação por tipo de célula e as falhas fechadas.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "rdd_bolsa"
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "40_h1_vagas_imediatas.py"
DOC = ROOT / "docs" / "06_execucao" / "57n_resultados_H1_vagas_imediatas.md"
ADENDO = ROOT / "docs" / "06_execucao" / "48b_adendo_H1_vagas_imediatas.md"


def _mod(nome: str, caminho: Path):
    if nome in sys.modules:
        return sys.modules[nome]
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    return mod


HI = _mod("hi40_teste", SCRIPT)
L = HI.L


def _ler():
    return HI.ler_saidas()


class TestSinteticoEmMemoria(unittest.TestCase):
    """sintético: dados construídos aqui, só em memória."""

    def _celulas_sinteticas(self, salto: float) -> pd.DataFrame:
        # sintético: 3 ciclos, 40 municípios por lado, 3 células por município, y linear no IVS + salto + EF de curso
        linhas = []
        rng = np.random.default_rng(48)
        for k in (1, 2, 3):
            for j in range(80):
                s = round(255 + j * (90 / 79), 3)
                for curso in (1, 2, 3):
                    y = 0.30 + 0.002 * (s - 300) + (salto if s > 300 else 0.0) + 0.05 * curso + 0.01 * k
                    linhas.append({"co_ibge": f"{k}{j:05d}", "s_mil": round(s, 3), "fe_curso_ciclo": f"c{k}_curso{curso}",
                                   "y": y, "tipo_vaga_imediata": 1.0, "ciclo": k, "ruido": rng.normal()})
        return pd.DataFrame(linhas)

    def test_sintetico_estimador_celula_recupera_o_salto(self):
        # sintético: sem ruído, o salto comum com EF de curso × ciclo e retas por ciclo é exato
        d = self._celulas_sinteticas(-0.07)
        frames = {k: d[d["ciclo"] == k].reset_index(drop=True) for k in (1, 2, 3)}
        a = HI.amostra(frames, (1, 2, 3), 300)
        r = HI.est_celula(a, a.col("y"))
        self.assertAlmostEqual(r["tau"], -0.07, places=10)
        self.assertEqual(r["n_clusters"], len(set(a.cl[np.abs(L.normalizar_s_mil(a.s) - 300) < 50])))

    def test_sintetico_agregacao_conta_todos_os_alocados_da_mista(self):
        # sintético: um município com uma célula pura, uma mista e uma só de reserva
        cel = pd.DataFrame({"ciclo": [1, 1, 1], "co_ibge": ["999999"] * 3,
                            "vagas_imediatas": [2.0, 1.0, 0.0], "vagas_cr": [0.0, 3.0, 2.0], "aloc": [1.0, 3.0, 1.0]})
        cel["tipo_celula"] = HI.tipo_celula(cel["vagas_imediatas"], cel["vagas_cr"])
        self.assertEqual(cel["tipo_celula"].tolist(), ["so_imed", "mista", "so_cr"])
        g = HI.agregar_municipio(cel).iloc[0]
        self.assertEqual(g["aloc_imed"], 4.0)    # mista conta todos os 3 alocados (limite registrado)
        self.assertEqual(g["vi_imed"], 3.0)      # controle de HI-2: só as vagas imediatas
        self.assertEqual(g["aloc_pura"], 1.0)
        self.assertEqual(g["vi_pura"], 2.0)
        self.assertEqual(g["aloc_cr"], 1.0)
        self.assertEqual(g["vcr_cr"], 2.0)

    def test_sintetico_celula_sem_vaga_falha(self):
        # sintético: célula sem vaga nenhuma não existe no quadro e para o script
        with self.assertRaises(HI.FalhaValidacao):
            HI.tipo_celula(pd.Series([0.0, 1.0]), pd.Series([0.0, 0.0]))

    def test_sintetico_reproducao_falha_quando_diverge(self):
        # sintético: a comparação da reprodução para quando o salto não bate
        meu = {"tau": 0.10, "ep": 0.02, "p_valor": 0.01, "ic95_inf": 0.06, "ic95_sup": 0.14,
               "n_abaixo": 10, "n_acima": 9, "n_obs": 19}
        ref = pd.Series({"tau": 0.11, "ep": 0.02, "p_valor": 0.01, "n_abaixo": 10, "n_acima": 9, "n_obs": 19})
        with self.assertRaises(HI.FalhaValidacao):
            HI._comparar("sintetico", meu, ref)
        ref["tau"] = 0.10
        self.assertTrue(HI._comparar("sintetico", meu, ref)["reproduz"])


class TestSaidas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.est, cls.res = _ler()

    def test_rotulos_estatuto_e_natureza(self):
        self.assertEqual(set(self.est["natureza_dos_dados"]), {"EMPIRICO"})
        self.assertEqual(set(self.est["estatuto"]), {"ADENDO_48B_POS_RESULTADO"})
        self.assertEqual(self.res["estatuto"], "ADENDO_48B_POS_RESULTADO")
        self.assertEqual(self.res["natureza_dos_dados"], "EMPIRICO")
        self.assertEqual(set(self.est["status"]), {"EXECUTADO"})
        self.assertFalse(self.est["id_linha"].duplicated().any())

    def test_linhas_do_adendo_relatadas(self):
        for lid in ["HI-1", "HI-2"] + [f"HI-s{i}" for i in range(1, 9)]:
            self.assertTrue((self.est["linha"] == lid).any(), lid)
        prim = self.est[self.est["entra_holm"]]
        self.assertEqual(sorted(zip(prim["linha"], prim["corte"])),
                         sorted([("HI-1", "0.300"), ("HI-1", "0.400"), ("HI-2", "0.300"), ("HI-2", "0.400")]))
        self.assertTrue((prim["ciclo"] == "1+2+3").all())
        self.assertTrue((prim["versao_quadro_c2"] == "13fev").all())

    def test_holm_e_bky_recalculados(self):
        prim = self.est[self.est["entra_holm"]]
        np.testing.assert_allclose(prim["p_holm"], L.holm(prim["p_valor"].to_numpy(float)), rtol=0, atol=1e-14)
        sec = self.est[self.est["entra_bky"]]
        np.testing.assert_allclose(sec["q_bky"], L.qvalores_bky(sec["p_valor"].to_numpy(float)), rtol=0, atol=1e-14)
        self.assertTrue((sec["papel"] == "secundaria").all())
        fora = self.est[self.est["linha"].isin(["HI-s7", "SENS-19MAR"])
                        | self.est["variante"].str.startswith("ic_honesto")
                        | (self.est["variante"] == "definicao_literal_alocado")]
        self.assertFalse(fora["entra_bky"].any())
        self.assertFalse(fora["entra_holm"].any())

    def test_sensibilidade_19mar_rotulada(self):
        s = self.est[self.est["linha"] == "SENS-19MAR"]
        self.assertEqual(len(s), 8)
        self.assertEqual(set(s["rotulo"]), {"tipo de vaga pós-resultado (não usar)"})
        self.assertEqual(set(s["versao_quadro_c2"]), {"19mar"})
        self.assertEqual(set(s["papel"]), {"sensibilidade_nao_usar"})

    def test_tost_com_a_funcao_do_36_e_margens_do_protocolo_60(self):
        T36 = HI.T36
        for _, r in self.est[self.est["linha"] == "HI-s7"].iterrows():
            base = self.est[(self.est["linha"] == r["outcome"]) & (self.est["corte"] == r["corte"])
                            & (self.est["variante"] == "principal")].iloc[0]
            m = 0.10 if r["outcome"] == "HI-1" else 0.25 * base["media_abaixo"]
            self.assertAlmostEqual(r["margem"], m, places=12)
            t = T36.tost(r["tau"], r["ep"], r["margem"], r["vies_max"])
            self.assertAlmostEqual(r["p_tost"], t["p_tost"], places=12)
            self.assertEqual(r["leitura_tost"], T36.classificar(t["p_aumento"] < 0.05, t["p_queda"] < 0.05))

    def test_ic_honesto_da_primaria_e_o_de_M_x1(self):
        for _, r in self.est[self.est["entra_holm"]].iterrows():
            h = self.est[(self.est["linha"] == "HI-s8") & (self.est["outcome"] == r["outcome"])
                         & (self.est["corte"] == r["corte"]) & (self.est["variante"] == "ic_honesto_M_x1")].iloc[0]
            self.assertAlmostEqual(r["ic_honesto_inf"], h["ic95_inf"], places=12)
            self.assertAlmostEqual(h["tau"], r["tau"], places=10)

    def test_hashes_e_adendo_com_a_nota_7(self):
        self.assertEqual(self.res["adendo"]["sha256"], HI.sha256(ADENDO))
        self.assertEqual(self.res["adendo"]["sha256_com_nota_7"], HI.sha256(ADENDO))
        self.assertIn("## 7. Nota datada", ADENDO.read_text(encoding="utf-8"))
        for e in self.res["entradas"]:
            self.assertEqual(e["sha256"], HI.sha256(ROOT / e["arquivo"]), e["arquivo"])
        arquivos = {e["arquivo"] for e in self.res["entradas"]}
        self.assertIn("data/raw/aquisicao/vagas/2026_ciclo2_chamada1_vagas_e_servicos_retificado.xlsx", arquivos)

    def test_reproducao_registrada(self):
        rep = self.res["reproducao"]
        self.assertTrue(rep["reproduz"])
        self.assertLessEqual(rep["max_abs_dif"], 1e-9)
        self.assertEqual(len(rep["linhas"]), 10)
        na = pd.read_csv(OUT / "NA_estimativas.csv", dtype={"corte": str}, low_memory=False)
        n = pd.read_csv(OUT / "N_estimativas.csv", dtype={"corte": str}, low_memory=False)
        for x in rep["linhas"]:
            if x["id"] == "A3":
                ref = na[(na["outcome_id"] == "A3_PREENCHIDA") & (na["especificacao"] == "A3")
                         & (na["variante"] == "principal") & (na["populacao"] == "V1+V2+V3 (celulas)")
                         & (na["corte"] == x["corte"])].iloc[0]
            elif x["id"] == "N1":
                ref = n[(n["outcome_id"] == "N1") & (n["especificacao"] == "S-a") & (n["variante"] == "principal")
                        & (n["populacao"] == "V1+V2+V3") & (n["corte"] == x["corte"])].iloc[0]
            else:
                continue
            self.assertAlmostEqual(x["tau"], ref["tau"], places=12)
            self.assertAlmostEqual(x["ep"], ref["ep"], places=12)
            self.assertEqual(x["n_abaixo"], int(ref["n_abaixo"]))

    def test_amostra_conta_as_celulas_fora(self):
        cc = self.res["amostra"]["celulas"]
        cel = pd.read_parquet(HI.ARQ_VC)
        for k in (1, 3):   # ciclos 1 e 3: quadro do pipeline
            x = cc[f"V{k}"]
            self.assertEqual(x["celulas_no_quadro"], int((cel["ciclo"] == k).sum()))
            self.assertEqual(x["celulas_na_amostra_hi"] + x["celulas_so_cr"]
                             + x["celulas_sem_ivs_oficial_fora_da_rdd"], x["celulas_no_quadro"])
        q = self.res["quadro_ciclo2"]["conferencia"]
        self.assertEqual(q["celulas"], int((cel["ciclo"] == 2).sum()))
        self.assertEqual(cc["V2"]["celulas_so_cr"], q["celulas_so_cr_13fev"])


class TestNumerosRefeitos(unittest.TestCase):
    """Primárias refeitas com a rdd_lib direto e agregação própria (não com os invólucros do script)."""

    @classmethod
    def setUpClass(cls):
        cls.est, _ = _ler()
        cls.dados = HI.carregar()["13fev"]

    def _linha(self, oid, corte):
        e = self.est
        return e[(e["linha"] == oid) & (e["variante"] == "principal") & (e["corte"] == corte)].iloc[0]

    def test_hi1_refeita(self):
        for c in (300, 400):
            partes = []
            for k in (1, 2, 3):
                d = self.dados["CK"][k]
                d = d[d["vagas_imediatas"] > 0]
                partes.append(d.assign(corte=c, grupo=f"c{k}"))
            d = pd.concat(partes, ignore_index=True)
            r = L.rd_empilhado(d["s_mil"], d["n_alocados_ch1"].ge(1).astype(float), d["corte"], grupo=d["grupo"],
                               h_mil=50, cluster=d["co_ibge"], ids_unidade=d["co_ibge"],
                               efeitos_fixos=d["fe_curso_ciclo"])
            x = self._linha("HI-1", HI.ROTULO_CORTE[c])
            self.assertAlmostEqual(r["tau"], x["tau"], places=12)
            self.assertAlmostEqual(r["ep"], x["ep"], places=12)
            self.assertEqual(r["n_abaixo"], int(x["n_abaixo"]))

    def test_hi2_refeita(self):
        for c in (300, 400):
            partes = []
            for k in (1, 2, 3):
                cel = self.dados["CK"][k]
                im = cel[cel["vagas_imediatas"] > 0]
                g = im.groupby("co_ibge").agg(y=("n_alocados_ch1", "sum"), v=("vagas_imediatas", "sum"),
                                              s_mil=("s_mil", "first")).reset_index()
                partes.append(g.assign(corte=c, grupo=f"c{k}"))
            d = pd.concat(partes, ignore_index=True)
            # controle sem centrar, uma coluna por ciclo (o centro não muda o salto)
            Z = np.column_stack([np.where(d["grupo"] == f"c{k}", d["v"], 0.0) for k in (1, 2, 3)])
            r = L.rd_empilhado(d["s_mil"], d["y"].astype(float), d["corte"], grupo=d["grupo"], h_mil=50,
                               cluster=d["co_ibge"], ids_unidade=d["co_ibge"], Z=Z, nomes_z=["v1", "v2", "v3"])
            x = self._linha("HI-2", HI.ROTULO_CORTE[c])
            self.assertAlmostEqual(r["tau"], x["tau"], places=10)
            self.assertAlmostEqual(r["ep"], x["ep"], places=10)
            self.assertEqual(r["n_obs"], int(x["n_obs"]))

    def test_tipo_do_ciclo2_e_o_de_13fev(self):
        q = HI.A36L.ler_quadro(HI.ARQ_C2_13FEV)
        c2 = self.dados["cel"][self.dados["cel"]["ciclo"] == 2]
        chave = c2["co_cnes_7d"].astype(str).str.zfill(7) + "_" + c2["cod_curso"].astype(int).astype(str).str.zfill(2)
        vi = chave.map(q.set_index("chave")["vagas_imediatas"])
        np.testing.assert_array_equal(vi.to_numpy(float), c2["vagas_imediatas"].to_numpy(float))
        for k in (1, 3):
            pipe = pd.read_parquet(HI.ARQ_VC)
            pipe = pipe[pipe["ciclo"] == k]
            np.testing.assert_array_equal(self.dados["cel"].loc[self.dados["cel"]["ciclo"] == k, "vagas_imediatas"]
                                          .to_numpy(float), pipe["vagas_imediatas"].to_numpy(float))


class TestDocumento(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.est, cls.res = _ler()
        cls.texto = DOC.read_text(encoding="utf-8")

    def test_doc_igual_ao_gerado(self):
        self.assertEqual(self.texto, HI.gerar_doc(self.est, self.res))

    def test_secoes(self):
        for s in ("## 1. Resposta curta", "## 2. Amostra", "## 3. Primárias", "## 4. Secundárias", "## 5. Figuras",
                  "## 6. Limites"):
            self.assertIn(s, self.texto)
        for nome in ("resposta_curta", "amostra", "quadro_ciclo2", "reproducao", "primarias", "sens_19mar", "limites"):
            self.assertIn(f"<!-- HI:{nome}:inicio -->", self.texto)

    def test_figuras_existem_com_como_ler(self):
        self.assertEqual(len(self.res["figuras"]), 4)
        for f in self.res["figuras"]:
            self.assertTrue((ROOT / f["arquivo"]).exists(), f["arquivo"])
            self.assertTrue(f["como_ler"].startswith("Como ler:"))
            self.assertIn(Path(f["arquivo"]).name, self.texto)

    def test_linguagem(self):
        t = self.texto.lower()
        for proibido in ("a bolsa reduz", "a bolsa diminui", "efeito zero", "não há efeito"):
            self.assertNotIn(proibido, t)
        self.assertIn("pacote do corte", t)
        self.assertIn("tipo de vaga pós-resultado (não usar)", t)

    def test_numeros_das_primarias_no_doc(self):
        for _, r in self.est[self.est["entra_holm"]].iterrows():
            self.assertIn(HI.fv(r), self.texto)
            self.assertIn(HI.fic(r), self.texto)


class TestIntegridade(unittest.TestCase):
    def test_nao_le_ivs_errado_nem_cnes_nem_escreve_em_data(self):
        fonte = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("ivs_ipea_2010_municipios", fonte)
        self.assertNotIn("cnes_nacional", fonte)
        for s in ("N_estimativas.csv\", index", "NA_estimativas.csv\", index", "ND_estimativas.csv\", index"):
            self.assertNotIn(s, fonte)
        leitura = (ROOT / "scripts" / "auditoria_H1" / "a36_leitura.py").read_text(encoding="utf-8")
        self.assertNotIn("to_csv", leitura)
        self.assertNotIn("ivs_ipea_2010_municipios", leitura)

    def test_sem_identificador_pessoal(self):
        est = pd.read_csv(OUT / "HI_estimativas.csv")
        self.assertFalse(any(c.lower() in ("cpf", "nome", "id_candidato") for c in est.columns))


if __name__ == "__main__":
    unittest.main()
