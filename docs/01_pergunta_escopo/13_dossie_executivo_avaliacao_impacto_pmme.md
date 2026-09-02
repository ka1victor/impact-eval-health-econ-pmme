# Dossiê executivo — implementação do PMM-E e próximo desenho causal

> **Status em 31/08/2026:** a evidência disponível para o ciclo 1 é uma
> comparação ajustada entre vagas inicialmente imediatas e vagas inicialmente
> em cadastro de reserva. Ela não identifica, sozinha, o efeito causal do PMM-E.

## 1. Resultado que temos hoje

O universo publicado contém 587 células município–curso em 368 municípios. A
amostra com variação usada pela DDD contém 319 células em 93 municípios. A
modalidade imediata não foi sorteada e não representa “programa”; a modalidade
reserva também pertence ao PMM-E e pode receber alocação posteriormente.

| Diagnóstico | Estimativa | Leitura permitida |
|---|---:|---|
| Diferença na alocação confirmada | +2,79 p.p.; IC 95% [-10,91; 16,48] | Primeiro estágio impreciso; não demonstrado |
| Diferença ajustada no estoque CNES | -0,446; IC 95% [-0,934; 0,042] | Não há aumento relativo robusto na janela |
| Diferença ajustada na cobertura | +0,73 p.p.; p = 0,637 | Inconclusiva |
| Diferença ajustada nas entradas | -0,073; p = 0,087 | Sugestiva, não confirmatória |
| Diferença ajustada nas saídas | -0,018; p = 0,716 | Inconclusiva |
| Teste conjunto dos coeficientes pré | F = 1,262; p = 0,255 | Não rejeita zero; não prova paralelismo |
| Presença aos seis meses entre entrantes | 86,9% imediata; 79,7% reserva | Descritiva e condicional a uma variável pós-exposição |

A Figura 3 mostra trajetórias brutas: aproximadamente 7,09 para 8,35
(imediata) e 10,77 para 12,77 (reserva). Os grupos diferem em nível desde o
início. O gráfico não compara grandes centros com interior, nem médicos do
PMM-E com médicos não participantes.

## 2. O que esses achados não demonstram

Não é sustentado afirmar que:

- o PMM-E causou queda, aumento ou ausência de efeito sobre a oferta médica;
- tendências paralelas foram “formalmente validadas”;
- a alta presença entre entrantes foi causada pelo programa;
- atração, e não retenção, é necessariamente o único gargalo;
- redistribuição intramunicipal foi descartada;
- falta de infraestrutura, carreira ou seleção direta causou o resultado;
- um patamar de 65% de preenchimento determina significância estatística;
- condicionar bolsas ao CNES é uma recomendação já testada.

Essas proposições podem ser hipóteses institucionais. Não são estimativas deste
estudo. O CNES registra vínculos cadastrais; não prova exercício físico,
participação individual no programa, produção clínica ou pagamento de bolsa.

## 3. Contribuição publicável no curto prazo

A contribuição atual é um diagnóstico de implementação: prioridade
administrativa, preenchimento e aumento do estoque são margens diferentes. Na
janela disponível, a modalidade imediata teve um primeiro estágio fraco e não
apresentou aumento relativo robusto do estoque cadastrado em comparação com a
reserva. Essa conclusão é relevante, mas deve ser apresentada como associação
ajustada.

O ciclo 3 permanece congelado prospectivamente. Sua coorte e seus outcomes não
devem ser redefinidos após observação de efeitos, e a análise de seis meses só
ocorrerá com competências maduras.

## 4. Desenho causal prioritário

O caminho de curto prazo com melhor fundamento é testar o efeito local de
**R$ 5 mil adicionais na bolsa** nos limiares administrativos do IVS:

- 0,400/0,401: R$ 10 mil para R$ 15 mil;
- 0,500/0,501: R$ 15 mil para R$ 20 mil.

O outcome primário é procura e preenchimento por vaga. O estoque CNES é
secundário e só será examinado depois de demonstrado o primeiro estágio
administrativo. SIH/SIA entram depois, com outcomes clínicos pré-especificados e
auditoria de cointervenções do Agora Tem Especialistas.

Esse desenho está **bloqueado na reconstrução da regra**: a faixa publicada
diverge da faixa obtida com o IVS local disponível em 177 dos 368 municípios do
ciclo 1. Antes de estimar qualquer efeito é necessário validar versão, casas
decimais, arredondamento, data de corte e eventuais exceções do escore usado pelo
controlador.

Plano e prompts executáveis:

- [plano de implementação da RDD](../05_identificacao/14_plano_implementacao_rdd_bolsa.md);
- [portão de regra e suporte](../../prompts/avaliacao_rdd_bolsa/01_portao_regra_e_suporte.md);
- [congelamento e estimação administrativa](../../prompts/avaliacao_rdd_bolsa/02_congelar_e_estimar_administrativo.md).

## 5. Decisão agora

Executar primeiro o portão documental da RDD. Se a regra exata não for
reproduzida, encerrar esse desenho sem consultar outcomes e publicar o ciclo 1
como estudo de implementação. Se o portão passar, congelar amostra, bandwidths,
outcomes e inferência antes de estimar procura e preenchimento. O limiar 0,400 é
o candidato principal pelo suporte preliminar; 0,500 será replicação apenas se
houver massa local suficiente.
