# 09. Roteiro de fala da banca 2 (cerca de 7 minutos)

> **Data:** 28/10/2026, dia da banca 2 (versão anterior: 27/10/2026, no histórico do Git, commit `33d15d9`).<br>
> **Decisão do autor (28/10/2026):** "a hipótese é simplesmente sobre o efeito bolsa → 1ª opção", com "só comparação
> entre municípios da mesma UF"; "UF, origem etc. é tudo controle/pareamento". A fala não interpreta a origem: nada de
> "a origem pesa mais", ×11,0 ou D_UF (este só como resposta de reserva, pergunta 4). Ajuste do mesmo dia: nada de
> preenchimento; só a escolha da 1ª opção (o deck não tem mais apêndice).<br>
> **Fonte da verdade:** os blocos `> **Roteiro (N s).**` do [doc 04](04_conteudo_deck_curto.md). Este documento repete
> o mesmo texto, slide a slide, para ensaiar sem abrir o deck; o deck leva o roteiro nas notas do apresentador, no
> primeiro parágrafo ("FALA"), antes do detalhe para perguntas. Divergência entre este doc e o doc 04 é erro deste
> doc: `tests/test_deck_curto_banca2.py` confere que são iguais.<br>
> **Regras:** todo número falado é o valor de um código de `output/apresentacao_banca2/numeros_banca2.json`, listado na
> linha `**Números:**` do slide no doc 04; os tempos são metas de fala, não resultados. 
> Redação: o VL-1 compara "vagas da mesma UF (a de origem ou outra)" e é pós-resultado;
> sem fixar a UF (o pré-registrado), o IC contém 1; forte só no ciclo 2; "os dados sugerem"; pacote do corte;
> condicional a se candidatar.

## Tempos

Ritmo-alvo: cerca de 140 palavras por minuto. O roteiro tem 893 palavras escritas; dito em voz alta, cada número
vira várias palavras, e o roteiro fica perto de 7 minutos, sem a troca de slides. O ensaio decide.

| # | Slide | Seção | Tempo | Acumulado |
|---|---|---|---|---|
| 1 | Pergunta e hipótese: a bolsa maior muda a 1ª opção? | Hipótese | 35 s | 0:35 |
| 2 | Dados e amostra: de onde vêm e quem entra no modelo | Dados | 45 s | 1:20 |
| 3 | A bolsa é função exata do IVS: a regra é sharp | Análise descritiva | 25 s | 1:45 |
| 4 | Onde escolhem: a maioria fica na própria UF | Análise descritiva | 30 s | 2:15 |
| 5 | Descritivo: perto do corte, a bolsa maior é mais escolhida | Análise descritiva | 35 s | 2:50 |
| 6 | Modelo: logit condicional da 1ª opção | Metodologia | 35 s | 3:25 |
| 7 | Identificação: as premissas e o nosso caso | Identificação | 45 s | 4:10 |
| 8 | Dentro da mesma UF, a vaga de bolsa maior é preferida | Resultados | 50 s | 5:00 |
| 9 | Robustez: sempre comparando vagas da mesma UF | Robustez | 40 s | 5:40 |
| 10 | Conclusão: a bolsa maior aumenta a 1ª opção? Sim | Discussão | 35 s | 6:15 |
| 11 | Limitações e o que cada uma implica | Discussão | 45 s | 7:00 |

Total: 7:00.

Como usar: ensaiar com cronômetro; se um slide passar do tempo, cortar a última frase dele, nunca as ressalvas
(pós-resultado, sem fixar a UF o IC contém 1, pacote do corte, condicional a se candidatar). Os números ficam na
tela; não é preciso falar todos os intervalos. Se o ensaio passar de 7 minutos, os primeiros cortes seguros são: no
slide 2, a lista das fontes (ela está na figura); no slide 8, "o intervalo vai de 1,15 a 1,89" (está na tela); no
slide 9, "Por que o ciclo 2? Não sabemos" (vai para as perguntas).

## 1. Pergunta e hipótese: a bolsa maior muda a 1ª opção? (35 s)

Nossa pergunta é simples: quando o médico especialista escolhe uma vaga do PMM-E, a bolsa maior muda qual vaga ele põe
em 1ª opção? A hipótese: comparando vagas da mesma UF, a vaga de bolsa maior tem mais chance de ser a 1ª opção. A
motivação: o programa paga bolsa maior onde o IVS do município é maior; queremos saber se isso muda a vaga que o
médico escolhe. Um aviso honesto, que está na tela: formulamos esta hipótese depois de ver os dados.

## 2. Dados e amostra: de onde vêm e quem entra no modelo (45 s)

A 1ª opção de cada candidato vem dos editais do Ministério da Saúde, ciclos 1 a 3; a origem vem do CNES: o município
onde ele tinha vínculo médico antes da inscrição; bolsa e vagas, dos quadros de vagas; o IVS, do Ipea; distância e UF,
do IBGE. A unidade de observação é o par candidato × vaga: cada candidato aparece uma vez para cada vaga aberta do seu
curso e ciclo, e a variável dependente vale 1 na sua 1ª opção. O funil, à direita, mostra quem sai em cada etapa: dos
5.714 candidatos com 1ª opção, 5.421 entram no modelo.

## 3. A bolsa é função exata do IVS: a regra é sharp (25 s)

De onde vem a variação da bolsa? De uma regra. Até IVS 0,300, R$ 10 mil; até 0,400, R$ 15 mil; acima, R$ 20 mil. Cada
ponto é um município, e a regra reproduz a faixa de todos os municípios dos ciclos 1 e 2. O município não escolhe a
bolsa: é a regra que dá.

## 4. Onde escolhem: a maioria fica na própria UF (30 s)

Antes do modelo, os dados crus. Dos 5.425 candidatos com origem, 79% põem a 1ª opção na própria UF, e a distância
mediana é de 51 km. Isso é descritivo, e não é o nosso resultado: é o motivo do desenho. Como a maioria escolhe dentro
da própria UF, comparamos só vagas da mesma UF, e a UF entra como controle.

## 5. Descritivo: perto do corte, a bolsa maior é mais escolhida (35 s)

Agora, a descritiva da hipótese. Pegamos só as 1ªs opções na UF de origem, a até 0,050 de um corte de IVS, onde as
vagas dos dois lados são parecidas. O lado de bolsa maior tem 52,5% das vagas, mas recebe 60,8% das 1ªs opções: é mais
escolhido do que oferecido, e nos três ciclos. Cuidado: é descritivo, sem teste e sem controlar a distância; quem
testa é o modelo.

## 6. Modelo: logit condicional da 1ª opção (35 s)

Usamos um logit condicional. A escolha é discreta: o candidato escolhe uma entre as vagas abertas do seu curso. Cada
candidato é comparado consigo mesmo, e o efeito fixo do par de UFs faz a comparação só entre vagas da mesma UF, vistas
por médicos da mesma UF de origem. A distância, a região e o município entram como controle. A bolsa varia pela regra
do IVS. O teste é β maior que zero, com erro-padrão agrupado por conjunto de escolha.

## 7. Identificação: as premissas e o nosso caso (45 s)

Cinco premissas. Primeiro, a bolsa segue a regra do IVS, sem exceção nos ciclos 1 e 2. Segundo, o que mantemos fixo: o
próprio candidato, o par de UFs e a distância; a região de saúde e o município também entram como controle. Terceiro,
nos mesmos cortes mudam outras regras federais: medimos o pacote do corte. Quarto, e precisamos ser claros: esta
especificação foi escolhida depois de ver o resultado; a pré-registrada, sem fixar a UF, tem intervalo que contém 1.
Quinto, supomos que o candidato viu todas as vagas do seu curso.

## 8. Dentro da mesma UF, a vaga de bolsa maior é preferida (50 s)

Este é o resultado principal. Comparando só vagas da mesma UF, a de origem ou outra, vistas por médicos da mesma UF de
origem, a vaga com bolsa R$ 5 mil maior tem 1,47 vez a chance de ser a 1ª opção, nos ciclos 1 a 3 juntos; o intervalo
vai de 1,15 a 1,89. No ciclo 2, 1,90. Em palavras: entre duas vagas parecidas da mesma UF, a de bolsa maior tem cerca de uma vez e meia
a chance de ser a escolhida; ou, por R$ 5 mil a mais, o médico aceita uma vaga 75 km mais longe.
Duas ressalvas, na tela: é uma especificação escolhida depois do resultado; e a pré-registrada, sem fixar a UF, tem
intervalo que contém 1.

## 9. Robustez: sempre comparando vagas da mesma UF (40 s)

A robustez fica sempre dentro da mesma UF. À esquerda, o peso da bolsa se mantém com a distância em log e com a região
de saúde de origem no lugar da UF de origem. Com poucos grupos, o p do score bootstrap continua 0,011. Só com vagas
perto do corte, o intervalo contém 1: inconclusivo. À
direita, ciclo a ciclo: o efeito é forte só no ciclo 2; nos ciclos 1 e 3, o intervalo contém 1. Por que o ciclo 2? Não
sabemos.

## 10. Conclusão: a bolsa maior aumenta a 1ª opção? Sim (35 s)

Voltando à pergunta: a bolsa maior aumenta a chance de a vaga ser a 1ª opção, comparando vagas da mesma UF? Sim: 1,47
vez a chance nos três ciclos juntos, e forte só no ciclo 2. Pela teoria da banca 1, o médico aceita a vaga se a bolsa
compensa o custo do lugar; os dados sugerem que R$ 5 mil compensam parte desse custo, cerca de 75 km a menos. Isso
vale para a escolha de quem se candidatou.

## 11. Limitações e o que cada uma implica (45 s)

Seis limitações e o que cada uma implica. A especificação é pós-resultado: o resultado é exploratório e pede dados
novos. Sem fixar a UF, como no pré-registrado, o intervalo contém 1. Só vemos quem se candidatou: nada diz sobre quem
não se inscreveu. O contraste é o pacote do corte: vale para o pacote, não para os R$ 5 mil sozinhos. O efeito
é forte só no ciclo 2: não dá para generalizar. E a origem é o vínculo no CNES, não a residência. Obrigado.

## Perguntas prováveis da banca (doc 66, §8)

Respostas curtas. Os números vêm do registro (`VL1_EMP_*`, `VLB_EMP_*`, `VC_B_HOLM`, `VG1_*`, `VG3_*`, `VC_DUF_*`); o
detalhe está nas notas do slide de Limitações.

1. **"Vocês formularam a hipótese depois de ver os resultados?"** Sim, e isso está na tela do slide 1. A
   especificação que compara vagas da mesma UF foi congelada antes de rodar (adendo 52e; auditoria 48), mas depois de
   ver o modelo base. Por isso tratamos o resultado como exploratório.
2. **"Se o pré-registrado tem IC que contém 1, por que acreditar?"** Porque, comparando vagas da mesma UF, a razão de
   chances é 1,47 [1,15; 1,89], p de Holm 0,005, e se mantém com o score bootstrap; sem fixar a UF, 1,25 [0,98;
   1,61], p 0,072. Mas é exploratório, e forte só no ciclo 2: nos ciclos 1 e 3, separados, 1,15 [0,66; 2,01] e
   1,25 [0,90; 1,73].
3. **"Isso é a bolsa ou o pacote?"** O pacote do corte: nos mesmos cortes de IVS mudam outras regras federais
   (auditoria 18). Em 0,300 nenhum outro incentivo individual ao especialista do PMM-E muda (auditoria 35); em 0,400
   fica aberta a ajuda de custo do PMMB; nos dois cortes, o serviço do município pode mudar. Não é a participação no
   PMM-E nem o Agora Tem Especialistas.
4. **"E a origem? Ela não importa mais que a bolsa?"** Não é a pergunta desta hipótese: a UF de origem é controle, e
   por isso comparamos dentro da UF. Só se insistirem: no modelo base, sem fixar a UF, o teste origem × toda a bolsa
   (D_UF) dá 1,94 [1,48; 2,40] em log-chance (doc 57p); não o interpretamos aqui.

Outras, com resposta no doc 66, §8: "origem é onde ele mora?" (não: vínculo médico no CNES antes da inscrição); "por
que só o ciclo 2?" (não sabemos; leituras candidatas sem teste); "e quem não se candidatou?" (correto: tudo é condicional a
se candidatar). Com resposta no doc 66, §5: "a 1ª opção é a preferência verdadeira, se a alocação é por nota?" (é uma
premissa que não se testa com estes dados: supomos que o candidato viu todas as vagas do seu curso e listou sem
estratégia; por isso "suposto" na tabela de Identificação); "o que quer dizer o 1,47?" (é a razão de chances entre
duas vagas parecidas da mesma UF, uma com bolsa R$ 5 mil maior; no logit condicional, é a razão entre as
probabilidades de o candidato escolher uma e a outra).
