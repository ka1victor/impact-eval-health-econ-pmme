"""A cadeia da RDD da bolsa no `run_all.py`: ordem, argumentos e scripts retirados.

Lê `run_all.py` como módulo, sem executar nenhuma etapa do pipeline. Só a conferência
sem rede do a09 (`--etapa verificar`) e a leitura do cache do a10 e do a11 são
exercitadas, com a rede bloqueada, para provar que o pipeline não baixa nada por padrão.
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
    # Rodada multi-outcome (protocolo 40, §11).
    AQ / "a10_normas_mesmos_cortes_ivs.py",
    AQ / "a11_adquirir_resultado_ciclo2_chamada1.py",
    AQ / "a09_adquirir_cnes_nacional.py",
    # Protocolo 47: SIA do TabNet, só conferido (`--etapa verificar`), como o a09.
    AQ / "a12_adquirir_sia_tabnet.py",
    AQ / "a14_adquirir_tiss_ans.py",  # protocolo 47: TISS/ANS, só verificar
    RDD / "12_construir_outcomes_funil.py",
    RDD / "13_estimar_E6_funil.py",
    RDD / "23_estimar_contagem_vagas.py",  # família N (protocolo 48): lê os outcomes e o E6
    RDD / "16_estimar_E9_escolha.py",
    RDD / "24_abertura_vagas_selecao.py",  # adendo §7 do protocolo 48: lê 12, a09, 23 e o E9 (16)
    RDD / "14_estimar_E7_dird_cnes.py",
    RDD / "21_producao_dird.py",  # família K, D1 (protocolo 47): lê a12, a13, a14, a09 e funções do 14 e do 23
    RDD / "22_chegada_pmme_evento.py",  # família K, D2: lê as séries do 21
    RDD / "15_sintese_E8.py",
    RDD / "09b_conferir_sinal.py",  # o 09 exige a conferência em dia com o E3
    RDD / "09_gerar_relatorio_pdf.py",  # lê E1 a E9 e a síntese E8
    RDD / "10_galeria_figura_regra.py",
]
A09 = AQ / "a09_adquirir_cnes_nacional.py"
A14 = AQ / "a14_adquirir_tiss_ans.py"
A15 = AQ / "a15_adquirir_sih_residencia.py"  # portão G3 (plano 51): SIH por residência, só verificar
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

    def test_dependencias_da_rodada_multioutcome(self) -> None:
        antes = {
            # a10 lê a categoria do a07 e o IVS oficial do a08.
            AQ / "a10_normas_mesmos_cortes_ivs.py": [AQ / "a07_adquirir_ivs_administrativo.py",
                                                    AQ / "a08_adquirir_ivs_2010_oficial.py"],
            # a09 lê o universo do a08, a ponte e o painel do ciclo 1 (para conferir hashes).
            A09: [AQ / "a08_adquirir_ivs_2010_oficial.py", AQ / "01_congelar_ponte_cbo.py",
                  ROOT / "scripts" / "avaliacao_impacto" / "run_pipeline_avaliacao.py"],
            # a12 lê a ponte (CBO-alvo) e importa a regra de grupos de CBO do a09; não lê IVS.
            AQ / "a12_adquirir_sia_tabnet.py": [AQ / "01_congelar_ponte_cbo.py", A09],
            # 12 lê o E4 municipal (08), o manifesto do a11, o funil (A1), a tipologia (A2) e o Censo 2022.
            RDD / "12_construir_outcomes_funil.py": [
                RDD / "08_estimar_E4_proporcao.py", AQ / "a11_adquirir_resultado_ciclo2_chamada1.py",
                AQ / "a07_adquirir_ivs_administrativo.py", TT / "02_reconciliar_funil_ciclo1.py",
                TT / "03_construir_tipologia_territorial.py", AQ / "06_adquirir_populacao_censo2022.py"],
            # E6 lê os outcomes (12), E3, E4, a janela LR do E5 (11) e o IED/diagnóstico do a10.
            RDD / "13_estimar_E6_funil.py": [
                RDD / "12_construir_outcomes_funil.py", RDD / "07_estimar_E3_rdd_completa.py",
                RDD / "08_estimar_E4_proporcao.py", RDD / "11_inferencia_alternativa.py",
                AQ / "a10_normas_mesmos_cortes_ivs.py"],
            # Família N (protocolo 48) lê os outcomes (12), a janela LR e as estimativas do E6 (13).
            RDD / "23_estimar_contagem_vagas.py": [RDD / "12_construir_outcomes_funil.py",
                                                  RDD / "13_estimar_E6_funil.py",
                                                  AQ / "a08_adquirir_ivs_2010_oficial.py"],
            # Adendo §7 (24) lê os outcomes (12), o CNES (a09), o Censo (a06), N_estimativas (23) e o E9 (16).
            RDD / "24_abertura_vagas_selecao.py": [RDD / "12_construir_outcomes_funil.py", A09,
                                                  AQ / "06_adquirir_populacao_censo2022.py",
                                                  RDD / "23_estimar_contagem_vagas.py",
                                                  RDD / "16_estimar_E9_escolha.py",
                                                  AQ / "a08_adquirir_ivs_2010_oficial.py"],
            # E9 lê as tabelas de escolha do 12 e o manifesto do a11.
            RDD / "16_estimar_E9_escolha.py": [RDD / "12_construir_outcomes_funil.py",
                                              AQ / "a11_adquirir_resultado_ciclo2_chamada1.py"],
            # Família K (protocolo 47): D1 lê SIA, SIH, TISS e CNES, o a08, a lista de V1 (12), o IED (a10) e
            # importa funções do E7 (14) e das figuras da família N (23); D2 importa o D1.
            RDD / "21_producao_dird.py": [
                AQ / "a12_adquirir_sia_tabnet.py", AQ / "a13_adquirir_sih_tabnet.py", A14, A09,
                AQ / "a08_adquirir_ivs_2010_oficial.py", AQ / "a10_normas_mesmos_cortes_ivs.py",
                RDD / "12_construir_outcomes_funil.py", RDD / "14_estimar_E7_dird_cnes.py",
                RDD / "23_estimar_contagem_vagas.py"],
            RDD / "22_chegada_pmme_evento.py": [RDD / "21_producao_dird.py", RDD / "12_construir_outcomes_funil.py"],
            # a15 (SIH por residência) compara seus totais nacionais com as validações versionadas do a13.
            A15: [AQ / "a13_adquirir_sih_tabnet.py"],
            # E7 lê o painel do a09, o IED do a10, a janela LR do E5 e confere a de U com a do E6.
            RDD / "14_estimar_E7_dird_cnes.py": [
                A09, AQ / "a10_normas_mesmos_cortes_ivs.py", RDD / "11_inferencia_alternativa.py",
                RDD / "12_construir_outcomes_funil.py", RDD / "13_estimar_E6_funil.py"],
        }
        for etapa, deps in antes.items():
            for dep in deps:
                self.assertLess(posicao(dep), posicao(etapa), f"{dep.name} tem de vir antes de {etapa.name}")

    def test_relatorio_09_depois_da_rodada_multioutcome(self) -> None:
        # O 09 lê as saídas de E6, E7, E9, da síntese E8 e da auditoria 18 (a10).
        texto = (RDD / "09_gerar_relatorio_pdf.py").read_text(encoding="utf-8")
        produtores = {"E6_": "13_estimar_E6_funil.py", "E7_": "14_estimar_E7_dird_cnes.py",
                      "E9_": "16_estimar_E9_escolha.py", "E8_": "15_sintese_E8.py"}
        for saida, script in produtores.items():
            if saida in texto:
                self.assertLess(posicao(RDD / script), posicao(RDD / "09_gerar_relatorio_pdf.py"), script)
        if "a10_" in texto:
            self.assertLess(posicao(AQ / "a10_normas_mesmos_cortes_ivs.py"), posicao(RDD / "09_gerar_relatorio_pdf.py"))
        # A síntese lê E3, E5, E6, E7 e E9.
        for dep in ("07_estimar_E3_rdd_completa.py", "11_inferencia_alternativa.py", "13_estimar_E6_funil.py",
                    "14_estimar_E7_dird_cnes.py", "16_estimar_E9_escolha.py"):
            self.assertLess(posicao(RDD / dep), posicao(RDD / "15_sintese_E8.py"), dep)

    def test_cnes_nacional_nao_baixa_por_padrao(self) -> None:
        """O run_all não dispara os ~23 GB do CNES nacional: a09 só confere o painel versionado."""
        self.assertEqual(RA.ARGUMENTOS[A09], ["--etapa", "verificar"])
        arvore = ast.parse(A09.read_text(encoding="utf-8"))
        padrao = None
        for no in ast.walk(arvore):
            if isinstance(no, ast.Call) and getattr(no.func, "attr", None) == "add_argument" \
                    and no.args and isinstance(no.args[0], ast.Constant) and no.args[0].value == "--etapa":
                padrao = next(k.value.value for k in no.keywords if k.arg == "default")
        self.assertEqual(padrao, "verificar")

    def test_verificacao_do_a09_nao_usa_rede_nem_grava(self) -> None:
        import json
        import sys
        from unittest import mock

        spec = importlib.util.spec_from_file_location("a09_pipeline", A09)
        a09 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(a09)
        saidas = [a09.PAINEL_FILE, a09.MANIFESTO_FILE, a09.VALIDACAO_FILE, a09.ROTULOS_FILE, a09.RESUMO_FILE]
        antes = {p: p.stat().st_mtime_ns for p in saidas}

        def sem_rede(*_a, **_k):
            raise AssertionError("a09 em --etapa verificar tentou acessar a rede")

        with mock.patch("urllib.request.urlopen", sem_rede), \
                mock.patch.object(a09, "etapa_aquisicao", sem_rede), \
                mock.patch.object(a09, "gravar_painel", sem_rede), \
                mock.patch.object(sys, "argv", ["a09", "--etapa", "verificar"]):
            self.assertEqual(a09.main(), 0)
        self.assertEqual({p: p.stat().st_mtime_ns for p in saidas}, antes)
        self.assertEqual(json.loads(a09.MANIFESTO_FILE.read_text(encoding="utf-8"))["competencias_planejadas"],
                         a09.COMPETENCIAS)

    def test_a10_e_a11_rodam_do_cache_versionado(self) -> None:
        """Com o cache conferido no repositório, nenhuma das duas aquisições baixa nada."""
        from unittest import mock

        def sem_rede(*_a, **_k):
            raise AssertionError("aquisição tentou acessar a rede com o cache presente")

        mods = {}
        for nome in ("a10_normas_mesmos_cortes_ivs.py", "a11_adquirir_resultado_ciclo2_chamada1.py"):
            spec = importlib.util.spec_from_file_location(f"pipeline_{nome[:3]}", AQ / nome)
            mods[nome[:3]] = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mods[nome[:3]])
        with mock.patch("urllib.request.urlopen", sem_rede):
            for fonte in mods["a10"].FONTES:
                _, status = mods["a10"].obter(fonte)
                self.assertTrue(status.startswith("cache_conferido"), (fonte["id"], status))
            for item in mods["a11"].ARQUIVOS:
                status, _, _ = mods["a11"].obter(item)
                self.assertEqual(status, "ja_preservado", item["arquivo"])

    def test_registro_do_failure_mode_fica_fora_do_pipeline(self) -> None:
        # Lê versões antigas do histórico do Git; não roda num clone sem histórico.
        script = TT / "12_registrar_failure_mode_ivs.py"
        self.assertTrue(script.exists())
        self.assertNotIn(script, RA.STEPS)
        self.assertIn("12_registrar_failure_mode_ivs.py", (ROOT / "run_all.py").read_text(encoding="utf-8"))

    def test_e3_roda_com_o_escore_completo(self) -> None:
        self.assertEqual(RA.ARGUMENTOS[RDD / "07_estimar_E3_rdd_completa.py"], ["--escore", ESCORE_COMPLETO])
        self.assertEqual(set(RA.ARGUMENTOS), {RDD / "07_estimar_E3_rdd_completa.py", A09,
                                              AQ / "a12_adquirir_sia_tabnet.py", AQ / "a13_adquirir_sih_tabnet.py", A14,
                                              A15})
        self.assertEqual(RA.ARGUMENTOS[AQ / "a12_adquirir_sia_tabnet.py"], ["--etapa", "verificar"])
        # a13 (SIH no TabNet, protocolo 47): como o a09, o run_all só confere sem rede.
        self.assertEqual(RA.ARGUMENTOS[AQ / "a13_adquirir_sih_tabnet.py"], ["--etapa", "verificar"])
        self.assertEqual(RA.ARGUMENTOS[A14], ["--etapa", "verificar"])
        # a15 (SIH por residência, portão G3): como o a13, o run_all só confere sem rede; fora do --rdd-bolsa.
        self.assertEqual(RA.ARGUMENTOS[A15], ["--etapa", "verificar"])
        self.assertNotIn(A15, RA.etapas(somente_rdd_bolsa=True))
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
