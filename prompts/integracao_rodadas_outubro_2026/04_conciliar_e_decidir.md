# S6 — Conciliar o PR 4 com a rodada de 14/10 e levar as decisões ao autor

> **Para quem é:** o agente que assumir o PR
> [ka1victor/impact-eval-health-econ-pmme#4](https://github.com/ka1victor/impact-eval-health-econ-pmme/pull/4)
> (branch `claude/gallant-carson-11uzic`). A sessão que abriu o PR foi encerrada
> em 14/10/2026; tudo o que ela sabia e não virou commit está aqui.<br>
> **Não autoriza:** merge na `main` sem o autor; escolher entre protocolos ou
> resultados depois de vê-los; reestimar A4/A5/A8 sem emenda commitada; alterar
> `data/`; descongelar o ciclo 3. O [`CLAUDE.md`](../../CLAUDE.md) vale sobre
> tudo o que está aqui.

## 1. Estado de partida

| Branch | Conteúdo | Situação |
|---|---|---|
| `claude/gallant-carson-11uzic` (PR 4) | rodadas de 01/10 e 05/10 integradas, `main` até `40a8c98`, revisões S1a e S1b, correções sem decisão do autor | 214 testes verdes, conferidores aprovando; nenhum outcome do RDD aberto |
| `claude/vigilant-mccarthy-dd92mc` | rodada de 14/10, feita por outra sessão a partir da `main`, sem conhecer o 05/10 | **ainda não integrada**; pode ter recebido commits depois desta nota (`git log 2996bf0..origin/claude/vigilant-mccarthy-dd92mc`) |

Sessões da [ordem original](README.md): S1a, S1b e S2 feitas; S3 só a seção B;
S4 e S5 não executadas. Esta S6 vem antes de S3 (seção A) e de S4.

## 2. Fatos verificados que mudam o plano

Confira cada um antes de agir; os comandos são curtos.

1. **O IVS administrativo é o IVS 2010 oficial do Ipea.** O IVS do quadro do
   PMMB 2026 (05/10, `output/rdd_bolsa/matriz_municipio_ivs_administrativo.csv`,
   coluna `ivs_adm`) é igual, até a 3ª casa, ao `ivs` da base completa da
   Plataforma IVS (`output/aquisicao/a08_ivs_2010_oficial_municipio.csv`, commit
   `92c2ba4` do branch de 14/10) em **5.565 de 5.565** municípios. O `ivs` da
   Relação Nominal do MS (`7156c78`) também é igual nos 404 em que existe.
2. **O arquivo local `data/ivs_ipea_2010_municipios.csv` não é o IVS municipal.**
   Coincide com o oficial em só 38 municípios; segundo `d2fabe7`, é a linha de
   subgrupo "mulheres negras, área urbana" da mesma base (5.554 municípios iguais
   nesse recorte). Ele alimenta, entre outros, `scripts/aquisicao/04_harmonizar_territorio_ibge.py`,
   os R1 públicos (`00_`, `01_`, `01b_`), o `01c` e o `a07` (só para comparação),
   e o red team `07_`. Liste tudo com `grep -rln ivs_ipea_2010_municipios scripts`.
3. **Consequências diretas no PR 4.** Ficam errados ou precisam de outra leitura:
   - a decisão 0 do rascunho
     [`18`](../../docs/05_identificacao/18_protocolo_r3_rdd_bolsa_rascunho.md)
     ("trocar o IVS 2010 pelo IVS administrativo"): não há troca, a running
     variable é o IVS 2010 canônico, lido da fonte certa;
   - as frases "o IVS administrativo não é o IVS 2010", "outra safra", "o IVS 2010
     erra 27%/48%" e o "R1 público reprovado" (auditoria 15, docs 14, 16, 17 e 18,
     README, TODO, roadmap, controlador, `test_ivs_administrativo_nao_e_o_ivs_2010`):
     o que reprovou foi o **arquivo local**, não o IVS 2010;
   - as covariadas do R2 `ivs_2010`, `ivs_infra_2010`, `ivs_ch_2010`,
     `ivs_rt_2010`, `idhm_2010` e `log_rdpc_2010` vêm da tipologia, que depende do
     arquivo local; o balanço do R2 precisa ser refeito com as covariadas
     oficiais (sem outcome). O achado de `capital` em 0,300 independe disso.
   - continuam válidos: o R1 sharp (a regra é a mesma, só a origem do escore
     ficou documentada), a correção do MDE conjunto e o controlador endurecido.
4. **A RDD já foi estimada no branch de 14/10.** O protocolo `be11852`
   (`output/rdd_bolsa/protocolo_escore_administrativo.json`, congelado às 13:53)
   pré-especificou o E3 antes de qualquer contagem por ciclo; o E3 rodou em
   `92918e3` (14:31) no IVS oficial, ciclos 1 e 2: **nenhum salto distinguível de
   zero**, IC de cerca de ±40 p.p., densidade sem salto e desequilíbrio no corte
   0,400 do ciclo 1 (capital humano e estrato). Antes do E3 rodaram E1/E2
   (outcome `D_k` só nos municípios com escore) e depois o E4 (proporção
   preenchida, limites). Resultados em `docs/06_execucao/37_resultados_rdd_bolsa_ivs_oficial.md`
   daquele branch.
5. **Por isso o rascunho 18 deixou de ser pré-análise** para os desfechos que
   se sobrepõem ao E3/E4 (preenchimento e presença perto dos cortes). Qualquer
   registro R3 posterior tem de declarar esse conhecimento prévio; para desfechos
   não tocados (procura, alocação por célula, homologação) ele ainda pode ser
   registrado antes de abrir, mas não é mais "cego" quanto ao resultado vizinho.

## 3. Conciliação técnica (sem decisão do autor)

Num worktree, a partir de `claude/gallant-carson-11uzic`:
`git merge --no-ff origin/claude/vigilant-mccarthy-dd92mc`. Conflitos esperados:

| Arquivo | Resolução |
|---|---|
| `scripts/aquisicao/a07_adquirir_ivs_administrativo.py` e `output/aquisicao/a07_manifesto_ivs_administrativo.json` (add/add) | mantenha o `a07` de 05/10 (quadro do PMMB) e renomeie o de 14/10 (relação nominal) para um número livre, ex. `a09_adquirir_ivs_relacao_nominal.py` e manifesto correspondente, ajustando os caminhos que ele grava e quem os lê; atenção: o 14/10 já usa `a08` para o IVS oficial |
| `docs/auditorias/15_*` e `scripts/rdd_bolsa/04_*` (numeração duplicada, sem conflito textual) | renomeie os de 14/10 para o próximo número livre e corrija os links; entrada no registro de mudanças |
| `docs/00_registro_mudancas.md` | todas as entradas, por data |
| `docs/06_execucao/33_status_execucao_plano_causal.md` | é gerado: resolva regerando pelo controlador depois do merge |
| `CLAUDE.md`, `AGENTS.md` | o 14/10 já editou (IVS 2010 oficial como canônico, arquivo local proibido). Mantenha o texto de 14/10 por ora e leve ao autor a decisão D1 abaixo; não aplique a redação do adendo 03 (A6), que está superada |
| `README.md`, `TODO.md`, docs 14–18, roadmap | os dois lados mudaram; alinhe aos fatos da seção 2 |

Depois do merge:

- `tests/test_r1_r2_ivs_administrativo.py` proíbe que scripts de R1/R2 leiam
  arquivos com a marca `nominal`; o R1 de 14/10 lê a relação nominal. Separe:
  o R1 de 14/10 é **validação da fonte**, não R1 vigente; ajuste o teste para
  cobrir os scripts certos, sem afrouxar a proibição nos scripts de R2.
- `test_ivs_administrativo_nao_e_o_ivs_2010` passa a testar o contrário contra a
  base oficial (igualdade 5.565/5.565) e a diferença contra o arquivo local.
- O controlador não reconhece `E1_*`–`E4_*` como resultado R4. Não mude isso
  antes da decisão D2.
- Rode a suíte e os conferidores `10_` e `11_` no ambiente fixado
  (`uv venv --python 3.12 .venv && VIRTUAL_ENV=.venv uv pip install -r requirements.txt`).
  **Não rode `run_all.py`.**

## 4. Decisões do autor

Pergunte tudo de uma vez, com a recomendação marcada. Sem resposta, pare e
deixe as perguntas no PR; não há decisão por padrão.

### Bloco D — RDD da bolsa (novas, por causa da seção 2)

| # | Decisão | Recomendação |
|---|---|---|
| D1 | Running variable: confirmar o **IVS 2010 oficial** (base completa do Ipea, `a08`) como canônico, com o arquivo local proibido como running variable e covariada | confirmar; é o que o `CLAUDE.md` já pedia, agora com a fonte certa |
| D2 | Qual resultado é o principal: (a) o E3 de 14/10, pré-especificado em `be11852`; (b) um R3 novo pelo rascunho 18, declarando o E3 como conhecimento prévio; (c) os dois, com papéis fixados agora | (a) para presença e preenchimento, com o R3 do doc 18 restrito a desfechos ainda fechados (procura, alocação por célula) e declarado como posterior ao E3. Decidir **sem** reabrir as estimativas |
| D3 | Status de E1, E2 e E4 | exploratórios, rotulados; E1/E2 condicionam na cobertura e perderam a razão de ser com o escore completo |
| D4 | Refazer o R2 (balanço) com as covariadas oficiais e na população escolhida, sem outcome | sim, antes de qualquer novo registro |
| D5 | Impacto do arquivo local fora do RDD: A2 (tipologia), A3–A5, A8, artigos e banca usam `ivs_2010` ou derivados? | auditoria de impacto primeiro (só leitura, lista de artefatos e cifras afetadas); qualquer regravação só com emenda commitada antes, como manda o 02 de 01/10 |
| D6 | Pedido de dados ao MS (`ce7c551` e `93b8b1e`) | cancelado: o campo é público; não enviar |
| D7 | Linguagem do resultado do E3 | "não detectado, com IC de ±40 p.p."; nunca "sem efeito" |

### Bloco R3 — rascunho 18 (o que sobra depois de D2)

As decisões 1 a 12 da seção 2 do
[rascunho 18](../../docs/05_identificacao/18_protocolo_r3_rdd_bolsa_rascunho.md),
com a nota da revisão S1b no topo dele. A decisão 0 é substituída pela D1. As
que mais pesam: `capital` em 0,300 no principal; população sem o ciclo 3
(MDE conjunto de 28,2 p.p. na banda 0,050); o que fazer com os entregáveis do
plano 14, §4, que o R2 não produziu
([nota no prompt 01](../avaliacao_rdd_bolsa/01_portao_regra_e_suporte.md)).

### Bloco S3 — pendências da rodada de 01/10

As sete decisões da seção A de
[`../fechamento_sessao_remota/02_resolver_pendencias.md`](../fechamento_sessao_remota/02_resolver_pendencias.md),
lidas com o [adendo 03](03_adendo_pendencias_fechamento.md), exceto onde a
seção 2 acima o supera:

| # | Decisão | Recomendação |
|---|---|---|
| A1 | A5/A6 sob o ambiente fixado: regravar ou errata | depende de D5: se o arquivo local afetar A5, a regravação vira parte daquela emenda; se regravar, rodar o `06c` no mesmo ato (hash da `A5_tabela_13` está num teste) |
| A2 | relatórios que o `run_all.py` grava em `docs/` passam a `output/`, com teste que falha se `docs/` mudar | sim |
| A3 | `run_all.py` sem os microdados do CNES: manter o aborto ou modo "artefatos congelados" | modo congelado, com hash conferido |
| A4 | hashes vencidos do quadro de vagas em `portao_regra_ivs.json` e `diagnostico_viabilidade_salario_ivs.json` | regenerar pelos scripts de origem, junto com a correção da fonte do IVS (D5) |
| A5 | estado de D-3 e RDD-IVS em todas as fontes | RDD com R1 sharp no IVS 2010 oficial e E3 estimado; D-3 cancelado |
| A6 | `CLAUDE.md` e `AGENTS.md` | partir do texto de 14/10 (D1) e acrescentar, se o autor aprovar: fila vigente, regra de ambiente (Python ≥ 3.12 fixado) e a linguagem do A8; não usar a redação do adendo 03 |
| A7 | hook `SessionStart` para criar o `.venv` | sim |

Itens de leitura da S1a que também são do autor: a conclusão sobre o curso 16
no backlog 36 (mais forte que o corpo, "na prática, indeterminado"); e a frase
"a bolsa é o piso da remuneração" na banca 1 (o 14/10 abriu a errata E10).

## 5. Entrega

- Commit de merge e commits de alinhamento, cada um com mensagem em português;
  push só para `claude/gallant-carson-11uzic`.
- Atualize a descrição do PR 4: o que foi conciliado, as decisões tomadas (com
  data e quem decidiu) e as que continuam abertas.
- Atualize o estado em [`README.md`](README.md) desta pasta e o roadmap.
- Merge na `main` só com autorização expressa do autor.
