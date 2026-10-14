# IVS 2010 oficial do Ipea e o arquivo local `data/ivs_ipea_2010_municipios.csv`

> **Execução:** 2026-10-14.<br>
> **Decisão:** a *running variable* da RDD da bolsa é o **IVS 2010 oficial do
> Ipea**, que é o próprio escore administrativo do MS. R1 =
> `APROVADO_SHARP`.<br>
> **Achado colateral:** o arquivo local usado desde o início do projeto como
> "IVS 2010" é a base oficial do Ipea, mas **a linha errada**: em 5.554
> municípios ele traz o IVS 2010 de **mulheres negras em área urbana**, e não o
> IVS do município.<br>
> **Supera:** [`15`](15_portao_r1_escore_administrativo.md) na parte em que
> dizia que o escore estava incompleto, e o diagnóstico de
> [`07`](07_portao_rdd_bolsa.md) e de
> [`05_identificacao/16`](../05_identificacao/16_sintese_achados_e_novo_plano_causal.md),
> §3.5, de que a regra não se reproduzia com o IVS 2010.

## 1. Fonte

[Plataforma IVS do Ipea](https://ivs.ipea.gov.br/), "Base de Dados e
Shapefiles" → "Base Completa":
`https://ivs.ipea.gov.br/api/cockpit/storage/uploads/databases/basecompletamunicipal.zip`.
O zip tem 201 MB, SHA-256 `56f8a133…1ebbe`, e contém
`atlasivs_dadosbrutos_pt_v2.xlsx`, de 28/02/2024.

Recorte usado: `nivel = regiao,uf,rm,municipio`, `ano = 2010`, cor, sexo e
situação de domicílio "Total". Ficam 5.565 municípios (malha de 2010) com IVS,
subíndices, IDHM, população e renda per capita.

O zip fica fora do Git por causa do tamanho. É reprodutível pela URL e pelo
hash, que o script confere. Script:
`scripts/aquisicao/a08_adquirir_ivs_2010_oficial.py`. Saídas:
`output/aquisicao/a08_ivs_2010_oficial_municipio.csv` e
`output/aquisicao/a08_manifesto_ivs_2010_oficial.json`.

## 2. O escore administrativo é o IVS 2010 oficial

`scripts/rdd_bolsa/04b_validar_ivs_oficial_escore_administrativo.py` →
`output/rdd_bolsa/portao_r1_ivs_oficial.json`:

| Teste | Resultado |
|---|---:|
| escore `ivs` da relação nominal PMM-E igual ao IVS 2010 oficial, a 3 casas | **404 / 404** |
| `categoria_ivs` do consolidado PMMB igual à classe do IVS 2010 oficial | **5.565 / 5.565** |
| municípios de P1 (ciclo 1) com IVS oficial; regra reproduzida | 368 / 368; 368 |
| municípios de P2 (ciclo 2) com IVS oficial; regra reproduzida | 454 / 454; 454 |
| ciclo 3 (congelado) | 747 / 748; falta `422000`, criado depois de 2010 |

A regra aplicada desde o ciclo 1 é:

| IVS 2010 oficial | Bolsa |
|---|---:|
| até 0,300 | R$ 10 mil |
| de 0,301 a 0,400 | R$ 15 mil |
| acima de 0,400 | R$ 20 mil |

Isso está de acordo com a NT 122/2024 CGFAP/SAPS, que usa "a base do IVS do
IPEA de 2010" (conferido no PDF). Pela busca, a Portaria GM/MS 485/2023 adota o
IVS do Atlas do Ipea (2015); o texto dela não está arquivado no repositório.

O FAQ e a cláusula 11.1.4 do edital 3/2025 descrevem uma grade um degrau menos
generosa: muito alta → Faixa 1, alta → Faixa 2, o resto → Faixa 3. A grade
aplicada é a de cima. Aplicada ao IVS oficial, a grade do FAQ acerta 202 de 368
municípios, põe 166 "acima" e nenhum "abaixo": é daí que vinha a aparência de
"IVS como piso".

## 3. O arquivo local é o IVS de um subgrupo, não o do município

`data/ivs_ipea_2010_municipios.csv` (SHA-256 `84d23a…818c`) entrou no commit
inicial do repositório (`3027942`, 02/09/2026), sem script de aquisição nem
fonte registrada.

| Comparação com a base oficial | Arquivo local |
|---|---|
| IVS: valores iguais a 3 casas | 0,7% |
| IVS: correlação | 0,85 |
| IDHM: valores iguais | cerca de 0,9% (Recife 0,733 contra 0,772 oficial) |
| População 2010 | São Paulo 2,1 milhões contra 11,25 milhões; Recife 468 mil contra 1,54 milhão; Florianópolis 29 mil contra 421 mil |

**De onde ele vem.** A base completa do Ipea tem, para cada município e ano,
uma linha por combinação de cor (Total, Branco, Negro), sexo (Total, Homem,
Mulher) e situação de domicílio (Total, Urbano, Rural). O IVS do município é a
linha "Total/Total/Total". O script
`scripts/rdd_bolsa/04c_identificar_recorte_arquivo_local.py` compara o arquivo
local com todas essas linhas e grava o resultado em
`output/rdd_bolsa/identificacao_arquivo_local_ivs.json`.

| Arquivo local contra a linha… | IVS igual | IDHM igual | População igual |
|---|---:|---:|---:|
| **Negro / Mulher / Urbano** (5.554 municípios) | **100%** | **100%** | **98,8%** |
| Total / Total / Total (o IVS do município) | 0,7% | 0,9% | 0% |

Nos 11 municípios que não têm a linha "Negro / Mulher / Urbano", todos no RS e
em SC, o arquivo traz outra linha parcial, quase sempre "Total / Mulher /
Total". O arquivo não é inventado: é um **erro de extração**. Para cada
município, pegou-se uma linha de subgrupo em vez da linha total.

Isso também explica a população: os 41,9 milhões que a coluna soma, contra 190,8
milhões no Censo 2010, são a população desse subgrupo. Florianópolis tem 29 mil
mulheres negras em área urbana, num total de 421 mil habitantes. A hipótese
"alguma subpopulação do Atlas", registrada em
[`04_dados/02`](../04_dados/02_inventario_dados_por_outcome.md), §4.0, fica
confirmada.

Com a base oficial, as correlações do IVS 2010 nos 5.565 municípios são: 0,83
com o subíndice de infraestrutura urbana, 0,91 com capital humano, 0,89 com
renda e trabalho e −0,88 com o IDHM. Os números 0,48, 0,77, 0,80 e −0,74,
citados em 14/10/2026 antes deste achado, vinham do arquivo local.

Pela regra do projeto, o arquivo não é alterado. Ele é **rebaixado**: deixa de
ser *running variable* e covariável do município. Se alguma análise precisar
do IVS de mulheres negras urbanas, deve ler esse recorte direto da base
oficial, com o rótulo correto.

## 4. O que muda nas conclusões anteriores

| Conclusão anterior | Origem | Situação |
|---|---|---|
| "a regra não se reproduz pelo IVS"; 177 de 368 municípios "acima do piso" | IVS do arquivo local + grade do FAQ | **errada**: com o IVS oficial e a grade aplicada, a reprodução é de 100% |
| primeiro estágio instável em 0,400 e nulo em 0,500 | arquivo local | **artefato**: no IVS oficial o salto é 0% → 100% em 0,300 e 0,400, e 0,500 não é corte |
| teto de 78% de qualquer regra de dois cortes | arquivo local | **artefato** |
| RDD-IVS arquivada; pedido do escore ao MS | anterior | **superado**: o escore é público |
| gradiente de IVS no A4 e covariáveis de IVS, IDHM e população do arquivo local | arquivo local | **a rever**: os coeficientes de estrato do A4 não dependem do arquivo, mas os de IVS sim |

Scripts que leem o arquivo local, para revisão:
- `scripts/00_inventario_dados.py`;
- `scripts/02_auditar_fontes_pmme.py`;
- `scripts/aquisicao/04_harmonizar_territorio_ibge.py`;
- `scripts/aquisicao/06_adquirir_populacao_censo2022.py`;
- `scripts/aquisicao/a03_adquirir_ivs_regra.py`;
- `scripts/aquisicao/a06_integrar_portao.py`;
- `scripts/rdd_bolsa/00_*`, `01_*` e `01b_*`;
- `scripts/rdd_bolsa/04_portao_r1_escore_administrativo.py`;
- `scripts/rdd_bolsa/06_estimar_E2_limites.py` e `08_estimar_E4_proporcao.py`, no
  cenário "informado", que usou o arquivo local como banda;
- `scripts/tema_trabalho/07_red_team_sintese.py`.

Os slides da banca 1 que citam o IVS (slide 4: "177 dos 368 acima do piso")
herdam o erro. Ver a errata em
[`07_apresentacoes/banca1/04_versao_apresentada.md`](../07_apresentacoes/banca1/04_versao_apresentada.md)
quando ela for atualizada.
