# Próximas etapas

> **Núcleo causal vigente: A8 — cutoff de escore de seleção.** O ciclo 1
> permanece como análise associativa de implementação: A4 é motivação
> descritiva do gradiente territorial e A5 é evidência associativa de apêndice.
> A RDD da bolsa pelo IVS está arquivada por ausência de primeiro estágio e o
> pedido administrativo foi cancelado sem envio. O ciclo 3 continua congelado
> até maturidade. Decisão canônica em
> `docs/05_identificacao/17_plano_causal_publico_cutoff_escore.md`; portões
> executados em `docs/06_execucao/33_status_execucao_plano_causal.md`.

## Fila imediata — tema de atração e provimento fora das capitais

- [x] Auditar se oferta, território, alocação, homologação e CNES sustentam o
  tema (`output/tema_trabalho/diagnostico_atracao_provimento_interior.json`).
- [x] Fixar a formulação defensável como atração administrativa e persistência
  da oferta médica local, não retenção individual do bolsista.
- [x] A1 — reconciliar as 468 confirmações, 316 homologações, realocações e
  versões com a oferta original; explicar as 211 confirmações em células de
  reserva e as dez células imediatas acima da capacidade publicada.
- [x] A1 — decidir formalmente entre denominador por vaga e outcome binário por
  célula (`prompts/avaliacao_atracao_interior/01_reconciliar_funil_ciclo1.md`).
- [x] A1 — portão `APROVADO_CELULA`: usar alguma confirmação/homologação por
  célula; não estimar taxa de preenchimento por vaga.
- [x] A2 — construir e congelar tipologia capital/metropolitano/interior
  próximo/interior remoto sem consultar outcomes — `APROVADO_4_ESTRATOS`
  (540/540 municípios A1 classificados; 25 capitais, 101 metropolitanos strict,
  238 interior próximo, 176 interior remoto; REGIC 2018 + RM/RIDE 2022 strict
  — RM/RIDE apenas Metropolitana/Integrada, exclui Colar/Área/Entorno; AU 44 fora).
- [x] A3 — congelar outcome binário por célula, FE curso+UF e cluster municipal. O valor global de 3,8pp foi reclassificado como benchmark de uma proporção; os MDEs dos contrastes contra interior remoto são 19,5pp (capital), 13,7pp (metropolitano) e 11,9pp (interior próximo).
- [x] A4 — estimar atração em 1.295 células/368 municípios: metropolitano +29,4pp versus interior remoto no LPM mínimo e +19,8pp no completo; resultado preservado em confirmação (+28,5pp), homologação (+25,0pp) e colapso município–curso (+33,1pp).
- [x] A5 — estimar a evolução do estoque cadastrado com referência limpa em 202506, follow-up 202603 e amostra confirmatória de 587 células/295 municípios. Estudo dinâmico com FE célula, curso–mês e UF–mês; resultado secundário associativo, sem linguagem de provimento causal ou retenção.
- [x] A6 — executar red team, matriz afirmação–evidência–limite, síntese e manifesto reproduzível.

## Trilha encerrada — RDD do adicional de bolsa

- [x] Retirar da camada editorial a linguagem causal não sustentada pela DDD.
- [x] Auditar a viabilidade de salário, IVS, preenchimento e provimento
  duradouro (`docs/01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md`).
- [x] Auditar o primeiro estágio entre IVS 2010 público e bolsa anunciada: sem
  salto estável em `0,400` e salto zero em `0,500` nas janelas principais;
  fuzzy RDD pública reprovada.
- [x] Consolidar achados, alternativas, linguagem e plano fail-closed em
  `docs/05_identificacao/16_sintese_achados_e_novo_plano_causal.md`.
- [x] Materializar R1 público em matriz municipal, relatório e JSON de decisão:
  191/368 faixas reproduzidas, 177 divergentes; R1 permanece reprovado.
- [x] Preparar a solicitação focal conjunta e a triagem automática de resposta,
  sem enviar pedido nem versionar futuros microdados administrativos.
- [x] Implementar o controlador fail-closed que bloqueia R2–R4 enquanto R1 não
  for aprovado e registra o estado executado do plano causal.
- [x] Antes de R3, reconciliar as 678 vagas imediatas com alocações e
  homologações no grão município–CNES–curso–chamada por meio de A1.
- [x] **Encerrar a trilha.** O pedido administrativo foi `CANCELADO_NAO_ENVIADO`
  e a RDD-IVS ficou `ARQUIVADO_SEM_PRIMEIRO_ESTAGIO`. R1 a R6 e a submissão dos
  pedidos deixam de ser fila: nenhum resultado do trabalho depende de resposta
  do Ministério. O pacote de solicitação e a triagem permanecem versionados,
  prontos, caso o autor decida retomar a pergunta da bolsa no futuro.

## Fila imediata — núcleo causal A8 (cutoff de escore)

- [x] A7 — auditar o cutoff de seleção como diagnóstico exploratório; o recorte
  amplo misturava empates e gaps maiores, o que motivou o A8.
- [x] A8-P0 — congelar protocolo, amostra, tratamento, outcomes, inferência e
  linguagem proibida, registrando que o protocolo é **retrospectivo**, pois o
  A7 já havia aberto os outcomes.
- [x] A8-P1/P2 — suporte e recorte estrito: 36 pares em 2025 (30 na chamada 1 e
  6 na chamada 2), ampla concorrência, primeira opção, gap de exatamente um
  ponto e exclusão de empates.
- [x] A8-P3 — estimar: +63,9 p.p. em homologação e +33,3 p.p. em presença ativa
  no mesmo curso–CNES.
- [x] A8-P4 — placebo abaixo do cutoff, sensibilidade de gap e leave-one-out
  sem inversão de sinal.
- [x] A8-P5 — replicação de 2026: 11 pares, +36,4 p.p., teste exato `p=0,125`;
  classificada como direcional e imprecisa.
- [x] A8-P6 — auditar proteção de dados, hashes de entrada e testes.
- [x] Redigir o trabalho curto em torno do A8, com A4 como motivação descritiva,
  A5 no apêndice associativo e RDD-IVS e DDD apenas como rotas descartadas
  (`paper_pmme_submission.tex`). Literatura e bibliografia incorporadas: 16
  referências, todas presentes nos documentos do repositório.
- [x] Instrumentar a conferência automática do artigo: 184 cifras mapeadas para
  arquivo-fonte e localizador em `A8_conferencia_numeros_artigo.csv`, com
  `10_conferir_numeros_artigo.py` integrado ao `run_all.py`.
- [ ] Compilar o `.tex` e revisar as provas. Não há compilador LaTeX no ambiente
  de execução; a validação feita foi estrutural (ambientes balanceados, colunas
  das tabelas, `\label`/`\ref` e existência das figuras).

## Fila imediata — correções pós-auditoria (plano congelado em 09/09/2026)

Plano e alvos numéricos em `docs/06_execucao/35_plano_correcoes_pos_auditoria.md`.
A implementação que divergir dos alvos é erro de implementação, não resultado novo.

- [x] C1 — A4: colapsar UF em macrorregião, como o protocolo A3 declara, em vez
  do balde único `RESTO`. Capital vai de +0,2318 para +0,3264; metropolitano de
  +0,2942 para +0,2793. Publicar as três variantes como sensibilidade.
- [x] C2 — A5: promover a escala proporcional (`log1p`, +0,0684, `p=0,0002`) a
  forma primária, publicar leave-one-curso-out do coeficiente de evento e a
  sensibilidade de mês de referência, e corrigir os graus de liberdade que
  ignoram os FE absorvidos (`p` de 0,033 para 0,044).
- [x] C3 — refazer a justificativa do pedido do escore administrativo de IVS em
  torno da impossibilidade demonstrada (teto de 78,0% para qualquer regra de dois
  cortes) e do primeiro estágio sharp (527/527). Sem envio.

## Fila pós-auditoria — 23 itens em `docs/06_execucao/36_backlog_pos_auditoria.md`

Agrupados por consequência, com alvo numérico medido antes de qualquer alteração.
A ordem de execução do backlog é **normativa**, com estado por sessão e protocolo
de início e encerramento. Comece pela primeira sessão `ABERTA` e não pule adiante.

> **Próxima sessão: 1 — item A-1.** Balde `RESTO` nos modelos secundários de A5:
> `delta_minimal` vai de `+1,2949` (EP 0,7749) para `+0,5014` (EP 0,2508) em
> macrorregião, ou `+0,5002` sem colapso. O estudo de evento, que é a manchete de
> A5, **não** é afetado — absorve `sg_uf` direto. Nenhum desses números aparece no
> artigo. Por ser Grupo A, exige emenda escrita e commitada antes de implementar.

- [ ] Grupo A — muda número publicado (3 itens): balde `RESTO` nos modelos
  secundários de A5 (`+1,2949` → `+0,5014`); wild cluster bootstrap que o A3 exige
  e nunca foi computado; efeito marginal médio do logit com contrafactual
  impossível. Cada um exige emenda escrita e commitada antes de implementar.
- [ ] Grupo B — muda artefato, não muda número publicado (7 itens): censura gravada
  como zero em `presentes_6m`; relatório de A5 que é código morto; manifesto de
  reprodução de A6 que não reproduz; nota aritmética errada na tipologia;
  multiplicidade nunca tratada; rótulos enganosos; `sg_uf` de tipo misto.
- [ ] Grupo C — documentação e linguagem (9 itens): o 30,3% é da primeira chamada
  e não do ciclo; afirmação falsa sobre sub judice; IC fora do espaço de
  parâmetros; portão de A1 apresentado como teste; MDE por estrato com fórmula de
  proporção única; MDE ex-ante otimista; quatro ameaças ausentes do red team;
  assinatura de CPF não comparável; dois estimadores idênticos apresentados como
  duas evidências.
- [ ] Grupo D — bloqueado (4 itens): compilação do artigo, sem TeX no ambiente;
  ciclo 3 aguardando `RDAC2606`/`RDRR2606`, competência `202703` e `T0+12m`; envio
  do pedido do escore de IVS, que é decisão do autor; microdados do CNES ausentes
  do repositório.

## Decisões concluídas

- [x] Fixar o ciclo 1, chamada 1, como coorte inicial.
- [x] Usar vaga imediata versus apenas cadastro de reserva como contraste, não
  como pergunta substantiva.
- [x] Formular a pergunta principal como gradiente territorial da atração administrativa.
- [x] Definir célula CNES–curso como unidade principal de A4 e `município–curso–mês` como unidade secundária de A5.
- [x] Definir atração binária como outcome primário e estoque cadastrado como outcome secundário.
- [x] Usar todo o pós maduro e pré-especificar presença em 6 e 12 meses.
- [x] Manter RDD, efeito causal da bolsa e métodos sintéticos fora da primeira
  versão.

## Portões obrigatórios

- [x] Verificar, com alocações e homologações públicas, se a classificação
  imediata gera exposição administrativa substantivamente distinta da reserva.
  O portão **falhou na amostra identificadora**: +2,79 p.p., EP 6,89 p.p.,
  `p=0,6871`. Os +19,17 p.p. brutos no universo CNES–curso não substituem esse
  teste.
- [x] Auditar a proveniência e congelar a ponte operacional entre os 16 cursos
  do ciclo 1 e CBOs. Ela não é uma crosswalk oficial, apesar do nome histórico
  `output/aquisicao/ponte_curso_cbo_oficial.json`.
- [x] Resolver sobreposições de CBO entre cursos antes de observar efeitos (especificação com CBOs unívocos na Tabela 2 e Tabela 4).
- [x] Agregar o tratamento para `município–curso` e quantificar a amostra que
  identifica a DDD dentro do município (1.184 células em 368 municípios; 319
  células em 93 municípios no portão confirmatório).
- [x] Quantificar continuidade mensal de `CO_PROFISSIONAL_SUS`, remover
  duplicidades intramunicipais e distinguir zero de censura. A continuidade
  observada não substitui documentação externa da chave.
- [x] Parar a afirmação causal se relevância, suporte ou integridade longitudinal
  falharem. A linguagem causal foi interrompida pela falha de relevância; o
  teste de pré-tendências foi `F=1,262`, `p=0,2546`.

## Construção dos dados

- [x] Adquirir e validar as 26 competências CNES de 2024-06 a 2026-07 (`05_integrar_painel_analitico.py`).
- [x] Construir o painel `município–curso–mês` e deduplicar profissionais entre
  CNES do mesmo município (`painel_municipio_curso_mes.parquet`).
- [x] Construir o estoque mensal de especialistas (`especialistas_mst`).
- [x] Construir entradas com seis meses anteriores de ausência observada (`n_entradas_6m`).
- [x] Construir saídas apenas quando houver três meses posteriores observados (`n_saidas_confirmadas_3m`).
- [x] Construir saldo e a coorte madura de entrantes presentes seis meses depois (`entrantes_presentes_6m`).
- [x] Registrar como censuradas as observações sem horizonte suficiente (12 meses formalmente censurados).
- [x] Documentar novas ofertas aos controles durante o seguimento (22.38% de alocação em reservas documentados).

## Análise e entrega

- [x] Produzir tabela de construção, perdas, clusters e baseline por modalidade (`tabela1_estatisticas_descritivas_baseline.csv`).
- [x] Mostrar a trajetória mensal completa de 2024-06 a 2026-07 (`figura3_trajetoria_estoque_por_modalidade.png`).
- [x] Estimar a DDD estática do estoque e o estudo de evento (`tabela2_ddd_estatica_resultado_primario.csv` e `figura1_estudo_evento_ddd_dinamico.png`).
- [x] Aplicar a mesma lógica aos mecanismos maduros, sem condicionar a análise
  causal ao conjunto de entrantes (`tabela3_mecanismos_fluxos_e_retencao.csv` e `figura4_decomposicao_mecanismos_fluxos.png`).
- [x] Comparar município completo e CNES ofertante como diagnóstico de local de
  alocação; manter a região apenas descritiva, sem estimativa causal de spillover
  (`tabela4_diagnosticos_robustez_e_redistribuicao.csv`).
- [x] Auditar pré-tendências, suporte, perdas, clusters dominantes e exposições
  posteriores.
- [x] Entregar nota curta com status **comparação ajustada**, pois o portão
  administrativo falhou (`03_nota_tecnica_avaliacao_impacto_pmme.md`).
- [x] Integrar os scripts A1–A6 e seus produtos ao `run_all.py` depois da validação.

## Atualização prospectiva e infraestrutura paralela

- [ ] Acrescentar novas competências sem redefinir a janela da primeira versão.
- [ ] Estimar presença doze meses depois somente quando toda a coorte congelada
  possuir seguimento comum maduro, com extensão do CNES até 2027-01 para a
  coorte de entradas encerrada em 2026-01.
- [x] Construir módulo utilitário DBC -> Parquet do DATASUS, começando por um
  benchmark SIH e medindo separadamente tráfego, pico temporário e espaço
  persistente (`scripts/utils/datasus_dbc.py`).

## Ciclo 3 prospectivo

- [x] C3-01 — congelar coorte, exposição e ponte; correção independente fixou
  como núcleo integral somente os cursos 1, 12 e 24
  (`output/avaliacao_ciclo3/coorte_c3_congelada.parquet`,
  `docs/auditorias/05_coorte_c3_e_exposicao.md`).
- [x] C3-02 — executar piloto técnico SIH pré-tratamento para anestesiologia;
  viabilidade confirmada, mas painel ainda não liberado como insumo causal
  (`docs/auditorias/06_piloto_sih_anestesiologia.md`).
- [ ] C3-02B — tentativa de 31/08/2026 persistiu 675 manifestos e historicizou
  25 SIGTAP, mas ficou bloqueada em 673 sucessos: `RDAC2606.dbc` e
  `RDRR2606.dbc` não estavam no FTP oficial. Repetir só após ambos aparecerem;
  não imputar zeros (`prompts/avaliacao_ciclo3/02b_corrigir_e_validar_sih_pre.md`).
- [x] C3-03 — separar portões e executar o torneio de força de trabalho com 26
  competências CNES estritamente pré-T0. Protocolo congelado; anestesiologia
  classificada como `associacao_ajustada` (MDE 2,22 no CNES e 4,44 no
  município). Nenhum efeito foi estimado.
- [x] C3-04 — não acionar: SIA/ecocardiografia não venceu a rubrica nem
  substitui automaticamente o SIH incompleto.
- [ ] C3-05 — estimar a versão de seis meses apenas com seguimento comum maduro
  (aguardando competência CNES `202703` publicada e validada).
- [ ] C3-06 — atualizar a mesma análise aos doze meses, sem redesenho (aguardando T0+12m em setembro/2027).

## Congelado

Não executar agora: efeitos do ciclo 3 antes da maturidade; efeito da dose
recebida sem folha; fila, outcomes clínicos e custos; identificação individual
sem ponte; envio de A07. A RDD do IVS público não deve ser restaurada em
`0,300`, `0,400` ou `0,500` sem recuperar a regra administrativa. Heterogeneidades
do A8 por remoticidade, IVS, curso ou região são exploratórias e não podem virar
conclusão com 36 pares. Não inferir curva de sobrevivência a partir do snapshot,
pois isso seleciona sobreviventes. Synthetic DiD pode ser robustez
pré-especificada, nunca reparo retrospectivo de pré-tendências.
