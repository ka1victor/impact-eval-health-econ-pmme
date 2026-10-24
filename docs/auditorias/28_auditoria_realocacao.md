# Auditoria independente da realocação (protocolo 58)

> **Data:** 24/10/2026.<br>
> **Objeto:** commits `a6a77e7` (protocolo) e `c5e80ad` (execução):
> `scripts/rdd_bolsa/32_realocacao_bolsa.py`, `output/rdd_bolsa/R_*`, o
> [doc 57g](../06_execucao/57g_resultados_realocacao.md) e
> `tests/test_realocacao_bolsa.py`, contra o
> [protocolo 58](../06_execucao/58_protocolo_realocacao_bolsa.md).<br>
> **Veredito:** **APROVADO COM CORREÇÕES.** Mercado, exposição, regressão principal, Holm, MDE,
> sensibilidades de mercado (R1, R2) e placebos (PL1, PL2) foram reproduzidos com código próprio.
> Nenhuma estimativa mudou. As correções são de relato:
> - o sinal de R1/R_P1 (IC exclui zero) vinha com o placebo PL1 só como número solto; PL1 tem tamanho parecido
>   (−1,99 contra −2,17 p.p. por R$ 1 mil), e o texto agora diz que o sinal não é específico do mesmo curso;
> - os resultados por ciclo (C1/R_P2 e C2/R_S1 com p < 0,05, em 9 estimativas) não traziam aviso de
>   multiplicidade;
> - faltava dizer o que "inconclusivo" quer dizer (IC de −14,3 a +4,6 p.p. em R_P1);
> - o "Como ler" das figuras tinha quatro frases e uma delas ("ponto abaixo do zero... seria sinal de
>   deslocamento") contradizia a leitura pré-registrada, que exige Holm e placebos;
> - duas decisões de implementação (controle do nº de concorrentes no R7; IC pela normal) e uma frase
>   inverificável ("regra escrita antes da primeira execução") no registro de desvios.<br>
> **Proveniência dos números:** todo número citado aqui foi lido de `output/rdd_bolsa/R_estimativas.csv` e
> `R_resumo.json`. A conferência que fica no repositório é a classe `TestRecalculoIndependenteAuditoria28` de
> `tests/test_realocacao_bolsa.py`.

## 1. Ordem dos commits

`a6a77e7` toca só `docs/00_registro_mudancas.md` e o protocolo 58 (2 arquivos, 264 linhas); `c5e80ad` é o
filho direto e traz script, saídas, doc 57g e testes. O protocolo não contém nenhum coeficiente, EP ou p por
exposição. Os únicos números de dados são a contagem de células, de concorrentes e as frações de exposição (§4,
"sem nenhum outcome"). Ordem correta.

## 2. Como a auditoria foi feita

Código escrito do zero em pandas e numpy, sem importar o script 32 nem a `rdd_lib`. Leitura própria de:
`outcomes_V_celula.parquet`, `a08_ivs_2010_oficial_municipio.csv` (não o arquivo local de IVS),
`datasus_tabnet_br_regsaud.cnv` (CIR, por expressão regular), centroides do IBGE (JSON), população do Censo 2022 e
painel CNES do a09 (média 202406–202506 do `alvo_pmme` e de `generalistas`, só municípios com as 13
competências). Haversine com raio 6.371,0088 km. A regressão é MQO com EP CR1 escrito à mão
(G/(G−1) × (n−1)/(n−k)); o Holm e o MDE (2,8016 × EP × 5) também.

## 3. Recálculo

| Item | Linhas | Diferença máxima |
|---|---:|---|
| Universo: 5.135 células, 10 fora (1 sem IVS, 9 sem CIR), 5.125 no universo; 0 sem covariável | 1 | idêntico |
| Principal (CIR): n = 2.875, 227 CIR; coef e EP de R_P1, R_P2 e R_S1 | 6 | 4e-12 |
| p (normal) das três saídas | 3 | 6e-10 |
| MDE por R$ 5 mil de R_P1 (0,13502) e R_P2 (0,68431) | 2 | 1e-9 |
| Holm das duas primárias (0,62423; 0,76020) | 2 | 1e-9 (arredondamento do CSV) |
| R1 (raio de 200 km, n = 4.522, 367 CIR) e R2 (UF, n = 4.844, 373 CIR): coef e EP de R_P1 e R_P2 | 8 | 5e-12 |
| PL1 (n = 4.864) e PL2 (n = 623): coef e EP de R_P1 e R_P2 | 8 | 4e-11 |
| Exposição E de células amostradas contra laço direto | amostra | 1e-12 |

Primeira versão do recálculo usou `pinv` sem padronizar colunas e diferiu 3e-8 em PL1/R_P2; a diferença era
condicionamento numérico da minha conta (população e estoques em escalas diferentes), não do script. Com
`lstsq` padronizado, 4e-11.

Não foram recalculados de forma independente: R3, R4, R5, R6, R7, os ciclos C1–C3 e as figuras. Ficam cobertos
só pelos testes do próprio script e pela grade completa de especificações.

## 4. Conferência contra o protocolo

| Regra do protocolo 58 | Situação |
|---|---|
| Unidade = célula aberta, ciclos 1–3, mercado = mesmo curso e ciclo na CIR | ok |
| E = bolsa média das concorrentes − própria; concorrentes excluem a própria célula | ok |
| Controles: faixa própria, spline do IVS próprio e média da spline nas concorrentes, log(1 + n), curso × ciclo, covariáveis do A4; cluster por CIR | ok |
| Holm só nas duas primárias da principal | ok (0,624 e 0,760) |
| Limiares do MDE por R$ 5 mil: 10 p.p. e 0,25 candidato | ok; MDE 13,5 p.p. e 0,684, ambos acima |
| Leitura: IC contém zero e MDE acima do limiar = inconclusivo | ok, nas duas primárias |
| Placebos: PL1 sem concorrente de outro curso e PL2 sem célula posterior ficam fora, com motivo | ok (261; 2.291 + 2.211) |
| Células excluídas contadas | ok: 5.135 = 2.875 + 2.250 sem concorrente + 10 fora do universo |
| Decisões de implementação registradas | 4 já registradas; 2 acrescentadas (§6) |

A diferença 2.875 contra 2.876 do §4 do protocolo é a célula sem IVS oficial, que o §4 já dizia ficar fora; o
desvio 1 do doc a explica.

## 5. Integridade

- `natureza_dos_dados = EMPIRICO` em todas as linhas de `R_estimativas.csv` e `R_variacao_exposicao.csv` e no
  resumo; estatuto `EXPLORATORIO_REALOCACAO`.
- O script não contém `ivs_ipea_2010_municipios`, e o resumo não lista esse arquivo entre as entradas.
- `data/` sem diferença entre `c4c183a` e o HEAD (`git diff --stat -- data` vazio).
- A6: `scripts/tema_trabalho/07_red_team_sintese.py` foi reexecutado e regravou o manifesto byte a byte igual
  ao commitado (só a linha do script 32 em relação ao pai).
- Nenhuma coluna ou texto com identificador de candidato; as saídas são contagens por célula.
- Figuras: só rótulos de eixo e ticks; sem título, anotação nem texto de leitura embutido.

## 6. Defeitos e correções

| # | Defeito | Correção |
|---|---|---|
| 1 | R1/R_P1 exclui zero e o doc só citava o PL1 em coeficiente e p, sem pôr os dois lado a lado | frase gerada pelo script: R1/R_P1 −2,17 p.p. contra PL1/R_P1 −1,99 p.p. (p = 0,065), "não é específico das concorrentes do mesmo curso e não é lido como deslocamento" |
| 2 | Resultados por ciclo sem aviso: 2 de 9 linhas têm IC que exclui zero (C1/R_P2, C2/R_S1) | parágrafo "Por ciclo" na seção 3 e aviso na seção 8; o p < 0,05 isolado não é achado |
| 3 | "Inconclusivo" sem explicação | parágrafo com os IC por R$ 5 mil e a frase "não é evidência de que não haja deslocamento, nem de que haja" |
| 4 | "Como ler" longo; frase sobre "sinal de deslocamento" destoava do §10 | dois textos de até 3 frases, em `COMO_LER` (reflete no doc e no `R_resumo.json`) |
| 5 | Desvios: faltavam o controle de n no R7 e o IC pela normal; "regra escrita antes da primeira execução" não é verificável | itens 5 e 6 acrescentados; frase trocada por "regra definida sem consultar outcome" |

Estimativas, figuras e CSVs não mudaram (hashes iguais). Mudaram `R_resumo.json` (textos de como-ler e
desvios) e o doc 57g, regenerados pelo script.

## 7. Linguagem

Sem "não há deslocamento". Leitura pré-registrada "inconclusivo" nas duas primárias. O sinal de R1 vem com o
PL1. Por ciclo não é lido como achado. O pacote do corte e a condição "vagas abertas" aparecem em
estimando, leitura e limites. Um ponto que o relato deve manter: o ponto central de PL1/R_P1 por R$ 5 mil
(−10,0 p.p.) é maior que o da principal (−4,9 p.p.); a principal não se distingue de um placebo.

## 8. Testes

`python -m pytest tests/test_realocacao_bolsa.py tests/test_pipeline_rdd_bolsa.py`: 42 passam (36 antes, mais
6 da `TestRecalculoIndependenteAuditoria28`: amostras e exposição, principal, Holm e leitura, PL1 e PL2, texto
do doc, "Como ler" curto e figuras sem texto). Não foram rodados `run_all.py` nem a suíte inteira.
