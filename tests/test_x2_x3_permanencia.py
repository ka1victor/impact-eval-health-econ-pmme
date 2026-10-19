"""Testes do X2 e do X3 (`scripts/rdd_bolsa/18_permanencia_ativos.py`), protocolo exploratório 45.

Duas partes:

1. Classes `...Sintetico...`: lógica de ligação, consolidação, agregação,
   completude e estimação com DADOS SINTÉTICOS gerados em memória (semente
   fixa). Nada é gravado em `output/` nem em `data/`; os dados sintéticos só
   conferem que o código recupera valores conhecidos.
2. `TestSaidasReais`: invariantes das saídas versionadas em
   `output/rdd_bolsa/X2_*` e `X3_*`. Todo alvo é lido de `output/` ou de
   `data/` (somente leitura) ou recalculado de forma independente; nenhum
   número é digitado aqui. Nomes e CRM só existem em memória dentro do teste
   de ausência de dados pessoais.
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
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "18_permanencia_ativos.py"
_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location("x2x3_permanencia_18", SCRIPT)
X = importlib.util.module_from_spec(_spec)
sys.modules["x2x3_permanencia_18"] = X
_spec.loader.exec_module(X)
sys.dont_write_bytecode = _bytecode

OUT = ROOT / "output" / "rdd_bolsa"
DOC = ROOT / "docs" / "06_execucao" / "46_resultados_exploratorios_pos_sintese.md"
SAIDAS_CSV = ["X2_pessoas", "X2_celulas", "X2_municipios", "X2_descritivo", "X2_motivos_ligacao", "X2_estimativas",
              "X3_painel_municipio_curso_mes", "X3_painel_municipio_mes", "X3_municipio", "X3_completude",
              "X3_descritivo", "X3_estimativas"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


# --------------------------------------------------------------------------
# Dados sintéticos (só em memória)
# --------------------------------------------------------------------------

def pessoas_sinteticas() -> pd.DataFrame:
    """Alocados sintéticos: cada linha exercita um ramo da regra de ligação."""
    linhas = [
        ("ANA SOUZA LIMA", 1, "100001", "0000001", 1, False),        # exato e único -> LIGADO
        ("BRUNO COSTA", 2, "100001", "0000001", 1, False),           # chave repetida entre alocados
        ("BRUNO COSTA", 2, "100001", "0000002", 2, False),           # (mesma chave, outro ciclo)
        ("CARLA DIAS", 3, "100002", "0000003", 1, False),            # chave repetida na lista de ativos
        ("DANIEL ROCHA PINTO", 4, "100002", "0000004", 2, False),    # grafia próxima -> INCERTO
        ("EVA MARIA NUNES", 5, "100003", "0000005", 2, False),       # mesmo 1o nome + 2 partes -> INCERTO
        ("FABIO REIS", 6, "100003", "0000006", 1, False),            # nome+curso em outro município
        ("GABI MOTA", 7, "100004", "0000007", 2, False),             # nome em outro curso
        ("HUGO SILVA", 8, "100004", "0000008", 1, False),            # sem correspondente
        ("IARA LEAL", 9, "100005", "0000009", 2, True),              # ambígua na alocação
    ]
    p = pd.DataFrame(linhas, columns=["_nome", "cod_curso", "co_ibge", "co_cnes_7d", "ciclo", "ambiguo_alocacao"])
    p["motivo_alocacao"] = np.where(p["ambiguo_alocacao"], "homonimos", "")
    return p


def ativos_sinteticos() -> pd.DataFrame:
    linhas = [
        ("ANA SOUZA LIMA", 1, "100001", "0000001", 1),
        ("BRUNO COSTA", 2, "100001", "0000001", 2),
        ("CARLA DIAS", 3, "100002", "0000003", 1),
        ("CARLA DIAS", 3, "100002", "0000099", 1),
        ("DANIEL ROCHA PINTU", 4, "100002", "0000004", 2),
        ("EVA NUNES CARDOSO", 5, "100003", "0000005", 2),
        ("FABIO REIS", 6, "999999", "0000555", 1),
        ("GABI MOTA", 11, "100004", "0000007", 2),
        ("IARA LEAL", 9, "100005", "0000009", 2),
    ]
    return pd.DataFrame(linhas, columns=["_nome", "cod_curso", "co_ibge", "co_cnes_7d", "ciclo_k"])


class TestLigacaoSintetico(unittest.TestCase):
    """Regra de ligação com dados sintéticos."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.lig = X.ligar(pessoas_sinteticas(), ativos_sinteticos()).set_index("_nome", drop=False)

    def _st(self, nome: str) -> pd.DataFrame:
        return self.lig.loc[[nome]]

    def test_exato_unico_liga(self) -> None:
        r = self._st("ANA SOUZA LIMA").iloc[0]
        self.assertEqual(r["status_ligacao"], "LIGADO")
        self.assertEqual(r["ativo"], 1.0)
        self.assertEqual(r["cnes_igual"], 1.0)
        self.assertEqual(r["ciclo_igual"], 1.0)

    def test_chave_repetida_entre_alocados_e_ambigua(self) -> None:
        g = self._st("BRUNO COSTA")
        self.assertEqual(set(g["status_ligacao"]), {"AMBIGUO"})
        self.assertTrue(g["ativo"].isna().all())

    def test_chave_repetida_na_lista_de_ativos_e_ambigua(self) -> None:
        r = self._st("CARLA DIAS").iloc[0]
        self.assertEqual(r["status_ligacao"], "AMBIGUO")
        self.assertIn("lista de ativos", r["motivo_ligacao"])

    def test_grafia_proxima_e_incerta(self) -> None:
        for nome in ("DANIEL ROCHA PINTO", "EVA MARIA NUNES"):
            r = self._st(nome).iloc[0]
            self.assertEqual(r["status_ligacao"], "INCERTO", nome)
            self.assertTrue(np.isnan(r["ativo"]))

    def test_regra_estreita_nao_usa_partes_do_nome(self) -> None:
        lig = X.ligar(pessoas_sinteticas(), ativos_sinteticos(), partes=False).set_index("_nome")
        self.assertEqual(lig.at["DANIEL ROCHA PINTO", "status_ligacao"], "INCERTO")      # similaridade
        self.assertEqual(lig.at["EVA MARIA NUNES", "status_ligacao"], "NAO_LIGADO")      # só partes
        self.assertEqual(lig.at["EVA MARIA NUNES", "ativo"], 0.0)

    def test_motivos_de_nao_ligacao(self) -> None:
        r = self._st("FABIO REIS").iloc[0]
        self.assertEqual((r["status_ligacao"], r["ativo"], r["ativo_no_programa"]), ("NAO_LIGADO", 0.0, 1.0))
        self.assertIn("outro municipio", r["motivo_ligacao"])
        r = self._st("GABI MOTA").iloc[0]
        self.assertIn("outro curso", r["motivo_ligacao"])
        r = self._st("HUGO SILVA").iloc[0]
        self.assertEqual((r["status_ligacao"], r["ativo"], r["ativo_no_programa"]), ("NAO_LIGADO", 0.0, 0.0))

    def test_ambigua_na_alocacao_fica_fora_mesmo_com_chave_exata(self) -> None:
        r = self._st("IARA LEAL").iloc[0]
        self.assertEqual(r["status_ligacao"], "AMBIGUO")
        self.assertTrue(r["motivo_ligacao"].startswith("alocacao"))

    def test_mesmo_ativo_nao_liga_a_dois_alocados(self) -> None:
        p = pessoas_sinteticas().iloc[[0]].copy()
        p2 = p.assign(co_cnes_7d="0000077")
        dois = pd.concat([p, p2], ignore_index=True)
        lig = X.ligar(dois, ativos_sinteticos())
        self.assertEqual(set(lig["status_ligacao"]), {"AMBIGUO"})


class TestConsolidacaoSintetico(unittest.TestCase):
    """Consolidação de eventos em pessoas com dados sintéticos."""

    def eventos(self) -> pd.DataFrame:
        return pd.DataFrame([
            # confirmada numa célula e homologada noutra: célula final = homologação
            (1, "confirmacao", 1, "P UM", "111", "0000001", 1, "100001"),
            (1, "homologacao", 2, "P UM", "111b", "0000002", 1, "100002"),
            # só confirmada
            (1, "confirmacao", 1, "P DOIS", "222", "0000003", 2, "100003"),
            # homônimos no mesmo arquivo
            (2, "alocacao", 1, "P TRES", "333", "0000004", 3, None),
            (2, "alocacao", 1, "P TRES", "334", "0000005", 3, None),
        ], columns=["ciclo", "evento", "prioridade", "_nome", "_cpf", "co_cnes_7d", "cod_curso", "co_ibge_arquivo"])

    def test_celula_final_trilha_homonimos_e_pseudonimo(self) -> None:
        p, diag = X.consolidar_pessoas(self.eventos())
        um = p[p["_nome"] == "P UM"].iloc[0]
        self.assertEqual((um["co_cnes_7d"], um["evento_final"]), ("0000002", "homologacao"))
        self.assertEqual(diag["trilha_ciclo1"], {"homologado_em_outra_celula": 1, "confirmado_sem_homologacao": 1})
        tres = p[p["_nome"] == "P TRES"].iloc[0]
        self.assertTrue(tres["ambiguo_alocacao"])
        self.assertTrue(p["id_pessoa"].str.fullmatch(r"x2_c[12]_\d{4}").all())
        p2, _ = X.consolidar_pessoas(self.eventos().sample(frac=1.0, random_state=3))
        self.assertEqual(dict(zip(p["_nome"], p["id_pessoa"])), dict(zip(p2["_nome"], p2["id_pessoa"])))
        for c in p["id_pessoa"]:
            self.assertNotIn("P ", c)


class TestAgregacaoSintetico(unittest.TestCase):
    """Agregação por célula e município com dados sintéticos."""

    def test_fracoes_selecao_e_motivos(self) -> None:
        cel = pd.DataFrame({"ciclo": 1, "co_cnes_7d": ["A", "B", "C", "D"], "cod_curso": 1,
                            "co_ibge": ["m1", "m1", "m2", "m2"], "s_mil": [290.0, 290.0, 310.0, 310.0],
                            "faixa_anunciada": "x"})
        pes = pd.DataFrame({"ciclo": 1, "co_cnes_7d": ["A", "A", "A", "C"], "cod_curso": 1,
                            "celula_no_quadro": True, "ativo": [1.0, 0.0, np.nan, np.nan]})
        c = X.agregar_celulas(pes, cel).set_index("co_cnes_7d")
        self.assertAlmostEqual(c.at["A", "x2_frac_ativos_celula"], 0.5)
        self.assertEqual(c.at["A", "x2_celula_com_alocado_ativo"], 1.0)
        self.assertEqual(c.at["B", "x2_celula_com_alocado_ativo"], 0.0)
        self.assertTrue(np.isnan(c.at["B", "x2_frac_ativos_celula"]))
        self.assertTrue(np.isnan(c.at["C", "x2_celula_com_alocado_ativo"]))
        self.assertEqual(int(c.at["C", "so_excluidos"]), 1)
        self.assertIn("sem alocado", json.loads(c.at["B", "motivos_ausencia"])["x2_frac_ativos_celula"])
        m = X.agregar_municipios(c.reset_index()).set_index("co_ibge")
        self.assertAlmostEqual(m.at["m1", "x2_frac_ativos_municipio"], 0.5)
        self.assertTrue(np.isnan(m.at["m1", "x2_alocados_ativos_por_celula"]))   # m1 tem um excluído
        self.assertEqual(int(m.at["m2", "so_excluidos"]), 1)


def serie_sintetica(remover: tuple[str, str] | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Série sintética coerente com um retrato: 3 meses, 3 municípios."""
    retrato = pd.DataFrame({"co_ibge": ["100001", "100001", "100002", "100003"], "cod_curso": [1, 1, 2, 1],
                            "dt_inicio": pd.to_datetime(["2025-09-01", "2026-02-10", "2025-09-01", "2026-03-15"])})
    linhas = []
    for mes in ("2026-01", "2026-02", "2026-03"):
        ini = pd.Timestamp(f"{mes}-01")
        for (mun, cur), g in retrato.groupby(["co_ibge", "cod_curso"]):
            n = int((g["dt_inicio"] < ini).sum()) + (1 if (mun == "100002" and mes != "2026-03") else 0)
            if n and (mun, mes) != remover:
                linhas.append({"co_ibge": mun, "cod_curso": cur, "mes": mes, "ativos": n})
    linhas.append({"co_ibge": "100003", "cod_curso": 1, "mes": "2026-03", "ativos": 1})
    return pd.DataFrame(linhas), retrato


class TestSerieSintetico(unittest.TestCase):
    """Completude e outcomes do X3 com dados sintéticos."""

    def test_listagem_completa_passa_e_preenche_zero(self) -> None:
        painel, retrato = serie_sintetica()
        tab, comp = X.verificar_completude(painel, retrato)
        self.assertTrue(comp["ultimo_mes_reproduz_retrato_nominal"])
        self.assertTrue(comp["listagem_completa_em_todos_os_meses"])
        rv = pd.DataFrame({"co_ibge": ["100001", "100002", "100003", "100004"], "s_mil": [290.0, 310, 320, 330]})
        pop = pd.Series(10_000.0, index=rv["co_ibge"])
        pm, mun = X.outcomes_x3(painel, rv, pop, completa=True, ultimo_completo=True, universo=pd.Index(rv["co_ibge"]))
        self.assertEqual(len(pm), 4 * 3)
        self.assertEqual(float(pm.loc[pm["co_ibge"] == "100004", "ativos"].sum()), 0.0)
        m = mun.set_index("co_ibge")
        self.assertEqual(m.at["100002", "x3_queda_pico_ultimo"], 1.0)           # 2 -> 1
        self.assertAlmostEqual(m.at["100002", "x3_queda_relativa"], 0.5)
        self.assertTrue(np.isnan(m.at["100004", "x3_queda_pico_ultimo"]))      # sem ativo: fora
        self.assertEqual(m.at["100001", "x3_meses_com_ativo"], 3)

    def test_listagem_incompleta_falha_e_restringe(self) -> None:
        painel, retrato = serie_sintetica(remover=("100001", "2026-02"))
        tab, comp = X.verificar_completude(painel, retrato)
        self.assertFalse(comp["listagem_completa_em_todos_os_meses"])
        self.assertIn("2026-02", comp["meses_com_violacao"])
        self.assertNotIn("2026-02", comp["meses_sem_municipio_da_cota_ausente"])
        rv = pd.DataFrame({"co_ibge": ["100001", "100002", "100003"], "s_mil": [290.0, 310, 320]})
        pop = pd.Series(10_000.0, index=rv["co_ibge"])
        pm, mun = X.outcomes_x3(painel, rv, pop, completa=False, ultimo_completo=True,
                                meses_sensibilidade=comp["meses_sem_municipio_da_cota_ausente"])
        self.assertFalse(((pm["co_ibge"] == "100001") & (pm["mes"] == "2026-02")).any())  # ausência não vira zero
        m = mun.set_index("co_ibge")
        self.assertEqual(m.at["100001", "meses_listados"], 2)
        self.assertIn("x3s_queda_pico_ultimo", mun.columns)

    def test_ultimo_mes_divergente_falha(self) -> None:
        painel, retrato = serie_sintetica()
        painel.loc[painel["mes"] == "2026-03", "ativos"] += 1
        _, comp = X.verificar_completude(painel, retrato)
        self.assertFalse(comp["ultimo_mes_reproduz_retrato_nominal"])
        self.assertFalse(comp["listagem_completa_em_todos_os_meses"])

    def test_competencia(self) -> None:
        self.assertEqual(X.competencia_iso("dez/25"), "2025-12")
        with self.assertRaises(X.FalhaValidacao):
            X.competencia_iso("13/25")


class TestEstimacaoSintetico(unittest.TestCase):
    """O X2 recupera um salto conhecido (dados sintéticos, semente fixa)."""

    def test_recupera_salto_e_sinal(self) -> None:
        rng = np.random.default_rng(20261019)
        salto = 0.3
        cels, muns = [], []
        for k in (1, 2):
            s = rng.integers(240, 461, 300).astype(float)
            for i, si in enumerate(s):
                t = float((250 < si <= 350 and si > 300) or si > 400)
                y = 0.4 + salto * t + rng.normal(0, 0.05)
                cels.append({"ciclo": k, "co_ibge": f"{k}{i:05d}", "s_mil": si, "x2_frac_ativos_celula": y,
                             "selecionada": 1, "x2_celula_com_alocado_ativo": y})
                muns.append({"ciclo": k, "co_ibge": f"{k}{i:05d}", "s_mil": si, "x2_frac_ativos_municipio": y,
                             "selecionado": 1, "x2_alocados_ativos_por_celula": y})
        est = X.estimar_x2(pd.DataFrame(cels), pd.DataFrame(muns))
        r = est[(est["outcome_id"] == "X2.2") & (est["especificacao"] == "ciclos_e_cortes_empilhados")].iloc[0]
        self.assertLess(abs(r["tau"] - salto), 4 * r["ep"])
        self.assertGreater(r["tau"], 0)
        self.assertTrue((est["estatuto"] == X.ESTATUTO).all())
        self.assertTrue((est["natureza_dos_dados"] == "EMPIRICO").all())
        lee = est[(est["especificacao"] == "limites_lee") & (est["status"] == "EXECUTADO")]
        self.assertTrue(lee["p_valor"].isna().all())
        self.assertTrue(est.loc[est["entra_bky"], "q_bky"].notna().all())


# --------------------------------------------------------------------------
# Saídas reais
# --------------------------------------------------------------------------

class TestSaidasReais(unittest.TestCase):
    """Invariantes das saídas X2 e X3 versionadas."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.csv = {n: pd.read_csv(OUT / f"{n}.csv", dtype={"co_ibge": str, "co_cnes_7d": str, "ciclo": str,
                                                           "corte": str, "mes": str}, low_memory=False)
                   for n in SAIDAS_CSV}
        cls.r2 = json.loads((OUT / "X2_resumo.json").read_text(encoding="utf-8"))
        cls.r3 = json.loads((OUT / "X3_resumo.json").read_text(encoding="utf-8"))

    def test_rotulos_em_toda_linha(self) -> None:
        for n, df in self.csv.items():
            self.assertTrue((df["natureza_dos_dados"] == "EMPIRICO").all(), n)
            self.assertTrue((df["estatuto"] == "EXPLORATORIO_POS_SINTESE").all(), n)
        for r in (self.r2, self.r3):
            self.assertEqual((r["natureza_dos_dados"], r["estatuto"]), ("EMPIRICO", "EXPLORATORIO_POS_SINTESE"))

    def test_hashes_de_saidas_e_entradas(self) -> None:
        for r in (self.r2, self.r3):
            for nome, h in r["saidas"].items():
                self.assertEqual(sha256(OUT / nome), h, nome)
            for e in r["entradas"]:
                self.assertEqual(sha256(ROOT / e["caminho"]), e["sha256"], e["caminho"])
                for chave in ("data_referencia", "cobertura", "unidade", "chaves", "filtros"):
                    self.assertTrue(e[chave], (e["caminho"], chave))
                self.assertNotIn("ivs_ipea_2010_municipios", e["caminho"])

    def test_sem_dados_pessoais(self) -> None:
        proibidas = re.compile(r"(^|_)(nome|cpf|crm)($|_)", re.I)
        for n, df in self.csv.items():
            self.assertFalse([c for c in df.columns if proibidas.search(c)], n)
        at = X.ler_ativos_nominais()
        nomes = set(at["set"]["_nome"]) | set(at["ago"]["_nome"])
        crms = {c for c in set(at["set"]["_crm"]) | set(at["ago"]["_crm"]) if len(c) >= 4}
        for n in ("X2_pessoas", "X2_celulas", "X2_motivos_ligacao"):
            valores = set(self.csv[n].astype(str).to_numpy().ravel())
            self.assertFalse(valores & nomes, n)
        self.assertFalse(set(self.csv["X2_pessoas"]["id_pessoa"]) & crms)
        self.assertTrue(self.csv["X2_pessoas"]["id_pessoa"].str.fullmatch(r"x2_c[12]_\d{4}").all())
        self.assertFalse(self.csv["X2_pessoas"]["id_pessoa"].duplicated().any())

    def test_ativos_e_o_arquivo_do_e3(self) -> None:
        self.assertEqual(sha256(X.ATIVOS_ZIP), X.B.SHA256_ATIVOS_PROTOCOLO)

    def test_running_variable_e_a08(self) -> None:
        a08 = pd.read_csv(ROOT / "output" / "aquisicao" / "a08_ivs_2010_oficial_municipio.csv", dtype={"co_ibge": str})
        mapa = dict(zip(a08["co_ibge"].str[:6], np.round(a08["ivs"].astype(float) * 1000)))
        for n in ("X2_celulas", "X2_municipios", "X3_municipio"):
            d = self.csv[n]
            d = d[d["s_mil"].notna()]
            self.assertTrue(np.allclose(d["s_mil"].astype(float), d["co_ibge"].map(mapa).astype(float)), n)

    def test_x2_reproduz_contagens_da_tarefa_b(self) -> None:
        vc = pd.read_parquet(ROOT / "output" / "rdd_bolsa" / "outcomes" / "outcomes_V_celula.parquet")
        vc = vc[vc["ciclo"] == 2]
        cel = self.csv["X2_celulas"]
        cel = cel[cel["ciclo"] == "2"]
        m = cel.merge(vc.astype({"cod_curso": int}), on=["co_cnes_7d", "cod_curso"])
        self.assertEqual(len(m), len(vc))
        self.assertTrue((m["n_alocados"] == m["n_alocados_ch1"]).all())
        self.assertTrue(self.r2["conferencia_contra_tarefa_b"]["c1_confirmacao_igual_a_n_confirmacoes_ch1"])
        self.assertTrue(self.r2["conferencia_contra_tarefa_b"]["c1_homologacao_igual_a_n_homologacoes_ch1"])

    def test_pessoas_e_descritivo_coerentes(self) -> None:
        p, d = self.csv["X2_pessoas"], self.csv["X2_descritivo"]
        for regra, st, at in ((X.REGRA_AMPLA, "status_ligacao", "ativo"),
                              (X.REGRA_ESTREITA, "status_ligacao_regra_estreita", "ativo_regra_estreita")):
            tot = d[(d["faixa"] == "TOTAL") & (d["subgrupo"] == "todos") & (d["regra_ligacao"] == regra)]
            tot = tot.set_index("ciclo")
            for k, g in p.groupby("ciclo"):
                self.assertEqual(int(tot.at[k, "n_alocados"]), len(g))
                self.assertEqual(int(tot.at[k, "n_ligados"]), int((g[st] == "LIGADO").sum()))
                self.assertEqual(int(tot.at[k, "n_incertos"]), int((g[st] == "INCERTO").sum()))
                self.assertAlmostEqual(float(tot.at[k, "permanencia_set"]), float(g[at].mean()))
        # A regra ampla só reclassifica NAO_LIGADO (sem correspondente) da estreita como INCERTO.
        mud = p[p["status_ligacao"] != p["status_ligacao_regra_estreita"]]
        self.assertTrue((mud["status_ligacao"] == "INCERTO").all())
        self.assertTrue((mud["status_ligacao_regra_estreita"] == "NAO_LIGADO").all())
        self.assertTrue((p.loc[p["status_ligacao"] == "LIGADO", "ativo"] == 1).all())
        self.assertTrue(p.loc[p["status_ligacao"].isin(["AMBIGUO", "INCERTO"]), "ativo"].isna().all())
        cel = self.csv["X2_celulas"]
        self.assertEqual(int(cel["n_ativos"].sum()),
                         int(p.loc[p["celula_no_quadro"].astype(bool), "ativo"].fillna(0).sum()))

    def test_x2_reestima_uma_linha(self) -> None:
        cel = self.csv["X2_celulas"]
        d = cel[(cel["ciclo"] == "2") & cel["s_mil"].notna() & (cel["so_excluidos"] == 0)]
        r = X.L.rd_local_linear(d["s_mil"].to_numpy(float), d["x2_celula_com_alocado_ativo"].to_numpy(float), 300,
                                X.H, cluster=d["co_ibge"].to_numpy(), ids_unidade=d["co_ibge"].to_numpy())
        e = self.csv["X2_estimativas"]
        lin = e[(e["outcome_id"] == "X2.3") & (e["ciclo"] == "2") & (e["corte"] == "0.300")
                & (e["especificacao"] == "principal") & (e["regra_ligacao"] == X.REGRA_AMPLA)].iloc[0]
        self.assertAlmostEqual(lin["tau"], r["tau"], places=10)
        self.assertAlmostEqual(lin["ep"], r["ep"], places=10)

    def test_bky_dentro_de_cada_x(self) -> None:
        for n in ("X2_estimativas", "X3_estimativas"):
            e = self.csv[n]
            m = e["entra_bky"].astype(bool)
            q = X.L.qvalores_bky(e.loc[m, "p_valor"].to_numpy(float))
            self.assertTrue(np.allclose(q, e.loc[m, "q_bky"].to_numpy(float)), n)
            self.assertTrue(e.loc[~m, "q_bky"].isna().all(), n)
            mp = m & e["no_protocolo_45"].astype(bool)
            qp = X.L.qvalores_bky(e.loc[mp, "p_valor"].to_numpy(float))
            self.assertTrue(np.allclose(qp, e.loc[mp, "q_bky_so_protocolo"].to_numpy(float)), n)
        e = self.csv["X2_estimativas"]
        self.assertFalse(e.loc[e["regra_ligacao"] == X.REGRA_ESTREITA, "entra_bky"].astype(bool).any())

    def test_rotulos_de_adicao_e_condicionamento(self) -> None:
        e2 = self.csv["X2_estimativas"]
        adic = e2["outcome_id"].isin(["X2.3", "X2.4"]) | e2["corte"].eq("empilhado") | e2["ciclo"].eq("1+2")
        self.assertFalse(e2.loc[adic, "no_protocolo_45"].astype(bool).any())
        self.assertTrue(e2.loc[adic, "rotulo"].str.startswith(X.ADICIONAL).all())
        self.assertTrue(e2.loc[~adic, "no_protocolo_45"].astype(bool).all())
        self.assertTrue(e2["condicionamento"].notna().all())
        e3 = self.csv["X3_estimativas"]
        prot = e3["especificacao"].eq("principal")
        self.assertTrue(e3.loc[prot, "no_protocolo_45"].astype(bool).all())
        self.assertFalse(e3.loc[~prot, "no_protocolo_45"].astype(bool).any())
        self.assertTrue(e3["condicionamento"].str.contains("pos-tratamento").all())
        self.assertTrue(e3["condicionamento"].str.contains("sem limites de Lee").all())

    def test_variante_sem_mai_jun(self) -> None:
        mun = self.csv["X3_municipio"]
        pm = self.csv["X3_painel_municipio_mes"]
        larga = pm.pivot(index="co_ibge", columns="mes", values="ativos")
        meses = [m for m in larga.columns if m not in self.r3["meses_excluidos_na_variante_x3m"]]
        pico = larga[meses].max(axis=1)
        m = mun.set_index("co_ibge")
        pos = m["com_ativo_nos_meses_sensibilidade_x3m"] == 1
        self.assertTrue(np.allclose(m.loc[pos, "pico_meses_sensibilidade_x3m"], pico.reindex(m.index[pos])))
        self.assertTrue(np.allclose(m.loc[pos, "x3m_queda_pico_ultimo"],
                                    m.loc[pos, "pico_meses_sensibilidade_x3m"] - m.loc[pos, "ativos_ultimo_mes"]))
        e3 = self.csv["X3_estimativas"]
        self.assertEqual(int(e3["especificacao"].str.startswith("sensibilidade_sem_mai_jun").sum()), 9)

    def test_ordem_de_execucao_divulgada(self) -> None:
        self.assertTrue(any("DEPOIS" in x and "faixa" in x for x in self.r2["ordem_de_execucao"]))
        self.assertTrue(any("DEPOIS" in x and "queda por faixa" in x for x in self.r3["ordem_de_execucao"]))
        self.assertIn("horizonte_por_ciclo", self.r2)

    def test_lee_so_por_ciclo_e_corte(self) -> None:
        e = self.csv["X2_estimativas"]
        lee = e[e["especificacao"] == "limites_lee"]
        exe = lee[lee["status"] == "EXECUTADO"]
        self.assertTrue(exe["ciclo"].isin(["1", "2"]).all() and exe["corte"].isin(["0.300", "0.400"]).all())
        self.assertTrue((exe["lee_tau_inf"] <= exe["lee_tau_sup"]).all())
        self.assertTrue((lee.loc[lee["status"] == "NAO_EXECUTADO", "nota"].str.contains("rdd_lib")).all())

    def test_x3_ultimo_mes_reproduz_retrato(self) -> None:
        nominal = pd.read_csv(ROOT / "data" / "pmm_especialistas_nominal.csv", dtype=str, usecols=["co_ibge"])
        pm = self.csv["X3_painel_municipio_mes"]
        ultimo = sorted(pm["mes"].unique())[-1]
        self.assertEqual(int(pm.loc[pm["mes"] == ultimo, "ativos"].sum()), len(nominal))
        self.assertEqual(self.r3["completude"]["ultimo_mes_reproduz_retrato_nominal"], True)

    def test_x3_soma_da_serie_preservada(self) -> None:
        s = pd.read_csv(ROOT / "data" / "pmm_especialistas_serie_historica.csv", dtype=str)
        s["mes"] = s["competencia"].map(X.competencia_iso)
        bruto = s.assign(q=pd.to_numeric(s["qtd_ativos"])).groupby("mes")["q"].sum()
        mc = self.csv["X3_painel_municipio_curso_mes"].groupby("mes")["ativos"].sum()
        pm = self.csv["X3_painel_municipio_mes"].groupby("mes")["ativos"].sum()
        self.assertTrue(np.allclose(bruto.sort_index(), mc.sort_index()))
        self.assertTrue(np.allclose(bruto.sort_index(), pm.sort_index()))

    def test_x3_regra_da_populacao_segue_a_completude(self) -> None:
        pm = self.csv["X3_painel_municipio_mes"]
        if self.r3["completude"]["listagem_completa_em_todos_os_meses"]:
            self.assertTrue((pm.groupby("mes").size() == pm["co_ibge"].nunique()).all())
        else:
            self.assertTrue((pm["listado"] == 1).all())   # ausência não vira zero

    def test_x3_queda(self) -> None:
        mun = self.csv["X3_municipio"]
        pos = mun[mun["pico"] > 0]
        self.assertTrue(np.allclose(pos["x3_queda_pico_ultimo"], pos["pico"] - pos["ativos_ultimo_mes"]))
        self.assertTrue((pos["x3_queda_pico_ultimo"] >= 0).all())
        self.assertTrue(mun.loc[mun["pico"] <= 0, "x3_queda_pico_ultimo"].isna().all())

    def test_tabelas_do_doc_iguais_as_geradas_das_saidas(self) -> None:
        geradas = X.gerar_tabelas_doc(X.ler_saidas())
        no_doc = X.tabelas_no_doc(DOC.read_text(encoding="utf-8"))
        self.assertEqual(set(no_doc), set(X.MAPA_MARCAS))
        for chave, corpo in no_doc.items():
            self.assertEqual(corpo, geradas[X.MAPA_MARCAS[chave]], chave)

    def _prosa(self) -> str:
        texto = DOC.read_text(encoding="utf-8")
        ini = texto.index("## X2")
        fim = texto.find("\n## X", texto.index("## X3") + 1)
        texto = texto[ini:fim if fim > 0 else None]
        texto = X.MARCA.sub("", texto)
        texto = re.sub(r"`[^`]*`", "", texto)
        texto = re.sub(r"\]\([^)]*\)", "]", texto)
        texto = re.sub(r"\b\d{2}/\d{2}/\d{4}\b", "", texto)
        texto = re.sub(r"\b[A-Za-z_]+\d+[a-z]?(?:\.\d+)*[a-z]?\b", "", texto)
        texto = re.sub(r"\d+ª", "", texto)
        texto = re.sub(r"§\s?\d+", "", texto)
        for fixo in ("SHA-256", "IC 95%", "auditoria 18", "doc 41a", "doc 45", "protocolo 40", "protocolo 45", "dez/25",
                      "ago/26", "mai/26", "jun/26", "p < 0,05"):
            texto = texto.replace(fixo, "")
        return texto

    def test_prosa_das_secoes_sem_numero_de_resultado(self) -> None:
        texto = self._prosa()
        decimais = set(re.findall(r"(?<![\w.,])[−+-]?\d+[,.]\d+", texto))
        self.assertEqual(decimais - {"0,300", "0,400", "0,050", "0,85"}, set())
        resto = re.sub(r"(?<![\w.,])[−+-]?\d+[,.]\d+", "", texto)
        inteiros = set(re.findall(r"(?<![\w.,])[−+-]?\d+(?![\w.,]\d)", resto))
        anos = {x for x in inteiros if x.isdigit() and 2000 <= int(x) <= 2030}   # IVS 2010, Censo 2022
        self.assertEqual(inteiros - {"1", "2", "10"} - anos, set())


if __name__ == "__main__":
    unittest.main()
