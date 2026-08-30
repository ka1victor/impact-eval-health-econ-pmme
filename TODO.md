# Próximas etapas — vagas viram médicos?

> A única fila empírica autorizada é a do plano em
> `docs/05_roadmap_execucao.md`. Todos os artefatos e etapas encontram-se
> versionados e salvos no diretório `output/avaliacao_impacto/`.

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
  imediata gera exposição administrativa substantivamente distinta da reserva (`01_avaliar_portao_relevancia.py`: +19.17 p.p. em alocação, +9.78 p.p. em homologação).
- [x] Auditar a proveniência e validar a ponte candidata versionada entre os 16
  cursos do ciclo 1 e CBOs (`output/aquisicao/ponte_curso_cbo_oficial.json`).
- [x] Resolver sobreposições de CBO entre cursos antes de observar efeitos (especificação com CBOs unívocos na Tabela 2 e Tabela 4).
- [x] Agregar o tratamento para `município–curso` e quantificar a amostra que
  identifica a DDD dentro do município (152 municípios, 819 células município-curso).
- [x] Validar estabilidade mensal de `CO_PROFISSIONAL_SUS`, duplicidades e
  significado de ausência no CNES.
- [x] Parar a afirmação causal se relevância, suporte ou integridade longitudinal
  falharem (relevância e pré-tendências aprovadas: teste Wald F = 5.0188, p = 0.4136).

## Construção dos dados

- [x] Adquirir e validar as 26 competências CNES de 2024-06 a 2026-07 (`05_integrar_painel_analitico.py`).
- [x] Construir o painel `município–curso–mês` e deduplicar profissionais entre
  CNES do mesmo município (`painel_municipio_curso_mes.parquet`).
- [x] Construir o estoque mensal de especialistas (`especialistas_mst`).
- [x] Construir entradas com seis meses anteriores de ausência observada (`n_entradas`).
- [x] Construir saídas apenas quando houver três meses posteriores observados (`n_saidas`).
- [x] Construir saldo e a coorte madura de entrantes presentes seis meses depois (`permanencia_6m`).
- [x] Registrar como censuradas as observações sem horizonte suficiente (12 meses formalmente censurados).
- [x] Documentar novas ofertas aos controles durante o seguimento (22.38% de alocação em reservas documentados).

## Análise e entrega

- [x] Produzir tabela de construção, perdas, clusters e baseline por modalidade (`tabela1_estatisticas_descritivas_baseline.csv`).
- [x] Mostrar a trajetória mensal completa de 2024-06 a 2026-07 (`figura3_trajetoria_estoque_por_modalidade.png`).
- [x] Estimar a DDD estática do estoque e o estudo de evento (`tabela2_ddd_estatica_resultado_primario.csv` e `figura1_estudo_evento_ddd_dinamico.png`).
- [x] Aplicar a mesma lógica aos mecanismos maduros, sem condicionar a análise
  causal ao conjunto de entrantes (`tabela3_mecanismos_fluxos_e_retencao.csv` e `figura4_decomposicao_mecanismos_fluxos.png`).
- [x] Comparar resultados no CNES, município e região como diagnóstico de
  remanejamento (`tabela4_diagnosticos_robustez_e_redistribuicao.csv` e `figura2_diagnostico_redistribuicao.png`).
- [x] Auditar pré-tendências, suporte, perdas, clusters dominantes e exposições
  posteriores.
- [x] Entregar nota curta, classificando o resultado como causal somente se as
  hipóteses forem defensáveis (`03_nota_tecnica_avaliacao_impacto_pmme.md`).
- [x] Integrar scripts e produtos ao `run_all.py` somente depois da validação.

## Atualização prospectiva

- [ ] Acrescentar novas competências sem redefinir a janela da primeira versão.
- [ ] Estimar presença doze meses depois somente quando toda a coorte congelada
  possuir seguimento comum maduro, com extensão do CNES até 2027-01 para a
  coorte de entradas encerrada em 2026-01.

## Congelado

Não executar agora: ciclos 2–3 como novas coortes; RDD/IVS; efeito causal das
faixas de bolsa; métodos escalonados ou sintéticos; FTE; produção, filas,
outcomes clínicos e custos; identificação individual de bolsistas; pedidos
administrativos A07.
