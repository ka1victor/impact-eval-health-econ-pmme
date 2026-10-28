# Guia do grupo: a hipótese da banca 2 em uma página (para acompanhar e montar os slides)

> **Para quem é:** para o grupo acompanhar a parte empírica e montar os slides da banca 2.<br>
> **Data:** 28/10/2026, dia da banca (versão anterior: 27/10/2026, no histórico, commit `33d15d9`).<br>
> **Mudança de 28/10/2026 (decisão do autor):** "a hipótese é simplesmente sobre o efeito bolsa → 1ª opção", com "só
> comparação entre municípios da mesma UF"; "UF, origem etc. é tudo controle/pareamento". A hipótese não fala mais da
> origem; o teste origem × toda a bolsa (D_UF, ×11,0 contra ×1,57) **saiu do deck**. O que mudou slide a slide e o
> texto exato da tela estão no [doc 10](10_mapa_deck_anterior_para_rubrica.md), **§6**; a fala, no
> [doc 09](09_roteiro_fala_7min.md).<br>
> **Regra do projeto:** todo número dos slides sai de `output/` por script. Os números abaixo servem para o grupo
> entender a história. No slide, use a figura gerada pelo pipeline, nunca um número digitado à mão.

## 1. A hipótese

**Comparando vagas da mesma UF, a vaga de bolsa maior tem mais chance de ser a 1ª opção do médico.**

- Foi formulada **depois** de ver os dados. Isso está no slide 1.
- A UF de origem, a UF da vaga, a região de saúde, o município e a distância são **só controle e pareamento**.
  Nenhum slide fala de quanto a origem pesa.

## 2. A história em 7 passos (o deck de 28/10)

| Passo | Mensagem | Slide e figura (em `output/`) |
|---|---|---|
| 1. Motivação | no corte, comparando municípios pareados na mesma UF, não detectamos aumento do preenchimento | slide 1 (uma linha); figura no apêndice, `apresentacao_banca2/curto_fato_pareado.png` (slide 12) |
| 2. Por que dentro da UF | a maioria põe a 1ª opção na própria UF: por isso comparamos dentro dela | slide 4, `apresentacao_banca2/exp_escolha_origem.png` |
| 3. Descritiva da hipótese | perto do corte, na UF de origem, o lado de bolsa maior recebe mais 1ªs opções do que tem de vagas | slide 5, `rdd_bolsa/H2_figuras/H2_F2_mesma_uf_perto_do_corte.png` |
| 4. Modelo | logit condicional com efeito fixo de UF de origem × UF da vaga; teste β > zero | slide 6 (texto) |
| 5. Resultado | comparando vagas da mesma UF, a vaga de bolsa maior é mais escolhida (VL-1) | slide 8, `apresentacao_banca2/curto_bolsa_mesma_uf.png` |
| 6. Robustez | mantém com distância em log e região de saúde; forte só no ciclo 2; perto do corte, inconclusivo | slide 9, `apresentacao_banca2/curto_robustez_escolha.png` |
| 7. Conclusão e teoria | sim, a bolsa maior aumenta a chance de a vaga ser a 1ª opção dentro da mesma UF, forte no ciclo 2; os dados sugerem que ela compensa parte do custo do lugar | slides 10 e 11 (texto) |

## 3. Os números que contam a história (para entender, não para digitar)

| O quê | Valor | Fonte |
|---|---|---|
| 1ª opção na própria UF (descritivo; motivação) | 79% | `numeros_banca2.json` (`ESC_UF`) |
| Perto do corte, na UF de origem: lado de bolsa maior nas vagas e nas 1ªs opções (descritivo) | 52,5% e 60,8% (1.568 candidatos) | doc 66, §3 (`H2D_*`) |
| Bolsa +R$ 5 mil, vagas da mesma UF, ciclos 1–3 (VL-1; resultado principal) | razão de chances 1,47 [1,15; 1,89] | 57x, auditoria 48 (`VL1_EMP_*`) |
| Idem, ciclo 2 | 1,90 [1,30; 2,78] | 57x (`VL1_C2_*`) |
| Idem, ciclos 1 e 3 separados | 1,15 [0,66; 2,01] e 1,25 [0,90; 1,73]: IC contém 1 | 57z, adendo 52g, auditoria pendente (`VG1_*`, `VG3_*`) |
| +R$ 5 mil pesam como… | 75 km a menos de distância, dentro da mesma UF | 57x (`VL1_EMP_K5`) |
| Sem fixar a UF (pré-registrado), ciclos 1–3 | 1,25 [0,98; 1,61]: IC contém 1 | 57x, 57p (`VLB_EMP_*`) |
| Só vagas perto do corte | 1,28 [0,95; 1,72]: inconclusivo | 57x (`VL2_EMP_*`) |

**Como ler a razão de chances:** acima de 1, a vaga de bolsa maior é preferida a uma vaga parecida da mesma UF.
1,47 quer dizer que, entre duas vagas parecidas da mesma UF, a de bolsa R$ 5 mil maior tem 1,47 vez a chance de ser
a 1ª opção.

## 4. O que dizer e o que não dizer

| Dizer | Não dizer |
|---|---|
| "comparando vagas da mesma UF, a vaga de bolsa maior é mais escolhida como 1ª opção" | "a bolsa traz mais médicos" |
| "forte só no ciclo 2; nos ciclos 1 e 3 o IC contém 1" | "a bolsa funciona em todos os ciclos" |
| "sem fixar a UF, como no pré-registrado, o IC contém 1" | esconder que a especificação é pós-resultado |
| "no corte, não detectamos aumento do preenchimento" | "a bolsa não encheu mais vagas" ou "a bolsa reduz o preenchimento" |
| "a UF é controle: comparamos dentro dela" | "a origem pesa mais que a bolsa", "×11", "D_UF" |
| "o contraste da bolsa é o pacote de regras que muda no corte" | "o efeito do PMM-E" |

**Ressalvas obrigatórias:** (1) pós-resultado; (2) sem fixar a UF, o IC contém 1; (3) condicional a se candidatar:
escolha não é preenchimento; (4) pacote do corte; (5) forte só no ciclo 2; (6) origem = vínculo no CNES, não a
residência.

## 5. Estrutura obrigatória do deck (8 seções, até 14 slides + apêndice)

Hipótese → Dados → Análise descritiva → Metodologia → Identificação → Resultados → Robustez → Discussão
([doc 06](06_estrutura_obrigatoria_versao_final.md)). No máximo ~30 palavras por slide; o detalhe vai nas notas.
O deck de 28/10 tem 11 slides no corpo e 1 no apêndice.

## 6. Onde está cada coisa

| Para | Arquivo |
|---|---|
| a hipótese | [07_nova_hipotese.md](07_nova_hipotese.md) |
| o conteúdo de cada slide (fonte da verdade) | [04_conteudo_deck_curto.md](04_conteudo_deck_curto.md) |
| os resultados da escolha | docs 57x (VL-1) e 57z (ciclos 1 e 3) em `docs/06_execucao/` |
| a análise completa e a F2 | [`docs/06_execucao/66_analise_completa_H2.md`](../../06_execucao/66_analise_completa_H2.md) ([auditoria 52](../../auditorias/52_auditoria_analise_H2.md)) |
| o deck | `output/apresentacao_banca2/deck_banca2_curto.pdf` |
| o roteiro de 7 minutos | [09_roteiro_fala_7min.md](09_roteiro_fala_7min.md) |
| o que mudou em 28/10 e o texto da tela | [10_mapa_deck_anterior_para_rubrica.md](10_mapa_deck_anterior_para_rubrica.md), §6 |
