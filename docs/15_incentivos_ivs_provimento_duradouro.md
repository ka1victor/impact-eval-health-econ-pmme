# Atração e provimento duradouro de especialistas fora das capitais

> **Decisão em 31/08/2026, após conferência das bases:** o tema é viável como
> trabalho econométrico de implementação, com núcleo associativo e upgrade
> causal condicionado. A base sustenta atração administrativa e persistência da
> oferta médica local, mas não sustenta hoje “efeito total do PMM-E” nem
> retenção individual dos bolsistas. O primeiro portão operacional é reconciliar
> o denominador de preenchimento.

## 1. Tema e pergunta

Título de trabalho recomendado:

> **Atração de médicos especialistas e persistência da oferta local fora das
> capitais: evidências de implementação do Mais Médicos Especialistas.**

Pergunta empírica principal:

> Em que medida as vagas do primeiro ciclo do PMM-E foram preenchidas fora das
> capitais, quais características territoriais estão associadas ao
> preenchimento e se ele foi acompanhado por persistência da oferta médica
> local?

Pergunta econômica que motiva o mecanismo:

> Incentivos financeiros conseguem compensar as desvantagens territoriais na
> atração e no provimento duradouro de especialistas?

Ela combina duas forças distintas:

1. o IVS descreve uma dimensão prévia de vulnerabilidade territorial;
2. o adicional da bolsa é o instrumento de política potencialmente capaz de
   compensar a menor atratividade local.

O trabalho não estimará o “efeito causal do IVS”. Vulnerabilidade não é um
tratamento manipulável e agrega múltiplas características territoriais. O
estimando causal candidato é o efeito local de **oferecer R$ 5 mil adicionais**
próximo a uma fronteira administrativa válida.

“Fora das capitais” é a definição operacional disponível hoje: município cujo
código IBGE não pertence às 27 capitais. Ela não equivale a “interior remoto”,
pois inclui municípios metropolitanos. Antes da estimação, uma tipologia
capital–metropolitano–interior próximo–interior remoto deverá ser construída e
congelada com fonte externa reproduzível. O contraste binário capital versus
não capital será descritivo: apenas 18 capitais aparecem no quadro e 14 possuem
vaga imediata, número insuficiente para apoiar sozinho a identificação.

## 2. Por que salário e IVS não entram como regressoras independentes simples

Na regra anunciada de 2025, o valor é função da faixa de vulnerabilidade:

| Faixa anunciada | Categoria declarada | Valor mensal anunciado |
|---|---|---:|
| Faixa 1 | muito alta vulnerabilidade | R$ 20 mil |
| Faixa 2 | alta vulnerabilidade | R$ 15 mil |
| Faixa 3 | média, baixa ou muito baixa | R$ 10 mil |

Portanto, uma regressão global que inclua simultaneamente `valor_bolsa` e IVS
como se variassem independentemente depende de extrapolação funcional e não
separa dois efeitos causais. As 177 divergências entre faixa anunciada e faixa
recalculada com o IVS local também não podem ser usadas como experimento:
enquanto sua origem não for explicada, podem refletir outro escore, versão,
arredondamento, exceção ou decisão administrativa endógena.

A decomposição conceitual correta, se R1 validar a atribuição, é:

\[
E[Y_m\mid R_m] = f(R_m-c) + \tau 1(R_m>c),
\]

onde:

- `R` é o escore administrativo de IVS;
- `f(R-c)` representa o gradiente suave de dificuldade territorial;
- `τ` é o salto associado à oferta do adicional da bolsa;
- `Y` é preenchimento ou oferta local persistente.

O gradiente é descritivo/associativo. O salto só recebe linguagem causal se a
regra, o suporte e as demais hipóteses da RDD passarem.

## 3. Dois módulos do artigo

### 3.1 Núcleo publicável com os dados atuais

Pergunta:

> Quais características territoriais e das vagas estão associadas à dificuldade
> de preenchimento e à evolução posterior da oferta local?

Este módulo é econométrico, mas associativo. Deve usar modelos separados e
transparentes:

1. gradiente de preenchimento por IVS;
2. diferenças por faixa/valor anunciado;
3. modelos ajustados por curso, UF e covariadas exclusivamente pré-oferta;
4. validação de sensibilidade e, se houver finalidade preditiva, desempenho
   fora da amostra.

O coeficiente da faixa não será chamado de efeito do salário. O coeficiente do
IVS não será chamado de efeito da vulnerabilidade. A finalidade é diagnosticar
onde e para quais especialidades a implementação encontra maior dificuldade.

População inicialmente planejada: todas as 1.295 células CNES–curso publicadas
no ciclo 1, chamada 1, em 368 municípios. “Interior” não será uma restrição de
amostra automática: 350 municípios já estão fora das capitais e concentram 593
das 678 vagas imediatas. A variação útil deverá vir de gradientes de
remoticidade, centralidade, infraestrutura e especialidade dentro desse
universo, preservando as capitais apenas como referência descritiva.

### 3.2 Upgrade causal condicionado

Pergunta:

> Qual é o efeito local de oferecer R$ 5 mil adicionais sobre preenchimento e
> provimento local próximo aos cutoffs de 2025?

Cutoffs candidatos:

- `0,400/0,401`: principal candidato, por ter suporte preliminar maior;
- `0,500/0,501`: replicação potencial, condicionada à potência.

O desenho seguirá
[`14_plano_implementacao_rdd_bolsa.md`](14_plano_implementacao_rdd_bolsa.md):
R1 reconstrói regra e escore; R2 audita suporte e cointervenções; R3 congela o
protocolo; R4 abre os outcomes administrativos. Nenhum resultado será usado
para escolher cutoff, janela ou especificação.

## 4. Outcomes e linguagem permitida

| Margem | Outcome preferido | Situação atual | Linguagem máxima |
|---|---|---|---|
| Atração administrativa | alocados confirmados / vagas imediatas efetivamente ofertadas | parcialmente observável; denominador precisa reconciliação | preenchimento administrativo |
| Homologação | homologados / vagas imediatas | observável parcialmente | candidatura homologada, não entrada em atividade |
| Procura | candidaturas válidas / vaga | universo não público | bloqueado até A07-02 |
| Entrada local | variação do estoque e entradas no CNES | observável agregadamente | oferta cadastrada local |
| Provimento em 6 meses | estoque/cobertura municipal em horizonte fixo | viável agregadamente | persistência da oferta local |
| Provimento em 12 meses | estoque em horizonte desde a publicação | calendário disponível até 2026-07, mas início efetivo incerto | atualização agregada com data-base explícita |
| Presença 12 meses após entrada | entrante ainda observado em `t+12` | censurado | aguarda CNES 2027-01 |
| Retenção do bolsista | participante permanece na mesma vaga | não identificável | bloqueado até ponte e log administrativos |
| Reocupação/rotatividade da vaga | spells sucessivos da mesma vaga | não identificável | bloqueado sem `id_vaga` estável |
| Salário recebido | valor individual pago por competência | não observado | bloqueado até A07-05 |

### Denominador de preenchimento

Cadastro de reserva não é vaga imediatamente disponível. O denominador
principal deve conter apenas vagas imediatas efetivamente abertas na chamada e
na versão válida. O quadro congelado contém 678 vagas imediatas e 1.145 de
reserva, totalizando 1.823. Reapresentações não serão somadas como vagas novas.

Antes da estimação, alocação e homologação precisam ser reconciliadas com esse
denominador no mesmo grão `município–CNES–curso–chamada`. A ausência de
`id_vaga` individual impede afirmar qual vaga física foi ocupada quando uma
célula contém mais de um posto.

A conferência de 31/08/2026 encontrou:

- 468 profissionais com “local de atuação confirmado”; todos pertencem a uma
  chave CNES–curso presente no quadro inicial;
- 257 confirmações em células com vaga imediata, mas 211 em células
  originalmente classificadas apenas como reserva;
- dez células com vaga imediata possuem mais confirmações do que a quantidade
  imediata publicada;
- 316 homologações foram publicadas; 296 estão em chaves do quadro inicial e
  vinte registros, distribuídos em 18 chaves, não fecham diretamente com ele;
- entre as vagas imediatas originais, a razão descritiva
  confirmação/vaga é 40,1% fora das capitais e 22,4% nas capitais.

O último contraste não é resultado econométrico nem evidência contra ou a favor
da “força gravitacional” dos centros. Ele pode refletir composição de cursos,
faixas de bolsa, gestão, transformação de reservas, realocação ou diferenças de
versionamento. Até a reconciliação, o outcome seguro é “confirmação ou
homologação observada na célula publicada”, não “vaga física preenchida”.

## 5. Atração, retenção e seleção pós-tratamento

“Retenção entre quem entrou” condiciona a análise a uma variável potencialmente
afetada pela bolsa. Se o incentivo muda quem entra, comparar a proporção
remanescente entre entrantes mistura efeito e composição.

Com dados públicos, os outcomes mais limpos são incondicionais:

- estoque municipal do CBO no horizonte;
- cobertura municipal no horizonte;
- número de novos entrantes ainda presentes em `t+6` ou `t+12`, reportado em
  nível e não apenas dividido pelos entrantes;
- mudança líquida do estoque desde o baseline.

Essas medidas representam **provimento duradouro agregado**, não retenção dos
participantes. Uma análise individual de retenção exigiria `id_vaga_pseudo` e
`id_profissional_pseudo` estáveis, datas de entrada/saída, afastamentos,
retornos e reocupações.

## 6. Unidade, estimação e inferência

### Núcleo associativo

- unidade administrativa: `município–curso–chamada`, preservando o número de
  vagas como denominador;
- modelos candidatos: binomial para contagem preenchida/total, fractional logit
  para taxas e modelo linear como transparência/robustez;
- efeitos fixos candidatos: curso e UF; chamada quando mais de uma chamada for
  comparável;
- covariadas prévias: estoque de especialistas, população, infraestrutura
  observável e classificação territorial validada;
- inferência agrupada no município;
- especialidades não serão tratadas como observações independentes da regra
  municipal da bolsa.

Distância, tempo até polo regional e centralidade são teoricamente relevantes,
mas ainda precisam de fonte e regra reproduzíveis antes de entrar. “Interior”
não será definido por conveniência após os resultados.

### RDD

- atribuição e inferência no município;
- randomização local como estimador principal candidato por causa dos mass
  points em três casas decimais;
- local-linear com inclinações separadas como robustez;
- pesos por vagas podem alterar o estimando, mas não transformar várias vagas do
  mesmo município em atribuições independentes;
- testes de balanceamento, densidade, cutoffs placebo e
  `leave-one-mass-point-out`;
- wild cluster bootstrap não substitui inferência compatível com poucos
  municípios e running variable discreta.

O efeito em `0,400` e o efeito em `0,500` são efeitos locais em populações com
níveis distintos de vulnerabilidade. A diferença entre ambos pode sugerir
heterogeneidade, mas não será testada como conclusão principal sem potência.

## 7. Viabilidade observada

O diagnóstico reproduzível está em
[`output/rdd_bolsa/diagnostico_viabilidade_salario_ivs.json`](../output/rdd_bolsa/diagnostico_viabilidade_salario_ivs.json).

| Bloco | Evidência disponível | Decisão |
|---|---|---|
| Oferta | 1.295 células CNES–curso, 1.823 vagas, 368 municípios e 16 cursos | suficiente para descrever a oferta |
| Recorte territorial | 350 municípios fora das capitais; 593/678 vagas imediatas | tema territorial tem massa, mas “remoto” ainda não está medido |
| Valor anunciado | 100% das células com faixa; grade R$ 10/15/20 mil | suficiente como incentivo anunciado |
| Valor pago | não vinculável a vaga/profissional/mês | não estimar dose recebida |
| IVS local | cobertura de 100% dos municípios | suficiente para gradiente associativo |
| Regra administrativa | 177/368 municípios divergem da reconstrução local | RDD bloqueada em R1 |
| Suporte 0,400 | 12/8 municípios em ±0,010; 30/18 em ±0,020 | promissor, não aprovado |
| Suporte 0,500 | 5/5 em ±0,010; 8/6 em ±0,020 | fraco; somente replicação potencial |
| Alocação | 468 confirmações em chaves da oferta; 211 em células originalmente de reserva | outcome administrativo existe; denominador ainda bloqueado |
| Homologação | 316 registros; vinte não fecham diretamente com o quadro inicial | reconciliar realocações e versões |
| CNES | 26 competências, 2024-06 a 2026-07, 368 municípios | oferta local agregada e horizonte de seis meses tecnicamente viáveis |
| Ponte curso–CBO | 10 de 16 cursos sem sobreposição | núcleo CNES precisa restringir/estratificar |
| Presença individual | snapshot de sobreviventes e máscaras incompatíveis | retenção individual inviável hoje |

## 8. Veredito

Há segurança de produzir um trabalho econométrico relevante se o piso for:

> análise rigorosa da implementação, do preenchimento parcialmente observável e
> do gradiente territorial, com linguagem associativa.

Não há segurança, ainda, de produzir uma avaliação causal da bolsa. O RDD é um
upgrade de alto valor, mas pode morrer corretamente em R1. Se morrer, não será
substituído por regressão de faixa sobre IVS apresentada como causal.

Também não é viável hoje prometer “retenção dos médicos do PMM-E”. A formulação
defensável é **provimento duradouro da oferta local**, reservando retenção
individual para eventual resposta administrativa.

## 9. Plano de execução por sessão

O projeto segue duas pistas. A pista A garante uma entrega econométrica
associativa. A pista B acrescenta causalidade somente se os portões do RDD
passarem. Uma não pode emprestar linguagem da outra.

| Sessão | Trabalho autorizado | Entregável mínimo | Portão para avançar |
|---:|---|---|---|
| A1 | reconciliar oferta, reserva, alocação, realocação e homologação do ciclo 1 | `matriz_funil_ciclo1.parquet`, relatório de perdas e `portao_denominador.json` | numerador e população definidos sem somar reapresentações |
| A2 | construir tipologia territorial prévia | matriz capital/metropolitano/interior e dicionário de fontes | classificação completa e congelada antes dos modelos |
| A3 | definir estimandos associativos, covariadas, MDE, missing e inferência | registro de pré-análise com hashes | outcome primário e regra de linguagem aprovados |
| A4 | estimar atração/implementação | tabela principal, especificações de sensibilidade e diagnóstico de influência | resultados não dependem de uma única UF, curso ou município |
| A5 | construir desfechos CNES alinhados à homologação/início físico | painel de estoque, entradas e presença em seis meses | T0 validado e ponte CBO restrita às dez correspondências sem sobreposição |
| A6 | estimar associação com provimento duradouro e red team | resultados agregados e auditoria de seleção pós-tratamento | nenhuma interpretação como retenção individual ou efeito total |
| S | sintetizar artigo e materiais reprodutíveis | texto, apêndice e manifesto final | todas as afirmações respeitam o maior nível de identificação alcançado |

Pista causal paralela:

| Sessão | Trabalho autorizado | Regra de parada |
|---:|---|---|
| R1 | recuperar escore, vintagem, precisão, arredondamento e exceções | se a faixa não for reproduzida, encerrar RDD |
| R2 | suporte municipal, MDE, composição e cointervenções sem outcomes | se suporte/potência falhar, rebaixar a exploratório |
| R3 | congelar cutoff, janela, outcomes, inferência e hashes | sem registro, não abrir R4 |
| R4 | estimar efeito local do adicional sobre atração | sem primeiro estágio comportamental, não avançar ao CNES |
| R5 | estimar oferta local agregada próxima ao cutoff | sem ponte, não chamar de retenção do bolsista |

Os prompts executáveis dessas sessões estão em
[`../prompts/avaliacao_atracao_interior/`](../prompts/avaliacao_atracao_interior/README.md).

## 10. Regras de decisão finais

1. Se A1 não produzir denominador confiável, o outcome primário será binário
   por célula (“alguma confirmação/homologação observada”), com a modalidade
   original explícita; não haverá taxa de preenchimento por vaga.
2. Candidaturas por vaga, tempo até preenchimento e spells dependem de A07-02.
3. “Retenção” só entra no título se uma ponte individual e um log de eventos
   permitirem observar entrada, saída, censura e reocupação. Até lá, usar
   “persistência da oferta médica local”.
4. Se o curso exigir uma conclusão causal e R1 falhar, este tema não garante o
   requisito: será necessário trocar o desenho ou a política, não flexibilizar
   retrospectivamente o padrão de evidência.
5. SIH/SIA, produção, resolutividade e custo-benefício permanecem fora do núcleo.
