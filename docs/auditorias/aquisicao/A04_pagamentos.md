# A04 — Regras financeiras e pagamentos públicos

> **Adendo prospectivo de 30/08/2026:** a Nota Técnica nº
> 59/2026-CGPLAD/DEGEPS/SGTES/MS definiu vínculo `070102`, CNPJ de detalhamento
> do Ministério da Saúde, CBO e cargas horárias para registrar bolsistas PMM-E
> no CNES. Essa combinação pode funcionar como ponte pública no ciclo 3, mas
> ainda precisa ser observada e reconciliada com as alocações. Ela não revela
> pagamentos devidos ou realizados e, portanto, não altera a conclusão
> financeira histórica abaixo.

## Resultado

A A04 observa **parcialmente o valor anunciado**, como regra normativa, e não
observa o valor devido ou recebido por profissional, vaga, CNES e competência.
Também não preservou uma resposta oficial reproduzível de execução orçamentária
que permita publicar valores exatos de empenho, liquidação ou pagamento.

Consequentemente, esta frente **não identifica efeito causal nem primeiro estágio
financeiro**. Ela apenas delimita qual versão do tratamento financeiro pode ser
medida com a evidência atual.

## 1. Evidência monetária efetivamente preservada

O único documento local que contém uma grade monetária explícita é o
[FAQ oficial do Chamamento Público SGTES/MS nº 3/2025](https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2025/chamamento-publico-sgtes-ms-no-3-2025-pmm-e/faq/qual-o-valor-da-bolsa-formacao).
Seu HTML oficial está preservado em
`data/raw/aquisicao/ivs_regra/edital_sgtes_03_2025_faq_bolsa.html`, com SHA-256
`a6ff2d5597286176153fc73c986028cd30b98f91667f5c3019d2fa804505a31f`.

O script extrai diretamente do bloco `div#form-widgets-resposta`:

| Faixa declarada | Categoria declarada no FAQ | Valor mensal anunciado |
|---:|---|---:|
| 1 | muito alta vulnerabilidade | R$ 20.000,00 |
| 2 | alta vulnerabilidade | R$ 15.000,00 |
| 3 | média, baixa ou muito baixa vulnerabilidade | R$ 10.000,00 |

O mesmo bloco informa que o pagamento está condicionado à participação efetiva
nas atividades e à regularidade no curso. Por isso, a tabela comprova uma
**oferta normativa anunciada**, não o direito apurado em cada competência nem o
crédito efetivamente recebido.

Cada linha do arquivo `output/aquisicao/a04_grade_anunciada_2025.csv` registra
documento, URL, arquivo local, hash e localizador da evidência. As páginas
oficiais de 2026 preservadas localmente não expõem uma grade monetária verificável
no HTML adquirido. Nenhum valor exato de 2026 é inferido ou replicado.

## 2. Separação dos estágios financeiros

| Estágio | O que representa | Estado na A04 | O que não se pode concluir |
|---|---|---|---|
| **Anunciado** | Valor informado na oferta normativa | Parcialmente observado para o Chamamento nº 3/2025 | Que uma vaga foi preenchida ou que o participante recebeu esse valor |
| **Devido** | Obrigação apurada para profissional e competência após as regras aplicáveis | Não observado | Que o anunciado seja integralmente devido em todos os meses |
| **Empenhado** | Crédito comprometido por documento de empenho | Não adquirido em resposta oficial reproduzível | Qualquer total exato ou sua atribuição ao PMM-E |
| **Liquidado** | Despesa reconhecida após verificação do direito do credor | Não adquirido em resposta oficial reproduzível | Que o empenhado corresponda a serviço validado de determinado participante |
| **Pago** | Desembolso registrado para favorecido | Não observado com chave defensável do PMM-E | Ligação a profissional, vaga, CNES e competência |

Esta separação impede transformar despesa agregada em “dose média”, confundir
regra com transferência ou preencher lacunas com hipóteses sobre permanência,
frequência, glosas e retroativos.

## 3. Execução orçamentária: correção de proveniência

A versão anterior da A04 publicava valores exatos de dotação, empenho,
liquidação e pagamento a partir de constantes digitadas no script. Não existia
resposta oficial correspondente com endpoint, consulta, filtros, exercício,
posição temporal e hash.

Esses valores e o arquivo derivado foram removidos. O manifesto agora registra
separadamente as consultas insuficientes:

- [SIOP](https://www.siop.planejamento.gov.br/): não há resposta local,
  endpoint, parâmetros ou filtros reproduzíveis;
- [Portal da Transparência — pagamentos](https://portaldatransparencia.gov.br/despesas/pagamentos):
  não há resposta local que isole o PMM-E e ligue simultaneamente profissional,
  vaga, CNES e competência;
- folha individual PMM-E: não foi localizada publicação oficial aberta com as
  chaves e campos necessários.

Logo, a A04 atual não publica totais orçamentários exatos. Uma aquisição futura
só poderá adicioná-los se preservar a resposta oficial original e documentar a
consulta completa.

## 4. Fontes normativas catalogadas e limites

O catálogo derivado `output/aquisicao/a04_normas_regras_financeiras_pmme.json`
registra URLs exatas, versões, caminhos e hashes de quatro fontes oficiais já
preservadas por A03:

- FAQ oficial do Chamamento SGTES/MS nº 3/2025;
- Lei nº 15.233/2025;
- página do Chamamento SGTES/MS nº 1/2026;
- página do Edital SGTES/MS nº 28/2026.

Catalogar uma página não equivale a extrair dela determinada regra. Na versão
atual, somente o FAQ de 2025 é usado como evidência de valores monetários. As
páginas de 2026 permanecem catalogadas, mas não sustentam números exatos nos
artefatos A04.

A A04 também deixou de atribuir ao SGP ou a outros sistemas nomes de campos
internos, regras de fechamento de folha ou fluxos operacionais sem documentação
oficial preservada.

## 5. Tratamentos candidatos

### Faixa anunciada

**Mensurável parcialmente como regra de 2025.** É uma característica da oferta
normativa. Não mede participação, exposição continuada ou dose monetária.

### Valor devido

**Não mensurável com os dados atuais.** Exigiria registros mensais que permitam
apurar o direito do participante segundo entrada, permanência e eventuais
ajustes. Esses registros não foram obtidos.

### Valor recebido

**Não mensurável com os dados atuais.** Não há microdados oficiais abertos com
valor pago e chave comum de profissional, vaga, CNES e competência.

## 6. Produtos e reprodução

O comando:

```powershell
python scripts/aquisicao/a04_adquirir_pagamentos.py
```

gera deterministicamente:

- `output/aquisicao/a04_grade_anunciada_2025.csv`;
- `output/aquisicao/a04_normas_regras_financeiras_pmme.json`;
- `output/aquisicao/a04_manifesto_pagamentos.json`;
- `output/aquisicao/a04_matriz_dose_financeira.json`.

Não há bruto A04 em `data/raw/aquisicao/pagamentos/`: nenhuma resposta financeira
oficial nova foi obtida. Os HTMLs oficiais reutilizados permanecem no diretório
de aquisição normativa de A03, e seus hashes são verificados a cada execução.

## 7. Veredito para integração

```text
Faixa anunciada de 2025:         OBSERVÁVEL PARCIALMENTE COMO REGRA NORMATIVA
Faixa anunciada de 2026:         NÃO CONFIRMADA PELA EXTRAÇÃO LOCAL ATUAL
Valor devido por competência:    NÃO OBSERVADO
Empenhado e liquidado:           NÃO ADQUIRIDOS EM RESPOSTA REPRODUZÍVEL
Valor recebido por participante: NÃO OBSERVADO COM VÍNCULO A VAGA/CNES
Efeito causal financeiro:        NÃO IDENTIFICADO
```

A04 está saneada quanto à proveniência, mas a mensuração da dose financeira
efetiva continua bloqueada por ausência de dados administrativos adequados.
