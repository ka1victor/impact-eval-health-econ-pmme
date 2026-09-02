# A06 — Integração das aquisições e novo portão

## Pré-requisitos

Execute somente depois de incorporar os commits A01–A05, concluir o prompt A05R
com decisão `ENTRADAS APTAS PARA A06` e confirmar que os ZIPs CNES não
versionados estão disponíveis no workspace principal com os hashes do manifesto
A05. Leia a revisão e o saneamento pré-A06, todos os relatórios e manifestos da
pasta `output/aquisicao/`, além de `AGENTS.md`, `CLAUDE.md`, as auditorias 01–02
e o roadmap. Esta tarefa é sequencial e tem responsabilidade exclusiva pelas
atualizações compartilhadas.

## Missão

Integrar o que foi obtido sem construir resultados de impacto. Verifique hashes,
proveniência, cobertura, chaves, versões e coerência entre as cinco frentes.
Reavalie o portão que antes classificou o estudo como `aguardando dados`.

## Perguntas obrigatórias

1. Existe universo versionado e denominador de vagas?
2. Existe `id_vaga` estável entre retificações e reapresentações?
3. Existem eventos suficientes para spells e `cobertura_90/120/180`?
4. Existe chave pseudonimizada PMM-E–CNES?
5. O IVS, sua vintagem, precisão e cutoff aplicados estão observados por vaga?
6. A dose é faixa anunciada, valor devido ou valor pago?
7. O CNES permite baseline, vínculos simultâneos, FTE cadastral e infraestrutura?
8. Qual é a maior janela comum madura **antes de olhar efeitos**?
9. Qual contraste é identificável: participação, pacote ou incentivo marginal?

## Entregáveis

- `output/aquisicao/portao_integrado.json`;
- `output/aquisicao/matriz_variavel_fonte_final.json`;
- `docs/auditorias/03_portao_apos_aquisicao.md`;
- atualização mínima de `README.md`, `docs/06_execucao/05_roadmap_execucao.md` e
  `prompts/README.md` para refletir a decisão;
- lista fechada de lacunas que A07 deve converter em pedidos administrativos.

O JSON do portão deve registrar para cada requisito `passou`, `parcial`,
`falhou` ou `não aplicável`, com evidência e caminho da fonte. A decisão final é
uma entre `prosseguir para prompt 03`, `prosseguir com escopo reduzido`,
`aguardar dados administrativos` ou `parar`.

## Regras de parada

Sem identificador estável e eventos, não declare cobertura mensurável. Sem regra
e primeiro estágio, não libere RDD. Sem ponte ao CNES, não prometa capacidade
líquida individual. Não mude o outcome para aproveitar a disponibilidade e não
estime efeitos.

Valide hashes, schemas e pipeline, faça commit próprio e informe hash, decisão e
bloqueios; não faça push ou merge.
