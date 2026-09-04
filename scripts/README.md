# Scripts do Projeto PMM-E

Este diretório contém todas as rotinas executáveis, pipelines de processamento, modelos econométricos e utilitários do projeto de avaliação de impacto do **Programa Mais Médicos Especialistas (PMM-E / Lei nº 15.233/2025)**.

---

## 1. Ponto de Entrada Canônico: `run_all.py`

O script mestre na raiz do repositório ([`run_all.py`](../run_all.py)) orquestra e executa ponta a ponta o estado validado da pesquisa:

```bash
python run_all.py
```

Ele executa sequencialmente:
1. `scripts/00_inventario_dados.py` — inventário determinístico das bases observadas.
2. `scripts/02_auditar_fontes_pmme.py` — auditoria e integridade de fontes oficiais.
3. `scripts/aquisicao/01_congelar_ponte_cbo.py` — congelamento da ponte operacional curso–CBO.
4. `scripts/aquisicao/02_consolidar_quadro_vagas.py` — consolidação da matriz de vagas e tratamento.
5. `scripts/aquisicao/04_harmonizar_territorio_ibge.py` — harmonização territorial e malha do IVS 2010.
6. `scripts/aquisicao/05_integrar_painel_analitico.py` — construção do painel analítico CNES mensal.
7. `scripts/avaliacao_impacto/run_pipeline_avaliacao.py` — pipeline completo do diagnóstico histórico DDD (etapas 01 a 09).
8. `scripts/tema_trabalho/01_auditar_atracao_provimento_interior.py` — diagnóstico de atração e provimento.
9. `scripts/tema_trabalho/02_reconciliar_funil_ciclo1.py` — reconciliação do funil administrativo (A1).
10. `scripts/tema_trabalho/03_construir_tipologia_territorial.py` — estratificação territorial em 4 níveis (A2).
11. `scripts/tema_trabalho/04_congelar_pre_analise.py` — pré-análise e cálculo de potência econométrica (A3).
12. `scripts/tema_trabalho/05_estimar_atracao.py` — estimação dos modelos LPM e Logit de atração (A4).
13. `scripts/tema_trabalho/06_avaliar_provimento_cnes.py` — avaliação da evolução do estoque médico cadastrado no CNES (A5).
14. `scripts/tema_trabalho/07_red_team_sintese.py` — síntese red team, matriz de evidências e manifesto reproduzível (A6).
15. `scripts/tema_trabalho/08_auditar_cutoff_selecao.py` — auditoria do último selecionado versus primeiro não selecionado, ligação agregada a homologação/presença ativa e portão causal (A7).

---

## 2. Mapa dos Subdiretórios

```text
scripts/
├── 00_inventario_dados.py              # Inventário determinístico de entradas
├── 01_adquirir_fontes_pmme.py          # Download idempotente de editais e planilhas públicas
├── 02_auditar_fontes_pmme.py           # Auditoria estrutural e hashes de fontes do PMM-E
├── 03_planejar_aquisicao_cnes.py       # Planejamento e manifesto de competências CNES
├── aquisicao/                          # Tratamento de vagas, ponte CBO, malha e painel
├── avaliacao_ciclo3/                   # Protocolo prospectivo e piloto do ciclo 3
├── avaliacao_impacto/                  # Pipeline do diagnóstico histórico DDD agregada
├── rdd_bolsa/                          # Diagnóstico de viabilidade do RDD do IVS / adicional
├── revisao_literatura/                 # Mineração bibliográfica e geradores históricos
├── tema_trabalho/                      # Núcleo principal de atração e dinâmica local (A1–A7)
└── utils/                              # Utilitários compartilhados (DBC parser, gráficos, tema)
```

### Detalhamento por Domínio:

- **`aquisicao/`:** Scripts responsáveis pela ingestão, higienização, mapeamento curso–CBO e integração longitudinal das 26 competências do CNES. Contém tanto a rotina de produção (`01_` a `05_`) quanto os scripts de auditoria de versões (`a01_` a `a06_`).
- **`tema_trabalho/`:** Contém a cadeia empírica central do artigo (A1 a A7), desde a auditoria inicial, construção da tipologia territorial (REGIC + RMs), pré-análise, estimações econométricas principais (LPM/Logit com clustering municipal) até o red team de encerramento.
- **`avaliacao_impacto/`:** Reúne o pipeline do diagnóstico histórico DDD (imediatas vs reserva). Avalia portão de relevância, constrói painéis analíticos, estima modelos estáticos e dinâmicos (estudo de evento), testa mecanismos, gera figuras, nota técnica e infográfico.
- **`rdd_bolsa/`:** Rotinas de auditoria e teste de viabilidade para o desenho de regressão descontínua (RDD) baseado no adicional de R$ 5 mil e limiares do IVS 2010.
- **`avaliacao_ciclo3/`:** Pipeline prospectivo do ciclo 3 (congelamento de coorte, ingestão de dados de procedimentos hospitalares SIH/SUS pré-tratamento e auditoria de potência).
- **`revisao_literatura/`:** Mineração de referências (`01_minerar_literatura.py`) e subpasta `historico/` com os scripts de apoio que geraram tabelas de rúbrica e documentação teórica em estágios anteriores.
- **`utils/`:** Módulos utilitários reutilizáveis:
  - `datasus_dbc.py`: descompressão e parsing de arquivos `.dbc` do DATASUS.
  - `theme_pmme.py`: paleta de cores e estilo visual padronizado para gráficos.
  - `gerar_grafico_custo_laboral.py`: geração da figura conceitual de custo laboral/burnout.

---

## 3. Diretrizes para Novos Scripts

1. **Caminhos relativos:** Sempre defina o diretório raiz via `ROOT = Path(__file__).resolve().parents[...]` para garantir que o script funcione independentemente de onde for invocado.
2. **Imutabilidade de `data/`:** NUNCA modifique arquivos em `data/`. Todas as transformações devem ser salvas exclusivamente em `output/`.
3. **Determinismo:** Defina sementes de números aleatórios (`random_state`) e evite ordenações não determinísticas.
4. **Princípio Fail-Closed:** Se uma verificação de integridade ou invariante falhar, lance erro explícito (`AssertionError` ou `ValueError`) em vez de mascarar valores com imputações silenciosas.
