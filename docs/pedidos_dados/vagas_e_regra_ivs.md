# Pedido 1 — cadastro mestre, versionamento de vagas e regra histórica do IVS

> Status: **`não enviado`**. Minuta técnica; não constitui protocolo, contato ou aceite de condições.

## Destinatário provável e finalidade

**Órgão:** Ministério da Saúde. **Unidade provável:** unidade da Secretaria de Gestão do Trabalho e da Educação na Saúde (SGTES) responsável pela gestão do PMM-E, a confirmar pelo Serviço de Informação ao Cidadão. Se não for a custodiante, solicita-se encaminhamento interno.

**Período exato:** de **24/07/2025 a 29/08/2026**, incluindo todas as versões vigentes e substituídas das vagas dos ciclos 1, 2 e 3 publicadas ou mantidas administrativamente até a data final. Incluir registros criados antes de 24/07/2025 apenas quando forem origem administrativa de vaga publicada no período.

**Finalidade pública e de pesquisa:** documentar a implementação, a transparência do denominador de vagas e a regra administrativa do incentivo, permitindo distinguir criação, retificação, reapresentação e retirada. A finalidade é avaliação independente de política pública; não se solicita resultado causal nem decisão sobre elegibilidade individual.

## Tabelas e grãos

Solicitam-se três CSVs. Os nomes abaixo são nomes sugeridos para a entrega, não alegações sobre campos internos existentes.

### `vagas_mestre.csv` — uma linha por vaga individual

| Campo | Tipo | Definição |
|---|---|---|
| `id_vaga_pseudo` | texto | Chave pseudonimizada estável da vaga individual, invariável entre versões, chamadas e reapresentações. |
| `ciclo` | texto | Ciclo do PMM-E ao qual a vaga foi inicialmente associada. |
| `chamada_origem` | texto | Chamada em que a vaga individual foi criada ou registrada pela primeira vez. |
| `cnes` | texto(7) | CNES do estabelecimento na vigência inicial, com zeros à esquerda. |
| `ibge_municipio` | texto | Código municipal usado administrativamente, com padrão declarado. |
| `curso` | texto | Curso/aprimoramento na grafia administrativa da vigência inicial. |
| `modalidade_inicial` | categoria | Imediata, cadastro de reserva ou outra categoria documentada. |
| `cota_inicial` | categoria/NA | Modalidade de concorrência da vaga, se aplicável. |
| `data_criacao` | data | Data administrativa de criação; não confundir com publicação. |
| `id_vaga_origem_pseudo` | texto/NA | Vaga da qual esta derivou, somente se houver relação administrativa. |

**Chave:** `id_vaga_pseudo`, única e não nula. Uma célula CNES–curso pode conter várias vagas e, portanto, várias linhas. `quantidade` não pertence a esta tabela.

### `vagas_versoes.csv` — uma linha por vaga individual e versão/vigência

| Campo | Tipo | Definição |
|---|---|---|
| `id_vaga_pseudo` | texto | Chave estável que liga ao cadastro mestre. |
| `id_versao` | texto | Identificador da versão ou ato de atualização. |
| `versao_vigencia_inicio` | timestamp | Início da validade do estado. |
| `versao_vigencia_fim` | timestamp/NULL | Fim da validade; vazio apenas quando vigente no corte. |
| `data_publicacao` | timestamp/NULL | Publicação externa, se ocorreu. |
| `ciclo` | texto | Ciclo nessa versão. |
| `chamada` | texto | Chamada nessa versão. |
| `cnes` | texto(7) | Estabelecimento nessa versão. |
| `ibge_municipio` | texto | Município nessa versão. |
| `curso` | texto | Curso nessa versão. |
| `modalidade` | categoria | Imediata, reserva ou categoria documentada. |
| `cota` | categoria/NA | Modalidade de concorrência; `NA` se não aplicável. |
| `status_vaga` | categoria | Estado administrativo documentado da vaga. |
| `reapresentacao_origem` | texto/NA | Ciclo/chamada ou `id_versao` de origem quando a vaga foi reapresentada. |
| `motivo_alteracao` | texto/NA | Motivo documentado de retificação, conversão, retirada, transferência ou cancelamento. |
| `fonte_ato` | texto | Referência do ato, processo ou publicação que sustenta a versão. |

**Chave:** `id_vaga_pseudo + id_versao`. Intervalos da mesma vaga não devem se sobrepor sem explicação no dicionário.

### `regra_ivs_vaga.csv` — uma linha por vaga e vigência da regra aplicada

| Campo | Tipo | Definição |
|---|---|---|
| `id_vaga_pseudo` | texto | Liga à vaga individual. |
| `vigencia_inicio` | data | Início da regra aplicada à vaga. |
| `vigencia_fim` | data/NULL | Fim da regra; vazio se vigente no corte. |
| `escore_ivs_aplicado` | decimal/texto | Escore efetivamente usado, preservando a precisão original. |
| `vintagem` | texto | Ano/edição/arquivo do IVS efetivamente aplicado. |
| `precisao` | inteiro/texto | Casas decimais ou precisão operacional. |
| `regra_arredondamento` | texto | Regra usada antes da categorização; informar “não houve” quando for o caso. |
| `cutoff` | decimal/texto | Limite efetivamente aplicado àquela decisão, com inclusão/exclusão da fronteira. |
| `categoria` | texto | Categoria administrativa do IVS nessa vigência. |
| `faixa` | texto | Faixa de atração nessa vigência. |
| `valor_anunciado` | decimal/NULL | Valor anunciado associado à vaga e vigência, não valor devido ou pago. |
| `unidade_monetaria` | texto/NA | BRL ou unidade documentada; `NA` quando não houver valor. |
| `excecao_motivo` | texto/NA | Exceção documentada à regra geral; `NA` se a regra não admitir o campo. |
| `fonte_regra` | texto | Ato, memória ou arquivo administrativo que prova a aplicação. |

**Chave:** `id_vaga_pseudo + vigencia_inicio`. A resposta deve preservar o valor antes de eventual recodificação posterior. O IVS 2010 do IPEA é a referência canônica do projeto, mas o pedido não presume que tenha sido a vintagem administrativa efetivamente usada.

## Metadados, segurança e formato

Aplicam-se o padrão técnico do [README](README.md) e o desenho consolidado em [layouts_requisitados.md](layouts_requisitados.md). Solicita-se dicionário com domínios, nulabilidade, origem, regra de derivação, timezone, data de corte, política de revisão e histórico de alterações. Códigos devem ser texto; CSV UTF-8 em ZIP; manifesto com SHA-256.

Não se solicitam nomes, CPF, CNS, CRM ou outros identificadores civis. A chave da vaga deve ser pseudonimizada e estável. Não se promete anonimato absoluto; solicita-se minimização, controle de acesso proporcional e supressão apenas do que for estritamente necessário.

## Ausência, zero e não aplicável

- vazio/`NULL`: informação desconhecida ou não registrada, conforme código do dicionário;
- `0`: quantidade ou valor observado igual a zero, nunca “sem informação”;
- `NA`: campo não aplicável por regra;
- inexistência de linha em `vagas_versoes.csv` não pode ser interpretada como retirada, cancelamento ou ausência de vaga sem regra expressa.

## Alternativas hierarquizadas

1. Entrega preferida: três tabelas no nível de vaga individual, com chaves estáveis.
2. Se o nível individual não puder ser fornecido: tabela por célula CNES–curso–versão com `quantidade`, decomposição por modalidade/cota e identificador estável da célula, mais matriz explícita de reapresentações; declarar que não identifica vaga individual.
3. Se a regra por vaga for restrita: memória de cálculo por município–vigência e tabela de ligação `id_vaga_pseudo`–município–vigência, preservando escore, vintagem, precisão, arredondamento e exceções.
4. Último recurso: documentação normativa e contagens agregadas por versão, com justificativa legal e quantificação do que foi suprimido. Esta alternativa não fecha A07-01/A07-04 por si só.

## Teste objetivo de completude

A resposta é completa quando: (a) `id_vaga_pseudo` é único no mestre e reaparece em todas as versões/regras; (b) toda vaga vigente em cada publicação oficial auditada pode ser reconciliada, com quantidades por CNES–curso–modalidade iguais ao quadro correspondente ou diferença explicada; (c) nenhuma vigência se sobrepõe sem justificativa; (d) toda reapresentação aponta para origem ou é marcada explicitamente como criação nova; (e) 100% das vagas têm regra IVS ou motivo codificado de não aplicação; e (f) dicionário, revisões, corte, manifesto e hashes estão presentes.
