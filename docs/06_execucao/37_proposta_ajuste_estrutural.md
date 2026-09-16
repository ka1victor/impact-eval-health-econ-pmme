# 37. Proposta de ajuste estrutural — o que está fundamentalmente errado

> [!IMPORTANT]
> **Status: PROPOSTA. Nada aqui foi aplicado.** Nenhum número foi reestimado,
> nenhuma amostra foi mexida, nenhuma especificação foi trocada. O documento
> lista defeitos, mostra a evidência de cada um e propõe a correção, para o
> autor decidir o que entra e em que ordem.<br>
> **Data:** 16 de setembro de 2026.<br>
> **Origem:** pergunta do autor sobre duas suspeitas — se o repositório
> descreve mal a finalidade do programa (formação × atração) e se descreve mal
> a unidade territorial (município × grupo de municípios). As duas se
> confirmaram, e a verificação abriu outras.

---

## 0. Como ler

Cada item tem um tipo, e o tipo governa o custo:

| Tipo | Significado | Exige reexecução? |
|---|---|---|
| **F** | fundamental: muda o que o trabalho afirma ou o objeto que ele mede | depende |
| **D** | descrição: o que foi feito está certo, o que está escrito está errado | não |
| **P** | proveniência: a cadeia de reprodução está quebrada | sim, quando desbloquear |

**Regra de ordem, inegociável.** Quatro itens desta proposta mudam insumo de
estimativa já publicada. Para todos eles, os coeficientes candidatos **já são
conhecidos** (ver F4). O `CLAUDE.md` proíbe escolher filtro, janela ou
estimador depois de ver resultado. Logo: cada correção que toque insumo é
declarada como **conserto de defeito**, com o defeito descrito antes, e a
decisão registrada **antes** de rodar. Se o defeito não for demonstrável sem
olhar o resultado, o item não entra.

**Sobre os números desta proposta.** As conferências abaixo foram feitas por
leitura direta dos arquivos brutos e dos scripts. Elas **não são saída de
pipeline** e, pela regra de proveniência do projeto, nenhuma delas pode entrar
em slide, artigo ou relatório antes de ser produzida por script versionado com
saída em `output/`. Aqui elas servem só para demonstrar o defeito.

---

## 1. Quadro-resumo

| # | Item | Tipo | Toca estimativa? |
|---|---|:---:|:---:|
| **F1** | A pergunta declarada e o único resultado causal falam de objetos diferentes | F | não |
| **F2** | A bolsa entra na teoria como salário puro; o pacote formativo e a margem de 20 h ficam fora | F | não |
| **F3** | `macro_regiao_saude` não é macrorregião de saúde — é grande região do IBGE | F/D | não |
| **F4** | Geografia vem do arquivo do programa, não da malha: 531 de 5.565 municípios | F | **sim** |
| **F5** | A unidade regional do serviço não entra na análise nem na narrativa | F | não (abre teste novo) |
| **D1** | "1.295 vagas" são 1.295 células CNES–curso; as vagas imediatas são 678 | D | não |
| **D2** | A manchete do README é o desfecho quase mecânico | D | não |
| **P1** | A5 não é reexecutável e o manifesto perde insumo em silêncio | P | sim, quando desbloquear |
| **P2** | Arquivo bruto com extensão errada | P | não |

---

## 2. F1 · A pergunta declarada e o único resultado causal falam de objetos diferentes

**Este é o item mais grave da lista.**

**O que está escrito.** A pergunta canônica, em
[`01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md`](../01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md),
§1: *"Bolsa maior compensa município pior?"*, lida como *"um degrau de R$ 5 mil
na bolsa-formação é suficiente para vencer a desvantagem territorial de um
município mais vulnerável?"*. O slide 9 da banca 1 repete: *"Maiores bolsas do
PMM-E para municípios mais vulneráveis compensam suas desvantagens territoriais
na atração de médicos especialistas?"*.

**O que é o caso.** O estimando dessa pergunta dependia da RDD da bolsa, que
está arquivada: `RDD-IVS` = `ARQUIVADO_ESCORE_NAO_OBSERVADO` em
[`33_status_execucao_plano_causal.md`](33_status_execucao_plano_causal.md). O
único resultado causal vigente é o A8, e ele responde a outra pergunta: *ganhar
marginalmente a vaga de primeira opção aumenta a homologação e a presença
posterior naquele curso–CNES?*

O próprio relatório do A8 (`output/tema_trabalho/A8_relatorio_cutoff_escore.md`,
§6) delimita o alcance sem ambiguidade:

> O desenho **não identifica** o efeito da bolsa, do IVS, do programa sobre o
> estoque geral, da vulnerabilidade ou sobre a decisão de se candidatar.

**Consequência.** O trabalho curto tem título e pergunta sobre compensação
territorial e um núcleo causal sobre conversão de alocação em presença. São
objetos distintos: o A8 mede o que acontece **depois** que a vaga foi alocada, a
pergunta canônica trata do que leva alguém a querer a vaga. Nenhum leitor
cuidadoso aceita o encaixe, e o `CLAUDE.md` é explícito nos dois sentidos —
começar pelo outcome e pelo estimando, e registrar a mudança de escopo quando o
desenho muda.

**Correção proposta.** Escolher explicitamente uma rota. Não há terceira:

- **Rota A — a pergunta passa a ser a que o A8 responde.** Objeto: a conversão
  entre alocação administrativa e presença efetiva. A vaga ofertada não é
  provimento; o que o dado mostra é quanto da alocação vira médico presente, e
  a distância entre homologar e continuar ativo. O gradiente territorial (A4)
  vira motivação descritiva, e o título muda junto.
- **Rota B — a pergunta territorial fica, e o A8 desce a mecanismo.** O trabalho
  assume-se descritivo sobre a compensação territorial, com o A8 no apêndice
  como evidência de que a margem de aceitação existe e é grande.

A Rota A é a que o material sustenta hoje. A Rota B é honesta, mas entrega um
trabalho sem núcleo causal.

**Custo.** Reescrita de pergunta, título e abertura; nenhuma reestimação.

---

## 3. F2 · A bolsa entra na teoria como salário puro

**O que está escrito.** Em
[`02_teoria/modelo_micro.md`](../02_teoria/modelo_micro.md), §3, a bolsa entra
na utilidade como renda: `V = Σδᵗ[E(w | B_m(IVS_m))/p − c] + ε`. O slide 7 abre
com *"o programa aposta que dinheiro compensa lugar ruim"*.

**O que é o caso.** O PMM-E é regulado como **integração ensino-serviço**
(Portaria GM/MS nº 7.177/2025), com quatro objetivos declarados — provimento,
fixação, equilíbrio territorial e **formação** — conforme já registrado em
[`auditorias/01_regra_institucional.md`](../auditorias/01_regra_institucional.md),
§3. O participante recebe **bolsa-formação**, sem vínculo, num aprimoramento em
serviço de até 12 meses e 20 horas semanais, com supervisão e mentoria de
instituição formadora. A aposta do desenho é dinheiro **mais** título,
supervisão e rede — não dinheiro sozinho.

Precisão que vale segurar: o PMM-E **não forma especialista**. Exige RQE na área
da vaga. É aprimoramento de quem já é especialista, ao contrário do braço de
residência do Agora Tem Especialistas. Nenhum documento do repositório afirma o
contrário; o ponto entra aqui para não se perder.

**Consequências, em ordem de gravidade:**

1. **A margem de decisão pode não ser locacional.** Vinte horas semanais, doze
   meses, sem vínculo: o médico não abandona a renda que tem. A decisão pode ser
   *acrescentar uma atividade*, não migrar. O modelo canônico é de escolha de
   localidade e a literatura transportada é de emprego integral — Dal Bó, Finan
   & Rossi com concurso real, Scott et al. com renda total. Se a margem é outra,
   as elasticidades não são comparáveis e "provimento duradouro" não significa o
   que o título sugere. O slide 7 trata isso como ajuste de percentual
   (*"a bolsa do PMM-E remunera 20 horas semanais"*), quando é mudança de objeto.
2. **A leitura de nível fica sem apoio.** Preenchimento, gradiente territorial e
   o próprio A8 medem procura pelo **pacote inteiro**. Nenhum deles isola
   dinheiro.
3. **Para o RDD dos R$ 5 mil, é inofensivo** — e é bom dizer isso em voz alta. O
   pacote é constante nos dois lados do cutoff, como
   [`auditorias/01_regra_institucional.md`](../auditorias/01_regra_institucional.md),
   §7, já registra. O argumento existe; falta estar no modelo.

**Correção proposta.** Decompor o retorno do posto em componente pecuniário
(`B_m`, descontínuo na regra) e componente formativo (`F`, uniforme por edital),
declarar que o desenho identifica a derivada em relação ao primeiro com o
segundo fixo, e registrar a margem 20 h / sem vínculo como limite de
transportabilidade da literatura.

**Aviso sobre material arquivado.** `90_arquivo_historico/15` e `16` carregam um
"+34% de adesão para bolsa com especialização" que sustentaria exatamente esta
tese. Está no arquivo histórico, com precisão suspeita e sem citação
rastreável. **Não importar sem conferir a fonte primária.**

---

## 4. F3 · `macro_regiao_saude` não é macrorregião de saúde

**O que está escrito.** O docstring de
`scripts/aquisicao/04_harmonizar_territorio_ibge.py` diz que o script integra
"a estrutura de Regiões de Saúde (CIR) e **Macrorregiões do SUS**". O texto que
o `05_estimar_atracao.py` **grava no relatório** (linhas 190, 1267, 1522, 1557)
descreve a especificação primária como "UF com <5 clusters colapsada na
macrorregião de saúde". O mesmo termo está em
[`35_plano_correcoes_pos_auditoria.md`](35_plano_correcoes_pos_auditoria.md),
§§ das linhas 39 e 202, e em todo o
[`36_backlog_pos_auditoria.md`](36_backlog_pos_auditoria.md).

**O que é o caso.** A variável é preenchida na linha 99 daquele script a partir
da coluna `regiao` de `data/pmm_especialistas_serie_historica.csv`. Os valores
distintos dessa coluna são cinco: `NORDESTE`, `SUDESTE`, `NORTE`,
`CENTRO-OESTE`, `SUL`. É a **grande região do IBGE**. Os níveis de efeito fixo
gravados em `output/` confirmam: `MACRO_NORTE`, `MACRO_NORDESTE`,
`MACRO_SUDESTE`, `MACRO_CENTRO` e `MACRO_SEM_REGIAO_SAUDE`.

Macrorregião de saúde do SUS é outra coisa: entidade intraestadual, desenhada
justamente para organizar média e alta complexidade — que é o objeto deste
trabalho. A região de saúde verdadeira existe no mesmo arquivo, em outra coluna
(`regiao_saude`, 352 valores distintos), e não é usada no efeito fixo.

**Consequência.** A operação é legítima — colapsar UF com poucos clusters na sua
grande região é defensável e foi o que o protocolo A3 quis dizer com "colapsar
em região". O **nome** é que está errado, em oito lugares, inclusive no texto
que sai impresso no relatório. É o tipo de coisa que uma banca pega em trinta
segundos e que contamina a confiança no resto.

**Correção proposta.** Renomear a variável para `grande_regiao`, corrigir o
docstring e as quatro cadeias de texto do `05_estimar_atracao.py`, corrigir os
documentos 35 e 36, e abrir errata em
[`auditorias/14_erratas_artefatos_congelados.md`](../auditorias/14_erratas_artefatos_congelados.md).
**Nenhum coeficiente muda.**

---

## 5. F4 · Geografia vem do arquivo do programa, não da malha

**O que é o caso.** O mapa de regiões é montado a partir de
`pmm_especialistas_serie_historica.csv` e `pmm_especialistas_nominal.csv` — dois
arquivos do **programa**. Municípios ausentes deles ficam com string vazia.
Conferência direta:

| Conferência | Valor |
|---|---:|
| municípios na malha (IVS 2010) | 5.565 |
| municípios com região atribuída | 531 |
| **municípios sem região** | **5.034** |

A grande região é derivável da UF para os 5.565. A região de saúde vem da malha
pública do DATASUS/IBGE, que o repositório não versiona.

**Consequências:**

1. O balde residual `MACRO_SEM_REGIAO_SAUDE` — que é o **item A-1 em aberto** do
   backlog — é artefato de fonte, não dado faltante. Isso muda a natureza da
   decisão pendente: não é escolher entre 23 e 24 níveis de efeito fixo, é
   consertar de onde vem a variável.
2. Sem região de saúde na malha completa, **não há como testar deslocamento
   intrarregional** — exatamente o teste que o red team registra como não feito
   em [`auditorias/09_red_team_atracao_provimento.md`](../auditorias/09_red_team_atracao_provimento.md),
   §"honestidade de escopo", e que o `CLAUDE.md` exige para separar expansão
   líquida de remanejamento.

**Armadilha de ordem.** Corrigir a fonte muda quem cai em qual nível de efeito
fixo, e os dois coeficientes candidatos **já estão publicados** no backlog:
+0,5062 com 24 níveis e +0,5014 com 23. Portanto a correção só pode entrar como
conserto de defeito de proveniência, declarada antes de rodar, com o motivo
sendo a cobertura de 531/5.565 — nunca o valor do coeficiente.

**Correção proposta.** Trazer grande região e região de saúde de fonte
territorial versionada cobrindo os 5.565 municípios, com manifesto e hash; só
então reexecutar, e registrar o resultado qualquer que seja.

---

## 6. F5 · A unidade regional do serviço não entra na análise

**O que está escrito.** A vaga é tratada como um CNES num município, e o slide 6
mede retaguarda profissional como **colegas da mesma especialidade no
município**, concluindo que *"onde a bolsa é maior, o médico fica sozinho"*.

**O que é o caso.** A parte administrativa está certa: o quadro de vagas publica
`CURSO · REGIÃO · UF · IBGE · MUNICÍPIO · CNES · ESTABELECIMENTO · GESTÃO ·
FAIXA DE ATRAÇÃO`. Mas o serviço é, em boa parte, regional. Conferência no
quadro do ciclo 1:

| Conferência | Valor |
|---|---:|
| células CNES–curso | 1.295 |
| células em estabelecimento de gestão estadual (incl. estadual/municipal) | 552 — **42,6%** |
| CNES distintos com "REGIONAL" no nome | 93 de 460 |
| células nesses estabelecimentos | 339 — **26,2%** |

Os dois primeiros registros do arquivo são "SES AP HOSPITAL ESTADUAL DE
OIAPOQUE" e "HOSPITAL REGIONAL DE ARIQUEMES". E a priorização federal pesa
explicitamente **escala regional e fluxo de usuários** (Edital 02/2025, itens
3.8–3.10, já em `auditorias/01_regra_institucional.md`, §5).

**Consequências:**

1. **Fronteira errada na medida de isolamento.** Para um hospital regional, a
   retaguarda relevante é a do estabelecimento e da região, não a do município.
   A medida não é falsa — a frase do slide é que é mais forte que ela.
2. **Descasamento entre incentivo e população atendida.** A bolsa é fixada pelo
   IVS do município-sede; a clientela é a da região. **Isto não é erro nosso** —
   é uma propriedade do desenho da política, e é um bom argumento a fazer,
   explicitamente, em vez de passar batido.
3. **Efeito local pode ser deslocamento.** Ganho no município-sede pode ser
   perda no vizinho da mesma região. Ver F4, consequência 2: o teste está
   bloqueado por falta da malha.

**Correção proposta.** Dizer no slide 6 que a medida é municipal e por quê;
registrar a versão por região de saúde como robustez pendente; transformar o
descasamento incentivo × clientela em parágrafo próprio da motivação; e listar o
deslocamento intrarregional como limitação declarada da banca 1.

---

## 7. D1 · "1.295 vagas" são 1.295 células

**O que está escrito.** Slide 4: *"**1.295 vagas** estabelecimento–curso em 460
estabelecimentos e 368 municípios"*. Slide 8: *"Das **1.295 vagas** da primeira
chamada, **30%** tiveram alguém confirmado ou homologado"*.

**O que é o caso.** Conferência no quadro bruto do ciclo 1:

| Conferência | Valor |
|---|---:|
| células CNES–curso | 1.295 |
| **vagas imediatas** | **678** |
| vagas de cadastro de reserva | 1.145 |
| células com ao menos uma vaga imediata | 513 |
| células apenas com cadastro de reserva | 782 |

O 678 confere com o README, que já usa o número certo ("593 das 678 vagas
imediatas" fora das capitais). O problema está nos slides.

**Consequência.** No slide 8 o rótulo contradiz a própria auditoria: o portão A1
foi concluído como `APROVADO_CELULA` justamente porque **não há denominador por
vaga**, e a análise usa "alguma confirmação/homologação por célula". Chamar
célula de vaga reintroduz, na frase, o denominador que a auditoria rejeitou. E
agrava: 782 das 1.295 células não tinham vaga imediata nenhuma.

**Conferido e limpo.** A composição imediata × reserva é equilibrada entre
faixas — 37,8%, 41,1% e 39,3% das células da Faixa 1, 2 e 3 têm vaga imediata —
então a comparação por faixa do slide 8 **não** está mecanicamente confundida
por isso. **Corrigir a palavra, não o número.**

---

## 8. D2 · A manchete do README é o desfecho quase mecânico

O box "Decisão atual" do `README.md` lidera com **63,9 p.p.** em homologação. O
relatório do A8, §2, diz que esse desfecho "mede conversão administrativa
imediata e está próximo da própria elegibilidade criada pela alocação", e que
"o resultado substantivamente mais informativo é o segundo": presença ativa,
**33,3 p.p.**

**Correção proposta.** Inverter a ordem no README e no resumo, e rotular o 63,9
como conversão administrativa. O A8 já faz isso internamente; quem lê só a capa
não vê.

---

## 9. P1 · A cadeia de proveniência de A5 está quebrada

Já catalogado como **D-4** no backlog, mas pertence a esta lista porque é
estrutural: **A5 não é reexecutável neste ambiente** — os microdados do CNES não
estão versionados. Dois efeitos registrados no próprio backlog:

- `07_red_team_sintese.py` **remove em silêncio** a entrada de
  `painel_municipio_curso_mensal.parquet` do manifesto de hashes quando o
  arquivo não existe, empobrecendo a auditoria sem avisar;
- uma correção barata de JSON foi **tentada e revertida** porque mudar o hash de
  `portao_denominador.json` quebra a cadeia fixada em A3, A4 e A5, e A5 não pode
  ser regravado.

Ou seja: há resultado publicado no apêndice que não pode ser reproduzido no
ambiente documentado, e o gerador de manifesto degrada silenciosamente. O
mínimo, independente do desbloqueio, é o gerador **distinguir insumo ausente de
insumo inexistente no desenho**, gravando a ausência com motivo.

## 10. P2 · Arquivo bruto com extensão errada

`data/raw/aquisicao/ivs_regra/edital_sgtes_02_2025_gestores.html` é um PDF —
começa com `%PDF-1.4`. Renomear e corrigir o manifesto. O conteúdo está
preservado; só o rótulo engana quem for ler.

---

## 11. Itens já catalogados que esta proposta não substitui

Esta proposta é sobre premissas e rótulos. O backlog pós-auditoria continua
valendo integralmente, e dois itens dele são de gravidade comparável:

- **A-1** — definição do efeito fixo para as células sem região publicada. Ver
  F4: a proposta muda a natureza do item, de escolha para conserto.
- **A-2** — o wild cluster bootstrap que o protocolo A3 exige e que nunca foi
  computado. `G = 368` é nominal; o `G` efetivo do estrato metropolitano é ≈ 32
  e o de capital é 18. Enquanto não rodar, os erros-padrão de A4 estão
  subestimados onde mais importa.

---

## 12. Sequência proposta

**Onda 1 — nada toca estimativa.** F3 (renomear), D1 (rótulo dos slides), D2
(manchete), P2 (extensão), mais o parágrafo de F2 no modelo e a limitação de F5.
Tudo isso é texto e nome; sai num commit, com errata e registro de mudanças.

**Onda 2 — decisão do autor, sem código.** F1: escolher Rota A ou Rota B. Tudo
que vier depois depende dessa escolha, inclusive título e resumo.

**Onda 3 — toca insumo, com declaração prévia.** F4 (malha territorial
versionada) e, junto dela, a correção do JSON presa em P1. Só depois A-1 se
resolve sozinho e o teste de deslocamento de F5 fica possível.

**Onda 4 — inferência.** A-2, o bootstrap que falta.

---

## 13. O que foi conferido e está certo

Para não virar dúvida depois:

- o `co_cnes` vazio na série histórica está corretamente documentado no
  inventário — conferido: 0 de 7.276 linhas. O cadastro nominal, esse, tem CNES
  em todas as 1.480 linhas;
- os totais do ciclo 1 no README — 678 vagas imediatas, 593 fora das capitais,
  350 municípios — conferem com o arquivo bruto;
- a composição imediata × reserva entre faixas é equilibrada (D1);
- o relatório do A8 delimita seu próprio alcance corretamente; o problema de F1
  está na capa e na pergunta, não no relatório;
- a leitura institucional de `auditorias/01` está correta e bem citada,
  inclusive o ponto de que o pacote formativo é constante no cutoff.

---

## 14. Decisões que dependem do autor

1. **F1: Rota A ou Rota B.** Sem isso, o resto da reescrita não tem direção.
2. **F4: quando declarar a correção de fonte**, sabendo que os dois coeficientes
   candidatos já são públicos no backlog.
3. **F5: o descasamento incentivo × clientela entra como argumento da motivação
   ou como limitação?** As duas são defensáveis; a primeira é mais interessante
   e exige assumir que o trabalho fala de política, não só de estimativa.
