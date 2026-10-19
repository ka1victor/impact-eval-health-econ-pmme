# Suíte de Testes Automatizados do PMM-E

Este diretório reúne a suíte de testes automatizados do projeto, composta por **558 testes em 39 módulos** (contagem de 18/10/2026), garantindo a integridade substantiva, metodológica, computacional e documental da pesquisa.

---

## 1. Como Executar os Testes

A suíte exige **Python 3.12 ou superior** com as dependências de
`requirements.txt` instaladas. Em versões anteriores o `unittest` não consegue
importar os módulos que dependem de `pandas` e reporta erro de importação, não
falha substantiva.

O repositório disponibiliza um executor direto na raiz:

```bash
python run_tests.py
```

Alternativamente, é possível executar via módulo padrão do Python:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

Para rodar um módulo específico:

```bash
python -m unittest tests/test_pipeline_invariants.py
```

---

## 2. Catálogo dos Módulos de Teste

| Módulo | Testes | Foco e Garantias Econométricas |
|---|:---:|---|
| [`test_pipeline_invariants.py`](test_pipeline_invariants.py) | Invariantes | Balanceamento do painel (26 meses), não imputação de FTE/horas, censura de margens longitudinais, ponte CBO operacional, convergência numérica dos modelos e validade de todos os links de documentação. |
| [`test_estimativas_atracao_a4.py`](test_estimativas_atracao_a4.py) | A4 Atração | Estimação LPM e Logit de atração (+29,4pp metropolitano vs remoto), erros clusterizados por município, invariância da amostra N=1.295 células em 368 municípios. |
| [`test_provimento_cnes_a5.py`](test_provimento_cnes_a5.py) | A5 Dinâmica CNES | Avaliação da oferta médica local cadastrada no CNES (amostra confirmatória de 587 células em 295 municípios, referência 202506 e follow-up 202603, tom estritamente associativo). Inclui a conferência de proveniência dos hashes de entrada, ausente até 09/09/2026. |
| [`test_red_team_a6.py`](test_red_team_a6.py) | A6 Red Team | Auditoria das 11 afirmações substantivas na matriz afirmação–evidência–limite e validação do manifesto de hashes reproduzíveis. |
| [`test_cutoff_selecao_a7.py`](test_cutoff_selecao_a7.py) | A7 Corte de seleção | Suporte dos pares adjacentes, resultados de homologação/presença ativa, proteção de dados pessoais e bloqueio explícito de linguagem causal sem os desempates. |
| [`test_cutoff_escore_estrito_a8.py`](test_cutoff_escore_estrito_a8.py) | A8 Cutoff estrito | Suporte sem empates e gap de um ponto, efeitos principais, placebos, sensibilidades, replicação de 2026, linguagem causal condicional e proteção de dados pessoais. |
| [`test_fonte_ivs_oficial.py`](test_fonte_ivs_oficial.py) | IVS oficial | Nenhum script do pipeline lê `data/ivs_ipea_2010_municipios.csv` (ou saída de script retirado que o usava) fora da lista de documentadores do failure mode; varre o texto bruto de todo `.py` sob `scripts/` e na raiz (inclusive `utils/` e `rdd_lib.py`), juntando literais concatenados e casando globs, com contagem exata de ocorrências autorizada por script, e prova a guarda injetando violações numa cópia temporária fora do repositório; doc 16 e proveniência da banca 1 citam o ajuste completo lido de `A4_tabela_03b`; plano, estratégia, roadmap e fila do ciclo 3 citam o C3-03 reestimado e explicitam a virada de suporte; malha e tipologia iguais à a08 e ao Censo 2022 em todo município; ajuste completo antigo só como failure mode (auditoria 19). |
| [`test_tipologia_territorial.py`](test_tipologia_territorial.py) | A2 Território | Classificação em 4 estratos (Capital, Metropolitano, Interior Próximo e Interior Remoto) via REGIC 2018 + RM/RIDE 2022 strict, sem consulta a desfechos. |
| [`test_reconciliacao_funil_ciclo1.py`](test_reconciliacao_funil_ciclo1.py) | A1 Funil | Auditoria de confirmações em células de reserva e formalização do portão `APROVADO_CELULA`. |
| [`test_pre_analise_atracao.py`](test_pre_analise_atracao.py) | A3 Pré-Análise | Congelamento dos contrastes e MDEs calculados antes da estimação de A4, verificação de hashes de entrada e clusterização. |
| [`test_tema_atracao_provimento.py`](test_tema_atracao_provimento.py) | Auditoria de Tema | Viabilidade do tema de atração administrativa e delimitação entre provimento local e retenção individual. |
| [`test_validacao_ivs_oficial_04b.py`](test_validacao_ivs_oficial_04b.py) | RDD Bolsa — R1 com o IVS oficial | Escore do MS igual ao IVS 2010 oficial (404/404; 5.565/5.565 categorias), regra reproduzida em 368/368 e 454/454 e decisão `APROVADO_SHARP`; funções puras em dados sintéticos rotulados. |
| [`test_recorte_arquivo_local_04c.py`](test_recorte_arquivo_local_04c.py) | RDD Bolsa — arquivo de IVS errado | O mecanismo "última linha de subgrupo com IVS preenchido" reproduz `data/ivs_ipea_2010_municipios.csv` inteiro (4.362 municípios na linha de mulheres negras urbanas); soma da população da linha total igual ao Censo 2010. |
| [`test_cache_ivs_oficial_a08.py`](test_cache_ivs_oficial_a08.py) | RDD Bolsa — aquisição | O zip de 201 MB do Ipea não é baixado de novo quando já existe com o SHA-256 certo; download parcial não vira insumo. |
| [`test_e1_densidade.py`](test_e1_densidade.py) | RDD Bolsa — E1 | Razão de densidades em mass points: sem salto em densidade uniforme, detecta massa plantada, corte no lado inferior. Sintético. |
| [`test_e2_limites.py`](test_e2_limites.py) | RDD Bolsa — E2 | Limites parciais com escore ausente: ordenação, colapso sem ausência, validade e aninhamento; propriedades nas saídas reais. |
| [`test_e3_rdd_sintetico.py`](test_e3_rdd_sintetico.py) | RDD Bolsa — E3 | Local linear sharp com kernel triangular e EP HC1: recupera saltos conhecidos, EP calibrado, falha fechada sem escore completo, diagnósticos antes dos outcomes, covariável igual à running variable sem teste. Sintético. |
| [`test_e4_proporcao.py`](test_e4_proporcao.py) | RDD Bolsa — E4 | Proporção preenchida reconstruída dos brutos (393/1.295 e 461/1.295, zero divergências) e estimadores E4 em dados sintéticos. |
| [`test_e5_inferencia_sintetico.py`](test_e5_inferencia_sintetico.py) | RDD Bolsa — E5 (exploratório) | Especificações alternativas, permutação de Fisher, limites unilaterais e TOST, seleção da janela de local randomization só por balanço. Sintético. |
| [`test_rdd_lib.py`](test_rdd_lib.py) | RDD Bolsa — biblioteca E6–E9 | `rdd_lib.py`: identidade bit a bit com o E3 e com o E5; local linear, empilhado (duplicatas, cluster, EF de ciclo), IC honesto de Armstrong–Kolesár (cv(0) = 1,96, M = 0 igual a HC1, cobertura), Poisson local, DiRD em delta = DiRD em painel, estudo de evento, índices KLK e Anderson, Holm e BKY contra exemplos à mão, limites de Lee, Fisher; nada descartado em silêncio (rótulo ausente levanta erro, descartes contados), suporte explícito da regra de bolso, separação no Poisson e EP igual ao sanduíche do statsmodels, BKY igual ao statsmodels. Sintético. |
| [`test_outcomes_funil.py`](test_outcomes_funil.py) | RDD Bolsa — outcomes do funil | Construção dos outcomes F0–F4 dos ciclos 1–3 e das tabelas de escolha do E9: reprodução de E3/E4, chaves, NaN sempre com motivo, nada lido do arquivo de IVS errado. |
| [`test_e6_funil.py`](test_e6_funil.py) | RDD Bolsa — E6 | Estimação do protocolo 40 para F0, F1, F2, F4, índice P1 e S1–S4: todas as especificações presentes, reprodução do E3/E5, sinal, BKY, tabelas do doc 41 geradas das saídas. |
| [`test_e9_escolha.py`](test_e9_escolha.py) | RDD Bolsa — E9 | Logit condicional da escolha dos candidatos (§12, §14, §15): recuperação sintética do coeficiente, equivalência com o statsmodels, robustez pós-auditoria e números do doc 42 conferidos contra os CSVs. |
| [`test_cnes_nacional.py`](test_cnes_nacional.py) | Aquisição — CNES nacional | Painel município × grupo de CBO × mês (39 competências): esquema, painel balanceado só em meses lidos, nenhum mês ≥ 202609, horas SUS (§16), horas em branco nunca viram zero, portão antes de gravar e validação contra o painel do ciclo 1. |
| [`test_e7_dird.py`](test_e7_dird.py) | RDD Bolsa — E7 | Diferença em descontinuidades no CNES nacional (F3, P2, S2–S6, §16): recuperação sintética, horas faltantes nunca viram zero, portões fail-closed, tabelas e afirmações do doc 43 conferidas contra os CSVs. |
| [`test_conferencia_sinal_rdd.py`](test_conferencia_sinal_rdd.py) | RDD Bolsa — sinal do salto | O salto é o lado com bolsa maior menos o lado com bolsa menor; reestimação independente e decomposição da diferença bruta em salto e inclinação. Sintético. |
| [`test_pipeline_rdd_bolsa.py`](test_pipeline_rdd_bolsa.py) | RDD Bolsa — pipeline | Ordem da cadeia da RDD no `run_all.py`, argumento do E3 e retirada dos scripts que liam o arquivo de IVS errado. |
| [`test_integridade_dados.py`](test_integridade_dados.py) | Integridade | Nenhum arquivo em `data/` ou `output/` com nome de dado simulado; toda saída rotulada com `natureza_dos_dados` é `EMPIRICO`. |
| [`test_viabilidade_salario_ivs.py`](test_viabilidade_salario_ivs.py) | RDD Bolsa — **registro superado** | Falha de replicação das faixas em 177 municípios e encerramento do R1. Testa saídas feitas com o arquivo de IVS errado (auditoria 16); mantido como histórico. |
| [`test_primeiro_estagio_publico_rdd.py`](test_primeiro_estagio_publico_rdd.py) | RDD Bolsa — **registro superado** | Ausência de salto estável no "IVS 2010 público", que era o arquivo errado (auditoria 16); mantido como histórico. |
| [`test_portao_regra_rdd.py`](test_portao_regra_rdd.py) | RDD Bolsa — **registro superado** | Matriz municipal com 177 divergências e bloqueio de R2–R5, feitos com o arquivo errado; mantido como histórico. |
| [`test_reconstrucao_regra_faixa.py`](test_reconstrucao_regra_faixa.py) | RDD Bolsa — **registro superado** | Reconstrução da regra de faixa com o arquivo errado; mantido como histórico. |
| [`test_triagem_admin_rdd.py`](test_triagem_admin_rdd.py) | RDD Bolsa — **registro superado** | Triagem da resposta ao pedido do escore ao MS, cancelado porque o escore é público (auditoria 16). |
| [`test_conferencia_artigos.py`](test_conferencia_artigos.py) | Artigos | Toda cifra dos dois artigos tem origem em `output/`, e os dois citam o mesmo núcleo de resultados. |
| [`test_verificacao_ambiente.py`](test_verificacao_ambiente.py) | Ambiente | Verificação das versões exigidas antes de rodar o pipeline. |
| [`test_coorte_c3.py`](test_coorte_c3.py) | Ciclo 3 Coorte | Congelamento dos cursos 1, 12 e 24 com suporte integral e verificação da assinatura cadastral (Nota Técnica nº 59/2026). |
| [`test_sih_pre_c3.py`](test_sih_pre_c3.py) | Ciclo 3 SIH Pré | Auditoria dos dados hospitalares do SIH, dicionário SIGTAP e regra *fail-closed* ante ausência de arquivos no FTP. |
| [`test_pre_analysis_c3.py`](test_pre_analysis_c3.py) | Ciclo 3 Pré-Análise | Torneio pré-tratamento de anestesiologia e congelamento de protocolo antes da maturidade de 202703; o bloco congelado não é reescrito (`--refresh-hashes` só por emenda datada) e a emenda de 18/10/2026 registra a validação do modo de reestimação com a malha antiga. |
| [`test_datasus_parser.py`](test_datasus_parser.py) | Utilitário DBC | Validação funcional da rotina de descompressão e conversão de arquivos `.dbc` do DATASUS. |

---

## 3. Padrões de Teste

1. **Isolamento e determinismo:** Os testes operam sobre os artefatos congelados em `output/` e garantem que qualquer alteração de código que degrade coeficientes, altere amostras ou quebre links da documentação seja imediatamente detectada.
2. **Sem dados sintéticos desavisados:** Nenhum teste deve aceitar dados simulados como se fossem bases reais.
3. **Auditoria de Documentação:** Testes verificam automaticamente a consistência entre o texto publicado e as tabelas numéricas salvas.
