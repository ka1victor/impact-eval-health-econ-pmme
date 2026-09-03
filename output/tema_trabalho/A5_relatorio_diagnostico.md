# A5 — Evolução da oferta médica cadastrada local no CNES

> **Nível de identificação:** associativo; atração administrativa é resultado realizado, não tratamento exógeno.
> **Amostra principal:** 587 células município–curso, 295 municípios e 10 cursos com ponte CBO unívoca.
> **Referência limpa:** junho/2025, última competência anterior à publicação da oferta.
> **Follow comum:** março/2026; nove meses de calendário desde a referência, com tempo de exposição física heterogêneo.

## 1. Correção de desenho

Setembro/2025 não é usado como baseline principal. O snapshot nominal registra início mediano em 2025-09-19, com datas entre 2025-09-11 e 2026-03-17; portanto, setembro já contém exposição parcial. A janela setembro/2025–março/2026 permanece apenas como diagnóstico histórico em `A5_tabela_03f_sensibilidade_T0_alternativo.csv`.

Os modelos principais usam somente a ponte sem sobreposição. As 597 células dos seis cursos com CBO compartilhado aparecem como sensibilidade ampliada, nunca misturadas ao estimando principal.

## 2. Resultado principal: dinâmica do estoque

O estudo de evento compara a trajetória do estoque CNES de células com e sem atração administrativa, relativamente a junho/2025. Ele absorve efeitos fixos município–curso, curso–mês e UF–mês e agrupa a inferência por município.

- Teste conjunto dos coeficientes anteriores à referência: F=1.031, p=0.420. A não rejeição não prova comparabilidade.
- Em março/2026, a diferença ajustada relativa a junho/2025 é 0.500 especialista (EP 0.234, p=0.033).
- A estimativa descreve evolução diferencial associada à atração; não é efeito do PMM-E, da bolsa ou do IVS.

A tabela completa está em `A5_tabela_07_estudo_evento_atracao.csv`; a figura principal é `A5_figura_04_estudo_evento_atracao.png`.

## 3. Distribuição e sensibilidade

Na amostra confirmatória, a variação junho/2025–março/2026 tem mediana 0.0 e máximo 211. Entre células com atração, a média é 2.29, a mediana 1.0 e 57.7% apresentam aumento; sem atração, os valores são 0.55, 0.0 e 32.5%.

As regressões de nível, cobertura, novos vínculos mensais após washout, presença da coorte e validação preditiva são diagnósticos secundários. `n_entradas_6m` significa novo vínculo observado no mês após seis meses de ausência, e não entradas acumuladas ao longo de seis meses.

## 4. Linguagem autorizada

Permitido: **evolução do estoque cadastral**, **trajetória diferencial associada à atração**, cobertura e novos vínculos mensais após washout. Proibido: provimento causal, retenção individual do bolsista, atividade física confirmada, efeito causal do PMM-E/bolsa/IVS, taxa por vaga ou dose recebida.

O CNES não identifica participantes do programa. Sem log completo, ponte individual e pagamentos, o A5 permanece uma análise descritiva longitudinal complementar ao resultado de implementação A4.

*Gerado em 2026-09-03 por `scripts/tema_trabalho/06_avaliar_provimento_cnes.py`.*
