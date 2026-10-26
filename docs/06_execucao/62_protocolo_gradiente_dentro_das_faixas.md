# 62. Protocolo: por que o preenchimento sobe com o IVS dentro das faixas? (descritivo)

> **Data de congelamento:** 26/10/2026, antes de rodar qualquer conta deste
> protocolo.<br>
> **Origem:** o autor olhou a figura de dados crus do deck
> (`output/apresentacao_banca2/exp_rdd_crua.png`). Nas faixas de R$ 10 mil e de
> R$ 15 mil, a fração de células preenchidas parece subir à medida que o IVS
> aumenta.<br>
> **Estatuto:** `DESCRITIVO_62_POS_RESULTADO`. Não é contraste causal nem muda
> nenhum protocolo anterior. Toda saída leva `natureza_dos_dados = EMPIRICO`.<br>
> **O que já foi visto:**
> - a figura citada;
> - o diagnóstico 61 (doc 57l, preliminar);
> - no logit do P1 (doc 57a), as células do Nordeste, do Norte e do
>   Centro-Oeste são mais escolhidas que as do Sudeste.

## 1. Pergunta e quantidade

Dentro de cada faixa da bolsa, onde a bolsa é constante, como muda a
probabilidade de a célula aberta ser preenchida na 1ª chamada à medida que o
IVS aumenta?

**Faixas:**
- R$ 10 mil: IVS até 0,300;
- R$ 15 mil: de 0,301 a 0,400;
- R$ 20 mil: acima de 0,400.

**Amostra e modelo:** células abertas dos ciclos 1–3, a mesma base do A3
(adendo §7 do protocolo 48). Para cada faixa, um modelo de probabilidade linear
da célula preenchida no IVS contínuo, com efeito fixo de ciclo e erro-padrão
agrupado por município.

**Principal:** a inclinação por 0,100 de IVS, em toda a faixa e na janela de
0,050 junto ao corte superior da faixa.

## 2. Explicações candidatas (lista fechada; todas relatadas)

Para cada uma: quanto a inclinação muda quando o fator entra no modelo.

| Id | Explicação | Fator acrescentado |
|---|---|---|
| G-a | região: IVS maior está mais no Norte e no Nordeste, onde há mais candidatos que ficam perto de casa | efeito fixo de macrorregião; depois, de UF |
| G-b | oferta de candidatos por perto | nº de candidatos do mesmo curso e ciclo com origem (G1) na mesma UF e na mesma região de saúde da célula, por vaga oferecida |
| G-c | composição das vagas | efeito fixo de curso × ciclo; célula só de cadastro reserva; tipo e gestão do estabelecimento |
| G-d | porte e hierarquia urbana | log(população 2022); REGIC |
| G-e | concorrência | nº de células do mesmo curso e ciclo na região de saúde |
| G-f | outras políticas que variam com o IVS | sem fator testável no nível da célula; relatar o que a pesquisa documental do mesmo dia achar |

**Relato:**
- tabela com a inclinação original e a inclinação depois de cada fator,
  separadamente, e com todos juntos;
- figura de médias por faixa de IVS de 0,010, com a reta e a reta ajustada;
- "Como ler" em cada figura.

**Inferência:** BKY entre as inclinações; nenhuma linha é primária.

## 3. Leitura pré-registrada

| Situação | Leitura |
|---|---|
| um fator reduz a inclinação pela metade ou mais | ele descreve a subida (associação) |
| nenhum fator reduz | a subida não se explica com os dados disponíveis |

Em qualquer caso é **descritivo**: diz com o que a subida anda junto, não por
quê.

## 4. Saídas

| Item | Onde |
|---|---|
| script | `scripts/rdd_bolsa/39_gradiente_faixas.py` |
| estimativas | `output/rdd_bolsa/GF_estimativas.csv`, `GF_resumo.json`, `GF_figuras/` |
| resultados | `docs/06_execucao/57m_gradiente_faixas.md` |
| testes | `tests/test_gradiente_faixas.py` |

## 5. Integridade

Valem as regras de sempre:
- nada imputado;
- ausente fica ausente;
- o arquivo de IVS errado não é lido;
- nenhum CNES ≥ 202609;
- sem identificador pessoal em `output/`;
- as saídas de outros blocos não são regravadas.
