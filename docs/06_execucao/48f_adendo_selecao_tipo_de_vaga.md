# 48f. Adendo: seleção pelo tipo de vaga na H1 (tipo como outcome, balanço e limites de Lee)

> **Data de congelamento:** 26/10/2026, antes de rodar as contas deste adendo.<br>
> **Decisão do autor (26/10/2026):** aprovou a recomendação 5 da §2.16 de
> [`../07_apresentacoes/banca2/05_discussao_historia_empirica.md`](../07_apresentacoes/banca2/05_discussao_historia_empirica.md);
> a pergunta de origem está na §2.12 do mesmo doc ("o que transforma as vagas
> em cadastro reserva, imediata etc. não pode estar influenciando a H1?").<br>
> **Estatuto:** `ADENDO_48F_POS_RESULTADO`. A H1 só com vagas imediatas (48b,
> doc 57n) e o salto descritivo da parte de células só de reserva (doc 57l)
> já foram vistos. Toda saída leva `natureza_dos_dados = EMPIRICO`.

## 1. O problema

A SGTES decide qual município recebe vaga imediata e qual fica no cadastro
reserva, com critério que não está nos dados. O adendo 48b compara só células
com vaga imediata. Se o tipo de vaga responde ao corte, essa amostra é
**selecionada** pelo próprio tratamento: os municípios com vaga imediata acima e
abaixo do corte podem não ser comparáveis. Este adendo mede o tamanho dessa
seleção e dá um intervalo para o salto da H1 que **não depende** de como o
Ministério escolheu o tipo.

## 2. Unidade, amostra e definições

- **Running variable:** IVS 2010 oficial (a08). O arquivo de IVS errado não é
  lido.
- **Tipo de vaga:** do quadro da 1ª chamada; no ciclo 2, do quadro de
  **13/02/2026** (48b, §7), anterior à alocação.
- **Unidade principal:** município × ciclo, entre os municípios com pelo menos
  uma célula no quadro do ciclo (qualquer tipo), ciclos 1–3.
- **Seleção (S):** S = 1 se o município × ciclo tem ≥ 1 célula com vaga
  imediata (célula só imediata ou mista).
- **Outcomes, observados só quando S = 1** (versões municipais da H1 do 48b,
  as mesmas do pareamento do 48d):
  - **Y1:** fração das células com vaga imediata que foram preenchidas na 1ª
    chamada (definição de "preenchida" do A3, por ciclo);
  - **Y2:** médicos alocados na 1ª chamada em células com vaga imediata, por
    vaga imediata.

## 3. Linhas

| Id | Linha | Papel |
|---|---|---|
| **SV-1** | **tamanho da seleção:** RDD de S no corte (município × ciclo), por corte; e RDD de "célula tem vaga imediata" (unidade célula, efeitos fixos de curso × ciclo) | **principal** (diagnóstico central) |
| SV-2 | **balanço dentro da amostra selecionada:** salto, no corte, das covariáveis L e M do 48d (capital, macrorregião, log da população, médicos e especialistas por 10 mil no município e no resto da região de saúde), só entre S = 1, comparado com o mesmo salto em toda a amostra | secundária |
| **SV-3** | **limites de Lee** para o salto de Y1 e de Y2, por corte | **principal** |
| SV-4 | SV-3 na janela 0,020 | sensibilidade |
| SV-5 | SV-3 com a reta (versão local linear: aparar dentro de cada lado depois de tirar a reta de Y em IVS por ciclo, e estimar o salto com os resíduos aparados) | sensibilidade |

**Especificação comum da RDD (SV-1, SV-2):** local linear, kernel triangular,
h = 0,050, cada corte separado, ciclos empilhados com intercepto e inclinações
por ciclo, CR1 por município.

**Limites de Lee (SV-3), versão de randomização local:**
1. Na janela |IVS − corte| ≤ 0,050, com os pesos do kernel triangular,
   calcula-se a taxa de seleção de cada lado, p_acima e p_abaixo (média
   ponderada de S, com efeito de ciclo: a taxa é calculada dentro de cada ciclo
   e os limites combinados com o peso de cada ciclo no número de unidades com
   S = 1).
2. No lado com taxa maior, apara-se a fração q = (p_maior − p_menor) / p_maior
   das unidades com S = 1 (quantis ponderados). O salto é sempre acima −
   abaixo. Se o lado aparado é o de **cima**: no limite inferior saem as de
   **maior** Y; no superior, as de **menor** Y. Se o lado aparado é o de
   **baixo**: no limite inferior saem as de **menor** Y; no superior, as de
   **maior** Y.
3. O limite inferior e o superior do salto são as diferenças de médias
   ponderadas (acima − abaixo) com o lado aparado de cada jeito.
4. IC de 95% para o conjunto identificado por Imbens e Manski (2004), com erros
   por *bootstrap* em blocos de município (1.999 reamostras, semente 20261026),
   refazendo a aparagem em cada reamostra.

**Premissa (monotonicidade):** o corte muda a chance de ter vaga imediata numa
só direção para todos os municípios. É a premissa de Lee (2009). Ela não é
testável; é relatada.

## 4. Leitura pré-registrada

| Resultado | Leitura |
|---|---|
| SV-1 com IC que contém zero e taxas de seleção parecidas (q < 0,05) | a seleção pelo tipo de vaga é pequena no corte; o 48b não é muito afetado por ela |
| SV-1 com IC que exclui zero | o tipo de vaga responde ao corte (ou a algo que muda nele): a amostra do 48b é selecionada; dar peso aos limites de SV-3 |
| SV-3 com os dois limites e seus IC contendo zero | mesmo sem supor nada sobre como o Ministério escolheu o tipo (além da monotonicidade), não se detecta diferença de preenchimento no corte |
| SV-3 com o intervalo identificado inteiro de um lado do zero | relatar o sinal como robusto à seleção pelo tipo de vaga, com o pacote do corte |
| SV-2 mostra desbalanço maior entre S = 1 do que na amostra toda | a restrição a vagas imediatas piora a comparabilidade; relatar |

## 5. Saídas

| Item | Onde |
|---|---|
| script | `scripts/rdd_bolsa/46_selecao_tipo_vaga.py` (importa os construtores do 40 e do 44) |
| estimativas | `output/rdd_bolsa/SV_estimativas.csv`, `SV_balanco.csv`, `SV_resumo.json`, `SV_figuras/` |
| resultados | `docs/06_execucao/57t_resultados_selecao_tipo_vaga.md` (blocos gerados pelo script) |
| testes | `tests/test_selecao_tipo_vaga.py` |

**Portão:** antes de qualquer conta nova, o script reproduz HI-1 e HI-2 do 48b
nos dois cortes (≤ 1e−8) e a parte de células só de reserva acima e abaixo do
corte do doc 57l (D-b), se a definição coincidir; se não coincidir, relata a
diferença de definição.

## 6. Integridade

- Nada imputado; Y de unidade com S = 0 fica ausente, nunca zero.
- Nada adquirido; nada escrito em `data/`.
- Nenhuma competência do CNES ≥ 2026-09.
- `HI_*`, `CL_*` e `DQ_*` não são regravados.
