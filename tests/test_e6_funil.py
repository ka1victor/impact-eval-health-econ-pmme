"""Testes do E6 (`scripts/rdd_bolsa/13_estimar_E6_funil.py`).

Duas partes:

1. `TestPipelineSintetico` e `TestFuncoesSinteticas`: a cola do pipeline com
   DADOS SINTÉTICOS gerados em memória (semente fixa). Nada é gravado em
   `output/` nem em `data/`; os dados sintéticos só servem para conferir que o
   código recupera um salto conhecido, o sinal, as linhas do protocolo, os
   rótulos e as tabelas do doc.
2. `TestSaidasReais`: invariantes das saídas versionadas em
   `output/rdd_bolsa/E6_*`. Todo alvo de validação é lido de arquivos de
   `output/` (E3, outcomes, a08) ou recalculado de forma independente com numpy;
   nenhum número é digitado aqui.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "13_estimar_E6_funil.py"
_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location("e6_funil_13", SCRIPT)
E6 = importlib.util.module_from_spec(_spec)
sys.modules["e6_funil_13"] = E6
_spec.loader.exec_module(E6)
sys.dont_write_bytecode = _bytecode

OUT = ROOT / "output" / "rdd_bolsa"
EST = OUT / "E6_estimativas.csv"
DIAG = OUT / "E6_diagnosticos.csv"
RESUMO = OUT / "E6_resumo.json"
DOC = ROOT / "docs" / "06_execucao" / "41_resultados_E6_funil.md"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


# --------------------------------------------------------------------------
# Dados sintéticos (só em memória)
# --------------------------------------------------------------------------

SALTO_SINTETICO = 0.25


def dados_sinteticos(semente: int = 7) -> dict:
    """Municípios sintéticos com salto conhecido de +0,25 em F1.3 nos dois cortes."""
    rng = np.random.default_rng(semente)
    V, C = {}, {}
    for k in (1, 2):
        n = 400
        s = rng.integers(220, 481, n).astype(float)
        cod = [f"9{k}{i:04d}" for i in range(n)]
        t = ((s > 300) & (s <= 350)) | (s > 400)
        n_cel = rng.integers(1, 6, n)
        celulas = []
        for i in range(n):
            p = np.clip(0.3 + 0.4 * (s[i] / 1000 - 0.3) + SALTO_SINTETICO * t[i], 0, 1)
            for j in range(n_cel[i]):
                celulas.append({"co_ibge": cod[i], "s_mil": s[i], "f1_3_preenchida_ch1": float(rng.random() < p),
                                "f1_2_tem_candidato": float(rng.random() < min(1, p + 0.2))})
        cel = pd.DataFrame(celulas)
        agg = cel.groupby("co_ibge")[["f1_3_preenchida_ch1", "f1_2_tem_candidato"]].mean()
        d = pd.DataFrame({"co_ibge": cod, "s_mil": s, "n_celulas": n_cel})
        d["f1_3_fracao_celulas_preenchidas_ch1"] = d["co_ibge"].map(agg["f1_3_preenchida_ch1"])
        d["f1_2_fracao_celulas_com_candidato"] = d["co_ibge"].map(agg["f1_2_tem_candidato"])
        d["n_cand_1a_opcao"] = rng.poisson(d["n_celulas"] * np.exp(0.2 + 0.3 * t))
        d["f1_1_cand_1a_opcao_por_celula"] = d["n_cand_1a_opcao"] / d["n_celulas"]
        d["n_ativos_ciclo"] = rng.poisson(d["n_celulas"] * 0.5)
        d["f2_1_ativos_por_celula"] = d["n_ativos_ciclo"] / d["n_celulas"]
        V[k], C[k] = d, cel
    n = 1500
    s = rng.integers(150, 551, n).astype(float)
    u = pd.DataFrame({"co_ibge": [f"8{i:05d}" for i in range(n)], "s_mil": s})
    u["f0_1_tem_celula_c1"] = (rng.random(n) < 0.1).astype(float)
    g3 = pd.DataFrame({"co_ibge": ["700001", "700002"], "s_mil": [300.0, 401.0]})
    return {"U": u, "G3": g3, "V": V, "C": C}


SEM_S3_S4 = {"S3": {"tabela": None, "motivo": "insumo sintetico ausente"},
             "S4": {"tabela": None, "motivo": "insumo sintetico ausente"}}
LR_SINT = {("V1", 300): 10, ("V1", 400): 10, ("V2", 300): None, ("V2", 400): 8, ("U", 300): 5, ("U", 400): None}


class TestPipelineSintetico(unittest.TestCase):
    """Pipeline inteiro em dados sintéticos (nada é gravado)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.dados = dados_sinteticos()
        cls.est, cls.extras = E6.estimar_tudo(cls.dados, sup=SEM_S3_S4, lr=LR_SINT, log=lambda *a: None)

    def _linha(self, **f) -> pd.Series:
        m = np.ones(len(self.est), dtype=bool)
        for k, v in f.items():
            m &= self.est[k].astype(str) == str(v)
        sub = self.est[m]
        self.assertEqual(len(sub), 1, f)
        return sub.iloc[0]

    def test_recupera_salto_sintetico_em_f13(self) -> None:
        r = self._linha(outcome_id="F1.3", populacao="V1+V2", corte="empilhado", especificacao="principal")
        self.assertLess(abs(r["tau"] - SALTO_SINTETICO), 3 * r["ep"])
        self.assertGreater(r["tau"], 0)  # sinal: lado de cima (bolsa maior) menos lado de baixo

    def test_poisson_recupera_salto_em_log(self) -> None:
        r = self._linha(outcome_id="F1.1", populacao="V1", corte="0.300", especificacao="poisson_local")
        self.assertLess(abs(r["tau"] - 0.3), 4 * r["ep"])

    def test_especificacoes_por_corte_presentes(self) -> None:
        sub = self.est[(self.est["outcome_id"] == "F1.3") & (self.est["populacao"] == "V1")
                       & (self.est["corte"] == "0.300")]
        esp = set(sub["especificacao"])
        for e in ("principal", "sensibilidade_h", "ic_honesto", "ic_honesto_h_otimo", "local_randomization",
                  "ponderado_celulas", "nivel_celula", "S2_donut", "S3_porte_muda", "S3_porte_nao_muda",
                  "S3_diferenca"):
            self.assertIn(e, esp)
        self.assertEqual(int((sub["especificacao"] == "ic_honesto").sum()), 3)
        self.assertFalse(sub.loc[sub["especificacao"] == "ic_honesto_h_otimo", "no_protocolo"].any())
        self.assertTrue((sub.loc[sub["especificacao"] == "ic_honesto_h_otimo", "rotulo"]
                         .str.startswith("ESPECIFICACAO_ADICIONAL_AO_PROTOCOLO")).all())

    def test_s4_so_em_0400(self) -> None:
        s4 = self.est[self.est["especificacao"].str.startswith("S4")]
        self.assertTrue((s4["corte"] == "0.400").all())
        self.assertTrue((s4["status"] == "NAO_EXECUTADO").all())
        self.assertTrue((s4["nota"] == "insumo sintetico ausente").all())

    def test_sem_janela_lr_vira_nao_executado_com_motivo(self) -> None:
        r = self._linha(outcome_id="F1.3", populacao="V2", corte="0.300", especificacao="local_randomization")
        self.assertEqual(r["status"], "NAO_EXECUTADO")
        self.assertTrue(r["nota"])

    def test_principal_tem_ic_honesto_anexado(self) -> None:
        r = self._linha(outcome_id="F1.3", populacao="V1", corte="0.400", especificacao="principal")
        self.assertTrue(np.isfinite(r["ic_honesto_inf"]) and np.isfinite(r["M"]))
        self.assertLessEqual(r["ic_honesto_inf"], r["ic95_inf"] + 1e-12)

    def test_nan_sempre_com_nota(self) -> None:
        nucleo = ["tau", "ep", "ic95_inf", "ic95_sup", "p_valor"]
        ruins = self.est[self.est[nucleo].isna().any(axis=1) & (self.est["nota"].fillna("") == "")]
        self.assertEqual(len(ruins), 0)

    def test_bky_so_nas_linhas_marcadas(self) -> None:
        # q aguçado (BKY) pode ficar abaixo do p; só se exige q em (0, 1] e recálculo idêntico por família.
        q = self.est["q_bky"]
        self.assertTrue(q[~self.est["entra_bky"]].isna().all())
        m = self.est["entra_bky"]
        self.assertTrue(((q[m] > 0) & (q[m] <= 1)).all())
        for fam in E6.FAMILIAS_BKY:
            mf = m & (self.est["familia"] == fam)
            if mf.any():
                np.testing.assert_allclose(q[mf], E6.L.qvalores_bky(self.est.loc[mf, "p_valor"].to_numpy(dtype=float)))
        self.assertFalse(self.est.loc[self.est["familia"] == "P1", "entra_bky"].any())

    def test_indice_padronizado_pelo_lado_abaixo(self) -> None:
        d = self.extras["indice"]["dados_klk"]
        x = d["s_mil"] - d["corte_mil"]
        ref = (x > -50) & (x <= 0)
        # Com os quatro componentes presentes, a média do índice na referência é a média de z's de média zero.
        for _, sub in d[ref].groupby("grupo"):
            self.assertTrue((sub["n_componentes"] == 4).all())
            self.assertAlmostEqual(float(sub["indice"].mean()), 0.0, places=10)
        p1 = self._linha(outcome_id="P1", populacao="V1+V2", corte="empilhado", especificacao="principal")
        self.assertGreater(p1["tau"], 0)

    def test_natureza_empirico_so_como_rotulo_de_coluna(self) -> None:
        # O pipeline marca as linhas como EMPIRICO; dados sintéticos nunca são gravados (o teste não grava).
        self.assertTrue((self.est["natureza_dos_dados"] == "EMPIRICO").all())

    def test_tabelas_do_doc_geradas_e_aplicadas(self) -> None:
        resumo = {"validacoes": {"E3": {}, "E5": {}}, "contagens": {}, "p1_para_holm": {}}
        diag = pd.DataFrame(columns=["diagnostico", "especificacao", "populacao", "corte", "n_abaixo", "n_acima",
                                     "rho", "rho_ic95_inf", "rho_ic95_sup", "p_valor", "variavel", "tau"])
        tabs = E6.gerar_tabelas_doc(self.est, diag, resumo)
        texto = "a\n<!-- E6:indice_P1:inicio -->\nvelho\n<!-- E6:indice_P1:fim -->\nb"
        novo = E6.aplicar_tabelas_doc(texto, tabs)
        self.assertEqual(E6.tabelas_no_doc(novo)["indice_P1"], tabs["indice_P1"])


class TestFuncoesSinteticas(unittest.TestCase):
    """Funções auxiliares com entradas sintéticas mínimas."""

    def test_s_mil_rejeita_quatro_casas(self) -> None:
        with self.assertRaises(E6.FalhaValidacao):
            E6.s_mil_de_ivs(pd.Series([0.3001]))
        self.assertTrue(np.isnan(E6.s_mil_de_ivs(pd.Series([np.nan, 0.3])).iloc[0]))

    def test_diferenca_de_saltos(self) -> None:
        a = {"tau": 1.0, "ep": 0.3, "n_abaixo": 2, "n_acima": 3, "nota": ""}
        b = {"tau": 0.4, "ep": 0.4, "n_abaixo": 1, "n_acima": 1, "nota": ""}
        r = E6._rd_dif(a, b)
        self.assertAlmostEqual(r["tau"], 0.6)
        self.assertAlmostEqual(r["ep"], 0.5)

    def test_colunas_empilhadas_sem_duplicata(self) -> None:
        sp = E6._preparar_spec(next(c for c in E6.CATALOGO if c["col"] == "f0_3_vagas_pedidas"), 3)
        cols = E6._cols_spec(sp)
        self.assertEqual(len(cols), len(set(cols)))

    def test_arquivo_errado_de_ivs_nao_e_lido(self) -> None:
        fonte = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("ivs_ipea_2010_municipios", fonte)


# --------------------------------------------------------------------------
# Saídas reais
# --------------------------------------------------------------------------

@unittest.skipUnless(EST.exists() and RESUMO.exists() and DIAG.exists(), "saidas do E6 ausentes")
class TestSaidasReais(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.est = pd.read_csv(EST, dtype={"corte": str, "ciclo": str})
        cls.diag = pd.read_csv(DIAG, dtype={"corte": str})
        cls.resumo = json.loads(RESUMO.read_text(encoding="utf-8"))

    def _uma(self, **f) -> pd.Series:
        m = np.ones(len(self.est), dtype=bool)
        for k, v in f.items():
            if k == "h":
                m &= np.isclose(self.est["h"].astype(float), v)
            else:
                m &= self.est[k].astype(str) == str(v)
        sub = self.est[m]
        self.assertEqual(len(sub), 1, f)
        return sub.iloc[0]

    def test_natureza_empirico(self) -> None:
        self.assertTrue((self.est["natureza_dos_dados"] == "EMPIRICO").all())
        self.assertTrue((self.diag["natureza_dos_dados"] == "EMPIRICO").all())
        self.assertEqual(self.resumo["natureza_dos_dados"], "EMPIRICO")

    def test_todas_as_especificacoes_do_protocolo_presentes(self) -> None:
        faltam = []
        for spec in E6.CATALOGO:
            for k in spec["ciclos"]:
                col = E6._col(spec, k)
                pops = [spec["pop"]] if spec["pop"] != "V" else [f"V{k}"]
                for pop in pops:
                    base = (self.est["outcome"] == col) & (self.est["populacao"] == pop) & (
                        self.est["ciclo"] == E6._fmt_ciclo(k))
                    for corte in ("0.300", "0.400", "empilhado"):
                        sub = self.est[base & (self.est["corte"] == corte)]
                        esp = sub["especificacao"].value_counts().to_dict()
                        exig = {"principal": 1, "sensibilidade_h": 2, "ic_honesto": 3, "S2_donut": 1}
                        if corte != "empilhado":
                            exig |= {"ic_honesto_h_otimo": 3, "local_randomization": 1, "S3_porte_muda": 1,
                                     "S3_porte_nao_muda": 1, "S3_diferenca": 1}
                            if "poisson" in spec:
                                exig["poisson_local"] = 1
                            if "lee" in spec:
                                exig["limites_lee"] = 1
                            if corte == "0.400":
                                exig |= {"S4_dentro": 1, "S4_fora": 1, "S4_diferenca": 1}
                        if "peso" in spec:
                            exig["ponderado_celulas"] = 1
                        if "celula" in spec:
                            exig["nivel_celula"] = 1
                        for e, n in exig.items():
                            if esp.get(e, 0) != n:
                                faltam.append((col, pop, corte, e, esp.get(e, 0)))
            if spec["pop"] == "V" and len(spec["ciclos"]) >= 2:
                pop = "+".join(f"V{k}" for k in spec["ciclos"])
                for corte in ("0.300", "0.400", "empilhado"):
                    sub = self.est[(self.est["outcome"] == spec["col"]) & (self.est["populacao"] == pop)
                                   & (self.est["corte"] == corte)]
                    for e, n in {"principal": 1, "sensibilidade_h": 2, "ic_honesto": 3, "S2_donut": 1}.items():
                        if int((sub["especificacao"] == e).sum()) != n:
                            faltam.append((spec["col"], pop, corte, e))
        self.assertEqual(faltam, [])
        p1 = self._uma(outcome_id="P1", populacao="V1+V2+V3", corte="empilhado", especificacao="principal")
        self.assertTrue(bool(p1["no_protocolo"]))

    def test_nan_sempre_com_nota(self) -> None:
        nucleo = ["tau", "ep", "ic95_inf", "ic95_sup", "p_valor"]
        ruins = self.est[self.est[nucleo].isna().any(axis=1) & (self.est["nota"].fillna("") == "")]
        self.assertEqual(len(ruins), 0)
        self.assertTrue((self.est.loc[self.est["status"] == "NAO_EXECUTADO", "nota"].fillna("") != "").all())

    def test_reproduz_E3_exatamente(self) -> None:
        e3 = pd.read_csv(OUT / "E3_estimativas.csv")
        mapa = {"fracao_celulas_ch1_com_confirmacao_ou_homologacao": "F1.3",
                "D_k_especialista_ativo_do_ciclo": "F2.3"}
        for r in e3.to_dict("records"):
            pop = "V1" if r["populacao"] == "P1" else "V2"
            esp = "principal" if r["especificacao"] == "principal" else "sensibilidade_h"
            x = self._uma(outcome_id=mapa[r["outcome"]], populacao=pop, ciclo=pop[1], corte=f"{r['corte']:.3f}",
                          especificacao=esp, h=r["h"])
            for c in ("tau", "ep", "ic95_inf", "ic95_sup", "p_valor"):
                self.assertEqual(float(x[c]), float(r[c]), (r["outcome"], r["populacao"], r["corte"], r["h"], c))
            self.assertEqual(int(x["n_abaixo"]), int(r["n_abaixo"]))
            self.assertEqual(int(x["n_acima"]), int(r["n_acima"]))

    def _rederivar(self, y: np.ndarray, s: np.ndarray, corte: int, h: int = 50) -> float:
        """Salto independente: reta ponderada de cada lado; acima - abaixo no corte (numpy puro)."""
        x = s - corte
        w = np.clip(1 - np.abs(x) / h, 0, None)
        ok = (np.abs(x) < h) & np.isfinite(y) & (w > 0)
        ints = {}
        for lado, m in (("abaixo", ok & (x <= 0)), ("acima", ok & (x > 0))):
            X = np.column_stack([np.ones(m.sum()), x[m] / 1000])
            W = w[m]
            b = np.linalg.solve(X.T @ (X * W[:, None]), X.T @ (W * y[m]))
            ints[lado] = b[0]
        return ints["acima"] - ints["abaixo"]

    def test_sinal_rederivado_em_tres_linhas(self) -> None:
        a08 = pd.read_csv(ROOT / "output" / "aquisicao" / "a08_ivs_2010_oficial_municipio.csv", dtype={"co_ibge": str})
        smap = a08.set_index(a08["co_ibge"].str.zfill(6))["ivs"].mul(1000).round()
        u = pd.read_parquet(OUT / "outcomes" / "outcomes_U_municipio.parquet")
        vm = pd.read_parquet(OUT / "outcomes" / "outcomes_V_municipio.parquet")
        casos = [
            (u, "f0_1_tem_celula_c3", "U", "3", 300),
            (vm[vm["ciclo"] == 2], "f1_3_fracao_celulas_preenchidas_ch1", "V2", "2", 400),
            (vm[vm["ciclo"] == 1], "f2_1_ativos_por_celula", "V1", "1", 300),
        ]
        for df, col, pop, ciclo, corte in casos:
            s = df["co_ibge"].map(smap).to_numpy(dtype=float)
            ok = np.isfinite(s)
            tau = self._rederivar(df[col].to_numpy(dtype=float)[ok], s[ok], corte)
            x = self._uma(outcome=col, populacao=pop, ciclo=ciclo, corte=f"{corte / 1000:.3f}", especificacao="principal")
            self.assertAlmostEqual(float(x["tau"]), tau, places=10, msg=(col, pop, corte))

    def test_q_bky_recalculado(self) -> None:
        for fam in E6.FAMILIAS_BKY:
            m = (self.est["familia"] == fam) & self.est["entra_bky"]
            q = E6.L.qvalores_bky(self.est.loc[m, "p_valor"].to_numpy(dtype=float))
            np.testing.assert_allclose(self.est.loc[m, "q_bky"].to_numpy(dtype=float), q)
        self.assertTrue(self.est.loc[~self.est["entra_bky"], "q_bky"].isna().all())

    def test_hashes_das_entradas_conferem(self) -> None:
        for e in self.resumo["entradas"]:
            self.assertEqual(sha256(ROOT / e["caminho"]), e["sha256"], e["caminho"])
        self.assertEqual(self.resumo["protocolo"]["sha256"], sha256(ROOT / self.resumo["protocolo"]["arquivo"]))
        for nome, info in self.resumo["saidas"].items():
            if nome == "figuras":
                for f in info:
                    self.assertTrue((ROOT / f).exists(), f)
            else:
                self.assertEqual(sha256(ROOT / info["arquivo"]), info["sha256"], nome)

    def test_desvios_com_data_e_motivo(self) -> None:
        for d in self.resumo["desvios"]:
            self.assertTrue(d.get("data") and d.get("situacao") and d.get("resolucao"), d)

    def test_p1_do_resumo_igual_ao_csv(self) -> None:
        p1 = self._uma(outcome_id="P1", populacao="V1+V2+V3", corte="empilhado", especificacao="principal")
        # O CSV é gravado com a precisão padrão do pandas (a mesma do E3); o JSON guarda o float completo.
        for k in ("tau", "ep", "p_valor"):
            self.assertAlmostEqual(float(p1[k]), self.resumo["p1_para_holm"][k], delta=1e-15 * max(1.0, abs(float(p1[k]))))


@unittest.skipUnless(DOC.exists() and EST.exists(), "doc 41 ou saidas do E6 ausentes")
class TestDoc41(unittest.TestCase):
    """O doc 41 não tem número de resultado digitado: tabelas = geradas das saídas; prosa só com parâmetros."""

    def test_tabelas_do_doc_iguais_as_geradas_das_saidas(self) -> None:
        est, diag, resumo = E6.ler_saidas()
        geradas = E6.gerar_tabelas_doc(est, diag, resumo)
        no_doc = E6.tabelas_no_doc(DOC.read_text(encoding="utf-8"))
        self.assertTrue(no_doc)
        for nome, corpo in no_doc.items():
            self.assertEqual(corpo, geradas[nome], nome)

    def test_prosa_sem_numero_de_resultado(self) -> None:
        texto = E6.MARCA.sub("", DOC.read_text(encoding="utf-8"))
        texto = re.sub(r"`[^`]*`", "", texto)                       # nomes de arquivo e coluna
        texto = re.sub(r"\]\([^)]*\)", "]", texto)                   # links
        texto = re.sub(r"(?m)^#+ .*$", "", texto)                      # títulos numerados das seções
        texto = re.sub(r"§+\s?\d+(?:[.,]\d+)*", "", texto)             # referências a seções
        decimais = set(re.findall(r"(?<![\w.,])[−+-]?\d+[,.]\d+", texto))
        # Só parâmetros do protocolo e referências de magnitude da literatura (protocolo §§1, 3, 6, 7).
        permitidos = {"0,300", "0,400", "0,050", "0,030", "0,080", "0,5", "0,005", "0,001", "0,05", "0,3", "0,4",
                      "3.493", "12.871", "15.233", "1,96"}
        self.assertEqual(decimais - permitidos, set())


if __name__ == "__main__":
    unittest.main()
