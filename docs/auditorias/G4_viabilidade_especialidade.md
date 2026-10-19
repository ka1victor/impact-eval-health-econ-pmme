# G4 — Mapa curso → procedimentos e viabilidade da produção por especialidade

> **Data:** 19/10/2026.<br>
> **Tarefa:** portão G4 do plano das perguntas reformuladas
> ([`06_execucao/51`](../06_execucao/51_plano_perguntas_reformuladas.md), P3,
> T3.2). Bloqueia o T3.2 (produção da especialidade que chegou).<br>
> **Script:** [`scripts/aquisicao/g4_mapa_especialidade_procedimento.py`](../../scripts/aquisicao/g4_mapa_especialidade_procedimento.py).<br>
> **Números:** todos estão em
> [`output/rdd_bolsa/G4_resumo.json`](../../output/rdd_bolsa/G4_resumo.json), no
> mapa [`G4_mapa_especialidade_procedimento.csv`](../../output/rdd_bolsa/G4_mapa_especialidade_procedimento.csv)
> (curso × forma de organização) e em
> [`G4_mapa_especialidade_subgrupo.csv`](../../output/rdd_bolsa/G4_mapa_especialidade_subgrupo.csv).
> Os blocos marcados abaixo são conferidos contra o resumo por
> `tests/test_g4_mapa_especialidade.py`.<br>
> **Cegamento:** é um portão. Nada foi calculado por IVS, faixa da bolsa, lado de
> corte, tratamento ou chegada; o IVS não é lido. Os únicos números vistos são
> totais nacionais.

## 1. Veredito

<!-- G4:veredito -->
**VIAVEL_PARCIAL.**

- **O filtro funciona.** O TabNet do SIA cruza a forma de organização (coluna)
  com o filtro de CBO do profissional, por município e mês. No teste de um mês
  (202406, CBO-alvo do PMM-E):
  - a consulta municipal trouxe todos os municípios do formulário;
  - o total de cada forma é igual ao da consulta nacional por CBO;
  - a soma das formas por subgrupo reproduz o a12, célula a célula.
- **Falta a fonte normativa pedida.** A compatibilidade procedimento × CBO do
  SIGTAP (`rl_procedimento_ocupacao`) não pôde ser obtida nesta execução (seção
  2). O mapa foi montado com a produção ambulatorial aprovada de 2024. Ele é
  **revelado** (o que as CBO de fato registram no SUS), não **normativo** (o
  que a regra permite).
- **O lado hospitalar não tem especialidade.** O TabNet do SIH não oferece CBO.
  Cirurgias e anestesias em AIH não se atribuem ao especialista.
<!-- /G4:veredito -->

## 2. SIGTAP: o que foi tentado

O script tentou a fonte oficial, em três vias. Cada resposta ficou registrada
em [`output/aquisicao/sigtap/sigtap_sondagem.json`](../../output/aquisicao/sigtap/sigtap_sondagem.json),
com URL, data e hora, status e SHA-256.

| Via | URL | Resultado em 19/10/2026 |
|---|---|---|
| Página de download | `http://sigtap.datasus.gov.br/tabela-unificada/app/download.jsp` | responde 200 com "Caro usuário, no momento o serviço de downloads encontra-se indisponível." |
| RSS de competências | `http://sigtap.datasus.gov.br/tabela-unificada/competencias.rss` | responde e dá o nome oficial do ZIP da competência 12/2024: `TabelaUnificada_202412_v2501172121.zip` |
| FTP oficial | `ftp://ftp2.datasus.gov.br/pub/sistemas/tup/downloads/` | conexão esgota o tempo: a porta 21 não é alcançável deste ambiente; o mesmo host por HTTP e HTTPS também não responde |

Também foram tentados, à mão:
- o serviço SOAP do SIGTAP (`servicos.saude.gov.br`): a conexão HTTPS foi
  encerrada sem resposta no túnel de saída deste ambiente;
- a consulta por procedimento no aplicativo web do SIGTAP: mostra as CBO de um
  procedimento por vez, em navegação JSF instável. Raspar milhares de páginas
  não é uma aquisição reprodutível.

Nenhuma cópia não oficial foi usada.

A coluna `compatibilidade_sigtap` do mapa vale `NAO_OBTIDA` em todas as linhas.
Quando o FTP estiver acessível, `--etapa tudo` baixa o ZIP pelo nome do RSS, lê
a tabela pelo layout que vem no próprio ZIP (leitor testado com um ZIP
sintético) e preenche a coluna, sem mudar o resto do mapa.

## 3. O mapa revelado

**Fonte.** TabNet do SIA, "Produção Ambulatorial do SUS - Brasil - por local de
atendimento" (`sia/cnv/qabr.def`), o mesmo formulário do a12. Duas consultas
nacionais, cada uma somando os 12 meses de processamento de 2024 (antes das
chegadas do PMM-E):

| Consulta | Linha | Coluna | Filtro | Uso |
|---|---|---|---|---|
| `nac_cbo_medica_forma_2024` | Profissional - CBO | Forma organização | todas as CBO médicas (2251, 2252, 2253, 2231) | produção de cada CBO por forma |
| `nac_forma_todos_2024` | Forma organização | — | nenhum | produção de todos os profissionais por forma |

**Construção.** Curso → CBO pela ponte curso–CBO
([`output/aquisicao/ponte_curso_cbo_oficial.json`](../../output/aquisicao/ponte_curso_cbo_oficial.json)).
Para cada curso e forma, a tabela traz:
- a quantidade aprovada das CBO do curso;
- a participação dessa forma na produção do curso, e a participação acumulada;
- `tipica`: a forma está entre as que somam os primeiros 80% da produção do
  curso, em ordem decrescente (a forma que cruza o limiar entra);
- a especificidade: a quantidade das CBO do curso dividida pela produção médica
  da forma. Alta ≥ 0,50; média ≥ 0,20; baixa abaixo disso. A mesma razão contra
  todos os profissionais também está na tabela.

Esses limiares foram fixados no script antes de ler as respostas.

**Classe do curso** (descritiva):
- `ESPECIFICO`: ≥ 20% da produção das CBO do curso está em formas de
  especificidade alta;
- `PARCIAL`: o limiar só é atingido somando as formas de especificidade média;
- `GENERICO`: nos demais casos.

Esse limiar foi fixado depois de ver o mapa nacional, sem IVS nem outcome. A
escolha final dos outcomes por especialidade é do adendo §12 do protocolo 47.

<!-- G4:classes -->
| Classe | Cursos (código da ponte) |
|---|---|
| ESPECIFICO | 7, 10, 11, 12, 13, 14, 15, 16 |
| PARCIAL | 4, 9 |
| GENERICO | 1, 2, 3, 5, 6, 8 |
<!-- /G4:classes -->

**Leitura.**
- **Exames e terapias ambulatoriais têm assinatura própria.** É o caso de:
  - endoscopia e colonoscopia: forma 020901, aparelho digestivo;
  - oncologia clínica: quimioterapia, 0304;
  - radioterapia: 030401;
  - anatomia patológica: 020301 e 020302;
  - otorrinolaringologia: 021107, 020904 e 040401;
  - radiologia: ultrassonografia, raios X, tomografia e ressonância.

  Nesses cursos, a produção da especialidade é separável no SIA por forma e CBO.
- **Os cursos cirúrgicos e a anestesiologia são `GENERICO` no SIA.** Isso vale
  para cirurgia geral, oncológica, do aparelho digestivo e ginecológica, e para
  a anestesiologia. A produção ambulatorial dessas CBO é sobretudo consulta
  (030101), atendimento de urgência (030106) e pequenas cirurgias. O que as
  distingue (cirurgias e anestesias) está na AIH, e o TabNet do SIH não tem CBO.
  Para esses cursos, o caminho por especialidade no SUS exige outra fonte: a
  AIH com os profissionais (SP do SIH em microdado) ou a compatibilidade do
  SIGTAP aplicada aos procedimentos da AIH por subgrupo, por exemplo 0407 para o
  aparelho digestivo.
- **A consulta médica (030101) é típica de quase todos os cursos.** A
  especificidade dela é baixa, e ela não separa especialidades.
- **A CBO é mais larga que o curso.**
  - O curso 14 (ultrassonografia mamária) herda toda a radiologia da CBO 225320.
  - O curso 9 (ecocardiografia) herda toda a cardiologia.
  - O curso 8 (colposcopia) herda toda a ginecologia e obstetrícia.

  O mapa mede a especialidade da CBO, não o conteúdo do curso.
- **Cursos com a mesma CBO não se distinguem:**
  - 6 e 8;
  - 10 e 11;
  - o 7 compartilha CBO com o 4, o 10 e o 11.

  A lista está em `por_curso[].cursos_que_compartilham_alguma_cbo` no resumo.

## 4. Viabilidade do filtro no TabNet

| Pergunta | Resposta |
|---|---|
| Forma de organização × filtro de CBO, por município e mês? | sim; teste de 202406 aprovado (seção 1) |
| Procedimento × município? | não numa só consulta. "Procedimento" só existe como linha ou filtro; o nível mais fino que cruza com município é a forma de organização |
| Município × CBO? | não numa só consulta. "Profissional - CBO" só existe como linha ou filtro; cada consulta municipal cobre um conjunto de CBO |
| Custo de uma aquisição completa | uma consulta por mês e por conjunto de CBO: 55 meses × 14 conjuntos distintos de CBO dos cursos (ou × 17 CBO, 935 consultas, se por CBO). A resposta do teste tem cerca de 1,7 MB e levou segundos; estimativas em `custo_estimado_aquisicao` no resumo |

O teste guarda em `output/` só totais nacionais
([`g4_teste_filtro_totais_nacionais.csv`](../../output/aquisicao/sigtap/g4_teste_filtro_totais_nacionais.csv)).
As respostas municipais ficam no cache, fora do controle de versão.

## 5. Saídas

| Arquivo | Conteúdo |
|---|---|
| `output/rdd_bolsa/G4_mapa_especialidade_procedimento.csv` | curso × forma de organização: quantidades, participações, típica, especificidade, compatibilidade SIGTAP (`NAO_OBTIDA`) |
| `output/rdd_bolsa/G4_mapa_especialidade_subgrupo.csv` | o mesmo, agregado a subgrupo |
| `output/rdd_bolsa/G4_resumo.json` | veredito, sondagem do SIGTAP, regras, cobertura, resumo por curso, teste do filtro, custo e limites |
| `output/aquisicao/sigtap/g4_sia_nacional_cbo_forma_2024.csv` | CBO médica × forma, nacional, 2024 |
| `output/aquisicao/sigtap/g4_sia_nacional_forma_2024.csv` | forma: produção médica e de todos, nacional, 2024 |
| `output/aquisicao/sigtap/g4_teste_filtro_totais_nacionais.csv` | teste de 202406: total por forma nas consultas municipal e por CBO |
| `output/aquisicao/sigtap/sigtap_sondagem.json` | tentativas de obter o SIGTAP |
| `output/aquisicao/sigtap/manifesto_g4.json` | entradas (ponte, a12) com SHA-256; para cada consulta: URL, corpo do POST, data e hora, SHA-256 e tamanho; SHA-256 de cada saída |
| `output/aquisicao/sigtap/cache/` | formulário, respostas e páginas brutas (fora do controle de versão) |

Todas as saídas têm `natureza_dos_dados = EMPIRICO`.

## 6. Limites

- Mapa revelado, não normativo: uma CBO que registra pouco no SIA parece pouco
  específica, mesmo que a regra lhe reserve procedimentos.
- A CBO é a informada pelo prestador. A produção sem CBO na tabela do TabNet
  fica fora de "médicos" e entra só em "todos".
- O grupo 09 (OCI) começa em 2025 e não aparece na janela de 2024. Se a
  especialidade migrou para OCI depois, o mapa de 2024 não a vê.
- Quantidade aprovada não é paciente: um laudo de anatomia patológica e uma
  sessão de quimioterapia contam igual.

## 7. Reprodução

```bash
python3 scripts/aquisicao/g4_mapa_especialidade_procedimento.py                   # verificar (sem rede, não grava)
python3 scripts/aquisicao/g4_mapa_especialidade_procedimento.py --etapa tudo      # sonda o SIGTAP, baixa e consolida
python3 scripts/aquisicao/g4_mapa_especialidade_procedimento.py --etapa consolidar
python3 -m pytest tests/test_g4_mapa_especialidade.py
```

O G4 não entra no `run_all.py`: é um portão de viabilidade, sem etapa
dependente no pipeline. O protocolo da onda 2 (adendo §12 do protocolo 47)
decide se a aquisição completa por especialidade entra.
