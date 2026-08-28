# Relatorio de Auditoria A03 - IVS e Regra Administrativa do Tratamento

> **Data da Auditoria:** 28 de agosto de 2026 (revisado pós-saneamento)
> **Autor:** Agente A03 (Sprint de Aquisicao de Dados / Saneamento A05R)
> **Escopo:** Documentacao normativa, auditoria do IVS 2010 IPEA e avaliacao de viabilidade do desenho RDD no PMM-E (Lei 15.233/2025).
> **Outputs:** `data/raw/aquisicao/ivs_regra/`, `output/aquisicao/a03_manifesto_ivs_regra.json`, `output/aquisicao/a03_matriz_regra_tratamento.json`.

---

## 1. Sumario Executivo

A presente auditoria investigou a cadeia normativa e empirica da categorizacao de vulnerabilidade e atribuicao de faixas no PMM-E.

### Principais Conclusoes:
1. **IVS nao determina participacao:** Depende de adesao municipal, pactuacao CIB e capacidade instalada CNES. O IVS atua apenas na faixa de bolsa anunciada.
2. **Divergencia de 42,56% com IVS 2010 local:** Dos 531 municipios na serie historica, 305 (57,44%) coincidem com os cutoffs do Atlas do IPEA e 226 (42,56%) divergem. Esta divergencia e compativel com multiplas explicacoes (vintagem distinta, regras de precisao/arredondamento, reclassificacoes administrativas ou erro cadastral), nao demonstrando por si so regra multicriterio.
3. **Instabilidade temporal na definicao de faixas:** A Faixa 2 em 2025 (Alta) virou Faixa 1 em 2026, enquanto a Faixa 3 em 2025 (Media/Baixa) virou Faixa 2 em 2026.
4. **Quatro Pilares do RDD:** Cutoff normativo nao confirmado internamente; Escore por vaga ausente nas bases publicas; 1o estagio anunciado deterministico condicional a categoria textual mas nao ao IVS continuo; 1o estagio recebido nao observado.
5. **Veredito:** Sharp RDD e inviavel e indefensavel. Fuzzy RDD e inviavel hoje e estritamente condicionado a dados administrativos futuros via LAI.

---

## 2. Base Normativa Preservada e Catalogada

### 2.1 Documentos Brutos Preservados Localmente (`data/raw/aquisicao/ivs_regra/`)

| ID | Descricao | Orgao | Natureza | Arquivo Preservado | SHA-256 (prefixo) |
|---|---|---|---|---|:---:|
| `lei_15233_2025` | Lei 15.233/2025 - Altera a Lei 12.871/2013 e institui o PMM-E | Presidencia da Republica / SG | Lei Federal | `lei_15233_2025.html` | `d53e7877fe` |
| `edital_sgtes_02_2025_gestores` | Chamamento Publico SGTES/SAES 02/2025 - Adesao e oferta | Ministerio da Saude / SGTES / SAES | Edital de Adesao | `edital_sgtes_02_2025_gestores.html` | `2fef58c438` |
| `edital_sgtes_03_2025_faq_bolsa` | FAQ Oficial Chamamento SGTES/MS 3/2025 - Bolsas 2025 | Ministerio da Saude / SGTES | Documentacao de Bolsa | `edital_sgtes_03_2025_faq_bolsa.html` | `a6ff2d5597` |
| `edital_sgtes_01_2026_ciclo2` | Chamamento Publico SGTES/MS 01/2026 - Ciclo 2 | Ministerio da Saude / SGTES | Edital de Selecao | `edital_sgtes_01_2026_ciclo2.html` | `90b95c902f` |
| `edital_sgtes_05_2026_adesao_ciclo3` | Chamamento Publico SGTES/MS 05/2026 - Adesao Ciclo 3 | Ministerio da Saude / SGTES | Edital de Adesao | `edital_sgtes_05_2026_adesao_ciclo3.html` | `38687fbfb2` |
| `edital_sgtes_06_2026_edital_28_2026_ciclo3` | Edital SGTES/MS 28/2026 - Selecao Ciclo 3 | Ministerio da Saude / SGTES | Edital de Selecao | `edital_sgtes_06_2026_edital_28_2026_ciclo3.html` | `eb1e07b444` |

### 2.2 Documentos Normativos e Metodologicos Externos Catalogados

| ID | Descricao | Orgao | Natureza | URL Oficial | Status no Manifesto |
|---|---|---|---|---|:---:|
| `portaria_gm_ms_7177_2025` | Portaria GM/MS 7.177/2025 - Institui o PMM-E | MS / GM | Portaria | [BVSMS](https://bvsms.saude.gov.br/bvs/saudelegis/gm/2025/prt7177_11_06_2025.html) | Catalogado sem bruto local (conexao BVSMS instavel) |
| `portaria_gm_ms_7266_2025` | Portaria GM/MS 7.266/2025 - Programa Agora Tem Especialistas | MS / GM | Portaria | [BVSMS](https://bvsms.saude.gov.br/bvs/saudelegis/gm/2025/prt7266_18_06_2025.html) | Catalogado sem bruto local (conexao BVSMS instavel) |
| `ipea_atlas_vulnerabilidade_social_2015` | Atlas da Vulnerabilidade Social (Ipea, 2015) | IPEA | Relatorio Metodologico | [IPEA](https://repositorio.ipea.gov.br/bitstream/11058/4381/1/Atlas_da_vulnerabilidade_social_nos_municipios_brasileiros.pdf) | Referencia externa; microdados em `data/ivs_ipea_2010_municipios.csv` |

---

## 3. Avaliacao dos Quatro Pilares do RDD

### PILAR A CUTOFF NORMATIVO
- **Status:** NAO_CONFIRMADO_NO_PMM_E
- **Evidencia:** Os editais citam categorizacao do IVS mas nao publicam algoritmo numerico de corte nem equacao de arredondamento.
- **Detalhes:** Os cutoffs 0.200, 0.300, 0.400, 0.500 sao da taxonomia externa do Atlas do Ipea (2015), nao regra explicita do PMM-E.

### PILAR B ESCORE ADMINISTRATIVO POR VAGA
- **Status:** AUSENTE_NAS_BASES_PUBLICAS
- **Evidencia:** Nenhum quadro de vagas publica a variavel corrida numerica (escore continuo) usada pelo Ministerio.
- **Detalhes:** As tabelas publicam apenas a categoria ou a faixa ordinal discreta (Faixa 1, 2, 3), impedindo reconstrucao exata da running variable.

### PILAR C PRIMEIRO ESTAGIO VALOR ANUNCIADO
- **Status:** DETERMINISTICO_CONDICIONAL_A_CATEGORIA_TEXTUAL
- **Evidencia:** 100 por cento de correspondencia entre categoria textual e Faixa anunciada; valor anunciado e funcao exata da faixa no edital.
- **Detalhes:** Salto anunciado de +R$ 5.000 ou +R$ 10.000 e deterministico condicionalmente a categoria textual, mas nao ao IVS continuo local.

### PILAR D PRIMEIRO ESTAGIO VALOR RECEBIDO
- **Status:** NAO_OBSERVADO_AGUARDANDO_DADOS_ADMINISTRATIVOS
- **Evidencia:** Folha de pagamento mensal individualizada nao esta disponivel publicamente.
- **Detalhes:** Nao e possivel verificar glosas, suspensoes, adicionais de imersao, ajuda de custo ou se participantes de 2025 migraram de valor em 2026.

---

## 4. Auditoria Empirica: IVS 2010 vs. Categoria Textual Observada

- **Total de municipios auditados na serie:** 531
- **Concordantes com IVS 2010:** 305 [57.44%]
- **Divergentes de IVS 2010:** 226 [42.56%]

### Deslocamentos de Rank Observados:
- shift_-2: 2 municipios
- shift_-1: 102 municipios
- shift_0: 305 municipios
- shift_1: 111 municipios
- shift_2: 11 municipios

### Matriz de Transicao Completa [Calculada vs. Textual]:

| Categoria Calculada | Muito Baixa | Baixa | Media | Alta | Muito Alta | Total |
|---|---:|---:|---:|---:|---:|---:||
| **MUITO BAIXA VULNERABILIDADE** | 17 | 7 | 0 | 0 | 0 | 24 |
| **BAIXA VULNERABILIDADE** | 31 | 91 | 22 | 4 | 0 | 148 |
| **MEDIA VULNERABILIDADE** | 2 | 57 | 121 | 54 | 7 | 241 |
| **ALTA VULNERABILIDADE** | 0 | 0 | 14 | 49 | 28 | 91 |
| **MUITO ALTA VULNERABILIDADE** | 0 | 0 | 0 | 0 | 27 | 27 |
| **All** | 50 | 155 | 157 | 107 | 62 | 531 |

---

## 5. Auditoria da Consistencia nos Quadros de Vagas

### Quadro: 1_2_cadastro_reserva
- Total de linhas: 1762
- Total de municipios: 507
- Municipios com faixa 100% unica: 507
- Municipios com multiplas faixas: 0

### Quadro: 2_1_vagas_retificadas
- Total de linhas: 1547
- Total de municipios: 454
- Municipios com faixa 100% unica: 454
- Municipios com multiplas faixas: 0

### Quadro: 2_2_vagas_reserva
- Total de linhas: 1039
- Total de municipios: 369
- Municipios com faixa 100% unica: 369
- Municipios com multiplas faixas: 0

### Quadro: 3_1_vagas_retificadas
- Total de linhas: 2293
- Total de municipios: 748
- Municipios com faixa 100% unica: 748
- Municipios com multiplas faixas: 0

---

## 6. Classificacao do Contraste Causal e Viabilidade de RDD

- **Tipo de Contraste:** INCENTIVO_MARGINAL_ANUNCIADO_COM_REGRA_NAO_RECONSTRUIDA
- **Justificativa:** O IVS nao determina participacao no PMM-E nem criacao de vagas. Condicionalmente a vaga ofertada, a categoria administrativa define o valor anunciado. Como o escore continuo e a regra exata nao foram publicados e 42,56% dos municipios divergem do recálculo com o IVS 2010 local (o que é compatível com diferentes vintagens, arredondamentos ou erros cadastrais), a regra administrativa exata não pôde ser reconstruída e o contraste não pode ser estimado por RDD sharp.
- **Viabilidade RDD:** INVIAVEL_COM_DADOS_PUBLICOS_ATUAIS

### Condicoes Necessarias para Futuro RDD Fuzzy:
- Acesso a tabela de escore administrativo continuo exato usado pela SGTES/MS
- Microdados mensais de pagamentos efetivos (SGP/FNS) para estimar primeiro estagio
- Identificador estavel de vaga para controlar processo de oferta e remanejamento

---

## 7. Recomendacoes para Agentes A06 e A07

1. **Para A06 [Integracao]:** Bloquear Sharp RDD com IVS 2010. Manter `faixa_atracao` apenas para estratificacao descritiva.
2. **Para A07 [LAI/Pedidos]:** Requisitar memoria de calculo continua e escores da SGTES/MS e folha de pagamentos FNS/SGP.