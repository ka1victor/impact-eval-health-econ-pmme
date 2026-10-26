"""Executa o pipeline validado do projeto no seu estado atual ponta a ponta.

Uso:

    python run_all.py              # pipeline inteiro
    python run_all.py --rdd-bolsa  # só a cadeia da RDD da bolsa (a07 a 14)

A opção `--rdd-bolsa` roda a cadeia sobre os insumos já versionados das etapas
anteriores (quadro de vagas, funil e tipologia do ciclo 1, população do Censo
2022, painel do ciclo 1), inclusive as aquisições a07 a a11 e a rodada
multi-outcome (12, 13, 16 e 14), a família N (23), a abertura (24 e o P5, 29), a escolha do P1 (25), a trajetória dos médicos (P4, 28), o mecanismo de alocação (P6, 30 em
`--etapa verificar` e 31) e a família K (21, 22 e as extensões do P3, 27). Nenhuma etapa baixa o CNES nacional, o SIA, o SIH nem o
TISS: o a09, o a12, o a12b, o a13, o a13b, o a14, o a15, o a16 (portão G5) e o a17 rodam em `--etapa verificar`;
o a12b, o a13, o a13b, o a15 e o a17 não fazem parte da opção `--rdd-bolsa`.
"""

from pathlib import Path
import argparse
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))

from utils.ambiente import verificar_ambiente  # noqa: E402

# Mudar STEPS exige regerar o manifesto A6: scripts/tema_trabalho/07_red_team_sintese.py
# deriva desta lista, por AST, a sequência de reprodução, e tests/test_red_team_a6.py
# confere as duas. Por isso cada passo é um caminho literal `ROOT / "..."`.
STEPS = [
    ROOT / "scripts" / "00_inventario_dados.py",
    ROOT / "scripts" / "02_auditar_fontes_pmme.py",
    ROOT / "scripts" / "aquisicao" / "01_congelar_ponte_cbo.py",
    ROOT / "scripts" / "aquisicao" / "02_consolidar_quadro_vagas.py",
    # Retirados em 18/10/2026: rdd_bolsa/01_auditar_regra_e_suporte.py e
    # rdd_bolsa/01_auditar_primeiro_estagio_publico.py usam como running variable
    # data/ivs_ipea_2010_municipios.csv, que não é o IVS do município
    # (docs/auditorias/16_ivs_2010_oficial_e_arquivo_local.md). Ver o bloco da RDD abaixo.
    #
    # a07, a08 e o Censo 2022 vêm antes da malha territorial desde 18/10/2026: 04_harmonizar e
    # tema_trabalho/01 leem o IVS 2010 oficial gravado pelo a08, e não mais o arquivo
    # local (docs/auditorias/19_reestimacao_base_oficial_failure_mode.md). Os dois só leem
    # insumos brutos; a ordem relativa da cadeia da RDD (a07 < a08 < 04 < ... < 10) fica igual.
    ROOT / "scripts" / "aquisicao" / "a07_adquirir_ivs_administrativo.py",
    ROOT / "scripts" / "aquisicao" / "a08_adquirir_ivs_2010_oficial.py",
    # População residente do Censo 2022 (SIDRA 4709), denominador por habitante da
    # malha e da tipologia; roda sem rede a partir de data/raw/aquisicao/populacao/.
    ROOT / "scripts" / "aquisicao" / "06_adquirir_populacao_censo2022.py",
    ROOT / "scripts" / "aquisicao" / "04_harmonizar_territorio_ibge.py",
    ROOT / "scripts" / "aquisicao" / "05_integrar_painel_analitico.py",
    ROOT / "scripts" / "avaliacao_impacto" / "run_pipeline_avaliacao.py",
    ROOT / "scripts" / "tema_trabalho" / "01_auditar_atracao_provimento_interior.py",
    ROOT / "scripts" / "tema_trabalho" / "02_reconciliar_funil_ciclo1.py",
    ROOT / "scripts" / "tema_trabalho" / "03_construir_tipologia_territorial.py",
    ROOT / "scripts" / "tema_trabalho" / "04_congelar_pre_analise.py",
    ROOT / "scripts" / "tema_trabalho" / "05_estimar_atracao.py",
    ROOT / "scripts" / "tema_trabalho" / "06_avaliar_provimento_cnes.py",
    ROOT / "scripts" / "tema_trabalho" / "06b_ameacas_a5_placebo_pretendencia_deslocamento.py",
    # A síntese A6 (07_red_team_sintese.py) roda depois da cadeia da RDD, cujas saídas lê.
    ROOT / "scripts" / "tema_trabalho" / "08_auditar_cutoff_selecao.py",
    ROOT / "scripts" / "tema_trabalho" / "09_estimar_cutoff_escore_estrito.py",
    ROOT / "scripts" / "tema_trabalho" / "09b_intervalos_exatos_escore.py",
    # RDD da bolsa, na ordem de dependência (docs/06_execucao/38_estado_e_pendencias_rdd_bolsa.md, §4).
    # A running variable é o IVS 2010 oficial do Ipea (a08). 07, 08a e 08 leem o funil do
    # ciclo 1 (tema_trabalho/02); 07, a tipologia (tema_trabalho/03); 08a, o quadro de
    # tratamento (aquisicao/02).
    #
    # Retirados em 18/10/2026, sem apagar os scripts nem as saídas já versionadas, que
    # ficam como registro superado (09, 09b e tema_trabalho/10 ainda leem a01b_*,
    # a01_* e portao_regra_ivs.json como histórico): rdd_bolsa/01b_reconstruir_regra_faixa.py lê
    # data/ivs_ipea_2010_municipios.csv como IVS 2010; rdd_bolsa/02_controlar_execucao_plano_causal.py
    # consolida os portões feitos com esse arquivo (01, 01_primeiro_estagio) e regrava
    # docs/06_execucao/33; rdd_bolsa/03_triagem_resposta_administrativa.py faz a triagem da
    # resposta ao pedido do escore ao MS, cancelado porque o escore é público (auditoria 16, §4).
    # a07 e a08, as aquisições desta cadeia, rodam no início (ver acima).
    ROOT / "scripts" / "rdd_bolsa" / "04_portao_r1_escore_administrativo.py",
    ROOT / "scripts" / "rdd_bolsa" / "04b_validar_ivs_oficial_escore_administrativo.py",
    ROOT / "scripts" / "rdd_bolsa" / "04c_identificar_recorte_arquivo_local.py",
    ROOT / "scripts" / "rdd_bolsa" / "05_estimar_E1_densidade.py",
    ROOT / "scripts" / "rdd_bolsa" / "06_estimar_E2_limites.py",
    ROOT / "scripts" / "rdd_bolsa" / "07_estimar_E3_rdd_completa.py",
    ROOT / "scripts" / "rdd_bolsa" / "08a_reconstruir_proporcao_preenchida.py",
    ROOT / "scripts" / "rdd_bolsa" / "08_estimar_E4_proporcao.py",
    # E5, exploratório e pós-resultado: reproduz o principal do E3 e lê a proporção do 08a.
    ROOT / "scripts" / "rdd_bolsa" / "11_inferencia_alternativa.py",
    # Rodada multi-outcome (docs/06_execucao/40_protocolo_multioutcome_rdd_bolsa.md, §11),
    # antes do relatório 09, que lê E1 a E9 e a síntese E8. Aquisições primeiro, todas sem rede
    # quando o cache versionado confere: a10 (normas nos mesmos cortes; lê a07 e a08),
    # a11 (resultado da 1a chamada do ciclo 2) e a09 (CNES nacional; o run_all só confere
    # o painel versionado com `--etapa verificar`, ver ARGUMENTOS).
    ROOT / "scripts" / "aquisicao" / "a10_normas_mesmos_cortes_ivs.py",
    ROOT / "scripts" / "aquisicao" / "a11_adquirir_resultado_ciclo2_chamada1.py",
    ROOT / "scripts" / "aquisicao" / "a09_adquirir_cnes_nacional.py",
    # a12 (SIA/SUS do TabNet, protocolo 47): como o a09, só confere as saídas versionadas
    # contra o manifesto, sem rede (ver ARGUMENTOS). Lê a ponte (01) e a regra de CBO do a09.
    ROOT / "scripts" / "aquisicao" / "a12_adquirir_sia_tabnet.py",
    # Safra v2 do SIA nos meses 202509–202607 (a12b, adendo §12.1 do protocolo 47): embrulho do a12;
    # só confere as saídas versionadas e a comparação com a v1, sem rede (ver ARGUMENTOS). Não lê IVS.
    ROOT / "scripts" / "aquisicao" / "a12b_safra_v2_sia.py",
    # SIH/SUS no TabNet (protocolo 47, insumo de K2): o run_all só confere os painéis
    # versionados com `--etapa verificar`, sem rede (ver ARGUMENTOS). Não lê IVS.
    ROOT / "scripts" / "aquisicao" / "a13_adquirir_sih_tabnet.py",
    # SIH por local de residência (a15, portão G3 do plano 51): como o a13, só confere os painéis
    # versionados sem rede (ver ARGUMENTOS). Vem depois do a13, cujas validações compara. Não lê IVS.
    ROOT / "scripts" / "aquisicao" / "a15_adquirir_sih_residencia.py",
    # Safra v2 do SIH (a13b, adendo §12.1 do protocolo 47): embrulho do a13; compara com a v1 do a13 e com
    # as validações do a15; só confere sem rede (ver ARGUMENTOS). Não lê IVS.
    ROOT / "scripts" / "aquisicao" / "a13b_safra_v2_sih.py",
    # SIA por forma de organização × curso específico (a17, adendo §12.2 do protocolo 47): importa o a12 e o
    # G4 e cruza com as tabelas CBO × subgrupo do a12 e do a12b; só confere sem rede (ver ARGUMENTOS).
    ROOT / "scripts" / "aquisicao" / "a17_adquirir_sia_forma_curso.py",
    # TISS/ANS do protocolo 47 (a14): como o a09, só confere o painel versionado (ARGUMENTOS).
    ROOT / "scripts" / "aquisicao" / "a14_adquirir_tiss_ans.py",
    # Portão G5 (doc 51, T4.0): painel CNES médico × mês dos médicos ligados na X1 (a16). Como o a09,
    # só confere as saídas versionadas contra o manifesto, sem rede e sem gravar (ver ARGUMENTOS).
    ROOT / "scripts" / "aquisicao" / "a16_cnes_profissional_mensal.py",
    # Outcomes do funil (tarefa B): lê E4 (08) e o manifesto do a11.
    ROOT / "scripts" / "rdd_bolsa" / "12_construir_outcomes_funil.py",
    # E6: lê os outcomes (12), E3, E4, a janela LR do E5 (11) e as saídas do a10.
    ROOT / "scripts" / "rdd_bolsa" / "13_estimar_E6_funil.py",
    # Família N (protocolo 48, pós-resultado): número de vagas preenchidas com e sem controle pelas
    # vagas oferecidas. Lê os outcomes (12), a janela LR e as estimativas do E6 (13) e os editais.
    ROOT / "scripts" / "rdd_bolsa" / "23_estimar_contagem_vagas.py",
    # E9: lê as tabelas de escolha do 12 e o manifesto do a11.
    ROOT / "scripts" / "rdd_bolsa" / "16_estimar_E9_escolha.py",
    # Adendo §7 do protocolo 48 (pós-resultado): abertura de vagas como seleção (A1–A4). Lê os outcomes (12),
    # o painel CNES pré-programa (a09), o Censo 2022 (a06), N_estimativas (23) e o resumo do E9 (16).
    ROOT / "scripts" / "rdd_bolsa" / "24_abertura_vagas_selecao.py",
    # P5 (protocolo 55, descritivo): determinantes do pedido, da priorização (ciclo 3) e do quadro (ciclos 1-2).
    # Lê os outcomes e as leituras do cardápio e da adesão do 12, o CNES pré (a09), o SIA pré (a12), o a08, o
    # Censo 2022 (a06), a tipologia (tema_trabalho/03), o REGIC e a CIR brutos, e funções do 24 e do 23.
    ROOT / "scripts" / "rdd_bolsa" / "29_determinantes_abertura.py",
    # P1 (protocolo 52, T1.1–T1.5): escolha do candidato, DAP, logit misto e aninhado, ponte P1 → P2. Lê as tabelas
    # de escolha do 12, o a08, as saídas versionadas do portão G1 (fora do run_all), a CIR e os centroides brutos,
    # E9_estimativas (16, conferência) e NA_estimativas (24, conferência da RDD por célula); importa o 16, o 17 e o 19.
    ROOT / "scripts" / "rdd_bolsa" / "25_escolha_dap.py",
    # P1h (protocolo 52b, pós-resultado): peso da bolsa contra o custo do lugar (H3). Reestima M1, M2, M4, M5 e M7 com
    # as funções do 25 só para a covariância conjunta e para se não reproduzir P1_estimativas.csv (portão 1e-8).
    ROOT / "scripts" / "rdd_bolsa" / "25c_magnitudes_P1h.py",
    # Realocação (protocolo 58, exploratório): a bolsa das concorrentes do mesmo curso e ciclo na região de saúde
    # desloca candidatos e preenchimento? Lê as células do 12, o a08, a grade de faixas (a03, a04), a CIR e os
    # centroides brutos, o Censo 2022 (a06) e o CNES pré (a09, função do 24); importa o 16, o 17, o 19 e o 24.
    ROOT / "scripts" / "rdd_bolsa" / "32_realocacao_bolsa.py",
    # P4 (protocolo 54, exploratório): trajetória individual dos médicos do PMM-E, origem e contabilidade líquida.
    # Lê o painel médico × mês do a16 (conferido acima), X1_medicos.parquet (saída versionada do 17, fora do
    # run_all), as listas nominais só em memória (função do 17), o painel do a09 e a ponte curso–CBO. Não lê IVS.
    ROOT / "scripts" / "rdd_bolsa" / "28_trajetoria_medicos.py",
    # P6 (protocolo 56, exploratório): amostra do mecanismo de alocação e passo 0. A amostra vem do cache privado
    # do a16 e do dicionário do G1 (fora do Git); o run_all só confere as saídas versionadas contra o resumo do
    # passo 0, sem rede e sem gravar (ver ARGUMENTOS). Lê o G1 e o G2 versionados. Não lê IVS.
    ROOT / "scripts" / "rdd_bolsa" / "30_mecanismo_alocacao.py",
    # P6: estimação R1–R5, balanço e doc 57f, só das saídas versionadas do 30.
    ROOT / "scripts" / "rdd_bolsa" / "31_rd_mecanismo.py",
    # E7: lê o painel do a09, o IED do a10, a janela LR do E5 e confere a de U com a do E6 (13).
    ROOT / "scripts" / "rdd_bolsa" / "14_estimar_E7_dird_cnes.py",
    # Família K (protocolo 47, pós-síntese, Holm próprio): D1, DiRD da produção especializada nos cortes.
    # Lê as saídas versionadas do a12 (SIA), a13 (SIH), a14 (TISS) e a09 (CNES), o a08, o Censo 2022, a lista de
    # V1 do 12, o IED do a10 e funções do E7 (14) e das figuras da família N (23).
    ROOT / "scripts" / "rdd_bolsa" / "21_producao_dird.py",
    # D2 (exploratório): chegada do especialista do PMM-E, Callaway-Sant'Anna. Lê as mesmas séries do D1 (21),
    # a lista nominal (só leitura), os outcomes do 12 e X2_municipios.csv (saída versionada do 18, fora do run_all).
    ROOT / "scripts" / "rdd_bolsa" / "22_chegada_pmme_evento.py",
    # P3, adendo §12 do protocolo 47 (pós-resultado, BKY próprio): especialidade (a17), residentes (a15), safra v2
    # do SIH (a13b) e do SIA (a12b), controles alternativos, DiD sintético e região de saúde. Importa o 21 e o 22,
    # confere-se contra K_D1/K_D2 e lê o G4, a X1 (17) e as células do 12.
    ROOT / "scripts" / "rdd_bolsa" / "27_producao_extensoes.py",
    # Protocolo 59 (pós-resultado): comparação alternativa do P3/P4 (35) e sensibilidade de Rambachan–Roth (34).
    # O 35 refaz o painel dos candidatos do cache privado (fora do Git) e o 34 recalcula as funções de influência
    # do 27 e do 28; no run_all os dois só conferem as saídas e o doc 57h contra o resumo (ver ARGUMENTOS).
    ROOT / "scripts" / "rdd_bolsa" / "35_comparacao_alternativa_P3P4.py",
    ROOT / "scripts" / "rdd_bolsa" / "34_sensibilidade_honestdid.py",
    # Protocolo 60, parte A (pós-resultado): TOST de equivalência de A3 e N1. Lê só as estimativas gravadas pelo 23
    # (N_estimativas) e pelo 24 (NA_estimativas) e confere-as contra o doc 57; não reestima nada.
    ROOT / "scripts" / "rdd_bolsa" / "36_equivalencia_H1.py",
    # Protocolo 61 (diagnóstico pós-resultado): por que o preenchimento cai em 0,300 (D-a a D-g). Reproduz Q1–Q3 e
    # para se não baterem com N_ (23), NA_ (24) e ND_estimativas (23b, saída versionada, fora do run_all); lê os
    # outcomes do 12, o CNES pré (a09), o G1 versionado, a CIR, o REGIC e o cardápio (funções do 29) e as exposições
    # de concorrência do 32.
    ROOT / "scripts" / "rdd_bolsa" / "38_diagnostico_queda_0300.py",
    # Protocolo 60, parte B (pós-resultado): oferta local de especialistas depois da chegada do 1º médico do PMM-E
    # (Callaway-Sant'Anna município × mês). Importa o 22 (que importa o 21 e o 14) e a honestdid_lib; confere as
    # coortes contra K_D2_resumo.json (22) e B1/B2 contra o F3 do E7 (14); lê o a09, o a16, a X1 (17, versionada),
    # os outcomes do 12, a lista nominal e a de ativos (só colunas sem nome). Não lê IVS como variável.
    ROOT / "scripts" / "rdd_bolsa" / "37_oferta_local_chegada.py",
    # Síntese E8: lê E3, E5, E6, E7 e E9 e aplica o Holm às primárias P1 e P2.
    ROOT / "scripts" / "rdd_bolsa" / "15_sintese_E8.py",
    # O relatório para se a conferência do sinal não corresponder ao E3 atual.
    ROOT / "scripts" / "rdd_bolsa" / "09b_conferir_sinal.py",
    ROOT / "scripts" / "rdd_bolsa" / "09_gerar_relatorio_pdf.py",
    ROOT / "scripts" / "rdd_bolsa" / "10_galeria_figura_regra.py",
    # Fora do pipeline: tema_trabalho/12_registrar_failure_mode_ivs.py lê com `git show`
    # as versões anteriores à correção de 18/10/2026 (commit 22eddb5) e para sem elas;
    # num clone raso o pipeline quebraria por motivo alheio aos dados. Roda-se à mão,
    # depois do pipeline (scripts/README.md).
    # A6 lê R1, E3 e E5 e registra os hashes deles no manifesto.
    ROOT / "scripts" / "tema_trabalho" / "07_red_team_sintese.py",
    ROOT / "scripts" / "tema_trabalho" / "10_conferir_numeros_artigo.py",
    ROOT / "scripts" / "tema_trabalho" / "11_conferir_numeros_artigo_curto.py",
]

# Argumentos de linha de comando por passo. Ficam fora de STEPS porque os leitores
# por AST só aceitam caminhos; o manifesto A6 não os registra. O `--escore` do E3
# repete o padrão do script (IVS 2010 oficial, gravado pelo 04b) para deixar a
# running variable explícita; com o escore parcial do a07, o E3 para em
# AGUARDANDO_ESCORE_COMPLETO e apaga as saídas E3.
ARGUMENTOS = {
    ROOT / "scripts" / "rdd_bolsa" / "07_estimar_E3_rdd_completa.py": [
        "--escore", "output/rdd_bolsa/escore_completo_ivs2010_oficial.csv",
    ],
    # O painel do CNES nacional vem de 39 ZIPs (~600 MB cada, ~23 GB) cujo cache fica
    # fora do Git. O run_all só confere o painel versionado contra o manifesto, sem rede
    # e sem gravar. Refazer exige pedir de propósito: `--etapa painel` (cache local) ou
    # `--etapa tudo` (download). Decisão de 19/10/2026 (tarefa E8d).
    ROOT / "scripts" / "aquisicao" / "a09_adquirir_cnes_nacional.py": ["--etapa", "verificar"],
    # O SIA vem de ~400 consultas ao TabNet cujas respostas brutas ficam fora do Git
    # (output/aquisicao/sia/brutos/). O run_all só confere as saídas versionadas contra o
    # manifesto, sem rede e sem gravar. Refazer exige `--etapa consolidar` (cache local) ou
    # `--etapa tudo` (download). Protocolo 47, 19/10/2026.
    ROOT / "scripts" / "aquisicao" / "a12_adquirir_sia_tabnet.py": ["--etapa", "verificar"],
    # O SIH vem de 440 consultas ao TabNet cujo cache bruto fica fora do Git. Como no a09,
    # o run_all só confere os painéis versionados contra o manifesto, sem rede e sem gravar;
    # refazer exige `--etapa consolidar` (cache local) ou `--etapa tudo` (download).
    ROOT / "scripts" / "aquisicao" / "a13_adquirir_sih_tabnet.py": ["--etapa", "verificar"],
    # SIH por residência (a15): 495 consultas ao TabNet, cache bruto fora do controle de versão; o run_all só
    # confere as saídas versionadas contra o manifesto, sem rede e sem gravar.
    ROOT / "scripts" / "aquisicao" / "a15_adquirir_sih_residencia.py": ["--etapa", "verificar"],
    # Safras v2 (adendo §12.1 do protocolo 47) e a17 (adendo §12.2): consultas ao TabNet com cache bruto
    # fora do controle de versão; o run_all só confere as saídas versionadas contra o manifesto, sem rede.
    ROOT / "scripts" / "aquisicao" / "a12b_safra_v2_sia.py": ["--etapa", "verificar"],
    ROOT / "scripts" / "aquisicao" / "a13b_safra_v2_sih.py": ["--etapa", "verificar"],
    ROOT / "scripts" / "aquisicao" / "a17_adquirir_sia_forma_curso.py": ["--etapa", "verificar"],
    # TISS/ANS (a14): cerca de 83 GB de ZIPs, apagados depois da agregação; o run_all só
    # confere as saídas versionadas contra o manifesto, sem rede e sem gravar.
    ROOT / "scripts" / "aquisicao" / "a14_adquirir_tiss_ans.py": ["--etapa", "verificar"],
    # Portão G5 (a16): 27 ZIPs do CNES (~20 GB), apagados depois da extração; o cache com registro do
    # conselho fica fora do Git. O run_all só confere as saídas versionadas, sem rede e sem gravar.
    ROOT / "scripts" / "aquisicao" / "a16_cnes_profissional_mensal.py": ["--etapa", "verificar"],
    # P6, passo 0 (30): a amostra exige o cache privado do a16 e o dicionário do G1, fora do Git. O run_all só
    # confere as saídas versionadas contra P6_passo0_resumo.json, sem rede e sem gravar; refazer exige
    # `--etapa aquisicao` e `--etapa construir`.
    ROOT / "scripts" / "rdd_bolsa" / "30_mecanismo_alocacao.py": ["--etapa", "verificar"],
    # Protocolo 59: o 35 exige o cache privado do a16 e do G1 para recalcular; o 34 leva cerca de uma hora.
    ROOT / "scripts" / "rdd_bolsa" / "35_comparacao_alternativa_P3P4.py": ["--etapa", "verificar"],
    ROOT / "scripts" / "rdd_bolsa" / "34_sensibilidade_honestdid.py": ["--etapa", "verificar"],
}

AQUISICAO_RDD_BOLSA = (
    ROOT / "scripts" / "aquisicao" / "a07_adquirir_ivs_administrativo.py",
    ROOT / "scripts" / "aquisicao" / "a08_adquirir_ivs_2010_oficial.py",
    ROOT / "scripts" / "aquisicao" / "a10_normas_mesmos_cortes_ivs.py",
    ROOT / "scripts" / "aquisicao" / "a11_adquirir_resultado_ciclo2_chamada1.py",
    ROOT / "scripts" / "aquisicao" / "a09_adquirir_cnes_nacional.py",
    ROOT / "scripts" / "aquisicao" / "a12_adquirir_sia_tabnet.py",
    ROOT / "scripts" / "aquisicao" / "a14_adquirir_tiss_ans.py",
    ROOT / "scripts" / "aquisicao" / "a16_cnes_profissional_mensal.py",
)


def etapas(somente_rdd_bolsa: bool = False) -> list[Path]:
    """Passos a executar, na ordem de STEPS."""
    if not somente_rdd_bolsa:
        return list(STEPS)
    return [p for p in STEPS if p in AQUISICAO_RDD_BOLSA or p.parent == ROOT / "scripts" / "rdd_bolsa"]


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument(
        "--rdd-bolsa",
        action="store_true",
        help="executa só a cadeia da RDD da bolsa (a07 a 14), sobre os insumos versionados",
    )
    args = parser.parse_args(argv)

    # O pipeline grava artefato versionado, cuja proveniencia e ancorada em
    # SHA-256. Ambiente divergente reescreve arquivo em silencio, entao aqui a
    # verificacao aborta em vez de avisar.
    verificar_ambiente(estrito=True)

    alvo = "da cadeia da RDD da bolsa" if args.rdd_bolsa else "consolidado do PMM-E"
    print(f"Iniciando execução do pipeline {alvo}...\n")
    for script in etapas(args.rdd_bolsa):
        extras = ARGUMENTOS.get(script, [])
        print(f">> Executando {' '.join([str(script.relative_to(ROOT)), *extras])}...")
        subprocess.run([sys.executable, str(script), *extras], cwd=ROOT, check=True)
        print()

    destinos = (
        "output/aquisicao/ e output/rdd_bolsa/" if args.rdd_bolsa
        else "output/aquisicao/, output/avaliacao_impacto/, output/tema_trabalho/ e output/rdd_bolsa/"
    )
    print(f"Pipeline executado com sucesso! Artefatos consolidados salvos em {destinos}.")


if __name__ == "__main__":
    main()
