# R3 — decisões do autor e congelamento do protocolo

Esta sessão **não estima nada e não abre outcome**. Ela termina com
`output/rdd_bolsa/registro_pre_analise.json` gravado por script versionado e
commitado. R4 é outra sessão, com outro prompt
([`03_estimar_r4_atracao.md`](03_estimar_r4_atracao.md)).

## Pré-condições

Pare se qualquer uma faltar:

1. a revisão de
   [`../integracao_rodadas_outubro_2026/01_revisar_rdd_ivs_administrativo.md`](../integracao_rodadas_outubro_2026/01_revisar_rdd_ivs_administrativo.md)
   foi feita e não deixou nada `BLOQUEADO`;
2. `output/rdd_bolsa/a01c_regra_ivs_administrativo.json` diz `APROVADO_SHARP`;
3. `output/rdd_bolsa/r2_portao.json` diz `VIAVEL_CONTINUIDADE` ou
   `VIAVEL_CONTINUIDADE_COM_RESSALVAS`;
4. o controlador `scripts/rdd_bolsa/02_controlar_execucao_plano_causal.py`
   está em `R1_R2_EXECUTADOS_AGUARDANDO_R3`;
5. `output/rdd_bolsa/registro_pre_analise.json` **não** existe.

Leia antes: `CLAUDE.md`, o plano 14, a auditoria 15 e o rascunho 18
([`docs/05_identificacao/18_protocolo_r3_rdd_bolsa_rascunho.md`](../../docs/05_identificacao/18_protocolo_r3_rdd_bolsa_rascunho.md)).

## Ambiente

Python ≥ 3.12 com as versões de `requirements.txt`. No container da nuvem há
`python3.12` e `uv`:

```bash
uv venv --python 3.12 .venv && VIRTUAL_ENV=.venv uv pip install -r requirements.txt
.venv/bin/python run_tests.py
```

## Passo 1 — decisões do autor

Pergunte tudo de uma vez, com a proposta do rascunho 18 como opção padrão.
Sem resposta do autor, **pare aqui** e registre as perguntas no relatório.

0. trocar a running variable canônica do IVS 2010 pelo IVS administrativo
   (o `CLAUDE.md` exige autorização explícita);
1. outcome primário;
2. outcomes secundários, incluindo procura (candidaturas por célula);
3. unidade principal: município–onda, célula ou município;
4. ondas incluídas. A do ciclo 3 só entra com autorização, porque o ciclo 3
   está congelado no `CLAUDE.md`; o resultado dele também é *sub judice*;
5. estimador principal e banda fixa;
6. bandas de robustez;
7. estimativa conjunta dos dois cortes e hipótese principal;
8. covariadas e exclusão de capitais em robustez;
9. inferência;
10. placebos;
11. limiar de MDE acima do qual a manchete vira exploratória;
12. linguagem máxima.

Registre as respostas, com data, em `docs/05_identificacao/18_...` e mude o
cabeçalho do documento de "rascunho" para "decidido em <data>".

## Passo 2 — dados que faltam, sem abrir valores

1. Adquira o resultado final da 1ª chamada do ciclo 2
   (`resultado-final-pmme-2o-ciclo-25-05.xlsx`, página do Chamamento SGTES/MS
   nº 1/2026) estendendo `scripts/aquisicao/a07_adquirir_ivs_administrativo.py`
   ou num `a08` próprio. Preserve em `data/raw/`, com URL, data e SHA-256 no
   manifesto.
2. Confira só a estrutura de cada lista de resultado: colunas, situações
   publicadas, número de linhas, chaves CNES–curso. **Não cruze com faixa nem
   com IVS.**

## Passo 3 — matriz analítica sem outcomes

Escreva `scripts/rdd_bolsa/05_congelar_registro_r3.py`, que:

- monta a matriz de análise (unidade escolhida × running variable × corte ×
  onda × covariadas) **sem nenhuma coluna de desfecho**, grava em
  `output/rdd_bolsa/` e registra o SHA-256;
- calcula o MDE da unidade escolhida pelo desenho local-linear, sem outcome,
  em dois extremos de correlação entre ondas do mesmo município (independentes
  e perfeitamente correlacionadas);
- contém o construtor de desfechos como função **testada só com dado
  sintético**. Ele não roda sobre as listas reais nesta sessão;
- grava `output/rdd_bolsa/registro_pre_analise.json` com: as decisões do passo
  1 e quem autorizou; hashes de todas as entradas, incluindo os brutos das
  listas de resultado; a matriz sem outcomes; o estimador, a inferência, a
  multiplicidade, os placebos, o MDE e a linguagem; e a declaração de
  conhecimento prévio (comparações por faixa de A4 e das conversas de 21/09 a
  05/10/2026).

## Passo 4 — portões e commit

1. Atualize `tests/test_r1_r2_ivs_administrativo.py`: o teste que exige a
   ausência do registro passa a exigir que ele traga a autorização do autor e
   que nenhum resultado R4 exista.
2. Rode o controlador. O estado esperado é `R3_CONGELADO_R4_AUTORIZAVEL`.
3. A suíte tem de passar, e os conferidores `10_` e `11_` têm de aprovar.
4. Atualize o roadmap e o registro de mudanças.
5. Faça um commit só do R3, com mensagem em português. Não estime nada. Push e
   merge só com autorização do autor.
