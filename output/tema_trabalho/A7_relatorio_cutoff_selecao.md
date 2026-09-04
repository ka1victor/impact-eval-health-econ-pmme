# A7 — Corte de seleção, atração e presença ativa

> **Veredito:** existe uma descontinuidade administrativa observável e substantivamente grande, mas os dados públicos ainda não autorizam chamá-la de efeito causal.

## 1. O que foi encontrado

As listas publicadas permitem formar pares dentro da mesma célula curso–CNES: o último candidato selecionado em sua primeira opção e o primeiro candidato não selecionado. Há **423 pares adjacentes** em quatro publicações; **184** têm o mesmo escore publicado. Os dois estágios de 2025 fornecem **193 pares** com homologação e presença ativa observáveis; **81** têm o mesmo escore.

Na primeira chamada de 2025, entre 136 pares, a homologação foi 59.6% para o último selecionado e 13.2% para o primeiro não selecionado: diferença de **46.3 p.p.** (IC95% 37.1 a 55.5). No snapshot de 2026-08-12, a presença ativa no ciclo 1 foi 49.3% versus 22.1%, diferença de **27.2 p.p.** (IC95% 15.6 a 38.8).

Na segunda chamada, as diferenças correspondentes foram **77.2 p.p.** em homologação e **56.1 p.p.** em presença ativa. A repetição do sinal em chamadas separadas torna o padrão relevante, mas não resolve a identificação.

## 2. Por que isso ainda não é causal

O ranking não é um sorteio. O Edital nº 3/2025 determina que empates sejam resolvidos primeiro pela escolha de vaga na mesma UF do domicílio ou nascimento e depois pela maior idade. Localidade prévia e idade também podem afetar aceitação e permanência. Esses campos não são publicados. Logo, nem comparar rank 1 com rank 2 nem restringir ao mesmo barema elimina seleção não observada.

O vínculo entre arquivos foi feito somente por nome normalizado exato e único, sem aproximação textual. Todos os 316 homologados da primeira chamada aparecem na lista de seleção, mas as máscaras de CPF são incompatíveis. O snapshot de ativos mede estar ativo em uma data fixa; ele não reconstrói início, interrupções ou duração contínua.

## 3. Trabalho pequeno recomendado

**Pergunta:** ganhar marginalmente a vaga de primeira opção aumenta a entrada e a presença posterior do especialista no PMM-E?

**Estimando principal:** intenção de tratamento local de ganhar a primeira opção sobre início em até 30 dias. Homologação e presença ativa em 90 e 180 dias serão secundários. O desfecho de presença deve ser incondicional à entrada, evitando selecionar apenas quem começou.

**Desenho:** ampla concorrência; exclusão predefinida de casos sub judice; reconstrução integral de preferências, vagas e recursos. Dentro dos empates de barema e do mesmo status de prioridade por UF, usar idade em dias centrada na idade do último selecionado como running variable em RDD empilhado. A análise de pares adjacentes fica como apresentação intuitiva e robustez.

**Dados mínimos:** identificadores pseudonimizados estáveis, barema final, indicador de prioridade pela UF, idade em dias ou distância etária ao cutoff, capacidade por modalidade e eventos datados de confirmação, homologação, início e saída. Não é necessário receber data de nascimento nem endereço.

## 4. Relação com os resultados existentes

A4 continua sendo evidência associativa sobre quais territórios atraíram candidatos. A5 continua sendo evidência associativa sobre estoque municipal no CNES. O RDD do IVS continua encerrado. A7 é um desenho distinto, no nível do candidato, voltado exatamente à margem de atração/entrada; ele não transforma retrospectivamente A4 ou A5 em resultados causais.

## 5. Uso autorizado

- **Hoje:** “há uma grande descontinuidade de homologação e presença ativa no corte publicado de seleção”.
- **Ainda não:** “ganhar a vaga causou o aumento”.
- **Após os dados de desempate e os diagnósticos:** linguagem causal local, se o RDD empilhado passar suporte, continuidade e testes de manipulação/balanceamento.

Fonte normativa: https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2025/chamamento-publico-sgtes-ms-no-3-2025-projeto-mais-medicos-especialistas/edital-de-chamamento-publico-no-3-2025.pdf
