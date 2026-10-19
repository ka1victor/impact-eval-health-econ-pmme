# 56. Protocolo P6: alocado por pouco contra não alocado por pouco

> **Data de congelamento:** 19/10/2026, antes de ligar os candidatos ao painel
> CNES mensal e de abrir qualquer outcome.<br>
> **Origem:** plano do doc 51 (P6), depois dos portões G1 (`VIAVEL`), G2
> (`VIAVEL_PARCIAL`) e G5 (`VIAVEL_PARCIAL`).<br>
> **Estatuto:** `EXPLORATORIO_P6`. Toda saída leva
> `natureza_dos_dados = EMPIRICO`.

## 1. O que o G2 mostrou e como o desenho responde

| Achado do G2 | Resposta do desenho |
|---|---|
| a concordância de 99% só vale com a capacidade efetiva; as vagas acrescentadas pelo item 5.7 vieram de decisão discricionária posterior às filas | **só entram células cuja capacidade efetiva é igual às vagas imediatas do quadro** |
| a nota é inteira (0–15) e há muitos empates no corte; o desempate é uma regra fixa (UF, idade), não sorteio | **principal exclui os empatados na nota de corte** (donut de um ponto); sensibilidade os inclui com indicador do desempate |
| cotas (raciais, PcD) mudam a ordem | célula × modalidade de concorrência como unidade do corte, se a modalidade estiver no dado; se não estiver, as células com cota processada ficam fora e são contadas |

## 2. Amostra

- Ciclos 1 e 2, 1ª chamada. O ciclo 3 fica fora: seguimento no CNES insuficiente
  até 202608.
- Candidatos com a 1ª opção numa célula elegível (seção 1) **com corte
  efetivo**: a última nota admitida abaixo da maior nota de quem escolheu.
- Ligados ao CNES pelo G1, regra principal. Sensibilidade só por nome.
- Variável de seleção: r = nota − nota de corte da 1ª opção.
- Principal: r ∈ {−2, −1, +1, +2}, sem r = 0.

## 3. Primeiro estágio e outcomes

**Tratamento:**
- D = alocado na 1ª opção;
- D' = alocado em qualquer célula do PMM-E;
- relatar P(D = 1 | r).

**Outcomes:** do painel a16 estendido aos candidatos (passo 0), no último mês
disponível e em média nos meses de seguimento:

| Ciclo | Seguimento |
|---|---|
| 1 | 202510–202608 |
| 2 | 202604–202608 |

| Id | Outcome |
|---|---|
| Y1 | tem vínculo cadastrado no município da 1ª opção |
| Y2 | horas SUS semanais totais |
| Y3 | horas totais |
| Y4 | tem vínculo fora do município de origem pré-programa |
| Y5 | número de municípios com vínculo |

**Passo 0** (sem abrir outcomes por r):
1. Gerar o arquivo de chaves dos candidatos ligados no G1 (fora do Git).
2. Consolidar o a16 com `--chaves-extra`, usando o cache privado copiado para
   `output/aquisicao/cnes_profissional/cache_privado/`.
3. Relatar a cobertura por mês.

## 4. Especificações

| Id | Especificação | Leitura |
|---|---|---|
| R1 | randomização local: diferença de médias entre r ∈ {+1, +2} e r ∈ {−1, −2}, com efeito fixo de célula; p-valor por permutação dentro de célula (999, semente 20261019) | **principal**, forma reduzida |
| R2 | Wald (forma reduzida ÷ primeiro estágio) com a mesma amostra | efeito de ser alocado, para os que obedecem |
| R3 | regressão com tendência linear em r de cada lado, efeito fixo de célula, cluster por célula, r ∈ [−3, +3] sem 0 | robustez |
| R4 | incluindo r = 0, com indicador de desempate | sensibilidade |
| R5 | ligação só por nome | sensibilidade |
| R6 | escore de propensão do mecanismo (Abdulkadiroğlu et al., 2017), condicionando na probabilidade de alocação dada a nota e as opções | robustez, se a forma de calcular for estável |

**Balanço:** antes dos outcomes, testar a continuidade em r das covariáveis
pré-determinadas:
- vínculo médico pré (G1);
- horas no CNES pré, a partir do a16 em 202406–202506 para quem estiver no
  painel;
- mesma UF da vaga;
- distância origem–vaga.

T6.3, a variação do mecanismo como instrumento no nível do município, **não
roda** neste protocolo. Só entra depois, se o primeiro estágio do R1 for forte
(F > 10) e houver células suficientes.

## 5. Relato

- Primeiro estágio, balanço e todos os outcomes, qualquer que seja o resultado.
- BKY entre Y1 e Y5 no R1.
- Figuras de médias por r, com "Como ler".
- Linguagem: efeito de ser alocado sobre a trajetória cadastrada do médico,
  para candidatos perto da nota de corte. Não é o efeito da bolsa.

## 6. Saídas

| Item | Onde |
|---|---|
| scripts | `scripts/rdd_bolsa/30_mecanismo_alocacao.py` (amostra e passo 0); `31_rd_mecanismo.py` (estimação) |
| estimativas | `output/rdd_bolsa/P6_estimativas.csv` |
| resumo | `P6_resumo.json` |
| figuras | `P6_figuras/` |
| resultados | `docs/06_execucao/57f_resultados_P6_mecanismo.md` |

## 7. Integridade

- Nada imputado. Candidato sem ligação fica fora e é contado.
- Sem nome, CPF, CNS ou CRM em `output/`.
- O arquivo de IVS errado não é lido.
- Nenhum mês ≥ 202609.
- Os dados nominais ficam só no cache privado fora do Git.
