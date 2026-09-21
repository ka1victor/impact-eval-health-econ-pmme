"""Invariantes A5 — dinâmica associativa da oferta cadastrada no CNES."""

from __future__ import annotations

import json
import hashlib
import unittest
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "tema_trabalho"

# Entradas declaradas por A5 que o pipeline regera e o repositorio nao versiona.
REGERAVEIS_NAO_VERSIONADOS = {"output/painel_municipio_curso_mensal.parquet"}


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class ProvimentoCnesA5Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.panel = pd.read_parquet(OUT / "A5_painel_T0.parquet")
        cls.cross = pd.read_csv(OUT / "A5_cross_section_6m.csv", dtype={"co_ibge_6d": str})
        cls.manifest = json.loads((OUT / "A5_manifesto_maturidade_censura.json").read_text(encoding="utf-8"))
        cls.est = json.loads((OUT / "A5_estimativas_provimento.json").read_text(encoding="utf-8"))
        cls.report = (OUT / "A5_relatorio_diagnostico.md").read_text(encoding="utf-8")

    def test_hashes_entradas_conferem(self) -> None:
        # Proveniencia de A5, ausente ate entao: A3, A4 e A6 ja checavam seus
        # hashes de entrada, mas A5 nao, e por isso registros obsoletos de A5
        # passavam despercebidos. Os sha256 sao sempre da forma canonica LF
        # imposta pelo .gitattributes; um tree com CRLF produz outro digest.
        #
        # Uma unica entrada declarada nao e versionada: o painel mensal
        # municipio-curso e regeravel pelo pipeline e esta no .gitignore. Num
        # clone limpo ele nao existe, entao a existencia so e exigida dos
        # arquivos versionados; se o painel estiver presente, o hash e cobrado
        # como qualquer outro.
        for artefato, hashes in [
            ("A5_estimativas_provimento.json", self.est["hashes_entradas"]),
            ("A5_manifesto_maturidade_censura.json", self.manifest["hashes_entradas"]),
        ]:
            self.assertGreater(len(hashes), 3, f"bloco de hashes incompleto em {artefato}")
            conferidos = 0
            for rel, meta in hashes.items():
                caminho = ROOT / rel
                if not caminho.exists():
                    self.assertIn(
                        rel,
                        REGERAVEIS_NAO_VERSIONADOS,
                        f"missing {artefato}: {rel}",
                    )
                    continue
                self.assertEqual(sha(caminho), meta["sha256"], f"hash diverge {artefato}: {rel}")
                conferidos += 1
            self.assertGreater(conferidos, 3, f"poucas entradas conferidas em {artefato}")

    def test_painel_balanceado(self) -> None:
        self.assertEqual(len(self.panel), 1184 * 26)
        self.assertEqual(self.panel["co_ibge_6d"].nunique(), 368)
        self.assertFalse(self.panel.duplicated(["co_ibge_6d", "cod_curso", "competencia"]).any())

    def test_referencia_limpa_e_timing(self) -> None:
        timing = self.est["t0_e_horizonte"]
        self.assertEqual(timing["referencia_pre_oferta"], "202506")
        self.assertEqual(timing["follow_comum"], "202603")
        self.assertNotIn("baseline", timing)
        self.assertIn("Setembro/2025 não é usado como baseline", self.report)
        self.assertIn("tempo de exposição física heterogêneo", self.report)

    def test_amostra_principal_confirmatoria(self) -> None:
        self.assertEqual(self.cross["amostra_confirmatoria"].sum(), 587)
        primary = self.est["modelos"]["principal_dinamico_confirmatorio"]
        self.assertEqual(primary["n_celulas"], 587)
        self.assertEqual(primary["n_clusters"], 295)
        level = pd.read_csv(OUT / "A5_tabela_03_modelo_estoque_6m.csv")
        row = level[(level["termo"] == "atracao_muni") & level["espec"].str.contains("minimal")].iloc[0]
        self.assertEqual(int(row["n"]), 587)
        self.assertEqual(int(row["n_clusters"]), 295)

    def test_estudo_evento(self) -> None:
        event = pd.read_csv(OUT / "A5_tabela_07_estudo_evento_atracao.csv", dtype={"competencia": str})
        self.assertEqual(set(event["amostra"]), {"confirmatoria_587", "ampliada_1184"})
        self.assertEqual(len(event), 52)
        ref = event[(event["amostra"] == "confirmatoria_587") & (event["competencia"] == "202506")].iloc[0]
        self.assertTrue(ref["referencia"])
        self.assertEqual(ref["beta"], 0)
        summary = self.est["modelos"]["principal_dinamico_confirmatorio"]
        self.assertIn("pre_p", summary)
        self.assertIn("mar2026_beta", summary)

    def test_delta_distribuicao_transparente(self) -> None:
        self.assertIn("delta_estoque_jun25_mar26", self.cross.columns)
        distribution = self.est["modelos"]["distribuicao_delta_confirmatoria"]
        self.assertEqual(distribution["0"]["mediana"], 0)
        self.assertEqual(distribution["1"]["mediana"], 1)
        self.assertGreater(distribution["1"]["max"], 100)
        self.assertIn("mediana", self.report.lower())
        self.assertIn("máximo", self.report.lower())

    def test_fluxo_mensal_nao_e_acumulado(self) -> None:
        definition = self.est["outcomes_permitidos"]["n_entradas_6m"].lower()
        self.assertIn("washout", definition)
        self.assertIn("nao fluxo acumulado", definition)
        self.assertIn("não entradas acumuladas", self.report.lower())

    def test_censura(self) -> None:
        self.assertTrue(self.panel.loc[self.panel["competencia"] < "202412", "n_entradas_6m"].isna().all())
        self.assertTrue(self.panel.loc[self.panel["competencia"] > "202604", "n_saidas_confirmadas_3m"].isna().all())
        checks = self.manifest["checks"]
        self.assertTrue(checks["painel_balanceado_1184x26"])
        self.assertTrue(checks["referencia_202506_madura_para_6m"])

    def test_figuras(self) -> None:
        for name in [
            "A5_figura_01_trajetoria_estoque_estrato.png",
            "A5_figura_02_trajetoria_estoque_atracao.png",
            "A5_figura_03_delta_estoque_atracao.png",
            "A5_figura_04_estudo_evento_atracao.png",
        ]:
            path = OUT / name
            self.assertTrue(path.exists())
            self.assertGreater(path.stat().st_size, 5000)

    def test_escala_proporcional_e_primaria(self) -> None:
        # C2 do plano congelado: a escala proporcional passa a ser a forma
        # primaria de reportar A5, com os coeficientes registrados na auditoria
        # antes da implementacao.
        prop = pd.read_csv(OUT / "A5_tabela_08_estudo_evento_proporcional.csv", dtype={"competencia": str})
        linha = prop[(prop["amostra"] == "confirmatoria_587") & (prop["competencia"] == "202603")].iloc[0]
        self.assertEqual(round(float(linha["beta"]), 4), 0.0684)
        self.assertEqual(round(float(linha["p_valor"]), 4), 0.0002)
        escala = self.est["escala_de_reporte"]
        self.assertIn("proporcional", escala["primaria"])
        self.assertIn("nivel", escala["sensibilidade"])
        self.assertIn("fragil", escala["sensibilidade"])

    def test_leave_one_curso_do_coeficiente_de_evento(self) -> None:
        loo = pd.read_csv(OUT / "A5_tabela_09_leave_one_curso_evento.csv")
        self.assertEqual(set(loo["escala"]), {"nivel", "proporcional"})
        # 10 cursos deixados de fora, mais a amostra cheia e os 8 estritos.
        self.assertEqual(len(loo), 24)
        alvos = {
            ("nivel", "sem_curso_14", 3): 0.200,
            ("nivel", "somente_8_cbo_1_para_1", 3): 0.121,
            ("proporcional", "sem_curso_14", 4): 0.0592,
            ("proporcional", "somente_8_cbo_1_para_1", 4): 0.0570,
        }
        for (escala, subamostra, casas), alvo in alvos.items():
            linha = loo[(loo["escala"] == escala) & (loo["subamostra"] == subamostra)].iloc[0]
            self.assertEqual(round(float(linha["beta"]), casas), alvo, f"{escala}/{subamostra}")
        estritos = loo[loo["subamostra"] == "somente_8_cbo_1_para_1"]["n_cursos"].unique().tolist()
        self.assertEqual(estritos, [8])

    def test_sensibilidade_mes_de_referencia(self) -> None:
        ref = pd.read_csv(OUT / "A5_tabela_10_sensibilidade_referencia.csv")
        linha = ref[(ref["escala"] == "nivel") & (ref["referencia"] == "media_12_meses_pre")].iloc[0]
        self.assertEqual(round(float(linha["beta"]), 3), 0.405)
        self.assertEqual(round(float(linha["p_valor"]), 3), 0.174)
        # A referencia publicada continua sendo 202506 e continua na tabela.
        self.assertIn("202506", set(ref["referencia"].astype(str)))

    def test_graus_de_liberdade_contam_os_fe_absorvidos(self) -> None:
        correcao = self.est["correcao_graus_liberdade"]
        self.assertEqual(correcao["k_regressores_visiveis"], 25)
        self.assertEqual(correcao["n_parametros_fe_absorvidos"], 1547)
        self.assertEqual(round(correcao["nivel_202603_se_k_visivel"], 4), 0.2340)
        self.assertEqual(round(correcao["nivel_202603_p_k_visivel"], 4), 0.0334)
        self.assertEqual(round(correcao["nivel_202603_se_gl_fe"], 4), 0.2469)
        self.assertEqual(round(correcao["nivel_202603_p_gl_fe"], 4), 0.0437)
        evento = pd.read_csv(OUT / "A5_tabela_07_estudo_evento_atracao.csv", dtype={"competencia": str})
        for coluna in ["se_cluster_gl_fe", "p_valor_gl_fe", "ci_low_gl_fe", "ci_high_gl_fe"]:
            self.assertIn(coluna, evento.columns)

    def test_fit_absorbed_ols_sem_n_absorbed_nao_muda(self) -> None:
        # O parametro e opt-in: os scripts da versao agregada do ciclo 1 usam a
        # funcao sem ele e nao podem mudar de comportamento.
        import sys

        sys.path.insert(0, str(ROOT / "scripts" / "avaliacao_impacto"))
        from model_utils import fit_absorbed_ols

        rng = np.random.default_rng(20260909)
        n = 400
        frame = pd.DataFrame({
            "g": rng.integers(0, 20, n),
            "h": rng.integers(0, 10, n),
            "cluster": rng.integers(0, 25, n),
            "x": rng.normal(size=n),
        })
        frame["y"] = 1.5 * frame["x"] + frame["g"] * 0.1 + rng.normal(size=n)
        base, _ = fit_absorbed_ols(frame, "y", ["x"], ["g", "h"], "cluster")
        repetido, _ = fit_absorbed_ols(frame, "y", ["x"], ["g", "h"], "cluster", n_absorbed=None)
        self.assertEqual(float(base.bse["x"]), float(repetido.bse["x"]))
        n_fe = frame["g"].nunique() + frame["h"].nunique() - 1
        corrigido, diag = fit_absorbed_ols(frame, "y", ["x"], ["g", "h"], "cluster", n_absorbed=n_fe)
        fator = (n - 1) / (n - 1 - n_fe)
        self.assertEqual(float(corrigido.params["x"]), float(base.params["x"]))
        self.assertAlmostEqual(
            float(corrigido.bse["x"]) / float(base.bse["x"]), float(np.sqrt(fator)), places=12
        )
        self.assertEqual(diag["n_parametros_fe_absorvidos"], n_fe)

    def test_nomenclatura_cbo_nao_compartilhado(self) -> None:
        ponte = self.manifest["ponte_curso_cbo"]
        self.assertEqual(len(ponte["cursos_cbo_nao_compartilhado_confirmatorios"]), 10)
        self.assertEqual(ponte["n_cursos_cbo_estritamente_1_para_1"], 8)
        self.assertEqual(
            sorted(int(c) for c in ponte["cursos_nao_compartilhados_com_multiplos_cbo"]), [14, 16]
        )
        low = self.report.lower()
        self.assertIn("cbo não compartilhado entre cursos", low)
        # "Unívoco" só pode aparecer na frase que corrige o rótulo, nunca como
        # descritor da amostra confirmatória.
        for descritor in ["cursos com cbo unívoco", "ponte cbo unívoca", "dez cursos com cbo unívoco"]:
            self.assertNotIn(descritor, low)
        self.assertIn('e não "cbo unívoco"', low)

    def test_linguagem(self) -> None:
        low = self.report.lower()
        self.assertIn("associativo", low)
        self.assertIn("proibido", low)
        self.assertIn("evolução do estoque cadastral", low)
        self.assertNotIn("persistencia da oferta medica local no cnes", low)
        self.assertIn("retenção individual", low)

    # ------------------------------------------------------------------
    # Modo de reestimacao a partir do painel congelado (D-4 parcial)
    # ------------------------------------------------------------------
    def test_modo_painel_registrado_e_ancorado(self) -> None:
        # O painel mensal do CNES nao esta no repositorio (D-4). A5 passa a
        # aceitar reestimar a partir de `A5_painel_T0.parquet`, mas so com o
        # hash conferido contra o manifesto A6 e com a ausencia registrada, e
        # nunca omitida, no bloco de hashes.
        for artefato, doc in [("estimativas", self.est), ("manifesto", self.manifest)]:
            self.assertIn(doc["modo_painel"], {"construido_do_painel_mensal", "reestimado_do_painel_T0_congelado"}, artefato)
            hashes = doc["hashes_entradas"]
            painel = "output/painel_municipio_curso_mensal.parquet"
            self.assertIn(painel, hashes, artefato)
            if doc["modo_painel"] == "construido_do_painel_mensal":
                self.assertEqual(len(hashes[painel]["sha256"]), 64, artefato)
                continue
            entrada = hashes[painel]
            self.assertIsNone(entrada["sha256"], artefato)
            self.assertFalse(entrada["presente"], artefato)
            self.assertIn("D-4", entrada["motivo_ausencia"], artefato)
            # A ancora do painel que construiu o congelado nao pode se perder.
            self.assertEqual(len(entrada["sha256_registrado_em_execucao_anterior"]), 64, artefato)
            t0 = "output/tema_trabalho/A5_painel_T0.parquet"
            self.assertIn(t0, hashes, artefato)
            self.assertEqual(hashes[t0]["sha256"], sha(ROOT / t0), artefato)
            a6 = json.loads((OUT / "A6_manifesto_reproducao.json").read_text(encoding="utf-8"))
            self.assertEqual(hashes[t0]["sha256"], a6["hashes_entradas_e_artefatos"][t0]["sha256"], artefato)

    def test_reestimacao_aborta_sem_ancora_ou_com_hash_divergente(self) -> None:
        import importlib.util
        import tempfile

        spec = importlib.util.spec_from_file_location(
            "a5_provimento", ROOT / "scripts" / "tema_trabalho" / "06_avaliar_provimento_cnes.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        original = mod.MANIFESTO_A6
        try:
            with tempfile.TemporaryDirectory() as tmp:
                # Sem manifesto A6: sem ancora, o modo nao e permitido.
                mod.MANIFESTO_A6 = Path(tmp) / "inexistente.json"
                with self.assertRaises(RuntimeError):
                    mod.carregar_painel_t0_congelado()
                # Manifesto com hash diferente do arquivo em disco: aborta.
                falso = Path(tmp) / "a6.json"
                falso.write_text(json.dumps({"hashes_entradas_e_artefatos": {mod.PAINEL_T0_REL: {"sha256": "0" * 64}}}), encoding="utf-8")
                mod.MANIFESTO_A6 = falso
                with self.assertRaises(RuntimeError):
                    mod.carregar_painel_t0_congelado()
        finally:
            mod.MANIFESTO_A6 = original
        # Com o manifesto real, o painel carrega balanceado e com a mesma
        # tipagem que a construcao integral produz.
        painel = mod.carregar_painel_t0_congelado()
        self.assertEqual(len(painel), 1184 * 26)
        self.assertTrue(pd.api.types.is_string_dtype(painel["competencia"]))
        self.assertTrue(isinstance(painel["estrato"].dtype, pd.CategoricalDtype))

    # ------------------------------------------------------------------
    # A-1 / emenda 2 do plano 35: colapso de UF em macrorregiao
    # ------------------------------------------------------------------
    def test_a1_colapso_uf_em_macrorregiao_reproduz_alvos_da_emenda_2(self) -> None:
        tab = pd.read_csv(OUT / "A5_tabela_11_sensibilidade_colapso_uf.csv")
        self.assertEqual(sorted(tab["variante_uf_fe"].unique()), ["balde_unico", "macro_regiao", "sem_colapso"])
        delta = tab[tab["modelo"] == "delta_estoque_6m_minimal"].set_index("variante_uf_fe")
        alvos = {
            "balde_unico": (1.2949, 0.7749, 0.0947, 20),
            "macro_regiao": (0.5062, 0.2506, 0.0434, 24),
            "sem_colapso": (0.5002, 0.2414, 0.0382, 27),
        }
        for variante, (coef, se, p, niveis) in alvos.items():
            linha = delta.loc[variante]
            self.assertEqual(round(float(linha["coef"]), 4), coef, variante)
            self.assertEqual(round(float(linha["se_cluster"]), 4), se, variante)
            self.assertEqual(round(float(linha["p_valor"]), 4), p, variante)
            self.assertEqual(int(linha["n_niveis_uf_fe"]), niveis, variante)
        self.assertTrue(bool(delta.loc["macro_regiao", "primaria"]))
        self.assertFalse(bool(delta.loc["balde_unico", "primaria"]))

    def test_a1_variante_primaria_e_a_do_c1(self) -> None:
        fe = self.est["efeito_fixo_uf"]
        self.assertEqual(fe["variante_primaria"], "macro_regiao")
        self.assertEqual(fe["n_niveis_amostra_confirmatoria"], 24)
        self.assertEqual(fe["nivel_residual"], "MACRO_SEM_REGIAO_SAUDE")
        self.assertEqual(len(fe["ufs_colapsadas"]), 8)
        # O balde RESTO saiu das duas implementacoes: painel e tabela de UF.
        conf = self.cross[self.cross["amostra_confirmatoria"]]
        self.assertNotIn("RESTO", set(conf["uf_fe"].astype(str)))
        self.assertEqual(conf["uf_fe"].nunique(), 24)
        self.assertIn("MACRO_SEM_REGIAO_SAUDE", set(conf["uf_fe"].astype(str)))
        uf_tab = pd.read_csv(OUT / "A5_tabela_01e_amostra_uf.csv")
        self.assertNotIn("RESTO", set(uf_tab["uf_fe"].astype(str)))
        self.assertEqual(int(uf_tab["colapsada"].sum()), 8)
        # O delta_minimal publicado na tabela 03b e a variante primaria.
        t03b = pd.read_csv(OUT / "A5_tabela_03b_modelo_delta_estoque.csv")
        sel = t03b[(t03b["espec"] == "OLS_delta_estoque_minimal") & (t03b["termo"] == "atracao_muni")]
        self.assertEqual(round(float(sel["coef"].iloc[0]), 4), 0.5062)

    def test_a1_estudo_de_evento_nao_e_afetado(self) -> None:
        # A manchete de A5 absorve UF-mes com as 27 UFs e nao passa por uf_fe.
        prop = self.est["modelos"]["principal_proporcional_confirmatorio"]
        self.assertEqual(round(prop["mar2026_beta"], 4), 0.0684)
        nivel = self.est["modelos"]["principal_dinamico_confirmatorio"]
        self.assertEqual(round(nivel["mar2026_beta"], 3), 0.5)

    # ------------------------------------------------------------------
    # Sessao 4 do backlog: B-1, B-2, B-5, B-6 e C-9
    # ------------------------------------------------------------------
    def test_b1_censura_de_presentes_6m_nao_e_zero(self) -> None:
        # A coorte do follow (202603) nao tem seis meses observados; a coluna
        # tem de ser NaN com marcador, nunca zero.
        self.assertFalse(self.cross["coorte_6m_madura"].astype(bool).any())
        self.assertTrue(self.cross["presentes_6m"].isna().all())
        self.assertTrue(self.cross["presentes_6m_censurado"].astype(bool).all())
        self.assertTrue(self.manifest["checks"]["presentes_6m_censura_gravada_como_nan_nao_zero"])
        # A presenca modelada vem da coorte madura da referencia.
        self.assertTrue(self.cross["coorte_madura_baseline"].astype(bool).all())
        self.assertFalse(self.cross["presentes_baseline_6m"].isna().any())

    def test_b2_relatorio_promovido_sem_texto_obsoleto(self) -> None:
        for secao in ["Construção, maturidade e censura", "Trajetória agregada", "Influência e robustez", "Multiplicidade", "Limites"]:
            self.assertIn(secao, self.report, secao)
        # Texto obsoleto do bloco morto nao pode ter sido promovido.
        self.assertNotIn("202509 baseline", self.report)
        self.assertNotIn("FE curso (16)", self.report)
        self.assertNotIn("G=368", self.report)
        self.assertIn("587 células", self.report)

    def test_b5_multiplicidade_declarada_e_publicada(self) -> None:
        mult = self.est["multiplicidade"]
        self.assertEqual(len(mult["familias_corte_transversal"]), 10)
        for fam in ["minimal_5_desfechos", "full_5_desfechos"]:
            self.assertEqual(sum(f["familia"] == fam for f in mult["familias_corte_transversal"]), 5)
        for tabela in ["A5_tabela_07_estudo_evento_atracao.csv", "A5_tabela_08_estudo_evento_proporcional.csv"]:
            ev = pd.read_csv(OUT / tabela, dtype={"competencia": str})
            for col in ["q_fdr_bh", "q_fdr_bh_gl_fe", "familia_fdr"]:
                self.assertIn(col, ev.columns, tabela)
            est = ev[~ev["referencia"].astype(bool)]
            self.assertFalse(est["q_fdr_bh_gl_fe"].isna().any(), tabela)
            self.assertTrue((est["q_fdr_bh_gl_fe"] >= est["p_valor_gl_fe"] - 1e-12).all(), tabela)
            self.assertTrue(ev.loc[ev["referencia"].astype(bool), "q_fdr_bh"].isna().all(), tabela)
        # q de manchete: a escala proporcional sobrevive a familia de 25; a de nivel nao.
        self.assertLess(mult["mar2026_q_fdr_bh_gl_fe_proporcional_confirmatoria"], 0.01)
        self.assertGreater(mult["mar2026_q_fdr_bh_gl_fe_nivel_confirmatoria"], 0.05)
        # q_fdr_atracao deixou de sair NaN nas tabelas de corte transversal.
        t03b = pd.read_csv(OUT / "A5_tabela_03b_modelo_delta_estoque.csv")
        atr = t03b[t03b["termo"] == "atracao_muni"]
        self.assertFalse(atr["q_fdr_atracao"].isna().any())
        self.assertTrue((atr["q_fdr_atracao"] >= atr["p_valor"] - 1e-12).all())

    def test_b6_rotulo_da_janela_antiga_descreve_a_janela_real(self) -> None:
        t03f = pd.read_csv(OUT / "A5_tabela_03f_sensibilidade_T0_alternativo.csv")
        self.assertEqual(set(t03f["espec"]), {"OLS_delta_T0alt_202509_202603_minimal"})
        timing = self.manifest["t0"]
        self.assertEqual((timing["alt_baseline"], timing["alt_follow"]), ("202509", "202603"))

    def test_c9_delta_full_e_estoque_full_sao_um_estimador(self) -> None:
        d = self.est["modelos"]["delta_full"]
        e = self.est["modelos"]["estoque_6m_full"]
        self.assertEqual(d["equivalente_a"], "estoque_6m_full")
        self.assertEqual(e["equivalente_a"], "delta_full")
        self.assertAlmostEqual(d["coef_atracao"], e["coef_atracao"], places=10)
        t03b = pd.read_csv(OUT / "A5_tabela_03b_modelo_delta_estoque.csv")
        nota = t03b.loc[(t03b["espec"] == "OLS_delta_full") & (t03b["termo"] == "atracao_muni"), "nota"].iloc[0]
        self.assertIn("Frisch-Waugh-Lovell", str(nota))

    # ------------------------------------------------------------------
    # C-7: placebo, pre-tendencia por curso e deslocamento (protocolo congelado)
    # ------------------------------------------------------------------
    def test_c7_artefato_segue_o_protocolo_congelado(self) -> None:
        c7 = json.loads((OUT / "A5_ameacas_c7.json").read_text(encoding="utf-8"))
        self.assertIn("antes da execucao", c7["protocolo_congelado_em"])
        # Ancora no painel congelado e no A6.
        self.assertEqual(c7["hashes_entradas"]["output/tema_trabalho/A5_painel_T0.parquet"]["sha256"], sha(OUT / "A5_painel_T0.parquet"))
        self.assertEqual(c7["amostra"]["celulas_confirmatorias"], 587)
        # Placebo: 372 celulas sem atracao, divididas por municipio com/sem atracao.
        pl = c7["placebo"]["resultado"]
        for esc in ("nivel", "proporcional"):
            self.assertEqual(pl[esc]["n_tratadas"] + pl[esc]["n_controle"], 372, esc)
            self.assertEqual(pl[esc]["n_coef_pre"], 12)
        # Pre-tendencia: dez cursos, regra de exclusao aplicada como declarada.
        pre = c7["pretendencia_por_curso"]
        self.assertEqual(len(pre["por_curso"]), 10)
        rej = pre["cursos_pre_p_lt_0_05_proporcional"]
        for c, esc in pre["por_curso"].items():
            self.assertEqual(int(c) in rej, esc["proporcional"]["pre_p_gl_fe"] < 0.05, c)
            self.assertIn("pre_F_confiavel", esc["proporcional"])
        if rej:
            sens = pre["sensibilidade_excluindo_cursos_rejeitados"]["proporcional"]
            self.assertLess(sens["n_unidades"], 587)
        # Amostra completa reproduz a manchete de A5 nas duas escalas.
        self.assertAlmostEqual(pre["amostra_completa"]["proporcional"]["mar2026_beta"], self.est["modelos"]["principal_proporcional_confirmatorio"]["mar2026_beta"], places=10)
        self.assertAlmostEqual(pre["amostra_completa"]["nivel"]["mar2026_beta"], self.est["modelos"]["principal_dinamico_confirmatorio"]["mar2026_beta"], places=10)
        # Deslocamento: duas definicoes, limite declarado, cluster por regiao em (b).
        ds = c7["deslocamento"]
        self.assertIn("dentro do quadro", ds["limite"])
        self.assertEqual(ds["oferta_liquida_regional"]["nivel"]["n_clusters"], ds["n_regioes"])
        self.assertEqual(ds["transbordo"]["nivel"]["n_tratadas"] + ds["transbordo"]["nivel"]["n_controle"], 372)
        for tabela in ["A5_tabela_12_placebo_municipio_com_atracao.csv", "A5_tabela_13_pretendencia_por_curso.csv", "A5_tabela_14_deslocamento_regional.csv"]:
            self.assertTrue((OUT / tabela).exists(), tabela)

    # ---- Revisao da PR 3 depois do merge (21/09/2026) ----

    def test_a1b_tabela_11_cobre_as_duas_especificacoes(self) -> None:
        # A emenda 2 publicou so os cinco `minimal`, mas a definicao de uf_fe
        # move tambem a `full`: sem as linhas `full` a consequencia da decisao
        # de A-1 nao fica auditavel no artefato. Ver errata E-7.
        tab = pd.read_csv(OUT / "A5_tabela_11_sensibilidade_colapso_uf.csv")
        self.assertEqual(sorted(tab["espec"].unique()), ["full", "minimal"])
        self.assertEqual(len(tab), 30, "3 variantes x 2 especificacoes x 5 desfechos")
        for espec in ("minimal", "full"):
            for variante in ("balde_unico", "macro_regiao", "sem_colapso"):
                sel = tab[(tab["espec"] == espec) & (tab["variante_uf_fe"] == variante)]
                self.assertEqual(len(sel), 5, f"{espec}/{variante}")
        # A cifra que a errata E-7 declara: o `full` saiu de p=0,791 para p=0,094.
        full = tab[(tab["modelo"] == "estoque_6m_full")].set_index("variante_uf_fe")
        self.assertEqual(round(float(full.loc["balde_unico", "p_valor"]), 3), 0.791)
        self.assertEqual(round(float(full.loc["macro_regiao", "p_valor"]), 3), 0.094)

    def test_a1b_singletons_nao_movem_coeficiente_mas_inflam_r2(self) -> None:
        # Nivel de efeito fixo com uma unica celula e ajustado exatamente: nao
        # identifica nada, mas conta em `n` e no R2. Ver errata E-8.
        tab = pd.read_csv(OUT / "A5_tabela_15_singletons_efeito_fixo.csv")
        self.assertEqual(sorted(tab["singletons"].unique()), ["mantidos", "removidos"])
        mant = tab[tab["singletons"] == "mantidos"].set_index(["modelo"])
        remo = tab[tab["singletons"] == "removidos"].set_index(["modelo"])
        self.assertEqual(sorted(mant.index), sorted(remo.index))
        for modelo in mant.index:
            self.assertAlmostEqual(float(mant.loc[modelo, "coef"]), float(remo.loc[modelo, "coef"]), places=4,
                                   msg=f"{modelo}: remover singleton nao pode mover o coeficiente")
        # O que muda e o ajuste, nao a estimativa.
        self.assertGreater(float(mant.loc["estoque_6m_minimal", "r2"]), 0.8)
        self.assertLess(float(remo.loc["estoque_6m_minimal", "r2"]), 0.3)
        self.assertEqual(int(mant.loc["estoque_6m_minimal", "n"]) - int(remo.loc["estoque_6m_minimal", "n"]),
                         int(remo.loc["estoque_6m_minimal", "n_celulas_removidas"]))
        # A especificacao primaria continua sendo a que mantem os singletons.
        self.assertTrue(bool(mant.loc["estoque_6m_minimal", "primaria"]))
        self.assertFalse(bool(remo.loc["estoque_6m_minimal", "primaria"]))

    def test_a1b_json_e_tabela_06_declaram_o_n_efetivo(self) -> None:
        bloco = self.est["singletons_efeito_fixo"]
        self.assertEqual(bloco["n_nominal"] - bloco["n_efetivo"], bloco["n_celulas_removidas"])
        self.assertGreater(bloco["n_celulas_removidas"], 0)
        # Brasilia domina a soma de quadrados do estoque; e por isso que o R2 salta.
        self.assertGreater(bloco["peso_na_soma_de_quadrados_por_desfecho"]["estoque_6m"], 0.8)
        pred = pd.read_csv(OUT / "A5_tabela_06_validacao_preditiva.csv").set_index("modelo")
        for col in ("n_efetivo", "r2_insample_sem_singletons", "rmse_insample_sem_singletons"):
            self.assertIn(col, pred.columns)
        self.assertLess(float(pred.loc["OLS_estoque_6m_minimal", "r2_insample_sem_singletons"]),
                        float(pred.loc["OLS_estoque_6m_minimal", "r2_insample"]))
        self.assertIn("singleton", self.report)

    def test_c7b_multiplicidade_na_triagem_de_pretendencia(self) -> None:
        # O item B-5 declarou duas familias de FDR e deixou de fora a triagem
        # por curso, que e justamente a que governa a regra de exclusao.
        c7 = json.loads((OUT / "A5_ameacas_c7.json").read_text(encoding="utf-8"))
        mult = c7["pretendencia_por_curso"]["multiplicidade"]
        self.assertEqual(mult["alpha"], 0.05)
        q_prop = mult["q_por_curso"]["proporcional"]
        self.assertEqual(len(q_prop), 10)
        # O q nunca pode ser menor que o p do mesmo curso.
        por_curso = c7["pretendencia_por_curso"]["por_curso"]
        for curso, q in q_prop.items():
            self.assertGreaterEqual(q + 1e-12, por_curso[curso]["proporcional"]["pre_p_gl_fe"], curso)
        # A regra de exclusao continua sobre o p cru, e o q e apenas leitura.
        self.assertEqual(c7["pretendencia_por_curso"]["cursos_pre_p_lt_0_05_proporcional"], [2, 16])
        self.assertEqual(mult["cursos_q_lt_0_05_proporcional"], [16])
        tab = pd.read_csv(OUT / "A5_tabela_13_pretendencia_por_curso.csv")
        self.assertIn("q_fdr_bh_pre", tab.columns)

    def test_c7c_oferta_liquida_regional_decomposta(self) -> None:
        # O teste (b) so distingue oferta liquida de oferta da celula onde a
        # regiao-curso agrega mais de um municipio do painel.
        c7 = json.loads((OUT / "A5_ameacas_c7.json").read_text(encoding="utf-8"))
        ds = c7["deslocamento"]
        dec = ds["decomposicao_oferta_liquida"]
        self.assertEqual(dec["n_regiao_curso_multi_municipio"] + dec["n_regiao_curso_um_municipio"],
                         ds["n_regiao_curso"])
        self.assertEqual(dec["multi_municipio"]["proporcional"]["n_unidades"],
                         dec["n_regiao_curso_multi_municipio"])
        # A maior parte das regiao-curso nao agrega nada, e e de la que vem o p.
        self.assertGreater(dec["n_regiao_curso_um_municipio"], dec["n_regiao_curso_multi_municipio"])
        self.assertLess(ds["oferta_liquida_regional"]["proporcional"]["mar2026_p_gl_fe"], 0.05)
        self.assertGreater(dec["multi_municipio"]["proporcional"]["mar2026_p_gl_fe"], 0.05)
        # A configuracao em que realocacao e observavel e ainda mais rara.
        self.assertLessEqual(ds["n_regiao_curso_com_municipio_atraido_e_nao_atraido"],
                             dec["n_regiao_curso_multi_municipio"])
        tab = pd.read_csv(OUT / "A5_tabela_14_deslocamento_regional.csv")
        self.assertEqual(sorted(tab["subamostra"].dropna().unique()),
                         ["agregam_mais_de_um_municipio", "todas", "um_unico_municipio"])


if __name__ == "__main__":
    unittest.main()
