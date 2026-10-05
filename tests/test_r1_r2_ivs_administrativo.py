"""Invariantes do R1 e do R2 do RDD da bolsa com o IVS administrativo da SGTES.

O R1 so vale enquanto a regra acertar todos os municipios de todas as ondas; um
unico erro derruba o "sharp". O R2 so vale enquanto nao ler outcome e enquanto
registrar tambem o criterio que reprovou, nao so o que aprovou.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
R1 = ROOT / "output" / "rdd_bolsa" / "a01c_regra_ivs_administrativo.json"
MATRIZ = ROOT / "output" / "rdd_bolsa" / "matriz_municipio_ivs_administrativo.csv"
R2 = ROOT / "output" / "rdd_bolsa" / "r2_portao.json"
TESTES_R2 = ROOT / "output" / "rdd_bolsa" / "r2_testes_continuidade.csv"
MANIFESTO = ROOT / "output" / "aquisicao" / "a07_manifesto_ivs_administrativo.json"
SCRIPT_R1 = ROOT / "scripts" / "rdd_bolsa" / "01c_reconstruir_regra_ivs_administrativo.py"
SCRIPT_R2 = ROOT / "scripts" / "rdd_bolsa" / "04_auditar_r2_suporte_selecao_balanco.py"
PROTOCOLO_R3 = ROOT / "output" / "rdd_bolsa" / "registro_pre_analise.json"

# Arquivos e colunas de desfecho do projeto. Nenhum script de R1/R2 pode le-los.
MARCAS_DE_OUTCOME = (
    "matriz_funil",
    "homologados",
    "alocacao",
    "resultado_final",
    "classificacao",
    "painel_cnes",
    "qtd_ativos",
    "outcome_",
    "nominal",
)


class TestR1IvsAdministrativo(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.r1 = json.loads(R1.read_text(encoding="utf-8"))
        cls.matriz = pd.read_csv(MATRIZ, dtype={"co_ibge_6d": str})

    def test_regra_reproduz_todas_as_ondas_sem_excecao(self) -> None:
        rep = self.r1["reproducao_da_faixa_anunciada"]
        self.assertEqual(self.r1["decisao_r1"], "APROVADO_SHARP")
        self.assertEqual(rep["acertos"], rep["total_municipio_onda_versao"])
        for onda, bloco in rep["por_onda_versao"].items():
            with self.subTest(onda=onda):
                self.assertEqual(bloco["reproduzidos_regra_edital_28_2026"], bloco["municipios"])
                self.assertEqual(bloco["com_mais_de_uma_faixa"], 0)
        self.assertGreaterEqual(len(rep["por_onda_versao"]), 8)

    def test_cortes_sao_os_do_atlas_aplicados_ao_ivs_administrativo(self) -> None:
        m = self.matriz
        esperado = m.ivs_adm.map(lambda v: "FAIXA 1" if v > 0.400 else "FAIXA 2" if v > 0.300 else "FAIXA 3")
        self.assertTrue(esperado.eq(m.faixa_regra).all())
        self.assertTrue(m.categoria_publicada.eq(m.categoria_recalculada).all())
        self.assertEqual(self.r1["regra"]["cortes"], {"faixa3_para_faixa2": 0.3, "faixa2_para_faixa1": 0.4})

    def test_texto_do_faq_de_2025_nao_e_a_regra_aplicada(self) -> None:
        c1 = self.r1["reproducao_da_faixa_anunciada"]["por_onda_versao"]["2025_c1_ch1/original"]
        self.assertLess(c1["reproduzidos_texto_faq_2025"], c1["municipios"])

    def test_nenhum_municipio_muda_de_faixa_entre_ondas(self) -> None:
        pares = self.r1["faixa_entre_ondas"]["pares"]
        self.assertEqual(len(pares), 10)
        self.assertTrue(all(p["faixa_muda"] == 0 for p in pares.values()))

    def test_ivs_administrativo_nao_e_o_ivs_2010(self) -> None:
        comp = self.r1["comparacao_ivs_2010_atlas"]
        self.assertLess(comp["valor_identico"], 0.05 * comp["municipios"])
        self.assertLess(comp["mesma_categoria"], 0.7 * comp["municipios"])

    def test_rotulo_da_serie_coincide_com_a_categoria(self) -> None:
        rot = self.r1["rotulo_da_serie_historica"]
        self.assertEqual(rot["municipios_com_rotulo"], rot["rotulo_igual_categoria_administrativa"])

    def test_matriz_cobre_o_pais_e_todos_os_ofertados(self) -> None:
        self.assertEqual(self.matriz.co_ibge_6d.nunique(), len(self.matriz))
        self.assertGreater(len(self.matriz), 5500)
        self.assertFalse(self.matriz.ivs_adm.isna().any())
        self.assertEqual(int(self.matriz.ofertado_alguma_onda.sum()), 1144)

    def test_fonte_preservada_com_hash_do_manifesto(self) -> None:
        manifesto = json.loads(MANIFESTO.read_text(encoding="utf-8"))
        quadro = next(f for f in manifesto["fontes"] if f["id"] == "pmmb_2026_quadro_de_vagas")
        self.assertEqual(self.r1["fontes"]["ivs_administrativo"]["sha256"], quadro["sha256"])
        self.assertTrue((ROOT / quadro["arquivo_local"]).exists())


class TestR2SemOutcome(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.r2 = json.loads(R2.read_text(encoding="utf-8"))
        cls.testes = pd.read_csv(TESTES_R2)

    def test_scripts_declaram_e_cumprem_que_nao_abrem_outcome(self) -> None:
        for script in (SCRIPT_R1, SCRIPT_R2):
            with self.subTest(script=script.name):
                texto = script.read_text(encoding="utf-8")
                self.assertIn("nao abre nenhum outcome", texto)
                caminhos = " ".join(re.findall(r'ROOT / [^\n]+', texto)).lower()
                for marca in MARCAS_DE_OUTCOME:
                    self.assertNotIn(marca, caminhos)
        self.assertFalse(self.r2["outcomes_abertos"])

    def test_os_dois_cortes_sao_viaveis_e_os_placebos_nao_tem_salto(self) -> None:
        self.assertEqual(self.r2["decisao_r2"], "VIAVEL_CONTINUIDADE_COM_RESSALVAS")
        self.assertEqual(self.r2["cortes_viaveis"], ["0.300", "0.400"])
        for corte in ("0.200", "0.500"):
            self.assertEqual(self.r2["cortes"][corte]["salto_da_bolsa_anunciada"], 0)

    def test_a_regra_estrita_que_reprovou_fica_registrada(self) -> None:
        for corte in ("0.300", "0.400"):
            bloco = self.r2["cortes"][corte]
            with self.subTest(corte=corte):
                self.assertIsNone(bloco["randomizacao_local"]["janela_regra_estrita"])
                self.assertFalse(bloco["criterios"]["randomizacao_local_viavel"])
        self.assertTrue(any("regra estrita" in limite for limite in self.r2["limites"]))

    def test_criterios_essenciais_passam_nos_cortes_de_tratamento(self) -> None:
        for corte in ("0.300", "0.400"):
            criterios = self.r2["cortes"][corte]["criterios"]
            with self.subTest(corte=corte):
                for chave in self.r2["regras_pre_especificadas"]["criterios_essenciais"]:
                    self.assertTrue(criterios[chave], chave)

    def test_potencia_limitada_e_declarada(self) -> None:
        mde = self.r2["mde_conjunto_dois_cortes_pp"]
        self.assertGreater(mde["0.050"]["0.3"], 15)
        for corte in ("0.300", "0.400"):
            por_banda = self.r2["cortes"][corte]["local_linear"]["mde_proporcao_municipal_pp"]
            self.assertGreater(por_banda["0.030"]["0.3"], por_banda["0.100"]["0.3"])

    def test_testes_cobrem_os_dois_metodos_e_os_quatro_cortes(self) -> None:
        self.assertEqual(set(self.testes.metodo), {"randomizacao_local", "local_linear"})
        self.assertEqual(sorted(self.testes.corte.unique()), [0.2, 0.3, 0.4, 0.5])
        self.assertEqual(
            set(self.testes.grupo), {"selecao", "balanco", "composicao", "cointervencao"}
        )

    def test_nao_ha_protocolo_r3_sem_autorizacao(self) -> None:
        self.assertFalse(PROTOCOLO_R3.exists())


if __name__ == "__main__":
    unittest.main()
