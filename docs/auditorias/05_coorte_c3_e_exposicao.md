# Auditoria da Coorte e Exposicao do Ciclo 3 (PMM-E)

> **Data de Congelamento:** 2026-08-30  
> **Status:** Protocolo Pre-Tratamento Congelado (C3-01 Concluido)  
> **Arquivo Analitico:** `output/avaliacao_ciclo3/coorte_c3_congelada.parquet`

---

## 1. Resumo executivo e contraste comparativo

O processo de adesao do terceiro ciclo gerou um contraste prospectivo plausivel por
intencao de tratar (ITT): celulas CNES--curso contempladas com vaga imediata pura
versus propostas de gestores nao priorizadas. A priorizacao **nao foi aleatoria**.
Logo, esta auditoria nao transforma o contraste em experimento; a interpretacao
causal depende de suporte comum, ausencia de antecipacao, pre-tendencias compativeis
e controle explicito de contaminacao e cointervencoes.

### Unidades e Contagens Oficiais Congeladas
- **Total de Propostas Auditadas (CNES–curso):** 5,534
- **Vagas Imediatas Puras (Tratamento Principal):** 451 celulas
- **Propostas Nao Priorizadas Puras (Controle Principal):** 3241 celulas
- **Cadastro de Reserva Puro:** 1595 celulas (excluido do contraste confirmatorio)
- **Celulas Mistas (Imediata + Reserva):** 247 celulas (excluidas do contraste confirmatorio)

### Primeiro estagio administrativo publicado
- **Vagas Imediatas Ofertadas no Braco Imediato Puro:** 882
- **Alocacoes publicadas:** 396
- **Razao alocacoes publicadas/vagas:** 44.90%

Essa razao nao prova inicio ou permanencia no exercicio. O primeiro estagio efetivo
sera medido prospectivamente no CNES.

---

## 2. Ponte Normativa CBO — Nota Tecnica no 59/2026

A harmonizacao ocupacional foi transcrita do **Anexo I, paginas 4--7, da Nota
Tecnica no 59/2026-CGPLAD/DEGEPS/SGTES/MS**. A fonte oficial e
<https://www.gov.br/saude/pt-br/centrais-de-conteudo/publicacoes/notas-tecnicas/2026/nota-tecnica-no-59-2026-cgplad-degeps-sgtes-ms.pdf>. O codigo calcula as sobreposicoes por intersecao dos CBOs
e os testes congelam a transcricao dos 24 cursos.

### Nucleo confirmatorio sem sobreposicao entre cursos

Dos 24 cursos, **15** possuem ao menos
uma celula em cada braco. Somente tres combinam esse suporte com uma ponte integral
sem CBO compartilhado:

1. **01. ANESTESIOLOGIA PERIOPERATORIA E SEDACAO SEGURA:** 119 imediatas vs. 305 controles (CBO 225151)
2. **12. ONCOLOGIA CLINICA: CANCERES PREVALENTES NO SUS:** 12 imediatas vs. 39 controles (CBO 225121)
3. **24. ROTINAS ASSISTENCIAIS EM MEDICINA INTENSIVA NO SUS:** 6 imediatas vs. 83 controles (CBO 225150)

O curso 2 nao e integralmente 1:1: a norma aceita `225225`, exclusivo no ciclo, e
`225220`, compartilhado com o curso 5. Ele fica como sensibilidade pre-especificada
no CBO exclusivo, nao como parte do nucleo confirmatorio. Cursos 13, 14 e 21 tambem
compartilham ao menos um CBO e nao podem ser apresentados como pontes 1:1.

---

## 3. Modulo de Anestesiologia e Cirurgias (SIH)

### Suporte e Cointervencoes
- **Total de CNES com Anestesiologia Imediata:** 119 estabelecimentos em 78 municipios.
- **Vagas Imediatas de Anestesiologia:** 290 vagas (133 alocados, taxa de ocupacao de 45,86%).
- **Controles Nao Priorizados de Anestesiologia:** 305 estabelecimentos em 247 municipios.
- **Anestesiologia Isolada (Sem outra vaga cirurgica simultanea no municipio):**
  - Tratados: 62 municipios
  - Controles: 218 municipios

---

## 4. Auditoria da Assinatura Cadastral do PMM-E no CNES

Validou-se no layout publico `tbCargaHorariaSus` a presenca dos campos necessarios
para construir uma assinatura operacional candidata do PMM-E:
- `IND_VINCULACAO = 070102` (Bolsa - Bolsista)
- `NU_CNPJ_DETALHAMENTO_VINCULO = 00394544012787` (Ministerio da Saude)
- Carga horaria semanal padronizada: 16h assistenciais + 4h formativas (total 20h).

Na competencia de julho de 2026, foram identificados 7.924 vinculos com a combinacao
exata de bolsa federal no Brasil, incluindo APS e ciclos anteriores. Portanto, a
assinatura isolada nao identifica o Ciclo 3. Nas competencias posteriores a $T_0$,
ela devera ser cruzada com a coorte CNES--curso, os CBOs normativos e a data de
entrada, com reconciliacao de excecoes. `CO_PROFISSIONAL_SUS` sera tratado como
identificador operacional cuja estabilidade longitudinal ainda precisa ser testada;
nao se presume algoritmo MD5 nem anonimato absoluto.

---

## 5. Proximos Passos (Portao C3-02)

Com a coorte corrigida e congelada, a sequencia e:

1. concluir o piloto SIH apenas no pre-tratamento e auditar cobertura, porte e
   definicao de cirurgias eletivas;
2. executar o torneio pre-tratamento sem consultar outcomes pos-tratamento;
3. validar prospectivamente $T_0$ pela entrada observada dos vinculos do Ciclo 3;
4. estimar aos seis meses e atualizar aos doze meses somente depois do amadurecimento.
