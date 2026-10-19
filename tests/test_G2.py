"""Portão G2 (doc 51, T6.0): replicação do mecanismo de alocação do PMM-E.

Duas partes:

1. Saídas gravadas (`output/rdd_bolsa/G2_*`): esquema, rótulo EMPIRICO,
   ausência de dados pessoais, concordâncias recalculadas do parquet, regra do
   veredito refeita do JSON, cortes e margens coerentes entre si, conferências
   de entrada, hashes, trechos dos editais e relatório igual ao gerado.
2. Verificação do mecanismo em mercados SINTÉTICOS, só em memória (nada é
   gravado): exemplos à mão, ordem das cotas, tipagem das vagas acrescidas,
   equivalência com Boston sem vagas reservadas e estabilidade da aceitação
   adiada em mercados sintéticos aleatórios.
"""

from __future__ import annotations

import hashlib
import html
import importlib.util
import json
import re
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "G2_mecanismo_alocacao.py"
OUT = ROOT / "output" / "rdd_bolsa"
ALOC = OUT / "G2_alocacao_reconstruida.parquet"
CORTES = OUT / "G2_cortes_celula.csv"
RESUMO = OUT / "G2_resumo.json"
DOC = ROOT / "docs" / "auditorias" / "G2_viabilidade_mecanismo.md"

_spec = importlib.util.spec_from_file_location("g2_mecanismo", SCRIPT)
G2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(G2)

CHAMADAS = {"c1_ch1": (1, 1), "c2_ch1": (2, 1), "c3_ch1": (3, 1), "c1_ch2": (1, 2), "c2_ch2": (2, 2)}


def sha256(caminho: Path) -> str:
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


# --------------------------------------------------------------------------
# 1. Saídas gravadas
# --------------------------------------------------------------------------

class TestSaidasG2(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.aloc = pd.read_parquet(ALOC)
        cls.cortes = pd.read_csv(CORTES, dtype={"co_cnes_7d": str})
        cls.r = json.loads(RESUMO.read_text(encoding="utf-8"))

    def test_esquema_chaves_e_rotulo(self) -> None:
        self.assertFalse(self.aloc.duplicated(["ciclo", "chamada", "id_candidato"]).any())
        self.assertFalse(self.cortes.duplicated(["ciclo", "chamada", "co_cnes_7d", "cod_curso"]).any())
        self.assertEqual(set(self.aloc["natureza_dos_dados"]), {"EMPIRICO"})
        self.assertEqual(set(self.cortes["natureza_dos_dados"]), {"EMPIRICO"})
        self.assertEqual(self.r["natureza_dos_dados"], "EMPIRICO")
        self.assertEqual(set(zip(self.aloc["ciclo"], self.aloc["chamada"])), set(CHAMADAS.values()))
        self.assertTrue(self.aloc["id_candidato"].str.fullmatch(r"c[123](ch2)?_\d{5}").all())
        self.assertTrue(self.cortes["co_cnes_7d"].str.fullmatch(r"\d{7}").all())
        self.assertEqual(len(self.aloc), self.r["saidas"]["alocacao"]["linhas"])
        self.assertEqual(len(self.cortes), self.r["saidas"]["cortes"]["linhas"])

    def test_nenhum_dado_pessoal_gravado(self) -> None:
        for df in (self.aloc, self.cortes):
            cols = " ".join(df.columns).upper()
            for proibido in ("NOME", "CPF", "TIPO_INSCRICAO", "IVS", "FAIXA"):
                self.assertNotIn(proibido, cols)
            for c in df.select_dtypes(include=["object", "string"]).columns:
                v = df[c].dropna().astype(str)
                self.assertFalse(v.str.contains(r"X{2,}|\*{3}|\d{3}\.\d{2}", regex=True).any(), c)
        texto = RESUMO.read_text(encoding="utf-8") + DOC.read_text(encoding="utf-8")
        self.assertIsNone(re.search(r"\d{3}\.\d{2}X|\*\*\*\.\d{3}", texto))

    def test_ids_iguais_aos_do_e9_na_1a_chamada(self) -> None:
        esc = pd.read_parquet(ROOT / "output" / "rdd_bolsa" / "outcomes" / "escolhas_candidatos.parquet",
                              columns=["ciclo", "id_candidato"]).drop_duplicates()
        a = self.aloc[self.aloc["chamada"] == 1][["ciclo", "id_candidato"]]
        self.assertEqual(set(map(tuple, a.values)), set(map(tuple, esc.values)))
        for k, v in self.r["chamadas"].items():
            c = v["conferencia_com_escolhas_candidatos"]
            if c is None:
                continue
            self.assertEqual(c["linhas_casadas"], c["linhas_g2"])
            self.assertEqual(c["linhas_casadas"], c["linhas_escolhas"])
            self.assertEqual(c["pontuacao_igual"], c["linhas_g2"])
            self.assertEqual(c["alvo_igual"], c["linhas_g2"])
            cv = v["conferencia_vagas_com_V_celula"]
            self.assertEqual(cv["imediatas_iguais"], cv["celulas_g2"])
            self.assertEqual(cv["cr_iguais"], cv["celulas_g2"])

    def test_concordancia_recalculada_do_parquet(self) -> None:
        def mesma(a: pd.DataFrame, suf: str) -> pd.Series:
            pc, pk = a["co_cnes_7d_publicado"], a["cod_curso_publicado"]
            rc, rk = a[f"co_cnes_7d_{suf}"], a[f"cod_curso_{suf}"]
            ambos_vazios = pc.isna() & rc.isna()
            return ambos_vazios | ((pc == rc) & (pk == rk))

        for k, (ciclo, ch) in CHAMADAS.items():
            a = self.aloc[(self.aloc["ciclo"] == ciclo) & (self.aloc["chamada"] == ch)]
            self.assertTrue((mesma(a, "reconstruido").astype(int) == a["concorda_principal"]).all(), k)
            e = self.r["chamadas"][k]["especificacoes"]
            self.assertAlmostEqual(a["concorda_principal"].mean(), e["P_efetiva_publicada"]["taxa"], places=12)
            self.assertEqual(int(a["concorda_principal"].sum()), e["P_efetiva_publicada"]["concordantes"])
            self.assertAlmostEqual(a["concorda_so_nota"].mean(), e["S_efetiva_publicada_so_nota"]["taxa"], places=12)
            self.assertAlmostEqual(a["concorda_cotas_ordem_alternativa"].mean(),
                                   e["S_efetiva_publicada_cotas_alternativa"]["taxa"], places=12)
            if "A_ex_ante_publicada" in e:
                self.assertAlmostEqual(a["concorda_ex_ante"].mean(), e["A_ex_ante_publicada"]["taxa"], places=12)
            else:
                self.assertTrue(a["concorda_ex_ante"].isna().all())
                self.assertTrue(a["motivos_ausencia"].str.contains("concorda_ex_ante").all())
            s = self.r["chamadas"][k]["sorteios_desempate"]
            self.assertEqual(s["n_sorteios"], 100)
            self.assertAlmostEqual(a["taxa_concordancia_sorteios"].mean(), s["efetiva_ex_post"]["media"], places=12)
            # Divergência sempre tipificada; concordância nunca.
            self.assertTrue((a.loc[a["concorda_principal"] == 0, "tipo_divergencia_principal"] != "").all())
            self.assertTrue((a.loc[a["concorda_principal"] == 1, "tipo_divergencia_principal"] == "").all())
            tipos = a.loc[a["concorda_principal"] == 0, "tipo_divergencia_principal"].value_counts().to_dict()
            self.assertEqual(tipos, self.r["chamadas"][k]["divergencias_principal_por_tipo"])

    def test_regra_do_veredito_refeita(self) -> None:
        meta = self.r["meta_concordancia"]
        self.assertEqual(meta, 0.99)
        vered = {}
        for k in ("c1_ch1", "c2_ch1", "c3_ch1"):
            e = self.r["chamadas"][k]["especificacoes"]
            if "A_ex_ante_publicada" in e and e["A_ex_ante_publicada"]["taxa"] >= meta:
                vered[k] = "VIAVEL"
            elif e["P_efetiva_publicada"]["taxa"] >= meta:
                vered[k] = "VIAVEL_PARCIAL"
            else:
                vered[k] = "INVIAVEL"
            iv = self.r["chamadas"][k]["intervalo_variantes_capacidade_efetiva_desempate_publicado"]
            taxas = [e[n]["taxa"] for n in iv["variantes"]]
            self.assertAlmostEqual(min(taxas), iv["minimo"], places=12)
            self.assertEqual(self.r["veredito_robusto_as_variantes_do_mecanismo"][k], min(taxas) >= meta)
        self.assertEqual(vered, self.r["veredito_por_ciclo"])
        if all(v == "VIAVEL" for v in vered.values()):
            g = "VIAVEL"
        elif all(v != "INVIAVEL" for v in vered.values()):
            g = "VIAVEL_PARCIAL"
        else:
            g = "INVIAVEL"
        self.assertEqual(g, self.r["veredito"])

    def test_alocacao_publicada_respeita_capacidade_efetiva(self) -> None:
        for (ciclo, ch), g in self.cortes.groupby(["ciclo", "chamada"]):
            self.assertTrue((g["n_alocados_publicado"] <= g["vagas_total"]).all())
            self.assertTrue((g["n_admitidos"] <= g["vagas_total"]).all())
            a = self.aloc[(self.aloc["ciclo"] == ciclo) & (self.aloc["chamada"] == ch)]
            # Cortes só listam células escolhidas por candidatos elegíveis: todo admitido aparece numa célula.
            self.assertEqual(int(g["n_admitidos"].sum()), int(a["alocado_reconstruido"].sum()))
            self.assertEqual(int(g["n_admitidos"].sum()),
                             int((g["n_admitidos_vaga_geral"] + g["n_admitidos_reserva"]).sum()))

    def test_cortes_coerentes_e_ausencias_com_motivo(self) -> None:
        c = self.cortes
        self.assertTrue(((c["corte_ativo"] == 1) == (c["n_recusados"] > 0)).all())
        sem = c["corte_pontuacao"].isna()
        self.assertTrue(c.loc[sem, "motivo_corte"].fillna("").str.len().gt(0).all())
        self.assertTrue(c.loc[~sem, "motivo_corte"].isna().all())
        self.assertTrue(c.loc[c["corte_ativo_ex_ante"].isna(), "motivo_corte_ex_ante"].fillna("").str.len().gt(0).all())
        com = c[~sem]
        self.assertTrue(com["corte_opcao"].isin([1, 2]).all())
        self.assertTrue((com["n_admitidos_no_corte"] >= 1).all())
        self.assertTrue((com["n_admitidos_no_corte"] <= com["n_empatados_no_corte"]).all())
        # Contagens do JSON refeitas do CSV.
        for k, (ciclo, ch) in CHAMADAS.items():
            g = c[(c["ciclo"] == ciclo) & (c["chamada"] == ch)]
            j = self.r["chamadas"][k]["cortes_principal"]
            self.assertEqual(j["celulas_com_vaga"], int((g["vagas_total"] > 0).sum()))
            self.assertEqual(j["celulas_com_corte_ativo"], int(((g["corte_ativo"] == 1) & (g["vagas_total"] > 0)).sum()))
            self.assertEqual(j["com_corte_entre_1a_opcao"], int((g["corte_opcao"] == 1).sum()))
            self.assertEqual(j["com_corte_entre_2a_opcao"], int((g["corte_opcao"] == 2).sum()))

    def test_margem_igual_nota_menos_corte_da_1a_opcao(self) -> None:
        for k, (ciclo, ch) in CHAMADAS.items():
            a = self.aloc[(self.aloc["ciclo"] == ciclo) & (self.aloc["chamada"] == ch) & (self.aloc["elegivel"] == 1)]
            g = self.cortes[(self.cortes["ciclo"] == ciclo) & (self.cortes["chamada"] == ch)]
            m = a.merge(g, left_on=["co_cnes_7d_1a_opcao", "cod_curso_1a_opcao"], right_on=["co_cnes_7d", "cod_curso"],
                        how="left", validate="many_to_one")
            definida = (m["corte_opcao"] == 1)
            esperado = np.where(definida, m["pontuacao"] - m["corte_pontuacao"], np.nan)
            np.testing.assert_allclose(m["margem_1a_opcao"].to_numpy(), esperado, equal_nan=True, err_msg=k)
            self.assertTrue(m.loc[m["margem_1a_opcao"].isna(), "motivos_ausencia"].str.contains("margem_1a_opcao").all())
            j = self.r["chamadas"][k]["margem_1a_opcao_principal"]
            d = m["margem_1a_opcao"].dropna()
            self.assertEqual(j["definida"], len(d))
            self.assertEqual(j["igual_0_empate_no_corte"], int((d == 0).sum()))
            self.assertEqual(j["abs_ate_1"], int((d.abs() <= 1).sum()))
            self.assertEqual(j["abs_ate_2"], int((d.abs() <= 2).sum()))

    def test_hashes_das_entradas_e_editais(self) -> None:
        for e in self.r["entradas"]:
            self.assertEqual(sha256(ROOT / e["caminho"]), e["sha256"], e["caminho"])
        for e in self.r["editais"].values():
            self.assertEqual(sha256(ROOT / e["caminho"]), e["sha256"], e["caminho"])
        caminhos = " ".join(e["caminho"] for e in self.r["entradas"])
        self.assertNotIn("ivs_ipea_2010", caminhos)
        self.assertNotIn("cnes", caminhos.lower().replace("co_cnes", ""))

    def test_trechos_dos_editais_estao_nos_arquivos(self) -> None:
        def norm(t: str) -> str:
            return re.sub(r"\s+", " ", t.replace("ﬁ", "fi").replace("ﬂ", "fl"))

        bruto = (ROOT / self.r["editais"]["ciclo_1"]["caminho"]).read_bytes().decode("utf-8", "replace")
        bruto = re.sub(r"(?is)<(script|style).*?</\1>", " ", bruto)
        c1 = norm(html.unescape(re.sub(r"<[^>]+>", " ", bruto)))
        for t in self.r["trechos_edital_conferidos"]["ciclo_1"]:
            self.assertIn(norm(t["trecho"]), c1, t["item"])
        try:
            import pypdf
        except ImportError:
            self.skipTest("pypdf ausente: conferência do edital do ciclo 3 não executada")
        leitor = pypdf.PdfReader(str(ROOT / self.r["editais"]["ciclo_3"]["caminho"]))
        c3 = norm(" ".join(p.extract_text() or "" for p in leitor.pages))
        for t in self.r["trechos_edital_conferidos"]["ciclo_3"]:
            self.assertIn(norm(t["trecho"]), c3, t["item"])

    def test_relatorio_igual_ao_gerado_do_json(self) -> None:
        self.assertEqual(DOC.read_text(encoding="utf-8"), G2.gerar_doc(self.r))
        texto = DOC.read_text(encoding="utf-8")
        self.assertIn(f"**Veredito: `{self.r['veredito']}`**", texto)

    def test_script_nao_le_outcome(self) -> None:
        fonte = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('columns=["ciclo", "co_cnes_7d", "cod_curso", "vagas_imediatas", "vagas_cr"]', fonte)
        for proibido in ("a08_ivs", "cnes_nacional", "painel", "tabnet", "a12_", "a13_", "a14_", "f1_3", "f2_1",
                         "ivs_2010_oficial", "faixa_anunciada"):
            self.assertNotIn(proibido, fonte.lower())
        self.assertNotIn("G2_mecanismo_alocacao", (ROOT / "run_all.py").read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# 2. Mecanismo em mercados sintéticos (só em memória)
# --------------------------------------------------------------------------

def mercado_sintetico(linhas: list[tuple]) -> pd.DataFrame:
    """Linhas (id, celula, opcao, pontuacao, tipo, classificacao) — dados SINTÉTICOS, só em memória."""
    df = pd.DataFrame(linhas, columns=["id_candidato", "celula", "opcao_rank", "pontuacao", "tipo_inscricao",
                                       "classificacao_publicada"])
    df["classificacao_publicada"] = df["classificacao_publicada"].astype(float)
    df["pontuacao"] = df["pontuacao"].astype(float)
    return df


def celulas(sim: dict) -> dict:
    return {p: c for p, (c, _) in sim.items()}


class TestMecanismoSintetico(unittest.TestCase):
    """Verificação sintética: mercados inventados, rotulados como sintéticos, nunca gravados."""

    A, B, C, D, E, F = ("sint", 1), ("sint", 2), ("sint", 3), ("sint", 4), ("sint", 5), ("sint", 6)

    def test_sintetico_prioridade_da_1a_opcao_contra_so_nota(self) -> None:
        m = mercado_sintetico([
            ("x", self.A, 1, 9, "AC", 1), ("x", self.B, 2, 9, "AC", 3),
            ("y", self.B, 1, 5, "AC", 1),
            ("w", self.C, 1, 8, "AC", 1), ("w", self.B, 2, 8, "AC", 2),
        ])
        vagas = {self.A: (1, 0, 0), self.B: (1, 0, 0), self.C: (0, 0, 0)}
        da = celulas(G2.alocar(m, vagas, G2.AC_PRIMEIRO))
        self.assertEqual(da, {"x": self.A, "y": self.B})
        so_nota = celulas(G2.alocar(m, vagas, G2.AC_PRIMEIRO, prioridade_1a_opcao=False))
        self.assertEqual(so_nota, {"x": self.A, "w": self.B})
        self.assertEqual(celulas(G2.boston(m, vagas, G2.AC_PRIMEIRO)), da)

    def test_sintetico_desempate_pela_classificacao_publicada(self) -> None:
        m = mercado_sintetico([("p", self.A, 1, 5, "AC", 2), ("q", self.A, 1, 5, "AC", 1)])
        self.assertEqual(celulas(G2.alocar(m, {self.A: (1, 0, 0)}, G2.AC_PRIMEIRO)), {"q": self.A})
        sorteio = {"p": 0.1, "q": 0.9}
        self.assertEqual(celulas(G2.alocar(m, {self.A: (1, 0, 0)}, G2.AC_PRIMEIRO, desempate="sorteio",
                                           sorteio=sorteio)), {"p": self.A})

    def test_sintetico_ordem_das_cotas(self) -> None:
        m = mercado_sintetico([("a", self.D, 1, 9, "ER", 1), ("b", self.D, 1, 8, "AC", 2),
                               ("c", self.D, 1, 3, "ER", 3)])
        v = {self.D: (1, 1, 0)}
        self.assertEqual(G2.alocar(m, v, G2.AC_PRIMEIRO), {"a": (self.D, "AC"), "c": (self.D, "ER")})
        self.assertEqual(G2.alocar(m, v, G2.RESERVA_PRIMEIRO), {"a": (self.D, "ER"), "b": (self.D, "AC")})

    def test_sintetico_remanescente_de_cota(self) -> None:
        m = mercado_sintetico([("b", self.D, 1, 8, "AC", 1), ("d", self.D, 1, 6, "AC", 2),
                               ("e", self.D, 1, 2, "AC", 3)])
        for ordem in (G2.AC_PRIMEIRO, G2.RESERVA_PRIMEIRO):
            self.assertEqual(G2.alocar(m, {self.D: (1, 1, 0)}, ordem), {"b": (self.D, "AC"), "d": (self.D, "AC_REM")})

    def test_sintetico_boston_difere_so_com_vaga_reservada(self) -> None:
        m = mercado_sintetico([
            ("f", self.E, 1, 9, "AC", 1), ("g", self.E, 1, 8, "AC", 2),
            ("i", self.F, 1, 9, "AC", 1),
            ("h", self.F, 1, 5, "ER", 2), ("h", self.E, 2, 5, "ER", 3),
        ])
        v = {self.E: (1, 1, 0), self.F: (1, 0, 0)}
        self.assertEqual(celulas(G2.alocar(m, v, G2.AC_PRIMEIRO)), {"f": self.E, "h": self.E, "i": self.F})
        self.assertEqual(celulas(G2.boston(m, v, G2.AC_PRIMEIRO)), {"f": self.E, "g": self.E, "i": self.F})
        sem_reserva = {c: (sum(x), 0, 0) for c, x in v.items()}
        m_ac = m.assign(tipo_inscricao="AC")
        self.assertEqual(celulas(G2.alocar(m_ac, sem_reserva, G2.AC_PRIMEIRO)),
                         celulas(G2.boston(m_ac, sem_reserva, G2.AC_PRIMEIRO)))

    def test_sintetico_tipagem_das_vagas_acrescidas(self) -> None:
        self.assertEqual(G2.tipar_acrescimo(4, (2, 1, 1), "divisao_cr"), (2, 1, 1))
        self.assertEqual(G2.tipar_acrescimo(5, (1, 1, 1), "divisao_cr"), (3, 1, 1))
        self.assertEqual(G2.tipar_acrescimo(1, (2, 1, 1), "divisao_cr"), (1, 0, 0))
        self.assertEqual(G2.tipar_acrescimo(3, (2, 1, 1), "divisao_cr"), (2, 1, 0))
        self.assertEqual(G2.tipar_acrescimo(2, (0, 0, 0), "divisao_cr"), (2, 0, 0))
        self.assertEqual(G2.tipar_acrescimo(3, (1, 1, 1), "tudo_ac"), (3, 0, 0))

    def test_sintetico_capacidade_efetiva(self) -> None:
        quadro = pd.DataFrame([{"co_cnes_7d": "sint", "cod_curso": 1, "vagas_imediatas": 1, "vagas_imediatas_ac": 1,
                                "vagas_imediatas_er": 0, "vagas_imediatas_pcd": 0, "vagas_cr": 2, "vagas_cr_ac": 1,
                                "vagas_cr_er": 1, "vagas_cr_pcd": 0},
                               {"co_cnes_7d": "sint", "cod_curso": 2, "vagas_imediatas": 3, "vagas_imediatas_ac": 2,
                                "vagas_imediatas_er": 1, "vagas_imediatas_pcd": 0, "vagas_cr": 0, "vagas_cr_ac": 0,
                                "vagas_cr_er": 0, "vagas_cr_pcd": 0}])
        pub = pd.DataFrame({"id_candidato": ["a", "b", "c", "d"], "celula": [self.A, self.A, self.A, self.B],
                            "tipo_vaga_publicada": ["AC", "AC", "ER", "AC"]})
        cap = G2.capacidade_efetiva(quadro, pub)
        self.assertEqual(cap[self.A], (2, 1, 0))  # 1 imediata + 2 acrescidas pela divisão do CR
        self.assertEqual(cap[self.B], (2, 1, 0))  # publicação abaixo das imediatas: fica o quadro
        self.assertEqual(G2.capacidade_efetiva(quadro, pub, "tudo_ac")[self.A], (3, 0, 0))

    def test_sintetico_aleatorio_estavel_e_igual_a_boston_sem_reserva(self) -> None:
        rng = np.random.default_rng(7)
        for _ in range(40):
            n_cel, n_cand = int(rng.integers(2, 6)), int(rng.integers(3, 15))
            cel = [("sint", k) for k in range(n_cel)]
            vagas = {c: (int(rng.integers(0, 3)), 0, 0) for c in cel}
            linhas = []
            for i in range(n_cand):
                nota = int(rng.integers(0, 6))
                ops = rng.choice(n_cel, size=int(rng.integers(1, 3)), replace=False)
                for o, k in enumerate(ops, start=1):
                    linhas.append((f"s{i}", cel[k], o, nota, "AC", float(rng.random())))
            m = mercado_sintetico(linhas)
            da = celulas(G2.alocar(m, vagas, G2.AC_PRIMEIRO))
            self.assertEqual(da, celulas(G2.boston(m, vagas, G2.AC_PRIMEIRO)))
            # Estabilidade: ninguém prefere uma célula com vaga livre ou com admitido de prioridade pior.
            chave = {(r.id_candidato, r.celula): (r.opcao_rank, -r.pontuacao, r.classificacao_publicada)
                     for r in m.itertuples(index=False)}
            ocup = {c: [p for p, cc in da.items() if cc == c] for c in cel}
            for c, ps in ocup.items():
                self.assertLessEqual(len(ps), vagas[c][0])
            for r in m.itertuples(index=False):
                atual = da.get(r.id_candidato)
                if atual == r.celula:
                    continue
                rank_atual = m[(m.id_candidato == r.id_candidato) & (m.celula == atual)]["opcao_rank"]
                if atual is not None and int(rank_atual.iloc[0]) < r.opcao_rank:
                    continue
                c = r.celula
                self.assertGreaterEqual(len(ocup[c]), vagas[c][0], "vaga livre desejada")
                pior = max((chave[(q, c)] for q in ocup[c]), default=None)
                if pior is not None:
                    self.assertLess(pior, chave[(r.id_candidato, c)], "par bloqueante")


if __name__ == "__main__":
    unittest.main()
