"""Testes da tarefa B do protocolo E6: outcomes do funil (script 12) e tabelas de escolha do E9.

Duas partes:

1. `TestConstrucaoSintetico`: as funções puras de
   `scripts/rdd_bolsa/12_construir_outcomes_funil.py` com DADOS SINTÉTICOS
   montados em memória (nada é gravado e nada é observação empírica):
   contagens por célula, frações municipais, médias por pessoa, sensibilidades,
   G3, motivos de ausência e tabela de escolhas.
2. `TestSaidasReais`: invariantes das saídas versionadas em
   `output/rdd_bolsa/outcomes/`. Todo alvo de validação é lido de arquivos de
   `output/` ou calculado pelas funções do E3, nunca digitado: número de linhas
   de U contra a base do IVS oficial (a08), V1 contra o E4, V2 contra a
   população P2 do E3, F1.3/F1.4 do ciclo 1 contra Y1/Y2 do E4 e D_k contra o
   próprio E3.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "12_construir_outcomes_funil.py"
SCRIPT_E3 = ROOT / "scripts" / "rdd_bolsa" / "07_estimar_E3_rdd_completa.py"
_bytecode = sys.dont_write_bytecode


def _carregar(nome: str, caminho: Path):
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


B = _carregar("outcomes_funil_12", SCRIPT)
sys.dont_write_bytecode = _bytecode

OUT = ROOT / "output" / "rdd_bolsa" / "outcomes"
DICIONARIO = OUT / "dicionario_outcomes_funil.json"
CHAVE = ["co_cnes_7d", "cod_curso"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


# --------------------------------------------------------------------------
# Fixtures sintéticas (só em memória)
# --------------------------------------------------------------------------

def quadro_sintetico() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "co_cnes_7d": ["0000001", "0000001", "0000002", "0000003"],
            "cod_curso": [1, 2, 1, 1],
            "co_ibge": ["100001", "100001", "100001", "200002"],
            "faixa_anunciada": ["FAIXA 1", "FAIXA 1", "FAIXA 1", "FAIXA 3"],
            "vagas_imediatas": [2.0, 0.0, 1.0, 1.0],
            "vagas_cr": [0.0, 1.0, 0.0, 2.0],
            "situacao_vagas": ["", "", "", ""],
            "regiao": ["NORTE", "NORTE", "NORTE", "NORDESTE"],
        }
    )


def candidaturas_sinteticas() -> pd.DataFrame:
    linhas = [
        # pessoa, cnes, curso, opcao, alocado, pontuacao, sem_pre
        ("p1", "0000001", 1, 1, True, 6.0, False),
        ("p2", "0000001", 1, 1, False, 4.0, False),
        ("p2", "0000002", 1, 2, False, 4.0, False),
        ("p3", "0000002", 1, 1, False, float("nan"), True),
        ("p4", "0000003", 1, 2, True, 8.0, False),
    ]
    df = pd.DataFrame(linhas, columns=["_pessoa", "co_cnes_7d", "cod_curso", "opcao", "alocado", "pontuacao",
                                       "sem_pre_requisito"])
    df["status"] = np.where(df["alocado"], "ALOCADO AC", "CADASTRO RESERVA")
    df["sub_judice"] = False
    df["classificado"] = True
    df["co_ibge_arquivo"] = None
    return df


class TestConstrucaoSintetico(unittest.TestCase):
    """Funções puras do script 12 com dados sintéticos em memória."""

    def setUp(self) -> None:
        self.q = quadro_sintetico()
        self.c = candidaturas_sinteticas()

    def test_chaves(self) -> None:
        self.assertEqual(B.chave_cnes(2001500), "2001500")
        self.assertEqual(B.chave_cnes(12505), "0012505")
        self.assertEqual(B.chave_cnes("2.001.500"), "2001500")
        self.assertIsNone(B.chave_cnes(12345678))
        self.assertEqual(B.chave_curso("01. Aprimoramento em X"), 1)
        self.assertEqual(B.chave_curso("24. Aprimoramento em Y"), 24)
        self.assertIsNone(B.chave_curso("Aprimoramento sem código"))
        self.assertEqual(B.chave_ibge(1200401), "120040")
        self.assertEqual(B.chave_ibge("270030"), "270030")
        self.assertEqual(B.opcao("1ª OPÇÃO"), 1)
        self.assertEqual(B.opcao(2), 2)
        self.assertIsNone(B.opcao(None))

    def test_casamento_nao_atribui_linha_fora_do_quadro(self) -> None:
        extra = self.c.iloc[[0]].assign(co_cnes_7d="0000001", cod_curso=9)
        linhas = pd.concat([self.c, extra], ignore_index=True)
        casado, diag = B.casar_com_quadro(self.q, linhas)
        self.assertEqual(len(casado), len(self.c))
        self.assertEqual(diag["linhas_fora_do_quadro"], 1)
        self.assertEqual(diag["linhas_fora_com_cnes_no_quadro_e_curso_diferente"], 1)

    def test_outcomes_celula(self) -> None:
        aloc_ch2 = self.c.iloc[[2]].assign(alocado=True)  # célula 0000002/1 recebe alocado na 2a chamada
        cel = B.outcomes_celula(self.q, self.c, 2, alocacao_ch2=aloc_ch2,
                                ativos=pd.DataFrame({"co_cnes_7d": ["0000001"], "cod_curso": [1]}))
        cel = cel.set_index(CHAVE)
        self.assertEqual(cel.loc[("0000001", 1), "n_cand_1a_opcao"], 2)
        self.assertEqual(cel.loc[("0000002", 1), "n_cand_1a_opcao"], 1)
        self.assertEqual(cel.loc[("0000002", 1), "n_cand_1a_opcao_com_pre_requisito"], 0)
        self.assertEqual(cel.loc[("0000001", 2), "n_candidaturas"], 0)  # oferecida sem candidato: zero observado
        self.assertEqual(cel.loc[("0000003", 1), "f1_2_tem_candidato"], 1)  # só 2a opção conta em F1.2
        self.assertEqual(cel.loc[("0000003", 1), "n_cand_1a_opcao"], 0)
        self.assertEqual(cel.loc[("0000001", 1), "f1_3_preenchida_ch1"], 1.0)
        self.assertEqual(cel.loc[("0000002", 1), "f1_3_preenchida_ch1"], 0.0)
        self.assertEqual(cel.loc[("0000002", 1), "f1_4_preenchida_ate_ch2"], 1.0)
        self.assertEqual(cel.loc[("0000001", 1), "f2_1_ativos_na_celula"], 1.0)
        self.assertEqual(cel.loc[("0000001", 1), "f4_2_pontuacao_media_cand_1a_opcao"], 5.0)
        self.assertTrue(np.isnan(cel.loc[("0000002", 1), "f4_2_pontuacao_media_cand_1a_opcao"]))

    def test_canonica_ciclo1_tem_precedencia(self) -> None:
        canon = self.q[CHAVE].assign(n_confirmacoes_ch1=0, n_homologacoes_ch1=0, n_homologacoes_novas_ch2=0,
                                     y1=[0, 1, 0, 0], y2=[0, 1, 1, 0])
        cel = B.outcomes_celula(self.q, self.c, 1, canonica=canon).set_index(CHAVE)
        self.assertEqual(cel.loc[("0000001", 1), "f1_3_preenchida_ch1"], 0.0)  # Y1 canônico, não o alocado
        self.assertEqual(cel.loc[("0000001", 2), "f1_3_preenchida_ch1"], 1.0)
        self.assertEqual(cel.loc[("0000002", 1), "f1_4_preenchida_ate_ch2"], 1.0)

    def test_sem_segunda_chamada_f1_4_fica_nan(self) -> None:
        cel = B.outcomes_celula(self.q, self.c, 3)
        self.assertTrue(cel["f1_4_preenchida_ate_ch2"].isna().all())
        self.assertTrue(cel["f2_1_ativos_na_celula"].isna().all())

    def test_sensibilidades_extras(self) -> None:
        sj = self.c.iloc[[1]].assign(sub_judice=True, alocado=False)
        cel = B.outcomes_celula(self.q, self.c, 3, alocacoes_extra={"sub_judice": sj}).set_index(CHAVE)
        self.assertEqual(cel.loc[("0000001", 1), "n_sub_judice"], 1)
        self.assertEqual(cel["f1_3s_preenchida_ch1_com_sub_judice"].sum(), cel["f1_3_preenchida_ch1"].sum())

    def test_outcomes_municipio(self) -> None:
        cel = B.outcomes_celula(self.q, self.c, 2, alocacao_ch2=self.c.iloc[[2]].assign(alocado=True))
        ativos = pd.DataFrame({"co_ibge": ["100001", "100001", "300003"]})
        mun = B.outcomes_municipio(cel, ativos).set_index("co_ibge")
        m1 = mun.loc["100001"]
        self.assertEqual(m1["n_celulas"], 3)
        self.assertAlmostEqual(m1["f1_1_cand_1a_opcao_por_celula"], 3 / 3)
        self.assertAlmostEqual(m1["f1_2_fracao_celulas_com_candidato"], 2 / 3)
        self.assertAlmostEqual(m1["f1_3_fracao_celulas_preenchidas_ch1"], 1 / 3)
        self.assertAlmostEqual(m1["f1_4_fracao_celulas_preenchidas_ate_ch2"], 2 / 3)
        self.assertAlmostEqual(m1["f1_3s_fracao_celulas_imediatas_preenchidas_ch1"], 1 / 2)
        self.assertEqual(m1["n_ativos_ciclo"], 2.0)
        self.assertAlmostEqual(m1["f2_1_ativos_por_celula"], 2 / 3)
        self.assertEqual(m1["f2_3_d_k_algum_ativo_do_ciclo"], 1.0)
        # Média por pessoa: p1 (6) e p2 (4) em 1a opção; p3 sem pontuação fica fora.
        self.assertAlmostEqual(m1["f4_2_pontuacao_media_cand_1a_opcao"], 5.0)
        self.assertAlmostEqual(m1["f4_1_pontuacao_media_alocados"], 6.0)
        m2 = mun.loc["200002"]
        self.assertEqual(m2["f2_3_d_k_algum_ativo_do_ciclo"], 0.0)
        self.assertTrue(np.isnan(m2["f4_2_pontuacao_media_cand_1a_opcao"]))

    def test_g3(self) -> None:
        card = pd.DataFrame({"co_cnes_7d": ["1", "2", "3"], "cod_curso": [1, 1, 1],
                             "co_ibge": ["100001", "100001", "200002"], "vagas_cardapio": [3.0, 2.0, 1.0]})
        ades = pd.DataFrame({"co_cnes_7d": ["1", "9", "8"], "cod_curso": [1, 2, 1],
                             "co_ibge": ["100001", "100001", "999999"], "priorizadas": [2.0, 0.0, 5.0],
                             "priorizadas_imediatas": [1.0, 0.0, 5.0], "priorizadas_cr": [1.0, 0.0, 0.0],
                             "nao_priorizadas": [1.0, 2.0, 0.0]})
        pop = pd.Series({"100001": 20000.0, "200002": 5000.0})
        g3, diag = B.outcomes_g3(card, ades, pop)
        g3 = g3.set_index("co_ibge")
        self.assertEqual(list(g3.index), ["100001", "200002"])
        self.assertEqual(g3.loc["100001", "f0_3a_consta_do_resultado_final_adesao"], 1)
        self.assertEqual(g3.loc["100001", "f0_3_vagas_pedidas"], 5.0)  # inclui célula fora do cardápio
        self.assertAlmostEqual(g3.loc["100001", "f0_3_fracao_priorizada"], 2 / 5)
        # Não consta do resultado: 0 em F0.3a, mas pedidos NaN (não é "não pediu").
        self.assertEqual(g3.loc["200002", "f0_3a_consta_do_resultado_final_adesao"], 0)
        self.assertEqual(g3.loc["200002", "n_linhas_adesao"], 0)
        for c in ("f0_3_vagas_pedidas", "f0_3_fracao_priorizada", "f0_3_vagas_imediatas_priorizadas"):
            self.assertTrue(np.isnan(g3.loc["200002", c]), c)
        mot = json.loads(B.anotar_ausencias(g3.reset_index(), B.MOTIVOS_G3).iloc[1])
        self.assertEqual(mot["f0_3_vagas_pedidas"], "não consta do resultado final de adesão")
        self.assertEqual(diag["municipios_com_adesao_fora_do_cardapio"], 1)
        self.assertEqual(diag["linhas_adesao_em_municipios_g3_com_celula_fora_do_cardapio"], 1)

    def test_motivos_falham_fechado(self) -> None:
        df = pd.DataFrame({"ciclo": [1, 3], "f1_4_preenchida_ate_ch2": [1.0, np.nan], "x": [1.0, 2.0]})
        mot = B.anotar_ausencias(df, B.MOTIVOS_V)
        self.assertEqual(json.loads(mot.iloc[0]), {})
        self.assertIn("F1.4", json.loads(mot.iloc[1])["f1_4_preenchida_ate_ch2"])
        with self.assertRaises(AssertionError):  # NaN sem motivo registrado
            B.anotar_ausencias(df.assign(x=[np.nan, 1.0]), B.MOTIVOS_V)
        with self.assertRaises(AssertionError):  # NaN num ciclo em que o motivo não vale
            B.anotar_ausencias(pd.DataFrame({"ciclo": [1], "f1_4_preenchida_ate_ch2": [np.nan]}), B.MOTIVOS_V)

    def test_motivos_em_json_sem_separador_ambiguo(self) -> None:
        motivos = {"a": ("motivo com ; e | e : dentro", None), "b": ("outro; motivo", {3})}
        df = pd.DataFrame({"ciclo": [3, 3, 1], "a": [np.nan, 1.0, np.nan], "b": [np.nan, np.nan, 2.0]})
        lidos = [json.loads(x) for x in B.anotar_ausencias(df, motivos)]
        self.assertEqual(lidos[0], {"a": "motivo com ; e | e : dentro", "b": "outro; motivo"})
        self.assertEqual(lidos[1], {"b": "outro; motivo"})
        self.assertEqual(lidos[2], {"a": "motivo com ; e | e : dentro"})
        # Condição por coluna: NaN só onde a coluna de condição tem o valor dado.
        cond = {"x": ("não consta", ("consta", 0))}
        ok = pd.DataFrame({"consta": [0, 1], "x": [np.nan, 1.0]})
        self.assertEqual(json.loads(B.anotar_ausencias(ok, cond).iloc[0]), {"x": "não consta"})
        with self.assertRaises(AssertionError):
            B.anotar_ausencias(pd.DataFrame({"consta": [1], "x": [np.nan]}), cond)

    def test_escolhas_e_conjunto(self) -> None:
        c = pd.concat([self.c, self.c.iloc[[0]].assign(_pessoa="p5", cod_curso=7)], ignore_index=True)
        esc = B.tabela_escolhas(c, self.q, 2)
        self.assertEqual(len(esc), len(c))
        self.assertEqual(esc["id_candidato"].nunique(), 5)
        self.assertTrue(esc["id_candidato"].str.match(r"^c2_\d{5}$").all())
        self.assertNotIn("_pessoa", esc.columns)
        fora = esc[esc["cod_curso"] == 7]
        self.assertEqual(int(fora["celula_no_quadro"].iloc[0]), 0)
        self.assertTrue(fora["co_ibge"].isna().all())
        self.assertIn("fora do quadro", B.anotar_ausencias(esc, B.MOTIVOS_ESCOLHAS)[fora.index[0]])
        # Determinismo do pseudônimo: mesma entrada, mesmos ids.
        pd.testing.assert_frame_equal(esc, B.tabela_escolhas(c.sample(frac=1, random_state=7), self.q, 2))
        self.assertNotIn("tipo_inscricao", esc.columns)
        # 2a opção em outro curso: o conjunto da linha é o do curso da própria opção.
        c2 = pd.concat([self.c, self.c.iloc[[0]].assign(opcao=2, cod_curso=2, co_cnes_7d="0000001")], ignore_index=True)
        esc2 = B.tabela_escolhas(c2, self.q, 2)
        p1 = esc2[esc2["opcao_rank"] == 2].query("cod_curso == 2").iloc[0]
        self.assertEqual(p1["id_conjunto_escolha"], "c2_curso02")
        self.assertEqual(p1["curso_da_1a_opcao"], 1.0)
        self.assertEqual(p1["opcoes_em_cursos_diferentes"], 1.0)
        pop = pd.Series({"100001": 20000.0, "200002": 5000.0})
        estr = pd.Series({"100001": "capital", "200002": "interior_remoto"})
        conj = B.conjunto_escolha(self.q, 2, pop, estr)
        self.assertEqual(len(conj), len(self.q))  # principal: todas as células, com ou sem vaga imediata
        self.assertEqual(int(conj["tem_vaga_imediata"].sum()), 3)
        self.assertTrue(np.allclose(conj["log_vagas_imediatas_mais_1"], np.log(conj["vagas_imediatas"] + 1)))
        self.assertEqual(set(conj["id_conjunto_escolha"]), {"c2_curso01", "c2_curso02"})
        self.assertEqual(conj.set_index("co_ibge")["estrato_territorial"].to_dict()["200002"], "interior_remoto")


# --------------------------------------------------------------------------
# Saídas reais
# --------------------------------------------------------------------------

@unittest.skipUnless(DICIONARIO.exists(), "saídas do script 12 ausentes")
class TestSaidasReais(unittest.TestCase):
    """Invariantes das saídas empíricas; alvos lidos de output/ ou do E3."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.u = pd.read_parquet(OUT / "outcomes_U_municipio.parquet")
        cls.g3 = pd.read_parquet(OUT / "outcomes_G3_municipio.parquet")
        cls.vm = pd.read_parquet(OUT / "outcomes_V_municipio.parquet")
        cls.vc = pd.read_parquet(OUT / "outcomes_V_celula.parquet")
        cls.esc = pd.read_parquet(OUT / "escolhas_candidatos.parquet")
        cls.conj = pd.read_parquet(OUT / "escolhas_conjunto_principal.parquet")
        cls.conj_sens = pd.read_parquet(OUT / "escolhas_conjunto_sensibilidade_vaga_imediata.parquet")
        cls.dic = json.loads(DICIONARIO.read_text(encoding="utf-8"))
        cls.e4 = pd.read_csv(ROOT / "output" / "rdd_bolsa" / "E4_proporcao_municipio.csv", dtype={"co_ibge": str})

    def test_chaves_unicas(self) -> None:
        for df, chave in ((self.u, ["co_ibge"]), (self.g3, ["co_ibge"]), (self.vm, ["ciclo", "co_ibge"]),
                          (self.vc, ["ciclo"] + CHAVE), (self.conj, ["ciclo"] + CHAVE),
                          (self.conj_sens, ["ciclo"] + CHAVE),
                          (self.esc, ["ciclo", "id_candidato", "opcao_rank", "co_cnes_7d", "cod_curso"])):
            self.assertFalse(df.duplicated(chave).any(), chave)

    def test_u_e_a_base_do_ivs_oficial(self) -> None:
        ivs = pd.read_csv(ROOT / "output" / "aquisicao" / "a08_ivs_2010_oficial_municipio.csv", dtype={"co_ibge": str})
        self.assertEqual(sorted(self.u["co_ibge"]), sorted(ivs["co_ibge"].str.zfill(6)))
        m = self.u.merge(ivs.assign(co_ibge=ivs["co_ibge"].str.zfill(6)), on="co_ibge")
        self.assertTrue((m["ivs_2010_oficial"] == m["ivs"]).all())

    def test_v1_e_celulas_do_ciclo1(self) -> None:
        v1 = self.vm[self.vm["ciclo"] == 1]
        self.assertEqual(sorted(v1["co_ibge"]), sorted(self.e4["co_ibge"]))
        trat = pd.read_parquet(ROOT / "output" / "aquisicao" / "quadro_vagas_tratamento.parquet")
        self.assertEqual(int((self.vc["ciclo"] == 1).sum()), len(trat))

    def test_f1_3_e_f1_4_do_ciclo1_reproduzem_e4(self) -> None:
        m = self.vm[self.vm["ciclo"] == 1].merge(self.e4, on="co_ibge", suffixes=("", "_e4"))
        self.assertEqual(len(m), len(self.e4))
        self.assertTrue((m["n_celulas"] == m["n_celulas_e4"]).all())
        self.assertTrue((m["n_celulas_preenchidas_ch1"] == m["n_celulas_y1"]).all())
        self.assertTrue((m["n_celulas_preenchidas_ate_ch2"] == m["n_celulas_y2"]).all())
        self.assertTrue(np.allclose(m["f1_3_fracao_celulas_preenchidas_ch1"], m["y1"], atol=1e-9, rtol=0))
        self.assertTrue(np.allclose(m["f1_4_fracao_celulas_preenchidas_ate_ch2"], m["y2"], atol=1e-9, rtol=0))

    def test_d_k_e_v2_reproduzem_e3(self) -> None:
        e3 = _carregar("e3_rdd_completa", SCRIPT_E3)
        sys.dont_write_bytecode = _bytecode
        pops = e3.carregar_populacoes(ROOT)
        ativos = e3.ler_ativos(ROOT / "data" / "raw" / "aquisicao" / "ivs_administrativo"
                               / "tb_profissionais_ativos_pmme_csv.zip")
        for nome, k in (("P1", 1), ("P2", 2)):
            vk = self.vm[self.vm["ciclo"] == k].set_index("co_ibge")
            self.assertEqual(sorted(vk.index), sorted(set(pops[nome]["co_ibge"])), nome)
            d = e3.construir_d_k(pops[nome]["co_ibge"], ativos, k)
            self.assertTrue((vk.loc[d.index, "f2_3_d_k_algum_ativo_do_ciclo"] == d).all(), nome)

    def test_f1_1_bate_com_a_tabela_de_escolhas(self) -> None:
        um = self.esc[self.esc["opcao_rank"] == 1].groupby(["ciclo"] + CHAVE).size()
        cel = self.vc.set_index(["ciclo"] + CHAVE)["n_cand_1a_opcao"]
        self.assertTrue((cel.reindex(um.index) == um).all())
        self.assertEqual(int(cel.sum()), int(um.sum()))

    def test_conjuntos_de_escolha(self) -> None:
        # Principal (§14): todas as células do quadro; sensibilidade (§12): só as com vaga imediata.
        self.assertEqual(sorted(self.vc.set_index(["ciclo"] + CHAVE).index),
                         sorted(self.conj.set_index(["ciclo"] + CHAVE).index))
        imed = self.vc[self.vc["vagas_imediatas"] > 0].set_index(["ciclo"] + CHAVE)
        self.assertEqual(sorted(imed.index), sorted(self.conj_sens.set_index(["ciclo"] + CHAVE).index))
        self.assertFalse(self.conj[["estrato_territorial", "macrorregiao", "populacao_2022"]].isna().any().any())
        # Toda escolha cai no conjunto do curso da própria opção.
        chaves = set(zip(self.conj["id_conjunto_escolha"], self.conj["co_cnes_7d"], self.conj["cod_curso"]))
        esc = zip(self.esc["id_conjunto_escolha"], self.esc["co_cnes_7d"], self.esc["cod_curso"])
        self.assertTrue(all(x in chaves for x in esc))
        self.assertNotIn("tipo_inscricao", self.esc.columns)

    def test_g3_nao_codifica_ausencia_como_zero_pedido(self) -> None:
        nao = self.g3[self.g3["f0_3a_consta_do_resultado_final_adesao"] == 0]
        self.assertTrue(nao[["f0_3_vagas_pedidas", "f0_3_fracao_priorizada"]].isna().all().all())
        sim = self.g3[self.g3["f0_3a_consta_do_resultado_final_adesao"] == 1]
        self.assertTrue((sim["f0_3_vagas_pedidas"] >= 1).all())

    def test_integridade(self) -> None:
        for df in (self.u, self.g3, self.vm, self.vc, self.esc, self.conj, self.conj_sens):
            self.assertEqual(set(df["natureza_dos_dados"]), {"EMPIRICO"})
            outcome = [c for c in df.columns if c not in ("motivos_ausencia", "natureza_dos_dados")]
            nulos = df[outcome].isna()
            # motivos_ausencia é JSON: as chaves são exatamente as colunas NaN da linha.
            for i, texto in enumerate(df["motivos_ausencia"]):
                self.assertEqual(set(json.loads(texto)), set(nulos.columns[nulos.iloc[i].to_numpy()]))
            self.assertFalse(any(c.lower() in ("nome", "cpf", "cpf_masc", "_pessoa") for c in df.columns))
        self.assertEqual(self.dic["natureza_dos_dados"], "EMPIRICO")
        self.assertNotIn("ivs_ipea_2010_municipios", SCRIPT.read_text(encoding="utf-8"))

    def test_dicionario_registra_hashes_das_saidas_e_entradas(self) -> None:
        for bloco in self.dic["saidas"].values():
            self.assertEqual(sha256(ROOT / bloco["arquivo"]), bloco["sha256"], bloco["arquivo"])
            self.assertTrue(bloco["chave_unica"])
        for e in self.dic["entradas"]:
            self.assertEqual(sha256(ROOT / e["caminho"]), e["sha256"], e["caminho"])
            for campo in ("data_referencia", "cobertura", "unidade", "chaves", "filtros"):
                self.assertIn(campo, e)


if __name__ == "__main__":
    unittest.main()
