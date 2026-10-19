# G2. Viabilidade do desenho do mecanismo de alocação (P6)

> **Data:** 19/10/2026.<br>
> **Pedido:** portão G2 do doc 51 (T6.0): reconstruir a alocação publicada a partir das escolhas, notas,
> elegibilidade e vagas, com meta de ≥ 99% de concordância por ciclo e chamada.<br>
> **Estatuto:** portão de viabilidade. Não calcula contraste de outcome: nada de CNES, produção, IVS ou faixa
> da bolsa foi lido. Cortes e margens são variáveis do mecanismo.<br>
> **Gerado por:** `scripts/rdd_bolsa/G2_mecanismo_alocacao.py`. Todo número deste documento vem de
> `output/rdd_bolsa/G2_resumo.json` e é conferido por `tests/test_G2.py`.

**Veredito: `VIAVEL_PARCIAL`** (por ciclo: ciclo 1 `VIAVEL_PARCIAL`, ciclo 2 `VIAVEL`, ciclo 3 `VIAVEL_PARCIAL`).

Robustez: com capacidade efetiva e desempate publicado, a concordância fica entre ciclo 1 99,19%–99,60%; ciclo 2 99,82%–100,00%; ciclo 3 99,96%–99,96% nas variantes do mecanismo (aceitação adiada ou Boston, ordem das cotas, tipagem das vagas acrescidas).

Nota de processo: a grade de especificações, a regra de tipagem das vagas acrescidas e a regra do veredito
foram fixadas nesta execução depois de rodadas exploratórias sobre os mesmos arquivos. Não há outcome no
portão, mas as taxas de concordância não são pré-registradas.

## 1. O mecanismo dos editais

Trechos conferidos nos editais do repositório (ciclo 1: Edital SGTES/MS nº 3/2025; ciclo 3: Edital nº
28/2026; o texto do edital do ciclo 2 não está no repositório, só a página de anexos):

| Item | O que diz |
|---|---|
| 4.1.3 | até 2 locais de atuação, em ordem de preferência; no ciclo 3, a 2ª no mesmo aprimoramento da 1ª |
| 4.1.3.4 | célula de cadastro reserva não tem vaga imediata; pode recebê-la por remanejamento |
| 4.1.7 (c1) / 4.1.6 (c3) | alocação no estabelecimento indicado, observadas a ordem de classificação e as vagas |
| 5.2 | classificação pela pontuação do barema (inteira, 0 a 15) |
| 5.2.5 | desempate: mesma UF da residência (c1: ou do nascimento; c3: depois nascimento) e maior idade |
| 5.4–5.5 | cotista concorre também na ampla concorrência; vaga reservada vazia vai à ampla (remanescente de cota) |
| 5.6 | ordem: c1 = ações afirmativas, ampla, remanescentes; c3 = ampla, ações afirmativas, remanescentes |
| 5.7 | vaga imediata não preenchida pode ser redistribuída a célula de cadastro reserva com lista de espera, por priorização da SGTES (regiões com mais dificuldade de acesso e escassez) |

Mecanismo implementado: Aceitação adiada (deferred acceptance) com até 2 opções por candidato, na ordem de prioridade escolhida. Cada célula CNES × curso ordena quem a escolheu por (i) ordem da opção — quem a pôs em 1º lugar vem antes de quem a pôs em 2º —, (ii) pontuação, decrescente, e (iii) desempate. Com 2 opções, essa prioridade e sem vagas reservadas, o resultado é idêntico ao do mecanismo de Boston em duas rodadas (1ª opções primeiro, depois 2ª opções nas vagas que sobraram); com vagas reservadas os dois podem diferir, e Boston é relatado como variante. As vagas reservadas (ER, PCD) são processadas na ordem do item 5.6 de cada edital; quem se inscreve em reserva concorre também às vagas de ampla concorrência (item 5.5); vaga reservada sem candidato vai à ampla concorrência como remanescente de cota (item 5.4). Desempate do edital (item 5.2.5: mesma UF de residência ou de nascimento; maior idade) não é observável; a especificação principal usa a classificação publicada da célula, que embute esse desempate, e a sensibilidade usa sorteio.

O que o edital não escreve e os dados revelam: a classificação publicada de cada célula põe quem escolheu a
célula como 1ª opção antes de quem a escolheu como 2ª, e só depois ordena por nota. A especificação "só
nota" abaixo testa a alternativa (ditadura serial pela nota) e concorda menos.

## 2. Concordância com a alocação publicada

Concordância = proporção de candidatos cuja célula reconstruída (ou nenhuma) é igual à publicada.

| Chamada | Candidatos | Principal: capacidade efetiva, desempate publicado | Ex ante: vagas imediatas do quadro | Boston em duas rodadas | Só nota | Cotas na ordem alternativa | Vagas acrescidas todas AC | Sorteio no desempate (média; mín.–máx.) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Ciclo 1, 1ª chamada | 993 | 99,19% (985) | 74,62% | 99,60% | 93,15% | 99,19% | 99,40% | 92,55%; 90,43%–94,06% |
| Ciclo 2, 1ª chamada | 2.179 | 100,00% (2.179) | 100,00% | 99,82% | 95,04% | 100,00% | 100,00% | 92,04%; 91,10%–93,39% |
| Ciclo 3, 1ª chamada | 2.604 | 99,96% (2.603) | 93,70% | 99,96% | 97,93% | 99,96% | 99,96% | 95,81%; 95,08%–96,74% |
| Ciclo 1, 2ª chamada | 615 | 100,00% (615) | — (quadro ausente) | 100,00% | 96,75% | 100,00% | — (sem quadro) | 93,80%; 91,54%–96,10% |
| Ciclo 2, 2ª chamada | 609 | 99,84% (608) | — (quadro só com cadastro reserva) | 99,51% | 95,24% | 99,84% | 98,52% | 93,66%; 91,46%–96,06% |

Como ler: a coluna principal usa a capacidade efetiva de cada célula (as vagas imediatas do quadro,
acrescidas do que a publicação alocou acima delas) e a classificação publicada da célula como desempate. As
vagas acrescidas seguem a divisão AC/ER/PCD do cadastro reserva do quadro; a coluna "vagas acrescidas todas
AC" é a alternativa. Essa regra de tipagem foi escolhida depois de ver as divergências da 2ª chamada do ciclo
2, onde cotistas ocupam vagas de cadastro reserva; por isso a alternativa é relatada ao lado. A coluna ex ante
usa só as vagas imediatas do quadro, sem a redistribuição do item 5.7. "Boston em duas rodadas" processa
todas as 1ª opções antes das 2ª opções. A última coluna troca o desempate do edital, que não é observável, por
um sorteio (100 sorteios).

Conferências de entrada (1ª chamada): as linhas lidas aqui são as de `escolhas_candidatos.parquet`
(mesmo pseudônimo, célula, opção e nota) e as vagas são as de `outcomes_V_celula.parquet`:

| Chamada | Linhas casadas / lidas | Nota igual | Alvo igual ao E9 | Células com vagas iguais |
|---|---:|---:|---:|---:|
| Ciclo 1, 1ª chamada | 1.671 / 1.671 | 1.671 | 1.671 | 1.295 / 1.295 |
| Ciclo 2, 1ª chamada | 3.646 / 3.646 | 3.646 | 3.646 | 1.547 / 1.547 |
| Ciclo 3, 1ª chamada | 4.532 / 4.532 | 4.532 | 4.532 | 2.293 / 2.293 |

## 3. Divergências

Tipos, na ordem de atribuição: *sub judice*; redistribuição do item 5.7 (só na especificação ex ante);
vagas reservadas; efeito em cadeia de outra divergência na mesma célula; não explicada.

| Chamada | Especificação | Tipo | Candidatos |
|---|---|---|---:|
| Ciclo 1, 1ª chamada | principal | vagas reservadas (ER/PCD) | 6 |
| Ciclo 1, 1ª chamada | principal | não explicada | 2 |
| Ciclo 1, 1ª chamada | ex ante | redistribuição para cadastro reserva (item 5.7) | 250 |
| Ciclo 1, 1ª chamada | ex ante | não explicada | 2 |
| Ciclo 3, 1ª chamada | principal | *sub judice* (fora do alvo, alocado pela reconstrução) | 1 |
| Ciclo 3, 1ª chamada | ex ante | redistribuição para cadastro reserva (item 5.7) | 163 |
| Ciclo 3, 1ª chamada | ex ante | *sub judice* (fora do alvo, alocado pela reconstrução) | 1 |
| Ciclo 2, 2ª chamada | principal | não explicada | 1 |

Outras fontes de diferença, fora da comparação principal:

- Ciclo 1: o alvo é o resultado do processamento (527 classificados). Destes, 59 tiveram o local depois desconsiderado a pedido da gestão (Quadro 2, realocação). Contra só os confirmados, a mesma reconstrução concorda em 93,25%.
- Ciclo 1: 114 candidatos com "SEM PRÉ-REQUISITO" ficam fora do processamento (não classificados na publicação e na reconstrução).
- Ciclo 3: 2 linhas *sub judice*. Contando-as como alocadas, a concordância é 99,96%.
- Ciclo 2, 2ª chamada: a publicação aloca 1 candidato em duas células; a comparação usa a primeira linha publicada. O arquivo da 2ª chamada do ciclo 1 é
  a alocação preliminar (título da planilha), não a final.
- Ciclo 2: as vagas remanescentes (resultados de 05/05/2026 e o anterior) e a 2ª chamada são etapas
  posteriores à 1ª chamada; só a 2ª chamada é reconstruída aqui, com o próprio quadro e o próprio resultado.
- Ciclos 1 e 3: a publicação da 1ª chamada já inclui a redistribuição do item 5.7 (células acima das
  imediatas: ciclo 1 = 202, ciclo 3 = 121; vagas acrescidas na capacidade efetiva: 243 e 163). A priorização da SGTES que decide para onde vão essas vagas não é publicada; por isso a especificação
  ex ante não as reproduz.
- Aceitação adiada com prioridade da 1ª opção × Boston em duas rodadas: sem vagas reservadas, as duas dão o
  mesmo resultado em todas as chamadas (candidatos com resultado diferente: Ciclo 1, 1ª chamada 0, Ciclo 2, 1ª chamada 0, Ciclo 3, 1ª chamada 0, Ciclo 1, 2ª chamada 0, Ciclo 2, 2ª chamada 0). Com as vagas reservadas, diferem em Ciclo 1, 1ª chamada 4, Ciclo 2, 1ª chamada 4, Ciclo 3, 1ª chamada 0, Ciclo 1, 2ª chamada 0, Ciclo 2, 2ª chamada 2 candidatos: em Boston, a vaga reservada sem cotista de 1ª opção vira remanescente já na rodada das 1ª
  opções; na aceitação adiada, ela espera o cotista de 2ª opção. A tabela 2 mostra qual reproduz melhor cada
  chamada.

## 4. Cortes por célula e margens (variáveis do mecanismo)

Corte da célula: prioridade do último admitido em vaga de ampla concorrência — o par (ordem da opção,
pontuação). Corte ativo: algum candidato que propôs à célula foi recusado. Margem da 1ª opção: pontuação
menos a pontuação de corte da célula da 1ª opção, definida só quando o corte cai entre candidatos de 1ª
opção. Margem 0 = empatado no corte, onde decide o desempate não observável. Contagens apenas, para
planejamento de poder; nenhuma comparação de outcome.

| Chamada | Células com vaga | Com corte ativo | Corte entre 1ª opções | Corte entre 2ª opções | Empate no corte decidido por desempate | Margem definida | Margem = 0 (admitidos / recusados) | \|margem\| ≤ 1 | \|margem\| ≤ 2 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Ciclo 1, 1ª chamada | 473 | 197 | 180 | 17 | 60 | 571 | 266 (191 / 75) | 330 | 436 |
| Ciclo 2, 1ª chamada | 728 | 368 | 347 | 21 | 130 | 1.356 | 636 (400 / 236) | 805 | 1.132 |
| Ciclo 3, 1ª chamada | 498 | 228 | 216 | 12 | 86 | 851 | 394 (278 / 116) | 517 | 708 |
| Ciclo 1, 2ª chamada | 295 | 89 | 81 | 8 | 30 | 293 | 150 (93 / 57) | 200 | 253 |
| Ciclo 2, 2ª chamada | 226 | 75 | 73 | 2 | 30 | 327 | 143 (90 / 53) | 183 | 268 |

Como ler: valores da especificação principal (capacidade efetiva). A mesma tabela na capacidade ex ante está
em `G2_resumo.json` (`cortes_ex_ante`, `margem_1a_opcao_ex_ante`).

## 5. O que isso implica para o P6

1. A regra de alocação é replicável quando a classificação publicada da célula entra como desempate e a
   capacidade efetiva é tomada da publicação. Sem a classificação publicada, a nota (inteira, 0–15) e a
   ordem da opção não bastam: os empates no corte são decididos por UF de residência ou nascimento e idade,
   que não são públicos.
2. A variável de corte é discreta (pontuação inteira) e a vizinhança do corte é dominada por empates. Um
   desenho de RD na nota terá poucos pontos de suporte; o contraste perto do corte compara candidatos
   empatados separados por um desempate determinístico (idade, UF), não por sorteio.
3. Nos ciclos 1 e 3, a capacidade de parte das células resulta de uma redistribuição discricionária (item
   5.7) feita depois de ver as listas de espera; essas células precisam de tratamento separado no protocolo
   56 (por exemplo, restringir o contraste às células cuja capacidade efetiva é igual às imediatas do
   quadro).
4. Ciclo 2: o texto do edital não está no repositório; a ordem das cotas foi assumida (a do ciclo 3) e a
   ordem alternativa é relatada na tabela 2.

## 6. Saídas

- `output/rdd_bolsa/G2_alocacao_reconstruida.parquet`: uma linha por candidato × chamada (7.000 linhas).
- `output/rdd_bolsa/G2_cortes_celula.csv`: uma linha por célula × chamada (3.618 linhas).
- `output/rdd_bolsa/G2_resumo.json`: concordâncias, divergências, contagens, entradas com SHA-256 e veredito.

Nenhum nome ou CPF é gravado; o candidato é o pseudônimo `id_candidato` do script 12. A inscrição em ação
afirmativa é gravada só como indicador (reserva sim/não). O arquivo local de IVS não é lido.
