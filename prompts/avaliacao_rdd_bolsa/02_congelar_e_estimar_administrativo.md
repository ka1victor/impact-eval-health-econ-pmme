# R3–R4 — congelar protocolo e estimar outcomes administrativos

Execute somente se `output/rdd_bolsa/portao_regra_ivs.json` e
`output/rdd_bolsa/portao_suporte.json` aprovarem explicitamente a continuação.

## R3

1. Leia integralmente os portões e o plano canônico.
   Inclua `docs/15_incentivos_ivs_provimento_duradouro.md` e preserve a
   distinção entre preenchimento, oferta local persistente e retenção individual.
2. Construa a matriz sem outcomes e preserve seu hash.
3. Registre cutoff, janela, unidade municipal, amostra, denominadores,
   estimando, estimadores, inferência, exclusões, multiplicidade, missing e
   linguagem máxima em `output/rdd_bolsa/registro_pre_analise.json`.
4. Valide que nenhum outcome foi usado para escolher essas decisões.

Se R3 não puder ser congelado, pare.

## R4

Outcomes públicos permitidos:

- alocações confirmadas por vaga publicada;
- indicador de ao menos uma alocação;
- homologações por vaga, separadas de entrada em atividade.

Use randomização local municipal como principal se autorizada pelo portão;
RDD local-linear é robustez. Preserve mass points, não trate vagas do mesmo
município como atribuições independentes e não selecione janela por p-valor.

O universo de candidaturas só entra se A07-02 tiver sido respondido e validado.
Valor efetivamente recebido só entra com A07-05. Não execute CNES pós, SIH,
SIA ou ciclo 3 neste prompt.

Entregue scripts, matrizes, resultados, testes de falsificação, nota de
interpretação e auditoria independente. Faça commit próprio e não faça push.
