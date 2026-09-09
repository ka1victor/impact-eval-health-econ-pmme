# 03. Proveniência de figuras e números — banca 1

> **Classificação:** registro de proveniência, exigido antes da apresentação<br>
> **Regra aplicada:** todo número exibido em slide declara fonte, data de referência, cobertura, unidade e reprodutibilidade<br>
> **Conteúdo dos slides:** [02_conteudo_slides.md](02_conteudo_slides.md)<br>
> **Atualização:** 9 de setembro de 2026

---

## 1. Estado geral

| Código | Figura | Slide | Origem | Reprodutível por script do repositório | Estado |
|---|---|:---:|---|:---:|:---:|
| `F1` | Recortes de imprensa e comunicação oficial | 3 | terceiros (imprensa e gov.br) | não se aplica | ✅ |
| `F2` | Especialistas por 100 mil habitantes, por UF, 2024 | 4 | Demografia Médica no Brasil 2025 | não | ⚠️ `P2` |
| `F3` | Deslocamento médio para alta complexidade, por região, km | 4 | REGIC 2018 (cálculo externo) | não | ⚠️ `P2` |
| `F4` | Bolsa mensal por faixa de atração | 5 | Lei nº 15.233/2025 e edital | sim (valores nominais da regra) | ✅ |
| `F5` | Participação regional: estoque 2024 versus PMM-E | 6 | Demografia Médica 2025 + `data/pmm_especialistas_nominal.csv` | parcialmente | 🔴 `P1` |
| `F6` | Reta de indiferença e degrau de R$ 5.000 | 11 | derivada do modelo | a produzir | 🔴 `P3` |

Legenda: ✅ fechado · ⚠️ pendência não bloqueante · 🔴 pendência bloqueante.

---

## 2. Números exibidos

| Número | Slide | Fonte declarada | Verificação |
|---|:---:|---|---|
| Urgência em saúde pública por dois anos (07/05/2025) | 3 | Correio do Povo, editoria Saúde | recorte preservado em `F1`; conferir portaria citada antes da banca |
| 10% dos especialistas atendem no SUS | 3 | Senado Notícias (25/09/2025), citando o Ministério da Saúde | citação de segunda mão; apresentar como dado citado, não como estatística própria |
| Prorrogação até fevereiro de 2027; 52% no interior; ~500 anestesiologistas | 3 | gov.br — Agora Tem Especialistas (26/08/2026) | comunicação oficial |
| 453,5 especialistas por 100 mil hab. (DF) e 68,2 (MA) | 4 | Demografia Médica no Brasil 2025 | ⚠️ `P2` |
| 276 km (Norte), 256 km (Centro-Oeste), 179 km (Nordeste), 107 km (Sudeste), 101 km (Sul) | 4 | REGIC 2018, cálculo externo | ⚠️ `P2` |
| R$ 20.000 / R$ 15.000 / R$ 10.000 por faixa | 5 | Lei nº 15.233/2025 e edital | ✅ consistente com `docs/01_pergunta_escopo/15_...md`, seção 2 |
| Degrau de R$ 5.000 entre faixas contíguas | 5, 11 | aritmética da regra | ✅ |
| 14,5% do estoque de especialistas no Nordeste; 55,3% no Sudeste | 6 | Demografia Médica no Brasil 2025 | ⚠️ `P2` |
| 60,3% dos ativos do ciclo 1 no Nordeste | 6 | `data/pmm_especialistas_nominal.csv` | ✅ reproduzido |
| Demais participações regionais do PMM-E | 6 | — | 🔴 `P1`: valores do deck anterior não reproduzem |
| 5.565 municípios; IVS de 0,066 a 0,752 | 13 | `data/ivs_ipea_2010_municipios.csv` | ✅ `docs/04_dados/02_inventario_dados_por_outcome.md` |
| 1.480 registros; 325 municípios; 518 CNES; 16 cursos; ref. 12/08/2026 | 13 | `data/pmm_especialistas_nominal.csv` | ✅ reproduzido |
| 7.276 registros; 9 competências dez/2025–ago/2026 | 13 | `data/pmm_especialistas_serie_historica.csv` | ✅ reproduzido |
| 678 vagas imediatas e 1.145 posições de reserva | 14 | quadro do ciclo 1, chamada 1 | ✅ `docs/auditorias/08_portao_denominador_atracao.md` |
| Denominador aprovado por célula, reprovado por vaga (01/09/2026) | 14 | portão A1 | ✅ mesma auditoria |

---

## 3. Pendências

### `P1` — Distribuição regional do PMM-E

**Bloqueante.** A série "PMM-E (ativos em 2025)" da figura `F5` do deck anterior
**não é reprodutível** a partir de nenhuma base preservada em `data/`. Apenas o
Nordeste coincide.

Comparação, tomando o ciclo 1 do cadastro nominal (521 profissionais,
referência 12/08/2026) como base candidata:

| Região | Deck anterior | `pmm_especialistas_nominal.csv`, ciclo 1 | Diferença |
|---|---:|---:|---:|
| Nordeste | 60,3% | 60,3% | 0,0 p.p. |
| Norte | 18,0% | 12,1% | −5,9 p.p. |
| Centro-Oeste | 6,8% | 3,6% | −3,2 p.p. |
| Sudeste | 10,6% | 23,0% | **+12,4 p.p.** |
| Sul | 4,3% | 1,0% | −3,3 p.p. |

Outras leituras testadas e descartadas como origem da série:

| Recorte alternativo | Nordeste | Norte | C.-Oeste | Sudeste | Sul |
|---|---:|---:|---:|---:|---:|
| Cadastro nominal, ciclos 1 e 2 (1.480 ativos) | 58,5% | 12,4% | 3,0% | 24,6% | 1,6% |
| Série histórica, competência dez/2025 (577 ativos) | 60,1% | 12,1% | 3,8% | 23,1% | 0,9% |
| Municípios distintos com profissional ativo (325) | 46,8% | 14,2% | 6,8% | 28,0% | 4,3% |

Nenhum recorte reproduz o conjunto. O erro é material: a participação do
Sudeste no deck anterior está subestimada em mais de doze pontos percentuais, o
que **exagera a redistributividade** que o slide 6 afirma.

Registrado também em [`docs/04_dados/02_inventario_dados_por_outcome.md`](../../04_dados/02_inventario_dados_por_outcome.md), seção 4.1.

**Ação exigida antes do deck final:** gerar a figura por script versionado a
partir de `data/pmm_especialistas_nominal.csv`, gravando a saída em `output/`,
com a unidade declarada no rótulo (profissionais ativos, ciclo 1, referência
12/08/2026). Enquanto a figura não for regerada, o slide 6 não vai ao deck.

Reprodução dos valores corretos:

```python
import csv, collections
linhas = list(csv.DictReader(open("data/pmm_especialistas_nominal.csv")))
ciclo1 = [linha for linha in linhas if linha["ciclo"] == "1"]
contagem = collections.Counter(linha["regiao"] for linha in ciclo1)
total = len(ciclo1)  # 521
```

### `P2` — Figuras de fonte externa sem manifesto

**Não bloqueante, mas exigido pela regra de proveniência.** As figuras `F2`,
`F3` e a série de estoque de `F5` vêm de fontes externas que não estão
preservadas no repositório. Falta registrar, para cada uma: edição, tabela ou
página de origem, data de referência, cobertura, unidade e hash do arquivo
obtido.

Observação adicional sobre `F2`: o gráfico exibe **16 unidades da federação**
(DF, SP, RJ, RS, SC, PR, ES, MG, MS, GO, MT, BA, PE, CE, PA, MA), não as 27. O
rótulo precisa dizer que se trata de um recorte, ou o gráfico precisa ser
completado. Exibir 16 UFs sob um eixo que sugere o país inteiro é impreciso, e
é o tipo de detalhe que uma banca nota.

### `P3` — Figura da condição de aceitação

**Bloqueante para o slide 11.** A figura `F6` não existe. Especificação:

- eixos: custo latente $c_0(IVS_m)$ na horizontal, bolsa real $B_m/p_m$ na vertical;
- reta de indiferença $B/p = c_0 + \bar{v}$, separando aceitação (acima) de recusa (abaixo);
- dois pontos representando municípios contíguos na fronteira de faixa, deslocados verticalmente por $\Delta B = \text{R\$ }5.000$;
- rótulo do trecho em que o degrau é insuficiente, isto é, $\Delta B/p < \Delta c_0$.

É figura conceitual, sem dado observado. Deve ser rotulada como ilustração do
modelo, nunca como resultado, e gerada por script em `output/` como as demais.

---

## 4. Regra para o deck em LaTeX

1. Nenhuma figura entra no `.tex` sem código de proveniência (`F1`…`F6`) e sem
   linha correspondente neste documento.
2. Figura derivada de dado do repositório é gerada por script e lida de
   `output/`; não se cola imagem produzida fora do pipeline.
3. Figura conceitual recebe rótulo explícito de ilustração do modelo.
4. Número exibido em slide sem linha na tabela da seção 2 é erro de deck, não
   detalhe editorial.
