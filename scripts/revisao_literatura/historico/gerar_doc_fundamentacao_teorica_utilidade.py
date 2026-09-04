# -*- coding: utf-8 -*-
"""Preserva a versão histórica do modelo unificado anterior à revisão do Doc 17."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT_MD = ROOT / "docs" / "90_arquivo_historico" / "17_modelo_unificado_legado.md"

DOC = r"""# 17. Base Microeconômica Unificada da Escolha Locacional Médica

> **Projeto:** Avaliação de Impacto e Economia da Saúde — Programa Mais Médicos Especialistas (PMM-E / Lei nº 15.233/2025)  
> **Objeto:** Decisão intertemporal de alocação espacial e oferta de trabalho médico  
> **Status:** Documento teórico canônico de referência  
> **Data de Consolidação:** 31 de agosto de 2026  

---

## 1. Arquitetura do Modelo Unificado

O modelo microeconômico do estudo adota uma **arquitetura teórica unificada**:

1. **O Núcleo Canônico é Moehling et al. (2020):** fornece o problema intertemporal em que o médico escolhe a localidade que maximiza o fluxo descontado da remuneração real esperada menos um termo agregado de custos e desamenidades locacionais ($c$).
2. **A Microfundamentação Estrutural de $c$ vem de Roback (1982) e Reinhardt (1975):** no paper original de Moehling et al., o termo $c$ é mantido em forma reduzida como uma "caixa-preta". Usamos Roback e Reinhardt para **abrir e formalizar os componentes estruturais implícitos em $c$**, transformando-o em uma função explícita de condições clínicas, tempo, propósito, suporte de pares e fricção espacial:
   $$
   c^{(s)}_{it} = c\Big(R_{it}, L_{it}, K_{it}, \boldsymbol{\Omega}_{it}, D_{it}, N_{it}, \mathbf{Z}_i; \; r_{it}, s_{it}, d_i\Big)
   $$

Essa unificação preserva a regra de decisão de Moehling et al., ao mesmo tempo em que dá conteúdo econômico rigoroso aos fatores institucionais, tecnológicos, espaciais e vocacionais que determinam a atratividade do município.

---

## 2. O Ponto de Partida: Moehling et al. (2020) e a "Caixa-Preta" de $c$

Moehling, Niemesh, Thomasson e Treber (2020, p. 187) escrevem o problema microeconômico de escolha locacional do médico como:

$$
\arg\max_{i \in \mathcal{I}} U(\omega_i) = \arg\max_{i \in \mathcal{I}} \sum_t \delta^t \left[ \frac{\mathbb{E}(w^{(s)}_{it})}{p_{it}} - c^{(s)}_{it} \right]
$$

onde:

* $i \in \mathcal{I}$ indexa o município no conjunto de opções viáveis $\mathcal{I}$;
* $t$ indexa o período temporal (horizonte de planejamento);
* $s$ identifica a especialidade médica / grupo de qualificação;
* $w^{(s)}_{it}$ é a remuneração nominal esperada;
* $p_{it}$ é o nível geral de preços local / custo de vida;
* $\delta \in (0, 1)$ é o fator de desconto intertemporal;
* $c^{(s)}_{it}$ é o parâmetro aditivo que reúne os custos e desamenidades locacionais.

### O que $c$ representa no paper oficial de Moehling et al.?

No texto original, os autores discutem $c^{(s)}_{it}$ em forma reduzida, mencionando:
* Preferência por estilo de vida urbano versus rural (*"taste for rural/urban living"*);
* Proximidade geográfica da família e vínculos de nascimento (*"proximity to family"*);
* Custos de deslocamento e despesas residenciais genéricas.

Ao mesmo tempo, Moehling et al. tratam hospitais, laboratórios, densidade médica e malha de transporte como **amenidades produtivas** que deslocam a remuneração nominal esperada $\mathbb{E}(w^{(s)}_{it})$.

> [!NOTE]
> **A Limitação Teórica de Moehling et al.:**
> Embora separem remuneração real e custos locacionais, Moehling et al. **não abrem o mecanismo interno de $c$**. Fatores cruciais para o especialista — como a frustração por falta de equipamentos, a ausência de equipe de enfermagem, o risco de sobrecarga de plantão, o custo de dupla residência, o isolamento profissional e o ganho moral por impacto assistencial — permanecem condensados implicitamente dentro do resíduo $c$.

---

## 3. Abrindo a Caixa de $c$: Microfundamentação via Reinhardt (1975) e Roback (1982)

Para tornar $c$ diretamente mapeável aos dados do CNES, IVS e editais do PMM-E, estruturamos seus argumentos a partir das equações canônicas de Reinhardt e Roback:

### 3.1 Bloco Clínico, Produtivo e Temporal: Reinhardt (1975)

Reinhardt (1975) modela a microeconomia da prática médica por meio de:

$$
U = U(R, Y, L, D; \mathbf{Z}), \qquad \bar{H} = R + H
$$

$$
q = f(H, L, K; \boldsymbol{\Omega}), \qquad \pi = p q - w L - r K
$$

#### O que são $K$ e $\boldsymbol{\Omega}$ em Reinhardt e por que afetam a Utilidade ($U$) e o Custo Locacional ($c$)?

* **Capital Físico / Equipamentos Diagnósticos ($K$):** Representa o estoque de leitos cirúrgicos, aparelhos de ultrassonografia, tomógrafos, salas de parto e instrumental hospitalar.
  * *Canal de Frustração e Resolutividade:* A utilidade do médico depende de sua capacidade de resolver casos clínicos ($q$ e $D$). Trabalhar em uma unidade sem equipamentos ($K \approx 0$) gera **frustração profissional, impotência diagnóstica e risco médico-legal elevado**, aumentando a desutilidade subjetiva de fixação no município ($\frac{\partial c}{\partial K} < 0$).
  * *Canal de Esforço por Atendimento:* A ausência de equipamentos complementares exige maior esforço físico e tempo por consulta ($H$), consumindo o lazer ($R$).
* **Tecnologia Institucional e Rede de Apoio ($\boldsymbol{\Omega}$):** Representa o ambiente organizacional da unidade, prontuário eletrônico, protocolos clínicos e a eficiência da **rede de referência e contrarreferência regional**.
  * *Canal de Estresse e Desamparo Assistencial:* A impossibilidade de referenciar pacientes graves para leitos de UTI ou hospitais terciários gera sobrecarga emocional extrema sobre o especialista, ampliando $c$ ($\frac{\partial c}{\partial \boldsymbol{\Omega}} < 0$).
* **Alocação de Tempo e Lazer ($R = \bar{H} - H$):** Plantões imprevistos e excesso de carga horária ($H$) reduzem o lazer $R$, elevando $c$ ($\frac{\partial c}{\partial R} < 0$, ou $\frac{\partial c}{\partial H} > 0$).
* **Equipe Auxiliar ($L$):** A escassez de enfermeiros e técnicos de saúde sobrecarrega o médico com funções administrativas e de triagem ($\frac{\partial c}{\partial L} < 0$).
* **Propósito e Impacto Assistencial ($D$):** A oportunidade de suprir vazios assistenciais em áreas desassistidas gera realização moral para médicos vocacionados ($\frac{\partial c}{\partial D} < 0$).
* **Vetor de Características Pessoais ($\mathbf{Z}$):** Estágio de carreira, especialidade clínica/cirúrgica e vínculos prévios de residência/origem.

### 3.2 Bloco Espacial, Habitacional e Logístico: Roback (1982) e Extensões Espaciais

Roback (1982) formaliza o equilíbrio hedônico entre salários, aluguéis e amenidades:

$$
\max_{x, \ell^c} U(x, \ell^c; s) \quad \text{sujeito a} \quad w + I = x + r \ell^c, \qquad V(w, r; s) = k
$$

* **Custo de Moradia e Dupla Residência ($r$):** Custos habitacionais e manutenção de duas moradias elevam os gastos recorrentes ($\frac{\partial c}{\partial r} > 0$).
* **Amenidades Urbanas e Familiares ($s$):** Segurança pública, infraestrutura de lazer, qualidade de escolas para os filhos e oportunidades de emprego para o cônjuge reduzem a desamenidade de residência ($\frac{\partial c}{\partial s} < 0$).
* **Fricção Geográfica e Distância ($d$):** Tempo de viagem rodoviária e distância até aeroportos/polos regionais para cumprimento da jornada semanal ($\frac{\partial c}{\partial d} > 0$).
* **Densidade de Pares e Comunidade Profissional ($N$):** Conforme apontado em Moehling et al., a presença de colegas de especialidade, preceptores e ambiente de discussão clínica atenua o isolamento profissional ($\frac{\partial c}{\partial N} < 0$).

---

## 4. O Modelo Microeconômico Unificado do PMM-E

Integrando a função estrutural $c(\cdot)$ ao problema intertemporal de Moehling et al., o **valor da opção municipal $i$** para o médico especialista do tipo $s$ é formalizado por:

$$
V_i = \sum_t \delta^t \left[ \frac{\mathbb{E}(w^{(s)}_{it})}{p_{it}} - c\Big(R_{it}, L_{it}, K_{it}, \boldsymbol{\Omega}_{it}, D_{it}, N_{it}, \mathbf{Z}_i; \; r_{it}, s_{it}, d_i\Big) \right]
$$

E a **regra de escolha locacional ótima** é:

$$
i^* = \arg\max_{i \in \mathcal{I}} V_i
$$

### Propriedades Monotônicas da Função Estrutural $c(\cdot)$

| Argumento | Origem no Modelo | Sinal em $c$ | Mecanismo Teórico |
| :--- | :--- | :---: | :--- |
| **Lazer ($R = \bar{H} - H$)** | Reinhardt (1975) | $\frac{\partial c}{\partial R} < 0$ | Jornada contratual previsível (20h) preserva o lazer e reduz a desutilidade. |
| **Equipe Auxiliar ($L$)** | Reinhardt (1975) | $\frac{\partial c}{\partial L} < 0$ | Enfermagem e suporte técnico reduzem o esforço e a sobrecarga de triagem. |
| **Equipamentos Clínicos ($K$)** | Reinhardt (1975) | $\frac{\partial c}{\partial K} < 0$ | Infraestrutura diagnóstica evita frustração profissional por baixa resolutividade. |
| **Rede de Referência ($\boldsymbol{\Omega}$)** | Reinhardt (1975) | $\frac{\partial c}{\partial \boldsymbol{\Omega}} < 0$ | Capacidade de transferir casos graves mitiga estresse e risco médico-legal. |
| **Propósito Assistencial ($D$)** | Reinhardt (1975) | $\frac{\partial c}{\partial D} < 0$ | Atendimento a populações vulneráveis gera ganho moral para médicos vocacionados. |
| **Densidade de Pares ($N$)** | Moehling et al. (2020) | $\frac{\partial c}{\partial N} < 0$ | Contato com outros especialistas e mentores reduz o isolamento profissional. |
| **Vetor de Origem/Tipo ($\mathbf{Z}$)** | Reinhardt (1975) | $\pm$ | Vínculos prévios de nascimento ou graduação na região atenuam $c$. |
| **Aluguel / Moradia ($r$)** | Roback (1982) | $\frac{\partial c}{\partial r} > 0$ | Custos habitacionais e manutenção de dupla residência elevam a despesa. |
| **Amenidades Urbanas ($s$)** | Roback (1982) | $\frac{\partial c}{\partial s} < 0$ | Segurança, escolas para filhos e lazer tornam a localidade mais atrativa. |
| **Distância / Fricção ($d$)** | Moehling / Espacial | $\frac{\partial c}{\partial d} > 0$ | Tempo de viagem até capital/aeroporto eleva o custo de deslocamento. |

---

## 5. Contextualização para o PMM-E e o Papel do IVS 2010

| Primitivo do Modelo Unificado | Dimensão Econômica no PMM-E | Proxy / Mapeamento no Estudo |
| :--- | :--- | :--- |
| $\frac{\mathbb{E}(w)}{p}$ | Retorno financeiro real da bolsa-formação federal | Faixas de Bolsa (R\$ 10k, 15k, 20k) deflacionadas |
| $R = \bar{H} - H$ | Carga horária semanal no SUS e múltiplos vínculos | Jornada de 20h do edital e contratos no CNES |
| $L$ | Equipe de enfermagem e apoio na unidade | Enfermeiros e técnicos por leito no CNES |
| $K$ | Capital diagnóstico e cirúrgico instalado | Leitos, tomógrafos, ultrassons e salas cirúrgicas |
| $\boldsymbol{\Omega}$ | Protocolos clínicos e regulação de referência | Habilitação de alta complexidade e rede regional |
| $D$ | Necessidade epidemiológica e impacto social | Vulnerabilidade social da população atendida |
| $N$ | Aglomeração médica e rede de preceptoria | Estoque basal de especialistas no município/polo |
| $r$ | Custo de vida local e aluguel | Custo estimado de moradia e estadia |
| $s$ | Amenidades territoriais e serviços urbanos | Indicadores de desenvolvimento urbano e segurança |
| $d$ | Fricção de transporte e isolamento geográfico | Tempo rodoviário/aéreo até o polo regional/capital |
| $\mathbf{Z}$ | Especialidade e vínculos regionais prévios | Especialidade médica e proximidade da formação/origem |
| $\delta^t$ | Desconto intertemporal do valor da formação | Duração da bolsa (12 a 24 meses) e certificação futura |

> [!IMPORTANT]
> **Por que o Efeito Total do IVS 2010 é Teoricamente Ambíguo?**  
> No modelo unificado, o IVS 2010 atua simultaneamente sobre múltiplos canais com direções opostas:
> 1. **Canal Positivo na Bolsa:** O IVS eleva administrativamente a bolsa federal ($\Delta \mathbb{E}(w) > 0$);
> 2. **Canal Negativo em $c$ (Desamenidades e Precariedade Clínica):** Municípios com alto IVS apresentam menor amenidade urbana ($s$), maior isolamento ($d$), menor densidade de pares ($N$) e escassez de capital clínico ($K, L, \boldsymbol{\Omega}$), elevando $c$;
> 3. **Canal Positivo em $c$ (Propósito Assistencial):** Para médicos orientados por impacto social ($\mathbf{Z}$), o alto IVS representa maior necessidade assistencial ($D$), reduzindo $c$.
> 
> Como o saldo líquido $\frac{dV_i}{d(IVS)}$ depende do balanço entre essas forças, a teoria **não impõe sinal único *a priori***, exigindo identificação causal empírica.

---

## 6. O que as Equações Autorizam sobre Forma Funcional

1. **Benchmark Linear na Remuneração Real:** A formulação canônica adota a remuneração real em nível linear ($\mathbb{E}(w)/p$), sem impor retornos marginais decrescentes artificiais.
2. **Restrições a Formas Alternativas:** Os modelos seminais não prescrevem utilidade logarítmica ($\ln w$), CRRA ou exponencial CARA ($-\exp(-aw)$). Tais transformações devem ser tratadas como testes de robustez.
3. **Não Imposição de Interações Mecânicas:** A compensação pecuniária por desamenidades e precariedade opera aditivamente no modelo unificado, sem impor a priori $\beta_{\text{Bolsa} \times \text{IVS}} > 0$.

---

## 7. Referências Canônicas

* **Moehling, C. M.; Niemesh, G. T.; Thomasson, M. A.; Treber, J. (2020).** [*Medical Education Reforms and the Origins of the Rural Physician Shortage*](https://doi.org/10.1007/s11698-019-00187-w). **Cliometrica**, 14(2), 181–225. ([Manuscrito dos Autores](https://niemesgt.github.io/files/MoehlingNiemeshThomassonTreber2019.pdf)).
* **Reinhardt, U. E. (1975).** [*Health Manpower Planning in a Market Context: The Case of Physician Manpower*](https://pure.iiasa.ac.at/213/1/XB-75-001.pdf), em N. T. J. Bailey e M. Thompson (eds.), *Systems Aspects of Health Planning*, North-Holland / IIASA, pp. 131–162.
* **Roback, J. (1982).** [*Wages, Rents, and the Quality of Life: A General Equilibrium Model of Geographic Differences*](https://doi.org/10.1086/261120). **Journal of Political Economy**, 90(6), 1257–1278. ([PDF](https://www.nathanschiff.com/webdocs/grad_urban/urban_papers/Roback_JPE_1982.pdf)).
"""


def main() -> None:
    OUT_MD.write_text(DOC.rstrip() + "\n", encoding="utf-8")
    print(f"Documento gerado: {OUT_MD}")


if __name__ == "__main__":
    main()
