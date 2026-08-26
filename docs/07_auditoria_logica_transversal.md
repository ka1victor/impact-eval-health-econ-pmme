# 07. Auditoria lógica transversal: o que cada número permite concluir

> Este documento é independente da ordem narrativa dos demais dossiês. Seu objeto é o projeto inteiro. Ele não redesenha ainda a estratégia empírica; identifica, para cada eixo, o estimando pretendido, as interpretações concorrentes, as conclusões vedadas e a evidência que faltaria para distingui-las.

## 1. A cadeia causal e seus elos não automáticos

O PMM-E pode ser representado pela seguinte cadeia:

```text
regra de bolsa
  → candidatura/preenchimento
  → entrada e permanência
  → oferta médica líquida e capacidade
  → produção e localização do cuidado
  → acesso e tempo de espera
  → trajetória clínica e saúde
  → custos e bem-estar
```

Nenhuma seta é uma identidade contábil. Um estudo pode identificar um elo e permanecer silencioso sobre os seguintes. O erro lógico recorrente do projeto era pular de uma métrica intermediária para um veredito sobre o objetivo final.

## 2. Não equivalências que governam a interpretação

| Evidência encontrada | Não equivale automaticamente a |
|---|---|
| Mais registros de médicos ativos | Oferta médica líquida adicional, porque pode haver migração de outro vínculo ou município |
| Mais vagas preenchidas | Permanência, produtividade ou qualidade |
| Mais atendimento local | Mais atendimento total, fila menor ou melhor saúde |
| Atendimento global estável | Impacto nulo, igualdade exata ou ausência de demanda induzida |
| Menos atendimento externo | Viagem efetivamente evitada ou economia de transporte |
| Mais exames | Diagnóstico precoce, tratamento oportuno ou sobrevida |
| Mais anestesiologistas | Centros cirúrgicos destravados ou substituição de urgências por eletivas |
| Menor coeficiente de distância na teleconsulta | Validação causal do PMM-E ou prova de que toda evasão é custo rodoviário |
| Despesa municipal menor | Economia consolidada do SUS ou benefício social líquido |
| Resultado estatisticamente não significativo | Efeito igual a zero |
| Resultado muito significativo | Identificação causal, se o desfecho foi construído a partir do tratamento |

## 3. Eixo 1 — atração, preenchimento e elasticidade-salário

### Pergunta substantiva

O adicional de bolsa induz mais especialistas a aceitar vagas que já seriam ofertadas em municípios comparáveis?

### O que a métrica precisaria observar

O denominador deve ser o universo de vagas ofertadas por município-especialidade-chamamento. O numerador deve distinguir candidatura, aceite, entrada efetiva e ocupação em uma data predefinida. A unidade natural é a vaga-especialidade, não todos os municípios brasileiros.

### Limitação atual

O arquivo nominal contém apenas participantes ativos. O script atribui a taxa de preenchimento conforme a faixa de IVS: 0,48/0,35 abaixo de 0,300; 0,88/0,70 entre 0,300 e 0,400; 0,94/0,80 acima de 0,400, dependendo da presença de médico. Assim, o salto estimado está parcialmente embutido no desfecho.

O RDD também inclui municípios sem evidência de vaga ofertada. Se a seleção das vagas variar com vulnerabilidade, estrutura ou demanda, o corte de bolsa não é o único componente que muda.

### Histórias compatíveis com mais preenchimento

- o adicional de bolsa realmente mudou a decisão marginal do médico;
- municípios acima do corte receberam vagas ou especialidades mais atraentes;
- o cadastro de ativos captura apenas sobreviventes, não todos os aceites;
- diferenças de infraestrutura, localização ou processo de seleção coincidem com o corte;
- a própria regra usada para construir a variável produz o salto.

### Conclusão vedada agora

Não se pode afirmar elasticidade de 1,48 ou saturação salarial em R$ 15 mil como resultado empírico. Também não se pode concluir que, acima desse valor, “o gargalo passa a ser infraestrutura” sem medir infraestrutura e testar mediação ou heterogeneidade.

### Evidência discriminante

Lista de vagas e candidatos, regra institucional completa, amostra restrita às vagas expostas, entrada observada e contraste local que isole o adicional da seleção das vagas.

## 4. Eixo 2 — retenção, FTE e oferta líquida

### Pergunta substantiva

Os profissionais entram, permanecem e acrescentam capacidade médica que não existiria sem o incentivo?

### Limitação atual

A retenção é calculada pelo número de competências distintas em que o município aparece na série, e não como sobrevivência individual de cada profissional desde a entrada. Um município pode manter seis meses de atividade com troca de médicos. Quem ainda não teve seis meses completos de exposição também pode ser classificado como baixa retenção por censura à direita.

O FTE é definido como um por registro nominal, embora o texto o apresente como carga horária observada no CNES. Não há dedução de vínculos anteriores, redução de horas em outro estabelecimento ou deslocamento de médico entre municípios.

### Histórias compatíveis com mais ativos

- entrada líquida de capacidade;
- relocalização de um especialista já atuante no SUS;
- formalização/cadastro de atividade preexistente;
- múltiplos vínculos do mesmo profissional;
- rotatividade com estoque municipal estável.

### Conclusão vedada agora

O salto negativo de retenção nas faixas mais vulneráveis não identifica abandono causado por falta de infraestrutura. Essa explicação é uma hipótese de mecanismo, não uma variável observada.

### Evidência discriminante

Painel profissional-vaga com datas de entrada e saída, tratamento correto da censura, CNES mensal antes e depois, carga horária e vínculos alternativos do mesmo médico.

## 5. Eixo 3 — resolutividade local, global e fila

### Pergunta substantiva

O programa aproxima o cuidado, amplia o acesso total e reduz o tempo entre a solicitação e o atendimento?

### A decomposição correta

Para residentes de um município:

$$Q_{global}=Q_{local}+Q_{externo}$$

Essa identidade permite separar localização e quantidade, mas não identifica causa nem fila.

| Padrão | Interpretações possíveis | O que falta para decidir |
|---|---|---|
| $Q_{local}\uparrow$, $Q_{global}$ estável | Substituição espacial com possível ganho de conveniência; mudança de codificação; perda externa compensada localmente | Distância/tempo, qualidade, fila e consistência de registro |
| $Q_{local}\uparrow$, $Q_{global}\uparrow$ | Demanda reprimida atendida; demanda induzida; tendência temporal; mudança de faturamento | Necessidade clínica, controle temporal e desfechos |
| $Q_{local}\uparrow$, $Q_{global}\downarrow$ | Localização melhor, mas acesso total potencialmente pior | Filas, recusas, capacidade e composição dos pacientes |
| $Q_{local}$ estável, $Q_{global}\uparrow$ | Expansão externa ou regional sem efeito de localização | Origem do aumento e exposição ao programa |

### Resposta à pergunta “se só remanejou, o impacto é nulo?”

Não. A localização do cuidado faz parte do bem-estar: pode reduzir tempo de viagem, faltas ao trabalho, custo, penosidade e descontinuidade. Isso é um efeito potencialmente valioso mesmo com $Q_{global}$ constante.

Mas “remanejamento” também não prova benefício. O cuidado local pode ter qualidade diferente; o paciente pode continuar esperando o mesmo; a redução externa pode ser mudança de faturamento; e o ganho local pode deslocar pacientes de municípios vizinhos. O impacto deve ser decomposto em quantidade, tempo, qualidade, deslocamento e transbordamentos.

### Limitação atual

O pipeline não encontra arquivos origem-destino brutos e carrega um painel pré-compilado. Na construção desse painel, a produção de cada médico é parametrizada e 65% do incremento é subtraído do atendimento externo. Logo, “substituição” é parte do mecanismo programado. Além disso, o resultado local possui $p$ paramétrico acima de 0,20 na janela estreita, embora o $p$ de permutação reportado seja inferior a 0,05; essa divergência exige auditoria, não linguagem de comprovação.

O efeito global não significativo também não autoriza “ausência de demanda induzida”: não rejeitar um efeito pode refletir imprecisão, e demanda total estável não testa a adequação clínica dos procedimentos.

### Conclusão vedada agora

Não se pode afirmar substituição geográfica pura, viagens evitadas ou efeito real na fila. A fila é o objetivo legal central e ainda não é observada no repositório.

### Evidência discriminante

Microdados mensais de residência-prestador sem incrementos sintéticos, período pré e pós, dados de solicitação/regulação, distância e tempo de viagem, composição por procedimento e análise de polos receptores.

## 6. Eixo 4 — produção clínica, cirurgias e saúde

### Pergunta substantiva

A capacidade adicional acelera diagnóstico e tratamento e melhora a trajetória clínica?

### Limitação atual

Os totais de consultas e exames são projeções: cada curso recebe uma produtividade mensal fixa. Eles não são contagens de produção vinculadas ao profissional. Da mesma forma, 384 registros de Anestesiologia descrevem a composição dos ativos, mas não demonstram que salas existiam, estavam ociosas ou foram reativadas.

No script de resolutividade, toda cirurgia local é tratada como eletiva e toda cirurgia externa como urgência, sem usar efetivamente `CAR_INT`. Localização e caráter de internação são dimensões distintas.

Exames adicionais podem representar rastreamento apropriado, repetição, mudança de código, diagnóstico de casos sintomáticos ou sobreutilização. Sem ligação a diagnóstico, estágio e terapia, “diagnóstico precoce” é uma interpretação possível, não observada.

### Conclusão vedada agora

Não se pode afirmar que anestesiologistas destravaram centros cirúrgicos, que urgências foram substituídas por eletivas, que cânceres foram detectados mais cedo ou que houve ganho de QALYs.

### Evidência discriminante

Produção observada por CNES, médico/curso e competência; capacidade instalada prévia; salas ativas; `CAR_INT` e transferências; APAC oncológica; intervalo diagnóstico-terapia; reinternação, complicação e mortalidade específica em horizonte plausível.

## 7. Eixo 5 — custos, transporte e bem-estar

### Pergunta substantiva

O custo social incremental do programa é menor que os recursos e o tempo poupados e os ganhos de saúde produzidos?

### Limitação atual

O BCR de 2,38 usa três parâmetros fixos: R$ 5 mil de adicional, 140 viagens mensais evitadas e R$ 85 por viagem. O BCR de 95,4 acrescenta 112 QALYs anuais e R$ 50 mil por QALY, também fixados. O pipeline não estima essas grandezas a partir dos dados.

Há ainda um problema de perspectiva: a bolsa é despesa federal; o transporte costuma ser municipal; o faturamento pode migrar entre prestadores; e recursos poupados podem ser realocados. Uma transferência entre entes ou estabelecimentos não é, por si só, ganho social. O benefício relevante inclui custo real de combustível, veículo e trabalho, tempo do paciente, qualidade e saúde; deve excluir dupla contagem.

### Se o gasto total municipal não cair

Isso não torna o impacto nulo. O recurso pode financiar outros serviços e produzir benefício de oportunidade. Mas tampouco permite chamar o valor realocado de “economia fiscal líquida” sem observar a execução e definir a perspectiva.

### Conclusão vedada agora

Não se pode dizer que o programa “se paga” nem reportar 2,4x ou 95,4x como resultado. São cenários pontuais sem incerteza e sem sensibilidade.

### Evidência discriminante

Custos observados por rota e veículo, ocupação, distância, diárias, frequência, fonte pagadora, custos do provimento, produção adicional e análise probabilística de sensibilidade por perspectiva municipal, federal e social.

## 8. Eixo 6 — OCI, teleconsulta e mecanismo espacial

### Pergunta substantiva

A OCI representa capacidade nova ou reclassificação? A teleconsulta reduz o papel da distância física?

### Limitação atual

O número de estabelecimentos OCI, a fração de 86,4% de reetiquetagem e os coeficientes $-1,4043$, $-0,1142$ e $-0,1480$ estão escritos diretamente no script. A execução não os estima dos microdados presentes.

Mesmo que estimados externamente, um gradiente menor na teleconsulta pode refletir diferenças de procedimento, seleção de pacientes, rede de faturamento, oferta de tecnologia e composição de origem/destino. É evidência coerente com fricção física menor, não prova exclusiva do mecanismo nem validação do BCR do PMM-E.

### Conclusão vedada agora

Não se pode afirmar que a OCI é 86,4% reetiquetagem no universo analisado aqui nem que a teleconsulta “comprova” que a barreira é rodoviária.

### Evidência discriminante

Extração reproduzível por competência/CNES, mapa OCI-componentes, mesma amostra e especificação para presencial e remoto, efeitos fixos comparáveis, composição de pacientes e intervalos de confiança conjuntos.

## 9. Eixo 7 — identificação e inferência

### O que o IVS pré-determinado resolve

O IVS 2010 não pode ter sido manipulado em resposta a uma política de 2025. Isso reduz uma ameaça de sorting da running variable.

### O que ele não resolve

- a oferta de vagas pode ser selecionada por infraestrutura, necessidade e capacidade;
- o adicional pode não ser função exclusivamente determinística dos cortes descritos;
- municípios sem vaga não estão expostos ao mesmo tratamento;
- resultados em municípios com médico ativo condicionam em uma variável pós-tratamento;
- outros programas e regras podem mudar no mesmo limiar;
- IVS antigo não torna automaticamente municípios vizinhos equivalentes em covariáveis atuais.

O “McCrary proxy” atual é uma razão de contagens em janelas, não um teste de densidade formal. O script 01 calcula diferença de médias, não RDD local linear. A permutação não está clusterizada apesar do rótulo; e os p-valores de preenchimento são mecanicamente pequenos porque o desfecho contém a faixa de tratamento. Placebos desse desfecho construído não validam o primeiro estágio.

No script 02, o ajuste chamado “FDR de Anderson” implementa a fórmula Benjamini-Hochberg sem impor monotonicidade reversa, e o índice KLK combina resultados simulados e observados. Esses nomes não substituem a auditoria estatística.

## 10. Achados surpreendentes defensáveis

O projeto encontrou surpresas relevantes, mas elas precisam ser classificadas corretamente.

### 10.1 Surpresa substantiva observada

**Anestesiologia representa 384 de 1.480 registros ativos, aproximadamente 26% do total.** É a maior categoria do cadastro. O fato motiva investigar se o provimento removeu uma restrição complementar à cirurgia, mas não demonstra capacidade ociosa anterior, produção adicional ou melhora clínica.

### 10.2 Surpresa de mensuração

**Os resultados aparentemente mais fortes recuperam valores inseridos na construção dos desfechos.** O preenchimento varia por faixa porque a própria variável recebe valores por faixa. Produção, substituição externa, viagens, custos e QALYs também combinam parâmetros com registros. Significância extrema não corrige essa circularidade.

### 10.3 Surpresa inferencial

Para resolutividade local em $c=0{,}300$ e $h=0{,}020$, o protótipo entrega:

- $\tau=+0{,}059$;
- erro-padrão HC1 de 0,0532 e $p_{param}=0{,}2673$;
- $p_{perm}=0{,}0285$;
- $q=0{,}1425$ no ajuste implementado;
- índice conjunto KLK com $p=0{,}2055$.

O desacordo não permite escolher a inferência mais favorável. Ele indica que a hipótese de permutação, a implementação e a família de testes precisam ser revistas.

### 10.4 Surpresa de robustez

Os placebos não são todos nulos. No falso corte $c=0{,}250$, o desfecho de diagnósticos globais apresenta $p_{perm}=0{,}030$ em $h=0{,}020$; outras combinações ficam próximas de 0,10. Ao mesmo tempo, as estimativas globais no corte real mudam de sinal entre bandas: +4.519, +1.764, -140 e -1.458 no output atual. Esse padrão é incompatível com a antiga narrativa de robustez uniforme.

### 10.5 Surpresa de reprodutibilidade

O script 01 não fixa a semente NumPy antes das permutações, de modo que os $p$-valores variam entre execuções. O script 03 escolhe exemplos a partir do primeiro elemento de um `set`, cuja ordem não é garantida. Parte do diff de `output/` pode, portanto, mudar sem mudança substantiva dos dados.

### 10.6 O que permanece hipótese, não achado

- elasticidades 1,48 e 0,31 e “saturação” da bolsa;
- evasão causada por precariedade de infraestrutura;
- substituição geográfica pura e ausência de demanda induzida;
- redução da fila;
- destravamento cirúrgico por anestesiologistas;
- viagens e horas efetivamente evitadas;
- BCR logístico/social;
- reetiquetagem OCI de 86,4% e validação por teleconsulta.

O achado mais importante da auditoria é, portanto, que **a evidência causal é mais frágil que a precisão aparente das saídas**.

## 11. Placar honesto do estado atual

| Eixo | O que se pode dizer agora | Veredito causal |
|---|---|---|
| Implantação | Há 1.480 registros ativos na referência, distribuídos por 325 municípios e 518 CNES | **Não aplicável: descrição** |
| Composição | Anestesiologia é o maior curso, com 384 registros | **Não aplicável: descrição** |
| Atração/preenchimento | A métrica atual é parcialmente imposta no código | **Não identificado** |
| Retenção/FTE líquido | Definições atuais não medem sobrevivência individual nem horas líquidas | **Não identificado** |
| Resolutividade local/global | Painel e mecanismos incorporam parâmetros de produção/substituição | **Não identificado** |
| Fila | Não observada | **Não avaliado** |
| Clínica | Produção, cirurgias e QALYs são presumidos ou não vinculados | **Não avaliado** |
| Custos | BCR é cenário determinístico | **Não avaliado** |
| OCI/teleconsulta | Cifras centrais estão fixadas no script | **Não reproduzido neste repositório** |

O projeto, portanto, não deve escolher entre “deu certo” e “deu errado” neste estágio. A conclusão defensável é mais estreita: **a implantação pode ser descrita, mas o efeito causal por eixo permanece em aberto**.

## 12. Regra para a etapa futura

O redesenho deverá começar pelo estimando, não pelo método preferido. Para cada eixo:

1. definir a unidade e a população exposta;
2. definir o contraste contrafactual;
3. separar desfecho observado de parâmetro;
4. listar interpretações concorrentes;
5. escolher o dado que as distingue;
6. só então escolher RDD, painel, evento ou outro desenho;
7. escrever a frase máxima que o resultado poderá sustentar antes de estimá-lo.

Essa etapa foi deixada deliberadamente para depois desta auditoria, conforme o escopo solicitado.
