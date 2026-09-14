"""Invariantes do portão A1 de atração administrativa."""

from __future__ import annotations

import ast
import json
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "output" / "tema_trabalho" / "portao_denominador.json"
MATRIX = ROOT / "output" / "tema_trabalho" / "matriz_funil_ciclo1.parquet"


class ReconciliacaoFunilCiclo1Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.gate = json.loads(GATE.read_text(encoding="utf-8"))
        cls.matrix = pd.read_parquet(MATRIX)

    def test_gate_approves_cell_not_vacancy(self) -> None:
        self.assertEqual(self.gate["portao"], "APROVADO_CELULA")
        self.assertFalse(self.gate["decisao"]["denominador_por_vaga"])
        self.assertTrue(self.gate["decisao"]["denominador_por_celula"])
        self.assertIn(
            "taxa de preenchimento por vaga",
            self.gate["decisao"]["outcomes_bloqueados"],
        )

    def test_allocation_versions_are_not_summed(self) -> None:
        comparison = self.gate["chamada_1"]["versoes_alocacao"]["comparacao"]
        self.assertEqual(comparison["registros_versao_anterior"], 1671)
        self.assertEqual(comparison["registros_versao_canonica"], 1671)
        self.assertEqual(comparison["chaves_adicionadas"], 0)
        self.assertEqual(comparison["chaves_removidas"], 0)
        self.assertEqual(comparison["registros_com_conteudo_alterado"], 3)
        self.assertEqual(comparison["registros_com_marcacao_em_coluna_adicional"], 1)

    def test_first_call_funnel_and_capacity(self) -> None:
        call = self.gate["chamada_1"]
        self.assertEqual(call["quadro_original"]["celulas"], 1295)
        self.assertEqual(call["quadro_original"]["vagas_imediatas"], 678)
        self.assertEqual(call["quadro_original"]["vagas_reserva"], 1145)
        self.assertEqual(call["confirmacoes"], 468)
        self.assertEqual(call["propostas_realocacao"], 59)
        self.assertEqual(call["homologacoes"], 316)
        self.assertEqual(call["homologacoes_fora_do_quadro_original"], 20)
        self.assertEqual(call["celulas_homologacao_fora_do_quadro_original"], 18)
        self.assertEqual(call["celulas_confirmacao_acima_vagas_imediatas"], 10)
        self.assertEqual(call["celulas_confirmacao_acima_capacidade_total_publicada"], 15)
        self.assertEqual(call["confirmacoes_excedentes_capacidade_total_publicada"], 20)
        self.assertEqual(sum(call["trilha_homologacao"].values()), 316)

    def test_second_call_is_not_simple_cumulative_list(self) -> None:
        call = self.gate["chamada_2"]
        self.assertEqual(call["quadro_cadastro_reserva"]["celulas"], 1762)
        self.assertEqual(
            call["quadro_cadastro_reserva"]["vagas_reserva_publicadas"], 2896
        )
        self.assertFalse(
            call["quadro_cadastro_reserva"]["vagas_imediatas_numericas_publicadas"]
        )
        self.assertEqual(call["publicacao_preliminar"]["registros"], 98)
        self.assertEqual(call["publicacao_preliminar"]["classificados"], 33)
        self.assertEqual(call["classificacao_final"]["alocados"], 374)
        homolog = call["segunda_lista_homologados"]
        self.assertEqual(homolog["registros"], 581)
        self.assertEqual(homolog["reaparecem_da_primeira_lista"], 299)
        self.assertEqual(homolog["novos_na_segunda_lista"], 282)
        self.assertEqual(homolog["homologados_ch1_ausentes_na_segunda_lista"], 17)
        self.assertEqual(homolog["total_distinto_observado_nas_duas_listas"], 598)
        self.assertEqual(sum(homolog["trilha_novos"].values()), 581)

    def test_matrix_key_counts_and_privacy(self) -> None:
        key = ["ciclo", "chamada", "versao_quadro", "co_cnes_7d", "cod_curso"]
        self.assertEqual(len(self.matrix), 3323)
        self.assertEqual(self.matrix.duplicated(key).sum(), 0)
        self.assertEqual(self.matrix["registro_fora_do_quadro_publicado"].sum(), 266)
        lowered = [column.lower() for column in self.matrix.columns]
        self.assertFalse(any("cpf" in column for column in lowered))
        self.assertFalse(any("candidato" in column for column in lowered))
        self.assertFalse(any("person" in column for column in lowered))

    def test_event_totals_are_preserved(self) -> None:
        call1 = self.matrix[self.matrix["chamada"] == 1]
        call2 = self.matrix[self.matrix["chamada"] == 2]
        self.assertEqual(call1["n_confirmacoes_ch1"].sum(), 468)
        self.assertEqual(call1["n_homologacoes_ch1"].sum(), 316)
        self.assertEqual(call2["n_classificados_preliminares_ch2"].sum(), 33)
        self.assertEqual(call2["n_alocados_finais_ch2"].sum(), 374)
        self.assertEqual(call2["n_homologacoes_lista_ch2"].sum(), 581)
        self.assertEqual(call2["n_homologacoes_novas_ch2"].sum(), 282)


    def test_assinatura_cpf_nao_cruza_familias_de_mascara(self) -> None:
        """C-8: a assinatura de CPF só vale entre as duas listas de homologados.

        Cada publicação mascara posições diferentes do CPF, e a assinatura
        "3 primeiros + 4 últimos" é tirada dos dígitos visíveis. Verificado em
        14/09/2026 sobre os insumos: homologados Ch1 (`999XXX99999`) e Ch2
        (`999.XXX.X99-99`) deixam visíveis as posições 8-11 no fim, enquanto a
        classificação final Ch2 (`999.99X.XXX-99`) e a alocação Ch1
        (`99999XXXX99`) deixam as posições 4,5,10,11. As duas famílias produzem
        strings do mesmo formato e não são comparáveis.

        Hoje o uso é inerte — o único cruzamento é homologados contra
        homologados, com 299/299 e zero discordância. Este teste falha se
        alguém estender o uso a outro quadro, que é quando o pareamento passaria
        a sair errado em silêncio.
        """
        fonte = (
            ROOT / "scripts" / "tema_trabalho" / "02_reconciliar_funil_ciclo1.py"
        ).read_text(encoding="utf-8")
        arvore = ast.parse(fonte)

        quadros_autorizados = {
            "result",       # a própria criação da coluna, em person_events
            "homolog_c1",   # lado de referência do cruzamento autorizado
            "homolog_c2",   # lado comparado do cruzamento autorizado
        }

        quadros_usados = set()
        for no in ast.walk(arvore):
            if not isinstance(no, ast.Subscript):
                continue
            indice = no.slice
            if not (isinstance(indice, ast.Constant) and indice.value == "_cpf_signature_34"):
                continue
            alvo = no.value
            quadros_usados.add(alvo.id if isinstance(alvo, ast.Name) else ast.dump(alvo))

        self.assertTrue(
            quadros_usados <= quadros_autorizados,
            "assinatura de CPF usada fora do par de homologados, onde as máscaras "
            f"não são comparáveis: {sorted(quadros_usados - quadros_autorizados)}",
        )
        self.assertIn("homolog_c1", quadros_usados)
        self.assertIn("homolog_c2", quadros_usados)

        # A ressalva tem de continuar junto da função, não só no backlog.
        self.assertIn("Só comparável entre as duas listas de homologados", fonte)

    def test_assinatura_e_nome_nunca_sao_persistidos(self) -> None:
        """C-8: nenhum artefato pode carregar CPF, nome ou par reidentificável."""
        proibidas = {"_cpf_signature_34", "_person_name"}
        self.assertTrue(proibidas.isdisjoint(set(self.matrix.columns)))
        for coluna in self.matrix.columns:
            self.assertFalse(coluna.startswith("_"), f"coluna auxiliar persistida: {coluna}")


    def test_portao_marca_premissa_documental_como_nao_testada(self) -> None:
        """C-4: o portão publica duas constantes como se fossem critério testado.

        `vacancy_id_available` e `immediate_capacity_all_calls` são literais no
        código, então APROVADO_VAGA e REPROVADO são inatingíveis por construção.
        As premissas são factualmente corretas — nenhum dos oito insumos traz
        identificador de vaga física —, mas o JSON as publica em `criterios`,
        ao lado de verificações computadas, como se tivessem sido testadas.

        A separação em `criterios_testados` + `premissas_documentais` foi
        implementada e revertida: ela muda o SHA-256 de portao_denominador.json,
        que A3, A4 e A5 fixam como hash de entrada, e A5 não é regravável sem os
        microdados do CNES (D-4). Este teste fixa o estado atual e a ressalva no
        código, para que a pendência não se perca.
        """
        criterios = self.gate["criterios"]
        for chave in ("id_vaga_fisica_persistente_disponivel",
                      "capacidade_imediata_numerica_em_todas_as_chamadas"):
            self.assertIn(chave, criterios)
            self.assertFalse(criterios[chave], f"{chave} deixou de ser constante falsa")

        # Enquanto as duas forem falsas, o portão só pode sair APROVADO_CELULA
        # ou REPROVADO. Se alguém as derivar de checagem real, isto falha e
        # obriga a revisitar o item C-4.
        self.assertEqual(self.gate["portao"], "APROVADO_CELULA")

        fonte = (
            ROOT / "scripts" / "tema_trabalho" / "02_reconciliar_funil_ciclo1.py"
        ).read_text(encoding="utf-8")
        self.assertIn("Premissas documentais, não testes", fonte)
        self.assertIn("inatingível por construção", fonte)


if __name__ == "__main__":
    unittest.main()
