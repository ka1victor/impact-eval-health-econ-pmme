# 55. Auditoria do deck da banca 2 revisto pela rubrica (7 minutos; 11 slides no corpo e 2 no apêndice)

> **Data:** 27/10/2026, véspera da banca 2.<br>
> **Objeto:** `output/apresentacao_banca2/deck_banca2_curto.pptx` e `.pdf` no commit `4748ad1` (branch
> `claude/vigilant-mccarthy-dd92mc`, igual à `origin/main`); a figura nova `curto_dados_amostra.png` e os códigos
> `AM_*` de `numeros_banca2.json`; os docs 03, 04, 06 (§4), 08, 09, 10 e README da banca 2; a cópia
> `output/apresentacao_banca2/versoes/deck_banca2_curto_8901dea.pdf`; o gerador `scripts/apresentacao/gerar_deck_banca2.py`
> e os testes `tests/test_deck_curto_banca2.py`, `tests/test_conteudo_banca2.py` e `tests/test_sintese_H2.py`.<br>
> **Referências:** `CLAUDE.md`; [doc 07](../07_apresentacoes/banca2/07_nova_hipotese.md); [doc 66](../06_execucao/66_analise_completa_H2.md)
> e [auditoria 52](52_auditoria_analise_H2.md); auditorias [50](50_auditoria_avaliacao_hipoteses.md) e
> [53](53_auditoria_deck_H2.md) (redação); docs 57p, 57i, 57a, 57v, 57x e 57y; a rubrica da banca (planilha do autor,
> nove critérios; [doc 06](../07_apresentacoes/banca2/06_estrutura_obrigatoria_versao_final.md), §4).<br>
> **Método:**
> 1. texto e notas lidos com python-pptx; PDF renderizado em PNG (80 dpi, e 60 dpi para simular projeção) e visto
>    slide a slide;
> 2. cada número da tela, das notas, do roteiro (doc 09) e do mapa (doc 10) conferido contra o seletor do registro e
>    a saída de origem; o funil `AM_*` relido de `P1_resumo.json` e conferido contra a lógica de exclusão do script
>    25 (`carregar()`) e contra o `mesma_amostra` do `VC_resumo.json`;
> 3. tempo do roteiro recontado com a função de palavras do gerador e reestimado com os números por extenso;
> 4. hash da cópia `8901dea` conferido com `git show 8901dea:output/apresentacao_banca2/deck_banca2_curto.pdf`;
> 5. testes rodados antes e depois com o deck do grupo (`PMME_DECK_GRUPO`), o que inclui o teste de determinismo.
>
> Nada foi reestimado. Nada foi gravado em `data/` nem nas saídas de estimação.

## Veredito

**Aprovado com correções.** As correções são de redação e de tempo de fala; nenhum número estava errado. Todas já
foram aplicadas no doc 04 (fonte da verdade), nos docs 03, 08, 09 e 10, nos testes e no deck regerado.

- **Números.** Todos os números da tela, das notas, do doc 09 e do doc 10 conferem com a saída de origem (seção 3).
  O funil está certo e cada etapa está bem definida.
- **Cópia anterior.** O SHA-256 de `versoes/deck_banca2_curto_8901dea.pdf` é
  `66fa8369fbc68eb23456a103a9585d90c3935a2fb913e423f8cb9053a20c66df`, igual ao do `git show 8901dea:…` e ao citado
  no doc 10 e no manifesto.
- **Forma.** As 8 seções estão na ordem. Cada slide tem até 30 palavras. Toda figura tem "Como ler". Nada fica
  cortado nem passa sobre o logo. A figura do funil é legível mesmo a 60 dpi.
- **Testes.** Antes e depois: 118 passaram, sem pulos (`test_deck_curto_banca2`, `test_conteudo_banca2` e
  `test_sintese_H2`, com o determinismo do `.pptx`).

## 1. Achados, por gravidade

Não há achado grave: nenhum número está errado, o teste central está bem descrito e as frases obrigatórias das
auditorias 50, 52 e 53 estão todas lá.

### Médios (corrigidos)

**M1. O tempo de 7:00 é otimista: os números falados contam como uma palavra, mas são ditos com várias.**

- A soma dos tempos-alvo confere: 35 + 50 + 25 + 35 + 45 + 30 + 50 + 40 + 40 + 30 + 40 s = 7:00. A contagem também:
  eram 982 palavras, a 140 por minuto.
- O problema é o que se diz em voz alta. "1,94" vira "um vírgula noventa e quatro"; "932.577" vira onze palavras.
  Com os números por extenso, o roteiro dava cerca de 1.090 palavras, perto de 7:50 a 140 por minuto. Isso sem a
  troca de slides e sem folga.
- Três slides ficavam acima de 165 palavras por minuto: 2 (o funil inteiro falado), 3 (368 de 368, 454 de 454) e 7
  (5.421 e o IC de 1,48 a 2,40).

**Correção:**
- o roteiro dos slides 2, 3, 4, 7 e 11 fala menos números; eles continuam na tela;
- agora são 944 palavras escritas, cerca de 1.010 com os números por extenso, perto de 7:10 a 140 por minuto;
- o doc 09 diz isso e lista três cortes seguros caso o ensaio passe de 7 minutos;
- as ressalvas obrigatórias não foram cortadas.

**M2. A leitura do coeficiente não dizia contra o quê se compara (slide 7).**

A linha dizia "Na UF de origem, chance 11,0 vezes maior". No logit condicional, exp(θ_UF) = P(j)/P(k). Ou seja, é a
razão entre as probabilidades de escolher duas vagas que só diferem nesse atributo: uma na UF de origem, a outra em
outra UF, à mesma distância. Pelo 57i (Como ler), o termo é também a categoria "mesma UF fora da região de saúde",
contra outra UF à mesma distância.

Traduzir "razão de chances" por "chance N vezes" está certo em português técnico ("chance" = *odds*). O que faltava
era o termo de comparação, e "11,0 vezes maior" pode ser ouvido como "a probabilidade desta vaga vira 11 vezes".
Isso só vale de forma aproximada, para vagas de probabilidade pequena.

**Redação certa e simples:**
- tela: "UF de origem vs. outra UF: chance ×11,0; toda a bolsa: ×1,57 (IC contém 1)";
- fala: "entre duas vagas iguais no resto, inclusive na distância, a da UF de origem tem 11,0 vezes a chance de ser a
  1ª opção";
- na bolsa: "toda a diferença de bolsa multiplica a chance por 1,57, e esse intervalo contém 1: sozinho, o peso da
  bolsa não se distingue de zero". Antes era "sozinha, ela não se distingue de zero", que misturava a razão (1) com o
  peso (0).

O slide 8 passou de "chance 1,47 vez maior" para "chance ×1,47", na notação das figuras; o comparador ("na mesma UF,
+R$ 5 mil") já estava. As notas dos slides 7 e 8 e o doc 09 (perguntas) têm a frase completa.

**M3. Limitações: a coluna "Implicação" repetia a limitação em três de seis linhas, e o roteiro contradizia as notas.**

- "Pacote do corte → bolsa não isolada", "Só ciclo 2 → bolsa instável" e "Origem = CNES → não é residência" são
  descrições, não implicações. Com 30 palavras na tela, a profundidade que a rubrica pede ("discute de forma mais
  aprofundada suas implicações") depende da fala. A tela é só a deixa.
- O roteiro dizia "a origem é o vínculo no CNES, não a residência: laços de família ficam de fora". Mas as notas do
  mesmo slide e o doc 66 §5 dizem que θ_UF "junta família, rede, registro…". A família não fica de fora: ela entra
  misturada.

**Correção:**
- "Só ciclo 2 → não generalizar", no mesmo número de palavras;
- o roteiro diz a implicação de cada uma: "pede dados novos"; "não é causa da escolha"; "nada diz quantos médicos a
  bolsa atrairia"; "vale para o pacote, não para os R$ 5 mil sozinhos"; "não dá para generalizar"; "para quem
  trabalha longe de casa, [a origem] é a do trabalho";
- "Pacote do corte → bolsa não isolada" e "Origem = CNES → não é residência" ficaram, porque não há palavra sobrando
  no slide (30/30); a implicação vai na fala e, com detalhe, nas notas.

### Menores (corrigidos)

**m1. Título do slide 10, "Conclusão: a origem pesa mais que a bolsa? Sim".** Não é exagero. É exatamente o que o
D_UF testa: θ_UF − 10β > 0, com p unilateral < 0,001 no M1, IC acima de zero nos três ciclos (secundárias, sem Holm;
auditoria 53) e em todas as variantes (doc 66 §7). A condição é que "a bolsa" seja **toda** a diferença de bolsa
(R$ 10 → 20 mil), e "a origem", a vaga na UF de origem à mesma distância.

Sem o "toda", o título pode ser ouvido como "a bolsa não importa", o que o slide 8 desmente. Passou a "Conclusão: a
origem pesa mais que toda a bolsa? Sim" (51 caracteres), igual ao título do slide 7. A robustez também ganhou o
"toda" ("Mantém: origem pesa mais que toda a bolsa nos três ciclos"). O caráter exploratório do "Sim" é dito no
slide 1 e na tabela de Limitações.

**m2. Roteiro do slide 5: "tudo o que é dele, como idade, nota ou família, é igual entre as vagas e sai da conta".**
"Família" não sai da conta: a distância até a família varia entre vagas e entra, misturada, em θ_UF e na distância.
Ficou "como idade ou nota".

**m3. Slide 6, "Conjunto | todas as vagas vistas".** Na coluna "Aderência", soava como verificado. Mas é uma premissa
que não se testa (doc 66 §5: o candidato viu todas as vagas e listou sem estratégia). Passou a "suposto: todas
vistas". O doc 09 ganhou a pergunta provável "a 1ª opção é a preferência verdadeira, se a alocação é por nota?".

**m4. Slide 9, "Não se mantém: peso da bolsa: forte só no ciclo 2…".** Tinha dois-pontos em sequência. Passou a
"peso da bolsa, forte só no ciclo 2; perto do corte, inconclusivo".

**m5. Doc 08 (guia do grupo), passo 6: "os dados sugerem que o custo de sair da própria região domina".** É a forma
que a auditoria 53 (A4) tirou do deck: a evidência é no nível da UF, e "domina" é leitura dita como dado. Ficou "os
dados sugerem que um degrau de R$ 5 mil não compensa sair da própria UF (leitura, sem teste direto)". O "Como ler" do
guia ganhou o termo de comparação do ×11,0.

**m6. Doc 03, linha `G30`.** Ainda trazia o título antigo do slide de robustez. Agora traz "Robustez: o que se
mantém e o que não se mantém", com o antigo entre parênteses.

**m7. Doc 10 (mapa para o grupo):**
- o p 0,072 estava como se estivesse "na linha 'Hipótese: pós-resultado' do slide 7" do deck anterior; estava nas
  notas desse slide (tela, só na cautela do slide 9);
- faltava dizer que a equação em palavras perdeu o "(UF, região, município)";
- o checklist não cobria os critérios 1 (narrativa) e 4 (descritiva ligada à pergunta), nem as ressalvas
  obrigatórias da fala.

Tudo corrigido. A seção 5 nova lista, linha a linha, o que mudou nesta auditoria, para quem já tinha copiado a tela.

### Observações (sem correção)

- **O funil está certo, e cada etapa está bem definida.** O script 25 marca uma exclusão por candidato, nesta
  prioridade:
  1. sem município de origem no G1, por candidato não ligado: 55 · 77 · 69 (`AM_C*_NLIG`);
  2. sem município de origem no G1, por falta de vínculo médico na competência de referência: 20 · 30 · 38
     (`AM_C*_SVIN`);
  3. município de origem sem região de saúde: 0 · 1 · 0;
  4. 1ª opção em município sem região de saúde: 3 · 0 · 0.

  A ordem das faixas do funil é a mesma, então as diferenças `AM_C*_LIG` e `AM_C*_ORI` são exatas. A linha "− sem
  região de saúde" junta os itens 3 e 4 (3 · 1 · 0), como dizem as notas ("a origem ou a 1ª opção").
  `VC_resumo.json` confirma o M1 corrigido com 5.421 candidatos, 932.577 linhas e 56 conjuntos. O 5.425 do slide 4
  é a mesma amostra antes dos itens 3 e 4 (= `ESC_N`).
- **O que fica antes do funil.** O funil começa em "1ª opção numa vaga do quadro". Os 62 candidatos que só têm linha
  de 2ª opção (`candidatos_sem_linha_de_1a_opcao`) ficam de fora antes dele, o que está coerente com o rótulo.
- **"Vaga" é célula.** No modelo, "vaga" é a célula do quadro (estabelecimento × curso; 5.125). Isso inclui células
  sem vaga imediata, já que ter vaga imediata é covariável. "Vaga aberta" é o termo do doc 66; as notas dizem
  "5.125 vagas (estabelecimento × curso)". Se a banca perguntar, a resposta está aí.
- **Doc 07, §2, item 5.** Ainda diz "o custo que domina … é o de sair da própria região", seguido de "os dados
  sugerem (não testado diretamente)". É o documento da decisão do autor, revisado pela auditoria 52; não foi editado
  aqui. O deck, o doc 08 e o doc 10 não usam essa forma.
- **As frases obrigatórias estão todas lá:**
  - "não detectamos aumento" (slide 1 e roteiro);
  - teste central = D_UF (slides 5 e 7);
  - VL-1 "vagas da mesma UF, a de origem ou outra", pós-resultado (slide 8: roteiro, notas e figura);
  - pré-registrado com IC que contém 1 (cautela do slide 9; p 0,072 no slide 8);
  - "os dados sugerem" (slide 10);
  - pacote do corte, preferência revelada e condicional a se candidatar (notas dos slides 1, 6, 7, 9, 10 e 11);
  - 75 km na tela e 119 só nas notas (o teste confere).

  Nenhuma frase proibida aparece no doc 04, no doc 09, no doc 10 nem no deck. No doc 08, aparecem só na coluna "Não
  dizer".

## 2. Notas prováveis pela rubrica (1 a 5), depois das correções

| Critério | Nota provável | Por quê | O que ainda falta (ou depende da fala) |
|---|---|---|---|
| 1. Slides, estrutura, narrativa | 4–5 | pergunta no título do slide 1 e retomada no 10; 8 seções na ordem; uma ideia por slide; figuras grandes com "Como ler" | slides 5, 6, 10 e 11 são só texto; a transição "então a bolsa não pesa? Pesa…" (7 → 8) precisa sair natural na fala |
| 2. Apresentador | 3–4 | roteiro por slide, com tempo e perguntas prováveis | tudo depende do ensaio: o tempo fica perto de 7:10 sem folga; ler o roteiro em voz alta derruba "tom e flexibilidade" — usar como guia, não como texto lido |
| 3. Base de dados | 5 | origem de cada variável, unidade de observação na tela, funil por ciclo com quem sai e por quê, tamanho do modelo | período e datas dos quadros só nas notas (bastam para as perguntas) |
| 4. Análise descritiva | 4 | a regra *sharp* (de onde vem a variação) e onde escolhem (79%, 51 km), ambas ligadas à pergunta e ditas como descritivas | não há descritiva crua bolsa × escolha. É por desenho: a comparação crua mistura bolsa, IVS e origem (doc 66 §3) e a versão perto do corte é inconclusiva; dizer isso se perguntarem |
| 5. Modelo econométrico | 4 | logit condicional com três justificativas (escolha discreta; o candidato comparado consigo mesmo; a bolsa pelos saltos da regra), o IVS em curva contínua e o teste D_UF unilateral com cluster | a equação formal está só nas notas e no doc 66 §4; uma banca de economistas pode pedir U_ij na tela (fica no detalhe para perguntas) |
| 6. Interpretação | 4–5 | razão de chances com termo de comparação (após M2); D_UF em log-chance com p; IC que contém 1 dito como tal; km equivalentes | dizer "entre duas vagas iguais no resto" toda vez; não dizer "probabilidade 11 vezes maior" |
| 7. Robustez | 4–5 | oito especificações e D_UF por ciclo numa figura; "mantém / não se mantém" explícito; o pré-registrado na frente | o "por que o ciclo 2?" fica sem resposta (honesto: "não sabemos") |
| 8. Conclusões | 4–5 | retoma a pergunta, responde "sim" com o que o D_UF testa, separa dado (pontos 1 e 2) de leitura (ponto 3, "os dados sugerem") | o "Sim" é exploratório; a fala deve ligar a ele o slide 11 |
| 9. Limitações | 3–4 na tela; 4–5 com a fala | seis limitações com implicação; após M3 o roteiro diz a consequência de cada uma | na tela, a coluna "Implicação" é telegráfica (30 palavras); **a profundidade que a rubrica pede depende da fala** e das notas ("Implicações, com mais detalhe") |

## 3. Tabela de conferência

Fonte: `rdd/` = `output/rdd_bolsa/`. "Código" é o do registro `numeros_banca2.json`. "Confere" diz se o valor bate
com a saída de origem.

| Slide (onde) | Número(s) | Código | Fonte (arquivo; seletor) | Confere |
|---|---|---|---|---|
| 2 (figura, roteiro, doc 10) | 993 · 2.140 · 2.581; total 5.714 | `AM_C*_R1`, `AM_TOT_R1` | `rdd/P1_resumo.json` `amostra.r1_por_ciclo` | sim; = `D_C*_CAND1` |
| 2 (figura, doc 10) | 55 · 77 · 69 sem ligação; 20 · 30 · 38 sem vínculo | `AM_C*_NLIG`, `AM_C*_SVIN` | idem, `amostra.exclusoes` | sim |
| 2 (figura, doc 10) | 938 · 2.063 · 2.512; 5.513 | `AM_C*_LIG`, `AM_TOT_LIG` | diferença R1 − NLIG | sim |
| 2 (figura, doc 10) | 918 · 2.033 · 2.474; 5.425 | `AM_C*_ORI`, `AM_TOT_ORI` | diferença LIG − SVIN | sim; = `ESC_N` |
| 2 (figura, doc 10) | 3 · 1 · 0 sem região de saúde | `AM_C*_SREG` | ORI − `p1_por_ciclo`; = soma das duas exclusões por região | sim |
| 2 (tela, figura, roteiro) | 915 · 2.032 · 2.474; 5.421 | `D_C*_P1`, `M1_N` | `p1_por_ciclo`; `P1_estimativas.csv` M1 | sim; `VC_resumo.json` M1: 5.421 |
| 2 (tela, figura) | 932.577 pares; 56 conjuntos; 5.125 vagas | `AM_PARES`, `AM_CONJ`, `AM_VAGAS` | `amostra.linhas_m1`, `conjuntos_m1`, `celulas_p1` | sim; = `VC_resumo` M1 (932.577; 56) |
| 3, 6 | 368/368; 454/454; 404/404; 747/748 | `R_*` | `rdd/portao_r1_ivs_oficial.json` | sim; corte "≤ 0,300" (protocolo do escore) = "até 0,300" da fala |
| 4 | 79%, 46%, 36%; 51 km; 189 km; 5.425 | `ESC_*` | descritiva G1 | sim (0,7917; 0,4579; 0,3583; 51,4; 188,5) |
| 6, 8, 11 | p 0,072 (família de um teste) | `VC_B_HOLM` | `rdd/VC_estimativas.csv`, corrigida_13fev, M1, `bolsa_mil`, `p_holm` | sim (0,0724) |
| 7 | D_UF 1,94 [1,48; 2,40]; p < 0,001 | `VC_DUF_*` | idem, `D_UF` | sim (2,3950 − 10 × 0,04529 = 1,9421) |
| 7 | θ_UF 2,40 [2,27; 2,52]; ×11,0 [9,7; 12,5] | `VC_THETA*`, `VC_THETAX*` | idem, `mesma_uf`; exp | sim (exp 2,3950 = 10,97) |
| 7 | 10·β 0,45 [−0,04; 0,95]; ×1,57 [0,96; 2,58] | `VC_B10*`, `VC_B10X*` | idem, `bolsa_mil` × 10; exp | sim (exp 0,4529 = 1,573); limite de cima 0,95 < limite de baixo de θ_UF 2,27 |
| 8, 11 | VL-1 1,47 [1,15; 1,89], Holm 0,005; ciclo 2 1,90 [1,30; 2,78], Holm 0,003 | `VL1_*` | `rdd/VL_estimativas.csv`, VL1_emp / VL1_c2 | sim |
| 8, 9 | M1 1,25 [0,98; 1,61]; ciclo 2 1,79 [1,19; 2,68] | `VLB_*` | idem, M1_emp / M1_c2 | sim (= exp(5β) do VC) |
| 8 | 75 km [28; 122]; 117 [56; 178]; 119 [−12; 250]; 302 [88; 516] | `VL1_*_K5*`, `VLB_*_K5*` | idem, `km_equivalentes` K5 | sim; 75 na tela, 119 só nas notas |
| 9 | ciclos 1,07 [0,69; 1,65], 1,79, 1,00 [0,72; 1,39]; refeito 1,70 [1,22; 2,37] | `VC_M5C*`, `VC_M5C2A_*` | `VC_estimativas.csv`, M5_1/2/3; antiga_19mar | sim |
| 9 | log 1,45 [1,15; 1,83] (c2 1,75 [1,23; 2,49]); região 1,49 [1,15; 1,92] (c2 1,91 [1,33; 2,74]); perto do corte 1,28 [0,95; 1,72], Holm 0,103 | `VLLOG_*`, `VL3_*`, `VL2_EMP_*` | `VL_estimativas.csv` | sim |
| 9 (figura, roteiro) | D_UF por ciclo 2,34 [1,45; 3,24]; 1,19 [0,51; 1,86]; 2,37 [1,75; 3,00] | `VC_DUF_C*` | `VC_estimativas.csv`, M5_k, `D_UF` | sim; os três IC excluem zero |
| 12, 13 | apêndice (HI, PL, CL, P4, OC) | ver auditoria 53, §2 | — | sem mudança desde a 53; o teste relê |
| 9 (doc) | 7:00; 982 palavras | tempos e `palavras()` do gerador | doc 04, blocos `Roteiro` | soma confere; com os números por extenso, cerca de 7:50 (M1). Agora 944 palavras, cerca de 7:10 |

## 4. O que mudou

| Onde | Antes | Depois |
|---|---|---|
| Slide 6 (tela) | Conjunto: "todas as vagas vistas" | "suposto: todas vistas" |
| Slide 7 (tela) | "Na UF de origem, chance 11,0 vezes maior; toda a bolsa: 1,57 (IC contém 1)." | "UF de origem vs. outra UF: chance ×11,0; toda a bolsa: ×1,57 (IC contém 1)." |
| Slide 7 (roteiro e notas) | "ter a vaga na UF de origem multiplica a chance… por 11,0"; "sozinha, ela não se distingue de zero"; 5.421 e o IC falados | "entre duas vagas iguais no resto, inclusive na distância, a da UF de origem tem 11,0 vezes a chance…"; "sozinho, o peso da bolsa não se distingue de zero"; o IC fica na tela; o 5.421 vai para as notas |
| Slide 8 (tela) | "chance 1,47 vez maior" | "chance ×1,47" |
| Slide 9 (tela) | "Mantém: a origem pesa mais que a bolsa…"; "Não se mantém: peso da bolsa: forte…" | "Mantém: origem pesa mais que toda a bolsa…"; "Não se mantém: peso da bolsa, forte…" |
| Slide 10 (título) | "Conclusão: a origem pesa mais que a bolsa? Sim" | "Conclusão: a origem pesa mais que toda a bolsa? Sim" |
| Slide 11 (tela e roteiro) | "Só ciclo 2 → bolsa instável"; "laços de família ficam de fora" | "não generalizar"; a implicação de cada limitação na fala; "para quem trabalha longe de casa, é a do trabalho" |
| Roteiro 2, 3, 4, 5 | funil inteiro falado; 368 de 368…; "nota ou família" | só 5.714 → 5.421; "todos os municípios dos ciclos 1 e 2"; frase do slide 4 mais curta; "idade ou nota" |
| Doc 09 | 982 palavras, sem folga | 944 palavras; aviso dos números falados e cortes seguros; duas perguntas prováveis novas (lista estratégica; o que é o 11,0) |
| Doc 10 | texto da tela antigo; p 0,072 mal localizado; checklist sem os critérios 1 e 4 | tela atual; correções; checklist completo; §5 com o que mudou nesta auditoria |
| Docs 03, 08, README | título antigo do G30; "custo de sair da própria região domina" | título atual; "um degrau de R$ 5 mil não compensa sair da própria UF (leitura)"; README cita esta auditoria |
| Testes | texto antigo da tela | texto novo (comparador na tela e no roteiro; "toda a bolsa"; "suposto"; "não generalizar") |

O deck foi regerado por `gerar_deck_banca2.py --curto --deck <deck do grupo>`. O `.pptx` novo tem SHA-256
`0e93345fd2097d566690370696d514102ad73558efd8b42be911c1aae990ec85` (manifesto do deck curto). O PDF foi renderizado
em `qa_render/` (`curto_slide01` a `13` e `grade_curto.png`). Nenhuma figura mudou.

## 5. Para o grupo e para o autor

1. **Ensaiar com cronômetro.** O roteiro fica perto de 7:10 com os números ditos por extenso. Se passar, use os
   cortes seguros do doc 09; nunca corte as ressalvas.
2. **Quem já copiou a tela do doc 10** deve aplicar a §5 desse doc (seis linhas e um título).
3. **Se a banca pedir a equação**, ela está nas notas do slide 5 e no doc 66 §4.
4. **Se a banca perguntar "11 vezes o quê?"**, a resposta está no doc 09 (perguntas): é a razão de chances entre duas
   vagas iguais no resto, uma na UF de origem e outra fora.
