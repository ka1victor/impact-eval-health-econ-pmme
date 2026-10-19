"""Testes da família N (protocolo 48): `scripts/rdd_bolsa/23_estimar_contagem_vagas.py`.

Duas partes:

1. `TestSintetico`: DADOS SINTÉTICOS gerados em memória (semente fixa), rotulados como
   sintéticos e nunca gravados em `output/` nem em `data/`. Servem para conferir que o
   estimador com controle (covariável comum aos dois lados, CCFT 2019) recupera um salto
   conhecido, que a decomposição total = oferta + preenchimento fecha, que o Poisson daqui
   é o da rdd_lib e o do statsmodels, que a regra do cadastro reserva escolhe o controle
   certo e que controle ausente sai da linha e é contado, nunca vira zero.
2. `TestSaidasReais` e `TestDoc49`: invariantes das saídas versionadas
   (`output/rdd_bolsa/N_*`) e do doc 49. Os alvos são lidos de `output/` ou recalculados
   de forma independente; nenhum número de resultado é digitado aqui.
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
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "23_estimar_contagem_vagas.py"
_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location("contagem_vagas_23", SCRIPT)
N = importlib.util.module_from_spec(_spec)
sys.modules["contagem_vagas_23"] = N
_spec.loader.exec_module(N)
sys.dont_write_bytecode = _bytecode
L = N.L

OUT = ROOT / "output" / "rdd_bolsa"
EST = OUT / "N_estimativas.csv"
RESUMO = OUT / "N_resumo.json"
DOC = ROOT / "docs" / "06_execucao" / "49_resultados_contagem_vagas_preenchidas.md"

NATUREZA_SINTETICA = "SINTETICO_TESTE"   # rótulo dos dados gerados aqui; nunca gravados


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


# --------------------------------------------------------------------------
# Dados sintéticos (só em memória)
# --------------------------------------------------------------------------

SALTO_SINTETICO = 1.5      # salto conhecido em N1 dado as vagas (sintético)
GAMMA_SINTETICO = 0.4      # vagas preenchidas por vaga oferecida (sintético)


def municipios_sinteticos(semente: int = 11, n: int = 1200, salto_oferta: float = 0.0) -> pd.DataFrame:
    """SINTÉTICO: vagas oferecidas suaves no IVS (com salto opcional) e N1 = gamma vagas + salto T + ruído."""
    rng = np.random.default_rng(semente)
    s = rng.integers(200, 501, n).astype(float)
    t = ((s > 300) & (s <= 350)) | (s > 400)
    vi = rng.poisson(2 + 4 * (s / 1000 - 0.2) + salto_oferta * t).astype(float)
    vcr = rng.poisson(3, n).astype(float)
    vagas = vi + vcr + 1
    y = np.maximum(0, np.round(GAMMA_SINTETICO * vagas + 0.5 + 2 * (s / 1000 - 0.3) + SALTO_SINTETICO * t
                               + rng.normal(0, 0.8, n)))
    n_cel = np.maximum(1, np.round(vagas / 2))
    d = pd.DataFrame({"co_ibge": [f"9{i:05d}" for i in range(n)], "s_mil": s, "natureza_dos_dados": NATUREZA_SINTETICA,
                      "vagas_imediatas": vi, "vagas_cr": vcr + 1, "n_alocados_ch1": y, "n_celulas": n_cel})
    d["vagas_imediatas_mais_cr"] = d["vagas_imediatas"] + d["vagas_cr"]
    d["n_celulas_preenchidas_ch1"] = np.minimum(d["n_celulas"], np.ceil(y / 2))
    d["n_celulas_preenchidas_ate_ch2"] = np.minimum(d["n_celulas"], d["n_celulas_preenchidas_ch1"] + 1)
    d["n_ativos_ciclo"] = rng.poisson(1 + 0.2 * y).astype(float)
    d["motivos_ausencia"] = None
    return d


def amostra(d: pd.DataFrame, corte: int) -> "N.Amostra":
    return N.montar_amostra([(d, corte, str(corte))], empilhada=False)


class TestSintetico(unittest.TestCase):
    """Estimadores e regras em dados sintéticos (nada é gravado)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.d = municipios_sinteticos()

    def test_dados_rotulados_como_sinteticos(self) -> None:
        self.assertEqual(set(self.d["natureza_dos_dados"]), {NATUREZA_SINTETICA})

    def test_controle_recupera_salto_conhecido_e_reduz_ep(self) -> None:
        # Sintético: o salto dado as vagas é conhecido; o controle (comum aos dois lados) o recupera.
        for corte in (300, 400):
            a = amostra(self.d, corte)
            y, v = a.col("n_alocados_ch1"), a.col("vagas_imediatas_mais_cr")
            com = N.ajustar(a, y, N.H, v=v)
            sem = N.ajustar(a, y, N.H)
            self.assertLess(abs(com["tau"] - SALTO_SINTETICO), 3 * com["ep"], corte)
            self.assertGreater(com["tau"], 0)  # sinal: lado de bolsa maior menos lado de bolsa menor
            self.assertLess(com["ep"], sem["ep"])
            self.assertLess(abs(com["gamma"][str(corte)] - GAMMA_SINTETICO), 4 * com["ep_gamma"][str(corte)])

    def test_controle_igual_a_mqp_independente(self) -> None:
        # Sintético: o salto com controle = coeficiente de T num MQP feito à mão com [1, x, T, T x, v].
        a = amostra(self.d, 300)
        y, v = a.col("n_alocados_ch1"), a.col("vagas_imediatas_mais_cr")
        r = N.ajustar(a, y, N.H, v=v)
        x = (a.s - 300) / 1000
        w = np.clip(1 - np.abs(a.s - 300) / N.H, 0, None)
        ok = w > 0
        t = (x > 0).astype(float)
        X = np.column_stack([np.ones(ok.sum()), x[ok], t[ok], t[ok] * x[ok], v[ok]])
        b = np.linalg.solve(X.T @ (X * w[ok][:, None]), X.T @ (w[ok] * y[ok]))
        self.assertAlmostEqual(r["tau"], b[2], places=10)
        self.assertAlmostEqual(r["gamma"]["300"], b[4], places=10)

    def test_empilhado_recupera_salto(self) -> None:
        d2 = municipios_sinteticos(semente=12)
        a = N.montar_amostra([(d, c, f"c{k}_{c}") for k, d in ((1, self.d), (2, d2)) for c in (300, 400)],
                             empilhada=True)
        r = N.ajustar(a, a.col("n_alocados_ch1"), N.H, v=a.col("vagas_imediatas_mais_cr"))
        self.assertLess(abs(r["tau"] - SALTO_SINTETICO), 3 * r["ep"])
        self.assertEqual(len(r["gamma"]), 4)  # um coeficiente do controle por ciclo x corte
        self.assertIsNotNone(r["n_clusters"])

    def test_decomposicao_fecha_exatamente(self) -> None:
        # Sintético com salto na oferta: total (S-b) = S-a + gamma x salto do controle.
        d = municipios_sinteticos(semente=13, salto_oferta=3.0)
        a = amostra(d, 400)
        y, v = a.col("n_alocados_ch1"), a.col("vagas_imediatas_mais_cr")
        ra, rb = N.ajustar(a, y, N.H, v=v), N.ajustar(a, y, N.H)
        dv = N.ajustar(a, v, N.H)
        self.assertAlmostEqual(rb["tau"], ra["tau"] + ra["gamma"]["400"] * dv["tau"], places=10)
        self.assertGreater(dv["tau"], 0)  # a oferta salta: S-a fica condicional a uma variável afetada

    def test_residualizado_tem_o_salto_de_s_a(self) -> None:
        a = amostra(self.d, 300)
        y, v = a.col("n_alocados_ch1"), a.col("vagas_imediatas_mais_cr")
        ra = N.ajustar(a, y, N.H, v=v)
        rt = N.ajustar(a, N.residualizar(y, ra), N.H)
        self.assertAlmostEqual(rt["tau"], ra["tau"], places=10)

    def test_controle_ausente_sai_e_e_contado_nunca_zero(self) -> None:
        # Sintético: vagas ausentes em municípios da janela; a linha os descarta e conta.
        d = self.d.copy()
        dentro = np.flatnonzero(np.abs(d["s_mil"].to_numpy() - 300) < N.H)[:7]
        d.loc[d.index[dentro], "vagas_imediatas_mais_cr"] = np.nan
        a = amostra(d, 300)
        y = a.col("n_alocados_ch1")
        r = N.ajustar(a, y, N.H, v=a.col("vagas_imediatas_mais_cr"))
        r0 = N.ajustar(amostra(self.d, 300), y, N.H, v=amostra(self.d, 300).col("vagas_imediatas_mais_cr"))
        self.assertEqual(r["n_descartadas_covariavel_ausente"], 7)
        self.assertEqual(r["n_obs"], r0["n_obs"] - 7)
        # Com zero no lugar do ausente o resultado seria outro: o ausente não é tratado como zero.
        dz = d.copy()
        dz["vagas_imediatas_mais_cr"] = dz["vagas_imediatas_mais_cr"].fillna(0.0)
        rz = N.ajustar(amostra(dz, 300), y, N.H, v=amostra(dz, 300).col("vagas_imediatas_mais_cr"))
        self.assertNotAlmostEqual(r["tau"], rz["tau"], places=6)
        ln = N.preencher(N.nova_linha({}, "S-a", "principal", "-", h_mil=N.H, unidade="u",
                                      controle="vagas_imediatas_mais_cr", forma="VIC"), r)
        self.assertEqual(ln["n_descartadas_controle_ausente"], 7)

    def test_pipeline_sintetico_conta_ausencias_e_marca_holm(self) -> None:
        V = {1: municipios_sinteticos(semente=21, n=500), 2: municipios_sinteticos(semente=22, n=500)}
        V[1].loc[V[1].index[:5], "vagas_imediatas_mais_cr"] = np.nan
        lr = {(f"V{k}", c): {"w": 10, "id_pop": k, "origem": "sintetico", "motivo": ""} for k in (1, 2) for c in (300, 400)}
        est, _ = N.estimar_tudo(V, None, controle_principal="VIC", lr=lr, log=lambda *a: None)
        self.assertEqual(int(est["entra_holm"].sum()), 4)
        np.testing.assert_allclose(est.loc[est["entra_holm"], "p_holm"].to_numpy(float),
                                   L.holm(est.loc[est["entra_holm"], "p_valor"].to_numpy(float)))
        sa = est[(est["outcome_id"] == "N1") & (est["especificacao"] == "S-a") & (est["variante"] == "principal")
                 & (est["populacao"] == "V1")]
        self.assertTrue((sa["n_descartadas_controle_ausente"] >= 0).all())
        self.assertEqual(int(V[1]["vagas_imediatas_mais_cr"].isna().sum()), 5)  # nada foi preenchido
        self.assertTrue((est["estatuto"] == N.ESTATUTO).all())
        for esp in ("S-a", "S-b", "S-d", "S-e", "S-f", "S-g", "S-h", "S-i", "S-j", "decomposicao"):
            self.assertTrue((est["especificacao"] == esp).any(), esp)

    def test_poisson_igual_rdd_lib_e_statsmodels(self) -> None:
        import statsmodels.api as sm
        a = amostra(self.d, 300)
        y, v = a.col("n_alocados_ch1"), a.col("vagas_imediatas_mais_cr")
        off = np.log(v)
        meu = N.poisson(a, y, N.H, offset=off)
        ref = L.rd_poisson_local(a.s, y, 300, N.H, offset=off)
        self.assertAlmostEqual(meu["tau"], ref["tau"], places=9)
        self.assertAlmostEqual(meu["ep"], ref["ep"], places=9)
        # Com log(v) como covariável: coeficientes = GLM Poisson ponderado pelo kernel.
        cov = N.poisson(a, y, N.H, covariavel=np.log(v))
        x = (a.s - 300) / 1000
        w = np.clip(1 - np.abs(a.s - 300) / N.H, 0, None)
        ok = w > 0
        t = (x > 0).astype(float)
        X = np.column_stack([np.ones(ok.sum()), x[ok], t[ok], t[ok] * x[ok], np.log(v[ok])])
        glm = sm.GLM(y[ok], X, family=sm.families.Poisson(), var_weights=w[ok]).fit(tol=1e-12)
        self.assertAlmostEqual(cov["tau"], glm.params[2], places=6)

    def test_regra_do_cadastro_reserva(self) -> None:
        # Sintético: com alocado em célula só de CR, o controle é imediatas + CR; sem, só imediatas.
        cel = pd.DataFrame({"ciclo": [1, 1, 2], "n_alocados_ch1": [1.0, 2.0, 1.0], "vagas_imediatas": [0.0, 2.0, 1.0],
                            "vagas_cr": [1.0, 0.0, 0.0]})
        vm = pd.DataFrame({"ciclo": [1, 2], "co_ibge": ["900001", "900002"], "n_alocados_ch1": [3.0, 1.0],
                           "vagas_imediatas": [2.0, 1.0], "vagas_cr": [1.0, 0.0]})
        r = N.verificar_cadastro_reserva(cel, vm, None)
        self.assertEqual((r["resposta"], r["controle_principal"]), ("sim", "VIC"))
        self.assertEqual(r["pode_por_ciclo_nos_dados"], {"1": True, "2": False})
        cel2 = cel.assign(n_alocados_ch1=[0.0, 2.0, 1.0])
        r2 = N.verificar_cadastro_reserva(cel2, vm.assign(n_alocados_ch1=[2.0, 1.0]), None)
        self.assertEqual((r2["resposta"], r2["controle_principal"]), ("nao", "VI"))

    def test_u_zero_so_fora_do_quadro(self) -> None:
        # Sintético: no quadro com ausente, U fica ausente; fora do quadro, zero estrutural.
        V = {1: pd.DataFrame({"co_ibge": ["1", "2"], "s_mil": [290.0, 310.0], "n_alocados_ch1": [2.0, np.nan],
                              "n_celulas_preenchidas_ch1": [1.0, 1.0], "n_celulas_preenchidas_ate_ch2": [1.0, 1.0],
                              "n_ativos_ciclo": [0.0, 1.0]})}
        U = pd.DataFrame({"co_ibge": ["1", "2", "3"], "s_mil": [290.0, 310.0, 320.0], "n_ativos_pmme_c1": [0.0, 1.0, 2.0],
                          "vagas_imediatas_c1": [1.0, 1.0, 0.0], "vagas_cr_c1": [0.0, 1.0, 0.0],
                          "n_celulas_c1": [1.0, 1.0, 0.0]})
        u = N.colunas_u(U, V)
        self.assertEqual(u["n_alocados_ch1_c1"].iloc[0], 2.0)
        self.assertTrue(np.isnan(u["n_alocados_ch1_c1"].iloc[1]))
        self.assertEqual(u["n_alocados_ch1_c1"].iloc[2], 0.0)
        self.assertEqual(u["n_ativos_ciclo_c1"].iloc[2], 2.0)  # N4 em U: ativos observados também fora do quadro

    def test_faixas_das_figuras_nao_misturam_dentro_e_fora(self) -> None:
        x = np.arange(-80, 81, dtype=float)
        f = N._faixas(x)
        dentro = np.abs(x) < N.H
        for b in np.unique(f):
            self.assertEqual(len(set(dentro[f == b])), 1, b)
        self.assertTrue((f[x <= 0] < 0).all() and (f[x > 0] >= 0).all())

    def test_arquivo_errado_de_ivs_nao_e_lido_e_nada_vira_zero_por_fillna(self) -> None:
        fonte = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("ivs_ipea_2010_municipios", fonte)
        self.assertNotIn("fillna(0", fonte)

    def test_tabelas_do_doc_aplicadas(self) -> None:
        texto = "a\n<!-- N:x:inicio -->\nvelho\n<!-- N:x:fim -->\nb"
        self.assertEqual(N.tabelas_no_doc(N.aplicar_tabelas_doc(texto, {"x": "novo"}))["x"], "novo")


# --------------------------------------------------------------------------
# Saídas reais
# --------------------------------------------------------------------------

@unittest.skipUnless(EST.exists() and RESUMO.exists(), "saidas da familia N ausentes")
class TestSaidasReais(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.est = pd.read_csv(EST, dtype={"corte": str, "ciclo": str})
        cls.resumo = json.loads(RESUMO.read_text(encoding="utf-8"))

    def _uma(self, **f) -> pd.Series:
        m = np.ones(len(self.est), dtype=bool)
        for k, v in f.items():
            m &= self.est[k].astype(str) == str(v)
        sub = self.est[m]
        self.assertEqual(len(sub), 1, f)
        return sub.iloc[0]

    def test_esquema_e_rotulos(self) -> None:
        self.assertEqual(list(self.est.columns), N.COLUNAS)
        self.assertTrue((self.est["natureza_dos_dados"] == "EMPIRICO").all())
        self.assertTrue((self.est["estatuto"] == "PROTOCOLO_48_POS_RESULTADO").all())
        self.assertEqual(self.resumo["natureza_dos_dados"], "EMPIRICO")
        self.assertEqual(self.resumo["estatuto"], "PROTOCOLO_48_POS_RESULTADO")
        self.assertTrue(set(self.est["status"]) <= {"EXECUTADO", "SEM_ESTIMATIVA", "NAO_EXECUTADO"})

    def test_nan_sempre_com_nota(self) -> None:
        nucleo = ["tau", "ep", "ic95_inf", "ic95_sup", "p_valor"]
        ruins = self.est[self.est[nucleo].isna().any(axis=1) & (self.est["nota"].fillna("") == "")]
        self.assertEqual(len(ruins), 0)

    def test_holm_recalculado(self) -> None:
        h = self.est[self.est["entra_holm"].astype(bool)]
        self.assertEqual(sorted(h["outcome_id"]), ["N1", "N2", "N3", "N4"])
        self.assertTrue((h["especificacao"] == "S-a").all() and (h["variante"] == "principal").all())
        self.assertTrue((h["corte"] == "empilhado").all())
        self.assertEqual(dict(zip(h["outcome_id"], h["populacao"])),
                         {"N1": "V1+V2+V3", "N2": "V1+V2+V3", "N3": "V1+V2", "N4": "V1+V2"})
        np.testing.assert_allclose(h["p_holm"].to_numpy(float), L.holm(h["p_valor"].to_numpy(float)))
        self.assertTrue(self.est.loc[~self.est["entra_holm"].astype(bool), "p_holm"].isna().all())
        for r in self.resumo["holm"]["linhas"]:
            x = h[h["outcome_id"] == r["outcome_id"]].iloc[0]
            self.assertAlmostEqual(float(x["p_holm"]), r["p_holm"], places=12)

    def test_todas_as_especificacoes_presentes(self) -> None:
        faltam = []
        for spec in N.CATALOGO_N:
            ks = [k for k in spec["ciclos"]]
            pops = [(f"V{k}", ("0.300", "0.400", "empilhado")) for k in ks]
            pops += [("+".join(f"V{k}" for k in ks), ("0.300", "0.400", "empilhado"))]
            for pop, cortes in pops:
                for c in cortes:
                    sub = self.est[(self.est["outcome_id"] == spec["id"]) & (self.est["populacao"] == pop)
                                   & (self.est["corte"] == c)]
                    esp = sub["especificacao"].value_counts().to_dict()
                    empilhada = "+" in pop or c == "empilhado"
                    # No empilhado: + a variante de coeficiente único da auditoria 20; S-h sai NAO_EXECUTADO.
                    exig = {"S-a": 3 + (1 if spec["controle"] == "vagas_oferecidas" else 0) + (1 if empilhada else 0),
                            "S-b": 3, "S-d": 2, "S-e": 1, "S-f": 1, "S-g": 8, "S-j": 2, "decomposicao": 3,
                            "S-h": 1 if empilhada else 2}
                    for e, n in exig.items():
                        if esp.get(e, 0) != n:
                            faltam.append((spec["id"], pop, c, e, esp.get(e, 0)))
            for k in ks:
                n_si = int(((self.est["outcome_id"] == spec["id"]) & (self.est["populacao"] == f"V{k}")
                            & (self.est["especificacao"] == "S-i")).sum())
                if n_si != 2 * (3 + len(N.PLACEBOS_MIL)):
                    faltam.append((spec["id"], k, "S-i", n_si))
        for oid in N.OFERTA:
            for pop in ("V1", "V2", "V3", "V1+V2+V3", "U"):
                for c in ("0.300", "0.400", "empilhado"):
                    n = int(((self.est["outcome_id"] == oid) & (self.est["populacao"] == pop) & (self.est["corte"] == c)
                             & (self.est["especificacao"] == "S-c") & (self.est["variante"] == "principal")).sum())
                    if n < 1:
                        faltam.append((oid, pop, c, "S-c"))
        self.assertEqual(faltam, [])

    def test_empilhados_sem_s_h_e_s_i_saem_nao_executado(self) -> None:
        # Auditoria 20: toda especificação do protocolo aparece em cada amostra, executada ou com o motivo.
        sh = self.est[(self.est["especificacao"] == "S-h") & (self.est["variante"] == "empilhado")]
        self.assertTrue(len(sh) > 0 and (sh["status"] == "NAO_EXECUTADO").all() and sh["nota"].str.len().gt(0).all())
        self.assertTrue(sh["tau"].isna().all())
        si = self.est[(self.est["especificacao"] == "S-i") & (self.est["variante"] == "ciclos_empilhados")]
        self.assertEqual(sorted(si["outcome_id"]), ["N1", "N2", "N3", "N4"])
        self.assertTrue((si["status"] == "NAO_EXECUTADO").all() and si["tau"].isna().all())

    def test_sensibilidade_coeficiente_unico(self) -> None:
        # Auditoria 20: variante fora do protocolo, rotulada, fora do Holm do protocolo; Holm próprio recalculado.
        u = self.est[self.est["variante"] == "controle_coeficiente_unico"]
        self.assertTrue(len(u) > 0)
        self.assertTrue((u["especificacao"] == "S-a").all() and (~u["no_protocolo"].astype(bool)).all())
        self.assertTrue(u["rotulo"].str.startswith("SENSIBILIDADE_AUDITORIA_20").all())
        self.assertFalse(u["entra_holm"].astype(bool).any())
        self.assertTrue(((u["corte"] == "empilhado") | u["populacao"].str.contains(r"\+")).all())
        s = self.resumo["sensibilidade_coeficiente_unico_auditoria_20"]
        self.assertFalse(s["no_protocolo"])
        h = self.est[self.est["entra_holm"].astype(bool)]
        self.assertEqual({x["outcome_id"] for x in s["linhas"]}, set(h["outcome_id"]))
        pu = np.array([x["p_coef_unico"] for x in s["linhas"]], dtype=float)
        np.testing.assert_allclose([x["p_holm_coef_unico"] for x in s["linhas"]], L.holm(pu))
        for x in s["linhas"]:
            r = self._uma(outcome_id=x["outcome_id"], populacao=x["populacao"], corte="empilhado",
                          especificacao="S-a", variante="controle_coeficiente_unico")
            self.assertAlmostEqual(float(r["p_valor"]), x["p_coef_unico"], places=12)
            self.assertTrue(0.0 <= x["wald_igualdade_p"] <= 1.0)

    def test_coeficiente_unico_igual_a_mqp_independente(self) -> None:
        # MQP à mão, CR1 por município: grupos ciclo x corte com intercepto e inclinações por lado, salto comum e
        # um só coeficiente das vagas oferecidas; confere a linha de N1 com ciclos e cortes empilhados.
        vm = pd.read_parquet(OUT / "outcomes" / "outcomes_V_municipio.parquet")
        vm = vm[vm["ivs_2010_oficial"].notna()]
        blocos = []
        for k in (1, 2, 3):
            d = vm[vm["ciclo"] == k]
            for c in (300, 400):
                blocos.append(pd.DataFrame({"m": d["co_ibge"].to_numpy(), "x": (d["ivs_2010_oficial"] * 1000).round()
                                            .to_numpy() - c, "y": d["n_alocados_ch1"].to_numpy(float),
                                            "v": (d["vagas_imediatas"] + d["vagas_cr"]).to_numpy(float),
                                            "g": f"{k}_{c}"}))
        b = pd.concat(blocos, ignore_index=True)
        w = np.clip(1 - np.abs(b["x"].to_numpy()) / 50, 0, None)
        b, w = b[w > 0].reset_index(drop=True), w[w > 0]
        x, t = b["x"].to_numpy() / 1000, (b["x"].to_numpy() > 0).astype(float)
        cols = []
        for g in sorted(b["g"].unique()):
            ind = (b["g"] == g).to_numpy(float)
            cols += [ind, ind * x, ind * t * x]
        X = np.column_stack(cols + [t, b["v"].to_numpy()])
        y = b["y"].to_numpy()
        bread = np.linalg.inv(X.T @ (X * w[:, None]))
        beta = bread @ (X.T @ (w * y))
        sc = X * (w * (y - X @ beta))[:, None]
        _, idx = np.unique(b["m"], return_inverse=True)
        S = np.zeros((idx.max() + 1, X.shape[1]))
        np.add.at(S, idx, sc)
        G, n, k = S.shape[0], len(y), X.shape[1]
        V = bread @ (S.T @ S) @ bread * (G / (G - 1)) * ((n - 1) / (n - k))
        i = X.shape[1] - 2
        r = self._uma(outcome_id="N1", populacao="V1+V2+V3", corte="empilhado", especificacao="S-a",
                      variante="controle_coeficiente_unico")
        self.assertAlmostEqual(float(r["tau"]), beta[i], places=9)
        self.assertAlmostEqual(float(r["ep"]), float(np.sqrt(V[i, i])), places=9)

    def test_ciclo3_de_n3_e_n4_nao_executado_com_motivo(self) -> None:
        for oid in ("N3", "N4"):
            sub = self.est[(self.est["outcome_id"] == oid) & (self.est["populacao"] == "V3")]
            self.assertEqual(len(sub), 3)
            self.assertTrue((sub["status"] == "NAO_EXECUTADO").all())
            self.assertTrue(sub["nota"].str.len().gt(0).all())
            self.assertTrue(sub["tau"].isna().all())  # ausente fica ausente

    def test_linha_principal_reproduzida_de_forma_independente(self) -> None:
        # MQP à mão com [1, x, T, T x, v] para V1 em 0,300 (h = 0,050), lido das saídas da tarefa B e do a08.
        a08 = pd.read_csv(ROOT / "output" / "aquisicao" / "a08_ivs_2010_oficial_municipio.csv", dtype={"co_ibge": str})
        smap = a08.set_index(a08["co_ibge"].str.zfill(6))["ivs"].mul(1000).round()
        vm = pd.read_parquet(OUT / "outcomes" / "outcomes_V_municipio.parquet")
        d = vm[vm["ciclo"] == 1].copy()
        d["s"] = d["co_ibge"].map(smap)
        d = d[d["s"].notna()]
        x = (d["s"].to_numpy(float) - 300) / 1000
        w = np.clip(1 - np.abs(x * 1000) / 50, 0, None)
        ok = w > 0
        t = (x > 0).astype(float)
        v = (d["vagas_imediatas"] + d["vagas_cr"]).to_numpy(float)
        y = d["n_alocados_ch1"].to_numpy(float)
        for com in (True, False):
            cols = [np.ones(ok.sum()), x[ok], t[ok], t[ok] * x[ok]] + ([v[ok]] if com else [])
            X = np.column_stack(cols)
            b = np.linalg.solve(X.T @ (X * w[ok][:, None]), X.T @ (w[ok] * y[ok]))
            r = self._uma(outcome_id="N1", populacao="V1", corte="0.300", especificacao="S-a" if com else "S-b",
                          variante="principal")
            self.assertAlmostEqual(float(r["tau"]), b[2], places=10)

    def test_verificacao_cr_recalculada_e_controle_coerente(self) -> None:
        vc = self.resumo["verificacao_cadastro_reserva"]
        cel = pd.read_parquet(OUT / "outcomes" / "outcomes_V_celula.parquet")
        for k, g in cel.groupby("ciclo"):
            c = vc["contagens_por_ciclo"][str(int(k))]
            self.assertEqual(c["alocados_em_celulas_so_cadastro_reserva"],
                             float(g.loc[g["vagas_imediatas"] == 0, "n_alocados_ch1"].sum()))
            self.assertEqual(c["celulas_com_alocados_acima_das_imediatas"],
                             int((g["n_alocados_ch1"] > g["vagas_imediatas"]).sum()))
        esperado = "VIC" if vc["resposta"] == "sim" else "VI"
        self.assertEqual(vc["controle_principal"], esperado)
        self.assertEqual(self.resumo["controle"]["principal"], esperado)
        sa = self.est[(self.est["outcome_id"] == "N1") & (self.est["especificacao"] == "S-a")
                      & (self.est["variante"] == "principal")]
        self.assertEqual(set(sa["controle"]), {N.OFERTA[esperado]["col"]})
        alt = self.est[(self.est["outcome_id"] == "N1") & (self.est["variante"] == "controle_forma_alternativa")]
        self.assertEqual(set(alt["controle"]), {N.OFERTA[vc["controle_sensibilidade"]]["col"]})

    def test_trechos_dos_editais_estao_nos_arquivos(self) -> None:
        try:
            import pypdf
        except ImportError:
            self.skipTest("pypdf ausente: conferencia do texto do edital nao executada")
        textos = {}
        for e in self.resumo["verificacao_cadastro_reserva"]["editais"]:
            caminho = ROOT / e["arquivo"]
            self.assertEqual(sha256(caminho), e["sha256"])
            if caminho not in textos:
                r = pypdf.PdfReader(str(caminho))
                bruto = " ".join(p.extract_text() or "" for p in r.pages)
                textos[caminho] = re.sub(r"\s+", " ", bruto.replace("ﬁ", "fi").replace("ﬂ", "fl"))
            self.assertIn(e["trecho"], textos[caminho], e["item"])

    def test_hashes_das_entradas_conferem(self) -> None:
        for e in self.resumo["entradas"]:
            self.assertEqual(sha256(ROOT / e["caminho"]), e["sha256"], e["caminho"])
        self.assertEqual(self.resumo["protocolo"]["sha256"], sha256(ROOT / self.resumo["protocolo"]["arquivo"]))
        self.assertEqual(sha256(EST), self.resumo["saidas"]["N_estimativas.csv"]["sha256"])

    def test_figuras_existem_e_titulos_batem_com_o_csv(self) -> None:
        figs = self.resumo["saidas"]["figuras"]
        self.assertEqual(len(figs), 6)
        nomes = {Path(f["arquivo"]).name for f in figs}
        for com in ("sem_controle", "com_controle"):
            for s in ("ciclo1", "ciclo2", "empilhado"):
                self.assertIn(f"N1_{com}_{s}.png", nomes)
        for f in figs:
            caminho = ROOT / f["arquivo"]
            self.assertTrue(caminho.exists() and caminho.stat().st_size > 10_000, f["arquivo"])
            self.assertEqual(caminho.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
            for p in f["paineis"]:
                r = self._uma(outcome_id="N1", populacao=f["populacao"], corte=p["corte"],
                              especificacao=p["especificacao"], variante="principal")
                for c in ("tau", "ic95_inf", "ic95_sup", "p_valor"):
                    self.assertAlmostEqual(float(r[c]), p[c], places=12, msg=(f["arquivo"], c))

    def test_decomposicao_fecha_nas_saidas(self) -> None:
        d = self.est[self.est["especificacao"] == "decomposicao"]
        for _, g in d.groupby(["outcome_id", "populacao", "corte"]):
            v = dict(zip(g["variante"], g["tau"]))
            self.assertAlmostEqual(v["total (= S-b na amostra de S-a)"],
                                   v["via oferta (soma gamma x salto do controle)"]
                                   + v["preenchimento dado as vagas (= S-a)"], places=9)

    def test_mde_e_efeito_relativo(self) -> None:
        ok = self.est[self.est["ep"].notna() & self.est["mde"].notna()]
        np.testing.assert_allclose(ok["mde"], 2.8 * ok["ep"])
        r = self.est[self.est["efeito_relativo_media_abaixo"].notna() & ~self.est["especificacao"].eq("decomposicao")]
        np.testing.assert_allclose(r["efeito_relativo_media_abaixo"], r["tau"] / r["media_abaixo"])

    def test_resultados_anteriores_intactos(self) -> None:
        # O script só lê E6 (janela LR e alvo de conferência); os hashes registrados conferem com os arquivos.
        lidos = {e["caminho"] for e in self.resumo["entradas"]}
        self.assertIn("output/rdd_bolsa/E6_estimativas.csv", lidos)
        self.assertTrue(self.resumo["validacoes"]["E6_ponderado"]["reproduz"])


@unittest.skipUnless(EST.exists(), "saidas da familia N ausentes")
class TestRecalculoIndependenteAuditoria20(unittest.TestCase):
    """Auditoria 20: S-a, S-b e S-c principais (por corte, cortes empilhados, ciclos empilhados) refeitos com o MQP
    ponderado do statsmodels (HC1; CR1 por município no empilhado), sem a rdd_lib nem o script 23, lendo só
    `outcomes_V_municipio.parquet` (running variable = coluna `ivs_2010_oficial`); confere também a média abaixo,
    o efeito relativo, o MDE, os n e o Holm."""

    TOL = 1e-9

    @classmethod
    def setUpClass(cls) -> None:
        import statsmodels.api as sm
        cls.sm = sm
        cls.est = pd.read_csv(EST, dtype={"corte": str, "ciclo": str})
        vm = pd.read_parquet(OUT / "outcomes" / "outcomes_V_municipio.parquet")
        vm = vm[vm["ivs_2010_oficial"].notna()].copy()   # o município sem IVS oficial fica fora (nunca vira zero)
        vm["s"] = (vm["ivs_2010_oficial"] * 1000).round()
        vm["VIC"] = vm["vagas_imediatas"] + vm["vagas_cr"]
        cls.V = {int(k): d.reset_index(drop=True) for k, d in vm.groupby("ciclo")}

    def _amostras(self, ks):
        rc = {300: "0.300", 400: "0.400"}
        out = []
        for k in ks:
            out += [(f"V{k}", rc[c], [(self.V[k], c, str(c))], False) for c in (300, 400)]
            out.append((f"V{k}", "empilhado", [(self.V[k], c, str(c)) for c in (300, 400)], True))
        if len(ks) > 1:
            pop = "+".join(f"V{k}" for k in ks)
            out += [(pop, rc[c], [(self.V[k], c, f"c{k}") for k in ks], True) for c in (300, 400)]
            out.append((pop, "empilhado", [(self.V[k], c, f"c{k}_{c}") for k in ks for c in (300, 400)], True))
        return out

    def _ajuste(self, partes, ycol, vcol, empilhada):
        b = pd.concat([pd.DataFrame({"m": d["co_ibge"].to_numpy(), "x": d["s"].to_numpy() - c,
                                     "y": d[ycol].to_numpy(float),
                                     "v": d[vcol].to_numpy(float) if vcol else 0.0, "g": g}) for d, c, g in partes],
                      ignore_index=True)
        b["k"] = np.where(np.abs(b["x"]) < 50, 1 - np.abs(b["x"]) / 50, 0.0)
        b = b[(b["k"] > 0) & np.isfinite(b["y"]) & np.isfinite(b["v"])].reset_index(drop=True)
        t, x = (b["x"] > 0).astype(float), b["x"] / 1000
        cols = {}
        grupos = sorted(b["g"].unique())
        if empilhada:
            for g in grupos:
                ind = (b["g"] == g).astype(float)
                cols.update({f"c{g}": ind, f"x{g}": ind * x, f"tx{g}": ind * t * x})
            cols["T"] = t
        else:
            cols.update({"c": 1.0 + 0 * x, "x": x, "T": t, "tx": t * x})
        if vcol:
            for g in grupos:
                cols[f"v{g}"] = (b["g"] == g).astype(float) * b["v"]
        X = pd.DataFrame(cols)
        m = self.sm.WLS(b["y"].to_numpy(), X.to_numpy(), weights=b["k"].to_numpy())
        if empilhada:
            _, cl = np.unique(b["m"].to_numpy(), return_inverse=True)
            r = m.fit(cov_type="cluster", cov_kwds={"groups": cl, "use_correction": True})
        else:
            r = m.fit(cov_type="HC1")
        i = list(X.columns).index("T")
        abaixo = b["x"] <= 0
        return {"tau": r.params[i], "ep": r.bse[i], "p": float(r.pvalues[i]), "media": b.loc[abaixo, "y"].mean(),
                "n_ab": b.loc[abaixo, "m"].nunique(), "n_ac": b.loc[~abaixo, "m"].nunique(), "n_obs": len(b)}

    def _conferir(self, meu, **f):
        m = np.ones(len(self.est), dtype=bool)
        for k, v in f.items():
            m &= self.est[k].astype(str) == str(v)
        sub = self.est[m]
        self.assertEqual(len(sub), 1, f)
        r = sub.iloc[0]
        for a, b in (("tau", "tau"), ("ep", "ep"), ("p", "p_valor"), ("media", "media_abaixo")):
            self.assertLess(abs(meu[a] - float(r[b])), self.TOL, (f, b))
        self.assertLess(abs(meu["tau"] / meu["media"] - float(r["efeito_relativo_media_abaixo"])), self.TOL, f)
        self.assertLess(abs(2.8 * meu["ep"] - float(r["mde"])), self.TOL, f)
        self.assertEqual((meu["n_ab"], meu["n_ac"], meu["n_obs"]),
                         (int(r["n_abaixo"]), int(r["n_acima"]), int(r["n_obs"])), f)
        return r

    def test_s_a_s_b_s_c_e_holm(self) -> None:
        outs = {"N1": ("n_alocados_ch1", "VIC", (1, 2, 3)), "N2": ("n_celulas_preenchidas_ch1", "n_celulas", (1, 2, 3)),
                "N3": ("n_celulas_preenchidas_ate_ch2", "n_celulas", (1, 2)), "N4": ("n_ativos_ciclo", "VIC", (1, 2))}
        p_holm, n = {}, 0
        for oid, (ycol, vcol, ks) in outs.items():
            for pop, corte, partes, emp in self._amostras(ks):
                ra = self._ajuste(partes, ycol, vcol, emp)
                self._conferir(ra, outcome_id=oid, populacao=pop, corte=corte, especificacao="S-a", variante="principal")
                self._conferir(self._ajuste(partes, ycol, None, emp), outcome_id=oid, populacao=pop, corte=corte,
                               especificacao="S-b", variante="principal")
                n += 2
                if corte == "empilhado" and "+" in pop:
                    p_holm[oid] = ra["p"]
        for oid, col in (("VIC", "VIC"), ("VI", "vagas_imediatas"), ("NC", "n_celulas")):
            for pop, corte, partes, emp in self._amostras((1, 2, 3)):
                self._conferir(self._ajuste(partes, col, None, emp), outcome_id=oid, populacao=pop, corte=corte,
                               especificacao="S-c", variante="principal")
                n += 1
        self.assertEqual(n, 120)
        from statsmodels.stats.multitest import multipletests
        ids = sorted(p_holm)
        ref = multipletests([p_holm[i] for i in ids], method="holm")[1]
        h = self.est[self.est["entra_holm"].astype(bool)].set_index("outcome_id")
        for i, p in zip(ids, ref):
            self.assertLess(abs(float(h.loc[i, "p_holm"]) - p), self.TOL, i)


@unittest.skipUnless(DOC.exists() and EST.exists(), "doc 49 ou saidas da familia N ausentes")
class TestDoc49(unittest.TestCase):
    """O doc 49 não tem número de resultado digitado: blocos = gerados das saídas; prosa só com parâmetros."""

    def test_blocos_do_doc_iguais_aos_gerados(self) -> None:
        est, resumo = N.ler_saidas()
        geradas = N.gerar_tabelas_doc(est, resumo)
        no_doc = N.tabelas_no_doc(DOC.read_text(encoding="utf-8"))
        self.assertTrue(no_doc)
        self.assertEqual(set(no_doc), set(geradas))
        for nome, corpo in no_doc.items():
            self.assertEqual(corpo, geradas[nome], nome)

    @staticmethod
    def _prosa() -> str:
        texto = N.MARCA.sub("", DOC.read_text(encoding="utf-8"))
        texto = re.sub(r"`[^`]*`", "", texto)
        texto = re.sub(r"\]\([^)]*\)", "]", texto)
        texto = re.sub(r"(?m)^#+ .*$", "", texto)
        texto = re.sub(r"§+\s?\d+(?:[.,–-]\d+)*", "", texto)
        texto = re.sub(r"\b\d{2}/\d{2}/\d{4}\b", "", texto)
        texto = re.sub(r"\b[A-Za-z_]+\d+[a-z]?(?:\.\d+)*\b", "", texto)
        texto = re.sub(r"\d+ª", "", texto)
        texto = re.sub(r"(?m)^\s*\d+\. ", "", texto)
        # Referências a documentos e seções (não são resultados): "docs 41 a 46", "protocolo 40", "seção 5".
        texto = re.sub(r"\b(?:docs?|protocolo|seção)\s+\d+(?:\s+a\s+\d+)?", "", texto)
        for fixo in ("SHA-256", "IC 95%", "auditorias/18"):
            texto = texto.replace(fixo, "")
        return texto

    def test_prosa_sem_numero_de_resultado(self) -> None:
        decimais = set(re.findall(r"(?<![\w.,])[−+-]?\d+[,.]\d+", self._prosa()))
        permitidos = {"0,300", "0,400", "0,050", "0,030", "0,080", "0,002", "0,010", "0,190", "0,510", "2,8", "0,5"}
        self.assertEqual(decimais - permitidos, set())

    def test_prosa_sem_inteiro_de_resultado(self) -> None:
        texto = re.sub(r"(?<![\w.,])[−+-]?\d+[,.]\d+", "", self._prosa())
        inteiros = set(re.findall(r"(?<![\w.,])[−+-]?\d+(?![\w.,]\d)", texto))
        anos = {x for x in inteiros if x.isdigit() and 2000 <= int(x) <= 2030}
        self.assertEqual(inteiros - {"1", "2", "3", "4", "5", "10", "15", "20"} - anos, set())


if __name__ == "__main__":
    unittest.main()
