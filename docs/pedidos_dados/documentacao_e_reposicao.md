# Pedido 4 — documentação, historicização dos painéis e reposição de arquivos

> Status: **`não enviado`**. Este pacote solicita documentação e preservação, não novos outcomes nem bases de WP3–WP5.

## Destinatário provável, período e finalidade

**Órgão:** Ministério da Saúde. **Unidades prováveis:** unidade da SGTES produtora ou gestora dos painéis PMM-E e unidade responsável pelas páginas e arquivos dos chamamentos, a confirmar pelo SIC. Solicita-se encaminhamento interno ao custodiante quando necessário.

**Período exato:** documentação e versões dos painéis/cadastros entre **01/12/2025 e 29/08/2026**; arquivos públicos e histórico de páginas dos ciclos 1–3 entre **24/07/2025 e 29/08/2026**. Para cada item, informar a versão válida no corte e todas as revisões retroativas conhecidas no período.

**Finalidade:** interpretar corretamente o snapshot nominal e a série histórica, auditar revisões e garantir preservação de evidência pública. O snapshot de 518 CNES não deve ser confundido com a união de 1.930 CNES dos quadros.

## Itens solicitados

### `painel_metadados.csv` — uma linha por produto, versão e vigência

| Campo | Tipo | Definição |
|---|---|---|
| `id_produto` | texto | Identificador do painel, cadastro, série ou arquivo. |
| `versao` | texto | Versão documentada. |
| `vigencia_inicio` | timestamp | Início da validade. |
| `vigencia_fim` | timestamp/NULL | Fim; vazio quando vigente. |
| `data_corte` | timestamp | Data/hora a que os dados se referem. |
| `definicao_ativo` | texto | Critério completo de inclusão como ativo. |
| `regra_atualizacao` | texto | Periodicidade, defasagem e processo de atualização. |
| `tratamento_afastamento_transferencia` | texto | Como afastamentos e transferências entram/saem do estoque. |
| `politica_revisao` | texto | Reabertura e revisão retroativa de competências. |
| `historicizacao_faixa` | texto | Se a faixa é preservada historicamente ou recodificada pela regra corrente. |
| `dicionario` | texto | Nome/versão do dicionário anexo. |
| `observacao_cnes_vazio` | texto/NA | Regra que explica CNES/estabelecimento vazios na série, se aplicável. |

### `revisoes_painel.csv` — uma linha por revisão

| Campo | Tipo | Definição |
|---|---|---|
| `id_produto` | texto | Produto revisado. |
| `id_revisao` | texto | Chave única da revisão. |
| `registrada_em` | timestamp | Momento da revisão. |
| `competencia_afetada` | texto(6)/NA | Competência revista. |
| `tipo_revisao` | categoria | Tipo real documentado. |
| `linhas_incluidas` | inteiro/NA | Número incluído, se mensurado. |
| `linhas_excluidas` | inteiro/NA | Número excluído, se mensurado. |
| `linhas_alteradas` | inteiro/NA | Número alterado, se mensurado. |
| `motivo` | texto | Justificativa documentada. |

### `arquivos_publicos.csv` — uma linha por arquivo e versão

| Campo | Tipo | Definição |
|---|---|---|
| `id_arquivo` | texto | Identificador do documento. |
| `ciclo` | texto | Ciclo relacionado. |
| `chamada` | texto | Chamada relacionada. |
| `titulo` | texto | Título oficial. |
| `versao` | texto | Original, retificação ou outra versão documentada. |
| `data_publicacao` | timestamp | Publicação. |
| `url_canonica` | texto | URL oficial vigente ou histórica. |
| `nome_arquivo` | texto | Nome original. |
| `tamanho_bytes` | inteiro | Tamanho do arquivo. |
| `sha256` | texto(64) | Hash do conteúdo. |
| `substitui_id_arquivo` | texto/NA | Versão substituída, sem apagá-la. |
| `status_acesso` | categoria | Disponível, reposto, descontinuado ou domínio documentado. |

Solicita-se também a reposição ou URL canônica de qualquer arquivo oficial referenciado nas páginas dos chamamentos que esteja indisponível, preservando originais e retificações. A01 recuperou os itens antes quebrados por slugs oficiais ativos; este pedido busca política de preservação e eventuais versões faltantes, não presume que os mesmos links continuem quebrados.

## Documentos anexos solicitados

- dicionário completo de cada painel/série, com nomes, tipos, domínios, unidade e fonte;
- metodologia de construção, regras de corte, deduplicação e tratamento de atraso;
- histórico de layouts e mudanças de definição;
- explicação documentada sobre historicização/recodificação de categoria e faixa;
- catálogo de arquivos públicos com relação de substituição entre versões.

## Formato, semântica e LGPD

CSV UTF-8/ZIP, datas ISO 8601, manifesto e hashes, conforme [README](README.md). Documentos metodológicos podem ser PDF/A ou ODT/DOCX acompanhados, se possível, de versão textual acessível. Este pacote não necessita de identificadores pessoais. Caso exemplos reais sejam usados no dicionário, devem ser sintéticos ou minimizados. Ausência é `NULL`; zero é contagem confirmada igual a zero; `NA` é não aplicável. Ausência de linha não prova ausência de revisão.

## Alternativas hierarquizadas

1. Tabelas e documentação completas, com todas as versões e arquivos repostos.
2. Se não houver histórico estruturado: cópias datadas de cada snapshot e notas de versão suficientes para produzir o histórico.
3. Se não houver hashes históricos: arquivos originais com datas, tamanhos e cadeia de substituição, permitindo calcular hashes após recebimento.
4. Se um arquivo não puder ser reposto: declaração formal de indisponibilidade, motivo, período afetado e indicação de eventual repositório arquivístico. Isso documenta a lacuna, mas não substitui os dados.

## Teste objetivo de completude

A resposta é completa quando: (a) cada produto tem definição de ativo, corte, atualização, afastamento/transferência, revisão e historicização de faixa; (b) as nove competências públicas de dez/2025 a ago/2026 podem ser associadas a uma versão e data de corte; (c) toda revisão conhecida tem linha ou declaração explícita de inexistência; (d) cada arquivo listado tem bytes/hash ou justificativa de indisponibilidade; (e) originais e retificações permanecem distinguíveis; e (f) dicionários e mudanças de layout explicam campos vazios e recodificações sem inferência do pesquisador.
