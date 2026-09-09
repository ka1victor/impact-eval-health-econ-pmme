# Proveniência de figuras e números — banca 1

> **Regra aplicada:** todo número exibido declara fonte, data de referência, cobertura, unidade e reprodutibilidade<br>
> **Conteúdo dos slides:** [02_conteudo_slides.md](02_conteudo_slides.md)<br>
> **Atualização:** 9 de setembro de 2026

---

## 1. Figuras

| Código | Figura | Slide | Arquivo | Origem | Estado |
|---|---|:---:|---|---|:---:|
| `F1` | Manchetes sobre urgência em saúde e o programa | 3 | `figuras/motivacao_manchetes.png` | recortes de imprensa e gov.br, preservados do material anterior | ✅ |
| `F2` | Especialistas por 100 mil habitantes em jun/2025, por faixa de bolsa | 3 | `output/apresentacao_banca1/oferta_pre_por_faixa.png` | CNES + Censo 2022, gerada por script | ✅ |
| `F3` | Deslocamento médio para alta complexidade, por região | 3 | `figuras/deslocamento_por_regiao.png` | REGIC 2018, cálculo externo, preservada do material anterior | ⚠️ `P1` |
| `F4` | Bolsa mensal por faixa de atração | 4 | `output/apresentacao_banca1/bolsa_por_faixa.png` | Edital SGTES/MS nº 3/2025, gerada por script | ✅ |
| `F5` | Especialistas por 100 mil habitantes, mensal, por faixa, 2024–2026 | 5 | `output/apresentacao_banca1/oferta_antes_depois_por_faixa.png` | CNES + Censo 2022, gerada por script | ✅ |
| `F6` | Custo laboral líquido em função do volume de atendimentos | 9 | `docs/02_teoria/figuras/curva_custo_laboral_burnout.png` | figura conceitual do modelo, `scripts/utils/gerar_grafico_custo_laboral.py` | ✅ ilustração |

`F2`, `F4` e `F5` são produzidas por
[`scripts/apresentacao/gerar_figuras_banca1.py`](../../../scripts/apresentacao/gerar_figuras_banca1.py),
que grava `output/apresentacao_banca1/manifesto_figuras.json` com o hash das
entradas, o filtro aplicado, os marcos temporais e a série completa por faixa.

**Definição comum de `F2` e `F5`.** Numerador: profissionais distintos com
vínculo no CNES nos CBOs dos **10 cursos com correspondência unívoca
curso–CBO** (cursos 1, 2, 3, 5, 9, 12, 13, 14, 15 e 16), somados por município
— a restrição evita contar a mesma pessoa em dois cursos. Universo: **295
municípios** com vaga nesses cursos no ciclo 1. Denominador: população
residente do Censo 2022, fixa no tempo. Agrupamento pela grade de faixas de
2025 aplicada à categoria de IVS do município. É presença cadastral, não
participação no programa; não há grupo de comparação.

`figuras/especialistas_por_uf.png` (Demografia Médica 2025, 16 UFs) continua
preservada, mas **não é mais usada**: foi substituída por `F2`, que mede o mesmo
fenômeno na unidade e na dimensão da política.

---

## 2. Números exibidos

| Número | Slide | Fonte | Verificação |
|---|:---:|---|---|
| Urgência em saúde pública por dois anos | 3 | Correio do Povo, 07/05/2025 | recorte preservado em `F1` |
| 10% dos especialistas atendem no SUS | 3 | Senado Notícias, 25/09/2025, citando o Ministério da Saúde | citação de segunda mão |
| Prorrogação até fev/2027; 52% no interior | 3 | gov.br, 26/08/2026 | comunicação oficial |
| 16,0 / 10,0 / 7,3 especialistas por 100 mil hab. por faixa, jun/2025; razão 2,2 | 3 | `F2` | ✅ manifesto |
| 276, 256 e 101 km por região | 3 | REGIC 2018, cálculo externo | ⚠️ `P1` |
| Cortes do IVS: 0,200 / 0,300 / 0,400 / 0,500 | 4 | Ipea, Atlas da Vulnerabilidade Social (2015) | ✅ `docs/auditorias/01_regra_institucional.md`, §6.3 |
| R$ 20.000 / R$ 15.000 / R$ 10.000 por faixa; 20 h semanais; até 12 meses | 4 | Edital SGTES/MS nº 3/2025 | ✅ mesma auditoria, §6.1 |
| 177 dos 368 municípios com faixa publicada diferente da regra recalculada | 4, 11 | portão R1 | ✅ `docs/05_identificacao/16_sintese_achados_e_novo_plano_causal.md`, §3.5 |
| Variação pré: −4% / +7% / +4%; pós: +21% / +20% / +17% por faixa | 5 | `F5` | ✅ manifesto: 7,67→7,33→8,87; 9,30→9,97→11,94; 15,37→16,03→18,76 |
| 393 de 1.295 células com confirmação ou homologação (30,3%); 31,6% / 37,4% / 23,6% por faixa | 5 | quadro de vagas do ciclo 1, chamada 1 | ✅ `output/tema_trabalho/A4_relatorio_diagnostico.md`, linha 12; n = 291 / 465 / 539 |
| 1.295 células; 368 municípios; 1.480 ativos em 12/08/2026 | 11 | quadro de vagas; `data/pmm_especialistas_nominal.csv` | ✅ |

---

## 3. Pendência aberta

### `P1` — Figura de deslocamento sem manifesto

`F3` vem de cálculo externo sobre a REGIC 2018 e não está reproduzida no
repositório. Falta registrar tabela de origem, método de cálculo da distância,
data e hash. Não bloqueia o conteúdo. A alternativa é substituí-la por medida
municipal de acesso construída no repositório, o que exigiria adquirir a base
de deslocamentos da REGIC.

### `P2` — Equação original de Reinhardt (1975)

A documentação do projeto não transcreve a função de produção original de
Reinhardt. Na tabela de literatura ele entra como fundamento do papel de $L$ e
$K$, na mesma linha de Choné e Ma. Se a banca pedir a equação, é preciso
recuperá-la dos capítulos 3 e 4 do livro.

---

## 4. Achados registrados nesta conferência

### `populacao_2010` não é população residente

A única variável populacional em `data/` — `populacao_2010`, do arquivo do IVS
do Ipea — soma **41.852.890** contra **190.755.799** do Censo 2010, e a razão
para o valor real varia de 0,10 a 0,42 entre municípios. Qualquer taxa por
habitante construída com ela sai inflada em cerca de 4,5 vezes e distorcida de
forma não uniforme. Ela é usada como covariável (`log_pop`) nos módulos A4 e A5
e aparece rotulada como "População municipal 2010" em
`output/avaliacao_impacto/tabelas/tabela1_estatisticas_descritivas_baseline`.
O achado está registrado em
[`docs/04_dados/02_inventario_dados_por_outcome.md`](../../04_dados/02_inventario_dados_por_outcome.md),
seção 4.1. As figuras desta apresentação usam o Censo 2022, adquirido por
[`scripts/aquisicao/06_adquirir_populacao_censo2022.py`](../../../scripts/aquisicao/06_adquirir_populacao_censo2022.py).

### Distribuição regional do material anterior

A figura de participação regional do `.pptx` recebido não reproduzia a partir
de `data/`: apenas o Nordeste (60,3%) coincidia; o Sudeste aparecia com 10,6%
quando a base dá 23,0%. A figura foi descartada — participação no total
confunde tamanho do programa com tamanho da população — e substituída por
`F5`.

---

## 5. Regra permanente

1. Figura derivada de base do repositório é gerada por script e lida de
   `output/`. Não se cola imagem produzida fora do pipeline.
2. Figura de fonte externa é preservada em `figuras/`, com a fonte na legenda e
   uma linha na seção 1.
3. Figura conceitual recebe rótulo de ilustração do modelo.
4. Número exibido sem linha na seção 2 é erro, não detalhe editorial.
