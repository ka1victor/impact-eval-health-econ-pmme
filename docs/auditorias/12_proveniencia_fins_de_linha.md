# Auditoria de proveniência — fins de linha e cadeia de hashes A3–A6

> **Data:** 2026-09-09. **Estado:** `CORRIGIDO_SEM_MUDANCA_SUBSTANTIVA`.
> **Escopo:** cinco artefatos a montante, três testes acusando, nenhum número
> substantivo alterado.

## 1. Sintoma

A suíte automatizada falhava em três testes de proveniência, todos exigindo que
o sha256 registrado por um artefato conferisse com o arquivo em disco:

- `test_estimativas_atracao_a4.py::test_hashes_entradas_conferem` (A4);
- `test_pre_analise_atracao.py::test_hashes_presentes` (A3);
- `test_red_team_a6.py::test_manifesto_reproducao_completo` (A6).

## 2. Causa raiz

Não houve mudança de conteúdo. Os hashes registrados são o sha256 dos **mesmos
arquivos com fins de linha CRLF**, enquanto o repositório canoniza LF:

| artefato | sha256 em LF | sha256 em CRLF |
|---|---|---|
| `manifesto_tipologia_territorial.json` | `eb3839b5…` | `81cf5637…` |
| `portao_denominador.json` | `0055baf7…` | `aabb0f3d…` |
| `potencia_atracao.json` | `91fa9055…` | `def99ef7…` |
| `suporte_estratos_territoriais.csv` | `4fc642a5…` | `8a998641…` |
| `ponte_curso_cbo_oficial.json` | `ed8c2a9a…` | `1770e076…` |

Os valores da coluna CRLF são exatamente os que estavam registrados. A
aritmética de bytes fecha e corrobora o diagnóstico de forma independente do
hash. O `A6_manifesto_reproducao.json` daquela execução registrava, para
`ponte_curso_cbo_oficial.json`, o par `sha256: 1770e076…` e `bytes: 16623`. Em
disco o arquivo tem 16.218 bytes em LF e 405 linhas, e 16.218 + 405 = 16.623: o
tamanho registrado é exatamente o da versão CRLF, em que cada quebra de linha
ocupa um byte a mais.

A confirmação independente está no próprio `A6_manifesto_reproducao.json`
daquela execução, que registrava `platform: Windows-11-10.0.26200-SP0` e
`python 3.12.14 [MSC v.1944]`. A cadeia foi congelada num working tree Windows
anterior ao `.gitattributes` (commit `939eda6`), que hoje impõe
`* text=auto eol=lf`. Num checkout Linux — e em qualquer clone atual, inclusive
no Windows — todo artefato textual passa a ter LF e nenhum dos hashes antigos
confere.

## 3. Escopo real

Cinco artefatos a montante, não um. Três testes acusaram; A5 não acusou por
lacuna de cobertura (seção 6).

## 4. Correção aplicada

Reexecução do conjunto mínimo a jusante, com Python 3.13 e as dependências de
`requirements.txt`:

1. `scripts/tema_trabalho/04_congelar_pre_analise.py`
2. `scripts/tema_trabalho/05_estimar_atracao.py`
3. `scripts/tema_trabalho/06_avaliar_provimento_cnes.py`
4. `scripts/tema_trabalho/07_red_team_sintese.py`

Não foram reexecutados a versão agregada do ciclo 1 — vedada pelo `CLAUDE.md` —
nem a tipologia territorial congelada, cujos hashes de fonte já conferiam com os
arquivos em disco. Nenhum hash foi escrito à mão e nenhum teste foi relaxado.

## 5. Prova de invariância substantiva

| verificação | resultado |
|---|---|
| chaves JSON de A3, A4 e A5 | idênticas (74, 219 e 223 campos) |
| pior diferença relativa numérica em JSON | `4,8e-12` |
| campos não-numéricos alterados | apenas `sha256` e data de geração |
| 24 CSVs, pior diferença relativa | `7,1e-11` |
| `A5_tabela_03h`, termo `const` | `1,1e-14 → -1,1e-14`; intercepto absorvido, zero de máquina, `p=0,99999999` nos dois casos, com `n`, `n_clusters` e `r2` idênticos |
| tabelas de influência municipal | permutação de linhas; mesmo conjunto de chaves, diferença absoluta máxima `4,1e-14`, top-5 de dfbeta idênticos |
| figuras PNG | dimensões em pixels idênticas; apenas bytes codificados diferem |

Os resultados publicados permanecem: A4 com 1.295 células em 368 municípios,
atração de 30,3%, metropolitano versus interior remoto de +29,4 p.p. no LPM
mínimo, +19,8 no ajuste completo, +28,5 em confirmação, +25,0 em homologação e
+33,1 em município–curso; A5 com 587 células em 295 municípios, 0,50 (EP 0,23)
em `202603` e pré-tendências `F=1,03`, `p=0,420`.

## 6. Lacuna de cobertura corrigida

`tests/test_provimento_cnes_a5.py` não tinha nenhuma asserção de proveniência.
Por isso os hashes obsoletos gravados por A5 passaram despercebidos enquanto A3,
A4 e A6 acusavam. Foi acrescentado `test_hashes_entradas_conferem`, que percorre
o bloco `hashes_entradas` dos dois artefatos de A5.

Uma das nove entradas declaradas por A5,
`output/painel_municipio_curso_mensal.parquet`, é regerável pelo pipeline e não
é versionada. O teste exige existência apenas dos arquivos versionados e cobra o
hash do painel somente quando ele está presente, de modo a continuar válido num
clone limpo. O teste foi falsificado: reinjetando o hash CRLF antigo, ele falha
com `hash diverge`.

## 7. Determinismo e regra operacional

- **Dentro da mesma plataforma a reexecução é determinística bit a bit.** Duas
  execuções seguidas de 04→07 produziram 241 arquivos sem nenhuma diferença,
  figuras incluídas.
- **Entre plataformas restam duas divergências que não são defeitos** e não
  afetam nenhuma conclusão: últimos dígitos de ponto flutuante, por diferenças de
  BLAS e libm, e bytes de PNG, por diferenças de matplotlib e freetype, com
  dimensões em pixels idênticas.
- **Regra:** hashes de proveniência devem ser sempre calculados sobre a forma
  canônica LF. O `.gitattributes` vigente já garante isso em qualquer clone, de
  modo que a recorrência exigiria burlar deliberadamente o atributo.
- Um artefato textual cujo hash diverge por exatamente o número de linhas do
  arquivo é, quase sempre, este problema — e não perda de integridade.
