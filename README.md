# Programa Mais Médicos Especialistas (PMM-E): Avaliação de Impacto e Eficiência em Saúde

> **Repositório dedicado e autocontido** para a avaliação econométrica causal do Programa Mais Médicos Especialistas (Lei nº 15.233/2025 — *Agora Tem Especialistas*).
> 
> Todos os dados, scripts e documentos deste tema estão centralizados nesta pasta.

---

## 🎯 Síntese do Projeto

* **Pergunta Central:** *Quais os efeitos do Programa Mais Médicos Especialistas sobre os outcomes de saúde dos pacientes e sobre os gastos dos municípios?*
* **Motivação:** Vale mais a pena para o SUS pagar um incentivo financeiro para fixar o médico especialista no interior ou continuar bancando o transporte sanitário de pacientes (vans e ambulâncias) até os polos regionais?
* **Desenho Empírico:** Regressão Descontínua (**RDD**) explorando a regra federal de remuneração das bolsas escalonada pelo Índice de Vulnerabilidade Social (**IVS 2010 do IPEA**):
  $$\text{Bolsa}(IVS_m) = \begin{cases} 
  \text{R\$ } 10.000/\text{mês} & \text{se } IVS_m \le 0{,}300 \quad (\text{Baixa / Média Vulnerabilidade}) \\
  \text{R\$ } 15.000/\text{mês} & \text{se } 0{,}300 < IVS_m \le 0{,}400 \quad (\text{Alta Vulnerabilidade, }+50{,}0\%) \\
  \text{R\$ } 20.000/\text{mês} & \text{se } IVS_m > 0{,}400 \quad (\text{Muito Alta Vulnerabilidade, }+33{,}3\%)
  \end{cases}$$
* **Identificação Causal:** O IVS 2010 foi calculado pelo IPEA no Censo de 2010 (14 anos antes da criação dos editais), sendo perfeitamente contínuo, universal para os 5.565 municípios e imune a manipulação por prefeitos.

---

## 📊 Principais Resultados Empíricos

1. **Atração Médica e Elasticidade-Salário (Nota 02):**
   * Salto de **+35,5 p.p.** no preenchimento imediato de vagas no corte de R\$ 10k $\to$ R\$ 15k ($48{,}0\% \to 83{,}5\%$, $t = +136{,}2$, $p < 0{,}0001$).
   * A oferta de especialistas é **fortemente elástica no 1º salto ($\varepsilon_1 = 1{,}48$)** e **colapsa para inelástica no 2º salto ($\varepsilon_2 = 0{,}31$)**.
2. **Resolutividade Local e Outcomes de Saúde (Nota 03):**
   * Salto de **+34,0 p.p.** na resolutividade local ($38\% \to 72\%$), retendo o cuidado dentro do próprio município.
   * Municípios logo acima do corte realizam **quase o dobro de biópsias e exames preventivos locais** em relação aos vizinhos logo abaixo (que sofrem com vacância de 52%), **substituindo internações de urgência na capital por cirurgias eletivas programadas no hospital municipal**.
   * Entrega de **97 mil consultas** e **162 mil exames diagnósticos/mês** no interior (51 mil de saúde da mulher e 24 mil colonoscopias/endoscopias).
3. **Análise Custo-Benefício e Gastos Públicos (Nota 04):**
   * **Razão Benefício-Custo Direta de 2,4x**: O aumento de R\$ 5.000/mês na bolsa federal evita ~140 viagens de van/mês, economizando R\$ 11.900/mês em transporte sanitário e gerando um saldo líquido positivo de **R\$ 6,9 mil/mês por município**.
   * Incorporando os ganhos clínicos de diagnósticos precoces (~112 QALYs/ano por especialista), a Razão Benefício-Custo Social Ampliada atinge **95,4x**.

---

## 💡 Os 4 Achados Inesperados e Contra-Intuitivos

1. **O Colapso da Elasticidade Salarial:** Pagar R\$ 20k/mês não atrai muito mais que R\$ 15k (+9,1 p.p. de ganho marginal), pois o gargalo acima de R\$ 15k deixa de ser salário e vira infraestrutura física, isolamento e escolas para os filhos.
2. **O Paradoxo da Retenção:** Cidades com a maior bolsa (R\$ 20k) perdem médicos mais rápido aos 6 meses ($\tau = -4{,}4\text{ p.p.}$) pela precariedade extrema de condições de trabalho em municípios com $IVS > 0{,}400$.
3. **A Ausência de Demanda Induzida:** O programa gerou **substituição geográfica quase perfeita** no SIA (3,77M linhas), sem inflar artificialmente o volume total per capita com exames supérfluos.
4. **O Gargalo Oculto do SUS:** O problema do interior não era construir novos hospitais, mas sim contratar **384 anestesiologistas**, que destravaram centros cirúrgicos municipais preexistentes que estavam ociosos.

---

## 📁 Estrutura da Pasta

```
mais_medicos_especialistas/
├── README.md                                    <- Este documento consolidado
├── docs/
│   ├── 01_dossie_e_motivacao_politica_publica.md <- Base legal, objetivos oficiais e escopo
│   ├── 02_resultados_rdd_e_elasticidades.md      <- Tabelas completas de primeiro estágio e RDD
│   ├── 03_resolutividade_local_vs_global.md     <- Decomposição SIA/SIH de fluxo e outcomes
│   └── 04_auditoria_financeira_e_custo_beneficio.md <- Avaliação de gastos, SIOPS e transporte
├── data/
│   ├── pmm_especialistas_nominal.csv            <- 1.480 médicos ativos em 325 municípios
│   ├── pmm_especialistas_serie_historica.csv    <- 7.276 registros mensais (2025-2026)
│   ├── ivs_ipea_2010_municipios.csv             <- 5.565 municípios com IVS 2010 oficial
│   └── geo8_pmm_resolutividade_painel_municipios.csv <- Painel compilado de fluxo SIA/SIH
├── scripts/
│   ├── 01_estima_rdd_completo.py                <- Motor econométrico de RDD e elasticidade
│   ├── 02_estima_resolutividade_local_global.py <- Motor de microdados de fluxo SIA e SIH
│   └── 03_analise_descritiva_pacientes.py       <- Tabelas descritivas clínicas e horas poupadas
└── output/
    ├── geo8_pmm_especialistas_rdd_completo.json <- Resultados numéricos completos do RDD
    ├── geo8_pmm_resolutividade_global_local_resultados.json <- Decomposição de resolutividade
    ├── geo8_pmm_descritiva_pacientes.json       <- Relatório clínico detalhado
    └── geo8_pmm_descritiva_tabela_pacientes.csv <- Tabela descritiva por domínio de saúde
```

---

## 🚀 Como Executar os Modelos

Para reproduzir todas as tabelas e estimativas econométricas:

```powershell
# 1. Estimação do RDD no Primeiro Estágio e Elasticidade-Salário:
python mais_medicos_especialistas/scripts/01_estima_rdd_completo.py

# 2. Decomposição de Resolutividade Local vs. Global (SIA e SIH):
python mais_medicos_especialistas/scripts/02_estima_resolutividade_local_global.py

# 3. Estatísticas Descritivas Clínicas de Atendimento ao Paciente:
python mais_medicos_especialistas/scripts/03_analise_descritiva_pacientes.py
```
