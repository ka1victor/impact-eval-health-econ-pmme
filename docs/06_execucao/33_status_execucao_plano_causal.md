# Estado executado do plano causal público

> **Data:** 2026-09-04.
> **Estado geral:** `A8_EXECUTADO_EFEITO_LOCAL_CONDICIONAL`.
> **Dependência externa:** nenhuma.

## Decisão vigente

O pedido administrativo não foi enviado. A RDD da bolsa pelo IVS público
permanece bloqueada, mas o diagnóstico foi corrigido em 09/09/2026: a regra
administrativa **é** determinística — o rótulo de IVS determina a faixa em 527 de
527 municípios — e o que falta é o **escore contínuo** que gera essa categoria.
Nenhuma regra de corte sobre o IVS 2010 do IPEA pode recuperá-lo; o teto
demonstrado é 78,0%. Isso não bloqueia o trabalho curto.
**Nenhum pedido foi enviado e nenhum efeito RDD da bolsa foi estimado.**

O núcleo causal agora é o cutoff de seleção por escore. A amostra principal
compara o último selecionado ao primeiro não selecionado na mesma primeira
opção, em ampla concorrência, exclui empates e exige diferença exata de um
ponto.

## Portões executados

| Etapa | Estado | Evidência/decisão |
|---|---|---|
| A8-P0 | `CONCLUIDO_RETROSPECTIVO` | pergunta, estimando, amostra, outcomes e linguagem proibida congelados após abertura prévia dos outcomes no A7 |
| A8-P1 | `APROVADO_SUPORTE` | 36 pares em 2025: 30 na chamada 1 e 6 na chamada 2 |
| A8-P2 | `APROVADO_SEM_EMPATES` | ampla concorrência, primeira opção, gap de um ponto; desempates por UF/idade não determinam os pares principais |
| A8-P3 | `ESTIMADO` | +63,9 p.p. em homologação e +33,3 p.p. em presença ativa no mesmo curso–CNES |
| A8-P4 | `APROVADO_DIAGNOSTICOS` | placebo abaixo nulo; gaps alternativos e leave-one-out sem inversão de sinal |
| A8-P5 | `REPLICACAO_DIRECIONAL` | 11 pares em 2026; +36,4 p.p. em presença ativa, teste exato `p=0,125` |
| A8-P6 | `AUDITADO` | outputs agregados sem PII, hashes de entrada e testes automatizados |
| RDD-IVS | `ARQUIVADO_ESCORE_NAO_OBSERVADO` | a regra é determinística (527/527), mas nenhuma regra de corte sobre o IVS 2010 público a recupera: teto de 78,0% para qualquer regra de dois cortes |
| Pedido administrativo | `CANCELADO_NAO_ENVIADO` | nenhum recebimento ou espera integra o plano atual |

## Resultado e alcance

Sob comparabilidade local, ganhar marginalmente a vaga de primeira opção
aumentou a adesão e a presença posterior naquele curso–CNES. O grau de rigor é
**moderado**: a comparação é muito próxima e institucionalmente bem definida,
mas o score é discreto, a amostra é pequena e a hipótese de comparabilidade
entre candidatos separados por um ponto não é integralmente testável.

O resultado não identifica o efeito da bolsa, do IVS, do programa sobre o
estoque geral, da decisão de se candidatar nem retenção individual contínua.

## Próxima ação interna

Redigir o trabalho curto com:

1. A4 como motivação descritiva do gradiente territorial;
2. A8 como resultado causal principal;
3. replicação de 2026, placebos e sensibilidades como validação;
4. A5 no apêndice como evidência associativa, sem usá-la para reforçar
   causalidade;
5. RDD-IVS e DDD apenas como rotas avaliadas e descartadas.

O plano completo está em
[`17_plano_causal_publico_cutoff_escore.md`](../05_identificacao/17_plano_causal_publico_cutoff_escore.md).

## Reprodutibilidade do estado validado — verificação de 01/10/2026

**Comando**, da raiz, sobre `127e3be`: `.venv/bin/python run_all.py` e depois
`.venv/bin/python run_tests.py`. Ambiente: Python 3.12.3, numpy 2.5.2, pandas
3.0.5, statsmodels 0.15.0, scipy 1.18.1, matplotlib 3.11.1, como fixado em
`requirements.txt`. `verificar_ambiente(estrito=True)` passou.

**`run_all.py` não completa sem os microdados do CNES.** Ele aborta na etapa 8
de 25, `scripts/aquisicao/05_integrar_painel_analitico.py`, com
`RuntimeError: Painel CNES incompleto`. É o D-4 de
[`36_backlog_pos_auditoria.md`](36_backlog_pos_auditoria.md). Para conferir o
resto, as etapas 8 a 25 rodaram uma a uma, na ordem de `STEPS` e sem mudar
nenhum script:

- a etapa 8 falha;
- a etapa 9, `run_pipeline_avaliacao.py`, roda só o passo 01. Ela falha no 02
  por falta de `output/painel_municipio_curso_mensal.parquet`, então os passos
  03 a 09 da DDD não rodam;
- as etapas 10 a 25 terminam sem erro.

`data/` não mudou: os SHA-256 dos 33 arquivos são iguais antes e depois.

**Suíte e conferidores.** Os 188 testes passam, tanto sobre os artefatos
regravados quanto depois da reversão. Os dois conferidores aprovam:

- artigo principal: 214 cifras, 0 problemas estruturais;
- artigo curto: 199 cifras (88 próprias e 111 reutilizadas), 101 decimais
  distintos, 0 sem origem.

**Classificação dos 41 arquivos alterados em `output/`.** Todos foram
revertidos com `git checkout -- output/` e nada regravado foi versionado.

*(a) Idênticos byte a byte.* Todo o resto, inclusive A1 a A3
(`tema_trabalho/01`–`04`), A4 (`05`), aquisição (`01`, `02`, `04`) e A8 (`09`,
`09b`, com `A8_figura_01`). Sob Python 3.12.3, A8 também reproduz byte a byte.

*(b) Só metadados ou carimbos.*

- Data de execução: `rdd_bolsa/a01b_reconstrucao_regra_faixa.json`,
  `rdd_bolsa/triagem_resposta_administrativa.json`,
  `A5_manifesto_maturidade_censura.json` e `A5_relatorio_diagnostico.md`.
- `rdd_bolsa/portao_regra_ivs.json`: data e SHA-256 de
  `aquisicao/quadro_vagas_tratamento.parquet`. **Achado:** o hash versionado
  (`41e1d3af…`) é o da versão anterior do parquet (`ac55c71`), não o da versão
  versionada (`96281c14…`). As duas versões têm o mesmo conteúdo, salvo o tipo
  de `cod_curso` (int32 numa, int64 na outra). O mesmo hash defasado está em
  `rdd_bolsa/diagnostico_viabilidade_salario_ivs.json`.
- `rdd_bolsa/status_execucao_plano_causal.json`: data e SHA-256 de
  `docs/pedidos_dados/solicitacao_focal_rdd_bolsa.md` e `vagas_e_regra_ivs.md`.
  Os dois documentos foram editados depois da última gravação.
- `A7_cutoff_selecao_resumo.json`: 10 caminhos com barra invertida do Windows
  passam a POSIX. Os hashes de entrada não mudam.
- Os cinco PNG de A5 (`A5_figura_01` a `05`) são iguais pixel a pixel. Só o
  campo `Software` muda: Matplotlib 3.11.2 no versionado, 3.11.1 no fixado.
- `A6_manifesto_reproducao.json`: data, versões e hashes que acompanham A5 e os
  documentos carimbados. A versão registrada no versionado é Python 3.11.15,
  numpy 2.4.6 e pandas 3.0.6.
- `A8_conferencia_numeros_artigo.csv` e `_curto.csv`: muda só
  `valor_bruto_na_fonte` no 15º ou 16º dígito (29 e 49 células), herdado de A5.
  As cifras aprovadas são as mesmas.

*(c) Mudança numérica.*

- Ruído de ponto flutuante de até 1,5e-11 em valor absoluto:
  - `avaliacao_impacto/relatorios/01_relatorio_portao_relevancia.json` e
    `tabela_portao_relevancia.csv`: até 1,6e-15;
  - `A7_tabela_02`: 1,7e-21;
  - `A5_estimativas_provimento.json`: 774 valores, até 2,6e-13;
  - `A5_tabela_03` a `03i`, `04`, `06` a `12`, `14` e `15`: no máximo 1,5e-11,
    em `03h.ci_low`.
- `A5_tabela_05` reordena 43 linhas empatadas em `delta`. O conjunto de linhas
  e os valores são os mesmos (diferença até 1,1e-13), e o top-20 não muda.
- `A5_tabela_03h`, termo `const` de `OLS_delta_ampliada_597_sobreposta_minimal`:
  o coeficiente é cerca de −4e-15, ou seja, a constante foi absorvida. Erro
  padrão, IC e `p` passam de NaN a 3,7e-7, ±7,2e-7 e 1,0. O termo é degenerado
  nas duas versões.
- **`A5_tabela_13_pretendencia_por_curso.csv` e o bloco `pretendencia_por_curso`
  de `A5_ameacas_c7.json` divergem acima do ruído.** `pre_F_gl_fe` muda até
  3,5e-4 (1,0e-3 em termos relativos) e `pre_p_gl_fe` até 2,5e-4. A divergência
  fica em quatro linhas: cursos 3 e 13, em nível e em proporção. Nas quatro,
  `pre_F_confiavel = False`, com posto da covariância de 4 e 3 em 12. Por
  efeito em cadeia, `q_fdr_bh_pre` muda até 2,5e-4 em 20 células das famílias
  de 10 cursos. Nenhuma decisão `pre_rejeita_5pct` ou `pre_rejeita_5pct_q` muda,
  e nenhuma cifra do artigo é afetada.

Leitura: A5 e A6 versionados foram gravados fora do ambiente fixado (nota de
ambiente de 21/09/2026 em `../auditorias/14_erratas_artefatos_congelados.md`).
Por isso A5 não reproduz byte a byte. O limite de 1,5e-11 daquela nota vale
para tudo, exceto o F de pré-tendência com covariância de posto incompleto,
que é numericamente instável.

**Efeito colateral em `docs/`, revertido.**

- `scripts/rdd_bolsa/02_controlar_execucao_plano_causal.py` reescreve **este
  arquivo** a partir de um modelo de 04/09/2026. O modelo traz o estado
  `PARCIAL_EXECUTADO_AGUARDANDO_DADOS_ADMINISTRATIVOS`, P1 como
  `PRONTO_NAO_ENVIADO` e A7 com 423 pares, e a reescrita apaga o estado curado.
  A suíte não detecta isso.
- Outros scripts carimbam a data em `../auditorias/07_portao_rdd_bolsa.md`,
  `../auditorias/09_matriz_afirmacao_evidencia_limite.md` e
  `../auditorias/09_red_team_atracao_provimento.md`, e o hash de A5 em
  `32_sintese_A6_resumo_intro_metodos_conclusao.md`.

**Pendente de decisão do autor**, sem mudança nesta sessão:

1. regravar A5 e A6 sob o ambiente fixado, como foi feito com A8 em 16/09;
2. corrigir os hashes defasados do quadro de vagas em `portao_regra_ivs.json` e
   `diagnostico_viabilidade_salario_ivs.json`;
3. impedir que o `02_controlar` sobrescreva este documento;
4. tratar o aborto do `run_all.py` sem CNES (D-4).
