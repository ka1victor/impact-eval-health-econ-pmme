# R1–R2 — regra, running variable, suporte e cointervenções

Execute somente os portões R1 e R2 de
`docs/14_plano_implementacao_rdd_bolsa.md`.
Leia também integralmente
`docs/15_incentivos_ivs_provimento_duradouro.md`, que fixa a pergunta,
denominadores e linguagem permitida.

## Proibições

- Não abra outcomes de candidatura, alocação, homologação, CNES pós, SIH
  ou SIA.
- Não estime efeitos.
- Não use o arquivo local de IVS como regra administrativa por presunção.
- Não escolha cutoff ou janela por resultado.
- Não altere arquivos brutos.

## R1

1. Recupere em fonte oficial a vintagem, arquivo, precisão, arredondamento,
   categoria e cutoff efetivamente aplicados ao ciclo 1 de 2025.
2. Preserve fontes, URLs, datas, versões e hashes.
3. Construa uma linha por município–vigência com escore, categoria, faixa,
   valor anunciado e regra reproduzida.
4. Reconcilie com todas as células do quadro de 24/07/2025.
5. Classifique o portão como `APROVADO_SHARP`, `APROVADO_FUZZY` ou `REPROVADO`.

Se R1 falhar, pare e documente exatamente a lacuna. Não execute R2.

## R2, somente se R1 passar

1. Para `0,400/0,401` e `0,500/0,501`, reporte suporte municipal e mass points
   nas janelas 0,010, 0,020, 0,030 e 0,050.
2. Calcule concentração por UF, curso e município e MDE sem consultar outcomes
   pós-tratamento.
3. Audite descontinuidades em vagas, modalidade, curso, estoque e infraestrutura
   prévia.
4. Construa matriz das demais ações do Agora Tem Especialistas observáveis por
   município–curso–mês.
5. Decida se o contraste candidato isola bolsa, pacote ou nenhum estimando.

## Entregáveis

- `scripts/rdd_bolsa/01_auditar_regra_e_suporte.py`;
- `output/rdd_bolsa/matriz_municipio_regra_ivs.csv`;
- `output/rdd_bolsa/matriz_cointervencoes_municipio_curso.csv`;
- `output/rdd_bolsa/portao_regra_ivs.json`;
- `output/rdd_bolsa/portao_suporte.json`;
- `docs/auditorias/07_portao_rdd_bolsa.md`.

Valide esquemas, unicidade, cobertura, hashes, sintaxe, testes e
`git diff --check`. Faça commit próprio e não faça push.
