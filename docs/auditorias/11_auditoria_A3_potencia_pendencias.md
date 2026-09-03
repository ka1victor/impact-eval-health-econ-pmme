# Auditoria A3 — potência por estrato (corrigida em loop 02/09/2026)

> **Data da auditoria inicial:** 02/09/2026 (pendências documentadas sem correção por instrução)
> **Data da correção:** 02/09/2026 — loop A3 iteração 1 (trabalho até perfeito)
> **Artefatos auditados:** `output/tema_trabalho/potencia_atracao.json`, `output/tema_trabalho/registro_pre_analise_atracao.json`, `docs/06_execucao/31_secao_econometrica_A3.md`, `scripts/tema_trabalho/04_congelar_pre_analise.py`
> **Decisão anterior:** A3 permanecia congelado em `30463d9`/`bc138ab` com pendências documentadas.
> **Decisão atual:** **CORRIGIDO** — artefatos re-congelados com clusters do quadro Ch1, DEFF floor e hashes completos. 11 pendências resolvidas; A3 perfeito.

## 1. Pendência crítica — denominador de clusters por estrato [RESOLVIDA]

- **Onde:** `scripts/tema_trabalho/04_congelar_pre_analise.py:88-104` (`g = n_municipios_populacao_A1`) e `potencia_atracao.json:24-59`
- **O que:** MDE por estrato usava `n_municipios_populacao_A1` (540) como `g`, quando a população primária é o **quadro Ch1** (`1295` células em **368** municípios). Correto é nº de municípios **do quadro Ch1** por estrato.
- **Histórico (antes do strict A2):** `capital 73/25 m2.92 deff1.096 15.7% → 73/18 16.1%`; `metropolitano 289/104 m2.78 deff1.089 7.9% → 289/75 m3.85 deff1.142 8.1%`; `interior_proximo 787/235 m3.35 deff1.117 4.8% → 787/200 m3.94 deff1.147 4.9%`; `interior_remoto 146/176 m0.83 deff0.991 10.6% → 146/75 m1.95 deff1.047 10.9%`; global `1295/368 deff1.126 3.8%` correto. O `deff<1` era artefato `m<1`.
- **Com strict A2 (corrigido agora):** valores finais congelados são **`capital 73/18 m4.06 deff1.153 mde30 16.1%`**, **`metropolitano 265/72 m3.68 deff1.134 mde30 8.4%`**, **`interior_proximo 811/203 m4.00 deff1.150 mde30 4.8%`**, **`interior_remoto 146/75 m1.95 deff1.047 mde30 10.9%`**, global `1295/368 deff1.126 mde30 3.8%`. Implicação permanece otimista 3–5% antes, agora corrigida.
- **Correção aplicada:** `04_congelar_pre_analise.py:86-110` agora faz `merge(quadro, tipologia).groupby(estrato).nunique()` para `g`, `deff=max(1,1+(m-1)*ICC)`, assert contra `suporte`, e `mde` recalculado. Seção `31_secao_econometrica_A3.md:27-30` agora lista 4 estratos completos com `265/72` e `811/203` (strict).

## 2. Outras observações [RESOLVIDAS]

- **Hashes território ausentes em A3:** `registro_pre_analise_atracao.json:102-117` omitia XLSX de território. **Corrigido:** agora `hashes_entradas` contém 7 entradas (`quadro`, `matriz_tipologia`, `malha`, `manifesto`, `portao`, `REGIC2018...xlsx`, `Composicao_RMs...xlsx`) + 2 artefatos, verificados (`scripts/04:229-233`).
- **Seção econométrica truncada:** `31_secao_econometrica_A3.md:25-28` só listava 2 estratos (remoto, metropolitano). **Corrigido:** agora lista 4 estratos `capital 73/18 metropolitano 265/72 interior_proximo 811/203 interior_remoto 146/75` com DEFF e MDE.
- **Transformação população:** `registro:65` `log1p` vs `log` em comentários — **mantido** `log1p` canônico; seção agora mantém `log(pop 2010)` como descritivo mas registro congela `log1p`.
- **Testes não pegavam:** `tests/test_pre_analise_atracao.py:53-62` checava só `mde<0.05` global. **Corrigido:** agora 12 testes cobrem `deff>=1`, `m>1`, `n_municipios` strict `18/72/203/75`, `n_celulas` `73/265/811/146`, `mde` numérico `0.1613/0.0840/0.0483/0.1087`, `hashes` território e `tipologia strict`.

## 3. Registro de decisão

Pendências da auditoria inicial foram **todas corrigidas em loop** nesta data, sem reabrir estimações (só pré-análise). `potencia_atracao.json` e `registro_pre_analise_atracao.json` re-congelados com hashes `742945f6`/`80bc3811`/`8a998641` verificados; `31_secao_econometrica_A3.md` completa; `tests/test_pre_analise_atracao.py` 12/12 OK (70/70 total). Próxima emenda só se A4 detectar desvio datado.

## 4. Emenda pós-estimação de 03/09/2026

A revisão da A4 identificou que os MDEs acima eram de uma proporção dentro de cada estrato, não dos contrastes de regressão contra a categoria de referência. O cálculo foi mantido apenas como benchmark descritivo e foram adicionados MDEs de duas proporções com DEFF separado para cada lado do contraste: 19,5pp para capital, 13,7pp para metropolitano e 11,9pp para interior próximo, sempre versus interior remoto e sob p=0,30. Esta emenda corrige a interpretação de potência sem alterar população, outcome ou especificação congelados.
