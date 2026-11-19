# 06 — Execução: índice por trilha

> **Por que um índice, e não subpastas.** Cerca de 60 saídas de `output/` gravam o caminho e o SHA-256 destes
> documentos (protocolos congelados, docs gerados por script). Mover um arquivo quebraria essa cadeia de
> proveniência. A numeração fica como está, e a organização é esta página.<br>
> **Convenção:** número inteiro para protocolo ou plano (`52`), letra para adendo ou resultado ligado a ele (`52e`,
> `57x`). O doc de resultado diz no topo o script que o gera e a saída de onde vêm os números.

## Comece aqui

| Para | Leia |
|---|---|
| o resultado da banca final (logit condicional, vagas da mesma UF, ×1,47) | [57x](57x_resultados_escolha_localizacao_par.md) e [66](66_analise_completa_H2.md) |
| o balanço de todas as perguntas da bolsa | [57](57_sintese_perguntas_reformuladas.md) (perguntas reformuladas) e [44](44_sintese_rdd_bolsa_multioutcome.md) (RDD multi-outcome) |
| o estado da RDD da bolsa e o que falta decidir | [38](38_estado_e_pendencias_rdd_bolsa.md) |
| a fila de execução e os portões | [05](05_roadmap_execucao.md) e [33](33_status_execucao_plano_causal.md) |

## 1. Gestão da execução

| Doc | O que é |
|---|---|
| [05](05_roadmap_execucao.md) | roadmap de execução (ciclo 1 validado) |
| [06](06_backlog_wp3_wp4_wp5.md) | backlog guardado: WP3, WP4 e WP5 |
| [33](33_status_execucao_plano_causal.md) | estado executado do plano causal público |
| [35](35_plano_correcoes_pos_auditoria.md) | plano de correções pós-auditoria (congelado) |
| [36](36_backlog_pos_auditoria.md) | backlog pós-auditoria |

## 2. Ciclo 1 e artigos (A3–A8)

| Doc | O que é |
|---|---|
| [31](31_secao_econometrica_A3.md) | seção econométrica congelada (A3) |
| [32](32_sintese_A6_resumo_intro_metodos_conclusao.md) | síntese empírica A6 |
| [34](34_minuta_trabalho_curto_cutoff_escore.md) | minuta do trabalho curto (corte de escore, A8) |

## 3. RDD da bolsa no IVS 2010 oficial

| Protocolo | Resultado | Tema |
|---|---|---|
| — | [37](37_resultados_rdd_bolsa_ivs_oficial.md), [38](38_estado_e_pendencias_rdd_bolsa.md), [39](39_inferencia_alternativa_rdd_bolsa.md) | E3 (principal), estado e pendências, E5 (inferência alternativa) |
| [40](40_protocolo_multioutcome_rdd_bolsa.md) | [41](41_resultados_E6_funil.md) (com [41a](41a_construcao_outcomes_funil.md)), [42](42_resultados_E9_escolha.md), [43](43_resultados_E7_dird_cnes.md), [**44**](44_sintese_rdd_bolsa_multioutcome.md) | rodada multi-outcome: funil (E6), escolha (E9), CNES (E7) e síntese (E8) |
| [45](45_protocolo_exploratorio_pos_sintese.md) | [46](46_resultados_exploratorios_pos_sintese.md) | exploratório pós-síntese (X1–X6) |
| [47](47_protocolo_producao_especializada.md) | [50](50_resultados_producao_especializada.md), [57c](57c_resultados_P3_extensoes.md) | produção especializada (família K e P3) |

## 4. H1 — preenchimento e número de vagas no corte

| Protocolo ou adendo | Resultado | Tema |
|---|---|---|
| [48](48_protocolo_contagem_vagas_preenchidas.md) | [49](49_resultados_contagem_vagas_preenchidas.md), [49b](49b_diagnostico_contagem_porte.md) | vagas preenchidas com e sem controle pelas oferecidas (família N) |
| [48b](48b_adendo_H1_vagas_imediatas.md) | [57n](57n_resultados_H1_vagas_imediatas.md) | só vagas imediatas |
| [48c](48c_adendo_capitais_e_UF.md) | [57o](57o_h1_capitais_uf.md) | capitais e UF no corte 0,300 |
| [48d](48d_adendo_controles_localizacao_e_medicos.md) | [57r](57r_resultados_controles_localizacao_medicos.md) | controles de localização e de médicos na região |
| [48e](48e_adendo_pareamento_regra_literal_e_0400.md) | [57s](57s_resultados_pareamento_regra_literal.md) | pareamento pela regra literal e PSM em 0,400 |
| [48f](48f_adendo_selecao_tipo_de_vaga.md) | [57t](57t_resultados_selecao_tipo_vaga.md) | seleção pelo tipo de vaga (limites de Lee) |
| [48g](48g_adendo_heterogeneidade_porte_ied.md) | [57u](57u_resultados_heterogeneidade_porte.md) | heterogeneidade pelo porte e IED |
| [48h](48h_adendo_pareamento_localizacao_unidade_e_medicos.md) | [57w](57w_resultados_pareamento_localizacao.md) | pareamento pela localização da unidade e dos médicos |
| [60](60_protocolo_equivalencia_e_oferta_local.md), parte A | [57j](57j_resultados_equivalencia_H1.md) | equivalência no preenchimento (TOST) |
| [61](61_protocolo_diagnostico_queda_0300.md) | [57l](57l_diagnostico_queda_0300.md) | por que o preenchimento cai em 0,300 |
| [62](62_protocolo_gradiente_dentro_das_faixas.md) | [57m](57m_gradiente_faixas.md) | gradiente dentro das faixas (descritivo) |
| [63](63_registro_explicacoes_e_controles_H1.md) | — | explicações candidatas e controles da H1 |

## 5. H2 — escolha da 1ª opção (logit condicional; banca 2 e banca final)

| Protocolo ou adendo | Resultado | Tema |
|---|---|---|
| [52](52_protocolo_P1_escolha_dap.md) | [57a](57a_resultados_P1_escolha.md), [57b](57b_cenarios_P1_bolsa.md) (simulação) | P1: quanto a bolsa move a escolha (M1, pré-registrado) |
| [52b](52b_protocolo_P1h_magnitudes.md) | [57i](57i_resultados_P1h_magnitudes.md) | P1h: peso da bolsa contra o custo do lugar |
| [52c](52c_adendo_vaga_imediata_ciclo2.md) | [57p](57p_escolha_vaga_imediata_c2.md) | tipo de vaga do ciclo 2 medido antes da alocação |
| [52d](52d_adendo_sensibilidades_ciclo2_quadro_1302.md) | [57v](57v_sensibilidades_ciclo2_quadro_1302.md) | sensibilidades com o quadro de 13/02 |
| [**52e**](52e_adendo_escolha_localizacao_par.md) | [**57x**](57x_resultados_escolha_localizacao_par.md) | **VL-1: vagas da mesma UF (resultado da banca final)** |
| [52f](52f_adendo_robustez_E9_ciclo2_quadro_1302.md) | [57y](57y_robustez_E9_ciclo2_quadro_1302.md) | robustez do E9 no ciclo 2 |
| [52g](52g_adendo_VL1_por_ciclo.md) | [57z](57z_VL1_por_ciclo.md) | VL-1 ciclo a ciclo |
| [52h](52h_adendo_VL1_por_corte.md) | [57za](57za_VL1_por_corte.md) | VL-1 por corte |
| — | [65](65_avaliacao_forca_hipoteses.md), [**66**](66_analise_completa_H2.md) | avaliação da força das hipóteses e análise completa da H2 |

## 6. Outras perguntas reformuladas (plano [51](51_plano_perguntas_reformuladas.md); síntese [57](57_sintese_perguntas_reformuladas.md))

| Protocolo | Resultado | Tema |
|---|---|---|
| [54](54_protocolo_P4_oferta_substituicao.md) | [57d](57d_resultados_P4_trajetoria.md) | P4: oferta nova ou substituição |
| [55](55_protocolo_P5_abertura_vagas.md) | [57e](57e_resultados_P5_abertura.md) | P5: onde o Ministério abre vagas |
| [56](56_protocolo_P6_mecanismo_alocacao.md) | [57f](57f_resultados_P6_mecanismo.md) | P6: alocado por pouco contra não alocado |
| [58](58_protocolo_realocacao_bolsa.md) | [57g](57g_resultados_realocacao.md) | realocação pela bolsa das concorrentes |
| [59](59_protocolo_P3P4_sensibilidade_comparacao.md) | [57h](57h_resultados_P3P4_sensibilidade.md) | Rambachan–Roth e comparação alternativa (P3/P4) |
| [60](60_protocolo_equivalencia_e_oferta_local.md), parte B | [57k](57k_resultados_oferta_local.md) | H4: oferta local depois da chegada |
| [64](64_protocolo_oferta_local_no_corte.md) | [57q](57q_resultados_oferta_local_corte.md) | oferta local comparada no corte |
