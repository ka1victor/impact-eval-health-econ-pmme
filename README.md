# Avaliação de impacto do Mais Médicos Especialistas

Este repositório organiza uma avaliação do Programa Mais Médicos Especialistas
(PMM-E). A primeira versão foi deliberadamente reduzida a uma pergunta que pode
ser enfrentada com dados públicos:

> Ser classificada inicialmente como **vaga imediata**, em vez de **apenas
> cadastro de reserva**, aumentou o número de especialistas cadastrados no
> estabelecimento contemplado?

## Decisão atual

O plano principal é um painel mensal `CNES–curso–mês` do ciclo 1, chamada 1. O
tratamento é a classificação publicada em 24/07/2025 e o outcome é o número de
profissionais distintos em CBOs elegíveis para o curso.

Na planilha oficial há 1.295 células: 503 apenas com vagas imediatas, 782 apenas
em reserva e 10 com as duas modalidades. Elas abrangem 460 estabelecimentos; em
165 deles existem cursos em modalidades distintas.

Será usada uma DDD com efeitos fixos de célula, CNES–mês e curso–mês. Como existe
uma única data de exposição na primeira versão, métodos para adoção escalonada
não são necessários agora. O período será junho de 2024 a julho de 2026, com
julho de 2025 excluído como transição.

O plano completo e seus limites estão em
[`docs/05_roadmap_execucao.md`](docs/05_roadmap_execucao.md). A fila fechada está
em [`TODO.md`](TODO.md).

## Interpretação correta

O contraste mede o efeito da **priorização imediata**, não o efeito de participar
do PMM-E versus não participar. Cadastro de reserva pode levar a alocação
posterior; por isso ele é uma condição de menor prioridade, não um grupo
permanentemente não tratado.

O outcome mede oferta médica cadastral líquida no estabelecimento. Não identifica
quais médicos são bolsistas, não mede retenção individual e não demonstra, por si
só, melhora de produção, espera ou saúde. A priorização também não foi aleatória:
a leitura causal dependerá de comparabilidade e tendências paralelas. Se os
diagnósticos falharem, o resultado será apresentado como comparação ajustada.

## Estado dos dados

- O quadro de oferta do ciclo 1 já está preservado e auditado.
- Três competências piloto do CNES confirmam a existência dos campos de
  profissional, CBO e carga horária.
- Ainda faltam a ponte oficial `curso PMM-E → CBO(s)` e as 23 competências CNES
  restantes para completar o painel de 26 meses.
- Ainda não há resultado de impacto estimado.

O portão A06 anterior continua válido para o antigo estimando de cobertura e
retenção individual, que permanece bloqueado por dados administrativos. O novo
estimando agregado não exige vincular nominalmente participantes do PMM-E ao
CNES.

## Escopo congelado

Não entram na primeira versão: ciclos 2 e 3; RDD pelo IVS; Callaway–Sant'Anna,
Sun–Abraham ou métodos sintéticos; FTE e rotatividade; mobilidade regional;
produção, filas, internações e outcomes de saúde; custos; heterogeneidades; envio
dos pedidos administrativos.

Os documentos `01` a `04` e `06` preservam a agenda mais ampla e o desenho
individual anterior, mas não constituem tarefas correntes.

## Executar o estado já validado

```bash
python run_all.py
```

No estado atual, o comando apenas reproduz inventários e auditorias existentes.
A nova estimação só será incorporada depois de a ponte curso–CBO e o painel
mensal serem construídos e validados.

## Estrutura

```text
data/      bases observadas preservadas
docs/      decisões, auditorias e plano empírico
prompts/   fila antiga, congelada até ser alinhada ao plano mínimo
scripts/   rotinas reprodutíveis
output/    produtos gerados
```
