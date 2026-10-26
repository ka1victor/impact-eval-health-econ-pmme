# 34. Auditoria independente do protocolo 60, parte B: oferta local depois da chegada (H4)

> **Data:** 26/10/2026.<br>
> **Objeto:** o retrato `886ac00` (branch `wip-a20c7726f13d92050`, "WIP (não auditado)"):
> `scripts/rdd_bolsa/37_oferta_local_chegada.py`, `output/rdd_bolsa/OL_estimativas.csv`,
> `OL_ligacao_municipio.csv`, `OL_resumo.json`, `OL_figuras/`, o
> [doc 57k](../06_execucao/57k_resultados_oferta_local.md) e `tests/test_oferta_local_chegada.py`, contra a
> parte B do [protocolo 60](../06_execucao/60_protocolo_equivalencia_e_oferta_local.md).<br>
> **Veredito:** **APROVADO COM CORREÇÕES.**
> - Nenhum número mudou.
> - O ATT médio do pós, o EP, o IC, o p, o Wald do pré, o Holm, o BKY e os θ(e) dos cinco outcomes foram
>   recalculados com código próprio. Diferença máxima: 2e−15. A grade de Rambachan–Roth e a ruptura de B1,
>   B2 e B3 batem com a `honestdid_lib` alimentada com β e Σ próprios.
> - A leitura pré-registrada se sustenta: nenhuma primária sobe com pré que passa **e** ruptura M̄ ≥ 1.
> - O retrato estava inconsistente: doc e figuras gerados por uma versão anterior do script, e três testes
>   falhando. As correções (seção 5) são de texto, rótulo, figura e teste. Foram feitas no script 37 e no
>   teste, e as saídas foram regeneradas pelo script.<br>
> **Proveniência dos números:** lidos de `output/rdd_bolsa/OL_*` depois da correção. O recálculo da auditoria
> ficou fora do repositório (scratchpad), como nas auditorias 30 e 32. A conferência que fica no repositório é
> `TestCorrecoesAuditoria34` em `tests/test_oferta_local_chegada.py`, junto com os recálculos que o teste já
> fazia.

## 1. Sincronização e ordem dos commits

- O `git merge --ff-only wip-a20c7726f13d92050` pedido não era possível. O worktree já tinha sete commits
  depois de `f47624f` (parte A do protocolo 60, auditoria 32, protocolo 61 e banca 2). O retrato foi trazido
  com `git merge --no-ff`.
- Houve conflito em cinco arquivos: `run_all.py`, `tests/README.md`, `tests/test_pipeline_rdd_bolsa.py`,
  o manifesto A6 e o registro de mudanças. Todos eram linhas acrescentadas pelos dois lados (36 e 37) e foram
  resolvidos mantendo as duas.
- O protocolo 60 não mudou desde `f47624f`. O SHA-256 do texto atual (`4c7cb1d0…`) é igual ao gravado em
  `OL_resumo.json`.
- O retrato é um commit só, sem commits intermediários. Por isso não dá para conferir a afirmação do doc 57k
  de que os esclarecimentos foram fixados antes de abrir os resultados por tempo de evento (observação O1).

## 2. Como a auditoria foi feita

O código foi escrito do zero. Não importa os scripts 37 e 22, nem o 21 e o 14 que eles importam. Lê direto:
- o a08 e a população do Censo 2022 (universo U);
- `outcomes_V_municipio` (célula em algum ciclo);
- a lista nominal, só nas colunas `co_ibge`, `dt_inicio_atividade` e `ciclo`;
- a lista de ativos, só em `ciclo`, `co_ibge` e `dt_inicio_atividade`;
- o painel a09, o manifesto a09 (CBO-alvo), o a16 (`painel_vinculo_mes`, `chaves_origem`) e a X1.

O que foi refeito:
- **Amostra e coortes:** U com célula em algum ciclo, menos os tratados da lista nominal sem célula nos
  ciclos 1 e 2. Coorte g = mês da menor `dt_inicio_atividade`. Quem não é coorte e tem início na lista de
  ativos até 202608 sai dos controles a partir desse mês.
- **Callaway–Sant'Anna:** ATT(g, t) com base g − 1 e controles G < 0 ou G > max(t, b), com Y observado em t
  e b. θ(e) com pesos de coorte e função de influência com o termo dos pesos.
- **Inferência:** bootstrap de Mammen com B = 9.999 e semente 20261026, EP pelo IQR; Wald do pré com
  IF'IF/N².
- **Ajustes múltiplos:** Holm escrito de novo. BKY pelo procedimento de dois estágios de Benjamini, Krieger e
  Yekutieli, com q-valor na grade de 0,001.
- **B3:** subtração refeita a partir do a16.
- **Rambachan–Roth:** a `honestdid_lib` (permitida pelo pedido), alimentada com β e Σ calculados aqui. Para
  conferir a ruptura de forma independente da biblioteca, foi feito um limite plug-in por diferença do pré
  (seção 3.3).

## 3. Recálculo

### 3.1 Portões

| Portão | Gravado | Recálculo |
|---|---|---|
| Coortes trimestrais do D2 (municípios / especialistas): 2025-07, 2025-10, 2026-01, 2026-04 | 130/894, 34/197, 47/150, 104/226 | iguais a `K_D2_resumo.json`; mesmos 315 tratados que a amostra do D2 com chegada até 202608 |
| Coortes mensais | 130, 4, 29, 1, 1, 46, 84, 20 (2025-09 a 2026-06) | iguais |
| Amostra: U com célula / excluídos / municípios / tratados / controles que saem / nunca tratados | 1.039 / 2 / 1.037 / 315 / 80 (1 em 2025-09, 79 em 2026-08) / 642 | iguais |
| B1 e B2 = F3.1 e F3.3 do E7 em 202506 | diferença 0; 4 ausentes em B2 | mesma definição no `CATALOGO` do 14: `n_vinculos` e `horas_sus_semanais` do grupo `alvo_pmme` ÷ população 2022 × 10 mil |

O painel a09 é balanceado: 5.565 municípios × 27 competências em cada grupo, com zeros explícitos. Célula
ausente na fonte só aparece como NaN de hora em branco. Não há zero imputado.

### 3.2 ATT médio do pós, pré e ajustes

Unidades por 10 mil hab. (Censo 2022). IC 95% pelo bootstrap. As colunas "recálculo = gravado" valem para
todos os campos da linha. Diferença máxima entre recálculo e gravado: 2e−15 nos θ(e), no ATT, no EP, no
Wald e nos p.

| Id | Papel | ATT médio do pós | EP | IC 95% | p | p Holm / q BKY | Wald do pré (5 gl), p | Ruptura M̄ (cond. / híbr.) |
|---|---|---|---|---|---|---|---|---|
| B1 vínculos | primária | +0,398 | 0,082 | [+0,24; +0,56] | 1,3e−6 | 2,2e−6 (Holm) | 6,90; 0,228 | 0 / 0 |
| B2 horas SUS | primária | +7,00 | 1,44 | [+4,19; +9,82] | 1,1e−6 | 2,2e−6 (Holm) | 10,10; 0,072 | 0 / 0 |
| B3 horas SUS dos outros | secundária | +1,88 | 0,91 | [+0,10; +3,66] | 0,038 | 0,040 (BKY) | 6,10; 0,297 | 0 / 0 |
| B4 horas totais | secundária | +7,27 | 1,43 | [+4,47; +10,06] | 3,6e−7 | 0,001 (BKY) | 8,81; 0,117 | 0,61 / 0,60 |
| B5 generalistas (placebo) | secundária | −0,13 | 0,13 | [−0,39; +0,13] | 0,339 | 0,128 (BKY) | 1,93; 0,859 | 0 / 0 |

- **Holm:** só entre B1 e B2. Os dois p ajustados ficam iguais (2,2e−6), porque o maior p é menor que o dobro
  do menor.
- **BKY:** só em B3, B4 e B5.
- **Leitura recalculada:** B1 e B2 "sobem" (ATT > 0 e Holm < 0,05) e o pré passa (p ≥ 0,05). Mas a ruptura
  fica abaixo de 1 nos dois métodos. Pela regra do protocolo, não há "associação da chegada com mais oferta
  cadastrada local". B3 não cai.

### 3.3 Rambachan–Roth (Δ^RM, média do pós)

A grade inteira de B1, B2 e B3 (M̄ = 0; 0,5; 1; 1,5; 2), nos dois métodos, bate com o gravado (diferença
máxima 7e−15), assim como a ruptura (0 nos três). O conjunto identificado da biblioteca confere com a conta
fechada: com 7 meses do pós, o pior viés da média é 4 · M̄ · (maior |1ª diferença| do pré).

| Id | Maior 1ª diferença do pré | Conjunto identificado em M̄ = 1 | IC robusto em M̄ = 0 (cond.) | IC convencional | Limite plug-in em M̄ = 1 | Ruptura plug-in (aprox.) |
|---|---|---|---|---|---|---|
| B1 | 0,131 | [−0,13; +0,92] | [−0,20; +1,02] | [+0,24; +0,56] | [−0,63; +1,47] | 0,34 |
| B2 | 1,345 | [+1,62; +12,38] | [−0,25; +14,54] | [+4,19; +9,82] | [−5,20; +18,60] | 0,50 |
| B3 | 1,204 | [−2,93; +6,70] | [−3,08; +6,39] | [+0,10; +3,66] | [−9,16; +12,34] | 0,01 |

**Limite plug-in.** Para cada diferença s do pré, l'β_pós ∓ 4M̄|Δβ_s| ∓ 1,96 EP, com EP pela Σ analítica,
tomando o pior s. É uma aproximação, não um teste com cobertura garantida. Serve só para ver se a conclusão
depende da biblioteca.

O que isso mostra:
- **A leitura não depende da biblioteca.** Em M̄ = 1 o IC inclui zero em B1, B2 e B3 na biblioteca e no
  plug-in. Em B1, o conjunto identificado em M̄ = 1 já contém zero mesmo sem erro amostral.
- **A ruptura 0 de B1 e B2 é, em boa parte, perda de potência.** Em M̄ = 0 o conjunto identificado é um ponto,
  e o IC convencional exclui zero com folga. Mesmo assim, o IC robusto de ARP já inclui zero, com 2,6 vezes a
  largura do convencional em B2. É o achado A1 da auditoria 30. A ruptura aproximada fica entre 0,3 e 0,5:
  ainda abaixo de 1. O doc não dizia isso e a tabela mostrava "0,00 / 0,00" sem contexto (achado M3).
- **Não monotonicidade em B2.** Em M̄ = 0,5 o IC exclui zero; em M̄ = 0 e em M̄ = 1, não. O script já relatava.

### 3.4 Construção do B3

| Item | Gravado | Recálculo |
|---|---|---|
| Vínculos dos ligados (regra D1, ciclos 1 a 3), SUS, CBO-alvo | 141.813 | 141.813 |
| Com hora em branco | 0 | 0 |
| Registros da X1 dos ciclos 1 e 2 com posto nos tratados / não ligados | 1.479 / 84 (5,7%) | 1.479 / 84 (5,68%) |
| Municípios com algum não ligado / com todos não ligados / sem registro | 53 / 10 / 0 | 53 / 10 / 0 |
| Parcela das horas SUS das CBO-alvo subtraída, agregada, pré / pós | 2,7% / 3,2% | 2,696% / 3,225% |
| ATT médio do pós de B3 | +1,882 | +1,882 |

**Regra do protocolo.** A subtração segue o protocolo: só horas SUS (ambulatorial + hospitalar,
`TP_SUS_NAO_SUS = 'S'`), em CBO-alvo, de médicos ligados, em estabelecimento do município do outcome, mês a
mês. Médico não ligado não é subtraído. Hora em branco deixaria B3 ausente; não houve nenhuma. Nenhuma célula
tem subtração maior que B2: o script para se tiver.

**Duas escolhas do agente, declaradas como esclarecimento e conferidas:**
1. **Conjunto fixo de pessoas.** Os ligados são subtraídos em todos os meses, inclusive antes do início. É a
   leitura certa para um teste de deslocamento. Subtrair só depois do início criaria uma queda mecânica.
2. **Município do outcome.** "Do próprio município" foi lido como o município do outcome, não o do posto do
   médico. Por isso 61,5% das horas subtraídas são de vínculos fora do município do posto do médico, como em
   Cacoal (RO), onde 14 a 17 médicos ligados têm vínculo e um só tem posto lá. A leitura é defensável e está
   no esclarecimento "B3: quem é subtraído".
   - **Sensibilidade da auditoria:** subtraindo só no município do posto, B3 = +2,00 [+0,10; +3,89], p = 0,039,
     pré p = 0,277. A leitura é a mesma (achado B2).

## 4. Fidelidade ao protocolo 60, parte B

| Regra | Situação |
|---|---|
| Município × mês, 202406–202608, nenhum mês ≥ 202609 | ok: o painel é filtrado na leitura e conferido, e o a16 é conferido contra o manifesto. O recálculo afirma o mesmo |
| Tratamento: mês de início do 1º médico (lista nominal, ciclos 1 e 2, como no D2) | ok. A coorte mensal em vez da trimestral do D2 é esclarecimento datado; o portão confere o trimestre |
| Controles: ainda não tratados com célula em algum ciclo, inclusive o ciclo 3 antes do início | ok. Inclui os nunca tratados no horizonte (642), como no `notyettreated` usual. Os 79 do ciclo 3 saem em 202608 |
| CS, base g − 1, agregação por e, Mammen por município, semente 20261026, e ∈ [−6, +6] | ok |
| Outcomes B1–B5 por 10 mil hab. (Censo 2022), definições do F3 do E7 | ok: portão 2 e conferência no catálogo do 14 |
| Holm em B1 e B2; BKY nas secundárias | ok |
| Wald do pré; Δ^RM em M̄ ∈ {0; 0,5; 1; 1,5; 2}, condicional e híbrido | ok |
| B3 só com ligados, horas SUS, CBO-alvo, município, mês; não ligados como limite | ok; fração relatada (5,7%) e limite no §7 do doc |
| Ausência não vira zero | ok |
| Leitura pré-registrada | ok nas categorias. "Ruptura ≥ 1" é exigida nos dois métodos: mais conservador, e aqui indiferente (as duas rupturas são 0) |

**Esclarecimentos datados.** São sete, todos 2026-10-26: coorte mensal, amostra, ciclo 3 nos controles, B3,
B4, regras de leitura e Rambachan–Roth. Nenhum muda o protocolo. Todos são honestos sobre o que fazem.

## 5. Achados e correções

| # | Gravidade | Achado | Correção |
|---|---|---|---|
| M1 | média | **Retrato inconsistente.** O script tinha sido editado depois de gerar o doc e as figuras. Ficaram defasados: os blocos `leitura`, `principal` e `rr` do doc 57k (a tabela dizia "primaria" e "hibrido"; a leitura dizia "p de Holm = < 0,001" e "B3 fica acima do comparável, o contrário de um deslocamento") e os três PNG (título com "p = < 0,001"). `pytest tests/test_oferta_local_chegada.py` falhava em 3 de 19: o doc diferia do gerado; o fixture sintético não tinha as colunas `e` e `Mbar`, que a leitura nova usa; e `.str` era aplicado a uma coluna `nota` toda vazia, lida como float | Script 37 rodado de novo (saídas e doc regenerados). Fixture com `reindex(columns=COLUNAS_EST)`. `fillna("")` antes do `.str`. O CSV e a ligação saíram com o mesmo SHA-256 do retrato: os números são os mesmos |
| M2 | média | **Figuras.** Nas três figuras, o "Como ler" passava da borda direita: palavras cortadas ("(acima", "Barra ="). Na de B3, o texto encostava na legenda | Quebra em 155 caracteres a 11 pt (`LARGURA_COMO_LER`) e legenda numa linha só, a 11 pt. Conferido nos três PNG regenerados. O "Como ler" ganhou a frase "se eles já sobem em direção ao zero, a diferença vinha crescendo antes da chegada, e a do pós não pode ser atribuída a ela", porque é o que se vê em B1–B3 |
| M3 | média | **Ruptura 0 sem contexto.** Em B1 e B2 o IC convencional exclui zero com folga, e o IC robusto em M̄ = 0 inclui zero por pouca potência do teste de ARP (seção 3.3; auditoria 30, A1). Lida sozinha, "ruptura 0,00" sugere um pré muito pior do que o que se vê | Nota gerada `nota_rm_potencia` na leitura. Ela diz que a ruptura 0 vem em boa parte da potência, que fica como a biblioteca define, e que em M̄ = 1 o IC inclui zero nos dois casos, de modo que a leitura não muda |
| M4 | média | **Linguagem.** "Os vínculos de especialistas (B1) ficaram maiores do que nos comparáveis" descreve nível, mas o ATT compara a mudança desde o mês −1. Perto de "aumento", isso convida a ler "a chegada aumentou os vínculos" quando a leitura pré-registrada não permite. Na versão do script, o B3 positivo dizia só "não há sinal de deslocamento", sem impedir a leitura de atração | Frases por outcome: "a mudança em X (Bk) foi maior do que nos comparáveis, mas a ruptura M̄ fica abaixo de 1". No B3: "Isso também não é lido como atração de outros especialistas pela chegada: sem ruptura M̄ ≥ 1, a diferença é compatível com uma tendência que já vinha de antes da chegada" (só quando a ruptura de B3 é < 1) |
| B1 | baixa | Tabela do portão com "0.0e+00" (ponto decimal) e rótulos tirados dos nomes das chaves ("coortes d2 refeitas iguais ao resumo", "municipios") | `ROTULO_CONFERENCIA` e vírgula decimal |
| B2 | baixa | O B3 subtrai os ligados em qualquer município onde tenham vínculo (61,5% das horas fora do posto). O protocolo admite as duas leituras de "do próprio município" | Sem correção: escolha declarada no esclarecimento. A sensibilidade da auditoria (só o município do posto) dá a mesma leitura (seção 3.4) |

**Mudanças no código e nos testes:**
- **Script 37:** só textos, rótulos e a figura (`LARGURA_COMO_LER`, `como_ler`, `figura`, `gerar_leitura`,
  `nota_rm_potencia`, `ROTULO_CONFERENCIA`, `gerar_tabelas_doc`). Nenhuma conta mudou.
- **Teste:** o fixture e a nota corrigidos, e a classe `TestCorrecoesAuditoria34` (5 testes). Ela confere:
  - a leitura sem "ficaram maiores" e com "a mudança";
  - a nota de potência quando o IC convencional exclui zero e o de M̄ = 0 inclui;
  - o B3 positivo que não vira atração;
  - o "Como ler" que cabe na largura;
  - a vírgula decimal no portão.

**Hashes depois da correção:**
- `OL_estimativas.csv` (`7e14188a…`) e `OL_ligacao_municipio.csv` (`81fc8073…`): iguais aos do retrato. O
  script 37 rodado de novo reproduz os números byte a byte: B = 9.999 bootstrap, mesma semente, mesma
  bisseção.
- PNG: B1 `7632554a…` → `4abd8681…`; B2 `8cd6f15b…` → `86046934…`; B3 `caf7916f…` → `359d67a0…`.
- `OL_resumo.json`: `cbbb59bf…` → `04497d9e…`. Mudou só a chave `figuras` (hashes e "Como ler"), conferido
  chave a chave.
- Doc 57k: blocos `leitura`, `principal`, `rr`, `portoes` e `figuras` regenerados. À mão, fora dos
  marcadores, só a linha "Auditoria" no topo e o item "Tendência antes da chegada" nos limites.

**Observações sem correção:**
- **O1.** Não dá para conferir que os esclarecimentos (sobretudo as regras de leitura) foram fixados antes de
  abrir os resultados: o retrato é um commit só. Eles são conservadores ou neutros. A exigência da ruptura nos
  dois métodos não decide nada aqui, e o "sobe" pelo p de Holm é a leitura natural do protocolo.
- **O2.** **Tendência no pré.** Em B1–B4, θ(−6) a θ(−2) são todos negativos e sobem em direção ao zero: o pré
  é uma rampa. Em 2 ou 3 dos 5 meses o IC exclui zero. O Wald conjunto passa (p de 0,07 a 0,30), mas tem pouco
  poder contra rampa suave; em B2 o p é 0,072, perto do limiar. A leitura do script já diz isso (nota do pré).
  É a razão de fundo para a ruptura < 1, e o "Como ler" agora a menciona.
- **O3.** `OL_ligacao_municipio.csv` traz, por município, a soma das horas dos médicos ligados nas janelas.
  Em 113 municípios há um só registro da X1 com posto. Mas a soma inclui todos os ligados com vínculo no
  município, a fonte (CNES) é pública e não há nome, CPF, CRM, CNS nem pseudônimo. Sem correção.
- **O4.** A média do pós pesa igualmente e = 0..6. As coortes de 2026-03 a 2026-06 (150 municípios, quase
  metade dos tratados) só entram nos primeiros meses do pós. O §7 do doc já diz isso.

## 6. Linguagem

| Ponto | Situação |
|---|---|
| Associação da chegada, não efeito da bolsa nem do programa como política | ok: no contraste do CSV e do resumo, no topo, nos limites, no "Como ler" e na frase final da leitura ("Tudo é ATT sob tendências paralelas da chegada, não efeito da bolsa nem da participação no programa") |
| Sem "aumento" quando o pré não passa ou a ruptura é < 1 | ok: "aumento" só aparece em "não dá para falar em aumento da oferta cadastrada local" e na pergunta. Reforçado em M4 |
| Vínculo cadastrado não é presença | ok: limites, "Como ler" e leitura |
| B3 positivo não vira "atração" | corrigido (M4) |
| Seleção da chegada (escolha do candidato e pedido do município) | ok, no §7 |

## 7. Integridade

- **`data/`.** `git diff --stat f47624f 886ac00 -- data/` vem vazio. Esta auditoria não escreve em `data/`.
- **Arquivo de IVS errado.** `ivs_ipea_2010_municipios` não aparece nos scripts 37, 22, 21 e 14, na
  `honestdid_lib` nem na `rdd_lib` (grep). O universo vem do a08 oficial, e o IVS não entra como variável.
- **Meses.** Nenhum mês ≥ 202609 é lido:
  - a09 filtrado `< 202609` e conferido;
  - a16 conferido contra as competências do manifesto;
  - lista nominal sem início ≥ 202609 (conferido).
  A lista de ativos tem 2 inícios em 202609, que não são CNES e não são usados: só inícios até 202608 tiram
  controles.
- **Identificadores.** Nenhuma coluna ou valor com nome, CPF, CRM, CNS, `id_prof` ou pseudônimo em
  `OL_estimativas.csv`, `OL_ligacao_municipio.csv`, `OL_resumo.json` e no doc. `id_prof` só aparece no resumo
  como nome de coluna de entrada, na descrição das chaves.
- **Saídas de outros blocos.** O retrato só toca `OL_*` e uma linha do manifesto A6. Depois de rodar o
  script 37 nesta auditoria, `git status` mostra só `OL_*`, o doc 57k, o script e o teste. O gerador do A6
  (`scripts/tema_trabalho/07_red_team_sintese.py`) foi rodado depois do merge e regravou o manifesto byte a
  byte igual ao da resolução do conflito (passos 36 e 37, nessa ordem, depois do 34).
- **Hashes de proveniência.** As entradas, as saídas e as figuras de `OL_resumo.json` batem com os arquivos
  (`test_hashes`).
- **Rótulo.** `natureza_dos_dados = EMPIRICO` e `estatuto = PROTOCOLO_60_POS_RESULTADO` em toda linha e no
  resumo.

## 8. Testes

Cada execução foi gravada em log, e o código de saída foi conferido. A suíte inteira e o `run_all.py` não
foram rodados.

| Comando | Resultado | Código de saída |
|---|---|---|
| `pytest tests/test_oferta_local_chegada.py` (retrato, antes das correções) | 16 passam, 3 falham (M1) | 1 || `python3 scripts/rdd_bolsa/37_oferta_local_chegada.py` (duas vezes, depois das correções) | portões aprovados; mesmos ATT; CSV iguais ao retrato | 0 |
| `pytest tests/test_oferta_local_chegada.py` (depois das correções) | 24 passam | 0 |
| `pytest tests/test_integridade_dados.py` | 4 passam | 0 |
| `pytest tests/test_pipeline_rdd_bolsa.py` | 15 passam | 0 |

## 9. Leitura para a banca

Nos municípios que receberam o 1º médico do PMM-E, a oferta cadastrada de especialistas cresceu mais nos 6
meses seguintes do que nos que ainda não tinham recebido: +0,40 vínculo e +7,0 horas SUS semanais por 10 mil
habitantes. Mas esses municípios já vinham crescendo mais antes da chegada. Com uma tendência do tamanho da
que se vê antes, a diferença deixa de se distinguir de zero. Por isso a regra combinada antes não permite
dizer que a chegada aumentou a oferta local. Também não há sinal de que os outros especialistas tenham saído:
as horas deles não caíram. Isso é associação da chegada, medida em vínculo cadastrado, não efeito da bolsa nem
do programa.
