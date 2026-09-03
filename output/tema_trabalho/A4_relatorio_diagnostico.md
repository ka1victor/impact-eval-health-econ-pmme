# A4 — Atração e implementação: diagnóstico e linguagem autorizada (02/09/2026)

> Registro A3: `output/tema_trabalho/registro_pre_analise_atracao.json` (hash 797f160d)
> Potência: `output/tema_trabalho/potencia_atracao.json`; MDE aproximado dos contrastes vs remoto: capital 19.5%, metro 13.7%, próximo 11.9%
> Tipologia A2 strict 540/540 (25/101/238/176) quadro 368 (18/72/203/75)
> Amostra primária: **1295 células CNES–curso Ch1 em 368 municípios**; estendida 3057 (1762 Ch2)

## 1. Construção e suporte (antes dos coeficientes)

Primária 1295: outcome médio **30.3%** (393/1295). Por estrato: capital 35.6% (73), metropolitano 44.9% (265), interior próximo 26.9% (811), remoto 20.5% (146). Ver `A4_tabela_01_amostra_construcao.csv` (por estrato) + `A4_tabela_00_construcao_steps.csv` (3323→3057→1295, 266 sem municipio, 29 fora quadro Ch1 com municipio).

Faixa anunciada (descritiva, não causal): FAIXA1 31.6% (n=291), FAIXA2 37.4% (465), FAIXA3 23.6% (539) — ver `A4_tabela_01b_amostra_faixa.csv`. IVS 2010 mediano 0.331; Q1–Q4 prevalência ver figura 02; correlação IVS–outcome 0.09 (associativa). Estoque pré médio 26.1 por município; log(pop) mediano 9.77. Curso distribuição ver `A4_tabela_01c_amostra_curso.csv` (16 cursos, min 22 max 188), UF ver `A4_tabela_01d_amostra_uf.csv` (27 UFs, 8 com <5 clusters colapsadas em RESTO: AL, AP, DF, ES, PB, PE, RR, SE) para FE.

População estendida Ch1+Ch2 (3057): prevalência Ch1 30.3% vs Ch2 11.7%, reforçando que Ch2 é cadastro reserva sem capacidade imediata numérica; análise conjunta mantém FE de chamada. Construção sem escolher amostra por resultado; 266 sem municipio e 29 fora quadro mantidos fora da primária por definição prévia.

## 2. Modelo primário exatamente como congelado em A3

**Especificação:** `outcome ~ estrato (ref. interior_remoto) + FE curso (16) + FE UF (colapsada)`, LPM com cluster município (G=368, G−1 gl). Logit AME mesma spec como alternativo.

**LPM minimal — coeficientes estrato (pp vs interior_remoto):**

| Estrato | coef (SE) cluster | IC95% | q FDR (3 testes) |
|---|---|---|---|
| capital | 0.232 (0.086)** | 0.063 a 0.400 | 0.007 |
| interior proximo polo | 0.127 (0.043)** | 0.042 a 0.211 | 0.005 |
| metropolitano | 0.294 (0.061)*** | 0.175 a 0.413 | 0.000 |

N=1295, G=368, R²=0.238, outcome médio 30.3%. O benchmark global de 3,8% mede precisão de uma proporção, não potência do coeficiente. Para os contrastes efetivos contra remoto, os MDEs aproximados são 19.5% (capital), 13.7% (metro) e 11.9% (próximo).

**Logit AME (mesma spec):**

| Estrato | AME (SE) | IC95% |
|---|---|---|
| capital | 0.250 (0.101) | 0.053 a 0.447 |
| interior proximo polo | 0.108 (0.040) | 0.029 a 0.187 |
| metropolitano | 0.293 (0.064) | 0.167 a 0.418 |


Concordância LPM–Logit: gradiente metro > capital > próximo > remoto (ref.) persiste; magnitude LPM ≈ AME (dif. <2pp).

**Robustez de definição e unidade.** Separando o funil, o contraste metropolitano vs remoto é 0.285 para alguma confirmação e 0.250 para alguma homologação. Colapsando múltiplos CNES para 1.184 células município–curso, o contraste é 0.331 (p=0.000). O gradiente não depende da união dos estágios nem do peso implícito de municípios com mais de um CNES.

## 3. Sensibilidade e separações (sem causalidade)

- **Ajuste completo** (+ IVS linear, log pop, estoque/10k, faixa): estrato metro 0.198 (p=0.020), capital 0.066 (ns), próximo 0.077 (ns); IVS -0.043 (p=0.880, ns); log pop 0.046 (p=0.056); faixa FAIXA2 vs FAIXA1 0.021 (ns), FAIXA3 vs FAIXA1 -0.070 (ns). Com ajuste, gradiente atenua — UF e curso capturam parte da variação territorial. Ver `A4_tabela_03b_ajuste_completo.csv`.

- **Winsorizado p99** (pop e estoque clipados p01-p99): metro 0.202, capital 0.075, próximo 0.080 — gradiente preservado, outliers não dirigem resultado. Ver `A4_tabela_03c_winsorizado.csv`.

- **IVS quadrático** (linear + quadrático como proxy spline): IVS linear -0.518, quadrático 0.636 (p=0.677, ns) — não linearidade não detectada; mantém linear parsimonioso. Ver `A4_tabela_03d_ivs_spline.csv`.

- **Faixa só (FE)**: FAIXA2 +0.108 vs FAIXA1, FAIXA3 +0.009 — descritivo; **não chamar de efeito da bolsa** (faixa colinear com IVS, colinearidade intencional da regra 2025).

- **IVS só (FE)**: coef 0.017 (p=0.944, ns) — gradiente vulnerabilidade não significativo condicional a FE; figura Q1–Q4 mostra variação modesta.

- **Estrato×IVS**: interação não significativa global; heterogeneidade IVS dentro de cada estrato limitada (ver `A4_tabela_03_separacao_*.csv`).

Interpretação: **associado a** maior atração em metropolitano/capital vs remoto, mas ajustado perde significância para capital/próximo; nenhuma evidência de gradiente causal de bolsa ou IVS.

## 4. Influência e robustez

Leave-one-UF (27): metro range 0.268–0.330 sd 0.012; capital 0.171–0.287. 
**leave_one_UF**: range metro 0.268–0.330 (sd 0.012); capital 0.202–0.287.

**leave_one_curso**: range metro 0.270–0.324 (sd 0.014); capital 0.171–0.268.


Leave-one-curso (16): metro range 0.270–0.324.

Leave-one-município (368): metro Δ min 0.280 max 0.321 sd 0.004 (base 0.294); top influentes:
- `co_ibge_6d 160030` em `estrato_capital`: Δ 0.043 (DFBETA 0.50)
- `co_ibge_6d 231290` em `estrato_metropolitano`: Δ 0.026 (DFBETA 0.43)
- `co_ibge_6d 140010` em `estrato_capital`: Δ 0.034 (DFBETA 0.40)
- `co_ibge_6d 312670` em `estrato_interior_proximo_polo`: Δ 0.017 (DFBETA 0.40)
- `co_ibge_6d 110020` em `estrato_capital`: Δ -0.029 (DFBETA -0.34)

Nenhum município inverte sinal do gradiente metro vs remoto.

Curso: análise por curso descritiva (cursos 7,10,11 com menor atração) — não testar 16 hipóteses independentes.

## 5. Validação preditiva (por município)

GroupKFold 5 splits por município (treino e teste sem compartilhar município): LPM out-sample AUC 0.757 sd 0.021, in-sample AUC 0.798, Brier out 0.177 vs in 0.160; Logit out AUC 0.756, in 0.801. Ver `A4_tabela_06_validacao_preditiva.csv`. Gap out vs in indica overfit de FE curso/UF e poder preditivo modesto — R² in-sample 0.238 não é prova preditiva.

## 6. Figuras

- `A4_figura_01_prob_ajustada_estrato.png`: médias marginais por estrato com IC95% delta-method cluster, inclusive a referência.
- `A4_figura_02_gradiente_ivs.png`: quartis observados e curva marginal com composição curso/UF mantida fixa.
- `A4_figura_03_faixa_descritiva.png`: FAIXA 1–3 (observada vs ajustada FE) — colinearidade faixa–IVS impede leitura causal.

## 7. Linguagem autorizada

Permitido: atração administrativa (alguma confirmação/homologação observada na célula), preenchimento parcialmente observável, gradiente territorial, persistência da oferta local (CNES agregado quando validado). **Proibido:** taxa de preenchimento por vaga, retenção individual do bolsista, efeito causal do PMM-E/bolsa/IVS, candidaturas por vaga, WTA. Faixa é descritiva.

## 8. Limites e próximos passos

- Capital G=18 <30: IC nominal; para heterogeneidade fina por estrato, reportar wild bootstrap se G pequeno (não computado nesta entrega).
- Cursos <50 células (ex. curso 3 n=26) MDE >15pp — análise por curso descritiva.
- Não estimar dose recebida (salário) nem retenção individual; A5 validará T0 físico CNES e ponte CBO 10/16 sem sobreposição.
- Pesos por vagas alteram estimando; não ponderado é primário.

*Gerado por `scripts/tema_trabalho/05_estimar_atracao.py` em 02/09/2026. Hashes entradas verificados em `A4_estimativas_atracao.json`.*
