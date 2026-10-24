# Auditoria independente do P1 (protocolo 52): escolha do candidato e DAP

> **Data:** 24/10/2026.<br>
> **Objeto:** commit `bd4b707`: `scripts/rdd_bolsa/25_escolha_dap.py`,
> `output/rdd_bolsa/P1_estimativas.csv`, `P1_dap.csv`, `P1_resumo.json`, `P1_figuras/`,
> o [doc 57a](../06_execucao/57a_resultados_P1_escolha.md) e `tests/test_escolha_dap.py`,
> contra o [protocolo 52](../06_execucao/52_protocolo_P1_escolha_dap.md).<br>
> **Veredito:** **APROVADO COM CORREÇÕES DE TEXTO.** Nenhuma estimativa mudou: M0, M1,
> a DAP por delta, M5 e o Wald foram reproduzidos com código próprio (diferença
> máxima de 3e-10). As correções são de relato (itens da seção 4).<br>
> **Proveniência dos números:** lidos de `output/rdd_bolsa/P1_*` depois da correção. A
> conferência que fica no repositório é `TestRecalculoIndependenteAuditoria26`.

## 1. Método

Logit condicional escrito do zero (log-verossimilhança, escore, informação, Newton com
passo limitado), sanduíche com cluster por conjunto de escolha (curso × ciclo) e fator
G/(G−1). Distância haversine, mesma UF, região de saúde (CIR) e município de origem
montados no teste. Só os leitores de insumos (IVS oficial, conjunto de escolha, CIR,
centroides) vêm do E9, da X5 e do X1. O script 25 não é importado. O arquivo de IVS
errado não foi lido (nem o script 25 nem os módulos importados o citam).

## 2. Recálculo

| Item | Diferença máxima |
|---|---|
| M0: bolsa e EP (5421 candidatos, 56 conjuntos) | ponto 7e-12; EP relativo 1e-10 |
| M1: 18 termos, EP e log-verossimilhança (−13658,16) | ponto 3e-10; EP relativo 4e-10 |
| M1: IC e p da bolsa | < 1e-5 |
| P1b/P1c: DAP e IC delta (distância, mesma UF, capital, vaga imediata) | < 1e-7 |
| M5: bolsa e EP nos ciclos 1, 2, 3 | ponto 4e-11; EP relativo 2e-10 |
| Wald de igualdade (χ² = 5,69; p = 0,058) | < 1e-8 |
| BKY (12 linhas, grade própria) | ≤ 1e-3 (arredondamento da grade) |

Holm só na linha M1 empilhado. M8 e M9 não foram refeitos: gradiente máximo 1e-8 e
5e-10, informação definida positiva, M9 com verossimilhança acima do M1 e a razão
registrada igual a 2·ΔLL; M8 acima do M1. O bootstrap tem 999 réplicas válidas e o
percentil 2,5–97,5 do coeficiente da bolsa envolve o ponto.

## 3. Protocolo e integridade

- Amostra G1 (5421), variáveis do M1 e Holm/BKY conforme o protocolo. A reparametrização
  da capital em M1 está declarada.
- M3 `NAO_EXECUTADO` com motivo: o G1 gravou a distância mais próxima só das células
  ranqueadas, e o cache dos vínculos não está no checkout. Nada aproximado. Aceito.
- `natureza_dos_dados = EMPIRICO` em todas as linhas. Varredura de `output/`: sem CPF,
  sem nome, sem pseudônimo de candidato.
- `data/` não aparece no diff do commit. O manifesto A6 é consistente com o gerador
  (`07_red_team_sintese.py`): o passo 25 está na posição de `run_all.py` e os hashes
  conferem com os arquivos; só mudaram o comando e a plataforma.
- **Correção numérica de M8/M9 (desvio 10).** A mudança (polimento por Newton depois do
  L-BFGS-B, mesma tolerância de 1e-4, mesma amostra e especificação) é só numérica, e o
  resultado final tem gradiente 4 a 6 ordens abaixo da tolerância. O relato é
  transparente. A ordem dos fatos ("nenhum coeficiente da primeira execução foi lido")
  **não é verificável**: o histórico tem um só commit e não guarda a primeira saída.

## 4. Defeitos de texto e correções

1. Desvios sem data no doc (a data existia só no JSON). Agora cada item traz a data.
2. P1g: sinais opostos (previsto +0,218; observado −0,457) sem leitura, e o "Como ler" dizia
   que "pares próximos" mostram a mesma história. Agora: sinais opostos, intervalos que se
   sobrepõem e contêm zero, não confirma nem refuta o M1, não é teste.
3. DAP: os ICs largos não eram destacados. Agora o parágrafo diz, em negrito, em quantos
   atributos o IC contém zero (delta e bootstrap), que o ponto não é preço e que a
   razão extrapola a faixa de R$ 10–20 mil. Há aviso sob a tabela sobre a DAP por ciclo.
4. P1a: só M0 e E9 apareciam ao lado do M1. Agora a leitura diz em quais outras
   especificações o IC exclui zero (M2, M4, M8, M9) e em quais contém (M7), e que a leitura
   é sensível à especificação.

Estimativas, CSVs e figuras ficaram idênticos (cmp). O script foi reexecutado por
inteiro (cerca de 20 min); mudaram o resumo (`como_ler`) e o doc 57a.

## 5. Linguagem conferida

P1a como escolha dentro das vagas abertas, pacote do corte, nada sobre quem não se
candidatou; IC do M1 contém zero e não vira "efeito"; figuras sem texto de leitura
embutido e com "Como ler" curto.

## 6. Testes

`python -m pytest tests/test_escolha_dap.py tests/test_pipeline_rdd_bolsa.py`: 51 passam.
