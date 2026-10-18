# RDD da bolsa — estado, pendências e decisões em aberto

> **Data:** 18/10/2026.<br>
> **Para quê:** ponto de retomada do trabalho de 14 a 18/10/2026 sobre o teste
> causal da hipótese da banca 1. Diz o que está feito, onde está, o que falta e
> o que depende de decisão do autor.<br>
> **Entrega seguinte:** apresentação em 28/10/2026.<br>
> **Branch:** `claude/vigilant-mccarthy-dd92mc`.

## 1. Resultado em uma frase

A bolsa do PMM-E é atribuída pelo **IVS 2010 oficial do Ipea**, com cortes em
**0,300 e 0,400** (+R$ 5 mil cada). A RDD sharp nesses cortes **não detecta
efeito** do anúncio de +R$ 5 mil sobre a proporção de células preenchidas na 1ª
chamada do ciclo 1:

| Corte | Salto | IC 95% |
|---|---:|---|
| 0,300 | −12,8 p.p. | [−45,5; +19,8] |
| 0,400 | −5,1 p.p. | [−36,5; +26,2] |

Os intervalos são largos (efeito mínimo detectável de cerca de 45 p.p.). A
leitura é **inconclusiva**, e não "a bolsa não funciona".

## 2. O que está feito

| Etapa | Estado | Onde |
|---|---|---|
| Regra da bolsa reconstruída: IVS oficial reproduz 368/368 (ciclo 1), 454/454 (ciclo 2), 747/748 (ciclo 3) | concluído | [`auditorias/16`](../auditorias/16_ivs_2010_oficial_e_arquivo_local.md); `output/rdd_bolsa/portao_r1_ivs_oficial.json` |
| Escore administrativo do MS = IVS 2010 oficial (404/404 valores; 5.565/5.565 categorias) | concluído | idem; `scripts/aquisicao/a07_*`, `a08_*`, `scripts/rdd_bolsa/04b_*` |
| Origem do arquivo errado `data/ivs_ipea_2010_municipios.csv`: última linha de subgrupo com IVS preenchido, reproduzida em 5.565/5.565 nas 7 colunas | concluído | [`auditorias/16`](../auditorias/16_ivs_2010_oficial_e_arquivo_local.md), §3; `scripts/rdd_bolsa/04c_*` |
| Protocolo e adendo congelados antes dos resultados | concluído | `output/rdd_bolsa/protocolo_escore_administrativo.json` (commit `be11852`); `protocolo_E4_adendo_proporcao.json` (`2996bf0`) |
| E3: RDD sharp completa, com diagnósticos (densidade sem salto; desequilíbrio de covariáveis no corte 0,400 do ciclo 1) | concluído | [`37`](37_resultados_rdd_bolsa_ivs_oficial.md); `output/rdd_bolsa/E3_*` |
| Proporção preenchida reconstruída dos brutos: 393/1.295 e 461/1.295, igual ao A4 célula a célula | concluído | `scripts/rdd_bolsa/08a_*`; `output/rdd_bolsa/E4_validacao_reconstrucao.json` |
| E1, E2 e E4 (exploratórios com escore parcial, superados pelo E3) | concluído | `output/rdd_bolsa/E1_*`, `E2_*`, `E4_*` |
| Relatório PDF (hipótese primeiro; presença como secundário; sem janelas de sensibilidade) | concluído | `output/rdd_bolsa/relatorio_resultados_rdd_bolsa.pdf` (`scripts/rdd_bolsa/09_*`) |
| Galeria com quatro formas da figura "bolsa × IVS" | concluído | `output/rdd_bolsa/galeria_figura_regra.pdf` (`scripts/rdd_bolsa/10_*`) |
| Guia de conferência manual | concluído | [`auditorias/17`](../auditorias/17_guia_conferencia_manual_ivs.md) |
| Correções em documentos antigos: "IVS é piso" (errata E10 da banca 1), pedido de dados cancelado, `CLAUDE.md`, README, status | concluído | [`00_registro_mudancas.md`](../00_registro_mudancas.md), entradas de 14/10/2026 |

## 3. Decisões em aberto, do autor

### D1. Forma da figura "bolsa × IVS"

Esta figura vai para a apresentação. As opções estão em
`output/rdd_bolsa/galeria_figura_regra.pdf`, cada uma com o IVS oficial e com o
arquivo antigo:

| Opção | O que mostra | A favor | Contra |
|---|---|---|---|
| A — pontos sobre o degrau | cada município no valor exato da bolsa | mais simples | onde há muitos pontos, viram uma faixa contínua e não dá para contar |
| **B — pontos empilhados** (recomendada; provisória no relatório) | cada município é um ponto; a pilha mostra quantos há em cada intervalo de 0,005 | mostra o município e a contagem; sem aleatoriedade | um pouco mais carregada |
| C — histograma por faixa | barras de 0,01 por valor de bolsa | leitura estatística familiar | perde o "um ponto = um município" |
| D — código de barras | um traço por município, uma fileira por faixa | a mais limpa; mostra o corte com nitidez | não mostra contagem |

Depois da escolha, aplica-se a escala de cor verde → amarelo → vermelho conforme
o IVS aumenta.

### D2. Preenchimento do ciclo 2 (opcional)

Hoje o ciclo 2 só tem o outcome de presença, porque o funil por célula só foi
reconciliado para o ciclo 1.
- **Prós:** daria uma replicação da própria hipótese, com 454 municípios.
- **Contras:** exige reconstruir o funil do ciclo 2 e congelar a definição antes
  de calcular. Leva cerca de meio dia e é retrospectivo.
- **Recomendação:** só se a banca pedir replicação. Para o dia 28, mostrar só o
  ciclo 1.

### D3. Análises antigas afetadas pelo arquivo errado

Estes números do projeto vêm do arquivo errado e não foram refeitos:
- o gradiente de IVS do A4;
- os controles `log_pop` e `estoque_pre_por_10k`, incluindo os 20,9 p.p. do
  "ajuste completo" do A4.

A RDD não é afetada, e os resultados por estrato do A4 também não. A lista está
na [`auditoria 16`](../auditorias/16_ivs_2010_oficial_e_arquivo_local.md), §4.
- **Opções:** (a) registrar como pendência e não usar esses números na
  apresentação; (b) reestimar com a base oficial.
- **Recomendação:** (a) agora; (b) depois do dia 28.

## 4. Próximos passos autorizados (18/10/2026)

1. **Pipeline:** pôr no `run_all.py` os scripts `a07`, `a08`, `04`, `04b`,
   `04c`, `05`, `06`, `07 --escore`, `08a`, `08`, `09` e `10`. Tirar de lá os
   scripts antigos da RDD que leem o arquivo errado (`01_*`, `01b_*`, `02_*`,
   `03_*`), que hoje regerariam saídas superadas.
2. **Artigo curto:** atualizar `paper_pmme_curto.tex`, que ainda diz "nenhum
   efeito da bolsa foi estimado", com a regra, o arquivo errado e o E3.
3. **Testes:** cobrir 04b, 04c, E1, E2 e E4 com testes automatizados.

## 5. Depois do dia 28

- D2 e D3(b), se decididos.
- Conteúdo canônico da apresentação em `docs/07_apresentacoes/`, como exige o
  `CLAUDE.md`, a partir do relatório e da figura escolhida.
- Ambiente: os testes antigos de A5 e C3 precisam de `scipy`, `statsmodels` e
  `matplotlib` (em `requirements.txt`), que não estavam instalados na sessão.
