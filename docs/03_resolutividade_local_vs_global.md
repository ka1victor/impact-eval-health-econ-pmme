# 03. Acesso local, acesso global e fila: decomposição sem atalhos lógicos

> Este dossiê aprofunda a pergunta levantada pela auditoria: se o programa apenas muda o local do atendimento, o impacto é nulo? A resposta é não, mas o valor e o sinal do impacto dependem de dimensões que a decomposição contábil não observa sozinha.

## 1. Três resultados diferentes

Para os residentes do município $m$:

$$Q_{global,m}=Q_{local,m}+Q_{externo,m}$$

Daí derivam três famílias de resultados:

1. **Localização:** qual parcela do cuidado ocorre perto da residência?
2. **Quantidade:** quanto cuidado total os residentes recebem?
3. **Tempo:** quanto esperam entre demanda, encaminhamento e atendimento?

O PMM-E pode afetar qualquer combinação dessas margens. “Resolutividade” não deve condensá-las em uma única palavra.

## 2. Por que substituição espacial pode ser impacto real

Se $Q_{local}$ sobe e $Q_{externo}$ cai na mesma magnitude, $Q_{global}$ permanece constante. Ainda assim, podem ocorrer:

- menor distância e tempo de viagem;
- menor custo monetário para paciente e gestor;
- menos perda de trabalho e necessidade de acompanhante;
- maior continuidade com a rede local;
- menor sobrecarga no polo de destino.

Esses são benefícios potenciais. Para chamá-los de impacto, é preciso observar distância, tempo, custo, continuidade ou capacidade liberada — não apenas inferi-los da mudança de prestador.

## 3. Por que substituição também pode esconder problemas

O mesmo padrão local-externo pode refletir:

- migração de código ou faturamento, sem mudança no percurso real do paciente;
- cuidado local de qualidade ou escopo diferente;
- restrição do encaminhamento externo sem capacidade local equivalente;
- transferência de pacientes de municípios vizinhos para outra rota;
- tendência temporal coincidente;
- painel construído com a própria hipótese de substituição.

Logo, “só remanejou” não é sinônimo nem de sucesso nem de fracasso.

## 4. A fila é um estimando próprio

O objetivo legal do PMM-E é reduzir o tempo de espera. Volume e fila não são equivalentes.

- Produção constante pode coexistir com fila menor se a demanda registrada cair, a produtividade aumentar ou a composição mudar.
- Produção maior pode coexistir com fila maior se a demanda crescer ainda mais.
- Fila administrativa menor pode refletir cancelamento, recadastramento ou mudança de prioridade.
- O tempo médio pode melhorar enquanto a cauda piora; por isso mediana e percentis também importam.

A métrica mínima deveria ligar solicitação, especialidade/procedimento, prioridade clínica e atendimento. Sem isso, o projeto não responde ainda à principal meta oficial.

## 5. Auditoria do painel atual

O pipeline procura arquivos origem-destino em diretórios que não existem no repositório. Quando não os encontra, carrega `data/geo8_pmm_resolutividade_painel_municipios.csv`, já pré-compilado.

Na rotina que gera esse tipo de painel:

- consultas, exames e cirurgias adicionais são atribuídos por curso a partir de tabelas de produtividade;
- 65% da produção adicional é subtraída do fluxo externo;
- 35% é tratado como expansão;
- viagens e horas poupadas decorrem dessas mesmas quantidades;
- QALYs são calculados por fator fixo.

Assim, o painel não separa o que veio do SIA/SIH do que foi acrescentado como premissa. A substituição espacial não pode ser tratada como achado independente.

## 6. Como ler as saídas numéricas existentes

O protótipo reporta aumento de resolutividade local e efeito global não significativo. A leitura correta é limitada:

- o resultado local é influenciado pela produção e substituição adicionadas no painel;
- no corte 0,300 e janela 0,015, o coeficiente local é +0,0758, mas o erro-padrão robusto é 0,0613 e o $p$ paramétrico é 0,2158; o $p$ de permutação reportado é 0,012;
- a divergência entre inferências pede validação da permutação e da hipótese nula;
- o índice conjunto KLK é não significativo no próprio output;
- o critério de parada para expansão global está reprovado no JSON.

Mesmo se esses resultados viessem de dados integralmente observados, “não significativo” não provaria efeito zero ou ausência de demanda induzida. Seriam necessários intervalos de confiança e testes de equivalência com margem substantiva pré-definida.

## 7. Demanda reprimida e demanda induzida não são opostos observáveis por volume

Um aumento global pode conter simultaneamente:

- necessidade legítima antes não atendida;
- diagnóstico mais oportuno;
- repetição ou procedimentos de baixo valor;
- mudança de registro;
- atendimento de pacientes atraídos de outras localidades.

Para distinguir essas histórias, o volume deve ser combinado com indicação clínica, duplicidade, continuidade, estágio, tratamento subsequente e resultados. Um efeito global nulo tampouco elimina demanda induzida: aumentos inadequados em um grupo podem ser compensados por quedas em outro.

## 8. Cirurgia: geografia não é caráter da internação

O script atual classifica toda produção cirúrgica local como eletiva e toda produção externa como urgência, sem usar efetivamente `CAR_INT`. Isso cria por construção a narrativa “local=eletiva, externo=urgência”.

A análise válida deve cruzar separadamente:

- município de residência;
- município e CNES de internação;
- caráter eletivo/urgência;
- procedimento e complexidade;
- transferência;
- capacidade instalada e data de entrada do especialista.

A presença de 384 registros em Anestesiologia é um fato descritivo interessante, mas não demonstra reativação de salas, aumento de cirurgias ou prevenção de urgências.

## 9. Matriz de interpretação para resultados futuros

| Local | Global | Fila | Interpretação provisória |
|---|---|---|---|
| Sobe | Estável | Cai | Acesso mais próximo e mais rápido, sem expansão de volume; avaliar qualidade e custo |
| Sobe | Estável | Estável | Ganho espacial possível, sem evidência de objetivo de fila |
| Sobe | Sobe | Cai | Expansão e oportunidade; distinguir necessidade atendida de uso de baixo valor |
| Sobe | Cai | Sobe | Sinal de risco: localização melhora, mas acesso total e espera pioram |
| Estável | Sobe | Cai | Expansão sem localização; benefício pode ocorrer em polos regionais |

Nenhuma célula, isoladamente, autoriza um veredito global sobre o programa.

## 10. Veredito atual do eixo

O repositório ainda não estima com dados observados o efeito do PMM-E sobre localização, quantidade ou fila. A formulação defensável é:

> Uma substituição espacial, se confirmada, pode gerar valor mesmo sem expansão do volume. Porém, o painel atual programa parte dessa substituição e não observa o tempo de espera; portanto, não sabemos se houve efeito real na fila nem se o remanejamento beneficiou os pacientes.
