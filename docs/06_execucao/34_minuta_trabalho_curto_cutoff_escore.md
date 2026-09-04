# Minuta do trabalho curto causal — alocação marginal e presença de especialistas

> **Versão de trabalho em 04/09/2026.** Texto-base para redação. Os números são
> reproduzidos pelo A8; a revisão de literatura e a formatação bibliográfica
> final ainda devem ser incorporadas na versão submetida.

## Título provisório

**Ganhar a vaga preferida atrai o especialista? Evidência local no cutoff de
seleção do Programa Mais Médicos Especialistas**

## Resumo

Este trabalho estima se obter marginalmente uma vaga de primeira opção aumenta
a adesão e a presença posterior de especialistas no estabelecimento escolhido
no Programa Mais Médicos Especialistas. Usamos publicações oficiais de
classificação, homologação e participantes ativos. A amostra principal compara,
dentro do mesmo curso, estabelecimento, chamada e modalidade de ampla
concorrência, o último selecionado e o primeiro não selecionado quando suas
pontuações diferem em exatamente um ponto. Empates são excluídos porque dependem
de critérios não observados de UF e idade. Em 36 pares de 2025, ganhar a vaga
aumenta a homologação na chamada e local em 63,9 pontos percentuais e a presença
ativa no mesmo curso–CNES em 12/08/2026 em 33,3 pontos percentuais. O placebo
imediatamente abaixo do cutoff é nulo; janelas alternativas e exclusões de
curso e UF preservam o sinal. Em 11 pares do ciclo 2 de 2026, a presença ativa
aumenta 36,4 pontos percentuais, mas a inferência exata é imprecisa. Como a
pontuação é discreta e o protocolo é retrospectivo, interpretamos os resultados
como efeito local condicional à comparabilidade entre candidatos separados por
um ponto. O desenho informa conversão da alocação em ingresso e presença, não o
efeito da bolsa, do IVS ou do programa sobre o estoque municipal total.

## 1. Introdução

A distribuição de especialistas não depende apenas da existência de vagas. Ela
depende de o médico aceitar uma oportunidade específica e permanecer vinculado
ao local em que foi alocado. Essa margem é particularmente importante quando
as vagas são territorialmente heterogêneas e quando candidatos ordenam mais de
uma preferência.

O PMM-E permite observar uma decisão administrativa simples: dentro de cada
curso e estabelecimento, alguns candidatos ganham a vaga de primeira opção e
outros ficam imediatamente abaixo do limite de seleção. O trabalho explora
essa fronteira para perguntar se o acesso marginal à vaga preferida se converte
em adesão e presença posterior.

A contribuição é deliberadamente estreita. Não estimamos produção assistencial,
internações, exames ou estoque geral de médicos. Também não identificamos o
efeito da remuneração adicional associada ao IVS, pois o IVS público não
reproduz a faixa administrativa nem gera primeiro estágio estável. Em vez
disso, examinamos o mecanismo de matching entre candidato e vaga no ponto em
que a regra muda a alocação.

## 2. Contexto institucional e hipótese

Os candidatos informam preferências e são ordenados por pontuação. A última
posição contemplada em uma célula curso–CNES recebe a alocação, enquanto a
posição seguinte não a recebe naquele momento. Em empates, o edital usa
critérios de mesma UF e maior idade. Como esses critérios não estão integralmente
disponíveis nas listas públicas, pares empatados não entram na análise causal.

A hipótese central é que candidatos da mesma célula, chamada, primeira
preferência e ampla concorrência, separados por um único ponto, teriam
resultados potenciais comparáveis na ausência da alocação. Sob essa hipótese, a
mudança de tratamento no cutoff identifica um efeito local de ganhar a primeira
opção.

Essa hipótese é mais forte do que a continuidade usada em uma RDD com running
variable efetivamente contínua. A pontuação é discreta, e um ponto pode refletir
experiência ou qualificação relacionada ao outcome. Por isso, o artigo usa a
expressão “efeito local condicional” e não apresenta a regra como sorteio
literal.

## 3. Dados e método

### 3.1 Amostra

A amostra principal combina a primeira e a segunda chamadas do ciclo 1 de 2025.
Para cada célula curso–CNES, selecionamos o último candidato alocado e o primeiro
não alocado quando:

1. ambos escolheram a vaga como primeira opção;
2. ambos concorrem em ampla concorrência;
3. há uma única pessoa em cada posição adjacente;
4. a pontuação do selecionado supera a do não selecionado em exatamente um
   ponto;
5. o tratamento muda de selecionado para não selecionado entre as duas
   posições.

O recorte produz 30 pares na primeira chamada e seis na segunda, totalizando
36 pares. Não há nomes repetidos nem células repetidas na amostra combinada.

### 3.2 Tratamento e outcomes

O tratamento é ganhar a vaga de primeira opção. Homologação no mesmo
curso–CNES é um outcome de processo: mede aceitação administrativa imediata,
mas está próximo da elegibilidade criada pela seleção. O outcome substantivo
principal é estar ativo no mesmo curso–CNES em 12/08/2026, definido para todos
os candidatos, sem condicionar à homologação.

Outcomes em qualquer local do programa verificam se o efeito se limita ao
endereço escolhido ou também altera o ingresso no programa. A ausência no
snapshot significa somente não estar ativo naquela data; não revela data de
saída nem permanência contínua.

### 3.3 Estimação e inferência

Para cada par, calculamos a diferença binária entre o candidato acima e o
candidato abaixo do cutoff. A estimativa é a média dessas diferenças. Reportamos
o teste exato bicaudal entre pares discordantes e, como descrição de incerteza,
um intervalo t pareado identificado como convencional.

O teste exato não torna a atribuição aleatória por si só. Sua validade causal
continua condicionada à comparabilidade local. A limitação é especialmente
importante porque há apenas um valor discreto de pontuação de cada lado.

Os diagnósticos incluem pares imediatamente abaixo e acima do cutoff, gaps de
até dois pontos e de qualquer tamanho positivo, outcomes em qualquer local,
exclusão sucessiva de cada curso e UF e replicação no ciclo 2 de 2026.

## 4. Resultados

### 4.1 Resultado principal de 2025

| Outcome | Selecionado | Não selecionado | Diferença | IC95% convencional | Teste exato |
|---|---:|---:|---:|---:|---:|
| Homologado no mesmo curso–CNES | 63,9% | 0,0% | +63,9 p.p. | [47,4; 80,4] | `p<0,000001` |
| Ativo no mesmo curso–CNES | 41,7% | 8,3% | +33,3 p.p. | [13,5; 53,1] | `p=0,0042` |

A homologação mostra forte conversão administrativa, embora seu zero entre os
não selecionados seja em parte esperado pela estrutura da chamada. O resultado
mais relevante é a presença posterior: candidatos marginalmente selecionados
têm probabilidade 33,3 p.p. maior de aparecer ativos naquele curso–CNES.

Em qualquer local do programa, as diferenças são +58,3 p.p. para homologação e
+33,3 p.p. para atividade. Assim, a presença posterior no local escolhido não
parece ser apenas uma troca mecânica de endereço entre participantes que
entrariam de qualquer forma.

### 4.2 Placebos e robustez

No placebo imediatamente abaixo, que compara dois candidatos não selecionados
separados por um ponto, a diferença é −3,3 p.p. em homologação e zero em
atividade. O salto não se repete onde o tratamento não muda.

Com gap de até dois pontos, os efeitos são +58,1 p.p. em homologação e +35,1
p.p. em atividade. Com qualquer gap positivo, são +58,0 e +36,0 p.p. Ao excluir
cada curso ou UF, o efeito sobre atividade permanece entre +27,3 e +38,7 p.p.
Esses exercícios mostram estabilidade de sinal e magnitude, mas não eliminam a
hipótese identificadora não testável.

### 4.3 Replicação de 2026

Na segunda chamada do ciclo 2 de 2026, 11 pares atendem ao mesmo critério. A
diferença de atividade no mesmo curso–CNES é +36,4 p.p., próxima da estimativa
de 2025. O intervalo convencional é [2,5; 70,3] p.p., enquanto o teste exato é
`p=0,125`. A replicação favorece consistência externa de direção, mas não tem
pares discordantes suficientes para precisão isolada.

## 5. Discussão

Os resultados indicam que o matching administrativo importa: para candidatos
no limite da mesma vaga preferida, ganhar a alocação aumenta a chance de o
especialista efetivamente aparecer naquele local em data posterior. Essa margem
é diretamente relevante para desenho de vagas e ordenação de preferências.

O resultado não mostra que elevar a bolsa atrai médicos para municípios mais
vulneráveis. Também não mede novos candidatos, pois a amostra começa depois da
inscrição. “Atração” deve ser entendida como atração realizada — conversão de
uma preferência declarada em ingresso e presença — e “retenção” apenas como
presença em uma data, não como duração até saída.

Quatro limitações organizam a leitura. Primeiro, a pontuação é discreta e pode
capturar atributos relevantes. Segundo, a amostra contém apenas 36 pares.
Terceiro, o linkage público entre publicações usa nome normalizado exato e
curso–CNES, embora a unicidade seja auditada. Quarto, o recorte foi refinado
depois que a análise A7 já havia mostrado os outcomes; o protocolo é
retrospectivo, não pré-registrado.

## 6. Conclusão

Sob comparabilidade local, ganhar marginalmente a primeira opção aumentou a
presença posterior do especialista no estabelecimento escolhido em cerca de um
terço da amostra. O efeito aparece em duas chamadas de 2025, não se reproduz no
placebo abaixo do cutoff, permanece em especificações alternativas e tem direção
semelhante numa pequena replicação de 2026.

Para um trabalho curto, a conclusão deve permanecer nesse nível. O estudo
oferece evidência causal local sobre alocação e presença, com rigor moderado. A
análise territorial descritiva explica a relevância do problema, mas não deve
ser fundida ao estimando causal. A RDD da bolsa pelo IVS e os outcomes de
produção permanecem fora da conclusão.

## Materiais de replicação

O plano completo está em
[`17_plano_causal_publico_cutoff_escore.md`](../05_identificacao/17_plano_causal_publico_cutoff_escore.md).
As estimativas estão em
[`A8_tabela_02_estimativas_escore_estrito.csv`](../../output/tema_trabalho/A8_tabela_02_estimativas_escore_estrito.csv),
os placebos em
[`A8_tabela_03_placebos_escore_estrito.csv`](../../output/tema_trabalho/A8_tabela_03_placebos_escore_estrito.csv)
e o protocolo em
[`A8_protocolo_cutoff_escore.json`](../../output/tema_trabalho/A8_protocolo_cutoff_escore.json).
