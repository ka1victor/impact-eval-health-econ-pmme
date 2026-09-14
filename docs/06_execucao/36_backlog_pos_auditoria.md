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

## C-2 · Afirmação falsa sobre linhas sub judice

O artigo e `docs/05_identificacao/17_plano_causal_publico_cutoff_escore.md` afirmam
que linhas sub judice são descartadas "nas publicações que trazem esse marcador".
Falso para o ciclo 1: o marcador existe na coluna 17 (`Unnamed: 16`, 1 linha) e o
código nunca o lê; só `read_support_2026` filtra `SITUACAO`, e só para 2026.

Numericamente imaterial — a linha cai num par de placebo e na amostra de empates,
e removê-la move o placebo de `0,000` para `+0,034`. Mas a afirmação é falsa e
precisa ser corrigida ou executada.

## C-3 · Intervalo de confiança fora do espaço de parâmetros

`A8_tabela_02`, linha `2025_C1_CH2` de homologação, traz
`ic95_convencional_superior = 1,2618`, fora de `[-1, 1]`. A coluna e a prosa já
rotulam "convencional" e a seção 5 do relatório diz que os intervalos `t` não
resolvem a discretização, mas nenhuma ressalva sinaliza **este** valor específico
e nenhum intervalo exato é oferecido ao lado.

## C-4 · Portão de A1 apresentado como teste

`02_reconciliar_funil_ciclo1.py:476` — `vacancy_id_available = False` e
`immediate_capacity_all_calls = False` são literais. `APROVADO_VAGA` e `REPROVADO`
são inatingíveis por construção. As premissas são factualmente corretas — não
existe coluna de identificador de vaga em nenhum dos oito insumos —, mas o JSON as
publica em `criterios` como se tivessem sido testadas contra os dados.

**Duas saídas:** derivar as duas constantes de uma checagem real de esquema, ou
renomeá-las como asserções documentais. A segunda é honesta e barata.

## C-5 · MDE por estrato de A3 com fórmula de proporção única

O `mde_global` foi corretamente rerrotulado, mas o bloco `por_estrato` continua
publicando `mde_80_pp_p50/p30` calculados com a fórmula de **proporção única** e
sem rótulo. O docstring ainda afirma *"MDE bilateral para diferença de proporções
vs baseline (aprox. 2*SE)"* — errado duas vezes: não é EP de diferença e o
multiplicador é 2,80, não 2. E `mde_diferenca_vs_resto_p50` usa o DEFF da amostra
inteira para o grupo complementar, em vez do DEFF do próprio complemento.

Nada disso entra no artigo, que usa só os contrastes, esses corretos. **Restrição
de congelamento:** A3 é protocolo congelado; prefira errata a reexecução.

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

## C-8 · Assinatura de CPF não comparável entre máscaras

Os homologados mascaram as posições 4–7 do CPF (`711XXX14162`); a classificação
final mascara 6–9 (`669.07X.XXX-00`). A assinatura "3 primeiros + 4 últimos" só
coincide entre os dois formatos de homologado. Hoje inerte — o pareamento
verificado é 299/299 com zero discordância —, mas se alguém usar a assinatura para
cruzar homologados com a classificação final, o pareamento sai errado. Vale um
comentário no código e um teste que falhe se o uso se espalhar.

## C-9 · `delta_full` e `estoque_6m_full` são o mesmo estimador

Ambos reportam `0,091608 / 0,345622 / 0,790969` porque a especificação `full`
inclui `estoque_baseline`; por Frisch–Waugh–Lovell são idênticos. O JSON os
apresenta como duas evidências.

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
canal e autorização. Nada na fila depende disso.

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

**Nota de reprodutibilidade observada na mesma verificação:** reexecutar A4 neste
ambiente reescreve doze arquivos com diferenças a partir da 14ª casa decimal, por
não determinismo de BLAS entre versões de biblioteca. Nenhuma conclusão muda, mas
a cadeia de hashes de A6 é sensível a isso. Qualquer sessão que reexecute A4 deve
declarar essa origem ao commitar, e não tratar a diferença como resultado novo.

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
| 1 | `BLOQUEADA_ACHADO` | **A-1** | Alvo da variante a adotar não reproduz, e a definição de efeito fixo é decisão do autor. Também depende de D-4. Detalhe na seção A-1. |
| 2 | `CONCLUIDA` (emenda `9e5de6d`, execução `fbc5f58`) | **A-2 + A-3 + C-6** | Executada em 14/09/2026 na especificação vigente. Emenda 1 do `35` commitada antes do código. Resultado e achado colateral na seção A-2 e no `35`. |
| 3 | `PARCIAL` | **C-7** | Red team. A parte documental — forma funcional e leitura correta do que já existe — é executável. Publicar placebo, heterogeneidade de pré-tendência e deslocamento exige regravar artefato de A5, bloqueado por D-4. |
| 4 | `BLOQUEADA_D4` | **B-1, B-2, B-5, B-6, C-9** | Higiene de A5. Toda ela regrava tabela ou relatório de A5; nenhum caminho legítimo sem o painel do CNES. |
| 5 | `ABERTA` | **B-3, C-1, C-2, C-3, C-4, C-5, C-8** | Documentação e rótulos; nenhum exige reexecução pesada. Por último porque vários citam números que as sessões 1 a 4 podem mudar — com 1, 3 e 4 travadas, esse risco caiu. |
| — | `DECISÃO DO AUTOR` | **B-4, B-7** | Errata contra reexecução da tipologia congelada. Recomendo errata. Não executar sem a decisão. |
| — | `RESOLVIDO` | **D-1** | TeX instalado; artigo compila. Só a revisão de provas pelo autor continua pendente. |
| — | `BLOQUEADA` | **D-2 a D-4** | Revisar a condição de desbloqueio, não executar. |

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
