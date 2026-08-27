# 06. Backlog guardado: WP3, WP4 e WP5

> Este documento preserva a agenda posterior sem transformá-la em trabalho corrente. Nenhum agente deve implementar estes WPs durante o estudo de eficácia operacional, salvo nova decisão explícita do autor.

## 1. Por que ficam guardados

WP3, WP4 e WP5 estão a jusante da capacidade médica. Executá-los agora ampliaria dados, teoria, identificação e linguagem antes de validar se o incentivo produz capacidade sustentada e adicional.

O adiamento não implica que esses outcomes sejam menos importantes. Tempo de espera continua sendo o objetivo legal mais próximo do paciente. A decisão é sequencial: testar primeiro o elo operacional que define o estudo atual.

## 2. WP3 — acesso, fila e deslocamento

### O que fica preservado

- definições de tempo de espera, demanda atendida e estoque da fila;
- distinção entre acesso local e global;
- decomposição origem–destino;
- hipóteses sobre proximidade, bypass e capacidade liberada nos polos;
- lista de dados necessários em `02_inventario_dados_por_outcome.md`.

### O que não será feito agora

- aquisição ou processamento de microdados de regulação;
- estimação de espera em 30/60/90 dias;
- SIA/SIH para fluxos residência–prestador;
- cálculo de distância, tempo de viagem ou viagens evitadas;
- afirmações de resolutividade local/global;
- inferência de fila a partir de produção ou localização do médico.

### Condições para reabrir

1. Estudo operacional concluído ou claramente inviável.
2. Dados de regulação com solicitação, prioridade, atendimento e cancelamento.
3. Regra estável para duplicidades, censura e mudanças cadastrais.
4. Fluxos residência–prestador comparáveis no tempo.
5. Novo protocolo causal específico para acesso.

## 3. WP4 — desfechos clínicos

### O que fica preservado

- candidatos a linhas de cuidado: cirurgia, oncologia, saúde da mulher/digestiva e cardiologia;
- princípios de usar outcomes específicos e horizontes biologicamente plausíveis;
- distinção entre produção, diagnóstico, tratamento e saúde;
- necessidade de APAC, SIH e ligação temporal entre eventos.

### O que não será feito agora

- seleção definitiva de linha clínica;
- vinculação de APAC/SIH;
- estimação de diagnóstico precoce, estadiamento, complicação, reinternação ou mortalidade;
- uso de volume de exames como proxy silenciosa de saúde;
- afirmação de que presença de determinada especialidade destravou procedimentos.

### Condições para reabrir

1. Evidência de primeiro estágio operacional e capacidade utilizável.
2. Linha de cuidado pré-especificada com mecanismo curto e plausível.
3. Cobertura e qualidade suficientes dos dados clínicos.
4. Horizonte compatível com implantação e tempo biológico.
5. Novo protocolo, inclusive multiplicidade e privacidade.

## 4. WP5 — custos e bem-estar

### O que fica preservado

- perspectivas federal, municipal, SUS consolidado e social;
- separação entre transferências financeiras e recursos reais;
- componentes de custo do programa, transporte e tempo do paciente;
- princípio de evitar dupla contagem;
- exigência de análise de sensibilidade.

### O que não será feito agora

- benefício–custo, custo-efetividade ou monetização de saúde;
- cenários de viagens evitadas;
- valores presumidos de transporte, tempo, produção ou QALY;
- atribuição automática de capacidade liberada como economia;
- cálculo econômico sem efeito causal e custos observados.

### Condições para reabrir

1. Efeito causal observado sobre um outcome relevante.
2. Custos incrementais do programa documentados.
3. Custos logísticos e privados observados ou faixa empiricamente defensável.
4. Perspectiva e horizonte definidos.
5. Protocolo para incerteza, sensibilidade e dupla contagem.

## 5. Regra de manutenção do backlog

- Não criar scripts ou outputs de WP3–WP5 no pipeline atual.
- Não baixar grandes bases desses WPs “por precaução”.
- Novas fontes podem ser anotadas neste backlog, sem iniciar análise.
- A reabertura exige decisão explícita, atualização do roadmap e novo prompt.
- Nenhum resultado do estudo operacional será extrapolado para esses WPs.
