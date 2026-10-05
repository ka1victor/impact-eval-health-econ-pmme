# Portões R1 e R2 com o IVS administrativo — a RDD da bolsa é identificável

> **Execução:** 05/10/2026.
> **Decisões:** R1 `APROVADO_SHARP`; R2 `VIAVEL_CONTINUIDADE_COM_RESSALVAS`.
> Nenhum outcome foi aberto. R3 depende de decisão do autor; R4 está bloqueado.
>
> Artefatos: [`a01c_regra_ivs_administrativo.json`](../../output/rdd_bolsa/a01c_regra_ivs_administrativo.json),
> [`matriz_municipio_ivs_administrativo.csv`](../../output/rdd_bolsa/matriz_municipio_ivs_administrativo.csv),
> [`r2_portao.json`](../../output/rdd_bolsa/r2_portao.json),
> [`r2_suporte.csv`](../../output/rdd_bolsa/r2_suporte.csv),
> [`r2_testes_continuidade.csv`](../../output/rdd_bolsa/r2_testes_continuidade.csv).
> Scripts: `scripts/aquisicao/a07_adquirir_ivs_administrativo.py`,
> `scripts/rdd_bolsa/01c_reconstruir_regra_ivs_administrativo.py`,
> `scripts/rdd_bolsa/04_auditar_r2_suporte_selecao_balanco.py`.

## 1. O que mudou

O R1 de 04/09 e 14/09 ([`07_portao_rdd_bolsa.md`](07_portao_rdd_bolsa.md)) reprovou
porque usou o IVS 2010 do Atlas como running variable. Esse diagnóstico continua
verdadeiro: o IVS 2010 não reproduz a faixa. O que faltava não era a regra, e sim
a variável certa. **A SGTES publica o próprio IVS.**

O quadro de vagas do Chamamento SGTES/MS nº 2/2026 do Mais Médicos para o Brasil
(PMMB), aba "Lista de Municípios-Tipo Equipe", traz para os 5.571 municípios o IVS
com três casas decimais e a "CATEGORIA IVS" derivada dele. O arquivo foi
preservado em `data/raw/aquisicao/ivs_regra/pmmb_2026_quadro_de_vagas.xlsx`, com
URL e SHA-256 no manifesto
[`a07_manifesto_ivs_administrativo.json`](../../output/aquisicao/a07_manifesto_ivs_administrativo.json).

A pista veio da série histórica de bolsistas ativos
(`data/pmm_especialistas_serie_historica.csv`): o rótulo de IVS de cada município
nunca muda entre competências e determina a faixa. O rótulo, porém, só existe para
municípios que tiveram bolsista, o que o condiciona ao desfecho; ele serviu de
conferência, não de base.

## 2. R1 — a regra é reproduzida em 100% dos casos

A regra é a do item 11.2 do Edital SGTES/MS nº 28/2026, com os cortes das
categorias do Atlas aplicados ao IVS administrativo:

| IVS administrativo | Categoria | Faixa | Bolsa anunciada |
|---|---|---|---:|
| até 0,300 | baixa ou muito baixa | 3 | R$ 10 mil |
| 0,301 a 0,400 | média | 2 | R$ 15 mil |
| acima de 0,400 | alta ou muito alta | 1 | R$ 20 mil |

- **Reprodução:** 4.103 de 4.103 combinações município–onda–versão, nas oito
  versões das cinco ondas de oferta (2025: ciclo 1, chamadas 1 e 2; 2026: ciclo 2,
  chamadas 1 e 2; ciclo 3, chamada 1). Nenhum município tem mais de uma faixa na
  mesma onda.
- **Categoria:** a categoria publicada no quadro do PMMB coincide com a
  recalculada pelos cortes em 5.571 de 5.571 municípios.
- **Rótulo da série:** coincide com a categoria administrativa nos 531 municípios
  em que existe.
- **O texto de 2025 não era a regra aplicada.** O FAQ do Chamamento nº 3/2025
  dizia Faixa 1 para muito alta e Faixa 2 para alta. Aplicado ao mesmo IVS, ele
  acerta 202 dos 368 municípios de 2025. A regra efetiva desde 2025 é a que o
  edital de 2026 escreve.
- **O IVS administrativo não é o IVS 2010.** Só 38 dos 5.565 valores são idênticos;
  a correlação é 0,851 e a categoria coincide em 2.999 municípios. A safra não é
  publicada nem pelo quadro nem pelo edital do PMMB.

### Três consequências para documentos anteriores

1. **Não há variação temporal da bolsa.** Nenhum município mudou de faixa entre
   qualquer par de ondas (dez pares, até 369 municípios em comum) nem entre
   versões retificadas da mesma chamada. A "Alternativa B" de
   [`16_sintese_achados_e_novo_plano_causal.md`](../05_identificacao/16_sintese_achados_e_novo_plano_causal.md),
   diferença-em-diferenças pela mudança de grade entre 2025 e 2026, não tem
   tratamento a explorar: mudou o texto, não a atribuição.
2. **O campo de faixa da série histórica diverge da regra em dez/2025 e
   jan/2026** (40 e 88 linhas), e coincide em todas as demais competências. Sem
   pagamento observado, isso não pode ser lido como mudança de valor recebido.
3. **A leitura de "piso" de 14/09 fica refutada.** O plano 14 leu a divergência
   unidirecional contra o IVS 2010 como um critério de localização do Anexo IV
   que promoveria municípios acima da categoria. Com o IVS administrativo, a
   categoria determina a faixa sozinha, sem nenhuma promoção. A divergência vinha
   da safra diferente e do mapeamento de 2026, já aplicado em 2025. O adicional
   da Lei 15.233 para Amazônia Legal e territórios indígenas não aparece nas
   faixas.

## 3. R2 — viável pelo desenho de continuidade, com ressalvas

Nenhum outcome foi lido. O tratamento é o salto de R$ 5 mil no valor anunciado em
0,300/0,301 (R$ 10 mil → R$ 15 mil) e em 0,400/0,401 (R$ 15 mil → R$ 20 mil). Os
cortes 0,200 e 0,500 mudam a categoria sem mudar a bolsa e funcionam como placebos.
A população de balanço são os 1.144 municípios ofertados em alguma onda.

### Suporte (banda 0,050)

| Corte | Ofertados à esquerda | Ofertados à direita | Pontos de massa (esq./dir.) |
|---|---:|---:|---:|
| 0,300 | 179 | 139 | 50 / 49 |
| 0,400 | 129 | 153 | 46 / 46 |

### Critérios essenciais — todos aprovados nos dois cortes

| Critério | 0,300 | 0,400 |
|---|---|---|
| Seleção na oferta: probabilidade de o município ser ofertado (local-linear, p) | 0,336 | 0,764 |
| PMMB 2026 como cointervenção: elegibilidade, vaga e número de vagas de eSF (menor p) | 0,252 | 0,243 |
| Balanço de 13 covariadas pré-tratamento, local-linear com Holm (p ajustado mínimo) | 0,260 | 0,233 |
| Composição da oferta: ondas, células, vagas, cursos (menor p) | 0,454 | 0,143 |

### O critério que reprovou, e por que ele fica registrado

A primeira regra executada foi a de randomização local de Cattaneo, Titiunik e
Vazquez-Bare: a maior janela em que **cada** covariada tem p ≥ 0,15, nela e nas
menores. Ela **reprova os dois cortes** — nenhuma janela passa. O teste conjunto,
pela permutação do máximo |t| entre covariadas, só balanceia em janelas mínimas
(±0,010 em 0,300 tem p = 0,42, mas ±0,005 tem 0,08; em 0,400, só ±0,005, com 15 e
16 municípios).

A leitura é que a hipótese de randomização local não se sustenta com suporte útil,
porque as covariadas ligadas ao IVS 2010 variam com o IVS administrativo dentro da
janela. O teste local-linear, que modela essa inclinação, separa inclinação de
salto e não encontra descontinuidade conjunta. Por isso **o estimador principal
candidato passa a ser local-linear**, e a randomização local fica como
complemento descritivo. A mudança foi decidida antes de qualquer outcome e o
resultado da regra estrita permanece no artefato.

### Ressalvas

- **Covariadas isoladamente desbalanceadas.** Em 0,300, `capital` (há capitais logo
  abaixo do corte e nenhuma logo acima); em 0,400, o IVS capital humano 2010.
  O placebo 0,200 sinaliza o IVS 2010 na mesma proporção, o que é compatível com
  acaso entre 13 testes. O protocolo deve ajustar por essas covariadas ou excluir
  capitais em robustez.
- **Potência.** O MDE para uma proporção municipal com linha de base de 30% é de
  31,5 p.p. em 0,300 e 32,9 p.p. em 0,400 na banda 0,050; combinando os dois cortes
  (mesma dose de R$ 5 mil), 22,8 p.p. na banda 0,050 e 16,5 p.p. na 0,100. Com
  município como unidade, só efeitos grandes são detectáveis. Município–onda ou
  célula como unidade, com agrupamento municipal, é a forma de reduzir o MDE, e é
  decisão do protocolo.
- **Estoque prévio de especialistas** não entrou no balanço: o bruto do CNES não
  está neste ambiente.
- **Safra do IVS administrativo** não documentada. A regra é reproduzida; a origem
  do escore, não.

## 4. O que isto autoriza e o que não autoriza

**Autoriza:** escrever e congelar um protocolo R3 para a RDD da bolsa com o IVS
administrativo. O rascunho está em
[`18_protocolo_r3_rdd_bolsa_rascunho.md`](../05_identificacao/18_protocolo_r3_rdd_bolsa_rascunho.md).

**Não autoriza:** abrir qualquer outcome por faixa ou por IVS administrativo antes
do congelamento; chamar de causal qualquer resultado anterior; tratar o pedido
administrativo D-3 como pré-condição do R1 (deixou de ser). O controlador
`02_controlar_execucao_plano_causal.py` bloqueia resultado R4 sem registro R3.
