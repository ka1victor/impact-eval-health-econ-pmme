# Programa Mais Médicos Especialistas (PMM-E): agenda de avaliação de impacto

> Repositório de pesquisa sobre o componente de provimento de especialistas do Programa Agora Tem Especialistas. O projeto está em **fase de auditoria do desenho**: os dados disponíveis já permitem descrever a implantação, mas ainda não sustentam os efeitos causais antes apresentados como resultados consolidados.

> [!IMPORTANT]
> Os números gerados pelo pipeline atual misturam registros observados, painéis pré-compilados e parâmetros definidos no código. Por isso, as estimativas de preenchimento, resolutividade, viagens evitadas, custo-benefício, QALYs, OCI e teleconsulta devem ser lidas como **protótipos ou cenários**, não como evidência de que o programa deu certo ou errado.

## A pesquisa em três perguntas que se encadeiam

1. **Qual problema o programa tenta resolver?**
2. **Quais métricas observam cada parte desse problema e quais dados temos para calculá-las?**
3. **Quais métricas já foram de fato analisadas, o que aprendemos e o que ainda não podemos concluir?**

Essa ordem é substantiva. Não faz sentido escolher um resultado antes de definir qual dimensão do problema ele representa; tampouco faz sentido chamar uma cifra de resultado se ela foi imposta como premissa no próprio código.

## 1. Qual problema o programa tenta resolver?

A [Lei nº 12.871/2013](https://www2.camara.leg.br/legin/fed/lei/2013/lei-12871-22-outubro-2013-777279-normaatualizada-pl.html) criou o Programa Mais Médicos para reduzir a carência regional de médicos, fortalecer a atenção primária e integrar formação e serviço. Alterações posteriores também incorporaram a qualificação da assistência especializada e a ampliação da especialização em áreas estratégicas.

A [Lei nº 15.233/2025](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/lei/l15233.htm) instituiu o Programa Agora Tem Especialistas. Seu art. 1º explicita três objetivos gerais: qualificar e diversificar serviços, ampliar a oferta e reduzir o tempo de espera por consultas, procedimentos e exames especializados. O art. 21 inseriu o Projeto Mais Médicos Especialistas na Lei nº 12.871/2013, destinado ao provimento em regiões prioritárias **com vistas à redução do tempo de espera**.

Para este projeto, o problema é organizado em uma cadeia, não em quatro resultados independentes:

```text
escassez/distribuição de especialistas
        ↓
capacidade efetivamente disponível
        ↓
acesso, deslocamento e tempo de espera
        ↓
continuidade, qualidade e desfechos clínicos
        ↓
custos públicos e bem-estar dos pacientes
```

Cada seta é uma hipótese causal a ser testada. Mais médicos não implicam automaticamente mais capacidade; mais produção local não implica automaticamente fila menor; fila menor não implica automaticamente melhor saúde.

Também não tratamos como fato estabelecido que a expansão da atenção primária “criou” um segundo gargalo, que pacientes viajam necessariamente de van ou que centros cirúrgicos estavam ociosos por falta de anestesista. Essas são hipóteses plausíveis, mas exigem dados próprios.

## 2. Quais métricas temos e o que elas podem avaliar?

| Eixo | Métrica principal | O que ela responde | Situação no repositório | O que ela não responde sozinha |
|---|---|---|---|---|
| **Provimento** | Vagas ofertadas, preenchidas e entrada em exercício | A bolsa altera a ocupação das vagas oferecidas? | **Parcial:** há cadastro nominal de ativos; falta a lista completa de vagas e candidatos | Não mede aumento líquido da oferta municipal nem fila |
| **Retenção e capacidade** | Sobrevivência do médico no posto; FTE observado no CNES | O profissional permanece e adiciona horas de trabalho? | **Parcial:** há série mensal agregada; FTE é presumido no script | Não mede produção, qualidade ou substituição de outro vínculo |
| **Acesso espacial** | Atendimentos locais, externos e taxa de bypass | O cuidado migrou para mais perto do paciente? | **Não identificado:** o painel disponível incorpora produção e substituição parametrizadas | Não mede espera, necessidade atendida ou qualidade |
| **Acesso global e fila** | Atendimentos totais por residente; tempo entre solicitação e atendimento | O total atendido aumentou e a espera caiu? | **Não avaliado:** não há microdado de fila/regulação no repositório | Total estável não prova fila estável; fila menor pode refletir mudança de registro |
| **Linha de cuidado** | Tempo diagnóstico-terapia, estadiamento, eletivas e urgências | O acesso mais rápido mudou a trajetória clínica? | **Não avaliado** | Volume de exames não equivale a diagnóstico precoce ou saúde melhor |
| **Custos e bem-estar** | Custo incremental, transporte observado, tempo de viagem e efeitos clínicos | O benefício social excede o custo de oportunidade? | **Cenário parametrizado** | Economia municipal não é automaticamente economia consolidada do SUS |
| **OCI e teleconsulta** | Migração de códigos, coortes e gradiente de distância | Mudou a capacidade ou apenas o registro? A distância física é um mecanismo? | **Protótipo:** as cifras centrais estão fixadas no código | Não valida, por si só, o efeito do PMM-E |

O inventário completo, incluindo definição, denominador, unidade e ameaça de interpretação de cada métrica, está em [docs/01_dossie_e_motivacao_politica_publica.md](docs/01_dossie_e_motivacao_politica_publica.md).

## 3. O que já analisamos e o que foi surpreendente?

### O que é observado

O arquivo nominal contém, na referência de 12 de agosto de 2026:

- **1.480 registros de profissionais ativos**, correspondentes a 1.478 combinações únicas de UF e CRM;
- **325 municípios** e **518 estabelecimentos CNES**;
- **384 registros em Anestesiologia**, a maior categoria do arquivo;
- 7.276 registros município-curso-competência na série histórica, entre dezembro de 2025 e agosto de 2026.

Isso descreve **onde e em que cursos aparecem participantes ativos**. Não mede taxa de preenchimento, retenção individual, adicional líquido de médicos, cirurgias destravadas ou efeito sobre a fila.

### Achados surpreendentes defensáveis

Até aqui, os achados surpreendentes são **descritivos ou metodológicos**. Nenhum deles autoriza ainda a frase “o PMM-E causou X”.

1. **Anestesiologia concentra cerca de 26% dos registros ativos.** São 384 de 1.480 registros, a maior categoria do arquivo nominal. A concentração é substantivamente interessante e gera uma hipótese sobre capacidade cirúrgica, mas não demonstra que salas foram reativadas ou que cirurgias aumentaram.
2. **Os efeitos mais espetaculares estavam parcialmente embutidos no código.** As taxas de preenchimento de 48%, 88% e 94% são atribuídas por faixa de IVS; produção mensal, substituição de 65% do atendimento externo, viagens, custo de R$ 85 e QALYs também são parâmetros. A precisão recupera essas regras, não necessariamente uma resposta comportamental observada.
3. **As duas inferências da resolutividade local contam histórias incompatíveis.** Em $IVS=0{,}300$ e $h=0{,}020$, o protótipo reporta $\tau=+0{,}059$, com $p_{perm}=0{,}0285$, mas $p_{param}=0{,}2673$. Após o ajuste de múltiplos testes implementado, $q=0{,}1425$; o índice conjunto KLK também é não significativo ($p=0{,}2055$). Isso exige auditoria do teste, não promoção do efeito.
4. **A robustez em falsos cortes não é universal.** No placebo $IVS=0{,}250$, diagnósticos globais apresentam $p_{perm}=0{,}030$ em uma banda e resultados marginais aparecem em outras métricas. Logo, a narrativa anterior de placebos “estritamente nulos” não é sustentada por todas as saídas.
5. **O resultado global muda de sinal entre bandas.** No corte 0,300, as estimativas de acesso global passam de positivas para negativas conforme $h$ aumenta. Com erros-padrão grandes, isso não prova expansão, substituição pura ou igualdade a zero.
6. **O pipeline não era numericamente estável.** Os $p$-valores do primeiro script mudam entre execuções por falta de semente NumPy, e alguns exemplos textuais dependem da ordem não determinística de conjuntos.

### O que não conta como achado empírico neste estágio

| Afirmação anterior | Por que não pode ser promovida |
|---|---|
| Preenchimento +35,5 p.p. e elasticidade 1,48 | Desfecho de preenchimento atribuído pela própria faixa |
| “Saturação” acima de R$ 15 mil | Segundo salto também deriva da regra construída; mecanismo de infraestrutura não foi medido |
| Retenção -4,4 p.p. por precariedade | Retenção não é individual e a infraestrutura não aparece no modelo |
| Resolutividade local +7,6 p.p. | Painel incorpora produtividade e substituição presumidas; inferências divergem |
| Ausência de demanda induzida | Não significância global não prova equivalência nem adequação clínica |
| Anestesiologistas destravaram cirurgias | Há composição profissional, mas não capacidade/produção vinculada |
| BCR 2,4x ou 95,4x | Viagens, custos, diagnósticos e QALYs são parâmetros de cenário |
| OCI 86,4% reetiquetagem e teleconsulta valida distância | Cifras estão fixadas no script e não são reestimadas localmente |

Portanto, **ainda não há um efeito causal validado do PMM-E neste repositório**. Essa conclusão não diz que o programa não teve efeito; diz que o desenho atual não distingue as explicações concorrentes.

### Por que “só remanejou” não significa “impacto nulo”

Se o atendimento total dos residentes permanecer constante e uma parcela passar a ocorrer no próprio município, podem existir ganhos reais de tempo, custo de deslocamento, continuidade e conveniência. Mas o mesmo padrão também é compatível com fila inalterada, qualidade diferente, mudança de codificação ou apenas redistribuição de faturamento.

Da mesma forma, um total global estatisticamente indistinguível de zero não prova igualdade: pode refletir baixa potência. E não rejeitar aumento global não descarta demanda induzida. Para afirmar redução de fila, precisamos observar a fila ou uma proxy temporal validada; para afirmar ganho de saúde, precisamos observar a linha de cuidado ou desfechos clínicos.

A análise eixo a eixo está em [docs/07_auditoria_logica_transversal.md](docs/07_auditoria_logica_transversal.md).

## Regra de linguagem a partir desta auditoria

O projeto passa a usar quatro níveis de afirmação:

- **Observado:** calculado diretamente de registros presentes e auditáveis;
- **Estimado:** produzido por desenho identificador válido e dados observados;
- **Cenário:** resultado que depende de parâmetros explicitados;
- **Hipótese:** mecanismo plausível ainda não distinguido empiricamente.

“Comprovou”, “descartou”, “funcionou” e “fracassou” ficam reservados para casos em que o estimando, o contraste e as hipóteses de identificação sustentem a afirmação.

## Estrutura do repositório

```text
README.md                                  síntese das três perguntas
TODO.md                                    fila orientada pelas lacunas da auditoria
docs/01_dossie_e_motivacao_politica_publica.md
docs/02_resultados_rdd_e_elasticidades.md
docs/03_resolutividade_local_vs_global.md
docs/04_auditoria_financeira_e_custo_beneficio.md
docs/05_agora_tem_especialistas_e_teleconsulta.md
docs/06_metodologia_e_limitacoes.md
docs/07_auditoria_logica_transversal.md     crítica transversal do projeto
scripts/                                   pipeline atual, ainda exploratório
output/                                    saídas reproduzíveis do pipeline atual
```

## Execução

```bash
pip install -r requirements.txt
python run_all.py
```

Executar o pipeline reproduz suas saídas numéricas; **não transforma premissas em evidência observada**. A próxima etapa, deliberadamente separada desta auditoria, será decidir como redesenhar e limitar o escopo empírico.
