# RDD da bolsa — estado, pendências e decisões em aberto

> **Atualização de 18/10/2026, noite:** o autor decidiu D2 e D3(b) — rodar
> tudo, sem esperar o dia 28 — e pediu vários outcomes simultâneos. A rodada
> segue o protocolo congelado
> [`40_protocolo_multioutcome_rdd_bolsa.md`](40_protocolo_multioutcome_rdd_bolsa.md).

> **Data:** 18/10/2026, revisto no fim do dia, depois da rodada de inferência,
> figuras, pipeline e artigos.<br>
> **Para quê:** ponto de retomada do trabalho de 14 a 18/10/2026 sobre o teste
> causal da hipótese da banca 1. Diz o que está feito, onde está, o que falta e
> o que depende de decisão do autor.<br>
> **Entrega seguinte:** apresentação em 28/10/2026.<br>
> **Branch:** `claude/vigilant-mccarthy-dd92mc`, também na `main`.

## 1. Resultado em uma frase

A bolsa do PMM-E é atribuída pelo **IVS 2010 oficial do Ipea**, com cortes em
**0,300 e 0,400** (+R$ 5 mil cada). A RDD sharp nesses cortes **não detecta
efeito** do anúncio de +R$ 5 mil sobre a proporção de células preenchidas na 1ª
chamada do ciclo 1:

| Corte | Bolsa | Salto | IC 95% |
|---|---|---:|---|
| 0,300 | R$ 10 mil → R$ 15 mil | −12,8 p.p. | [−45,5; +19,8] |
| 0,400 | R$ 15 mil → R$ 20 mil | −5,1 p.p. | [−36,5; +26,2] |

- **O sinal está conferido.** Salto = lado com bolsa maior menos lado com bolsa
  menor (`scripts/rdd_bolsa/09b_conferir_sinal.py`).
- **Por que o salto é negativo com a média bruta maior acima do corte.** O
  preenchimento sobe com o IVS dentro da janela. A média de cada lado reflete
  esse gradiente; o salto compara as duas retas no próprio corte.
- **Os ICs são largos.** O efeito mínimo detectável é de cerca de 45 p.p. As
  razões são o outcome ruidoso, 41 a 61 municípios por lado e a extrapolação
  local linear.
- **As 15 especificações exploratórias**
  ([`39`](39_inferencia_alternativa_rdd_bolsa.md)) não mudam a leitura.
  Nenhuma é distinguível de zero. A 5% unilateral, descartam saltos de
  +15 p.p. ou mais no corte de 0,300 (limite superior de 14,5 p.p.), mas
  nenhuma descarta +10 p.p.
- **Controle sintético e DiD não se aplicam.** Não há pré-período do outcome, e
  há centenas de municípios tratados ao mesmo tempo.

**Leitura:** inconclusiva, e não "a bolsa não funciona". Frase para os slides:

> Não encontramos evidência estatística de que +R$ 5 mil aumente o preenchimento
> das vagas perto dos cortes de IVS. A amostra também não permite descartar
> efeitos moderados: o resultado é inconclusivo, não uma prova de ineficácia.

Limites para citar:
- **Pelo IC 95% bicaudal, o do protocolo:** a amostra não descarta efeitos de
  até cerca de +20 p.p. em 0,300 e +26 p.p. em 0,400.
- **Pelo limite unilateral exploratório:** +14,5 e +21,2 p.p.

Nos slides, use um dos dois e diga qual.

## 2. O que está feito

| Etapa | Estado | Onde |
|---|---|---|
| Regra da bolsa reconstruída: o IVS oficial reproduz 368/368 (ciclo 1), 454/454 (ciclo 2) e 747/748 (ciclo 3) | concluído | [`auditorias/16`](../auditorias/16_ivs_2010_oficial_e_arquivo_local.md); `output/rdd_bolsa/portao_r1_ivs_oficial.json` |
| Origem do arquivo errado `data/ivs_ipea_2010_municipios.csv` (última linha de subgrupo com IVS preenchido) | concluído | idem, §3; `scripts/rdd_bolsa/04c_*` |
| Protocolo e adendo congelados antes dos resultados | concluído | `output/rdd_bolsa/protocolo_escore_administrativo.json`; `protocolo_E4_adendo_proporcao.json` |
| E3: RDD sharp completa com diagnósticos | concluído | [`37`](37_resultados_rdd_bolsa_ivs_oficial.md); `output/rdd_bolsa/E3_*` |
| E3: `ivs_2010` fora do teste de balanço (é a própria running variable) e IVS oficial como escore padrão do 07 | concluído | commits `9af03bd` e `0e04d88` |
| Conferência do sinal: quadro de vagas × lado do corte, código, reestimação independente | concluído | `output/rdd_bolsa/E3_conferencia_sinal.json` |
| E5: inferência alternativa, exploratória e pós-resultado (15 especificações, decomposição do IC, limites, outros desenhos) | concluído | [`39`](39_inferencia_alternativa_rdd_bolsa.md); `output/rdd_bolsa/E5_*`; `scripts/rdd_bolsa/11_*` |
| Relatório PDF, 29 páginas | concluído | `output/rdd_bolsa/relatorio_resultados_rdd_bolsa.pdf` |
| Galeria da figura da regra, com a variante A colorida | concluído | `output/rdd_bolsa/galeria_figura_regra.pdf` |
| Pipeline: `run_all.py` com a cadeia nova e a opção `--rdd-bolsa`; scripts antigos fora; A6 depois da RDD | concluído | `run_all.py`; [`scripts/README.md`](../../scripts/README.md) |
| Testes: 04b, 04c, cache do a08, E1, E2, E3, E4, E5, sinal, pipeline | concluído | [`tests/README.md`](../../tests/README.md); suíte com 337 testes, 0 falhas e 3 erros por pacotes ausentes |
| Artigo curto: RDD da bolsa como segunda camada causal; ajuste completo do A4 retirado | concluído | `paper_pmme_curto.tex` (conferidor aprovado) |
| Artigo de submissão: apêndice C com a RDD da bolsa; descarte antigo e ajuste completo retirados | concluído | `paper_pmme_submission.tex` (conferidor aprovado) |
| Síntese do red team (A6) e manifesto: RDD aprovada em R1 e inconclusiva no E3; ressalva do ajuste completo | concluído | [`auditorias/09`](../auditorias/09_red_team_atracao_provimento.md); [`32`](32_sintese_A6_resumo_intro_metodos_conclusao.md); `output/tema_trabalho/A6_manifesto_reproducao.json` |
| Guia de conferência manual | concluído | [`auditorias/17`](../auditorias/17_guia_conferencia_manual_ivs.md) |

O relatório tem:
- **ordem:** a hipótese primeiro e a presença como secundário;
- **"Como ler" antes de cada tabela,** com as médias brutas e as retas no corte;
- **gráficos de RDD tradicionais:** pontos por faixa de IVS, retas locais com
  IC e visão global;
- **diagnósticos:** densidade e balanço;
- **figura da regra:** variante A colorida;
- **seção do E5:** decomposição do IC, forest plot, todas as especificações,
  o que se pode descartar e a caixa "o que podemos e não podemos afirmar".

## 3. Decisões do autor

### D1. Forma da figura "bolsa × IVS" — decidida

Variante A, pontos sobre o degrau, com cor por IVS de verde a vermelho
(vermelho = IVS maior). A escala tem os pontos de cor nos centros das classes do
Ipea (0,15 a 0,55) e satura fora desse intervalo; essa escolha é ajustável. Na
versão do arquivo antigo, os 101 municípios do lado errado do corte têm
contorno preto.

### D2. Preenchimento do ciclo 2 (opcional) — em aberto

Hoje o ciclo 2 só tem o outcome de presença, porque o funil por célula só foi
reconciliado para o ciclo 1.
- **Prós:** daria uma replicação da própria hipótese.
- **Contras:** exige reconstruir o funil do ciclo 2 e congelar a definição
  antes de calcular, e é retrospectivo. Pelo E5, juntar os ciclos 1 e 2 levaria
  o efeito mínimo detectável a cerca de 31 p.p., no cenário otimista. Não muda
  a conclusão.
- **Recomendação:** não fazer antes do dia 28.

### D3. Análises antigas afetadas pelo arquivo errado — (a) e (b) aplicadas

- **O que vinha do arquivo errado:**
  - o gradiente de IVS do A4;
  - `log_pop` e `estoque_pre_por_10k`, incluindo o contraste do "ajuste
    completo" do A4 (o valor antigo só consta como failure mode na
    [auditoria 19](../auditorias/19_reestimacao_base_oficial_failure_mode.md));
  - as especificações completas de A5 e a Tabela 1 do ciclo 1.
- **(a) Aplicada:** os dois artigos deixaram de citar o ajuste completo antigo.
- **(b) Aplicada em 18/10/2026** (tarefa E do protocolo
  [`40`](40_protocolo_multioutcome_rdd_bolsa.md)): malha, tipologia A2, A4, A5 e a
  Tabela 1 do ciclo 1 reestimadas com a base oficial do Ipea (a08) e o Censo
  2022, mesma especificação e mesmas amostras; emenda datada no registro A3. Os
  artigos e a síntese do A6 citam o ajuste completo corrigido, conferido contra
  `output/`. Antes e depois, conclusões que mudam e onde os números antigos
  ainda aparecem: [auditoria 19](../auditorias/19_reestimacao_base_oficial_failure_mode.md).
  Também corrigidos no mesmo dia: o C3-03 do ciclo 3 (diagnósticos pré-T0 com
  covariadas oficiais, por emenda datada, sem ler mês pós-T0), o cenário
  "informado" de E2 e E4 (retirado das saídas ativas), a categoria de IVS das
  figuras da banca 1 e o diagnóstico `tema_trabalho/01`.

## 4. O que falta

1. **Conteúdo canônico da apresentação** de 28/10 em `docs/07_apresentacoes/`,
   como exige o `CLAUDE.md`, a partir do relatório e da figura escolhida. O
   deck é derivado desse conteúdo.
2. **Ambiente:** os três testes antigos que exigem `scipy`, `statsmodels` e
   `matplotlib` (do `requirements.txt`) dão erro de importação nesta sessão. O
   `run_all.py` também aborta por design com numpy 2.5.3, quando o
   `requirements.txt` fixa 2.5.2.
3. **Robustez menor:** o teste binomial exato do E1 estoura acima de cerca de
   1.030 municípios. Os dados reais têm no máximo 454, então nenhum resultado é
   afetado. O script não foi alterado porque o E4 grava o hash dele.

## 5. Depois do dia 28

- D2, se decidido. D3(b) foi aplicada em 18/10/2026.
- Diferença em descontinuidades com a oferta no CNES, o único desenho
  alternativo candidato ([`39`](39_inferencia_alternativa_rdd_bolsa.md), §5).
  Muda o outcome e exige protocolo próprio congelado antes de olhar os dados.
- O ciclo 3 continua congelado até a maturidade dos dados.
