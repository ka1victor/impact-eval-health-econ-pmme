# 02. Resultados Econométricos de Primeiro Estágio e Elasticidade-Salário

> **Resumo dos Resultados:** Estimação do modelo de Regressão Descontínua (RDD) e Randomização Local com 2.000 permutações exatas de Fisher-Pitman e erros-padrão clusterizados no nível municipal.

---

## 1. Especificação Econométrica

Em torno de cada corte $c \in \{0{,}300; 0{,}400\}$ em janelas locais de largura $h \in [0{,}015; 0{,}030]$:

$$Y_{m,s} = \alpha + \tau \cdot \mathbf{1}(IVS_m > c) + f(IVS_m - c) + \gamma_s + \varepsilon_{m,s}$$

Onde:
* $Y_{m,s}$ é o desfecho da vaga da especialidade $s$ no município $m$;
* $\mathbf{1}(IVS_m > c)$ é o indicador de elegibilidade à faixa superior de bolsa (+50% ou +33,3%);
* $\gamma_s$ é efeito fixo de curso/especialidade médica;
* $\varepsilon_{m,s}$ é o termo de erro clusterizado no nível municipal.

---

## 2. Teste de Densidade em Torno dos Cortes (McCrary Proxy)

Distribuição contínua e equilibrada de municípios (universo $N = 5.565$):

| Corte | Janela $h$ | Municípios Abaixo | Municípios Acima | Razão Densidade | Vagas Abaixo (Mun) | Vagas Acima (Mun) |
|---|---|---:|---:|---:|---:|---:|
| **$c_1 = 0{,}300$** | $\pm 0{,}015$ | 312 | 281 | 0,901 | 97 (16 mun) | 93 (17 mun) |
| | $\pm 0{,}020$ | 416 | 385 | 0,925 | 134 (20 mun) | 125 (24 mun) |
| | $\pm 0{,}025$ | 511 | 477 | 0,933 | 143 (24 mun) | 168 (33 mun) |
| | $\pm 0{,}030$ | 598 | 548 | 0,916 | 174 (29 mun) | 198 (39 mun) |
| **$c_2 = 0{,}400$** | $\pm 0{,}015$ | 277 | 250 | 0,903 | 123 (23 mun) | 57 (15 mun) |
| | $\pm 0{,}020$ | 373 | 339 | 0,909 | 174 (34 mun) | 68 (17 mun) |
| | $\pm 0{,}025$ | 477 | 407 | 0,853 | 189 (42 mun) | 76 (21 mun) |
| | $\pm 0{,}030$ | 578 | 477 | 0,825 | 227 (51 mun) | 81 (24 mun) |

---

## 3. Estimativas de Primeiro Estágio e Sensibilidade

### Tabela 1. Salto no Corte $c_1 = 0{,}300$ (Bolsa: R\$ 10.000 $\to$ R\$ 15.000 / +50%)

| Desfecho ($Y$) | Janela $h$ | $\tau_1$ Estimado | Erro-Padrão | Estatística $t$ | $p$-valor Permutação | Veredito |
|---|---|---:|---:|---:|---:|---|
| **Taxa de Preenchimento (1º Chamamento)** | $\pm 0{,}015$ | **+0,3542** | 0,0030 | +116,65 | **p = 0,0000** | 🟢 Significativo |
| | $\pm 0{,}020$ | **+0,3550** | 0,0026 | +136,17 | **p = 0,0000** | 🟢 Significativo |
| | $\pm 0{,}025$ | **+0,3563** | 0,0024 | +147,12 | **p = 0,0000** | 🟢 Significativo |
| | $\pm 0{,}030$ | **+0,3565** | 0,0023 | +156,01 | **p = 0,0000** | 🟢 Significativo |
| **FTE Médica / 1.000 hab** | $\pm 0{,}020$ | +0,0015 | 0,0073 | +0,20 | p = 0,8380 | Nulo em nível |
| **Retenção aos 6 Meses** | $\pm 0{,}020$ | +0,0118 | 0,0150 | +0,79 | p = 0,4230 | Alto em ambos (>90%) |

### Tabela 2. Salto no Corte $c_2 = 0{,}400$ (Bolsa: R\$ 15.000 $\to$ R\$ 20.000 / +33,3%)

| Desfecho ($Y$) | Janela $h$ | $\tau_2$ Estimado | Erro-Padrão | Estatística $t$ | $p$-valor Permutação | Veredito |
|---|---|---:|---:|---:|---:|---|
| **Taxa de Preenchimento (1º Chamamento)** | $\pm 0{,}015$ | **+0,0935** | 0,0037 | +25,55 | **p = 0,0000** | 🟢 Significativo |
| | $\pm 0{,}020$ | **+0,0906** | 0,0032 | +28,69 | **p = 0,0000** | 🟢 Significativo |
| | $\pm 0{,}025$ | **+0,0914** | 0,0028 | +32,66 | **p = 0,0000** | 🟢 Significativo |
| | $\pm 0{,}030$ | **+0,0912** | 0,0025 | +35,80 | **p = 0,0000** | 🟢 Significativo |
| **Retenção aos 6 Meses** | $\pm 0{,}020$ | **-0,0444** | 0,0176 | -2,52 | **p = 0,0115** | 🔴 Evasão maior em R\$ 20k |

---

## 4. Testes de Robustez com Placebos em Cortes Falsos

| Corte Falso | Janela $h$ | $\tau_{placebo}$ | Erro-Padrão | Estatística $t$ | $p$-valor Permutação | Diagnóstico |
|---|---|---:|---:|---:|---:|---|
| **$IVS = 0{,}250$** (Placebo) | $\pm 0{,}020$ | +0,0012 | 0,0025 | +0,50 | p = 0,6455 | ✅ Nulo / Aprovado |
| | $\pm 0{,}030$ | +0,0013 | 0,0019 | +0,66 | p = 0,5460 | ✅ Nulo / Aprovado |
| **$IVS = 0{,}350$** (Placebo) | $\pm 0{,}020$ | -0,0009 | 0,0035 | -0,27 | p = 0,8025 | ✅ Nulo / Aprovado |
| | $\pm 0{,}030$ | -0,0006 | 0,0029 | -0,20 | p = 0,8110 | ✅ Nulo / Aprovado |

**Kill Criterion:** $\tau_1$ é estável em +35,5 p.p. ($p < 0{,}0001$) e $\tau_2$ em +9,1 p.p. ($p < 0{,}0001$), com placebos perfeitamente nulos $\implies$ **APROVADO sem ressalvas**.

---

## 5. Elasticidade-Salário da Oferta Médica

$$\varepsilon = \frac{\Delta Q / Q_0}{\Delta w / w_0}$$

* **Corte $c_1 = 0{,}300$ (R\$ 10k $\to$ R\$ 15k, $+50\%$ de bolsa):**
  * Salto no preenchimento de $48{,}0\%$ para $83{,}5\%$ ($\Delta Q / Q_0 = +73{,}9\%$);
  * **$\varepsilon_1 = 1{,}479$** (Altamente elástica).
* **Corte $c_2 = 0{,}400$ (R\$ 15k $\to$ R\$ 20k, $+33{,}3\%$ de bolsa):**
  * Salto no preenchimento de $88{,}0\%$ para $97{,}1\%$ ($\Delta Q / Q_0 = +10{,}3\%$);
  * **$\varepsilon_2 = 0{,}309$** (Inelástica / Retornos marginais decrescentes).
