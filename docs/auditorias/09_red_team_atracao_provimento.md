# A6 — Red team da evidência empírica

> Data: 2026-09-03  
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
**Veredito:** A4 cobre 1.295 células em 368 municípios; A5 principal restringe-se a 587 células município–curso de dez cursos com CBO unívoco, em 295 municípios. A amostra ampliada é apenas sensibilidade.

### 4. Inferência municipal e concentração

**Refutação tentada:** usar erros independentes por célula e ignorar exposição comum dentro do município.  
**Veredito:** erros agrupados por município em todos os modelos principais. Leave-one-out (LOO) por UF, curso e município e diagnóstico de influência permanecem obrigatórios.

### 5. Confirmação, homologação, entrada e permanência

**Refutação tentada:** chamar confirmação de entrada física ou presença cadastral de retenção.  
**Veredito:** os estágios são separados. Em A4, o contraste metropolitano é 28.5 pp para confirmação e 25.0 pp para homologação. Em A5, “entrada” é um novo vínculo no mês após washout de seis meses, não um fluxo acumulado semestral.

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

- O contraste metropolitano versus interior remoto é 29.4 pp no LPM pré-especificado e 19.8 pp no ajuste completo.
- Separar o funil preserva o sinal: 28.5 pp em confirmação e 25.0 pp em homologação.
- Colapsar múltiplos CNES para município–curso aumenta o contraste para 33.1 pp; logo, o resultado não decorre do peso implícito de estabelecimentos múltiplos.
- Winsorizar covariadas e executar leave-one-out não inverte o gradiente. O resultado é robusto como associação territorial, não como efeito da bolsa.

## Ataques ao resultado secundário (A5)

- Setembro/2025 foi rejeitado como baseline porque já contém exposição física. A referência limpa é junho/2025 e o follow-up comum é março/2026.
- O estudo dinâmico usa efeitos fixos de célula, curso–mês e UF–mês, com cluster municipal. Em março/2026, a diferença associada à atração é 0.50 (EP 0.23; p=0.033); o teste conjunto prévio tem p=0.420.
- A sensibilidade ampliada produz 0.60 (p=0.006), mas mistura CBOs sobrepostos.
- A distribuição é assimétrica: sem atração, média 0.55, mediana 0, máximo 25; com atração, média 2.29, mediana 1, máximo 211. Winsorizar muda materialmente a precisão, portanto médias simples não bastam.
- O modelo de nível é dominado por diferenças basais e a validação preditiva fora da amostra é fraca. Ambos ficam como diagnósticos.

## Veredito geral

O núcleo útil é a desigualdade territorial na atração administrativa, robusta ao estágio do funil e à unidade analítica. A evolução do estoque cadastral após a oferta é compatível com uma diferença positiva modesta, mas vulnerável a caudas, composição e tempo de exposição heterogêneo. Não há base para reivindicar efeito causal, provimento atribuível ao programa ou retenção individual.

*Gerado por `scripts/tema_trabalho/07_red_team_sintese.py`.*
