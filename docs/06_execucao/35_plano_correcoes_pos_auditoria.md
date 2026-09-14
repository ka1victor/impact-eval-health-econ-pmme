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
