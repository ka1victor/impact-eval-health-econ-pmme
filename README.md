# Programa Mais Médicos Especialistas (PMM-E): Avaliação de Impacto e Eficiência em Saúde

> **Pacote de Replicação e Avaliação Causal** do componente de provimento especializado da Política Nacional de Atenção Especializada em Saúde — Programa *Agora Tem Especialistas* (Lei Federal nº 15.233/2025).

---

> [!WARNING]
> ### Definição Explicitamente Preliminar de Escopo
> Esta formulação constitui uma definição **explicitamente preliminar e viva do escopo de pesquisa**, fixada a partir dos primeiros ciclos de microdados federais (2025/2026), sujeita a refinamentos e aprofundamentos metodológicos adicionais conforme novas competências e diretrizes normativas forem incorporadas.

---

## 1. Problema de Política Pública e Motivação Oficial

* **Nome e Base Legal:** *Programa Mais Médicos Especialistas (PMM-E)* / *Agora Tem Especialistas* (Lei nº 15.233/2025 e Editais SGTES/MS nº 3/2025 e 6/2026).
* **Período de Execução:** Ciclos de 2025 e 2026 com acompanhamento de microdados mensais de provimento ativo.
* **Objetivos Oficiais (Art. 2º da Lei nº 15.233/2025):**
  1. **Redução de Filas e Tempo de Espera:** Acelerar o diagnóstico e o início do tratamento em 6 áreas prioritárias (oncologia, ginecologia, cardiologia, cirurgia geral, ortopedia e oftalmologia/otorrino);
  2. **Superação de Vazios Assistenciais:** Fixar profissionais em regiões de média e alta vulnerabilidade social sem oferta médica especializada;
  3. **Integralidade do Cuidado:** Realizar consultas, exames diagnósticos precoces (biópsias, mamografias, endoscopias) e cirurgias eletivas resolutivas localmente, evitando o agravamento clínico do paciente.
* **Estrutura Salarial:** Escalonamento federal das bolsas pelo Índice de Vulnerabilidade Social (IVS 2010 do IPEA):
  * **R\$ 10.000/mês** para Faixa 3 (Baixa/Média Vulnerabilidade: $IVS \le 0{,}300$);
  * **R\$ 15.000/mês** para Faixa 2 (Alta Vulnerabilidade: $0{,}300 < IVS \le 0{,}400$, salto de **+50,0%**);
  * **R\$ 20.000/mês** para Faixa 1 (Muito Alta Vulnerabilidade: $IVS > 0{,}400$, salto de **+33,3%**).
* **Dilema Econômico de Política Pública:** Vale mais a pena para o SUS pagar um incentivo financeiro para fixar o especialista no interior ou continuar bancando o transporte sanitário (vans e ambulâncias) de pacientes até os grandes centros? Qual é o piso de incentivo financeiro ótimo para atrair o médico sem gerar sobrepreço aos cofres públicos?
* **Pergunta de Pesquisa Central:** *Quais os efeitos do Programa Mais Médicos Especialistas sobre os outcomes de saúde dos pacientes e sobre os gastos dos municípios?*

---

## 2. Desenho Empírico (Identificação Causal)

* **Método (RDD):** Regressão Descontínua no primeiro corte de bolsa do programa: cidades com $IVS \le 0{,}300$ recebem R\$ 10k/mês e cidades com $IVS > 0{,}300$ recebem R\$ 15k/mês (+50%).
* **Identificação Causal:** O IVS foi calculado pelo IPEA no Censo de 2010 (14 anos antes da criação do programa), sendo imune a manipulação política por prefeitos. Cidades vizinhas ao corte (ex.: $IVS = 0{,}299$ vs. $0{,}301$) são socioeconomicamente idênticas, mudando apenas a remuneração federal.
* **Validação:** A densidade de municípios em torno do corte é contínua e equilibrada (sem *bunching*), e testes de placebo em cortes falsos ($IVS = 0{,}250$ e $0{,}350$) apresentam efeitos estritamente nulos ($p > 0{,}55$).

---

## 3. Evidências Empíricas Robustas (Logo Acima vs. Logo Abaixo do Corte)

| Dimensão Avaliada | Logo Abaixo ($IVS \le 0{,}300$, R\$ 10k) | Logo Acima ($IVS > 0{,}300$, R\$ 15k) | Efeito Causal Líquido (Salto no Corte) |
|---|:---:|:---:|:---:|
| **1. Atração Médica** | 48,0% de preenchimento | 83,5% de preenchimento | **+35,5 p.p.** ($\varepsilon = 1{,}48$, $p < 0{,}0001$) |
| **2. Resolutividade Local** | 38,0% retido na cidade | 72,0% retido na cidade | **+34,0 p.p.** ($p = 0{,}0165$) |
| **3. Outcomes de Saúde (SIA/SIH)** | Vacância de 52% e fila regional | Atendimento e biópsia no hospital local | **Dobro de exames locais e substituição de urgências por cirurgias eletivas** |
| **4. Economia de Gastos** | Gasto contínuo com transporte | 140 viagens de van evitadas/mês | **Razão Benefício-Custo de 2,4x** (saldo de +R\$ 6,9 mil/mês por município) |

---

## 4. Os 4 Achados Inesperados e Contra-Intuitivos

1. **O Colapso da Elasticidade Salarial (Pagar R\$ 20k não atrai muito mais que R\$ 15k):**
   * Pagar R\$ 20k/mês tem retorno marginal quase nulo (+9,1 p.p., $\varepsilon = 0{,}31$) comparado ao primeiro degrau (+35,5 p.p., $\varepsilon = 1{,}48$). Acima de R\$ 15k/mês, o gargalo deixa de ser salário e vira infraestrutura física, isolamento geográfico e escolas para os filhos dos médicos.
2. **O Paradoxo da Retenção (Cidades de R\$ 20k perdem médicos mais rápido):**
   * Cidades com a maior bolsa (R\$ 20k) perdem médicos mais rápido aos 6 meses ($\tau = -4{,}4\text{ p.p.}$, $p = 0{,}013$) pela precariedade extrema de condições de trabalho em municípios com $IVS > 0{,}400$ sem suporte diagnóstico básico.
3. **A Ausência de Demanda Induzida por Médicos:**
   * O programa gerou **substituição geográfica quase pura**: a realização de exames locais aumentou exatamente na mesma proporção em que as viagens para fora caíram, sem inflar artificialmente o volume total per capita de exames supérfluos.
4. **O Gargalo Oculto do SUS (O problema não era prédio, era Anestesista):**
   * A chave mestra do programa foi a alocação de **384 anestesiologistas (>25% do total)**, que destravaram centros cirúrgicos municipais preexistentes que estavam ociosos e paralisados por falta do profissional habilitado.

---

## 📁 Estrutura do Repositório

```
impact-eval-health-econ-pmme/
├── README.md                                    <- Síntese estruturada do paper e evidências
├── LICENSE                                      <- Licença MIT
├── requirements.txt                             <- Dependências Python (numpy, scipy, pandas)
├── .gitignore                                   <- Filtro de arquivos temporários e caches
├── run_all.py                                   <- Executa o pipeline completo em ~30 segundos
├── CLAUDE.md & AGENTS.md                        <- Diretrizes metodológicas e governança
├── TODO.md                                      <- Fila de pesquisa e próximos passos
├── docs/
│   ├── 01_dossie_e_motivacao_politica_publica.md <- Base normativa (Lei 15.233), IVS e achados
│   ├── 02_resultados_rdd_e_elasticidades.md      <- Tabelas completas de RDD no 1º estágio e placebos
│   ├── 03_resolutividade_local_vs_global.md     <- Decomposição SIA/SIH de fluxo e retenção
│   ├── 04_auditoria_financeira_e_custo_beneficio.md <- Avaliação de custos, SIOPS e BCR de 2,4x
│   ├── 05_agora_tem_especialistas_e_teleconsulta.md <- OCI Grupo 09 e teleconsulta (beta = -0,11)
│   └── 06_metodologia_e_limitacoes.md           <- Regras econométricas, proveniência e defesas
├── data/
│   ├── pmm_especialistas_nominal.csv            <- 1.480 médicos ativos em 325 municípios
│   ├── pmm_especialistas_serie_historica.csv    <- 7.276 registros mensais (2025-2026)
│   ├── ivs_ipea_2010_municipios.csv             <- 5.565 municípios do IPEA
│   └── geo8_pmm_resolutividade_painel_municipios.csv <- Painel compilado de fluxo municipal
├── scripts/
│   ├── 01_estima_rdd_completo.py                <- Motor econométrico de primeiro estágio
│   ├── 02_estima_resolutividade_local_global.py <- Motor de fluxo e resolutividade SIA/SIH
│   ├── 03_analise_descritiva_pacientes.py       <- Tabelas clínicas e horas de viagem poupadas
│   └── 04_teste_teleconsulta_e_grupo09.py       <- Validação de teleconsulta e Grupo 09
└── output/
    ├── geo8_pmm_especialistas_rdd_completo.json <- Resultados numéricos do RDD
    ├── geo8_pmm_resolutividade_global_local_resultados.json <- Decomposição de resolutividade
    ├── geo8_pmm_descritiva_pacientes.json       <- Relatório clínico detalhado
    └── geo8_pmm_descritiva_tabela_pacientes.csv <- Tabela descritiva por domínio clínico
```

---

## 🚀 Como Reproduzir os Resultados

Para executar todo o pipeline econométrico de ponta a ponta:

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Executar o pipeline completo (3 etapas em ~30s)
python run_all.py
```
