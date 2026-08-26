# Regras de trabalho do projeto

## Orientação substantiva

- Organize toda análise pela cadeia: implementação → força de trabalho → capacidade → acesso → saúde → custos/bem-estar → equidade e spillovers.
- Comece pelo outcome e pelo estimando; só depois escolha método e base.
- Não trate vínculo cadastrado, produção, acesso, espera e saúde como sinônimos.
- Não classifique um eixo inteiro como sucesso ou fracasso com base em uma única métrica intermediária.
- Separe expansão líquida de substituição, remanejamento, migração cadastral e deslocamento de pacientes.

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
- Resultados descritivos devem ser chamados de descritivos; associações não devem receber linguagem causal.

## Execução

- `run_all.py` é o ponto de entrada ponta a ponta do estado validado do projeto.
- Scripts usam caminhos relativos à raiz e devem ser determinísticos.
- Uma etapa só entra no pipeline após passar validações de esquema, cobertura e coerência substantiva.
- Resultados antigos no histórico do Git não são evidência vigente. A documentação corrente é a referência para o estado do projeto.
