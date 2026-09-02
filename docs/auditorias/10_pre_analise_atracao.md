# A3 — Pré-análise congelada do núcleo associativo

> **Data:** 2 de setembro de 2026
> **Registro:** `output/tema_trabalho/registro_pre_analise_atracao.json`
> **Potência:** `output/tema_trabalho/potencia_atracao.json`
> **Seção congelada:** `docs/06_execucao/31_secao_econometrica_A3.md`

## 1. Decisões congeladas

- **Outcome primário:** binário por célula `1[alguma confirmação ou homologação observada]` (A1 `APROVADO_CELULA`); taxa por vaga permanece proibida.
- **População:** 1.295 células CNES–curso do quadro Ch1 (368 municípios) como primária; 3.057 células do funil A1 como estendida. 266 registros fora do quadro sem município excluídos.
- **Unidade de inferência:** município (`co_ibge_6d`), cluster-robusto; FE de curso (16) e UF (colapsar <5 clusters).
- **Covariadas:** exclusivamente pré-oferta — estrato A2, IVS 2010 canônico (+ subíndices), log(pop 2010), região de saúde, estoque pré 202407–202506, faixa anunciada, curso, UF, chamada.
- **Modelos:** LPM (primário) e logit/AME (alternativo); binomial por célula; Poisson/NB apenas descritivo.
- **Linguagem:** associativa (gradiente, associado a); proibido efeito causal do PMM-E/bolsa/IVS, taxa por vaga, retenção individual.
- **Potência:** MDE 80% global 3,8pp (p=0,30) a 4,1pp (p=0,50) com DEFF 1,13 (ICC 0,05, m≈3,5). Por estrato: próximo 4,8pp (bem potenciado), metropolitano 7,9pp, remoto 10,6pp, capital 15,7pp (limitado). Mínima relevante 10pp (sens. 5pp).

## 2. Portão para A4

A4 liberado apenas com este registro assinado por hash. Qualquer desvio deve ser emendado e datado; não redefinir população/outcome após ver resultados.
