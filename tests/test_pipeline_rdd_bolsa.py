"""A cadeia da RDD da bolsa no `run_all.py`: ordem, argumentos e scripts retirados.

Lê `run_all.py` como módulo, sem executar nenhuma etapa.
"""

from __future__ import annotations

import ast
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("run_all_rdd_bolsa", ROOT / "run_all.py")
RA = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RA)

AQ = ROOT / "scripts" / "aquisicao"
RDD = ROOT / "scripts" / "rdd_bolsa"
TT = ROOT / "scripts" / "tema_trabalho"

CADEIA = [
    AQ / "a07_adquirir_ivs_administrativo.py",
    AQ / "a08_adquirir_ivs_2010_oficial.py",
    RDD / "04_portao_r1_escore_administrativo.py",
    RDD / "04b_validar_ivs_oficial_escore_administrativo.py",
    RDD / "04c_identificar_recorte_arquivo_local.py",
    RDD / "05_estimar_E1_densidade.py",
    RDD / "06_estimar_E2_limites.py",
    RDD / "07_estimar_E3_rdd_completa.py",
    RDD / "08a_reconstruir_proporcao_preenchida.py",
    RDD / "08_estimar_E4_proporcao.py",
    RDD / "11_inferencia_alternativa.py",
    RDD / "09b_conferir_sinal.py",  # o 09 exige a conferência em dia com o E3
    RDD / "09_gerar_relatorio_pdf.py",
    RDD / "10_galeria_figura_regra.py",
]
# Leem data/ivs_ipea_2010_municipios.csv como IVS 2010 ou dependem disso (auditoria 16).
RETIRADOS = [
    RDD / "01_auditar_regra_e_suporte.py",
    RDD / "01_auditar_primeiro_estagio_publico.py",
    RDD / "01b_reconstruir_regra_faixa.py",
    RDD / "02_controlar_execucao_plano_causal.py",
    RDD / "03_triagem_resposta_administrativa.py",
]
ESCORE_COMPLETO = "output/rdd_bolsa/escore_completo_ivs2010_oficial.csv"


def posicao(p: Path) -> int:
    return RA.STEPS.index(p)


class TestDocumentosVigentesApontamACorrecao(unittest.TestCase):
    """Documento vigente que fala da RDD da bolsa tem de apontar para a auditoria 16.

    Até 14/10/2026 esses documentos davam a RDD por bloqueada ("177/368",
    "não usar 0,300"), com base no arquivo de IVS errado. Uma afirmação antiga
    sem a correção ao lado orientaria um agente a desfazer o trabalho.
    """

    VIGENTES = [
        "CLAUDE.md",
        "README.md",
        "TODO.md",
        "prompts/avaliacao_rdd_bolsa/README.md",
        "docs/06_execucao/05_roadmap_execucao.md",
        "docs/01_pergunta_escopo/13_dossie_executivo_avaliacao_impacto_pmme.md",
        "docs/01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md",
        "docs/03_literatura_empirica/20_evidencia_empirica_hipotese_remuneracao_preenchimento.md",
        "docs/05_identificacao/14_plano_implementacao_rdd_bolsa.md",
        "docs/05_identificacao/16_sintese_achados_e_novo_plano_causal.md",
        "docs/05_identificacao/17_plano_causal_publico_cutoff_escore.md",
        "docs/auditorias/07_portao_rdd_bolsa.md",
    ]

    def test_cada_documento_aponta_a_auditoria_16(self) -> None:
        for rel in self.VIGENTES:
            texto = (ROOT / rel).read_text(encoding="utf-8")
            self.assertIn("16_ivs_2010_oficial_e_arquivo_local", texto, rel)

    def test_regras_revogadas_nao_voltam(self) -> None:
        claude = " ".join((ROOT / "CLAUDE.md").read_text(encoding="utf-8").split())
        self.assertNotIn("única execução imediata autorizada é R1", claude)
        self.assertNotIn("A fila imediata é o portão de viabilidade", claude)
        fila = (ROOT / "prompts/avaliacao_rdd_bolsa/README.md").read_text(encoding="utf-8")
        self.assertIn("~~não usar `0,300` como cutoff da grade de 2025~~", fila)


class TestCadeiaRddBolsa(unittest.TestCase):
    def test_cadeia_na_ordem_de_dependencia(self) -> None:
        posicoes = [posicao(p) for p in CADEIA]
        self.assertEqual(posicoes, sorted(posicoes))
        # 07, 08a e 08 leem o funil (A1); 07 lê a tipologia (A2); 08a lê o quadro de tratamento.
        for etapa in ("07_estimar_E3_rdd_completa.py", "08a_reconstruir_proporcao_preenchida.py",
                      "08_estimar_E4_proporcao.py"):
            self.assertLess(posicao(TT / "02_reconciliar_funil_ciclo1.py"), posicao(RDD / etapa))
        self.assertLess(posicao(TT / "03_construir_tipologia_territorial.py"), posicao(RDD / "07_estimar_E3_rdd_completa.py"))
        self.assertLess(posicao(AQ / "02_consolidar_quadro_vagas.py"),
                        posicao(RDD / "08a_reconstruir_proporcao_preenchida.py"))

    def test_sintese_a6_depois_da_cadeia_da_rdd(self) -> None:
        # A6 lê R1 (04b), E3 e E5 e registra os hashes deles no manifesto.
        a6 = posicao(TT / "07_red_team_sintese.py")
        for etapa in ("04b_validar_ivs_oficial_escore_administrativo.py", "07_estimar_E3_rdd_completa.py",
                      "11_inferencia_alternativa.py"):
            self.assertLess(posicao(RDD / etapa), a6, etapa)

    def test_e3_roda_com_o_escore_completo(self) -> None:
        self.assertEqual(RA.ARGUMENTOS, {RDD / "07_estimar_E3_rdd_completa.py": ["--escore", ESCORE_COMPLETO]})
        self.assertTrue((ROOT / ESCORE_COMPLETO).exists())
        # O 04b, que grava o escore completo, vem antes do E3.
        self.assertLess(posicao(RDD / "04b_validar_ivs_oficial_escore_administrativo.py"),
                        posicao(RDD / "07_estimar_E3_rdd_completa.py"))

    def test_scripts_antigos_fora_do_pipeline_mas_preservados(self) -> None:
        for p in RETIRADOS:
            self.assertNotIn(p, RA.STEPS, p.name)
            self.assertTrue(p.exists(), f"{p.name} foi apagado")

    def test_opcao_rdd_bolsa_seleciona_so_a_cadeia(self) -> None:
        self.assertEqual(RA.etapas(somente_rdd_bolsa=True), CADEIA)
        self.assertEqual(RA.etapas(), RA.STEPS)

    def test_passos_e_argumentos_existem(self) -> None:
        for p in RA.STEPS:
            self.assertTrue(p.exists(), p)
        self.assertEqual(len(RA.STEPS), len(set(RA.STEPS)))
        self.assertTrue(set(RA.ARGUMENTOS) <= set(RA.STEPS))

    def test_steps_continua_legivel_por_ast(self) -> None:
        """O manifesto A6 lê STEPS por AST e só aceita `ROOT / "..."` literal (07_red_team_sintese.py)."""
        arvore = ast.parse((ROOT / "run_all.py").read_text(encoding="utf-8"))
        no = next(n for n in arvore.body if isinstance(n, ast.Assign)
                  and any(isinstance(a, ast.Name) and a.id == "STEPS" for a in n.targets))
        self.assertIsInstance(no.value, ast.List)
        caminhos = []
        for elemento in no.value.elts:
            partes, atual = [], elemento
            while isinstance(atual, ast.BinOp) and isinstance(atual.op, ast.Div):
                self.assertIsInstance(atual.right, ast.Constant)
                partes.append(atual.right.value)
                atual = atual.left
            self.assertIsInstance(atual, ast.Name)
            self.assertEqual(atual.id, "ROOT")
            caminhos.append(ROOT.joinpath(*reversed(partes)))
        self.assertEqual(caminhos, RA.STEPS)


if __name__ == "__main__":
    unittest.main()
