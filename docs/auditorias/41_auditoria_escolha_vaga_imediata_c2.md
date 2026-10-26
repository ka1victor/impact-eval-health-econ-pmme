# 41. Auditoria do adendo 52c: tipo de vaga do ciclo 2 medido antes da alocação (E9, P1 M1 e M5, P1h-1)

> **Data:** 26/10/2026.<br>
> **Objeto:** adendo [`52c`](../06_execucao/52c_adendo_vaga_imediata_ciclo2.md), script
> `scripts/rdd_bolsa/42_escolha_vaga_imediata_c2.py`, saídas `output/rdd_bolsa/VC_*`, doc
> [`57p`](../06_execucao/57p_escolha_vaga_imediata_c2.md) e `tests/test_escolha_vaga_imediata_c2.py`. Base: branch
> `claude/vigilant-mccarthy-dd92mc` (commit `f97e1ca`). O adendo foi congelado no commit `4326241` e executado no
> `7bfe028`, sem mudança no adendo entre os dois.<br>
> **Referências:** `CLAUDE.md`; protocolos [52](../06_execucao/52_protocolo_P1_escolha_dap.md) e
> [52b](../06_execucao/52b_protocolo_P1h_magnitudes.md); docs 42, 57a e 57i; auditorias
> [31](31_auditoria_P1h_magnitudes.md) e [36](36_auditoria_dados_H1.md); scripts 16, 25 e 25c.<br>
> **Método:** recálculo próprio em memória, com código escrito do zero no scratch. Não importei os scripts 12, 16, 25,
> 25c nem 42. Escrevi do zero a leitura dos dois quadros do ciclo 2 (xlsx brutos), o mapa faixa → bolsa (a03), o
> spline, as matrizes, a CIR (TabNet bruto), os centroides (IBGE bruto), a distância, o logit condicional (Newton com
> meio-passo), o sanduíche com cluster por conjunto de escolha e o D_UF. Nada foi gravado em `output/`, salvo a
> reexecução do próprio script 42 para testar o determinismo.

## Veredito

**Aprovado, com correções de texto.** O quadro de 13/02/2026 entrou só onde o adendo manda: ciclo 2, nas três
colunas de vaga imediata, nos conjuntos do E9 e do P1. O portão de reprodução da versão antiga passou: a maior
diferença foi 4,8e−10, contra a tolerância de 1e−8. Meu recálculo independente bate com o gravado nas duas versões,
inclusive nos números pedidos:

- D_UF do P1h-1 corrigido: 1,942 [1,482; 2,402].
- Razão de chances do E9 no ciclo 2 corrigido: 2,037 [1,458; 2,848].

Nenhuma estimativa mudou. As correções são de texto no 57p: duas frases e uma referência, regravadas pelo script.
Fica um ponto de escopo para o autor (A1): o adendo não cobre todo o pedido da auditoria 36.

## Achados, por gravidade

### Médios

**A1. O conjunto de sensibilidade do E9 continua com o quadro de 19/03 (pendente; decisão do autor).** A auditoria
36 (seção 6, recomendação 3) pediu duas coisas no E9 do ciclo 2: reestimar com a vaga imediata de 13/02 e refazer o
conjunto de sensibilidade "só células com vaga imediata". O adendo 52c só manda a primeira (E9 principal, M1, M5 e
P1h-1). O script segue o adendo, e o 57p (§7) registra o que ficou de fora: a sensibilidade do E9, o M2, o M4, o M6,
o M7, o M8 e o M9 do P1, a DAP e o resto do P1h-3. Não é erro de execução. Mas a parte do doc 44 que diz que o ciclo
2 é robusto se apoia também nessas peças, e elas ainda usam o atributo formado em parte pelas escolhas. Refazer
exige outro adendo.

### Baixos

**A2. O 57p não dizia que a inferência robusta do doc 42 não foi refeita (corrigido).** O doc 44 diz que o sinal do
ciclo 2 é "robusto a poucos clusters e a placebos". O 57p conclui que "a leitura não muda" só pelo IC com cluster
(CR1, z), e citava como fragilidades apenas "só o ciclo 2; spline cúbico". Agora o bloco gerado diz que o score
bootstrap e os placebos de corte do doc 42 não foram refeitos com a covariável corrigida.

Para saber se isso mudaria a leitura, refiz no scratch o score bootstrap de Kline e Santos com pesos de Rademacher,
enumerando os 2^16 sinais (G = 16), sem usar o código do 16:

- Versão antiga: p = 9,2e−5, igual ao `E9_robustez_pos_auditoria.csv` (0,000092).
- Versão corrigida: p = 6,1e−5.

A robustez a poucos clusters se mantém. Esse número é da auditoria e não entra no 57p. Os placebos de corte e o spline
cúbico não foram refeitos.

**A3. Números fora dos blocos gerados (corrigido).** A §7 do 57p trazia "16 a 24 conjuntos por ciclo e 56 nos ciclos
empilhados" escrito no texto fixo do script, fora dos marcadores `VC:*`. Os valores estavam certos (16, 16 e 24 nos
ciclos 1, 2 e 3; 56 empilhado), mas não eram lidos das saídas. O texto agora remete à coluna `g_conjuntos` de
`VC_estimativas.csv`.

**A4. Referência ambígua (corrigido).** A §7 dizia "auditoria 36, seção 7" para o desequilíbrio de capitais. A seção
7 daquele documento é "Reprodução". O desequilíbrio está no item 7 da seção 3 ("Municípios que puxam o resultado"). O
texto agora diz "seção 3, item 7".

### Informativos

**I1. Linguagem.** A origem aparece sempre como preferência revelada, não como efeito causal: na resposta, nos
limites, no "Como ler" e no rodapé da figura. A bolsa aparece como pacote do corte e incentivo marginal, nunca como
efeito da participação no PMM-E. O "Como ler" diz que "a bolsa maior desloca a 1ª opção para a vaga". A frase é sobre
a bolsa, cujo contraste vem dos cortes (pacote), e o doc 44 usa a mesma formulação. Mantive.

**I2. A troca de covariável mexe nos coeficientes do tipo de vaga, não na bolsa.** No E9 do ciclo 2,
`tem_vaga_imediata` passa de 0,690 para −0,163, e `log_vagas_imediatas_mais_1` de 0,369 para 0,646. Faz sentido:
84,0% das 1ªs opções do ciclo 2 caem em célula com vaga imediata pelo quadro de 19/03, contra 53,3% pelo de 13/02. O
coeficiente da bolsa quase não se move (0,133 para 0,142). O D_UF do M1 também quase não se move (1,978 para 1,942).

**I3. Decisões de implementação.** As quatro decisões da §6 do 57p estão bem fundamentadas:

- parar se faltar célula, em vez de imputar;
- D_UF do M5 como sensibilidade, sem BKY;
- razão de chances do P1 por exp(5·β);
- Wald do P1d sem q BKY.

Nenhuma muda amostra, conjunto ou especificação.

## Verificações

### 1. Fidelidade ao adendo

| Item | Resultado |
|---|---|
| Quadro de 13/02 só no ciclo 2 | sim. `corrigir` troca só as linhas com `ciclo == 2`. Recalculei: ciclos 1 e 3 iguais byte a byte, e o M5 dos ciclos 1 e 3 é idêntico nas duas versões |
| Colunas trocadas | `vagas_imediatas`, `tem_vaga_imediata` e `log_vagas_imediatas_mais_1`. Município, faixa, população, macro e estrato não mudam (0 diferenças de município e de faixa entre os quadros) |
| Modelos reestimados | E9 principal (ciclo 2 e empilhado), P1 M1, M5 por ciclo, D_UF do P1h-1 (e P1h-3 do M5 como sensibilidade), Wald do P1d |
| Portão antes da troca | `estimar_versao` antigo → `portao` → só depois `estimar_versao` corrigido. Se falhar, `remover_saidas_calculadas` e saída 3 |
| Portão (≤ 1e−8) | PASSOU nas 11 linhas. Dif. máx. 4,8e−10 (coeficientes, os três EP, razão de chances e variação de probabilidade do E9, D_UF com IC e p, Wald) |
| Antigo e corrigido lado a lado | sim, todos os termos de todas as especificações em `VC_estimativas.csv` (226 linhas) |
| Holm | P1a e P1h-1 em famílias de um teste (p de Holm = p), E9 sem Holm, como nos protocolos 40, 52 e 52b |
| Nota na síntese 57 | não é exigida: a leitura do E9 no ciclo 2 não mudou (adendo §2) |

### 2. Recálculo independente

A leitura própria dos xlsx do ciclo 2 dá o seguinte:

- 1.547 células nos dois quadros.
- O conjunto gravado é igual ao quadro de 19/03 em 1.547 de 1.547 células.
- Nenhuma célula do conjunto falta no quadro de 13/02.
- 301 células eram só de reserva em 13/02 e têm vaga imediata em 19/03; o inverso não ocorre.
- Células com vaga imediata: 714 em 13/02 e 1.015 em 19/03.
- Vagas imediatas somadas: 1.206 e 1.836 (630 convertidas).

Tudo igual ao `VC_resumo.json` e à auditoria 36.

Refiz o logit condicional da 1ª opção. O conjunto de escolha é o das células do mesmo curso × ciclo. O cluster é o
conjunto de escolha (`id_conjunto_escolha`), com fator G/(G − 1). Para o E9: G = 16 no ciclo 2 e 56 no empilhado.
Para o P1, montei a amostra do G1 (`g1_cpf_nome`, origem com CIR, 1ª opção em município com CIR) e o formato longo
com distância haversine/100 km, mesma UF, mesma região de saúde e mesmo município.

| Especificação | Versão | Gravado | Recalculado | Dif. máx. (todos os coef.; EP da bolsa; RC; D_UF) |
|---|---|---|---|---|
| E9, ciclo 2: RC por +R$ 5 mil | antiga | 1,95 [1,48; 2,57] | 1,9455 [1,4752; 2,5657] | 3,8e−10; 4e−12; 3,7e−10 |
| E9, ciclo 2: RC por +R$ 5 mil | corrigida | 2,04 [1,46; 2,85] | 2,0374 [1,4578; 2,8476] | 4,1e−10; 3e−12; 4,3e−10 |
| E9, ciclos 1–3: RC | antiga / corrigida | 1,39 [1,12; 1,73] / 1,39 [1,11; 1,74] | 1,3922 [1,1202; 1,7302] / 1,3921 [1,1134; 1,7406] | ≤ 5,1e−9 |
| P1 M1: β da bolsa | antiga / corrigida | 0,0424 / 0,0453 | 0,04240 (p 0,065) / 0,04529 (p 0,072) | ≤ 2,9e−10 |
| P1h-1: D_UF (M1) | antiga | 1,978 [1,560; 2,396] | 1,9784 [1,5604; 2,3965]; LI 1,628 | 4,7e−10 |
| P1h-1: D_UF (M1) | corrigida | 1,942 [1,482; 2,402] | 1,9421 [1,4821; 2,4020]; LI 1,556 | 4,7e−10 |
| P1 M5, ciclo 2: RC / D_UF | antiga | 1,70 / 1,310 | 1,7021 / 1,3102 | ≤ 2,4e−9 |
| P1 M5, ciclo 2: RC / D_UF | corrigida | 1,79 / 1,187 | 1,7887 / 1,1869 | ≤ 2,2e−9 |

Os tamanhos de amostra conferem: 2.140 candidatos no E9 do ciclo 2, 5.714 no E9 empilhado, 5.421 no M1 (932.577
linhas candidato × célula) e 2.032 no M5 do ciclo 2. As diferenças até 5e−9 vêm do critério de parada do meu Newton.

### 3. Integridade

| Verificação | Resultado |
|---|---|
| IVS errado não é lido | `ivs_ipea_2010_municipios` não aparece no 42 nem nos scripts que ele importa (25c, 25, 16, 12, 17, 19, `rdd_lib`). O IVS vem do a08 |
| CNES ≥ 202609 | nenhuma leitura de CNES no 42. A origem vem do G1 versionado, e só tem as competências de referência 202506, 202510 e 202602 |
| `EMPIRICO` | 226 de 226 linhas do CSV e o resumo. Estatuto `ADENDO_52C_CORRECAO_COVARIAVEL` |
| Nada imputado | 0 células sem linha ou sem número no quadro de 13/02. `corrigir` para antes de imputar (testado com dado sintético) |
| `E9_*`, `P1_*`, `P1h_*` intactos | o commit `7bfe028` não os toca, e os hashes ficaram iguais depois da reexecução. O script não tem escrita neles |
| Determinismo | reexecutei o script 42 (41 s). `VC_estimativas.csv`, `VC_resumo.json`, a figura e o 57p saíram idênticos byte a byte |
| Identificadores | sem nome, CPF, CRM ou id de candidato em `VC_*` |
| Testes | `tests/test_escolha_vaga_imediata_c2.py`: 25 passaram, antes e depois das correções (só este módulo foi rodado) |

### 4. Texto do 57p

Todos os números das seções 1 a 6 estão em blocos `VC:*` gerados pelo script a partir de `output/`. O teste confere
que o doc é igual ao gerado. Só a §7 tinha números escritos à mão (A3), e foram tirados. As correções A2, A3 e A4
foram feitas no texto fixo do script 42, e o 57p foi regravado com `--atualizar-doc`. Saídas `VC_*` não mudaram.

## O que fica para o autor

1. Decidir se um novo adendo refaz, com o quadro de 13/02, o conjunto de sensibilidade "só células com vaga imediata"
   do E9 e os placebos e o score bootstrap do doc 42 (A1, A2). Esta auditoria indica que o score bootstrap se mantém.
2. Os modelos M2, M4, M6–M9 do P1, a DAP e o BKY das famílias secundárias continuam com o quadro de 19/03.
