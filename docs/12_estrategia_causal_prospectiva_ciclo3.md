# Estratégia causal prospectiva do ciclo 3

> **Decisão revista em 30/08/2026:** preservar a coorte do terceiro ciclo antes
> da observação dos resultados; usar anestesiologia como estudo principal de
> força de trabalho, cirurgias como desfecho clínico-chave condicionado a um
> portão prévio e os demais cursos como generalização secundária.
> Este documento é um plano. Ele não contém estimativas pós-tratamento e não
> reabre o protocolo individual bloqueado por dados administrativos.

## 1. Decisão executiva

O trabalho terá uma pergunta principal simples e relevante:

> Qual é o efeito de uma oferta imediata de anestesiologia pelo PMM-E, em
> comparação com uma proposta de anestesiologia do mesmo ciclo que não foi
> priorizada, sobre o número e a permanência de anestesiologistas no CNES
> ofertante e, como teste de oferta líquida, no município aos seis e doze meses?

O estimando principal é uma intenção de tratar pela **priorização imediata** no
terceiro ciclo. Não é o efeito de “participar efetivamente”, do número de bolsas
preenchidas ou do valor da bolsa. Anestesiologia foi escolhida antes do
pós-período porque tem ponte normativa integral (`225151`), maior suporte entre
os cursos sem sobreposição (119 CNES imediatos e 305 não priorizados) e uma
cadeia substantiva testável entre provimento, permanência e produção cirúrgica.

Essa escolha não elimina a pergunta geral. Oncologia clínica (`225121`) e
medicina intensiva (`225150`) formarão a generalização secundária, com efeitos
separados e um resumo empilhado predefinido. Eles não serão somados de forma a
esconder que anestesiologia domina numericamente o conjunto. Cirurgia geral
(curso 2) ficará como sensibilidade no CBO exclusivo `225225`, pois a norma
também aceita `225220`, compartilhado com outro curso.

O desfecho assistencial responderá, se passar os portões pré-tratamento:

> Uma oferta imediata de anestesiologia perioperatória elevou a realização de
> cirurgias eletivas compatíveis no estabelecimento e a oferta cirúrgica para os
> moradores dos municípios contemplados?

O SIH será secundário-chave, não co-primário automático: o programa pode elevar
o estoque médico antes que limitações de sala, equipe ou demanda permitam elevar
cirurgias. Anestesiologia teve 290 vagas imediatas e 133 alocações publicadas,
mas alocação publicada não prova início. A análise cirúrgica só receberá
linguagem causal condicional se proveniência, ponte clínica, suporte,
pré-tendências e potência forem aceitáveis sem consultar qualquer resultado
posterior ao início.

Ecocardiografia/SIA era a primeira alternativa condicional, e não um terceiro
desfecho acrescentado por conveniência. A rubrica prévia não a selecionou: SIA
não será baixado nem substituirá automaticamente o SIH incompleto. Essa decisão
não altera o estudo principal de força de trabalho em anestesiologia.

O torneio C3-03 foi concluído em 31/08/2026 sem abrir o pós. No CNES, há 119
tratados e 305 controles, MDE de 2,22 especialistas e suporte suficiente, mas
os intervalos não demonstraram equivalência de pré-tendências. No município,
há 77 tratados e 247 controles e MDE de 4,44. A classificação congelada é
`associacao_ajustada`; detalhes e linguagem permitida estão no
[`plano de pré-análise`](13_plano_pre_analise_ciclo3.md).

## 2. O que SIH e SIA permitem observar

### 2.1 Situação no repositório

O repositório agora contém um piloto SIH pré-tratamento, com 25 competências
entre 2024-06 e 2026-06, 612 CNES e 456 municípios da coorte ampla de
anestesiologia. A execução transferiu 2,14 GiB e produziu painéis persistentes
de menos de 0,5 MiB no total. Não há dados SIA locais.

A revisão independente encontrou pendências antes de usar o piloto para
pré-tendências. O corretivo C3-02B foi tentado em 31/08/2026: persistiu uma linha
para cada um dos 675 pares UF--competência, historicizou as 25 versões SIGTAP e
confirmou a classificação de 77 municípios tratados puros, 247 controles puros
e um município imediata+reserva excluído. Porém, o FTP oficial não continha
`RDAC2606.dbc` e `RDRR2606.dbc`. Foram 673 sucessos; as duas ausências não foram
convertidas em zeros. O [`relatório C3-02B`](auditorias/06_piloto_sih_anestesiologia.md)
mantém o painel clínico bloqueado. Esse portão foi separado do CNES: C3-03
executou o torneio de força de trabalho apenas com dados pré-T0, sem usar os
painéis SIH preliminares.

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
`CO_PROFISSIONAL_SUS`. O pipeline histórico preservou o primeiro, mas descartou
o CNPJ de detalhamento; por isso, ainda não é possível aplicar a assinatura nos
Parquets antigos. Na base bruta pública de 2026-07 havia 21.500 vínculos
`070102`, dos quais 7.924 também tinham o CNPJ do Ministério da Saúde. A
combinação continua incluindo APS e ciclos anteriores e, sozinha, não identifica
o ciclo 3.

Essa assinatura pode fornecer, sem identificadores civis:

- número de participantes PMM-E registrados por vaga, CNES e curso;
- tempo até o primeiro registro;
- permanência do mesmo `CO_PROFISSIONAL_SUS` em seis e doze meses;
- saídas, reposições e outros vínculos públicos do mesmo profissional.

Ela pode melhorar decisivamente a mensuração do primeiro estágio e da rotatividade,
mas **não cria exogeneidade**. A primeira tarefa deve comprovar que a combinação
chega à disseminação pública, é preenchida pelos gestores e reconcilia com as
alocações publicadas. Atraso, sub-registro ou uso inconsistente serão tratados
como erro de mensuração, não como ausência de participação.

`CO_PROFISSIONAL_SUS` será tratado como identificador operacional público cuja
estabilidade precisa ser testada. Não se presume algoritmo MD5, identificador
civil, anonimato absoluto nem continuidade perfeita entre competências.

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

O Anexo I da Nota Técnica nº 59/2026 foi transcrito integralmente e as
sobreposições foram recalculadas por código. Entre os 15 cursos com alguma
observação nos dois braços, somente três têm ponte integral sem CBO compartilhado:

| Curso | CNES–curso imediatas | CNES–curso não priorizadas |
|---|---:|---:|
| Anestesiologia perioperatória | 119 | 305 |
| Oncologia clínica | 12 | 39 |
| Medicina intensiva | 6 | 83 |
| **Total de células** | **137** | **427** |

O núcleo empilhado não será o outcome principal: anestesiologia representa 119
das 137 células imediatas e dominaria o resultado. Oncologia e intensiva serão
reportadas separadamente e em resumo secundário com pesos predefinidos. A ponte
anterior errou, entre outros pontos, radioterapia (`225320`, compartilhado com o
curso 14), mastologia (`225255`, compartilhado com o curso 14) e medicina
intensiva (`225150`). O JSON corrigido e os testes são a única fonte analítica
autorizada para o ciclo 3.

Na anestesiologia, há 78 municípios com alguma célula imediata e 247 somente
não priorizados; um dos 78 também contém reserva e deve ser excluído, deixando
77 tratados municipais puros. O indicador preliminar de ausência de outro curso
cirúrgico imediato sugere 62 municípios imediatos e 218 controles, mas será
recalculado depois da correção municipal C3-02B. Isso melhora a interpretação e
reduz potência; os estimandos serão diferenciados antes da estimação:

- **efeito total da oferta de anestesiologia**, permitindo cointervenções
  publicadas; e
- **efeito da oferta isolada de anestesiologia**, sem outra oferta cirúrgica
  imediata no município.

Uma variante ainda mais estrita excluirá qualquer outra oferta imediata do
PMM-E, mesmo não cirúrgica. Ela será robustez porque altera a população-alvo e
não pode ser escolhida depois dos resultados.

O segundo será confirmatório apenas se passar o portão de potência. O primeiro
não será apresentado como efeito exclusivo de um anestesiologista quando houver
outros cursos cirúrgicos imediatos.

## 5. Outcomes e horizontes

### 5.1 Principal — força de trabalho em anestesiologia

Unidade principal direta: CNES–mês. Município–mês é o secundário-chave que
separa ganho no serviço de criação líquida local; região de saúde–mês permanece
diagnóstico de redistribuição. O braço municipal usa todas as células de
anestesiologia e exclui qualquer combinação com reserva ou modalidades mistas.

Outcome primário:

- número de anestesiologistas distintos (`CBO 225151`) no sexto mês após o
  início operacional comum do tratamento.

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

### 5.2 Generalização secundária

Oncologia clínica e medicina intensiva repetirão o mesmo outcome nos CBOs
`225121` e `225150`. Cada efeito será mostrado separadamente. Um resumo
empilhado, se aprovado no pré-período, usará pesos fixados antes do pós e não
será descrito como “efeito médio geral” sem explicitar sua composição. O curso 2
entrará somente como sensibilidade no CBO exclusivo `225225`.

### 5.3 Anestesiologia — produção cirúrgica no SIH

O dicionário de procedimentos será definido com versões mensais do SIGTAP antes
de consultar o pós-período. O piloto atual usa todo o grupo 04; isso é uma
definição operacional ampla e ainda não demonstra sensibilidade específica à
anestesiologia. O outcome assistencial chave candidato é:

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

### 5.4 Alternativa condicional — ecocardiografia/SIA

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

Para anestesiologia, a especificação principal com data comum é:

\[
Y_{mt}=\alpha_m+\lambda_t
+\sum_{k\neq -1}\beta_k
\left(\text{Imediata}_{m}\times 1[t-T_0=k]\right)+\varepsilon_{mt},
\]

em que `m` é município e `T0` será a primeira competência em que a entrada dos
médicos do ciclo 3 puder ser observada no CNES. Efeitos fixos municipais e
mensais absorvem diferenças permanentes e choques nacionais. Especificações com
UF–mês ou região–mês, tendências prévias e pesos de sobreposição serão
predefinidas apenas com dados pré-tratamento.

A generalização secundária empilhará município–curso–mês para os cursos 1, 12 e
24. A DDD com município–mês e curso–mês será usada somente onde houver variação
dentro do município; fora desse suporte, serão reportados DiDs específicos por
curso. Não se apresentará a DDD estrita como se usasse todas as 564 células.

Como há uma data comum e controles não priorizados, não são necessários
Callaway–Sant'Anna ou Sun–Abraham no desenho principal. Um TWFE/event study
saturado é adequado. Synthetic DiD poderá ser robustez; não será usado para
“consertar” pré-tendências incompatíveis.

No nível do CNES, será usado o mesmo DiD/event study como análise de localização
do efeito. A variante isolada excluirá, por regra ex ante, outras ofertas
cirúrgicas imediatas; uma versão mais estrita excluirá qualquer outra imediata.

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

1. **Principal:** anestesiologia (`225151`), estoque municipal no mês 6 e a
   mesma medida atualizada no mês 12, por DiD/event study prospectivo.
2. **Secundário clínico-chave:** anestesiologia e cirurgias no SIH, condicionado
   à correção C3-02B e ao portão pré-tratamento.
3. **Generalização de política:** oncologia clínica e medicina intensiva,
   separadas e em resumo empilhado predefinido; curso 2/CBO 225225 como
   sensibilidade.
4. **Alternativa equivalente em ambição clínica:** ecocardiografia e exames no SIA,
   acionada apenas pela rubrica pré-tratamento.
5. **Estudo causal distinto:** RDD do IVS para o adicional de bolsa, se a regra
   administrativa for recuperada.
6. **Robustez histórica curta:** conversão de reserva em imediata no ciclo 2;
   limitada por seleção desconhecida e rápida reoferta dos controles.

Essa hierarquia evita dois erros: confundir o estudo principal coerente de
anestesiologia com uma alegação sobre todas as especialidades, ou multiplicar
linhas clínicas até encontrar um resultado.

## 9. Sequência operacional e calendário

1. Manter a coorte, a ponte, os pesos e o protocolo C3-03 congelados.
2. Acrescentar competências CNES sem consultar efeitos até `202703` estar madura.
3. Reexecutar o SIH pelo C3-02B quando AC/RR 2026-06 estiverem publicados, com
   27 UFs, 675 sucessos, exposição municipal correta, pico medido e SIGTAP já
   historicizado; isso libera apenas o subprotocolo clínico.
4. Estimar a versão de seis meses sem reescolher método, amostra ou outcome.
5. Atualizar a mesma análise aos doze meses.

Com `T0=202609`, os endpoints congelados são `202703` e `202709`; deve-se
acrescentar a defasagem de publicação do CNES/SIH.

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
