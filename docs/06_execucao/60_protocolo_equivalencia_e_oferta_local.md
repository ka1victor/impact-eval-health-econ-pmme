# 60. Protocolo: equivalência no preenchimento (H1) e oferta local depois da chegada (H4)

> **Data de congelamento:** 26/10/2026, antes de rodar qualquer conta deste
> protocolo.<br>
> **Origem:** perguntas do autor em 26/10/2026. Dá para dizer que não mudou
> nada, e como testar? Teve aumento de horas, mas não de especialistas no
> município?<br>
> **Estatuto:** `PROTOCOLO_60_POS_RESULTADO`. Toda saída leva
> `natureza_dos_dados = EMPIRICO`.<br>
> **O que já foi visto:**
> - Parte A: as estimativas pontuais e os IC 95% de A3 e N1 (docs 49 e 57).
>   Pelos IC publicados, a parte A já é previsível em boa parte.
> - Parte B: o D2 do protocolo 47 (produção e K4) e o P4 (horas do médico) já
>   foram vistos. A contagem municipal de especialistas depois da chegada
>   **não** foi estimada em nenhum bloco. A DiRD do E7 mede o degrau da bolsa
>   nos cortes, não a chegada.

## Parte A. Equivalência no preenchimento (H1)

**Pergunta.** Os dados permitem dizer que o salto no corte está dentro de uma
margem pequena, nos dois sentidos? Ou só que não é um aumento grande?

**Margens**, fixadas aqui a partir das referências do protocolo 40, §1:

| Outcome | Margem de equivalência |
|---|---|
| A3, célula aberta preenchida na 1ª chamada | ±10 p.p. |
| N1, vagas preenchidas por município com controle das vagas oferecidas (S-a) | ±25% da média abaixo do corte na mesma amostra |

**Teste.** TOST (dois testes unilaterais a 5%), equivalente a o IC 90% estar
dentro da margem. Relatar separadamente:
- o teste "o aumento é menor que a margem" (H0: salto ≥ +margem);
- o teste "a queda é menor que a margem" (H0: salto ≤ −margem).

**Linhas:**
- **primárias, com Holm entre as duas:** A3 empilhado (ciclos 1–3, cortes
  empilhados) e N1 empilhado;
- **secundárias:** A3 por corte e no ciclo 1; N1 por corte.

**Insumos.** As estimativas e EP gravados de `NA_estimativas.csv` e
`N_estimativas.csv`. Nada é reestimado.

**Sensibilidade e relato:**
- **IC honesto:** onde o bloco gravou o IC honesto, o mesmo TOST com ele.
- **Margem mínima de equivalência:** o menor m tal que o IC 90% fica em [−m; +m].
  É descritiva, para mostrar o que os dados conseguem afirmar.

**Leitura pré-registrada:**

| Resultado do TOST | O que se pode dizer |
|---|---|
| os dois testes rejeitam | o salto está dentro de ±margem: "não mudou além de X", para o pacote do corte e sob a aproximação local linear |
| só o teste do aumento rejeita | "não houve aumento de X ou mais", mas uma queda de X não fica descartada |
| nenhum rejeita | inconclusivo |

## Parte B. Oferta local de especialistas depois da chegada (H4, município × mês)

**Pergunta.** Quando o 1º especialista do PMM-E começa no município, a oferta
cadastrada de especialistas do município sobe? E a dos **outros**
especialistas, que não são do programa, cai?

| Item | Definição |
|---|---|
| Unidade | município × mês, 202406–202608 (nenhum mês ≥ 202609) |
| Tratamento | mês de início do 1º médico do PMM-E no município (listas nominais, ciclos 1 e 2, como no D2 do protocolo 47) |
| Controles | municípios ainda não tratados que ofereceram célula em algum ciclo (inclusive o ciclo 3 antes do início) |
| Estimador | Callaway–Sant'Anna, base g − 1, agregação por e; bootstrap multiplicador de Mammen por município, semente 20261026; janela principal e ∈ [−6, +6] |
| Fonte | painel CNES nacional (a09) para o município; painel a16 para os vínculos dos médicos do PMM-E ligados |

**Outcomes**, por 10 mil habitantes (Censo 2022), com as definições do E7
(protocolo 40, F3) para as CBO-alvo (`alvo_pmme`):

| Id | Outcome | Papel |
|---|---|---|
| **B1** | vínculos nas CBO-alvo | **primária** |
| **B2** | horas SUS semanais nas CBO-alvo | **primária** |
| B3 | B2 sem as horas dos médicos do PMM-E ligados (a16): os **outros** especialistas | secundária; é o teste de deslocamento (*crowding out*) |
| B4 | horas totais (SUS e não SUS) nas CBO-alvo | secundária |
| B5 | placebo: vínculos de generalistas | secundária |

- **Holm:** entre B1 e B2.
- **BKY:** nas secundárias.

**Pré e sensibilidade:**
- teste conjunto do pré (Wald);
- Rambachan–Roth com Δ^RM em M̄ ∈ {0; 0,5; 1; 1,5; 2} na média do pós, com a
  `honestdid_lib.py` do protocolo 59 (teste condicional e híbrido).

**Regras de construção:**
- **B3:**
  - Só se subtraem as horas SUS que o médico do PMM-E ligado tem em vínculo
    nas CBO-alvo, em estabelecimento do próprio município, no mês.
  - Médico não ligado não é subtraído. Isso é relatado como limite: o B3
    superestima os outros especialistas na proporção dos não ligados.
- **Ausência:** mês ou município ausente na fonte fica ausente, nunca zero.

**Leitura pré-registrada:**

| Se | Leitura |
|---|---|
| B1 ou B2 sobe, com pré que passa e ruptura M̄ ≥ 1 | associação da chegada com mais oferta cadastrada local |
| B3 cai | sinal de deslocamento dos outros especialistas |
| B3 não se distingue de zero e B2 sobe | o ganho vem dos médicos do programa, sem deslocamento detectável |

Em todos os casos é ATT sob tendências paralelas da chegada. Não é efeito da
bolsa nem da participação no programa como política.

## Saídas

| Item | Onde |
|---|---|
| scripts | `scripts/rdd_bolsa/36_equivalencia_H1.py` (parte A); `scripts/rdd_bolsa/37_oferta_local_chegada.py` (parte B) |
| estimativas | `output/rdd_bolsa/EQ_estimativas.csv`, `EQ_resumo.json`; `output/rdd_bolsa/OL_estimativas.csv`, `OL_resumo.json`, `OL_figuras/` |
| resultados | `docs/06_execucao/57j_resultados_equivalencia_H1.md`; `docs/06_execucao/57k_resultados_oferta_local.md`; gerados pelos scripts entre marcadores |
| testes | `tests/test_equivalencia_H1.py`; `tests/test_oferta_local_chegada.py` |

## Integridade

- Nada imputado.
- Ausente não vira zero.
- Sem nome, CPF ou CRM em `output/`.
- O arquivo de IVS errado não é lido.
- Nenhum CNES ≥ 202609.
- As saídas dos blocos anteriores não são regravadas.
