# A6 — Red team da evidência empírica

> Data: 2026-09-16  
> Escopo máximo: evidência associativa de implementação e evolução da oferta médica cadastrada.  
> Resultado principal: atração administrativa (A4). Resultado secundário: dinâmica agregada do CNES (A5).

## Método de refutação

Cada afirmação foi atacada por mudança de denominador, estágio do funil, unidade de observação, amostra CBO, período de referência, controles, influência e linguagem. “Passar” significa apenas sobreviver a esses testes; não transforma associação em efeito causal.

## Checklist e vereditos

### 1. Denominador e versionamento

**Refutação tentada:** usar 678 vagas imediatas como denominador e interpretar confirmações em reserva como preenchimento de vaga imediata. Há células com eventos acima da capacidade publicada e a chamada 2 não oferece quantidade imediata comparável.  
**Veredito:** usar a célula CNES–curso e o indicador de alguma confirmação ou homologação. Taxa por vaga fica bloqueada.

### 2. População territorial definida antes do resultado

**Refutação tentada:** redefinir interior depois de observar os coeficientes.  
**Veredito:** mantida a tipologia REGIC 2018 + RM/RIDE 2022 em quatro estratos, congelada antes da estimação: capital, metropolitano, interior próximo e interior remoto.

### 3. Seleção de municípios, cursos e estabelecimentos

**Refutação tentada:** misturar cursos com ponte CBO sobreposta e atribuir a mudança a uma especialidade específica.  
**Veredito:** A4 cobre 1.295 células em 368 municípios; A5 principal restringe-se a 587 células município–curso de dez cursos cujo CBO não é compartilhado com outro curso do PMM-E, em 295 municípios; apenas oito desses cursos têm CBO estritamente 1:1. A amostra ampliada é apenas sensibilidade.

### 4. Inferência municipal e concentração

**Refutação tentada:** usar erros independentes por célula e ignorar exposição comum dentro do município.  
**Veredito:** erros agrupados por município em todos os modelos principais. Leave-one-out (LOO) por UF, curso e município e diagnóstico de influência permanecem obrigatórios.

### 5. Confirmação, homologação, entrada e permanência

**Refutação tentada:** chamar confirmação de entrada física ou presença cadastral de retenção.  
**Veredito:** os estágios são separados. Em A4, o contraste metropolitano é 27,0 pp para confirmação e 23,8 pp para homologação. Em A5, “entrada” é um novo vínculo no mês após washout de seis meses, não um fluxo acumulado semestral.

### 6. IVS e faixa de bolsa

**Refutação tentada:** interpretar IVS, faixa e valor anunciado como fontes independentes de variação.  
**Veredito:** a grade administrativa é colinear e a regra não foi reproduzida para 177/368 municípios. IVS 2010 continua a running variable canônica, mas o RDD foi encerrado no portão R1.

### 7. CNES e retenção individual

**Refutação tentada:** usar estoque municipal do CBO para afirmar permanência do bolsista.  
**Veredito:** CNES mede oferta cadastrada agregada. Sem ponte nominal validada, não identifica participação no PMM-E nem retenção individual.

### 8. RDD

**Refutação tentada:** forçar descontinuidade em IVS=0,4 apesar da falha na reconstrução da regra e do suporte discreto.  
**Veredito:** RDD encerrado em R1; nenhuma afirmação causal do adicional da bolsa.

### 9. SIH/SIA, fila, saúde e custo-benefício

**Refutação tentada:** extrapolar estoque cadastral para resolutividade, internações, fila ou retorno econômico.  
**Veredito:** sem SIH/SIA e sem portão de linkage/pagamentos, esses desfechos ficam fora do núcleo empírico atual.

## Ataques ao resultado principal (A4)

- O contraste metropolitano versus interior remoto é 27,9 pp no LPM pré-especificado e 20,9 pp no ajuste completo.
- Separar o funil preserva o sinal: 27,0 pp em confirmação e 23,8 pp em homologação.
- Colapsar múltiplos CNES para município–curso aumenta o contraste para 31,6 pp; logo, o resultado não decorre do peso implícito de estabelecimentos múltiplos.
- Winsorizar covariadas e executar leave-one-out não inverte o gradiente. O resultado é robusto como associação territorial, não como efeito da bolsa.

## Ataques ao resultado secundário (A5)

- Setembro/2025 foi rejeitado como baseline porque já contém exposição física. A referência limpa é junho/2025 e o follow-up comum é março/2026.
- O estudo dinâmico usa efeitos fixos de célula, curso–mês e UF–mês, com cluster municipal. Em março/2026, a diferença associada à atração é 0,50 (EP 0,23; p=0,033); o teste conjunto prévio tem p=0,420.
- A sensibilidade ampliada produz 0,60 (p=0,006), mas mistura CBOs sobrepostos.
- A distribuição é assimétrica: sem atração, média 0,55, mediana 0, máximo 25; com atração, média 2,29, mediana 1, máximo 211. Winsorizar muda materialmente a precisão, portanto médias simples não bastam.
- O modelo de nível é dominado por diferenças basais e a validação preditiva fora da amostra é fraca. Ambos ficam como diagnósticos.

### Forma funcional: o que é frágil é o nível, não a proporção

**Refutação tentada:** atribuir o resultado secundário à escala de medida, testando se ele sobrevive à troca de nível por proporção e à retirada de cada curso.
**Veredito:** a fragilidade é **do nível**, e é específica dele. Em nível, o coeficiente de março/2026 cai de 0,50 para 0,20 sem o curso 14 (p=0,366) e para 0,12 nos oito cursos com CBO estritamente 1:1 (p=0,608) — deixa de ser distinguível de zero. Somar profissionais de municípios com estoques de ordens de grandeza diferentes faz um curso de estoque grande dominar o coeficiente mecanicamente.

Na escala proporcional, que é a primária, o mesmo exercício não desfaz o resultado: 0,068 (EP 0,018; p=0,0002) na amostra completa, entre 0,056 e 0,088 ao retirar um curso por vez, e 0,057 (p=0,010) nos oito cursos estritos. O enunciado correto, portanto, não é o de vulnerabilidade genérica a caudas que este documento trazia antes do item C2 do plano `35`: é que **o nível é frágil à composição de cursos e a proporção não é**. A escolha da escala proporcional é substantiva — mede variação relativa da oferta local, que é a pergunta pretendida — e vale nas duas direções do resultado. A multiplicidade aponta na mesma direção (item B-5): na família dos 25 coeficientes de evento da amostra confirmatória, o coeficiente de março/2026 tem q de Benjamini–Hochberg de 0,0034 na escala proporcional e de 0,364 em nível — só a proporção sobrevive.

### Placebo, pré-tendência por curso e deslocamento (C-7)

As três ameaças que a reauditoria independente levantou foram testadas em 16/09/2026 sob protocolo congelado antes da execução (`docs/06_execucao/36_backlog_pos_auditoria.md`, item C-7), a partir do painel congelado de A5 com hash conferido contra este manifesto. Resultados em `A5_ameacas_c7.json` e nas tabelas `A5_tabela_12` a `A5_tabela_14`; inferência na convenção que conta os efeitos fixos absorvidos.

**Placebo — células sem atração em municípios com atração.** Refutação tentada: o resultado principal seria choque municipal correlacionado com atrair, e não a atração da própria célula. Entre as células confirmatórias sem atração (198 em municípios com atração em alguma célula, 174 em municípios sem nenhuma), o coeficiente de março/2026 é 0,063 em nível (EP 0,309; p=0,837; pré-F 1,57, p=0,102) e 0,0007 na escala proporcional (p=0,980). **Veredito:** o placebo passa nas duas escalas; a reauditoria havia medido 0,092 (EP 0,303; p=0,761) em nível, mesma ordem e mesma leitura. O resultado principal é da célula, não do município.

**Heterogeneidade de pré-tendência por curso.** Refutação tentada: o p agregado do teste pré esconderia cursos com caminhos pré divergentes. Dentro de cada um dos dez cursos, o teste conjunto dos doze coeficientes pré rejeita a 5% na escala proporcional nos cursos 2, 16 e, em nível, nos cursos 2, 14, 16 — os mesmos que a reauditoria apontara (2, 14 e 16 em nível). Nos cursos 3, 5, 12, 13, 15, 16 a covariância das restrições não tem posto completo (poucos municípios), e o F conjunto não é confiável; o curso 16 está entre eles. Pela regra fixada no protocolo, excluindo os cursos rejeitados na escala proporcional o coeficiente de março/2026 vai a 0,0810 (EP 0,0236; p=0,0007) na proporção e a 0,579 (p=0,057) em nível, sobre 488 células. **Veredito:** a heterogeneidade existe e fica publicada por curso; ela não desfaz a escala proporcional e reforça que o nível é o que depende de composição.

**Deslocamento dentro da região de saúde.** Refutação tentada: o ganho do município com atração sairia de vizinhos da mesma região, sem expansão líquida — a separação que o `CLAUDE.md` exige. (a) Entre células sem atração, as expostas a outro município do painel na mesma região com atração no mesmo curso (70 contra 302) não perdem estoque: 0,276 em nível (p=0,542) e -0,0105 na proporção (p=0,741). (b) Somando o estoque por região–curso sobre os municípios do painel (173 regiões; 202 região–curso com atração contra 247 sem), a diferença de março/2026 é 0,773 em nível (EP 0,238; p=0,001) e 0,0502 na proporção (p=0,006), com pré-F de 0,79 (p=0,663). **Veredito:** não há sinal de deslocamento a partir dos vizinhos observados, e a oferta regional agregada também sobe. **Limite declarado:** o painel só contém os 368 municípios do quadro, de modo que "vizinho" é vizinho dentro do quadro; deslocamento a partir de municípios fora da oferta não é observável aqui, e a leitura continua associativa.

## Veredito geral

O núcleo útil é a desigualdade territorial na atração administrativa, robusta ao estágio do funil e à unidade analítica. A evolução do estoque cadastral após a oferta é compatível com uma diferença positiva modesta: na escala proporcional ela sobrevive à retirada de qualquer curso e à restrição aos CBOs estritos; na escala de nível, não. O que limita a leitura é a composição de cursos no nível, a pré-tendência divergente em dois cursos, o tempo de exposição física heterogêneo e o fato de que o teste de deslocamento só vê vizinhos dentro do quadro. O placebo passa, e a oferta regional agregada também sobe. Não há base para reivindicar efeito causal, provimento atribuível ao programa ou retenção individual.

*Gerado por `scripts/tema_trabalho/07_red_team_sintese.py`.*
