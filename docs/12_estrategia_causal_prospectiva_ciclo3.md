# Estratégia causal prospectiva do ciclo 3

> **Decisão em 30/08/2026:** preservar a coorte do terceiro ciclo antes da
> observação dos resultados; usar força de trabalho como núcleo confirmatório e
> anestesiologia/cirurgias como módulo assistencial confirmatório condicional.
> Este documento é um plano. Ele não contém estimativas pós-tratamento e não
> reabre o protocolo individual bloqueado por dados administrativos.

## 1. Decisão executiva

O trabalho terá uma pergunta principal simples e relevante:

> Qual é o efeito de uma oferta imediata do PMM-E, em comparação com uma
> proposta do mesmo ciclo que não foi priorizada, sobre a oferta municipal de
> especialistas compatíveis com o curso ao longo de seis e doze meses?

O estimando principal é uma intenção de tratar pela **priorização imediata** no
terceiro ciclo. Não é o efeito de “participar efetivamente”, do número de bolsas
preenchidas ou do valor da bolsa. A família confirmatória será formada, antes do
pós-período, pelos cursos com mapeamento oficial curso–CBO não sobreposto e
suporte nos dois braços. Seis cursos já demonstram um limite inferior de suporte;
o Anexo I da Nota Técnica nº 59/2026 permite auditar os 24 cursos do ciclo 3 sem
inventar uma ponte local.

O módulo assistencial responderá, se passar os portões pré-tratamento:

> Uma oferta imediata de anestesiologia perioperatória elevou a realização de
> cirurgias eletivas compatíveis no estabelecimento e a oferta cirúrgica para os
> moradores dos municípios contemplados?

Esse módulo usará SIH/SUS. Anestesiologia é uma escolha substantiva, não uma
subamostra escolhida por resultado: é um insumo transversal à produção
cirúrgica, teve 119 células CNES–curso com oferta imediata, 290 vagas imediatas e
133 alocações publicadas. Ainda assim, a análise de cirurgias só será
confirmatória se qualidade, suporte, pré-tendências e potência forem aceitáveis
sem consultar qualquer resultado posterior ao início.

Ecocardiografia/SIA é a primeira alternativa condicional, e não um terceiro
desfecho acrescentado por conveniência. A decisão entre anestesiologia e essa
alternativa será tomada por uma rubrica congelada no pré-período.

## 2. O que SIH e SIA permitem observar

### 2.1 Situação no repositório

Não há hoje arquivos `.dbc`/`.dbf`, Parquets ou painéis analíticos de SIH/SIA
no repositório. Há apenas o prompt preparatório
[`prompts/infraestrutura_datasus_dbc.md`](../prompts/infraestrutura_datasus_dbc.md),
ainda não executado. Os Parquets mensais já existentes são do CNES.

SIH e SIA são fontes públicas do DATASUS:

- o [SIH/SUS](https://wiki.saude.gov.br/sih/index.php/P%C3%A1gina_principal)
  registra as internações financiadas pelo SUS por AIH e inclui estabelecimento,
  residência, procedimento, caráter, permanência e desfecho da internação;
- o [SIA/SUS](https://wiki.saude.gov.br/sia/index.php/P%C3%A1gina_principal)
  registra produção ambulatorial por instrumentos diferentes. BPA-C é agregado
  e não identifica paciente; BPA-I e APAC têm maior individualização;
- o [SIGTAP](https://sigtap.datasus.gov.br/tabela-unificada/app/download.jsp)
  deve ser historicizado mensalmente para interpretar os códigos de
  procedimentos e suas alterações.

O SIH não mede fila nem tempo de espera. Ele mede internações faturadas e
aprovadas no SUS. O SIA tampouco mede automaticamente acesso individual: parte
da produção é agregada. Produção, acesso e saúde não serão tratados como
sinônimos.

### 2.2 Peso observado, e não apenas espaço final

Consulta aos índices públicos do DATASUS em 30/08/2026 encontrou:

| Base e competência de referência | Arquivos | Transferência comprimida |
|---|---:|---:|
| SIH/RD, Brasil, 2025-01 | 27 | 88.707.644 bytes (84,6 MiB) |
| SIA/PA, Brasil, 2025-01 | 31, contando partes estaduais | 1.822.581.649 bytes (1,70 GiB) |

Mantida essa ordem de grandeza, 36 competências nacionais representam cerca de
3,0 GiB de transferência no SIH e 61 GiB no SIA. O espaço **persistente** pode
ficar abaixo de 1 GiB se cada arquivo estadual for baixado, convertido, filtrado
por CNES/município/procedimento, validado e descartado antes do próximo. Isso
não torna a transferência nacional do SIA menor que 1 GiB.

Consequência operacional: começar pelo SIH e só adquirir SIA se a rubrica
pré-tratamento selecionar ecocardiografia. Todo download deve ser restrito às UFs
da coorte congelada e manter URL, competência, tamanho, data e SHA-256 no
manifesto.

### 2.3 Um novo marcador público dos participantes

A
[Nota Técnica nº 59/2026-CGPLAD/DEGEPS/SGTES/MS](https://www.gov.br/saude/pt-br/centrais-de-conteudo/publicacoes/notas-tecnicas/2026/nota-tecnica-no-59-2026-cgplad-degeps-sgtes-ms.pdf/view),
publicada em 24/07/2026, orientou o registro dos participantes do PMM-E no CNES
com uma combinação específica:

- `IND_VINCULACAO = 070102` — bolsa, bolsista, subsidiado por outro ente;
- `NU_CNPJ_DETALHAMENTO_VINCULO = 00394544012787` — Ministério da Saúde;
- CBO compatível com o curso, definido no Anexo I;
- 16 horas assistenciais e 4 horas em outras atividades formativas.

O arquivo público `tbCargaHorariaSus` contém `IND_VINCULACAO`,
`NU_CNPJ_DETALHAMENTO_VINCULO`, CBO, cargas horárias e
`CO_PROFISSIONAL_SUS`. O pipeline atual preservou o primeiro, mas descartou o
CNPJ de detalhamento; por isso, ainda não é possível aplicar a assinatura nos
Parquets existentes. `070102` isolado é genérico: havia 19.255 vínculos com esse
código em 2026-07, antes da implementação observável do terceiro ciclo.

Essa assinatura pode fornecer, sem identificadores civis:

- número de participantes PMM-E registrados por vaga, CNES e curso;
- tempo até o primeiro registro;
- permanência do mesmo `CO_PROFISSIONAL_SUS` em seis e doze meses;
- saídas, reposições e outros vínculos públicos do mesmo profissional.

Ela melhora decisivamente a mensuração do primeiro estágio e da rotatividade,
mas **não cria exogeneidade**. A primeira tarefa deve comprovar que a combinação
chega à disseminação pública, é preenchida pelos gestores e reconcilia com as
alocações publicadas. Atraso, sub-registro ou uso inconsistente serão tratados
como erro de mensuração, não como ausência de participação.

## 3. Onde existe — e onde não existe — exogeneidade

### 3.1 O SIH/SIA não é a fonte de exogeneidade

No [Edital nº 25/2026 do terceiro ciclo](https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2026/chamamento-publico-sgtes-ms-no-5-2026-pmm-e/edital),
a SGTES predefiniu estabelecimentos elegíveis e quantidades. A produção anterior
no SIH e no SIA entrou na análise dos estabelecimentos, mas a decisão também
considerou manifestação dos gestores, capacidade instalada, baixa disponibilidade
regional, fluxos de pacientes, escala regional, orçamento e planejamento da
SGTES. Não foi publicado escore ou cutoff numérico que transforme essa seleção
em experimento natural.

Portanto, SIH/SIA são simultaneamente:

1. insumos observados da decisão administrativa; e
2. fontes de outcomes assistenciais.

Esse fato exige controlar trajetórias prévias e torna a hipótese de tendências
paralelas mais exigente. Ele não gera aleatoriedade.

### 3.2 O que o IVS determina

O IVS não determinou mecanicamente a participação, a quantidade ou a composição
das vagas do PMM-E. Condicionalmente a uma vaga ofertada, a categoria
administrativa de vulnerabilidade determinou a faixa anunciada da bolsa. Logo,
um RDD válido identificaria o efeito local de **R$ 5 mil adicionais de bolsa**, e
não o efeito do programa inteiro.

Essa trilha continua bloqueada porque a vintagem, a precisão e a regra aplicada
por vaga não foram recuperadas; a regra mudou entre 2025 e 2026; e a categoria
publicada diverge do IVS 2010 local em 226 de 531 municípios. A decisão está
documentada em
[`docs/auditorias/01_regra_institucional.md`](auditorias/01_regra_institucional.md)
e
[`docs/auditorias/aquisicao/A03_ivs_e_regra.md`](auditorias/aquisicao/A03_ivs_e_regra.md).

O RDD ficará como estudo secundário de alto valor **somente se** a regra
administrativa exata e o primeiro estágio forem demonstrados. Faixa publicada
não será usada como substituto de uma running variable desconhecida.

### 3.3 Fonte de identificação disponível hoje

A identificação disponível é comparativa e prospectiva, não um sorteio:

- as propostas do ciclo 3 e os resultados de priorização já estão congelados;
- os outcomes pós-tratamento ainda não estavam disponíveis quando este plano foi
  escrito;
- tratados e controles vêm do mesmo processo de adesão;
- há um pré-período mensal longo no CNES e será construído o mesmo no SIH;
- a data de tratamento é comum, simplificando o desenho.

O contraste principal será **imediata pura versus não priorizada pura**.
Cadastro de reserva não será controle principal, porque pode ser convertido ou
ocupado depois. Células mistas serão excluídas. O resultado só receberá linguagem
causal se a comparabilidade condicional e as pré-tendências forem compatíveis
com o desenho.

## 4. Suporte empírico já auditado

No resultado final da adesão dos gestores do ciclo 3 há 5.534 células
CNES–curso:

- 451 apenas imediatas;
- 1.595 apenas em reserva;
- 3.241 apenas não priorizadas;
- 247 com imediata e reserva.

Para os seis cursos já cobertos pela ponte anterior e com braços comparáveis, o
suporte puro — um limite inferior antes da auditoria do Anexo I — é:

| Curso | CNES–curso imediatas | CNES–curso não priorizadas |
|---|---:|---:|
| Anestesiologia perioperatória | 119 | 305 |
| Cirurgia geral minimamente invasiva | 33 | 337 |
| Ecocardiografia transtorácica | 56 | 261 |
| Oncologia clínica | 12 | 39 |
| Radioterapia | 7 | 21 |
| Ultrassonografia mamária | 13 | 774 |
| **Total** | **240** | **1.737** |

Há 104 municípios com pelo menos um curso imediato e um não priorizado dentro
dessa família mínima, somando 524 células (182 imediatas e 342 não priorizadas). No
mesmo CNES, há 105 estabelecimentos e 267 células (119 imediatas e 148 não
priorizadas). Esses subconjuntos permitem absorver choques município–mês ou
CNES–mês, mas mudam a população-alvo e não serão escolhidos depois dos
resultados.

A Nota Técnica nº 59/2026 também fornece CBOs para os cursos 17–24 e revisa
algumas pontes antigas. O C3-01 deverá construir uma nova matriz normativa,
quantificar sobreposições e congelar a família geral. O conjunto de seis acima
não será mantido artificialmente se a fonte oficial permitir uma família maior
sem dupla contagem.

Na anestesiologia, existem 77 municípios imediatos e 247 não priorizados. Ao
excluir municípios com outra oferta imediata cirúrgica concorrente, restam 45 e
187, respectivamente. Entre os 45 tratados mais limpos havia 100 vagas e 37
alocações, em 18 municípios. Isso melhora a interpretação, mas pode reduzir a
potência; os dois estimandos serão diferenciados antes da estimação:

- **efeito total da oferta de anestesiologia**, permitindo cointervenções
  publicadas; e
- **efeito da oferta isolada de anestesiologia**, sem outra oferta cirúrgica
  imediata no município.

O segundo será confirmatório apenas se passar o portão de potência. O primeiro
não será apresentado como efeito exclusivo de um anestesiologista quando houver
outros cursos cirúrgicos imediatos.

## 5. Outcomes e horizontes

### 5.1 Núcleo geral — força de trabalho

Unidade principal: município–curso–mês. A unidade CNES–curso–mês mede efeito no
serviço; região de saúde–curso–mês diagnostica criação líquida versus
redistribuição.

Outcome primário:

- número de profissionais distintos com CBO compatível no sexto mês após o
  início comum do tratamento.

O mesmo outcome será atualizado no décimo segundo mês, sem transformar o
horizonte que “funcionar” em novo primário. O estudo de evento mostrará todos os
meses maduros.

Mecanismos pré-especificados:

- número de vínculos que satisfazem a assinatura pública do PMM-E;
- células com ao menos um participante PMM-E registrado;
- tempo entre `T0` e o primeiro vínculo específico;
- entradas e saídas mensais;
- saldo líquido e churn (entradas + saídas);
- número de entrantes pós-oferta ainda presentes aos seis e doze meses;
- número de participantes identificados ainda presentes aos seis e doze meses;
- horas cadastradas, sem imputá-las como atendimento realizado;
- presença de ao menos um especialista.

Não será usada como outcome principal uma taxa de retenção condicionada aos que
entraram, pois a entrada é pós-tratamento. O número de novos entrantes ainda
presentes é válido sem transformar o conjunto de entrantes no denominador causal.

### 5.2 Anestesiologia — produção cirúrgica no SIH

O dicionário de procedimentos será definido com versões mensais do SIGTAP antes
de consultar o pós-período. O outcome assistencial primário candidato é:

- número mensal de AIHs iniciais, de caráter eletivo, em uma família cirúrgica
  compatível pré-especificada, realizadas no CNES contemplado.

Complementos:

- total de cirurgias compatíveis no município, para distinguir expansão de
  remanejamento entre hospitais;
- cirurgias de residentes do município, dentro e fora dele, para medir
  resolutividade geográfica;
- proporção atendida no próprio município, com denominador definido por
  residência e sem chamá-la de tempo de espera;
- mortalidade, permanência e valor aprovado apenas como exploratórios, pois
  composição de casos pode mudar.

Serão mantidas apenas AIHs iniciais quando o estimando for número de internações.
AIHs de continuidade não serão contadas como novas cirurgias. Produção fora do
SUS não é observada.

### 5.3 Alternativa condicional — ecocardiografia/SIA

Ecocardiografia possui ligação clínica direta com procedimentos ambulatoriais e
uma amostra razoável de propostas, mas somente 24 alocações foram publicadas nas
56 células imediatas e o SIA/PA é muito mais pesado. Ela só substituirá o módulo
de anestesia se a rubrica pré-tratamento mostrar simultaneamente:

- melhor ponte curso–procedimento;
- potência superior para uma mudança relevante;
- pré-tendências mais compatíveis;
- menor contaminação por outros cursos; e
- aquisição viável após um piloto estadual.

## 6. Especificação e inferência

Para a família geral, a especificação preferida no suporte dentro de município é:

\[
Y_{mct}=\alpha_{mc}+\gamma_{mt}+\delta_{ct}
+\sum_{k\neq -1}\beta_k
\left(\text{Imediata}_{mc}\times 1[t-T_0=k]\right)+\varepsilon_{mct},
\]

em que `m` é município, `c` é curso e `T0` será a primeira competência em que a
entrada dos médicos poderia aparecer no CNES. Efeitos fixos município–curso,
município–mês e curso–mês absorvem diferenças permanentes, choques gerais do
município e choques nacionais de cada curso. A versão CNES troca município por
estabelecimento.

Como há uma data comum e controles não priorizados, não são necessários
Callaway–Sant'Anna ou Sun–Abraham no desenho principal. Um TWFE/event study
saturado é adequado. Synthetic DiD poderá ser robustez; não será usado para
“consertar” pré-tendências incompatíveis.

Para anestesiologia, com um único curso, será usado DiD/event study entre
municípios ou CNES imediatos e não priorizados, com ajuste de trajetórias
pré-tratamento fixado antes do pós-período. A variante isolada excluirá, por regra
ex ante, outras ofertas cirúrgicas imediatas.

Inferência:

- erros agrupados no nível de decisão mais conservador, inicialmente município;
- wild cluster bootstrap como inferência principal de pequena amostra nos
  módulos específicos;
- intervalos e magnitudes substantivas, não apenas p-valores;
- correção de multiplicidade dentro de cada família de mecanismos;
- sem inferência por randomização, pois a priorização não foi aleatória.

## 7. Diagnósticos que podem bloquear a linguagem causal

Antes de abrir qualquer pós-período, o protocolo deverá congelar:

1. `T0`, versão do quadro e regra de imediata/não priorizada;
2. ponte curso–CBO e ponte curso–procedimento;
3. universo, exclusões e tratamento de conversões futuras;
4. transformação de outcomes, pesos e covariáveis;
5. menor efeito substantivamente relevante;
6. janela pré e horizontes de seis e doze meses;
7. especificação, nível de cluster e família de testes.

Os portões objetivos serão:

| Portão | Teste no pré-período | Se falhar |
|---|---|---|
| Exposição | status e data reproduzíveis; sem mistura não tratada | parar |
| Marcador PMM-E | assinatura da Nota 59 presente, estável e reconciliada com alocações | manter estoque total; rebaixar mecanismos individuais |
| Ponte | Anexo I/CBO e procedimento inequívocos e historicizados | retirar curso/módulo antes do pós |
| Cobertura | competências e unidades completas no CNES/SIH | corrigir aquisição; não imputar silenciosamente |
| Suporte | sobreposição em nível e trajetória prévia | restringir ao suporte já definido ou abandonar |
| Pré-tendência | teste conjunto, intervalos e teste de equivalência contra limite substantivo | rebaixar a associação ajustada |
| Potência | MDE menor que o efeito mínimo relevante | tornar módulo exploratório |
| Cointervenção | exposição concorrente mensurada e estimando interpretável | usar variante isolada ou abandonar alegação específica |

Placebos terão datas falsas no pré-período, outcomes CBO/procedimentos não
relacionados e testes de antecipação. A robustez incluirá leave-one-region-out,
pesos de sobreposição fixados no pré-período e synthetic DiD. Nenhum desses
testes transforma uma regra endógena em aleatória; eles apenas tornam a hipótese
condicional mais ou menos crível.

## 8. Hierarquia das alternativas

1. **Principal:** família oficial de cursos com CBO não sobreposto, força de
   trabalho municipal e DDD prospectiva; seis cursos são o suporte mínimo já
   auditado.
2. **Módulo assistencial preferido:** anestesiologia e cirurgias no SIH.
3. **Alternativa equivalente em ambição:** ecocardiografia e exames no SIA,
   acionada apenas pela rubrica pré-tratamento.
4. **Exploratória:** cirurgia minimamente invasiva e produção correspondente;
   mecanismo claro, mas somente 33 células CNES–curso imediatas.
5. **Estudo causal distinto:** RDD do IVS para o adicional de bolsa, se a regra
   administrativa for recuperada.
6. **Robustez histórica curta:** conversão de reserva em imediata no ciclo 2;
   limitada por seleção desconhecida e rápida reoferta dos controles.

Essa hierarquia evita dois erros: reduzir todo o projeto a anestesiologia antes
do teste de potência ou multiplicar linhas clínicas até encontrar um resultado.

## 9. Sequência operacional e calendário

1. Congelar a coorte, a exposição e as pontes com dados administrativos já
   públicos.
2. Construir piloto SIH pré-tratamento e historicizar SIGTAP.
3. Executar a rubrica usando somente pré-dados; congelar o plano de análise e
   seus hashes.
4. Aguardar seguimento comum de seis meses e só então atualizar CNES/SIH.
5. Estimar a versão de seis meses sem reescolher método, amostra ou outcome.
6. Atualizar a mesma análise aos doze meses.

Se `T0` for setembro de 2026, seis meses completos terminam em fevereiro de
2027 e doze meses em agosto de 2027; deve-se acrescentar a defasagem de
publicação do CNES/SIH. O prompt de congelamento fixará a data exata.

## 10. Conclusões que não serão feitas

- Vaga imediata não é profissional efetivamente trabalhando.
- Alocação publicada não é permanência.
- Presença no CNES não é produção nem capacidade líquida.
- Cirurgia faturada não é redução de fila nem melhora de saúde.
- Efeito no CNES não é necessariamente efeito no município ou na região.
- Ausência de significância não é prova de efeito zero.
- O contraste C3 não será chamado de experimento natural.
- O eventual RDD do IVS não será chamado de efeito do PMM-E inteiro.

Os prompts operacionais estão em
[`prompts/avaliacao_ciclo3/`](../prompts/avaliacao_ciclo3/README.md).
