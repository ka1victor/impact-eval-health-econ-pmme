# AGENTS.md — Instruções para Agentes no Repositório PMM-E

> Este arquivo orienta agentes autônomos sobre os padrões de qualidade, execução de scripts e convenções econométricas.

---

## 1. Execução de Scripts e Pipeline

* O script mestre `run_all.py` executa o pipeline ponta a ponta.
* Todos os scripts em `scripts/` utilizam caminhos relativos ao diretório raiz deste repositório e salvam saídas consolidadas em `output/`.
* Nunca altere arquivos brutos em `data/`; gere sempre novas transformações via scripts versionados.

---

## 2. Escopo do Projeto

* O escopo do projeto é a **avaliação causal de impacto do Programa Mais Médicos Especialistas (PMM-E / Lei 15.233/2025)** sobre a atração de força de trabalho médica, retenção municipal de pacientes (resolutividade local), desfechos de saúde (exames diagnósticos e internações) e custo-benefício logístico.
* A running variable canônica é o **IVS 2010 oficial do IPEA** (`output/aquisicao/a08_ivs_2010_oficial_municipio.csv`), igual ao escore administrativo do MS. **`data/ivs_ipea_2010_municipios.csv` não é o IVS do município** (é uma linha de subgrupo da mesma base, em 78% dos municípios a de mulheres negras em área urbana) e não deve ser usado. Não substitua por IDHM ou PIB per capita sem justificativa econométrica explícita e autorização do autor.
