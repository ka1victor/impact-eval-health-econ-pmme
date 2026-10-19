"""Testes do X4 e do X5 (`scripts/rdd_bolsa/19_escolha_heterogeneidade.py`, protocolo exploratório 45).

Duas partes:
1. `TestX4X5Sintetico*`: dados SINTÉTICOS, gerados em memória com semente fixa e nunca gravados. Células,
   regiões, pontuações e escolhas são fictícias, com coeficientes conhecidos por construção. Verificam que a
   interação da bolsa com um grupo de candidato (conjuntos replicados) e com um grupo de célula é recuperada,
   que a replicação sem interação não muda a verossimilhança, que o efeito de vizinhança é recuperado, que o
   logit aninhado recupera lambda e a bolsa e coincide com o condicional quando lambda = 1, e a regra dos tercis.
2. `TestX4X5SaidasEmpiricas`: invariantes das saídas EMPÍRICAS em `output/rdd_bolsa/`: rótulos, todas as
   dimensões e especificações presentes, família BKY, reprodução do E9, hashes de entrada e saída, tabelas
   regeneradas dos CSVs, blocos do doc 46 iguais aos gerados e nenhum número digitado fora deles. Os alvos
   vêm de arquivos de `output/`, nunca digitados.
"""

from __future__ import annotations

import importlib.util
import json
import math
import re
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "19_escolha_heterogeneidade.py"
SPEC = importlib.util.spec_from_file_location("x4x5_escolha_teste", SCRIPT)
X = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(X)
E9 = X.E9

SEMENTE = 20261019
DOC = ROOT / "docs" / "06_execucao" / "46_resultados_exploratorios_pos_sintese.md"


# --------------------------------------------------------------------------
# Gerador sintético (só em memória)
# --------------------------------------------------------------------------

def celulas_sinteticas(rng: np.random.Generator, n_conj: int = 16, n_cel: int = 40, n_reg: int = 8) -> pd.DataFrame:
    """Células SINTÉTICAS no formato do conjunto de escolha (só em memória)."""
    linhas = []
    for c in range(n_conj):
        for j in range(n_cel):
            s = float(rng.integers(150, 651))
            vagas = float(rng.integers(0, 3))
            linhas.append({"ciclo": 9, "id_conjunto_escolha": f"sint_c{c:02d}", "cod_curso": c,
                           "co_cnes_7d": f"S{c:02d}{j:04d}", "s_mil": s,
                           "bolsa_mil": 20.0 if s > 400 else (15.0 if s > 300 else 10.0),
                           "faixa_anunciada": "FAIXA 1" if s > 400 else ("FAIXA 2" if s > 300 else "FAIXA 3"),
                           "tem_vaga_imediata": int(vagas > 0), "vagas_imediatas": vagas,
                           "log_vagas_imediatas_mais_1": math.log(vagas + 1.0),
                           "populacao_2022": float(np.exp(rng.normal(10.5, 1.0))),
                           "macrorregiao": rng.choice(["NORTE", "SUDESTE"]),
                           "estrato_territorial": rng.choice(["capital", "interior_remoto"]),
                           "co_cir": f"R{c:02d}{int(rng.integers(0, n_reg)):02d}"})
    return pd.DataFrame(linhas)


def utilidade_base(conj: pd.DataFrame) -> np.ndarray:
    sp = E9.base_spline(conj["s_mil"].to_numpy(), 1)
    v = (-0.30 * sp["ivs_inclinacao"] + 0.20 * sp["ivs_mudanca_inclinacao_0300"]
         - 0.25 * sp["ivs_mudanca_inclinacao_0400"]).to_numpy()
    return v + 0.4 * conj["tem_vaga_imediata"].to_numpy() + 0.1 * np.log(conj["populacao_2022"].to_numpy())


def escolher(rng: np.random.Generator, conj: pd.DataFrame, v_por_cand, n_cand: int) -> pd.DataFrame:
    """Escolhas SINTÉTICAS: candidato i escolhe a célula de maior v + Gumbel no seu conjunto."""
    _, conj_cel = np.unique(conj["id_conjunto_escolha"], return_inverse=True)
    idx_por = {s: np.flatnonzero(conj_cel == s) for s in np.unique(conj_cel)}
    n_s = len(idx_por)
    esc, cl = [], []
    for i in range(n_cand):
        s = i % n_s
        idx = idx_por[s]
        v = v_por_cand(i)[idx]
        esc.append(int(idx[np.argmax(v + rng.gumbel(size=len(idx)))]))
        cl.append(s)
    return pd.DataFrame({"idx_escolhida": esc, "idx_excluida": -1, "cluster_conjunto": [f"k{s:02d}" for s in cl],
                         "cluster_curso": [f"curso{s:02d}" for s in cl],
                         "cluster_candidato": [f"sint_{i:05d}" for i in range(n_cand)], "posto": 1})


def matriz(conj: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray]:
    _, conj_cel = np.unique(conj["id_conjunto_escolha"], return_inverse=True)
    Xm = E9.matriz_atributos(conj, 1, "linear", sorted(conj["macrorregiao"].unique()),
                             sorted(conj["estrato_territorial"].unique()))
    return Xm, conj_cel


class TestX4SinteticoInteracaoCandidato(unittest.TestCase):
    """Dados sintéticos: a bolsa tem inclinação diferente por grupo de candidato; os conjuntos replicados
    recuperam a diferença, e sem interação a replicação não muda a verossimilhança."""

    @classmethod
    def setUpClass(cls) -> None:
        rng = np.random.default_rng(SEMENTE)
        cls.conj = celulas_sinteticas(rng)
        base = utilidade_base(cls.conj)
        bolsa = cls.conj["bolsa_mil"].to_numpy()
        n = 9000
        cls.grupo = np.where(np.arange(n) % 3 == 0, "alto", "baixo")
        cls.beta = {"baixo": 0.05, "alto": 0.20}
        cls.grupos = escolher(rng, cls.conj, lambda i: base + cls.beta[cls.grupo[i]] * bolsa, n)
        cls.Xm, cls.conj_cel = matriz(cls.conj)

    def test_recupera_interacao(self) -> None:
        Xe, ce, ge, rot = X.expandir_por_grupo_de_candidato(self.Xm, self.conj_cel, self.grupos, self.grupo)
        Xe["bolsa_x_alto"] = Xe["bolsa_mil"].to_numpy() * (rot == "alto")
        r = X.ajustar(Xe, ce, ge)
        self.assertTrue(r["ok"], r["nota"])
        kb, ki = r["termos"].index("bolsa_mil"), r["termos"].index("bolsa_x_alto")
        alvo = self.beta["alto"] - self.beta["baixo"]
        self.assertLess(abs(r["theta"][ki] - alvo), 3 * math.sqrt(r["V_mle"][ki, ki]))
        self.assertLess(abs(r["theta"][kb] - self.beta["baixo"]), 3 * math.sqrt(r["V_mle"][kb, kb]))
        w = X.wald(r, np.eye(len(r["termos"]))[[ki]])
        self.assertLess(w["p_mle"], 0.01)

    def test_replicacao_sem_interacao_igual_ao_e9(self) -> None:
        r0 = X.ajustar(self.Xm, self.conj_cel, self.grupos)
        Xe, ce, ge, _ = X.expandir_por_grupo_de_candidato(self.Xm, self.conj_cel, self.grupos, self.grupo)
        r1 = X.ajustar(Xe, ce, ge)
        self.assertAlmostEqual(r0["ll"], r1["ll"], places=8)
        np.testing.assert_allclose(r0["theta"], r1["theta"], rtol=1e-7, atol=1e-9)
        np.testing.assert_allclose(r0["V_conj"], r1["V_conj"], rtol=1e-6, atol=1e-12)


class TestX4SinteticoInteracaoCelula(unittest.TestCase):
    """Dados sintéticos: inclinação da bolsa diferente por estrato da célula (sem diferença: Wald não rejeita
    com frequência; com diferença: recupera)."""

    def test_recupera_interacao_de_celula(self) -> None:
        rng = np.random.default_rng(SEMENTE + 1)
        conj = celulas_sinteticas(rng)
        bolsa = conj["bolsa_mil"].to_numpy()
        remoto = (conj["estrato_territorial"] == "interior_remoto").to_numpy()
        v = utilidade_base(conj) + 0.08 * bolsa + 0.12 * bolsa * remoto - 0.5 * remoto
        grupos = escolher(rng, conj, lambda i: v, 9000)
        Xm, cc = matriz(conj)
        Xm["bolsa_x_interior_remoto"] = bolsa * remoto
        r = X.ajustar(Xm, cc, grupos)
        k = r["termos"].index("bolsa_x_interior_remoto")
        self.assertLess(abs(r["theta"][k] - 0.12), 3 * math.sqrt(r["V_mle"][k, k]))
        sb = X.score_bootstrap(r, k, "cluster_conjunto")
        self.assertEqual(sb["g"], 16)
        self.assertLess(sb["rademacher"], 0.05)


class TestX4SinteticoTercis(unittest.TestCase):
    """Regra dos tercis em valores sintéticos: empate no corte vai para baixo."""

    def test_empate_vai_para_baixo(self) -> None:
        x = pd.Series([1.0, 2.0, 2.0, 2.0, 3.0, 4.0])
        t, (q1, q2) = X.tercis(x)
        self.assertTrue((t[x <= q1] == 1).all())
        self.assertTrue((t[(x > q1) & (x <= q2)] == 2).all())
        self.assertTrue((t[x > q2] == 3).all())
        self.assertEqual(int(t[x == 2.0].nunique()), 1)


class TestX5SinteticoVizinhanca(unittest.TestCase):
    """Dados sintéticos: a utilidade cai com o número de vizinhos de bolsa maior; o termo é recuperado."""

    def test_atributos_de_vizinhanca(self) -> None:
        conj = pd.DataFrame({"id_conjunto_escolha": ["a"] * 4 + ["b"] * 2, "co_cir": ["r1", "r1", "r1", "r2", "r1", "r1"],
                             "bolsa_mil": [10.0, 15.0, 20.0, 20.0, 10.0, 10.0]})
        v = X.atributos_vizinhanca(conj)
        self.assertEqual(v["n_vizinhos_bolsa_maior"].tolist(), [2.0, 1.0, 0.0, 0.0, 0.0, 0.0])
        self.assertEqual(v["n_outras_celulas_regiao"].tolist(), [2.0, 2.0, 2.0, 0.0, 1.0, 1.0])
        self.assertEqual(v["tem_vizinho_regiao"].tolist(), [1.0, 1.0, 1.0, 0.0, 1.0, 1.0])
        self.assertEqual(v["fracao_vizinhos_bolsa_maior"].tolist(), [1.0, 0.5, 0.0, 0.0, 0.0, 0.0])

    def test_recupera_efeito_de_vizinhanca(self) -> None:
        rng = np.random.default_rng(SEMENTE + 2)
        conj = celulas_sinteticas(rng, n_reg=6)
        viz = X.atributos_vizinhanca(conj)
        gama = -0.25
        v = utilidade_base(conj) + 0.08 * conj["bolsa_mil"].to_numpy() + gama * viz["n_vizinhos_bolsa_maior"].to_numpy()
        grupos = escolher(rng, conj, lambda i: v, 10000)
        Xm, cc = matriz(conj)
        for c in ("n_vizinhos_bolsa_maior", "n_outras_celulas_regiao"):
            Xm[c] = viz[c].to_numpy()
        r = X.ajustar(Xm, cc, grupos)
        k = r["termos"].index("n_vizinhos_bolsa_maior")
        self.assertLess(abs(r["theta"][k] - gama), 3 * math.sqrt(r["V_mle"][k, k]))
        self.assertLess(r["theta"][k], 0)


class TestX5SinteticoAninhado(unittest.TestCase):
    """Dados sintéticos do logit aninhado (escolhas sorteadas das probabilidades do modelo, lambda conhecido)."""

    @classmethod
    def setUpClass(cls) -> None:
        rng = np.random.default_rng(SEMENTE + 3)
        cls.conj = celulas_sinteticas(rng, n_conj=12, n_cel=40, n_reg=6)
        cls.Xm, cls.cc = matriz(cls.conj)
        cls.lam, cls.beta = 0.5, 0.10
        v = utilidade_base(cls.conj) + cls.beta * cls.conj["bolsa_mil"].to_numpy()
        ninho = pd.factorize(cls.conj["co_cir"])[0]
        a = v / cls.lam
        P = np.zeros(len(v))
        for s in np.unique(cls.cc):
            m = cls.cc == s
            nn = ninho[m]
            iv = {k: np.log(np.exp(a[m][nn == k]).sum()) for k in np.unique(nn)}
            den = sum(np.exp(cls.lam * x) for x in iv.values())
            P[m] = np.exp(a[m]) / np.exp(np.array([iv[k] for k in nn])) * \
                np.exp(cls.lam * np.array([iv[k] for k in nn])) / den
        cls.P = P
        n = 9000
        esc, cl = [], []
        idx_por = {s: np.flatnonzero(cls.cc == s) for s in np.unique(cls.cc)}
        for i in range(n):
            s = i % len(idx_por)
            idx = idx_por[s]
            esc.append(int(rng.choice(idx, p=P[idx] / P[idx].sum())))
            cl.append(s)
        cls.grupos = pd.DataFrame({"idx_escolhida": esc, "idx_excluida": -1,
                                   "cluster_conjunto": [f"k{s:02d}" for s in cl],
                                   "cluster_curso": [f"curso{s:02d}" for s in cl],
                                   "cluster_candidato": [f"sint_{i:05d}" for i in range(n)], "posto": 1})
        cls.ninho = ninho

    def test_probabilidades_somam_um(self) -> None:
        for s in np.unique(self.cc):
            self.assertAlmostEqual(float(self.P[self.cc == s].sum()), 1.0, places=10)

    def test_recupera_lambda_e_bolsa(self) -> None:
        r = X.ajustar(self.Xm, self.cc, self.grupos)
        nl = X.estimar_aninhado(r, self.ninho[r["_usadas"]])
        self.assertTrue(nl["convergiu"])
        kl, kb = nl["termos"].index("lambda"), nl["termos"].index("bolsa_mil")
        self.assertLess(abs(nl["theta"][kl] - self.lam), 3 * math.sqrt(nl["V_mle"][kl, kl]))
        self.assertLess(abs(nl["theta"][kb] - self.beta), 3 * math.sqrt(nl["V_mle"][kb, kb]))
        self.assertGreater(nl["ll"], r["ll"])

    def test_lambda_1_igual_ao_condicional(self) -> None:
        r = X.ajustar(self.Xm, self.cc, self.grupos)
        _, ninho = np.unique(np.column_stack([r["_conj"], self.ninho[r["_usadas"]]]), axis=0, return_inverse=True)
        ninho = ninho.ravel()
        nc = np.zeros(int(ninho.max()) + 1, dtype=int)
        nc[ninho] = r["_conj"]
        lp = X._logp_aninhado(np.concatenate([r["theta"], [1.0]]), r["_X"], r["_conj"], ninho, nc, r["_esc"])
        self.assertAlmostEqual(float(lp.sum()), r["ll"], places=6)


# --------------------------------------------------------------------------
# Saídas empíricas
# --------------------------------------------------------------------------

class TestX4X5SaidasEmpiricas(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.x4 = pd.read_csv(X.OUT_X4, dtype={"ciclo": str})
        cls.x5 = pd.read_csv(X.OUT_X5, dtype={"ciclo": str})
        cls.resumo = json.loads(X.OUT_RESUMO.read_text(encoding="utf-8"))

    def test_rotulos(self) -> None:
        for df in (self.x4, self.x5):
            self.assertTrue((df["natureza_dos_dados"] == "EMPIRICO").all())
            self.assertTrue((df["estatuto"] == "EXPLORATORIO_POS_SINTESE").all())
        self.assertEqual(self.resumo["natureza_dos_dados"], "EMPIRICO")
        self.assertEqual(self.resumo["estatuto"], "EXPLORATORIO_POS_SINTESE")

    def test_dimensoes_e_ciclos_completos(self) -> None:
        for dim in X.DIMENSOES:
            for ciclo in X.CICLOS:
                sel = self.x4[(self.x4.dimensao == dim) & (self.x4.ciclo == ciclo)]
                self.assertEqual(int((sel.tipo_linha == "wald_igualdade").sum()), 1, (dim, ciclo))
                n_g = int((sel.tipo_linha == "inclinacao_do_grupo").sum())
                self.assertEqual(int((sel.tipo_linha == "interacao").sum()), n_g - 1, (dim, ciclo))
                self.assertTrue(sel.loc[sel.tipo_linha != "wald_igualdade", "coef"].notna().all())
        for ciclo in X.CICLOS:
            sel = self.x5[self.x5.ciclo == ciclo]
            self.assertEqual(set(sel.especificacao), set(X.ESPEC_X5) | {"aninhado_cir"})
            self.assertEqual(int((sel.tipo_linha == "bolsa").sum()), len(X.ESPEC_X5) + 1)
            self.assertEqual(int((sel.tipo_linha == "vizinhanca").sum()), len(X.TERMO_TESTE_X5))
            self.assertEqual(int((sel.tipo_linha == "teste_lambda_igual_1").sum()), 1)

    def test_inclinacao_igual_base_mais_interacao(self) -> None:
        for (dim, ciclo), sel in self.x4[~self.x4.adicao_pos_auditoria.astype(bool)].groupby(["dimensao", "ciclo"]):
            inc = sel[sel.tipo_linha == "inclinacao_do_grupo"].set_index("grupo")["coef"]
            base = sel["grupo_base"].iloc[0]
            for r in sel[sel.tipo_linha == "interacao"].itertuples():
                self.assertAlmostEqual(inc[r.grupo], inc[base] + r.coef, places=8)
            for r in sel[sel.tipo_linha == "inclinacao_do_grupo"].itertuples():
                self.assertAlmostEqual(r.rc_por_5mil, math.exp(5 * r.coef), places=8)

    def test_familia_bky(self) -> None:
        for df, nome in ((self.x4, "x4"), (self.x5, "x5")):
            fam = df[df.entra_bky.astype(bool)]
            self.assertTrue(fam["q_bky"].notna().all())
            self.assertTrue(df.loc[~df.entra_bky.astype(bool), "q_bky"].isna().all())
            np.testing.assert_allclose(fam["q_bky"], X.L.qvalores_bky(fam["p"].to_numpy()), atol=1e-12)
            self.assertEqual(len(fam), self.resumo[nome]["familia_bky"]["linhas"])
            self.assertTrue(((fam["q_bky"] > 0) & (fam["q_bky"] <= 1)).all())
        curso = self.x4[self.x4.dimensao == "curso"]
        self.assertTrue(curso["inferencia_cluster_degenerada"].astype(bool).all())
        self.assertFalse(curso["entra_bky"].astype(bool).any())
        # termo próprio de curso: G efetivo por ciclo = 1 (o curso é o conjunto)
        inter = curso[(curso.tipo_linha == "interacao") & (curso.ciclo != "empilhado") &
                      (curso.grupo != "demais_cursos")]
        self.assertTrue((inter["g_efetivo_conjunto"] == 1).all())

    def test_reproducao_do_e9(self) -> None:
        e9 = pd.read_csv(X.E9_ESTIMATIVAS, dtype={"ciclo": str})
        rep = self.resumo["conferencias"]["reproducao_principal_E9"]
        for ciclo in X.CICLOS:
            alvo = e9[(e9.ciclo == ciclo) & (e9.modelo == E9.MODELO_COND) & (e9.conjunto == "principal") &
                      (e9.especificacao == E9.ESPEC_PRINCIPAL) & (e9.termo == "bolsa_mil")].iloc[0]
            self.assertTrue(rep[ciclo]["igual"])
            self.assertTrue(rep[ciclo]["expansao_por_grupo_de_candidato_igual"])
            self.assertAlmostEqual(rep[ciclo]["coef"], alvo.coef, places=8)

    def test_x5_sem_vizinhanca_e_amostra(self) -> None:
        """A linha sem vizinhança é o principal do E9 na amostra do X5; só sai o que não tem CIR oficial."""
        ret = self.resumo["x5"]["retirados"]
        e9 = pd.read_csv(X.E9_ESTIMATIVAS, dtype={"ciclo": str})
        for ciclo in ("1", "2", "3"):
            alvo = e9[(e9.ciclo == ciclo) & (e9.modelo == E9.MODELO_COND) & (e9.conjunto == "principal") &
                      (e9.especificacao == E9.ESPEC_PRINCIPAL) & (e9.termo == "bolsa_mil")].iloc[0]
            linha = self.x5[(self.x5.ciclo == ciclo) & (self.x5.especificacao == "sem_vizinhanca") &
                            (self.x5.termo == "bolsa_mil")].iloc[0]
            self.assertEqual(int(linha.n_candidatos) + ret["candidatos_de_1a_opcao_retirados_por_ciclo"].get(ciclo, 0),
                             int(alvo.n_candidatos))
            self.assertEqual(int(linha.n_alternativas) + ret["celulas_retiradas_por_ciclo"].get(ciclo, 0),
                             int(alvo.n_alternativas))
        # "um município do quadro não está na tabela do TabNet"
        self.assertEqual(len(ret["municipios_sem_cir_oficial"]), 1)
        conf = self.resumo["conferencias"]["cir_contra_malha"]
        self.assertEqual(conf["regioes_da_malha_em_mais_de_uma_cir"], {})
        self.assertEqual(conf["cir_com_mais_de_uma_regiao_da_malha"], 0)
        for d in self.resumo["x5"]["por_ciclo"].values():
            self.assertTrue(d["aninhado"]["convergiu"])

    def test_hashes(self) -> None:
        for e in self.resumo["entradas"]:
            self.assertEqual(E9.sha256_arquivo(ROOT / e["caminho"]), e["sha256"], e["caminho"])
        for caminho, sha in self.resumo["saidas"].items():
            self.assertEqual(E9.sha256_arquivo(ROOT / caminho), sha, caminho)
        man = json.loads(X.OUT_MANIFESTO_CIR.read_text(encoding="utf-8"))
        self.assertEqual(E9.sha256_arquivo(X.CIR_BRUTO), man["sha256"])
        self.assertNotIn("ivs_ipea_2010_municipios", json.dumps(self.resumo["entradas"]))

    def test_tabelas_regeneradas_dos_csv(self) -> None:
        res = {"x5_por_ciclo": self.resumo["x5"]["por_ciclo"], "x4_por_modelo": self.resumo["x4"]["por_modelo"],
               "x5_retirados": self.resumo["x5"]["retirados"], "cursos_sem_ponte": self.resumo["x4"]["cursos_sem_ponte"]}
        texto = X.tabelas_relato(pd.read_csv(X.OUT_X4), pd.read_csv(X.OUT_X5), res)
        self.assertEqual(texto, X.OUT_TABELAS.read_text(encoding="utf-8"))

    # ---------------------------------------------------------------- doc 46

    def _secao(self, chave: str) -> str:
        doc = DOC.read_text(encoding="utf-8")
        ini = doc.index(f"\n## {chave}")
        prox = doc.find("\n## ", ini + 1)
        return doc[ini:prox if prox >= 0 else len(doc)]

    def test_doc_46_tem_os_blocos_do_script(self) -> None:
        gerado = X.OUT_TABELAS.read_text(encoding="utf-8")
        for chave in ("X4", "X5"):
            self.assertIn(X.bloco_do_texto(gerado, chave), self._secao(chave))
        # linhas de curso das Tabelas X4.1 e X4.2 trazem a inferência de MV, marcada (cluster degenerado)
        linhas_curso = [ln for ln in X.bloco_do_texto(gerado, "X4").splitlines() if ln.startswith("| curso |")]
        self.assertTrue(linhas_curso)
        self.assertTrue(all(ln.rstrip().endswith("| MV (cluster degenerado) |") for ln in linhas_curso))

    def test_doc_46_sem_numero_digitado_fora_dos_blocos(self) -> None:
        """Fora dos blocos gerados, só números do protocolo (cortes, meses, limiares, mínimo de candidatos),
        de seções, tabelas, docs, auditorias e datas."""
        gerado = X.OUT_TABELAS.read_text(encoding="utf-8")
        for chave in ("X4", "X5"):
            sec = self._secao(chave)
            bloco = X.bloco_do_texto(gerado, chave)
            fora = sec.replace(bloco, " ")
            limpo = re.sub(r"`[^`]*`", " ", fora)
            limpo = re.sub(r"\]\([^)]*\)", "]", limpo)
            for padrao in (r"\d{2}/\d{2}/\d{4}", r"§\s?\d+(\.\d+)?", r"[Tt]abelas? X\d\.\d( (a|e) X\d\.\d)?",
                           r"[Aa]uditorias? \d+", r"doc \d+\w?", r"protocolo \d+", r"^#+ .*$", r"\bX\d\b",
                           r"\b[A-Z]\d+\b", r"IC 95%", r"G − 1", r"G ≤ 24", r"SHA-256", r"\d+ª", r"1/3", r"2/3",
                           r"\(a\)|\(b\)|\(c\)|\(d\)|\(i\)|\(ii\)"):
                limpo = re.sub(padrao, " ", limpo, flags=re.MULTILINE)
            permitidos = {"0,300", "0,400", "0,05", "0", "1", "2", "3", "5", "10", "100", "202406", "202506",
                          "2010", "2022"}
            for n in re.findall(r"−?\d+(?:,\d+)?", limpo):
                self.assertIn(n, permitidos, f"número fora dos blocos gerados na seção {chave}: {n}")

    def test_doc_46_afirmacoes_qualitativas(self) -> None:
        """Frases das seções X4 e X5 do doc 46, conferidas contra os CSVs."""
        x4, x5 = self.x4, self.x5
        fam = x4[x4.entra_bky.astype(bool)]
        # "estrato: no ciclo 3 e no empilhado o Wald rejeita a igualdade com q < 0,05; a capital responde menos"
        w = fam[(fam.dimensao == "estrato") & (fam.tipo_linha == "wald_igualdade")].set_index("ciclo")
        for c in ("3", "empilhado"):
            self.assertLess(w.loc[c, "q_bky"], 0.05)
        for c in ("1", "2"):
            self.assertGreater(w.loc[c, "q_bky"], 0.05)
        inter = x4[(x4.dimensao == "estrato") & (x4.tipo_linha == "interacao") & (x4.ciclo == "empilhado")]
        self.assertTrue((inter["coef"] > 0).all())
        inc = x4[(x4.dimensao == "estrato") & (x4.tipo_linha == "inclinacao_do_grupo") & (x4.ciclo == "empilhado")]
        cap = inc[inc.grupo == "capital"].iloc[0]
        self.assertTrue(cap.ic95_inf < 0 < cap.ic95_sup)
        # "nota: nenhum tercil difere do tercil 1 com q < 0,05 em nenhum ciclo; o grupo sem pontuação (ciclo 1) sim
        # no empilhado"
        nt = fam[(fam.dimensao == "nota_tercil") & (fam.tipo_linha == "interacao")]
        self.assertTrue((nt[nt.grupo.isin(["tercil2", "tercil3"])]["q_bky"] > 0.05).all())
        sp = nt[(nt.grupo == "sem_pontuacao") & (nt.ciclo == "empilhado")].iloc[0]
        self.assertLess(sp.q_bky, 0.05)
        # "... mas dentro do ciclo 1, o único em que o grupo existe, a diferença não tem q < 0,05"
        sp1 = nt[(nt.grupo == "sem_pontuacao") & (nt.ciclo == "1")].iloc[0]
        self.assertGreater(sp1.q_bky, 0.05)
        wn = fam[(fam.dimensao == "nota_tercil") & (fam.tipo_linha == "wald_igualdade")].set_index("ciclo")
        for c in ("1", "2", "3"):
            self.assertGreater(wn.loc[c, "q_bky"], 0.05)
        # "escassez: entre os tercis, nenhuma interação com q < 0,05; o Wald só rejeita no ciclo 1, com o tercil do
        # meio abaixo dos outros dois (não monotônico); o grupo sem ponte (cursos 17 a 24) responde menos no ciclo 3"
        es = fam[(fam.dimensao == "escassez_tercil") & (fam.tipo_linha == "interacao")]
        self.assertTrue((es[es.grupo.isin(["tercil2", "tercil3"])]["q_bky"] > 0.05).all())
        we = fam[(fam.dimensao == "escassez_tercil") & (fam.tipo_linha == "wald_igualdade")].set_index("ciclo")
        self.assertLess(we.loc["1", "q_bky"], 0.05)
        for c in ("2", "3", "empilhado"):
            self.assertGreater(we.loc[c, "q_bky"], 0.05)
        e1 = x4[(x4.dimensao == "escassez_tercil") & (x4.ciclo == "1") &
                (x4.tipo_linha == "inclinacao_do_grupo")].set_index("grupo")["coef"]
        self.assertLess(e1["tercil2"], min(e1["tercil1"], e1["tercil3"]))
        self.assertTrue((es[es.grupo == "sem_ponte_curso_cbo"]["coef"] < 0).all())
        self.assertTrue((es[es.grupo == "sem_ponte_curso_cbo"]["q_bky"] < 0.05).all())
        # "o curso de menor inclinação no ciclo 3 é um dos cursos sem ponte, e a inclinação dele é negativa também
        # pelo EP de MV"
        c3 = x4[(x4.dimensao == "curso") & (x4.ciclo == "3") &
                (x4.tipo_linha == "inclinacao_do_grupo")].sort_values("coef").iloc[0]
        self.assertIn(int(c3.grupo.replace("curso", "")), self.resumo["x4"]["cursos_sem_ponte"])
        self.assertLess(c3.coef, 0)
        self.assertLess(c3.p_mle, 0.05)
        # Estrato (resposta à auditoria): "a capital é o estrato com a maior fração de candidatos no ciclo 3";
        # "a capital tem a menor inclinação nos três ciclos, mas a diferença só tem q < 0,05 no ciclo 3"
        est = x4[(x4.dimensao == "estrato") & (x4.tipo_linha == "inclinacao_do_grupo") & (x4.ciclo != "empilhado")]
        n = est.pivot(index="grupo", columns="ciclo", values="n_candidatos_grupo")
        frac3 = n["3"] / n.sum(axis=1)
        self.assertEqual(frac3.idxmax(), "capital")
        bc = est.pivot(index="grupo", columns="ciclo", values="coef")
        for c in ("1", "2", "3"):
            self.assertEqual(bc[c].idxmin(), "capital")
        ie = fam[(fam.dimensao == "estrato") & (fam.tipo_linha == "interacao")]
        self.assertTrue((ie[ie.ciclo.isin(["1", "2"])]["q_bky"] > 0.05).all())
        # Adição pós-auditoria: "as três diferenças continuam positivas, com IC 95% acima de zero e p do score
        # bootstrap abaixo de 0,05 por conjunto e por curso"; fora do BKY
        ad = x4[x4.adicao_pos_auditoria.astype(bool)]
        self.assertFalse(ad.entra_bky.astype(bool).any())
        ai = ad[ad.tipo_linha == "interacao"]
        self.assertEqual(len(ai), 3)
        self.assertTrue((ai["ic95_inf"] > 0).all())
        self.assertTrue((ai["p_score_rademacher_conjunto"] < 0.05).all())
        self.assertTrue((ai["p_score_rademacher_curso"] < 0.05).all())
        # "na dimensão curso, o EP por cluster é menor que o de máxima verossimilhança nos termos próprios de curso"
        cp = x4[(x4.dimensao == "curso") & (x4.tipo_linha == "interacao") & (x4.ciclo != "empilhado") &
                (x4.grupo != "demais_cursos")]
        self.assertTrue((cp["ep_conj"] < cp["ep_mle"]).all())
        # "pelo EP de MV, o Wald entre cursos rejeita nos ciclos 2, 3 e empilhado, não no ciclo 1"
        wc = x4[(x4.dimensao == "curso") & (x4.tipo_linha == "wald_igualdade")].set_index("ciclo")
        for c in ("2", "3", "empilhado"):
            self.assertLess(wc.loc[c, "p_mle"], 0.05)
        self.assertGreater(wc.loc["1", "p_mle"], 0.05)
        # "no empilhado, o Wald da nota rejeita com q < 0,05"; "o tercil 2 é o menor nos ciclos 2 e 3"
        self.assertLess(wn.loc["empilhado", "q_bky"], 0.05)
        for c in ("2", "3"):
            n = self.resumo["x4"]["por_modelo"][f"nota_tercil|{c}"]["n_candidatos_por_grupo"]
            self.assertLess(n["tercil2"], min(n["tercil1"], n["tercil3"]))
        # "dentro de ciclo, fora da dimensão curso, as linhas com q < 0,05 são só: capitais no ciclo 3 (estrato),
        # escassez no ciclo 1 (Wald) e cursos sem ponte no ciclo 3"
        sig = fam[(fam.ciclo != "empilhado") & (fam.q_bky < 0.05)]
        achados = {(r.dimensao, r.ciclo) for r in sig.itertuples()}
        self.assertEqual(achados, {("estrato", "3"), ("escassez_tercil", "1"), ("escassez_tercil", "3")})
        self.assertEqual(set(sig[sig.dimensao == "escassez_tercil"].query("ciclo == '1'").tipo_linha),
                         {"wald_igualdade"})
        self.assertEqual(set(sig[(sig.dimensao == "escassez_tercil") & (sig.ciclo == "3")].grupo),
                         {"sem_ponte_curso_cbo"})
        e3 = x4[(x4.dimensao == "estrato") & (x4.ciclo == "3") & (x4.tipo_linha == "interacao")]
        self.assertTrue((e3["coef"] > 0).all())
        # X5: "a contagem sozinha tem coeficiente negativo em todos os ciclos"; "a razão de verossimilhança rejeita
        # o condicional em todos os ciclos"
        so = x5[(x5.tipo_linha == "vizinhanca") & (x5.especificacao == "vizinhos_contagem")]
        self.assertTrue((so["coef"] < 0).all())
        lr = x5[x5.tipo_linha == "teste_lambda_igual_1"]
        self.assertEqual(len(lr), len(X.CICLOS))
        self.assertTrue((lr["p_razao_verossimilhanca"] < 0.05).all())
        # "ciclo 2: a inclinação é positiva com IC acima de zero em todos os grupos de nota, escassez e estrato"
        c2 = x4[(x4.ciclo == "2") & (x4.tipo_linha == "inclinacao_do_grupo") & (x4.dimensao != "curso")]
        self.assertTrue((c2["ic95_inf"] > 0).all())
        # X5: "lambda abaixo de 1 em todos os ciclos, com IC 95% abaixo de 1"
        lam = x5[x5.tipo_linha == "lambda"]
        self.assertTrue((lam["coef"] < 1).all() and (lam["ic95_sup"] < 1).all())
        t1 = x5[x5.tipo_linha == "teste_lambda_igual_1"].set_index("ciclo")
        for c in ("1", "2", "empilhado"):
            self.assertLess(t1.loc[c, "q_bky"], 0.05)
        self.assertGreater(t1.loc["3", "q_bky"], 0.05)
        # "nenhum termo de vizinhança tem q < 0,05; com o total de vizinhos no modelo, a contagem fica perto de zero"
        viz = x5[x5.tipo_linha == "vizinhanca"]
        self.assertTrue((viz["q_bky"] > 0.05).all())
        ct = viz[viz.especificacao == "vizinhos_contagem_e_total"]
        self.assertTrue(((ct["ic95_inf"] < 0) & (ct["ic95_sup"] > 0)).all())
        fr = viz[viz.especificacao == "vizinhos_fracao"]
        self.assertTrue(((fr["ic95_inf"] < 0) & (fr["ic95_sup"] > 0)).all())
        # "a bolsa muda pouco com os termos de vizinhança e no aninhado: o sinal e a conclusão do E9 por ciclo ficam"
        b = x5[x5.tipo_linha == "bolsa"]
        for c, sel in b.groupby("ciclo"):
            self.assertEqual(len(set((sel["ic95_inf"] > 0).tolist())), 1, c)


if __name__ == "__main__":
    unittest.main()
