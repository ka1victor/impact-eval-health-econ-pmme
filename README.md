# Avaliação do Mais Médicos Especialistas

Este repositório organiza uma avaliação do Programa Mais Médicos Especialistas
(PMM-E). A comparação pública já executada e o novo desenho causal são
deliberadamente separados.

Há três camadas separadas no repositório:

1. **Tema principal com entrega garantida:** quais características territoriais
   e das vagas estão associadas à atração administrativa e à persistência da
   oferta médica local fora das capitais?
2. **Upgrade causal:** R$ 5 mil adicionais de bolsa aumentam a
   procura e o preenchimento das vagas junto aos limiares administrativos do
   IVS?
3. **Diagnóstico já executado:** vagas inicialmente imediatas apresentaram
   trajetória de estoque CNES diferente das inicialmente mantidas em reserva?

## Decisão atual

> **Resultado vigente:** o tema é viável como econometria associativa de
> implementação. Imediata versus reserva continua sendo comparação ajustada,
> e o RDD do adicional da bolsa continua bloqueado até a reconstrução da regra.

O plano rápido está em
[`docs/14_plano_implementacao_rdd_bolsa.md`](docs/14_plano_implementacao_rdd_bolsa.md).
O tema, os outcomes e o veredito de viabilidade estão em
[`docs/15_incentivos_ivs_provimento_duradouro.md`](docs/15_incentivos_ivs_provimento_duradouro.md).
Uma auditoria reproduzível confirmou 350 municípios fora das capitais, 593 das
678 vagas imediatas nesse grupo e 26 competências CNES. Também encontrou que
211 das 468 confirmações públicas pertencem a células originalmente apenas de
reserva; portanto, o denominador deve ser reconciliado antes de se falar em taxa
de preenchimento. As sessões do núcleo estão organizadas em
[`prompts/avaliacao_atracao_interior/`](prompts/avaliacao_atracao_interior/README.md).
Ele pergunta se oferecer R$ 5 mil mensais adicionais alterou procura e
preenchimento de vagas próximas a um cutoff administrativo do IVS. Em 2025, os
cutoffs candidatos são `0,400/0,401` e `0,500/0,501`; não existe salto em
`0,300` nessa grade.

O RDD ainda não tem amostra estimável aprovada: primeiro é necessário reproduzir
a faixa da bolsa com o escore administrativo exato. Se o portão passar, a
unidade primária será município–curso–chamada, preservando vagas imediatas como
denominador, e os outcomes serão procura e preenchimento. CNES, SIH e SIA são extensões
condicionais, não a primeira estimação.

O diagnóstico encerrado usa `município–curso–mês` no ciclo 1 e o CNES mensal de
junho de 2024 a julho de 2026:

- 2024-06 a 2025-06: pré-tratamento;
- 2025-07: transição;
- 2025-08 a 2026-07: trajetória pós disponível.

Nele foi executada uma DDD com efeitos fixos de município–curso, município–mês e
curso–mês, acompanhada por estudo de evento. O plano completo está em
[`docs/05_roadmap_execucao.md`](docs/05_roadmap_execucao.md), e a auditoria do
pipeline e dos resultados está em
[`docs/auditorias/04_auditoria_pipeline_agregado.md`](docs/auditorias/04_auditoria_pipeline_agregado.md).

## Interpretação correta do diagnóstico encerrado

"Vaga imediata" e "cadastro de reserva" são o contraste empírico, não o tema do
trabalho. O contraste mede a diferença ajustada após disponibilizar inicialmente
uma vaga para preenchimento imediato, em vez de mantê-la apenas em reserva,
entre municípios–especialidades incluídos no mesmo processo.

Cadastro de reserva não é ausência permanente do programa e pode receber
exposição posterior. A classificação também não foi aleatória. A leitura causal
exigiria relevância administrativa, suporte e tendências paralelas. O portão de
relevância falhou e o resultado foi encerrado como comparação ajustada.

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

## Avaliação prospectiva do ciclo 3

O ciclo 3 permanece uma replicação prospectiva, mas não é a fila imediata.
Nenhum efeito pode ser estimado antes da competência `202703` madura. O plano
congelado prevê:

- estudo principal: oferta imediata pura versus proposta não priorizada pura de
  anestesiologia sobre o estoque no CNES ofertante aos seis e doze meses, com
  estoque municipal como teste obrigatório de oferta líquida;
- desfecho clínico-chave condicional: cirurgias eletivas no SIH;
- generalização secundária: oncologia clínica e medicina intensiva, com efeitos
  separados; cirurgia geral/CBO 225225 apenas como sensibilidade;
- alternativa somente se o pré-período justificar: ecocardiografia no SIA;
- RDD do IVS preservado como estudo do adicional de bolsa, ainda bloqueado pela
  regra administrativa não reconstruída.

A Nota Técnica nº 59/2026 criou uma assinatura cadastral potencialmente
observável dos participantes no CNES. O C3-01 já corrigiu a ponte do Anexo I: os
únicos cursos com suporte comparativo e ponte integral sem sobreposição são 1,
12 e 24. O C3-02B tentou os 675 pares de 27 UFs × 25 competências: 673 foram
processados, mas `RDAC2606.dbc` e `RDRR2606.dbc` não existiam no FTP oficial em
31/08/2026. As 25 versões SIGTAP foram historicizadas. Conforme a regra
*fail-closed*, as ausências não viraram zeros e os painéis preliminares do
C3-02 não foram promovidos. Esse bloqueio foi separado do CNES: o C3-03 de
força de trabalho foi executado apenas com o pré e congelou o plano em
[`docs/13_plano_pre_analise_ciclo3.md`](docs/13_plano_pre_analise_ciclo3.md).
Anestesiologia ficou como associação ajustada: suporte aprovado, mas
equivalência e potência para um especialista insuficientes. C3-02B ainda deve
ser repetido quando os dois arquivos aparecerem, exclusivamente para liberar o
módulo clínico.

A estratégia e seus limites estão em
[`docs/12_estrategia_causal_prospectiva_ciclo3.md`](docs/12_estrategia_causal_prospectiva_ciclo3.md).
Os prompts ordenados para sessões futuras estão em
[`prompts/avaliacao_ciclo3/`](prompts/avaliacao_ciclo3/README.md). Nenhum efeito
do ciclo 3 foi estimado. Qualquer estimação aguarda a competência `202703`
madura e seguirá a especificação congelada, sem redesenho pelo resultado.

## Escopo e bloqueios

Entram agora duas auditorias sem nova estimação: A1 reconcilia o funil público e
R1 reconstrói a regra da bolsa. A2 pode começar somente depois de A1 e congela a
tipologia territorial sem outcomes. A DDD, o estoque, os fluxos e a presença em
seis meses permanecem como resultados fechados do diagnóstico anterior.

Permanecem congelados: estimação do ciclo 3 antes da maturidade; efeito da dose
recebida sem pagamentos; SIA/SUS, SIH/SUS, fila, saúde e custos antes dos
portões do RDD; identificação individual sem ponte; e envio dos pedidos A07.
Estão liberados A1, R1 e, condicionalmente, A2/R2. A3 deve congelar o protocolo
antes de A4. Métodos sintéticos não serão usados para reparar
retrospectivamente a DDD anterior.

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
