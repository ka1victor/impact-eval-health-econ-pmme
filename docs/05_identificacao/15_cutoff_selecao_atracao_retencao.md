# Corte de seleção para atração e presença posterior

> **Estado em 04/09/2026:** desenho promissor, ainda não causal com dados públicos.  
> **Estimando candidato:** efeito local de ganhar a vaga de primeira opção sobre entrada e presença ativa posterior no PMM-E.

## 1. Por que este desenho é mais adequado ao trabalho curto

O desenho atua exatamente na decisão individual de atração. Ele não usa produção, internações, exames ou estoque agregado como substituto da adesão do especialista. A unidade é o candidato dentro de uma vaga curso–CNES, e o contraste intuitivo é entre o último selecionado e o primeiro não selecionado em sua primeira opção.

Ele é distinto do RDD territorial da bolsa. O IVS 2010 do IPEA continua sendo a running variable canônica para estudar o adicional de R$ 5 mil. Aqui, a regra de seleção dos candidatos cria outro limiar administrativo, em outro grão e para outro estimando.

## 2. Evidência pública já reproduzida

Quatro publicações produzem 423 pares adjacentes no ranking; 184 pares têm o mesmo escore publicado. Em 2025, 193 pares podem ser ligados a homologação e ao cadastro de participantes ativos em 12/08/2026.

| Chamada | Pares | Diferença em homologação | Diferença em presença ativa |
|---|---:|---:|---:|
| 2025 ciclo 1, chamada 1 | 136 | +46,3 p.p. | +27,2 p.p. |
| 2025 ciclo 1, chamada 2 | 57 | +77,2 p.p. | +56,1 p.p. |

As diferenças vêm de comparações pareadas no mesmo curso–CNES. São grandes e aparecem nas duas chamadas, mas são **descontinuidades preliminares**, não efeitos causais identificados.

## 3. O bloqueio causal exato

O item 5.2.5 do Edital nº 3/2025 resolve empates primeiro pela escolha de vaga na mesma UF do domicílio ou nascimento e depois pela maior idade. Esses dois critérios podem afetar diretamente a disposição de ingressar e permanecer. Como não aparecem nas planilhas públicas, restringir ao mesmo barema não torna o selecionado e o não selecionado intercambiáveis.

Também faltam identificadores pseudonimizados estáveis. A auditoria pública liga publicações apenas por nome normalizado exato e único; as máscaras de CPF são incompatíveis. Essa solução é adequada para prototipagem agregada, não para a versão final do artigo.

Fonte normativa: https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2025/chamamento-publico-sgtes-ms-no-3-2025-projeto-mais-medicos-especialistas/edital-de-chamamento-publico-no-3-2025.pdf

## 4. Desenho causal proposto

### População

- ampla concorrência;
- primeira opção;
- células curso–CNES com pelo menos um selecionado e um não selecionado;
- exclusão predefinida de registros sub judice;
- recursos, realocações e capacidade de vagas reconstruídos sem usar os outcomes.

### Tratamento e estimando

O tratamento é ganhar marginalmente a vaga da primeira opção. O estimando principal é a intenção de tratamento local. O grupo abaixo do corte pode receber a segunda opção ou entrar em chamada posterior; isso faz parte do contrafactual institucional e não deve ser apagado.

### Running variable condicional

Dentro de blocos `curso–CNES × barema final × prioridade mesma-UF`, a idade determina a ordem restante. A running variable candidata é a idade em dias, centrada na idade do último selecionado do bloco. O sinal deve ser orientado de modo que valores positivos indiquem maior prioridade etária.

Esse RDD empilhado somente será estimado se houver observações suficientes dos dois lados, reconstrução perfeita da regra, nenhuma outra mudança no limiar e balanceamento local compatível. Caso o suporte seja insuficiente, o projeto deve encerrar esta rota em vez de chamar rank discreto de experimento.

### Outcomes

1. primário: início efetivo em até 30 dias da data prevista;
2. secundário: homologação;
3. secundários de retenção: ativo aos 90 e 180 dias, sempre incondicionais à entrada;
4. diagnóstico público disponível: ativo em 12/08/2026.

Não usar produção assistencial. Não condicionar a análise de retenção apenas aos que iniciaram, pois a entrada é pós-tratamento.

## 5. Especificação e diagnósticos

O modelo principal será local-linear na distância etária ao cutoff, com inclinações separadas, efeitos fixos de chamada e ponderação que dê o mesmo peso aos cutoffs. Erros devem respeitar o agrupamento no nível da célula de seleção. Randomização local pareada será reportada apenas se a janela passar balanceamento prévio e a regra de alocação estiver integralmente reconstruída.

Antes dos outcomes, congelar:

1. universo, modalidades e capacidade;
2. regra de duas opções;
3. tratamento de cotas, recursos, sub judice e realocações;
4. janela e kernel;
5. nível de agrupamento;
6. efeito mínimo relevante e potência;
7. outcomes e horizontes.

Testes obrigatórios: reprodução da classificação, suporte nos dois lados, densidade e mass points, balanceamento de covariáveis prévias, placebos em falsos cutoffs, leave-one-course e leave-one-UF. Nenhum teste compensa desempates não observados.

## 6. Linguagem permitida

Hoje: “há grande descontinuidade de homologação e presença ativa no corte publicado de seleção”.

Depois dos dados, se os portões passarem: “ganhar marginalmente a primeira opção aumentou localmente a probabilidade de entrada/presença ativa”.

Nunca: “o PMM-E causou aumento geral de especialistas no município”. Esse é outro estimando.
