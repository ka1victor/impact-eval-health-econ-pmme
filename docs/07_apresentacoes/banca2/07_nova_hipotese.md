# A hipótese da banca 2: comparando vagas da mesma UF, a vaga de bolsa maior tem mais chance de ser a 1ª opção

> **Decisão do autor, 28/10/2026 (dia da banca).** "A hipótese é simplesmente sobre o efeito bolsa → 1ª opção", com
> "só comparação entre municípios da mesma UF". Reforço do mesmo dia: "pode deixar TUDO na mesma UF. UF, origem etc. é
> tudo controle/pareamento".<br>
> **O que isso muda:** a hipótese deixa de comparar a origem com a bolsa. Sai "pesa menos que a origem"; sai o teste
> central origem × toda a bolsa (D_UF), do corpo e do apêndice. A UF de origem, a UF da vaga, a região de saúde, o
> município e a distância passam a ser só controle e pareamento: nenhum coeficiente deles é interpretado. O resultado
> principal é o VL-1 do adendo 52e; a robustez fica toda dentro da mesma UF, com os ciclos 1 e 3 do adendo 52g.<br>
> **Estatuto:** a hipótese foi formulada **depois** de ver os resultados do preenchimento no corte e os coeficientes
> do modelo de escolha, e a especificação com o par de UFs fixado também é pós-resultado (adendo 52e, congelado antes
> de rodar, depois de ver o modelo base). Isso é dito na apresentação. Nenhum número deste documento é novo.<br>
> **Histórico:** a versão de 27/10/2026 (hipótese "o médico escolhe perto de onde já trabalha; a bolsa maior muda qual
> vaga ele escolhe entre vagas da mesma UF, mas pesa menos que a própria origem", com o teste central D_UF) fica no
> histórico do repositório (commit `33d15d9`); a §6 resume o que saiu.

## 1. A hipótese, numa frase

**Comparando vagas da mesma UF, a vaga de bolsa maior tem mais chance de ser a 1ª opção do médico.**

- O contraste da bolsa é o **pacote do corte** de IVS (a bolsa e as outras regras federais que mudam nos mesmos
  cortes; [auditoria 18](../../auditorias/18_politicas_nos_mesmos_cortes_ivs.md)), não a participação no PMM-E nem o
  Agora Tem Especialistas.
- Tudo é **condicional a se candidatar**: mudar a escolha não é mudar o preenchimento.

## 2. A história, na ordem da apresentação

1. **Motivação.** No corte de IVS, onde a bolsa é R$ 5 mil maior, comparando municípios pareados na mesma UF, **não
   detectamos aumento** do preenchimento ([57w](../../06_execucao/57w_resultados_pareamento_localizacao.md);
   auditoria 47). Ligar a hipótese a esse fato é interpretação, não teste (auditoria 50).
2. **Por que comparar dentro da UF.** A maioria dos candidatos põe a 1ª opção na própria UF (`ESC_UF`,
   descritivo): por isso a comparação é entre vagas da mesma UF, e a UF entra como controle.
3. **A descritiva da hipótese.** Perto do corte, na UF de origem, o lado de bolsa maior recebe uma parte das 1ªs
   opções maior que a sua parte das vagas (F2 do [doc 66](../../06_execucao/66_analise_completa_H2.md), códigos
   `H2D_*`); sem teste e sem controlar a distância.
4. **O modelo.** Logit condicional da 1ª opção, com efeito fixo de UF de origem × UF da vaga: cada candidato é
   comparado consigo mesmo, só entre vagas da mesma UF (a de origem ou outra), vistas por médicos da mesma UF de
   origem. Teste: β > zero, erro-padrão agrupado por conjunto de escolha.
5. **O resultado.** O VL-1 ([57x](../../06_execucao/57x_resultados_escolha_localizacao_par.md); auditoria 48): a
   vaga de bolsa maior tem mais chance de ser a 1ª opção nos ciclos 1–3 e no ciclo 2 (`VL1_*`), e +R$ 5 mil pesam
   como uma distância menor (`VL1_EMP_K5`).
6. **A robustez, sempre dentro da mesma UF.** Distância em log e região de saúde de origem × UF da vaga: mantém. Só
   vagas perto do corte (VL-2): inconclusivo. Por ciclo ([57z](../../06_execucao/57z_VL1_por_ciclo.md), adendo 52g,
   auditoria pendente): forte só no ciclo 2; nos ciclos 1 e 3 o IC contém 1.
7. **A teoria (modelo da banca 1).** O médico aceita a vaga se a bolsa compensa o custo do lugar. Os dados
   **sugerem** que a bolsa compensa parte desse custo na escolha entre vagas da mesma UF (leitura, não teste).

## 3. O que dá e o que não dá para afirmar

| Dá para afirmar | Não dá para afirmar |
|---|---|
| Entre quem se candidatou, a vaga de bolsa maior é preferida a uma vaga parecida da mesma UF, com força só no ciclo 2 | que a bolsa **causa** mais médicos no município |
| No corte, comparando municípios pareados na mesma UF, não se detecta aumento do preenchimento | que o efeito no preenchimento é zero |
| A especificação pré-registrada, sem fixar a UF, tem IC que contém 1 | que a bolsa reduz o preenchimento |
| — | qualquer coisa sobre o peso da origem: ela é controle, não resultado |

## 4. Ressalvas obrigatórias na fala

1. A hipótese e a especificação com o par de UFs vieram depois dos dados (pós-resultado; exploratório).
2. Sem fixar a UF, como no pré-registrado, o IC contém 1.
3. Condicional a se candidatar: escolha não é preenchimento.
4. Pacote do corte.
5. Forte só no ciclo 2; nos ciclos 1 e 3 o IC contém 1; perto do corte, inconclusivo.
6. A origem é o vínculo médico anterior no CNES, não a residência; ela só define o par de UFs que fica fixo.

## 5. Os gráficos

| Slide | Gráfico | Mensagem |
|---|---|---|
| 4 | onde os candidatos escolhem (`exp_escolha_origem.png`) | "a maioria escolhe na própria UF: comparamos dentro dela" |
| 5 | F2 do doc 66 (`output/rdd_bolsa/H2_figuras/H2_F2_mesma_uf_perto_do_corte.png`) | "descritivo: perto do corte, a bolsa maior é mais escolhida que oferecida" |
| 8 | VL-1, ciclos 1–3 e ciclo 2, sem o modelo base (`curto_bolsa_mesma_uf.png`) | "comparando vagas da mesma UF, a bolsa maior é preferida" |
| 9 | robustez dentro da mesma UF e por ciclo (`curto_robustez_escolha.png`) | "mantém com distância em log e região; forte só no ciclo 2" |
| 12 (apêndice) | o fato pareado na mesma UF (`curto_fato_pareado.png`) | "não detectamos aumento do preenchimento" |

Todos gerados por script a partir de `output/`: `scripts/apresentacao/gerar_figuras_banca2.py`, e a F2 por
`scripts/rdd_bolsa/51_sintese_H2.py`, usada sem redesenho.

## 6. O que saiu em 28/10/2026

- A frase "a bolsa pesa menos que a origem" e o teste central origem × toda a bolsa (D_UF): ele compara a UF de
  origem com outras UFs, então não é comparação dentro da mesma UF. Fica numa linha das notas do slide de Limitações,
  só como resposta de reserva a uma pergunta da banca.
- "A origem é preferência revelada, não causa" como cautela de resultado: como a origem não é mais resultado, a
  cautela passou a ser "origem = vínculo no CNES" nas limitações.
- No apêndice, a RDD sem controle e a antiga H3 (oferta).
