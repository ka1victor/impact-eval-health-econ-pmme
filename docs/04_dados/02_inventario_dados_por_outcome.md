# 02. Inventário de dados por outcome

> Situação das fontes atualmente preservadas no repositório. “Temos” significa que o campo está presente; não significa que o outcome já esteja identificado.

## 1. Bases atuais

### `data/ivs_ipea_2010_municipios.csv`

- 5.565 municípios;
- IVS 2010 entre 0,066 e 0,752;
- dimensões do IVS, IDHM, população de 2010 e renda domiciliar per capita;
- códigos IBGE e UF.

Uso: running variable canônica, estratificação de equidade, população e covariáveis históricas. Limite: população e contexto são de 2010; não representam capacidade de saúde no início do programa.

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

## 2. Disponibilidade por outcome

| Outcome | O que temos | O que falta | Prontidão |
|---|---|---|:---:|
| Vagas ofertadas | Nada no repositório | Editais em formato tabular, vaga, CNES, especialidade e chamada | 🔴 |
| Preenchimento | Estoque final de ativos | Denominador de vagas e status de cada chamada | 🔴 |
| Entrada efetiva | Data de início dos ativos atuais | Selecionados que não entraram e datas administrativas | 🟡 |
| Retenção individual | Série agregada e fotografia final | Identificador longitudinal, saída e censura | 🔴 |
| FTE líquido | Tipo de prática e participante ativo | CNES mensal com carga horária e baseline prévio | 🔴 |
| Produção especializada | Nenhum microdado preservado | SIA por CNES, procedimento, residência e competência | 🔴 |
| Cirurgias e internações | Nenhum microdado preservado | SIH com residência, prestador, procedimento e `CAR_INT` | 🔴 |
| Acesso local/global | Município do profissional | Fluxo residência-prestador observado | 🔴 |
| Tempo de espera | Nada | Solicitação, prioridade, atendimento/cancelamento e datas | 🔴 |
| Linha oncológica | Nada | APAC, estágio, diagnóstico e início da terapia | 🔴 |
| Transporte | Nada | Rotas, pacientes, ocupação, distância e custo | 🔴 |
| Custos do programa | Faixa, sem folha | Valores pagos, supervisão e administração | 🔴 |
| Equidade por IVS | IVS e localização | Qualquer outcome observado para cruzamento | 🟡 |
| Transbordamentos | Município e região | Fluxos médicos e de pacientes entre municípios | 🔴 |

## 3. Aquisições mínimas

### Bloco A — provimento

1. Universo de vagas ofertadas por chamada.
2. Candidaturas, classificação, aceite e convocação.
3. Entrada, afastamento, transferência e desligamento.
4. Valor efetivamente pago e regras aplicadas a cada vaga.
5. CNES mensal de vínculos e carga horária antes e depois.

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

## 5. Regra de incorporação

Uma nova base só entra no pipeline quando vier acompanhada de:

- fonte e data de extração;
- unidade de observação;
- cobertura temporal e geográfica;
- dicionário de campos;
- validações de contagem;
- distinção entre campo observado e transformação;
- licença ou justificativa de uso.
