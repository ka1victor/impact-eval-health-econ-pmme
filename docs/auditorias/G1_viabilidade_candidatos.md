# G1. Viabilidade: identificar todos os candidatos e ligá-los ao CNES pré

> **Data:** 19/10/2026.<br>
> **Plano:** [`06_execucao/51`](../06_execucao/51_plano_perguntas_reformuladas.md),
> §3 (P1, T1.0) e §5 (onda 1, portão G1).<br>
> **Estatuto:** portão de viabilidade. Mede só cobertura e ligação. Nenhum
> contraste por IVS, lado de corte, faixa da bolsa, alocação ou outcome foi
> calculado, e o IVS não foi lido. A alocação aparece só como estrato da taxa
> de **ligação**.<br>
> **Script:** `scripts/rdd_bolsa/G1_identificar_candidatos.py`.<br>
> **Saídas:** `output/rdd_bolsa/G1_resumo.json`,
> `G1_candidatos_origem.parquet`, `G1_distancias_opcoes.parquet` e
> `G1_inventario_identificadores.csv`, todas com
> `natureza_dos_dados = EMPIRICO`.<br>
> **Números:** os blocos `<!-- G1:... -->` são gerados das saídas
> (`--atualizar-doc`) e conferidos por `tests/test_G1.py`.

## 1. Pergunta

O P1 (T1.1, disposição a pagar por distância) e o P6 (T6.2, RD do candidato na
nota de corte) precisam saber de onde vem cada candidato, e não só os
alocados. A pergunta do portão tem duas partes:

1. os arquivos públicos de classificação e resultado identificam todos os
   candidatos?
2. essa identificação liga cada candidato ao seu registro no CNES antes do
   programa, sem ambiguidade e sem depender da alocação?

O universo é o de `escolhas_candidatos.parquet`: os candidatos classificados
com opção na 1ª chamada dos ciclos 1 a 3.

## 2. Que identificadores os arquivos trazem

Os arquivos foram lidos sem alteração. Cada aba com coluna de CPF foi
inventariada. "Candidatos de `escolhas` presentes" conta os candidatos do mesmo
ciclo achados na aba por nome normalizado idêntico e pelos mesmos dígitos
visíveis do CPF nas posições em comum.

<!-- G1:inventario:inicio -->
| Arquivo | Aba | Ciclo | Chamada | Papel | Pessoas (nome + CPF) | Nome | CPF mascarado (molde) | CRM | UF do CRM | Nº de inscrição | Candidatos de `escolhas` presentes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `2025_ciclo1_chamada1_alocacao_retificada.xlsx` | Quadro 1 | 1 | 1 | resultado da alocação (retificado) | 993 | sim | `aaaaaXXXXaa (1671)` | não | não | não | 993 de 993 |
| `2025_ciclo1_chamada1_alocacao_retificada_subjudice.xlsx` | Quadro 1 | 1 | 1 | resultado da alocação (retificado, sub judice); base de escolhas_candidatos | 993 | sim | `aaaaaXXXXaa (1671)` | não | não | não | 993 de 993 |
| `2025_ciclo1_chamada1_realocacao_retificado.xlsx` | Quadro 2 | 1 | 1 | realocação (quadro 2) | 59 | sim | `aaaaaXXXXaa (59)` | não | não | não | 59 de 993 |
| `2025_ciclo1_chamada1_homologados.xlsx` | Quadro 1 | 1 | 1 | homologados | 316 | sim | `aaaXXXaaaaa (316)` | não | não | não | 316 de 993 |
| `2025_ciclo1_chamada2_classificacao_final.xlsx` | ALOCADOS | 1 | 2 | classificação final | 615 | sim | `aaa.aaX.XXX-aa (757)` | não | não | não | 103 de 993 |
| `2025_ciclo1_chamada2_classificacao_final.xlsx` | DESCLASSIFICADO | 1 | 2 | classificação final; aba de desclassificados | 88 | sim | `aaa.aaX.XXX-aa (88)` | não | não | não | 19 de 993 |
| `2025_ciclo1_chamada2_vagas_e_alocados.xlsx` | ALOCADOS - VAGAS IMEDIATAS | 1 | 2 | alocados em vagas imediatas | 92 | sim | `aaaaaXXXXaa (98)` | não | não | não | 92 de 993 |
| `2025_ciclo1_chamada2_homologados.xlsx` | Homologados | 1 | 2 | homologados | 581 | sim | `aaa.XXX.Xaa-aa (581)` | não | não | não | 360 de 993 |
| `resultado-preliminar-pmme.xlsx` | Classificados | 2 | 1 | resultado preliminar | 2.185 | sim | `aaa.aaX.XXX-aa (3442)` | não | não | não | 2.176 de 2.179 |
| `resultado-preliminar-pmme.xlsx` | Desclassificados | 2 | 1 | resultado preliminar; aba de desclassificados | 168 | sim | `aaa.aaX.XXX-aa (167); aaaaaaaaaaa (1)` | não | não | não | 3 de 2.179 |
| `resultado-final-pmme-2o-ciclo-25-05.xlsx` | Classificados | 2 | 1 | resultado final; base de escolhas_candidatos | 2.179 | sim | `aaa.aaX.XXX-aa (3646)` | não | não | não | 2.179 de 2.179 |
| `resultado-final-pmme-2o-ciclo-25-05.xlsx` | Desclassificados | 2 | 1 | resultado final; aba de desclassificados | 175 | sim | `aaa.aaX.XXX-aa (174); aaaaaaXaXXXaaa (1)` | não | não | não | 1 de 2.179 |
| `resultado-final-vagas-remanescentes.xlsx` | Planilha4 | 2 | 1 | vagas remanescentes | 79 | sim | `aaa.aaX.XXX-aa (81)` | não | não | não | 79 de 2.179 |
| `2026_ciclo2_chamada1_resultado_final_remanescentes.xlsx` | Planilha1 | 2 | 1 | remanescentes (05/05) | 9 | sim | `aaa.aaX.XXX-aa (9)` | não | não | não | 9 de 2.179 |
| `2026_ciclo2_chamada2_resultado_final.xlsx` | Classificados | 2 | 2 | resultado final | 609 | sim | `aaa.XXX.aaa-aa (1053)` | não | não | não | 219 de 2.179 |
| `2026_ciclo2_chamada2_resultado_final.xlsx` | Desclassificados | 2 | 2 | resultado final; aba de desclassificados | 55 | sim | `aaa.XXX.aaa-aa (55)` | não | não | não | 6 de 2.179 |
| `2026_ciclo3_chamada1_resultado_final_sub_judice.xlsx` | Classificados | 3 | 1 | resultado final (sub judice); base de escolhas_candidatos | 2.604 | sim | `***.aaa.aaa-** (4532)` | não | não | não | 2.604 de 2.604 |
| `2026_ciclo3_chamada1_resultado_final_sub_judice.xlsx` | Desclassificados | 3 | 1 | resultado final (sub judice); aba de desclassificados | 213 | sim | `***.aaa.aaa-** (213)` | não | não | não | 0 de 2.604 |
<!-- G1:inventario:fim -->

Todos os arquivos trazem nome e CPF mascarado. Nenhum traz CRM, UF do CRM ou
número de inscrição. A coluna UF é a do posto, e a modalidade (AC, ER, PCD) não
identifica a pessoa. A máscara muda de arquivo para arquivo: os ciclos 1 e 2
mostram 7 dígitos (posições 1–5 e 10–11), e o ciclo 3 mostra 6 (posições 4–9).
Por isso o portão não cruza máscaras de arquivos diferentes, porque isso
revelaria mais dígitos do que cada publicação mostra. Os quadros de vagas, a
adesão dos gestores e o comunicado em PDF não têm lista de pessoas.

O CRM só existe nas listas de ativos do PMM-E, usadas pela X1. Por isso a regra
da X1 (CRM e UF; depois CRM com nome compatível) não se aplica aos candidatos.
Ela serve aqui de **validação independente**: é a rota X1, que vai do
candidato alocado ao ativo da mesma célula com nome compatível e daí ao CNES
pelo CRM, com a regra D1.

## 3. Regra de ligação

A regra foi fixada antes de ligar e é análoga à da X1. O `CO_CPF` público do
CNES também é mascarado (seção 3.1). Por isso a chave usa só as posições
visíveis **nas duas** máscaras, a do candidato e a do CNES, e guarda em
SHA-256 os dígitos dessas posições. São 6 dígitos no ciclo 3 e só 2 nos
ciclos 1 e 2. Nesses dois ciclos, quem desambigua é sobretudo o nome.

1. Mesma chave e nome normalizado idêntico, com um único profissional
   (`CO_PROFISSIONAL_SUS`).
2. Sem (1): mesma chave e nome compatível (definição da X1), com um único
   profissional.
3. Ambíguos ficam fora, com o motivo: mais de um profissional, ou um
   profissional ligado a mais de um candidato do mesmo ciclo. Não achados
   também ficam fora, com o motivo.

A sensibilidade usa só o nome normalizado idêntico e único, sem CPF, e é
relatada lado a lado.

**Conjunto de busca do ciclo.** Entram os profissionais com vínculo médico
(CBO 2251, 2252, 2253 ou 2231) em alguma competência do cache da X1 até a
competência de referência do ciclo. A referência é a última competência lida
antes da abertura das inscrições da 1ª chamada:

| Ciclo | Inscrições | Referência |
|---|---|---|
| 1 | 28/07/2025 | 202506 |
| 2 | edital de 03/02/2026 | 202510 |
| 3 | julho de 2026 | 202602 |

Assim, só informação pré-programa define quem é procurado.

### 3.1 Dicionário de nomes e CPF

O cache da X1 não guarda CPF, e guarda o nome só dos CRMs das listas do PMM-E.
Por isso o portão baixou **uma** competência, 202602, pelo mesmo servlet HTTPS
do a09. O SHA-256 foi conferido contra o manifesto do a09. Do arquivo saiu só
a `tbDadosProfissionalSus`, e o ZIP foi apagado. Nada foi gravado em `data/`.
O cache em `output/rdd_bolsa/G1_cache/` é ignorado pelo Git. Ele guarda só o
nome normalizado e a chave do CPF em hash, e só dos médicos com o nome idêntico
ao de algum candidato, ou com o mesmo primeiro nome e a mesma chave.

Dois fatos saíram da extração, antes de qualquer ligação:

- **o `CO_CPF` público é mascarado**, com as posições 4 a 9 visíveis (de 1 a
  11);
- **a tabela é cumulativa**: traz milhões de profissionais sem vínculo na
  própria competência e contém todos os médicos das competências de
  referência.

O segundo fato tornou desnecessário baixar 202506 e 202510 para a identidade.
O critério do veredito "dicionário diferente da referência" virou "cobertura
do dicionário sobre os médicos da referência abaixo de 99%". A revisão está
registrada em `veredito.criterios.revisao_antes_de_ligar`.

<!-- G1:dicionario:inicio -->
- Competência baixada: 202602 (SHA-256 igual ao do a09: sim).
- `tbDadosProfissionalSus`: 7.614.703 linhas; o `CO_CPF` público é mascarado: molde mais comum `XXX.ddd.ddd.XX`, posições visíveis 3-4-5-6-7-8 em 7.614.626 linhas.
- Posições do CPF comuns ao candidato e ao CNES (base da chave): ciclo 1: 3-4 (2 dígitos); ciclo 2: 3-4 (2 dígitos); ciclo 3: 3-4-5-6-7-8 (6 dígitos) (posições contadas a partir de 0).
- Profissionais do dicionário sem vínculo na própria competência: 3.107.072.
- Médicos de cada competência do cache da X1 presentes no dicionário: 202406: 100,0%; 202501: 100,0%; 202506: 100,0%; 202510: 100,0%; 202602: 100,0%; 202608: 96,7%.
<!-- G1:dicionario:fim -->

## 4. Taxas de ligação

"Com município de origem" exige vínculo médico na própria competência de
referência. É a base do veredito.

<!-- G1:taxas:inicio -->
| Regra | Ciclo | Referência | Candidatos | Ligados | Taxa | Com município de origem | Ambíguos | Alocados: taxa | Não alocados: taxa |
|---|---|---|---|---|---|---|---|---|---|
| G1 (CPF + nome), principal | 1 | 202506 | 993 | 938 | 94,5% | 92,4% | 4 (0,4%) | 95,7% | 93,3% |
| G1 (CPF + nome), principal | 2 | 202510 | 2.179 | 2.102 | 96,5% | 95,0% | 6 (0,3%) | 97,1% | 95,9% |
| G1 (CPF + nome), principal | 3 | 202602 | 2.604 | 2.533 | 97,3% | 95,8% | 0 (0,0%) | 97,7% | 97,1% |
| G1 (CPF + nome), principal | total | — | 5.776 | 5.573 | 96,5% | 94,9% | 10 (0,2%) | 97,0% | 96,2% |
| só nome, sensibilidade | 1 | 202506 | 993 | 899 | 90,5% | 88,5% | 5 (0,5%) | 91,2% | 89,9% |
| só nome, sensibilidade | 2 | 202510 | 2.179 | 2.007 | 92,1% | 90,7% | 14 (0,6%) | 92,1% | 92,1% |
| só nome, sensibilidade | 3 | 202602 | 2.604 | 2.399 | 92,1% | 90,9% | 20 (0,8%) | 93,5% | 91,6% |
| só nome, sensibilidade | total | — | 5.776 | 5.305 | 91,8% | 90,4% | 39 (0,7%) | 92,4% | 91,5% |
<!-- G1:taxas:fim -->

Motivos da regra principal, por ciclo:

<!-- G1:motivos:inicio -->
| Motivo | Ciclo 1 | Ciclo 2 | Ciclo 3 |
|---|---|---|---|
| `ambiguo_cpf_nome_compativel_com_mais_de_um_profissional` | 4 | 6 | 0 |
| `cpf_compativel_sem_nome_compativel` | 50 | 71 | 24 |
| `ligado` | 938 | 2.102 | 2.533 |
| `mascara_cpf_invalida` | 1 | 0 | 0 |
| `sem_profissional_com_cpf_compativel_no_conjunto_de_busca` | 0 | 0 | 47 |
| ligado pela etapa `1_cpf_nome_identico` | 904 | 2.021 | 2.417 |
| ligado pela etapa `2_cpf_nome_compativel` | 34 | 81 | 116 |
<!-- G1:motivos:fim -->

**Validação.** São duas verificações independentes da regra:

- **rota X1:** nos candidatos alocados que as duas rotas ligam, o profissional
  é o mesmo?
- **mesma pessoa em dois ciclos:** a pessoa é reconhecida pelo nome idêntico e
  pelos mesmos dígitos nas posições comuns das duas máscaras. O profissional
  ligado é o mesmo nos dois ciclos? Essa verificação cobre os **não alocados**.
  Na comparação com o ciclo 3, a ligação do ciclo 3 usa 6 dígitos do CPF, e por
  isso confere a dos ciclos 1 e 2, que usa só 2.

<!-- G1:validacao:inicio -->
- G1 (CPF + nome), principal: dos 868 candidatos alocados ligados pela rota X1, 856 também ligam pela regra; o profissional é o mesmo em 856 (concordância 100,00%); 12 não ligam pela regra.
- só nome, sensibilidade: dos 868 candidatos alocados ligados pela rota X1, 813 também ligam pela regra; o profissional é o mesmo em 813 (concordância 100,00%); 55 não ligam pela regra.
- Mesma pessoa nos ciclos 1 e 2 (nome idêntico e dígitos comuns do CPF iguais): 153 pares, 146 ligados nos dois pela regra principal, mesmo profissional em 146 (concordância 100,00%; entre os não alocados no ciclo 1: 100,00% de 107).
- Mesma pessoa nos ciclos 1 e 3 (nome idêntico e dígitos comuns do CPF iguais): 108 pares, 103 ligados nos dois pela regra principal, mesmo profissional em 103 (concordância 100,00%; entre os não alocados no ciclo 1: 100,00% de 70).
- Mesma pessoa nos ciclos 2 e 3 (nome idêntico e dígitos comuns do CPF iguais): 328 pares, 315 ligados nos dois pela regra principal, mesmo profissional em 315 (concordância 100,00%; entre os não alocados no ciclo 2: 100,00% de 266).
- Entre as regras: 5.305 ligados nas duas, 268 só na principal, 0 só na sensibilidade; mesma origem em 5.303 dos ligados nas duas.
<!-- G1:validacao:fim -->

## 5. Origem e distância

A origem são os municípios (do gestor do estabelecimento) em que o candidato
tinha vínculo médico na competência de referência. O município principal é o
de mais vínculos. A distância vai do município de cada célula ranqueada ao de
origem principal e ao de origem mais próximo, pelo círculo máximo entre os
centroides do IBGE já no repositório. Aqui só se relata cobertura: nenhuma
distância média por grupo foi calculada.

<!-- G1:distancia:inicio -->
- Linhas candidato × opção: 9.849; com distância: 9.353 (ciclo 1: 1.552 de 1.671; ciclo 2: 3.456 de 3.646; ciclo 3: 4.345 de 4.532).
- Sem distância, por motivo: sem município de origem (não ligado ou sem vínculo na referência): 496.
- Municípios do conjunto de escolha com centroide: ciclo 1: 368 de 368; ciclo 2: 454 de 454; ciclo 3: 748 de 748.
- Municípios de origem com centroide: 650 de 650.
<!-- G1:distancia:fim -->

## 6. Veredito e o que os protocolos podem usar

<!-- G1:veredito:inicio -->
**Veredito: `VIAVEL`.**

- Ciclo 1: `VIAVEL` — a chave do CPF tem só 2 dígito(s) comum(ns) ao CO_CPF do CNES: a ligação se apoia no nome (informativo; a concordância com a rota X1 mede o risco).
- Ciclo 2: `VIAVEL` — a chave do CPF tem só 2 dígito(s) comum(ns) ao CO_CPF do CNES: a ligação se apoia no nome (informativo; a concordância com a rota X1 mede o risco).
- Ciclo 3: `VIAVEL`.

- **P1 (T1.1):** distância origem–célula para todos os candidatos ligados com vínculo na referência, não só alocados; ciclo 1: 92,4% dos candidatos com município de origem em 202506 (VIAVEL); ciclo 2: 95,0% dos candidatos com município de origem em 202510 (VIAVEL); ciclo 3: 95,8% dos candidatos com município de origem em 202602 (VIAVEL). Candidatos sem origem ficam fora com o motivo, e a amostra com distância entra como limite e sensibilidade (doc 51, P1, ameaças).
- **P6 (T6.2):** outcomes CNES individuais dos ciclos 1 e 2 pelo CO_PROFISSIONAL_SUS ligado (painel mensal do G5); a ligação usa só informação pré-programa no conjunto de busca e o dicionário cumulativo cobre todos os médicos da referência. A taxa de ligação por alocação vai para o protocolo 56 como diagnóstico de seleção; não ligados ficam fora com o motivo, com limites para a ligação diferencial. Nos ciclos 1 e 2 a chave do CPF tem 2 dígitos, e o nome faz a maior parte da ligação: a sensibilidade só por nome (mesma origem em quase todos) deve ser repetida no T6.2.
- Download adicional: nenhum; a tbDadosProfissionalSus de 202602 é cumulativa (traz profissionais sem vínculo na competência) e contém todos os médicos das competências de referência; nenhum download adicional é necessário para a identidade. Os locais vêm do cache da X1.
<!-- G1:veredito:fim -->

Os critérios do veredito foram fixados antes de ligar e estão em
`G1_resumo.json` (`veredito.criterios`).

## 7. Limites

- O universo são os classificados com opção na 1ª chamada. Ficam de fora os
  desclassificados, a 2ª chamada e quem não se inscreveu (este último exige
  pedido externo).
- Um único dicionário (202602, cumulativo) identifica as pessoas dos três
  ciclos, com o nome de 202602. Quem mudou de nome depois da referência pode
  não ligar.
- Nos ciclos 1 e 2, a chave do CPF tem só 2 dígitos e a ligação se apoia no
  nome. As validações cobrem os alocados (rota X1) e quem voltou em outro
  ciclo, e não todos os não alocados.
- O conjunto de busca vem das seis competências do cache da X1. Um vínculo
  médico que só existe em meses não lidos não conta.
- Vínculo no CNES não é presença. A origem é o município do estabelecimento, e
  não a residência do candidato.
- O pseudônimo `id_candidato` é fraco: ele se reconstrói a partir dos arquivos
  públicos de resultado. A origem liga duas fontes públicas, e o arquivo não
  deve ser cruzado com dados nominais.
