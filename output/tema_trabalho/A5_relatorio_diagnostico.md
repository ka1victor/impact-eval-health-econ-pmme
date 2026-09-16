# A5 — Evolução da oferta médica cadastrada local no CNES

> **Nível de identificação:** associativo; atração administrativa é resultado realizado, não tratamento exógeno.
> **Amostra principal:** 587 células município–curso, 295 municípios e 10 cursos cujo CBO não é compartilhado com outro curso do PMM-E; oito deles têm CBO estritamente 1:1.
> **Referência limpa:** junho/2025, última competência anterior à publicação da oferta.
> **Follow comum:** março/2026; nove meses de calendário desde a referência, com tempo de exposição física heterogêneo.

## 1. Correção de desenho

Setembro/2025 não é usado como baseline principal. O snapshot nominal registra início mediano em 2025-09-19, com datas entre 2025-09-11 e 2026-03-17; portanto, setembro já contém exposição parcial. A janela setembro/2025–março/2026 permanece apenas como diagnóstico histórico em `A5_tabela_03f_sensibilidade_T0_alternativo.csv`.

Os modelos principais usam somente a ponte sem CBO compartilhado. As 597 células dos seis cursos com CBO compartilhado aparecem como sensibilidade ampliada, nunca misturadas ao estimando principal.

## 2. Resultado principal: dinâmica proporcional do estoque

O estudo de evento compara a trajetória do estoque CNES de células com e sem atração administrativa, relativamente a junho/2025. Ele absorve efeitos fixos município–curso, curso–mês e UF–mês e agrupa a inferência por município.

**A escala proporcional é a forma primária de reportar A5.** O desfecho em nível soma profissionais de municípios com estoques de ordens de grandeza diferentes, de modo que um curso com estoque grande domina o coeficiente mecanicamente; a escala proporcional mede variação relativa da oferta local, que é a pergunta pretendida. A escolha é substantiva e vale independentemente da direção do resultado.

- Em março/2026, a diferença ajustada em `log1p` do estoque, relativa a junho/2025, é 0.0684 (EP 0.0191, p=0.0004 na convenção que conta os efeitos fixos absorvidos; EP 0.0181 e p=0.0002 na convenção anterior).
- Teste conjunto dos coeficientes anteriores à referência: F=0.633, p=0.813. A não rejeição não prova comparabilidade.
- A estimativa descreve evolução diferencial associada à atração; não é efeito do PMM-E, da bolsa ou do IVS.

Tabela em `A5_tabela_08_estudo_evento_proporcional.csv`; figura em `A5_figura_05_estudo_evento_proporcional.png`.

## 3. Escala em nível: sensibilidade explicitamente frágil

A especificação em nível continua publicada, mas **não** como forma primária, porque é frágil a duas coisas que nenhum artefato testava antes.

- Em março/2026, a diferença ajustada em nível é 0.500 especialista (EP 0.2469, p=0.0437 na convenção com efeitos fixos absorvidos; EP 0.2340 e p=0.0334 na convenção anterior). Teste conjunto pré-referência: F=1.031, p=0.420.
- **Composição de cursos.** Sem o curso 14 o coeficiente cai para 0.200 (p=0.366); restrito aos oito cursos com CBO estritamente 1:1, cai para 0.121 (p=0.608). Na escala proporcional os mesmos recortes dão 0.0592 (p=0.0043) e 0.0570 (p=0.0100). O leave-one-curso-out completo, nas duas escalas, está em `A5_tabela_09_leave_one_curso_evento.csv`.
- **Mês de referência.** Junho/2025 é o ponto mais baixo do caminho pré. Contra a média dos doze meses pré estimados, o coeficiente em nível de março/2026 é 0.405 (EP 0.297, p=0.174); na escala proporcional, 0.0633 (EP 0.0232, p=0.0067). Todas as referências alternativas estão em `A5_tabela_10_sensibilidade_referencia.csv`.

O curso 14 mede todos os radiologistas do município, não a competência específica do curso, e é o que sustenta o coeficiente em nível. A tabela de nível permanece em `A5_tabela_07_estudo_evento_atracao.csv` e a figura em `A5_figura_04_estudo_evento_atracao.png`.

Nomenclatura: os dez cursos da amostra confirmatória têm **CBO não compartilhado entre cursos** do PMM-E, e não "CBO unívoco". Apenas 8 deles têm mapeamento estritamente 1:1; os cursos 14 (MULTIESPECIALIDADE_EXCLUSIVA) e 16 (FAMILIA_PATOLOGIA) agregam mais de um CBO na própria ponte. A ponte não foi alterada.

## 4. Graus de liberdade dos efeitos fixos absorvidos

O ajuste roda OLS sobre variáveis já residualizadas, e a correção de pequenas amostras do statsmodels conta apenas os 25 regressores visíveis, ignorando os 1547 parâmetros de efeito fixo absorvidos. Na convenção de `reghdfe`/`fixest`, com `K` incluindo os efeitos fixos, o erro-padrão do coeficiente em nível de março/2026 passa de 0.2340 para 0.2469 e o `p` de 0.0334 para 0.0437.

As duas convenções são publicadas lado a lado: colunas sem sufixo preservam os números já divulgados; colunas com sufixo `_gl_fe` usam a convenção correta e são as que devem ser citadas. O parâmetro correspondente em `model_utils.fit_absorbed_ols` é opt-in, de modo que os scripts da versão agregada do ciclo 1 permanecem inalterados.

## 5. Construção, maturidade e censura

O painel `A5_painel_T0.parquet` tem 1.184 células município–curso em 368 municípios e 26 competências (junho/2024 a julho/2026), 30.784 linhas; a amostra confirmatória tem 587 células em 295 municípios. O estoque nunca é censurado; `n_entradas_6m` é indisponível nas seis primeiras competências, `n_saidas_confirmadas_3m` nas três últimas, e a presença da coorte de entrantes é madura até janeiro/2026. A coorte de 202603 não tem seis meses de seguimento, por isso `presentes_6m` fica **NaN**, e não zero, em `A5_cross_section_6m.csv`, com o marcador `presentes_6m_censurado` (item B-1). Modo de obtenção do painel nesta execução: `reestimado_do_painel_T0_congelado`. Ver `A5_manifesto_maturidade_censura.json` e `A5_tabela_00_construcao_steps.csv`.

## 6. Trajetória agregada

Estoque médio por célula: 13.05 em junho/2024, 13.61 na referência de junho/2025, 14.65 em março/2026 e 15.20 em julho/2026. Entre junho/2025 e março/2026, a variação média nas 1.184 células é 1.04 (mediana 0.0). Com atração (N=378), o estoque médio vai de 21.6 para 23.6; sem atração (N=806), de 9.8 para 10.4. Os grupos diferem muito em nível antes da oferta, o que é seleção, não efeito. Ver `A5_tabela_01b`, `A5_tabela_01c`, `A5_tabela_02` e `A5_figura_01/02`.

## 7. Influência e robustez dos modelos secundários

No `delta_minimal` (variante primária de efeito fixo), a exclusão sucessiva de cada UF e de cada curso move o coeficiente de atração dentro de 0.235 a 0.940 sd 0.111; leave-one-município: base 0.506, faixa 0.391 a 0.623, com os três municípios mais influentes 355710 (Δ 0.12, DFBETA 0.47), 522045 (Δ -0.11, DFBETA -0.46), 355370 (Δ 0.07, DFBETA 0.28). Ver `A5_tabela_04_leave_one_out.csv` e `A5_tabela_05_influencia_municipal.csv`. Validação preditiva por município (GroupKFold, 5 dobras): `delta_minimal` com R² fora da amostra -0.315 contra 0.933 dentro; `estoque_6m_minimal` -0.078 contra 0.876. Ver `A5_tabela_06_validacao_preditiva.csv`.

## 8. Multiplicidade

Nenhuma correção de multiplicidade existia em A5 até 16/09/2026 (item B-5). As famílias agora declaradas são: os 25 coeficientes de evento de cada par amostra–escala, com q de Benjamini–Hochberg nas colunas `q_fdr_bh` e `q_fdr_bh_gl_fe` das tabelas 07 e 08; e o coeficiente de atração nos cinco desfechos de corte transversal, separadamente para `minimal` e `full`, na coluna `q_fdr_atracao` das tabelas 03 a 03e. Para março/2026 na escala proporcional da amostra confirmatória, q = 0.0034; em nível, q = 0.3638. Os dois modelos `full` de estoque e de variação são o mesmo estimador por Frisch–Waugh–Lovell, porque a especificação inclui o estoque de referência, e são contados como uma evidência (item C-9).

## 9. Distribuição e diagnósticos secundários

Na amostra confirmatória, a variação junho/2025–março/2026 tem mediana 0.0 e máximo 211. Entre células com atração, a média é 2.29, a mediana 1.0 e 57.7% apresentam aumento; sem atração, os valores são 0.55, 0.0 e 32.5%.

As regressões de nível, cobertura, novos vínculos mensais após washout, presença da coorte e validação preditiva são diagnósticos secundários. Nelas, o efeito fixo de UF colapsa as unidades com menos de cinco municípios (14, 16, 25, 26, 27, 28, 32, 53) na macrorregião de saúde, com nível residual rotulado para município sem macrorregião publicada — 24 níveis na amostra confirmatória, a mesma definição do C1 em A4 (item A-1). O balde único `RESTO` anterior inflava o coeficiente de `delta_minimal` de 0.5062 para 1.2949; as três variantes estão em `A5_tabela_11_sensibilidade_colapso_uf.csv`. O estudo de evento absorve UF–mês com as 27 unidades e não passa por esse colapso. `n_entradas_6m` significa novo vínculo observado no mês após seis meses de ausência, e não entradas acumuladas ao longo de seis meses.

## 10. Limites

A unidade de inferência é o município, e a heterogeneidade por estrato tem pouca potência (capital com 18 clusters), como em A3. Entradas e saídas dependem das janelas de seis e três meses e da estabilidade de `CO_PROFISSIONAL_SUS`, sem documentação externa da chave (D-4). A presença da coorte em nível é pequena e sensível a ruído cadastral. Sem log de eventos do programa nem ponte individual, nenhum indivíduo bolsista é vinculado ao CNES. Sem regra administrativa validada (R1), nenhum salto no IVS é atribuído à bolsa.

## 11. Linguagem autorizada

Permitido: **evolução do estoque cadastral**, **trajetória diferencial associada à atração**, cobertura e novos vínculos mensais após washout. Proibido: provimento causal, retenção individual do bolsista, atividade física confirmada, efeito causal do PMM-E/bolsa/IVS, taxa por vaga ou dose recebida.

O CNES não identifica participantes do programa. Sem log completo, ponte individual e pagamentos, o A5 permanece uma análise descritiva longitudinal complementar ao resultado de implementação A4.

*Gerado em 2026-09-16 por `scripts/tema_trabalho/06_avaliar_provimento_cnes.py`.*
