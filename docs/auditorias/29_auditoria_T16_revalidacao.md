# Auditoria independente da revalidação do T1.6 (adendo §8 do protocolo 52)

> **Data:** 25/10/2026.<br>
> **Objeto:** commits `046720e` (adendo §8) e `d0b0dee` (implementação): `scripts/rdd_bolsa/25b_cenarios_bolsa.py`,
> `output/cenarios/`, [doc 57b](../06_execucao/57b_cenarios_P1_bolsa.md), mudanças em `33_sintese_perguntas.py`,
> docs 57 e 38, contra o [protocolo 52, §7 e §8](../06_execucao/52_protocolo_P1_escolha_dap.md).<br>
> **Veredito:** **APROVADO COM RESSALVAS DE RELATO.** Protocolo respeitado, validação de base reproduzida, Δ total de
> C1 e C2 reproduzido com código próprio dentro do ruído de simulação. Nenhum achado substantivo; três de severidade baixa.
> **Natureza:** os números de cenário abaixo são recomputações de simulação (`CENARIO_CONTRAFACTUAL`), não observação.

## 1. Verificações e números

| # | Verificação | Resultado |
|---|---|---|
| 1 | Ordem do protocolo | `046720e` (adendo) precede `d0b0dee` (resultados). O adendo só toca `52_protocolo...md` (+49 linhas). §8.1 fixa o desempate, incluindo a posição do sorteio entre os observados empatados: `(mín. T − 0,5) + u·(máx. T − mín. T + 1)`, `u` puro se T vazio. §8.2 mantém tolerância max(3; 2%), regra "em todas as réplicas", R = 200, semente 20261024, M1 e S1–S4, C1–C4. No código, o diff de 25b muda só o desempate (`referencia_desempate`, `desempate_par`, chamada do `alocar`), a opção `--depurar`, o histórico de 24/10 e o texto. Constantes, cenários e modelos idênticos. **Nenhuma mudança além do desempate.** |
| 2 | Execução de depuração | A nota de processo declara uma depuração com R = 2 que só roda a validação de base e não grava nada; passou e não calculou cenários. Compatível com o adendo (§8.3 permite) e com minha reprodução (item 3). |
| 3 | B0, código próprio | Reconstruí listas, sorteio condicional, desempate do §8 e chamei só o `alocar` e o `preparar` do G2 (não usei função de 25b). B0 = **529 / 1057 / 705** vagas (ciclos 1–3) em todas as réplicas rodadas, igual à coluna G2 principal do csv de validação. Contra o observado (527 / 1057 / 704): desvio máximo **2** (ciclo 1, total). Ciclo 1, Faixa 3: B0 = **184** contra observado **183** (desvio 1, tolerância 3,66). Todas as 12 linhas passam; mín. = máx. em todas (B0 não varia, pois todos os pares são observados). |
| 4 | Δ total, código próprio (60 réplicas, semente própria 777) | C1: **+10,95** (EP 0,61); script: **+11,60** (EP 0,39, R = 200). C2: **+14,52** (EP 0,95); script: **+14,54** (EP 0,49). Diferença de C1 = 0,65, abaixo de 1,1 EP da diferença; C2 = 0,02. Por ciclo (C1): meu −0,03 / 4,58 / 6,40; script −0,46 / 5,49 / 6,58. Compatível com o ruído. |
| 5 | C2 == C4 | Nas 5 variantes, as 7 saídas de vagas (total, faixas, mudam, deixam, passam) são iguais réplica a réplica; só o custo difere. Igualdade esperada: as grades diferem por constante, e o logit só usa diferenças entre células. Reproduzi igual no meu código (C2 = C4 em todas as réplicas). |
| 6 | Limites S1/S2 (somando ciclos 1–3, das 200 réplicas) | C1: S1 −0,22; principal 11,60; S3 11,64; S2 18,58; S4 6,38. C2: −0,22; 14,54; 13,64; 18,06; 5,48. C3: +0,44; −6,88; −7,62; −19,64; −7,18. S1 (β no limite inferior, ≈ 0) dá efeito nulo; S2 maior em módulo que o principal em todos os cenários; ordem coerente (C3 com sinal negativo, em ordem inversa). Não há ordenação exigida entre S3/S4 e o principal. |
| 7 | Rotulagem | Todos os 6 arquivos de dados em `output/cenarios/` (4 csv, 1 parquet, 1 json) têm `natureza_dos_dados = CENARIO_CONTRAFACTUAL`; nada de cenário em `output/rdd_bolsa/` (o resumo declara `saidas_em_output_rdd_bolsa: false`). Docs 57 e 38 e `S57_*` não contêm número simulado (busca por 11,6; 14,5 relativo a T1.6; 27,1; 117,2: só ocorrências de outras estimativas). O 57b abre com o aviso de simulação e a seção 7 declara o limite de candidatos e vagas fixos ("Só redistribuição"), a incerteza herdada do M1 (IC do β contém zero) e a leitura por faixa, não por ponto. |
| 8 | Falha de 24/10 preservada | `P1_cenarios_validacao_base_falha_2026-10-24.csv` é **idêntico byte a byte** ao csv da base (`diff` vazio). O texto antigo da seção 4 reaparece na seção 9.1 sem alteração de número ou de conclusão; mudanças: título, "(nenhuma foi executada em 24/10)" e a marca da opção 1 como escolhida em 25/10. A tabela da falha foi regerada do csv preservado. |
| 9 | Privacidade | Sem identificador de candidato (`c1_00001` etc.), CPF (11 dígitos ou formatado), CNS, CRM ou nome em csv, parquet e json de `output/cenarios/` e nos dois `S57_*`. As menções a "nome e CPF" no json são texto de proveniência ("só em memória"). Nenhum arquivo de `data/` no diff. |
| 10 | Testes | `python -m pytest tests/test_cenarios_bolsa.py tests/test_sintese_perguntas.py -q`: **41 passed** (inclui `test_desempate_do_adendo_8`, que confere 4,0, +∞ e 3,5 nos casos do §8). |

## 2. Achados

| Severidade | Achado | Ação |
|---|---|---|
| Baixa | O doc 57b diz que a faixa S3 do total em C1 "contém zero", mas o limite inferior é −0,025 (exibido "−0,0"). Vale por 0,025; a leitura deve ser "tangencia zero". | Relato; não corrigi, porque o doc é gerado por script e o conteúdo é do autor. |
| Baixa | A validação de base agora testa o mecanismo do G2, não o modelo nem o sorteio: B0 é determinístico e igual ao G2 principal (mín. = máx.). Passar a tolerância (≤ 2 vagas de desvio) não valida a parte nova dos cenários (pares novos e o posicionamento do sorteio), que só aparece nos cenários. O 57b diz isso na seção 3, mas a seção 7 sobre desempate poderia citar a ausência de teste de pares novos. | Relato. |
| Baixa | Em `S57_tabela_perguntas.csv` a linha T1.6 mantém `natureza_dos_dados = EMPIRICO`, e a constante interna `FORCA_FALHA` guarda o nome histórico com o valor "cenário (simulação)". A linha não copia número simulado, e o texto diz que é cenário; a coluna de natureza fica enganosa. | Relato; mudar a natureza exige regerar a síntese. |

Nenhum achado substantivo: não há mudança de regra além do desempate, nenhum número simulado em documento empírico,
nenhuma saída de cenário fora de `output/cenarios/`.

## 3. Limites desta auditoria

- Reproduzi Δ total para C1, C2 (e C4 = C2) com 60 réplicas e semente própria; não reproduzi S1 a S4, C3 nem as saídas
  por faixa e de fluxos. A comparação de médias tem EP de 0,4 a 1 vaga.
- Reaproveitei o mecanismo (`alocar`, `preparar`, `capacidade_efetiva`) e o M1 gravado (`P1_estimativas.csv`) como insumos:
  não auditei de novo o G2 nem o M1 (auditorias G2 e 26).
- Por ser simulação com candidatos e vagas fixos, os números não identificam atração de médicos nem efeito causal; a
  auditoria não os promove a resultado empírico.
