# Erratas de artefatos congelados

> **Criado em:** 2026-09-14, na sessão 5 da fila de
> [`36_backlog_pos_auditoria.md`](../06_execucao/36_backlog_pos_auditoria.md).
> **Finalidade:** registrar defeito de rótulo, fórmula ou nota em artefato cuja
> reexecução não é autorizada ou não é barata, quando corrigir o artefato
> custaria mais do que corrigir a afirmação.
> **Regra:** a errata **não** altera o artefato. O valor publicado continua onde
> está; o que muda é o que se pode afirmar sobre ele. Cada entrada diz o que o
> artefato publica, o que está errado, qual é o valor ou a leitura correta, e
> por que a reexecução não foi feita.

Esta não é uma lista de resultados novos. Nenhuma entrada aqui muda estimativa,
amostra, desfecho ou estimador.

---

## E-1 · Intervalo convencional fora do espaço de parâmetros em A8

**Item de origem:** C-3.
**Artefato:** `output/tema_trabalho/A8_tabela_02_estimativas_escore_estrito.csv`.

**O que o artefato publica.** Duas linhas de `2025_C1_CH2`, amostra `gap_1_ac`,
trazem `ic95_convencional_superior = 1,2618`:

| ciclo_chamada | desfecho | n_pares | diferença | IC95% convencional |
|---|---|---:|---:|---|
| `2025_C1_CH2` | `homologacao_mesma_celula` | 6 | +0,8333 | 0,4049 a **1,2618** |
| `2025_C1_CH2` | `homologacao_qualquer_local` | 6 | +0,8333 | 0,4049 a **1,2618** |

**O que está errado.** A diferença de duas proporções vive em `[-1, 1]`. Um
limite superior de 1,2618 está fora do espaço de parâmetros e não é
interpretável como probabilidade. A coluna já se chama "convencional" e a seção
5 do `A8_relatorio_cutoff_escore.md` já diz que os intervalos `t` não resolvem a
discretização da running variable, mas nenhuma ressalva sinalizava **estas**
linhas, e nenhum intervalo alternativo era oferecido ao lado.

**A leitura correta.** Com seis pares, cinco discordantes favoráveis e nenhum
contrário, a aproximação normal é inadequada nas duas pontas. O intervalo exato
condicional — Clopper–Pearson sobre os pares discordantes, o análogo exato do
teste de McNemar que a própria tabela já usa em `p_exato_pareado_bicaudal` — é:

| desfecho | IC95% convencional | IC95% exato |
|---|---|---|
| `homologacao_mesma_celula` | 0,4049 a 1,2618 | **−0,0364 a 0,8333** |
| `homologacao_qualquer_local` | 0,4049 a 1,2618 | **−0,0364 a 0,8333** |

Além de caber no espaço de parâmetros, o intervalo exato **cobre o zero**,
enquanto o convencional não. Isso é coerente com o `p` exato já publicado para
essas linhas, `0,0625`, que não rejeita a 5%: o convencional era otimista, não
apenas mal delimitado. A leitura correta dessas duas linhas é de **efeito
direcional impreciso**, sustentado por seis pares, e não de efeito estabelecido.

**O que foi feito em vez de reexecutar A8.** O intervalo exato passa a ser
publicado ao lado, em artefato próprio, sem tocar nas tabelas de A8:

- gerador: [`scripts/tema_trabalho/09b_intervalos_exatos_escore.py`](../../scripts/tema_trabalho/09b_intervalos_exatos_escore.py)
- artefato: `output/tema_trabalho/A8_tabela_06_intervalos_exatos.csv`

Ele lê `A8_tabela_02` e `A8_tabela_03` já publicadas, recalcula nada do
estimador e acrescenta três colunas: `ic95_convencional_fora_do_espaco`,
`ic95_exato_inferior` e `ic95_exato_superior`. Das 22 linhas cobertas, duas têm
intervalo convencional fora de `[-1, 1]` — exatamente as duas acima.

**Por que não reexecutar A8.** Duas razões independentes. A fila proíbe alterar
amostra, desfecho ou estimador de A8. E, verificado nesta sessão, os artefatos de
A8 versionados **não reproduzem byte a byte** sob o ambiente documentado: ver a
seção "Achado de reprodutibilidade" abaixo.

---

## E-2 · MDE por estrato do A3 usa fórmula de proporção única

**Item de origem:** C-5.
**Artefato:** `output/tema_trabalho/potencia_atracao.json`, bloco `por_estrato`.
**Gerador:** `scripts/tema_trabalho/04_congelar_pre_analise.py`.

**O que o artefato publica.** Cada estrato traz `mde_80_pp_p50` e
`mde_80_pp_p30` — por exemplo, capital `0,176` e `0,1613` — sem nenhum rótulo
sobre o que esses números são.

**O que está errado.** Três coisas, todas confirmadas por leitura do código:

1. **Não são MDE de diferença.** São calculados por `mde_proporcao`, cujo
   erro-padrão é `sqrt(p(1-p)/n)·sqrt(DEFF)`, o de **uma** proporção. O MDE de
   um contraste soma a variância dos dois lados, como faz
   `mde_diferenca_dois_grupos`. O bloco `mde_global` já carrega o rótulo
   `"benchmark de precisão de uma proporção; não é o MDE dos coeficientes
   territoriais"`; o bloco `por_estrato` publica números da mesma fórmula **sem**
   rótulo equivalente.
2. **O docstring errava duas vezes.** Dizia *"MDE bilateral para diferença de
   proporções vs baseline (aprox. 2*SE)"*. Não é EP de diferença, como acima; e
   o multiplicador não é 2, e sim `Z_ALPHA + Z_POWER = 1,9600 + 0,8416 =
   **2,8016**` para alfa bilateral de 5% e poder de 80%. Conferido reproduzindo
   capital à mão: `sqrt(0,25/73)·sqrt(1,153)·2,8016 = 0,176`, exatamente o valor
   publicado.
3. **`mde_diferenca_vs_resto_p50` usa o DEFF errado de um lado.** A chamada passa
   `deff2=deff`, o DEFF da **amostra inteira** (1,126), onde o correto seria o
   DEFF do próprio complemento do estrato. Conferido: capital com
   `n1=73, deff1=1,153, n2=1.222, deff2=1,126` devolve `0,1811`, o valor
   publicado.

**Consequência substantiva: nenhuma para o artigo.** O artigo usa apenas os
contrastes versus interior remoto, do bloco `contrastes_vs_interior_remoto`, que
são calculados por `mde_diferenca_dois_grupos` com o DEFF de cada lado e estão
corretos. O `interpretacao.regra` do próprio artefato já manda usar esses, e não
o benchmark global.

**Leitura correta do bloco `por_estrato`.** `mde_80_pp_p50` e `mde_80_pp_p30`
devem ser lidos como **precisão de uma proporção dentro do estrato**, não como
potência de um contraste, e `mde_diferenca_vs_resto_p50` como aproximação com o
DEFF do complemento substituído pelo da amostra inteira.

**Por que errata e não reexecução.** A3 é protocolo congelado e o próprio item
recomenda errata. Reexecutar regravaria `potencia_atracao.json` e
`registro_pre_analise_atracao.json`, cujos hashes entram no manifesto A6 e na
cadeia a jusante, para trocar rótulo de números que o artigo não usa. O
docstring e um comentário no ponto exato do código foram corrigidos, porque não
alteram nenhuma saída; os artefatos seguem intactos, com hashes
`91fa9055…` e `eb2bf812…`.

---

## E-3 · `celulas_confirmacao_acima_vagas_imediatas` não é a contagem literal

**Item de origem:** B-6, segundo ponto. **Sessão:** 4, em 16/09/2026.
**Artefato:** `output/tema_trabalho/portao_denominador.json`, campo
`chamada_1.celulas_confirmacao_acima_vagas_imediatas`.
**Gerador:** `scripts/tema_trabalho/02_reconciliar_funil_ciclo1.py`.

**O que o artefato publica.** `10`.

**O que está errado.** O nome promete a contagem de células cujas confirmações
excedem as vagas imediatas publicadas, mas o código filtra `immediate > 0`
antes de contar, ou seja, só conta células que **tinham** vaga imediata. As
células que eram só de reserva e receberam confirmação ficam de fora, embora
sejam o caso mais numeroso.

**A leitura correta**, reproduzida em 16/09/2026 sobre
`matriz_funil_ciclo1.parquet`, chamada 1: **185 células** com confirmações
acima das vagas imediatas publicadas, somando **221 confirmações excedentes**;
das 185, apenas **10** tinham vaga imediata maior que zero, que é o número
publicado. O rótulo correto do `10` é "células com vaga imediata e confirmações
acima dela".

**Consequência substantiva: nenhuma.** Nenhum documento publica o `10`, e a
decisão de A1 (`APROVADO_CELULA`, outcome binário por célula) já nasceu
justamente porque confirmações em reserva impedem denominador por vaga.

**Por que errata e não reexecução.** O SHA-256 de `portao_denominador.json`
está fixado como entrada em `registro_pre_analise_atracao.json` (A3),
`A4_estimativas_atracao.json`, `A5_estimativas_provimento.json` e
`A5_manifesto_maturidade_censura.json`. Regravá-lo exige reexecutar A3, que é
protocolo congelado, e toda a cadeia até A6, para corrigir um rótulo que nenhum
documento cita — o mesmo custo que bloqueou o C-4. A correção do campo entra
junto da primeira reexecução legítima de A1→A3, se houver, com o C-4.

---

## E-4 · `n_celulas_funil_A1` conta linhas, não células

**Item de origem:** B-6, terceiro ponto. **Sessão:** 4, em 16/09/2026.
**Artefato:** `output/tema_trabalho/manifesto_tipologia_territorial.json`,
campos `estratos.<estrato>.n_celulas_funil_A1`.
**Gerador:** `scripts/tema_trabalho/03_construir_tipologia_territorial.py`.

**O que o artefato publica.** Capital 250, metropolitano 591, interior próximo
1.711, interior remoto 505 — total **3.057**.

**O que está errado.** São linhas de `matriz_funil_ciclo1.parquet` na população
A1, não células distintas. A matriz tem uma linha por célula **e chamada**, e
**929** células aparecem nas duas chamadas.

**A leitura correta**, reproduzida em 16/09/2026: **2.128 células CNES–curso
distintas** na população A1 (3.057 − 929). Os campos devem ser lidos como
"linhas célula–chamada do funil".

**Consequência substantiva: nenhuma.** O campo é descritivo do manifesto e não
alimenta amostra, estimando ou artigo; A4 usa as 1.295 células do quadro da
primeira chamada, contadas no próprio A4.

**Por que errata e não reexecução.** A tipologia é congelada (A2); reexecutar
`03_construir_tipologia_territorial.py` regrava o manifesto e a matriz e quebra
a cadeia de hashes até A6, pela mesma razão do B-4 e do B-7. A recomendação da
fila é errata, e a decisão delegada pelo autor em 16/09/2026 a adotou.

---

## E-5 · Nota aritmética errada no manifesto da tipologia

**Item de origem:** B-4. **Decisão:** delegada pelo autor em 16/09/2026 e
tomada como a fila recomendava — errata, não reexecução.
**Artefato:** `output/tema_trabalho/manifesto_tipologia_territorial.json`,
campo `rm_detalhe.nota`.

**O que o artefato publica.** *"Strict corrige para 1331 únicos (1316 nacionais
após remover 27 capitais duplas)"*.

**O que está errado.** Apenas **25** das 27 capitais pertencem a RM/RIDE
strict; Rio Branco e Campo Grande não pertencem. Reproduzido em 16/09/2026 sobre
`matriz_tipologia_territorial.parquet`: 27 capitais, 25 com `flag_rm_ride_2022`,
as duas fora são exatamente essas; 1.331 municípios em RM/RIDE strict.

**A leitura correta.** `1331 − 25 = 1306`, que é o que o parquet publica. A
frase deve ser lida como "1.306 nacionais após remover 25 capitais duplas".

**Por que errata.** A tipologia é congelada (A2). Reexecutar
`03_construir_tipologia_territorial.py` regrava manifesto e matriz, cujos
hashes estão fixados em A3, A4, A5 e A6, para trocar uma frase de nota.

---

## E-6 · `sg_uf` de tipo misto na tipologia

**Item de origem:** B-7. **Decisão:** delegada pelo autor em 16/09/2026 e
tomada como a fila recomendava — errata, não reexecução.
**Artefato:** `output/tema_trabalho/matriz_tipologia_territorial.parquet`,
coluna `sg_uf`; e `manifesto_tipologia_territorial.json`,
`concentracao.por_uf_top10_populacao_A1`.

**O que o artefato publica.** 31 valores distintos de `sg_uf` para 27 UFs: os
27 códigos numéricos da malha (`11`…`53`) mais as siglas `MS`, `PA`, `RS` e
`SC`, preenchidas do REGIC para os cinco municípios criados após o Censo 2010
— Mojuí dos Campos/PA, Pinto Bandeira/RS, Balneário Rincão/SC, Pescaria
Brava/SC e Paraíso das Águas/MS —, que também ficam com `nome_uf` nulo. O
manifesto publica `{"31": 150, "52": 44, "21": 35, "35": 35, …}`: códigos
apresentados como se fossem siglas.

**Consequência substantiva: nenhuma.** Nenhum dos cinco municípios está na
população A1, e todos os módulos a jusante usam `co_ibge_6d` como chave; a UF
dos modelos vem do painel, não desta coluna.

**A leitura correta.** `sg_uf` é código IBGE de UF em 5.565 linhas e sigla em
5; `por_uf_top10_populacao_A1` é indexado por código IBGE (31 = MG, 52 = GO,
21 = MA, 35 = SP, 33 = RJ, 23 = CE, 43 = RS, 11 = RO, 15 = PA, 51 = MT).

**Por que errata.** Mesma restrição de congelamento da E-5.

---

## Decisão de 16/09/2026 — A8 regravado sob o ambiente documentado

**Delegada pelo autor em 16/09/2026** (decisão 4 da lista consolidada no
backlog) e tomada nos termos do complemento acima: regravar conserta um
registro de proveniência objetivamente errado e não muda nenhum número.

**O que foi verificado antes de aceitar a regravação.** Reexecução de
`09_estimar_cutoff_escore_estrito.py` e `09b_intervalos_exatos_escore.py` no
ambiente documentado (Python 3.13, numpy 2.5.2, pandas 3.0.5, scipy 1.18.1,
statsmodels 0.15.0, matplotlib 3.11.1):

- `A8_tabela_02`, `A8_tabela_03`, `A8_tabela_04`: **só** as colunas
  `ic95_convencional_inferior`/`superior` diferem, e a maior diferença absoluta
  é **1,1 × 10⁻¹⁶**. Diferenças, erros-padrão, contagens, discordantes e `p`
  exatos são idênticos byte a byte.
- `A8_estimativas_cutoff_escore.json` e `A8_protocolo_cutoff_escore.json`: os
  14 caminhos com barra invertida do Windows passam a POSIX relativos à raiz;
  o restante das diferenças é o mesmo ruído do 15º dígito.
- `A8_figura_01`: PNG regravado pela versão de renderização do ambiente
  documentado.
- `A8_tabela_06_intervalos_exatos.csv` (09b) acompanha, porque lê as tabelas
  regravadas.
- Amostra, desfecho e estimador **não** mudaram: 36 pares em 2025, 11 em 2026;
  o conferidor do artigo segue aprovando as mesmas 193 cifras; suíte verde.

**Por que isto não é "ajustar até fechar".** Nenhum número foi movido em
direção a nada: a única mudança de conteúdo é o formato dos caminhos, e o
registro de proveniência passa a corresponder à plataforma declarada no
manifesto A6. A partir desta data a afirmação "A8 reproduz byte a byte no
ambiente documentado" é verificável, como já era para A1 e A4.

---

## Achado de reprodutibilidade — A8 não reproduz byte a byte

Registrado aqui porque condiciona a escolha da E-1, e não como resultado.

Verificado em 14/09/2026, no ambiente documentado (Python 3.13.12, numpy 2.5.2,
pandas 3.0.5, scipy 1.18.1, matplotlib 3.11.1, todos iguais ao
`requirements.txt`): reexecutar `scripts/tema_trabalho/09_estimar_cutoff_escore_estrito.py`
**altera seis artefatos de A8** em relação ao que está versionado.

O que muda é pequeno e não é resultado:

- `A8_tabela_02`, `A8_tabela_03`, `A8_tabela_04`, `A8_estimativas_cutoff_escore.json`
  e `A8_protocolo_cutoff_escore.json` diferem **apenas** nas colunas de intervalo
  de confiança, e apenas a partir do 15º dígito significativo — por exemplo,
  `0,41394184915555393` contra `0,413941849155554`. Diferenças, erros-padrão,
  contagens de pares, discordantes e `p` exatos são idênticos dígito a dígito.
- `A8_figura_01_efeitos_cutoff_escore.png` muda de 63.929 para 75.121 bytes, o
  que é assinatura de outra versão de renderização.

**Duas execuções consecutivas agora são byte a byte idênticas entre si**,
incluindo o PNG. Ou seja, o script é determinístico neste ambiente; o que não
bate é o artefato versionado, que foi gravado sob outro estado de biblioteca.

**O que isso significa e o que não significa.** Não invalida nenhum número
publicado: toda cifra de A8 citada no artigo é reportada em precisão muito acima
da divergência, e o conferidor segue aprovando. O que deixa de valer é a
generalização de que *o repositório inteiro* reproduz byte a byte sob o ambiente
documentado — verificada para A4, e **falsa para A8**.

**Não corrigido nesta sessão, de propósito.** Regravar os artefatos de A8 para
fazê-los bater seria ajustar até o resultado fechar, que é o que a fila proíbe.
A decisão de regravar A8 sob o ambiente documentado — e de registrar o novo
conjunto de hashes — é do autor, e está anotada no item C-3 da fila.

### Complemento de 14/09/2026 — há um defeito objetivo junto do juízo

A discussão acima é sobre dígitos, e nela cabe juízo. Junto dela viaja um
defeito que não depende de juízo nenhum: **os artefatos versionados de A8
registram os caminhos dos insumos com barra invertida do Windows**, seis
ocorrências em `A8_protocolo_cutoff_escore.json` e oito em
`A8_estimativas_cutoff_escore.json`, do tipo
`data\raw\pmm_e\2025_ciclo1_chamada1_homologados.xlsx`. O manifesto de
reprodução do próprio repositório declara a plataforma como
`Linux-6.18.44-fc-v24-x86_64-with-glibc2.39`.

Não é divergência de precisão: é registro de proveniência gravado num formato
que não corresponde à plataforma declarada e que não resolve para caminho válido
aqui. Reexecutar `09_estimar_cutoff_escore_estrito.py` no ambiente documentado
corrige isso sozinho, gravando caminhos POSIX relativos à raiz.

Isso muda o peso da decisão do autor. Regravar A8 **não seria apenas** trocar
dígitos irrelevantes para fazer hash bater; seria também consertar um registro
de proveniência que hoje está errado. Os dois efeitos vêm no mesmo ato e não
podem ser separados, porque ambos saem da mesma reexecução.

A recomendação desta errata continua sendo que a decisão é do autor, mas com a
ponderação explícita: **manter os artefatos como estão preserva a cadeia de
hashes e conserva caminhos Windows incorretos; regravá-los conserta os caminhos
e obriga a reemitir os hashes de A8 onde eles estiverem fixados.** Amostra,
desfecho e estimador de A8 não mudam em nenhum dos dois caminhos.

---

## E-7 · A emenda 2 (A-1) moveu também a especificação `full`, e a documentação de C-9 não acompanhou

**O que a documentação publica.** A seção C-9 de
[`36_backlog_pos_auditoria.md`](../06_execucao/36_backlog_pos_auditoria.md)
abre com «Ambos reportam `0,091608 / 0,345622 / 0,790969`», e o corpo da PR 3
declara, em «O que NÃO mudou», que a emenda 2 reemitiu «os cinco modelos
`minimal`».

**O que está errado.** Os três valores citados em C-9 são anteriores ao item
A-1, cujo commit (`62bb4ed`) precede o da sessão 4 (`3a89233`) na mesma PR.
Depois de A-1 a especificação `full` passou a reportar
`0,376737 / 0,225207 / 0,094364`. A definição de efeito fixo de UF move as duas
especificações, não só a `minimal`:

| modelo `full` | antes de A-1 | depois de A-1 |
|---|---|---|
| `estoque_6m` (= `delta` por FWL) | `+0,0916` (EP `0,3456`; `p = 0,791`) | `+0,3767` (EP `0,2252`; `p = 0,094`) |
| `entradas_6m` | `+0,0158` (`p = 0,892`) | `+0,1190` (`p = 0,106`) |
| `cobertura_6m` | `+0,0293` (`p = 0,102`) | `+0,0321` (`p = 0,077`) |
| `presentes_baseline_6m` | `+0,0013` (`p = 0,975`) | `+0,0161` (`p = 0,679`) |

**Leitura correta.** A frase de C-9 permanece verdadeira no que afirma — os
dois modelos `full` são o mesmo estimador por Frisch–Waugh–Lovell —, mas os
números que ela cita são de uma execução superada. A leitura de que «no `full`
o efeito desaparece» era apoiada por `p = 0,79`; hoje o artefato traz
`p = 0,094`. Nenhuma das duas sustenta afirmação causal, e nenhuma cifra do
artigo depende do `full`.

**O que foi feito.** Não é errata de valor: a
`A5_tabela_11_sensibilidade_colapso_uf.csv` passa a emitir as três variantes de
colapso para as duas especificações (30 linhas, contra 15), de modo que a
consequência da definição de UF sobre o `full` fica auditável no artefato, e
não só no histórico. A frase de C-9 fica como registro histórico do estado em
que o item foi aberto.

---

## E-8 · Níveis singleton de efeito fixo inflam o R² dentro da amostra e não estão no `n`

**O que o artefato publica.** `A5_tabela_06_validacao_preditiva.csv` reporta,
para `estoque_6m_minimal`, `r2_insample = 0,876` contra `r2_media_out = -0,078`,
sobre `n = 587` e 295 clusters; para `delta_minimal`, `0,933` contra `-0,315`.

**O que está errado.** Sob a variante primária de A-1, três níveis de `uf_fe`
têm uma única célula na amostra confirmatória: `41`, `MACRO_CENTRO-OESTE` e
`MACRO_SUDESTE`. O dummy do nível ajusta essa célula exatamente, de modo que ela
não contribui variação identificadora, mas continua contada em `n` e no R².
Uma delas é Brasília (`530010`, curso 14, estoque 923), que sozinha responde por
**83,8%** da soma de quadrados de `estoque_6m` e por **92,2%** da de
`delta_estoque_6m`. O salto do R² de `0,103` para `0,876` entre a variante
`balde_unico` e a primária não é ganho de ajuste: é o dummy de Brasília.

A causa é o denominador da regra de colapso. `colapsar_uf_fe` conta **municípios
no painel de 1.184 células**, não **células na amostra estimada de 587**: a UF 41
tem cinco municípios no painel e por isso não colapsa, mas tem uma única célula
na confirmatória; e a UF 53 colapsa para `MACRO_CENTRO-OESTE`, nível que nenhuma
outra UF ocupa, de modo que o colapso não a acompanha.

**Leitura correta.** Os coeficientes **não** dependem disso. Removendo os três
níveis singleton até o ponto fixo (`n` efetivo 584, 292 clusters, 21 níveis), o
coeficiente de atração é idêntico em quatro casas em todos os dez modelos —
`delta_minimal` `0,5062`, `estoque_6m_minimal` `3,5970`, `full` `0,3767` —,
exatamente o que se espera de níveis que não identificam nada. O que muda é o
ajuste: `r2` de `estoque_6m_minimal` vai de `0,876` para `0,209`, e o de
`delta_minimal` de `0,933` para `0,119`. Consequência prática: o contraste
dentro/fora da amostra da validação preditiva era muito menor do que parecia, e
a linha de Brasília em `A5_tabela_05_influencia_municipal.csv` (`delta` de
`-3,2e-14`) é zero por construção, não por ausência de influência.

**O que foi feito.** Diagnóstico e sensibilidade publicados em
`A5_tabela_15_singletons_efeito_fixo.csv` e no bloco `singletons_efeito_fixo` de
`A5_estimativas_provimento.json`; `A5_tabela_06` ganha `n_efetivo`,
`r2_insample_sem_singletons` e `rmse_insample_sem_singletons`. **A especificação
primária não muda**: os singletons continuam mantidos, para não reescolher
estimador depois de observar resultado. A remoção fica declarada como
sensibilidade.

---

## Nota de ambiente — reexecução de 21/09/2026

A reexecução de `06`, `06b` e `07` que produziu as entradas E-7 e E-8 rodou em
Python 3.11.15 com `numpy` 2.4.6, `pandas` 3.0.6 e `statsmodels` 0.15.0, e não
nas versões fixadas em `requirements.txt` (`numpy==2.5.2`, `pandas==3.0.5`), que
não resolvem no índice disponível a este ambiente. Conferido antes de aceitar: em
todas as tabelas de A5 já versionadas, a maior divergência numérica é
**1,5e-11**, em colunas de intervalo de confiança e de valor `p`; nenhum
coeficiente, contagem, amostra ou desfecho muda, e os 23 alvos congelados de A5
continuam conferindo. As figuras PNG foram regravadas pela própria reexecução.
