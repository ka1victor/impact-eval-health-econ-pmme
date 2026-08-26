# 01. Problema de política, teoria da mudança e inventário de métricas

> Este dossiê responde às duas primeiras perguntas da pesquisa: qual problema o PMM-E tenta resolver e quais métricas podem representar cada elo desse problema. O estado dos resultados aparece nos dossiês seguintes; a crítica transversal está em [07_auditoria_logica_transversal.md](07_auditoria_logica_transversal.md).

## 1. Genealogia normativa sem extrapolação

A [Lei nº 12.871/2013](https://www2.camara.leg.br/legin/fed/lei/2013/lei-12871-22-outubro-2013-777279-normaatualizada-pl.html) instituiu o Programa Mais Médicos. Entre seus objetivos estão reduzir a carência de médicos em regiões prioritárias, fortalecer a atenção primária, aprimorar a formação e integrar ensino e serviço. A redação atual também inclui qualificar a assistência especializada em todos os níveis de atenção e ampliar a especialização em áreas estratégicas.

A [Lei nº 15.233/2025](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/lei/l15233.htm) instituiu o Programa Agora Tem Especialistas. O art. 1º estabelece os objetivos gerais de qualificar e diversificar serviços, ampliar a oferta e reduzir o tempo de espera por atenção especializada. O art. 21 acrescentou o art. 22-D à Lei nº 12.871/2013 e criou o Projeto Mais Médicos Especialistas, destinado ao provimento em regiões prioritárias **com vistas à redução no tempo de espera**.

Essa distinção importa:

- o **Agora Tem Especialistas** é um programa amplo, com contratação complementar, telemedicina, radioterapia, diálise e outras frentes;
- o **PMM-E** é seu componente de provimento e formação de especialistas;
- um efeito do PMM-E não deve ser confundido com o efeito do programa amplo;
- metas de fila e oferta são oficiais; mecanismos como “vans evitadas”, “centro cirúrgico ocioso” ou “segundo gargalo criado pela APS” são hipóteses empíricas, não enunciados da lei.

## 2. O problema em uma teoria da mudança

O problema central é o acesso tardio e desigual à atenção especializada. A hipótese do componente de provimento pode ser decomposta:

1. a remuneração diferenciada aumenta a atratividade de vagas prioritárias;
2. o profissional aceita, entra e permanece;
3. sua entrada aumenta a oferta líquida e a capacidade efetiva;
4. a capacidade muda quantidade, localização ou composição dos atendimentos;
5. essas mudanças reduzem espera e descontinuidade;
6. atendimento oportuno altera a trajetória clínica;
7. benefícios clínicos e logísticos podem superar os custos do programa.

Cada item é um estimando distinto. Confirmar o item 1 não confirma o 7; refutar o 5 não refuta necessariamente o 4.

## 3. Quem usaria os números e para qual decisão

| Usuário | Decisão | Métrica necessária | Limite da decisão |
|---|---|---|---|
| SGTES/MS | Calibrar adicional e desenho dos chamamentos | Preenchimento e permanência por vaga-especialidade | Não inferir saúde ou custo-benefício a partir da adesão |
| SAES/MS e gestores estaduais | Distribuir capacidade e organizar referências | Produção líquida, origem-destino, espera e transbordamentos | Atendimento local não basta para avaliar fila |
| Gestores municipais | Comparar provisão local e encaminhamento | Viagens, tempo, custo real e qualidade relativa | Despesa remanejada não é necessariamente economia fiscal |
| Avaliadores econômicos | Comparar custos e benefícios sociais | Custos incrementais, tempo, saúde e incerteza | Não monetizar produção presumida como benefício observado |

## 4. Inventário de métricas

### 4.1 Provimento e capacidade

| Métrica | Definição e unidade | Fonte desejada | Estado atual | Interpretação máxima |
|---|---|---|---|---|
| Vagas ofertadas | Contagem vaga-estabelecimento-especialidade-chamamento | Editais e anexos SGTES | Ausente | Não calculável |
| Preenchimento | Entradas no prazo / vagas ofertadas | Seleção e exercício SGTES | Numerador parcial; denominador ausente | Não calculável |
| Entrada efetiva | Profissional iniciou atividade até data fixa | SGTES + CNES | Cadastro de ativos, sem universo de selecionados | Descrição de ativos |
| Retenção | Sobrevivência individual após 6/12 meses, com censura | Painel individual SGTES/CNES | Série agregada por município-curso | Não calculada corretamente |
| FTE adicional líquido | Horas SUS pós menos contrafactual/preexistente | CNES mensal | Um FTE presumido por registro | Cenário, não observação |
| Elasticidade da oferta | Variação proporcional do preenchimento / variação da bolsa | Métricas anteriores identificadas | Resultado deriva de preenchimento atribuído no código | Não estimada |

### 4.2 Acesso, localização e fila

| Métrica | Definição e unidade | Fonte desejada | Estado atual | Interpretação máxima |
|---|---|---|---|---|
| Produção local | Atendimentos de residentes no próprio município | SIA/SIH mensal por residência-prestador | Painel pré-compilado com incrementos parametrizados | Não identificado |
| Produção externa | Atendimentos de residentes fora do município | SIA/SIH mensal por residência-prestador | Redução de 65% imposta na construção | Não identificado |
| Resolutividade local | $Q_{local}/Q_{global}$ | Fluxos observados | Mistura observado/premissa | Protótipo de métrica |
| Acesso global | $Q_{global}/população$ | Fluxos observados | Mistura observado/premissa | Protótipo de métrica |
| Tempo de espera | Dias entre solicitação e atendimento | Regulação interoperável prevista no art. 47-A da Lei nº 8.080 | Ausente | Não avaliado |
| Deslocamento | Distância/tempo dos atendimentos efetivos | SIA/SIH + matriz viária | Horas presumidas por curso | Cenário |

### 4.3 Linha de cuidado e saúde

| Métrica | O que poderia responder | Fonte desejada | Estado atual | Risco lógico |
|---|---|---|---|---|
| Consultas e exames observados | Capacidade usada | SIA por CNES/procedimento | Produtividade fixa por curso | Confundir projeção com produção |
| Eletiva/urgência | Mudança de composição hospitalar | SIH com `CAR_INT` | Local é tratado como eletivo e externo como urgência | Confundir geografia com caráter |
| Tempo diagnóstico-terapia | Oportunidade do cuidado | SIA/APAC/SIH vinculados | Ausente | Falar em fila sem tempo observado |
| Estadiamento | Diagnóstico em estágios mais iniciais | APAC oncologia | Ausente | Chamar mais exames de diagnóstico precoce |
| Reinternação/complicação/mortalidade específica | Resultado clínico | SIH/SIM em horizonte adequado | Ausente | Pular de processo para saúde |

### 4.4 Custos e bem-estar

| Métrica | Perspectiva | Estado atual | Uso permitido |
|---|---|---|---|
| Custo incremental da bolsa | Federal | R$ 5 mil/mês fixos para um degrau | Cenário do primeiro corte |
| Custo de transporte | Municipal/social | R$ 85 × 140 viagens fixas | Sensibilidade ilustrativa |
| Tempo do paciente | Social | Horas fixas por tipo de curso | Cenário, sem valoração observada |
| BCR logístico | Perspectiva não consolidada | 2,38 calculado por parâmetros | Não é resultado do programa |
| QALYs e BCR social | Social | 112 QALYs e R$ 50 mil fixos | Não reportável como evidência |

### 4.5 OCI e teleconsulta

| Métrica | Pergunta | Estado atual | Interpretação máxima |
|---|---|---|---|
| Fração de reclassificação OCI | Capacidade nova ou novo código? | 86,4% fixado no script | Hipótese a reproduzir |
| Coortes de entrada OCI | Há adoção escalonada? | Contagens fixadas no script | Protótipo |
| Gradiente de distância presencial/remoto | A distância física participa do mecanismo? | Coeficientes fixados no script | Resultado externo não reproduzido |

## 5. Métricas que não devem ser descartadas cedo demais

O fato de uma métrica ser difícil não a torna conceitualmente irrelevante.

- **Fila/regulação:** é o objetivo legal central. A heterogeneidade administrativa exige desenho e harmonização; não justifica substituí-la silenciosamente por volume.
- **Despesa:** gasto agregado pode ter pouca potência, mas custos de transporte e uso alternativo de recursos ainda importam. A solução é definir perspectiva e granularidade.
- **Mortalidade:** provavelmente inadequada como desfecho primário de curto prazo, mas desfechos específicos e intermediários podem ser apropriados.

## 6. Predições e limites antes da próxima estimação

- Se a bolsa afeta atração, o preenchimento **entre vagas comparáveis e ofertadas** deve aumentar no corte após o chamamento.
- Se a entrada adiciona capacidade, FTE e produção observados devem subir sem queda equivalente em outros vínculos do mesmo médico.
- Se há substituição espacial benéfica, $Q_{local}$ deve subir, $Q_{externo}$ cair e distância/tempo dos atendimentos efetivos diminuir, com qualidade não pior.
- Se há expansão de acesso, $Q_{global}$ ou a taxa de atendimento da demanda registrada deve subir; isso ainda não distingue necessidade atendida de demanda induzida.
- Se o objetivo legal é alcançado, a distribuição do tempo de espera deve melhorar para a população exposta.

Essas predições limitam o que cada número sustentará. O projeto ainda não as testou com os dados necessários.
