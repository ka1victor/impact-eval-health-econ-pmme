# 30. Auditoria independente do protocolo 59 (sensibilidade de Rambachan–Roth e comparação alternativa P3/P4)

> **Data:** 26/10/2026. **Commit auditado:** `b71468b` (protocolo `1cc4d68`), base `1bb109d`.<br>
> **Escopo:** doc 59 e adendo, scripts 34 e 35, `honestdid_lib.py`, `H_*`, `CA_*`, doc 57h, atualizações dos docs 57, 38 e
> 33, `run_all.py`. Código de recomputação próprio, sem importar `honestdid_lib`; scripts em memória, fora do repositório.

## 1. Ordem do protocolo

- `1cc4d68` (25/10, 16:31) precede `b71468b` (26/10, 07:09) e é o único commit de resultados. O diff 1cc4d68..b71468b no
  doc 59 só **acrescenta** o adendo ao fim (26 linhas); o texto congelado está intacto. O adendo é datado
  (25/10/2026), declara o que já tinha sido visto (H-P4 horas totais e P3-CA, antes do P4-CA), mantém o condicional puro em
  todas as linhas (`RM`, `RM_ruptura`) e põe o híbrido em colunas separadas. Não substitui o método congelado.
- Desvios no script: nenhum encontrado em janelas (P3 pré −12..−2, pós 0..9; P4 −6..−2/0..6; CA P3 −24..+9, CA P4 −12..+5),
  grades (M̄ e M/u), amostras, controles e família de Holm (4 primárias). O §6 é aplicado com as duas rupturas.
- `CA_resumo.json` grava `sha256_texto = 5a2ceafd…`, que é o hash do doc 59 **com o adendo**; o hash do texto congelado
  em `1cc4d68` é `f039e3f5…`. O campo não prova o congelamento (ver A3).

## 2. Recomputação

**Parte A (P4 horas totais; θ(e) e Σ lidos de `H_coeficientes.csv`).**

| Item | Publicado | Recomputado |
|---|---|---|
| θ(e) vs `P4_estimativas.csv` (T4.1b, D1, [−6,6]) | — | diferença máx. 5e−10; média do pós 6,6043 |
| θ(e) e EP analítico vs `K_X_estudo_evento.csv` (12.2, K_esp) | — | 5e−11 e 2e−11 |
| IC normal da média do pós | [5,34; 7,86] | [5,34; 7,86] (EP 0,643) |
| Conjunto identificado Δ^RM, M̄ = 0 / 0,25 / 1 / 2 | [6,60; 6,60] / [5,94; 7,27] / [3,95; 9,25] / [1,30; 11,91] | idêntico (PL próprio, união dos poliedros) |
| Δ^SD, FLCI, M/u = 0 / 0,1 / 0,5 / 1 | [5,15; 8,14] / [4,12; 8,40] / [0,04; 9,71] / [−3,44; 12,03] | [5,15; 8,14] / [4,12; 8,40] / [0,04; 9,72] / [−3,45; 12,03] |
| Ruptura Δ^SD | M/u = 0,50 | consistente (limite inferior 0,04 em 0,5) |
| Δ^RM, M̄ = 0, IC | condicional [2,81; 10,43]; híbrido [2,80; 10,44] | teste LF próprio (2.000 sim.): 95% [4,1; 9,1]; 99,5% [2,1; 11,1] |
| Δ^RM, M̄ = 1, IC | [1,48; 11,77] | LF 95% (300 sim., grade 0,25): [0,5; 12,8] |
| P3 K_esp, Δ^RM, M̄ = 0 | [−27,08; 56,33] | LF 95%: [−23,2; 51,8]; 99,5%: [−45,7; 73,8] |

Os IC condicional e híbrido publicados ficam entre o LF a 95% e o LF a 99,5%, como a teoria exige (o teste condicional
não pode ser mais estreito que o LF no ponto onde o híbrido trunca). Com M̄ = 1 meu LF é mais largo que o condicional, também
como esperado. A ruptura de 1,30 das horas totais é, portanto, plausível; só um valor LF mais largo, não mais estreito, aparece
nas minhas contas. A ruptura 0 do P3 K_esp se reproduz: o IC de Δ^RM em M̄ = 0 inclui zero em qualquer teste válido que usei.

**Parte B.**

| Item | Publicado | Recomputado |
|---|---|---|
| P3-CA: controles (pedido no ciclo 3, nenhuma linha priorizada do curso no município, sem chegada na lista nominal, em U) | 761 (112/99/31/14/505 nos cursos 10–14); tratados 178 | idêntico, regra reescrita por mim a partir de `ler_adesao` e da lista nominal |
| P3-CA: θ(e), e = −24..+9, CS próprio (coorte trimestral, base g − 1, controles do mesmo curso, peso = tratados) | média do pós +5,2873 | +5,2873; θ(e) idêntico, diferença máx. 4e−9 |
| P4-CA: amostra (G1 CPF+nome, r ∈ ±1,2, células com os dois lados) em `P6_amostra.parquet` | 98 candidatos, 30/68, 27 células, ciclo 1: 2 e ciclo 2: 96 | idêntico |
| P4-CA: média do pós de horas, DiD próprio com efeito fixo de célula (dummies, MQO, EP agrupado por célula, G/(G − 1)); painel de candidatos refeito pelo pipeline a partir do cache privado (lido via link simbólico para o cache do worktree do autor, sem cópia, removido ao fim) | totais +7,91 [−0,63; 16,45]; município da 1ª opção +10,92 [4,15; 17,68]; fora −3,01 [−10,14; 4,12] | +7,908 [−0,63; 16,45]; +10,917 [4,15; 17,68]; −3,009 [−10,14; 4,12]; θ(e) de e = −12..+5 idêntico (diferença máx. 3e−9) |
| Holm sobre as 4 primárias (p 0,264; 0,054; 0,004; 0,412) | 0,527; 0,162; 0,016; 0,527 | idêntico |

O painel mensal do P4-CA vem do cache privado (ausente no meu worktree; usei o do worktree do autor, só leitura). A ligação candidato–CNES e a agregação mensal são as do pipeline (que confere o painel contra `P6_amostra.parquet`, diferenças 0); o DiD e o EP são meus. P-valor por permutação não recomputado (opcional).

## 3. Linguagem e contraste

O doc 57h declara o contraste como priorização entre quem pediu (P3-CA) e alocação na 1ª opção perto do corte (P4-CA), "não é
efeito da bolsa nem da participação no PMM-E". A ressalva mecânica está no resumo e nas limitações: horas no município da 1ª
opção são em parte mecânicas (ser alocado cria o vínculo no município da vaga), "vínculo cadastrado não é presença". A
conclusão "1 de 4 primárias passa o Holm com pré válido; com a ruptura de Δ^RM ≥ 1, nenhuma" confere com as saídas. Linguagem
descritiva onde cabe; nenhuma frase causal indevida.

## 4. Privacidade

`CA_*` e `H_*` não têm colunas de nome, CPF, CNS, CRM ou `id_prof`; só estatísticas por e e por especificação (`CA_resumo.json`
cita as palavras apenas no texto de integridade). Os caches estão no `.gitignore` (`git check-ignore` confirma os dois).
`P6_amostra.parquet` tem `id_candidato` pseudônimo, é anterior a esta onda e não foi alterado.

## 5. Testes

`tests/test_comparacao_alternativa_P3P4.py`, `test_pipeline_rdd_bolsa.py` e `test_sintese_perguntas.py`: 50 passaram em 5 s.
`tests/test_honestdid.py` (rodado em segundo plano): 21 passaram em 661 s (11 min).

## 6. Achados

| # | Severidade | Achado |
|---|---|---|
| A1 | Média | O doc 57h explica o IC largo de Δ^RM em M̄ = 0 por o desvio da média poder ser "repartido em pequenos passos mensais". Em M̄ = 0 os passos são forçados a zero (o conjunto identificado é um ponto e a hipótese é paralelismo exato no pós); a largura vem da estatística sup-t sobre 2 × (nº de passos) momentos com parâmetros de perturbação, não de repartição. É um teste válido, mas pouco potente: nas horas totais o IC em M̄ = 0 é 3 vezes o IC convencional, e no P3 K_esp inclui zero embora o IC convencional [3,57; 25,11] não inclua. "Ruptura 0" do P3 é, em boa parte, perda de potência do teste, não evidência de viés. O resultado é conservador (não infla robustez). A conclusão de fragilidade do P3 se sustenta pelo Δ^SD (M/u = 0,02), que é independente do teste condicional. Sem correção no texto gerado (o 57h é gerado pelo script 34); recomenda-se reescrever a frase no script. |
| A2 | Baixa | O híbrido foi acrescentado depois de ver o IC de M̄ = 0 mais largo que o de M̄ = 0,25 na primeira linha real. Isso é decisão guiada por resultado, mas o adendo declara, mantém o método congelado em todas as linhas e o híbrido quase não muda nada (rupturas 1,30 vs 1,29; 1,90 vs 1,89; 0,78 vs 0,76; P3 0 vs 0). Sem efeito na leitura. O híbrido roda só nas linhas principais e no CA, escolha declarada. |
| A3 | Baixa | `sha256_texto` do `CA_resumo.json` (e a entrada de proveniência do 57h) referem o doc 59 já com o adendo (`5a2ceafd…`); o hash do texto congelado é `f039e3f5…`. A ordem de commits é a prova do congelamento, não o hash. Sugere-se gravar também o hash do commit de congelamento. |
| A4 | Resolvido | P4-CA recomputado com o cache privado do worktree do autor: médias do pós e ICs idênticos aos publicados (totais +7,91; município da 1ª opção +10,92 [4,15; 17,68]), θ(e) idêntico. Ressalva: a ligação e o painel mensal são do pipeline (conferidos contra o P6), não reimplementados. |
| A5 | Baixa | A data de execução gravada é 2026-10-25 e o doc 57h traz "Data: 2026-10-25", mas o commit dos resultados é de 26/10 07:09 e o registro de mudanças usa 26/10. Inconsistência de data, sem efeito. |
| A6 | Informativa | P3-CA primária: pré não passa (p = 0,009) e ressalva de sinal oposto; P4-CA horas no município da 1ª opção (Holm 0,016, pré passa) é a única que rejeita zero e é parcialmente mecânica; ruptura 0. O 57h diz isso corretamente. |

Nenhum achado exigiu correção de código ou de saída; as correções recomendadas (A1, A3, A5) tocam texto gerado pelo
script 34 e pelo manifesto e ficam para o autor.

## 7. Veredito

**Aprovado com ressalvas.** Ordem do protocolo respeitada, texto congelado intacto, adendo honesto e subordinado. Os números
de θ(e), conjuntos identificados, FLCI de Δ^SD, controles e ATT do P3-CA, DiD do P4-CA e Holm se reproduzem com código próprio; os IC de
Δ^RM publicados são coerentes com um teste LF independente (válidos e conservadores). Pende só a explicação imprecisa da largura do IC de Δ^RM (A1). Resultados continuam associativos; nenhum vira
efeito causal.

## 8. Correções posteriores (26/10/2026)

- A1: a explicação da largura do IC de Δ^RM no doc 57h foi corrigida no script 34 antes do merge.
- A3: `H_resumo.json` e `CA_resumo.json` registram agora, além de `sha256_texto` (arquivo atual, com o adendo), o
  `sha256_texto_congelado` (`f039e3f5…`), o `commit_congelamento` (`1cc4d68`) e uma nota que distingue os dois.
- A5: `DATA_EXECUCAO` dos scripts 34 e 35 passou a 2026-10-26, a data dos commits e do registro. As duas etapas foram
  reestimadas; estimativas, eventos e covariâncias saíram idênticas byte a byte, e só os campos do resumo e a data do
  57h mudaram.
