# Prompt: Infraestrutura de Parser e Pipeline DBC -> Parquet do DATASUS

> **Status:** módulo de infraestrutura preparatório para o piloto SIH do ciclo 3
> e eventual SIA condicional.
> **Execução:** isolável da V1 econométrica, em worktree/branch próprio.
> **Armazenamento:** meta de pegada **persistente** reduzida, a ser demonstrada
> em benchmark. Isso não equivale ao volume transferido: em 2025-01, uma
> competência nacional comprimida ocupava 84,6 MiB no SIH/RD e 1,70 GiB no
> SIA/PA.

---

## Objetivo

Implementar um módulo utilitário e um pipeline resiliente para aquisição, descompressão e conversão de arquivos DBC do DATASUS para formato Parquet particionado e filtrado, seguindo estritamente as regras de integridade do repositório (`AGENTS.md`).

### Requisitos Técnicos:

1. **Módulo Utilitário de Parser (`scripts/utils/datasus_dbc.py`):**
   - Construir uma rotina em Python capaz de ler e descompactar arquivos `.dbc` do DATASUS para `pandas.DataFrame` / `pyarrow.Table` (usando bibliotecas de descompressão Blast/DBC consolidadas, como `pyreaddbc` ou bindings de descompressão do algoritmo Blast do DATASUS).
   - Fornecer função `dbc_to_parquet(input_dbc_path, output_parquet_path, filter_cols=None, filter_query=None)` com suporte a particionamento e compressão `zstd`.

2. **Pipeline de Ingestão Resiliente e Eficiente em Disco (`scripts/aquisicao/06_adquirir_datasus.py` ou similar):**
   - Download automatizado via FTP público do DATASUS (`ftp://ftp.datasus.gov.br/dissemin/publicos/SIASUS/` e `SIHSUS/`) com tratamento de retentativas, fallbacks e idempotência (verificação de `.part` e hash SHA-256).
   - **Economia de disco:** processar uma UF–competência por vez, filtrar pelos
     CNES/municípios/procedimentos da coorte congelada e remover o intermediário
     somente após validar o Parquet e registrar URL, tamanho e SHA-256. Medir
     separadamente tráfego, pico temporário e espaço persistente; não prometer
     `<1 GB` antes do piloto.
   - Começar por SIH/RD. Não adquirir SIA/PA sem decisão explícita do portão
     descrito em `prompts/avaliacao_ciclo3/03_torneio_pre_tratamento_e_pre_analise.md`.
   - Geração de manifesto JSON com metadados (linhas lidas, linhas filtradas, taxa de compressão e hashes SHA-256).

3. **Validação e Benchmark:**
   - Criar teste de integração que processe primeiro uma competência SIH de uma
     UF da coorte para validar esquema, tipos, zeros à esquerda, AIH inicial
     versus continuidade e velocidade com DuckDB/PyArrow. Um piloto SIA é uma
     etapa condicional separada.
   - Manter o pipeline modular e isolado, sem alterar os dados brutos existentes em `data/` e sem quebrar o pipeline principal vigente da V1 (`run_all.py`).
