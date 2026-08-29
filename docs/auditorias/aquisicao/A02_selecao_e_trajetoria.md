# A02 — Seleção e trajetória administrativa pública do PMM-E

> **Data de auditoria:** 28 de agosto de 2026<br>
> **Objeto:** seleção, alocação e eventos públicos da trajetória no Programa Mais Médicos Especialistas (PMM-E).<br>
> **Fontes:** planilhas oficiais da SGTES/MS preservadas por A01, demais resultados oficiais dos chamamentos, cadastro nominal de ativos e série histórica agregada.<br>
> **Situação:** `AGUARDANDO DADOS ADMINISTRATIVOS` para spells, permanência e cobertura de 90/120/180 dias.

## 1. Conclusão executiva

As fontes públicas permitem descrever resultados publicados de preferência, classificação, alocação e homologação em algumas chamadas. Elas não formam um cadastro completo de inscrições nem um log longitudinal de entrada, aceite, afastamento e saída.

A correção principal desta versão é separar três unidades que antes apareciam misturadas:

1. **registro publicado de preferência/classificação/alocação:** uma linha da planilha; um candidato pode ocupar duas linhas, uma por opção;
2. **candidato distinto dentro da publicação:** chave formada por CPF mascarado e nome normalizado, sujeita às limitações da máscara;
3. **universo completo de inscrições submetidas:** não observado, salvo se uma fonte declarar e demonstrar essa cobertura — o que não ocorre nas planilhas auditadas.

Na primeira chamada de 2025, a versão canônica contém **1.671 registros publicados**, correspondentes a **993 chaves distintas de candidato**. Esses 1.671 registros não são 1.671 candidatos nem provam representar todas as inscrições submetidas.

As três fontes de 2025 recuperadas por A01 estão disponíveis no slug oficial ativo e foram incorporadas por A02. O antigo diagnóstico de que esses arquivos permaneceriam inacessíveis não se aplica mais.

Ainda não são observáveis publicamente:

- aceite ou recusa individual;
- data completa de entrada para ativos e inativos;
- afastamentos e retornos;
- desistência ou desligamento com data e motivo;
- reocupação de uma mesma vaga física;
- trajetória contínua necessária a `cobertura_90`, `cobertura_120` e `cobertura_180`.

## 2. Proveniência e versionamento

O manifesto reproduzível é `output/aquisicao/a02_manifesto_trajetoria.json`. Para as três fontes recuperadas por A01, ele registra o caminho em `data/raw/aquisicao/vagas/`, a URL oficial ativa, o hash local e a conferência desse hash com `output/aquisicao/a01_manifesto_vagas.json`.

### 2.1 Primeira chamada de 2025

| Publicação | Data | Papel analítico | Registros |
|---|:---:|---|---:|
| `2025_ciclo1_chamada1_alocacao_retificada.xlsx` | 10/09/2025 | versão de comparação | 1.671 |
| `2025_ciclo1_chamada1_alocacao_retificada_subjudice.xlsx` | 19/09/2025 | versão canônica para contagens | 1.671 |
| `2025_ciclo1_chamada1_realocacao_retificado.xlsx` | 10/09/2025 | quadro complementar de proposta de realocação | 59 |

A versão sub judice substitui a retificada anterior para fins de contagem. As duas versões do Quadro 1 **não são somadas**. A comparação por chave `CPF mascarado + nome + CNES + curso + opção` encontrou:

- zero registros adicionados;
- zero registros removidos;
- três registros com conteúdo alterado;
- um registro com marcação adicional `SUB JUDICE`.

O Quadro 2 contém 59 propostas de realocação e também não é somado ao Quadro 1 como se fossem novas inscrições.

### 2.2 Inventário das demais publicações

| Fonte | Ciclo/chamada | Conteúdo observável | Contagem publicada auditada |
|---|:---:|---|---:|
| `2025_ciclo1_chamada1_homologados.xlsx` | C1 Ch1 | profissionais homologados | 316 |
| `2025_ciclo1_chamada2_vagas_e_alocados.xlsx` | C1 Ch2 | vagas e alocados imediatos | 98 alocados imediatos; 2.896 vagas de reserva |
| `2025_ciclo1_chamada2_classificacao_final.xlsx` | C1 Ch2 | registros de preferência/classificação e desclassificação | 757 + 88 |
| `2025_ciclo1_chamada2_homologados.xlsx` | C1 Ch2 | lista cumulativa de homologados | 581 |
| `2026_ciclo2_chamada1_resultado_final_remanescentes.xlsx` | C2 Ch1 | resultado residual publicado | 9 registros |
| `2026_ciclo2_chamada2_resultado_final.xlsx` | C2 Ch2 | registros de resultado e desclassificação | 1.053 + 55 |
| `2026_ciclo3_chamada1_resultado_final_sub_judice.xlsx` | C3 Ch1 | registros de resultado e desclassificação | 4.532 + 999 |

Essas contagens descrevem linhas ou categorias publicadas em cada arquivo. Não devem ser reinterpretadas automaticamente como pessoas únicas ou universo de inscrições.

## 3. Recontagem da primeira chamada de 2025

A recontagem é feita diretamente pelo script A02 sobre os três arquivos de A01, e fica registrada em `auditoria_primeira_chamada_2025` dentro da matriz JSON.

| Medida | Resultado | Interpretação permitida |
|---|---:|---|
| Registros publicados no Quadro 1 canônico | 1.671 | linhas de preferência/classificação/alocação |
| Chaves distintas `CPF mascarado + nome` | 993 | aproximação de candidatos distintos dentro da publicação |
| Registros de 1ª opção | 993 | linhas, não novas pessoas |
| Registros de 2ª opção | 678 | linhas adicionais para parte dos candidatos |
| Registros classificados | 527 | linhas com resultado de classificação |
| Locais confirmados para início | 468 | resultado administrativo publicado; não comprova exercício continuado |
| Locais desconsiderados pela gestão/capacidade | 59 | resultado administrativo publicado |
| Propostas do Quadro 2 | 59 | realocação proposta; não inscrição nova |

O fato de os 993 CPF mascarados distintos coincidirem com 993 nomes normalizados distintos reduz, mas não elimina, o risco de colisão ou erro de identificação. Não há identificador oficial pseudonimizado estável.

## 4. Observabilidade dos eventos

| Evento | C1 Ch1 | C1 Ch2 | C2 Ch1 | C2 Ch2 | C3 Ch1 |
|---|---|---|---|---|---|
| Universo completo de inscrições | Não observado | Não observado | Não localizado | Não observado | Não observado |
| Preferências publicadas | Individual no resultado | Individual no resultado | Parcial | Individual no resultado | Individual no resultado |
| Classificação/barema publicados | Individual no resultado | Individual no resultado | Parcial | Individual no resultado | Individual no resultado |
| Convocação individual com timestamp | Não | Não | Não | Não | Não |
| Aceite/recusa | Não localizado | Não localizado | Não localizado | Não localizado | Não localizado |
| Homologação | Individual | Individual | Não localizada | Não localizada | Não localizada |
| Entrada em exercício | Parcial, só sobreviventes | Parcial, só sobreviventes | Parcial, só sobreviventes | Parcial, só sobreviventes | Não localizada |
| Afastamento/retorno | Não localizado | Não localizado | Não localizado | Não localizado | Não localizado |
| Transferência/realocação | Proposta parcial | Não localizada | Não localizada | Não localizada | Não localizada |
| Desistência/desligamento | Não localizado | Não localizado | Não localizado | Não localizado | Não localizado |
| Reocupação da vaga | Não identificável | Não identificável | Não identificável | Não identificável | Não identificável |

“Individual no resultado” significa apenas que a publicação contém identificação individual naquele estágio. Não implica cobertura do universo anterior de inscrições nem existência de acompanhamento posterior.

## 5. Chaves e ligação entre bases

### 5.1 Vaga

Nenhum quadro público atribui identificador único e perene à vaga física. `CNES + curso + chamada` agrupa células de oferta, mas não permite provar que uma vaga reapresentada é a mesma vaga não preenchida, abandonada ou convertida em outra modalidade.

### 5.2 Profissional

Os arquivos usam máscaras incompatíveis de CPF. Além disso:

- o cadastro nominal de ativos contém nome, CRM, UF, CNES, curso e data de início, mas não CPF;
- resultados e homologações contêm nome e CPF mascarado, porém não CRM;
- o CNES mensal usa CNS e nome, sem ponte explícita com a matrícula PMM-E.

Ligação probabilística apenas por nome pode produzir homônimos e erros de grafia. A análise longitudinal requer `id_profissional_pseudo` e `id_vaga_pseudo` estáveis, ou uma ponte administrativa equivalente.

## 6. Spells e cobertura de 90/120/180 dias

Um spell de cobertura exige, no mínimo, início e término do vínculo, períodos de afastamento e identificação estável da vaga. Nas fontes públicas:

1. a data de término não existe;
2. afastamentos e retornos não existem;
3. a data de início aparece apenas para sobreviventes no snapshot de 12/08/2026;
4. não existe `id_vaga` persistente.

Portanto, maturidade de calendário não equivale a mensurabilidade. Mesmo chamadas de 2025 com mais de 180 dias transcorridos não permitem calcular dias efetivamente cobertos.

| Outcome | Situação |
|---|---|
| `cobertura_90` | incalculável com fontes públicas atuais |
| `cobertura_120` | incalculável com fontes públicas atuais |
| `cobertura_180` | incalculável com fontes públicas atuais |
| permanência/sobrevivência | inobservável sem entradas e saídas completas |
| rotatividade | inobservável; estoque agregado não identifica transições |
| reocupação | inobservável sem identificador persistente da vaga |

Usar presença no cadastro nominal de 12/08/2026 como permanência contínua produziria viés de sobrevivência: quem entrou e saiu antes do corte não aparece.

## 7. Bloqueios e encaminhamento

### Bloqueios mantidos

1. `cobertura_90`, `cobertura_120` e `cobertura_180` não podem ser computadas sem histórico administrativo de eventos;
2. faltam chaves estáveis de profissional e vaga;
3. falta o universo completo de inscrições, além de aceite, recusa, afastamento e saída.

### Bloqueio removido

O bloqueio de “links quebrados” para os três quadros da primeira chamada de 2025 foi removido. A01 recuperou os bytes pelos slugs oficiais ativos, e A02 os lê diretamente de `data/raw/aquisicao/vagas/`. A URL histórica com slug antigo pode permanecer quebrada sem tornar o arquivo atual inacessível.

### Dados administrativos necessários

- log de eventos com identificadores pseudonimizados, tipo de evento, timestamp, estado anterior, estado novo e motivo;
- universo de inscrições submetidas e resultados de validação;
- convocações e termos de aceite/recusa;
- datas de início e término para ativos e inativos;
- afastamentos e retornos;
- ponte pseudonimizada entre PMM-E e CNES.

## 8. Decisão A02

A02 está apto como inventário de resultados públicos de seleção e como diagnóstico de observabilidade. Ele **não libera** estimação de permanência ou cobertura sustentada. Esses outcomes continuam bloqueados até a obtenção de dados administrativos longitudinais.
