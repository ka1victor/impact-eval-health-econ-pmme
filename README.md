# Avaliação do Mais Médicos Especialistas (PMM-E)

Avaliação de impacto do Programa Mais Médicos Especialistas (Lei nº 15.233/2025) com dados públicos: editais e
resultados do programa, CNES, SIA, SIH, TISS e o IVS 2010 do Ipea. Todo número sai de um script versionado, é
gravado em `output/` com manifesto e hash, e é conferido por teste.

O repositório serve para duas coisas: guardar a evidência do trabalho (bancas 1, 2 e final, artigos) e servir de
base para outras perguntas sobre o PMM-E ou sobre força de trabalho médica no SUS. Veja
[Reaproveitar o repositório](#reaproveitar-o-repositório).

## Estado em 18/11/2026

**Pergunta da banca final:** a bolsa maior (+R$ 5 mil/mês nas faixas de IVS do edital) muda qual vaga o médico
escolhe como 1ª opção?

| Resultado | Leitura | Onde está |
|---|---|---|
| **Logit condicional, vagas da mesma UF (VL-1).** +R$ 5 mil multiplicam a chance de a vaga ser a 1ª opção por **×1,47** [1,15; 1,89] nos ciclos 1–3 (p de Holm 0,005) e por ×1,90 [1,30; 2,78] no ciclo 2. Em distância, +R$ 5 mil valem o mesmo que a vaga ficar **75 km** mais perto [28; 122] | resultado da banca final. **Exploratório:** a especificação foi escolhida depois de ver os dados (adendo 52e). Na especificação pré-registrada (M1), o peso da bolsa não passa no Holm | [57x](docs/06_execucao/57x_resultados_escolha_localizacao_par.md), [66](docs/06_execucao/66_analise_completa_H2.md) |
| **Onde o médico escolhe (descritivo).** Entre 5.425 candidatos com origem conhecida, 79% põem a 1ª opção na UF onde já trabalham e 36% no mesmo município; distância mediana de 51 km | descritivo | [66](docs/06_execucao/66_analise_completa_H2.md) |
| **RDD da bolsa** nos cortes 0,300 e 0,400 do IVS 2010 oficial (preenchimento, funil, CNES, produção) | nenhuma primária rejeita zero depois do Holm: inconclusivo, não evidência de ineficácia. Nos mesmos cortes mudam outras regras federais: a RDD mede um pacote. A running variable é o IVS 2010 oficial do Ipea; `data/ivs_ipea_2010_municipios.csv` **não** é o IVS do município | [44](docs/06_execucao/44_sintese_rdd_bolsa_multioutcome.md), [57](docs/06_execucao/57_sintese_perguntas_reformuladas.md), [auditoria 16](docs/auditorias/16_ivs_2010_oficial_e_arquivo_local.md) |
| **Corte de seleção (A8).** Em 36 pares separados por um ponto, ganhar a vaga eleva a homologação em 63,9 p.p. e a presença ativa posterior em 33,3 p.p. | causal local, rigor moderado; núcleo dos dois artigos | [17](docs/05_identificacao/17_plano_causal_publico_cutoff_escore.md), [33](docs/06_execucao/33_status_execucao_plano_causal.md) |
| **Atração territorial (A4) e oferta no CNES (A5)**, ciclo 1 | associativos | [35](docs/06_execucao/35_plano_correcoes_pos_auditoria.md) |
| **Ciclo 3** | congelado até a competência `202703` do CNES estar publicada e madura | [12](docs/05_identificacao/12_estrategia_causal_prospectiva_ciclo3.md), [13](docs/05_identificacao/13_plano_pre_analise_ciclo3.md) |

O README anterior, com o histórico do estado em camadas, está em
[`docs/90_arquivo_historico/README_raiz_ate_18nov2026.md`](docs/90_arquivo_historico/README_raiz_ate_18nov2026.md).

## Comece aqui

| Quero… | Onde |
|---|---|
| apresentar a banca final | deck `output/apresentacao_banca_final/deck_banca_final_bernardo_r13.pptx` e roteiro `roteiro_fala_banca_final.docx` (mesma pasta); conteúdo e perguntas prováveis em [`docs/07_apresentacoes/banca_final/`](docs/07_apresentacoes/banca_final/README.md) |
| entender a pergunta e a teoria | [pergunta do artigo](docs/01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md), [modelo microeconômico](docs/02_teoria/modelo_micro.md) |
| saber de onde vem cada número | o doc de resultado em [`docs/06_execucao/`](docs/06_execucao/) (cada um diz o script e a saída) e a auditoria correspondente em [`docs/auditorias/`](docs/auditorias/) |
| navegar pela documentação | [`docs/README.md`](docs/README.md) |
| ler os artigos | `paper_pmme_submission.tex` (completo) e `paper_pmme_curto.tex` (sete páginas); cada cifra é conferida contra `output/` pelo `run_all.py` |
| ver o que falta | [`TODO.md`](TODO.md) |
| saber as regras de trabalho | [`CLAUDE.md`](CLAUDE.md) (regras do projeto) e [`AGENTS.md`](AGENTS.md) |

## Reaproveitar o repositório

Blocos que funcionam fora da pergunta da bolsa:

| Bloco | O que faz | Onde |
|---|---|---|
| Aquisição de dados públicos de saúde | CNES mensal e nacional, CNES profissional, SIA e SIH pelo TabNet (por local de atendimento e por residência), TISS/ANS, SIGTAP, IVS 2010 oficial, Censo 2022, editais e resultados do PMM-E, normas federais. Os scripts de aquisição gravam manifesto com SHA-256, e os de bases grandes (a09 em diante) têm `--etapa verificar`, que confere o que está versionado sem rede | [`scripts/aquisicao/`](scripts/aquisicao/), saídas em [`output/aquisicao/`](output/aquisicao/) |
| Leitura de arquivos do DATASUS | download, descompressão e conversão de `.dbc` para DataFrame ou Parquet | [`scripts/utils/datasus_dbc.py`](scripts/utils/datasus_dbc.py) |
| Referência sobre as bases | o que cada sistema mede, unidade, acesso e limites | [inventário por outcome](docs/04_dados/02_inventario_dados_por_outcome.md), [dossiê das bases de saúde](docs/04_dados/20_dossie_bases_dados_saude_brasil_pmme.md) |
| Estimadores | RDD (`rdd_lib.py`), logit condicional de escolha (`16_estimar_E9_escolha.py`, `50_escolha_localizacao_par.py`), sensibilidade de Rambachan–Roth (`honestdid_lib.py`), DiRD, Holm e BKY | [`scripts/rdd_bolsa/`](scripts/rdd_bolsa/) |
| Ambiente reprodutível | confere Python, numpy e pandas antes de rodar | [`scripts/utils/ambiente.py`](scripts/utils/ambiente.py) |
| Decks e roteiros gerados por script | python-pptx sobre o deck do grupo, figuras de `output/`, roteiro em Word | [`scripts/apresentacao/`](scripts/apresentacao/) |

**Para abrir uma pergunta nova**, siga o caminho que as anteriores seguiram:

1. Protocolo em `docs/06_execucao/` (próximo número livre), congelado antes de olhar o resultado; o que vier
   depois de ver dados é rotulado como pós-resultado ou exploratório.
2. Script em `scripts/<área>/`, com caminhos relativos à raiz, lendo `data/` ou `output/` e gravando só em `output/`.
3. Teste em `tests/` que confere esquema, cobertura, hashes e, quando houver, o doc gerado.
4. Doc de resultado em `docs/06_execucao/` e, se o arquivo for novo, entrada em
   [`docs/00_registro_mudancas.md`](docs/00_registro_mudancas.md).

As regras que valem para tudo isso (nunca alterar `data/`, proveniência, linguagem causal só com identificação)
estão no [`CLAUDE.md`](CLAUDE.md).

## Executar

### Ambiente

O `requirements.txt` fixa `numpy==2.5.2` e `pandas==3.0.5`, que exigem **Python 3.12 ou superior**.

```bash
python3.13 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

O ambiente é obrigatório, não recomendado. Com versões próximas (por exemplo numpy 2.4.6), os scripts rodam e os
testes passam, mas as saídas mudam a partir da 14ª casa decimal. Como a proveniência é ancorada em SHA-256 de
arquivo, isso reescreve artefatos e quebra a cadeia de hashes sem aviso. Por isso o `run_all.py`, que grava,
**aborta** diante de divergência; o `run_tests.py`, que só lê, **avisa** e segue
([`scripts/utils/ambiente.py`](scripts/utils/ambiente.py); erratas em
[`docs/auditorias/14_erratas_artefatos_congelados.md`](docs/auditorias/14_erratas_artefatos_congelados.md)).

### Pipeline e testes

```bash
python run_all.py              # pipeline completo; exige os 26 arquivos mensais do CNES do manifesto
python run_all.py --rdd-bolsa  # só a cadeia da RDD da bolsa
python run_tests.py            # suíte de testes (98 arquivos em tests/)
```

A ordem dos passos é a lista `STEPS` do `run_all.py`, descrita em [`scripts/README.md`](scripts/README.md).
As rodadas exploratórias e os decks rodam fora do pipeline, com o comando registrado no doc de cada uma.

## Estrutura

| Caminho | O que guarda |
|---|---|
| [`data/`](data/README.md) | bases observadas e brutos; **só leitura** |
| [`docs/`](docs/README.md) | pergunta, teoria, literatura, dados, identificação, execução, apresentações, auditorias; [registro de mudanças](docs/00_registro_mudancas.md) |
| [`output/`](output/README.md) | painéis, estimativas, figuras, decks e manifestos, todos gerados por script |
| [`scripts/`](scripts/README.md) | aquisição, estimação, apresentação e utilitários |
| [`tests/`](tests/README.md) | testes de integridade, de estimadores e de documentos gerados |
| [`prompts/`](prompts/README.md) | sessões de trabalho já executadas e filas congeladas (ciclo 3) |
| `run_all.py`, `run_tests.py` | pontos de entrada do pipeline e da suíte |
| `paper_pmme_submission.tex`, `paper_pmme_curto.tex` | artigos |
| `TODO.md` | pendências |
| `CLAUDE.md`, `AGENTS.md` | regras de trabalho para pessoas e agentes |
