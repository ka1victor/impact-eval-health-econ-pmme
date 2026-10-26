# 52d. Adendo: sensibilidades da escolha no ciclo 2 com o tipo de vaga do quadro de 13/02/2026

> **Data de congelamento:** 26/10/2026, antes de rodar as contas deste adendo.<br>
> **Decisão do autor (26/10/2026):** "pode fazer tudo isso" (pendência do
> achado 1 da auditoria 41, registrada na §2.16 de
> [`../07_apresentacoes/banca2/05_discussao_historia_empirica.md`](../07_apresentacoes/banca2/05_discussao_historia_empirica.md)).<br>
> **Estatuto:** `ADENDO_52D_POS_RESULTADO`. As versões com o quadro de 19/03
> e o adendo 52c (principais corrigidas) já foram vistos. Toda saída leva
> `natureza_dos_dados = EMPIRICO`.

## 1. O que falta corrigir

O adendo 52c refez as **principais** da escolha (E9 ciclo 2 e empilhado; P1 M1
e M5; P1h-1) com "tem vaga imediata" e "log(vagas imediatas + 1)" do ciclo 2
tirados do quadro vigente na inscrição (13/02/2026), e não do retificado de
19/03/2026, refeito depois do resultado preliminar (auditoria 36). A auditoria
41 (achado 1) apontou que as **sensibilidades** que sustentam a robustez do
ciclo 2 (doc 44) ainda usam o quadro de 19/03:
- o conjunto de escolha "só células com vaga imediata" do E9;
- as variantes M2, M4 e M6 a M9 do P1 (doc 57a);
- a DAP (disposição a pagar / km equivalentes) do P1 e do P1h que dependem
  dessas variantes.

## 2. O que se estima

Exatamente as mesmas especificações dos docs 42, 57a e 57i, com uma única
troca: no ciclo 2, toda variável que depende do tipo de vaga (indicador de
vaga imediata, número de vagas imediatas e a **definição do conjunto de
escolha** "só células com vaga imediata") vem do quadro de **13/02/2026**,
lido como no 52c (mesmo leitor, mesmo hash). Ciclos 1 e 3 não mudam.

| Id | Linha | Papel |
|---|---|---|
| **VD-1** | E9, ciclo 2, conjunto "só células com vaga imediata" (quadro de 13/02): razão de chances da 1ª opção por +R$ 5 mil | **principal** deste adendo |
| VD-2 | E9 empilhado com o mesmo conjunto | secundária |
| VD-3 | P1 M2, M4, M6, M7, M8 e M9 nos ciclos e no empilhado em que usam o tipo de vaga | secundária |
| VD-4 | DAP e km equivalentes que dependem de VD-3 | secundária |
| VD-5 | as mesmas linhas com o quadro de 19/03 (reprodução da versão antiga), lado a lado | referência |

Inferência como nos docs originais (cluster por conjunto de escolha, score
bootstrap onde o original usou). BKY entre as secundárias.

## 3. Leitura pré-registrada

| Resultado | Leitura |
|---|---|
| VD-1 com o mesmo sinal da versão antiga e IC que exclui 1 | a robustez do ciclo 2 (doc 44) se mantém com o tipo de vaga anterior à alocação |
| VD-1 com IC que contém 1 | a robustez do ciclo 2 dependia do quadro pós-resultado; relatar e rebaixar a frase do doc 44 |
| VD-3 com variantes mudando de sinal | relatar quais; a leitura da H2 se apoia nas que não mudam |

## 4. Saídas

| Item | Onde |
|---|---|
| script | `scripts/rdd_bolsa/48_sensibilidades_ciclo2_quadro_1302.py` (importa os scripts 42, 25, 25c e 16; não os reescreve) |
| estimativas | `output/rdd_bolsa/VD_estimativas.csv`, `VD_resumo.json`, `VD_figuras/` |
| resultados | `docs/06_execucao/57v_sensibilidades_ciclo2_quadro_1302.md` (blocos gerados pelo script) |
| testes | `tests/test_sensibilidades_ciclo2_quadro_1302.py` |

**Portão:** reproduzir as linhas VD-5 contra as saídas antigas (`E9_*`,
`P1_*`, `P1h_*`) com diferença ≤ 1e−8 antes de qualquer conta nova.

## 5. Integridade

Nada imputado, adquirido ou escrito em `data/`; IVS oficial; `E9_*`, `P1_*`,
`P1h_*` e `VC_*` não são regravados.
