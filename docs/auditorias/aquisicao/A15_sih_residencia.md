# A15 — SIH/SUS no TabNet: AIH por município de residência × mês × grupo (portão G3)

> **Data:** 19/10/2026.<br>
> **Tarefa:** portão G3 do plano das perguntas reformuladas
> ([`06_execucao/51`](../../06_execucao/51_plano_perguntas_reformuladas.md), P3,
> T3.4): adquirir a SIH por local de residência com as mesmas regras do
> [A13](A13_sih_tabnet.md).<br>
> **Script:** [`scripts/aquisicao/a15_adquirir_sih_residencia.py`](../../../scripts/aquisicao/a15_adquirir_sih_residencia.py).<br>
> **Números:** contagens, totais nacionais, validações por mês e status estão no
> resumo gerado,
> [`output/aquisicao/sih_residencia/a15_resumo.md`](../../../output/aquisicao/sih_residencia/a15_resumo.md),
> em [`a15_validacoes.json`](../../../output/aquisicao/sih_residencia/a15_validacoes.json)
> e no manifesto
> [`manifesto_sih_residencia.json`](../../../output/aquisicao/sih_residencia/manifesto_sih_residencia.json).
> As listas marcadas abaixo são conferidas contra o manifesto por
> `tests/test_aquisicao_sih_residencia.py`.<br>
> **Cegamento:** só aquisição. Nada foi calculado por IVS, faixa da bolsa, lado de
> corte, tratamento ou chegada; o script não lê IVS.

## 1. Veredito do G3

**VIAVEL.** O TabNet entrega a SIH por município de residência, mês de
processamento e grupo para 202201–202607, com as mesmas consultas, regras e
validações do a13. Todas as validações obrigatórias passaram.

O total nacional por residência é igual, em cada mês e grupo, ao total por local
de internação consultado na mesma execução (v8). Ele também é igual ao total
versionado do a13 em 44 dos 55 meses. Nos 11 meses finais (202509–202607), a
própria fonte foi revista entre a extração do a13 e a do a15, no mesmo dia
(seção 5). Esse achado vale também para o a13 e para o K2.

## 2. Fonte e consultas

- **Formulário:** `http://tabnet.datasus.gov.br/cgi/deftohtm.exe?sih/cnv/qrbr.def`,
  "Procedimentos hospitalares do SUS - por local de residência - Brasil". Só
  HTTP. Os campos e os `VALUE` das opções saem do formulário baixado, como no
  a13.
- **Conferência:** o formulário do a13 (`sih/cnv/qibr.def`, local de
  internação) é baixado na mesma execução. Uma consulta por mês, UF × grupo,
  serve a três usos:
  - o total nacional contemporâneo (v8);
  - a detecção de UF-mês sem arquivo de internação;
  - o alerta de UF-mês atípico.

| Consulta | Formulário | Linha | Coluna | Incremento | Filtro |
|---|---|---|---|---|---|
| `mun_grupo_aih`, `mun_grupo_internacoes`, `mun_grupo_valor` | qrbr | Município (residência) | Grupo procedimento | AIH aprovadas, Internações, Valor total | — |
| `uf_grupo_aih` | qrbr | UF (residência) | Grupo procedimento | AIH aprovadas | — |
| `procmes_grupo_aih` | qrbr | Ano/mês processamento | Grupo procedimento | AIH aprovadas | — |
| `mun_carater_g04_aih` | qrbr | Município (residência) | Caráter atendimento | AIH aprovadas | Grupo = 04 |
| `mun_grupo_aih_uf_AC`, `mun_grupo_aih_uf_RR` | qrbr | Município (residência) | Grupo procedimento | AIH aprovadas | UF de residência = AC; = RR |
| `int_uf_grupo_aih` | qibr | UF (internação) | Grupo procedimento | AIH aprovadas | — |

São 9 consultas × 55 meses = 495 POSTs. Para cada um, o manifesto guarda URL,
corpo, data e hora, SHA-256 e tamanho. O leitor confere ainda o título da
página: uma resposta do formulário de internação não passa como de residência,
e vice-versa.

## 3. Tempo, lugar e unidade

- **Tempo:** mês de processamento (arquivo `qrbrAAMM.dbf`), conferido pela v4.
  Não é o mês da internação nem o da alta. Nenhum mês ≥ 202609 é pedido.
- **Lugar:** município de **residência** do paciente. Mede o uso de internação
  pelos residentes, onde quer que tenham sido internados. Aproxima acesso, não
  oferta local (plano 51, T3.4).
- **Unidade:** município × mês × grupo do procedimento principal. A lista de
  municípios é a do formulário: 5.571 códigos, inclusive o `510183`, posterior
  ao Censo 2022, como no a13.

As colunas do painel são as do a13, mais `mes_com_falta_em_outra_uf`.

## 4. Ausências e alertas

| `status` | Valor | Quando |
|---|---|---|
| `observado`, `zero_tabnet`, `zero_coluna_omitida` | ≥ 0 | como no a13 |
| `ausente_uf_mes_sem_dado` | NaN | a UF de residência tem total zero no mês |
| `ausente_uf_internacao_sem_dado` | NaN | o arquivo de internação da própria UF falta no mês: total zero da UF na consulta `int_uf_grupo_aih` |

Por que a regra (b) existe: na residência, uma UF sem arquivo de internação não
fica zerada. Os residentes dela internados em outras UF continuam aparecendo.
Esse número parcial nunca entra no painel; o total parcial da UF fica só nas
validações.

Alertas, que não mudam o valor:
- `uf_mes_atipico`: o total da UF **de internação** no mês ficou abaixo de 0,5 ×
  a mediana mensal da UF. É a regra do a13, aplicada à consulta contemporânea;
- `mes_com_falta_em_outra_uf`: no mês, outra UF de internação está sem arquivo
  ou atípica. Os residentes desta UF internados lá podem faltar.

Listas desta execução:

UF-mês sem arquivo de internação:
<!-- uf_meses_sem_arquivo_internacao -->
Nenhum.
<!-- /uf_meses_sem_arquivo_internacao -->

UF-mês de residência zerado:
<!-- uf_meses_sem_dado -->
Nenhum.
<!-- /uf_meses_sem_dado -->

UF-mês atípico:
<!-- uf_meses_atipicos -->
- 202206 — RR
- 202309 — RR
- 202607 — RR
<!-- /uf_meses_atipicos -->

**Diferença em relação ao a13.** Na extração do a13 (19/10/2026, por volta das
12h UTC), AC e RR estavam sem dado em 202607, e RR 202606 era atípico. Na do a15
(por volta das 20h UTC), AC e RR **têm** arquivo em 202607, e RR 202606 deixou
de ser atípico. RR 202607 está presente, mas atípico (515 AIH contra uma
mediana mensal de 3.340), o que é compatível com um arquivo parcial.

## 5. Conferência com o a13 e revisão da fonte

- **v8 (obrigatória):** em todos os 55 meses, o total nacional por residência
  é igual ao total por local de internação da mesma execução, por grupo. As AIH
  são as mesmas; muda só a linha.
- **v9:** os 44 meses de 202201 a 202508 são iguais ao total versionado do a13,
  em AIH. Neles, internações e valor também conferem: internações exatamente, e
  valor dentro do arredondamento das células.
- Nos meses abaixo, o total difere do a13. Também difere do a13 o total por
  local de internação consultado agora. Portanto a fonte foi revista depois da
  extração do a13; não é diferença de conceito.

<!-- meses_revisados -->
202509, 202510, 202511, 202512, 202601, 202602, 202603, 202604, 202605, 202606, 202607
<!-- /meses_revisados -->

As diferenças crescem para o fim da série (tabela no resumo gerado):
- de dezenas de AIH em 202509;
- a cerca de 7 mil (0,6%) em 202605;
- a cerca de 60 mil (5%) em 202607.

O aviso da página, "últimos seis meses sujeitos a atualização", subestima a
janela: a revisão alcançou 11 meses.

**Consequência para o K2 (protocolo 47, adendo §10):**
- o painel versionado do a13 é anterior à revisão;
- o pós principal do K2 (202510–202605) está inteiro dentro dos meses revistos.

O a15 não altera o a13. Cabe ao autor decidir, por adendo datado, entre:
- refazer o a13 (`--etapa tudo`), o que muda o insumo do D1/D2 já estimado;
- manter a extração do a13 e registrar a revisão como limite.

## 6. Validações (fail closed)

| Id | Validação |
|---|---|
| leitor | título da fonte certo; período = mês pedido; filtro ecoado; cabeçalho; células numéricas ou `-`; Total da linha = soma das colunas; linha Total = soma das linhas |
| v1 | municípios + ignorados = Total, por grupo, nos três incrementos |
| v2 | Total municipal = Total por UF = linha do mês no processamento |
| v3 | por UF de residência × grupo: municípios + ignorado da UF = linha da UF |
| v4 | o arquivo do mês só tem AIH no próprio mês de processamento |
| v5 | grupo 04 por caráter soma o grupo 04, por município |
| v6 | AC e RR célula a célula: consulta filtrada pela UF de residência = nacional |
| v7 | municípios de cada resposta = lista do formulário |
| v8 | total nacional por residência = por local de internação, na mesma execução |
| v9 | igual ao a13 nos meses não revistos (AIH, internações e valor); mês diferente só passa se a fonte por internação também mudou |

## 7. Limites

- Sem CBO: a internação não se atribui ao especialista.
- Residência informada na AIH; erro de endereço cai no município errado ou em
  "ignorado".
- Mês de processamento, com as mesmas defasagens e reapresentações do a13. Os
  meses recentes mudam entre extrações (seção 5).
- Sem o par residência–internação: este painel diz quantas internações os
  residentes tiveram, não onde. O fluxo origem–destino exigiria uma consulta
  por município de residência ou o microdado da AIH.
- AIH aprovadas inclui as de continuação; `internacoes` exclui.

## 8. Reprodução

```bash
python3 scripts/aquisicao/a15_adquirir_sih_residencia.py                     # padrão: verificar (sem rede, não grava)
python3 scripts/aquisicao/a15_adquirir_sih_residencia.py --etapa tudo        # baixa para o cache e consolida
python3 scripts/aquisicao/a15_adquirir_sih_residencia.py --etapa consolidar  # só refaz as saídas do cache
python3 -m pytest tests/test_aquisicao_sih_residencia.py
```

O `run_all.py` roda o a15 em `--etapa verificar`, depois do a13. O cache bruto
(cerca de 76 MB) fica fora do controle de versão. Uma nova extração pode não
reproduzir os SHA-256 dos meses recentes. Se o a13 for refeito, o modo
verificar avisa que a comparação v9 ficou velha.
