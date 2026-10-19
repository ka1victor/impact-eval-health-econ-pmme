# A12b e A13b — safras v2 do SIA e do SIH no TabNet (adendo §12.1 do protocolo 47)

> **Data:** 19/10/2026.<br>
> **Tarefa:** adendo §12.1 do protocolo
> [`06_execucao/47`](../../06_execucao/47_protocolo_producao_especializada.md):
> reextrair o SIH por local de internação (lógica do a13) e o SIA nos meses
> 202509–202607 (lógica do a12) em pastas datadas, sem sobrescrever as
> extrações usadas, e comparar as duas safras. Só aquisição e validação.<br>
> **Scripts:** [`scripts/aquisicao/a13b_safra_v2_sih.py`](../../../scripts/aquisicao/a13b_safra_v2_sih.py)
> e [`scripts/aquisicao/a12b_safra_v2_sia.py`](../../../scripts/aquisicao/a12b_safra_v2_sia.py).<br>
> **Números:** nos resumos gerados,
> [`output/aquisicao/sih_v2/a13_resumo.md`](../../../output/aquisicao/sih_v2/a13_resumo.md) e
> [`output/aquisicao/sia_v2/a12_resumo.md`](../../../output/aquisicao/sia_v2/a12_resumo.md),
> e nas comparações `comparacao_v2_v1_*` de cada pasta. As listas marcadas abaixo
> são conferidas contra as saídas por `tests/test_aquisicao_safras_v2.py`.<br>
> **Cegamento:** nada foi calculado por IVS, faixa da bolsa, lado de corte,
> tratamento ou chegada; os scripts não leem IVS. Natureza dos dados: `EMPIRICO`.

## 1. Resultado

**SIH (a13b).** A safra v2 difere da v1 em todos os 11 meses de 202509 a 202607
e em nenhum outro. Os 44 meses de 202201 a 202508 são iguais célula a célula na
tabela UF × mês × grupo, em AIH, internações e valor.

Meses revistos frente à v1:
<!-- sih_meses_revisados -->
202509, 202510, 202511, 202512, 202601, 202602, 202603, 202604, 202605, 202606, 202607
<!-- /sih_meses_revisados -->

- A diferença cresce para o fim da série: 57 AIH em 202509 (0,005%), cerca de
  7 mil em 202605 (0,6%), cerca de 19 mil em 202606 (1,6%) e cerca de 60 mil em
  202607 (5,0%). No grupo 04 (cirurgias, insumo do K2), a v2 tem cerca de 36 mil
  AIH a mais que a v1 nos 11 meses somados; 23 mil delas em 202607 (4,1% do mês).
- A revisão não é só acréscimo: em 11 células UF × mês × grupo a v2 tem menos
  AIH que a v1 (por exemplo, SP em 202605–202607).
- Em 202607, AC e RR estavam sem dado na v1 (ausentes, nunca zero). Na v2 as duas
  UF têm arquivo; RR 202607 ficou atípico (abaixo de 0,5 × a mediana da UF), e
  RR 202606 deixou de ser. A mediana de RR usada pelo alerta mudou porque os
  meses mudaram.
- O total nacional da v2, por grupo, é igual ao total por local de internação que
  o a15 consultou por volta das 20h UTC, nos 55 meses. A fonte não mudou entre a
  extração do a15 e a v2.

**SIA (a12b).** Nenhuma revisão. As 14.250.618 células município × mês ×
subgrupo × conjunto de CBO dos 11 meses são iguais nas duas safras, e as sete
validações do a12 passaram na v2.

Meses do SIA com revisão frente à v1:
<!-- sia_meses_revisados -->
Nenhum.
<!-- /sia_meses_revisados -->

**Consequência para o adendo §12.1.**
- K2: a reestimação em D1 e D2 com a v2 tem insumo pronto em
  `output/aquisicao/sih_v2/`. Ela não foi feita aqui; é tarefa de estimação.
- K1: o adendo manda reestimar "se houver revisão". Nesta extração o SIA não foi
  revisto, então a v2 do SIA reproduz a v1 nos meses em que a revisão era
  plausível.

## 2. Como as safras foram feitas

Os dois scripts são embrulhos finos. Cada um carrega o módulo original (a13 ou
a12) e troca só os caminhos de saída e de cache para a pasta da safra. Consultas,
leitor, validações, regras de zero e ausência, esquema dos painéis e manifesto
são os do script original, sem cópia. Rodado sozinho, o a13 continua gravando em
`output/aquisicao/sih/` e o a12 em `output/aquisicao/sia/`; nada da v1 foi
sobrescrito.

| | SIH v2 (a13b) | SIA v2 (a12b) |
|---|---|---|
| Pasta | `output/aquisicao/sih_v2/` | `output/aquisicao/sia_v2/` |
| Meses de processamento | 202201–202607 (55, o plano do a13) | 202509–202607 (11) |
| Consultas | 8 × 55 = 440 | 7 × 11 + 10 de conferência = 87 |
| Extração (UTC) | 19/10/2026, 20h56–21h09 | 19/10/2026, 21h09–21h15 |
| Extração da v1 (UTC) | 19/10/2026, 12h23–12h42 | 19/10/2026, 12h52–12h58 (nesses meses) |
| Falhas | nenhuma | nenhuma |

As consultas foram sequenciais, com pausa entre elas e espera crescente em caso
de falha. Para cada consulta, o manifesto da safra guarda URL, corpo do POST,
data e hora, SHA-256 e tamanho da resposta. O bloco `safra` do manifesto guarda a
versão, o SHA-256 do script original, a primeira e a última hora de extração e os
SHA-256 das comparações. Nenhum mês ≥ 202609 é pedido.

Duas adaptações do SIA, fixadas antes de baixar a v2:
- só os 11 meses em que a revisão era plausível (A15 §5);
- a conferência célula a célula de AC e RR (V5 do a12) usa 202509, o primeiro mês
  da janela, porque o mês fixado no a12 (202506) fica fora dela.

## 3. Comparação

**SIH, UF × mês × grupo** (`comparacao_v2_v1_uf_mes_grupo.csv`):
- soma de municípios e "município ignorado" da UF, a mesma soma que reproduz a
  linha da UF no TabNet; o exterior fica fora;
- AIH aprovadas, internações e valor total nas duas safras e a diferença;
- número de municípios com AIH diferente;
- situação: `igual` (AIH e internações idênticas, valor dentro do arredondamento,
  nenhum município diferente), `diferente`, ou `ausente_so_na_v1` /
  `ausente_so_na_v2` / `ausente_nas_duas` quando a UF-mês está sem dado numa
  safra. Ausente continua ausente; nunca vira zero na comparação.

**SIH, mês** (`comparacao_v2_v1_mes.csv`): total nacional das validações de cada
safra, diferença absoluta e relativa, grupo 04, UF com diferença, sinal de mês
revisto e a conferência com o a15.

**SIA, célula a célula** (município × mês × subgrupo × conjunto de CBO):
- `comparacao_v2_v1_mes_conjunto.csv`: células, iguais, diferentes, ausentes,
  quantidade nas duas safras;
- `comparacao_v2_v1_uf_mes_conjunto.csv` e `comparacao_v2_v1_subgrupo_mes_conjunto.csv`:
  o mesmo resumo por UF e por subgrupo;
- `comparacao_v2_v1_celulas_diferentes.parquet`: as células diferentes (vazio
  nesta extração).

Subgrupo que é coluna numa safra e não na outra não tem linha naquela safra
(regra do a12). Ele só conta como diferença se a quantidade da safra que tem a
linha for maior que zero.

## 4. Limites

- A v2 é outra fotografia da mesma fonte, não a versão definitiva. Os meses
  recentes podem continuar mudando; a janela de revisão observada no SIH (11
  meses) é maior que os "seis meses" do aviso do TabNet.
- A v1 continua sendo a principal (adendo §12.1): o resultado do K2 já foi
  visto. As duas versões são relatadas lado a lado.
- A comparação do SIH é por UF; a contagem de municípios com AIH diferente
  indica onde a revisão caiu, sem detalhar por município no relato.
- Mês de processamento, não de atendimento ou internação: AIH reapresentadas
  podem mudar de mês entre safras.

## 5. Reprodução

```bash
python3 scripts/aquisicao/a13b_safra_v2_sih.py                     # verificar (sem rede, não grava)
python3 scripts/aquisicao/a13b_safra_v2_sih.py --etapa tudo        # baixa para o cache da v2, consolida e compara
python3 scripts/aquisicao/a12b_safra_v2_sia.py                     # verificar
python3 scripts/aquisicao/a12b_safra_v2_sia.py --etapa tudo
python3 -m pytest tests/test_aquisicao_safras_v2.py
```

O `run_all.py` roda os dois em `--etapa verificar`: o a12b depois do a12 e o a13b
depois do a15. O cache bruto de cada safra fica fora do controle de versão. Uma
nova extração pode não reproduzir os SHA-256 dos meses recentes.
