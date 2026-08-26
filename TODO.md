# TODO.md — Fila após a auditoria lógica do PMM-E

## Concluído nesta etapa

- [x] Reorganizar a narrativa em problema → métricas → estado da evidência.
- [x] Separar registros observados, estimativas, cenários parametrizados e hipóteses.
- [x] Auditar as inferências de cada eixo sem redesenhar prematuramente o estudo.
- [x] Registrar que o pipeline atual não sustenta vereditos causais sobre sucesso ou fracasso.

## Dados necessários antes de reestimar

- [ ] Obter o universo de vagas ofertadas por município, estabelecimento, especialidade, chamamento e faixa de bolsa.
- [ ] Obter candidaturas/classificação, aceite, entrada efetiva e desligamento em nível profissional-vaga.
- [ ] Vincular CNES mensal para medir carga horária observada e possível substituição de vínculos preexistentes.
- [ ] Incorporar microdados origem-destino do SIA e do SIH com competência, procedimento e caráter de internação; não usar incrementos de produção presumidos.
- [ ] Obter dados de solicitação e atendimento em regulação, ou construir e validar uma proxy temporal antes de falar em fila.
- [ ] Obter custos observados de transporte sanitário, distância, ocupação, frequência e fonte pagadora.
- [ ] Documentar a origem reproduzível dos dados de OCI e teleconsulta; retirar cifras fixadas manualmente da camada de resultados.

## Decisões de desenho para a próxima etapa

- [ ] Definir a unidade causal: vaga-especialidade, estabelecimento ou município.
- [ ] Verificar se o IVS determina apenas o valor da bolsa ou também a seleção/oferta de vagas.
- [ ] Decidir entre RDD sharp, fuzzy RDD, desenho de encorajamento ou outro contraste, conforme a regra institucional real.
- [ ] Restringir a amostra a unidades comparáveis e efetivamente expostas à regra de bolsa.
- [ ] Definir um estimando separado para cada elo: adesão, entrada líquida, capacidade, acesso, fila, clínica e custo.
- [ ] Pré-especificar desfechos primários, janelas, covariáveis, placebos, testes múltiplos e critérios de interpretação.
- [ ] Incluir análises de potência e intervalos de confiança; “não significativo” não será traduzido como “igual a zero”.

## Métricas ainda não avaliadas com dados observados adequados

- [ ] Taxa de preenchimento no primeiro chamamento.
- [ ] Retenção individual aos 6 e 12 meses.
- [ ] FTE especializado adicional líquido.
- [ ] Resolutividade local e global sem componentes simulados.
- [ ] Tempo de espera por consulta, exame e procedimento.
- [ ] Tempo entre diagnóstico e terapia.
- [ ] Estadiamento oncológico inicial.
- [ ] Composição eletiva/urgência e transferência no SIH.
- [ ] Transporte e horas de viagem efetivamente evitados.
- [ ] Razão benefício-custo com análise de sensibilidade e perspectiva fiscal explícita.
- [ ] Efeitos de transbordamento sobre polos regionais.

## Itens descritivos que podem ser mantidos

- [x] Contagem de 1.480 registros nominais ativos na referência de 12/08/2026.
- [x] Cobertura descritiva de 325 municípios e 518 estabelecimentos CNES.
- [x] Composição por curso, incluindo 384 registros em Anestesiologia.

Esses itens descrevem a implantação observada; não são efeitos do programa.
