# 52. Protocolo P1: quanto o salário move a escolha de onde trabalhar

> **Data de congelamento:** 19/10/2026, antes de estimar qualquer linha abaixo.
> O portão G1 (`docs/auditorias/G1_viabilidade_candidatos.md`) foi juntado sem
> contrastes.<br>
> **Origem:** plano do doc 51 (P1, tarefas T1.1–T1.5). Os cenários do T1.6 ficam
> para depois da auditoria deste bloco.<br>
> **Estatuto:** `PROTOCOLO_52_POS_RESULTADO`. O E9 (doc 42) e a X4 e a X5 (doc
> 46) já foram vistos. Este protocolo não muda o E9 nem o Holm do protocolo 40.
> Toda saída leva `natureza_dos_dados = EMPIRICO`.

## 1. Pergunta e estimandos

**Pergunta econômica.** Quanto a remuneração anunciada move a escolha de onde
trabalhar, em relação a distância, porte, capital, tipo de vaga e
vulnerabilidade? Isto é, qual o diferencial compensatório?

| Id | Estimando | Papel |
|---|---|---|
| P1a | coeficiente da bolsa (por R$ 1 mil/mês) na utilidade da 1ª opção, ciclos 1–3 empilhados, com distância | **primária** |
| P1b | disposição a pagar (DAP) por 100 km a menos de distância origem–vaga = −β_dist / β_bolsa, em R$ mil/mês | primária descritiva (IC, sem teste de zero) |
| P1c | DAP por ficar na mesma UF da origem, por capital, por vaga imediata | secundárias |
| P1d | β_bolsa por ciclo e teste de igualdade entre ciclos (T1.3) | secundária |
| P1e | heterogeneidade: bolsa × tercil da nota, bolsa × origem no próprio município, bolsa × curso (T1.2, T1.4) | secundárias |
| P1f | logit misto: média e desvio do coeficiente da bolsa e da distância | secundária |
| P1g | ponte P1 → P2: salto previsto pelo modelo em candidatos de 1ª opção por célula no corte, contra a RDD por célula (T1.5) | secundária |

## 2. Dados

| Item | Fonte |
|---|---|
| Escolhas | `output/rdd_bolsa/outcomes/escolhas_candidatos.parquet` (1ª opção como escolha; a 2ª opção entra no logit explodido) |
| Conjunto de escolha | `escolhas_conjunto_principal.parquet` (curso × ciclo, todas as células do quadro, como no E9 §14) |
| Bolsa | `faixa_anunciada` → R$ 10, 15 ou 20 mil |
| IVS | oficial, via os arquivos de outcome; spline contínua com nós em 0,300 e 0,400, como no E9 §15 |
| Distância | `G1_distancias_opcoes.parquet`, a distância da origem principal; `dist_km_origem_mais_proxima` como sensibilidade |
| Mesma UF, mesma região de saúde, mesmo município | `G1_candidatos_origem.parquet` com a tabela de regiões de saúde do TabNet |
| Capital e porte | log da população de 2022 |
| Hierarquia urbana | REGIC 2018 (`data/raw/aquisicao/territorio/`), só leitura |

**Amostra principal:** candidatos com origem ligada (G1). Sensibilidade: o E9
reestimado na mesma amostra sem distância, e na amostra completa do E9, para
mostrar o efeito da seleção pela ligação.

## 3. Especificações

Base comum, igual ao E9 §15:
- logit condicional;
- bolsa linear em R$ mil;
- IVS como spline;
- EP sanduíche com cluster por conjunto de escolha (curso × ciclo);
- EP de máxima verossimilhança e cluster por candidato relatados também.

| Id | Especificação |
|---|---|
| M0 | E9 principal na amostra G1 (sem distância) |
| **M1** | **M0 + distância/100 km + mesma UF + mesma região de saúde + mesmo município de origem + log pop + capital + vaga imediata** (principal de P1a–P1c) |
| M2 | M1 com log(1 + distância) no lugar da distância linear |
| M3 | M1 com distância da origem mais próxima |
| M4 | M1 com efeito fixo de UF da vaga |
| M5 | M1 por ciclo; teste de Wald de igualdade de β_bolsa entre ciclos |
| M6 | M1 + bolsa × (tercil da nota no ciclo); bolsa × origem no município; bolsa × curso (≥ 100 candidatos) |
| M7 | logit explodido (1ª e 2ª opção) com M1 |
| M8 | logit misto: coeficientes normais na bolsa e na distância; 500 sorteios Halton (semente 20261019); demais fixos |
| M9 | logit aninhado por região de saúde (como a X5), com M1 |

**DAP:** razão de coeficientes, IC pelo método delta e por bootstrap por
conjunto de escolha (999 réplicas, semente fixa). Unidades: R$ mil por mês.

**P1g:** usar M1 para prever, em cada célula, a esperança de candidatos de 1ª
opção. Depois:
- calcular o salto no corte que o modelo implica, mudando só a bolsa;
- comparar com a RDD por célula de `n_cand_1a_opcao`, com efeito fixo de curso
  × ciclo e cluster por município (convenção do A3).

A leitura é de consistência, não um teste novo.

## 4. Inferência e relato

- Holm só em P1a. P1b e P1c são estimativas com IC.
- BKY nas secundárias com p-valor (P1d, P1e, P1f).
- Toda especificação é relatada.
- Linguagem: P1a é um efeito da remuneração na escolha **dentro do conjunto de
  vagas abertas**, identificado pelos saltos da bolsa nos cortes, com a
  vulnerabilidade contínua controlada. Não diz nada sobre quem não se
  candidatou.

**Ameaças declaradas:**
- seleção pela ligação (5% sem origem);
- origem = município do estabelecimento, não residência;
- o conjunto de escolha supõe que o candidato viu todas as células do curso;
- outras políticas nos cortes podem mudar atributos não observados da vaga
  (pacote).

## 5. Saídas

| Item | Onde |
|---|---|
| script | `scripts/rdd_bolsa/25_escolha_dap.py` |
| estimativas | `output/rdd_bolsa/P1_estimativas.csv`, `P1_dap.csv` |
| resumo | `P1_resumo.json` |
| figuras | `P1_figuras/` (DAP com IC; β por ciclo; ponte P1g), cada uma com "Como ler" |
| resultados | `docs/06_execucao/57_resultados_perguntas_reformuladas.md`, seção P1, gerada pelo script |

## 6. Integridade

Valem as regras de sempre:
- nada imputado;
- o que falta fica faltante, com motivo;
- sem nome nem CPF em `output/`;
- números do doc gerados ou testados;
- o arquivo de IVS errado não é lido;
- nenhum CNES ≥ 202609.
