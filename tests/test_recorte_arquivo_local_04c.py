"""Testes do 04c: de que recorte da base do Ipea vem `data/ivs_ipea_2010_municipios.csv`.

Duas partes:

1. O mecanismo "última linha de 2010 com IVS preenchido, sem filtrar a linha
   Total" e as alternativas de `scripts/rdd_bolsa/04c_identificar_recorte_arquivo_local.py`,
   aplicados a uma base SINTÉTICA com a estrutura da planilha do Ipea (linhas
   de subgrupo por município, algumas vazias, uma ausente). Códigos fictícios
   com prefixo 9; valores inventados para identificar a linha escolhida. Nada
   aqui é observação empírica e nada é gravado.
2. Conferência do JSON real versionado `output/rdd_bolsa/identificacao_arquivo_local_ivs.json`:
   o mecanismo reproduz o arquivo inteiro, 4.362 municípios na linha "Negro /
   Mulher / Urbano" e soma da população da linha total igual a 190.755.799.
   A planilha de 210 MB fica fora do Git; o teste que a lê pula se ela faltar.
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
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "04c_identificar_recorte_arquivo_local.py"
SPEC = importlib.util.spec_from_file_location("recorte_arquivo_local_04c", SCRIPT)
R = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(R)

IDENTIFICACAO = ROOT / "output" / "rdd_bolsa" / "identificacao_arquivo_local_ivs.json"
MANIFESTO_A08 = ROOT / "output" / "aquisicao" / "a08_manifesto_ivs_2010_oficial.json"

TOTAL = "Total Cor / Total Sexo / Total Situação de Domicílio"
NMU = "Negro / Mulher / Urbano"
# Ordem das linhas de subgrupo de cada município na planilha (recorte da estrutura real).
ORDEM = [
    TOTAL,
    "Total Cor / Mulher / Total Situação de Domicílio",
    "Total Cor / Mulher / Urbano",
    "Negro / Mulher / Total Situação de Domicílio",
    NMU,
]
# Município SINTÉTICO -> linhas sem IVS (vazias) e linhas ausentes da planilha.
CASOS = {
    "900001": {"vazias": [], "ausentes": []},
    "900002": {"vazias": [NMU], "ausentes": []},
    "900003": {"vazias": [NMU, ORDEM[3]], "ausentes": []},
    "900004": {"vazias": ORDEM[1:], "ausentes": []},
    "900005": {"vazias": [], "ausentes": [NMU]},
}
ESPERADO = {"900001": NMU, "900002": ORDEM[3], "900003": ORDEM[2], "900004": TOTAL, "900005": ORDEM[3]}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def base_sintetica() -> pd.DataFrame:
    """Linhas municipais SINTÉTICAS de 2010 na ordem da planilha (coluna id).

    Cada linha tem valores próprios (o IVS codifica município e linha), para
    que a linha escolhida seja identificável. Linha vazia tem todos os
    indicadores ausentes, como os subgrupos pequenos da base real.
    """
    regs, ident = [], 1
    for m, (co, caso) in enumerate(CASOS.items()):
        for j, linha in enumerate(ORDEM):
            if linha in caso["ausentes"]:
                continue
            cor, sexo, situacao = linha.split(" / ")
            reg = {"id": ident, "co_ibge": co, "cor": cor, "sexo": sexo, "situacao": situacao, "linha": linha}
            vazia = linha in caso["vazias"]
            valores = {
                "ivs": 0.100 + 0.100 * m + 0.010 * j,
                "ivs_infraestrutura_urbana": 0.050 + 0.010 * j,
                "ivs_capital_humano": 0.300 + 0.010 * j,
                "ivs_renda_e_trabalho": 0.200 + 0.010 * j,
                "idhm": 0.600 + 0.010 * j,
                "populacao": 1000.0 * (m + 1) * (len(ORDEM) - j),
                "renda_per_capita": 400.0 + 10.0 * j,
            }
            reg.update({c: (np.nan if vazia else v) for c, v in valores.items()})
            regs.append(reg)
            ident += 1
    return pd.DataFrame(regs)


def arquivo_local_de(candidato: pd.DataFrame) -> pd.DataFrame:
    """Arquivo local SINTÉTICO com o esquema de data/ivs_ipea_2010_municipios.csv."""
    local = candidato.rename(columns={v: k for k, v in R.PARES.items()}).rename(columns={"co_ibge": "cod_ibge6"})
    return local[["cod_ibge6", *R.PARES]].reset_index(drop=True)


class TestMecanismoSintetico(unittest.TestCase):
    def setUp(self) -> None:
        self.base = base_sintetica()

    def test_ultima_linha_preenchida_recua_sobre_vazias_e_ausentes(self) -> None:
        escolhidas = R.ultima_linha_preenchida(self.base).set_index("co_ibge")["linha"].to_dict()
        self.assertEqual(escolhidas, ESPERADO)

    def test_ultima_linha_sem_filtrar_vazias_pega_a_linha_vazia(self) -> None:
        ultima = R.ultima_linha(self.base).set_index("co_ibge")
        self.assertEqual(ultima.loc["900002", "linha"], NMU)
        self.assertTrue(np.isnan(ultima.loc["900002", "ivs"]))
        self.assertEqual(ultima.loc["900005", "linha"], ORDEM[3])  # sem a linha NMU

    def test_linha_total_e_uma_por_municipio(self) -> None:
        total = R.linha_total(self.base)
        self.assertEqual(sorted(total["co_ibge"]), sorted(CASOS))
        self.assertTrue((total["linha"] == TOTAL).all())

    def test_mecanismo_reproduz_todas_as_colunas(self) -> None:
        local = arquivo_local_de(R.ultima_linha_preenchida(self.base))
        conf = R.conferir(local, R.ultima_linha_preenchida(self.base))
        self.assertEqual(conf["municipios"], len(CASOS))
        for col in R.PARES:
            self.assertEqual(conf[col], {"iguais": len(CASOS), "base_vazia": 0}, col)

    def test_alternativas_nao_reproduzem_e_vazio_conta_como_divergencia(self) -> None:
        local = arquivo_local_de(R.ultima_linha_preenchida(self.base))
        total = R.conferir(local, R.linha_total(self.base))
        self.assertEqual(total["ivs_2010"], {"iguais": 1, "base_vazia": 0})  # só 900004, por acaso
        ultima = R.conferir(local, R.ultima_linha(self.base))
        # 900002, 900003 e 900004 têm a última linha vazia; 900001 e 900005 batem.
        self.assertEqual(ultima["ivs_2010"], {"iguais": 2, "base_vazia": 3})

    def test_municipio_ausente_do_candidato_diverge(self) -> None:
        candidato = R.ultima_linha_preenchida(self.base)
        local = arquivo_local_de(candidato)
        conf = R.conferir(local, candidato[candidato["co_ibge"] != "900003"])
        self.assertEqual(conf["ivs_2010"], {"iguais": 4, "base_vazia": 1})

    def test_tolerancias_de_comparacao(self) -> None:
        candidato = R.ultima_linha_preenchida(self.base).reset_index(drop=True)
        local = arquivo_local_de(candidato)
        local.loc[0, "populacao_2010"] += 0.4   # dentro de 0,5
        local.loc[1, "populacao_2010"] += 0.6   # fora
        local.loc[0, "rdpc_2010"] += 0.004      # dentro de 0,005
        local.loc[1, "rdpc_2010"] += 0.006      # fora
        local.loc[0, "ivs_2010"] += 0.0004      # dentro de 0,0005 (3 casas)
        local.loc[1, "ivs_2010"] += 0.0006      # fora
        conf = R.conferir(local, candidato)
        for col in ("populacao_2010", "rdpc_2010", "ivs_2010"):
            self.assertEqual(conf[col]["iguais"], len(CASOS) - 1, col)


class TestIdentificacaoReal(unittest.TestCase):
    """JSON empírico versionado, gerado pelo 04c a partir da planilha oficial."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.ident = json.loads(IDENTIFICACAO.read_text(encoding="utf-8"))

    def test_mecanismo_reproduz_o_arquivo_inteiro(self) -> None:
        mec = self.ident["mecanismo"]
        self.assertTrue(mec["reproduz_o_arquivo_inteiro"])
        conf = mec["conferencia_por_coluna"]
        self.assertEqual(conf["municipios"], 5565)
        for col in R.PARES:
            self.assertEqual(conf[col], {"iguais": 5565, "base_vazia": 0}, col)

    def test_linha_escolhida_por_municipio(self) -> None:
        linhas = self.ident["mecanismo"]["linha_escolhida_por_municipio"]
        self.assertEqual(linhas[NMU], 4362)
        self.assertEqual(linhas[TOTAL], 1)
        self.assertEqual(sum(linhas.values()), 5565)
        nmu = self.ident["linha_negro_mulher_urbano"]
        self.assertEqual(nmu, {"municipios_com_a_linha": 5554, "municipios_com_ivs_vazio_nessa_linha": 1192,
                               "municipios_sem_a_linha": 11})
        self.assertEqual(nmu["municipios_com_a_linha"] - nmu["municipios_com_ivs_vazio_nessa_linha"], linhas[NMU])

    def test_alternativas_nao_reproduzem(self) -> None:
        alt = self.ident["alternativas"]
        self.assertEqual(alt["ultima_linha_sem_filtrar_vazios"]["ivs_2010"]["iguais"], 4362)
        self.assertEqual(alt["linha_total_do_municipio"]["ivs_2010"]["iguais"], 38)

    def test_populacao_da_linha_total_e_o_censo(self) -> None:
        pop = self.ident["populacao"]
        self.assertEqual(pop["soma_linha_total_da_base"], 190_755_799)
        self.assertEqual(pop["censo_2010_brasil"], 190_755_799)
        self.assertTrue(pop["linha_total_igual_ao_censo"])
        local = pd.read_csv(R.LOCAL, dtype={"cod_ibge6": str})
        self.assertEqual(int(pd.to_numeric(local["populacao_2010"], errors="coerce").sum()),
                         pop["soma_arquivo_local"])
        self.assertEqual(pop["soma_arquivo_local"], 41_852_890)

    def test_fontes_conferem(self) -> None:
        fontes = self.ident["fontes"]
        self.assertEqual(fontes[str(R.LOCAL.relative_to(ROOT))], sha256(R.LOCAL))
        manifesto = json.loads(MANIFESTO_A08.read_text(encoding="utf-8"))
        self.assertEqual(fontes[str(R.XLSX.relative_to(ROOT))], manifesto["fonte"]["sha256_xlsx"])

    @unittest.skipUnless(R.XLSX.exists(), "planilha do Ipea fora do Git; rode scripts/aquisicao/a08_*")
    def test_planilha_preservada_e_a_do_json(self) -> None:
        self.assertEqual(sha256(R.XLSX), self.ident["fontes"][str(R.XLSX.relative_to(ROOT))])


if __name__ == "__main__":
    unittest.main()
