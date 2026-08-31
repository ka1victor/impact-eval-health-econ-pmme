# Avaliação de impacto do Mais Médicos Especialistas

Este repositório organiza uma avaliação do Programa Mais Médicos Especialistas
(PMM-E). A primeira versão foi reduzida a uma pergunta relevante e mensurável
com dados públicos:

> **A disponibilização de vagas do PMM-E para preenchimento imediato aumentou
> o número de especialistas nos municípios contemplados? Os novos médicos
> permaneceram pelo maior horizonte comum observado?**

Em linguagem curta: **vagas viram médicos — e eles permanecem?**

## Decisão atual

> **Resultado da execução de 30/08/2026:** comparação ajustada, não impacto
> causal. O portão de relevância falhou na amostra que identifica a DDD.

O painel principal será `município–curso–mês` para o ciclo 1, chamada 1. A
exposição é a existência inicial de ao menos uma vaga imediata para o curso no
município; a comparação é ter apenas cadastro de reserva no mesmo quadro.

O outcome primário é o número de especialistas distintos no município. Entradas,
saídas, saldo e presença seis meses depois da entrada serão mecanismos
secundários. A presença em doze meses está pré-especificada para quando a coorte
comum tiver seguimento maduro; para a coorte de entradas até 2026-01, isso exige
CNES até 2027-01.

A primeira versão usará o CNES mensal de junho de 2024 a julho de 2026:

- 2024-06 a 2025-06: pré-tratamento;
- 2025-07: transição;
- 2025-08 a 2026-07: trajetória pós disponível.

Foi executada uma DDD com efeitos fixos de município–curso, município–mês e
curso–mês, acompanhada por estudo de evento. O plano completo está em
[`docs/05_roadmap_execucao.md`](docs/05_roadmap_execucao.md), e a auditoria do
pipeline e dos resultados está em
[`docs/auditorias/04_auditoria_pipeline_agregado.md`](docs/auditorias/04_auditoria_pipeline_agregado.md).

## Interpretação correta

"Vaga imediata" e "cadastro de reserva" são o contraste empírico, não o tema do
trabalho. O estimando mede o efeito de disponibilizar inicialmente uma vaga para
preenchimento imediato, em vez de mantê-la apenas em reserva, entre
municípios–especialidades incluídos no mesmo processo.

Cadastro de reserva não é ausência permanente do programa e pode receber
exposição posterior. A classificação também não foi aleatória. A leitura causal
dependerá de relevância administrativa, suporte e tendências paralelas. Se os
diagnósticos falharem, o resultado será apresentado como comparação ajustada.

O estudo mede oferta médica cadastral total no município, não identifica
individualmente bolsistas e não demonstra, por si só, horas trabalhadas,
produção, redução de espera ou melhora de saúde.

## Estado dos dados e da evidência

- O quadro de oferta do ciclo 1 está preservado e auditado: 1.295 células
  CNES–curso, das quais 503 apenas imediatas, 782 apenas em reserva e 10 mistas.
- As 26 competências do CNES foram processadas, de 2024-06 a 2026-07, usando
  todos os estabelecimentos dos 368 municípios do quadro.
- O painel municipal deduplica `CO_PROFISSIONAL_SUS`; não soma a lista nominal,
  não presume 40 horas e censura margens sem seguimento.
- A ponte curso–CBO é operacional, não uma crosswalk oficial. Dez cursos sem
  CBO compartilhado formam a amostra confirmatória.
- No grão e na amostra da DDD, imediata versus reserva não prediz alocação:
  +2,79 p.p., erro-padrão 6,89 p.p., `p=0,6871`. O portão causal não foi
  aprovado.
- A diferença ajustada principal no estoque foi −0,446 especialista por
  município–curso (IC 95% [−0,934; 0,042]). Esse número não é interpretado
  como efeito causal.

O portão A06 continua válido para o desenho individual anterior, bloqueado por
dados administrativos. O plano agregado atual não exige vincular nominalmente
participantes do PMM-E ao CNES.

## Próxima avaliação prospectiva

O ciclo 1 permanece encerrado como comparação ajustada. A próxima tentativa
causal não reutilizará filtros ou estimadores para mudar esse resultado. Ela
congelará prospectivamente o ciclo 3 antes de observar seus outcomes:

- estudo principal: oferta imediata pura versus proposta não priorizada pura de
  anestesiologia sobre o estoque municipal de anestesiologistas aos seis e
  doze meses;
- desfecho clínico-chave condicional: cirurgias eletivas no SIH;
- generalização secundária: oncologia clínica e medicina intensiva, com efeitos
  separados; cirurgia geral/CBO 225225 apenas como sensibilidade;
- alternativa somente se o pré-período justificar: ecocardiografia no SIA;
- RDD do IVS preservado como estudo do adicional de bolsa, ainda bloqueado pela
  regra administrativa não reconstruída.

A Nota Técnica nº 59/2026 criou uma assinatura cadastral potencialmente
observável dos participantes no CNES. O C3-01 já corrigiu a ponte do Anexo I: os
únicos cursos com suporte comparativo e ponte integral sem sobreposição são 1,
12 e 24. O piloto C3-02 comprovou que o SIH é público e manejável (2,14 GiB para
25 competências/24 UFs), mas a revisão encontrou falhas de proveniência,
fluxos interestaduais, classificação municipal e SIGTAP. A próxima sessão é o
C3-02B corretivo, não uma estimação.

A estratégia e seus limites estão em
[`docs/12_estrategia_causal_prospectiva_ciclo3.md`](docs/12_estrategia_causal_prospectiva_ciclo3.md).
Os prompts ordenados para sessões futuras estão em
[`prompts/avaliacao_ciclo3/`](prompts/avaliacao_ciclo3/README.md). Nenhum efeito
do ciclo 3 foi estimado e o protocolo C3-03 ainda não está validamente
congelado.

## Escopo da primeira versão

Entram: ciclo 1; estoque municipal de especialistas; entradas, saídas, saldo e
presença seis meses depois; diagnósticos de remanejamento; DDD e estudo de
evento.

Permanecem congelados **nesta primeira versão**: ciclos 2 e 3 como novas
coortes; RDD pelo IVS; efeito causal dos valores de bolsa; métodos sintéticos;
FTE; SIA/SUS; SIH/SUS; filas; outcomes de saúde; custos; identificação
individual de bolsistas; e envio dos pedidos administrativos A07. A preparação
prospectiva separada do ciclo 3 segue os próprios portões e não altera o
resultado desta versão.

## Executar o estado validado

```bash
python run_all.py
```

O comando exige que os 26 arquivos mensais listados no manifesto CNES já
estejam disponíveis localmente. Ele reproduz a integração, os portões, a
comparação ajustada, tabelas, figuras e nota técnica. Novas rotinas entram no
pipeline somente depois de passarem pelos portões de esquema, cobertura e
coerência substantiva.

## Estrutura

```text
data/      bases observadas preservadas
docs/      decisões, auditorias e plano empírico
prompts/   tarefas históricas e orientação da fila vigente
scripts/   rotinas reprodutíveis
output/    produtos gerados e validados
```
