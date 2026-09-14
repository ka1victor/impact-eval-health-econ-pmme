"""Portoes do diagnostico R1 de reconstrucao da regra da faixa da bolsa.

O artefato so serve se continuar dizendo, sem ambiguidade, que o IVS publico
nao determina a faixa anunciada. Um dia em que ele passe a dizer o contrario e
um dia em que alguem trocou o insumo sem trocar a conclusao do portao.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTEFATO = ROOT / "output" / "rdd_bolsa" / "a01b_reconstrucao_regra_faixa.json"
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "01b_reconstruir_regra_faixa.py"


class TestReconstrucaoRegraFaixa(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.d = json.loads(ARTEFATO.read_text(encoding="utf-8"))

    def test_o_diagnostico_nao_autoriza_estimacao(self) -> None:
        self.assertEqual(self.d["status"], "DIAGNOSTICO_NAO_AUTORIZATIVO")
        self.assertFalse(self.d["outcomes_abertos"])
        self.assertEqual(self.d["conclusoes"]["r1_continua"], "REPROVADO_PENDENTE_DE_RECONSTRUCAO")

    def test_as_faixas_se_sobrepoem_no_ivs(self) -> None:
        f = self.d["faixa_por_ivs"]
        self.assertGreater(f["FAIXA 3"]["ivs_max"], f["FAIXA 2"]["ivs_min"])
        self.assertGreater(f["FAIXA 2"]["ivs_max"], f["FAIXA 1"]["ivs_min"])

    def test_existe_inversao_logo_nenhum_limiar_reproduz(self) -> None:
        """Uma inversao basta; o teste guarda o fato, nao o numero."""
        self.assertGreater(self.d["monotonicidade"]["inversoes"], 0)
        self.assertFalse(self.d["conclusoes"]["ivs_publico_e_criterio_unico"])
        self.assertFalse(self.d["conclusoes"]["regra_reconstruida"])

    def test_a_melhor_regra_possivel_ainda_erra(self) -> None:
        melhor = self.d["regra_de_limiar"]["melhor_possivel"]
        self.assertLess(melhor["acertos"], melhor["n"])
        atlas = self.d["regra_de_limiar"]["taxonomia_atlas"]
        self.assertGreater(melhor["acertos"], atlas["acertos"])

    def test_o_corte_de_0_500_nao_separa_faixas(self) -> None:
        janela = self.d["corte_de_0_500_nao_tem_acao"]
        self.assertEqual(janela["faixas_presentes_na_janela"], ["FAIXA 1"])
        self.assertLess(janela["ivs_max_da_faixa2"], 0.450)

    def test_o_script_declara_que_nao_abre_outcomes(self) -> None:
        self.assertIn("nao abre nenhum outcome", SCRIPT.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()


class TestQuemEscapaDaRegra(unittest.TestCase):
    """O desvio da melhor regra tem de continuar sendo sistematico, nao ruido.

    Se um dia os tres grupos ficarem parecidos, o argumento contra o pareamento
    cai junto, e a fila precisa saber disso.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.perfil = json.loads(ARTEFATO.read_text(encoding="utf-8"))["quem_escapa_da_regra"]["perfil"]

    def test_quem_recebe_mais_e_menor_e_mais_pobre(self) -> None:
        acima = self.perfil["acima_do_previsto"]["medianas"]
        abaixo = self.perfil["abaixo_do_previsto"]["medianas"]
        self.assertLess(acima["populacao_2010"], abaixo["populacao_2010"])
        self.assertLess(acima["rdpc_2010"], abaixo["rdpc_2010"])

    def test_quem_recebe_mais_e_mais_remoto(self) -> None:
        def prop_remoto(grupo: str) -> float:
            estratos = self.perfil[grupo]["estratos"]
            return estratos.get("interior_remoto", 0) / self.perfil[grupo]["n"]

        self.assertGreater(prop_remoto("acima_do_previsto"), prop_remoto("abaixo_do_previsto"))
        self.assertGreater(prop_remoto("acima_do_previsto"), prop_remoto("no_previsto"))
