# Proveniência de figuras e números — banca 2

> **Regra aplicada:** toda figura e todo número exibido saem de arquivo de
> `output/` gravado por script versionado (`CLAUDE.md`)<br>
> **Conteúdo dos slides:** [02_conteudo_slides.md](02_conteudo_slides.md)<br>
> **Geradores:** [`scripts/apresentacao/gerar_figuras_banca2.py`](../../../scripts/apresentacao/gerar_figuras_banca2.py)
> (figuras, tabelas e números) e [`scripts/apresentacao/gerar_deck_banca2.py`](../../../scripts/apresentacao/gerar_deck_banca2.py)
> (deck)<br>
> **Teste:** [`tests/test_conteudo_banca2.py`](../../../tests/test_conteudo_banca2.py)<br>
> **Atualização:** 26 de outubro de 2026 (H3 com o P1h auditado)

> [!IMPORTANT]
> **Como a conferência funciona.** O bloco da §2 é **gerado** pelo script a
> partir de `output/apresentacao_banca2/numeros_banca2.json`, que por sua vez
> é lido dos arquivos de `output/` pelos seletores declarados no script —
> nenhum valor é digitado. O teste: (1) relê cada arquivo-fonte pelo seletor e
> confere o valor formatado contra o JSON e contra o bloco; (2) confere que
> todo número de cada slide de [02](02_conteudo_slides.md) é o valor de um
> código listado na linha `**Números:**` daquele slide ou um parâmetro da §3;
> (3) confere que todo número desenhado dentro das figuras novas é o valor de
> um código ou um parâmetro; (4) confere que todo caminho de figura citado
> existe e foi produzido por script do pipeline, com hash igual ao do
> manifesto; (5) confere que o texto dos slides novos do deck é o do doc 02 e
> que todo número do deck vem do registro.

## 1. Figuras e tabelas

| Código | Figura | Slide (doc 02) | Arquivo | Script gerador | Natureza |
|---|---|---|---|---|---|
| `G1` | bolsa anunciada contra o IVS 2010 oficial, ciclo 1 (variante A colorida, doc 38, D1) | A bolsa é função exata do IVS | `output/apresentacao_banca2/regra_bolsa_ivs_oficial.png` (vetor: `.svg`) | `scripts/apresentacao/gerar_figuras_banca2.py`, com `fig_regra_pontos` via `scripts/rdd_bolsa/10_galeria_figura_regra.py` | EMPIRICO |
| `G2` | H1: N1 com e sem controle e A3 empilhado e por corte, com "Como ler" | H1 | `output/apresentacao_banca2/h1_preenchimento.png` | `scripts/apresentacao/gerar_figuras_banca2.py` | EMPIRICO |
| `G3` | H2: razão de chances da 1ª opção (M1, M5 por ciclo, E9 ciclo 2), com "Como ler" | H2 | `output/apresentacao_banca2/h2_escolha.png` | idem | EMPIRICO |
| `G4` | H4: horas do médico (P4) e comparação na nota de corte (P4-CA), com "Como ler" | H4 | `output/apresentacao_banca2/h4_horas_medico.png` | idem | EMPIRICO |
| `G5` | cadeia-resumo com as linhas do doc 57 (N1, A3, P1 M1, P4, P6, K1, realocação), a da H3 (P1h, D_UF) e a força da evidência | Na cadeia | `output/apresentacao_banca2/cadeia_resumo_doc57.png` | idem | EMPIRICO |
| `G12` | H3: pesos na utilidade da escolha (M1), na mesma escala, com os rótulos corrigidos pela auditoria 31 | H3 | `output/rdd_bolsa/P1h_figuras/P1h_magnitudes.png` | `scripts/rdd_bolsa/25c_magnitudes_P1h.py` (não é redesenhada aqui) | EMPIRICO |
| `G6` | tabela descritiva por ciclo | (no deck, tabela nativa) | `output/apresentacao_banca2/tabela_descritiva_ciclos.png` e `.csv` | idem | EMPIRICO |
| `G7` | tabela de fontes | (no deck, tabela nativa) | `output/apresentacao_banca2/tabela_fontes.png` e `.csv` | idem | EMPIRICO |
| `G8` | a figura da regra com o arquivo de IVS errado no eixo | fora do deck | `output/apresentacao_banca2/failure_mode/regra_bolsa_arquivo_errado_FAILURE_MODE.png` | gravada em 19/10/2026 pela versão anterior do gerador; **não regenerada** | **FAILURE_MODE** |
| `G9` | as linhas da tabela-síntese do E8 (rascunho de 19/10) | fora do deck | `output/apresentacao_banca2/cadeia_sintese_completa.png` | `scripts/apresentacao/gerar_figuras_banca2.py` | EMPIRICO |
| `G10` | um outcome por elo do E8 (rascunho de 19/10) | fora do deck | `output/apresentacao_banca2/cadeia_sintese_principal.png` | idem | EMPIRICO |
| `G11` | preenchimento: IC convencional contra +10 p.p. (rascunho de 19/10) | fora do deck | `output/apresentacao_banca2/descarte_preenchimento.png` | idem | EMPIRICO |

**Definições.**
- **`G1`.** Ciclo 1, chamada 1 (quadro `c1_ch1` de
  `output/rdd_bolsa/matriz_municipio_escore_administrativo.csv`), um ponto por
  município no valor exato da bolsa anunciada; eixo = IVS 2010 oficial
  (`output/aquisicao/a08_ivs_2010_oficial_municipio.csv`). O script para se
  algum município ficar do lado errado de um corte ou se o número de
  municípios divergir do portão R1. A leitura dos dados agora é feita no
  próprio gerador (`dados_regra`), sem a função da galeria que também lia o
  arquivo de IVS errado; o PNG regenerado tem o mesmo SHA-256 de antes.
- **`G2`, `G3` e `G4`.** Um painel por outcome; em cada linha, o rótulo em
  cima e o intervalo de 95% embaixo, com o valor à direita. Verde: o IC exclui
  o nulo; cinza: contém. A linha preta é o nulo; a tracejada laranja, a
  referência de +10 p.p. do protocolo. O bloco "Como ler" fica na própria
  imagem: foi a lição do grupo, que achou incompreensíveis os gráficos de
  descontinuidade com faixas e pontos sem explicação. Todo texto desenhado é
  gravado no manifesto (`figuras_novas`), e o teste confere os números.
- **`G5`.** Uma linha por pergunta do doc 57, cada uma na sua escala,
  simétrica em torno do nulo. A "força da evidência" de cada **linha** sai de
  uma regra explícita do gerador (`forca_da_linha`) aplicada a valores
  registrados: p de Holm ≥ 0,05, ou IC com o nulo, dá "inconclusivo"; o p do
  Wald do pré ≥ 0,05 dá "ATT sob tendências paralelas" (abaixo, "ATT com pré
  falhando"); o estatuto EXPLORATORIO do bloco dá "exploratório". A regra e as
  entradas de cada linha ficam no manifesto (`forca_regra`). Ela é por linha:
  o doc 57 classifica a pergunta inteira, e no P4 outros outcomes falham no
  pré, o que a leitura curta da linha diz. Na linha da H3, a regra do Holm
  recebe também o estatuto do bloco: Holm < 0,05 num bloco cujo estatuto
  termina em `POS_RESULTADO` dá "rejeita zero, pós-resultado".
- **`G12`.** É a figura do P1h, usada sem redesenho para não reabrir o que a
  auditoria 31 corrigiu (A1: "no modelo de escolha", com a vaga como sujeito;
  A2: θ_UF é "mesma UF, outra região de saúde", contra outra UF à mesma
  distância). O gerador de figuras confere, antes de registrar os números,
  que o SHA-256 dela e o do `P1h_magnitudes.csv` são os gravados em
  `P1h_resumo.json` e que tudo tem natureza EMPIRICO; o teste confere o mesmo.
  O "Como ler" dela está no resumo do P1h e no doc 57i, não na imagem.
- **`G6` e `G7`.** As descritivas são contadas pelo gerador no quadro de
  células da 1ª chamada (`output/rdd_bolsa/outcomes/outcomes_V_celula.parquet`)
  e no resumo do portão G1. A faixa é a da **grade aplicada** (cortes 0,300 e
  0,400 no IVS 2010 oficial); o script para se ela divergir da faixa publicada
  em alguma célula com IVS. No deck, as duas tabelas entram como tabela nativa,
  com o texto do doc 02, que o teste confere contra os CSVs.
- **`G8`.** Não é regenerada: refazê-la exigiria ler o arquivo de IVS errado,
  e a contagem desenhada nela não tem mais código no registro. Fica em
  `failure_mode/`, com natureza FAILURE_MODE no manifesto, e não entra no deck.

O manifesto `output/apresentacao_banca2/manifesto_figuras.json` registra, para
cada figura, o SHA-256, a natureza e as fontes, e para cada entrada o
SHA-256, o papel, a data de referência, a cobertura, a unidade e as chaves.

## 2. Números

Cada número exibido em [02](02_conteudo_slides.md) tem um código. O bloco
abaixo é **gerado** (`python3 scripts/apresentacao/gerar_figuras_banca2.py
--atualizar-doc`); não editar à mão. Três naturezas, em blocos separados no
JSON: `EMPIRICO`; `FAILURE_MODE`, que só documenta o arquivo errado e nunca é
resultado; e `TEXTO_NORMATIVO`/`CITACAO_LITERATURA`, extraídos por expressão
regular do texto-fonte (auditoria 18; trechos do doc 20 copiados pelo E8).

Os códigos da entrega de 26/10/2026 vêm de cinco tipos de fonte: a chave `v`
de `output/rdd_bolsa/S57_resumo.json` (a síntese vigente, doc 57, que já grava
o arquivo e o seletor de origem de cada valor); os CSVs de estimativas dos
blocos (`N_estimativas.csv`, `P1_estimativas.csv`, `H_estimativas.csv`,
`CA_estimativas.csv`); o resumo do portão G1 e o manifesto do a16; e as
descritivas contadas pelo gerador (seletor `descritiva`); e, para a H3
(`H3_*`), `output/rdd_bolsa/P1h_magnitudes.csv` e `P1h_resumo.json`, sem
recálculo. O limite unilateral do km (`H3_K5_P`) é registrado só para a nota
do apresentador que diz por que ele não é prova: o teste pré-registrado da
bolsa é o bilateral do P1a (`M1_P`). A razão de chances
por +R$ 5 mil do M5 por ciclo é a transformação declarada no seletor
(`transf`: multiplica o coeficiente por R$ 1 mil e exponencia).

Formatos: `pp1s` = fração multiplicada por cem, uma casa, com sinal (p.p.); `d1s`/`d2s`/`d3s`/`d4s` =
uma a quatro casas, com sinal; `d1`/`d2`/`d3` = sem sinal; `p3` = três casas,
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
| `A3_EMP_TAU` | −4,9 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "a3p_todos_emp_tau", "v"]}` | `d1s` | A3 ciclos 1–3, cortes empilhados: salto (p.p.) |
| `A3_EMP_INF` | −12,9 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "a3p_todos_emp_lo", "v"]}` | `d1s` | A3 empilhado: IC 95% inferior |
| `A3_EMP_SUP` | +3,2 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "a3p_todos_emp_hi", "v"]}` | `d1s` | A3 empilhado: IC 95% superior (maior aumento compatível) |
| `A3_EMP_MDE` | 11,5 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "a3p_todos_emp_mde", "v"]}` | `d1` | A3 empilhado: MDE de 80% (p.p.) |
| `A3_EMP_MEDIA` | 34,7 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "a3p_todos_emp_media", "v"]}` | `d1` | A3 empilhado: média abaixo do corte (%) |
| `A3_EMP_P` | 0,237 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "a3p_todos_emp_p", "v"]}` | `p3` | A3 empilhado: p |
| `A3_300_TAU` | −8,4 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "a3p_todos_300_tau", "v"]}` | `d1s` | A3 ciclos 1–3, corte 0,300: salto (p.p.) |
| `A3_300_INF` | −18,5 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "a3p_todos_300_lo", "v"]}` | `d1s` | A3 0,300: IC inferior |
| `A3_300_SUP` | +1,7 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "a3p_todos_300_hi", "v"]}` | `d1s` | A3 0,300: IC superior |
| `A3_300_MDE` | 14,5 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "a3p_todos_300_mde", "v"]}` | `d1` | A3 0,300: MDE de 80% |
| `A3_400_TAU` | −1,3 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "a3p_todos_400_tau", "v"]}` | `d1s` | A3 ciclos 1–3, corte 0,400: salto (p.p.) |
| `A3_400_INF` | −14,0 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "a3p_todos_400_lo", "v"]}` | `d1s` | A3 0,400: IC inferior |
| `A3_400_SUP` | +11,3 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "a3p_todos_400_hi", "v"]}` | `d1s` | A3 0,400: IC superior |
| `A3_400_MDE` | 18,1 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "a3p_todos_400_mde", "v"]}` | `d1` | A3 0,400: MDE de 80% |
| `A3_300_MEDIA` | 33,3 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "a3p_todos_300_media", "v"]}` | `d1` | A3 0,300: média abaixo do corte (%) |
| `A3_400_MEDIA` | 36,8 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "a3p_todos_400_media", "v"]}` | `d1` | A3 0,400: média abaixo do corte (%) |
| `A3_C1_MEDIA` | 31,2 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "a3p_c1_emp_media", "v"]}` | `d1` | A3 ciclo 1: média abaixo do corte (%) |
| `A3_C1_TAU` | −3,3 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "a3p_c1_emp_tau", "v"]}` | `d1s` | A3 só ciclo 1, cortes empilhados: salto (p.p.) |
| `A3_C1_INF` | −20,9 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "a3p_c1_emp_lo", "v"]}` | `d1s` | A3 ciclo 1: IC inferior |
| `A3_C1_SUP` | +14,2 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "a3p_c1_emp_hi", "v"]}` | `d1s` | A3 ciclo 1: IC superior |
| `A3_C1_MDE` | 25,1 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "a3p_c1_emp_mde", "v"]}` | `d1` | A3 ciclo 1: MDE de 80% |
| `A3C_EMP_TAU` | −7,1 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "a3c_todos_emp_tau", "v"]}` | `d1s` | A3 célula com candidato de 1ª opção, empilhado (p.p.) |
| `A3C_EMP_INF` | −19,6 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "a3c_todos_emp_lo", "v"]}` | `d1s` | IC inferior |
| `A3C_EMP_SUP` | +5,4 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "a3c_todos_emp_hi", "v"]}` | `d1s` | IC superior |
| `N1_SA_TAU` | −0,76 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "n_N1_tau", "v"]}` | `d2s` | N1 com controle das vagas oferecidas (S-a): salto (vagas por município) |
| `N1_SA_INF` | −1,44 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "n_N1_lo", "v"]}` | `d2s` | N1 S-a: IC 95% inferior |
| `N1_SA_SUP` | −0,07 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "n_N1_hi", "v"]}` | `d2s` | N1 S-a: IC 95% superior |
| `N1_SA_P` | 0,031 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "n_N1_p", "v"]}` | `p3` | N1 S-a: p |
| `N1_SA_HOLM` | 0,124 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "n_N1_holm", "v"]}` | `p3` | N1 S-a: p de Holm (família N1–N4) |
| `N1_SA_MDE` | 0,98 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "n_N1_mde", "v"]}` | `d2` | N1 S-a: MDE de 80% |
| `N1_SB_TAU` | −1,45 | EMPIRICO | `output/rdd_bolsa/N_estimativas.csv` | `{"filtro": {"outcome_id": "N1", "populacao": "V1+V2+V3", "corte": "empilhado", "especificacao": "S-b", "variante": "principal"}, "coluna": "tau"}` | `d2s` | N1 sem controle (S-b, efeito total da faixa): salto |
| `N1_SB_INF` | −2,90 | EMPIRICO | `output/rdd_bolsa/N_estimativas.csv` | `{"filtro": {"outcome_id": "N1", "populacao": "V1+V2+V3", "corte": "empilhado", "especificacao": "S-b", "variante": "principal"}, "coluna": "ic95_inf"}` | `d2s` | N1 S-b: IC inferior |
| `N1_SB_SUP` | −0,01 | EMPIRICO | `output/rdd_bolsa/N_estimativas.csv` | `{"filtro": {"outcome_id": "N1", "populacao": "V1+V2+V3", "corte": "empilhado", "especificacao": "S-b", "variante": "principal"}, "coluna": "ic95_sup"}` | `d2s` | N1 S-b: IC superior |
| `N1_SB_P` | 0,048 | EMPIRICO | `output/rdd_bolsa/N_estimativas.csv` | `{"filtro": {"outcome_id": "N1", "populacao": "V1+V2+V3", "corte": "empilhado", "especificacao": "S-b", "variante": "principal"}, "coluna": "p_valor"}` | `p3` | N1 S-b: p |
| `N1_SB_MDE` | 2,06 | EMPIRICO | `output/rdd_bolsa/N_estimativas.csv` | `{"filtro": {"outcome_id": "N1", "populacao": "V1+V2+V3", "corte": "empilhado", "especificacao": "S-b", "variante": "principal"}, "coluna": "mde"}` | `d2` | N1 S-b: MDE de 80% |
| `N1_MEDIA` | 2,16 | EMPIRICO | `output/rdd_bolsa/N_estimativas.csv` | `{"filtro": {"outcome_id": "N1", "populacao": "V1+V2+V3", "corte": "empilhado", "especificacao": "S-a", "variante": "principal"}, "coluna": "media_abaixo"}` | `d2` | N1: média do lado de bolsa menor, na janela (vagas por município) |
| `N1_NABX` | 267 | EMPIRICO | `output/rdd_bolsa/N_estimativas.csv` | `{"filtro": {"outcome_id": "N1", "populacao": "V1+V2+V3", "corte": "empilhado", "especificacao": "S-a", "variante": "principal"}, "coluna": "n_abaixo"}` | `int` | N1: municípios abaixo do corte (h = 0,050, ciclos e cortes empilhados) |
| `N1_NACI` | 265 | EMPIRICO | `output/rdd_bolsa/N_estimativas.csv` | `{"filtro": {"outcome_id": "N1", "populacao": "V1+V2+V3", "corte": "empilhado", "especificacao": "S-a", "variante": "principal"}, "coluna": "n_acima"}` | `int` | N1: municípios acima do corte |
| `N1_UNICO_TAU` | −1,03 | EMPIRICO | `output/rdd_bolsa/N_estimativas.csv` | `{"filtro": {"outcome_id": "N1", "populacao": "V1+V2+V3", "corte": "empilhado", "variante": "controle_coeficiente_unico"}, "coluna": "tau"}` | `d2s` | N1 com um só coeficiente do controle (auditoria 20, fora do protocolo): salto |
| `N1_UNICO_INF` | −1,79 | EMPIRICO | `output/rdd_bolsa/N_estimativas.csv` | `{"filtro": {"outcome_id": "N1", "populacao": "V1+V2+V3", "corte": "empilhado", "variante": "controle_coeficiente_unico"}, "coluna": "ic95_inf"}` | `d2s` | IC inferior |
| `N1_UNICO_SUP` | −0,28 | EMPIRICO | `output/rdd_bolsa/N_estimativas.csv` | `{"filtro": {"outcome_id": "N1", "populacao": "V1+V2+V3", "corte": "empilhado", "variante": "controle_coeficiente_unico"}, "coluna": "ic95_sup"}` | `d2s` | IC superior |
| `N1_HON_INF` | −79,58 | EMPIRICO | `output/rdd_bolsa/N_estimativas.csv` | `{"filtro": {"outcome_id": "N1", "populacao": "V1+V2+V3", "corte": "empilhado", "variante": "S-a: ic_honesto_M_x1"}, "coluna": "ic95_inf"}` | `d2s` | N1 S-a: IC honesto (M do protocolo), inferior |
| `N1_HON_SUP` | +78,07 | EMPIRICO | `output/rdd_bolsa/N_estimativas.csv` | `{"filtro": {"outcome_id": "N1", "populacao": "V1+V2+V3", "corte": "empilhado", "variante": "S-a: ic_honesto_M_x1"}, "coluna": "ic95_sup"}` | `d2s` | N1 S-a: IC honesto, superior |
| `N1_H030_TAU` | −0,78 | EMPIRICO | `output/rdd_bolsa/N_estimativas.csv` | `{"filtro": {"outcome_id": "N1", "populacao": "V1+V2+V3", "corte": "empilhado", "especificacao": "S-a", "variante": "h=0.030"}, "coluna": "tau"}` | `d2s` | N1 S-a com h = 0,030 |
| `N1_H080_TAU` | −0,47 | EMPIRICO | `output/rdd_bolsa/N_estimativas.csv` | `{"filtro": {"outcome_id": "N1", "populacao": "V1+V2+V3", "corte": "empilhado", "especificacao": "S-a", "variante": "h=0.080"}, "coluna": "tau"}` | `d2s` | N1 S-a com h = 0,080 |
| `N1_DONUT_TAU` | −0,65 | EMPIRICO | `output/rdd_bolsa/N_estimativas.csv` | `{"filtro": {"outcome_id": "N1", "populacao": "V1+V2+V3", "corte": "empilhado", "variante": "donut (S-a)"}, "coluna": "tau"}` | `d2s` | N1 S-a sem os municípios colados ao corte (donut) |
| `N1_DONUT_INF` | −1,43 | EMPIRICO | `output/rdd_bolsa/N_estimativas.csv` | `{"filtro": {"outcome_id": "N1", "populacao": "V1+V2+V3", "corte": "empilhado", "variante": "donut (S-a)"}, "coluna": "ic95_inf"}` | `d2s` | IC inferior |
| `N1_DONUT_SUP` | +0,14 | EMPIRICO | `output/rdd_bolsa/N_estimativas.csv` | `{"filtro": {"outcome_id": "N1", "populacao": "V1+V2+V3", "corte": "empilhado", "variante": "donut (S-a)"}, "coluna": "ic95_sup"}` | `d2s` | IC superior |
| `N2_SA_TAU` | −0,31 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "n_N2_tau", "v"]}` | `d2s` | N2 S-a: salto |
| `N2_SA_INF` | −0,66 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "n_N2_lo", "v"]}` | `d2s` | N2 S-a: IC inferior |
| `N2_SA_SUP` | +0,04 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "n_N2_hi", "v"]}` | `d2s` | N2 S-a: IC superior |
| `N2_SA_HOLM` | 0,235 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "n_N2_holm", "v"]}` | `p3` | N2 S-a: p de Holm |
| `N3_SA_TAU` | −0,35 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "n_N3_tau", "v"]}` | `d2s` | N3 S-a: salto |
| `N3_SA_INF` | −0,87 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "n_N3_lo", "v"]}` | `d2s` | N3 S-a: IC inferior |
| `N3_SA_SUP` | +0,17 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "n_N3_hi", "v"]}` | `d2s` | N3 S-a: IC superior |
| `N3_SA_HOLM` | 0,376 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "n_N3_holm", "v"]}` | `p3` | N3 S-a: p de Holm |
| `N4_SA_TAU` | −0,21 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "n_N4_tau", "v"]}` | `d2s` | N4 S-a: salto |
| `N4_SA_INF` | −1,34 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "n_N4_lo", "v"]}` | `d2s` | N4 S-a: IC inferior |
| `N4_SA_SUP` | +0,92 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "n_N4_hi", "v"]}` | `d2s` | N4 S-a: IC superior |
| `N4_SA_HOLM` | 0,717 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "n_N4_holm", "v"]}` | `p3` | N4 S-a: p de Holm |
| `M1_COEF` | +0,0424 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "m1_coef", "v"]}` | `d4s` | M1: coeficiente da bolsa por R$ 1 mil/mês |
| `M1_INF` | −0,0027 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "m1_lo", "v"]}` | `d4s` | M1: IC 95% inferior |
| `M1_SUP` | +0,0874 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "m1_hi", "v"]}` | `d4s` | M1: IC 95% superior |
| `M1_P` | 0,065 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "m1_p", "v"]}` | `p3` | M1: p (família de um teste; p de Holm = p) |
| `M1_RC` | 1,24 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "m1_rc", "v"]}` | `d2` | M1: razão de chances por +R$ 5 mil |
| `M1_RC_INF` | 0,99 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "m1_rc_lo", "v"]}` | `d2` | M1: razão de chances, IC inferior |
| `M1_RC_SUP` | 1,55 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "m1_rc_hi", "v"]}` | `d2` | M1: razão de chances, IC superior |
| `M1_RC_MDE` | 1,38 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "m1_rc_mde", "v"]}` | `d2` | M1: MDE de 80% em razão de chances |
| `M1_N` | 5.421 | EMPIRICO | `output/rdd_bolsa/P1_estimativas.csv` | `{"filtro": {"modelo": "M1", "ciclo": "empilhado", "termo": "bolsa_mil"}, "coluna": "n_candidatos"}` | `int` | M1: candidatos de 1ª opção na amostra P1 |
| `M5_C1_RC` | 1,07 | EMPIRICO | `output/rdd_bolsa/P1_estimativas.csv` | `{"filtro": {"modelo": "M5", "ciclo": "1", "termo": "bolsa_mil"}, "coluna": "coef", "transf": [["mul", 5], ["exp"]]}` | `d2` | M5 ciclo 1: razão de chances por +R$ 5 mil |
| `M5_C1_RCI` | 0,69 | EMPIRICO | `output/rdd_bolsa/P1_estimativas.csv` | `{"filtro": {"modelo": "M5", "ciclo": "1", "termo": "bolsa_mil"}, "coluna": "ic95_inf", "transf": [["mul", 5], ["exp"]]}` | `d2` | M5 ciclo 1: IC inferior |
| `M5_C1_RCS` | 1,65 | EMPIRICO | `output/rdd_bolsa/P1_estimativas.csv` | `{"filtro": {"modelo": "M5", "ciclo": "1", "termo": "bolsa_mil"}, "coluna": "ic95_sup", "transf": [["mul", 5], ["exp"]]}` | `d2` | M5 ciclo 1: IC superior |
| `M5_C1_P` | 0,764 | EMPIRICO | `output/rdd_bolsa/P1_estimativas.csv` | `{"filtro": {"modelo": "M5", "ciclo": "1", "termo": "bolsa_mil"}, "coluna": "p"}` | `p3` | M5 ciclo 1: p |
| `M5_C1_COEF` | +0,0132 | EMPIRICO | `output/rdd_bolsa/P1_estimativas.csv` | `{"filtro": {"modelo": "M5", "ciclo": "1", "termo": "bolsa_mil"}, "coluna": "coef"}` | `d4s` | M5 ciclo 1: coeficiente por R$ 1 mil |
| `M5_C2_RC` | 1,70 | EMPIRICO | `output/rdd_bolsa/P1_estimativas.csv` | `{"filtro": {"modelo": "M5", "ciclo": "2", "termo": "bolsa_mil"}, "coluna": "coef", "transf": [["mul", 5], ["exp"]]}` | `d2` | M5 ciclo 2: razão de chances por +R$ 5 mil |
| `M5_C2_RCI` | 1,22 | EMPIRICO | `output/rdd_bolsa/P1_estimativas.csv` | `{"filtro": {"modelo": "M5", "ciclo": "2", "termo": "bolsa_mil"}, "coluna": "ic95_inf", "transf": [["mul", 5], ["exp"]]}` | `d2` | M5 ciclo 2: IC inferior |
| `M5_C2_RCS` | 2,37 | EMPIRICO | `output/rdd_bolsa/P1_estimativas.csv` | `{"filtro": {"modelo": "M5", "ciclo": "2", "termo": "bolsa_mil"}, "coluna": "ic95_sup", "transf": [["mul", 5], ["exp"]]}` | `d2` | M5 ciclo 2: IC superior |
| `M5_C2_P` | 0,002 | EMPIRICO | `output/rdd_bolsa/P1_estimativas.csv` | `{"filtro": {"modelo": "M5", "ciclo": "2", "termo": "bolsa_mil"}, "coluna": "p"}` | `p3` | M5 ciclo 2: p |
| `M5_C2_COEF` | +0,1064 | EMPIRICO | `output/rdd_bolsa/P1_estimativas.csv` | `{"filtro": {"modelo": "M5", "ciclo": "2", "termo": "bolsa_mil"}, "coluna": "coef"}` | `d4s` | M5 ciclo 2: coeficiente por R$ 1 mil |
| `M5_C3_RC` | 1,00 | EMPIRICO | `output/rdd_bolsa/P1_estimativas.csv` | `{"filtro": {"modelo": "M5", "ciclo": "3", "termo": "bolsa_mil"}, "coluna": "coef", "transf": [["mul", 5], ["exp"]]}` | `d2` | M5 ciclo 3: razão de chances por +R$ 5 mil |
| `M5_C3_RCI` | 0,72 | EMPIRICO | `output/rdd_bolsa/P1_estimativas.csv` | `{"filtro": {"modelo": "M5", "ciclo": "3", "termo": "bolsa_mil"}, "coluna": "ic95_inf", "transf": [["mul", 5], ["exp"]]}` | `d2` | M5 ciclo 3: IC inferior |
| `M5_C3_RCS` | 1,39 | EMPIRICO | `output/rdd_bolsa/P1_estimativas.csv` | `{"filtro": {"modelo": "M5", "ciclo": "3", "termo": "bolsa_mil"}, "coluna": "ic95_sup", "transf": [["mul", 5], ["exp"]]}` | `d2` | M5 ciclo 3: IC superior |
| `M5_C3_P` | 0,990 | EMPIRICO | `output/rdd_bolsa/P1_estimativas.csv` | `{"filtro": {"modelo": "M5", "ciclo": "3", "termo": "bolsa_mil"}, "coluna": "p"}` | `p3` | M5 ciclo 3: p |
| `M5_C3_COEF` | −0,0004 | EMPIRICO | `output/rdd_bolsa/P1_estimativas.csv` | `{"filtro": {"modelo": "M5", "ciclo": "3", "termo": "bolsa_mil"}, "coluna": "coef"}` | `d4s` | M5 ciclo 3: coeficiente por R$ 1 mil |
| `M5_WALD_P` | 0,058 | EMPIRICO | `output/rdd_bolsa/P1_estimativas.csv` | `{"filtro": {"modelo": "M5", "tipo_linha": "wald_igualdade_ciclos"}, "coluna": "p"}` | `p3` | M5: Wald da igualdade do coeficiente da bolsa entre os ciclos, p |
| `M0_COEF` | +0,0690 | EMPIRICO | `output/rdd_bolsa/P1_estimativas.csv` | `{"filtro": {"modelo": "M0", "ciclo": "empilhado", "termo": "bolsa_mil"}, "coluna": "coef"}` | `d4s` | M0: coeficiente da bolsa (sem distância) |
| `M2_COEF` | +0,0492 | EMPIRICO | `output/rdd_bolsa/P1_estimativas.csv` | `{"filtro": {"modelo": "M2", "ciclo": "empilhado", "termo": "bolsa_mil"}, "coluna": "coef"}` | `d4s` | M2: coeficiente da bolsa (log da distância) |
| `M4_COEF` | +0,0759 | EMPIRICO | `output/rdd_bolsa/P1_estimativas.csv` | `{"filtro": {"modelo": "M4", "ciclo": "empilhado", "termo": "bolsa_mil"}, "coluna": "coef"}` | `d4s` | M4: coeficiente da bolsa (efeito fixo de UF) |
| `M7_COEF` | +0,0304 | EMPIRICO | `output/rdd_bolsa/P1_estimativas.csv` | `{"filtro": {"modelo": "M7", "ciclo": "empilhado", "termo": "bolsa_mil"}, "coluna": "coef"}` | `d4s` | M7: coeficiente da bolsa (logit explodido) |
| `M8_COEF` | +0,0499 | EMPIRICO | `output/rdd_bolsa/P1_estimativas.csv` | `{"filtro": {"modelo": "M8", "ciclo": "empilhado", "termo": "media_bolsa_mil"}, "coluna": "coef"}` | `d4s` | M8: coeficiente da bolsa (logit misto, média) |
| `M9_COEF` | +0,0434 | EMPIRICO | `output/rdd_bolsa/P1_estimativas.csv` | `{"filtro": {"modelo": "M9", "ciclo": "empilhado", "termo": "bolsa_mil"}, "coluna": "coef"}` | `d4s` | M9: coeficiente da bolsa (logit aninhado) |
| `M7_INF` | −0,0150 | EMPIRICO | `output/rdd_bolsa/P1_estimativas.csv` | `{"filtro": {"modelo": "M7", "ciclo": "empilhado", "termo": "bolsa_mil"}, "coluna": "ic95_inf"}` | `d4s` | M7: IC inferior |
| `M7_SUP` | +0,0758 | EMPIRICO | `output/rdd_bolsa/P1_estimativas.csv` | `{"filtro": {"modelo": "M7", "ciclo": "empilhado", "termo": "bolsa_mil"}, "coluna": "ic95_sup"}` | `d4s` | M7: IC superior |
| `H3_ESTATUTO` | PROTOCOLO_52B_POS_RESULTADO | EMPIRICO | `output/rdd_bolsa/P1h_resumo.json` | `{"caminho": ["estatuto"]}` | `txt` | P1h: estatuto do bloco (pós-resultado; regra da força da evidência na figura da cadeia) |
| `H3_DUF` | 1,98 | EMPIRICO | `output/rdd_bolsa/P1h_magnitudes.csv` | `{"filtro": {"id_linha": "P1h-1"}, "coluna": "estimativa"}` | `d2` | P1h-1: D_UF = θ_UF − 10·β no M1 (log-chance; mesma UF, outra região de saúde, contra toda a amplitude da bolsa) |
| `H3_DUF_INF` | 1,56 | EMPIRICO | `output/rdd_bolsa/P1h_magnitudes.csv` | `{"filtro": {"id_linha": "P1h-1"}, "coluna": "ic95_inf"}` | `d2` | P1h-1: IC 95% inferior (cluster por conjunto) |
| `H3_DUF_SUP` | 2,40 | EMPIRICO | `output/rdd_bolsa/P1h_magnitudes.csv` | `{"filtro": {"id_linha": "P1h-1"}, "coluna": "ic95_sup"}` | `d2` | P1h-1: IC 95% superior |
| `H3_DUF_P` | < 0,001 | EMPIRICO | `output/rdd_bolsa/P1h_magnitudes.csv` | `{"filtro": {"id_linha": "P1h-1"}, "coluna": "p_unilateral"}` | `p3` | P1h-1: p unilateral (H0: D_UF ≤ 0) |
| `H3_DUF_HOLM` | < 0,001 | EMPIRICO | `output/rdd_bolsa/P1h_magnitudes.csv` | `{"filtro": {"id_linha": "P1h-1"}, "coluna": "p_holm"}` | `p3` | P1h-1: p de Holm (família de um teste; igual ao p unilateral) |
| `H3_K5` | 112 | EMPIRICO | `output/rdd_bolsa/P1h_magnitudes.csv` | `{"filtro": {"id_linha": "P1h-2a"}, "coluna": "estimativa"}` | `d0` | P1h-2a: K5, km a menos de distância com o peso de um degrau de R$ 5 mil (descritivo) (km, método delta) |
| `H3_K5_INF` | −9 | EMPIRICO | `output/rdd_bolsa/P1h_magnitudes.csv` | `{"filtro": {"id_linha": "P1h-2a"}, "coluna": "ic95_inf"}` | `d0` | P1h-2a: K5, km a menos de distância com o peso de um degrau de R$ 5 mil (descritivo), IC 95% inferior (km, método delta) |
| `H3_K5_SUP` | 233 | EMPIRICO | `output/rdd_bolsa/P1h_magnitudes.csv` | `{"filtro": {"id_linha": "P1h-2a"}, "coluna": "ic95_sup"}` | `d0` | P1h-2a: K5, km a menos de distância com o peso de um degrau de R$ 5 mil (descritivo), IC 95% superior (km, método delta) |
| `H3_K10` | 224 | EMPIRICO | `output/rdd_bolsa/P1h_magnitudes.csv` | `{"filtro": {"id_linha": "P1h-2b"}, "coluna": "estimativa"}` | `d0` | P1h-2b: K10, km a menos de distância com o peso de toda a amplitude (descritivo) (km, método delta) |
| `H3_K10_INF` | −18 | EMPIRICO | `output/rdd_bolsa/P1h_magnitudes.csv` | `{"filtro": {"id_linha": "P1h-2b"}, "coluna": "ic95_inf"}` | `d0` | P1h-2b: K10, km a menos de distância com o peso de toda a amplitude (descritivo), IC 95% inferior (km, método delta) |
| `H3_K10_SUP` | 466 | EMPIRICO | `output/rdd_bolsa/P1h_magnitudes.csv` | `{"filtro": {"id_linha": "P1h-2b"}, "coluna": "ic95_sup"}` | `d0` | P1h-2b: K10, km a menos de distância com o peso de toda a amplitude (descritivo), IC 95% superior (km, método delta) |
| `H3_K5_P` | 0,035 | EMPIRICO | `output/rdd_bolsa/P1h_magnitudes.csv` | `{"filtro": {"id_linha": "P1h-2a"}, "coluna": "p_unilateral"}` | `p3` | P1h-2a: p unilateral de K5 (descritivo; não substitui o teste bilateral do P1a) |
| `H3_S_M2` | 1,18 | EMPIRICO | `output/rdd_bolsa/P1h_magnitudes.csv` | `{"filtro": {"id_linha": "P1h-3", "modelo": "M2", "ciclo": "empilhado"}, "coluna": "estimativa"}` | `d2` | P1h-3: D_UF em M2 (log da distância), sensibilidade com BKY |
| `H3_S_M4` | 1,73 | EMPIRICO | `output/rdd_bolsa/P1h_magnitudes.csv` | `{"filtro": {"id_linha": "P1h-3", "modelo": "M4", "ciclo": "empilhado"}, "coluna": "estimativa"}` | `d2` | P1h-3: D_UF em M4 (efeito fixo de UF da vaga), sensibilidade com BKY |
| `H3_S_M5C1` | 2,34 | EMPIRICO | `output/rdd_bolsa/P1h_magnitudes.csv` | `{"filtro": {"id_linha": "P1h-3", "modelo": "M5", "ciclo": "1"}, "coluna": "estimativa"}` | `d2` | P1h-3: D_UF em M5 (só o ciclo 1), sensibilidade com BKY |
| `H3_S_M5C2` | 1,31 | EMPIRICO | `output/rdd_bolsa/P1h_magnitudes.csv` | `{"filtro": {"id_linha": "P1h-3", "modelo": "M5", "ciclo": "2"}, "coluna": "estimativa"}` | `d2` | P1h-3: D_UF em M5 (só o ciclo 2), sensibilidade com BKY |
| `H3_S_M5C3` | 2,37 | EMPIRICO | `output/rdd_bolsa/P1h_magnitudes.csv` | `{"filtro": {"id_linha": "P1h-3", "modelo": "M5", "ciclo": "3"}, "coluna": "estimativa"}` | `d2` | P1h-3: D_UF em M5 (só o ciclo 3), sensibilidade com BKY |
| `H3_S_M7` | 2,07 | EMPIRICO | `output/rdd_bolsa/P1h_magnitudes.csv` | `{"filtro": {"id_linha": "P1h-3", "modelo": "M7", "ciclo": "empilhado"}, "coluna": "estimativa"}` | `d2` | P1h-3: D_UF em M7 (logit explodido, 1ª e 2ª opção), sensibilidade com BKY |
| `H3_10B` | 0,42 | EMPIRICO | `output/rdd_bolsa/P1h_magnitudes.csv` | `{"filtro": {"id_linha": "FIG", "componente": "10β"}, "coluna": "estimativa"}` | `d2` | peso no M1: toda a amplitude da bolsa, 10·β |
| `H3_10B_INF` | −0,03 | EMPIRICO | `output/rdd_bolsa/P1h_magnitudes.csv` | `{"filtro": {"id_linha": "FIG", "componente": "10β"}, "coluna": "ic95_inf"}` | `d2` | peso no M1: toda a amplitude da bolsa, 10·β, IC 95% inferior |
| `H3_10B_SUP` | 0,87 | EMPIRICO | `output/rdd_bolsa/P1h_magnitudes.csv` | `{"filtro": {"id_linha": "FIG", "componente": "10β"}, "coluna": "ic95_sup"}` | `d2` | peso no M1: toda a amplitude da bolsa, 10·β, IC 95% superior |
| `H3_THETA` | 2,40 | EMPIRICO | `output/rdd_bolsa/P1h_magnitudes.csv` | `{"filtro": {"id_linha": "FIG", "componente": "θ_UF"}, "coluna": "estimativa"}` | `d2` | peso no M1: mesma UF, outra região de saúde, θ_UF |
| `H3_THETA_INF` | 2,28 | EMPIRICO | `output/rdd_bolsa/P1h_magnitudes.csv` | `{"filtro": {"id_linha": "FIG", "componente": "θ_UF"}, "coluna": "ic95_inf"}` | `d2` | peso no M1: mesma UF, outra região de saúde, θ_UF, IC 95% inferior |
| `H3_THETA_SUP` | 2,53 | EMPIRICO | `output/rdd_bolsa/P1h_magnitudes.csv` | `{"filtro": {"id_linha": "FIG", "componente": "θ_UF"}, "coluna": "ic95_sup"}` | `d2` | peso no M1: mesma UF, outra região de saúde, θ_UF, IC 95% superior |
| `P4_HT_ATT` | +6,6 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "p4_ht_att", "v"]}` | `d1s` | P4 horas totais: média de θ(0..+6), h/sem |
| `P4_HT_INF` | +5,4 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "p4_ht_lo", "v"]}` | `d1s` | P4 horas totais: IC inferior |
| `P4_HT_SUP` | +7,8 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "p4_ht_hi", "v"]}` | `d1s` | P4 horas totais: IC superior |
| `P4_HT_PRE` | 0,310 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "p4_ht_pre", "v"]}` | `p3` | P4 horas totais: p do Wald do pré |
| `P4_HM_ATT` | +8,7 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "p4_hm_att", "v"]}` | `d1s` | P4 horas no município do posto: média de θ(0..+6), h/sem |
| `P4_HM_INF` | +7,9 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "p4_hm_lo", "v"]}` | `d1s` | P4 horas no município do posto: IC inferior |
| `P4_HM_SUP` | +9,5 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "p4_hm_hi", "v"]}` | `d1s` | P4 horas no município do posto: IC superior |
| `P4_HM_PRE` | 0,001 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "p4_hm_pre", "v"]}` | `p3` | P4 horas no município do posto: p do Wald do pré |
| `P4_HF_ATT` | −2,1 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "p4_hf_att", "v"]}` | `d1s` | P4 horas fora do município do posto: média de θ(0..+6), h/sem |
| `P4_HF_INF` | −3,2 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "p4_hf_lo", "v"]}` | `d1s` | P4 horas fora do município do posto: IC inferior |
| `P4_HF_SUP` | −1,0 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "p4_hf_hi", "v"]}` | `d1s` | P4 horas fora do município do posto: IC superior |
| `P4_HF_PRE` | 0,927 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "p4_hf_pre", "v"]}` | `p3` | P4 horas fora do município do posto: p do Wald do pré |
| `P4_ORIGEM` | 51,0 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "p4_origem", "v"]}` | `d1` | P4: médicos que já tinham vínculo no município do posto (%) |
| `P4_ORIGEM_INF` | 48,4 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "p4_origem_lo", "v"]}` | `d1` | IC inferior (%) |
| `P4_ORIGEM_SUP` | 53,7 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "p4_origem_hi", "v"]}` | `d1` | IC superior (%) |
| `RR_HT` | 1,30 | EMPIRICO | `output/rdd_bolsa/H_estimativas.csv` | `{"filtro": {"id_linha": "H-P4-horas_totais", "alvo": "media_pos", "restricao": "RM_ruptura"}, "coluna": "parametro"}` | `d2` | Rambachan–Roth, horas totais: ruptura de M̄ (Δ^RM, teste condicional) |
| `RR_HM` | 1,90 | EMPIRICO | `output/rdd_bolsa/H_estimativas.csv` | `{"filtro": {"id_linha": "H-P4-horas_mun_posto", "alvo": "media_pos", "restricao": "RM_ruptura"}, "coluna": "parametro"}` | `d2` | Rambachan–Roth, horas no município do posto: ruptura de M̄ |
| `RR_HF` | 0,78 | EMPIRICO | `output/rdd_bolsa/H_estimativas.csv` | `{"filtro": {"id_linha": "H-P4-horas_fora_mun_posto", "alvo": "media_pos", "restricao": "RM_ruptura"}, "coluna": "parametro"}` | `d2` | Rambachan–Roth, horas fora do município do posto: ruptura de M̄ |
| `RR_HT_M1_INF` | +1,48 | EMPIRICO | `output/rdd_bolsa/H_estimativas.csv` | `{"filtro": {"id_linha": "H-P4-horas_totais", "alvo": "media_pos", "restricao": "RM", "parametro": "1"}, "coluna": "ic_inf"}` | `d2s` | Rambachan–Roth, horas totais, M̄ = 1: IC robusto inferior |
| `RR_HT_M1_SUP` | +11,77 | EMPIRICO | `output/rdd_bolsa/H_estimativas.csv` | `{"filtro": {"id_linha": "H-P4-horas_totais", "alvo": "media_pos", "restricao": "RM", "parametro": "1"}, "coluna": "ic_sup"}` | `d2s` | Rambachan–Roth, horas totais, M̄ = 1: IC robusto superior |
| `CA_HT_EST` | +7,91 | EMPIRICO | `output/rdd_bolsa/CA_estimativas.csv` | `{"filtro": {"id_linha": "P4-CA", "outcome": "horas_totais", "estatistica": "efeito_pos_medio"}, "coluna": "valor"}` | `d2s` | P4-CA horas totais: efeito médio do pós (h/sem) |
| `CA_HT_INF` | −0,63 | EMPIRICO | `output/rdd_bolsa/CA_estimativas.csv` | `{"filtro": {"id_linha": "P4-CA", "outcome": "horas_totais", "estatistica": "efeito_pos_medio"}, "coluna": "ic95_inf"}` | `d2s` | P4-CA horas totais: IC inferior |
| `CA_HT_SUP` | +16,45 | EMPIRICO | `output/rdd_bolsa/CA_estimativas.csv` | `{"filtro": {"id_linha": "P4-CA", "outcome": "horas_totais", "estatistica": "efeito_pos_medio"}, "coluna": "ic95_sup"}` | `d2s` | P4-CA horas totais: IC superior |
| `CA_HT_HOLM` | 0,162 | EMPIRICO | `output/rdd_bolsa/CA_estimativas.csv` | `{"filtro": {"id_linha": "P4-CA", "outcome": "horas_totais", "estatistica": "efeito_pos_medio"}, "coluna": "p_holm"}` | `p3` | P4-CA horas totais: p de Holm |
| `CA_HT_PRE` | 0,837 | EMPIRICO | `output/rdd_bolsa/CA_estimativas.csv` | `{"filtro": {"id_linha": "P4-CA", "outcome": "horas_totais", "estatistica": "wald_pre"}, "coluna": "p_valor"}` | `p3` | P4-CA horas totais: p do pré (permutação) |
| `CA_HM_EST` | +10,92 | EMPIRICO | `output/rdd_bolsa/CA_estimativas.csv` | `{"filtro": {"id_linha": "P4-CA", "outcome": "horas_mun_1a", "estatistica": "efeito_pos_medio"}, "coluna": "valor"}` | `d2s` | P4-CA horas no município da 1ª opção: efeito médio do pós (h/sem) |
| `CA_HM_INF` | +4,15 | EMPIRICO | `output/rdd_bolsa/CA_estimativas.csv` | `{"filtro": {"id_linha": "P4-CA", "outcome": "horas_mun_1a", "estatistica": "efeito_pos_medio"}, "coluna": "ic95_inf"}` | `d2s` | P4-CA horas no município da 1ª opção: IC inferior |
| `CA_HM_SUP` | +17,68 | EMPIRICO | `output/rdd_bolsa/CA_estimativas.csv` | `{"filtro": {"id_linha": "P4-CA", "outcome": "horas_mun_1a", "estatistica": "efeito_pos_medio"}, "coluna": "ic95_sup"}` | `d2s` | P4-CA horas no município da 1ª opção: IC superior |
| `CA_HM_HOLM` | 0,016 | EMPIRICO | `output/rdd_bolsa/CA_estimativas.csv` | `{"filtro": {"id_linha": "P4-CA", "outcome": "horas_mun_1a", "estatistica": "efeito_pos_medio"}, "coluna": "p_holm"}` | `p3` | P4-CA horas no município da 1ª opção: p de Holm |
| `CA_HM_PRE` | 0,297 | EMPIRICO | `output/rdd_bolsa/CA_estimativas.csv` | `{"filtro": {"id_linha": "P4-CA", "outcome": "horas_mun_1a", "estatistica": "wald_pre"}, "coluna": "p_valor"}` | `p3` | P4-CA horas no município da 1ª opção: p do pré (permutação) |
| `CA_HF_EST` | −3,01 | EMPIRICO | `output/rdd_bolsa/CA_estimativas.csv` | `{"filtro": {"id_linha": "P4-CA", "outcome": "horas_fora_1a", "estatistica": "efeito_pos_medio"}, "coluna": "valor"}` | `d2s` | P4-CA horas fora do município da 1ª opção: efeito médio do pós (h/sem) |
| `CA_HF_INF` | −10,14 | EMPIRICO | `output/rdd_bolsa/CA_estimativas.csv` | `{"filtro": {"id_linha": "P4-CA", "outcome": "horas_fora_1a", "estatistica": "efeito_pos_medio"}, "coluna": "ic95_inf"}` | `d2s` | P4-CA horas fora do município da 1ª opção: IC inferior |
| `CA_HF_SUP` | +4,12 | EMPIRICO | `output/rdd_bolsa/CA_estimativas.csv` | `{"filtro": {"id_linha": "P4-CA", "outcome": "horas_fora_1a", "estatistica": "efeito_pos_medio"}, "coluna": "ic95_sup"}` | `d2s` | P4-CA horas fora do município da 1ª opção: IC superior |
| `CA_HF_HOLM` | 0,527 | EMPIRICO | `output/rdd_bolsa/CA_estimativas.csv` | `{"filtro": {"id_linha": "P4-CA", "outcome": "horas_fora_1a", "estatistica": "efeito_pos_medio"}, "coluna": "p_holm"}` | `p3` | P4-CA horas fora do município da 1ª opção: p de Holm |
| `CA_HF_PRE` | 0,200 | EMPIRICO | `output/rdd_bolsa/CA_estimativas.csv` | `{"filtro": {"id_linha": "P4-CA", "outcome": "horas_fora_1a", "estatistica": "wald_pre"}, "coluna": "p_valor"}` | `p3` | P4-CA horas fora do município da 1ª opção: p do pré (permutação) |
| `P6_ESTATUTO` | EXPLORATORIO_P6 | EMPIRICO | `output/rdd_bolsa/P6_resumo.json` | `{"caminho": ["estatuto"]}` | `txt` | P6: estatuto do bloco (regra da força da evidência na figura da cadeia) |
| `P6_Y1_EST` | +0,405 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "p6_y1_media_est", "v"]}` | `d3s` | P6 Y1 vínculo no município da vaga, média do seguimento |
| `P6_Y1_INF` | +0,210 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "p6_y1_media_lo", "v"]}` | `d3s` | P6 Y1: IC inferior |
| `P6_Y1_SUP` | +0,600 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "p6_y1_media_hi", "v"]}` | `d3s` | P6 Y1: IC superior |
| `P6_Y1_HOLM` | 0,010 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "p6_y1_media_holm", "v"]}` | `p3` | P6 Y1: p de Holm |
| `P6_Y3_EST` | +15,5 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "p6_y3_media_est", "v"]}` | `d1s` | P6 Y3 horas totais, média do seguimento (h/sem) |
| `P6_Y3_INF` | +0,6 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "p6_y3_media_lo", "v"]}` | `d1s` | P6 Y3: IC inferior |
| `P6_Y3_SUP` | +30,4 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "p6_y3_media_hi", "v"]}` | `d1s` | P6 Y3: IC superior |
| `P6_Y3_HOLM` | 0,384 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "p6_y3_media_holm", "v"]}` | `p3` | P6 Y3: p de Holm |
| `K1_TAU` | +7,92 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "kd1_K1_tau", "v"]}` | `d2s` | K1 produção SUS nas CBO-alvo, DiRD nos cortes (por 10 mil hab./mês) |
| `K1_INF` | −27,58 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "kd1_K1_lo", "v"]}` | `d2s` | K1: IC inferior |
| `K1_SUP` | +43,42 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "kd1_K1_hi", "v"]}` | `d2s` | K1: IC superior |
| `K1_HOLM` | 1,000 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "kd1_K1_holm", "v"]}` | `p3` | K1: p de Holm (família K1–K3) |
| `R_P1_EST` | −4,9 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "R_P1_c5", "v"]}` | `d1s` | R-P1 célula preenchida por +R$ 5 mil na bolsa média das concorrentes (p.p.) |
| `R_P1_INF` | −14,3 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "R_P1_lo", "v"]}` | `d1s` | R-P1: IC inferior |
| `R_P1_SUP` | +4,6 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "R_P1_hi", "v"]}` | `d1s` | R-P1: IC superior |
| `R_P1_HOLM` | 0,624 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "R_P1_holm", "v"]}` | `p3` | R-P1: p de Holm |
| `R_P1_MDE` | 13,5 | EMPIRICO | `output/rdd_bolsa/S57_resumo.json` | `{"caminho": ["v", "R_P1_mde", "v"]}` | `d1` | R-P1: MDE de 80% (p.p.) |
| `D_C1_MUN` | 368 | EMPIRICO | `output/rdd_bolsa/outcomes/outcomes_V_celula.parquet` | `{"descritiva": "C1_MUN"}` | `int` | ciclo 1: municípios com célula no quadro da 1ª chamada |
| `D_C1_CEL` | 1.295 | EMPIRICO | `output/rdd_bolsa/outcomes/outcomes_V_celula.parquet` | `{"descritiva": "C1_CEL"}` | `int` | ciclo 1: células (estabelecimento × curso) no quadro da 1ª chamada |
| `D_C1_VI` | 678 | EMPIRICO | `output/rdd_bolsa/outcomes/outcomes_V_celula.parquet` | `{"descritiva": "C1_VI"}` | `int` | ciclo 1: vagas imediatas |
| `D_C1_CR` | 1.145 | EMPIRICO | `output/rdd_bolsa/outcomes/outcomes_V_celula.parquet` | `{"descritiva": "C1_CR"}` | `int` | ciclo 1: vagas de cadastro reserva |
| `D_C1_CAND1` | 993 | EMPIRICO | `output/rdd_bolsa/outcomes/outcomes_V_celula.parquet` | `{"descritiva": "C1_CAND1"}` | `int` | ciclo 1: candidatos com 1ª opção numa célula do quadro |
| `D_C1_PRE1` | 393 | EMPIRICO | `output/rdd_bolsa/outcomes/outcomes_V_celula.parquet` | `{"descritiva": "C1_PRE1"}` | `int` | ciclo 1: células com alguma confirmação ou homologação na 1ª chamada |
| `D_C1_PRE1_PCT` | 30,3 | EMPIRICO | `output/rdd_bolsa/outcomes/outcomes_V_celula.parquet` | `{"descritiva": "C1_PRE1_PCT"}` | `pct1` | ciclo 1: fração de células preenchidas na 1ª chamada (%) |
| `D_C1_F3` | 159 | EMPIRICO | `output/rdd_bolsa/outcomes/outcomes_V_celula.parquet` | `{"descritiva": "C1_F3"}` | `int` | ciclo 1: municípios na faixa de R$ 10 mil (IVS até 0,300) pela grade aplicada |
| `D_C1_F2` | 107 | EMPIRICO | `output/rdd_bolsa/outcomes/outcomes_V_celula.parquet` | `{"descritiva": "C1_F2"}` | `int` | ciclo 1: municípios na faixa de R$ 15 mil (IVS de 0,301 a 0,400) |
| `D_C1_F1` | 102 | EMPIRICO | `output/rdd_bolsa/outcomes/outcomes_V_celula.parquet` | `{"descritiva": "C1_F1"}` | `int` | ciclo 1: municípios na faixa de R$ 20 mil (IVS acima de 0,400) |
| `D_C2_MUN` | 454 | EMPIRICO | `output/rdd_bolsa/outcomes/outcomes_V_celula.parquet` | `{"descritiva": "C2_MUN"}` | `int` | ciclo 2: municípios com célula no quadro da 1ª chamada |
| `D_C2_CEL` | 1.547 | EMPIRICO | `output/rdd_bolsa/outcomes/outcomes_V_celula.parquet` | `{"descritiva": "C2_CEL"}` | `int` | ciclo 2: células (estabelecimento × curso) no quadro da 1ª chamada |
| `D_C2_VI` | 1.836 | EMPIRICO | `output/rdd_bolsa/outcomes/outcomes_V_celula.parquet` | `{"descritiva": "C2_VI"}` | `int` | ciclo 2: vagas imediatas |
| `D_C2_CR` | 1.053 | EMPIRICO | `output/rdd_bolsa/outcomes/outcomes_V_celula.parquet` | `{"descritiva": "C2_CR"}` | `int` | ciclo 2: vagas de cadastro reserva |
| `D_C2_CAND1` | 2.140 | EMPIRICO | `output/rdd_bolsa/outcomes/outcomes_V_celula.parquet` | `{"descritiva": "C2_CAND1"}` | `int` | ciclo 2: candidatos com 1ª opção numa célula do quadro |
| `D_C2_PRE1` | 728 | EMPIRICO | `output/rdd_bolsa/outcomes/outcomes_V_celula.parquet` | `{"descritiva": "C2_PRE1"}` | `int` | ciclo 2: células com alguma confirmação ou homologação na 1ª chamada |
| `D_C2_PRE1_PCT` | 47,1 | EMPIRICO | `output/rdd_bolsa/outcomes/outcomes_V_celula.parquet` | `{"descritiva": "C2_PRE1_PCT"}` | `pct1` | ciclo 2: fração de células preenchidas na 1ª chamada (%) |
| `D_C2_F3` | 210 | EMPIRICO | `output/rdd_bolsa/outcomes/outcomes_V_celula.parquet` | `{"descritiva": "C2_F3"}` | `int` | ciclo 2: municípios na faixa de R$ 10 mil (IVS até 0,300) pela grade aplicada |
| `D_C2_F2` | 115 | EMPIRICO | `output/rdd_bolsa/outcomes/outcomes_V_celula.parquet` | `{"descritiva": "C2_F2"}` | `int` | ciclo 2: municípios na faixa de R$ 15 mil (IVS de 0,301 a 0,400) |
| `D_C2_F1` | 129 | EMPIRICO | `output/rdd_bolsa/outcomes/outcomes_V_celula.parquet` | `{"descritiva": "C2_F1"}` | `int` | ciclo 2: municípios na faixa de R$ 20 mil (IVS acima de 0,400) |
| `D_C3_MUN` | 748 | EMPIRICO | `output/rdd_bolsa/outcomes/outcomes_V_celula.parquet` | `{"descritiva": "C3_MUN"}` | `int` | ciclo 3: municípios com célula no quadro da 1ª chamada |
| `D_C3_CEL` | 2.293 | EMPIRICO | `output/rdd_bolsa/outcomes/outcomes_V_celula.parquet` | `{"descritiva": "C3_CEL"}` | `int` | ciclo 3: células (estabelecimento × curso) no quadro da 1ª chamada |
| `D_C3_VI` | 1.132 | EMPIRICO | `output/rdd_bolsa/outcomes/outcomes_V_celula.parquet` | `{"descritiva": "C3_VI"}` | `int` | ciclo 3: vagas imediatas |
| `D_C3_CR` | 3.999 | EMPIRICO | `output/rdd_bolsa/outcomes/outcomes_V_celula.parquet` | `{"descritiva": "C3_CR"}` | `int` | ciclo 3: vagas de cadastro reserva |
| `D_C3_CAND1` | 2.581 | EMPIRICO | `output/rdd_bolsa/outcomes/outcomes_V_celula.parquet` | `{"descritiva": "C3_CAND1"}` | `int` | ciclo 3: candidatos com 1ª opção numa célula do quadro |
| `D_C3_PRE1` | 497 | EMPIRICO | `output/rdd_bolsa/outcomes/outcomes_V_celula.parquet` | `{"descritiva": "C3_PRE1"}` | `int` | ciclo 3: células com alguma confirmação ou homologação na 1ª chamada |
| `D_C3_PRE1_PCT` | 21,7 | EMPIRICO | `output/rdd_bolsa/outcomes/outcomes_V_celula.parquet` | `{"descritiva": "C3_PRE1_PCT"}` | `pct1` | ciclo 3: fração de células preenchidas na 1ª chamada (%) |
| `D_C3_F3` | 276 | EMPIRICO | `output/rdd_bolsa/outcomes/outcomes_V_celula.parquet` | `{"descritiva": "C3_F3"}` | `int` | ciclo 3: municípios na faixa de R$ 10 mil (IVS até 0,300) pela grade aplicada |
| `D_C3_F2` | 180 | EMPIRICO | `output/rdd_bolsa/outcomes/outcomes_V_celula.parquet` | `{"descritiva": "C3_F2"}` | `int` | ciclo 3: municípios na faixa de R$ 15 mil (IVS de 0,301 a 0,400) |
| `D_C3_F1` | 291 | EMPIRICO | `output/rdd_bolsa/outcomes/outcomes_V_celula.parquet` | `{"descritiva": "C3_F1"}` | `int` | ciclo 3: municípios na faixa de R$ 20 mil (IVS acima de 0,400) |
| `D_C1_PRE2` | 461 | EMPIRICO | `output/rdd_bolsa/outcomes/outcomes_V_celula.parquet` | `{"descritiva": "C1_PRE2"}` | `int` | ciclo 1: células com alguma confirmação ou homologação até a 2ª chamada |
| `D_C1_PRE2_PCT` | 35,6 | EMPIRICO | `output/rdd_bolsa/outcomes/outcomes_V_celula.parquet` | `{"descritiva": "C1_PRE2_PCT"}` | `pct1` | ciclo 1: fração de células preenchidas até a 2ª chamada (%) |
| `D_C2_PRE2` | 867 | EMPIRICO | `output/rdd_bolsa/outcomes/outcomes_V_celula.parquet` | `{"descritiva": "C2_PRE2"}` | `int` | ciclo 2: células com alguma confirmação ou homologação até a 2ª chamada |
| `D_C2_PRE2_PCT` | 56,0 | EMPIRICO | `output/rdd_bolsa/outcomes/outcomes_V_celula.parquet` | `{"descritiva": "C2_PRE2_PCT"}` | `pct1` | ciclo 2: fração de células preenchidas até a 2ª chamada (%) |
| `D_C3_SEM_IVS` | 1 | EMPIRICO | `output/rdd_bolsa/outcomes/outcomes_V_celula.parquet` | `{"descritiva": "C3_SEM_IVS"}` | `int` | ciclo 3: municípios com célula e sem IVS 2010 (criados depois de 2010) |
| `D_C1_CANDG1` | 993 | EMPIRICO | `output/rdd_bolsa/G1_resumo.json` | `{"caminho": ["taxas_ligacao", "g1_cpf_nome", "1", "candidatos"]}` | `int` | ciclo 1: candidatos no portão G1 |
| `D_C1_LIG` | 938 | EMPIRICO | `output/rdd_bolsa/G1_resumo.json` | `{"caminho": ["taxas_ligacao", "g1_cpf_nome", "1", "ligados"]}` | `int` | ciclo 1: candidatos ligados a um profissional do CNES (G1) |
| `D_C2_CANDG1` | 2.179 | EMPIRICO | `output/rdd_bolsa/G1_resumo.json` | `{"caminho": ["taxas_ligacao", "g1_cpf_nome", "2", "candidatos"]}` | `int` | ciclo 2: candidatos no portão G1 |
| `D_C2_LIG` | 2.102 | EMPIRICO | `output/rdd_bolsa/G1_resumo.json` | `{"caminho": ["taxas_ligacao", "g1_cpf_nome", "2", "ligados"]}` | `int` | ciclo 2: candidatos ligados a um profissional do CNES (G1) |
| `D_C3_CANDG1` | 2.604 | EMPIRICO | `output/rdd_bolsa/G1_resumo.json` | `{"caminho": ["taxas_ligacao", "g1_cpf_nome", "3", "candidatos"]}` | `int` | ciclo 3: candidatos no portão G1 |
| `D_C3_LIG` | 2.533 | EMPIRICO | `output/rdd_bolsa/G1_resumo.json` | `{"caminho": ["taxas_ligacao", "g1_cpf_nome", "3", "ligados"]}` | `int` | ciclo 3: candidatos ligados a um profissional do CNES (G1) |
| `D_C1_P1` | 915 | EMPIRICO | `output/rdd_bolsa/P1_resumo.json` | `{"caminho": ["amostra", "p1_por_ciclo", "1"]}` | `int` | ciclo 1: amostra da escolha (P1): 1ª opção numa célula, ligado ao CNES e com município de origem |
| `D_C2_P1` | 2.032 | EMPIRICO | `output/rdd_bolsa/P1_resumo.json` | `{"caminho": ["amostra", "p1_por_ciclo", "2"]}` | `int` | ciclo 2: amostra da escolha (P1): 1ª opção numa célula, ligado ao CNES e com município de origem |
| `D_C3_P1` | 2.474 | EMPIRICO | `output/rdd_bolsa/P1_resumo.json` | `{"caminho": ["amostra", "p1_por_ciclo", "3"]}` | `int` | ciclo 3: amostra da escolha (P1): 1ª opção numa célula, ligado ao CNES e com município de origem |
| `D_IVS_MUN` | 5.565 | EMPIRICO | `output/aquisicao/a08_ivs_2010_oficial_municipio.csv` | `{"descritiva": "IVS_MUN"}` | `int` | municípios com IVS 2010 oficial (a08) |
| `D_POP_MUN` | 5.570 | EMPIRICO | `output/aquisicao/populacao_censo2022_municipios.csv` | `{"descritiva": "POP_MUN"}` | `int` | municípios com população do Censo 2022 |
| `D_ATIVOS` | 1.957 | EMPIRICO | `output/aquisicao/cnes_profissional/a16_manifesto_cnes_profissional.json` | `{"caminho": ["listas_pmme", "registros_ativos_2026_09_11"]}` | `int` | registros na lista de especialistas ativos do PMM-E de 11/09/2026 |
| `FM_NMU` | 4.362 | FAILURE_MODE | `output/rdd_bolsa/identificacao_arquivo_local_ivs.json` | `{"caminho": ["mecanismo", "linha_escolhida_por_municipio", "Negro / Mulher / Urbano"]}` | `int` | municípios em que o arquivo errado traz a linha Negro / Mulher / Urbano |
| `FM_MUN` | 5.565 | FAILURE_MODE | `output/rdd_bolsa/identificacao_arquivo_local_ivs.json` | `{"caminho": ["mecanismo", "conferencia_por_coluna", "municipios"]}` | `int` | municípios do arquivo |
| `FM_NMU_PCT` | 78 | FAILURE_MODE | calculado por este script | `{"razao": ["FM_NMU", "FM_MUN"]}` | `pct0` | FM_NMU / FM_MUN (%) |
| `FM_IGUAIS` | 38 | FAILURE_MODE | `output/tema_trabalho/failure_mode_ivs_resumo.json` | `{"caminho": ["arquivo_errado", "ivs_igual_3_casas"]}` | `int` | municípios em que o arquivo errado acerta o IVS oficial a 3 casas |
| `FM_CORR` | 0,85 | FAILURE_MODE | `output/tema_trabalho/failure_mode_ivs_resumo.json` | `{"caminho": ["arquivo_errado", "correlacao_ivs"]}` | `d2` | correlação entre o arquivo errado e o IVS oficial |
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
| cortes 0,300 e 0,400 (e 0,3 e 0,4 no texto dos atos); limite 0,301 da faixa do meio | regra da bolsa; protocolo 40, §3 |
| h = 0,050; sensibilidades 0,030 e 0,080 | protocolo 40, §6 |
| bolsas de R$ 10, 15 e 20 mil; degrau de R$ 5 mil; R$ 1 mil como unidade do coeficiente | editais; protocolo 40, §3; protocolo 52 |
| referências +10 p.p. e +25% | protocolo 40, §7 |
| IC 95%, α = 0,05, valor crítico 1,96, limiar p < 0,001, MDE de 80%, M̄ = 1 | convenções de relato |
| ciclos 1, 2 e 3; chamadas 1ª e 2ª; "3 casas" decimais | desenho |
| anos, datas, competências (`2025-10`, `202703`), números de atos (`752/2023`), seções (§), documentos, protocolos e códigos de outcome (F1.3, N1, Y1, M5, H1–H4) | nomes, não números |
| números de slide do deck do grupo (até 36), nos quadros do doc 02 | posição, não resultado |

## 4. Entradas lidas pelo gerador de figuras

Com SHA-256 no manifesto. O arquivo de IVS errado (`data/`) **não é mais
lido**: a figura e os números do failure mode que dependiam dele não são
regenerados.

| Arquivo | Papel |
|---|---|
| `output/rdd_bolsa/S57_resumo.json` | síntese vigente (doc 57): valores com arquivo e seletor de origem |
| `output/rdd_bolsa/N_estimativas.csv` | família N (protocolo 48): N1 com e sem controle, robustez |
| `output/rdd_bolsa/P1_estimativas.csv` | P1 (protocolo 52): M1, M5 por ciclo, M0–M9 |
| `output/rdd_bolsa/H_estimativas.csv` | Rambachan–Roth do P4 (protocolo 59, parte A) |
| `output/rdd_bolsa/CA_estimativas.csv` | comparação na nota de corte (protocolo 59, parte B) |
| `output/rdd_bolsa/G1_resumo.json` | candidatos ligados ao CNES, por ciclo |
| `output/aquisicao/cnes_profissional/a16_manifesto_cnes_profissional.json` | lista de ativos do PMM-E |
| `output/rdd_bolsa/outcomes/outcomes_V_celula.parquet` | quadro de células da 1ª chamada (descritivas) |
| `output/aquisicao/populacao_censo2022_municipios.csv` | cobertura da tabela de fontes |
| `output/rdd_bolsa/E8_resumo.json` | síntese E8: Holm, descarte, E9, E7, seleção, famílias, degrau, literatura |
| `output/rdd_bolsa/E8_tabela_sintese.csv` | tabela-síntese por elo (figuras de 19/10) |
| `output/rdd_bolsa/E3_estimativas.csv` | municípios por lado na âncora do E3 |
| `output/rdd_bolsa/portao_r1_ivs_oficial.json` | reprodução da regra com o IVS oficial |
| `output/rdd_bolsa/identificacao_arquivo_local_ivs.json` | mecanismo do arquivo errado (só failure mode) |
| `output/tema_trabalho/failure_mode_ivs_resumo.json` | registro do failure mode (auditoria 19) |
| `output/rdd_bolsa/matriz_municipio_escore_administrativo.csv` | faixa anunciada por município |
| `output/aquisicao/a08_ivs_2010_oficial_municipio.csv` | running variable |
| `docs/auditorias/18_politicas_nos_mesmos_cortes_ivs.md` | parâmetros normativos das co-políticas |
| `scripts/rdd_bolsa/10_galeria_figura_regra.py` | código da variante A colorida |
| `output/rdd_bolsa/P1h_magnitudes.csv` | H3 (P1h, protocolo 52b): D_UF, km equivalentes, sensibilidades e pesos |
| `output/rdd_bolsa/P1h_resumo.json` | H3: estatuto do bloco e hashes das saídas auditadas |
| `output/rdd_bolsa/P1h_figuras/P1h_magnitudes.png` | H3: figura auditada (só o hash é conferido) |

## 5. Deck

`scripts/apresentacao/gerar_deck_banca2.py` lê o deck do grupo (caminho em
`PMME_DECK_GRUPO` ou `--deck`; só leitura), o doc 02 e `numeros_banca2.json`,
e grava em `output/apresentacao_banca2/`:

| Arquivo | O que é |
|---|---|
| `deck_banca2_proposta.pptx` | o deck inteiro, com as correções do quadro do doc 02 e os slides novos no lugar dos marcadores "X" |
| `slides_empiricos_banca2.pptx` | só os slides novos, para colar no deck em uso |
| `manifesto_deck_banca2.json` | entradas (deck do grupo, doc 02, registro, figuras) e saídas com SHA-256; ordem dos slides; correções aplicadas |
| `qa_render/` | imagens de conferência dos slides novos e corrigidos (LibreOffice, com a Montserrat instalada) |

O texto dos slides novos é o do doc 02; os números das correções no deck do
grupo vêm do registro. As figuras entram como imagem, a partir de `output/`;
as tabelas, como tabela nativa. O zip é gravado com data fixa e ordem
estável, e duas execuções dão o mesmo SHA-256.

## 6. Pendências e ressalvas

1. **H3.** Entrou com o P1h auditado (doc 57i; auditoria 31, aprovado com
   correções de rótulo). O teste é pós-resultado: os coeficientes do M1 já
   eram conhecidos quando o protocolo 52b foi congelado. O IC do km contém
   zero, e o limite unilateral dele não é usado como evidência de que a bolsa
   importa. O logit misto e o aninhado ficaram fora do P1h (doc 57i, §7).
2. **`run_all.py`.** Os dois geradores não estão no pipeline ponta a ponta; a
   inclusão fica para o coordenador.
3. **PNG da regra.** Depende do Chromium headless; sem ele o script grava só o
   SVG e registra `png_gerado: false` no manifesto.
4. **Texto citado.** Os números de atos e de literatura são conferidos pela
   presença do trecho no texto-fonte, não contra o ato ou o artigo originais;
   a conferência desses está na auditoria 18 e no doc 20 da seção 03.
5. **Figura do failure mode.** Congelada (ver `G8`); não entra no deck.

## 7. Reprodução

```bash
python3 scripts/apresentacao/gerar_figuras_banca2.py
PMME_DECK_GRUPO="<deck do grupo>" python3 scripts/apresentacao/gerar_deck_banca2.py
PMME_DECK_GRUPO="<deck do grupo>" python3 -m unittest tests.test_conteudo_banca2
```
