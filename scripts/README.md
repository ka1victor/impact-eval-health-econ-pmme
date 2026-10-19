# Scripts do Projeto PMM-E

Este diretório contém todas as rotinas executáveis, pipelines de processamento, modelos econométricos e utilitários do projeto de avaliação de impacto do **Programa Mais Médicos Especialistas (PMM-E / Lei nº 15.233/2025)**.

---

## 1. Ponto de Entrada Canônico: `run_all.py`

O script mestre na raiz do repositório ([`run_all.py`](../run_all.py)) orquestra e executa ponta a ponta o estado validado da pesquisa:

```bash
python run_all.py              # pipeline inteiro
python run_all.py --rdd-bolsa  # só a cadeia da RDD da bolsa
```

A lista `STEPS` do `run_all.py` é a fonte da ordem; o manifesto A6 a copia.
Ele executa sequencialmente:
1. `scripts/00_inventario_dados.py` — inventário determinístico das bases observadas.
2. `scripts/02_auditar_fontes_pmme.py` — auditoria e integridade de fontes oficiais.
3. `scripts/aquisicao/01_congelar_ponte_cbo.py` — congelamento da ponte operacional curso–CBO.
4. `scripts/aquisicao/02_consolidar_quadro_vagas.py` — consolidação da matriz de vagas e tratamento.
5. `scripts/aquisicao/a07_adquirir_ivs_administrativo.py` e `a08_adquirir_ivs_2010_oficial.py` — escore publicado pelo MS e base completa do Ipea (zip fora do Git; tamanho e SHA-256 em `output/aquisicao/a08_manifesto_ivs_2010_oficial.json`). Rodam antes da malha desde 18/10/2026.
   Depois, `scripts/aquisicao/04_harmonizar_territorio_ibge.py` — harmonização territorial com o IVS 2010 oficial (a08) e o Censo 2022; até 18/10/2026 lia o arquivo de IVS errado (`docs/auditorias/19_reestimacao_base_oficial_failure_mode.md`).
6. `scripts/aquisicao/05_integrar_painel_analitico.py` — construção do painel analítico CNES mensal.
7. `scripts/avaliacao_impacto/run_pipeline_avaliacao.py` — pipeline completo do diagnóstico histórico DDD (etapas 01 a 09).
8. `scripts/tema_trabalho/01_auditar_atracao_provimento_interior.py` — diagnóstico de atração e provimento.
9. `scripts/tema_trabalho/02_reconciliar_funil_ciclo1.py` — reconciliação do funil administrativo (A1).
10. `scripts/tema_trabalho/03_construir_tipologia_territorial.py` — estratificação territorial em 4 níveis (A2).
11. `scripts/tema_trabalho/04_congelar_pre_analise.py` — pré-análise e cálculo de potência econométrica (A3).
12. `scripts/tema_trabalho/05_estimar_atracao.py` — estimação dos modelos LPM e Logit de atração (A4).
13. `scripts/tema_trabalho/06_avaliar_provimento_cnes.py` e `06b_ameacas_a5_placebo_pretendencia_deslocamento.py` — evolução do estoque médico cadastrado no CNES e as três ameaças testadas (A5).
14. `scripts/tema_trabalho/07_red_team_sintese.py` — síntese red team, matriz de evidências e manifesto reproduzível (A6).
15. `scripts/tema_trabalho/08_auditar_cutoff_selecao.py` — auditoria do último selecionado versus primeiro não selecionado, ligação agregada a homologação/presença ativa e portão causal (A7).
16. `scripts/tema_trabalho/09_estimar_cutoff_escore_estrito.py` e `09b_intervalos_exatos_escore.py` — efeito local condicional no corte de seleção, placebos, sensibilidades, replicação e intervalos exatos (A8).
17. **RDD da bolsa** (IVS 2010 oficial do Ipea como running variable; `docs/06_execucao/37`, `38` e `39`):
    - as aquisições `a07` e `a08` rodam no início (passo 5);
    - `scripts/rdd_bolsa/04_*`, `04b_*` e `04c_*` — portão R1 (`APROVADO_SHARP`), escore completo e identificação do arquivo de IVS errado;
    - `05_*` (E1), `06_*` (E2), `07_*` (E3, principal), `08a_*` e `08_*` (E4) e `11_*` (E5, exploratório);
    - rodada multi-outcome (`docs/06_execucao/40_protocolo_multioutcome_rdd_bolsa.md`, §11):
      - `scripts/aquisicao/a10_normas_mesmos_cortes_ivs.py` — normas federais nos mesmos cortes do IVS (cache em `data/raw/aquisicao/normas_ivs/` conferido por SHA-256; só baixa ato ausente) e IED da Portaria 3.493/2024;
      - `scripts/aquisicao/a11_adquirir_resultado_ciclo2_chamada1.py` — resultado da 1a chamada do ciclo 2 (arquivos em `data/raw/pmm_e/` conferidos por SHA-256; só baixa arquivo ausente);
      - `scripts/aquisicao/a09_adquirir_cnes_nacional.py` — CNES nacional; no pipeline roda em `--etapa verificar`: confere o painel versionado contra o manifesto, sem rede e sem gravar. Refazer o painel exige pedir `--etapa painel` (cache local, fora do Git) ou `--etapa tudo` (39 ZIPs, ~23 GB);
      - `scripts/aquisicao/a13_adquirir_sih_tabnet.py` — SIH/SUS no TabNet (protocolo 47, insumo de K2): AIH por município de internação × mês de processamento × grupo; no pipeline roda em `--etapa verificar` (sem rede, não grava). Refazer exige `--etapa consolidar` (cache local, fora do Git) ou `--etapa tudo` (440 consultas ao TabNet);
      - `scripts/rdd_bolsa/12_construir_outcomes_funil.py` — outcomes F0–F4 dos ciclos 1–3 e tabelas de escolha;
      - `scripts/rdd_bolsa/13_estimar_E6_funil.py` — E6, RDD dos outcomes do funil (lê a janela LR do E5);
      - `scripts/rdd_bolsa/23_estimar_contagem_vagas.py` — família N (protocolo 48, pós-resultado): número de vagas preenchidas com e sem controle pelas vagas oferecidas, decomposição, Poisson, placebos e figuras (`docs/06_execucao/49`);
      - `scripts/rdd_bolsa/16_estimar_E9_escolha.py` — E9, logit condicional da escolha dos candidatos;
      - `scripts/rdd_bolsa/14_estimar_E7_dird_cnes.py` — E7, DiRD no CNES nacional (confere a janela LR de U com a do E6).
      - `scripts/rdd_bolsa/15_sintese_E8.py` — síntese E8: Holm das primárias P1 e P2 e tabela-síntese (`docs/06_execucao/44`);
    - `09b_conferir_sinal.py`, `09_gerar_relatorio_pdf.py` e `10_galeria_figura_regra.py` — conferência do sinal, relatório em PDF (E1 a E9 e síntese E8) e galeria da figura da regra;
18. `scripts/tema_trabalho/10_conferir_numeros_artigo.py` e `11_conferir_numeros_artigo_curto.py` — relêem os artefatos, reformatam cada valor no padrão dos artigos e exigem que o trecho exista em `paper_pmme_submission.tex` e `paper_pmme_curto.tex`; falham se alguma cifra não tiver origem rastreável.

Rodada exploratória pós-síntese (`docs/06_execucao/45` e `46`), fora do
`run_all.py` por ser exploratória e, no X1, por baixar seis competências do CNES
com o registro profissional (cache local fora do Git):
`scripts/rdd_bolsa/17_ponte_pmme_cnes.py` (X1, ponte PMM-E–CNES pelo CRM),
`18_permanencia_ativos.py` (X2 e X3), `19_escolha_heterogeneidade.py` (X4 e X5)
e `20_poder_descartes.py` (X6, só aritmética sobre saídas existentes).

Saíram do pipeline em 18/10/2026, sem apagar os scripts: `scripts/rdd_bolsa/01_*`,
`01b_*`, `02_*` e `03_*`. Eles usavam `data/ivs_ipea_2010_municipios.csv`, que não
é o IVS do município (`docs/auditorias/16_ivs_2010_oficial_e_arquivo_local.md`),
ou dependiam do pedido do escore ao MS, cancelado porque o escore é público.

Fora do pipeline, por depender do histórico do Git: `scripts/tema_trabalho/12_registrar_failure_mode_ivs.py`
lê as versões de A2, A4, A5 e da Tabela 1 anteriores à correção de 18/10/2026 no commit
`22eddb5`, compara com as atuais e gera `output/tema_trabalho/failure_mode_ivs_*` e
`docs/auditorias/19_reestimacao_base_oficial_failure_mode.md`. Rodar depois do pipeline.
Não entra no `run_all.py` porque lê os valores "antes" com `git show` do commit de
referência e para sem ele: num clone raso ou numa exportação do repositório o
pipeline quebraria por um motivo alheio aos dados.

---

## 2. Mapa dos Subdiretórios

```text
scripts/
├── 00_inventario_dados.py              # Inventário determinístico de entradas
├── 01_adquirir_fontes_pmme.py          # Download idempotente de editais e planilhas públicas
├── 02_auditar_fontes_pmme.py           # Auditoria estrutural e hashes de fontes do PMM-E
├── 03_planejar_aquisicao_cnes.py       # Planejamento e manifesto de competências CNES
├── apresentacao/                       # Figuras da apresentação da banca 1, geradas de output/
├── aquisicao/                          # Tratamento de vagas, ponte CBO, malha, painel e população
├── avaliacao_ciclo3/                   # Protocolo prospectivo e piloto do ciclo 3
├── avaliacao_impacto/                  # Pipeline do diagnóstico histórico DDD agregada
├── rdd_bolsa/                          # RDD do adicional de bolsa nos cortes do IVS 2010 oficial
├── revisao_literatura/                 # Mineração bibliográfica e geradores históricos
├── tema_trabalho/                      # Núcleo principal de atração e cutoff causal local (A1–A8)
└── utils/                              # Utilitários compartilhados (DBC parser, gráficos, tema)
```

### Detalhamento por Domínio:

- **`aquisicao/`:** Scripts responsáveis pela ingestão, higienização, mapeamento curso–CBO e integração longitudinal das 26 competências do CNES. Contém tanto a rotina de produção (`01_` a `05_`) quanto os scripts de auditoria de versões (`a01_` a `a06_`) e as aquisições da RDD da bolsa (`a07_` a `a11_`; o `a09_` baixa o CNES nacional só com `--etapa tudo` ou `aquisicao`) e da produção especializada (`a13_`, SIH no TabNet; baixa só com `--etapa baixar` ou `tudo`). O `06_adquirir_populacao_censo2022.py` baixa a população residente do Censo 2022 (IBGE/SIDRA), único denominador populacional válido do repositório — a coluna `populacao_2010` do arquivo do IVS não é população residente.
- **`apresentacao/`:** `gerar_figuras_banca1.py` produz as figuras da banca 1 em `output/apresentacao_banca1/`, com manifesto de entradas e hashes. Lê o painel município–curso–mês e a população do Censo 2022; não recalcula nada do pipeline analítico.
- **`tema_trabalho/`:** Contém a cadeia empírica central do artigo (A1 a A8), desde a auditoria inicial, tipologia territorial e resultados associativos até o cutoff estrito de seleção, seus placebos e a replicação pública.
- **`avaliacao_impacto/`:** Reúne o pipeline do diagnóstico histórico DDD (imediatas vs reserva). Avalia portão de relevância, constrói painéis analíticos, estima modelos estáticos e dinâmicos (estudo de evento), testa mecanismos, gera figuras, nota técnica e infográfico.
- **`rdd_bolsa/`:** RDD sharp do adicional de R$ 5 mil nos cortes 0,300 e 0,400 do IVS 2010 oficial do Ipea: portão R1, escore completo, estimações E1 a E5, conferência do sinal, relatório e galeria; na rodada multi-outcome, outcomes do funil (`12_`), E6 (`13_`), E7 (`14_`) e E9 (`16_`), com a biblioteca `rdd_lib.py`. Os scripts `00_` a `03_` são registro superado: usavam o arquivo de IVS errado ou o pedido de dados cancelado.
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
