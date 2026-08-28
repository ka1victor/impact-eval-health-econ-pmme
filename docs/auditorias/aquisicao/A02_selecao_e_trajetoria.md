# Auditoria de Aquisição A02 — Seleção e Trajetória Administrativa Pública

> **Agente:** A02 — Seleção e Trajetória Administrativa Pública  
> **Data da Auditoria:** 28 de agosto de 2026 (revisado pós-saneamento)  
> **Objeto:** Trajetória individual e administrativa no Programa Mais Médicos Especialistas (PMM-E / Lei nº 15.233/2025).  
> **Fontes Primárias:** Planilhas e editais oficiais da Secretaria de Gestão do Trabalho e da Educação na Saúde (SGTES/MS), base nominal de ativos e série histórica de provimento.  
> **Classificação de Disponibilidade:** `AGUARDANDO DADOS ADMINISTRATIVOS` para trajetória longitudinal completa e cálculo de spells.

---

## 1. Sumário Executivo

Esta auditoria analisa a disponibilidade, integridade, granularidade e auditabilidade dos dados públicos relativos a todas as etapas da trajetória administrativa dos médicos e das vagas no Programa Mais Médicos Especialistas (PMM-E), desde a inscrição inicial até o encerramento do exercício.

### Principais Conclusões:
1. **Natureza Transversal/Estática das Fontes Públicas:** As publicações oficiais disponíveis são "fotografias" de etapas intermediárias ou finais (listas de classificados, alocados homologados e cadastro de reserva), inexistindo um **log transacional de eventos** com registro cronológico contínuo (`id_evento`, `id_vaga`, `id_profissional_pseudo`, timestamp, estado anterior, estado novo, motivo).
2. **Inexistência de Chave Administrativa Estável:**
   - **Vaga:** Nenhum quadro público atribui um identificador único e perene à vaga física (`id_vaga`). A tríade analítica `CNES + Curso + Chamada` permite agrupar ofertas, mas é incapaz de rastrear se uma vaga não preenchida ou abandonada no Ciclo 1 foi reapresentada no Ciclo 2 ou convertida em cadastro de reserva.
   - **Profissional:** Há grave fragmentação de identificadores. O Ministério da Saúde aplicou pelo menos **seis padrões incompatíveis de mascaramento de CPF** entre diferentes chamamentos e listas. Ademais, o cadastro nominal de participantes ativos (`data/pmm_especialistas_nominal.csv`) possui `CRM` e `Nome`, mas **não contém CPF**; as listas de classificação/alocação contêm CPF mascarado e Nome, mas **não contêm CRM**; e os registros mensais do CNES baseiam-se em `CNS` e `Nome`.
3. **Inviabilidade de Construção de Spells de Permanência e Cobertura:**
   - Não é possível construir spells (`dt_inicio_spell`, `dt_fim_spell`, `dias_cobertos`) porque datas de desligamento, desistência, licenças e afastamentos são **completamente inobserváveis** em fontes públicas.
   - O cadastro nominal de ativos observa exclusivamente **sobreviventes** até 12/08/2026. Condicionar a análise a essa base geraria viés de sobrevivência severo, pois médicos que entraram e saíram antes dessa data têm suas entradas truncadas e suas saídas ocultadas.
   - Como consequência, o outcome primário do estudo prioritário — **cobertura sustentada em 180 dias (`cobertura_180`)** —, bem como as janelas intermediárias de `cobertura_90` e `cobertura_120`, **não são mensuráveis** exclusivamente com os dados públicos abertos.
4. **Incorporação das Fontes de 2025 Recuperadas por A01:** Os arquivos da 1ª chamada de 2025 (`2025_ciclo1_chamada1_alocacao_retificada.xlsx`, `2025_ciclo1_chamada1_alocacao_retificada_subjudice.xlsx` e `2025_ciclo1_chamada1_realocacao_retificado.xlsx`) foram plenamente incorporados via slug oficial ativo do Ministério da Saúde, permitindo auditar 1.671 inscrições/alocações e 59 propostas de realocação da chamada inaugural.

---

## 2. Inventário e Proveniência das Fontes Preservadas

A auditoria processou 10 fontes documentais ligadas diretamente à seleção e alocação médica, além das duas bases locais de provimento e dos quadros de vagas dos chamamentos.

| ID da Fonte | Arquivo Preservado | Ciclo / Chamada | Unidade Declarada | Registros / Contagem | Status de Disponibilidade |
|---|---|:---:|---|---|:---:|
| `alocacao_2025_c1_retificada` | `2025_ciclo1_chamada1_alocacao_retificada.xlsx` | C1 Ch1 | Candidatura Alocada / Vaga | 1.671 candidaturas (Quadro 1) | Preservado em `data/raw/aquisicao/vagas/` (A01) |
| `alocacao_2025_c1_retificada_subjudice` | `2025_ciclo1_chamada1_alocacao_retificada_subjudice.xlsx` | C1 Ch1 | Candidatura Alocada / Vaga | 1.671 candidaturas (Sub Judice) | Preservado em `data/raw/aquisicao/vagas/` (A01) |
| `realocacao_2025_c1_retificado` | `2025_ciclo1_chamada1_realocacao_retificado.xlsx` | C1 Ch1 | Profissional / Vaga Remanejada | 59 profissionais (Quadro 2) | Preservado em `data/raw/aquisicao/vagas/` (A01) |
| `homologados_2025_c1` | `2025_ciclo1_chamada1_homologados.xlsx` | C1 Ch1 | Profissional Homologado | 316 médicos | Preservado Localmente em `data/raw/pmm_e/` |
| `vagas_alocados_2025_c1_ch2` | `2025_ciclo1_chamada2_vagas_e_alocados.xlsx` | C1 Ch2 | Candidato Alocado / Reserva | 98 cand. imed. / 2.896 vagas res. | Preservado Localmente em `data/raw/pmm_e/` |
| `classificacao_2025_c1_ch2` | `2025_ciclo1_chamada2_classificacao_final.xlsx` | C1 Ch2 | Candidatura / Preferência | 757 linhas (374 aloc.) + 88 descl. | Preservado Localmente em `data/raw/pmm_e/` |
| `homologados_2025_c1_ch2` | `2025_ciclo1_chamada2_homologados.xlsx` | C1 Ch2 | Profissional Homologado | 581 médicos (cumulativo) | Preservado Localmente em `data/raw/pmm_e/` |
| `resultado_2026_c2_ch1_remanescentes` | `2026_ciclo2_chamada1_resultado_final_remanescentes.xlsx` | C2 Ch1 | Candidatura Remanescente | 9 médicos alocados | Preservado Localmente em `data/raw/pmm_e/` |
| `resultado_2026_c2_ch2` | `2026_ciclo2_chamada2_resultado_final.xlsx` | C2 Ch2 | Candidatura / Classificação | 1.053 linhas (303 aloc.) + 55 descl. | Preservado Localmente em `data/raw/pmm_e/` |
| `resultado_2026_c3_sub_judice` | `2026_ciclo3_chamada1_resultado_final_sub_judice.xlsx` | C3 Ch1 | Candidatura / Classificação | 4.532 linhas (704 aloc.) + 999 descl. | Preservado Localmente em `data/raw/pmm_e/` |

Todos os arquivos baixados e íntegros encontram-se espelhados e validados por hash SHA-256 no manifesto `output/aquisicao/a02_manifesto_trajetoria.json`.

---

## 3. Matriz Dimensional de Eventos da Trajetória Administrativa

Para cada uma das 5 coortes operacionais de chamamentos do PMM-E, a tabela abaixo classifica a observabilidade dos **12 eventos fundamentais** da trajetória, empregando as categorias padronizadas:
- `Observado individualmente`: Campo e registro observados em microdado oficial com identificação individual do profissional ou candidatura;
- `Inferível mas inadequado`: Evento não registrado diretamente com timestamp individual, mas deduzível a partir de cronogramas coletivos ou situações cadastrais derivadas (gera viés);
- `Somente agregado`: Dados publicados apenas em totais macro ou notas explicativas, sem identificação de unidades;
- `Não localizado`: Evento inexistente nas publicações e portais oficiais consultados;
- `Link quebrado`: Documento oficial catalogado pelo Ministério cuja URL pública retorna erro HTTP 404.

### Tabela 1: Matriz de Observabilidade por Etapa e Coorte

| Evento da Trajetória | Ciclo 1 Chamada 1 | Ciclo 1 Chamada 2 | Ciclo 2 Chamada 1 | Ciclo 2 Chamada 2 | Ciclo 3 Chamada 1 |
|---|:---:|:---:|:---:|:---:|:---:|
| **1. Inscrição / Candidatura** | `Observado individualmente` (alocação) | `Observado individualmente` | `Não localizado` | `Observado individualmente` | `Observado individualmente` |
| **2. Preferências (1ª e 2ª Opções)** | `Observado individualmente` | `Observado individualmente` | `Observado individualmente` (parcial) | `Observado individualmente` | `Observado individualmente` |
| **3. Classificação e Barema** | `Observado individualmente` | `Observado individualmente` | `Observado individualmente` (parcial) | `Observado individualmente` | `Observado individualmente` |
| **4. Convocação** | `Inferível mas inadequado` | `Inferível mas inadequado` | `Inferível mas inadequado` | `Inferível mas inadequado` | `Inferível mas inadequado` |
| **5. Aceite / Recusa Formal** | `Não localizado` | `Não localizado` | `Não localizado` | `Não localizado` | `Não localizado` |
| **6. Homologação da Seleção** | `Observado individualmente` | `Observado individualmente` | `Não localizado` | `Não localizado` | `Não localizado` |
| **7. Entrada em Exercício** | `Inferível mas inadequado` | `Inferível mas inadequado` | `Inferível mas inadequado` | `Inferível mas inadequado` | `Não localizado` |
| **8. Afastamento / Licença** | `Não localizado` | `Não localizado` | `Não localizado` | `Não localizado` | `Não localizado` |
| **9. Retorno de Afastamento** | `Não localizado` | `Não localizado` | `Não localizado` | `Não localizado` | `Não localizado` |
| **10. Transferência / Realocação** | `Observado parcialmente` | `Não localizado` | `Não localizado` | `Não localizado` | `Não localizado` |
| **11. Desistência / Desligamento** | `Não localizado` | `Não localizado` | `Não localizado` | `Não localizado` | `Não localizado` |
| **12. Reocupação de Vaga** | `Não localizado` | `Inferível mas inadequado` | `Não localizado` | `Não localizado` | `Não localizado` |

---

## 4. Diagnóstico Detalhado por Etapa da Trajetória

### 4.1 Inscrição, Preferências e Classificação
- **Ciclo 1:** Na 1ª chamada, a planilha recuperada por A01 (`2025_ciclo1_chamada1_alocacao_retificada.xlsx`) contém 1.671 inscrições/alocações (1.096 em 1ª opção e 575 em 2ª opção, em 636 células CNES–curso), com pontuação no barema geral e rankings por modalidade de concorrência. Adicionalmente, o Quadro 2 retificado registra proposta de realocação para 59 profissionais de serviços descontinuados. Na 2ª chamada, há 757 registros de preferências (562 escolhas em 1ª opção e 195 em 2ª opção), totalizando 703 nomes distintos classificados e 88 desclassificados.
- **Ciclo 2:** Na 1ª chamada, a relação geral de candidatos não foi disponibilizada em planilha aberta; apenas a lista residual de 9 candidatos remanescentes foi publicada. Na 2ª chamada, constam 1.053 preferências registradas (609 em 1ª opção e 444 em 2ª opção), sendo 303 alocações e 750 registros em cadastro de reserva, além de 55 desclassificados.
- **Ciclo 3:** A 1ª chamada publica 4.532 registros de preferências (2.581 em 1ª opção e 1.951 em 2ª opção) correspondendo a 2.817 médicos distintos, dos quais 704 foram alocados (677 AC, 17 ER, 10 PcD), 2 sub judice e 3.826 alocados em cadastro de reserva, além de 999 desclassificados.
- *Limitação Crítica:* As preferências observadas restringem-se à 1ª e 2ª opções informadas. A função de utilidade/ordenação completa do candidato sobre todas as vagas do país não é publicada. Microdados brutos de todas as inscrições antes do filtro de processamento das opções não são abertos.

### 4.2 Convocação, Aceite e Recusa
- Não existe registro público de **notificação de convocação** com carimbo de data/hora individual. Convocação é meramente presumida pela data de publicação em Diário Oficial ou comunicado.
- Não há registro de **aceite ou recusa**. A não confirmação de uma vaga é um evento "silencioso": o candidato alocado simplesmente não comparece na lista de homologação subsequente ou no cadastro de ativos, sem que se saiba se houve desistência explícita, recusa da localidade, impedimento documental ou perda de prazo.

### 4.3 Homologação vs. Entrada em Exercício
- A publicação formal de listas de médicos homologados ocorreu de forma estruturada em planilhas apenas para o **Ciclo 1 de 2025** (316 médicos na 1ª chamada e 581 cumulativos na 2ª chamada). Nos Ciclos 2 e 3, as planilhas publicam apenas "Resultados Finais".
- A **data de entrada em exercício** (`dt_inicio_atividade`) está disponível apenas no snapshot `data/pmm_especialistas_nominal.csv` para quem estava ativo em 12/08/2026. Médicos que ingressaram e se desligaram antes desse corte têm sua entrada inteiramente omitida da base de dados.

### 4.4 Afastamentos, Retornos, Transferências e Desligamentos
- **Afastamentos e Retornos:** Inexistência absoluta de dados públicos. Licenças por saúde, maternidade, capacitação ou suspensões de bolsa não são registradas.
- **Transferências:** Menções apenas qualitativas em comunicados ou portarias genéricas. Não há base contendo `cnes_origem`, `cnes_destino`, `dt_transferencia` e `motivo`.
- **Desligamentos e Rotatividade:** Inexistência de data de saída e tipo de rescisão. A redução observada de 31 médicos entre julho/2026 (1.511 ativos) e agosto/2026 (1.480 ativos) na série histórica agregada não pode ser desmembrada em desligamentos individuais sem microdados.

---

## 5. Auditoria de Identificadores e Proteção de Dados Pessoais (LGPD)

### 5.1 Heterogeneidade nas Máscaras de CPF
A auditoria identificou que o Ministério da Saúde utilizou pelo menos **seis formatos distintos e mutuamente incompatíveis de mascaramento de CPF** nos arquivos públicos:

| Arquivo de Origem | Coluna | Formato da Máscara | Exemplo Observado | Dígitos Expostos |
|---|---|---|---|:---:|
| `2025_ciclo1_chamada1_homologados.xlsx` | `CPF` | `DDDXXXDDDDD` | `711XXX14162` | 1-3 e 7-11 |
| `2025_ciclo1_chamada2_classificacao_final.xlsx` | `CPF` | `DDD.DDX.XXX-DD` | `669.07X.XXX-00` | 1-5 e 10-11 |
| `2025_ciclo1_chamada2_homologados.xlsx` | `CPF ` | `DDD.XXX.XDD-DD` | `711.XXX.X41-62` | 1-3 e 8-11 |
| `2025_ciclo1_chamada2_vagas_e_alocados.xlsx` | `CPF` | `DDDDXXXXXDD` | `06191XXXX08` | 1-5 e 10-11 |
| `2026_ciclo2_chamada2_resultado_final.xlsx` | `CPF_MASC` | `DDD.XXX.DDD-DD` | `587.XXX.842-53` | 1-3 e 7-11 |
| `2026_ciclo3_chamada1_resultado_final_sub_judice.xlsx` | `CPF_MASC` | `***.DDD.DDD-**` | `***.045.024-**` | 4-9 |

**Implicação Crítica:** O Ciclo 3 mascara os primeiros 3 e os últimos 2 dígitos (`***.045.024-**`), enquanto os ciclos anteriores mascaram os dígitos intermediários. Logo, **não é possível realizar cruzamento determinístico direto de CPFs mascarados entre chamadas e ciclos**.

### 5.2 Descasamento de Chaves entre Bases
A cadeia de identificação sofre de graves lacunas de integração:
1. **Cadastro Nominal de Ativos (`data/pmm_especialistas_nominal.csv`):** Contém `Nome`, `CRM`, `UF`, `CNES`, `Curso`, `dt_inicio_atividade`, mas **não possui CPF**.
2. **Resultados de Chamamentos e Homologação:** Contêm `Nome`, `CPF mascarado`, `CNES`, `Curso`, mas **não possuem CRM**.
3. **CNES Mensal Nacional:** Identifica o profissional por `CNS` e `Nome`, mas não possui vínculo explícito direto com a matrícula SGP do PMM-E.

Adotar vinculação probabilística por Nome Normalizado introduziria erros de atrito devido a homônimos, casamentos/mudanças de sobrenome e variações de grafia. A identificação segura exige que o Ministério forneça chaves pseudonimizadas padronizadas (`id_profissional_pseudo` e `id_vaga_pseudo`).

---

## 6. Viabilidade de Spells e Cobertura Temporal (90, 120 e 180 dias)

O desenho prioritário de avaliação de impacto depende da mensuração da **cobertura sustentada da vaga** por um horizonte de tempo padronizado.

### 6.1 Condições para Construção de Spells de Permanência
A construção de um spell formal de cobertura da vaga $v$ pelo profissional $i$ exige:
$$Spell_{v,i} = [\text{Data Entrada}_{v,i}, \text{Data Término}_{v,i}]$$
$$\text{Dias Efetivamente Cobertos}_v = \sum_{i} \left( \min(\text{Data Término}_{v,i}, t_0 + W) - \max(\text{Data Entrada}_{v,i}, t_0) \right) - \text{Dias Afastamento}$$

Nas fontes públicas:
1. $\text{Data Término}$ não existe;
2. $\text{Dias Afastamento}$ não existem;
3. $\text{Data Entrada}$ existe apenas para os sobreviventes ativos em 12/08/2026;
4. $v$ (identificador único da vaga física) não existe.

### 6.2 Maturidade de Calendário vs. Mensurabilidade Empírica

| Coorte de Oferta | Data de Início do Chamamento | Dias de Calendário até 12/08/2026 | Janela de 90 Dias Madura? | Janela de 120 Dias Madura? | Janela de 180 Dias Madura? | Cobertura Mensurável Hoje? |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Ciclo 1, Chamada 1** | 24/07/2025 | 384 dias | Sim | Sim | Sim | **Não** |
| **Ciclo 1, Chamada 2** | 29/09/2025 | 317 dias | Sim | Sim | Sim | **Não** |
| **Ciclo 2, Chamada 1** | 19/03/2026 | 146 dias | Sim | Sim | Não | **Não** |
| **Ciclo 2, Chamada 2** | 16/04/2026 | 118 dias | Sim | Não | Não | **Não** |
| **Ciclo 3, Chamada 1** | 24/07/2026 | 19 dias | Não | Não | Não | **Não** |

**Conclusão sobre Janelas:**
- Mesmo para as chamadas de 2025 (com mais de 300 dias transcorridos), **a cobertura sustentada em 180 dias (`cobertura_180`) é incalculável** com os dados públicos porque não se observam os períodos exatos de vacância ou as datas de eventuais abandonos intermediários.
- Tratar a presença no snapshot nominal de 12/08/2026 como indicativo de cobertura contínua desde a entrada introduziria um **viés de seleção extremo**.

---

## 7. Decomposição de Componentes da Cadeia de Provimento

| Componente | Mensurável com Fontes Públicas? | Justificativa e Diagnóstico |
|---|:---:|---|
| **Preenchimento Inicial** | **Parcialmente** | Observável nas listas de alocação/homologação publicadas, mas sem taxa exata onde o denominador de vagas imediatas é ambíguo. |
| **Tempo até Entrada** | **Não** | Observável apenas para os sobreviventes em relação à data coletiva do edital; data de notificação individual e data de aceite são ausentes. |
| **Permanência e Sobrevivência** | **Não** | Inobservável. Condicionar a análise ao snapshot de ativos em 12/08/2026 elimina quem saiu antes dessa data. |
| **Rotatividade (Turnover)** | **Não** | A série histórica agregada observa estoque líquido mensal, não transições de entrada, saída e substituição. |
| **Reocupação de Vaga** | **Não** | Sem `id_vaga` administrativo, não é possível saber se uma nova alocação substitui um profissional desistente ou ocupa uma vaga remanescente. |

---

## 8. Recomendações e Bloqueios para as Frentes A06 e A07

### Bloqueios Confirmados pelo Agente A02:
1. **Bloqueio B1 (Outcome Primário Inobservável):** `cobertura_180`, `cobertura_120` e `cobertura_90` não podem ser computadas sem dados administrativos de eventos de entrada e saída com timestamps.
2. **Bloqueio B2 (Inexistência de Chaves Estáveis):** A ausência de `id_vaga_pseudo` e `id_profissional_pseudo` unificado impede o encadeamento dos chamamentos e a ligação determinística com o CNES.
3. **Bloqueio B3 (Links Quebrados):** As bases originais de vagas e alocação do Ciclo 1 Chamada 1 permanecem inacessíveis via portal web.

### Encaminhamentos:
- **Para o Agente A06 (Integração e Portão):** Registrar que a trilha de seleção e trajetória administrativa pública sustenta análises descritivas das preferências e classificações observadas, mas **bloqueia o avanço para estimação causal do efeito sobre cobertura e permanência** antes do recebimento dos dados administrativos.
- **Para o Agente A07 (Pedidos Administrativos / LAI):** Solicitar formalmente à SGTES/MS:
  1. Microdados transacionais de eventos (`id_evento`, `id_vaga_pseudo`, `id_profissional_pseudo`, tipo de evento, timestamp, situação anterior, situação nova, motivo);
  2. Histórico de inscrições completas, convocações, termos de aceite/recusa e datas exatas de início e término de exercício de todos os participantes (ativos e inativos);
  3. Crosswalk pseudonimizado entre a matrícula SGP do médico no PMM-E e o seu número de CNS/CPF para integração segura com o CNES mensal.
