# Resultados da RDD da bolsa no IVS 2010 oficial

> **Data:** 2026-10-14.<br>
> **Estado:** `E3_CONCLUIDO_SEM_EFEITO_DETECTAVEL`.<br>
> **Protocolos:** [`protocolo_escore_administrativo.json`](../../output/rdd_bolsa/protocolo_escore_administrativo.json)
> (commit `be11852`, congelado antes de qualquer contagem por ciclo) e
> [`protocolo_E4_adendo_proporcao.json`](../../output/rdd_bolsa/protocolo_E4_adendo_proporcao.json)
> (commit `2996bf0`). Nenhum dos dois foi pré-registrado; as exposições prévias
> a outcomes estão listadas neles.<br>
> **Relatório com figuras:** `output/rdd_bolsa/relatorio_resultados_rdd_bolsa.pdf`.

## 1. Pergunta e contraste

Hipótese da banca 1, na forma local: no corte do IVS 2010 oficial, onde a bolsa
anunciada sobe **R$ 5 mil** e o custo do lugar varia continuamente, os
municípios do lado de cima têm mais preenchimento e mais presença de
especialistas?

O contraste é o **incentivo marginal anunciado**:
- Faixa 3 → Faixa 2 em 0,300;
- Faixa 2 → Faixa 1 em 0,400.

Não é o efeito do PMM-E nem do Agora Tem Especialistas. Se outra política
mudar nos mesmos cortes de IVS, por exemplo a ajuda de custo do PMMB por
categoria, o contraste mede o pacote.

## 2. Identificação

- **Running variable:** IVS 2010 oficial do Ipea, que é o escore
  administrativo do MS ([`auditorias/16`](../auditorias/16_ivs_2010_oficial_e_arquivo_local.md)).
- **Primeiro estágio sharp:** a faixa anunciada é reproduzida em 368 de 368
  municípios do ciclo 1 e em 454 de 454 do ciclo 2.
- **Manipulação:** o IVS 2010 foi calculado em 2015, com dados de 2010, uma
  década antes do programa. A densidade dos municípios com vaga não salta nos
  cortes:

  | Corte (ciclo 1) | Razão de densidades | IC 95% |
  |---|---:|---|
  | 0,300 | 0,93 | [0,40; 2,16] |
  | 0,400 | 0,61 | [0,29; 1,30] |

  No ciclo 2, a razão é 1,09 em 0,300 e 0,96 em 0,400.
- **Balanço de covariáveis pré-programa** (h = 0,050):
  - **Ciclo 1, corte 0,300:** sem desequilíbrio.
  - **Ciclo 1, corte 0,400:** três desequilíbrios com p < 0,05, todos no
    sentido de municípios menos metropolitanos acima do corte:
    - subíndice de capital humano: +0,036 (p = 0,020);
    - estrato interior próximo de polo: +0,39 (p = 0,018);
    - estrato metropolitano: −0,24 (p = 0,043).
  - **Ciclo 2, corte 0,300:** capital −0,22 (p = 0,025).

  São nove covariáveis por corte, e parte disso é esperada por acaso. O corte
  de 0,400 do ciclo 1 merece cautela. O `ivs_2010` não conta: com a base
  oficial, ele é a própria running variable, e o "salto" dele é zero por
  construção. Até 18/10/2026, o `E3_diagnosticos.csv` trazia p-valores desse
  ruído numérico (0,026 a 0,00006). Agora a linha sai sem teste, com nota. Os
  três subíndices são componentes do IVS, cuja média é contínua no corte; os
  saltos deles não são testes independentes.

## 3. Resultado principal (E3)

RDD sharp local linear, kernel triangular, h = 0,050, EP HC1 por município
([`E3_estimativas.csv`](../../output/rdd_bolsa/E3_estimativas.csv)).

**Como ler o salto:** valor estimado no corte do lado com bolsa maior (IVS
acima do corte) menos o do lado com bolsa menor:
- em 0,300, de R$ 10 mil para R$ 15 mil;
- em 0,400, de R$ 15 mil para R$ 20 mil.

Positivo significa mais preenchimento ou presença onde a bolsa é maior. O
sinal foi conferido no código e nos dados por
`scripts/rdd_bolsa/09b_conferir_sinal.py`, com resultado em
[`E3_conferencia_sinal.json`](../../output/rdd_bolsa/E3_conferencia_sinal.json):
- o lado de cima do corte tem bolsa maior em todos os municípios dos ciclos 1
  e 2;
- uma reestimação independente reproduz o salto nas 18 especificações.

| População | Outcome | Corte | n abaixo / acima | Salto | IC 95% | p |
|---|---|---:|---:|---:|---|---:|
| Ciclo 1 | fração de células preenchidas na 1ª chamada | 0,300 | 61 / 53 | −12,8 p.p. | [−45,5; +19,8] | 0,44 |
| Ciclo 1 | fração de células preenchidas na 1ª chamada | 0,400 | 53 / 41 | −5,1 p.p. | [−36,5; +26,2] | 0,75 |
| Ciclo 1 | especialista do ciclo ativo em 09/10/2026 | 0,300 | 61 / 53 | −3,2 p.p. | [−47,5; +41,1] | 0,89 |
| Ciclo 1 | especialista do ciclo ativo em 09/10/2026 | 0,400 | 53 / 41 | −12,0 p.p. | [−53,1; +29,0] | 0,57 |
| Ciclo 2 (replicação) | especialista do ciclo ativo | 0,300 | 82 / 61 | −15,2 p.p. | [−51,6; +21,1] | 0,41 |
| Ciclo 2 (replicação) | especialista do ciclo ativo | 0,400 | 53 / 53 | +11,5 p.p. | [−13,9; +36,9] | 0,38 |

As janelas de 0,030 e 0,080 não mudam a leitura: nenhum salto distinguível de
zero, e o menor p é 0,155.

**Leitura.** Não detectamos efeito do anúncio de +R$ 5 mil sobre preenchimento
ou presença nos cortes. Os intervalos são largos. O efeito mínimo detectável
(2,8 × EP) é de cerca de **45 p.p.** para a fração de células preenchidas e
**60 p.p.** para a presença no ciclo 1. A RDD descarta efeitos muito grandes,
mas **não descarta efeitos grandes em nenhuma direção**. A conclusão é "sem
evidência de efeito, com baixa precisão", e não "a bolsa não funciona".

As médias brutas são maiores do lado de cima em alguns cortes (0,24 → 0,37 na
fração de células em 0,300). Isso reflete a inclinação em relação ao IVS
dentro da janela, que o modelo local linear absorve. Não é salto. Em 0,300, a
reta do lado de R$ 10 mil chega ao corte em 40,7%, e a do lado de R$ 15 mil
parte de 27,9%; a diferença bruta de +12,9 p.p. se decompõe em −12,8 de salto,
+26,5 de inclinação e −0,7 de resíduo (`E3_conferencia_sinal.json`).

**Inferência alternativa (exploratória, pós-resultado).** Ver
[`39`](39_inferencia_alternativa_rdd_bolsa.md). São 15 especificações
alternativas: local constante, cortes empilhados, covariáveis, local
randomization e nível célula.
- **Nenhuma é distinguível de zero;** o menor p é 0,44.
- **O que fica descartado:** a 5% unilateral, saltos de +15 p.p. ou mais no
  corte de 0,300 (limite superior de 14,5 p.p.) e saltos médios de +15 p.p.
  com os cortes empilhados.
- **O que não fica descartado:** efeitos de +10 p.p., em nenhuma
  especificação.
- **O IC é largo** pelo outcome ruidoso, por 41 a 61 municípios por lado e
  pela extrapolação local linear, que multiplica o EP por 2,2 a 2,6 em relação
  à diferença de médias.

## 4. Antes do escore completo (exploratórios, superados pelo E3)

| Componente | O que fez | Resultado |
|---|---|---|
| E1 | razão de densidades dos municípios com especialista ativo, só com os 404 escores publicados | 0,81 [0,28; 2,40] em 0,300 e 0,58 [0,19; 1,75] em 0,400 |
| E2 | limites com escore ausente | todos os intervalos principais contêm zero |
| E4 | limites e Lee para a fração preenchida | todos os intervalos principais contêm zero |

E1, E2 e E4 são coerentes com o E3. O cenário "informado" de E2 e E4 usou o
arquivo local como banda e fica superado.

## 5. Limites

1. **Poder:** cerca de 60 municípios de cada lado na janela principal. Mesmo
   juntando ciclos, efeitos moderados ficariam fora do alcance.
2. **Retrospectivo:** os protocolos foram congelados depois de exposições
   parciais a outcomes, listadas em cada um.
3. **Outcome de presença:** é um retrato em 09/10/2026, não retenção
   individual.
4. **Pacote:** outros benefícios ligados à categoria de IVS podem mudar nos
   mesmos cortes. Não foram mapeados.
5. **Desequilíbrio** no corte de 0,400 do ciclo 1.

## 6. Reprodução

Em ordem:

1. `scripts/aquisicao/a07_adquirir_ivs_administrativo.py`;
2. `scripts/aquisicao/a08_adquirir_ivs_2010_oficial.py`;
3. `scripts/rdd_bolsa/04_portao_r1_escore_administrativo.py`;
4. `scripts/rdd_bolsa/04b_validar_ivs_oficial_escore_administrativo.py`;
5. `scripts/rdd_bolsa/05_estimar_E1_densidade.py`;
6. `scripts/rdd_bolsa/06_estimar_E2_limites.py`;
7. `scripts/rdd_bolsa/07_estimar_E3_rdd_completa.py` (o escore padrão é o IVS
   oficial; equivale a `--escore output/rdd_bolsa/escore_completo_ivs2010_oficial.csv`);
8. `scripts/rdd_bolsa/08a_reconstruir_proporcao_preenchida.py`;
9. `scripts/rdd_bolsa/08_estimar_E4_proporcao.py`;
10. `scripts/rdd_bolsa/11_inferencia_alternativa.py` (E5, exploratório);
11. `scripts/rdd_bolsa/09b_conferir_sinal.py`;
12. `scripts/rdd_bolsa/09_gerar_relatorio_pdf.py`;
13. `scripts/rdd_bolsa/10_galeria_figura_regra.py`.

Ou, de uma vez: `python run_all.py --rdd-bolsa` (inclui também `04c`).
