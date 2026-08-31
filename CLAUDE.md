# Regras de trabalho do projeto

## Orientação substantiva

- Organize toda análise pela cadeia: implementação → força de trabalho → capacidade → acesso → saúde → custos/bem-estar → equidade e spillovers.
- Comece pelo outcome e pelo estimando; só depois escolha método e base.
- No estudo prospectivo vigente do ciclo 3, use o estoque municipal de
  especialistas como outcome primário e entradas, saídas, saldo e presença
  posterior como mecanismos. Anestesiologia/SIH é módulo assistencial
  confirmatório condicional aos portões pré-tratamento. Use seis meses na
  primeira atualização e doze meses somente quando a coorte tiver seguimento
  completo.
- Não trate vínculo cadastrado, produção, acesso, espera e saúde como sinônimos.
- Não classifique um eixo inteiro como sucesso ou fracasso com base em uma única métrica intermediária.
- Separe expansão líquida de substituição, remanejamento, migração cadastral e
  deslocamento de pacientes. No plano vigente, o município–curso–mês é a
  unidade principal; CNES e região de saúde são diagnósticos de redistribuição.
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
  `docs/12_estrategia_causal_prospectiva_ciclo3.md` e
  `prompts/avaliacao_ciclo3/README.md` são a ordem canônica da próxima avaliação.
  `docs/03_plano_avaliacao_outcomes.md` é agenda ampla e não deve ser
  interpretado como fila imediata.
- Antes de iniciar uma tarefa, confirme a fila vigente em
  `docs/05_roadmap_execucao.md`. Os prompts históricos em `prompts/` não
  autorizam executar o desenho individual anterior.
- WP3, WP4 e WP5 continuam guardados conforme
  `docs/06_backlog_wp3_wp4_wp5.md`, exceto o módulo explícito e limitado de
  anestesiologia/SIH autorizado na fila C3. Não amplie essa exceção para fila,
  saúde, custos ou SIA sem o portão previsto.
- Na primeira versão, execute somente o plano agregado do ciclo 1: relevância
  de imediata versus reserva, ponte curso–CBO, painel CNES, estoque municipal,
  mecanismos maduros, DDD e estudo de evento. Demais WPs permanecem como
  agenda, salvo nova autorização expressa do autor.
- A execução agregada de 30/08/2026 terminou como comparação ajustada: o
  portão de relevância falhou na amostra município–curso da DDD. Não promover
  esses resultados a efeito causal nem escolher filtros, janelas ou estimadores
  retrospectivamente para mudar essa conclusão.
- Nos prompts C3-01 a C3-04, não consulte outcomes pós-tratamento. Nos prompts
  C3-05 e C3-06, não reescolha amostra, outcome ou estimador depois de observar
  resultados.
- Os pares de tarefas 01–02 e 04–05 só podem rodar em paralelo em worktrees isolados.
- Cada agente deve produzir commit próprio e não fazer push ou merge, salvo instrução explícita do autor.
- `run_all.py` é o ponto de entrada ponta a ponta do estado validado do projeto.
- Scripts usam caminhos relativos à raiz e devem ser determinísticos.
- Uma etapa só entra no pipeline após passar validações de esquema, cobertura e coerência substantiva.
- Resultados antigos no histórico do Git não são evidência vigente. A documentação corrente é a referência para o estado do projeto.
