# 48g. Adendo: heterogeneidade pelo porte onde o estrato da atenção primária muda no corte

> **Data de congelamento:** 26/10/2026, antes de rodar as contas deste adendo.<br>
> **Decisão do autor (26/10/2026):** "pode fazer tudo isso" (item 4 da §2.16
> de [`../07_apresentacoes/banca2/05_discussao_historia_empirica.md`](../07_apresentacoes/banca2/05_discussao_historia_empirica.md)).<br>
> **Estatuto:** `ADENDO_48G_POS_RESULTADO`. A H1 (48b), a oferta local no corte
> (64) e os controles e pareamentos (48d, 48e) já foram vistos; a divisão por
> porte, não. Toda saída leva `natureza_dos_dados = EMPIRICO`.<br>
> **Origem:** auditoria 18, §2.5 e recomendação 5.

## 1. A ideia

Nos mesmos cortes da bolsa muda também o **estrato do IED** (Portaria
3.493/2024, componente fixo/de equidade da atenção primária, R$ 2.000 por eSF
por mês por degrau, desde a parcela de 05/2024). Mas o estrato só muda em
alguns portes (auditoria 18, tabela lida de `a10_diagnostico_cortes_normas.json`):
- em **0,300**: muda nos portes **2 e 3**; não muda nos portes 1 e 4;
- em **0,400**: muda nos portes **1, 2 e 4**; não muda no porte 3.

A bolsa do PMM-E muda em **todos** os portes. Comparar o salto no corte entre
os portes onde o estrato muda (G = 1) e onde não muda (G = 0) separa, em parte,
o canal do IED do resto do pacote. Se o salto (da H1 ou da oferta) aparece só
onde o estrato muda, o canal provável é o IED; se aparece igual nos dois
grupos, o IED não explica.

**Limite:** dentro da janela, os portes também diferem em tamanho, capital e
região; a diferença entre grupos é **descritiva** de heterogeneidade
pré-tratamento, não causal do IED.

## 2. Definições

- **Porte:** o do próprio Anexo VI da 3.493/2024 (IBGE 2022, pré-tratamento),
  lido de `output/aquisicao/a10_ied_aps_2024_municipio.csv`. Município sem
  porte no Anexo VI sai, contado.
- **G (por corte):** em 0,300, G = 1 nos portes 2 e 3; em 0,400, G = 1 nos
  portes 1, 2 e 4. A regra é **lida** de `a10_diagnostico_cortes_normas.json`
  (`estrato_ied_por_codigo_ivs_e_porte`), não digitada.
- **Running variable:** IVS 2010 oficial (a08).

## 3. Especificação

Diferença em descontinuidades entre grupos, local linear, kernel triangular,
h = 0,050, **cada corte separado**:

Y = α_g + τ₀·acima + τ₁·acima·G + retas em IVS por lado **e por grupo** (+ o
que a especificação base de cada outcome já tem: ciclos com parâmetros
próprios e efeitos fixos na H1; ΔY na oferta local).

τ₁ = salto onde o estrato muda − salto onde não muda.

| Id | Outcome (especificação base) | Papel |
|---|---|---|
| **PO-1** | HI-1 e HI-2 do 48b (célula e município; ciclo 2 pelo quadro de 13/02), τ₁ por corte | **primária** (4 linhas; Holm) |
| PO-2 | OC-A1 e OC-A2 do protocolo 64 (ΔB1, ΔB2 em V), τ₁ por corte | secundária |
| **PO-3** | ΔB5, generalistas (o placebo do 64), τ₁ por corte: é o outcome que o IED deve mover se tiver efeito | secundária (teste do canal) |
| PO-4 | o salto em cada grupo separadamente (τ₀ e τ₀ + τ₁), por outcome e corte | descritiva |
| PO-5 | contagens por grupo, lado e corte na janela; balanço de capital e região por grupo | diagnóstico |

BKY entre as secundárias. Grupo × lado com menos de 10 unidades na janela: a
linha fica sem estimativa, contada.

## 4. Leitura pré-registrada

| Resultado | Leitura |
|---|---|
| τ₁ com IC que contém zero em PO-1 | não se detecta que o salto da H1 dependa de o estrato do IED mudar; o IED não explica o sinal da H1 (com pouca potência: relatar contagens) |
| τ₁ de PO-1 rejeita zero depois do Holm, com o salto concentrado onde o estrato muda | o sinal da H1 anda junto com o canal do IED; reforça que o corte mede pacote |
| PO-3 com salto de generalistas só onde o estrato muda | indício de que o IED move a atenção primária no corte |
| contagens de algum grupo × lado < 10 | relatar como sem potência para esse grupo |

## 5. Saídas

| Item | Onde |
|---|---|
| script | `scripts/rdd_bolsa/47_heterogeneidade_porte_ied.py` (importa os construtores do 40 e do 43) |
| estimativas | `output/rdd_bolsa/PO_estimativas.csv`, `PO_resumo.json`, `PO_figuras/` |
| resultados | `docs/06_execucao/57u_resultados_heterogeneidade_porte.md` (blocos gerados pelo script) |
| testes | `tests/test_heterogeneidade_porte_ied.py` |

**Portão:** antes de qualquer conta nova, o script reproduz HI-1 e HI-2 do 48b
e OC-A1 do 64 em 0,300 sem a divisão por grupo (≤ 1e−8), e confere que G sai
da tabela do a10 (porte × código de IVS → estrato) e não de valor digitado.

## 6. Integridade

Nada imputado, adquirido ou escrito em `data/`; IVS oficial; nenhuma
competência do CNES ≥ 2026-09; `HI_*`, `OC_*`, `CL_*` e `PM_*` não são
regravados.
