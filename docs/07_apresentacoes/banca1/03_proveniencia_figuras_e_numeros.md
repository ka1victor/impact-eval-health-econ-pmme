# Proveniência de figuras e números — banca 1

> **Regra aplicada:** todo número exibido declara fonte, data de referência, cobertura, unidade e reprodutibilidade<br>
> **Conteúdo dos slides:** [02_conteudo_slides.md](02_conteudo_slides.md)<br>
> **Atualização:** 9 de setembro de 2026

---

## 1. Figuras

| Código | Figura | Slide | Arquivo | Origem |
|---|---|:---:|---|---|
| `F1` | Especialistas por 100 mil habitantes em jun/2025, por faixa | 3 | `output/apresentacao_banca1/oferta_pre_por_faixa.png` | CNES + Censo 2022, gerada por script |
| `F2` | Colegas da mesma especialidade no município, jun/2025, por faixa | 3 | `output/apresentacao_banca1/retaguarda_por_faixa.png` | CNES, gerada por script |
| `F3` | Bolsa mensal por faixa de atração | 4 | `output/apresentacao_banca1/bolsa_por_faixa.png` | Edital SGTES/MS nº 3/2025, gerada por script |
| `F4` | Custo laboral líquido em função do volume de atendimentos | 9 | `docs/02_teoria/figuras/curva_custo_laboral_burnout.png` | ilustração conceitual do modelo |

Produzidas por
[`scripts/apresentacao/gerar_figuras_banca1.py`](../../../scripts/apresentacao/gerar_figuras_banca1.py),
que grava `output/apresentacao_banca1/manifesto_figuras.json` com o hash das
entradas, o filtro aplicado e a série completa por faixa.

**Definição comum de `F1` e `F2`.** Profissionais distintos com vínculo no CNES
nos CBOs dos **10 cursos com correspondência unívoca curso–CBO** (1, 2, 3, 5, 9,
12, 13, 14, 15 e 16), somados por município — a restrição evita contar a mesma
pessoa em dois cursos. Universo: **295 municípios** com vaga nesses cursos no
ciclo 1. Em `F1`, denominador é a população residente do Censo 2022. É presença
cadastral, não participação no programa.

### Figuras geradas e não usadas

| Arquivo | Situação |
|---|---|
| `output/apresentacao_banca1/oferta_antes_depois_por_faixa.png` | série mensal de especialistas por 100 mil habitantes, 2024–2026. Saiu do deck na segunda rodada de revisão: sem grupo de comparação, não se lê como efeito do programa. O script continua gerando; pode servir ao artigo |
| `docs/07_apresentacoes/banca1/figuras/especialistas_por_uf.png` | Demografia Médica 2025, 16 UFs. Substituída por `F1`, que mede o mesmo fenômeno na unidade da política |
| `docs/07_apresentacoes/banca1/figuras/deslocamento_por_regiao.png` | REGIC 2018. Retirada: mede custo do paciente, e reduzir deslocamento não é objetivo declarado do edital |
| `docs/07_apresentacoes/banca1/figuras/motivacao_manchetes.png` | recortes de imprensa. Retirada na segunda rodada, quando o slide 3 passou a tratar da perspectiva do médico |

---

## 2. Números exibidos

### Slide 3 — o problema

| Número | Fonte |
|---|---|
| 16,0 e 7,3 especialistas por 100 mil hab. (Faixa 3 e Faixa 1), jun/2025 | `F1` |
| Mediana de 2 colegas na Faixa 1 contra 5 na Faixa 3; 42% sozinho ou com um único colega | `F2`. Faixa 1 tem 19 pares município–especialidade: a proporção é frágil, a mediana é robusta |

### Slide 4 — a política

| Número | Fonte |
|---|---|
| 16 indicadores, 3 dimensões do IVS 2010 | Ipea, *Atlas da Vulnerabilidade Social nos Municípios Brasileiros* (2015) |
| Cortes 0,200 / 0,300 / 0,400 / 0,500 | mesma fonte; reproduzidos em `docs/auditorias/01_regra_institucional.md`, §6.3 |
| R$ 20.000 / R$ 15.000 / R$ 10.000; 20 h semanais; até 12 meses | Edital SGTES/MS nº 3/2025 e retificação; mesma auditoria, §6.1 |
| 177 dos 368 municípios com faixa publicada diferente da recalculada | portão R1, `docs/05_identificacao/16_sintese_achados_e_novo_plano_causal.md`, §3.5 |
| Grade mudou em 2026: *alta* passou à Faixa 1 | Chamamento SGTES/MS nº 1/2026; auditoria §6.4 |

### Slide 5 — a evidência

Todos os números foram conferidos na fonte primária em 09/09/2026. O
catálogo completo, com mais estudos, está em
[`docs/03_literatura_empirica/19_...md`](../../03_literatura_empirica/19_literatura_empirica_escolha_locacional_medicos.md),
seção 7.

| Número | Fonte | Verificação |
|---|---|---|
| Salário +33% eleva aceitação em 15,1 p.p.; postos a >200 km vão de ~25% a ~80%; anula o desconto de IDH | Dal Bó, Finan & Rossi (2013), *QJE* 128(3) | RCT com salário sorteado entre 106 postos |
| 65% não mudariam por nenhum pacote; prêmio exigido de 37% a 130% da renda anual | Scott et al. (2013), *Soc Sci Med* 96 | escolha discreta, 3.727 clínicos |
| Elasticidade-salário ~0,4 nas metrópoles e ~0,7 no interior | Costa, Nunes & Sanches (2024), *REStat* 106(1) | **conferido no PDF**: "physicians' supply function is inelastic, with mean and median wage elasticity ranging around 0.4 and 0.7 in metropolitan areas and the countryside, respectively" |
| +50% no salário público corrige 12,4% do desequilíbrio a US$ 15,7 mi/p.p.; cotas corrigem 63,8% a US$ 2,2–5,1 mi/p.p. | idem | **conferido na Tabela 6 do PDF**: 12,40 e 15.727 para a coluna *Wage x1.5 (N/NE CS)*; 63,76 e [2.169; 5.066] para cotas |
| 12% contra 39% de permanência após oito anos | Pathman, Konrad & Ricketts (1992), *JAMA* 268(12) | coorte de 9 anos, 412 médicos |
| Prêmio compensatório da ordem de 35% a 65% da renda | síntese de Scott et al. (2013), Miranda et al. (2012) e Costa et al. (2024) | é síntese do projeto, não número de um paper. Deve ser apresentada como tal |
| 30,3% das 1.295 células com confirmação; 31,6% / 37,4% / 23,6% por faixa | quadro de vagas do ciclo 1, chamada 1 | `output/tema_trabalho/A4_relatorio_diagnostico.md`, linha 12; n = 291 / 465 / 539 |

### Slide 11 — viabilidade

| Número | Fonte |
|---|---|
| 1.295 células estabelecimento–curso, 368 municípios | quadro de vagas do ciclo 1, chamada 1 |
| CNES mensal, jun/2024 a jul/2026 | `output/avaliacao_impacto/dados/painel_municipio_curso_mes.parquet` |

---

## 3. Pendências e ressalvas

### `P1` — Reinhardt: a equação é de 1972, não de 1975

O projeto cita Reinhardt (1975), *Physician Productivity and the Demand for
Health Manpower*, caps. 3 e 4, e o livro não tem sua especificação transcrita no
repositório. A equação exibida no slide 7,
$Q = f(H, X_1, X_2, \ldots, X_n)$, é a forma geral do artigo
**Reinhardt (1972), *Review of Economics and Statistics* 54(1), 55–66**, onde
$Q$ é a taxa de produto do consultório, $H$ o insumo de tempo do médico e o
vetor $X$ os demais insumos, entre eles pessoal auxiliar e capital. A citação do
slide deve dizer 1972. Se a banca pedir a especificação estimada, é preciso
recuperá-la do artigo ou do livro.

### `P2` — a régua de 35% a 65% é síntese, não citação

Nenhum artigo publica esse intervalo. Ele resume Scott et al. (2013), que
estima 37% a 130% na Austrália, e Miranda et al. (2012), que simula +50% e +75%
no Peru. Apresentar como síntese do projeto.

### `P3` — comparabilidade do prêmio com a bolsa

Os prêmios compensatórios da literatura são sobre a **renda total** do médico. A
bolsa do PMM-E remunera **20 horas semanais**. Traduzir R$ 5 mil em "+50%" e
comparar com a régua australiana pressupõe que a bolsa seja a fração dominante
do rendimento — hipótese sobre composição de vínculos, não dado. O slide 5
declara essa ressalva.

### `P4` — `populacao_2010` não é população residente

A coluna do arquivo do IVS soma 41.852.890 contra 190.755.799 do Censo 2010, com
razão variando de 0,10 a 0,42 entre municípios. Não é usada como denominador
aqui; o denominador é o Censo 2022, adquirido por
[`scripts/aquisicao/06_adquirir_populacao_censo2022.py`](../../../scripts/aquisicao/06_adquirir_populacao_censo2022.py).
Registro completo em
[`docs/04_dados/02_inventario_dados_por_outcome.md`](../../04_dados/02_inventario_dados_por_outcome.md),
seção 4.0.

---

## 4. Regra permanente

1. Figura derivada de base do repositório é gerada por script e lida de
   `output/`.
2. Figura de fonte externa é preservada em `figuras/`, com a fonte na legenda e
   uma linha na seção 1.
3. Figura conceitual recebe rótulo de ilustração do modelo.
4. Número exibido sem linha na seção 2 é erro, não detalhe editorial.
