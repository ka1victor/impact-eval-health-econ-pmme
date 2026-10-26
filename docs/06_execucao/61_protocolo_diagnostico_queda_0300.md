# 61. Protocolo: por que o preenchimento cai no corte 0,300? (diagnóstico)

> **Data de congelamento:** 26/10/2026, antes de rodar qualquer conta deste
> protocolo.<br>
> **Origem:** pedido do autor em 26/10/2026: "aprofunda até achar uma
> explicação minimamente convincente, porque vamos ter que explicar na
> apresentação".<br>
> **Estatuto:** `DIAGNOSTICO_61_POS_RESULTADO`. Nada aqui vira especificação
> principal, nem muda o Holm ou a leitura dos protocolos 40 e 48. Toda saída
> leva `natureza_dos_dados = EMPIRICO`.<br>
> **O que já foi visto** (docs 49 e 49b):
> - Em 0,300, o número de vagas preenchidas com controle (S-a) é negativo, com
>   IC que exclui zero, mas sem passar no Holm.
> - A taxa por vaga oferecida cai, com IC que exclui zero; o resultado depende
>   da medida.
> - A célula aberta preenchida (A3) é negativa, com IC que contém zero.
> - O porte não explica a queda. A parte de cadastro reserva sobe no corte.
> - Cerca de metade da queda da taxa vem do ciclo 2.
> - Em 0,400, porte e oferta explicam a maior parte.
>
> Este protocolo lista **antes de rodar** as explicações candidatas e o teste
> de cada uma, e relata todas, qualquer que seja o resultado.

## 1. O que se quer explicar

As três quantidades em 0,300, ciclos 1–3, com a especificação dos protocolos
48 e o adendo §7:

| Quantidade | Definição |
|---|---|
| Q1 | N1 com controle (S-a) |
| Q2 | taxa N1 ÷ vagas oferecidas, ponderada pelas vagas |
| Q3 | A3, célula aberta preenchida, no nível da célula |

O corte 0,400 entra como **contraste** em todas as linhas.

## 2. Explicações candidatas e testes (lista fechada)

| Id | Explicação | Teste | O que contaria como apoio |
|---|---|---|---|
| **D-a** | **Acaso:** um salto desse tamanho é comum em cortes que não existem | Cortes placebo de 0,250 a 0,450, passo 0,005, sem os pontos a menos de h = 0,050 dos cortes reais, com a mesma especificação de Q1, Q2 e Q3. Relatar a posição do salto real na distribuição dos placebos (p por posto) e a fração de placebos com \|t\| > 1,96. Randomização local (Fisher, 999 permutações, semente 20261026) nas janelas ±0,010 e ±0,020 | o salto real não se destaca dos placebos (p por posto > 0,10) |
| **D-b** | **Composição das vagas:** acima do corte há mais vagas de cadastro reserva, de cursos ou de estabelecimentos que preenchem menos | (i) salto no corte, por ciclo, da composição: parte de CR, células só de CR, curso, tipo e gestão do estabelecimento, vagas imediatas por célula. (ii) Q3 no nível da célula com efeitos fixos de curso × ciclo, indicador de célula só de CR, tipo e gestão do estabelecimento, comparado com Q3 sem eles. (iii) Q2 sem as células só de CR | o salto cai pela metade ou mais ao fixar a composição |
| **D-c** | **Funil:** onde a célula se perde | Decompor Q3 em P(ter candidato de 1ª opção) e P(preenchida \| tem candidato de 1ª opção); a segunda, também por motivo de não alocação quando a base distinguir (nota insuficiente contra a da 2ª opção; desclassificação). Salto de cada parte no corte | a queda se concentra numa das partes |
| **D-d** | **Concorrência:** células acima do corte disputam candidatos com mais células próximas ou de bolsa igual ou maior | Para cada célula: nº de células do mesmo curso e ciclo na mesma região de saúde e na mesma UF, e a bolsa média delas. Salto no corte dessas medidas; Q3 controlando por elas | as medidas de concorrência saltam no corte, e controlar por elas reduz o salto |
| **D-e** | **Médicos por perto:** do lado de cima há menos especialistas por perto, mesmo com o IVS contínuo | Balanço no corte, pré-determinado: vínculos pré (202406–202506) das CBO do curso na região de saúde por 10 mil hab.; distância da célula à origem mais próxima entre os candidatos do curso e ciclo (G1); hierarquia urbana (REGIC) | as medidas saltam no corte, e controlar por elas reduz o salto |
| **D-f** | **Ciclo 2 e cadastro reserva:** a queda é mecânica no ciclo 2 | No ciclo 2: Q2 com e sem as células só de CR; Q2 só com vagas imediatas; nº de células só de CR de cada lado; a regra do edital do ciclo 2 sobre o uso do CR na 1ª chamada (citar o item) | a queda do ciclo 2 some sem as células só de CR |
| **D-g** | **Outras políticas em 0,300** | Sem teste causal possível. Placebo de balanço com generalistas pré por 10 mil hab. e com vínculos SUS totais pré no corte; listar as regras da auditoria 18 que mudam em 0,300 e não em 0,400 | — (relato) |

**Inferência:**
- especificação base dos protocolos 48 e §7: local linear, kernel triangular,
  h = 0,050, uma reta de cada lado por ciclo, CR1 por município;
- BKY entre as linhas de salto de cada explicação;
- nenhuma linha é primária.

## 3. Leitura pré-registrada

Ao final, uma tabela "quanto da queda cada explicação leva", em que cada linha
traz o salto de Q1, Q2 e Q3 depois de fixar o fator dela, ao lado do salto
original.

| Situação | Leitura |
|---|---|
| D-a apoia | a explicação principal é **acaso mais poucos municípios**; as outras viram descrição |
| uma ou mais de D-b a D-f reduzem o salto pela metade ou mais | essas são as explicações candidatas, ditas como **descritivas** |
| nada reduz o salto e D-a não apoia | **não há explicação** nos dados disponíveis, e isso é relatado assim |

## 4. Saídas

| Item | Onde |
|---|---|
| script | `scripts/rdd_bolsa/38_diagnostico_queda_0300.py` |
| estimativas | `output/rdd_bolsa/DQ_estimativas.csv`, `DQ_resumo.json`, `DQ_figuras/` |
| resultados | `docs/06_execucao/57l_diagnostico_queda_0300.md`, gerado entre marcadores |
| testes | `tests/test_diagnostico_queda_0300.py` |

## 5. Integridade

- Nada imputado.
- Ausente fica ausente.
- O arquivo de IVS errado não é lido.
- Nenhum CNES ≥ 202609.
- Sem identificador pessoal em `output/`.
- As saídas de outros blocos não são regravadas.
