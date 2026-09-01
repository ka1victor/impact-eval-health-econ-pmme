# A1 — Reconciliar o funil administrativo do ciclo 1

> **Executado em 01/09/2026:** `APROVADO_CELULA`. O denominador por vaga foi
> reprovado; o outcome liberado é alguma confirmação/homologação observada na
> célula. Ver `docs/auditorias/08_portao_denominador_atracao.md`.

## Objetivo

Construir a população e o denominador antes de qualquer estimação. Explicar por
que 211 das 468 confirmações aparecem em células originalmente apenas de
reserva, por que dez células imediatas excedem a capacidade publicada e por que
vinte homologações não fecham diretamente com o quadro inicial.

## Entradas mínimas

- quadro original de vagas do ciclo 1, chamada 1;
- alocação retificada e sub judice;
- quadro de realocação;
- homologados da chamada 1;
- vagas, alocados, classificação e homologados da chamada 2;
- manifestos e hashes já preservados em `output/aquisicao/`.

## Procedimento

1. Construir chaves `ciclo–chamada–versão–município–CNES–curso`.
2. Manter separadas quantidade imediata, quantidade de reserva, candidato
   classificado, local confirmado, realocação e homologação.
3. Não somar reapresentações como novas vagas.
4. Produzir trilha de cada divergência, sem imputar vaga física individual.
5. Decidir entre denominador por vaga, outcome binário por célula ou apenas
   contagem administrativa.

## Entregáveis

- `scripts/tema_trabalho/02_reconciliar_funil_ciclo1.py`;
- `output/tema_trabalho/matriz_funil_ciclo1.parquet`;
- `output/tema_trabalho/portao_denominador.json`;
- `docs/auditorias/08_portao_denominador_atracao.md`;
- testes de contagem, unicidade e capacidade.

## Portão

`APROVADO_VAGA`, `APROVADO_CELULA` ou `REPROVADO`. Se apenas a célula for
aprovada, remover “taxa de preenchimento por vaga” do texto e usar “alguma
confirmação/homologação observada”.
