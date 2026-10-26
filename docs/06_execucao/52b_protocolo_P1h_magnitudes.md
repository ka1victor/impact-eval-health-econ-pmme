# 52b. Protocolo P1h: o peso da bolsa contra o custo do lugar na escolha (H3)

> **Data de congelamento:** 26/10/2026, antes de rodar qualquer conta deste
> protocolo.<br>
> **Origem:** plano da banca 2
> ([`07_apresentacoes/banca2/04_plano_entrega_empirica.md`](../07_apresentacoes/banca2/04_plano_entrega_empirica.md),
> §3 e §6.1, item 1). O autor delegou em 26/10/2026 o que fosse preciso para
> deixar a entrega pronta.<br>
> **Estatuto:** `PROTOCOLO_52B_POS_RESULTADO`. Toda saída leva
> `natureza_dos_dados = EMPIRICO`.<br>
> **O que já foi visto.**
> - Os coeficientes do M1 e os seus IC estão publicados no doc 57a
>   (protocolo 52, auditoria 26).
> - Pelos IC publicados, a resposta da linha primária é previsível: a conta
>   aproximada da amplitude da bolsa contra a mesma UF já foi feita na
>   conversa de 26/10/2026.
>
> O que este protocolo acrescenta é a inferência formal da diferença, com a
> covariância conjunta, e a amplitude da bolsa expressa em km com IC. Não é
> teste confirmatório novo.

## 1. Pergunta e hipótese

**H3 (incentivo limitado).** No modelo de escolha do P1, o peso de toda a
amplitude da bolsa que a política oferece (de R$ 10 mil para R$ 20 mil por mês)
é menor que o peso de a vaga ficar na UF de origem do candidato.

É uma comparação de **pesos na utilidade da escolha**, não de efeitos causais
do lugar:
- **a bolsa (β):** identificada pelos saltos nos cortes de IVS, com o IVS em
  spline contínua (pacote do corte);
- **a origem (θ):** é preferência revelada condicional ao modelo. Mistura
  família, rede, registro profissional e outros motivos ligados à origem.
  Não é efeito de mudar a geografia de ninguém.

## 2. Modelo, amostra e inferência

- **Modelo:** M1 do protocolo 52 (§3), exatamente como estimado:
  - ciclos 1–3 empilhados;
  - amostra do P1 (origem ligada, com região de saúde);
  - mesmo conjunto de escolha;
  - mesmas covariáveis.
- **Reestimação:** o script reestima o M1 só para obter a matriz de covariância
  conjunta, que o script 25 não gravou.
  - **Portão:** os coeficientes e os EP com cluster por conjunto têm de
    reproduzir os de `output/rdd_bolsa/P1_estimativas.csv` com diferença
    máxima ≤ 1e−8.
  - Se não reproduzirem, a execução para (`FALHA_REPRODUCAO_M1`) e nada é
    calculado.
- **Inferência principal:** EP sanduíche com cluster por conjunto de escolha
  (curso × ciclo), como no P1a. Relatar também o EP de máxima verossimilhança e
  o EP com cluster por candidato.

Notação, pelos termos do M1:
- β = `bolsa_mil`, por R$ 1 mil/mês;
- γ = `distancia_100km`, negativo;
- θ_UF = `mesma_uf`;
- θ_reg = `mesma_regiao_saude`, incremento sobre a mesma UF;
- θ_mun = `mesmo_municipio`, incremento sobre a mesma região.

## 3. Estimandos

| Id | Estimando | Papel |
|---|---|---|
| **P1h-1** | D_UF = θ_UF − 10·β | **primária**; H0: D_UF ≤ 0 contra H1: D_UF > 0, teste unilateral a 5%; Holm numa família de um teste |
| P1h-2a | km equivalentes a um degrau da bolsa (R$ 5 mil): K5 = 100 · 5β / (−γ) | secundária descritiva; IC pelo método delta e por Fieller |
| P1h-2b | km equivalentes a toda a amplitude (R$ 10 mil): K10 = 100 · 10β / (−γ) | idem |
| P1h-3 | D_UF nas especificações M2, M4, M5 (por ciclo) e M7 do protocolo 52, cada uma reestimada com o mesmo portão de reprodução contra o CSV do P1 | sensibilidade; BKY entre essas linhas (p unilateral) |

Para cada linha: estimativa, EP, IC 95% bilateral, limite inferior unilateral
de 95% e p unilateral.

Fora daqui, para não depender de razão com denominador perto de zero:
- a DAP em R$ (razões sobre β), que já está no 57a;
- o logit misto (M8), caro de reestimar;
- o M3, não estimado no P1.

## 4. Leitura pré-registrada

**Se o P1h-1 rejeitar H0 depois do Holm:**
- No modelo de escolha, a amplitude inteira da bolsa pesa menos que a vaga
  ficar na UF de origem.
- Isso vale condicional a se candidatar e dentro das vagas abertas.
- Não diz que a bolsa não tem efeito nem que a geografia causa a escolha.

**Se não rejeitar:** inconclusivo, com o IC.

**Em todos os casos, relatar** os km equivalentes com IC. Se o IC de β contiver
zero, o de K5 e K10 também conterá, e isso será dito assim.

## 5. Saídas

| Item | Onde |
|---|---|
| script | `scripts/rdd_bolsa/25c_magnitudes_P1h.py` (reusa as funções do script 25; não altera as saídas do P1) |
| estimativas | `output/rdd_bolsa/P1h_magnitudes.csv` |
| resumo | `output/rdd_bolsa/P1h_resumo.json` (hash deste protocolo, entradas com hash, portão de reprodução) |
| figura | `output/rdd_bolsa/P1h_figuras/P1h_magnitudes.png`: pesos na utilidade com IC 95% de um degrau e da amplitude da bolsa, 100 km a menos, mesma UF, mesma região e mesmo município, na mesma escala; com bloco "Como ler" |
| resultados | `docs/06_execucao/57i_resultados_P1h_magnitudes.md`, gerado pelo script entre marcadores |
| testes | `tests/test_P1h_magnitudes.py`: doc igual ao gerado, números contra `output/`, combinação linear e delta conferidos num caso sintético em memória rotulado "sintético" |

## 6. Integridade

- Nada imputado.
- Sem nome, CPF ou CRM em `output/`.
- O arquivo de IVS errado não é lido.
- Nenhum CNES ≥ 202609.
- As saídas do P1 (`P1_*`) não são regravadas.
