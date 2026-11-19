# Dossiê Técnico: Bases de Dados de Saúde no Brasil e Aplicação na Avaliação de Impacto do PMM-E

> **Classificação:** Documento de Referência Metodológica e Institucional (Base Canônica de Dados)  
> **Data de Atualização e Auditoria:** Setembro de 2026  
> **Projeto:** Avaliação de Impacto do Programa Mais Médicos Especialistas (PMM-E / Lei nº 15.233/2025)  
> **Finalidade:** Fornecer embasamento formal, legal e técnico-operacional sobre todos os sistemas de informação em saúde do Brasil, documentando proveniência, unidade de observação, mecanismos de alimentação, regimes de acesso, dicionários canônicos, limitações econométricas e seu papel específico no desenho causal do projeto.

---

## 1. Marco Regulatório e Arquitetura Institucional da Informação em Saúde no Brasil

A governança dos dados de saúde no Brasil está enraizada no arcabouço constitucional e legal do Sistema Único de Saúde (SUS), caracterizado por uma estrutura federativa descentralizada, tripartite e de comando único em cada esfera de governo.

### 1.1 Fundamentos Legais e Normativos

1. **Constituição da República Federativa do Brasil de 1988 (CF/88):**
   - **Art. 196 a 200:** Estabelecem a saúde como direito de todos e dever do Estado, integrando ações e serviços públicos em rede regionalizada e hierarquizada, com direção descentralizada. O art. 200, incisos V e VI, confere expressamente ao SUS a competência de incrementar o desenvolvimento científico e tecnológico e fiscalizar serviços, o que demanda sistemas nacionais de monitoramento e auditoria.
2. **Lei Orgânica da Saúde (Lei nº 8.080/1990):**
   - **Art. 6º, inciso I, alínea "a":** Inclui no campo de atuação do SUS a vigilância sanitária e epidemiológica, além de ações voltadas à saúde do trabalhador.
   - **Arts. 15, 16, 17 e 18:** Definem as atribuições comuns e específicas da União, dos Estados e dos Municípios. À União (Ministério da Saúde) compete a definição e coordenação dos sistemas de informação de saúde de âmbito nacional; aos Estados, a coordenação e agregação descentralizada; aos Municípios, a alimentação direta e gerência dos serviços na ponta.
   - **Art. 47:** Condiciona as transferências voluntárias e os repasses fundo a fundo à regularidade da prestação de contas e à alimentação contínua dos sistemas de informação federais.
3. **Decreto Federal nº 7.508/2011:**
   - Regulamenta a Lei nº 8.080/1990 para dispor sobre a organização do SUS, o planejamento da saúde, a assistência à saúde e a articulação interfederativa.
   - Cria o **Mapa da Saúde** (descrição geográfica da distribuição de recursos humanos, leitos e serviços) e formaliza o **Contrato Organizativo da Ação Pública da Saúde (COAP)**, exigindo indicadores padronizados de cobertura, resolutividade e tempo de espera.
4. **Legislação Específica do Programa Mais Médicos e PMM-E:**
   - **Lei Federal nº 12.871/2013:** Instituiu originalmente o Programa Mais Médicos (focado em Atenção Primária à Saúde).
   - **Lei Federal nº 15.233/2025:** Alterou a Lei nº 12.871/2013 para introduzir a Estratégia e o Projeto Mais Médicos Especialistas (arts. 22-D a 22-F), voltados expressamente a reduzir filas e tempos de espera para consultas e exames especializados em regiões prioritárias.
   - **Portaria GM/MS nº 7.177/2025:** Regulamenta o PMM-E como integração ensino-serviço (formação especializada em serviço).
   - **Portaria GM/MS nº 7.266/2025:** Institui o Programa Agora Tem Especialistas, do qual o PMM-E é componente de provimento de força de trabalho.
   - **Nota Técnica nº 59/2026-CGPLAD/DEGEPS/SGTES/MS:** Fixa os parâmetros cadastrais específicos de registro dos médicos bolsistas do PMM-E no CNES.
5. **Regimes de Acesso, Transparência e Privacidade:**
   - **Lei nº 12.527/2011 (Lei de Acesso à Informação — LAI):** Determina a publicidade como preceito geral e o sigilo como exceção. Regula o fornecimento de dados públicos governamentais.
   - **Lei nº 13.709/2018 (Lei Geral de Proteção de Dados Pessoais — LGPD):** Classifica dados de saúde como dados pessoais sensíveis (art. 5º, II). Autoriza o tratamento para tutela da saúde (art. 7º, VIII) e realização de estudos por órgãos de pesquisa (art. 7º, IV e art. 16, II), exigindo preferencialmente a anonimização ou pseudonimização.

### 1.2 O Papel do DATASUS e o Fluxo Federativo da Informação

O **Departamento de Informática do Sistema Único de Saúde (DATASUS)**, vinculado à Secretaria Executiva do Ministério da Saúde (originalmente instituído pelo Decreto nº 100/1991 e mantido nas estruturas regimentais subsequentes), atua como o custodiante e operador técnico da infraestrutura computacional do SUS.

O fluxo federativo segue a lógica tripartite:
1. **Ponta Operacional:** Unidades Básicas de Saúde (UBS), Centros de Especialidades Odontológicas (CEO), Policlínicas, Unidades de Pronto Atendimento (UPA), Hospitais Gerais e Especializados (públicos, filantrópicos ou contratualizados privados).
2. **Captação Municipal:** As Secretarias Municipais de Saúde (SMS) coletam os arquivos magnéticos de produção, validam as regras de faturamento e enviam as remessas eletrônicas para o nível federal.
3. **Validação Estadual:** As Secretarias Estaduais de Saúde (SES) validam estabelecimentos sob gestão estadual e consolidam os tetos orçamentários da Programação Pactuada e Integrada (PPI) ou do Plano Diretor de Regionalização (PDR).
4. **Processamento Central (DATASUS):** As remessas mensais (denominadas **competências**) são processadas contra os bancos de dados de cadastro (CNES) e de regras de faturamento (tabela SIGTAP). Os dados são validados para fins de liquidação financeira pelo Fundo Nacional de Saúde (FNS) e simultaneamente compilados para disseminação estatística.

---

## 2. Dossiê Detalhado dos Sistemas e Bases de Dados de Saúde

```
                                SISTEMAS DE INFORMAÇÃO DO SUS
 ┌───────────────────────────────┬───────────────────────────────┬───────────────────────────────┐
 │   CAPACIDADE & CADASTRO       │     PRODUÇÃO & ASSISTÊNCIA    │   VIGILÂNCIA & REGULAÇÃO      │
 ├───────────────────────────────┼───────────────────────────────┼───────────────────────────────┤
 │ • CNES (Recursos e Equipes)   │ • SIA/SUS (Ambulatorial/APAC) │ • SISREG (Filas e Regulação)  │
 │ • SGTES/PMM-E (Bolsas/Vagas)  │ • SIH/SUS (Internações/AIH)   │ • SIM (Mortalidade - DO)      │
 │ • SIGTAP (Tabela Unificada)   │ • SISAB/e-SUS (Atenção Básica)│ • SINASC (Nascidos Vivos - DN)│
 │ • RNDS / CADSUS (Identidade)  │ • BPA-I / BPA-C (Procedimentos│ • SINAN (Agravos Notificáveis)│
 └───────────────────────────────┴───────────────────────────────┴───────────────────────────────┘
```

---

### 2.1 CNES — Cadastro Nacional de Estabelecimentos de Saúde

* **Ato Instituidor e Base Normativa:** Criado pela Portaria SAS/MS nº 511/2000; consolidado na Portaria de Consolidação GM/MS nº 1/2017 (Origem: PRT MS/GM 1.646/2015).
* **Órgão Custodiante:** Secretaria de Atenção Especializada à Saúde (SAES/MS) e processamento pelo DATASUS.
* **Grão (Unidade de Observação):**
  - Nível Estabelecimento: `CO_CNES` (código de 7 dígitos).
  - Nível Vínculo/Profissional: `CO_CNES` + `CO_PROFISSIONAL_SUS` (ou CNS) + `CBO` (Classificação Brasileira de Ocupações) por competência mensal (`AAAAMM`).
* **Origem e Mecanismo de Alimentação:**
  - Cadastramento compulsório de todo e qualquer estabelecimento de saúde em território nacional (público, filantrópico ou estritamente privado, com ou sem fins lucrativos).
  - As secretarias municipais e estaduais alimentam o aplicativo local do CNES e transmitem a base mensal ao DATASUS. Nenhuma unidade de saúde pode faturar no SUS sem CNES regular.
* **Arquivos e Tabelas Oficiais Chave:**
  - `tbCargaHorariaSusAAAAMM.csv` (ou `.dbc`): Contém `CO_CNES`, `CO_PROFISSIONAL_SUS`, `CBO`, `IND_VINCULACAO`, `TP_SUS_NAO_SUS`, `QT_CARGA_HORARIA_AMBULATORIAL`, `QT_CARGA_HORARIA_OUTROS`, `QT_CARGA_HORARIA_HOSPITALAR`.
  - `tbEstabelecimentoAAAAMM.csv`: Razão social, nome fantasia, natureza jurídica, esfera administrativa, coordenadas geográficas, município IBGE (`CO_MUNICIPIO_GESTOR`).
  - `rlEstabComplementarAAAAMM.csv`: Mapeamento de leitos por especialidade e tipo (cirúrgico, clínico, UTI tipo I, II, III).
  - `rlEstabEquipamentoAAAAMM.csv`: Código do equipamento (tomógrafo, mamógrafo, aparelho de ultrassom), quantidade existente e quantidade em uso.
* **Regime de Acesso e Disseminação:**
  - **Público e Aberto.** Disseminado em arquivos mensais completos no formato compactado `.ZIP` (contendo arquivos CSV e layouts) no portal `cnes.datasus.gov.br` e em arquivos `.DBC` via FTP oficial (`ftp://ftp.datasus.gov.br/dissemin/publicos/CNES/`).
* **Papel em Economia da Saúde e Pesquisa:**
  - Medição de oferta e Full-Time Equivalent (FTE) médico;
  - Densidade de especialistas por 100 mil habitantes;
  - Infraestrutura física prévia instalada como mediador ou restrição de capacidade.
* **Armadilhas e Limitações Econométricas:**
  1. *Descompasso Cadastral (Lag de Desligamento):* Profissionais que se desligam da unidade física por vezes permanecem cadastrados no CNES por meses se a gestão municipal não homologar a baixa cadastral.
  2. *Vínculo vs. Exercício Real:* Mede contrato/vínculo formal declarado, não biometria ou horas efetivamente trabalhadas no consultório.
  3. *Inexistência de CPF aberto:* Nas disseminações públicas modernas, o DATASUS oculta ou mascara o CPF e fornece chaves sintéticas ou o CNS (Cartão Nacional de Saúde), exigindo tratamento para painéis de trajetórias individuais de médicos.

---

### 2.2 SIA/SUS — Sistema de Informações Ambulatoriais

* **Ato Instituidor e Base Normativa:** Instituído na década de 1990 para operacionalizar os repasses federais da assistência ambulatorial; normatizado pela Portaria SAS/MS nº 111/2010 e consolidado na Portaria de Consolidação GM/MS nº 1/2017.
* **Órgão Custodiante:** SAES/MS e DATASUS.
* **Grão (Unidade de Observação):**
  - BPA Consolidado (`BPA-C`): Agregado por estabelecimento (`CO_CNES`) + procedimento SIGTAP (`CO_PROCEDIMENTO`) + competência.
  - BPA Individualizado (`BPA-I`): Registro individual de procedimento ambulatorial de média complexidade, contendo paciente (anonimizado), município de residência, idade, sexo, CID-10 e data.
  - APAC (Autorização de Procedimentos de Alta Complexidade): Laudo individualizado e sequencial para terapias prolongadas (oncologia clínica/radioterapia, terapia renal substitutiva/hemodiálise, bariatria, dispensação de medicamentos do componente especializado).
* **Origem e Mecanismo de Alimentação:**
  - Prestadores ambulatoriais registram cada consulta especializada, exame diagnóstica e terapia no Sistema de Faturamento Ambulatorial (SIA). O envio é obrigatório para processar o teto financeiro de Média e Alta Complexidade (MAC).
* **Arquivos e Tabelas Oficiais Chave:**
  - `PAUFyymm.dbc` (Produção Ambulatorial Geral): Procedimento, quantidade aprovada, quantidade apresentada, valores ambulatoriais, município de residência (`PA_UFMUN`) e do prestador (`PA_GESTÃO`).
  - `AQ/AR/AT/AM...UFyymm.dbc`: Arquivos específicos de APAC para quimioterapia, radioterapia, nefrologia e medicamentos excepcionais.
* **Regime de Acesso e Disseminação:**
  - **Público e Aberto.** Microdados em arquivos `.dbc` mensais por Unidade da Federação no FTP oficial (`ftp://ftp.datasus.gov.br/dissemin/publicos/SIASUS/200801_/Dados/`) e Tabnet.
* **Papel em Economia da Saúde:**
  - Avaliação de produção atribuível (exames diagnósticos, biópsias, ultrassonografias, endoscopias, consultas ambulatoriais);
  - Análise de fluxos espaciais de pacientes (município de residência versus município prestador);
  - Tempo entre suspeita e início do tratamento em oncologia (APAC).
* **Armadilhas e Limitações Econométricas:**
  1. *Teto Orçamentário e "Glosas":* O prestador pode realizar atendimentos acima do teto físico-financeiro pactuado; se a cota esgotar, procedimentos excedentes podem não ser faturados ou serem empurrados para a competência seguinte.
  2. *Procedimentos em BPA-C:* Parte relevante das consultas básicas e exames laboratoriais mais simples é registrada em lote agregado sem identificação do paciente, impedindo rastreamento longitudinal na atenção primária.
  3. *Mudanças de Codificação na Tabela SIGTAP:* Procedimentos podem ser desmembrados ou renumerados pelo Ministério da Saúde, criando descontinuidades artificiais nas séries temporais se não houver harmonização histórica.

---

### 2.3 SIH/SUS — Sistema de Informações Hospitalares

* **Ato Instituidor e Base Normativa:** Operacionalizado desde o antigo INAMPS através da Autorização de Internação Hospitalar (AIH); regulamentado pela Portaria SAS/MS nº 284/2007 e normativas vigentes da SAES/MS.
* **Órgão Custodiante:** SAES/MS e DATASUS.
* **Grão (Unidade de Observação):**
  - AIH individual (`N_AIH` de 13 dígitos). Cada linha corresponde a uma internação hospitalar encerrada (por alta, transferência ou óbito) faturada naquela competência.
* **Origem e Mecanismo de Alimentação:**
  - O médico assistente emite o laudo de solicitação de internação; o órgão regulador emite o número da AIH; o hospital alimenta os dados clínicos e os procedimentos realizados durante a estada hospitalar e remete o espelho de faturamento para auditoria e pagamento.
* **Arquivos e Tabelas Oficiais Chave:**
  - `RDUFyymm.dbc` (Reduzida da AIH): Contém as variáveis essenciais:
    - `MUNIC_RES`: Município de residência do paciente (código IBGE de 6 dígitos);
    - `MUNIC_MOV`: Município do estabelecimento hospitalar prestador;
    - `CNES`: Código do hospital;
    - `CAR_INT`: Caráter da internação (`01` = Eletiva; `02` = Urgência/Emergência; `03` = Acidente; etc.);
    - `PROC_REA`: Procedimento cirúrgico ou clínico efetivamente realizado;
    - `DIAG_PRINC` e `DIAG_SECUN`: Códigos de diagnóstico segundo a CID-10;
    - `MORTE`: Indicador de óbito intra-hospitalar (`1` = Sim, `0` = Não);
    - `QT_DIARIAS`: Tempo total de permanência em dias;
    - `DIAR_UTI`: Dias de internação em Unidade de Terapia Intensiva;
    - `VAL_TOT`: Valor total pago pelo SUS ao prestador.
  - `SPUFyymm.dbc`: Serviços Profissionais vinculados à AIH (identifica os atos médicos complementares e cirúrgicos).
* **Regime de Acesso e Disseminação:**
  - **Público e Aberto.** Microdados em arquivos `.dbc` mensais por UF via FTP (`ftp://ftp.datasus.gov.br/dissemin/publicos/SIHSUS/200801_/Dados/`) e Tabnet.
* **Papel em Economia da Saúde:**
  - Medir resolutividade hospitalar local versus evasão para polos regionais;
  - Avaliação de conversão de urgência em eletiva (indicador clássico de acesso ambulatorial prévio oportuno);
  - Internações por Condições Sensíveis à Atenção Primária (ICSAP);
  - Custos diretos hospitalares do SUS.
* **Armadilhas e Limitações Econométricas:**
  1. *Ausência de Internações Estritamente Privadas:* O SIH cobre apenas internações financiadas pelo SUS (leitos públicos ou leitos privados contratualizados pelo SUS). Internações cobertas por planos de saúde privados ou desembolso direto (*out-of-pocket*) não constam no SIH.
  2. *Dependência de Alta:* A AIH é faturada no mês de encerramento da internação. Internações de longuíssima permanência aparecem com atraso em relação à data de admissão.
  3. *Incentivo ao Upcoding Financeiro:* Como o pagamento depende do procedimento e complexidade da AIH, hospitais podem ter incentivo a codificar procedimentos de maior valor de ressarcimento.

---

### 2.4 SISREG e Sistemas Estaduais/Municipais de Regulação (CROSS, etc.)

* **Ato Instituidor e Base Normativa:** Política Nacional de Regulação do SUS instituída pela Portaria GM/MS nº 1.559/2008; consolidada na Portaria de Consolidação GM/MS nº 2/2017.
* **Órgão Custodiante:** Secretarias Municipais e Estaduais de Saúde e DATASUS (para os municípios que utilizam a versão federal SISREG III).
* **Grão (Unidade de Observação):**
  - Solicitação individual de regulação (chave da solicitação). Acompanha o ciclo de vida: data da solicitação pelo médico solicitante na UBS, data da autorização pelo médico regulador, classificação de risco, data do agendamento, comparecimento ou cancelamento.
* **Origem e Mecanismo de Alimentação:**
  - Médicos da atenção primária geram a guia de referência especializada; médicos reguladores avaliam a indicação clínica e priorizam a fila; o paciente é notificado e encaminhado.
* **Principais Variáveis:**
  - Data de solicitação, data de regulação, data de agendamento, data de atendimento;
  - Tempo de espera em dias (delta entre solicitação e execução);
  - Especialidade demandada / código do procedimento;
  - Status da vaga: atendida, cancelada por absenteísmo (no-show), cancelada administrativamente por óbito, desistência ou limpeza de fila.
* **Regime de Acesso e Disseminação:**
  - **Restrito.** Não existe repositório público de microdados abertos do SISREG em âmbito nacional no DATASUS.
  - O acesso depende de **requisições via LAI (Lei nº 12.527/2011)** a municípios ou estados específicos, ou convênios de cooperação técnica com anonimização.
* **Papel em Economia da Saúde:**
  - É a **métrica de ouro para avaliar tempo de espera real** (o estimando legal da Lei 15.233/2025).
* **Armadilhas e Limitações Econométricas:**
  1. *Viés de Limpeza de Fila (Queue Purging):* Municípios frequentemente promovem "mutirões de recadastramento" em que milhares de pacientes antigos são excluídos por não responderem ao contato telefônico, gerando uma redução artificial do tempo médio ou do estoque da fila.
  2. *Heterogeneidade de Software:* Estados populosos operam sistemas próprios (ex.: CROSS em São Paulo; Regula SUS no RS; SIGA Saúde em capitais), o que impede a construção direta de um painel nacional homogêneo sem harmonização caso a caso.

---

### 2.5 SIM — Sistema de Informações sobre Mortalidade

* **Ato Instituidor e Base Normativa:** Criado em 1975 pelo Ministério da Saúde; padronizado pela Portaria GM/MS nº 116/2009 e Portaria de Consolidação GM/MS nº 1/2017.
* **Órgão Custodiante:** Secretaria de Vigilância em Saúde e Ambiente (SVSA/MS) e DATASUS.
* **Grão (Unidade de Observação):**
  - Declaração de Óbito (DO) individual (`NUMERODO` de 8 dígitos).
* **Origem e Mecanismo de Alimentação:**
  - Médicos atestantes preenchem a DO obrigatoriamente para emissão da certidão de óbito em cartório de registro civil. As Secretarias Municipais de Saúde recolhem e digitam as declarações no módulo municipal do SIM.
* **Arquivos e Tabelas Oficiais Chave:**
  - `DOUFyymm.dbc` (ou arquivos anuais consolidados `DOBRaaaa.dbc`):
    - `DTOBITO`: Data do óbito;
    - `CODMUNRES`: Município de residência do falecido;
    - `CODMUNOCOR`: Município onde ocorreu o óbito;
    - `CAUSABAS`: Causa básica da morte segundo classificação CID-10 a 4 dígitos;
    - `IDADE`, `SEXO`, `RACACOR`, `ESC`: Variáveis sociodemográficas do falecido.
* **Regime de Acesso e Disseminação:**
  - **Público e Aberto.** Microdados anuais desidentificados no FTP (`ftp://ftp.datasus.gov.br/dissemin/publicos/SIM/CID10/DORES/`) e OpenDataSUS.
* **Papel em Economia da Saúde:**
  - Desfechos clínicos duros de longo prazo (mortalidade prematura, mortes por causas evitáveis, mortalidade cardiovascular ou oncológica).
* **Limitações no Curto Prazo:**
  - *Tempo Biológico Longo:* O impacto do provimento de um cardiologista ou cirurgião não altera a mortalidade geral de um município em uma janela de 6 a 12 meses.
  - *Causas Mal Definidas:* Municípios com baixa cobertura médica apresentam percentual elevado de óbitos registrados no Capítulo XVIII da CID-10 (sintomas e sinais mal definidos), o que pode gerar causalidade reversa (o envio de médicos melhora o diagnóstico do atestado de óbito, aumentando aparentemente a mortalidade por causas específicas).

---

### 2.6 SINASC — Sistema de Informações sobre Nascidos Vivos

* **Ato Instituidor e Base Normativa:** Implantado formalmente em 1990; regulamentado pela Portaria GM/MS nº 116/2009.
* **Órgão Custodiante:** SVSA/MS e DATASUS.
* **Grão (Unidade de Observação):**
  - Declaração de Nascido Vivo (DN) individual (`NUMERODN`).
* **Origem e Mecanismo de Alimentação:**
  - Preenchida pelo hospital/maternidade onde ocorreu o parto ou pelo oficial de registro no caso de partos domiciliares.
* **Arquivos e Tabelas Oficiais Chave:**
  - `DNUFyymm.dbc` ou `DNBRaaaa.dbc`:
    - `PESO`: Peso ao nascer em gramas (indicador de baixo peso < 2500g);
    - `APGAR1` e `APGAR5`: Escore de vitalidade no primeiro e quinto minutos de vida;
    - `CONSULTAS`: Número de consultas de pré-natal realizadas;
    - `PARTO`: Tipo de parto (vaginal ou cesariana);
    - `GESTACAO`: Semanas de idade gestacional (prematuridade).
* **Regime de Acesso e Disseminação:**
  - **Público e Aberto.** Microdados anuais no FTP do DATASUS (`ftp://ftp.datasus.gov.br/dissemin/publicos/SINASC/1996_/Dados/DNRES/`).
* **Papel no Estudo:**
  - Utilizado em avaliações de programas de Atenção Primária (ex.: PMM clássico). Para o PMM-E, seria relevante caso fossem providos ginecologistas-obstetras em regiões sem cobertura de parto de risco habitual, mas está fora do escopo da Versão 1.

---

### 2.7 SISAB / e-SUS APS — Atenção Primária à Saúde

* **Ato Instituidor e Base Normativa:** Instituído pela Portaria GM/MS nº 1.412/2013, que implantou a estratégia e-SUS Atenção Básica, e Portarias de Consolidação nº 1 e 2/2017.
* **Órgão Custodiante:** Secretaria de Atenção Primária à Saúde (SAPS/MS) e DATASUS.
* **Grão (Unidade de Observação):**
  - Atendimento individual no Prontuário Eletrônico do Cidadão (PEC) ou ficha simplificada (CDS) por equipe da Estratégia Saúde da Família (ESF).
* **Origem:**
  - Alimentação diária pelos profissionais da atenção básica nas UBS de todo o país.
* **Regime de Acesso e Disseminação:**
  - Microdados nominais são **estritamente sigilosos**.
  - Dados tabulares agregados (por município e equipe) são públicos no portal de relatórios do SISAB (`sisab.saude.gov.br`).
* **Relação com o PMM-E:**
  - O PMM-E trata de **atenção especializada** (médicos com RQE e residência médica alocados em ambulatórios de especialidades e hospitais), enquanto o SISAB monitora primariamente a atenção básica. Não constitui a fonte principal de observação do especialista, embora o encaminhamento nasça na UBS.

---

### 2.8 CADSUS e RNDS — Base Nacional do Cidadão

* **Ato Instituidor e Base Normativa:** Portaria GM/MS nº 940/2011 (CADSUS) e Portaria GM/MS nº 1.434/2020 (institui a Rede Nacional de Dados em Saúde — RNDS).
* **Órgão Custodiante:** Secretaria de Informação e Saúde Digital (SEIDIGI/MS).
* **Conteúdo:** Identificador único do usuário no SUS (Cartão Nacional de Saúde — CNS e CPF), vínculo demográfico, registros clínicos eletrônicos interoperáveis.
* **Regime de Acesso:**
  - **Sigiloso.** Acesso restrito protegido pela LGPD e segredo médico. Pesquisas científicas de ligação de bancos com base no CADSUS dependem de protocolo ético submetido à Plataforma Brasil (CEP/CONEP) e celebração de Termo de Compromisso de Utilização de Dados (TCUD) com o Ministério da Saúde ou execução em ambiente seguro (como a Sala de Acesso a Dados do CIDACS/Fiocruz).

---

### 2.9 Bases da Saúde Suplementar (ANS)

* **Ato Instituidor e Base Normativa:** Lei Federal nº 9.656/1998 e Lei Federal nº 9.961/2000 (criação da Agência Nacional de Saúde Suplementar).
* **Principais Produtos:**
  - **SIB (Sistema de Informações de Beneficiários):** Número de pessoas cobertas por planos privados de assistência médica por município, faixa etária e tipo de contratação.
  - **TISS (Padrão de Troca de Informações na Saúde Suplementar):** Registros eletrônicos de procedimentos privados faturados.
* **Regime de Acesso:**
  - Beneficiários agregados por município e dados econômico-financeiros (DIOPS) são **públicos** no portal de Dados Abertos da ANS (`dados.gov.br/dados/conjuntos-dados/informacoes-consolidadas-de-beneficiarios`).
* **Papel no Projeto:**
  - Fornece covariáveis pré-tratamento de controle para taxa de cobertura de plano de saúde privado, controlando a demanda potencial que concorre com a rede pública.

---

### 2.10 IVS — Índice de Vulnerabilidade Social (IPEA)

* **Ato e Metodologia:** Desenvolvido pelo Instituto de Pesquisa Econômica Aplicada (IPEA) a partir dos microdados dos Censos Demográficos do IBGE; publicado no *Atlas da Vulnerabilidade Social nos Municípios Brasileiros* (IPEA, 2015).
* **Estrutura:** Índice sintético variando de 0,000 (menor vulnerabilidade) a 1,000 (máxima vulnerabilidade), composto por 16 indicadores distribuídos em três subíndices:
  1. *Infraestrutura Urbana* (saneamento, água encanada, coleta de lixo, tempo de deslocamento);
  2. *Capital Humano* (mortalidade infantil, analfabetismo, crianças fora da escola, mães chefes de família sem fundamental);
  3. *Renda e Trabalho* (renda domiciliar per capita, desocupação, dependência de idosos/crianças, vulnerabilidade à pobreza).
* **Faixas Canônicas de Vulnerabilidade do Ipea:**
  - Muito Baixa: `0,000 a 0,200`
  - Baixa: `0,201 a 0,300`
  - Média: `0,301 a 0,400`
  - Alta: `0,401 a 0,500`
  - Muito Alta: `0,501 a 1,000`
* **Regime de Acesso:**
  - **Público e Aberto.** Disponível na plataforma do IPEA (`ivs.ipea.gov.br`).
* **Papel no Projeto PMM-E:**
  - **Running variable canônica** da regra de incentivo financeiro: as regras de remuneração da bolsa-formação anunciadas nos editais da SGTES/MS escalonam o complemento monetário conforme a classificação de vulnerabilidade do IVS municipal.

---

## 3. Mapeamento Estratégico no Projeto PMM-E: O que entra na V1 vs. O que está no Backlog

O projeto segue rigorosamente o plano de etapas e portões auditáveis documentado em [`docs/06_execucao/05_roadmap_execucao.md`](file:///c:/Users/camil/Desktop/Kauã/Insper/impact-eval-health-econ-pmme/docs/06_execucao/05_roadmap_execucao.md) e [`docs/06_execucao/06_backlog_wp3_wp4_wp5.md`](file:///c:/Users/camil/Desktop/Kauã/Insper/impact-eval-health-econ-pmme/docs/06_execucao/06_backlog_wp3_wp4_wp5.md).

```
                      CADEIA CAUSAL E ALOCAÇÃO DAS BASES
┌─────────────────────────────────────────────────────────────────────────────┐
│ ETAPA 1 (PRIMEIRO ESTÁGIO / OFERTA E FORÇA DE TRABALHO): ATIVA NA VERSÃO 1  │
│                                                                             │
│  [Editais SGTES/MS] ──► [Vagas Imediata vs. Reserva]                        │
│          │                                                                  │
│          ▼                                                                  │
│  [CNES Mensal: 202406 a 202607] ──► Estoque Municipal de Médicos (CBOs)    │
│          │                                                                  │
│          ▼                                                                  │
│  [IVS 2010 IPEA + IBGE] ──► Controles de Equidade e Running Variable        │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼ (Exige primeiro estágio comprovado)
┌─────────────────────────────────────────────────────────────────────────────┐
│ ETAPA 2 (PRODUÇÃO, ACESSO, FILA E SAÚDE): CONGELADAS NO BACKLOG (WP3/4/5)   │
│                                                                             │
│  • SIA/SUS (BPA/APAC) ──► Produção de exames e consultas especializadas    │
│  • SIH/SUS (AIH)       ──► Cirurgias eletivas e internações                │
│  • SISREG / LAI        ──► Dias de espera e atendimento da fila             │
│  • SIM / SINASC        ──► Desfechos clínicos e sobrevida                   │
│  • Microcusteio TFD    ──► Custo de transporte e custo-benefício social    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.1 Bases em Uso Ativo na Versão 1

1. **Quadro Consolidado de Oferta de Vagas (SGTES/MS):**
   - *Origem:* Editais, chamamentos e listas de alocação retificadas oficiais do Ciclo 1 (Edital SGTES/MS nº 2/2025 e Edital nº 3/2025).
   - *Papel:* Identifica se o município ofertou vaga na modalidade **preenchimento imediato** ou apenas **cadastro de reserva** para determinado curso/especialidade.
2. **CNES Mensal Nacional (DATASUS):**
   - *Origem:* Painel mensal contínuo de 26 competências (junho de 2024 a julho de 2026), processado a partir dos arquivos oficiais de microdados do DATASUS.
   - *Papel:* Permite observar o estoque de médicos especialistas no nível municipal antes da política (2024-06 a 2025-06), durante a transição (2025-07) e na vigência da alocação (2025-08 a 2026-07).
   - *Variáveis:* Códigos CBO compatibilizados pelo dicionário de ocupações, carga horária semanal e identificador de estabelecimento.
3. **Ponte Paramétrica de Ocupações (`Curso PMM-E → CBO`):**
   - *Papel:* Conecta os 16 cursos ofertados no PMM-E (ex.: *Cardiologia Clínica*, *Ginecologia e Obstetrícia*, *Cirurgia Geral*, *Ortopedia e Traumatologia*) aos respectivos códigos de ocupação de 6 dígitos da CBO do Ministério do Trabalho presentes no CNES, viabilizando o painel analítico `município–curso–mês`.
4. **IVS 2010 (IPEA) e Malha Territorial (IBGE):**
   - *Papel:* Estratificação socioeconômica, controles exógenos pré-tratamento e verificação da regra de bolsas.

---

### 3.2 Bases Congeladas no Backlog Guardado (WP3, WP4 e WP5) e Justificativas Metodológicas

Conforme estabelecido nas auditorias do projeto, a ampliação empírica prematura para bases assistenciais antes da validação do primeiro estágio introduz sérios riscos de inferência espúria:

1. **SIA/SUS e SIH/SUS (WP3 e WP4 — Produção e Internações):**
   - *Por que estão congeladas?* A disponibilização de uma vaga não garante que um médico entrou em exercício; e a entrada de um médico não garante acréscimo líquido de horas se houver substituição de profissionais pré-existentes. Analisar procedimentos no SIA ou internações no SIH antes de confirmar que a vaga gerou oferta médica líquida adicional confunde flutuações sazonais de faturamento com impacto da política.
   - *Status da Auditoria Técnica:* No piloto do SIH para procedimentos cirúrgicos de Anestesiologia (auditoria C3-02B), a extração oficial de 675 pares UF–competência no FTP do DATASUS revelou a ausência dos arquivos de junho/2026 para o Acre (`RDAC2606.dbc`) e Roraima (`RDRR2606.dbc`). A regra de integridade do repositório proíbe imputar zero ou avançar na análise de desfechos clínicos sem catálogo oficial completo e íntegro.
2. **SISREG e Dados de Fila de Espera (WP3 — Regulação):**
   - *Por que estão congelados?* O tempo de espera é o objetivo legal mais nobre da Lei nº 15.233/2025. Todavia, como o DATASUS não dissemina microdados abertos nacionais de solicitações de regulação, as métricas municipais de fila dependem de pedidos via LAI ou parcerias locais. Além disso, as filas são vulneráveis ao viés de recadastramento cadastral (cancelamentos administrativos confundidos com atendimento real da demanda).
3. **SIM e SINASC (WP4 — Desfechos Clínicos e Vitais):**
   - *Por que estão congelados?* Desfechos de mortalidade têm horizonte temporal biológico estendido e são determinados por uma vasta matriz de determinantes sociais e econômicos. Atribuir reduções de mortalidade municipal a um provimento médico com menos de um ano de seguimento é conceitualmente indefensável.
4. **Microcusteio e Dados Logísticos de Transporte (WP5 — Custo-Benefício):**
   - *Por que estão congelados?* O cálculo de custos logísticos evitados (viagens de ambulância e ônibus municipais no programa TFD — Tratamento Fora de Domicílio) exige saber previamente se houve atendimento local efetivo. Qualquer monetização prévia sem primeiro estágio demonstrado incorre em especulação paramétrica.

---

## 4. Matriz Comparativa Oficial das Bases de Dados de Saúde

A tabela a seguir consolida as especificações operacionais de todas as bases de dados analisadas:

| Sistema / Base | Órgão Gestor | Unidade de Observação | Frequência de Atualização | Canal Oficial de Acesso | Classificação de Acesso | Papel no Projeto PMM-E |
|---|---|---|---|---|---|---|
| **Editais e Alocações PMM-E** | SGTES / MS | Vaga / Inscrição / Médico | Por ciclo e chamada pública | Portal gov.br / DOU | **Público** | **Tratamento e Exposição Causal** |
| **CNES Mensal** | DATASUS / SAES / MS | Vínculo / Estabelecimento (`CO_CNES` + `CBO`) | Mensal (por competência) | FTP DATASUS / Servlets CNES | **Público (Aberto)** | **Outcome Primário: Estoque e Retenção Médica** |
| **IVS 2010** | IPEA | Município (código IBGE) | Decenal (Censo) | Portal IPEA / Atlas IVS | **Público (Aberto)** | **Running Variable e Equidade** |
| **Bases Territoriais** | IBGE | Município | Anual | Portal de Dados IBGE | **Público (Aberto)** | **Harmonização Territorial e População** |
| **SIA/SUS (BPA e APAC)** | DATASUS / SAES / MS | Procedimento ambulatorial faturado | Mensal (por competência) | FTP DATASUS / Tabnet | **Público (Aberto)** | *Backlog WP3/WP4 (Produção diagnóstica)* |
| **SIH/SUS (AIH - Reduzida)** | DATASUS / SAES / MS | Internação hospitalar encerrada | Mensal (por competência) | FTP DATASUS / Tabnet | **Público (Aberto)** | *Backlog WP4 (Cirurgias e internações)* |
| **SISREG / Sistemas Locais** | Municípios / Estados | Solicitação individual de regulação | Contínua / Diária | e-Gestor / LAI municipal | **Restrito (LAI/Convênio)** | *Backlog WP3 (Tempo de espera na fila)* |
| **SIM (Declaração de Óbito)** | DATASUS / SVSA / MS | Óbito individual (DO) | Anual (fechamento oficial) | FTP DATASUS / OpenDataSUS | **Público (Aberto)** | *Fora de escopo V1 (Horizonte biológico)* |
| **SINASC (Nascidos Vivos)** | DATASUS / SVSA / MS | Nascido vivo individual (DN) | Anual (fechamento oficial) | FTP DATASUS / OpenDataSUS | **Público (Aberto)** | *Fora de escopo V1* |
| **SINAN** | DATASUS / SVSA / MS | Notificação compulsória | Semanal epidemiológica | FTP DATASUS / Tabnet | **Público / Restrito (nominal)** | *Fora de escopo V1* |
| **CADSUS / RNDS** | SEIDIGI / MS | Usuário individual (CPF/CNS) | Tempo real / Contínua | Barramento RNDS / Plataforma Brasil | **Sigiloso (LGPD / CEP)** | *Não utilizado (estudo agregado)* |
| **ANS (SIB e DIOPS)** | ANS | Beneficiário / Município | Trimestral / Anual | Portal Dados Abertos ANS | **Público (Aberto)** | *Covariável de controle (cobertura privada)* |

---

## 5. Diretrizes para Utilização em Documentos Formais e Artigos

Ao redigir relatórios executivos, planos de pré-análise e artigos acadêmicos decorrentes deste projeto, devem ser seguidas as seguintes convenções institucionais:

1. **Citação Oficial da Legislação:**
   * "Programa Mais Médicos Especialistas (PMM-E), instituído pela Lei Federal nº 15.233, de 2025, que acresceu os artigos 22-D, 22-E e 22-F à Lei Federal nº 12.871, de 2013, e regulamentado pela Portaria GM/MS nº 7.177, de 2025, no âmbito da formação em serviço."
2. **Definição da Métrica de Oferta no CNES:**
   * O estoque de especialistas deve ser explicitado como **"estoque cadastral municipal de profissionais vinculados às CBOs compatíveis com o curso"**, ressaltando que o CNES capta vínculos administrativos formais e cargas horárias contratadas, e não a comprovação biométrica ou presencial do ato médico.
3. **Tratamento da Relação Causal e Primeiro Estágio:**
   * É estritamente vedado afirmar impacto sobre saúde, filas ou economia de recursos sem a demonstração prévia e conclusiva do primeiro estágio (aumento do FTE médico no CNES líquido de remanejamentos locais).
4. **Governança de Dados e Integridade:**
   * Todas as rotinas computacionais devem operar de maneira idempotente, preservando os arquivos brutos em seus formatos originais, registrando manifestos com hashes criptográficos SHA-256 e documentando lacunas de fornecimento (como inconsistências no FTP do DATASUS) sem imputação ad hoc.
