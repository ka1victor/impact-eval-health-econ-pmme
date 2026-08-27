# A07 — Pacote de pedidos administrativos

## Pré-requisitos

Execute depois de A06 e use exclusivamente as lacunas finais do portão integrado.
Leia `AGENTS.md`, `CLAUDE.md`, as três auditorias e todos os relatórios A01–A06.

## Missão

Preparar pedidos modulares, precisos e tecnicamente utilizáveis para os dados que
continuarem indisponíveis. **Não envie pedidos, não aceite termos e não contate
órgãos em nome do autor.** A submissão é uma decisão externa do autor.

## Pacotes a preparar

Crie apenas os pacotes ainda necessários:

1. `vagas_e_regra_ivs.md`: cadastro mestre, versões, reapresentações, score,
   vintagem, precisão, cutoff, faixa, valor anunciado e exceções;
2. `eventos_e_ponte_cnes.md`: log de candidatura a encerramento, spells,
   `id_vaga_pseudo`, `id_profissional_pseudo` e crosswalk seguro com CNES;
3. `pagamentos_mensais.md`: valores devidos/pagos, componentes, glosas,
   retroativos e competência;
4. `documentacao_e_reposicao.md`: dicionários, regras dos painéis, definição de
   ativo, versionamento e reposição de arquivos públicos quebrados.

## Especificação mínima de cada pedido

- órgão/unidade provável e período exato;
- justificativa pública e finalidade de pesquisa;
- grão de cada tabela e layout CSV sugerido;
- nomes, tipos e definições dos campos;
- chaves entre tabelas e estabilidade temporal;
- significado de ausência, zero e não aplicável;
- data de corte, histórico de revisões e dicionário;
- formato, codificação e compressão;
- solicitação de dados pseudonimizados e minimização conforme LGPD;
- alternativa hierarquizada caso o nível individual não possa ser fornecido;
- teste objetivo para considerar a resposta completa.

Peça logs em formato longo — uma linha por evento — e não apenas fotografia dos
ativos. Para o crosswalk, prefira que o controlador faça a vinculação e devolva
chave pseudonimizada, evitando circulação de identificadores civis.

## Entregáveis

- arquivos em `docs/pedidos_dados/` para cada pacote necessário;
- `docs/pedidos_dados/README.md` com ordem de envio, dependências, órgão, status
  inicial `não enviado` e checklist de resposta;
- `docs/pedidos_dados/layouts_requisitados.md`, com tabelas e chaves;
- `docs/pedidos_dados/triagem_de_respostas.md`, dizendo como preservar, hashear,
  validar e decidir se o prompt 03 foi liberado.

Não inclua resultado causal, não prometa anonimato absoluto e não solicite dados
pessoais identificáveis quando pseudonimização ou vinculação pelo controlador
resolver. Valide referências e consistência com A06, faça commit próprio e
informe hash; não faça push ou merge.

