# 05. Plano principal mínimo

> Decisão vigente. Este documento substitui, para a execução atual, o plano de
> cobertura individual de vagas. O desenho anterior continua preservado como
> agenda futura, mas não será executado agora.

## 1. Pergunta que será respondida

> Ser classificada inicialmente como **vaga imediata**, em vez de **apenas
> cadastro de reserva**, aumentou o número mensal de especialistas elegíveis
> cadastrados no estabelecimento contemplado pelo PMM-E?

Esse é um estudo do efeito da **priorização imediata** sobre a oferta médica
cadastral local. Não é um estudo do efeito global do PMM-E, do preenchimento de
cada vaga ou da permanência individual dos bolsistas.

## 2. Por que este é o plano principal

Ele usa o melhor contraste atualmente disponível em dados públicos:

- tratamento e comparação estão no mesmo quadro administrativo;
- a unidade `CNES–curso` está explicitamente identificada na oferta;
- o CNES mensal permite medir o estoque de médicos sem identificar nominalmente
  os participantes do PMM-E;
- o ciclo 1 já possui uma janela pré e pós razoavelmente simétrica;
- a pergunta é estreita e pode ser respondida antes de incorporar produção,
  filas, internações ou desfechos clínicos.

O desenho é da mesma família da estratégia anteriormente discutida — painel
mensal com DiD/DDD —, mas troca o estimando individual bloqueado por um estimando
agregado mensurável com dados públicos.

## 3. O que o contraste significa

O tratamento será fixado pela publicação de 24/07/2025:

```text
Immediate_is = 1  se a célula CNES i – curso s tinha vaga imediata
Immediate_is = 0  se a célula tinha apenas cadastro de reserva
```

Na planilha do ciclo 1, chamada 1, há:

- 503 células apenas com vagas imediatas;
- 782 células apenas em cadastro de reserva;
- 10 células com as duas modalidades, que serão excluídas da especificação
  principal;
- 460 estabelecimentos, dos quais 165 têm cursos em modalidades distintas e
  ajudam a identificar comparações dentro do próprio CNES.

Os totais acima se referem a **células CNES–curso**, não ao número de vagas. O
tratamento é binário e mede o pacote associado à classificação inicial da célula;
não estima o efeito por vaga adicional.

Cadastro de reserva não é ausência de programa nem um grupo nunca exposto. Vagas
em reserva podem ser reapresentadas, convertidas ou posteriormente alocadas. Por
isso, o estimando será descrito como:

> efeito da classificação inicial como imediata, comparada à classificação
> inicial apenas em reserva.

Na análise principal, a classificação de julho permanecerá fixa. Reclassificar
ou censurar controles depois de conversões poderia condicionar a amostra a
eventos posteriores ao tratamento. A ativação posterior de reservas será
registrada como contaminação do contraste e tende a aproximar os grupos.

## 4. Dados e janela

### Oferta

Fonte principal:
`data/raw/aquisicao/vagas/2025_ciclo1_chamada1_vagas.xlsx`.

Somente o ciclo 1, chamada 1, entrará na primeira versão. Não serão somadas
reapresentações nem outras chamadas.

### Outcome

Será adquirido o painel público mensal completo do CNES entre **junho de 2024 e
julho de 2026**. Os identificadores de CNES, profissional e CBO serão preservados
como texto.

A unidade será `CNES–curso–mês`. Cada curso deverá ter um conjunto de CBOs
elegíveis definido por regra oficial congelada antes da construção do outcome.

Outcome único da primeira versão:

```text
especialistas_ist = número de CO_PROFISSIONAL_SUS distintos
                    no CNES i, no mês t, pertencentes ao conjunto
                    de CBOs elegíveis para o curso s
```

O outcome mede estoque cadastral de especialistas. Um aumento é compatível com
atração ou expansão da oferta no estabelecimento, mas não prova que os médicos
adicionais sejam bolsistas do PMM-E.

### Calendário

- pré-tratamento: 2024-06 a 2025-06;
- 2025-07: mês de transição, excluído;
- pós-tratamento: 2025-08 a 2026-07.

Como a oferta foi publicada em 24/07/2025, agosto de 2025 será o primeiro mês
pós. A escolha é determinada pelo calendário, não pelos resultados.

## 5. Único portão técnico antes do painel

É obrigatório construir e auditar a correspondência `curso PMM-E → CBO(s)` a
partir dos requisitos oficiais de elegibilidade. Essa ponte ainda não está
pronta no repositório.

Antes de baixar e transformar todo o painel, o portão deve informar:

1. quais CBOs representam cada curso;
2. se a correspondência é unívoca ou envolve múltiplas especialidades;
3. quais células de um mesmo CNES têm conjuntos de CBOs sobrepostos;
4. quantas observações permanecem numa amostra não ambígua.

A especificação principal usará apenas cursos com mapeamento defensável. Células
com conjuntos sobrepostos e modalidades conflitantes no mesmo CNES serão
excluídas ou colapsadas por regra escrita antes de observar os outcomes. Se não
houver amostra comparável suficiente após esse portão, o projeto não usará a
DDD para fazer afirmação causal.

## 6. Estimação principal

Como o ciclo 1 possui uma única data inicial de exposição, não é necessário usar
Callaway–Sant'Anna ou Sun–Abraham na primeira versão. A especificação principal
será a DDD estática:

```text
Y_ist = alpha_is
      + gamma_it
      + delta_st
      + beta (Immediate_is × Post_t)
      + epsilon_ist
```

em que:

- `alpha_is` são efeitos fixos da célula CNES–curso;
- `gamma_it` são efeitos fixos CNES–mês, que absorvem choques gerais do
  estabelecimento;
- `delta_st` são efeitos fixos curso–mês, que absorvem choques comuns ao curso;
- `beta` é a diferença pós-oferta entre células inicialmente imediatas e células
  inicialmente em reserva, líquida desses três conjuntos de efeitos fixos.

O modelo principal será linear em número de médicos, para que `beta` seja lido
diretamente em especialistas. A inferência será agrupada por município. Serão
reportados o número de municípios, a distribuição de células por cluster e a
sensibilidade a clusters dominantes.

## 7. Diagnóstico mínimo

Além da estimativa estática, será produzido um estudo de evento com a mesma
estrutura de efeitos fixos. Ele servirá para mostrar tendências anteriores,
antecipação e dinâmica; não será usado para escolher retrospectivamente a janela
mais favorável.

A primeira entrega conterá somente:

1. tabela de construção e perdas da amostra;
2. tabela descritiva de baseline por modalidade;
3. gráfico de médias mensais por grupo;
4. gráfico de evento com leads e lags;
5. coeficiente principal da DDD, intervalo de confiança e interpretação em
   número de especialistas.

A priorização imediata não foi aleatória. O fato de os grupos pertencerem ao
mesmo processo administrativo melhora comparabilidade, mas não garante
identificação. A interpretação causal exige tendências paralelas condicionais
aos efeitos fixos e ausência de choque específico simultâneo à célula tratada.
Se houver pré-tendências substantivas, falta de suporte ou concentração do
resultado em poucos locais, a entrega será nomeada **comparação ajustada**, não
impacto causal.

## 8. O que não será feito agora

Ficam congelados, sem tarefas de execução na primeira versão:

- ciclos 2 e 3 e qualquer painel de adoção escalonada;
- Callaway–Sant'Anna, Sun–Abraham, synthetic DiD e matrix completion;
- RDD pelo IVS, efeito de incentivo financeiro e variáveis instrumentais;
- identificação individual de bolsistas, cobertura de vagas e retenção
  individual;
- FTE, entradas, saídas, churn e permanência em seis ou doze meses;
- remanejamento entre CNES, municípios ou regiões de saúde;
- produção SIA/SUS, internações SIH/SUS, filas, exames e outcomes de saúde;
- custos, custo-benefício, heterogeneidades e correção por múltiplos outcomes;
- envio dos pedidos administrativos A07.

Esses itens só serão reabertos por nova decisão explícita após a entrega da
versão mínima.

## 9. Sequência operacional fechada

```text
1. Congelar a ponte curso–CBO e a amostra elegível
2. Adquirir as 26 competências CNES
3. Construir um único outcome mensal de estoque
4. Produzir descritivas, DDD estática e estudo de evento
5. Auditar pré-tendências, suporte, clusters e perdas
6. Entregar nota curta com linguagem proporcional à identificação
```

Não há outra frente em paralelo. O plano individual anterior permanece bloqueado
por dados administrativos; este plano agregado não depende de identificar quais
médicos pertencem ao PMM-E.
