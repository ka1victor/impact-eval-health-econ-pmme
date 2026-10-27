# 09. Roteiro de fala da banca 2 (cerca de 7 minutos)

> **Data:** 27/10/2026, véspera da banca 2.<br>
> **Pedido:** melhorar o deck da banca 2, só com a H2, pela rubrica da banca e para uma apresentação de cerca de 7
> minutos; no critério "Apresentador" (tom, ritmo, didática, domínio), um roteiro de fala por slide, com tempo-alvo.<br>
> **Fonte da verdade:** os blocos `> **Roteiro (N s).**` do [doc 04](04_conteudo_deck_curto.md). Este documento repete
> o mesmo texto, slide a slide, para ensaiar sem abrir o deck; o deck leva o roteiro nas notas do apresentador, no
> primeiro parágrafo ("FALA"), antes do detalhe para perguntas. Divergência entre este doc e o doc 04 é erro deste
> doc: `tests/test_deck_curto_banca2.py` confere que são iguais.<br>
> **Regras:** todo número falado é o valor de um código de `output/apresentacao_banca2/numeros_banca2.json`, listado na
> linha `**Números:**` do slide no doc 04; os tempos são metas de fala, não resultados. O apêndice não é apresentado.
> Redação das auditorias 50, 52 e 53: "não detectamos aumento"; o teste central é o D_UF; o VL-1 compara "vagas da
> mesma UF (a de origem ou outra)" e é pós-resultado; o pré-registrado tem IC que contém 1; "os dados sugerem";
> pacote do corte; preferência revelada; condicional a se candidatar.<br>
> **Revisão da [auditoria 55](../../auditorias/55_auditoria_deck_rubrica.md) (27/10/2026):** os slides 2, 3, 4, 7 e
> 11 falam menos números (eles ficam na tela), porque um número dito em voz alta vale várias palavras; a leitura do
> coeficiente diz contra o quê se compara ("entre duas vagas iguais no resto, inclusive na distância"); o título da
> Conclusão diz "toda a bolsa", como o teste D_UF.

## Tempos

Ritmo-alvo: cerca de 140 palavras por minuto. O roteiro tem 944 palavras escritas. Dito em voz alta, cada número
vira várias palavras ("um vírgula noventa e quatro"); contando assim, o roteiro fica um pouco acima de 7 minutos a
140 palavras por minuto, sem a troca de slides. Não há folga: o ensaio decide.

| # | Slide | Seção | Tempo | Acumulado |
|---|---|---|---|---|
| 1 | Pergunta e hipótese: origem ou bolsa na escolha? | Hipótese | 35 s | 0:35 |
| 2 | Dados e amostra: de onde vêm e quem entra no modelo | Dados | 50 s | 1:25 |
| 3 | A bolsa é função exata do IVS: a regra é sharp | Análise descritiva | 25 s | 1:50 |
| 4 | Onde escolhem: perto de onde já trabalham | Análise descritiva | 35 s | 2:25 |
| 5 | Modelo: logit condicional da 1ª opção | Metodologia | 45 s | 3:10 |
| 6 | Identificação: as premissas e o nosso caso | Identificação | 30 s | 3:40 |
| 7 | Teste central: a origem pesa mais que toda a bolsa | Resultados | 50 s | 4:30 |
| 8 | Dentro da mesma UF, a vaga de bolsa maior é preferida | Resultados | 40 s | 5:10 |
| 9 | Robustez: o que se mantém e o que não se mantém | Robustez | 40 s | 5:50 |
| 10 | Conclusão: a origem pesa mais que toda a bolsa? Sim | Discussão | 30 s | 6:20 |
| 11 | Limitações e o que cada uma implica | Discussão | 40 s | 7:00 |

Total: 7:00.

Como usar: ensaiar com cronômetro; se um slide passar do tempo, cortar a última frase dele, nunca as ressalvas
(pós-resultado, preferência revelada, pacote do corte, condicional a se candidatar). Os números ficam na tela; não é
preciso falar todos os intervalos. Se o ensaio passar de 7 minutos, os primeiros cortes seguros são: no slide 4, a
frase "Para a pergunta..."; no slide 5, a última frase (unilateral e cluster estão na tela); no slide 9, "Por que o
ciclo 2? Não sabemos" (vai para as perguntas).

## 1. Pergunta e hipótese: origem ou bolsa na escolha? (35 s)

Nossa pergunta é simples: quando o médico especialista escolhe uma vaga do PMM-E, o que pesa mais, a bolsa ou a origem
dele? A hipótese: ele escolhe perto de onde já trabalha; a bolsa maior muda qual vaga ele escolhe, mas pesa menos que
a própria origem. A motivação vem do corte de IVS: onde a bolsa é R$ 5 mil maior, não detectamos aumento do
preenchimento. Um aviso honesto, que está na tela: formulamos esta hipótese depois de ver os dados.

## 2. Dados e amostra: de onde vêm e quem entra no modelo (50 s)

A 1ª opção de cada candidato vem dos editais do Ministério da Saúde, ciclos 1 a 3; a origem vem do CNES: o município
onde ele tinha vínculo médico antes da inscrição; bolsa e vagas, dos quadros de vagas; o IVS, do Ipea; distância e UF,
do IBGE. A unidade de observação é o par candidato × vaga: cada candidato aparece uma vez para cada vaga aberta do seu
curso e ciclo, e a variável dependente vale 1 na sua 1ª opção. O funil, à direita, mostra quem sai em cada etapa: dos
5.714 candidatos com 1ª opção, 5.421 entram no modelo.

## 3. A bolsa é função exata do IVS: a regra é sharp (25 s)

De onde vem a variação da bolsa? De uma regra. Até IVS 0,300, R$ 10 mil; até 0,400, R$ 15 mil; acima, R$ 20 mil. Cada
ponto é um município, e a regra reproduz a faixa de todos os municípios dos ciclos 1 e 2. O município não escolhe a
bolsa: é a regra que dá.

## 4. Onde escolhem: perto de onde já trabalham (35 s)

Antes do modelo, os dados crus. Dos 5.425 candidatos com origem, 79% põem a 1ª opção na própria UF, 46% na mesma
região de saúde e 36% no próprio município; a distância mediana é de 51 km. Isso é descritivo: mostra onde escolhem,
não por quê. Para a pergunta: a origem é uma força grande; falta saber quanto a bolsa pesa diante dela, e é isso que o
modelo mede.

## 5. Modelo: logit condicional da 1ª opção (45 s)

Usamos um logit condicional, por três razões. Primeiro, a escolha é discreta: o candidato escolhe uma entre as vagas
abertas do seu curso. Segundo, cada candidato é comparado consigo mesmo: tudo o que é dele, como idade ou nota, é
igual entre as vagas e sai da conta. Terceiro, a bolsa varia entre vagas por uma regra do IVS, e o IVS entra como
curva contínua; então o peso da bolsa vem só dos saltos nos cortes. O teste central é o D_UF: o peso de a vaga estar
na UF de origem menos o peso de toda a diferença de bolsa. É unilateral, com erro-padrão agrupado por conjunto de
escolha.

## 6. Identificação: as premissas e o nosso caso (30 s)

Cinco premissas. A bolsa segue a regra do IVS, sem exceção nos ciclos 1 e 2. Mas nos mesmos cortes mudam outras regras
federais: medimos o pacote do corte. A independência de alternativas irrelevantes vale só em parte, mas no logit
aninhado o peso da bolsa fica perto do mesmo valor. Com o par de UFs fixado, ele não diminui. E supomos que o
candidato viu todas as vagas do seu curso.

## 7. Teste central: a origem pesa mais que toda a bolsa (50 s)

Este é o teste central. No mesmo modelo, entre duas vagas iguais no resto, inclusive na distância, a da UF de origem
tem 11,0 vezes a chance de ser a 1ª opção. Toda a diferença de bolsa, de R$ 10 mil para R$ 20 mil, multiplica a chance
por 1,57, e esse intervalo contém 1: sozinho, o peso da bolsa não se distingue de zero. A diferença entre os dois
pesos, em log-chance, é 1,94, com p unilateral menor que 0,001. Em palavras: a origem pesa muito mais que toda a
bolsa. Um cuidado: a origem é preferência revelada, não causa.

## 8. Dentro da mesma UF, a vaga de bolsa maior é preferida (40 s)

Então a bolsa não pesa? Pesa, quando comparamos vagas parecidas. Fixando o par de UFs, comparamos só vagas da mesma
UF, a de origem ou outra, vistas por médicos da mesma UF de origem. Aí, R$ 5 mil a mais multiplicam a chance por 1,47
nos ciclos 1 a 3 juntos e por 1,90 no ciclo 2. Na escolha, isso vale o mesmo que 75 km a menos de distância. Duas
ressalvas: é um adendo feito depois do resultado; e, na especificação pré-registrada, sem fixar a UF, o p é 0,072.

## 9. Robustez: o que se mantém e o que não se mantém (40 s)

Se mantém, à direita: a origem pesa mais que toda a bolsa em cada ciclo separado; a diferença fica acima de zero nos
três, de 1,19 no ciclo 2 a 2,37 no ciclo 3. E, entre vagas da mesma UF, a bolsa continua pesando com a distância em
log e com a região de saúde fixada. Não se mantém o peso da bolsa sozinho: no pré-registrado o intervalo contém 1; ele
é forte só no ciclo 2, e perto do corte é inconclusivo. Por que o ciclo 2? Não sabemos.

## 10. Conclusão: a origem pesa mais que toda a bolsa? Sim (30 s)

Voltando à pergunta: na escolha da vaga, a origem pesa mais que toda a bolsa? Sim, e em todos os ciclos. Segundo,
entre vagas da mesma UF, a bolsa maior é preferida: ela muda qual vaga o médico escolhe. Terceiro, pela teoria da
banca 1, o médico aceita a vaga se a bolsa compensa o custo do lugar; os dados sugerem que um degrau de R$ 5 mil não
compensa sair da própria UF: incentivo limitado.

## 11. Limitações e o que cada uma implica (40 s)

Seis limitações e o que cada uma implica. A hipótese é pós-resultado: o resultado é exploratório e pede dados novos. A
origem é preferência revelada: não é causa da escolha. Só vemos quem se candidatou: nada diz quantos médicos a bolsa
atrairia. O contraste é o pacote do corte: vale para o pacote, não para os R$ 5 mil sozinhos. A bolsa pesa forte só no
ciclo 2: não dá para generalizar. E a origem é o vínculo no CNES, não a residência: para quem trabalha longe de casa,
é a do trabalho. Obrigado.

## Perguntas prováveis da banca (doc 66, §8)

Respostas curtas. Os números vêm do registro (`VL1_EMP_*`, `VC_B_HOLM`); o detalhe está nas notas do slide de
Limitações.

1. **"Vocês formularam a hipótese depois de ver os resultados?"** Sim, e isso está na tela do slide 1. O teste D_UF
   formaliza uma diferença já visível nos intervalos (protocolo 52b; auditoria 31), e o adendo que compara vagas da
   mesma UF foi congelado antes de rodar (52e; auditoria 48). Por isso tratamos o resultado como exploratório.
2. **"Se o peso da bolsa não passa no Holm no pré-registrado, como ela muda qual vaga?"** Pelo adendo que compara
   vagas da mesma UF (a de origem ou outra), que passa no Holm do adendo: 1,47 [1,15; 1,89], p de Holm 0,005; e
   pelo ciclo 2. No pré-registrado, sem fixar a UF, o p é 0,072. O teste central da hipótese continua sendo o D_UF.
3. **"Isso é a bolsa ou o pacote?"** O pacote do corte: nos mesmos cortes de IVS mudam outras regras federais
   (auditoria 18). Em 0,300 nenhum outro incentivo individual ao especialista do PMM-E muda (auditoria 35); em 0,400
   fica aberta a ajuda de custo do PMMB; nos dois cortes, o serviço do município pode mudar. Não é a participação no
   PMM-E nem o Agora Tem Especialistas.

Outras, com resposta no doc 66, §8: "a origem é causal?" (não: preferência revelada); "origem é onde ele mora?"
(não: vínculo médico no CNES antes da inscrição); "por que só o ciclo 2?" (não sabemos; leituras candidatas sem
teste); "escolha não é preenchimento" (correto: condicional a se candidatar). Com resposta no doc 66, §5: "a 1ª opção
é a preferência verdadeira, se a alocação é por nota?" (é uma premissa que não se testa com estes dados: supomos que
o candidato viu todas as vagas do seu curso e listou sem estratégia; por isso "suposto" na tabela de Identificação);
"o que quer dizer o 11,0?" (é a razão de chances entre duas vagas iguais no resto, inclusive na distância, uma na UF
de origem e outra fora dela; no logit condicional, é a razão entre as probabilidades de o candidato escolher uma e a
outra. Não é a probabilidade de uma vaga qualquer multiplicada por 11,0; é a comparação entre as duas).
