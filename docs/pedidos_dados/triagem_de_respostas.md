# Triagem das respostas administrativas

> Este procedimento começa somente após eventual submissão e recebimento autorizado. Preparar os pedidos não libera o prompt 03.

## 1. Preservação e registro

1. Preservar os bytes recebidos em diretório bruto novo, sem editar ou regravar os arquivos originais.
2. Registrar canal, protocolo, órgão/unidade informada, datas de pedido/resposta, restrições de uso e data de corte.
3. Calcular SHA-256 e tamanho de cada arquivo; comparar com o manifesto do órgão quando houver.
4. Separar anexos, dicionários, ofícios e arquivos de dados; nunca versionar publicamente conteúdo restrito ou pessoal.
5. Criar transformação somente por script versionado, com saída em `output/`. Não alterar `data/` observado.

## 2. Validação estrutural

- conferir formato, UTF-8, delimitador, cabeçalho, número de linhas/colunas e leitura sem truncamento;
- validar tipos, domínios, zeros, `NULL` e `NA` contra o dicionário;
- testar unicidade das chaves e integridade referencial descritas em [layouts_requisitados.md](layouts_requisitados.md);
- testar estabilidade de `id_vaga_pseudo` e `id_profissional_pseudo` entre todos os pacotes;
- verificar intervalos sobrepostos, timestamps regressivos, eventos duplicados e revisões apagadas;
- reconciliar vagas por publicação, inscrições por chamada, estados no corte e totais financeiros;
- quantificar linhas suprimidas, não localizadas, ambíguas e fora de escopo.

Falha de leitura, ausência de dicionário ou chave instável classifica a resposta como `incompleta`, nunca como zero.

## 3. Testes substantivos por lacuna

| Lacuna | Teste necessário para “atendida” |
|---|---|
| A07-01 | Vaga individual distinguível de célula/quantidade; versões e reapresentações reconciliadas por ID estável. |
| A07-02 | Universo inclui inscrições submetidas além dos resultados publicados; log longo permite reconstruir entrada, interrupções, saída e reocupação. |
| A07-03 | Controlador devolveu ponte pseudonimizada válida ou derivação CNES minimizada; ausência de identificadores civis na entrega de pesquisa. |
| A07-04 | Escore aplicado, vintagem, precisão, arredondamento, cutoff, categoria, faixa, vigência e exceção estão observados por vaga/regra. |
| A07-05 | Devido e pago são observados por competência, vaga e profissional; anunciado/empenhado/liquidado/pago não são confundidos; reconciliação documentada. |
| A07-06 | Definição de ativo, corte, atualização, afastamento/transferência, revisão, historicização de faixa e dicionários explicam snapshots e revisões. |

Cada lacuna recebe `atendida`, `parcial`, `não atendida` ou `não avaliável`, acompanhada de evidência, contagem e hash. Uma alternativa agregada pode ser útil sem fechar a lacuna individual.

## 4. Proteção de dados

- interromper processamento e isolar a resposta se ela trouxer CPF, CNS, CRM, nome, endereço, conta bancária ou outro identificador não solicitado;
- não publicar amostras de linhas, tokens raros ou cruzamentos que elevem risco de reidentificação;
- confirmar finalidade, minimização, retenção, controle de acesso e descarte conforme termos válidos e LGPD;
- tratar pseudonimização como medida de segurança, não anonimato absoluto;
- não aceitar novos termos nem transferir dados antes de decisão expressa do autor.

## 5. Novo portão antes do prompt 03

Produzir uma matriz variável–fonte revisada e responder novamente às nove perguntas do A06. O prompt 03 só pode ser considerado liberado se, no mínimo:

1. o contraste institucional e a regra administrativa estiverem reconstruídos sem substituir o IVS 2010 canônico por outra variável;
2. houver denominador de vagas e IDs estáveis suficientes para a população pretendida;
3. eventos permitirem mensurar a janela proposta sem usar snapshot de sobreviventes como spell;
4. a ponte PMM-E–CNES for segura e validada, se FTE/vínculos integrarem o desenho;
5. a dose financeira necessária ao contraste estiver observada no estágio correto;
6. revisões e definições dos painéis forem interpretáveis;
7. limitações, perdas e alternativas forem registradas antes de olhar efeitos.

Receber apenas parte dos pacotes não autoriza redefinir silenciosamente outcome, população ou tratamento. Se os critérios falharem, manter `aguardar dados administrativos`, reduzir formalmente o escopo em decisão do autor ou parar. Não executar estimação durante a triagem.

## 6. Registro de decisão

O novo portão deve gerar relatório e JSON versionados com: commit base, data de referência, hashes de entradas, resultado de cada teste, decisão final, autorização explícita ou bloqueio do prompt 03 e próximo prompt. Até esse registro existir, o estado vigente permanece o de `output/aquisicao/portao_integrado.json`: `aguardar dados administrativos`, protocolo e estimação não liberados.
