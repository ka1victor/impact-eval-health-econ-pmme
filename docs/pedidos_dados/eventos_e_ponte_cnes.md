# Pedido 2 — universo de inscrições, log de eventos e ponte pseudonimizada com o CNES

> Status: **`não enviado`**. O pedido não solicita identificadores civis ao pesquisador e não promete anonimato absoluto.

## Destinatário provável, período e finalidade

**Órgão:** Ministério da Saúde. **Unidades prováveis:** unidade da SGTES responsável pelos registros administrativos do PMM-E e, para a vinculação, a unidade controladora capaz de relacioná-los ao CNES/DATASUS; competências exatas devem ser confirmadas pelo SIC, com encaminhamento interno se necessário.

**Período exato:** eventos e inscrições entre **28/07/2025 e 29/08/2026**, cobrindo todas as chamadas dos ciclos 1, 2 e 3. Incluir eventos posteriores ao fim das inscrições e até o corte, bem como eventos anteriores a 28/07/2025 somente se criarem inscrição/vaga que permaneça no universo solicitado. Para a ponte CNES, vigências que intersectem **01/06/2024 a 29/08/2026**, permitindo validar o baseline e as três competências piloto sem solicitar as 23 competências CNES restantes.

**Finalidade:** auditar o funil completo, reconstruir spells vaga–profissional e mensurar futuramente cobertura de 90/120/180 dias sem viés de sobrevivência; permitir que o controlador vincule participação PMM-E ao cadastro CNES com minimização de dados. Presença cadastral no CNES não será tratada como participação ou capacidade líquida.

## Tabelas solicitadas

### `inscricoes_universo.csv` — uma linha por inscrição submetida

| Campo | Tipo | Definição |
|---|---|---|
| `id_inscricao_pseudo` | texto | Chave estável da inscrição, inclusive inválida, retirada ou não publicada. |
| `id_profissional_pseudo` | texto | Chave estável do profissional nos pacotes PMM-E, sem identificador civil. |
| `ciclo` | texto | Ciclo da inscrição. |
| `chamada` | texto | Chamada da inscrição. |
| `timestamp_submissao` | timestamp | Momento da submissão com fuso. |
| `status_validacao` | categoria | Resultado documentado da validação administrativa. |
| `motivo_invalidacao` | texto/NA | Motivo quando aplicável. |
| `quantidade_opcoes` | inteiro | Número de escolhas submetidas; zero apenas se observado. |
| `versao_registro` | texto | Versão do registro no corte. |

**Chave:** `id_inscricao_pseudo`. Um registro publicado pode representar uma preferência; um candidato pode ter várias linhas publicadas; nenhuma dessas contagens substitui o universo completo de inscrições.

### `inscricoes_opcoes.csv` — uma linha por inscrição e opção de vaga

| Campo | Tipo | Definição |
|---|---|---|
| `id_inscricao_pseudo` | texto | Liga ao universo. |
| `ordem_opcao` | inteiro | Ordem declarada da preferência. |
| `id_vaga_pseudo` | texto | Vaga individual escolhida, estável entre pacotes. |
| `timestamp_escolha` | timestamp/NULL | Momento registrado da escolha ou alteração. |
| `status_opcao` | categoria | Situação administrativa da opção no corte. |

**Chave:** `id_inscricao_pseudo + ordem_opcao` por versão vigente; alterações devem aparecer no log de eventos.

### `opcoes_elegiveis.csv` — uma linha por inscrição, vaga disponível e intervalo de visibilidade

Esta tabela representa o **conjunto de escolha efetivamente disponível** ao candidato no momento da decisão. Não deve conter apenas as opções selecionadas.

| Campo | Tipo | Definição |
|---|---|---|
| `id_inscricao_pseudo` | texto | Inscrição para a qual a alternativa estava disponível. |
| `id_vaga_pseudo` | texto | Vaga individual elegível ou exibida. |
| `inicio_visibilidade` | timestamp | Início do intervalo em que a opção podia ser escolhida. |
| `fim_visibilidade` | timestamp/NULL | Fim exclusivo do intervalo; vazio se disponível no corte. |
| `elegivel` | booleano | Indica se o profissional cumpria os critérios no intervalo. |
| `motivo_inelegibilidade` | categoria/NA | Regra administrativa quando a vaga era visível, mas não elegível. |
| `status_disponibilidade` | categoria | Disponível, temporariamente indisponível, ocupada, retirada ou domínio real documentado. |
| `versao_catalogo` | texto | Versão da oferta e das regras usada para produzir a linha. |

**Chave:** `id_inscricao_pseudo + id_vaga_pseudo + inicio_visibilidade`. Se a materialização inscrição–vaga for operacionalmente excessiva, aceita-se o catálogo versionado de vagas mais as regras e atributos pseudonimizados necessários para o controlador reconstruir exatamente esse conjunto. A ausência desta tabela limita a análise à descrição das opções escolhidas e impede estimar preferências frente às oportunidades reais.

### `perfil_preferencia_minimizado.csv` — atributos pré-escolha, categorizados

Solicitam-se somente atributos administrativos existentes antes da escolha e necessários para heterogeneidade de preferência, em formato minimizado:

| Campo | Tipo | Definição |
|---|---|---|
| `id_profissional_pseudo` | texto | Chave estável, sem identificador civil. |
| `faixa_tempo_desde_especializacao` | categoria/NA | Faixas pré-definidas e suficientemente agregadas. |
| `experiencia_sus_previa` | booleano/NA | Indicador administrativo anterior à inscrição. |
| `experiencia_area_vulneravel_previa` | booleano/NA | Indicador anterior à inscrição, quando já existente no sistema. |
| `faixa_etaria` | categoria/NA | Faixa ampla, somente se necessária e autorizada. |

Não se solicita endereço, data de nascimento, currículo narrativo ou dado criado a partir do desfecho. A escolha de município vulnerável não deve ser usada para construir retrospectivamente uma proxy de “vocação”.

### `vinculos_profissional_opcao.csv` — indicadores territoriais derivados pelo controlador

Uma linha por profissional e vaga presente no conjunto de escolha, produzida internamente sem divulgar localidades pessoais:

| Campo | Tipo | Definição |
|---|---|---|
| `id_profissional_pseudo` | texto | Liga ao perfil e às inscrições. |
| `id_vaga_pseudo` | texto | Alternativa de trabalho/formação. |
| `mesma_uf_residencia_opcao` | booleano/NA | Residência pré-inscrição e vaga estão na mesma UF. |
| `mesma_uf_nascimento_opcao` | booleano/NA | Nascimento e vaga estão na mesma UF. |
| `mesma_uf_graduacao_opcao` | booleano/NA | Graduação e vaga estão na mesma UF. |
| `mesma_uf_residencia_medica_opcao` | booleano/NA | Residência médica/formação especializada e vaga estão na mesma UF. |
| `faixa_distancia_residencia_opcao` | categoria/NA | Faixa de distância ou tempo de viagem, calculada pelo controlador. |
| `regra_derivacao` | texto | Fonte, data de referência, faixas e versão da transformação. |

**Chave:** `id_profissional_pseudo + id_vaga_pseudo`. Indicadores derivados são preferíveis à entrega de município de residência, nascimento ou formação. Células raras devem seguir a política de proteção do órgão.

### `eventos_longos.csv` — uma linha por evento

Formato longo obrigatório; snapshots de ativos não substituem esta tabela.

| Campo | Tipo | Definição |
|---|---|---|
| `id_evento` | texto | Identificador único e estável do evento. |
| `id_inscricao_pseudo` | texto/NA | Inscrição relacionada; `NA` quando o evento ocorre fora desse objeto. |
| `id_vaga_pseudo` | texto | Vaga afetada. |
| `id_profissional_pseudo` | texto/NA | Profissional relacionado; `NA` antes de haver pessoa associada. |
| `tipo_evento` | categoria | Tipo documentado do evento. |
| `timestamp` | timestamp | Data e hora efetivas, com fuso e precisão declarada. |
| `estado_anterior` | texto/NA | Estado imediatamente anterior. |
| `estado_novo` | texto | Estado resultante. |
| `motivo` | texto/NA | Motivo documentado; não inferir a partir do estado. |
| `id_vaga_origem_pseudo` | texto/NA | Origem em transferência/realocação. |
| `id_vaga_destino_pseudo` | texto/NA | Destino em transferência/realocação. |
| `vigencia_inicio` | timestamp | Início do efeito administrativo do evento. |
| `registrado_em` | timestamp | Momento de registro, distinto da vigência. |
| `versao_evento` | texto | Versão/revisão do evento. |
| `evento_anulado` | booleano | Indica anulação sem apagar o histórico. |

O vocabulário deve cobrir, quando existirem administrativamente: `inscrição`, `classificação`, `convocação`, `aceite/recusa` (preservados como resultados distinguíveis), `homologação`, `entrada`, `afastamento`, `retorno`, `transferência`, `saída` e `reocupação`. A lista solicita conceitos necessários; não afirma que esses sejam os nomes internos nem que todos existam como evento separado. O dicionário deve mapear os estados reais.

### `ponte_pmme_cnes.csv` — uma linha por profissional e intervalo de validade

Preferência expressa: **o controlador realiza internamente a vinculação** usando os identificadores sob sua guarda e devolve somente:

| Campo | Tipo | Definição |
|---|---|---|
| `id_profissional_pseudo` | texto | Mesma chave estável das inscrições, eventos e pagamentos. |
| `identificador_cnes_pseudo` | texto | Token pseudonimizado estável derivado do identificador profissional no CNES. |
| `inicio_validade` | data | Início da validade da correspondência. |
| `fim_validade` | data/NULL | Fim; vazio quando vigente no corte. |
| `regra_crosswalk` | categoria/texto | Método administrativo de vinculação e versão, sem expor identificadores civis. |
| `status_vinculo` | categoria | Confirmado, não localizado, ambíguo ou outro domínio documentado. |

**Chave:** `id_profissional_pseudo + inicio_validade`. Não solicitar nem devolver CPF, CNS, CRM, nome, data de nascimento ou endereço quando a vinculação pelo controlador for suficiente.

## Chaves, estabilidade e semântica

`id_vaga_pseudo` deve ser idêntico ao pacote de vagas; `id_profissional_pseudo`, estável em inscrições, eventos, ponte e folha; `id_evento`, imutável mesmo após correção. Anulações e revisões devem ser versionadas, não apagadas. Ausência de evento nunca significa automaticamente recusa, saída ou zero dias; `NULL` significa desconhecido/não registrado; `0` apenas valor observado igual a zero; `NA` apenas não aplicável.

Solicitam-se CSV UTF-8/ZIP, timestamps ISO 8601, dicionário, data de corte, histórico de revisões, regras de atualização, domínios e hashes SHA-256, conforme [README](README.md). A pseudonimização deve usar segredo sob controle do órgão e evitar tokens derivados diretamente de identificadores civis sem proteção adequada.

## Alternativas hierarquizadas

1. Sete tabelas completas, com conjunto de escolha e linkage realizados pelo controlador.
2. Se a ponte linha a linha não puder sair: o controlador agrega o CNES por `id_profissional_pseudo` e competência e devolve indicadores/cargas cadastrais estritamente necessários, mantendo a tabela de eventos individual pseudonimizada.
3. Se microdados só puderem ser acessados em ambiente seguro: disponibilização controlada com exportação apenas de resultados de completude; ainda sem entrega de identificadores civis.
4. Se eventos individuais forem legalmente inviáveis: contagens por vaga–dia e estado, acompanhadas do universo de vagas e regras de transição. Essa alternativa não permite spells individuais completos e não fecha A07-02/A07-03 sem avaliação adicional.

## Teste objetivo de completude

A resposta é completa se: (a) toda inscrição submetida no período tem `id_inscricao_pseudo`, inclusive as não publicadas; (b) toda opção escolhida referencia inscrição e vaga existentes; (c) o conjunto elegível/visível é reconstruível no timestamp da decisão; (d) vínculos territoriais são derivados sem divulgar localidades pessoais; (e) `id_evento` é único e todos os eventos estão em linhas separadas; (f) transições inválidas, duplicidades e timestamps regressivos são zero ou explicados; (g) entradas, afastamentos, retornos, transferências e saídas reconciliam o estado no corte; (h) cada profissional associado tem ponte confirmada ou status/motivo explícito; (i) as chaves são estáveis entre arquivos; e (j) dicionário, corte, revisões, manifesto, hashes e quantificação de supressões acompanham a entrega.
