# 02. Provimento, retenção e elasticidade: auditoria dos resultados atuais

> Este documento responde à terceira pergunta da narrativa para o eixo de força de trabalho: o que já foi calculado e qual estatuto de evidência cada cálculo possui.

## 1. Fatos descritivos reproduzíveis

Na referência de 12/08/2026, os arquivos presentes contêm:

| Item | Contagem | Natureza |
|---|---:|---|
| Registros nominais ativos | 1.480 | Observado no arquivo nominal |
| Combinações únicas UF-CRM | 1.478 | Observado; sugere dois registros adicionais/múltiplos |
| Municípios com ao menos um registro | 325 | Observado |
| Estabelecimentos CNES | 518 | Observado |
| Registros na série histórica | 7.276 | Observado em nove competências |
| Anestesiologia | 384 registros | Composição descritiva, não impacto |
| Faixa 1 / 2 / 3 | 316 / 697 / 467 registros | Distribuição dos ativos, sem denominador de vagas |

Esses números mostram a implantação registrada. Não informam quantas vagas foram ofertadas, quantas ficaram vazias, quantos selecionados nunca entraram ou quantos médicos teriam trabalhado nesses locais sem o PMM-E.

## 2. O que o pipeline atual produz

O JSON de saída apresenta, entre outros números:

| Saída do protótipo | Como é gerada | Estatuto correto |
|---|---|---|
| Salto de preenchimento de +35,5 p.p. em 0,300 | A variável recebe valores definidos por faixa de IVS no próprio script | Regra recuperada, não primeiro estágio observado |
| Salto de +9,1 p.p. em 0,400 | Mesmo procedimento | Regra recuperada |
| Elasticidades 1,48 e 0,31 | Razão entre esses saltos construídos e os degraus de bolsa | Cenário algébrico |
| Retenção de -4,4 p.p. no corte 0,400 | Competências ativas agregadas por município | Estimativa exploratória com desfecho inadequado |
| FTE por 1.000 habitantes | Um FTE atribuído a cada registro nominal | Cenário de capacidade |
| Placebos nulos de preenchimento | Aplicados à variável construída por faixa | Não validam a relação causal |

Os p-valores muito pequenos de preenchimento são esperados: o tratamento por faixa participa da construção do desfecho. Inferência estatística não corrige circularidade de mensuração.

## 3. Taxa de preenchimento: denominador e população em risco

A taxa correta é:

$$
Preenchimento_{v,s,c}=
\frac{\text{vagas com entrada válida até a data de corte}}
{\text{vagas efetivamente ofertadas}}
$$

Ela deve ser calculada por vaga $v$, especialidade $s$ e chamamento $c$. Municípios sem vaga não pertencem automaticamente ao denominador. Usar apenas o cadastro de ativos produz seleção por sobrevivência e não observa as vagas fracassadas.

Para interpretar o corte do IVS como incentivo, ainda precisamos saber se:

- a faixa determina o valor da bolsa de forma mecânica;
- a oferta e a composição das vagas são contínuas no corte;
- infraestrutura, distância, porte e especialidade não mudam de regra no mesmo limiar;
- o adicional foi conhecido no momento da candidatura;
- não houve outras vantagens discretas associadas à faixa.

## 4. Retenção: estoque municipal não é sobrevivência individual

O script conta quantas competências aparecem para cada município e transforma seis ou mais em retenção igual a um. Essa medida possui quatro problemas:

1. troca de médicos pode manter o município “ativo” sem retenção do profissional;
2. profissionais do ciclo recente não tiveram tempo de completar seis meses;
3. a ausência de identificador individual na série impede ligar entrada e saída;
4. agregar todos os cursos mascara retenção específica por especialidade.

O resultado negativo próximo de 0,400 pode ser sinal a investigar, mas não permite atribuir evasão à infraestrutura. A mesma cifra pode refletir composição de ciclos, censura, curso ou rotatividade.

## 5. FTE e adicional líquido

Presença nominal não equivale a 40 horas adicionais. A medida desejada é:

$$
\Delta FTE_{m,s,t}=FTE^{pós}_{m,s,t}-FTE^{contrafactual}_{m,s,t}
$$

O CNES mensal deve informar horas, vínculos e estabelecimentos antes e depois. Também é necessário verificar se o profissional:

- já trabalhava no mesmo município;
- reduziu horas em outro prestador local;
- migrou de um município vizinho, criando deslocamento espacial sem aumento regional;
- acumulou vínculos sem cumprir a carga presumida.

## 6. Elasticidade: qual resposta e qual margem?

Uma elasticidade de oferta pode significar candidatura, aceite, entrada, permanência ou horas. Esses são comportamentos diferentes. Além disso, comparar um salto de 50% com outro de 33,3% em patamares distintos não identifica sozinho “saturação”; mudam vulnerabilidade, composição de vagas e população marginal.

Antes de estimar, deve-se definir:

- resultado: preenchimento, entrada, retenção ou FTE;
- base: nível abaixo do corte, média local ou probabilidade contrafactual;
- horizonte: primeiro chamamento, 6 ou 12 meses;
- população: vagas comparáveis efetivamente ofertadas;
- interpretação: efeito local no limiar, não política ótima nacional.

## 7. Veredito atual do eixo

O eixo de provimento possui uma base descritiva útil, mas não um primeiro estágio causal validado. A formulação correta é:

> Na referência disponível, o PMM-E registra 1.480 participantes ativos em 325 municípios. O efeito do adicional de bolsa sobre preenchimento, retenção e oferta líquida permanece não identificado porque faltam o universo de vagas e medidas individuais observadas desses desfechos.

Os números de +35,5 p.p., +9,1 p.p., 1,48, 0,31 e -4,4 p.p. devem permanecer apenas como diagnóstico do pipeline anterior até que sejam reconstruídos a partir de dados observados.
