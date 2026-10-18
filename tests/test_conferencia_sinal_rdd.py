"""Teste da conferencia do sinal do salto da RDD da bolsa com DADOS SINTETICOS.

Todos os escores, bolsas e outcomes deste modulo sao SINTETICOS: gerados em
memoria, com semente fixa e saltos conhecidos por construcao. Nada aqui e
observacao empirica e nada e gravado em disco.

Verifica, para `scripts/rdd_bolsa/09b_conferir_sinal.py` e o estimador do E3
(`07_estimar_E3_rdd_completa.py`):
(1) com a bolsa R$ 5 mil maior acima do corte e efeito positivo por construcao,
    o salto do E3, o das duas retas separadas e o do modelo com a bolsa no lugar
    de T sao positivos e iguais ao efeito;
(2) o estimador independente reproduz o salto e o EP HC1 do E3;
(3) a decomposicao "diferenca bruta = salto + inclinacao + residuo" fecha;
(4) com inclinacao forte e salto negativo, a diferenca de medias brutas sai
    positiva: o caso que motivou a conferencia nao indica sinal invertido.
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def _importar(nome: str, arquivo: str):
    spec = importlib.util.spec_from_file_location(nome, ROOT / "scripts" / "rdd_bolsa" / arquivo)
    mod = importlib.util.module_from_spec(spec)
    antes = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.dont_write_bytecode = antes
    return mod


E3 = _importar("e3_rdd_completa", "07_estimar_E3_rdd_completa.py")
CS = _importar("conferir_sinal_09b", "09b_conferir_sinal.py")

SEMENTE = 20261018
CORTE_MIL = 300
H_MIL = 50
BOLSA_MENOR, BOLSA_MAIOR = 10_000.0, 15_000.0


def dados_sinteticos(rng: np.random.Generator, salto: float, inclinacao: float, ruido: float, n: int = 800):
    """SINTETICO: escore em milesimos, bolsa pela regra (corte no lado de baixo) e outcome com salto conhecido."""
    s = rng.integers(200, 401, size=n)
    t = (s > CORTE_MIL).astype(float)
    bolsa = np.where(t == 1, BOLSA_MAIOR, BOLSA_MENOR)
    x = (s - CORTE_MIL) / 1000.0
    y = 0.30 + inclinacao * x + salto * t + (rng.normal(0.0, ruido, size=n) if ruido else 0.0)
    return s, y, bolsa


class TestSinalDoSaltoSintetico(unittest.TestCase):
    def test_salto_positivo_conhecido_sem_ruido(self):
        s, y, bolsa = dados_sinteticos(np.random.default_rng(SEMENTE), salto=0.10, inclinacao=1.0, ruido=0.0)
        e3 = E3.rdd_local_linear(s, y, CORTE_MIL, H_MIL)
        ind = CS.estimar_independente(s, y, bolsa, CORTE_MIL, H_MIL, passo_brl=BOLSA_MAIOR - BOLSA_MENOR)
        self.assertAlmostEqual(e3["tau"], 0.10, places=10)
        self.assertAlmostEqual(ind["tau_duas_retas"], 0.10, places=10)
        self.assertAlmostEqual(ind["tau_bolsa_do_quadro"], 0.10, places=10)
        self.assertEqual(ind["bolsa_lado_menor"], [BOLSA_MENOR])
        self.assertEqual(ind["bolsa_lado_maior"], [BOLSA_MAIOR])

    def test_independente_reproduz_salto_e_ep_do_e3(self):
        s, y, bolsa = dados_sinteticos(np.random.default_rng(SEMENTE + 1), salto=-0.07, inclinacao=2.0, ruido=0.2)
        e3 = E3.rdd_local_linear(s, y, CORTE_MIL, H_MIL)
        ind = CS.estimar_independente(s, y, bolsa, CORTE_MIL, H_MIL, passo_brl=BOLSA_MAIOR - BOLSA_MENOR)
        self.assertAlmostEqual(ind["tau_duas_retas"], e3["tau"], places=10)
        self.assertAlmostEqual(ind["tau_bolsa_do_quadro"], e3["tau"], places=10)
        self.assertAlmostEqual(ind["ep_hc1"], e3["ep"], places=10)
        self.assertEqual(ind["lado_bolsa_menor"]["n"], e3["n_abaixo"])
        self.assertEqual(ind["lado_bolsa_maior"]["n"], e3["n_acima"])
        self.assertAlmostEqual(ind["lado_bolsa_menor"]["media_bruta"], e3["media_bruta_abaixo"], places=12)
        self.assertAlmostEqual(ind["lado_bolsa_maior"]["media_bruta"], e3["media_bruta_acima"], places=12)

    def test_decomposicao_fecha(self):
        s, y, bolsa = dados_sinteticos(np.random.default_rng(SEMENTE + 2), salto=0.05, inclinacao=-3.0, ruido=0.2)
        ind = CS.estimar_independente(s, y, bolsa, CORTE_MIL, H_MIL, passo_brl=BOLSA_MAIOR - BOLSA_MENOR)
        dec = ind["decomposicao"]
        self.assertAlmostEqual(dec["salto"] + dec["inclinacao_dentro_da_janela"] + dec["residuo"],
                               ind["diferenca_medias_brutas"], places=12)
        self.assertAlmostEqual(dec["salto"], ind["tau_duas_retas"], places=12)
        self.assertAlmostEqual(ind["lado_bolsa_maior"]["valor_da_reta_no_corte"]
                               - ind["lado_bolsa_menor"]["valor_da_reta_no_corte"], ind["tau_duas_retas"], places=12)

    def test_inclinacao_forte_faz_media_bruta_subir_com_salto_negativo(self):
        s, y, bolsa = dados_sinteticos(np.random.default_rng(SEMENTE + 3), salto=-0.10, inclinacao=6.0, ruido=0.02)
        e3 = E3.rdd_local_linear(s, y, CORTE_MIL, H_MIL)
        ind = CS.estimar_independente(s, y, bolsa, CORTE_MIL, H_MIL, passo_brl=BOLSA_MAIOR - BOLSA_MENOR)
        self.assertLess(e3["tau"], 0.0)
        self.assertAlmostEqual(e3["tau"], -0.10, delta=0.02)
        self.assertGreater(e3["media_bruta_acima"] - e3["media_bruta_abaixo"], 0.0)
        self.assertGreater(ind["decomposicao"]["inclinacao_dentro_da_janela"], 0.0)


if __name__ == "__main__":
    unittest.main()
