# Protocolo exploratório pós-síntese (X1–X6)

> **Data de congelamento:** 19/10/2026, depois da síntese E8 (doc 44) e antes
> de abrir qualquer um dos outcomes abaixo.<br>
> **Pedido do autor (19/10/2026):** antes de escolher a hipótese, garantir que
> tudo o que os dados permitem foi explorado.<br>
> **Estatuto:** **exploratório e pós-resultado.** Nada aqui é teste
> confirmatório. Nenhuma análise abaixo muda o protocolo 40, os resultados
> E3–E9 nem o Holm das primárias. Toda saída leva `estatuto = EXPLORATORIO_POS_SINTESE`.

## 1. Por que este protocolo existe

A síntese (doc 44, §7) propõe três leituras: A (realocação entre vagas sem
expansão líquida), B (elasticidade da escolha à remuneração, relativa a fatores
não pecuniários) e C (quanto e em que margem). Uma revisão das lacunas
encontrou análises que os dados do repositório e dados públicos permitem e que
ainda não foram feitas. Cada uma discrimina entre A, B e C:

| Id | Pergunta | Proposta que testa | Por que não foi feito antes |
|---|---|---|---|
| X1 | O especialista do PMM-E já estava no município ou no estabelecimento antes de entrar? De onde veio? | A (substituição e remanejamento contra entrada líquida), B (distância) | supunha-se que a ponte PMM-E–CNES exigia pedido externo (pedido 2); o CNES público traz o registro profissional e a lista nominal do PMM-E traz o CRM |
| X2 | Quem foi alocado continua ativo? A saída é maior do lado de bolsa menor? | H2 (fixação), C | o protocolo 40 mediu presença, não permanência condicional à alocação |
| X3 | Como evolui o número de ativos por município e curso, mês a mês? | H2, C | série histórica pública não usada como outcome |
| X4 | A resposta da escolha à bolsa varia com a nota do candidato, o curso e a escassez local? | A, B | heterogeneidade não estava no protocolo 40 |
| X5 | Uma célula de bolsa maior tira candidatos de células vizinhas de bolsa menor na mesma região de saúde? | A (deslocamento) | proposto no doc 44, §7.3, não executado |
| X6 | Qual o efeito mínimo detectável de cada outcome, e o que cada IC descarta em termos relativos? | C, leitura dos nulos | a síntese relata ICs, mas não uma tabela de poder comparável |

## 2. Regras

- As regras de integridade valem integralmente:
  - nada simulado, imputado ou digitado vira observação;
  - o que falta fica faltante, com o motivo;
  - números de docs saem de `output/` e são conferidos por teste;
  - o arquivo de IVS errado não é lido.
- Ligações entre pessoas usam só identificadores publicados (CRM, UF do CRM,
  nome, estabelecimento). Saídas em `output/` não trazem nome nem CPF: usam
  pseudônimo determinístico. A taxa de ligação e os casos ambíguos são
  relatados, e o que não liga sem ambiguidade fica fora.
- Nenhum mês CNES ≥ 202609 é lido (plano do ciclo 3).
- **Downloads públicos são permitidos** (CNES do DATASUS, coordenadas
  municipais do IBGE), com URL, data e SHA-256. Pedidos externos de dados
  continuam fora.
- Toda especificação abaixo é relatada, qualquer que seja o resultado. Cada
  linha leva rótulo exploratório, e nada é reescolhido depois de ver resultados.
- Inferência: RDD como no protocolo 40 (local linear, h = 0,050, HC1/CR1,
  cortes empilhados) e logit condicional como no E9 (§15). Outcome condicional
  à alocação recebe limites de Lee. Os p-valores são exploratórios e levam q de
  BKY dentro de cada X.

## 3. Especificações

### X1 — Origem e substituição (ponte PMM-E–CNES pelo registro profissional)

- **Ligação:**
  - lista nominal de ativos do PMM-E (CRM, UF, CNES do estabelecimento, data de
    início, ciclo) contra os vínculos do CNES (registro do conselho e UF, CNS
    do profissional, CNES, município, CBO);
  - competências públicas 202406, 202501, 202506, 202510, 202602 e 202608,
    baixadas e extraídas com o registro profissional;
  - regra de ligação, em ordem: CRM+UF exato; depois CRM exato com nome
    compatível; ambíguos fora.
- **Outcomes por médico** (ciclos 1 e 2):
  - (a) já tinha vínculo no **mesmo estabelecimento** antes do início;
  - (b) já tinha vínculo no **mesmo município**;
  - (c) local de origem: mesmo município / mesma região de saúde / mesma UF /
    outra UF / sem vínculo médico anterior no CNES (última competência pré-início);
  - (d) distância em km entre o município de origem e o do PMM-E, se as
    coordenadas oficiais do IBGE forem obtidas;
  - (e) número de vínculos simultâneos depois do início.
- **Análises:**
  - descritivo por ciclo e faixa;
  - RDD nos cortes da fração de entrantes "novos no município" e da distância,
    por município com médico ativo; é condicional à alocação, então com limites
    de Lee usando a fração de células preenchidas;
  - logit da escolha com a distância (só para alocados), sensibilidade.

### X2 — Permanência dos alocados

- **Ligação:** alocados e homologados da 1ª chamada dos ciclos 1 e 2 (arquivos
  de resultado) contra a lista de ativos de 09/10/2026, por CRM quando houver e
  por nome + curso + município.
- **Outcome:** alocado ainda ativo no retrato, por célula e por município.
- **Análise:** RDD com limites de Lee (seleção = preencher); descritivo por faixa.

### X3 — Dinâmica dos ativos

- **Fonte:** `data/pmm_especialistas_serie_historica.csv` (município × curso ×
  mês, dez/25 a ago/26).
- **Outcomes:** ativos por município e curso em cada mês; queda do pico ao
  último mês; meses com ativo.
- **Análise:** RDD mês a mês (estilo estudo de evento, sem pré-período) e RDD
  da queda; descritivo.

### X4 — Heterogeneidade da escolha (E9)

No modelo principal do E9, interações da bolsa com:
- (a) a nota do candidato (tercis dentro do ciclo);
- (b) o curso (curso a curso, com ao menos 100 candidatos);
- (c) a escassez pré-programa da especialidade no município (vínculos das CBO
  do curso por 10 mil habitantes em 202406–202506, painel nacional), em tercis;
- (d) o estrato territorial.

Mesmos erros-padrão do E9, com cluster por conjunto e por curso.

### X5 — Deslocamento regional

- **Teste:** no logit condicional, se a bolsa maior de uma célula reduz a
  escolha de células de bolsa menor da mesma região de saúde, além do efeito
  direto.
- **Formas:** (i) logit aninhado por região de saúde dentro do curso e ciclo;
  (ii) nas células, o número de células vizinhas (mesma região) com bolsa
  maior como atributo.
- **Leitura:** pela proposta A, o efeito de vizinhança é negativo.

### X6 — Poder e o que se descarta

Para cada outcome principal de E6, E7 e E9:
- efeito mínimo detectável a 80% e 5% (2,8 × EP);
- limite superior do IC 95% em termos absolutos e relativos à média abaixo do
  corte;
- comparação com as referências do protocolo 40 (+10 p.p., +25%) e com os
  efeitos da literatura citados no doc 20.

Tudo lido das saídas existentes, sem estimação nova.

## 4. Saídas

| Id | Script | Saídas | Doc |
|---|---|---|---|
| X1 | `scripts/rdd_bolsa/17_ponte_pmme_cnes.py` | `output/rdd_bolsa/X1_*` | 46 |
| X2, X3 | `scripts/rdd_bolsa/18_permanencia_ativos.py` | `output/rdd_bolsa/X2_*`, `X3_*` | 46 |
| X4, X5 | `scripts/rdd_bolsa/19_escolha_heterogeneidade.py` | `output/rdd_bolsa/X4_*`, `X5_*` | 46 |
| X6 | `scripts/rdd_bolsa/20_poder_descartes.py` | `output/rdd_bolsa/X6_*` | 46 |

A leitura conjunta vai para `docs/06_execucao/46_resultados_exploratorios_pos_sintese.md`.
