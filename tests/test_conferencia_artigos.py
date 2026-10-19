"""Conferência de números dos dois artigos: nenhuma cifra sem origem em `output/`."""

from __future__ import annotations

import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "tema_trabalho"


class ConferenciaArtigosTest(unittest.TestCase):
    def _quadro(self, nome: str) -> pd.DataFrame:
        caminho = OUT / nome
        self.assertTrue(caminho.exists(), nome)
        return pd.read_csv(caminho)

    def test_artigo_principal_toda_cifra_aprovada(self) -> None:
        q = self._quadro("A8_conferencia_numeros_artigo.csv")
        self.assertGreaterEqual(len(q), 193, "o conferidor do artigo principal perdeu cifras")
        self.assertTrue(q["status"].eq("OK").all(), q[q["status"].ne("OK")]["id"].tolist())
        self.assertEqual(q["id"].nunique(), len(q))
        # As evidências novas de A5 (B-5 e C-7) entraram no apêndice B e são conferidas.
        for prefixo in ["A5_TXT_Q_PROP", "A5_TXT_Q_NIVEL", "A5_TXT_C7_PLACEBO_NIVEL", "A5_TXT_C7_DESLOC_REGIONAL"]:
            self.assertIn(prefixo, set(q["id"]), prefixo)
        # A RDD da bolsa no IVS 2010 oficial (R1 e E3) substituiu o descarte da
        # regra (191/177 de 368), que vinha do arquivo de IVS errado (auditoria
        # 16); o ajuste completo de A4, estimado com o mesmo arquivo, saiu.
        for identificador in ["RDD_R1_REGRA_P1", "RDD_TAB_P1_PREENCH_C0300_tau"]:
            self.assertIn(identificador, set(q["id"]), identificador)
        for antigo in ["RDD_TXT_REPRODUZIDOS", "RDD_TXT_DIVERGENTES", "A4_TAB_FULL_dif", "A4_TXT_FULL_COEF"]:
            self.assertNotIn(antigo, set(q["id"]), antigo)
        # Rodada multi-outcome (E6-E9, síntese E8): primárias com Holm, tabela C2,
        # estudo de evento do E7 e tabela C3 do E9 lidos de output/rdd_bolsa.
        mo = q[q["id"].str.startswith("MO_")]
        for identificador in ["MO_HOLM_TXT_P1_p_holm", "MO_HOLM_TXT_P2_p_holm", "MO_TAB_F1_3_V1V2V3_tau",
                              "MO_TAB_F3_1_U_aj", "MO_E7_NIVEL_NIVEL_PRE_EXTRA_TAU", "MO_TAB_E9_RC_C2_RC_5MIL",
                              "MO_DESCARTE_EMPILHADO_HI"]:
            self.assertIn(identificador, set(mo["id"]), identificador)
        self.assertTrue(mo["fonte_arquivo"].str.startswith("output/").all())

    def test_varredura_de_orfaos_cobre_os_apendices(self) -> None:
        """Sintético: no principal os apêndices vêm depois da bibliografia; a varredura
        tem de vê-los e tirar só o bloco thebibliography."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "conferidor_principal_teste", ROOT / "scripts" / "tema_trabalho" / "10_conferir_numeros_artigo.py")
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)
        tex = ("\\begin{document} corpo 1,5 \\begin{thebibliography}{9} 105(7), 2,25 \\end{thebibliography}"
               " \\appendix apendice 7,25 \\end{document}")
        decimais, sem_origem = modulo.decimais_sem_origem(tex, [{"status": "OK", "trecho_esperado_no_tex": "corpo 1,5"}])
        self.assertEqual(decimais, ["1,5", "7,25"])
        self.assertEqual(sem_origem, ["7,25"])

    def test_artigo_curto_toda_cifra_aprovada_e_coberta(self) -> None:
        q = self._quadro("A8_conferencia_numeros_artigo_curto.csv")
        self.assertTrue(q["status"].eq("OK").all(), q[q["status"].ne("OK")]["id"].tolist())
        self.assertEqual(q["id"].nunique(), len(q))
        self.assertEqual(set(q["origem_registro"]), {"artigo_curto", "conferidor_principal"})
        proprios = q[q["origem_registro"] == "artigo_curto"]
        self.assertGreaterEqual(len(proprios), 70)
        # Tabelas do artigo curto que só ele publica.
        for prefixo in ["CURTO_VAL_REP2026_n", "CURTO_A8_CH2_EXATO_LO", "CURTO_A4_WILD_capital", "CURTO_A5_Q_PROP", "CURTO_C7_REGIONAL_beta"]:
            self.assertIn(prefixo, set(q["id"]), prefixo)

    def test_os_dois_artigos_citam_o_mesmo_nucleo(self) -> None:
        # O artigo curto reutiliza a formulação do principal para o núcleo A8;
        # se um deles mudar um número, o outro deixa de o reutilizar e este
        # teste denuncia a divergência.
        q = self._quadro("A8_conferencia_numeros_artigo_curto.csv")
        reusados = set(q.loc[q["origem_registro"] == "conferidor_principal", "id"].str.replace("REUSO_", "", regex=False))
        # O núcleo da RDD é a regra reproduzida com o IVS 2010 oficial (R1) e o
        # salto do E3 na tabela da bolsa; o antigo "RDD_TXT_reproduzidos" citava
        # o descarte que vinha do arquivo de IVS errado (auditoria 16).
        for nucleo in ["A8_PRINCIPAL_HOMOLOG_LOCAL_dif", "A8_PRINCIPAL_ATIVO_LOCAL_dif", "A4_TAB_LPM_dif", "A5_TXT_PROP", "RDD_R1_REGRA_P1", "RDD_TAB_P1_PREENCH_C0300_tau", "DDD_TXT_dif"]:
            candidatos = [r for r in reusados if r.startswith(nucleo.rsplit("_", 1)[0])]
            self.assertTrue(candidatos, f"núcleo não reutilizado pelo artigo curto: {nucleo}")


if __name__ == "__main__":
    unittest.main()
