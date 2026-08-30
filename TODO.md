# Próximas etapas — vagas viram médicos?

> A única fila empírica autorizada é a do plano em
> `docs/05_roadmap_execucao.md`. Artefatos não versionados não contam como etapas
> concluídas.

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

- [ ] Verificar, com alocações e homologações públicas, se a classificação
  imediata gera exposição administrativa substantivamente distinta da reserva.
- [ ] Auditar a proveniência e validar a ponte candidata versionada entre os 16
  cursos do ciclo 1 e CBOs; o nome `oficial` do arquivo não encerra o portão.
- [ ] Resolver sobreposições de CBO entre cursos antes de observar efeitos.
- [ ] Agregar o tratamento para `município–curso` e quantificar a amostra que
  identifica a DDD dentro do município.
- [ ] Validar estabilidade mensal de `CO_PROFISSIONAL_SUS`, duplicidades e
  significado de ausência no CNES.
- [ ] Parar a afirmação causal se relevância, suporte ou integridade longitudinal
  falharem.

## Construção dos dados

- [ ] Adquirir e validar as 26 competências CNES de 2024-06 a 2026-07.
- [ ] Construir o painel `município–curso–mês` e deduplicar profissionais entre
  CNES do mesmo município.
- [ ] Construir o estoque mensal de especialistas.
- [ ] Construir entradas com seis meses anteriores de ausência observada.
- [ ] Construir saídas apenas quando houver três meses posteriores observados.
- [ ] Construir saldo e a coorte madura de entrantes presentes seis meses depois.
- [ ] Registrar como censuradas as observações sem horizonte suficiente.
- [ ] Documentar novas ofertas aos controles durante o seguimento.

## Análise e entrega

- [ ] Produzir tabela de construção, perdas, clusters e baseline por modalidade.
- [ ] Mostrar a trajetória mensal completa de 2024-06 a 2026-07.
- [ ] Estimar a DDD estática do estoque e o estudo de evento.
- [ ] Aplicar a mesma lógica aos mecanismos maduros, sem condicionar a análise
  causal ao conjunto de entrantes.
- [ ] Comparar resultados no CNES, município e região como diagnóstico de
  remanejamento.
- [ ] Auditar pré-tendências, suporte, perdas, clusters dominantes e exposições
  posteriores.
- [ ] Entregar nota curta, classificando o resultado como causal somente se as
  hipóteses forem defensáveis.
- [ ] Integrar scripts e produtos ao `run_all.py` somente depois da validação.

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
