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
    AQ / "a16_cnes_profissional_mensal.py",  # portão G5 (doc 51): painel médico × mês, só verificar
    RDD / "12_construir_outcomes_funil.py",
    RDD / "13_estimar_E6_funil.py",
    RDD / "23_estimar_contagem_vagas.py",  # família N (protocolo 48): lê os outcomes e o E6
    RDD / "16_estimar_E9_escolha.py",
    RDD / "24_abertura_vagas_selecao.py",  # adendo §7 do protocolo 48: lê 12, a09, 23 e o E9 (16)
    RDD / "29_determinantes_abertura.py",  # P5 (protocolo 55): lê 12, a09, a12, a08 e funções do 24
    RDD / "25_escolha_dap.py",  # P1 (protocolo 52): lê 12, a08, G1 (versionado), E9 (16) e NA (24)
    RDD / "25c_magnitudes_P1h.py",  # P1h (protocolo 52b): importa o 25 e confere-se contra P1_estimativas
    RDD / "42_escolha_vaga_imediata_c2.py",  # adendo 52c: importa o 25c e o 12; portão contra E9_, P1_ e P1h_
    RDD / "48_sensibilidades_ciclo2_quadro_1302.py",  # adendo 52d: importa o 42; portão contra E9_, P1_ e P1h_
    RDD / "52_robustez_E9_ciclo2_quadro_1302.py",  # adendo 52f: importa o 48; portão contra E9_; confere VC_ e VD_
    RDD / "50_escolha_localizacao_par.py",  # adendo 52e: importa o 42; portão contra P1_, P1h_, VC_ e VD_
    RDD / "53_VL1_por_ciclo.py",  # adendo 52g: importa o 50; portão VG-R contra VL_
    RDD / "51_sintese_H2.py",  # síntese da H2: lê G1_, E9_, P1_, P1h_, VC_, VD_ e VL_; não reestima
    RDD / "32_realocacao_bolsa.py",  # realocação (protocolo 58): lê 12, a08, a06, a09 e funções do 16, 19 e 24
    RDD / "28_trajetoria_medicos.py",  # P4 (protocolo 54): lê o a16, a X1 (17, versionada), o a09 e a ponte
    RDD / "30_mecanismo_alocacao.py",  # P6 (protocolo 56), passo 0: só verificar; lê o G1 e o G2 versionados
    RDD / "31_rd_mecanismo.py",  # P6: estimação a partir das saídas versionadas do 30
    RDD / "14_estimar_E7_dird_cnes.py",
    RDD / "21_producao_dird.py",  # família K, D1 (protocolo 47): lê a12, a13, a14, a09 e funções do 14 e do 23
    RDD / "22_chegada_pmme_evento.py",  # família K, D2: lê as séries do 21
    RDD / "27_producao_extensoes.py",  # P3, adendo §12: importa o 21 e o 22; lê a12b, a13b, a15, a17 e K_D1/K_D2
    RDD / "35_comparacao_alternativa_P3P4.py",  # protocolo 59, parte B: só verificar (cache privado)
    RDD / "34_sensibilidade_honestdid.py",  # protocolo 59, parte A: só verificar (hashes e doc 57h)
    RDD / "36_equivalencia_H1.py",  # protocolo 60, parte A: TOST a partir de N_ (23) e NA_ (24)
    RDD / "38_diagnostico_queda_0300.py",  # protocolo 61: diagnóstico da queda em 0,300; reproduz N_, NA_ e ND_
    RDD / "39_gradiente_faixas.py",  # protocolo 62: gradiente dentro das faixas; importa carregar() do 38
    RDD / "40_h1_vagas_imediatas.py",  # adendo 48b: H1 só com vagas imediatas; reproduz N_, NA_ e ND_
    RDD / "41_h1_capitais_uf.py",  # adendo 48c: capitais e UF; portões contra HI_ (40), NA_ (24), N_ (23)
    RDD / "37_oferta_local_chegada.py",  # protocolo 60, parte B: importa o 22; lê K_D2, a09, a16 e a X1
    RDD / "43_oferta_local_corte.py",  # protocolo 64: importa o 37; reproduz o F3.1 do E7 e confere V com OL_
    RDD / "44_controles_localizacao_medicos.py",  # adendo 48d: portões contra HI_ (40) e OC_ (43)
    RDD / "45_pareamento_regra_literal.py",  # adendo 48e: importa o 44; portão contra o PS-1/PS-2 de CL_ (44)
    RDD / "46_selecao_tipo_vaga.py",  # adendo 48f: portões contra HI_ (40) e DQ_ (38); confere CL_ (44)
    RDD / "47_heterogeneidade_porte_ied.py",  # adendo 48g: portões contra HI_ (40) e OC_ (43); G lido do a10
    RDD / "49_pareamento_localizacao.py",  # adendo 48h: importa o 44 e o 45; portão contra o PM-1 de PM_ (45)
    RDD / "15_sintese_E8.py",
    RDD / "09b_conferir_sinal.py",  # o 09 exige a conferência em dia com o E3
    RDD / "09_gerar_relatorio_pdf.py",  # lê E1 a E9 e a síntese E8
    RDD / "10_galeria_figura_regra.py",
]
A09 = AQ / "a09_adquirir_cnes_nacional.py"
A14 = AQ / "a14_adquirir_tiss_ans.py"
A15 = AQ / "a15_adquirir_sih_residencia.py"  # portão G3 (plano 51): SIH por residência, só verificar
A16 = AQ / "a16_cnes_profissional_mensal.py"
P6_PASSO0 = RDD / "30_mecanismo_alocacao.py"  # P6 (protocolo 56): passo 0 só verificar no run_all
# Adendo §12 do protocolo 47: safras v2 do SIA (a12b) e do SIH (a13b) e SIA por forma × curso (a17), só verificar
A12B = AQ / "a12b_safra_v2_sia.py"
A13B = AQ / "a13b_safra_v2_sih.py"
A17 = AQ / "a17_adquirir_sia_forma_curso.py"
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
            # P5 (29) lê os outcomes e as leituras do cardápio e da adesão do 12, o CNES pré (a09), o SIA pré (a12),
            # o a08, o Censo 2022 (a06) e a tipologia (tema_trabalho/03), e importa funções do 24 (e do 23).
            RDD / "29_determinantes_abertura.py": [RDD / "12_construir_outcomes_funil.py", A09,
                                                  AQ / "a12_adquirir_sia_tabnet.py",
                                                  AQ / "a08_adquirir_ivs_2010_oficial.py",
                                                  AQ / "06_adquirir_populacao_censo2022.py",
                                                  TT / "03_construir_tipologia_territorial.py",
                                                  RDD / "24_abertura_vagas_selecao.py",
                                                  RDD / "23_estimar_contagem_vagas.py"],
            # P1 (25) lê as tabelas de escolha do 12, o a08, E9_estimativas (16) e NA_estimativas (24), e importa o 16.
            RDD / "25_escolha_dap.py": [RDD / "12_construir_outcomes_funil.py", RDD / "16_estimar_E9_escolha.py",
                                       RDD / "24_abertura_vagas_selecao.py", AQ / "a08_adquirir_ivs_2010_oficial.py"],
            # P1h (25c) importa o 25 e confere-se contra P1_estimativas.csv, que o 25 grava.
            RDD / "25c_magnitudes_P1h.py": [RDD / "25_escolha_dap.py"],
            # Adendo 52c (42) importa o 25c (e por ele o 25 e o 16) e o ler_quadro do 12; confere-se contra E9_ (16),
            # P1_ (25) e P1h_ (25c).
            RDD / "42_escolha_vaga_imediata_c2.py": [RDD / "25c_magnitudes_P1h.py", RDD / "25_escolha_dap.py",
                                                    RDD / "16_estimar_E9_escolha.py",
                                                    RDD / "12_construir_outcomes_funil.py"],
            # Adendo 52d (48) importa o 42 (e por ele o 25c, o 25, o 16 e o 12); confere-se contra E9_ (16), P1_ e
            # P1_dap (25), P1h_ (25c) e VC_ (42).
            RDD / "48_sensibilidades_ciclo2_quadro_1302.py": [RDD / "42_escolha_vaga_imediata_c2.py",
                                                             RDD / "25c_magnitudes_P1h.py", RDD / "25_escolha_dap.py",
                                                             RDD / "16_estimar_E9_escolha.py",
                                                             RDD / "12_construir_outcomes_funil.py"],
            # Adendo 52f (52) importa o 48 (e por ele o 42, o 25c, o 25, o 16 e o 12); portão contra E9_ (16); confere
            # VC_ (42) e VD_ (48).
            RDD / "52_robustez_E9_ciclo2_quadro_1302.py": [RDD / "48_sensibilidades_ciclo2_quadro_1302.py",
                                                          RDD / "42_escolha_vaga_imediata_c2.py",
                                                          RDD / "25c_magnitudes_P1h.py", RDD / "25_escolha_dap.py",
                                                          RDD / "16_estimar_E9_escolha.py",
                                                          RDD / "12_construir_outcomes_funil.py",
                                                          AQ / "a08_adquirir_ivs_2010_oficial.py"],
            # Adendo 52e (50) importa o 42 (e por ele o 25c, o 25, o 16 e o 12); portão contra P1_ (25), P1h_ (25c),
            # VC_ (42) e VD_ (48).
            RDD / "50_escolha_localizacao_par.py": [RDD / "42_escolha_vaga_imediata_c2.py",
                                                   RDD / "48_sensibilidades_ciclo2_quadro_1302.py",
                                                   RDD / "25c_magnitudes_P1h.py", RDD / "25_escolha_dap.py",
                                                   RDD / "16_estimar_E9_escolha.py",
                                                   RDD / "12_construir_outcomes_funil.py",
                                                   AQ / "a08_adquirir_ivs_2010_oficial.py"],
            # Adendo 52g (53) importa o 50 (e por ele o 42, o 25c, o 25, o 16 e o 12); portão VG-R contra VL_ (50).
            RDD / "53_VL1_por_ciclo.py": [RDD / "50_escolha_localizacao_par.py",
                                          RDD / "42_escolha_vaga_imediata_c2.py", RDD / "25c_magnitudes_P1h.py",
                                          RDD / "25_escolha_dap.py", RDD / "16_estimar_E9_escolha.py",
                                          RDD / "12_construir_outcomes_funil.py",
                                          AQ / "a08_adquirir_ivs_2010_oficial.py"],
            # Síntese da H2 (51) lê E9_ (16), P1_ (25), P1h_ (25c), VC_ (42), VD_ (48), VL_ (50), as tabelas de escolha do
            # 12 e o a08; o G1 é saída versionada fora do run_all.
            RDD / "51_sintese_H2.py": [RDD / "50_escolha_localizacao_par.py",
                                       RDD / "48_sensibilidades_ciclo2_quadro_1302.py",
                                       RDD / "42_escolha_vaga_imediata_c2.py", RDD / "25c_magnitudes_P1h.py",
                                       RDD / "25_escolha_dap.py", RDD / "16_estimar_E9_escolha.py",
                                       RDD / "12_construir_outcomes_funil.py",
                                       AQ / "a08_adquirir_ivs_2010_oficial.py"],
            # Realocação (32) lê as células do 12, o a08, o Censo (a06) e o CNES pré (a09) e importa o 16 e o 24.
            RDD / "32_realocacao_bolsa.py": [RDD / "12_construir_outcomes_funil.py", RDD / "16_estimar_E9_escolha.py",
                                            RDD / "24_abertura_vagas_selecao.py", AQ / "a08_adquirir_ivs_2010_oficial.py",
                                            AQ / "06_adquirir_populacao_censo2022.py", A09],
            # P4 (28) lê o painel médico × mês do a16, o painel do a09 e a ponte curso–CBO (01); importa a função das
            # listas do 17 (fora do run_all; X1_medicos.parquet é saída versionada).
            RDD / "28_trajetoria_medicos.py": [A16, A09, AQ / "01_congelar_ponte_cbo.py"],
            # P6: o 30 confere-se contra o a16 versionado e lê o G1 e o G2 (fora do run_all, versionados); o 31 lê
            # só as saídas do 30.
            RDD / "30_mecanismo_alocacao.py": [A16],
            RDD / "31_rd_mecanismo.py": [RDD / "30_mecanismo_alocacao.py"],
            # Protocolo 59: o 35 lê o 12.2 (27), a adesão (12) e as saídas do P6 (30); o 34 confere-se contra o 27, o
            # 28 e lê as saídas do 35.
            RDD / "35_comparacao_alternativa_P3P4.py": [RDD / "27_producao_extensoes.py",
                                                       RDD / "12_construir_outcomes_funil.py",
                                                       RDD / "30_mecanismo_alocacao.py"],
            RDD / "34_sensibilidade_honestdid.py": [RDD / "27_producao_extensoes.py", RDD / "28_trajetoria_medicos.py",
                                                   RDD / "35_comparacao_alternativa_P3P4.py"],
            # Protocolo 60, parte A: o 36 lê só N_estimativas (23) e NA_estimativas (24).
            RDD / "36_equivalencia_H1.py": [RDD / "23_estimar_contagem_vagas.py",
                                            RDD / "24_abertura_vagas_selecao.py"],
            # Protocolo 61: o 38 reproduz N_ (23) e NA_ (24), lê os outcomes (12), o CNES pré (a09), o a08 e importa
            # funções do 29 e do 32.
            RDD / "38_diagnostico_queda_0300.py": [RDD / "23_estimar_contagem_vagas.py",
                                                   RDD / "24_abertura_vagas_selecao.py",
                                                   RDD / "12_construir_outcomes_funil.py", A09,
                                                   AQ / "a08_adquirir_ivs_2010_oficial.py",
                                                   RDD / "29_determinantes_abertura.py",
                                                   RDD / "32_realocacao_bolsa.py"],
            # Protocolo 62: o 39 importa carregar() do 38 (que usa o 24, o 29 e o 32) e lê as escolhas e o quadro do 12.
            RDD / "39_gradiente_faixas.py": [RDD / "38_diagnostico_queda_0300.py", RDD / "24_abertura_vagas_selecao.py",
                                             RDD / "12_construir_outcomes_funil.py", RDD / "29_determinantes_abertura.py",
                                             RDD / "32_realocacao_bolsa.py", AQ / "a08_adquirir_ivs_2010_oficial.py"],
            # Adendo 48b (40): reproduz N_ (23), NA_ (24) e ND_ (23b, versionada); importa o 23 e o 36; lê os
            # outcomes (12) e o a08.
            RDD / "40_h1_vagas_imediatas.py": [RDD / "23_estimar_contagem_vagas.py",
                                               RDD / "24_abertura_vagas_selecao.py",
                                               RDD / "36_equivalencia_H1.py", RDD / "12_construir_outcomes_funil.py",
                                               AQ / "a08_adquirir_ivs_2010_oficial.py"],
            # Protocolo 60, parte B (37): importa o 22 e confere-se contra K_D2_resumo.json; B1/B2 contra o F3 do E7
            # (14); lê o painel do a09, o a16, a X1 (17, versionada) e os outcomes do 12.
            RDD / "37_oferta_local_chegada.py": [RDD / "22_chegada_pmme_evento.py", RDD / "14_estimar_E7_dird_cnes.py",
                                                RDD / "21_producao_dird.py", RDD / "12_construir_outcomes_funil.py",
                                                A09, A16],
            # Protocolo 64 (43): importa o 37 (e por ele o 22, o 21 e o 14); reproduz o F3.1 do E7 (14) e confere V
            # contra OL_resumo.json (37); lê o painel do a09, o a16, a X1 (17, versionada) e os outcomes do 12.
            RDD / "43_oferta_local_corte.py": [RDD / "37_oferta_local_chegada.py", RDD / "22_chegada_pmme_evento.py",
                                               RDD / "14_estimar_E7_dird_cnes.py", RDD / "21_producao_dird.py",
                                               RDD / "12_construir_outcomes_funil.py", A09, A16],
            # Adendo 48c (41): portões contra HI_ (40), NA_ (24) e N_ (23); lê o a08 e a referência do IBGE gravada.
            RDD / "41_h1_capitais_uf.py": [RDD / "40_h1_vagas_imediatas.py", RDD / "24_abertura_vagas_selecao.py",
                                           RDD / "23_estimar_contagem_vagas.py",
                                           AQ / "a08_adquirir_ivs_2010_oficial.py"],
            # Adendo 48d (44): portões contra HI_ (40) e OC_ (43); importa o 19 (CIR), o 23 e o 37, e a leitura da
            # referência do IBGE do 41 (adendo 48c, auditoria 42).
            RDD / "44_controles_localizacao_medicos.py": [RDD / "40_h1_vagas_imediatas.py",
                                                          RDD / "41_h1_capitais_uf.py",
                                                          RDD / "43_oferta_local_corte.py",
                                                          RDD / "37_oferta_local_chegada.py",
                                                          RDD / "23_estimar_contagem_vagas.py"],
            # Adendo 48e (45): importa o 44 (e por ele o 40, o 43, o 37 e o 23) e confere-se contra o PS-1 e o PS-2 de
            # CL_estimativas.csv e os pares de CL_resumo.json, gravados pelo 44.
            RDD / "45_pareamento_regra_literal.py": [RDD / "44_controles_localizacao_medicos.py",
                                                    RDD / "40_h1_vagas_imediatas.py",
                                                    RDD / "43_oferta_local_corte.py"],
            # Adendo 48f (46): portões contra HI_ (40) e o D-b de DQ_ (38); confere o CL-0 de CL_ (44); importa o 24
            # (IC de Imbens–Manski), o 40 e o 44 (covariáveis L e M e H1 municipal).
            RDD / "46_selecao_tipo_vaga.py": [RDD / "44_controles_localizacao_medicos.py",
                                              RDD / "40_h1_vagas_imediatas.py",
                                              RDD / "38_diagnostico_queda_0300.py",
                                              RDD / "24_abertura_vagas_selecao.py",
                                              AQ / "a08_adquirir_ivs_2010_oficial.py"],
            # Adendo 48g (47): portões contra HI_ (40) e o OC-A1 de OC_ (43); importa o 40, o 43 e o 44 (referência do
            # IBGE); lê a regra do IED e o porte do a10 (JSON e CSV) e o a08.
            RDD / "47_heterogeneidade_porte_ied.py": [RDD / "40_h1_vagas_imediatas.py",
                                                      RDD / "43_oferta_local_corte.py",
                                                      RDD / "44_controles_localizacao_medicos.py",
                                                      AQ / "a10_normas_mesmos_cortes_ivs.py",
                                                      AQ / "a08_adquirir_ivs_2010_oficial.py"],
            # Adendo 48h (49): importa o 44 e o 45 (e por eles o 40 e o 43) e confere-se contra o PM-1 de
            # PM_estimativas.csv e os pares de PM_resumo.json (45); lê a X1 versionada e os centroides do 17.
            RDD / "49_pareamento_localizacao.py": [RDD / "45_pareamento_regra_literal.py",
                                                   RDD / "44_controles_localizacao_medicos.py",
                                                   RDD / "40_h1_vagas_imediatas.py",
                                                   RDD / "43_oferta_local_corte.py"],
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
            # Extensões do P3 (27, adendo §12): importa o 21 e o 22 e confere K_D1/K_D2; lê as safras v2 (a12b,
            # a13b), o SIH por residência (a15) e o SIA por forma × curso (a17).
            RDD / "27_producao_extensoes.py": [RDD / "21_producao_dird.py", RDD / "22_chegada_pmme_evento.py",
                                               RDD / "12_construir_outcomes_funil.py", A12B, A13B, A15, A17],
            # a15 (SIH por residência) compara seus totais nacionais com as validações versionadas do a13.
            A15: [AQ / "a13_adquirir_sih_tabnet.py"],
            # a16 (portão G5) importa funções do a09 e confere o SHA-256 dos ZIPs contra o manifesto dele.
            A16: [A09],
            # Safras v2 (adendo §12.1): o a12b embrulha o a12 e compara com a v1; o a13b embrulha o a13 e compara
            # com a v1 e com as validações do a15.
            A12B: [AQ / "a12_adquirir_sia_tabnet.py"],
            A13B: [AQ / "a13_adquirir_sih_tabnet.py", A15],
            # a17 (adendo §12.2) importa o a12, lê o G4 e cruza com as tabelas CBO × subgrupo do a12 e do a12b.
            A17: [AQ / "a12_adquirir_sia_tabnet.py", A12B, AQ / "01_congelar_ponte_cbo.py"],
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
                                              A15, A16, A12B, A13B, A17, P6_PASSO0,
                                              RDD / "35_comparacao_alternativa_P3P4.py",
                                              RDD / "34_sensibilidade_honestdid.py"})
        # Protocolo 59: o 35 exige o cache privado e o 34 leva cerca de uma hora; o run_all só confere.
        for script in (RDD / "35_comparacao_alternativa_P3P4.py", RDD / "34_sensibilidade_honestdid.py"):
            self.assertEqual(RA.ARGUMENTOS[script], ["--etapa", "verificar"], script.name)
        # P6, passo 0: a amostra vem do cache privado; o run_all só confere sem rede.
        self.assertEqual(RA.ARGUMENTOS[P6_PASSO0], ["--etapa", "verificar"])
        # a16 (portão G5): como o a09, o run_all só confere sem rede.
        self.assertEqual(RA.ARGUMENTOS[A16], ["--etapa", "verificar"])
        self.assertEqual(RA.ARGUMENTOS[AQ / "a12_adquirir_sia_tabnet.py"], ["--etapa", "verificar"])
        # a13 (SIH no TabNet, protocolo 47): como o a09, o run_all só confere sem rede.
        self.assertEqual(RA.ARGUMENTOS[AQ / "a13_adquirir_sih_tabnet.py"], ["--etapa", "verificar"])
        self.assertEqual(RA.ARGUMENTOS[A14], ["--etapa", "verificar"])
        # a15 (SIH por residência, portão G3): como o a13, o run_all só confere sem rede; fora do --rdd-bolsa.
        self.assertEqual(RA.ARGUMENTOS[A15], ["--etapa", "verificar"])
        self.assertNotIn(A15, RA.etapas(somente_rdd_bolsa=True))
        # Safras v2 e a17 (adendo §12 do protocolo 47): só verificar, sem rede; fora do --rdd-bolsa.
        for script in (A12B, A13B, A17):
            self.assertEqual(RA.ARGUMENTOS[script], ["--etapa", "verificar"], script.name)
            self.assertNotIn(script, RA.etapas(somente_rdd_bolsa=True), script.name)
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
