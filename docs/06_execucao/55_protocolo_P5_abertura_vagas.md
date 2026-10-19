# 55. Protocolo P5: como o Ministério escolhe onde abrir vagas

> **Data de congelamento:** 19/10/2026, antes de estimar.<br>
> **Origem:** plano do doc 51 (P5, tarefas T5.1–T5.3).<br>
> **Estatuto:** `PROTOCOLO_55_DESCRITIVO`. T5.1 e T5.3 são **descritivos**: não
> há leitura causal da decisão do Ministério. T5.2 é uma RDD nos cortes, que
> mede o pacote. Já vistos: F0.3 por município (doc 41) e S-c (doc 49). Toda
> saída leva `natureza_dos_dados = EMPIRICO`.

## 1. Etapas e unidades

| Etapa | Ciclo | Unidade | Outcome |
|---|---|---|---|
| E1. pedido do gestor | 3 | célula do cardápio | célula pedida (linha na adesão) |
| E2. priorização da SGTES | 3 | célula pedida | célula priorizada (tudo ou nada) |
| E3. quadro publicado | 1, 2 | município | nº de células e de vagas no quadro |

No ciclo 3, o município que não aparece no resultado da adesão fica **ausente**
nas variáveis de pedido, nunca zero (regra do doc 41a §5). A E1 é estimada
entre os municípios presentes no resultado. A presença em si é uma linha
separada, ao nível do município.

## 2. Covariáveis pré-determinadas

- **Estabelecimento** (do cardápio): tipo, gestão, natureza jurídica.
- **Município:**
  - log da população de 2022;
  - hierarquia urbana (REGIC 2018);
  - capital;
  - macrorregião;
  - polo da região de saúde (maior população da região, pela tabela do TabNet).
- **Capacidade pré** (painel CNES, 202406–202506, média): vínculos das CBO do
  curso da célula e de todos os médicos, por 10 mil habitantes. Para o curso,
  usar a ponte curso–CBO do a09.
- **Produção pré** (SIA, a12, competências 202406–202506): produção aprovada do
  conjunto de CBO `alvo_pmme` e de todos os profissionais, por 10 mil
  habitantes.
- **Escassez regional:** vínculos das CBO do curso por 10 mil na região de saúde.
- **IVS 2010 oficial,** contínuo.

## 3. Especificações

| Id | Especificação | Leitura |
|---|---|---|
| T5.1a | logit de E1 nas covariáveis, com efeito fixo de curso; EP com cluster por município | descritivo |
| T5.1b | logit de E2 nas covariáveis, entre células pedidas, com efeito fixo de curso | descritivo |
| T5.1c | efeitos marginais médios e contribuição de cada bloco (pseudo-R² com e sem o bloco) | descritivo |
| T5.2a | RDD nos cortes da fração de células pedidas e da priorizada, por célula (cluster por município, efeito fixo de curso) e por município | pacote nos cortes; h = 0,050; cortes empilhados |
| T5.2b | T5.2a com covariáveis pré-determinadas (CCFT) | robustez |
| T5.3 | Poisson do nº de células e de vagas no quadro dos ciclos 1 e 2 nas mesmas covariáveis municipais, com o IVS contínuo | descritivo, dá base ao A4 |

## 4. Relato

- Tabelas de efeitos marginais e figuras de contribuição por bloco, com "Como
  ler".
- Sem teste múltiplo nas linhas descritivas.
- T5.2 com BKY entre as suas linhas.
- Linguagem: "associado a", nunca "o Ministério escolhe por causa de".
- O critério oficial não é publicado (auditoria 01; doc 51 §1).

## 5. Saídas

| Item | Onde |
|---|---|
| script | `scripts/rdd_bolsa/29_determinantes_abertura.py` |
| estimativas | `output/rdd_bolsa/P5_estimativas.csv` |
| resumo | `P5_resumo.json` |
| figuras | `P5_figuras/` |
| resultados | doc 57, seção P5 |

## 6. Integridade

Valem as regras de sempre:
- nada imputado;
- ausente não vira zero;
- nenhum CNES ≥ 202609;
- o SIA é lido só no pré;
- o arquivo de IVS errado não é lido.
