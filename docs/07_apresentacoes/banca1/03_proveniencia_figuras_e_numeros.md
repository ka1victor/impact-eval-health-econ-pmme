# Proveniência de figuras e números — banca 1

> **Classificação:** registro de proveniência, exigido antes da apresentação<br>
> **Regra aplicada:** todo número exibido declara fonte, data de referência, cobertura, unidade e reprodutibilidade<br>
> **Conteúdo dos slides:** [02_conteudo_slides.md](02_conteudo_slides.md)<br>
> **Atualização:** 9 de setembro de 2026

---

## 1. Figuras

| Código | Figura | Slide | Arquivo | Origem | Estado |
|---|---|:---:|---|---|:---:|
| `F1` | Manchetes sobre urgência em saúde e o programa | 3 | `figuras/motivacao_manchetes.png` | recortes de imprensa e gov.br | ✅ |
| `F2` | Especialistas por 100 mil habitantes, por UF, 2024 | 4 | `figuras/especialistas_por_uf.png` | Demografia Médica no Brasil 2025 | ⚠️ `P1` |
| `F3` | Deslocamento médio para alta complexidade, por região | 4 | `figuras/deslocamento_por_regiao.png` | REGIC 2018, cálculo externo | ⚠️ `P1` |
| `F4` | Bolsa mensal por faixa de atração | 5 | `output/apresentacao_banca1/bolsa_por_faixa.png` | Lei nº 15.233/2025 e edital | ✅ gerada por script |
| `F5` | Participação regional: estoque 2024 e PMM-E ciclo 1 | 6 | `output/apresentacao_banca1/distribuicao_regional.png` | `data/pmm_especialistas_nominal.csv` + Demografia Médica 2025 | ✅ gerada por script |

`F4` e `F5` são produzidas por
[`scripts/apresentacao/gerar_figuras_banca1.py`](../../../scripts/apresentacao/gerar_figuras_banca1.py),
que grava também `output/apresentacao_banca1/manifesto_figuras.json` com o
hash SHA-256 da base de entrada, o recorte aplicado, a data de referência e as
constantes externas usadas.

`F1`, `F2` e `F3` são imagens preservadas do material anterior. Não são
reprodutíveis no repositório porque as bases de origem não estão nele.

---

## 2. Números exibidos

| Número | Slide | Fonte | Verificação |
|---|:---:|---|---|
| Urgência em saúde pública por dois anos | 3 | Correio do Povo, 07/05/2025 | recorte preservado; conferir a portaria citada |
| 10% dos especialistas atendem no SUS | 3 | Senado Notícias, 25/09/2025, citando o Ministério da Saúde | citação de segunda mão; apresentar como dado citado |
| Prorrogação até fev/2027; 52% no interior | 3 | gov.br — Agora Tem Especialistas, 26/08/2026 | comunicação oficial |
| 453,5 (DF) e 68,2 (MA) especialistas por 100 mil hab. | 4 | Demografia Médica no Brasil 2025 | ⚠️ `P1` |
| 276, 256, 179, 107 e 101 km por região | 4 | REGIC 2018, cálculo externo | ⚠️ `P1` |
| R$ 20.000 / R$ 15.000 / R$ 10.000 por faixa | 5 | Lei nº 15.233/2025 e edital | ✅ |
| Degrau de R$ 5.000 entre faixas contíguas | 5, 11 | aritmética da regra | ✅ |
| 14,5% (NE), 6,1% (N), 55,3% (SE) do estoque de 2024 | 6 | Demografia Médica no Brasil 2025 | ⚠️ `P1` |
| 60,3% (NE), 12,1% (N), 23,0% (SE) dos ativos do ciclo 1 | 6 | `data/pmm_especialistas_nominal.csv`, ciclo 1, 521 registros | ✅ reproduzido pelo script |
| 5.565 municípios; IVS de 0,066 a 0,752 | 13 | `data/ivs_ipea_2010_municipios.csv` | ✅ |
| 1.480 registros; 325 municípios; 518 CNES; 16 cursos | 13 | `data/pmm_especialistas_nominal.csv` | ✅ |
| 7.276 registros; 9 competências dez/25–ago/26 | 13 | `data/pmm_especialistas_serie_historica.csv` | ✅ |
| 678 vagas imediatas e 1.145 posições de reserva | 14 | quadro do ciclo 1, chamada 1 | ✅ |
| Denominador aprovado por célula, reprovado por vaga | 14 | portão A1, 01/09/2026 | ✅ |

---

## 3. Pendência aberta

### `P1` — Figuras e números de fonte externa sem manifesto

Não bloqueante para o conteúdo, mas exigido pela regra de proveniência do
projeto. Falta registrar, para `F2`, `F3` e a série de estoque de `F5`: edição,
tabela ou página de origem, data de referência, cobertura, unidade e hash do
arquivo obtido.

Observação adicional sobre `F2`: o gráfico exibe **16 unidades da federação**
— DF, SP, RJ, RS, SC, PR, ES, MG, MS, GO, MT, BA, PE, CE, PA e MA — não as 27. O
rótulo precisa dizer que é um recorte, ou o gráfico precisa ser completado.
Exibir 16 UFs sob um eixo que sugere o país inteiro é impreciso.

---

## 4. Pendência encerrada

### `P0` — Distribuição regional do PMM-E que não reproduzia

**Encerrada em 09/09/2026.** A figura equivalente do material anterior exibia
valores que não se obtinham de nenhuma base de `data/`. Apenas o Nordeste
coincidia.

| Região | Material anterior | Base do repositório, ciclo 1 | Diferença |
|---|---:|---:|---:|
| Nordeste | 60,3% | 60,3% | 0,0 p.p. |
| Norte | 18,0% | 12,1% | −5,9 p.p. |
| Centro-Oeste | 6,8% | 3,6% | −3,2 p.p. |
| Sudeste | 10,6% | 23,0% | **+12,4 p.p.** |
| Sul | 4,3% | 1,0% | −3,3 p.p. |

Recortes alternativos testados e descartados como origem da série: cadastro
nominal com os ciclos 1 e 2 (58,5 / 12,4 / 3,0 / 24,6 / 1,6), série histórica na
competência dez/2025 (60,1 / 12,1 / 3,8 / 23,1 / 0,9) e contagem de municípios
distintos com profissional ativo (46,8 / 14,2 / 6,8 / 28,0 / 4,3). Nenhum
reproduz o conjunto.

O erro era material: a participação do Sudeste estava subestimada em mais de
doze pontos percentuais, o que **exagerava a redistributividade** afirmada no
slide. A figura foi regerada por script a partir da base, e o achado está
registrado em
[`docs/04_dados/02_inventario_dados_por_outcome.md`](../../04_dados/02_inventario_dados_por_outcome.md),
seção 4.1.

---

## 5. Regra permanente

1. Figura derivada de base do repositório é gerada por script versionado e lida
   de `output/`. Não se cola imagem produzida fora do pipeline.
2. Figura de fonte externa é preservada em `figuras/`, com a fonte declarada na
   legenda e uma linha nesta tabela.
3. Figura conceitual, que ilustra o modelo em vez de mostrar dado, recebe rótulo
   explícito de ilustração.
4. Número exibido sem linha na tabela da seção 2 é erro, não detalhe editorial.
