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

Na escala proporcional, que é a primária, o mesmo exercício não desfaz o resultado: 0,068 (EP 0,018; p=0,0002) na amostra completa, entre 0,056 e 0,088 ao retirar um curso por vez, e 0,057 (p=0,010) nos oito cursos estritos. O enunciado correto, portanto, não é o de vulnerabilidade genérica a caudas que este documento trazia antes do item C2 do plano `35`: é que **o nível é frágil à composição de cursos e a proporção não é**. A escolha da escala proporcional é substantiva — mede variação relativa da oferta local, que é a pergunta pretendida — e vale nas duas direções do resultado.

### Ameaças que este red team não testou

Honestidade de escopo: três ameaças levantadas pela reauditoria independente **não** são testadas aqui, e a ausência não deve ser lida como aprovação. São elas o **placebo** sobre células sem atração em municípios com atração, a **heterogeneidade de pré-tendência** por curso, e o **deslocamento** entre municípios da mesma região de saúde, que o `CLAUDE.md` exige separar de expansão líquida. Todas exigiriam regravar artefato de A5, hoje impossível neste ambiente: o painel do CNES não está versionado. Condição de desbloqueio e o que a reauditoria mediu por conta própria estão em `docs/06_execucao/36_backlog_pos_auditoria.md`, itens C-7 e D-4.

## Veredito geral

O núcleo útil é a desigualdade territorial na atração administrativa, robusta ao estágio do funil e à unidade analítica. A evolução do estoque cadastral após a oferta é compatível com uma diferença positiva modesta: na escala proporcional ela sobrevive à retirada de qualquer curso e à restrição aos CBOs estritos; na escala de nível, não. O que limita a leitura é a composição de cursos no nível, o tempo de exposição física heterogêneo e três ameaças ainda não testadas. Não há base para reivindicar efeito causal, provimento atribuível ao programa ou retenção individual.

*Gerado por `scripts/tema_trabalho/07_red_team_sintese.py`.*
