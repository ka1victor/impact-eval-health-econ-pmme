"""Testes do 04b: IVS 2010 oficial do Ipea contra o escore administrativo do MS.

Duas partes:

1. Funções puras de `scripts/rdd_bolsa/04b_validar_ivs_oficial_escore_administrativo.py`
   com dados SINTÉTICOS: municípios com código fictício (prefixo 9, inexistente
   no IBGE), escores e faixas montados em memória. Nada aqui é observação
   empírica e nada é gravado.
2. Conferência das saídas reais versionadas: `output/rdd_bolsa/portao_r1_ivs_oficial.json`
   (404/404 valores, 5.565/5.565 categorias, 368/368 em P1, 454/454 em P2,
   APROVADO_SHARP) e `output/rdd_bolsa/escore_completo_ivs2010_oficial.csv`,
   recalculados a partir das entradas versionadas com as mesmas funções.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "04b_validar_ivs_oficial_escore_administrativo.py"
SPEC = importlib.util.spec_from_file_location("validar_ivs_oficial_04b", SCRIPT)
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)

PORTAO = ROOT / "output" / "rdd_bolsa" / "portao_r1_ivs_oficial.json"
ESCORE_COMPLETO = ROOT / "output" / "rdd_bolsa" / "escore_completo_ivs2010_oficial.csv"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def oficial_sintetico(s_mil: list[int], inicio: int = 0) -> pd.DataFrame:
    """IVS oficial SINTÉTICO em milésimos, com código fictício 9xxxxx."""
    return pd.DataFrame({
        "co_ibge": [f"{900000 + inicio + i:06d}" for i in range(len(s_mil))],
        "s_mil": s_mil,
    })


def administrativo_de(of: pd.DataFrame) -> pd.DataFrame:
    """Escore administrativo SINTÉTICO igual ao oficial (como o do MS)."""
    return pd.DataFrame({"co_ibge": of["co_ibge"], "s_mil_adm": of["s_mil"]})


def categoria_de(of: pd.DataFrame) -> pd.DataFrame:
    """Categoria administrativa SINTÉTICA coerente com as classes do Atlas."""
    return pd.DataFrame({"co_ibge": of["co_ibge"], "categoria_ivs_admin": of["s_mil"].map(V.categoria)})


def matriz_de(of: pd.DataFrame, quadros: dict[str, list[str]]) -> pd.DataFrame:
    """Quadros de vagas SINTÉTICOS: faixa anunciada pela regra de dois cortes."""
    faixa = dict(zip(of["co_ibge"], of["s_mil"].map(V.faixa)))
    linhas = [
        {"quadro": quadro, "co_ibge": co, "faixa_anunciada": faixa.get(co, "FAIXA 1")}
        for quadro, municipios in quadros.items()
        for co in municipios
    ]
    return pd.DataFrame(linhas)


class TestRegraECategoria(unittest.TestCase):
    def test_corte_pertence_ao_lado_inferior(self) -> None:
        esperado = {0: "FAIXA 3", 300: "FAIXA 3", 301: "FAIXA 2", 400: "FAIXA 2", 401: "FAIXA 1", 1000: "FAIXA 1"}
        for s, f in esperado.items():
            self.assertEqual(V.faixa(s), f, s)

    def test_classes_do_atlas(self) -> None:
        esperado = {
            200: "MUITO BAIXA VULNERABILIDADE", 201: "BAIXA VULNERABILIDADE",
            300: "BAIXA VULNERABILIDADE", 301: "MEDIA VULNERABILIDADE",
            400: "MEDIA VULNERABILIDADE", 401: "ALTA VULNERABILIDADE",
            500: "ALTA VULNERABILIDADE", 501: "MUITO ALTA VULNERABILIDADE",
        }
        for s, c in esperado.items():
            self.assertEqual(V.categoria(s), c, s)

    def test_milesimos_tres_casas(self) -> None:
        self.assertEqual(V.milesimos(pd.Series([0.3, 0.301, 0.4004, 0.3996])).tolist(), [300, 301, 400, 400])


class TestConferenciaSintetica(unittest.TestCase):
    def setUp(self) -> None:
        rng = np.random.default_rng(20261018)
        self.of = oficial_sintetico(rng.integers(150, 651, size=500).tolist())
        # Escore publicado só para um subconjunto (como os 404 da relação nominal).
        self.adm = administrativo_de(self.of.iloc[::5].reset_index(drop=True))
        self.cat = categoria_de(self.of)

    def test_escore_e_categoria_iguais(self) -> None:
        c = V.conferir_escore_administrativo(self.of, self.adm, self.cat)
        self.assertEqual(c, {"valores_iguais": 100, "valores_comparados": 100,
                             "categorias_iguais": 500, "categorias_comparadas": 500})
        self.assertTrue(V.escore_confere(c))

    def test_um_milesimo_de_diferenca_reprova(self) -> None:
        adm = self.adm.copy()
        adm.loc[7, "s_mil_adm"] += 1
        c = V.conferir_escore_administrativo(self.of, adm, self.cat)
        self.assertEqual(c["valores_iguais"], 99)
        self.assertFalse(V.escore_confere(c))

    def test_municipio_sem_ivs_oficial_conta_como_divergencia(self) -> None:
        adm = pd.concat([self.adm, pd.DataFrame({"co_ibge": ["999999"], "s_mil_adm": [300]})], ignore_index=True)
        c = V.conferir_escore_administrativo(self.of, adm, self.cat)
        self.assertEqual((c["valores_iguais"], c["valores_comparados"]), (100, 101))
        self.assertFalse(V.escore_confere(c))

    def test_categoria_fora_da_base_oficial_nao_entra_na_conta(self) -> None:
        # Município criado depois de 2010 (sem IVS oficial): fica fora, como os 6 do consolidado PMMB.
        cat = pd.concat([self.cat, pd.DataFrame({"co_ibge": ["999999"],
                                                 "categoria_ivs_admin": ["ALTA VULNERABILIDADE"]})])
        c = V.conferir_escore_administrativo(self.of, self.adm, cat)
        self.assertEqual((c["categorias_iguais"], c["categorias_comparadas"]), (500, 500))

    def test_categoria_divergente_reprova(self) -> None:
        cat = self.cat.copy()
        cat.loc[3, "categoria_ivs_admin"] = "MUITO ALTA VULNERABILIDADE" if V.categoria(
            int(self.of.loc[3, "s_mil"])) != "MUITO ALTA VULNERABILIDADE" else "BAIXA VULNERABILIDADE"
        c = V.conferir_escore_administrativo(self.of, self.adm, cat)
        self.assertEqual(c["categorias_iguais"], 499)
        self.assertFalse(V.escore_confere(c))


class TestReproducaoDaRegraSintetica(unittest.TestCase):
    POPS = {"P1": ["c1_ch1"], "P2": ["c2_ch1", "c2_ch2"], "ciclo_3_congelado": ["c3_ch1"]}

    def setUp(self) -> None:
        rng = np.random.default_rng(20261019)
        self.of = oficial_sintetico(rng.integers(150, 651, size=300).tolist())
        co = self.of["co_ibge"].tolist()
        # P2 é a união de duas chamadas com municípios em comum.
        self.quadros = {"c1_ch1": co[:120], "c2_ch1": co[100:220], "c2_ch2": co[200:260], "c3_ch1": co[150:300]}
        self.matriz = matriz_de(self.of, self.quadros)
        self.conf = V.conferir_escore_administrativo(self.of, administrativo_de(self.of), categoria_de(self.of))

    def test_regra_reproduzida_aprova_sharp(self) -> None:
        pops = V.reproduzir_regra(self.matriz, self.of, self.POPS)
        self.assertEqual(pops["P1"], {"municipios": 120, "com_ivs_oficial": 120, "sem_ivs_oficial": [],
                                      "regra_reproduz": 120})
        self.assertEqual(pops["P2"]["municipios"], 160)  # 100..259, sem contar duas vezes 200..219
        self.assertEqual(pops["P2"]["regra_reproduz"], 160)
        self.assertEqual(V.decidir_r1(self.conf, pops), "APROVADO_SHARP")

    def test_faixa_anunciada_divergente_nao_e_sharp(self) -> None:
        matriz = self.matriz.copy()
        i = matriz.index[matriz["quadro"] == "c1_ch1"][0]
        matriz.loc[i, "faixa_anunciada"] = "FAIXA 1" if matriz.loc[i, "faixa_anunciada"] != "FAIXA 1" else "FAIXA 3"
        pops = V.reproduzir_regra(matriz, self.of, self.POPS)
        self.assertEqual(pops["P1"]["regra_reproduz"], 119)
        self.assertEqual(V.decidir_r1(self.conf, pops), "REPROVADO")

    def test_municipio_de_p2_sem_ivs_oficial_reprova(self) -> None:
        sem = self.quadros["c2_ch2"][-1]
        of = self.of[self.of["co_ibge"] != sem]
        pops = V.reproduzir_regra(self.matriz, of, self.POPS)
        self.assertEqual(pops["P2"]["sem_ivs_oficial"], [sem])
        self.assertEqual(pops["P2"]["com_ivs_oficial"], pops["P2"]["municipios"] - 1)
        self.assertEqual(V.decidir_r1(self.conf, pops), "REPROVADO")

    def test_ciclo_3_incompleto_nao_entra_na_decisao(self) -> None:
        # Como 422000, criado depois de 2010: relatado, sem mudar a decisão sobre P1 e P2.
        matriz = pd.concat([self.matriz, pd.DataFrame({"quadro": ["c3_ch1"], "co_ibge": ["999999"],
                                                       "faixa_anunciada": ["FAIXA 1"]})], ignore_index=True)
        pops = V.reproduzir_regra(matriz, self.of, self.POPS)
        self.assertEqual(pops["ciclo_3_congelado"]["sem_ivs_oficial"], ["999999"])
        self.assertEqual(V.decidir_r1(self.conf, pops), "APROVADO_SHARP")

    def test_escore_que_nao_confere_reprova_mesmo_com_regra_perfeita(self) -> None:
        pops = V.reproduzir_regra(self.matriz, self.of, self.POPS)
        conf = dict(self.conf, valores_iguais=self.conf["valores_comparados"] - 1)
        self.assertEqual(V.decidir_r1(conf, pops), "REPROVADO")


class TestSaidaRealPortaoR1(unittest.TestCase):
    """Saídas empíricas versionadas, recalculadas a partir das entradas versionadas."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.portao = json.loads(PORTAO.read_text(encoding="utf-8"))

    def test_decisao_e_contagens(self) -> None:
        p = self.portao
        self.assertEqual(p["decisao_r1"], "APROVADO_SHARP")
        self.assertFalse(p["outcomes_abertos"])
        self.assertEqual(p["escore_administrativo_e_ivs_2010_oficial"],
                         {"valores_iguais_3_casas": "404/404", "categorias_iguais": "5565/5565"})
        pops = p["populacoes"]
        self.assertEqual(pops["P1"], {"municipios": 368, "com_ivs_oficial": 368, "sem_ivs_oficial": [],
                                      "regra_reproduz": 368})
        self.assertEqual(pops["P2"], {"municipios": 454, "com_ivs_oficial": 454, "sem_ivs_oficial": [],
                                      "regra_reproduz": 454})
        self.assertEqual(pops["ciclo_3_congelado"], {"municipios": 748, "com_ivs_oficial": 747,
                                                     "sem_ivs_oficial": ["422000"], "regra_reproduz": 747})

    def test_fontes_conferem_com_os_arquivos(self) -> None:
        for rel, h in self.portao["fontes"].items():
            self.assertEqual(sha256(ROOT / rel), h, f"{rel} mudou depois do portão R1")

    def test_recalculo_com_as_funcoes_do_script(self) -> None:
        of = pd.read_csv(V.OFICIAL, dtype={"co_ibge": str})
        of["s_mil"] = V.milesimos(of["ivs"])
        adm = pd.read_csv(V.ADMIN, dtype={"co_ibge": str})
        adm["s_mil_adm"] = V.milesimos(adm["ivs_admin"])
        cat = pd.read_csv(V.CATEGORIA, dtype={"co_ibge": str})
        conf = V.conferir_escore_administrativo(of, adm, cat)
        pops = V.reproduzir_regra(pd.read_csv(V.MATRIZ, dtype={"co_ibge": str}), of)
        self.assertEqual((conf["valores_iguais"], conf["valores_comparados"]), (404, 404))
        self.assertEqual((conf["categorias_iguais"], conf["categorias_comparadas"]), (5565, 5565))
        self.assertEqual(pops, self.portao["populacoes"])
        self.assertEqual(V.decidir_r1(conf, pops), self.portao["decisao_r1"])

    def test_escore_completo_e_o_ivs_oficial_a_tres_casas(self) -> None:
        self.assertEqual(self.portao["saida_escore_completo"], str(ESCORE_COMPLETO.relative_to(ROOT)))
        texto = pd.read_csv(ESCORE_COMPLETO, dtype=str)
        self.assertEqual(list(texto.columns), ["co_ibge", "ivs_admin"])
        self.assertTrue(texto["ivs_admin"].str.fullmatch(r"[01]\.\d{3}").all())
        escore = pd.read_csv(ESCORE_COMPLETO, dtype={"co_ibge": str})
        self.assertEqual(len(escore), 5565)
        self.assertTrue(escore["co_ibge"].is_unique)
        of = pd.read_csv(V.OFICIAL, dtype={"co_ibge": str})
        j = escore.merge(of[["co_ibge", "ivs"]], on="co_ibge", how="outer", indicator=True)
        self.assertTrue((j["_merge"] == "both").all())
        self.assertTrue((V.milesimos(j["ivs_admin"]) == V.milesimos(j["ivs"])).all())


if __name__ == "__main__":
    unittest.main()
