# 00. Registro de mudanças da documentação

> **Finalidade:** rastrear alterações **estruturais** da documentação — arquivo
> criado, fundido, removido, renomeado ou movido — e o motivo de cada uma.<br>
> **Não registra:** correção de texto, atualização de número ou acréscimo de
> seção dentro de um documento que permaneceu no mesmo lugar.<br>
> **Regra:** quem move informação de lugar abre entrada aqui no mesmo commit.

---

## 19/10/2026 — Aquisições do adendo §12 do protocolo 47: safras v2 do SIH e do SIA (§12.1) e a17 (§12.2)

Motivo: o adendo §12 do protocolo
[`06_execucao/47`](06_execucao/47_protocolo_producao_especializada.md) pede uma
segunda safra do SIH e do SIA, por causa da revisão da fonte vista no A15 §5, e a
produção ambulatorial por forma de organização dos cursos "específico" do G4
(T3.2). É só aquisição e validação: nada foi calculado por IVS, lado de corte,
tratamento ou chegada, e nada foi estimado.

### Criado

| Arquivo | O que é |
|---|---|
| [`auditorias/aquisicao/A12b_A13b_safras_v2.md`](auditorias/aquisicao/A12b_A13b_safras_v2.md) | safras v2 do SIH (202201–202607) e do SIA (202509–202607): como foram feitas, comparação com a v1 (SIH revisto em 202509–202607; SIA sem revisão), limites |
| [`auditorias/aquisicao/A17_sia_forma_curso.md`](auditorias/aquisicao/A17_sia_forma_curso.md) | aquisição a17: SIA por município × mês × forma de organização × curso "específico", consultas, regras de zero e ausência, validações, cobertura e limites |

Mudanças fora de `docs/`:
- `scripts/aquisicao/a12b_safra_v2_sia.py` e `a13b_safra_v2_sih.py` (embrulhos do
  a12 e do a13; o a12 e o a13 não mudaram) e saídas em `output/aquisicao/sia_v2/`
  e `output/aquisicao/sih_v2/`;
- `scripts/aquisicao/a17_adquirir_sia_forma_curso.py` e saídas em
  `output/aquisicao/sia_forma_curso/`;
- caches brutos dos três no `.gitignore`;
- `run_all.py`: a12b, a13b e a17 em `--etapa verificar`, fora do `--rdd-bolsa`;
  manifesto A6 regenerado pelo gerador;
- testes `tests/test_aquisicao_safras_v2.py` e
  `tests/test_aquisicao_sia_forma_curso.py`; `tests/test_pipeline_rdd_bolsa.py`
  atualizado;
- `scripts/README.md`, `tests/README.md` e o inventário
  [`04_dados/02`](04_dados/02_inventario_dados_por_outcome.md).

## 19/10/2026 — Auditoria 23: P5 (protocolo 55), aprovado com correções

Motivo: auditoria independente do P5 (commit `89c0eef`). Bases, T5.1, T5.2,
BKY e T5.3 foram reproduzidos com código próprio, e nenhuma estimativa mudou.
As correções são de relato:
- nota e marca † no termo CAPS da sensibilidade, idêntico ao curso 17;
- leitura com todas as associações que excluem zero e com o T5.2b;
- desvios 6 e 7 declarados (células pedidas fora do cardápio no E2; amostra do
  T5.2b por célula);
- linguagem sem verbo de mudança;
- rótulos e legenda das figuras.

### Criado

| Arquivo | O que é |
|---|---|
| [`auditorias/23_auditoria_P5_abertura.md`](auditorias/23_auditoria_P5_abertura.md) | auditoria do P5: recálculo, achados C1–C5, julgamento dos desvios e números principais |

Mudanças fora de `docs/`:
- `scripts/rdd_bolsa/29_determinantes_abertura.py`, reexecutado; as saídas
  `P5_*` são byte a byte iguais entre duas execuções;
- `scripts/rdd_bolsa/23_estimar_contagem_vagas.py`: `desenhar` ganhou
  `legenda_salto` e `legenda_fora`, com padrões que mantêm as figuras N, NA e
  K;
- `tests/test_P5_abertura.py`, que passou de 27 para 36 testes, com a classe
  `TestRecalculoIndependenteAuditoria23`, e `tests/README.md`, agora com 1.065
  testes em 58 módulos. Rodados módulo a módulo: 1.063 passaram e 2 foram
  pulados;
- o link no [`README.md`](README.md) de `docs/` e a linha de auditoria no
  [doc 57e](06_execucao/57e_resultados_P5_abertura.md).

## 19/10/2026 — Resultados do P5 (protocolo 55): determinantes da abertura e da priorização

Motivo: onda 3 do plano do doc 51 (agente E-P5). Estima o protocolo 55, congelado
antes: T5.1 (logit do pedido e da priorização do ciclo 3, efeitos marginais e
contribuição de blocos), T5.2 (RDD nos cortes, pacote) e T5.3 (Poisson do quadro
dos ciclos 1 e 2). T5.1 e T5.3 são descritivos.

### Criado

| Arquivo | O que é |
|---|---|
| [`06_execucao/57e_resultados_P5_abertura.md`](06_execucao/57e_resultados_P5_abertura.md) | resultados do P5, com os números gerados pelo script entre marcadores; é a seção P5 que o §5 do protocolo 55 manda pôr no doc 57 (síntese da onda 5) |

Mudanças fora de `docs/`:
- `scripts/rdd_bolsa/29_determinantes_abertura.py`, no `run_all.py` logo depois
  do 24 (o manifesto A6 foi regerado pelo gerador);
- saídas `output/rdd_bolsa/P5_estimativas.csv`, `P5_resumo.json` e
  `P5_figuras/`;
- `tests/test_P5_abertura.py`, `tests/test_pipeline_rdd_bolsa.py` e
  `tests/README.md`.

## 19/10/2026 — Protocolos 54 (P4) e 56 (P6)

Motivo: execução do plano do doc 51 depois do portão G5. Os protocolos foram
congelados antes de abrir o painel CNES por tempo de evento e antes de ligar os
candidatos aos outcomes.

### Criado

| Arquivo | O que é |
|---|---|
| [`06_execucao/54_protocolo_P4_oferta_substituicao.md`](06_execucao/54_protocolo_P4_oferta_substituicao.md) | P4: trajetória das horas cadastradas dos médicos do PMM-E ao redor da entrada, por origem; perdas na origem; contabilidade líquida (exploratório) |
| [`06_execucao/56_protocolo_P6_mecanismo_alocacao.md`](06_execucao/56_protocolo_P6_mecanismo_alocacao.md) | P6: alocado por pouco contra não alocado por pouco, perto da nota de corte de cada célula, com as restrições do G2 (capacidade efetiva, desempate fixo, cotas) (exploratório) |

## 19/10/2026 — Portão G5: CNES profissional mensal (a16)

Motivo: portão de viabilidade G5 do plano
[`06_execucao/51`](06_execucao/51_plano_perguntas_reformuladas.md) (T4.0,
insumo de P4 e de T6.2). Verifica se o CNES público traz o registro do
conselho por vínculo e monta o painel médico × mês (202406–202608) dos
médicos do PMM-E ligados na X1, com chave pseudônima pronta para receber as
chaves do G1. Nenhum contraste foi calculado.

### Criado

| Arquivo | O que é |
|---|---|
| [`auditorias/aquisicao/A16_cnes_profissional.md`](auditorias/aquisicao/A16_cnes_profissional.md) | fonte, tabelas, chave pseudônima, cobertura, estabilidade da chave, critérios e veredito do G5; o que P4 e T6.2 podem usar |

Mudanças fora de `docs/`:
- `scripts/aquisicao/a16_cnes_profissional_mensal.py` (etapas `verificar`,
  `baixar`, `consolidar`, `tudo`);
- saídas em `output/aquisicao/cnes_profissional/` (painéis, chaves,
  cobertura, resumo e manifesto) e `output/rdd_bolsa/G5_resumo.json`;
- cache privado `output/aquisicao/cnes_profissional/cache_privado/`, fora do
  controle de versão (entrada nova no arquivo de exclusões);
- `run_all.py`: a16 em `--etapa verificar`; `tests/test_pipeline_rdd_bolsa.py`;
  manifesto A6 regenerado pelo gerador;
- `tests/test_aquisicao_cnes_profissional.py` e `tests/README.md`;
- inventário [`04_dados/02`](04_dados/02_inventario_dados_por_outcome.md),
  seção 1.1.

## 19/10/2026 — Protocolos 52 (P1) e 55 (P5); adendo §12 do protocolo 47 (P3)

Motivo: execução do plano do doc 51, depois dos portões G1–G4. Os protocolos
foram congelados antes de qualquer estimação.

### Criado

| Arquivo | O que é |
|---|---|
| [`06_execucao/52_protocolo_P1_escolha_dap.md`](06_execucao/52_protocolo_P1_escolha_dap.md) | P1: elasticidade da escolha à bolsa, disposição a pagar por distância e atributos, ciclos, heterogeneidade, logit misto, ponte com o preenchimento |
| [`06_execucao/55_protocolo_P5_abertura_vagas.md`](06_execucao/55_protocolo_P5_abertura_vagas.md) | P5: determinantes descritivos do pedido e da priorização (ciclo 3) e do quadro (ciclos 1–2); RDD nos cortes |

O protocolo 47 ganhou o adendo §12 (revisão da SIH, produção por especialidade,
controles alternativos, acesso dos residentes, transbordamento regional). O doc
51 ganhou a §8 com os vereditos dos portões.

## 19/10/2026 — Portão G1: candidatos do PMM-E ligados ao CNES pré (onda 1 do doc 51)

Motivo: o portão G1 do plano
[`06_execucao/51`](06_execucao/51_plano_perguntas_reformuladas.md) (§5, onda 1;
T1.0) verifica se os arquivos públicos de classificação e resultado
identificam todos os candidatos da 1ª chamada dos ciclos 1–3 e se essa
identificação liga cada um ao CNES antes do programa. É só viabilidade: nenhum
contraste por IVS, faixa, alocação ou outcome.

### Criado

| Arquivo | O que é |
|---|---|
| [`auditorias/G1_viabilidade_candidatos.md`](auditorias/G1_viabilidade_candidatos.md) | inventário dos identificadores, regra de ligação (CPF mascarado + nome; a regra da X1 por CRM vira validação), taxas por ciclo e por alocação, cobertura de origem e distância, veredito e o que os protocolos 52 (P1) e 56 (P6) podem usar |

Mudanças fora de `docs/`:
- `scripts/rdd_bolsa/G1_identificar_candidatos.py` (fora do `run_all.py` por
  enquanto);
- saídas `output/rdd_bolsa/G1_resumo.json`, `G1_candidatos_origem.parquet`,
  `G1_distancias_opcoes.parquet` e `G1_inventario_identificadores.csv`;
- `.gitignore`: `output/rdd_bolsa/G1_cache/` (ZIP transitório do CNES 202602 e
  dicionário com nome normalizado e chave do CPF em hash);
- `tests/test_G1.py` e `tests/README.md`.

## 19/10/2026 — Portões G3 e G4 do plano 51 (SIH por residência; mapa especialidade → procedimento)

Motivo: onda 1 do plano das perguntas reformuladas
([`06_execucao/51`](06_execucao/51_plano_perguntas_reformuladas.md)), P3. O G3
adquire a SIH por município de residência (a15) e libera o T3.4. O G4 monta o
mapa curso → formas de organização e testa o filtro de CBO no TabNet do SIA, que
o T3.2 exige. São só portões: nada foi calculado por IVS, lado de corte,
tratamento ou chegada.

### Criado

| Arquivo | O que é |
|---|---|
| [`auditorias/aquisicao/A15_sih_residencia.md`](auditorias/aquisicao/A15_sih_residencia.md) | aquisição a15: fonte, consultas, ausências (residência zerada e arquivo de internação ausente), conferência com o a13 e a revisão de 202606–202607 na fonte, validações, limites e veredito do G3 |
| [`auditorias/G4_viabilidade_especialidade.md`](auditorias/G4_viabilidade_especialidade.md) | portão G4: sondagem do SIGTAP (download indisponível, FTP inalcançável), mapa revelado pela produção de 2024, classes dos cursos, teste do filtro e veredito |

Mudanças fora de `docs/`:
- `scripts/aquisicao/a15_adquirir_sih_residencia.py` e saídas em
  `output/aquisicao/sih_residencia/` (cache bruto fora do controle de versão);
- `scripts/aquisicao/g4_mapa_especialidade_procedimento.py` e saídas em
  `output/aquisicao/sigtap/` (cache bruto fora do controle de versão) e
  `output/rdd_bolsa/G4_*`;
- `run_all.py`: a15 em `--etapa verificar`, depois do a13; manifesto A6
  regenerado pelo gerador;
- testes `tests/test_aquisicao_sih_residencia.py` e
  `tests/test_g4_mapa_especialidade.py`; `tests/test_pipeline_rdd_bolsa.py`
  atualizado;
- `.gitignore`, `scripts/README.md`, `tests/README.md` e o inventário
  [`04_dados/02`](04_dados/02_inventario_dados_por_outcome.md).

## 19/10/2026 — Portão G2: replicação do mecanismo de alocação (P6, T6.0 do doc 51)

Motivo: portão de viabilidade da onda 1 do doc
[`06_execucao/51`](06_execucao/51_plano_perguntas_reformuladas.md). Verifica se
a alocação publicada da 1ª chamada dos ciclos 1–3 (e da 2ª chamada dos ciclos
1 e 2) é reconstruída a partir das escolhas, notas, elegibilidade e vagas. Não
abre outcome: nada de CNES, produção, IVS ou faixa foi lido. Veredito
`VIAVEL_PARCIAL`: ≥ 99% em todos os ciclos com a capacidade efetiva ex post e a
classificação publicada como desempate; ex ante só no ciclo 2.

### Criado

| Arquivo | O que é |
|---|---|
| [`auditorias/G2_viabilidade_mecanismo.md`](auditorias/G2_viabilidade_mecanismo.md) | relatório do portão G2, gerado pelo script: mecanismo dos editais, concordância por ciclo e chamada, divergências, cortes e margens (contagens), veredito |

Mudanças fora de `docs/`:
- `scripts/rdd_bolsa/G2_mecanismo_alocacao.py` (novo; fora do `run_all.py`);
- saídas novas `output/rdd_bolsa/G2_alocacao_reconstruida.parquet`,
  `G2_cortes_celula.csv` e `G2_resumo.json`;
- `tests/test_G2.py` (novo) e `tests/README.md`.

O `docs/README.md` passa a apontar para o relatório.

## 19/10/2026 — Auditoria independente do adendo §7 do protocolo 48 (auditoria 22)

Motivo: auditoria independente do commit `738a706`, que tem o script 24, as
saídas `NA_*`, a seção 15 do doc 49, a correção §8 do protocolo
[`06_execucao/48`](06_execucao/48_protocolo_contagem_vagas_preenchidas.md) e os
testes. Veredito: aprovado com correções. Das linhas de `NA_estimativas.csv`,
mudam só as 12 `A2_EXTENSIVA`, porque o aparo de empates passou a ser
proporcional.

### Criado

| Arquivo | O que é |
|---|---|
| [`auditorias/22_auditoria_abertura_vagas_NA.md`](auditorias/22_auditoria_abertura_vagas_NA.md) | recálculo independente de A1–A4 e do bootstrap do A2; achados e correções C1–C4; conferência das fontes do §8 |

Mudanças fora de `docs/`:
- `scripts/rdd_bolsa/rdd_lib.py`: opção `empates` no aparo de Lee, com o
  padrão antigo mantido;
- `scripts/rdd_bolsa/23_estimar_contagem_vagas.py`: opções de `desenhar`, com
  padrões que reproduzem as figuras N byte a byte;
- `scripts/rdd_bolsa/24_abertura_vagas_selecao.py`:
  - empates proporcionais no Lee extensivo;
  - regras da leitura conjunta;
  - ausente que não vira zero;
  - figuras;
- saídas `output/rdd_bolsa/NA_*` regeneradas pelo script;
- `tests/test_abertura_vagas.py`, com o recálculo independente versionado, e
  `tests/test_rdd_lib.py`.

O doc 49, seção 15, ganhou prosa sobre empates e sobre a variante ponderada
pela população, e os blocos foram regenerados. O `docs/README.md` e o doc 38
apontam para a auditoria.

## 19/10/2026 — Auditoria independente da família K (auditoria 21)

Motivo: auditoria do commit `1c35900` (doc 50, scripts 21 e 22) com código
próprio. Veredito: aprovado com correções. O D1 não muda. O D2 passa a tratar
como ainda não tratados os municípios cuja 1ª chegada é posterior ao fim da
série. As figuras foram refeitas, e o teste de integridade de rótulos foi
corrigido para não estourar a memória.

### Criado

| Arquivo | O que é |
|---|---|
| [`auditorias/21_auditoria_producao_K.md`](auditorias/21_auditoria_producao_K.md) | achados, tabela de recálculo independente (outcomes, D1, D2), correções e observações para o autor |

Fora de `docs/`, foram alterados:
- `scripts/rdd_bolsa/21_producao_dird.py`: figuras e frase gerada do estudo de
  evento;
- `22_chegada_pmme_evento.py`: data de tratamento, leituras geradas e figuras;
- `23_estimar_contagem_vagas.py`: opção `rotulo_salto`, com o padrão
  inalterado;
- `tests/test_producao_K.py` e `tests/test_integridade_dados.py`;
- as saídas `K_D1_figuras/`, `K_D2_*` e as tabelas geradas do doc 50.

---

## 19/10/2026 — Resultados da família K: produção especializada (doc 50)

Motivo: execução do protocolo
[`06_execucao/47`](06_execucao/47_protocolo_producao_especializada.md), com os
adendos §10 e §11 (pedido do autor: produção de consultas, exames e cirurgias
que exigem especialista, no SUS e no SUS + planos). Estatuto posterior à
síntese E8; Holm próprio (K1–K3); nada altera o protocolo 40, o Holm de P1 e P2
nem os docs 41–49.

### Criado

| Arquivo | O que é |
|---|---|
| [`06_execucao/50_resultados_producao_especializada.md`](06_execucao/50_resultados_producao_especializada.md) | D1 (DiRD nos cortes da bolsa: K1–K3 com Holm, secundárias com BKY, placebos KP1–KP3, robustez dos §10–§11, IC honesto, Poisson, S2–S5, estudo de evento) e D2 exploratório (chegada do especialista, Callaway–Sant'Anna, pré-tendência, sensibilidade, dose), leitura de substituição do §5, figuras com guia de leitura; tabelas e frases geradas pelos scripts |

Insumos novos fora de `docs/`: `scripts/rdd_bolsa/21_producao_dird.py` e
`22_chegada_pmme_evento.py`, saídas `output/rdd_bolsa/K_D1_*` e `K_D2_*`
(com `K_D1_figuras/` e `K_D2_figuras/`) e `tests/test_producao_K.py`. O
`run_all.py` roda o 21 e o 22 logo depois do E7 (14); o manifesto A6 foi
regerado pelo seu gerador.

## 19/10/2026 — Plano das perguntas reformuladas (doc 51)

Motivo: pedido do autor de planejar tudo o que deveríamos e poderíamos rodar
para as perguntas que saíram da teoria da mudança do programa (escolha, preenchimento dada a
vaga aberta, produção, substituição, abertura de vagas e mecanismo de
alocação), com execução em ondas de subagentes.

### Criado

| Arquivo | O que é |
|---|---|
| [`06_execucao/51_plano_perguntas_reformuladas.md`](06_execucao/51_plano_perguntas_reformuladas.md) | plano P1–P6: tarefas, portões de viabilidade G1–G5, protocolos 52–56, ondas de execução, auditorias e síntese (doc 57) |

## 19/10/2026 — Auditoria independente da família N (auditoria 20)

Motivo: auditoria independente do commit `c47380e`, que tem o script 23, as
saídas `N_*`, o doc 49 e os testes, contra o protocolo
[`06_execucao/48`](06_execucao/48_protocolo_contagem_vagas_preenchidas.md).
Veredito: aprovado com correções. As linhas originais de `N_estimativas.csv`
não mudam.

### Criado

| Arquivo | O que é |
|---|---|
| [`auditorias/20_auditoria_contagem_vagas_N.md`](auditorias/20_auditoria_contagem_vagas_N.md) | recálculo independente (statsmodels, a partir do parquet) de S-a, S-b, S-c, decomposição, Holm, IC honesto e Poisson empilhado; julgamento dos desvios; achados e correções C1–C5 |

Mudanças fora de `docs/`:
- `scripts/rdd_bolsa/23_estimar_contagem_vagas.py`:
  - variante de coeficiente único, fora do protocolo, com o Wald;
  - linhas NAO_EXECUTADO para S-h e S-i empilhados;
  - figuras sem sobreposição;
- saídas `output/rdd_bolsa/N_*` regeneradas pelo script;
- `tests/test_contagem_vagas.py`: recálculo independente versionado.

O doc 49 ganhou a tabela de sensibilidade, gerada pelo script, e a prosa dos
motivos (ii) e (iv) foi corrigida. O `docs/README.md` e o doc 38 apontam para a
auditoria.

## 19/10/2026 — Resultados da família N: contagem de vagas preenchidas (doc 49)

Motivo: execução do protocolo
[`06_execucao/48`](06_execucao/48_protocolo_contagem_vagas_preenchidas.md)
(diretriz do autor: número de vagas preenchidas, controlando pelas vagas
oferecidas). Estatuto pós-resultado; nada altera o protocolo 40, o Holm de P1 e
P2 nem os docs 41–46.

### Criado

| Arquivo | O que é |
|---|---|
| [`06_execucao/49_resultados_contagem_vagas_preenchidas.md`](06_execucao/49_resultados_contagem_vagas_preenchidas.md) | resultados de N1–N4 (S-a a S-j), verificação do cadastro reserva e escolha do controle, S-c (oferta como outcome), decomposição total = oferta + preenchimento, Holm das quatro linhas empilhadas, figuras com guia de leitura; tabelas geradas pelo script |

Insumos novos fora de `docs/`: `scripts/rdd_bolsa/23_estimar_contagem_vagas.py`,
saídas `output/rdd_bolsa/N_estimativas.csv`, `N_resumo.json` e `N_figuras/`, e
`tests/test_contagem_vagas.py`. O `run_all.py` roda o 23 logo depois do E6 (13).

## 19/10/2026 — Aquisição TISS/ANS para a família K (a14)

Motivo: o protocolo
[`06_execucao/47`](06_execucao/47_protocolo_producao_especializada.md) (§2, §9)
pede a produção paga por planos de saúde (dados abertos TISS da ANS) por
município do prestador, mês, tipo de procedimento e grupo de CBO, para K3,
K3a, K3b e K5. Só aquisição: nada calculado por IVS, corte ou tratamento.

### Criado

| Arquivo | O que é |
|---|---|
| [`auditorias/aquisicao/A14_tiss_ans.md`](auditorias/aquisicao/A14_tiss_ans.md) | fonte, dicionário, unidade, chaves, filtros, grupos de CBO (importados do a09), regra TUSS dos tipos, cobertura (zero × ausente), validações, limites e pressupostos do protocolo que falharam |

Insumos e scripts novos: `scripts/aquisicao/a14_adquirir_tiss_ans.py`,
`tests/test_aquisicao_tiss.py` e `output/aquisicao/tiss/` (painéis, manifesto,
cobertura, validação e resumo gerado). O `run_all.py` roda o a14 só em
`--etapa verificar`.

## 19/10/2026 — Aquisição SIA/SUS pelo TabNet (a12, protocolo 47)

Motivo: primeira aquisição da família K do protocolo
[`47`](06_execucao/47_protocolo_producao_especializada.md): produção
ambulatorial aprovada pelo SUS por município de atendimento, mês de
processamento, subgrupo e conjunto de CBO do profissional executante. Só
aquisição e validação; nada por IVS, faixa ou lado de corte.

### Criado

| Arquivo | O que é |
|---|---|
| [`auditorias/aquisicao/A12_sia_tabnet.md`](auditorias/aquisicao/A12_sia_tabnet.md) | auditoria da aquisição: fonte, consultas, conjuntos de CBO, chaves, regras de zero e ausência, validações, cobertura e limites |
| `scripts/aquisicao/a12_adquirir_sia_tabnet.py` | aquisição (`--etapa verificar` padrão, `baixar`, `consolidar`, `tudo`) |
| `output/aquisicao/sia/` | painel, tabelas de validação, manifesto e resumo gerado (`a12_resumo.md`); respostas brutas em `brutos/`, fora do Git |
| `tests/test_aquisicao_sia.py` | testes do a12 |

O a12 entra no `run_all.py` em `--etapa verificar`, depois do a09, como o a09.
O inventário [`04_dados/02`](04_dados/02_inventario_dados_por_outcome.md) ganha
a linha do SIA.

## 19/10/2026 — Aquisição SIH/SUS no TabNet (a13, protocolo 47)

Motivo: o protocolo de produção especializada
([`06_execucao/47`](06_execucao/47_protocolo_producao_especializada.md), §9)
pede as AIH do SUS por município de internação e mês, insumo da primária K2
(cirurgias, grupo 04). Só aquisição: nada foi calculado por IVS ou corte.

### Criado

| Arquivo | O que é |
|---|---|
| [`auditorias/aquisicao/A13_sih_tabnet.md`](auditorias/aquisicao/A13_sih_tabnet.md) | fonte, consultas, conceito de tempo e lugar, chaves, filtros, validações, UF-mês sem dado e limites do painel SIH município × mês × grupo (`scripts/aquisicao/a13_adquirir_sih_tabnet.py`) |

Insumos novos fora de `docs/`: `scripts/aquisicao/a13_adquirir_sih_tabnet.py`,
saídas em `output/aquisicao/sih/` (cache bruto `cache_tabnet/` fora do Git) e
`tests/test_aquisicao_sih.py`. O `run_all.py` roda o a13 só em `--etapa verificar`.

## 19/10/2026 — Protocolo de contagem de vagas preenchidas (doc 48)

Motivo: diretriz do autor de trocar a variável de efeito da fração para o
número de vagas preenchidas, controlando pelas vagas oferecidas, e rodar tudo de
novo com prioridade. Os resultados da família K (doc 47) passam do doc 48 para o
doc 50.

### Criado

| Arquivo | O que é |
|---|---|
| [`06_execucao/48_protocolo_contagem_vagas_preenchidas.md`](06_execucao/48_protocolo_contagem_vagas_preenchidas.md) | protocolo da família N: vagas preenchidas com e sem controle pelas vagas oferecidas, decomposição, Poisson, ciclos 1–3, cortes e ciclos empilhados |

## 19/10/2026 — Protocolo de produção especializada (doc 47)

Motivo: pedido do autor de medir, como KPI central, consultas, exames e
cirurgias que exigem médico especialista, no SUS e no conjunto SUS + planos do
município. O protocolo foi congelado antes de baixar qualquer outcome.

### Criado

| Arquivo | O que é |
|---|---|
| [`06_execucao/47_protocolo_producao_especializada.md`](06_execucao/47_protocolo_producao_especializada.md) | protocolo da família K: SIA e SIH (TabNet) e TISS da ANS; DiRD nos cortes (D1) e chegada do especialista do PMM-E (D2, exploratório) |

## 19/10/2026 — Relatório curto de validação para os professores

Motivo: o autor precisa de um relatório de 10 a 15 páginas A4 para os professores validarem o desenho e os
resultados da RDD da bolsa obtidos até agora (E3 a E9, síntese E8, X1 a X3 e X6). É um derivado do relatório de 46
páginas (`output/rdd_bolsa/relatorio_resultados_rdd_bolsa.pdf`), que continua sendo a referência completa. A análise
de produção (SIA/SIH/TISS) não entra: ainda não rodou.

### Criado

| Arquivo | O que é |
|---|---|
| `scripts/apresentacao/gerar_relatorio_validacao_professores.py` | gera `output/apresentacao_validacao/relatorio_validacao_rdd_bolsa.html` e `.pdf` (A4, Chromium headless); reutiliza as funções do `scripts/rdd_bolsa/09_gerar_relatorio_pdf.py`; sem estimação nova, sem leitura de `data/`, sem data nem commit no HTML (saída determinística) |
| `tests/test_relatorio_validacao_professores.py` | HTML em dia, números rastreados a `output/`, código sem número digitado, nada de `data/`, figuras do pipeline, sinal e rótulos, PDF |
| `output/apresentacao_validacao/relatorio_validacao_rdd_bolsa.{html,pdf}` | o relatório |
| `scripts/apresentacao/gerar_figuras_validacao_professores.py` e `output/apresentacao_validacao/figuras_validacao_rdd_bolsa.{html,pdf}` | versão lean (7 páginas): tabela de resultados lida de `output/` (E3 e E7) antes das figuras, quatro figuras do relatório com guia de leitura e conclusões; sem estimação nova |

### Atualizado

[`07_apresentacoes/banca2/README.md`](07_apresentacoes/banca2/README.md) (uma linha com o ponteiro) e
[`tests/README.md`](../tests/README.md) (contagem e linha do módulo novo).

## 19/10/2026 — Resultados exploratórios pós-síntese X1–X6 (doc 46)

Motivo: execução do protocolo exploratório
[`45`](06_execucao/45_protocolo_exploratorio_pos_sintese.md), pedida pelo autor
antes de escolher a hipótese. Cada tarefa foi auditada de forma independente
antes da junção.

### Criado

| Arquivo | O que é |
|---|---|
| [`06_execucao/46_resultados_exploratorios_pos_sintese.md`](06_execucao/46_resultados_exploratorios_pos_sintese.md) | resultados exploratórios: X1 (ponte PMM-E–CNES pelo CRM: origem, substituição e distância), X2 (permanência dos alocados), X3 (dinâmica dos ativos), X4 (heterogeneidade da escolha), X5 (deslocamento regional) e X6 (poder e descartes); cada seção é gerada pelo seu script |

Insumos e scripts novos: `scripts/rdd_bolsa/17_ponte_pmme_cnes.py`,
`18_permanencia_ativos.py`, `19_escolha_heterogeneidade.py` e
`20_poder_descartes.py`; regiões de saúde oficiais (TabNet/DATASUS) e
centroides municipais do IBGE em `data/raw/aquisicao/territorio/`.

## 19/10/2026 — Conteúdo canônico da banca 2 (28/10/2026)

Motivo: a apresentação de 28/10/2026 precisa de conteúdo canônico em
`docs/07_apresentacoes/` antes de qualquer deck (`CLAUDE.md`; doc 38, §4;
doc 44, §9). O conteúdo parte da síntese E8 e é rascunho até o autor decidir
a revisão da hipótese (doc 44, §7) e a mensagem principal.

### Criado

| Arquivo | O que é |
|---|---|
| [`07_apresentacoes/banca2/README.md`](07_apresentacoes/banca2/README.md) | propósito, estado (rascunho), decisões em aberto, figuras e índice |
| [`07_apresentacoes/banca2/01_roteiro_narrativo.md`](07_apresentacoes/banca2/01_roteiro_narrativo.md) | arco, lógica de cada bloco, mensagens candidatas e frases que não mudam |
| [`07_apresentacoes/banca2/02_conteudo_slides.md`](07_apresentacoes/banca2/02_conteudo_slides.md) | 21 slides e 7 de apêndice, com figura, linha de números e notas do apresentador |
| [`07_apresentacoes/banca2/03_proveniencia_figuras_e_numeros.md`](07_apresentacoes/banca2/03_proveniencia_figuras_e_numeros.md) | figura → arquivo e script; número → arquivo e chave, em bloco gerado |
| `scripts/apresentacao/gerar_figuras_banca2.py` | figuras da regra (variante A colorida e failure mode, separado), da cadeia e do descarte, registro de números e manifesto em `output/apresentacao_banca2/` |
| `tests/test_conteudo_banca2.py` | números dos slides contra `output/`, figuras do pipeline, failure mode separado, formatador com valores sintéticos |

### Atualizado

[`07_apresentacoes/README.md`](07_apresentacoes/README.md) (índice). O gerador
lê o arquivo de IVS errado só para a figura e a contagem do failure mode; por
isso entrou como documentador autorizado na guarda
`tests/test_fonte_ivs_oficial.py` (contagem exata 1) e na tabela de leitores
da [auditoria 19](auditorias/19_reestimacao_base_oficial_failure_mode.md),
pela lista `AUDITORIA` de `scripts/tema_trabalho/12_registrar_failure_mode_ivs.py`.

---

## 19/10/2026 — Síntese E8 da RDD da bolsa (protocolo 40)

Motivo: a tarefa E8 do protocolo multi-outcome
([`06_execucao/40`](06_execucao/40_protocolo_multioutcome_rdd_bolsa.md), §7 e
§11) junta E3, E5, E6, E7 e E9, faz o Holm das duas primárias e registra, como
proposta ao autor, a revisão da pergunta econômica.

### Criado

| Arquivo | O que é |
|---|---|
| [`06_execucao/44_sintese_rdd_bolsa_multioutcome.md`](06_execucao/44_sintese_rdd_bolsa_multioutcome.md) | resposta curta, tabela por elo da cadeia, Holm, o que se pode e não se pode afirmar, literatura de magnitude e proposta de revisão da hipótese; blocos gerados de `output/rdd_bolsa/E8_*` |
| `scripts/rdd_bolsa/15_sintese_E8.py` | gera `E8_resumo.json`, `E8_tabela_sintese.csv` e os blocos do doc 44, sem estimação nova além do Holm |
| `tests/test_e8_sintese.py` | Holm (sintético e contra os CSV), reprodução das saídas e números do doc 44 |

### Atualizado

[`06_execucao/38`](06_execucao/38_estado_e_pendencias_rdd_bolsa.md) (estado),
[`README.md`](README.md) (índice), [`04_dados/02`](04_dados/02_inventario_dados_por_outcome.md)
(inventário com as bases novas), `TODO.md` e `README.md` da raiz.

## 19/10/2026 — Resultados do E7: DiRD no CNES (família F3 do protocolo 40)

Motivo: a tarefa E7 do protocolo multi-outcome
([`06_execucao/40`](06_execucao/40_protocolo_multioutcome_rdd_bolsa.md)) estima
a família F3 (oferta líquida no CNES) por diferença em descontinuidades, com
placebos, estudo de evento e as suplementares S2–S6 e as horas do §16.

### Criado

| Arquivo | O que é |
|---|---|
| [`06_execucao/43_resultados_E7_dird_cnes.md`](06_execucao/43_resultados_E7_dird_cnes.md) | contraste identificado, amostras, P2, estimativas, sensibilidades, placebos, níveis, S5, estudo de evento, S3/S4, limites e desvios do E7; tabelas geradas de `output/rdd_bolsa/E7_*` por `scripts/rdd_bolsa/14_estimar_E7_dird_cnes.py` |

## 18/10/2026 — CNES nacional para a DiRD (tarefa C do protocolo 40)

Motivo: a família F3 do protocolo multi-outcome
([`06_execucao/40`](06_execucao/40_protocolo_multioutcome_rdd_bolsa.md)) pede
o painel CNES de todos os municípios, com pré-período desde 2022, para a
diferença em descontinuidades (E7).

### Criado

| Arquivo | O que é |
|---|---|
| [`auditorias/aquisicao/A09_cnes_nacional.md`](auditorias/aquisicao/A09_cnes_nacional.md) | fonte, competências, chave municipal, esquema e validação do painel município × grupo de CBO × mês (`scripts/aquisicao/a09_adquirir_cnes_nacional.py`) |

## 19/10/2026 — Protocolo exploratório pós-síntese (X1–X6)

Motivo: antes de escolher a hipótese, o autor pediu garantia de que tudo o que
os dados permitem foi explorado. A revisão das lacunas achou seis análises
viáveis, congeladas antes de abrir os outcomes.

### Criado

| Arquivo | O que é |
|---|---|
| [`06_execucao/45_protocolo_exploratorio_pos_sintese.md`](06_execucao/45_protocolo_exploratorio_pos_sintese.md) | protocolo exploratório: ponte PMM-E–CNES pelo registro profissional (origem e substituição), permanência dos alocados, dinâmica dos ativos, heterogeneidade e deslocamento na escolha, poder e descartes |

## 18/10/2026 — Estimação do E6 (famílias F0, F1, F2 e F4 do protocolo 40)

Motivo: a tarefa E6 do protocolo multi-outcome estima, sob o protocolo
congelado, todas as especificações fixadas para F0, F1, F2, F4, o índice P1 e
as suplementares S1–S4.

### Criado

| Arquivo | O que é |
|---|---|
| [`06_execucao/41_resultados_E6_funil.md`](06_execucao/41_resultados_E6_funil.md) | resultados do E6 (índice P1, componentes, diagnósticos de seleção, co-políticas, suplementares), como ler o salto, o que cada contraste identifica e limites; as tabelas são geradas de `output/rdd_bolsa/E6_*` por `scripts/rdd_bolsa/13_estimar_E6_funil.py --atualizar-doc` |

## 18/10/2026 — E9: escolha revelada dos candidatos (protocolo 40, §12, §14, §15)

Motivo: estimação do logit condicional (e explodido) da escolha dos
candidatos entre células do mesmo curso e ciclo, com a forma funcional fixada
no §15 antes de estimar.

### Criado

| Arquivo | O que é |
|---|---|
| [`06_execucao/42_resultados_E9_escolha.md`](06_execucao/42_resultados_E9_escolha.md) | estimando, especificação, diagnósticos, resultados (tabelas geradas por `scripts/rdd_bolsa/16_estimar_E9_escolha.py` e conferidas por `tests/test_e9_escolha.py`), desvios e limites do E9 |

## 18/10/2026 — Reestimação com a base oficial do IVS (failure mode)

Motivo: o autor mandou reestimar tudo o que dependia de
`data/ivs_ipea_2010_municipios.csv` (linha de subgrupo, não o IVS do município)
com a base oficial; os números antigos só valem como failure mode (tarefa E do
protocolo [`40`](06_execucao/40_protocolo_multioutcome_rdd_bolsa.md)).

### Criado

| Arquivo | O que é |
|---|---|
| [`auditorias/19_reestimacao_base_oficial_failure_mode.md`](auditorias/19_reestimacao_base_oficial_failure_mode.md) | registro do failure mode: o erro, a propagação, a detecção, todos os leitores do arquivo com a classe de cada uso, antes e depois de cada estimativa (A2, A4, A5, Tabela 1 do ciclo 1, C3-03, banca 1, E2/E4) e onde os números antigos ainda aparecem. Gerado por script |
| `scripts/tema_trabalho/12_registrar_failure_mode_ivs.py` | lê do histórico do Git as versões anteriores à correção, compara com `output/` e gera a auditoria 19 e `output/tema_trabalho/failure_mode_ivs_*` |
| `tests/test_fonte_ivs_oficial.py` | reprova script do pipeline (e de `avaliacao_ciclo3/` e `apresentacao/`) que leia o arquivo errado fora dos documentadores do failure mode ou use colunas territoriais de painel antigo sem repô-las; varre o texto bruto de todo `.py` de `scripts/` e da raiz com contagem exata autorizada por script; confere malha e tipologia contra a a08 e o Censo 2022 |
| `output/aquisicao/manifesto_territorio_ibge.json` | proveniência da malha territorial |

### Atualizado no mesmo dia

- `run_all.py`: a07, a08 e o Censo 2022 (`aquisicao/06`) rodam antes da malha.
- Erratas e notas de failure mode: [`05_identificacao/13`](05_identificacao/13_plano_pre_analise_ciclo3.md)
  (C3-03), [`05_identificacao/16`](05_identificacao/16_sintese_achados_e_novo_plano_causal.md),
  [`06_execucao/36`](06_execucao/36_backlog_pos_auditoria.md),
  [`auditorias/12`](auditorias/12_proveniencia_fins_de_linha.md), [`13`](auditorias/13_reauditoria_independente_A1_A8.md),
  [`14`](auditorias/14_erratas_artefatos_congelados.md) (E-7), [`16`](auditorias/16_ivs_2010_oficial_e_arquivo_local.md),
  banca 1 (`07_apresentacoes/banca1/01`, `02`, `03`) e a fila `prompts/avaliacao_ciclo3/README.md`.
- [`06_execucao/38`](06_execucao/38_estado_e_pendencias_rdd_bolsa.md): D3 (a) e (b) aplicadas.

## 18/10/2026 — Construção dos outcomes do funil (tarefa B do protocolo 40)

Motivo: a tarefa B do protocolo multi-outcome constrói, às cegas quanto ao
corte, os outcomes F0, F1, F2 e F4 e as tabelas de escolha do E9 (adendo §12).

### Criado

| Arquivo | O que é |
|---|---|
| [`06_execucao/41a_construcao_outcomes_funil.md`](06_execucao/41a_construcao_outcomes_funil.md) | fontes, definições, casamento entre arquivos e desvios da construção dos outcomes do funil e das tabelas de escolha do E9; sem resultado por lado de corte. Aquisição do resultado da 1ª chamada do ciclo 2 em `scripts/aquisicao/a11_adquirir_resultado_ciclo2_chamada1.py` (numerado a11 para não colidir com outra tarefa) |

## 18/10/2026 — Políticas nos mesmos cortes de IVS (tarefa D do protocolo 40)

Motivo: o protocolo 40 (§4) pediu conferir, na fonte primária, se outra
política federal muda nos cortes 0,300 e 0,400 da bolsa.

### Criado

| Arquivo | O que é |
|---|---|
| [`auditorias/18_politicas_nos_mesmos_cortes_ivs.md`](auditorias/18_politicas_nos_mesmos_cortes_ivs.md) | auditoria das regras federais com faixas de IVS (752/2023, 485/2023, ajuda de custo do PMMB, IED da APS, teto de emendas "IVS maior que 0,3", outras), alcance sobre o PMM-E, implicações para RDD e DiRD e recomendações para E6/E7 |

Insumos novos fora de `docs/`: `scripts/aquisicao/a10_normas_mesmos_cortes_ivs.py`,
cache `data/raw/aquisicao/normas_ivs/` e saídas `output/aquisicao/a10_*`.

## 18/10/2026 — Protocolo multi-outcome da bolsa

Motivo: o autor autorizou rodar tudo com dados do repositório ou públicos, com
vários outcomes derivados do edital, e reestimar tudo com a base oficial.

### Criado

| Arquivo | O que é |
|---|---|
| [`06_execucao/40_protocolo_multioutcome_rdd_bolsa.md`](06_execucao/40_protocolo_multioutcome_rdd_bolsa.md) | protocolo congelado antes de abrir os outcomes novos: famílias F0–F4, populações, métodos (cortes e ciclos empilhados, IC honesto, Poisson local, DiRD no CNES), testes múltiplos e tarefas |

## 18/10/2026 — Inferência alternativa da RDD da bolsa

Motivo: o autor perguntou por que os ICs da RDD são tão largos, se outro método
(controle sintético, por exemplo) daria inferência melhor e o que se pode
afirmar.

### Criado

| Arquivo | O que é |
|---|---|
| [`06_execucao/39_inferencia_alternativa_rdd_bolsa.md`](06_execucao/39_inferencia_alternativa_rdd_bolsa.md) | E5, exploratório e pós-resultado: decomposição da largura do IC, 15 especificações alternativas, o que os dados descartam e avaliação de controle sintético, DiD e outros desenhos |

### Atualizado no mesmo dia

- **RDD e relatório:**
  - [`06_execucao/37`](06_execucao/37_resultados_rdd_bolsa_ivs_oficial.md),
    com a convenção do sinal, o resumo do E5 e a nota do balanço;
  - [`06_execucao/38`](06_execucao/38_estado_e_pendencias_rdd_bolsa.md),
    com o estado e a decisão D1, variante A colorida.
- **Pipeline:** [`scripts/README.md`](../scripts/README.md) e
  [`tests/README.md`](../tests/README.md), com a cadeia nova da RDD no
  `run_all.py`.
- **Documentos regerados pelo A6:**
  [`auditorias/09_red_team_atracao_provimento.md`](auditorias/09_red_team_atracao_provimento.md),
  [`auditorias/09_matriz_afirmacao_evidencia_limite.md`](auditorias/09_matriz_afirmacao_evidencia_limite.md)
  e [`06_execucao/32`](06_execucao/32_sintese_A6_resumo_intro_metodos_conclusao.md).
  Deixam de dizer "RDD encerrado em R1" e passam a ressalvar o ajuste
  completo.
- **Artigos:** `paper_pmme_curto.tex` e `paper_pmme_submission.tex`.

## 18/10/2026 — Estado e pendências da RDD da bolsa

Motivo: o autor pediu um ponto de retomada organizado antes de compactar a
conversa.

### Criado

| Arquivo | O que é |
|---|---|
| [`06_execucao/38_estado_e_pendencias_rdd_bolsa.md`](06_execucao/38_estado_e_pendencias_rdd_bolsa.md) | o que está feito e onde, as decisões em aberto do autor (forma da figura, preenchimento do ciclo 2, análises antigas afetadas) e os próximos passos autorizados |

## 14/10/2026 — Guia de conferência manual do IVS

Motivo: o autor pediu um caminho para conferir à mão, sem depender de agentes,
de onde vem o IVS da bolsa e por que o arquivo local não servia.

### Criado

| Arquivo | O que é |
|---|---|
| [`auditorias/17_guia_conferencia_manual_ivs.md`](auditorias/17_guia_conferencia_manual_ivs.md) | passo a passo com navegador e planilha: dados abertos do MS, base completa do Ipea, arquivo do repositório e IBGE, com tabela de valores esperados para nove municípios, seis deles perto dos cortes |

## 14/10/2026 — IVS 2010 oficial, RDD da bolsa estimada

Motivo: a busca pedida pelo autor mostrou que o escore administrativo do MS é o
IVS 2010 oficial do Ipea, público para todos os municípios, e que o arquivo
local usado como IVS 2010 não é a base oficial. Com o escore completo, a RDD
sharp foi estimada pelo protocolo congelado.

### Criado

| Arquivo | O que é |
|---|---|
| [`auditorias/16_ivs_2010_oficial_e_arquivo_local.md`](auditorias/16_ivs_2010_oficial_e_arquivo_local.md) | fonte oficial do IVS 2010, validação contra o escore do MS (404/404; 5.565/5.565), R1 `APROVADO_SHARP`, diagnóstico do arquivo local e lista do que precisa ser revisto |
| [`06_execucao/37_resultados_rdd_bolsa_ivs_oficial.md`](06_execucao/37_resultados_rdd_bolsa_ivs_oficial.md) | resultados da RDD da bolsa: E3 principal, diagnósticos e E1/E2/E4 como exploratórios superados |
| `data/raw/aquisicao/ivs_oficial/` (fora do Git, 201 MB) | base completa da Plataforma IVS, reprodutível por URL e SHA-256 |

### Atualizado no mesmo commit

`CLAUDE.md` e `AGENTS.md`, na regra da running variable;
[`auditorias/15`](auditorias/15_portao_r1_escore_administrativo.md), com caixa
de correção; [`06_execucao/33`](06_execucao/33_status_execucao_plano_causal.md);
[`05_identificacao/16`](05_identificacao/16_sintese_achados_e_novo_plano_causal.md),
§3.5.1, marcada como superada;
[`pedidos_dados/solicitacao_focal_rdd_bolsa.md`](pedidos_dados/solicitacao_focal_rdd_bolsa.md),
**cancelado e não enviado**;
[`07_apresentacoes/banca1/04_versao_apresentada.md`](07_apresentacoes/banca1/04_versao_apresentada.md),
com a errata E10 ("o IVS é o piso" era artefato); `README.md`; `TODO.md`.

## 14/10/2026 — Portão R1 refeito com o escore administrativo de IVS

Motivo: o autor priorizou o teste causal da hipótese da banca 1. O escore
administrativo, cuja ausência tinha arquivado a RDD da bolsa, foi encontrado
nos dados abertos do Ministério da Saúde.

### Criado

| Arquivo | O que é |
|---|---|
| [`auditorias/15_portao_r1_escore_administrativo.md`](auditorias/15_portao_r1_escore_administrativo.md) | R1 refeito: a regra da bolsa é de dois cortes, 0,300 e 0,400, no escore `ivs` publicado pelo MS; reproduz 100% das faixas nos quatro quadros. O escore só é publicado onde há especialista ativo, então R2 continua bloqueado |
| `data/raw/aquisicao/ivs_administrativo/` | brutos dos dados abertos (relação nominal PMM-E, consolidado PMMB e dicionário), capturados em 14/10/2026 |

### Atualizado no mesmo commit

[`06_execucao/33`](06_execucao/33_status_execucao_plano_causal.md), na linha
RDD-IVS e na nota de topo, e
[`pedidos_dados/solicitacao_focal_rdd_bolsa.md`](pedidos_dados/solicitacao_focal_rdd_bolsa.md),
com o pedido reduzido ao campo `ivs` de todos os municípios. O diagnóstico de
[`05_identificacao/16`](05_identificacao/16_sintese_achados_e_novo_plano_causal.md),
§3.5.1, fica superado na parte em que dizia que o escore não era observado.

---

## 07/10/2026 — Literatura empírica: resumo apresentável

Motivo: o autor pediu um resumo apresentável da literatura que embasa a
hipótese da banca, publicado no GitHub.

### Criado

| Arquivo | O que é |
|---|---|
| [`03_literatura_empirica/README.md`](03_literatura_empirica/README.md) | visão geral de uma página dos 60 estudos do fichamento `20`: a hipótese, o veredito e quatro perguntas da literatura, cada uma com um estudo principal — o brasileiro, quando há — e três secundários, e a lacuna que o trabalho ocupa. Abre automaticamente ao navegar a pasta no GitHub. Não traz número novo: tudo vem das fichas de `20` |

O fichamento `20` passou, em 05/10/2026, de documento temático a uma ficha por
estudo, com método e conclusão conferidos na fonte; a mudança foi de conteúdo,
sem mover arquivo.

---

## 05/10/2026 — Banca 1: versão apresentada registrada e literatura empírica da hipótese

Motivo: o autor enviou o PDF do deck que o grupo de fato apresentou à banca e
pediu (i) que o repositório correspondesse à apresentação e (ii) uma pesquisa
mais funda da literatura empírica que responde à hipótese econômica
apresentada.

### Criado

| Arquivo | O que é |
|---|---|
| [`07_apresentacoes/banca1/apresentada/banca1_apresentada.pdf`](07_apresentacoes/banca1/apresentada/banca1_apresentada.pdf) | o PDF exibido à banca, 21 páginas, SHA-256 `2d7a6bf5…36cdd`. Registro, não deck derivado: não é corrigido |
| [`07_apresentacoes/banca1/04_versao_apresentada.md`](07_apresentacoes/banca1/04_versao_apresentada.md) | transcrição slide a slide da versão apresentada, com errata E1–E9, proveniência de cada número e o que mudou em relação à versão de preparação. Abre `P12` (taxas de crescimento por faixa do slide 6, que não se reproduzem) e `P13` (distribuição regional dos ativos, diferença de até 0,2 p.p.) |
| [`03_literatura_empirica/20_evidencia_empirica_hipotese_remuneracao_preenchimento.md`](03_literatura_empirica/20_evidencia_empirica_hipotese_remuneracao_preenchimento.md) | a evidência empírica externa sobre a hipótese "maior remuneração oferecida, maior preenchimento", organizada pelos termos do modelo apresentado, com grau de verificação por estudo |

### Mudança de papel

[`07_apresentacoes/banca1/02_conteudo_slides.md`](07_apresentacoes/banca1/02_conteudo_slides.md)
deixa de ser "o que foi à tela": passa a ser a **versão de preparação** de
21/09/2026, da qual continuam derivando os decks Beamer e Slidev. O que a banca
viu é o `04`. Os decks **não** foram reconstruídos sobre a versão apresentada,
porque ela traz números que a regra 6 da proveniência mantém fora de qualquer
deck do repositório.

### Atualizado no mesmo commit

README da banca 1, roteiro (seção 4k), proveniência (nota de topo e `P12`/`P13`),
README de `07_apresentacoes/`, este índice, e
[`02_teoria/hipoteses_e_viabilidade_empirica.md`](02_teoria/hipoteses_e_viabilidade_empirica.md),
que ganhou a seção 4.4 — correspondência entre H1 e a redação apresentada — e
teve a referência de Costa, Nunes & Sanches corrigida para a versão publicada.
No catálogo `19`, o DOI da mesma referência na lista final foi unificado em
`10.1162/rest_a_01155`.

---

## 21/09/2026 — Banca 1: Q&A e apêndice, moldura sem navbar, galeria e Slidev reconstruído

Motivo: o autor pediu a leitura do deck em PowerPoint que o grupo de fato
apresentou na banca 1 e a implementação do que valesse a pena. O conteúdo não
muda; o tema ganha componentes e perde a barra de navegação do topo.

### Criado

| Arquivo | O que é |
|---|---|
| [`07_apresentacoes/banca1/deck_beamer/exemplos_tema.tex`](07_apresentacoes/banca1/deck_beamer/exemplos_tema.tex) | galeria de componentes do tema: a referência visual para montar um deck novo. Não é apresentação e não usa figura nem número do repositório |
| `scripts/apresentacao/build_exemplos_tema.sh` | build determinístico da galeria, para `output/apresentacao_banca1/deck_beamer/exemplos_tema.pdf` |

### Mudança de moldura

A barra de navegação de duas linhas saiu do topo e a trilha de seções passou
ao rodapé, registrada com `\pmmeselecaoitem` na ordem das seções. São 0,60 cm
de página devolvidos ao corpo, e o rodapé continua exibindo a linha de
rastreio do documento de conteúdo, agora com as outras seções em cinza ao
lado. Três tabelas voltaram de `\scriptsize` para `\footnotesize`.

### Q&A e apêndice

O documento de conteúdo ganhou, **depois** do `deck:fim` e entre
`apendice:inicio` e `apendice:fim`, um Q&A e quatro slides de apêndice: o
diagnóstico da reconstrução da regra, que saiu da tela em 17/09 (`A1`, quatro
builds); os dois trabalhos cortados da tabela do slide 7 (`A2`); a contribuição
previdenciária e o adicional não regulamentado (`A3`); e as pendências abertas
(`A4`). Nenhum número é novo: todos vêm de
[`05_identificacao/14`](05_identificacao/14_plano_implementacao_rdd_bolsa.md),
[`05_identificacao/16`](05_identificacao/16_sintese_achados_e_novo_plano_causal.md),
[`03_literatura_empirica/19`](03_literatura_empirica/19_literatura_empirica_escolha_locacional_medicos.md)
e [`auditorias/01`](auditorias/01_regra_institucional.md).

Esses slides **não entram na contagem de 17**: no Beamer ficam depois de
`\appendix`, o contador do rodapé para em `17 / 17` no último slide de
conteúdo e o apêndice exibe `Apêndice · A1` sem número. A tabela do primeiro
estágio da RDD *fuzzy* pública ficou de fora mesmo do apêndice, por ser saída
de regressão. A pendência 6 segue fechada para o Beamer e aberta para o
Slidev, que não tem apêndice.

### Slidev reconstruído; pendência 6 fechada

O deck Slidev deixou a estrutura de 15 slides em 6 seções, duas atrás do
documento, e passou à vigente: 40 páginas, uma por build, com as três
divisórias, o Q&A e os quatro slides de apêndice. No mesmo dia, a pedido do
autor, foi **repintado na identidade institucional do Insper**, a mesma do
Beamer, no lugar do verde do `slidev-theme-academic`: Inter no corpo, Playfair
Display nos títulos, preto e vermelho, capa com o gráfico institucional,
divisórias com arcos de listra e o filete vermelho na borda inferior. As
fontes entraram como `@fontsource/inter` e `@fontsource/playfair-display`
5.3.0; o logo e o gráfico são os mesmos arquivos de `deck_beamer/insper/`,
publicados por link simbólico. As figuras seguem na paleta verde do pipeline,
como no Beamer. A convenção do deck foi
mantida — um build é uma página, com o título repetido e o `n de N` no
rastreio —, e no apêndice o rastreio perde o contador. `style.css` ganhou o
layout `divisoria`, o rótulo de build e as cores da cadeia da teoria da
mudança; `Rastreio.vue` ganhou a propriedade `semnum`. O script de build passa
a vincular as sete figuras.

Ficou registrado também que o PDF do Slidev **não é reprodutível byte a
byte**: quem o escreve é o Chromium, que carimba identificadores próprios a
cada exportação. O README do deck afirmava o contrário e foi corrigido; o
conteúdo continua fixo pelas versões de `package-lock.json`.

Com isso a **pendência 6 fecha por inteiro**: nenhum dos dois decks diverge
mais do documento em estrutura. As identidades visuais seguem diferentes de
propósito, e a numeração de rodapé também: o Beamer para em `17 / 17` porque
lá um build não é uma página.

### Componentes novos no tema

Linha métrica no título de build (`\pmmebuild[...]`, `\pmmemetrica`), equação
em cartão com a referência em etiqueta (`\pmmeequacao`), fichas de termos
(`pmmefichas`), selos de sinal (`\pmmeselo`, `\pmmeselov`, `\pmmeselor`),
caixa de saída (`\pmmesaida`) e véu com faixa (`\pmmeveu`). Nenhum cria
palavra: a métrica é a descrição da figura no documento e o selo é o sinal da
derivada ao lado. A divisória passou a aceitar rótulo opcional
(`\pmmedivisoria[]`, usada no Q&A) e o rodapé, o modo de apêndice
(`\pmmeapendice`).

---

## 21/09/2026 — Revisão da PR 3 depois do merge: itens A-1b, C-7b e C-7c

Nenhum arquivo de documentação criado, movido ou removido. Entrada aberta porque
um artefato de saída novo passa a ser referenciado pela documentação corrente:
`output/tema_trabalho/A5_tabela_15_singletons_efeito_fixo.csv`.

Revisão do diff já integrado `198d401..79b6a6f`, a pedido do autor. Seções
acrescentadas dentro de documentos que permaneceram no mesmo lugar:
[`36_backlog_pos_auditoria.md`](06_execucao/36_backlog_pos_auditoria.md) ganha
«Revisão da PR 3 depois do merge» com os itens A-1b, C-7b e C-7c, e a seção C-9
ganha aviso de cifra vencida;
[`14_erratas_artefatos_congelados.md`](auditorias/14_erratas_artefatos_congelados.md)
ganha E-7 (a emenda 2 moveu também a especificação `full`), E-8 (níveis
singleton inflam o R² e não estão no `n`) e nota de ambiente da reexecução.
O red team [`09_red_team_atracao_provimento.md`](auditorias/09_red_team_atracao_provimento.md)
é regerado por `07_red_team_sintese.py` e passa a dizer que o teste de oferta
líquida regional não sustenta o veredito anterior. Os dois artigos perdem a
afirmação de que o resultado é «incompatível com pura realocação».

Amostra, desfecho, estimador e a manchete de A5 (`0,0684`; `0,50`) não mudam.

---

## 19/09/2026 — Banca 1: deck Beamer reconstruído na estrutura de 17 slides

A pedido do autor, os frames de
[`07_apresentacoes/banca1/deck_beamer/banca1_beamer.tex`](07_apresentacoes/banca1/deck_beamer/banca1_beamer.tex)
deixaram a estrutura de 15 slides em 6 seções e passaram à vigente de
[`02_conteudo_slides.md`](07_apresentacoes/banca1/02_conteudo_slides.md): 17
slides em 3 seções, um build (`\only<n>`) por `###`, três divisórias
(`\pmmedivisoria`), sumário único e as sete figuras de
`output/apresentacao_banca1/`. Nenhum arquivo criado, movido ou removido; o
tema ganhou `\pmmebuild` (título de build) e `\pmmesumariopasso` (passo do
sumário), e a linha de orientação da capa passou a ser opcional. A pendência 6
fecha para o Beamer e segue aberta para o Slidev. Documentação atualizada no
mesmo commit: README do deck (mapeamento, decisões e verificação), README da
banca, nota de abertura e pendência 6 do documento de conteúdo, seção 4i do
roteiro.

---

## 19/09/2026 — Banca 1: identidade institucional do Insper no tema Beamer

A pedido do autor, o tema Beamer passa a reproduzir a identidade do Insper
(tema oficial para Quarto, [padsInsper/quarto-insper-theme](https://github.com/padsInsper/quarto-insper-theme),
MIT): Inter no corpo, Playfair Display nos títulos (no lugar da GT Ultra Fine,
comercial), preto e vermelho, capa com o gráfico institucional, divisória de
seção. A paleta do PMM-E fica como acento e na capa alternativa `\pmmecapa`.

### Criado

| Arquivo | O que é |
|---|---|
| [`07_apresentacoes/banca1/deck_beamer/pmmeinsper.sty`](07_apresentacoes/banca1/deck_beamer/pmmeinsper.sty) | capa institucional `\inspercapa` e divisória de seção `\pmmedivisoria` |
| [`07_apresentacoes/banca1/deck_beamer/insper/`](07_apresentacoes/banca1/deck_beamer/insper/README.md) | `logo.png`, `insper-bg.png`, licença MIT do tema oficial e `README.md` |
| `07_apresentacoes/banca1/deck_beamer/fontes/Inter-*.otf`, `PlayfairDisplay-*.ttf`, `LICENSE-Inter.txt`, `OFL-Playfair.txt` | fontes de corpo e de exibição (OFL); a Playfair é instância estática gerada da fonte variável |

### Renomeado

| De | Para | Motivo |
|---|---|---|
| `07_apresentacoes/banca1/deck_beamer/fontes/OFL.txt` | `07_apresentacoes/banca1/deck_beamer/fontes/OFL-Oswald.txt` | passou a haver mais de uma licença OFL no diretório |

O deck compila a 10pt (antes 11pt) por causa da Inter. Sem mudança no documento
canônico; os frames seguiam na estrutura de 15 slides até a reconstrução do
mesmo dia (entrada acima).
## 16/09/2026 — Fila pós-auditoria exaurida por delegação; artigo curto e scripts novos

Motivo: o autor delegou à sessão as decisões pendentes da fila de
[`06_execucao/36_backlog_pos_auditoria.md`](06_execucao/36_backlog_pos_auditoria.md)
e pediu um artigo curto. Toda a documentação de estado foi atualizada no mesmo
conjunto de commits.

### Arquivos criados

| Arquivo | Papel |
|---|---|
| `paper_pmme_curto.tex` | artigo curto em três camadas (causal A8, descritiva A4, associativa A5), sete páginas |
| `scripts/tema_trabalho/06b_ameacas_a5_placebo_pretendencia_deslocamento.py` | as três ameaças do C-7, sob protocolo congelado; no `run_all.py` entre A5 e A6 |
| `scripts/tema_trabalho/11_conferir_numeros_artigo_curto.py` | conferidor do artigo curto, com cobertura de todos os decimais do corpo; no `run_all.py` depois do `10` |
| `tests/test_conferencia_artigos.py` | os dois conferidores aprovam e o artigo curto reutiliza o núcleo do principal |
| `output/tema_trabalho/A5_tabela_11_sensibilidade_colapso_uf.csv` | três variantes de efeito fixo de UF nos modelos secundários de A5 (A-1) |
| `output/tema_trabalho/A5_tabela_12` a `A5_tabela_14`, `A5_ameacas_c7.json` | placebo, pré-tendência por curso e deslocamento regional (C-7) |
| `output/tema_trabalho/A8_conferencia_numeros_artigo_curto.csv` | mapeamento cifra → artefato do artigo curto |

### Documentos alterados sem mudar de lugar

- `35_plano_correcoes_pos_auditoria.md`: emenda 2 (A-1), congelada antes do
  código e com o resultado da execução.
- `36_backlog_pos_auditoria.md`: estados das sessões 1, 3 e 4; decisões
  delegadas; D-4 parcialmente destravado; revisão de provas em D-1.
- `auditorias/14_erratas_artefatos_congelados.md`: erratas E-3 a E-6 e a
  decisão de regravar A8.
- `auditorias/09_red_team_atracao_provimento.md` e
  `06_execucao/32_sintese_A6_resumo_intro_metodos_conclusao.md`: regenerados
  pelo `07_red_team_sintese.py`; a seção "Ameaças que este red team não testou"
  foi substituída por "Placebo, pré-tendência por curso e deslocamento (C-7)".
- `TODO.md`, `README.md`, `06_execucao/05_roadmap_execucao.md`: estado da fila
  e dos artigos.

### Não foi feito, e por quê

O pedido administrativo do escore de IVS (D-3) **não foi enviado**: é ato
externo em nome do autor, fora da delegação genérica. O FTP do DATASUS não é
acessível deste ambiente, então C3-02B continua em 673/675 (D-2).

---

## 17/09/2026 — Banca 1: seções 2 e 3 revistas, e o deck passa a 17 slides

Segunda rodada do dia, a pedido do autor, sobre as **seções 2 e 3**. A primeira
rodada está na entrada seguinte. O deck passa de **16 para 17 slides**, com dois
slides criados e um removido; os builds continuam **32**, e nenhum slide passa de
três. Detalhe item a item em
[`07_apresentacoes/banca1/01_roteiro_narrativo.md`](07_apresentacoes/banca1/01_roteiro_narrativo.md),
seção 4h.

### Slides criados

- **Slide 10 — "Três tradições sustentam uma equação".** As **equações
  originais** de Moehling et al., Redding & Rossi-Hansberg e Choné & Ma saem do
  slide do custo e ganham slide próprio, no formato da tabela que existia no
  slide 9 até 16/09/2026, com a coluna "Primitiva que fornece" trocada por
  **"Equações originais"**. O slide do custo ficou com as equações **inferidas** e
  com a leitura termo a termo das desvantagens.
- **Slide 6 — "Quanto maior o IVS, mais difícil é exercer ali".** A explicação do
  índice e das suas três dimensões sai do slide das implicações, na seção 3, e
  passa à seção 1, logo depois da cláusula do edital que usa o IVS. O slide da
  política ficou intacto, em três builds.

### Slide removido

- **Desafio metodológico**, o slide 16 da estrutura anterior. A separação entre
  efeito da bolsa e efeito da vulnerabilidade deixa de ser tratada na
  apresentação. Nada foi desmentido: os três achados do portão R1 continuam em
  [`05_identificacao/16_sintese_achados_e_novo_plano_causal.md`](05_identificacao/16_sintese_achados_e_novo_plano_causal.md),
  §3.5, e a seção correspondente da proveniência foi **mantida**, marcada como
  fora da tela, pela regra 7 daquele documento.

### Informação que mudou de lugar

- A **condição de aceitação** e a **fronteira entre faixas** saem do slide da
  hipótese e vão para o das implicações; o slide da hipótese fica só com o
  enunciado de H1.
- A quarta desvantagem do médico, **mercado privado ausente**, sai do slide do
  custo e passa ao da remuneração, onde é de remuneração e não de custo.
- A advertência sobre o símbolo $B$ — amenidade, benefício ao paciente, bolsa —
  passa ao slide 10, onde os três usos aparecem juntos.

### Uma divergência declarada com o documento canônico

A pedido do autor, a tela passou a dizer que o **custo cresce com o IVS**. O
documento canônico diz o contrário: em
[`02_teoria/modelo_micro.md`](02_teoria/modelo_micro.md), §3.1, e na hipótese H4
de [`02_teoria/hipoteses_e_viabilidade_empirica.md`](02_teoria/hipoteses_e_viabilidade_empirica.md),
§4, o sinal de $c_0'(IVS)$ é ambíguo. **A teoria não foi mudada para acompanhar a
tela.** A simplificação está declarada nas notas de produção dos slides 6, 15 e
17, registrada como pendência 9 no documento de conteúdo e como `P11` na
proveniência, com as duas saídas possíveis de fechamento.

Na mesma rodada corrigiu-se uma referência: **Choné & Ma (2011)** era citado no
deck como *IJHCFE* 11 e passou a *Annals of Economics and Statistics* 101/102,
229–256, que é a referência canônica e a que contém a p. 232 da equação exibida.

---

## 17/09/2026 — Banca 1: corte de texto na seção 1, e as figuras do slide 4 entram no pipeline

A pedido do autor, sobre a seção 1 da apresentação, com um pedido geral acima de
todos — **corta texto** — e quatro específicos: gráfico no lugar de texto e de
tabela no slide do Problema, refatoração do slide da Política com análise do PR
de ajuste estrutural aberto, e dois a favor e dois contra na literatura do slide
de Efeitos. O número de slides **não mudou**: seguem 16, em três seções. Os
builds caem de **33 para 32**.

### Informação que mudou de lugar

- O **diagrama de teoria da mudança** sai do slide 5 (Política) e vai para o
  slide 7 (Pergunta de pesquisa), como primeiro build. É onde ele faz o trabalho
  que o roteiro já lhe atribuía: separar os elos escritos em ato oficial dos que
  são suposição do programa é o que torna a pergunta inevitável. O slide 5 cai de
  cinco builds para três; o slide 7 sobe de um para dois, e nenhum slide do deck
  passa de três.
- As figuras `especialistas_por_uf.png` e `deslocamento_por_regiao.png` saem de
  `docs/07_apresentacoes/banca1/figuras/` e passam a ser **geradas** em
  `output/apresentacao_banca1/`. Os dois PNGs antigos ficam no lugar, como
  material preservado do deck do grupo, e voltam à lista de figuras não usadas.

### Arquivos novos, todos derivados

Três figuras passam a ser produzidas por
[`scripts/apresentacao/gerar_figuras_banca1.py`](../scripts/apresentacao/gerar_figuras_banca1.py),
em `output/apresentacao_banca1/`: `especialistas_por_uf_extremos.png`,
`deslocamento_por_regiao.png` e `dupla_pratica_cirurgioes.png`. Os valores são
estatísticas publicadas, declaradas no script como constantes com fonte, página e
cobertura, e repetidas no `manifesto_figuras.json` sob
`estatisticas_publicadas_slide_4`, cada uma com `fonte_primaria_confirmada`.
Nenhuma deriva de base do repositório, e nenhuma é estimativa do projeto.

### Um defeito encontrado na conferência

A figura de especialistas por UF do deck do grupo **não era usável**. Calibrada
pelos dois únicos rótulos impressos — DF 453,5 e MA 68,2 —, as barras
intermediárias dão **SP ≈ 419** e **PA ≈ 135**, contra os **244** e **70** da
série que a proveniência cita. Só os dois extremos batem; a série das outras
catorze barras não tem origem conhecida. A figura nova mostra os **quatro**
valores com fonte registrada, e o panorama das 27 unidades só volta quando a
tabela por UF da *Demografia Médica 2025* estiver registrada em `data/raw/` com
hash. A pendência 1 mudou de conteúdo por isso: era de forma, virou de cobertura.

### O que veio do PR de ajuste estrutural

Dos nove itens de
[`06_execucao/37_proposta_ajuste_estrutural.md`](06_execucao/37_proposta_ajuste_estrutural.md),
entram só os de **rótulo e texto**, que é a onda 1 da sequência que o próprio PR
propõe. **D1**: "1.295 vagas" vira "1.295 **células** estabelecimento–curso", com
as 678 vagas imediatas ditas na tela, nos slides 5 e 6. **F2**: o pacote
formativo entra no slide 5 como o que **não** varia. **F5** não entra: o PR o
lista como decisão do autor, e ele vira a **pendência 8** de
[02 — Conteúdo](07_apresentacoes/banca1/02_conteudo_slides.md) e `P10` de
[03 — Proveniência](07_apresentacoes/banca1/03_proveniencia_figuras_e_numeros.md).
Nada que toque estimativa foi executado.

### Conteúdo que saiu da tela

Nenhum número mudou de valor. Saíram do corpo dos slides, e seguem rastreados em
[03 — Proveniência](07_apresentacoes/banca1/03_proveniencia_figuras_e_numeros.md):
os quatro marcadores do retrato nacional e a tabela dos três percentuais de
atuação, que **entraram nas figuras**; os 16 cursos e os 6 títulos de oncologia;
a contribuição previdenciária e o adicional não regulamentado; duas das quatro
células da literatura contrária, Costa, Nunes & Sanches (2024) — que continua no
slide 10 — e Pathman, Konrad & Ricketts (1992); e os dois números do slide 6 que
eram **saída de estimação**, o +20,9 p.p. ajustado e o +0,50 com erro padrão
0,234, porque a banca 1 não apresenta resultado de estimação.

---

## 16/09/2026 — Banca 1: nova estrutura em 3 seções, 16 slides, e cabeçalho como slide

A pedido do autor, que trouxe a estrutura pronta e comentários por bloco. A
apresentação sai de **6 seções e 15 slides** para **3 seções e 16 slides**, e o
documento canônico passa a ter uma convenção de cabeçalho que o torna
diretamente conversível em deck.

### A convenção nova

Entre os comentários `deck:inicio` e `deck:fim` de
[`02_conteudo_slides.md`](07_apresentacoes/banca1/02_conteudo_slides.md), **cada
cabeçalho é um slide**: `#` é layout de capa — a capa e as três divisórias de
seção — e `##` é layout de conteúdo. O que está fora dos marcadores é
documentação, não vai à tela. A tabela "Mapa da apresentação", no topo do
arquivo, é a correspondência autoritativa entre rótulo do roteiro, número e
título de tela.

### O rearranjo

| Seção nova | Slides | Vem de |
|---|:---:|---|
| **1. Motivação e Pergunta** | 3–7 | antigas seções 1 e 2, em quatro blocos: Problema, Política, Efeitos, Pergunta |
| **2. Literatura Teórica e Modelo Microeconômico** | 8–11 | antigas seções 3 e 4, fundidas em Visão geral, Custo da localidade e Remuneração da localidade |
| **3. Hipótese e Viabilidade Empírica** | 12–16 | antigas seções 5 e 6, abertas em Implicações, Hipótese, Disponibilidade de dados e Desafio metodológico |

O sumário passa a aparecer **uma vez**; as três divisórias de seção substituem
as repetições. "Remuneração da localidade", "Disponibilidade de dados" e
"Desafio metodológico" ganham slide próprio.

### Informação que mudou de lugar

- A tabela das **quatro desvantagens do médico** sai do slide de problema e vai
  para o slide de custo da localidade, onde cada desvantagem é mapeada a um
  termo do modelo.
- As figuras de **oferta prévia** e **retaguarda por faixa** saem do antigo
  slide 6 e passam ao slide de política, junto com a figura da bolsa: as três
  respondem à mesma pergunta, que é onde a regra manda o dinheiro.

### Conteúdo novo

- **O que determina a remuneração oferecida**, em texto: o valor é do município
  e só dele — nenhum município e nenhuma célula município–curso tem mais de uma
  faixa —, fixado por duas cláusulas que divergem, com a previdência incidindo e
  com o adicional do art. 22-D, §4º previsto em lei e não regulamentado no ciclo 1.
- **Teoria da mudança** em diagrama, separando os elos escritos em ato oficial
  dos três elos que são suposição do programa.
- **Hone et al. (2020)** entra na literatura contrária, por separar expansão
  bruta de líquida.

### Correção de erro factual

A proveniência registrava "10% dos cirurgiões atuando exclusivamente no SUS". A
fonte primária diz **7,7%** exclusivamente públicos, 19,9% exclusivamente
privados e 72,4% em dupla prática. A manchete corrente de que "apenas 10% dos
especialistas atendem no SUS" foi rebaixada a não citável: é fala em debate
parlamentar, sem metodologia, e conflita com a própria fonte primária.

### Segunda rodada: o texto cabe no frame

Ainda em 16/09/2026, a pedido do autor: **texto mais sintético** e **redundância
fora**. Duas consequências estruturais.

**`###` passa a marcar build.** Dentro de um slide, cada `###` é um `\only<n>` no
Beamer e um clique no Slidev. Um slide com três `###` é **um** frame com três
builds, não três frames. São **33 builds em 16 slides**, e o mapa no topo de
`02_conteudo_slides.md` ganhou a coluna correspondente. Cada build foi
dimensionado para caber em cerca de 14 linhas de tela.

**O que não vai à tela ficou declarado.** A linha `**Fontes:**` vira nota de
rodapé; todo bloco marcado `**Nota de produção.**` é instrução para quem monta o
deck. Antes disso, nota editorial e conteúdo de tela se misturavam no mesmo
corpo.

**Duas remoções por redundância.** A tabela das três tradições, que abria o slide
9, saiu: o conteúdo dela é coberto integralmente depois, e cada tradição passa a
ser apresentada no momento em que faz trabalho. No slide 13, a equação que
decompunha o custo saiu, porque repetia o slide 10 inteiro; ficou uma referência
cruzada.

### Divergência assumida

Os decks Beamer e Slidev permanecem na estrutura de **15 slides** até a próxima
reconstrução, por decisão do autor. A divergência está anunciada no topo de
`02_conteudo_slides.md` e nos dois READMEs de deck.


## 16/09/2026 — Banca 1: fonte Oswald embarcada, build em LuaLaTeX

A pedido do autor, para aproximar o deck da peça oficial do PMM-E: paleta
amostrada do banner, fonte de destaque igual à do título (Oswald, OFL),
imagem de fundo por frame e layouts em duas e quatro partes no tema.

### Criado

| Arquivo | O que é |
|---|---|
| [`07_apresentacoes/banca1/deck_beamer/fontes/`](07_apresentacoes/banca1/deck_beamer/fontes/README.md) | `Oswald-{Regular,Medium,SemiBold,Bold}.ttf`, `OFL.txt` e `README.md`: a fonte de destaque da identidade, versionada porque a licença permite e porque o build precisa dela |

`scripts/apresentacao/build_deck_beamer.sh` passou de `pdflatex` para
`lualatex` (o `fontspec` carrega a Oswald); o `.tex` compila nos dois motores.
Sem mudança no documento canônico: as macros novas (`\pmmefundo`, `pmmeduas`,
`pmmequatro`) não são usadas na banca 1.

---

## 16/09/2026 — Banca 1: tema Beamer próprio (PMME) no lugar do Warsaw

A pedido do autor: identidade visual do deck alinhada à peça oficial do Projeto
Mais Médicos Especialistas (azul-royal, amarelo, verde e vermelho), capa com
espaço para autores, professores e logo do Insper, sumário com composição
gráfica própria e barra de navegação de seção/subseção no topo.

### Renomeado

| De | Para | Motivo |
|---|---|---|
| `07_apresentacoes/banca1/deck_beamer/banca1_warsaw.tex` | [`07_apresentacoes/banca1/deck_beamer/banca1_beamer.tex`](07_apresentacoes/banca1/deck_beamer/banca1_beamer.tex) | o deck deixou de usar o tema Warsaw |
| `output/apresentacao_banca1/deck_beamer/banca1_warsaw.pdf` | `output/apresentacao_banca1/deck_beamer/banca1_beamer.pdf` | artefato derivado, acompanha o nome do `.tex` |

### Criado

| Arquivo | O que é |
|---|---|
| [`07_apresentacoes/banca1/deck_beamer/beamerthemePMME.sty`](07_apresentacoes/banca1/deck_beamer/beamerthemePMME.sty) | tema Beamer do projeto: paleta, fontes, navbar de seção/subseção, frametitle, rodapé, blocos e utilitários (`\fonte`, `\lead`, `\num`, `destaque`) que antes viviam no preâmbulo do `.tex` |
| [`07_apresentacoes/banca1/deck_beamer/pmmecapa.sty`](07_apresentacoes/banca1/deck_beamer/pmmecapa.sty) | capa em TikZ com slots para autoria, orientação, instituição, data, logo e foto |
| [`07_apresentacoes/banca1/deck_beamer/pmmesumario.sty`](07_apresentacoes/banca1/deck_beamer/pmmesumario.sty) | sumário em TikZ com seis seções e descrição curta |

`scripts/apresentacao/build_deck_beamer.sh` passou a exportar `TEXINPUTS` para
o diretório do deck, de modo que `\usetheme{PMME}` resolva sem instalação.

### Documento canônico

`02_conteudo_slides.md`, slide 1: a linha de autoria ganhou o slot
"orientação" e a lista dos elementos da capa. Slide 2: cada seção ganhou a
descrição curta que o sumário exibe como linha auxiliar. Conteúdo primeiro no
documento canônico, depois no deck, conforme a regra do projeto.

---

## 16/09/2026 — Banca 1: corte de 19 para 15 slides, para o arco narrativo

A pedido do autor: **cortar além de comprimir**, para facilitar a narrativa. A
compressão de 14/09 tinha reduzido os decks de 36 para 22 frames, mas o
documento canônico continuava com 19 slides e o tempo estimado em 29 minutos.
Além disso, o deck construía do slide 3 ao 18 uma hipótese sobre o valor da
bolsa e fechava dizendo que o desenho causal do trabalho usava outra coisa, sem
enquadrar a passagem.

### O corte

Critério: um slide por afirmação (roteiro, §2.2), aplicado ao contrário — dois
slides com a mesma afirmação viram um; slide que descreve sem argumentar
encolhe. Detalhe slide a slide em
[`07_apresentacoes/banca1/01_roteiro_narrativo.md`](07_apresentacoes/banca1/01_roteiro_narrativo.md), §4d.

| Fusão ou corte | Antes | Depois |
|---|:---:|:---:|
| retrato nacional + o que o médico vê | 3, 4 | **3** |
| o que é o PMM-E, sem a lista de cursos, o fluxo em passos e a figura regional | 5 | **4** |
| evidência a favor + contra | 8, 9 | **7** |
| custo geográfico + custo laboral, sem a figura do U | 13, 14 | **11** |
| o que a bolsa paga + o IVS organiza o custo | 16, 17 | **13** |
| viabilidade, reescrita com enquadramento e "o que fica de pé" | 19 | **15** |

Os demais slides só mudaram de número. Tempo estimado: de 29 para 24 minutos.

### Consequências

- `F4` (`curva_custo_laboral_burnout.png`) e `F5` (`vagas_ciclo1_por_regiao.png`)
  saem do deck e passam à lista de figuras geradas e não usadas em
  `03_proveniencia_figuras_e_numeros.md`. O script de figuras continua gerando
  `F5`; os scripts de build dos decks deixam de exigir as duas.
- As duas ressalvas de conteúdo abertas ficam **encerradas**: a contagem de 10
  cursos ambulatoriais foi conferida na Tabela 3 do edital e nos cursos 7 a 16
  do quadro de vagas (a lista antiga colapsava três cursos num item), e a
  legibilidade de `F4` deixa de afetar a apresentação.
- Os decks foram reconstruídos a partir do documento cortado: Beamer com **15
  frames** (um por slide) e 27 páginas, sem `Overfull`; Slidev com **26
  páginas**. `SOURCE_DATE_EPOCH` do Beamer passou a 16/09/2026.
- `02_teoria/hipoteses_e_viabilidade_empirica.md`, §4.2, ainda dizia que isolar
  o efeito da bolsa exigia "o escore administrativo"; passou a refletir a leitura
  do edital de 14/09: o que falta é o **Anexo IV** e os critérios de localização
  da cláusula 11.1.3.

### O que não mudou

Nenhum número novo entrou. Os cinco pontos de proveniência `P1`–`P5` continuam
registrados; `P4` foi reescrito para dizer o estado atual — as três figuras
usam a faixa publicada desde 14/09 — em vez da escolha anterior, que ele ainda
descrevia como deliberada.

---

## 14/09/2026 — Banca 1: a motivação reordenada para seguir o argumento

A motivação estava fragmentada porque estava fora de ordem lógica, e a correção
de agrupamento da mesma data agravou o sintoma: o slide 4 passou a remeter
explicitamente a "(slide 7)" para explicar a divergência entre faixa publicada e
categoria recalculada — uma referência para a frente, duas telas adiante. O
slide falava em "faixa publicada", "Faixa 1" e "categoria de IVS" antes de
qualquer um desses termos ter sido definido.

### A nova ordem

Os três blocos pedidos pelos professores — dor, política, efeitos — foram
mantidos. Mudou o que está dentro de cada um.

| Bloco | Antes | Agora |
|---|---|---|
| **O problema** | 3, 4, 5 | **3, 4** — a escassez é territorial; e, do outro lado, para o médico ela é um pacote de desvantagens concretas |
| **A política** | 6, 7 | **5, 6** — o que é o programa, e a regra que põe preço no lugar |
| **O efeito é incerto** | 8, 9, 10 | **7 a 10** — as duas medidas de oferta discordam e a bolsa maior vai para onde o médico fica sozinho; a evidência internacional não decide; o primeiro ciclo tampouco |

Em números de slide: o antigo 4 passou a **7**; o antigo 5 passou a **4**; os
antigos 6 e 7 passaram a **5** e **6**. Os slides 8 a 18 não mudaram.

O antigo slide 4 migrou para a **abertura do bloco do efeito**, que é onde ele
argumenta em vez de apenas descrever, e onde seus termos já foram definidos.

### As costuras

| Slide | Frase |
|:---:|---|
| 4 | fecha em "nenhuma dessas desvantagens se resolve sozinha. É aí que entra a política" |
| 5 | fecha em "cada vaga sai publicada com uma faixa de bolsa. É essa regra — e só ela — que o trabalho estuda" |
| 7 | abre em "onde a regra manda o dinheiro?" e fecha em "o programa põe R$ 5 mil a mais onde o médico trabalharia sozinho" |

A referência cruzada do slide 7 passou a apontar para o **slide 6**, que agora o
antecede. A coluna "Medimos?" da retaguarda dizia "sim — slide anterior",
referência que a nova ordem quebraria; passou a nomear a fonte, CNES.

**Nada foi reafirmado da versão anterior à correção de agrupamento.** As frases
de costura foram escritas sobre o achado corrigido: por habitante a bolsa maior
**não** vai para onde falta mais; em número de colegas, vai.

### Verificação

- Equivalência documento ⇄ deck conferida nos dois sentidos, contra a linha de
  base da `main`: **nenhuma divergência nova** foi introduzida.
- Nenhuma sobra da afirmação antiga ("menos da metade", "já havia menos
  especialistas") no documento ou no deck.
- Beamer em 22 frames e 29 páginas, sem `Overfull \hbox` ou `\vbox`; Slidev
  reordenado junto, em 33 páginas.

### Ponto de atenção aberto

A figura `F2` rotula as barras de mediana com **zero casas decimais**
(`f"{valor:.0f}"` em `scripts/apresentacao/gerar_figuras_banca1.py`), enquanto o
texto do slide 7 fala em **2,5** e **6,5** colegas. Na tela a figura mostra
**2** e **6**. A divergência é de formatação, não de dado, e é anterior a esta
entrada. Não foi corrigida aqui para não misturar mudança de pipeline com
reordenação narrativa.

---

## 14/09/2026 — Trava de ambiente, correção de série pré-C1 e achados da fila

Motivo: a tentativa de executar a fila pós-auditoria expôs que o repositório
roda em silêncio sob ambiente errado, e que a correção C1 não tinha propagado
para a documentação.

### O que foi criado

| Arquivo | Conteúdo | Por que existe |
|---|---|---|
| [`scripts/utils/ambiente.py`](../scripts/utils/ambiente.py) | verificação do interpretador e das versões fixadas | rodar sob versão próxima da fixada não dá erro, mas reescreve artefato a partir da 14ª casa decimal e quebra a cadeia de hashes sem aviso |
| [`tests/test_verificacao_ambiente.py`](../tests/test_verificacao_ambiente.py) | seis testes da trava | a trava só protege se ela mesma estiver coberta |

`run_all.py`, que grava artefato, passa a **abortar** diante de divergência.
`run_tests.py`, que apenas lê, **avisa** e segue. A suíte vai de 138 para 144
testes.

### O que foi corrigido

A série de A4 no `README.md` e em
[`05_identificacao/16_sintese_achados_e_novo_plano_causal.md`](05_identificacao/16_sintese_achados_e_novo_plano_causal.md)
ainda era a anterior ao C1, do balde único `RESTO`. Passa a ser a da
especificação primária vigente: metropolitano +27,9 p.p. no lugar de +29,4,
capital +32,6 no lugar de +23,2, e assim por diante. O `paper_pmme_submission.tex`
já estava correto, e o conferidor de números seguiu aprovando as 190 cifras.

`docs/auditorias/12_proveniencia_fins_de_linha.md` **não** foi alterado: ele
registra o estado observado numa data anterior ao C1, e corrigir seus números
falsificaria o registro.

### O que foi registrado

[`06_execucao/36_backlog_pos_auditoria.md`](06_execucao/36_backlog_pos_auditoria.md)
recebeu os achados que travam a fila: o alvo congelado do item A-1 não reproduz,
A5 não é reexecutável sem os microdados do CNES, e regenerar o manifesto de A6
hoje removeria em silêncio um registro de proveniência. O item D-1 passou a
resolvido, porque o artigo compilou.

### Sessões 3 e 5 da fila, no mesmo dia

Executadas juntas porque a sessão 4 está bloqueada por D-4 e as duas dividem o
gerador `07_red_team_sintese.py`. Da sessão 3 só a quarta ameaça do item C-7 é
executável; as três primeiras exigem regravar artefato de A5 e continuam
bloqueadas.

| Arquivo | Conteúdo | Por que existe |
|---|---|---|
| [`auditorias/14_erratas_artefatos_congelados.md`](auditorias/14_erratas_artefatos_congelados.md) | erratas E-1 (IC fora do espaço de parâmetros em A8) e E-2 (MDE por estrato do A3), mais o achado de que A8 não reproduz byte a byte | os dois artefatos são congelados, e corrigi-los custaria mais do que corrigir a afirmação sobre eles; a errata deixa o valor onde está e conserta o que se pode dizer dele |
| [`../scripts/tema_trabalho/09b_intervalos_exatos_escore.py`](../scripts/tema_trabalho/09b_intervalos_exatos_escore.py) | intervalo exato condicional ao lado do convencional, a partir das tabelas de A8 já publicadas | o item C-3 pede o intervalo exato "ao lado"; publicá-lo em artefato próprio atende sem tocar em A8 |

O script entra em `run_all.py` logo após `09_estimar_cutoff_escore_estrito.py` e
grava `output/tema_trabalho/A8_tabela_06_intervalos_exatos.csv`. Nenhuma tabela
de A8 é regravada, e amostra, desfecho e estimador de A8 continuam intactos.

Fora isso, nada foi criado, movido ou removido: as demais correções das sessões
3 e 5 são de conteúdo dentro de arquivos que permaneceram no mesmo lugar. A
suíte vai de 144 para 156 testes.

## 14/09/2026 — Banca 1: hipótese única, e o deck Beamer eleito e comprimido

Duas mudanças, de origens diferentes, no mesmo commit.

### A pedido da banca: uma hipótese, não duas

Os professores pediram que a apresentação ficasse com **uma única hipótese, a
primeira**. A correção foi feita primeiro no documento canônico e só depois nos
artefatos derivados, como manda a regra de proveniência.

| Documento | O que mudou |
|---|---|
| [`07_apresentacoes/banca1/02_conteudo_slides.md`](07_apresentacoes/banca1/02_conteudo_slides.md) | slide 17 passou de "Duas hipóteses" a **"A hipótese"**; a seção 5 ficou no singular, no título e no sumário; a tabela de derivadas ficou só com H1; o passo 4 foi reescrito. O documento inteiro foi reescrito no mesmo commit — ver adiante |
| [`07_apresentacoes/banca1/01_roteiro_narrativo.md`](07_apresentacoes/banca1/01_roteiro_narrativo.md) | título literal do slide 17, papel narrativo da seção 5 e as três linhas que contavam "duas hipóteses" |
| [`02_teoria/hipoteses_e_viabilidade_empirica.md`](02_teoria/hipoteses_e_viabilidade_empirica.md) | seção 4.2 refeita: a banca 1 leva uma hipótese. O conjunto canônico H1–H4 **não** mudou — mudou o que a apresentação enuncia |
| [`07_apresentacoes/banca1/README.md`](07_apresentacoes/banca1/README.md) | seção 5 no singular nas três tabelas |

**O que aconteceu com o custo locacional.** A antiga H2 — maior custo reduz o
preenchimento — não virou nota de rodapé nem sumiu: passou a ser apresentada
como **obstáculo de identificação**, que é o que ela é. O custo não varia
livremente, porque a regra do edital o amarra à bolsa e os dois sobem juntos;
ele é o que torna H1 difícil de testar, não uma segunda afirmação a testar. A
condição de degrau $\Delta B/p > \Delta c_0$ continua no slide, como
consequência da condição de aceitação na fronteira entre faixas.

A frase do slide 18 que dizia "separar H1 de H2" passou a "isolar o efeito da
bolsa do efeito do custo", no documento de conteúdo e nos dois decks.

### Decisão do autor: vai-se com o Beamer, mais limpo e mais comprimido

Dos dois decks construídos em paralelo, o **Beamer (Warsaw) é o escolhido**. Ele
foi então limpo e comprimido.

| Arquivo | O que mudou |
|---|---|
| [`07_apresentacoes/banca1/deck_beamer/banca1_warsaw.tex`](07_apresentacoes/banca1/deck_beamer/banca1_warsaw.tex) | reescrito: de **36 frames em 37 páginas** para **22 frames em 29 páginas** |
| [`scripts/apresentacao/build_deck_beamer.sh`](../scripts/apresentacao/build_deck_beamer.sh) | passou a relatar também `Overfull \vbox` |
| [`07_apresentacoes/banca1/deck_beamer/README.md`](07_apresentacoes/banca1/deck_beamer/README.md) | mapa de frames refeito; seções 3.1, 3.3, 3.4 e 5 reescritas |
| `output/apresentacao_banca1/deck_beamer/banca1_warsaw.pdf` | recompilado, 29 páginas |

**Uma barra só, embaixo.** A `headline` do Warsaw foi esvaziada e o rastreio de
seção desceu para o rodapé, no lugar antes ocupado pelo título do trabalho — que
se repetia em todas as páginas sem acrescentar nada a quem já leu a capa. A
faixa de `frametitle` com degradê, que é o que torna o tema reconhecível, ficou,
agora encostada no corpo. Saíram também as sombras das caixas de destaque. O
ganho é de cerca de uma linha e meia de texto em **todos** os frames.

**Compressão.** Sete slides do documento que estavam repartidos em dois, três ou
quatro frames de mesmo título dentro de uma só subseção foram fundidos em frame
único; outros sete viraram **um frame com dois overlays**. `\insertframenumber`
conta frames, não páginas: em um frame com overlay o rodapé exibe o mesmo
número nas duas telas, sob o mesmo título e o mesmo rastreio — para a banca é um
slide que se completa, não um slide novo. E overlay não custa tempo de fala além
do que o conteúdo já custa, o que importa contra os 28 minutos da seção 6 do
roteiro.

O slide 13 do documento ganhou o caminho inverso: o overlay que separava a
função-valor do seu glossário deixou de ser necessário, porque a altura
recuperada fez os dois caberem na mesma tela.

**O que saiu.** Prosa de ligação, citação que ilustrava sem acrescentar fato,
duas manchetes de jornal em caixa que repetiam a frase ao lado, e vão morto.
**Nenhuma afirmação e nenhum número do documento de conteúdo saíram** — todos os
valores exibidos foram reconferidos um a um contra a versão anterior do `.tex`.

**Verificação.** O build termina sem nenhum `Overfull \hbox` ou `\vbox` — nenhum
frame estoura a altura, que era o modo de falha esperado ao comprimir. Duas
execuções produzem o mesmo PDF byte a byte. As 29 páginas foram revistas uma a
uma em PNG.

### O documento canônico foi reescrito para ser a base concisa

Até aqui o deck estava **mais enxuto que o documento canônico** — divergência na
direção errada: quem lê a fonte de verdade encontrava prosa, citação e manchete
que a apresentação não mostra. `02_conteudo_slides.md` foi reescrito para dizer
exatamente o que vai à tela, e nada além.

| O que saiu | Onde |
|---|---|
| duas manchetes de jornal em citação recuada | slide 3 |
| as duas citações em inglês que ilustravam sem acrescentar fato | slides 5 e 8 |
| linhas `> Referência` soltas, que duplicavam o bloco `Fontes:` | slides 8 e 9 |
| prosa de ligação e repetição de rótulo | todos |

Dois ajustes de forma, no mesmo espírito: os números que **a figura já rotula**
— 16,0 / 10,0 / 7,3, os 5 / 3 / 2 colegas, os 15% / 34% / 42% e as sete
porcentagens de preenchimento — passaram da prosa para a **legenda da figura**,
que é onde eles são o registro do que a plateia vê sem obrigá-la a ler duas
vezes; e as duas ressalvas abertas (cursos ambulatoriais, figura do custo
laboral) ganharam seção própria no fim, em vez de ficarem só nos README dos
decks.

O cabeçalho do documento agora declara o que ele é: fonte de verdade, decks
derivados, banca teórica que termina na viabilidade empírica.

**Conferência de equivalência.** Todo número exibido no `.tex` foi procurado no
documento, e todo número do documento, no `.tex`. A única diferença que resta é
a esperada: os treze valores rotulados dentro das figuras estão no documento e
não no texto do deck, por causa da regra de não repetir em prosa o número que a
figura carrega. As afirmações foram conferidas uma a uma pelo mesmo método.

### O deck Slidev permanece, sincronizado apenas no conteúdo

O deck em `deck_slidev/` não foi descartado do repositório, mas deixou de ser
candidato. Recebeu apenas a mudança de conteúdo — hipótese única e a frase do
slide 18 — para não divergir do documento canônico. Sua composição não foi
retrabalhada, e a página 31 ficou com folga no rodapé por causa da linha de H2
removida.

---

## 14/09/2026 — Decks da banca 1 em duas tecnologias: Beamer (Warsaw) e Slidev (academic)

Motivo: produzir o artefato de projeção da banca 1, que até aqui existia só como
markdown de leitura. Foram feitos dois decks em paralelo, em tecnologias
diferentes, para comparação de clareza de apresentação. Ambos derivam de
[`07_apresentacoes/banca1/02_conteudo_slides.md`](07_apresentacoes/banca1/02_conteudo_slides.md).
Nenhuma afirmação, número, citação ou figura foi criada aqui: o documento de
conteúdo continua sendo a fonte de verdade, e divergência entre deck e documento
é erro do deck.

### Deck A — LaTeX Beamer, tema Warsaw

#### O que foi criado

| Arquivo | Conteúdo | Por que existe |
|---|---|---|
| [`07_apresentacoes/banca1/deck_beamer/banca1_warsaw.tex`](07_apresentacoes/banca1/deck_beamer/banca1_warsaw.tex) | deck em Beamer, tema Warsaw, 16:9, 36 frames em 37 páginas | a banca 1 tinha conteúdo canônico em markdown e nenhum artefato de projeção versionado |
| [`07_apresentacoes/banca1/deck_beamer/README.md`](07_apresentacoes/banca1/deck_beamer/README.md) | como compilar, mapeamento slide do documento → frames e decisões de composição | o corte de um slide do documento em vários frames precisa ser rastreável |
| `scripts/apresentacao/build_deck_beamer.sh` | build determinístico: confere as figuras, roda `pdflatex` duas vezes, relata `Overfull \hbox`, grava o PDF em `output/` e limpa auxiliares | regra do projeto: saída de apresentação é produzida por script versionado |
| `output/apresentacao_banca1/deck_beamer/banca1_warsaw.pdf` | PDF compilado, 37 páginas | artefato derivado, regerável pelo script |

#### Decisões registradas

| Decisão | Conteúdo |
|---|---|
| Mapeamento | os 18 slides do documento viram 36 frames; cada frame repete o título literal e a linha de rastreio do slide de origem, exibida em faixa fina fora do título |
| Repetição | onde a figura já rotula o número, o texto ao lado traz só a afirmação; nenhum valor aparece duas vezes na mesma tela |
| Overlay | o glossário da função-valor (slide 13) fica no mesmo frame da equação, em segundo overlay, para não deixar o referente fora da tela |
| Figuras | apenas as seis já versionadas — cinco de `output/apresentacao_banca1/` e a ilustração conceitual de `02_teoria/figuras/` — lidas por `\graphicspath` relativo à raiz, sem recorte, edição ou regeração. Cada figura tem uma única legenda, no mesmo formato `Fontes:` dos frames de texto |
| Ressalva registrada | em projeção, a legenda e as anotações de zona de `F4` (curva de custo laboral) ficam em torno de 5 pt e não são legíveis. O deck não pode regerar a figura; a decisão sobre refazê-la com tipografia maior é do autor. Detalhe no README do deck, seção 4.1 |
| Tema | Warsaw preservado no `frametitle` com degradê e sombra e nos blocos arredondados; a barra de navegação da headline foi trocada pela faixa de rastreio e o rodapé de três caixas por uma faixa fina; paleta trocada do azul padrão para o verde das figuras |
| Escopo | mantido o da banca 1 — termina na viabilidade empírica, sem slide de perguntas e sem resultado de estimação |

### Deck B — Slidev, tema `slidev-theme-academic`

#### O que foi criado

| Arquivo | Conteúdo | Por que existe |
|---|---|---|
| [`07_apresentacoes/banca1/deck_slidev/slides.md`](07_apresentacoes/banca1/deck_slidev/slides.md) | os 18 slides do documento em 33 páginas Slidev, tema `slidev-theme-academic` | a entrega da banca precisa de um deck projetável; o markdown de conteúdo é para leitura, não para projeção |
| [`07_apresentacoes/banca1/deck_slidev/README.md`](07_apresentacoes/banca1/deck_slidev/README.md) | como rodar e exportar, mapeamento slide do documento → páginas, decisões de composição | o mapeamento 1→N precisa ser auditável contra o documento de conteúdo |
| `07_apresentacoes/banca1/deck_slidev/style.css` e `components/` | estilo, faixa de rastreio de seção, faixa de fontes, figura com proporção travada | as regras de composição da seção 2 do roteiro — título é takeaway, rastreio fora do título, fonte que não compete com o conteúdo — são decisões visuais e viram CSS |
| `07_apresentacoes/banca1/deck_slidev/package.json` e `package-lock.json` | versões exatas de `@slidev/cli` (52.19.1), do tema (3.0.1) e das fontes empacotadas | build determinístico |
| `scripts/apresentacao/build_deck_slidev.sh` | exportação do PDF e dos PNG de revisão | figura ou número exibido em slide segue a mesma regra de proveniência de qualquer saída: é gerado por script versionado |

#### Saída gerada

`output/apresentacao_banca1/deck_slidev/banca1_slidev.pdf`, 33 páginas. Os PNG
por página, usados na revisão visual, são derivados do mesmo deck e ficam fora
do versionamento.

#### Segunda rodada de revisão, no mesmo dia

O deck saiu de 36 para 33 páginas. Três fusões: a figura do preenchimento do
ciclo 1 voltou a caber com sua leitura em uma página; a equação do valor
presente voltou a ficar na mesma página que o glossário dos seus termos; e os
quatro passos das hipóteses passaram de três páginas para duas. Onde a figura já
rotula o número na barra, o texto ao lado ficou só com a afirmação, sem relistar
o que a figura mostra. Nada de conteúdo foi cortado: só repetição e vão.

Ressalva registrada no README do deck: o documento canônico anuncia "10
ambulatoriais" e lista oito itens. O deck transcreve como está; a correção cabe
ao documento canônico, não ao artefato derivado.

#### Terceira rodada de revisão, no mesmo dia

O espaço livre da página passou a ser ocupado por quem ganha com ele: a figura
cresce até a barra de fontes sem distorcer, a tabela de quatro linhas ou mais se
estica, e nas páginas sem figura nem tabela o corpo do texto aumenta em vez de
ser esticado. Cartão e lista continuam sem esticar. As cinco páginas em que o
vão de rodapé permanece estão nomeadas no README do deck, com o motivo de cada
uma. Contagem de páginas inalterada.

#### O que não mudou

Nenhum arquivo da documentação foi movido, fundido ou removido. O conteúdo dos
18 slides, os números, as citações e as fontes vieram inalterados de
`02_conteudo_slides.md`; os 16 títulos dos slides 3 a 18 são os literais da
seção 2.1 do roteiro. As seis figuras são as que já existiam em
`output/apresentacao_banca1/` e em `docs/02_teoria/figuras/`: o build cria
links simbólicos para elas em um diretório de trabalho não versionado, sem
gerar, editar nem copiar imagem alguma para dentro do repositório.

### Ponto de atenção herdado do documento de conteúdo

O slide 6 de `02_conteudo_slides.md` anuncia **10 cursos ambulatoriais** e
enumera oito itens entre parênteses. Os dois decks transcrevem a lista como
está, por fidelidade; a conferência no Edital SGTES/MS nº 3/2025 fica pendente
no documento canônico, não nos decks.

---

## 09/09/2026 — Seção de apresentações, absorção do documento 18 e limpeza de referências

Motivo: preparar a entrega da banca 1 e eliminar as três duplicações de conteúdo
teórico que o projeto vinha carregando.

### O que foi criado

| Arquivo | Conteúdo | Por que existe |
|---|---|---|
| [`00_registro_mudancas.md`](00_registro_mudancas.md) | este registro | a documentação já tinha sido reorganizada antes sem deixar rastro do que foi para onde |
| [`07_apresentacoes/README.md`](07_apresentacoes/README.md) | regra da seção de apresentações | entregas de banca não tinham lugar próprio e vinham sendo tratadas como documento de teoria |
| [`07_apresentacoes/banca1/README.md`](07_apresentacoes/banca1/README.md) | escopo, estado por bloco e pendências bloqueantes | declarar que a banca 1 termina na viabilidade empírica |
| [`07_apresentacoes/banca1/01_roteiro_narrativo.md`](07_apresentacoes/banca1/01_roteiro_narrativo.md) | arco, regras de composição, rastreio do feedback e defeitos do deck anterior | feedback de banca sem ajuste rastreável não é feedback incorporado |
| [`07_apresentacoes/banca1/02_conteudo_slides.md`](07_apresentacoes/banca1/02_conteudo_slides.md) | conteúdo dos 15 slides, com título, corpo, visual, fonte e nota | fonte de verdade do deck; o `.pptx` passa a ser artefato derivado |
| [`07_apresentacoes/banca1/03_proveniencia_figuras_e_numeros.md`](07_apresentacoes/banca1/03_proveniencia_figuras_e_numeros.md) | origem e reprodutibilidade de cada número exibido | a regra de proveniência do projeto valia para `output/`, mas não estava sendo aplicada a slide |

### O que foi removido

| Arquivo removido | Para onde o conteúdo foi | Motivo |
|---|---|---|
| `02_teoria/18_modelo_teorico_slides_apresentacao.md` | [`02_teoria/modelo_micro.md`](02_teoria/modelo_micro.md), seções 3 e 3.2 | mantinha uma segunda versão da mesma teoria, com a adaptação ao PMM-E e as equações dos complementos que faltavam no documento canônico. Com o conteúdo de slides em `07_apresentacoes/`, o documento 18 deixou de ter função |

### O que mudou de lugar dentro da documentação

| Conteúdo | Antes | Agora | Motivo |
|---|---|---|---|
| Adaptação da equação de Moehling ao PMM-E, com $B_m(IVS_m)$ | documento 18 | `modelo_micro.md`, seção 3 | o modelo canônico parava no custo integrado e nunca chegava à bolsa |
| Equações originais de Redding & Rossi-Hansberg e de Choné & Ma | documento 18 | `modelo_micro.md`, seção 3.2 | mesma razão |
| Composição do IVS e correspondência com os blocos de custo | documento 18 **e** `hipoteses_e_viabilidade_empirica.md`, seção 3 | `modelo_micro.md`, seção 3.1 (única cópia) | estava duplicado em dois documentos com redações divergentes |
| Consequência econométrica da não monotonicidade de $c_0'(IVS)$ | `hipoteses_e_viabilidade_empirica.md`, seção 3 | permanece lá, agora sem repetir a teoria | teoria e consequência para estimação são coisas distintas |
| Hipótese de heterogeneidade clínico versus cirúrgico | `hipoteses_e_viabilidade_empirica.md`, hipótese 3 | mesma seção, agora como 4.1, rebaixada a heterogeneidade pré-declarada | não é hipótese principal e concorria com as três centrais |

### O que foi acrescentado a documentos existentes

| Documento | Acréscimo | Motivo |
|---|---|---|
| [`01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md`](01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md) | seção "Formulação curta canônica": a pergunta em uma linha, as duas margens e o bloco "o que a pergunta não é" | feedback da banca pedia simplificação da pergunta; a versão curta precisa ser canônica, não só de slide |
| [`02_teoria/modelo_micro.md`](02_teoria/modelo_micro.md) | seção 4 — condição de aceitação, condição de degrau $\Delta B/p > \Delta c_0$ e estática comparativa que gera H1 a H4 | feedback da banca pedia derivar as hipóteses diretamente da teoria; antes elas apareciam apenas listadas em outro documento |
| [`02_teoria/hipoteses_e_viabilidade_empirica.md`](02_teoria/hipoteses_e_viabilidade_empirica.md) | seção 4 reescrita como leitura empírica das derivadas, com 4.2 mapeando as hipóteses canônicas nas três apresentadas e 4.3 fixando linguagem permitida | as hipóteses eram postuladas no documento empírico, sem ligação formal com o modelo |
| [`03_literatura_empirica/19_literatura_empirica_escolha_locacional_medicos.md`](03_literatura_empirica/19_literatura_empirica_escolha_locacional_medicos.md) | Sivey et al. (2012) na tabela de estudos centrais; seção 7 declarando a lacuna que o trabalho ocupa; seção 8 de referências | Sivey era citado em outro documento sem estar catalogado; a lacuna estava implícita |
| [`04_dados/02_inventario_dados_por_outcome.md`](04_dados/02_inventario_dados_por_outcome.md) | seção 4.1 — números publicados que não reproduzem nas bases | achado da conferência da banca 1, detalhado abaixo |
| [`06_execucao/05_roadmap_execucao.md`](06_execucao/05_roadmap_execucao.md) | bloco "Entrega de banca 1", com estado item a item | a entrega existia e não aparecia em nenhum roadmap |
| [`README.md`](README.md) | seção 1.1 apontando este registro; seção 07 na navegação; regra de precedência ampliada | — |

### Correções de referência

| Problema | Onde | Correção |
|---|---|---|
| Link para `04_dados/20_dossie_bases_dados_saude_brasil_pmme.md`, arquivo inexistente | `README.md` | referência removida |
| Links para `02_teoria/17_fundamentacao_teorica_formacao_utilidade_regressores.md`, arquivo inexistente | três documentos de `90_arquivo_historico/` | redirecionados para `02_teoria/modelo_micro.md` |
| Referências por número — "documento 17", "documento 19", "documentos 12–14" — a arquivos que já haviam sido renomeados | `README.md`, seções 3 e 6, e documento 19 | substituídas por nome e link do arquivo vigente |

### Achado de proveniência registrado

A figura de distribuição regional do PMM-E usada no material anterior **não é
reprodutível** a partir de `data/`. Apenas o Nordeste, 60,3%, coincide com o
ciclo 1 de `pmm_especialistas_nominal.csv`. Na mesma base, o Sudeste é 23,0% e
não 10,6% — diferença de 12,4 pontos percentuais, no sentido de exagerar a
redistributividade do programa. Recortes alternativos testados, ciclos 1+2,
série histórica de dez/2025 e contagem de municípios distintos, também não
reproduzem o conjunto.

Registrado em [`04_dados/02_inventario_dados_por_outcome.md`](04_dados/02_inventario_dados_por_outcome.md),
seção 4.1, e detalhado em
[`07_apresentacoes/banca1/03_proveniencia_figuras_e_numeros.md`](07_apresentacoes/banca1/03_proveniencia_figuras_e_numeros.md).

### Conteúdo do deck anterior que foi descartado

O arquivo `PEE__Modelo_econômico.pptx` trazia, no slide de literatura, seis
referências de economia do crime — Becker (1968), Ehrlich (1973), Fella &
Gallipoli (2014), Bennett & Ouazad (2020), Dix-Carneiro et al. (2018),
Deshpande & Mueller-Smith (2022) — sem relação com escolha locacional médica.
Nenhuma delas entrou na documentação. O slide foi refeito com a literatura
canônica do projeto.

---

## 09/09/2026 — Quarta revisão da banca 1: seis seções, 18 slides e edital no repositório

Motivo: o sumário do conteúdo usava "Parte I/II/III", que não é a estrutura da
banca 1. A estrutura correta tem seis seções — motivação, pergunta, literatura
teórica, modelo microeconômico, hipóteses, viabilidade empírica — e cada uma
pode ocupar quantos slides o argumento pedir. O conteúdo foi reescrito para
essa estrutura e aprofundado onde estava raso.

### O que mudou em [`07_apresentacoes/banca1/02_conteudo_slides.md`](07_apresentacoes/banca1/02_conteudo_slides.md)

| Seção | Antes | Agora |
|---|---|---|
| 1. Motivação | 3 slides | 8 slides, em três blocos: **problema** (retrato nacional da Demografia Médica 2025 e manchetes; nossos dados por faixa; as desvantagens na visão do médico), **política** (o que é o PMM-E — lei, quem participa, aprimoramento em serviço, 16 cursos, como a vaga chega, ciclo 1 por região; e a regra IVS → faixa → bolsa) e **efeito incerto** (evidência a favor; evidência contra; o preenchimento do ciclo 1 por faixa e por estrato) |
| 2. Pergunta | 1 slide | 1 slide, com a leitura em dois objetos — preço e desvantagem |
| 3. Literatura teórica | tabela | tabela com parágrafo dizendo o que cada tradição resolve |
| 4. Modelo | 2 slides | 4 slides: decisão; **o que a bolsa paga e o que não paga** (novo — bolsa e mercado local); custo; **o IVS organiza o custo** (novo — as três dimensões do índice e o sinal ambíguo de $c_0'$) |
| 5. Hipóteses | 1 slide | 1 slide, derivação em quatro passos |
| 6. Viabilidade | 1 slide | 1 slide, com custo de vida e distância da família na tabela |

### O que foi criado

| Arquivo | Conteúdo | Por que existe |
|---|---|---|
| `data/raw/aquisicao/ivs_regra/edital_sgtes_03_2025_dou.pdf` | texto integral do Edital SGTES/MS nº 3/2025 (DOU, 24/07/2025), SHA-256 `417c82d9…d9afb2` | o repositório tinha só o FAQ da bolsa; o slide "O que é o PMM-E" cita itens do edital (objeto, requisitos, cursos, escolha de locais, barema, bolsa) que precisavam de fonte primária local |
| `output/apresentacao_banca1/vagas_ciclo1_por_regiao.png` | células e vagas imediatas do ciclo 1 por região | figura do slide 6, gerada por script |
| `output/apresentacao_banca1/preenchimento_ciclo1.png` | proporção de células preenchidas por faixa anunciada e por estrato territorial | figura do slide 10, gerada por script a partir das tabelas descritivas do módulo A4 |

### O que foi acrescentado a documentos existentes

| Documento | Acréscimo |
|---|---|
| [`07_apresentacoes/banca1/01_roteiro_narrativo.md`](07_apresentacoes/banca1/01_roteiro_narrativo.md) | arco reescrito nas seis seções; títulos dos 18 slides; quarta rodada de ajustes; tempo estimado |
| [`07_apresentacoes/banca1/03_proveniencia_figuras_e_numeros.md`](07_apresentacoes/banca1/03_proveniencia_figuras_e_numeros.md) | figuras F5 e F6; números dos slides 3, 5, 6 e 10; fontes documentais externas conferidas em 09/09/2026 |
| [`07_apresentacoes/banca1/README.md`](07_apresentacoes/banca1/README.md) | estrutura em seis seções; estado por seção |
| `scripts/apresentacao/gerar_figuras_banca1.py` | funções `figura_vagas_por_regiao` e `figura_preenchimento_ciclo1`; manifesto com as novas entradas |

### Fontes externas conferidas para o slide 3

Demografia Médica no Brasil 2025 (Scheffer et al., FMUSP/AMB): 597 mil
médicos em 2024, 353.287 especialistas (59,1%); Sudeste com 55,4% dos
especialistas e Norte com 5,9%; 453 especialistas por 100 mil habitantes no
Distrito Federal, 68 no Maranhão e 70 no Pará — conferidos na cobertura da
Agência Brasil (abril de 2025). Portaria GM/MS nº 7.061/2025 reconheceu
situação de urgência em saúde pública por 24 meses em razão do tempo de espera
na atenção especializada. A manchete do Senado Notícias de 25/09/2025 foi
conferida na página original.

---

## 09/09/2026 — Terceira revisão da banca 1: escopo teórico e saída de Reinhardt

Motivo: terceira rodada de revisão do autor, fixando o escopo da banca.

### Regra de escopo

**A banca 1 é teórica.** Fora da motivação, nenhum slide traz literatura
empírica, econometria ou estimação. A motivação é a exceção declarada: ali,
antes da pergunta, entra evidência sobre o que se pode esperar da política,
inclusive de trabalhos empíricos, porque é o que justifica perguntar. A regra
está em
[`07_apresentacoes/banca1/01_roteiro_narrativo.md`](07_apresentacoes/banca1/01_roteiro_narrativo.md),
seção 2.4.

Consequências: o slide 11 foi reescrito sem vocabulário econométrico — passa a
perguntar se há como medir cada peça do modelo e declara as duas que ficam de
fora, a renda no mercado privado local e a distância até a família. O slide 5
descreve o desenho de cada estudo em palavras comuns.

### Reinhardt retirado do slide 7

Choné e Ma (2011) já escrevem o custo de atender como $C(q; L, K)$: equipe e
capital instalado já entram no modelo por essa via. O que Reinhardt
acrescentaria é que esses insumos também elevam o benefício produzido — mas
escrever $B(q; L, K)$ em vez de $B(q)$ é **extensão deste projeto**, não dele. A
citação saiu do slide e a extensão passou a ser creditada ao projeto.

Reinhardt permanece como referência secundária em
[`02_teoria/modelo_micro.md`](02_teoria/modelo_micro.md), seção 2.3, agora com a
distinção correta entre os dois canais e com a referência de **1972**, cuja
forma geral $Q = f(H, X_1, \ldots, X_n)$ é verificável, ao lado do livro de 1975
que o projeto citava sem transcrever.

### Slide 5 reescrito como narrativa

No lugar da tabela de quatro estudos, três movimentos: **funciona** — o
experimento mexicano que sorteou o salário anunciado; **é caro** — a régua
australiana e o custo-efetividade brasileiro; **não segura** — a retenção
americana após o fim da obrigação. Fecha com o degrau do PMM-E dentro da faixa
que a literatura estima ser necessária, e com o fato de que no primeiro ciclo a
bolsa maior não trouxe mais gente.

### Títulos simplificados

"Três primitivas teóricas" virou **"De onde vem o modelo"**; "A decisão
locacional do médico" virou **"Como o médico escolhe onde trabalhar"**.

---

## 09/09/2026 — Segunda revisão da banca 1: evidência internacional, retaguarda profissional e estrutura em três partes

Motivo: segunda rodada de revisão do autor, ponto a ponto, sobre a versão em
markdown.

### Estrutura

A apresentação passou de 12 para **11 slides**, organizados em **Parte I —
Introdução** (motivação, pergunta), **Parte II — Teoria** (literatura teórica,
modelo microeconômico, hipóteses) e **Parte III — Empiria** (viabilidade
empírica). O slide de perguntas foi eliminado: a apresentação termina na
viabilidade.

### Mudanças de conteúdo

| Slide | Mudança |
|---|---|
| 3 | passou a explicar as desvantagens territoriais **na perspectiva do médico**. Nova figura de retaguarda profissional. Saíram as manchetes e o gráfico de deslocamento por região |
| 4 | explicação em três passos de como o IVS vira valor de bolsa |
| 5 | refeito: deixa de mostrar a evolução da oferta e passa a trazer **evidência externa** sobre se incentivo financeiro atrai médico para área desassistida |
| 7 | equações corrigidas para renderizar em tabela; Choné & Ma e Reinhardt em linhas separadas, cada um com sua equação original |
| 10 → 11 | a tabela de como cada objeto aparece nos dados saiu das hipóteses e entrou na viabilidade empírica |

### Por que o gráfico de deslocamento saiu

Verificação no edital: a Portaria GM/MS nº 7.177/2025 declara quatro objetivos —
**provimento, fixação, equilíbrio territorial e formação**. Reduzir deslocamento
de paciente **não é objetivo declarado**; fluxo de usuários aparece apenas como
um entre vários critérios de priorização de vagas (Edital SGTES/MS nº 2/2025,
itens 3.8–3.10). Além disso a figura media custo do paciente, quando o slide
trata do custo do médico.

### Acrescentado à literatura empírica

[`03_literatura_empirica/19_...md`](03_literatura_empirica/19_literatura_empirica_escolha_locacional_medicos.md)
ganhou a seção 7, com evidência sobre incentivos financeiros para provimento em
áreas desassistidas, em quatro blocos: o que move a alocação, a ordem de
grandeza do prêmio exigido, a evidência de que é caro ou insuficiente, e a
permanência que não acompanha a atração. Dez referências novas. Os números de
Costa, Nunes e Sanches (2024) foram conferidos no PDF do working paper —
elasticidade de 0,4 e 0,7, redução de 12,4% do desequilíbrio a US$ 15,7 milhões
por ponto percentual contra US$ 2,2 a 5,1 milhões das cotas.

Registro relevante para o desenho: **nenhum estudo dessa literatura usa RDD**. A
evidência causal disponível é RCT de oferta salarial, DiD sobre elegibilidade
geográfica ou coorte observacional.

### Figuras

| Arquivo | Situação |
|---|---|
| `output/apresentacao_banca1/retaguarda_por_faixa.png` | **nova**: colegas da mesma especialidade por município, por faixa |
| `output/apresentacao_banca1/oferta_antes_depois_por_faixa.png` | continua sendo gerada, mas **saiu do deck** |
| `figuras/motivacao_manchetes.png`, `figuras/deslocamento_por_regiao.png`, `figuras/especialistas_por_uf.png` | preservadas, **não usadas** |

Nenhuma figura de fonte externa entra mais no deck: as três em uso são geradas
por script e a quarta é ilustração conceitual do modelo.

### Ressalva de citação

A equação de Reinhardt exibida no slide 7 é a forma geral do artigo de **1972**
no *Review of Economics and Statistics*, não do livro de 1975 que o projeto
cita. Registrado em
[`07_apresentacoes/banca1/03_proveniencia_figuras_e_numeros.md`](07_apresentacoes/banca1/03_proveniencia_figuras_e_numeros.md),
seção 3.

---

## 09/09/2026 — Revisão de conteúdo da banca 1, população do Censo 2022 e achado sobre `populacao_2010`

Motivo: revisão ponto a ponto do autor sobre a primeira versão em markdown, e
a descoberta de que o repositório não tinha denominador populacional válido.

### Conteúdo

A apresentação passou de 15 para **12 slides**, na margem de **preenchimento**
apenas. Mudanças por slide em
[`07_apresentacoes/banca1/01_roteiro_narrativo.md`](07_apresentacoes/banca1/01_roteiro_narrativo.md),
seção 4. As hipóteses foram reduzidas a duas — remuneração real com sinal
positivo e custo locacional com sinal negativo sobre a probabilidade de
preenchimento — e o slide passou a declarar como cada objeto aparece nos dados
e o limite de identificação.

### Criado

| Arquivo | Conteúdo |
|---|---|
| `scripts/aquisicao/06_adquirir_populacao_censo2022.py` | baixa a população residente municipal do Censo 2022 (IBGE/SIDRA, tabela 4709), com bruto em `data/raw/aquisicao/populacao/` e manifesto com hash |
| `output/aquisicao/populacao_censo2022_municipios.csv` | 5.570 municípios, 203.080.756 habitantes |
| `output/apresentacao_banca1/oferta_pre_por_faixa.png` | especialistas por 100 mil habitantes em jun/2025, por faixa de bolsa |
| `output/apresentacao_banca1/oferta_antes_depois_por_faixa.png` | a mesma taxa, mensal, jun/2024 a jul/2026 |

### Removido

| Arquivo | Motivo |
|---|---|
| `output/apresentacao_banca1/distribuicao_regional.png` | participação no total confunde tamanho do programa com tamanho da população; substituída pelas figuras por habitante |

### Achado registrado

`populacao_2010`, única variável populacional de `data/`, **não é população
residente**: soma 41,85 milhões contra 190,76 milhões do Censo 2010, com razão
variando de 0,10 a 0,42 entre municípios. Afeta `estoque_pre_por_10k`, a
covariável `log_pop` dos módulos A4 e A5 e o rótulo da tabela 1 de estatísticas
descritivas. Registrado em
[`04_dados/02_inventario_dados_por_outcome.md`](04_dados/02_inventario_dados_por_outcome.md),
seção 4.0. As saídas históricas não foram reescritas.

### Acrescentado a documentos existentes

| Documento | Acréscimo |
|---|---|
| [`04_dados/02_inventario_dados_por_outcome.md`](04_dados/02_inventario_dados_por_outcome.md) | base derivada de população do Censo 2022; seção 4.0 |
| [`02_teoria/hipoteses_e_viabilidade_empirica.md`](02_teoria/hipoteses_e_viabilidade_empirica.md) | seção 4.2 refeita para as duas hipóteses da banca |
| [`scripts/README.md`](../scripts/README.md) | `apresentacao/` e o script de população no mapa |

---

## 09/09/2026 — Conteúdo da banca 1 em markdown, figuras versionadas e correção da figura regional

Motivo: a entrega passa a ser lida no GitHub e no Obsidian, não montada como
deck. O conteúdo deixa de ser especificação de slide e vira documento legível de
ponta a ponta, com as figuras dentro do repositório.

### Estrutura da apresentação

Reorganizada nas três partes da banca 1, no lugar dos seis blocos anteriores:

| Parte | Conteúdo | Slides |
|:---:|---|:---:|
| 1 | Motivação e pergunta | 3–7 |
| 2 | Literatura teórica, modelo micro e hipóteses | 8–12 |
| 3 | Viabilidade empírica | 13–14 |

O slide de literatura passou a liderar pela literatura **teórica**, com cada
trabalho declarando qual primitiva fornece e onde ela entra no modelo. A
evidência empírica ficou como bloco de apoio ao argumento da lacuna.

### Figuras

| Arquivo | Origem |
|---|---|
| `docs/07_apresentacoes/banca1/figuras/motivacao_manchetes.png` | externa, preservada do material anterior |
| `docs/07_apresentacoes/banca1/figuras/especialistas_por_uf.png` | externa, Demografia Médica no Brasil 2025 |
| `docs/07_apresentacoes/banca1/figuras/deslocamento_por_regiao.png` | externa, REGIC 2018 |
| `output/apresentacao_banca1/bolsa_por_faixa.png` | gerada por script |
| `output/apresentacao_banca1/distribuicao_regional.png` | gerada por script |

Criado `scripts/apresentacao/gerar_figuras_banca1.py`, que grava as duas figuras
geradas e um `manifesto_figuras.json` com hash SHA-256 da base de entrada,
recorte aplicado, data de referência e as constantes externas usadas.

### Pendência encerrada

A figura de distribuição regional foi regerada a partir de
`data/pmm_especialistas_nominal.csv`, ciclo 1. Os valores corretos são Nordeste
60,3%, Sudeste 23,0%, Norte 12,1%, Centro-Oeste 3,6% e Sul 1,0%. A versão
anterior trazia o Sudeste com 10,6%, doze pontos percentuais abaixo, o que
exagerava a redistributividade afirmada no slide. Permanece aberta apenas a
pendência de manifesto das figuras de fonte externa.

### Removido

A seção de restrições de template e a decisão sobre equações nativas em
PowerPoint saíram do documento de conteúdo. Eram específicas da produção de
`.pptx`, que deixou de ser o formato da entrega.

---

## Antes de 09/09/2026

A reorganização em seções numeradas 01 a 06, com `90_arquivo_historico/`, é
anterior a este registro e está descrita na
[`README.md`](README.md), seções 2 e 4. Os documentos 07 a 11 e as versões 15 e
16 foram arquivados naquela ocasião, sem entrada individual.
