# Plano rápido de implementação — RDD do adicional de bolsa

> **Decisão em 31/08/2026:** este é o primeiro desenho a ser testado para uma
> nova afirmação causal. A comparação do ciclo 1 entre vaga imediata e cadastro
> de reserva permanece encerrada como associação ajustada. Nenhum resultado de
> efeito será consultado antes da aprovação dos portões abaixo.

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
- `APROVADO_FUZZY`: há exceções documentadas, mas o salto no valor recebido é
  forte e mensurável;
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

1. `alocados_confirmados / vagas_publicadas` por município–curso;
2. indicador de ao menos uma alocação confirmada;
3. `homologados / vagas_publicadas`, mantido separado de entrada em atividade.

O denominador será o quadro vigente da chamada, sem somar reapresentações.
Resultados serão agregados ou inferidos no nível municipal, porque o valor da
bolsa não varia entre cursos do mesmo município.

### Núcleo ampliado condicionado a dados administrativos

1. candidaturas válidas por vaga;
2. probabilidade de receber ao menos uma candidatura;
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
