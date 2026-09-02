# -*- coding: utf-8 -*-
"""Gera o documento canônico enxuto de fundamentação teórica (Doc 17) do PMM-E."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_MD = ROOT / "docs" / "17_fundamentacao_teorica_formacao_utilidade_regressores.md"

DOC = r"""# 17. Base Microeconômica da Escolha Locacional Médica

> **Projeto:** Avaliação de Impacto e Economia da Saúde — Programa Mais Médicos Especialistas (PMM-E / Lei nº 15.233/2025)  
> **Objeto:** Decisão intertemporal de alocação espacial e oferta de trabalho médico  
> **Status:** Documento teórico canônico de referência  
> **Data de Consolidação:** 31 de agosto de 2026  

---

## 1. Arquitetura Teórica

A fundamentação microeconômica é estruturada em **três camadas complementares**:

1. **Moehling et al. (2020) são o núcleo:** apresentam o problema intertemporal de escolha da localidade pelo médico.
2. **Roback (1982) complementa o bloco espacial:** formaliza amenidades de consumo, custo de moradia (aluguéis) e amenidades produtivas em equilíbrio espacial.
3. **Reinhardt (1975) complementa o bloco de produção médica:** explicita utilidade, alocação de tempo (trabalho vs. lazer), insumos e produção de serviços médicos.

> [!NOTE]
> Os três trabalhos não escrevem conjuntamente um único modelo. A relação proposta aqui é **estritamente interpretativa**: Roback e Reinhardt ajudam a compreender os canais que permanecem em forma reduzida na equação locacional de Moehling et al. Nenhuma função *ad hoc* foi criada para fundi-los.

---

## 2. Moehling et al. (2020) — Escolha Locacional Intertemporal

Moehling, Niemesh, Thomasson e Treber (2020) escrevem o problema microeconômico de escolha locacional do médico como:

$$
\arg\max_{i \in \mathcal{I}} U(\omega_i) = \arg\max_{i \in \mathcal{I}} \sum_t \delta^t \left[ \frac{\mathbb{E}(w^{(s)}_{it})}{p_{it}} - c^{(s)}_{it} \right]
$$

Na notação dos autores:

* $i \in \mathcal{I}$ indexa a localidade no conjunto de opções viáveis $\mathcal{I}$;
* $t$ indexa o período temporal;
* $s$ identifica o grupo de qualificação / especialidade;
* $w^{(s)}_{it}$ é a remuneração nominal esperada;
* $p_{it}$ é o nível de preços local;
* $c^{(s)}_{it}$ reúne custos e desamenidades de consumo ligados à localidade;
* $\delta \in (0, 1)$ é o fator de desconto intertemporal.

O médico escolhe a localidade que oferece o maior valor presente da remuneração real esperada, líquida dos custos e desamenidades locacionais ($c$). 

Atributos como distância da família e estilo de vida entram em $c$. Infraestrutura clínica, laboratórios, tamanho do mercado e proximidade de outros profissionais são tratados como **amenidades produtivas** que elevam a remuneração nominal esperada $\mathbb{E}(w^{(s)}_{it})$.

---

## 3. Reinhardt (1975) — Utilidade, Tempo e Produção Médica

Reinhardt (1975) modela a microeconomia da prática médica por meio das seguintes equações:

$$
U = U(R, Y, L, D; \mathbf{Z})
$$

$$
\bar{H} = R + H
$$

$$
q = f(H, L, K; \boldsymbol{\Omega})
$$

$$
Y = [1 - t(\pi + I)] \cdot (\pi + I)
$$

$$
\pi = p q - w L - r K
$$

Na notação do autor:

* $R$ são horas de lazer e $H$ são horas de trabalho clínico ($\bar{H} = R + H$ é a dotação total de tempo);
* $Y$ é a renda líquida e $I$ é a renda externa à prática;
* $q$ é a produção de serviços e consultas médicas;
* $L$ é o trabalho de pessoal auxiliar (enfermagem/apoio);
* $K$ é o vetor de insumos de capital não laborais (leitos, salas, equipamentos);
* $D$ representa o compromisso com a assistência disponível à comunidade e a contribuição do próprio médico;
* $\mathbf{Z}$ reúne características pessoais que deslocam a utilidade;
* $\boldsymbol{\Omega}$ reúne deslocadores da tecnologia produtiva;
* $p$ é a tarifa de reembolso/remuneração por unidade de serviço;
* $w$ e $r$ são os custos unitários dos insumos laborais e de capital.

> [!TIP]
> Em **Moehling et al.**, $p$ é o *índice de custo de vida local*; em **Reinhardt**, $p$ é o *reembolso/preço unitário do procedimento*.

---

## 4. Roback (1982) — Amenidades e Equilíbrio Espacial

Roback (1982) apresenta o problema do trabalhador e as condições de equilíbrio espacial:

$$
\max_{x, \ell^c} U(x, \ell^c; s) \quad \text{sujeito a} \quad w + I = x + r \ell^c
$$

$$
V(w, r; s) = k
$$

$$
C(w, r; s) = 1
$$

onde:

* $x$ é o bem de consumo composto e $\ell^c$ é a quantidade de terra/moradia consumida;
* $r$ é o aluguel da moradia e $w$ é o salário nominal;
* $s$ é o vetor de características ou amenidades locais;
* $V(w, r; s)$ é a utilidade indireta do trabalhador e $C(w, r; s)$ é a função de custo unitário da firma.

O modelo explicita que atributos locais ($s$) afetam a utilidade do trabalhador (amenidades de consumo) e a produtividade da firma (amenidades produtivas). Salários e aluguéis ajustam-se conjuntamente no equilíbrio territorial.

---

## 5. Relação entre os Três Modelos

| Dimensão | Moehling et al. (2020) | Roback (1982) | Reinhardt (1975) |
| :--- | :--- | :--- | :--- |
| **Pergunta Central** | *Qual município o médico escolhe?* | *Como salários e aluguéis se ajustam no espaço?* | *Como tempo e insumos geram serviços e renda?* |
| **Tratamento da Produção** | Forma reduzida em $\mathbb{E}(w)$ | Função de custo $C(w, r; s)$ | Função de produção $q = f(H, L, K; \boldsymbol{\Omega})$ |
| **Tratamento da Renda** | Remuneração real $\mathbb{E}(w)/p$ | Orçamento com moradia $x + r \ell^c$ | Lucro operacional $\pi$ e renda líquida $Y$ |
| **Papel no Estudo** | **Núcleo de Escolha Locacional** | **Equilíbrio Espacial e Diferenciais** | **Infraestrutura Clínica e Tempo** |

---

## 6. Modelo Microeconômico Adotado

O modelo microeconômico adotado como benchmark é o problema intertemporal de **Moehling et al. (2020)**.

Define-se o valor de atratividade da localidade $i$ por:

$$
V_i \equiv \sum_t \delta^t \left[ \frac{\mathbb{E}(w^{(s)}_{it})}{p_{it}} - c^{(s)}_{it} \right]
$$

A regra de decisão ótima do médico especialista é:

$$
i^* = \arg\max_{i \in \mathcal{I}} V_i
$$

O especialista pondera:
1. **Remuneração nominal esperada:** valor da bolsa federal do PMM-E;
2. **Poder de compra real:** nível local de preços e custos habitacionais;
3. **Custos e desamenidades locacionais ($c$):** distância familiar, conectividade e serviços locais;
4. **Desconto intertemporal ($\delta^t$):** peso relativo dado ao fluxo presente versus benefícios futuros de qualificação e titulação.

---

## 7. Contextualização para o PMM-E e o IVS 2010

| Elemento Teórico | Interpretação no PMM-E | Proxy no Estudo |
| :--- | :--- | :--- |
| $\mathbb{E}(w)/p$ *(Moehling et al.)* | Retorno monetário real esperado da bolsa | Faixa de Bolsa Federal (R\$ 10k, 15k, 20k) deflacionada |
| $c$ *(Moehling et al.)* | Custos e desamenidades de deslocamento e moradia | Distância até polo regional/capital e infraestrutura urbana |
| Amenidades Produtivas | Infraestrutura clínica e rede de apoio | Leitos, tomógrafos, ultrassons e enfermagem no CNES |
| $\delta^t$ *(Moehling et al.)* | Desconto temporal dos ganhos formativos | Duração da bolsa (12 a 24 meses) e certificação futura |
| $s, r$ *(Roback)* | Amenidades urbanas e custo de moradia | Aluguel estimado e indicadores de serviços locais |
| $H, R$ *(Reinhardt)* | Alocação entre jornada PMM-E e lazer | Carga horária (20h semanais) e múltiplos vínculos |
| $L, K, \boldsymbol{\Omega}$ *(Reinhardt)* | Equipe e capital complementar na unidade | Pessoal auxiliar e equipamentos instalados no CNES |
| $D$ *(Reinhardt)* | Propósito assistencial e compromisso social | Vulnerabilidade social e carência assistencial da localidade |

> [!IMPORTANT]
> **Status do IVS 2010:**  
> O IVS não é um primitivo isolado de nenhuma das funções. Ele atua simultaneamente como critério de remuneração (bolsa mais alta), indicador de desamenidade urbana ($c$) e marcador de necessidade de saúde ($D$). Como esses canais possuem sinais teóricos opostos, o **efeito líquido total do IVS sobre a utilidade é teoricamente ambíguo**. O IVS 2010 permanece a **running variable canônica** do estudo.

---

## 8. O que as Equações Autorizam sobre Forma Funcional

1. **Benchmark Linear em Nível Real:** A equação de Moehling et al. introduz a remuneração real linearmente ($\mathbb{E}(w)/p$). Portanto, a forma canônica para a remuneração é em nível real.
2. **Restrições Funcionais:** Os modelos não impõem utilidade logarítmica, CRRA ou exponencial (CARA). Qualquer curvatura adicional constitui hipótese teórica alternativa e não decorre dos modelos originais selecionados.
3. **Não Imposição de Interações:** Não há justificativa teórica para forçar interação positiva mecânica entre Bolsa e IVS ($\beta_{\text{Bolsa} \times \text{IVS}} > 0$).

---

## 9. Referências Canônicas

* **Moehling, C. M.; Niemesh, G. T.; Thomasson, M. A.; Treber, J. (2020).** [*Medical Education Reforms and the Origins of the Rural Physician Shortage*](https://doi.org/10.1007/s11698-019-00187-w). **Cliometrica**, 14(2), 181–225. ([Manuscrito dos Autores](https://niemesgt.github.io/files/MoehlingNiemeshThomassonTreber2019.pdf)).
* **Reinhardt, U. E. (1975).** [*Health Manpower Planning in a Market Context: The Case of Physician Manpower*](https://pure.iiasa.ac.at/213/1/XB-75-001.pdf), em N. T. J. Bailey e M. Thompson (eds.), *Systems Aspects of Health Planning*, North-Holland / IIASA, pp. 131–162.
* **Roback, J. (1982).** [*Wages, Rents, and the Quality of Life: A General Equilibrium Model of Geographic Differences*](https://doi.org/10.1086/261120). **Journal of Political Economy**, 90(6), 1257–1278. ([PDF](https://www.nathanschiff.com/webdocs/grad_urban/urban_papers/Roback_JPE_1982.pdf)).
"""


def main() -> None:
    OUT_MD.write_text(DOC.rstrip() + "\n", encoding="utf-8")
    print(f"Documento gerado: {OUT_MD}")


if __name__ == "__main__":
    main()
