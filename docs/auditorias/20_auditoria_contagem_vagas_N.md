# Auditoria independente da família N (protocolo 48, doc 49)

> **Data:** 19/10/2026.<br>
> **Objeto:** commit `c47380e`, com `scripts/rdd_bolsa/23_estimar_contagem_vagas.py`,
> `output/rdd_bolsa/N_estimativas.csv`, `N_resumo.json`, `N_figuras/`,
> [`06_execucao/49`](../06_execucao/49_resultados_contagem_vagas_preenchidas.md) e
> `tests/test_contagem_vagas.py`, contra o protocolo congelado
> [`06_execucao/48`](../06_execucao/48_protocolo_contagem_vagas_preenchidas.md).<br>
> **Veredito:** **APROVADO COM CORREÇÕES.** Os números do protocolo foram
> reproduzidos de forma independente. As correções não mudam nenhuma das 2.173
> linhas originais de `N_estimativas.csv`: elas acrescentam 48 linhas, refazem as
> figuras e corrigem a prosa do doc 49.<br>
> **Proveniência dos números:** os valores citados aqui foram lidos de
> `output/rdd_bolsa/N_resumo.json` e `N_estimativas.csv` depois da correção. A
> conferência independente está versionada em `tests/test_contagem_vagas.py`
> (classe `TestRecalculoIndependenteAuditoria20` e testes marcados "auditoria 20").

## 1. Como a auditoria foi feita

O código de conferência foi escrito do zero. Ele não importa o script 23 nem a
`rdd_lib`:
- lê só `output/rdd_bolsa/outcomes/outcomes_V_municipio.parquet` e `outcomes_V_celula.parquet`;
- usa como running variable a coluna `ivs_2010_oficial`, em milésimos;
- não lê `data/ivs_ipea_2010_municipios.csv`.

Estimação:
- MQP do statsmodels com kernel triangular e h = 0,050;
- EP HC1 por corte e CR1 por município nos empilhados;
- empilhado com intercepto e inclinações por grupo × lado e salto comum, na
  mesma convenção do E6 (`13_estimar_E6_funil.py`, `_ciclos_empilhados`);
- com ciclos e cortes empilhados, o grupo é ciclo × corte, e os interceptos por
  grupo contêm o efeito fixo de ciclo do protocolo.

O IC honesto foi refeito à parte, com quártica por lado, M máximo de |f''|,
variância por vizinhos (J = 3), viés de Taylor e valor crítico de |N(t, 1)|.
O Poisson empilhado foi conferido contra o GLM Poisson do statsmodels com
`var_weights` = kernel e CR1.

## 2. Tabela de recálculo

| Item | Linhas | Resultado |
|---|---:|---|
| S-a principal (controle comum aos dois lados, um coeficiente por grupo), N1–N4, por corte, cortes empilhados e ciclos empilhados | 42 | tau, EP, IC, p, média abaixo, efeito relativo e MDE iguais até ~1e-13; n abaixo, n acima e n_obs idênticos |
| S-b principal (sem controle), mesmas amostras | 42 | idem |
| S-c principal (VIC, VI, NC como outcome) em V1–V3 e empilhados | 36 | idem |
| Decomposição total = via oferta + S-a | 42 amostras | "via oferta" recalculada e igual; resíduo da identidade ~1e-13 |
| Holm das quatro linhas S-a empilhadas | 4 | igual ao do `statsmodels.multitest` |
| IC honesto: S-b V1 0,300, S-b V2 0,400, S-a (residualizado) V1 0,300 e V2 0,300 | 4 | M, EP, viés máximo e IC iguais a 6 casas |
| S-d empilhado (offset e covariável), N1 ciclos e cortes | 2 | tau e EP iguais a 8 casas |
| Verificação do cadastro reserva, por ciclo | 3 | todas as contagens iguais (células, só CR, alocados, alocados em célula só de CR, células acima das imediatas e de imediatas + CR, municípios com N1 > imediatas) |

Linha principal da família, S-a com ciclos e cortes empilhados, lida de
`N_resumo.json`:

| Outcome | População | Salto | IC 95% (CR1) | p | p Holm | Média abaixo | Salto / média | MDE |
|---|---|---:|---|---:|---:|---:|---:|---:|
| N1 | V1+V2+V3 | −0,756 | [−1,442; −0,070] | 0,031 | 0,124 | 2,156 | −35,1 % | 0,980 |
| N2 | V1+V2+V3 | −0,311 | [−0,658; +0,035] | 0,078 | 0,235 | 1,513 | −20,6 % | 0,495 |
| N3 | V1+V2 | −0,351 | [−0,873; +0,171] | 0,188 | 0,376 | 2,313 | −15,2 % | 0,746 |
| N4 | V1+V2 | −0,209 | [−1,338; +0,920] | 0,717 | 0,717 | 2,426 | −8,6 % | 1,613 |

Sem controle (S-b), N1 V1+V2+V3: −1,453 (p = 0,048). Vagas oferecidas
(S-c, VIC) com ciclos e cortes empilhados: −1,73 (p = 0,438).

## 3. Achados

### 3.1 Conformes

1. **Verificação do cadastro reserva e escolha do controle.** O protocolo pede
   para verificar, antes de estimar, se um alocado da 1ª chamada pode ocupar
   vaga de cadastro reserva, e para escolher o controle por essa regra. A
   verificação usa só contagens globais por ciclo, sem nada por lado de corte.
   - Ciclo 1: há alocados em células só de cadastro reserva, e células com mais
     alocados que vagas imediatas.
   - Ciclo 2: nenhum dos dois casos.
   - Ciclo 3: há alocados em células só de cadastro reserva.
   - Os trechos dos editais 3/2025 e 28/2026 estão nos PDFs, conferido pelo teste.

   Resposta: sim. Controle principal: `vagas_imediatas + vagas_cr`; "só
   imediatas" fica como sensibilidade. A regra foi seguida.
2. **Sinal.** T = 1 para IVS > corte, e o corte fica no lado de baixo. O salto é
   o lado de bolsa maior menos o lado de bolsa menor, como diz o doc 49.
3. **Amostras e ausências.**
   - Um município do quadro não tem IVS oficial e fica fora da RDD.
   - Nenhuma vaga oferecida está ausente.
   - N3 e N4 do ciclo 3 saem NAO_EXECUTADO com o motivo da tarefa B.
   - Nenhum NaN vira zero: não há `fillna(0` no script, e o teste sintético
     confere que um controle ausente é descartado e contado.
   - Em U, o zero fora do quadro é o zero estrutural do protocolo.
4. **Rótulos.** Toda linha tem `natureza_dos_dados = EMPIRICO` e
   `estatuto = PROTOCOLO_48_POS_RESULTADO`.
5. **Determinismo.** Duas execuções seguidas do script deram arquivos
   byte-idênticos: CSV, JSON, as seis figuras e o doc 49.
6. **Manifesto A6.** A linha do script 23 em `A6_manifesto_reproducao.json` foi
   escrita à mão. Rodar o gerador `scripts/tema_trabalho/07_red_team_sintese.py`,
   que deriva os comandos da lista `STEPS` de `run_all.py`, reproduz o arquivo
   byte a byte, antes e depois das correções. Não houve violação na prática, e
   nada foi alterado.

### 3.2 Desvios declarados: julgamento

| Desvio | Julgamento |
|---|---|
| Poisson empilhado (S-d) implementado no script | aceito. Reproduz a `rdd_lib` com um corte, com falha fechada, e o GLM do statsmodels no empilhado (seção 2) |
| S-h e S-i só por ciclo × corte | aceito no mérito. Mas o protocolo pede cada linha também empilhada, e faltava a linha NAO_EXECUTADO com o motivo (correção C2) |
| "Janela mínima do E5" lida como a janela selecionada pelo E5/E6 (`E6_lr_selecao_janela.csv`) | aceito. É a regra de balanço já usada no E5 e no E6, escolhida só por covariáveis e antes dos outcomes |
| IC honesto de S-a com o coeficiente do controle fixo | aceito, porque está declarado. A incerteza do coeficiente fica de fora, o que estreita o IC. Mas o IC honesto é tão largo que isso não muda a leitura (achado 3.3.3) |
| Coeficiente do controle por grupo no empilhado | decisão registrada, sobre um ponto em que o protocolo é ambíguo. Ver achado 3.3.1 |

### 3.3 Problemas encontrados

1. **A conclusão do Holm depende do coeficiente do controle no empilhado.** O
   protocolo pede um ajuste "comum aos dois lados" e "efeito fixo de ciclo", mas
   não diz se o coeficiente das vagas oferecidas é um por grupo (ciclo × corte)
   ou um só. O script usa um por grupo. Com um só coeficiente:
   - N1 empilhado: −1,03 [−1,79; −0,28], p = 0,007, p de Holm na variante = 0,029,
     ou seja, rejeitaria zero;
   - N2: p de Holm na variante = 0,052.

   O Wald (CR1) rejeita a igualdade dos coeficientes por grupo nas quatro linhas
   (p < 0,001). A taxa por vaga varia por ciclo, e a linha por grupo é a
   defensável. Escolher a especificação agora seria seleção retrospectiva, e a
   linha principal não muda. Mas o doc 49 dizia, sem ressalva, que nenhuma linha
   sobrevive ao Holm. **Correção C1.**
2. **Faltavam S-h empilhado e S-i com ciclos empilhados.** O protocolo pede cada
   linha por corte e empilhada. Essas especificações não tinham linha própria e
   só apareciam em `desvios`. **Correção C2.**
3. **O doc 49 usava o IC honesto como argumento forte.** A regra de bolso do E6,
   aplicada a contagens, dá M entre 10^4 e 10^5 por IVS². No ciclo 1, em 0,300, o
   IC honesto sem controle vai de −68,6 a +68,1 vagas para uma média de 1,6. Por
   isso "contém zero com folga" não informa. **Correção C3.**
4. **Placebo do ciclo 2: a implicação estava genérica.**
   - O corte falso na média do segmento entre 0,300 e 0,400 do ciclo 2 (0,348)
     dá −5,64 sem controle (p = 0,010) e −1,64 com controle (p = 0,052).
   - Esse corte usa os mesmos municípios que formam o lado de cima da janela de
     0,300 no ciclo 2.
   - Esse lado tem a linha por ciclo com o sinal mais forte: S-a do ciclo 2 em
     0,300, −2,09, p = 0,027.

   O doc dizia só que "a reta local não capta bem a forma do outcome ali", sem
   tirar a consequência para o corte de 0,300 do ciclo 2 nem para o empilhado.
   **Correção C3.**
5. **Figuras.**
   - Nos dois gráficos empilhados, a terceira linha da legenda encostava no
     texto "COMO LER": a altura do texto era subestimada.
   - O rótulo "salto" ficava sobre pontos e retas em alguns painéis.
   - No empilhado, o tamanho do ponto conta linhas município × ciclo, mas a
     legenda dizia "municípios".

   **Correção C4.**

O resto da linguagem do doc 49 está correto:
- não há linguagem causal;
- S-a é dita condicional a um controle possivelmente afetado, com S-c e a regra
  fixa no código;
- o sinal negativo não é apresentado como prova de que a bolsa reduz o
  preenchimento;
- o contraste é o pacote do corte;
- os números estão em blocos gerados e conferidos pelo teste.

## 4. Correções feitas

| Id | Onde | O que mudou |
|---|---|---|
| C1 | script 23, `N_*`, doc 49 §3 e §12 | Nova variante S-a `controle_coeficiente_unico` em toda amostra empilhada, fora do protocolo (`no_protocolo = False`, rótulo `SENSIBILIDADE_AUDITORIA_20`, fora do Holm do protocolo). Nota com o Wald da igualdade dos coeficientes por grupo. Bloco `sensibilidade_coeficiente_unico_auditoria_20` em `N_resumo.json`, com Holm só na variante. Tabela e frase geradas no doc 49 (§3) e prosa dos motivos (i) e §12 ajustada |
| C2 | script 23, `N_*` | Linhas NAO_EXECUTADO com o motivo para S-h empilhado (22) e para S-i com ciclos empilhados (4). O desvio foi registrado em `desvios` |
| C3 | doc 49 §3 e §12 | Motivo (ii): o IC honesto é pouco informativo aqui. Motivo (iv): o placebo do ciclo 2 usa os municípios do lado de cima de 0,300, e o salto em 0,300 do ciclo 2, com a parte do empilhado que vem dele, não deve ser lido como descontinuidade. Tudo sem número digitado |
| C4 | script 23, `N_figuras/` | Altura do texto e da legenda recalculada, sem sobreposição (conferido visualmente nas seis figuras). Rótulo "salto" com fundo. No empilhado, a escala de tamanho diz "linhas município × ciclo", e a legenda explica isso |
| C5 | `tests/test_contagem_vagas.py` | Recálculo independente versionado das 120 linhas principais S-a, S-b e S-c e do Holm (statsmodels, a partir do parquet). Teste da variante de coeficiente único por MQP à mão. Teste das linhas NAO_EXECUTADO. Contagem de S-a e S-h por amostra atualizada |

Depois das correções:
- `N_estimativas.csv` tem 2.221 linhas: 2.171 EXECUTADO e 50 NAO_EXECUTADO;
- as 2.173 linhas anteriores são idênticas campo a campo;
- o script é determinístico, conferido em duas execuções;
- `python -m pytest -q` passa.

## 5. Números finais

Família N, linha principal do protocolo (S-a, ciclos e cortes empilhados, coeficiente
do controle por ciclo × corte):
- N1: −0,76 vaga por município (−35 % da média abaixo do corte), IC 95%
  [−1,44; −0,07], p = 0,031, Holm 0,124, MDE 0,98;
- N2 a N4: negativos, com Holm entre 0,235 e 0,717.

Nenhuma linha rejeita zero depois do Holm na especificação do protocolo. Essa
conclusão não é robusta a um coeficiente único do controle, uma restrição que o
Wald rejeita. O contraste é o pacote do corte. A leitura defensável continua
sendo a ausência de efeito positivo detectável do degrau de R$ 5 mil sobre o
número de vagas preenchidas. Não há evidência de que a bolsa reduza o
preenchimento.
