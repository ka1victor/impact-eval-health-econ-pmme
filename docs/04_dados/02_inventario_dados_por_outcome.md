# 02. Inventário de dados por outcome

> Situação das fontes atualmente preservadas no repositório. “Temos” significa que o campo está presente; não significa que o outcome já esteja identificado.

> **Atualização de 19/10/2026.** A rodada multi-outcome da RDD da bolsa
> (protocolo [`06_execucao/40`](../06_execucao/40_protocolo_multioutcome_rdd_bolsa.md))
> trouxe ao repositório os quadros de vagas e os resultados das chamadas dos
> ciclos 1 a 3, a relação nominal de ativos, o PMMB consolidado, o IVS 2010
> oficial do Ipea e o CNES nacional mensal. As novas bases estão na seção 1.1;
> a tabela da seção 2 foi revista. Contagens de linhas, municípios e
> competências não são repetidas aqui: estão nos manifestos e dicionários
> citados, gerados pelos scripts de aquisição e construção.

## 1. Bases atuais

### `data/ivs_ipea_2010_municipios.csv` — não é o IVS do município

- 5.565 municípios;
- IVS 2010 entre 0,066 e 0,752;
- dimensões do IVS, IDHM, população de 2010 e renda domiciliar per capita;
- códigos IBGE e UF.

> **Corrigido em 14/10/2026.** O arquivo é, em cada município, a última linha
> de subgrupo com IVS preenchido da base do Ipea, e não a linha do município
> ([`auditorias/16`](../auditorias/16_ivs_2010_oficial_e_arquivo_local.md)).
> **Não é running variable nem covariável municipal.** Só serve para
> documentar o failure mode
> ([`auditorias/19`](../auditorias/19_reestimacao_base_oficial_failure_mode.md)).
> A running variable canônica é o IVS 2010 oficial (seção 1.1).

~~Uso: running variable canônica, estratificação de equidade, população e covariáveis históricas.~~ Limite: população e contexto são de 2010; não representam capacidade de saúde no início do programa.

### `data/pmm_especialistas_nominal.csv`

- 1.480 registros ativos na referência de 12/08/2026;
- 1.478 combinações únicas UF-CRM;
- 325 municípios, 518 CNES e 16 cursos;
- município, estabelecimento, tipo de prática, faixa de atração, curso, início de atividade, ciclo e identificação profissional.

Uso: fotografia dos participantes ativos e composição do provimento. Limites: contém apenas ativos, não o universo de vagas, candidatos, desistentes ou desligados; por isso não mede preenchimento nem retenção.

### `data/pmm_especialistas_serie_historica.csv`

- 7.276 registros agregados;
- nove competências entre dezembro de 2025 e agosto de 2026;
- 531 municípios e 40 rótulos de curso;
- quantidades ativas e composição por sexo.

Uso: evolução agregada município-curso. Limites: `co_cnes` está vazio em todas as linhas; não há identificador individual; os 40 rótulos precisam ser harmonizados com os 16 cursos do cadastro nominal; meses recentes têm censura para retenção de 6/12 meses.

### `output/aquisicao/populacao_censo2022_municipios.csv` (derivada)

- 5.570 municípios; população residente total de 203.080.756;
- fonte: IBGE, Censo Demográfico 2022, SIDRA tabela 4709, variável 93;
- adquirida por `scripts/aquisicao/06_adquirir_populacao_censo2022.py`, com
  bruto em `data/raw/aquisicao/populacao/` e manifesto com hash em
  `output/aquisicao/manifesto_populacao_censo2022.json`.

Uso: **único denominador populacional válido do repositório**. Motivo na seção
4.1. Limite: população de 2022, fixa no tempo; adequada para taxas em 2024–2026,
não para tendências demográficas.

### 1.1 Bases trazidas pela RDD da bolsa (14 a 19/10/2026)

| Base | Onde | Proveniência | Uso | Limite |
|---|---|---|---|---|
| IVS 2010 oficial do Ipea, por município, com subíndices, IDHM e população de 2010 | `output/aquisicao/a08_ivs_2010_oficial_municipio.csv` | Plataforma IVS do Ipea; `scripts/aquisicao/a08_*`; manifesto `a08_manifesto_ivs_2010_oficial.json` | **running variable canônica** da bolsa e covariáveis pré | contexto de 2010 |
| Quadros de vagas da 1ª chamada (células CNES × curso) dos ciclos 1, 2 e 3, com a faixa da bolsa impressa | `data/raw/aquisicao/vagas/`, `data/raw/pmm_e/` | páginas dos chamamentos; versões em `output/aquisicao/a01_inventario_versoes.json` | oferta de vagas (F0), denominador por célula | sem identificador persistente de vaga |
| Resultados das chamadas: candidaturas com 1ª e 2ª opção, nota, alocação | `data/raw/aquisicao/vagas/`, `data/raw/pmm_e/`; 1ª chamada do ciclo 2 pela aquisição a11 (`output/aquisicao/a11_manifesto_ciclo2_chamada1.json`) | publicações oficiais do PMM-E | candidaturas, preenchimento e escolha (F1, F4, E9) | registros publicados, não o universo de inscrições; sem residência do candidato |
| Adesão e cardápio de gestores do ciclo 3 | `data/raw/aquisicao/vagas/`, `data/raw/pmm_e/` | publicações oficiais | demanda municipal (F0.3) | só o ciclo 3 |
| Relação nominal de especialistas ativos do PMM-E | `data/raw/aquisicao/ivs_administrativo/tb_profissionais_ativos_pmme_csv.zip` | MS | presença no retrato (F2) | retrato em uma data, não retenção |
| PMMB consolidado por município | `data/raw/aquisicao/ivs_administrativo/ppf_mais_medicos_csv.zip` | MS; dicionário arquivado no mesmo diretório | co-política nos mesmos cortes (F0.4, S1, S4) | estoque acumulado em uma data |
| Normas com cortes de IVS e estrato da APS | `output/aquisicao/a10_*` | portarias arquivadas; [`auditorias/18`](../auditorias/18_politicas_nos_mesmos_cortes_ivs.md) | co-políticas (S3) | — |
| Outcomes do funil por município, célula e candidato (U, G3, V1–V3) | `output/rdd_bolsa/outcomes/` | `scripts/rdd_bolsa/12_construir_outcomes_funil.py`; contagens em `dicionario_outcomes_funil.json` | F0, F1, F2, F4 e E9 | construídos às cegas ([`06_execucao/41a`](../06_execucao/41a_construcao_outcomes_funil.md)) |
| CNES nacional: painel município × grupo de CBO × mês, desde 2022 | `output/aquisicao/cnes_nacional/painel_municipio_cbo_mes.parquet` | CNES/DATASUS; `scripts/aquisicao/a09_*`; manifesto `a09_manifesto_cnes_nacional.json`; [`auditorias/aquisicao/A09`](../auditorias/aquisicao/A09_cnes_nacional.md) | oferta líquida local por DiRD (F3) | vínculo cadastrado não é médico do PMM-E nem retenção; competências do ciclo 3 pós-T0 não lidas |
| SIH/SUS: AIH aprovadas, internações e valor por município de internação × mês de processamento × grupo do procedimento, 202201–202607; grupo 04 também por caráter (eletivo, urgência e causas externas) | `output/aquisicao/sih/painel_sih_municipio_mes_grupo.parquet`, `painel_sih_municipio_mes_carater_g04.parquet` | TabNet/DATASUS (`sih/cnv/qibr.def`); `scripts/aquisicao/a13_*`; manifesto `output/aquisicao/sih/manifesto_sih.json`; [`auditorias/aquisicao/A13`](../auditorias/aquisicao/A13_sih_tabnet.md) | cirurgias SUS hospitalares (K2 do protocolo 47) | sem CBO do executante; local de internação, não residência; mês de processamento, não de internação; UF-mês sem dado na fonte fica ausente |

## 2. Disponibilidade por outcome

| Outcome | O que temos | O que falta | Prontidão |
|---|---|---|:---:|
| Vagas ofertadas | Quadros da 1ª chamada dos ciclos 1–3 por célula CNES × curso, com faixa da bolsa; cardápio de gestores do ciclo 3 (seção 1.1) | Identificador persistente de vaga; versões internas | 🟢 por célula |
| Candidaturas e escolha | 1ª e 2ª opção e nota dos candidatos publicados nos ciclos 1–3 (E9) | Universo de inscrições, conjunto de escolha efetivo e residência do candidato ([`pedidos_dados/eventos_e_ponte_cnes.md`](../pedidos_dados/eventos_e_ponte_cnes.md), não enviado) | 🟡 |
| Preenchimento | Alocação e confirmação por célula nas chamadas dos ciclos 1–3; preenchimento do ciclo 2 estimado no E6 | Denominador por vaga; status individual de cada chamada | 🟢 por célula |
| Entrada efetiva | Data de início dos ativos atuais | Selecionados que não entraram e datas administrativas | 🟡 |
| Retenção individual | Série agregada e fotografia final | Identificador longitudinal, saída e censura | 🔴 |
| FTE líquido | Tipo de prática e participante ativo; CNES nacional mensal com horas SUS por município e grupo de CBO, desde 2022 (E7) | Ponte PMM-E–CNES por profissional | 🟡 agregado |
| Produção especializada | Nenhum microdado preservado | SIA por CNES, procedimento, residência e competência | 🔴 |
| Cirurgias e internações | SIH agregado do TabNet (a13): AIH por município de internação × mês de processamento × grupo, e grupo 04 por caráter, 202201–202607 | Microdado da AIH com residência, prestador, procedimento e `CAR_INT`; CBO do executante | 🟡 agregado |
| Acesso local/global | Município do profissional | Fluxo residência-prestador observado | 🔴 |
| Tempo de espera | Nada | Solicitação, prioridade, atendimento/cancelamento e datas | 🔴 |
| Linha oncológica | Nada | APAC, estágio, diagnóstico e início da terapia | 🔴 |
| Transporte | Nada | Rotas, pacientes, ocupação, distância e custo | 🔴 |
| Custos do programa | Faixa, sem folha | Valores pagos, supervisão e administração | 🔴 |
| Equidade por IVS | IVS 2010 oficial (a08) e os outcomes acima | Outcomes de acesso e saúde | 🟡 |
| Transbordamentos | Município e região | Fluxos médicos e de pacientes entre municípios | 🔴 |

## 3. Aquisições mínimas

### Bloco A — provimento

1. Universo de vagas ofertadas por chamada. *(Obtido por célula, de fonte
   pública, para a 1ª chamada dos ciclos 1–3; falta o identificador de vaga.)*
2. Candidaturas, classificação, aceite e convocação. *(Registros publicados
   obtidos; falta o universo de inscrições.)*
3. Entrada, afastamento, transferência e desligamento.
4. Valor efetivamente pago e regras aplicadas a cada vaga.
5. CNES mensal de vínculos e carga horária antes e depois. *(Obtido: painel
   nacional a09.)*

### Bloco B — acesso e produção

1. SIA mensal por residência, prestador, procedimento e quantidade.
2. SIH mensal com caráter, procedimento, residência e prestador.
3. Mapa de códigos comparável no tempo, incluindo migração para OCI.
4. População contemporânea e capacidade instalada do CNES.

### Bloco C — fila

1. Solicitação ou encaminhamento com data e prioridade.
2. Agendamento, atendimento, cancelamento e motivo.
3. Procedimento/especialidade e município de residência.
4. Regra de limpeza de duplicidades e reclassificações.

### Bloco D — clínica

1. APAC oncológica e estágio.
2. Ligação diagnóstico-terapia.
3. SIH para urgência/eletiva, complicações e reinternações.
4. Desfechos específicos por linha de cuidado.

### Bloco E — economia

1. Folha e custo administrativo do programa.
2. Microcusteio amostral do transporte sanitário.
3. Matriz de distância/tempo e ocupação efetiva dos veículos.
4. Valoração do tempo e parâmetros clínicos apenas após estimar efeitos.

## 4. Problemas de qualidade a resolver antes de modelar

- harmonizar nomes e códigos de curso entre nominal e série;
- investigar as duas ocorrências excedentes à unicidade de UF-CRM;
- documentar por que a série cobre 531 municípios e o nominal apenas 325;
- obter CNES para a série histórica;
- converter competências para calendário padronizado;
- distinguir ausência verdadeira de zero e campo faltante;
- criar dicionário e hash de cada arquivo de origem;
- não armazenar no diretório `data/` nenhuma coluna construída por hipótese comportamental.

### 4.0 `populacao_2010` não é população residente

> **Confirmado em 14/10/2026.** O arquivo é, em cada município, a última linha
> de subgrupo com IVS preenchido da base oficial do Ipea (mulheres negras
> urbanas em 4.362 municípios; outros recortes de mulheres no resto). Essa regra
> reproduz as 7 colunas em 5.565 de 5.565 municípios. A coluna de população é a
> desses subgrupos. Ver
> [`auditorias/16`](../auditorias/16_ivs_2010_oficial_e_arquivo_local.md), §3.

Registro aberto em 09/09/2026. A coluna `populacao_2010` de
`data/ivs_ipea_2010_municipios.csv` soma **41.852.890** habitantes contra
**190.755.799** do Censo 2010. A razão para o valor censitário varia de 0,10
(Curitiba, Porto Alegre) a 0,42 (Salvador) e correlaciona com vulnerabilidade;
a mediana municipal é 1.895, quando a real em 2010 era cerca de 10.900. É alguma
subpopulação do Atlas do Ipea, não o total residente.

Consequências:

- qualquer taxa por habitante com esse denominador sai inflada em cerca de 4,5
  vezes e distorcida de forma não uniforme entre municípios;
- `estoque_pre_por_10k` em `output/tema_trabalho/matriz_tipologia_territorial.parquet`
  e `estoque_por_10k` em `A5_painel_T0.parquet` herdam o problema;
- `log_pop`, usado como covariável nos módulos A4 e A5, é logaritmo de uma
  variável mal rotulada — o ajuste continua válido como controle de escala,
  mas não pode ser lido como população;
- `output/avaliacao_impacto/tabelas/tabela1_estatisticas_descritivas_baseline`
  rotula a variável como "População municipal 2010". O rótulo está incorreto.

Decisão: o denominador populacional passa a ser o Censo 2022 (seção 1). As
saídas históricas não são reescritas à mão; a correção do rótulo e de
`estoque_pre_por_10k` entra na próxima execução dos scripts correspondentes.

### 4.1 Números publicados que não reproduzem nas bases

Registro aberto em 09/09/2026, na conferência do material da banca 1.

| Número publicado | Onde apareceu | Situação |
|---|---|---|
| Participação regional dos ativos do PMM-E: Norte 18,0%, Centro-Oeste 6,8%, Sudeste 10,6%, Sul 4,3% | figura de motivação do deck `PEE__Modelo_econômico.pptx` | **não reproduz**. Apenas o Nordeste (60,3%) coincide com o ciclo 1 de `pmm_especialistas_nominal.csv`. A mesma base dá Sudeste 23,0%, Norte 12,1%, Centro-Oeste 3,6% e Sul 1,0%. Recortes alternativos testados (ciclos 1+2, série histórica de dez/2025, contagem de municípios distintos) também não reproduzem o conjunto |

Consequência de regra: **figura derivada de base do repositório é gerada por
script versionado e lida de `output/`**. Gráfico produzido fora do pipeline não
entra em apresentação, artigo ou relatório. O detalhamento está em
[`docs/07_apresentacoes/banca1/03_proveniencia_figuras_e_numeros.md`](../07_apresentacoes/banca1/03_proveniencia_figuras_e_numeros.md).

## 5. Regra de incorporação

Uma nova base só entra no pipeline quando vier acompanhada de:

- fonte e data de extração;
- unidade de observação;
- cobertura temporal e geográfica;
- dicionário de campos;
- validações de contagem;
- distinção entre campo observado e transformação;
- licença ou justificativa de uso.
