# Regras de trabalho do projeto

## Orientação substantiva

- Organize toda análise pela cadeia: implementação → força de trabalho → capacidade → acesso → saúde → custos/bem-estar → equidade e spillovers.
- Comece pelo outcome e pelo estimando; só depois escolha método e base.
- A fila imediata é o portão de viabilidade do RDD do adicional de bolsa,
  documentado em `docs/14_plano_implementacao_rdd_bolsa.md`. O efeito candidato
  é o incentivo marginal de R$ 5 mil, não participação no PMM-E nem o efeito
  total do Agora Tem Especialistas. Não consulte outcomes antes de reconstruir
  a regra e congelar o protocolo.
- `docs/15_incentivos_ivs_provimento_duradouro.md` define a pergunta do artigo:
  salário anunciado é o instrumento candidato, IVS é gradiente territorial e
  oferta persistente no CNES não equivale a retenção individual.
- O ciclo 3 permanece prospectivo e congelado. Use seis meses apenas quando a
  competência `202703` estiver publicada, completa e madura; doze meses somente
  quando toda a coorte tiver seguimento comum.
- Não trate vínculo cadastrado, produção, acesso, espera e saúde como sinônimos.
- Não classifique um eixo inteiro como sucesso ou fracasso com base em uma única métrica intermediária.
- Separe expansão líquida de substituição, remanejamento, migração cadastral e
  deslocamento de pacientes. No plano vigente, CNES–mês mede o efeito direto;
  município–mês é o teste obrigatório de oferta líquida local.
- Não defina grupos causais comparando retrospectivamente casos que deram certo e errado; heterogeneidades devem usar condições pré-tratamento.

## Dados e proveniência

- Nunca altere arquivos observados em `data/`.
- Toda transformação deve ser produzida por script versionado e gravada em `output/`.
- Registre fonte, data de referência, cobertura, unidade, chaves, filtros e hash de cada entrada.
- Não grave dados simulados, parâmetros assumidos ou cenários como se fossem observações.
- Cenários contrafactuais ou testes sintéticos devem ficar explicitamente rotulados e separados dos resultados empíricos.

## Identificação causal

- O IVS 2010 do IPEA é a running variable canônica; não o substitua por IDHM ou PIB per capita sem justificativa econométrica explícita e autorização do autor.
- O uso de RDD depende de demonstrar a regra efetiva de elegibilidade/alocação, o cutoff, o primeiro estágio e a ausência de manipulação relevante.
- Se a implantação não gerar uma descontinuidade válida, escolha outro desenho coerente com a variação observada e registre a mudança de escopo.
- Reporte estimando, população, período, unidade, contraste, incerteza, diagnósticos e limitações.
- Diga se o contraste identifica participação no PMM-E, um pacote de regras ou apenas o incentivo marginal.
- Resultados descritivos devem ser chamados de descritivos; associações não devem receber linguagem causal.

## Execução

- `docs/05_roadmap_execucao.md` preserva a execução validada do ciclo 1.
  `docs/14_plano_implementacao_rdd_bolsa.md` e
  `prompts/avaliacao_rdd_bolsa/README.md` são a fila imediata. A fila do ciclo
  3 em `prompts/avaliacao_ciclo3/README.md` continua congelada até maturidade.
  `docs/03_plano_avaliacao_outcomes.md` é agenda ampla e não deve ser
  interpretado como fila imediata.
- Antes de iniciar uma tarefa, confirme a fila vigente em
  `docs/05_roadmap_execucao.md`. Os prompts históricos em `prompts/` não
  autorizam executar o desenho individual anterior.
- WP3, WP4 e WP5 continuam guardados conforme
  `docs/06_backlog_wp3_wp4_wp5.md`. SIH/SIA só entram depois dos portões R1–R5
  do novo plano; não use produção clínica para procurar um resultado antes de
  validar a fonte de exogeneidade.
- A primeira versão agregada do ciclo 1 já foi executada. Não a reexecute nem
  redesenhe: relevância, ponte curso–CBO, painel CNES, estoque, mecanismos, DDD
  e estudo de evento permanecem como registro encerrado. A única execução
  imediata autorizada é R1 e, condicionalmente, R2 da fila RDD.
- A execução agregada de 30/08/2026 terminou como comparação ajustada: o
  portão de relevância falhou na amostra município–curso da DDD. Não promover
  esses resultados a efeito causal nem escolher filtros, janelas ou estimadores
  retrospectivamente para mudar essa conclusão.
- O C3-03 de força de trabalho depende do CNES pré validado, não do SIH. O
  C3-02B completo é portão somente para o submódulo clínico. Nos prompts
  C3-01 a C3-04, não consulte outcomes pós-tratamento. Nos prompts
  C3-05 e C3-06, não reescolha amostra, outcome ou estimador depois de observar
  resultados.
- Em 31/08/2026, C3-02B ficou em 673/675 porque `RDAC2606.dbc` e
  `RDRR2606.dbc` estavam ausentes do FTP oficial. Não trate essas ausências como
  zeros. Cirurgias e resolutividade permanecem bloqueadas até 675 sucessos;
  o protocolo CNES C3-03 foi congelado em 31/08/2026.
- Os pares de tarefas 01–02 e 04–05 só podem rodar em paralelo em worktrees isolados.
- Cada agente deve produzir commit próprio e não fazer push ou merge, salvo instrução explícita do autor.
- `run_all.py` é o ponto de entrada ponta a ponta do estado validado do projeto.
- Scripts usam caminhos relativos à raiz e devem ser determinísticos.
- Uma etapa só entra no pipeline após passar validações de esquema, cobertura e coerência substantiva.
- Resultados antigos no histórico do Git não são evidência vigente. A documentação corrente é a referência para o estado do projeto.
