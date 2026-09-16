# 00. Registro de mudanças da documentação

> **Finalidade:** rastrear alterações **estruturais** da documentação — arquivo
> criado, fundido, removido, renomeado ou movido — e o motivo de cada uma.<br>
> **Não registra:** correção de texto, atualização de número ou acréscimo de
> seção dentro de um documento que permaneceu no mesmo lugar.<br>
> **Regra:** quem move informação de lugar abre entrada aqui no mesmo commit.

---

## 16/09/2026 — Banca 1: fonte Oswald embarcada, build em LuaLaTeX

A pedido do autor, para aproximar o deck da peça oficial do PMM-E: paleta
amostrada do banner, fonte de destaque igual à do título (Oswald, OFL),
imagem de fundo por frame e layouts em duas e quatro partes no tema.

### Criado

| Arquivo | O que é |
|---|---|
| [`07_apresentacoes/banca1/deck_beamer/fontes/`](07_apresentacoes/banca1/deck_beamer/fontes/README.md) | `Oswald-{Regular,Medium,SemiBold,Bold}.ttf`, `OFL.txt` e `README.md`: a fonte de destaque da identidade, versionada porque a licença permite e porque o build precisa dela |

`scripts/apresentacao/build_deck_beamer.sh` passou de `pdflatex` para
`lualatex` (o `fontspec` carrega a Oswald); o `.tex` compila nos dois motores.
Sem mudança no documento canônico: as macros novas (`\pmmefundo`, `pmmeduas`,
`pmmequatro`) não são usadas na banca 1.

---

## 16/09/2026 — Banca 1: tema Beamer próprio (PMME) no lugar do Warsaw

A pedido do autor: identidade visual do deck alinhada à peça oficial do Projeto
Mais Médicos Especialistas (azul-royal, amarelo, verde e vermelho), capa com
espaço para autores, professores e logo do Insper, sumário com composição
gráfica própria e barra de navegação de seção/subseção no topo.

### Renomeado

| De | Para | Motivo |
|---|---|---|
| `07_apresentacoes/banca1/deck_beamer/banca1_warsaw.tex` | [`07_apresentacoes/banca1/deck_beamer/banca1_beamer.tex`](07_apresentacoes/banca1/deck_beamer/banca1_beamer.tex) | o deck deixou de usar o tema Warsaw |
| `output/apresentacao_banca1/deck_beamer/banca1_warsaw.pdf` | `output/apresentacao_banca1/deck_beamer/banca1_beamer.pdf` | artefato derivado, acompanha o nome do `.tex` |

### Criado

| Arquivo | O que é |
|---|---|
| [`07_apresentacoes/banca1/deck_beamer/beamerthemePMME.sty`](07_apresentacoes/banca1/deck_beamer/beamerthemePMME.sty) | tema Beamer do projeto: paleta, fontes, navbar de seção/subseção, frametitle, rodapé, blocos e utilitários (`\fonte`, `\lead`, `\num`, `destaque`) que antes viviam no preâmbulo do `.tex` |
| [`07_apresentacoes/banca1/deck_beamer/pmmecapa.sty`](07_apresentacoes/banca1/deck_beamer/pmmecapa.sty) | capa em TikZ com slots para autoria, orientação, instituição, data, logo e foto |
| [`07_apresentacoes/banca1/deck_beamer/pmmesumario.sty`](07_apresentacoes/banca1/deck_beamer/pmmesumario.sty) | sumário em TikZ com seis seções e descrição curta |

`scripts/apresentacao/build_deck_beamer.sh` passou a exportar `TEXINPUTS` para
o diretório do deck, de modo que `\usetheme{PMME}` resolva sem instalação.

### Documento canônico

`02_conteudo_slides.md`, slide 1: a linha de autoria ganhou o slot
"orientação" e a lista dos elementos da capa. Slide 2: cada seção ganhou a
descrição curta que o sumário exibe como linha auxiliar. Conteúdo primeiro no
documento canônico, depois no deck, conforme a regra do projeto.

---

## 16/09/2026 — Banca 1: corte de 19 para 15 slides, para o arco narrativo

A pedido do autor: **cortar além de comprimir**, para facilitar a narrativa. A
compressão de 14/09 tinha reduzido os decks de 36 para 22 frames, mas o
documento canônico continuava com 19 slides e o tempo estimado em 29 minutos.
Além disso, o deck construía do slide 3 ao 18 uma hipótese sobre o valor da
bolsa e fechava dizendo que o desenho causal do trabalho usava outra coisa, sem
enquadrar a passagem.

### O corte

Critério: um slide por afirmação (roteiro, §2.2), aplicado ao contrário — dois
slides com a mesma afirmação viram um; slide que descreve sem argumentar
encolhe. Detalhe slide a slide em
[`07_apresentacoes/banca1/01_roteiro_narrativo.md`](07_apresentacoes/banca1/01_roteiro_narrativo.md), §4d.

| Fusão ou corte | Antes | Depois |
|---|:---:|:---:|
| retrato nacional + o que o médico vê | 3, 4 | **3** |
| o que é o PMM-E, sem a lista de cursos, o fluxo em passos e a figura regional | 5 | **4** |
| evidência a favor + contra | 8, 9 | **7** |
| custo geográfico + custo laboral, sem a figura do U | 13, 14 | **11** |
| o que a bolsa paga + o IVS organiza o custo | 16, 17 | **13** |
| viabilidade, reescrita com enquadramento e "o que fica de pé" | 19 | **15** |

Os demais slides só mudaram de número. Tempo estimado: de 29 para 24 minutos.

### Consequências

- `F4` (`curva_custo_laboral_burnout.png`) e `F5` (`vagas_ciclo1_por_regiao.png`)
  saem do deck e passam à lista de figuras geradas e não usadas em
  `03_proveniencia_figuras_e_numeros.md`. O script de figuras continua gerando
  `F5`; os scripts de build dos decks deixam de exigir as duas.
- As duas ressalvas de conteúdo abertas ficam **encerradas**: a contagem de 10
  cursos ambulatoriais foi conferida na Tabela 3 do edital e nos cursos 7 a 16
  do quadro de vagas (a lista antiga colapsava três cursos num item), e a
  legibilidade de `F4` deixa de afetar a apresentação.
- Os decks foram reconstruídos a partir do documento cortado: Beamer com **15
  frames** (um por slide) e 27 páginas, sem `Overfull`; Slidev com **26
  páginas**. `SOURCE_DATE_EPOCH` do Beamer passou a 16/09/2026.
- `02_teoria/hipoteses_e_viabilidade_empirica.md`, §4.2, ainda dizia que isolar
  o efeito da bolsa exigia "o escore administrativo"; passou a refletir a leitura
  do edital de 14/09: o que falta é o **Anexo IV** e os critérios de localização
  da cláusula 11.1.3.

### O que não mudou

Nenhum número novo entrou. Os cinco pontos de proveniência `P1`–`P5` continuam
registrados; `P4` foi reescrito para dizer o estado atual — as três figuras
usam a faixa publicada desde 14/09 — em vez da escolha anterior, que ele ainda
descrevia como deliberada.

---

## 14/09/2026 — Banca 1: a motivação reordenada para seguir o argumento

A motivação estava fragmentada porque estava fora de ordem lógica, e a correção
de agrupamento da mesma data agravou o sintoma: o slide 4 passou a remeter
explicitamente a "(slide 7)" para explicar a divergência entre faixa publicada e
categoria recalculada — uma referência para a frente, duas telas adiante. O
slide falava em "faixa publicada", "Faixa 1" e "categoria de IVS" antes de
qualquer um desses termos ter sido definido.

### A nova ordem

Os três blocos pedidos pelos professores — dor, política, efeitos — foram
mantidos. Mudou o que está dentro de cada um.

| Bloco | Antes | Agora |
|---|---|---|
| **O problema** | 3, 4, 5 | **3, 4** — a escassez é territorial; e, do outro lado, para o médico ela é um pacote de desvantagens concretas |
| **A política** | 6, 7 | **5, 6** — o que é o programa, e a regra que põe preço no lugar |
| **O efeito é incerto** | 8, 9, 10 | **7 a 10** — as duas medidas de oferta discordam e a bolsa maior vai para onde o médico fica sozinho; a evidência internacional não decide; o primeiro ciclo tampouco |

Em números de slide: o antigo 4 passou a **7**; o antigo 5 passou a **4**; os
antigos 6 e 7 passaram a **5** e **6**. Os slides 8 a 18 não mudaram.

O antigo slide 4 migrou para a **abertura do bloco do efeito**, que é onde ele
argumenta em vez de apenas descrever, e onde seus termos já foram definidos.

### As costuras

| Slide | Frase |
|:---:|---|
| 4 | fecha em "nenhuma dessas desvantagens se resolve sozinha. É aí que entra a política" |
| 5 | fecha em "cada vaga sai publicada com uma faixa de bolsa. É essa regra — e só ela — que o trabalho estuda" |
| 7 | abre em "onde a regra manda o dinheiro?" e fecha em "o programa põe R$ 5 mil a mais onde o médico trabalharia sozinho" |

A referência cruzada do slide 7 passou a apontar para o **slide 6**, que agora o
antecede. A coluna "Medimos?" da retaguarda dizia "sim — slide anterior",
referência que a nova ordem quebraria; passou a nomear a fonte, CNES.

**Nada foi reafirmado da versão anterior à correção de agrupamento.** As frases
de costura foram escritas sobre o achado corrigido: por habitante a bolsa maior
**não** vai para onde falta mais; em número de colegas, vai.

### Verificação

- Equivalência documento ⇄ deck conferida nos dois sentidos, contra a linha de
  base da `main`: **nenhuma divergência nova** foi introduzida.
- Nenhuma sobra da afirmação antiga ("menos da metade", "já havia menos
  especialistas") no documento ou no deck.
- Beamer em 22 frames e 29 páginas, sem `Overfull \hbox` ou `\vbox`; Slidev
  reordenado junto, em 33 páginas.

### Ponto de atenção aberto

A figura `F2` rotula as barras de mediana com **zero casas decimais**
(`f"{valor:.0f}"` em `scripts/apresentacao/gerar_figuras_banca1.py`), enquanto o
texto do slide 7 fala em **2,5** e **6,5** colegas. Na tela a figura mostra
**2** e **6**. A divergência é de formatação, não de dado, e é anterior a esta
entrada. Não foi corrigida aqui para não misturar mudança de pipeline com
reordenação narrativa.

---

## 14/09/2026 — Trava de ambiente, correção de série pré-C1 e achados da fila

Motivo: a tentativa de executar a fila pós-auditoria expôs que o repositório
roda em silêncio sob ambiente errado, e que a correção C1 não tinha propagado
para a documentação.

### O que foi criado

| Arquivo | Conteúdo | Por que existe |
|---|---|---|
| [`scripts/utils/ambiente.py`](../scripts/utils/ambiente.py) | verificação do interpretador e das versões fixadas | rodar sob versão próxima da fixada não dá erro, mas reescreve artefato a partir da 14ª casa decimal e quebra a cadeia de hashes sem aviso |
| [`tests/test_verificacao_ambiente.py`](../tests/test_verificacao_ambiente.py) | seis testes da trava | a trava só protege se ela mesma estiver coberta |

`run_all.py`, que grava artefato, passa a **abortar** diante de divergência.
`run_tests.py`, que apenas lê, **avisa** e segue. A suíte vai de 138 para 144
testes.

### O que foi corrigido

A série de A4 no `README.md` e em
[`05_identificacao/16_sintese_achados_e_novo_plano_causal.md`](05_identificacao/16_sintese_achados_e_novo_plano_causal.md)
ainda era a anterior ao C1, do balde único `RESTO`. Passa a ser a da
especificação primária vigente: metropolitano +27,9 p.p. no lugar de +29,4,
capital +32,6 no lugar de +23,2, e assim por diante. O `paper_pmme_submission.tex`
já estava correto, e o conferidor de números seguiu aprovando as 190 cifras.

`docs/auditorias/12_proveniencia_fins_de_linha.md` **não** foi alterado: ele
registra o estado observado numa data anterior ao C1, e corrigir seus números
falsificaria o registro.

### O que foi registrado

[`06_execucao/36_backlog_pos_auditoria.md`](06_execucao/36_backlog_pos_auditoria.md)
recebeu os achados que travam a fila: o alvo congelado do item A-1 não reproduz,
A5 não é reexecutável sem os microdados do CNES, e regenerar o manifesto de A6
hoje removeria em silêncio um registro de proveniência. O item D-1 passou a
resolvido, porque o artigo compilou.

### Sessões 3 e 5 da fila, no mesmo dia

Executadas juntas porque a sessão 4 está bloqueada por D-4 e as duas dividem o
gerador `07_red_team_sintese.py`. Da sessão 3 só a quarta ameaça do item C-7 é
executável; as três primeiras exigem regravar artefato de A5 e continuam
bloqueadas.

| Arquivo | Conteúdo | Por que existe |
|---|---|---|
| [`auditorias/14_erratas_artefatos_congelados.md`](auditorias/14_erratas_artefatos_congelados.md) | erratas E-1 (IC fora do espaço de parâmetros em A8) e E-2 (MDE por estrato do A3), mais o achado de que A8 não reproduz byte a byte | os dois artefatos são congelados, e corrigi-los custaria mais do que corrigir a afirmação sobre eles; a errata deixa o valor onde está e conserta o que se pode dizer dele |
| [`../scripts/tema_trabalho/09b_intervalos_exatos_escore.py`](../scripts/tema_trabalho/09b_intervalos_exatos_escore.py) | intervalo exato condicional ao lado do convencional, a partir das tabelas de A8 já publicadas | o item C-3 pede o intervalo exato "ao lado"; publicá-lo em artefato próprio atende sem tocar em A8 |

O script entra em `run_all.py` logo após `09_estimar_cutoff_escore_estrito.py` e
grava `output/tema_trabalho/A8_tabela_06_intervalos_exatos.csv`. Nenhuma tabela
de A8 é regravada, e amostra, desfecho e estimador de A8 continuam intactos.

Fora isso, nada foi criado, movido ou removido: as demais correções das sessões
3 e 5 são de conteúdo dentro de arquivos que permaneceram no mesmo lugar. A
suíte vai de 144 para 156 testes.

## 14/09/2026 — Banca 1: hipótese única, e o deck Beamer eleito e comprimido

Duas mudanças, de origens diferentes, no mesmo commit.

### A pedido da banca: uma hipótese, não duas

Os professores pediram que a apresentação ficasse com **uma única hipótese, a
primeira**. A correção foi feita primeiro no documento canônico e só depois nos
artefatos derivados, como manda a regra de proveniência.

| Documento | O que mudou |
|---|---|
| [`07_apresentacoes/banca1/02_conteudo_slides.md`](07_apresentacoes/banca1/02_conteudo_slides.md) | slide 17 passou de "Duas hipóteses" a **"A hipótese"**; a seção 5 ficou no singular, no título e no sumário; a tabela de derivadas ficou só com H1; o passo 4 foi reescrito. O documento inteiro foi reescrito no mesmo commit — ver adiante |
| [`07_apresentacoes/banca1/01_roteiro_narrativo.md`](07_apresentacoes/banca1/01_roteiro_narrativo.md) | título literal do slide 17, papel narrativo da seção 5 e as três linhas que contavam "duas hipóteses" |
| [`02_teoria/hipoteses_e_viabilidade_empirica.md`](02_teoria/hipoteses_e_viabilidade_empirica.md) | seção 4.2 refeita: a banca 1 leva uma hipótese. O conjunto canônico H1–H4 **não** mudou — mudou o que a apresentação enuncia |
| [`07_apresentacoes/banca1/README.md`](07_apresentacoes/banca1/README.md) | seção 5 no singular nas três tabelas |

**O que aconteceu com o custo locacional.** A antiga H2 — maior custo reduz o
preenchimento — não virou nota de rodapé nem sumiu: passou a ser apresentada
como **obstáculo de identificação**, que é o que ela é. O custo não varia
livremente, porque a regra do edital o amarra à bolsa e os dois sobem juntos;
ele é o que torna H1 difícil de testar, não uma segunda afirmação a testar. A
condição de degrau $\Delta B/p > \Delta c_0$ continua no slide, como
consequência da condição de aceitação na fronteira entre faixas.

A frase do slide 18 que dizia "separar H1 de H2" passou a "isolar o efeito da
bolsa do efeito do custo", no documento de conteúdo e nos dois decks.

### Decisão do autor: vai-se com o Beamer, mais limpo e mais comprimido

Dos dois decks construídos em paralelo, o **Beamer (Warsaw) é o escolhido**. Ele
foi então limpo e comprimido.

| Arquivo | O que mudou |
|---|---|
| [`07_apresentacoes/banca1/deck_beamer/banca1_warsaw.tex`](07_apresentacoes/banca1/deck_beamer/banca1_warsaw.tex) | reescrito: de **36 frames em 37 páginas** para **22 frames em 29 páginas** |
| [`scripts/apresentacao/build_deck_beamer.sh`](../scripts/apresentacao/build_deck_beamer.sh) | passou a relatar também `Overfull \vbox` |
| [`07_apresentacoes/banca1/deck_beamer/README.md`](07_apresentacoes/banca1/deck_beamer/README.md) | mapa de frames refeito; seções 3.1, 3.3, 3.4 e 5 reescritas |
| `output/apresentacao_banca1/deck_beamer/banca1_warsaw.pdf` | recompilado, 29 páginas |

**Uma barra só, embaixo.** A `headline` do Warsaw foi esvaziada e o rastreio de
seção desceu para o rodapé, no lugar antes ocupado pelo título do trabalho — que
se repetia em todas as páginas sem acrescentar nada a quem já leu a capa. A
faixa de `frametitle` com degradê, que é o que torna o tema reconhecível, ficou,
agora encostada no corpo. Saíram também as sombras das caixas de destaque. O
ganho é de cerca de uma linha e meia de texto em **todos** os frames.

**Compressão.** Sete slides do documento que estavam repartidos em dois, três ou
quatro frames de mesmo título dentro de uma só subseção foram fundidos em frame
único; outros sete viraram **um frame com dois overlays**. `\insertframenumber`
conta frames, não páginas: em um frame com overlay o rodapé exibe o mesmo
número nas duas telas, sob o mesmo título e o mesmo rastreio — para a banca é um
slide que se completa, não um slide novo. E overlay não custa tempo de fala além
do que o conteúdo já custa, o que importa contra os 28 minutos da seção 6 do
roteiro.

O slide 13 do documento ganhou o caminho inverso: o overlay que separava a
função-valor do seu glossário deixou de ser necessário, porque a altura
recuperada fez os dois caberem na mesma tela.

**O que saiu.** Prosa de ligação, citação que ilustrava sem acrescentar fato,
duas manchetes de jornal em caixa que repetiam a frase ao lado, e vão morto.
**Nenhuma afirmação e nenhum número do documento de conteúdo saíram** — todos os
valores exibidos foram reconferidos um a um contra a versão anterior do `.tex`.

**Verificação.** O build termina sem nenhum `Overfull \hbox` ou `\vbox` — nenhum
frame estoura a altura, que era o modo de falha esperado ao comprimir. Duas
execuções produzem o mesmo PDF byte a byte. As 29 páginas foram revistas uma a
uma em PNG.

### O documento canônico foi reescrito para ser a base concisa

Até aqui o deck estava **mais enxuto que o documento canônico** — divergência na
direção errada: quem lê a fonte de verdade encontrava prosa, citação e manchete
que a apresentação não mostra. `02_conteudo_slides.md` foi reescrito para dizer
exatamente o que vai à tela, e nada além.

| O que saiu | Onde |
|---|---|
| duas manchetes de jornal em citação recuada | slide 3 |
| as duas citações em inglês que ilustravam sem acrescentar fato | slides 5 e 8 |
| linhas `> Referência` soltas, que duplicavam o bloco `Fontes:` | slides 8 e 9 |
| prosa de ligação e repetição de rótulo | todos |

Dois ajustes de forma, no mesmo espírito: os números que **a figura já rotula**
— 16,0 / 10,0 / 7,3, os 5 / 3 / 2 colegas, os 15% / 34% / 42% e as sete
porcentagens de preenchimento — passaram da prosa para a **legenda da figura**,
que é onde eles são o registro do que a plateia vê sem obrigá-la a ler duas
vezes; e as duas ressalvas abertas (cursos ambulatoriais, figura do custo
laboral) ganharam seção própria no fim, em vez de ficarem só nos README dos
decks.

O cabeçalho do documento agora declara o que ele é: fonte de verdade, decks
derivados, banca teórica que termina na viabilidade empírica.

**Conferência de equivalência.** Todo número exibido no `.tex` foi procurado no
documento, e todo número do documento, no `.tex`. A única diferença que resta é
a esperada: os treze valores rotulados dentro das figuras estão no documento e
não no texto do deck, por causa da regra de não repetir em prosa o número que a
figura carrega. As afirmações foram conferidas uma a uma pelo mesmo método.

### O deck Slidev permanece, sincronizado apenas no conteúdo

O deck em `deck_slidev/` não foi descartado do repositório, mas deixou de ser
candidato. Recebeu apenas a mudança de conteúdo — hipótese única e a frase do
slide 18 — para não divergir do documento canônico. Sua composição não foi
retrabalhada, e a página 31 ficou com folga no rodapé por causa da linha de H2
removida.

---

## 14/09/2026 — Decks da banca 1 em duas tecnologias: Beamer (Warsaw) e Slidev (academic)

Motivo: produzir o artefato de projeção da banca 1, que até aqui existia só como
markdown de leitura. Foram feitos dois decks em paralelo, em tecnologias
diferentes, para comparação de clareza de apresentação. Ambos derivam de
[`07_apresentacoes/banca1/02_conteudo_slides.md`](07_apresentacoes/banca1/02_conteudo_slides.md).
Nenhuma afirmação, número, citação ou figura foi criada aqui: o documento de
conteúdo continua sendo a fonte de verdade, e divergência entre deck e documento
é erro do deck.

### Deck A — LaTeX Beamer, tema Warsaw

#### O que foi criado

| Arquivo | Conteúdo | Por que existe |
|---|---|---|
| [`07_apresentacoes/banca1/deck_beamer/banca1_warsaw.tex`](07_apresentacoes/banca1/deck_beamer/banca1_warsaw.tex) | deck em Beamer, tema Warsaw, 16:9, 36 frames em 37 páginas | a banca 1 tinha conteúdo canônico em markdown e nenhum artefato de projeção versionado |
| [`07_apresentacoes/banca1/deck_beamer/README.md`](07_apresentacoes/banca1/deck_beamer/README.md) | como compilar, mapeamento slide do documento → frames e decisões de composição | o corte de um slide do documento em vários frames precisa ser rastreável |
| `scripts/apresentacao/build_deck_beamer.sh` | build determinístico: confere as figuras, roda `pdflatex` duas vezes, relata `Overfull \hbox`, grava o PDF em `output/` e limpa auxiliares | regra do projeto: saída de apresentação é produzida por script versionado |
| `output/apresentacao_banca1/deck_beamer/banca1_warsaw.pdf` | PDF compilado, 37 páginas | artefato derivado, regerável pelo script |

#### Decisões registradas

| Decisão | Conteúdo |
|---|---|
| Mapeamento | os 18 slides do documento viram 36 frames; cada frame repete o título literal e a linha de rastreio do slide de origem, exibida em faixa fina fora do título |
| Repetição | onde a figura já rotula o número, o texto ao lado traz só a afirmação; nenhum valor aparece duas vezes na mesma tela |
| Overlay | o glossário da função-valor (slide 13) fica no mesmo frame da equação, em segundo overlay, para não deixar o referente fora da tela |
| Figuras | apenas as seis já versionadas — cinco de `output/apresentacao_banca1/` e a ilustração conceitual de `02_teoria/figuras/` — lidas por `\graphicspath` relativo à raiz, sem recorte, edição ou regeração. Cada figura tem uma única legenda, no mesmo formato `Fontes:` dos frames de texto |
| Ressalva registrada | em projeção, a legenda e as anotações de zona de `F4` (curva de custo laboral) ficam em torno de 5 pt e não são legíveis. O deck não pode regerar a figura; a decisão sobre refazê-la com tipografia maior é do autor. Detalhe no README do deck, seção 4.1 |
| Tema | Warsaw preservado no `frametitle` com degradê e sombra e nos blocos arredondados; a barra de navegação da headline foi trocada pela faixa de rastreio e o rodapé de três caixas por uma faixa fina; paleta trocada do azul padrão para o verde das figuras |
| Escopo | mantido o da banca 1 — termina na viabilidade empírica, sem slide de perguntas e sem resultado de estimação |

### Deck B — Slidev, tema `slidev-theme-academic`

#### O que foi criado

| Arquivo | Conteúdo | Por que existe |
|---|---|---|
| [`07_apresentacoes/banca1/deck_slidev/slides.md`](07_apresentacoes/banca1/deck_slidev/slides.md) | os 18 slides do documento em 33 páginas Slidev, tema `slidev-theme-academic` | a entrega da banca precisa de um deck projetável; o markdown de conteúdo é para leitura, não para projeção |
| [`07_apresentacoes/banca1/deck_slidev/README.md`](07_apresentacoes/banca1/deck_slidev/README.md) | como rodar e exportar, mapeamento slide do documento → páginas, decisões de composição | o mapeamento 1→N precisa ser auditável contra o documento de conteúdo |
| `07_apresentacoes/banca1/deck_slidev/style.css` e `components/` | estilo, faixa de rastreio de seção, faixa de fontes, figura com proporção travada | as regras de composição da seção 2 do roteiro — título é takeaway, rastreio fora do título, fonte que não compete com o conteúdo — são decisões visuais e viram CSS |
| `07_apresentacoes/banca1/deck_slidev/package.json` e `package-lock.json` | versões exatas de `@slidev/cli` (52.19.1), do tema (3.0.1) e das fontes empacotadas | build determinístico |
| `scripts/apresentacao/build_deck_slidev.sh` | exportação do PDF e dos PNG de revisão | figura ou número exibido em slide segue a mesma regra de proveniência de qualquer saída: é gerado por script versionado |

#### Saída gerada

`output/apresentacao_banca1/deck_slidev/banca1_slidev.pdf`, 33 páginas. Os PNG
por página, usados na revisão visual, são derivados do mesmo deck e ficam fora
do versionamento.

#### Segunda rodada de revisão, no mesmo dia

O deck saiu de 36 para 33 páginas. Três fusões: a figura do preenchimento do
ciclo 1 voltou a caber com sua leitura em uma página; a equação do valor
presente voltou a ficar na mesma página que o glossário dos seus termos; e os
quatro passos das hipóteses passaram de três páginas para duas. Onde a figura já
rotula o número na barra, o texto ao lado ficou só com a afirmação, sem relistar
o que a figura mostra. Nada de conteúdo foi cortado: só repetição e vão.

Ressalva registrada no README do deck: o documento canônico anuncia "10
ambulatoriais" e lista oito itens. O deck transcreve como está; a correção cabe
ao documento canônico, não ao artefato derivado.

#### Terceira rodada de revisão, no mesmo dia

O espaço livre da página passou a ser ocupado por quem ganha com ele: a figura
cresce até a barra de fontes sem distorcer, a tabela de quatro linhas ou mais se
estica, e nas páginas sem figura nem tabela o corpo do texto aumenta em vez de
ser esticado. Cartão e lista continuam sem esticar. As cinco páginas em que o
vão de rodapé permanece estão nomeadas no README do deck, com o motivo de cada
uma. Contagem de páginas inalterada.

#### O que não mudou

Nenhum arquivo da documentação foi movido, fundido ou removido. O conteúdo dos
18 slides, os números, as citações e as fontes vieram inalterados de
`02_conteudo_slides.md`; os 16 títulos dos slides 3 a 18 são os literais da
seção 2.1 do roteiro. As seis figuras são as que já existiam em
`output/apresentacao_banca1/` e em `docs/02_teoria/figuras/`: o build cria
links simbólicos para elas em um diretório de trabalho não versionado, sem
gerar, editar nem copiar imagem alguma para dentro do repositório.

### Ponto de atenção herdado do documento de conteúdo

O slide 6 de `02_conteudo_slides.md` anuncia **10 cursos ambulatoriais** e
enumera oito itens entre parênteses. Os dois decks transcrevem a lista como
está, por fidelidade; a conferência no Edital SGTES/MS nº 3/2025 fica pendente
no documento canônico, não nos decks.

---

## 09/09/2026 — Seção de apresentações, absorção do documento 18 e limpeza de referências

Motivo: preparar a entrega da banca 1 e eliminar as três duplicações de conteúdo
teórico que o projeto vinha carregando.

### O que foi criado

| Arquivo | Conteúdo | Por que existe |
|---|---|---|
| [`00_registro_mudancas.md`](00_registro_mudancas.md) | este registro | a documentação já tinha sido reorganizada antes sem deixar rastro do que foi para onde |
| [`07_apresentacoes/README.md`](07_apresentacoes/README.md) | regra da seção de apresentações | entregas de banca não tinham lugar próprio e vinham sendo tratadas como documento de teoria |
| [`07_apresentacoes/banca1/README.md`](07_apresentacoes/banca1/README.md) | escopo, estado por bloco e pendências bloqueantes | declarar que a banca 1 termina na viabilidade empírica |
| [`07_apresentacoes/banca1/01_roteiro_narrativo.md`](07_apresentacoes/banca1/01_roteiro_narrativo.md) | arco, regras de composição, rastreio do feedback e defeitos do deck anterior | feedback de banca sem ajuste rastreável não é feedback incorporado |
| [`07_apresentacoes/banca1/02_conteudo_slides.md`](07_apresentacoes/banca1/02_conteudo_slides.md) | conteúdo dos 15 slides, com título, corpo, visual, fonte e nota | fonte de verdade do deck; o `.pptx` passa a ser artefato derivado |
| [`07_apresentacoes/banca1/03_proveniencia_figuras_e_numeros.md`](07_apresentacoes/banca1/03_proveniencia_figuras_e_numeros.md) | origem e reprodutibilidade de cada número exibido | a regra de proveniência do projeto valia para `output/`, mas não estava sendo aplicada a slide |

### O que foi removido

| Arquivo removido | Para onde o conteúdo foi | Motivo |
|---|---|---|
| `02_teoria/18_modelo_teorico_slides_apresentacao.md` | [`02_teoria/modelo_micro.md`](02_teoria/modelo_micro.md), seções 3 e 3.2 | mantinha uma segunda versão da mesma teoria, com a adaptação ao PMM-E e as equações dos complementos que faltavam no documento canônico. Com o conteúdo de slides em `07_apresentacoes/`, o documento 18 deixou de ter função |

### O que mudou de lugar dentro da documentação

| Conteúdo | Antes | Agora | Motivo |
|---|---|---|---|
| Adaptação da equação de Moehling ao PMM-E, com $B_m(IVS_m)$ | documento 18 | `modelo_micro.md`, seção 3 | o modelo canônico parava no custo integrado e nunca chegava à bolsa |
| Equações originais de Redding & Rossi-Hansberg e de Choné & Ma | documento 18 | `modelo_micro.md`, seção 3.2 | mesma razão |
| Composição do IVS e correspondência com os blocos de custo | documento 18 **e** `hipoteses_e_viabilidade_empirica.md`, seção 3 | `modelo_micro.md`, seção 3.1 (única cópia) | estava duplicado em dois documentos com redações divergentes |
| Consequência econométrica da não monotonicidade de $c_0'(IVS)$ | `hipoteses_e_viabilidade_empirica.md`, seção 3 | permanece lá, agora sem repetir a teoria | teoria e consequência para estimação são coisas distintas |
| Hipótese de heterogeneidade clínico versus cirúrgico | `hipoteses_e_viabilidade_empirica.md`, hipótese 3 | mesma seção, agora como 4.1, rebaixada a heterogeneidade pré-declarada | não é hipótese principal e concorria com as três centrais |

### O que foi acrescentado a documentos existentes

| Documento | Acréscimo | Motivo |
|---|---|---|
| [`01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md`](01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md) | seção "Formulação curta canônica": a pergunta em uma linha, as duas margens e o bloco "o que a pergunta não é" | feedback da banca pedia simplificação da pergunta; a versão curta precisa ser canônica, não só de slide |
| [`02_teoria/modelo_micro.md`](02_teoria/modelo_micro.md) | seção 4 — condição de aceitação, condição de degrau $\Delta B/p > \Delta c_0$ e estática comparativa que gera H1 a H4 | feedback da banca pedia derivar as hipóteses diretamente da teoria; antes elas apareciam apenas listadas em outro documento |
| [`02_teoria/hipoteses_e_viabilidade_empirica.md`](02_teoria/hipoteses_e_viabilidade_empirica.md) | seção 4 reescrita como leitura empírica das derivadas, com 4.2 mapeando as hipóteses canônicas nas três apresentadas e 4.3 fixando linguagem permitida | as hipóteses eram postuladas no documento empírico, sem ligação formal com o modelo |
| [`03_literatura_empirica/19_literatura_empirica_escolha_locacional_medicos.md`](03_literatura_empirica/19_literatura_empirica_escolha_locacional_medicos.md) | Sivey et al. (2012) na tabela de estudos centrais; seção 7 declarando a lacuna que o trabalho ocupa; seção 8 de referências | Sivey era citado em outro documento sem estar catalogado; a lacuna estava implícita |
| [`04_dados/02_inventario_dados_por_outcome.md`](04_dados/02_inventario_dados_por_outcome.md) | seção 4.1 — números publicados que não reproduzem nas bases | achado da conferência da banca 1, detalhado abaixo |
| [`06_execucao/05_roadmap_execucao.md`](06_execucao/05_roadmap_execucao.md) | bloco "Entrega de banca 1", com estado item a item | a entrega existia e não aparecia em nenhum roadmap |
| [`README.md`](README.md) | seção 1.1 apontando este registro; seção 07 na navegação; regra de precedência ampliada | — |

### Correções de referência

| Problema | Onde | Correção |
|---|---|---|
| Link para `04_dados/20_dossie_bases_dados_saude_brasil_pmme.md`, arquivo inexistente | `README.md` | referência removida |
| Links para `02_teoria/17_fundamentacao_teorica_formacao_utilidade_regressores.md`, arquivo inexistente | três documentos de `90_arquivo_historico/` | redirecionados para `02_teoria/modelo_micro.md` |
| Referências por número — "documento 17", "documento 19", "documentos 12–14" — a arquivos que já haviam sido renomeados | `README.md`, seções 3 e 6, e documento 19 | substituídas por nome e link do arquivo vigente |

### Achado de proveniência registrado

A figura de distribuição regional do PMM-E usada no material anterior **não é
reprodutível** a partir de `data/`. Apenas o Nordeste, 60,3%, coincide com o
ciclo 1 de `pmm_especialistas_nominal.csv`. Na mesma base, o Sudeste é 23,0% e
não 10,6% — diferença de 12,4 pontos percentuais, no sentido de exagerar a
redistributividade do programa. Recortes alternativos testados, ciclos 1+2,
série histórica de dez/2025 e contagem de municípios distintos, também não
reproduzem o conjunto.

Registrado em [`04_dados/02_inventario_dados_por_outcome.md`](04_dados/02_inventario_dados_por_outcome.md),
seção 4.1, e detalhado em
[`07_apresentacoes/banca1/03_proveniencia_figuras_e_numeros.md`](07_apresentacoes/banca1/03_proveniencia_figuras_e_numeros.md).

### Conteúdo do deck anterior que foi descartado

O arquivo `PEE__Modelo_econômico.pptx` trazia, no slide de literatura, seis
referências de economia do crime — Becker (1968), Ehrlich (1973), Fella &
Gallipoli (2014), Bennett & Ouazad (2020), Dix-Carneiro et al. (2018),
Deshpande & Mueller-Smith (2022) — sem relação com escolha locacional médica.
Nenhuma delas entrou na documentação. O slide foi refeito com a literatura
canônica do projeto.

---

## 09/09/2026 — Quarta revisão da banca 1: seis seções, 18 slides e edital no repositório

Motivo: o sumário do conteúdo usava "Parte I/II/III", que não é a estrutura da
banca 1. A estrutura correta tem seis seções — motivação, pergunta, literatura
teórica, modelo microeconômico, hipóteses, viabilidade empírica — e cada uma
pode ocupar quantos slides o argumento pedir. O conteúdo foi reescrito para
essa estrutura e aprofundado onde estava raso.

### O que mudou em [`07_apresentacoes/banca1/02_conteudo_slides.md`](07_apresentacoes/banca1/02_conteudo_slides.md)

| Seção | Antes | Agora |
|---|---|---|
| 1. Motivação | 3 slides | 8 slides, em três blocos: **problema** (retrato nacional da Demografia Médica 2025 e manchetes; nossos dados por faixa; as desvantagens na visão do médico), **política** (o que é o PMM-E — lei, quem participa, aprimoramento em serviço, 16 cursos, como a vaga chega, ciclo 1 por região; e a regra IVS → faixa → bolsa) e **efeito incerto** (evidência a favor; evidência contra; o preenchimento do ciclo 1 por faixa e por estrato) |
| 2. Pergunta | 1 slide | 1 slide, com a leitura em dois objetos — preço e desvantagem |
| 3. Literatura teórica | tabela | tabela com parágrafo dizendo o que cada tradição resolve |
| 4. Modelo | 2 slides | 4 slides: decisão; **o que a bolsa paga e o que não paga** (novo — bolsa e mercado local); custo; **o IVS organiza o custo** (novo — as três dimensões do índice e o sinal ambíguo de $c_0'$) |
| 5. Hipóteses | 1 slide | 1 slide, derivação em quatro passos |
| 6. Viabilidade | 1 slide | 1 slide, com custo de vida e distância da família na tabela |

### O que foi criado

| Arquivo | Conteúdo | Por que existe |
|---|---|---|
| `data/raw/aquisicao/ivs_regra/edital_sgtes_03_2025_dou.pdf` | texto integral do Edital SGTES/MS nº 3/2025 (DOU, 24/07/2025), SHA-256 `417c82d9…d9afb2` | o repositório tinha só o FAQ da bolsa; o slide "O que é o PMM-E" cita itens do edital (objeto, requisitos, cursos, escolha de locais, barema, bolsa) que precisavam de fonte primária local |
| `output/apresentacao_banca1/vagas_ciclo1_por_regiao.png` | células e vagas imediatas do ciclo 1 por região | figura do slide 6, gerada por script |
| `output/apresentacao_banca1/preenchimento_ciclo1.png` | proporção de células preenchidas por faixa anunciada e por estrato territorial | figura do slide 10, gerada por script a partir das tabelas descritivas do módulo A4 |

### O que foi acrescentado a documentos existentes

| Documento | Acréscimo |
|---|---|
| [`07_apresentacoes/banca1/01_roteiro_narrativo.md`](07_apresentacoes/banca1/01_roteiro_narrativo.md) | arco reescrito nas seis seções; títulos dos 18 slides; quarta rodada de ajustes; tempo estimado |
| [`07_apresentacoes/banca1/03_proveniencia_figuras_e_numeros.md`](07_apresentacoes/banca1/03_proveniencia_figuras_e_numeros.md) | figuras F5 e F6; números dos slides 3, 5, 6 e 10; fontes documentais externas conferidas em 09/09/2026 |
| [`07_apresentacoes/banca1/README.md`](07_apresentacoes/banca1/README.md) | estrutura em seis seções; estado por seção |
| `scripts/apresentacao/gerar_figuras_banca1.py` | funções `figura_vagas_por_regiao` e `figura_preenchimento_ciclo1`; manifesto com as novas entradas |

### Fontes externas conferidas para o slide 3

Demografia Médica no Brasil 2025 (Scheffer et al., FMUSP/AMB): 597 mil
médicos em 2024, 353.287 especialistas (59,1%); Sudeste com 55,4% dos
especialistas e Norte com 5,9%; 453 especialistas por 100 mil habitantes no
Distrito Federal, 68 no Maranhão e 70 no Pará — conferidos na cobertura da
Agência Brasil (abril de 2025). Portaria GM/MS nº 7.061/2025 reconheceu
situação de urgência em saúde pública por 24 meses em razão do tempo de espera
na atenção especializada. A manchete do Senado Notícias de 25/09/2025 foi
conferida na página original.

---

## 09/09/2026 — Terceira revisão da banca 1: escopo teórico e saída de Reinhardt

Motivo: terceira rodada de revisão do autor, fixando o escopo da banca.

### Regra de escopo

**A banca 1 é teórica.** Fora da motivação, nenhum slide traz literatura
empírica, econometria ou estimação. A motivação é a exceção declarada: ali,
antes da pergunta, entra evidência sobre o que se pode esperar da política,
inclusive de trabalhos empíricos, porque é o que justifica perguntar. A regra
está em
[`07_apresentacoes/banca1/01_roteiro_narrativo.md`](07_apresentacoes/banca1/01_roteiro_narrativo.md),
seção 2.4.

Consequências: o slide 11 foi reescrito sem vocabulário econométrico — passa a
perguntar se há como medir cada peça do modelo e declara as duas que ficam de
fora, a renda no mercado privado local e a distância até a família. O slide 5
descreve o desenho de cada estudo em palavras comuns.

### Reinhardt retirado do slide 7

Choné e Ma (2011) já escrevem o custo de atender como $C(q; L, K)$: equipe e
capital instalado já entram no modelo por essa via. O que Reinhardt
acrescentaria é que esses insumos também elevam o benefício produzido — mas
escrever $B(q; L, K)$ em vez de $B(q)$ é **extensão deste projeto**, não dele. A
citação saiu do slide e a extensão passou a ser creditada ao projeto.

Reinhardt permanece como referência secundária em
[`02_teoria/modelo_micro.md`](02_teoria/modelo_micro.md), seção 2.3, agora com a
distinção correta entre os dois canais e com a referência de **1972**, cuja
forma geral $Q = f(H, X_1, \ldots, X_n)$ é verificável, ao lado do livro de 1975
que o projeto citava sem transcrever.

### Slide 5 reescrito como narrativa

No lugar da tabela de quatro estudos, três movimentos: **funciona** — o
experimento mexicano que sorteou o salário anunciado; **é caro** — a régua
australiana e o custo-efetividade brasileiro; **não segura** — a retenção
americana após o fim da obrigação. Fecha com o degrau do PMM-E dentro da faixa
que a literatura estima ser necessária, e com o fato de que no primeiro ciclo a
bolsa maior não trouxe mais gente.

### Títulos simplificados

"Três primitivas teóricas" virou **"De onde vem o modelo"**; "A decisão
locacional do médico" virou **"Como o médico escolhe onde trabalhar"**.

---

## 09/09/2026 — Segunda revisão da banca 1: evidência internacional, retaguarda profissional e estrutura em três partes

Motivo: segunda rodada de revisão do autor, ponto a ponto, sobre a versão em
markdown.

### Estrutura

A apresentação passou de 12 para **11 slides**, organizados em **Parte I —
Introdução** (motivação, pergunta), **Parte II — Teoria** (literatura teórica,
modelo microeconômico, hipóteses) e **Parte III — Empiria** (viabilidade
empírica). O slide de perguntas foi eliminado: a apresentação termina na
viabilidade.

### Mudanças de conteúdo

| Slide | Mudança |
|---|---|
| 3 | passou a explicar as desvantagens territoriais **na perspectiva do médico**. Nova figura de retaguarda profissional. Saíram as manchetes e o gráfico de deslocamento por região |
| 4 | explicação em três passos de como o IVS vira valor de bolsa |
| 5 | refeito: deixa de mostrar a evolução da oferta e passa a trazer **evidência externa** sobre se incentivo financeiro atrai médico para área desassistida |
| 7 | equações corrigidas para renderizar em tabela; Choné & Ma e Reinhardt em linhas separadas, cada um com sua equação original |
| 10 → 11 | a tabela de como cada objeto aparece nos dados saiu das hipóteses e entrou na viabilidade empírica |

### Por que o gráfico de deslocamento saiu

Verificação no edital: a Portaria GM/MS nº 7.177/2025 declara quatro objetivos —
**provimento, fixação, equilíbrio territorial e formação**. Reduzir deslocamento
de paciente **não é objetivo declarado**; fluxo de usuários aparece apenas como
um entre vários critérios de priorização de vagas (Edital SGTES/MS nº 2/2025,
itens 3.8–3.10). Além disso a figura media custo do paciente, quando o slide
trata do custo do médico.

### Acrescentado à literatura empírica

[`03_literatura_empirica/19_...md`](03_literatura_empirica/19_literatura_empirica_escolha_locacional_medicos.md)
ganhou a seção 7, com evidência sobre incentivos financeiros para provimento em
áreas desassistidas, em quatro blocos: o que move a alocação, a ordem de
grandeza do prêmio exigido, a evidência de que é caro ou insuficiente, e a
permanência que não acompanha a atração. Dez referências novas. Os números de
Costa, Nunes e Sanches (2024) foram conferidos no PDF do working paper —
elasticidade de 0,4 e 0,7, redução de 12,4% do desequilíbrio a US$ 15,7 milhões
por ponto percentual contra US$ 2,2 a 5,1 milhões das cotas.

Registro relevante para o desenho: **nenhum estudo dessa literatura usa RDD**. A
evidência causal disponível é RCT de oferta salarial, DiD sobre elegibilidade
geográfica ou coorte observacional.

### Figuras

| Arquivo | Situação |
|---|---|
| `output/apresentacao_banca1/retaguarda_por_faixa.png` | **nova**: colegas da mesma especialidade por município, por faixa |
| `output/apresentacao_banca1/oferta_antes_depois_por_faixa.png` | continua sendo gerada, mas **saiu do deck** |
| `figuras/motivacao_manchetes.png`, `figuras/deslocamento_por_regiao.png`, `figuras/especialistas_por_uf.png` | preservadas, **não usadas** |

Nenhuma figura de fonte externa entra mais no deck: as três em uso são geradas
por script e a quarta é ilustração conceitual do modelo.

### Ressalva de citação

A equação de Reinhardt exibida no slide 7 é a forma geral do artigo de **1972**
no *Review of Economics and Statistics*, não do livro de 1975 que o projeto
cita. Registrado em
[`07_apresentacoes/banca1/03_proveniencia_figuras_e_numeros.md`](07_apresentacoes/banca1/03_proveniencia_figuras_e_numeros.md),
seção 3.

---

## 09/09/2026 — Revisão de conteúdo da banca 1, população do Censo 2022 e achado sobre `populacao_2010`

Motivo: revisão ponto a ponto do autor sobre a primeira versão em markdown, e
a descoberta de que o repositório não tinha denominador populacional válido.

### Conteúdo

A apresentação passou de 15 para **12 slides**, na margem de **preenchimento**
apenas. Mudanças por slide em
[`07_apresentacoes/banca1/01_roteiro_narrativo.md`](07_apresentacoes/banca1/01_roteiro_narrativo.md),
seção 4. As hipóteses foram reduzidas a duas — remuneração real com sinal
positivo e custo locacional com sinal negativo sobre a probabilidade de
preenchimento — e o slide passou a declarar como cada objeto aparece nos dados
e o limite de identificação.

### Criado

| Arquivo | Conteúdo |
|---|---|
| `scripts/aquisicao/06_adquirir_populacao_censo2022.py` | baixa a população residente municipal do Censo 2022 (IBGE/SIDRA, tabela 4709), com bruto em `data/raw/aquisicao/populacao/` e manifesto com hash |
| `output/aquisicao/populacao_censo2022_municipios.csv` | 5.570 municípios, 203.080.756 habitantes |
| `output/apresentacao_banca1/oferta_pre_por_faixa.png` | especialistas por 100 mil habitantes em jun/2025, por faixa de bolsa |
| `output/apresentacao_banca1/oferta_antes_depois_por_faixa.png` | a mesma taxa, mensal, jun/2024 a jul/2026 |

### Removido

| Arquivo | Motivo |
|---|---|
| `output/apresentacao_banca1/distribuicao_regional.png` | participação no total confunde tamanho do programa com tamanho da população; substituída pelas figuras por habitante |

### Achado registrado

`populacao_2010`, única variável populacional de `data/`, **não é população
residente**: soma 41,85 milhões contra 190,76 milhões do Censo 2010, com razão
variando de 0,10 a 0,42 entre municípios. Afeta `estoque_pre_por_10k`, a
covariável `log_pop` dos módulos A4 e A5 e o rótulo da tabela 1 de estatísticas
descritivas. Registrado em
[`04_dados/02_inventario_dados_por_outcome.md`](04_dados/02_inventario_dados_por_outcome.md),
seção 4.0. As saídas históricas não foram reescritas.

### Acrescentado a documentos existentes

| Documento | Acréscimo |
|---|---|
| [`04_dados/02_inventario_dados_por_outcome.md`](04_dados/02_inventario_dados_por_outcome.md) | base derivada de população do Censo 2022; seção 4.0 |
| [`02_teoria/hipoteses_e_viabilidade_empirica.md`](02_teoria/hipoteses_e_viabilidade_empirica.md) | seção 4.2 refeita para as duas hipóteses da banca |
| [`scripts/README.md`](../scripts/README.md) | `apresentacao/` e o script de população no mapa |

---

## 09/09/2026 — Conteúdo da banca 1 em markdown, figuras versionadas e correção da figura regional

Motivo: a entrega passa a ser lida no GitHub e no Obsidian, não montada como
deck. O conteúdo deixa de ser especificação de slide e vira documento legível de
ponta a ponta, com as figuras dentro do repositório.

### Estrutura da apresentação

Reorganizada nas três partes da banca 1, no lugar dos seis blocos anteriores:

| Parte | Conteúdo | Slides |
|:---:|---|:---:|
| 1 | Motivação e pergunta | 3–7 |
| 2 | Literatura teórica, modelo micro e hipóteses | 8–12 |
| 3 | Viabilidade empírica | 13–14 |

O slide de literatura passou a liderar pela literatura **teórica**, com cada
trabalho declarando qual primitiva fornece e onde ela entra no modelo. A
evidência empírica ficou como bloco de apoio ao argumento da lacuna.

### Figuras

| Arquivo | Origem |
|---|---|
| `docs/07_apresentacoes/banca1/figuras/motivacao_manchetes.png` | externa, preservada do material anterior |
| `docs/07_apresentacoes/banca1/figuras/especialistas_por_uf.png` | externa, Demografia Médica no Brasil 2025 |
| `docs/07_apresentacoes/banca1/figuras/deslocamento_por_regiao.png` | externa, REGIC 2018 |
| `output/apresentacao_banca1/bolsa_por_faixa.png` | gerada por script |
| `output/apresentacao_banca1/distribuicao_regional.png` | gerada por script |

Criado `scripts/apresentacao/gerar_figuras_banca1.py`, que grava as duas figuras
geradas e um `manifesto_figuras.json` com hash SHA-256 da base de entrada,
recorte aplicado, data de referência e as constantes externas usadas.

### Pendência encerrada

A figura de distribuição regional foi regerada a partir de
`data/pmm_especialistas_nominal.csv`, ciclo 1. Os valores corretos são Nordeste
60,3%, Sudeste 23,0%, Norte 12,1%, Centro-Oeste 3,6% e Sul 1,0%. A versão
anterior trazia o Sudeste com 10,6%, doze pontos percentuais abaixo, o que
exagerava a redistributividade afirmada no slide. Permanece aberta apenas a
pendência de manifesto das figuras de fonte externa.

### Removido

A seção de restrições de template e a decisão sobre equações nativas em
PowerPoint saíram do documento de conteúdo. Eram específicas da produção de
`.pptx`, que deixou de ser o formato da entrega.

---

## Antes de 09/09/2026

A reorganização em seções numeradas 01 a 06, com `90_arquivo_historico/`, é
anterior a este registro e está descrita na
[`README.md`](README.md), seções 2 e 4. Os documentos 07 a 11 e as versões 15 e
16 foram arquivados naquela ocasião, sem entrada individual.
