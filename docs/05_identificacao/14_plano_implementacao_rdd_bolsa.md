# Plano rápido de implementação — RDD do adicional de bolsa

> **Decisão em 31/08/2026:** este é o primeiro desenho a ser testado para uma
> nova afirmação causal. A comparação do ciclo 1 entre vaga imediata e cadastro
> de reserva permanece encerrada como associação ajustada. Nenhum resultado de
> efeito será consultado antes da aprovação dos portões abaixo.

> **Atualização em 04/09/2026:** o IVS público também falhou como instrumento
> fuzzy para a bolsa anunciada. A decisão consolidada, as alternativas e a nova
> ordem operacional estão em
> [`16_sintese_achados_e_novo_plano_causal.md`](16_sintese_achados_e_novo_plano_causal.md).

A formulação substantiva, os outcomes e o diagnóstico de viabilidade deste
plano estão em
[`15_incentivos_ivs_provimento_duradouro.md`](../01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md).

## 1. Pergunta, tratamento e estimando

Pergunta principal:

> Qual é o efeito local de **oferecer R$ 5 mil mensais adicionais** sobre a
> procura e o preenchimento das vagas do PMM-E próximas a uma fronteira
> administrativa do IVS?

O tratamento não é participação no PMM-E nem vulnerabilidade alta. É o salto
no **valor anunciado da bolsa**, condicional à existência de uma vaga já
publicada. O estimando primário é a intenção de tratar da oferta do adicional.
Somente com folha de pagamento e primeiro estágio financeiro poderá ser
estimado o efeito do valor efetivamente recebido.

Para o edital de 2025, as fronteiras candidatas são:

- `0,400/0,401`: R$ 10 mil para R$ 15 mil;
- `0,500/0,501`: R$ 15 mil para R$ 20 mil.

Não há salto em `0,300` na grade de 2025. O escore possui suporte discreto em
três casas decimais; por isso, randomização local é o estimador principal
candidato. RDD contínua local-linear será robustez, não escolha automática.

## 2. Sequência curta e fail-closed

```text
R1 regra administrativa e escore exato
        ↓ passou
R2 suporte, primeiro estágio da bolsa e cointervenções
        ↓ passou
R3 congelamento de amostra, outcomes e inferência
        ↓ hashes preservados
R4 efeito sobre procura/alocação
        ↓ primeiro estágio comportamental suficiente
R5 estoque CNES e permanência cadastral
        ↓ somente se justificável
R6 SIH/SIA e resolutividade
```

Se R1 ou R2 falhar, não se estima R4–R6. O produto será uma auditoria de
inviabilidade do RDD, não uma troca retrospectiva de cutoff, janela ou outcome.

## 3. R1 — reconstruir a regra aplicada

### Entradas

- quadro de vagas do ciclo 1, chamada 1, publicado em 24/07/2025;
- edital, retificações, FAQ e Anexo IV vigentes naquela publicação;
- arquivo do IVS identificado pelo ato administrativo, com vintagem, precisão
  e regra de arredondamento;
- `faixa_atracao_anunciada` observada em cada célula CNES–curso.

O arquivo local `data/ivs_ipea_2010_municipios.csv` é apenas candidato. Ele não
pode ser promovido a running variable administrativa enquanto a divergência
com as faixas publicadas permanecer sem explicação.

### Entregáveis planejados

- `scripts/rdd_bolsa/01_auditar_regra_e_suporte.py`;
- `output/rdd_bolsa/matriz_municipio_regra_ivs.csv`;
- `output/rdd_bolsa/portao_regra_ivs.json`;
- `docs/auditorias/07_portao_rdd_bolsa.md`.

### Testes e decisão

1. Toda vaga deve ter município, escore administrativo, faixa, valor e vigência.
2. A mesma combinação município–vigência deve ter um único escore e regra.
3. A grade reconstruída deve reproduzir a faixa publicada em 100% dos casos,
   salvo exceções identificadas em ato anterior ao outcome.
4. Deve ser possível localizar exatamente o lado do cutoff, inclusive o
   tratamento de `0,400`, `0,401`, `0,500` e `0,501`.
5. Hash, URL, data de captura e versão de cada fonte devem ser preservados.

Estados possíveis:

- `APROVADO_SHARP`: o lado do cutoff determina perfeitamente o valor anunciado;
- `APROVADO_FUZZY`: há exceções documentadas, mas o salto no tratamento
  declarado é forte e mensurável — valor anunciado para efeito da oferta ou
  valor recebido para efeito da dose;
- `REPROVADO`: escore, regra ou salto não são reconstruíveis.

O diagnóstico público atual encontra divergência entre faixa anunciada e faixa
recalculada em 177 dos 368 municípios do ciclo 1. Logo, o estado inicial de R1
é `REPROVADO_PENDENTE_DE_RECONSTRUCAO`, não autorização para estimar.

Esse número é reproduzido, apenas como diagnóstico, ao combinar
`output/aquisicao/quadro_vagas_tratamento.parquet` com
`data/ivs_ipea_2010_municipios.csv` e aplicar a taxonomia externa de 2025
(`IVS <= 0,400` → Faixa 3; `0,401–0,500` → Faixa 2; `> 0,500` → Faixa 1):

| Faixa anunciada | Recalculada 1 | Recalculada 2 | Recalculada 3 |
|---|---:|---:|---:|
| Faixa 1 | 19 | 46 | 37 |
| Faixa 2 | 0 | 13 | 94 |
| Faixa 3 | 0 | 0 | 159 |

A diagonal soma 191 municípios e as células fora da diagonal somam 177. Essa
reconstrução **não valida a regra**: os cutoffs são da taxonomia do Atlas do
Ipea, enquanto os documentos preservados não publicam o algoritmo numérico nem
o escore contínuo efetivamente usado pelo PMM-E.

### Diagnóstico adicional: a RDD fuzzy pública também não passa

Foi estimado o primeiro estágio entre o IVS 2010 disponível e o valor anunciado,
sempre com uma observação por município. No corte `0,400/0,401`, a diferença
bruta é -R$ 625 na janela de 0,010, praticamente zero na janela de 0,020 e só
fica positiva ao ampliar a janela; o salto local-linear muda de sinal entre as
especificações. No corte `0,500/0,501`, todos os municípios nas janelas de 0,010
a 0,050 recebem R$ 20 mil nos dois lados, de modo que o primeiro estágio é
exatamente zero.

Portanto, usar o IVS público como instrumento para a faixa publicada não salva
o desenho: falta relevância estável no primeiro estágio. A única janela de
0,010 em `0,400` que produz um coeficiente local-linear positivo é incompatível
com a diferença bruta negativa, usa apenas 20 municípios e não se sustenta nas
demais janelas; ela não será selecionada retrospectivamente.

Os números são reproduzidos por
`scripts/rdd_bolsa/01_auditar_primeiro_estagio_publico.py` e preservados em
`output/rdd_bolsa/a01_primeiro_estagio_publico.csv`. Esse resultado reprova
somente o desenho fuzzy com o arquivo público candidato. Ele não elimina uma
RDD sharp futura com o escore administrativo correto.

### Correção de 14/09/2026 — o corte de 0,500 não era um corte

O diagnóstico acima testou uma única taxonomia candidata, a do Atlas do Ipea
(`0,400` e `0,500`), e leu o resultado como falta de relevância. A leitura
precisa ser corrigida, e ela **agrava** o problema em vez de aliviá-lo.

`scripts/rdd_bolsa/01b_reconstruir_regra_faixa.py` faz a pergunta anterior:
existe **alguma** regra de limiar no IVS público que reproduza a faixa
anunciada? Artefato em `output/rdd_bolsa/a01b_reconstrucao_regra_faixa.json`.

**O corte de 0,500 é vazio.** O IVS máximo entre os municípios de Faixa 2 é
`0,437`. Na janela de `0,05` em torno de `0,500` há 31 municípios e **todos são
Faixa 1**, dos dois lados. O primeiro estágio exatamente nulo medido ali não
mede ausência de resposta à bolsa: mede ausência de regra naquele ponto. Era um
RDD estimado onde a regra não tem ação.

**Nenhum limiar reproduz a faixa.** Os intervalos de IVS das três faixas se
sobrepõem — Faixa 3 vai até `0,372`, Faixa 2 começa em `0,277`; Faixa 2 vai até
`0,437`, Faixa 1 começa em `0,303`. Em 44.073 pares comparáveis há **2.763
inversões (6,3%)**: municípios com IVS *maior* que recebem bolsa *menor*. Uma
única inversão já basta para provar que nenhuma regra de limiar monótona no IVS
público reproduz o anúncio, qualquer que seja o corte.

**Quanto falta.** A busca exaustiva sobre todos os pares de cortes acerta no
máximo **285 de 368 (77,4%)**, em `0,323` e `0,377` — longe dos `0,400/0,500`
supostos, que acertam 191 (51,9%). Acrescentar covariáveis municipais
pré-tratamento (tipologia, população, renda, IDHM, componentes do IVS, estoque
prévio, UF, região de saúde) não fecha a conta: com 2 a 3 divisões chega-se a
79–82%, o mesmo patamar da melhor regra de limiar, e só com profundidade 8 se
chega a 97,3% — com 368 observações, isso é memorização, não regra.

**Consequência.** O critério efetivo da bolsa usa informação que **não está**
em nenhuma base deste repositório. R1 continua `REPROVADO_PENDENTE_DE_RECONSTRUCAO`,
agora por um motivo mais forte e mais bem medido: não é que a taxonomia
candidata erra, é que nenhuma função de limiar do IVS público pode acertar. Isso
torna o pedido administrativo de **D-3** o único caminho para o estimando da
bolsa, e não uma formalidade.

### O que o edital de fato diz, e por que isso encerra a RDD no IVS

Lido em 14/09/2026 no PDF do DOU preservado em
`data/raw/aquisicao/ivs_regra/edital_sgtes_03_2025_dou.pdf`, com hash registrado
no artefato. Duas cláusulas importam:

- **11.1.4** dá a regra que sempre se supôs: Faixa 1 para muito alta
  vulnerabilidade, Faixa 2 para alta, Faixa 3 para média, baixa ou muito baixa.
  São as categorias do Atlas do Ipea, isto é, os cortes `0,400` e `0,500`. A
  taxonomia testada pela auditoria anterior era, portanto, a correta.
- **11.1.3** diz o que faltava: o valor é estabelecido "conforme critérios de
  **localização** e vulnerabilidade definidos de acordo com a faixa de atração
  definida no **Anexo IV** no site do Mais Médicos".

O edital não publica limiar numérico, vintagem do IVS nem algoritmo. O documento
operativo é o Anexo IV, que **não está no repositório**. O FAQ oficial da bolsa
repete as três categorias e também não traz limiar.

**O dado mostra exatamente a estrutura que as duas cláusulas descrevem.** A
divergência entre faixa anunciada e categoria de IVS é **estritamente
unidirecional**: `0` municípios recebem menos do que a categoria manda e `177`
recebem mais. Isso não é ruído de vintagem nem erro de medida — uma vintagem
diferente erraria nos dois sentidos.

> **O IVS não é o critério da bolsa. É o piso dela.** A categoria de IVS garante
> um valor mínimo, e o critério de localização do Anexo IV promove 48% dos
> municípios acima desse piso, nunca abaixo.

**E o piso não morde em nenhum dos dois cortes nominais.** É isso que encerra o
desenho:

| Corte | Janela | Esquerda | Direita |
|---|---|---|---|
| `0,500` | ±0,050 | 20 municípios, **100% Faixa 1** | 11 municípios, **100% Faixa 1** |
| `0,400` | ±0,010 | 10 municípios: 7 Faixa 1, 3 Faixa 2 | 8 municípios: 5 Faixa 1, 3 Faixa 2 |

Em `0,500` não há o que saltar: os dois lados já estão no teto de R$ 20 mil. Em
`0,400` não há nenhum município de Faixa 3 por perto — o maior IVS da Faixa 3 é
`0,372` — e a composição dos dois lados é equivalente, com a média até caindo ao
cruzar o corte. Quando o IVS chega ao limiar, a promoção pelo outro critério já
aconteceu.

**Conclusão de identificação.** A descontinuidade no IVS não falha por potência:
falha porque **o tratamento é localmente constante nos dois cortes**. Onde a
bolsa de fato varia — a faixa de IVS entre `0,25` e `0,44`, em que as três faixas
coexistem — a variação é governada pelo critério de localização, que não
observamos. Nenhuma escolha de janela, kernel ou estimador contorna isso.

**Testes de regra composta, todos negativos.** Foram testadas hipóteses de que o
piso do IVS seria promovido por uma condição simples: interior remoto (216/368),
renda per capita baixa (255), Norte/Nordeste (237), porte populacional (182),
ausência de RM/RIDE (182), estoque prévio baixo (180). Também bases alternativas:
maior subíndice do IVS (272, mas errando 62 para menos, o que viola o piso),
média dos subíndices (192). Nenhuma se aproxima de reproduzir a regra.

**Por que comparar municípios parecidos também não resolve.** Há suporte comum:
municípios de IVS semelhante recebem bolsas diferentes — é justamente o que as
inversões acima significam. O problema é o que gera essa variação. Dos 83
municípios fora da melhor regra, os 41 que recebem **mais** do que o IVS
preveria têm mediana de população de 7.933 contra 32.179 dos 42 que recebem
**menos**, renda per capita menor (R$ 414,78 contra R$ 479,51) e 12 de 41 em
interior remoto contra 2 de 42. Os desvios não são ruído de medida: são
sistematicamente alinhados com remoticidade e porte.

Isso é fatal para o pareamento porque **remoticidade é o previsor mais forte do
próprio desfecho** neste projeto — o gradiente de A4 vai de interior remoto a
capital com +32,6 p.p. Parear por IVS e comparar bolsas diferentes usa exatamente
a variação residual que está correlacionada com o gradiente territorial, e o viés
tem direção conhecida: municípios com bolsa maior são os mais difíceis de prover,
de modo que a comparação subestima o efeito da bolsa, podendo até inverter-lhe o
sinal. O artefato registra esse perfil em `quem_escapa_da_regra`.

**O que este diagnóstico não autoriza.** O corte de `0,323` foi encontrado por
busca de ajuste, não lido em ato normativo. Ele é hipótese a confrontar com o
documento pedido em D-3, e **não** um cutoff onde estimar efeito. Estimar ali
seria escolher o corte pelos dados e depois abrir o outcome.

## 4. R2 — suporte, composição e pacote de políticas

R2 deve ser executado sem abrir outcomes de procura, alocação ou CNES pós.

### Suporte

Para cada cutoff, reportar janelas simétricas `0,010`, `0,020`, `0,030` e
`0,050`, sempre em número de **municípios**, não apenas vagas ou cursos. Reportar:

- municípios e mass points de cada lado;
- vagas, cursos e CNES por município;
- concentração por UF, curso e mass point;
- MDE para taxa de preenchimento e para `+0,5` especialista;
- sensibilidade ao município mais influente.

Usando somente o IVS local candidato, o suporte preliminar é:

| Cutoff | Janela | Lado inferior | Lado superior | Total |
|---:|---:|---:|---:|---:|
| 0,400/0,401 | 0,010 | 12 | 8 | 20 |
| 0,400/0,401 | 0,020 | 30 | 18 | 48 |
| 0,400/0,401 | 0,030 | 42 | 26 | 68 |
| 0,400/0,401 | 0,050 | 77 | 39 | 116 |
| 0,500/0,501 | 0,010 | 5 | 5 | 10 |
| 0,500/0,501 | 0,020 | 8 | 6 | 14 |
| 0,500/0,501 | 0,030 | 11 | 7 | 18 |
| 0,500/0,501 | 0,050 | 20 | 11 | 31 |

Essas contagens não aprovam R2 porque usam um escore ainda não validado. Elas
apenas indicam que 0,400 tem escala mais promissora e que 0,500 deve ser tratado
como replicação potencial, não segundo estudo principal automático.

A janela principal será escolhida por regra de balanceamento de covariadas
pré-tratamento, sem consultar outcomes. O RDD só poderá ser manchete se houver
suporte em vários mass points dos dois lados e potência para um efeito
substantivamente relevante. Tamanho de amostra será acompanhado pelo MDE; não
será inflado contando repetidamente vagas do mesmo município como atribuições
independentes.

### Cointervenções

Construir `output/rdd_bolsa/matriz_cointervencoes_municipio_curso.csv` com, no
mínimo:

- número e modalidade das vagas PMM-E;
- composição de cursos;
- estoque CNES e infraestrutura prévia;
- exposição observável a OCI, componente cirúrgico, SUS Digital, radioterapia,
  prestação complementar, unidades móveis e mutirões;
- regra de ajuda de custo ou benefício adicional.

Se outro componente também saltar no mesmo cutoff, o estimando deve ser chamado
de **efeito do pacote no limiar**. Ele não será apresentado como efeito isolado
da bolsa.

## 5. R3 — protocolo congelado

Antes de estimar, registrar em
`output/rdd_bolsa/registro_pre_analise.json`:

- hashes de todas as entradas e da matriz analítica sem outcomes;
- cutoff e janela principal;
- população e unidade de atribuição municipal;
- estimando e tratamento;
- outcomes, horizontes e denominadores;
- estimadores e inferência;
- regras de exclusão, multiplicidade e missing;
- exposição a chamadas posteriores e demais componentes;
- linguagem máxima permitida.

Como resultados exploratórios antigos já existem no histórico, esta será uma
pré-especificação **prospectiva para o novo desenho**, não alegação de ausência
de conhecimento prévio sobre qualquer outcome do projeto.

## 6. R4 — outcomes administrativos

### Núcleo público executável

1. proporção municipal de células município–curso publicadas com alguma
   confirmação ou homologação;
2. indicador de ao menos uma atração administrativa no município;
3. número de células município–curso com atração, como outcome secundário;
4. modelo no nível da célula com agrupamento municipal, como robustez.

O denominador público é o conjunto versionado de **células publicadas**, não a
quantidade de vagas físicas. Cada município receberá o mesmo peso na análise
principal, porque o tratamento é municipal. Confirmação e homologação serão
mantidas separadas de início em atividade.

### Núcleo ampliado condicionado a dados administrativos

1. candidaturas válidas por oferta/vaga estável;
2. probabilidade de uma oferta receber ao menos uma candidatura;
3. aceite, homologação e entrada;
4. tempo até preenchimento e reocupação.

O núcleo ampliado depende do universo de inscrições e do log de eventos de
`A07-02`. Lista de publicados não equivale ao universo de candidatos.

### Inferência

- randomização local no nível municipal como principal, se R1/R2 a sustentarem;
- inferência por permutação preservando os mass points e a regra de atribuição;
- RDD local-linear com inclinações separadas e pesos triangulares como robustez;
- erros e intervalos compatíveis com atribuição municipal e running variable
  discreta;
- placebos em cutoffs sem mudança normativa, balanceamento e análise
  leave-one-mass-point-out;
- nenhuma seleção de janela por menor p-valor.

## 7. R5 — força de trabalho no CNES

Somente após R4 e com a interpretação do primeiro estágio preservada:

- outcome principal: mudança do estoque municipal do CBO correspondente;
- secundários: cobertura, entradas e saídas cadastrais;
- CNES ofertante: diagnóstico de localização;
- município: teste de oferta líquida local;
- região de saúde: descrição de redistribuição, não spillover causal automático.

A publicação da vaga em julho de 2025 não é início físico de atividade. O
horizonte deve respeitar alocação em setembro e início/homologação. A janela
curta até janeiro de 2026 será separada da janela contaminável por ciclo 2 e
pela mudança da grade de bolsa em 2026. Presença no CNES é cadastral e não
identifica bolsista sem ponte administrativa.

## 8. R6 — produção e resolutividade

SIH/SIA só entram se:

1. R1–R4 passarem;
2. houver ligação clínica pré-especificada entre curso e procedimento;
3. não houver salto simultâneo de outro componente do Agora Tem Especialistas;
4. os arquivos cobrirem pré e pós integralmente;
5. localização, quantidade e espera permanecerem outcomes distintos.

Nenhuma produtividade por médico, substituição geográfica, viagem, custo ou
QALY será imputado como observação. O primeiro resultado clínico candidato é
produção cirúrgica eletiva no SIH; resolutividade exige origem do paciente e
prestador, e não mede fila por si só.

## 9. Kill criteria e interpretação

| Portão | Falha material | Consequência |
|---|---|---|
| R1 | escore/regra não reproduzem a faixa | encerrar RDD |
| R2 | pouco suporte ou cointervenção descontínua | rebaixar a exploratório ou pacote |
| R3 | hashes/amostra/outcomes não congelados | não estimar |
| R4 | sem salto em procura/alocação | reportar efeito do incentivo sobre implantação; não IV |
| R5 | sem ponte PMM-E–CNES | estimar apenas oferta líquida municipal reduzida |
| R6 | primeiro estágio ou mapeamento clínico falha | não interpretar SIH/SIA como efeito do PMM-E |

Linguagem máxima se todos os portões passarem:

> Próximo ao cutoff administrativo e sob as hipóteses documentadas, a oferta de
> R$ 5 mil adicionais alterou/não alterou o outcome em X.

Nunca extrapolar automaticamente para todos os municípios, para o efeito total
do PMM-E ou para o Agora Tem Especialistas.

## 10. Ordem operacional imediata

1. Corrigir a documentação e retirar causalidade indevida da DDD existente.
2. Executar somente R1 com fontes públicas e arquivos já preservados.
3. Se R1 passar, executar R2 sem outcomes.
4. Congelar R3 e revisar o protocolo uma vez.
5. Estimar R4; só então decidir R5.
6. Manter R6 e o ciclo 3 fora da fila imediata.

O pedido administrativo não é pré-condição automática de R1: primeiro será
esgotada a reconstrução pública. Se ela falhar, a decisão externa será entre
encerrar o RDD ou enviar apenas os módulos estritamente necessários de A07
(`A07-02`, `A07-04` e, para dose recebida, `A07-05`).
