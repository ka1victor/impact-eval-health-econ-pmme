# A2 — Tipologia territorial (capital / metropolitano / interior próximo / interior remoto)

> **Data:** 2 de setembro de 2026
> **Decisão:** `APROVADO_4_ESTRATOS`
> **População A1 coberta:** 540/540 municípios (100%); 266 registros da matriz A1 sem município são fora do quadro publicado e não entram na tipologia
> **Fontes oficiais:** IBGE REGIC 2018 (hierarquia) + IBGE Composição de RMs/RIDEs 2022 (31/12/2022, pré-PMM-E) + IVS 2010 IPEA (canônico) + CNES 202407–202506

## 1. Conclusão executiva

A população aprovada em A1 foi integralmente classificada nos quatro estratos
sem consultar alocação, homologação ou CNES pós:

| Estrato | Municípios A1 | % A1 | Células quadro Ch1 | Vagas imediatas |
|---|---:|---:|---:|---:|
| capital | 25 | 4,6% | 73 | 85 |
| metropolitano | 104 | 19,3% | 289 | 149 |
| interior próximo (conectado a polo) | 235 | 43,5% | 787 | 383 |
| interior remoto | 176 | 32,6% | 146 | 61 |
| **total A1** | **540** | **100%** | **1.295** | **678** |

Nacionalmente (5570 municípios): 27 capitais, 1.363 metropolitanos (RM/RIDE 2022),
873 interior próximo, 3.307 interior remoto. A variação é suficiente para estimar
heterogeneidade territorial sem redefinir a amostra após os resultados.

A remoticidade não foi inferida apenas por ser não capital: segue a hierarquia
urbana da REGIC 2018 (centro local = remoto; demais níveis = polo/conectado).

## 2. Regra congelada

- **capital:** `co_ibge_7d` ∈ 27 capitais oficiais (DTB estável).
- **metropolitano:** não capital e membro de RM ou RIDE na composição oficial IBGE
  de 31/12/2022 (pré-PMM-E; `Composicao_RMs_RIDEs_AglomUrbanas_2022_v2.xlsx`).
- **interior remoto:** não capital, não RM/RIDE e `REGIC hierarquia_grupo = 5 - Centro Local`
  (com ou sem integrante de arranjo populacional).
- **interior próximo (conectado a polo):** não capital, não RM/RIDE e
  `hierarquia_grupo ∈ {1-Metrópole, 2-Capital Regional, 3-Centro Sub-Regional, 4-Centro de Zona}`
  (com ou sem integrante de AP) — municípios com função de polo ou sub-polo regional.

Medidas contínuas preservadas (todas prévias):
`ivs_2010` (+ subíndices infra/ch/rt, categoria), `populacao_2010`, `idhm_2010`,
`rdpc_2010`, `macro_regiao_saude`/`no_regiao_saude`,
`estoque_especialistas_pre_12m_media` (CNES 202407–202506, média mensal por município,
soma sobre CNES/curso do quadro) e `estoque_pre_por_10k`.

Colunas de outcome (`n_confirmacoes`, `n_homologacoes`, `outcome_*`, `alocacao*`)
foram bloqueadas na construção; a tipologia não leu confirmação, homologação ou CNES pós.

## 3. Fontes e versionamento

| Fonte | Arquivo | SHA-256 (manifest) |
|---|---|---|
| Malha + IVS 2010 | `output/aquisicao/malha_municipios_regioes_saude.parquet` | ver `manifesto_tipologia_territorial.json` |
| Quadro Ch1 | `output/aquisicao/quadro_vagas_tratamento.parquet` | — |
| Matriz A1 | `output/tema_trabalho/matriz_funil_ciclo1.parquet` | — |
| Painel CNES | `output/painel_cnes_especialidade_mensal.parquet` | — |
| REGIC 2018 | `data/raw/aquisicao/territorio/REGIC2018_Municipios_Hierarquia_e_regiao.xlsx` | — |
| RM/RIDE 2022 | `data/raw/aquisicao/territorio/Composicao_RMs_RIDEs_AglomUrbanas_2022_v2.xlsx` | — |

URLs oficiais versionadas registradas no manifesto:
`geoftp.ibge.gov.br/organizacao_do_territorio/divisao_regional/regioes_de_influencia_das_cidades/.../REGIC2018_Municipios_Hierarquia_e_regiao.xlsx`
e
`geoftp.ibge.gov.br/organizacao_do_territorio/estrutura_territorial/municipios_por_regioes_metropolitanas/Situacao_2020a2029/Composicao_RMs_RIDEs_AglomUrbanas_2022_v2.xlsx`.

Arquivos brutos não são alterados; o script baixa apenas se ausente.

## 4. Missing, códigos e concentração

- **Cobertura A1:** 540/540 (100%), nenhum `NAO_CLASSIFICADO`.
- **Mudanças de código municipal:** 5 municípios criados após o Censo 2010
  (`1504752` Mojuí dos Campos/PA, `4212650` Pescaria Brava/SC,
  `4220000` Balneário Rincão/SC, `4314548` Pinto Bandeira/RS,
  `5006275` Paraíso das Águas/MS) não constam em `malha_municipios_regioes_saude.parquet`
  (base IVS 2010 = 5.565) mas têm hierarquia REGIC (todos Centro Local).
  IVS/pop ficam `NA`; classificação preservada via REGIC/RM.
  Nenhum deles pertence à população A1, portanto não afeta a análise.
- **Estoque pré-oferta:** disponível para 368/540 municípios A1 (média 202407–202506).
  Os 172 sem estoque são municípios exclusiva ou predominantemente da Ch2
  (o painel CNES cobre apenas CNES/curso do quadro Ch1) — reportados como `NA`.
- **Concentração (população A1):** UF com mais municípios — ver `manifesto_tipologia_territorial.json:concentracao.por_uf_top10_populacao_A1`;
  cursos com mais células no quadro — `concentracao.por_curso_top10_quadro`.
- **Região de saúde ausente:** alguns municípios da malha têm `no_regiao_saude = ""`
  (reproduzido da fonte); mantido como string vazia e reportado no manifesto.

## 5. Suporte por estrato (sem outcomes)

`output/tema_trabalho/suporte_estratos_territoriais.csv` traz por estrato:
`n_municipios_nacional`, `n_municipios_populacao_A1`, `n_celulas_quadro_ch1`,
`n_celulas_funil_A1`, `vagas_imediatas/reserva_publicadas`,
`municipios_com_estoque_pre_disponivel`, `ivs_medio_nacional`,
`populacao_2010_media_nacional`. A tabela não contém confirmação, homologação
ou taxa por vaga (proibidas por A1).

## 6. Entregáveis e reprodutibilidade

- `scripts/tema_trabalho/03_construir_tipologia_territorial.py`
- `output/tema_trabalho/matriz_tipologia_territorial.parquet` (5570 linhas, chave `co_ibge_6d`, `in_populacao_A1`)
- `output/tema_trabalho/manifesto_tipologia_territorial.json`
- `output/tema_trabalho/suporte_estratos_territoriais.csv`
- `tests/test_tipologia_territorial.py`

```powershell
.\.venv\Scripts\python.exe scripts\tema_trabalho\03_construir_tipologia_territorial.py
.\.venv\Scripts\python.exe -m unittest tests.test_tipologia_territorial tests.test_reconciliacao_funil_ciclo1 -v
```

O script gera atomicamente matriz, suporte e manifesto. Os testes verificam
cobertura integral A1, distribuição 25/104/235/176, ausência de colunas de
outcome, unicidade da chave, privacidade, e regra de missing para os 5 novos.

## 7. Próximo portão

A3 está liberado para congelar outcome, população, MDE, covariadas, inferência e
linguagem sobre a população A1 com a tipologia agora congelada. A4 permanece
bloqueado até o registro A3 com hashes.
