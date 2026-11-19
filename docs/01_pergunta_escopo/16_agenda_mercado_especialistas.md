# 16 — Próxima agenda: o mercado de médicos especialistas no Brasil

> **Estatuto:** proposta do autor de 19/11/2026 (PR #6), revista na integração à `main` no mesmo dia. **Não há
> protocolo nem execução**, e este documento não traz nenhum número novo. Os números do artigo de partida vêm de
> [`03_literatura_empirica/20`](../03_literatura_empirica/20_evidencia_empirica_hipotese_remuneracao_preenchimento.md),
> item C1, conferidos lá contra o manuscrito final.<br>
> **Relação com o PMM-E:** é uma pergunta nova e mais geral. Não depende dos resultados do PMM-E e não muda nenhum
> deles. Reaproveita a infraestrutura de dados do repositório.<br>
> **Primeiro passo:** um protocolo em `docs/06_execucao/`, congelado antes de qualquer resultado (seção 7).

## 1. Pergunta e estimandos

**Pergunta.** Onde os médicos especialistas trabalham no Brasil, como se movem entre municípios e o que pesa na escolha
do local: porte e infraestrutura do lugar, distância de onde já estavam, formação e, se houver fonte, remuneração. É a
pergunta de alocação, que vale fora de qualquer programa de provimento.

| Etapa | Estimando | Natureza |
|---|---|---|
| 1. Estoque | especialistas por 100 mil habitantes, por especialidade (CBO) × região de saúde × mês; concentração; vínculos e horas por profissional | descritivo |
| 2. Fluxos | taxas de entrada, de saída do cadastro e de mudança de município, por especialidade e região | descritivo |
| 3. Escolha | pesos dos atributos do local na escolha de quem entra num município novo, num logit condicional | preferência revelada sob a forma funcional do logit; não é efeito causal de política |
| 4. Extensões | elasticidade à remuneração, heterogeneidade (coeficientes aleatórios) e contrafactuais | só com instrumento e fonte de remuneração defensáveis |

## 2. O artigo de partida: Costa, Nunes & Sanches (2024)

*How to Attract Physicians to Underserved Areas? Policy Recommendations from a Structural Model*, *The Review of
Economics and Statistics* 106(1), 36–52 ([doi:10.1162/rest_a_01155](https://doi.org/10.1162/rest_a_01155)).

- **Amostra:** 46.989 **generalistas** formados entre 2001 e 2013. A variável é o local do primeiro emprego, nos três
  primeiros anos de carreira.
- **Alternativas:** 52, a região metropolitana ou o interior de cada UF.
- **Dados:** cadastro do CFM ligado à RAIS (2001–2015) e ao CNES (2005–2016).
- **Modelo:** logit de coeficientes aleatórios do lado da oferta, com a demanda de estabelecimentos privados. O salário
  é endógeno: entra por função de controle e é instrumentado pelos atributos médios de outros locais da mesma
  macrorregião.
- **Resultado:** elasticidade-salário de ≈ 0,4 nas metrópoles e ≈ 0,7 no interior. Origem e formação pesam mais que o
  salário, e cotas e vagas de medicina em áreas carentes custam menos que incentivo financeiro.

**O que a extensão muda:**

| | Artigo | Extensão proposta |
|---|---|---|
| População | generalistas recém-formados | especialistas, em qualquer ponto da carreira |
| Decisão | primeiro emprego | cada mudança de município observada |
| Fonte | CFM + RAIS identificada + CNES | só o CNES, que é público, mais bases municipais públicas |
| Alternativas | 52 (metrópole ou interior × UF) | as 52 do artigo, para comparar, e depois região de saúde |
| Salário | observado na RAIS e instrumentado | ausente no CNES; é extensão, com fonte a verificar |

Para especialistas, que são o gargalo, não há no repositório evidência comparável com dados brasileiros (doc 20,
seção C).

## 3. O que o CNES dá e o que não dá

| Dá, mês a mês | Não dá |
|---|---|
| vínculo profissional × estabelecimento × CBO | salário ou renda |
| município do estabelecimento (`CO_MUNICIPIO_GESTOR`, a chave do a09) | local de nascimento |
| horas ambulatoriais, hospitalares e outras; vínculo SUS e não SUS | escola médica e residência cursadas |
| código do profissional (`CO_PROFISSIONAL_SUS`) e registro do conselho | título de especialista (RQE): CBO é ocupação declarada |
| tipo de unidade, gestão e natureza jurídica do estabelecimento | presença efetiva, produção ou retenção |

A reprodução é **parcial** por isso. Ela começa pelo que o CNES sustenta e diz o que difere do artigo.

## 4. O que o repositório já tem e o que falta

| Peça | O que cobre | Limite para esta agenda |
|---|---|---|
| [`a09`](../../scripts/aquisicao/a09_adquirir_cnes_nacional.py): painel município × grupo de CBO × mês | os 5.565 municípios; trimestral em 2022–2024 e mensal de 202406 a 202608; grupos `generalistas`, `mfc_225130`, `especialistas_nao_alvo`, `alvo_pmme`, `todos_medicos` e a variante sem residentes | agregado, sem o profissional (não serve aos fluxos); grupos e não especialidade; os ZIPs são apagados depois da extração |
| [`a16`](../../scripts/aquisicao/a16_cnes_profissional_mensal.py): painel profissional × mês | vínculo, CBO, município e horas, com chave pseudônima; de 202406 a 202608 ([auditoria A16](../auditorias/aquisicao/A16_cnes_profissional.md)) | **só os médicos do PMM-E** ligados na X1. Para esta agenda, o filtro tem de passar a ser "todos os médicos" |
| [`datasus_dbc.py`](../../scripts/utils/datasus_dbc.py) | leitura dos `.dbc` do FTP do DATASUS | para séries longas, pelos arquivos por UF (PF, ST); acesso e cobertura a verificar |
| [`50_escolha_localizacao_par.py`](../../scripts/rdd_bolsa/50_escolha_localizacao_par.py) | logit condicional com efeito fixo, usado na banca final | é específico da escolha do PMM-E; serve de base para o estimador, não para ser reaproveitado sem mudanças |
| [Dossiê das bases](../04_dados/20_dossie_bases_dados_saude_brasil_pmme.md) | fontes públicas de saúde, com acesso e chaves | ponto de partida para população, leitos, escolas e residências |

**Falta:** um painel nacional profissional × mês com todos os médicos, numa janela longa o bastante para observar
mudanças de município. O a16 já resolve chave, horas e pseudonimização; a extensão é trocar o filtro e a janela, e
medir o volume (o a09 sozinho baixa cerca de 23 GB de ZIPs).

## 5. Etapas

1. **Estoque (descritivo).** Primeiro com o painel do a09, que já existe, nos grupos que ele tem; depois por
   especialidade, a partir da extração nova. Densidade por habitante, concentração, vínculos múltiplos, horas SUS e
   não SUS.
2. **Fluxos (descritivo).** Primeira aparição no CNES, mudança de município e saída do cadastro, com o painel nacional
   profissional × mês. Portão: estabilidade da chave e da gravação das competências (seção 6).
3. **Logit condicional** na versão mais simples do artigo. A população é quem entra num município novo. As
   alternativas seguem o estilo do artigo e, depois, a região de saúde. Os atributos são população, estabelecimentos,
   leitos e equipamentos no CNES, distância do local anterior e residência médica próxima. Conferir se sinais e ordens
   de grandeza dos atributos comuns batem com os do artigo. A comparação é qualitativa, porque população e decisão
   diferem.
4. **Extensões**, só depois de 1 a 3: remuneração, coeficientes aleatórios com instrumento como no artigo, e
   contrafactuais de política, rotulados como cenário e separados dos resultados empíricos.

## 6. Cuidados

- **Trava do ciclo 3.** O a09 e o a16 não baixam nem leem competência ≥ `202609`, pelo plano de pré-análise do ciclo
  3 do PMM-E. Um painel nacional depois dessa data mostraria, agregados, os desfechos do ciclo 3 antes da hora. Até a
  análise do ciclo 3 ser executada, esta agenda segue o mesmo limite, salvo decisão do autor registrada antes.
- **Quem é especialista.** No CNES, especialidade é a CBO declarada, não o título. O prefixo 2251 inclui os
  generalistas `225125`, `225142` (estratégia de saúde da família) e `225170`, que o a09 já separa. Medicina de família
  e comunidade (`225130`) fica em grupo próprio, e médico residente (`2231F9`) fica fora do estoque.
- **Vínculo não é presença.** Vínculo cadastrado não é presença, produção nem retenção. Um médico tem vários
  vínculos, então a contagem é de profissionais distintos, com as horas.
- **Chave do profissional.** Pelo portão G5, o `CO_PROFISSIONAL_SUS` é estável e o número do CRM gravado no vínculo
  muda para parte dos médicos. Nenhum nome ou CPF vai para `output/`.
- **Arquivo antigo não é foto do mês.** No CNES-HB, as competências de 2007 a 2015 foram regravadas em lote em
  04/06/2014 (achado do PR #5). Antes de usar "primeira aparição" como data, conferir a data de gravação das tabelas
  usadas.
- **IIA.** Na banca final, o logit aninhado rejeitou a IIA (λ = 0,45). O logit condicional da etapa 3 é a versão de
  partida, e não a especificação final.
- **Remuneração.** A RAIS pública cobre o emprego formal com CBO e município. A renda de especialista como pessoa
  jurídica ou autônomo fica de fora, então a cobertura tem de ser medida antes de usar.
- **Linguagem.** As etapas 1 e 2 são descritivas. A etapa 3 estima preferências sob um modelo, não o efeito de uma
  política.

## 7. Primeiro passo

Um protocolo da etapa 1 em `docs/06_execucao/` (número livre seguinte), congelado antes de olhar resultados. Ele fixa:

- a definição de especialista;
- a unidade geográfica;
- a janela, respeitando a trava do ciclo 3;
- as tabelas e as figuras.

O protocolo vem junto com um portão de viabilidade do painel nacional profissional × mês. O portão cobre volume, chave
e data de gravação, no molde do G5. Pela regra do repositório, a mudança de escopo entra em
[`00_registro_mudancas.md`](../00_registro_mudancas.md).
