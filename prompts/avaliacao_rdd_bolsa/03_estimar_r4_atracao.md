# R4 — estimar o efeito local do adicional sobre a atração

Execute **somente o que o registro R3 fixou**. Nenhuma decisão do registro é
reaberta depois de ver resultado.

## Pré-condições

1. `output/rdd_bolsa/registro_pre_analise.json` existe, traz a autorização do
   autor e foi commitado **antes** desta sessão. Confira com `git log` que
   nenhum commit anterior ao registro contém resultado R4;
2. o controlador está em `R3_CONGELADO_R4_AUTORIZAVEL`;
3. o ambiente é o fixado (Python ≥ 3.12, `requirements.txt`) e a suíte passa.

## Execução

1. Rode o construtor de desfechos do R3 sobre as listas reais, sem alterar o
   código congelado. Se ele falhar nos dados reais, pare e registre; não
   improvise outro desfecho.
2. Escreva `scripts/rdd_bolsa/06_estimar_r4_atracao.py`, que lê o registro e
   aplica exatamente a especificação principal, as robustezes e os placebos
   declarados. O script recusa rodar se o hash da matriz sem outcomes divergir
   do registro.
3. Grave `output/rdd_bolsa/resultados_rdd_atracao.csv` e `.json`, com
   estimativa, erro-padrão, intervalo, `n` por lado, número de municípios,
   banda, unidade e MDE ao lado de cada estimativa.
4. Publique tudo, inclusive se nulo. Com MDE acima do limiar do registro, o
   texto diz que efeitos menores não seriam detectados.

## Interpretação

- O estimando é a intenção de tratar da **oferta anunciada** de R$ 5 mil, local
  aos cortes, condicional às vagas publicadas. Não é valor recebido,
  participação no PMM-E, efeito do IVS nem do Agora Tem Especialistas.
- Placebos não nulos em `0,200` ou `0,500` indicam efeito de categoria sem
  bolsa e rebaixam a leitura.
- Procura, alocação e homologação são estágios distintos; não some nem
  substitua um pelo outro.

## Documentação

- Auditoria nova em `docs/auditorias/`, com resultado, diagnósticos e limites.
- Notas datadas nos planos 14 e 16, no roadmap e no registro de mudanças.
- Artigos e banca só mudam com decisão do autor. Os trechos que hoje dizem que
  a RDD foi encerrada no R1 estão listados em
  [`../integracao_rodadas_outubro_2026/03_adendo_pendencias_fechamento.md`](../integracao_rodadas_outubro_2026/03_adendo_pendencias_fechamento.md).
- R5 (CNES pós) não começa nesta sessão.

Commit próprio, suíte verde e conferidores aprovando. Push e merge só com
autorização do autor.
