"""Testes do P6 (protocolo 56): `scripts/rdd_bolsa/30_mecanismo_alocacao.py` e `31_rd_mecanismo.py`.

Três partes:

1. `TestSintetico`: DADOS SINTÉTICOS gerados em memória (semente fixa), rotulados "sintético" (`SINTETICO_TESTE`)
   e nunca gravados em `output/` nem em `data/`. Conferem o R1 (efeito conhecido, efeito fixo de célula, células
   de um lado só fora, permutação), o Wald, o R3, o painel candidato × mês (zero só para quem não aparece numa
   competência lida, hora vazia = ausente, município da 1ª opção, fora da origem, sem origem = ausente) e a regra
   de elegibilidade das células.
2. `TestSaidasReais`: esquema e rótulos de `output/rdd_bolsa/P6_*`, ausência de identificadores (inclusive uma
   varredura de `output/`), BKY e Holm só na família do protocolo e recalculados, hashes, "Como ler" e números
   refeitos de `output/` com código próprio (média ponderada das diferenças por célula).
3. `TestDoc57f`: o doc 57f é igual ao que o script gera das saídas, e a linguagem segue o protocolo.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
RDD = ROOT / "scripts" / "rdd_bolsa"


def _importar(caminho: Path, nome: str):
    if nome in sys.modules:
        return sys.modules[nome]
    bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    sys.dont_write_bytecode = bytecode
    return mod


P0 = _importar(RDD / "30_mecanismo_alocacao.py", "passo0_p6")
P6 = _importar(RDD / "31_rd_mecanismo.py", "rd_mecanismo_31")

OUT = ROOT / "output" / "rdd_bolsa"
EST = OUT / "P6_estimativas.csv"
RESUMO = OUT / "P6_resumo.json"
PASSO0 = OUT / "P6_passo0_resumo.json"
AMOSTRA = OUT / "P6_amostra.parquet"
CELULAS = OUT / "P6_celulas.csv"
COBERTURA = OUT / "P6_cobertura_mensal.csv"
DOC = ROOT / "docs" / "06_execucao" / "57f_resultados_P6_mecanismo.md"

NATUREZA_SINTETICA = "SINTETICO_TESTE"   # rótulo dos dados gerados aqui (sintético); nunca gravados


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def dados_sinteticos(semente: int = 7, tau: float = 3.0, ruido: float = 1.0, n_cel: int = 40):
    """SINTÉTICO: células com efeito fixo próprio, r ∈ {−2, −1, +1, +2} e efeito tau acima do corte."""
    rng = np.random.default_rng(semente)
    linhas = []
    for c in range(n_cel):
        alfa = rng.normal(10, 5)
        for r in (-2, -1, 1, 2):
            for _ in range(int(rng.integers(1, 4))):
                z = float(r > 0)
                linhas.append({"celula": f"s{c:02d}", "r": r, "z": z,
                               "y": alfa + tau * z + ruido * rng.normal(), "natureza": NATUREZA_SINTETICA})
    return pd.DataFrame(linhas)


def fe_independente(y, z, cel) -> float:
    """Código próprio: média das diferenças acima − abaixo por célula, pesos n_c p_c (1 − p_c)."""
    d = pd.DataFrame({"y": y, "z": z, "c": cel}).dropna()
    num = den = 0.0
    for _, g in d.groupby("c"):
        n1, n0 = int((g["z"] == 1).sum()), int((g["z"] == 0).sum())
        if n1 == 0 or n0 == 0:
            continue
        n = n1 + n0
        w = n * (n1 / n) * (n0 / n)
        num += w * (g.loc[g["z"] == 1, "y"].mean() - g.loc[g["z"] == 0, "y"].mean())
        den += w
    return num / den if den else np.nan


class TestSintetico(unittest.TestCase):
    """Verificação sintética (dados sintéticos em memória, rotulados SINTETICO_TESTE)."""

    def test_rotulo_sintetico(self):
        self.assertTrue((dados_sinteticos()["natureza"] == "SINTETICO_TESTE").all())

    def test_r1_recupera_efeito_sem_ruido_e_ignora_efeito_fixo(self):
        d = dados_sinteticos(ruido=0.0, tau=3.0)
        res = P6.r1(d["y"], d["z"], d["celula"], b_perm=99)
        self.assertAlmostEqual(res["estimativa"], 3.0, places=10)
        self.assertLess(res["p_perm"], 0.05)

    def test_r1_igual_a_media_ponderada_e_permutacao_sob_nulo(self):
        d = dados_sinteticos(ruido=1.0, tau=0.0, semente=11)
        res = P6.r1(d["y"], d["z"], d["celula"], b_perm=199)
        self.assertAlmostEqual(res["estimativa"], fe_independente(d["y"], d["z"], d["celula"]), places=10)
        self.assertGreater(res["p_perm"], 0.01)
        self.assertTrue(abs(res["estimativa"]) < 4 * res["ep"])

    def test_celula_de_um_lado_so_nao_entra(self):
        d = dados_sinteticos(ruido=0.5, semente=5)
        extra = pd.DataFrame({"celula": ["unilateral"] * 3, "r": [1, 2, 1], "z": [1.0] * 3, "y": [1e6] * 3,
                              "natureza": NATUREZA_SINTETICA})
        a = P6.r1(d["y"], d["z"], d["celula"], permutar=False)
        b = P6.r1(pd.concat([d, extra])["y"], pd.concat([d, extra])["z"], pd.concat([d, extra])["celula"],
                  permutar=False)
        self.assertAlmostEqual(a["estimativa"], b["estimativa"], places=10)
        self.assertEqual(b["n_celulas_dois_lados"], a["n_celulas_dois_lados"])

    def test_permutacao_deterministica(self):
        d = dados_sinteticos(ruido=1.0, tau=0.5)
        self.assertEqual(P6.r1(d["y"], d["z"], d["celula"], b_perm=99)["p_perm"],
                         P6.r1(d["y"], d["z"], d["celula"], b_perm=99)["p_perm"])

    def test_wald_com_primeiro_estagio_parcial(self):
        d = dados_sinteticos(ruido=0.0, tau=0.0, semente=3)
        rng = np.random.default_rng(1)
        dd = np.where(d["z"] == 1, (rng.random(len(d)) < 0.8).astype(float), 0.0)
        y = d["y"].to_numpy() + 4.0 * dd
        w = P6.wald(y, dd, d["z"], d["celula"])
        self.assertAlmostEqual(w["estimativa"], 4.0, places=8)

    def test_r3_tendencia_linear(self):
        d = dados_sinteticos(ruido=0.0, tau=2.0, semente=9)
        y = d["y"] + 0.7 * d["r"]
        X = np.column_stack([d["z"], d["r"], d["z"] * d["r"]])
        g = P6.regressao_fe(y, X, ["acima", "r", "acima_x_r"], d["celula"])
        self.assertAlmostEqual(g["estimativa"], 2.0, places=8)

    def test_painel_candidato_mes_sintetico(self):
        comps = ["202601", "202602", "202603"]
        v = pd.DataFrame({
            "competencia": ["202601", "202601", "202602", "202601"],
            "co_profissional_sus": ["A", "A", "A", "B"],
            "co_cnes": ["1", "2", "1", "3"],
            "co_municipio": ["100", "200", "100", "300"],
            "co_cbo": ["225125"] * 4,
            "tp_sus_nao_sus": ["S", "N", "S", "S"],
            "qt_ch_ambulatorial": pd.array([10, 5, 10, pd.NA], dtype="Int32"),
            "qt_ch_hosp_sus": pd.array([0, 0, 0, 0], dtype="Int32"),
            "qt_ch_outros": pd.array([0, 0, 0, 0], dtype="Int32"),
        })
        cmap = pd.DataFrame({"chave": ["kA", "kB"], "co_profissional_sus": ["A", "B"],
                             "co_ibge_1a_opcao": pd.array(["200", "300"], dtype="string"),
                             "tem_origem": [True, False]})
        origem = pd.DataFrame({"chave": ["kA"], "co_municipio": ["100"]}).astype("string")
        p = P0.painel_candidato_mes(v, cmap, origem, comps).set_index(["chave", "competencia"])
        a1 = p.loc[("kA", "202601")]
        self.assertEqual(a1["y3_horas_totais"], 15.0)
        self.assertEqual(a1["y2_horas_sus"], 10.0)
        self.assertEqual(a1["y1_vinculo_mun_1a_opcao"], 1.0)
        self.assertEqual(a1["y4_vinculo_fora_origem"], 1.0)
        self.assertEqual(a1["y5_n_municipios"], 2.0)
        a2 = p.loc[("kA", "202602")]
        self.assertEqual((a2["y1_vinculo_mun_1a_opcao"], a2["y4_vinculo_fora_origem"]), (0.0, 0.0))
        a3 = p.loc[("kA", "202603")]                      # competência lida, sem vínculo: zero
        self.assertEqual((a3["tem_vinculo_medico"], a3["y3_horas_totais"], a3["y5_n_municipios"]), (0.0, 0.0, 0.0))
        b1 = p.loc[("kB", "202601")]                      # hora vazia: ausente, nunca zero
        self.assertTrue(np.isnan(b1["y3_horas_totais"]) and np.isnan(b1["y2_horas_sus"]))
        self.assertTrue(np.isnan(p.loc[("kB", "202602"), "y4_vinculo_fora_origem"]))  # sem origem: ausente

    def test_holm_e_bky_da_biblioteca(self):
        p = np.array([0.01, 0.04, 0.03, 0.5])
        np.testing.assert_allclose(P6.L.holm(p), [0.04, 0.09, 0.09, 0.5])
        self.assertTrue((P6.L.qvalores_bky(p) >= 0).all())


class TestSaidasReais(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.est = pd.read_csv(EST)
        cls.est["nota"] = cls.est["nota"].fillna("")
        cls.resumo = json.loads(RESUMO.read_text(encoding="utf-8"))
        cls.p0 = json.loads(PASSO0.read_text(encoding="utf-8"))
        cls.am = pd.read_parquet(AMOSTRA)
        cls.cel = pd.read_csv(CELULAS, dtype={"co_cnes_7d": str})
        cls.cob = pd.read_csv(COBERTURA)

    def test_esquema_e_rotulos(self):
        self.assertEqual(list(self.est.columns), P6.COLUNAS)
        for df in (self.est, self.am, self.cel, self.cob):
            self.assertTrue((df["natureza_dos_dados"] == "EMPIRICO").all())
            self.assertTrue((df["estatuto"] == "EXPLORATORIO_P6").all())
        for r in (self.resumo, self.p0):
            self.assertEqual(r["natureza_dos_dados"], "EMPIRICO")
            self.assertEqual(r["estatuto"], "EXPLORATORIO_P6")
        self.assertTrue(set(self.est["status"]) <= {"EXECUTADO", "SEM_ESTIMATIVA", "NAO_EXECUTADO"})
        self.assertEqual(set(self.est["especificacao"]), {"PE_por_r", "PE", "BAL", "R1", "R2", "R3", "R4", "R5", "R6",
                                                         "T6.3", "medias_por_r"})
        self.assertTrue(self.est["leitura"].fillna("").str.len().gt(0).all())
        self.assertEqual(list(self.am.columns), self.p0["saidas"]["P6_amostra.parquet"]["colunas"])
        self.assertEqual(set(self.am["regra_ligacao"]), set(P0.REGRAS))
        self.assertEqual(set(self.am["ciclo"]), {1, 2})

    def test_ausencia_tem_nota(self):
        sem = self.est[self.est["estimativa"].isna()]
        self.assertTrue((sem["nota"] != "").all())
        self.assertTrue(sem["status"].isin(["SEM_ESTIMATIVA", "NAO_EXECUTADO"]).all())
        self.assertTrue((self.est.loc[self.est["especificacao"].isin(["R6", "T6.3"]), "status"]
                         == "NAO_EXECUTADO").all())
        nl = self.am[self.am["ligado"] == 0]
        self.assertTrue(nl["y3_horas_totais_media"].isna().all())
        self.assertTrue(nl["motivo_ausencia"].str.contains("não ligado").all())
        aus = self.am[(self.am["ligado"] == 1) & self.am["y4_vinculo_fora_origem_media"].isna()]
        self.assertTrue(aus["motivo_ausencia"].str.contains("referência").all())

    def test_sem_identificadores_nas_saidas_do_p6(self):
        proibidos = ("nome", "cpf", "cns", "crm", "co_profissional", "id_prof", "nu_registro", "_chave", "_padrao")
        for df in (self.est, self.am, self.cel, self.cob):
            for c in df.columns:
                self.assertFalse(any(p in c.lower() for p in proibidos), c)
        texto = EST.read_text(encoding="utf-8") + RESUMO.read_text(encoding="utf-8") + PASSO0.read_text(
            encoding="utf-8") + COBERTURA.read_text(encoding="utf-8")
        self.assertIsNone(re.search(r"\bc[123]_\d{5}\b|\bg5p_\d+|\bx1m_\d+", texto))
        self.assertIsNone(re.search(r"(?<![\d.])\d{15}(?![\d.])", texto))
        for chave in ("\"_nome\"", "\"crm\"", "\"cpf\"", "\"cns\"", "co_profissional_sus\":"):
            self.assertNotIn(chave, (RESUMO.read_text(encoding="utf-8") + PASSO0.read_text(encoding="utf-8")).lower())

    def test_varredura_de_output_sem_colunas_pessoais(self):
        """Todo CSV e parquet versionável de output/ (rastreados e não ignorados pelo Git) sem coluna de nome, CPF,
        CNS, CRM ou código do profissional. Exceção única: `nome` dos pilares teóricos da revisão de literatura."""
        fs = subprocess.run(["git", "ls-files", "-co", "--exclude-standard", "output"], capture_output=True,
                            text=True, cwd=ROOT).stdout.split()
        self.assertIn("output/rdd_bolsa/P6_amostra.parquet", fs)
        proib = {"nome", "no_profissional", "nome_norm", "cpf", "co_cpf", "cns", "co_cns", "crm", "nu_registro",
                 "sg_uf_crm", "co_profissional_sus"}
        excecao = {("output/revisao_literatura/pilares_teoricos_pmme.csv", "nome")}
        achados = []
        for f in fs:
            p = ROOT / f
            if "cache" in Path(f).parts or not p.exists():
                continue
            if p.suffix == ".parquet":
                cols = pq.read_schema(p).names
            elif p.suffix == ".csv":
                with open(p, encoding="utf-8", errors="ignore") as h:
                    cols = next(csv.reader(h), [])
            else:
                continue
            achados += [(f, c) for c in cols if c.strip().lower() in proib and (f, c.strip().lower()) not in excecao]
        self.assertEqual(achados, [])

    def test_cache_privado_no_gitignore(self):
        texto = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        for l in P0.LINHAS_GITIGNORE:
            self.assertIn(l, texto)
        self.assertTrue(self.p0["cache_privado"]["gitignore"]["presentes"])

    def test_passo0_reproduz_a16_e_g1(self):
        self.assertTrue(self.p0["reproducao_a16"]["ligacao_x1_reproduzida_100pct"])
        self.assertTrue(self.p0["reproducao_a16"]["painel_medico_mes_identico"])
        self.assertEqual(self.p0["reproducao_a16"]["linhas_painel_medico_mes"],
                         len(pd.read_parquet(P0.A16_PAINEL_MEDICO)))
        g1 = pd.read_parquet(P0.G1_CAND)
        for regra, v in self.p0["ligacao"]["reproducao_g1"].items():
            self.assertTrue(all(n == 0 for n in v["diferencas_por_campo"].values()))
            self.assertEqual(v["ligados"], int(g1.loc[g1["regra_ligacao"] == regra, "ligado"].sum()))
        self.assertTrue(all(n == 0 for n in self.p0["conferencia_agregacao_a16"]["diferencas"].values()))

    def test_ligacao_da_amostra_igual_ao_g1(self):
        g1 = pd.read_parquet(P0.G1_CAND)[["regra_ligacao", "ciclo", "id_candidato", "ligado", "motivo"]]
        m = self.am.merge(g1, on=["regra_ligacao", "ciclo", "id_candidato"], suffixes=("", "_g1"), validate="one_to_one")
        self.assertEqual(len(m), len(self.am))
        self.assertTrue((m["ligado"].astype(int) == m["ligado_g1"].astype(int)).all())
        self.assertTrue((m["motivo_ligacao"] == m["motivo"]).all())

    def test_amostra_recalculada_do_g2(self):
        """r = nota − corte, D e D' refeitos do G2; células elegíveis pela regra do adendo."""
        g2 = pd.read_parquet(P0.G2_ALOC)
        g2 = g2[(g2["chamada"] == 1) & g2["ciclo"].isin([1, 2])]
        a = self.am[self.am["regra_ligacao"] == "g1_cpf_nome"].merge(g2, on=["ciclo", "id_candidato"],
                                                                    validate="one_to_one")
        self.assertTrue((a["r"] == a["margem_1a_opcao"]).all())
        self.assertTrue((a["inscricao_em_reserva"] == 0).all())
        d = ((a["alocado_publicado"] == 1) & (a["co_cnes_7d_publicado"] == a["co_cnes_7d_1a_opcao"])
             & (a["cod_curso_publicado"] == a["cod_curso_1a_opcao"])).astype(int)
        self.assertTrue((d == a["d_alocado_1a_opcao"]).all())
        self.assertTrue((a["alocado_publicado"] == a["d_alocado_pmme"]).all())
        el = self.cel[self.cel["celula_elegivel"] == 1]
        self.assertTrue((el["vagas_total"] == el["vagas_imediatas_quadro"]).all())
        self.assertTrue((el["corte_pontuacao"] < el["maior_nota_ac_1a_opcao"]).all())
        self.assertTrue((el["corte_opcao"] == 1).all() and (el["corte_ativo"] == 1).all())
        self.assertEqual(set(self.am["celula"]), set(el["celula"]) & set(self.am["celula"]))
        self.assertEqual(int(self.cel["celula_elegivel"].sum()),
                         sum(self.p0["contagens"]["celulas_elegiveis"].values()))

    def test_familia_bky_holm(self):
        f = self.est[self.est["entra_familia"]]
        self.assertEqual(len(f), 10)
        self.assertTrue((f["especificacao"] == "R1").all() and (f["regra_ligacao"] == "g1_cpf_nome").all())
        self.assertEqual(set(f["medida"]), {"ultimo", "media"})
        self.assertTrue(self.est.loc[~self.est["entra_familia"], ["q_bky", "p_holm"]].isna().all().all())
        np.testing.assert_allclose(P6.L.qvalores_bky(f["p_valor"].to_numpy(float)), f["q_bky"], atol=1e-9)
        np.testing.assert_allclose(P6.L.holm(f["p_valor"].to_numpy(float)), f["p_holm"], atol=1e-9)
        np.testing.assert_allclose(f["p_valor"], f["p_perm"])
        k = f["p_perm"].to_numpy(float) * (P6.B_PERM + 1)
        np.testing.assert_allclose(k, np.round(k), atol=1e-6)   # p = (1 + contagem) / 1000

    def test_r1_recalculado_com_codigo_proprio(self):
        d = self.am[(self.am["regra_ligacao"] == "g1_cpf_nome") & (self.am["ligado"] == 1)
                    & self.am["r"].isin([-2, -1, 1, 2])]
        z = (d["r"] > 0).astype(float)
        for col, _, _, _ in P0.OUTCOMES:
            for med in ("ultimo", "media"):
                r = self.est[(self.est["especificacao"] == "R1") & (self.est["outcome"] == col)
                             & (self.est["medida"] == med)].iloc[0]
                self.assertAlmostEqual(r["estimativa"], fe_independente(d[f"{col}_{med}"], z, d["celula"]), places=8)
        for c, _, _ in P0.COVARIAVEIS:
            r = self.est[(self.est["especificacao"] == "BAL") & (self.est["outcome"] == c)].iloc[0]
            self.assertAlmostEqual(r["estimativa"], fe_independente(d[c], z, d["celula"]), places=8)
        dt = self.am[(self.am["regra_ligacao"] == "g1_cpf_nome") & self.am["r"].isin([-2, -1, 1, 2])]
        r = self.est[(self.est["especificacao"] == "BAL") & (self.est["outcome"] == "ligado")
                     & (self.est["regra_ligacao"] == "g1_cpf_nome") & (self.est["medida"] == "R1")].iloc[0]
        self.assertAlmostEqual(r["estimativa"], fe_independente(dt["ligado"].astype(float), (dt["r"] > 0).astype(float),
                                                                dt["celula"]), places=8)

    def test_primeiro_estagio_por_r_recalculado(self):
        d = self.am[self.am["regra_ligacao"] == "g1_cpf_nome"]
        s = self.est[(self.est["especificacao"] == "PE_por_r") & (self.est["amostra"] == "todos")]
        for _, r in s.iterrows():
            g = d[d["r"] == r["r"]]
            self.assertEqual(int(r["n_obs"]), len(g))
            self.assertAlmostEqual(r["estimativa"], g[r["outcome"]].mean(), places=10)

    def test_resumo_e_contagens_batem(self):
        am = self.resumo["amostra"]["principal"]
        d = self.am[(self.am["regra_ligacao"] == "g1_cpf_nome") & (self.am["ligado"] == 1)
                    & self.am["r"].isin([-2, -1, 1, 2])]
        self.assertEqual(am["acima"], int((d["r"] > 0).sum()))
        self.assertEqual(am["abaixo"], int((d["r"] < 0).sum()))
        self.assertEqual(am["celulas"], d["celula"].nunique())
        up = self.p0["universo_principal"]
        self.assertEqual(up["candidatos"], int((self.am["regra_ligacao"] == "g1_cpf_nome").sum()))
        for k, v in self.resumo["principais"].items():
            if k.startswith("R1_"):
                self.assertIsNotNone(v["n_obs"])
        c = self.p0["contagens"]["candidatos"]
        for k in ("1", "2"):
            self.assertEqual(c[k]["no_universo_p6"],
                             int(((self.am["regra_ligacao"] == "g1_cpf_nome") & (self.am["ciclo"] == int(k))).sum()))

    def test_cobertura_sem_quebra_por_r(self):
        self.assertNotIn("r", self.cob.columns)
        self.assertTrue((self.cob["competencia"].astype(str) < "202609").all())
        self.assertEqual(self.cob["competencia"].astype(str).min(), "202406")
        self.assertTrue(self.cob["fracao_com_vinculo_medico"].between(0, 1).all())

    def test_hashes_entradas_e_figuras(self):
        for ent in self.resumo["entradas"]:
            self.assertEqual(sha256(ROOT / ent["caminho"]), ent["sha256"], ent["caminho"])
        for ent in self.p0["entradas"]:
            self.assertEqual(sha256(ROOT / ent["caminho"]), ent["sha256"], ent["caminho"])
        for nome, s in self.p0["saidas"].items():
            self.assertEqual(sha256(ROOT / s["arquivo"]), s["sha256"], nome)
        self.assertEqual(sha256(EST), self.resumo["saidas"]["P6_estimativas.csv"]["sha256"])
        figs = self.resumo["saidas"]["figuras"]
        self.assertEqual(len(figs), 4)
        for f in figs:
            self.assertEqual(sha256(ROOT / f["arquivo"]), f["sha256"])
            self.assertTrue(f["como_ler"])
            self.assertEqual(self.resumo["como_ler"][Path(f["arquivo"]).name], f["como_ler"])
            n_frases = len([s for s in re.split(r"(?<=[.;])\s", f["como_ler"]) if s.strip()])
            self.assertLessEqual(n_frases, 3)

    def test_nao_le_ivs_errado_nem_mes_proibido(self):
        for s in (RDD / "30_mecanismo_alocacao.py", RDD / "31_rd_mecanismo.py"):
            fonte = s.read_text(encoding="utf-8")
            self.assertNotIn("ivs_ipea_2010_municipios", fonte)
            limpo = fonte.replace("20261019", "").replace('LIMITE_EXCLUSIVO = "202609"', "").replace(">= 202609", "")
            self.assertIsNone(re.search(r"202609|20261[0-2]|2027\d\d", limpo))
        self.assertEqual(self.p0["parametros"]["limite_exclusivo"], "202609")
        self.assertEqual(self.p0["parametros"]["competencias"], ["202406", "202608"])

    def test_desvios_registrados(self):
        itens = [d["item"] for d in self.resumo["desvios"]]
        self.assertTrue(any("célula × ampla concorrência" in i for i in itens))
        self.assertTrue(any("Passo 0" in i for i in itens))
        self.assertTrue(any("R6" in i for i in itens))


class TestDoc57f(unittest.TestCase):
    def test_doc_igual_ao_gerado(self):
        est, resumo, p0, am = P6.ler_saidas()
        self.assertEqual(DOC.read_text(encoding="utf-8"), P6.gerar_doc(est, resumo, p0, am))

    def test_linguagem(self):
        texto = DOC.read_text(encoding="utf-8").lower()
        for termo in ("efeito causal", "causou", "comprova", "efeito da bolsa é"):
            self.assertNotIn(termo, texto)
        self.assertIn("não é o efeito da bolsa", texto)
        self.assertIn("vínculo cadastrado não é presença", texto)
        self.assertIn("como ler", texto)
        self.assertIn("taxa de ligação", texto)


if __name__ == "__main__":
    unittest.main()


class TestRecalculoIndependenteAuditoria27(unittest.TestCase):
    """Recálculo independente da auditoria 27 (`docs/auditorias/27_auditoria_P6_mecanismo.md`).

    Código próprio em pandas/numpy a partir de `P6_amostra.parquet` (agregado pseudônimo versionado), sem chamar
    funções dos scripts 30 e 31: contagem da janela, primeiro estágio, R1 (efeito fixo de célula por centragem) em
    Y1 e Y3, permutação dentro da célula com outra semente (ordem de grandeza), Holm e BKY da família de 10 e
    balanço de distância e taxa de ligação. Também confere os avisos do doc.
    """

    @classmethod
    def setUpClass(cls):
        g = pd.read_parquet(AMOSTRA)
        g = g[g["regra_ligacao"] == "g1_cpf_nome"]
        w = g[g["r"].isin([-2, -1, 1, 2])].copy()
        w["D"] = (w["r"] > 0).astype(int)
        cls.g, cls.w = g, w
        cls.est = pd.read_csv(EST)

    @staticmethod
    def _fe(df, y):
        df = df[df.groupby("celula")["D"].transform(lambda s: s.nunique() == 2)]
        yy = df[y] - df.groupby("celula")[y].transform("mean")
        dd = df["D"] - df.groupby("celula")["D"].transform("mean")
        return float((dd * yy).sum() / (dd * dd).sum()), df

    @staticmethod
    def _perm(df, y, B=1999, semente=7):
        rng = np.random.default_rng(semente)
        b, df = TestRecalculoIndependenteAuditoria27._fe(df, y)
        grupos = [np.where(df["celula"].to_numpy() == c)[0] for c in df["celula"].unique()]
        yv, dv = df[y].to_numpy(float), df["D"].to_numpy(float)
        n = 0
        for _ in range(B):
            num = den = 0.0
            for ix in grupos:
                dp = rng.permutation(dv[ix])
                d0 = dp - dp.mean()
                num += float((d0 * (yv[ix] - yv[ix].mean())).sum())
                den += float((d0 * d0).sum())
            n += abs(num / den) >= abs(b) - 1e-12
        return (n + 1) / (B + 1)

    def _est(self, esp, out, medida):
        r = self.est[(self.est["especificacao"] == esp) & (self.est["regra_ligacao"] == "g1_cpf_nome") &
                     (self.est["outcome"] == out) & (self.est["medida"] == medida)]
        self.assertEqual(len(r), 1)
        return r.iloc[0]

    def test_contagens_e_primeiro_estagio(self):
        self.assertEqual((len(self.g), self.g["celula"].nunique()), (320, 62))
        lig = self.w[self.w["ligado"] == 1]
        self.assertEqual(((lig["D"] == 1).sum(), (lig["D"] == 0).sum()), (64, 70))
        b, df = self._fe(lig, "d_alocado_1a_opcao")
        self.assertEqual((round(b, 6), int((df["D"] == 1).sum()), int((df["D"] == 0).sum())), (1.0, 30, 68))
        b, _ = self._fe(lig, "d_alocado_pmme")
        self.assertAlmostEqual(b, 0.917902, places=5)
        b, df = self._fe(self.w, "d_alocado_pmme")
        self.assertAlmostEqual(b, 0.925721, places=5)
        self.assertEqual((int((df["D"] == 1).sum()), int((df["D"] == 0).sum())), (32, 73))

    def test_r1_y1_y3_e_permutacao(self):
        lig = self.w[self.w["ligado"] == 1]
        for col, out, medida, pmax in (("y1_vinculo_mun_1a_opcao_ultimo", "y1_vinculo_mun_1a_opcao", "ultimo", 0.005),
                                       ("y1_vinculo_mun_1a_opcao_media", "y1_vinculo_mun_1a_opcao", "media", 0.005),
                                       ("y3_horas_totais_media", "y3_horas_totais", "media", 0.12)):
            s = lig.dropna(subset=[col])
            b, _ = self._fe(s, col)
            e = self._est("R1", out, medida)
            self.assertAlmostEqual(b, float(e["estimativa"]), places=6)
            p = self._perm(s, col)
            self.assertLess(p, pmax)
            if out == "y3_horas_totais":
                self.assertGreater(p, 0.01)
                self.assertLess(abs(p - float(e["p_perm"])), 0.03)

    def test_holm_e_bky_da_familia(self):
        f = self.est[self.est["entra_familia"].astype(bool)]
        p = f["p_perm"].to_numpy(float)
        m = len(p)
        self.assertEqual(m, 10)
        o = np.argsort(p)
        holm, corrente = np.empty(m), 0.0
        for k, i in enumerate(o):
            corrente = max(corrente, (m - k) * p[i])
            holm[i] = min(corrente, 1.0)
        np.testing.assert_allclose(holm, f["p_holm"].to_numpy(float), atol=1e-3)
        q = np.ones(m)
        for nivel in np.arange(0.999, 0.0, -0.001):
            qq = nivel / (1 + nivel)
            ps = p[o]
            r1 = next((k for k in range(m, 0, -1) if ps[k - 1] <= qq * k / m), 0)
            if r1 == 0:
                continue
            if r1 == m:
                rej = np.ones(m, bool)
            else:
                q2 = qq * m / (m - r1)
                r2 = next((k for k in range(m, 0, -1) if ps[k - 1] <= q2 * k / m), 0)
                rej = np.zeros(m, bool)
                rej[o[:r2]] = True
            q[rej] = nivel
        np.testing.assert_allclose(q, f["q_bky"].to_numpy(float), atol=1e-3)
        y3 = self._est("R1", "y3_horas_totais", "media")
        self.assertLess(float(y3["p_perm"]), 0.05)
        self.assertGreater(float(y3["q_bky"]), 0.05)
        self.assertGreater(float(y3["p_holm"]), 0.05)

    def test_balanco_distancia_e_ligacao(self):
        lig = self.w[self.w["ligado"] == 1]
        b, _ = self._fe(lig.dropna(subset=["cov_dist_km"]), "cov_dist_km")
        self.assertAlmostEqual(b, float(self._est("BAL", "cov_dist_km", "R1")["estimativa"]), places=4)
        self.assertGreater(b, 300)
        w = self.w.assign(lg=self.w["ligado"].astype(float))
        b, df = self._fe(w, "lg")
        self.assertAlmostEqual(b, 0.0913, places=3)
        self.assertEqual(df.groupby("D")["lg"].mean().round(3).to_dict(), {0: 0.932, 1: 1.0})

    def test_doc_destaca_avisos(self):
        t = DOC.read_text(encoding="utf-8")
        self.assertIn("Leia com três avisos", t)
        self.assertIn("Y3, média do seguimento, não é efeito", t)
        self.assertIn("O degrau do Y1 é quase mecânico", t)
        self.assertNotIn("sugere efeito de ser alocado", t)
        for f in ("P6_balanco.png",):
            self.assertIn("Distância e ligação diferem", t)
