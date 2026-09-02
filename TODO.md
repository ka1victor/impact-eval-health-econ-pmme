# Próximas etapas

> O ciclo 1 foi concluído como comparação ajustada. O tema principal passa a
> ter um núcleo associativo com portões próprios e um upgrade causal pelo RDD.
> O ciclo 3 continua congelado até maturidade.

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
- [x] A3 — congelar outcome binário por célula, unidade célula com cluster município, covariadas pré-oferta, FE curso+UF, MDE global 3,8pp (p=0,30; DEFF 1,126) e por estrato quadro Ch1 strict 16,1% capital 73/18 / 8,4% metro 265/72 / 4,8% próximo 811/203 / 10,9% remoto 146/75 (DEFF floor, hashes território REGIC/RM), linguagem associativa (`registro_pre_analise_atracao.json` + `potencia_atracao.json` + `31_secao_econometrica_A3.md`).
- [x] A5 — avaliar persistência da oferta médica local no CNES agregado (painel T0 alinhado 30.784 linhas, 1184 células, 368 mun, horizonte comum 6m; modelos minimal e full FE curso+UF cluster município; LOO e influência municipal; validação preditiva GroupKFold; sem causalidade; 14 testes OK) (`scripts/tema_trabalho/06_avaliar_provimento_cnes.py` + `A5_estimativas_provimento.json` + `A5_relatorio_diagnostico.md` + 20 tabelas/figuras).
- [ ] A6 — executar red team e auditoria de sensibilidade sem chamar o resultado de retenção individual ou efeito total do PMM-E.

## Fila imediata — RDD do adicional de bolsa

- [x] Retirar da camada editorial a linguagem causal não sustentada pela DDD.
- [x] Auditar a viabilidade de salário, IVS, preenchimento e provimento
  duradouro (`docs/01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md`).
- [ ] R1 — recuperar a running variable administrativa exata, vintagem,
  precisão, arredondamento e cutoffs da grade de 2025.
- [ ] R1 — reproduzir 100% das faixas anunciadas ou documentar exceções
  normativas anteriores aos outcomes.
- [ ] R2 — medir suporte municipal, mass points, MDE e concentração sem abrir
  outcomes.
- [ ] R2 — construir matriz de cointervenções do Agora Tem Especialistas e
  decidir se o cutoff isola bolsa ou pacote.
- [ ] R3 — congelar amostra, cutoff, janela, outcomes, inferência e hashes.
- [x] Antes de R3, reconciliar as 678 vagas imediatas com alocações e
  homologações no grão município–CNES–curso–chamada por meio de A1.
- [ ] R4 — estimar procura/alocação somente se R1–R3 passarem.
- [ ] R5/R6 — manter CNES e SIH/SIA condicionados aos portões anteriores.

## Decisões concluídas

- [x] Fixar o ciclo 1, chamada 1, como coorte inicial.
- [x] Usar vaga imediata versus apenas cadastro de reserva como contraste, não
  como pergunta substantiva.
- [x] Formular a pergunta como efeito sobre oferta médica local e persistência.
- [x] Definir `município–curso–mês` como unidade principal.
- [x] Definir estoque municipal de especialistas como outcome primário.
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
- [x] Integrar scripts e produtos ao `run_all.py` somente depois da validação.

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

Não executar agora: efeitos do ciclo 3 antes da maturidade; R4–R6 antes de R1–R3;
efeito da dose recebida sem folha; fila, outcomes clínicos e custos antes do
primeiro estágio; identificação individual sem ponte; envio de A07. Synthetic
DiD pode ser robustez pré-especificada, nunca reparo retrospectivo de
pré-tendências.
