# 52c. Adendo aos protocolos 52 e 52b e ao E9: tipo de vaga do ciclo 2 medido antes da alocação

> **Data de congelamento:** 26/10/2026, antes de reestimar.<br>
> **Estatuto:** `ADENDO_52C_CORRECAO_COVARIAVEL`. Toda saída leva
> `natureza_dos_dados = EMPIRICO`.<br>
> **Motivo:** a auditoria 36 mostrou que, no ciclo 2, o quadro de vagas usado
> (retificado de 19/03/2026) foi refeito depois do resultado preliminar: 630
> vagas de reserva viraram imediatas, quase todas em células que tinham recebido
> alocado. As covariáveis "tem vaga imediata" e "log(vagas imediatas + 1)" do
> logit da escolha (E9, M1–M9 do P1, P1h), no ciclo 2, são portanto **em parte
> resultado da própria escolha**. Controle pós-tratamento pode viesar o peso da
> bolsa e o da origem.

## 1. Correção

- No ciclo 2, "tem vaga imediata" e "log(vagas imediatas + 1)" passam a vir do
  **quadro de 13/02/2026** (vigente na inscrição). Ciclos 1 e 3 sem mudança.
- Reestimar com a correção:
  - E9 principal (ciclo 2 e empilhado);
  - P1 M1 (empilhado) e M5 (por ciclo);
  - P1h-1 (D_UF), com o portão de reprodução aplicado à versão **antiga** antes
    de trocar a covariável.
- Relatar a versão antiga e a corrigida lado a lado, para todas as linhas.

## 2. Leitura

**A versão corrigida passa a ser a de referência** para H2 (bolsa × origem) e
para o E9 no ciclo 2. Se o "sinal robusto do ciclo 2" (E9) mudar de leitura, a
síntese (doc 57) registra isso numa nota datada. A síntese é gerada por script:
a nota vem de um adendo ao script 33, não de edição à mão.

## 3. Saídas

| Item | Onde |
|---|---|
| script | `scripts/rdd_bolsa/42_escolha_vaga_imediata_c2.py` |
| saídas | `output/rdd_bolsa/VC_estimativas.csv`, `VC_resumo.json` |
| resultados | `docs/06_execucao/57p_escolha_vaga_imediata_c2.md` |
| testes | `tests/test_escolha_vaga_imediata_c2.py` |
