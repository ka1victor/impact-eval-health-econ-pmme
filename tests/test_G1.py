"""Testes do portão G1 (`scripts/rdd_bolsa/G1_identificar_candidatos.py`; doc 51, §5, onda 1).

Três partes:

1. `TestG1Sintetico`: dados SINTÉTICOS, montados em memória (candidatos, máscaras de
   CPF, dicionário e conjuntos de busca fictícios), nunca gravados. Conferem a leitura
   da máscara, a chave do CPF, a regra de ligação (CPF + nome idêntico; CPF + nome
   compatível; ambíguos fora; profissional repetido no ciclo fora), a sensibilidade só
   por nome, a competência de referência e o veredito.
2. `TestG1SaidasReais`: invariantes das saídas EMPÍRICAS `output/rdd_bolsa/G1_*`:
   natureza e estatuto, universo igual ao de `escolhas_candidatos`, taxas do resumo
   recalculadas do parquet, nenhum dado pessoal, nenhuma coluna de IVS, faixa ou
   outcome, nenhuma competência >= 202609, hashes das saídas.
3. `TestDocG1`: os blocos `<!-- G1:... -->` do doc de auditoria são idênticos aos
   gerados das saídas.
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
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "G1_identificar_candidatos.py"
_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location("g1_candidatos", SCRIPT)
G1 = importlib.util.module_from_spec(_spec)
sys.modules["g1_candidatos"] = G1
_spec.loader.exec_module(G1)
sys.dont_write_bytecode = _bytecode

TEM_SAIDAS = all(p.exists() for p in (G1.OUT_RESUMO, G1.OUT_CANDIDATOS, G1.OUT_DISTANCIAS, G1.OUT_INVENTARIO))


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


# --------------------------------------------------------------------------
# 1. Sintético (só em memória)
# --------------------------------------------------------------------------

PADRAO = "0-1-2-3-4-9-10"


def _cand_sintetico(linhas: list[tuple]) -> pd.DataFrame:
    df = pd.DataFrame(linhas, columns=["ciclo", "id_candidato", "_nome", "_cpf"])
    m = df["_cpf"].map(G1.mascara_cpf)
    df["_padrao"] = m.map(lambda x: x[0] if x else None)
    df["_chave"] = [G1.chave_cpf(x[0], x[1]) if x else None for x in m]
    return df


def _dic_sintetico(linhas: list[tuple]) -> pd.DataFrame:
    df = pd.DataFrame(linhas, columns=["co_profissional_sus", "nome_norm", "_cpf"])
    df[f"chave_{PADRAO}"] = [G1.chave_cpf(PADRAO, G1.digitos_no_padrao(c, PADRAO)) for c in df["_cpf"]]
    return df.drop(columns="_cpf")


class TestG1Sintetico(unittest.TestCase):
    """Regra de ligação com registros SINTÉTICOS (nomes e CPFs fictícios)."""

    def test_mascara(self) -> None:
        self.assertEqual(G1.mascara_cpf("12345XXXX67"), (PADRAO, "1234567"))
        self.assertEqual(G1.mascara_cpf("123.45X.XXX-67"), (PADRAO, "1234567"))
        self.assertEqual(G1.mascara_cpf("***.456.789-**"), ("3-4-5-6-7-8", "456789"))
        self.assertIsNone(G1.mascara_cpf("EBE12XXXXC6"))  # letra fora de X/*
        self.assertIsNone(G1.mascara_cpf("123XXXXXXXX"))  # poucos dígitos visíveis
        self.assertIsNone(G1.mascara_cpf("1234567"))  # comprimento errado
        self.assertIsNone(G1.mascara_cpf(None))

    def test_chave_nas_posicoes_comuns(self) -> None:
        cnes = "3-4-5-6-7-8"
        self.assertEqual(G1.posicoes_comuns(PADRAO, cnes), "3-4")
        self.assertEqual(G1.posicoes_comuns("0-1-2", "9-10"), "")
        # Mesmo CPF fictício (12345678901) mascarado de dois jeitos: a chave nas posições comuns coincide.
        k_cand = G1.chave_cpf(PADRAO, "1234501", "3-4")
        k_cnes = G1.chave_cpf(cnes, "456789", G1.posicoes_comuns(PADRAO, cnes))
        self.assertEqual(k_cand, k_cnes)
        self.assertNotEqual(k_cand, G1.chave_cpf(cnes, "996789", "3-4"))
        self.assertIsNone(G1.chave_cpf(PADRAO, "1234501", ""))
        c = G1.chaves_candidatos(pd.DataFrame({"_cpf": ["12345XXXX01", "EBE12XXXXC6"]}), cnes)
        self.assertEqual(c["_chave"].iloc[0], k_cnes)
        self.assertTrue(pd.isna(c["_chave"].iloc[1]))
        self.assertEqual(G1.mascara_cpf("***.456.789-**", 1), ("3-4-5-6-7-8", "456789"))
        self.assertEqual(G1.digitos_no_padrao("12345678901", PADRAO), "1234501")
        self.assertEqual(G1.digitos_no_padrao("12345678901", "3-4-5-6-7-8"), "456789")

    def test_moldes_consistentes(self) -> None:
        self.assertTrue(G1.moldes_consistentes(PADRAO, "1234501", "3-4-5-6-7-8", "456789"))
        self.assertFalse(G1.moldes_consistentes(PADRAO, "1234501", "3-4-5-6-7-8", "999789"))
        self.assertIsNone(G1.moldes_consistentes("0-1-2-3-4-5", "123456", "6-7-8-9-10", "78901"))

    def setUp(self) -> None:
        # CPFs fictícios de 11 dígitos; a máscara mostra posições 0-4 e 9-10.
        self.dic = _dic_sintetico([
            ("P1", "ANA SOUZA LIMA", "11111222233"),     # c1: CPF + nome idêntico
            ("P2", "BRUNO COSTA", "22222333344"),        # c2: CPF + nome compatível (nome do meio a mais)
            ("P3", "CARLA DIAS", "33333444455"),         # c3 e c3b: mesmo CPF visível, dois profissionais
            ("P4", "CARLA DIAS", "33333999955"),
            ("P5", "DANIEL REIS", "44444555566"),        # c4: CPF igual, nome incompatível
            ("P6", "EVA ROCHA", "55555666677"),          # c5: fora do conjunto de busca
            ("P7", "FABIO NUNES", "66666777788"),        # c6 e c7 ligariam ao mesmo profissional
        ])
        self.cands = _cand_sintetico([
            (1, "c1_00001", "ANA SOUZA LIMA", "11111XXXX33"),
            (1, "c1_00002", "BRUNO HENRIQUE COSTA", "22222XXXX44"),
            (1, "c1_00003", "CARLA DIAS", "33333XXXX55"),
            (1, "c1_00004", "MARIA REIS", "44444XXXX66"),
            (1, "c1_00005", "EVA ROCHA", "55555XXXX77"),
            (1, "c1_00006", "FABIO NUNES", "66666XXXX88"),
            (1, "c1_00007", "FABIO NUNES", "66666XXXX88"),
            (1, "c1_00008", "GIL PRADO", "EBE12XXXXC6"),
        ])
        self.pool = {1: {"P1", "P2", "P3", "P4", "P5", "P7"}}

    def test_regra_principal(self) -> None:
        r = G1.ligar(self.cands, self.dic, self.pool, usar_cpf=True).set_index("id_candidato")
        self.assertEqual(r.at["c1_00001", "co_profissional_sus"], "P1")
        self.assertEqual(r.at["c1_00001", "etapa_ligacao"], "1_cpf_nome_identico")
        self.assertEqual(r.at["c1_00002", "co_profissional_sus"], "P2")
        self.assertEqual(r.at["c1_00002", "etapa_ligacao"], "2_cpf_nome_compativel")
        self.assertEqual(r.at["c1_00003", "motivo"], "ambiguo_cpf_nome_identico_com_mais_de_um_profissional")
        self.assertEqual(r.at["c1_00004", "motivo"], "cpf_compativel_sem_nome_compativel")
        self.assertEqual(r.at["c1_00005", "motivo"], "sem_profissional_com_cpf_compativel_no_conjunto_de_busca")
        for c in ("c1_00006", "c1_00007"):
            self.assertEqual(r.at[c, "motivo"], "ambiguo_profissional_ligado_a_mais_de_um_candidato_do_ciclo")
            self.assertEqual(r.at[c, "ligado"], 0)
        self.assertEqual(r.at["c1_00008", "motivo"], "mascara_cpf_invalida")
        self.assertEqual(int(r["ligado"].sum()), 2)
        self.assertTrue(r.loc[r["ligado"] == 0, "co_profissional_sus"].isna().all())

    def test_sensibilidade_so_nome(self) -> None:
        r = G1.ligar(self.cands, self.dic, self.pool, usar_cpf=False).set_index("id_candidato")
        self.assertEqual(r.at["c1_00001", "co_profissional_sus"], "P1")
        self.assertEqual(r.at["c1_00002", "motivo"], "sem_nome_identico_no_conjunto_de_busca")
        self.assertEqual(r.at["c1_00003", "motivo"], "ambiguo_homonimos_no_conjunto_de_busca")
        self.assertEqual(r.at["c1_00005", "motivo"], "sem_nome_identico_no_conjunto_de_busca")  # fora do conjunto
        self.assertEqual(r.at["c1_00008", "motivo"], "sem_nome_identico_no_conjunto_de_busca")

    def test_conjunto_de_busca_restringe(self) -> None:
        pool = {1: {"P2", "P3", "P4", "P5", "P7"}}  # sem P1
        r = G1.ligar(self.cands, self.dic, pool, usar_cpf=True).set_index("id_candidato")
        self.assertEqual(r.at["c1_00001", "ligado"], 0)

    def test_competencia_de_referencia(self) -> None:
        for k, ref in G1.REFERENCIA.items():
            self.assertLess(ref, G1.ABERTURA_INSCRICOES[k])
            self.assertLess(ref, G1.LIMITE_EXCLUSIVO)
            posteriores = [c for c in G1.COMPETENCIAS_X1 if ref < c < G1.ABERTURA_INSCRICOES[k]]
            self.assertEqual(posteriores, [], "a referência é a última competência antes das inscrições")
        self.assertLess(G1.COMPETENCIA_DICIONARIO, G1.LIMITE_EXCLUSIVO)

    def _tx(self, taxa: float, amb: float = 0.0, dif: float = 0.0) -> dict:
        b = {"taxa_com_municipio_de_origem": taxa, "fracao_ambiguos": amb,
             "diferenca_alocados_menos_nao_alocados": dif}
        return {k: dict(b) for k in ("1", "2", "3")}

    def _meta(self, cobertura_c1: float = 1.0) -> dict:
        cob = {c: {"fracao": 1.0} for c in G1.COMPETENCIAS_X1}
        cob[G1.REFERENCIA[1]] = {"fracao": cobertura_c1}
        return {"cobertura_do_dicionario_sobre_medicos_x1": cob}

    def _chave(self, n: int = 6) -> dict:
        return {k: {"n_posicoes": n} for k in ("1", "2", "3")}

    def test_veredito(self) -> None:
        ok = {"concordancia": 0.99}
        v = G1.veredito(self._tx(0.9), ok, self._meta(), self._chave())
        self.assertEqual(v["veredito"], "VIAVEL")
        v = G1.veredito(self._tx(0.9), ok, self._meta(cobertura_c1=0.9), self._chave())
        self.assertEqual(v["por_ciclo"]["1"]["veredito"], "VIAVEL_PARCIAL")
        self.assertEqual(v["por_ciclo"]["3"]["veredito"], "VIAVEL")
        self.assertEqual(v["veredito"], "VIAVEL_PARCIAL")
        self.assertEqual(G1.veredito(self._tx(0.3), ok, self._meta(), self._chave())["veredito"], "INVIAVEL")
        self.assertEqual(G1.veredito(self._tx(0.9), {"concordancia": 0.5}, self._meta(), self._chave())["veredito"],
                         "INVIAVEL")
        self.assertEqual(G1.veredito(self._tx(0.9), {"concordancia": 0.95}, self._meta(), self._chave())["veredito"],
                         "VIAVEL_PARCIAL")
        self.assertEqual(G1.veredito(self._tx(0.9), ok, self._meta(), self._chave(0))["veredito"], "INVIAVEL")
        v = G1.veredito(self._tx(0.9, dif=0.2), ok, self._meta(), self._chave())
        self.assertEqual(v["por_ciclo"]["3"]["veredito"], "VIAVEL_PARCIAL")
        v = G1.veredito(self._tx(0.9), ok, self._meta(), self._chave(2))  # chave curta: só informativo
        self.assertEqual(v["veredito"], "VIAVEL")
        self.assertTrue(v["por_ciclo"]["1"]["motivos"])


# --------------------------------------------------------------------------
# 2. Saídas reais
# --------------------------------------------------------------------------

@unittest.skipUnless(TEM_SAIDAS, "saídas do G1 ausentes")
class TestG1SaidasReais(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.resumo = json.loads(G1.OUT_RESUMO.read_text(encoding="utf-8"))
        cls.cand = pd.read_parquet(G1.OUT_CANDIDATOS)
        cls.dist = pd.read_parquet(G1.OUT_DISTANCIAS)
        cls.inv = pd.read_csv(G1.OUT_INVENTARIO)
        cls.esc = pd.read_parquet(G1.ESCOLHAS)

    def test_rotulos(self) -> None:
        self.assertEqual(self.resumo["natureza_dos_dados"], "EMPIRICO")
        self.assertEqual(self.resumo["estatuto"], G1.ESTATUTO)
        for df in (self.cand, self.dist, self.inv):
            self.assertEqual(set(df["natureza_dos_dados"]), {"EMPIRICO"})
        self.assertEqual(set(self.cand["estatuto"]), {G1.ESTATUTO})

    def test_universo_igual_ao_de_escolhas(self) -> None:
        alvo = set(zip(self.esc["ciclo"], self.esc["id_candidato"]))
        for regra, g in self.cand.groupby("regra_ligacao"):
            self.assertEqual(set(zip(g["ciclo"], g["id_candidato"])), alvo, regra)
            self.assertFalse(g.duplicated(["ciclo", "id_candidato"]).any())
        self.assertEqual(set(self.cand["regra_ligacao"]), set(G1.REGRAS))
        self.assertEqual(len(self.dist), len(self.esc))
        aloc = self.esc.groupby(["ciclo", "id_candidato"])["alocado"].max()
        c = self.cand.set_index(["ciclo", "id_candidato"])
        for regra, g in c.groupby("regra_ligacao"):
            self.assertTrue((g["alocado_1a_chamada"] == aloc.loc[g.index]).all())

    def test_sem_dados_pessoais_nem_contraste(self) -> None:
        proibidas = re.compile(r"nome|cpf|crm|cns|profissional_sus|registro|ivs|faixa|s_mil|corte|pontuacao|outcome",
                               re.I)
        for df in (self.cand, self.dist):
            self.assertEqual([c for c in df.columns if proibidas.search(c)], [])
        self.assertTrue(self.cand["id_candidato"].str.fullmatch(r"c[123]_\d{5}").all())
        self.assertNotIn("ivs", json.dumps(self.resumo["entradas"]).lower().replace("ivs_administrativo", ""))
        texto = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("a08_ivs", texto)
        self.assertNotIn("ivs_ipea", texto)

    def test_competencias(self) -> None:
        self.assertLess(self.resumo["dicionario_cnes"]["competencia"], "202609")
        for c in self.resumo["cache_x1"]:
            self.assertLess(c, "202609")
        self.assertTrue(set(self.cand["competencia_referencia"].dropna()) <= set(G1.REFERENCIA.values()))
        self.assertTrue(self.resumo["dicionario_cnes"]["sha256_igual_ao_a09"])

    def test_taxas_recalculadas(self) -> None:
        for regra, g in self.cand.groupby("regra_ligacao"):
            tx = self.resumo["taxas_ligacao"][regra]
            for k in ("1", "2", "3", "total"):
                d = g if k == "total" else g[g["ciclo"] == int(k)]
                t = tx[k]
                self.assertEqual(t["candidatos"], len(d))
                self.assertEqual(t["ligados"], int(d["ligado"].sum()))
                self.assertAlmostEqual(t["taxa"], d["ligado"].mean(), places=12)
                self.assertEqual(t["ambiguos"], int(d["motivo"].str.startswith("ambiguo").sum()))
                self.assertAlmostEqual(t["taxa_com_municipio_de_origem"], d["co_ibge_origem"].notna().mean(),
                                       places=12)
                for nome, a in (("alocados", 1), ("nao_alocados", 0)):
                    s = d[d["alocado_1a_chamada"] == a]
                    self.assertEqual(t[nome]["ligados"], int(s["ligado"].sum()))
                self.assertEqual(t["motivos"], {m: int(n) for m, n in d["motivo"].value_counts().items()})

    def test_ausente_tem_motivo(self) -> None:
        self.assertTrue((self.cand.loc[self.cand["ligado"] == 0, "motivo"] != "ligado").all())
        self.assertTrue((self.cand.loc[self.cand["ligado"] == 1, "motivo"] == "ligado").all())
        sem = self.cand["co_ibge_origem"].isna()
        self.assertTrue(self.cand.loc[sem, "motivo_origem_ausente"].notna().all())
        sem_d = self.dist["dist_km_origem_mais_proxima"].isna()
        self.assertTrue((self.dist.loc[sem_d, "motivo_distancia_ausente"] != "").all())
        self.assertTrue((self.dist.loc[~sem_d, "motivo_distancia_ausente"] == "").all())
        self.assertTrue((self.dist["dist_km_origem_mais_proxima"].dropna() >= 0).all())
        ok = self.dist.dropna(subset=["dist_km_origem_principal"])
        self.assertTrue((ok["dist_km_origem_mais_proxima"] <= ok["dist_km_origem_principal"] + 1e-9).all())

    def test_validacao_rota_x1(self) -> None:
        g = self.cand[self.cand["regra_ligacao"] == "g1_cpf_nome"]
        v = self.resumo["validacao_rota_x1"]["g1_cpf_nome"]
        self.assertEqual(v["candidatos_ligados_pela_rota_x1"], int((g["ligado_rota_x1"] == 1).sum()))
        self.assertEqual(v["mesmo_profissional"], int((g["mesmo_profissional_rota_x1"] == 1).sum()))
        self.assertEqual(v["ligados_tambem_pela_regra"], int(g["mesmo_profissional_rota_x1"].notna().sum()))
        self.assertTrue(g.loc[g["ciclo"] == 3, "ligado_rota_x1"].isna().all())

    def test_veredito_reproduz(self) -> None:
        meta = {"cobertura_do_dicionario_sobre_medicos_x1":
                self.resumo["dicionario_cnes"]["cobertura_do_dicionario_sobre_medicos_x1"]}
        v = G1.veredito(self.resumo["taxas_ligacao"]["g1_cpf_nome"], self.resumo["validacao_rota_x1"]["g1_cpf_nome"],
                        meta, self.resumo["chave_cpf_por_ciclo"])
        self.assertEqual(v, self.resumo["veredito"])
        self.assertIn(v["veredito"], {"VIAVEL", "VIAVEL_PARCIAL", "INVIAVEL"})
        # A chave do CPF usa as posições visíveis nas duas máscaras (o CO_CPF público também é mascarado).
        d = self.resumo["dicionario_cnes"]
        for k, x in self.resumo["chave_cpf_por_ciclo"].items():
            self.assertEqual(x["posicoes_comuns_com_co_cpf"],
                             G1.posicoes_comuns(x["padrao_candidato"], d["padrao_co_cpf_dominante"]))

    def test_validacao_entre_ciclos(self) -> None:
        for regra in G1.REGRAS:
            for par, x in self.resumo["validacao_rota_x1"][regra]["entre_ciclos"].items():
                self.assertLessEqual(x["mesmo_profissional"], x["ligados_nos_dois"])
                self.assertLessEqual(x["ligados_nos_dois"], x["pares_mesma_pessoa"])

    def test_hashes_das_saidas(self) -> None:
        for p, h in self.resumo["saidas"].items():
            self.assertEqual(sha256(ROOT / p), h, p)

    def test_inventario(self) -> None:
        self.assertEqual(int(self.inv["tem_crm"].sum()), 0)
        self.assertEqual(int(self.inv["tem_uf_do_crm"].sum()), 0)
        self.assertTrue((self.inv["tem_nome"] == 1).all())
        base = self.inv[self.inv["papel"].str.contains("base de escolhas")]
        self.assertEqual(sorted(base["ciclo"].unique().tolist()), [1, 2, 3])
        self.assertTrue((base["candidatos_de_escolhas_presentes"] == base["candidatos_de_escolhas_no_ciclo"]).all())


# --------------------------------------------------------------------------
# 3. Documento
# --------------------------------------------------------------------------

@unittest.skipUnless(TEM_SAIDAS and G1.DOC.exists(), "saídas ou doc do G1 ausentes")
class TestDocG1(unittest.TestCase):
    def test_blocos_iguais_aos_gerados(self) -> None:
        resumo, inv, cand = G1.ler_saidas()
        gerados = G1.blocos_doc(resumo, inv, cand)
        texto = G1.DOC.read_text(encoding="utf-8")
        no_doc = {m.group("nome"): m.group("corpo") for m in G1.MARCA.finditer(texto)}
        self.assertEqual(set(no_doc), set(gerados))
        for nome, corpo in gerados.items():
            self.assertEqual(no_doc[nome], corpo, nome)


if __name__ == "__main__":
    unittest.main()
