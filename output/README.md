# Artefatos Gerados (Output) do Projeto PMM-E

Este diretório contém todos os produtos derivados, painéis analíticos, tabelas de regressão, figuras científicas, notas técnicas e manifestos de replicação gerados pelo pipeline de pesquisa.

---

## 1. Princípio de Reprodutibilidade

Todos os artefatos neste diretório são gerados deterministicamente a partir das bases brutas em `data/` por meio de scripts versionados em `scripts/`.

Para reproduzir todos os produtos do pipeline validado:
```bash
python run_all.py
```

---

## 2. Mapa dos Subdiretórios e Artefatos

```text
output/
├── auditoria_fontes_pmme.json             # Hashes e auditoria de fontes públicas
├── inventario_dados.json                  # Inventário determinístico de insumos
├── manifesto_aquisicao_cnes.json          # Rastreabilidade dos 26 arquivos ZIP do CNES
├── manifesto_fontes_pmme.json             # Manifestos de download de editais
├── painel_municipio_curso_mensal.parquet  # Painel longitudinal consolidado
├── aquisicao/                             # Insumos intermediários e auditorias de entrada
├── avaliacao_ciclo3/                      # Coorte congelada e pré-análise do ciclo 3
├── avaliacao_impacto/                     # Diagnóstico histórico DDD (tabelas, figuras, notas)
├── rdd_bolsa/                             # Diagnóstico de viabilidade do RDD do IVS
├── revisao_literatura/                    # Rúbricas e matrizes comparativas de papers
└── tema_trabalho/                         # Núcleo principal de atração e provimento (A1–A7)
```

### Detalhamento por Domínio:

- **`tema_trabalho/`:** Resultados centrais da pesquisa atual:
  - `matriz_funil_ciclo1.parquet` e `portao_denominador.json` (A1 — reconciliação do funil).
  - `matriz_tipologia_territorial.parquet` e `suporte_estratos_territoriais.csv` (A2 — REGIC + RMs).
  - `registro_pre_analise_atracao.json` e `potencia_atracao.json` (A3 — pré-análise e MDE).
  - `A4_tabela_02_modelo_principal_LPM.csv`, `A4_tabela_02b_logit_AME.csv` e figuras de gradiente (A4 — estimação de atração).
  - `A5_relatorio_diagnostico.md` e tabelas dinâmicas de oferta cadastrada (A5 — evolução CNES).
  - `A6_matriz_afirmacao_evidencia_limite.csv` e `A6_manifesto_reproducao.json` (A6 — auditoria de afirmações e manifesto com hashes SHA-256).

- **`avaliacao_impacto/`:** Artefatos da investigação histórica agregada DDD (2024–2026):
  - `dados/`: painel município–curso–mês e subamostra confirmatória de 10 cursos unívocos.
  - `modelos/`: coeficientes, erros-padrão clusterizados e diagnósticos numéricos de absorção dos modelos DDD e estudo de evento.
  - `tabelas/`: baseline, estatísticas descritivas e modelos estáticos/dinâmicos.
  - `figuras/`: estudo de evento, trajetórias brutas, mecanismos e `figura_master_infografico_pmme.png`.
  - `relatorios/`: relatório do portão de relevância e nota técnica consolidada.

- **`aquisicao/`:**
  - `ponte_curso_cbo_oficial.json`: mapeamento operacional entre cursos e CBOs com status explícito de sobreposição.
  - `quadro_vagas_tratamento.parquet`: universo de 1.295 células de oferta do ciclo 1.
  - `malha_municipios_regioes_saude.parquet` e `painel_municipios_regioes.parquet`: harmonização territorial IBGE/IPEA.

- **`rdd_bolsa/`:** Diagnósticos de viabilidade da grade salarial e teste de replicação do escore administrativo IVS 2010.

- **`avaliacao_ciclo3/`:** Coorte congelada, manifesto dos 673 arquivos hospitalares SIH/SUS e auditoria pré-tratamento de anestesiologia.

---

## 3. Política de Versionamento

- **Rastreados no Git:** Relatórios `.json` de metadados/hashes, tabelas analíticas em `.csv`, figuras editoriais em `.png` e notas técnicas em `.md`.
- **Ignorados pelo Git (`.gitignore`):** Parquets volumosos de alta dimensionalidade (`cnes_vinculos_*.parquet`, microdados mensais brutos) para manter o repositório leve, ágil e clonável.
