# 05. Plano principal: vagas viram médicos?

> Registro canônico da primeira versão, já executada. O desenho individual
> anterior permanece preservado como agenda futura. A próxima avaliação
> prospectiva está em
> [`12_estrategia_causal_prospectiva_ciclo3.md`](12_estrategia_causal_prospectiva_ciclo3.md).

## 0. Estado após a execução

O pipeline foi executado de ponta a ponta com as 26 competências do CNES. A
versão agregada está concluída como **comparação ajustada**, não como avaliação
causal. A razão é anterior ao resultado do CNES: no mesmo grão
município–curso e na mesma amostra que identifica a DDD, a modalidade imediata
não prediz alocação confirmada (+2,79 p.p.; EP 6,89 p.p.; `p=0,6871`).

A diferença ajustada principal no estoque foi −0,446 especialista por
município–curso (IC 95% [−0,934; 0,042]). Ela não é denominada efeito do
PMM-E. O teste conjunto de pré-tendências (`p=0,2546`) e o placebo temporal
(`p=0,8684`) não corrigem a falta de primeiro estágio.

A auditoria de implementação, os resultados permitidos e as conclusões vedadas
estão em
[`auditorias/04_auditoria_pipeline_agregado.md`](auditorias/04_auditoria_pipeline_agregado.md).

## 1. Pergunta substantiva

> A disponibilização de vagas do PMM-E para preenchimento imediato aumentou o
> número de especialistas nos municípios contemplados? Os novos médicos
> permaneceram pelo maior horizonte comum observado?

Em linguagem curta: **vagas viram médicos — e eles permanecem?**

O estudo mede a oferta médica cadastral local. Não mede o efeito global do
PMM-E sobre produção, espera ou saúde e não identifica nominalmente quais
profissionais são bolsistas. A inferência é sobre a disponibilização imediata
da vaga dentro do universo publicado, não sobre elegibilidade nacional ao
programa.

## 2. Por que a pergunta é relevante

O PMM-E pretende ampliar o provimento de especialistas em áreas prioritárias.
Uma vaga publicada só representa capacidade adicional se for seguida por maior
presença médica local. O efeito pode assumir formas diferentes:

- aumento persistente do estoque municipal de especialistas;
- entrada seguida de saída rápida;
- troca de profissionais sem mudança do estoque;
- remanejamento entre estabelecimentos do mesmo município;
- deslocamento entre municípios, sem expansão regional líquida.

O outcome municipal evita chamar uma troca de hospital dentro do mesmo
município de atração local. Resultados no estabelecimento e na região de saúde
serão diagnósticos de redistribuição, não novas famílias de outcomes.

## 3. Contraste administrativo usado para identificação

O tratamento será fixado pelo quadro original do ciclo 1, chamada 1, publicado
em 24/07/2025. Após agregar todos os CNES do município:

```text
Immediate_ms = 1  se o município m tinha ao menos uma vaga imediata no curso s
Immediate_ms = 0  se tinha vaga apenas em cadastro de reserva no curso s
```

No quadro de origem existem 1.295 células CNES–curso: 503 apenas imediatas, 782
apenas em reserva e 10 com ambas as modalidades. Esses números descrevem a
fonte, não a amostra municipal final. A agregação `município–curso`, a ponte
curso–CBO e os requisitos de variação dentro do município determinarão a
amostra identificadora antes da observação dos efeitos.

Cadastro de reserva não significa ausência do programa. Ele pode ser
reapresentado, convertido ou alocado posteriormente. Portanto, o estimando é:

> efeito da disponibilização inicial para preenchimento imediato, comparada à
> permanência inicial apenas em cadastro de reserva, entre
> municípios–especialidades incluídos no mesmo quadro administrativo.

A classificação inicial permanecerá fixa. Ativações posteriores da reserva
serão documentadas e tratadas como cruzamento entre regimes no seguimento; não
serão usadas para redefinir retrospectivamente tratamento ou amostra.

## 4. Dados, unidade e outcomes

### 4.1 Oferta

Fonte principal:
`data/raw/aquisicao/vagas/2025_ciclo1_chamada1_vagas.xlsx`.

Somente o ciclo 1, chamada 1, define a coorte inicial. Reapresentações e
retificações não serão somadas como novas vagas. Chamadas posteriores serão
usadas apenas para auditar novas exposições durante o seguimento.

### 4.2 Unidade principal

A unidade será `município–curso–mês`. Para cada curso, será congelado um
conjunto defensável de CBOs a partir dos requisitos oficiais. O mesmo
profissional será contado uma única vez dentro do município–curso–mês, ainda
que possua mais de um vínculo ou CNES local.

Os identificadores serão tratados como texto. Identificadores civis não serão
publicados; os produtos analíticos usarão somente as chaves técnicas mínimas.

### 4.3 Outcome primário

```text
especialistas_mst = número de CO_PROFISSIONAL_SUS distintos
                    no município m, no mês t, pertencentes
                    aos CBOs elegíveis para o curso s
```

Esse outcome mede estoque cadastral de especialistas. Um aumento é compatível
com expansão da oferta local, mas não prova que os profissionais adicionais
sejam bolsistas nem que as horas cadastradas tenham sido realizadas.

### 4.4 Mecanismos secundários

Usando a estabilidade longitudinal de `CO_PROFISSIONAL_SUS`, que deverá ser
validada antes do uso:

- `entradas_mst`: profissionais presentes no mês e ausentes do mesmo
  município–curso nos seis meses anteriores;
- `saidas_mst`: profissionais cuja última presença é seguida por pelo menos três
  competências consecutivas de ausência;
- `saldo_mst`: entradas menos saídas;
- `entrantes_presentes_6m`: entrantes da coorte pós-oferta ainda observados no
  mesmo município–curso seis meses após a entrada;
- `entrantes_presentes_12m`: a mesma medida em doze meses, somente quando toda a
  coorte congelada possuir seguimento comum maduro.

Entradas e saídas serão contagens, não taxas divididas por estoque
pós-tratamento. A proporção retida entre entrantes será apenas descritiva,
porque o tratamento pode alterar a composição de quem entra.

## 5. Janela e maturidade

A primeira versão utilizará as 26 competências planejadas do CNES:

- pré-tratamento: 2024-06 a 2025-06;
- 2025-07: mês de transição, excluído da DDD estática;
- pós-tratamento observado: 2025-08 a 2026-07.

Toda a trajetória pós disponível será mostrada. A versão inicial permite
acompanhar o estoque por aproximadamente doze meses depois do anúncio. Para
presença seis meses após a entrada, a coorte madura será formada por entradas
entre 2025-08 e 2026-01.

Presença doze meses depois da entrada ainda não é comum e madura nessa janela.
Ela fica pré-especificada para uma atualização prospectiva do painel, sem
misturar profissionais com tempos distintos de seguimento. Novas competências
ampliarão o horizonte; não substituirão nem redefinirão a janela da primeira
versão. Para acompanhar por doze meses toda a coorte de entradas de 2025-08 a
2026-01, será necessário estender o painel até 2027-01.

Saídas serão calculadas somente nos meses para os quais existam três
competências posteriores. Observações sem seguimento suficiente serão marcadas
como censuradas, nunca como permanência ou ausência.

## 6. Portões antes da estimação

### 6.1 Relevância da classificação administrativa

Antes de construir outcomes, as listas públicas de alocação e homologação do
ciclo 1 serão usadas para verificar se a classificação imediata prediz uma
probabilidade substantivamente maior de alocação/homologação que a condição
apenas em reserva.

Esse teste é um portão de relevância, não uma estimativa de impacto. Se a
classificação não separar exposições administrativas, ela não será usada como
tratamento causal.

### 6.2 Ponte curso–CBO

É obrigatório construir e auditar a correspondência `curso PMM-E → CBO(s)` a
partir dos requisitos oficiais de elegibilidade. O portão deverá informar:

1. quais CBOs representam cada curso;
2. se a correspondência é unívoca ou envolve múltiplas especialidades;
3. onde conjuntos de CBOs se sobrepõem;
4. quantos municípios–curso permanecem numa amostra não ambígua;
5. quantos municípios possuem simultaneamente cursos imediatos e apenas em
   reserva e, portanto, identificam a DDD com efeitos município–mês.

O arquivo `output/aquisicao/ponte_curso_cbo_oficial.json` e seu script gerador
estão versionados como artefatos candidatos. O nome do arquivo não substitui a
auditoria: proveniência de cada correspondência, sobreposições e perdas da
amostra ainda devem passar por este portão antes da construção do outcome.

### 6.3 Integridade longitudinal do CNES

Antes de calcular entradas ou saídas, serão validados:

- estabilidade de `CO_PROFISSIONAL_SUS` entre competências;
- duplicidades entre vínculos e estabelecimentos;
- distinção entre ausência real, arquivo ausente e registro não aplicável;
- mudanças de CBO, CNES e município;
- cobertura temporal idêntica nos grupos de tratamento e comparação.

A existência ou o versionamento de um artefato não o torna automaticamente um
produto validado. Scripts e outputs só mudam o estado da fila depois de passarem
pelos testes substantivos correspondentes.

## 7. Estratégia de identificação

Como o ciclo 1 possui uma única data inicial de exposição, a especificação
principal será uma DDD estática:

```text
Y_mst = alpha_ms
      + gamma_mt
      + delta_st
      + beta (Immediate_ms × Post_t)
      + epsilon_mst
```

em que:

- `alpha_ms` são efeitos fixos município–curso;
- `gamma_mt` são efeitos fixos município–mês, que absorvem choques gerais do
  mercado médico local;
- `delta_st` são efeitos fixos curso–mês, que absorvem choques nacionais da
  especialidade;
- `beta` é a diferença pós-oferta entre cursos inicialmente imediatos e apenas
  em reserva, líquida desses efeitos.

O outcome primário será estimado em níveis, para que `beta` seja interpretado
em número de especialistas. A inferência será agrupada por município; serão
reportados número e tamanho dos clusters e sensibilidade a municípios
dominantes.

Um estudo de evento com a mesma estrutura mostrará todos os meses pré e pós
observados. Com uma única coorte inicial, Callaway–Sant'Anna e Sun–Abraham não
são necessários nesta versão. Métodos sintéticos não serão usados para
"corrigir" retrospectivamente pré-tendências incompatíveis.

## 8. Condições para linguagem causal

A classificação imediata não foi aleatória. O fato de os grupos pertencerem ao
mesmo quadro melhora a comparabilidade, mas não garante identificação. A
interpretação causal exige:

1. relevância administrativa da classificação imediata;
2. suporte entre cursos imediatos e em reserva dentro dos municípios;
3. tendências paralelas condicionais antes da oferta;
4. ausência de choque simultâneo específico dos cursos tratados;
5. resultado não concentrado em poucos municípios;
6. perdas e mudanças cadastrais não diferenciais;
7. documentação das exposições posteriores do grupo de reserva.

Se os diagnósticos falharem, a entrega será denominada **comparação ajustada**,
não impacto causal. Não se escolherá retrospectivamente janela, amostra ou
método em função do sinal dos resultados.

## 9. Escopo ativo e congelado

Entram na primeira versão:

- ciclo 1, chamada 1;
- painel CNES mensal de 2024-06 a 2026-07;
- estoque municipal de especialistas como outcome primário;
- entradas, saídas, saldo e presença seis meses depois como mecanismos;
- presença em doze meses como atualização pré-especificada quando madura;
- diagnósticos no CNES e na região para distinguir remanejamento;
- DDD estática e estudo de evento.

Permanecem congelados:

- ciclos 2 e 3 como coortes de tratamento e adoção escalonada;
- RDD pelo IVS e efeito causal dos diferentes valores de bolsa;
- synthetic DiD, matrix completion e variáveis instrumentais;
- FTE, produção SIA/SUS, internações SIH/SUS, filas e outcomes de saúde;
- custos, custo-benefício e heterogeneidades adicionais;
- identificação individual de bolsistas e envio dos pedidos A07.

As faixas anunciadas poderão aparecer apenas em descrições de baseline. Não
serão interpretadas como efeito causal da bolsa sem running variable e regra
administrativa validadas.

## 10. Sequência operacional

```text
1. Validar a relevância de imediata versus reserva nas listas públicas
2. Congelar a ponte curso–CBO e a amostra municipal identificadora
3. Adquirir e validar as 26 competências CNES
4. Construir o painel município–curso–mês e o estoque de especialistas
5. Construir entradas, saídas e coortes de presença com censura explícita
6. Produzir descritivas, DDD estática e estudo de evento
7. Auditar pré-tendências, suporte, clusters, perdas e novas exposições
8. Entregar nota com linguagem proporcional à identificação
9. Atualizar presença em doze meses quando a coorte comum estiver madura
```

Durante a execução desta versão não havia outra frente empírica autorizada. O
plano individual anterior continua bloqueado por dados administrativos. O
resultado do ciclo 1 permanece fechado e não depende de identificar quais
médicos pertencem ao PMM-E. A preparação prospectiva posterior do ciclo 3 tem
fila e portões próprios; não reabre nem corrige retrospectivamente esta análise.

### 10.1 Infraestrutura de Dados Paralelizável (Parser DBC -> Parquet)

Tarefas de engenharia de dados desacopladas do modelo econométrico podem ser desenvolvidas em paralelo (ex: em worktree/branch isolado) sem interferir no pipeline principal:
- **Prompt:** [`prompts/infraestrutura_datasus_dbc.md`](../prompts/infraestrutura_datasus_dbc.md).
- **Utilidade:** Habilitar a ingestão e conversão de microdados do DATASUS distribuídos em `.dbc` (SIA ambulatorial / APAC e SIH hospitalar / AIH) diretamente para `.parquet` colunar com compressão `zstd`.
- **Eficiência e Escopo Local:** o parser foi especificado para filtragem
  seletiva durante a ingestão. Isso pode manter a pegada persistente pequena,
  mas não reduz o tráfego: uma competência nacional observada tinha 84,6 MiB no
  SIH/RD e 1,70 GiB no SIA/PA. O piloto deve medir o custo antes de prometer
  limite de disco.
- **Isolamento:** Prepara a infraestrutura para eventual reabertura de WP3 e WP4 sem violar o congelamento metodológico da V1 nem alterar arquivos de `data/`.

## 11. Definição de conclusão

O trabalho estará concluído quando puder informar, com horizonte e linguagem
compatíveis com os dados:

> Entre municípios–especialidades incluídos no mesmo quadro do PMM-E, a
> disponibilização imediata alterou em X o estoque cadastral de especialistas
> ao longo de Y meses. O padrão refletiu entrada persistente, saída, reposição
> ou remanejamento, dentro dos limites do contraste observado.

A conclusão declarará explicitamente que presença cadastral não prova
participação individual no PMM-E, horas efetivamente trabalhadas, produção ou
efeito sobre pacientes.

### 11.1 Resultado desta versão

A execução respondeu apenas à parte descritiva e ajustada da pergunta. Ela não
preenche a formulação causal acima porque o portão de relevância falhou na
amostra identificadora. Repetir a mesma DDD com filtros, janelas ou estimadores
escolhidos pelo sinal observado não é próximo passo autorizado.

## 12. Próximo estudo, sem reabrir o ciclo 1

O autor autorizou em 30/08/2026 uma avaliação prospectiva separada do ciclo 3.
O estudo principal usa imediata pura versus não priorizada pura de
anestesiologia para medir o efeito direto no CNES ofertante e a oferta líquida
municipal; cirurgias no SIH são o secundário clínico condicionado, e oncologia
clínica/medicina intensiva são generalizações separadas. O C3-02 provou
viabilidade técnica do SIH. A tentativa
C3-02B de 31/08/2026 historicizou as 25 versões SIGTAP e produziu manifesto
para os 675 pares, mas o FTP oficial não continha AC e RR em 2026-06: foram 673
sucessos e duas falhas documentadas, sem zeros fabricados. O portão foi então
separado corretamente: C3-03 executou somente a força de trabalho com 26 meses
CNES pré-T0; o SIH continua bloqueando somente cirurgias. Anestesiologia teve
suporte, mas falhou equivalência estrita e potência para detectar um especialista:
MDE 2,22 no CNES e 4,44 no município. A classificação prospectiva é
`associacao_ajustada`, documentada em
[`docs/13_plano_pre_analise_ciclo3.md`](13_plano_pre_analise_ciclo3.md). A fila
deve seguir
[`prompts/avaliacao_ciclo3/`](../prompts/avaliacao_ciclo3/README.md). Estimação
só ocorrerá quando a competência `202703` estiver madura, sem reescolher
amostra, outcome ou estimador.
