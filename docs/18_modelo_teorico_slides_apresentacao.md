# 18. Sistema Unificado de Equações Teóricas Microeconômicas para Apresentação (Slides)

> **Documento Teórico de Referência para Apresentações e Defesas**  
> **Projeto:** Avaliação de Impacto e Economia da Saúde — Programa Mais Médicos Especialistas (PMM-E / Lei nº 15.233/2025)  
> **Tema Central:** *Incentivos financeiros, vulnerabilidade territorial e provimento duradouro de especialistas: evidências do Mais Médicos Especialistas.*  
> **Finalidade:** Fornecer um sistema teórico axiomático puro em 3 blocos interligados (Utilidade Estrutural $\rightarrow$ Equilíbrio Espacial de Roback $\rightarrow$ Condição de Diferencial Compensatório), integrando Renda, Esforço, Propósito/Missão e Lazer/Amenidades.  
> **Data de Consolidação:** 31 de Agosto de 2026  

---

## O Slide Teórico Perfeito: O Modelo Microeconômico de Escolha Espacial Médica

```
====================================================================================================
               FUNDAMENTAÇÃO TEÓRICA: O EQUILÍBRIO ESPACIAL HEDÔNICO DO ESPECIALISTA
====================================================================================================
```

### [Bloco 1] Função de Utilidade Estrutural do Médico Especialista
*(Inspirada em Rosen 1986, p. 643; Besley & Ghatak 2005, AER, p. 618; Roback 1982, JPE, p. 1259)*

$$U(w_m, e, s_m) = \underbrace{v(w_m)}_{\substack{\text{Utilidade da Renda} \\ \text{(Bolsa + Salário) (+) }}} - \underbrace{c(e)}_{\substack{\text{Desutilidade do Esforço} \\ \text{e Plantões (-) }}} + \underbrace{\theta \cdot \Delta(IVS_m)}_{\substack{\text{Motivação Intrínseca} \\ \text{e Propósito Social (+) }}} + \underbrace{\alpha \cdot s_m}_{\substack{\text{Amenidades Urbanas,} \\ \text{Lazer e Serviços (+) }}}$$

* **Componentes Microeconômicos:**
  * $v(w_m)$ com $v' > 0, v'' \le 0$: Utilidade côncava do rendimento monetário ($w_m = w_0 + \text{Bolsa}_m$);
  * $c(e) = \frac{1}{2} e^2$: Custo convexo de esforço e sobrecarga hospitalar (*Becker 1965; McGuire 2000*);
  * $\theta \cdot \Delta(IVS_m)$: Ganho de utilidade moral gerado pelo impacto assistencial $\Delta$ em áreas desassistidas (*Besley & Ghatak 2005, AER*);
  * $s_m = -IVS_m$: Vetor de amenidades de qualidade de vida e opções de lazer da cidade (*Glaeser et al. 2001; Diamond 2016*).

---

### [Bloco 2] Condição de Indiferença e Equilíbrio Espacial Geral
*(Roback 1982, Journal of Political Economy, p. 1259, Eq. 1 e Eq. 2)*

Pela condição de livre mobilidade, a utilidade indireta $V(w_m, s_m)$ iguala-se à utilidade de reserva no polo metropolitano ($V_0$):

$$V(w_m, s_m) = V_0$$

Diferenciando totalmente a utilidade indireta no equilíbrio ($dV = 0$):

$$\left. \frac{dw_m}{ds_m} \right|_{V = V_0} = -\frac{\frac{\partial V}{\partial s_m}}{\frac{\partial V}{\partial w_m}} = -\frac{\alpha + \theta \Delta'(s_m)}{v'(w_m)} < 0$$

Como a vulnerabilidade territorial $IVS_m$ representa o déficit de amenidades ($s_m = -IVS_m$):

$$\left. \frac{dw_m}{d(IVS_m)} \right|_{V = V_0} = \frac{\alpha - \theta \Delta'(IVS_m)}{v'(w_m)} > 0$$

---

### [Bloco 3] A Condição de Compensação Territorial (Willingness to Accept da Bolsa)
*(Sivey et al. 2012, Journal of Health Economics, p. 816; Rosen 1986, p. 643)*

A bolsa federal mínima necessária ($\text{Bolsa}^*$) para viabilizar a atração e retenção do especialista no município $m$ satisfaz:

$$\text{Bolsa}^*(IVS_m) = \underbrace{\left( \frac{\alpha}{v'} \right) \cdot IVS_m}_{\substack{\text{Compensação Financeira por Pobreza} \\ \text{e Falta de Lazer/Amenidades (+) }}} - \underbrace{\left( \frac{\theta}{v'} \right) \cdot \Delta(IVS_m)}_{\substack{\text{Alívio na Bolsa por Motivação} \\ \text{Intrínseca e Missão (-) }}} + \underbrace{\frac{c(e)}{v'}}_{\substack{\text{Compensação de} \\ \text{Esforço/Plantão (+) }}}$$

---

## 2. Roteiro de Fala para a Apresentação do Slide (Script Acadêmico)

1. *"Apresentamos o problema de decisão do especialista a partir de uma função de utilidade estrutural microeconômica que integra quatro dimensões de bem-estar: o retorno financeiro da bolsa ($v(w)$), a desutilidade do esforço hospitalar ($c(e)$), o ganho moral de missão pública ao atender no SUS ($\theta \Delta$) e o consumo de amenidades e lazer da localidade ($\alpha s$)."*
2. *"Pelo teorema de equilíbrio espacial de Roback (1982, JPE), a utilidade do médico precisa se equalizar entre a capital e o interior ($V = V_0$). Ao diferenciarmos essa condição, provamos matematicamente que municípios com alto IVS exigem um gradiente salarial positivo ($\frac{dw}{d(IVS)} > 0$)."*
3. *"Essa condição deriva diretamente a equação teórica da bolsa compensatória ($\text{Bolsa}^*$): o incentivo financeiro precisa cobrir o custo de isolamento territorial ($\alpha \cdot IVS$), mas é atenuado na medida em que o médico possui compromisso social e vocação pública com o SUS ($\theta \Delta$)."*
