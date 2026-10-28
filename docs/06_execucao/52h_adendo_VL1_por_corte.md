# 52h. Adendo: escolha da 1ª opção com o par de UFs fixado, degrau por degrau (cortes 0,300 e 0,400)

> **Data de congelamento:** 28/10/2026, antes de rodar as contas deste adendo.<br>
> **Pedido do autor (28/10/2026):** o grupo perguntou se o efeito da bolsa vale nos dois cortes; o autor pediu "Faz
> aí a análise nova p termos ctz", separando o efeito da bolsa por corte (0,300 e 0,400) e comparando só vagas da
> mesma UF.<br>
> **Estatuto:** `ADENDO_52H_POS_RESULTADO`. O VL-1 do 52e (doc 57x), nos ciclos 1–3 e no ciclo 2, e o VL-1 por ciclo
> do 52g (doc 57z) já foram vistos. Toda saída leva `natureza_dos_dados = EMPIRICO`.

## 1. Motivo

A bolsa é função exata do IVS 2010 oficial (a08), com regra sharp: bolsa = 10 + 5·1[IVS > 0,300] + 5·1[IVS > 0,400]
(R$ mil/mês). No VL-1, `bolsa_mil` entra linear; logo o modelo força o mesmo salto de utilidade nos dois cortes. Este
adendo solta essa restrição e nada mais.

## 2. O que se estima

| Id | Linha | Papel |
|---|---|---|
| **VK-1** | VL-1 com `bolsa_mil` trocada por dois degraus, D300 = 1[IVS > 0,300] e D400 = 1[IVS > 0,400] (cada um = +R$ 5 mil); resto idêntico (spline do IVS com mudança de inclinação em 0,300 e 0,400, distância, mesma região de saúde, mesmo município, atributos da vaga, efeito fixo de UF de origem × UF da vaga); ciclos 1–3. Razão de chances de cada degrau | principal |
| **VK-2** | idem no ciclo 2 | principal |
| **VK-D** | igualdade dos dois degraus em VK-1 e VK-2: Wald (cluster por conjunto de escolha) de H0: δ300 = δ400; razão das razões de chances exp(δ300 − δ400) com IC 95% | teste da hipótese do pedido |
| VK-3 | VK-1 com efeito fixo de região de saúde de origem × UF da vaga (como o VL-3) | sensibilidade |
| VK-5 | quem identifica cada degrau: conjuntos de escolha, pares de UF e candidatos com vagas dos dois lados de cada corte dentro da mesma UF | diagnóstico |
| VK-R | reprodução do VL-1 dos ciclos 1–3 e do ciclo 2 (≤ 1e−8), antes de qualquer conta nova | portão |

O VL-1 é o caso restrito do VK (δ300 = δ400 = 5β); o spline do IVS fica, de modo que cada degrau é o salto de
nível no seu corte, com as inclinações livres dos dois lados.

## 3. Inferência

Como no 52e: sanduíche com cluster por conjunto de escolha (curso × ciclo), IC 95% e p pela normal, mais o p com t
de G − 1. Score bootstrap de Rademacher (Kline–Santos) para cada degrau, se as funções do script 50 o permitirem
para um termo arbitrário; se não, registra-se e usa-se cluster + t(G − 1). Holm entre os quatro degraus principais
(dois cortes × VK-1/VK-2), conforme o doc 38 §3 D4 (família só da hipótese). VK-D, VK-3 e VK-5 ficam fora do Holm.

## 4. Leitura pré-registrada

| Resultado | Leitura |
|---|---|
| Os dois degraus com RC > 1 e o IC da razão entre eles contendo 1 | o efeito por +R$ 5 mil vale nos dois cortes; o efeito linear é adequado |
| Um degrau com IC que exclui 1, o outro com IC que contém 1, e o IC da razão contendo 1 | o efeito aparece num corte; não dá para dizer que difere entre cortes |
| IC da razão excluindo 1 | o efeito difere entre cortes; relatar qual é maior |
| Sinal oposto com IC que exclui 1 | relatar; o efeito linear esconde heterogeneidade |

Lê-se VK-1 e VK-2, cada um.

## 5. Saídas

| Item | Onde |
|---|---|
| script | `scripts/rdd_bolsa/54_VL1_por_corte.py` (importa o 50; não o reescreve) |
| estimativas | `output/rdd_bolsa/VK_estimativas.csv`, `VK_resumo.json` |
| resultados | `docs/06_execucao/57za_VL1_por_corte.md` (blocos gerados pelo script) |
| testes | `tests/test_VL1_por_corte.py` |

## 6. Linguagem e integridade

O degrau é o pacote do corte (bolsa e outras regras federais que mudam nos mesmos cortes; auditoria 18), não a
participação no PMM-E. Tudo é condicional a se candidatar, sobre a vaga marcada como 1ª opção (não a ida ao
município). Pós-resultado. Nada imputado, adquirido ou escrito em `data/`; IVS do a08; `VL_*` e `VG_*` não são
regravados.
