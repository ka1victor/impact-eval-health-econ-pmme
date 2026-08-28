# Auditoria e Inspeção do CNES Mensal (A05)

> **Data da Auditoria:** 28 de agosto de 2026 (revisado pós-saneamento)
> **Agente:** A05 — Aquisição e Inspeção do CNES Mensal
> **Escopo:** Avaliação de impacto do Programa Mais Médicos Especialistas (PMM-E / Lei 15.233/2025)
> **Janela Temporal do CNES:** Junho de 2024 a Julho de 2026 (26 competências planejadas; 3 inspecionadas no piloto)
> **Status:** Piloto de esquema concluído; dicionário e anatomia interna extraídos; diagnóstico de FTE e ponte administrativa documentados.

---

## 1. Sumário Executivo e Objetivos de A05

A missão do Agente A05 consiste em auditar, catalogar e inspecionar a base de dados mensal do **Cadastro Nacional de Estabelecimentos de Saúde (CNES)** mantida pelo DATASUS/Ministério da Saúde. O CNES mensal é o instrumento canônico no SUS para:
1. **Medir a força de trabalho médica e o Full-Time Equivalent (FTE) cadastral:** cargas horárias declaradas (ambulatorial, hospitalar e outras) por ocupação (CBO 2002 de 6 dígitos);
2. **Avaliar histórico e simultaneidade de vínculos:** vínculos anteriores e paralelos de profissionais alocados em municípios prioritários;
3. **Mapear a infraestrutura pré-tratamento:** baseline de capacidade física (leitos em `rlEstabComplementar`), tecnológica (equipamentos em `rlEstabEquipamento`) e assistencial (serviços especializados em `rlEstabServClass` e habilitações em `rlEstabSipac`);
4. **Verificar a estabilidade de esquema e integridade de chaves:** consistência dos microdados entre o período pré-oferta (202406), o início das chamadas públicas (202506) e o corte mais recente (202607).

### Conclusão Principal da Auditoria:
- **Disponibilidade Pública e Esquema:** As bases mensais do CNES são públicas e contêm todas as tabelas necessárias para calcular FTE cadastral agregado e estoque pré-tratamento de infraestrutura. O esquema revelou-se altamente estável entre 2024 e 2026 (com adições marginais documentadas).
- **Validação Cadastral dos Estabelecimentos:** 100,0% dos 518 estabelecimentos do snapshot nominal de ativos foram validados no CNES em 202607 (e 99,42% já constavam no baseline de 202406).
- **Limitação Crítica (A Ausência da Ponte PMM-E–CNES):** O CNES não possui nenhum campo, flag ou código de sub-vínculo público que identifique deterministicamente um bolsista do PMM-E. As bases públicas do PMM-E contêm CRM, Nome e CPF mascarado; o CNES contém CNS e Nome. A vinculação determinística é **inviável com dados estritamente públicos** e depende de chave administrativa via SGTES/LAI (Solicitação A07).

---

## 2. Catálogo Oficial e Janela de Aquisição

O catálogo oficial de bases de dados do CNES disponibiliza mensalmente o arquivo nacional `BASE_DE_DADOS_CNES_AAAAMM.ZIP` via servlet HTTP do DATASUS (`https://cnes.datasus.gov.br/pages/downloads/arquivosBaseDados.jsp`).

### 2.1 Grade Completa de Competências Planejadas (26 meses)

| Competência | Cobertura Temporal | Função no Desenho do Estudo | Status Atual |
|---|---|---|---|
| **202406** | Junho / 2024 | Baseline histórico de longo prazo (12 meses pré-ciclo 1) | **Piloto Preservado e Inspecionado** |
| `202407` a `202412` | Julho a Dezembro / 2024 | Painel pré-tratamento (tendências pré-programa) | Planejado no catálogo |
| `202501` a `202505` | Janeiro a Maio / 2025 | Dinâmica imediata pré-chamamento | Planejado no catálogo |
| **202506** | Junho / 2025 | Baseline imediato (1 mês antes da oferta do Ciclo 1) | **Piloto Preservado e Inspecionado** |
| `202507` a `202512` | Julho a Dezembro / 2025 | Início das alocações e entradas do Ciclo 1 | Planejado no catálogo |
| `202601` a `202606` | Janeiro a Junho / 2026 | Expansão para Ciclos 2 e 3 | Planejado no catálogo |
| **202607** | Julho / 2026 | Competência oficial mais recente disponível | **Piloto Preservado e Inspecionado** |

---

## 3. Protocolo de Aquisição, Idempotência e Criptografia

O script `scripts/aquisicao/a05_adquirir_cnes.py` implementa os seguintes critérios de segurança:
1. **Download Atômico e Verificação de Assinatura:** O fluxo grava em arquivo temporário `.zip.part`, valida o cabeçalho PK (`b"PK\x03\x04"`), testa a integridade interna via `zipfile.ZipFile.testzip()` e só então efetua a substituição atômica para o arquivo final.
2. **Idempotência Estrita:** Caso o arquivo já exista em `data/raw/cnes/`, o script valida sua integridade estrutural e calcula o hash SHA-256 sem rebaixar desnecessariamente.
3. **Cálculo de Digest SHA-256:** Todos os arquivos possuem hashes registrados no manifesto `output/aquisicao/a05_manifesto_cnes.json`.
4. **Isolamento de Arquivos Grandes:** Arquivos ZIP de grandes dimensões são mantidos no caminho físico do workspace (`data/raw/cnes/`) e excluídos do Git.

### 3.1 Tabela de Arquivos Inspecionados no Piloto

| Competência | Arquivo | Tamanho (Bytes) | SHA-256 | Validação ZIP |
|---|---|---:|---|:---:|
| **202406** | `BASE_DE_DADOS_CNES_202406.ZIP` | 594,371,169 | `10746d84f19d45f5ef6f89e74d616ae73e37e6dd7dfd3b026e1b93a519a22253` | OK (Íntegro) |
| **202506** | `BASE_DE_DADOS_CNES_202506.ZIP` | 639,832,653 | `b43d12780a1d2ad47ab244272912262fd3b3b59e08c5f2ae715abf2a318e95ba` | OK (Íntegro) |
| **202607** | `BASE_DE_DADOS_CNES_202607.ZIP` | 734,781,715 | `f4ad8a2b4a156a8be9f3e76fafaba9870b9165bc56e86ac23578ffb609755ec9` | OK (Íntegro) |

---

## 4. Anatomia dos Arquivos ZIP e Estrutura Real das Tabelas

Ao descompactar seletivamente os ZIPs mensais do DATASUS, identificou-se que a base do CNES é composta por arquivos estruturados em formato CSV delimitados por ponto-e-vírgula (`;`) codificados em Latin-1 (ISO-8859-1). Cada competência contém exatamente **117 tabelas relacionais**.

### 4.1 Principais Tabelas Encontradas e Nomenclatura Real

| Módulo Temático | Nome Real da Tabela no ZIP | Entidade Representada | Chaves de Junção |
|---|---|---|---|
| **Estabelecimento** | `tbEstabelecimentoAAAAMM.csv` | Cadastro geral da unidade de saúde | `CO_UNIDADE` (13 dígitos), `CO_CNES` (7 dígitos), `CO_MUNICIPIO_GESTOR` |
| **Carga Horária / Vínculo** | `tbCargaHorariaSusAAAAMM.csv` | Vínculo profissional–estabelecimento | `CO_UNIDADE`, `CO_PROFISSIONAL_SUS`, `CO_CBO` |
| **Dados do Profissional** | `tbDadosProfissionalSusAAAAMM.csv` | Cadastro individual de profissionais | `CO_PROFISSIONAL_SUS`, `CO_CNS`, `NO_PROFISSIONAL` |
| **Atividade Profissional** | `tbAtividadeProfissionalAAAAMM.csv` | Ocupação e especialidade (CBO) | `CO_CBO` |
| **Leitos Instalados** | `rlEstabComplementarAAAAMM.csv` / `tbLeito` | Capacidade e leitos SUS/Não SUS | `CO_UNIDADE`, `CO_LEITO`, `CO_TIPO_LEITO` |
| **Equipamentos** | `rlEstabEquipamentoAAAAMM.csv` / `tbEquipamento` | Equipamentos diagnósticos e cirúrgicos | `CO_UNIDADE`, `CO_EQUIPAMENTO` |
| **Serviços Especializados** | `rlEstabServClassAAAAMM.csv` / `tbServicoEspecializado` | Serviços e ambulatórios especializados | `CO_UNIDADE`, `CO_SERVICO`, `CO_CLASSIFICACAO` |
| **Habilitações** | `rlEstabSipacAAAAMM.csv` / `tbSubGruposHabilitacao` | Habilitações SUS de alta complexidade | `CO_UNIDADE`, `COD_SUB_GRUPO_HABILITACAO` |

---

## 5. Dicionário de Dados e Estabilidade de Esquema

A comparação estrutural entre **202406**, **202506** e **202607** demonstrou estabilidade quase perfeita:
- **Tabelas 100% Estáveis (sem alteração de colunas):** `tbCargaHorariaSus` (18 colunas), `tbAtividadeProfissional` (6 colunas), `rlEstabComplementar` (10 colunas), `rlEstabServClass` (13 colunas), `tbEquipe` (30 colunas).
- **Alterações Incrementais Observadas no Catálogo do DATASUS:**
  - `tbEstabelecimento`: Inclusão da coluna `ST_COWORKING` em 202506 e 202607 (passou de 54 para 55 colunas);
  - `tbDadosProfissionalSus`: Inclusão de `NO_SOCIAL` em 202506 e sanitização do cabeçalho `CO_CPF` (passou de 9 para 10 colunas);
  - `rlEstabEquipamento`: Inclusão do campo `QT_SUS` em 202607;
  - `tbEquipamento`: Inclusão do identificador `NU_RENEM` (Registro Nacional de Equipamentos Médicos) em 202607;
  - `rlEstabSipac`: Inclusão do campo `DT_PORTARIA` em 202607.

### 5.1 Campos Essenciais para o Estudo PMM-E

#### Módulo Força de Trabalho e FTE (`tbCargaHorariaSus`):
- `CO_UNIDADE`: Chave primária do estabelecimento no CNES (13 dígitos).
- `CO_PROFISSIONAL_SUS`: Identificador do profissional no CNES (16 dígitos).
- `CO_CBO`: Código Brasileiro de Ocupações (6 dígitos). Para médicos especialistas:
  - `2251xx`: Médicos clínicos e especialidades clínicas (Cardiologia, Pediatria, Neurologia, etc.);
  - `2252xx`: Médicos cirúrgicos (Cirurgia Geral, Ortopedia, Ginecologia e Obstetrícia, etc.);
  - `2253xx`: Médicos diagnósticos e terapêuticos (Radiologia, Patologia, etc.).
- `QT_CARGA_HORARIA_AMBULATORIAL`: Horas semanais contratadas dedicadas ao ambulatório.
- `QT_CARGA_HORARIA_HOSPITALAR`: Horas semanais contratadas dedicadas à internação.
- `QT_CARGA_HORARIA_OUTROS`: Horas semanais em outras atividades (gestão/ensino).
- `TP_SUS_NAO_SUS`: Atendimento ao SUS (Sim/Não).
- `IND_VINCULACAO`: Indicador de vínculo.

#### Módulo Estabelecimentos (`tbEstabelecimento`):
- `CO_UNIDADE`: Chave interna do estabelecimento (13 dígitos).
- `CO_CNES`: Código público do estabelecimento no SUS (7 dígitos).
- `CO_MUNICIPIO_GESTOR`: Código IBGE do município gestor (6 dígitos).
- `CO_ESTADO_GESTOR`: UF gestora (2 dígitos).
- `TP_UNIDADE`: Tipologia (01=Posto de Saúde, 02=Centro de Saúde/UBS, 04=Policlínica/Ambulatório Especializado, 05=Hospital Geral, 07=Hospital Especializado, 22=Consultório Isolado).
- `CO_NATUREZA_JUR`: Mantenedora (Administração Pública Direta Municipal/Estadual, Entidade Beneficente, Empresa Privada).
- `TP_GESTAO`: Gestão Municipal (M), Estadual (E) ou Dupla (D).

---

## 6. Viabilidade Metodológica de Construção de FTE Líquido

### 6.1 Definição do FTE Cadastral
O Full-Time Equivalent (FTE) médico em cada município $m$ e competência $t$ para a especialidade médica $s$ é formalizado por:

$$\text{FTE}_{m,t,s} = \sum_{i \in \text{Médicos}_{m,t,s}} \frac{\text{QT\_CARGA\_HORARIA\_AMBULATORIAL}_{i,m,t} + \text{QT\_CARGA\_HORARIA\_HOSPITALAR}_{i,m,t}}{40}$$

### 6.2 O que o CNES Permite Medir:
1. **Estoque e FTE Médico por Município:** Variação no FTE total e no número de profissionais únicos atuando no município ao longo do tempo.
2. **Decomposição da Carga Horária:** Separação entre oferta ambulatorial especializada vs hospitalar.
3. **Detecção Contábil de Remanejamento Intra-SUS:** Médicos que já possuíam vínculo no mesmo município antes do programa e tiveram redução de carga em um CNES simultaneamente ao aumento em outro.

### 6.3 O que o CNES NÃO Mede (Cuidados Substantivos):
- **Carga Cadastrada vs Horas Reais:** O CNES registra a carga horária *declarada/contratada*, não ponto eletrônico, presença efetiva ou produtividade clínica.
- **Rotatividade Intra-mês:** O CNES é um retrato cadastral mensal consolidado; não registra faltas ou greves pontuais.

---

## 7. Diagnóstico da Ausência da Ponte Determinística PMM-E–CNES

```text
[Bases do PMM-E (SGP / Editais)]                  [Cadastro CNES Mensal (DATASUS)]
--------------------------------                  --------------------------------
- CRM + UF                                        - CNS (Cartão Nacional de Saúde)
- Nome do Médico                                  - Nome do Profissional
- CPF Mascarado (ex: ***.123.456-**)              - CO_PROFISSIONAL_SUS
- Faixa de Incentivo                              - CBO + Carga Horária Ambulatorial/Hosp
- CNES da Vaga Ofertada                           - CO_CNES / CO_UNIDADE
```

### O Desafio da Identificação Individual:
1. **Ausência de Chave Primária Compartilhada:** O edital do PMM-E não publica o número do CNS do médico; o CNES público não publica CRM nem CPF desmascarado.
2. **Inadequação do Pareamento por Nome:** A correspondência probabilística por string de nome normalizado introduz viés de homonímia, erros de digitação e falsos positivos em um universo nacional de mais de 500 mil médicos cadastrados.
3. **Implicação Causal:** Sem a ponte administrativa oficial (crosswalk fornecido pela SGTES com identificadores pseudonimizados), o pesquisador **não pode atribuir causalmente um vínculo individual específico ao PMM-E**.
4. **Bloqueio Causal:** A estimação de efeitos causais agregados ou individuais permanece dependente de validação econométrica e dados administrativos, enquanto a análise no nível do médico participante depende da liberação do Pedido Administrativo LAI (Agente A07).

---

## 8. Auditoria de Códigos CNES das Vagas do PMM-E no Cadastro Oficial

Verificou-se o cruzamento dos códigos `CO_CNES` presentes no cadastro nominal de ativos do PMM-E (`data/pmm_especialistas_nominal.csv`) em relação à base de dados oficial de estabelecimentos do CNES (`tbEstabelecimento`).

### Resultados do Cruzamento:
- **Total de CNES Únicos no Snapshot Nominal de Ativos:** 518 estabelecimentos.
- **Competência 202406:** 515 de 518 estabelecimentos localizados na `tbEstabelecimento` (99.42% de cobertura cadastral). Universo total de estabelecimentos no Brasil: 535,727.
- **Competência 202506:** 517 de 518 estabelecimentos localizados na `tbEstabelecimento` (99.81% de cobertura cadastral). Universo total de estabelecimentos no Brasil: 577,247.
- **Competência 202607:** 518 de 518 estabelecimentos localizados na `tbEstabelecimento` (100.00% de cobertura cadastral). Universo total de estabelecimentos no Brasil: 631,973.

Os 3 estabelecimentos do snapshot nominal que não constavam em 202406 passam a constar no cadastro oficial a partir da competência 202506 (compatível com inauguração, habilitação recente ou atualização cadastral de código), atingindo 100,00% de cobertura cadastral na competência 202607.

---

## 9. Instruções de Continuidade e Reprodutibilidade

1. **Localização dos Arquivos Brutos:** Os arquivos ZIP baixados residem no diretório:
   `C:/Users/camil/Desktop/Kauã/Insper/impact-eval-health-econ-pmme/data/raw/cnes`
2. **Execução do Piloto de Esquema:**
   ```bash
   python scripts/aquisicao/a05_adquirir_cnes.py --inspect-only
   ```
3. **Download Assíncrono do Painel Completo (26 meses):** Quando houver janela de execução apropriada em segundo plano:
   ```bash
   python scripts/aquisicao/a05_adquirir_cnes.py --full --confirm-large-download
   ```

