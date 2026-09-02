# A2 — Construir e congelar a tipologia territorial

> **Executado em 02/09/2026 — corrigido (strict RM/RIDE):** `APROVADO_4_ESTRATOS` — 540/540 municípios A1
> classificados nos 4 estratos (25 capital, 101 metropolitano strict, 238 interior
> próximo, 176 remoto) com REGIC 2018 + RM/RIDE 2022 strict (apenas Metropolitana/Integrada/Administrativa Integrada; exclui Colar/Área/Entorno; AU 44 fora). Ver
> `docs/auditorias/09_tipologia_territorial.md`.

## Objetivo

Substituir o rótulo amplo “interior” por medidas territoriais observáveis e
anteriores ao PMM-E.

## Estrutura mínima

1. capital;
2. município não capital em arranjo/região metropolitana;
3. interior conectado a polo regional;
4. interior remoto.

Preservar também medidas contínuas quando disponíveis: população prévia,
centralidade, distância ou tempo até polo/capital, IVS 2010 e estoque médico
pré-oferta. O IVS 2010 permanece canônico; não o substituir por IDHM ou renda.

## Regras

- usar fontes oficiais ou uma rota reproduzível e versionada;
- congelar a classificação sem consultar alocação, homologação ou CNES pós;
- reportar missing, mudanças de código municipal e concentração por UF/curso;
- não inferir remoticidade apenas por ser não capital.

## Entregáveis

- `scripts/tema_trabalho/03_construir_tipologia_territorial.py`;
- `output/tema_trabalho/matriz_tipologia_territorial.parquet`;
- `output/tema_trabalho/manifesto_tipologia_territorial.json`;
- tabela de suporte por estrato territorial.

## Portão

Cobertura integral da população aprovada em A1 ou regra de missing congelada.
Se não for possível construir remoticidade, manter apenas “fora das capitais” e
retirar “interior remoto” das hipóteses.

