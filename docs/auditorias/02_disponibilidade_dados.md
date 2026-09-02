# Auditoria de disponibilidade dos dados

> **Adendo prospectivo de 30/08/2026:** a Nota Técnica nº
> 59/2026-CGPLAD/DEGEPS/SGTES/MS, publicada em 24/07/2026, definiu uma
> assinatura cadastral potencial do PMM-E no CNES (`IND_VINCULACAO=070102`,
> CNPJ de detalhamento do Ministério da Saúde, CBO e cargas horárias). O arquivo
> público `tbCargaHorariaSus` contém esses campos, mas o pipeline consolidado
> descartou o CNPJ e a implementação pelos gestores ainda não foi testada. Isso
> abre uma nova auditoria prospectiva para o ciclo 3; não altera a conclusão
> desta auditoria sobre os arquivos então integrados. Veja
> [`12_estrategia_causal_prospectiva_ciclo3.md`](../05_identificacao/12_estrategia_causal_prospectiva_ciclo3.md).

> **Data da auditoria:** 27 de agosto de 2026
>
> **Escopo:** vagas e trajetória administrativa do PMM-E, CNES mensal, chaves de vinculação e maturidade das janelas de 90, 120 e 180 dias.
>
> **Não contém:** estimação de efeitos, imputação de eventos ausentes ou aquisição de bases de WP3, WP4 e WP5.

## 1. Conclusão executiva

O estudo prioritário, tal como definido — efeito do incentivo sobre cobertura sustentada e capacidade líquida — está **aguardando dados administrativos**. A auditoria encontrou e preservou 11 planilhas oficiais pequenas do Ministério da Saúde, que melhoram substancialmente a observação das vagas, candidaturas e alocações. O CNES mensal necessário para FTE e infraestrutura também é público e tem competências disponíveis de junho de 2017 a julho de 2026 no catálogo consultado.

Isso ainda não abre o portão de estimação por cinco razões:

1. nenhum quadro público contém identificador estável da vaga; CNES, curso e chamada permitem construir uma chave analítica, mas não distinguem com segurança uma vaga reapresentada de uma nova vaga;
2. as listas públicas registram etapas finais e estados correntes, não o log completo de candidatura, convocação, aceite, recusa, entrada, afastamento, transferência e saída;
3. não existe identificador profissional comum entre cadastro PMM-E, quadros de vagas e CNES mensal; nome, CRM, CPF mascarado e CNS não formam hoje uma chave determinística compartilhada;
4. a faixa anunciada está disponível, mas o escore/vintagem de IVS aplicado e o valor mensal efetivamente pago não foram localizados por vaga e competência;
5. as bases locais observam estoque de ativos, não spells vaga–profissional. Logo, até chamadas com 180 dias de calendário não têm `cobertura_180` mensurável.

**Classificação final:** `aguardando dados`. É possível construir agora um painel descritivo parcial de ofertas e resultados publicados; não é possível calcular o outcome primário nem identificar causalmente o incentivo.

## 2. Convenção de disponibilidade

| Código | Classificação exigida pelo prompt | Significado nesta auditoria |
|---|---|---|
| `L` | Disponível localmente | Campo observado em arquivo preservado no repositório |
| `P` | Disponível publicamente | Fonte oficial localizada, mas ainda não adquirida ou incompleta para todos os ciclos |
| `LAI` | Somente por pedido administrativo/LAI | Não publicado no nível ou com a chave necessária |
| `NL` | Não localizado | Não foi encontrado em fonte pública oficial consultada |
| `I` | Inadequado para o estimando | Existe, mas não mede a variável pretendida sem inferência indevida |

`L` e `P` não significam que o campo seja suficiente para identificação causal. A adequação depende da unidade, da temporalidade, da chave e da definição administrativa.

## 3. Auditoria das três bases existentes

Nenhum dos três arquivos foi alterado. Os hashes permanecem os mesmos do inventário anterior.

### 3.1 Cadastro nominal de ativos

`data/pmm_especialistas_nominal.csv` contém 1.480 linhas, todas referidas a 12/08/2026, com início de atividade entre 11/09/2025 e 24/07/2026. Há 1.478 pares únicos UF–CRM e duas ocorrências excedentes à unicidade.

Campos úteis:

- município, CNES, curso, faixa corrente, início da atividade, ciclo, nome e CRM;
- fotografia dos participantes ainda ativos em 12/08/2026;
- possível apoio à vinculação auditiva por nome–CNES–curso.

Campos ou estados ausentes:

- vaga ofertada e identificador da vaga;
- candidatos não alocados, recusas e selecionados que não entraram;
- datas de afastamento, retorno, transferência e saída;
- histórico mensal da faixa e do valor pago;
- CNS ou identificador pseudonimizado comum ao CNES.

O arquivo é inadequado para retenção: condicionar a amostra aos ativos na data de referência elimina, por construção, quem saiu antes dela.

### 3.2 Série histórica agregada

`data/pmm_especialistas_serie_historica.csv` contém 7.276 linhas e nove competências. `co_cnes` e `estabelecimento` estão vazios em todas as linhas e não há identificador individual.

| Competência | Ativos somados |
|---|---:|
| dez/2025 | 577 |
| jan/2026 | 583 |
| fev/2026 | 569 |
| mar/2026 | 551 |
| abr/2026 | 1.350 |
| mai/2026 | 1.363 |
| jun/2026 | 1.501 |
| jul/2026 | 1.511 |
| ago/2026 | 1.480 |

A queda de 31 registros entre julho e agosto pode refletir saída, transferência, correção cadastral, mudança de corte ou outro processo. Sem identificador e regra de atualização, ela não pode ser traduzida em 31 desligamentos. Da mesma forma, a elevação entre março e abril não identifica entradas individuais nem vagas cobertas.

### 3.3 IVS local

`data/ivs_ipea_2010_municipios.csv` contém 5.565 municípios e o IVS 2010. É útil como running variable candidata e covariável pré-tratamento, mas não prova que esse arquivo, essa precisão e essa categorização foram usados administrativamente. A divergência de categoria documentada no Prompt 1 permanece um bloqueio.

## 4. Fontes oficiais adquiridas

Foram baixados 11 arquivos XLSX oficiais, totalizando 1.864.467 bytes. Os bytes foram preservados sem transformação em `data/raw/pmm_e/`; URLs, cobertura, unidades, data de extração, tamanhos e SHA-256 estão em `output/manifesto_fontes_pmme.json`.

Dois links ainda exibidos na página oficial de 2025 retornaram HTTP 404 em 27/08/2026:

- quadro de vagas da primeira chamada do ciclo 1;
- alocação retificada da primeira chamada do ciclo 1.

O manifesto registra as URLs quebradas e não cria substitutos sintéticos.

### 4.1 O que os quadros permitem observar

| Fonte | Conteúdo observado | Contagens estruturais | Limite principal |
|---|---|---:|---|
| Ciclo 1, chamada 1 — homologados | CPF mascarado, nome, curso, IBGE, CNES, faixa e homologação | 316 homologados | quadro de vagas e alocação estão com links quebrados |
| Ciclo 1, chamada 2 — vagas/resultados | candidatos a vagas imediatas e quadro de cadastro de reserva | 98 linhas de candidatos; 2.896 vagas de reserva publicadas | a planilha não fornece denominador inequívoco das vagas imediatas da chamada |
| Ciclo 1, chamada 2 — classificação | preferências, barema, classificação e alocação | 757 linhas; 374 alocações publicadas; 88 desclassificados | uma pessoa pode aparecer em mais de uma linha/preferência |
| Ciclo 1 — lista de homologados publicada na 2ª chamada | nome, CPF mascarado, município, CNES e curso | 581 nomes | inclui nomes já presentes na lista da 1ª chamada; não são 581 novas entradas |
| Ciclo 2, chamada 1 — vagas retificadas | CNES, IBGE, curso, faixa, imediatas e reserva | 1.836 imediatas; 1.053 reserva | não há `id_vaga`; o resultado remanescente recuperado tem apenas 9 alocações |
| Ciclo 2, chamada 2 — vagas | mesmos campos do quadro anterior | 0 imediatas; 1.992 reserva | cadastro de reserva não equivale a uma nova vaga ofertada |
| Ciclo 2, chamada 2 — resultado | preferências, classificação e situação | 303 alocações; 750 linhas em reserva; 55 desclassificados | não contém aceite, homologação, entrada ou saída |
| Ciclo 3 — adesão final dos gestores | proposta, priorização, CNES, curso e capacidade declarada | 5.131 priorizadas: 1.136 imediatas e 3.995 reserva | proposta/adesão não é o mesmo objeto que a vaga final ao médico |
| Ciclo 3 — quadro retificado aos médicos | CNES, curso, faixa, tipo de município e vagas | 5.131 vagas: 1.132 imediatas e 3.999 reserva | quatro vagas mudaram de modalidade entre as duas publicações; não há versão por `id_vaga` |
| Ciclo 3 — resultado final sub judice | preferências, classificação e situação | 704 alocações, 3.826 linhas em reserva e 2 sub judice | ainda não é trajetória de exercício |

As contagens são auditoria de estrutura, não indicadores de desempenho. Não se deve somar quadros de chamadas: a chamada 2 do ciclo 2, por exemplo, publica somente cadastro de reserva, e vagas podem ser reapresentadas.

## 5. Matriz variável × fonte × disponibilidade

### 5.1 Base A — vagas e trajetória administrativa

| Variável necessária | Bases locais originais | Planilhas oficiais preservadas | Outra fonte pública | Classificação final | Diagnóstico |
|---|---|---|---|---|---|
| Universo de vagas ofertadas | `I` | `L` parcial | páginas dos chamamentos | `P` parcial + `LAI` | falta primeira chamada de 2025 e deduplicação entre chamadas |
| Identificador estável da vaga | `NL` | `NL` | `NL` | `LAI` | CNES–curso–chamada é chave construída, não identificador administrativo |
| Chamamento/ciclo | `L` parcial | `L` por arquivo | páginas e cronogramas | `L` | deve ser incorporado como metadado da fonte |
| Município e código IBGE | `L` | `L` | `P` | `L` | códigos alternam entre 6 e 7 dígitos nos arquivos públicos; normalização é necessária |
| CNES | `L` no nominal; ausente na série | `L` | Portal CNES | `L` parcial | valores numéricos podem perder zeros à esquerda |
| Especialidade/curso | `L` | `L` | editais | `L` | rótulos mudam entre ciclos e precisam de dicionário versionado |
| Faixa anunciada na vaga | `L` corrente | `L` nos quadros de vagas | editais | `L` parcial | falta a versão original da primeira chamada de 2025; faixa corrente não é história |
| Valor anunciado por vaga | `NL` | `I` — derivável da faixa | editais | `P` | é transformação normativa, não pagamento observado |
| Valor efetivamente pago por competência | `NL` | `NL` | `NL` | `LAI` | indispensável para dose e primeiro estágio se houver exceções |
| Escore e vintagem de IVS usados | arquivo local não validado | `NL` | taxonomia Ipea, não aplicação PMM-E | `LAI` | bloqueio direto do RDD |
| Candidatura completa | `NL` | `L` parcial | sistema UNA-SUS sem microdados abertos | `LAI` | listas finais não necessariamente incluem inscrições incompletas, retiradas ou todas as escolhas |
| Classificação e alocação | `NL` | `L` parcial | páginas dos chamamentos | `L` parcial | cobertura desigual entre chamadas e versões |
| Convocação | `NL` | `I` — às vezes inferida da alocação | comunicados agregados | `LAI` | convocação não é sinônimo de aceite ou entrada |
| Aceite e recusa | `NL` | `NL` | `NL` | `LAI` | necessários para falha de conversão |
| Homologação | `NL` | `L` apenas em parte de 2025 | comunicados sem painel individual completo | `LAI` | listas de 2026 não fecham a trajetória individual |
| Entrada em exercício | `L` só para ativos em 12/08/2026 | `NL` | `NL` | `LAI` | sobreviventes não representam todas as entradas |
| Afastamento e retorno | `NL` | `NL` | `NL` | `LAI` | indispensáveis para dias cobertos |
| Transferência/realocação | `NL` | `L` episódico, sem log completo | comunicados | `LAI` | precisa de origem, destino, motivo e data |
| Saída/desligamento | `NL` | `NL` | `NL` | `LAI` | ausência posterior não pode ser tratada como saída sem regra da fonte |
| Identificador pseudonimizado estável do profissional | CRM+UF só no nominal; nome | CPF mascarado com padrões diferentes | CNS no CNES | `LAI` | não existe uma chave comum publicada |
| Datas individuais dos eventos | início só dos ativos | `NL` | cronogramas coletivos | `LAI` | cronograma administrativo não substitui timestamp individual |

### 5.2 Base B — CNES mensal

| Variável necessária | Fonte pública CNES | Disponibilidade | Adequação ao estudo |
|---|---|---|---|
| Competência mensal | base nacional desde 06/2017 | `P` | adequada para painel mensal; não mede dias exatos |
| CNS/identificador do profissional | arquivo de profissionais | `P` | longitudinal dentro do CNES, mas sem ponte segura para o PMM-E |
| CBO | arquivo de vínculos profissionais | `P` | adequada para ocupação cadastrada |
| Carga horária ambulatorial, hospitalar e outras | arquivo de vínculos | `P` | proxy cadastral de FTE; não é hora efetivamente trabalhada |
| Estabelecimento e município | arquivos CNES | `P` | adequados após normalizar CNES e IBGE |
| Vínculos anteriores e simultâneos | repetição de CNS–CNES–competência | `P` | possível contabilmente; causalidade do remanejamento exige cautela |
| Equipamentos, leitos, serviços e habilitações | módulos do estabelecimento | `P` | adequados como infraestrutura pré-tratamento se medidos antes da oferta |
| Participação/vaga específica do PMM-E | não confirmada no dicionário auditado | `NL` | exige ponte administrativa; não inferir apenas pelo CBO |
| Frequência, presença e atividade efetiva | CNES é cadastral | `I` | não mede cobertura diária nem assiduidade |

O [Portal CNES](https://wiki.saude.gov.br/cnes/index.php/Portal_CNES) documenta CNS, CBO, CNES e as cargas horárias ambulatorial, hospitalar e “outras” na extração de profissionais. O catálogo oficial de bases mensais lista `BASE_DE_DADOS_CNES_AAAAMM.ZIP`; em 27/08/2026, a competência mais recente disponível era julho de 2026.

## 6. Plano de aquisição do CNES

O bruto nacional não foi baixado porque é grande. Foi criado um plano reproduzível para junho de 2025 a julho de 2026, período que cobre um mês anterior ao primeiro quadro de vagas e toda a observação pública posterior disponível nesta auditoria.

O script `scripts/03_planejar_aquisicao_cnes.py`:

- gera, sem download por padrão, `output/manifesto_aquisicao_cnes.json`;
- lista URL, competência, cobertura, unidade e status de cada um dos 14 ZIPs;
- só baixa após as duas flags explícitas `--download --confirm-large-download`;
- não sobrescreve bruto existente;
- calcula SHA-256 após download.

Antes de executar a aquisição grande, o Prompt 3 deve decidir se serão usadas todas as competências ou apenas meses alinhados a cada chamada. Baixar a base não resolve a ausência da ponte de identificação entre SGP/PMM-E e CNS.

## 7. Janelas de 90, 120 e 180 dias

A maturidade abaixo usa como fim observado a referência do arquivo nominal, 12/08/2026, e a data do quadro final/retificado quando disponível. “Madura” significa apenas que transcorreu tempo de calendário; não significa que a cobertura seja mensurável.

| Coorte | Data de oferta usada | Dias potenciais até 12/08/2026 | 90 | 120 | 180 | Cobertura mensurável hoje? |
|---|---:|---:|:---:|:---:|:---:|:---:|
| Ciclo 1, chamada 1 | 24/07/2025 | 384 | Sim | Sim | Sim | Não |
| Ciclo 1, chamada 2 | 29/09/2025 | 317 | Sim | Sim | Sim | Não |
| Ciclo 2, chamada 1 — retificação final | 19/03/2026 | 146 | Sim | Sim | Não | Não |
| Ciclo 2, chamada 2 | 16/04/2026 | 118 | Sim | Não | Não | Não |
| Ciclo 3, chamada 1 — quadro retificado | 24/07/2026 | 19 | Não | Não | Não | Não |

Implicações:

- uma janela comum de 180 dias só é madura nas chamadas de 2025;
- 120 dias alcançam 2025 e a primeira chamada do ciclo 2;
- 90 dias alcançam também a segunda chamada do ciclo 2;
- incluir o ciclo 3 no mesmo corte de dados reduz a janela comum a menos de 30 dias;
- nenhuma dessas janelas pode ser calculada com o estoque nominal e a série agregada atuais.

O protocolo não deve escolher 90 dias apenas para maximizar o número de coortes. Primeiro precisa definir a população institucionalmente comparável e recuperar eventos de cobertura; depois congela a maior janela comum antes de observar efeitos.

## 8. Viabilidade da vinculação

### 8.1 O que é possível como auditoria

- 746 das 1.480 linhas do nominal têm correspondência exata de nome normalizado em alguma lista pública preservada;
- 1.170 das 1.480 linhas têm combinação CNES–curso presente em algum quadro público de vagas;
- município, CNES e curso permitem verificar plausibilidade e localizar inconsistências;
- códigos CNES devem ser tratados como identificadores de sete dígitos, e códigos IBGE precisam de crosswalk entre formatos de seis e sete dígitos.

Essas taxas não são medidas de preenchimento. A cobertura pública é incompleta, listas podem ser cumulativas e nome não é chave de pesquisa aceitável para o painel final.

### 8.2 O que não é possível com segurança

Não há chave determinística que ligue:

```text
vaga administrativa → candidatura/alocação → participante PMM-E → vínculo CNES mensal
```

O nominal traz CRM e nome; resultados trazem nome e CPF mascarado; CNES traz CNS e nome. A vinculação probabilística por nome pode gerar falsos positivos, muda com homônimos e expõe dados pessoais desnecessariamente. A solução adequada é receber do Ministério uma chave pseudonimizada estável ou um crosswalk produzido pelo controlador dos dados.

### 8.3 Identificador mínimo recomendado

Cada extração administrativa deveria conter:

- `id_vaga_pseudo`, estável entre retificações e chamadas;
- `id_profissional_pseudo`, estável entre SGP, pagamento e CNES;
- `id_evento` e timestamp;
- `versao_registro` ou data de vigência;
- CNES, curso, chamamento e cota como atributos, não como substitutos da chave.

## 9. Pedidos administrativos necessários

Os pedidos devem solicitar microdados pseudonimizados, dicionário, regras de atualização e versão histórica, com base legal e ambiente de acesso compatíveis com LGPD.

### Pedido 1 — cadastro mestre e versionamento das vagas

Solicitar à SGTES/DGEPSS, para todos os ciclos e chamadas do PMM-E:

- identificador estável pseudonimizado da vaga;
- edital, ciclo, chamada, data e versão de publicação;
- município/IBGE, CNES, curso, tipo de prática e cota;
- vagas imediatas e de reserva, com indicação de reapresentação ou criação;
- faixa anunciada original, valor anunciado e vigência;
- escore, categoria, vintagem e precisão do IVS usados;
- status e motivo de retificação, retirada, remanejamento ou cancelamento.

### Pedido 2 — log de candidaturas e trajetória da vaga

Uma linha por evento, com `id_vaga_pseudo`, `id_profissional_pseudo`, timestamp, situação anterior, situação nova e motivo, cobrindo:

- inscrição e ordem das escolhas;
- elegibilidade/classificação;
- convocação;
- aceite ou recusa;
- homologação;
- entrada em exercício;
- afastamento e retorno;
- transferência/realocação;
- desistência, desligamento ou encerramento;
- reocupação por outro profissional.

O pedido deve incluir a definição de cada status e informar se ausência de linha significa zero, não aplicável ou dado não registrado.

### Pedido 3 — ponte segura com o CNES

Solicitar crosswalk pseudonimizado entre `id_profissional_pseudo` e CNS/identificador interno usado no CNES, ou pedir que o próprio Ministério faça a vinculação e devolva apenas a chave pseudonimizada. Incluir datas de validade e mudanças de CNS.

### Pedido 4 — pagamentos

Solicitar, por competência, vaga e profissional:

- valor devido e valor pago da bolsa;
- componente fixo, componente variável e ajuda de custo;
- faixa/regra aplicada;
- suspensão, glosa, estorno, retroativo e correção;
- data de competência e data de pagamento.

Sem isso, o tratamento permanece oferta normativa do incentivo, não dose recebida.

### Pedido 5 — documentação dos painéis

Solicitar dicionário e regra de produção do cadastro nominal e da série histórica, incluindo:

- definição de “ativo” e data de corte;
- tratamento de afastamento, transferência e atraso cadastral;
- razão de `co_cnes` e estabelecimento vazios na série;
- historicização ou recodificação da faixa;
- explicação da divergência entre categoria textual de IVS e IVS 2010 local;
- política de revisão retroativa das competências.

### Pedido 6 — reposição dos arquivos públicos quebrados

Solicitar cópia autenticada ou novo link para o quadro de vagas e a alocação retificada da primeira chamada de 2025, preservando todas as versões anteriores e datas de vigência.

## 10. Consequência para o estimando

As fontes públicas sustentam que a faixa é anunciada por vaga, mas ainda não demonstram:

- qual escore exato gerou a faixa;
- se o valor efetivamente recebido acompanhou a regra;
- se vagas próximas aos cutoffs são comparáveis em composição e priorização;
- se uma unidade observada em chamadas posteriores é a mesma vaga reapresentada;
- quantos dias cada vaga esteve coberta.

Portanto, o Prompt 3 não deve congelar um RDD como desenho principal enquanto esses pontos permanecerem abertos. A saída honesta do portão é:

```text
painel descritivo de vagas publicadas:  executável parcialmente
cobertura sustentada de 90/120/180 dias: aguardando log administrativo
FTE e infraestrutura prévia:             publicamente adquiríveis, mas aguardam CNES e ponte de identificação
RDD do incentivo:                         bloqueado por regra/escore e primeiro estágio não observados
estudo causal prioritário:                aguardando dados
```

## 11. Reprodutibilidade e manifestos

Arquivos produzidos por esta auditoria:

- `scripts/01_adquirir_fontes_pmme.py`: aquisição idempotente das planilhas pequenas; recusa sobrescrever mudança remota;
- `scripts/02_auditar_fontes_pmme.py`: leitura somente, hashes, estrutura, contagens, vinculação auditiva e maturidade das janelas;
- `scripts/03_planejar_aquisicao_cnes.py`: plano e aquisição opcional dos ZIPs grandes do CNES;
- `output/manifesto_fontes_pmme.json`: URLs, datas, cobertura, unidades, tamanhos, hashes e falhas de download;
- `output/auditoria_fontes_pmme.json`: diagnóstico reproduzível das fontes preservadas;
- `output/manifesto_aquisicao_cnes.json`: competências, URLs e status do CNES planejado.

Fontes de catálogo e documentação:

- [Dados Abertos do SUS — Programa de Provimento Federal](https://dadosabertos.saude.gov.br/dataset/provimento-federal-programa-mais-medicos);
- [Chamamento PMM-E de 2025](https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2025/chamamento-publico-sgtes-ms-no-3-2025-pmm-e);
- [Chamamento PMM-E do ciclo 2 de 2026](https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2026/chamamento-publico-sgtes-ms-no-1-2026-pmm-e/chamamento-publico-sgtes-ms-no-1-2026-pmm-e);
- [Adesão de gestores ao ciclo 3](https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2026/chamamento-publico-sgtes-ms-no-5-2026-pmm-e);
- [Chamamento médico do ciclo 3](https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2026/chamamento-publico-sgtes-ms-no-6-2026-pmm-e);
- [Portal CNES — documentação de campos e downloads](https://wiki.saude.gov.br/cnes/index.php/Portal_CNES);
- [Catálogo mensal da base nacional do CNES](https://cnes.datasus.gov.br/pages/downloads/arquivosBaseDados.jsp).

## 12. Decisão para o roadmap

O Prompt 2 melhora a base documental, mas **não libera estimação**. O próximo agente deve usar este diagnóstico para congelar um protocolo condicional:

1. se os pedidos administrativos entregarem vaga, eventos, ponte profissional e regra do IVS, prosseguir com o outcome de cobertura e testar o desenho causal;
2. se vierem vaga e eventos, mas não CNES, limitar a conclusão à cobertura administrativa sem adicionalidade/FTE;
3. se vier CNES sem ponte com o PMM-E, usar infraestrutura prévia no nível do estabelecimento, mas não atribuir vínculos individuais ao programa;
4. se não vier identificador estável e log de eventos, parar o estudo causal e manter apenas descrição transparente das publicações.
