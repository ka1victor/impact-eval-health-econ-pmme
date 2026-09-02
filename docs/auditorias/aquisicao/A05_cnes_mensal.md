# Auditoria e Inspeção do CNES Mensal (A05)

> **Adendo prospectivo de 30/08/2026:** a Nota Técnica nº
> 59/2026-CGPLAD/DEGEPS/SGTES/MS definiu uma assinatura específica para o
> registro dos participantes do PMM-E no CNES: `IND_VINCULACAO=070102`, CNPJ de
> detalhamento `00394544012787`, CBO do Anexo I e cargas horárias próprias. O
> `tbCargaHorariaSus` público contém esses campos, porém o pipeline A05 não
> preservou o CNPJ e a implementação da regra ainda não foi validada. Portanto,
> a limitação descrita abaixo continua correta para os Parquets A05, enquanto o
> ciclo 3 ganha uma rota prospectiva a ser auditada em
> [`12_estrategia_causal_prospectiva_ciclo3.md`](../../05_identificacao/12_estrategia_causal_prospectiva_ciclo3.md).

> **Data da Auditoria:** 28 de agosto de 2026 (revisado pós-saneamento)
> **Agente:** A05 — Aquisição e Inspeção do CNES Mensal
> **Escopo:** Avaliação de impacto do Programa Mais Médicos Especialistas (PMM-E / Lei 15.233/2025)
> **Janela Temporal do CNES:** Junho de 2024 a Julho de 2026 (26 competências planejadas; 3 inspecionadas no piloto)
> **Status:** Piloto de esquema e aquisição pública parcial; 3 de 26 competências adquiridas.

---

## 1. Sumário Executivo e Objetivos de A05

A missão do Agente A05 consiste em auditar, catalogar e inspecionar a base de dados mensal do **Cadastro Nacional de Estabelecimentos de Saúde (CNES)** mantida pelo DATASUS/Ministério da Saúde. O CNES mensal é o instrumento canônico no SUS para:
1. **Medir a força de trabalho médica e o Full-Time Equivalent (FTE) cadastral:** cargas horárias declaradas (ambulatorial, hospitalar e outras) por ocupação (CBO 2002 de 6 dígitos);
2. **Avaliar histórico e simultaneidade de vínculos:** vínculos anteriores e paralelos de profissionais alocados em municípios prioritários;
3. **Mapear a infraestrutura pré-tratamento:** baseline de capacidade física (leitos em `rlEstabComplementar`), tecnológica (equipamentos em `rlEstabEquipamento`) e assistencial (serviços especializados em `rlEstabServClass` e habilitações em `rlEstabSipac`);
4. **Verificar a estabilidade de esquema e integridade de chaves:** consistência dos microdados entre o período pré-oferta (202406), o início das chamadas públicas (202506) e o corte mais recente (202607).

### Conclusão Principal da Auditoria:
- **Aquisição parcial:** somente as competências 202406, 202506 e 202607 foram preservadas e inspecionadas. Elas servem para validar esquema e cobertura cadastral, não para formar um painel de avaliação.
- **Dois universos separados:** o snapshot nominal contém 1,480 registros e 518 CNES distintos; os quadros finais escolhidos em A01 são relidos diretamente e auditados por versão.
- **Limitação crítica:** o CNES público não identifica deterministicamente participantes do PMM-E. Cadastro, carga declarada e existência do estabelecimento não demonstram presença, horas realizadas ou efeito do programa.

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
3. **Descrição de mudanças cadastrais:** com painel completo, seria possível descrever variações simultâneas de carga declarada entre vínculos; classificá-las como remanejamento provocado pelo programa exigiria identificação e desenho adicionais.

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
3. **Implicação de mensuração:** sem uma ponte administrativa oficial, não é possível afirmar que um vínculo público específico pertence a um participante do PMM-E.
4. **Limite deste piloto:** a disponibilidade do CNES não identifica tratamento nem valida estratégia causal; isso depende de decisão posterior do portão e, para análises individuais, de ponte administrativa segura.

---

## 8. Auditoria Separada dos Dois Universos

A05 relê as planilhas XLSX reais selecionadas por A01. O snapshot nominal e os quadros de oferta têm unidades diferentes e não são intercambiáveis.

### 8.1 Universo 1 — snapshot nominal de participantes ativos

Fonte: `data/pmm_especialistas_nominal.csv` (`76237f4cb6bf7e9aaccbf22ea443e1070c889c05a0357a3c1cb34ee50f58fc7d`).

| Linhas de participantes | Linhas com CNES válido | CNES distintos | Repetições de CNES entre registros | Perdas de normalização |
|---:|---:|---:|---:|---|
| 1,480 | 1,480 | 518 | 962 | `{}` |

Uma linha representa participante ativo na data de referência. Um CNES repetido pode refletir pessoas distintas no mesmo estabelecimento; não representa, por si só, duplicidade de vaga.

### 8.2 Universo 2 — células CNES–curso dos quadros finais de A01

| Versão escolhida | Arquivo-fonte | Linhas/células lidas | Células válidas | CNES distintos | Células duplicadas | Repetições de CNES entre células | Perdas CNES/curso | Vagas físicas na versão |
|---|---|---:|---:|---:|---:|---:|---|---:|
| Ciclo 1, chamada 1 — quadro original (versão de oferta disponível) | `data/raw/aquisicao/vagas/2025_ciclo1_chamada1_vagas.xlsx` | 1,295 | 1,295 | 460 | 0 | 835 | `{}` | 1,823 |
| Ciclo 1, chamada 2 — quadro de cadastro de reserva | `data/raw/pmm_e/2025_ciclo1_chamada2_vagas_e_alocados.xlsx` | 1,762 | 1,762 | 638 | 0 | 1,124 | `{}` | 2,896 |
| Ciclo 2, chamada 1 — quadro retificado final de 19/03/2026 | `data/raw/pmm_e/2026_ciclo2_chamada1_vagas_retificadas.xlsx` | 1,547 | 1,547 | 685 | 0 | 862 | `{}` | 2,889 |
| Ciclo 2, chamada 2 — quadro publicado em 16/04/2026 | `data/raw/pmm_e/2026_ciclo2_chamada2_vagas.xlsx` | 1,039 | 1,039 | 532 | 0 | 507 | `{}` | 1,992 |
| Ciclo 3, chamada 1 — quadro retificado de 24/07/2026 | `data/raw/pmm_e/2026_ciclo3_chamada1_vagas_retificadas.xlsx` | 2,293 | 2,293 | 1,262 | 0 | 1,031 | `{}` | 5,131 |

A união das 5 versões escolhidas contém **1,930 estabelecimentos distintos**. Esse número serve apenas como denominador cadastral. Células e vagas não são somadas entre chamadas porque ofertas podem ser reapresentadas.

### 8.3 Cobertura nas três competências piloto

| Competência | Snapshot ativo | União dos quadros A01 | Universo nacional em `tbEstabelecimento` |
|---|---:|---:|---:|
| 202406 | 515/518 (99.42%) | 1,904/1,930 (98.65%) | 535,727 |
| 202506 | 517/518 (99.81%) | 1,927/1,930 (99.84%) | 577,247 |
| 202607 | 518/518 (100.00%) | 1,930/1,930 (100.00%) | 631,973 |

Cobertura indica somente que o código aparece no cadastro daquela competência. Alterações entre competências não permitem inferir inauguração, início de atividade, presença de participante ou efeito do PMM-E sem observar e documentar esses eventos.

#### Cobertura dos quadros A01 por versão

| Versão | 202406 | 202506 | 202607 |
|---|---:|---:|---:|
| Ciclo 1, chamada 1 — quadro original (versão de oferta disponível) | 459/460 (99.78%) | 460/460 (100.00%) | 460/460 (100.00%) |
| Ciclo 1, chamada 2 — quadro de cadastro de reserva | 635/638 (99.53%) | 638/638 (100.00%) | 638/638 (100.00%) |
| Ciclo 2, chamada 1 — quadro retificado final de 19/03/2026 | 681/685 (99.42%) | 685/685 (100.00%) | 685/685 (100.00%) |
| Ciclo 2, chamada 2 — quadro publicado em 16/04/2026 | 528/532 (99.25%) | 532/532 (100.00%) | 532/532 (100.00%) |
| Ciclo 3, chamada 1 — quadro retificado de 24/07/2026 | 1,240/1,262 (98.26%) | 1,259/1,262 (99.76%) | 1,262/1,262 (100.00%) |

---

## 9. Instruções de Continuidade e Reprodutibilidade

1. **Localização dos arquivos brutos:** `data/raw/cnes/`.
2. **Execução do Piloto de Esquema:**
   ```bash
   python scripts/aquisicao/a05_adquirir_cnes.py --inspect-only
   ```
3. **Painel integral adiado:** as 23 competências restantes não devem ser baixadas até existir ponte PMM-E–CNES ou decisão explícita do portão sobre o desenho e o denominador necessários.
