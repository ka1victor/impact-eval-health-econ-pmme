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
- **Potência (emenda 03/09/2026):** 3,8pp é somente benchmark de precisão de uma proporção e não o MDE dos coeficientes territoriais. Para os contrastes estimados contra interior remoto, os MDEs aproximados a 80% sob p=0,30 são 19,5pp (capital), 13,7pp (metropolitano) e 11,9pp (interior próximo). A conclusão de potência deve usar estes contrastes; a mínima relevante permanece 10pp (sensibilidade 5pp).
- **Tipologia:** A2 `APROVADO_4_ESTRATOS` strict — 540/540 (25/101/238/176) e quadro Ch1 368 (18/72/203/75); REGIC 2018 + RM/RIDE 2022 strict.
- **Hashes:** 7 entradas (inclui REGIC/RM xlsx) + 2 artefatos A1/A2 verificados; DEFF floor e join quadro↔tipologia auditados.

## 2. Portão para A4

A4 liberado apenas com este registro assinado por hash. Qualquer desvio deve ser emendado e datado; não redefinir população/outcome após ver resultados.
