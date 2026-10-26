# 42. Auditoria do adendo 48c: capitais e UF no corte 0,300 (H1)

> **Data:** 26/10/2026.<br>
> **Objeto:** adendo [`48c`](../06_execucao/48c_adendo_capitais_e_UF.md), script `scripts/rdd_bolsa/41_h1_capitais_uf.py`,
> saídas `output/rdd_bolsa/HC_*`, referência `output/aquisicao/ibge_capitais_uf_regiao.csv` com o manifesto, e doc
> [`57o`](../06_execucao/57o_h1_capitais_uf.md). O trabalho tinha entrado no branch como WIP (commit `384a2a0`), sem
> testes e sem auditoria. Base: branch `claude/vigilant-mccarthy-dd92mc`, commit `f97e1ca`.<br>
> **Método:** duas partes. (1) Completar: testes, `run_all.py`, conferência da aquisição. (2) Recalcular de forma
> independente com `scripts/auditoria_H1/a42_auditoria_capitais_uf.py`, que não importa o 41, a `rdd_lib` nem a
> reconstrução da auditoria 36. Ele lê a base de células já auditada (`output/auditoria_H1/a36_celulas.csv`), o IVS
> oficial (a08) e o quadro bruto do ciclo 2 de 13/02/2026, com leitor próprio. Estimador, CR1, BKY e leitura foram
> escritos do zero. Saídas em `output/auditoria_H1/a42_recalculo.csv` e `a42_resumo.json`.<br>
> **Estatuto do que se audita:** `ADENDO_48C_POS_RESULTADO`, robustez pós-resultado. O contraste é o pacote do corte,
> nunca a participação no PMM-E.

## Veredito

**Aprovado com correções.** Recalculei 42 linhas: o C-1 inteiro, a base e C-2 a C-4 nos dois cortes, e uma linha
do C-5. Todas batem com `HC_estimativas.csv` até 7e−14 no salto e 2e−14 no EP. As contagens de municípios e de
capitais e os q-valores de BKY são iguais. A leitura pré-registrada refeita dá o mesmo: em 0,300, "anda junto com
capitais ou região"; em 0,400, "relatar como está".

**Nenhuma estimativa mudou.** `HC_estimativas.csv` e as quatro figuras ficaram iguais byte a byte depois de rodar o 41
de novo. `HI_*` e `CL_*` não foram regravados.

As correções foram de texto, de conferência e de pipeline:
- o 57o repetia "e não com a bolsa" como conclusão própria e não dizia que a queda da HI-2 já não passava no Holm
  do 48b;
- a explicação do salto do Nordeste estava errada;
- a conferência contra o 48b estava pendente;
- faltavam os testes e o lugar no `run_all.py`.

Um ponto fica para o autor: a fonte do IBGE não foi arquivada.

> **Nota de 26/10/2026: A1 resolvido.** O autor autorizou o download. O script
> `scripts/aquisicao/a19_arquivar_ibge_capitais_uf.py` baixou de novo, das mesmas URLs do manifesto do 41, o ZIP de
> Localidades do Brasil 2022 (4.511.488 bytes, `Last-Modified` igual ao de 15:48) e as 6 respostas do SIDRA 4709
> (de 799 a 2.349 bytes). Os 7 SHA-256 são iguais aos do manifesto `manifesto_ibge_capitais_uf_regiao.json`. Os brutos
> estão em `data/raw/aquisicao/ibge_capitais_uf/`, um diretório novo, e não em `territorio/`, como sugeria a decisão
> abaixo: assim nenhum arquivo já existente em `data/` foi tocado. O manifesto de arquivamento é
> `output/aquisicao/a19_manifesto_arquivamento_ibge_capitais_uf.json`.
>
> Sem rede, o modo `--verificar` reconstrói `ibge_capitais_uf_regiao.csv` do bruto arquivado, e o resultado é
> idêntico byte a byte (SHA-256 `e4c9ffb6…`, o do manifesto). O DBF extraído também tem o SHA-256 registrado. Nada do
> pipeline mudou: o 41, a cópia, o manifesto do 41 e as saídas `HC_*` ficaram como estavam. Teste:
> `tests/test_arquivamento_ibge_capitais.py`. Isso fecha também a recomendação A8 da auditoria 40 para esta
> referência.

## Achados, por gravidade

### Médios

**A1. A referência do IBGE não tem a fonte arquivada (resolvido em 26/10/2026; ver a nota no veredito).** O manifesto `manifesto_ibge_capitais_uf_regiao.json` está
completo nos campos. Ele traz:
- fonte oficial: IBGE, Localidades do Brasil 2022, e SIDRA 4709 para a região de cada UF;
- URL, data de acesso (26/10/2026) e `Last-Modified`;
- SHA-256 do ZIP, do DBF e de cada resposta do SIDRA, e SHA-256 da cópia;
- filtro, cobertura, unidade e chaves.

Mas o ZIP e as respostas foram lidos em memória e **não foram gravados** em `data/raw/`, como nas outras aquisições
(a08, população do Censo, REGIC). Sem rede, o CSV não pode ser reproduzido. O script de aquisição existe e está
versionado: é o modo `--baixar-referencias` do próprio 41. O que falta é a fonte arquivada. Por isso **não criei**
um script novo de reprodução: não há fonte local de onde reproduzir, e baixar de novo estava fora do escopo.

O que deu para conferir sem rede:

| Conferência | Resultado |
|---|---|
| SHA-256 do CSV igual ao do manifesto | sim |
| região de cada UF igual à da REGIC 2018 do IBGE, arquivada em `data/raw/aquisicao/territorio/` | 27 de 27 |
| região de cada UF igual à coluna "Região" do quadro bruto do ciclo 2 (MS) | 27 de 27 |
| região igual à dada pelo 1º dígito do código da UF (convenção do IBGE) | 27 de 27 |
| código das 27 capitais existe na REGIC 2018 | 27 de 27 |
| municípios marcados CAPITAL no quadro do ciclo 3 estão na lista | 22 de 22 |
| lista igual à que a auditoria 36 digitou | sim |

A região está confirmada por uma fonte oficial arquivada. A lista de capitais está confirmada só em parte: a REGIC não
marca capital, o quadro do ciclo 3 marca 22 das 27, e a lista da auditoria 36 foi digitada, não lida de uma fonte.

**Decisão do autor:** autorizar um download para arquivar o ZIP e as respostas do SIDRA em
`data/raw/aquisicao/territorio/`. Isso seria feito por uma etapa de aquisição própria, que confere o SHA-256 contra
este manifesto. Atende também à recomendação A8 da auditoria 40. Até lá, o 41 no pipeline lê a cópia e confere o
hash, sem rede.

**A2. "E não com a bolsa" e a queda que não passava no Holm (corrigido no texto).** A regra do 48c, §2, diz "e não com a
bolsa". O 57o aplicou a regra certo e citou o texto pré-registrado. Mas a frase "Para dizer na banca" repetia "A queda
anda junto com essas poucas capitais grandes, e não com a bolsa" como conclusão própria. Isso contradiz o próprio
limite do 57o: "não diz [...] que a bolsa não tenha efeito".

Faltavam também duas coisas:
- **O Holm do 48b.** A única linha com queda a explicar é a HI-2 em 0,300. Ela tem p = 0,032 sem correção, mas p de
  Holm = 0,126 nas primárias do 48b. A queda já não rejeitava zero na especificação principal.
- **Quanto do ponto sobra.** A regra só olha o IC, e o IC da HI-2 excluía zero por pouco. Com a dummy de capital, o
  ponto vai de −1,13 a −0,83 médico por município: 73% do ponto continua. Com o efeito fixo de UF, vai a −0,32 (29%).
  Sem as capitais, vai a −0,30 (27%). "Deixa de se distinguir de zero" é verdade nos três ajustes. "O salto some" só
  vale com UF e sem capitais.

Correção no gerador (`resposta_curta`, `frase_banca`, `gerar_doc`), só no texto:
- o significado de "e não com a bolsa" ficou explicado: o corte não separa a bolsa da composição de capitais;
- o p de Holm do 48b agora aparece, lido de `HI_estimativas.csv`;
- entrou um limite novo, "A regra do §2 olha só o IC", com a fração do ponto que sobra em cada ajuste.

A leitura pré-registrada não mudou, e a regra foi aplicada certo.

**A3. A explicação do salto do Nordeste estava errada (corrigido).** No C-1, a fração de municípios do Nordeste cai
47,7 p.p. no corte [−82,6; −12,8]. As médias cruas da janela de 0,050 vão no sentido oposto (26% abaixo, 39% acima).
O 57o explicava isso com "logo abaixo estão capitais do Nordeste".

Na faixa de 0,010 abaixo do corte, na amostra da H1, há 20 municípios × ciclo:
- 12 são do Nordeste, e só 2 desses são capitais (Natal, em dois ciclos);
- logo acima, 19% são do Nordeste.

O desbalanceamento de região perto do corte é sobretudo de municípios do Nordeste que não são capitais. O texto agora
dá esses números, e o 57o ganhou o bloco `composicao_estreita`, com as médias cruas na janela de 0,010. Isso pesa na
leitura: o 48c diz "capitais (ou região)". Os dados mostram dois desbalanceamentos que se sobrepõem só em parte.

### Baixos

**A4. Conferência contra o 48b pendente (corrigido).** Quando o 41 rodou, `HI_estimativas.csv` ainda não estava no
branch, e o 57o dizia "pendente". Rodei o 41 de novo. Agora diz "conferido": as 4 linhas (HI-1 e HI-2 × 2 cortes) são
iguais às primárias do 48b, com diferença máxima de 3,0e−14. O teste novo refaz essa conferência.

**A5. Sem testes, fora do pipeline, manifesto A6 desatualizado (corrigido).**
- Criei `tests/test_h1_capitais_uf.py`, com 22 testes.
- Pus o 41 no `run_all.py`, depois do 40 e antes do 44, que importa dele a leitura da referência.
- `tests/test_pipeline_rdd_bolsa.py` tem a cadeia e as dependências do 41: 40, 24, 23 e a08 antes; o 41 antes do 44.
- O manifesto A6, regerado pelo gerador, ganhou o 41. Ganhou também o 43 e o 44, que já faltavam desde o 48d e o
  protocolo 64.

**A6. Robustez pós-resultado: dita e coerente com a ordem dos commits (verificado, sem correção).**
- O adendo se declara `ADENDO_48C_POS_RESULTADO` e diz "Em qualquer caso é robustez pós-resultado".
- O 57o repete isso no cabeçalho, na resposta curta, na frase da banca e no primeiro limite.
- O SHA-256 do adendo em `HC_resumo.json` é igual ao do arquivo.

A ordem dos commits é coerente:

| Hora (UTC) | Commit |
|---|---|
| 15:34 | auditoria 36 (`1756209`): já tinha visto o desbalanceamento de capitais e a HI-1 sem ajuste |
| 15:35 | adendo congelado (`4326241`) |
| 15:44 | 48b executado (`232e81a`) |
| 15:48 | referência do IBGE baixada |
| 15:54 | WIP do 48c (`384a2a0`) |

O adendo é pós-resultado para a HI-1 e para a dummy de capital, e diz isso.

**A7. O efeito fixo de UF se apoia em metade das UFs.** Na janela de 0,050 em 0,300, a amostra da HI-2 tem municípios
de 24 UFs. Só 14 delas têm município dos dois lados do corte, e a C-3 se identifica por essas 14. O 57o já diz isso em
palavras. O número fica registrado aqui.

**A8. Linhas a mais, declaradas.** O 41 acrescenta o C-1 no quadro inteiro e o A3 com o tipo de vaga de 13/02 no C-5.
As duas coisas estão nas decisões do 57o, fora do BKY e da leitura. Não mudam nada do que o adendo pede.

## O que segue o adendo (verificado)

- **Especificação base do 48b:**
  - local linear, kernel triangular, h = 0,050, |IVS − corte| < h;
  - cada corte separado;
  - ciclos 1–3 empilhados, com intercepto, inclinação e inclinação × lado por ciclo, e salto comum;
  - CR1 por município, com fator G/(G−1)·(n−1)/(n−k).

  Refiz tudo isso com código próprio e bate.
- **HI-1:** células com pelo menos 1 vaga imediata, EF de curso × ciclo.
- **HI-2:** alocados nessas células por município × ciclo, com as vagas imediatas delas como controle, um coeficiente
  por ciclo.
- **Ciclo 2 pelo quadro de 13/02/2026:** li o quadro bruto com um leitor próprio (1º bloco "TOTAL" das vagas
  imediatas, por CNES × curso). As vagas imediatas pré-alocação das 1.547 células do ciclo 2 são iguais às da base:
  0 diferenças.
- **Capitais e UF:** capital pela lista do IBGE; UF pelos dois primeiros dígitos do código. A sigla do quadro é igual à
  do código em todas as células.
- **BKY:** entre as 12 linhas C-2 a C-4, como manda o adendo. Todos os q = 1,000.
- **Running variable:** só o IVS 2010 oficial (a08). O rastreio de arquivos abertos no recálculo não registrou o arquivo
  de IVS errado. No 41, o caminho dele só aparece no `a36_reconstruir_H1.py`, numa conferência de texto, nunca numa
  leitura (o teste confere). Nenhum dado do CNES é usado.

## O que foi recalculado

Tudo em `output/auditoria_H1/a42_recalculo.csv`, com a diferença contra o gravado em cada linha.

**C-1, balanço no corte, amostra da H1, por município × ciclo (p.p.):**

| Corte | É capital | É do Nordeste | É do Norte |
|---|---|---|---|
| 0,300 | −29,9 [−57,1; −2,8] | −47,7 [−82,6; −12,8] | +18,4 [−6,0; +42,7] |
| 0,400 | −9,7 [−24,2; +4,9] | +7,1 [−30,5; +44,7] | −10,1 [−43,9; +23,7] |

Por célula, em 0,300: capital −38,7 [−71,2; −6,1]; Nordeste −66,3 [−108,6; −23,9]. No quadro inteiro, em 0,300:
capital −17,8 por município e −50,3 por célula, iguais aos da auditoria 36. As 24 linhas do C-1 batem com o gravado.

**Capitais perto do corte:**
- em 0,300, na janela de 0,050: 13 abaixo e 6 acima;
- em 0,300, a menos de 0,010: 4 abaixo (São Paulo, Goiânia, Natal, Brasília) e nenhuma acima;
- em 0,400: 3 abaixo e nenhuma acima.

**C-2 a C-4 em 0,300:**

| Linha | HI-1 (p.p.) | HI-2 (médicos por município) |
|---|---|---|
| base (48b) | −3,7 [−21,3; +13,9] | −1,13 [−2,15; −0,10], p 0,032 (Holm no 48b: 0,126) |
| C-2, dummy de capital | +2,6 [−15,7; +21,0] | −0,83 [−1,87; +0,21], p 0,119 |
| C-3, efeito fixo de UF | +4,0 [−11,0; +19,0] | −0,32 [−1,31; +0,66], p 0,519 |
| C-4, sem capitais | +2,9 [−16,3; +22,1] | −0,30 [−1,22; +0,62], p 0,525 |

Em 0,400, as 8 linhas também batem, todas com IC que contém zero.

**Uma linha do C-5: taxa por vaga oferecida (S-e), 0,300, quadro inteiro.** Sem ajuste, −16,0 p.p.
[−27,9; −4,1]. Com efeito fixo de UF, +0,5 p.p. [−8,4; +9,4]. Igual ao gravado.

**Leitura pré-registrada, refeita das minhas linhas:**
- em 0,300, o C-1 mostra salto (capital e Nordeste). A linha a explicar é a HI-2, e os três ajustes levam o IC dela a
  conter zero. Leitura: "anda junto com capitais ou região";
- em 0,400, não há salto no C-1 nem queda a explicar. Leitura: "relatar como está".

## O que foi mudado

| Arquivo | Mudança |
|---|---|
| `scripts/rdd_bolsa/41_h1_capitais_uf.py` | texto gerado (A2, A3); p de Holm do 48b lido na conferência; composição na janela de 0,010; link para esta auditoria |
| `output/rdd_bolsa/HC_resumo.json` | conferência contra o 48b "CONFERIDO", p de Holm, composição na janela de 0,010 |
| `docs/06_execucao/57o_h1_capitais_uf.md` | regerado pelo script |
| `tests/test_h1_capitais_uf.py` | novo |
| `run_all.py`, `tests/test_pipeline_rdd_bolsa.py`, `tests/README.md` | o 41 entra no pipeline, antes do 44 |
| `output/tema_trabalho/A6_manifesto_reproducao.json` | regerado (41, e o 43 e o 44 que faltavam) |
| `scripts/auditoria_H1/a42_auditoria_capitais_uf.py`, `output/auditoria_H1/a42_*` | recálculo desta auditoria |

`HC_estimativas.csv`, as figuras `HC_figuras/*`, `HI_*` e `CL_*` ficaram iguais byte a byte.

Testes rodados: `tests/test_h1_capitais_uf.py` (22), `tests/test_pipeline_rdd_bolsa.py` e
`tests/test_controles_localizacao_medicos.py` (40 juntos), e `tests/test_red_team_a6.py` (15), por causa do manifesto.
Todos passaram.
