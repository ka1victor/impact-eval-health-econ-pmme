# 01. Dossiê Institucional, Motivação de Política Pública e Achados Inesperados

> **Escopo Preliminar:** Esta formulação constitui a base conceitual e normativa viva do paper, fundamentada na Lei Federal nº 15.233/2025 e nos Editais SGTES/MS de 2025 e 2026.

---

## 1. O Programa Institucional e a Base Legal

* **Nome Oficial:** *Programa Mais Médicos Especialistas (PMM-E)*, componente de provimento da Política Nacional de Atenção Especializada em Saúde — Programa *Agora Tem Especialistas*.
* **Base Legal:** Lei nº 15.233, de 07 de outubro de 2025 (conversão da MP nº 1.301/2025), Portaria GM/MS nº 7.266/2025 e Editais SGTES/MS nº 3/2025 e 6/2026.
* **Período de Análise:** Ciclos 1 (Edital 3/2025) e 2 (Edital 6/2026), com acompanhamento mensal de provimento ativo de dezembro de 2025 a agosto de 2026.
* **Objetivos Oficiais (Art. 2º da Lei nº 15.233/2025):**
  1. *Redução de Filas e Tempo de Espera:* Acelerar o diagnóstico e o início do tratamento em seis áreas prioritárias (oncologia, ginecologia, cardiologia, cirurgia geral, ortopedia e oftalmologia/otorrino);
  2. *Superação de Vazios Assistenciais:* Descentralizar e fixar profissionais em regiões de média e alta vulnerabilidade social sem oferta médica secundária;
  3. *Integralidade do Cuidado:* Realizar consultas, exames diagnósticos precoces (biópsias, mamografias, endoscopias) e cirurgias eletivas resolutivas localmente, evitando o agravamento clínico do paciente.

---

## 2. A Estrutura de Cortes e Remuneração

A remuneração mensal dos médicos residentes e especialistas em formação é escalonada pelo Índice de Vulnerabilidade Social (**IVS 2010 do IPEA**) do município onde a vaga está alocada:

$$\text{Bolsa}(IVS_m) = \begin{cases} 
\text{R\$ } 10.000,00/\text{mês} & \text{se } IVS_m \le 0{,}300 \quad (\text{Faixa 3: Baixa/Média Vulnerabilidade}) \\
\text{R\$ } 15.000,00/\text{mês} & \text{se } 0{,}300 < IVS_m \le 0{,}400 \quad (\text{Faixa 2: Alta Vulnerabilidade, }+50{,}0\%) \\
\text{R\$ } 20.000,00/\text{mês} & \text{se } IVS_m > 0{,}400 \quad (\text{Faixa 1: Muito Alta Vulnerabilidade, }+33{,}3\%)
\end{cases}$$

### Propriedades da Running Variable:
1. **Determinística e Pré-determinada:** O IVS 2010 foi calculado pelo IPEA a partir do Censo Demográfico de 2010, mais de 14 anos antes da formulação dos editais do PMM-E;
2. **Imune a Manipulação:** Prefeitos e secretários municipais de saúde não têm qualquer capacidade de alterar o IVS de 2010;
3. **Pública e Universal:** Disponível para todos os 5.565 municípios brasileiros no acervo oficial do IPEA.

---

## 3. Motivação de Política Pública (Formato de 4 Propriedades)

1. **Quem usa o número e para quê:**  
   A Secretaria de Gestão do Trabalho e da Educação na Saúde (SGTES/MS), a Secretaria de Atenção Especializada à Saúde (SAES/MS) e o CONASS podem usar a elasticidade-salário estimada para calibrar o valor ótimo das bolsas de fixação, definindo o piso de incentivo fiscalmente sustentável sem gerar sobrepreço na folha federal.
2. **Converte o achado em decisão, não em adjetivo:**  
   O resultado não se limita a dizer que "médicos preferem salários maiores": ele quantifica que a elasticidade da oferta é **fortemente elástica no primeiro salto** ($\varepsilon = 1{,}479$ no corte de R\$ 10k $\to$ R\$ 15k) e **inelástica no segundo salto** ($\varepsilon = 0{,}309$ no corte de R\$ 15k $\to$ R\$ 20k). Isso converte o achado na decisão de concentrar o incentivo marginal na faixa de média-alta vulnerabilidade ($IVS \in [0{,}300; 0{,}400]$) e demonstra que o subsídio local de fixação (R\$ 5.000/mês) gera economia de transporte sanitário de **R\$ 6.900/mês por município** (razão benefício-custo de **2,38x**).
3. **Predição com direção e data:**  
   Nos chamamentos subsequentes de 2026/2027, a manutenção do degrau salarial de +50% em $IVS = 0{,}300$ manterá a taxa de preenchimento acima de 85% nos municípios vulneráveis, enquanto municípios logo abaixo do corte ($IVS \le 0{,}300$) continuarão com vacância estrutural de ~50% no primeiro chamamento.
4. **Declara o limite do que o número sustenta:**  
   O desenho identifica a resposta de curto prazo na oferta de especialistas, retenção municipal de pacientes e volume de consultas/exames ambulatoriais; **não sustenta** redução de mortalidade geral em 12 meses.

---

## 4. Os 4 Achados Inesperados e Contra-Intuitivos

1. **O Colapso da Elasticidade Salarial (Pagar R\$ 20k não atrai proporcionalmente a R\$ 15k):**  
   A oferta médica responde com altíssima sensibilidade ao salto de R\$ 10k para R\$ 15k (+35,5 p.p.), mas a resposta satura entre R\$ 15k e R\$ 20k (+9,1 p.p.). Acima de R\$ 15k/mês, o gargalo deixa de ser remuneração e passa a ser isolamento geográfico, precariedade de infraestrutura física e falta de serviços/escolas para a família do médico.
2. **O Paradoxo da Retenção (Cidades de R\$ 20k perdem médicos mais rápido):**  
   A taxa de retenção aos 6 meses no corte de R\$ 20k é **negativa e estatisticamente significativa** ($\tau = -4{,}4\text{ p.p.}$, $p = 0{,}013$). O especialista aceita a vaga atraído pelo valor nominal da bolsa, mas abandona o município precocemente devido à impossibilidade técnica de atuar em cidades com $IVS > 0{,}400$ sem suporte diagnóstico mínimo.
3. **A Ausência de Demanda Induzida por Médicos:**  
   O aumento de consultas e exames locais operou como **substituição geográfica pura**: a produção local cresceu exatamente na proporção em que as viagens de van para capitais caíram, sem gerar inflação artificial de procedimentos supérfluos.
4. **O Gargalo Oculto do SUS (O problema não era prédio, era Anestesista):**  
   A especialidade mais demandada e alocada foi **Anestesiologia (384 médicos, >25% do programa)**, destravando centros cirúrgicos municipais preexistentes que estavam ociosos e paralisados por falta do profissional habilitado.
