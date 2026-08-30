# Avaliação de impacto do Mais Médicos Especialistas

Este repositório organiza uma avaliação do Programa Mais Médicos Especialistas
(PMM-E). A primeira versão foi reduzida a uma pergunta relevante e mensurável
com dados públicos:

> **A disponibilização de vagas do PMM-E para preenchimento imediato aumentou
> o número de especialistas nos municípios contemplados? Os novos médicos
> permaneceram pelo maior horizonte comum observado?**

Em linguagem curta: **vagas viram médicos — e eles permanecem?**

## Decisão atual

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

Será usada uma DDD com efeitos fixos de município–curso, município–mês e
curso–mês, acompanhada por estudo de evento. O plano completo e seus portões
estão em [`docs/05_roadmap_execucao.md`](docs/05_roadmap_execucao.md); a fila
operacional está em [`TODO.md`](TODO.md).

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

## Estado dos dados

- O quadro de oferta do ciclo 1 está preservado e auditado.
- A fonte contém 1.295 células CNES–curso: 503 apenas imediatas, 782 apenas em
  reserva e 10 com ambas as modalidades.
- Três competências piloto do CNES confirmam os campos necessários; o painel
  versionado completo ainda não foi validado.
- A ponte oficial `curso PMM-E → CBO(s)`, a relevância de imediata versus reserva
  e a estabilidade longitudinal dos identificadores são portões obrigatórios.
- Ainda não existe resultado de impacto validado.

O portão A06 continua válido para o desenho individual anterior, bloqueado por
dados administrativos. O plano agregado atual não exige vincular nominalmente
participantes do PMM-E ao CNES.

## Escopo da primeira versão

Entram: ciclo 1; estoque municipal de especialistas; entradas, saídas, saldo e
presença seis meses depois; diagnósticos de remanejamento; DDD e estudo de
evento.

Permanecem congelados: ciclos 2 e 3 como novas coortes; RDD pelo IVS; efeito
causal dos valores de bolsa; métodos sintéticos; FTE; SIA/SUS; SIH/SUS; filas;
outcomes de saúde; custos; identificação individual de bolsistas; e envio dos
pedidos administrativos A07.

## Executar o estado validado

```bash
python run_all.py
```

O comando reproduz apenas o estado incorporado e validado do repositório. Novas
rotinas entrarão no pipeline somente depois de passarem pelos portões de esquema,
cobertura e coerência substantiva.

## Estrutura

```text
data/      bases observadas preservadas
docs/      decisões, auditorias e plano empírico
prompts/   tarefas históricas e orientação da fila vigente
scripts/   rotinas reprodutíveis
output/    produtos gerados e validados
```
