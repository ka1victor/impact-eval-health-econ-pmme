# 01. Outcomes e estimandos do PMM-E

> **Status:** agenda conceitual ampla. Na primeira versão, a pergunta ativa é se
> a disponibilização imediata de vagas aumenta o estoque municipal de
> especialistas e se os novos médicos permanecem pelo horizonte comum maduro.
> O estimando e a fila estão definidos em
> [`05_roadmap_execucao.md`](../06_execucao/05_roadmap_execucao.md).
>
> Este documento define o que o projeto quer medir antes de escolher método ou produzir resultados. O foco é o efeito do componente de provimento do PMM-E, não o efeito agregado de todas as frentes do Agora Tem Especialistas.

Na agenda completa, espera e acesso são os outcomes mais próximos do objetivo
legal. O desenho anterior havia escolhido cobertura sustentada da vaga em 180
dias; ele está preservado em [`04_escopo_eficacia_operacional.md`](04_escopo_eficacia_operacional.md),
mas não será executado na primeira versão.

No plano vigente, o estoque em `município–curso–mês` é o outcome primário.
Entradas, saídas, saldo e presença seis meses depois são mecanismos; presença em
doze meses será incorporada apenas quando a coorte congelada tiver seguimento
comum. Presença cadastral não será tratada como identificação de bolsista.

## 1. Pergunta central

O provimento de especialistas em regiões prioritárias aumenta a capacidade efetiva do SUS e melhora o acesso oportuno à atenção especializada? Se sim, por quais mecanismos, para quais pacientes e a que custo?

A redução do tempo de espera é o objetivo explicitamente atribuído ao Projeto Mais Médicos Especialistas pelo art. 22-D da Lei 12.871/2013, acrescido pela Lei 15.233/2025. Portanto, força de trabalho e produção são mecanismos intermediários; espera e acesso são os outcomes de política mais próximos do objetivo legal.

A cadeia causal de interesse é:

```text
regra de incentivo e oferta de vagas
        ↓
aceite, entrada e permanência do especialista
        ↓
capacidade médica líquida e produção efetiva
        ↓
acesso, localização e tempo de espera
        ↓
oportunidade clínica e desfechos de saúde
        ↓
custos públicos, tempo do paciente e bem-estar
```

Cada seta é uma hipótese. O projeto produzirá um resultado separado para cada elo, sem transformar um resultado intermediário em veredito global.

## 2. Hierarquia dos outcomes

### 2.1 Outcomes de implementação e primeiro estágio

Eles respondem se o instrumento de política alterou a força de trabalho médica.

| Outcome | Estimando pretendido | Unidade | Horizonte | Interpretação máxima |
|---|---|---|---|---|
| Preenchimento | Efeito da condição de incentivo sobre a probabilidade de uma vaga ofertada ser ocupada | Vaga-especialidade-chamamento | Data fixa após cada chamada | Atração para vagas ofertadas |
| Entrada efetiva | Efeito sobre a probabilidade e o tempo até início do exercício | Profissional-vaga | Dias/semanas | Conversão de aceite em trabalho efetivo |
| Retenção | Efeito sobre a sobrevivência no posto | Profissional-vaga | 6 e 12 meses | Permanência, com censura tratada |
| FTE líquido | Efeito sobre horas especializadas adicionais no município/região | Município-especialidade-mês | Mensal | Capacidade adicional, descontando vínculos deslocados |

Esses outcomes são necessários para qualquer análise posterior, mas não medem fila, qualidade ou saúde.

### 2.2 Outcomes primários de acesso

Eles correspondem mais diretamente ao objetivo legal de reduzir espera e ampliar o acesso especializado.

| Outcome | Estimando pretendido | Unidade | Medida principal | Risco de interpretação |
|---|---|---|---|---|
| Tempo de espera | Efeito sobre dias entre solicitação válida e atendimento | Solicitação-paciente-procedimento | Mediana e percentis 75/90 | Mudança de cadastro ou cancelamento |
| Atendimento da demanda | Efeito sobre a probabilidade de uma solicitação ser atendida em janela fixa | Solicitação | 30/60/90 dias | Seleção das solicitações registradas |
| Acesso global | Efeito sobre atendimentos especializados recebidos pelos residentes | Município-procedimento-mês | Quantidade por população elegível | Demanda induzida ou mudança de codificação |
| Acesso local | Efeito sobre atendimentos realizados mais perto da residência | Par residência-prestador | Parcela local e distância/tempo | Proximidade não garante qualidade |

O tempo de espera será o outcome primário de política se houver dado comparável. Volume não será usado como substituto silencioso de fila.

### 2.3 Outcomes de capacidade e produção

Eles testam o mecanismo entre profissional presente e cuidado entregue.

| Outcome | Medida | Unidade | Condição para interpretação |
|---|---|---|---|
| Produção atribuível | Consultas, exames e procedimentos observados | CNES-especialidade-procedimento-mês | Vínculo temporal e clínico com o profissional |
| Capacidade instalada em uso | Salas, equipamentos, turnos e agendas ativas | Estabelecimento-mês | Baseline anterior ao provimento |
| Composição eletiva/urgência | Internações por caráter e procedimento | Residência-prestador-mês | Usar `CAR_INT`, sem inferir caráter pela geografia |
| Encaminhamento e retorno | Sequências na linha de cuidado | Paciente ou coorte | Ligação consistente entre eventos |

### 2.4 Outcomes clínicos

| Domínio | Outcome | Horizonte plausível | Interpretação |
|---|---|---|---|
| Oncologia | Tempo diagnóstico-terapia e estágio ao diagnóstico | Meses | Oportunidade e gravidade inicial |
| Cirurgia | Complicações, conversão urgência/eletiva e reinternação | 30/90 dias | Qualidade e oportunidade cirúrgica |
| Cardiologia | Diagnóstico, seguimento e internação evitável específica | Meses | Continuidade e manejo de risco |
| Saúde da mulher/digestiva | Conclusão da linha diagnóstica após exame alterado | Meses | Resolução, não apenas produção de exames |

Mortalidade geral municipal não será outcome primário de curto prazo. Desfechos clínicos devem ser específicos à linha de cuidado e ao tempo biológico relevante.

### 2.5 Outcomes econômicos e de bem-estar

| Outcome | Perspectiva | Componentes |
|---|---|---|
| Custo incremental do provimento | Federal e SUS consolidado | Bolsa, supervisão, administração e contrapartidas |
| Custo logístico | Municipal e social | Rotas efetivas, veículo, ocupação, distância e custo marginal |
| Tempo do paciente | Social | Viagem, espera presencial, acompanhante e trabalho perdido |
| Capacidade liberada nos polos | Regional/SUS | Produção adicional possível e redução de congestionamento |
| Custo-efetividade | Social | Custos incrementais e desfechos clínicos observados |

Transferências entre entes e prestadores serão separadas de recursos reais. Não haverá BCR sem análise de sensibilidade e perspectiva explícita.

### 2.6 Equidade e transbordamentos

Todos os outcomes serão examinados por IVS, região, distância ao polo, especialidade e capacidade inicial. A análise de equidade é distributiva: pergunta quem ganha, não apenas se a média muda.

Transbordamentos importam porque um médico pode ser deslocado de outro município e porque a redução de fluxo para um polo pode liberar capacidade para terceiros. O efeito municipal não será automaticamente interpretado como efeito regional líquido.

## 3. O que constitui sucesso em cada eixo

| Eixo | Evidência favorável | Evidência insuficiente |
|---|---|---|
| Provimento | Mais vagas comparáveis ocupadas e maior FTE líquido | Mais registros ativos sem denominador ou baseline |
| Retenção | Maior sobrevivência individual ajustada por censura | Município aparece em várias competências |
| Acesso | Menor espera e/ou maior demanda atendida | Mais produção bruta isolada |
| Proximidade | Menor distância/tempo com qualidade não pior | Prestador no mesmo município apenas |
| Clínica | Linha de cuidado mais oportuna e melhores desfechos específicos | Mais exames presumidos como diagnóstico precoce |
| Economia | Benefício incremental robusto a incerteza | Cenário pontual com parâmetros fixos |

O programa pode funcionar em um eixo e não em outro. O relatório final será um perfil de efeitos, não um selo único de sucesso ou fracasso.

## 4. Ordem de prioridade

1. Validar oferta de vagas, regra de incentivo e primeiro estágio.
2. Medir FTE e produção realmente adicionais.
3. Medir fila e atendimento da demanda.
4. Decompor acesso local/global e deslocamento.
5. Avaliar linhas clínicas com dados suficientes.
6. Fazer avaliação econômica apenas depois de observar recursos e efeitos.

Sem primeiro estágio válido, outcomes a jusante não serão atribuídos ao PMM-E pelo mesmo desenho.
