# A3 — Congelar a pré-análise do núcleo associativo

> **Executado em 02/09/2026:** congelado — outcome binário por célula, unidade
> célula com cluster município, FE curso+UF, MDE global 3,8pp (p=0,30).
> Ver `docs/auditorias/10_pre_analise_atracao.md` e
> `output/tema_trabalho/registro_pre_analise_atracao.json`.

## Objetivo

Fixar pergunta, população, outcome, covariadas, estimadores e linguagem antes
de abrir as estimações finais.

## Decisões obrigatórias

- outcome primário conforme o estado de A1;
- unidade `município–curso–chamada` ou célula CNES–curso justificada;
- covariadas exclusivamente pré-oferta;
- curso e UF como efeitos fixos candidatos;
- inferência agrupada no município;
- mínima diferença substantivamente relevante e MDE;
- missing, outliers, pesos, multiplicidade e influência;
- separação explícita entre explicação associativa e previsão.

Modelos candidatos: binomial para contagem preenchida/denominador aprovado;
logit/LPM para alguma confirmação; Poisson/negativo binomial apenas para
contagens com exposição bem definida. Fractional logit é robustez quando a taxa
possuir denominador válido.

## Entregáveis

- `output/tema_trabalho/registro_pre_analise_atracao.json`;
- `output/tema_trabalho/potencia_atracao.json`;
- seção econométrica congelada no documento principal;
- hashes de entradas e da matriz sem outcomes finais.

## Portão

Não executar A4 sem outcome primário, denominador, unidade de inferência e
linguagem máxima aprovados.

