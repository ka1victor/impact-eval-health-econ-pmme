# A4 — Atração e implementação: diagnóstico e linguagem autorizada (02/09/2026)

> Registro A3: `output/tema_trabalho/registro_pre_analise_atracao.json` (hash eb2bf812)
> Potência: `output/tema_trabalho/potencia_atracao.json`; MDE **ex-ante** dos contrastes vs remoto: capital 19.5%, metro 13.7%, próximo 11.9%. O MDE **ex-post** do EP realizado está na seção 2 e em `A4_tabela_09_mde_ex_ante_ex_post.csv`
> Tipologia A2 strict 540/540 (25/101/238/176) quadro 368 (18/72/203/75)
> Amostra primária: **1295 células CNES–curso Ch1 em 368 municípios**; estendida 3057 (1762 Ch2)

## 1. Construção e suporte (antes dos coeficientes)

Primária 1295: outcome médio **30.3%** (393/1295). Por estrato: capital 35.6% (73), metropolitano 44.9% (265), interior próximo 26.9% (811), remoto 20.5% (146). Ver `A4_tabela_01_amostra_construcao.csv` (por estrato) + `A4_tabela_00_construcao_steps.csv` (3323→3057→1295, 266 sem municipio, 29 fora quadro Ch1 com municipio).

Faixa anunciada (descritiva, não causal): FAIXA1 31.6% (n=291), FAIXA2 37.4% (465), FAIXA3 23.6% (539) — ver `A4_tabela_01b_amostra_faixa.csv`. IVS 2010 mediano 0.331; Q1–Q4 prevalência ver figura 02; correlação IVS–outcome 0.09 (associativa). Estoque pré médio 26.1 por município; log(pop) mediano 9.77. Curso distribuição ver `A4_tabela_01c_amostra_curso.csv` (16 cursos, min 22 max 188), UF ver `A4_tabela_01d_amostra_uf.csv` (27 UFs, 8 com <5 clusters colapsadas na macrorregião de saúde conforme A3 — AL, AP, DF, ES, PB, PE, RR, SE —, resultando em 24 níveis de FE) para FE.

População estendida Ch1+Ch2 (3057): prevalência Ch1 30.3% vs Ch2 11.7%, reforçando que Ch2 é cadastro reserva sem capacidade imediata numérica; análise conjunta mantém FE de chamada. Construção sem escolher amostra por resultado; 266 sem municipio e 29 fora quadro mantidos fora da primária por definição prévia.

## 2. Modelo primário exatamente como congelado em A3

**Especificação:** `outcome ~ estrato (ref. interior_remoto) + FE curso (16) + FE UF (UF com <5 clusters colapsada na macrorregião de saúde, como manda o registro A3)`, LPM com cluster município (G=368, G−1 gl). Logit AME mesma spec como alternativo.

**LPM minimal — coeficientes estrato (pp vs interior_remoto):**

| Estrato | coef (SE) cluster | IC95% | q FDR (3 testes) |
|---|---|---|---|
| capital | 0.326 (0.072)*** | 0.186 a 0.467 | 0.000 |
| interior proximo polo | 0.121 (0.043)** | 0.036 a 0.205 | 0.005 |
| metropolitano | 0.279 (0.059)*** | 0.165 a 0.394 | 0.000 |

N=1295, G=368, R²=0.261, outcome médio 30.3%. O benchmark global de 3,8% mede precisão de uma proporção, não potência do coeficiente. Para os contrastes efetivos contra remoto, os MDEs **ex-ante** aproximados são 19.5% (capital), 13.7% (metro) e 11.9% (próximo).

**Logit AME (mesma spec):** o contraste de estrato troca o **bloco inteiro** de indicadoras contra `interior_remoto`, e não uma indicadora isolada. A última coluna traz, só para auditoria, o valor que `get_margeff(dummy=True)` devolvia: ele altera apenas a coluna do estrato avaliado e mantém as demais no valor observado, o que constrói células simultaneamente capital e metropolitana — um contrafactual que não existe na população — e superestima o contraste.

| Estrato | AME (SE) | IC95% | AME antigo (indicadora isolada) |
|---|---|---|---|
| capital | 0.340 (0.076) | 0.192 a 0.489 | 0.361 |
| interior proximo polo | 0.091 (0.035) | 0.022 a 0.159 | 0.101 |
| metropolitano | 0.251 (0.052) | 0.149 a 0.354 | 0.278 |


Concordância LPM–Logit: gradiente metro > capital > próximo > remoto (ref.) persiste; magnitude LPM ≈ AME (dif. <2pp).

**Wild cluster bootstrap (registro A3).** O A3 manda reportar wild cluster bootstrap quando um subgrupo tem `G<30`, e capital tem `G=18` na amostra primária. A reauditoria acrescenta que o `G=368` do cluster principal é nominal, por concentração da variância de `estrato_metropolitano` em poucos municípios; esse diagnóstico é da auditoria e não é recomputado aqui. Procedimento restrito, pesos de Rademacher por município, `B=1999`, semente `42`, `p = (1 + excedentes) / (B + 1)`:

| Estrato | t observado | p nominal cluster | p wild | excedentes |
|---|---|---|---|---|
| capital | 4.547 | 0.00001 | 0.0015 | 2 de 1999 |
| metropolitano | 4.770 | 0.00000 | 0.0005 | 0 de 1999 |
| interior proximo polo | 2.798 | 0.00514 | 0.0115 | 22 de 1999 |


O `p` wild é **coluna adicional**, não substituto: o `p` principal continua sendo o cluster-robusto nominal, e o `q` de FDR entre estratos segue calculado sobre ele.

**Potência ex-post.** O MDE ex-ante de A3 é analítico e ignora que os FE de curso e de UF absorvem variação do próprio estrato, então subestima o erro-padrão que o modelo entrega. Os dois ficam publicados lado a lado; o ex-ante **não** é recalculado, porque A3 é protocolo congelado:

| Estrato | EP realizado | MDE ex-post | MDE ex-ante A3 | otimismo do ex-ante |
|---|---|---|---|---|
| capital | 0.07179 | 20.1% | 19.5% | +3.4% |
| metropolitano | 0.05855 | 16.4% | 13.7% | +19.4% |
| interior proximo polo | 0.04312 | 12.1% | 11.9% | +1.5% |


**Robustez de definição e unidade.** Separando o funil, o contraste metropolitano vs remoto é 0.270 para alguma confirmação e 0.238 para alguma homologação. Colapsando múltiplos CNES para 1.184 células município–curso, o contraste é 0.316 (p=0.000). O gradiente não depende da união dos estágios nem do peso implícito de municípios com mais de um CNES.

## 3. Sensibilidade e separações (sem causalidade)

- **Colapso do FE de UF.** O registro A3 manda "colapsar UF com <5 clusters **em região**". A primária implementa isso: cada uma das 8 UFs pequenas entra pela sua macrorregião de saúde. As três variantes, com a mesma amostra (N=1295), o mesmo desfecho, o mesmo cluster (G=368) e a mesma referência `interior_remoto`:

| Variante do colapso | Níveis de FE UF | Capital | Metropolitano | Interior próximo |
|---|---:|---:|---:|---:|
| `macro_regiao` **(primária)** | 24 | +0.3264 | +0.2793 | +0.1207 |
| `balde_unico` | 20 | +0.2318 | +0.2942 | +0.1266 |
| `sem_colapso` | 27 | +0.3358 | +0.2733 | +0.1200 |

A escolha da primária é a do protocolo, não uma seleção posterior ao resultado; as três ficam publicadas em `A4_tabela_07_sensibilidade_colapso_uf.csv` com EP cluster, p-valor, níveis de FE e N. O balde único `RESTO`, usado antes da auditoria, punha num único nível de FE quatro macrorregiões, com 32 células de capital contra 1 de interior remoto — exatamente a comparação entre estados que o FE de UF deveria impedir. O contraste metropolitano é estável entre as três variantes; o de capital é o que se move. Limite conhecido: os 4 municípios de UF pequena sem macrorregião publicada na tipologia (UNIAO DOS PALMARES/AL, OIAPOQUE/AP, CACHOEIRO DE ITAPEMIRIM/ES, LINHARES/ES; 6 células, estratos interior_proximo_polo, interior_remoto) formam o nível residual MACRO_SEM_REGIAO_SAUDE, que ainda agrega UFs de macrorregiões distintas.

- **Ajuste completo** (+ IVS linear, log pop, estoque/10k, faixa): estrato metro 0.209 (p=0.008), capital 0.198 (ns), próximo 0.082 (ns); IVS -0.245 (p=0.384, ns); log pop 0.036 (p=0.117); faixa FAIXA2 vs FAIXA1 -0.011 (ns), FAIXA3 vs FAIXA1 -0.100 (ns). Com ajuste, gradiente atenua — UF e curso capturam parte da variação territorial. Ver `A4_tabela_03b_ajuste_completo.csv`.

- **Winsorizado p99** (pop e estoque clipados p01-p99): metro 0.212, capital 0.205, próximo 0.086 — gradiente preservado, outliers não dirigem resultado. Ver `A4_tabela_03c_winsorizado.csv`.

- **IVS quadrático** (linear + quadrático como proxy spline): IVS linear -0.957, quadrático 0.952 (p=0.530, ns) — não linearidade não detectada; mantém linear parsimonioso. Ver `A4_tabela_03d_ivs_spline.csv`.

- **Faixa só (FE)**: FAIXA2 +0.096 vs FAIXA1, FAIXA3 +0.008 — descritivo; **não chamar de efeito da bolsa** (faixa colinear com IVS, colinearidade intencional da regra 2025).

- **IVS só (FE)**: coef -0.102 (p=0.671, ns) — gradiente vulnerabilidade não significativo condicional a FE; figura Q1–Q4 mostra variação modesta.

- **Estrato×IVS**: interação não significativa global; heterogeneidade IVS dentro de cada estrato limitada (ver `A4_tabela_03_separacao_*.csv`).

Interpretação: **associado a** maior atração em metropolitano/capital vs remoto, mas ajustado perde significância para capital/próximo; nenhuma evidência de gradiente causal de bolsa ou IVS.

## 4. Influência e robustez

Leave-one-UF (27): metro range 0.253–0.315 sd 0.012; capital 0.273–0.362. 
**leave_one_UF**: range metro 0.253–0.315 (sd 0.011); capital 0.299–0.361.

**leave_one_curso**: range metro 0.255–0.310 (sd 0.013); capital 0.273–0.362.


Leave-one-curso (16): metro range 0.255–0.310.

Leave-one-município (368): metro Δ min 0.265 max 0.305 sd 0.003 (base 0.279); top influentes:
- `co_ibge_6d 130260` em `estrato_capital`: Δ 0.039 (DFBETA 0.54)
- `co_ibge_6d 231290` em `estrato_metropolitano`: Δ 0.026 (DFBETA 0.45)
- `co_ibge_6d 120040` em `estrato_capital`: Δ 0.030 (DFBETA 0.42)
- `co_ibge_6d 312670` em `estrato_interior_proximo_polo`: Δ 0.017 (DFBETA 0.39)
- `co_ibge_6d 110020` em `estrato_capital`: Δ -0.024 (DFBETA -0.33)

Nenhum município inverte sinal do gradiente metro vs remoto.

Curso: análise por curso descritiva (cursos 7,10,11 com menor atração) — não testar 16 hipóteses independentes.

## 5. Validação preditiva (por município)

GroupKFold 5 splits por município (treino e teste sem compartilhar município): LPM out-sample AUC 0.774 sd 0.026, in-sample AUC 0.812, Brier out 0.170 vs in 0.155; Logit out AUC 0.775, in 0.815. Ver `A4_tabela_06_validacao_preditiva.csv`. Gap out vs in indica overfit de FE curso/UF e poder preditivo modesto — R² in-sample 0.261 não é prova preditiva.

## 6. Figuras

- `A4_figura_01_prob_ajustada_estrato.png`: médias marginais por estrato com IC95% delta-method cluster, inclusive a referência.
- `A4_figura_02_gradiente_ivs.png`: quartis observados e curva marginal com composição curso/UF mantida fixa.
- `A4_figura_03_faixa_descritiva.png`: FAIXA 1–3 (observada vs ajustada FE) — colinearidade faixa–IVS impede leitura causal.

## 7. Linguagem autorizada

Permitido: atração administrativa (alguma confirmação/homologação observada na célula), preenchimento parcialmente observável, gradiente territorial, persistência da oferta local (CNES agregado quando validado). **Proibido:** taxa de preenchimento por vaga, retenção individual do bolsista, efeito causal do PMM-E/bolsa/IVS, candidaturas por vaga, WTA. Faixa é descritiva.

## 8. Limites e próximos passos

- Capital G=18 <30 na amostra primária, gatilho literal do registro A3. O wild cluster bootstrap exigido foi computado (Rademacher, nula imposta, B=1999, semente 42) e está na seção 2 e em `A4_tabela_08_wild_cluster_bootstrap.csv`. O p wild é coluna adicional; o p principal continua sendo o cluster-robusto nominal.
- Cursos <50 células (ex. curso 3 n=26) MDE >15pp — análise por curso descritiva.
- Não estimar dose recebida (salário) nem retenção individual; A5 validará T0 físico CNES e ponte CBO 10/16 sem sobreposição.
- Pesos por vagas alteram estimando; não ponderado é primário.

*Gerado por `scripts/tema_trabalho/05_estimar_atracao.py` em 02/09/2026. Hashes entradas verificados em `A4_estimativas_atracao.json`.*
