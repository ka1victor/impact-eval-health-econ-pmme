# Pacotes A07 — pedidos de dados administrativos do PMM-E

> Preparados em 29/08/2026. **Nenhum pedido foi enviado, nenhum termo foi aceito e nenhum órgão foi contatado.** A submissão depende de decisão externa do autor.

> **Prioridade em 04/09/2026:** os pacotes 1 e 2 são o caminho mínimo para a
> pergunta causal de atração pelo adicional da bolsa. O pacote 3 não é necessário
> para estimar o efeito da oferta anunciada; ele só é prioritário se o estimando
> passar a ser a dose efetivamente recebida. Ver a
> [síntese causal](../05_identificacao/16_sintese_achados_e_novo_plano_causal.md).

O texto único pronto para submissão, ainda não enviado, está em
[`solicitacao_focal_rdd_bolsa.md`](solicitacao_focal_rdd_bolsa.md). Ele remete
aos layouts detalhados abaixo e deixa canal, protocolo e eventuais termos em
aberto para decisão expressa do autor.

## Escopo fechado

Estes documentos operacionalizam exclusivamente as seis lacunas fechadas pelo portão A06: A07-01 cadastro e versionamento de vagas; A07-02 inscrições e eventos; A07-03 ponte pseudonimizada PMM-E–CNES; A07-04 regra histórica do IVS por vaga; A07-05 folha mensal e execução financeira vinculável; e A07-06 documentação e historicização dos painéis.

Eles preservam as distinções obrigatórias: célula CNES–curso, quantidade e vaga individual são unidades diferentes; registro publicado, candidato único e universo de inscrições não são equivalentes; os 518 CNES do snapshot nominal não são a união de 1.930 CNES dos quadros; faixa anunciada, devido, empenhado, liquidado e pago são estágios distintos; presença no CNES não prova participação no PMM-E ou capacidade líquida; e as competências 202406, 202506 e 202607 são apenas piloto, não painel completo.

## Ordem sugerida e dependências

| Ordem | Pacote | Lacunas | Destinatário provável, a confirmar pelo SIC | Dependência | Status inicial |
|---:|---|---|---|---|---|
| 1 | [Vagas e regra do IVS](vagas_e_regra_ivs.md) | A07-01, A07-04 | Ministério da Saúde, unidade da SGTES responsável pela gestão do PMM-E | Nenhuma | `não enviado` |
| 2 | [Eventos e ponte CNES](eventos_e_ponte_cnes.md) | A07-02, A07-03 | Ministério da Saúde, SGTES e unidade controladora dos registros PMM-E, com articulação interna com o CNES/DATASUS se cabível | Reutilizar as chaves pseudonimizadas do pacote 1 | `não enviado` |
| 3 | [Pagamentos mensais](pagamentos_mensais.md) | A07-05 | Ministério da Saúde, unidade gestora da bolsa e unidade de execução financeira, a serem identificadas pelo SIC | Reutilizar as chaves dos pacotes 1 e 2 | `não enviado` |
| 4 | [Documentação e reposição](documentacao_e_reposicao.md) | A07-06 | Ministério da Saúde, unidade produtora dos painéis e unidade responsável pelas páginas dos chamamentos | Pode tramitar em paralelo; documentação deve acompanhar os demais | `não enviado` |

Para o trabalho curto de atração/retenção, o [pedido focal do corte de seleção](cutoff_selecao_causal.md) extrai o subconjunto mínimo dos pacotes 1 e 2: regra de desempate, distância etária ao cutoff, chaves pseudonimizadas e eventos de entrada/presença.

“Provável” não afirma competência interna. Se a unidade indicada não custodiar os dados, solicita-se encaminhamento interno ao custodiante competente, sem presumir o nome de sistema, base ou campo interno.

## Padrão comum de entrega solicitado

- arquivos CSV separados por tabela, UTF-8, delimitador vírgula, aspas duplas e cabeçalho na primeira linha;
- datas ISO 8601 (`AAAA-MM-DD`), timestamps com fuso (`AAAA-MM-DDThh:mm:ss±hh:mm`) e competências `AAAAMM`;
- identificadores e códigos como texto, preservando zeros à esquerda; valores monetários em centavos inteiros ou decimal com ponto, conforme dicionário;
- pacote ZIP, sem senha enviada no mesmo canal; um SHA-256 por arquivo e manifesto com tamanho em bytes;
- dicionário, data de corte, período coberto, histórico de revisões, regra de atualização e versão do esquema;
- chaves pseudonimizadas estáveis, não reversíveis pelo pesquisador e consistentes entre pacotes; a pseudonimização reduz riscos, mas não é promessa de anonimato absoluto;
- ausência representada como vazio/`NULL` somente quando desconhecida ou não registrada; zero apenas para valor ou contagem observada igual a zero; `NA` apenas quando o campo não se aplica. O dicionário deve declarar eventuais códigos diferentes.

## Checklist de resposta

- [ ] A resposta identifica custodiante, data de corte, cobertura temporal e eventuais exclusões.
- [ ] Cada tabela corresponde ao grão solicitado e passa o teste de chave declarado no pacote.
- [ ] `id_vaga_pseudo` e `id_profissional_pseudo` são estáveis nas extrações aplicáveis.
- [ ] O log de eventos está em formato longo, uma linha por evento.
- [ ] O controlador realizou a vinculação PMM-E–CNES ou forneceu alternativa segura sem identificadores civis.
- [ ] Ausência, zero e não aplicável estão diferenciados.
- [ ] Dicionário, versões, revisões, manifesto e hashes acompanham os arquivos.
- [ ] Restrições ou supressões são quantificadas por tabela, período e motivo.
- [ ] A resposta foi triada segundo [triagem_de_respostas.md](triagem_de_respostas.md).

O recebimento de arquivos não libera automaticamente o prompt 03. A integração deve passar por novo portão; até lá, a decisão vigente continua `aguardar dados administrativos`.
