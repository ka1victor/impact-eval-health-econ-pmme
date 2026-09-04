# Avaliação do Mais Médicos Especialistas

Este repositório organiza uma avaliação do Programa Mais Médicos Especialistas
(PMM-E). A comparação pública já executada e o novo desenho causal são
deliberadamente separados.

Há quatro camadas separadas no repositório:

1. **Resultado principal:** quais características territoriais estão associadas
   à atração administrativa no primeiro ciclo?
2. **Resultado causal principal:** ganhar marginalmente a vaga de primeira
   opção aumenta a homologação e a presença posterior do especialista naquele
   curso–CNES?
3. **Pergunta causal arquivada:** R$ 5 mil adicionais de bolsa aumentam a
   procura e o preenchimento junto aos limiares administrativos do IVS?
4. **Resultado secundário:** células município–curso com atração administrativa
   apresentaram evolução distinta da oferta médica cadastrada no CNES?

## Decisão atual

> **Resultado vigente:** o A8 é o núcleo causal do trabalho curto. Em 36 pares
> de candidatos de ampla concorrência, sem empates e separados por exatamente
> um ponto no cutoff da mesma primeira opção, ganhar a vaga elevou a
> homologação no mesmo curso–CNES em **63,9 p.p.** e a presença ativa posterior
> em **33,3 p.p.** A interpretação é causal local sob comparabilidade dos pares,
> com rigor moderado. A4 e A5 permanecem associativos.

A decisão consolidada, todos os achados e a sequência de avanço estão em
[`docs/05_identificacao/17_plano_causal_publico_cutoff_escore.md`](docs/05_identificacao/17_plano_causal_publico_cutoff_escore.md).
O estado efetivamente executado dos portões está em
[`docs/06_execucao/33_status_execucao_plano_causal.md`](docs/06_execucao/33_status_execucao_plano_causal.md):
A8 concluído, RDD-IVS arquivada e pedido administrativo cancelado sem envio.

O plano anterior do cutoff está preservado em
[`docs/05_identificacao/15_cutoff_selecao_atracao_retencao.md`](docs/05_identificacao/15_cutoff_selecao_atracao_retencao.md).
O plano territorial da bolsa está em
[`docs/05_identificacao/14_plano_implementacao_rdd_bolsa.md`](docs/05_identificacao/14_plano_implementacao_rdd_bolsa.md).
O tema, os outcomes e o veredito de viabilidade estão em
[`docs/01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md`](docs/01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md).
Uma auditoria reproduzível confirmou 350 municípios fora das capitais, 593 das
678 vagas imediatas nesse grupo e 26 competências CNES. Também encontrou que
211 das 468 confirmações públicas pertencem a células originalmente apenas de
reserva. A1 concluiu a reconciliação como `APROVADO_CELULA`: a análise usará
alguma confirmação/homologação por célula e não taxa de preenchimento por vaga.
A2 concluiu a tipologia como `APROVADO_4_ESTRATOS` (540/540 municípios A1 em
capital/metropolitano/interior próximo/remoto via REGIC 2018 + RM/RIDE 2022).
As sessões do núcleo estão organizadas em
[`prompts/avaliacao_atracao_interior/`](prompts/avaliacao_atracao_interior/README.md).
A RDD da bolsa foi avaliada e arquivada: o IVS público não reproduz a faixa
administrativa nem gera primeiro estágio estável em `0,400` ou `0,500`. O
arquivo público não será usado como running variable por conveniência, e o
trabalho atual não depende de obter outro escore.

O diagnóstico histórico imediata versus reserva usa `município–curso–mês` no ciclo 1 e o CNES mensal de
junho de 2024 a julho de 2026:

- 2024-06 a 2025-06: pré-tratamento;
- 2025-07: transição;
- 2025-08 a 2026-07: trajetória pós disponível.

Nele foi executada uma DDD com efeitos fixos de município–curso, município–mês e
curso–mês, acompanhada por estudo de evento. O plano completo está em
[`docs/06_execucao/05_roadmap_execucao.md`](docs/06_execucao/05_roadmap_execucao.md), e a auditoria do
pipeline e dos resultados está em
[`docs/auditorias/04_auditoria_pipeline_agregado.md`](docs/auditorias/04_auditoria_pipeline_agregado.md).

## Interpretação correta do diagnóstico histórico

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
- A4 é o resultado principal: atração em 30,3% das células; metropolitano
  +29,4pp versus interior remoto, preservado em confirmação (+28,5pp),
  homologação (+25,0pp) e unidade município–curso (+33,1pp).
- A5 usa como principal 587 células município–curso em 295 municípios, referência
  limpa 202506 e follow-up 202603. O estudo dinâmico encontra +0,50 profissional
  cadastrado em março de 2026 (EP 0,23), em linguagem estritamente associativa;
  a mediana é 1 e o máximo 211 no grupo com atração.
- A7 identifica 423 pares adjacentes de seleção em quatro publicações. O A8
  restringe o núcleo a 36 pares de 2025 em ampla concorrência, primeira opção,
  sem empate e com gap exato de um ponto. O efeito local condicional é +63,9
  p.p. em homologação e +33,3 p.p. em presença ativa no mesmo curso–CNES; o
  placebo abaixo é nulo e a replicação de 2026 tem direção consistente.
- No grão e na amostra da DDD, imediata versus reserva não prediz alocação:
  +2,79 p.p., erro-padrão 6,89 p.p., `p=0,6871`. O portão causal não foi
  aprovado.
- A antiga diferença imediata versus reserva de −0,446 especialista é mantida
  apenas como diagnóstico histórico de outro estimando, não como resultado
  principal do artigo.

O antigo portão A06 permanece apenas como registro do desenho individual
anterior. O A8 não depende de entrega administrativa e não persiste
identificadores pessoais nos artefatos analíticos.

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
[`docs/05_identificacao/13_plano_pre_analise_ciclo3.md`](docs/05_identificacao/13_plano_pre_analise_ciclo3.md).
Anestesiologia ficou como associação ajustada: suporte aprovado, mas
equivalência e potência para um especialista insuficientes. C3-02B ainda deve
ser repetido quando os dois arquivos aparecerem, exclusivamente para liberar o
módulo clínico.

A estratégia e seus limites estão em
[`docs/05_identificacao/12_estrategia_causal_prospectiva_ciclo3.md`](docs/05_identificacao/12_estrategia_causal_prospectiva_ciclo3.md).
Os prompts ordenados para sessões futuras estão em
[`prompts/avaliacao_ciclo3/`](prompts/avaliacao_ciclo3/README.md). Nenhum efeito
do ciclo 3 foi estimado. Qualquer estimação aguarda a competência `202703`
madura e seguirá a especificação congelada, sem redesenho pelo resultado.

## Escopo e bloqueios

O portão A1 foi concluído como `APROVADO_CELULA`; A2–A8 foram executados e
auditados. O A8 é o resultado causal principal. R1 não reproduziu a regra da
bolsa, portanto a RDD-IVS está arquivada. A DDD imediata versus reserva
permanece como diagnóstico histórico, separado da A4, da A5 e do A8.

Permanecem fora do núcleo: estimação do ciclo 3 antes da maturidade; efeito da
dose recebida sem pagamentos; SIA/SUS, SIH/SUS, fila, saúde e custos; retenção
contínua sem log de eventos; empates dependentes de UF/idade; e qualquer RDD do
IVS público sem primeiro estágio. Métodos sintéticos não serão usados para
reparar retrospectivamente a DDD anterior.

## Executar o estado validado

### Pipeline completo de replicação
```bash
python run_all.py
```
O comando exige que os 26 arquivos mensais listados no manifesto CNES já estejam disponíveis localmente. Ele reproduz a integração, a comparação histórica e as etapas A1–A8, incluindo tabelas, figuras, red team, cutoff estrito e manifestos.

### Suíte de testes automatizados (131 testes)
```bash
python run_tests.py
```
Executa a validação formal de integridade dos dados, invariantes de painel, pre-analysis conformity, estimadores LPM/Logit e rastreabilidade documental.

---

## Estrutura do Repositório

Cada diretório principal possui documentação autônoma orientando seu conteúdo, regras e padrões de reprodutibilidade:

| Diretório | Documentação | Função e Conteúdo |
|---|---|---|
| [`data/`](data/README.md) | [Guia de Dados](data/README.md) | Bases observadas brutas, editais e microdados preservados (leitura estrita) |
| [`docs/`](docs/README.md) | [Mapa Canônico](docs/README.md) | Pergunta, modelo microeconômico, literatura empírica, identificação e auditorias |
| [`output/`](output/README.md) | [Guia de Artefatos](output/README.md) | Painéis analíticos, estimativas, tabelas, figuras e manifestos reproduzíveis |
| [`prompts/`](prompts/README.md) | [Fila e Histórico](prompts/README.md) | Sessões executadas, cadernos de prompts e especificações de pesquisa |
| [`scripts/`](scripts/README.md) | [Guia de Scripts](scripts/README.md) | Rotinas modulares de aquisição, estimação, avaliação de impacto e utilitários |
| [`tests/`](tests/README.md) | [Guia de Testes](tests/README.md) | 131 testes automatizados garantindo integridade econométrica e invariantes |
