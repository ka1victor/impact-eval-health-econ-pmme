# A06 — Portão integrado após a aquisição

> **Data de referência:** 29 de agosto de 2026
> **Escopo:** integração crítica de A01–A05, sem estimação de efeitos.
> **Decisão:** `aguardar dados administrativos`

## Decisão

A decisão é **aguardar dados administrativos**. As aquisições públicas melhoraram o versionamento das ofertas, a observação de resultados publicados, a documentação normativa e a viabilidade de esquema do CNES. Ainda assim, o outcome primário de cobertura sustentada não é mensurável e nenhum contraste causal foi identificado.

Resumo do portão: **1 passou**, **3 parciais**, **5 falharam** e **0 não aplicáveis**.

Essa decisão não autoriza o prompt 03. O próximo prompt é A07, exclusivamente para converter a lista fechada de lacunas em pedidos administrativos; não deve haver protocolo ou estimação antes da resposta e integração desses pedidos.

## Respostas obrigatórias

### 1. Existe universo versionado e denominador de vagas?

**Status: `passou`.** Existem quadros oficiais versionados e denominadores fechados por publicação. Uma linha é uma célula CNES–curso e seus campos de quantidade medem vagas na versão. Não existe denominador cumulativo deduplicado entre chamadas, pois ofertas podem ser reapresentadas.

Evidência: `output/aquisicao/a01_inventario_versoes.json` — 19 planilhas auditadas; denominador válido por versão, não pela soma de chamadas.; `output/aquisicao/a05_auditoria_universos_cnes.json` — Cinco quadros finais formam união cadastral de 1.930 CNES, sem somar suas vagas.

### 2. Existe id_vaga estável entre retificações e reapresentações?

**Status: `falhou`.** Não. CNES + curso + chamada identifica uma célula agregada, não uma vaga individual, e não demonstra identidade entre reapresentações.

Evidência: `output/aquisicao/a01_inventario_versoes.json` — id_vaga_existe=false e chave candidata explicitamente agregada.

### 3. Existem eventos suficientes para spells e cobertura_90/120/180?

**Status: `falhou`.** Não. Faltam aceite/recusa, entradas completas, afastamentos, retornos, saídas, reocupações e id_vaga. Os 1.671 registros publicados da primeira chamada são 993 chaves de candidato dentro da publicação, não o universo de inscrições. Nenhuma cobertura pode ser declarada.

Evidência: `output/aquisicao/a02_matriz_eventos_publicos.json` — Spells e coberturas de 90/120/180 dias classificados como incalculáveis.

### 4. Existe chave pseudonimizada PMM-E–CNES?

**Status: `falhou`.** Não. PMM-E publica combinações incompletas de nome, CRM ou CPF mascarado; o CNES usa CNS/identificador próprio. Pareamento nominal não é ponte determinística.

Evidência: `output/aquisicao/a05_auditoria_universos_cnes.json` — Ausência de chave primária compartilhada entre participante PMM-E e vínculo CNES.

### 5. O IVS, sua vintagem, precisão e cutoff aplicados estão observados por vaga?

**Status: `falhou`.** Não. O IVS 2010 do IPEA permanece a running variable canônica, mas não há escore administrativo contínuo por vaga, vintagem, precisão, regra de arredondamento ou cutoff do PMM-E. A divergência de 42,56% não identifica sua causa.

Evidência: `output/aquisicao/a03_matriz_regra_tratamento.json` — Cutoff não confirmado; escore por vaga ausente; 226/531 municípios divergem do recálculo local.

### 6. A dose é faixa anunciada, valor devido ou valor pago?

**Status: `parcial`.** Somente a faixa e a grade anunciada de 2025 são parcialmente observadas. Valor devido, empenhado, liquidado e pago não foram adquiridos em nível e proveniência adequados; não há dose recebida nem primeiro estágio financeiro.

Evidência: `output/aquisicao/a04_matriz_dose_financeira.json` — Grade normativa 2025 preservada; demais estágios financeiros não observados.

### 7. O CNES permite baseline, vínculos simultâneos, FTE cadastral e infraestrutura?

**Status: `parcial`.** O esquema público contém os campos necessários para essas mensurações cadastrais, mas só três de 26 competências foram inspecionadas. Presença cadastral não prova participação no PMM-E, horas realizadas ou capacidade líquida atribuível ao programa.

Evidência: `output/aquisicao/a05_dicionario_tabelas_cnes.json` — Esquemas de estabelecimento, carga horária, profissional, leitos, equipamentos e serviços nas três competências piloto.; `output/aquisicao/a05_manifesto_cnes.json` — 3 competências preservadas de 26 planejadas; 23 não baixadas.

### 8. Qual é a maior janela comum madura antes de olhar efeitos?

**Status: `parcial`.** A maturidade é apenas calendárica: 180 dias para as duas chamadas de 2025; 90 dias ao incluir chamadas até abril de 2026; 19 dias ao incluir também a oferta do ciclo 3 no corte de 12/08/2026. Sem população congelada e log de eventos, nenhuma dessas janelas é uma janela mensurável de cobertura.

Evidência: `output/aquisicao/a02_matriz_eventos_publicos.json` — Dias potenciais por coorte e bloqueio explícito da mensuração de cobertura.

### 9. Qual contraste é identificável: participação, pacote ou incentivo marginal?

**Status: `falhou`.** Nenhum contraste causal está identificado. Institucionalmente, o candidato mais estreito é o incentivo marginal anunciado, condicional à vaga; porém regra, escore e primeiro estágio recebido não foram reconstruídos. Participação não é determinada pelo IVS, e não se exclui pacote de componentes simultâneos.

Evidência: `output/aquisicao/a03_matriz_regra_tratamento.json` — RDD inviável com dados públicos atuais; contraste candidato não estimável.

## Janela e contraste antes de efeitos

A única afirmação possível é sobre maturidade de calendário, não cobertura observada. Restringir às duas chamadas de 2025 produz 180 dias potenciais; incluir chamadas até abril de 2026 reduz a janela comum a 90 dias; incluir o ciclo 3 reduz a 19 dias no corte nominal. Nenhuma escolha é congelada porque faltam população comparável, eventos e chave da vaga.

O IVS não determina participação. O contraste institucional candidato é o incentivo marginal **anunciado** condicional à oferta, mas ele não é causalmente identificável: o escore administrativo, a regra histórica e o primeiro estágio recebido não estão observados, e outros componentes simultâneos não foram excluídos. RDD, DiD e estudo de evento permanecem bloqueados.

## Distinções preservadas

- célula CNES–curso, quantidade publicada e vaga individual são unidades diferentes;
- registro publicado, candidato distinto dentro da publicação e universo de inscrições são universos diferentes;
- o snapshot nominal de 518 CNES e a união cadastral de 1.930 CNES dos quadros não são intercambiáveis;
- faixa anunciada, valor devido, empenhado, liquidado e pago são estágios financeiros diferentes;
- presença cadastral no CNES não demonstra participação no PMM-E nem capacidade líquida;
- 202406, 202506 e 202607 são três competências piloto, não um painel mensal completo.

## Lista fechada para A07

### A07-01 — Cadastro mestre e versionamento de vagas

Campos mínimos: `id_vaga_pseudo`, `ciclo`, `chamada`, `versao_vigencia`, `CNES`, `curso`, `quantidade`, `modalidade`, `reapresentacao_origem`, `motivo_alteracao`.

### A07-02 — Universo de inscrições e log longitudinal de eventos

Campos mínimos: `id_inscricao_pseudo`, `id_vaga_pseudo`, `id_profissional_pseudo`, `id_evento`, `timestamp`, `estado_anterior`, `estado_novo`, `motivo`.

Eventos mínimos: `inscrição`, `classificação`, `convocação`, `aceite/recusa`, `homologação`, `entrada`, `afastamento`, `retorno`, `transferência`, `saída`, `reocupação`.

### A07-03 — Ponte pseudonimizada PMM-E–CNES

Campos mínimos: `id_profissional_pseudo`, `identificador_CNES_pseudo`, `inicio_validade`, `fim_validade`, `regra_crosswalk`.

### A07-04 — Regra administrativa histórica do IVS por vaga

Campos mínimos: `id_vaga_pseudo`, `escore_IVS_aplicado`, `vintagem`, `precisao`, `regra_arredondamento`, `cutoff`, `categoria`, `faixa`, `vigencia`, `excecao_motivo`.

### A07-05 — Folha mensal individualizada e execução financeira vinculável

Campos mínimos: `competencia`, `id_vaga_pseudo`, `id_profissional_pseudo`, `valor_anunciado`, `valor_devido`, `valor_pago`, `data_pagamento`, `glosa`, `suspensao`, `estorno`, `retroativo`, `componente`.

### A07-06 — Documentação e historicização dos painéis administrativos

Campos mínimos: `definicao_ativo`, `data_corte`, `regra_atualizacao`, `tratamento_afastamento_transferencia`, `politica_revisao`, `historicizacao_faixa`, `dicionario`.

A07 deve preparar esses seis pedidos, com pseudonimização, dicionário, vigência, regras de atualização, política de revisão e indicação explícita de quando ausência significa zero, não aplicável ou não registrado. A07 não deve enviar pedidos nem estimar efeitos sem autorização posterior.

## Reprodutibilidade

Execute:

```powershell
python scripts/aquisicao/a06_integrar_portao.py
python run_all.py
```

Os caminhos e SHA-256 das 13 entradas integradas estão em `output/aquisicao/portao_integrado.json`. A matriz final de observabilidade está em `output/aquisicao/matriz_variavel_fonte_final.json`.
