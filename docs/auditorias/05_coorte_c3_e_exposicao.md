# Auditoria da Coorte e Exposicao do Ciclo 3 (PMM-E)

> **Data de Congelamento:** 2026-08-30  
> **Status:** Protocolo Pre-Tratamento Congelado (C3-01 Concluido)  
> **Arquivo Analitico:** `output/avaliacao_ciclo3/coorte_c3_congelada.parquet`

---

## 1. Resumo Executivo e Contraste Causal

O terceiro ciclo do PMM-E oferece uma oportunidade impar de avaliacao causal comparativa por Intencao de Tratar (ITT). Ao contrario do Ciclo 1 — onde tanto as vagas imediatas quanto as de reserva receberam alocacoes —, o processo de adesao do Ciclo 3 gerou uma separacao nitida entre propostas que foram contempladas com prioridade imediata e propostas de gestores que **nao foram priorizadas** pelo Ministerio da Saude.

### Unidades e Contagens Oficiais Congeladas
- **Total de Propostas Auditadas (CNES–curso):** 5,534
- **Vagas Imediatas Puras (Tratamento Principal):** 451 celulas
- **Propostas Nao Priorizadas Puras (Controle Principal):** 3241 celulas
- **Cadastro de Reserva Puro:** 1595 celulas (excluido do contraste confirmatorio)
- **Celulas Mistas (Imediata + Reserva):** 247 celulas (excluidas do contraste confirmatorio)

### Primeiro Estagio Administrativo
- **Vagas Imediatas Ofertadas no Braco Imediato Puro:** 882
- **Medicos Bolsistas Alocados Confirmados:** 396
- **Taxa de Alocacao Publica Efetiva:** 44.90%

---

## 2. Ponte Normativa CBO — Nota Tecnica no 59/2026

A harmonizacao ocupacional foi reconstruida a partir do **Anexo I da Nota Tecnica no 59/2026-CGPLAD/DEGEPS/SGTES/MS**, eliminando a dependencia de correspondencias locais informais.

### Familia Confirmatoria Univoca (Sem Sobreposicao)
Dos 24 cursos do ciclo, **15 cursos possuem suporte em ambos os bracos** (imediata e nao priorizada). Dentre eles, destacam-se os cursos com correspondencia 1:1 estrita:
1. **01. Anestesiologia Perioperatoria e Sedacao Segura:** 119 imediatas vs. 305 controles (CBO 225151)
2. **02. Cirurgia Geral Minimamente Invasiva:** 33 imediatas vs. 337 controles (CBO 225225)
3. **12. Oncologia Clinica:** 12 imediatas vs. 39 controles (CBO 225121)
4. **13. Radioterapia:** 7 imediatas vs. 21 controles (CBO 225330)
5. **14. Ultrassonografia Mamaria:** 13 imediatas vs. 774 controles (CBO 225320)
6. **21. Cirurgia Mamaria Oncologica:** 7 imediatas vs. 30 controles (CBO 225260)
7. **24. Medicina Intensiva:** 6 imediatas vs. 83 controles (CBO 225112)

---

## 3. Modulo de Anestesiologia e Cirurgias (SIH)

### Suporte e Cointervencoes
- **Total de CNES com Anestesiologia Imediata:** 119 estabelecimentos em 78 municipios.
- **Vagas Imediatas de Anestesiologia:** 290 vagas (133 alocados, taxa de ocupacao de 45,86%).
- **Controles Nao Priorizados de Anestesiologia:** 305 estabelecimentos em 247 municipios.
- **Anestesiologia Isolada (Sem outra vaga cirurgica simultanea no municipio):**
  - Tratados: 45 municipios
  - Controles: 187 municipios

---

## 4. Auditoria da Assinatura Cadastral do PMM-E no CNES

Validou-se no arquivo publico `tbCargaHorariaSus` que o Ministerio da Saude disponibiliza os campos necessarios para identificar os bolsistas do PMM-E:
- `IND_VINCULACAO = 070102` (Bolsa - Bolsista)
- `NU_CNPJ_DETALHAMENTO_VINCULO = 00394544012787` (Ministerio da Saude)
- Carga horaria semanal padronizada: 16h assistenciais + 4h formativas (total 20h).

Na competencia de julho de 2026, foram identificados 7.924 vinculos com a combinacao exata de bolsa federal no Brasil (incluindo participantes da atencao primaria e ciclos anteriores). Nas competencias posteriores a $T_0$, o cruzamento dessa assinatura com os CBOs do Anexo I permitira auditar o provimento e a rotatividade individual de forma publica e transparente.

---

## 5. Proximos Passos (Portao C3-02)

Com a coorte e as unidades congeladas no hash oficial, o proximo passo autorizado e:
- **C3-02:** Executar o piloto do SIH/SUS exclusivamente para as competencias pre-tratamento (2024-06 a $T_0-1$) para as UFs da coorte congelada, construindo os indicadores de AIHs cirurgicas eletivas.
