# Backlog pós-auditoria — fila executável

> **Criado em:** 2026-09-09. **Origem:** `docs/auditorias/13_reauditoria_independente_A1_A8.md`.
> **Plano já executado:** `35_plano_correcoes_pos_auditoria.md` (C1, C2 e C3, concluídos).
> **Regra desta fila:** cada item traz o alvo numérico medido **antes** de qualquer
> alteração. A implementação que divergir do alvo é erro de implementação, não
> resultado novo. Nenhuma especificação pode ser reescolhida depois de ver o efeito.

## Como usar

Os itens estão agrupados por **consequência**, não por módulo, porque é a
consequência que decide quanto rigor de processo cada um exige:

| Grupo | O que caracteriza | Processo exigido |
|---|---|---|
| **A** | Muda número publicado ou já divulgado | Emenda escrita e commitada antes de implementar, como no `35` |
| **B** | Muda artefato versionado, sem tocar número publicado | Commit próprio, sem emenda prévia |
| **C** | Só documentação, rótulo ou texto | Pode entrar junto de outro commit |
| **D** | Bloqueado por dependência externa | Não executar; revisar a condição |

Dentro de cada grupo a ordem é por dependência, depois por risco.

---

# Grupo A — muda número publicado

## A-1 · Balde `RESTO` nos modelos secundários de A5

**Onde:** `scripts/tema_trabalho/06_avaliar_provimento_cnes.py:194`, e o uso em
`:421`, `:425`, `:433`.

**O quê:** o mesmo defeito corrigido em A4 pelo item C1. As oito UFs com menos de
cinco municípios são jogadas num balde único `RESTO`, misturando quatro
macrorregiões. Em A5 o balde cobre 1.248 observações e 21 municípios da amostra
confirmatória.

**O que NÃO é afetado:** o estudo de evento, que é a manchete de A5, absorve
`sg_uf` direto na linha 768, com as 27 unidades. O `0,50` publicado é a variante
sem colapso e não muda.

**Alvo congelado** — modelo `delta_minimal`, corte transversal secundário:

| Variante | coef | EP | p | níveis UF |
|---|---:|---:|---:|---:|
| Balde único `RESTO` (atual) | **+1,2949** | 0,7749 | 0,0947 | 20 |
| Colapso em macrorregião | **+0,5014** | 0,2508 | 0,0456 | 23 |
| Sem colapso | **+0,5002** | 0,2414 | 0,0382 | 27 |

**Por que importa mais do que parece:** o balde infla o coeficiente 2,6× e é o
**mecanismo** pelo qual o outlier de Brasília contamina o modelo. O DF está dentro
do `RESTO` e por isso não tem efeito fixo próprio para absorvê-lo. Com UF própria,
o outlier desaparece sozinho. O achado da auditoria de que "o outlier responde por
55% do `delta_minimal`" e este item são a mesma coisa vista de dois ângulos.

**Efeito no artigo:** nenhum. `delta_minimal` não é citado em
`paper_pmme_submission.tex` — verificado por busca.

**Decisão a tomar na emenda:** adotar macrorregião, por simetria com o C1 e com o
protocolo. Registrar as três variantes em tabela, como foi feito no
`A4_tabela_07_sensibilidade_colapso_uf.csv`.

**Portão:** reproduzir os três valores acima; suíte verde; conferidor do artigo
inalterado em 190 cifras.

### Achado de 14/09/2026 — o alvo da variante a adotar NÃO reproduz

A sessão 1 parou antes de implementar, como manda o protocolo. Conferência
read-only sobre `A5_painel_T0.parquet`, replicando `build_X("minimal")`/`fit_ols`
de A5 e a função `colapsar_uf_fe` do C1 em A4:

| Variante | coef | EP | p | níveis | alvo |
|---|---:|---:|---:|---:|---|
| Balde único `RESTO` | +1,2949 | 0,7749 | 0,0947 | 20 | reproduz |
| **Colapso em macrorregião (C1 literal)** | **+0,5062** | **0,2506** | **0,0434** | **24** | **não reproduz** |
| Sem colapso | +0,5002 | 0,2414 | 0,0382 | 27 | reproduz |

**Causa.** Quatro células da amostra confirmatória não têm `macro_regiao_saude`
publicada: Oiapoque/AP e, no Espírito Santo, Cachoeiro de Itapemirim e Linhares.
É o mesmo conjunto que o relatório de A4 já rotula como `MACRO_SEM_REGIAO_SAUDE`.

O C1, em `05_estimar_atracao.py:176-180`, trata esse caso de propósito: cria um
**nível residual rotulado** para essas células, o que dá 24 níveis e +0,5062. O
alvo congelado de +0,5014 com 23 níveis só aparece quando `uf_fe` fica **ausente**
nessas quatro células e `pd.get_dummies` as descarta em silêncio, jogando-as na
categoria de referência **sem efeito fixo de UF nenhum**. Isso foi verificado
explicitamente: a variante "ausente → referência" devolve +0,5014 / 0,2508 /
0,0456 / 23 níveis, exatamente o alvo.

Ou seja, a medição congelada da variante que este item manda adotar carrega a
mesma classe de defeito que o item A-1 existe para corrigir — células sem efeito
fixo próprio. Em A4 o tratamento com 24 níveis reproduziu os alvos do C1 na
íntegra, então a assimetria está na medição de A5, não na implementação de A4.

**Decisão do autor, antes de qualquer emenda.** Qual é a definição correta do
colapso para células sem macrorregião publicada: nível residual rotulado, com 24
níveis e simetria real com o C1, ou o que a auditoria mediu, com 23 níveis e
quatro células sem efeito fixo? A diferença substantiva é pequena — +0,5062
contra +0,5014, `p` de 0,0434 contra 0,0456, mesma direção e mesma conclusão —
mas são definições de efeito fixo diferentes, e **escolher depois de ver os dois
coeficientes é o que esta fila proíbe**. Resolvida a definição, o alvo precisa ser
reemitido aqui antes de a emenda ao `35` ser escrita.

**Cobertura do alvo é parcial, e isso também é decisão.** `uf_fe` alimenta muito
mais do que `delta_minimal`: as tabelas `03`, `03b`–`03i`, `04` de leave-one-out,
`05` de influência e `06` de validação preditiva. O item congela alvo para um
único coeficiente; adotar macrorregião move todos os outros sem alvo declarado.

**Segunda implementação do colapso.** `A5_tabela_01e_amostra_uf.csv` é gerada na
linha 349 com `np.where(n_municipios<5,"RESTO",sg_uf)`, independente da linha 198.
Qualquer correção precisa tocar as duas.

**O que o achado não muda.** A manchete de A5 está a salvo: o estudo de evento
monta `uf_month` a partir de `sg_uf` direto, nas duas escalas, sem passar por
`uf_fe`. As seis cifras de A5 conferidas no artigo vêm de descritivas, não de
modelos com `uf_fe`. E `A5_tabela_11` está livre: as tabelas de A5 vão hoje até a
10.

**Bloqueio adicional, independente da decisão acima:** ver D-4. A5 não é
reexecutável neste ambiente.

### Executado em 16/09/2026 — sessão 1. Reproduz os três alvos reemitidos

**Decisão (delegada pelo autor em 16/09/2026): nível residual rotulado, 24
níveis**, a mesma definição de `colapsar_uf_fe` do C1 em A4. Fundamento e alvos
reemitidos na **emenda 2** do `35_plano_correcoes_pos_auditoria.md`, commitada
antes do código (`03ccc1c`): o princípio "município sem macrorregião forma nível
próprio, em vez de herdar uma região" foi fixado pelo C1 em 09/09/2026, antes de
qualquer coeficiente de A5 ser medido; a alternativa de 23 níveis deixa quatro
células sem efeito fixo de UF, que é a classe de defeito que este item corrige;
e as duas variantes levam à mesma conclusão. O alvo de +0,5014 / 23 níveis do
quadro acima deixou de ser alvo e ficou como medição.

Execução no modo de reestimação (D-4 parcialmente destravado), com
`colapsar_uf_fe` copiada de A4 para A5 e aplicada nas **duas** implementações
— coluna do painel e `A5_tabela_01e_amostra_uf.csv`:

| Variante | coef | EP | p | níveis | alvo da emenda 2 |
|---|---:|---:|---:|---:|---|
| Balde único `RESTO` | +1,2949 | 0,7749 | 0,0947 | 20 | reproduz |
| **Colapso em macrorregião, residual rotulado (primária)** | **+0,5062** | **0,2506** | **0,0434** | **24** | **reproduz** |
| Sem colapso | +0,5002 | 0,2414 | 0,0382 | 27 | reproduz |

As três variantes, para os cinco modelos `minimal` de corte transversal, estão
em `A5_tabela_11_sensibilidade_colapso_uf.csv`; o próprio script confere os 12
valores de `delta_minimal` como alvo congelado, ao lado dos 11 do C2. As tabelas
`03`–`03i`, `04`, `05` e `06` mudaram por consequência mecânica da definição de
efeito fixo, como a emenda previa e sem alvo prévio. O estudo de evento não
mudou: `0,0684` e `0,50` idênticos. `A5_painel_T0.parquet` não foi regravado;
sua coluna `uf_fe` traz a definição superada e é recomputada em memória.
Nenhuma cifra do artigo mudou. Três testes novos.

## A-2 · Wild cluster bootstrap que o A3 exige e nunca foi computado

**Onde:** `scripts/tema_trabalho/05_estimar_atracao.py`; o A3 exige o
procedimento quando um subgrupo tem `G < 30` e o A4 registra o aviso sem executar.

**O quê:** `G = 368` é nominal. A variância de `estrato_metropolitano` concentra
61,5% nos cinco maiores municípios, o que dá `G` efetivo ≈ **32**. Capital tem
`G = 18`.

**Alvo congelado** — Rademacher, nula imposta, `B = 1999`, sobre a especificação
**anterior ao C1** (balde `RESTO`):

| Estrato | t | p nominal | p wild |
|---|---:|---:|---:|
| metropolitano | 4,852 | 1,22e-06 | ≤ 0,0005 (0 de 1999) |
| capital | 2,694 | 0,00705 | **0,0185** |
| interior próximo | 2,934 | 0,00334 | **0,0070** |

**Atenção:** esses três valores foram medidos na especificação com balde único.
Depois do C1 a especificação primária mudou, então o bootstrap **precisa ser
recomputado na especificação vigente**, e os valores acima servem apenas como
ordem de grandeza esperada, não como alvo exato. Este é o único item da fila cujo
alvo é indicativo — registre isso na emenda.

**Efeito no artigo:** o artigo não cita `p` de capital. O efeito é sobre a
honestidade da precisão reportada, e deve entrar como nota de rodapé ou coluna
adicional, não como troca do `p` principal.

### Executado em 14/09/2026 — sessão 2. Direção reproduz; `p` de capital sai da faixa

Especificação vigente (macrorregião, 24 níveis), Rademacher, nula imposta,
`B = 1999`, semente `42` declarada na emenda antes de rodar:

| Estrato | t | p nominal | p wild | vs. alvo indicativo |
|---|---:|---:|---:|---|
| metropolitano | 4,770 | 1,84e-06 | **0,0005** (0 de 1999) | reproduz |
| capital | 4,547 | 5,45e-06 | **0,0015** (2 de 1999) | uma ordem abaixo de 0,0185 |
| interior próximo | 2,798 | 5,14e-03 | **0,0115** (22 de 1999) | ordem de 0,0070 |

`p wild >= p nominal` nos três, e os três seguem significativos a 5%.

**Capital não é erro de implementação, e isso foi verificado antes de aceitar o
número.** A mesma implementação, aplicada em diagnóstico somente-leitura à
especificação anterior ao C1, devolve `t` de 4,852 / 2,694 / 2,934 e `p` nominal
de 1,221e-06 / 7,050e-03 / 3,344e-03 — **dígito a dígito os valores congelados
neste item** — e reproduz o `0 de 1999` exato de metropolitano. Os `p` wild saem
0,0005 / 0,0225 / 0,0065 contra os 0,0005 / 0,0185 / 0,0070 medidos pela
auditoria: diferença de ruído de Monte Carlo de semente distinta, com erro-padrão
de simulação de cerca de 0,0031 nessa faixa.

O que move capital é o próprio C1, que leva o coeficiente de +0,2318 a +0,3264 e
o `t` de 2,694 a 4,547. `t` maior implica `p` de bootstrap menor. O alvo
indicativo envelheceu com a especificação, como a ressalva da emenda previa.

### Achado colateral — o `61,5%` da reauditoria não foi reproduzido

Este item e a reauditoria motivam o bootstrap com *"a variância de
`estrato_metropolitano` concentra 61,5% nos cinco maiores municípios, dando `G`
efetivo ≈ 32"*. Nenhuma das cinco definições naturais testadas devolve 61,5%:
soma de quadrados do regressor centrado por município (23,1%), quadrado da soma
do escore de cluster (51,2%), contagem de células metropolitanas (29,1%), e as
duas versões residualizadas por Frisch–Waugh–Lovell (12,8% e 31,9%).

**Não se procurou uma sexta definição que batesse.** Escolher a definição depois
de ver qual reproduz o número é o que esta fila proíbe.

**Consequência adotada:** o `61,5%` e o `G` efetivo ≈ 32 não são publicados como
resultado de A4 nem citados no artigo. O bootstrap é justificado pelo gatilho
literal do A3 — `G < 30` em subgrupo, e capital tem `G = 18`, de
`A4_tabela_01_amostra_construcao.csv`. **Não corrigido:** a definição do `61,5%`
segue em aberto na reauditoria, e resolvê-la é de quem a escreveu.

## A-3 · Efeito marginal médio do logit com contrafactual impossível

**Onde:** `scripts/tema_trabalho/05_estimar_atracao.py`, chamada a
`get_margeff(dummy=True)`.

**O quê:** o statsmodels altera apenas a coluna do estrato avaliado e deixa as
demais indicadoras de estrato no valor observado, gerando células simultaneamente
capital e metropolitana. O AME correto troca o **bloco inteiro** contra
`interior_remoto`.

**Alvo congelado** — medido na especificação com balde `RESTO`; recomputar na
vigente:

| Estrato | AME publicado | AME correto |
|---|---:|---:|
| metropolitano | 0,2928 | **0,2669** (EP 0,0554) |
| capital | 0,2501 | **0,2204** (EP 0,0944) |
| interior próximo | 0,1077 | **0,0984** (EP 0,0355) |

Superestimação de 0,9 a 3,0 p.p. Sinal, ordem e significância intactos.

**Efeito no artigo:** a Tabela A1 do apêndice publica a linha "Logit, efeito
marginal médio". O LPM é o primário e não muda.

### Executado em 14/09/2026 — sessão 2. Reproduz

Na especificação vigente, o AME passa a trocar o bloco inteiro contra
`interior_remoto`, com EP por método delta sobre a VCE cluster-robusta:

| Estrato | AME antigo | AME por bloco | Δ (p.p.) |
|---|---:|---:|---:|
| metropolitano | 0,2784 | **0,2513** (EP 0,0524) | −2,71 |
| capital | 0,3606 | **0,3403** (EP 0,0757) | −2,03 |
| interior próximo | 0,1009 | **0,0908** (EP 0,0350) | −1,02 |

Dentro da faixa de 1 a 3 p.p. do alvo, todas reduções, com sinal, ordenação,
significância e concordância com o LPM intactos. O valor antigo ficou em coluna
própria de `A4_tabela_02b_logit_AME.csv`, para auditoria. A Tabela A1 do artigo
passou de `27,8 / 6,2` para `25,1 / 5,2`; o LPM primário não mudou.

---

# Grupo B — muda artefato, não muda número publicado

## B-1 · `presentes_6m` grava censura como zero

**Onde:** `scripts/tema_trabalho/06_avaliar_provimento_cnes.py:341`,
`cross["presentes_6m"].fillna(0)`.

**Estado verificado:** em `A5_cross_section_6m.csv` a coluna é `0,0` nas 1.184
linhas, enquanto `coorte_6m_madura` é `False` nas 1.184 e `elegiveis_6m` é `NaN`
nas 1.184. É censura convertida em zero, com o denominador ainda nulo.

**Por que corrigir mesmo sem efeito estimado:** o `CLAUDE.md` proíbe explicitamente
confundir zero com censura, e este é um CSV exportado que um leitor externo pode
usar. Nenhum modelo consome a coluna — eles usam `presentes_baseline_6m`, que é
madura. Nenhum dos 13 `checks` do manifesto testa isso; acrescentar o teste faz
parte do item.

### Executado em 16/09/2026 — sessão 4

`presentes_6m` fica **NaN** nas 1.184 linhas em que `coorte_6m_madura` é `False`,
com a coluna nova `presentes_6m_censurado`; o script aborta se a coorte da
referência não for madura ou se censura for gravada como valor. O manifesto
ganha o 14º check, `presentes_6m_censura_gravada_como_nan_nao_zero`. Nenhum
modelo mudou, porque nenhum consumia a coluna. Um teste novo.

## B-2 · Relatório de A5 é código morto

**Onde:** `scripts/tema_trabalho/06_avaliar_provimento_cnes.py`, linhas ~1145–1229
montam um relatório rico (construção, trajetória, influência, LOO, validação
preditiva, limitações) que é **sobrescrito na linha ~1231** antes de qualquer
escrita.

**Consequência:** o `A5_relatorio_diagnostico.md` publicado não tem seção de
influência nem de robustez. O bloco morto ainda carrega texto obsoleto — cita
`13.92 (202509 baseline)` quando o baseline é `202506`, "FE curso (16)" quando são
10, e "cluster municipio (G=368)" quando é 295.

**Decisão:** ou remover o bloco morto, ou promovê-lo. Recomendo promovê-lo, agora
que o LOO e a sensibilidade de referência existem como artefato — o relatório é
justamente onde um leitor procura essa fragilidade.

### Executado em 16/09/2026 — sessão 4. Promovido, com o texto obsoleto corrigido

O bloco morto (11.250 caracteres) foi removido e suas seções foram promovidas
ao relatório publicado com os números lidos das tabelas gravadas, não do texto
antigo: construção, maturidade e censura; trajetória agregada; influência e
robustez (LOO de UF e curso, leave-one-município, validação preditiva);
multiplicidade; limites. O que o bloco morto dizia de errado não foi promovido
— `13.92 (202509 baseline)`, `FE curso (16)`, `G=368` —, e o relatório passa a
declarar referência 202506, 10 cursos e 295 municípios na amostra
confirmatória. Um teste garante que o texto obsoleto não reaparece.

## B-3 · Manifesto de reprodução de A6 não reproduz

**Onde:** `output/tema_trabalho/A6_manifesto_reproducao.json`, campo
`comandos_reproducao`.

**Estado verificado:** lista caminhos Windows (`.venv\Scripts\python.exe`) enquanto
`versoes.platform` registra Linux; começa em `02_reconciliar_funil_ciclo1.py`,
omitindo A1 e **toda a aquisição**, inclusive
`scripts/aquisicao/05_integrar_painel_analitico.py`, que constrói o insumo de A5.
Não hasheia `A5_painel_T0.parquet`, que é o dataset de estimação, nem
`data/pmm_especialistas_nominal.csv`, `data/ivs_ipea_2010_municipios.csv` ou
`manifesto_cnes_26_competencias.json`.

**Nota de ambiente:** o comando correto neste repositório exige Python ≥ 3.12; ver
a seção de ambiente do `README.md`.

### Verificado em 14/09/2026 — regenerar o manifesto hoje o piora

`07_red_team_sintese.py` foi executado no ambiente documentado, com Python
3.13.12 e numpy 2.5.2. Ele roda sem erro, mas **remove em silêncio** a entrada de
`output/painel_municipio_curso_mensal.parquet` de `hashes_entradas_e_artefatos`,
porque o arquivo não existe nesta máquina (item D-4). O registro de proveniência
some sem nenhum aviso, e o manifesto fica mais pobre do que o publicado.

Isso acrescenta um requisito ao item, que antes era só de conteúdo: o gerador
deve distinguir **insumo ausente** de **insumo inexistente no desenho**, gravando
a entrada com marca explícita de ausência e o motivo, em vez de omiti-la. Sem
isso, qualquer reexecução em ambiente sem os microdados degrada a auditoria.

O mesmo cuidado vale para os dois documentos de auditoria que o script regrava,
`09_red_team_atracao_provimento.md` e `09_matriz_afirmacao_evidencia_limite.md`:
eles mudam de hash a cada execução porque carregam a data de referência.

### Executado em 14/09/2026 — sessão 5, commit `2375267`

Corrigido **antes** de o gerador ser rodado por qualquer outro motivo, para que
as demais correções da sessão não levassem a degradação junto.

`insumos_declarados()` passa a listar cada insumo com o papel que cumpre no
desenho, e `hashear_insumos()` distingue os dois casos: insumo do desenho ausente
do disco continua tendo entrada, com `sha256: null`, `presente: false` e
`motivo_ausencia`; insumo que não faz parte do desenho simplesmente não aparece
na lista. O manifesto ganha também `insumos_ausentes`, que hoje traz exatamente
`output/painel_municipio_curso_mensal.parquet`.

Os demais pontos do item: os comandos deixam de ser caminhos Windows e passam a
`.venv/bin/python`; a sequência deixa de ser mantida à mão e é **derivada da
lista `STEPS` de `run_all.py` por leitura de AST**, então cobre A1 e toda a
aquisição, inclusive `scripts/aquisicao/05_integrar_painel_analitico.py`, e não
pode divergir do ponto de entrada; passam a ser hasheados `A5_painel_T0.parquet`,
`data/pmm_especialistas_nominal.csv`, `data/ivs_ipea_2010_municipios.csv` e
`output/aquisicao/manifesto_cnes_26_competencias.json`. Novo bloco
`ambiente_exigido` registra Python ≥ 3.12 e o interpretador.

Três testes novos em `tests/test_red_team_a6.py`.

## B-4 · Nota aritmética errada no manifesto da tipologia

**Onde:** `output/tema_trabalho/manifesto_tipologia_territorial.json`,
`rm_detalhe.nota`.

**Estado verificado:** o texto diz *"Strict corrige para 1331 únicos (1316
nacionais após remover 27 capitais duplas)"*. Apenas **25** das 27 capitais
pertencem a RM/RIDE strict — Rio Branco e Campo Grande não pertencem. O correto é
`1331 − 25 = 1306`, que é exatamente o que o parquet publica.

**Restrição:** a tipologia é **congelada**. Corrigir a nota exige reexecutar
`03_construir_tipologia_territorial.py`, o que regrava o manifesto e quebra a
cadeia de hashes a jusante, obrigando a reexecutar A3–A6. Como é só uma frase,
avalie se compensa; a alternativa é registrar a errata em documento, sem tocar no
artefato congelado. **Recomendo a errata.**

## B-5 · Multiplicidade nunca tratada em A5

**Onde:** `06_avaliar_provimento_cnes.py:122` define `bh_fdr`, que nunca é
chamada; `q_fdr_atracao` sai `NaN` em todas as tabelas.

São 25 coeficientes de evento mais cerca de 12 modelos secundários sem qualquer
discussão de multiplicidade. A4 aplica FDR entre estratos; A5 não aplica nada.

### Executado em 16/09/2026 — sessão 4. Famílias declaradas antes de ver os q

Famílias: (i) os 25 coeficientes de evento de cada par amostra–escala, com
Benjamini–Hochberg nas colunas `q_fdr_bh` e `q_fdr_bh_gl_fe` das tabelas 07 e
08; (ii) o coeficiente de atração nos cinco desfechos de corte transversal,
separadamente para `minimal` e `full`, na coluna `q_fdr_atracao` das tabelas 03
a 03e, que antes saía `NaN`. Registro em `A5_estimativas_provimento.json`,
bloco `multiplicidade`.

Resultado, lido dos artefatos: na amostra confirmatória, o coeficiente de
março/2026 na **escala proporcional** tem `q = 0,0034` e sobrevive à família de
25; o coeficiente em **nível** tem `q = 0,364` e **não sobrevive** — mais uma
razão, independente da composição de cursos, para o nível ser sensibilidade e
não forma primária, como o C2 do plano `35` já decidira. No corte transversal
`minimal`, cobertura (`q = 0,024`) e estoque (`q = 0,047`) ficam abaixo de 0,05;
`delta` (`q = 0,067`) e entradas (`q = 0,067`) não. Nenhum desses coeficientes
entra no artigo. Um teste novo.

## B-6 · Rótulos e artefatos enganosos

Três itens pequenos, do mesmo tipo, que podem ir num commit só:

- `A5_tabela_03f` tem `espec = "OLS_delta_T0alt_202507_202601_minimal"` mas as
  constantes são `202509 → 202603`. O valor publicado (0,6409; `p = 0,110`) é o da
  janela real; o rótulo descreve outra.
- `portao_denominador.json`, campo `celulas_confirmacao_acima_vagas_imediatas`:
  publica **10** porque filtra `immediate > 0`, mas o nome promete a contagem
  literal, que é **185 células** e **221 confirmações excedentes**. Nenhum
  documento publica o 10.
- `manifesto_tipologia_territorial.json`, `n_celulas_funil_A1` conta linhas
  (3.057), não células distintas (**2.128**; 929 aparecem nas duas chamadas).
  Mesma restrição de congelamento do B-4.

### Executado em 16/09/2026 — sessão 4. Um rótulo corrigido, dois em errata

- `A5_tabela_03f`: o rótulo passa a ser derivado das constantes,
  `OLS_delta_T0alt_202509_202603_minimal`, e o comentário do código que dizia
  `202507 -> 202601` foi corrigido. Valor inalterado.
- `portao_denominador.json`: **errata E-3** em
  [`../auditorias/14_erratas_artefatos_congelados.md`](../auditorias/14_erratas_artefatos_congelados.md).
  Reproduzido: 185 células e 221 confirmações excedentes; o `10` publicado é o
  subconjunto com vaga imediata maior que zero. Regravar exigiria reexecutar
  A3–A6 pelo hash, o mesmo bloqueio do C-4.
- `manifesto_tipologia_territorial.json`: **errata E-4**. Reproduzido: 3.057
  linhas célula–chamada, 2.128 células distintas, 929 nas duas chamadas.
  Tipologia congelada; decisão delegada pelo autor: errata.

## B-7 · `sg_uf` de tipo misto na tipologia

`matriz_tipologia_territorial.parquet` tem 31 valores distintos de `sg_uf` para 27
UFs: 27 códigos numéricos vindos da malha, mais 4 siglas preenchidas do REGIC para
os cinco municípios criados após o Censo 2010, que também ficam com `nome_uf`
nulo. Nenhum dos cinco está na população A1, então nenhum resultado é afetado.

Efeito visível: `concentracao.por_uf_top10_populacao_A1` lista `{"31": 150, "52":
44, "35": 35, …}`, códigos apresentados como se fossem siglas. Mesma restrição de
congelamento do B-4.

---

# Grupo C — documentação e linguagem

## C-1 · O 30,3% é da primeira chamada, não do ciclo

**Onde:** `docs/06_execucao/32_sintese_A6_resumo_intro_metodos_conclusao.md:9`.

**Estado verificado:** o texto diz *"a implementação do **primeiro ciclo** … 30,3%
das células"*. O 30,3% (393/1.295) é do quadro da **primeira chamada**. Pelo ciclo
1 inteiro são **461/1.295 = 35,6%**: 68 células com desfecho zero na primeira
chamada receberam homologado novo na segunda, somando 84 pessoas.

O `paper_pmme_submission.tex` está correto e explícito ("do quadro da primeira
chamada"). O defeito é só deste documento — que é gerado por
`07_red_team_sintese.py`, então a correção é no gerador.

**Bônus:** o mesmo documento usa ponto decimal (`27.9`) em texto português, onde o
resto do projeto usa vírgula.

### Executado em 14/09/2026 — sessão 5, commit `093fb44`

Números conferidos nos artefatos antes de escrever, sobre
`matriz_funil_ciclo1.parquet`: primeira chamada **393 / 1.295 = 30,3%**; ciclo 1
inteiro **461 / 1.295 = 35,6%**; **68** células sem desfecho na primeira chamada
receberam homologado novo na segunda, somando **84** pessoas. Reproduz o alvo.

Corrigido no gerador, não no arquivo. `prevalencia_atracao()` calcula as duas
prevalências a partir do artefato versionado, então nenhum dos dois números fica
escrito à mão; o resumo e a linha correspondente da matriz publicam as duas com
o rótulo de qual é qual. O `paper_pmme_submission.tex` já estava correto e não
foi tocado.

Bônus do item: `num()` passa a formatar em convenção brasileira e `pct()` passa
por ele, então a síntese, o red team e a matriz saem com vírgula decimal. Dois
testes novos.

## C-2 · Afirmação falsa sobre linhas sub judice

O artigo e `docs/05_identificacao/17_plano_causal_publico_cutoff_escore.md` afirmam
que linhas sub judice são descartadas "nas publicações que trazem esse marcador".
Falso para o ciclo 1: o marcador existe na coluna 17 (`Unnamed: 16`, 1 linha) e o
código nunca o lê; só `read_support_2026` filtra `SITUACAO`, e só para 2026.

Numericamente imaterial — a linha cai num par de placebo e na amostra de empates,
e removê-la move o placebo de `0,000` para `+0,034`. Mas a afirmação é falsa e
precisa ser corrigida ou executada.

### Executado em 14/09/2026 — sessão 5, commit `8c4d3e9`. Caminho: corrigir a afirmação

Verificado nos insumos, sem alterar nada em `data/`:

| Publicação | marcador sub judice | o código lê? |
|---|---|---|
| `2025_ciclo1_chamada1_alocacao_retificada_subjudice.xlsx` | 1 linha em `Unnamed: 16` (coluna 17 de 17) | **não** — `read_call1` usa as colunas 0,1,4,6,7,8,9,10,11,12,13 |
| `2025_ciclo1_chamada2_classificacao_final.xlsx` | nenhum, em nenhuma célula | n/a |
| publicações de 2026 | coluna `SITUACAO` | sim — `read_support_2026` filtra |

**Decisão: corrigir a afirmação, não executar o filtro.** Executá-lo mudaria
número publicado e mexeria na amostra congelada de A8, que esta fila proíbe
alterar e que exigiria emenda prévia; a sessão 5 só carrega itens dos grupos B e
C. Como a diferença é imaterial, executar compraria nada ao custo de mexer em
amostra congelada. Corrigir o texto descreve exatamente o que o código faz.

O artigo passa a dizer que o descarte vale para as publicações de 2026 e que o
recorte do ciclo 1 não o faz. O `17_plano_causal_publico_cutoff_escore.md` perde
o bullet de "O que fortalece o desenho" e ganha o registro em "O que impede rigor
alto". Não foi afirmado em que par a linha cai: isso não é verificável a partir
dos artefatos publicados, que são agregados, e a medição correspondente é da
reauditoria, não deste repositório. Um teste novo amarra a afirmação ao código.

## C-3 · Intervalo de confiança fora do espaço de parâmetros

`A8_tabela_02`, linha `2025_C1_CH2` de homologação, traz
`ic95_convencional_superior = 1,2618`, fora de `[-1, 1]`. A coluna e a prosa já
rotulam "convencional" e a seção 5 do relatório diz que os intervalos `t` não
resolvem a discretização, mas nenhuma ressalva sinaliza **este** valor específico
e nenhum intervalo exato é oferecido ao lado.

### Executado em 14/09/2026 — sessão 5, commit `e7fc9e9`

São **duas** as linhas fora do espaço, não uma: `2025_C1_CH2` / `gap_1_ac` em
`homologacao_mesma_celula` e em `homologacao_qualquer_local`, ambas com
`ic95_convencional_superior = 1,2618`.

O intervalo exato condicional — Clopper–Pearson sobre os pares discordantes, o
análogo exato do teste de McNemar que a tabela já usa — é **−0,0364 a 0,8333**.
Além de caber no espaço de parâmetros, ele **cobre o zero**, enquanto o
convencional não cobre; isso é coerente com o `p` exato de `0,0625` já publicado.
A leitura correta dessas duas linhas é de efeito direcional impreciso sobre seis
pares, e não de efeito estabelecido.

Publicado **ao lado**, sem tocar em A8: `scripts/tema_trabalho/09b_intervalos_exatos_escore.py`
lê `A8_tabela_02` e `A8_tabela_03` já publicadas e grava
`output/tema_trabalho/A8_tabela_06_intervalos_exatos.csv`. Amostra, desfecho e
estimador de A8 seguem intactos. Ressalva escrita em
[`docs/auditorias/14_erratas_artefatos_congelados.md`](../auditorias/14_erratas_artefatos_congelados.md), errata E-1.

### Achado colateral — A8 não reproduz byte a byte

No ambiente documentado, reexecutar `09_estimar_cutoff_escore_estrito.py` altera
seis artefatos de A8: as colunas de intervalo de confiança a partir do **15º
dígito significativo** (`0,41394184915555393` contra `0,413941849155554`) e o
PNG, de 63.929 para 75.121 bytes. Diferenças, erros-padrão, contagens de pares,
discordantes e `p` exatos são idênticos dígito a dígito, e o conferidor do artigo
segue aprovando.

**Duas execuções consecutivas agora são idênticas entre si**, incluindo o PNG: o
script é determinístico neste ambiente, e o que não bate é o artefato
versionado, gravado sob outro estado de biblioteca. **Não regravado de
propósito** — fazer os artefatos baterem seria ajustar até fechar. O que deixa de
valer é a generalização de que o repositório inteiro reproduz byte a byte sob o
ambiente documentado: verificada para A4 e A1, **falsa para A8**. Regravar A8 e
reemitir os hashes é decisão do autor.

## C-4 · Portão de A1 apresentado como teste

`02_reconciliar_funil_ciclo1.py:476` — `vacancy_id_available = False` e
`immediate_capacity_all_calls = False` são literais. `APROVADO_VAGA` e `REPROVADO`
são inatingíveis por construção. As premissas são factualmente corretas — não
existe coluna de identificador de vaga em nenhum dos oito insumos —, mas o JSON as
publica em `criterios` como se tivessem sido testadas contra os dados.

**Duas saídas:** derivar as duas constantes de uma checagem real de esquema, ou
renomeá-las como asserções documentais. A segunda é honesta e barata.

### Tentado e revertido em 14/09/2026 — sessão 5, commit `1893e95`. **BLOQUEADO por D-4**

A saída recomendada — renomear as duas constantes como asserções documentais —
foi implementada, separando `criterios` em `criterios_testados` e
`premissas_documentais`, e **revertida**. Motivo: ela muda o SHA-256 de
`output/tema_trabalho/portao_denominador.json`, que está fixado como hash de
entrada em `registro_pre_analise_atracao.json` (A3),
`A4_estimativas_atracao.json`, `A5_estimativas_provimento.json` e
`A5_manifesto_maturidade_censura.json`. Três testes de hash falharam ao tentar.

Reparar a cadeia exigiria reexecutar A3, A4 e A5, e **A5 não é regravável sem os
microdados do CNES** (D-4). O item é barato em código e caro na cadeia de
proveniência, ao contrário do que a recomendação original supunha.

**O que ficou.** A ressalva no ponto exato do código, dizendo que as duas são
premissas documentais e não testes e que `APROVADO_VAGA` é inatingível por
construção, mais um teste que fixa o estado atual para a pendência não se
perder. A correção do JSON continua pendente e **entra junto da primeira
reexecução legítima de A5**, quando D-4 for desbloqueado.

Confirmado após a reversão: A1 reexecuta byte a byte idêntico.

## C-5 · MDE por estrato de A3 com fórmula de proporção única

O `mde_global` foi corretamente rerrotulado, mas o bloco `por_estrato` continua
publicando `mde_80_pp_p50/p30` calculados com a fórmula de **proporção única** e
sem rótulo. O docstring ainda afirma *"MDE bilateral para diferença de proporções
vs baseline (aprox. 2*SE)"* — errado duas vezes: não é EP de diferença e o
multiplicador é 2,80, não 2. E `mde_diferenca_vs_resto_p50` usa o DEFF da amostra
inteira para o grupo complementar, em vez do DEFF do próprio complemento.

Nada disso entra no artigo, que usa só os contrastes, esses corretos. **Restrição
de congelamento:** A3 é protocolo congelado; prefira errata a reexecução.

### Executado em 14/09/2026 — sessão 5, commit `e7fc9e9`. Errata, não reexecução

Os três defeitos confirmados por leitura do código e reprodução aritmética:
o bloco `por_estrato` usa `mde_proporcao`, cujo EP é o de **uma** proporção;
o multiplicador é `Z_ALPHA + Z_POWER = 2,8016`, não 2; e
`mde_diferenca_vs_resto_p50` passa `deff2 = 1,126`, o DEFF da amostra inteira, e
não o do complemento. Reproduzido à mão: capital,
`sqrt(0,25/73)·sqrt(1,153)·2,8016 = 0,176`, exatamente o publicado.

Como o item recomenda, **errata em vez de reexecução**: o docstring de
`mde_proporcao` e um comentário no ponto exato do código foram corrigidos,
porque não alteram saída nenhuma, e a errata está em
[`docs/auditorias/14_erratas_artefatos_congelados.md`](../auditorias/14_erratas_artefatos_congelados.md), E-2.
Os artefatos de A3 seguem intactos, com hashes `91fa9055…` e `eb2bf812…`
conferidos após a edição. O artigo usa só os contrastes versus interior remoto,
que estão corretos.

## C-6 · MDE ex-ante é otimista contra o modelo estimado

| Estrato | EP realizado | MDE ex-post | MDE ex-ante do A3 | Otimismo |
|---|---:|---:|---:|---:|
| capital | 0,08602 | 24,1 p.p. | 19,5 p.p. | 23,8% |
| metropolitano | 0,06064 | 17,0 p.p. | 13,7 p.p. | 23,6% |
| interior próximo | 0,04315 | 12,1 p.p. | 11,9 p.p. | 1,6% |

A fórmula analítica ignora que os efeitos fixos de curso e UF absorvem variação do
próprio estrato. O artigo cita 13,7 p.p. como MDE do contraste metropolitano; o
número que o modelo entrega é 17,0. Medido na especificação anterior ao C1;
recomputar.

### Executado em 14/09/2026 — sessão 2. Reproduz

Recomputado na especificação vigente, com `MDE = 2,801585 x EP realizado`:

| Estrato | EP realizado | MDE ex-post | MDE ex-ante A3 | Otimismo |
|---|---:|---:|---:|---:|
| capital | 0,07179 | 20,1 p.p. | 19,5 p.p. | 3,4% |
| metropolitano | 0,05855 | **16,4 p.p.** | 13,7 p.p. | **19,4%** |
| interior próximo | 0,04312 | 12,1 p.p. | 11,9 p.p. | 1,5% |

Direção igual à da medição anterior ao C1 — ex-post maior que ex-ante nos três.
O otimismo de capital cai de 23,8% para 3,4% porque o C1 reduziu o EP de capital;
o de metropolitano permanece e é o caso relevante. O ex-ante **não** foi apagado
nem recalculado, e A3 não foi reexecutado. O artigo passa a citar os dois.

## C-7 · Ameaças ausentes do red team

Quatro, com o que já foi medido:

1. **Placebo.** Nenhum foi rodado. O óbvio é viável no próprio painel: células
   *sem* atração em municípios *com* atração contra municípios sem. **Medido:
   0,092 (EP 0,303; `p = 0,761`), pré-`F` 0,81 — o placebo passa**, o que reforça o
   achado. Falta publicá-lo.
2. **Heterogeneidade de pré-tendência.** O `p = 0,420` agregado esconde que nos
   cursos que carregam o resultado em nível o teste conjunto pré **rejeita**: curso
   14 `F = 2,46` (`p = 0,007`), curso 16 `F = 11,90` (`p < 0,001`), curso 2
   `F = 6,85` (`p < 0,001`). Subamostras pequenas, VCE instável — sinal de alerta,
   não prova, mas nada nos artefatos menciona.
3. **Deslocamento entre municípios.** O `CLAUDE.md` exige separar expansão líquida
   de deslocamento. O painel tem `region_id` e existe um painel regional, mas
   nenhum teste de se o ganho do município atraído sai de vizinhos da mesma região
   de saúde.
4. **Forma funcional.** Parcialmente resolvido pelo item C2 do plano `35`, que
   promoveu a escala proporcional. Falta o red team refletir isso: ele ainda diz
   "vulnerável a caudas" quando o diagnóstico correto é "o **nível** é frágil à
   composição; a **proporção** não é".

### Executado em 14/09/2026 — sessão 3, commit `a8107cb`. **Só a quarta ameaça**

**Por que a sessão 3 rodou junto da 5.** A sessão 4 está bloqueada por D-4. Das
quatro ameaças deste item, as três primeiras exigem regravar artefato de A5 e
ficam bloqueadas pelo mesmo motivo; só a quarta é executável, e ela divide o
gerador `07_red_team_sintese.py` com os itens da sessão 5. Juntar as duas foi o
tratamento previsto para bloqueio, não um furo de fila.

**Quarta ameaça — forma funcional.** O red team dizia "vulnerável a caudas".
Depois do item C2 do plano `35`, que promoveu a escala proporcional a primária,
o diagnóstico correto é outro, e o leave-one-curso-out já publicado em A5 o
sustenta:

| escala | amostra completa | sem o curso 14 | oito cursos estritos |
|---|---:|---:|---:|
| nível | 0,50 | 0,20 (`p = 0,366`) | 0,12 (`p = 0,608`) |
| proporcional | 0,068 (`p = 0,0002`) | 0,059 (`p = 0,004`) | 0,057 (`p = 0,010`) |

Ou seja: **o nível é frágil à composição de cursos e a proporção não é.** A nova
seção do red team publica isso com os números lidos do artefato, e a conclusão
da síntese acompanha. Acrescentada também a seção "Ameaças que este red team não
testou", que nomeia as três bloqueadas e aponta para este item e para D-4.

**As três primeiras ameaças continuam bloqueadas por D-4.** Placebo,
heterogeneidade de pré-tendência e deslocamento entre municípios exigem regravar
artefato de A5, e `output/painel_municipio_curso_mensal.parquet` não existe nesta
máquina. Os valores citados nos itens 1 e 2 acima — o placebo de `0,092`
(`p = 0,761`) e os `F` por curso — **são medição da reauditoria independente, não
artefato deste repositório**, e não foram reproduzidos aqui. Nenhum deles foi
publicado em artefato, e nenhum teste novo foi inventado para substituí-los.

Dois testes novos, um deles amarrado ao próprio `A5_estimativas_provimento.json`,
para que a afirmação caia se o artefato mudar.

### Protocolo congelado em 16/09/2026, antes da execução — as três ameaças restantes

Com D-4 parcialmente destravado (`da4d6f7`), as três ameaças passam a ser
executáveis a partir de `A5_painel_T0.parquet`. O que segue foi escrito
**antes** de rodar qualquer modelo; o script novo
`scripts/tema_trabalho/06b_ameacas_a5_placebo_pretendencia_deslocamento.py`
implementa exatamente isto, confere o hash do painel contra o A6 e grava
`A5_tabela_12`, `A5_tabela_13`, `A5_tabela_14` e `A5_ameacas_c7.json`.

Comum aos três: amostra confirmatória de 587 células; as duas escalas (nível e
`log1p`); efeitos fixos de célula, curso–mês e UF–mês; erros agrupados por
município; referência 202506; inferência citada na convenção `_gl_fe`. Nenhuma
subamostra, janela ou estimador será reescolhido depois de ver os resultados.

1. **Placebo — células sem atração em municípios com atração.** Amostra: células
   confirmatórias com `atracao_muni = 0`. "Tratamento" placebo: o município
   tem atração em **alguma** das suas 1.184 células (qualquer curso). Se o
   coeficiente pós for distinguível de zero, choques municipais correlacionados
   com atrair — e não a atração da própria célula — explicam parte do resultado
   principal; se for indistinguível de zero, o resultado principal é da célula.
   Comparação declarada: a reauditoria mediu `0,092` (EP `0,303`; `p = 0,761`)
   e pré-`F` `0,81` em nível.
2. **Heterogeneidade de pré-tendência por curso.** Para cada um dos dez cursos
   confirmatórios, o mesmo estudo de evento dentro do curso (curso–mês colapsa
   em mês), com o teste conjunto dos doze coeficientes pré e o coeficiente de
   202603. Regra fixada agora: os cursos com pré-`p < 0,05` na escala
   proporcional são listados, e o coeficiente de 202603 é reportado, como
   sensibilidade, **excluindo-os** — nas duas escalas. Comparação declarada: a
   reauditoria mediu curso 14 `F = 2,46` (`p = 0,007`), curso 16 `F = 11,90`,
   curso 2 `F = 6,85`, em subamostras pequenas e com VCE instável.
3. **Deslocamento dentro da região de saúde.** Dois testes. (a) *Transbordo
   sobre células sem atração:* amostra de células confirmatórias com
   `atracao_muni = 0`; exposição = existe **outro** município da mesma
   `region_id`, dentro dos 368 do painel, com atração no **mesmo curso**;
   coeficiente pós negativo indica deslocamento a partir de vizinhos, zero não
   o indica. (b) *Oferta líquida regional:* estoque somado por região–curso–mês
   sobre os municípios do painel; tratamento = a região–curso tem ao menos uma
   célula com atração; efeitos fixos região–curso, curso–mês e UF–mês; cluster
   por região. Se o ganho municipal fosse só realocação dentro da região, o
   coeficiente regional seria zero; se houver expansão líquida, positivo.
   Limite declarado: o painel só contém os municípios do quadro, então
   "vizinho" é vizinho **dentro do quadro**; o teste é obrigatório pelo
   `CLAUDE.md`, mas não vê municípios fora da oferta.

Depois de rodar, o red team (`07_red_team_sintese.py`) troca a seção "Ameaças
que este red team não testou" por uma seção com os resultados lidos do JSON, e a
limitação (a) fica registrada nela. O achado colateral do B-5 — o nível não
sobrevive ao FDR da família de 25 e o proporcional sobrevive — entra na seção
de forma funcional.

### Executado em 16/09/2026 — sessão 3 concluída. Protocolo `1fab57d`, código depois

Script `06b_ameacas_a5_placebo_pretendencia_deslocamento.py`, no `run_all.py`
entre A5 e A6; artefatos `A5_tabela_12` a `A5_tabela_14` e `A5_ameacas_c7.json`,
hash do painel conferido contra o A6. Inferência na convenção `_gl_fe`.

| Ameaça | Resultado (março/2026) | Leitura pré-especificada |
|---|---|---|
| **Placebo** — 372 células sem atração: 198 em município com atração, 174 em município sem | nível `+0,063` (EP `0,309`; `p = 0,837`; pré-F `1,57`, `p = 0,102`); proporcional `+0,0007` (`p = 0,980`) | **passa** nas duas escalas; a reauditoria medira `0,092` (`0,303`; `0,761`) em nível — mesma ordem e mesma leitura |
| **Pré-tendência por curso** — dez cursos | rejeita a 5% na proporcional nos cursos **2 e 16**; em nível, **2, 14 e 16** (os mesmos da reauditoria). Posto incompleto da covariância das restrições nos cursos 3, 5, 12, 13, 15 e 16: F não confiável ali. Regra fixada: excluindo 2 e 16, proporcional `+0,0810` (EP `0,0236`; `p = 0,0007`), nível `+0,579` (`p = 0,058`), 488 células | heterogeneidade existe e fica publicada; não desfaz a proporcional; o nível é o que depende de composição |
| **Deslocamento (a)** — transbordo sobre 372 células sem atração, 70 expostas a vizinho do quadro com atração no mesmo curso | nível `+0,276` (`p = 0,542`); proporcional `−0,0105` (`p = 0,741`) | sem sinal de deslocamento a partir dos vizinhos observados |
| **Deslocamento (b)** — oferta líquida por região–curso, 173 regiões, 449 região–curso (64 com mais de um município do painel), cluster por região | nível `+0,773` (EP `0,238`; `p = 0,001`); proporcional `+0,0502` (EP `0,0179`; `p = 0,006`); pré-F `0,79` (`p = 0,663`) | a oferta regional agregada também sobe: não é pura realocação dentro do quadro |

**Limite declarado e mantido:** o painel só contém os 368 municípios do quadro;
"vizinho" é vizinho dentro do quadro, e deslocamento a partir de municípios
fora da oferta não é observável. A leitura de tudo continua associativa.

O red team troca a seção "Ameaças que este red team não testou" pela seção
"Placebo, pré-tendência por curso e deslocamento (C-7)", com os números lidos
do JSON, e a seção de forma funcional passa a citar o FDR (`q = 0,0034` na
proporcional, `0,364` em nível). Veredito geral e conclusão da síntese
atualizados pelo gerador. Dois testes novos, mais o teste do red team
reescrito para exigir os resultados em vez da ausência. O C-7 está
**concluído**.

## C-8 · Assinatura de CPF não comparável entre máscaras

Os homologados mascaram as posições 4–7 do CPF (`711XXX14162`); a classificação
final mascara 6–9 (`669.07X.XXX-00`). A assinatura "3 primeiros + 4 últimos" só
coincide entre os dois formatos de homologado. Hoje inerte — o pareamento
verificado é 299/299 com zero discordância —, mas se alguém usar a assinatura para
cruzar homologados com a classificação final, o pareamento sai errado. Vale um
comentário no código e um teste que falhe se o uso se espalhar.

### Executado em 14/09/2026 — sessão 5, commit `1893e95`

Máscaras verificadas nos próprios insumos, sem nada persistido:

| Publicação | máscara | dígitos visíveis | `digits[-4:]` |
|---|---|---|---|
| homologados Ch1 | `999XXX99999` | 1-3, 7-11 | posições 8,9,10,11 |
| homologados Ch2 | `999.XXX.X99-99` | 1-3, 8-11 | posições 8,9,10,11 |
| classificação final Ch2 | `999.99X.XXX-99` | 1-5, 10-11 | posições 4,5,10,11 |
| alocação Ch1 | `99999XXXX99` | 1-5, 10-11 | posições 4,5,10,11 |

O item mencionava só a classificação final; **a alocação da Ch1 está na mesma
família incompatível**, e também recebe `cpf_position`. Uma linha dela tem padrão
`EBE99XXXXC9`, com três dígitos, e a guarda `len >= 7` já devolve string vazia.

Confirmado que hoje é inerte: o único cruzamento é `homolog_c1` contra
`homolog_c2`, com **299 de 299** e **zero discordância** entre nome e assinatura.

`cpf_signature_34` ganha a tabela acima e a ressalva de que só vale entre
homologados. O teste novo percorre a AST do script e falha se
`_cpf_signature_34` for lido a partir de qualquer quadro fora de
`{result, homolog_c1, homolog_c2}` — conferido que dispara ao simular o uso
espalhado. Um segundo teste garante que nem a assinatura nem o nome chegam a
artefato.

## C-9 · `delta_full` e `estoque_6m_full` são o mesmo estimador

Ambos reportam `0,091608 / 0,345622 / 0,790969` porque a especificação `full`
inclui `estoque_baseline`; por Frisch–Waugh–Lovell são idênticos. O JSON os
apresenta como duas evidências.

### Executado em 16/09/2026 — sessão 4

O JSON passa a declarar `equivalente_a` nos dois modelos e uma
`nota_equivalencia`; as tabelas `03` e `03b` ganham a coluna `nota` com a mesma
explicação; o script aborta se os dois coeficientes deixarem de ser idênticos; o
relatório os conta como uma evidência. Os valores não mudaram. Um teste novo.

---

# Grupo D — bloqueado

## D-1 · Compilação do artigo — `DESBLOQUEADO em 14/09/2026`

TeX Live foi instalado no ambiente e o artigo **compilou pela primeira vez**:
12 páginas, zero referência indefinida, as 16 chaves de bibliografia usadas e
definidas, e as três figuras encontradas nos caminhos declarados. O conferidor
`10_conferir_numeros_artigo.py` seguiu aprovando as 190 cifras.

A compilação revelou um defeito que a validação estrutural não pegava: a tabela
`tab:principal` estourava a margem em 59,43 pt. Corrigida para `\footnotesize`
com `\tabcolsep` de 4 pt; a compilação passa a sair sem nenhum `Overfull \hbox`.

**A revisão de provas — leitura do PDF pelo autor — continua pendente e é do
autor.** O que deixa de ser verdade é a impossibilidade de compilar.

## D-2 · Ciclo 3

- **C3-02B** parou em 673 de 675 manifestos porque `RDAC2606.dbc` e `RDRR2606.dbc`
  não estavam no FTP oficial em 31/08/2026. **Não imputar zeros.** Repetir só
  quando ambos aparecerem.
- **C3-05** aguarda a competência CNES `202703` publicada, completa e madura.
- **C3-06** aguarda `T0+12m`, em setembro de 2027.

## D-3 · Pedido do escore administrativo de IVS

O pacote está pronto e a justificativa foi reescrita pelo item C3 do plano `35` em
torno da impossibilidade demonstrada. **O envio é decisão do autor** — escolha de
canal e autorização. Nenhum item desta fila depende disso, mas a pergunta
declarada do projeto depende inteiramente.

### O pedido ficou mais preciso em 14/09/2026

A leitura do edital mudou o que se deve pedir. Não é "o escore de IVS": a
cláusula 11.1.4 já publica a regra sobre o IVS, e ela é o **piso** da bolsa. O
que promove 177 municípios acima desse piso é o critério de **localização** da
cláusula 11.1.3, definido no **Anexo IV**. Pedir o escore de IVS traria algo que
já se tem.

Itens a pedir, em ordem de utilidade:

1. **Anexo IV do Edital SGTES/MS nº 3/2025**, com a faixa de atração por
   município e a data de vigência — é o documento operativo citado pelo próprio
   edital e ausente do repositório.
2. **Os critérios de localização** da cláusula 11.1.3: quais são, como se
   combinam com a categoria de IVS e se a promoção é de uma faixa ou mais.
3. **A vintagem e a fonte do IVS** efetivamente usada, com a regra de
   arredondamento.
4. **Folha de pagamento da bolsa**, se o alvo incluir o valor recebido e não
   apenas o anunciado — sem ela, R1 identifica intenção de tratar da oferta.

Os três primeiros destravam R1; o quarto separa dose de oferta.

## D-4 · Microdados do CNES ausentes do repositório

`output/aquisicao/cnes_mensal/` não existe, e `data/raw/cnes/` é gitignored. A
cadeia auditável de A5 começa no painel já integrado, e `run_all.py` falharia em
`05_integrar_painel_analitico.py` num clone limpo. Consequências não verificáveis
hoje: `co_municipio_gestor` (que pode atribuir estabelecimento de gestão estadual
a outro município, deslocando estoque), a expansão CBO→curso, e
`CO_PROFISSIONAL_SUS` como chave longitudinal.

### Confirmado em 14/09/2026 — este item bloqueia a fila, não só a auditoria

Verificado diretamente: `output/painel_municipio_curso_mensal.parquet` não existe
em lugar nenhum da máquina, e `06_avaliar_provimento_cnes.py` aborta na linha 160
com `FileNotFoundError` nesse caminho. O painel é produzido por
`05_integrar_painel_analitico.py` a partir dos ZIPs mensais do CNES, que o
manifesto de aquisição registra em cerca de 640 MB por competência — mais de
16 GB para as 26 competências, acima do que este ambiente comporta.

**Consequência para a fila:** nenhuma tabela de A5 pode ser regravada aqui, e a
regra do projeto proíbe produzir saída fora de script versionado. Isso bloqueia
as **sessões 1 e 4 por inteiro** e a parte medida da **sessão 3**. A **sessão 2**
não é afetada: A4 lê apenas artefatos versionados presentes e foi reexecutado com
sucesso, reproduzindo os alvos do C1 (capital +0,3264, metropolitano +0,2793,
interior próximo +0,1207, 24 níveis de efeito fixo).

**Nota de reprodutibilidade, corrigida.** Uma primeira verificação sugeriu que
reexecutar A4 reescrevia doze arquivos com diferenças a partir da 14ª casa
decimal, e atribuiu isso a não determinismo de BLAS. **Estava errado.** A causa
era o interpretador: o `python3` do sistema é 3.11 com numpy 2.4.6, enquanto o
`requirements.txt` fixa numpy 2.5.2 e o `README.md` exige Python 3.12 ou
superior. Montado o ambiente documentado com `python3.13` — as mesmas versões que
o manifesto A6 registra —, `05_estimar_atracao.py` reexecuta **sem alterar um
único byte** das saídas de A4, e a suíte segue verde.

A conclusão correta é mais estreita do que a que escrevi primeiro. **A4 reproduz
byte a byte no ambiente documentado**, e diferença numérica ali é sinal de
ambiente errado, não de indeterminismo tolerável — não deve ser declarada como
ruído em commit nenhum.

**A generalização para o repositório inteiro é falsa, e foi corrigida no mesmo
dia.** A sessão 3/5 mostrou que A8 **não** reproduz: reexecutar
`09_estimar_cutoff_escore_estrito.py` altera seis artefatos, nas colunas de
intervalo de confiança a partir do 15º dígito e no tamanho do PNG. Duas
execuções consecutivas são idênticas entre si, então o script é determinístico;
o que não bate é o artefato versionado, gravado sob outro estado de biblioteca —
em outra plataforma, como mostram os caminhos com barra invertida do Windows que
ele ainda carrega. Detalhe e decisão pendente em
[`../auditorias/14_erratas_artefatos_congelados.md`](../auditorias/14_erratas_artefatos_congelados.md).

### Destravado parcialmente em 16/09/2026 — A5 reestima a partir do painel congelado

O bloqueio de D-4 sobre a fila era mais estreito do que estava registrado.
`A5_painel_T0.parquet` — versionado, 30.784 linhas, hash `bcdb9848…` fixado no
manifesto A6 — é exatamente o objeto `panel` que `06_avaliar_provimento_cnes.py`
constrói do painel mensal antes de qualquer estimação. Tudo o que o script faz
depois desse ponto lê apenas `panel` e artefatos versionados.

`06_avaliar_provimento_cnes.py` ganhou um **modo de reestimação**: quando
`output/painel_municipio_curso_mensal.parquet` não está no disco, o script lê o
painel congelado, **confere o SHA-256 contra o manifesto A6** e aborta se não
bater ou se não houver âncora; nesse modo `A5_painel_T0.parquet` nunca é
regravado. A ausência do painel mensal fica registrada no bloco de hashes com
`sha256: null`, `presente: false`, o motivo e o hash que a execução anterior
havia registrado (`285db221…`), no padrão do B-3.

**Validação antes de qualquer mudança de conteúdo:** executado no ambiente
documentado, o modo de reestimação reproduziu **byte a byte** todas as tabelas
CSV e figuras PNG de A5 versionadas; só mudaram `data_referencia`, o novo campo
`modo_painel` e o bloco de hashes dos dois JSONs, mais a data do relatório. Os
11 alvos congelados do C2 seguem conferidos pelo próprio script. Dois testes
novos em `tests/test_provimento_cnes_a5.py`.

**Consequência para a fila:** as sessões **1** e **4** e a parte medida da
**3** deixam de estar bloqueadas por D-4. O que D-4 continua bloqueando é o que
exige o painel mensal ou os microdados brutos: reconstruir o painel com outra
definição, auditar `co_municipio_gestor`, a expansão CBO→curso e a chave
`CO_PROFISSIONAL_SUS`, e qualquer análise no grão CNES. O `run_all.py` num
clone limpo continua falhando em `05_integrar_painel_analitico.py`.

---

# Fila de execução — normativa

**Esta ordem é a fila vigente, não uma sugestão.** Uma sessão que for executar
itens deste backlog começa pela primeira sessão ainda aberta e não pula adiante,
salvo decisão explícita do autor registrada aqui. A ordem foi construída por
dependência e por risco, não por conveniência: as sessões 1 e 2 mexem em número,
e a 2 depende de a especificação do C1 já estar valendo.

> **Estado revisto em 14/09/2026.** A tentativa de executar a sessão 1 produziu
> dois achados que mudam a fila: o alvo congelado da variante a adotar não
> reproduz (ver A-1) e A5 não é reexecutável neste ambiente (ver D-4). A ordem
> abaixo permanece, mas três sessões passam a depender de decisão ou de dado
> ausente. Pular uma sessão bloqueada para executar a seguinte **não** é furar a
> fila: é o tratamento previsto para bloqueio, e o motivo fica registrado aqui.

| Sessão | Estado | Itens | Por quê nesta ordem |
|---|---|---|---|
| 1 | `CONCLUIDA` (emenda `03ccc1c`, execução na seção A-1) | **A-1** | Executada em 16/09/2026 depois de D-4 ser parcialmente destravado (`da4d6f7`). Decisão delegada pelo autor: residual rotulado, 24 níveis. Os três alvos reemitidos reproduzem. |
| 2 | `CONCLUIDA` (emenda `9e5de6d`, execução `fbc5f58`) | **A-2 + A-3 + C-6** | Executada em 14/09/2026 na especificação vigente. Emenda 1 do `35` commitada antes do código. Resultado e achado colateral na seção A-2 e no `35`. |
| 3 | `CONCLUIDA` (14/09/2026 `a8107cb` para a forma funcional; 16/09/2026 para as três restantes, protocolo `1fab57d`) | **C-7** | Red team completo. Placebo passa; pré-tendência rejeita nos cursos 2 e 16 (proporcional) e 2, 14 e 16 (nível), publicada por curso; deslocamento sem sinal nos vizinhos do quadro e oferta regional agregada positiva. Limite: vizinho é vizinho dentro do quadro. |
| 4 | `CONCLUIDA` (16/09/2026) | **B-1, B-2, B-5, B-6, C-9** | Executada no modo de reestimação de A5 (`da4d6f7`). B-6 fechou um rótulo no código e dois em errata (E-3, E-4). Achado colateral do B-5: o coeficiente em nível não sobrevive ao FDR da família de 25; o proporcional sobrevive. |
| 5 | `CONCLUIDA` (14/09/2026) | **B-3, C-1, C-2, C-3, C-5, C-8** — **C-4 bloqueado** | Executada com a sessão 3. Commits: B-3 `2375267`, C-1 `093fb44`, C-2 `8c4d3e9`, C-3 e C-5 `e7fc9e9`, C-4 e C-8 `1893e95`. O C-4 não foi concluído: a renomeação recomendada muda o SHA-256 de `portao_denominador.json`, fixado como hash de entrada em A3, A4 e A5 — ver a seção C-4. |
| — | `DECISÃO DO AUTOR` | **B-4, B-7** | Errata contra reexecução da tipologia congelada. Recomendo errata. Não executar sem a decisão. |
| — | `RESOLVIDO` | **D-1** | TeX instalado; artigo compila. Só a revisão de provas pelo autor continua pendente. |
| — | `BLOQUEADA` | **D-2 a D-4** | Revisar a condição de desbloqueio, não executar. |

## Decisões que dependem do autor — consolidadas em 14/09/2026

Estão espalhadas pelos itens; esta lista existe para que não se perca nenhuma.
Nenhuma delas foi tomada por sessão de agente, de propósito: todas escolhem
entre alternativas defensáveis, e a fila proíbe escolher depois de ver o efeito.

**Correção de ordenação, 14/09/2026.** A tabela abaixo estava ordenada pela
lógica interna da fila, e nessa ordem o envio dos pedidos administrativos
aparecia por último, como escolha de canal. Isso subestima o item. A fila de
fato não depende do **D-3**, mas a **pergunta declarada do projeto depende**: o
efeito do salto no valor anunciado da bolsa está bloqueado em R1 porque o escore
administrativo não foi obtido, e nenhum outro item desta lista muda isso. Ver o
diagnóstico abaixo. Quem for priorizar pelo que o projeto se propõe a medir, e
não pelo que a fila consegue executar, começa pelo D-3.

### Por que o D-3 é o único caminho para o efeito da bolsa

Três fatos, todos já registrados em artefato, fecham as alternativas públicas:

1. **A bolsa não varia dentro do município.** A faixa é municipal e o valor é
   função dela — R$ 10 mil, R$ 15 mil, R$ 20 mil. Como a faixa é atribuída por
   vulnerabilidade, variação de bolsa é também variação de território. Sem
   descontinuidade na regra, os dois efeitos são a mesma variação e nenhuma
   especificação os separa.
2. **A regra não é reconstruível com o IVS público.** `portao_regra_ivs.json`
   registra 191 faixas reproduzidas em 368 e **177 divergentes**, com assimetria
   sistemática — 94 células de Faixa 2 anunciada recalculam para Faixa 3.
3. **O desenho fuzzy falhou onde não havia regra.** Verificado em 14/09/2026 por
   `01b_reconstruir_regra_faixa.py`: o IVS máximo da Faixa 2 é `0,437`, de modo
   que na janela de `0,05` em torno de `0,500` **só existe Faixa 1 dos dois
   lados**. O primeiro estágio nulo medido ali mede ausência de regra no ponto,
   não ausência de resposta à bolsa.
4. **E nenhum limiar funciona.** Os intervalos de IVS das três faixas se
   sobrepõem, e há **2.763 inversões em 44.073 pares** (6,3%) — IVS maior com
   bolsa menor. A melhor regra de dois cortes possível acerta 285 de 368
   (77,4%), em `0,323/0,377`; a taxonomia do Atlas acerta 191. Covariáveis
   municipais pré-tratamento não fecham a conta. O critério efetivo usa
   informação que não está em nenhuma base deste repositório.

Nota sobre o escopo do pedido: obtido o escore, R1 identifica o efeito do valor
**anunciado** — intenção de tratar da oferta. O efeito do valor **recebido**
exige folha de pagamento, como o próprio plano `14` já diz. São dois insumos
distintos e convém pedi-los no mesmo ato.

| # | Decisão | Onde está o detalhe | Por que não foi decidida aqui |
|---|---|---|---|
| 1 | Definição do efeito fixo para as quatro células sem macrorregião publicada: nível residual rotulado, com 24 níveis, ou o que a auditoria mediu, com 23 e quatro células sem efeito fixo | item **A-1** | os dois coeficientes já são conhecidos, +0,5062 e +0,5014; escolher agora seria escolher vendo o efeito. Resolvida a definição, o alvo precisa ser reemitido antes da emenda |
| 2 | Errata contra reexecução da tipologia congelada | itens **B-4** e **B-7** | reexecutar regrava o manifesto e quebra a cadeia de hashes a jusante, obrigando a refazer A3–A6, para corrigir uma frase e um tipo de coluna. A fila já recomenda a errata |
| 3 | Portão de A1 publicado como critério testado, quando as duas constantes são literais | item **C-4** | a renomeação honesta muda o SHA-256 de `portao_denominador.json`, fixado como hash de entrada em A3, A4 e A5. Reparar exigiria reexecutar A5, hoje impossível por D-4 |
| 4 | Regravar ou não os artefatos de A8 sob o ambiente documentado | [`../auditorias/14_erratas_artefatos_congelados.md`](../auditorias/14_erratas_artefatos_congelados.md) | manter conserva a cadeia de hashes e preserva caminhos Windows incorretos; regravar conserta os caminhos e obriga a reemitir os hashes. Nenhum número publicado muda nos dois casos |
| 5 | Revisão de provas do PDF | item **D-1** | a compilação deixou de ser impedimento; a leitura do artigo é do autor |
| 6 | Envio dos pedidos administrativos — **na prática, a de maior consequência** | item **D-3** | escolha de canal e autorização são do autor. Nenhum item *desta fila* depende disso, mas a pergunta declarada do projeto depende: é o que destrava R1 e, com ele, o efeito da bolsa. Ver a correção de ordenação acima |

Três itens **não** são decisão, e sim espera por dado externo: `C3-02B` depende
de dois arquivos aparecerem no FTP oficial, `C3-05` da competência `202703`
madura e `C3-06` de setembro de 2027. Ver **D-2**.

## Protocolo de sessão

Ao **iniciar** uma sessão desta fila:

1. Confirme aqui qual é a primeira sessão `ABERTA`. Não pule.
2. Se a sessão contém item do **Grupo A**, escreva a emenda ao plano — o que muda,
   por quê, alvo esperado, o que não muda — e **commite a emenda antes de tocar em
   código**, como foi feito em `35_plano_correcoes_pos_auditoria.md`.
3. Releia as restrições em "O que esta fila não autoriza".

Ao **terminar**:

4. Suíte verde e conferidor do artigo passando são portão, não formalidade.
5. Troque o estado da sessão para `CONCLUIDA` **neste arquivo**, com o hash do
   commit, e ajuste o ponteiro de próxima sessão no `TODO.md` e no
   `05_roadmap_execucao.md`. Sem isso a próxima sessão não sabe onde a fila parou.
6. Se um alvo congelado não reproduzir, **pare**: é achado, não resultado novo.

## O que esta fila não autoriza

- Promover A5 a causal, em qualquer escala.
- Reexecutar a versão agregada do ciclo 1 — DDD, estudo de evento, mecanismos.
- Alterar a amostra, o desfecho ou o estimador de A8.
- Reexecutar a tipologia congelada sem decisão explícita do autor (B-4, B-7).
- Enviar qualquer pedido administrativo.
- Escolher entre variantes depois de ver qual favorece a narrativa.
