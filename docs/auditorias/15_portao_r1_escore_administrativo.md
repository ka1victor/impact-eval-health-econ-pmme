# Portão R1 refeito — escore administrativo de IVS nos dados abertos

> [!WARNING]
> **Corrigido no mesmo dia por [`16`](16_ivs_2010_oficial_e_arquivo_local.md).**
> O escore administrativo **é** o IVS 2010 oficial do Ipea: 404/404 valores e
> 5.565/5.565 categorias iguais. A base oficial é pública para todos os
> municípios. Ficam erradas:
> - a §2.2, que dizia "outra safra ou outro cálculo". Quem diverge da base
>   oficial é o arquivo local `data/ivs_ipea_2010_municipios.csv`;
> - a §2.3 e a §4, sobre o bloqueio por cobertura: o escore está completo para
>   os ciclos 1 e 2.
>
> A reconstrução da regra (§2.1) continua válida.

> **Execução:** 2026-10-14.<br>
> **Decisão:** `REGRA_RECONSTRUIDA_ESCORE_INCOMPLETO`.<br>
> **Outcomes abertos:** nenhum. O módulo lê faixa anunciada, escore, categoria e
> IVS 2010; não calcula preenchimento, homologação, presença nem CNES pós.<br>
> **Substitui:** o diagnóstico `ARQUIVADO_ESCORE_NAO_OBSERVADO` de
> [`07`](07_portao_rdd_bolsa.md) e de
> [`05_identificacao/16`](../05_identificacao/16_sintese_achados_e_novo_plano_causal.md), §3.5.1,
> na parte em que dizia que o escore não era observado.

## 1. O que mudou

O dicionário de dados abertos do Ministério da Saúde, versão de 13/07/2026,
passou a documentar na **Relação Nominal Ativos – PMM-E** a coluna `ivs`,
"valor do Índice de Vulnerabilidade Social (IVS) calculado pelo IPEA", ao lado
de `categoria_ivs` e `faixa_atracao`. A versão de 09/10/2026 do arquivo traz o
escore para 404 municípios, com três casas decimais (o campo vem multiplicado
por 10.000). O **consolidado do Programa Mais Médicos** traz `categoria_ivs`
para 5.570 municípios.

Os brutos estão em `data/raw/aquisicao/ivs_administrativo/`, com URL, data de
captura e SHA-256 em `output/aquisicao/a07_manifesto_ivs_administrativo.json`.
Só as colunas da regra são extraídas; nome, CRM e contagens não são lidos.

## 2. Resultado

### 2.1 A regra está reconstruída

| Quadro de vagas | Municípios | Faixa pela categoria administrativa | Faixa pelo escore, onde há escore |
|---|---:|---:|---:|
| Ciclo 1, chamada 1 (24/07/2025) | 368 | **368 / 368** | **209 / 209** |
| Ciclo 2, chamada 1 (retificado) | 454 | **454 / 454** | **275 / 275** |
| Ciclo 2, chamada 2 | 369 | **369 / 369** | **203 / 203** |
| Ciclo 3, chamada 1 (retificado) | 748 | **748 / 748** | **285 / 285** |

A regra aplicada é de **dois cortes no escore administrativo**:

| Escore | Categoria | Faixa | Bolsa |
|---|---|---|---:|
| até 0,300 | muito baixa ou baixa | Faixa 3 | R$ 10 mil |
| de 0,301 a 0,400 | média | Faixa 2 | R$ 15 mil |
| acima de 0,400 | alta ou muito alta | Faixa 1 | R$ 20 mil |

O lado de **0,400** é observado: 0,400 está na Faixa 2 e 0,401 na Faixa 1. O
valor **0,300** exato não aparece; pela classe do Atlas ele é "baixa" e cai na
Faixa 3. Máximo observado da Faixa 3: 0,299; mínimo da Faixa 2: 0,302.

Dois contrastes de **+R$ 5 mil** cada: 0,300 (Faixa 3 → 2) e 0,400
(Faixa 2 → 1). O corte de 0,500, que a RDD pública testava, **não tem ação**
na regra efetiva. A regra é a mesma nos três ciclos, inclusive no de 2025,
apesar de o FAQ do edital 3/2025 descrever outra grade.

### 2.2 Por que o IVS 2010 não reproduzia

O escore administrativo **não é** o IVS 2010 público: correlação de 0,892,
diferença média de +0,005 e desvio-padrão de 0,052, de −0,114 a +0,189.
Apenas 0,5% dos municípios têm valores idênticos. É outra safra ou outro
cálculo. Isso explica o teto de 78% das regras de corte sobre o IVS 2010 e o
primeiro estágio instável em 0,400. Era erro de medida na *running variable*,
e não ausência de regra.

### 2.3 O que impede a estimação

O escore contínuo só existe para municípios com **especialista ativo** na data
de referência:

| Quadro | Cobertura do escore | Faixa 1 | Faixa 2 | Faixa 3 |
|---|---:|---:|---:|---:|
| Ciclo 1, chamada 1 | 56,8% | 60,8% | 72,0% | 44,0% |
| Ciclo 2, chamada 1 | 60,6% | 69,0% | 73,9% | 48,1% |
| Ciclo 2, chamada 2 | 55,0% | 54,9% | 70,0% | 48,2% |
| Ciclo 3, chamada 1 | 38,1% | 32,3% | 53,3% | 34,3% |

A ausência do escore é, por construção, função do desfecho. Uma RDD estimada
só nos municípios cobertos condiciona na própria variável dependente e **não
é autorizada**. A falta de escore também não é tratada como zero nem imputada
a partir do IVS 2010: imputar recriaria o erro de medida que bloqueou a RDD
pública.

## 3. Requisitos de R1

| Requisito de [`14`](../05_identificacao/14_plano_implementacao_rdd_bolsa.md), §3 | Estado |
|---|---|
| município, escore, faixa, valor e vigência completos | **não**: escore ausente em 43% do ciclo 1 |
| escore único por município | sim |
| regra reproduz 100% | **sim**, nos quatro quadros |
| lado do cutoff localizável | sim em 0,400; 0,300 exato não observado |
| fontes e hashes preservados | sim |

R2 a R5 continuam bloqueados.

## 4. O que destrava

Um único campo: **`ivs` para todos os municípios**, ou ao menos para os que
tiveram vaga ofertada. É o mesmo campo que o Ministério já publica na relação
nominal e que alimenta a `categoria_ivs` do consolidado, que hoje cobre 5.570
municípios. O pedido ficou menor que o redigido em
[`pedidos_dados/solicitacao_focal_rdd_bolsa.md`](../pedidos_dados/solicitacao_focal_rdd_bolsa.md).

Com o escore completo, o primeiro estágio é *sharp* por construção. No ciclo
1, entre os municípios hoje cobertos, a janela de ±0,050 tem 71 municípios
em torno de 0,300 e 72 em torno de 0,400. Com cobertura completa e os ciclos
2 e 3 empilhados, o suporte cresce. O tamanho final e o MDE são tarefa de R2,
que não abre outcome.

## 5. Running variable

O `CLAUDE.md` fixa o IVS 2010 do Ipea como *running variable* canônica e exige
justificativa econométrica e autorização do autor para trocá-la. A
justificativa está acima: a atribuição efetiva da bolsa é função
determinística do escore administrativo, e não do IVS 2010. **A troca depende
de autorização expressa do autor**, registrada antes de R2.

**Autorizada em 14/10/2026.** O `CLAUDE.md` e o `AGENTS.md` foram atualizados.
O protocolo de estimação foi congelado em commit próprio, antes de qualquer
contagem por ciclo de ingresso:
`output/rdd_bolsa/protocolo_escore_administrativo.json`. Ele define três
estimandos:
- **E1:** razão de densidades sob continuidade da densidade do escore;
- **E2:** limites parciais com o escore ausente;
- **E3:** RDD sharp, quando o escore estiver completo.

## 6. Artefatos

- `scripts/aquisicao/a07_adquirir_ivs_administrativo.py`;
- `scripts/rdd_bolsa/04_portao_r1_escore_administrativo.py`;
- `output/aquisicao/a07_manifesto_ivs_administrativo.json`;
- `output/aquisicao/a07_ivs_administrativo_municipio.csv`;
- `output/aquisicao/a07_categoria_ivs_pmmb_municipio.csv`;
- `output/rdd_bolsa/portao_r1_escore_administrativo.json`;
- `output/rdd_bolsa/matriz_municipio_escore_administrativo.csv`.
