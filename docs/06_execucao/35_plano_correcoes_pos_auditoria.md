# Plano de correções pós-auditoria — congelado antes da implementação

> **Data:** 2026-09-09. **Estado:** `PLANO_CONGELADO_PRE_IMPLEMENTACAO`.
> **Origem:** `docs/auditorias/13_reauditoria_independente_A1_A8.md`.
> **Regra deste documento:** os números-alvo abaixo foram calculados na auditoria
> e estão registrados **antes** de qualquer alteração de código. A implementação
> que divergir deles é erro de implementação, não novo resultado. Nenhuma
> especificação pode ser reescolhida depois de ver o efeito.

## Por que este documento existe antes do código

A auditoria encontrou três problemas que exigem mudança de artefato, não apenas
de texto. Dois deles alteram números publicados. Num projeto cujo `CLAUDE.md`
proíbe escolher filtros, janelas ou estimadores retrospectivamente, mudar
estimativa depois de ver resultado é exatamente o risco a evitar. A proteção
adotada é congelar aqui, com antecedência, o que muda, por quê, e qual número
deve sair — de modo que a execução seja verificável contra um alvo declarado.

---

## C1 — A4: alinhar o colapso de UF ao protocolo declarado

### Problema

`docs/.../registro_pre_analise_atracao.json` (A3) declara: *"colapsar UF com &lt;5
clusters **em região**"*. `scripts/tema_trabalho/05_estimar_atracao.py:169` junta
as oito UFs pequenas num balde único `"RESTO"`, misturando quatro macrorregiões
(AL, PB, PE, SE do Nordeste; AP, RR do Norte; DF do Centro-Oeste; ES do Sudeste).
O próprio comentário do código diz "em região", mas o código não faz isso.

Dentro do balde `RESTO` há 32 células de capital contra **uma única** célula de
interior remoto (AP, n=1, taxa 0). O balde permite exatamente a comparação entre
estados que o efeito fixo de UF deveria impedir.

### Decisão

**Corrigir a implementação para o protocolo.** O protocolo foi escrito e
congelado antes dos desfechos; a implementação divergiu em silêncio. A
especificação primária passa a ser a declarada — colapso em macrorregião de
saúde — e as outras duas viram sensibilidade publicada.

Esta não é reescolha retrospectiva: não se está selecionando a variante que dá
o melhor resultado, e sim restaurando a que foi pré-especificada. As três
variantes serão publicadas lado a lado, para que a escolha fique auditável.

### Alvos congelados

| Variante | Capital | Metropolitano | Interior próximo |
|---|---:|---:|---:|
| Executado até aqui (balde `RESTO`) | +0,2318 | +0,2942 | +0,1266 |
| **Protocolo (macrorregião) — nova primária** | **+0,3264** | **+0,2793** | **+0,1207** |
| Sem colapso (27 UFs) | +0,3358 | +0,2733 | +0,1200 |

O resultado de manchete do artigo é o contraste metropolitano, que se move de
+29,4 para +27,9 p.p. — estável. O contraste de capital se move 40%, de +23,2
para +32,6 p.p., e é ele que motiva a correção.

### Escopo

- `05_estimar_atracao.py`: colapso em `macro_regiao_saude`; nova tabela de
  sensibilidade com as três variantes.
- Reexecução de A4 e, por dependência de hash, A6. **Não** reexecutar A1, A2,
  A3 nem a versão agregada do ciclo 1.
- Artigo: atualizar o contraste de capital e acrescentar a sensibilidade.

---

## C2 — A5: promover a escala proporcional e publicar leave-one-curso-out

### Problema

O coeficiente de manchete de A5 (0,50 no `202603`) é frágil a duas coisas que
nenhum artefato testa:

1. **Composição de cursos.** Sem o curso 14 cai para 0,200 (`p = 0,366`); com
   apenas os oito cursos de CBO estritamente 1:1 cai para 0,121 (`p = 0,608`).
2. **Mês de referência.** Contra a média dos doze meses pré, é +0,405
   (`p = 0,174`). `202506`, a referência escolhida, é o ponto mais baixo do
   caminho pré.

Some-se a isso que **"dez cursos com CBO unívoco" é falso para dois deles**: na
própria ponte, o curso 14 é `MULTIESPECIALIDADE_EXCLUSIVA` e o 16 é
`FAMILIA_PATOLOGIA`. "Unívoco" está sendo usado como "não compartilhado com
outro curso do PMM-E", que é outra coisa. O curso 14 mede todos os radiologistas
do município, não a competência específica do curso.

### Decisão

**A especificação em nível deixa de ser a forma primária de reportar A5, e a
proporcional (`log1p`) passa a sê-lo.** Motivo substantivo, não estatístico: o
desfecho em nível soma profissionais de municípios com estoques de ordens de
grandeza diferentes, então um curso com estoque grande domina mecanicamente. A
escala proporcional é a pergunta correta — variação relativa da oferta local — e
já era a leitura pretendida do texto.

A escala proporcional é robusta a tudo o que derruba a de nível:

| Amostra | `log1p` | p |
|---|---:|---:|
| 10 cursos | +0,0684 | 0,0002 |
| sem o curso 14 | +0,0592 | 0,0040 |
| só os 8 cursos 1:1 estritos | +0,0570 | 0,0100 |

### Alvos congelados

- Coeficiente proporcional primário: **+0,0684** (`p = 0,0002`).
- Leave-one-curso-out em nível deve reproduzir 0,200 sem o curso 14 e 0,121 nos
  oito estritos.
- Sensibilidade de referência deve reproduzir +0,405 (`p = 0,174`) contra a média
  do período pré.
- A correção de graus de liberdade que ignora os FE absorvidos move o `p` da
  especificação em nível de 0,033 para 0,044. **Corrigir também.**

### Escopo

- `06_avaliar_provimento_cnes.py`: especificação `log1p`; leave-one-curso-out do
  coeficiente de evento; sensibilidade de mês de referência; `k` incluindo os FE
  absorvidos em `model_utils.fit_absorbed_ols`.
- Renomear a categoria da ponte para o que ela de fato significa, sem alterar a
  ponte.
- Artigo: o apêndice de A5 passa a reportar a escala proporcional, mantendo a de
  nível como sensibilidade explicitamente frágil.

A linguagem de A5 continua **associativa**. Nada aqui promove A5 a causal.

---

## C3 — Pedido do escore administrativo de IVS: refazer a justificativa

### Problema

O pedido foi arquivado como `CANCELADO_NAO_ENVIADO` com a justificativa "a regra
não é reproduzível". A auditoria mostrou que essa justificativa está errada, e
que a correta é muito mais forte.

### O que a auditoria estabeleceu

1. A regra **é** determinística: na janela estável de fev a ago/2026, o rótulo
   administrativo de IVS determina a faixa de bolsa em **527 de 527 municípios**,
   sem uma única ambiguidade.
2. A regra aplicada **não é** a publicada no FAQ. De facto, muito alta e alta →
   Faixa 1; média → Faixa 2; baixa e muito baixa → Faixa 3. Só a competência
   jan/2026 segue o texto do FAQ.
3. Nenhuma regra de corte sobre o IVS 2010 do IPEA reproduz a atribuição. O
   **teto** de qualquer regra monótona é 65,1%; o de qualquer regra de dois
   cortes para a faixa é 78,0%, errando no mínimo 119 de 540 municípios, apesar
   de `ρ = 0,812` de Spearman.
4. Não há variação temporal: zero mudanças de faixa em seis pares de competências
   consecutivas.

### Decisão

Reescrever a justificativa do pedido em torno de (3), que é uma impossibilidade
demonstrada, e de (1), que mostra que o primeiro estágio seria *sharp* por
construção assim que o escore existir. **O pedido continua não enviado**: o canal
é decisão do autor. O que muda é que o pacote passa a carregar o argumento certo.

### Escopo

- `docs/pedidos_dados/vagas_e_regra_ivs.md` e
  `docs/pedidos_dados/solicitacao_focal_rdd_bolsa.md`: nova justificativa.
- `docs/05_identificacao/16_sintese_achados_e_novo_plano_causal.md`: corrigir o
  diagnóstico de "regra não reproduzível" para "escore não observado".
- Nenhum código. Nenhum envio.

---

## O que este plano NÃO autoriza

- Promover A5 a causal, em qualquer escala.
- Reexecutar a versão agregada do ciclo 1 (DDD, estudo de evento, mecanismos).
- Reexecutar A1, A2 ou A3, cujos portões e congelamentos permanecem válidos.
- Alterar a amostra, o desfecho ou o estimador de A8. Os defeitos de medida de
  A8 já foram corrigidos no texto do artigo em `53e513e` e não exigem novo
  cálculo do resultado principal.
- Escolher entre as variantes de C1 depois de ver qual favorece a narrativa. A
  primária é a do protocolo, decidida aqui.
- Enviar qualquer pedido administrativo.

## Portão de aceitação

A implementação só é aceita se reproduzir os alvos congelados acima. Divergência
substantiva contra qualquer um deles interrompe a execução e vira achado, não
resultado novo. A suíte deve continuar verde e a conferência de cifras do artigo
deve continuar passando.

---

# Emenda 1 — 14/09/2026 — inferência e precisão de A4

> **Estado:** `EMENDA_CONGELADA_PRE_IMPLEMENTACAO`.
> **Origem:** sessão 2 da fila normativa de `36_backlog_pos_auditoria.md`, itens
> **A-2**, **A-3** e **C-6**.
> **Regra desta emenda:** vale a mesma do documento — o que muda, por quê e qual
> número deve sair ficam registrados **antes** de qualquer alteração de código.

## Ressalva que se aplica às três correções

Os alvos numéricos que o backlog congelou para A-2, A-3 e C-6 foram medidos na
especificação **anterior ao C1**, isto é, com o balde único `RESTO` e 20 níveis
de efeito fixo de UF. O C1 já está implementado e a especificação primária
vigente é outra: colapso em macrorregião de saúde, com **24 níveis** de efeito
fixo de UF, reproduzindo capital +0,3264, metropolitano +0,2793 e interior
próximo +0,1207.

Os três itens **precisam ser recomputados na especificação vigente**. Os valores
do backlog servem como **ordem de grandeza e direção esperadas**, não como alvo
exato, e o próprio backlog diz isso para A-2 e C-6. Esta emenda estende a mesma
ressalva ao A-3, que é medido na mesma especificação e tem a mesma dependência.

O portão de aceitação passa a ser, para estes três itens: **direção e ordem de
grandeza**. Divergência de direção, ou de ordem de grandeza, interrompe a
execução e vira achado — não se ajusta a implementação até bater.

Nada aqui altera o estimador primário. O **LPM continua sendo o modelo
primário**, e seus coeficientes, erros-padrão e valores `p` não mudam.

---

## E1-A — wild cluster bootstrap que o protocolo A3 exige (item A-2)

### Problema

`output/tema_trabalho/registro_pre_analise_atracao.json`, campo `inferencia`,
declara: *"HC cluster-robusto (LPM/logit) com G clusters; **se G<30 em subgrupo,
reportar também wild cluster bootstrap**"*. O A4 registra o aviso —
*"wild bootstrap recomendado para subgrupo, não computado nesta entrega"* — e
nunca executa o procedimento.

A condição está satisfeita: capital tem `G = 18`. E o `G = 368` do cluster
principal é nominal: a variância de `estrato_metropolitano` concentra 61,5% nos
cinco maiores municípios, o que dá `G` efetivo ≈ 32.

### Decisão

**Computar o procedimento que o protocolo manda computar.** Não é reescolha de
inferência: é executar o que foi pré-especificado e ficou pendente.

Especificação, fixada aqui antes de rodar:

- Wild cluster bootstrap com **nula imposta** (restrito), sobre o LPM primário.
- Pesos de **Rademacher** (+1 / −1 com probabilidade 1/2), sorteados por
  **cluster de município**.
- `B = 1999` replicações.
- Semente fixa e declarada: **`SEED_WILD_BOOTSTRAP = 42`**, a mesma convenção de
  semente já usada no script (`group_kfold_splits`).
- Estatística bootstrapada: `t` cluster-robusto do coeficiente, com a mesma
  correção de amostra finita do ajuste principal.
- `p` bilateral pela convenção `p = (1 + N_excedentes) / (B + 1)`, em que
  `N_excedentes` conta as replicações com `|t*| >= |t observado|`, de modo que
  zero rejeições devolve `0,0005` e não zero.

### Alvo esperado — indicativo

Medido na especificação anterior ao C1 (balde `RESTO`):

| Estrato | t | p nominal | p wild |
|---|---:|---:|---:|
| metropolitano | 4,852 | 1,22e-06 | ≤ 0,0005 (0 de 1999) |
| capital | 2,694 | 0,00705 | 0,0185 |
| interior próximo | 2,934 | 0,00334 | 0,0070 |

Na especificação vigente espera-se: `p wild >= p nominal` nos três estratos, com
metropolitano na casa de `0,0005`, capital na ordem de `10^-2` e interior
próximo entre `10^-3` e `10^-2`. Os três permanecem significativos a 5%.

### O que explicitamente NÃO muda

- O `p` **principal** continua sendo o `p` cluster-robusto nominal. O `p` wild
  entra como **coluna adicional** e tabela própria, nunca como troca.
- Coeficientes, erros-padrão e intervalos de confiança do LPM.
- O `q` de FDR entre estratos, que segue calculado sobre o `p` nominal.
- O artigo: ele não cita `p` de capital, e a Tabela A1 publica diferença e
  erro-padrão, não `p`. Nenhuma cifra do artigo muda por este item.

---

## E1-B — efeito marginal médio do logit com contrafactual impossível (item A-3)

### Problema

`05_estimar_atracao.py` chama `res_logit_min.get_margeff(at="overall",
method="dydx", dummy=True, count=True)`. Para uma indicadora, o statsmodels
calcula a diferença predita alterando **apenas a coluna daquela indicadora** e
mantendo as demais no valor observado.

As quatro categorias de estrato são um **bloco mutuamente exclusivo**. Alterar só
`estrato_metropolitano` de 0 para 1 numa célula de capital produz uma célula que
é simultaneamente capital e metropolitana — um contrafactual que não existe na
população. O AME publicado é a média de contrastes contra um estado impossível.

### Decisão

**Trocar o bloco inteiro.** O AME de cada estrato passa a ser o contraste contra
a categoria de referência `interior_remoto`, com todas as indicadoras do bloco
zeradas no braço de referência e apenas a do estrato avaliado ligada no braço
tratado, mantendo curso, UF e demais covariadas no valor observado:

```
AME_L = media_i [ Lambda(x_i com bloco = L) - Lambda(x_i com bloco = 0) ]
```

O erro-padrão vem do método delta sobre a **mesma matriz de covariância
cluster-robusta** já usada no ajuste do logit, preservando o cluster de
município. Não se troca o estimador nem a especificação: troca-se o
contrafactual, de um impossível para o declarado em A3, que é "contraste contra
interior remoto".

### Alvo esperado — indicativo

Medido na especificação anterior ao C1:

| Estrato | AME publicado | AME correto |
|---|---:|---:|
| metropolitano | 0,2928 | 0,2669 (EP 0,0554) |
| capital | 0,2501 | 0,2204 (EP 0,0944) |
| interior próximo | 0,1077 | 0,0984 (EP 0,0355) |

Superestimação de 0,9 a 3,0 p.p. Na especificação vigente espera-se o mesmo
padrão: **AME correto menor em valor absoluto** que o publicado, na ordem de 1 a
3 p.p., com **sinal, ordenação entre estratos e significância intactos**, e
concordância com o LPM preservada. Os valores publicados hoje na especificação
vigente, dos quais a correção parte, são capital 0,3606, metropolitano 0,2784 e
interior próximo 0,1009.

### O que explicitamente NÃO muda

- O **LPM continua sendo o primário**. O logit é e permanece alternativo.
- A especificação do logit — covariadas, efeitos fixos, cluster, otimizador.
- O AME das covariadas que **não** pertencem ao bloco de estrato: curso e UF
  também são blocos categóricos, mas não são estimando publicado nem citado, e
  alterá-los estaria fora do escopo deste item. O valor do statsmodels para eles
  permanece, e a tabela passa a rotular por linha qual método gerou cada AME.
- O valor antigo não é apagado: fica em coluna própria, para auditoria.

### Efeito no artigo

A Tabela A1 do apêndice publica a linha **"Logit, efeito marginal médio"**, hoje
`27,8` com erro-padrão `6,2`. Essa linha **muda**, e o artigo precisa ser
atualizado junto com o artefato. A linha "Modelo linear pré-especificado", que é
o resultado primário, **não muda**.

---

## E1-C — MDE ex-ante é otimista contra o modelo estimado (item C-6)

### Problema

O MDE publicado em A3 é analítico: parte de uma fórmula de diferença de
proporções com DEFF por estrato. Ele ignora que os efeitos fixos de curso e de UF
absorvem variação do próprio estrato, e por isso subestima o erro-padrão que o
modelo de fato entrega. O artigo cita **13,7 p.p.** como efeito mínimo detectável
do contraste metropolitano; o erro-padrão realizado implica um valor maior.

### Decisão

**Publicar o MDE ex-post ao lado do ex-ante, sem apagar o ex-ante.** O ex-ante
continua sendo o registro do que foi pré-especificado em A3, e A3 é protocolo
congelado — não se reescreve. O ex-post é a leitura honesta da precisão que o
modelo entregou.

Fórmula do ex-post, a partir do erro-padrão cluster-robusto realizado do próprio
coeficiente:

```
MDE_ex_post = (z_{1-alpha/2} + z_poder) * EP_realizado
            = (1,959964 + 0,841621) * EP_realizado
            = 2,801585 * EP_realizado
```

a 80% de poder e 5% bilateral, os mesmos parâmetros do ex-ante.

### Alvo esperado

Aqui o alvo é **exato**, não indicativo: os erros-padrão realizados da
especificação vigente já estão publicados em
`A4_tabela_02_modelo_principal_LPM.csv`, e o cálculo é aritmética sobre eles.

| Estrato | EP realizado (vigente) | MDE ex-post | MDE ex-ante do A3 | Otimismo |
|---|---:|---:|---:|---:|
| capital | 0,07179 | **20,1 p.p.** | 19,5 p.p. | ~3% |
| metropolitano | 0,05855 | **16,4 p.p.** | 13,7 p.p. | ~19% |
| interior próximo | 0,04312 | **12,1 p.p.** | 11,9 p.p. | ~2% |

Para registro, na especificação anterior ao C1 o backlog mediu 24,1 / 17,0 / 12,1
contra os mesmos ex-ante, com otimismo de 23,8% / 23,6% / 1,6%. O C1 reduziu o
erro-padrão de capital, então o otimismo de capital cai muito; o de
metropolitano cai pouco e continua sendo o caso relevante. **A direção é a mesma
nas duas especificações: o ex-post é maior que o ex-ante nos três estratos.**

### O que explicitamente NÃO muda

- O MDE **ex-ante** de A3 permanece publicado, com o mesmo valor e o mesmo
  rótulo. A3 continua congelado e **não** é reexecutado.
- `potencia_atracao.json` e `registro_pre_analise_atracao.json` não são tocados.
- O benchmark global de 3,8 p.p., que já foi corretamente rerrotulado como
  precisão de uma proporção.
- O item **C-5**, que é outro defeito do bloco `por_estrato` de A3 e pertence à
  sessão 5.

### Efeito no artigo

O artigo hoje cita apenas os 13,7 p.p. ex-ante. Passa a citar os dois, com o
rótulo de cada um. O 13,7 **não é apagado**.

---

## Escopo total desta emenda

- `scripts/tema_trabalho/05_estimar_atracao.py`: wild cluster bootstrap, AME por
  bloco, MDE ex-post. Nenhuma mudança de amostra, desfecho ou estimador primário.
- Saídas `output/tema_trabalho/A4_*`, incluindo duas tabelas novas.
- `paper_pmme_submission.tex`: linha do logit na Tabela A1 e a frase de precisão.
- `scripts/tema_trabalho/10_conferir_numeros_artigo.py`: a cifra nova do MDE
  ex-post precisa de origem rastreável, como toda cifra do artigo.

## O que esta emenda NÃO autoriza

- Tocar em `06_avaliar_provimento_cnes.py` ou em qualquer saída `A5_*`. A5 está
  bloqueado por dado ausente (item D-4).
- Reexecutar A1, A2 ou A3.
- Trocar o `p` principal do LPM pelo `p` do bootstrap.
- Promover o logit a primário.
- Alterar as seções A-1 e D-4 do backlog, que registram achado de outra sessão.
- Escolher, depois de ver os números, qual variante de AME ou de `p` publicar.

## Portão de aceitação desta emenda

Direção e ordem de grandeza reproduzidas nos três itens; `run_tests.py` verde;
`10_conferir_numeros_artigo.py` aprovando **todas** as cifras do artigo; e o
artigo compilando sem transbordo de caixa e sem referência indefinida.

---

# Emenda 1 — resultado da execução (14/09/2026)

> Registrado **depois** de executar, contra os alvos declarados acima. Commit da
> emenda: `9e5de6d`. Nenhuma implementação foi ajustada para bater alvo.

## E1-B (A-3) e E1-C (C-6) reproduzem

**AME por bloco**, especificação vigente:

| Estrato | AME antigo (indicadora isolada) | AME por bloco | Δ (p.p.) |
|---|---:|---:|---:|
| capital | 0,3606 | **0,3403** (EP 0,0757) | −2,03 |
| metropolitano | 0,2784 | **0,2513** (EP 0,0524) | −2,71 |
| interior próximo | 0,1009 | **0,0908** (EP 0,0350) | −1,02 |

Dentro da faixa de 1 a 3 p.p. declarada, todas as reduções, sinal, ordenação e
significância intactos, e a concordância com o LPM preservada.

**MDE ex-post**: 20,1 / 16,4 / 12,1 p.p. contra ex-ante 19,5 / 13,7 / 11,9, com
otimismo de 3,4% / 19,4% / 1,5%. Exatamente o alvo declarado.

## E1-A (A-2) reproduz a direção; o `p` de capital fica fora da faixa declarada

| Estrato | t | p nominal | p wild obtido | faixa declarada |
|---|---:|---:|---:|---|
| metropolitano | 4,770 | 1,84e-06 | **0,0005** (0 de 1999) | casa de 0,0005 ✔ |
| capital | 4,547 | 5,45e-06 | **0,0015** (2 de 1999) | ordem de 10⁻² ✘ |
| interior próximo | 2,798 | 5,14e-03 | **0,0115** (22 de 1999) | 10⁻³ a 10⁻² ✔ (borda) |

`p wild >= p nominal` nos três, e os três seguem significativos a 5%: a direção,
que é o que a emenda fixou como portão, reproduz.

**Por que capital sai da faixa, e por que isso não é erro de implementação.** A
faixa de 10⁻² foi derivada do `t = 2,694` da especificação **anterior ao C1**. O
C1 é justamente a correção que move capital mais: o coeficiente vai de +0,2318
para +0,3264 e o `t` de 2,694 para 4,547. Um `t` quase 70% maior produz
necessariamente um `p` de bootstrap menor. O alvo indicativo envelheceu junto com
a especificação, exatamente como a ressalva desta emenda previa.

**Verificação independente, antes de aceitar o número.** A mesma implementação
foi aplicada, em diagnóstico somente-leitura, à especificação anterior ao C1:

| Estrato | t obtido | t do backlog | p nominal obtido | p nominal do backlog | p wild obtido | p wild do backlog |
|---|---:|---:|---:|---:|---:|---:|
| metropolitano | 4,852 | 4,852 | 1,221e-06 | 1,22e-06 | 0,0005 (0/1999) | ≤ 0,0005 (0/1999) |
| capital | 2,694 | 2,694 | 7,050e-03 | 0,00705 | 0,0225 | 0,0185 |
| interior próximo | 2,934 | 2,934 | 3,344e-03 | 0,00334 | 0,0065 | 0,0070 |

Os `t` e os `p` nominais batem dígito a dígito, e metropolitano reproduz o
`0 de 1999` exato. As duas diferenças restantes de `p` wild são ruído de Monte
Carlo de semente distinta — a auditoria não publicou a sua —, com erro-padrão de
simulação de cerca de 0,0031 em `B = 1999` nessa faixa de `p`. A implementação
está validada; o que mudou foi a especificação.

## Achado colateral — o `61,5%` da reauditoria não foi reproduzido

A reauditoria motiva o bootstrap dizendo que *"a variância de
`estrato_metropolitano` concentra 61,5% nos cinco maiores municípios, dando `G`
efetivo ≈ 32"*. Nenhuma das cinco definições naturais testadas devolve 61,5%:
soma de quadrados do regressor centrado por município (23,1%), quadrado da soma
do escore de cluster (51,2%), contagem de células metropolitanas (29,1%), e as
duas versões residualizadas por Frisch–Waugh–Lovell (12,8% e 31,9%).

**Não se procurou uma sexta definição que batesse**, porque escolher a definição
depois de ver qual reproduz o número é precisamente o que esta fila proíbe.

**Consequência adotada:** o `61,5%` e o `G` efetivo ≈ 32 **não** são publicados
como resultado de A4 nem citados no artigo. O bootstrap passa a ser justificado
pelo gatilho literal do protocolo A3 — `G < 30` em subgrupo, e capital tem
`G = 18`, número que vem de `A4_tabela_01_amostra_construcao.csv`. O diagnóstico
da auditoria continua onde está, atribuído a ela.

**Não corrigido:** a definição exata do `61,5%` continua em aberto em
`docs/auditorias/13_reauditoria_independente_A1_A8.md`. Resolver isso é decisão
de quem escreveu a auditoria, não desta sessão.

## Efeito no artigo

- Tabela A1, linha "Logit, efeito marginal médio": **27,8 / 6,2 → 25,1 / 5,2**.
- Nota da Tabela A1: passa a dizer o que o AME contrasta.
- Apêndice A: o MDE ex-ante de 13,7 p.p. é mantido e passa a vir acompanhado do
  ex-post de 16,4 p.p., com o rótulo de cada um; parágrafo novo sobre o
  bootstrap.
- A linha "Modelo linear pré-especificado" (27,9 / 5,9), que é o primário, **não
  muda**, e nenhum outro número do artigo muda.
- O conferidor passa de 190 para **193** cifras, todas aprovadas.

---

# Emenda 2 — 16/09/2026 — colapso de UF em macrorregião nos modelos secundários de A5

> **Estado:** `EMENDA_CONGELADA_PRE_IMPLEMENTACAO`.
> **Origem:** sessão 1 da fila normativa de `36_backlog_pos_auditoria.md`, item
> **A-1**, bloqueada em 14/09/2026 por achado e por D-4.
> **Regra desta emenda:** a mesma do documento — o que muda, por quê e qual
> número deve sair ficam registrados **antes** de qualquer alteração de código.
> **Autorização:** o autor delegou a esta sessão, em 16/09/2026, as decisões
> listadas em "Decisões que dependem do autor" do backlog, com a instrução de
> decidir e documentar. A decisão abaixo foi tomada nesses termos.

## O que destravou a sessão

O bloqueio de D-4 era mais estreito do que estava registrado: A5 pode ser
reestimado a partir de `A5_painel_T0.parquet`, com o hash conferido contra o
manifesto A6, e isso foi validado byte a byte antes desta emenda (commit
`da4d6f7`; detalhe na seção D-4 do backlog). O achado sobre o alvo continua e é
resolvido aqui.

## Decisão 1 — definição do efeito fixo para células sem macrorregião publicada

**Adotada: nível residual rotulado**, `MACRO_SEM_REGIAO_SAUDE`, o que dá **24
níveis** de efeito fixo de UF — a mesma implementação de `colapsar_uf_fe` do C1
em A4.

Por quê, e por que isto não é escolher depois de ver o efeito:

1. O princípio é anterior aos dois coeficientes. O C1 fixou, em 09/09/2026, que
   município sem macrorregião publicada forma nível próprio rotulado "em vez de
   herdar uma região" (`05_estimar_atracao.py`, `colapsar_uf_fe`). A-1 existe
   para dar a A5 a mesma correção que A4 recebeu; aplicar em A5 uma definição
   diferente da de A4 seria a assimetria, não a simetria.
2. A alternativa carrega a classe de defeito que o item corrige. Com 23 níveis,
   as quatro células (Oiapoque/AP, Cachoeiro de Itapemirim/ES, Linhares/ES e a
   quarta do mesmo conjunto `MACRO_SEM_REGIAO_SAUDE`) ficam **sem efeito fixo de
   UF nenhum**, descartadas em silêncio por `pd.get_dummies`. A-1 nasceu de
   células sem efeito fixo próprio; adotar uma medição que reproduz isso seria
   corrigir o defeito em 21 municípios e mantê-lo em três.
3. A escolha não muda a conclusão em nenhuma direção: +0,5062 contra +0,5014,
   `p` 0,0434 contra 0,0456, mesmo sinal, mesma ordem, mesma leitura
   associativa. Nenhuma das duas favorece a narrativa; a decisão é
   definicional, e as duas variantes ficam publicadas lado a lado.

## Alvos reemitidos

Medidos em 14/09/2026 em conferência somente-leitura sobre `A5_painel_T0.parquet`,
replicando `build_X("minimal")`/`fit_ols` de A5 — modelo `delta_minimal`,
variação do estoque 202506→202603, amostra confirmatória de 587 células:

| Variante | coef | EP | p | níveis UF | papel |
|---|---:|---:|---:|---:|---|
| Balde único `RESTO` (implementação atual) | **+1,2949** | 0,7749 | 0,0947 | 20 | sensibilidade publicada |
| **Colapso em macrorregião, residual rotulado** | **+0,5062** | **0,2506** | **0,0434** | **24** | **nova primária dos modelos secundários** |
| Sem colapso (27 UFs) | **+0,5002** | 0,2414 | 0,0382 | 27 | sensibilidade publicada |

O alvo de +0,5014 / 23 níveis do backlog **não** é mais alvo: ele descreve a
variante "ausente → referência", que a Decisão 1 rejeita. Fica registrado como
medição, não como alvo.

## Decisão 2 — cobertura do alvo

`uf_fe` alimenta as tabelas `03`, `03b`–`03i`, `04`, `05` e `06` de A5. O
backlog congela alvo para um único coeficiente e alerta que adotar macrorregião
move todos os outros sem alvo declarado. Tratamento adotado:

- o **portão numérico** é o `delta_minimal` da tabela acima, nas três variantes;
- as demais tabelas mudam **por consequência mecânica** da mesma definição de
  efeito fixo, sem alvo prévio, e o que se exige delas é a coerência
  documentada: a tabela nova de sensibilidade publica as três variantes também
  para `estoque_6m_minimal`, `cobertura_6m_minimal`, `entradas_6m_minimal` e
  `presentes_baseline_6m_minimal`, para que a mudança de cada coeficiente
  secundário fique auditável;
- **nenhum deles entra no artigo**, e nenhuma das seis cifras de A5 que o
  conferidor confere vem de modelo com `uf_fe`.

## O que muda

- `06_avaliar_provimento_cnes.py`: `uf_fe` passa a ser construído por
  colapso em macrorregião com residual rotulado, nas **duas** implementações
  hoje existentes — a coluna do painel e a de `A5_tabela_01e_amostra_uf.csv`.
  No modo de reestimação, a coluna `uf_fe` lida do painel congelado, que traz a
  definição superada, é recomputada em memória; o parquet não é regravado.
- Nova tabela `A5_tabela_11_sensibilidade_colapso_uf.csv`, com as três variantes
  para os cinco modelos `minimal` de corte transversal, no formato de
  `A4_tabela_07_sensibilidade_colapso_uf.csv`.
- `A5_estimativas_provimento.json` passa a registrar a variante primária e o
  número de níveis de efeito fixo.

## O que explicitamente NÃO muda

- O estudo de evento, manchete de A5, nas duas escalas: `uf_month` vem de
  `sg_uf` direto, com as 27 unidades. `0,0684` e `0,50` não mudam.
- A amostra confirmatória, a referência 202506, o follow 202603, a ponte.
- Os 11 alvos congelados do C2 que o próprio script confere.
- Qualquer cifra do artigo: o conferidor deve seguir aprovando as mesmas
  **193** cifras.

## Portão de aceitação desta emenda

1. `delta_minimal` reproduz as três linhas da tabela acima em quatro casas de
   coeficiente, EP e `p`, com o número de níveis declarado.
2. O script continua conferindo os 11 alvos do C2.
3. Suíte verde e conferidor do artigo inalterado em 193 cifras.
4. Divergência em qualquer dos três: **parar** — é achado, não resultado novo.

# Emenda 2 — resultado da execução (16/09/2026)

> **Estado:** `EXECUTADA`. Commit da emenda: `03ccc1c`, anterior ao código.
> Nenhuma implementação foi ajustada para bater alvo.

Os três alvos reemitidos reproduzem em quatro casas, com o número de níveis
declarado: `RESTO` +1,2949 / 0,7749 / 0,0947 / 20; macrorregião com residual
rotulado **+0,5062 / 0,2506 / 0,0434 / 24**; sem colapso +0,5002 / 0,2414 /
0,0382 / 27. O script confere os 12 valores como alvo congelado, ao lado dos 11
do C2 (23 alvos). Os cinco modelos `minimal` nas três variantes estão em
`A5_tabela_11_sensibilidade_colapso_uf.csv`. O estudo de evento não mudou;
`A5_painel_T0.parquet` não foi regravado; nenhuma cifra do artigo mudou e o
conferidor segue aprovando 193. Suíte: 174 testes verdes.
