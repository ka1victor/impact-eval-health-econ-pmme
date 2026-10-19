# Proveniência de figuras e números — banca 2

> **Regra aplicada:** toda figura e todo número exibido saem de arquivo de
> `output/` gravado por script versionado (`CLAUDE.md`)<br>
> **Conteúdo dos slides:** [02_conteudo_slides.md](02_conteudo_slides.md)<br>
> **Gerador:** [`scripts/apresentacao/gerar_figuras_banca2.py`](../../../scripts/apresentacao/gerar_figuras_banca2.py)<br>
> **Teste:** [`tests/test_conteudo_banca2.py`](../../../tests/test_conteudo_banca2.py)<br>
> **Atualização:** 19 de outubro de 2026

> [!IMPORTANT]
> **Como a conferência funciona.** O bloco da §2 é **gerado** pelo script a
> partir de `output/apresentacao_banca2/numeros_banca2.json`, que por sua vez
> é lido dos arquivos de `output/` pelos seletores declarados no script —
> nenhum valor é digitado. O teste: (1) relê cada arquivo-fonte pelo seletor e
> confere o valor formatado contra o JSON e contra o bloco; (2) confere que
> todo número de cada slide de [02](02_conteudo_slides.md) é o valor de um
> código listado na linha `**Números:**` daquele slide ou um parâmetro da §3;
> (3) confere que todo caminho de figura citado existe e foi produzido por
> script do pipeline, com hash igual ao do manifesto quando a figura é deste
> gerador.

## 1. Figuras

| Código | Figura | Slide | Arquivo | Script gerador | Natureza |
|---|---|:---:|---|---|---|
| `G1` | bolsa anunciada contra o IVS 2010 oficial, ciclo 1 (variante A colorida, doc 38, D1) | 5 | `output/apresentacao_banca2/regra_bolsa_ivs_oficial.png` (vetor: `.svg`) | `scripts/apresentacao/gerar_figuras_banca2.py`, com `fig_regra_pontos` de `scripts/rdd_bolsa/09_gerar_relatorio_pdf.py` via `10_galeria_figura_regra.py` | EMPIRICO |
| `G2` | a mesma figura com o arquivo errado no eixo | 6 | `output/apresentacao_banca2/failure_mode/regra_bolsa_arquivo_errado_FAILURE_MODE.png` (vetor: `.svg`) | idem | **FAILURE_MODE** |
| `G3` | a cadeia em uma figura: um outcome por elo | 10 | `output/apresentacao_banca2/cadeia_sintese_principal.png` | `scripts/apresentacao/gerar_figuras_banca2.py` | EMPIRICO |
| `G4` | índice P1 com ciclos e cortes agrupados (visual) | 11 | `output/rdd_bolsa/E6_figuras/E6_indice_P1_agrupado.png` | `scripts/rdd_bolsa/13_estimar_E6_funil.py` | EMPIRICO |
| `G5` | F1.3 no ciclo 2, por corte | 12 | `output/rdd_bolsa/E6_figuras/E6_F1_3_V2.png` | `scripts/rdd_bolsa/13_estimar_E6_funil.py` | EMPIRICO |
| `G6` | preenchimento: IC convencional contra +10 p.p. | 13 | `output/apresentacao_banca2/descarte_preenchimento.png` | `scripts/apresentacao/gerar_figuras_banca2.py` | EMPIRICO |
| `G7` | utilidade estimada da célula contra o IVS (E9) | 14 | `output/rdd_bolsa/E9_figuras/E9_utilidade_ivs.png` | `scripts/rdd_bolsa/16_estimar_E9_escolha.py` | EMPIRICO |
| `G8` | estudo de evento da DiRD, F3.1 em U | 15 | `output/rdd_bolsa/E7_figuras/E7_evento_F3_1_U.png` | `scripts/rdd_bolsa/14_estimar_E7_dird_cnes.py` | EMPIRICO |
| `G9` | as 23 linhas da tabela-síntese | B1 | `output/apresentacao_banca2/cadeia_sintese_completa.png` | `scripts/apresentacao/gerar_figuras_banca2.py` | EMPIRICO |
| `G10` | F1.3 no ciclo 1, por corte (âncora do E3) | B2 | `output/rdd_bolsa/E6_figuras/E6_F1_3_V1.png` | `scripts/rdd_bolsa/13_estimar_E6_funil.py` | EMPIRICO |
| `G11` | F3.1 em nível, por período e corte | B4 | `output/rdd_bolsa/E7_figuras/E7_nivel_F3_1_U.png` | `scripts/rdd_bolsa/14_estimar_E7_dird_cnes.py` | EMPIRICO |

**Definições.**
- **`G1` e `G2`.** Ciclo 1, chamada 1 (quadro `c1_ch1` de
  `output/rdd_bolsa/matriz_municipio_escore_administrativo.csv`), um ponto por
  município no valor exato da bolsa anunciada, sem deslocamento; cor = IVS do
  eixo, verde → vermelho, com âncoras nos centros das classes do Ipea. Em
  `G1` o eixo é o IVS 2010 oficial (`output/aquisicao/a08_ivs_2010_oficial_municipio.csv`);
  o script para se algum município ficar do lado errado de um corte ou se o
  número de municípios divergir do portão R1. Em `G2` o eixo é
  `data/ivs_ipea_2010_municipios.csv`, que **não é o IVS do município**
  (auditoria 16); a figura só documenta o failure mode, fica na subpasta
  `failure_mode/` e tem natureza `FAILURE_MODE` no manifesto. Os PNG são a
  rasterização dos SVG pelo Chromium headless, em escala 2.
- **`G3` e `G9`.** Lidas de `output/rdd_bolsa/E8_tabela_sintese.csv`. Cada
  linha tem a sua escala, simétrica em torno do nulo (0; 1 na razão de
  chances, em escala log): a figura mostra se o IC contém o nulo, não compara
  tamanhos entre linhas. Azul quando o IC 95% exclui o nulo. O texto de cada
  linha repete a estimativa e o IC da tabela, e a leitura curta vem da coluna
  `leitura` (primária com p Holm; q BKY; robustez do E9).
- **`G6`.** Lida de `output/rdd_bolsa/E8_resumo.json` (`descarte`). Azul
  quando o limite superior do IC convencional fica abaixo da referência do
  protocolo; a leitura à direita diz se isso vale em todas as especificações
  convencionais ou só na principal. O script para se algum IC honesto excluir
  a referência, porque a nota da figura diz que nenhum exclui.
- **`G4`.** O número no título da figura é o salto da reta comum do visual,
  não a estimativa P1; o slide usa a estimativa P1 da tabela.

O manifesto `output/apresentacao_banca2/manifesto_figuras.json` registra, para
cada figura gerada aqui, o SHA-256, a natureza e as fontes, e para cada
entrada o SHA-256, o papel, a data de referência, a cobertura, a unidade e as
chaves.

## 2. Números

Cada número exibido em [02](02_conteudo_slides.md) tem um código. O bloco
abaixo é **gerado** (`python3 scripts/apresentacao/gerar_figuras_banca2.py
--atualizar-doc`); não editar à mão. Três naturezas, em blocos separados no
JSON: `EMPIRICO`; `FAILURE_MODE`, que só documenta o arquivo errado e nunca é
resultado; e `TEXTO_NORMATIVO`/`CITACAO_LITERATURA`, extraídos por expressão
regular do texto-fonte (auditoria 18; trechos do doc 20 copiados pelo E8).

Formatos: `pp1s` = fração multiplicada por cem, uma casa, com sinal (p.p.); `d2s`/`d3s`/`d1s` =
duas, três ou uma casa, com sinal; `d2`/`d3` = sem sinal; `p3` = três casas,
ou "< 0,001"; `pct0`/`pct1` = fração multiplicada por cem (%); `int` = inteiro com separador de
milhar; `fracao` = "a/b" com separador de milhar; `txt` = trecho como está.

<!-- banca2:numeros:inicio -->
| Código | Valor exibido | Natureza | Arquivo | Seletor | Formato | Descrição |
|---|---|---|---|---|---|---|
| `R_ESCORE_IGUAIS` | 404/404 | EMPIRICO | `output/rdd_bolsa/portao_r1_ivs_oficial.json` | `{"caminho": ["escore_administrativo_e_ivs_2010_oficial", "valores_iguais_3_casas"]}` | `fracao` | escore da relação nominal do MS igual ao IVS 2010 oficial, a 3 casas |
| `R_CATEG_IGUAIS` | 5.565/5.565 | EMPIRICO | `output/rdd_bolsa/portao_r1_ivs_oficial.json` | `{"caminho": ["escore_administrativo_e_ivs_2010_oficial", "categorias_iguais"]}` | `fracao` | categoria de IVS do consolidado PMMB igual à classe do IVS oficial |
| `R_C1_MUN` | 368 | EMPIRICO | `output/rdd_bolsa/portao_r1_ivs_oficial.json` | `{"caminho": ["populacoes", "P1", "municipios"]}` | `int` | municípios do ciclo 1 |
| `R_C1_REPR` | 368 | EMPIRICO | `output/rdd_bolsa/portao_r1_ivs_oficial.json` | `{"caminho": ["populacoes", "P1", "regra_reproduz"]}` | `int` | ciclo 1: faixa reproduzida |
| `R_C2_MUN` | 454 | EMPIRICO | `output/rdd_bolsa/portao_r1_ivs_oficial.json` | `{"caminho": ["populacoes", "P2", "municipios"]}` | `int` | municípios do ciclo 2 |
| `R_C2_REPR` | 454 | EMPIRICO | `output/rdd_bolsa/portao_r1_ivs_oficial.json` | `{"caminho": ["populacoes", "P2", "regra_reproduz"]}` | `int` | ciclo 2: faixa reproduzida |
| `R_C3_MUN` | 748 | EMPIRICO | `output/rdd_bolsa/portao_r1_ivs_oficial.json` | `{"caminho": ["populacoes", "ciclo_3_congelado", "municipios"]}` | `int` | municípios do ciclo 3 (congelado) |
| `R_C3_REPR` | 747 | EMPIRICO | `output/rdd_bolsa/portao_r1_ivs_oficial.json` | `{"caminho": ["populacoes", "ciclo_3_congelado", "regra_reproduz"]}` | `int` | ciclo 3: faixa reproduzida (um município criado depois de 2010 sem IVS) |
| `R_LADO_ERRADO_OFICIAL` | 0 | EMPIRICO | calculado por este script | `{"calculado": "lado_errado_oficial"}` | `int` | municípios do ciclo 1 do lado errado do corte com o IVS oficial (figura da regra) |
| `P1_TAU` | −0,13 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["holm", "P1", "tau"]}` | `d2s` | P1: salto (DP) |
| `P1_INF` | −0,44 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["holm", "P1", "ic95_inf"]}` | `d2s` | P1: IC 95% inferior |
| `P1_SUP` | +0,19 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["holm", "P1", "ic95_sup"]}` | `d2s` | P1: IC 95% superior |
| `P1_P` | 0,426 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["holm", "P1", "p_valor"]}` | `p3` | P1: p |
| `P1_HOLM` | 0,851 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["holm", "P1", "p_holm"]}` | `p3` | P1: p Holm |
| `P2_TAU` | +0,083 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["holm", "P2", "tau"]}` | `d3s` | P2: DiRD (vínculos por 10 mil hab.) |
| `P2_INF` | −0,309 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["holm", "P2", "ic95_inf"]}` | `d3s` | P2: IC 95% inferior |
| `P2_SUP` | +0,476 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["holm", "P2", "ic95_sup"]}` | `d3s` | P2: IC 95% superior |
| `P2_P` | 0,677 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["holm", "P2", "p_valor"]}` | `p3` | P2: p |
| `P2_HOLM` | 0,851 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["holm", "P2", "p_holm"]}` | `p3` | P2: p Holm |
| `F11_EST` | +0,063 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F1.1", "populacao": "V1+V2+V3", "ciclo": "1+2+3"}, "coluna": "estimativa"}` | `d3s` | F1.1 candidatos de 1ª opção por célula |
| `F11_INF` | −0,511 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F1.1", "populacao": "V1+V2+V3", "ciclo": "1+2+3"}, "coluna": "ic95_inf"}` | `d3s` | F1.1 IC inferior |
| `F11_SUP` | +0,636 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F1.1", "populacao": "V1+V2+V3", "ciclo": "1+2+3"}, "coluna": "ic95_sup"}` | `d3s` | F1.1 IC superior |
| `F12_EST` | −7,0 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F1.2", "populacao": "V1+V2+V3", "ciclo": "1+2+3"}, "coluna": "estimativa"}` | `pp1s` | F1.2 fração de células com candidato |
| `F12_INF` | −18,9 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F1.2", "populacao": "V1+V2+V3", "ciclo": "1+2+3"}, "coluna": "ic95_inf"}` | `pp1s` | F1.2 IC inferior |
| `F12_SUP` | +4,9 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F1.2", "populacao": "V1+V2+V3", "ciclo": "1+2+3"}, "coluna": "ic95_sup"}` | `pp1s` | F1.2 IC superior |
| `F13_EST` | −7,3 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F1.3", "populacao": "V1+V2+V3", "ciclo": "1+2+3"}, "coluna": "estimativa"}` | `pp1s` | F1.3 preenchidas na 1ª chamada |
| `F13_INF` | −17,9 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F1.3", "populacao": "V1+V2+V3", "ciclo": "1+2+3"}, "coluna": "ic95_inf"}` | `pp1s` | F1.3 IC inferior |
| `F13_SUP` | +3,4 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F1.3", "populacao": "V1+V2+V3", "ciclo": "1+2+3"}, "coluna": "ic95_sup"}` | `pp1s` | F1.3 IC superior |
| `F13_Q` | 1,000 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F1.3", "populacao": "V1+V2+V3", "ciclo": "1+2+3"}, "coluna": "q_bky"}` | `d3` | F1.3 q BKY |
| `F14_EST` | −8,0 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F1.4", "populacao": "V1+V2", "ciclo": "1+2"}, "coluna": "estimativa"}` | `pp1s` | F1.4 preenchidas até a 2ª chamada |
| `F14_INF` | −23,6 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F1.4", "populacao": "V1+V2", "ciclo": "1+2"}, "coluna": "ic95_inf"}` | `pp1s` | F1.4 IC inferior |
| `F14_SUP` | +7,6 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F1.4", "populacao": "V1+V2", "ciclo": "1+2"}, "coluna": "ic95_sup"}` | `pp1s` | F1.4 IC superior |
| `F11_Q` | 1,000 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F1.1", "populacao": "V1+V2+V3", "ciclo": "1+2+3"}, "coluna": "q_bky"}` | `d3` | F1.1 q BKY |
| `F12_Q` | 1,000 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F1.2", "populacao": "V1+V2+V3", "ciclo": "1+2+3"}, "coluna": "q_bky"}` | `d3` | F1.2 q BKY |
| `F14_Q` | 1,000 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F1.4", "populacao": "V1+V2", "ciclo": "1+2"}, "coluna": "q_bky"}` | `d3` | F1.4 q BKY |
| `D_F13_MAXCONV` | +7,8 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["descarte", "preenchimento"], "filtro": {"outcome_id": "F1.3", "populacao": "V1+V2+V3"}, "campo": "maior_ic95_sup_convencional"}` | `pp1s` | F1.3 empilhado: maior limite superior entre as especificações convencionais |
| `D_F13_NCONV` | 6 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["descarte", "preenchimento"], "filtro": {"outcome_id": "F1.3", "populacao": "V1+V2+V3"}, "campo": "n_especificacoes_convencionais"}` | `int` | F1.3 empilhado: número de especificações convencionais |
| `D_F14_MAXCONV` | +12,0 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["descarte", "preenchimento"], "filtro": {"outcome_id": "F1.4", "populacao": "V1+V2"}, "campo": "maior_ic95_sup_convencional"}` | `pp1s` | F1.4 empilhado: maior limite superior convencional |
| `D_F13_V1_SUP` | +14,0 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["descarte", "preenchimento"], "filtro": {"outcome_id": "F1.3", "populacao": "V1"}, "campo": "ic95_sup"}` | `pp1s` | F1.3 ciclo 1: IC superior |
| `D_F13_V2_SUP` | +14,1 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["descarte", "preenchimento"], "filtro": {"outcome_id": "F1.3", "populacao": "V2"}, "campo": "ic95_sup"}` | `pp1s` | F1.3 ciclo 2: IC superior |
| `D_F13_V3_SUP` | +4,7 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["descarte", "preenchimento"], "filtro": {"outcome_id": "F1.3", "populacao": "V3"}, "campo": "ic95_sup"}` | `pp1s` | F1.3 ciclo 3: IC superior |
| `E3_300_TAU` | −12,8 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["descarte", "ancora_E3_ciclo1"], "filtro": {"corte": "0.300"}, "campo": "tau"}` | `pp1s` | E3 âncora 0,300: salto |
| `E3_300_INF` | −45,5 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["descarte", "ancora_E3_ciclo1"], "filtro": {"corte": "0.300"}, "campo": "ic95_inf"}` | `pp1s` | E3 âncora 0,300: IC inferior |
| `E3_300_SUP` | +19,8 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["descarte", "ancora_E3_ciclo1"], "filtro": {"corte": "0.300"}, "campo": "ic95_sup"}` | `pp1s` | E3 âncora 0,300: IC superior |
| `E3_300_MDE` | 46,6 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["descarte", "ancora_E3_ciclo1"], "filtro": {"corte": "0.300"}, "campo": "mde_80"}` | `pp1` | E3 âncora 0,300: MDE de 80% (E5) |
| `E3_400_TAU` | −5,1 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["descarte", "ancora_E3_ciclo1"], "filtro": {"corte": "0.400"}, "campo": "tau"}` | `pp1s` | E3 âncora 0,400: salto |
| `E3_400_INF` | −36,5 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["descarte", "ancora_E3_ciclo1"], "filtro": {"corte": "0.400"}, "campo": "ic95_inf"}` | `pp1s` | E3 âncora 0,400: IC inferior |
| `E3_400_SUP` | +26,2 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["descarte", "ancora_E3_ciclo1"], "filtro": {"corte": "0.400"}, "campo": "ic95_sup"}` | `pp1s` | E3 âncora 0,400: IC superior |
| `E3_400_MDE` | 44,8 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["descarte", "ancora_E3_ciclo1"], "filtro": {"corte": "0.400"}, "campo": "mde_80"}` | `pp1` | E3 âncora 0,400: MDE de 80% (E5) |
| `E3_300_NABX` | 61 | EMPIRICO | `output/rdd_bolsa/E3_estimativas.csv` | `{"filtro": {"populacao": "P1", "outcome": "fracao_celulas_ch1_com_confirmacao_ou_homologacao", "especificacao": "principal", "corte": "0.3"}, "coluna": "n_abaixo"}` | `int` | E3 0,300: municípios abaixo do corte (h = 0,050) |
| `E3_300_NACI` | 53 | EMPIRICO | `output/rdd_bolsa/E3_estimativas.csv` | `{"filtro": {"populacao": "P1", "outcome": "fracao_celulas_ch1_com_confirmacao_ou_homologacao", "especificacao": "principal", "corte": "0.3"}, "coluna": "n_acima"}` | `int` | E3 0,300: municípios acima do corte |
| `E3_400_NABX` | 53 | EMPIRICO | `output/rdd_bolsa/E3_estimativas.csv` | `{"filtro": {"populacao": "P1", "outcome": "fracao_celulas_ch1_com_confirmacao_ou_homologacao", "especificacao": "principal", "corte": "0.4"}, "coluna": "n_abaixo"}` | `int` | E3 0,400: municípios abaixo do corte |
| `E3_400_NACI` | 41 | EMPIRICO | `output/rdd_bolsa/E3_estimativas.csv` | `{"filtro": {"populacao": "P1", "outcome": "fracao_celulas_ch1_com_confirmacao_ou_homologacao", "especificacao": "principal", "corte": "0.4"}, "coluna": "n_acima"}` | `int` | E3 0,400: municípios acima do corte |
| `E9_C1_RC` | 1,39 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e9", "principal", "1", "rc_5mil"]}` | `d2` | E9 ciclo 1: razão de chances por +R$ 5 mil |
| `E9_C1_RCI` | 0,90 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e9", "principal", "1", "rc_5mil_ic95", 0]}` | `d2` | E9 ciclo 1: IC inferior |
| `E9_C1_RCS` | 2,13 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e9", "principal", "1", "rc_5mil_ic95", 1]}` | `d2` | E9 ciclo 1: IC superior |
| `E9_C1_P` | 0,137 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e9", "principal", "1", "p"]}` | `p3` | E9 ciclo 1: p |
| `E9_C2_RC` | 1,95 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e9", "principal", "2", "rc_5mil"]}` | `d2` | E9 ciclo 2: razão de chances |
| `E9_C2_RCI` | 1,48 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e9", "principal", "2", "rc_5mil_ic95", 0]}` | `d2` | E9 ciclo 2: IC inferior |
| `E9_C2_RCS` | 2,57 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e9", "principal", "2", "rc_5mil_ic95", 1]}` | `d2` | E9 ciclo 2: IC superior |
| `E9_C2_P` | < 0,001 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e9", "principal", "2", "p"]}` | `p3` | E9 ciclo 2: p |
| `E9_C3_RC` | 1,05 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e9", "principal", "3", "rc_5mil"]}` | `d2` | E9 ciclo 3: razão de chances |
| `E9_C3_RCI` | 0,77 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e9", "principal", "3", "rc_5mil_ic95", 0]}` | `d2` | E9 ciclo 3: IC inferior |
| `E9_C3_RCS` | 1,43 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e9", "principal", "3", "rc_5mil_ic95", 1]}` | `d2` | E9 ciclo 3: IC superior |
| `E9_C3_P` | 0,761 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e9", "principal", "3", "p"]}` | `p3` | E9 ciclo 3: p |
| `E9_EMP_RC` | 1,39 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e9", "principal", "empilhado", "rc_5mil"]}` | `d2` | E9 empilhado: razão de chances |
| `E9_EMP_RCI` | 1,12 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e9", "principal", "empilhado", "rc_5mil_ic95", 0]}` | `d2` | E9 empilhado: IC inferior |
| `E9_EMP_RCS` | 1,73 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e9", "principal", "empilhado", "rc_5mil_ic95", 1]}` | `d2` | E9 empilhado: IC superior |
| `E9_EMP_P` | 0,003 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e9", "principal", "empilhado", "p"]}` | `p3` | E9 empilhado: p |
| `E9_EMP_N` | 5.714 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e9", "principal", "empilhado", "n_candidatos"]}` | `int` | E9 empilhado: candidatos de 1ª opção |
| `E9_C2_NPLAC` | 27 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e9", "ciclo2", "placebo", "n_placebos"]}` | `int` | E9: cortes placebo |
| `E9_C2_PLAC_GE` | 0 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e9", "ciclo2", "placebo", "n_abs_t_placebo_ge_real"]}` | `int` | E9 ciclo 2: placebos com |t| ≥ t real |
| `E9_C2_PPOSTO` | 0,036 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e9", "ciclo2", "placebo", "p_posto"]}` | `p3` | E9 ciclo 2: p por posto |
| `E9_C2_WEBB` | 0,002 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e9", "ciclo2", "p_score_webb"]}` | `p3` | E9 ciclo 2: p do score bootstrap (Webb) |
| `E9_C2_CV3` | < 0,001 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e9", "ciclo2", "p_cv3"]}` | `p3` | E9 ciclo 2: p do CV3 |
| `E9_C2_CUB_P` | 0,083 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e9", "ciclo2", "spline_cubico", "p"]}` | `p3` | E9 ciclo 2: p com spline cúbico |
| `E9_PLAC_FRAC` | 14,8 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e9", "empilhado", "placebo", "fracao_abs_t_maior_1_96"]}` | `pct1` | E9 empilhado: fração de cortes placebo com |t| > 1,96 (%) |
| `E9_C2_PLAC_FRAC` | 14,8 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e9", "ciclo2", "placebo", "fracao_abs_t_maior_1_96"]}` | `pct1` | E9 ciclo 2: fração de cortes placebo com |t| > 1,96 (%) |
| `E9_EMP_PLAC_GE` | 2 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e9", "empilhado", "placebo", "n_abs_t_placebo_ge_real"]}` | `int` | E9 empilhado: placebos com |t| ≥ t real |
| `E9_EMP_PPOSTO` | 0,107 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e9", "empilhado", "placebo", "p_posto"]}` | `p3` | E9 empilhado: p por posto |
| `E9_EMP_SEM2_P` | 0,267 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e9", "empilhado", "ciclos_1_e_3", "p"]}` | `p3` | E9 ciclos 1 e 3 empilhados, sem o 2: p |
| `E9_EMP_Q_P` | 0,014 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e9", "empilhado", "cochran_Q", "p"]}` | `p3` | E9: p do Q de Cochran |
| `E9_EMP_CUB_P` | 0,220 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e9", "empilhado", "spline_cubico", "p"]}` | `p3` | E9 empilhado: p com spline cúbico |
| `E9_CURSO_WEBB` | 0,047 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e9", "empilhado", "cluster_curso", "p_score_webb"]}` | `p3` | E9 empilhado: p do score (Webb) com cluster por curso |
| `F21_EST` | −0,136 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F2.1", "populacao": "V1+V2", "ciclo": "1+2"}, "coluna": "estimativa"}` | `d3s` | F2.1 especialistas ativos por célula |
| `F21_INF` | −0,491 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F2.1", "populacao": "V1+V2", "ciclo": "1+2"}, "coluna": "ic95_inf"}` | `d3s` | F2.1 IC inferior |
| `F21_SUP` | +0,218 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F2.1", "populacao": "V1+V2", "ciclo": "1+2"}, "coluna": "ic95_sup"}` | `d3s` | F2.1 IC superior |
| `F23_EST` | −5,2 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F2.3", "populacao": "V1+V2", "ciclo": "1+2"}, "coluna": "estimativa"}` | `pp1s` | F2.3 algum especialista ativo |
| `F23_INF` | −25,0 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F2.3", "populacao": "V1+V2", "ciclo": "1+2"}, "coluna": "ic95_inf"}` | `pp1s` | F2.3 IC inferior |
| `F23_SUP` | +14,7 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F2.3", "populacao": "V1+V2", "ciclo": "1+2"}, "coluna": "ic95_sup"}` | `pp1s` | F2.3 IC superior |
| `F32_EST` | −2,5 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F3.2", "populacao": "U", "ciclo": "pós 2025-10..2026-08"}, "coluna": "estimativa"}` | `pp1s` | F3.2 município com especialista nas CBO-alvo |
| `F32_INF` | −5,9 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F3.2", "populacao": "U", "ciclo": "pós 2025-10..2026-08"}, "coluna": "ic95_inf"}` | `pp1s` | F3.2 IC inferior |
| `F32_SUP` | +1,0 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F3.2", "populacao": "U", "ciclo": "pós 2025-10..2026-08"}, "coluna": "ic95_sup"}` | `pp1s` | F3.2 IC superior |
| `F33_EST` | −2,0 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F3.3", "populacao": "U", "ciclo": "pós 2025-10..2026-08"}, "coluna": "estimativa"}` | `d1s` | F3.3 horas SUS por 10 mil hab. |
| `F33_INF` | −6,4 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F3.3", "populacao": "U", "ciclo": "pós 2025-10..2026-08"}, "coluna": "ic95_inf"}` | `d1s` | F3.3 IC inferior |
| `F33_SUP` | +2,3 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F3.3", "populacao": "U", "ciclo": "pós 2025-10..2026-08"}, "coluna": "ic95_sup"}` | `d1s` | F3.3 IC superior |
| `FP1_EST` | −0,088 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F3.P1", "populacao": "U", "ciclo": "pós 2025-10..2026-08"}, "coluna": "estimativa"}` | `d3s` | placebo: generalistas por 10 mil hab. |
| `FP1_INF` | −1,190 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F3.P1", "populacao": "U", "ciclo": "pós 2025-10..2026-08"}, "coluna": "ic95_inf"}` | `d3s` | placebo generalistas: IC inferior |
| `FP1_SUP` | +1,014 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F3.P1", "populacao": "U", "ciclo": "pós 2025-10..2026-08"}, "coluna": "ic95_sup"}` | `d3s` | placebo generalistas: IC superior |
| `FP2_EST` | −0,059 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F3.P2", "populacao": "U", "ciclo": "pós 2025-10..2026-08"}, "coluna": "estimativa"}` | `d3s` | placebo: especialistas fora das CBO-alvo |
| `FP2_INF` | −0,485 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F3.P2", "populacao": "U", "ciclo": "pós 2025-10..2026-08"}, "coluna": "ic95_inf"}` | `d3s` | placebo fora das CBO-alvo: IC inferior |
| `FP2_SUP` | +0,367 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F3.P2", "populacao": "U", "ciclo": "pós 2025-10..2026-08"}, "coluna": "ic95_sup"}` | `d3s` | placebo fora das CBO-alvo: IC superior |
| `E7_SEQ_N` | 5 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e7", "f31_U_0300", "maior_sequencia_p_menor_005", "n_meses"]}` | `int` | E7 F3.1 U 0,300: meses consecutivos do pós com p < 0,05 |
| `E7_DEPOIS_N` | 6 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e7", "f31_U_0300", "meses_pos_depois_da_sequencia"]}` | `int` | E7: meses do pós depois da sequência |
| `E7_DEPOIS_SIG` | 0 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e7", "f31_U_0300", "meses_pos_depois_da_sequencia_p_menor_005"]}` | `int` | E7: desses, com p < 0,05 |
| `E7_ANTES_N` | 24 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e7", "f31_U_0300", "meses_antes_da_referencia"]}` | `int` | E7: meses antes da referência |
| `E7_ANTES_SIG` | 0 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e7", "f31_U_0300", "meses_antes_da_referencia_p_menor_005"]}` | `int` | E7: desses, com p < 0,05 |
| `E7_PREEXT_TAU` | −1,811 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e7", "f31_U_0300", "nivel_pre_extra", "tau"]}` | `d3s` | E7 F3.1 U 0,300: descontinuidade em nível no pré extra (2022-01..2023-03) |
| `E7_PREEXT_INF` | −3,591 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e7", "f31_U_0300", "nivel_pre_extra", "ic95_inf"]}` | `d3s` | IC inferior |
| `E7_PREEXT_SUP` | −0,030 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e7", "f31_U_0300", "nivel_pre_extra", "ic95_sup"]}` | `d3s` | IC superior |
| `E7_DIRD300_TAU` | +0,287 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e7", "f31_U_0300", "dird_principal", "tau"]}` | `d3s` | E7 F3.1 U 0,300: DiRD principal |
| `E7_DIRD300_INF` | −0,235 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e7", "f31_U_0300", "dird_principal", "ic95_inf"]}` | `d3s` | IC inferior |
| `E7_DIRD300_SUP` | +0,810 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e7", "f31_U_0300", "dird_principal", "ic95_sup"]}` | `d3s` | IC superior |
| `E7_DIRD300_P` | 0,281 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e7", "f31_U_0300", "dird_principal", "p_valor"]}` | `p3` | p |
| `E7_GEN_N` | 7 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e7", "generalistas_U_0400", "pre_extra_meses"]}` | `int` | E7 generalistas U 0,400: meses do pré extra |
| `E7_GEN_SIG` | 2 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e7", "generalistas_U_0400", "pre_extra_p_menor_005"]}` | `int` | E7 generalistas U 0,400: desses, com p < 0,05 |
| `E7_V1_N` | 12 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e7", "v1_0300", "meses_pre_extra_e_entre"]}` | `int` | E7 V1 0,300: meses do pré extra e do trecho até o pré |
| `E7_V1_SIG` | 12 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["e7", "v1_0300", "meses_pre_extra_e_entre_p_menor_005"]}` | `int` | E7 V1 0,300: desses, com p < 0,05 |
| `FAM_F0_N` | 42 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["familias", "F0", "resumo_testes", "linhas_principais_no_bky"]}` | `int` | F0: linhas principais no BKY |
| `FAM_F0_P` | 2 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["familias", "F0", "resumo_testes", "p_menor_005"]}` | `int` | F0: linhas com p < 0,05 |
| `FAM_F0_Q` | 0 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["familias", "F0", "resumo_testes", "q_menor_005"]}` | `int` | F0: linhas com q BKY < 0,05 |
| `FAM_F0_MINQ` | 0,639 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["familias", "F0", "resumo_testes", "menor_q"]}` | `d3` | F0: menor q BKY |
| `FAM_F1_N` | 45 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["familias", "F1", "resumo_testes", "linhas_principais_no_bky"]}` | `int` | F1: linhas principais no BKY |
| `FAM_F1_P` | 0 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["familias", "F1", "resumo_testes", "p_menor_005"]}` | `int` | F1: linhas com p < 0,05 |
| `FAM_F1_Q` | 0 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["familias", "F1", "resumo_testes", "q_menor_005"]}` | `int` | F1: linhas com q BKY < 0,05 |
| `FAM_F1_MINQ` | 1,000 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["familias", "F1", "resumo_testes", "menor_q"]}` | `d3` | F1: menor q BKY |
| `FAM_F2_N` | 24 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["familias", "F2", "resumo_testes", "linhas_principais_no_bky"]}` | `int` | F2: linhas principais no BKY |
| `FAM_F2_P` | 1 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["familias", "F2", "resumo_testes", "p_menor_005"]}` | `int` | F2: linhas com p < 0,05 |
| `FAM_F2_Q` | 0 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["familias", "F2", "resumo_testes", "q_menor_005"]}` | `int` | F2: linhas com q BKY < 0,05 |
| `FAM_F2_MINQ` | 0,828 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["familias", "F2", "resumo_testes", "menor_q"]}` | `d3` | F2: menor q BKY |
| `FAM_F3_N` | 18 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["familias", "F3", "resumo_testes", "linhas_principais_no_bky"]}` | `int` | F3: linhas principais no BKY |
| `FAM_F3_P` | 0 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["familias", "F3", "resumo_testes", "p_menor_005"]}` | `int` | F3: linhas com p < 0,05 |
| `FAM_F3_Q` | 0 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["familias", "F3", "resumo_testes", "q_menor_005"]}` | `int` | F3: linhas com q BKY < 0,05 |
| `FAM_F3_MINQ` | 1,000 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["familias", "F3", "resumo_testes", "menor_q"]}` | `d3` | F3: menor q BKY |
| `FAM_F4_N` | 24 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["familias", "F4", "resumo_testes", "linhas_principais_no_bky"]}` | `int` | F4: linhas principais no BKY |
| `FAM_F4_P` | 2 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["familias", "F4", "resumo_testes", "p_menor_005"]}` | `int` | F4: linhas com p < 0,05 |
| `FAM_F4_Q` | 0 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["familias", "F4", "resumo_testes", "q_menor_005"]}` | `int` | F4: linhas com q BKY < 0,05 |
| `FAM_F4_MINQ` | 0,830 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["familias", "F4", "resumo_testes", "menor_q"]}` | `d3` | F4: menor q BKY |
| `F02_EST` | −0,035 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F0.2", "populacao": "U", "ciclo": "1"}, "coluna": "estimativa"}` | `d3s` | F0.2 vagas imediatas por 10 mil hab., ciclo 1 |
| `F02_INF` | −0,065 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F0.2", "populacao": "U", "ciclo": "1"}, "coluna": "ic95_inf"}` | `d3s` | F0.2 IC inferior |
| `F02_SUP` | −0,006 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F0.2", "populacao": "U", "ciclo": "1"}, "coluna": "ic95_sup"}` | `d3s` | F0.2 IC superior |
| `F02_Q` | 0,639 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F0.2", "populacao": "U", "ciclo": "1"}, "coluna": "q_bky"}` | `d3` | F0.2 q BKY |
| `F41_EST` | −0,396 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F4.1", "populacao": "V1+V2+V3", "ciclo": "1+2+3"}, "coluna": "estimativa"}` | `d3s` | F4.1 nota média dos alocados |
| `F41_INF` | −0,939 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F4.1", "populacao": "V1+V2+V3", "ciclo": "1+2+3"}, "coluna": "ic95_inf"}` | `d3s` | F4.1 IC inferior |
| `F41_SUP` | +0,147 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F4.1", "populacao": "V1+V2+V3", "ciclo": "1+2+3"}, "coluna": "ic95_sup"}` | `d3s` | F4.1 IC superior |
| `F42_EST` | −0,453 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F4.2", "populacao": "V1+V2+V3", "ciclo": "1+2+3"}, "coluna": "estimativa"}` | `d3s` | F4.2 nota média dos candidatos de 1ª opção |
| `F42_INF` | −0,873 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F4.2", "populacao": "V1+V2+V3", "ciclo": "1+2+3"}, "coluna": "ic95_inf"}` | `d3s` | F4.2 IC inferior |
| `F42_SUP` | −0,033 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F4.2", "populacao": "V1+V2+V3", "ciclo": "1+2+3"}, "coluna": "ic95_sup"}` | `d3s` | F4.2 IC superior |
| `F42_P` | 0,035 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F4.2", "populacao": "V1+V2+V3", "ciclo": "1+2+3"}, "coluna": "p_valor"}` | `p3` | F4.2 p |
| `F42_Q` | 0,830 | EMPIRICO | `output/rdd_bolsa/E8_tabela_sintese.csv` | `{"filtro": {"outcome_id": "F4.2", "populacao": "V1+V2+V3", "ciclo": "1+2+3"}, "coluna": "q_bky"}` | `d3` | F4.2 q BKY |
| `SEL_DENS` | 0,61 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["selecao_v1_0400", "densidade_V1_0400", "razao"]}` | `d2` | V1 0,400: razão de densidades |
| `SEL_DENS_INF` | 0,29 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["selecao_v1_0400", "densidade_V1_0400", "ic95", 0]}` | `d2` | IC inferior |
| `SEL_DENS_SUP` | 1,30 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["selecao_v1_0400", "densidade_V1_0400", "ic95", 1]}` | `d2` | IC superior |
| `SEL_BAL_P` | 3 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["selecao_v1_0400", "balanco_V1_0400", "p_menor_005"]}` | `int` | V1 0,400: covariáveis com p < 0,05 |
| `SEL_BAL_N` | 13 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["selecao_v1_0400", "balanco_V1_0400", "covariaveis_testadas"]}` | `int` | V1 0,400: covariáveis testadas |
| `SEL_PESO` | 12,3 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["selecao_v1_0400", "peso_c1_400_no_P1"]}` | `pct1` | peso do grupo ciclo 1 × 0,400 no P1 empilhado (%) |
| `E8_LINHAS` | 23 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["saidas", "E8_tabela_sintese.csv", "linhas"]}` | `int` | linhas principais da tabela-síntese do E8 |
| `MAG_DEG300` | +50 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["degrau_relativo_bolsa", "0.300", "relativo"]}` | `pct0s` | degrau relativo da bolsa em 0,300 (%) |
| `MAG_DEG400` | +33 | EMPIRICO | `output/rdd_bolsa/E8_resumo.json` | `{"caminho": ["degrau_relativo_bolsa", "0.400", "relativo"]}` | `pct0s` | degrau relativo da bolsa em 0,400 (%) |
| `FM_NMU` | 4.362 | FAILURE_MODE | `output/rdd_bolsa/identificacao_arquivo_local_ivs.json` | `{"caminho": ["mecanismo", "linha_escolhida_por_municipio", "Negro / Mulher / Urbano"]}` | `int` | municípios em que o arquivo errado traz a linha Negro / Mulher / Urbano |
| `FM_MUN` | 5.565 | FAILURE_MODE | `output/rdd_bolsa/identificacao_arquivo_local_ivs.json` | `{"caminho": ["mecanismo", "conferencia_por_coluna", "municipios"]}` | `int` | municípios do arquivo |
| `FM_NMU_PCT` | 78 | FAILURE_MODE | calculado por este script | `{"razao": ["FM_NMU", "FM_MUN"]}` | `pct0` | FM_NMU / FM_MUN (%) |
| `FM_IGUAIS` | 38 | FAILURE_MODE | `output/tema_trabalho/failure_mode_ivs_resumo.json` | `{"caminho": ["arquivo_errado", "ivs_igual_3_casas"]}` | `int` | municípios em que o arquivo errado acerta o IVS oficial a 3 casas |
| `FM_CORR` | 0,85 | FAILURE_MODE | `output/tema_trabalho/failure_mode_ivs_resumo.json` | `{"caminho": ["arquivo_errado", "correlacao_ivs"]}` | `d2` | correlação entre o arquivo errado e o IVS oficial |
| `FM_LADO_ERRADO` | 101 | FAILURE_MODE | calculado por este script | `{"calculado": "lado_errado_arquivo_errado"}` | `int` | municípios do ciclo 1 do lado errado do corte com o arquivo errado no eixo |
| `CP_EMENDAS` | +20% | TEXTO_NORMATIVO | `docs/auditorias/18_politicas_nos_mesmos_cortes_ivs.md` | `{"regex": "parcelas PAP e MAC (\\+\\d+%)"}` | `txt` | acréscimo no teto de emendas e parcelas de custeio para IVS > 0,3 |
| `CP_752_300` | 10% → 40% | TEXTO_NORMATIVO | `docs/auditorias/18_politicas_nos_mesmos_cortes_ivs.md` | `{"regex": "\\((\\d+% → \\d+%) de teto de coparticipação"}` | `txt` | Portaria 752/2023: teto de coparticipação do PMMB em 0,3 |
| `CP_752_400` | 40% → 100% | TEXTO_NORMATIVO | `docs/auditorias/18_politicas_nos_mesmos_cortes_ivs.md` | `{"regex": "texto da 752 \\((\\d+% → \\d+%)\\)"}` | `txt` | Portaria 752/2023: teto de coparticipação do PMMB em 0,4 |
| `CP_IED_300` | 2 e 3 | TEXTO_NORMATIVO | `docs/auditorias/18_politicas_nos_mesmos_cortes_ivs.md` | `{"regex": "estrato IED da APS nos portes (\\d e \\d)"}` | `txt` | IED da APS: portes em que o estrato muda em 0,300 |
| `CP_IED_400` | 1, 2 e 4 | TEXTO_NORMATIVO | `docs/auditorias/18_politicas_nos_mesmos_cortes_ivs.md` | `{"regex": "estrato IED nos portes (\\d, \\d e \\d)"}` | `txt` | IED da APS: portes em que o estrato muda em 0,400 |
| `LIT_DALBO_SAL` | +33% | CITACAO_LITERATURA | `output/rdd_bolsa/E8_resumo.json` | `{"regex": "salário anunciado sorteado \\((\\+\\d+%)\\)"}` | `txt` | Dal Bó, Finan e Rossi (2013): aumento sorteado do salário anunciado |
| `LIT_DALBO_ACEIT` | +15,1 | CITACAO_LITERATURA | `output/rdd_bolsa/E8_resumo.json` | `{"regex": "aceitação (\\+\\d+,\\d) p\\.p\\."}` | `txt` | Dal Bó, Finan e Rossi (2013): efeito na aceitação (p.p.) |
| `LIT_DALBO_CAND` | +26% | CITACAO_LITERATURA | `output/rdd_bolsa/E8_resumo.json` | `{"regex": "candidaturas \\*\\*(\\+\\d+%)\\*\\*"}` | `txt` | Dal Bó, Finan e Rossi (2013): efeito nas candidaturas |
| `LIT_BOBBA` | +13% | CITACAO_LITERATURA | `output/rdd_bolsa/E8_resumo.json` | `{"regex": "define adicional de (\\+\\d+%)"}` | `txt` | Bobba et al.: adicional por regra |
<!-- banca2:numeros:fim -->

## 3. Parâmetros que podem aparecer sem código

Não são resultados; são parâmetros do protocolo ou da regra, ou partes de
datas e nomes:

| Parâmetro | Onde está fixado |
|---|---|
| cortes 0,300 e 0,400 (e 0,3 e 0,4 no texto dos atos) | regra da bolsa; protocolo 40, §3 |
| h = 0,050; sensibilidades 0,030 e 0,080 | protocolo 40, §6 |
| bolsas de R$ 10, 15 e 20 mil; degrau de R$ 5 mil | editais; protocolo 40, §3 |
| referências +10 p.p. e +25% | protocolo 40, §7 |
| IC 95%, α = 0,05, valor crítico 1,96, limiar p < 0,001, MDE de 80% | convenções de relato |
| ciclos 1, 2 e 3; chamadas 1ª e 2ª | desenho |
| anos, datas, competências (`2025-10`, `202703`), números de atos (`752/2023`), seções (§), documentos e códigos de outcome (F1.3, V1, E9) | nomes, não números |

## 4. Entradas lidas pelo gerador

Com SHA-256 no manifesto. O arquivo errado é lido **só** para `G2` e para o
código `FM_LADO_ERRADO`.

| Arquivo | Papel |
|---|---|
| `output/rdd_bolsa/E8_resumo.json` | síntese E8: Holm, descarte, E9, E7, seleção, famílias, degrau, literatura |
| `output/rdd_bolsa/E8_tabela_sintese.csv` | tabela-síntese por elo |
| `output/rdd_bolsa/E3_estimativas.csv` | municípios por lado na âncora do E3 |
| `output/rdd_bolsa/portao_r1_ivs_oficial.json` | reprodução da regra com o IVS oficial |
| `output/rdd_bolsa/identificacao_arquivo_local_ivs.json` | mecanismo do arquivo errado (só failure mode) |
| `output/tema_trabalho/failure_mode_ivs_resumo.json` | registro do failure mode (auditoria 19) |
| `output/rdd_bolsa/matriz_municipio_escore_administrativo.csv` | faixa anunciada por município |
| `output/aquisicao/a08_ivs_2010_oficial_municipio.csv` | running variable |
| `data/ivs_ipea_2010_municipios.csv` | **só failure mode** |
| `docs/auditorias/18_politicas_nos_mesmos_cortes_ivs.md` | parâmetros normativos das co-políticas |
| `scripts/rdd_bolsa/10_galeria_figura_regra.py` | código da variante A colorida |

## 5. Pendências e ressalvas

1. **`run_all.py`.** O gerador não está no pipeline ponta a ponta; a inclusão
   fica para o coordenador.
2. **Decisões do autor.** Os slides 1, 20 e 21 dependem da revisão da
   hipótese e da mensagem principal; nenhum número depende delas.
3. **PNG da regra.** Depende do Chromium headless; sem ele o script grava só o
   SVG e registra `png_gerado: false` no manifesto.
4. **Texto citado.** Os números de atos e de literatura são conferidos pela
   presença do trecho no texto-fonte, não contra o ato ou o artigo originais;
   a conferência desses está na auditoria 18 e no doc 20 da seção 03.

## 6. Reprodução

```bash
python3 scripts/apresentacao/gerar_figuras_banca2.py
python3 -m unittest tests.test_conteudo_banca2
```
