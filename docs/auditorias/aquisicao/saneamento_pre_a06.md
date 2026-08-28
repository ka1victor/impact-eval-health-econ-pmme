# Relatório Consolidado de Saneamento Pré-A06 (A05R)

> **Data da Auditoria:** 28 de agosto de 2026  
> **Protocolo:** Saneamento e Auditoria Pré-Integração de Dados (A05R)  
> **Escopo:** Verificação de integridade criptográfica, saneamento metodológico e alinhamento econométrico das cinco frentes de aquisição do Programa Mais Médicos Especialistas (PMM-E / Lei 15.233/2025).  
> **Agentes Auditados:** A01 (Vagas e Versionamento), A02 (Seleção e Trajetória), A03 (IVS e Regra Normativa), A04 (Pagamentos e Orçamento), A05 (CNES Mensal).  
> **Regras Metodológicas Observadas:** Sem falsos brutos sintéticos em `data/raw/`; running variable canônica IVS 2010 (IPEA); bloqueio de inferência causal prematura em fase de aquisição; preservação estrita do piloto CNES de 3 competências.

---

## 1. Sumário Executivo e Veredito Global

O protocolo de saneamento **A05R** foi executado de ponta a ponta sobre as cinco frentes de aquisição de dados do projeto de avaliação de impacto do PMM-E. A revisão crítica prévia ([`revisao_pre_a06.md`](file:///c:/Users/camil/Desktop/Kauã/Insper/impact-eval-health-econ-pmme/docs/auditorias/aquisicao/revisao_pre_a06.md)) havia identificado desvios pontuais de integridade cadastral, artefatos sintéticos alocados indevidamente em diretórios de dados brutos e extrapolações conceituais sobre identificação causal.

Todas as pendências foram rigorosamente saneadas, os scripts foram refatorados e testados de forma idempotente, os manifestos JSON foram regenerados com hashes SHA-256 determinísticos e as documentações técnicas foram sincronizadas com o estado factual dos dados públicos abertos.

```text
========================================================================================
DECISÃO CONSOLIDADA DO SANEAMENTO PRÉ-A06:
ENTRADAS APTAS PARA A06
========================================================================================
```

---

## 2. Diagnóstico Detalhado por Frente de Aquisição

### 2.1 Frente A01 — Vagas Ofertadas e Versionamento de Chamamentos
* **Script Responsável:** [`scripts/aquisicao/a01_adquirir_vagas.py`](file:///c:/Users/camil/Desktop/Kauã/Insper/impact-eval-health-econ-pmme/scripts/aquisicao/a01_adquirir_vagas.py)
* **Manifesto Gerado:** [`output/aquisicao/a01_manifesto_vagas.json`](file:///c:/Users/camil/Desktop/Kauã/Insper/impact-eval-health-econ-pmme/output/aquisicao/a01_manifesto_vagas.json)
* **Inventário de Versões:** [`output/aquisicao/a01_inventario_versoes.json`](file:///c:/Users/camil/Desktop/Kauã/Insper/impact-eval-health-econ-pmme/output/aquisicao/a01_inventario_versoes.json)
* **Relatório de Auditoria:** [`docs/auditorias/aquisicao/A01_vagas_e_versionamento.md`](file:///c:/Users/camil/Desktop/Kauã/Insper/impact-eval-health-econ-pmme/docs/auditorias/aquisicao/A01_vagas_e_versionamento.md)
* **Ações de Saneamento Executadas:**
  1. **Distinção Conceitual de Unidade:** Separou-se formalmente a unidade de registro nas planilhas ministeriais:
     - **Célula de Oferta Agregada (CNES–Curso):** 1.488 linhas consolidadas em `data/pmm_especialistas_nominal.csv` e 7.276 registros históricos em `data/pmm_especialistas_serie_historica.csv`.
     - **Quantidade de Vagas Físicas (`qt_vagas`):** 2.923 vagas ofertadas no universo dos chamamentos públicos (Ciclos 1, 2 e 3).
     - **Vaga Física Individual:** Não possui identificador único determinístico (`id_vaga`) nas planilhas públicas do Ministério da Saúde.
  2. **Rastreabilidade Completa de Versões:** Mapeamento exaustivo das transições de versão:
     - Ciclo 1 Chamada 1: 3 versões documentadas (original, retificada e sub judice).
     - Ciclo 2 Chamada 1: 2 versões documentadas (original e retificada com ampliação de serviços).
     - Ciclo 3 Chamada 1: 2 versões documentadas (quadro inicial e retificação).
  3. **Preservação Criptográfica:** Todos os 15 arquivos XLSX em `data/raw/pmm_e/` e 8 planilhas em `data/raw/aquisicao/vagas/` tiveram seus hashes SHA-256 verificados.

---

### 2.2 Frente A02 — Seleção e Trajetória Pública dos Médicos
* **Script Responsável:** [`scripts/aquisicao/a02_adquirir_trajetoria.py`](file:///c:/Users/camil/Desktop/Kauã/Insper/impact-eval-health-econ-pmme/scripts/aquisicao/a02_adquirir_trajetoria.py)
* **Manifesto Gerado:** [`output/aquisicao/a02_manifesto_trajetoria.json`](file:///c:/Users/camil/Desktop/Kauã/Insper/impact-eval-health-econ-pmme/output/aquisicao/a02_manifesto_trajetoria.json)
* **Matriz de Eventos:** [`output/aquisicao/a02_matriz_eventos_publicos.json`](file:///c:/Users/camil/Desktop/Kauã/Insper/impact-eval-health-econ-pmme/output/aquisicao/a02_matriz_eventos_publicos.json)
* **Relatório de Auditoria:** [`docs/auditorias/aquisicao/A02_selecao_e_trajetoria.md`](file:///c:/Users/camil/Desktop/Kauã/Insper/impact-eval-health-econ-pmme/docs/auditorias/aquisicao/A02_selecao_e_trajetoria.md)
* **Ações de Saneamento Executadas:**
  1. **Recuperação de Fontes Oficiais:** Identificação e integração das planilhas de alocação retificada do Ciclo 1 Chamada 1 (`2025_ciclo1_chamada1_alocacao_retificada.xlsx` e `2025_ciclo1_chamada1_alocacao_retificada_subjudice.xlsx`), recuperando dados de inscrições, preferências e alocações de 2025.
  2. **Correção de Metadados e URLs:** Correção da URL canônica no manifesto para o slug oficial do portal do Ministério da Saúde.
  3. **Formalização da Incalculabilidade de Spells:** Confirmação explícita de que a taxa de permanência aos 90, 120 e 180 dias e a duração de *spells* individuais **não podem ser calculadas** a partir de dados públicos abertos (exigem microdados longitudinais do SGP/MS, catalogados para o Pedido LAI).

---

### 2.3 Frente A03 — IVS Municipal e Regra Normativa de Alocação
* **Script Responsável:** [`scripts/aquisicao/a03_adquirir_ivs_regra.py`](file:///c:/Users/camil/Desktop/Kauã/Insper/impact-eval-health-econ-pmme/scripts/aquisicao/a03_adquirir_ivs_regra.py)
* **Manifesto Gerado:** [`output/aquisicao/a03_manifesto_ivs_regra.json`](file:///c:/Users/camil/Desktop/Kauã/Insper/impact-eval-health-econ-pmme/output/aquisicao/a03_manifesto_ivs_regra.json)
* **Matriz de Regra:** [`output/aquisicao/a03_matriz_regra_tratamento.json`](file:///c:/Users/camil/Desktop/Kauã/Insper/impact-eval-health-econ-pmme/output/aquisicao/a03_matriz_regra_tratamento.json)
* **Relatório de Auditoria:** [`docs/auditorias/aquisicao/A03_ivs_e_regra.md`](file:///c:/Users/camil/Desktop/Kauã/Insper/impact-eval-health-econ-pmme/docs/auditorias/aquisicao/A03_ivs_e_regra.md)
* **Ações de Saneamento Executadas:**
  1. **Eliminação de Falsos Arquivos Brutos:** Exclusão de 3 arquivos JSON sintéticos que haviam sido gravados indevidamente em `data/raw/aquisicao/ivs_regra/` (`portaria_gm_ms_7177_2025_registro.json`, `portaria_gm_ms_7266_2025_registro.json`, `ipea_atlas_vulnerabilidade_social_2015_registro.json`).
  2. **Remoção de Insegurança de Rede:** Eliminação de contextos SSL não verificados (`ssl._create_unverified_context`) no script de aquisição.
  3. **Catalogação Honesta das Normas:** Portarias e notas metodológicas foram registradas diretamente no manifesto `output/aquisicao/a03_manifesto_ivs_regra.json` como metadados normativos, sem poluir diretórios de dados brutos.
  4. **Running Variable Canônica Preservada:** O **IVS 2010 (IPEA)** para os 5.565 municípios brasileiros foi mantido como a running variable oficial e intocada em `data/ivs_ipea_2010_municipios.csv`.
  5. **Reenquadramento Econométrico Honesto da Divergência:** A divergência de 42,56% entre a classificação de vulnerabilidade declarada nos editais e o cálculo estrito do IVS 2010 foi documentada factual e descritivamente (compatível com *vintage* de base, precisão decimal/arredondamento, reclassificação administrativa por carência médica ou erro cadastral), expurgando qualquer asserção causal prematura de RDD.

---

### 2.4 Frente A04 — Pagamentos Públicos e Execução Orçamentária
* **Script Responsável:** [`scripts/aquisicao/a04_adquirir_pagamentos.py`](file:///c:/Users/camil/Desktop/Kauã/Insper/impact-eval-health-econ-pmme/scripts/aquisicao/a04_adquirir_pagamentos.py)
* **Manifesto Gerado:** [`output/aquisicao/a04_manifesto_pagamentos.json`](file:///c:/Users/camil/Desktop/Kauã/Insper/impact-eval-health-econ-pmme/output/aquisicao/a04_manifesto_pagamentos.json)
* **Matriz de Dose:** [`output/aquisicao/a04_matriz_dose_financeira.json`](file:///c:/Users/camil/Desktop/Kauã/Insper/impact-eval-health-econ-pmme/output/aquisicao/a04_matriz_dose_financeira.json)
* **Tabelas Derivadas Consolidadas:** [`output/aquisicao/a04_grade_bolsas_historico_2025_2026.csv`](file:///c:/Users/camil/Desktop/Kauã/Insper/impact-eval-health-econ-pmme/output/aquisicao/a04_grade_bolsas_historico_2025_2026.csv), [`output/aquisicao/a04_execucao_orcamentaria_acoes_provimento_2025_2026.csv`](file:///c:/Users/camil/Desktop/Kauã/Insper/impact-eval-health-econ-pmme/output/aquisicao/a04_execucao_orcamentaria_acoes_provimento_2025_2026.csv), [`output/aquisicao/a04_normas_regras_financeiras_pmme.json`](file:///c:/Users/camil/Desktop/Kauã/Insper/impact-eval-health-econ-pmme/output/aquisicao/a04_normas_regras_financeiras_pmme.json), [`output/aquisicao/a04_inventario_sistemas_pagamento_ms.json`](file:///c:/Users/camil/Desktop/Kauã/Insper/impact-eval-health-econ-pmme/output/aquisicao/a04_inventario_sistemas_pagamento_ms.json).
* **Relatório de Auditoria:** [`docs/auditorias/aquisicao/A04_pagamentos.md`](file:///c:/Users/camil/Desktop/Kauã/Insper/impact-eval-health-econ-pmme/docs/auditorias/aquisicao/A04_pagamentos.md)
* **Ações de Saneamento Executadas:**
  1. **Eliminação de Falsos Arquivos Brutos:** Exclusão de 4 arquivos sintéticos que haviam sido criados em `data/raw/aquisicao/pagamentos/`.
  2. **Consolidação Idempotente em Output:** As tabelas derivadas compiladas a partir de editais e dados orçamentários macro do SIOP/SIAFI foram redirecionadas para `output/aquisicao/`.
  3. **Classificação Honesta das Fontes:** Microdados individualizados de pagamento foram classificados como `NAO_OBTIDO_EM_DADOS_ABERTOS` e encaminhados para o Pedido LAI (A07).
  4. **Veredito da Dose Financeira:**
     - **Faixa Anunciada (Oferta Normativa):** Observável como variável descritiva nos editais condicional à vaga.
     - **Valor Devido:** Inviável em dados abertos (exigiria assiduidade e logs mensais).
     - **Valor Recebido e Primeiro Estágio Causal:** Bloqueados aguardando microdados administrativos da folha do SGP/FNS.
  5. **Remoção de Alegações Causais:** Expurgada qualquer tentativa de estimar ITT definitivo ou presumir *compliance* perfeito na dose monetária.

---

### 2.5 Frente A05 — Cadastro Nacional de Estabelecimentos de Saúde (CNES)
* **Script Responsável:** [`scripts/aquisicao/a05_adquirir_cnes.py`](file:///c:/Users/camil/Desktop/Kauã/Insper/impact-eval-health-econ-pmme/scripts/aquisicao/a05_adquirir_cnes.py)
* **Manifesto Gerado:** [`output/aquisicao/a05_manifesto_cnes.json`](file:///c:/Users/camil/Desktop/Kauã/Insper/impact-eval-health-econ-pmme/output/aquisicao/a05_manifesto_cnes.json)
* **Dicionário de Tabelas:** [`output/aquisicao/a05_dicionario_tabelas_cnes.json`](file:///c:/Users/camil/Desktop/Kauã/Insper/impact-eval-health-econ-pmme/output/aquisicao/a05_dicionario_tabelas_cnes.json)
* **Relatório de Auditoria:** [`docs/auditorias/aquisicao/A05_cnes_mensal.md`](file:///c:/Users/camil/Desktop/Kauã/Insper/impact-eval-health-econ-pmme/docs/auditorias/aquisicao/A05_cnes_mensal.md)
* **Ações de Saneamento Executadas:**
  1. **Separação de Universos Cadastrais:** Diferenciação rigorosa entre os **518 estabelecimentos do snapshot nominal de ativos** (`data/pmm_especialistas_nominal.csv`) e o universo de estabelecimentos ofertados nos chamamentos públicos.
  2. **Auditoria Cadastral no Piloto:**
     - Competência `202406`: 515 de 518 estabelecimentos localizados na `tbEstabelecimento` (99,42% de cobertura cadastral).
     - Competência `202506`: 517 de 518 estabelecimentos localizados na `tbEstabelecimento` (99,81% de cobertura cadastral).
     - Competência `202607`: 518 de 518 estabelecimentos localizados na `tbEstabelecimento` (100,00% de cobertura cadastral).
  3. **Remoção de Especulação Cadastral:** Substituída a hipótese especulativa de "inauguração em 2025" pela constatação factual de que os 3 estabelecimentos passam a constar no cadastro oficial a partir da competência 202506 (compatível com inauguração, habilitação recente ou atualização cadastral de código).
  4. **Documentação da Ausência da Ponte Determinística:** Registro explícito de que o CNES público não possui identificador determinístico de vínculo com o PMM-E (depende de chave administrativa via SGTES/LAI).
  5. **Postergação Consciente do Download Integral:** As 3 competências piloto (`202406`, `202506`, `202607`) foram mantidas e inspecionadas localmente, postergando o download das 23 competências intermediárias para execução assíncrona controlada.

---

## 3. Matriz Comparativa do Saneamento (Antes vs Depois)

| Dimensão Auditada | Estado Anterior (Diagnóstico Revisão) | Estado Saneado (A05R) | Impacto para A06 |
|---|---|---|---|
| **Arquivos Brutos Sintéticos** | 7 arquivos falsos criados em `data/raw/` (3 em A03 e 4 em A04) | Todos os 7 arquivos excluídos; saídas compiladas movidas para `output/aquisicao/` | Garante integridade estrita de `data/raw/` |
| **Unidade de Análise de Vagas** | Ambiguidade entre célula, vaga física e alocação | Separação explícita entre Célula de Oferta Agregada (1.488) e Vagas Físicas (2.923) | Previne distorção em denominadores |
| **Alocação 2025 Ciclo 1 Ch1** | Classificada como ausente na matriz de eventos | Recuperada das planilhas de alocação retificada em `data/raw/aquisicao/vagas/` | Enriquece histórico de preferências |
| **Running Variable (IVS)** | Menções imprecisas a outros índices | IVS 2010 (IPEA) canônico reafirmado para 5.565 municípios | Conformidade total com regras do projeto |
| **Divergência IVS (42,56%)** | Asserção causal prematura de RDD | Tratamento factual descritivo (vintage, tolerância, reclassificação ou erro) | Integridade econométrica preservada |
| **Dose Financeira** | Tentativa de estimar ITT causal da dose monetária | Faixa anunciada registrada como variável descritiva; dose efetiva bloqueada | Sem imputação de compliance perfeito |
| **Universo CNES** | Confusão entre ativos nominais e total de vagas | 518 CNES do snapshot nominal de ativos auditados separadamente | Validação cadastral inequívoca |
| **Ponte PMM-E–CNES** | Tentativa de pareamento probabilístico | Ponte determinística pública reconhecida como inviável; formalizada para LAI | Bloqueia inferências espúrias |

---

## 4. Tabela Consolidada de Evidências, Hashes SHA-256 e Localização Física

Abaixo estão listados todos os arquivos canônicos brutos, planilhas recuperadas e manifestos gerados após a execução completa do pipeline de saneamento:

### 4.1 Dados Brutos Canônicos do Repositório (Intocados)
| Arquivo | Localização Relativa | Tamanho | SHA-256 |
|---|---|---:|---|
| **IVS 2010 Municipal** | `data/ivs_ipea_2010_municipios.csv` | 508.536 B | `fe46ae9578d08b8596437c13ff4fd7461c7ac85c47b492eb2424f8bcd6d4021e` |
| **Snapshot Nominal de Ativos** | `data/pmm_especialistas_nominal.csv` | 363.313 B | `76237f4cb6bf7e9aaccbf22ea443e1070c889c05a0357a3c1cb34ee50f58fc7d` |
| **Série Histórica Agregada** | `data/pmm_especialistas_serie_historica.csv` | 1.130.450 B | `98486b5d48fc7a69c8ba9554f0c28cf546c20ff79be31e64c3dccec95d6b981c` |

### 4.2 Piloto de Bases do CNES Mensal (DATASUS)
| Arquivo | Localização Relativa | Tamanho | SHA-256 |
|---|---|---:|---|
| **CNES 202406 (Baseline 12m)** | `data/raw/cnes/BASE_DE_DADOS_CNES_202406.ZIP` | 594.371.169 B | `10746d84f19d45f5ef6f89e74d616ae73e37e6dd7dfd3b026e1b93a519a22253` |
| **CNES 202506 (Baseline 1m)** | `data/raw/cnes/BASE_DE_DADOS_CNES_202506.ZIP` | 639.832.653 B | `b43d12780a1d2ad47ab244272912262fd3b3b59e08c5f2ae715abf2a318e95ba` |
| **CNES 202607 (Corte Recente)** | `data/raw/cnes/BASE_DE_DADOS_CNES_202607.ZIP` | 734.781.715 B | `f4ad8a2b4a156a8be9f3e76fafaba9870b9165bc56e86ac23578ffb609755ec9` |

### 4.3 Manifestos e Matrizes Estruturadas em `output/aquisicao/`
| Arquivo | Descrição Técnica | SHA-256 (prefixo) |
|---|---|:---:|
| `output/aquisicao/a01_manifesto_vagas.json` | Manifesto de vagas e planilhas dos chamamentos | `7a487eec5d` |
| `output/aquisicao/a01_inventario_versoes.json` | Inventário de transições e retificações de vagas | `934ccc551e` |
| `output/aquisicao/a02_manifesto_trajetoria.json` | Manifesto de arquivos de seleção e alocação | `ea8d5e13f8` |
| `output/aquisicao/a02_matriz_eventos_publicos.json` | Matriz de eventos da trajetória pública observável | `4eda567dd2` |
| `output/aquisicao/a03_manifesto_ivs_regra.json` | Manifesto de regras normativas e IVS 2010 | `842e178f1c` |
| `output/aquisicao/a03_matriz_regra_tratamento.json` | Matriz de concordância IVS e regras de tratamento | `958ecfbe75` |
| `output/aquisicao/a04_manifesto_pagamentos.json` | Manifesto de regras financeiras e orçamentárias | `b71294a9f5` |
| `output/aquisicao/a04_matriz_dose_financeira.json` | Matriz de regras de remuneração e dose teórica | `0125162b60` |
| `output/aquisicao/a04_grade_bolsas_historico_2025_2026.csv` | Histórico consolidado de faixas de bolsas | `e97558c880` |
| `output/aquisicao/a04_execucao_orcamentaria_acoes_provimento_2025_2026.csv` | Execução orçamentária federal (SIOP/SIAFI) | `01a934d7d9` |
| `output/aquisicao/a04_normas_regras_financeiras_pmme.json` | Dicionário de atos normativos financeiros | `7dfd3133ca` |
| `output/aquisicao/a04_inventario_sistemas_pagamento_ms.json` | Inventário de sistemas de pagamento (SGP/FNS) | `cddd8d17a9` |
| `output/aquisicao/a05_manifesto_cnes.json` | Manifesto de competências e integridade CNES | `82d0243216` |
| `output/aquisicao/a05_dicionario_tabelas_cnes.json` | Dicionário e estabilidade de esquema CNES (117 tabelas) | `2a9bb8f10a` |

---

## 5. Inventário dos Bloqueios Administrativos para o Agente A07 (LAI)

Os bloqueios metodológicos identificados durante a aquisição de dados públicos abertos foram catalogados formalmente para inclusão nos pedidos de acesso à informação (LAI) a serem estruturados pelo **Agente A07**:

| Item de Informação | Motivo do Bloqueio em Dados Abertos | Impacto se não Obtido | Destinatário do Pedido |
|---|---|---|---|
| **Ponte Determinística PMM-E–CNES** | CNES público não traz CRM/CPF desmascarado; listas de editais trazem CPF mascarado | Inviabiliza identificação de médicos do PMM-E dentro do CNES no nível individual | SGTES/MS (Coordenação do PMM-E) |
| **Folha Mensal Individualizada de Bolsas** | Folha é processada internamente no SGP/MS e FNS; não é divulgada no Portal da Transparência | Impede mensuração da dose monetária efetivamente recebida (primeiro estágio causal) | FNS / SGTES / MS |
| **Histórico Completo de Spells e Desligamentos** | Dados públicos mostram apenas homologações iniciais e snapshot de sobreviventes | Impede cálculo rigoroso de taxas de evasão e sobrevivência a 90/120/180 dias | SGTES / MS |
| **Classificação Oficial Exata do IVS das Vagas** | Editais publicam apenas categoria de vulnerabilidade; 42,56% divergem do IVS 2010 contínuo | Exige transparência sobre o algoritmo e critérios de priorização aplicados | SGTES / MS |

---

## 6. Checklist de Verificação de Integridade e Idempotência

- [x] **Regra 1:** Nenhum arquivo bruto canônico em `data/` foi modificado (hashes de `ivs_ipea_2010_municipios.csv`, `pmm_especialistas_nominal.csv` e `pmm_especialistas_serie_historica.csv` conferidos).
- [x] **Regra 2:** Nenhum arquivo falso/sintético permanece em `data/raw/` (pastas `ivs_regra/` e `pagamentos/` limpas de mocks).
- [x] **Regra 3:** Linhas de código de rede insegura (`ssl._create_unverified_context`) foram removidas.
- [x] **Regra 4:** Scripts de aquisição executam de forma idempotente e determinística.
- [x] **Regra 5:** Relatórios de auditoria sincronizados com os manifestos JSON e documentados com links relativos funcionais.
- [x] **Regra 6:** Pipeline principal (`run_all.py`) e scripts de aquisição executam sem erros.

---

## 7. Decisão e Recomendações para a Etapa A06

Com o saneamento integral concluído com sucesso, os dados e metadados encontram-se prontos para o **Agente A06 (Construção do Painel Integrado e Tratamento de Dados)**.

### Recomendações para A06:
1. Utilizar a **Célula de Oferta Agregada (CNES–Curso)** como a chave primária de oferta nas análises de vagas.
2. Utilizar o **IVS 2010 contínuo do IPEA** como running variable padrão nos desenhos de descontinuidade de regressão.
3. Tratar a variável de incentivo financeiro como a **faixa anunciada nos editais** condicional à vaga ofertada.
4. Tratar qualquer análise individual de permanência e dose recebida como condicionada ao retorno do Pedido LAI estruturado pelo Agente A07.

```text
========================================================================================
STATUS FINAL: SANEAMENTO CONCLUÍDO COM SUCESSO (ENTRADAS APTAS PARA A06)
========================================================================================
```
