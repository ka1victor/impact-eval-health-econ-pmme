# A5 — Persistencia da oferta medica local no CNES (associativo)

> Registro A3: `output/tema_trabalho/registro_pre_analise_atracao.json` (hash 42a8a279)
> Potencia A3: MDE global 3.8% p30; estrato capital 16.1% metro 8.4% proximo 4.8% remoto 10.9%
> Tipologia A2 strict 540/540 (25/101/238/176) painel 368 mun 1184 celulas municipio-curso
> Amostra A5: **1184 celulas municipio-curso (368 municipios) x26 competencias =30784 linhas**; confirmatoria 587 (295 mun) sem sobreposicao
> T0_admin: **202510** (primeira competencia apos homologacao 2025-09-29); baseline 202509 -> follow 6m 202603; horizonte comum 6 meses maduro
> Ponte: 10 cursos estritamente univocos (1,2,3,5,9,12,13,14,15,16) como primario; 6 cursos sobrepostos (4,6,7,8,10,11) sensibilidade

## 1. Construcao, painel alinhado ao T0 e maturidade/censura

Painel analitico `A5_painel_T0.parquet` (30784 linhas) alinha `t_rel_T0 = competencia - 202510` com definicoes:
- estoque_mst: CO_PROFISSIONAL_SUS distinto por municipio-curso-mes (CBOs operacionais do curso; deduplicacao intramunicipal)
- cobertura_binaria_mst: 1[estoque>0]
- n_entradas_6m: presente em t e ausente nos 6 meses anteriores (censurado se <202412)
- n_saidas_confirmadas_3m: presente em t e ausente nos 3 meses posteriores (censurado se >202604)
- presentes_6m (nivel): entrantes elegiveis em t ainda presentes em t+6 (nivel, nao taxa; madura se idx+6<26 ate 202601)
- saldo_liquido: entradas - saidas

Censura documentada: 26 competencias 202406-202607 completas; estoque nunca censurado (0 se sem profissional); entradas indisponiveis 202406-202411 (primeiros 6m), saidas indisponiveis 202605-202607 (ultimos 3m), presenca madura ate baseline 202601 (inclui 202509). Ver `A5_manifesto_maturidade_censura.json` e `A5_tabela_00_construcao_steps.csv`.

T0 fisico validado: nominal ciclo1 n=521, dt_inicio de 2025-09-11 a 2026-03-17, mediano 2025-09-19 (p25 2025-09-18 p75 2025-11-24), 274 antes vs 247 apos homologacao 2025-09-29. Snapshot de sobreviventes ativos em 2026-08-12, nao log completo, por isso T0_admin 202510 e usado como referencia agregada e baseline 202509 como ultima pre-T0 madura. Ponte restrita ao nucleo sem sobreposicao (587 celulas) como primario: FTE cadastral por CNES nao contamina cursos compartilhados.

## 2. Trajetoria agregada (antes dos coeficientes)

Media geral estoque: 13.05 (202406) -> 13.92 (202509 baseline) -> 14.65 (202603 follow) -> 15.20 (202607). Incremento 6m baseline->follow medio **0.73** sd 6.16 (mediana 0.0). Por estrato baseline: capital  69.7  metropolitano 18.8  interior_proximo 9.9  remoto 2.6 . Ver `A5_tabela_01b_trajetoria_mensal.csv` e figuras `A5_figura_01/02`.

Por atracao administrativa A1 (agregada ao municipio-curso, max sobre CNES): com atracao N=378 media baseline 22.2 estoque_6m 23.6 delta 1.42; sem atracao N=806 baseline 10.0 delta 0.41. Cobertura baseline: com atracao 97.4% vs sem 93.2%; 6m: 97.9% vs 93.4%. Entradas 6m media: 0.60 vs 0.17; presentes nivel: 0.51 vs 0.12. Ver `A5_tabela_02_descritiva_outcomes_6m.csv`.

## 3. Modelos primarios (associativos, sem causalidade)

Especificacao minimal exatamente como A3 adaptada: `outcome ~ atracao_muni (0/1) + FE curso (16) + FE UF(colapsada RESTO ['14', '16', '25', '26', '27', '28', '32', '53']) + cluster municipio (G=368)`. Atracao preditor binario municipal (max sobre CNES). Full adiciona estrato + ivs_2010 + log_pop + estoque_por_10k.

| Outcome 6m | coef atracao (SE) minimal | IC95% | p | N | G | R2 | coef full |
|---|---|---|---|---|---|---|---|
| estoque_6m | 12.006 (3.707) | 4.739 a 19.272 | 0.001 | 1184 | 368 | 0.118 | 5.705 |
| delta_estoque_6m | 0.641 (0.401) | -0.145 a 1.427 | 0.110 | 1184 | 368 | 0.042 | 0.462 |
| cobertura_6m (LPM) | 0.044 (0.014) | 0.016 a 0.072 | 0.002 | 1184 | 368 | - | - |
| entradas_6m follow | 0.345 (0.144) | 0.062 a 0.628 | 0.017 | | | | |
| presentes_baseline_6m (nivel) | 0.384 (0.089) | 0.209 a 0.559 | 0.000 | | | | |

Linguagem: **associado a** maior estoque/cobertura em 6m quando houve atracao na celula; delta pequeno e IC largo; nenhuma inferencia causal nem dose bolsa. Faixa nao entra como covariada principal por colinearidade com IVS (regra anunciada). Ver `A5_tabela_03*.csv`.

Sensibilidade horizonte alternativo 202507->202601: coef delta 0.566 (SE 0.269) p 0.036 - magnitude similar, preserva conclusao.
Sensibilidades adicionais: winsorizado p99 delta 0.327 (p 0.009); confirmatoria 587 vs ampliada 597: confirmatoria 1.080 (ampliada em tabela `A5_tabela_03h`); heterogeneidade atracao x estrato nao significativa (ver `A5_tabela_03i`). Ver `A5_tabela_03g/03h/03i`.

## 4. Influencia e robustez

Leave-one-UF (27) e leave-one-curso (16) para delta minimal: range coef atracao 0.200 a 0.831 sd 0.109. Nenhuma UF/curso inverte sinal de forma relevante. Ver `A5_tabela_04_leave_one_out.csv`.

Leave-one-municipio (368) DFBETA para atracao em delta: base 0.641 range 0.277 a 0.698 sd 0.021; top influentes: 530010 Δ-0.36 DFBETA-0.91, 140047 Δ-0.06 DFBETA-0.15, 251080 Δ0.06 DFBETA0.14 . Nenhum |DFBETA|>1.5. Ver `A5_tabela_05_influencia_municipal.csv`.

Curso como exploracao: 10 cursos confirmatorios contribuem; cursos sobrepostos estratificados mostram sensibilidade sem mudar primario.

## 5. Validacao preditiva por municipio (GroupKFold 5)

Delta estoque minimal: R2 out -0.278 sd 0.218 vs in 0.042; RMSE out 4.35 vs in 6.03.
Estoque 6m: R2 out -0.076 vs in 0.118. Gap pequeno indica overfit FE limitado. Ver `A5_tabela_06_validacao_preditiva.csv`.

## 6. Figuras

- `A5_figura_01_trajetoria_estoque_estrato.png`: trajetoria medias por estrato com T0.
- `A5_figura_02_trajetoria_estoque_atracao.png`: com vs sem atracao.
- `A5_figura_03_delta_estoque_atracao.png`: delta 6m por atracao.

## 7. Linguagem autorizada e decisao sobre ligacao com atracao

Permitido: oferta cadastrada local, persistencia da oferta local (estoque/cobertura/entradas/saldo/presentes em nivel), gradiente territorial, associado a. **Proibido:** retenção individual do bolsista, atividade fisica confirmada, efeito causal do PMM-E/bolsa/IVS, WTA, taxa por vaga, dose recebida.

Decisao explicita: **Pode** ligar descriptiva e associativamente o outcome A1 binario por celula (atracao administrativa max ao municipio-curso) ao painel CNES agregado no horizonte 6m comum 202509->202603 usando especificacoes pre-definidas, FE curso/UF e cluster municipio, com ponte restrita ao nucleo sem sobreposicao como primario e estratificacao ampliada como sensibilidade. A ligacao e **somente associativa** (persistencia da oferta local onde houve atracao vs onde nao houve), reportada em nivel e diferenca bruta/ajustada, sem taxa condicional a entrantes.

**Nao pode:** chamar delta ou presenca de efeito do PMM-E/bolsa adicional; nao chamar presenca no CNES de participacao confirmada no programa; nao usar presenca condicionada so nos entrantes como retencao; nao interpretar entradas tardias 202605+ sem censura; nao converter faixa anunciada em dose causal (colinearidade IVS-faixa).

## 8. Limites e proximos passos

- Amostra 1184 municipio-curso tem municipios com múltiplos CNES; unidade inferencia municipio correta, mas potencia heterogeneidade por estrato limitada (capital 18 clusters) como em A3.
- Entradas/saidas dependem de definicao 6m/3m e da estabilidade do identificador CO_PROFISSIONAL_SUS (continuidade mediana 99.2% mes a mes, mas sem documentacao externa; ver manifesto painel).
- Presenca em nivel e pequeno (media <0.3); ruidos cadastrais podem confundir mudanca real.
- Sem log de eventos PMM-E (A07-02) e sem ponte individual (A07-03), nao vincular individuo bolsista a CNES.
- Sem regra administrativa validada (R1), nao estimar salto causal em cutoff IVS para CNES; manter A6 red team antes de artigo.

*Gerado por `scripts/tema_trabalho/06_avaliar_provimento_cnes.py` em 2026-09-02. Hashes verificados em `A5_estimativas_provimento.json` e `A5_manifesto_maturidade_censura.json`.*
