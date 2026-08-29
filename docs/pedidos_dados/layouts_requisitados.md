# Layouts requisitados e chaves entre pacotes

Este documento consolida o contrato técnico sugerido. Os campos são **nomes de entrega solicitados**, não nomes atribuídos a sistemas internos.

## Mapa de tabelas

| Tabela | Grão | Chave primária sugerida | Chaves estrangeiras |
|---|---|---|---|
| `vagas_mestre.csv` | vaga individual | `id_vaga_pseudo` | `id_vaga_origem_pseudo` → vaga |
| `vagas_versoes.csv` | vaga–versão | `id_vaga_pseudo + id_versao` | vaga |
| `regra_ivs_vaga.csv` | vaga–vigência da regra | `id_vaga_pseudo + vigencia_inicio` | vaga |
| `inscricoes_universo.csv` | inscrição submetida | `id_inscricao_pseudo` | profissional |
| `inscricoes_opcoes.csv` | inscrição–opção | `id_inscricao_pseudo + ordem_opcao` | inscrição, vaga |
| `eventos_longos.csv` | evento individual | `id_evento` | inscrição, vaga, profissional, vaga origem/destino |
| `ponte_pmme_cnes.csv` | profissional–intervalo | `id_profissional_pseudo + inicio_validade` | profissional |
| `folha_componentes.csv` | competência–vaga–profissional–componente–versão | chave composta correspondente | vaga, profissional |
| `execucao_financeira.csv` | documento–estágio | `id_documento_financeiro_pseudo + estagio + data_estagio` | vaga, profissional, documento origem |
| `painel_metadados.csv` | produto–versão | `id_produto + versao` | dicionário |
| `revisoes_painel.csv` | revisão | `id_revisao` | produto |
| `arquivos_publicos.csv` | arquivo–versão | `id_arquivo` | arquivo substituído |

## Chaves transversais e estabilidade

| Chave | Escopo | Requisito de estabilidade |
|---|---|---|
| `id_vaga_pseudo` | vagas, opções, eventos, regra IVS e pagamentos | Mesma vaga física através de retificações, reapresentações, mudança de modalidade, ocupações e reocupações. Não derivar apenas de CNES–curso. |
| `id_profissional_pseudo` | inscrições, eventos, ponte e pagamentos | Mesma pessoa através de ciclos, chamadas e fontes administrativas; não expor identificador civil. |
| `id_inscricao_pseudo` | universo, opções e eventos | Persistir após validação, retirada ou correção. |
| `identificador_cnes_pseudo` | ponte | Estável para a identidade CNES enquanto válida; mudanças devem abrir novo intervalo. |
| `id_evento` | eventos | Imutável; correções criam versão/anulação, não reutilizam o ID. |

O controlador deve manter a tabela secreta de correspondência. Tokens devem ser determinísticos dentro do escopo acordado, resistentes a reversão e consistentes entre extrações. Não se solicita o segredo nem identificadores de origem.

## Domínios e representação

- `texto`: string UTF-8; códigos como texto para preservar zeros.
- `data`: `AAAA-MM-DD`.
- `timestamp`: ISO 8601 com offset; declarar precisão e timezone.
- `competencia`: `AAAAMM`.
- `decimal`: ponto como separador decimal, sem separador de milhar; moeda declarada.
- `booleano`: `true`/`false`.
- `NULL`: campo vazio por desconhecimento/não registro, acompanhado de status quando necessário.
- `0`: observação quantitativa confirmada igual a zero.
- `NA`: não aplicável segundo regra; códigos alternativos precisam de dicionário.

Cada CSV deve ter cabeçalho único, delimitador vírgula, aspas duplas e quebra de linha consistente. Entrega em ZIP; manifesto deve listar nome, tabela, linhas, colunas, bytes, SHA-256, corte, período e versão de esquema.

## Regras de integridade

1. Chaves primárias não nulas e sem duplicidade na versão corrente.
2. Toda chave estrangeira resolve na tabela-mãe, salvo `NA` permitido e documentado.
3. Intervalos usam início inclusivo e fim exclusivo, salvo convenção contrária documentada; não se sobrepõem para a mesma entidade sem motivo.
4. Eventos têm `registrado_em >= timestamp` ou exceção explicada; anulações não apagam o histórico.
5. Valores financeiros mantêm competência e data de pagamento separadas.
6. Agregação de `vagas_mestre` por versão deve reconciliar quantidades publicadas sem confundir célula CNES–curso, quantidade e vaga individual.
7. O vínculo CNES só indica correspondência cadastral; não codifica, sozinho, participação no PMM-E nem capacidade líquida.

## Dicionário mínimo por campo

Para cada coluna: nome entregue, nome/origem administrativa se divulgável, definição, tipo, domínio, unidade, nulabilidade, chave, regra de derivação, vigência, mudança de definição, significado de vazio/zero/NA e exemplo sintético. Para cada tabela: grão, população incluída/excluída, corte, atualização, revisão e responsável custodiante.
