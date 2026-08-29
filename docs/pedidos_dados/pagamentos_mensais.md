# Pedido 3 — folha mensal individualizada e execução financeira vinculável

> Status: **`não enviado`**. Faixa anunciada, valor devido, empenhado, liquidado e pago permanecem objetos distintos.

## Destinatário provável, período e finalidade

**Órgão:** Ministério da Saúde. **Unidades prováveis:** unidade gestora da bolsa-formação do PMM-E e unidade de execução financeira correspondente, a confirmar pelo SIC. Não se presume sistema, base ou fluxo interno; solicita-se encaminhamento ao custodiante.

**Período exato:** competências **202509 a 202608**, com registros de pagamento, ajuste, glosa, suspensão, estorno ou retroativo registrados até **29/08/2026** e referentes a essas competências. Se houver competência anterior ligada ao PMM-E, incluí-la e documentar o motivo.

**Finalidade:** medir a dose financeira efetivamente devida e paga, auditar diferenças entre regra e execução e permitir futuro teste de primeiro estágio. Não se solicita saldo bancário, conta, agência, CPF, nome ou outro dado civil.

## Tabelas solicitadas

### `folha_componentes.csv` — uma linha por competência, vaga, profissional e componente

| Campo | Tipo | Definição |
|---|---|---|
| `competencia` | texto(6) | Mês de referência `AAAAMM`, não data do desembolso. |
| `id_vaga_pseudo` | texto | Chave estável comum ao cadastro de vagas. |
| `id_profissional_pseudo` | texto | Chave estável comum aos eventos e à ponte. |
| `componente` | categoria | Componente financeiro conforme domínio documentado. |
| `valor_anunciado` | decimal/NULL | Valor normativo anunciado para a situação, se aplicável. |
| `valor_devido` | decimal | Obrigação apurada na competência; zero somente se apurado em zero. |
| `valor_pago` | decimal | Total desembolsado atribuído ao componente/competência até o corte. |
| `data_pagamento` | data/NULL | Data do desembolso; vazio se não pago até o corte. |
| `glosa` | decimal | Redução apurada por glosa, com sinal/convenção documentados. |
| `suspensao` | decimal/booleano | Valor ou indicador, conforme dicionário; não misturar tipos. |
| `estorno` | decimal | Valor estornado, com convenção de sinal. |
| `retroativo` | decimal | Parcela paga ou devida retroativamente. |
| `faixa_aplicada` | texto/NA | Faixa usada na apuração da competência. |
| `regra_vigencia` | texto | Referência à regra financeira aplicada. |
| `status_folha` | categoria | Estado do processamento no corte. |
| `versao_registro` | texto | Versão/revisão da linha. |

**Chave:** `competencia + id_vaga_pseudo + id_profissional_pseudo + componente + versao_registro`. Entregas com uma linha vigente devem indicar qual versão é corrente sem apagar revisões.

### `execucao_financeira.csv` — uma linha por documento/estágio vinculável

| Campo | Tipo | Definição |
|---|---|---|
| `id_documento_financeiro_pseudo` | texto | Chave pseudonimizada do documento financeiro. |
| `estagio` | categoria | `empenhado`, `liquidado` ou `pago`, sem combinar estágios. |
| `data_estagio` | data | Data do estágio. |
| `exercicio` | inteiro | Exercício orçamentário. |
| `competencia` | texto(6)/NA | Competência atribuível; `NA` se o estágio não usar competência. |
| `id_vaga_pseudo` | texto/NA | Vaga atribuível, quando houver vínculo administrativo. |
| `id_profissional_pseudo` | texto/NA | Profissional atribuível, quando houver vínculo administrativo. |
| `componente` | categoria/NA | Componente vinculado. |
| `valor` | decimal | Valor do estágio, em BRL, com sinal documentado. |
| `classificacao_orcamentaria` | texto | Classificação necessária para provar o escopo PMM-E, minimizada ao necessário. |
| `id_documento_origem_pseudo` | texto/NA | Documento anterior na cadeia, quando existente. |
| `status_documento` | categoria | Vigente, cancelado, estornado ou domínio real documentado. |

Não se presume que todo documento financeiro possa ser atribuído a vaga ou profissional. Nulos devem refletir essa limitação e não ser artificialmente preenchidos.

## Metadados, formato e LGPD

Solicitam-se data de corte, calendário de fechamento/reabertura, política de revisão, dicionário de componentes e status, regra de sinais e reconciliação contábil. Formato: CSV UTF-8 em ZIP, códigos como texto, valores decimais com ponto ou centavos inteiros declarados, manifesto e SHA-256.

As chaves pseudonimizadas devem ser consistentes com os demais pacotes. Não solicitar identificadores civis nem dados bancários. O risco residual deve ser tratado por minimização, controle de acesso e eventual ambiente seguro; pseudonimização não equivale a anonimato absoluto.

## Ausência, zero e não aplicável

- `valor_devido = 0` ou `valor_pago = 0` somente quando a apuração confirmou zero;
- vazio/`NULL` quando ainda não apurado, desconhecido ou não registrado, distinguido pelo `status_folha`;
- `NA` quando componente/estágio não se aplica;
- ausência de linha não significa não pagamento, glosa ou suspensão;
- pagamento posterior deve manter a competência original e registrar separadamente a data de pagamento.

## Alternativas hierarquizadas

1. Microdados pseudonimizados completos das duas tabelas.
2. Se documento financeiro individual não puder ser entregue: folha por profissional–vaga–competência–componente e execução agregada por competência–componente–estágio, com reconciliação entre totais.
3. Se o nível profissional for restrito: dados por vaga–competência–componente, preservando devido, pago, ajustes e número de profissionais, sem usar médias que ocultem zeros.
4. Último recurso: totais mensais por componente e estágio com documentação de filtros e consulta reproduzível. Não fecha a dose individual nem o primeiro estágio financeiro.

## Teste objetivo de completude

A resposta é completa quando: (a) toda combinação profissional–vaga com evento de entrada possui uma linha para cada competência elegível ou motivo/status explícito; (b) `valor_devido`, `valor_pago`, glosas, estornos e retroativos reconciliam segundo fórmula documentada; (c) pagamentos fora da competência preservam competência e data distintas; (d) totais pagos da folha reconciliam com a execução no nível possível, e diferenças são quantificadas; (e) nenhuma faixa anunciada é apresentada como valor devido/pago; e (f) chaves, dicionário, revisões, corte, manifesto e hashes estão completos.
