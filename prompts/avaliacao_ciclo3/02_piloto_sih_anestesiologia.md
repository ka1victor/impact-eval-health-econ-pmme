# C3-02 — Piloto SIH pré-tratamento para anestesiologia

## Objetivo

Implementar aquisição leve e auditável do SIH/RD e construir somente outcomes
pré-tratamento para avaliar a viabilidade de anestesiologia/cirurgias. Não abrir
nem estimar o pós-período.

## Pré-requisitos

- C3-01 incorporado e revisado;
- `T0`, UFs, municípios, CNES e braços congelados;
- ausência de resultados pós-tratamento nos insumos analíticos.

Leia `AGENTS.md`, `CLAUDE.md`,
`docs/12_estrategia_causal_prospectiva_ciclo3.md`, o relatório C3-01, a
[documentação oficial do SIH](https://wiki.saude.gov.br/sih/index.php/P%C3%A1gina_principal),
o layout RD e o prompt `prompts/infraestrutura_datasus_dbc.md`.

## Trabalho em duas fases

### Fase 1 — benchmark obrigatório

1. Escolha uma UF–competência pré-tratamento com CNES tratados e controles.
2. Baixe o DBC para diretório temporário, registre URL/tamanho/data/SHA-256 e
   converta com parser testado.
3. Compare linhas, tipos e contagens com uma consulta oficial agregada quando
   possível.
4. Meça tempo, pico de disco e tamanho do Parquet filtrado.
5. Pare se o parser perder registros, corromper zeros à esquerda ou não
   distinguir AIH inicial de continuidade.

### Fase 2 — pré-painel

1. Adquira somente UFs e competências entre 2024-06 e `T0-1` necessárias à
   coorte congelada.
2. Processe um arquivo por vez; preserve apenas derivados filtrados e manifestos.
3. Historicize SIGTAP por competência antes de definir a família cirúrgica.
4. Construa candidatos de outcome sem olhar o pós:
   - AIHs iniciais eletivas por CNES–mês;
   - total municipal por ocorrência;
   - total de residentes por município e local de ocorrência;
   - mortalidade, permanência e valor apenas para diagnóstico exploratório.
5. Não solicite, exponha nem persista CNS ou identificadores civis. Use apenas
   campos necessários à agregação.
6. Diferencie competência de processamento, internação e alta.

## Entregáveis

- parser reutilizável em `scripts/utils/datasus_dbc.py`;
- aquisição em `scripts/avaliacao_ciclo3/02_adquirir_sih_pre.py`;
- testes do parser e do esquema;
- `output/avaliacao_ciclo3/sih_pre/` com Parquets agregados/filtrados;
- `output/avaliacao_ciclo3/manifesto_sih_pre.json`;
- `output/avaliacao_ciclo3/dicionario_procedimentos_anestesia.csv`;
- `docs/auditorias/06_piloto_sih_anestesiologia.md`.

## Validações

- hashes, tamanho e competência de cada DBC;
- reconciliação de linhas lidas, filtradas e agregadas;
- unicidade no grão declarado;
- cobertura mensal e zeros estruturais explícitos;
- AIH inicial separada de continuidade;
- versões SIGTAP e códigos válidos em cada mês;
- nenhum arquivo bruto existente modificado;
- pico de espaço e tráfego efetivo reportados, sem prometer `<1 GB` antes do
  benchmark;
- testes automatizados e `git diff --check`.

Não estime DiD, não consulte meses `>=T0`, não escolha procedimentos pela
resposta pós-tratamento e não baixe SIA.

Ao final, crie commit próprio e não faça push.
