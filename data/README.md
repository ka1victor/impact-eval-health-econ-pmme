# Dados Observados do Projeto PMM-E

Este diretório armazena todas as bases de dados brutas e observadas utilizadas na pesquisa de avaliação de impacto do **Programa Mais Médicos Especialistas (PMM-E / Lei nº 15.233/2025)**.

---

## 1. Regra Fundamental de Integridade

> [!CAUTION]
> **NUNCA altere, substitua ou edite arquivos dentro de `data/`.**
> Todas as bases aqui armazenadas são insumos observados brutos ou congelados de fontes públicas oficiais. Quaisquer limpezas, transformações, agregações e cruzamentos devem ser executados via scripts versionados em `scripts/` e gravados exclusivamente em `output/`.

---

## 2. Estrutura dos Arquivos

```text
data/
├── ivs_ipea_2010_municipios.csv             # Running variable canônica (IVS 2010 IPEA por município)
├── pmm_especialistas_nominal.csv            # Dados administrativos nominais do PMM-E
├── pmm_especialistas_serie_historica.csv    # Série histórica consolidada do programa
└── raw/
    ├── aquisicao/                           # Insumos capturados durante auditorias de versão
    │   ├── ivs_regra/                       # Editais, portarias normativas e Lei 15.233/2025
    │   ├── territorio/                      # REGIC 2018 (IBGE) e Composição de RMs/RIDEs 2022
    │   ├── trajetoria/                      # Histórico de confirmações e homologações
    │   └── vagas/                           # Editais e quadros de vagas por ciclo/chamada
    ├── cnes/                                # 26 competências mensais do CNES (202406 a 202607)
    └── pmm_e/                               # Planilhas públicas de vagas e resultados do MS
```

---

## 3. Descrição das Fontes e Proveniência

| Base / Diretório | Fonte Oficial | Unidade de Análise | Papel na Econometria |
|---|---|---|---|
| `ivs_ipea_2010_municipios.csv` | IPEA (Atlas da Vulnerabilidade Social) | Município (IBGE 6d/7d) | Running variable canônica para o RDD e covariável de heterogeneidade territorial |
| `raw/aquisicao/territorio/` | IBGE (REGIC 2018 e Arranjos RMs 2022) | Município | Classificação em 4 estratos territoriais (Capital, Metropolitano, Interior Próximo, Interior Remoto) |
| `raw/cnes/` | DATASUS / CNES Oficial | Estabelecimento–profissional–mês | Painel longitudinal de oferta médica cadastrada de junho/2024 a julho/2026 |
| `raw/pmm_e/` e `raw/aquisicao/vagas/` | Ministério da Saúde / SGTES | Vaga / Célula município–curso | Quadro de ofertas, alocações de vagas imediatas e cadastro de reserva |
| `pmm_especialistas_nominal.csv` | Ministério da Saúde (LAI/Transparência) | Registro nominal | Insumo administrativo preservado (não vinculado diretamente sem ponte aprovada) |

---

## 4. Auditoria e Rastreabilidade

O inventário determinístico e os hashes SHA-256 de todas as entradas são monitorados e verificados pelo script:
```bash
python scripts/00_inventario_dados.py
```
O resultado consolidado com contagens de linhas, codificação e integridade é gerado em [`output/inventario_dados.json`](../output/inventario_dados.json).
