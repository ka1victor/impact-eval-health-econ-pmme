# 05. OCI e teleconsulta: hipóteses de registro e mecanismo espacial

> OCI e teleconsulta pertencem ao contexto mais amplo do Agora Tem Especialistas. Elas podem ajudar a entender mensuração e mecanismos, mas não são automaticamente controles ou validações do efeito do PMM-E.

## 1. OCI: capacidade nova ou mudança de código?

A pergunta correta possui três margens:

1. **registro:** procedimentos antes faturados separadamente passam a um pacote do Grupo 09;
2. **organização:** a linha de cuidado fica mais integrada, mesmo sem nova capacidade física;
3. **capacidade:** novos profissionais, equipamentos ou horários aumentam a oferta real.

Um estabelecimento já realizar componentes antes da OCI é evidência contra interpretar a primeira APAC como abertura física. Não prova que a mudança é “apenas contábil”: integração, coordenação, remuneração e sequência do cuidado podem mudar.

## 2. Estado da evidência OCI no repositório

O script contém manualmente:

- série de CNES por competência;
- fração de 86,4% de estabelecimentos que já faturavam componentes;
- contagens de novos entrantes;
- percentuais de migração por subgrupo.

Não há arquivos de origem suficientes no repositório para reproduzir essas cifras. O próprio comentário do código chama parte do procedimento de “simulação/mapeamento estruturado”. Portanto:

> A hipótese de reclassificação é metodologicamente importante, mas o valor de 86,4% não é um resultado reproduzido nesta execução.

## 3. Por que a OCI afeta a avaliação do PMM-E

Se produção migra dos grupos 02/03/04 para o Grupo 09, séries construídas apenas com códigos antigos podem mostrar queda artificial após 2025. O viés pode:

- atenuar um aumento real;
- fabricar queda;
- afetar de modo desigual municípios que adotaram OCI;
- coincidir com a entrada do PMM-E.

Antes de estimar produção, é preciso mapear componentes e reconstruir uma família de procedimentos comparável ao longo do tempo. A OCI é, primeiro, uma ameaça de mensuração; só depois pode ser evento de interesse.

## 4. Teleconsulta: uma hipótese de mecanismo, não uma prova automática

Se a distância física restringe o cuidado presencial, é plausível que o gradiente de distância seja menor para teleconsulta. A comparação é informativa quando:

- presencial e remoto usam a mesma população de origem e janela;
- os procedimentos têm escopo clínico comparável;
- a disponibilidade tecnológica e a rede de prestadores são controladas;
- efeitos fixos, pesos e erros-padrão são idênticos;
- a residência do paciente e o prestador remoto têm significado consistente.

Um coeficiente menor é compatível com menor fricção física. Também pode refletir seleção de pacientes, faturamento centralizado, concentração de oferta digital ou diferenças de complexidade.

## 5. Estado da evidência de teleconsulta no repositório

Os coeficientes presencial e remoto apresentados no output estão escritos diretamente no script:

| Coeficiente | Valor fixado |
|---|---:|
| Presencial em SP | -1,4043 |
| Teleconsulta em SP | -0,1142 |
| Teleconsulta em PE | -0,1480 |

A execução não carrega a matriz origem-destino nem estima a regressão. Assim, a diferença de mais de 90% é um resultado externo incorporado ao protótipo, não uma validação reproduzível.

Mesmo se reproduzida, ela não “comprova” o BCR de transporte: o coeficiente descreve um gradiente de fluxo e não quantifica viagens evitadas, custo marginal ou efeito do PMM-E.

## 6. Relação com o programa amplo

A Lei nº 15.233/2025 permite atendimentos por telemedicina e estabelece prioridade para regiões remotas ou com escassez de especialistas. Isso cria complementaridade e substituição potenciais:

- teleconsulta pode ampliar o alcance do especialista presencial;
- pode substituir parte das consultas que exigiriam deslocamento;
- pode aumentar encaminhamentos presenciais adequados;
- pode competir por profissionais e tempo;
- pode mudar onde o atendimento é faturado sem mudar a localização do paciente.

Logo, PMM-E, OCI e teleconsulta podem ocorrer simultaneamente. Atribuir mudança de produção a um único componente exige datas e exposições separadas.

## 7. Evidência necessária

- microdados mensais de Grupo 09 por CNES, procedimento principal e componentes;
- histórico dos mesmos componentes por origem antes da adoção;
- produção de teleconsulta por residência-prestador;
- atos normativos e datas efetivas;
- mesma especificação estimada para presencial e remoto;
- testes de composição, preexistência, antecipação e mudança de código.

## 8. Veredito atual do eixo

> OCI e teleconsulta levantam hipóteses valiosas sobre mensuração e distância. As cifras centrais, porém, não são reproduzidas pelos dados presentes. Elas não devem ser usadas para declarar oferta nova, mera reetiquetagem, validação causal do PMM-E ou retorno logístico.
