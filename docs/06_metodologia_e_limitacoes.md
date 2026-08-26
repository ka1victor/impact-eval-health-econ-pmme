# 06. Auditoria metodológica, proveniência e linguagem de inferência

> Este documento verifica se as regras metodológicas declaradas pelo projeto são atendidas pela implementação atual. A conclusão é de não conformidade em pontos centrais; isso deve orientar a etapa futura de redesenho.

## 1. Proveniência em quatro níveis

| Nível | Definição | Exemplos atuais |
|---|---|---|
| **Observado** | Campo ou contagem calculada diretamente de arquivo identificável | IVS 2010; registros nominais ativos; município; CNES; curso |
| **Derivado** | Transformação transparente de dados observados, sem hipótese comportamental | Contagem de registros por curso; municípios únicos |
| **Parametrizado** | Valor imposto por literatura, regra prática ou hipótese | Produtividade por curso; substituição 65%; R$ 85; QALYs |
| **Não reproduzido** | Resultado incorporado sem dados/estimação local | Betas de teleconsulta; 86,4% de OCI; parte do painel pré-compilado |

Toda tabela futura deve marcar essa proveniência no nível da variável, não apenas no nível do arquivo. Um CSV pode conter colunas observadas e simuladas lado a lado.

## 2. Auditoria de conformidade

| Regra declarada | Implementação atual | Situação |
|---|---|---|
| RDD no corte institucional | Script 01 usa diferença de médias em janelas; script 02 usa local linear sobre painel construído | **Parcial/não validado** |
| Running variable canônica IVS 2010 | IVS é usado | **Atendido** |
| Desfecho observado | Preenchimento, FTE, produção, substituição e custos contêm premissas | **Não atendido** |
| População exposta comparável | Inclui todos os municípios, mesmo sem vaga documentada | **Não atendido** |
| Erro-padrão clusterizado | Script 01 usa variância de duas médias; script 02 usa HC1, sem cluster | **Não atendido** |
| Permutação exata com 2.000 repetições | Há Monte Carlo de 2.000 permutações; não é exata e a atribuição é permutada sem desenho local justificado | **Não atendido como rotulado** |
| Testes de densidade | Razão de contagens é chamada “McCrary proxy” | **Não é teste formal** |
| Placebos | Aplicados inclusive a desfecho definido pela faixa | **Não informativos para o primeiro estágio** |
| FDR de Anderson/BH | Implementa fórmula BH simplificada, sem ajuste monotônico; rotulada como Anderson | **Não atendido como rotulado** |
| Índice KLK | Combina variáveis que incluem componentes parametrizados | **Não interpretável causalmente** |
| Kill criterion | Aplicado a saídas cuja mensuração não passou na auditoria | **Prematuro** |
| Reprodutibilidade numérica | Script 01 fixa `random.seed`, mas não `numpy.random.seed` antes das permutações | **Não atendido** |

## 3. A running variable antiga resolve apenas uma ameaça

O IVS 2010 não foi manipulado por prefeitos em resposta a uma lei de 2025. Isso é uma vantagem real.

Mas uma RDD exige mais:

- regra de tratamento conhecida e aplicada no corte;
- continuidade da probabilidade de receber vaga e de outras políticas;
- comparabilidade das unidades expostas;
- ausência de seleção pós-tratamento;
- forma funcional e banda adequadas;
- desfechos medidos da mesma forma dos dois lados.

Chamar o IVS de “imune a manipulação” não torna a identificação automática. A seleção de municípios e especialidades pode ser a ameaça dominante.

## 4. Sharp, fuzzy ou encorajamento?

O corte parece alterar o valor da bolsa, mas não necessariamente determina:

- se o município recebeu vaga;
- qual especialidade foi ofertada;
- se houve candidato;
- se o profissional entrou;
- se permaneceu.

Por isso, o desenho não deve ser chamado de sharp RDD antes de auditar a regra. Pode ser um desenho fuzzy ou de encorajamento, cujo primeiro estágio é o efeito do corte sobre exposição/entrada observada. Se não houver descontinuidade no primeiro estágio medido corretamente, efeitos a jusante não são identificados por esse instrumento.

## 5. Inferência não resgata mensuração circular

Um $t$ muito alto e um $p$ muito baixo apenas dizem que, sob o cálculo usado, os grupos diferem de forma precisa. Se o valor do desfecho foi atribuído pela própria faixa de tratamento, a precisão recupera a regra de codificação.

O inverso também vale: $p>0,10$ não estabelece igualdade. Para sustentar equivalência ou ausência substantiva de efeito, é preciso:

- margem de equivalência relevante;
- intervalo de confiança suficientemente estreito;
- potência adequada;
- mensuração válida.

Assim, “efeito nulo” deve ser substituído por “estimativa imprecisa/compatível com intervalo X” até que um teste de equivalência seja pré-especificado.

## 6. Permutação e estrutura do desenho

O script 01 permuta valores agregados entre lados e chama o teste de “clustered”, mas não há clusters. O script 02 permuta o indicador de tratamento mantendo a running variable e reestima interações. Para justificar esse procedimento, seria necessário especificar:

- hipótese de randomização local;
- janela escolhida antes do resultado;
- mecanismo de atribuição permutável;
- clusters e dependências espaciais;
- estatística de teste e correção de Monte Carlo;
- compatibilidade com a regra determinística do corte.

Com 2.000 sorteios, o valor zero deve ser evitado com correção $(b+1)/(B+1)$. “Exata” é inadequado quando apenas uma amostra de permutações é usada.

## 7. Placebos e densidade

### Placebos

Placebos em cortes falsos podem detectar padrões suaves ou especificação oportunista. Não validam um desfecho cuja descontinuidade real foi programada no código. Também não substituem:

- resultados pré-tratamento;
- covariáveis balanceadas;
- outros limiares institucionais;
- testes de antecipação;
- desfechos que não deveriam responder.

### Densidade

A razão de municípios acima/abaixo depende da distribuição natural do IVS e da largura da janela. Um teste de densidade formal deve estimar descontinuidade na densidade da running variable com incerteza. Mais importante, deve-se verificar a densidade **das unidades elegíveis/ofertadas**, não só de todos os municípios.

## 8. Múltiplos desfechos e hierarquia causal

Corrigir p-valores não resolve a escolha excessiva de resultados nem a mistura de elos causais. A família deve ser definida por pergunta:

- provimento: candidatura, aceite, entrada e retenção;
- capacidade: FTE e produção;
- acesso: local, externo, global e fila;
- clínica: oportunidade e desfechos;
- economia: custos por perspectiva.

Uma estratégia futura deve escolher desfechos primários em cada família e tratar os demais como mecanismos ou exploratórios. O índice conjunto só deve combinar variáveis com direção, escala e proveniência coerentes.

## 9. Ameaças específicas por eixo

| Eixo | Ameaça dominante atual | Consequência |
|---|---|---|
| Preenchimento | Denominador ausente e taxa construída | Primeiro estágio circular |
| Retenção | Agregação municipal e censura | Não mede permanência individual |
| FTE | Uma unidade presumida por registro | Não mede capacidade líquida |
| Resolutividade | Incrementos e substituição parametrizados | Mecanismo embutido no resultado |
| Fila | Dado ausente | Objetivo legal não avaliado |
| Cirurgias | Local=eletiva e externo=urgência | Composição criada por definição |
| Custos | Parâmetros pontuais e perspectivas misturadas | BCR não empírico |
| OCI/tele | Coeficientes e séries fixados | Não reproduzível |

## 10. Reprodutibilidade da execução

A auditoria do diff e a reexecução mostraram duas fontes de variação que explicam parte das mudanças não commitadas em `output/`:

- no script 01, as permutações usam NumPy sem semente; os coeficientes permanecem iguais, mas os $p$-valores Monte Carlo mudam entre execuções;
- no script 03, `procedimento_exemplo` é escolhido como o primeiro elemento de um `set`; a ordem não é estável, de modo que o texto do exemplo pode mudar sem alteração dos dados.

Além disso, nesta sessão o `run_all.py` concluiu a etapa 1 e reestimou a etapa 2, mas a etapa 2 falhou ao sobrescrever um CSV existente por restrição de escrita do ambiente. Como o script mestre interrompe na primeira falha, as etapas seguintes não foram executadas por ele. Isso é uma falha de execução ponta a ponta nesta máquina, separada das limitações substantivas dos dados.

Uma futura etapa de correção deve fixar todas as sementes, ordenar coleções antes de serializar, registrar versões das dependências e escrever saídas de modo atômico.

## 11. Linguagem autorizada

| Situação | Formulação adequada |
|---|---|
| Contagem direta | “O arquivo registra...” |
| Associação descritiva | “Observa-se diferença...” |
| Estimativa com hipóteses plausíveis | “Sob as hipóteses X, estima-se...” |
| Cenário | “Se A e B, o limiar/BCR seria...” |
| Não significância | “A estimativa é imprecisa e compatível com...” |
| Mecanismo não testado | “Uma hipótese é...” |

Evitar: “comprova”, “descarta”, “efeito rigorosamente nulo”, “se paga”, “gargalo deixou de ser salário” e “destravou”, salvo quando a evidência específica sustentar a frase.

## 12. Conclusão metodológica

O pipeline é útil como protótipo de arquitetura: enumera métricas, fórmulas e possíveis saídas. Ele ainda não é um pacote de replicação causal porque várias colunas-chave são construídas por premissas e as regras de inferência declaradas não coincidem com a implementação.

O passo seguinte será redesenhar e limitar o escopo após decidir quais dados observados podem sustentar quais elos. Até lá, as únicas conclusões firmes são descritivas.
