# 52e. Adendo: H2 com a localização do médico e da vaga fixada (efeito fixo do par de UFs e comparação local no corte)

> **Data de congelamento:** 27/10/2026, antes de rodar as contas deste adendo.<br>
> **Pedido do autor (27/10/2026):** "rodar de novo a H1 fazendo pareamento pela localização da unidade e do
> médico, como se fosse um controle. O mesmo vale para a H2."<br>
> **Estatuto:** `ADENDO_52E_POS_RESULTADO`. P1 (57a), P1h (57i), 52c (57p) e 52d (57v) já foram vistos. Toda
> saída leva `natureza_dos_dados = EMPIRICO`.

## 1. O que é "parear pela localização" no modelo de escolha

No logit condicional da 1ª opção, cada candidato já é comparado **consigo mesmo**: o modelo pergunta qual das vagas
do seu conjunto ele escolheu. A especificação base (M1, doc 57a) já controla a localização relativa do médico e da
vaga por distância, mesma UF, mesma região de saúde e mesmo município de origem, e o M4 troca a macrorregião por
efeito fixo de UF da vaga. O que falta é **fixar o par de localizações**: comparar só vagas que estão na mesma
relação geográfica com o médico. Isso se faz com:

1. **efeito fixo de UF de origem × UF da vaga**: o peso da bolsa passa a vir só de vagas da **mesma UF**, vistas por
   médicos da **mesma UF de origem**;
2. **comparação local no corte**: só vagas a até 0,050 de um corte de IVS, com o efeito fixo do par de UFs. É a
   versão "RDD dentro da escolha": vagas parecidas, mesma UF, de um lado e do outro do corte.

Ciclo 2 com o tipo de vaga do quadro de 13/02/2026 (52c).

## 2. Linhas

| Id | Linha | Papel |
|---|---|---|
| **VL-1** | M1 (bolsa linear, *spline* do IVS, log da distância, mesma região de saúde, mesmo município) com **efeito fixo de UF de origem × UF da vaga**, ciclos 1–3 e ciclo 2: razão de chances por +R$ 5 mil | **principal** |
| **VL-2** | VL-1 restrito a vagas com \|IVS − corte\| ≤ 0,050 (os dois cortes juntos, com intercepto por corte), mesmo efeito fixo | **principal** |
| VL-3 | VL-1 e VL-2 com efeito fixo de **região de saúde de origem × UF da vaga** | sensibilidade |
| VL-4 | **km equivalentes de +R$ 5 mil** em VL-1 (razão entre o peso da bolsa e o da distância), como no P1h | secundária |
| VL-5 | M1 e P1h-1 sem mudança (reprodução, referência) | referência |

O D_UF do P1h (peso da mesma UF − peso de toda a bolsa) **não é identificado** em VL-1, porque o efeito fixo do par
de UFs absorve "mesma UF". Ele fica relatado da especificação base (VL-5). Inferência: *cluster* por conjunto de
escolha (curso × ciclo), como no 52c; com poucos *clusters*, score bootstrap de Rademacher como no doc 42. Holm entre
as linhas principais (VL-1 ciclos 1–3, VL-1 ciclo 2, VL-2); BKY nas secundárias.

## 3. Leitura pré-registrada

| Resultado | Leitura |
|---|---|
| VL-1 e VL-2 com razão de chances parecida com a do M1 | o peso da bolsa na escolha não vem da localização: entre vagas na mesma relação geográfica com o médico, a bolsa maior pesa o mesmo |
| VL-1 cai para perto de 1 com IC que contém 1 | o peso da bolsa no M1 vinha, em parte, de onde as vagas de bolsa maior ficam em relação à origem dos médicos |
| VL-2 com IC muito largo | a comparação local tem pouca informação; relatar |
| VL-4 | traduzir: "+R$ 5 mil pesa como X km a menos de distância, comparando vagas da mesma UF" |

## 4. Saídas

| Item | Onde |
|---|---|
| script | `scripts/rdd_bolsa/50_escolha_localizacao_par.py` (importa 42, 25, 25c e 16; não os reescreve) |
| estimativas | `output/rdd_bolsa/VL_estimativas.csv`, `VL_resumo.json`, `VL_figuras/` |
| resultados | `docs/06_execucao/57x_resultados_escolha_localizacao_par.md` (blocos gerados pelo script) |
| testes | `tests/test_escolha_localizacao_par.py` |

**Portão:** reproduzir VL-5 contra `VC_*`/`P1_*` (≤ 1e−8) antes de qualquer conta nova.

## 5. Integridade

Nada imputado, adquirido ou escrito em `data/`; IVS oficial; `E9_*`, `P1_*`, `P1h_*`, `VC_*` e `VD_*` não são
regravados. A origem é preferência revelada, não efeito causal.
